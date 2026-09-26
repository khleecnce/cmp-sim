"""Does frictional heating explain the residual on the VELOCITY axis?

Motivation
----------
``tools/pressure_saturation_probe.py`` asked the same question of the PRESSURE
axis and falsified a saturation law: the residual slope against ln P straddles
zero. That probe never touched the other half of Preston's P*V, and the two
axes are NOT symmetric in the physics even though they are symmetric in the
equation:

* pressure enters the CONTACT problem (real area of contact),
* velocity enters the CONTACT problem *and* the ENERGY balance, because the
  frictional power dissipated per unit wafer area is

      q'' = mu * P * V                                   [W/m^2]

  (Coulomb friction, all sliding work converted to heat). Pressure appears in
  q'' too, but a pressure ladder at fixed V raises q'' by the same factor it
  raises the mechanical term, so the thermal effect is partly ABSORBED into the
  per-dataset scale. A velocity ladder is the cleaner probe.

If the interface temperature rises with q'' and the chemical leg is thermally
activated (Arrhenius), the true rate is SUPER-LINEAR in V and a linear-in-V
Preston model must UNDER-predict at the top of every velocity ladder. That is a
sharp, one-sided, falsifiable prediction.

THE DERIVED CHAIN (what would be adopted if the prediction survives)
--------------------------------------------------------------------
1. Frictional power per area          q'' = mu * P * V
2. Interface temperature rise         dT  = R_th * q''
   (R_th = effective thermal resistance of the pad/slurry/wafer stack, K per
   W/m^2; a TOOL property, one GLOBAL constant, not one per pack)
3. Arrhenius on the chemical leg      f_T = exp(-(Ea/R)(1/(T0+dT) - 1/T0))

Constant accounting if adopted: Ea already exists as a pack field
(``chem_activation_energy_kj_per_mol``) and mu already exists in the pad data.
The only NEW number is R_th, and it is global. So the law costs +1 global
constant and would have to earn it across every velocity ladder at once.

WHAT THIS SCRIPT DOES
---------------------
Measurement only. It fits nothing into any pack. For every dataset with at
least ``MIN_VELOCITY_LEVELS`` distinct platen speeds it fits the corpus's own
single free scale, then regresses ln(measured / scaled prediction) on ln V.

Reading the sign:
  slope > 0  the model under-predicts as V rises  -> consistent with thermal
             activation (the prediction above)
  slope < 0  the model over-predicts as V rises   -> consistent with slurry
             starvation / hydroplaning, the OPPOSITE mechanism
  straddles  neither law is present corpus-wide; the misses are per-dataset

A corpus-wide law must show ONE sign. If the slopes straddle zero the way the
pressure slopes did, the thermal law is falsified at corpus level exactly as
the saturation law was, and no R_th constant may be introduced.

The script also reports the slope against ln(P*V) -- the quantity that actually
drives q'' -- so that a thermal effect masked by the V-only cut has a chance to
show itself.

RESULT 2026-09-26 — THERMAL ACTIVATION FALSIFIED; A REAL P/V ASYMMETRY FOUND
----------------------------------------------------------------------------
5 datasets carry >= 3 distinct platen speeds. Residual slopes at the fitted
scale:

    median d(ln ratio)/d(ln V) = -0.549      1 of 5 positive

The sign is the OPPOSITE of the thermal prediction, so **frictional-heating
activation is falsified as a corpus-wide law and no R_th constant is
introduced.** (Ea/mu are untouched; the pack-level Arrhenius term stays for
runs that state a temperature, which is a different claim.)

What the joint fit adds, and it is the substantive finding. Regressing the same
residual on ln P and ln V TOGETHER separates laws the V-only column cannot:

    median b_P = -0.036        median b_V = -0.549

So the residual is **flat in pressure and strongly falling in velocity**. That
single asymmetry disposes of two more candidate laws at once:

  * Stribeck / hydrodynamic lubrication (rate falls with the Sommerfeld number
    eta*V/P) requires b_P = -b_V, i.e. equal and opposite. Measured sum is
    -0.585, not 0. FALSIFIED.
  * any series-resistance form in the PRODUCT P*V requires b_P = b_V, since
    such a law cannot tell the two factors apart. Measured b_P is ~0 while b_V
    is ~-0.55. FALSIFIED -- and this is an independent confirmation of the
    pressure-saturation rejection already recorded in
    ``tools/pressure_saturation_probe.py``, reached from the other axis.

Preston's LINEARITY IN P therefore survives a second, sharper test: the
corpus's pressure response needs no correction at all. Its linearity in V does
not.

WHY NO CONSTANT WAS ADDED ANYWAY
--------------------------------
The obvious move is a sub-linear velocity exponent, and the counterfactual is
reported by this script so nobody has to guess: a post-hoc V**(2/3-1)
correction moves the corpus median from 16.7 % to 14.5 %. That number is NOT a
licence to adopt it. The methodology here is that an exponent must come from a
law, and the law that predicts exactly 2/3 is reactant starvation:

    reactant inventory per swept area ~ Q/V, and the repo's DERIVED cube-root
    concentration law (2026-09-28) gives MRR ~ P * V * (Q/V)**(1/3)
                                            = P * V**(2/3) * Q**(1/3)

with ZERO free constants. It makes three predictions, not one, and the third is
the check: b_Q must be +1/3. Measured on the only corpus dataset that varies
flow, b_Q = -0.201 -- wrong sign.

That is why the exponent is withheld. But the flow evidence must not be
overstated in the other direction either: the sole flow-varying dataset,
``yang2023_quartz_ceria_L25``, is the WORST-fitting dataset in the corpus
(69 % shape) and its own b_P is -1.276, which contradicts the P-linearity that
the other four datasets establish cleanly. A dataset that cannot reproduce
Preston's best-established axis cannot arbitrate a weaker one. So the honest
verdict on starvation is **INCONCLUSIVE for want of a trustworthy flow sweep**,
not falsified -- and the honest verdict on the 2/3 exponent is that adopting it
now would be fitting the V axis with a number whose supporting law fails its
one independent test.

WHAT WOULD SETTLE IT — SETTLED, SAME DAY. SEE ``tools/sorooshian_flow_probe.py``
--------------------------------------------------------------------------------
The dataset asked for above was found: Sorooshian 2005 (Univ. of Arizona PhD,
Philipossian group), a FULL FACTORIAL on thermal oxide in exactly the three
constrained variables -- flow 40/120 cc/min, velocity 0.32/0.64/0.96 m/s,
pressure 2/4/6 psi. It passes the Preston audit that yang2023 failed, so it is
entitled to arbitrate. Measured:

    b_P = +1.165  (30 ladders)      Preston requires +1.000   AUDIT PASSED
    b_V = +0.655  (29 ladders)      starvation predicts +0.667
    b_Q = -0.010  (47 MATCHED pairs) starvation predicts +0.333

Two legs land almost exactly on the derivation; the third is flatly absent.
Tripling the flow moves the rate by -1.1 % where the law needs +44.2 %, and the
sign of the per-pair exponent is a coin flip (22/47 positive).

**The starvation law is therefore FALSIFIED, and the V**(2/3) exponent still
does not go in.** b_V and b_Q come from the SAME mass balance -- Q/V is one
quantity -- so the derivation cannot be adopted one half at a time. Keeping the
velocity half because it matches while discarding the flow half because it does
not would convert a derived law into a fitted exponent that merely happens to
be written as a fraction.

What HAS changed is the status of the sub-linear velocity response itself: it
is no longer a corpus artefact but a corroborated experimental fact (Sorooshian
+0.655; Tseng & Wang 1997 derive +0.5 for thermal oxide; Park/Lee/Jeong 2005 fit
+0.74 for copper). What is missing is a mechanism that predicts sub-linearity
WITHOUT predicting a flow dependence that measurement says is absent. Two
published observations constrain that search, and both are recorded in
``research/digitized/sorooshian2005_PROVENANCE.md``: slurry utilisation
efficiency is only 2-22 % and itself depends on V (so dispensed Q was probably
the wrong variable all along), and Borucki's Cu data show the velocity exponent
CHANGING SIGN with pressure (-0.81 / -0.62 / +0.33 at 1 / 1.5 / 2 psi), which no
single global exponent can reproduce. Measuring that pressure dependence is the
next move; the corpus median stays 18.9 % until a mechanism survives.
"""
from __future__ import annotations

