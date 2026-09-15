"""P2 — Greenwood-Williamson asperity contact.

Why this layer exists
---------------------
Preston applies the *nominal* pressure, but a polyurethane pad touches the
wafer only at asperity summits. With an exponential summit-height
distribution the GW result is remarkable and is what saves Preston:

    A_r  proportional to W        (real contact area grows linearly with load)
    p_r  = W / A_r = const        (mean real contact pressure is load-INDEPENDENT)
    n    proportional to W        (the number of contacts grows instead)

So raising the down-force does not press each abrasive harder; it recruits more
contacts. That is exactly why MRR is linear in P — Preston's phenomenology is a
consequence of GW geometry, not an independent assumption.

Reference: J. A. Greenwood, J. B. P. Williamson, "Contact of nominally flat
surfaces", Proc. R. Soc. Lond. A 295, 300 (1966), doi:10.1098/rspa.1966.0242.

Implementation
--------------
The GW inverse problem (nominal pressure -> separation -> contact state) is
already solved and self-tested in the inherited modules, so it is wrapped, not
re-derived:

* ``legacy/sim/tier2_physics/gw_contact.py``      Hertz force/area, exponential
  summit pdf, ``gw_numeric``, ``gw_analytic_ratio``, ``plasticity_index``
* ``legacy/sim/tier2_physics/gw_pressure_solve.py`` ``solve_separation`` (Brent)
  and ``local_contact_state``
* ``legacy/sim/tier2_physics/gw_preston_link.py``  ``n_contacts_at``,
  ``calibrate_alpha_removal`` — the Kp = alpha_removal * dn/dP decomposition

What this module adds
---------------------
1. Pad properties come from the pad object / parameter pack instead of module
   constants, so a different pad is a data change (``PadContactState``).
2. A Shore D -> Young's modulus correlation for when a datasheet gives only
   hardness.
3. A *relative* contact factor for the solver: the GW-predicted contact term
   normalised by the same term at the pack's reference pad state, so it is
   exactly 1.0 for the pad the Kp was calibrated on and cannot double-count.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

from cmp_sim.core.legacy_bridge import install  # noqa: F401

import gw_contact                # legacy/sim/tier2_physics/gw_contact.py
import gw_preston_link           # legacy/sim/tier2_physics/gw_preston_link.py
from gw_pressure_solve import local_contact_state  # legacy

NAME = "contact_gw"


class ContactSolverOutOfRange(ValueError):
    """The elastic GW contact model has no solution at this load."""


def shore_d_to_youngs_modulus_pa(shore_d: float) -> float:
    """Young's modulus [Pa] from Shore D durometer.

    Correlation of Qi, Joyce & Boyce (Rubber Chem. Technol. 76, 419 (2003)),
    who measured E against both Shore A and Shore D on polyurethanes:

        E [MPa] = 10 ** (0.0235 * S - 0.6403)      with S the Shore A value
        S_A = S_D * 2.0 + 20.0                     (ASTM D2240 overlap region,
                                                    valid roughly S_D 20-60)

    IC1000-class CMP pads are quoted near 55-60 Shore D and measure a few
    hundred MPa in the literature, which this reproduces to the right order.
    Outside Shore D 20-60 the conversion is an extrapolation and the caller
    is warned.
    """
    s_d = float(shore_d)
    s_a = 2.0 * s_d + 20.0
    e_mpa = 10.0 ** (0.0235 * s_a - 0.6403)
    return e_mpa * 1.0e6


def shore_d_conversion_is_in_range(shore_d: float) -> bool:
    return 20.0 <= float(shore_d) <= 60.0


def equivalent_modulus_pa(e_pad_pa: float, nu_pad: float = 0.4,
                          e_wafer_pa: float = 7.0e10, nu_wafer: float = 0.17) -> float:
    """Hertz equivalent (reduced) modulus E*.

        1/E* = (1 - nu_1^2)/E_1 + (1 - nu_2^2)/E_2

    The wafer film is ~2 orders stiffer than the pad, so E* is pad-dominated;
    the film term is kept because it matters for hard films such as SiC.
    Defaults: thermal oxide E = 70 GPa, nu = 0.17.
    """
    inv = (1.0 - nu_pad ** 2) / float(e_pad_pa) + (1.0 - nu_wafer ** 2) / float(e_wafer_pa)
    return 1.0 / inv


@dataclass
class PadContactState:
    """GW summit statistics of one pad surface at one conditioning state."""
    e_star_pa: float
    asperity_radius_m: float
    asperity_density_m2: float
    height_sigma_m: float          # 1/beta, the exponential height scale
    nominal_area_m2: float = 1.0e-4

    @property
    def beta_inv_m(self) -> float:
        return self.height_sigma_m

    def contact_state(self, pressure_pa: float) -> Dict[str, float]:
        """Solve the GW inverse problem at this nominal pressure.

        The inherited solver brackets the separation over a fixed span of the
        summit-height distribution, so a load it cannot reach even with every
        summit fully engaged fails to bracket. That is a genuine physical limit
        of the elastic GW picture, not a numerical hiccup, but the inherited
        message says only "bracket failed" (in Korean) with two residuals.
        Translate it into what the user actually did.
        """
        try:
            return local_contact_state(
                float(pressure_pa), self.nominal_area_m2,
                1.0 / self.height_sigma_m, self.asperity_density_m2,
                self.e_star_pa, self.asperity_radius_m)
        except RuntimeError as exc:
            raise self._out_of_range(pressure_pa) from exc

    def _out_of_range(self, pressure_pa: float) -> "ContactSolverOutOfRange":
        return ContactSolverOutOfRange(
            f"the Greenwood-Williamson contact solver cannot reach "
            f"{float(pressure_pa) / 6894.757:.1f} psi on this pad "
            f"(E* = {self.e_star_pa / 1e6:.0f} MPa, summit density "
            f"{self.asperity_density_m2:.3g} /m^2, roughness "
            f"{self.height_sigma_m * 1e6:.1f} um). Every summit is already in "
            f"contact below this load, so the elastic asperity model has no "
            f"solution here: past full contact the pad deforms in bulk rather "
            f"than at its summits. Either lower the pressure into the 0.5-10 psi "
            f"range these correlations were fitted across, or use a profile "
            f"without the contact layer (for example 'preston_baseline').")

    def n_contacts(self, pressure_pa: float) -> float:
        # Reaches the same inherited solver by a different path, so it needs
        # the same translation - see contact_state().
        try:
            return float(gw_preston_link.n_contacts_at(
                float(pressure_pa), E_star=self.e_star_pa,
                R=self.asperity_radius_m, beta=1.0 / self.height_sigma_m,
                eta=self.asperity_density_m2, A_n=self.nominal_area_m2))
        except RuntimeError as exc:
            raise self._out_of_range(pressure_pa) from exc

    def mean_real_pressure_pa(self, pressure_pa: float) -> float:
        return float(self.contact_state(pressure_pa)["p_r_mean"])

    def real_area_fraction(self, pressure_pa: float) -> float:
        return float(self.contact_state(pressure_pa)["contact_area_fraction"])

    @property
    def n_asperities_total(self) -> float:
        """Every summit on the nominal area — the ceiling on n_contacts."""
        return self.asperity_density_m2 * self.nominal_area_m2

    def saturation(self, pressure_pa: float) -> float:
        """Fraction of summits in contact, n(P) / (eta * A_n).

        GW's load-independent real pressure holds while contact is confined to
        the exponential tail of the height distribution. Once most summits are
        touching, the pad can only respond by compressing existing contacts:
        p_r starts to rise, A_r stops growing linearly, and the Preston
        linearity that GW underwrites is lost. Saturation is therefore a hard
        validity boundary that must be reported, not silently crossed.
        """
        return self.n_contacts(pressure_pa) / self.n_asperities_total

    def plasticity_index(self, film_hardness_pa: float) -> float:
        """psi = (E*/H) * sqrt(sigma_z/R). psi > 1 means plastic asperity flow;
        the elastic GW result (load-independent p_r) then no longer holds."""
        return float(gw_contact.plasticity_index(
            self.e_star_pa, float(film_hardness_pa),
            self.height_sigma_m, self.asperity_radius_m))

    def dn_dp_per_pa(self, pressures_pa: Optional[List[float]] = None) -> float:
        """Least-squares slope dn/dP — the geometric half of Preston's Kp."""
        ps = list(pressures_pa or [14.0e3, 48.0e3, 96.0e3])
        ns = [self.n_contacts(p) for p in ps]
        slope, _ = gw_preston_link.linear_fit_slope(ps, ns)
        return float(slope)


