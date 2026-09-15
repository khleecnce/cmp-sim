"""Unit registry (pint) + the conversions this project repeats everywhere.

Single source of truth for unit handling so no module re-invents psi->Pa.
"""
from __future__ import annotations

import pint

ureg = pint.UnitRegistry()
Q_ = ureg.Quantity

PSI_TO_PA = 6894.757293168361      # exact definition of psi
M_PER_S_TO_NM_PER_MIN = 6.0e10     # 1 m/s = 1e9 nm/s * 60 s/min
ANGSTROM_PER_NM = 10.0


def psi_to_pa(psi: float) -> float:
    return float(psi) * PSI_TO_PA


def pa_to_psi(pa: float) -> float:
    return float(pa) / PSI_TO_PA


def rpm_to_rad_s(rpm: float) -> float:
    return float(rpm) * 2.0 * 3.141592653589793 / 60.0


def mps_to_nm_per_min(v: float) -> float:
    return float(v) * M_PER_S_TO_NM_PER_MIN


def nm_per_min_to_angstrom_per_min(v: float) -> float:
    return float(v) * ANGSTROM_PER_NM
