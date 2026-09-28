"""The monotone size FAMILY is not what costs, and one block cannot cross by it.

docs/limits.md §54. §53 measured the packs' declared peaked size curves inert
and refuted, and it opened a question it did not answer: the shipping size
term is a SINGLE POWER LAW, monotone by construction, while several sweeps in
the corpus are not monotone. How much does that functional family cost?

Measured (``tools/size_family_floor_probe.py``): almost nothing. The best
single exponent FITTED ON EACH BLOCK ITSELF -- one free parameter per block,
far more freedom than the shipping model has -- leaves the non-monotone blocks
NO worse than the monotone ones. So non-monotonicity is not where the size
error lives, and the peaked-curve line of work that §53 closed stays closed
for a second, independent reason.

The load-bearing consequence is a FIT-FREE BOUND. The block the held-out
median needs (`us20190127607a1_teos_ceriasilica_size_sweep`, the 2nd cheapest
crosser at 18.9%) has a family floor ABOVE the 15% completion bar: no monotone
power law in the size exponent, however chosen, can carry it across. Any
crossing must come from outside this term.

Every number here is re-measured at test time from the dataset files. Nothing
is pinned as a literal that a data change could make stale while still
passing.
"""
from __future__ import annotations

import statistics

import pytest

from tools.size_family_floor_probe import (
    CONTROLS,
    NONMONOTONE_MIN_DEPTH,
    _nonmonotone_depth,
    _shape_mape,
    controls,
    measure,
)

BAR_PCT = 15.0

#: The block this section is about. It is named because the claim is about
#: THIS block's bound, not about a rank that a corpus change could shuffle.
BOUND_BLOCK = "us20190127607a1_teos_ceriasilica_size_sweep"


@pytest.fixture(scope="module")
def blocks():
    return measure()


# ── the probe must be an instrument before it is evidence (§43) ────────────

def test_controls_pass_or_nothing_below_is_evidence():
    ctl = controls()
    assert ctl, "the probe declares no controls — it cannot be trusted"
    failed = [c["name"] for c in ctl if not c["passed"]]
    assert not failed, (
        f"instrument controls failed: {failed}. Every corpus number this "
        "section quotes is then the reduction speaking, not the data.")


def test_the_control_that_makes_a_small_difference_meaningful_can_see_cost():
    """A sharp peak MUST leave a large floor.

    Without this, 'the family costs little' is indistinguishable from 'the
    reduction cannot see family cost'. The synthetic peak is the case where
    the answer is certain.
    """
    peak = [c for c in controls() if "peak" in c["name"]]
    assert peak, "the peaked control was removed"
    assert peak[0]["floor_pct"] > 20.0, (
        "the reduction reports a small floor for a series no monotone power "
        "law can follow — it is blind to the very thing §54 measures")
    # The control must also CARRY its bar, or a later session can silently
    # neuter the control config and leave `passed` True by vacuity.
    declared = [c for c in CONTROLS if "peak" in c["name"]]
    assert declared and declared[0]["min_floor_pct"] is not None, (
        "the peaked control no longer declares a min_floor_pct, so "
        "`passed` is True by vacuity and the control guards nothing")


def test_the_control_that_the_family_can_be_reached_also_passes():
    exact = [c for c in controls() if "power law" in c["name"]]
    assert exact, "the exact-power-law control was removed"
    assert exact[0]["floor_pct"] < 0.5 and exact[0]["explained"] > 0.95, (
        "the scan cannot recover an exponent that generated the data, so a "
        "large floor elsewhere would be the scan's failure, not the family's")


# ── non-vacuity: a collapsed subject must not read as a finding ────────────

def test_the_probe_has_both_classes_of_subject(blocks):
    assert len(blocks) >= 6, (
        f"only {len(blocks)} pure size sweeps — too few to compare classes")
    nm = [b for b in blocks if b["nonmonotone"]]
    mo = [b for b in blocks if not b["nonmonotone"]]
    assert nm and mo, (
        "one class is empty, so the comparison this section rests on is "
        "vacuous; a passing test would be indistinguishable from a deleted one")


def test_every_block_is_held_out(blocks):
    """The bound is only honest on blocks the model was not fitted to."""
    fitted = [b["dataset"] for b in blocks if not b["held_out"]]
    assert not fitted, (
        f"{fitted} are flagged used_for_calibration; their floors grade the "
        "model on its own answer key and must not be quoted as bounds")


# ── the finding ────────────────────────────────────────────────────────────

def test_non_monotonicity_is_not_what_costs(blocks):
    """The non-monotone blocks' family floor is NOT worse than the monotone
    blocks'. That is the measurement retiring the peaked-curve line of work,
    independently of §53's reachability and refutation arguments.
    """
    nm = statistics.median([b["floor_pct"] for b in blocks if b["nonmonotone"]])
    mo = statistics.median(
        [b["floor_pct"] for b in blocks if not b["nonmonotone"]])
    assert nm <= mo + 1e-9, (
        f"non-monotone floor {nm:.2f}% now EXCEEDS monotone {mo:.2f}%. The "
        "functional family has become a cost after all — §54's closure of the "
        "peaked-curve axis expires and the measurement must be redone.")


