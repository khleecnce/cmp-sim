"""Can the axis ORACLE see a law that BENDS? (§45's general check, continued)

Why this script exists
----------------------
§45 showed that a *span ratio* answers "how much" and can never answer "which
way", because ``max/min`` throws away the pairing of prediction with
measurement. The generalisable rule it left was: ask of every reduction what it
DISCARDS. The next reduction in line is the one behind the largest closure
argument in this repository.

``tools/axis_error_census.py`` prices an axis with an oracle::

    predicted' = predicted * (x / x_ref) ** b        b fitted per dataset

and calls the resulting drop "the MOST any closed-form law on that axis could
buy". On that sentence rest:

* §14  "the improvable error is DISTRIBUTED: no single-axis law reaches 10 %"
* §16  "<= 10 % is outside the reach of any shared-constant model"
* the ``OWNERSHIP_MIN_GAIN`` = 2 pp bar that decides which axis owns a dataset,
  hence the pre-registered READING 1 / READING 2 verdict.

But ``(x/x_ref)**b`` is a straight line in log-log. It spans exactly the
MONOTONE POWER LAWS. The model being priced does not only contain those: its
pH term is a Gaussian in pH, its oxidiser term is a Langmuir saturation, its
zeta terms are referenced to an isoelectric point. Those BEND. A reduction that
fits one slope cannot report a bend, so "the most any law could buy" is in fact
"the most any *power law* could buy" -- and an axis whose real law is peaked or
saturating can be priced at ~0 pp and filed as closed.

The blindness is arithmetic, not statistical (proved in the test)
----------------------------------------------------------------
Let ``u = log(x/x_ref)`` and let the true log-residual be purely quadratic,
``ly = c*u**2``. The oracle's slope is the OLS estimate

    b = sum (u - ubar)(ly - lybar) / sum (u - ubar)**2 .

For levels laid out SYMMETRICALLY in ``u`` (a geometric ladder -- 1/2/4/8 wt%,
or any sweep the experimenter chose to space evenly in log), the odd moments
vanish, ``sum u**3 = 0`` with ``ubar = 0``, so ``b = 0`` EXACTLY: the oracle
reports zero gain while a one-constant curved law explains the residual
completely. No corpus change can recover it, exactly as in §45; the quantity
simply is not a function of the curvature.

What this script measures
-------------------------
The same datasets and axes ``axis_error_census`` prices, priced a second time
with ONE extra shape parameter -- a quadratic in ``log x`` -- and compared:

    linear  : ly ~ b1*u              (the shipping oracle)
    curved  : ly ~ b1*u + b2*u**2    (this probe)

Two guards keep the comparison honest, because a second free parameter buys
error reduction on noise alone:

1. ``MIN_LEVELS_CURVE = 4``. With 3 levels a 2-parameter shape plus the free
   scale passes through every point; the "gain" would be interpolation, which
   is the same rule ``MIN_LEVELS = 3`` already applies to the linear oracle.
2. A **null control by permutation**: the axis values are shuffled against the
   residuals and both oracles refitted, ``NULL_TRIALS`` times. The median
   curved-minus-linear gain under shuffling is the gain an extra degree of
   freedom buys from nothing, and it is reported next to every real gain. A
   real gain that does not clear its own null is not evidence.

And because a LAW carries one constant into every dataset, the shared-constant
version is measured too: a single curvature ``b2`` scanned across every dataset
sweeping the axis, each keeping its own free scale. That is the number a real
model could buy; the per-dataset figure remains an upper bound nothing attains.

This module MEASURES ONLY. It fits nothing into any pack. The exponents live
for the duration of the process and are thrown away.

Usage: ``python tools/oracle_curvature_blindness_probe.py`` (inside ``.venv``).
"""
from __future__ import annotations

import math
import random
import statistics
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

import yaml

from cmp_sim.core.predictive_score import _measured
from cmp_sim.core.validation import dataset_paths
from tools.axis_error_census import (
    MIN_LEVELS, OWNERSHIP_MIN_GAIN, _oracle, _predict_rows, _shape_mape,
)
from tools.residual_census import INERT_TOLERANCE, _axis_value, census

#: A quadratic shape needs more levels than a linear one for the same reason
#: ``MIN_LEVELS`` exists: with as many free parameters as levels the fit is
#: interpolation and its "gain" is meaningless.
MIN_LEVELS_CURVE = 4

#: Permutation trials for the degree-of-freedom null control.
NULL_TRIALS = 200

#: Fixed seed: the null control is a published number and must be reproducible.
NULL_SEED = 20260928


@dataclass
class CurvePrice:
    dataset: str
    film: str
    axis: str
    n: int
    levels: int
    shape: float                        # scored shape MAPE, no oracle
    linear_gain_pp: float               # what the shipping oracle reports
    curved_gain_pp: float               # with one extra (quadratic) parameter
    b1: float
    b2: float
    null_excess_pp: float               # median curved-minus-linear under shuffling
    log_spacing_cv: float               # how evenly the levels sit in log x

    @property
    def excess_pp(self) -> float:
        """Curvature gain above the linear oracle, net of the dof null."""
        return self.curved_gain_pp - self.linear_gain_pp - self.null_excess_pp

    @property
    def flips_ownership(self) -> bool:
        """Was this axis below the ownership bar until curvature was allowed?"""
        return (self.linear_gain_pp < OWNERSHIP_MIN_GAIN
                and self.curved_gain_pp - self.null_excess_pp >= OWNERSHIP_MIN_GAIN)


