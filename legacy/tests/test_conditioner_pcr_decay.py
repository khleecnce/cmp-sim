"""conditioner_pcr_decay.py 회귀 테스트 — _self_test()의 5항목을 pytest화."""
import math
import numpy as np

import conditioner_pcr_decay as cpd


def test_anchor_calibration_exact():
    ratio = cpd.pcr_decay(cpd.ENTEGRIS_ANCHOR_T_HOURS, 1.0, cpd.TAU_AGING_HOURS)
    assert abs(ratio - cpd.ENTEGRIS_ANCHOR_RATIO) < 1e-9


def test_tau_inf_gives_constant_pcr():
    assert abs(cpd.pcr_decay(1000.0, 1.0, float("inf")) - 1.0) < 1e-12


def test_pcr_monotonic_nonincreasing():
    ts = np.linspace(0, 100, 50)
    pcrs = np.array([cpd.pcr_decay(t, 1.0, cpd.TAU_AGING_HOURS) for t in ts])
    assert np.all(np.diff(pcrs) <= 1e-15)


def test_aging_conditioner_wears_more_than_ideal():
    r_aging = cpd.simulate_conditioned_wear(tau_hours=cpd.TAU_AGING_HOURS, n_steps=40, dt_hours=1.0)
    r_ideal = cpd.simulate_conditioned_wear(tau_hours=float("inf"), n_steps=40, dt_hours=1.0)
    assert r_aging["mean_height"][-1] < r_ideal["mean_height"][-1]


def test_three_tier_ranking_none_lt_aging_lt_ideal():
    r_none = cpd.simulate_conditioned_wear(tau_hours=cpd.TAU_AGING_HOURS, C1_cond=0.0, n_steps=40, dt_hours=1.0)
    r_aging = cpd.simulate_conditioned_wear(tau_hours=cpd.TAU_AGING_HOURS, n_steps=40, dt_hours=1.0)
    r_ideal = cpd.simulate_conditioned_wear(tau_hours=float("inf"), n_steps=40, dt_hours=1.0)
    assert r_none["mean_height"][-1] < r_aging["mean_height"][-1] < r_ideal["mean_height"][-1]


def test_calibrate_tau_from_anchor_rejects_bad_ratio():
    import pytest
    with __import__("pytest").raises(ValueError):
        cpd.calibrate_tau_from_anchor(50.0, 1.5)