def test_a_floor_with_no_explained_spread_carries_no_verdict(blocks):
    """§26/§36's trap in this reduction: a block whose best exponent barely
    beats a single constant has a small floor for the wrong reason. Such
    blocks must be NAMED, never silently averaged into the class medians.
    """
    blind = [b for b in blocks if b["explained"] < 0.10]
    for b in blind:
        assert b["flat_pct"] - b["floor_pct"] < 1.0, (
            f"{b['dataset']} is classified blind but its exponent buys "
            f"{b['flat_pct'] - b['floor_pct']:.2f} pp — the classification is "
            "wrong")
    # The section's own reading must survive dropping them: otherwise the
    # comparison rests on blocks that measured nothing.
    seeing = [b for b in blocks if b["explained"] >= 0.10]
    nm = [b["floor_pct"] for b in seeing if b["nonmonotone"]]
    mo = [b["floor_pct"] for b in seeing if not b["nonmonotone"]]
    assert nm and mo, "dropping the blind blocks empties a class"
    assert statistics.median(nm) <= statistics.median(mo) + 1e-9, (
        "the reading survives only because a block with no explained spread "
        "was averaged in — it is an artefact, not a finding")


def test_the_binding_block_cannot_cross_the_bar_inside_this_family(blocks):
    """The fit-free bound. The block sits 2nd in the held-out crossing
    shortlist, and its floor is ABOVE the completion bar, so no size exponent
    can carry it across. This is what makes the size axis closeable rather
    than merely unpromising.
    """
    hit = [b for b in blocks if b["dataset"] == BOUND_BLOCK]
    assert hit, (
        f"{BOUND_BLOCK} is no longer a pure size sweep. If the dataset changed "
        "the bound must be RE-MEASURED, not edited.")
    b = hit[0]
    assert b["floor_pct"] > BAR_PCT, (
        f"{BOUND_BLOCK}'s family floor is now {b['floor_pct']:.2f}% <= "
        f"{BAR_PCT}%. The bound has expired: a monotone size exponent CAN now "
        "carry this block across the bar, and the axis reopens.")
    assert b["explained"] >= 0.10, (
        "the bound would be meaningless on a block whose exponent explains "
        "nothing — it would be the flat baseline, not the family")


def test_the_bound_is_a_bound_not_a_fit(blocks):
    """The floor must be <= the shipping error on every block: it is fitted
    in-sample on the block being scored, so it can only flatter the family.
    A floor that ever exceeds the shipping error means the scan is broken and
    'even the best exponent cannot' would be an artefact.
    """
    bad = [(b["dataset"], b["floor_pct"], b["shipping_pct"]) for b in blocks
           if b["floor_pct"] > b["shipping_pct"] + 1e-6]
    assert not bad, f"floor exceeds the shipping error on {bad}"


def test_the_best_exponents_are_reported_not_adopted():
    """§33 already refused a per-block exponent for this constant family.
    The probe must not be able to write one back into a pack.
    """
    import pathlib
    src = pathlib.Path(__file__).resolve().parents[1] / "tools" \
        / "size_family_floor_probe.py"
    text = src.read_text()
    for forbidden in ("write_text", "safe_dump", "yaml.dump"):
        assert forbidden not in text, (
            f"the probe contains {forbidden!r}: a measuring tool that can "
            "write a pack is one session away from fitting one exponent per "
            "dataset, which §33 refused")


# ── the reversal statistic must mean what it says ──────────────────────────

def test_reversal_depth_is_zero_exactly_for_monotone_series():
    assert _nonmonotone_depth([1.0, 2.0, 3.0, 4.0]) == 0.0
    assert _nonmonotone_depth([4.0, 3.0, 2.0, 1.0]) == 0.0


def test_a_rounding_level_wobble_is_not_a_shape():
    """§40: 182 then 183 is literally an interior maximum and is noise. The
    depth statistic must keep such a series below the bar.
    """
    means = [100.0, 182.0, 183.0, 182.5, 300.0]
    assert _nonmonotone_depth(means) < NONMONOTONE_MIN_DEPTH


def test_a_real_reversal_clears_the_bar():
    means = [875.0, 1828.0, 1311.0, 2223.0]   # the TEOS series, A/min
    assert _nonmonotone_depth(means) >= NONMONOTONE_MIN_DEPTH


def test_shape_mape_matches_the_scorers_free_scale_convention():
    """The probe reimplements the scorer's single free scale. If the two
    drift, every number in §54 is measured against a different metric than the
    headline median. Pin the property that defines it: scaling the measured
    series must not change the shape error.
    """
    levels = [20.0, 50.0, 100.0, 200.0]
    means = [100.0, 150.0, 210.0, 260.0]
    a = _shape_mape(levels, means, 0.5)
    b = _shape_mape(levels, [7.3 * m for m in means], 0.5)
    assert a == pytest.approx(b, rel=1e-9)
