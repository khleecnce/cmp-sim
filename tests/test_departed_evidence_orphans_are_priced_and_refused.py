r"""§56: the §55 orphan class has more members, and the repairs are REFUSED on
measurement — while the fit-vs-derivation question §55 opened is closed on the
size axis in the opposite direction.

WHAT THIS FILE PINS
-------------------
§55 found ONE orphaned constant (evidence re-assigned to another pack, the
citation still resolving, the value still acting, nothing breaking) and
repaired it by withdrawal.  Its generalisation was *a constant's evidence can
leave without the constant noticing*, and its instruction to the next session
was to ask the class question mechanically.

That was done (`tools/departed_evidence_census.py`), and this file pins the
three separable results, every number re-measured at run time:

 1. THE CLASS HAS MORE MEMBERS, AND THEY ARE ENUMERABLE.  Two live numeric
    constants have every cited block outside their reach AND nothing in reach
    that sweeps their axis, so no measurement this corpus contains can
    contradict them.  Both are `abrasive_size_exponent`.

 2. THE REPAIRS ARE REFUSED, AND REFUSED ON MEASUREMENT.  §55 repaired its
    orphan by withdrawing the fit so a derivation acted.  Here the same repair
    is PRICED and is much worse: replacing the declared size exponent with the
    engine's `n_d = -q(1-alpha*chi)+beta` costs 10 blocks and gains 1.  The
    other candidate repair -- re-assigning the departed dataset back -- is
    likewise priced: on W it is exactly neutral on shape and moves neither
    corpus median, on Cu it buys 0.4 pp of trend for a 6.4x absolute-scale
    error.  The refusals are written into the packs' own notes with their
    numbers, so the next reader meets the measurement, not the conclusion.

 3. "0 WORSE" IS NOT THE ADOPTION RULE, AND THE ASYMMETRY HOLDS BOTH WAYS.
    §55 adopted a derived value BECAUSE it was derived.  The mirror case is
    here: the derivation is worse, so the fit stays and the disagreement is
    recorded rather than tuned away.  Had this file adopted the derivation for
    symmetry with §55 it would have added ~6 pp to the corpus median.

WHY THIS IS NOT §55 RESTATED
----------------------------
§55's probe asked one pack one question.  This probe asks every pack, and it
asks the direction `tools/calibration_flag_audit.py` structurally cannot: that
audit EXCUSES a cross-pack citation as ordinary evidence reuse (its `own_pack`
filter, added because §46 got exactly that false positive).  The excuse is
right there and is the blind spot here -- a citation waved through as harmless
reuse may be a constant's ONLY evidence, leaving it unfalsifiable inside its
own reach.  Two readers, opposite questions, same citations.
"""
from __future__ import annotations

import statistics
from pathlib import Path

import pytest
import yaml

from cmp_sim.core.params import load_pack
from tools import departed_evidence_census as dec
from tools import size_exponent_derivation_price as price

DATASETS = (Path(__file__).resolve().parents[1] / "cmp_sim" / "data"
            / "validation" / "datasets")

#: The two orphans the census reports. Named so a test failure says WHICH
#: constant changed state rather than only that a count moved.
ORPHANS = {
    ("cu_alkaline_benzenesulfonic", "abrasive_size_exponent"):
        "tw202115224a_cu_abrasive_size_pressure",
    ("w_fe_oxidizer", "abrasive_size_exponent"):
        "bouvet2002_w_silica_size_sweep",
}


@pytest.fixture(scope="module")
def findings():
    return dec.collect()


@pytest.fixture(scope="module")
def priced():
    return price.measure()


# ── 1. the class, enumerated ────────────────────────────────────────────
def test_the_census_is_not_vacuous(findings):
    """A probe that examines nothing passes every other test in this file."""
    assert len(findings) > 100, len(findings)
    assert any(f.klass == "testable" for f in findings), (
        "no constant is testable at all -- the reach or axis mapping is "
        "broken, and every 'untestable' verdict below is then meaningless")


def test_the_instrument_recovers_a_known_departed_citation(findings):
    """Instrument control: the probe must SEE a citation that really moved.

    Without this the file passes cleanly when the source parsing breaks, and
    "no orphans found" reads as a clean bill of health for the repository.
    """
    moved = [f for f in findings if f.departed]
    assert moved, ("the census found no departed citation at all, which "
                   "contradicts rulings #27/#49-B -- suspect the probe")


def test_every_orphan_is_still_an_orphan(findings):
    """The §55 class, re-enumerated. Both members, by name."""
    hot = {(f.pack, f.constant): f
           for f in findings if f.klass == "DEPARTED-AND-UNTESTABLE"}
    assert set(hot) == set(ORPHANS), (
        f"the orphan set changed: {sorted(hot)} vs {sorted(ORPHANS)}. If a "
        "constant left it, say which repair retired it; if one joined, it is "
        "a new instance of the §55 class and needs its own pricing.")
    for key, dataset in ORPHANS.items():
        assert dataset in hot[key].departed, (key, hot[key].departed)
        assert not hot[key].testable, (
            f"{key} now has a block that could refute it: {hot[key].testable}. "
            "That is good news -- re-price the constant against it.")


