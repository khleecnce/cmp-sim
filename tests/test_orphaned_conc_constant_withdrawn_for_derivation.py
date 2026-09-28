r"""§55: a fitted constant was orphaned by a dataset re-assignment, and the
DERIVATION it was masking is better on every block under its pack.

WHAT THIS FILE PINS
-------------------
Three separable claims, each re-measured at run time (nothing here is a
literal pinned from the session that made the change):

 1. THE ORPHAN IS REAL.  `abrasive_conc_half_wt_pct` on `sic_ceria_h2o2` was
    declared null and justified by an ENUMERATION of six iso-condition
    loading ladders, of which the decisive falling one was Entegris
    US20220315802A1.  Ruling #49-B moved that dataset to the
    `sic_alumina_kmno4` pack.  Re-running the enumeration must find ZERO
    falling ladders under `sic_ceria_h2o2`.  This is the §52 rule ("an
    absence-of-data claim is a MEASUREMENT and it expires -- re-RUN it,
    never re-read it") applied to an enumeration of the corpus rather than
    of the literature.

 2. THE REPAIR IS A WITHDRAWAL, NOT A REFIT.  `abrasive_conc_exponent` is
    now null, so the engine's own three-factor decomposition supplies
    n_C = p*(1-alpha*chi).  The test asserts the pack declares NO value and
    that the axis still MOVES the rate -- a withdrawal that silenced the
    axis would be the §20 failure (inert is acceptable, silently inert is
    not) wearing a derivation's clothes.

 3. THE PRICE WAS PAID IN THE RIGHT DIRECTION.  Priced through the SHIPPING
    solver on every block under the pack: 0 worse.  The two blocks that
    improve are both held out.  And -- the load-bearing half -- the
    saturating alternative C_half is measured to be WORSE than the
    derivation at every value scanned, so the dissolved contradiction did
    NOT license fitting a saturation constant.

WHY THE THIRD CLAIM MATTERS MOST
--------------------------------
A refusal whose stated reason dissolves is exactly the moment a project
starts fitting: the obstacle is gone, so the constant "may" now be filled.
§51's lesson is that the DECISION usually survives for a different reason.
Here it does, and the reason is measured rather than argued: one ladder
cannot identify a saturation constant, and the form it would compete with
is already derived.
"""
from __future__ import annotations

import copy
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import pytest
import yaml

from cmp_sim.core.params import load_pack
from cmp_sim.core.predictive_score import _measured, _predict_with_gate
from cmp_sim.core.validation import dataset_paths
from tools.sic_conc_half_refusal_reaudit import PACK, ladders

CONC_KEY = "abrasive_conc_exponent"
HALF_KEY = "abrasive_conc_half_wt_pct"

#: The departed dataset whose falling ladder was the refusal's decisive
#: counter-example. Named so the test says WHICH claim expired.
DEPARTED = "entegris2022_us20220315802a1_sic_alumina_conc"
DEPARTED_NOW_BELONGS_TO = "sic_alumina_kmno4"

#: C_half values scanned when pricing the saturating alternative (wt%).
#: Spans from well below the pack's reference loading to above its declared
#: saturation concentration, so a favourable value cannot hide between them.
CHALF_SCAN = (1.0, 2.0, 2.5, 4.0, 6.0, 8.0)


# ── shared measurement helpers ──────────────────────────────────────────
def _pack_docs() -> List[Tuple[Path, Dict[str, Any]]]:
    out = []
    for path in dataset_paths():
        try:
            doc = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        except Exception:
            continue
        if str(doc.get("pack") or "") == PACK:
            out.append((path, doc))
    return out


def _shape_mape(doc: Dict[str, Any]) -> Optional[float]:
    """Shape MAPE with ONE free scale -- the scorer's own convention."""
    rows = [r for r in (doc.get("conditions") or []) if _measured(r) is not None]
    ms: List[float] = []
    ps: List[float] = []
    for row in rows:
        value, _gate, _declined = _predict_with_gate(doc, row)
        if value is None:
            return None
        ms.append(float(_measured(row)))
        ps.append(float(value))
    if len(ms) < 3:
        return None
    scale = sum(m * p for m, p in zip(ms, ps)) / sum(p * p for p in ps)
    return 100.0 * sum(abs(scale * p - m) / m for m, p in zip(ms, ps)) / len(ms)


def _with_override(doc: Dict[str, Any], key: str, value: Any) -> Dict[str, Any]:
    out = copy.deepcopy(doc)
    for row in out.get("conditions") or []:
        row.setdefault("overrides", {})[key] = value
    return out


@pytest.fixture(scope="module")
def pack_docs() -> List[Tuple[Path, Dict[str, Any]]]:
    docs = _pack_docs()
    assert docs, (
        f"no dataset is predicted by {PACK}; this whole file would then pass "
        "by vacuity, which is indistinguishable from a deleted check")
    return docs


