"""wiwnu_pattern_combined.py의 _selftest() 항목을 pytest화한 회귀 테스트.

극한 a)/b)는 구조적 항등식(자명한 배선 검증), c)는 분리가능 곱구조의 대수적 하한
(sigma_pct/CV 기준)을 확인한다. half_range_pct는 대수적 하한이 보장되지 않는 지표이므로
assert하지 않고 정보로만 취급한다(wiwnu_pattern_combined.py 상단 docstring 참조).
"""
import numpy as np

from wiwnu import mrr_radial, wiwnu, p_uniform, p_edge_concentration
from pattern_density import effective_density, oxide_removed_up
from wiwnu_pattern_combined import combined_removal_map, _area_weighted_2d

R_w, r_cc, kp = 0.150, 0.200, 1.0e-13
n_r = 401


def _die_rho_eff():
    x_die = np.linspace(0.0, 20.0, 401)
    rho_local = 0.5 + 0.2 * np.sin(2 * np.pi * x_die / 4.0)
    return effective_density(x_die, rho_local, PL=3.0)


def test_limit_a_uniform_rho_eff_matches_wiwnu_alone():
    rs_ref, mrr_ref = mrr_radial(R_w, r_cc, 50.0, 60.0, kp,
                                  p_edge_concentration(20.7e3, amp=0.30, n=8), n_r=n_r)
    rho_ones = np.ones(51)
    res = combined_removal_map(rs_ref, rho_ones, R_w, r_cc, 50.0, 60.0, kp,
                                p_edge_concentration(20.7e3, amp=0.30, n=8), n_r=n_r)
    assert np.max(np.abs(res["RR"] - mrr_ref[:, None])) < 1e-15

    w_ref = wiwnu(rs_ref, mrr_ref)
    w_a = _area_weighted_2d(rs_ref, res["RR"])
    assert abs(w_a["sigma_pct"] - w_ref["sigma_pct"]) / w_ref["sigma_pct"] < 1e-9


def test_limit_b_constant_K_matches_pattern_density_alone():
    rs_u, mrr_u = mrr_radial(R_w, r_cc, 60.0, 60.0, kp, p_uniform(20.7e3), n_r=n_r)
    k_spread = (mrr_u.max() - mrr_u.min()) / mrr_u.mean()
    assert k_spread < 1e-9
    K0 = float(mrr_u[0])

    rho_eff_die = _die_rho_eff()
    res = combined_removal_map(rs_u, rho_eff_die, R_w, r_cc, 60.0, 60.0, kp,
                                p_uniform(20.7e3), n_r=n_r)

    t_small = 1e-9
    h0_huge = 1e6
    removed = oxide_removed_up(t_small, K0, rho_eff_die, h0_huge)
    rr_up_reference = removed / t_small
    rel_err = np.max(np.abs(res["RR"] - rr_up_reference[None, :]) / rr_up_reference[None, :])
    assert rel_err < 1e-9


def test_combined_cv_lower_bound_holds():
    """분리가능 곱구조: CV_combined^2 = CV_r^2 + CV_x^2 + CV_r^2*CV_x^2 >= max(CV_r^2, CV_x^2)."""
    rho_eff_die = _die_rho_eff()
    rs_c, mrr_c = mrr_radial(R_w, r_cc, 50.0, 60.0, kp,
                              p_edge_concentration(20.7e3, amp=0.30, n=8), n_r=n_r)
    res_c = combined_removal_map(rs_c, rho_eff_die, R_w, r_cc, 50.0, 60.0, kp,
                                  p_edge_concentration(20.7e3, amp=0.30, n=8), n_r=n_r)
    combined_w = _area_weighted_2d(rs_c, res_c["RR"])

    radial_only = wiwnu(rs_c, mrr_c)
    K_const = np.full_like(rs_c, mrr_c.mean())
    RR_pattern_only = K_const[:, None] / rho_eff_die[None, :]
    pattern_only_w = _area_weighted_2d(rs_c, RR_pattern_only)

    assert combined_w["sigma_pct"] >= max(radial_only["sigma_pct"], pattern_only_w["sigma_pct"]) - 1e-9
