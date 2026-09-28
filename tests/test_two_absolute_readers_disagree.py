"""§59 — the repository has TWO absolute-rate readers, and they disagree.

WHAT THIS PINS
--------------
§58 split the plausibility envelope's firing blocks into `model-scale-failure`,
`mixed`, `envelope-too-narrow` and `no-envelope`, and STATUS's 61st-run item
proposed hunting a shared condition axis across the 19 blocks of the first two
classes.  The ladder's cheaper question comes first: **is that class a new
reader, or `absolute_scale_audit` wearing a different name?**  Both look at
absolute rate; if one recovers the other, the hunt repeats §34/§47 on a
relabelled population.

Measured (`tools/envelope_jurisdiction_overlap_probe.py`): rank AUC **0.699**
between the envelope's class and `|log10 scale_ratio|`.  Neither reader is a
re-reading of the other, and neither REPORTS the other's finding.  They disagree
on **14 of 52** blocks, by three distinct mechanisms:

  `hidden-by-median` (7)  `absolute_scale_audit` reduces a block to the MEDIAN
                          of measured/predicted before comparing to SCALE_BAR.
                          A median is a reduction, so §45's question applies to
                          it: a block whose rows STRADDLE the envelope passes
                          the scale audit at 1.09x while individual predictions
                          sit outside a published plausibility bound.
  `forbidden` (3)         the dataset's own notes forbid absolute comparison, so
                          `absolute_scale_audit` correctly drops the block and
                          the ENVELOPE is the only absolute reader left here.
  `scale-only` (4)        flagged by the scale audit and never by the envelope:
                          inside the published bound and still 3x+ wrong.

The deliverable is the DECLARED division of labour, exactly as in §58: nothing
is fitted, no constant moves, and the median must not move.

⚠ NOT a proposal to score on absolute scale (§34 measured that shape and scale
fail independently), NOT a licence to widen an envelope (`core/sanity.py`'s own
header records the `snag` entry being DELETED for citing nothing), and NOT a
licence to replace the scale audit's median with a per-row statistic — the
median is the right reduction for ITS question.  All three get mutation guards.

⚠ It also CLOSES STATUS 61-1: the signed misses of the failing class are centred
(median +0.063, 10 under- vs 6 over-predicting), which is precisely the reading
§34 used to close the "one universal correction" search before it starts.
"""
from __future__ import annotations

import math

import pytest

from tools import envelope_jurisdiction_overlap_probe as P
from tools.absolute_scale_audit import SCALE_BAR


@pytest.fixture(scope="module")
def rows():
    return P.rows()


# ── the finding: the two readers are not the same reader ─────────────────────
def test_the_two_absolute_readers_are_not_recoverable_from_each_other(rows):
    """AUC near 0.5 = independent, near 1.0 = one is the other re-read."""
    sep = P.separation(rows)
    assert sep["n_failing"] >= 8 and sep["n_rest"] >= 8, (
        "non-vacuity: both sides of the comparison must be populated, or the "
        "AUC is computed on nothing and passes for free")
    assert 0.55 <= sep["auc"] <= 0.85, (
        "measured 0.699. Above ~0.85 the envelope's class would be "
        "`absolute_scale_audit` re-read per row and this whole section is "
        "redundant; below ~0.55 it would carry no relation at all, which "
        "would itself need explaining. Re-measure, do not re-pin.")


def test_the_readers_disagree_on_a_substantial_minority(rows):
    dis = P.disagreements(rows)
    total = sum(len(v) for v in dis.values())
    assert total >= 8, (
        "measured 14 of 52. If this collapses to near zero the two readers "
        "have converged and the declared division of labour below is stale.")
    for klass in ("hidden-by-median", "forbidden", "scale-only"):
        assert dis[klass], (
            "class %r is empty: it is then indistinguishable from a deleted "
            "branch, and the classifier could be collapsed to one answer "
            "without any test noticing" % klass)


# ── each mechanism is real, and is a DIFFERENT mechanism ─────────────────────
def test_hidden_by_median_blocks_really_do_pass_the_scale_audit(rows):
    """The mechanism is the scale audit's own reduction, not a bad number."""
    bar = math.log10(SCALE_BAR)
    hidden = P.disagreements(rows)["hidden-by-median"]
    for r in hidden:
        assert r.failing, r.dataset
        assert r.log_scale is not None, r.dataset
        assert abs(r.log_scale) < bar, (
            "%s: %+.3f is outside SCALE_BAR, so the scale audit DOES flag it "
            "and it is not hidden at all" % (r.dataset, r.log_scale))


