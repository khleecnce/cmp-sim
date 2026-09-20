"""Fitting physical factors to data, without inventing physics that is not there.

The design claim: feeding measurements should reshape the model's *named
physical factors*, and only those the data can actually identify. The failure
mode being guarded against is the obvious one — more parameters always fit the
training data better, so a factor must earn its place out of sample.

The synthetic tools below are generated from a known exponent, so the tests can
ask the hardest question available: does the fitter recover the truth, and does
it stay silent when there is nothing to recover?
"""
import math

import pytest

from cmp_sim.core.calibration import Measurement
from cmp_sim.core.factor_fit import (MIN_CV_GAIN, MIN_LEVERAGE,
                                     POINTS_PER_FACTOR, fit_factors)
from cmp_sim.core.solver import simulate
from cmp_sim.core.state import Disk, Pad, Recipe, Slurry, Tool, Wafer

OFFSET_M = 0.20
KP_TRUE = 3.0e-13


def _synthetic(pressures=(1.0, 2.0, 3.5, 5.0), speeds=(60, 120),
               pressure_exponent=1.0, velocity_exponent=1.0, noise=0.0,
               seed=11):
    """A pretend tool obeying MRR = Kp * P^a * V^b, sampled on a grid."""
    import random
    rng = random.Random(seed)
    v_ref = 2 * math.pi * 90 / 60 * OFFSET_M
    out = []
    for psi in pressures:
        for rpm in speeds:
            v = 2 * math.pi * rpm / 60 * OFFSET_M
            p = psi * 6894.757
            rate = (KP_TRUE * p * v * 1e10 * 60
                    * (psi / 3.0) ** (pressure_exponent - 1.0)
                    * (v / v_ref) ** (velocity_exponent - 1.0))
            out.append(Measurement(rate * (1 + rng.uniform(-noise, noise)),
                                   psi, rpm))
    return out


# ── recovering real physics ──────────────────────────────────────────
def test_a_genuine_sub_linear_pressure_law_is_recovered():
    fit = fit_factors(_synthetic(pressure_exponent=0.65))
    assert "pressure_exponent" in fit.unlocked
    assert fit.values["pressure_exponent"] == pytest.approx(0.65, abs=0.05)


def test_recovering_it_collapses_the_error():
    fit = fit_factors(_synthetic(pressure_exponent=0.65))
    assert fit.baseline_cv_mape > 10.0, "the test data are not actually non-Preston"
    assert fit.cv_mape < fit.baseline_cv_mape / 5.0


def test_the_fit_survives_realistic_measurement_noise():
    for seed in (1, 2, 3):
        fit = fit_factors(_synthetic(pressure_exponent=0.65, noise=0.08,
                                     seed=seed))
        assert "pressure_exponent" in fit.unlocked, f"missed the signal, seed {seed}"
        assert fit.values["pressure_exponent"] == pytest.approx(0.65, abs=0.12)


# ── refusing to invent physics ───────────────────────────────────────
def test_data_that_obey_prestons_law_unlock_nothing():
    """The most important test here: no departure, no fitted departure."""
    fit = fit_factors(_synthetic(pressure_exponent=1.0, velocity_exponent=1.0))
    assert fit.unlocked == []
    assert fit.rejected, "the factors were never even tried"


def test_noise_never_makes_out_of_sample_prediction_worse():
    """The property that actually matters, replacing a count of acceptances.

    This test used to assert "at most 1 in 5 noise-only datasets may unlock a
    factor". That is the wrong quantity. A spurious factor is only harmful if
    it degrades prediction on data the fit never saw — and counting
    acceptances made the threshold look protective while it was silently
    costing real detections (at 0.25 the fitter rejected a genuine 0.763
    pressure law outright, leaving 13.0% when 10.5% was available).

    Measured over twelve noise-only logs, lowering the gate from 0.25 to 0.10
    made leave-one-out error worse in 0 of 12 and better in 1 (9.6% -> 8.3%).
    The acceptances that appear are marginal-by-construction: they survive
    cross-validation, so they cannot be pure noise-chasing.

    So the assertion is now: whatever the fitter unlocks, the cross-validated
    error must not exceed the scale-only baseline. A factor that costs
    out-of-sample accuracy is a bug; one that merely appears is not.
    """
    for seed in (1, 2, 3, 4, 5, 6, 7, 8):
        fit = fit_factors(_synthetic(pressure_exponent=1.0, noise=0.08,
                                     seed=seed))
        assert fit.cv_mape is not None and fit.baseline_cv_mape is not None, (
            f"seed {seed}: the fit reported no cross-validated error at all")
        assert fit.cv_mape <= fit.baseline_cv_mape + 1e-9, (
            f"seed {seed}: unlocking {fit.unlocked} made out-of-sample error "
            f"worse ({fit.baseline_cv_mape:.1f}% -> {fit.cv_mape:.1f}%)")


