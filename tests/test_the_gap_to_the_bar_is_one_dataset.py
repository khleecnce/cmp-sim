"""Limit 28: the distance to the completion bar is ONE dataset, and the term it
needs is a CURVATURE the model structurally cannot produce.

Three claims are pinned here, all re-measured at test time from the shipping
solver and the dataset files -- never from numbers copied into this file:

1.  The completion bar is a COUNTING statistic. The headline median is the
    upper median `sorted(errors)[n//2]`, which is <= the bar exactly when at
    least `n//2 + 1` datasets are <= the bar. So the remaining distance is an
    integer number of datasets, not a diffuse spread of percentage points, and
    a session that improves a dataset already above the median but still above
    the bar moves the headline by exactly zero.

2.  No shared term is missing at LOW LOADING. The tempting reading of the
    binding dataset's one bad row (1 wt%, over-predicted 57.7%) is that the
    model over-predicts dilute slurries everywhere. It does not: the
    sub-reference population is centred. That reading is rejected.

3.  What IS shared is curvature. The model's concentration response is a single
    power law, so its local log-log slope is identical at every loading
    (measured: |model curvature| < 0.01 on every ladder). The corpus's ladders
    flatten. That is a missing term with a KNOWN SIGN, which is a derivation
    target -- and specifically NOT a licence to re-fit the withdrawn
    `abrasive_conc_half_wt_pct` (limit 14's second amendment), which is why
    this file also asserts the constant is still absent.
"""

from __future__ import annotations

import pytest

from cmp_sim.core.predictive_score import score_all
from cmp_sim.core.params import available_packs, load_pack
from tools.concentration_curvature_probe import ladders, summarise
from tools.low_loading_residual_probe import collect as low_loading_rows
from tools.low_loading_residual_probe import summarise as low_loading_summary
from tools.median_crossing_probe import crossing_report

# The bar `tests/test_definition_of_done.py` enforces. Imported rather than
# retyped so a re-derived bound cannot leave this file asserting a stale one.
from tests.test_definition_of_done import COMPLETION_MEDIAN_PCT

WITHDRAWN_CONSTANT = "abrasive_conc_half_wt_pct"


@pytest.fixture(scope="module")
def scores():
    return score_all()


@pytest.fixture(scope="module")
def curvature():
    found = ladders()
    return found, summarise(found)


# ---------------------------------------------------------------- claim 1


def test_the_gap_to_the_bar_is_a_small_integer_number_of_datasets(scores):
    """Not '3.2 percentage points' -- a countable number of datasets.

    This is the claim that redirects effort: the worst-scoring dataset in the
    corpus cannot move the headline at all, while the one just above the bar
    moves it entirely.
    """
    rep = crossing_report(COMPLETION_MEDIAN_PCT, scores=scores)
    assert rep["n"] >= 40, "corpus shrank; re-derive this limit before trusting it"
    must_cross = rep["datasets_that_must_cross"]
    assert must_cross <= 3, (
        f"{must_cross} datasets must cross the {COMPLETION_MEDIAN_PCT}% bar. "
        "This limit was written when the answer was 1; if the corpus has grown "
        "or regressed enough to need several, the 'one binding dataset' reading "
        "no longer holds and the entry must be re-measured")


def test_the_binding_dataset_is_identified_and_close(scores):
    """The nearest dataset above the bar is the one that decides the headline."""
    rep = crossing_report(COMPLETION_MEDIAN_PCT, scores=scores)
    if rep["datasets_that_must_cross"] == 0:
        pytest.skip("bar already met; this limit describes the approach to it")
    assert rep["nearest"], "datasets must cross the bar but none are above it"
    name, err, _floor = rep["nearest"][0]
    headroom = rep["headroom_of_the_binding_dataset"]
    assert headroom is not None and headroom < 6.0, (
        f"the binding dataset {name} is {err:.1f}%, {headroom} points above the "
        "bar. The limit's point is that the gap is small and specific; a large "
        "headroom means the corpus changed and the entry needs re-measuring")


