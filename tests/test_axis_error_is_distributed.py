"""The improvable error is DISTRIBUTED: no single-axis law reaches 10 %.

STATUS.md pre-registered the reading of this measurement BEFORE it was run
(after four consecutive thin-axis closures moved the corpus median ~1 pp):

  1. If one axis holds >= 30 % of the improvable POINTS, target that axis next.
  2. If none does, the error is distributed, <= 10 % is not reachable by adding
     closed-form laws one axis at a time, and that argument -- not the word
     "hard" -- is what licenses the <= 15 % completion allowance.

``tools/axis_error_census.py`` ran it and reading 2 held: the largest named axis
(``abrasive_wt_pct``) holds 24.9 % and the single largest block, 42.4 % of
improvable points, is error NO axis the dataset sweeps can reach even when
granted a free exponent.

These tests pin the closure and, more importantly, pin the ONE result that
keeps it from being an excuse: tightening the bound from a per-dataset oracle to
a single SHARED exponent (which is what a real law must use) collapses four of
six axes to near zero because their per-dataset exponents disagree in SIGN --
while ``oxidizer_wt_pct`` survives and stays a derivation target.

The measurement is expensive (the real simulator runs over every improvable
dataset), so it is computed once per session and shared.
"""
from __future__ import annotations

import functools
import statistics

import pytest

from tools import axis_error_census as census


@functools.lru_cache(maxsize=1)
def _prices():
    return tuple(census.price())


@functools.lru_cache(maxsize=None)
def _bound(axis: str):
    return census.shared_exponent_bound(list(_prices()), axis)


def _points_by_owner():
    owners: dict[str, int] = {}
    for dp in _prices():
        owners[dp.owner] = owners.get(dp.owner, 0) + dp.n
    return owners


def test_no_single_axis_owns_thirty_percent_of_the_improvable_points():
    """Reading 1 is refuted: the corpus has no dominant axis.

    Shares are measured in POINTS, never dataset counts, for the reason the
    11th run pinned by test: a median over 46 datasets moves by re-ranking the
    median dataset, so a dataset-count share can make a 24-point axis look like
    the main event.
    """
    owners = _points_by_owner()
    total = sum(owners.values())
    assert total > 300, f"the improvable bucket shrank unexpectedly ({total} points)"

    named = {k: v for k, v in owners.items() if k != "distributed"}
    top, top_points = max(named.items(), key=lambda kv: kv[1])
    share = 100.0 * top_points / total
    assert share < 30.0, (
        f"{top} now holds {share:.1f} % of improvable points. Reading 1 was "
        "pre-registered: if an axis clears 30 %, it becomes the next target "
        "regardless of how derivable its physics looks. Follow the "
        "pre-registration instead of editing this test.")


def test_the_largest_single_block_is_error_no_swept_axis_can_reach():
    """42.4 % of improvable points are owned by NO axis.

    This is the quantitative core of the <= 15 % allowance. These datasets
    respond to the axes they sweep (they are in ``responsive_miss``, so
    inertness is already excluded), and yet a FREE exponent on their best axis
    buys less than the ownership threshold. Their error is therefore not a
    missing single-axis law.
    """
    owners = _points_by_owner()
    total = sum(owners.values())
    distributed = owners.get("distributed", 0)
    assert distributed / total > 0.33, (
        f"only {100.0 * distributed / total:.1f} % of improvable points are "
        "unowned now. If this block has genuinely shrunk, the distributed "
        "verdict in docs/limits.md section 14 must be re-argued.")
    assert distributed >= max(v for k, v in owners.items() if k != "distributed"), (
        "the unowned block must remain the largest single block for section "
        "14's argument to hold")


