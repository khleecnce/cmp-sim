"""P5 unit tests — radial non-uniformity, zone pressure, slurry supply."""
import numpy as np
import pytest

from cmp_sim.core.units import psi_to_pa
from cmp_sim.models import preston, uniformity as un


R_W, R_CC = 0.150, 0.200


# ── the velocity field is NOT the cause of WIWNU ─────────────────────
def test_equal_rpm_gives_an_exactly_uniform_speed_field():
    """omega_w = omega_p makes |v| = omega_p * r_cc everywhere on the wafer."""
    rs, v = un.relative_speed_profile(R_W, R_CC, 60.0, 60.0)
    assert np.std(v) / np.mean(v) < 1e-12
    assert np.mean(v) == pytest.approx(2 * np.pi * 60.0 / 60.0 * R_CC, rel=1e-9)


def test_speed_nonuniformity_stays_tiny_even_off_match():
    """Off-match the wafer's own rotation averages the angle out, so the
    time-averaged speed still varies by only a fraction of a percent."""
    assert un.velocity_nonuniformity_pct(R_W, R_CC, 60.0, 60.0) < 1e-9
    assert un.velocity_nonuniformity_pct(R_W, R_CC, 50.0, 60.0) < 1.0


def test_pressure_dominates_velocity_as_a_source_of_nonuniformity():
    """Velocity alone contributes <1%, zone pressure tens of percent — which is
    why zone pressure is the knob that actually controls the profile."""
    vel_only = un.velocity_nonuniformity_pct(R_W, R_CC, 50.0, 60.0)
    rs, mrr, _ = preston.mrr_radial_nm_per_min(
        R_W, R_CC, 60.0, 60.0, 1e-13, psi_to_pa(3.0), n_radial=41,
        zone_pressures_pa=[psi_to_pa(2.0), psi_to_pa(3.0), psi_to_pa(5.0)],
        zone_edges_norm=[0.0, 0.5, 0.8, 1.0])
    press_only = un.metrics(rs, mrr)["sigma_pct"]
    assert press_only > 10.0 * vel_only


# ── pressure profiles ────────────────────────────────────────────────
def test_edge_pressure_profile_is_flat_in_the_middle_and_rises_at_the_rim():
    fn = un.edge_pressure_profile(psi_to_pa(3.0), amplitude=0.5, exponent=8.0)
    centre, mid, edge = float(fn(0.0)), float(fn(0.5)), float(fn(1.0))
    assert centre == pytest.approx(psi_to_pa(3.0), rel=1e-12)
    assert mid < 1.01 * centre                       # localised to the rim
    assert edge == pytest.approx(1.5 * centre, rel=1e-9)


def test_zone_profile_is_piecewise_constant():
    fn = un.zone_pressure_profile([0.0, 0.5, 1.0], [1.0e4, 2.0e4])
    assert float(fn(0.1)) == float(fn(0.4)) == 1.0e4
    assert float(fn(0.6)) == float(fn(0.99)) == 2.0e4


def test_metrics_are_area_weighted_not_simple_averages():
    """Outer radii carry more area, so an edge-heavy profile must pull the mean
    above the unweighted average."""
    rs = np.linspace(0.0, R_W, 81)
    vals = 100.0 + 50.0 * (rs / R_W)
    m = un.metrics(rs, vals)
    assert m["mean"] > float(np.mean(vals))
    assert m["edge_center"] == pytest.approx(1.5, rel=1e-6)


def test_metric_set_is_complete():
    rs = np.linspace(0.0, R_W, 41)
    m = un.metrics(rs, np.full_like(rs, 100.0))
    for key in ("mean", "half_range_pct", "sigma_pct", "three_sigma_pct", "edge_center"):
        assert key in m
    assert m["sigma_pct"] == pytest.approx(0.0, abs=1e-9)


# ── slurry supply ────────────────────────────────────────────────────
def _supply(flow):
    return un.diagnose_supply(
        flow_ml_min=flow, wafer_radius_m=R_W, mean_speed_m_s=1.25,
        pressure_pa=psi_to_pa(3.0), viscosity_pa_s=8.9e-4,
        pad_roughness_m=1.5e-6, groove_depth_m=7.5e-4, groove_area_fraction=0.25)


