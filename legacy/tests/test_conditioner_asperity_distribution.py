"""conditioner_asperity_distribution.py 회귀 테스트 — _self_test()의 5항목을 pytest화."""
import math
import numpy as np

import conditioner_asperity_distribution as cad
import conditioner_pcr_decay as cpd


def test_scale_factor_identity_at_t0():
    t_arr, s_arr = cad.scale_factor_series(cad.A0_DEFAULT, float("inf"), n_steps=1, dt_hours=1.0)
    assert abs(s_arr[0] - 1.0) < 1e-12


def test_ideal_conditioner_halves_sigma_at_calibrated_time():
    sigma0 = 8.112e-6
    n_steps = int(cad.T_HALF_HOURS) + 1
    t_arr, sig_arr = cad.sigma_series(sigma0, cad.A0_DEFAULT, float("inf"), n_steps=n_steps, dt_hours=1.0)
    assert abs(sig_arr[-1] / sigma0 - 0.5) < 0.02


def test_aging_conditioner_sigma_shrinks_slower_than_ideal():
    sigma0 = 8.112e-6
    n_steps = int(cad.T_HALF_HOURS) + 1
    _, sig_ideal = cad.sigma_series(sigma0, cad.A0_DEFAULT, float("inf"), n_steps=n_steps, dt_hours=1.0)
    _, sig_aging = cad.sigma_series(sigma0, cad.A0_DEFAULT, cpd.TAU_AGING_HOURS, n_steps=n_steps, dt_hours=1.0)
    assert sig_aging[-1] > sig_ideal[-1]


def test_sigma_monotonic_nonincreasing_under_ideal_conditioner():
    sigma0 = 8.112e-6
    n_steps = int(cad.T_HALF_HOURS) + 1
    _, sig_arr = cad.sigma_series(sigma0, cad.A0_DEFAULT, float("inf"), n_steps=n_steps, dt_hours=1.0)
    assert np.all(np.diff(sig_arr) <= 1e-15)


def test_similarity_scaling_matches_theoretical_ratio():
    rng = np.random.default_rng(7)
    n = 200000
    sigma0 = 8.112e-6
    heights = rng.normal(loc=50e-6, scale=sigma0, size=n)
    A_test = cad.A0_DEFAULT
    t_test = 20.0
    scaled = cad.apply_similarity_scaling(heights, d=0.0, A=A_test, t=t_test)
    theory_ratio = math.exp(2.0 * A_test * t_test)
    empirical_ratio = float(scaled.std() / heights.std())
    assert abs(empirical_ratio - theory_ratio) / theory_ratio < 1e-3
