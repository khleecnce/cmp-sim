"""Measure whether W's super-Prestonian pressure response is a PASSIVATION
THRESHOLD set by inhibitor coverage — i.e. whether the two axes the model is
currently BLIND to (`inhibitor_ppm`, `fe_ppm`) and the pressure curvature are
ONE phenomenon with ONE law, or three separate handles.

Why this probe exists
---------------------
`ep3161098b1_w_silica_pressure_sweep` is the worst-scoring responsive dataset
in the corpus (54.9% shape). STATUS named the cause as plumbing, not physics:
the dataset sweeps `fe_ppm` and `inhibitor_ppm` and the simulator answers with
the SAME rate for every composition, because `w_fe_oxidizer` declares no term
on either axis. Six compositions therefore collapse onto one predicted curve
and the residual is a fan.

The naive repair is two new fitted constants (a Fenton order in [Fe] and a
Langmuir K for the inhibitor). This probe asks whether ONE law does the work of
BOTH plus the pressure curvature, which would be a constant-REDUCING repair
rather than a constant-adding one.

The candidate law, and where each piece comes from
-------------------------------------------------
Tungsten removal in Fe/H2O2 is the classic Kaufman cycle (J. Electrochem. Soc.
138 (1991) 3460): the oxidiser grows a passivating WOx layer, and the abrasive
must SHEAR THAT LAYER OFF before any metal leaves. A film that must be
mechanically broken before removal starts is a YIELD problem, not a linear one,
so Preston's law acquires a threshold:

    RR = K * V * max(P - P0, 0)                                          (1)

(1) is not new — it is the standard threshold-Preston form used for films with
a finite shear strength. What is new here is the CLAIM about P0. An etch
inhibitor (here picolinic-type, at 37-63 ppm) adsorbs on the WOx and raises the
pressure needed to shear it, so

    P0 = P_y * theta,     theta = K_L*C / (1 + K_L*C)                    (2)

with theta the Langmuir coverage of the inhibitor and P_y the threshold at full
coverage. Two constants (P_y, K_L) against 18 points on 3 inhibitor levels x 3
pressures x 2 Fe levels, so the form is over-determined, not interpolated.

The sharp, falsifiable prediction
---------------------------------
Fit P0 SEPARATELY for each of the six compositions from its own 3-point
pressure ladder (Eq. 1 with two unknowns K*V and P0 -> exactly determined by
2 points, over-determined by 3). Then:

  * If passivation-shear is the mechanism, the six P0 values must ORDER BY
    INHIBITOR CONCENTRATION and must NOT order by Fe. Fe feeds the oxidiser
    cycle (a rate scale), it does not set the film's shear strength.
  * If instead P0 scatters without ordering by inhibitor, the threshold is an
    artefact of fitting curvature and the law is FALSIFIED — report that and
    add nothing.

This is the same protocol as the earlier pressure-saturation probe, which came
back FALSIFIED and was recorded as such. Nothing is written into any pack here;
this script only measures.

Run: python tools/w_passivation_threshold_probe.py
"""
from __future__ import annotations

import math
from collections import defaultdict
from pathlib import Path

import yaml

DATASET = (Path(__file__).resolve().parents[1] / "cmp_sim" / "data" /
           "validation" / "datasets" /
           "ep3161098b1_w_silica_pressure_sweep.yaml")


def load_rows():
    doc = yaml.safe_load(DATASET.read_text(encoding="utf-8"))
    rows = []
    for cond in doc["conditions"]:
        ov = cond.get("overrides") or {}
        rows.append({
            "label": cond["label"],
            "p": float(cond["pressure_psi"]),
            "rate": float(cond["mrr_nm_per_min"]),
            "fe": float(ov["fe_ppm"]),
            "inh": float(ov["inhibitor_ppm"]),
        })
    return rows


def groups(rows):
    """(fe, inhibitor) -> pressure ladder, sorted by pressure."""
    out = defaultdict(list)
    for r in rows:
        out[(r["fe"], r["inh"])].append((r["p"], r["rate"]))
    return {k: sorted(v) for k, v in out.items()}


def fit_threshold(ladder):
    """Least-squares fit of RR = a * (P - P0) over a pressure ladder.

    Linear in (a, b) with b = -a*P0, so solve the 2-parameter linear
    regression RR = a*P + b exactly and read P0 = -b/a. With 3 points this is
    over-determined; the residual is reported so a bad linear fit cannot pass
    as a good threshold.
    """
    n = len(ladder)
    sx = sum(p for p, _ in ladder)
    sy = sum(r for _, r in ladder)
    sxx = sum(p * p for p, _ in ladder)
    sxy = sum(p * r for p, r in ladder)
    denom = n * sxx - sx * sx
    a = (n * sxy - sx * sy) / denom
    b = (sy * a * 0 + sy - a * sx) / n
    p0 = -b / a if a else float("nan")
    pred = [a * p + b for p, _ in ladder]
    ss_res = sum((r - q) ** 2 for (_, r), q in zip(ladder, pred))
    mean = sy / n
    ss_tot = sum((r - mean) ** 2 for _, r in ladder)
    r2 = 1.0 - ss_res / ss_tot if ss_tot else float("nan")
    return a, p0, r2


def fit_preston_exponent(ladder):
    """Plain power-law exponent d(ln RR)/d(ln P) for comparison."""
    xs = [math.log(p) for p, _ in ladder]
    ys = [math.log(r) for _, r in ladder]
    n = len(xs)
    sx, sy = sum(xs), sum(ys)
    sxx = sum(x * x for x in xs)
    sxy = sum(x * y for x, y in zip(xs, ys))
    return (n * sxy - sx * sy) / (n * sxx - sx * sx)


