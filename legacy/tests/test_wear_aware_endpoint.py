"""wear_aware_endpoint.py 회귀 테스트 — _selftest()의 4개 검증 항목을 pytest화."""
import numpy as np

import wear_aware_endpoint as wae
import pad_wear_glazing as pwg
import process_time as pt


def test_cumulative_matches_full_trapz():
    r = pwg.simulate_pad_wear(n_steps=40)
    t_arr, mrr_arr = r["t"], r["MRR"]
    cum = wae.cumulative_removed_thickness_drift(t_arr, mrr_arr)
    full_trapz = np.trapezoid(mrr_arr, t_arr)
    rel_err = abs(cum[-1] - full_trapz) / full_trapz
    assert rel_err < 1e-9


def test_no_drift_limit_matches_process_time_v0():
    r0 = pwg.simulate_pad_wear(n_steps=40, C1=0.0)
    t0, mrr0 = r0["t"], r0["MRR"]
    target_const = 0.5 * wae.cumulative_removed_thickness_drift(t0, mrr0)[-1]
    t_drift0 = wae.endpoint_time_drift(target_const, t0, mrr0)
    t_v0 = pt.endpoint_time(target_const, mrr0[0])
    rel_err = abs(t_drift0 - t_v0) / t_v0
    assert rel_err < 0.01


def test_naive_is_optimistic_when_mrr_decays():
    r = pwg.simulate_pad_wear(n_steps=40)
    target_drift = 0.5 * wae.cumulative_removed_thickness_drift(r["t"], r["MRR"])[-1]
    cmp = wae.compare_naive_vs_drift(target_drift, pad_wear_kwargs={"n_steps": 40})
    assert cmp["optimism_pct"] > 0


def test_unreachable_target_raises_runtime_error():
    r = pwg.simulate_pad_wear(n_steps=40)
    huge_target = wae.cumulative_removed_thickness_drift(r["t"], r["MRR"])[-1] * 1000.0
    try:
        wae.endpoint_time_drift(huge_target, r["t"], r["MRR"])
        raised = False
    except RuntimeError:
        raised = True
    assert raised
