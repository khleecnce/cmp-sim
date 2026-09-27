"""Would wiring the pad-wafer gap change any prediction? Reachability first.

`decide_supply` returns (p, q) which feed n_C = p(1-alpha*chi) and
n_d = -q(1-alpha*chi)+beta. But `mechanical_factor` OVERRIDES both with the
pack's own measured exponents when they exist. So before wiring the gap, ask
whether the DERIVED exponents are reachable at all.

This script, for every scored dataset:
  1. runs the shipping solver and records the rate,
  2. re-runs with gap_m forced to a multilayer value (10x the diameter),
  3. reports whether the predicted rate moved.

Nothing is fitted and no pack is modified.
"""
from __future__ import annotations

from typing import Any, Dict, List

import yaml

from cmp_sim.core.predictive_score import _recipe_for
from cmp_sim.core.validation import dataset_paths


def main() -> None:
    from cmp_sim import api
    from cmp_sim.core import solver

    rows: List[Dict[str, Any]] = []
    for path in dataset_paths():
        doc = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        conditions = doc.get("conditions") or []
        if not conditions:
            continue
        try:
            base = api.run_recipe(_recipe_for(doc, conditions[0]))
        except Exception:
            continue
        rate0 = base.get("removal_rate_A_per_min")
        regime = base.get("abrasive_regime") or {}
        # Force a multilayer gap by monkeypatching the key lookup the solver
        # uses for pad_wafer_gap_m.
        d_nm = None
        prov = base.get("provenance") or {}
        for key in ("abrasive_d50_nm", "abrasive_size_nm"):
            entry = prov.get(key)
            value = entry.get("value") if isinstance(entry, dict) else entry
            if value:
                d_nm = float(value)
                break
        if not d_nm:
            continue
        gap = 10.0 * d_nm * 1e-9
        original = solver.ResolvedRecipe.p_or

        def patched(self, key, default=None, _orig=original, _gap=gap):
            if key == "pad_wafer_gap_m":
                return _gap
            return _orig(self, key, default)

        solver.ResolvedRecipe.p_or = patched
        try:
            forced = api.run_recipe(_recipe_for(doc, conditions[0]))
        except Exception:
            forced = {}
        finally:
            solver.ResolvedRecipe.p_or = original
        rate1 = forced.get("removal_rate_A_per_min")
        reg1 = forced.get("abrasive_regime") or {}
        if not (rate0 and rate1):
            continue
        rows.append({
            "dataset": path.stem,
            "delta_pct": 100.0 * (float(rate1) - float(rate0)) / float(rate0),
            "p0": regime.get("p"), "p1": reg1.get("p"),
            "nC0": regime.get("n_conc"), "nC1": reg1.get("n_conc"),
            "nd0": regime.get("n_size"), "nd1": reg1.get("n_size"),
        })

    moved = [r for r in rows if abs(r["delta_pct"]) > 0.5]
    print(f"{'dataset':46s} {'dRATE%':>8s} {'p':>12s} {'n_C':>14s} {'n_d':>14s}")
    print("-" * 100)
    for r in sorted(rows, key=lambda x: -abs(x["delta_pct"])):
        f = lambda a, b: f"{a}->{b}"
        print(f"{r['dataset'][:44]:46s} {r['delta_pct']:8.2f} "
              f"{f(r['p0'], r['p1']):>12s} {f(r['nC0'], r['nC1']):>14s} "
              f"{f(r['nd0'], r['nd1']):>14s}")
    print(f"\n{len(rows)} datasets run; {len(moved)} changed the predicted rate "
          f"by more than 0.5% when the gap was forced to 10x the diameter.")
    if not moved:
        print("=> the DERIVED supply exponents are UNREACHABLE: every pack's own "
              "measured exponent overrides them. Wiring the gap cannot change a "
              "single prediction in this corpus.")


if __name__ == "__main__":
    main()