#: summit-contact fraction above which the GW exponential-tail result is void
SATURATION_WARN = 0.50


def contact_factor(pad: PadContactState, reference: PadContactState,
                   pressure_pa: float) -> Tuple[float, List[str], List[str]]:
    """Dimensionless Kp multiplier from the pad's contact state.

    Removal is taken proportional to the real contact area (equivalently, for
    exponential summits, to the number of contacts), so

        factor = A_r(pad) / A_r(reference)     at the same nominal pressure.

    It is exactly 1.0 when the pad equals the reference pad the pack's Kp was
    calibrated on, which is what prevents double counting.
    """
    notes: List[str] = []
    warnings: List[str] = []
    a_pad = pad.real_area_fraction(pressure_pa)
    a_ref = reference.real_area_fraction(pressure_pa)
    factor = a_pad / a_ref
    notes.append(
        f"GW contact: real-area fraction {a_pad:.3e} vs reference {a_ref:.3e} "
        f"-> kappa = {factor:.4f}")
    notes.append(
        f"mean real contact pressure {pad.mean_real_pressure_pa(pressure_pa):.3e} Pa "
        f"(load-independent for exponential summits, GW 1966)")

    for label, state in (("pad", pad), ("reference pad", reference)):
        sat = state.saturation(pressure_pa)
        notes.append(f"{label} summit saturation {100.0 * sat:.1f}%")
        if sat > SATURATION_WARN:
            warnings.append(
                f"{label} has {100.0 * sat:.0f}% of its summits in contact at "
                f"{pressure_pa / 1e3:.1f} kPa. Above ~{100.0 * SATURATION_WARN:.0f}% "
                "the GW exponential-tail assumption fails: real contact area stops "
                "growing linearly with load, so both kappa and the Preston pressure "
                "linearity are unreliable here. Use a stiffer pad, a rougher "
                "surface, or a lower pressure — or treat this point as out of range.")
    return factor, notes, warnings


