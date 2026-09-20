"""FabSim HTTP API — 웹 배포용. Studio(단일 사용자)와 달리 여러 클라이언트를 받는다.

  uvicorn sim.api:app --host 0.0.0.0 --port 8080
  pip install 'fabsim[web]'

왜 별도인가: Streamlit은 세션당 스크립트를 통째로 재실행하는 구조라 다중 사용자·
자동화 연동에 맞지 않는다. 계산 코어는 같고(sim.slots / sim.engine), 이 파일은
그 코어를 HTTP로 노출하는 얇은 층이다.

엔드포인트
  GET  /api/health
  GET  /api/catalog        슬롯·구현·팩 목록 (UI가 이걸로 화면을 그린다)
  POST /api/simulate       레시피 + 슬롯 설정 → 결과
  GET  /api/scope/{agent}  조사 범위 (읽기 전용 — 웹에서 편집은 막는다)
  GET  /                   내장 웹 UI
"""
from __future__ import annotations

import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

try:
    from fastapi import FastAPI, HTTPException, UploadFile, File, Form
    from fastapi.responses import HTMLResponse
    from pydantic import BaseModel, Field
except ImportError:  # pragma: no cover
    raise SystemExit("웹 API에는 fastapi가 필요합니다: pip install 'fabsim[web]'")

from sim.engine import Recipe, available_models  # noqa: E402
from sim.metrics.uniformity import compute_metrics  # noqa: E402
from sim.params import available_packs, load_pack, ParamMissing  # noqa: E402
from sim.pack_meta import pack_meta, grouped  # noqa: E402
import sim.models  # noqa: F401,E402
import sim.slots as S  # noqa: E402
from sim.recipe_builder import load_schemas, to_overrides, coverage  # noqa: E402

app = FastAPI(title="FabSim API", version="0.3.0")


# ── 접근 토큰 (터널로 외부에 노출할 때만 켜진다) ─────────────────────────
# FABSIM_TOKEN이 없으면 미들웨어 자체를 붙이지 않는다 — 사내 LAN에서 쓰는
# 기본 경로에 로그인 벽을 세우지 않기 위해서다. 반대로 cloudflare 터널로
# 공개 URL이 생기는 순간 인증이 없으면 **누구나 시뮬레이터와 런 DB를 연다.**
# 그래서 mobile 런처는 터널 모드에서 토큰을 강제한다.
_TOKEN = os.environ.get("FABSIM_TOKEN", "").strip()
if _TOKEN:
    from starlette.middleware.base import BaseHTTPMiddleware
    from starlette.responses import PlainTextResponse, RedirectResponse

    class _TokenGate(BaseHTTPMiddleware):
        async def dispatch(self, request, call_next):
            if request.url.path in ("/api/health", "/icon.svg",
                                    "/manifest.webmanifest"):
                return await call_next(request)
            if request.cookies.get("fabsim_token") == _TOKEN:
                return await call_next(request)
            q = request.query_params.get("t")
            if q == _TOKEN:
                # 쿼리로 한 번 들어오면 쿠키를 심어 이후 요청(API 호출 포함)을 통과시킨다.
                # 이게 없으면 첫 화면만 뜨고 /api/simulate가 전부 401이 된다.
                url = str(request.url.remove_query_params("t"))
                r = RedirectResponse(url, status_code=302)
                r.set_cookie("fabsim_token", _TOKEN, max_age=60 * 60 * 24 * 30,
                             httponly=True, samesite="lax")
                return r
            return PlainTextResponse("FabSim: 접근 토큰이 필요합니다 (?t=...)",
                                     status_code=401)

    app.add_middleware(_TokenGate)


class SimRequest(BaseModel):
    pack: str = "oxide_silica"
    wafer: str = "NPW"
    pressure_psi: Optional[float] = None
    rpm_wafer: Optional[float] = None
    rpm_platen: Optional[float] = None
    time_s: float = 60.0
    initial_thickness_nm: Optional[float] = None
    zone_pressures_psi: Optional[List[float]] = None
    zone_edges_norm: Optional[List[float]] = None
    meta: Dict[str, str] = Field(default_factory=dict)
    slots: Dict[str, str] = Field(default_factory=dict)
    # 구성요소 스키마 값 — "slurry.abrasive.primary_size_nm": 60 형식.
    # 연결된 것만 팩 오버라이드가 되고, 나머지는 경고로 돌아온다.
    components: Dict[str, Any] = Field(default_factory=dict)
    # V2 3D UI가 직접 던지는 팩 키 오버라이드 (예: {"slurry_ph": 11.0}).
    # 구성요소 경로를 거치지 않고 팩터를 즉시 흔들 수 있는 통로다.
    pack_overrides: Dict[str, float] = Field(default_factory=dict)
    model: str = "tier1.preston_radial"


