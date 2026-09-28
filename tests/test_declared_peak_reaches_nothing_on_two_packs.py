"""§49 — a pack key that is DECLARED, GRADED and reaches nothing on that pack.

WHAT THIS PINS
--------------
§42 asked the reverse wiring question ("a pack key that is DECLARED and reads
nothing") and answered it per KEY: does any engine code path read this name?
`oxidizer_peak_wt_pct` passes that audit — `chemical_rate.py` reads it, and
three packs declare it with a unit, a source and a confidence grade.

Measured per (key, PACK) instead, the answer inverts for two of the three:

    cu_h2o2_bta                  3.0 wt% [literature]  -> 13.889 % REACHED
    cu_alkaline_benzenesulfonic  1.0 wt% [estimated]    ->  0.000 % UNREACHABLE
    w_fe_oxidizer                6.0 wt% [estimated]    ->  0.000 % UNREACHABLE

because the branch that consumes it is selected by a DIFFERENT key
(`oxidizer_peak_shape_K`), which only `cu_h2o2_bta` declares. The other two
return from the Langmuir branch first and never look at their own peak.

The second half is the corrective: the peak position on the one pack where it
IS live was priced against the corpus and the declared value WON, so this file
must not be read as a licence to move it. Three blocks respond, each degrading
monotonically as the peak moves toward the only directly measured position in
the literature held here (Lin & Du 2009).

WHY THESE TESTS AND NOT A PROBE RUN
-----------------------------------
Every number above is re-measured here through the shipping solver and the
shipping scorer, never restated from a transcript, so this file fails if the
wiring changes or if a later session moves the peak to "the measured value".
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from cmp_sim.api import run_recipe                       # noqa: E402
from cmp_sim.core.params import load_pack                # noqa: E402
from cmp_sim.models.chemical_rate import (               # noqa: E402
    langmuir_coverage, peaked_oxidizer_response,
)
from cmp_sim.core.predictive_score import (              # noqa: E402
    PACK_FILM, _measured, _predict_with_gate, dataset_paths,
)

PEAK_KEY = "oxidizer_peak_wt_pct"
SHAPE_KEY = "oxidizer_peak_shape_K"
LIVE_PACK = "cu_h2o2_bta"

#: Perturbations: SMALL FIRST and BOTH directions, per §43 (the perturbation is
#: part of the instrument). A key is called unreachable only if NONE of these
#: moves the rate.
FACTORS = (1.05, 0.95, 1.25, 0.8, 1.5, 0.67, 2.0, 0.5, 3.0, 0.33)

#: Same bar as tools/inert_axis_scan.py, so "unreachable" here means what
#: "inert" means there rather than a second private threshold.
INERT_TOLERANCE_PCT = 0.5

#: Lin & Du, ECS Trans 18(1) 485-490 (2009), doi:10.1149/1.3096490 — the
#: measured Cu maximum at three dilutions of one slurry. Quoted, not fitted.
#: Provenance and the full quotation live in
#: research/cu_oxidizer_peak_position_evidence.yaml.
LIN2009_PEAKS = (0.90, 0.74, 0.66)

EVIDENCE = ROOT / "research" / "cu_oxidizer_peak_position_evidence.yaml"


# ---------------------------------------------------------------- helpers

def _run(pack: str, film: str, overrides: Optional[Dict] = None) -> float:
    """One run of the SHIPPING solver. Never a local reimplementation."""
    recipe = {
        "model": "auto",
        "wafer": {"film": film, "n_radial": 11},
        "slurry": {"pack": pack},
        "tool": {"pressure_psi": 4.0, "rpm_platen": 60, "rpm_head": 60,
                 "time_s": 60.0},
    }
    if overrides:
        recipe["params"] = dict(overrides)
    rate = run_recipe(recipe).get("removal_rate_A_per_min")
    return float(rate) if rate else 0.0


def _max_response_pct(pack: str, film: str, key: str, base_value: float,
                      baseline: float) -> float:
    """Largest |d rate| (%) over the admissible perturbations of one key."""
    if not baseline:
        return 0.0
    best = 0.0
    for f in FACTORS:
        r = _run(pack, film, {key: base_value * f})
        if r:
            best = max(best, abs(r - baseline) / baseline * 100.0)
    return best


def _packs_declaring_peak() -> Dict[str, Tuple[str, float, bool]]:
    """(pack) -> (film, declared peak, declares the shape selector)."""
    out: Dict[str, Tuple[str, float, bool]] = {}
    for name, film in PACK_FILM.items():
        try:
            pack = load_pack(name)
        except Exception:
            continue
        p = pack.params.get(PEAK_KEY)
        if p is None or p.value is None:
            continue
        shape = pack.params.get(SHAPE_KEY)
        out[name] = (film, float(p.value),
                     shape is not None and shape.value is not None)
    return out


DECLARERS = _packs_declaring_peak()


def _best_scale(measured: List[float], predicted: List[float]) -> float:
    """The one free multiplicative scale per block the shape score allows."""
    den = sum(p * p for p in predicted)
    return (sum(m * p for m, p in zip(measured, predicted)) / den) if den else 1.0


def _cu_blocks() -> List[Tuple[str, Dict, List[Dict]]]:
    out = []
    for path in dataset_paths():
        doc = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        if not isinstance(doc, dict) or not doc.get("in_scope"):
            continue
        if doc.get("pack") != LIVE_PACK:
            continue
        out.append((path.name, doc, doc.get("conditions") or []))
    return out


def _shape_mape(doc: Dict, rows: List[Dict],
                peak: Optional[float]) -> Optional[float]:
    """Block shape MAPE through the scorer's own recipe builder and gate."""
    measured, predicted = [], []
    for row in rows:
        m = _measured(row)
        if m is None:
            continue
        d = dict(doc)
        if peak is not None:
            d["pack_overrides"] = dict(doc.get("pack_overrides") or {})
            d["pack_overrides"][PEAK_KEY] = peak
        p, gated, _declined = _predict_with_gate(d, row)
        if p is None or gated:
            return None
        measured.append(m)
        predicted.append(p)
    if len(measured) < 2:
        return None
    s = _best_scale(measured, predicted)
    return 100.0 * sum(abs(s * p - m) / m
                       for m, p in zip(measured, predicted)) / len(measured)


