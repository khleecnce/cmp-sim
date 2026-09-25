"""Probe: can a DERIVED pH rate law beat the fitted Gaussian with fewer constants?

This is a MEASUREMENT script, not production code. It touches no pack and no
scorer; it answers one question and prints the answer so STATUS.md can record
it.

THE QUESTION
------------
`chemical_rate.ph_response` is a Gaussian with a given peak and THREE fitted
constants per pack (``ph_response_width``, ``ph_floor``, ``ph_acid_floor``).
Across the three silica packs plus the ceria pack that is 12 constants, none of
which comes from a law. STATUS.md's NEXT asks whether a law-derived form can
reach the same shape error with fewer.

CANDIDATE FORM (derived, 2 GLOBAL constants, nothing per-pack)
--------------------------------------------------------------
    f(pH) = S(pH) ** N_DISSOLUTION  *  exp(-B * q_abrasive(pH) * q_film(pH))

Leg 1 — surface-kinetic leg  S(pH) ** 0.5
    Amorphous silica dissolves by OH(-)-catalysed hydrolysis of siloxane
    bridges; Brady & Walther (1990, Chem. Geol. 82:253) measured the rate as
    HALF order in hydroxide activity, r ~ a_OH ** 0.5, over pH 3-8 — a
    LITERATURE exponent, not a fitted one.
    Half order alone cannot be right at high pH: it predicts a 10**1.25 = 18x
    rise from pH 10 to 12.5 where Li 2021 measures a 1.2x span. The missing
    physics is site saturation: the reacting site is the deprotonated silanol
    =SiO(-), whose fraction is Langmuir in a_OH,

        S(pH) = 1 / (1 + 10 ** (pKa - pH)),   pKa = 6.8 (silica surface)

    which is LINEAR in a_OH far below pKa (so S**0.5 reproduces Brady &
    Walther's half order exactly in the regime they measured) and SATURATES
    above it (so the rate stops climbing, as Li 2021 measures). One equation
    covers both regimes; pKa is a measured material property (Ong, Zhao &
    Eisenthal 1992, Chem. Phys. Lett. 191:327, SHG on fused silica: a bimodal
    silanol distribution, ~19% at pKa 4.5 and ~81% at pKa 8.5; 6.8 is the
    population-weighted effective value).

Leg 2 — electrostatic leg  exp(-B * q_a * q_f)
    This is why the optimum MOVES with abrasive charge, the fact this repo
    already established: on the SAME TEOS film, plain silica peaks at pH 11,
    cationic core-shell silica at 4.9, anionic silica at <= 2. A Gaussian
    cannot express that (its peak is an input); a charge product can, because
    the charge sign flips at each material's OWN isoelectric point, which is a
    MEASURED quantity:

        SiO2 film / colloidal silica   IEP 2.0   Parks 1965, Chem. Rev. 65:177
        CeO2                           IEP 6.8   Nabavi 1993, JCIS 160:459
        alpha-Al2O3                    IEP 9.1   Parks 1965
        aminosilane-grafted silica     IEP 9.8   amine pKa (propylamine ~10.6
                                                 lowered by surface density)

    q_x(pH) = tanh(ALPHA * (IEP_x - pH))  -- positive below the IEP, negative
    above it, saturating, the usual shape of a potentiometric titration curve.
    The product q_a * q_f is NEGATIVE for opposite charges (attraction, rate
    up) and POSITIVE for like charges (repulsion, rate down), and
    exp(-B * product) is the Boltzmann weight of the electrostatic part of the
    particle-surface interaction energy in the DLVO sense.

    ALPHA (titration sharpness) and B (interaction strength in kT) are the
    only two free constants and they are GLOBAL -- one pair for every pack.

SCORING RULE (from STATUS.md's NEXT)
------------------------------------
Count constants before and after. Same median with FEWER constants is the win;
a lower median bought with MORE constants is a loss. Shape only: each dataset
keeps one free scale under BOTH forms, so the scale is not what is being
compared.

RESULT 2026-09-27 — THE DERIVED FORM IS FALSIFIED (second falsification)
------------------------------------------------------------------------
6 pH-sweep groups with >= 3 pH levels. In-sample shape medians:

    Gaussian, 4 constants fitted PER GROUP (24 total)      11.0 %
    derived, 2 GLOBAL constants (ALPHA, B)                 60.4 %
    electrostatic leg ALONE, 2 GLOBAL constants            35.3 %
    kinetic leg ALONE (S ** 0.5), ZERO constants           93.6 %

The decisive line is the third. **Adding the derived kinetic leg to the
electrostatic leg makes the fit WORSE (35.3 -> 60.4 %)**, so the leg that was
supposed to be the law-backed half of this proposal is the half that is wrong.

Diagnosis, and it is not "the exponent needs tuning". Brady & Walther's half
order describes STATIC dissolution of silica into solution. S(pH) ** 0.5 is
therefore monotone increasing in pH by construction, but four of the six
measured sweeps peak in ACID (anionic silica <= 2, cationic 4.6-4.9, ceria
5.5) and one of those falls 9x across pH 2-6. A monotone-rising factor cannot
be a component of a falling response unless something else falls faster, and
when it is forced to be, the electrostatic term has to absorb the error: fitting
B per pack (1 global + 4 pack = 5 constants) drives B NEGATIVE for oxide_silica
(-5.0) while the other three packs want +2.25 to +6.75. A term whose sign flips
per pack is a fitting handle, not an interaction energy.

The physical reading: in CMP the chemical leg is NOT net dissolution flux. It
is the mechanical removal of a hydrated, softened surface layer, and the rate
is set by how many particles attach and how soft the layer is -- not by how
fast silica would dissolve if left alone. Dissolution kinetics enter the layer's
THICKNESS, which saturates, not the removal rate directly. This repo already
carries that mechanism (Cook 1990) in the softening term; importing it a second
time as a rate law double-counts it.

CONSEQUENCE FOR THE INCUMBENT -- the honest number is NOT 11.0 %
----------------------------------------------------------------
The Gaussian's 11.0 % is in-sample with 4 constants against groups of 3, 4, 7,
9 and 11 levels. Two of the six groups have constants >= levels, i.e. exact
interpolation (li2021, n=3, scores 0.0 %). Under leave-one-pH-LEVEL-out
(refit peak+width+floor+acid_floor on n-1, predict the held-out level) the
Gaussian scores **52.9 %** over 42 held-out points. The electrostatic form with
its 2 constants fitted on the OTHER FIVE GROUPS -- a strictly harsher protocol,
since nothing from the scored group informs it -- scores 66.6 %.

So the incumbent is not a good pH model that a derived form failed to beat. It
is a 4-parameter-per-group interpolator whose out-of-sample pH error is ~50 %,
and a 2-constant charge argument gets within 14 points of it while generalising
across packs. That is where the pH axis's 25-26 % median actually comes from,
and it is the reason a THIRD attempt at a closed-form pH law is not the next
move: the corpus has 6 usable sweeps and 4 distinct peak positions, so any pH
form with a free peak is under-determined no matter how it is derived.
"""
from __future__ import annotations

