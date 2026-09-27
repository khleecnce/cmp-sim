"""PRICE the zero-constant lognormal PSD-width factor BEFORE wiring it (§28's rule).

limits.md §40 leaves the width axis with a KNOWN SIGN (negative, from two
independent applicants) and NO magnitude.  The obvious next move is the one
form that needs no fitted constant at all:

DERIVATION (no free parameter anywhere in it)
---------------------------------------------
Assume the size distribution is lognormal -- the standard model for a
comminuted or grown colloid, and the distribution both source PSDs are
reported against.  Then for a lognormal with median `d50` and shape `sigma`,
the p-th quantile is `d_p = d50 * exp(z_p * sigma)`, so the PUBLISHED pair
(D50, D99) determines sigma outright:

    sigma = ln(D99 / D50) / z_99,      z_99 = 2.32635

Nothing is fitted: z_99 is the standard normal quantile and both diameters are
printed in the source tables.

The abrasive is dosed by MASS (wt%), not by number.  The number of particles
per unit volume at fixed mass loading is therefore

    N  =  phi / <v>  ~  phi / <d^3>

and for a lognormal `<d^3> = d50^3 * exp(4.5 sigma^2)`.  Hence at FIXED D50 and
FIXED wt%, broadening the distribution multiplies the available particle count
by

    f(sigma) = exp(-4.5 * sigma^2)                                        (W)

This is a pure consequence of dosing by mass: the same grams of abrasive spread
over a broader distribution buys fewer particles, because the third moment runs
away faster than the median.  The sign is NEGATIVE with no freedom to be
otherwise, which is the sign Basim 2000 measures.

WHAT THIS PROBE DOES
--------------------
It PRICES (W) against the corpus without touching a pack, per §28: a term must
be priced before it is wired, because the expensive mistake is wiring a term
whose sign is right and whose magnitude is wrong.  It reports, per block:

  * the derived sigma and factor for every row (no fit);
  * the shape MAPE now, and the shape MAPE if (W) multiplied the prediction;
  * the residual slope against ln f, which is +1.00 if (W) is exactly the
    missing physics, 0.00 if the residual does not know about it, and anything
    else if the form is right but the exponent 4.5 is not.

A verdict is printed, but the DECISION is deliberately left to the reader: a
median improvement is not sufficient grounds to wire (§26 -- a counting
statistic moves for reasons unrelated to physics).

Run:  .venv/bin/python tools/lognormal_width_price_probe.py
"""

from __future__ import annotations

import math
import sys
from pathlib import Path
from typing import Dict, List, Optional

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import yaml

from cmp_sim.core.predictive_score import (  # noqa: E402
    _measured, _predict_with_gate, dataset_paths,
)

#: Standard normal 99th-percentile quantile. Not a fitted constant: it is the
#: definition of "D99" under the lognormal assumption.
Z99 = 2.32635

#: Third-moment coefficient for a lognormal: <d^3> = d50^3 exp(4.5 sigma^2).
#: Also not fitted -- it is 3^2/2 from the lognormal moment formula
#: <d^k> = d50^k exp(k^2 sigma^2 / 2) with k = 3.
MOMENT3 = 4.5


def sigma_from(d50: Optional[float], d99: Optional[float]) -> Optional[float]:
    """Lognormal shape parameter implied by a published (D50, D99) pair."""
    if not d50 or not d99 or d99 <= d50:
        return None
    return math.log(float(d99) / float(d50)) / Z99


def width_factor(sigma: float) -> float:
    """f(sigma) = exp(-4.5 sigma^2) -- equation (W). Zero free constants."""
    return math.exp(-MOMENT3 * sigma * sigma)


def _mape(pairs) -> float:
    return 100.0 * sum(abs(p - m) / m for m, p in pairs) / len(pairs)


def _best_scale(measured: List[float], predicted: List[float]) -> float:
    """The scorer's single free multiplicative scale, fitted its way."""
    return (sum(m * p for m, p in zip(measured, predicted))
            / sum(p * p for p in predicted))


