"""P3 unit tests — abrasive mechanics: single-particle law and exponents."""
import math

import pytest

from cmp_sim.models import luo_dornfeld as ld


# ── single-particle mechanics ────────────────────────────────────────
def test_indentation_depth_matches_the_closed_form():
    """delta = F / (2 pi R H)."""
    F, R, H = 1.0e-7, 35.0e-9, 7.0e9
    assert ld.indentation_depth_m(F, R, H) == pytest.approx(
        F / (2.0 * math.pi * R * H), rel=1e-12)


def test_indentation_is_inversely_proportional_to_hardness():
    """A chemically softened surface indents deeper — the chemistry channel."""
    a = ld.indentation_depth_m(1e-7, 35e-9, 7.0e9)
    b = ld.indentation_depth_m(1e-7, 35e-9, 3.5e9)
    assert b == pytest.approx(2.0 * a, rel=1e-12)


def test_smaller_particle_indents_deeper_at_equal_load():
    """beta = -1: at fixed load per particle a smaller sphere cuts deeper.
    The opposite folk claim comes from the particle-count term."""
    small = ld.indentation_depth_m(1e-7, 20e-9, 7e9)
    big = ld.indentation_depth_m(1e-7, 80e-9, 7e9)
    assert small > big
    assert small / big == pytest.approx(4.0, rel=1e-12)


def test_indentation_depth_is_a_small_fraction_of_the_particle():
    """Sanity: at CMP loads the indent must be nanometre-scale and much smaller
    than the particle, otherwise the shallow-indent geometry is invalid."""
    R = 35e-9
    delta = ld.indentation_depth_m(1e-7, R, 7e9)
    assert 1e-12 < delta < 0.1 * R


def test_single_particle_removal_scales_as_F_1p5_over_H_1p5():
    """Q1 ~ a*delta ~ F^1.5 R^-1 H^-1.5."""
    base = ld.single_particle_removal_rate(1e-7, 35e-9, 7e9)
    heavier = ld.single_particle_removal_rate(2e-7, 35e-9, 7e9)
    softer = ld.single_particle_removal_rate(1e-7, 35e-9, 3.5e9)
    assert heavier / base == pytest.approx(2.0 ** 1.5, rel=1e-9)
    assert softer / base == pytest.approx(2.0 ** 1.5, rel=1e-9)


def test_invalid_inputs_raise():
    with pytest.raises(ValueError):
        ld.indentation_depth_m(1e-7, 0.0, 7e9)
    with pytest.raises(ValueError):
        ld.contact_radius_m(1e-7, 0.0)
    with pytest.raises(ValueError):
        ld.particles_per_unit_area(0.1, 0.0)


def test_particle_count_and_load_sharing_are_consistent():
    """More, smaller particles share the same load, so each carries less."""
    n_small = ld.particles_per_unit_area(0.05, 30e-9)
    n_big = ld.particles_per_unit_area(0.05, 120e-9)
    assert n_small > n_big
    assert (ld.load_per_particle_n(20.7e3, n_small)
            < ld.load_per_particle_n(20.7e3, n_big))


# ── exponent decomposition ───────────────────────────────────────────
def test_elastic_full_sharing_gives_the_one_third_law():
    """n_C = p(1-alpha*chi) = 1*(1-2/3) = 1/3. Usually called
    'surface-area-limited', but it is really elastic contact with full load
    sharing — the naming has misled the field."""
    reg = ld.resolve_regime(area_pressure_exponent=1.0,
                            contact_stress_pa=1.0e8, surface_hardness_pa=7.0e9,
                            gap_m=70e-9, particle_diameter_m=70e-9)
    assert reg.chi == pytest.approx(1.0, abs=1e-6)
    assert reg.alpha == pytest.approx(ld.ALPHA_ELASTIC, rel=1e-6)
    assert reg.n_conc == pytest.approx(1.0 / 3.0, abs=1e-6)


