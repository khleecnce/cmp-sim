"""A declined axis cannot be evidence that the model responds too weakly.

`ladder_span_probe` measures, per single-axis block and with no fitting,

    span_ratio = (max/min of PREDICTED) / (max/min of MEASURED)

A population sitting below 1 would say every exponent-bearing term in the
chain is collectively too shallow -- one claim rather than eighteen, and a
licence to go derive a steepening term.  Pooled over all 20 blocks the corpus
said exactly that: geometric mean 0.80x, 15 of 20 under-spread, sign-test
p = 0.04.

**It is an artefact of counting refusals as answers.**  Seven of those blocks
sweep an axis the run explicitly DECLINED (`core.declined_axes`): the
inhibitor term refused at 10 mM, pad hardness unread by the rate, conditioner
usage hours, the pH terms gated outside their calibration window.  Such a
block predicts a *constant*, so its predicted span is 1.00x and its ratio is
bounded at or below 1 no matter what the physics does.  They cannot dissent.
Pooling them with real predictions manufactures a one-sided population out of
declared silence -- the same failure as §36 (a refusal graded as a prediction)
one level up, now in the residual diagnostics rather than the headline score.

Split out, the claim evaporates, and it evaporates under EITHER defensible
exclusion rule -- dropping only the five blocks that predict a constant
(15 blocks, geo-mean 0.93x, p = 0.30) or dropping all seven that carry a
decline (13 blocks, geo-mean 0.98x, p = 0.58).  There is no corpus-wide
under-response to derive against, and a damping or steepening term fitted to
that pooled 0.80x would have been fitted to the refusals.

A second fact fell out of writing this, and it is why the two rules differ:
**the gate fires per ROW, not per block.**  `cn109609035b` and `li2021`
decline `slurry_ph` on the rows outside their pack's calibration window and
still predict a 9.10x and 1.23x span across the rest, so "declined" and
"predicts a constant" are genuinely different properties.  The first draft of
this module assumed declined implied flat and failed on exactly that.

These tests pin the property, not the numbers:

* a block that predicts a constant must have declared its axis (§36);
* partially-declined blocks exist, so the split stays three-way;
* the verdict must hold under both exclusion rules, or it is a choice of rule;
* the split must stay non-vacuous on both sides, or the guards mean nothing.
"""

from __future__ import annotations

import math
import statistics

import pytest

from cmp_sim.core.predictive_score import score_all
from tools.ladder_span_probe import sign_test_p, span_report


@pytest.fixture(scope="module")
def blocks():
    """Every single-axis block, tagged with whether it declined its own axis."""
    out = []
    for s in score_all():
        if s.shape_mape is None:
            continue
        b = span_report(s.dataset)
        if not b:
            continue
        b["declined"] = b["axis"] in set(s.declined_axes_swept)
        # The gate can fire on SOME rows only (outside the pack's calibration
        # window), so "declined" and "predicts a constant" are different
        # facts and both are needed.
        b["flat"] = abs(b["pred_span"] - 1.0) < 1e-6
        out.append(b)
    return out


def _geometric_mean(ratios):
    return math.exp(statistics.fmean(math.log(r) for r in ratios))


def test_the_split_is_non_vacuous_on_both_sides(blocks):
    """Guard: every assertion below is meaningless if one side is empty.

    If the declined side reaches zero because every block now predicts its
    axis, that is progress -- delete this guard, do not lower it.
    """
    declined = [b for b in blocks if b["declined"]]
    predicting = [b for b in blocks if not b["declined"]]
    assert len(declined) >= 3, (
        "fewer than 3 declined single-axis blocks (%d): the artefact this "
        "module documents can no longer be demonstrated" % len(declined))
    assert len(predicting) >= 8, (
        "fewer than 8 predicting single-axis blocks (%d): the population "
        "test below has no power" % len(predicting))


def test_a_flat_block_is_always_a_declared_one(blocks):
    """A constant prediction cannot dissent -- and must say so (limits.md §36).

    The first draft of this module asserted the converse, that *declined*
    implies *flat*, and it was WRONG: two blocks decline `slurry_ph` and still
    predict a 9.10x and a 1.23x span, because the gate fires PER ROW (outside
    the pack's calibration window) rather than per block.  The true structural
    statement runs the other way, and it is the one worth pinning: a block that
    predicts a constant along its swept axis is contributing no information
    about response strength, so it had better be declared.
    """
    for b in blocks:
        if not b["flat"]:
            continue
        assert b["declined"], (
            "%s predicts a constant along %s but declares nothing: a silent "
            "flat prediction is graded as an answer (limits.md §36)"
            % (b["dataset"], b["axis"]))