def test_cmp_operates_in_the_boundary_lubrication_regime():
    """l_hd = mu U / p is tens of nm against micron pad roughness, so
    lambda << 1. That is why abrasives reach the wafer at all."""
    s = _supply(200.0)
    assert s.lambda_ratio < 1.0
    assert s.regime == "boundary"
    assert 1.0 < s.film_thickness_m * 1e9 < 500.0


def test_friction_coefficient_is_in_the_reported_cmp_range():
    """Oxide CMP boundary-regime COF is reported around 0.2-0.4."""
    assert 0.15 < _supply(200.0).cof < 0.45


def test_required_flow_is_the_right_order_for_a_300mm_tool():
    """A real 300 mm process runs 150-300 ml/min, so the computed minimum has
    to sit below that — a criterion demanding thousands of ml/min would be
    wrong, not the tools."""
    assert 5.0 < _supply(200.0).required_flow_m3_s * 6.0e7 < 150.0


def test_supply_number_is_proportional_to_flow():
    assert _supply(400.0).supply_number == pytest.approx(
        2.0 * _supply(200.0).supply_number, rel=1e-9)


def test_adequate_flow_is_not_starved_and_low_flow_is():
    assert not _supply(200.0).starved
    starved = _supply(5.0)
    assert starved.starved
    assert any("starved" in w for w in starved.warnings)


def test_starvation_warning_admits_it_does_not_predict_the_droop():
    """The risk is predicted; the profile shape is geometry-specific and is not
    invented."""
    assert any("NOT predicted" in w for w in _supply(5.0).warnings)


def test_faster_platen_needs_more_flow():
    slow = un.diagnose_supply(flow_ml_min=200, wafer_radius_m=R_W, mean_speed_m_s=0.5,
                              pressure_pa=psi_to_pa(3), viscosity_pa_s=8.9e-4,
                              pad_roughness_m=1.5e-6, groove_depth_m=7.5e-4)
    fast = un.diagnose_supply(flow_ml_min=200, wafer_radius_m=R_W, mean_speed_m_s=2.5,
                              pressure_pa=psi_to_pa(3), viscosity_pa_s=8.9e-4,
                              pad_roughness_m=1.5e-6, groove_depth_m=7.5e-4)
    assert fast.required_flow_m3_s > slow.required_flow_m3_s
    assert fast.supply_number < slow.supply_number


def test_grooves_are_reported_as_a_reservoir_not_as_demand():
    """The groove volume dominates the interface volume but is re-circulated,
    so it must show up in residence time, not in the flow requirement."""
    s = _supply(200.0)
    assert s.interface_volume_cm3 > 1.0
    assert s.mean_residence_time_s > 0.5
    assert any("reservoir" in n for n in s.notes)


def test_full_hydrodynamic_film_is_flagged_as_out_of_regime():
    """A thick film separating pad and wafer would stop removal entirely."""
    s = un.diagnose_supply(flow_ml_min=200, wafer_radius_m=R_W, mean_speed_m_s=5.0,
                           pressure_pa=psi_to_pa(0.05), viscosity_pa_s=0.5,
                           pad_roughness_m=1.0e-8, groove_depth_m=7.5e-4)
    assert s.lambda_ratio > 3.0
    assert any("outside the model" in w for w in s.warnings)


# ── starvation profile ───────────────────────────────────────────────
def test_no_starvation_length_means_no_invented_profile():
    rs = np.linspace(0.0, R_W, 21)
    assert un.starvation_profile(rs, R_W, 0.5, None) is None


def test_starvation_profile_is_centre_slow_and_edge_fed():
    """Slurry enters at the rim, so the centre sees the least."""
    rs = np.linspace(0.0, R_W, 21)
    w = un.starvation_profile(rs, R_W, 0.4, 0.05)
    assert w[-1] > w[0]
    assert w[-1] == pytest.approx(1.0, rel=1e-9)
    assert np.all(np.diff(w) > 0)


def test_ample_supply_flattens_the_starvation_profile():
    rs = np.linspace(0.0, R_W, 21)
    w = un.starvation_profile(rs, R_W, 1.0, 0.05)
    assert np.allclose(w, 1.0, rtol=1e-12)
