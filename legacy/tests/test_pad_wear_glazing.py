"""pad_wear_glazing.py 회귀 테스트 — _self_test()의 5개 항목을 pytest화."""
import numpy as np
import pad_wear_glazing as pwg
import gw_contact as gw


def test_mean_height_monotonic_nonincreasing():
    r = pwg.simulate_pad_wear(n_steps=30)
    h = r["mean_height"]
    assert np.all(np.diff(h) <= 1e-15)


def test_mrr_monotonic_nonincreasing():
    r = pwg.simulate_pad_wear(n_steps=30)
    mrr = r["MRR"]
    assert np.all(np.diff(mrr) <= 1e-18)


def test_decay_diminishing_returns():
    r = pwg.simulate_pad_wear(n_steps=30)
    mrr = r["MRR"]
    early_drop = mrr[0] - mrr[len(mrr) // 3]
    late_drop = mrr[2 * len(mrr) // 3] - mrr[-1]
    assert early_drop > late_drop


def test_discrete_t0_matches_continuum_gw():
    r0 = pwg.simulate_pad_wear(n_steps=1, n_asperity=200000)
    d0 = r0["d"][0]
    cont = gw.gw_numeric(d0, beta=1.0 / 0.3e-6, eta=200000 / 1e-4, A_n=1e-4, E_star=1e9, R=5e-6)
    p_r_cont = cont["W"] / cont["A_r"]
    p_r_disc = r0["p_r"][0]
    assert abs(p_r_disc - p_r_cont) / p_r_cont < 0.1


def test_p_r_changes_significantly_over_wear_time():
    r = pwg.simulate_pad_wear(n_steps=30)
    pr = r["p_r"]
    change_pct = abs(pr[-1] - pr[0]) / pr[0] * 100
    assert change_pct > 1.0