@pytest.fixture(scope="module")
def shipping(pack_docs) -> Dict[str, float]:
    out = {}
    for path, doc in pack_docs:
        val = _shape_mape(doc)
        if val is not None:
            out[path.stem] = val
    assert len(out) >= 3, out
    return out


# ── claim 1: the orphan is real, and it is real TODAY ───────────────────
def test_the_refusals_decisive_counterexample_left_this_pack():
    """The falling ladder the null cited is no longer this pack's dataset."""
    rows = {r["dataset"]: r for r in ladders()}
    assert DEPARTED in rows, (
        f"{DEPARTED} is no longer an iso-condition loading ladder in the "
        "corpus at all; re-measure the refusal rather than editing this test")
    assert rows[DEPARTED]["pack"] == DEPARTED_NOW_BELONGS_TO, (
        f"{DEPARTED} is predicted by {rows[DEPARTED]['pack']}, not "
        f"{DEPARTED_NOW_BELONGS_TO}; the orphan finding must be re-measured")
    assert rows[DEPARTED]["slope"] < 0, (
        "the departed ladder no longer falls, so the note's description of it "
        "is stale in a second way")


def test_no_falling_loading_ladder_remains_under_this_pack():
    """The contradiction that justified the null has dissolved.

    EXIT CONDITION. If a falling ladder ever returns under this pack, the
    original reasoning is live again and the null must be re-argued on it.
    """
    mine = [r for r in ladders() if r["pack"] == PACK]
    assert mine, (
        f"{PACK} has no iso-condition loading ladder at all; the C_half note "
        "cannot be checked and must be re-measured, not re-read")
    falling = [r for r in mine if r["slope"] < 0]
    assert not falling, (
        "a falling loading ladder is back under this pack: "
        f"{[(r['dataset'], round(r['slope'], 3)) for r in falling]}. "
        "Re-open the C_half refusal's original reasoning.")


def test_one_ladder_cannot_identify_a_saturation_constant():
    """The null's NEW reason: identifiability, not contradiction.

    EXIT CONDITION. A second iso-condition ladder under this pack makes the
    saturation constant identifiable and this test fails, demanding the
    refusal be re-priced.
    """
    mine = [r for r in ladders() if r["pack"] == PACK]
    assert len(mine) == 1, (
        f"{len(mine)} loading ladders now sit under {PACK} "
        f"({[r['dataset'] for r in mine]}); C_half may now be identifiable -- "
        "re-price it rather than editing this bar")


def test_the_pack_note_records_the_expiry_rather_than_hiding_it():
    """§51: keep the superseded reasoning, marked superseded in place."""
    note = str(load_pack(PACK).params[HALF_KEY].note or "")
    assert "RE-AUDIT" in note, "the note does not say its enumeration expired"
    assert "EXIT CONDITION" in note, "a refusal with no exit condition is permanent by accident"
    assert "966.7" in note, (
        "the superseded enumeration was DELETED rather than marked superseded; "
        "how a wrong scope failed is the lesson (docs/limits.md §51)")


# ── claim 2: the repair is a withdrawal, and the axis still lives ───────
def test_the_fitted_concentration_exponent_is_withdrawn():
    param = load_pack(PACK).params[CONC_KEY]
    assert param.value is None, (
        f"{CONC_KEY} is back at {param.value!r}. It was withdrawn so the "
        "engine's derived n_C = p*(1-alpha*chi) acts; restoring a fitted "
        "value re-introduces a constant the derivation replaces.")
    note = str(param.note or "")
    assert "WITHDRAWN" in note and "n_C" in note, note[:200]


def test_withdrawing_the_constant_did_not_silence_the_axis(pack_docs):
    """Inert is acceptable; silently inert is not (docs/limits.md §20).

    A null that made loading stop moving the rate would score identically to
    a working derivation on blocks that do not sweep loading, and would be a
    regression dressed as a simplification.
    """
    moved = []
    for _path, doc in pack_docs:
        rows = [r for r in (doc.get("conditions") or []) if _measured(r) is not None]
        if not rows:
            continue
        row = rows[0]
        base, _g, _d = _predict_with_gate(doc, row)
        if base is None:
            continue
        bumped = copy.deepcopy(doc)
        bumped["conditions"] = [copy.deepcopy(row)]
        ov = bumped["conditions"][0].setdefault("overrides", {})
        current = ov.get("abrasive_wt_pct")
        ov["abrasive_wt_pct"] = (float(current) * 3.0) if current else 9.0
        after, _g2, _d2 = _predict_with_gate(bumped, bumped["conditions"][0])
        if after is None:
            continue
        moved.append(abs(after - base) / base)
    assert moved, "no block could be perturbed; the check is vacuous"
    assert max(moved) > 0.01, (
        "tripling the abrasive loading moves the rate by at most "
        f"{100 * max(moved):.4f}% on every block under {PACK}. The withdrawal "
        "silenced the axis instead of handing it to the derivation.")


