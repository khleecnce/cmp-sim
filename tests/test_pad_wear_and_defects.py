"""P7 + P8 unit tests — pad life drift and scratch-risk proxy."""
import math

import pytest

from cmp_sim.models import defect_proxy as dp
from cmp_sim.pad import wear


# ══════════════════════════════════════════════════════════════════
# P7 — pad wear and conditioning
# ══════════════════════════════════════════════════════════════════
def test_contact_count_decays_with_polishing_time():
    """Jeong 2024 Table 1: unconditioned polishing destroys contact points."""
    assert wear.contact_ratio(3.0, 0.0) == pytest.approx(1.0, rel=1e-9)
    assert wear.contact_ratio(3.0, 5.0) < 1.0
    assert wear.contact_ratio(3.0, 10.0) < wear.contact_ratio(3.0, 5.0)


def test_higher_pressure_glazes_the_pad_faster():
    """tau shortens with load, so a high-pressure process loses contacts sooner."""
    assert wear.contact_decay_tau_min(5.0) < wear.contact_decay_tau_min(2.0)


def test_asperity_summits_blunt_over_time():
    """Eq. 4: the mean summit radius grows linearly with polish time."""
    r0 = wear.mean_asperity_radius_um(3.0, 0.0)
    r10 = wear.mean_asperity_radius_um(3.0, 10.0)
    assert r10 > r0
    assert wear.radius_growth_ratio(3.0, 10.0) == pytest.approx(r10 / r0, rel=1e-9)


def test_unmeasured_pressure_is_snapped_not_extrapolated():
    """Table 1 covers 2-5 psi only; a fit must not be run outside its data."""
    state = wear.evaluate(pressure_psi=8.0, polish_minutes=5.0)
    assert any("snapped" in w for w in state.warnings)


def test_mrr_trend_proxy_is_labelled_as_direction_only():
    """The inherited self-test found its peak at ~7 min against a measured
    3 min, so the value must not be presented as calibrated."""
    state = wear.evaluate(pressure_psi=3.0, polish_minutes=5.0)
    assert any("direction, not the value" in n for n in state.notes)


def test_conditioner_cut_rate_decays_with_disk_hours():
    """Entegris field anchor: 16% of the initial cut rate after 50 h."""
    assert wear.disk_cut_rate_ratio(0.0) == pytest.approx(1.0, rel=1e-9)
    assert wear.disk_cut_rate_ratio(50.0) == pytest.approx(0.16, rel=1e-3)
    assert wear.disk_cut_rate_ratio(100.0) < wear.disk_cut_rate_ratio(50.0)


def test_a_worn_disk_is_warned_about():
    state = wear.evaluate(pressure_psi=3.0, polish_minutes=5.0, disk_hours=80.0)
    assert any("worn" in w for w in state.warnings)


# ── glazing vs conditioning balance ──────────────────────────────────
def test_steady_state_rises_with_conditioning_and_falls_with_glazing():
    """n_ss = k_c G / (k_g + k_c G)."""
    base = wear.steady_state_contact_ratio(1.0, 1.0)
    assert base == pytest.approx(0.5, rel=1e-12)
    assert wear.steady_state_contact_ratio(1.0, 4.0) > base
    assert wear.steady_state_contact_ratio(4.0, 1.0) < base


def test_a_worn_disk_lowers_the_steady_state_plateau():
    """Even with the same conditioning recipe, a blunt disk leaves the pad glazed."""
    fresh = wear.steady_state_contact_ratio(1.0, 2.0, disk_effectiveness=1.0)
    worn = wear.steady_state_contact_ratio(1.0, 2.0, disk_effectiveness=0.16)
    assert worn < fresh


def test_steady_state_is_bounded_between_zero_and_one():
    for kg, kc in ((0.01, 10.0), (10.0, 0.01), (1.0, 1.0)):
        assert 0.0 < wear.steady_state_contact_ratio(kg, kc) < 1.0


def test_rates_must_be_physical():
    with pytest.raises(ValueError):
        wear.steady_state_contact_ratio(-1.0, 1.0)
    with pytest.raises(ValueError):
        wear.steady_state_contact_ratio(0.0, 0.0)


def test_missing_rate_constants_are_reported_rather_than_assumed():
    state = wear.evaluate(pressure_psi=3.0, polish_minutes=5.0)
    assert state.steady_state_contact is None
    assert any("not supplied" in w for w in state.warnings)


# ══════════════════════════════════════════════════════════════════
# P8 — defect proxy
# ══════════════════════════════════════════════════════════════════
def test_risk_is_exactly_one_at_the_reference_slurry():
    r = dp.evaluate(d99_nm=350.0, d99_ref_nm=350.0, exponent=1.44)
    assert r.delta == pytest.approx(1.0, rel=1e-12)


def test_a_fatter_tail_raises_the_risk_superlinearly():
    """Scratch count follows the tail, with an exponent above 1."""
    r = dp.evaluate(d99_nm=700.0, d99_ref_nm=350.0, exponent=1.44)
    assert r.delta == pytest.approx(2.0 ** 1.44, rel=1e-9)
    assert r.delta > 2.0


