"""Threshold-Preston removal for a PASSIVATING metal film (P4/P1 coupling).

Derivation
----------
Tungsten in Fe(III)/H2O2 removes by the Kaufman cycle (Kaufman et al.,
J. Electrochem. Soc. 138 (1991) 3460): the oxidiser grows a passivating WOx
layer, and NO metal leaves until the abrasive has sheared that layer off. A
layer with a finite shear strength is a YIELD problem, so the asperity must
carry more than a critical load before it removes anything. Integrating
Preston's proportionality over the contact area with that yield condition gives
the threshold form

    RR = K * V * max(P - P0, 0)                                          (1)

which is Preston's law with an offset, not a new free shape: at P >> P0 it is
indistinguishable from RR = K*P*V, and the whole effect lives at low pressure,
where W CMP actually runs.

What sets P0
------------
An etch inhibitor adsorbs on the WOx and stiffens it, so the pressure needed to
shear the layer scales with the inhibitor's surface COVERAGE, not its bulk
concentration. Langmuir adsorption on a fixed site density gives

    P0 = P_y * theta,     theta = K_L*C / (1 + K_L*C)                    (2)

with P_y the threshold at full coverage (a mechanical property of the saturated
passivation layer) and K_L the adsorption constant. Two constants total.

Why this is a constant-REDUCING change
--------------------------------------
Before this term, `w_fe_oxidizer` was SILENT on `inhibitor_ppm`: six patented
compositions that differ only in inhibitor loading collapsed onto one predicted
curve, and the resulting curvature had to be absorbed by a per-pack pressure
exponent (n ~ 2.15 fitted globally, a third constant that is pure curve-fitting
with no mechanism). Eq. (1)-(2) removes the need for any pressure exponent on W
AND makes the inhibitor axis live, for a net change of +2 constants / -1
constant, with a mechanism attached to each.

Measured support, and the falsification that shaped it
-----------------------------------------------------
`tools/w_passivation_threshold_probe.py` on EP3161098B1 Table 5B (18 points, 6
compositions x 3 pressures):

    model                                shape MAPE   free constants
    pure Preston (P^1)                       46.1%          0
    best single fitted exponent P^n          26.9%          1  (n = 2.15)
    threshold, Eq.(1)+(2)                    12.4%          2

The probe ALSO reports a partial falsification that is kept rather than hidden:
fitting P0 SEPARATELY per composition does NOT come out monotone in inhibitor
(0.52 / 1.19 / 1.08 psi at 37 / 50 / 63 ppm), i.e. the 50 and 63 ppm groups are
within each other's scatter. That is consistent with Eq.(2) SATURATING - at the
fitted K_L the coverage only moves 0.17 -> 0.26 over that range, so the top two
levels are predicted to be nearly equal - but it means the data constrain the
ONSET of coverage, not its plateau. P_y is therefore an extrapolated quantity
and is flagged as such in the pack. The inhibitor axis dominates the Fe axis in
P0 by 7.7x, which is what Eq.(2) requires (Fe catalyses the oxidation, it does
not set the layer's shear strength).

Declined here, on purpose: Fenton kinetics is first order in the Fe(III)
catalyst, so a factor (C_Fe / C_Fe,ref) improves the same fit to 11.5% with no
new SHAPE constant - but it needs a reference concentration, and this pack's Kp
was anchored on a DIFFERENT patent (US2011/0186542A1) that never states its Fe
loading. Writing a reference would be inventing the number that makes the term
work, so the Fe axis stays silent and the finding is recorded instead.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass
class ThresholdResult:
    factor: float
    notes: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    terms: Dict[str, Any] = field(default_factory=dict)


def langmuir_coverage(conc: float, k_l: float) -> float:
    """theta = K_L*C / (1 + K_L*C). Dimensionless, 0..1."""
    if conc <= 0.0 or k_l <= 0.0:
        return 0.0
    return (k_l * conc) / (1.0 + k_l * conc)


def threshold_pressure_psi(inhibitor_ppm: float, yield_psi: float,
                           k_l_per_ppm: float) -> float:
    """P0 = P_y * theta(C_inh)  — Eq. (2) of this module's derivation."""
    return yield_psi * langmuir_coverage(inhibitor_ppm, k_l_per_ppm)


def passivation_threshold_factor(pressure_psi: float, inhibitor_ppm: float,
                                 yield_psi: float,
                                 k_l_per_ppm: float) -> ThresholdResult:
    """Multiplier turning ``Kp*P*V`` into ``K*V*(P - P0)``.

    Returned as a RATIO (P - P0)/P so it composes with the existing Preston
    chain instead of replacing it — the pack's Kp keeps its meaning at
    P >> P0, where the threshold vanishes.
    """
    if pressure_psi <= 0.0:
        return ThresholdResult(factor=1.0)
    p0 = threshold_pressure_psi(inhibitor_ppm, yield_psi, k_l_per_ppm)
    terms = {"threshold_pressure_psi": p0,
             "inhibitor_coverage": langmuir_coverage(inhibitor_ppm,
                                                     k_l_per_ppm)}
    notes = [
        f"passivation threshold P0 = {p0:.3f} psi from Langmuir inhibitor "
        f"coverage {terms['inhibitor_coverage']:.3f} at "
        f"{inhibitor_ppm:.0f} ppm (Kaufman 1991 shear-off cycle; "
        f"cmp_sim/models/passivation_threshold.py)"
    ]
    warnings: List[str] = []
    if pressure_psi <= p0:
        # Below threshold the model says NOTHING is removed. That is a real
        # prediction, but reporting zero silently would look like a crash, and
        # extrapolating (1) below its data is exactly the trap this repo has
        # paid for before, so the floor is explicit and loud.
        warnings.append(
            f"down force {pressure_psi:.2f} psi is at or below the "
            f"passivation shear threshold {p0:.3f} psi — the model predicts "
            f"removal is suppressed, and this is EXTRAPOLATION below the "
            f"1.5-3.0 psi band the threshold was measured in")
        return ThresholdResult(factor=1e-6, notes=notes, warnings=warnings,
                               terms=terms)
    factor = (pressure_psi - p0) / pressure_psi
    return ThresholdResult(factor=factor, notes=notes, warnings=warnings,
                           terms=terms)
