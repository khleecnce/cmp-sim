"""엔진에 등록된 Pourbaix Nernst pH 기울기 진단의 계약 테스트.

근거: sim/tier2_physics/pourbaix_nernst_slope.py,
knowledge/cmp/surface-chemistry-cu-w-pourbaix-passivation.md.
dE/dpH = -(RT/F)ln10*(m/n) = -59.16*(m/n) mV/pH (25 degC).

고정하는 계약:
  1. 금속막(cu/w)에서만 값이 나오고, 산화막·SiC는 스킵사유만.
  2. 값은 원본 모듈과 비트 단위로 같다(재구현 아님).
  3. n==0(전자 안 오가는 탈수 반응)은 집계에서 빠진다 — 원본 is_self_limiting_type()이
     m==n=0에 True를 주는 것에 오염되지 않아야 한다.
  4. 계량계수가 앞에 붙은 반응식("2Cu + ...")도 놓치지 않는다.
  5. MRR 경로 비트 불변.
"""
import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "sim" / "tier2_physics"))

from sim.engine import Recipe, simulate  # noqa: E402

METAL_PACKS = ["cu_h2o2_bta", "w_fe_oxidizer"]
NONMETAL_PACKS = ["oxide_silica", "sti_ceria", "sic_ceria_h2o2"]


@pytest.mark.parametrize("pack", METAL_PACKS)
def test_metal_packs_get_standard_slope(pack):
    r = simulate(Recipe(pack=pack, time_s=60))
    assert r.pourbaix_nernst_slope_mv_per_ph == pytest.approx(-59.16, abs=0.01)
    assert r.pourbaix_self_limiting_reactions >= 1
    assert "mV/pH" in r.pourbaix_nernst_note


@pytest.mark.parametrize("pack", NONMETAL_PACKS)
def test_nonmetal_packs_skip_without_inventing(pack):
    r = simulate(Recipe(pack=pack, time_s=60))
    assert r.pourbaix_nernst_slope_mv_per_ph is None
    assert r.pourbaix_self_limiting_reactions is None
    assert "금속막이 아니라" in r.pourbaix_nernst_note


def test_matches_source_module_bitwise():
    import pourbaix_nernst_slope as PNS
    expected = PNS.nernst_ph_slope(1, 1) * 1000.0
    r = simulate(Recipe(pack="cu_h2o2_bta", time_s=60))
    assert r.pourbaix_nernst_slope_mv_per_ph == expected


def test_zero_electron_reaction_is_excluded():
    """Cu(OH)2 -> CuO 탈수(m=n=0)는 Nernst 미정의라 집계에서 빠져야 한다.

    원본 모듈의 is_self_limiting_type()은 m==n만 보므로 이 반응에도 True를 준다.
    엔진 쪽에서 n>0 필터를 먼저 걸지 않으면 self_limiting 카운트가 부풀려진다.
    """
    import pourbaix_nernst_slope as PNS
    dehydration = [x for x in PNS.CMP_SURFACE_REACTIONS if x.n == 0]
    assert dehydration, "전제 붕괴: 모듈에 n=0 참고 반응이 사라졌다"
    assert dehydration[0].is_self_limiting_type() is True, "원본 동작이 바뀌었다"
    r = simulate(Recipe(pack="cu_h2o2_bta", time_s=60))
    # Cu 좌변 산화환원 반응은 Eq.9, Eq.10 두 건뿐 — 탈수가 섞이면 3이 된다
    assert r.pourbaix_self_limiting_reactions == 2


def test_stoichiometric_prefix_reaction_is_matched():
    """"2Cu + 2OH- -> Cu2O ..." 처럼 계수가 앞에 붙어도 Cu 반응으로 잡혀야 한다."""
    r = simulate(Recipe(pack="cu_h2o2_bta", time_s=60))
    assert "Cu2O" in r.pourbaix_nernst_note


def test_tungsten_does_not_pick_up_copper_reactions():
    r = simulate(Recipe(pack="w_fe_oxidizer", time_s=60))
    assert "WO3" in r.pourbaix_nernst_note
    assert "Cu2O" not in r.pourbaix_nernst_note
    assert r.pourbaix_self_limiting_reactions == 1


def test_diagnostic_does_not_touch_mrr():
    a = simulate(Recipe(pack="cu_h2o2_bta", time_s=60))
    b = simulate(Recipe(pack="cu_h2o2_bta", time_s=60))
    np.testing.assert_array_equal(a.mrr_nm_per_min, b.mrr_nm_per_min)
    assert a.pourbaix_nernst_slope_mv_per_ph is not None


def test_note_carries_secondary_citation_warning():
    """2차 인용이라는 사실이 결과에 실려 나가야 한다(정직성 계약)."""
    r = simulate(Recipe(pack="cu_h2o2_bta", time_s=60))
    assert "2차 인용" in r.pourbaix_nernst_note
