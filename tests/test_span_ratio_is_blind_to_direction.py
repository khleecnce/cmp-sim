"""A span RATIO cannot see DIRECTION, and §37's reading of the corpus rests on it.

`tools/ladder_span_probe.py` reduces each single-axis block to
`span_ratio = (max/min predicted) / (max/min measured)`.  docs/limits.md §37
uses the population of those ratios to veto deriving a corpus-wide steepening
term.  The reduction is fit-free and its invariance to the scorer's one free
scale is real -- but it is a MAGNITUDE, and a magnitude cannot distinguish a
prediction that moves the right amount the right way from one that moves the
right amount BACKWARDS.

These tests pin that blindness, pin the reader that closes it
(`tools/span_direction_probe.py`), and -- most importantly -- pin the EXIT
CONDITION: today both `anti` blocks are already published as failures by
`score_report` (`beats_predicting_the_mean = False`), so the direction reader
adds a mechanism and no new defect.  An `anti` block that BEATS its own
measured mean would be a real, otherwise-unreported failure, and the test below
fails the moment one appears.

Everything is re-measured at test time.  Pinning today's counts (2 anti, 6
non-monotonic, 5 agrees) would go stale the first time a pH constant is
re-sourced, and then the temptation is to edit the number instead of re-running
the probe (the §40 failure mode).
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tools.ladder_span_probe import span_report  # noqa: E402
from tools.span_direction_probe import (  # noqa: E402
    ANTI_BAR, classify, pearson, survey,
)


@pytest.fixture(scope="module")
def blocks():
    return survey()


def test_the_survey_is_not_vacuous(blocks):
    """A probe that examines nothing passes every other test here."""
    assert len(blocks) >= 10, (
        "fewer than 10 single-axis blocks reached the direction reader; either "
        "the corpus shrank or block selection broke. A vacuous survey is "
        "indistinguishable from a deleted check.")
    predicting = [b for b in blocks if not b["declined"]]
    assert len(predicting) >= 5, (
        "the direction claim is about PREDICTING blocks; with fewer than 5 "
        f"(got {len(predicting)}) there is no population to read.")


def test_a_span_ratio_is_provably_blind_to_direction():
    """The motivating defect, proved as arithmetic rather than asserted.

    Reverse the predicted series against the same measured series: every
    predicted value still occurs, so max/min is unchanged and the span ratio is
    IDENTICAL -- while the log-space correlation flips from +1 to -1.  This is
    why §37's statistic cannot be asked a direction question, and it holds for
    any series, so no corpus change can retire it.
    """
    m = [100.0, 200.0, 400.0, 800.0]
    fwd = [10.0, 20.0, 40.0, 80.0]
    rev = list(reversed(fwd))
    span = lambda s: max(s) / min(s)          # noqa: E731
    assert span(fwd) == span(rev)
    lg = lambda s: [math.log(x) for x in s]   # noqa: E731
    assert pearson(lg(m), lg(fwd)) == pytest.approx(1.0)
    assert pearson(lg(m), lg(rev)) == pytest.approx(-1.0)
    # And the span RATIO, the actual §37 statistic, is equal for both.
    assert span(fwd) / span(m) == span(rev) / span(m)


def test_direction_is_invariant_to_the_scorers_free_scale():
    """`r_log` must be as calibration-independent as the span ratio is.

    The shape score gives each block one free multiplicative scale, which is an
    additive offset in logs.  A direction statistic that moved under it would
    be reporting the calibration, not the physics.
    """
    m = [100.0, 130.0, 90.0, 260.0]
    q = [11.0, 14.0, 9.0, 33.0]
    lg = lambda s: [math.log(x) for x in s]   # noqa: E731
    base = pearson(lg(m), lg(q))
    for k in (0.01, 3.7, 1000.0):
        assert pearson(lg(m), lg([k * x for x in q])) == pytest.approx(base)


def test_an_anti_block_that_beats_its_own_mean_would_be_unreported(blocks):
    """THE EXIT CONDITION -- this is the test that is allowed to fail.

    A block whose prediction points backwards AND which still beats predicting
    the measured mean is a failure no existing reader publishes: the median
    sees a modest shape error, `flat_prediction_census` sees a real (non-flat)
    prediction, `ladder_span_probe` sees a span ratio near 1.  Today there is
    none -- both `anti` blocks already fail `beats_predicting_the_mean`, which
    is why §45 records a mechanism rather than a defect count.
    """
    offenders = [b["dataset"] for b in blocks
                 if classify(b) == "anti" and b.get("beats_flat")]
    assert not offenders, (
        f"{offenders} predict BACKWARDS along their swept axis (negative "
        "log-correlation) while still beating their own measured mean. No "
        "other reader in this repository reports that. Do not relax this "
        "test: fix the peaked term's declared optimum, or record in "
        "docs/limits.md why the sign is right and the data wrong.")


def test_declined_blocks_are_given_no_direction_verdict(blocks):
    """§37's own rule, applied to the new reader.

    A declined axis predicts a constant for the rows it declines, so it has no
    direction.  Grading it `anti` or `agrees` would import a refusal into a
    physics statistic -- the exact mistake §36/§37 exist to prevent.
    """
    for b in blocks:
        if b["declined"]:
            assert classify(b) == "declined", (
                f"{b['dataset']} declines its swept axis but was classified "
                f"{classify(b)!r}")
    # Non-vacuity: the split must still have a declined side, or this test
    # passes by examining nothing.
    assert any(b["declined"] for b in blocks), (
        "no block declines its swept axis any more; if that is genuinely true "
        "the corpus changed fundamentally and §37 needs re-reading.")


def test_the_reader_examines_exactly_the_blocks_the_span_probe_does(blocks):
    """Two readers of one population must not drift apart on WHICH rows.

    If the direction reader selected a different set, its verdict would not be
    about §37's statistic at all -- and the discrepancy would be invisible,
    since both print plausible tables.
    """
    for b in blocks:
        ref = span_report(b["dataset"])
        assert ref is not None, (
            f"{b['dataset']} is read by span_direction_probe but REJECTED by "
            "ladder_span_probe; the two block selections have drifted.")
        assert ref["axis"] == b["axis"]
        assert ref["n"] == b["n"]
        assert ref["ratio"] == pytest.approx(b["span_ratio"], rel=1e-9)


def test_at_least_one_block_hides_a_direction_defect_behind_its_span(blocks):
    """The finding, re-measured: the blindness is REACHED in this corpus.

    Not a hypothetical. At least one block must be classified `anti` or
    `non-monotonic` -- i.e. its two spans are excursions between different
    pairs of conditions, or its prediction anti-correlates -- while its span
    ratio sits inside a band a reader would call agreement (0.5x-2x). If this
    ever fails, the corpus has become monotone-agreeing and §45 should be
    re-read rather than the band widened.
    """
    hidden = [b for b in blocks
              if classify(b) in ("anti", "non-monotonic")
              and 0.5 <= b["span_ratio"] <= 2.0]
    assert hidden, (
        "no block now hides a direction defect behind a plausible span ratio; "
        "re-measure §45 rather than editing this band.")


def test_the_anti_bar_is_a_sign_bar_not_a_fitted_threshold():
    """`ANTI_BAR` must stay at exactly zero.

    The claim is a SIGN claim -- does the prediction move with or against the
    measurement. Any non-zero bar is a fitted threshold, and this repository's
    rule is that a constant chosen to make a classification come out is a
    constant fitted to its own answer.
    """
    assert ANTI_BAR == 0.0


def test_the_classifier_can_actually_return_every_class():
    """A classifier that has collapsed to one answer passes the corpus tests.

    Deleting the `anti` branch makes every predicting block read `agrees`, and
    the corpus tests above can only notice that through a population count --
    which a future corpus change could also explain away. Drive each class
    directly from a synthetic block so the collapse is caught as a bug in the
    reader, not as a change in the data.
    """
    base = dict(dataset="synthetic", axis="slurry_ph", n=4, span_ratio=1.0)
    assert classify({**base, "declined": True, "r_log": 0.9,
                     "extremes_pair": True}) == "declined"
    assert classify({**base, "declined": False, "r_log": -0.5,
                     "extremes_pair": False}) == "anti"
    assert classify({**base, "declined": False, "r_log": 0.5,
                     "extremes_pair": False}) == "non-monotonic"
    assert classify({**base, "declined": False, "r_log": 0.5,
                     "extremes_pair": True}) == "agrees"
    assert classify({**base, "declined": False, "r_log": None,
                     "extremes_pair": True}) == "no-direction"
