"""Some datasets cannot be predicted better than they were measured.

STATUS listed hong2007_cu_ads_bta_polish_rate as a failure, recording 14.8% shape
error against a flat baseline of 12.6% — i.e. the model losing to predicting the
dataset's own mean. The natural reading is that the inhibitor term is broken:
hong2007 is a BTA adsorption series, so the inhibitor is the obvious suspect.

TWO THINGS TURN OUT TO BE WRONG WITH THAT.

First, the flat baseline is not 12.6%. It is 14.8% — identical to the model's, to
four decimal places. The model does not lose to the mean here, it IS the mean:
the inhibitor term is flat across these points, so the two predictions coincide.
The recorded 12.6% was stale.

Second, and the reason the tie is correct rather than a failure: three rows are
IDENTICAL in every override — same pH, oxidiser, abrasive, chelator, promoter,
flow, and inhibitor_mM = 0 — and they report:

    2650, 2400, 1850 A/min

A mean of 2300 with a mean absolute deviation of 13.0%. No model, correct or
otherwise, can score better than 13.0% on this dataset, because the measurement
does not distinguish rates more finely than that. Both 14.8% figures sit at the
noise floor.

The inhibitor points barely escape that scatter either. The zero-inhibitor
replicates span 1850-2650; the 10 mM point (2200) falls INSIDE that span, and the
0.5 mM point (1700) sits just 8% below its floor. So one of the two inhibitor
levels is indistinguishable from no inhibitor at all, and the other is marginal —
this dataset cannot establish a Langmuir coverage curve, and a term that declines
to fit one from it is behaving correctly.

This reframes `beats_flat` for such datasets: tying the mean is not evidence of a
broken term when the mean is within measurement scatter of every point.

APPLYING THE SAME TEST ACROSS THE CORPUS finds two more datasets whose error is
at or below their own replicate scatter:

    dataset                                 replicate   shape   flat
    sic2026_ceria_h2o2_ph_DOE50               38.5%      34.0%  62.5%
    us9200180b2_cu_benzenesulfonic_series     24.6%      26.8%  29.6%
    hong2007_cu_ads_bta_polish_rate           13.0%      14.8%  14.8%

The SiC DOE50 entry is the useful one: its 34.0% has been treated all session as
the SiC model's weakness, and it is in fact BETTER than the set's own
reproducibility. The pH refit earlier in this session moved it 39.3 -> 34.0,
which crossed from above the noise floor to below it — the refit was worth doing
and further refitting on this set would be fitting its noise.

Only datasets with genuine replicates can be checked this way; most of the
corpus reports one rate per condition and its noise floor is unknown. That is a
limit of the evidence, not a licence to assume the floor is zero.
"""
from __future__ import annotations

import statistics
from collections import defaultdict

import yaml

from cmp_sim.core.predictive_score import _measured, score_dataset
from cmp_sim.core.validation import dataset_paths

#: datasets whose error is at or below their own replicate scatter, so further
#: fitting on them would be fitting noise
AT_NOISE_FLOOR = {
    "hong2007_cu_ads_bta_polish_rate",
    "sic2026_ceria_h2o2_ph_DOE50",
    "us9200180b2_cu_benzenesulfonic_series",
}


def _replicate_scatter(path):
    """Mean |deviation from group mean| / group mean, over exact-duplicate rows.

    Returns None when the dataset has no repeated condition, which is the
    common case: one rate per condition means the noise floor is unmeasured.
    """
    doc = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    groups = defaultdict(list)
    for row in doc.get("conditions") or []:
        key = (tuple(sorted((k, str(v))
                            for k, v in (row.get("overrides") or {}).items())),
               row.get("pressure_psi"), row.get("rpm_platen"),
               row.get("rpm_head"))
        groups[key].append(_measured(row))

    deviations = []
    for rates in groups.values():
        rates = [r for r in rates if r]
        if len(rates) > 1:
            mean = statistics.mean(rates)
            deviations += [abs(r - mean) / mean for r in rates]
    return 100 * statistics.mean(deviations) if deviations else None


def _path(stem):
    return next(p for p in dataset_paths() if p.stem == stem)


# ---------------------------------------------------------------------------
# the specific dataset STATUS called a failure
# ---------------------------------------------------------------------------

