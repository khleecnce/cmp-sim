"""WHICH AXIS carries the improvable error, weighted by POINTS?

Why this script exists
----------------------
Four axes were closed in a row (pH, velocity exponent, pressure saturation,
P-V interaction) and the corpus median moved by ~1 pp in total. The reason is
now visible in hindsight: every one of those axes was THIN. The velocity
closure touched 29 measured points, the P-V closure 24, out of 427. Each run
picked its axis by which mechanism looked derivable, never by which axis
carries the error.

``tools/residual_census.py`` answers "which BUCKET is improvable" (35 datasets
/ 342 points in ``responsive_miss``). It does not answer "improvable ALONG
WHAT". This script does, and it reports POINTS, never dataset counts, because a
median over 46 datasets moves by re-ranking rather than by getting anything
right (pinned by test in the 11th run).

The reading was pre-registered in STATUS.md before this was run:

1. If one axis holds >= 30 % of ``responsive_miss`` POINTS, that axis is the
   next target regardless of how attractive its physics looks.
2. If no axis holds >= 30 %, the error is DISTRIBUTED, and the honest reading
   is that <= 10 % is not reachable by adding laws one axis at a time. That
   argument then belongs in ``docs/limits.md`` as evidence for the <= 15 %
   allowance -- as an argument about what sets the floor, not as "it is hard".

HOW AN AXIS IS BLAMED (this is the whole method)
-----------------------------------------------
Correlation of the residual with an axis is NOT used to blame it. A residual
can correlate with pressure simply because pressure correlates with whatever
the real cause is, and in a Taguchi array several axes move together.

Instead each axis is priced by an ORACLE, exactly as the P-V axis was priced
in the 11th run: grant the model ONE extra free exponent on that axis alone,

    predicted' = predicted * (x / x_ref) ** b        b fitted per dataset,

fit b by least squares in log space together with the single free scale the
shape score already allows, and re-measure the shape MAPE. The drop is the
MOST any closed-form law on that axis could buy in this dataset, because a
free per-dataset exponent is strictly more powerful than any law with shared
constants: a real law has to use ONE exponent for every dataset, the oracle
gets a fresh one for each. An oracle gain is therefore an upper bound, and a
SMALL oracle gain is the informative outcome -- it closes the axis.

The axis with the largest oracle gain in a dataset owns that dataset's points.
Datasets whose best oracle buys less than ``OWNERSHIP_MIN_GAIN`` pp are owned
by nobody and counted as ``distributed``: their error does not live on any one
axis they sweep, so no single-axis law can reach it.

This module MEASURES ONLY. It fits nothing into any pack and must never modify
one. The exponents it fits exist for the duration of the process and are
thrown away; that is what makes them an oracle rather than a model.

Usage: ``python tools/axis_error_census.py`` (inside ``.venv``).
"""
from __future__ import annotations

import math
import statistics
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import yaml

from cmp_sim.core.predictive_score import _measured, _recipe_for, score_all
from cmp_sim.core.validation import dataset_paths
from tools.residual_census import (
    INERT_TOLERANCE, _axis_value, census,
)

#: An oracle gain below this (percentage points of shape MAPE) does not buy an
#: axis the ownership of a dataset. 2 pp is the scale of the whole corpus
#: movement produced by the four closed axes combined, so an axis that cannot
#: clear it inside a single dataset -- with a free exponent, its best possible
#: case -- is not where the error lives.
OWNERSHIP_MIN_GAIN = 2.0

#: Axes needing at least this many distinct levels for an exponent to be
#: meaningful. With 2 levels a free exponent passes exactly through both points
#: and reports a gain that is interpolation, not a law.
MIN_LEVELS = 3


@dataclass
class AxisPrice:
    axis: str
    levels: int
    gain_pp: Optional[float] = None      # shape MAPE drop granted by the oracle
    exponent: Optional[float] = None     # the oracle's fitted b (diagnostic)


@dataclass
class DatasetPrice:
    dataset: str
    film: str
    n: int
    shape: float
    prices: List[AxisPrice] = field(default_factory=list)
    owner: str = "distributed"
    best_gain: float = 0.0
    residual_after: Optional[float] = None


def _predict_rows(doc: Dict[str, Any],
                  rows: List[Dict[str, Any]]) -> Optional[List[float]]:
    from cmp_sim.api import run_recipe
    out = []
    for row in rows:
        try:
            result = run_recipe(_recipe_for(doc, row))
        except Exception:
            return None
        value = result.get("removal_rate_A_per_min")
        if value in (None, 0):
            return None
        out.append(float(value))
    return out


