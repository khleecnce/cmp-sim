"""Audit the axes a dataset varies at ROW level, which no existing scan sees.

Why this probe exists
---------------------
`tools/inert_axis_scan.py` swept 94 axes and reported **0 silent** inert axes,
and `core/predictive_score._varying_axes` publishes the axis list every other
tool filters on (`Score.declined_axes_swept`, `axis_error_census`,
`median_crossing_probe`).  Both read the same two places:

* `row["pressure_psi"]`  -> the axis named ``pressure``
* `row["rpm_platen"]`    -> the axis named ``velocity``
* every key of ``row["overrides"]``

A validation row is a free-form mapping, so a dataset can vary a quantity that
lives in NEITHER place -- straight on the row, next to ``pressure_psi``.  Those
keys were invisible to the census, so the audit's "0 silent" verdict was made
without ever looking at them.  That is the reader-bug class: a negative result
that retires a question while measuring the wrong space.

What is measured
----------------
For every scored dataset, every row-level key (excluding labels, provenance and
the measured-rate fields themselves) whose value CHANGES across rows is treated
as a swept axis and perturbed on the shipping model, exactly as
`inert_axis_scan` does for override keys: predict the first row, then predict it
again with the key halved and doubled.  Each axis is classified as

  responsive          the rate moves
  declared            the rate does not move AND a warning names the axis
                      (machine-readable ``[DECLINES_AXIS: ...]``)
  prose-only          the rate does not move, a warning EXPLAINS why, but no
                      marker -- so the scorer counts the flat response as a
                      prediction (the §36 failure, recurring where §36 could
                      not look)
  silent              the rate does not move and nothing says why -- worst
  dropped             the scorer never puts the key into the recipe at all, so
                      the model is not even asked

This probe fits nothing and changes no pack.
    python -m tools.row_level_axis_scan
"""
from __future__ import annotations

import copy
from typing import Any, Dict, List, Optional, Set, Tuple

import yaml

from cmp_sim.core.declined_axes import declined_axes
from cmp_sim.core.predictive_score import (
    dataset_paths, _measured, _recipe_for, _varying_axes,
)

# Row keys that are bookkeeping, not process inputs.  Kept explicit rather than
# pattern-matched: a new measured-rate unit must be added here deliberately,
# because silently treating one as an axis would perturb the ANSWER.
NOT_AN_AXIS: Set[str] = {
    "label", "overrides", "read_method", "source", "source_detail", "notes",
    "note", "comment", "doi", "ruling",
}
_MEASURED_PREFIXES = ("mrr", "measured_mrr", "removal", "rate")
_UNCERTAINTY = ("uncertainty", "scatter", "stddev", "std_dev", "sigma", "error")
# Reported observations, not inputs: perturbing them asks the model a question
# about an output.
_OBSERVED = ("roughness_ra_nm", "defects", "wiwnu", "nonuniformity")


def is_axis_candidate(key: str) -> bool:
    if key in NOT_AN_AXIS:
        return False
    k = key.lower()
    if any(k.startswith(p) for p in _MEASURED_PREFIXES):
        return False
    if any(t in k for t in _UNCERTAINTY):
        return False
    if any(t in k for t in _OBSERVED):
        return False
    return True


def row_level_axes(rows: List[Dict[str, Any]]) -> List[str]:
    """Row-level keys whose value varies across rows."""
    keys: Set[str] = set()
    for row in rows:
        keys |= {k for k in row.keys() if is_axis_candidate(k)}
    out = []
    for key in sorted(keys):
        values = {_hashable(r.get(key)) for r in rows}
        values = {v for v in values if v is not None}
        if len(values) > 1:
            out.append(key)
    return out


def _hashable(v: Any) -> Any:
    if isinstance(v, (list, tuple)):
        return tuple(_hashable(x) for x in v)
    if isinstance(v, dict):
        return tuple(sorted((k, _hashable(x)) for k, x in v.items()))
    return v


