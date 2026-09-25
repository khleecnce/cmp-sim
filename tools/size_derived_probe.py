"""Probe: is there ONE abrasive-size exponent that a Luo-Dornfeld derivation
could supply, or does the measured exponent scatter so widely that no single
derived law can cover it?

This is a MEASUREMENT script, not production code. It touches no pack and no
scorer. STATUS.md's NEXT asks for the size-axis equivalent of
``tools/ph_derived_probe.py``, and explicitly asks for THIS check FIRST:

    "Before writing any model, run the equivalent of tools/ph_derived_probe.py
     for size: fit each sweep's own exponent, look at the SPREAD across packs.
     If the measured exponents scatter across the range a single derivation
     would have to cover, the derivation is already falsified."

WHAT THE DERIVATIONS PREDICT (the range a single law would have to cover)
------------------------------------------------------------------------
Luo & Dornfeld (2001, IEEE Trans. Semicond. Manuf. 14:112) model removal as
N_active particles each indenting the film plastically under a shared load.
Two competing d-dependences fall out of the same picture, and which one wins
decides the exponent:

  (a) FIXED SOLIDS LOADING, load shared over all contacting particles.
      At constant weight fraction the particle count goes as d**-3, the load
      per particle as d**+3, the plastic indentation depth as sqrt(P/H) i.e.
      d**1.5 / d = ... ; carrying Luo-Dornfeld's own algebra through
      (volume per particle ~ d * delta**2 with delta the indentation depth)
      gives MRR independent of d to first order, and their published
      correction terms make it WEAKLY RISING.   n ~ 0 .. +0.5

  (b) SIZE-SELECTED CONTACT (the pad's asperity gap admits only the largest
      particles). Then the active count is set by the tail of the size
      distribution, not by the mean, and MRR rises steeply with d.
      n ~ +1 .. +2    (Luo-Dornfeld's "large particle" branch)

  (c) SURFACE-AREA / chemistry-limited removal: the reacted-layer supply is
      proportional to abrasive surface area, which at fixed wt% goes as d**-1.
      n ~ -1    (Cook 1990's regime; the branch that makes small ceria win)

So a single derived law must land somewhere in -1 .. +2. That is the span the
measured exponents are tested against: if the corpus itself scatters across
most of that span, the choice of branch is being made BY the data, which means
a derivation cannot remove the fitted constant -- it can only rename it.

METHOD
------
For every validation dataset, group conditions by every axis EXCEPT abrasive
size, keep groups with >= 3 distinct sizes, and fit the local power law
MRR = C * d**n by least squares in log-log. n is scale-free, so the unknown
per-dataset scale drops out -- exactly the shape-only rule used elsewhere in
this repo. r2 is reported so a noisy group cannot be read as evidence.

RESULT 2026-09-27 -- A SINGLE GLOBAL EXPONENT IS FALSIFIED, BUT THE SCATTER IS
ORGANISED BY ABRASIVE MATERIAL
------------------------------------------------------------------------------
11 groups from 9 datasets, 3-6 distinct sizes each:

    measured n = -0.45 .. +1.00,  median +0.16,  stdev 0.43

That occupies 48 % of the -1..+2 span a Luo-Dornfeld branch choice could
cover, so the pH verdict applies verbatim to a GLOBAL derived exponent: the
branch would be chosen by the data, i.e. the constant renamed, not removed.

But grouping by abrasive material (r2 >= 0.5 groups) the scatter collapses:

    silica         k=3   mean n = -0.13   (-0.45 .. +0.10)
    alumina        k=2   mean n = +0.28   (+0.24 .. +0.33)
    ceria/silica   k=2   mean n = +0.80   (+0.75 .. +0.85)
    ceria          k=1   mean n = +1.00

    between-material spread (stdev of the means)      0.51
    within-material  spread (stdev of the residuals)  0.16      ratio 3.2x

Between-material variance is ~3x within-material, and the ordering is monotone
and crosses materials, films and labs: bouvet2002 silica on three different
films (oxide/W/Ti) all sit near zero, two independent alumina sweeps 15 years
and 20x in size apart (lai2001 50-1000 nm on Cu, su2011 1-3.5 um on SiC) agree
to 0.09, and the two ceria/silica sweeps from ONE patent agree to 0.10 while
sitting 0.5 above every silica group.

READING -- and what it is NOT
-----------------------------
This says the exponent is a property of the ABRASIVE, not a free per-pack
handle, so it can be ASSIGNED from material identity across packs instead of
fitted inside each. Six packs currently declare a fitted
``abrasive_size_exponent``; four material values would cover them, and more
importantly a NEW pack whose abrasive is known inherits an exponent without a
size sweep of its own -- that is the mechanism that turns ``ranking_only``
combinations into real predictions.

It is NOT yet a derivation, and must not be reported as one. The ordering does
not track abrasive hardness (alumina ~20 GPa > silica ~8 GPa > ceria ~6 GPa is
not the measured order), so the Luo-Dornfeld hardness branch does not explain
it. The ordering DOES track chemical affinity for the oxide film -- ceria's
Ce-O-Si "chemical tooth" (Cook 1990; Kelsall/Hoshino 2001) makes removal
proportional to the CONTACT AREA the particle presents, which grows with d,
while an inert silica particle removes by indentation, whose Luo-Dornfeld
algebra is d-independent at fixed solids loading. That is a hypothesis
consistent with the data, not a law fitted here, and the corpus has only ONE
pure-ceria group, so it cannot yet be tested against the alternative.

CAVEATS worth keeping attached to the numbers
---------------------------------------------
- k=1 for pure ceria: "ceria mean +1.00" is a single dataset (son2021).
- The abrasive label for tw202115224a comes from that patent's Table 1 (Nalco
  / Fuso colloidal silica), recorded explicitly here because neither the
  filename nor the pack name carries it.
- Two files (wei2026, su2011) declare a pack marked PLACEHOLDER in their own
  headers; reading the pack instead of the filename mislabels both as ceria
  and MANUFACTURES a false within-ceria spread of 0.10..1.00. The first run of
  this probe did exactly that. Filename is authoritative here.
"""
from __future__ import annotations