def test_concentration_exponent_never_exceeds_one():
    """Structural bound: p <= 1 and 0 <= (1-alpha*chi) <= 1, so n_C <= 1.
    A quoted exponent of 4/3 cannot come from this decomposition."""
    for stress in (1e7, 1e8, 1e9, 5e9, 2e10):
        for ape in (0.0, 0.5, 1.0):
            reg = ld.resolve_regime(area_pressure_exponent=ape,
                                    contact_stress_pa=stress,
                                    surface_hardness_pa=7.0e9,
                                    gap_m=70e-9, particle_diameter_m=70e-9)
            assert reg.n_conc <= 1.0 + 1e-9, (stress, ape, reg.n_conc)


def test_beta_is_paired_with_alpha_not_chosen_freely():
    """alpha and beta come from the same contact law."""
    assert ld.beta_for_alpha(ld.ALPHA_PLASTIC) == pytest.approx(-1.0)
    assert ld.beta_for_alpha(ld.ALPHA_ELASTIC) == pytest.approx(2.0 / 3.0)
    mid = ld.beta_for_alpha(0.5 * (ld.ALPHA_PLASTIC + ld.ALPHA_ELASTIC))
    assert -1.0 < mid < 2.0 / 3.0


def test_transition_band_is_declared_not_hidden():
    reg = ld.resolve_regime(area_pressure_exponent=1.0,
                            contact_stress_pa=5.0e9, surface_hardness_pa=7.0e9,
                            gap_m=70e-9, particle_diameter_m=70e-9)
    assert any("transition" in n for n in reg.notes)


def test_missing_inputs_lower_the_confidence_and_say_why():
    reg = ld.resolve_regime()
    assert reg.confidence in ("unverified", "estimated")
    assert any("undetermined" in n or "not decided" in n for n in reg.notes)


def test_notes_are_english_so_they_survive_into_json_output():
    reg = ld.resolve_regime(area_pressure_exponent=1.0, contact_stress_pa=1e8,
                            surface_hardness_pa=7e9, gap_m=70e-9,
                            particle_diameter_m=70e-9)
    joined = " ".join(reg.notes)
    assert joined.isascii(), joined


# ── saturation ───────────────────────────────────────────────────────
def test_apparent_exponent_slides_from_one_to_zero():
    """Same physics, different measurement window: the apparent concentration
    exponent is 1 when dilute and 0 when saturated. This is why quoting a
    single exponent without stating the concentration is meaningless."""
    assert ld.apparent_conc_exponent(0.01, 10.0) == pytest.approx(1.0, abs=1e-3)
    assert ld.apparent_conc_exponent(200.0, 10.0) < 1e-3


def test_occupancy_ratio_saturates_instead_of_growing_forever():
    """Doubling the abrasive well past C_half must not double the rate."""
    r1 = ld.occupancy_ratio(20.0, 10.0, 2.0)
    r2 = ld.occupancy_ratio(40.0, 10.0, 2.0)
    assert r1 == pytest.approx(r2, rel=1e-3)
    # the reference itself sits at 5*C_half, i.e. already 99.3% occupied, so the
    # saturated ratio is 1/0.9933 = 1.0067 rather than exactly 1
    assert r1 == pytest.approx(1.0, rel=1e-2)
    # doubling the abrasive changes the rate by well under 1%
    assert abs(r2 / r1 - 1.0) < 1e-3


def test_occupancy_is_one_at_the_reference_concentration():
    assert ld.occupancy_ratio(8.0, 8.0, 3.0) == pytest.approx(1.0, rel=1e-12)


def test_unknown_saturation_returns_none_rather_than_a_guess():
    assert ld.occupancy_ratio(5.0, 10.0, None) is None
    assert ld.apparent_conc_exponent(5.0, None) is None


# ── the Kp multiplier ────────────────────────────────────────────────
@pytest.fixture
def regime():
    return ld.resolve_regime(area_pressure_exponent=1.0, contact_stress_pa=1e8,
                             surface_hardness_pa=7e9, gap_m=70e-9,
                             particle_diameter_m=70e-9)


