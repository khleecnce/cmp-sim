r"""§53 — twelve declared, graded, cited constants that reach nothing AND that
the corpus refutes fit-free.

WHAT THIS PINS
--------------
§49 asked reachability per (key, PACK) of ONE key family and found two inert
oxidiser peaks. Asked of the other peaked family in this repository, the answer
is larger and the second half is new:

    four pack families declare a three-parameter peaked particle-size curve
    (abrasive_size_peak_nm / _exp_below_peak / _exp_above_peak), twelve
    constants, every one graded `literature` with a primary citation, and
    NONE of the twelve moves any prediction (0.000000 %).

The cause is §49's cause with the layers swapped: the piecewise curve is
implemented in the inherited layer (`legacy/sim/factors.py`) while the shipping
size factor is one pooled exponent per abrasive family
(`cmp_sim/models/luo_dornfeld.py`), which never consults a peak.

The corrective half is the opposite of §49's. There the declared value WON when
priced, so the entry forbade moving it. Here the declared curve LOSES, twice
over:

  * priced  — the pooled exponent beats the piecewise curve on 8 of 8 pure size
    sweeps. This reading is partly in-sample, so it is asserted only as the
    weaker of the two.
  * fit-free — a peak POSITION is refutable without fitting anything, and 6 of
    8 sweeps refute it. The decisive one is `bouvet2002_oxide_silica_size_sweep`:
    the corpus's only GENUINE colloidal-silica-on-thermal-oxide match, the same
    system the declared 80 nm came from, whose own authors print the maximum at
    25 nm. The declared curve requires the rate to rise to 80 nm; it falls from
    25 nm on.

So this file must not be read as a licence to WIRE the curve, nor to move the
constants to the refuting datasets' argmax. It pins the third option: values
unchanged, curve unwired, and every one of the twelve saying so in its own
note — because §49 established that an unquotable number ages into fact.

WHY TESTS AND NOT A PROBE RUN
-----------------------------
Every number is re-measured here through the shipping solver, and the corpus
verdicts are recomputed from the datasets' own rows. Pinning literals would go
stale the moment a size constant is re-sourced, and a stale literal invites
editing the claim instead of the code (the failure of §40).
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from cmp_sim.api import run_recipe                       # noqa: E402
from cmp_sim.core.params import load_pack                # noqa: E402
from cmp_sim.core.predictive_score import (              # noqa: E402
    PACK_FILM, dataset_paths,
)

PEAK_KEYS = ("abrasive_size_peak_nm",
             "abrasive_size_exp_below_peak",
             "abrasive_size_exp_above_peak")

#: Small first, both directions (§43: the perturbation is part of the
#: instrument). A constant is called inert only if NONE of these reaches it.
FACTORS = (1.05, 0.95, 1.25, 0.8, 1.5, 0.67, 2.0, 0.5)

#: Same 0.5 % bar `tools/inert_axis_scan.py` uses, so the two cannot disagree.
INERT_TOLERANCE = 0.5

#: The base run is displaced off `abrasive_ref_size_nm` before anything is
#: perturbed. At d == d_ref every normalised size factor is exactly 1.0 for
#: EVERY exponent, so a measurement there reports the normalisation contract as
#: inertness — the trap of §42/§43, reached here through the reference rather
#: than through a symmetry point.
SIZE_DISPLACEMENT = 1.7

EVIDENCE = ROOT / "research" / "size_peak_reachability.yaml"
PROBE = ROOT / "tools" / "size_peak_reachability_probe.py"


def _rate(pack: str, film: str,
          overrides: Optional[Dict[str, Any]] = None) -> Optional[float]:
    recipe: Dict[str, Any] = {
        "model": "auto",
        "wafer": {"film": film, "n_radial": 11},
        "slurry": {"pack": pack},
        "tool": {"pressure_psi": 3.0, "rpm_platen": 60, "rpm_head": 60,
                 "time_s": 60.0, "flow_ml_min": 200.0},
    }
    if overrides:
        recipe["params"] = dict(overrides)
    value = run_recipe(recipe).get("removal_rate_A_per_min")
    return None if not value else float(value)


def _packs_with_triple() -> Dict[str, str]:
    out = {}
    for name, film in PACK_FILM.items():
        try:
            pack = load_pack(name)
        except Exception:
            continue
        if all((pack.params.get(k) is not None
                and pack.params[k].value is not None) for k in PEAK_KEYS):
            out[name] = film
    return out


def _displaced_query(pack_name: str) -> Optional[float]:
    params = load_pack(pack_name).params
    d = params.get("abrasive_size_nm")
    if d is None or not d.value:
        return None
    ref = params.get("abrasive_ref_size_nm")
    base = float(ref.value) if ref is not None and ref.value else float(d.value)
    return base * SIZE_DISPLACEMENT


def _max_response(pack_name: str, film: str, key: str) -> float:
    query = _displaced_query(pack_name)
    assert query is not None
    base_ov = {"abrasive_size_nm": query}
    base = _rate(pack_name, film, base_ov)
    assert base, f"{pack_name} produced no base rate"
    value = float(load_pack(pack_name).params[key].value)
    best = 0.0
    for f in FACTORS:
        ov = dict(base_ov)
        ov[key] = value * f
        r = _rate(pack_name, film, ov)
        if r is not None:
            best = max(best, abs(r - base) / base * 100.0)
    return best


# ── the subject must exist (a deleted check must not read as a pass) ────────

def test_the_triple_is_actually_declared_by_several_packs():
    """Guard against vacuity. If no pack declares the triple, every assertion
    below passes trivially and the section becomes undetectable — which is the
    state §49's entry exists to prevent."""
    packs = _packs_with_triple()
    assert len(packs) >= 4, (
        "fewer than four packs declare the peaked size triple; this file's "
        f"subject has moved, got {sorted(packs)}")
    for name in packs:
        for key in PEAK_KEYS:
            p = load_pack(name).params[key]
            assert p.value is not None
            assert getattr(p, "source", None), (
                f"{name}.{key} has no source — the finding is about CITED "
                "constants that reach nothing, so an uncited one would weaken it")


