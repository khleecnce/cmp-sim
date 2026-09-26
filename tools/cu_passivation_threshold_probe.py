"""Test whether the W passivation-shear THRESHOLD generalises to Cu, i.e.
whether Cu's Preston law also needs `RR = K*V*max(P - P0, 0)` with a non-zero
P0 set by inhibitor coverage.

Why this probe exists
---------------------
The 2026-09-26 run derived a threshold for W from the Kaufman cycle (JES 138
(1991) 3460): the oxidiser grows a passivating WOx film, the abrasive must
shear it off before metal leaves, so Preston acquires a yield offset whose size
is the inhibitor's Langmuir coverage (`cmp_sim/models/passivation_threshold.py`).
That repair took `ep3161098b1_w` from 54.9% to 12.9% shape error.

Cu/BTA is the TEXTBOOK passivation system, so the same logic PREDICTS a
threshold on Cu. STATUS deliberately forbade copying P_y across films (the
Cu-BTA complex is a different solid from WOx with a different shear strength),
so the only admissible move is to measure Cu's own pressure ladders.

Method (identical protocol to the W probe, so the two are comparable)
--------------------------------------------------------------------
For every Cu validation dataset, group rows that share EVERY override and every
non-pressure condition, keeping groups with >=2 distinct pressures. Each group
is one pressure ladder at frozen chemistry. On each ladder fit

    RR = a*(P - P0)                                                       (1)

as the 2-parameter linear regression RR = a*P + b, P0 = -b/a.

Then ask three questions, with the answers decided in advance:

  Q1  Is P0 systematically positive?  A threshold means the intercept must be
      positive (you need pressure BEFORE material moves).  A median P0 near
      zero, or a scatter straddling zero, is a NULL result and must be reported
      as such -- that was the pre-registered outcome STATUS asked for.
  Q2  Does P0 order by inhibitor loading where the corpus varies it?  This is
      the mechanism test.  Without it, a positive intercept is merely curvature
      and cannot be attributed to coverage.
  Q3  Does the threshold actually BUY anything over zero-intercept Preston?
      Report the SSE ratio of the 2-parameter fit against the 1-parameter
      proportional fit on the same ladder.  On a 2-point ladder the threshold
      fits exactly by construction (SSE=0), so those ladders are counted as
      UNINFORMATIVE for Q3 and only >=3-point ladders are used.

Relation to the earlier `tools/p0_per_film_probe.py`
---------------------------------------------------
That probe asked whether ONE P0 per film improves the corpus SCORE, and reported
that a global P0 bought 0.3 points. This probe asks the prior question the W
result made answerable: does Cu's own raw data contain an intercept AT ALL, and
can it be attributed to inhibitor coverage? A score gain from a free intercept
is not evidence of a mechanism; an ordered, positive intercept is. So this is
the mechanism test, not a re-run of the scoring test.

Nothing is written into any pack. This script only measures.

Run: python tools/cu_passivation_threshold_probe.py
"""
from __future__ import annotations

import json
import math
from collections import defaultdict
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "cmp_sim" / "data" / "validation" / "datasets"

# Keys that identify "the same chemistry at a different pressure". Pressure and
# the measured rate are excluded; everything else must match for rows to share a
# ladder.
# NOTE: per-row bookkeeping fields (`measured_mrr_angstrom_per_min`,
# `read_method`, digitisation notes) must be ignored too -- leaving them in made
# every row of us6918821b2 its own singleton group and silently dropped that
# dataset's three 2-point ladders.
LADDER_IGNORE = {"pressure_psi", "mrr_nm_per_min", "label", "notes", "source",
                 "read_method", "comment", "uncertainty_pct"}


def is_ignored(key: str) -> bool:
    return key in LADDER_IGNORE or key.startswith("measured_")


def freeze(obj):
    """Hashable, order-independent view of a condition's non-pressure fields."""
    if isinstance(obj, dict):
        return tuple(sorted((k, freeze(v)) for k, v in obj.items()))
    if isinstance(obj, list):
        return tuple(freeze(v) for v in obj)
    return obj


