"""Re-measure the vetoed-branch loading ladders after the corpus gained a source.

`models/luo_dornfeld.py` quotes four ladders, all from US9499721B2, as the
evidence that the substituted elastic exponent (+1/3) is what the data support
on a vetoed branch. `tests/test_vetoed_branch_is_a_scope_claim.py` asserts that
"ONE dataset" caveat is a FACT and fails when a second source appears, so the
claim has to be widened from a measurement rather than edited to match.

    python tools/vetoed_branch_widening_probe.py
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from plastic_branch_exponent_probe import (dataset_branches, loading_groups,
                                           slope_with_se)


def main() -> int:
    branches = dataset_branches()
    rows = [g for g in loading_groups()
            if branches.get(g["dataset"]) in ("plastic", "transition")]
    slopes = []
    print(f"{'dataset':52s} {'branch':12s} {'n':>2s} {'slope':>8s} "
          f"{'SE':>6s} {'r2':>5s}")
    for g in sorted(rows, key=lambda g: g["dataset"]):
        m, se, r2 = slope_with_se(g["points"])
        slopes.append(m)
        print(f"{g['dataset'][:52]:52s} {branches[g['dataset']]:12s} "
              f"{len(g['points']):2d} {m:+8.3f} {se:6.3f} {r2:5.2f}")
    print()
    print(f"ladders: {len(rows)}   sources: "
          f"{sorted({g['dataset'] for g in rows})}")
    if slopes:
        srt = sorted(slopes)
        print("slopes : " + ", ".join(f"{s:+.3f}" for s in srt))
        print(f"median : {srt[len(srt) // 2]:+.3f}")
        print(f"all positive: {all(s > 0 for s in slopes)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
