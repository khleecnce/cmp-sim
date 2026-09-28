"""§51's rule applied once more: an "absence of data" claim is a MEASUREMENT
that expires, and §49's is false -- but the DECISION it guards survives for a
stronger, measured reason (limits §52).

§49 said of `cu_alkaline_benzenesulfonic` and `w_fe_oxidizer`: "both packs'
corpora sweep the oxidizer at one level or not at all, so the experiment needed
is a >=3-level oxidizer sweep on those chemistries."  Re-running the
enumeration instead of quoting it finds FOUR such ladders, one of them five
levels and held out.

The decision nevertheless stands, because `oxidizer_peak_shape_K` is a PEAK
SHAPE constant and every one of those ladders is MONOTONE: no value of K places
a peak inside a range the data cross monotonically, so the constant is
unidentifiable from them at any level count.

What is asserted here:

  1. The sentence's factual half is false -- multi-level ladders exist.  Asserted
     by re-enumerating the real dataset files, never from the evidence file's
     copy, so the test cannot pass on a stale transcription.

  2. Every such ladder is monotone, so none can anchor a peak shape.  This is
     the load-bearing assertion: it is what keeps the decision standing.

  3. EXPIRY.  The moment any held-out, pH-unconfounded ladder brackets an
     INTERIOR maximum, this fails -- and the correct response is to anchor
     `oxidizer_peak_shape_K`, not to relax the test.

  4. The two packs' constants are unmoved: finding data is not a licence to fit.

  5. CONTROL against the proxy error the entry is about: a synthetic ladder with
     an interior maximum MUST be detected, and a synthetic monotone one must
     not.  Without this, "no interior maximum anywhere" could be a broken
     detector reporting a clean bill of health.

  6. Non-vacuity: if the enumeration stops finding ladders, every assertion
     above passes for free and is indistinguishable from a deleted test.
"""
from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from cmp_sim.core.params import load_pack

ROOT = Path(__file__).resolve().parents[1]
DATASETS = ROOT / "cmp_sim" / "data" / "validation" / "datasets"
EVIDENCE = ROOT / "research" / "absent_data_claim_reaudit.yaml"
PROBE = ROOT / "tools" / "absent_data_claim_reaudit_probe.py"

SUBJECT_PACKS = ("cu_alkaline_benzenesulfonic", "w_fe_oxidizer")
SHAPE_KEY = "oxidizer_peak_shape_K"
POSITION_KEY = "oxidizer_peak_wt_pct"
MIN_LEVELS = 3


def _ladders(pack_name):
    """Re-enumerate from the REAL dataset files. Replicates at one level are
    collapsed to their mean before any shape question -- within-level scatter
    is not curvature."""
    out = []
    for path in sorted(DATASETS.glob("*.yaml")):
        doc = yaml.safe_load(path.read_text())
        if not isinstance(doc, dict) or doc.get("pack") != pack_name:
            continue
        by_level, phs = {}, []
        for c in doc.get("conditions") or []:
            ov = (c or {}).get("overrides") or {}
            if "oxidizer_wt_pct" not in ov or c.get("mrr_nm_per_min") is None:
                continue
            by_level.setdefault(float(ov["oxidizer_wt_pct"]), []).append(
                float(c["mrr_nm_per_min"]))
            if ov.get("slurry_ph") is not None:
                phs.append(float(ov["slurry_ph"]))
        if len(by_level) < MIN_LEVELS:
            continue
        levels = sorted(by_level)
        out.append({
            "name": path.stem,
            "levels": levels,
            "means": [sum(by_level[v]) / len(by_level[v]) for v in levels],
            "calib": bool(doc.get("used_for_calibration")),
            "ph_span": (max(phs) - min(phs)) if phs else 0.0,
        })
    return out


def _has_interior_max(means) -> bool:
    if len(means) < 3:
        return False
    i = means.index(max(means))
    return 0 < i < len(means) - 1


# ── 5. control first: the detector must be able to answer both ways ─────────

def test_interior_maximum_detector_answers_both_ways():
    """CONTROL. If this collapsed to one answer, 'no interior maximum anywhere'
    would be a broken detector rather than a finding."""
    assert _has_interior_max([1.0, 9.0, 2.0]) is True
    assert _has_interior_max([1.0, 5.0, 9.0, 12.0]) is False   # rising
    assert _has_interior_max([12.0, 9.0, 5.0, 1.0]) is False   # falling
    assert _has_interior_max([1.0, 2.0]) is False              # too short


