"""The residual census must be DERIVED from the dataset files, not hardcoded.

The census exists to decide whether the 10 % target is arithmetically
reachable, so the bucket counts have to be recomputed from the corpus every
time. A hardcoded count would keep asserting an old verdict after datasets or
packs change — exactly the failure mode that let the README claim "of 49
datasets" after the corpus grew to 50.

What is pinned here is the STRUCTURE and the VERDICT, not the digits:
* every scored dataset lands in exactly one bucket,
* a dataset whose varied axes all leave the predicted rate unchanged is
  ``no_constant`` and can never be fixed by a better law,
* the improvable bucket (``responsive_miss``) is the majority of measured
  points, which is the evidence that the <=15 % allowance is NOT yet justified,
* the census measures only: it never changes a score.
"""
from __future__ import annotations

import statistics

import pytest

from cmp_sim.core.predictive_score import score_all
from tools.residual_census import BUCKETS, INERT_TOLERANCE, census, report


@pytest.fixture(scope="module")
def scores():
    return score_all()


@pytest.fixture(scope="module")
def records(scores):
    return census(scores)


def test_every_scored_dataset_gets_exactly_one_known_bucket(records, scores):
    scored = [s for s in scores if s.shape_mape is not None]
    assert len(records) == len(scored), (
        "the census must cover every scored dataset; unscorable ones are "
        "explained by the score report and are deliberately excluded")
    assert {r.dataset for r in records} == {s.dataset for s in scored}
    for rec in records:
        assert rec.bucket in BUCKETS, rec


def test_noise_floor_bucket_agrees_with_the_datasets_own_replicates(records,
                                                                   scores):
    """A dataset at its own reproducibility is irreducible, and that claim
    comes from the dataset's replicate rows, not from this test."""
    floored = {s.dataset for s in scores if s.at_noise_floor}
    assert {r.dataset for r in records if r.bucket == "noise_floor"} == floored


def test_no_constant_bucket_means_no_varied_axis_reaches_the_rate(records):
    """The defining property, re-measured: for these datasets the simulator
    returns the SAME rate at both ends of every axis the paper varied, so the
    error is a declared gap in the packs and no law can remove it."""
    group = [r for r in records if r.bucket == "no_constant"]
    assert group, "the corpus is known to contain declared-gap datasets"
    for rec in group:
        assert rec.responsive_axes == [], rec
        assert rec.axes, f"{rec.dataset} would be unscorable with no axes"
        for axis, resp in rec.response.items():
            assert resp is None or resp < INERT_TOLERANCE, (rec.dataset, axis)


def test_responsive_miss_datasets_really_do_respond(records):
    for rec in (r for r in records if r.bucket == "responsive_miss"):
        assert rec.responsive_axes, rec
        assert rec.n >= 4, rec


def test_improvable_bucket_is_the_majority_of_points(records):
    """The verdict the census was built to deliver.

    If this ever fails the argument flips: a small improvable bucket would mean
    the corpus median is dominated by irreducible noise and declared gaps, and
    the <=15 % allowance would then be justified BY THIS TABLE. Until then, 10 %
    is not blocked by arithmetic and no allowance may be claimed.
    """
    total = sum(r.n for r in records)
    improvable = sum(r.n for r in records
                     if r.bucket == "responsive_miss")
    assert improvable > total / 2, (
        f"only {improvable}/{total} points are in a bucket a better law can "
        "move; revisit the <=15 % allowance argument in STATUS.md")


def test_census_does_not_change_any_score(scores):
    """Measurement only. Running the census must leave the corpus untouched,
    otherwise validation becomes circular."""
    before = {s.dataset: s.shape_mape for s in scores}
    census(scores)
    after = {s.dataset: s.shape_mape for s in score_all()}
    assert before == after


def test_report_states_the_bucket_median_and_the_point_share(records):
    text = report(records)
    for bucket in BUCKETS:
        assert bucket in text
    improvable = [r for r in records if r.bucket == "responsive_miss"]
    assert f"{len(improvable)}/{len(records)} datasets" in text
    # the headline median in the report is the true statistical median; the
    # score report's own figure uses the UPPER of the two middle values, which
    # is the more conservative of the two and is left as the published number
    assert f"{statistics.median(r.shape for r in records):.1f}%" in text