# ── (1) all twelve are inert, and the instrument can see the axis ───────────

def test_every_declared_size_peak_constant_reaches_nothing():
    packs = _packs_with_triple()
    inert, reached = [], []
    for name, film in sorted(packs.items()):
        for key in PEAK_KEYS:
            resp = _max_response(name, film, key)
            (inert if resp < INERT_TOLERANCE else reached).append(
                (f"{name}.{key}", resp))
    assert not reached, (
        "a size-peak constant now REACHES the rate, so §53's premise has "
        f"changed and the pack notes claiming inertness are stale: {reached}")
    assert len(inert) >= 12, f"expected >=12 inert constants, got {len(inert)}"


@pytest.mark.parametrize("pack_name", sorted(_packs_with_triple()))
def test_instrument_control_the_size_axis_itself_does_move_the_rate(pack_name):
    """§43: a zero response is unquotable without evidence the probe can see a
    live key. The control is the DRIVER the three constants are meant to shape;
    if the size axis were dead on this pack, the row above would be a probe
    failure rather than a wiring fact."""
    film = _packs_with_triple()[pack_name]
    query = _displaced_query(pack_name)
    assert query is not None
    base = _rate(pack_name, film, {"abrasive_size_nm": query})
    assert base
    moved = 0.0
    for f in (1.25, 0.8, 2.0, 0.5):
        r = _rate(pack_name, film, {"abrasive_size_nm": query * f})
        if r is not None:
            moved = max(moved, abs(r - base) / base * 100.0)
    assert moved >= INERT_TOLERANCE, (
        f"{pack_name}: abrasive_size_nm itself moves only {moved:.4f}% — this "
        "pack's inert verdict would be a probe failure, not a wiring fact")


def test_the_displacement_matters_so_the_zero_is_not_the_reference_contract():
    """The zeros must be measured AWAY from `abrasive_ref_size_nm`. At d == d_ref
    the size factor is 1.0 for every exponent, so a probe standing there would
    report the normalisation contract as inertness — and would also report the
    LIVE pooled exponent as inert. Asserted by measuring that the size axis is
    reachable only once displaced."""
    pack_name = "oxide_silica"
    film = PACK_FILM[pack_name]
    params = load_pack(pack_name).params
    ref = float(params["abrasive_ref_size_nm"].value)
    at_ref = _rate(pack_name, film, {"abrasive_size_nm": ref})
    displaced = _rate(pack_name, film, {"abrasive_size_nm": ref * SIZE_DISPLACEMENT})
    assert at_ref and displaced
    assert abs(displaced - at_ref) / at_ref * 100.0 >= INERT_TOLERANCE, (
        "displacing off the reference size no longer changes the rate, so the "
        "displacement in this file's probe has stopped doing its job")