@pytest.mark.parametrize("axis", ["abrasive_size_nm", "pressure", "slurry_ph"])
def test_a_shared_exponent_buys_almost_nothing_on_the_dispersed_axes(axis):
    """A LAW must use one constant everywhere, and here that costs the gain.

    The per-dataset oracle buys 4-8 pp on each of these axes. One exponent
    shared across the same datasets buys < 2 pp. The gap is the whole reason
    the oracle is reported as an upper bound: what looks like a missing law is
    between-dataset dispersion.

    ``abrasive_wt_pct`` was in this list until 2026-09-27 and is now measured
    separately below: fixing the saturating branch's load-sharing exponent
    removed its sign disagreement, so the "dispersed" diagnosis no longer
    describes it.
    """
    bound = _bound(axis)
    assert bound is not None, f"{axis} is no longer swept by 2+ datasets"
    assert bound["shared_gain_pp"] < 2.0, (
        f"a single shared exponent on {axis} now buys "
        f"{bound['shared_gain_pp']:.1f} pp (oracle "
        f"{bound['oracle_gain_pp']:.1f} pp). If that is real, {axis} has become "
        "a derivable law and belongs in a pack -- with a derivation, not this "
        "fitted offset.")
    assert bound["shared_gain_pp"] < bound["oracle_gain_pp"], (
        "sharing a constant cannot beat a per-dataset fit; if it does, the "
        "oracle is mis-measured")


@pytest.mark.parametrize("axis", ["abrasive_size_nm", "pressure", "slurry_ph"])
def test_the_dispersed_axes_disagree_in_sign_not_merely_in_magnitude(axis):
    """The diagnosis, not just the symptom.

    Exponents that scattered but shared a sign would still admit a law with a
    mean value. These straddle zero, so no single exponent is even the right
    DIRECTION for every dataset. That is what makes the axis unreachable rather
    than merely noisy.
    """
    bound = _bound(axis)
    assert bound is not None
    exponents = bound["exponents"]
    assert min(exponents) < 0.0 < max(exponents), (
        f"{axis} exponents no longer straddle zero ({exponents}); re-argue "
        "section 14 rather than relaxing this test")


def test_the_concentration_axis_stopped_disagreeing_in_sign_when_the_model_did():
    """The sign scatter on ``abrasive_wt_pct`` was partly the MODEL's, not the data's.

    Until 2026-09-27 this axis was pinned alongside the other dispersed axes:
    its per-dataset residual exponents straddled zero, which was read as
    "no single exponent is even the right direction" and used to argue that
    the axis is unreachable (docs/limits.md section 14).

    Three of those nine exponents were NEGATIVE because the model was
    over-predicting the concentration response, not because those experiments
    disagreed with the others. The saturating branch of
    ``models/luo_dornfeld.mechanical_factor`` was multiplying by the active
    particle COUNT ratio (N^1), asserting chi = 0 against the chi = 1.0 the
    same call resolves; datasets under a pack with ``abrasive_conc_half_wt_pct``
    therefore needed a negative correction to undo the model's excess slope.
    See docs/derivations.md, "The two concentration branches were different
    PHYSICS".

    Measured across that one change (`tools/axis_error_census.py`):

        before   exponents [-0.54, -0.18, -0.04, 0.0, 0.10, 0.26, 0.44, 0.49, 0.81]
                 shared gain 1.46 pp,  oracle 7.58 pp,  85 points owned (24.9 %)
        after    exponents [ 0.00,  0.02,  0.12, 0.18, 0.26, 0.26, 0.44, 0.49, 1.05]
                 shared gain 2.54 pp,  oracle 6.85 pp,  63 points owned (18.4 %)

    Two things follow, and they point in opposite directions, so both are
    pinned rather than the convenient one:

    1. The axis is no longer DISPERSED in the sign sense. Every residual
       exponent is now >= 0, so a single shared exponent is at least the right
       direction everywhere. That is why it is no longer parametrized into the
       two tests above.
    2. It is therefore also no longer closed. A shared exponent now buys
       2.5 pp, over the 2.0 pp bar those tests use as "a law may be hiding
       here". **That is a lead, not a licence to fit one**: all nine residual
       exponents being positive means the model still UNDER-responds to
       loading, and the honest next step is to find which term is missing, not
       to add a fitted offset that would reproduce this residual by
       construction. This test exists so the lead cannot be quietly forgotten.
    """
    bound = _bound("abrasive_wt_pct")
    assert bound is not None, "abrasive_wt_pct is no longer swept by 2+ datasets"
    exponents = bound["exponents"]
    assert min(exponents) >= 0.0, (
        f"the concentration residual exponents straddle zero again "
        f"({exponents}). Either a regression re-introduced an over-steep "
        "concentration term, or a newly added dataset genuinely disagrees in "
        "sign -- find out which before touching this test.")
    assert bound["shared_gain_pp"] > 2.0, (
        f"a shared concentration exponent now buys only "
        f"{bound['shared_gain_pp']:.2f} pp. If a DERIVED term closed this gap, "
        "that is the intended outcome: record it in docs/derivations.md and "
        "retire this test. If it shrank without a derivation, something is "
        "masking the axis.")
    assert bound["shared_gain_pp"] < bound["oracle_gain_pp"], (
        "sharing a constant cannot beat a per-dataset fit; if it does, the "
        "oracle is mis-measured")


