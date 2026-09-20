"""sim/integration/spatiotemporal_removal.py self-test 항목을 pytest화."""
import numpy as np

from wiwnu import p_edge_concentration, mrr_radial
from pattern_density import effective_density
from spatiotemporal_removal import thickness_field, endpoint_time_at, cv_percent_2d

R_w, r_cc, kp = 0.150, 0.200, 1.0e-13
n_r = 401


def _die_rho_eff():
    x_die = np.linspace(0.0, 20.0, 401)
    rho_local = 0.5 + 0.2 * np.sin(2 * np.pi * x_die / 4.0)
    return effective_density(x_die, rho_local, PL=3.0)


def _pfn():
    return p_edge_concentration(20.7e3, amp=0.30, n=8)


def test_thickness_field_linear_in_time():
    rs_ref, _ = mrr_radial(R_w, r_cc, 50.0, 60.0, kp, _pfn(), n_r=n_r)
    rho_eff = _die_rho_eff()
    r60 = thickness_field(rs_ref, rho_eff, R_w, r_cc, 50.0, 60.0, kp, _pfn(), 60.0, n_r=n_r)
    r120 = thickness_field(rs_ref, rho_eff, R_w, r_cc, 50.0, 60.0, kp, _pfn(), 120.0, n_r=n_r)
    assert np.max(np.abs(r120["thickness"] / r60["thickness"] - 2.0)) < 1e-9


def test_uniform_rho_eff_matches_K_times_t():
    rs_ref, mrr_ref = mrr_radial(R_w, r_cc, 50.0, 60.0, kp, _pfn(), n_r=n_r)
    rho_ones = np.ones(51)
    res = thickness_field(rs_ref, rho_ones, R_w, r_cc, 50.0, 60.0, kp, _pfn(), 90.0, n_r=n_r)
    expect = mrr_ref[:, None] * 90.0
    assert np.max(np.abs(res["thickness"] - expect)) < 1e-15


def test_endpoint_time_wiring_matches_direct_division():
    rs_ref, _ = mrr_radial(R_w, r_cc, 50.0, 60.0, kp, _pfn(), n_r=n_r)
    rho_eff = _die_rho_eff()
    res = thickness_field(rs_ref, rho_eff, R_w, r_cc, 50.0, 60.0, kp, _pfn(), 60.0, n_r=n_r)
    rr_cell = float(res["RR"][10, 200])
    target = 50e-9
    assert abs(endpoint_time_at(target, rr_cell) - target / rr_cell) / (target / rr_cell) < 1e-12


def test_cv_time_invariant():
    rs_ref, _ = mrr_radial(R_w, r_cc, 50.0, 60.0, kp, _pfn(), n_r=n_r)
    rho_eff = _die_rho_eff()
    r60 = thickness_field(rs_ref, rho_eff, R_w, r_cc, 50.0, 60.0, kp, _pfn(), 60.0, n_r=n_r)
    r120 = thickness_field(rs_ref, rho_eff, R_w, r_cc, 50.0, 60.0, kp, _pfn(), 120.0, n_r=n_r)
    cv60 = cv_percent_2d(r60["thickness"])
    cv120 = cv_percent_2d(r120["thickness"])
    assert abs(cv120 - cv60) / cv60 < 1e-9