# ---------------------------------------------------------------- claim 2


def test_the_model_does_not_systematically_over_predict_dilute_slurries():
    """REJECTED reading, kept failing-if-wrong.

    A missing low-loading term would show as a signed residual: the dilute rows
    would be predominantly over-predicted. They are not. If a future model
    change makes them so, this fires and the rejected reading reopens.
    """
    rows = low_loading_rows()
    s = low_loading_summary(rows)
    assert s["dilute_rows"] >= 30, (
        "too few sub-reference rows to say anything; a non-vacuity guard, "
        "because a probe that collects nothing 'passes' every claim")
    over = s["dilute_over_predicting"]
    frac = over / s["dilute_rows"]
    assert 0.25 < frac < 0.75, (
        f"{over}/{s['dilute_rows']} dilute rows are over-predicted ({frac:.0%}). "
        "The corpus now has a SIGNED low-loading residual, which is a missing "
        "shared term -- the opposite of what limit 28 records. Re-open it")


# ---------------------------------------------------------------- claim 3


def test_the_model_produces_no_concentration_curvature_at_all(curvature):
    """The structural half of the claim: a power law cannot bend.

    Asserted on the SHIPPING solver's own predictions, not by reading the
    source, so any future term that does bend the response makes this fail
    loudly rather than leaving the limit quietly stale.
    """
    found, _ = curvature
    scored = [f for f in found if f["model_curvature"] is not None]
    assert len(scored) >= 8, "too few ladders scored against the model"
    worst = max(abs(f["model_curvature"]) for f in scored)
    assert worst < 0.05, (
        f"the model now bends the concentration response by {worst:+.3f} on some "
        "ladder. Limit 28 rests on it being a pure power law -- if a curvature "
        "term has landed, this entry must be rewritten around its residual")


def test_the_corpus_ladders_flatten_and_agree_on_the_sign(curvature):
    """The empirical half: several INDEPENDENT ladders curve the same way.

    One curved ladder plus one new constant is interpolation of a single
    dataset. The claim being pinned is agreement across datasets, which is what
    makes a shared term identifiable at all.
    """
    found, s = curvature
    assert s["ladders"] >= 10, "too few iso-condition ladders to claim agreement"
    assert s["flattening_datasets"] >= 3, (
        f"only {s['flattening_datasets']} distinct datasets flatten. Below three "
        "independent sources this is a property of one experiment, not a law")
    assert s["flattening"] > s["steepening"], (
        f"{s['flattening']} flattening vs {s['steepening']} steepening: the sign "
        "agreement limit 28 rests on has gone")
    assert s["median_residual_curvature"] is not None
    assert s["median_residual_curvature"] < -0.05, (
        "the residual curvature the model leaves unexplained has vanished; "
        "either a term landed or the corpus changed")


def test_the_withdrawn_saturation_constant_has_not_crept_back():
    """The exit this limit must NOT be taken through.

    Curvature with a known sign is exactly the argument that would be used to
    restore `abrasive_conc_half_wt_pct`, withdrawn on NECESSITY (limit 14,
    second amendment: NEEDED 0 / HARMFUL 1 / redundant 6). Restoring it would
    fit the curvature with the constant whose own residual was part of what
    made the axis look like a law. A derived saturation -- one whose scale
    comes from geometry the model already carries -- is admissible; this
    constant is not, and the difference is what this test defends.
    """
    carrying = []
    for name in available_packs():
        try:
            pack = load_pack(name)
        except Exception:
            continue
        param = pack.params.get(WITHDRAWN_CONSTANT)
        if param is not None and param.value is not None:
            carrying.append(name)
    assert not carrying, (
        f"{carrying} carry {WITHDRAWN_CONSTANT} again. It was withdrawn on "
        "necessity, not on score; re-adding it to explain the curvature in "
        "limit 28 re-fits the constant whose residual created the appearance "
        "of the law. Derive the saturation scale instead")