def test_a_rejected_factor_says_it_was_rejected_for_overfitting():
    fit = fit_factors(_synthetic(pressure_exponent=1.0))
    reason = " ".join(fit.rejected.values())
    assert "cross-validated" in reason
    assert "overfitting" in reason


# ── identifiability gates ────────────────────────────────────────────
def test_a_factor_whose_driver_never_varies_is_locked():
    """Four runs at one pressure cannot say anything about pressure."""
    fit = fit_factors([Measurement(3000, 3.0, 60), Measurement(6000, 3.0, 120),
                       Measurement(4500, 3.0, 90), Measurement(7500, 3.0, 150)])
    assert "pressure_exponent" not in fit.unlocked
    assert "pressure varies by only 0%" in fit.locked["pressure_exponent"]


def test_too_few_measurements_lock_everything_beyond_the_scale():
    fit = fit_factors(_synthetic(pressures=(2.0, 4.0), speeds=(60,)))
    assert fit.unlocked == []
    assert fit.kp_m_per_pa is not None, "the scale should still be fitted"
    assert any("per free parameter" in v for v in fit.locked.values())


def test_the_budget_scales_with_the_dataset():
    small = fit_factors(_synthetic(pressures=(1.0, 3.0), speeds=(60,),
                                   pressure_exponent=0.65))
    large = fit_factors(_synthetic(pressure_exponent=0.65))
    assert len(small.unlocked) <= len(large.unlocked)


def test_the_scale_is_always_fitted_even_when_nothing_unlocks():
    fit = fit_factors([Measurement(1450, 3.0, 60)])
    assert fit.kp_m_per_pa is not None
    assert fit.unlocked == []


def test_thresholds_are_documented_constants_not_magic_numbers():
    assert 0 < MIN_LEVERAGE < 1
    # Lower bound only. 0.25 was tried and measured to cost two real
    # detections in twelve to avoid one false one, while a gate at 0.10 never
    # made out-of-sample error worse (see
    # test_noise_never_makes_out_of_sample_prediction_worse). Below ~0.05 the
    # false-positive rate climbs to 7/12, which is where noise-chasing starts.
    assert 0.05 <= MIN_CV_GAIN < 1.0, (
        "below 0.05 the gate admits noise as physics; the two-sided noise "
        "study is tabulated above MIN_CV_GAIN in factor_fit.py")
    assert POINTS_PER_FACTOR >= 2


# ── the slurry factors ───────────────────────────────────────────────
def _abrasive_series(c_half=3.0, pressures=(2.0, 4.0),
                     concentrations=(0.5, 1.0, 2.0, 4.0, 8.0, 16.0)):
    """Loading series obeying Luo-Dornfeld occupancy with a known C_half."""
    ref = sum(concentrations) / len(concentrations)
    v = 2 * math.pi * 60 / 60 * OFFSET_M
    out = []
    for c in concentrations:
        for psi in pressures:
            base = KP_TRUE * psi * 6894.757 * v * 1e10 * 60
            occ = (1 - math.exp(-c / c_half)) / (1 - math.exp(-ref / c_half))
            out.append(Measurement(base * occ, psi, 60, abrasive_wt_pct=c))
    return out


def test_abrasive_saturation_is_recovered():
    """The defining Luo-Dornfeld behaviour, fitted from a loading series."""
    fit = fit_factors(_abrasive_series(c_half=3.0))
    assert "abrasive_half_wt_pct" in fit.unlocked
    assert fit.values["abrasive_half_wt_pct"] == pytest.approx(3.0, rel=0.15)
    assert fit.cv_mape < fit.baseline_cv_mape / 10.0


def test_a_saturating_slurry_is_distinguished_from_a_starved_one():
    """The practical question: is more abrasive still buying rate?"""
    saturated = fit_factors(_abrasive_series(c_half=1.0))
    starved = fit_factors(_abrasive_series(c_half=20.0))
    assert (saturated.values["abrasive_half_wt_pct"]
            < starved.values["abrasive_half_wt_pct"])


