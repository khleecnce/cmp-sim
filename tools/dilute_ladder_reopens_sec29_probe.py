r"""Does the NEW dilute ladder reopen docs/limits.md §29?

Why a second probe rather than a re-read of the first
-----------------------------------------------------
`tools/load_sharing_slope_probe.py` splits the corpus at `theta = 1`, because
that is where the Poisson occupancy law `chi = 1 - exp(-theta)` turns over.
That was the right cut when the only dilute evidence was one diamond patent at
`theta ~ 0.03`, two orders below the cut.

It is the WRONG cut for judging the new evidence, and the reason is arithmetic
rather than physical: the new colloidal-silica ladder
(`us9422456b2_teos_silica_dilute_loading`, Example 1 of US9422456B2) reaches
`theta = 1.38` at its most dilute pair. That is BELOW the cut in every sense
that matters to the derivation -- `chi(1.38) = 0.75`, i.e. a quarter of the load
is still going to bare pad -- and yet it lands in the ">= 1" bucket and is
averaged in with pairs at `theta = 18`. A knife edge inherited from an era when
no datum sat near it silently discards the only datum that sits near it.

So this probe asks the same question with the knife edge removed, and it asks
it in the way that is hardest to pass:

  1. **Drop the diamond patent entirely.** §29's weakness was that all nine of
     its `theta < 1` pairs came from one source. Re-running WITHOUT that source
     tests whether the trend exists in the rest of the corpus on its own.
  2. **Correlate over the continuum**, no bucket, using the derivation's own
     predicted slope as the x-axis rather than theta. `s_pred(theta)` is
     monotone in theta, so this is the same hypothesis stated without a cut,
     and it is directly interpretable: perfect agreement is slope 1 through the
     origin.
  3. **Report the dilute END as a band, not a point** -- pairs with
     `chi < 0.9`, i.e. where the derivation claims at least 10% of the load is
     NOT carried by particles. That is the physically meaningful definition of
     "the regime where the term does something", and it is stated as a property
     of chi rather than of theta so it cannot be tuned.

Nothing here is fitted; the law has no free parameter.

    python tools/dilute_ladder_reopens_sec29_probe.py
"""

from __future__ import annotations

import math
import statistics
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tools.load_sharing_slope_probe import _spearman, slope_pairs

# The single source that supplied every theta < 1 pair before this run. §29's
# stated weakness was that it stood alone; excluding it is how we find out
# whether it still has to.
SINGLE_SOURCE = "us20110186542a1_w_diamond_h2o2_ph"

# The colloidal-silica ladder added to test §29's exit condition.
NEW_LADDER = "us9422456b2_teos_silica_dilute_loading"


def _chi(theta: float) -> float:
    return 1.0 - math.exp(-theta)


def _fmt(v: Optional[float], spec: str = "+.3f") -> str:
    return "n/a" if v is None else format(v, spec)


def analyse() -> Dict[str, Any]:
    pairs = [p for p in slope_pairs() if p["in_premise"]]
    without = [p for p in pairs if p["dataset"] != SINGLE_SOURCE]

    def corr(rows: List[Dict[str, Any]], key: str) -> Optional[float]:
        rows = [r for r in rows if r.get(key) is not None]
        if len(rows) < 3:
            return None
        return _spearman([r[key] for r in rows], [r["s_meas"] for r in rows])

    # Band defined on chi, not theta: "the term claims >=10% of the load is not
    # on particles here".
    dilute = [p for p in without if _chi(p["theta"]) < 0.9]
    dense = [p for p in without if _chi(p["theta"]) >= 0.9]

    return {
        "pairs": len(pairs),
        "without_single_source": len(without),
        "rho_theta_all": corr(pairs, "theta"),
        "rho_theta_without": corr(without, "theta"),
        "rho_spred_without": corr(without, "s_pred"),
        "dilute": dilute,
        "dense": dense,
        "dilute_sets": sorted({p["dataset"] for p in dilute}),
        "new_ladder_pairs": [p for p in pairs if p["dataset"] == NEW_LADDER],
    }


def main() -> int:
    a = analyse()
    print(f"iso-condition loading pairs (in premise) : {a['pairs']}")
    print(f"  after dropping {SINGLE_SOURCE} : {a['without_single_source']}")
    print()
    print("Spearman(x, measured slope) -- the derivation requires NEGATIVE "
          "against theta,")
    print("and POSITIVE against its own predicted slope s_pred.")
    print(f"  vs theta,  whole corpus            : "
          f"{_fmt(a['rho_theta_all'])}")
    print(f"  vs theta,  diamond source dropped  : "
          f"{_fmt(a['rho_theta_without'])}")
    print(f"  vs s_pred, diamond source dropped  : "
          f"{_fmt(a['rho_spred_without'])}")
    print()
    print("Band defined on chi (not theta): chi < 0.9 means the derivation "
          "claims")
    print(">=10% of the load is NOT carried by particles there.")
    for name, rows in (("chi <  0.9 (dilute)", a["dilute"]),
                       ("chi >= 0.9 (dense) ", a["dense"])):
        if rows:
            print(f"  {name} : n={len(rows):3d}  median s_meas "
                  f"{statistics.median(r['s_meas'] for r in rows):+.3f}")
        else:
            print(f"  {name} : none")
    print(f"  datasets supplying the dilute band : {len(a['dilute_sets'])}  "
          f"{a['dilute_sets']}")
    print()
    print("Is chi < 0.9 a cut chosen to make this pass? Sweep it. The "
          "separation must")
    print("survive every sane threshold, or the band IS the finding.")
    pairs_np = [p for p in slope_pairs()
                if p["in_premise"] and p["dataset"] != SINGLE_SOURCE]
    for cut in (0.5, 0.6, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95, 0.99):
        lo = [p["s_meas"] for p in pairs_np if _chi(p["theta"]) < cut]
        hi = [p["s_meas"] for p in pairs_np if _chi(p["theta"]) >= cut]
        if len(lo) < 3 or len(hi) < 3:
            print(f"  chi < {cut:.2f} : n={len(lo):3d}/{len(hi):3d}  "
                  f"(too few on one side to read)")
            continue
        print(f"  chi < {cut:.2f} : n={len(lo):3d}/{len(hi):3d}  "
              f"dilute {statistics.median(lo):+.3f}  vs  dense "
              f"{statistics.median(hi):+.3f}  "
              f"gap {statistics.median(lo) - statistics.median(hi):+.3f}")
    print()
    print(f"the new ladder's own pairs ({NEW_LADDER}):")
    for p in sorted(a["new_ladder_pairs"], key=lambda p: p["theta"]):
        print(f"  theta {p['theta']:7.3f}  chi {_chi(p['theta']):.3f}  "
              f"{p['c1']:>5g}->{p['c2']:<5g} wt%   s_meas "
              f"{p['s_meas']:+.3f}   s_pred {_fmt(p['s_pred'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
