"""Fit the model's physical factors to data — but only the ones the data can see.

Why factors rather than a fresh model each time
-----------------------------------------------
Given a table of measurements one could regress a new expression every time. Three
reasons not to, all of them already demonstrated inside this repository:

**Identifiability.** The Kaufman oxidizer curve has two free parameters, a peak
position and a shape exponent, which are mathematically degenerate when only
sub-peak data exist — no amount of data in that region can separate them. This
is why the copper pack uses a one-parameter Langmuir form instead. Re-deriving a
model per dataset walks into that trap repeatedly; fitting *named factors* makes
the degeneracy explicit and refusable.

**Extrapolation.** A black-box regression collapses outside the measured box. A
fitted physical factor keeps the structure: doubling pressure still doubles rate,
because that is the form, not something learned from data.

**Convergence on few points.** Every free parameter costs data. One measurement
already moves Kp from -56.7% to -0.8%; a ten-parameter surface fitted to ten
points reproduces the points and predicts nothing.

The overfitting risk, handled
-----------------------------
More factors always fit the training data better. So a factor is only unlocked
when the data can actually identify it, tested three ways:

1. **Leverage** — the input must vary across the dataset. Fitting an abrasive
   exponent to runs at one concentration is fitting noise.
2. **Budget** — at least ``POINTS_PER_FACTOR`` measurements per free parameter,
   Kp included.
3. **Earning its place** — the factor is kept only if it improves the
   *cross-validated* error, never the in-sample error. A parameter that helps in
   sample and hurts out of sample is overfitting, and is rejected with that
   stated.

The result is a fit that grows with the dataset: one point sets the scale, a
pressure sweep unlocks the pressure exponent, an abrasive series unlocks the
abrasive terms, and anything the data cannot see stays at its literature value
with a note saying why.
"""
from __future__ import annotations

import itertools
import math
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Sequence, Tuple

from cmp_sim.core.calibration import Measurement

#: Measurements required per free parameter before it may be unlocked.
POINTS_PER_FACTOR = 3
#: Relative spread an input needs before a factor depending on it is fittable.
MIN_LEVERAGE = 0.15
#: A factor must improve cross-validated error by at least this fraction.
#: Set from a noise study rather than by taste: with 8% measurement scatter on
#: data that genuinely obeys Preston's law, a 2% threshold admitted a spurious
#: pressure exponent in 2 runs out of 5. A real departure (true exponent 0.65)
#: cuts the error by 60-70%, so a 25% floor keeps every true signal while
#: rejecting noise-chasing. Better to miss a marginal factor than to report one
#: that is not there.
MIN_CV_GAIN = 0.25


@dataclass
class Factor:
    """One physically-named, fittable quantity."""
    name: str
    param_key: str
    description: str
    #: which measurement attribute must vary for this to be identifiable
    driver: str
    default: float
    bounds: Tuple[float, float]
    #: multiplier applied to the rate, given the factor value and a measurement
    apply: Callable[[float, Measurement, Dict[str, float]], float]

    def leverage(self, ms: Sequence[Measurement], ctx: Dict[str, Any]) -> float:
        vals = [_driver_value(self.driver, m, ctx) for m in ms]
        vals = [v for v in vals if v is not None and v > 0]
        if len(vals) < 2:
            return 0.0
        return (max(vals) - min(vals)) / max(vals)


def _driver_value(driver: str, m: Measurement, ctx: Dict[str, Any]) -> Optional[float]:
    if driver == "pressure":
        return m.pressure_psi
    if driver == "velocity":
        return m.velocity_m_s(ctx.get("center_offset_m", 0.20))
    if driver == "pv":
        return m.pv(ctx.get("center_offset_m", 0.20))
    return getattr(m, driver, None)


# ── the factor library ───────────────────────────────────────────────
def _pressure_exponent(value: float, m: Measurement, ctx: Dict[str, float]) -> float:
    """MRR ~ P^n. Preston says n = 1; contact mechanics predicts departures."""
    ref = ctx.get("pressure_ref_psi") or 3.0
    return (m.pressure_psi / ref) ** (value - 1.0)


def _velocity_exponent(value: float, m: Measurement, ctx: Dict[str, float]) -> float:
    """MRR ~ V^n. n < 1 indicates a transport or lubrication limit."""
    ref = ctx.get("velocity_ref_m_s") or 1.0
    v = m.velocity_m_s(ctx.get("center_offset_m", 0.20))
    return (v / ref) ** (value - 1.0) if v > 0 else 1.0