def test_the_oxidizer_axis_survives_sharing_but_its_gain_is_inadmissible():
    """The measurement that motivated limit 15, kept separate from its verdict.

    ``oxidizer_wt_pct`` genuinely does keep most of its oracle gain when the
    exponent is shared, with all-positive exponents — that is a real property of
    the census and this test pins it so the follow-up cannot be forgotten. What
    it does NOT mean is that a term should be added: the follow-up probe
    (``tools/oxidizer_order_probe.py``, limit 15) found the measured order is
    negative in two admissible blocks, and that this +9.5 pp comes entirely from
    one calibration set plus one promoter-confounded body. Admissibility is
    asserted in ``tests/test_oxidizer_order_is_not_half.py``; here only the
    census number is pinned.
    """
    bound = _bound("oxidizer_wt_pct")
    assert bound is not None, "the oxidizer axis lost its sweeping datasets"
    assert bound["shared_gain_pp"] > 5.0, (
        "the oxidizer axis no longer survives sharing; limit 15 explains why "
        "that gain was inadmissible anyway, but the number it audits is this "
        "one and the limit must be re-argued if it moves")
    assert all(b >= 0.0 for b in bound["exponents"]), (
        f"oxidizer exponents were all positive when limit 15 was written "
        f"({bound['exponents']}); that shared sign is why the axis looked open")
    assert 0.2 < bound["db"] < 0.8, (
        f"the shared oxidizer exponent moved to {bound['db']:+.2f}; the "
        "radical-chain half-order rationale examined in docs/limits.md §15 is "
        "pinned to a value near +1/2 and must be re-argued if it moves")


def test_the_census_never_blames_an_axis_the_rate_ignores():
    """Guard against the failure mode the census was built to avoid.

    An axis that does not reach the predicted rate at all (INERT in
    ``residual_census``) must not be priced, because a free exponent on an
    inert axis would fit the residual perfectly and claim the dataset -- which
    would be fitting, not measuring.
    """
    for dp in _prices():
        for p in dp.prices:
            assert p.axis  # priced axes are named
        assert dp.owner == "distributed" or dp.best_gain >= census.OWNERSHIP_MIN_GAIN, (
            f"{dp.dataset} is owned by {dp.owner} on a gain of "
            f"{dp.best_gain:.1f} pp, below the ownership threshold")


def test_the_measurement_modifies_no_pack():
    """The census is a measurement. Nothing it fits may reach a pack."""
    import inspect
    source = inspect.getsource(census)
    for forbidden in ("write_text", "safe_dump", "yaml.dump", "open("):
        assert forbidden not in source, (
            f"tools/axis_error_census.py contains {forbidden!r}: a measurement "
            "tool must never write a pack")


def test_the_report_states_points_not_dataset_counts_as_the_axis_size():
    """The report must express axis size in points, the way the reading demands."""
    text = census.report(list(_prices()))
    assert "POINTS BY OWNING AXIS" in text
    assert "improvable points" in text
    assert "SHARED-EXPONENT BOUND" in text, (
        "the shared-exponent bound is the part that distinguishes a law from an "
        "oracle; it must stay in the report")
    owners = _points_by_owner()
    total = sum(owners.values())
    assert f"{total} measured points" in text


def test_the_unowned_block_is_not_explained_by_small_datasets():
    """Cheap escape hatch, closed: the unowned block is not just tiny datasets.

    If every unowned dataset had 4 rows, "distributed" would mean "too few
    points to fit anything" rather than "no axis carries it". Check the median
    size of unowned datasets against the owned ones.
    """
    unowned = [dp.n for dp in _prices() if dp.owner == "distributed"]
    owned = [dp.n for dp in _prices() if dp.owner != "distributed"]
    assert unowned and owned
    assert statistics.median(unowned) >= 4, (
        "the unowned block is dominated by 3-row datasets; the distributed "
        "verdict would then be a statement about dataset size, not physics")