def langmuir_coverage(c, k_l):
    return k_l * c / (1.0 + k_l * c)


def fit_langmuir(points):
    """Fit P0 = P_y * K_L*C/(1+K_L*C) by scanning K_L (1-D), P_y in closed form.

    Only two constants, and K_L is scanned rather than gradient-fitted so the
    reported optimum cannot hide a local minimum.
    """
    best = None
    for i in range(1, 4001):
        k_l = 10 ** (-5 + 4.0 * i / 4000.0)   # 1e-5 .. 1e-1 per ppm
        thetas = [langmuir_coverage(c, k_l) for c, _ in points]
        num = sum(t * p for t, (_, p) in zip(thetas, points))
        den = sum(t * t for t in thetas)
        if den <= 0:
            continue
        p_y = num / den
        sse = sum((p - p_y * t) ** 2 for t, (_, p) in zip(thetas, points))
        if best is None or sse < best[0]:
            best = (sse, k_l, p_y)
    return best


def main():
    rows = load_rows()
    gs = groups(rows)
    print(f"dataset: {DATASET.name}   {len(rows)} points, {len(gs)} compositions")
    print()
    print("  Fe   inh   n    P0(psi)   r2(lin)   Preston-n   rates")
    fitted = []
    for (fe, inh), ladder in sorted(gs.items(), key=lambda kv: (kv[0][1], kv[0][0])):
        a, p0, r2 = fit_threshold(ladder)
        n_exp = fit_preston_exponent(ladder)
        fitted.append({"fe": fe, "inh": inh, "p0": p0, "r2": r2, "n": n_exp})
        rates = " ".join(f"{r:6.1f}" for _, r in ladder)
        print(f" {fe:4.0f}  {inh:4.0f}  {len(ladder)}   {p0:7.3f}   {r2:7.4f}   "
              f"{n_exp:8.2f}   {rates}")
    print()

    # --- ordering test: does P0 order by inhibitor, and NOT by Fe? ----------
    by_inh = defaultdict(list)
    by_fe = defaultdict(list)
    for f in fitted:
        by_inh[f["inh"]].append(f["p0"])
        by_fe[f["fe"]].append(f["p0"])

    print("P0 grouped by INHIBITOR ppm (the law's prediction: increases):")
    inh_means = {}
    for inh in sorted(by_inh):
        vals = by_inh[inh]
        inh_means[inh] = sum(vals) / len(vals)
        print(f"  {inh:4.0f} ppm : mean {inh_means[inh]:6.3f}  "
              f"({', '.join(f'{v:.3f}' for v in vals)})")
    print("P0 grouped by Fe ppm (the law's prediction: NO ordering):")
    fe_means = {}
    for fe in sorted(by_fe):
        vals = by_fe[fe]
        fe_means[fe] = sum(vals) / len(vals)
        print(f"  {fe:4.0f} ppm : mean {fe_means[fe]:6.3f}  "
              f"({', '.join(f'{v:.3f}' for v in vals)})")
    print()

    inh_sorted = [inh_means[k] for k in sorted(inh_means)]
    monotone = all(b >= a for a, b in zip(inh_sorted, inh_sorted[1:]))
    inh_spread = max(inh_sorted) - min(inh_sorted)
    fe_spread = abs(fe_means[max(fe_means)] - fe_means[min(fe_means)])
    print(f"inhibitor-axis spread of P0 : {inh_spread:.3f} psi "
          f"(monotone increasing: {monotone})")
    print(f"Fe-axis spread of P0        : {fe_spread:.3f} psi")
    ratio = inh_spread / fe_spread if fe_spread else float("inf")
    print(f"ratio inhibitor/Fe          : {ratio:.2f}x "
          f"(law needs the inhibitor axis to dominate)")
    print()

    best = fit_langmuir([(f["inh"], f["p0"]) for f in fitted])
    sse, k_l, p_y = best
    print("Langmuir fit of P0 = P_y * K_L C/(1+K_L C)  (2 constants, 6 points):")
    print(f"  K_L = {k_l:.5f} /ppm   P_y = {p_y:.3f} psi   SSE = {sse:.4f}")
    resid = []
    for f in fitted:
        theta = langmuir_coverage(f["inh"], k_l)
        pred = p_y * theta
        resid.append(abs(pred - f["p0"]))
        print(f"  inh {f['inh']:4.0f}: theta {theta:.3f}  P0_pred {pred:6.3f}  "
              f"P0_fit {f['p0']:6.3f}  d {pred - f['p0']:+6.3f}")
    print(f"  mean |residual| = {sum(resid)/len(resid):.3f} psi")
    print()

    # --- what the THRESHOLD buys over plain Preston, per composition -------
    print("Rate SCALE a = K*V after removing the threshold (should now order "
          "by Fe, since Fe drives the oxidiser cycle):")
    for f in sorted(fitted, key=lambda d: (d["inh"], d["fe"])):
        ladder = gs[(f["fe"], f["inh"])]
        a, _, _ = fit_threshold(ladder)
        print(f"  Fe {f['fe']:4.0f} inh {f['inh']:4.0f} : a = {a:7.1f} nm/min/psi")

    verdict = ("SUPPORTED" if monotone and ratio > 2.0 else "FALSIFIED")
    print()
    print(f"VERDICT: threshold-passivation law is {verdict}")


if __name__ == "__main__":
    main()
