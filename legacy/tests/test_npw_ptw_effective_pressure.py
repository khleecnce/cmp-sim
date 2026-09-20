"""npw_ptw_effective_pressure.py 회귀 테스트 — _self_test()의 항목을 pytest화.

노트 knowledge/cmp/product-wafer-proxy-metrics-virtual-metrology.md §4, §6 verify (B)(B')의
값만 재현한다 (새 문헌 숫자 없음). 전부 문헌 표값과의 직접 대조 또는 노트의 해석적 결론
(1/ρ 과대예측, 온도 단조성) 검증이다 — 스냅샷·change-detector 없음.
"""
import pytest

import npw_ptw_effective_pressure as pep


def test_table_ratio_matches_raw_table_value():
    r = pep.table_ratio(0.10, 3, 45)
    assert abs(r - 12.73 / 3) < 1e-9


def test_mean_ratio_at_density_010():
    assert abs(pep.mean_ratio_at_density(0.10) - 2.67) < 0.02


def test_mean_ratio_at_density_050():
    assert abs(pep.mean_ratio_at_density(0.50) - 1.79) < 0.02


def test_mean_ratio_at_density_090():
    assert abs(pep.mean_ratio_at_density(0.90) - 1.27) < 0.02


@pytest.mark.parametrize("density", [0.10, 0.50, 0.90])
def test_mean_ratio_within_25pct_of_summary(density):
    rel_err = abs(pep.mean_ratio_at_density(density) - pep.summary_ratio(density)) / pep.summary_ratio(density)
    assert rel_err <= 0.25


def test_inverse_density_model_overpredicts_low_density():
    r10 = pep.inverse_density_ratio(0.10) / pep.mean_ratio_at_density(0.10)
    assert r10 > 3.5


@pytest.mark.parametrize("density", [0.10, 0.50, 0.90])
@pytest.mark.parametrize("pressure_psi", [3, 7])
def test_ratio_increases_with_temperature(density, pressure_psi):
    lo = pep.table_ratio(density, pressure_psi, 10)
    hi = pep.table_ratio(density, pressure_psi, 45)
    assert hi > lo


def test_table_ratio_rejects_unsupported_pressure():
    with pytest.raises(ValueError):
        pep.table_ratio(0.10, 5, 23)


def test_effective_pressure_ratio_none_pressure_is_average():
    epr = pep.effective_pressure_ratio(0.10, temp_C=23)
    expect = (pep.table_ratio(0.10, 3, 23) + pep.table_ratio(0.10, 7, 23)) / 2.0
    assert abs(epr - expect) < 1e-9
