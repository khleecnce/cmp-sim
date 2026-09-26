"""Attribute each scored dataset's residual to a CAUSE, and count the causes.

Why this exists
---------------
Four consecutive runs reduced the model's fitted-constant count (the pH law was
falsified, the size exponent re-attributed to abrasive material, the
concentration exponent replaced by a derived +1/3) and the corpus median did
not move once: 19.5 % shape after all four. That is a measurement, not bad
luck. Before another constant is touched, the residual has to be DECOMPOSED, so
the next law is chosen by evidence instead of by guess.

Every scored dataset lands in exactly one bucket, in this order:

1. ``noise_floor``  — the error is already at the dataset's OWN replicate
   scatter (``Score.at_noise_floor``). Irreducible by any model: fitting
   further fits that paper's noise.
2. ``no_constant``  — the model's rate does NOT RESPOND to any axis the dataset
   varies. The pack is declaring a gap (or a regime gate is switched on), so
   the prediction is effectively one number for a ladder of measurements.
   Cannot improve without new literature; improving it by inventing a constant
   is forbidden.
3. ``responsive_miss`` — the model DOES respond to at least one varied axis,
   has enough levels for the response to be tested, and still misses. **This is
   the only bucket where a better law lowers the median.**
4. ``few_levels``   — responds, but the varied axes carry <= 2 distinct levels
   (or < 4 scorable rows), so the shape error is arithmetically dominated by
   one or two readings and a trend cannot be distinguished from an offset.

Responsiveness is MEASURED, not declared: for each varied axis the tool takes
one baseline row, rebuilds it at the axis minimum and at the axis maximum seen
in that dataset, runs the real simulator on both, and asks whether the
predicted rate moved by more than ``INERT_TOLERANCE``. That is the same
question a reader would ask ("does this input reach the output?") and it cannot
be fooled by a constant that exists in a YAML file but never reaches the rate.

This module MEASURES ONLY. It fits nothing and must never modify a pack.
Usage: ``python tools/residual_census.py`` (inside ``.venv``).
"""
from __future__ import annotations

import statistics
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

from cmp_sim.core.predictive_score import (
    PACK_FILM, Score, _measured, _recipe_for, score_all,
)
from cmp_sim.core.validation import dataset_paths

#: A predicted-rate change below this, end to end across the dataset's own
#: range of an axis, means the axis does not reach the rate at all. 0.5 % is
#: far below any measured CMP response and far above float noise.
INERT_TOLERANCE = 0.5

BUCKETS = ("noise_floor", "no_constant", "responsive_miss", "few_levels")


@dataclass
class Census:
    dataset: str
    film: str
    shape: float
    n: int
    axes: List[str] = field(default_factory=list)
    #: axis -> end-to-end percentage change in PREDICTED rate over the
    #: dataset's own range of that axis. None when the pair could not be run.
    response: Dict[str, Optional[float]] = field(default_factory=dict)
    bucket: str = ""

    @property
    def responsive_axes(self) -> List[str]:
        return [a for a, r in self.response.items()
                if r is not None and r >= INERT_TOLERANCE]


def _axis_value(row: Dict[str, Any], axis: str) -> Any:
    if axis == "pressure":
        return row.get("pressure_psi")
    if axis == "velocity":
        return row.get("rpm_platen")
    return (row.get("overrides") or {}).get(axis)


def _with_axis(row: Dict[str, Any], axis: str, value: Any) -> Dict[str, Any]:
    new = {k: (dict(v) if isinstance(v, dict) else v) for k, v in row.items()}
    if axis == "pressure":
        new["pressure_psi"] = value
    elif axis == "velocity":
        new["rpm_platen"] = value
    else:
        overrides = dict(new.get("overrides") or {})
        overrides[axis] = value
        new["overrides"] = overrides
    return new


def _predict(doc: Dict[str, Any], row: Dict[str, Any]) -> Optional[float]:
    from cmp_sim.api import run_recipe
    try:
        result = run_recipe(_recipe_for(doc, row))
    except Exception:
        return None
    value = result.get("removal_rate_A_per_min")
    return None if value in (None, 0) else float(value)


