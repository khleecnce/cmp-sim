"""A saturating rate in pressure is FALSIFIED on this corpus.

The two-resistance form ``1/RR = 1/(k*P*V) + 1/RR_chem`` (Kaufman 1991's
passivation picture) is the standard proposal for the datasets that respond to
pressure and still miss. It costs one new per-pack constant, so the project's
methodology requires the data to demand it. They do not.

These tests re-derive the verdict from the dataset files on every run, so if a
future corpus DOES show the predicted curvature the verdict flips loudly instead
of staying buried in a comment.
"""
from __future__ import annotations

import statistics

import pytest

from tools.pressure_saturation_probe import MIN_PRESSURE_LEVELS, report, trends


@pytest.fixture(scope="module")
def rows():
    return trends()


def test_enough_pressure_ladders_exist_to_answer_the_question(rows):
    assert len(rows) >= 8, (
        "the falsification rests on many independent pressure ladders; with "
        "fewer, a null result would only mean the corpus is too thin")
    for t in rows:
        assert t.p_max > t.p_min
        assert t.n >= MIN_PRESSURE_LEVELS


def test_residual_does_not_trend_down_with_pressure(rows):
    """The sharp prediction of saturation, tested directly.

    A saturating rate would leave a linear-in-P model over-predicting at the top
    of every ladder, i.e. d ln(measured/predicted) / d ln P consistently
    negative. The observed median is ~0 and the signs are mixed.
    """
    slopes = [t.slope for t in rows]
    median = statistics.median(slopes)
    assert median > -0.25, (
        f"median residual slope {median:+.3f} is negative enough to support "
        "saturation; re-open the two-resistance law with this as evidence")
    negative = sum(1 for s in slopes if s < 0)
    assert negative < 0.8 * len(slopes), (
        f"{negative}/{len(slopes)} ladders trend down; that IS the saturation "
        "signature and the law should be reconsidered")


def test_the_scatter_is_not_a_shared_curvature_but_per_dataset(rows):
    """Sign-flipping across the SAME pressure range is the positive finding.

    Two datasets that overlap in pressure disagree on the sign of the trend, so
    whatever is wrong belongs to the dataset (scale, chemistry, tool) and not to
    the P dependence — which is why no curvature constant is added.
    """
    spread = max(t.slope for t in rows) - min(t.slope for t in rows)
    assert spread > 1.0, (
        "if every ladder agreed, a single shared curvature would be the right "
        "explanation and this whole verdict would be wrong")
    overlapping = [(a, b) for a in rows for b in rows
                   if a.dataset < b.dataset
                   and a.p_min < b.p_max and b.p_min < a.p_max
                   and a.slope * b.slope < 0]
    assert overlapping, (
        "expected at least one pair of pressure-overlapping datasets whose "
        "residual trends have OPPOSITE sign")


def test_report_records_the_rejection(rows):
    text = report(rows)
    assert "rejected" in text
    assert "RR_chem" in text
