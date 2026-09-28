"""The alkaline oxidiser gate's MECHANISM claim is refuted in MAGNITUDE, and
its own "no such sweep exists" exit condition had already fired (limits §51).

This is the THIRD instance of the §50 class: a single-sourced refusal whose
stated reason is a claim about the WORLD rather than a property of the model's
function family.  §38/§40 was the PSD-width SIGN, §50 was the ceria pH SHAPE,
this one is the alkaline Cu oxidiser MAGNITUDE.

What is asserted here, and why each assertion exists:

  1. The gate's VALUE is untouched.  A refuted justification is not a licence
     to refit (§50's rejected list).  If a later session moves the window, this
     fails.

  2. The mechanism's magnitude does NOT transfer.  Measured on the two
     alkaline Cu/BTA ladders already in this corpus, against Miranda's own
     alkaline leg.  The numbers are READ FROM the evidence file, never pinned
     as literals -- a better transcription must tighten this automatically
     (the §50 lesson about hard-coded bars).

  3. The SIGN still does transfer, and the gate's actual argument (two legs,
     opposite signs, one single-signed constant) is untouched.  Asserting the
     refutation without this control would license deleting the gate.

  4. CONTROL / non-vacuity: the probe must still FIND both ladders.  If the
     enumeration silently empties, every assertion above passes for free and is
     indistinguishable from a deleted test.

  5. EXPIRY: neither ladder is admissible as an anchor today, for reasons the
     evidence file names.  When one becomes admissible -- an independent,
     pH-fixed alkaline Cu/BTA sweep -- this fails, and the gate should be
     reconsidered rather than the prose edited.

  6. The superseded sentence is KEPT, marked, not deleted.  Deleting it
     restores the undetectable state.

MUTATION-GUARD NOTE (a real false negative found while validating this file).
A YAML folded block (`note: >`) WRAPS its lines, so the sentence under test is
split across two physical lines on disk while the LOADED note is one line.  The
first mutation attempt replaced the literal substring on disk, deleted only the
unwrapped copy, and the deletion test passed -- a mutation that appears not to
bite because the mutation itself was incomplete, not because the test is weak.
Assertions here therefore run on the note as the PARAMETER LOADER returns it,
never on the file text; and any future mutation check of a `note:` must match
across newlines (`re.sub(r"no\\s+sweep\\s+has\\s+been\\s+located", ...)`).
"""
from __future__ import annotations

import math
from pathlib import Path

import pytest
import yaml

from cmp_sim.core.params import load_pack

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "research" / "alkaline_oxidizer_sign_transfer.yaml"
DATASETS = ROOT / "cmp_sim" / "data" / "validation" / "datasets"
PROBE = ROOT / "tools" / "alkaline_oxidizer_sign_transfer_probe.py"

GATE_PACK = "cu_h2o2_bta"
GATE_KEY = "oxidizer_ph_window"


@pytest.fixture(scope="module")
def ev():
    assert EVIDENCE.exists(), (
        f"{EVIDENCE.name} is the evidence behind this refutation; without it "
        "the assertions below are unquotable")
    return yaml.safe_load(EVIDENCE.read_text())


def _loglog_slope(levels, rates):
    pts = [(c, r) for c, r in zip(levels, rates) if c > 0 and r > 0]
    assert len(pts) >= 3, "a slope needs at least three positive points"
    xs = [math.log(c) for c, _ in pts]
    ys = [math.log(r) for _, r in pts]
    n = len(xs)
    mx, my = sum(xs) / n, sum(ys) / n
    sxx = sum((x - mx) ** 2 for x in xs)
    sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    return sxy / sxx


# ── 1. the decision is untouched ────────────────────────────────────────────

def test_gate_value_is_unchanged_by_the_refutation():
    """A refuted MECHANISM is not a licence to refit the gate. The decision
    rests on the two legs having opposite signs, not on the magnitude."""
    p = load_pack(GATE_PACK).params[GATE_KEY]
    assert [float(x) for x in p.value] == [2.0, 6.25]
    assert p.confidence == "literature"
    assert p.source and "Miranda" in p.source


# ── 2. the magnitude does not transfer ──────────────────────────────────────

def test_mechanism_magnitude_does_not_transfer_to_either_alkaline_ladder(ev):
    """Miranda's alkaline leg is an order of magnitude steeper than both
    independent alkaline Cu/BTA ladders. Slopes are RECOMPUTED from the
    measured rows in the evidence file, not pinned as literals."""
    mech = float(ev["mechanism_source"]["alkaline_leg"]["loglog_slope"])
    assert mech < -2.0, "the mechanism's own leg must be steeply negative"

    seen = 0
    for row in ev["transfer_test"]:
        slope = _loglog_slope(row["levels_wt_pct"], row["measured_nm_per_min"])
        # the file's recorded slope must match what its own rows give
        assert slope == pytest.approx(float(row["loglog_slope"]), abs=0.01), (
            f"{row['dataset']}: the recorded slope disagrees with the "
            "measured rows in the same file")
        # and it must be an order of magnitude shallower than the mechanism
        assert abs(slope) < abs(mech) / 5.0, (
            f"{row['dataset']}: slope {slope:+.2f} is no longer distinguishable "
            f"from the mechanism's {mech:+.2f} -- re-measure before trusting "
            "the refutation")
        seen += 1
    assert seen >= 2, (
        "the refutation rests on TWO independent alkaline ladders; with fewer "
        "it is single-sourced again, which is the very thing §50 warns about")


