"""Estimating Kp from material properties when no CMP data exist.

The claim under test is not "this predicts the rate accurately" — it does not,
and says so. The claim is that the Archard/Preston identity Kp = k/H collapses
the scatter in Kp enough to be useful, and that the resulting estimate is
labelled as an estimate everywhere it surfaces.
"""
import math

import pytest

from cmp_sim.core.params import load_pack
from cmp_sim.core.solver import simulate
from cmp_sim.core.state import Disk, Pad, Recipe, Slurry, Tool, Wafer
from cmp_sim.models import first_principles as fp

#: The packs the correlation was built from: device CMP at 1-6 psi, published
#: Kp, literature hardness. The Si-substrate pack is deliberately NOT here - its
#: Kp comes from a 0.62 psi wafer-maker polisher, a different tool class.
CALIBRATION_FILMS = {
    "cu_h2o2_bta": 1.2e9,
    "w_fe_oxidizer": 12.0e9,
    "oxide_silica": 9.0e9,
    "poly_si_alkaline": 11.5e9,
    "sti_ceria": 9.0e9,
}
#: Excluded, with the hardness each would contribute.
EXCLUDED_FILMS = {
    "si_substrate_alkaline": 10.0e9,      # wafer-maker tool class
    "sic_ceria_h2o2": 26.0e9,             # chemically rate-limited
}


def _sd_log10(values):
    return math.sqrt(sum((math.log10(v) - sum(math.log10(x) for x in values)
                          / len(values)) ** 2 for v in values) / (len(values) - 1))


def test_dividing_by_hardness_helps_within_one_tool_class():
    """The justification for the module - and it is a modest effect, so the
    test asserts only what the five points actually support."""
    kps, ks = [], []
    for pack_name, hardness in CALIBRATION_FILMS.items():
        kp = load_pack(pack_name).params["kp_m_per_pa"].value
        kps.append(kp)
        ks.append(kp * hardness)
    assert _sd_log10(ks) < _sd_log10(kps), (
        f"dividing by hardness made the scatter worse "
        f"({_sd_log10(ks):.3f} vs {_sd_log10(kps):.3f} in log10): the Archard "
        "correlation does not hold even within one tool class")


def test_the_improvement_is_modest_and_the_module_says_so():
    """Guards against the correlation being oversold in the docs or warnings.

    Band lowered 1.5-2.5 -> 1.3-2.5 on 2026-09-26. sti_ceria's Kp was
    re-anchored from an unreproduced 2.2e-13 estimate to 1.09e-13 backed out of
    four measured datasets, and ceria had been the largest k outlier, so the
    spread necessarily shrank (1.8x -> 1.5x). That is bookkeeping, NOT new
    evidence for 1/H — removing an over-estimate cannot confirm a correlation.
    The upper bound is what actually guards against overselling and is unchanged.
    """
    ks = [load_pack(p).params["kp_m_per_pa"].value * h
          for p, h in CALIBRATION_FILMS.items()]
    assert 1.3 < 10 ** _sd_log10(ks) < 2.5, (
        "the spread moved; the advertised uncertainty factor needs revisiting")
    assert fp.WEAR_COEFFICIENT_SPREAD == pytest.approx(
        10 ** _sd_log10(ks), abs=0.2)


def test_mixing_tool_classes_destroys_the_correlation():
    """Why the wafer-maker point is excluded: with it, dividing by hardness is
    actively worse than not doing it at all."""
    films = dict(CALIBRATION_FILMS)
    films["si_substrate_alkaline"] = EXCLUDED_FILMS["si_substrate_alkaline"]
    kps = [load_pack(p).params["kp_m_per_pa"].value for p in films]
    ks = [load_pack(p).params["kp_m_per_pa"].value * h for p, h in films.items()]
    assert _sd_log10(ks) > _sd_log10(kps), (
        "the wafer-maker outlier no longer hurts; the exclusion may be stale")


def test_the_published_constant_matches_the_packs_it_came_from():
    ks = [load_pack(p).params["kp_m_per_pa"].value * h
          for p, h in CALIBRATION_FILMS.items()]
    geo = math.exp(sum(math.log(k) for k in ks) / len(ks))
    assert fp.WEAR_COEFFICIENT == pytest.approx(geo, rel=0.05), (
        "WEAR_COEFFICIENT has drifted from the packs it was derived from")


def test_chemically_limited_films_are_excluded_from_the_correlation():
    """SiC's k is ~20x below the rest because its removal is not mechanical.
    Including it would corrupt the constant."""
    sic_k = (load_pack("sic_ceria_h2o2").params["kp_m_per_pa"].value * 26.0e9)
    assert sic_k < fp.WEAR_COEFFICIENT / 10.0
    assert "sic" not in " ".join(CALIBRATION_FILMS)


