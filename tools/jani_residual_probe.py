"""Decompose the jani2025 held-out miss (51.2%) by composition axis.

Why this probe exists
---------------------
`docs/limits.md` §17 left ONE unambiguous target in the whole corpus: the
jani2025 held-out RSM block. Its authors PUBLISHED their own reproducibility
(RSD 1.5-9.5%, "mostly below 7%"), so - uniquely here - "the data are noisy"
has been excluded by the source itself, and our 51.2% is ~5.4x that bound.
Every other large miss in the corpus is confounded with an unstated scatter.

This script MEASURES, it does not fit. It answers three questions and prints
the numbers whichever way they come out:

  Q1  Sign of the residual vs each swept axis. If the model were merely
      mis-scaled, log-residual would be FLAT in every axis and offset in the
      mean. A slope means a term is missing or has the wrong exponent.
  Q2  Is the block's error dominated by the pair the dataset itself declares
      structurally unpredictable (E9/E23: identical model input, different
      measured rate, differing only in an unmodelled oxalic-acid level)?
      The dataset's `excluded_axes` block says this pair caps the achievable
      score; that claim has never been priced.
  Q3  Does `promoter_M` (oxalic acid here) actually move the prediction at
      all? The 13th run recorded it as inert. If the term is gated off, the
      residual slope in Q1 for promoter_M is a direct measurement of what the
      missing term would have to do.

Nothing here writes to a pack.
"""
from __future__ import annotations

import math
from pathlib import Path
from typing import Any, Dict, List

import yaml

from cmp_sim.core.predictive_score import _predict, _recipe_for, _measured

DATASET = (Path(__file__).resolve().parents[1] / "cmp_sim" / "data"
           / "validation" / "datasets"
           / "jani2025_cu_rsm_composition_heldout.yaml")

AXES = ("abrasive_wt_pct", "oxidizer_wt_pct", "chelator_M", "promoter_M")


def _rows(doc: Dict[str, Any]) -> List[Dict[str, Any]]:
    return list(doc.get("conditions") or [])


def _ols(xs: List[float], ys: List[float]):
    """Least-squares slope, intercept and its standard error (n-2 dof)."""
    n = len(xs)
    if n < 3:
        return None, None, None
    mx = sum(xs) / n
    my = sum(ys) / n
    sxx = sum((x - mx) ** 2 for x in xs)
    if sxx <= 0:
        return None, None, None
    sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    b = sxy / sxx
    a = my - b * mx
    resid = [y - (a + b * x) for x, y in zip(xs, ys)]
    s2 = sum(r * r for r in resid) / (n - 2)
    se = math.sqrt(s2 / sxx) if s2 > 0 else 0.0
    return b, a, se