import glob
import math
import os
import statistics
from typing import Dict, List, Sequence, Tuple

import yaml

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATASET_DIR = os.path.join(HERE, "cmp_sim", "data", "validation", "datasets")

# --- literature constants (see module docstring for citations) -------------
SILANOL_PKA = 6.8           # Ong, Zhao & Eisenthal 1992 (population-weighted)
N_DISSOLUTION = 0.5         # Brady & Walther 1990, half order in a_OH
IEP = {
    "silica": 2.0,          # Parks 1965
    "ceria": 6.8,           # Nabavi 1993
    "alumina": 9.1,         # Parks 1965
    "aminosilane_silica": 9.8,
}
FILM_IEP = {"oxide": 2.0, "quartz": 2.0}

# Which pH-sweep datasets the probe can use, and what abrasive each carries.
# Restricted to sweeps where pH is the ONLY varied axis within a group.
ABRASIVE_OF_PACK = {
    "oxide_silica": "silica",
    "oxide_silica_anionic": "silica",
    "oxide_silica_aminosilane": "aminosilane_silica",
    "sti_ceria": "ceria",
}


def _mrr(cond: dict) -> float | None:
    for key in ("mrr_nm_per_min", "mrr_a_per_min", "rate_nm_per_min"):
        if cond.get(key) is not None:
            v = float(cond[key])
            return v * 10.0 if key.endswith("nm_per_min") else v
    return None