FACTORS: Tuple[Factor, ...] = (
    Factor(
        name="pressure_exponent",
        param_key="pressure_exponent",
        description="exponent on pressure; Preston requires exactly 1. Below 1 "
                    "suggests the real contact area is saturating, above 1 that "
                    "higher load is recruiting new contacts or changing the "
                    "removal mechanism",
        driver="pressure",
        default=1.0,
        bounds=(0.4, 1.8),
        apply=_pressure_exponent,
    ),
    Factor(
        name="velocity_exponent",
        param_key="velocity_exponent",
        description="exponent on velocity; Preston requires exactly 1. Below 1 "
                    "is the signature of a transport limit - slurry refresh or "
                    "a thickening lubricating film - rather than of mechanics",
        driver="velocity",
        default=1.0,
        bounds=(0.2, 1.6),
        apply=_velocity_exponent,
    ),
)

FACTORS_BY_NAME = {f.name: f for f in FACTORS}


@dataclass
class FactorFit:
    """The outcome of fitting factors to a dataset."""
    kp_m_per_pa: Optional[float] = None
    values: Dict[str, float] = field(default_factory=dict)
    unlocked: List[str] = field(default_factory=list)
    locked: Dict[str, str] = field(default_factory=dict)
    rejected: Dict[str, str] = field(default_factory=dict)
    cv_mape: Optional[float] = None
    baseline_cv_mape: Optional[float] = None
    n_points: int = 0
    notes: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    def as_dict(self) -> Dict[str, Any]:
        return {
            "n_points": self.n_points,
            "kp_m_per_pa": self.kp_m_per_pa,
            "fitted_factors": {k: round(v, 4) for k, v in self.values.items()},
            "unlocked": self.unlocked,
            "locked": self.locked,
            "rejected": self.rejected,
            "cross_validated_mape_percent": (
                None if self.cv_mape is None else round(self.cv_mape, 2)),
            "baseline_cross_validated_mape_percent": (
                None if self.baseline_cv_mape is None
                else round(self.baseline_cv_mape, 2)),
            "improvement_percent_points": (
                None if (self.cv_mape is None or self.baseline_cv_mape is None)
                else round(self.baseline_cv_mape - self.cv_mape, 2)),
            "notes": self.notes,
            "warnings": self.warnings,
        }


def _predict(kp: float, m: Measurement, active: Dict[str, float],
             ctx: Dict[str, Any]) -> float:
    """Rate in A/min for one measurement under a factor set."""
    rate = kp * m.pv(ctx.get("center_offset_m", 0.20))
    for name, value in active.items():
        rate *= FACTORS_BY_NAME[name].apply(value, m, ctx)
    return rate


def _fit_kp(ms: Sequence[Measurement], active: Dict[str, float],
            ctx: Dict[str, Any]) -> float:
    """Closed-form least-squares scale, given the factor values."""
    num = den = 0.0
    for m in ms:
        shape = _predict(1.0, m, active, ctx)
        num += shape * m.rate_a_per_min
        den += shape * shape
    if den <= 0:
        raise ValueError("no usable measurements")
    return num / den


def _mape(ms: Sequence[Measurement], kp: float, active: Dict[str, float],
          ctx: Dict[str, Any]) -> float:
    errs = [abs(_predict(kp, m, active, ctx) - m.rate_a_per_min) / m.rate_a_per_min
            for m in ms if m.rate_a_per_min]
    return 100.0 * sum(errs) / len(errs) if errs else float("nan")


def _grid_search(ms: Sequence[Measurement], names: Sequence[str],
                 ctx: Dict[str, Any], steps: int = 21) -> Dict[str, float]:
    """Coarse-to-fine grid over the named factors, minimising in-sample error.

    A grid rather than a gradient method: two or three bounded parameters make
    it cheap, and it cannot fall into a local minimum or fail to converge, which
    matters more here than speed.
    """
    grids = {n: [FACTORS_BY_NAME[n].bounds[0]
                 + (FACTORS_BY_NAME[n].bounds[1] - FACTORS_BY_NAME[n].bounds[0])
                 * i / (steps - 1) for i in range(steps)] for n in names}
    best: Dict[str, float] = {n: FACTORS_BY_NAME[n].default for n in names}
    for _round in range(2):
        for combo in itertools.product(*(grids[n] for n in names)):
            trial = dict(zip(names, combo))
            try:
                kp = _fit_kp(ms, trial, ctx)
            except ValueError:
                continue
            err = _mape(ms, kp, trial, ctx)
            if not math.isfinite(err):
                continue
            if err < _mape(ms, _fit_kp(ms, best, ctx), best, ctx):
                best = trial
        # refine around the winner
        for n in names:
            lo, hi = FACTORS_BY_NAME[n].bounds
            span = (hi - lo) / (steps - 1) * 2
            centre = best[n]
            grids[n] = [max(lo, min(hi, centre - span + 2 * span * i / (steps - 1)))
                        for i in range(steps)]
    return best


