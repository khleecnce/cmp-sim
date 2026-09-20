"""판정#94 회귀 — 모델이 '예측하지 않는다'고 선언한 구간을 응답지도가 채점하지 않는가.

배경(2026-09-20): `sim/factors.py::_ph_cu_acidic_term` 은 관측이 없는 레짐
(알칼리 × 억제제 존재 등)에서 항을 끄고 notes 에 이유를 남긴다. 그 구간의 MRR 은
"변하지 않는다는 예측"이 아니라 **"예측하지 않는다는 선언"**인데,
`tools/response_map.py` 는 숫자만 봐서 둘을 구분하지 못했다. 그 결과 살아 있는
산성 가지(단조↓)와 침묵하는 알칼리 가지(상수)가 이어져 만든 인공 골짜기를
문헌 정점(Ihnfeldt 2008, pH 3/8.3/10)과 대조해 **CONFLICT score 120** 을
최우선 갭으로 찍고 있었다. 그 처방("정점을 단조로 근사한 경우가 가장 흔하다 —
부호를 고쳐라")을 따랐다면 근거가 있는 산성 가지까지 망가뜨렸을 것이다.

이 테스트가 고정하는 계약 4가지:
  1. 항이 레짐을 끄면 `Factor.gated` 에 사유가 남는다(문자열 파싱 금지).
  2. 응답지도가 그 점을 형상 판정에서 뺀다.
  3. 남은 근거 구간이 3점 미만이면 판정을 CONFLICT 가 아니라 GATED 로 낸다.
  4. 갭 랭커에서 GATED 는 CONFLICT 보다 **낮은** 점수다(코드 수정 과제가 아니라
     데이터 과제이므로).
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import pytest

from sim.engine import Recipe, simulate
import sim.models  # noqa: F401
import tools.response_map as rm


MODEL = "tier2.gw_physical_kp"


def _chi(ph: float, inhibitor_mM=None):
    ov = {"slurry_ph": ph}
    if inhibitor_mM is not None:
        ov["inhibitor_mM"] = inhibitor_mM
    r = simulate(Recipe(pack="cu_h2o2_bta", pack_overrides=ov), model=MODEL)
    return r, r.factors["chi"]


def test_gate_is_declared_structurally_not_only_in_notes():
    """알칼리 × 억제제 존재 = 관측 없는 레짐 → gated 에 사유가 실린다."""
    _, chi = _chi(10.0)                     # 팩 기본 inhibitor_mM = 1.0 (>0)
    assert "slurry_ph" in chi.gated, chi.gated
    assert chi.gated["slurry_ph"], "사유 문자열이 비어 있으면 안 된다"


def test_supported_regime_is_not_gated():
    """산성 × 억제제 존재는 근거가 있는 레짐 — 게이트가 걸리면 안 된다."""
    _, chi = _chi(4.0)
    assert "slurry_ph" not in chi.gated, chi.gated
    assert "ph_cu_acidic" in chi.terms


def test_gate_reason_is_read_from_factor_not_regex():
    """response_map 이 notes 정규식이 아니라 Factor.gated 를 읽는다."""
    r, _ = _chi(10.0)
    assert rm._gate_reason(r, "slurry_ph") is not None
    assert rm._gate_reason(r, "pressure_psi") is None


def test_gated_points_are_excluded_from_shape():
    """스윕이 침묵 구간을 곡선에서 빼고 gated_x 에 따로 담는다."""
    f = next(x for x in rm.FACTORS if x.key == "slurry_ph")
    sw = rm.sweep("cu_h2o2_bta", f, (3.0, 10.0))
    assert sw is not None
    assert sw.get("gated_x"), "알칼리 구간이 통째로 빠져야 한다"
    assert all(x <= 6.25 for x in sw["xs"]), sw["xs"]


def test_verdict_is_gated_not_conflict():
    """모델이 말하지 않은 구간을 근거로 CONFLICT 를 찍지 않는다."""
    rep = rm.build(["cu_h2o2_bta"])
    row = next(r for r in rep["rows"] if r["key"] == "slurry_ph")
    assert row["verdict"] == "GATED", row["verdict"]
    assert row["model_shape"] == "gated"
    assert "근거 없음" in row["note"]


def test_no_conflict_remains_for_pack():
    rep = rm.build(["cu_h2o2_bta"])
    assert [r["key"] for r in rep["rows"] if r["verdict"] == "CONFLICT"] == []


def test_gated_scores_below_conflict_in_ranker():
    import tools.accuracy_gaps as ag
    gaps = ag.gaps_response()
    g = [x for x in gaps if x["kind"] == "RESPONSE_GATED"]
    assert g, "GATED 갭이 랭커에 나타나야 한다"
    assert all(x["score"] < 120 for x in g), [x["score"] for x in g]


def test_verdict_of_gated_ignores_lit_shape():
    """문헌이 어떤 형상이든 모델이 침묵하면 GATED 다."""
    for lit in ("peak", "valley", "up", "down", "mixed", "unknown"):
        assert rm.verdict_of("gated", lit) == "GATED"
