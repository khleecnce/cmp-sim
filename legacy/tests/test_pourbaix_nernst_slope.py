"""pourbaix_nernst_slope.py의 self-test 항목을 pytest화한 회귀 테스트."""
import pytest

from pourbaix_nernst_slope import (
    nernst_ph_slope,
    CMP_SURFACE_REACTIONS,
    mo_cu_w_oxidizer_peak_shift_direction,
)


def test_standard_59mV_per_pH_slope():
    slope = nernst_ph_slope(1, 1)
    assert abs(slope * 1000 - (-59.16)) < 0.01


def test_m_equals_2n_gives_half_slope():
    slope_2_1 = nernst_ph_slope(2, 1)
    slope_1_1 = nernst_ph_slope(1, 1)
    assert abs(slope_2_1 - 2 * slope_1_1) < 1e-12


def test_zero_electron_raises():
    with pytest.raises(ValueError):
        nernst_ph_slope(1, 0)


def test_w_passivation_reaction_standard_slope():
    w_reaction = CMP_SURFACE_REACTIONS[0]
    assert abs(w_reaction.slope_mV_per_pH() - (-59.16)) < 0.01


def test_cu_reactions_are_self_limiting_type():
    cu9, cu10 = CMP_SURFACE_REACTIONS[1], CMP_SURFACE_REACTIONS[2]
    assert cu9.is_self_limiting_type()
    assert cu10.is_self_limiting_type()


def test_complexing_agent_shifts_peak_direction():
    assert mo_cu_w_oxidizer_peak_shift_direction(True) == "peak shifts to higher oxidizer concentration"
    assert mo_cu_w_oxidizer_peak_shift_direction(False) == "baseline peak"
