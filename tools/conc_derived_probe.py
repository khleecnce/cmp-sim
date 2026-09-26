"""Probe: is the abrasive-CONCENTRATION exponent a MATERIAL property (like the
size exponent turned out to be), or is it a free per-pack handle?

This is a MEASUREMENT script, not production code. It touches no pack and no
scorer. It is the concentration twin of ``tools/size_derived_probe.py`` and
deliberately reuses that file's grouping, power-law fit and abrasive-labelling
helpers so the two axes are measured the SAME way; a second independent
implementation would make a difference in the result unattributable.

STATUS.md's NEXT (2026-09-27) specifies the protocol and, importantly, the
stopping rule:

    "If the ratio is not clearly > 2, STOP and record that concentration is NOT
     a material property -- do not re-attribute it anyway for symmetry."

WHAT THE DERIVATIONS PREDICT (the span one law would have to cover)
-------------------------------------------------------------------
Luo & Dornfeld (2001, IEEE Trans. Semicond. Manuf. 14:112) again gives more
than one branch, and the branch decides the exponent m in MRR ~ C_wt**m:

  (a) LOAD-SHARING / SATURATED. The wafer load is fixed, so adding particles
      divides the SAME total load over more contacts. Each particle indents
      less; to first order the removed volume per unit load is conserved and
      MRR is independent of concentration once the pad-wafer gap is fully
      populated.                                              m ~ 0
  (b) ACTIVE-COUNT-LIMITED (dilute). Below full population, every added
      particle is an added cutting point at unchanged load per particle, so
      MRR rises linearly.                                     m ~ +1
  (c) CHEMICAL/TRANSPORT-LIMITED. If the reacted surface layer is regenerated
      more slowly than particles arrive, extra particles do nothing and can
      even hinder (slurry film thickening, agglomeration).     m ~ 0 .. -0.5

So a single derived law must land in about -0.5 .. +1.0. The Langmuir-type
saturation form the packs actually use (``abrasive_conc_half_wt_pct``)
interpolates (b) -> (a) and is a two-constant description of that crossover.

METHOD
------
For every validation dataset, group conditions by every process axis EXCEPT
``abrasive_wt_pct``, keep groups with >= 3 distinct concentrations, and fit
MRR = C * wt**m in log-log. m is scale-free, so the unknown per-dataset scale
drops out -- the same shape-only rule used everywhere else in this repo.
r2 is reported so a noisy group cannot be read as evidence, and the
between-material / within-material variance ratio is computed exactly as for
the size axis (r2 >= 0.5 groups only).

⚠ A LOCAL POWER LAW IS AN APPROXIMATION TO A SATURATING CURVE. If a sweep
spans the knee, its fitted m is a chord slope, not a limiting exponent, and it
will read lower than the dilute-branch value. That biases the WITHIN-material
spread upward (sweeps at different absolute wt% ranges disagree), i.e. it
makes the material hypothesis HARDER to confirm, not easier. Recorded because
it means a negative result here is weaker evidence than the size positive was.

RESULT: see the printout; the finding is recorded in STATUS.md and pinned by
tests/test_conc_exponent_material_scope.py.
"""
from __future__ import annotations

import glob
import math
import os
import statistics
import sys
from typing import Dict, List, Tuple

import yaml

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from size_derived_probe import _abrasive, _mrr, fit_power  # noqa: E402

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATASET_DIR = os.path.join(HERE, "cmp_sim", "data", "validation", "datasets")

# The span a single Luo-Dornfeld-style concentration branch could cover.
DERIVABLE_MIN, DERIVABLE_MAX = -0.5, 1.0

# Process axes held constant within a concentration group. Same whitelist as
# the size probe MINUS the swept axis, PLUS abrasive size (which must be held
# now that it is no longer the sweep variable).
GROUP_AXES = ("pressure_psi", "rpm_platen", "rpm_wafer", "temperature_c",
              "slurry_ph", "abrasive_size_nm", "sfr_ml_min", "oxidizer_wt_pct",
              "inhibitor_mm", "pad")

# The ratio STATUS.md requires before re-attributing the constant.
MIN_RATIO = 2.0


def _conc(cond: dict) -> float | None:
    ov = cond.get("overrides", {}) or {}
    for key in ("abrasive_wt_pct", "abrasive_conc_wt_pct"):
        if ov.get(key) is not None:
            return float(ov[key])
        if cond.get(key) is not None:
            return float(cond[key])
    return None