def _shape_mape(measured: List[float], predicted: List[float]) -> float:
    """The scored quantity: MAPE after ONE free multiplicative scale."""
    scale = (sum(m * p for m, p in zip(measured, predicted))
             / sum(p * p for p in predicted))
    return 100.0 * sum(abs(scale * p - m) / m
                       for m, p in zip(measured, predicted)) / len(measured)


def _oracle(measured: List[float], predicted: List[float],
            x: List[float]) -> Tuple[float, float]:
    """Best (shape MAPE, exponent) when one free exponent on x is granted.

    b is fitted by ordinary least squares on log(measured/predicted) against
    log(x), which is the maximum-likelihood fit for multiplicative error and
    matches how the shape score's free scale works (a ratio, not an offset).
    MAPE is then re-measured the ordinary way, so the number stays comparable
    with every other shape figure in the repository.
    """
    lx = [math.log(v) for v in x]
    ly = [math.log(m / p) for m, p in zip(measured, predicted)]
    mx = sum(lx) / len(lx)
    my = sum(ly) / len(ly)
    sxx = sum((v - mx) ** 2 for v in lx)
    if sxx <= 0:
        return _shape_mape(measured, predicted), 0.0
    b = sum((v - mx) * (w - my) for v, w in zip(lx, ly)) / sxx
    xr = math.exp(mx)                                  # reference: geometric mean
    boosted = [p * (v / xr) ** b for p, v in zip(predicted, x)]
    return _shape_mape(measured, boosted), b


def price(records=None) -> List[DatasetPrice]:
    records = records if records is not None else census()
    scores = {s.dataset: s for s in score_all()}
    by_name = {r.dataset: r for r in records if r.bucket == "responsive_miss"}
    out: List[DatasetPrice] = []
    for path in dataset_paths():
        rec = by_name.get(Path(path).stem)
        if rec is None:
            continue
        doc = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
        rows = [r for r in (doc.get("conditions") or [])
                if _measured(r) is not None]
        predicted = _predict_rows(doc, rows)
        if predicted is None:
            continue
        measured = [float(_measured(r)) for r in rows]
        # Reproduce the scored shape from this run so the gains below are
        # differences against the SAME number the report publishes.
        base = _shape_mape(measured, predicted)
        dp = DatasetPrice(dataset=rec.dataset, film=rec.film, n=len(rows),
                          shape=base)
        for axis, response in rec.response.items():
            if response is None or response < INERT_TOLERANCE:
                continue                    # axis never reaches the rate
            values = [_axis_value(r, axis) for r in rows]
            if any(not isinstance(v, (int, float)) or v <= 0 for v in values):
                continue                    # log-space oracle needs positives
            levels = len(set(values))
            ap = AxisPrice(axis=axis, levels=levels)
            if levels >= MIN_LEVELS:
                mape, b = _oracle(measured, predicted, [float(v) for v in values])
                ap.gain_pp = base - mape
                ap.exponent = b
            dp.prices.append(ap)
        priced = [p for p in dp.prices if p.gain_pp is not None]
        if priced:
            best = max(priced, key=lambda p: p.gain_pp)
            dp.best_gain = best.gain_pp
            if best.gain_pp >= OWNERSHIP_MIN_GAIN:
                dp.owner = best.axis
                dp.residual_after = base - best.gain_pp
        out.append(dp)
    return out


def shared_exponent_bound(prices: List[DatasetPrice],
                          axis: str) -> Optional[Dict[str, Any]]:
    """Price a REAL law on one axis: ONE exponent shared by every dataset.

    The per-dataset oracle above is an upper bound that no law can attain,
    because a law carries the same constant into every dataset. This scans a
    single shared exponent offset ``db`` over the datasets that sweep ``axis``
    with enough levels, keeping each dataset's own free scale, and reports the
    best achievable SUM of shape MAPE. If the oracle exponents disagree in
    SIGN, the best shared value is near zero and the axis is closed to any
    closed-form law, however large the per-dataset gains looked.
    """
    members = [(dp, p) for dp in prices for p in dp.prices
               if p.axis == axis and p.gain_pp is not None]
    if len(members) < 2:
        return None
    cached: List[Tuple[List[float], List[float], List[float]]] = []
    for dp, _ in members:
        path = next((q for q in dataset_paths() if Path(q).stem == dp.dataset), None)
        if path is None:
            continue
        doc = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
        rows = [r for r in (doc.get("conditions") or [])
                if _measured(r) is not None]
        predicted = _predict_rows(doc, rows)
        if predicted is None:
            continue
        measured = [float(_measured(r)) for r in rows]
        x = [float(_axis_value(r, axis)) for r in rows]
        cached.append((measured, predicted, x))
    if len(cached) < 2:
        return None

    def total(db: float) -> float:
        acc = 0.0
        for measured, predicted, x in cached:
            xr = math.exp(sum(math.log(v) for v in x) / len(x))
            boosted = [p * (v / xr) ** db for p, v in zip(predicted, x)]
            acc += _shape_mape(measured, boosted)
        return acc

    grid = [(-1.5 + 0.01 * i) for i in range(301)]
    best_db = min(grid, key=total)
    base = total(0.0) / len(cached)
    best = total(best_db) / len(cached)
    oracle = statistics.mean(p.gain_pp for _, p in members)
    return {"axis": axis, "datasets": len(cached), "db": best_db,
            "mean_shape_before": base, "mean_shape_after": best,
            "shared_gain_pp": base - best, "oracle_gain_pp": oracle,
            "exponents": sorted(round(p.exponent, 2) for _, p in members)}


