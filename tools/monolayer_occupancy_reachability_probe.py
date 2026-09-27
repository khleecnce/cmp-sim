"""Can a monolayer occupancy saturation be DERIVED here, or is it unreachable?

The target (docs/limits.md §28)
-------------------------------
11 of 14 iso-condition loading ladders flatten as loading rises (median
residual curvature -0.296) while the model's concentration response is a pure
power law with |curvature| < 0.01 on every ladder.  A term with a known sign is
missing.  The admissible fix adds NO free constant, so it must get its scale
from geometry the model already computes.

The candidate derivation
------------------------
Particles remove material only where they are LOADED, and they are loaded only
inside the real contact between pad and wafer.  The Luo-Dornfeld layer supplies
a monolayer areal count

    N_supply  ~  phi / d^2            (`particles_per_unit_area`)

per unit NOMINAL area, where phi is the abrasive volume fraction.  The number
of monolayer sites that actually lie inside the real contact is

    N_sites   ~  (A_r / A_0) / d^2

with `A_r / A_0` the GW real-contact area fraction the contact layer already
computes for the pad and pressure of the run.  Both scale as `1 / d^2`, so the
particle diameter cancels exactly and the occupancy is set by a ratio of two
quantities the model already has:

    theta  =  N_supply / N_sites  =  phi / (A_r / A_0)

The active count then saturates as sites fill,
`N_active = N_sites * (1 - exp(-theta))` or any equivalent monotone filling law,
which bends the log-log response downwards as loading rises -- the observed
sign -- and introduces no fitted parameter, because `A_r/A_0` comes from the
pad's own asperity statistics and phi from the recipe.

Why this probe must run BEFORE any wiring
-----------------------------------------
This repository's most expensive mistakes are terms that are wired first and
found to be unreachable, inert, or degenerate afterwards.  A derived saturation
is only real if `theta` actually VARIES across the corpus and reaches order 1
somewhere: if `theta << 1` everywhere the filling law is linear in phi and the
term reproduces the existing power law exactly (zero curvature, a derivation
that changes nothing); if `theta >> 1` everywhere the response is flat in phi
everywhere (no ladder would rise at all, which contradicts the measurements).
Equally, every normalised factor in this model must be exactly 1.0 at its
pack's reference condition, so what matters for the RATE is not theta itself
but `theta / theta_ref`.

So this probe reports, per corpus run: phi, the GW area fraction, theta, and
theta relative to the same pack's reference composition -- and whether the
ladders that flatten are the ones with the largest theta span.  It fits
nothing, changes no pack, and wires nothing.

    python tools/monolayer_occupancy_reachability_probe.py
"""

from __future__ import annotations

import math
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

from cmp_sim.core import predictive_score as ps
from cmp_sim.core.params import load_pack

DATASETS = (Path(__file__).resolve().parents[1] / "cmp_sim" / "data"
            / "validation" / "datasets")

AXIS = "abrasive_wt_pct"

# Abrasive mass -> volume fraction needs a density. Rather than invent one, the
# probe reports theta in units where the density cancels: the RATIO
# theta/theta_ref is what the rate uses, and density cancels exactly there
# provided the abrasive is the same material as the pack's reference (which the
# swap detector, limit 27, already checks separately). Absolute theta is
# reported using the pack's own declared density when it has one, and skipped
# otherwise -- an absolute occupancy computed on a guessed density would be an
# invented number wearing a derivation.
DENSITY_KEYS = ("abrasive_density_kg_m3", "abrasive_density_g_cm3")


def _pack_density(pack) -> Optional[float]:
    for key in DENSITY_KEYS:
        param = pack.params.get(key)
        if param is not None and param.value is not None:
            value = float(param.value)
            return value * 1000.0 if key.endswith("g_cm3") else value
    return None