def load_conc_groups() -> List[dict]:
    """One entry per (dataset, non-concentration condition group), >= 3 wt%."""
    out: List[dict] = []
    for path in sorted(glob.glob(os.path.join(DATASET_DIR, "*.yaml"))):
        name = os.path.basename(path)[:-5]
        if name.startswith("_"):
            continue
        doc = yaml.safe_load(open(path)) or {}
        groups: Dict[tuple, List[Tuple[float, float]]] = {}
        for cond in doc.get("conditions", []):
            c = _conc(cond)
            rate = _mrr(cond)
            if c is None or rate is None or c <= 0 or rate <= 0:
                continue
            ov = cond.get("overrides", {}) or {}
            merged = {**cond, **ov}
            key = tuple(merged.get(k) for k in GROUP_AXES)
            groups.setdefault(key, []).append((c, rate))
        for _key, pts in groups.items():
            if len({c for c, _ in pts}) < 3:
                continue
            out.append({"dataset": name, "pack": doc.get("pack"),
                        "film": doc.get("film"), "points": sorted(pts)})
    return out


def material_scope() -> dict:
    """Between- vs within-material spread of the fitted exponents."""
    rows = []
    for g in load_conc_groups():
        m, r2 = fit_power(g["points"])
        cs = sorted({c for c, _ in g["points"]})
        rows.append({"dataset": g["dataset"], "film": g["film"],
                     "abrasive": _abrasive(g["dataset"], g["pack"]),
                     "m": m, "r2": r2, "k": len(cs),
                     "lo": cs[0], "hi": cs[-1]})
    rows.sort(key=lambda r: r["m"])
    by: Dict[str, List[float]] = {}
    for r in rows:
        if r["r2"] >= 0.5:
            by.setdefault(r["abrasive"], []).append(r["m"])
    means = [statistics.fmean(v) for v in by.values()]
    within = [v - statistics.fmean(vals) for vals in by.values()
              if len(vals) > 1 for v in vals]
    between_sd = statistics.stdev(means) if len(means) > 1 else None
    within_sd = statistics.pstdev(within) if within else None
    ratio = (between_sd / within_sd) if (between_sd and within_sd) else None
    return {"rows": rows, "by_material": by, "between_sd": between_sd,
            "within_sd": within_sd, "ratio": ratio}


def global_law_scope() -> dict:
    """Test the SURFACE-AREA derivation m = +1/3 as a single GLOBAL constant.

    The material split having failed, the next-simplest hypothesis is the one
    the code already defaults to: Li 2021's surface-area-limited branch
    MRR ~ C**(1/3). Derivation (no fitted constant):

      at fixed weight fraction C and fixed particle diameter d, the number of
      particles per unit slurry volume is n ~ C / d**3. If removal is limited
      by the RATE OF SUPPLY of reacted surface (Cook 1990), the relevant
      quantity is the abrasive surface area presented per unit time, and only
      the particles inside the pad-wafer gap participate. The gap admits a
      2-D monolayer, so the participating count scales as the 2/3 power of the
      volumetric count, n_gap ~ n**(2/3) ~ C**(2/3) / d**2; each contact
      removes volume proportional to its load, which at fixed total wafer load
      falls as 1/n_gap ... carrying Li 2021's algebra through leaves
      MRR ~ C**(1/3).                                 ZERO fitted constants.

    That is a REAL removal of a constant if the data supports it, not a
    renaming: five packs currently declare their OWN fitted value
    (+0.227, +0.3333, +0.3333, -0.4295, -0.406).
    """
    res = material_scope()
    strong = [r for r in res["rows"] if r["r2"] >= 0.5]
    ms = [r["m"] for r in strong]
    third = 1.0 / 3.0
    within = [r for r in strong if abs(r["m"] - third) <= 0.25]
    return {"strong": strong, "n_strong": len(strong),
            "median": statistics.median(ms) if ms else None,
            "mean": statistics.fmean(ms) if ms else None,
            "sd": statistics.stdev(ms) if len(ms) > 1 else None,
            "n_within_0_25": len(within),
            "dissenters": [r for r in strong if abs(r["m"] - third) > 0.25]}


def conc_range_scope() -> dict:
    """Does the exponent track the absolute wt% RANGE instead of the material?

    A saturating (Langmuir-type) response predicts a HIGH chord slope in the
    dilute limit falling toward zero once the gap is populated, so m should
    CORRELATE NEGATIVELY with the sweep's geometric-mean concentration. That
    is a falsifiable prediction with a sign attached, and it is the hypothesis
    the pack constant ``abrasive_conc_half_wt_pct`` encodes.
    """
    strong = [r for r in material_scope()["rows"] if r["r2"] >= 0.5]
    xs = [math.log(math.sqrt(r["lo"] * r["hi"])) for r in strong]
    ys = [r["m"] for r in strong]
    if len(xs) < 3:
        return {"n": len(xs), "r": None}
    mx, my = statistics.fmean(xs), statistics.fmean(ys)
    sxx = sum((x - mx) ** 2 for x in xs)
    syy = sum((y - my) ** 2 for y in ys)
    sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    r = sxy / math.sqrt(sxx * syy) if sxx and syy else None
    return {"n": len(xs), "r": r, "slope": (sxy / sxx) if sxx else None}