def _fit_quadratic(u: Sequence[float], ly: Sequence[float]) -> Tuple[float, float]:
    """OLS of ``ly ~ b1*u + b2*u**2`` with the intercept left to the free scale.

    The intercept is deliberately absorbed by the shape score's own free
    multiplicative scale, exactly as in the linear oracle, so the two prices
    differ by the quadratic term ALONE and nothing else.
    """
    n = len(u)
    mu1 = sum(u) / n
    mu2 = sum(v * v for v in u) / n
    my = sum(ly) / n
    # centred design: [u - mu1, u^2 - mu2]
    a11 = sum((v - mu1) ** 2 for v in u)
    a12 = sum((v - mu1) * (v * v - mu2) for v in u)
    a22 = sum((v * v - mu2) ** 2 for v in u)
    r1 = sum((v - mu1) * (w - my) for v, w in zip(u, ly))
    r2 = sum((v * v - mu2) * (w - my) for v, w in zip(u, ly))
    det = a11 * a22 - a12 * a12
    if abs(det) < 1e-18:
        if a11 <= 0:
            return 0.0, 0.0
        return r1 / a11, 0.0
    return (r2 * -a12 + r1 * a22) / det, (r1 * -a12 + r2 * a11) / det


def _oracle_curved(measured: Sequence[float], predicted: Sequence[float],
                   x: Sequence[float]) -> Tuple[float, float, float]:
    """Best (shape MAPE, b1, b2) when a quadratic in ``log x`` is granted."""
    lx = [math.log(v) for v in x]
    xr = math.exp(sum(lx) / len(lx))
    u = [v - math.log(xr) for v in lx]
    ly = [math.log(m / p) for m, p in zip(measured, predicted)]
    b1, b2 = _fit_quadratic(u, ly)
    boosted = [p * math.exp(b1 * v + b2 * v * v)
               for p, v in zip(predicted, u)]
    return _shape_mape(list(measured), boosted), b1, b2


def _log_spacing_cv(x: Sequence[float]) -> float:
    """Coefficient of variation of the gaps between sorted ``log x`` levels.

    0 means a perfect geometric ladder, which is precisely the layout on which
    the linear oracle's blindness to curvature is exact.
    """
    lv = sorted(set(math.log(v) for v in x))
    if len(lv) < 3:
        return float("nan")
    gaps = [b - a for a, b in zip(lv, lv[1:])]
    m = statistics.mean(gaps)
    if m <= 0:
        return float("nan")
    return statistics.pstdev(gaps) / m


def _null_excess(measured: Sequence[float], predicted: Sequence[float],
                 x: Sequence[float]) -> float:
    """Median curved-minus-linear gain when x is shuffled against the residual.

    This is the price of the extra degree of freedom with no signal present.
    """
    rng = random.Random(NULL_SEED)
    xs = list(x)
    out: List[float] = []
    for _ in range(NULL_TRIALS):
        rng.shuffle(xs)
        lin, _b = _oracle(list(measured), list(predicted), xs)
        cur, _b1, _b2 = _oracle_curved(measured, predicted, xs)
        out.append(lin - cur)            # both are MAPEs: lower is better
    return statistics.median(out)


def price_curvature(records=None) -> List[CurvePrice]:
    records = records if records is not None else census()
    by_name = {r.dataset: r for r in records if r.bucket == "responsive_miss"}
    out: List[CurvePrice] = []
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
        base = _shape_mape(measured, predicted)
        for axis, response in rec.response.items():
            if response is None or response < INERT_TOLERANCE:
                continue
            values = [_axis_value(r, axis) for r in rows]
            if any(not isinstance(v, (int, float)) or v <= 0 for v in values):
                continue
            levels = len(set(values))
            if levels < MIN_LEVELS_CURVE:
                continue                  # guard 1: no interpolation prices
            xs = [float(v) for v in values if isinstance(v, (int, float))]
            lin_mape, b_lin = _oracle(measured, predicted, xs)
            cur_mape, b1, b2 = _oracle_curved(measured, predicted, xs)
            out.append(CurvePrice(
                dataset=rec.dataset, film=rec.film, axis=axis, n=len(rows),
                levels=levels, shape=base,
                linear_gain_pp=base - lin_mape,
                curved_gain_pp=base - cur_mape,
                b1=b1, b2=b2,
                null_excess_pp=_null_excess(measured, predicted, xs),
                log_spacing_cv=_log_spacing_cv(xs)))
    return out


