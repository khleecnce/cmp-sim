"""What would the DERIVED monolayer saturation do to the corpus, before wiring it?

Context
-------
`docs/limits.md` §28: the corpus median is decided by one dataset, and what it
needs is curvature in the abrasive-loading response -- 11 of 14 iso-condition
ladders flatten while the model's power law has |curvature| < 0.01 everywhere.

`tools/monolayer_occupancy_reachability_probe.py` established that the
candidate derivation is REACHABLE: with the GW real-contact area fraction the
solver already computes (median 1.7e-3, spread 13.8x), the occupancy

    theta = phi / (A_r / A_0)

has median 4.9 and runs from 0.018 to 97.9 -- it crosses order 1, so a filling
law built on it is neither linear everywhere (which would reproduce the present
power law and change nothing) nor saturated everywhere (which would flatten
every ladder, contradicting the measurements).

This probe
----------
Prices the change WITHOUT wiring it, because wiring first and pricing later is
how this repository has repeatedly bought a better trend for a worse rate.

The derived active count is the monolayer count limited by the sites available
inside the real contact,

    N_active = N_sites * (1 - exp(-theta)),   N_sites ~ (A_r/A_0) / d^2

so the particle diameter cancels and, relative to the pack's own reference
composition at the same pad and pressure, the count ratio the rate uses is

    N/N_ref = (1 - exp(-theta)) / (1 - exp(-theta_ref))

against the present power law's `C/C_ref`.  The rate depends on that count
through the same load-sharing exponent the model already resolves, so the
multiplicative correction to a prediction is

    [ ((1-exp(-theta))/theta) / ((1-exp(-theta_ref))/theta_ref) ] ^ n_eff

where `n_eff` is the exponent the shipping model ACTUALLY applies on this row
-- measured per row by perturbing the loading and reading the model's own local
log-log slope, rather than assumed, so a pack carrying a measured exponent is
priced with that exponent and not with the derived one.

Note the correction is exactly 1.0 when `theta = theta_ref`, i.e. at every
pack's reference composition, which is the invariant every factor in this model
must satisfy.  It is <= 1 for `theta > theta_ref` and >= 1 below, i.e. it bends
the response DOWNWARD as loading rises: the measured sign.

Reported: shape error per affected dataset before/after, the corpus median
before/after, AND the absolute-scale ratio before/after -- because a curvature
term moves absolute rate too, and scoring shape alone has previously bought a
13x-wrong rate for a better trend number.

    python tools/derived_saturation_counterfactual.py
"""

from __future__ import annotations

import math
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import yaml

# Running this file directly puts tools/ on sys.path, not the repo root, so the
# sibling probe would not be importable as `tools.<name>`.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from cmp_sim.core import predictive_score as ps
from cmp_sim.core.params import load_pack
from tools.monolayer_occupancy_reachability_probe import (
    _area_fraction, _pack_density)

DATASETS = (Path(__file__).resolve().parents[1] / "cmp_sim" / "data"
            / "validation" / "datasets")
AXIS = "abrasive_wt_pct"


def _theta(doc: Dict[str, Any], row: Dict[str, Any], wt: float,
           density: Optional[float]) -> Optional[float]:
    area = _area_fraction(doc, row)
    if not area:
        return None
    phi = (wt / 100.0) / (density / 1000.0) if density else (wt / 100.0)
    return phi / area


def _local_exponent(doc: Dict[str, Any], row: Dict[str, Any],
                    wt: float) -> Optional[float]:
    """The loading exponent the SHIPPING model applies at this row.

    Measured by perturbation rather than read from the pack, so a measured
    override, a gate or a regime substitution is priced as it actually acts.
    """
    lo, hi = wt * 0.9, wt * 1.1
    out = []
    for value in (lo, hi):
        probe = dict(row)
        probe["overrides"] = dict(row.get("overrides") or {})
        probe["overrides"][AXIS] = value
        rate = ps._predict(doc, probe)
        if not rate:
            return None
        out.append(rate)
    if out[0] <= 0 or out[1] <= 0:
        return None
    return math.log(out[1] / out[0]) / math.log(hi / lo)


def _correction(theta: float, theta_ref: float, n_eff: float) -> float:
    if theta <= 0 or theta_ref <= 0:
        return 1.0
    fill = (1.0 - math.exp(-theta)) / theta
    fill_ref = (1.0 - math.exp(-theta_ref)) / theta_ref
    if fill_ref <= 0:
        return 1.0
    return (fill / fill_ref) ** n_eff


def rescore() -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    rows_out: List[Dict[str, Any]] = []
    for path in sorted(DATASETS.glob("*.yaml")):
        doc = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        try:
            pack = load_pack(str(doc.get("pack") or ""))
        except Exception:
            continue
        ref_param = pack.params.get(AXIS)
        if ref_param is None or ref_param.value is None:
            continue
        c_ref = float(ref_param.value)
        density = _pack_density(pack)

        rows = [r for r in (doc.get("conditions") or [])
                if ps._measured(r) is not None
                and (r.get("overrides") or {}).get(AXIS) is not None]
        if len(rows) < 3:
            continue
        loadings = {float((r["overrides"])[AXIS]) for r in rows}
        if len(loadings) < 2:
            continue

        measured, base, adjusted = [], [], []
        for row in rows:
            wt = float(row["overrides"][AXIS])
            rate = ps._predict(doc, row)
            m = ps._measured(row)
            if not rate or m is None:
                continue
            theta = _theta(doc, row, wt, density)
            theta_ref = _theta(doc, row, c_ref, density)
            n_eff = _local_exponent(doc, row, wt)
            if theta is None or theta_ref is None or n_eff is None:
                continue
            measured.append(m)
            base.append(rate)
            adjusted.append(rate * _correction(theta, theta_ref, n_eff))
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
        })

    # Corpus median, recomputed with the affected datasets replaced. Datasets
    # this term does not touch keep their shipping score, so the headline is
    # comparable to the published one.
    shipping = {s.dataset: s.shape_mape for s in ps.score_all()
                if s.shape_mape is not None}
    changed = {r["dataset"]: r["shape_after"] for r in rows_out
               if r["dataset"] in shipping}
    before = sorted(shipping.values())
    after = sorted({**shipping, **changed}.values())
    summary = {
        "affected": len(changed),
        "median_before": before[len(before) // 2],
        "median_after": after[len(after) // 2],
        "improved": sum(1 for r in rows_out
                        if r["shape_after"] < r["shape_before"] - 0.05),
        "worsened": sum(1 for r in rows_out
                        if r["shape_after"] > r["shape_before"] + 0.05),
    }
    return rows_out, summary


def main() -> int:
    rows, s = rescore()
    print(f"datasets priced : {len(rows)}  (in the scored corpus: {s['affected']})")
    print(f"improved / worsened : {s['improved']} / {s['worsened']}")
    print(f"corpus median  {s['median_before']:.2f}%  ->  {s['median_after']:.2f}%")
    print()
    print(f"{'dataset':52s} {'shape%':>14s} {'scale x':>16s}")
    for r in sorted(rows, key=lambda r: r["shape_after"] - r["shape_before"]):
        print(f"{r['dataset'][:52]:52s} "
              f"{r['shape_before']:6.1f}->{r['shape_after']:6.1f} "
              f"{r['scale_before']:7.3f}->{r['scale_after']:7.3f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
