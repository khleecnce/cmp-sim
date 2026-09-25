"""Every number the README advertises must be computed, not remembered.

The README's badges said "688 passing" and "394 points" long after the corpus
reached 816 and 424, and its axis table still carried medians from an earlier
run (oxidizer 20.2% when the value was 22.6%). Stale published numbers are worse
than absent ones: a reader has no way to tell which are current.

This file recomputes everything the README claims and fails when the page drifts.
It also pins the distinction the page now leads with — that 19.5% is a RANKING
claim, not a rate claim — because dropping that caveat while keeping the number
would be the most misleading edit anyone could make to this project.
"""
from __future__ import annotations

import re
import statistics as st
from collections import defaultdict
from pathlib import Path

from cmp_sim.core.predictive_score import score_all
from cmp_sim.core.validation import dataset_paths

README = Path(__file__).resolve().parent.parent / "README.md"

#: README axis label -> the axis name datasets use
AXES = {
    "abrasive particle size": "abrasive_size_nm",
    "oxidizer": "oxidizer_wt_pct",
    "abrasive loading": "abrasive_wt_pct",
    "pressure": "pressure",
    "pH": "slurry_ph",
    "velocity": "velocity",
}


def _text():
    return README.read_text(encoding="utf-8")


def _scored():
    return [s for s in score_all() if s.shape_mape is not None]


def test_the_headline_totals_are_current():
    scores = _scored()
    text = _text()
    shape = sorted(s.shape_mape for s in scores if s.shape_mape is not None)
    loo = sorted(s.loo_mape for s in scores if s.loo_mape is not None)
    median_shape = shape[len(shape) // 2]
    median_loo = loo[len(loo) // 2]
    points = sum(s.n for s in scores)

    claim = (f"**Overall: median {median_shape:.1f}% shape error, "
             f"{median_loo:.1f}% leave-one-out**")
    flat = " ".join(text.split())
    assert claim in flat, f"README no longer states: {claim}"
    # the corpus SIZE is computed too — it used to be hardcoded as 49 here,
    # which meant adding a dataset silently made the README's own denominator
    # wrong while this test still passed on it.
    total = len(dataset_paths())
    assert (f"{len(scores)} of {total} datasets and {points} measured points"
            in flat), (
        f"README must say {len(scores)} of {total} datasets and {points} "
        "points")


def test_the_axis_table_matches_the_computed_medians():
    by_axis = defaultdict(list)
    for score in _scored():
        for axis in score.axes:
            if score.shape_mape is not None:
                by_axis[axis].append(score.shape_mape)

    text = _text()
    for label, axis in AXES.items():
        values = by_axis.get(axis)
        assert values, f"no dataset varies {axis} any more"
        row = re.search(rf"^\| {re.escape(label)} \| (\d+) \| \**([\d.]+)%",
                        text, re.M)
        assert row, f"README axis table has no row for {label}"
        assert int(row.group(1)) == len(values), (
            f"{label}: README says {row.group(1)} datasets, computed "
            f"{len(values)}")
        assert abs(float(row.group(2)) - st.median(values)) < 0.05, (
            f"{label}: README says {row.group(2)}%, computed "
            f"{st.median(values):.1f}%")


def test_the_scale_claim_is_current():
    scaled = [s for s in _scored() if s.scale_ratio is not None]
    calibrated = [s for s in scaled if s.scale_is_calibrated]
    off = len(scaled) - len(calibrated)
    # collapse the blockquote's line wrapping so the assertions test content,
    # not where the paragraph happens to break
    flat = " ".join(_text().split())

    assert f"**{off} of {len(scaled)} comparable datasets are off by more " \
           f"than 3×**" in flat, (
        f"README must state that {off} of {len(scaled)} datasets are off >3x")
    assert f"{len(calibrated)} of {len(scaled)} are calibrated within 3×" \
           in flat, (
        f"README must state that {len(calibrated)} of {len(scaled)} are "
        "calibrated within 3x")


def test_the_ranking_not_rate_caveat_survives():
    """The caveat must travel with the number it qualifies."""
    text = _text()
    scores = _scored()
    scaled = [s for s in scores if s.scale_ratio is not None]
    off = [s for s in scaled if not s.scale_is_calibrated]
    assert "ranking claim, not a rate claim" in text, (
        "the README's central caveat is gone: without it, '19.5% median' reads "
        "as a promise to predict absolute removal rate to 20%, which the scale "
        f"column shows is false on {len(off)} of {len(scaled)} datasets")

    # The concrete case must be CURRENT, not a remembered one. It was
    # ep3161098b1 at 139x until the pH edge-hold removed that artefact; naming
    # a stale case is exactly the staleness this file exists to prevent, so the
    # worst live case is recomputed and its magnitude looked up in the text.
    worst = max(off, key=lambda s: max(s.scale_ratio, 1 / s.scale_ratio))
    magnitude = max(worst.scale_ratio, 1 / worst.scale_ratio)
    assert f"{magnitude:.1f}×" in text, (
        f"the concrete case must be the current worst one "
        f"({worst.dataset}, {worst.shape_mape:.1f}% shape, {magnitude:.1f}x "
        "scale); an abstract caveat is easy to skim past")
    assert "re-anchor" in text.lower(), (
        "the README must tell the reader what to do about it: one calibration "
        "wafer re-anchors Kp for their tool")


def test_the_badges_are_not_stale():
    text = _text()
    scores = _scored()
    points = sum(s.n for s in scores)
    assert f"{points}%20points" in text, (
        f"the accuracy badge does not mention {points} points")
    scaled = [s for s in scores if s.scale_ratio is not None]
    calibrated = [s for s in scaled if s.scale_is_calibrated]
    assert f"{len(calibrated)}%2F{len(scaled)}%20within%203x" in text, (
        f"the scale badge should read {len(calibrated)}/{len(scaled)} within 3x")


def test_the_badge_does_not_call_the_trend_number_a_prediction():
    """Badge wording is where overclaiming is easiest and least visible."""
    text = _text()
    assert "badge/trend-19.5" in text, (
        "the accuracy badge must be labelled 'trend', not 'prediction': the "
        "19.5% does not describe absolute-rate prediction")