def shared_curvature_bound(prices: List[CurvePrice],
                           axis: str) -> Optional[Dict[str, Any]]:
    """Price a real LAW: one curvature ``b2`` shared by every dataset.

    Each dataset keeps its own free scale and its own linear slope (the model
    already carries per-pack exponents on most of these axes), so the scanned
    quantity is the shared BEND alone. If the per-dataset curvatures disagree
    in sign, the best shared value sits near zero and the axis is closed to any
    curved law too -- which is the outcome that would make this probe's finding
    a measurement rather than an opening.
    """
    members = [p for p in prices if p.axis == axis]
    if len(members) < 2:
        return None
    cached: List[Tuple[List[float], List[float], List[float]]] = []
    wanted = {p.dataset for p in members}
    for path in dataset_paths():
        if Path(path).stem not in wanted:
            continue
        doc = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
        rows = [r for r in (doc.get("conditions") or [])
                if _measured(r) is not None]
        predicted = _predict_rows(doc, rows)
        if predicted is None:
            continue
        measured = [float(_measured(r)) for r in rows]
        raw = [_axis_value(r, axis) for r in rows]
        if any(not isinstance(v, (int, float)) or v <= 0 for v in raw):
            continue
        xs = [float(v) for v in raw if isinstance(v, (int, float))]
        cached.append((measured, predicted, xs))
    if len(cached) < 2:
        return None

    def total(b2: float) -> float:
        acc = 0.0
        for measured, predicted, x in cached:
            lx = [math.log(v) for v in x]
            u = [v - sum(lx) / len(lx) for v in lx]
            # the shared bend is imposed first, then each dataset's own slope
            # is refitted on the remainder: a law fixes the curvature, not the
            # per-pack exponent, which the packs already carry.
            resid = [math.log(m / p) - b2 * v * v
                     for m, p, v in zip(measured, predicted, u)]
            mu = sum(u) / len(u)
            my = sum(resid) / len(resid)
            sxx = sum((v - mu) ** 2 for v in u)
            b1 = (sum((v - mu) * (w - my) for v, w in zip(u, resid)) / sxx
                  if sxx > 0 else 0.0)
            boosted = [p * math.exp(b1 * v + b2 * v * v)
                       for p, v in zip(predicted, u)]
            acc += _shape_mape(measured, boosted)
        return acc

    grid = [(-1.0 + 0.01 * i) for i in range(201)]
    best_b2 = min(grid, key=total)
    before = total(0.0) / len(cached)
    after = total(best_b2) / len(cached)
    return {"axis": axis, "datasets": len(cached), "b2": best_b2,
            "mean_shape_before": before, "mean_shape_after": after,
            "shared_gain_pp": before - after,
            "oracle_excess_pp": statistics.mean(p.excess_pp for p in members),
            "curvatures": sorted(round(p.b2, 2) for p in members)}


def report(prices: Optional[List[CurvePrice]] = None) -> str:
    prices = prices if prices is not None else price_curvature()
    lines = [
        f"{'dataset':42s} {'axis':20s} {'lv':>2s} {'shape%':>7s} "
        f"{'linear':>7s} {'curved':>7s} {'null':>6s} {'excess':>7s} "
        f"{'b1':>6s} {'b2':>6s} {'cv':>5s}",
        "-" * 132,
    ]
    for p in sorted(prices, key=lambda q: -q.excess_pp):
        lines.append(
            f"{p.dataset[:42]:42s} {p.axis[:20]:20s} {p.levels:2d} "
            f"{p.shape:7.1f} {p.linear_gain_pp:+7.2f} {p.curved_gain_pp:+7.2f} "
            f"{p.null_excess_pp:+6.2f} {p.excess_pp:+7.2f} "
            f"{p.b1:+6.2f} {p.b2:+6.2f} {p.log_spacing_cv:5.2f}")

    flips = [p for p in prices if p.flips_ownership]
    lines += ["", f"{len(prices)} (dataset, axis) pairs with >= {MIN_LEVELS_CURVE} "
                  f"levels priced both ways "
                  f"(the shipping oracle needs only {MIN_LEVELS})",
              f"curvature buys more than its own dof null on "
              f"{sum(1 for p in prices if p.excess_pp > 0)}",
              f"axes that cross the {OWNERSHIP_MIN_GAIN:.0f} pp ownership bar ONLY "
              f"with curvature: {len(flips)}"]
    for p in flips:
        lines.append(f"    {p.dataset} / {p.axis}: "
                     f"{p.linear_gain_pp:+.2f} pp -> "
                     f"{p.curved_gain_pp - p.null_excess_pp:+.2f} pp")

    lines += ["", "SHARED-CURVATURE BOUND (what a law, not an oracle, can buy):"]
    for axis in sorted({p.axis for p in prices}):
        bound = shared_curvature_bound(prices, axis)
        if bound is None:
            lines.append(f"  {axis:22s} fewer than 2 datasets: no law testable")
            continue
        lines.append(
            f"  {axis:22s} {bound['datasets']:2d} datasets  best shared b2="
            f"{bound['b2']:+.2f}  mean shape {bound['mean_shape_before']:.1f}% -> "
            f"{bound['mean_shape_after']:.1f}%  shared {bound['shared_gain_pp']:+.1f} pp"
            f"  per-dataset b2 {bound['curvatures']}")
    return "\n".join(lines)


if __name__ == "__main__":
    print(report())