def test_the_derived_exponent_is_positive_and_bounded(pack_docs):
    """The derivation's structural bounds, asserted on what actually runs.

    n_C = p*(1-alpha*chi) with p <= 1 and 0 <= 1-alpha*chi <= 1, so the
    applied exponent cannot leave [0, 1]. Measured by perturbing loading on
    the shipping solver rather than by reading the source: measured
    overrides and regime substitutions mean the pack value is often not
    what acts (docs/limits.md §28).
    """
    import math

    slopes = []
    for _path, doc in pack_docs:
        rows = [r for r in (doc.get("conditions") or []) if _measured(r) is not None]
        if not rows:
            continue
        row = rows[0]
        ov = (row.get("overrides") or {})
        c0 = float(ov.get("abrasive_wt_pct") or 0) or 4.0
        pair = []
        for c in (c0, c0 * 2.0):
            probe = copy.deepcopy(doc)
            probe["conditions"] = [copy.deepcopy(row)]
            probe["conditions"][0].setdefault("overrides", {})["abrasive_wt_pct"] = c
            val, _g, _d = _predict_with_gate(probe, probe["conditions"][0])
            if val is None:
                break
            pair.append((c, val))
        if len(pair) == 2 and pair[0][1] > 0 and pair[1][1] > 0:
            (ca, ra), (cb, rb) = pair
            slopes.append(math.log(rb / ra) / math.log(cb / ca))
    assert slopes, "no block yielded a measurable loading slope"
    for s in slopes:
        assert -1e-6 <= s <= 1.0 + 1e-6, (
            f"applied loading exponent {s:+.3f} is outside the structural "
            "bound [0, 1] of p*(1-alpha*chi)")
    assert max(slopes) > 0.05, (
        f"the largest applied loading exponent is {max(slopes):+.3f}; the "
        "derivation is supposed to supply a positive surface-area exponent")


# ── claim 3: the price, and the alternative that was refused ────────────
def test_the_withdrawal_makes_no_block_worse(pack_docs, shipping):
    """0 worse is the claim; re-measured against the restored fitted value."""
    worse = []
    for path, doc in pack_docs:
        if path.stem not in shipping:
            continue
        restored = _shape_mape(_with_override(doc, CONC_KEY, 0.227))
        if restored is None:
            continue
        if shipping[path.stem] > restored + 1e-6:
            worse.append((path.stem, restored, shipping[path.stem]))
    assert not worse, (
        "withdrawing the fitted exponent made these blocks WORSE: "
        f"{[(n, round(a, 2), round(b, 2)) for n, a, b in worse]}. The "
        "withdrawal was adopted on 0-worse; re-measure the decision.")


def test_the_withdrawal_improves_a_held_out_block(pack_docs, shipping):
    """A change that improves nothing held out is not evidence of anything."""
    improved_heldout = []
    for path, doc in pack_docs:
        if path.stem not in shipping or doc.get("used_for_calibration"):
            continue
        restored = _shape_mape(_with_override(doc, CONC_KEY, 0.227))
        if restored is not None and restored > shipping[path.stem] + 1.0:
            improved_heldout.append(path.stem)
    assert improved_heldout, (
        "no HELD-OUT block improves by more than 1 pp from the withdrawal; "
        "the change would then rest on calibration blocks only")


def test_the_saturating_alternative_is_refused_by_measurement(pack_docs, shipping):
    """The dissolved contradiction did NOT license fitting C_half.

    Every scanned saturation constant must leave the pack's loading block
    worse than the derivation. If one ever beats it, that is a finding and
    this test must be re-run, not relaxed.
    """
    target = None
    for path, doc in pack_docs:
        axes = {k for r in (doc.get("conditions") or [])
                for k in (r.get("overrides") or {})
                if len({(rr.get("overrides") or {}).get(k)
                        for rr in (doc.get("conditions") or [])}) > 1}
        if "abrasive_wt_pct" in axes and path.stem in shipping:
            target = (path, doc)
            break
    assert target is not None, (
        "no block under this pack sweeps abrasive loading, so C_half cannot "
        "be priced at all; the refusal's new reason must be re-derived")
    path, doc = target
    base = shipping[path.stem]
    beats = []
    for ch in CHALF_SCAN:
        val = _shape_mape(_with_override(doc, HALF_KEY, ch))
        if val is not None and val < base - 1e-6:
            beats.append((ch, val))
    assert not beats, (
        f"a saturation constant now beats the derivation on {path.stem} "
        f"(base {base:.2f}%): {[(c, round(v, 2)) for c, v in beats]}. "
        "Re-price the refusal; do not relax this bar.")


def test_the_probe_never_writes():
    """A ladder enumeration is one session away from becoming a fitter."""
    src = Path(__file__).resolve().parents[1] / "tools" / "sic_conc_half_refusal_reaudit.py"
    text = src.read_text(encoding="utf-8")
    for forbidden in ("write_text", "yaml.dump", "yaml.safe_dump", "open("):
        assert forbidden not in text, (
            f"{src.name} contains {forbidden!r}; a probe that writes can turn "
            "a per-block measurement into a per-block constant")
