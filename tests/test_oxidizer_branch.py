"""The oxidizer term must agree with its own pack.

Copper in H2O2 is the textbook non-monotonic system: the rate rises, peaks
around 1-3 wt% and falls as passivation thickens. The Cu pack has always
declared that peak.

For a long time the model contradicted it. A Langmuir passivation constant took
precedence and the oxidizer term fell monotonically from zero, so a
concentration scan showed no maximum at all. That was defensible on
identifiability grounds — a peaked curve with both the peak position and the
shape free cannot be fitted from data on one side of the maximum — and these
tests pinned the contradiction in place, along with the warnings that disclosed
it.

That limitation is now resolved rather than merely disclosed. Pinning the peak
to a MEASURED position makes the decay scale a consequence of it, leaving one
free parameter, which Du 2004 supplies with six points spanning the peak
(doi:10.1149/1.1648029, verified against the original PDF). The tests below
therefore assert the opposite of what they once did; the form itself is
validated in tests/test_peaked_oxidizer.py.
"""
import pytest

from cmp_sim.core.solver import simulate
from cmp_sim.core.state import (Additive, Disk, Pad, Recipe, Slurry, Tool,
                                Wafer)


def _recipe(oxidizer_wt_pct):
    return Recipe(
        model="auto",
        wafer=Wafer(film="cu", n_radial=11),
        slurry=Slurry(pack="cu_h2o2_bta", additives=[
            Additive(name="hydrogen_peroxide", conc_wt_pct=oxidizer_wt_pct)]),
        pad=Pad(groove_width_mm=0.5, groove_pitch_mm=2.0, groove_depth_mm=0.75),
        disk=Disk(),
        tool=Tool(pressure_psi=2.0, rpm_platen=60.0, rpm_head=60.0, time_s=60.0))


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


def test_the_modelled_branch_now_peaks_instead_of_falling_monotonically():
    """RESOLVED LIMITATION. These three tests used to pin the OPPOSITE: that the
    term fell monotonically, contradicting the peak the pack declares, and that
    the contradiction was at least disclosed.

    The obstacle was identifiability rather than physics — a peaked curve with
    both the peak position and the shape free cannot be fitted from one side of
    the maximum. Taking the peak position from a measurement and deriving the
    decay scale from it leaves one free parameter, which Du 2004 supplies
    (doi:10.1149/1.1648029, six points across the peak, verified against the
    original PDF). See tests/test_peaked_oxidizer.py.
    """
    concs = (0.5, 1.0, 2.0, 3.0, 4.0, 6.0, 10.0)
    values = [_run(c).factors["psi_chemistry"] for c in concs]
    peak_index = values.index(max(values))
    assert 0 < peak_index < len(values) - 1, (
        f"no interior maximum in {[round(v, 4) for v in values]}")
    rising = values[:peak_index + 1]
    falling = values[peak_index:]
    assert rising == sorted(rising), f"the rising limb is not monotonic: {rising}"
    assert falling == sorted(falling, reverse=True), (
        f"the falling limb is not monotonic: {falling}")


def test_the_peak_sits_where_the_pack_says_it_does():
    """The peak position is a measured input, so the model must honour it
    exactly rather than drifting to wherever the fit prefers."""
    from cmp_sim.core.solver import resolve

    declared = float(resolve(_recipe(3.0)).p_or("oxidizer_peak_wt_pct", 0))
    grid = [c / 4.0 for c in range(1, 81)]
    values = [(c, _run(c).factors["psi_chemistry"]) for c in grid]
    best = max(values, key=lambda cv: cv[1])[0]
    assert best == pytest.approx(declared, abs=0.3), (
        f"peak modelled at {best} wt% but the pack declares {declared} wt%")


def test_the_replacement_of_the_inherited_term_is_stated():
    """Double-counting the same surface chemistry once collapsed a copper rate
    by 20x here, so the swap must be visible in the notes."""
    notes = " ".join(_run(3.0).notes)
    assert "replaced the inherited" in notes
    assert "double-count" in notes


def test_the_borrowed_curvature_is_disclosed_as_borrowed():
    """K came from a glycine-free, vol%-axis paper while this pack is a
    wt%-axis glycine slurry. That transfer must not read as calibrated."""
    from cmp_sim.core.solver import resolve

    pack = resolve(_recipe(3.0)).pack
    param = pack.param("oxidizer_peak_shape_K")
    assert param.confidence == "low", (
        f"borrowed curvature is marked '{param.confidence}', not low")
    note = (param.note or "") + (param.source or "")
    assert "VOL%" in note.upper(), "the unit mismatch is not recorded"
    assert "glycine" in note.lower(), "the chemistry difference is not recorded"


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