def _area_fraction(doc: Dict[str, Any], row: Dict[str, Any]) -> Optional[float]:
    """The GW real-contact area fraction for this run, from the shipping path.

    Taken from the same `pad_state` the solver's kappa hook uses, so the number
    is the one the model actually holds -- not a re-derivation that could drift
    away from it.
    """
    from cmp_sim.api import recipe_from_dict
    from cmp_sim.core.solver import resolve
    from cmp_sim.pad.material import pad_state

    try:
        recipe = recipe_from_dict(ps._recipe_for(doc, row))
        resolved = resolve(recipe)
        state, _notes, _warnings = pad_state(recipe.pad, resolved, None)
        return float(state.real_area_fraction(resolved.pressure_pa))
    except Exception:
        return None


def collect() -> List[Dict[str, Any]]:
    records: List[Dict[str, Any]] = []
    for path in sorted(DATASETS.glob("*.yaml")):
        doc = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        pack_name = str(doc.get("pack") or "")
        try:
            pack = load_pack(pack_name)
        except Exception:
            continue
        ref_param = pack.params.get(AXIS)
        c_ref = (None if ref_param is None or ref_param.value is None
                 else float(ref_param.value))
        density = _pack_density(pack)
        for row in doc.get("conditions") or []:
            wt = (row.get("overrides") or {}).get(AXIS)
            if wt is None or ps._measured(row) is None:
                continue
            area = _area_fraction(doc, row)
            if not area:
                continue
            # phi in the same (arbitrary, density-carrying) units for every row
            # of a pack; the rate only ever uses theta/theta_ref, where the
            # conversion cancels.
            phi = float(wt) / 100.0
            if density:
                phi = (float(wt) / 100.0) / (density / 1000.0)
            records.append({
                "dataset": path.stem,
                "pack": pack_name,
                "wt_pct": float(wt),
                "phi_like": phi,
                "area_fraction": area,
                "theta_like": phi / area,
                "c_ref": c_ref,
                "density_known": bool(density),
            })
    return records


def summarise(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    if not records:
        return {"rows": 0}
    areas = sorted(r["area_fraction"] for r in records)
    thetas = sorted(r["theta_like"] for r in records)
    by_pack: Dict[str, List[Dict[str, Any]]] = {}
    for r in records:
        by_pack.setdefault(r["pack"], []).append(r)
    spans = []
    for pack, rows in by_pack.items():
        ts = [r["theta_like"] for r in rows]
        if len(ts) > 1 and min(ts) > 0:
            spans.append((pack, max(ts) / min(ts)))
    return {
        "rows": len(records),
        "datasets": len({r["dataset"] for r in records}),
        "area_min": areas[0],
        "area_median": areas[len(areas) // 2],
        "area_max": areas[-1],
        "area_spread": areas[-1] / areas[0] if areas[0] > 0 else None,
        "theta_min": thetas[0],
        "theta_median": thetas[len(thetas) // 2],
        "theta_max": thetas[-1],
        "theta_span_within_pack": sorted(spans, key=lambda kv: -kv[1])[:6],
        "density_known_rows": sum(1 for r in records if r["density_known"]),
    }


def main() -> int:
    records = collect()
    s = summarise(records)
    if not s.get("rows"):
        print("no rows collected — the area fraction is not reachable from the "
              "run result. That is itself the finding: the GW contact area the "
              "derivation needs is not published by the solver.")
        return 0
    print(f"rows: {s['rows']} across {s['datasets']} datasets "
          f"({s['density_known_rows']} with a pack density)")
    print()
    print("GW real-contact area fraction A_r/A_0:")
    print(f"  min {s['area_min']:.4g}   median {s['area_median']:.4g}   "
          f"max {s['area_max']:.4g}   spread {s['area_spread']:.2f}x")
    print()
    print("occupancy-like theta = phi / (A_r/A_0):")
    print(f"  min {s['theta_min']:.4g}   median {s['theta_median']:.4g}   "
          f"max {s['theta_max']:.4g}")
    print()
    print("theta span WITHIN one pack (the ratio the rate actually uses):")
    for pack, span in s["theta_span_within_pack"]:
        print(f"  {span:8.2f}x  {pack}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
