"""P8 — defect proxy: scratch and residue risk.

Scratches are not caused by the mean particle size. A 50-150 nm D50 is far
below the ~680 nm scratch threshold; what scratches a wafer is the **tail** of
the distribution — the few oversized or agglomerated particles.

    Delta = (D99 / D99_ref)^n * (1 + aggregate_ratio)

exactly 1.0 at the pack's reference slurry, and **never multiplied into MRR** —
it is a diagnostic risk index, not a rate term.

Term 1, the large-particle tail
-------------------------------
Scratch count is linear in the *number* of particles above the critical size
(Remsen et al. 2006, doi:10.1149/1.2184036, Table V). Re-expressed on the D99
axis that becomes a power law with exponent `n` from the pack:

* ceria 1.44 — Hitachi US8439995B2, 4-point log-log regression, R^2 = 0.997
* tungsten 2.54 — Egan & Kim 2019, doi:10.1149/2.0311905jss
* copper 2.54 — transferred from tungsten (estimated)

`n` is *not* a material constant: it is a secant of a log-normal tail whose
local slope falls 8.4 -> 4.6 -> 0.7 across the Hitachi points. Swinging D99
across the threshold with a fixed `n` under-predicts below it and
over-predicts above it, and that is reported.

Term 2, agglomeration
---------------------
Basim & Moudgil 2002 (doi:10.1006/jcis.2002.8352) found that below the critical
coagulation concentration the *mean* size does not move while AFM Rmax doubles
(25 -> 50 nm). So there is a transient-agglomeration path D99 cannot see, kept
as an independent `1 + aggregate_ratio` term. It is a single-point basis, so
extrapolating the coefficient across chemistries is unverified.

Reported but deliberately not multiplied in
-------------------------------------------
* **Threshold position** `D99 / d_c` with `d_c` = 680 nm (Remsen 2006; Kwon
  2023 gives 700 nm; Eusner 2009 aggregates converge at 610/762 nm). Not a step
  term, because counts are non-zero below the threshold and most packs sit
  below it, which would clash with the "exactly 1.0 at reference" contract.
* **Scratch dimensions** from Saka 2008 (doi:10.1016/j.cirp.2008.03.098, Eqs.
  14-15) and Eusner 2009 (doi:10.1149/1.3121964, Eqs. 10-11):

      2 a_max = D99 sqrt(H_pad,max / H_film)
      delta_max = (D99 / 2) (H_pad,max / H_film)

  These set how *severe* a scratch is, and they depend on film hardness, which
  is why the same Delta means different damage on different films: Cu
  delta_max ~65 nm against W ~3 nm.

Limits
------
Absolute scratch counts are not predicted — published slopes differ by orders
of magnitude between systems. **Delta must not be compared across packs.**
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

import math

NAME = "defect_proxy"

#: FALLBACK critical particle size for scratching [nm] (Remsen 2006; Kwon 2023
#: 700 nm; Eusner 2009 aggregates 610/762 nm).
#:
#: This is the value used ONLY when the caller supplies none. Every shipped
#: pack declares its own ``scratch_threshold_nm`` with the same citation, and
#: ``evaluate`` now reads that. Before it did not: the module constant shadowed
#: the pack key entirely, so twelve packs carried a sourced number that could
#: not reach any output — the same failure mode as the withdrawn acid floor
#: (STATUS §26), and harder to see, because here the shadowed key and the
#: hardcoded value happened to be EQUAL. Nothing was wrong with any prediction;
#: what was wrong is that no future disagreement could have shown up. A
#: threshold is a property of the film and the abrasive (610 nm for one
#: aggregate population, 762 for another in the same paper), so it belongs to
#: the pack, and the constant here must be only the last resort.
SCRATCH_THRESHOLD_NM = 680.0

#: typical D99/D50 ratio when only D50 is known (Levitronix/Silco 2008,
#: secondary source). Reproduces Hitachi measured pairs only to 30-60%, so any
#: D99 derived this way is an estimate, not a measurement.
D99_OVER_D50_TYPICAL = 5.00


def d99_from_d50_nm(d50_nm: float) -> float:
    """Estimate D99 from D50 when no tail measurement exists."""
    return float(d50_nm) * D99_OVER_D50_TYPICAL


def tail_term(d99_nm: float, d99_ref_nm: float, exponent: float) -> float:
    """(D99/D99_ref)^n — the large-particle tail contribution."""
    if d99_ref_nm <= 0 or d99_nm <= 0:
        raise ValueError("particle sizes must be positive")
    return (float(d99_nm) / float(d99_ref_nm)) ** float(exponent)


def aggregation_term(aggregate_ratio: float) -> float:
    """1 + a — the agglomeration path D99 cannot see."""
    if aggregate_ratio < 0:
        raise ValueError("aggregate ratio must be non-negative")
    return 1.0 + float(aggregate_ratio)


def max_scratch_width_m(d99_nm: float, pad_hardness_pa: float,
                        film_hardness_pa: float) -> float:
    """2 a_max = D99 sqrt(H_pad / H_film)  [m]  (Saka 2008 Eq. 14)."""
    if film_hardness_pa <= 0 or pad_hardness_pa <= 0:
        raise ValueError("hardness values must be positive")
    return float(d99_nm) * 1e-9 * math.sqrt(float(pad_hardness_pa) / float(film_hardness_pa))


def max_scratch_depth_m(d99_nm: float, pad_hardness_pa: float,
                        film_hardness_pa: float) -> float:
    """delta_max = (D99/2) (H_pad / H_film)  [m]  (Saka 2008 Eq. 15)."""
    if film_hardness_pa <= 0 or pad_hardness_pa <= 0:
        raise ValueError("hardness values must be positive")
    return 0.5 * float(d99_nm) * 1e-9 * (float(pad_hardness_pa) / float(film_hardness_pa))


@dataclass
class DefectRisk:
    delta: float
    terms: Dict[str, float] = field(default_factory=dict)
    d99_nm: Optional[float] = None
    threshold_ratio: Optional[float] = None
    max_scratch_width_nm: Optional[float] = None
    max_scratch_depth_nm: Optional[float] = None
    active: bool = False
    notes: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    def as_dict(self) -> Dict[str, Any]:
        out: Dict[str, Any] = {
            "delta_risk_index": round(self.delta, 4),
            "active": self.active,
            "terms": {k: round(v, 4) for k, v in self.terms.items()},
            "notes": self.notes, "warnings": self.warnings,
        }
        if self.d99_nm is not None:
            out["d99_nm"] = round(self.d99_nm, 1)
        if self.threshold_ratio is not None:
            out["d99_over_scratch_threshold"] = round(self.threshold_ratio, 3)
        if self.max_scratch_width_nm is not None:
            out["max_scratch_width_nm"] = round(self.max_scratch_width_nm, 2)
        if self.max_scratch_depth_nm is not None:
            out["max_scratch_depth_nm"] = round(self.max_scratch_depth_nm, 2)
        return out


def evaluate(*, d99_nm: Optional[float], d99_ref_nm: Optional[float],
             exponent: Optional[float], aggregate_ratio: Optional[float] = None,
             d50_nm: Optional[float] = None,
             pad_hardness_pa: Optional[float] = None,
             film_hardness_pa: Optional[float] = None,
             scratch_threshold_nm: Optional[float] = None,
             film: str = "") -> DefectRisk:
    """Scratch-risk index relative to the pack's reference slurry."""
    notes: List[str] = []
    warnings: List[str] = []
    terms: Dict[str, float] = {}

    # The pack's own threshold wins; the module constant is the last resort.
    # See SCRATCH_THRESHOLD_NM for why this indirection exists.
    threshold_nm = (float(scratch_threshold_nm)
                    if scratch_threshold_nm and float(scratch_threshold_nm) > 0
                    else SCRATCH_THRESHOLD_NM)
    if scratch_threshold_nm is None:
        notes.append(
            f"no scratch_threshold_nm supplied: using the fallback "
            f"{SCRATCH_THRESHOLD_NM:.0f} nm (Remsen 2006 / Kwon 2023 / "
            "Eusner 2009). The threshold depends on film and abrasive, so a "
            "pack that declares its own overrides this")

    if d99_nm is None and d50_nm is not None:
        d99_nm = d99_from_d50_nm(d50_nm)
        warnings.append(
            f"no D99 measurement: estimated {d99_nm:.0f} nm as D50 x "
            f"{D99_OVER_D50_TYPICAL:g} (Levitronix/Silco secondary source). That "
            "ratio misses measured pairs by 30-60%, so this is an estimate. "
            "Scratches come from the tail, so a real particle-size distribution "
            "is the single most valuable input you can supply here")

    if d99_nm is None:
        return DefectRisk(
            delta=1.0, active=False,
            warnings=["defect proxy inactive: no large-particle tail (D99) and no "
                      "D50 to estimate it from. Mean size alone cannot predict "
                      "scratching — the 50-150 nm D50 of a normal slurry is far "
                      f"below the {threshold_nm:.0f} nm scratch threshold"])

    if exponent is None:
        return DefectRisk(
            delta=1.0, active=False, d99_nm=d99_nm,
            warnings=["defect proxy inactive: the pack declares no damage_exponent. "
                      "Published values are system-specific (ceria 1.44, tungsten "
                      "2.54) and must not be borrowed across chemistries"])

    ref = float(d99_ref_nm) if d99_ref_nm else float(d99_nm)
    terms["tail"] = tail_term(d99_nm, ref, exponent)
    notes.append(
        f"tail term (D99 {d99_nm:.0f} / ref {ref:.0f})^{float(exponent):.2f} = "
        f"{terms['tail']:.3f}")

    if aggregate_ratio is not None:
        terms["aggregation"] = aggregation_term(aggregate_ratio)
        notes.append(
            f"aggregation term 1 + {float(aggregate_ratio):g} = "
            f"{terms['aggregation']:.3f} (Basim & Moudgil 2002: mean size can stay "
            "flat while AFM Rmax doubles, a path D99 cannot see)")
    else:
        notes.append("aggregation path not declared by this pack — not investigated, "
                     "which is not the same as no effect")

    delta = 1.0
    for v in terms.values():
        delta *= v

    threshold_ratio = float(d99_nm) / threshold_nm
    notes.append(
        f"D99 / scratch threshold = {threshold_ratio:.2f} "
        f"(threshold {threshold_nm:.0f} nm, Remsen 2006 / Kwon 2023 / Eusner 2009)")
    if threshold_ratio > 1.0:
        warnings.append(
            f"D99 {d99_nm:.0f} nm exceeds the ~{threshold_nm:.0f} nm scratch "
            "threshold: this slurry has particles large enough to scratch, and "
            "filtration or better colloidal stability matters more than any rate tuning")
    if abs(math.log10(max(threshold_ratio, 1e-9))) < 0.2:
        warnings.append(
            "D99 sits close to the scratch threshold, where the log-normal tail's "
            "local slope changes fastest. A constant damage exponent is least "
            "reliable exactly here")

    width = depth = None
    if pad_hardness_pa and film_hardness_pa:
        width = max_scratch_width_m(d99_nm, pad_hardness_pa, film_hardness_pa) * 1e9
        depth = max_scratch_depth_m(d99_nm, pad_hardness_pa, film_hardness_pa) * 1e9
        notes.append(
            f"scratch dimension bounds on {film or 'this film'}: width <= {width:.1f} nm, "
            f"depth <= {depth:.1f} nm (Saka 2008 / Eusner 2009). Severity is set by "
            "film hardness, so the same risk index means different damage on "
            "different films")

    notes.append(
        "Delta is a relative risk index against this pack's reference slurry. It "
        "does not predict absolute scratch counts and must NOT be compared across packs")
    return DefectRisk(delta=delta, terms=terms, d99_nm=float(d99_nm),
                      threshold_ratio=threshold_ratio,
                      max_scratch_width_nm=width, max_scratch_depth_nm=depth,
                      active=True, notes=notes, warnings=warnings)