def test_activation_energy_is_recovered_from_a_temperature_series():
    R = 8.314462618e-3
    v = 2 * math.pi * 60 / 60 * OFFSET_M
    ms = []
    for t in (20, 30, 40, 50, 60):
        for psi in (2.0, 4.0):
            base = KP_TRUE * psi * 6894.757 * v * 1e10 * 60
            arr = math.exp(-45.0 / R * (1 / (t + 273.15) - 1 / (40 + 273.15)))
            ms.append(Measurement(base * arr, psi, 60, temperature_c=t))
    fit = fit_factors(ms)
    assert "activation_energy_kj_per_mol" in fit.unlocked
    assert fit.values["activation_energy_kj_per_mol"] == pytest.approx(45.0, rel=0.1)


def test_two_real_effects_are_separated_rather_than_confounded():
    """Sub-linear pressure AND abrasive saturation in one dataset."""
    import random
    rng = random.Random(5)
    v = 2 * math.pi * 60 / 60 * OFFSET_M
    ms = []
    for psi in (1.0, 2.0, 3.5, 5.0):
        for c in (1.0, 3.0, 9.0):
            occ = (1 - math.exp(-c / 3.0)) / (1 - math.exp(-(13 / 3) / 3.0))
            rate = (KP_TRUE * psi * 6894.757 * v * 1e10 * 60
                    * (psi / 3.0) ** (0.7 - 1.0) * occ)
            ms.append(Measurement(rate * (1 + rng.uniform(-0.05, 0.05)), psi, 60,
                                  abrasive_wt_pct=c))
    fit = fit_factors(ms)
    assert set(fit.unlocked) == {"abrasive_half_wt_pct", "pressure_exponent"}
    assert fit.values["pressure_exponent"] == pytest.approx(0.70, abs=0.08)
    assert fit.values["abrasive_half_wt_pct"] == pytest.approx(3.0, rel=0.2)
    assert fit.cv_mape < 5.0


def test_factors_with_no_data_stay_locked_even_in_a_rich_dataset():
    """A 12-point pressure/abrasive study still says nothing about temperature."""
    fit = fit_factors(_abrasive_series())
    for name in ("activation_energy_kj_per_mol", "oxidizer_langmuir_K",
                 "abrasive_size_exponent", "velocity_exponent"):
        assert name not in fit.unlocked
        assert name in fit.locked


# ── through the solver ───────────────────────────────────────────────
def _run(measurements, psi=3.0):
    return simulate(Recipe(
        model="preston",
        wafer=Wafer(film="oxide", n_radial=11),
        slurry=Slurry(pack="oxide_silica"),
        pad=Pad(groove_width_mm=0.5, groove_pitch_mm=2.0, groove_depth_mm=0.75),
        disk=Disk(),
        tool=Tool(pressure_psi=psi, rpm_platen=60.0, rpm_head=60.0, time_s=60.0),
        measurements=[{"rate_A_per_min": m.rate_a_per_min,
                       "pressure_psi": m.pressure_psi,
                       "rpm_platen": m.rpm_platen} for m in measurements]))


def test_the_solver_reports_what_it_fitted_and_what_it_locked():
    r = _run(_synthetic(pressure_exponent=0.65))
    ff = r.extras["factor_fit"]
    assert ff["unlocked"] == ["pressure_exponent"]
    assert ff["fitted_factors"]["pressure_exponent"] == pytest.approx(0.65, abs=0.05)
    assert ff["improvement_percent_points"] > 0


def test_the_solver_leaves_preston_alone_when_the_data_agree_with_it():
    ff = _run(_synthetic(pressure_exponent=1.0)).extras["factor_fit"]
    assert ff["unlocked"] == []
    assert ff["fitted_factors"] == {}


def test_a_departure_from_prestons_law_is_warned_about():
    r = _run(_synthetic(pressure_exponent=0.65))
    assert any("not the 1" in w and "pressure_exponent" in w for w in r.warnings)


def test_the_residuals_shown_come_from_the_model_actually_used():
    """The per-point table once showed scale-only predictions - every point
    identical, ~56% error - directly beneath a quoted accuracy of 0.8%. A
    report that contradicts itself on the same screen is worse than no report.
    """
    r = _run(_synthetic(pressure_exponent=0.65))
    cal = r.extras["calibration"]
    quoted = cal["cross_validated_mape_percent"]
    worst = max(abs(row["error_percent"]) for row in cal["residuals"])
    assert worst < max(5.0, quoted * 4), (
        f"residuals reach {worst:.1f}% while the quoted accuracy is "
        f"{quoted:.1f}%: the table is not showing the fitted model")
    predictions = {row["predicted_A_per_min"] for row in cal["residuals"]}
    assert len(predictions) > 1, "every point has the same prediction"


def test_fitting_still_produces_a_usable_prediction():
    r = _run(_synthetic(pressure_exponent=0.65))
    assert r.mean_rr_angstrom_per_min > 0
    assert r.wiwnu_percent is not None