def test_partial_declines_exist_and_are_not_treated_as_flat(blocks):
    """Row-level gating is real, so the probe must not assume block-level.

    Kept as a named fact because the wrong assumption is the natural one and
    it silently mislabels two pH blocks.  If partial declines disappear, the
    gate has become block-level and this guard should go.
    """
    partial = [b for b in blocks if b["declined"] and not b["flat"]]
    assert partial, (
        "no partially-declined blocks remain: the pH gate no longer fires "
        "per row, so the three-way split can collapse to two")
    for b in partial:
        assert b["pred_span"] > 1.0 + 1e-6


def test_no_under_response_signal_under_EITHER_exclusion_rule(blocks):
    """The verdict must not depend on where the exclusion line is drawn.

    Two defensible rules exist -- drop only the fully-flat blocks, or drop
    every block carrying a decline -- and the partially-declined pair sits
    between them.  A conclusion that held under one and not the other would
    be a choice of rule, not a measurement, so both are asserted.

    Asserted as a sign test, not a median: the question is "more often than
    chance?".  If this ever fails, the corpus has genuinely turned one-sided
    and a steepening term becomes admissible -- read the failure as an
    instruction to derive one (and to price it before wiring it, limits.md
    §28), not as a test to relax.
    """
    rules = {
        "drop fully-flat only": [b for b in blocks if not b["flat"]],
        "drop any declined": [b for b in blocks if not b["declined"]],
    }
    for name, grp in rules.items():
        ratios = [b["ratio"] for b in grp]
        under = sum(1 for r in ratios if r < 1.0)
        p = sign_test_p(len(ratios), under)
        assert p > 0.05, (
            "under '%s' the blocks are one-sided (%d/%d under, geo-mean "
            "%.2fx, p=%.3f): a corpus-wide response-strength term is now "
            "admissible"
            % (name, under, len(ratios), _geometric_mean(ratios), p))


def test_pooling_the_declined_blocks_is_what_created_the_signal(blocks):
    """The trap is live, so the exclusion is load-bearing rather than tidy.

    Without this, someone re-pools the two groups, sees a significant result,
    and derives a term against the refusals.  The test states the measured
    fact that the pooled population is MORE one-sided than the predicting one.
    """
    all_r = [b["ratio"] for b in blocks]
    pred_r = [b["ratio"] for b in blocks if not b["declined"]]
    assert _geometric_mean(all_r) < _geometric_mean(pred_r), (
        "pooling no longer biases the span statistic (pooled %.3fx vs "
        "predicting %.3fx); if the declined blocks have gone away, drop this "
        "module" % (_geometric_mean(all_r), _geometric_mean(pred_r)))


def test_the_sign_test_is_correct_on_known_cases():
    """The verdict above rests on this arithmetic, so it is checked directly."""
    assert sign_test_p(0, 0) == pytest.approx(1.0)
    # a fair coin, perfectly split
    assert sign_test_p(10, 5) == pytest.approx(1.0)
    # all ten one way: 2 * (1/1024)
    assert sign_test_p(10, 10) == pytest.approx(2.0 / 1024.0)
    # symmetric in k vs n-k
    assert sign_test_p(13, 3) == pytest.approx(sign_test_p(13, 10))


def test_the_null_is_reported_as_blunt_not_as_vindication(blocks):
    """A pass here means "not detected", never "the terms are correctly steep".

    limits.md §37 quantifies exactly how blunt: at n = 13 the smallest
    under-count reaching p <= 0.05 is 11 of 13, a 5.5:1 imbalance.  That
    number is asserted rather than described, because the difference between
    "no signal" and "no power to see one" is the difference between a finding
    and a comfortable silence -- and it is the sentence most likely to be
    dropped when someone later cites this null as evidence the model is fine.
    """
    n = len([b for b in blocks if not b["declined"]])
    smallest = next((k for k in range(n // 2, n + 1)
                     if sign_test_p(n, k) <= 0.05), None)
    assert smallest is not None, (
        "at n=%d no under-count at all reaches p<=0.05: this test cannot "
        "detect a one-sided corpus and must not be read as a null" % n)
    assert smallest / n >= 0.70, (
        "the sign test has become sharp (needs only %d/%d under): §37's "
        "'blunt instrument' caveat is now wrong and should be rewritten"
        % (smallest, n))
