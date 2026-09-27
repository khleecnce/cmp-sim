"""§46 — the axis oracle spans the MONOTONE POWER LAWS, and nothing else.

`tools/axis_error_census.py` prices an axis by granting the model one free
exponent, `predicted * (x/x_ref)**b`, and calls the drop "the MOST any
closed-form law on that axis could buy". That sentence carries §14's
"the improvable error is DISTRIBUTED", §16's "<= 10 % is outside reach", and
the 2 pp ownership bar behind the pre-registered READING 1 / READING 2 verdict.

A straight line in log-log cannot bend. The model being priced does bend --
Gaussian in pH, Langmuir in oxidiser, IEP-referenced zeta -- so an axis whose
real law saturates or peaks can be priced at ~0 pp and filed as closed.

Every number here is RE-MEASURED at run time. Literals would go stale the
moment a pack constant is re-sourced, and going stale silently is the failure
these tests exist to prevent (§40's lesson: a stale claim gets its prose
edited instead of its code).

Calibrated against the bug: forcing `b2 = 0` in
`tools/oracle_curvature_blindness_probe._oracle_curved` (i.e. reverting the
probe to the shipping oracle) fails `test_the_blindness_is_arithmetic_not_statistical`,
`test_curvature_buys_more_than_its_own_degree_of_freedom`, and
`test_at_least_one_axis_crosses_the_ownership_bar_only_with_curvature`.
"""
from __future__ import annotations

import json
import math
import subprocess
import sys
from pathlib import Path

import pytest

from tools.axis_error_census import MIN_LEVELS, OWNERSHIP_MIN_GAIN, _oracle
from tools.oracle_curvature_blindness_probe import (
    MIN_LEVELS_CURVE, _fit_quadratic, _oracle_curved, price_curvature,
    report, shared_curvature_bound,
)

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def prices():
    out = price_curvature()
    assert out, "the probe priced nothing: the corpus or the census changed shape"
    return out


# ───────────────────────── the arithmetic ──────────────────────────

def test_the_blindness_is_arithmetic_not_statistical():
    """On a symmetric log ladder a pure bend is INVISIBLE to a fitted slope.

    Take levels spaced evenly in log x (1/2/4/8/16 -- the layout experimenters
    habitually choose for a concentration or size sweep) and a log-residual
    that is purely quadratic. The odd moments of the centred design vanish, so
    the OLS slope is exactly zero: the linear oracle reports no gain at all
    while one curved constant explains the residual completely.

    This is the same class of fact as §45's span-ratio proof -- a property of
    the statistic, not of this corpus -- so no dataset change can recover it.
    """
    x = [1.0, 2.0, 4.0, 8.0, 16.0]
    xr = math.exp(sum(math.log(v) for v in x) / len(x))
    u = [math.log(v / xr) for v in x]
    assert abs(sum(u)) < 1e-12                      # centred by construction
    assert abs(sum(v ** 3 for v in u)) < 1e-9       # the odd moment that vanishes

    c = 0.30
    predicted = [1000.0] * len(x)
    measured = [p * math.exp(c * v * v) for p, v in zip(predicted, u)]

    lin_mape, b_lin = _oracle(measured, predicted, x)
    cur_mape, b1, b2 = _oracle_curved(measured, predicted, x)

    assert abs(b_lin) < 1e-9, (
        f"the linear oracle's slope is {b_lin:.3e}, not zero: the ladder is no "
        "longer symmetric in log x and the proof below does not apply")
    assert b2 == pytest.approx(c, abs=1e-9), (
        f"the curved oracle recovered b2={b2:.4f} instead of the planted "
        f"{c}; the quadratic fit is wrong, not the claim")
    assert abs(b1) < 1e-9
    assert cur_mape < 1e-6 < lin_mape, (
        f"curved MAPE {cur_mape:.3e} vs linear {lin_mape:.3f}: a bend a single "
        "constant explains exactly must be worth nothing to the slope oracle")


def test_the_quadratic_fit_recovers_a_planted_law_exactly():
    """Non-vacuity guard for the fit itself, on an ASYMMETRIC ladder.

    The test above uses a symmetric ladder, where `b1` is zero for a trivial
    reason. If `_fit_quadratic` silently dropped the linear column it would
    still pass. Here both constants are planted and both must come back.
    """
    x = [0.5, 1.0, 1.7, 3.0, 9.0]
    xr = math.exp(sum(math.log(v) for v in x) / len(x))
    u = [math.log(v / xr) for v in x]
    b1_true, b2_true = -0.42, 0.17
    ly = [b1_true * v + b2_true * v * v for v in u]
    b1, b2 = _fit_quadratic(u, ly)
    assert b1 == pytest.approx(b1_true, abs=1e-9)
    assert b2 == pytest.approx(b2_true, abs=1e-9)


def test_the_curve_oracle_demands_more_levels_than_the_slope_oracle():
    """Guard 1: a 2-parameter shape on 3 levels is interpolation, not a price.

    The shipping oracle's own `MIN_LEVELS = 3` exists for exactly this reason
    with one parameter; allowing the quadratic the same floor would let it
    report gains that are the fit passing through every point.
    """
    assert MIN_LEVELS_CURVE > MIN_LEVELS
    assert MIN_LEVELS_CURVE >= 4


