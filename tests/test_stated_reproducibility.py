"""Reproducibility must be TRANSCRIBED from the source, never estimated.

The accuracy programme reached a point where the remaining question was not "what
physics is missing" but "how good can any model be here". §16 showed <=10% is
unreachable for a constant-sharing model. The other half of that claim — that 15%
is at the MEASUREMENT floor — was unproven, because the floor computed from the
data (`Score.replicate_scatter`) exists for only 6 of 46 scored datasets.

This file guards the transcription pass that answered it, and the answer is
NEGATIVE and unfavourable to us: of 17 sources searched, only four state a
quantifiable reproducibility, and the best-documented one (jani2025, an RSD of
1.5-9.5%) is BETTER than 15%. So a blanket "15% is the noise floor" cannot be
claimed from this corpus. The evidence for <=15% remains between-dataset
dispersion (§14) and the oracle bound (§16), which are different claims.

What must not be allowed to happen later:
  * a number appearing in reproducibility.yaml that is not in its own quote;
  * a `spatial_only` SD (points across one wafer) being read as a floor on
    predicting the wafer-average rate;
  * "the source averaged 5 runs" quietly becoming a floor of zero, OR a floor of
    15%;
  * this file feeding the score.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import pytest
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from cmp_sim.core.predictive_score import score_all  # noqa: E402
from cmp_sim.core.validation import dataset_paths  # noqa: E402
from tools.stated_reproducibility import (  # noqa: E402
    MEASUREMENT_KINDS, UNQUANTIFIED_KINDS, floor_percent, load_statements,
)

KNOWN_KINDS = MEASUREMENT_KINDS | UNQUANTIFIED_KINDS | {"transcription_floor"}

#: the corpus medians this pass must NOT move (it transcribes, it does not fit)
MEDIAN_SHAPE = 18.9
MEDIAN_LOO = 21.3


@pytest.fixture(scope="module")
def statements():
    return load_statements()


def test_every_entry_names_a_known_kind_and_a_real_dataset(statements):
    stems = {p.stem for p in dataset_paths()}
    for stem, entry in statements.items():
        assert stem in stems, f"{stem} is not a dataset in the corpus"
        assert entry.get("kind") in KNOWN_KINDS, (stem, entry.get("kind"))
        assert entry.get("quote"), f"{stem} has no quote — untraceable"
        assert entry.get("source"), f"{stem} has no source"


def test_every_number_in_an_entry_appears_in_its_own_quote(statements):
    """The anti-invention rule, enforced mechanically.

    A value that is not in the quote is either a typo or an estimate, and this
    corpus cannot tell those apart after the fact.
    """
    numeric_fields = ("value_percent_min", "value_percent_max",
                      "typical_percent", "value_nm_per_min", "adjusted_r2",
                      "replicates")
    # sources write small counts as words ("repeated at least three times"), so a
    # spelled-out numeral is a legitimate appearance, not a missing one
    WORDS = {1: "one", 2: "two", 3: "three", 4: "four", 5: "five", 6: "six",
             7: "seven", 8: "eight", 9: "nine", 10: "ten"}
    for stem, entry in statements.items():
        quote = str(entry.get("quote", ""))
        # the numbers a reader could check, as they would be written in prose
        present = set(re.findall(r"\d+(?:\.\d+)?", quote))
        for field in numeric_fields:
            if entry.get(field) is None:
                continue
            value = float(entry[field])
            forms = {f"{value:g}", f"{value:.1f}", str(int(value))}
            word = WORDS.get(int(value)) if value == int(value) else None
            if word and re.search(rf"\b{word}\b", quote, re.I):
                continue
            assert forms & present, (
                f"{stem}.{field} = {value} does not appear in its own quote; "
                "every transcribed number must be readable in the quoted text")


def test_spatial_scatter_never_becomes_a_floor(statements):
    """An SD across points on ONE wafer is non-uniformity, not reproducibility.

    Both kenchappa2021 and dandu2009 print an SD computed across 48 and 17 points
    on a single wafer. A model predicting the wafer-average rate is not bounded by
    it, and kenchappa2021 scores 42.8% — reading its within-wafer SD as a floor
    would excuse the single largest miss in the corpus with the wrong statistic.
    """
    spatial = [s for s, e in statements.items() if e.get("kind") == "spatial_only"]
    assert spatial, "the distinction this test protects has disappeared"
    for stem in spatial:
        lo, hi, _ = floor_percent(stem, statements[stem])
        assert lo is None and hi is None, (
            f"{stem} is a within-wafer SD; it must yield NO floor")


def test_withheld_scatter_yields_neither_zero_nor_fifteen(statements):
    """"Averaged 5 runs, spread not printed" is a third answer, not a floor."""
    withheld = [s for s, e in statements.items()
                if e.get("kind") == "replicated_scatter_withheld"]
    assert withheld, "state 2 has vanished from the transcription"
    for stem in withheld:
        entry = statements[stem]
        assert entry.get("replicates", 0) >= 2, (
            f"{stem} claims replication; it must say how many runs")
        lo, hi, _ = floor_percent(stem, entry)
        assert lo is None and hi is None, (
            f"{stem}'s floor is unrecoverable; producing a number for it would "
            "be an estimate")


def test_the_miranda_pure_error_reproduces_the_printed_adjusted_r2(statements):
    """The one derived floor must be checkable ARITHMETICALLY, not trusted.

    Inputs, all printed: a 2^2 factorial with 3 replicates (n=12), four cell
    means (243 / 1743 / 2908 / 1953 A/min) and adjusted R^2 = 0.69. The recovered
    SS_error must, fed back through the definition of adjusted R^2, return 0.69.
    """
    entry = statements["miranda2004_cu_ph_h2o2_2x2"]
    lo, hi, kind = floor_percent("miranda2004_cu_ph_h2o2_2x2", entry)
    assert kind == "derived_pure_error"
    assert lo is not None and hi is not None

    means = [24.3, 174.3, 290.8, 195.3]  # nm/min, as the dataset file holds them
    r, n, p = 3, 12, 4
    grand = sum(means) / len(means)
    ss_between = r * sum((y - grand) ** 2 for y in means)
    sd = lo * grand / 100.0            # invert the reported percentage
    ss_error = sd ** 2 * (n - p)
    ss_total = ss_between + ss_error
    adj_r2 = 1 - (ss_error / (n - p)) / (ss_total / (n - 1))
    assert abs(adj_r2 - 0.69) < 5e-3, (
        f"round-trip adjusted R^2 = {adj_r2:.4f}, the source prints 0.69")

    # and the band from the p = 3 / p = 4 ambiguity must be narrow enough to be
    # a usable statement rather than a shrug
    assert hi - lo < 3.0, (lo, hi)


def test_at_least_one_source_documents_a_floor_far_above_fifteen_percent(statements):
    """The reason a blanket floor cannot be assumed in EITHER direction.

    miranda2004's own replicate scatter recovers to ~37%: a 2x2 with 3 replicates
    whose cell means span 12x, on thick electroplated Cu. Some published CMP
    experiments really are that noisy — which is why the floor must be read per
    source and not assigned.
    """
    lo, hi, _ = floor_percent("miranda2004_cu_ph_h2o2_2x2",
                              statements["miranda2004_cu_ph_h2o2_2x2"])
    assert lo is not None and lo > 25.0, lo


def test_the_best_documented_floor_refutes_a_blanket_fifteen_percent(statements):
    """The unfavourable finding, pinned so it cannot quietly disappear.

    jani2025 is the only corpus source that publishes a replicate RSD for every
    condition of a designed experiment. Its ceiling is 9.5%. Any future claim that
    "15% is the measurement floor" must therefore exclude this dataset explicitly
    or be wrong.
    """
    for stem in ("jani2025_cu_h2o2_acidic_chelator",
                 "jani2025_cu_rsm_composition_heldout"):
        entry = statements[stem]
        assert entry["kind"] == "replicate_rsd"
        _, hi, _ = floor_percent(stem, entry)
        assert hi is not None and hi < 15.0, (
            f"{stem} states a reproducibility of at most {hi}%, which is better "
            "than 15%; a blanket 15% floor cannot cover it")

    # and the held-out half of that same paper scores 51.2% — five times its own
    # stated floor. That error is REAL, not noise, and must stay legible as such.
    scores = {s.dataset: s for s in score_all()}
    held = scores["jani2025_cu_rsm_composition_heldout"]
    assert held.shape_mape is not None and held.shape_mape > 30.0, (
        "if this dataset's error has fallen, re-read docs/limits.md §17: the "
        "argument there rests on it being far above its measured floor")


def test_an_absolute_uncertainty_is_converted_per_row_not_against_the_mean(
        statements):
    """+/-14 nm/min on rates spanning 15x is not one percentage.

    Averaging sigma/rate over the rows (as MAPE averages) gives a materially
    larger floor than sigma/mean_rate, because the slow rows dominate. The
    conservative-looking choice here is the CORRECT one: it must match the way
    the error it is compared against is averaged.
    """
    stem = "ihnfeldt2008_cu_alumina_ph_oxidizer_chelator"
    lo, hi, kind = floor_percent(stem, statements[stem])
    assert kind == "absolute_uncertainty"
    assert lo == hi and lo is not None

    path = next(p for p in dataset_paths() if p.stem == stem)
    doc = yaml.safe_load(path.read_text(encoding="utf-8"))
    rates = [r["mrr_nm_per_min"] for r in doc["conditions"]]
    per_row = 100.0 * sum(14.0 / r for r in rates) / len(rates)
    against_mean = 100.0 * 14.0 / (sum(rates) / len(rates))
    assert abs(lo - per_row) < 0.05, (lo, per_row)
    assert per_row > against_mean * 1.2, (
        "the two conventions no longer differ materially, so this test no longer "
        "protects anything — check the dataset's rate spread")


def test_transcribing_reproducibility_does_not_move_the_score():
    """Reporting only. If this file could move a median, it could be fitted."""
    scores = [s for s in score_all() if s.shape_mape is not None]
    shape = sorted(s.shape_mape for s in scores)[len(scores) // 2]
    loo = sorted(s.loo_mape for s in scores)[len(scores) // 2]
    assert abs(shape - MEDIAN_SHAPE) < 0.05, (shape, MEDIAN_SHAPE)
    assert abs(loo - MEDIAN_LOO) < 0.05, (loo, MEDIAN_LOO)


def test_the_search_was_wider_than_the_sources_that_help(statements):
    """Selection discipline: silence is recorded, not skipped.

    If only the sources that STATE a floor had been entered, the file would be
    four entries long and the implied conclusion ("floors are large") would be an
    artefact of who was asked. Most entries must therefore be the unhelpful kinds.
    """
    silent = sum(1 for e in statements.values()
                 if e.get("kind") in UNQUANTIFIED_KINDS)
    quantified = sum(1 for e in statements.values()
                     if e.get("kind") in MEASUREMENT_KINDS)
    assert silent > quantified, (
        f"{quantified} quantified vs {silent} silent — a transcription pass that "
        "found a floor more often than not would mean the search was steered")