def price_block(doc: Dict, rows: List[Dict]) -> Optional[Dict]:
    meas: List[float] = []
    base: List[float] = []
    fac: List[float] = []
    sigmas: List[float] = []
    for row in rows:
        ov = row.get("overrides") or {}
        d50 = ov.get("abrasive_d50_nm") or ov.get("abrasive_size_nm")
        s = sigma_from(d50, ov.get("abrasive_d99_nm"))
        pred, _gate, _dec = _predict_with_gate(doc, row)
        m = _measured(row)
        if s is None or pred is None or pred <= 0 or m is None or m <= 0:
            return None
        meas.append(m)
        base.append(pred)
        sigmas.append(s)
        fac.append(width_factor(s))
    n = len(meas)
    if n < 3:
        return None

    s0 = _best_scale(meas, base)
    before = _mape([(m, s0 * p) for m, p in zip(meas, base)])

    withw = [p * f for p, f in zip(base, fac)]
    s1 = _best_scale(meas, withw)
    after = _mape([(m, s1 * p) for m, p in zip(meas, withw)])

    # Residual slope against ln f. 1.0 means (W) is exactly what was missing.
    xs = [math.log(f) for f in fac]
    ys = [math.log(m / p) for m, p in zip(meas, base)]
    mx = sum(xs) / n
    my = sum(ys) / n
    sxx = sum((x - mx) ** 2 for x in xs)
    slope = (sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sxx
             if sxx > 0 else None)
    stderr = None
    if slope is not None and n > 2:
        inter = my - slope * mx
        resid = [y - (inter + slope * x) for x, y in zip(xs, ys)]
        s2 = sum(r * r for r in resid) / (n - 2)
        stderr = math.sqrt(s2 / sxx) if s2 > 0 else 0.0

    return {"n": n, "before": before, "after": after,
            "slope": slope, "stderr": stderr,
            "sigma_min": min(sigmas), "sigma_max": max(sigmas),
            "factor_span": max(fac) / min(fac)}


def report() -> Dict:
    out = {}
    for path in dataset_paths():
        doc = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        rows = [r for r in (doc.get("conditions") or [])
                if _measured(r) is not None
                and (r.get("overrides") or {}).get("abrasive_d99_nm")]
        if len(rows) < 3:
            continue
        priced = price_block(doc, rows)
        if priced:
            out[path.stem] = priced
    return out


def main() -> None:
    rep = report()
    print("LOGNORMAL PSD-WIDTH FACTOR -- PRICE BEFORE WIRING")
    print("=" * 72)
    print("f(sigma) = exp(-4.5 sigma^2),  sigma = ln(D99/D50)/2.32635")
    print("ZERO free constants: both diameters are published, z99 and the")
    print("third-moment coefficient are definitions, not fits.")
    print()
    if not rep:
        print("no block carries a usable (D50, D99) pair -- nothing to price")
        return
    for stem, r in sorted(rep.items()):
        print(f"  {stem}")
        print(f"    n={r['n']}  sigma {r['sigma_min']:.3f}..{r['sigma_max']:.3f}"
              f"  factor span {r['factor_span']:.3f}x")
        print(f"    shape  {r['before']:6.1f}%  ->  {r['after']:6.1f}%"
              f"   ({r['after'] - r['before']:+.1f} pp)")
        if r["slope"] is not None:
            se = f" +/- {r['stderr']:.2f}" if r["stderr"] is not None else ""
            print(f"    residual slope vs ln f : {r['slope']:+.2f}{se}"
                  "   (+1.00 would mean (W) is exactly the missing term)")
    print()
    print("HOW TO READ THIS")
    print("  The factor span is the whole size of the effect available. If it")
    print("  is small the term cannot repair a block however right it is, and")
    print("  a median that moves anyway moved for another reason (§26).")
    print("  A slope near 0 means the residual does not know about width;")
    print("  a slope near +1 means it does and (W) has the right magnitude.")


if __name__ == "__main__":
    main()