# ── (2) the fit-free refutation, recomputed from the datasets' own rows ─────

def _size_sweeps() -> List[Dict[str, Any]]:
    out = []
    for path in dataset_paths():
        try:
            doc = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        except Exception:
            continue
        by_level: Dict[float, List[float]] = {}
        for row in doc.get("conditions") or []:
            ov = row.get("overrides") or {}
            d = ov.get("abrasive_size_nm", ov.get("abrasive_d50_nm"))
            rate = row.get("mrr_nm_per_min")
            if rate is None and row.get("mrr_A_per_min") is not None:
                rate = float(row["mrr_A_per_min"]) / 10.0
            if d is None or rate is None:
                continue
            by_level.setdefault(float(d), []).append(float(rate))
        if len(by_level) < 3:
            continue
        levels = sorted(by_level)
        means = [sum(by_level[d]) / len(by_level[d]) for d in levels]
        out.append({"dataset": path.stem, "pack": str(doc.get("pack") or ""),
                    "levels": levels, "rates": means,
                    "argmax": levels[max(range(len(levels)),
                                         key=lambda i: means[i])]})
    return out


def _verdict(peak: float, levels: List[float], rates: List[float],
             argmax: float) -> Tuple[str, str]:
    """What the sweep can decide, and what it decides.

    IDENTIFIABILITY FIRST (§52): a bracketing sweep tests the POSITION; a sweep
    wholly below the peak tests only that the declared below-leg SIGN (rising)
    holds; wholly above, the above-leg sign (falling). The weaker claims are
    still refutable, and refuting a sign refutes the curve without needing any
    exponent magnitude.
    """
    if levels[0] <= peak <= levels[-1]:
        return ("position",
                "CONFIRMS" if abs(argmax - peak) / peak <= 0.25 else "REFUTES")
    if peak > levels[-1]:
        rising = all(b >= a for a, b in zip(rates, rates[1:]))
        return "below-leg sign", "CONFIRMS" if rising else "REFUTES"
    falling = all(b <= a for a, b in zip(rates, rates[1:]))
    return "above-leg sign", "CONFIRMS" if falling else "REFUTES"


def test_the_corpus_refutes_the_declared_peak_more_often_than_it_confirms():
    verdicts = []
    for row in _size_sweeps():
        try:
            pack = load_pack(row["pack"])
        except Exception:
            continue
        p = pack.params.get("abrasive_size_peak_nm")
        if p is None or p.value is None:
            continue
        testable, verdict = _verdict(float(p.value), row["levels"],
                                     row["rates"], row["argmax"])
        verdicts.append((row["dataset"], testable, verdict))
    refutes = [v for v in verdicts if v[2] == "REFUTES"]
    confirms = [v for v in verdicts if v[2] == "CONFIRMS"]
    assert len(refutes) > len(confirms), (
        "the corpus no longer refutes the declared size peaks more often than "
        f"it confirms them; refutes={refutes} confirms={confirms}")
    # BOTH halves non-empty, so the entry cannot pass vacuously: a corpus that
    # confirmed nothing would make the refutation unfalsifiable in principle.
    assert confirms, (
        "no sweep confirms any declared peak — a verdict with no confirming "
        "case is not evidence that the constants are wrong, it is evidence the "
        "reader is broken")


def test_the_decisive_refutation_is_the_genuine_system_match():
    """The load-bearing row must be the one where abrasive AND film match the
    declared value's own source. A refutation drawn only from transplanted packs
    would be the cross-pack laundering §32/§34 forbids."""
    rows = {r["dataset"]: r for r in _size_sweeps()}
    key = "bouvet2002_oxide_silica_size_sweep"
    assert key in rows, f"{key} has left the corpus; §53's decisive row is gone"
    row = rows[key]
    assert row["pack"] == "oxide_silica", (
        f"{key} is no longer scored against oxide_silica, so it is no longer a "
        "same-abrasive same-film match for the declared 80 nm")
    peak = float(load_pack("oxide_silica").params["abrasive_size_peak_nm"].value)
    # The sweep's own maximum is interior AND far below the declared peak.
    assert row["argmax"] < peak / 2.0, (
        f"{key} argmax {row['argmax']} nm is no longer far below the declared "
        f"{peak} nm; the refutation has weakened")
    best = row["levels"].index(row["argmax"])
    assert 0 < best < len(row["levels"]) - 1, (
        "the maximum is at a range endpoint, which §44 forbids reading as an "
        "optimum — the refutation would then rest on the publication's choice "
        "of range rather than on a measured peak")