def test_tungsten_is_more_scratch_sensitive_than_ceria_systems():
    """Egan & Kim 2019 give n = 2.54 for W against 1.44 for ceria."""
    w = dp.evaluate(d99_nm=700.0, d99_ref_nm=350.0, exponent=2.54)
    ce = dp.evaluate(d99_nm=700.0, d99_ref_nm=350.0, exponent=1.44)
    assert w.delta > ce.delta


def test_agglomeration_is_an_independent_path():
    """Basim & Moudgil 2002: mean size flat, AFM Rmax doubled. D99 cannot see it."""
    plain = dp.evaluate(d99_nm=350.0, d99_ref_nm=350.0, exponent=1.44)
    agg = dp.evaluate(d99_nm=350.0, d99_ref_nm=350.0, exponent=1.44,
                      aggregate_ratio=1.0)
    assert agg.delta == pytest.approx(2.0 * plain.delta, rel=1e-9)


def test_crossing_the_scratch_threshold_is_warned():
    r = dp.evaluate(d99_nm=900.0, d99_ref_nm=350.0, exponent=1.44)
    assert r.threshold_ratio > 1.0
    assert any("scratch threshold" in w for w in r.warnings)


def test_sitting_near_the_threshold_warns_the_exponent_is_least_reliable():
    r = dp.evaluate(d99_nm=dp.SCRATCH_THRESHOLD_NM, d99_ref_nm=350.0, exponent=1.44)
    assert any("least" in w for w in r.warnings)


def test_mean_size_alone_cannot_drive_the_proxy():
    """A 70 nm D50 is an order below the threshold; without a tail there is
    nothing to predict from."""
    r = dp.evaluate(d99_nm=None, d99_ref_nm=None, exponent=1.44)
    assert not r.active
    assert r.delta == 1.0
    assert any("tail" in w for w in r.warnings)


def test_d99_estimated_from_d50_is_flagged_as_an_estimate():
    r = dp.evaluate(d99_nm=None, d50_nm=70.0, d99_ref_nm=350.0, exponent=1.44)
    assert r.d99_nm == pytest.approx(350.0, rel=1e-9)
    assert any("estimate" in w for w in r.warnings)


def test_missing_exponent_disables_the_proxy_rather_than_borrowing_one():
    r = dp.evaluate(d99_nm=350.0, d99_ref_nm=350.0, exponent=None)
    assert not r.active
    assert any("must not be borrowed" in w for w in r.warnings)


# ── scratch dimensions ───────────────────────────────────────────────
def test_softer_films_take_wider_deeper_scratches():
    """Same slurry, different film: Cu (~1 GPa) vs W (~7 GPa). Severity is set
    by film hardness, which is why one risk index means different damage."""
    cu_w = dp.max_scratch_width_m(350.0, 0.31e9, 1.0e9)
    w_w = dp.max_scratch_width_m(350.0, 0.31e9, 7.0e9)
    assert cu_w > w_w
    assert dp.max_scratch_depth_m(350.0, 0.31e9, 1.0e9) > dp.max_scratch_depth_m(
        350.0, 0.31e9, 7.0e9)


def test_scratch_width_follows_the_square_root_of_the_hardness_ratio():
    """2 a_max = D99 sqrt(H_pad/H_film) — Saka 2008 Eq. 14."""
    got = dp.max_scratch_width_m(680.0, 0.31e9, 7.0e9)
    assert got == pytest.approx(680e-9 * math.sqrt(0.31 / 7.0), rel=1e-12)


def test_scratch_dimensions_are_reported_when_hardness_is_known():
    r = dp.evaluate(d99_nm=700.0, d99_ref_nm=350.0, exponent=2.54,
                    pad_hardness_pa=0.31e9, film_hardness_pa=1.0e9, film="cu")
    d = r.as_dict()
    assert d["max_scratch_width_nm"] > 0
    assert d["max_scratch_depth_nm"] > 0


def test_invalid_inputs_raise():
    with pytest.raises(ValueError):
        dp.tail_term(0.0, 350.0, 1.44)
    with pytest.raises(ValueError):
        dp.aggregation_term(-0.5)
    with pytest.raises(ValueError):
        dp.max_scratch_depth_m(350.0, 0.31e9, 0.0)


def test_cross_pack_comparison_is_explicitly_forbidden():
    r = dp.evaluate(d99_nm=350.0, d99_ref_nm=350.0, exponent=1.44)
    assert any("NOT be compared across packs" in n for n in r.notes)


def test_risk_index_is_never_multiplied_into_the_rate():
    """Guard the contract: Delta is diagnostic only."""
    from cmp_sim.core.solver import simulate
    from cmp_sim.core.state import Abrasive, Recipe, Slurry, Tool, Wafer
    a = simulate(Recipe(model="full", wafer=Wafer(film="cu", n_radial=21),
                        slurry=Slurry(pack="cu_h2o2_bta"),
                        tool=Tool(pressure_psi=3.0, rpm_platen=60, rpm_head=60)))
    b = simulate(Recipe(model="full", wafer=Wafer(film="cu", n_radial=21),
                        slurry=Slurry(pack="cu_h2o2_bta",
                                      abrasive=Abrasive(kind="silica", d99_nm=900.0)),
                        tool=Tool(pressure_psi=3.0, rpm_platen=60, rpm_head=60)))
    assert b.mean_rr_nm_per_min == pytest.approx(a.mean_rr_nm_per_min, rel=1e-9)
