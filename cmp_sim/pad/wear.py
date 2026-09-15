"""P7 — pad wear, glazing and conditioning drift.

A pad does not hold its removal rate. Two competing processes act on the
asperity population that P2 depends on:

* **glazing / wear** — polishing flattens summits. Contact points are lost and
  the survivors grow blunter, so the pad slowly stops cutting.
* **conditioning** — a diamond disk cuts fresh asperities back into the
  surface, restoring the population.

Their balance sets the steady state, and the drift between conditioning cycles
is what shows up as rate decay over pad life.

Measured behaviour (Jeong et al. 2024, *Materials* 17, 1817,
doi:10.3390/ma17081817, Table 1 and Eq. 4), wrapped from the inherited
`legacy/sim/tier2_physics/pad_glazing_jeong2024.py`:

    N(t)/N0   = exp(-t / tau(p))          contact count decays
    mu_R(t)   = (0.28 p + 0.621) t + 5.45 exp(0.18 p)   [um]   summits blunt

Note the direction. A naive GW argument says that thinning the asperity
population at fixed nominal pressure should *increase* the contact count; the
measurement says the opposite, and the measurement wins. The inherited module
records this contradiction rather than hiding it, and so does this wrapper.

The `relative_mrr_proxy` combines the two as `N(t)/N0 * mu_R(t)/mu_R(0)`,
approximating "force per contact" by the summit radius alone. That is a coarse
proxy: it contains no indentation depth and no effective modulus, and the
inherited self-test found its peak at ~7 min rather than the 3 min of the
measured MRR curve. It is therefore used for *trend direction only*, and the
code says so instead of implying a precision it does not have.

Conditioner ageing uses the inherited `conditioner_pcr_decay.py`, whose decay
constant is back-calculated from an Entegris field anchor (pad cut rate falls
to 16% of its initial value after 50 hours of disk use).
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from cmp_sim.core.legacy_bridge import install  # noqa: F401

import conditioner_pcr_decay as pcr      # legacy/sim/tier2_physics/
import pad_glazing_jeong2024 as glaze    # legacy/sim/tier2_physics/

NAME = "pad_wear"

#: pressures for which Jeong 2024 Table 1 has contact-count data
MEASURED_PRESSURES_PSI = (2, 3, 4, 5)

#: Entegris field anchor: disk cut rate falls to 16% after 50 h
DISK_AGING_TAU_HOURS = pcr.TAU_AGING_HOURS

#: longest polish time in Jeong 2024 Table 1 [min]. Beyond this the exponential
#: fit is an extrapolation, and it decays to absurdity fast: at 120 min it
#: predicts 0.01% of the initial contacts and a 185 um summit radius, which is
#: larger than the asperities themselves.
MEASURED_MAX_MINUTES = 10.0


def contact_decay_tau_min(pressure_psi: float) -> float:
    """Exponential decay constant of the contact count [min], from Table 1."""
    return float(glaze.contact_decay_tau_min(_nearest_measured(pressure_psi)))


def _nearest_measured(pressure_psi: float) -> int:
    """Snap to the nearest measured pressure; extrapolation is not invented."""
    return min(MEASURED_PRESSURES_PSI, key=lambda p: abs(p - float(pressure_psi)))


def contact_ratio(pressure_psi: float, minutes: float) -> float:
    """N(t)/N0 — surviving fraction of contact points."""
    return float(glaze.contact_ratio(_nearest_measured(pressure_psi), float(minutes)))


def mean_asperity_radius_um(pressure_psi: float, minutes: float) -> float:
    """Mean summit radius [um] (Jeong 2024 Eq. 4)."""
    return float(glaze.mean_asperity_radius_um(float(pressure_psi), float(minutes)))


def radius_growth_ratio(pressure_psi: float, minutes: float) -> float:
    return float(glaze.radius_growth_ratio(float(pressure_psi), float(minutes)))


def relative_mrr_proxy(pressure_psi: float, minutes: float) -> float:
    """Coarse MRR trend proxy — direction only, not a calibrated rate."""
    return float(glaze.relative_mrr_proxy(_nearest_measured(pressure_psi),
                                          float(minutes)))


def disk_cut_rate_ratio(hours_used: float) -> float:
    """Conditioner cut rate relative to a new disk, exponential ageing."""
    return float(pcr.pcr_decay(float(hours_used), 1.0, DISK_AGING_TAU_HOURS, 0.0))


def steady_state_contact_ratio(glazing_rate: float, conditioning_rate: float,
                               disk_effectiveness: float = 1.0) -> float:
    """Balance of asperity destruction and regeneration.

    Treating the asperity population `n` as gaining from conditioning and
    losing to glazing,

        dn/dt = k_c * G * (1 - n) - k_g * n

    where `G` is the disk's current effectiveness. At steady state

        n_ss = k_c G / (k_g + k_c G)

    so a worn disk (`G` small) lowers the plateau: the pad settles glazed.
    """
    kg, kc = float(glazing_rate), float(conditioning_rate) * float(disk_effectiveness)
    if kg < 0 or kc < 0:
        raise ValueError("rates must be non-negative")
    if kg + kc == 0:
        raise ValueError("at least one of glazing or conditioning must be active")
    return kc / (kg + kc)


@dataclass
class PadLifeState:
    polish_minutes: float
    contact_ratio: float
    asperity_radius_um: float
    radius_growth: float
    mrr_trend_proxy: float
    disk_hours: float
    disk_cut_rate_ratio: float
    steady_state_contact: Optional[float] = None
    notes: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    def as_dict(self) -> Dict[str, Any]:
        out = {
            "polish_minutes": round(self.polish_minutes, 2),
            "contact_count_ratio": round(self.contact_ratio, 4),
            "mean_asperity_radius_um": round(self.asperity_radius_um, 3),
            "asperity_radius_growth": round(self.radius_growth, 4),
            "mrr_trend_proxy": round(self.mrr_trend_proxy, 4),
            "disk_hours_used": round(self.disk_hours, 2),
            "disk_cut_rate_ratio": round(self.disk_cut_rate_ratio, 4),
            "notes": self.notes, "warnings": self.warnings,
        }
        if self.steady_state_contact is not None:
            out["steady_state_contact_ratio"] = round(self.steady_state_contact, 4)
        return out


def evaluate(*, pressure_psi: float, polish_minutes: float,
             disk_hours: float = 0.0,
             glazing_rate: Optional[float] = None,
             conditioning_rate: Optional[float] = None) -> PadLifeState:
    """Pad-life state at one point in a pad's history."""
    notes: List[str] = []
    warnings: List[str] = []

    used_p = _nearest_measured(pressure_psi)
    if abs(used_p - float(pressure_psi)) > 0.25:
        warnings.append(
            f"contact-count decay is measured only at {MEASURED_PRESSURES_PSI} psi "
            f"(Jeong 2024 Table 1); {pressure_psi:g} psi was snapped to {used_p} psi "
            "rather than extrapolating a fit beyond its data")

    if float(polish_minutes) > MEASURED_MAX_MINUTES:
        warnings.append(
            f"{polish_minutes:g} min of polishing is beyond the "
            f"{MEASURED_MAX_MINUTES:g} min covered by Jeong 2024 Table 1. The "
            "exponential fit is being extrapolated and degenerates quickly "
            "(it predicts near-zero contacts and physically impossible summit "
            "radii within a couple of hours). Treat the numbers below as "
            "'the pad is glazed', not as quantities. Real pads are conditioned "
            "in situ, which this unconditioned decay does not represent")

    n_ratio = contact_ratio(pressure_psi, polish_minutes)
    radius = mean_asperity_radius_um(pressure_psi, polish_minutes)
    growth = radius_growth_ratio(pressure_psi, polish_minutes)
    proxy = relative_mrr_proxy(pressure_psi, polish_minutes)
    disk_ratio = disk_cut_rate_ratio(disk_hours)

    notes.append(
        f"after {polish_minutes:g} min at {used_p} psi without conditioning: "
        f"contact count {100 * n_ratio:.0f}% of initial (tau = "
        f"{contact_decay_tau_min(pressure_psi):.1f} min), mean summit radius "
        f"{radius:.1f} um ({growth:.2f}x) — the pad glazes")
    notes.append(
        f"MRR trend proxy {proxy:.3f} = contact ratio x radius growth. Coarse: "
        "'force per contact' is approximated by summit radius alone, with no "
        "indentation depth or effective modulus, so use the direction, not the value")
    notes.append(
        f"conditioner after {disk_hours:g} h cuts at {100 * disk_ratio:.0f}% of a "
        f"new disk (tau = {DISK_AGING_TAU_HOURS:.1f} h from the Entegris 50 h / "
        "16% field anchor)")

    if disk_ratio < 0.3:
        warnings.append(
            f"the conditioner is worn ({100 * disk_ratio:.0f}% of new cut rate): "
            "asperity regeneration can no longer keep up with glazing, so the pad "
            "will settle at a lower steady state and the rate will drift down")

    ss = None
    if glazing_rate is not None and conditioning_rate is not None:
        ss = steady_state_contact_ratio(glazing_rate, conditioning_rate, disk_ratio)
        notes.append(
            f"steady-state contact fraction {ss:.3f} = k_c G / (k_g + k_c G) with "
            f"k_g = {glazing_rate:g}, k_c = {conditioning_rate:g}, G = {disk_ratio:.3f}")
    else:
        warnings.append(
            "glazing and conditioning rate constants were not supplied, so the "
            "steady-state balance was not computed — only the unconditioned decay "
            "is shown, which is the worst case")
    return PadLifeState(polish_minutes=float(polish_minutes), contact_ratio=n_ratio,
                        asperity_radius_um=radius, radius_growth=growth,
                        mrr_trend_proxy=proxy, disk_hours=float(disk_hours),
                        disk_cut_rate_ratio=disk_ratio, steady_state_contact=ss,
                        notes=notes, warnings=warnings)
