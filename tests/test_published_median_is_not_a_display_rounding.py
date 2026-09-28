"""§57: the published median was computed on a DISPLAY rounding.

`docs/limits.md` §57. The 59th run set out to classify §56's 35
`untestable-no-sweep-in-reach` constants by perturbing each one and re-scoring
the held-out blocks in its reach. One row of that classification was
arithmetically impossible and that, not the classification, was the finding.

THE CLAIM UNDER TEST
--------------------
`Kp` multiplies every predicted rate in a block by one factor, and the shape
score fits one free multiplicative scale per block, so `shape_mape` MUST be
exactly invariant under a change of `Kp`. It was not, on `sic_ceria_h2o2`,
because `StateResult.summary()` publishes `round(rate, 1)` for human reading
and `predictive_score` read that same field. 4H-SiC polishes at a few A/min,
where 0.1 A/min is up to 1.45% per row, and the quantisation does not scale
with `Kp`.

These tests pin:

  * the arithmetic of the defect, on synthetic numbers, so the motivation
    cannot expire with the corpus;
  * the physics claim (Kp scale-invariance) on the REAL corpus, per pack;
  * that the scorer reads the exact field and that deleting it is caught;
  * the honesty-fix invariance: the published median must NOT move (§ the
    repository's standing rule -- a zero is the correct outcome and must be
    asserted, or a later session reads it as failure and "improves" it);
  * the probe's classifier, driven from synthetic input so it cannot collapse
    to one answer, plus a non-vacuity guard.
"""
from __future__ import annotations

import statistics
from pathlib import Path

import pytest
import yaml

from cmp_sim.core import predictive_score as PS
from cmp_sim.core.params import load_pack
from cmp_sim.core.validation import dataset_paths
from tools import quiet_constant_response_probe as QP
from tools import rate_quantisation_probe as RQ

ROOT = Path(__file__).resolve().parents[1]


# --------------------------------------------------------------------------
# 1. The defect as ARITHMETIC. No corpus, no model.
# --------------------------------------------------------------------------

def _shape(measured, predicted):
    denom = sum(p * p for p in predicted)
    scale = sum(m * p for m, p in zip(measured, predicted)) / denom
    return PS._mape([(m, scale * p) for m, p in zip(measured, predicted)])


def test_shape_score_is_exactly_scale_invariant_by_construction():
    """The property the whole finding rests on: one free scale per block."""
    measured = [100.0, 180.0, 260.0, 300.0]
    predicted = [3.4, 6.1, 8.8, 10.2]
    base = _shape(measured, predicted)
    for factor in (0.5, 0.8, 1.25, 3.0, 1e4):
        scaled = [p * factor for p in predicted]
        assert _shape(measured, scaled) == pytest.approx(base, abs=1e-9), (
            "the shape score must be invariant under any multiplicative "
            "rescaling of the predictions; if this fails the finding below "
            "is not a defect but a change of definition")


def test_display_rounding_breaks_that_invariance_and_its_size_tracks_magnitude():
    """Quantising the predictions re-introduces a Kp dependence.

    And the size of the breakage is set by the MAGNITUDE of the rate, which is
    why the corpus saw it on 4H-SiC (a few A/min) and not on Cu (~3000 A/min).
    """
    measured = [100.0, 180.0, 260.0, 300.0]

    def rounded_shape(predicted, factor):
        return _shape(measured, [round(p * factor, RQ.PUBLISHED_DECIMALS)
                                 for p in predicted])

    small = [3.4, 6.1, 8.8, 10.2]                  # SiC-scale rates
    large = [p * 1000.0 for p in small]            # Cu-scale rates

    small_spread = max(abs(rounded_shape(small, f) - rounded_shape(small, 1.0))
                       for f in (0.8, 1.25))
    large_spread = max(abs(rounded_shape(large, f) - rounded_shape(large, 1.0))
                       for f in (0.8, 1.25))

    assert small_spread > 0.05, (
        "a quantised prediction at SiC scale must visibly break scale "
        "invariance -- that break is the defect being recorded")
    assert large_spread < 0.01
    assert small_spread > 100.0 * large_spread, (
        "the breakage must scale with 1/rate; a size-independent reading "
        "would mean the cause is something other than the display rounding")


# --------------------------------------------------------------------------
# 2. The repair, on the REAL corpus.
# --------------------------------------------------------------------------

def test_summary_publishes_an_exact_rate_alongside_the_rounded_one():
    from cmp_sim.api import run_recipe

    out = run_recipe({
        "model": "auto",
        "wafer": {"film": "oxide", "n_radial": 11},
        "slurry": {"pack": "oxide_silica"},
        "tool": {"pressure_psi": 3.0, "rpm_platen": 60, "rpm_head": 60,
                 "time_s": 60.0},
    })
    assert "removal_rate_A_per_min" in out
    assert "removal_rate_A_per_min_exact" in out, (
        "the scorer needs a full-precision rate; deleting this field silently "
        "returns the published median to a display rounding")
    exact = float(out["removal_rate_A_per_min_exact"])
    assert round(exact, RQ.PUBLISHED_DECIMALS) == pytest.approx(
        float(out["removal_rate_A_per_min"]), abs=1e-9)


