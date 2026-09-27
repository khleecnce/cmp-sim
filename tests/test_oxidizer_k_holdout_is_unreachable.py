"""The last self-graded citation is unrepairable too (docs/limits.md §35).

`cu_h2o2_bta.oxidizer_peak_shape_K = 8.0` was fitted to Du 2004's H2O2 series
and that block is then scored at 6.2% as if held out. One citation, so only
reachability needs asking: can K come from another sweep?

Measured (``tools/oxidizer_k_holdout_probe.py``): no. K spans four orders of
magnitude across the corpus, the within-group spread exceeds the between-group
spread on every candidate grouping (ratios 0.69-0.71x against a 2x bar), and
the worst disagreement -- 3.58 decades -- is inside Cu alone. A held-out K
would be a transplant of that size.

With this, all 18 self-graded citations of §32 are measured and none is
repairable, so the held-out median 19.5% stands as the honest figure.
"""
from __future__ import annotations

import math

import pytest

from tools.oxidizer_k_holdout_probe import (
    IMPLICATED,
    donors,
    spread_by,
    sweeps,
    verdict,
)
from tools.ph_holdout_reachability_probe import PROPERTY_BAR


@pytest.fixture(scope="module")
def rows():
    r = sweeps()
    assert len(r) >= 8, (
        "only %d oxidiser sweeps yielded a fittable K; below this every "
        "assertion here passes by default" % len(r))
    assert IMPLICATED <= {x["dataset"] for x in r}, (
        "the probe no longer reaches the implicated block %s" % sorted(IMPLICATED))
    return r


def test_no_grouping_makes_k_a_property(rows):
    """The assertion that makes outcome (b) unreachable.

    A ratio below 1.0 means two members of one group differ more than two
    groups do. A grouping clearing the 2x bar reopens the repair and this
    must fail.
    """
    v = verdict(rows)
    clearing = [("+".join(g["keys"]), g["ratio"]) for g in v["groupings"]
                if g["is_property"]]
    assert not clearing, (
        "%s now clear the %.1fx property bar for the oxidiser shape constant; "
        "a held-out K may exist and §35 must be re-measured"
        % (clearing, PROPERTY_BAR))
    finite = [g["ratio"] for g in v["groupings"] if g["ratio"] == g["ratio"]]
    assert finite and max(finite) < 1.0, (
        "the best grouping now reaches %.2fx; below 1.0 was the finding"
        % (max(finite) if finite else float("nan")))


def test_the_quoted_cu_disagreement_is_real(rows):
    """§35's headline example must be checkable, not rhetorical.

    Two Cu sweeps fit K = 190 and K = 0.05. If the Cu spread ever collapses,
    the example is wrong even if the ratio still fails.
    """
    cu = [r for r in rows if r["film"] == "cu"]
    assert len(cu) >= 3, "too few Cu oxidiser sweeps to make the claim: %d" % len(cu)
    span = math.log10(max(r["k"] for r in cu)) - math.log10(min(r["k"] for r in cu))
    assert span >= 2.0, (
        "the Cu within-film K span has fallen to %.2f decades; the quoted "
        "3.58-decade disagreement no longer holds" % span)


def test_grid_edge_fits_are_reported_not_dropped(rows):
    """The verdict must not be buyable by excluding inconvenient blocks.

    Six sweeps pin K at the low edge, meaning they never reach a peak and
    carry no curvature for the peaked form. Dropping them would remove
    exactly the evidence that the peaked form does not describe them —
    the selection this repository forbids.
    """
    edge = [r for r in rows if r["at_grid_edge"]]
    assert edge, (
        "no sweep pins K at a grid edge any more; either the grid or the "
        "corpus changed and §35's stated limits are stale")
    # and they must be INSIDE the measurement, not filtered out of it
    v_all = verdict(rows)
    v_kept = verdict([r for r in rows if not r["at_grid_edge"]])
    assert v_all["worst_within_decades"] >= v_kept["worst_within_decades"], (
        "excluding grid-edge fits WIDENS the within-group spread, which means "
        "they are not the source of the disagreement and the stated limit is "
        "describing the wrong thing")


def test_the_donor_exists_so_this_is_not_a_no_data_refusal(rows):
    """Du 2004 shares a film with other publications: the refusal is about
    the donor's quality, not its absence."""
    d = donors(rows, ("film",))
    assert d and all(v > 0 for v in d.values()), (
        "du2004 was supposed to HAVE donor publications on its film; got %s" % d)


def test_expiry_a_narrow_within_group_spread_reopens_the_repair(rows):
    """A second Cu H2O2 sweep that passes its peak and agrees with Du would
    make K a property of the oxidant-film pair."""
    v = verdict(rows)
    assert v["worst_within_decades"] > 1.0, (
        "the worst within-group K disagreement has fallen to %.2f decades; a "
        "held-out K may now be meaningful and outcome (b) must be priced"
        % v["worst_within_decades"])


def test_between_and_within_are_measured_in_the_log(rows):
    """K spans decades, so an arithmetic spread would be dominated by the
    largest fitted value and would report a ratio that says nothing.

    Pinned because switching to a linear spread is an easy 'simplification'
    that would silently change every number in §35.
    """
    s = spread_by(rows, ("film",))
    assert s["between"] < 5.0 and s["within"] < 5.0, (
        "spreads of %.2f / %.2f look like raw K rather than log10 K; §35's "
        "decades are no longer decades" % (s["between"], s["within"]))