import math
import statistics
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

import yaml

from cmp_sim.core.predictive_score import _measured, _recipe_for
from cmp_sim.core.validation import dataset_paths

#: Below three distinct speeds a "trend" is a two-point line through noise.
MIN_VELOCITY_LEVELS = 3


@dataclass
class VelocityTrend:
    dataset: str
    film: str
    n: int
    v_min: float
    v_max: float
    #: d ln(measured/predicted) / d ln V at the fitted scale. Positive means
    #: the model UNDER-predicts as speed rises (thermal activation).
    slope_v: float
    #: the same regression against ln(P*V), i.e. against frictional power.
    slope_pv: Optional[float]
    #: JOINT regression of ln(ratio) on ln P and ln V together. This is the
    #: discriminator: a V/P (lubrication) law needs b_p == -b_v, a pure
    #: velocity exponent needs b_p == 0. None when P and V are collinear.
    joint_p: Optional[float] = None
    joint_v: Optional[float] = None


def _run(doc: Dict[str, Any], row: Dict[str, Any]) -> Optional[float]:
    from cmp_sim.api import run_recipe
    try:
        result = run_recipe(_recipe_for(doc, row))
    except Exception:
        return None
    value = result.get("removal_rate_A_per_min")
    return None if value in (None, 0) else float(value)