def cu_datasets():
    out = []
    for path in sorted(DATA.glob("*_cu_*.yaml")):
        doc = yaml.safe_load(path.read_text(encoding="utf-8"))
        conds = doc.get("conditions") or []
        rows = []
        for c in conds:
            if c.get("pressure_psi") is None or c.get("mrr_nm_per_min") is None:
                continue
            key = freeze({k: v for k, v in c.items() if not is_ignored(k)})
            rows.append({
                "p": float(c["pressure_psi"]),
                "rate": float(c["mrr_nm_per_min"]),
                "key": key,
                "ov": c.get("overrides") or {},
            })
        if rows:
            out.append((path.name, doc, rows))
    return out


def ladders(rows):
    g = defaultdict(list)
    for r in rows:
        g[r["key"]].append(r)
    out = []
    for key, rs in g.items():
        ps = {r["p"] for r in rs}
        if len(ps) >= 2:
            out.append(sorted(rs, key=lambda r: r["p"]))
    return out


def fit_threshold(ladder):
    """RR = a*P + b over the ladder; returns (a, P0, r2, sse)."""
    n = len(ladder)
    xs = [r["p"] for r in ladder]
    ys = [r["rate"] for r in ladder]
    sx, sy = sum(xs), sum(ys)
    sxx = sum(x * x for x in xs)
    sxy = sum(x * y for x, y in zip(xs, ys))
    denom = n * sxx - sx * sx
    if denom == 0:
        return None
    a = (n * sxy - sx * sy) / denom
    b = (sy - a * sx) / n
    p0 = -b / a if a else float("nan")
    pred = [a * x + b for x in xs]
    sse = sum((y - q) ** 2 for y, q in zip(ys, pred))
    mean = sy / n
    sst = sum((y - mean) ** 2 for y in ys)
    r2 = 1.0 - sse / sst if sst else float("nan")
    return a, p0, r2, sse


def fit_proportional(ladder):
    """RR = a*P (zero intercept, ONE constant); returns (a, sse)."""
    xs = [r["p"] for r in ladder]
    ys = [r["rate"] for r in ladder]
    den = sum(x * x for x in xs)
    a = sum(x * y for x, y in zip(xs, ys)) / den
    sse = sum((y - a * x) ** 2 for x, y in zip(xs, ys))
    return a, sse


def inhibitor_level(ov):
    """Whatever inhibitor handle this dataset uses, in its own units."""
    for k in ("inhibitor_mM", "inhibitor_ppm", "inhibitor_M", "bta_mM",
              "bta_ppm", "inhibitor_wt_pct"):
        if k in ov and ov[k] is not None:
            return k, float(ov[k])
    return None, None


def median(vals):
    vs = sorted(vals)
    if not vs:
        return float("nan")
    m = len(vs) // 2
    return vs[m] if len(vs) % 2 else 0.5 * (vs[m - 1] + vs[m])


