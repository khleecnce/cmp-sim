"""Why a rotating CMP tool is uniform at all, tested rather than assumed.

Most examples report WIWNU near zero, which looks like a stub returning a
constant. It is not: it is the classical kinematic result. When the head and
platen turn at the same speed, every point on the wafer sweeps the same
relative speed regardless of where it sits, so a velocity-proportional removal
law predicts a flat profile. That is the reason production tools run head and
platen close together.

These tests pin the mechanism, so a future flat profile cannot be mistaken for
a stub, and a non-flat one cannot appear without a cause.
"""
import numpy as np
import pytest

from cmp_sim.core.solver import simulate
from cmp_sim.core.state import Disk, Pad, Recipe, Slurry, Tool, Wafer
from cmp_sim.models.uniformity import relative_speed_profile

#: Wafer centre to platen centre, the geometry of a real polisher.
OFFSET_M = 0.20
WAFER_R_M = 0.15


def _run(rpm_head=60.0, rpm_platen=60.0, zones=None, edges=None, n=41):
    return simulate(Recipe(
        model="preston",
        wafer=Wafer(film="oxide", n_radial=n),
        slurry=Slurry(pack="oxide_silica"),
        pad=Pad(groove_width_mm=0.5, groove_pitch_mm=2.0, groove_depth_mm=0.75),
        disk=Disk(),
        tool=Tool(pressure_psi=3.0, rpm_platen=rpm_platen, rpm_head=rpm_head,
                  time_s=60.0, zone_pressures_psi=zones, zone_edges_norm=edges)))


def test_equal_speeds_make_the_relative_velocity_uniform():
    """The kinematic identity behind a flat profile."""
    _r, v = relative_speed_profile(WAFER_R_M, OFFSET_M, 60.0, 60.0)
    assert v.std() / v.mean() < 1e-6, "equal speeds did not give a uniform sweep"
    assert v.mean() == pytest.approx(2 * np.pi * 60.0 / 60.0 * OFFSET_M, rel=1e-6)


def test_a_flat_profile_is_earned_not_hardcoded():
    """Breaking the speed match must break the uniformity."""
    matched = _run(rpm_head=60.0, rpm_platen=60.0)
    mismatched = _run(rpm_head=30.0, rpm_platen=60.0)
    assert matched.wiwnu_percent < 0.01
    assert mismatched.wiwnu_percent > matched.wiwnu_percent, (
        "a large head/platen speed mismatch produced no extra non-uniformity, "
        "which suggests the profile is not actually being computed")


def test_the_speed_mismatch_shows_up_in_the_velocity_field():
    _r, matched = relative_speed_profile(WAFER_R_M, OFFSET_M, 60.0, 60.0)
    _r, mismatched = relative_speed_profile(WAFER_R_M, OFFSET_M, 30.0, 60.0)
    assert mismatched.std() > matched.std()


def test_zone_pressures_break_uniformity_even_at_matched_speed():
    """The other lever a real tool has."""
    flat = _run()
    zoned = _run(zones=[2.0, 3.0, 4.5], edges=[0.0, 0.4, 0.75, 1.0])
    assert zoned.wiwnu_percent > flat.wiwnu_percent
    prof = np.asarray(zoned.mrr_nm_per_min)
    assert prof.max() > prof.min()


def test_the_profile_follows_the_zone_pressures_in_order():
    """An outer zone at higher pressure must polish the edge faster."""
    r = _run(zones=[2.0, 3.0, 4.5], edges=[0.0, 0.4, 0.75, 1.0])
    prof = np.asarray(r.mrr_nm_per_min)
    assert prof[-1] > prof[0], "the edge zone is at higher pressure but polishes slower"


def test_uniformity_is_reported_as_a_percentage_of_the_mean():
    r = _run(zones=[2.0, 4.0], edges=[0.0, 0.5, 1.0])
    prof = np.asarray(r.mrr_nm_per_min)
    expected = 100.0 * prof.std() / prof.mean()
    # area weighting makes this approximate, but it must be the same order.
    assert 0.3 * expected < r.wiwnu_percent < 3.0 * expected