def _slope(xs: Sequence[float], ys: Sequence[float]) -> Optional[float]:
    """Ordinary least squares slope, or None if x has no spread."""
    mx = sum(xs) / len(xs)
    my = sum(ys) / len(ys)
    den = sum((x - mx) ** 2 for x in xs)
    if den == 0:
        return None
    return sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / den


def _joint(lp: Sequence[float], lv: Sequence[float],
           ly: Sequence[float]) -> Optional[Tuple[float, float]]:
    """Two-variable OLS of ly on (lp, lv). None if the design is collinear.

    Solved in closed form from the 2x2 normal equations so the probe keeps no
    numerical dependency. The determinant is the design's P-V independence:
    when a dataset ramps P and V together it is zero and no separation is
    possible, which is exactly when the answer must be withheld.
    """
    n = len(ly)
    mp = sum(lp) / n
    mv = sum(lv) / n
    my = sum(ly) / n
    spp = sum((x - mp) ** 2 for x in lp)
    svv = sum((x - mv) ** 2 for x in lv)
    spv = sum((a - mp) * (b - mv) for a, b in zip(lp, lv))
    spy = sum((a - mp) * (b - my) for a, b in zip(lp, ly))
    svy = sum((a - mv) * (b - my) for a, b in zip(lv, ly))
    det = spp * svv - spv * spv
    if spp == 0 or svv == 0 or abs(det) < 1e-12 * max(spp * svv, 1e-30):
        return None
    return ((svv * spy - spv * svy) / det, (spp * svy - spv * spy) / det)


def _joint3(cols: Sequence[Sequence[float]],
            ly: Sequence[float]) -> Optional[Tuple[float, ...]]:
    """OLS of ly on several centred regressors, via Gaussian elimination.

    Returns None when the design matrix is singular (two regressors moved
    together across the whole dataset), which is precisely when the
    coefficients would be uninterpretable.
    """
    k = len(cols)
    n = len(ly)
    means = [sum(c) / n for c in cols]
    my = sum(ly) / n
    xc = [[c[i] - m for i in range(n)] for c, m in zip(cols, means)]
    yc = [v - my for v in ly]
    a = [[sum(xc[r][i] * xc[c][i] for i in range(n)) for c in range(k)]
         + [sum(xc[r][i] * yc[i] for i in range(n))] for r in range(k)]
    for col in range(k):
        piv = max(range(col, k), key=lambda r: abs(a[r][col]))
        if abs(a[piv][col]) < 1e-12:
            return None
        a[col], a[piv] = a[piv], a[col]
        pv = a[col][col]
        a[col] = [v / pv for v in a[col]]
        for r in range(k):
            if r == col:
                continue
            f = a[r][col]
            a[r] = [v - f * w for v, w in zip(a[r], a[col])]
    return tuple(row[k] for row in a)


#: Starvation prediction, derived and free of fitted constants.
#:
#:   The reactant that the abrasion consumes arrives with the slurry at
#:   volumetric rate Q and is swept through the contact at speed V, so the
#:   reactant inventory available per unit swept area scales as Q/V. The repo
#:   has already DERIVED (2026-09-28, surface-area law) that the rate goes as
#:   the cube root of abrasive/reactant concentration, m = +1/3. Substituting
#:   C_eff ~ Q/V into MRR ~ k*P*V*C_eff**(1/3) gives
#:
#:       MRR ~ P * V**(2/3) * Q**(1/3)
#:
#:   so, measured as a residual against a linear-in-P*V Preston prediction,
#:   the three coefficients are pinned with NO free constant:
STARVATION_BP, STARVATION_BV, STARVATION_BQ = 0.0, -1.0 / 3.0, 1.0 / 3.0


