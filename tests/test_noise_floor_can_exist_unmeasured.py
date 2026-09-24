"""A noise floor can exist and still be unmeasurable — four different states.

`Score.replicate_scatter` measures a dataset's own reproducibility from rows that
are identical in every condition. It found three datasets already at their floor
and reports blank for the other 40, where no condition repeats.

Blank is doing a lot of work in that sentence, and this test file is about not
over-reading it. Auditing every dataset's provenance prose for mentions of
averaging, replicate counts and error bars, the 49 files fall into four states —
not two:

1. REPLICATES PRESENT IN THE DATA. Identical rows, so the floor is computed.
   5 datasets. hong2007 is the clearest: three identical zero-inhibitor rows
   giving 2650 / 2400 / 1850 A/min, a 13.0% floor.

2. RATES ARE AVERAGES AND THE SCATTER IS WITHHELD. The floor exists, is
   non-zero, and cannot be recovered. du2004 states its rates are "five-run
   averages" and explicitly lists "error bars or standard deviations on the
   five-run averages" among what the paper does not report. Computing a floor of
   None here is correct; concluding the floor is zero would be wrong.

3. DIGITIZED FROM A FIGURE, with the read error quantified. This is a
   TRANSCRIPTION floor rather than a measurement one, and it is stated:
   bouvet2002_w says ~+/-3 nm/min (about 1.0% of its typical rate) and
   bouvet2002_ti says ~+/-4 nm/min (about 2.7%).

   This is where the distinction earns its keep. bouvet2002_w scores 2.3%,
   within about 2x of its 1.0% transcription floor, so there is essentially
   nothing left to win there. bouvet2002_ti scores 30.7% against a 2.7% floor —
   an order of magnitude above it, so its miss is real and worth diagnosing.
   Without the floors these two look like the same kind of number.

4. NOTHING STATED. The paper reports one rate per condition and says nothing
   about replication. The floor is simply unknown.

The rule this fixes: a blank `repl%` column means UNMEASURED, and the three
reasons it can be blank are different claims about the evidence. The reporting
change must not let a reader collapse them into "no noise here".
"""
from __future__ import annotations

import re

import yaml

from cmp_sim.core.predictive_score import score_dataset
from cmp_sim.core.validation import dataset_paths

#: rates are averages AND the source withholds the spread: floor exists,
#: unrecoverable
AVERAGED_SCATTER_WITHHELD = {"du2004_cu_h2o2_concentration_sweep"}

#: digitized from a figure with the read error stated, as (dataset, nm/min)
DIGITIZATION_FLOOR = {
    "bouvet2002_w_silica_size_sweep": 3.0,
    "bouvet2002_ti_silica_size_sweep": 4.0,
}


def _doc(stem):
    return yaml.safe_load(next(p for p in dataset_paths() if p.stem == stem)
                          .read_text(encoding="utf-8"))


def _prose(doc) -> str:
    return " ".join(str(doc.get(key, ""))
                    for key in ("notes", "source", "provenance", "method"))


def _typical_rate(doc) -> float:
    rates = [row.get("mrr_nm_per_min") or row.get("mrr_a_per_min")
             for row in doc.get("conditions") or []]
    rates = [r for r in rates if r]
    return sum(rates) / len(rates)


# ---------------------------------------------------------------------------
# state 2: the floor exists and cannot be recovered
# ---------------------------------------------------------------------------

def test_averaged_rates_with_withheld_scatter_report_no_floor_not_a_zero_floor():
    for stem in AVERAGED_SCATTER_WITHHELD:
        score = score_dataset(next(p for p in dataset_paths()
                                   if p.stem == stem))
        assert score.replicate_scatter is None, (
            f"{stem} has no identical rows, so no floor can be computed from "
            "the data")
        assert score.at_noise_floor is None, (
            "at_noise_floor must be None (unanswerable), never False, when the "
            "floor is unmeasured — False would assert the error exceeds a floor "
            "nobody measured")


def test_the_source_says_the_rates_are_averages_and_withholds_the_spread():
    """The claim above is read from the dataset, not assumed."""
    for stem in AVERAGED_SCATTER_WITHHELD:
        prose = _doc(stem)
        text = _prose(prose)
        assert re.search(r"five-run averages|averages", text, re.I), stem
        assert re.search(r"error bars?[^.]*(not|withheld)|not stated[^.]*error",
                         text, re.I), (
            f"{stem} is registered as withholding its scatter; the prose no "
            "longer says so")


# ---------------------------------------------------------------------------
# state 3: a transcription floor, which separates two similar-looking misses
# ---------------------------------------------------------------------------

def test_digitized_datasets_state_their_read_error():
    for stem, expected in DIGITIZATION_FLOOR.items():
        text = _prose(_doc(stem))
        found = re.search(r"\+/-\s*([\d.]+)\s*nm/min", text)
        assert found, f"{stem} no longer states a digitization error"
        assert abs(float(found.group(1)) - expected) < 0.51, (
            stem, found.group(1), expected)


def test_the_transcription_floor_separates_bouvet_w_from_bouvet_ti():
    """The same experiment, the same figure, two very different verdicts."""
    verdicts = {}
    for stem, read_error in DIGITIZATION_FLOOR.items():
        doc = _doc(stem)
        floor_pct = 100 * read_error / _typical_rate(doc)
        score = score_dataset(next(p for p in dataset_paths()
                                   if p.stem == stem))
        verdicts[stem] = (floor_pct, score.shape_mape)

    w_floor, w_error = verdicts["bouvet2002_w_silica_size_sweep"]
    ti_floor, ti_error = verdicts["bouvet2002_ti_silica_size_sweep"]

    # W: error within a small multiple of its transcription floor
    assert w_floor < 2.0, w_floor
    assert w_error < w_floor * 4, (w_error, w_floor)

    # Ti: an order of magnitude above its floor, so the miss is real
    assert ti_floor < 4.0, ti_floor
    assert ti_error > ti_floor * 8, (
        f"Ti scores {ti_error:.1f}% against a {ti_floor:.1f}% transcription "
        "floor; if that gap has closed, the point this test makes is gone")


# ---------------------------------------------------------------------------
# and the general rule: blank means unmeasured, in three different ways
# ---------------------------------------------------------------------------

def test_most_datasets_mention_averaging_even_without_replicate_rows():
    """Why blank must not be read as 'no noise'."""
    mentioning = 0
    for path in dataset_paths():
        text = _prose(yaml.safe_load(path.read_text(encoding="utf-8")) or {})
        if re.search(r"평균|average|error bar|replicate|반복|재현|±|\+/-",
                     text, re.I):
            mentioning += 1
    total = sum(1 for _ in dataset_paths())
    assert mentioning > total / 3, (
        f"only {mentioning}/{total} datasets mention averaging or error bars; "
        "this test exists to show that a blank repl% column is common precisely "
        "because sources withhold the spread, not because there is none")


def test_no_dataset_reports_a_floor_of_exactly_zero():
    """A computed floor of 0.0 would mean perfectly repeatable CMP. Suspect it."""
    for path in dataset_paths():
        score = score_dataset(path)
        if score.replicate_scatter is not None:
            assert score.replicate_scatter > 0.0, (
                f"{path.stem} reports a replicate scatter of exactly 0, which "
                "means its 'replicates' are duplicated rows rather than repeated "
                "measurements — check the transcription")