def _predict(doc: Dict[str, Any], row: Dict[str, Any]
             ) -> Tuple[Optional[float], List[str]]:
    from cmp_sim.api import run_recipe
    try:
        result = run_recipe(_recipe_for(doc, row))
    except Exception as exc:                       # pragma: no cover - probe
        return None, [f"run failed: {exc}"]
    value = result.get("removal_rate_A_per_min")
    value = None if value in (None, 0) else float(value)
    return value, [str(w) for w in (result.get("warnings") or [])]


def classify(doc: Dict[str, Any], rows: List[Dict[str, Any]], key: str
             ) -> Dict[str, Any]:
    """Perturb `key` on the shipping model and say what happened."""
    base_row = next((r for r in rows
                     if isinstance(r.get(key), (int, float)) and r.get(key)),
                    None)
    if base_row is None:
        return {"axis": key, "verdict": "non-numeric", "detail":
                "levels are not numbers, so a 2x perturbation is undefined"}
    base, warns = _predict(doc, base_row)
    if base is None:
        return {"axis": key, "verdict": "unscorable", "detail": "; ".join(warns[:1])}

    reached = False
    for factor in (0.5, 2.0):
        row = copy.deepcopy(base_row)
        row[key] = base_row[key] * factor
        value, _ = _predict(doc, row)
        if value is None or abs(value / base - 1.0) > 1e-9:
            reached = True
    if reached:
        return {"axis": key, "verdict": "responsive"}

    # Inert.  Is the model's silence readable, explained, or absent?
    if key in declined_axes(warns):
        return {"axis": key, "verdict": "declared",
                "detail": next(w for w in warns if key in w)}
    mentions = [w for w in warns if key in w or key.replace("_", " ") in w]
    # The recipe builder is the other way an axis can go nowhere: if the key
    # never lands in the recipe, the model was not asked in the first place.
    recipe = _recipe_for(doc, base_row)
    if not _mentioned_in(recipe, key):
        return {"axis": key, "verdict": "dropped",
                "detail": "the scorer's _recipe_for never puts this key into "
                          "the recipe, so the model is not asked about it"}
    if mentions:
        return {"axis": key, "verdict": "prose-only", "detail": mentions[0]}
    return {"axis": key, "verdict": "silent", "detail": ""}


def _mentioned_in(obj: Any, key: str) -> bool:
    if isinstance(obj, dict):
        return any(k == key or _mentioned_in(v, key) for k, v in obj.items())
    if isinstance(obj, list):
        return any(_mentioned_in(v, key) for v in obj)
    return False


def scan() -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    for path in dataset_paths():
        doc = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        rows = [r for r in (doc.get("conditions") or []) if _measured(r) is not None]
        if len(rows) < 3:
            continue
        published = set(_varying_axes(rows))
        for key in row_level_axes(rows):
            if key in ("pressure_psi", "rpm_platen"):
                continue          # published as `pressure` / `velocity`
            verdict = classify(doc, rows, key)
            verdict["dataset"] = path.stem
            verdict["n"] = len(rows)
            verdict["levels"] = len({_hashable(r.get(key)) for r in rows} - {None})
            verdict["published_as_axis"] = key in published
            out.append(verdict)
    return out


def report(rows: List[Dict[str, Any]]) -> str:
    lines = ["ROW-LEVEL swept axes (invisible to _varying_axes and "
             "inert_axis_scan)", ""]
    order = ["silent", "prose-only", "dropped", "declared", "responsive",
             "non-numeric", "unscorable"]
    for verdict in order:
        group = [r for r in rows if r["verdict"] == verdict]
        if not group:
            continue
        lines.append(f"[{verdict}]  {len(group)} axis-dataset pair(s)")
        for r in group:
            lines.append(f"  {r['dataset']:46s} {r['axis']:18s} "
                         f"{r['levels']} levels, n={r['n']}, "
                         f"published={'yes' if r['published_as_axis'] else 'NO'}")
            if r.get("detail"):
                lines.append(f"      > {r['detail'][:150]}")
        lines.append("")
    published = sum(1 for r in rows if r["published_as_axis"])
    lines.append(f"{len(rows)} row-level swept axes across the corpus, "
                 f"{published} of them published by _varying_axes")
    return "\n".join(lines)


if __name__ == "__main__":
    print(report(scan()))