def flow_test(dataset: str = "yang2023_quartz_ceria_L25"
              ) -> Optional[Dict[str, float]]:
    """Joint P/V/Q residual fit on the one dataset that varies flow.

    Only ``yang2023_quartz_ceria_L25`` records ``flow_ml_min`` AND varies it,
    so the starvation law can be tested exactly once in this corpus. That is a
    weakness of the evidence, not of the law, and it is reported as such.
    """
    for path in dataset_paths():
        if Path(path).stem != dataset:
            continue
        doc = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
        rows = [r for r in (doc.get("conditions") or [])
                if _measured(r) is not None and _speed(r)
                and r.get("pressure_psi") and r.get("flow_ml_min")]
        if len(rows) < 6:
            return None
        measured, predicted = [], []
        lp, lv, lq = [], [], []
        for row in rows:
            value = _run(doc, row)
            if value is None:
                return None
            measured.append(float(_measured(row)))
            predicted.append(value)
            lp.append(math.log(float(row["pressure_psi"])))
            lv.append(math.log(float(_speed(row))))  # type: ignore[arg-type]
            lq.append(math.log(float(row["flow_ml_min"])))
        scale = (sum(m * p for m, p in zip(measured, predicted))
                 / sum(p * p for p in predicted))
        ly = [math.log(m / (scale * p)) for m, p in zip(measured, predicted)]
        fit = _joint3([lp, lv, lq], ly)
        if fit is None:
            return None
        return {"n": float(len(rows)), "b_p": fit[0], "b_v": fit[1],
                "b_q": fit[2]}
    return None


def _speed(row: Dict[str, Any]) -> Optional[float]:
    """Platen speed as the velocity proxy.

    The corpus records rpm, and relative pad-wafer speed is proportional to
    platen rpm whenever the head tracks the platen (the usual case, and what
    ``_recipe_for`` assumes when rpm_head is absent). A proportionality
    constant does not affect a LOG slope, so rpm is sufficient here.
    """
    value = row.get("rpm_platen")
    return None if value in (None, 0) else float(value)


def trends() -> List[VelocityTrend]:
    out: List[VelocityTrend] = []
    for path in dataset_paths():
        doc = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
        rows = [r for r in (doc.get("conditions") or [])
                if _measured(r) is not None and _speed(r)]
        if len({_speed(r) for r in rows}) < MIN_VELOCITY_LEVELS:
            continue
        measured: List[float] = []
        predicted: List[float] = []
        speeds: List[float] = []
        powers: List[Optional[float]] = []
        ok = True
        for row in rows:
            value = _run(doc, row)
            if value is None:
                ok = False
                break
            measured.append(float(_measured(row)))
            predicted.append(value)
            speed = _speed(row)
            assert speed is not None
            speeds.append(speed)
            pressure = row.get("pressure_psi")
            powers.append(None if not pressure else float(pressure) * speed)
        if not ok or len(measured) < MIN_VELOCITY_LEVELS:
            continue

        # One free multiplicative scale, exactly as the corpus scorer uses, so
        # the slope is a SHAPE statement: a pure calibration error cannot
        # create it.
        scale = (sum(m * p for m, p in zip(measured, predicted))
                 / sum(p * p for p in predicted))
        ly = [math.log(m / (scale * p)) for m, p in zip(measured, predicted)]

        slope_v = _slope([math.log(v) for v in speeds], ly)
        if slope_v is None:
            continue
        slope_pv = None
        if all(q for q in powers):
            slope_pv = _slope([math.log(float(q)) for q in powers], ly)

        joint_p = joint_v = None
        pressures = [r.get("pressure_psi") for r in rows]
        if all(p for p in pressures):
            fit = _joint([math.log(float(p)) for p in pressures],
                         [math.log(v) for v in speeds], ly)
            if fit is not None:
                joint_p, joint_v = fit

        out.append(VelocityTrend(
            dataset=Path(path).stem, film=str(doc.get("film") or "?"),
            n=len(measured), v_min=min(speeds), v_max=max(speeds),
            slope_v=slope_v, slope_pv=slope_pv,
            joint_p=joint_p, joint_v=joint_v))
    return out


def verdict(rows: Sequence[VelocityTrend]) -> Tuple[float, int, int]:
    """(median slope_v, n positive, n total)."""
    med = statistics.median(t.slope_v for t in rows)
    positive = sum(1 for t in rows if t.slope_v > 0)
    return med, positive, len(rows)


