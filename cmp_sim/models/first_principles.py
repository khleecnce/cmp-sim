"""Estimate a Preston coefficient from material properties, when none is published.

Why this can work at all
------------------------
Preston's law and Archard's wear law are the same statement. Archard writes the
worn volume per unit sliding distance as ``V/L = k*W/H`` — load over hardness,
scaled by a dimensionless wear coefficient ``k``. Dividing by the contact area
turns load into pressure and sliding distance into velocity:

    MRR = k * P * V / H          and Preston says MRR = Kp * P * V

so

    **Kp = k / H**

Hardness is the material property that carries the film identity; ``k`` is the
dimensionless efficiency of the abrasive-pad-slurry system at removing what it
plastically displaces. If ``k`` were roughly common across CMP processes, then a
film with a measured hardness but no CMP history could be estimated.

Does ``k`` actually hold still? Tested, and the answer is "barely"
------------------------------------------------------------------
Computed from this repository's own packs, whose Kp values come from published
data and whose hardnesses come from nanoindentation literature:

===========================  =========  ========  ========  ==============
pack                         Kp [m/Pa]  H [GPa]   k = Kp*H  tool class
===========================  =========  ========  ========  ==============
cu_h2o2_bta                   3.50e-13      1.2   4.2e-04   device, 1-6 psi
w_fe_oxidizer                 7.00e-14     12.0   8.4e-04   device, 1-6 psi
oxide_silica                  1.00e-13      9.0   9.0e-04   device, 1-6 psi
poly_si_alkaline              1.07e-13     11.5   1.2e-03   device, 1-6 psi
sti_ceria                     2.20e-13      9.0   2.0e-03   device, 1-6 psi
si_substrate_alkaline         6.91e-13     10.0   6.9e-03   wafer-maker, 0.6 psi
sic_ceria_h2o2                1.71e-15     26.0   4.5e-05   chemically limited
===========================  =========  ========  ========  ==============

Two of those seven do not belong in a mechanical correlation, and both
exclusions were forced by the data rather than chosen for convenience:

* **SiC** is chemically rate-limited — this repository measures its rate varying
  5.2x at *identical* P*V, with P*V explaining only R^2 = 0.09 of the variance.
  Its k sits 20x below the rest.
* **Si substrate** is a different machine. Its Kp was back-calculated from a
  0.62 psi double-sided wafer-maker polisher, not a device CMP tool, and its k
  is 5.2x above the geometric mean of the others — the largest single outlier.

Over the five remaining device-CMP films the improvement is real but **modest**:
the log-10 standard deviation falls from 0.284 (Kp alone) to 0.247 (k), i.e.
from a typical factor of 1.9x to 1.8x. Including the wafer-maker point, the
correlation is actively *worse* than not dividing by hardness at all
(0.378 -> 0.415).

So the honest summary is: dividing by hardness helps a little **within one tool
class**, and the physical argument for the 1/H form is far stronger than the
statistical evidence from five points. This estimator is worth having because
it extrapolates in the right direction — a film three times softer should polish
about three times faster, all else equal — not because it is accurate.

What this module therefore is
-----------------------------
An **order-of-magnitude estimator with a stated uncertainty band**, not a
substitute for measurement. It exists so an unestablished film can be reasoned
about at all — to answer "roughly how fast, and how does that change if I halve
the pressure" — while making the ~3x uncertainty impossible to overlook. One
real measurement replaces it entirely, and the calibration module will say by
how much it was wrong.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

#: k = Kp*H over the five device-CMP films above (1-6 psi rotary tools),
#: geometric mean. SiC (chemically limited) and the Si substrate wafer-maker
#: process are excluded; see the module docstring for why.
WEAR_COEFFICIENT = 9.50e-4
#: 10**(log-10 standard deviation) of those five: the typical factor of error.
WEAR_COEFFICIENT_SPREAD = 1.8
#: The observed extremes, used for the reported band.
WEAR_COEFFICIENT_MIN = 4.2e-4
WEAR_COEFFICIENT_MAX = 1.98e-3
#: Pressure range the correlation was built in. Outside it, the tool class
#: itself differs and the constant is not transferable.
CALIBRATED_PRESSURE_PSI = (1.0, 6.0)

#: Melting points [K] for the homologous-temperature check.
MELTING_POINT_K = {
    "snag": 494.0,      # Sn-3.5Ag eutectic, 221 C
    "sn": 505.0,
    "cu": 1358.0,
    "w": 3695.0,
    "al": 933.0,
}
#: Above this fraction of the melting point a metal creeps at room temperature.
CREEP_HOMOLOGOUS_LIMIT = 0.4


@dataclass
class Estimate:
    """A Kp estimated from material properties, with its uncertainty."""
    kp_m_per_pa: Optional[float] = None
    kp_low: Optional[float] = None
    kp_high: Optional[float] = None
    basis: str = ""
    notes: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return self.kp_m_per_pa is not None

    def as_dict(self) -> Dict[str, Any]:
        return {
            "kp_m_per_pa": self.kp_m_per_pa,
            "kp_range_m_per_pa": (
                None if self.kp_low is None else [self.kp_low, self.kp_high]),
            "uncertainty_factor": WEAR_COEFFICIENT_SPREAD,
            "basis": self.basis,
            "notes": self.notes,
            "warnings": self.warnings,
        }


def homologous_temperature(film: str, temp_c: float = 25.0) -> Optional[float]:
    """T/T_melt. Above ~0.4 a metal creeps at the service temperature."""
    tm = MELTING_POINT_K.get(str(film).strip().lower())
    if not tm:
        return None
    return (float(temp_c) + 273.15) / tm


def estimate_kp(film: str, hardness_pa: float, temp_c: float = 25.0,
                pressure_psi: Optional[float] = None) -> Estimate:
    """Kp = k/H, with the band implied by the scatter in k."""
    est = Estimate()
    if not hardness_pa or float(hardness_pa) <= 0:
        est.warnings.append(
            "no film hardness, so nothing can be estimated: hardness is the "
            "only material property the Archard relation needs")
        return est

    h = float(hardness_pa)
    est.kp_m_per_pa = WEAR_COEFFICIENT / h
    est.kp_low = WEAR_COEFFICIENT_MIN / h
    est.kp_high = WEAR_COEFFICIENT_MAX / h
    est.basis = (
        f"Archard/Preston identity Kp = k/H with k = {WEAR_COEFFICIENT:.2e} "
        f"(geometric mean of five device-CMP films at 1-6 psi) and "
        f"H = {h / 1e9:.2f} GPa")
    est.notes.append(est.basis)
    est.notes.append(
        f"the wear coefficient spans {WEAR_COEFFICIENT_MIN:.1e}-"
        f"{WEAR_COEFFICIENT_MAX:.1e} across those five films, so this Kp is an "
        f"order-of-magnitude estimate with a factor of ~{WEAR_COEFFICIENT_SPREAD:.1f} "
        f"either way, not a measurement")
    est.warnings.append(
        f"Kp was ESTIMATED from hardness, not measured: treat the absolute rate "
        f"as accurate to a factor of ~{WEAR_COEFFICIENT_SPREAD:.1f} AT BEST. The "
        f"correlation rests on five films, and dividing by hardness improves the "
        f"scatter only modestly (log-10 sd 0.284 -> 0.247) - the physical "
        f"argument for Kp = k/H is stronger than the statistical evidence for "
        f"it. Use this to rank recipes and see trends, not to quote a number. "
        f"One measured rate replaces it entirely")

    if pressure_psi is not None:
        lo, hi = CALIBRATED_PRESSURE_PSI
        if not lo <= float(pressure_psi) <= hi:
            est.warnings.append(
                f"the correlation was built from device-CMP processes at "
                f"{lo:g}-{hi:g} psi, but this run is at {float(pressure_psi):g} psi. "
                f"The one wafer-maker process in the source data (0.62 psi) has a "
                f"wear coefficient 5x above the device films, so the constant does "
                f"not transfer across tool classes - this estimate is weaker still")

    # ── the physics this simple form does not carry ──────────────────
    th = homologous_temperature(film, temp_c)
    if th is not None and th > CREEP_HOMOLOGOUS_LIMIT:
        est.notes.append(
            f"homologous temperature T/T_melt = {th:.2f} at {temp_c:.0f} C")
        est.warnings.append(
            f"this film sits at {th:.0%} of its melting point at room "
            "temperature, so it creeps while being polished. Archard assumes "
            "hardness is a fixed flow stress; for a creeping solid the "
            "effective hardness falls as the strain rate falls, so the real "
            "rate is likely HIGHER than estimated and will depend on dwell "
            "time in a way this model does not capture. It will also smear and "
            "embed abrasive rather than fracturing cleanly, which no term here "
            "represents")
    return est


def estimate_for_pack(pack, film: str, temp_c: float = 25.0,
                      pressure_psi: Optional[float] = None) -> Estimate:
    """Estimate Kp for a pack that declares a hardness but no Kp."""
    param = pack.params.get("film_bulk_hardness_pa")
    hardness = None if param is None else getattr(param, "value", None)
    if hardness is None:
        est = Estimate()
        est.warnings.append(
            f"'{film}' has neither a Preston coefficient nor a film hardness, "
            "so not even an order-of-magnitude estimate is possible. Supply "
            "film_bulk_hardness_pa under params:, or a measured rate under "
            "measurements:")
        return est
    est = estimate_kp(film, float(hardness), temp_c, pressure_psi)
    src = getattr(param, "source", "") or "unstated source"
    est.notes.append(f"hardness from: {src}")
    return est