def test_both_ladders_carry_an_inhibitor_which_is_the_gated_regime(ev):
    """A ladder without an inhibitor would be a different chemistry and could
    not speak to this pack's regime at all."""
    for row in ev["transfer_test"]:
        assert row["inhibitor_declared"] is True, (
            f"{row['dataset']} must declare an inhibitor to be evidence about "
            "a BTA-bearing pack")


# ── 3. the sign still transfers (control) ───────────────────────────────────

def test_the_sign_still_transfers_so_the_gate_is_not_deleted(ev):
    """CONTROL. Both ladders must still be NEGATIVE. If one went positive the
    refutation would be about the sign, not the magnitude, and the gate's
    opposite-signs argument would itself be in question."""
    for row in ev["transfer_test"]:
        slope = _loglog_slope(row["levels_wt_pct"], row["measured_nm_per_min"])
        assert slope <= 0.0, (
            f"{row['dataset']}: alkaline slope {slope:+.2f} is POSITIVE -- the "
            "gate's opposite-signs argument needs re-examination, not this test")
    assert "opposite" in ev["what_this_does_NOT_change"].lower()


# ── 4. non-vacuity: the ladders must still be found ─────────────────────────

def test_the_corpus_still_holds_both_alkaline_ladders(ev):
    """Non-vacuity. Every assertion above is about datasets that must actually
    exist and still be alkaline oxidiser ladders. If the enumeration empties,
    this test passes for free -- so enumerate it here, from the real files."""
    hi = float(load_pack(GATE_PACK).params[GATE_KEY].value[1])
    found = {}
    for path in sorted(DATASETS.glob("*.yaml")):
        doc = yaml.safe_load(path.read_text())
        if not isinstance(doc, dict) or doc.get("film") != "cu":
            continue
        levels, phs = set(), []
        for c in doc.get("conditions") or []:
            ov = (c or {}).get("overrides") or {}
            if "oxidizer_wt_pct" not in ov or c.get("mrr_nm_per_min") is None:
                continue
            levels.add(float(ov["oxidizer_wt_pct"]))
            if ov.get("slurry_ph") is not None:
                phs.append(float(ov["slurry_ph"]))
        if len(levels) >= 3 and phs and min(phs) > hi:
            found[path.stem] = sorted(levels)

    named = {row["dataset"] for row in ev["transfer_test"]}
    assert named <= set(found), (
        "an alkaline ladder named by the evidence file is no longer found by "
        f"the corpus scan: missing {sorted(named - set(found))}")
    assert len(found) >= 2, (
        "fewer than two alkaline Cu oxidiser ladders remain; the refutation is "
        "no longer supported by the corpus it was measured on")


# ── 5. expiry ───────────────────────────────────────────────────────────────

def test_no_alkaline_ladder_is_admissible_as_an_anchor_yet(ev):
    """EXPIRY. Today neither ladder can anchor an alkaline oxidiser constant
    for this pack. When one can -- independent, pH held fixed, admissible --
    this fails, and the GATE should be reconsidered, not this prose edited."""
    hi = float(load_pack(GATE_PACK).params[GATE_KEY].value[1])
    admissible = []
    for row in ev["transfer_test"]:
        ph = row["ph"]
        ph_fixed = not isinstance(ph, list) or abs(ph[1] - ph[0]) <= 0.3
        own_pack = row["pack_scored_under"] == GATE_PACK
        held_out = not row["used_for_calibration"]
        slope = _loglog_slope(row["levels_wt_pct"], row["measured_nm_per_min"])
        responds = abs(slope) >= 0.15
        lo_ph = ph[0] if isinstance(ph, list) else ph
        if ph_fixed and own_pack and held_out and responds and lo_ph > hi:
            admissible.append(row["dataset"])
    assert not admissible, (
        f"{admissible} is now an admissible alkaline anchor for {GATE_PACK}. "
        "The gate's CORRECTED exit condition has fired: fit an alkaline-branch "
        "oxidiser constant and replace the gate with a prediction, instead of "
        "relaxing this test.")
    assert "CORRECTED exit condition" in \
        load_pack(GATE_PACK).params[GATE_KEY].note


# ── 6. the superseded sentence is kept, marked, not deleted ─────────────────

def test_the_false_sentence_is_marked_refuted_in_place_not_deleted():
    """Deleting a wrong sentence restores the undetectable state. It must
    remain, quoted, under a refutation marker."""
    note = load_pack(GATE_PACK).params[GATE_KEY].note
    assert "no sweep has been located" in note, (
        "the refuted sentence was deleted instead of marked; how it was wrong "
        "is the lesson")
    assert "REFUTED IN PART" in note
    assert "SUPERSEDED" in note
    assert "research/alkaline_oxidizer_sign_transfer.yaml" in note, (
        "the note must name the evidence a reader can check")


def test_the_probe_that_measured_this_still_exists():
    """A claim whose instrument is gone cannot be re-measured."""
    assert PROBE.exists(), (
        "the probe behind this refutation is missing; re-measuring is the only "
        "honest response to a failure here")
    src = PROBE.read_text()
    assert "used_for_calibration" in src and "CONFOUNDED" in src, (
        "the probe must still report the two admissibility filters the "
        "conclusion depends on")
