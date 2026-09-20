"""판정#93 후속 — `--c4-requirement` k>1 개별판정 결함 회귀 테스트.

2026-09-20 실측 결함: k=2 에서 개별 후보의 구조적 상한(최대 1.0)을 **합** 요구치
(1.8325)와 직접 비교해, 실현가능한 후보 3건이 전부 "상한 1.0000 < 요구치"로
불가능 처리됐다. 바로 아래 쌍별 절은 같은 셋을 '가능'으로 옳게 판정하고 있어
**한 출력 안에서 두 절이 모순**됐다.

올바른 개별 판정은 "이 후보가 들어가는 실현가능한 k-조합이 하나라도 있는가"다.
아래 테스트는 그 성질을 절대값과 함께 고정한다 — 상대적 성질만 검사하면
결함이 되돌아와도 통과한다(판정#91 노트의 21,600km 버그 교훈).
"""
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))

import rank_ceiling as rc  # noqa: E402

PACK = "cu_h2o2_bta"


@pytest.fixture(scope="module")
def info():
    return rc.c4_requirement(PACK)


def test_k1_requirement_absolute_value(info):
    """k=1 요구치는 RHO_MIN*(n_sig+1) - existing_sum 의 정확한 값이어야 한다."""
    req = info["requirements"][1]["req_sum"]
    assert req == pytest.approx(0.98255, rel=1e-3)


def test_k2_requirement_absolute_value(info):
    req = info["requirements"][2]["req_sum"]
    assert req == pytest.approx(1.83255, rel=1e-3)
    assert info["requirements"][2]["req_mean_new"] == pytest.approx(0.916275, rel=1e-3)


def test_k2_individual_verdicts_match_pairwise_section(info):
    """개별 절과 쌍별 절이 모순되면 안 된다 — 이것이 원래 결함이었다.

    개별 절에서 '가능'인 후보는, 쌍별 절에서 자신이 들어가는 실현가능한 쌍이
    적어도 하나 있어야 한다. 반대도 성립해야 한다.
    """
    cands = {c["dataset"]: c for c in info["requirements"][2]["candidates"]}
    req_sum = info["requirements"][2]["req_sum"]
    P = rc.backtest.BacktestResult.P_THRESHOLD

    def sig_ok(c):
        return c["ceiling_p"] is not None and c["ceiling_p"] < P

    for name, c in cands.items():
        has_feasible_pair = any(
            sig_ok(c) and sig_ok(o)
            and (c["rho_ceiling"] + o["rho_ceiling"]) >= req_sum - 1e-9
            for oname, o in cands.items() if oname != name)
        assert c["possible_in_principle"] == has_feasible_pair, (
            f"{name}: 개별판정={c['possible_in_principle']} 인데 "
            f"실현가능 쌍 존재={has_feasible_pair} — 두 절이 모순된다")


def test_k2_exactly_three_candidates_are_possible(info):
    """결함 시절에는 0건이었다. 절대 건수와 이름을 고정한다."""
    poss = sorted(c["dataset"] for c in info["requirements"][2]["candidates"]
                  if c["possible_in_principle"])
    assert poss == [
        "ihnfeldt2008_cu_alumina_ph_oxidizer_chelator",
        "jani2025_cu_rsm_composition_heldout",
        "us8501625b2_cu_h2o2_pressure_series",
    ]


def test_structurally_insignificant_candidates_stay_impossible(info):
    """상한 자체가 영원히 비유의인 둘은 k 와 무관하게 불가능이어야 한다.

    이 둘은 '합치면 된다'로 구제되면 안 된다 — 유의하지 못하면 애초에
    C4 집계에 들어가지 못하기 때문이다.
    """
    for k in (1, 2):
        cands = {c["dataset"]: c for c in info["requirements"][k]["candidates"]}
        for name in ("hong2007_cu_ads_bta_polish_rate",
                     "miranda2004_cu_ph_h2o2_2x2"):
            assert cands[name]["blocked_significance"] is True
            assert cands[name]["possible_in_principle"] is False


def test_k1_uses_plain_ceiling_comparison(info):
    """k=1 에서는 파트너가 없으므로 자기 상한만으로 판정해야 한다."""
    req = info["requirements"][1]["req_sum"]
    for c in info["requirements"][1]["candidates"]:
        expected = c["rho_ceiling"] < req - 1e-9
        assert c["blocked_ceiling"] == expected


def test_no_candidate_ceiling_exceeds_one(info):
    """Spearman 상한은 1.0 을 넘을 수 없다 — 넘으면 계산 결함이다."""
    for k in (1, 2):
        for c in info["requirements"][k]["candidates"]:
            assert c["rho_ceiling"] <= 1.0 + 1e-9
