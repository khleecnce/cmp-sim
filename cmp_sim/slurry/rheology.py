"""Slurry bulk properties derived from the formulation (owner request 1-3).

Given abrasive loading, additive salts and pH, derive the properties that the
transport and contact layers actually consume: viscosity, ionic strength,
Debye length, zeta potential sign and colloidal stability.

Physics used (all standard, none CMP-specific)
----------------------------------------------
Viscosity of a dilute/semi-dilute hard-sphere suspension, Krieger-Dougherty:

    eta = eta_0 * (1 - phi/phi_max)^(-[eta]*phi_max)

with ``[eta] = 2.5`` (Einstein) and ``phi_max`` the maximum packing fraction.
Truncating the series at first order recovers Einstein's 1906 result
``eta = eta_0 (1 + 2.5 phi)``, so the two agree in the dilute limit; CMP
slurries at 1-30 wt% sit where the higher-order term matters.

  * I. M. Krieger, T. J. Dougherty, Trans. Soc. Rheol. 3, 137 (1959),
    doi:10.1122/1.548848
  * A. Einstein, Ann. Phys. 19, 289 (1906), doi:10.1002/andp.19063240204

Water viscosity vs temperature uses the Vogel form of the IAPWS correlation.

Volume fraction from weight percent (mass balance, exact):

    phi = (w/rho_p) / (w/rho_p + (1-w)/rho_w)

Ionic strength for a dissociating salt, I = 0.5 * sum(c_i z_i^2), and the
Debye length is taken from the inherited, already-verified
``legacy/sim/tier2_physics/dlvo_colloid.py`` (Israelachvili form) rather than
re-derived here.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from cmp_sim.core.legacy_bridge import install  # noqa: F401  (sys.path for tier2)

import dlvo_colloid  # legacy/sim/tier2_physics/dlvo_colloid.py

RHO_WATER_KG_M3 = 997.0          # 25 C
EINSTEIN_COEFF = 2.5             # intrinsic viscosity of hard spheres
PHI_MAX_RANDOM_CLOSE_PACK = 0.64  # random close packing of monodisperse spheres


def water_viscosity_pa_s(temp_c: float) -> float:
    """Dynamic viscosity of liquid water [Pa s], Vogel-type fit, 0-100 C.

        eta = A * 10^(B / (T - C))

    with **T in kelvin**, A = 2.414e-5 Pa s, B = 247.8 K, C = 140 K
    (Al-Shemmeri, "Engineering Fluid Mechanics", 2012, after the classic
    Vogel-Fulcher form). Reproduces the CRC Handbook values 1.002e-3 Pa s at
    20 C and 8.90e-4 at 25 C to better than 1%.

    Note: the argument is Celsius for convenience but the correlation is in
    kelvin — using Celsius directly is a ~15% error at room temperature.
    """
    t_k = float(temp_c) + 273.15
    return 2.414e-5 * 10.0 ** (247.8 / (t_k - 140.0))


def volume_fraction_from_wt_pct(wt_pct: float, particle_density_kg_m3: float,
                                fluid_density_kg_m3: float = RHO_WATER_KG_M3) -> float:
    """Exact mass-balance conversion of wt% solids to volume fraction."""
    w = float(wt_pct) / 100.0
    if not 0.0 <= w < 1.0:
        raise ValueError(f"abrasive wt% must be in [0,100), got {wt_pct}")
    if w == 0.0:
        return 0.0
    v_p = w / float(particle_density_kg_m3)
    v_f = (1.0 - w) / float(fluid_density_kg_m3)
    return v_p / (v_p + v_f)


def krieger_dougherty_viscosity(phi: float, eta_0_pa_s: float,
                                phi_max: float = PHI_MAX_RANDOM_CLOSE_PACK,
                                intrinsic: float = EINSTEIN_COEFF) -> float:
    """Suspension viscosity [Pa s]. Reduces to Einstein 1+2.5phi as phi->0."""
    phi = float(phi)
    if phi < 0:
        raise ValueError("volume fraction must be >= 0")
    if phi >= phi_max:
        raise ValueError(
            f"volume fraction {phi:.3f} reaches maximum packing {phi_max} — "
            "the suspension is jammed; Krieger-Dougherty does not apply")
    return float(eta_0_pa_s) * (1.0 - phi / phi_max) ** (-intrinsic * phi_max)


def einstein_viscosity(phi: float, eta_0_pa_s: float) -> float:
    """First-order dilute limit — kept for cross-checking KD."""
    return float(eta_0_pa_s) * (1.0 + EINSTEIN_COEFF * float(phi))


def ionic_strength_M(species: Optional[Dict[str, Any]] = None,
                     ph: Optional[float] = None) -> float:
    """I = 0.5 * sum c_i z_i^2 [mol/L].

    ``species`` maps a label to ``{"conc_M": c, "charge": z, "n_ions": k}``.
    When only pH is known, the contribution of H+ / OH- alone is returned —
    that is a *floor*, not the real ionic strength of a buffered slurry, and
    callers must treat it as such.
    """
    total = 0.0
    for spec in (species or {}).values():
        c = float(spec.get("conc_M", 0.0))
        z = float(spec.get("charge", 1.0))
        k = float(spec.get("n_ions", 1.0))
        total += k * c * z * z
    if ph is not None:
        h = 10.0 ** (-float(ph))
        oh = 10.0 ** (-(14.0 - float(ph)))
        total += h + oh
    return 0.5 * total


def debye_length_nm(ionic_strength_molar: float, temp_c: float = 25.0) -> float:
    """Debye screening length [nm] — inherited verified implementation."""
    return float(dlvo_colloid.debye_length_nm(max(float(ionic_strength_molar), 1e-12),
                                              T=float(temp_c) + 273.15))


@dataclass
class SlurryProperties:
    viscosity_pa_s: float
    volume_fraction: float
    ionic_strength_M: float
    debye_length_nm: float
    ph: Optional[float] = None
    zeta_sign_abrasive: Optional[str] = None
    zeta_sign_film: Optional[str] = None
    electrostatic_regime: Optional[str] = None
    stability: Optional[str] = None
    notes: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    def as_dict(self) -> Dict[str, Any]:
        return {
            "viscosity_pa_s": round(self.viscosity_pa_s, 6),
            "volume_fraction": round(self.volume_fraction, 5),
            "ionic_strength_M": round(self.ionic_strength_M, 6),
            "debye_length_nm": round(self.debye_length_nm, 3),
            "ph": self.ph,
            "zeta_sign_abrasive": self.zeta_sign_abrasive,
            "zeta_sign_film": self.zeta_sign_film,
            "electrostatic_regime": self.electrostatic_regime,
            "stability": self.stability,
            "notes": self.notes,
            "warnings": self.warnings,
        }


def _sign(ph: float, iep: float) -> str:
    """Surface charge sign relative to the isoelectric point."""
    if abs(ph - iep) < 0.3:
        return "neutral"
    return "negative" if ph > iep else "positive"


def derive(abrasive_wt_pct: Optional[float],
           particle_density_kg_m3: Optional[float],
           ph: Optional[float] = None,
           temp_c: float = 25.0,
           species: Optional[Dict[str, Any]] = None,
           abrasive_iep_ph: Optional[float] = None,
           film_iep_ph: Optional[float] = None,
           measured_viscosity_pa_s: Optional[float] = None,
           measured_zeta_mv: Optional[float] = None) -> SlurryProperties:
    """Derive bulk slurry properties from the formulation.

    A measured value always wins over the derived one; the derived value is
    still reported in ``notes`` so the discrepancy is visible.
    """
    notes: List[str] = []
    warnings: List[str] = []

    eta_0 = water_viscosity_pa_s(temp_c)
    phi = 0.0
    if abrasive_wt_pct:
        if not particle_density_kg_m3:
            raise ValueError(
                "abrasive wt% given without particle density — cannot convert to "
                "volume fraction. Supply density from the abrasive database.")
        phi = volume_fraction_from_wt_pct(abrasive_wt_pct, particle_density_kg_m3)
    eta = krieger_dougherty_viscosity(phi, eta_0)
    notes.append(
        f"Krieger-Dougherty: phi={phi:.4f} -> eta={eta:.4e} Pa s "
        f"(water {eta_0:.4e} at {temp_c:.1f} C; Einstein limit "
        f"{einstein_viscosity(phi, eta_0):.4e})")
    if measured_viscosity_pa_s:
        notes.append(f"using measured viscosity {measured_viscosity_pa_s:.4e} Pa s "
                     f"(derived would be {eta:.4e})")
        eta = float(measured_viscosity_pa_s)

    I = ionic_strength_M(species, ph)
    if not species and ph is not None:
        warnings.append(
            "ionic strength computed from pH alone — this is a lower bound; a "
            "buffered or salt-bearing slurry is far more concentrated. Supply "
            "additive concentrations for a real value.")
    kappa_inv = debye_length_nm(I, temp_c)
    notes.append(f"ionic strength {I:.3e} M -> Debye length {kappa_inv:.2f} nm")

    z_ab = z_film = regime = stability = None
    if ph is not None and abrasive_iep_ph is not None:
        z_ab = _sign(ph, abrasive_iep_ph)
        if film_iep_ph is not None:
            z_film = _sign(ph, film_iep_ph)
            same = (z_ab == z_film) and z_ab != "neutral"
            regime = "repulsive (like charges)" if same else "attractive (opposite charges)"
            notes.append(
                f"pH {ph} vs abrasive IEP {abrasive_iep_ph} / film IEP {film_iep_ph}: "
                f"abrasive {z_ab}, film {z_film} -> {regime}. Attraction raises "
                "particle-surface contact but also agglomeration and defect risk.")
        # Inherited qualitative agglomeration risk: distance from the IEP.
        # Its 1.0 / 2.0 pH thresholds are explicitly unverified in the legacy
        # note, so the risk level is reported, never silently trusted.
        st = dlvo_colloid.stability_qualitative(float(ph), float(abrasive_iep_ph),
                                                film_iep_ph)
        stability = f"agglomeration risk {st['risk']} (|pH-IEP|={st['distance_from_iep_ph']:.2f})"
        warnings.append(
            "colloidal stability classed by |pH-IEP| distance with unverified "
            "1.0/2.0 thresholds (inherited dlvo_colloid.stability_qualitative); "
            "a measured zeta potential should override it")
    if measured_zeta_mv is not None:
        z_ab = "negative" if measured_zeta_mv < 0 else "positive"
        notes.append(f"zeta sign taken from measured {measured_zeta_mv} mV")
        if abs(measured_zeta_mv) < 20.0:
            warnings.append(
                f"|zeta| = {abs(measured_zeta_mv):.1f} mV < 20 mV: electrostatic "
                "stabilisation is weak, agglomeration and large-particle tail growth "
                "are likely (raises the scratch-defect proxy)")

    return SlurryProperties(
        viscosity_pa_s=eta, volume_fraction=phi, ionic_strength_M=I,
        debye_length_nm=kappa_inv, ph=ph, zeta_sign_abrasive=z_ab,
        zeta_sign_film=z_film, electrostatic_regime=regime, stability=stability,
        notes=notes, warnings=warnings)
