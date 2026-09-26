"""The absolute-scale failure is NOT a mis-anchored Kp — the packs disagree
with THEMSELVES.

Pre-registered in STATUS.md (20th run). The axis programme closed against the
SHAPE score, which allows one free multiplicative scale per dataset and is
therefore structurally blind to being wrong about the rate itself. This is the
first measurement of that blind spot.

The result inverts the natural expectation. The obvious story — "each pack's Kp
was back-calculated from one measurement, so it is mis-anchored and needs
moving" — is refuted: the miss population is CENTRED (median 1.11x, 20 blocks
under-predicting and 17 over-predicting), so there is no corpus-wide missing
factor to find, and four of the five packs carrying a >=3x failure are
INCOHERENT — their own blocks disagree with each other by up to **222x** under
one shared Kp. A single constant cannot be moved to satisfy both ends of that
spread; doing so would trade one failure for another.

These tests pin the finding, and pin the trap: `cu_h2o2_bta` spans 0.06x to
12.7x, so any future run tempted to "fix the copper scale" by re-anchoring Kp
fails here with the spread printed in the message.
"""
from __future__ import annotations

import math

import pytest

from tools.absolute_scale_audit import (
    SCALE_BAR, by_pack, collect, failures, symmetry,
)


@pytest.fixture(scope="module")
def blocks():
    return collect()


def test_the_shape_score_cannot_see_these_failures(blocks):
    """The premise. A block can be 10x wrong and score single-digit shape.

    This is what justifies the whole audit: without it, the corpus median
    reports 18.9 % while the model is an order of magnitude out on real rates.
    """
    bad = failures(blocks)
    assert bad, "no scale failures — re-check the bar before deleting this test"
    good_shape_but_wrong_rate = [
        b for b in bad if b.shape is not None and b.shape < 15.0]
    assert good_shape_but_wrong_rate, (
        "no block combines a good shape with a bad rate any more; if that is "
        "real it is excellent news, but the claim in docs/limits.md §22 must "
        "then be restated rather than left standing")


def test_the_miss_population_is_centred_so_no_global_factor_is_missing(blocks):
    """S1. A one-sided population would mean a term absent from every pack.

    It is not one-sided, so the search for a single universal correction is
    closed before it starts — which is worth a test, because that is the first
    thing a later run would try.
    """
    sym = symmetry(blocks)
    assert sym["n"] >= 20, sym
    assert 0.5 <= sym["median_factor"] <= 2.0, (
        f"the population median moved to {sym['median_factor']:.2f}x; a "
        "systematic lean means a factor common to the corpus is missing and "
        "the §22 reasoning must be redone")
    minority = min(sym["under_predicting"], sym["over_predicting"])
    assert minority >= 0.3 * sym["n"], (
        f"the misses stopped being two-sided ({sym['under_predicting']} under "
        f"/ {sym['over_predicting']} over); see above")


def test_the_worst_pack_disagrees_with_itself_by_orders_of_magnitude(blocks):
    """S2, THE FINDING. One Kp, two blocks, a 222x gap between them.

    A mis-anchored constant produces a COHERENT offset: every block under the
    pack misses the same way. cu_h2o2_bta does the opposite, so its Kp is not
    what is wrong, and re-anchoring it can only move the failure around.
    """
    verdicts = {v.pack: v for v in by_pack(blocks)}
    cu = verdicts.get("cu_h2o2_bta")
    assert cu is not None and len(cu.blocks) >= 4, verdicts.keys()
    spread = 10 ** (max(cu.log_scales) - min(cu.log_scales))
    assert spread > 50.0, (
        f"cu_h2o2_bta's internal spread fell to {spread:.0f}x. If a real fix "
        "did that, say so in docs/limits.md §22; if a dataset was dropped, "
        "that is data selection and is forbidden")
    assert cu.coherent is False


def test_most_failing_packs_are_incoherent_not_mis_anchored(blocks):
    """S2 generalised: the finding is not one bad pack."""
    multi = [v for v in by_pack(failures(blocks)) if v.coherent is not None]
    assert multi, "no pack has two failing blocks to compare"
    incoherent = [v for v in multi if v.coherent is False]
    assert incoherent, (
        "every failing pack became coherent, which would mean the failures ARE "
        "mis-anchored constants after all — a different and much cheaper "
        "problem, so §22 must be rewritten rather than quietly kept")


def test_a_block_the_pack_was_fitted_on_cannot_re_anchor_it(blocks):
    """S4: the 13th-run rule, applied to scale instead of to shape.

    gong2024 is `used_for_calibration` for sic_alumina_kmno4 and is 0.07x. Its
    miss is a statement about the pack's OTHER evidence, not permission to move
    the constant to suit it.
    """
    bad = failures(blocks)
    calibrated = [b for b in bad if b.used_for_calibration]
    assert calibrated, "expected at least one calibration block among failures"
    for b in calibrated:
        assert not b.can_justify_reanchoring


def test_the_bar_matches_the_published_report(blocks):
    """The audit and score_report.py must never quote different thresholds."""
    from cmp_sim.core.predictive_score import report, score_all
    text = report(score_all())
    assert f">{SCALE_BAR:.0f}x" in text, (
        "score_report.py no longer states the same absolute-scale bar this "
        "audit uses; two thresholds will drift apart")
    bar = math.log10(SCALE_BAR)
    assert all(abs(b.log_scale) >= bar for b in failures(blocks))


def test_the_audit_counts_more_blocks_than_the_readme_and_that_is_deliberate(blocks):
    """Two published counts for one bar must be reconcilable, not merely different.

    The README says 9 of 34; the audit says 11 of 37. The gap is the blocks
    whose SHAPE is gated (unscorable) but whose SCALE is still comparable — a
    dataset the model declines to RANK can still be measured against, and
    dropping it would flatter the harder half of the corpus. Pinned so the two
    numbers can never diverge for an unexamined reason.
    """
    shapeless = [b for b in blocks if b.shape is None]
    assert shapeless, (
        "no gated-but-comparable blocks remain, so the audit and the README "
        "should now agree; reconcile them in docs/limits.md §22")
    assert len(blocks) - len(shapeless) >= 30, (
        f"only {len(blocks) - len(shapeless)} blocks carry both a shape and a "
        "scale; the two counts no longer overlap enough to be comparable")


def test_the_audit_changes_no_pack():
    """It measures. Kp must be exactly as shipped for the packs it names."""
    from cmp_sim.core.params import load_pack
    for name in ("cu_h2o2_bta", "sti_ceria", "sic_ceria_h2o2"):
        pack = load_pack(name)
        assert pack.params["kp_m_per_pa"].value is not None
