"""spatiotemporal_removal_physical_kp.py self-test 항목을 pytest화."""
import numpy as np

from wiwnu import p_uniform, p_zoned, mrr_radial
from pattern_density import effective_density
from spatiotemporal_removal import thickness_field
from spatiotemporal_removal_physical_kp import (
    thickness_field_physical_kp,
    kp_eff_at,
)
import gw_preston_link as link

R_w, r_cc = 0.150, 0.200
rpm_w, rpm_p = 50.0, 60.0
n_r = 401
P_ref, V_ref, kp_lit = 20.7e3, 0.8, 1e-13
t_sec = 60.0


def _die_rho_eff():
    x_die = np.linspace(0.0, 20.0, 401)
    rho_local = 0.5 + 0.2 * np.sin(2 * np.pi * x_die / 4.0)
    return effective_density(x_die, rho_local, PL=3.0)


def test_uniform_pressure_matches_constant_kp_field():
    pfn = p_uniform(P_ref)
    rs_ref, _ = mrr_radial(R_w, r_cc, rpm_w, rpm_p, kp_lit, pfn, n_r=n_r)
    rho_eff = _die_rho_eff()
    res_const = thickness_field(rs_ref, rho_eff, R_w, r_cc, rpm_w, rpm_p, kp_lit, pfn,
                                t_sec, n_r=n_r)
    res_phys = thickness_field_physical_kp(rs_ref, rho_eff, R_w, r_cc, rpm_w, rpm_p, pfn,
                                           V_ref, P_ref, kp_lit, t_sec, n_r=n_r)
    rel_dev = np.max(np.abs(res_phys["thickness"] / res_const["thickness"] - 1.0))
    assert rel_dev < 1e-6


def test_wide_pressure_range_deviation_is_small_and_finite():
    """물리적 kp_eff와 상수 kp_lit 모델의 편차가 작다 (TEST-AUDIT §3-A #4).

    근거: #3(test_models.py::gw_and_preston_converge)과 동일 — GW 지수분포에서
    n_contacts ∝ P가 정확한 해석해이므로 14~96kPa 넓은 범위에서도 편차는
    이산화 오차 수준(<1e-3, 실측시 ~1e-12)이어야 한다. 1e-2는 실제 회귀를
    가릴 만큼 느슨했다.
    """
    pfn = p_zoned([0.0, 0.33, 0.66, 1.0], [14e3, 48e3, 96e3])
    rs_wide, _ = mrr_radial(R_w, r_cc, rpm_w, rpm_p, kp_lit, pfn, n_r=n_r)
    rho_eff = _die_rho_eff()
    res_const = thickness_field(rs_wide, rho_eff, R_w, r_cc, rpm_w, rpm_p, kp_lit, pfn,
                                t_sec, n_r=n_r)
    res_phys = thickness_field_physical_kp(rs_wide, rho_eff, R_w, r_cc, rpm_w, rpm_p, pfn,
                                           V_ref, P_ref, kp_lit, t_sec, n_r=n_r)
    rel_dev = np.abs(res_phys["thickness"] / res_const["thickness"] - 1.0)
    assert np.all(np.isfinite(rel_dev))
    assert np.max(rel_dev) < 1e-3


def test_alpha_removal_matches_gw_preston_link_calibration():
    pfn = p_uniform(P_ref)
    rs_ref, _ = mrr_radial(R_w, r_cc, rpm_w, rpm_p, kp_lit, pfn, n_r=n_r)
    rho_eff = _die_rho_eff()
    res_phys = thickness_field_physical_kp(rs_ref, rho_eff, R_w, r_cc, rpm_w, rpm_p, pfn,
                                           V_ref, P_ref, kp_lit, t_sec, n_r=n_r)
    alpha_expect = link.calibrate_alpha_removal(P_ref, V_ref, kp_lit)
    assert abs(res_phys["alpha_removal"] / alpha_expect - 1.0) < 1e-12


def test_kp_eff_at_ref_pressure_equals_literature_kp():
    alpha = link.calibrate_alpha_removal(P_ref, V_ref, kp_lit)
    assert abs(kp_eff_at(P_ref, alpha) / kp_lit - 1.0) < 1e-9


def test_uniform_rho_eff_matches_K_eff_times_t():
    pfn = p_uniform(P_ref)
    rs_ref, _ = mrr_radial(R_w, r_cc, rpm_w, rpm_p, kp_lit, pfn, n_r=n_r)
    rho_ones = np.ones(51)
    res = thickness_field_physical_kp(rs_ref, rho_ones, R_w, r_cc, rpm_w, rpm_p, pfn,
                                      V_ref, P_ref, kp_lit, 90.0, n_r=n_r)
    expect = res["K_r"][:, None] * 90.0
    assert np.max(np.abs(res["thickness"] - expect)) < 1e-15
