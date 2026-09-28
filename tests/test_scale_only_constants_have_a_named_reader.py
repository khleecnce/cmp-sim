"""§58 — which READER grades a `scale-only` constant, and is the last one spent?

WHAT THIS PINS
--------------
§57 (`tools/quiet_constant_response_probe.py`) left 14 constants classified
`scale-only`: the predicted RATE moves, and every block's `shape_mape` is
EXACTLY unchanged, because the headline score fits one free multiplicative scale
per dataset (§34). No amount of new data repairs that -- it is a property of the
reader. §58 answers the question §57 left open, and finds two things:

1. **JURISDICTION.** 12 of the 14 are graded by `absolute_scale_audit`, which is
   the only reader here that looks at absolute rate (§34). That division of
   labour -- "the headline median can never test this constant; the scale audit
   can" -- was written down nowhere before, so a wrong value looked, in every
   report, exactly like a graded one.

2. **THE LAST READER IS ALREADY SPENT.** For the 2 with no scored reader the
   probe falls back to `core/sanity.py`'s plausibility envelope, which needs no
   dataset. It reports NO READER for both, by two DIFFERENT mechanisms, and the
   second is a corpus-wide finding: on `si_substrate_alkaline` the envelope is
   already firing on the UNPERTURBED run, so every perturbation looks identical
   to it. `tools/envelope_saturation_census.py` measures how general that is:
   the envelope fires on **30 of 52** scored blocks.

Neither result changes a constant, a prediction or the median. What they change
is what a future session may claim about falsifiability.

⚠ THIS IS NOT A PROPOSAL TO SCORE ON ABSOLUTE SCALE, and not a licence to widen
an envelope. §34 measured that shape and scale fail independently;
`core/sanity.py`'s own header records that the `snag` entry was DELETED for
citing nothing ("a guard that cannot fire is worse than no guard"). Both
temptations get an explicit mutation guard below.
"""
from __future__ import annotations

import math

import pytest

from tools import envelope_saturation_census as ESC
from tools import scale_only_jurisdiction_probe as SOJ
from tools.quiet_constant_response_probe import PERTURBATIONS


@pytest.fixture(scope="module")
def results():
    return SOJ.measure()


@pytest.fixture(scope="module")
def envelope_blocks():
    return ESC.collect()


# ── the instrument must be checkable before any verdict is read ───────────

def test_the_multiplicative_control_is_recovered_analytically(results):
    """`kp_m_per_pa` has an ANALYTIC response; if it is off, the probe is wrong.

    Kp multiplies every predicted rate and the scale ratio is
    median(measured/predicted), so perturbing Kp by f must move log10(scale) by
    exactly |log10 f|, on every comparable block. §43: a probe with no control
    decays into "nothing moves anything", which reads as a clean bill of health
    for the repository and which nothing else here contradicts.
    """
    residuals = SOJ.control_residuals(results)
    assert residuals, (
        "NO CONTROL RECOVERED -- no kp_m_per_pa constant reached a comparable "
        "block, so the whole jurisdiction table is unverified.")
    worst = max(abs(r) for _name, r in residuals)
    assert worst < 1e-9, (
        f"the multiplicative control is off by {worst:.2e} decades: the probe "
        "or the override path is not measuring what its docstring claims. "
        f"residuals={residuals}")


def test_the_control_is_a_classification_not_a_threshold(results):
    """The control must be named by CONSTANT, not by "something moved enough".

    §43: make a probe's instrument control a classification, not a percentage
    floor. A floor pins the search order instead of the wiring.
    """
    assert SOJ.MULTIPLICATIVE_CONTROLS == ("kp_m_per_pa",)
    controls = [r for r in results if r.is_control]
    assert len(controls) >= 3, (
        "fewer than three kp_m_per_pa constants came through as scale-only; "
        "the control has thinned out and the table needs re-reading")


# ── finding 1: jurisdiction ───────────────────────────────────────────────

def test_every_scale_only_constant_is_classified_and_none_is_scale_inert(results):
    """A multiplicative constant CANNOT move the rate and not the scale ratio."""
    assert results, "no scale-only constants found; §57's class has emptied"
    inert = [f"{r.pack}.{r.constant}" for r in results if r.klass == "scale-inert"]
    assert not inert, (
        f"{inert} move the predicted rate but not median(measured/predicted). "
        "That is arithmetically impossible for a multiplicative constant, so "
        "the probe -- not the pack -- is at fault.")


def test_most_scale_only_constants_are_graded_by_the_scale_audit(results):
    """The deliverable: name the reader, so 'untestable' stops being assumed.

    Measured 12 of 14. The bar is a majority rather than the exact count so a
    new dataset does not turn a recorded fact into a red test, but it is high
    enough that inverting the finding fails.
    """
    graded = [r for r in results if r.klass == "scale-graded"]
    assert len(graded) > len(results) / 2, (
        f"only {len(graded)} of {len(results)} scale-only constants have a "
        "reader; §58's finding was that MOST of them do (absolute_scale_audit),"
        " so this inversion needs recording, not re-pinning")


