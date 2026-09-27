"""Is the abrasive-concentration response CURVED in more than one place?

Why this probe exists
---------------------
`tools/median_crossing_probe.py` reduced the remaining distance to the
completion bar from "3.2 percentage points" to **one dataset**, and inside that
dataset to **one row**: `liang2026_4hsic_ceria_composite_h2o2_conc` at 1 wt%,
over-predicted 57.7% while its other three rows score 3.8 / 4.3 / 6.9%.

`tools/low_loading_residual_probe.py` then refuted the obvious explanation: the
sub-reference population is centred (36 of 81 rows over-predicting, median
0.97x), so no shared term is missing at low loading.

What remains is narrower and checkable.  The model's concentration response is
a single power law, `rate ~ C^n`, so its local log-log slope is the SAME at
every loading.  Liang's measured slope is not: **+0.532** between 1 and 5 wt%
and **+0.244** between 5 and 9 wt%, while the model reports +0.226 / +0.234.
The model is right where the pack is anchored and wrong far below it, which is
the signature of CURVATURE, not of a wrong exponent.

Curvature is fittable only if it appears in several independent ladders.  One
curved ladder plus one new constant is interpolation of a single dataset, which
this repository forbids (constants >= data levels).  So the question this probe
answers is not "is Liang curved" -- that is already measured -- but "**how many
independent iso-condition ladders in the corpus are curved, and do they curve
the same way?**"

Method
------
A ladder is a set of rows from one dataset that differ ONLY in
`abrasive_wt_pct` (every other override, pressure and both speeds identical),
with at least three distinct loadings -- the minimum at which a slope can
change at all.  For each ladder the local log-log slopes between consecutive
loadings are computed from the MEASURED rates, and curvature is reported as the
difference between the first and last local slope.  Negative means the response
flattens as loading rises (the saturating direction); positive means it steepens.

Nothing is fitted and no pack is modified.
    python tools/concentration_curvature_probe.py
"""

from __future__ import annotations

import math
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import yaml

from cmp_sim.core import predictive_score as ps

DATASETS = (Path(__file__).resolve().parents[1] / "cmp_sim" / "data"
            / "validation" / "datasets")

AXIS = "abrasive_wt_pct"
# Row fields that must match for two rows to be the same operating condition.
FIXED_FIELDS = ("pressure_psi", "rpm_platen", "rpm_wafer")


def _signature(row: Dict[str, Any]) -> Tuple:
    overrides = {k: v for k, v in (row.get("overrides") or {}).items()
                 if k != AXIS}
    fixed = tuple(row.get(f) for f in FIXED_FIELDS)
    return fixed + tuple(sorted(overrides.items(), key=lambda kv: kv[0]))


def ladders() -> List[Dict[str, Any]]:
    """Every iso-condition concentration ladder with >= 3 distinct loadings."""
    found: List[Dict[str, Any]] = []
    for path in sorted(DATASETS.glob("*.yaml")):
        doc = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        groups: Dict[Tuple, List[Tuple[float, float]]] = {}
        for row in doc.get("conditions") or []:
            loading = (row.get("overrides") or {}).get(AXIS)
            rate = ps._measured(row)
            if loading is None or rate is None:
                continue
            groups.setdefault(_signature(row), []).append(
                (float(loading), float(rate)))
        for sig, points in groups.items():
            uniq: Dict[float, float] = {}
            for c, r in sorted(points):
                uniq.setdefault(c, r)
            if len(uniq) < 3:
                continue
            cs = sorted(uniq)
            slopes = [
                math.log(uniq[b] / uniq[a]) / math.log(b / a)
                for a, b in zip(cs, cs[1:])
            ]
            # The model's OWN local slopes on the same ladder. Measured
            # curvature is only a target for new physics to the extent the
            # model does NOT already produce it: the concentration response is
            # a power law in `mechanical_factor`, but the GW contact and
            # chemical layers can bend the composite response, so the residual
            # curvature -- not the raw one -- is what a new term would have to
            # explain.
            rows_by_c = {}
            for row in doc.get("conditions") or []:
                load = (row.get("overrides") or {}).get(AXIS)
                if load is None or _signature(row) != sig:
                    continue
                rows_by_c.setdefault(float(load), row)
            model_slopes: Optional[List[float]] = []
            for a, b in zip(cs, cs[1:]):
                ra, rb = rows_by_c.get(a), rows_by_c.get(b)
                pa = ps._predict(doc, ra) if ra is not None else None
                pb = ps._predict(doc, rb) if rb is not None else None
                if not pa or not pb:
                    model_slopes = None
                    break
                model_slopes.append(math.log(pb / pa) / math.log(b / a))
            model_curv = (None if model_slopes is None
                          else model_slopes[-1] - model_slopes[0])
            found.append({
                "dataset": path.stem,
                "pack": doc.get("pack"),
                "loadings": cs,
                "slopes": slopes,
                "curvature": slopes[-1] - slopes[0],
                "model_slopes": model_slopes,
                "model_curvature": model_curv,
                "residual_curvature": (None if model_curv is None
                                       else slopes[-1] - slopes[0] - model_curv),
                "span": cs[-1] / cs[0],
            })
    return found


def summarise(found: List[Dict[str, Any]]) -> Dict[str, Any]:
    curvs = [f["curvature"] for f in found]
    flattening = [f for f in found if f["curvature"] < 0]
    steepening = [f for f in found if f["curvature"] > 0]
    datasets = {f["dataset"] for f in found}
    scored = [f for f in found if f["residual_curvature"] is not None]
    resid = sorted(f["residual_curvature"] for f in scored)
    return {
        "ladders": len(found),
        "datasets": len(datasets),
        "flattening": len(flattening),
        "steepening": len(steepening),
        "median_curvature": (sorted(curvs)[len(curvs) // 2] if curvs else None),
        # A shared saturation term is identifiable only if SEVERAL independent
        # ladders curve the SAME way. Agreement is counted on the majority side.
        "agreeing": max(len(flattening), len(steepening)),
        "flattening_datasets": len({f["dataset"] for f in flattening}),
        "scored_against_model": len(scored),
        "residual_flattening": sum(1 for f in scored
                                   if f["residual_curvature"] < 0),
        "median_residual_curvature": (resid[len(resid) // 2] if resid else None),
    }


def main() -> int:
    found = ladders()
    s = summarise(found)
    print(f"iso-condition concentration ladders : {s['ladders']} "
          f"across {s['datasets']} datasets")
    print(f"  flattening (saturating direction) : {s['flattening']}")
    print(f"  steepening                        : {s['steepening']}")
    if s["median_curvature"] is not None:
        print(f"  median curvature (last - first)   : {s['median_curvature']:+.3f}")
    print()
    print(f"scored against the model's own curvature : {s['scored_against_model']}")
    print(f"  still flattening AFTER the model       : {s['residual_flattening']}")
    if s["median_residual_curvature"] is not None:
        print(f"  median RESIDUAL curvature              : "
              f"{s['median_residual_curvature']:+.3f}")
    print()
    for f in sorted(found, key=lambda f: f["curvature"]):
        slopes = " ".join(f"{v:+.3f}" for v in f["slopes"])
        loads = "/".join(f"{c:g}" for c in f["loadings"])
        mc = ("   model=n/a" if f["model_curvature"] is None
              else f"   model={f['model_curvature']:+.3f}"
                   f" resid={f['residual_curvature']:+.3f}")
        print(f"  curv={f['curvature']:+.3f}{mc}  slopes[{slopes}]  "
              f"C={loads} wt%  {f['dataset'][:44]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