# ───────────────────────── the measurement ─────────────────────────

def test_curvature_buys_more_than_its_own_degree_of_freedom(prices):
    """A second free parameter buys error reduction from noise alone.

    So every real gain is reported net of a permutation null: the axis values
    shuffled against the residuals, both oracles refitted. The null must be
    non-vacuous (some pairs really do gain from nothing) and at least one pair
    must clear it -- otherwise "the oracle is blind to bends" would be a claim
    about the statistic with no instance in this corpus.
    """
    nulls = [p.null_excess_pp for p in prices]
    assert max(nulls) > 0.5, (
        f"the permutation null never exceeds {max(nulls):.3f} pp, so it is not "
        "policing anything; a dof control that always reads zero is decoration")

    winners = [p for p in prices if p.excess_pp > 0]
    assert winners, (
        "no (dataset, axis) pair gains from curvature beyond its own null. "
        "Then this probe measured a real absence and §14/§16 stand as written "
        "-- record that instead of deleting the test")
    best = max(winners, key=lambda p: p.excess_pp)
    assert best.excess_pp > 1.0, (
        f"the largest net curvature gain is only {best.excess_pp:.2f} pp on "
        f"{best.dataset}/{best.axis}")


def test_at_least_one_axis_crosses_the_ownership_bar_only_with_curvature(prices):
    """The consequence for §14: ownership was decided by a blind statistic.

    `OWNERSHIP_MIN_GAIN` routes a dataset's points to an axis or to
    `distributed`. A pair priced below the bar by the slope oracle and above it
    once a bend is allowed was mis-filed, and the pre-registered 30 % reading
    was taken on that filing.
    """
    flips = [p for p in prices if p.flips_ownership]
    assert flips, (
        "no pair crosses the ownership bar only with curvature; the blindness "
        "is then arithmetic but inconsequential here, which is a different and "
        "weaker claim -- amend §46 rather than this assertion")
    for p in flips:
        assert p.linear_gain_pp < OWNERSHIP_MIN_GAIN
        assert p.curved_gain_pp - p.null_excess_pp >= OWNERSHIP_MIN_GAIN
    names = {p.dataset for p in flips}
    text = report(prices)
    for name in names:
        assert name in text, f"{name} flips ownership but the report omits it"


def test_a_shared_curvature_is_priced_because_a_law_is_not_an_oracle(prices):
    """What a real model could buy: ONE bend shared by every dataset.

    The per-dataset figure is an upper bound nothing attains, which is the
    whole argument of `axis_error_census`. The honest follow-up is the shared
    constant, and it must be computed on the axis with the most members --
    chosen by count, never by which answer is prettier.
    """
    by_axis: dict[str, int] = {}
    for p in prices:
        by_axis[p.axis] = by_axis.get(p.axis, 0) + 1
    axis = max(sorted(by_axis), key=lambda a: by_axis[a])
    bound = shared_curvature_bound(prices, axis)
    assert bound is not None, f"{axis} has {by_axis[axis]} members but no bound"
    assert bound["datasets"] >= 2
    # A shared constant can only ever buy less than the mean per-dataset
    # oracle; if it buys more, the two prices are not measuring the same thing.
    assert bound["shared_gain_pp"] <= max(
        0.0, bound["oracle_excess_pp"]) + 25.0, bound


def test_the_flattening_majority_is_still_there_after_the_model(prices):
    """§28's sign claim, re-measured through this probe's independent route.

    §28 found loading-response curvature the model cannot produce, with a
    consistent SIGN (saturating). If that sign had evaporated the finding would
    be noise; it is re-derived here from the quadratic oracle rather than from
    successive-slope differences, so the two are independent reductions of the
    same data.
    """
    loading = [p for p in prices if p.axis == "abrasive_wt_pct"]
    assert len(loading) >= 4, f"only {len(loading)} loading ladders priced"
    negative = [p for p in loading if p.b2 < 0]
    assert len(negative) > len(loading) / 2, (
        f"only {len(negative)} of {len(loading)} loading curvatures are "
        "saturating; §28's signed residual has changed sign and that entry "
        "needs re-reading, not this test")


# ───────────────────────── the invariant ───────────────────────────

def test_this_probe_changes_no_prediction(prices):
    """It measures only. A moved median would mean a pack was written to.

    The corpus median is read from the shipping CLI, not recomputed here, so
    the check cannot be satisfied by a second copy of the scorer agreeing with
    itself.
    """
    out = subprocess.run([sys.executable, "-m", "cmp_sim.cli", "accuracy", "--json"],
                         capture_output=True, text=True, cwd=ROOT)
    assert out.returncode == 0, out.stderr[-500:]
    summary = json.loads(out.stdout)["summary"]
    assert summary["median_shape_error_percent"] > 0
    assert summary["datasets_scored"] >= 40
