"""Exhaustively find every INERT axis in the corpus, and classify each one.

Why this exists
---------------
The 16th run was investigating one dataset (``jani2025``) and stumbled on two
axes the model did not respond to at all. That was luck, not method: the other
45 datasets had never been examined the same way. An inert axis is the only
error class that is fixable with **zero new constants** -- the term already
exists somewhere and simply is not being called -- so it is the cheapest thing
in the whole programme to check, and the easiest to mistake for missing
physics.

It matters more than it looks. ``tools/axis_error_census.py`` (STATUS §14)
classified 145 points as "owned by no axis" and read that as "the error has no
single cause, which is what a healthy model looks like on a clean sweep". A
**missing wire looks exactly the same** from the census's point of view: an
input that never reaches the rate cannot own any of the residual either. So
the closure arguments of §14-§17 were all computed without anyone first
checking that every swept input is actually connected. This module performs
that check.

Method (measurement only -- nothing is fitted, no pack is modified)
-------------------------------------------------------------------
For every scored dataset and every axis it varies, take the dataset's own
first row, rebuild it at the axis minimum and at the axis maximum the paper
actually ran, run the real simulator on both, and compare the predicted rates.
A change below ``INERT_TOLERANCE`` (0.5 %, shared with residual_census) means
the input does not reach the output.

Each inert axis is then classified into exactly one of three kinds, and the
classification -- not the count -- is the product of this tool:

``declared``
    The engine SAYS SO. A warning naming the axis, or a blanket declaration
    ("chemistry layer inactive", "not declared by pack X"), is present in the
    run's own output. The pack is honestly reporting a gap it has no data for.
    Nothing to fix: the honest state is inert-and-announced.

``wiring``
    The physics term EXISTS and is reachable, but the harness or the plumbing
    hands it the value in a form it cannot consume, so it silently declines.
    The tell is a warning that names a unit or a key rather than a gap --
    e.g. "has no concentration in the unit the model needs". This is a bug,
    and fixing it costs no constants.

``aliased``
    The dataset states the SAME physical quantity twice under two keys, and
    the other key is responsive. ``abrasive_d50_nm`` beside ``abrasive_size_nm``
    is the standing case. Nothing is disconnected; perturbing one member of the
    pair alone is simply not a perturbation of the physics. Counting these as
    faults would manufacture work and hide the real ones, so they are named
    and set aside.

``silent``
    The axis moves, the rate does not, and NOTHING in the output says why.
    This is the worst kind, because a reader cannot distinguish it from a
    model that considered the input and found it unimportant. At minimum it
    must gain a warning.

Usage: ``python tools/inert_axis_scan.py`` (inside ``.venv``).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

from cmp_sim.core.predictive_score import _measured, _recipe_for, score_all
from cmp_sim.core.validation import dataset_paths
from tools.residual_census import INERT_TOLERANCE, _axis_value, _with_axis

#: Substrings that mark a warning as a DECLARED gap rather than a silent one.
#: These are blanket declarations: they do not name the axis, but they do say
#: that a whole class of inputs is lumped into Kp, which covers the axis.
BLANKET_DECLARATIONS = (
    "chemistry layer inactive",
    "is not declared by pack",
    "no physics layer consumes",
    "no physics term reads it",
    "recorded but not yet wired",
    "not applied to the result",
    # A term the model owns, has evidence about, and deliberately DECLINES to
    # apply is declared, not silent -- provided it says so in the result. The
    # 16th run's promoter refusal is the pattern: it names the axis, prints
    # both the gain forgone and the damage avoided, and states the one
    # measurement that would unblock it.
    "held off",
    "term refused",
    "is therefore inert",
    "so pH is INERT".lower(),
    "term skipped",
    # A peaked response evaluated far from its optimum saturates onto the
    # mechanical floor, which is a MODELLED answer ("chemistry contributes
    # nothing measurable here"), not a missing wire. The warning must be in
    # the output for this to count, and it is: the floor warning names the
    # distance from the optimum.
    "rests on the mechanical floor",
    "outside the range this pack",
)

#: Substrings that mark a warning as a WIRING fault: the term is present and
#: willing, and it refused because of the SHAPE of the input (unit, key,
#: missing companion constant) rather than because the physics is unknown.
WIRING_FAULTS = (
    "no concentration in the unit the model needs",
    "so it was not applied",
)

#: Axis keys that RESTATE another axis the same dataset already varies. The
#: pair must describe one physical quantity, or this would excuse a real gap.
#: A median diameter and "the" particle size are the same measurement reported
#: twice, so a perturbation of one alone is not a perturbation of the slurry.
ALIAS_OF = {
    "abrasive_d50_nm": "abrasive_size_nm",
    "abrasive_conc_wt_pct": "abrasive_wt_pct",
    "ph": "slurry_ph",
}


#: Words that identify an axis inside a free-text warning. Derived from the
#: key by default; overridden where the key's own words are too short or too
#: generic to match ("ph" is two characters and appears inside "phase").
AXIS_SYNONYMS = {
    "slurry_ph": ("ph ", "ph-", "ph_"),
    "ph": ("ph ", "ph-", "ph_"),
}


@dataclass
class InertAxis:
    dataset: str
    axis: str
    levels: int
    n_points: int
    kind: str = "silent"
    evidence: str = ""


@dataclass
class ScanResult:
    inert: List[InertAxis] = field(default_factory=list)
    #: dataset -> axis -> end-to-end % response (None when unrunnable)
    response: Dict[str, Dict[str, Optional[float]]] = field(default_factory=dict)

    def by_kind(self, kind: str) -> List[InertAxis]:
        return [a for a in self.inert if a.kind == kind]


def _run(doc: Dict[str, Any], row: Dict[str, Any]):
    """Rate and warnings for one condition, or (None, []) if it cannot run."""
    from cmp_sim.api import run_recipe
    try:
        result = run_recipe(_recipe_for(doc, row))
    except Exception:
        return None, []
    value = result.get("removal_rate_A_per_min")
    value = None if value in (None, 0) else float(value)
    return value, list(result.get("warnings") or [])


def _classify(axis: str, warnings: List[str],
              responsive: Optional[Dict[str, Optional[float]]] = None) -> tuple:
    """(kind, evidence) for an axis the model did not respond to.

    Order matters, and each test must be about THIS axis. An earlier version
    returned "wiring" for ``promoter_M`` on the strength of a warning about
    benzotriazole, because it searched the whole warning list for any wiring
    phrase. A diagnosis that can be produced by a warning concerning a
    different species is not a diagnosis.
    """
    axis_words = AXIS_SYNONYMS.get(axis) or tuple(
        w for w in axis.lower().replace("_", " ").split()
        if len(w) > 2 and w not in ("pct", "mm", "the"))

    alias = ALIAS_OF.get(axis)
    if alias and responsive is not None:
        partner = responsive.get(alias)
        if partner is not None and partner >= INERT_TOLERANCE:
            return "aliased", (f"restates '{alias}', which the same dataset "
                               f"also varies and which moves the rate "
                               f"{partner:.0f}%")

    for w in warnings:
        low = w.lower()
        if any(f in low for f in WIRING_FAULTS) and axis.lower() in low:
            return "wiring", w
    for w in warnings:
        low = w.lower()
        if any(d in low for d in BLANKET_DECLARATIONS):
            # A blanket declaration only covers the axis if it either names it
            # or is the whole-layer kind.
            if any(word in low for word in axis_words) or "layer inactive" in low:
                return "declared", w
    return "silent", ""


def scan(scores=None) -> ScanResult:
    scores = scores if scores is not None else score_all()
    by_name = {s.dataset: s for s in scores if s.shape_mape is not None}
    out = ScanResult()
    for path in dataset_paths():
        score = by_name.get(Path(path).stem)
        if score is None:
            continue
        doc = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
        rows = [r for r in (doc.get("conditions") or [])
                if _measured(r) is not None]
        if not rows:
            continue
        out.response[score.dataset] = {}
        # Pass 1 -- measure every axis. The alias test needs the WHOLE map, so
        # nothing may be classified until the last axis has been run.
        pending: List[tuple] = []
        for axis in score.axes:
            values = sorted({v for v in (_axis_value(r, axis) for r in rows)
                             if isinstance(v, (int, float))})
            if len(values) < 2:
                out.response[score.dataset][axis] = None
                continue
            lo, w_lo = _run(doc, _with_axis(rows[0], axis, values[0]))
            hi, w_hi = _run(doc, _with_axis(rows[0], axis, values[-1]))
            if lo is None or hi is None:
                out.response[score.dataset][axis] = None
                continue
            resp = 100.0 * abs(hi - lo) / max(hi, lo)
            out.response[score.dataset][axis] = resp
            if resp < INERT_TOLERANCE:
                pending.append((axis, len(values), w_lo + w_hi))
        # Pass 2 -- classify.
        for axis, levels, warns in pending:
            kind, evidence = _classify(axis, warns, out.response[score.dataset])
            out.inert.append(InertAxis(dataset=score.dataset, axis=axis,
                                       levels=levels, n_points=score.n,
                                       kind=kind, evidence=evidence))
    return out


def report(result: Optional[ScanResult] = None) -> str:
    result = result if result is not None else scan()
    lines = ["INERT AXES — every swept input whose 2-point perturbation moves "
             f"the predicted rate by < {INERT_TOLERANCE}%", "-" * 110]
    for kind, blurb in (("wiring", "A BUG — the term exists and was handed "
                                   "the value in a form it cannot read"),
                        ("silent", "WORST — no term, and nothing says so"),
                        ("declared", "honest — the pack announces the gap"),
                        ("aliased", "not a fault — restates a responsive axis")):
        group = result.by_kind(kind)
        lines.append(f"\n[{kind}]  {len(group)} axes — {blurb}")
        for a in sorted(group, key=lambda x: (x.dataset, x.axis)):
            lines.append(f"  {a.dataset[:46]:46s} {a.axis:24s} "
                         f"{a.levels} levels, n={a.n_points}")
            if a.evidence:
                lines.append(f"      > {a.evidence[:150]}")
    total_axes = sum(len(v) for v in result.response.values())
    lines.append("")
    lines.append(f"{len(result.response)} datasets, {total_axes} swept axes, "
                 f"{len(result.inert)} inert "
                 f"({len(result.by_kind('wiring'))} wiring, "
                 f"{len(result.by_kind('silent'))} silent, "
                 f"{len(result.by_kind('declared'))} declared, "
                 f"{len(result.by_kind('aliased'))} aliased)")
    return "\n".join(lines)


if __name__ == "__main__":
    print(report())
