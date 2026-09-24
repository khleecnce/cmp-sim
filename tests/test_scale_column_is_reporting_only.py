"""The scale column is reporting-only, exactly like repl%.

Shape error asks whether the model ranks conditions correctly. Scale asks
whether it gets the rate right at all. They fail independently, and until now
the report showed only the first: `ep3161098b1_teos_silica_pressure_sweep`
prints 7.1% shape while under-predicting absolute rate by 139x, and nothing in
`cmp-sim accuracy` said so.

Adding a column must not change a score. This file pins that contract the same
way `test_replicate_column_is_reporting_only.py` does — if the corpus medians
move, adding the column changed the model, and that is a bug however good the
new numbers look.

WHAT THE COLUMN REVEALED

13 of 34 comparable datasets are off by more than 3x in absolute rate while many
of them score well on shape. The exclusions are not ours: 11 datasets' own notes
forbid absolute comparison, and they print "-" rather than a number.
"""
from __future__ import annotations

import json
import subprocess
import sys

from cmp_sim.core.predictive_score import report, score_all

#: pinned corpus figures — these must survive a reporting-only change
MEDIAN_SHAPE = 19.5
MEDIAN_LOO = 22.6
SCORED = 45
POINTS = 424


def _scores():
    return [s for s in score_all() if s.shape_mape is not None]


def test_the_medians_did_not_move():
    scores = _scores()
    shape = sorted(s.shape_mape for s in scores if s.shape_mape is not None)
    loo = sorted(s.loo_mape for s in scores if s.loo_mape is not None)
    median_shape = shape[len(shape) // 2]
    median_loo = loo[len(loo) // 2]
    assert round(median_shape, 1) == MEDIAN_SHAPE, (
        f"median shape error moved to {median_shape:.1f}% — adding a report "
        "column must not change a score")
    assert round(median_loo, 1) == MEDIAN_LOO, (
        f"median LOO moved to {median_loo:.1f}%")
    assert len(scores) == SCORED
    assert sum(s.n for s in scores) == POINTS


def test_scale_is_none_exactly_where_the_source_forbids_comparison():
    """The '-' entries must be the datasets' decision, not a silent failure."""
    from tests.test_inherited_kp_is_not_the_problem import EXCLUDED

    excluded_and_scored = {s.dataset for s in _scores()
                           if s.dataset in EXCLUDED}
    for score in _scores():
        if score.dataset in excluded_and_scored:
            assert score.scale_ratio is None, (
                f"{score.dataset} forbids absolute comparison but reports a "
                f"scale ratio of {score.scale_ratio}")
        else:
            assert score.scale_ratio is not None, (
                f"{score.dataset} reports no scale ratio, but nothing in its "
                "notes forbids absolute comparison — a silent computation "
                "failure would look exactly like this")


def test_shape_and_scale_fail_independently():
    """The finding that motivated the column, kept as a live assertion."""
    scores = {s.dataset: s for s in _scores()}
    good_shape_bad_scale = [
        s for s in scores.values()
        if s.shape_mape is not None and s.shape_mape < 15
        and s.scale_ratio is not None and not s.scale_is_calibrated]
    assert good_shape_bad_scale, (
        "no dataset scores well on shape while being badly mis-scaled; if that "
        "is genuinely fixed, this column's justification has changed")

    worst = max(good_shape_bad_scale, key=lambda s: s.scale_ratio or 0)
    assert worst.scale_ratio is not None and worst.scale_ratio > 50, (
        f"the headline case is now {worst.dataset} at {worst.scale_ratio:.1f}x")


def test_the_report_prints_the_column_and_explains_the_dashes():
    text = report(score_all())
    assert "scale" in text.split("\n")[0], "no scale column in the header"
    assert "independent of shape" in text, (
        "the report must say that scale is a failure independent of shape, or "
        "a reader will assume a good shape error means a good prediction")
    assert "forbid" in text, (
        "the report must explain that '-' is the dataset's own restriction")


def test_the_json_carries_scale_for_machine_readers():
    out = subprocess.run(
        [sys.executable, "-m", "cmp_sim.cli", "accuracy", "--json"],
        capture_output=True, text=True, check=True).stdout
    payload = json.loads(out)
    rows = {d["dataset"]: d for d in payload["datasets"]}
    ep = rows["ep3161098b1_teos_silica_pressure_sweep"]
    assert ep["scale_ratio_measured_over_predicted"] > 50
    assert ep["scale_is_calibrated"] is False
    assert ep["shape_mape_percent"] < 15, (
        "the whole point of this row: excellent shape, terrible scale")


def test_over_prediction_is_ranked_as_badly_as_under_prediction():
    """0.08x is 12x wrong; sorting on the raw ratio would hide it."""
    text = report(score_all())
    line = next((ln for ln in text.split("\n")
                 if ln.startswith("absolute rate off by")), None)
    assert line, "the report no longer names the worst-scaled datasets"
    listed = [s for s in _scores() if s.dataset in line]
    assert listed, line
    # every dataset named must be further off than the best one omitted
    def wrongness(score):
        ratio = score.scale_ratio or 1.0
        return max(ratio, 1 / ratio)

    named = max(wrongness(s) for s in listed)
    others = [s for s in _scores()
              if s.scale_ratio is not None and not s.scale_is_calibrated
              and s.dataset not in line]
    if others:
        assert named >= max(wrongness(s) for s in others), (
            "a dataset further off than the ones named was omitted from the "
            "worst-offenders list")
