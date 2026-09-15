"""Post-hoc plausibility check of a predicted removal rate.

Why this exists
---------------
Every pack's ``kp_m_per_pa`` is back-calculated from a single published
operating point. Outside that regime the linear extrapolation can be wrong by
orders of magnitude — the inherited project records a case where a silica pack
calibrated at pH 11 was 40x off when run at pH 4.7.

A simulator that returns "11,935 A/min" for SiC with no comment is lying by
omission: published SiC CMP rates are a few nm/min, because SiC is one of the
hardest materials polished in a fab. This module compares the prediction with
the range reported in the literature for that film and says so when it falls
outside. It never modifies the number — it annotates it.

Ranges are order-of-magnitude envelopes from review literature, deliberately
generous (they are meant to catch 10x errors, not 30% ones).
"""
from __future__ import annotations

from typing import Dict, List, Optional, Tuple

#: film -> (low, high) removal rate in A/min, with the basis for the range
PLAUSIBLE_RATE_A_PER_MIN: Dict[str, Tuple[float, float, str]] = {
    "oxide": (200.0, 6000.0,
              "TEOS/thermal oxide with silica or ceria slurries; Mariscal 2020 "
              "measures 698-2,529 A/min over 2-4 psi and 0.75-1.75 m/s"),
    "oxide_ceria": (200.0, 6000.0, "as oxide; ceria slurries sit at the upper end"),
    "sti": (200.0, 6000.0, "STI oxide with ceria slurries"),
    "cu": (1000.0, 12000.0,
           "copper damascene bulk removal; production recipes target roughly "
           "3,000-10,000 A/min"),
    "w": (300.0, 4000.0,
          "tungsten plug CMP with Fe/H2O2 chemistry"),
    "poly_si": (200.0, 5000.0, "poly-Si in alkaline slurries"),
    "si": (100.0, 3000.0, "single-crystal Si substrate, final polish"),
    "sic": (1.0, 200.0,
            "4H-SiC is chemically inert and extremely hard: published CMP rates "
            "are a few nm/min (Wang DOE: 2.7-6.7 nm/min = 27-67 A/min)"),
    "snag": (1000.0, 20000.0, "SnAg solder is very soft"),
    "sin": (50.0, 2000.0, "silicon nitride, usually the stop layer"),
}


def check_rate(film: str, rate_a_per_min: float) -> List[str]:
    """Return warnings if the predicted rate is outside the published envelope."""
    entry = PLAUSIBLE_RATE_A_PER_MIN.get(str(film).lower())
    if entry is None:
        return [f"no published rate envelope on record for film '{film}', so the "
                "absolute value below could not be sanity-checked"]
    lo, hi, basis = entry
    if rate_a_per_min > hi:
        factor = rate_a_per_min / hi
        return [
            f"IMPLAUSIBLE RATE: {rate_a_per_min:,.0f} A/min is {factor:.1f}x above "
            f"the top of the published range for {film} ({lo:,.0f}-{hi:,.0f} A/min; "
            f"{basis}). The pack's Kp was back-calculated from one operating point, "
            "and this run is far enough outside it that the absolute value should "
            "not be trusted. Relative comparisons between two recipes remain useful; "
            "the absolute number needs Kp recalibrated against your own measurements."]
    if rate_a_per_min < lo:
        factor = lo / max(rate_a_per_min, 1e-9)
        return [
            f"IMPLAUSIBLE RATE: {rate_a_per_min:,.1f} A/min is {factor:.1f}x below "
            f"the bottom of the published range for {film} ({lo:,.0f}-{hi:,.0f} "
            f"A/min; {basis}). Check the pressure, speed and Kp source."]
    return []