@app.get("/api/health")
def health():
    return {"ok": True, "version": "0.3.0", "models": available_models()}


@app.get("/api/catalog")
def catalog():
    """UI가 화면을 그리는 데 필요한 전부 — 슬롯·구현·출처·팩."""
    reg = S.slots()
    slots = []
    for sid in S.SLOT_ORDER:
        slots.append({
            "id": sid, "label": S.SLOT_LABEL[sid], "owner": S.SLOT_OWNER[sid],
            "impls": [{
                "id": im.id, "label": im.label, "status": im.status,
                "note": im.note, "agent": im.agent, "warning": im.warning,
                "params": im.params,
            } for im in reg[sid].values()],
        })
    packs = []
    for name in available_packs():
        try:
            pk = load_pack(name)
            conf: Dict[str, int] = {}
            for prm in pk.params.values():
                conf[prm.confidence] = conf.get(prm.confidence, 0) + 1
            packs.append({"id": name, "description": pk.description,
                          # 사람이 읽는 이름·막질군 (2026-09-11 사용자 지시:
                          # 내부 ID를 UI에 그대로 노출하지 않는다)
                          **{k: v for k, v in pack_meta(name).items() if k != "id"},
                          "confidence_counts": conf,
                          "params": [{"key": p.key, "value": p.value, "unit": p.unit,
                                      "confidence": p.confidence,
                                      "source": p.source} for p in pk.params.values()]})
        except Exception as e:
            packs.append({"id": name, "error": str(e), **{k: v for k, v in pack_meta(name).items() if k != "id"}})
    pack_groups = grouped([p["id"] for p in packs])
    comps = []
    for cname, spec in load_schemas().items():
        comps.append({
            "id": cname, "label": spec.get("component", cname),
            "owner": spec.get("owner"), "description": spec.get("description", ""),
            "groups": [{
                "id": g["id"], "label": g.get("label", g["id"]),
                "origin": g.get("origin"), "owner": g.get("owner", spec.get("owner")),
                "why": g.get("why", ""),
                "fields": [{
                    "path": f"{cname}.{g['id']}.{fl['key']}",
                    "key": fl["key"], "label": fl.get("label", fl["key"]),
                    "type": fl.get("type", "text"), "unit": fl.get("unit", ""),
                    "options": fl.get("options"), "typical": fl.get("typical"),
                    "origin": fl.get("origin"), "status": fl.get("status"),
                    "maps_to": fl.get("maps_to"), "confidence": fl.get("confidence"),
                    "note": fl.get("note", ""),
                } for fl in g.get("fields", [])],
            } for g in spec.get("groups", [])],
        })
    return {"slots": slots, "default_config": S.default_config(), "packs": packs,
            "pack_groups": pack_groups,
            "components": comps, "coverage": coverage()}


