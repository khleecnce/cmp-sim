"""Is outcome (b) reachable for the LAST self-graded constant, `oxidizer_peak_shape_K`?

docs/limits.md §32 listed 18 self-graded pack-constant citations. §33 closed
the `abrasive_size_exponent` family (six citations) on PRICE, §34 closed the
pH-response family (eleven) on STRUCTURE. This is the eighteenth and last:
`cu_h2o2_bta.oxidizer_peak_shape_K = 8.0`, fitted to Du 2004's H2O2 sweep,
which is then scored as a held-out block at 6.2%.

One citation, so the question is only whether outcome (b) exists: can K be
supplied from an oxidiser sweep OTHER than Du 2004? The method is §34's,
because the question is the same one -- is the quantity a property of a
grouping that spans publications, or does it belong to the single experiment
that produced it?

WHAT K IS, AND WHY IT IS TESTABLE ACROSS DATASETS
-------------------------------------------------
`models/chemical_rate.py:peaked_oxidizer_response` is

    f(C) = [KC/(1+KC)] * exp(-C/Cd),      Cd = C_peak * (1 + K*C_peak)

with the peak position pinned to a MEASURED value so that K alone is free
(the pack's note is explicit that a free peak plus a free shape is degenerate
when the data lie on one side of the maximum). K is the Langmuir rate
constant of the promotion half: it has units of 1/wt% and it is a property of
the oxidant-surface pair, so if the mechanism is shared then independent
sweeps on the same film with the same oxidant should return the same K.

That is a falsifiable claim, and it is what this probe measures: refit K per
oxidiser sweep from the raw rows, with each sweep's own peak pinned to its own
argmax, then compare the spread within a (film, oxidant) group against the
spread between groups -- publications collapsed first (§33).

WHY THE PACK'S OWN NOTE ALREADY PREDICTS THE ANSWER, AND WHY IT IS STILL WORTH
MEASURING
------------------------------------------------------------------------------
`cu_h2o2_bta.yaml` records that the Cu oxidiser sweeps in this corpus
contradict each other in SIGN, and that the sign tracks pressure rather than
any slurry variable (`us8501625b2` shows both signs at identical chemistry).
A response that rises in one block and falls in another cannot be described by
one K. But that note is about the axis's slope, not about K's transferability,
and §32's rule is that the repair must be MEASURED rather than inferred -- the
same rule that stopped §33 from assuming the size exponent would transfer
because the material table said it should.

    python tools/oxidizer_k_holdout_probe.py
"""

from __future__ import annotations

import glob
import math
import os
import statistics
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from cmp_sim.models.chemical_rate import peaked_oxidizer_response
from tools.ph_holdout_reachability_probe import PROPERTY_BAR
from tools.size_exponent_loo_probe import publication

DATASET_DIR = (Path(__file__).resolve().parents[1] / "cmp_sim" / "data"
               / "validation" / "datasets")

#: The one oxidiser citation the calibration audit flags as self-graded.
IMPLICATED = {"du2004_cu_h2o2_concentration_sweep"}

#: Override keys that carry an oxidant concentration, and the oxidant each
#: names. Kept explicit: `oxidizer_wt_pct` is generic and its species comes
#: from the dataset, while `h2o2_vol_pct` names its own.
OXIDANT_KEYS = {"h2o2_vol_pct": "h2o2", "oxidizer_wt_pct": None}

#: K grid, 1/wt%. Spans three decades around the pack's 8.0 so a fitted value
#: cannot be pinned by the grid edge without it being visible.
K_GRID = [0.05 * 1.15 ** i for i in range(60)]


def _mrr(cond: dict) -> Optional[float]:
    for key in ("mrr_nm_per_min", "mrr_a_per_min", "rate_nm_per_min"):
        if cond.get(key) is not None:
            v = float(cond[key])
            return v * 10.0 if key.endswith("nm_per_min") else v
    return None


def _shape_error(pred: List[float], meas: List[float]) -> float:
    pairs = [(p, m) for p, m in zip(pred, meas) if p > 0 and m > 0]
    if len(pairs) < 2:
        return float("nan")
    scale = math.exp(statistics.fmean(math.log(m / p) for p, m in pairs))
    return statistics.median(abs(scale * p - m) / m * 100.0 for p, m in pairs)


