"""Owner-supplied parameters: the way past a gap in the literature.

Several packs honestly declare a value null because nobody has published it.
The error that results tells the user to supply their own — so that has to be
possible, and the supplied number must be clearly marked as theirs rather than
silently joining the sourced values.
"""
import pytest

from cmp_sim.core.params import ParamMissing
from cmp_sim.core.solver import simulate
from cmp_sim.core.state import Disk, Pad, Recipe, Slurry, Tool, Wafer


def _snag(params=None):
    return Recipe(
        model="auto",
        wafer=Wafer(film="snag", n_radial=11),
        slurry=Slurry(pack="snag_solder"),
        pad=Pad(groove_width_mm=0.5, groove_pitch_mm=2.0, groove_depth_mm=0.75),
        disk=Disk(),
        tool=Tool(pressure_psi=1.5, rpm_platen=60.0, rpm_head=60.0, time_s=60.0),
        params=params or {})


def test_without_an_owner_value_the_run_refuses():
    with pytest.raises(ParamMissing):
        simulate(_snag())


def test_the_advice_in_that_error_actually_works():
    """The message says to supply a Kp; supplying one must make it run."""
    r = simulate(_snag({"kp_m_per_pa": 2.0e-13}))
    assert r.mean_rr_angstrom_per_min > 0.0


def test_an_owner_value_is_marked_as_owner_provided():
    """It must never be mistaken for a sourced literature value."""
    r = simulate(_snag({"kp_m_per_pa": 2.0e-13}))
    assert any("owner-supplied" in n for n in r.notes)
    prov = r.provenance
    entry = prov.get("kp_m_per_pa")
    assert entry is not None
    assert "owner" in str(entry).lower()


def test_an_owner_value_beats_the_pack():
    """Two different Kp values must give two different, proportional rates."""
    a = simulate(_snag({"kp_m_per_pa": 1.0e-13})).mean_rr_angstrom_per_min
    b = simulate(_snag({"kp_m_per_pa": 2.0e-13})).mean_rr_angstrom_per_min
    assert b == pytest.approx(2.0 * a, rel=1e-6)


def test_overriding_a_key_the_pack_never_declared_is_reported():
    """Otherwise a typo looks like it worked."""
    r = simulate(_snag({"kp_m_per_pa": 2.0e-13, "not_a_real_parameter": 1.0}))
    assert any("not_a_real_parameter" in w for w in r.warnings)


def test_a_film_with_a_pack_still_works_unchanged():
    r = simulate(Recipe(
        model="auto", wafer=Wafer(film="oxide", n_radial=11),
        slurry=Slurry(pack="oxide_silica"),
        pad=Pad(groove_width_mm=0.5, groove_pitch_mm=2.0, groove_depth_mm=0.75),
        disk=Disk(),
        tool=Tool(pressure_psi=3.0, rpm_platen=60.0, rpm_head=60.0, time_s=60.0)))
    assert not any("owner-supplied" in n for n in r.notes)


def test_params_can_be_given_in_a_yaml_config():
    from cmp_sim.cli import recipe_from_dict

    r = recipe_from_dict({"wafer": {"film": "snag"},
                          "params": {"kp_m_per_pa": 2.0e-13}})
    assert r.params["kp_m_per_pa"] == 2.0e-13
