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
    "oxide_ceria": (200.0, 6000.0,
                    "same envelope as oxide, measured with a ceria slurry: "
                    "Mariscal 2020 reports 698-2,529 A/min on PETEOS over "
                    "2-4 psi; ceria sits at the upper end of the oxide range"),
    "sti": (200.0, 6000.0,
            "STI oxide with ceria slurries; bounded by the same PETEOS/ceria "
            "measurements (Mariscal 2020, 698-2,529 A/min at 2-4 psi)"),
    "cu": (1000.0, 12000.0,
           "copper damascene bulk removal; production recipes target roughly "
           "3,000-10,000 A/min"),
    "w": (300.0, 4000.0,
          "tungsten plug CMP with Fe/H2O2 chemistry; Kp least-squares fitted to "
          "US2011/0186542A1 and US8070843B2 rate tables"),
    "poly_si": (200.0, 5000.0,
                "poly-Si in alkaline slurries; Pirzada 2014 (doi:10.7939/"
                "r3zp3w76c) Table 3-1 gives K = 0.0064 (um/min)/(kN/(m*s)), "
                "reproducing 11.0-33.1 kN/(m*s) over 30-90 rpm"),
    "si": (100.0, 3000.0,
           "single-crystal Si substrate final polish; Seidel 1990 "
           "(doi:10.1149/1.2086277) for the alkaline mechanism, with the pack's "
           "Kp giving 0.302 um/min against the source's stated 0.3 um/min"),
    # Bounded by the measurement rather than by intuition: Wang's DOE spans
    # 27-67 A/min, so 10-300 allows a generous 2.5x either side of it while
    # still catching a 10x error. The old 1-200 was 200x wide - loose enough
    # that a prediction 40x below anything ever measured would have passed.
    "sic": (10.0, 300.0,
            "4H-SiC is chemically inert and extremely hard: published CMP rates "
            "are a few nm/min (Wang DOE: 2.7-6.7 nm/min = 27-67 A/min)"),
    # NO ENTRY for "snag", deliberately. Every other range here cites a
    # measurement; this one previously read (1,000-20,000, "SnAg solder is very
    # soft"), which cites nothing and was wide enough to pass any prediction the
    # model could produce - a guard that cannot fire is worse than no guard,
    # because it reads as having checked something. No primary source publishes
    # a SnAg or pure-Sn CMP removal rate at a stated pressure and velocity
    # (searched: 320 local CMP papers, ScienceDirect, Crossref). The missing
    # entry makes check_rate() say so instead.
    # NO ENTRY for "sin" either. There is no silicon-nitride parameter pack, so
    # the film cannot be run; the range that used to sit here (50-2,000, "usually
    # the stop layer") cited nothing and guarded nothing. If a nitride pack is
    # added, bound it with that pack's own measurements.
}


def check_rate(film: str, rate_a_per_min: float) -> List[str]:
    """Return warnings if the predicted rate is outside the published envelope."""
    entry = PLAUSIBLE_RATE_A_PER_MIN.get(str(film).lower())
    if entry is None:
        return [f"the absolute rate for '{film}' could not be sanity-checked: no "
                "published removal rate at a stated pressure and velocity exists "
                "to bound it. Treat the value as a RANKING between recipes, not a "
                "prediction — an error of 10x would not be caught here. One "
                "measured rate under `measurements:` replaces this with a "
                "cross-validated error."]
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