def test_running_outside_the_calibrated_pressure_range_is_flagged():
    est = fp.estimate_kp("snag", 0.27e9, pressure_psi=0.5)
    assert any("tool classes" in w for w in est.warnings)
    assert not any("tool classes" in w
                   for w in fp.estimate_kp("snag", 0.27e9, pressure_psi=3.0).warnings)


def test_the_estimate_reproduces_a_known_film_within_its_stated_band():
    """Held-out sanity: estimating copper from its hardness alone should land
    inside the uncertainty band the module advertises."""
    est = fp.estimate_kp("cu", 1.2e9)
    actual = load_pack("cu_h2o2_bta").params["kp_m_per_pa"].value
    assert est.kp_low <= actual <= est.kp_high, (
        f"the true Kp {actual:.2e} falls outside the estimated band "
        f"{est.kp_low:.2e}-{est.kp_high:.2e}")


def test_a_softer_film_is_predicted_to_polish_faster():
    """The one trend the Archard form guarantees."""
    soft = fp.estimate_kp("snag", 0.27e9).kp_m_per_pa
    hard = fp.estimate_kp("w", 12.0e9).kp_m_per_pa
    assert soft > hard
    assert soft / hard == pytest.approx(12.0 / 0.27, rel=1e-6)


def test_an_estimate_is_never_presented_as_a_measurement():
    est = fp.estimate_kp("snag", 0.27e9)
    assert any("ESTIMATED" in w for w in est.warnings)
    assert any("factor" in w for w in est.warnings)
    assert est.kp_low is not None and est.kp_high is not None


def test_a_creeping_metal_is_flagged():
    """Sn is at ~0.6 of its melting point at room temperature, so Archard's
    fixed flow stress is the wrong picture and the estimate is a lower bound."""
    est = fp.estimate_kp("snag", 0.27e9, temp_c=25.0)
    assert any("creeps" in w for w in est.warnings)
    assert any("HIGHER than estimated" in w for w in est.warnings)


def test_a_refractory_metal_is_not_flagged_for_creep():
    assert not any("creeps" in w for w in fp.estimate_kp("w", 12.0e9).warnings)


def test_homologous_temperature_is_computed_correctly():
    assert fp.homologous_temperature("snag", 25.0) == pytest.approx(
        298.15 / 494.0, rel=1e-6)
    assert fp.homologous_temperature("unknown_metal") is None


def test_without_hardness_nothing_is_estimated():
    est = fp.estimate_kp("mystery", 0.0)
    assert not est.ok
    assert any("nothing can be estimated" in w for w in est.warnings)


# ── through the solver ───────────────────────────────────────────────
def _snag(ph=6.5, **kw):
    return simulate(Recipe(
        model="auto",
        wafer=Wafer(film="snag", n_radial=11),
        slurry=Slurry(pack="snag_solder", ph=ph),
        pad=Pad(groove_width_mm=0.5, groove_pitch_mm=2.0, groove_depth_mm=0.75),
        disk=Disk(),
        tool=Tool(pressure_psi=1.5, rpm_platen=60.0, rpm_head=60.0, time_s=60.0),
        **kw))


def test_a_film_with_no_published_kp_still_produces_a_number():
    r = _snag()
    assert r.mean_rr_angstrom_per_min > 0
    assert "kp_estimate" in r.extras


def test_the_solver_labels_that_number_as_estimated():
    r = _snag()
    assert any("ESTIMATED from hardness" in w for w in r.warnings)
    assert r.extras["kp_estimate"]["uncertainty_factor"] > 1.0


def test_trends_survive_even_though_the_magnitude_is_uncertain():
    """What the estimate is actually for: ranking, not quoting."""
    from cmp_sim.core.state import Tool as T

    base = _snag()
    higher = simulate(Recipe(
        model="auto",
        wafer=Wafer(film="snag", n_radial=11),
        slurry=Slurry(pack="snag_solder", ph=6.5),
        pad=Pad(groove_width_mm=0.5, groove_pitch_mm=2.0, groove_depth_mm=0.75),
        disk=Disk(),
        tool=T(pressure_psi=3.0, rpm_platen=60.0, rpm_head=60.0, time_s=60.0)))
    assert higher.mean_rr_angstrom_per_min == pytest.approx(
        2.0 * base.mean_rr_angstrom_per_min, rel=1e-6)


def test_a_measurement_overrides_the_estimate():
    """One real number retires the correlation entirely."""
    r = _snag(measurements=[
        {"rate_A_per_min": 4700, "pressure_psi": 1.5, "rpm_platen": 60}])
    assert r.mean_rr_angstrom_per_min == pytest.approx(4700.0, rel=0.02)
    assert "calibration" in r.extras


def test_an_explicit_kp_also_overrides_the_estimate():
    r = _snag(params={"kp_m_per_pa": 2.0e-13})
    assert "kp_estimate" not in r.extras
