"""Is the alpha-chi veto's ELASTIC FALLBACK contradicted by the measurements?

This is a MEASUREMENT script, not production code. It touches no pack and
fits nothing that enters the model.

THE QUESTION (30th run, set by STATUS.md)
-----------------------------------------
`models/luo_dornfeld.resolve_regime` measures a contact branch for 33 of 49
corpus runs (plastic 11, transition 22) and then DISCARDS it: the plastic
alpha = 3/2 against the measured chi = 1.0 gives alpha*chi = 1.5 > 1, which
breaks the structural bound 0 <= 1 - alpha*chi <= 1 that the exponent
relations rest on. The code falls back to the inherited ELASTIC pair
(alpha = 2/3, chi = 1) and grades the regime `unverified`.

The fallback is not neutral. It makes a sharp, falsifiable prediction:

    n_C = p * (1 - alpha*chi) = 1 * (1 - 2/3) = +1/3

on every one of those runs. The plastic decomposition, taken literally with
full load sharing, would instead give n_C = 1 - 1.5 = -1/2 ("more abrasive
removes less"), which the bound forbids and which is why the veto exists.

So the veto is a CHOICE BETWEEN TWO EXPONENTS, and the corpus can score it:
fit the measured log-log slope of rate vs abrasive loading on every
iso-condition series that sits on a plastic or transition branch.

  * slopes clustered near +1/3  -> the elastic fallback is the RIGHT number
    and the veto is harmless; what is wrong is only the `unverified` grade
    and the warning text, which should say "outside the decomposition's
    validity" rather than "not determined from data". Zero constants.
  * slopes clustered near 0 or negative -> the plastic branch is real and the
    bound, not the data, is what needs re-deriving.
  * slopes scattered across both -> the axis is not decidable here; record it.

WHAT IS FITTED
--------------
Only the MEASUREMENTS. A power law rate ~ C^m per iso-condition group (every
other process axis held), exactly the grouping `conc_derived_probe` uses, so
the per-dataset Kp scale drops out. The model is run once per dataset only to
read which contact branch it resolved -- no model slope is compared here,
because the model's slope on these rows IS the fallback by construction and
comparing it to itself proves nothing.

CAVEAT recorded up front: a 3-5 point log-log fit over a narrow loading range
has a wide standard error, so this probe reports the per-group slope AND its
standard error, and the verdict is taken on the distribution, not on any one
group.
"""
from __future__ import annotations

import collections
import glob
import math
import os
import statistics
import sys
from typing import Dict, List, Optional, Tuple

import yaml

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE)

from conc_derived_probe import GROUP_AXES, _conc  # noqa: E402
from size_derived_probe import _mrr, fit_power  # noqa: E402

from cmp_sim.api import run_recipe  # noqa: E402
from cmp_sim.core.predictive_score import _recipe_for  # noqa: E402

DATASET_DIR = os.path.join(HERE, "cmp_sim", "data", "validation", "datasets")

# What the elastic fallback asserts on every vetoed run: n_C = p*(1-alpha*chi)
# with p = 1 (monolayer, derived from boundary lubrication in the 28th run),
# alpha = 2/3 (elastic Hertz) and chi = 1 (full load sharing).
ELASTIC_FALLBACK_N_C = 1.0 / 3.0
# What the plastic branch would assert if the bound were simply lifted.
PLASTIC_LITERAL_N_C = 1.0 - 1.5 * 1.0  # = -0.5


def slope_with_se(points: List[Tuple[float, float]]) -> Tuple[float, float, float]:
    """Log-log slope, its standard error, and r2."""
    m, r2 = fit_power(points)
    xs = [math.log(c) for c, _ in points]
    ys = [math.log(r) for _, r in points]
    n = len(points)
    mx = statistics.fmean(xs)
    sxx = sum((x - mx) ** 2 for x in xs)
    my = statistics.fmean(ys)
    resid = [y - (my + m * (x - mx)) for x, y in zip(xs, ys)]
    if n <= 2 or sxx <= 0:
        return m, float("nan"), r2
    s2 = sum(r * r for r in resid) / (n - 2)
    return m, math.sqrt(s2 / sxx), r2


def dataset_branches() -> Dict[str, Optional[str]]:
    """Contact branch the SHIPPING solver resolves for each dataset."""
    out: Dict[str, Optional[str]] = {}
    for path in sorted(glob.glob(os.path.join(DATASET_DIR, "*.yaml"))):
        name = os.path.basename(path)[:-5]
        if name.startswith("_"):
            continue
        doc = yaml.safe_load(open(path)) or {}
        conds = doc.get("conditions") or []
        if not conds:
            continue
        try:
            result = run_recipe(_recipe_for(doc, conds[0]))
        except Exception:
            out[name] = None
            continue
        out[name] = (result.get("situation") or {}).get("contact_branch")
    return out