BLOCKS = _cu_blocks()


# ------------------------------------------------- the wiring claim (§49a)

def test_at_least_three_packs_declare_the_peak():
    """Non-vacuity: with fewer declarers the split below cannot exist."""
    assert len(DECLARERS) >= 3, (
        f"only {sorted(DECLARERS)} declare {PEAK_KEY}; §49 is about the same "
        "key having opposite fates on different packs, so this file would "
        "pass for free"
    )


def test_exactly_the_packs_with_the_shape_selector_reach_the_peak():
    """The split is explained by SHAPE_KEY, not by luck. Both halves asserted."""
    reached, inert = {}, {}
    for pack, (film, peak, has_shape) in sorted(DECLARERS.items()):
        base = _run(pack, film)
        assert base > 0, f"{pack} produced no baseline rate"
        resp = _max_response_pct(pack, film, PEAK_KEY, peak, base)
        (reached if resp > INERT_TOLERANCE_PCT else inert)[pack] = (resp,
                                                                    has_shape)
    assert reached, "no pack reaches its own declared peak — §49 inverted"
    assert inert, (
        "every declarer now reaches its peak; §49's finding has been fixed, "
        "so this test must be retired rather than left passing vacuously"
    )
    for pack, (resp, has_shape) in reached.items():
        assert has_shape, (
            f"{pack} reaches {PEAK_KEY} ({resp:.3f} %) without declaring "
            f"{SHAPE_KEY} — the stated mechanism for the split is wrong"
        )
    for pack, (resp, has_shape) in inert.items():
        assert not has_shape, (
            f"{pack} declares {SHAPE_KEY} yet {PEAK_KEY} moves the rate only "
            f"{resp:.3f} % — the stated mechanism for the split is wrong"
        )


@pytest.mark.parametrize("pack", sorted(DECLARERS))
def test_inert_peaks_are_not_probe_failures(pack: str):
    """§43's control: a key known to be read MUST move on the same pack."""
    film, peak, _ = DECLARERS[pack]
    base = _run(pack, film)
    if _max_response_pct(pack, film, PEAK_KEY, peak, base) > INERT_TOLERANCE_PCT:
        pytest.skip(f"{pack} reaches its peak; no control needed")
    pk = load_pack(pack)
    moved = {}
    for key in ("oxidizer_wt_pct", "abrasive_wt_pct", "slurry_ph"):
        p = pk.params.get(key)
        if p is None or p.value is None:
            continue
        moved[key] = _max_response_pct(pack, film, key, float(p.value), base)
    assert moved, f"{pack} declares no control key; the zero is uninterpretable"
    assert max(moved.values()) > INERT_TOLERANCE_PCT, (
        f"{pack}: no key moved the rate at all ({moved}) — the zero on "
        f"{PEAK_KEY} says nothing about that key specifically"
    )