def test_hong2007_has_triplicate_rows_that_disagree_by_13_percent():
    doc = yaml.safe_load(_path("hong2007_cu_ads_bta_polish_rate")
                         .read_text(encoding="utf-8"))
    zero_inhibitor = [_measured(row) for row in doc["conditions"]
                      if (row.get("overrides") or {}).get("inhibitor_mM") == 0.0]

    assert len(zero_inhibitor) >= 3, zero_inhibitor
    assert max(zero_inhibitor) / min(zero_inhibitor) > 1.3, (
        f"{zero_inhibitor}: the argument here rests on these replicates "
        "disagreeing substantially")

    scatter = _replicate_scatter(_path("hong2007_cu_ads_bta_polish_rate"))
    assert 10.0 < scatter < 16.0, scatter


def test_the_models_error_is_at_hong2007s_noise_floor():
    path = _path("hong2007_cu_ads_bta_polish_rate")
    scatter = _replicate_scatter(path)
    score = score_dataset(path)
    assert score.shape_mape <= scatter * 1.3, (
        f"shape {score.shape_mape:.1f}% vs replicate scatter {scatter:.1f}%; if "
        "the model has drifted well above the noise floor there IS something to "
        "fix here after all")


def test_the_model_exactly_ties_the_flat_baseline_here():
    """A correction to STATUS, which recorded flat as 12.6%.

    Both numbers are 14.8%, identical — the model and the mean are the SAME
    prediction on this dataset, which is what a bounded inhibitor term does when
    the only non-zero inhibitor points sit inside replicate scatter of the zero
    points. 'Losing to the mean' was never happening; tying it is the correct
    outcome when the data cannot distinguish the two.
    """
    path = _path("hong2007_cu_ads_bta_polish_rate")
    scatter = _replicate_scatter(path)
    score = score_dataset(path)

    assert abs(score.shape_mape - score.flat_mape) < 0.01, (
        score.shape_mape, score.flat_mape)
    # and both sit essentially at the noise floor
    assert score.flat_mape <= scatter * 1.3, (score.flat_mape, scatter)


# ---------------------------------------------------------------------------
# and the same test applied corpus-wide
# ---------------------------------------------------------------------------

def test_the_noise_floor_check_is_applied_to_every_dataset_with_replicates():
    found = set()
    for path in dataset_paths():
        scatter = _replicate_scatter(path)
        if scatter is None:
            continue
        try:
            score = score_dataset(path)
        except Exception:
            continue
        if score.shape_mape is None:
            continue
        if score.shape_mape <= scatter * 1.3:
            found.add(path.stem)

    assert found == AT_NOISE_FLOOR, (
        f"at-noise-floor set changed: {sorted(found)} vs "
        f"{sorted(AT_NOISE_FLOOR)}. A dataset entering this set should stop "
        "being refitted; one leaving it has become worth diagnosing again.")


def test_the_sic_doe_set_is_better_than_its_own_reproducibility():
    """The session spent effort on this set's 34%; it is below its noise floor."""
    path = _path("sic2026_ceria_h2o2_ph_DOE50")
    scatter = _replicate_scatter(path)
    score = score_dataset(path)
    assert scatter > 30.0, scatter
    assert score.shape_mape < scatter, (score.shape_mape, scatter)


def test_most_of_the_corpus_has_no_measurable_noise_floor():
    """Stated as a limit: one rate per condition means the floor is unknown."""
    with_replicates = sum(1 for p in dataset_paths()
                          if _replicate_scatter(p) is not None)
    total = sum(1 for _ in dataset_paths())
    assert with_replicates < total / 3, (
        f"{with_replicates}/{total} datasets have replicates; if this has grown "
        "the corpus-wide noise floor is worth reporting alongside the median")


def test_the_inhibitor_levels_barely_escape_the_replicate_scatter():
    """Why no Langmuir curve can be fitted from this dataset."""
    doc = yaml.safe_load(_path("hong2007_cu_ads_bta_polish_rate")
                         .read_text(encoding="utf-8"))
    by_level = defaultdict(list)
    for row in doc["conditions"]:
        by_level[(row.get("overrides") or {}).get("inhibitor_mM")].append(
            _measured(row))

    zero = by_level[0.0]
    assert len(zero) >= 3, zero
    low, high = min(zero), max(zero)

    # the 10 mM point lands inside the zero-inhibitor scatter
    assert low <= by_level[10.0][0] <= high, (by_level[10.0], low, high)
    # and the 0.5 mM point is only marginally below it
    assert 0.85 * low < by_level[0.5][0] < low, (by_level[0.5], low)
