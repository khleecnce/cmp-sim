"""viscoelastic_maxwell.py 회귀 테스트 — 하단 _self_test()의 5개 검증 항목을 pytest화.

물리 로직은 재구현하지 않고 viscoelastic_maxwell.py의 함수를 그대로 호출해 assert한다.
"""
import numpy as np

import viscoelastic_maxwell as vm

E = 1.0
TAU0 = 1.0


def test_low_frequency_limit_zero_storage_and_loss():
    """omega -> 0 (완전 이완): E' -> 0, E'' -> 0."""
    Es_low, El_low = vm.maxwell_storage_loss([1e-6], E, TAU0)
    assert Es_low[0] < 1e-6
    assert El_low[0] < 1e-5


def test_high_frequency_limit_storage_equals_E():
    """omega -> inf (순간탄성): E' -> E, E'' -> 0."""
    Es_high, El_high = vm.maxwell_storage_loss([1e6], E, TAU0)
    assert abs(Es_high[0] - E) < 1e-5
    assert El_high[0] < 1e-5


def test_loss_peak_equals_E_over_2_at_omega_1_over_tau0():
    """해석적으로 E''_max = E/2 at omega = 1/tau0."""
    omega_peak = 1.0 / TAU0
    _, El_pk = vm.maxwell_storage_loss([omega_peak], E, TAU0)
    assert abs(El_pk[0] - E / 2.0) < 1e-10


def test_grid_search_peak_location_matches_1_over_tau0():
    """넓은 범위 grid search로도 E''의 최대점이 omega=1/tau0 근방임을 확인."""
    omega_peak = 1.0 / TAU0
    omega_scan = np.logspace(-3, 3, 100001) / TAU0
    _, El_scan = vm.maxwell_storage_loss(omega_scan, E, TAU0)
    omega_at_max = omega_scan[int(np.argmax(El_scan))]
    assert abs(omega_at_max - omega_peak) / omega_peak < 1e-3


def test_tan_delta_limits():
    """tan(delta): 저주파에서 매우 큼(점성 지배), 고주파에서 0에 근접(탄성 지배)."""
    Es_low, El_low = vm.maxwell_storage_loss([1e-6], E, TAU0)
    Es_high, El_high = vm.maxwell_storage_loss([1e6], E, TAU0)
    td_low = vm.tan_delta(Es_low, El_low)[0]
    td_high = vm.tan_delta(Es_high, El_high)[0]
    assert td_low > 100
    assert td_high < 1e-4