def main() -> None:
    res = material_scope()
    rows = res["rows"]
    print(f"conc-sweep groups usable (>=3 distinct wt%): {len(rows)}\n")
    for r in rows:
        mark = "" if DERIVABLE_MIN <= r["m"] <= DERIVABLE_MAX else "  <-- OUTSIDE"
        print(f"  {r['dataset'][:40]:40s} {str(r['film'])[:7]:7s} "
              f"{r['abrasive'][:12]:12s} k={r['k']} "
              f"wt={r['lo']:5.2f}-{r['hi']:5.2f}%  m={r['m']:+6.2f}  "
              f"r2={r['r2']:5.2f}{mark}")
    ms = [r["m"] for r in rows]
    if ms:
        print(f"\n  measured exponents: m = {min(ms):+.2f} .. {max(ms):+.2f}"
              f"   median {statistics.median(ms):+.2f}")
        if len(ms) > 1:
            print(f"  spread (stdev)    : {statistics.stdev(ms):.2f}")
        span = (max(ms) - min(ms)) / (DERIVABLE_MAX - DERIVABLE_MIN)
        print(f"  a single branch must land in [{DERIVABLE_MIN:+.1f}, "
              f"{DERIVABLE_MAX:+.1f}]; the corpus occupies {span * 100:.0f}% "
              "of that span.")

    print("\nBY ABRASIVE MATERIAL (r2 >= 0.5 groups only)")
    for abr, vals in sorted(res["by_material"].items(),
                            key=lambda kv: statistics.fmean(kv[1])):
        spread = f"{min(vals):+.2f}..{max(vals):+.2f}" if len(vals) > 1 else "-"
        print(f"  {abr:14s} k={len(vals)}  mean m={statistics.fmean(vals):+.2f}"
              f"   spread {spread}")
    if res["ratio"] is None:
        print("\n  VERDICT: the ratio is NOT COMPUTABLE from this corpus "
              "(need >=2 materials AND >=1 material with >=2 sweeps).")
        print("  -> per STATUS.md's stopping rule, do NOT re-attribute the "
              "concentration constant. Leave it withdrawing.")
    else:
        print(f"\n  between-material spread (stdev of means):      "
              f"{res['between_sd']:.2f}")
        print(f"  within-material  spread (stdev of residuals): "
              f"{res['within_sd']:.2f}   ratio {res['ratio']:.1f}x")
        verdict = ("MATERIAL PROPERTY -- re-attribution justified"
                   if res["ratio"] > MIN_RATIO else
                   "NOT a material property -- leave the constant withdrawing")
        print(f"  VERDICT (threshold {MIN_RATIO:.0f}x): {verdict}")

    # --- IS A SINGLE DERIVED +1/3 ENOUGH? ---------------------------------
    g = global_law_scope()
    print("\nSINGLE GLOBAL DERIVED EXPONENT m = +1/3 (surface-area limit, "
          "Li 2021 / Cook 1990)")
    print(f"  r2>=0.5 groups: {g['n_strong']}   median m={g['median']:+.2f}  "
          f"mean {g['mean']:+.2f}  sd {g['sd']:.2f}")
    print(f"  within 0.25 of +1/3: {g['n_within_0_25']}/{g['n_strong']}")
    for r in g["dissenters"]:
        print(f"    dissenter: {r['dataset'][:44]:44s} {r['abrasive']:8s} "
              f"wt={r['lo']:.2f}-{r['hi']:.2f}%  m={r['m']:+.2f} r2={r['r2']:.2f}")

    rng = conc_range_scope()
    if rng.get("r") is not None:
        print("\nSATURATION CHECK -- does m fall as the sweep's mean wt% rises?")
        print(f"  corr(m, log geo-mean wt%) = {rng['r']:+.2f}  "
              f"slope {rng['slope']:+.2f} per e-fold  (n={rng['n']})")
        print("  a Langmuir/saturating response REQUIRES a clearly NEGATIVE "
              "correlation; a near-zero or positive r falsifies it.")


if __name__ == "__main__":
    main()