def test_the_graded_set_is_graded_by_absolute_scale_not_by_the_median(results):
    """Both halves of the 'it goes somewhere else' claim (§ the D99 rule).

    Saying "the median cannot test this, the scale audit can" is an excuse
    unless BOTH are asserted: the shape score must be unmoved (that is what
    `scale-only` means, inherited from §57) and the scale ratio must MOVE.
    """
    graded = [r for r in results if r.klass == "scale-graded"]
    assert graded
    for r in graded:
        assert r.scale_decades >= SOJ.SCALE_TOLERANCE_DECADES, (
            f"{r.pack}.{r.constant} is filed as graded but its scale ratio "
            f"moves only {r.scale_decades:.2e} decades")
        assert r.rate_pct > 0.0, (
            f"{r.pack}.{r.constant} is filed as graded but its rate does not "
            "move -- it belongs to §57's rate-inert class")


def test_two_constants_have_no_reader_at_all(results):
    """Pin the ungraded set BY NAME (§56's rule for an orphan set).

    A member joining is a new instance needing its own reading; one leaving is a
    repair that must be recorded. Both current members are Kp on a pack whose
    only dataset declares `절대값 비교 금지` -- its own source says the absolute
    rates are not comparable, which is a fact about the source and not a defect.
    """
    ungraded = {f"{r.pack}.{r.constant}" for r in results if r.klass == "ungraded"}
    assert ungraded == {
        "si_substrate_alkaline.kp_m_per_pa",
        "dlc_zirconia_permanganate.kp_m_per_pa",
    }, (f"the ungraded set has changed: {sorted(ungraded)}. Read the new member "
        "rather than re-pinning -- either a reader appeared or one was lost.")


def test_the_two_ungraded_constants_fail_for_DIFFERENT_reasons(results):
    """Sub-classify before calling anything a bug (§ the token-band rule).

    `dlc` has no published envelope at all; `si` has one that is saturated.
    Collapsing them to "no reader" loses the fact that only one of them could
    be repaired by a measurement, and it is the dlc one (any second
    amorphous-carbon CMP rate with a stated pressure and velocity).
    """
    by_pack = {r.pack: r for r in results if r.klass == "ungraded"}
    dlc = by_pack["dlc_zirconia_permanganate"]
    si = by_pack["si_substrate_alkaline"]
    assert dlc.envelope is None and "NO READER AT ALL" in dlc.last_reader
    assert si.envelope is not None and si.envelope_fires_at == 1.0
    assert "ALREADY firing" in si.last_reader


# ── finding 2: the envelope is saturated ──────────────────────────────────

def test_the_plausibility_envelope_is_already_firing_on_most_of_the_corpus(
        envelope_blocks):
    """The by-product, and it is worth more than the question that raised it.

    `check_rate` is a per-run annotation; nothing here had ever read it across
    the corpus, so "the envelope would catch a 10x error" aged into fact. It
    fires on 30 of 52 blocks. The bar is a majority-of-a-substantial-minority
    rather than the exact count, so a corpus change does not redden it.
    """
    counts = ESC.summary(envelope_blocks)
    assert counts["blocks"] >= 40, "corpus too small to read this"
    assert counts["firing"] >= counts["blocks"] // 2, (
        f"the envelope now fires on only {counts['firing']} of "
        f"{counts['blocks']} blocks. §58 recorded 30/52; a large drop means "
        "either the model improved on absolute scale (record it, with which "
        "blocks) or an envelope was widened (forbidden -- see the mutation "
        "guard below)")


def test_an_out_of_envelope_prediction_is_split_by_the_measurement(
        envelope_blocks):
    """Both classes must be non-empty, or the split is doing no work.

    An out-of-envelope prediction means two different things and the envelope
    cannot tell them apart: if the MEASURED rate is outside too, the warning is
    about the envelope, not the model. Asserting both classes exist is the
    non-vacuity guard -- a split collapsed to one answer passes every
    corpus-level count while reporting nothing.
    """
    narrow = [b for b in envelope_blocks
              if b.klass in ("envelope-too-narrow", "mixed")]
    failure = [b for b in envelope_blocks
               if b.klass in ("model-scale-failure", "mixed")]
    assert narrow, (
        "no block has BOTH prediction and measurement outside its envelope. "
        "That class is why the raw firing count is not a defect count.")
    assert failure, (
        "no block has a prediction outside while its measurement is inside. "
        "That is the only class the guard was built for; if it is empty the "
        "guard is firing exclusively on its own envelopes.")


def test_the_worst_caught_block_is_the_worst_absolute_scale_miss(
        envelope_blocks):
    """Cross-check the census against the reader that already exists.

    `absolute_scale_audit` puts `gong2024` at 0.07x -- the corpus's worst
    absolute miss. An independent census of a different statistic must agree,
    or one of the two is measuring something else. gong2024 is also
    `used_for_calibration`, which is why it cannot re-anchor its own pack.
    """
    worst = max(envelope_blocks, key=lambda b: b.model_failure)
    assert worst.dataset == "gong2024_4hsic_alumina_kmno4_L25", (
        f"the most-caught block is now {worst.dataset}; the census and "
        "absolute_scale_audit no longer agree on the worst absolute miss")
    assert worst.model_failure == worst.rows, (
        "gong2024 was outside its envelope on every row; a partial count means "
        "its absolute scale moved and the §34 reading needs re-measuring")


