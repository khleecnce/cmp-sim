"""Unestablished films, and convergence on the owner's own tool.

Two behaviours are pinned here.

**A film nobody polishes must not be predicted from defaults.** SnAg has no
published Preston coefficient and the only primary CMP report eliminated both
slurry windows it tried, so the simulator refuses and asks for specific inputs.

**More measurements must bring the prediction closer to the truth**, and the
accuracy quoted must be cross-validated rather than in-sample — a one-parameter
fit passes exactly through a single point, so its in-sample error is 0% by
construction and says nothing.
"""
import pytest

from cmp_sim.core import calibration as calib
from cmp_sim.core.maturity import (EMERGING, ESTABLISHED, UNESTABLISHED,
                                   FilmNotEstablished)
from cmp_sim.core.solver import simulate
from cmp_sim.core.state import Disk, Pad, Recipe, Slurry, Tool, Wafer


def _recipe(film="oxide", pack="oxide_silica", psi=3.0, rpm=60.0,
            measurements=None, params=None, ph=None):
    return Recipe(
        model="preston",
        wafer=Wafer(film=film, n_radial=11),
        slurry=Slurry(pack=pack, ph=ph),
        pad=Pad(groove_width_mm=0.5, groove_pitch_mm=2.0, groove_depth_mm=0.75),
        disk=Disk(),
        tool=Tool(pressure_psi=psi, rpm_platen=rpm, rpm_head=rpm, time_s=60.0),
        params=params or {},
        measurements=measurements or [])


# ── grading ──────────────────────────────────────────────────────────
def test_a_backtested_film_is_established():
    r = simulate(_recipe())
    assert r.extras["cmp_maturity"]["grade"] == ESTABLISHED


def test_a_film_with_a_single_point_derived_kp_is_only_emerging():
    """Si substrate's Kp was back-calculated from one published run."""
    r = simulate(_recipe(film="si", pack="si_substrate_alkaline", psi=0.62))
    assert r.extras["cmp_maturity"]["grade"] == EMERGING
    assert any("single published operating point" in w for w in r.warnings)


def test_an_unestablished_film_refuses_and_says_what_it_needs():
    """Kp can now be estimated from hardness, so the outstanding requirement is
    the pH - which for this film cannot be defaulted, because the only primary
    report eliminated both windows it tried."""
    with pytest.raises(FilmNotEstablished) as exc:
        simulate(_recipe(film="snag", pack="snag_solder", psi=1.5))
    msg = str(exc.value)
    assert "not an established CMP target" in msg
    assert "slurry_ph" in msg
    for needle in ("why:", "measurements:"):
        assert needle in msg, f"the refusal does not explain {needle}"


def test_a_pack_may_lower_its_own_grade_but_not_raise_it():
    """Documented process failures are evidence; self-promotion is not."""
    from cmp_sim.core.maturity import assess
    from cmp_sim.core.params import load_pack

    pack = load_pack("oxide_silica")
    pack.params["cmp_maturity"] = type(pack.params["kp_m_per_pa"])(
        key="cmp_maturity", value="unestablished", unit="-",
        source="test", confidence="literature", note="")
    lowered = assess(pack, _recipe())
    assert lowered.grade == UNESTABLISHED

    pack.params["cmp_maturity"].value = "established"
    snag = load_pack("snag_solder")
    snag.params["cmp_maturity"].value = "established"
    m = assess(snag, _recipe(film="snag", pack="snag_solder"))
    assert m.grade == UNESTABLISHED, "a pack promoted itself above its evidence"
    assert any("declaration is ignored" in r for r in m.reasons)


def test_supplying_the_missing_inputs_unblocks_the_film():
    r = simulate(_recipe(
        film="snag", pack="snag_solder", psi=1.5, ph=6.5,
        measurements=[
            {"rate_A_per_min": 3200, "pressure_psi": 1.0, "rpm_platen": 60},
            {"rate_A_per_min": 6500, "pressure_psi": 2.0, "rpm_platen": 60},
        ]))
    assert r.mean_rr_angstrom_per_min > 0
    assert r.extras["cmp_maturity"]["grade"] == UNESTABLISHED
    assert r.extras["cmp_maturity"]["runnable"] is True