# ── 6. non-vacuity ─────────────────────────────────────────────────────────

def test_the_enumeration_still_finds_multi_level_ladders():
    found = {p: _ladders(p) for p in SUBJECT_PACKS}
    total = sum(len(v) for v in found.values())
    assert total >= 3, (
        "fewer than three multi-level oxidiser ladders remain under these "
        "packs; the entry's finding is no longer supported by the corpus it "
        f"was measured on (found {total})")
    assert all(found[p] for p in SUBJECT_PACKS), (
        f"one subject pack has no multi-level ladder at all: "
        f"{ {p: len(v) for p, v in found.items()} }")


# ── 1. the sentence's factual half is false ────────────────────────────────

def test_the_absence_claim_is_false_multi_level_sweeps_exist():
    """§49 said these packs sweep the oxidiser 'at one level or not at all'."""
    for pack_name in SUBJECT_PACKS:
        rows = _ladders(pack_name)
        assert rows, (
            f"{pack_name}: §49's sentence would be true again -- re-measure "
            "before trusting either version")
        best = max(len(r["levels"]) for r in rows)
        assert best >= MIN_LEVELS, best


def test_the_evidence_file_agrees_with_a_live_enumeration():
    """The evidence file must not drift from the corpus it describes."""
    ev = yaml.safe_load(EVIDENCE.read_text())
    assert ev["verdict_on_the_sentence"] is False or \
        str(ev["verdict_on_the_sentence"]).upper() == "FALSE"
    for pack_name in SUBJECT_PACKS:
        live = {r["name"] for r in _ladders(pack_name)}
        recorded = {d["dataset"] for d in ev["enumeration"][pack_name]
                    if len(d.get("levels_wt_pct", [])) >= MIN_LEVELS}
        assert recorded == live, (
            f"{pack_name}: the evidence file lists {sorted(recorded)} but the "
            f"corpus now holds {sorted(live)}")


# ── 2. the load-bearing assertion: every ladder is monotone ────────────────

def test_no_multi_level_ladder_can_anchor_a_peak_shape():
    """A peak SHAPE constant needs an INTERIOR maximum. Level count was always
    a proxy; this is the requirement it stood for."""
    for pack_name in SUBJECT_PACKS:
        for r in _ladders(pack_name):
            assert not _has_interior_max(r["means"]), (
                f"{r['name']} now brackets an interior maximum "
                f"({r['means']}) -- see the expiry test; anchor "
                f"{SHAPE_KEY} instead of relaxing this one")


# ── 3. expiry ──────────────────────────────────────────────────────────────

def test_no_admissible_ladder_can_reopen_the_shape_constant_yet():
    """EXPIRY. Held out, pH not confounded, and an interior maximum. When one
    appears, fit the constant -- do not edit this test."""
    reopeners = []
    for pack_name in SUBJECT_PACKS:
        for r in _ladders(pack_name):
            if (not r["calib"] and r["ph_span"] <= 0.3
                    and _has_interior_max(r["means"])):
                reopeners.append(f"{pack_name}:{r['name']}")
    assert not reopeners, (
        f"{reopeners} is now an admissible anchor for {SHAPE_KEY}. The "
        "corrected exit condition has fired: fit the peak shape and let the "
        "declared peak position reach the rate.")


# ── 4. finding data is not a licence to fit ────────────────────────────────

def test_the_two_packs_constants_are_unmoved():
    for pack_name in SUBJECT_PACKS:
        pack = load_pack(pack_name)
        assert SHAPE_KEY not in pack.params or \
            pack.params[SHAPE_KEY].value is None, (
                f"{pack_name} now declares {SHAPE_KEY}; if that was anchored "
                "on a bracketing ladder, update this entry deliberately")
        pos = pack.params.get(POSITION_KEY)
        assert pos is not None and pos.value is not None, (
            f"{pack_name} stopped declaring {POSITION_KEY}; deleting a dead "
            "declaration restores the undetectable state (§49)")


def test_the_probe_still_exists_and_separates_sentence_from_decision():
    assert PROBE.exists()
    src = PROBE.read_text()
    assert "interior" in src and "monotone" in src, (
        "the probe must still distinguish 'the data exist' from 'the data can "
        "anchor a peak' -- that separation IS the finding")