import glob
import math
import os
import statistics
from typing import Dict, List, Tuple

import yaml

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATASET_DIR = os.path.join(HERE, "cmp_sim", "data", "validation", "datasets")

# The span a single Luo-Dornfeld-style derivation would have to cover.
DERIVABLE_MIN, DERIVABLE_MAX = -1.0, 2.0

# Process axes that must be held constant within a size group.
GROUP_AXES = ("pressure_psi", "rpm_platen", "rpm_wafer", "temperature_c",
              "slurry_ph", "abrasive_wt_pct", "sfr_ml_min", "oxidizer_wt_pct",
              "inhibitor_mm", "pad")


def _mrr(cond: dict) -> float | None:
    for key in ("mrr_nm_per_min", "mrr_a_per_min", "rate_nm_per_min"):
        if cond.get(key) is not None:
            v = float(cond[key])
            return v * 10.0 if key.endswith("nm_per_min") else v
    return None


def _size(cond: dict) -> float | None:
    ov = cond.get("overrides", {}) or {}
    for key in ("abrasive_size_nm", "abrasive_diameter_nm"):
        if ov.get(key) is not None:
            return float(ov[key])
        if cond.get(key) is not None:
            return float(cond[key])
    return None


def _abrasive(name: str, pack: str | None) -> str:
    """Abrasive material for a dataset.

    ⚠ The FILENAME is authoritative and the PACK is not. Several files carry a
    pack marked PLACEHOLDER in their own header — wei2026 (silica abrasive on
    SiC) and su2011 (alumina abrasive on SiC) both borrow ``sic_ceria_h2o2``
    because no matching pack exists. Reading the pack first mislabelled both as
    ceria and manufactured a false ceria spread. Filename first, pack only as
    a fallback, explicit table for files that name neither.
    """
    explicit = {
        # TW202115224A lists Nalco and Fuso COLLOIDAL SILICA grades in its
        # Example 1 Table 1 (transcribed in that dataset's own header).
        "tw202115224a_cu_abrasive_size_pressure": "silica",
    }
    if name in explicit:
        return explicit[name]
    for hay in (name.lower(), (pack or "").lower()):
        for mat in ("ceriasilica", "ceria", "alumina", "zirconia", "diamond",
                    "silica"):
            if mat in hay:
                return "ceria/silica" if mat == "ceriasilica" else mat
    return "?"


def load_size_groups() -> List[dict]:
    """One entry per (dataset, non-size condition group) with >= 3 sizes."""
    out: List[dict] = []
    for path in sorted(glob.glob(os.path.join(DATASET_DIR, "*.yaml"))):
        name = os.path.basename(path)[:-5]
        if name.startswith("_"):
            continue
        doc = yaml.safe_load(open(path)) or {}
        groups: Dict[tuple, List[Tuple[float, float]]] = {}
        for cond in doc.get("conditions", []):
            d = _size(cond)
            rate = _mrr(cond)
            if d is None or rate is None or d <= 0 or rate <= 0:
                continue
            ov = cond.get("overrides", {}) or {}
            # Group on the PROCESS axes only, by whitelist. A blacklist was
            # tried first and silently split every group into singletons,
            # because provenance fields (source_detail, read_method,
            # digitization_uncertainty_*) differ row by row in these files.
            merged = {**cond, **ov}
            key = tuple(merged.get(k) for k in GROUP_AXES)
            groups.setdefault(key, []).append((d, rate))
        for key, pts in groups.items():
            if len({d for d, _ in pts}) < 3:
                continue
            out.append({"dataset": name, "pack": doc.get("pack"),
                        "film": doc.get("film"), "points": sorted(pts)})
    return out