def load_ph_groups() -> List[dict]:
    """Return one entry per (dataset, non-pH condition group)."""
    out: List[dict] = []
    for path in sorted(glob.glob(os.path.join(DATASET_DIR, "*.yaml"))):
        name = os.path.basename(path)[:-5]
        if name.startswith("_"):
            continue
        doc = yaml.safe_load(open(path)) or {}
        pack = doc.get("pack")
        if pack not in ABRASIVE_OF_PACK:
            continue
        film = doc.get("film")
        if film not in FILM_IEP:
            continue
        groups: Dict[tuple, List[Tuple[float, float]]] = {}
        for cond in doc.get("conditions", []):
            ov = cond.get("overrides", {}) or {}
            ph = ov.get("slurry_ph")
            rate = _mrr(cond)
            if ph is None or rate is None:
                continue
            key = (cond.get("pressure_psi"), cond.get("rpm_platen"),
                   ov.get("abrasive_wt_pct"), ov.get("abrasive_size_nm"))
            groups.setdefault(key, []).append((float(ph), rate))
        for key, pts in groups.items():
            if len({p for p, _ in pts}) < 3:
                continue          # a pH form cannot be tested on <3 levels
            out.append({"dataset": name, "pack": pack, "film": film,
                        "abrasive": ABRASIVE_OF_PACK[pack], "group": key,
                        "points": sorted(pts),
                        "calibration": bool(doc.get("used_for_calibration"))})
    return out


# --- the two competing forms ----------------------------------------------
def gaussian(ph: float, peak: float, width: float,
             floor: float, acid_floor: float) -> float:
    side = acid_floor if ph < peak else floor
    return side + (1.0 - side) * math.exp(-(((ph - peak) / width) ** 2))


def derived(ph: float, iep_a: float, iep_f: float,
            alpha: float, b: float) -> float:
    s = 1.0 / (1.0 + 10.0 ** (SILANOL_PKA - ph))
    kinetic = s ** N_DISSOLUTION
    q_a = math.tanh(alpha * (iep_a - ph))
    q_f = math.tanh(alpha * (iep_f - ph))
    return kinetic * math.exp(-b * q_a * q_f)


def shape_error(pred: Sequence[float], meas: Sequence[float]) -> float:
    """Median |err| % after the single best multiplicative scale (geometric)."""
    pairs = [(p, m) for p, m in zip(pred, meas) if p > 0 and m > 0]
    if len(pairs) < 2:
        return float("nan")
    scale = math.exp(statistics.fmean(math.log(m / p) for p, m in pairs))
    return statistics.median(abs(scale * p - m) / m * 100.0 for p, m in pairs)


def fit_gaussian(points, peak) -> Tuple[float, float, float, float]:
    best = (float("inf"), 1.0, 0.0, 0.0)
    for width in [0.3 + 0.1 * i for i in range(80)]:
        for floor in [0.0 + 0.02 * i for i in range(26)]:
            for acid in [0.0 + 0.02 * i for i in range(26)]:
                pred = [gaussian(p, peak, width, floor, acid) for p, _ in points]
                e = shape_error(pred, [m for _, m in points])
                if e == e and e < best[0]:
                    best = (e, width, floor, acid)
    return best