def main() -> None:
    doc = yaml.safe_load(DATASET.read_text(encoding="utf-8"))
    rows = _rows(doc)

    recs = []
    for row in rows:
        m = _measured(row)
        p = _predict(doc, row)
        if m is None or p is None or m <= 0 or p <= 0:
            continue
        ov = dict(row.get("overrides") or {})
        recs.append({
            "label": row.get("label"),
            "measured": m,
            "predicted": p,
            "logres": math.log(m / p),
            "err": 100.0 * abs(p - m) / m,
            **{k: ov.get(k) for k in AXES},
        })

    print(f"scored {len(recs)}/{len(rows)} rows")
    errs = sorted(r["err"] for r in recs)
    print(f"median |err| = {errs[len(errs) // 2]:.1f}%   "
          f"mean = {sum(errs) / len(errs):.1f}%   max = {errs[-1]:.1f}%")

    # Scale-free view: a pure calibration offset is a constant log-residual.
    mean_lr = sum(r["logres"] for r in recs) / len(recs)
    print(f"mean log-residual = {mean_lr:+.3f}  (=> uniform scale factor "
          f"{math.exp(mean_lr):.2f}x)")
    after = sorted(100.0 * abs(math.exp(r["logres"] - mean_lr) - 1.0)
                   for r in recs)
    print(f"median |err| after removing that ONE offset = "
          f"{after[len(after) // 2]:.1f}%   "
          f"(this is the part no rescaling can reach)")

    print("\nQ1  residual slope per axis (log measured/predicted vs log x)")
    print(f"{'axis':18s} {'levels':>6s} {'slope':>8s} {'SE':>7s} {'|t|':>5s}")
    for ax in AXES:
        xs, ys = [], []
        for r in recs:
            v = r.get(ax)
            if v is None or float(v) <= 0:
                continue
            xs.append(math.log(float(v)))
            ys.append(r["logres"])
        levels = len({round(x, 9) for x in xs})
        b, _, se = _ols(xs, ys)
        if b is None:
            print(f"{ax:18s} {levels:6d} {'--':>8s} {'--':>7s} {'--':>5s}")
            continue
        t = abs(b / se) if se else float("inf")
        print(f"{ax:18s} {levels:6d} {b:+8.3f} {se:7.3f} {t:5.1f}")

    print("\nQ2  the structurally-unpredictable pair declared by the dataset")
    pair = [r for r in recs if r["label"] and r["label"].startswith(("E9 ", "E23 "))]
    for r in pair:
        print(f"  {r['label']:52s} meas {r['measured']:7.1f}  "
              f"pred {r['predicted']:7.1f}  err {r['err']:5.1f}%")
    if len(pair) == 2:
        ratio = pair[0]["measured"] / pair[1]["measured"]
        print(f"  measured ratio E9/E23 = {ratio:.3f} at IDENTICAL model input "
              f"=> any single-valued model is wrong by >= "
              f"{100.0 * abs(ratio - 1) / (1 + ratio) * 2 / 2:.1f}% on one of them")
        rest = sorted(r["err"] for r in recs if r not in pair)
        print(f"  median |err| EXCLUDING the pair = {rest[len(rest) // 2]:.1f}% "
              f"(n={len(rest)}) -- if this is not much lower, the pair is NOT "
              f"the story and the dataset's own excuse does not hold")

    print("\nQ3  which of the four swept axes actually move the prediction?")
    base_row = next(r for r in rows if r.get("label") == recs[0]["label"])
    base_pred = _predict(doc, base_row)
    ov = dict(base_row.get("overrides") or {})
    for ax in AXES:
        if ov.get(ax) in (None, 0):
            print(f"  {ax:18s} base value {ov.get(ax)} -- cannot perturb")
            continue
        r2 = dict(base_row)
        o2 = dict(ov)
        o2[ax] = float(ov[ax]) * 2.0
        r2["overrides"] = o2
        p2 = _predict(doc, r2)
        moved = 100.0 * (p2 / base_pred - 1.0)
        print(f"  {ax:18s} x2 -> {p2:9.2f}  ({moved:+7.2f}%)"
              + ("   INERT" if abs(moved) < 1e-6 else ""))

    print("\nQ4  what would the ALREADY-SOURCED legacy promoter term do here?")
    print("    (legacy/sim/chemistry.py::_carboxylate_promoter_term, fitted on")
    print("     US6309560B1 TABLE 1 -- a DIFFERENT paper from this dataset, so")
    print("     applying it here is a genuine held-out test, zero new constants)")
    phi, m, anchor = 0.078058, 0.7238, 0.040290

    def g(c: float) -> float:
        return phi + (1.0 - phi) * (c / anchor) ** m

    # Reference is the pack's own composition, promoter_ref_M = 0 -> g = phi.
    def term(c: float) -> float:
        return g(c) / g(0.0)

    mult = [term(float(r["promoter_M"])) for r in recs]
    meas = [r["measured"] for r in recs]
    pred0 = [r["predicted"] for r in recs]
    pred1 = [p * t for p, t in zip(pred0, mult)]

    def shape_mape(ms, ps):
        s = sum(a * b for a, b in zip(ms, ps)) / sum(b * b for b in ps)
        e = sorted(100.0 * abs(s * b - a) / a for a, b in zip(ms, ps))
        return e[len(e) // 2], sum(e) / len(e)

    m0, a0 = shape_mape(meas, pred0)
    m1, a1 = shape_mape(meas, pred1)
    print(f"  shape median  before {m0:5.1f}%   after {m1:5.1f}%   "
          f"(mean {a0:5.1f}% -> {a1:5.1f}%)")
    slope = sum(mult) and None
    del slope
    # The local log-slope of the sourced term, to compare against Q1's
    # MEASURED residual slope. Agreement between a term fitted on another
    # patent and a residual measured here is the evidence; disagreement kills
    # the idea and must be printed either way.
    import statistics
    cs = [float(r["promoter_M"]) for r in recs]
    cmid = statistics.median(cs)
    h = 1e-4
    dlog = ((math.log(term(cmid + h)) - math.log(term(cmid - h)))
            / (math.log(cmid + h) - math.log(cmid - h)))
    print(f"  sourced term's local d(ln f)/d(ln C) at C={cmid:.3f} M: {dlog:+.3f}")
    print("  MEASURED residual slope on promoter_M (Q1) is printed above; if "
          "those two disagree in SIGN or by >2x, do not wire the term.")


if __name__ == "__main__":
    main()
