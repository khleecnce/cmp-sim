"""gw_pressure_solve.py 회귀 테스트 — _self_test()의 5개 항목을 pytest화."""
import gw_pressure_solve as gps
import gw_contact as gw

E_STAR = 1e9
R = 5e-6
BETA = 1.0 / 0.3e-6
ETA = 1e11
A_N = 1e-4


def test_solve_separation_roundtrip():
    d_true = 0.4e-6
    W = gw.gw_numeric(d_true, BETA, ETA, A_N, E_STAR, R)["W"]
    P = W / A_N
    d_rec = gps.solve_separation(P, A_N, BETA, ETA, E_STAR, R)
    assert abs(d_rec - d_true) / d_true < 1e-6


def test_p_r_mean_nearly_invariant_across_pressure():
    pressures = [14e3, 48e3, 96e3]
    states = [gps.local_contact_state(P, A_N, BETA, ETA, E_STAR, R) for P in pressures]
    p_r = [s["p_r_mean"] for s in states]
    avg = sum(p_r) / len(p_r)
    assert max(abs(v - avg) / avg for v in p_r) < 1e-3


def test_p_r_mean_matches_analytic_ratio():
    state = gps.local_contact_state(48e3, A_N, BETA, ETA, E_STAR, R)
    analytic = gw.gw_analytic_ratio(BETA, E_STAR, R)
    assert abs(state["p_r_mean"] - 1.0 / analytic) / (1.0 / analytic) < 1e-3


def test_contact_area_fraction_monotonic_with_pressure():
    pressures = [14e3, 48e3, 96e3]
    fracs = [gps.local_contact_state(P, A_N, BETA, ETA, E_STAR, R)["contact_area_fraction"] for P in pressures]
    assert fracs[0] < fracs[1] < fracs[2]