def report(prices: Optional[List[DatasetPrice]] = None) -> str:
    prices = prices if prices is not None else price()
    lines = [f"{'dataset':44s} {'film':6s} {'n':>3s} {'shape%':>7s} "
             f"{'owner':18s} {'gain':>6s} {'left':>6s}  per-axis oracle gain (pp)",
             "-" * 150]
    for dp in sorted(prices, key=lambda d: -d.n):
        detail = ", ".join(
            f"{p.axis}"
            + (f" {p.gain_pp:+.1f}pp b={p.exponent:+.2f}" if p.gain_pp is not None
               else f" ({p.levels} level{'s' if p.levels != 1 else ''})")
            for p in dp.prices)
        left = "" if dp.residual_after is None else f"{dp.residual_after:6.1f}"
        lines.append(f"{dp.dataset[:44]:44s} {dp.film[:6]:6s} {dp.n:3d} "
                     f"{dp.shape:7.1f} {dp.owner[:18]:18s} "
                     f"{dp.best_gain:6.1f} {left:>6s}  {detail}")

    total_points = sum(d.n for d in prices)
    lines += ["", f"{len(prices)} improvable datasets, {total_points} measured points",
              "", "POINTS BY OWNING AXIS (the pre-registered reading):"]
    owners: Dict[str, List[DatasetPrice]] = {}
    for dp in prices:
        owners.setdefault(dp.owner, []).append(dp)
    for owner, group in sorted(owners.items(), key=lambda kv: -sum(d.n for d in kv[1])):
        pts = sum(d.n for d in group)
        gains = [d.best_gain for d in group]
        lines.append(f"  {owner:20s} {pts:4d} points ({100.0*pts/total_points:4.1f} %), "
                     f"{len(group):2d} datasets, median oracle gain "
                     f"{statistics.median(gains):5.1f} pp")

    # What a REAL law can buy on each named axis: one shared exponent.
    lines += ["", "SHARED-EXPONENT BOUND (what a law, not an oracle, can buy):"]
    for axis in sorted({dp.owner for dp in prices} - {"distributed"}):
        bound = shared_exponent_bound(prices, axis)
        if bound is None:
            lines.append(f"  {axis:20s} fewer than 2 datasets sweep it: no law testable")
            continue
        lines.append(
            f"  {axis:20s} {bound['datasets']:2d} datasets  best shared db="
            f"{bound['db']:+.2f}  mean shape {bound['mean_shape_before']:.1f}% -> "
            f"{bound['mean_shape_after']:.1f}%  shared {bound['shared_gain_pp']:+.1f} pp "
            f"vs oracle {bound['oracle_gain_pp']:+.1f} pp  "
            f"per-dataset exponents {bound['exponents']}")

    named = {k: v for k, v in owners.items() if k != "distributed"}
    if named:
        top, group = max(named.items(), key=lambda kv: sum(d.n for d in kv[1]))
        share = 100.0 * sum(d.n for d in group) / total_points
        lines += ["", f"largest single axis: {top} with {share:.1f} % of improvable points"]
        lines.append("READING 1 (an axis holds >= 30 %): target it next."
                     if share >= 30.0 else
                     "READING 2 (no axis holds >= 30 %): the error is DISTRIBUTED. "
                     "No single-axis law reaches <= 10 %; write the floor argument "
                     "in docs/limits.md.")
    return "\n".join(lines)


if __name__ == "__main__":
    print(report())