def _cv_mape(ms: Sequence[Measurement], names: Sequence[str],
             ctx: Dict[str, Any]) -> Optional[float]:
    """Leave-one-out error for a factor set, refitting everything each fold."""
    if len(ms) < 2:
        return None
    errs = []
    for i in range(len(ms)):
        train = list(ms[:i]) + list(ms[i + 1:])
        if len(train) < 2:
            return None
        try:
            values = _grid_search(train, names, ctx) if names else {}
            kp = _fit_kp(train, values, ctx)
        except ValueError:
            return None
        held = ms[i]
        pred = _predict(kp, held, values, ctx)
        errs.append(abs(pred - held.rate_a_per_min) / held.rate_a_per_min)
    return 100.0 * sum(errs) / len(errs)


def fit_factors(measurements: Sequence[Measurement],
                center_offset_m: float = 0.20,
                pressure_ref_psi: float = 3.0) -> FactorFit:
    """Fit Kp plus whichever factors the data can actually identify."""
    ms = [m for m in measurements if m.rate_a_per_min > 0 and m.pressure_psi > 0]
    fit = FactorFit(n_points=len(ms))
    if not ms:
        fit.warnings.append("no usable measurements")
        return fit

    ctx: Dict[str, Any] = {
        "center_offset_m": center_offset_m,
        "pressure_ref_psi": pressure_ref_psi,
        "velocity_ref_m_s": sum(m.velocity_m_s(center_offset_m) for m in ms) / len(ms),
    }

    # ── baseline: scale only ─────────────────────────────────────────
    fit.kp_m_per_pa = _fit_kp(ms, {}, ctx) * 1e-10 / 60.0
    fit.baseline_cv_mape = _cv_mape(ms, [], ctx)
    fit.cv_mape = fit.baseline_cv_mape
    fit.notes.append(
        f"scale (Kp) fitted to {len(ms)} measurement(s); every other factor "
        "starts at its literature value")

    # ── which factors may even be attempted? ─────────────────────────
    budget = max(0, len(ms) // POINTS_PER_FACTOR - 1)
    candidates: List[str] = []
    for f in FACTORS:
        lev = f.leverage(ms, ctx)
        if lev < MIN_LEVERAGE:
            fit.locked[f.name] = (
                f"{f.driver} varies by only {lev:.0%} across these runs "
                f"(need {MIN_LEVERAGE:.0%}): the data cannot separate this "
                f"factor from the overall scale, so it stays at "
                f"{f.default:g}")
        else:
            candidates.append(f.name)

    if not candidates:
        fit.warnings.append(
            "no factor beyond the overall scale is identifiable from this "
            "dataset. Vary pressure or speed between runs to unlock them")
        return fit

    if budget < 1:
        for name in candidates:
            fit.locked[name] = (
                f"only {len(ms)} measurement(s): {POINTS_PER_FACTOR} per free "
                f"parameter are required before this may be fitted, or it will "
                f"absorb noise")
        fit.warnings.append(
            f"{len(ms)} measurements support the scale alone. "
            f"{POINTS_PER_FACTOR * 2} would unlock the first physical factor")
        return fit

    # ── unlock greedily, and only if cross-validation improves ───────
    active: List[str] = []
    for name in sorted(candidates,
                       key=lambda n: -FACTORS_BY_NAME[n].leverage(ms, ctx)):
        if len(active) >= budget:
            fit.locked[name] = (
                f"the measurement budget allows {budget} free factor(s) beyond "
                f"the scale; this one was not among the highest-leverage")
            continue
        trial = active + [name]
        cv = _cv_mape(ms, trial, ctx)
        if cv is None:
            fit.locked[name] = "too few points to cross-validate this factor"
            continue
        current = fit.cv_mape if fit.cv_mape is not None else float("inf")
        if cv < current * (1.0 - MIN_CV_GAIN):
            active = trial
            fit.cv_mape = cv
            fit.notes.append(
                f"unlocked '{name}': cross-validated error {current:.1f}% -> "
                f"{cv:.1f}%")
        else:
            fit.rejected[name] = (
                f"fitting it did not improve the cross-validated error "
                f"({current:.1f}% -> {cv:.1f}%), so it was rejected as "
                f"overfitting rather than kept for a better in-sample number")

    if active:
        values = _grid_search(ms, active, ctx)
        fit.values = values
        fit.kp_m_per_pa = _fit_kp(ms, values, ctx) * 1e-10 / 60.0
        fit.unlocked = active
        for name, value in values.items():
            f = FACTORS_BY_NAME[name]
            fit.notes.append(f"{name} = {value:.3f} ({f.description})")
            if abs(value - f.default) > 0.2:
                fit.warnings.append(
                    f"your data give {name} = {value:.2f}, not the "
                    f"{f.default:g} the standard form assumes. {f.description}")
    return fit
