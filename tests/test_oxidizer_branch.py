"""The oxidizer term must not contradict its own pack in silence.

Copper in H2O2 is the textbook non-monotonic system: the rate rises, peaks
around 1-3 wt% and falls as passivation thickens (Aksu & Doyle 2003). The Cu
pack declares that peak.

It also declares a Langmuir passivation constant, and the Langmuir branch takes
precedence, so the modelled oxidizer term falls monotonically from zero. That
choice is defensible — below the peak the Kaufman curve's shape exponent and
peak position are degenerate, while Langmuir has one identifiable parameter —
but a user scanning concentration would otherwise see a monotonic curve and
read it as the model's opinion about a system famous for having a maximum.
"""
import pytest

from cmp_sim.core.solver import simulate
from cmp_sim.core.state import (Additive, Disk, Pad, Recipe, Slurry, Tool,
                                Wafer)


def _run(oxidizer_wt_pct):
    return simulate(Recipe(
        model="auto",
        wafer=Wafer(film="cu", n_radial=11),
        slurry=Slurry(pack="cu_h2o2_bta", additives=[
            Additive(name="hydrogen_peroxide", conc_wt_pct=oxidizer_wt_pct)]),
        pad=Pad(groove_width_mm=0.5, groove_pitch_mm=2.0, groove_depth_mm=0.75),
        disk=Disk(),
        tool=Tool(pressure_psi=2.0, rpm_platen=60.0, rpm_head=60.0, time_s=60.0)))


def test_the_oxidizer_term_actually_responds_to_concentration():
    """The failure this guards against is a factor stuck at 1.0."""
    low = _run(1.0).factors["psi_chemistry"]
    high = _run(6.0).factors["psi_chemistry"]
    assert low != pytest.approx(high)


def test_the_reference_composition_gives_exactly_one():
    """Kp was back-calculated at 3 wt%, so the multiplier must be 1.0 there or
    the chemistry is counted twice."""
    assert _run(3.0).factors["psi_chemistry"] == pytest.approx(1.0, rel=1e-6)


def test_the_modelled_branch_is_monotonic():
    values = [_run(c).factors["psi_chemistry"] for c in (1.0, 2.0, 3.0, 4.0, 6.0)]
    assert values == sorted(values, reverse=True), values


def test_the_disagreement_with_the_declared_peak_is_disclosed():
    """Silence here would let a monotonic curve pass as a finding."""
    warnings = " ".join(_run(3.0).warnings)
    assert "peak at 3 wt%" in warnings
    assert "monotonic" in warnings
    assert "identifiable" in warnings, (
        "the warning does not say why the Langmuir branch was preferred")


def test_running_below_the_peak_is_flagged_specifically():
    """Below the peak the real system rises while this model falls, so even the
    ranking is wrong there — that is worth its own warning."""
    below = " ".join(_run(1.0).warnings)
    above = " ".join(_run(6.0).warnings)
    assert "sits below the declared peak" in below
    assert "RISE with concentration" in below
    assert "sits below the declared peak" not in above


def test_an_inhibitor_suppresses_the_rate():
    """BTA is the other half of the copper chemistry and must bite."""
    without = _run(3.0).mean_rr_angstrom_per_min
    with_bta = simulate(Recipe(
        model="auto",
        wafer=Wafer(film="cu", n_radial=11),
        slurry=Slurry(pack="cu_h2o2_bta", additives=[
            Additive(name="hydrogen_peroxide", conc_wt_pct=3.0),
            Additive(name="benzotriazole", conc_mM=10.0)]),
        pad=Pad(groove_width_mm=0.5, groove_pitch_mm=2.0, groove_depth_mm=0.75),
        disk=Disk(),
        tool=Tool(pressure_psi=2.0, rpm_platen=60.0, rpm_head=60.0,
                  time_s=60.0))).mean_rr_angstrom_per_min
    assert with_bta < without
