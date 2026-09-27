r"""Does the measured loading slope rise toward 1 as the contact empties?

The prediction being tested
---------------------------
`tools/load_sharing_onset_counterfactual.py` derives, with no new constant,
that the fraction of the load carried by particles is the Poisson occupancy of
the real contact,

    chi(theta) = 1 - exp(-theta),     theta = phi / (A_r/A_0)

which makes the local log-log slope of rate against abrasive loading

    s(theta) = (1 - alpha) + alpha * theta * exp(-theta) / (1 - exp(-theta))
                                     \_________ d ln chi / d ln theta _______/

with alpha = 1 - n_eff read off the shipping model per row.  So:

    theta -> 0    s -> 1            (each particle acts independently)
    theta >> 1    s -> 1 - alpha    (the model's own exponent; chi saturates)

That is a falsifiable statement about the DATA that does not go through the
corpus median at all, and it is worth testing separately because the median is
a counting statistic: the counterfactual's verdict (18.17 -> 18.95%) is decided
by exactly one dataset moving across the bar in each direction, which tells us
nothing about whether the law is right.

The test
--------
For every iso-condition loading ladder in the corpus (conditions identical on
every process axis except `abrasive_wt_pct`), take each adjacent pair, compute
the MEASURED local slope

    s_meas = ln(m2/m1) / ln(C2/C1)

and the theta at the geometric midpoint, then ask whether s_meas trends the way
the derivation requires.  Two readings are reported:

  1. the correlation of s_meas with theta -- the derivation demands a NEGATIVE
     one (slope falls as the contact fills);
  2. the split-population medians below and above theta = 1, which is where the
     occupancy law turns over.  The derivation demands the dilute group sit
     near 1 and clearly above the dense group.

Reported alongside: the model's own s_pred on each pair, so a disagreement is
attributed to the derivation rather than to the scoring.  Nothing here is
fitted; there is no free parameter to fit.

    python tools/load_sharing_slope_probe.py
"""

from __future__ import annotations

import math
import statistics
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from cmp_sim.core import predictive_score as ps
from cmp_sim.core.params import load_pack
from tools.derived_saturation_counterfactual import _local_exponent, _theta
from tools.monolayer_occupancy_reachability_probe import _pack_density

DATASETS = (Path(__file__).resolve().parents[1] / "cmp_sim" / "data"
            / "validation" / "datasets")
AXIS = "abrasive_wt_pct"

# Provenance fields differ row to row and are not process axes; grouping on
# them splits every ladder into singletons (docs/limits.md, size-exponent run).
PROCESS_AXES = (
    "pressure_psi", "rpm_platen", "rpm_wafer", "slurry_ph", "oxidizer_wt_pct",
    "inhibitor_wt_pct", "complexant_wt_pct", "abrasive_size_nm", "sfr_ml_min",
    "temperature_c", "dispersant_wt_pct", "abrasive_ref_wt_pct",
)


def _signature(row: Dict[str, Any]) -> Tuple:
    ov = row.get("overrides") or {}
    out: List[Tuple[str, Any]] = []
    for k in PROCESS_AXES:
        v = ov.get(k, row.get(k))
        out.append((k, v))
    return tuple(out)