@app.post("/api/simulate")
def api_simulate(req: SimRequest):
    comp_over, comp_warn = to_overrides(req.components) if req.components else ({}, [])
    try:
        rec = Recipe(
            pack_overrides=comp_over,
            pack=req.pack, wafer=req.wafer,  # type: ignore[arg-type]
            pressure_psi=req.pressure_psi, rpm_wafer=req.rpm_wafer,
            rpm_platen=req.rpm_platen, time_s=req.time_s,
            initial_thickness_nm=req.initial_thickness_nm,
            zone_pressures_psi=req.zone_pressures_psi,
            zone_edges_norm=req.zone_edges_norm, meta=req.meta,
        ).resolve()
    except KeyError as e:
        raise HTTPException(400, f"팩 해석 실패: {e}")

    r_max = rec.wafer_radius_m - rec.edge_exclusion_m
    radius = np.linspace(0.0, r_max, rec.n_points)
    try:
        mrr, notes, trace = S.run_pipeline(rec, radius, req.slots)
    except KeyError as e:
        raise HTTPException(400, str(e))

    mrr_nm = mrr * 1e9 * 60
    removed = mrr_nm * (rec.time_s / 60)
    remaining = (rec.initial_thickness_nm - removed
                 if rec.initial_thickness_nm else None)
    m = compute_metrics(radius, removed if remaining is None else remaining,
                        n_points=rec.n_points)
    return {
        "mrr_mean_nm_min": float(np.mean(mrr_nm)),
        "mrr_min_nm_min": float(np.min(mrr_nm)),
        "mrr_max_nm_min": float(np.max(mrr_nm)),
        "removed_mean_nm": float(np.mean(removed)),
        "remaining_mean_nm": float(np.mean(remaining)) if remaining is not None else None,
        "metrics": {
            "ttv_nm": m.ttv_nm, "cv_pct": m.cv_pct,
            "radial_sigma_pct": m.radial_sigma_pct,
            "radial_range_pct": m.radial_range_pct,
            "radial_maxring_range_nm": m.radial_maxring_range_nm,
            "wiwnu_3sigma_pct": m.wiwnu_3sigma_pct,
            "wiwnu_halfrange_pct": m.wiwnu_halfrange_pct,
            "definition": m.definition,
        },
        "profile": {"radius_mm": (radius * 1000).round(2).tolist(),
                    "mrr_nm_min": mrr_nm.round(3).tolist()},
        "trace": trace,
        "notes": notes + comp_warn,
        "component_overrides": comp_over,
        "component_warnings": comp_warn,
        "not_computed": ["roughness_ra", "dishing", "erosion",
                         "metal_contamination", "defect_density"],
    }


@app.post("/api/simulate/v2")
def api_simulate_v2(req: SimRequest):
    """V2 엔드포인트 — 3D 인터페이스가 쓰는 통합 결과.

    /api/simulate(슬롯 파이프라인)와 달리 engine.simulate()를 그대로 태워서
    **병합 파라미터 + 장비 출력값**을 함께 돌려준다. 3D 화면의 각 파트를
    클릭했을 때 보여줄 것이 전부 여기 들어 있다.
    """
    from sim.engine import simulate as _simulate

    comp_over, comp_warn = to_overrides(req.components) if req.components else ({}, [])
    # 3D UI는 팩 키를 직접 던진다(예: slurry_ph). 구성요소 경로와 합친다.
    overrides = dict(comp_over)
    overrides.update(req.pack_overrides or {})
    try:
        res = _simulate(Recipe(
            pack=req.pack, wafer=req.wafer,  # type: ignore[arg-type]
            pressure_psi=req.pressure_psi, rpm_wafer=req.rpm_wafer,
            rpm_platen=req.rpm_platen, time_s=req.time_s,
            initial_thickness_nm=req.initial_thickness_nm,
            zone_pressures_psi=req.zone_pressures_psi,
            zone_edges_norm=req.zone_edges_norm, meta=req.meta,
            pack_overrides=overrides,
        ), model=req.model)
    except KeyError as e:
        raise HTTPException(400, f"팩 해석 실패: {e}")
    except Exception as e:
        raise HTTPException(400, f"{type(e).__name__}: {e}")

    s = res.summary()
    s["profile"] = {
        "radius_mm": (res.radius_m * 1000).round(2).tolist(),
        "mrr_nm_min": res.mrr_nm_per_min.round(3).tolist(),
        "removed_nm": res.removed_nm.round(3).tolist(),
        "remaining_nm": (res.remaining_nm.round(3).tolist()
                         if res.remaining_nm is not None else None),
    }
    s["component_warnings"] = comp_warn
    s["provenance"] = res.provenance
    # ── 모든 실행을 DB에 저장 (사용자 지시: 다음 시뮬레이션에 반영) ──────
    # 저장 실패가 시뮬레이션을 죽이면 안 된다 — 결과는 돌려주고 경고만 싣는다.
    try:
        from sim import store as _store
        inputs = {"pack": req.pack, "wafer": req.wafer, "model": req.model,
                  "pressure_psi": req.pressure_psi, "rpm_wafer": req.rpm_wafer,
                  "rpm_platen": req.rpm_platen, "time_s": req.time_s,
                  "initial_thickness_nm": req.initial_thickness_nm,
                  "zone_pressures_psi": req.zone_pressures_psi,
                  "pack_overrides": overrides}
        s["run_id"] = _store.save_run(s, inputs)
    except Exception as e:
        s["run_id"] = None
        s.setdefault("notes", []).append(f"⚠ 런 저장 실패: {type(e).__name__}: {e}")
    return s


