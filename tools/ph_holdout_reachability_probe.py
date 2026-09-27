"""Is outcome (b) even STRUCTURALLY reachable for the self-graded pH constants?

docs/limits.md §32 found 11 pH-response citations across three packs -- the
largest self-graded family -- and §33 measured the size-exponent family and
refused the repair. STATUS.md's 38th-run instruction is explicit that the pH
family must not be attacked the same way without first asking a cheaper
question:

    "pH 상수는 물질표 같은 다중-출처 평균이 아니므로 (b)의 경로가 구조적으로
     있는지부터 확인하라 -- 없으면 바로 (a)다."
    (the pH constants are not a multi-source average like the material table,
     so check whether a path to (b) exists STRUCTURALLY first; if not, it is
     (a) immediately.)

That is the §31/§19 discipline applied before any fitting: ask reachability
and identifiability before hunting for a law. The size family had a path to
(b) ONLY because `SIZE_EXPONENT_BY_ABRASIVE` had already established that the
exponent is carried by the abrasive MATERIAL, so a material value is an
average over several publications and one of them can be held out. A pH peak
has no such table. This probe asks whether it could have one.

THE TEST
--------
For a held-out pH constant to exist, the pH response must be a property of
some GROUPING that spans more than one publication -- the natural candidates
being (film), (abrasive) and (film, abrasive), which is exactly the structure
that licensed the size table. The measurement is the same one:

    between-group spread  vs  within-group spread   of the fitted pH optimum

with each publication collapsed to one observation first (§33: sibling files
from one paper are not independent evidence). If within-group spread is
comparable to or larger than between-group spread, the optimum is NOT a
property of that grouping, no cross-publication average exists, and outcome
(b) is unreachable -- no amount of data already in the corpus creates a
held-out value.

Every pH optimum is re-fitted here from the raw dataset rows by the same
Gaussian grid search `tools/ph_derived_probe.py` uses, rather than read from
the packs. Reading the packs would be circular: the pack values ARE the
constants under audit.

    python tools/ph_holdout_reachability_probe.py
"""

from __future__ import annotations

import statistics
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tools.ph_derived_probe import fit_gaussian, load_ph_groups
from tools.size_exponent_loo_probe import publication

#: The pH-response citations `tools/calibration_flag_audit.py` flags as
#: self-graded. Subject list only; the audit remains the authority.
IMPLICATED = {
    "cn109609035b_oxide_anionic_silica_ph",
    "dandu2009_sio2_ceria_ph_sweep",
    "us9422456b2_teos_silica_ph_pressure",
}


def fitted_optima(peak_step: float = 0.1) -> List[Dict[str, Any]]:
    """Re-fit every usable pH sweep's optimum from the dataset rows.

    The peak is scanned on a grid rather than taken from the pack, because the
    pack values are the constants being audited. The grid is the pH range the
    corpus actually covers.

    ``peak_step`` trades resolution for time (the inner Gaussian fit is a
    54k-point grid per peak). The verdict this probe produces is about spreads
    of several pH UNITS, so a coarse grid cannot change it -- the enforcing
    test uses 1.0 and the CLI uses 0.1, and a test asserts the two agree on
    the verdict rather than on the digits.
    """
    out: List[Dict[str, Any]] = []
    for g in load_ph_groups():
        points = g["points"]
        best: Tuple[float, float, float, float, float] | None = None
        steps = int(round(12.0 / peak_step)) + 1
        for i in range(steps):
            peak = 1.0 + peak_step * i
            err, width, floor, acid = fit_gaussian(points, peak)
            if err != err:
                continue
            if best is None or err < best[0]:
                best = (err, peak, width, floor, acid)
        if best is None:
            continue
        err, peak, width, floor, acid = best
        out.append({
            "dataset": g["dataset"], "pack": g["pack"], "film": g["film"],
            "abrasive": g["abrasive"], "publication": publication(g["dataset"]),
            "peak": peak, "width": width, "floor": floor, "acid_floor": acid,
            "shape_err": err, "n_levels": len({p for p, _ in points}),
        })
    return out


def spread_by(rows: List[Dict[str, Any]], keys: Tuple[str, ...]
              ) -> Dict[str, Any]:
    """Between- vs within-group spread of the fitted optimum.

    Publications are collapsed to their mean FIRST (docs/limits.md §33): three
    files from one paper are one observation, and counting them as three
    deflates the within-group spread, which is the denominator of the ratio
    the whole attribution would rest on.
    """
    by_pub: Dict[Tuple[Any, ...], List[float]] = {}
    for r in rows:
        by_pub.setdefault(tuple(r[k] for k in keys) + (r["publication"],),
                          []).append(r["peak"])
    table: Dict[Tuple[Any, ...], List[float]] = {}
    for composite, peaks in by_pub.items():
        table.setdefault(composite[:-1], []).append(statistics.fmean(peaks))

    means = [statistics.fmean(v) for v in table.values()]
    within = [v - statistics.fmean(vals)
              for vals in table.values() if len(vals) > 1 for v in vals]
    between_sd = statistics.stdev(means) if len(means) > 1 else float("nan")
    within_sd = statistics.pstdev(within) if within else float("nan")
    multi = {k: v for k, v in table.items() if len(v) > 1}
    return {
        "keys": keys, "groups": table, "between": between_sd,
        "within": within_sd,
        "ratio": between_sd / within_sd if within_sd else float("nan"),
        "groups_with_two_publications": len(multi),
        "worst_within_span": max((max(v) - min(v) for v in multi.values()),
                                 default=0.0),
    }


