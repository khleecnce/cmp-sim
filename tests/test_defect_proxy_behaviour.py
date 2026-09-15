"""P8 defect proxy, exercised through the solver.

The unit tests cover the formula; these pin the behaviour a slurry engineer
would actually rely on — that the large-particle tail drives the risk, that
crossing the published scratch threshold is announced, and that the index is
never presented as an absolute defect count.
"""
import pytest

from cmp_sim.core.solver import simulate
from cmp_sim.core.state import (Abrasive, Disk, Pad, Recipe, Slurry, Tool,
                                Wafer)

#: Remsen 2006 / Kwon 2023 / Eusner 2009, as carried in the packs.
SCRATCH_THRESHOLD_NM = 680.0


def _risk(d99_nm=None, film="w", pack="w_fe_oxidizer"):
    abrasive = Abrasive(d99_nm=d99_nm) if d99_nm else Abrasive()
    r = simulate(Recipe(
        model="auto",
        wafer=Wafer(film=film, n_radial=11),
        slurry=Slurry(pack=pack, abrasive=abrasive),
        pad=Pad(groove_width_mm=0.5, groove_pitch_mm=2.0, groove_depth_mm=0.75),
        disk=Disk(),
        tool=Tool(pressure_psi=3.0, rpm_platen=60.0, rpm_head=60.0, time_s=60.0)))
    return r.extras["defect_risk"]


def test_risk_rises_steeply_with_the_large_particle_tail():
    """The tail is raised to a damage exponent, so this is super-linear."""
    small = _risk(250)["delta_risk_index"]
    large = _risk(1000)["delta_risk_index"]
    assert large > 4.0 * small, (
        "quadrupling the tail barely moved the risk; the exponent is not applied")


def test_the_reference_slurry_scores_exactly_one():
    """The index is relative, so the pack's own reference must be 1.0."""
    assert _risk()["delta_risk_index"] == pytest.approx(1.0, rel=1e-6)


def test_crossing_the_published_scratch_threshold_is_announced():
    below = _risk(400)
    above = _risk(1000)
    assert not any("exceeds" in w for w in below["warnings"])
    assert any("exceeds" in w and "scratch threshold" in w
               for w in above["warnings"])


def test_sitting_near_the_threshold_is_flagged_as_least_reliable():
    """The log-normal tail's local slope changes fastest there, so a constant
    damage exponent is weakest exactly at the interesting point."""
    near = _risk(int(SCRATCH_THRESHOLD_NM * 0.9))
    assert any("slope changes fastest" in w or "least reliable" in w
               for w in near["warnings"])


def test_scratch_dimensions_are_reported_not_just_an_index():
    """A number with no units cannot be acted on; width and depth can."""
    d = _risk(800)
    assert d["max_scratch_width_nm"] > 0
    assert d["max_scratch_depth_nm"] > 0
    assert d["max_scratch_width_nm"] > d["max_scratch_depth_nm"], (
        "a scratch should be wider than it is deep")


def test_the_same_tail_damages_a_soft_film_more_than_a_hard_one():
    """Severity is set by film hardness: copper is far softer than tungsten."""
    cu = _risk(500, film="cu", pack="cu_h2o2_bta")
    w = _risk(500, film="w", pack="w_fe_oxidizer")
    assert cu["max_scratch_depth_nm"] > w["max_scratch_depth_nm"]


def test_the_index_refuses_to_be_read_as_an_absolute_count():
    assert any("does not predict absolute scratch counts" in n
               for n in _risk()["notes"])


def test_an_uninvestigated_path_is_distinguished_from_no_effect():
    """Silence about aggregation would read as 'aggregation does not matter'."""
    assert any("not investigated" in n and "not the same as no effect" in n
               for n in _risk()["notes"])