# ═══════════════════════════════════════ 런 저장소 · 실측 임포트

@app.get("/api/runs")
def api_runs(limit: int = 50, pack: Optional[str] = None):
    from sim import store
    return {"runs": store.recent_runs(limit=limit, pack=pack), "stats": store.stats()}


@app.get("/api/runs/{rid}")
def api_run(rid: str):
    from sim import store
    r = store.get_run(rid)
    if not r:
        raise HTTPException(404, "없는 run id")
    return r


@app.get("/api/measurements")
def api_measurements(limit: int = 100):
    from sim import store
    return {"measurements": store.list_measurements(limit=limit)}


@app.post("/api/import")
async def api_import(file: UploadFile = File(...),
                     pack_hint: Optional[str] = Form(None),
                     label: Optional[str] = Form(None)):
    """엑셀/CSV/JSON 실측 파일을 그대로 넣으면 DB에 쌓인다.

    사용자 지시: "엑셀이나 다른 포맷 real data 파일을 넣으면 그냥 그대로
    빅데이터가 프로그램에 입력되도록".

    컬럼 매핑은 tools/ingest_measurement.py의 별칭 표를 쓴다(압력/psi/다운포스…).
    ⚠ 매핑이 안 되는 컬럼은 버리지 않고 `unmapped_columns`로 돌려준다.
      조건(압력·시간)이 없으면 저장은 하되 `comparable: false` — 시뮬레이션과
      비교할 수 없다는 사실을 숨기지 않는다.
    """
    import tempfile
    from sim import store
    sys.path.insert(0, str(ROOT / "tools"))
    import ingest_measurement as ing

    suffix = Path(file.filename or "upload").suffix.lower() or ".csv"
    if suffix not in (".csv", ".xlsx", ".xls", ".json", ".tsv", ".txt"):
        raise HTTPException(400, f"지원하지 않는 형식: {suffix} (csv/xlsx/json)")
    data = await file.read()
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        tmp.write(data)
        tmp_path = Path(tmp.name)
    try:
        r = ing.ingest(tmp_path, run_id=label or "upload", peek=True)
    except SystemExit as e:
        raise HTTPException(400, str(e))
    except Exception as e:
        raise HTTPException(400, f"파싱 실패: {type(e).__name__}: {e}")
    finally:
        tmp_path.unlink(missing_ok=True)

    r["source_file"] = file.filename
    quality = {"blockers": r["blockers"], "warnings": r["warnings"],
               "unmapped_columns": r["unmapped_columns"],
               "column_mapping": r["column_mapping"], "comparable": r["comparable"]}
    mid = store.save_measurement(
        source_file=file.filename or "upload", conditions=r["conditions"],
        points=r["points"], quality=quality, run_label=label, pack_hint=pack_hint)
    iid = store.save_import(file.filename or "upload", r["n_points"], 1,
                            r["blockers"] + r["warnings"])
    return {"measurement_id": mid, "import_id": iid,
            "n_points": r["n_points"], "conditions": r["conditions"],
            "column_mapping": r["column_mapping"],
            "unmapped_columns": r["unmapped_columns"],
            "blockers": r["blockers"], "warnings": r["warnings"],
            "comparable": r["comparable"],
            "mrr_mean": store.get_measurement(mid)["mrr_mean"],
            "stats": store.stats()}


@app.get("/api/calibration/{pack}")
def api_calibration(pack: str):
    """이 팩에 대해 DB의 실측이 만드는 Kp 보정계수 — 실측이 반영되는 유일한 통로."""
    from sim import store
    from sim.engine import simulate as _simulate

    def _predict(cond):
        kw = {k: cond[k] for k in ("pressure_psi", "rpm_wafer", "rpm_platen", "time_s")
              if k in cond}
        return float(np.mean(_simulate(Recipe(pack=pack, **kw)).mrr_nm_per_min))

    cal = store.calibration_factor(pack, _predict)
    return cal.to_dict()


