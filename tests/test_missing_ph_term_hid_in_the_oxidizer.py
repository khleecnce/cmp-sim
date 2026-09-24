"""A missing pH term does not stay missing — it hides inside another term.

`cu_alkaline_benzenesulfonic` declared NO pH response: no peak, no width, no
floor. Its only pH-adjacent entry was `ph_ref: 4.0`, inherited from the acidic
parent and meaningless for a slurry run between pH 8.5 and 11.1.

The visible symptom was one dataset losing to its own average. US9200180B2's
pH series measures a 3.4x fall (732 -> 214 A/min from pH 6.2 to 9.9) with H2O2
and abrasive fixed; the model returned the SAME number for all five rows and
scored 51.0%, exactly the predict-the-mean baseline, because a constant is what
predicting-the-mean is.

The invisible symptom mattered more. The inherited pack sets
oxidizer_peak_wt_pct = 1.0 with the stated reason that this puts the whole
observed window on the FALLING side of the Kaufman peak — a shape chosen so
rate decreases with oxidiser. But in us9200180b2_cu_h2o2_series the pH DRIFTS
10.2 -> 8.5 as acidic H2O2 is added, while us20110165777a1 holds pH at 11.1
with KOH and measures an essentially FLAT response (160 -> 157 A/min across
1-7 wt%, the patent stating outright that "H2O2 1-7% has little effect").

Two datasets, one pack, opposite oxidiser behaviour — and the thing that
differs between them is whether pH was buffered. So part of what the pack
called an oxidiser effect was a pH effect wearing the oxidiser's label.

Adding the pH term the pack lacked, fitted to the pH series and bounded at the
lowest measured pH rather than at the free optimum (3.3, outside the data):

    us9200180b2_cu_ph_alkaline_sweep   51.0% -> 3.7%   (fitted, self-scoring)
    us9200180b2_cu_h2o2_series         51.7% -> 12.7%  (HELD OUT)
    us9200180b2_cu_benzenesulfonic     29.6% -> 26.8%  (HELD OUT)

The held-out improvements are the evidence; the fitted dataset's score is not.
Both held-out sets also stopped losing to predicting their mean.

These tests pin the finding and, more importantly, guard the failure mode: a
pack must not carry an oxidiser shape whose justification is a pH effect.
"""
from __future__ import annotations

import yaml

from cmp_sim.core.params import load_pack
from cmp_sim.core.predictive_score import (_measured, _recipe_for,
                                           score_dataset)
from cmp_sim.core.validation import dataset_paths
from cmp_sim.api import run_recipe

PACK = "cu_alkaline_benzenesulfonic"
PH_SWEEP = "us9200180b2_cu_ph_alkaline_sweep"
DRIFTING = "us9200180b2_cu_h2o2_series"
BUFFERED = "us20110165777a1_cu_h2o2_series"


def _doc(stem: str) -> dict:
    return yaml.safe_load(
        next(p for p in dataset_paths() if p.stem == stem)
        .read_text(encoding="utf-8"))


def _score(stem: str):
    return score_dataset(next(p for p in dataset_paths() if p.stem == stem))


def _value(pack, key):
    param = pack.param(key)
    return param.value if hasattr(param, "value") else param


# ---------------------------------------------------------------------------
# the pack now has a pH response, and it is a BOUND
# ---------------------------------------------------------------------------

def test_the_pack_declares_a_ph_response_at_all():
    pack = load_pack(PACK)
    for key in ("ph_peak", "ph_response_width", "ph_mechanical_floor"):
        assert _value(pack, key) is not None, f"{key} missing again"


def test_the_peak_is_pinned_to_the_lowest_measured_ph():
    """Free fitting prefers 3.3, below every polished point. Refused."""
    measured_phs = [row["overrides"]["slurry_ph"]
                    for row in _doc(PH_SWEEP)["conditions"]]
    assert _value(load_pack(PACK), "ph_peak") == min(measured_phs)


def test_the_ph_term_actually_moves_the_rate():
    """The regression that started this: a pH sweep that changed nothing."""
    doc = _doc(PH_SWEEP)
    rates = [run_recipe(_recipe_for(doc, row))["removal_rate_A_per_min"]
             for row in doc["conditions"]]
    assert max(rates) / min(rates) > 2.0, rates


# ---------------------------------------------------------------------------
# the held-out evidence
# ---------------------------------------------------------------------------

def test_the_held_out_oxidizer_series_improved():
    """Not fitted to these constants, so this is the real check."""
    score = _score(DRIFTING)
    assert score.shape_mape < 20.0, score.shape_mape
    assert score.beats_flat, "still loses to predicting its own mean"


def test_the_held_out_benzenesulfonic_series_did_not_regress():
    score = _score("us9200180b2_cu_benzenesulfonic_series")
    assert score.shape_mape < 29.6, score.shape_mape


def test_the_fitted_dataset_is_marked_as_calibration():
    """Its 3.7% must never be quoted as independent evidence."""
    assert _doc(PH_SWEEP).get("used_for_calibration") is True


# ---------------------------------------------------------------------------
# the mechanism: buffered vs drifting pH
# ---------------------------------------------------------------------------

def test_the_two_oxidizer_datasets_differ_in_whether_pH_was_buffered():
    drifting = [row["overrides"]["slurry_ph"]
                for row in _doc(DRIFTING)["conditions"]]
    buffered = [row["overrides"]["slurry_ph"]
                for row in _doc(BUFFERED)["conditions"]]

    assert max(drifting) - min(drifting) > 1.0, drifting
    assert len(set(buffered)) == 1, buffered


def test_the_buffered_dataset_measures_a_flat_oxidizer_response():
    """The patent says H2O2 1-7% barely matters; the data must agree."""
    rates = [_measured(row) for row in _doc(BUFFERED)["conditions"]]
    assert (max(rates) - min(rates)) / max(rates) < 0.05, rates
