"""The replicate-scatter column is REPORTING ONLY: it must not move the score.

`cmp-sim accuracy` now prints each dataset's own reproducibility next to its
shape error, and marks the rows already at that floor so they stop reading as
failures. That is a presentation change to stop a reader over-interpreting the
medians — it is emphatically NOT a scoring change.

The danger is obvious and worth a test: once a "floor" concept exists in the
scorer, it is one small step to start excusing errors with it, or to quietly
exempt floored datasets from the median. Neither happens. The median, the
leave-one-out median, the per-dataset shape errors and the beats-the-mean flag
are all computed exactly as before; `replicate_scatter` is derived from the
measured rates alone and never touches a prediction.

The one thing the display DOES change is the summary line for datasets that lose
to predicting their own mean: three of them lose because their data cannot
resolve anything finer, so listing them beside genuine failures was misleading.
`beats_flat` itself is untouched — only the printed label differs.
"""
from __future__ import annotations

import json
import subprocess
import sys

from cmp_sim.core.predictive_score import score_dataset
from cmp_sim.core.validation import dataset_paths

#: the corpus medians. They survived the film transcription unchanged, which is
#: the strongest evidence that labelling data does not model it: the corpus grew
#: from 43 to 45 scored datasets (394 -> 424 points) and the medians did not move.
#: ⚠ RE-BASELINED 2026-09-27 by the pH edge-hold fix (chemical_rate.py), which
#: is NOT a reporting change and was never claimed to be one. Holding the pH
#: Gaussian at the nearest MEASURED edge instead of extrapolating its tail moved
#: LOO 22.6 -> 21.8 and beats-the-mean 34 -> 35. The SHAPE median is unmoved at
#: 19.5 because the change is a pure per-dataset scale factor, which divides out
#: of the shape metric — that invariant is the reason this file still guards
#: something after the re-baseline.
MEDIAN_SHAPE = 18.2  # moved by the saturating-branch load-sharing fix, 2026-09-27
MEDIAN_LOO = 21.3  # moved by the W passivation threshold (physics), 2026-09-26
#: 34, not 35, since 2026-09-27 — and the missing dataset is a FLOATING-POINT
#: TIE, not a regression. `lee2021_cu_nicotinic_inhibitor` predicts its own mean
#: exactly (it is a 3-point inhibitor sweep the model responds to only through a
#: scale that the shape metric divides out), so shape == flat analytically.
#: Before the load-sharing fix the subtraction happened to land at -7.1e-15 and
#: the strict `<` counted it as a win; afterwards it lands at exactly 0.0 and it
#: does not. Nothing about that dataset's prediction changed. Recorded rather
#: than papered over, because "the count went down" would otherwise read as a
#: model regression forever — and because a comparison decided at 1e-15 is not
#: a claim anyone should rely on either way.
BEATS_MEAN = 34
SCORED = 46


def _accuracy_json():
    out = subprocess.run(
        [sys.executable, "-m", "cmp_sim.cli", "accuracy", "--json"],
        capture_output=True, text=True, check=True)
    return json.loads(out.stdout)


def test_the_medians_are_unmoved_by_the_reporting_change():
    summary = _accuracy_json()["summary"]
    assert summary["median_shape_error_percent"] == MEDIAN_SHAPE
    assert summary["median_leave_one_out_percent"] == MEDIAN_LOO
    assert summary["datasets_scored"] == SCORED


def test_beats_the_mean_is_unchanged_only_its_label_differs():
    """Floored datasets are relabelled in the printout, not re-scored."""
    summary = _accuracy_json()["summary"]
    assert summary["beat_predicting_the_mean"] == BEATS_MEAN, (
        "the beats-the-mean count must not change: a dataset at its noise floor "
        "still loses to its own mean, and we say so — we just stop calling that "
        "a model failure")


def test_scatter_is_derived_from_measurements_alone():
    """It cannot drift with the model, so it is a fixed yardstick."""
    for path in dataset_paths():
        first = score_dataset(path).replicate_scatter
        second = score_dataset(path).replicate_scatter
        assert first == second, path.stem
        if first is not None:
            assert 0 < first < 100, (path.stem, first)


def test_floored_datasets_are_still_in_the_median():
    """No dataset is exempted from the score for being noisy."""
    data = _accuracy_json()
    floored = set(data["summary"]["at_own_noise_floor"])
    assert floored, "the audit found three; if zero, the column stopped working"
    scored = {d["dataset"] for d in data["datasets"]
              if d["shape_mape_percent"] is not None}
    assert floored <= scored, (
        "a floored dataset disappeared from the scored set — noisy data must "
        "still be scored, just read differently")


def test_the_json_explains_what_blank_means():
    """The caveat has to travel with the number, not live only in prose."""
    how = _accuracy_json()["how_to_read"]
    assert "replicate_scatter" in how
    text = how["replicate_scatter"].lower()
    assert "floor" in text
    assert "unmeasured" in text, (
        "the JSON must say null means UNMEASURED; a reader who assumes null "
        "means zero will mistake an unknown floor for a perfect one")