def _axis_response(doc: Dict[str, Any], rows: List[Dict[str, Any]],
                   axis: str) -> Optional[float]:
    """End-to-end % change in predicted rate across this axis' own range.

    The baseline is the dataset's FIRST row, so every other input stays at a
    combination the paper actually ran; only the axis under test is swapped.
    """
    values = sorted({v for v in (_axis_value(r, axis) for r in rows)
                     if isinstance(v, (int, float))})
    if len(values) < 2:
        return None
    lo = _predict(doc, _with_axis(rows[0], axis, values[0]))
    hi = _predict(doc, _with_axis(rows[0], axis, values[-1]))
    if lo is None or hi is None:
        return None
    return 100.0 * abs(hi - lo) / max(hi, lo)


def _levels(rows: List[Dict[str, Any]], axes: List[str]) -> int:
    """Most distinct levels any single one of these axes carries."""
    best = 0
    for axis in axes:
        values = {v for v in (_axis_value(r, axis) for r in rows)
                  if v is not None}
        best = max(best, len(values))
    return best


def census(scores: Optional[List[Score]] = None) -> List[Census]:
    scores = scores if scores is not None else score_all()
    by_name = {s.dataset: s for s in scores if s.shape_mape is not None}
    out: List[Census] = []
    for path in dataset_paths():
        score = by_name.get(Path(path).stem)
        if score is None:          # unscorable; already explained by the report
            continue
        doc = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
        rows = [r for r in (doc.get("conditions") or [])
                if _measured(r) is not None]
        rec = Census(dataset=score.dataset,
                     film=score.film or str(PACK_FILM.get(str(doc.get("pack")), "?")),
                     shape=float(score.shape_mape), n=score.n,
                     axes=list(score.axes))
        for axis in score.axes:
            rec.response[axis] = _axis_response(doc, rows, axis)

        if score.at_noise_floor:
            rec.bucket = "noise_floor"
        elif not rec.responsive_axes:
            rec.bucket = "no_constant"
        elif score.n < 4 or _levels(rows, rec.responsive_axes) < 3:
            rec.bucket = "few_levels"
        else:
            rec.bucket = "responsive_miss"
        out.append(rec)
    return out


def report(records: Optional[List[Census]] = None) -> str:
    records = records if records is not None else census()
    lines = [f"{'dataset':44s} {'film':8s} {'n':>3s} {'shape%':>7s}  "
             f"{'bucket':16s} responsive axes (end-to-end % of predicted rate)",
             "-" * 140]
    for rec in sorted(records, key=lambda r: (r.bucket, -r.shape)):
        detail = ", ".join(
            f"{a}{'' if r is None else f' {r:.0f}%'}"
            f"{' INERT' if (r is not None and r < INERT_TOLERANCE) else ''}"
            f"{' unrunnable' if r is None else ''}"
            for a, r in rec.response.items())
        lines.append(f"{rec.dataset[:44]:44s} {rec.film[:8]:8s} {rec.n:3d} "
                     f"{rec.shape:7.1f}  {rec.bucket:16s} {detail}")
    lines.append("")
    lines.append(f"{len(records)} scored datasets, "
                 f"{sum(r.n for r in records)} measured points")
    for bucket in BUCKETS:
        group = [r for r in records if r.bucket == bucket]
        if not group:
            lines.append(f"  {bucket:16s} 0")
            continue
        med = statistics.median(r.shape for r in group)
        lines.append(f"  {bucket:16s} {len(group):2d} datasets, "
                     f"{sum(r.n for r in group):3d} points, "
                     f"median shape {med:.1f}%")
    improvable = [r for r in records if r.bucket == "responsive_miss"]
    overall = statistics.median(r.shape for r in records)
    lines.append("")
    lines.append(f"corpus median {overall:.1f}% — the ONLY bucket a better law "
                 f"can move is responsive_miss ({len(improvable)}/{len(records)} "
                 f"datasets, "
                 f"{100.0 * sum(r.n for r in improvable) / sum(r.n for r in records):.0f}% "
                 "of points)")
    return "\n".join(lines)


if __name__ == "__main__":
    print(report())
