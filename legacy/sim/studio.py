"""FabSim Studio — 시뮬레이터 껍데기.

2026-09-05 사용자 지시:
  "시뮬레이션 툴 껍데기부터 만들어서 시각적으로 보여지는 시뮬레이션 모식도나
   클릭만으로 갈아끼울 수 있는 인터페이스를 구현해야 해"

3개 탭:
  ① 파이프라인 — CMP 모식도 + 슬롯별 구현 교체(클릭). 물리 모델을 갈아끼운다.
  ② 물성 팩   — 어떤 물질 묶음으로 돌릴 것인가. 값의 신뢰도가 색으로 보인다.
  ③ 조사 범위 — 에이전트가 무엇을·어떻게·어디까지 조사할지. SCOPE.yaml을 편집.

정본은 항상 파일이다(SCOPE.yaml, knowledge/params/*.yaml). UI는 그 파일을 보여주고
편집하는 창일 뿐이라, 여기서 바꾼 것이 크론 학습에 그대로 반영된다.

실행: streamlit run sim/studio.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import streamlit as st

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from sim.engine import Recipe, simulate, available_models  # noqa: E402
import sim.slots as S  # noqa: E402

SCOPE_F = ROOT / "agents" / "SCOPE.yaml"
PACK_DIR = ROOT / "knowledge" / "params"

st.set_page_config(page_title="FabSim Studio", layout="wide")

STATUS_COLOR = {"verified": "#7ee787", "sourced": "#79c0ff",
                "warn": "#f0883e", "unsourced": "#f85149"}
STATUS_LABEL = {"verified": "검증됨", "sourced": "출처있음",
                "warn": "주의", "unsourced": "근거없음"}
CONF_COLOR = {"verified": "#7ee787", "literature": "#79c0ff",
              "estimated": "#f0883e", "unverified": "#f85149"}


# ══════════════════════════════════════════════════ 사이드바: 레시피
def recipe_sidebar():
    st.sidebar.header("레시피")
    packs = sorted(p.stem for p in PACK_DIR.glob("*.yaml") if p.stem != "base")
    pack = st.sidebar.selectbox("물성 팩", packs,
                                index=packs.index("oxide_silica") if "oxide_silica" in packs else 0)
    wafer = st.sidebar.radio("웨이퍼", ["NPW", "PTW"], horizontal=True)
    press = st.sidebar.slider("압력 [psi]", 0.5, 8.0, 3.0, 0.1)
    rw = st.sidebar.slider("웨이퍼 rpm", 10, 150, 60, 5)
    rp = st.sidebar.slider("플래튼 rpm", 10, 150, 55, 5)
    t = st.sidebar.slider("시간 [s]", 5, 300, 60, 5)
    meta = {}
    if wafer == "PTW":
        meta["pattern_density"] = str(st.sidebar.slider("패턴 밀도 ρ", 0.05, 1.0, 0.5, 0.05))
    ph = st.sidebar.number_input("패드 사용시간 [h]", 0, 500, 0, 10)
    if ph:
        meta["pad_hours"] = str(ph)
    zon = st.sidebar.checkbox("멀티존 헤드")
    zp = ze = None
    if zon:
        c = st.sidebar.columns(3)
        zp = [c[i].number_input(f"존{i+1}", 0.5, 8.0, [3.0, 3.0, 4.5][i], 0.1,
                                key=f"z{i}") for i in range(3)]
        ze = [0.5, 0.8, 1.0]
    thick = st.sidebar.number_input("초기 막두께 [nm] (0=제거량만)", 0, 20000, 1000, 100)
    return Recipe(pack=pack, wafer=wafer,  # type: ignore[arg-type] pressure_psi=press, rpm_wafer=rw,
                  rpm_platen=rp, time_s=float(t), meta=meta,
                  zone_pressures_psi=zp, zone_edges_norm=ze,   # type: ignore[arg-type]
                  initial_thickness_nm=float(thick) if thick else None)


# ══════════════════════════════════════════════════ ① 파이프라인
def tab_pipeline(recipe):
    st.subheader("CMP 파이프라인 — 클릭으로 물리 모델 교체")
    st.caption("각 단계에서 어떤 물리를 쓸지 고른다. 색 = 근거 상태. "
               "빨강(근거없음)은 그 결과를 신뢰하면 안 된다는 뜻이다.")

    reg = S.slots()
    if "slot_cfg" not in st.session_state:
        st.session_state.slot_cfg = S.default_config()
    cfg = st.session_state.slot_cfg

    cols = st.columns(len(S.SLOT_ORDER))
    for col, slot in zip(cols, S.SLOT_ORDER):
        impls = reg[slot]
        with col:
            st.markdown(f"**{S.SLOT_LABEL[slot]}**")
            st.caption(f"담당: {S.SLOT_OWNER[slot]}")
            ids = list(impls)
            cur = cfg.get(slot, ids[0])
            pick = st.radio(S.SLOT_LABEL[slot], ids,
                            index=ids.index(cur) if cur in ids else 0,
                            key=f"slot_{slot}",
                            format_func=lambda i, s=slot: impls[i].label,
                            label_visibility="collapsed")
            cfg[slot] = pick
            im = impls[pick]
            c = STATUS_COLOR[im.status]
            st.markdown(
                f"<span style='color:{c};font-size:12px'>● {STATUS_LABEL[im.status]}</span>",
                unsafe_allow_html=True)
            if im.note and im.note != "—":
                st.caption(f"📄 {im.note.split('/')[-1]}")
            if im.agent:
                st.caption(f"👤 {im.agent}")
            if im.warning:
                st.warning(im.warning, icon="⚠")

    st.divider()
    if st.button("▶ 실행", type="primary", use_container_width=True):
        st.session_state.run = True

    if not st.session_state.get("run"):
        st.info("좌측에서 레시피를 정하고 ▶ 실행을 누르십시오.")
        return

    try:
        rr = recipe.resolve()
        r_max = rr.wafer_radius_m - rr.edge_exclusion_m
        radius = np.linspace(0.0, r_max, rr.n_points)
        mrr, notes, trace = S.run_pipeline(rr, radius, cfg)
    except Exception as e:
        st.error(f"{type(e).__name__}: {e}")
        return

    from sim.metrics.uniformity import compute_metrics
    mrr_nm = mrr * 1e9 * 60
    removed = mrr_nm * (rr.time_s / 60)
    remaining = (rr.initial_thickness_nm - removed
                 if rr.initial_thickness_nm else None)
    m = compute_metrics(radius, removed if remaining is None else remaining,
                        n_points=rr.n_points)

    k = st.columns(5)
    k[0].metric("평균 MRR", f"{np.mean(mrr_nm):.1f}", "nm/min")
    k[1].metric("TTV", f"{m.ttv_nm:.2f}", "nm")
    k[2].metric("radial σ", f"{m.radial_sigma_pct:.3f}", "% (문헌 default)")
    k[3].metric("CV", f"{m.cv_pct:.3f}", "%")
    k[4].metric("WIWNU(3σ)", f"{m.wiwnu_3sigma_pct:.3f}", "%")

    with st.expander("추가 지표 (회사 관행 포함)"):
        st.markdown(
            f"- TTV(SEMI MF1530): **{m.ttv_nm:.3f} nm**\n"
            f"- radial range: **{m.radial_range_pct:.3f} %** (문헌 default 후보 2)\n"
            f"- radial max-ring range: **{m.radial_maxring_range_nm:.3f} nm** "
            f"(링 #{m.radial_maxring_range_ring}) — ⚠ 회사 관행 정의, 문헌 근거 약함\n"
            f"- WIWNU(½range): **{m.wiwnu_halfrange_pct:.3f} %**")
        st.caption(m.definition)

    left, right = st.columns([2, 1])
    with left:
        st.markdown("**반경 프로파일**")
        import pandas as pd
        st.line_chart(pd.DataFrame(
            {"MRR [nm/min]": mrr_nm}, index=(radius * 1000).round(1)))
    with right:
        st.markdown("**실행 경로**")
        for t in trace:
            c = STATUS_COLOR[t["status"]]
            st.markdown(
                f"<div style='font-size:12px'>"
                f"<span style='color:{c}'>●</span> "
                f"<b>{S.SLOT_LABEL[t['slot']]}</b><br>"
                f"<span style='color:#8b949e;padding-left:14px'>{t['label']}</span></div>",
                unsafe_allow_html=True)

    miss = ["조도 Ra", "dishing", "erosion", "금속오염", "결함밀도"]
    st.info("**미산출**: " + ", ".join(miss) + " — 담당 에이전트 학습 대기 중. "
            "이 값들은 지어내지 않고 비워 둔다.", icon="ℹ")
    if notes:
        st.warning("**모델 한계 보고**\n\n" + "\n\n".join(f"- {n}" for n in notes), icon="⚠")


# ══════════════════════════════════════════════════ ② 물성 팩
def tab_packs(recipe):
    st.subheader("물성 팩 — 어떤 물질로 돌리나")
    st.caption("팩 하나를 바꾸면 같은 엔진이 다른 공정이 된다. "
               "코드는 한 줄도 안 고친다. 색 = 값의 신뢰도.")
    import yaml
    packs = sorted(p for p in PACK_DIR.glob("*.yaml"))
    sel = st.selectbox("팩", [p.stem for p in packs],
                       index=[p.stem for p in packs].index(recipe.pack)
                       if recipe.pack in [p.stem for p in packs] else 0)
    f = PACK_DIR / f"{sel}.yaml"
    data = yaml.safe_load(f.read_text()) or {}
    st.caption(data.get("description", ""))
    if data.get("base"):
        st.caption(f"상속: {data['base']}")

    rows = []
    for k, v in (data.get("params") or {}).items():
        if not isinstance(v, dict):
            v = {"value": v}
        rows.append({
            "파라미터": k,
            "값": v.get("value"),
            "단위": v.get("unit", ""),
            "신뢰도": v.get("confidence", "unverified"),
            "출처": (v.get("source") or "").split("/")[-1],
        })
    if rows:
        import pandas as pd
        df = pd.DataFrame(rows)

        def color(s):
            return [f"color: {CONF_COLOR.get(x, '#8b949e')}" for x in s]
        st.dataframe(df.style.apply(color, subset=["신뢰도"]),
                     use_container_width=True, hide_index=True)

    est = [r for r in rows if r["신뢰도"] in ("estimated", "unverified")]
    if est:
        st.warning(f"**{len(est)}개 파라미터가 미검증/추정값입니다** — "
                   + ", ".join(r["파라미터"] for r in est)
                   + ". 실데이터 캘리브레이션(M3)이 이 값들을 덮습니다.", icon="⚠")
    with st.expander("원본 YAML"):
        st.code(f.read_text(), language="yaml")


# ══════════════════════════════════════════════════ ③ 조사 범위
def tab_scope():
    st.subheader("조사 범위 — 에이전트가 무엇을·어떻게·어디까지 조사하나")
    st.caption(f"정본: `{SCOPE_F.relative_to(ROOT)}`. "
               "여기서 바꾸면 학습 크론이 다음 실행부터 그대로 따릅니다.")
    sys.path.insert(0, str(ROOT / "tools"))
    import importlib
    scope = importlib.import_module("scope")
    importlib.reload(scope)

    import yaml
    cfg = yaml.safe_load(SCOPE_F.read_text()) or {}
    agents_dir = sorted(d.name for d in (ROOT / "agents").iterdir()
                        if d.is_dir() and (d / "PROFILE.md").exists())
    overridden = list((cfg.get("agents") or {}).keys())

    sel = st.selectbox(
        "에이전트", agents_dir,
        index=agents_dir.index(overridden[0]) if overridden else 0,
        format_func=lambda a: f"{a}  {'⚙ 개별설정' if a in overridden else '· 기본값'}")

    e = scope.effective(sel)
    if e["focus"]:
        st.info(f"**집중 범위**\n\n{e['focus']}", icon="🎯")

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**허용 소스** (가중치 순)")
        for s in sorted(e["enabled_sources"], key=lambda x: -x.get("weight", 0)):
            st.markdown(f"- `{s.get('weight', 0):.1f}` **{s.get('label', s['id'])}**")
            if s.get("note"):
                st.caption(f"　{s['note']}")
        off = [s for s in e["sources"].values() if not s.get("enabled", True)]
        if off:
            st.markdown("**금지 소스**")
            for s in off:
                st.markdown(f"- ~~{s.get('label', s['id'])}~~ — {s.get('note', '')}")
    with c2:
        m = e["method"]
        st.markdown("**조사 방법**")
        st.markdown(f"""
