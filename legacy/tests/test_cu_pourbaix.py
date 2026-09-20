"""cu_pourbaix.py 회귀 테스트.

knowledge/cmp/cu-electrochemistry-pourbaix-bta-oxidizer-inhibitor.md §2.1 대조표
(Tamilmani 2005 그림 4.1 판독값, ±0.03 V / ±0.15 pH)를 그대로 재현한다.
"""
import pytest

import cu_pourbaix as cup


def test_cu2_cu_boundary_matches_fig41_readings():
    """Cu2+/Cu 수평선: log_a=-4 -> 0.22 V, log_a=-6 -> 0.16 V (그림 4.1 판독)."""
    assert abs(cup.cu2_cu_boundary_V(-4.0) - 0.22) < 0.03
    assert abs(cup.cu2_cu_boundary_V(-6.0) - 0.16) < 0.03


def test_cu_cu2o_boundary_matches_fig41_readings():
    """Cu/Cu2O 경사선: pH8 -> ~0.00 V, pH13 -> ~-0.30 V (그림 4.1 판독)."""
    assert abs(cup.cu_cu2o_boundary_V(8.0) - 0.00) < 0.03
    assert abs(cup.cu_cu2o_boundary_V(13.0) - (-0.30)) < 0.03


def test_cu_cu2o_boundary_recovers_crc_alkaline_value_at_pH14():
    """pH=14는 정의상 CRC 알칼리형 E0(-0.360 V)로 되돌아가야 한다(노트 §7 verify 1)."""
    assert abs(cup.cu_cu2o_boundary_V(14.0) - cup.E0_CU2O_ALK) < 1e-9


def test_triple_point_pH_matches_fig41_reading():
    """삼중점: log_a=-4 -> pH 4.14 (그림 판독 약 4.2), log_a=-6 -> pH 5.14."""
    assert abs(cup.triple_point_pH(-4.0) - 4.14) < 0.15
    assert abs(cup.triple_point_pH(-6.0) - 5.14) < 0.15


def test_triple_point_pH_shifts_by_one_per_decade():
    """활동도 100배 감소 -> 삼중점 pH가 정확히 +1.00 이동하는 해석적 성질(노트 §7)."""
    assert abs((cup.triple_point_pH(-6.0) - cup.triple_point_pH(-4.0)) - 1.0) < 1e-9


def test_cu2_cuoh2_vertical_pH_matches_note_values():
    """Cu2+/Cu(OH)2 수직선(CuO 자리 대용): log_a=-4 -> pH 6.47, log_a=-6 -> pH 7.47."""
    assert abs(cup.cu2_cuoh2_vertical_pH(-4.0) - 6.47) < 0.15
    assert abs(cup.cu2_cuoh2_vertical_pH(-6.0) - 7.47) < 0.15


def test_cuoh2_boundaries_are_directionally_beyond_unverified_CuO_readings():
    """Cu(OH)2 대체경계는 준안정상이므로 그림 4.1의 CuO 경계(pH 5.65, 절편 0.64V)보다
    더 높은 pH·더 높은 전위에 있어야 한다(노트 §2.2) — 크기는 미검증으로 남긴다."""
    assert cup.cu2_cuoh2_vertical_pH(-4.0) > 5.65
    assert cup.cu2o_cuoh2_boundary_V(0.0) > 0.64


def test_cu_plus_disproportionation_logK():
    """Cu+ 불균화 log K ~= +6.22 (노트 §2 식 6)."""
    assert abs(cup.cu_plus_disproportionation_logK() - 6.22) < 0.05
    assert cup.cu_plus_disproportionation_logK() > 5  # Cu+(aq) 열역학적 불안정 방향


@pytest.mark.parametrize("pH, E_V, expected", [
    (2.0, 0.3, "Cu2+"),
    (13.0, -0.5, "Cu"),
    (8.0, 0.3, "Cu(OH)2 (CuO 자리 대용, 미검증)"),
    (10.0, 0.0, "Cu2O"),
])
def test_stable_phase_contract_directions(pH, E_V, expected):
    """stable_phase()의 방향성 계약: 산성/고전위->Cu2+, 알칼리/저전위->Cu 금속,
    중성-알칼리/고전위->Cu(OH)2 대용, 중간전위->Cu2O."""
    assert cup.stable_phase(pH, E_V, log_a_cu=-4.0) == expected