def fit_power(points: List[Tuple[float, float]]) -> Tuple[float, float]:
    """Least-squares n and r2 for MRR = C * d**n (log-log)."""
    xs = [math.log(d) for d, _ in points]
    ys = [math.log(r) for _, r in points]
    mx, my = statistics.fmean(xs), statistics.fmean(ys)
    sxx = sum((x - mx) ** 2 for x in xs)
    sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    n = sxy / sxx if sxx else float("nan")
    ss_tot = sum((y - my) ** 2 for y in ys)
    ss_res = sum((y - (my + n * (x - mx))) ** 2 for x, y in zip(xs, ys))
    r2 = 1.0 - ss_res / ss_tot if ss_tot else float("nan")
    return n, r2


def main() -> None:
    groups = load_size_groups()
    print(f"size-sweep groups usable (>=3 distinct sizes): {len(groups)}\n")
    rows = []
    for g in groups:
        n, r2 = fit_power(g["points"])
        sizes = sorted({d for d, _ in g["points"]})
        rows.append((g["dataset"], g["pack"], g["film"], n, r2,
                     len(sizes), sizes[0], sizes[-1],
                     _abrasive(g["dataset"], g["pack"])))
    rows.sort(key=lambda r: r[3])
    for ds, pack, film, n, r2, k, lo, hi, abr in rows:
        mark = "" if DERIVABLE_MIN <= n <= DERIVABLE_MAX else "  <-- OUTSIDE"
        print(f"  {ds[:40]:40s} {str(film)[:7]:7s} {abr[:12]:12s} k={k} "
              f"d={lo:6.1f}-{hi:6.1f}nm  n={n:+6.2f}  r2={r2:5.2f}{mark}")
    ns = [r[3] for r in rows]
    strong = [r[3] for r in rows if r[4] >= 0.8]
    print(f"\n  measured exponents: n = {min(ns):+.2f} .. {max(ns):+.2f}"
          f"   median {statistics.median(ns):+.2f}")
    if len(ns) > 1:
        print(f"  spread (stdev)    : {statistics.stdev(ns):.2f}")
    if strong:
        print(f"  r2>=0.8 subset    : n = {min(strong):+.2f} .. "
              f"{max(strong):+.2f}  (n={len(strong)} groups)")
    span = (max(ns) - min(ns)) / (DERIVABLE_MAX - DERIVABLE_MIN)
    print(f"\n  a single Luo-Dornfeld branch must land in "
          f"[{DERIVABLE_MIN:+.1f}, {DERIVABLE_MAX:+.1f}]; the corpus occupies "
          f"{span * 100:.0f}% of that span.")
    print("  -> if that fraction is large, the branch is being chosen BY the "
          "data, and a derivation renames the fitted constant instead of "
          "removing it.")

    # --- DOES ABRASIVE MATERIAL SELECT THE BRANCH? ------------------------
    # The corpus-wide scatter only falsifies a SINGLE global exponent. If the
    # scatter is organised by abrasive material, the branch is a material
    # property (hardness relative to the film), not a free handle -- and then
    # the exponent can be assigned from hardness instead of fitted per pack.
    print("\nBY ABRASIVE MATERIAL (r2 >= 0.5 groups only)")
    by: Dict[str, List[float]] = {}
    for r in rows:
        if r[4] >= 0.5:
            by.setdefault(r[8], []).append(r[3])
    for abr, vals in sorted(by.items(), key=lambda kv: statistics.fmean(kv[1])):
        spread = f"{min(vals):+.2f}..{max(vals):+.2f}" if len(vals) > 1 else "-"
        print(f"  {abr:14s} k={len(vals)}  mean n={statistics.fmean(vals):+.2f}"
              f"   spread {spread}")
    within = [v - statistics.fmean(vals) for vals in by.values() if len(vals) > 1
              for v in vals]
    means = [statistics.fmean(v) for v in by.values()]
    if within and len(means) > 1:
        print(f"\n  between-material spread (stdev of means): "
              f"{statistics.stdev(means):.2f}")
        print(f"  within-material  spread (stdev of residuals): "
              f"{statistics.pstdev(within):.2f}")
        print("  -> if between >> within, the exponent is a MATERIAL property "
              "and can be assigned, not fitted.")


if __name__ == "__main__":
    main()
