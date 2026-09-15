"""P1 — Preston baseline.

    MRR(r) = Kp * P(r) * V(r)

Implementation reuses the inherited, verified modules rather than re-deriving:
* ``legacy/sim/tier1_empirical/kinematics.py`` — relative velocity field
  (Lai 2001 Eq. 2.12 kinematics of a rotary polisher)
* ``legacy/sim/tier1_empirical/preston.py``    — ``mrr_profile``, theta-averaged
  MRR(r) = Kp * P(r) * <|v(r,theta)|>_theta
* ``legacy/sim/tier1_empirical/wiwnu.py``      — pressure profile generators
  (``p_uniform`` / ``p_zoned``) and the area-weighted WIWNU metrics

Reference: F. Preston, "The theory and design of plate glass finishing
machines", J. Soc. Glass Technol. 11, 214 (1927).

Kp decomposition
----------------
Preston's Kp lumps slurry chemistry, abrasive mechanics, pad and film into one
constant. CMP-Sim keeps a literature-anchored ``kp_m_per_pa`` per film/slurry
pack and multiplies it by dimensionless factors (all exactly 1.0 at the pack's
reference condition), so P1 stays numerically identical to the calibration
point while later phases (P2-P7) attach physics without double counting:

    Kp_eff = kp_m_per_pa * prod(factor_i)

At P1 no factors are attached, hence ``Kp_eff == kp_m_per_pa``.
"""
from __future__ import annotations

from typing import Callable, Dict, List, Optional, Tuple

import numpy as np

from cmp_sim.core.legacy_bridge import legacy_preston, legacy_wiwnu
from cmp_sim.core.units import M_PER_S_TO_NM_PER_MIN

NAME = "preston"


def pressure_profile(
    pressure_pa: float,
    zone_pressures_pa: Optional[List[float]] = None,
    zone_edges_norm: Optional[List[float]] = None,
) -> Tuple[Callable[[np.ndarray], np.ndarray], str]:
    """Return ``P(r_norm)`` and a label describing which profile was used."""
    if zone_pressures_pa:
        edges = list(zone_edges_norm or [])
        if len(edges) == len(zone_pressures_pa):        # user gave outer edges only
            edges = [0.0] + edges
        if len(edges) != len(zone_pressures_pa) + 1:
            raise ValueError(
                "zone_edges_norm must have len(zone_pressures)+1 (inner..outer) "
                f"or len(zone_pressures); got {len(edges)} vs {len(zone_pressures_pa)}"
            )
        return legacy_wiwnu.p_zoned(edges, zone_pressures_pa), "zoned"
    return legacy_wiwnu.p_uniform(pressure_pa), "uniform"


def mrr_radial_nm_per_min(
    wafer_radius_m: float,
    center_offset_m: float,
    rpm_head: float,
    rpm_platen: float,
    kp_m_per_pa: float,
    pressure_pa: float,
    n_radial: int = 81,
    zone_pressures_pa: Optional[List[float]] = None,
    zone_edges_norm: Optional[List[float]] = None,
) -> Tuple[np.ndarray, np.ndarray, str]:
    """Radial MRR profile in nm/min.

    Returns ``(radius_m, mrr_nm_per_min, pressure_profile_label)``.
    """
    p_fn, label = pressure_profile(pressure_pa, zone_pressures_pa, zone_edges_norm)
    rs = np.linspace(0.0, wafer_radius_m, int(n_radial))

    # legacy preston.mrr_profile passes absolute radius to pressure_fn; the zone /
    # uniform generators from legacy wiwnu expect normalised radius, so wrap.
    def p_abs(r: float) -> float:
        return p_fn(np.asarray(r, float) / wafer_radius_m)

    rs, mrr_m_s = legacy_preston.mrr_profile(
        wafer_radius_m, center_offset_m, rpm_head, rpm_platen,
        pressure_pa, kp_m_per_pa, n_r=int(n_radial), pressure_fn=p_abs,
    )
    return rs, np.asarray(mrr_m_s) * M_PER_S_TO_NM_PER_MIN, label


def uniformity(radius_m: np.ndarray, values: np.ndarray) -> Dict[str, float]:
    """Area-weighted non-uniformity metrics (inherited definitions)."""
    return legacy_wiwnu.wiwnu(np.asarray(radius_m, float), np.asarray(values, float))