def test_a_declared_cross_system_transfer_is_not_counted_as_an_orphan(findings):
    """The classifier must not condemn a correctly-declared transfer.

    `cu_h2o2_bta.ph_mechanical_floor` cites an alkaline series scored under
    another pack and its note SAYS the transfer is deliberate ("CROSS-SYSTEM,
    and knowingly so"). Counting it would be §46's false positive one level
    up: reporting honesty as decay.
    """
    declared = [f for f in findings if f.klass == "declared-cross-system"]
    assert declared, ("no constant declares a cross-system transfer, so this "
                      "filter is untested and could be inverted without "
                      "anything failing")
    assert ("cu_h2o2_bta", "ph_mechanical_floor") in {
        (f.pack, f.constant) for f in declared}


def test_the_reference_exemption_is_not_swallowing_the_finding(findings):
    """A reference constant is 1.0 by contract, so it carries no residual.

    Excluding them is correct and is also the cheapest way to make this whole
    file vacuous, so the exemption is asserted to be narrow: it must not catch
    either orphan.
    """
    for pack, constant in ORPHANS:
        assert not dec._is_reference(constant), constant
    assert any(f.klass == "reference-condition" for f in findings)


# ── 2. the repairs, priced ──────────────────────────────────────────────
def test_the_derivation_is_worse_on_the_size_axis(priced):
    """§55's repair does not generalise to this axis, and the price says so."""
    assert len(priced) >= 30, len(priced)
    better = [r for r in priced if r["shape_after"] < r["shape_before"] - 0.05]
    worse = [r for r in priced if r["shape_after"] > r["shape_before"] + 0.05]
    assert len(worse) > len(better), (
        f"the derived size exponent is now better on {len(better)} blocks and "
        f"worse on {len(worse)}. §55's ordering applies: if the derivation is "
        "not worse, ADOPT it -- and update this test to pin the adoption.")
    med_before = statistics.median([r["shape_before"] for r in priced])
    med_after = statistics.median([r["shape_after"] for r in priced])
    assert med_after > med_before + 1.0, (med_before, med_after)


def test_the_damage_is_concentrated_on_blocks_that_actually_sweep_size(priced):
    """A price that moves blocks holding size FIXED would be measuring
    something else -- the exponent acts there only through (d/d_ref)^n."""
    swept_worse = [r for r in priced if r["varies_size"]
                   and r["shape_after"] > r["shape_before"] + 0.05]
    assert len(swept_worse) >= 5, len(swept_worse)


def test_the_w_reassignment_buys_no_accuracy():
    """Candidate repair: move the departed dataset back to the citing pack.

    Priced rather than argued. On W it is exactly neutral on shape, so it
    cannot be justified by accuracy -- and it would apply an alumina-
    referenced pack to a silica slurry with no `abrasive:` declaration to
    trigger the swap detector (§27).
    """
    import copy

    from cmp_sim.core import predictive_score as ps

    path = DATASETS / "bouvet2002_w_silica_size_sweep.yaml"
    doc = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    assert str(doc.get("pack")) == "oxide_silica", doc.get("pack")
    rows = [r for r in (doc.get("conditions") or [])
            if ps._measured(r) is not None]
    assert len(rows) >= 3

    def shape(d):
        ms, pr = [], []
        for row in rows:
            v = ps._predict(d, row)
            m = ps._measured(row)
            assert v and m is not None
            ms.append(m)
            pr.append(v)
        scale = sum(m * p for m, p in zip(ms, pr)) / sum(p * p for p in pr)
        return 100.0 * sum(abs(scale * p - m) / m
                           for m, p in zip(ms, pr)) / len(ms)

    alt = copy.deepcopy(doc)
    alt["pack"] = "w_fe_oxidizer"
    assert abs(shape(alt) - shape(doc)) < 0.5, (shape(doc), shape(alt))
    # And the file still gives the swap detector nothing to ask about, which
    # is why re-assigning is a SEPARATE decision from declaring the abrasive.
    assert doc.get("abrasive") is None


# ── 3. the refusals are written where the next reader will meet them ────
@pytest.mark.parametrize(("pack", "constant"), sorted(ORPHANS))
def test_each_orphan_declares_its_untestability_with_numbers(pack, constant):
    """A refusal with no numbers in it becomes permanent by accident.

    Asserted on the note the PARAMETER LOADER returns, not on the file text:
    a `note: >` block wraps on disk, so a file-level check can pass while the
    loaded value says something else (§52).
    """
    note = str(getattr(load_pack(pack).params[constant], "note", "") or "")
    flat = " ".join(note.split())
    assert "departed_evidence_census" in flat, flat[:200]
    assert "TODO(owner)" in flat
    # the exit condition, and at least one measured number behind the refusal
    assert any(tok in flat for tok in ("2.32%", "19.51%", "11.177", "44.01%"))


def test_the_notes_do_not_claim_the_repair_was_merely_considered():
    """Both notes must say the repair was PRICED, so a later session cannot
    read the refusal as an unexamined default."""
    for pack, constant in ORPHANS:
        flat = " ".join(str(load_pack(pack).params[constant].note).split())
        assert "REFUSED" in flat or "refused" in flat, (pack, flat[:200])