@app.get("/api/additives")
def api_additives():
    """첨가제 카탈로그 — 카테고리·케미컬·대상 막질·전형 농도·엔진 키.

    knowledge/additives/catalog.yaml 이 없으면 빈 카탈로그(UI는 '카탈로그 없음' 표시).
    """
    import yaml
    p = ROOT / "knowledge" / "additives" / "catalog.yaml"
    if not p.exists():
        return {"categories": {}, "chemicals": [], "note": "catalog.yaml not found"}
    d = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
    return {"categories": d.get("categories", {}), "chemicals": d.get("chemicals", [])}


@app.get("/api/npw")
def api_npw():
    """NPW(블랭킷 웨이퍼) 카탈로그 — 스택·초기값 범위."""
    import yaml
    p = ROOT / "knowledge" / "wafers" / "npw_catalog.yaml"
    if not p.exists():
        return {"wafers": [], "note": "npw_catalog.yaml not found"}
    d = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
    return {"wafers": d.get("wafers", [])}


@app.get("/api/performance/{part}")
def api_performance(part: str):
    """패드/디스크 성능 결정 인자 — 범위·근거·영향 방향·엔진 연결."""
    import yaml
    if part not in ("pad", "disk"):
        raise HTTPException(404, "pad | disk")
    p = ROOT / "knowledge" / "performance" / f"{part}.yaml"
    if not p.exists():
        return {"factors": [], "note": f"{part}.yaml not found"}
    d = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
    return {"factors": d.get("factors", []), "meta": {k: v for k, v in d.items() if k != "factors"}}


@app.get("/api/factors/lineage/{pack}")
def api_factor_lineage(pack: str):
    """팩터 계보 — 어떤 입력 항목에서 어떤 파라미터가 산출되는지.

    사용자 지시: "수많은 데이터에서 뽑아낸 파라미터들을 표시해. 어떤 항목들에서
    어떤 파라미터가 산출되었는지 확인할 수 있게."

    기준 조건에서 팩터를 계산해 drivers(입력 필드→값)·terms(항별 기여)·sources(문헌)를
    그대로 돌려준다. 미모델링 팩터는 왜 없는지(필요 파라미터)를 표시한다.
    """
    from sim.engine import simulate as _sim
    from sim.factors import FACTOR_SPEC
    from sim.store import get_setting
    overrides = get_setting("factor_symbols", {}) or {}
    try:
        res = _sim(Recipe(pack=pack))
    except ParamMissing as e:
        raise HTTPException(422, str(e))
    out = []
    for key, (sym, name, axis, parts) in FACTOR_SPEC.items():
        f = (res.factors or {}).get(key)
        d = f.to_dict() if f is not None else {
            "key": key, "symbol": sym, "name": name, "axis": axis, "parts": parts,
            "value": None, "status": "unmodeled", "drivers": {}, "terms": {},
            "confidence": "unverified", "sources": [], "notes": [], "mrr_coupled": False}
        d["symbol"] = overrides.get(key, sym)
        d["default_symbol"] = sym
        out.append(d)
    return {"pack": pack, "factors": out}


@app.get("/api/factors")
def api_factors():
    """병합 파라미터 정의 — UI가 축·파트 매핑을 그리는 데 쓴다.

    symbol은 사용자가 바꿀 수 있다(/api/factors/symbols). 기본 기호는 FACTOR_SPEC.
    """
    from sim.factors import FACTOR_SPEC, MRR_COUPLED
    from sim.store import get_setting
    overrides = get_setting("factor_symbols", {}) or {}
    return {"factors": [
        {"key": k, "symbol": overrides.get(k, sym), "default_symbol": sym,
         "name": name, "axis": axis, "parts": parts,
         "mrr_coupled": k in MRR_COUPLED}
        for k, (sym, name, axis, parts) in FACTOR_SPEC.items()]}


class SymbolMap(BaseModel):
    symbols: Dict[str, str]


@app.post("/api/factors/symbols")
def api_set_symbols(body: SymbolMap):
    """팩터 기호 변경 — DB settings에 저장되어 서버 재시작 후에도 유지된다.

    빈 문자열이면 기본 기호로 되돌린다. 기호는 1~3자.
    """
    from sim.factors import FACTOR_SPEC
    from sim.store import get_setting, set_setting
    cur = get_setting("factor_symbols", {}) or {}
    for k, v in body.symbols.items():
        if k not in FACTOR_SPEC:
            raise HTTPException(400, f"알 수 없는 팩터: {k}")
        v = (v or "").strip()
        if not v:
            cur.pop(k, None)
        elif len(v) > 3:
            raise HTTPException(400, f"기호는 1~3자: {k}={v!r}")
        else:
            cur[k] = v
    set_setting("factor_symbols", cur)
    return {"ok": True, "symbols": cur}