def test_scorer_reads_the_exact_field_not_the_rounded_one():
    src = (ROOT / "cmp_sim" / "core" / "predictive_score.py").read_text()
    assert "removal_rate_A_per_min_exact" in src, (
        "predictive_score must read the unrounded rate")


@pytest.mark.parametrize("pack_name", sorted({
    str((yaml.safe_load(Path(p).read_text(encoding="utf-8")) or {}).get("pack"))
    for p in dataset_paths()
} - {"None", ""}))
def test_kp_does_not_move_any_blocks_shape_score(pack_name):
    """The physics claim, per pack, on the shipping scorer.

    Derived from the corpus at test time, so a new pack is checked with no
    test edit. A pack whose `kp_m_per_pa` is absent or non-numeric is skipped
    rather than silently passing.
    """
    try:
        param = load_pack(pack_name).params.get("kp_m_per_pa")
    except Exception:                                      # noqa: BLE001
        pytest.skip(f"{pack_name} does not load")
    if param is None or not isinstance(param.value, (int, float)):
        pytest.skip(f"{pack_name} declares no numeric kp_m_per_pa")
    kp = float(param.value)

    docs = QP._docs()
    blocks = [(p, d) for (_stem, (p, d)) in sorted(docs.items())
              if str(d.get("pack") or "") == pack_name]
    checked = 0
    for path, doc in blocks:
        base, _ = QP._score_with(path, doc, None)
        if base is None:
            continue
        for factor in (0.8, 1.25):
            moved, _ = QP._score_with(path, doc, {"kp_m_per_pa": kp * factor})
            if moved is None:
                continue
            checked += 1
            assert moved == pytest.approx(base, abs=1e-6), (
                f"{path.stem}: Kp x{factor} moved shape_mape "
                f"{base:.4f} -> {moved:.4f}. Kp is purely multiplicative and "
                "the shape score fits a free scale, so any movement means the "
                "scorer is reading a quantised or otherwise non-linear rate")
    if checked == 0:
        pytest.skip(f"{pack_name} has no scorable block")


# --------------------------------------------------------------------------
# 3. The tie the same measurement exposed: beats_flat had no margin.
# --------------------------------------------------------------------------

def test_a_flat_block_reproduces_the_baseline_exactly():
    """The premise: with one free scale, a constant prediction IS the mean.

    Synthetic, so this cannot expire with the corpus.
    """
    measured = [100.0, 180.0, 260.0, 300.0]
    constant = [7.0, 7.0, 7.0, 7.0]
    flat_mape = PS._mape([(m, sum(measured) / len(measured)) for m in measured])
    assert _shape(measured, constant) == pytest.approx(flat_mape, abs=1e-12)


def test_beats_flat_requires_a_margin_so_a_tie_is_not_a_win():
    """A block that only reproduces the mean has added nothing."""
    assert PS.BEATS_FLAT_MARGIN_PP > 0, (
        "without a margin, `shape < flat` decides an exact mathematical tie on "
        "floating-point noise -- un-rounding the predicted rate flipped two "
        "blocks' published verdict while neither score moved by 1e-9")
    tie = PS.Score(dataset="t", film="oxide", n=4, shape_mape=10.0,
                   flat_mape=10.0)
    assert tie.beats_flat is False
    nudged = PS.Score(dataset="t", film="oxide", n=4,
                      shape_mape=10.0 - 1e-15, flat_mape=10.0)
    assert nudged.beats_flat is False, (
        "a 1e-15 difference is not a claim anyone should rely on")
    real = PS.Score(dataset="t", film="oxide", n=4, shape_mape=9.0,
                    flat_mape=10.0)
    assert real.beats_flat is True, (
        "the margin must not be large enough to suppress a real win")


def test_the_margin_is_far_below_every_real_gap_in_the_corpus():
    """Otherwise the margin, not the physics, is deciding the count."""
    scores = [s for s in PS.score_all()
              if s.shape_mape is not None and s.flat_mape is not None]
    gaps = [abs(float(s.flat_mape) - float(s.shape_mape)) for s in scores]
    real = [g for g in gaps if g > PS.BEATS_FLAT_MARGIN_PP]
    ties = [g for g in gaps if g <= PS.BEATS_FLAT_MARGIN_PP]
    assert real, "no block differs from its baseline at all -- check the scorer"
    assert ties, (
        "no exact tie remains, so this guard is passing vacuously; if the "
        "corpus no longer contains a flat block, say so rather than deleting "
        "the check")
    assert min(real) > 100.0 * PS.BEATS_FLAT_MARGIN_PP, (
        f"the smallest real gap ({min(real):.3e} pp) is within two orders of "
        f"the margin ({PS.BEATS_FLAT_MARGIN_PP:.0e} pp); the margin would be "
        "deciding a genuine comparison")
    assert max(ties) < 1e-9, (
        "a 'tie' larger than float noise is a real difference being suppressed")