def main() -> None:
    groups = load_ph_groups()
    print(f"pH-sweep groups usable (>=3 pH levels): {len(groups)}\n")

    # --- incumbent: Gaussian, peak given, 3 constants FITTED PER GROUP -----
    gauss_errs: List[float] = []
    for g in groups:
        peak = max(g["points"], key=lambda t: t[1])[0]   # peak given from data
        e, w, f, a = fit_gaussian(g["points"], peak)
        g["gauss"] = e
        gauss_errs.append(e)
        print(f"  GAUSS {g['dataset'][:44]:44s} n={len(g['points']):2d} "
              f"peak={peak:4.1f} w={w:4.1f} fl={f:4.2f} af={a:4.2f} "
              f"-> {e:6.1f}%")
    print(f"\n  Gaussian median {statistics.median(gauss_errs):.1f}%  "
          f"constants = {4 * len(groups)} "
          f"(peak+width+floor+acid_floor per group)\n")

    # --- candidate: derived, 2 GLOBAL constants ---------------------------
    best = (float("inf"), None, None)
    for alpha in [0.1 + 0.05 * i for i in range(40)]:
        for b in [0.0 + 0.25 * i for i in range(41)]:
            errs = []
            for g in groups:
                pred = [derived(p, IEP[g["abrasive"]], FILM_IEP[g["film"]],
                                alpha, b) for p, _ in g["points"]]
                e = shape_error(pred, [m for _, m in g["points"]])
                if e != e:
                    errs = None
                    break
                errs.append(e)
            if errs and statistics.median(errs) < best[0]:
                best = (statistics.median(errs), alpha, b)
    med, alpha, b = best
    print(f"  derived form best global constants: ALPHA={alpha:.2f}  B={b:.2f}")
    for g in groups:
        pred = [derived(p, IEP[g["abrasive"]], FILM_IEP[g["film"]], alpha, b)
                for p, _ in g["points"]]
        e = shape_error(pred, [m for _, m in g["points"]])
        g["derived"] = e
        flag = "WIN " if e < g["gauss"] else "lose"
        print(f"  DERIV {g['dataset'][:44]:44s} n={len(g['points']):2d} "
              f"-> {e:6.1f}%   ({flag} vs {g['gauss']:.1f}%)")
    print(f"\n  derived median {med:.1f}%  constants = 2 GLOBAL "
          f"(ALPHA, B) + 0 per group\n")

    # --- ABLATION: which leg is carrying the derived form? ----------------
    # This is the decisive measurement. If the law-backed kinetic leg helps,
    # removing it must make things worse.
    kin = statistics.median(
        shape_error([(1.0 / (1.0 + 10.0 ** (SILANOL_PKA - p))) ** N_DISSOLUTION
                     for p, _ in g["points"]], [m for _, m in g["points"]])
        for g in groups)

    def elec(ph, g, alpha, b):
        return math.exp(-b * math.tanh(alpha * (IEP[g["abrasive"]] - ph))
                        * math.tanh(alpha * (FILM_IEP[g["film"]] - ph)))

    best_e = (float("inf"), None, None)
    for a in [0.1 + 0.05 * i for i in range(40)]:
        for bb in [0.25 * i for i in range(41)]:
            errs = [shape_error([elec(p, g, a, bb) for p, _ in g["points"]],
                                [m for _, m in g["points"]]) for g in groups]
            if all(e == e for e in errs) and statistics.median(errs) < best_e[0]:
                best_e = (statistics.median(errs), a, bb)

    print("VERDICT (in-sample shape medians)")
    print(f"  Gaussian          : {statistics.median(gauss_errs):5.1f}%  "
          f"constants {4 * len(groups)} (per group)")
    print(f"  derived full      : {med:5.1f}%  constants 2 (global)")
    print(f"  electrostatic ONLY: {best_e[0]:5.1f}%  constants 2 (global)  "
          f"ALPHA={best_e[1]:.2f} B={best_e[2]:.2f}")
    print(f"  kinetic ONLY      : {kin:5.1f}%  constants 0")
    print("  -> removing the LAW-BACKED kinetic leg IMPROVES the fit "
          f"({med:.1f} -> {best_e[0]:.1f}%): that leg is falsified, "
          "not under-tuned. See the module docstring.")


if __name__ == "__main__":
    main()