# ── convergence ──────────────────────────────────────────────────────
#: A pretend tool whose rate is ~1.6x the pack's, sampled across P and V.
TOOL = [
    {"rate_A_per_min": 2380, "pressure_psi": 2.0, "rpm_platen": 60},
    {"rate_A_per_min": 4690, "pressure_psi": 4.0, "rpm_platen": 60},
    {"rate_A_per_min": 3610, "pressure_psi": 3.0, "rpm_platen": 60},
    {"rate_A_per_min": 7120, "pressure_psi": 3.0, "rpm_platen": 120},
]
HELD_OUT_RATE = 4800.0          # measured at 4 psi / 60 rpm, never fitted


def _error_with(n):
    r = simulate(_recipe(psi=4.0, rpm=60.0, measurements=TOOL[:n]))
    return abs(r.mean_rr_angstrom_per_min - HELD_OUT_RATE) / HELD_OUT_RATE * 100.0


def test_measurements_move_the_prediction_towards_the_real_tool():
    uncalibrated = _error_with(0)
    calibrated = _error_with(1)
    assert uncalibrated > 40.0, "the test tool is not actually different"
    assert calibrated < 5.0, "one measurement did not fix the absolute scale"


def test_more_measurements_do_not_make_it_worse():
    errors = [_error_with(n) for n in (1, 2, 3, 4)]
    assert max(errors) < 5.0
    assert errors[-1] <= errors[0] + 1.0


def test_a_single_point_refuses_to_quote_an_accuracy():
    """Its in-sample error is 0% by construction, which would be a lie."""
    r = simulate(_recipe(measurements=TOOL[:1]))
    cal = r.extras["calibration"]
    assert cal["cross_validated_mape_percent"] is None
    assert cal["accuracy_to_quote"] is None
    assert any("means nothing" in w for w in r.warnings)


def test_the_quoted_accuracy_is_cross_validated_not_in_sample():
    r = simulate(_recipe(measurements=TOOL))
    cal = r.extras["calibration"]
    assert cal["cross_validated_mape_percent"] is not None
    assert "leave-one-out" in cal["accuracy_to_quote"]


def test_the_fitted_exponent_confirms_prestons_law_on_clean_data():
    cal = simulate(_recipe(measurements=TOOL)).extras["calibration"]
    assert 0.9 < cal["pv_exponent"] < 1.1


def test_data_that_contradict_preston_are_flagged_rather_than_fitted():
    """The published copper anomaly: rate falls as speed rises."""
    anomalous = [
        {"rate_A_per_min": 425, "pressure_psi": 1.5, "rpm_platen": 60},
        {"rate_A_per_min": 419, "pressure_psi": 1.5, "rpm_platen": 120},
        {"rate_A_per_min": 250, "pressure_psi": 1.5, "rpm_platen": 200},
    ]
    r = simulate(_recipe(measurements=anomalous))
    assert any("not the 1.0 Preston's law requires" in w for w in r.warnings)


def test_every_calibration_suggests_the_next_experiment():
    for n in (1, 2, 4):
        cal = simulate(_recipe(measurements=TOOL[:n])).extras["calibration"]
        assert cal["next_experiment"], f"no guidance after {n} point(s)"


def test_residuals_are_reported_per_measurement():
    cal = simulate(_recipe(measurements=TOOL)).extras["calibration"]
    assert len(cal["residuals"]) == len(TOOL)
    assert all("error_percent" in row for row in cal["residuals"])


# ── input hygiene ────────────────────────────────────────────────────
def test_a_rate_without_its_conditions_is_rejected():
    with pytest.raises(ValueError, match="pressure_psi"):
        calib.from_dicts([{"rate_A_per_min": 1000}])


def test_nm_per_min_is_accepted_and_converted():
    m = calib.from_dicts([{"rate_nm_per_min": 145, "pressure_psi": 3,
                           "rpm_platen": 60}])
    assert m[0].rate_a_per_min == pytest.approx(1450.0)


def test_an_explicit_kp_still_beats_a_fit():
    """The owner's stated number wins over the model's inference."""
    r = simulate(_recipe(measurements=TOOL, params={"kp_m_per_pa": 1.0e-13}))
    bare = simulate(_recipe(params={"kp_m_per_pa": 1.0e-13}))
    assert r.mean_rr_angstrom_per_min == pytest.approx(
        bare.mean_rr_angstrom_per_min, rel=1e-9)