class TimelineRequest(BaseModel):
    """스택 연마 시간축 요청.

    layers: 위→아래. 각 {name, thickness_nm, pack|null, stop?, color?}
    pack이 null인 층은 이전 층 팩의 선택비로 근사하거나(있으면) 멈춘다.
    """
    layers: List[Dict[str, Any]]
    total_s: float = 120.0
    dt_s: float = 2.0
    pressure_psi: Optional[float] = None
    platen_rpm: Optional[float] = None
    wafer_rpm: Optional[float] = None
    slurry_flow_ml_min: Optional[float] = None
    zone_pressures_psi: Optional[List[float]] = None
    zone_edges_norm: Optional[List[float]] = None
    pack_overrides: Optional[Dict[str, float]] = None


@app.post("/api/timeline")
def api_timeline(body: TimelineRequest):
    """연마 중 두께 변화 — 프레임별 층 잔량(반경별)·MRR·온도·μ·토크."""
    from sim.timeline import Layer, run_timeline
    if not body.layers:
        raise HTTPException(400, "layers가 비어 있다")
    layers = []
    for L in body.layers:
        try:
            layers.append(Layer(name=str(L["name"]), thickness_nm=float(L["thickness_nm"]),
                                pack=L.get("pack") or None, stop=bool(L.get("stop", False)),
                                color=str(L.get("color", "#7fb3ff"))))
        except (KeyError, ValueError, TypeError) as e:
            raise HTTPException(400, f"층 정의 오류 {L}: {e}")
    kw: Dict[str, Any] = {"pack": layers[0].pack or "oxide_silica"}
    for f in ("pressure_psi", "platen_rpm", "wafer_rpm", "slurry_flow_ml_min",
              "zone_pressures_psi", "zone_edges_norm", "pack_overrides"):
        v = getattr(body, f)
        if v is not None:
            kw[f] = v
    try:
        res = run_timeline(layers, Recipe(**kw), total_s=body.total_s, dt_s=body.dt_s)
    except ValueError as e:
        raise HTTPException(400, str(e))
    except ParamMissing as e:
        raise HTTPException(422, str(e))
    return res.to_dict()


@app.get("/api/scope/{agent}")
def api_scope(agent: str):
    sys.path.insert(0, str(ROOT / "tools"))
    try:
        import scope
    except Exception:
        raise HTTPException(503, "SCOPE.yaml 없음 (배포본에는 조사범위가 포함되지 않습니다)")
    try:
        e = scope.effective(agent)
    except Exception as ex:
        raise HTTPException(404, str(ex))
    e["queries"] = scope.queries(agent)
    return e


_INDEX = Path(__file__).resolve().parent / "web" / "index.html"
_STUDIO3D = Path(__file__).resolve().parent / "web" / "studio3d.html"
_DEMO = Path(__file__).resolve().parent / "web" / "demo.html"
_BASIS = ROOT / "validation" / "MODEL-BASIS.md"


@app.get("/demo", response_class=HTMLResponse)
def demo_landing():
    """비공개 데모 랜딩(영어) — 면접관용. FABSIM_DEMO=1이면 '/'도 여기로 온다.

    {{FABSIM_*}} 토큰은 sim.web_facts.landing_facts() 가 실제 아티팩트에서
    산출한 값으로 치환한다 — 손으로 유지하는 숫자가 조용히 틀어지는 것을 막는다.
    """
    from sim.web_facts import landing_facts

    body = _DEMO.read_text(encoding="utf-8")
    for key, value in landing_facts().items():
        body = body.replace("{{" + key + "}}", value)
    return HTMLResponse(body, headers={"Cache-Control": "no-store"})


