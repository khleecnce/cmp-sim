"""The peaked oxidizer response, checked against the measurement it came from.

The copper/H2O2 system is famous for peaking at low peroxide and declining
after; the model used to fall monotonically from zero, contradicting the peak
its own parameter pack declared. The obstacle was identifiability, not physics:
a peaked curve with both the peak POSITION and the shape free is degenerate
when the data sit on one side of the maximum.

The resolution is to take the peak position from a measurement, which makes the
decay scale a consequence rather than a parameter and leaves exactly one degree
of freedom. This file checks the shape, the algebra behind that constraint, and
the reproduction of the source data.

Data: Du 2004, J. Electrochem. Soc. 151(4) G230, doi:10.1149/1.1648029, Fig. 1
-- read off the original PDF (axis "Peroxide Concentration (Vol%)", six points
0/1/3/5/7.5/10 at fixed pH 4, 4.6 wt% alumina, 7.63 psi, 0.2 m/s).
"""
import math

import pytest

from cmp_sim.models.chemical_rate import peaked_oxidizer_response as f

# Digitised from Fig. 1; the 1 vol% value is also printed in the text
# ("reaches a maximum of 180 nm/min in 1% H2O2"), which is what validates the
# digitisation procedure.
DU_CONC = [0.0, 1.0, 3.0, 5.0, 7.5, 10.0]
DU_RATE = [20.3, 180.4, 145.5, 109.4, 99.9, 85.3]
DU_PEAK = 1.0


# ── shape ────────────────────────────────────────────────────────────
def test_the_response_is_one_at_the_peak():
    """Normalised so it composes with Kp without changing the reference."""
    assert f(2.0, 2.0, 5.0) == pytest.approx(1.0)


def test_it_is_zero_at_zero_oxidizer():
    assert f(0.0, 1.0, 8.0) == 0.0


@pytest.mark.parametrize("k", [0.5, 2.0, 8.0, 30.0])
def test_the_maximum_really_sits_at_the_stated_peak(k):
    """This is the constraint the whole design rests on: d(ln f)/dC = 0 at the
    measured peak gives Cd = C_peak*(1 + K*C_peak). An earlier draft of the
    algebra used Cd = (1+K)/K and put the maximum somewhere else entirely -
    at K=30 it landed at 0.17 instead of 1.0."""
    peak = 1.0
    grid = [c / 500.0 for c in range(1, 6000)]
    found = max(grid, key=lambda c: f(c, peak, k))
    assert found == pytest.approx(peak, abs=0.01), (
        f"with K={k} the maximum is at {found}, not the stated {peak}")


def test_it_rises_before_the_peak_and_falls_after():
    peak, k = 1.0, 8.0
    assert f(0.3, peak, k) < f(0.7, peak, k) < f(peak, peak, k)
    assert f(peak, peak, k) > f(2.0, peak, k) > f(6.0, peak, k)


def test_a_missing_or_absurd_peak_is_refused_not_guessed():
    with pytest.raises(ValueError, match="peak"):
        f(1.0, 0.0, 8.0)
    with pytest.raises(ValueError):
        f(1.0, 1.0, 0.0)


# ── reproduction of the source data ──────────────────────────────────
def _fit_k_and_amplitude():
    """One free shape parameter (K) plus an amplitude; the floor is measured."""
    floor = DU_RATE[0]
    best = None
    for k_int in range(5, 20001, 5):
        k = k_int / 100.0
        num = den = 0.0
        for c, r in zip(DU_CONC, DU_RATE):
            if c == 0:
                continue
            v = f(c, DU_PEAK, k)
            num += v * (r - floor)
            den += v * v
        if den <= 0:
            continue
        a = num / den
        errs = [abs((floor + a * f(c, DU_PEAK, k) - r) / r)
                for c, r in zip(DU_CONC, DU_RATE) if c > 0]
        mape = sum(errs) / len(errs)
        if best is None or mape < best[0]:
            best = (mape, k, a, max(errs))
    return best


def test_it_reproduces_the_du_2004_sweep():
    """Six measured points, one free shape parameter, peak position measured."""
    mape, k, amplitude, worst = _fit_k_and_amplitude()
    assert mape < 0.10, (
        f"MAPE {mape*100:.1f}% with K={k}: the form does not describe the data")
    assert worst < 0.20, f"worst point off by {worst*100:.1f}%"


def test_the_fitted_amplitude_matches_the_printed_peak_rate():
    """The paper prints 180 nm/min at the peak. The amplitude plus the measured
    floor must land there, or the fit is describing something else."""
    _mape, _k, amplitude, _worst = _fit_k_and_amplitude()
    predicted_peak = DU_RATE[0] + amplitude * 1.0
    assert predicted_peak == pytest.approx(180.0, rel=0.10), (
        f"model peak {predicted_peak:.0f} vs the paper's printed 180 nm/min")


