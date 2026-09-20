"""gw_preston_link.py 회귀 테스트 — _self_test()의 4개 항목을 pytest화."""
import gw_preston_link as link

P_REF = 20.7e3
V_REF = 0.8
KP_LIT = 1e-13


def test_n_contacts_linear_in_pressure():
    P_points = [14e3, 48e3, 96e3]
    n_points = [link.n_contacts_at(P) for P in P_points]
    slope, intercept = link.linear_fit_slope(P_points, n_points)
    max_resid = max(
        abs((slope * P + intercept) - n) / n for P, n in zip(P_points, n_points)
    )
    assert max_resid < 1e-6


def test_calibration_identity_at_ref_point():
    alpha = link.calibrate_alpha_removal(P_REF, V_REF, KP_LIT)
    mrr_direct = link.mrr_preston_direct(P_REF, V_REF, KP_LIT)
    mrr_gw = link.mrr_gw_link(P_REF, V_REF, alpha)
    assert abs(mrr_gw / mrr_direct - 1.0) < 1e-9


def test_calibration_mrr_in_literature_range():
    mrr_direct = link.mrr_preston_direct(P_REF, V_REF, KP_LIT)
    rate_nm_min = link.mrr_to_nm_per_min(mrr_direct)
    assert 50.0 <= rate_nm_min <= 1000.0


def test_gw_link_matches_preston_across_pressures():
    alpha = link.calibrate_alpha_removal(P_REF, V_REF, KP_LIT)
    for P in [14e3, 48e3, 96e3]:
        mrr_gw = link.mrr_gw_link(P, V_REF, alpha)
        mrr_pr = link.mrr_preston_direct(P, V_REF, KP_LIT)
        assert abs(mrr_gw / mrr_pr - 1.0) < 1e-4