def loading_groups() -> List[dict]:
    """Iso-condition loading series with >= 3 distinct wt%, measurements only."""
    out: List[dict] = []
    for path in sorted(glob.glob(os.path.join(DATASET_DIR, "*.yaml"))):
        name = os.path.basename(path)[:-5]
        if name.startswith("_"):
            continue
        doc = yaml.safe_load(open(path)) or {}
        groups: Dict[tuple, List[Tuple[float, float]]] = {}
        for cond in doc.get("conditions", []):
            c = _conc(cond)
            rate = _mrr(cond)
            if c is None or rate is None or c <= 0 or rate <= 0:
                continue
            merged = {**cond, **(cond.get("overrides") or {})}
            key = tuple(merged.get(k) for k in GROUP_AXES)
            groups.setdefault(key, []).append((c, rate))
        for _key, pts in groups.items():
            if len({c for c, _ in pts}) < 3:
                continue
            out.append({"dataset": name, "pack": doc.get("pack"),
                        "film": doc.get("film"), "points": sorted(pts)})
    return out


def main() -> None:
    branches = dataset_branches()
    rows = []
    for g in loading_groups():
        branch = branches.get(g["dataset"])
        m, se, r2 = slope_with_se(g["points"])
        rows.append({**g, "branch": branch, "m": m, "se": se, "r2": r2})

    print(f"{'branch':12s} {'dataset':46s} {'film':7s} {'n':>2s} "
          f"{'m_data':>7s} {'SE':>6s} {'r2':>5s}")
    for r in sorted(rows, key=lambda r: (str(r["branch"]), r["dataset"])):
        print(f"{str(r['branch'] or '-'):12s} {r['dataset'][:46]:46s} "
              f"{str(r['film'])[:7]:7s} {len(r['points']):2d} "
              f"{r['m']:+7.3f} {r['se']:6.3f} {r['r2']:5.2f}")

    vetoed = [r for r in rows if r["branch"] in ("plastic", "transition")]
    print()
    print(f"groups on a VETOED (plastic/transition) branch: {len(vetoed)}")
    if not vetoed:
        print("  nothing to decide")
        return

    ms = sorted(r["m"] for r in vetoed)
    med = ms[len(ms) // 2]
    print(f"  measured slopes: {[f'{m:+.3f}' for m in ms]}")
    print(f"  median m_data = {med:+.3f}")
    print(f"  elastic fallback asserts n_C = {ELASTIC_FALLBACK_N_C:+.3f}")
    print(f"  plastic taken literally would be n_C = {PLASTIC_LITERAL_N_C:+.3f}")

    d_elastic = abs(med - ELASTIC_FALLBACK_N_C)
    d_plastic = abs(med - PLASTIC_LITERAL_N_C)
    print(f"  |median - elastic| = {d_elastic:.3f}   "
          f"|median - plastic| = {d_plastic:.3f}")

    # How many groups are closer to each candidate, and how many are within
    # one standard error of the elastic fallback (the weaker, fairer test for
    # short ladders).
    near_elastic = sum(1 for r in vetoed
                       if abs(r["m"] - ELASTIC_FALLBACK_N_C) <= abs(
                           r["m"] - PLASTIC_LITERAL_N_C))
    within_se = sum(1 for r in vetoed
                    if not math.isnan(r["se"])
                    and abs(r["m"] - ELASTIC_FALLBACK_N_C) <= 2.0 * r["se"])
    negative = sum(1 for r in vetoed if r["m"] < 0)
    print(f"  closer to elastic: {near_elastic}/{len(vetoed)}; "
          f"within 2 SE of elastic: {within_se}/{len(vetoed)}; "
          f"negative slopes: {negative}/{len(vetoed)}")

    by_branch = collections.Counter(r["branch"] for r in vetoed)
    print(f"  by branch: {dict(by_branch)}")
    print(f"  datasets contributing: "
          f"{sorted({r['dataset'] for r in vetoed})}")

    # HONESTY: which vetoed branches does the evidence actually cover? A
    # verdict quoted for "the veto" is only as wide as the branches that
    # produced a usable iso-condition ladder. The plastic branch is entirely
    # copper here, and copper's loading sweeps sit inside RSM/L-array designs
    # where no other axis is held, so they do not survive the grouping.
    covered = set(by_branch)
    for branch in ("plastic", "transition"):
        n_runs = sum(1 for b in branches.values() if b == branch)
        state = "COVERED" if branch in covered else "NOT COVERED"
        print(f"  {branch:11s}: {n_runs:2d} corpus runs -> {state} by the "
              "iso-condition ladders above")

    print()
    if negative == 0 and near_elastic >= 0.75 * len(vetoed):
        print("VERDICT: the measurements REFUSE the literal plastic exponent "
              "(no negative slope anywhere) and sit on the elastic fallback's "
              "side. The veto substitutes the right number; what is wrong is "
              "only its GRADE and its warning text.")
        if "plastic" not in covered:
            print("  SCOPE: this is measured on the TRANSITION branch only. "
                  "No plastic-branch dataset yields an iso-condition loading "
                  "ladder (they are all copper, all inside RSM/L-array "
                  "designs), so the 11 plastic runs inherit the verdict by "
                  "continuity of the same decomposition, NOT by their own "
                  "measurement. A copper loading ladder at frozen chemistry "
                  "would test them directly.")
    elif negative >= 0.5 * len(vetoed):
        print("VERDICT: the measurements support a near-zero or negative "
              "exponent -- the structural bound, not the data, is what needs "
              "re-deriving.")
    else:
        print("VERDICT: the slopes straddle both candidates; this corpus "
              "cannot decide the veto. Record it and do not fit around it.")


if __name__ == "__main__":
    main()
