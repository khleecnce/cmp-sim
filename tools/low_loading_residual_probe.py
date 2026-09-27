"""Is the model's error at LOW abrasive loading a systematic, signed residual?

Why this probe exists
---------------------
`tools/median_crossing_probe.py` showed that the distance from the corpus
median (18.2%) to the completion bar (15.0%) is not a diffuse 3.2 points: it is
**one dataset**, `liang2026_4hsic_ceria_composite_h2o2_conc`, and inside that
dataset it is **one row**.  Three of its four rows score 3.8 / 4.3 / 6.9%; the
fourth -- the lowest abrasive loading in the file, 1 wt% against a pack whose
reference composition is 5 wt% -- is over-predicted by 57.7%.

A single bad row is either (a) that dataset's own problem, or (b) the visible
tip of a term the model is missing everywhere and which only becomes large far
below each pack's reference loading.  Those two readings call for opposite
actions, and nothing in the score report distinguishes them, so measure it.

What is measured
----------------
For every dataset that varies `abrasive_wt_pct`, the scorer's own shape fit is
reproduced (one free multiplicative scale, least squares through the origin --
identical to `score_dataset`), and each row's signed residual

    ln(predicted_scaled / measured)

is paired with that row's loading expressed RELATIVE to its own pack's
reference concentration, `ln(C / C_ref)`.  Relative loading is the right
abscissa because the pack's Kp and every normalised factor are defined AT
C_ref: an absolute 1 wt% is a deep extrapolation for a 20 wt% pack and the
reference itself for a 1 wt% pack.

If the residual is uncorrelated with relative loading, the Liang row is that
file's own problem and no shared term is missing.  If the residual rises
systematically as C falls below C_ref -- the model over-predicting the more
dilute the slurry is -- then a term with a KNOWN SIGN is missing from every
pack, which is a derivation target rather than a fit.

This probe fits nothing and modifies no pack.
    python tools/low_loading_residual_probe.py
"""

from __future__ import annotations

import math
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import yaml

from cmp_sim.core import predictive_score as ps
from cmp_sim.core.params import load_pack

DATASETS = Path(__file__).resolve().parents[1] / "cmp_sim" / "data" / "validation" / "datasets"

# The pack key that names the composition every normalised factor is defined at.
REFERENCE_KEYS = ("abrasive_wt_pct", "reference_abrasive_wt_pct")


def _reference_loading(pack_name: str) -> Optional[float]:
    try:
        pack = load_pack(pack_name)
    except Exception:
        return None
    for key in REFERENCE_KEYS:
        param = pack.params.get(key)
        if param is not None and param.value is not None:
            return float(param.value)
    return None


def _rows_with_loading(doc: Dict[str, Any]) -> List[Tuple[Dict[str, Any], float]]:
    out = []
    for row in doc.get("conditions") or []:
        if ps._measured(row) is None:
            continue
        loading = (row.get("overrides") or {}).get("abrasive_wt_pct")
        if loading is None:
            continue
        out.append((row, float(loading)))
    return out


def collect() -> List[Dict[str, Any]]:
    """One record per scorable row on a concentration-varying dataset."""
    records: List[Dict[str, Any]] = []
    for path in sorted(DATASETS.glob("*.yaml")):
        doc = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        pairs = _rows_with_loading(doc)
        if len(pairs) < 3:
            continue
        if len({c for _, c in pairs}) < 2:
            continue  # loading declared but not varied: no information here
        c_ref = _reference_loading(str(doc.get("pack") or ""))
        if not c_ref:
            continue
        measured, predicted, keep = [], [], []
        for row, loading in pairs:
            value = ps._predict(doc, row)
            m = ps._measured(row)
            if value is None or not value or m is None:
                continue
            measured.append(m)
            predicted.append(value)
            keep.append(loading)
        if len(measured) < 3:
            continue
        # The scorer's own single free scale, so residuals are read off exactly
        # the fit the headline median is computed from.
        scale = (sum(m * p for m, p in zip(measured, predicted))
                 / sum(p * p for p in predicted))
        for loading, m, p in zip(keep, measured, predicted):
            records.append({
                "dataset": path.stem,
                "pack": doc.get("pack"),
                "wt_pct": loading,
                "relative": loading / c_ref,
                "ln_relative": math.log(loading / c_ref),
                "residual": math.log(scale * p / m),
                "abs_err_pct": 100.0 * abs(scale * p - m) / m,
            })
    return records


def _pearson(xs: List[float], ys: List[float]) -> float:
    n = len(xs)
    mx, my = sum(xs) / n, sum(ys) / n
    sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    sxx = sum((x - mx) ** 2 for x in xs)
    syy = sum((y - my) ** 2 for y in ys)
    if sxx <= 0 or syy <= 0:
        return 0.0
    return sxy / math.sqrt(sxx * syy)


def summarise(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    dilute = [r for r in records if r["relative"] < 1.0]
    rich = [r for r in records if r["relative"] > 1.0]
    at_ref = [r for r in records if r["relative"] == 1.0]
    xs = [r["ln_relative"] for r in records]
    ys = [r["residual"] for r in records]
    return {
        "rows": len(records),
        "datasets": len({r["dataset"] for r in records}),
        "correlation": _pearson(xs, ys) if len(records) > 2 else None,
        "dilute_rows": len(dilute),
        "dilute_over_predicting": sum(1 for r in dilute if r["residual"] > 0),
        "dilute_median_residual": (
            sorted(r["residual"] for r in dilute)[len(dilute) // 2] if dilute else None),
        "rich_rows": len(rich),
        "rich_over_predicting": sum(1 for r in rich if r["residual"] > 0),
        "rich_median_residual": (
            sorted(r["residual"] for r in rich)[len(rich) // 2] if rich else None),
        "at_reference_rows": len(at_ref),
    }


def main() -> int:
    records = collect()
    s = summarise(records)
    print(f"rows on concentration-varying datasets : {s['rows']} "
          f"across {s['datasets']} datasets")
    print(f"corr(ln(C/C_ref), ln(pred/meas))       : {s['correlation']:+.3f}"
          if s["correlation"] is not None else "correlation: n/a")
    print()
    print("BELOW each pack's reference loading:")
    print(f"  rows                : {s['dilute_rows']}")
    print(f"  over-predicting     : {s['dilute_over_predicting']}")
    if s["dilute_median_residual"] is not None:
        print(f"  median ln(pred/meas): {s['dilute_median_residual']:+.3f} "
              f"({math.exp(s['dilute_median_residual']):.2f}x)")
    print("ABOVE each pack's reference loading:")
    print(f"  rows                : {s['rich_rows']}")
    print(f"  over-predicting     : {s['rich_over_predicting']}")
    if s["rich_median_residual"] is not None:
        print(f"  median ln(pred/meas): {s['rich_median_residual']:+.3f} "
              f"({math.exp(s['rich_median_residual']):.2f}x)")
    print(f"AT the reference loading: {s['at_reference_rows']} rows")
    print()
    print("most dilute rows (relative loading ascending):")
    for r in sorted(records, key=lambda r: r["relative"])[:12]:
        print(f"  C/C_ref={r['relative']:6.3f}  ln(pred/meas)={r['residual']:+.3f}"
              f"  |err|={r['abs_err_pct']:5.1f}%  {r['dataset'][:46]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