def test_factor_is_unity_at_the_reference_slurry(regime):
    f, notes, _w = ld.mechanical_factor(
        conc=12.0, conc_ref=12.0, diameter_nm=70.0, diameter_ref_nm=70.0,
        regime=regime, conc_half=8.0)
    assert f == pytest.approx(1.0, rel=1e-9)


def test_lower_concentration_lowers_the_factor(regime):
    f, _n, _w = ld.mechanical_factor(conc=3.0, conc_ref=12.0, diameter_nm=None,
                                     diameter_ref_nm=None, regime=regime,
                                     conc_half=8.0)
    assert f < 1.0


def test_deep_saturation_is_warned(regime):
    _f, _n, warns = ld.mechanical_factor(conc=200.0, conc_ref=12.0,
                                         diameter_nm=None, diameter_ref_nm=None,
                                         regime=regime, conc_half=2.0)
    assert any("saturation" in w for w in warns)


def test_missing_c_half_falls_back_to_a_power_law_with_a_warning(regime):
    f, _n, warns = ld.mechanical_factor(conc=24.0, conc_ref=12.0, diameter_nm=None,
                                        diameter_ref_nm=None, regime=regime,
                                        conc_half=None)
    assert f == pytest.approx(2.0 ** regime.n_conc, rel=1e-9)
    assert any("power law" in w for w in warns)


def test_softened_surface_raises_the_rate_by_H_to_the_minus_1p5(regime):
    f, notes, _w = ld.mechanical_factor(
        conc=None, conc_ref=None, diameter_nm=None, diameter_ref_nm=None,
        regime=regime, hardness_pa=3.5e9, hardness_ref_pa=7.0e9)
    assert f == pytest.approx(2.0 ** 1.5, rel=1e-9)
    assert any("H^-1.5" in n for n in notes)


# ── the two concentration branches must describe the SAME physics ────
def test_the_saturating_branch_carries_the_same_load_sharing_as_the_power_law(regime):
    """The two concentration branches differ only by how N(C) is modelled.

    `occupancy_ratio` is a ratio of active particle COUNTS. The rate follows
    MRR ~ N^(1 - alpha*chi), which is exactly what makes the power-law branch's
    exponent n_C = p * (1 - alpha*chi). Applying the count ratio directly
    asserts (1 - alpha*chi) = 1, i.e. chi = 0 — no load sharing at all — while
    the same call has resolved chi = 1. That is not a different saturation
    model, it is a different contact regime smuggled in on one branch.

    The check is structural: in the DILUTE limit (C, C_ref << C_half) the
    occupancy model reduces to N ~ C, so the saturating branch must return
    exactly what the power law returns for p = 1. Before the fix it returned
    the count ratio itself — steeper by 1/(1 - alpha*chi) = 3x in the exponent.
    """
    kw = dict(conc=0.02, conc_ref=0.01, diameter_nm=None,
              diameter_ref_nm=None, regime=regime)
    saturating, _n, _w = ld.mechanical_factor(conc_half=50.0, **kw)   # C << C_half
    power_law, _n2, _w2 = ld.mechanical_factor(conc_half=None, **kw)
    assert regime.p == pytest.approx(1.0)      # dilute reduction is only valid here
    assert saturating == pytest.approx(power_law, rel=1e-3)
    # and the bug it replaces: the bare count ratio is a strictly larger claim
    assert saturating < 2.0 ** 1.0


def test_the_saturating_branch_still_saturates_after_the_correction(regime):
    """Raising to a positive power cannot remove the saturation.

    Guards the obvious over-correction: an exponent that made the branch flat
    would pass the test above (both branches would be 1.0) while deleting the
    physics C_half exists for.
    """
    kw = dict(conc_ref=1.0, diameter_nm=None, diameter_ref_nm=None,
              regime=regime, conc_half=2.0)
    f10, _n, _w = ld.mechanical_factor(conc=10.0, **kw)
    f20, _n2, _w2 = ld.mechanical_factor(conc=20.0, **kw)
    assert f20 > f10 > 1.0                       # still rising
    assert f20 / f10 < 1.05                      # but has stopped responding
    assert f20 < 10.0 ** regime.n_conc * 3.0     # below the unsaturated power law
