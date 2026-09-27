r"""§30's exit condition, measured on the ROWS the correction acts on.

Why this probe exists
---------------------
`docs/limits.md` §30 kept a SCOPED refusal of the load-sharing onset
`chi(theta) = 1 - exp(-theta)`: the law is supported in the band the corpus
reaches (chi 0.75-0.99) and badly damages the one place it acts hardest, the
US2011/0186542A1 diamond series at 0.01-0.04 wt% (chi ~ 0.03), where applying
it takes the shape error 8.7% -> 34.2%. The refusal could not be promoted into
a statement about the LAW because that extreme band held exactly one source.

The exit condition was "an iso-condition loading ladder below ~0.5 wt% from a
NON-diamond abrasive", and `test_the_extreme_dilute_evidence_still_rests_on_a
_single_dataset` was written to fire when one arrived.

THE READER PROBLEM THIS PROBE FIXES
-----------------------------------
That test reads `tools.load_sharing_slope_probe.slope_pairs()`, whose theta is
evaluated at the GEOMETRIC MIDPOINT of an adjacent pair, because a measured
log-log slope belongs to an interval and not to a point. That is right for a
slope and wrong for band membership: the correction is applied to a ROW, at
that row's own theta. A ladder whose most dilute ROW sits at chi = 0.17 --
inside the extreme band -- can have every PAIR midpoint above it, and the
exit-condition test then reports the band as still single-sourced when it is
not. The same error class as §27 (a detector that never receives input) and
§31 (a probe reading the wrong level of the file).

So this probe asks the membership question of the rows, with the same theta
the counterfactual uses to correct them, and reports what the second source
does to the refusal.

    python tools/extreme_dilute_second_source_probe.py
"""

from __future__ import annotations

import math
import sys
from pathlib import Path
from typing import Any, Dict, List

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from cmp_sim.core import predictive_score as ps
from cmp_sim.core.params import load_pack
from tools.derived_saturation_counterfactual import _local_exponent, _theta
from tools.load_sharing_onset_counterfactual import correction
from tools.monolayer_occupancy_reachability_probe import _pack_density

DATASETS = (Path(__file__).resolve().parents[1] / "cmp_sim" / "data"
            / "validation" / "datasets")
AXIS = "abrasive_wt_pct"

#: The band §30's surviving refusal is about: the derivation claims more than
#: 80% of the load is NOT carried by particles here, so the correction is at
#: its largest and any error in it is unmissable.
EXTREME_CHI = 0.2


def rows_in_band(cut: float = EXTREME_CHI) -> List[Dict[str, Any]]:
    """Every scored ROW whose own chi falls below the cut.

    Membership is evaluated at the row's theta -- the one the correction is
    applied at -- not at a pair midpoint.
    """
    out: List[Dict[str, Any]] = []
    for path in sorted(DATASETS.glob("*.yaml")):
        doc = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        try:
            pack = load_pack(str(doc.get("pack") or ""))
        except Exception:
            continue
        density = _pack_density(pack)
        for row in doc.get("conditions") or []:
            wt = (row.get("overrides") or {}).get(AXIS)
            if wt is None or ps._measured(row) is None:
                continue
            theta = _theta(doc, row, float(wt), density)
            n_eff = _local_exponent(doc, row, float(wt))
            if theta is None or theta <= 0 or n_eff is None:
                continue
            alpha = 1.0 - n_eff
            chi = 1.0 - math.exp(-theta)
            if chi >= cut:
                continue
            out.append({
                "dataset": path.stem, "wt_pct": float(wt),
                "theta": theta, "chi": chi, "alpha": alpha,
                "in_premise": 0.0 < alpha <= 1.0,
            })
    return out


def sources(cut: float = EXTREME_CHI) -> List[str]:
    return sorted({r["dataset"] for r in rows_in_band(cut)
                   if r["in_premise"]})


def main() -> int:
    from tools.load_sharing_onset_counterfactual import rescore

    band = rows_in_band()
    kept = [r for r in band if r["in_premise"]]
    names = sorted({r["dataset"] for r in kept})
    print(f"rows with chi < {EXTREME_CHI} (in premise) : {len(kept)}")
    print(f"sources supplying them                : {len(names)}")
    for n in names:
        mine = [r for r in kept if r["dataset"] == n]
        print(f"    {n:46s} n={len(mine):2d}  "
              f"wt% {min(r['wt_pct'] for r in mine):.3g}"
              f"-{max(r['wt_pct'] for r in mine):.3g}  "
              f"chi {min(r['chi'] for r in mine):.3f}"
              f"-{max(r['chi'] for r in mine):.3f}")

    print()
    print("what the onset correction does to each of them "
          "(shape%, from the counterfactual):")
    rows, _ = rescore()
    by = {r["dataset"]: r for r in rows}
    for n in names:
        r = by.get(n)
        if r is None:
            print(f"    {n:46s}  not priced")
            continue
        ratio = r["shape_after"] / r["shape_before"]
        print(f"    {n:46s} {r['shape_before']:6.1f}% -> "
              f"{r['shape_after']:6.1f}%   ({ratio:.2f}x)")

    print()
    if len(names) >= 2:
        print("=> the extreme band is NO LONGER single-sourced. §30's refusal "
              "can be re-argued on more than one applicant.")
    else:
        print("=> still single-sourced; §30's scoped refusal stands as written.")

    # A membership claim is only meaningful if the SAME question asked of the
    # pair midpoints gives a different answer -- otherwise the reader was fine
    # and this probe adds nothing.
    from tools.load_sharing_slope_probe import slope_pairs
    pair_sets = sorted({p["dataset"] for p in slope_pairs()
                        if p["in_premise"]
                        and 1.0 - math.exp(-p["theta"]) < EXTREME_CHI})
    print(f"\nsame band read off PAIR MIDPOINTS      : {len(pair_sets)} "
          f"{pair_sets}")
    print(f"read off the ROWS the correction acts on: {len(names)} {names}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