def test_forbidden_blocks_are_outside_the_scale_audit_by_construction(rows):
    """`scale_ratio is None` is a dataset's refusal, never missing data.

    These blocks' own notes forbid absolute comparison (benchtop coupons,
    scaled units).  Filling the value in would be inventing a measurement; the
    correct statement is that for them the envelope is the only reader.
    """
    forb = P.disagreements(rows)["forbidden"]
    for r in forb:
        assert r.failing, r.dataset
        assert r.log_scale is None, (
            "%s is comparable, so it belongs to `hidden-by-median` or to "
            "neither class" % r.dataset)


def test_scale_only_blocks_are_inside_their_envelope(rows):
    """Flagged by scale, silent to the envelope: the opposite direction."""
    bar = math.log10(SCALE_BAR)
    only = P.disagreements(rows)["scale-only"]
    for r in only:
        assert not r.failing, r.dataset
        assert r.log_scale is not None and abs(r.log_scale) >= bar, r.dataset


def test_no_block_is_in_two_disagreement_classes(rows):
    dis = P.disagreements(rows)
    names = [r.dataset for v in dis.values() for r in v]
    assert len(names) == len(set(names)), "classes must partition"


# ── the closure of STATUS 61-1 ───────────────────────────────────────────────
def test_the_failing_population_is_centred_so_no_universal_factor_is_missing(rows):
    """§34's reading, re-measured on §58's population rather than quoted.

    A population systematically on ONE side would mean a factor is missing from
    every pack.  A centred one means no single correction exists, which closes
    the shared-axis hunt without any modelling.
    """
    import statistics
    signed = [float(r.log_scale) for r in rows
              if r.failing and r.log_scale is not None]
    assert len(signed) >= 8, "non-vacuity"
    under = sum(1 for v in signed if v > 0)
    over = len(signed) - under
    assert min(under, over) >= 0.25 * len(signed), (
        "measured 10 under- vs 6 over-predicting. If this ever becomes "
        "one-sided, a factor IS missing from every pack and the hunt STATUS "
        "61-1 proposed becomes justified — reopen it rather than editing this "
        "number.")
    assert abs(statistics.median(signed)) < 0.30, (
        "measured +0.063 (1.16x). A median far from zero is a corpus-wide "
        "offset and would be a derivation target.")


# ── mutation guards: the three temptations this section forbids ──────────────
def test_probe_never_writes(rows):
    """A measuring probe that can write is one session from fitting."""
    import pathlib
    src = pathlib.Path(P.__file__).read_text(encoding="utf-8")
    for forbidden in ("write_text", "yaml.dump", "yaml.safe_dump", ".write("):
        assert forbidden not in src, (
            "%r in the probe: it measures only and must never modify a pack"
            % forbidden)


def test_the_scale_bar_is_imported_not_repeated():
    """One number, one home — or the two readers' bars silently drift apart."""
    import pathlib
    src = pathlib.Path(P.__file__).read_text(encoding="utf-8")
    assert "from tools.absolute_scale_audit import SCALE_BAR" in src
    # An ASSIGNMENT at column 0 — not a mention inside a printed message, which
    # is the honest place to quote the bar's value to a reader of the output.
    assert not any(line.startswith("SCALE_BAR") and "=" in line
                   for line in src.splitlines()), (
        "the bar is re-declared here; it must come from absolute_scale_audit")


def test_the_probe_refuses_the_three_forbidden_repairs():
    """State the refusals where a reader of the probe's OUTPUT will see them.

    A refusal recorded only in docs/limits.md is found second.  The three:
    widening an envelope, re-scoring the headline on absolute scale, and
    replacing the scale audit's median with a per-row statistic.
    """
    text = P.report()
    assert "NOT a licence to widen an envelope" in text
    assert "does NOT justify hunting a shared condition axis" in text
    assert "not a change to either reader" in text


def test_the_median_is_still_the_right_reduction_for_its_own_question(rows):
    """`hidden-by-median` is a JURISDICTION finding, not a defect in the median.

    The scale audit asks "is this block's rate systematically wrong?", and a
    median is the correct, outlier-robust answer to that.  Asserting that its
    hidden blocks are a MINORITY keeps the finding honest: if most blocks were
    hidden, the reduction really would be the wrong one.
    """
    dis = P.disagreements(rows)
    assert len(dis["hidden-by-median"]) < 0.5 * len(rows), (
        "most blocks hidden by the median would make this a defect in the "
        "reduction rather than a division of labour")
