"""Bad input must fail in a way the user can act on.

Before this existed, a negative pressure surfaced as
``RuntimeError: 브라켓 실패: f(d_lo)=8.424e+01`` — an inherited message, in
Korean, about a numerical bracket. It told the user nothing about what they
typed. Two separate obligations are tested here:

* input that cannot describe a real process is REJECTED, naming the field;
* input that is possible but outside the fitted range RUNS, and says so.
"""
import pytest

from cmp_sim.core.solver import simulate
from cmp_sim.core.state import (Abrasive, Disk, Pad, Recipe, Slurry, Tool,
                                Wafer)
from cmp_sim.core.validate_input import RecipeInvalid


def _recipe(**tool):
    base = dict(pressure_psi=3.0, rpm_platen=60.0, rpm_head=60.0, time_s=60.0)
    base.update(tool)
    return Recipe(
        model="auto",
        wafer=Wafer(film="oxide", n_radial=11),
        slurry=Slurry(pack="oxide_silica"),
        pad=Pad(groove_width_mm=0.5, groove_pitch_mm=2.0, groove_depth_mm=0.75),
        disk=Disk(), tool=Tool(**base))


# ── rejected ─────────────────────────────────────────────────────────
@pytest.mark.parametrize("field,value,needle", [
    ("pressure_psi", -3.0, "pressure"),
    ("pressure_psi", 0.0, "pressure"),
    ("time_s", -10.0, "polish time"),
    ("rpm_platen", -60.0, "rpm_platen"),
    ("flow_ml_min", -5.0, "flow"),
])
def test_impossible_tool_settings_are_rejected_by_name(field, value, needle):
    with pytest.raises(RecipeInvalid) as exc:
        simulate(_recipe(**{field: value}))
    assert needle in str(exc.value)
    assert str(value) in str(exc.value), "the message omits the offending value"


@pytest.mark.parametrize("density", [1.5, -0.2, 0.0])
def test_pattern_density_must_be_a_fraction(density):
    r = _recipe()
    r.wafer.pattern_density = density
    with pytest.raises(RecipeInvalid, match="pattern density"):
        simulate(r)


def test_ph_outside_zero_to_fourteen_is_rejected():
    r = _recipe()
    r.slurry.ph = 20.0
    with pytest.raises(RecipeInvalid, match="pH"):
        simulate(r)


def test_d99_below_d50_is_rejected():
    """The 99th percentile cannot sit below the median."""
    r = _recipe()
    r.slurry.abrasive = Abrasive(d50_nm=80.0, d99_nm=40.0)
    with pytest.raises(RecipeInvalid, match="99th percentile"):
        simulate(r)


def test_the_error_lists_every_problem_at_once():
    """One round trip per fix is a poor experience."""
    r = _recipe(pressure_psi=-1.0, time_s=-1.0)
    with pytest.raises(RecipeInvalid) as exc:
        simulate(r)
    assert len(exc.value.errors) >= 2


# ── accepted, with a warning ─────────────────────────────────────────
def test_pressure_outside_the_fitted_range_runs_but_warns():
    r = simulate(_recipe(pressure_psi=0.2))
    assert r.mean_rr_angstrom_per_min > 0.0
    assert any("extrapolation" in w for w in r.warnings)


def test_a_stationary_platen_removes_nothing_and_says_so():
    """Preston is proportional to velocity, so zero speed must give zero rate.
    An earlier version reported 815 A/min here."""
    r = simulate(_recipe(rpm_platen=0.0, rpm_head=0.0))
    assert r.mean_rr_angstrom_per_min == 0.0
    assert any("stationary" in w for w in r.warnings)


def test_uniformity_is_undefined_rather_than_zero_when_nothing_is_removed():
    """Every metric is a percentage of the mean, so at zero rate they are 0/0.
    Reporting 0% would read as a perfectly uniform wafer."""
    r = simulate(_recipe(rpm_platen=0.0, rpm_head=0.0))
    assert r.wiwnu_percent is None
    assert r.summary()["wiwnu_percent"] is None
    assert "undefined_because" in r.extras["uniformity"]


def test_a_load_beyond_the_contact_model_explains_itself_in_english():
    """The inherited solver raises an untranslated bracket error."""
    from cmp_sim.models.contact_gw import ContactSolverOutOfRange

    with pytest.raises(ContactSolverOutOfRange) as exc:
        simulate(_recipe(pressure_psi=500.0))
    msg = str(exc.value)
    assert msg.isascii(), f"non-English error leaked to the user: {msg}"
    assert "500.0 psi" in msg
    assert "preston_baseline" in msg, "the message offers no way forward"


def test_a_pack_with_no_preston_coefficient_refuses_by_name():
    """A null Kp is how an unsourced value is honestly recorded, so it must not
    surface as "float() argument must be ... not 'NoneType'"."""
    from cmp_sim.core.params import ParamMissing

    r = _recipe()
    r.wafer.film = "snag"
    r.slurry.pack = None
    with pytest.raises(ParamMissing) as exc:
        simulate(r)
    msg = str(exc.value)
    assert "snag" in msg, "the message does not say which film"
    assert "kp_m_per_pa" in msg, "the message does not name the missing value"
    assert "not been sourced" in msg, (
        "the message does not distinguish unsourced from zero")
    assert "slurry.pack" in msg, "the message offers no way forward"


def test_low_flow_is_flagged_as_starvation():
    r = simulate(_recipe(flow_ml_min=5.0))
    assert any("starvation" in w or "supply" in w.lower() for w in r.warnings)


def test_a_valid_recipe_produces_no_input_warnings():
    r = simulate(_recipe())
    assert not any("extrapolation" in w for w in r.warnings)
