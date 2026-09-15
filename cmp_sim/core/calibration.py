"""Fit the model to the owner's own measurements, and say how far to trust it.

The literature anchors this simulator, but the literature is not the owner's
tool, pad lot or slurry batch. This module closes that gap: give it measured
removal rates and it fits the model to them, then reports the accuracy by
**leave-one-out cross-validation** rather than by how well it fits the data it
was just fitted to.

That distinction is the whole point. Any model with a free constant can be made
to pass through its own calibration points; the in-sample error of a one-
parameter fit to one point is exactly zero, and it means nothing. What a user
needs to know is the error on a point the fit has *not* seen, which is what
leave-one-out estimates — and which cannot be estimated at all from a single
measurement, so with one point this module says so instead of printing 0%.

What each additional measurement buys
-------------------------------------
======  =========================================================
points  what becomes possible
======  =========================================================
1       the absolute scale (Kp). No error estimate is possible.
2-3     a first cross-validated error; the P*V exponent if P or V
        was varied.
4+      a usable cross-validated error, and a test of whether the
        rate really is proportional to P*V on this tool.
======  =========================================================

The P*V exponent matters beyond bookkeeping. Preston's law says removal is
proportional to pressure times velocity, i.e. an exponent of exactly 1. Fitting
it instead of assuming it is how the model detects that a process has left
Preston's validity range — the same effect that makes the published copper
dataset in this repo unfittable, where the rate *falls* with speed at low
pressure.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Sequence, Tuple

#: Below this many points, a cross-validated error cannot be formed at all.
MIN_POINTS_FOR_CV = 2
#: Below this, treat the cross-validated error as indicative only.
MIN_POINTS_FOR_RELIABLE_CV = 4
#: Fitted P*V exponents outside this band contradict Preston's law.
PRESTON_EXPONENT_BAND = (0.75, 1.25)
#: Relative spread in P*V needed before an exponent can be identified at all.
MIN_PV_SPREAD = 0.25

PSI_TO_PA = 6894.757


@dataclass
class Measurement:
    """One measured removal rate and the conditions it was measured at."""
    rate_a_per_min: float
    pressure_psi: float
    rpm_platen: float
    rpm_head: Optional[float] = None
    label: str = ""
    #: slurry state during this run, for fitting the chemistry/abrasive factors
    abrasive_wt_pct: Optional[float] = None
    abrasive_d50_nm: Optional[float] = None
    oxidizer_wt_pct: Optional[float] = None
    ph: Optional[float] = None
    temperature_c: Optional[float] = None

    @property
    def pressure_pa(self) -> float:
        return float(self.pressure_psi) * PSI_TO_PA

    def velocity_m_s(self, center_offset_m: float) -> float:
        """Relative speed of the sweep.

        With head and platen co-rotating the relative velocity is uniform across
        the wafer and equal to omega times the centre-to-centre offset, which is
        the quantity Preston's law is written against.
        """
        rpm = self.rpm_platen if self.rpm_head is None else self.rpm_head
        return 2.0 * math.pi * float(rpm) / 60.0 * float(center_offset_m)

    def pv(self, center_offset_m: float) -> float:
        return self.pressure_pa * self.velocity_m_s(center_offset_m)


@dataclass
class Calibration:
    """The result of fitting to owner measurements."""
    n_points: int
    kp_m_per_pa: Optional[float] = None
    pv_exponent: Optional[float] = None
    in_sample_mape: Optional[float] = None
    cv_mape: Optional[float] = None
    notes: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    next_experiment: Optional[str] = None
    residuals: List[Dict[str, Any]] = field(default_factory=list)

    def as_dict(self) -> Dict[str, Any]:
        return {
            "n_points": self.n_points,
            "kp_m_per_pa": self.kp_m_per_pa,
            "pv_exponent": (None if self.pv_exponent is None
                            else round(self.pv_exponent, 3)),
            "in_sample_mape_percent": (None if self.in_sample_mape is None
                                       else round(self.in_sample_mape, 2)),
            "cross_validated_mape_percent": (None if self.cv_mape is None
                                             else round(self.cv_mape, 2)),
            "accuracy_to_quote": (
                None if self.cv_mape is None
                else f"+/-{self.cv_mape:.0f}% (leave-one-out, not in-sample)"),
            "next_experiment": self.next_experiment,
            "residuals": self.residuals,
            "notes": self.notes,
            "warnings": self.warnings,
        }


def _fit_kp(points: Sequence[Tuple[float, float]]) -> float:
    """Least-squares Kp for rate = Kp * pv, through the origin."""
    num = sum(pv * rate for pv, rate in points)
    den = sum(pv * pv for pv, _ in points)
    if den <= 0:
        raise ValueError("every measurement has zero pressure or zero speed")
    return num / den


def _mape(pairs: Sequence[Tuple[float, float]]) -> float:
    """Mean absolute percentage error over (predicted, actual)."""
    vals = [abs(p - a) / abs(a) for p, a in pairs if a]
    return 100.0 * sum(vals) / len(vals) if vals else float("nan")


def _fit_power(points: Sequence[Tuple[float, float]]) -> Tuple[float, float]:
    """Fit rate = c * pv**n by least squares in log space."""
    xs = [math.log(pv) for pv, _ in points]
    ys = [math.log(rate) for _, rate in points]
    n = len(xs)
    mx, my = sum(xs) / n, sum(ys) / n
    sxx = sum((x - mx) ** 2 for x in xs)
    if sxx <= 0:
        raise ValueError("no spread in P*V")
    sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    slope = sxy / sxx
    return math.exp(my - slope * mx), slope


def calibrate(measurements: Sequence[Measurement],
              center_offset_m: float = 0.20) -> Calibration:
    """Fit Kp (and, if the data allow, the P*V exponent) to measurements."""
    pts = [(m.pv(center_offset_m), float(m.rate_a_per_min)) for m in measurements]
    pts = [(pv, r) for pv, r in pts if pv > 0 and r > 0]
    cal = Calibration(n_points=len(pts))

    if not pts:
        cal.warnings.append(
            "no usable measurements: each needs a positive rate, pressure and speed")
        cal.next_experiment = (
            "one polish at your normal pressure and speed, with the measured "
            "removal rate, is enough to set the absolute scale")
        return cal

    # ── scale ────────────────────────────────────────────────────────
    kp_a_per_min = _fit_kp(pts)
    # rate is in A/min; Kp in the model is m/s per Pa*(m/s).
    cal.kp_m_per_pa = kp_a_per_min * 1e-10 / 60.0
    cal.in_sample_mape = _mape([(kp_a_per_min * pv, r) for pv, r in pts])
    cal.notes.append(
        f"Kp = {cal.kp_m_per_pa:.3e} m/Pa fitted to {len(pts)} measurement(s) "
        f"by least squares through the origin")

    for m, (pv, rate) in zip(measurements, pts):
        pred = kp_a_per_min * pv
        cal.residuals.append({
            "label": m.label or f"{m.pressure_psi:g} psi / {m.rpm_platen:g} rpm",
            "measured_A_per_min": round(rate, 1),
            "predicted_A_per_min": round(pred, 1),
            "error_percent": round(100.0 * (pred - rate) / rate, 1),
        })

    # ── honest accuracy ──────────────────────────────────────────────
    if len(pts) < MIN_POINTS_FOR_CV:
        cal.warnings.append(
            "with a single measurement the fit passes exactly through it, so "
            "its in-sample error is 0% by construction and means nothing. No "
            "accuracy can be quoted until there is a second point")
        cal.in_sample_mape = None
    else:
        errs = []
        for i in range(len(pts)):
            rest = pts[:i] + pts[i + 1:]
            kp_i = _fit_kp(rest)
            pv_i, actual = pts[i]
            errs.append(abs(kp_i * pv_i - actual) / actual)
        cal.cv_mape = 100.0 * sum(errs) / len(errs)
        cal.notes.append(
            f"leave-one-out cross-validated error {cal.cv_mape:.1f}% — each "
            "point predicted by a fit that never saw it. Quote this, not the "
            f"in-sample {cal.in_sample_mape:.1f}%")
        if len(pts) < MIN_POINTS_FOR_RELIABLE_CV:
            cal.warnings.append(
                f"the cross-validated error rests on only {len(pts)} points, so "
                "treat it as indicative; it will move substantially with the "
                "next measurement")

    # ── does Preston's law actually hold on this tool? ───────────────
    pv_values = [pv for pv, _ in pts]
    spread = (max(pv_values) - min(pv_values)) / max(pv_values)
    if len(pts) >= 3 and spread >= MIN_PV_SPREAD:
        try:
            _c, exponent = _fit_power(pts)
        except ValueError:
            exponent = None
        if exponent is not None:
            cal.pv_exponent = exponent
            lo, hi = PRESTON_EXPONENT_BAND
            if lo <= exponent <= hi:
                cal.notes.append(
                    f"the fitted P*V exponent is {exponent:.2f}, consistent with "
                    "Preston's law (exponent 1), so the linear form is "
                    "supported by your own data")
            else:
                cal.warnings.append(
                    f"your data give a P*V exponent of {exponent:.2f}, not the "
                    "1.0 Preston's law requires. A single Kp cannot describe "
                    "this process: something is changing with load or speed - "
                    "check the lubrication and pad-load regimes reported for "
                    "these conditions before using the fitted Kp to extrapolate")
    elif len(pts) >= 3:
        cal.notes.append(
            f"P*V spans only {100 * spread:.0f}% of its maximum, too narrow to "
            "identify the exponent; vary pressure or speed to test Preston's law")

    # ── what to measure next ─────────────────────────────────────────
    if len(pts) == 1:
        cal.next_experiment = (
            "a second point at roughly double or half the pressure. That gives "
            "the first real error estimate and starts to test whether rate is "
            "proportional to P*V on your tool")
    elif len(pts) < MIN_POINTS_FOR_RELIABLE_CV:
        cal.next_experiment = (
            f"{MIN_POINTS_FOR_RELIABLE_CV - len(pts)} more point(s), spread "
            "across pressure and speed rather than repeated at one condition - "
            "repeats measure your tool's noise, spread measures the model")
    elif spread < MIN_PV_SPREAD:
        cal.next_experiment = (
            "a point at a clearly different pressure or speed: the current set "
            "is too clustered to test the P*V law")
    else:
        cal.next_experiment = (
            "vary the slurry rather than the tool from here - concentration or "
            "pH - since the P*V behaviour is now pinned")
    return cal


def from_dicts(raw: Sequence[Dict[str, Any]]) -> List[Measurement]:
    """Build measurements from a YAML/JSON ``measurements:`` block."""
    out: List[Measurement] = []
    for i, d in enumerate(raw or []):
        d = dict(d or {})
        rate = d.get("rate_A_per_min", d.get("rate_a_per_min"))
        if rate is None and d.get("rate_nm_per_min") is not None:
            rate = float(d["rate_nm_per_min"]) * 10.0
        missing = [k for k, v in (("rate", rate),
                                  ("pressure_psi", d.get("pressure_psi")),
                                  ("rpm_platen", d.get("rpm_platen"))) if v is None]
        if missing:
            raise ValueError(
                f"measurement {i + 1} is missing {', '.join(missing)}. Each needs "
                "a rate (rate_A_per_min or rate_nm_per_min) plus the "
                "pressure_psi and rpm_platen it was measured at - a rate without "
                "its conditions cannot calibrate anything")
        def _opt(key):
            v = d.get(key)
            return None if v is None else float(v)

        out.append(Measurement(
            rate_a_per_min=float(rate),
            pressure_psi=float(d["pressure_psi"]),
            rpm_platen=float(d["rpm_platen"]),
            rpm_head=(None if d.get("rpm_head") is None else float(d["rpm_head"])),
            label=str(d.get("label", "")),
            abrasive_wt_pct=_opt("abrasive_wt_pct"),
            abrasive_d50_nm=_opt("abrasive_d50_nm"),
            oxidizer_wt_pct=_opt("oxidizer_wt_pct"),
            ph=_opt("ph"),
            temperature_c=_opt("temperature_c"),
        ))
    return out