def verify_load_independence(pad: PadContactState,
                             pressures_pa: Optional[List[float]] = None
                             ) -> Dict[str, Any]:
    """Re-run GW's central claims on a given pad: p_r constant, n and A_r linear
    in load. Used by the unit tests and reported as a diagnostic."""
    ps = list(pressures_pa or [7.0e3, 14.0e3, 28.0e3, 48.0e3, 96.0e3])
    states = [pad.contact_state(p) for p in ps]
    p_r = np.array([s["p_r_mean"] for s in states])
    n = np.array([s["n_contacts"] for s in states])
    a_r = np.array([s["A_r"] for s in states])
    return {
        "pressures_pa": ps,
        "p_r_mean_pa": [float(v) for v in p_r],
        "p_r_spread_rel": float(np.ptp(p_r) / np.mean(p_r)),
        "n_over_p_spread_rel": float(np.ptp(n / np.array(ps)) / np.mean(n / np.array(ps))),
        "a_r_over_p_spread_rel": float(np.ptp(a_r / np.array(ps)) / np.mean(a_r / np.array(ps))),
        "analytic_a_r_over_w": float(gw_contact.gw_analytic_ratio(
            1.0 / pad.height_sigma_m, pad.e_star_pa, pad.asperity_radius_m)),
    }
