"""Price the load-sharing ONSET, before wiring it.

Why a second look at the same theta
-----------------------------------
`docs/limits.md` §28 established the target: the corpus median is decided by
one dataset, and what that dataset needs is CURVATURE in the abrasive-loading
response.  11 of 14 iso-condition ladders flatten as loading rises (residual
curvature -0.296) while the shipping power law has |curvature| < 0.01 by
construction.

Session 32 derived the monolayer occupancy

    theta = phi / (A_r / A_0)

-- particle volume fraction against the real contact area fraction the GW
layer already computes -- proved it REACHABLE (0.018 .. 97.9, median 4.9) and
then priced it and was REFUTED: median 18.17 -> 18.95%, and the binding
dataset 18.2 -> 30.5%.

That refutation is not a refutation of theta.  It is a refutation of where
theta was applied.  Session 32 applied it to the particle COUNT,

    N_active = N_sites * (1 - exp(-theta)),

which makes N sub-linear in C, and then raised that to the load-sharing
exponent the model already applies (n_eff ~ 0.23).  Sub-linear count raised to
a sub-unity exponent is FLATTER than the present power law at dilute loading,
so the correction RAISES the dilute prediction.  The measurements want the
opposite: on the binding dataset the measured log-log slope is +0.532 from
1->5 wt% and +0.244 from 5->9 wt%, i.e. the response is STEEPER than the model
at dilute and agrees with it above the pack reference.  The sign was wrong
before a single number was computed.

The derivation priced here
--------------------------
Same theta, applied instead to the quantity whose value the model has never
determined from anything: the fraction of the applied load carried by
PARTICLES rather than by bare pad asperity contact.

`core/regime.py` resolves `chi = 1.0` on all 49 datasets with a spread of
1.3e-10 -- that number is the analytic property of the exponential GW summit
distribution, not an observation (docs/limits.md §21).  chi = 1 asserts that
particles intercept the whole load at every loading, which cannot be true as
C -> 0: with no particles in the contact the pad touches the wafer directly
and removes nothing, and the load goes through the pad.

Poisson occupancy of the contact sites gives the covered fraction with no new
constant:

    chi(theta) = 1 - exp(-theta)              (theta = phi / (A_r/A_0))

Removal is then N particles each indenting under the load they actually carry,

    rate  ~  N * L_p^alpha ,     L_p = chi * L_total / N
          ~  N^(1-alpha) * (chi * L_total)^alpha

At fixed pressure and pad, relative to the pack's own reference composition,

    rate / rate_ref  =  (C/C_ref)^(1-alpha) * (chi/chi_ref)^alpha

The shipping model applies exactly (C/C_ref)^n_eff with n_eff = 1 - alpha*chi
and chi == 1, so alpha = 1 - n_eff is READ OFF the model per row (measured by
perturbation, never from the pack, so measured overrides / gates / regime
substitutions are priced as they act).  The multiplicative correction to a
shipping prediction is therefore

    [ (1 - exp(-theta)) / (1 - exp(-theta_ref)) ] ^ (1 - n_eff)

with NO new free constant.  Its limits are the two the measurements ask for:

  * theta << theta_ref  ->  chi ~ theta ~ C, and the total exponent becomes
    (1-alpha) + alpha = 1.  Each particle acts independently: the dilute slope
    goes to LINEAR, which is steeper than 0.23 -- the measured direction.
  * theta >> 1          ->  chi -> 1, correction -> 1, the exponent returns to
    the model's own 1-alpha.  The pack's anchored composition is untouched.
  * theta == theta_ref  ->  correction == 1.0 EXACTLY, the invariant every
    factor in this model must satisfy.

Scope, declared before the numbers
----------------------------------
alpha = 1 - n_eff is an indentation-load exponent, so the derivation only
speaks where alpha > 0, i.e. n_eff < 1.  A pack whose measured loading
exponent is negative (Entegris alumina, -0.406) gives alpha > 1: its response
is not a load-sharing response at all, and pricing it here would be applying a
law outside its own premise.  Both populations are reported separately and the
corpus median is reported BOTH ways, so the scope condition cannot be mistaken
for a choice of which datasets to count.

    python tools/load_sharing_onset_counterfactual.py
"""

from __future__ import annotations

import math
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from cmp_sim.core import predictive_score as ps
from cmp_sim.core.params import load_pack
from tools.derived_saturation_counterfactual import _local_exponent, _theta
from tools.monolayer_occupancy_reachability_probe import _pack_density

AXIS = "abrasive_wt_pct"


def correction(theta: float, theta_ref: float, n_eff: float) -> float:
    """Load-sharing onset correction. Exactly 1.0 at the pack reference."""
    if theta <= 0 or theta_ref <= 0:
        return 1.0
    alpha = 1.0 - n_eff
    chi = 1.0 - math.exp(-theta)
    chi_ref = 1.0 - math.exp(-theta_ref)
    if chi <= 0 or chi_ref <= 0:
        return 1.0
    return (chi / chi_ref) ** alpha


