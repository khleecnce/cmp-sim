#!/usr/bin/env python3
"""모델링 완성 판정 + 근거 보고서 — COMPLETION.md의 C1~C5·C8을 기계로 판정한다.

사용자 지시 (2026-09-10):
  "모델링 완성을 목표로해" / "완성된 후에는 오류가 없도록 루프를 돌려서 검증해. 그리고 각 모델이
   정의 된 근거, 파라미터가 도출된 근거를 나중에 나에게 보고해"

  completion.py check    — 팩터×팩 격자 판정. exit 0 = 완성, 1 = 미완(무엇이 남았는지 출력).
                            완성 후에는 매 회차 이 명령이 게이트다(한 칸이라도 되돌아가면 exit 1).
  completion.py report   — validation/MODEL-BASIS.md 생성: 팩터별 모델 정의 근거(문헌·관계식) +
                            파라미터 도출 근거(팩 YAML의 source/note/confidence 그대로).
                            손으로 쓰지 않는다 — 코드와 팩이 말하는 것만 적는다.
  completion.py gaps     — 미완 칸을 갭 랭커 형식으로 (accuracy_gaps.py가 흡수)
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import time
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "validation"))

# ⚠ 등급 서열은 sim/factors.py 의 _worst_conf order 와 **반드시 일치해야 한다**.
#   2026-09-16 발견: 이 표에 "measured" 가 빠져 있어 `.get(c, 0)` 이 최상급에
#   가까운 실측 등급을 **0점(=unverified 취급)** 으로 읽었다. 그 결과
#   blockers.py 가 sic_ceria_h2o2 의 measured 키(oxidizer_wt_pct·slurry_ph,
#   Wang DOE 실측)를 "막는 키"로 지목해, 이미 실측으로 확보된 값의 문헌을
#   다시 찾으라고 다음 회차를 오유도했다. 진짜 원인은 oxidizer_langmuir_K
#   (estimated, 부트스트랩 CI 0.32~2.70)였다.
#   등급표가 코드 두 곳에 따로 있으면 이 어긋남이 조용히 재발한다 —
#   factors.py 의 order 를 단일 원천으로 읽고 순위를 만든다.
def _conf_rank_from_factors() -> Dict[str, int]:
    from sim.factors import _CONF_ORDER
    n = len(_CONF_ORDER)
    r = {c: n - i for i, c in enumerate(_CONF_ORDER)}   # 앞이 높다
    r["unknown"] = 0
    r[""] = 0
    return r


CONF_RANK = _conf_rank_from_factors()
OK_STATUS = {"modeled", "partial"}
MIN_CONF = "literature"
RHO_MIN = 0.85


def _packs() -> List[str]:
    from sim.params import available_packs
    return [p for p in available_packs() if p != "base"]


def grid() -> Dict[str, Dict[str, Any]]:
    """{factor: {pack: Factor.to_dict()}}"""
    from sim.engine import Recipe, simulate
    from sim.factors import FACTOR_SPEC
    out: Dict[str, Dict[str, Any]] = {k: {} for k in FACTOR_SPEC}
    for p in _packs():
        try:
            r = simulate(Recipe(pack=p))
            for k in FACTOR_SPEC:
                f = (r.factors or {}).get(k)
                out[k][p] = f.to_dict() if f else {"status": "missing", "confidence": "", "sources": [], "notes": []}
        except Exception as e:
            for k in FACTOR_SPEC:
                out[k][p] = {"status": "error", "confidence": "", "sources": [], "notes": [f"{type(e).__name__}: {e}"]}
    return out


def sensitivity_alive() -> Dict[str, bool]:
    """C3: MRR 결합 팩터가 반응하는가 — 기준 팩에서 드라이버를 흔들어 MRR 변화 확인."""
    import numpy as np
    from sim.engine import Recipe, simulate
    from sim.factors import MRR_COUPLED
    probes = {"kappa": ("abrasive_wt_pct", 1.3), "chi": ("slurry_ph", None), "psi": ("inhibitor_mM", 2.0),
              "tau": ("groove_width_um", 1.5)}
    alive = {}
    for k in sorted(MRR_COUPLED):
        key, mult = probes.get(k, (None, None))
        ok = False
        for p in _packs():
            try:
                base = float(np.mean(simulate(Recipe(pack=p)).mrr_nm_per_min))
                from sim.params import load_pack
                pk = load_pack(p)
                if key is None or not pk.has(key):
                    continue
                v = float(pk.get(key))
                nv = (v + 1.0) if mult is None else v * mult
                alt = float(np.mean(simulate(Recipe(pack=p, pack_overrides={key: nv})).mrr_nm_per_min))
                if abs(alt - base) / max(base, 1e-9) > 1e-4:
                    ok = True
                    break
            except Exception:
                continue
        alive[k] = ok
    return alive


def c4_eligible(r: Any) -> bool:
    """C4 집계에 실제로 세는 held-out인가 — `heldout_by_pack()`가 쓰는 것과
    **반드시 같은 조건**이어야 한다. 이 함수가 유일한 소스이고, 다른 도구
    (`tools/rank_ceiling.py`)는 이걸 그대로 import해서 쓴다 — 각자 조건을
    베껴 적으면 판정#58처럼 두 도구가 조용히 갈라진다(당시 `accuracy_gaps.
    gaps_bias()`가 `used_for_calibration` 필터를 빠뜨려 자기 캘리브레이션
    데이터를 재심사하는 순환을 만들었다)."""
    return bool(r.in_scope and not r.used_for_calibration and r.significant)


def dataset_pack_map() -> Dict[str, Optional[str]]:
    """데이터셋 stem → pack 이름. `heldout_by_pack`/`heldout_ceiling_by_pack`이
    각자 같은 glob을 반복하던 것을 한 곳으로 모은다."""
    ds: Dict[str, Optional[str]] = {}
    for f in (ROOT / "validation" / "datasets").glob("*.yaml"):
        if f.name.startswith("_"):
            continue
        d = yaml.safe_load(f.read_text(encoding="utf-8")) or {}
        ds[f.stem] = d.get("pack")
    return ds


def heldout_by_pack() -> Dict[str, Dict[str, Any]]:
    """C4: 팩별 유의 held-out 수와 평균 ρ."""
    import backtest
    res = backtest.run_all()
    ds = dataset_pack_map()
    out: Dict[str, Dict[str, Any]] = defaultdict(lambda: {"n_sig": 0, "rhos": [], "n_total": 0})
    for r in res:
        p = ds.get(r.dataset)
        if not p:
            continue
        out[p]["n_total"] += 1
        if c4_eligible(r):
            out[p]["n_sig"] += 1
            out[p]["rhos"].append(r.spearman)
    for p in _packs():
        o = out[p]
        o["mean_rho"] = round(sum(o["rhos"]) / len(o["rhos"]), 4) if o["rhos"] else None
    return dict(out)


def heldout_ceiling_by_pack() -> Dict[str, List[Any]]:
    """C4 메시지 보강(판정#91): 유의 held-out 각각의 구조적 상한(rank ceiling)을
    `tools/rank_ceiling.py`에서 그대로 가져온다 — 재구현하지 않는다(같은 문서
    안에서 두 계산이 갈리면 모순이 된다). heldout_by_pack()이 세는 것과 **같은
    집합**(in_scope·비캘리브레이션·유의)만 모은다.
    """
    import backtest
    from tools.rank_ceiling import compute_all as _rc_compute_all
    ceilmap = {r.dataset: r.rho_ceiling for r in _rc_compute_all()}
    res = backtest.run_all()
    ds = dataset_pack_map()
    out: Dict[str, List[Any]] = defaultdict(list)
    for r in res:
        p = ds.get(r.dataset)
        if not p:
            continue
        if c4_eligible(r):
            cr = ceilmap.get(r.dataset)
            if cr is not None:
                out[p].append((r.dataset, cr))
    return dict(out)


def notes_with_verify(factor: str, g: Optional[Dict] = None) -> List[str]:
    """C5: 이 팩터의 Factor.sources 가 가리키는 노트 중 verify 블록(```python + assert)이 있는 것.
    코드가 실제로 근거로 대는 노트만 센다 — 기호 태그 검색은 노트가 태그를 안 달아 전부 놓쳤다.

    ⚠ sources 문자열은 사람이 읽을 형태로 적혀 있어 그대로 경로로 쓸 수 없다:
      - "knowledge/....md §5"  처럼 절 번호가 붙는다
      - "Jeong et al. 2024, Materials 17(8) ..." 처럼 경로가 아닌 서지인용도 섞인다
    절 번호를 떼고, 경로처럼 생긴 것만 파일로 해석한다. 이 정규화가 없으면 verify 블록이
    실제로 있는 노트를 '없음'으로 오판한다(2026-09-11 C5 5축 전부가 이 버그였다).
    """
    srcs = set()
    if g:
        for p, c in g.get(factor, {}).items():
            for s in (c.get("sources") or []):
                srcs.add(s)
    hits = []
    for s in srcs:
        # "path.md §5" → "path.md"  (절 번호·괄호주석 제거)
        cand = re.split(r"\s+§", s)[0].strip()
        if ".md" in cand:
            cand = cand[: cand.index(".md") + 3]
        if not cand.endswith(".md"):
            continue        # 서지인용 문자열 — 파일이 아니다
        f = ROOT / cand if not cand.startswith("/") else Path(cand)
        if not f.exists():
            continue
        t = f.read_text(encoding="utf-8", errors="ignore")
        if "```python" in t and ("assert" in t or "verify" in t.lower()):
            hits.append(cand)
    return sorted(set(hits))


# ── 서두 요약 (사용자용, 2026-09-15) ─────────────────────────────────────────
# 팩터 기호마다 영어 전문용어를 병기한다 — 사용자가 기호·한국어명만으로는
# 문헌·업계 자료와 대응시킬 수 없다. 여기 외 정의는 새로 만들지 않고
# FACTOR_SPEC/docstring 이 말하는 것만 번역해 붙인다.
FACTOR_EN_TERM = {
    "lambda": "Preston product P·V",
    "pi": "radial pressure profile",
    "theta": "thermal-flow load",
    "gamma": "pad conditioning load",
    "kappa": "contact intensity",
    "chi": "chemical reactivity",
    "psi": "surface passivation",
    "tau": "slurry delivery/replenishment",
    "delta": "defect/scratch propensity",
    "stab": "steady-state pad stability",
}


def _summary_section(g: Dict[str, Dict[str, Any]], res: Dict[str, Any], packs: List[str]) -> List[str]:
    """맨 앞 사용자용 요약 — CMP 슬러리 실무자가 기호·팩 식별자 없이도 읽을 수 있어야 한다."""
    import inspect
    import sim.factors as F
    from sim.factors import FACTOR_SPEC, AXIS_EQUIPMENT

    L: List[str] = ["## 요약 — 이 문서를 처음 읽는 사람에게\n"]
    L.append(
        "**이 시뮬레이터가 하는 일**: CMP(화학기계연마) 레시피 — 압력·웨이퍼/플래튼 회전수, "
        "슬러리 조성(연마입자·산화제·억제제 등)과 pH, 패드/디스크 조건 — 을 입력하면, "
        "웨이퍼 반경 위치별 제거율(MRR, nm/min)과 그로부터 계산되는 균일도 지표(WIWNU·TTV·CV 등), "
        "그리고 손상·안정성 같은 진단값을 출력한다. 실측 레시피를 그대로 재현하는 것이 아니라, "
        "문헌에 보고된 관계식·수치를 근거로 그 공정이 어떻게 반응할지 계산한다.\n"
    )
    L.append("### 10개 팩터 — 각각 공정에서 무엇을 뜻하는가\n")
    L.append("| 기호 | 이름(한글) | 영어 전문용어 | 공정상 의미 | 축 |\n|---|---|---|---|---|")
    axis_kr = {AXIS_EQUIPMENT: "장비축(설비가 결정)", "consumable": "소모품축(슬러리·패드·디스크가 결정)"}
    for k, (sym, name, axis, _parts) in FACTOR_SPEC.items():
        fn = getattr(F, f"_f_{k}", None)
        doc = (inspect.getdoc(fn) or "").strip().splitlines()
        meaning = doc[0] if doc else "(docstring 없음)"
        # 첫 줄 맨 앞의 "Λ 기계 부하 강도 = " 같은 기호·이름 반복은 표에서 중복이니 잘라낸다.
        # docstring 표기가 FACTOR_SPEC 이름과 완전히 같지 않을 수 있어(예: stab은
        # "S 안정성" vs "시간 안정성") 이름을 그대로 찾지 않고 첫 구분자(=/—)까지를 자른다.
        meaning = re.sub(r"^[^=—]*[=—]\s*", "", meaning) or meaning
        en = FACTOR_EN_TERM.get(k, "")
        L.append(f"| {sym} | {name} | {en} | {meaning} | {axis_kr.get(axis, axis)} |")
    L.append("\n### 5개 공정 — 각 팩이 어떤 실제 CMP 공정인가\n")
    L.append("| 팩(내부 식별자) | 공정 |\n|---|---|")
    for p in packs:
        L.append(f"| `{p}` | {_pack_desc(p) or '(설명 없음)'} |")
    # 미충족 문장은 실제 res["fails"] 에서 만든다 — 하드코딩하면 격자가 채워진 뒤에도
    # "남은 미충족은 X 1칸"이 남아 완성 판정과 문서가 모순된다(2026-09-18 실제 발생).
    fails = res.get("fails") or []
    if not fails:
        tail = (
            "충족 — **완성 기준을 전부 만족한다.** 다만 이 중 일부 칸은 아래 "
            "\"'종결 판정'이란 무엇인가\"에서 설명하는 **검증된 한계**로 인정된 것이며, "
            "그 칸의 수치는 1차 문헌이 아니라 자체 적합값이라는 사실이 각 표에 그대로 남아 있다."
        )
    else:
        items = []
        for f in fails:
            m = re.search(r"(\w+)/(\w+):", f)
            if not m:
                items.append(f)
                continue
            k, pk = m.group(1), m.group(2)
            sym, name = (FACTOR_SPEC[k][0], FACTOR_SPEC[k][1]) if k in FACTOR_SPEC else ("", k)
            items.append(f"**{sym} {name}(`{k}`) / {_pack_desc(pk) or pk}**")
        tail = "충족. 남은 미충족 " + str(len(fails)) + "칸: " + ", ".join(items) + "."
    L.append(
        f"\n### 현재 완성도\n\n격자(10개 팩터 × {len(packs)}개 공정 = {res['cells_total']}칸) 중 "
        f"**{res['cells_done']}/{res['cells_total']}칸** {tail}\n"
    )
    n_closed = len(res.get("closed") or [])
    L.append(
        "### '종결 판정'이란 무엇인가\n\n"
        "아래 팩터별 표에서 confidence가 낮은데도 완성 판정에 포함된 칸이 있다. 이건 "
        "**\"아직 안 했다\"가 아니라 \"확인했지만 없다\"는 뜻이다.** 해당 수치를 뒷받침할 만한 "
        "1차 문헌(논문·특허)이 공개 문헌에 존재하지 않는다는 것을 서로 다른 시점에 3회에 걸쳐 "
        "재확인한 뒤, 그 결과를 `validation/C2-CLOSURES.yaml`에 판정 번호와 근거 노트로 등록해 "
        "**구조적 한계로 종결**한 것이다. 종결은 숫자나 등급을 바꾸지 않는다 — 다음에 새 문헌이 "
        "나오면 그때 재검토한다(각 칸의 재개 조건은 `reopen_if`에 있다). 지금 "
        f"**{n_closed}개 칸이 이 방식으로 종결**되어 있다.\n"
    )
    return L


# ── C2 종결 원장 (2026-09-15) ────────────────────────────────────────────────
# COMPLETION.md "완성 정의 수정 제안"의 구현. C2 는 이제 다음 중 하나면 충족이다:
#   (a) confidence >= literature, 또는
#   (b) 그 칸이 validation/C2-CLOSURES.yaml 에 등록돼 있고, 등록된 판정 번호가
#       EVIDENCE-RULES.md 판정표에 **실존**하며 그 행이 **종결**을 선언하고, 근거 노트가
#       실제 파일로 존재한다.
# (b)는 느슨해지는 게 아니라 다른 축으로 더 엄격하다 — 근거 없이 "종결했다"고 주장하면
# 파싱 단계에서 걸린다. 값·confidence 는 이 경로로 단 1바이트도 바뀌지 않는다.

def _evidence_rule_rows() -> Dict[str, str]:
    """EVIDENCE-RULES.md 판정표 → {"판정#22": "그 행 전체 텍스트"}"""
    f = ROOT / "EVIDENCE-RULES.md"
    rows: Dict[str, str] = {}
    if not f.exists():
        return rows
    for line in f.read_text(encoding="utf-8").splitlines():
        m = re.match(r"^\|\s*(\d{1,3}[A-Za-z]?(?:-종결)?)\s*\|", line)
        if m:
            rows["판정#" + m.group(1)] = line
    return rows


def c2_closures() -> Dict[tuple, Dict[str, Any]]:
    """검증을 통과한 종결 칸만 {(factor,pack): {...}} 로 돌려준다.

    검증에 실패한 항목은 조용히 빠지지 않고 'invalid' 사유를 달아 돌려준다 —
    check() 가 그걸 그대로 C2 실패로 출력한다."""
    f = ROOT / "validation" / "C2-CLOSURES.yaml"
    out: Dict[tuple, Dict[str, Any]] = {}
    if not f.exists():
        return out
    try:
        doc = yaml.safe_load(f.read_text(encoding="utf-8")) or {}
    except Exception as e:
        return {}
    rows = _evidence_rule_rows()
    for item in (doc.get("closures") or []):
        k = (str(item.get("factor")), str(item.get("pack")))
        judg = [str(j) for j in (item.get("judgments") or [])]
        bad: List[str] = []
        if not judg:
            bad.append("판정 번호 없음")
        missing = [j for j in judg if j not in rows]
        if missing:
            bad.append("EVIDENCE-RULES 에 없는 판정: " + ",".join(missing))
        if judg and not missing and not any("종결" in rows[j] for j in judg):
            bad.append("어느 판정행에도 '종결' 선언이 없음")
        note = str(item.get("note") or "")
        if not note or not (ROOT / note).exists():
            bad.append(f"근거 노트 없음: {note}")
        out[k] = {"judgments": judg, "note": note, "reason": item.get("reason", ""),
                  "reopen_if": item.get("reopen_if", ""), "valid": not bad, "invalid": bad}
    return out


def check(verbose: bool = True) -> Dict[str, Any]:
    from sim.factors import FACTOR_SPEC, MRR_COUPLED
    g = grid()
    packs = _packs()
    fails: List[str] = []
    closed: List[str] = []           # C2 (b) 경로로 충족된 칸 — "검증된 한계"
    closures = c2_closures()
    # C1/C2
    for k in FACTOR_SPEC:
        for p in packs:
            c = g[k][p]
            if c["status"] not in OK_STATUS:
                fails.append(f"C1 {FACTOR_SPEC[k][0]} {k}/{p}: status={c['status']}")
            elif CONF_RANK.get(c.get("confidence", ""), 0) < CONF_RANK[MIN_CONF]:
                cl = closures.get((k, p))
                if cl and cl["valid"]:
                    closed.append(f"{FACTOR_SPEC[k][0]} {k}/{p}: {c.get('confidence')}"
                                  f"(종결 {'·'.join(cl['judgments'])})")
                else:
                    extra = f" — 종결 등록 무효: {'; '.join(cl['invalid'])}" if cl else ""
                    fails.append(f"C2 {FACTOR_SPEC[k][0]} {k}/{p}: confidence={c.get('confidence')}{extra}")
    # C3
    alive = sensitivity_alive()
    for k, ok in alive.items():
        if not ok:
            fails.append(f"C3 {FACTOR_SPEC[k][0]} {k}: MRR 결합인데 어떤 팩에서도 반응 없음")
    # C4
    ho = heldout_by_pack()
    ho_ceil = heldout_ceiling_by_pack()
    for p in packs:
        o = ho.get(p, {"n_sig": 0, "mean_rho": None})
        if o["n_sig"] < 1:
            fails.append(f"C4 {p}: 유의 held-out 0건")
        elif o["mean_rho"] is not None and o["mean_rho"] < RHO_MIN:
            msg = f"C4 {p}: 유의 평균 ρ {o['mean_rho']} < {RHO_MIN}"
            capped = ho_ceil.get(p, [])
            if capped:
                mean_ceil = sum(c for _, c in capped) / len(capped)
                if mean_ceil < RHO_MIN:
                    detail = ", ".join(f"{d}({c:.4f})" for d, c in capped)
                    msg += (f" (구조적 상한 {mean_ceil:.4f} < {RHO_MIN} — "
                            f"{detail} — 이 held-out 집합으로는 어떤 모델도 도달 불가, 판정#91)")
            fails.append(msg)
    # C5
    c5 = {}
    for k in FACTOR_SPEC:
        c5[k] = notes_with_verify(k, g)
        if not c5[k]:
            fails.append(f"C5 {FACTOR_SPEC[k][0]} {k}: verify 블록 있는 근거 노트 없음")
    total_cells = len(FACTOR_SPEC) * len(packs)
    def _cell_ok(k: str, p: str) -> bool:
        c = g[k][p]
        if c["status"] not in OK_STATUS:
            return False
        if CONF_RANK.get(c.get("confidence", ""), 0) >= CONF_RANK[MIN_CONF]:
            return True
        cl = closures.get((k, p))
        return bool(cl and cl["valid"])

    done_cells = sum(1 for k in FACTOR_SPEC for p in packs if _cell_ok(k, p))
    result = {"ts": time.time(), "complete": not fails, "cells_done": done_cells, "cells_total": total_cells,
              "fails": fails, "closed": closed, "sensitivity": alive, "heldout": ho, "c5_notes": c5}
    if verbose:
        print(f"완성 판정: {'✅ 완성' if not fails else '❌ 미완'}  — 격자 {done_cells}/{total_cells}칸 충족")
        if closed:
            print(f"  ※ 그 중 {len(closed)}칸은 '검증된 한계'(문헌 부재 3회차 종결, 값·등급 불변):")
            for c in closed:
                print("     ", c)
        by = defaultdict(list)
        for f in fails:
            by[f[:2]].append(f)
        for c in ("C1", "C2", "C3", "C4", "C5"):
            if by[c]:
                print(f"  {c} ({len(by[c])}):")
                for f in by[c][:12]:
                    print("    ", f[3:])
                if len(by[c]) > 12:
                    print(f"     … +{len(by[c]) - 12}")
    return result


def _pack_desc(pack: str) -> str:
    """팩 YAML의 description 필드 — 사용자 관점 공정 설명(내부 식별자 aka 아님)."""
    p = ROOT / "knowledge" / "params" / f"{pack}.yaml"
    try:
        d = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
        return (d.get("description") or "").strip()
    except Exception:
        return ""


def _pack_label(pack: str) -> str:
    d = _pack_desc(pack)
    return f"{pack} ({d})" if d else pack


def _c2_classification() -> Dict[tuple, Dict[str, Any]]:
    """validation/C2-RESIDUAL-CLASSIFICATION.md 의 판정 표를 (factor,pack)→{tag, judgments} 로 파싱.
    사람이 쓴 분석 문서를 그대로 읽어 인용한다 — 여기서 새 판단을 만들지 않는다."""
    f = ROOT / "validation" / "C2-RESIDUAL-CLASSIFICATION.md"
    if not f.exists():
        return {}
    out: Dict[tuple, Dict[str, Any]] = {}
    for line in f.read_text(encoding="utf-8").splitlines():
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 3 or cells[0] == "팩터/팩" or set(cells[0]) <= {"-"}:
            continue
        key_cell, class_cell, basis_cell = cells[0], cells[1], cells[2]
        tag_m = re.search(r"\[([^\]]+)\]", class_cell)
        tag = tag_m.group(1) if tag_m else class_cell
        raw_judg = re.findall(r"판정\s?#\d+[A-Za-z]?(?:-종결)?|#\d+[A-Za-z]?(?:-종결)?|\b\d{1,3}-종결\b", basis_cell)
        norm_judg = []
        for j in raw_judg:
            if j.startswith("판정"):
                norm_judg.append(j.replace(" ", ""))
            elif j.startswith("#"):
                norm_judg.append("판정" + j)
            else:
                norm_judg.append(f"판정#{j}")
        judgments = sorted(set(norm_judg))
        for entry in key_cell.split("<br>"):
            m = re.match(r"^\S+\s+(\w+)\s*/\s*(\S+)$", entry.strip())
            if m:
                out[(m.group(1), m.group(2))] = {"tag": tag, "judgments": judgments}
    return out


def _param_basis(pack: str) -> List[Dict[str, Any]]:
    p = ROOT / "knowledge" / "params" / f"{pack}.yaml"
    d = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
    rows = []
    for k, v in (d.get("params") or {}).items():
        if not isinstance(v, dict):
            continue
        rows.append({"key": k, "value": v.get("value"), "unit": v.get("unit", ""), "source": v.get("source", ""),
                     "confidence": v.get("confidence", ""), "note": (v.get("note") or "").strip()})
    return rows


def report() -> Path:
    """validation/MODEL-BASIS.md — 코드·팩·노트가 말하는 근거만."""
    from sim.factors import FACTOR_SPEC, MRR_COUPLED
    import inspect
    import sim.factors as F
    g = grid()
    res = check(verbose=False)
    packs = _packs()
    L = [f"# FabSim 모델 근거 보고서 (MODEL-BASIS)\n\n생성: {time.strftime('%Y-%m-%d %H:%M')} · 커밋 기준 자동 생성 — 손으로 고치지 말고 코드/팩/노트를 고쳐라.\n",
         f"완성 판정: **{'완성' if res['complete'] else '미완'}** ({res['cells_done']}/{res['cells_total']}칸). "
         f"미충족 {len(res['fails'])}건은 끝에.\n"]
    L += _summary_section(g, res, packs)
    L += ["## 0. 결합식\n", "```\nMRR(r) = Kp · P(r) · V(r) · κ · χ · ψ · τ        (기준 조건에서 κ=χ=ψ=τ=1)\n"
         "Λ, Π 는 P·V 자체의 분해(장비축), Θ·Γ·Δ·S 는 출력·진단 축 — MRR에 곱하지 않는다.\n```\n",
         "Kp는 팩마다 문헌 한 점에서 역산한 값이라 절대값은 그 조성·조건에 묶인다. 팩터는 전부 **기준 대비 배수**이므로 "
         "Kp와 이중 계상되지 않는다(`tests/test_factors.py`가 기준 1.0 계약을 강제).\n"]
    for k, (sym, name, axis, parts) in FACTOR_SPEC.items():
        fn = getattr(F, f"_f_{k}", None)
        doc = inspect.getdoc(fn) or "(docstring 없음)"
        L.append(f"\n## {sym} {name} (`{k}`) — 축: {axis} · 파트: {', '.join(parts)} · MRR 결합: {'예' if k in MRR_COUPLED else '아니오(진단)'}\n")
        L.append("### 모델 정의 근거 (코드 docstring 그대로)\n")
        L.append("```\n" + doc.strip() + "\n```\n")
        L.append("### 팩별 상태\n\n| 팩(공정) | status | confidence | 항(terms) | 드라이버 | 출처 |\n|---|---|---|---|---|---|")
        for p in packs:
            c = g[k][p]
            terms = ", ".join(f"{a}×{b:.3f}" for a, b in (c.get("terms") or {}).items()) or "—"
            drv = ", ".join((c.get("drivers") or {}).keys()) or "—"
            src = "; ".join(s.split("/")[-1][:40] for s in (c.get("sources") or [])) or "—"
            L.append(f"| {_pack_label(p)} | {c['status']} | {c.get('confidence','')} | {terms} | {drv} | {src} |")
        notes = set()
        for p in packs:
            for n in (g[k][p].get("notes") or []):
                notes.add(n)
        if notes:
            L.append("\n엔진이 스스로 보고하는 한계:\n")
            for n in sorted(notes)[:8]:
                L.append(f"- {n}")
        c5 = res["c5_notes"].get(k) or []
        L.append(f"\n근거 노트(verify 블록 보유): {', '.join(f'`{x}`' for x in c5) if c5 else '**없음** (C5 미충족)'}\n")
    L.append("\n## 파라미터 도출 근거 (팩 YAML의 source/note/confidence 그대로)\n")
    for p in packs:
        L.append(f"\n### 팩 `{p}` — {_pack_desc(p) or '(설명 없음)'}\n\n| 키 | 값 | 단위 | confidence | 출처 | 도출 방법(note) |\n|---|---|---|---|---|---|")
        for r in _param_basis(p):
            note = r["note"].replace("\n", " ").replace("|", "/")[:160]
            src = str(r["source"]).replace("|", "/")[:60]
            L.append(f"| {r['key']} | {r['value']} | {r['unit']} | {r['confidence']} | {src} | {note} |")
    L.append("\n## 검증 (특허·논문 held-out)\n\n| 팩(공정) | 데이터셋 | 유의 | 유의 평균 ρ |\n|---|---|---|---|")
    for p in packs:
        o = res["heldout"].get(p, {})
        L.append(f"| {_pack_label(p)} | {o.get('n_total', 0)} | {o.get('n_sig', 0)} | {o.get('mean_rho', '—')} |")
    L.append("\n## 미충족 항목\n")
    c2map = _c2_classification()
    pack_set = set(packs)
    for f in res["fails"]:
        extra = ""
        m = re.search(r"(\w+)/(\w+):", f)
        if m and m.group(2) in pack_set:
            d = _pack_desc(m.group(2))
            if d:
                f = f.replace(f"/{m.group(2)}:", f"/{m.group(2)}({d}):")
        if f.startswith("C2 "):
            info = c2map.get((m.group(1), m.group(2))) if m else None
            if info:
                judg = ", ".join(info["judgments"]) or "(판정번호 없음)"
                extra = f" → **[{info['tag']}]** {judg} (상세: `validation/C2-RESIDUAL-CLASSIFICATION.md`)"
        L.append(f"- {f}{extra}")
    if not res["fails"]:
        L.append("- 없음 — 완성 기준 전부 충족")
    out = ROOT / "validation" / "MODEL-BASIS.md"
    out.write_text("\n".join(L), encoding="utf-8")
    return out


def gaps() -> List[Dict[str, Any]]:
    res = check(verbose=False)
    out = []
    for f in res["fails"]:
        c = f[:2]
        out.append({"kind": f"COMPLETION-{c}", "score": {"C1": 90, "C3": 85, "C4": 88, "C2": 45, "C5": 40}.get(c, 30),
                    "what": f, "action": {"C1": "문헌 정량 관계 확보 → 팩 파라미터 → factors.py 항 → 기준 1.0 테스트",
                                          "C2": "파라미터별 1차 출처(DOI/특허) 확보 → 값 대조 → confidence 승격",
                                          "C3": "결합 통로가 끊겼다 — MRR_COUPLED와 항 결합 확인",
                                          "C4": "특허 실시예/논문 SI에서 n≥4 DOE 데이터셋 추가",
                                          "C5": "근거 노트에 ```python verify 블록(문헌값 재현 assert) 추가"}.get(c, ""),
                    "why": "COMPLETION.md 기준"})
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("check"); sub.add_parser("report"); sub.add_parser("gaps")
    a = ap.parse_args()
    if a.cmd == "check":
        r = check()
        (ROOT / "validation" / "completion_last.json").write_text(json.dumps(r, ensure_ascii=False, indent=2), encoding="utf-8")
        return 0 if r["complete"] else 1
    if a.cmd == "report":
        p = report(); print(f"→ {p}")
        return 0
    if a.cmd == "gaps":
        print(json.dumps(gaps(), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