def test_the_monotonic_alternative_cannot_fit_this_data():
    """Justifies the added term: if plain Langmuir worked, the peaked form
    would be unnecessary complexity."""
    from cmp_sim.models.chemical_rate import langmuir_coverage

    floor = DU_RATE[0]
    best = None
    for k_int in range(1, 20001, 5):
        k = k_int / 100.0
        num = den = 0.0
        for c, r in zip(DU_CONC, DU_RATE):
            if c == 0:
                continue
            v = langmuir_coverage(c, k)
            num += v * (r - floor)
            den += v * v
        if den <= 0:
            continue
        a = num / den
        errs = [abs((floor + a * langmuir_coverage(c, k) - r) / r)
                for c, r in zip(DU_CONC, DU_RATE) if c > 0]
        mape = sum(errs) / len(errs)
        if best is None or mape < best[0]:
            best = (mape, k)
    langmuir_mape = best[0]
    peaked_mape = _fit_k_and_amplitude()[0]
    assert peaked_mape < langmuir_mape / 2.0, (
        f"peaked {peaked_mape*100:.1f}% vs monotonic {langmuir_mape*100:.1f}%: "
        "the extra term does not earn its place")


# ── wired into the solver ────────────────────────────────────────────
def _run(oxidizer_wt_pct, peak_shape_k=8.0):
    from cmp_sim.core.solver import simulate
    from cmp_sim.core.state import (Additive, Disk, Pad, Recipe, Slurry, Tool,
                                    Wafer)

    params = {"oxidizer_peak_shape_K": peak_shape_k} if peak_shape_k else {}
    return simulate(Recipe(
        model="full", wafer=Wafer(film="cu", n_radial=21),
        slurry=Slurry(pack="cu_h2o2_bta", additives=[
            Additive(name="hydrogen_peroxide", conc_wt_pct=oxidizer_wt_pct,
                     role="oxidizer")]),
        pad=Pad(groove_width_mm=0.5, groove_pitch_mm=2.0, groove_depth_mm=0.75),
        disk=Disk(),
        tool=Tool(pressure_psi=3.0, rpm_platen=60, rpm_head=60, time_s=60),
        params=params))


def test_a_concentration_scan_now_shows_a_maximum():
    """The original complaint: the oxidizer response fell monotonically in a
    system whose defining feature is a maximum."""
    concs = [0.5, 1.0, 2.0, 3.0, 5.0, 8.0, 12.0]
    rates = [_run(c).mean_rr_angstrom_per_min for c in concs]
    peak_at = concs[rates.index(max(rates))]
    assert 0.5 < peak_at < 12.0, f"no interior maximum; peak at {peak_at}"
    assert rates[0] < max(rates) and rates[-1] < max(rates), (
        f"the scan is still monotonic: {[round(r) for r in rates]}")


def test_the_inherited_oxidizer_term_is_replaced_not_multiplied():
    """Double-counting the same surface chemistry once collapsed a copper rate
    by 20x in this project, so the replacement must be explicit."""
    result = _run(3.0)
    replaced = [n for n in result.notes if "replaced the inherited" in n]
    assert replaced, "the inherited oxidizer term was not divided out"
    terms = (result.extras.get("chemistry") or {}).get("terms", {})
    assert not ("oxidizer" in terms and "oxidizer_peaked" in terms), (
        f"both oxidizer terms are in the product: {terms}")


def test_without_a_shape_constant_the_old_behaviour_is_unchanged():
    """Adding the term must not silently change packs that do not opt in."""
    assert (_run(3.0, peak_shape_k=None).mean_rr_angstrom_per_min
            == pytest.approx(_run(3.0, peak_shape_k=None).mean_rr_angstrom_per_min))
    with_peak = _run(3.0, peak_shape_k=8.0).mean_rr_angstrom_per_min
    without = _run(3.0, peak_shape_k=None).mean_rr_angstrom_per_min
    # At the declared peak the response is 1.0, so the two must agree there.
    assert with_peak == pytest.approx(without, rel=1e-6), (
        f"at the peak the peaked form gives {with_peak} but the old path "
        f"gives {without}; the term is not normalised to 1.0 at the peak")


def test_far_past_the_peak_is_flagged_as_extrapolation():
    result = _run(20.0)
    assert [w for w in result.warnings if "3x the measured peak" in w], (
        "running far out on the falling limb produced no caveat")