def slope_pairs() -> List[Dict[str, Any]]:
    pairs: List[Dict[str, Any]] = []
    for path in sorted(DATASETS.glob("*.yaml")):
        doc = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        try:
            pack = load_pack(str(doc.get("pack") or ""))
        except Exception:
            continue
        density = _pack_density(pack)

        rows = [r for r in (doc.get("conditions") or [])
                if ps._measured(r) is not None
                and (r.get("overrides") or {}).get(AXIS) is not None]
        groups: Dict[Tuple, List[Dict[str, Any]]] = {}
        for r in rows:
            groups.setdefault(_signature(r), []).append(r)

        for sig, group in groups.items():
            if len(group) < 2:
                continue
            group = sorted(group, key=lambda r: float(r["overrides"][AXIS]))
            for a, b in zip(group, group[1:]):
                c1 = float(a["overrides"][AXIS])
                c2 = float(b["overrides"][AXIS])
                m1, m2 = ps._measured(a), ps._measured(b)
                if c2 <= c1 or not m1 or not m2:
                    continue
                s_meas = math.log(m2 / m1) / math.log(c2 / c1)
                p1, p2 = ps._predict(doc, a), ps._predict(doc, b)
                s_pred = (math.log(p2 / p1) / math.log(c2 / c1)
                          if p1 and p2 and p1 > 0 and p2 > 0 else None)
                c_mid = math.sqrt(c1 * c2)
                theta = _theta(doc, a, c_mid, density)
                n_eff = _local_exponent(doc, a, c_mid)
                if theta is None or theta <= 0 or n_eff is None:
                    continue
                alpha = 1.0 - n_eff
                pairs.append({
                    "dataset": path.stem, "theta": theta,
                    "s_meas": s_meas, "s_pred": s_pred, "alpha": alpha,
                    "c1": c1, "c2": c2,
                    "in_premise": 0.0 < alpha <= 1.0,
                })
    return pairs


def _spearman(xs: List[float], ys: List[float]) -> Optional[float]:
    n = len(xs)
    if n < 4:
        return None

    def rank(v: List[float]) -> List[float]:
        order = sorted(range(n), key=lambda i: v[i])
        out = [0.0] * n
        i = 0
        while i < n:
            j = i
            while j + 1 < n and v[order[j + 1]] == v[order[i]]:
                j += 1
            avg = (i + j) / 2.0 + 1.0
            for k in range(i, j + 1):
                out[order[k]] = avg
            i = j + 1
        return out

    rx, ry = rank(xs), rank(ys)
    mx, my = sum(rx) / n, sum(ry) / n
    num = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    den = math.sqrt(sum((a - mx) ** 2 for a in rx)
                    * sum((b - my) ** 2 for b in ry))
    return num / den if den else None


def main() -> int:
    pairs = slope_pairs()
    kept = [p for p in pairs if p["in_premise"]]
    print(f"iso-condition loading pairs : {len(pairs)} "
          f"(inside the premise 0 < alpha <= 1: {len(kept)})")
    if not kept:
        return 1

    rho = _spearman([p["theta"] for p in kept], [p["s_meas"] for p in kept])
    dilute = [p["s_meas"] for p in kept if p["theta"] < 1.0]
    dense = [p["s_meas"] for p in kept if p["theta"] >= 1.0]
    print(f"spearman(theta, measured slope) : "
          f"{rho:+.3f}   (derivation requires NEGATIVE)"
          if rho is not None else "spearman: n/a")
    print(f"  theta < 1  : n={len(dilute):3d}  median slope "
          f"{statistics.median(dilute):+.3f}"
          if dilute else "  theta < 1  : none")
    print(f"  theta >= 1 : n={len(dense):3d}  median slope "
          f"{statistics.median(dense):+.3f}"
          if dense else "  theta >= 1 : none")
    print(f"  derivation predicts the dilute group near +1.0 and clearly "
          f"above the dense group")
    dilute_sets = sorted({p["dataset"] for p in kept if p["theta"] < 1.0})
    print(f"  datasets supplying the theta < 1 evidence : "
          f"{len(dilute_sets)}  {dilute_sets}")
    print()
    print(f"{'dataset':46s} {'theta':>8s} {'C1->C2':>16s} "
          f"{'s_meas':>8s} {'s_pred':>8s}")
    for p in sorted(kept, key=lambda p: p["theta"]):
        sp = f"{p['s_pred']:+8.3f}" if p["s_pred"] is not None else "     n/a"
        print(f"{p['dataset'][:46]:46s} {p['theta']:8.3f} "
              f"{p['c1']:7.3g}->{p['c2']:7.3g} {p['s_meas']:+8.3f} {sp}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
