"""Reject impossible recipes at the door, with a message a user can act on.

Without this, bad input reaches the solver and surfaces as whatever the inner
numerics happen to raise. Observed before this existed: a negative pressure
produced ``RuntimeError: brackets failed: f(d_lo)=8.424e+01`` — in Korean,
from an inherited module — which tells the user nothing about what they typed.

Two distinct jobs, kept separate:

**Errors** are values that cannot describe a real process (a negative pressure,
a pattern density above 1). These are rejected.

**Warnings** are values that are physically possible but outside the range any
of the underlying models was fitted in (25 psi, 0 rpm). These run, and say so.
Refusing them would hide the fact that the model still produces a number there.
"""
from __future__ import annotations

import math
from typing import List, Tuple

from cmp_sim.core.state import Recipe

#: Ranges the constituent models were actually fitted across. Outside these the
#: simulator still answers, but the answer is an extrapolation.
TYPICAL_PRESSURE_PSI = (0.5, 10.0)
TYPICAL_RPM = (10.0, 300.0)
TYPICAL_FLOW_ML_MIN = (50.0, 500.0)
TYPICAL_TEMP_C = (15.0, 80.0)


def check(recipe: Recipe) -> Tuple[List[str], List[str]]:
    """Return (errors, warnings) for a recipe. Errors make it unrunnable."""
    errors: List[str] = []
    warnings: List[str] = []
    t, w, s, p, d = (recipe.tool, recipe.wafer, recipe.slurry,
                     recipe.pad, recipe.disk)

    # ── is it even a number? ─────────────────────────────────────────
    # Every check below compares against zero, which raises an opaque
    # TypeError on a string and silently succeeds on NaN (all comparisons
    # with NaN are False, so a NaN pressure passed straight through to the
    # contact solver and surfaced as "The function value at x=... is NaN").
    # Both are caught here, where the message can name the field.
    numeric_fields = (
        ("tool.pressure_psi", getattr(t, "pressure_psi", None)),
        ("tool.rpm_platen", getattr(t, "rpm_platen", None)),
        ("tool.rpm_head", getattr(t, "rpm_head", None)),
        ("tool.time_s", getattr(t, "time_s", None)),
        ("tool.flow_ml_min", getattr(t, "flow_ml_min", None)),
        ("tool.center_offset_m", getattr(t, "center_offset_m", None)),
        ("slurry.ph", getattr(s, "ph", None)),
        ("wafer.n_radial", getattr(w, "n_radial", None)),
        ("wafer.diameter_mm", getattr(w, "diameter_mm", None)),
        ("wafer.pattern_density", getattr(w, "pattern_density", None)),
        ("pad.use_hours", getattr(p, "use_hours", None)),
        ("disk.hours_used", getattr(d, "hours_used", None)),
    )
    for label, value in numeric_fields:
        if value is None or isinstance(value, bool):
            continue
        if not isinstance(value, (int, float)):
            errors.append(
                f"{label} must be a number, got {type(value).__name__} "
                f"{value!r}. A quantity given as text cannot be compared or "
                "multiplied, and letting it through produces an error deep in "
                "the solver that does not name the field.")
        elif math.isnan(value):
            errors.append(
                f"{label} is NaN. Every comparison with NaN is false, so this "
                "would pass all the range checks below and then surface as an "
                "unintelligible failure inside the contact solver.")
        elif math.isinf(value):
            errors.append(
                f"{label} is infinite ({value}). No physical quantity here can "
                "be unbounded.")
    if errors:
        # Nothing further can be trusted once a field is not a finite number.
        return errors, warnings

    # ── impossible ───────────────────────────────────────────────────
    if t.pressure_psi is None or t.pressure_psi <= 0:
        errors.append(
            f"pressure must be greater than zero, got {t.pressure_psi} psi. "
            "A CMP process with no down force removes nothing")
    if t.time_s is not None and t.time_s <= 0:
        errors.append(f"polish time must be greater than zero, got {t.time_s} s")
    if t.flow_ml_min is not None and t.flow_ml_min < 0:
        errors.append(f"slurry flow cannot be negative, got {t.flow_ml_min} ml/min")
    for name, rpm in (("rpm_platen", t.rpm_platen), ("rpm_head", t.rpm_head)):
        if rpm is not None and rpm < 0:
            errors.append(f"{name} cannot be negative, got {rpm}")
    if w.pattern_density is not None and not 0.0 < w.pattern_density <= 1.0:
        errors.append(
            f"pattern density is a fraction of die area, so it must lie in "
            f"(0, 1]; got {w.pattern_density}")
    if w.diameter_mm is not None and w.diameter_mm <= 0:
        errors.append(f"wafer diameter must be positive, got {w.diameter_mm} mm")
    if w.n_radial is not None and w.n_radial < 2:
        errors.append(f"n_radial must be at least 2, got {w.n_radial}")
    if s.ph is not None and not 0.0 <= s.ph <= 14.0:
        errors.append(f"pH must lie between 0 and 14, got {s.ph}")
    if p.use_hours is not None and p.use_hours < 0:
        errors.append(f"pad use hours cannot be negative, got {p.use_hours}")
    if d.hours_used is not None and d.hours_used < 0:
        errors.append(f"conditioner hours cannot be negative, got {d.hours_used}")
    if s.abrasive is not None:
        if s.abrasive.conc_wt_pct is not None and s.abrasive.conc_wt_pct < 0:
            errors.append("abrasive concentration cannot be negative")
        if s.abrasive.d50_nm is not None and s.abrasive.d50_nm <= 0:
            errors.append("abrasive d50 must be positive")
        if (s.abrasive.d99_nm is not None and s.abrasive.d50_nm is not None
                and s.abrasive.d99_nm < s.abrasive.d50_nm):
            errors.append(
                f"d99 ({s.abrasive.d99_nm} nm) is smaller than d50 "
                f"({s.abrasive.d50_nm} nm); the 99th percentile cannot be below "
                "the median")

    # ── possible, but outside where the models were fitted ───────────
    lo, hi = TYPICAL_PRESSURE_PSI
    if t.pressure_psi and not lo <= t.pressure_psi <= hi:
        warnings.append(
            f"{t.pressure_psi} psi is outside the {lo}-{hi} psi range the "
            "underlying correlations were fitted across; the result is an "
            "extrapolation")
    lo, hi = TYPICAL_RPM
    for name, rpm in (("platen", t.rpm_platen), ("head", t.rpm_head)):
        if rpm is not None and not lo <= rpm <= hi:
            warnings.append(
                f"{name} speed {rpm} rpm is outside the fitted {lo:g}-{hi:g} rpm "
                "range; the result is an extrapolation")
    if t.rpm_platen == 0 and t.rpm_head == 0:
        warnings.append(
            "both platen and head are stationary, so the relative velocity is "
            "zero almost everywhere. Any removal shown comes from terms that do "
            "not vanish with velocity and should not be trusted")
    lo, hi = TYPICAL_FLOW_ML_MIN
    if t.flow_ml_min is not None and t.flow_ml_min < lo:
        warnings.append(
            f"{t.flow_ml_min} ml/min is below the {lo:g} ml/min minimum of the "
            "fitted range; slurry starvation dominates here")
    lo, hi = TYPICAL_TEMP_C
    if s.temperature_c is not None and not lo <= s.temperature_c <= hi:
        warnings.append(
            f"{s.temperature_c} C is outside the fitted {lo:g}-{hi:g} C range")
    return errors, warnings


class RecipeInvalid(ValueError):
    """A recipe that cannot describe a real process."""

    def __init__(self, errors: List[str]):
        self.errors = errors
        super().__init__(
            "this recipe cannot describe a real process:\n  - "
            + "\n  - ".join(errors))


def validate(recipe: Recipe) -> List[str]:
    """Raise on impossible input; return warnings for out-of-range input."""
    errors, warnings = check(recipe)
    if errors:
        raise RecipeInvalid(errors)
    return warnings