def counterfactual_median(exponent: float) -> Optional[float]:
    """Corpus median shape error if V were raised to ``exponent``, not 1.

    Applied as a post-hoc residual correction (multiply the prediction by
    V**(exponent-1)) on every scored dataset, keeping each dataset's single
    free scale. This does NOT modify the model; it answers "what would the
    exponent buy?" so that a future run cannot mistake a cheap fit for a
    derived win.
    """
    errors: List[float] = []
    for path in dataset_paths():
        doc = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
        rows = [r for r in (doc.get("conditions") or [])
                if _measured(r) is not None and _speed(r)]
        if len(rows) < 2:
            continue
        measured, predicted = [], []
        ok = True
        for row in rows:
            value = _run(doc, row)
            if value is None:
                ok = False
                break
            speed = _speed(row)
            assert speed is not None
            measured.append(float(_measured(row)))
            predicted.append(value * speed ** (exponent - 1.0))
        if not ok or len(measured) < 2:
            continue
        scale = (sum(m * p for m, p in zip(measured, predicted))
                 / sum(p * p for p in predicted))
        errors.append(statistics.median(
            abs(scale * p - m) / m * 100.0
            for m, p in zip(measured, predicted) if m))
    return statistics.median(errors) if errors else None


def report(rows: Optional[List[VelocityTrend]] = None) -> str:
    rows = rows if rows is not None else trends()
    lines = [f"{'dataset':46s} {'film':7s}  n  rpm range      "
             f"d(lnR)/d(lnV)  d(lnR)/d(lnPV)   joint b_P   joint b_V",
             "-" * 122]
    for t in sorted(rows, key=lambda t: t.slope_v):
        pv = "      --" if t.slope_pv is None else f"{t.slope_pv:+8.3f}"
        jp = "     --" if t.joint_p is None else f"{t.joint_p:+7.3f}"
        jv = "     --" if t.joint_v is None else f"{t.joint_v:+7.3f}"
        lines.append(f"{t.dataset[:46]:46s} {t.film[:7]:7s} {t.n:2d} "
                     f"{t.v_min:5.0f}-{t.v_max:5.0f} rpm     "
                     f"{t.slope_v:+8.3f}        {pv}     {jp}     {jv}")
    med, positive, total = verdict(rows)
    lines.append("")
    lines.append(f"{total} datasets with >= {MIN_VELOCITY_LEVELS} speed levels; "
                 f"median d(ln ratio)/d(ln V) = {med:+.3f}; "
                 f"{positive}/{total} positive")
    lines.append(
        "Frictional-heating activation predicts a CONSISTENTLY POSITIVE slope "
        "(the model must under-predict at high speed). Slurry starvation "
        "predicts a consistently NEGATIVE one. A straddle falsifies both as "
        "corpus-wide laws and forbids adding a thermal resistance constant.")
    joint = [t for t in rows if t.joint_p is not None and t.joint_v is not None]
    if joint:
        bp = statistics.median(float(t.joint_p) for t in joint)  # type: ignore[arg-type]
        bv = statistics.median(float(t.joint_v) for t in joint)  # type: ignore[arg-type]
        lines.append("")
        lines.append(f"joint fit on {len(joint)} datasets where P and V vary "
                     f"independently: median b_P = {bp:+.3f}, "
                     f"median b_V = {bv:+.3f}, sum = {bp + bv:+.3f}")
        lines.append(
            "A Stribeck/lubrication law (rate falls with the Sommerfeld "
            "number eta*V/P) requires b_P = -b_V, i.e. a SUM near zero with "
            "b_V negative. A pure velocity exponent requires b_P = 0. These "
            "two are distinguishable only in this joint fit, never in the "
            "d(lnR)/d(lnV) column.")
    flow = flow_test()
    lines.append("")
    if flow is None:
        lines.append("starvation test: NOT RUNNABLE (no dataset both records "
                     "and varies flow_ml_min).")
    else:
        lines.append(
            f"starvation test on yang2023 (n={int(flow['n'])}, the ONLY corpus "
            f"dataset that varies flow): measured b_P={flow['b_p']:+.3f} "
            f"b_V={flow['b_v']:+.3f} b_Q={flow['b_q']:+.3f}   vs   "
            f"derived MRR ~ P*V^(2/3)*Q^(1/3) predicting "
            f"b_P={STARVATION_BP:+.3f} b_V={STARVATION_BV:+.3f} "
            f"b_Q={STARVATION_BQ:+.3f} (zero free constants)")
    base = counterfactual_median(1.0)
    alt = counterfactual_median(2.0 / 3.0)
    if base is not None and alt is not None:
        lines.append("")
        lines.append(
            f"counterfactual: applying V**(2/3-1) as a post-hoc correction to "
            f"every scored dataset moves the median from {base:.1f}% to "
            f"{alt:.1f}%. This is reported so the exponent cannot be adopted "
            "on the strength of a number nobody measured; adoption still "
            "requires the flow leg, which is falsified above.")
    return "\n".join(lines)


if __name__ == "__main__":
    print(report())