def fit_k(points: List[Tuple[float, float]]) -> Optional[Dict[str, Any]]:
    """Best K with the peak pinned to this sweep's own argmax.

    Zero-concentration rows are dropped, not fitted: `peaked_oxidizer_response`
    is 0 at C=0 by construction while six blocks in this corpus measure a
    non-zero rate there (the probe `oxidizer_order_probe.py` test 3), so
    including them would score the multiplicative-term failure rather than K.
    """
    pts = [(c, r) for c, r in points if c > 0 and r > 0]
    if len({c for c, _ in pts}) < 3:
        return None
    peak_conc = max(pts, key=lambda cr: cr[1])[0]
    if peak_conc <= 0:
        return None
    best: Optional[Tuple[float, float]] = None
    for k in K_GRID:
        pred = [peaked_oxidizer_response(c, peak_conc, k) for c, _ in pts]
        err = _shape_error(pred, [r for _, r in pts])
        if err != err:
            continue
        if best is None or err < best[0]:
            best = (err, k)
    if best is None:
        return None
    err, k = best
    return {"k": k, "shape_err": err, "peak_conc": peak_conc,
            "levels": len({c for c, _ in pts}),
            "at_grid_edge": k <= K_GRID[0] * 1.001 or k >= K_GRID[-1] * 0.999}


def sweeps() -> List[Dict[str, Any]]:
    """One entry per (dataset, non-oxidant condition group) with >= 3 levels."""
    out: List[Dict[str, Any]] = []
    for path in sorted(glob.glob(os.path.join(str(DATASET_DIR), "*.yaml"))):
        name = os.path.basename(path)[:-5]
        if name.startswith("_"):
            continue
        doc = yaml.safe_load(open(path)) or {}
        film = doc.get("film")
        groups: Dict[tuple, List[Tuple[float, float]]] = {}
        oxidant_of: Dict[tuple, str] = {}
        for cond in doc.get("conditions", []):
            ov = cond.get("overrides", {}) or {}
            conc: Optional[float] = None
            species: str = "unknown"
            for key, named in OXIDANT_KEYS.items():
                if ov.get(key) is not None:
                    conc = float(ov[key])
                    species = str(named or doc.get("oxidizer") or "unknown")
                    break
            rate = _mrr(cond)
            if conc is None or rate is None:
                continue
            key = (cond.get("pressure_psi"), cond.get("rpm_platen"),
                   ov.get("slurry_ph"), ov.get("abrasive_wt_pct"))
            groups.setdefault(key, []).append((conc, rate))
            oxidant_of[key] = species
        for key, pts in groups.items():
            fit = fit_k(sorted(pts))
            if fit is None:
                continue
            out.append({"dataset": name, "pack": doc.get("pack"),
                        "film": str(film), "oxidant": oxidant_of[key],
                        "publication": publication(name), **fit})
    return out


def spread_by(rows: List[Dict[str, Any]], keys: Tuple[str, ...]) -> Dict[str, Any]:
    """Between- vs within-group spread of log10(K), publications collapsed.

    K is a rate constant spanning decades, so the spread is measured in the
    log -- an arithmetic stdev on K would be dominated by whichever block
    fitted the largest value and would report a ratio that says nothing.
    """
    by_pub: Dict[tuple, List[float]] = {}
    for r in rows:
        by_pub.setdefault(tuple(r[k] for k in keys) + (r["publication"],),
                          []).append(math.log10(r["k"]))
    table: Dict[tuple, List[float]] = {}
    for composite, vals in by_pub.items():
        table.setdefault(composite[:-1], []).append(statistics.fmean(vals))
    means = [statistics.fmean(v) for v in table.values()]
    within = [v - statistics.fmean(vals)
              for vals in table.values() if len(vals) > 1 for v in vals]
    between_sd = statistics.stdev(means) if len(means) > 1 else float("nan")
    within_sd = statistics.pstdev(within) if within else float("nan")
    multi = {k: v for k, v in table.items() if len(v) > 1}
    return {"keys": keys, "between": between_sd, "within": within_sd,
            "ratio": between_sd / within_sd if within_sd else float("nan"),
            "groups_with_two_publications": len(multi),
            "worst_within_decades": max((max(v) - min(v) for v in multi.values()),
                                        default=0.0)}


