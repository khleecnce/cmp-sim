"""A step height of zero must not read as a perfect result.

Once the step clears, the wafer is planar and every further second is
overpolish — which is precisely when dishing and erosion accrue. Reporting only
"step height 0.0 nm" hides that: it looks like the recipe landed perfectly
rather than that it planarised long ago and kept going.

The initial step height is also an application choice, not a material constant:
poly-Si spans 190 nm (logic/STI) to >=5 um (MEMS), a 25x range, and
planarisation time is linear in it. A pack can carry only one value, so the
assumption has to be stated where the user sees it.
"""
import pytest

from cmp_sim.core.solver import simulate
from cmp_sim.core.state import Disk, Pad, Recipe, Slurry, Tool, Wafer


def _run(time_s=60.0, density=0.5, step_m=None):
    params = {"initial_step_height_m": step_m} if step_m else {}
    return simulate(Recipe(
        model="auto",
        wafer=Wafer(film="poly_si", n_radial=11, pattern_density=density),
        slurry=Slurry(pack="poly_si_alkaline"),
        pad=Pad(groove_width_mm=0.5, groove_pitch_mm=2.0, groove_depth_mm=0.75),
        disk=Disk(),
        tool=Tool(pressure_psi=3.0, rpm_platen=60.0, rpm_head=60.0, time_s=time_s),
        params=params))


def test_the_step_actually_decreases_with_time():
    early = _run(time_s=10.0).extras["pattern_effects"]["step_height_nm"]["max"]
    later = _run(time_s=30.0).extras["pattern_effects"]["step_height_nm"]["max"]
    assert early > later > 0.0


def test_the_clearing_time_is_reported():
    notes = " ".join(_run(time_s=10.0).notes)
    assert "the step clears at t =" in notes


def test_overpolishing_is_warned_about_with_its_share_of_the_recipe():
    r = _run(time_s=120.0)
    assert r.extras["pattern_effects"]["step_height_nm"]["max"] == 0.0
    joined = " ".join(r.warnings)
    assert "overpolish on a flat surface" in joined
    assert "not 'just right'" in joined, (
        "a zero step height is reported without explaining what it means")


def test_a_recipe_that_stops_at_the_step_is_not_warned_about():
    """The warning must discriminate, or it is noise."""
    assert not any("overpolish on a flat surface" in w
                   for w in _run(time_s=10.0).warnings)


def test_the_assumed_application_scale_is_stated():
    """190 nm is logic/STI; MEMS is >=5 um and would clear 25x later."""
    notes = " ".join(_run(time_s=10.0).notes)
    assert "assumed application scale" in notes
    assert "not a property of the film" in notes


def test_a_thicker_layer_takes_proportionally_longer_to_clear():
    """Planarisation time is linear in the initial step, which is why the
    MEMS-versus-logic distinction matters."""
    thin = _run(time_s=40.0)                       # 190 nm pack default
    thick = _run(time_s=40.0, step_m=5.0e-6)       # MEMS scale
    assert thin.extras["pattern_effects"]["step_height_nm"]["max"] == 0.0
    assert thick.extras["pattern_effects"]["step_height_nm"]["max"] > 0.0
    assert not any("overpolish on a flat surface" in w for w in thick.warnings)


def test_denser_patterns_clear_later():
    """RR_up = blanket / rho_eff, so the dense region is the last to clear."""
    sparse = _run(time_s=20.0, density=0.25).extras["pattern_effects"]
    dense = _run(time_s=20.0, density=0.75).extras["pattern_effects"]
    assert dense["step_height_nm"]["max"] > sparse["step_height_nm"]["max"]