# ── (3) the repair is the NOTE, and the values must stay put ────────────────

@pytest.mark.parametrize("pack_name", sorted(_packs_with_triple()))
def test_each_inert_constant_says_in_its_own_note_that_it_is_inert(pack_name):
    """§49's rule: an unreachable value may not present itself as a live one.
    Asserted through the PARAMETER LOADER rather than by reading the YAML text,
    because a `note: >` folded block stores differently from the source lines
    and a disk-string check can pass while the loaded note is untouched (the
    false negative caught in §51)."""
    params = load_pack(pack_name).params
    for key in PEAK_KEYS:
        note = str(getattr(params[key], "note", "") or "")
        assert "INERT" in note.upper(), (
            f"{pack_name}.{key} is measured inert but its own note does not say "
            "so; a graded, cited number that moves nothing and admits nothing "
            "is exactly how §49's peaks aged into fact")


def test_the_declared_values_were_not_refitted_to_the_refuting_datasets():
    """The refutation is NOT a licence to re-fit. Moving a peak onto the argmax
    of the dataset that refuted it would fit a term that reaches nothing to its
    own refutation, and `us20190127607a1`'s 210.7 nm is that patent's HIGHEST
    RUN LEVEL — a range endpoint, which §44 forbids reading as an optimum."""
    assert float(load_pack("oxide_silica").params[
        "abrasive_size_peak_nm"].value) == pytest.approx(80.0)
    for name in ("sti_ceria", "sic_ceria_h2o2"):
        assert float(load_pack(name).params[
            "abrasive_size_peak_nm"].value) == pytest.approx(163.0)
    forbidden = {25.0, 210.7, 12.0, 2500.0}
    for name in _packs_with_triple():
        got = float(load_pack(name).params["abrasive_size_peak_nm"].value)
        assert got not in forbidden, (
            f"{name}.abrasive_size_peak_nm was moved to {got} nm, an argmax of "
            "one of the refuting datasets — that is re-fitting an inert term to "
            "the data that refuted it")


def test_the_curve_is_still_unwired_so_the_notes_stay_true():
    """If a later session wires the piecewise curve, every note written above
    becomes false. That must fail here rather than be discovered by a reader."""
    for name, film in sorted(_packs_with_triple().items()):
        assert _max_response(name, film, "abrasive_size_peak_nm") < INERT_TOLERANCE, (
            f"{name}: the peaked size curve has been WIRED. Before doing that, "
            "price it — it lost to the pooled exponent on 8 of 8 pure size "
            "sweeps and is refuted fit-free on 6 of 8 "
            "(research/size_peak_reachability.yaml)")


def test_the_evidence_record_and_probe_exist_and_agree_with_the_verdict():
    """The quoted numbers live in one place. A test that restated them would let
    the record and the claim drift apart (§49)."""
    assert PROBE.exists(), "the probe behind §53 was deleted"
    doc = yaml.safe_load(EVIDENCE.read_text(encoding="utf-8")) or {}
    assert doc["reachability"]["constants_reached"] == 0
    assert doc["reachability"]["constants_inert"] >= 12
    tally = doc["fit_free_reading"]["tally"]
    assert tally["refutes"] > tally["confirms"]
    # The record must keep the REJECTED options, or the next session re-proposes
    # them and this file's reasoning has to be rediscovered.
    rejected = " ".join(str(r) for r in doc["what_was_rejected"])
    for must in ("wire the piecewise curve", "delete the twelve constants"):
        assert must in rejected, f"the record no longer rejects: {must}"
    assert doc["what_would_reopen_this"].strip(), (
        "a refusal with no exit condition is unfalsifiable")