def rescore() -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    rows_out: List[Dict[str, Any]] = []
    for path in sorted(DATASETS.glob("*.yaml")):
        doc = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        try:
            pack = load_pack(str(doc.get("pack") or ""))
        except Exception:
            continue
        # The reference composition the SOLVER normalises against is
        # `abrasive_ref_wt_pct` (solver.py:546), which a row may override --
        # not the pack's own `abrasive_wt_pct`.  Reading the wrong one puts
        # theta_ref at a composition the shipping factor never used, so the
        # correction stops being 1.0 where the model is anchored.  Resolved
        # per row below, because it is a row-level override.
        ref_param = pack.params.get("abrasive_ref_wt_pct")
        if ref_param is None or ref_param.value is None:
            ref_param = pack.params.get(AXIS)
        if ref_param is None or ref_param.value is None:
            continue
        pack_c_ref = float(ref_param.value)
        density = _pack_density(pack)

        rows = [r for r in (doc.get("conditions") or [])
                if ps._measured(r) is not None
                and (r.get("overrides") or {}).get(AXIS) is not None]
        if len(rows) < 3:
            continue
        if len({float((r["overrides"])[AXIS]) for r in rows}) < 2:
            continue

        measured, base, adjusted, alphas, thetas = [], [], [], [], []
        theta_refs: List[float] = []
        for row in rows:
            wt = float(row["overrides"][AXIS])
            rate = ps._predict(doc, row)
            m = ps._measured(row)
            if not rate or m is None:
                continue
            theta = _theta(doc, row, wt, density)
            c_ref = float((row.get("overrides") or {}).get(
                "abrasive_ref_wt_pct", pack_c_ref))
            theta_ref = _theta(doc, row, c_ref, density)
            n_eff = _local_exponent(doc, row, wt)
            if theta is None or theta_ref is None or n_eff is None:
                continue
            measured.append(m)
            base.append(rate)
            adjusted.append(rate * correction(theta, theta_ref, n_eff))
            alphas.append(1.0 - n_eff)
            thetas.append(theta)
            theta_refs.append(theta_ref)
        if len(measured) < 3:
            continue

        def shape(pred: List[float]) -> float:
            scale = (sum(m * p for m, p in zip(measured, pred))
                     / sum(p * p for p in pred))
            return (100.0 * sum(abs(scale * p - m) / m
                                for m, p in zip(measured, pred)) / len(measured))

        def scale_ratio(pred: List[float]) -> float:
            ratios = sorted(m / p for m, p in zip(measured, pred))
            return ratios[len(ratios) // 2]

        rows_out.append({
            "dataset": path.stem,
            "n": len(measured),
            "shape_before": shape(base),
            "shape_after": shape(adjusted),
            "scale_before": scale_ratio(base),
            "scale_after": scale_ratio(adjusted),
            "alpha_min": min(alphas),
            "alpha_max": max(alphas),
            "theta_min": min(thetas),
            "theta_max": max(thetas),
            "theta_ref": max(theta_refs),
            "in_premise": min(alphas) > 0.0 and max(alphas) <= 1.0,
        })
    return rows_out, _summary(rows_out)


DATASETS = (Path(__file__).resolve().parents[1] / "cmp_sim" / "data"
            / "validation" / "datasets")


def _summary(rows_out: List[Dict[str, Any]]) -> Dict[str, Any]:
    shipping = {s.dataset: s.shape_mape for s in ps.score_all()
                if s.shape_mape is not None}
    before = sorted(shipping.values())

    def median_with(subset: List[Dict[str, Any]]) -> float:
        changed = {r["dataset"]: r["shape_after"] for r in subset
                   if r["dataset"] in shipping}
        after = sorted({**shipping, **changed}.values())
        return after[len(after) // 2]

    in_premise = [r for r in rows_out if r["in_premise"]]
    return {
        "priced": len(rows_out),
        "in_premise": len(in_premise),
        "affected": len([r for r in rows_out if r["dataset"] in shipping]),
        "median_before": before[len(before) // 2],
        "median_all": median_with(rows_out),
        "median_in_premise": median_with(in_premise),
        "improved": sum(1 for r in in_premise
                        if r["shape_after"] < r["shape_before"] - 0.05),
        "worsened": sum(1 for r in in_premise
                        if r["shape_after"] > r["shape_before"] + 0.05),
    }


def main() -> int:
    rows, s = rescore()
    print(f"datasets priced     : {s['priced']}  "
          f"(inside the premise alpha>0: {s['in_premise']})")
    print(f"improved / worsened : {s['improved']} / {s['worsened']}  "
          f"(inside the premise)")
    print(f"corpus median  {s['median_before']:.2f}%  ->  "
          f"{s['median_in_premise']:.2f}%  (in-premise datasets only)")
    print(f"               {s['median_before']:.2f}%  ->  "
          f"{s['median_all']:.2f}%  (applied to every priced dataset)")
    print()
    hdr = f"{'dataset':50s} {'shape%':>14s} {'scale x':>16s} {'alpha':>13s} {'theta':>15s}"
    print(hdr)
    for r in sorted(rows, key=lambda r: r["shape_after"] - r["shape_before"]):
        flag = " " if r["in_premise"] else "*"
        print(f"{flag}{r['dataset'][:49]:49s} "
              f"{r['shape_before']:6.1f}->{r['shape_after']:6.1f} "
              f"{r['scale_before']:7.3f}->{r['scale_after']:7.3f} "
              f"{r['alpha_min']:6.2f}..{r['alpha_max']:5.2f} "
              f"{r['theta_min']:7.2f}..{r['theta_max']:6.1f}"
              f"  ref {r['theta_ref']:7.2f}")
    print("\n* = outside the derivation's premise "
          "(alpha = 1 - n_eff outside (0, 1] on some row)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