# --------------------------------------------------------------------------
# 4. The probe that found it.
# --------------------------------------------------------------------------

def test_the_repair_did_not_move_the_published_median():
    """Zero movement is the CORRECT outcome for an honesty fix -- assert it.

    The quantisation was symmetric noise on four SiC blocks, none of which sits
    at the centre of a 48-block distribution, so the headline cannot move. A
    later session reading a zero as failure and "improving" it is the failure
    mode this pins.
    """
    scores = [s for s in PS.score_all() if s.shape_mape is not None]
    errs = sorted(float(s.shape_mape) for s in scores)
    upper_median = errs[len(errs) // 2]
    assert 18.0 <= upper_median <= 19.5, (
        f"published upper median {upper_median:.2f}% left its recorded band; "
        "if this is a real improvement, re-baseline it in STATUS.md with the "
        "measurement that moved it")


# --------------------------------------------------------------------------
# 3. The probe that found it.
# --------------------------------------------------------------------------

def test_quiet_probe_perturbs_both_directions_small_first():
    """§43: a single large one-sided factor cannot distinguish 'no wire' from
    'pushed outside the term's own validity window'."""
    factors = QP.PERTURBATIONS
    assert any(f > 1 for f in factors) and any(f < 1 for f in factors)
    assert factors[0] < 1.1, "small perturbations must be tried first"
    assert max(factors) <= 2.0, (
        "a factor large enough to leave a term's declared validity window "
        "makes a live constant look inert")


@pytest.mark.parametrize("rate_pct,shape_pp,blocks,expected", [
    (0.0, 0.0, 0, "unrunnable"),
    (0.0, 0.0, 3, "rate-inert"),
    (60.0, 0.0, 3, "scale-only"),
    (60.0, 1.3, 3, "shape-testable"),
])
def test_quiet_probe_classifier_from_synthetic_input(rate_pct, shape_pp,
                                                     blocks, expected):
    """Every class driven from synthetic input: a classifier collapsed to one
    answer passes every corpus-level assertion."""
    r = QP.QuietResponse(pack="p", constant="k", value=1.0, reach=["p"],
                         rate_pct=rate_pct, shape_pp=shape_pp,
                         runnable_blocks=blocks)
    assert r.klass == expected


def test_quiet_probe_is_read_only():
    src = (ROOT / "tools" / "quiet_constant_response_probe.py").read_text()
    for forbidden in ("write_text", "yaml.dump", "yaml.safe_dump"):
        assert forbidden not in src, (
            "a per-constant perturbation probe is one session away from "
            "becoming one fitted constant per pack; it must never write")


def test_quantisation_probe_reports_the_magnitude_that_causes_it():
    """A bare 'the median was wrong' reading is unquotable without the rate
    scale that produces it."""
    src = (ROOT / "tools" / "rate_quantisation_probe.py").read_text()
    assert "min_rate" in src and "worst_row_pct" in src
    assert "_quantisation_pct" in src


def test_quantisation_probe_reads_the_result_object_not_a_summary_field():
    """Otherwise the probe could be measuring a second rounding.

    Asserted BEHAVIOURALLY, not by grep: a grep for the attribute name passed
    while the probe still rounded the value it read, which would make the whole
    audit report "no quantisation anywhere" -- a clean bill of health that
    nothing else here would contradict. So take one SiC row, whose rates are a
    few A/min, and require the probe's reading to be strictly finer than the
    published 0.1 A/min grid.
    """
    docs = QP._docs()
    stem = "su2011_procengr_6hsic_alumina_abrasive_conc"
    assert stem in docs, "the SiC block this reading is calibrated on is gone"
    _path, doc = docs[stem]
    rows = [r for r in (doc.get("conditions") or [])
            if PS._measured(r) is not None]
    exacts = [RQ._unrounded_rate(doc, row) for row in rows]
    exacts = [e for e in exacts if e is not None]
    assert exacts, "the probe could not read a rate at all"
    grid = 10 ** (-RQ.PUBLISHED_DECIMALS)
    assert any(abs(e - round(e, RQ.PUBLISHED_DECIMALS)) > 1e-9 for e in exacts), (
        "every rate the probe read sits exactly on the published "
        f"{grid} A/min grid, so the probe is reading a rounded value and "
        "cannot measure the quantisation it exists to measure")
    assert min(exacts) < 100.0, (
        "this assertion is calibrated on a block predicting a few A/min; if "
        "the rates have moved up, recalibrate rather than relaxing the bar")