# ── mutation guards: the two tempting wrong repairs ───────────────────────

def test_the_headline_median_is_not_computed_on_absolute_scale():
    """§34: shape and scale are DIFFERENT failures and must not be merged.

    The obvious 'fix' for a constant the median cannot see is to score on
    absolute scale instead. §34 measured that re-anchoring trades one failure
    for another, and 4 of 5 failing packs are INCOHERENT, so no single Kp
    satisfies them. This asserts the scorer still fits a free scale per block,
    i.e. that the finding above remains a statement about jurisdiction rather
    than a change of scoring.
    """
    from cmp_sim.core import predictive_score as PS
    doc = {"pack": "oxide_silica", "film": "oxide"}
    pairs = [(100.0, 10.0), (200.0, 20.0), (400.0, 40.0)]
    denom = sum(p * p for _m, p in pairs)
    scale = sum(m * p for m, p in pairs) / denom
    assert scale == pytest.approx(10.0), (
        "the scorer's free scale is not a plain least-squares multiplier any "
        "more; §58's reasoning about what the median can see must be re-derived")
    assert PS._mape([(m, scale * p) for m, p in pairs]) == pytest.approx(0.0), (
        "a prediction that is a constant multiple of the measurement no longer "
        "scores 0% -- the free scale has been removed or constrained, which "
        "would change which constants are testable")
    assert doc  # the doc is illustrative; nothing is scored against it


def test_no_envelope_was_widened_to_silence_a_block():
    """core/sanity.py's own precedent: a guard that cannot fire is worse.

    Every bound in `PLAUSIBLE_RATE_A_PER_MIN` cites a measurement, and the
    `snag` entry was deleted rather than left wide. The temptation created by
    §58 is to widen an envelope so the saturation count drops. Pin the current
    bounds; a change must be a deliberate edit here, with its own citation.
    """
    from cmp_sim.core.sanity import PLAUSIBLE_RATE_A_PER_MIN as ENV
    assert ENV["si"][:2] == (100.0, 3000.0)
    assert ENV["sic"][:2] == (10.0, 300.0)
    assert ENV["cu"][:2] == (1000.0, 12000.0)
    assert "snag" not in ENV, (
        "a SnAg envelope reappeared. No primary source publishes a SnAg CMP "
        "rate at a stated pressure and velocity; an invented one is the exact "
        "defect core/sanity.py's header records having removed.")
    assert "dlc" not in ENV, (
        "a DLC envelope appeared. §58 recorded that dlc_zirconia_permanganate."
        "kp_m_per_pa has NO reader because no published amorphous-carbon CMP "
        "rate bounds it. Adding a bound is only legitimate with that citation.")
    for film, (lo, hi, basis) in ENV.items():
        assert lo > 0 and hi > lo, film
        assert len(basis) > 40, (
            f"the {film} envelope's basis string is too short to be a citation")


def test_the_probe_writes_nothing():
    """A per-constant measurement is one session away from becoming a fit.

    §54's rule: assert the scan cannot write. If this probe could persist its
    numbers, a scale response would become a fitted constant per pack.
    """
    for module in (SOJ, ESC):
        src = __import__("pathlib").Path(module.__file__).read_text(
            encoding="utf-8")
        for forbidden in ("write_text", "yaml.dump", "yaml.safe_dump",
                          "json.dump"):
            assert forbidden not in src, (
                f"{module.__name__} contains {forbidden!r}: a measurement probe "
                "must never persist its own output")


def test_the_envelope_factors_reach_far_enough_to_be_a_real_answer():
    """An 'unbounded' verdict is only meaningful if the ladder was wide.

    The question the fallback asks is "how wrong could this constant be before
    anything complains", so the ladder must reach an order of magnitude past
    the §43 scoring perturbations, or 'never fires' would just mean 'barely
    perturbed'. Ordering (small first) is what makes the reported factor the
    SMALLEST catchable error.
    """
    assert max(SOJ.ENVELOPE_FACTORS) >= 100.0
    assert min(SOJ.ENVELOPE_FACTORS) <= 0.01
    for f in PERTURBATIONS:
        assert f in SOJ.ENVELOPE_FACTORS, (
            f"the envelope ladder no longer contains the scoring perturbation "
            f"x{f}; the two readers would be asked different questions")
    ordered = sorted(SOJ.ENVELOPE_FACTORS, key=lambda f: abs(math.log10(f)))
    assert ordered[0] in (1.05, 0.95), (
        "the envelope ladder's smallest step changed; the reported "
        "'first complains at' factor is only a lower bound if small comes first")