def donors_available(rows: List[Dict[str, Any]], keys: Tuple[str, ...]
                     ) -> Dict[str, int]:
    """For each implicated dataset, how many OTHER publications share its group.

    This is the count that decides reachability: with zero donors there is no
    held-out value to compute, whatever the spreads say.
    """
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


def verdict(rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Machine-readable form of the READING block below.

    A donor is necessary but NOT sufficient. A donor's optimum is a held-out
    measurement of THIS block's quantity only if the quantity is a property of
    the grouping, i.e. between-group spread >> within-group spread. Below 1.0
    the grouping explains less than nothing -- two members of one group differ
    more than two groups do -- so the "held-out" value is a transplant.
    """
    per_grouping = []
    for keys in GROUPINGS:
        s = spread_by(rows, keys)
        d = donors_available(rows, keys)
        per_grouping.append({
            "keys": keys, "donors": d,
            "has_donor": any(v > 0 for v in d.values()),
            "ratio": s["ratio"], "between": s["between"], "within": s["within"],
            "worst_within_span": s["worst_within_span"],
            "is_property": s["ratio"] == s["ratio"] and s["ratio"] >= PROPERTY_BAR,
        })
    return {
        "groupings": per_grouping,
        "any_donor": any(g["has_donor"] for g in per_grouping),
        "any_property": any(g["is_property"] for g in per_grouping),
        "worst_within_span": max(g["worst_within_span"] for g in per_grouping),
    }


#: The bar the repository already uses elsewhere to license a group-scoped
#: constant (abrasive_effects.py's material split cleared 3.2x against it).
PROPERTY_BAR = 2.0

GROUPINGS = (("film",), ("abrasive",), ("film", "abrasive"))


def main() -> int:
    rows = fitted_optima()
    print(f"pH sweeps with a re-fitted optimum: {len(rows)} groups from "
          f"{len({r['dataset'] for r in rows})} datasets\n")
    hdr = (f"{'dataset':44s} {'film':7s} {'abrasive':9s} {'pub':14s} "
           f"{'peak':>5s} {'width':>6s} {'fit%':>6s}")
    print(hdr)
    for r in sorted(rows, key=lambda r: r["peak"]):
        flag = "*" if r["dataset"] in IMPLICATED else " "
        print(f"{flag}{r['dataset'][:43]:43s} {str(r['film'])[:7]:7s} "
              f"{r['abrasive'][:9]:9s} {r['publication'][:14]:14s} "
              f"{r['peak']:5.1f} {r['width']:6.2f} {r['shape_err']:6.1f}")
    print("\n* = flagged self-graded by tools/calibration_flag_audit.py")

    print("\nCOULD A HELD-OUT pH OPTIMUM EXIST? (publications collapsed first)")
    print("  a grouping supports a held-out value only if the optimum is a")
    print("  PROPERTY of it: between-group spread >> within-group spread, and")
    print("  at least one implicated block has a donor publication.")
    for keys in GROUPINGS:
        s = spread_by(rows, keys)
        d = donors_available(rows, keys)
        label = "+".join(keys)
        print(f"\n  by {label:16s} between={s['between']:5.2f} pH  "
              f"within={s['within']:5.2f} pH  ratio={s['ratio']:5.2f}x")
        print(f"     groups with >=2 publications: "
              f"{s['groups_with_two_publications']}  "
              f"worst within-group span: {s['worst_within_span']:.1f} pH units")
        print(f"     donor publications per implicated block: "
              + (", ".join(f"{k.split('_')[0]}={v}" for k, v in sorted(d.items()))
                 or "none"))

    print("\nREADING")
    v = verdict(rows)
    if not v["any_donor"]:
        print("  No implicated pH block shares any grouping with another")
        print("  publication, so NO held-out optimum can be computed.")
    elif not v["any_property"]:
        print("  Donors EXIST but no grouping is a PROPERTY: on every candidate")
        print("  the within-group spread exceeds the between-group spread, so a")
        print("  donor's optimum is not a measurement of this block's quantity.")
        print(f"  The worst within-group disagreement is "
              f"{v['worst_within_span']:.1f} pH units --")
        print("  a 'held-out' value would be a transplant of that size.")
        print("  Outcome (b) is unreachable by STRUCTURE, not by preference:")
        print("  the repair is (a), and no amount of re-fitting changes it.")
    else:
        print("  A grouping qualifies; the leave-one-out price must now be")
        print("  measured as in tools/size_exponent_loo_probe.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