@app.get("/basis", response_class=HTMLResponse)
def basis_report():
    """근거 보고서(MODEL-BASIS.md)를 그대로 보여준다 — 자동 생성물이라 손대지 않는다."""
    if not _BASIS.exists():
        raise HTTPException(404, "MODEL-BASIS.md not in this build")
    import html as _h
    body = _h.escape(_BASIS.read_text(encoding="utf-8"))
    page = ("<!doctype html><meta charset=utf-8><title>FabSim — model basis</title>"
            "<style>body{background:#0b0d10;color:#e6e8eb;font:14px/1.5 ui-monospace,Menlo,monospace;"
            "max-width:1000px;margin:0 auto;padding:32px 20px}pre{white-space:pre-wrap;word-break:break-word}"
            "a{color:#5ec1ff}</style><a href='/demo'>← demo</a><pre>" + body + "</pre>")
    return HTMLResponse(page, headers={"Cache-Control": "no-store"})


@app.get("/3d", response_class=HTMLResponse)
def studio3d():
    """3D 스튜디오 — V2의 메인 화면 (ARCHITECTURE-V2.md §0).

    실제 장비 모양을 그리고, 각 부위를 클릭하면 그 파트의 설정 패널이 열린다.

    ⚠ 캐시 금지: 이 파일은 개발 중 수시로 바뀐다. 캐시 헤더가 없으면 폰 브라우저가
    구버전을 계속 보여주고, 사용자에겐 "고친 게 반영이 안 됐다"로 보인다
    (2026-09-11 실제 발생 — 새 탭이 안 보인다는 보고). 매번 새로 받게 한다.
    """
    if _STUDIO3D.exists():
        html = _STUDIO3D.read_text()
        # 화면에 파일 수정 시각을 박아 "지금 보는 게 최신인가"를 눈으로 확인하게 한다.
        stamp = datetime.fromtimestamp(_STUDIO3D.stat().st_mtime).strftime("%m-%d %H:%M")
        html = html.replace(
            '<span id="buildTag"',
            f'<span id="buildTag" data-build="{stamp}"',
        )
        return HTMLResponse(
            html,
            headers={
                "Cache-Control": "no-store, no-cache, must-revalidate, max-age=0",
                "Pragma": "no-cache",
                "Expires": "0",
            },
        )
    raise HTTPException(404, "studio3d.html 없음")


@app.get("/manifest.webmanifest")
def manifest():
    """PWA 매니페스트 — 폰에서 '홈 화면에 추가'하면 주소창 없는 전체화면 앱이 된다.

    3D 뷰가 44vh밖에 안 되는 폰에서 사파리 주소창·툴바가 차지하는 ~150px는 크다.
    standalone 표시 모드가 그걸 없앤다. 아이콘은 의존성 없이 인라인 SVG로 낸다.
    """
    from fastapi.responses import JSONResponse
    return JSONResponse({
        "name": "FabSim — CMP Simulator",
        "short_name": "FabSim",
        "start_url": "/3d",
        "scope": "/",
        "display": "standalone",
        "orientation": "any",
        "background_color": "#0b0f14",
        "theme_color": "#0b0f14",
        "icons": [{"src": "/icon.svg", "sizes": "any", "type": "image/svg+xml",
                   "purpose": "any maskable"}],
    }, media_type="application/manifest+json")


@app.get("/icon.svg")
def icon():
    from fastapi.responses import Response
    svg = (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512">'
        '<rect width="512" height="512" rx="96" fill="#0b0f14"/>'
        '<circle cx="256" cy="272" r="150" fill="none" stroke="#243141" stroke-width="26"/>'
        '<circle cx="256" cy="272" r="96" fill="none" stroke="#4da3ff" stroke-width="26"/>'
        '<circle cx="256" cy="272" r="30" fill="#4da3ff"/>'
        '<rect x="176" y="86" width="160" height="34" rx="17" fill="#5ddc9a"/>'
        '</svg>')
    return Response(svg, media_type="image/svg+xml")


@app.get("/", response_class=HTMLResponse)
def index():
    if os.environ.get("FABSIM_DEMO") == "1":
        return demo_landing()
    if _INDEX.exists():
        return _INDEX.read_text()
    return "<h1>FabSim API</h1><p>/docs 에서 API 문서를 보십시오.</p>"


def main() -> int:
    import uvicorn
    import os
    uvicorn.run(app, host=os.environ.get("FABSIM_HOST", "0.0.0.0"),
                port=int(os.environ.get("FABSIM_PORT", 8080)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