def donors(rows: List[Dict[str, Any]], keys: Tuple[str, ...]) -> Dict[str, int]:
    out: Dict[str, int] = {}
    for r in rows:
        if r["dataset"] not in IMPLICATED:
            continue
        sig = tuple(r[k] for k in keys)
        others = {o["publication"] for o in rows
                  if tuple(o[k] for k in keys) == sig
                  and o["publication"] != r["publication"]}
        out[r["dataset"]] = max(out.get(r["dataset"], 0), len(others))
    return out


GROUPINGS = (("film",), ("oxidant",), ("film", "oxidant"))


def verdict(rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    per = []
    for keys in GROUPINGS:
        s = spread_by(rows, keys)
        d = donors(rows, keys)
        per.append({"keys": keys, "donors": d,
                    "has_donor": any(v > 0 for v in d.values()),
                    "ratio": s["ratio"], "between": s["between"],
                    "within": s["within"],
                    "worst_within_decades": s["worst_within_decades"],
                    "is_property": s["ratio"] == s["ratio"] and s["ratio"] >= PROPERTY_BAR})
    return {"groupings": per,
            "any_donor": any(g["has_donor"] for g in per),
            "any_property": any(g["is_property"] for g in per),
            "worst_within_decades": max(g["worst_within_decades"] for g in per)}


def main() -> int:
    rows = sweeps()
    print(f"oxidiser sweeps with a fittable K: {len(rows)} groups from "
          f"{len({r['dataset'] for r in rows})} datasets\n")
    print(f"{'dataset':46s} {'film':6s} {'oxidant':8s} {'peak':>6s} "
          f"{'K':>8s} {'fit%':>6s} {'lvls':>4s}")
    for r in sorted(rows, key=lambda r: r["k"]):
        flag = "*" if r["dataset"] in IMPLICATED else " "
        edge = " <-grid edge" if r["at_grid_edge"] else ""
        print(f"{flag}{r['dataset'][:45]:45s} {r['film'][:6]:6s} "
              f"{r['oxidant'][:8]:8s} {r['peak_conc']:6.2f} {r['k']:8.2f} "
              f"{r['shape_err']:6.1f} {r['levels']:4d}{edge}")
    print("\n* = flagged self-graded by tools/calibration_flag_audit.py")
    edge = [r for r in rows if r["at_grid_edge"]]
    unknown = [r for r in rows if r["oxidant"] == "unknown"]
    print(f"\nTWO LIMITS OF THIS TABLE, STATED BEFORE THE VERDICT:")
    print(f"  {len(edge)} of {len(rows)} groups pin K at a grid edge. Six sit at")
    print("  the LOW edge, which is not a fit failure but a finding: at K -> 0")
    print("  the promotion limb is linear over the measured range, i.e. those")
    print("  sweeps never reach their peak and contain no curvature to fit.")
    print("  They are kept, because dropping the blocks that disagree with a")
    print("  peaked form is exactly the selection this repository forbids.")
    print(f"  {len(unknown)} of {len(rows)} groups carry oxidant 'unknown': only")
    print("  du2004 uses the species-naming override key, so the by-oxidant")
    print("  grouping is nearly the same partition as by-film and must not be")
    print("  read as an independent test.")

    print("\nCOULD A HELD-OUT K EXIST? (log10 K, publications collapsed first)")
    for keys in GROUPINGS:
        s = spread_by(rows, keys)
        d = donors(rows, keys)
        print(f"\n  by {'+'.join(keys):14s} between={s['between']:5.2f} dec  "
              f"within={s['within']:5.2f} dec  ratio={s['ratio']:5.2f}x")
        print(f"     groups with >=2 publications: "
              f"{s['groups_with_two_publications']}  worst within-group span: "
              f"{s['worst_within_decades']:.2f} decades")
        print("     donor publications for the implicated block: "
              + (", ".join(f"{k.split('_')[0]}={v}" for k, v in sorted(d.items()))
                 or "none"))

    v = verdict(rows)
    print("\nREADING")
    if not v["any_donor"]:
        print("  Du 2004 shares no grouping with another publication: there is")
        print("  no other sweep from which K could be supplied. Outcome (b) is")
        print("  unreachable for want of a donor, and the repair is (a).")
    elif not v["any_property"]:
        print("  A donor exists but K is not a property of any grouping: the")
        print(f"  worst within-group disagreement is {v['worst_within_decades']:.2f}")
        print("  decades, so a 'held-out' K would be a transplant. Repair (a).")
    else:
        print("  A grouping qualifies; price the leave-one-out as in §33.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