def test_inert_declarations_are_not_silently_graded_as_evidence():
    """An unreachable number must not claim to rest on literature (§35)."""
    for pack, (film, peak, has_shape) in sorted(DECLARERS.items()):
        base = _run(pack, film)
        if _max_response_pct(pack, film, PEAK_KEY, peak,
                             base) > INERT_TOLERANCE_PCT:
            continue
        conf = getattr(load_pack(pack).params[PEAK_KEY], "confidence", None)
        assert conf != "literature", (
            f"{pack}.{PEAK_KEY} is unreachable on this pack yet graded "
            f"'{conf}' — an unfalsifiable number must not carry the grade "
            "reserved for a tested one"
        )


def test_inert_declarations_say_in_prose_that_they_are_inert():
    """The packs already knew; pin the prose so it cannot quietly disappear.

    Both unreachable declarations carry a note ending "(비활성 — Langmuir
    경로로 대체됨, 판정#19)". That honesty is the reason §49 is a MISSING
    ASSERTION rather than a hidden dead value, so the entry's own claim about
    its size depends on this prose existing. If a later edit makes one of these
    live -- with an anchor, which is the exit condition -- this test fails and
    forces the note to be updated with it.
    """
    for pack, (film, peak, has_shape) in sorted(DECLARERS.items()):
        base = _run(pack, film)
        if _max_response_pct(pack, film, PEAK_KEY, peak,
                             base) > INERT_TOLERANCE_PCT:
            continue
        note = (getattr(load_pack(pack).params[PEAK_KEY], "note", "") or "")
        assert "비활성" in note or "inactive" in note.lower(), (
            f"{pack}.{PEAK_KEY} is unreachable on this pack and its note no "
            "longer says so. Either the note was trimmed (restore it) or the "
            "value became live (then it needs an anchor, not just a branch)"
        )


# ------------------------------------- the position was priced, not moved (§49b)

def test_neither_langmuir_branch_can_represent_a_peak():
    """The species gate's CORRECTED reason, proved as arithmetic.

    The gate in legacy/sim/chemistry.py refuses to transfer an oxalate-fitted
    chelator constant onto a glycine pack. Its note justified that with a SIGN
    claim ("oxalate rises, glycine decreases monotonically") read from one
    patent figure whose three points all start at 0.5 wt% H2O2 -- one limb. Two
    independent sources below that find the rate RISING, so the glycine
    response is PEAKED and the sign claim is wrong.

    The gate's DECISION survives on a stronger, structural reason: the two
    monotone branches cannot represent a peak for ANY constant. That is a
    statement about the function family, so no better constant retires it, and
    it is checked here rather than asserted in prose.
    """
    grid = [0.05 * i for i in range(1, 400)]     # 0.05 .. 19.95 wt%
    for k in (0.05, 0.2, 0.5, 0.7935, 2.0, 10.0):
        promoter = [langmuir_coverage(c, k) for c in grid]
        passivation = [1.0 - langmuir_coverage(c, k) for c in grid]
        for name, series in (("promoter", promoter),
                             ("passivation", passivation)):
            deltas = [b - a for a, b in zip(series, series[1:])]
            signs = {d > 0 for d in deltas if abs(d) > 1e-15}
            assert len(signs) <= 1, (
                f"{name} branch at K={k} changes direction — it is no longer "
                "monotone, so §49's structural justification for the species "
                "gate no longer holds and the gate needs a new reason"
            )

    # Non-vacuity: the form that CAN bend is present and does bend, otherwise
    # the check above would pass on an engine with no peaked capability at all.
    peaked = [peaked_oxidizer_response(c, 3.0, 8.0) for c in grid]
    rises = any(b > a for a, b in zip(peaked, peaked[1:]))
    falls = any(b < a for a, b in zip(peaked, peaked[1:]))
    assert rises and falls, (
        "peaked_oxidizer_response no longer rises AND falls, so the contrast "
        "this test draws against the monotone branches is meaningless"
    )