- 단원당 인용 상한 **{m.get('max_sources_per_unit')}건**
- 1차 출처 최소 **{m.get('min_primary_per_unit')}건**
- 최근 **{m.get('prefer_recent_years')}년** 우선
- DOI 실존 검증 **{'ON' if m.get('require_doi_check') else 'OFF'}**
- verify 블록 강제 **{'ON' if m.get('require_verify_block') else 'OFF'}**
- 유료 논문 폴백 **{'ON' if m.get('paywall_fallback') else 'OFF'}**
""")
        x = e["exclude"]
        st.markdown("**제외 규칙**")
        if x.get("keywords"):
            st.markdown("- 키워드: " + ", ".join(f"`{k}`" for k in x["keywords"]))
        if x.get("before_year"):
            st.markdown(f"- {x['before_year']}년 이전 (고전 예외 제외)")
        if x.get("note"):
            st.caption(x["note"])

    st.divider()
    st.markdown("**생성되는 검색어**")
    st.code("\n".join(scope.queries(sel)), language="text")

    st.markdown("**자료 판정 시험** — 이 문헌을 쓸 수 있나?")
    q = st.text_input("논문·특허 제목", placeholder="예: Electroplating of copper interconnects 2020")
    if q:
        r = scope.check(q, sel)
        if r["allowed"]:
            st.success("✓ 범위 안 — 사용 가능")
        else:
            st.error("✗ 범위 밖 — " + "; ".join(r["reasons"]))

    with st.expander("SCOPE.yaml 직접 편집"):
        txt = st.text_area("SCOPE.yaml", SCOPE_F.read_text(), height=420,
                           label_visibility="collapsed")
        if st.button("저장", type="primary"):
            try:
                yaml.safe_load(txt)
            except Exception as ex:
                st.error(f"YAML 오류 — 저장하지 않음: {ex}")
            else:
                SCOPE_F.write_text(txt)
                st.success("저장됨. 다음 크론 실행부터 반영됩니다.")


# ══════════════════════════════════════════════════
st.title("FabSim Studio")
st.caption("CMP 시뮬레이터 — 물리 모델·물성·조사 범위를 갈아끼운다")
recipe = recipe_sidebar()
t1, t2, t3 = st.tabs(["① 파이프라인", "② 물성 팩", "③ 조사 범위"])
with t1:
    tab_pipeline(recipe)
with t2:
    tab_packs(recipe)
with t3:
    tab_scope()