def main():
    records = []
    print("Cu pressure ladders at frozen chemistry")
    print("  dataset                                    n   P(psi range)   "
          "P0(psi)    r2     SSE2/SSE1  inhibitor")
    for name, doc, rows in cu_datasets():
        for lad in ladders(rows):
            fit = fit_threshold(lad)
            if fit is None:
                continue
            a, p0, r2, sse2 = fit
            _, sse1 = fit_proportional(lad)
            ratio = (sse2 / sse1) if sse1 > 0 else float("nan")
            ikey, ival = inhibitor_level(lad[0]["ov"])
            prange = f"{lad[0]['p']:.2f}-{lad[-1]['p']:.2f}"
            # normalise P0 by the ladder's own pressure scale so datasets at
            # very different pressures are comparable
            pmid = 0.5 * (lad[0]["p"] + lad[-1]["p"])
            records.append({
                "dataset": name, "n": len(lad), "p0": p0, "p0_frac": p0 / pmid,
                "r2": r2, "sse_ratio": ratio, "a": a,
                "inh_key": ikey, "inh": ival, "pmid": pmid,
            })
            itxt = f"{ikey}={ival}" if ikey else "-"
            print(f"  {name[:42]:42s} {len(lad)}  {prange:>11s}  "
                  f"{p0:8.3f}  {r2:6.3f}  "
                  f"{ratio:9.3f}  {itxt}")
    print()

    if not records:
        print("no Cu pressure ladders found")
        return

    # ---- Q1: is the intercept systematically positive? --------------------
    p0s = [r["p0"] for r in records if math.isfinite(r["p0"])]
    fracs = [r["p0_frac"] for r in records if math.isfinite(r["p0_frac"])]
    pos = sum(1 for v in p0s if v > 0)
    print(f"Q1 intercept sign: {pos}/{len(p0s)} ladders have P0 > 0")
    print(f"   median P0 = {median(p0s):+.3f} psi   "
          f"median P0/P_mid = {median(fracs):+.3f}")
    # A threshold worth modelling must be both positive AND a meaningful
    # fraction of the applied pressure; 10% of P_mid is the pre-registered bar
    # (below that it changes the rate by less than typical CMP repeatability).
    q1 = (pos / len(p0s) >= 0.75) and (median(fracs) >= 0.10)
    print(f"   -> Q1 {'SUPPORTED' if q1 else 'NULL'} "
          f"(bar: >=75% positive AND median P0 >= 0.10*P_mid)")
    print()

    # ---- Q2: does P0 order by inhibitor loading? -------------------------
    by_inh = defaultdict(list)
    for r in records:
        if r["inh"] is not None:
            by_inh[(r["inh_key"], r["inh"])].append(r["p0_frac"])
    if len(by_inh) >= 2:
        keys = sorted(by_inh)
        print("Q2 P0/P_mid grouped by inhibitor loading:")
        means = []
        for k in keys:
            vals = by_inh[k]
            means.append(sum(vals) / len(vals))
            print(f"   {k[0]}={k[1]:<8g} n={len(vals):2d}  mean {means[-1]:+.3f}")
        mono = all(b >= a for a, b in zip(means, means[1:]))
        print(f"   -> monotone increasing: {mono}")
    else:
        print("Q2 NOT TESTABLE: the Cu corpus's pressure ladders all sit at a "
              f"single inhibitor level ({len(by_inh)} distinct level(s)).")
        print("   A positive intercept therefore cannot be ATTRIBUTED to "
              "coverage from this data, only observed.")
    print()

    # ---- Q3: does the threshold buy anything on >=3-point ladders? -------
    informative = [r for r in records if r["n"] >= 3]
    print(f"Q3 informative ladders (>=3 pressures): {len(informative)}")
    if informative:
        for r in informative:
            print(f"   {r['dataset'][:42]:42s} SSE2/SSE1 = {r['sse_ratio']:.3f}")
        print(f"   median SSE2/SSE1 = {median([r['sse_ratio'] for r in informative]):.3f}")
    else:
        print("   NONE. Every Cu ladder in the corpus has exactly 2 pressures,")
        print("   where a 2-parameter threshold fits EXACTLY by construction.")
        print("   The intercept is therefore not falsifiable on this data.")
    print()

    verdict = "SUPPORTED" if (q1 and informative) else "NULL / NOT ATTRIBUTABLE"
    print(f"VERDICT: Cu passivation threshold is {verdict}")

    out = ROOT / "research" / "cu_passivation_threshold_probe.json"
    out.write_text(json.dumps({
        "records": records,
        "median_p0_psi": median(p0s),
        "median_p0_frac": median(fracs),
        "frac_positive": pos / len(p0s),
        "n_informative_ladders": len(informative),
        "distinct_inhibitor_levels": len(by_inh),
        "verdict": verdict,
    }, indent=2), encoding="utf-8")
    print(f"wrote {out.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