def test_the_corpus_can_actually_test_the_peak_position():
    """The refutation must not rest on an unfalsifiable claim of its own.

    The argument this file was DRAFTED to make -- 'every scored level sits past
    both candidate peaks, so the position is untestable' -- was measured and
    found false. Pin that it is false, or the refusal below is unsupported.
    """
    assert BLOCKS, f"no in-scope block scores under {LIVE_PACK}"
    responsive = []
    for name, doc, rows in BLOCKS:
        vals = [_shape_mape(doc, rows, p)
                for p in (None,) + LIN2009_PEAKS]
        vals = [v for v in vals if v is not None]
        if len(vals) > 1 and (max(vals) - min(vals)) > 0.05:
            responsive.append(name)
    assert responsive, (
        "moving the peak across the entire published range changes no block's "
        "score, so the corpus cannot test the position and the 'refuted by "
        "measurement' verdict in research/cu_oxidizer_peak_position_evidence"
        ".yaml is not supported by anything"
    )


def test_declared_peak_beats_every_measured_alternative_monotonically():
    """Why the transplant is refused: the corpus says the declared value wins."""
    checked = 0
    for name, doc, rows in BLOCKS:
        base = _shape_mape(doc, rows, None)
        if base is None:
            continue
        raw = [_shape_mape(doc, rows, p) for p in LIN2009_PEAKS]
        if any(a is None for a in raw):
            continue
        alts: List[float] = [float(a) for a in raw if a is not None]
        if max(alts) - min(alts) <= 0.05 and abs(alts[0] - base) <= 0.05:
            continue                       # inert block: nothing to order
        checked += 1
        assert base <= min(alts) + 1e-9, (
            f"{name}: a measured peak position ({min(alts):.1f} %) now beats "
            f"the declared one ({base:.1f} %) — the refusal recorded in "
            "research/cu_oxidizer_peak_position_evidence.yaml no longer holds "
            "and must be revisited, not left asserted"
        )
        # LIN2009_PEAKS descends 0.90 -> 0.66, i.e. monotonically further from
        # the declared 3.0 wt%; the error must not improve along that march.
        for a, b in zip(alts, alts[1:]):
            assert b >= a - 1e-9, (
                f"{name}: error is NOT monotone in distance from the declared "
                f"peak ({alts}) — the response is not a simple peak offset, "
                "so the ordering argument does not apply"
            )
    assert checked >= 2, (
        f"only {checked} block(s) could order the candidates; the refusal "
        "would then rest on a single block"
    )


def test_the_refusal_changed_no_constant():
    """A priced-and-refused change must leave the pack exactly as it was."""
    p = load_pack(LIVE_PACK).params[PEAK_KEY]
    assert float(p.value) == 3.0, (
        f"{LIVE_PACK}.{PEAK_KEY} is now {p.value}; §49 refused to move it, so "
        "any change must arrive with its own evidence and retire this test"
    )
    assert float(p.value) not in LIN2009_PEAKS, (
        "the peak has been set to one of Lin & Du's positions — that is the "
        "specific transplant §49 priced and refused"
    )


# ----------------------------------------------------- the record is backed

def test_evidence_file_states_the_verdict_and_its_basis():
    """The prose must not outrun the measurement, in either direction."""
    doc = yaml.safe_load(EVIDENCE.read_text(encoding="utf-8"))
    assert doc["pack"] == LIVE_PACK
    assert doc["axis"] == PEAK_KEY
    assert doc["verdict"] == "refused"
    assert doc["verdict_basis"] == "measured"
    assert doc["peak_position_is_transplantable"] is False
    # The shape claim is upheld (3 sources) while the POSITION claim is not;
    # conflating them is the error this file exists to prevent.
    assert doc["shape"] == "peaked"
    assert doc["magnitude"] is None, (
        "a magnitude has been asserted for the peak position; the sources "
        "here do not supply the composition dependence it would need"
    )


def test_lin2009_positions_are_quoted_from_the_evidence_file():
    """The constants in this test must not drift from their source record."""
    doc = yaml.safe_load(EVIDENCE.read_text(encoding="utf-8"))
    src = next(s for s in doc["sources"] if s["id"] == "lin2009")
    quoted = tuple(src["peak_wt_pct_h2o2_by_dilution"].values())
    assert quoted == LIN2009_PEAKS, (
        f"this test uses {LIN2009_PEAKS} but the evidence file records "
        f"{quoted} — one of them has drifted"
    )
    assert "10.1149/1.3096490" in src["citation"]
