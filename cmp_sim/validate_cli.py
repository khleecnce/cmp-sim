"""Literature back-test runner.

    python -m cmp_sim.validate_cli              # summary table
    python -m cmp_sim.validate_cli --json out.json
    python -m cmp_sim.validate_cli --gate 15    # exit 1 unless >=3 datasets within 15%

Scoring is described in ``cmp_sim/core/validation.py``: within one chemistry
group only pressure and the rotation speeds vary, the single free constant Kp
is fitted by least squares, and the reported error is the residual of that fit.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import List

from cmp_sim.core.legacy_bridge import LEGACY_DATASETS
from cmp_sim.core.params import REPO_ROOT
from cmp_sim.core.validation import (GroupFit, all_points_error,
                                     best_fit_per_dataset, run_all)

OWN_DATASETS = REPO_ROOT / "cmp_sim" / "data" / "validation" / "datasets"


def collect(min_points: int = 3) -> List[GroupFit]:
    fits: List[GroupFit] = []
    for d in (OWN_DATASETS, LEGACY_DATASETS):
        if d.exists():
            fits.extend(run_all(d, min_points=min_points))
    return fits


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="cmp-sim-validate")
    ap.add_argument("--json", help="write the full result here")
    ap.add_argument("--gate", type=float, default=None,
                    help="require >=3 in-scope datasets within this MAPE %%")
    ap.add_argument("--min-points", type=int, default=3)
    ap.add_argument("--all-groups", action="store_true",
                    help="show every chemistry group, not just the best per dataset")
    args = ap.parse_args(argv)

    fits = collect(args.min_points)
    if not fits:
        print("no datasets with a pressure/velocity sweep were found", file=sys.stderr)
        return 1

    shown = fits if args.all_groups else list(best_fit_per_dataset(fits).values())
    shown.sort(key=lambda f: f.mape_pct)

    # The all-points error per dataset, so a multi-group dataset cannot hide its
    # bad groups behind its best one. See validation.all_points_error.
    allpts = all_points_error(fits)

    print(f"{'dataset':<50} {'n':>3} {'MAPE%':>7} {'max%':>7}  "
          f"{'allMAPE%':>8} {'grp':>3}  {'read':<9} scope")
    print("-" * 110)
    for f in shown:
        scope = {True: "in", False: "out", None: "?"}[f.in_scope]
        ap = allpts.get(f.dataset, {})
        ngrp = int(ap.get("groups", 1))
        # Only interesting when the dataset actually splits; otherwise identical.
        allm = f"{ap.get('mape_pct', f.mape_pct):>8.1f}" if ngrp > 1 else " " * 8
        print(f"{f.dataset[:50]:<50} {f.n:>3} {f.mape_pct:>7.1f} "
              f"{f.max_abs_error_pct:>7.1f}  {allm} {ngrp:>3}  "
              f"{f.read_method or '-':<9} {scope}")

    in_scope = [f for f in shown if f.in_scope]
    print()
    print(f"{len(shown)} datasets with a P*V sweep, {len(in_scope)} in scope "
          "(semiconductor CMP film stacks)")

    split = [f for f in shown if int(allpts.get(f.dataset, {}).get("groups", 1)) > 1]
    if split:
        print()
        print("datasets that split into several groups — 'MAPE%' is the BEST group, "
              "'allMAPE%' is every point:")
        for f in split:
            ap = allpts[f.dataset]
            print(f"   ! {f.dataset}: best {f.mape_pct:.1f}% over {f.n} pts, "
                  f"all {ap['mape_pct']:.1f}% over {int(ap['n'])} pts "
                  f"in {int(ap['groups'])} groups")

    if args.json:
        Path(args.json).write_text(json.dumps(
            {"groups": [f.as_dict() for f in fits],
             "best_per_dataset": [f.as_dict() for f in shown],
             "all_points_per_dataset": allpts},
            indent=2), encoding="utf-8")
        print(f"wrote {args.json}")

    if args.gate is not None:
        # The gate is judged on the ALL-POINTS error where a dataset splits, so
        # that passing it cannot be a matter of which group got picked.
        def judged(f):
            return allpts.get(f.dataset, {}).get("mape_pct", f.mape_pct)

        passing = [f for f in in_scope if judged(f) <= args.gate]
        print(f"gate: {len(passing)} in-scope datasets within {args.gate:g}% "
              f"(need 3) -> {'PASS' if len(passing) >= 3 else 'FAIL'}")
        for f in passing:
            print(f"   + {f.dataset} MAPE {judged(f):.1f}%")
        held = [f for f in in_scope if judged(f) > args.gate and f.mape_pct <= args.gate]
        for f in held:
            print(f"   - {f.dataset} best group {f.mape_pct:.1f}% but "
                  f"{judged(f):.1f}% over all points — not counted")
        return 0 if len(passing) >= 3 else 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
