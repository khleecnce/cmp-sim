"""P3 — Luo-Dornfeld abrasive mechanics: particle size, count and load.

Framework
---------
J. Luo, D. A. Dornfeld, "Material removal mechanism in chemical mechanical
polishing: theory and modeling", *IEEE Trans. Semicond. Manuf.* **14**, 112
(2001), doi:10.1109/66.920723. Removal is the product of how many particles are
cutting and how much each one cuts:

    MRR = N_active * Q_1 * V

Single-particle law (plastic indentation) — derived here, not asserted
----------------------------------------------------------------------
A rigid sphere of radius `R` pressed into a surface of hardness `H` by a load
`F`. Hardness is defined as load per plastically supported area, so

    A_c = F / H = pi a^2                 =>  a = sqrt(F / (pi H))

For a shallow spherical indent `a^2 = 2 R delta`, hence the indentation depth

    delta = a^2 / (2R) = F / (2 pi R H)              (*)

A particle dragged along cuts a groove whose cross-section scales as
`a * delta`, so the volume removed per unit sliding distance is

    Q_1 / V  ~  a * delta  ~  F^(1/2) H^(-1/2) * F R^(-1) H^(-1)
             =  F^(3/2) * R^(-1) * H^(-3/2)

Three consequences the rest of the simulator uses:

1. `alpha = 3/2` — load exponent of the single-particle law (plastic branch).
2. `beta = -1` — size exponent: at *fixed load per particle*, a smaller
   particle indents deeper and cuts more. The commonly quoted "bigger particles
   polish faster" comes from the count term, not this one, which is why size
   dependence is experimentally non-monotonic.
3. **MRR proportional to H^(-3/2)** — this is the single channel through which
   slurry chemistry reaches the mechanical model: chemistry softens the top
   layer, and `H` is the softened surface hardness, not the bulk value. The
   chemical layer (P4) therefore multiplies in through `H`, and must never
   touch the contact or kinematic terms.

Why the exponents are computed, not tabulated
---------------------------------------------
Writing `MRR ~ C^n_C * d^n_d` with fitted `n_C`, `n_d` is post-hoc description:
the numbers only apply to the slurry they were regressed on. The inherited
`legacy/sim/abrasive_mechanics.py` instead answers three measurable questions —
who carries the load (`chi`), is removal elastic or plastic (`alpha`), is
particle supply a monolayer or multilayer (`p`, `q`) — and the exponents follow
in closed form:

    n_C = p * (1 - alpha * chi)
    n_d = -q * (1 - alpha * chi) + beta

That module is wrapped here unchanged. Two of its structural results matter:

* `n_C <= 1` is an upper bound, because `p <= 1` and `0 <= (1 - alpha*chi) <= 1`.
  A literature exponent of 4/3 cannot arise inside this decomposition, so
  quoting it requires explaining what is outside the model.
* `n_C = 1/3` is *not* a "surface-area-limited" law as usually named; it is the
  signature of elastic contact (`alpha = 2/3`) with full load sharing
  (`chi = 1`).

Saturation
----------
A single power law in concentration cannot be right at both ends. With a finite
number of contact sites,

    N_active = n_s * (1 - exp(-C / C_half))

so the *apparent* exponent slides from 1 (dilute) to 0 (saturated) with no
change in physics. Where `C_half` is known this module uses the occupancy ratio
directly instead of a power law; where it is not, it uses a power law and says
so. High-concentration saturation is a headline requirement of P3 and is
reported either way.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

import math

from cmp_sim.core.legacy_bridge import install  # noqa: F401

from sim import abrasive_mechanics as am  # legacy/sim/abrasive_mechanics.py

NAME = "luo_dornfeld"

ALPHA_PLASTIC = am.ALPHA_PLASTIC      # 3/2
ALPHA_ELASTIC = am.ALPHA_ELASTIC      # 2/3
BETA_FOR_ALPHA = am.BETA_FOR_ALPHA


# ── single-particle mechanics (derivation above) ─────────────────────
def indentation_depth_m(load_n: float, particle_radius_m: float,
                        surface_hardness_pa: float) -> float:
    """delta = F / (2 pi R H)  [m], equation (*) above."""
    if particle_radius_m <= 0 or surface_hardness_pa <= 0:
        raise ValueError("particle radius and surface hardness must be positive")
    return float(load_n) / (2.0 * math.pi * float(particle_radius_m)
                            * float(surface_hardness_pa))


def contact_radius_m(load_n: float, surface_hardness_pa: float) -> float:
    """a = sqrt(F / (pi H))  [m] — plastic contact radius."""
    if surface_hardness_pa <= 0:
        raise ValueError("surface hardness must be positive")
    return math.sqrt(float(load_n) / (math.pi * float(surface_hardness_pa)))


def particles_per_unit_area(conc_vol_fraction: float, diameter_m: float) -> float:
    """Monolayer areal number density [1/m^2]: N ~ phi / d^2.

    A monolayer of spheres at volume fraction `phi` supplies of order
    `phi / d^2` particles per unit area (exact prefactor absorbed into the
    reference normalisation, which is why only ratios are used downstream).
    """
    if diameter_m <= 0:
        raise ValueError("particle diameter must be positive")
    return float(conc_vol_fraction) / (float(diameter_m) ** 2)


def load_per_particle_n(pressure_pa: float, n_per_area_m2: float) -> float:
    """F = P / N when the applied load is shared by all contacting particles."""
    if n_per_area_m2 <= 0:
        raise ValueError("particle areal density must be positive")
    return float(pressure_pa) / float(n_per_area_m2)


def single_particle_removal_rate(load_n: float, particle_radius_m: float,
                                 surface_hardness_pa: float) -> float:
    """Groove cross-section a*delta [m^2] — volume removed per unit slide.

    Proportional to F^(3/2) R^(-1) H^(-3/2); the geometric prefactor is
    absorbed by the reference normalisation.
    """
    a = contact_radius_m(load_n, surface_hardness_pa)
    d = indentation_depth_m(load_n, particle_radius_m, surface_hardness_pa)
    return a * d


# ── regime resolution (wraps the inherited decomposition) ────────────
@dataclass
class AbrasiveRegime:
    """The resolved exponents plus the reasoning that produced them."""
    chi: float
    alpha: float
    beta: float
    p: float
    q: float
    n_conc: float
    n_size: float
    confidence: str
    notes: List[str] = field(default_factory=list)

    def as_dict(self) -> Dict[str, Any]:
        return {"chi": round(self.chi, 4), "alpha": round(self.alpha, 4),
                "beta": round(self.beta, 4), "p": round(self.p, 4),
                "q": round(self.q, 4),
                "n_conc": round(self.n_conc, 4), "n_size": round(self.n_size, 4),
                "confidence": self.confidence, "notes": self.notes}


def beta_for_alpha(alpha: float) -> float:
    """Pair the single-particle size exponent with its load exponent.

    ``alpha`` and ``beta`` come from the same contact law and must not be
    chosen independently:

        plastic plowing   Q1 ~ F^1.5 / d        -> alpha = 3/2, beta = -1
        elastic (Hertz)   Q1 ~ F^(2/3) d^(2/3)  -> alpha = 2/3, beta = +2/3

    The inherited ``decide_alpha`` interpolates ``alpha`` in the transition
    band between the two branches, so ``beta`` is interpolated on the same
    coordinate. (Looking ``alpha`` up in a discrete table silently returns
    ``beta = 0`` there, which is not a physical law at all.)
    """
    a = float(alpha)
    a_lo, a_hi = ALPHA_ELASTIC, ALPHA_PLASTIC
    if a <= a_lo:
        return BETA_FOR_ALPHA[ALPHA_ELASTIC]
    if a >= a_hi:
        return BETA_FOR_ALPHA[ALPHA_PLASTIC]
    t = (a - a_lo) / (a_hi - a_lo)
    return (1.0 - t) * BETA_FOR_ALPHA[ALPHA_ELASTIC] + t * BETA_FOR_ALPHA[ALPHA_PLASTIC]


def _english_summary(reg, alpha_source: str) -> List[str]:
    """Report the decomposition in English.

    The inherited module explains itself in Korean; its prose is not passed
    through to the JSON output, so the same facts are restated here.
    """
    return [
        f"load sharing chi = {reg.chi:.3f} "
        + ("(particles share the applied load)" if reg.chi > 0.5
           else "(pad asperities carry the load; particles see a local load only)"),
        f"single-particle law: alpha = {reg.alpha:.3f}, beta = {reg.beta:.3f} ({alpha_source})",
        f"particle supply: p = {reg.p:.3f}, q = {reg.q:.3f}",
        f"computed exponents: n_C = p(1-alpha*chi) = {reg.n_conc:+.3f}, "
        f"n_d = -q(1-alpha*chi)+beta = {reg.n_size:+.3f}",
    ]


def resolve_regime(*, area_pressure_exponent: Optional[float] = None,
                   contact_stress_pa: Optional[float] = None,
                   surface_hardness_pa: Optional[float] = None,
                   gap_m: Optional[float] = None,
                   particle_diameter_m: Optional[float] = None
                   ) -> AbrasiveRegime:
    """Answer the three questions -> exponents. Inherited implementation."""
    alpha_probe, alpha_conf = am.decide_alpha(contact_stress_pa,
                                              surface_hardness_pa, [])
    if alpha_probe >= ALPHA_PLASTIC - 1e-9:
        alpha_source = "plastic plowing branch"
    elif alpha_probe <= ALPHA_ELASTIC + 1e-9:
        alpha_source = "elastic Hertz branch"
    else:
        alpha_source = ("elastic-plastic transition band — interpolated, and no "
                        "single contact law strictly applies here")

    reg = am.resolve_regime(
        area_pressure_exponent=area_pressure_exponent,
        contact_stress_pa=contact_stress_pa,
        surface_hardness_pa=surface_hardness_pa,
        gap_m=gap_m, d_p_m=particle_diameter_m,
        beta=beta_for_alpha(alpha_probe),
    )
    notes = _english_summary(reg, alpha_source)
    if alpha_conf == "unverified":
        notes.append(
            "alpha undetermined: the per-particle contact stress or the softened "
            "surface hardness is unknown, so the elastic/plastic branch was not "
            "decided from data (the elastic branch is assumed)")
    if reg.n_conc > 1.0 + 1e-9:
        notes.append(
            f"computed n_C = {reg.n_conc:.3f} exceeds the structural upper bound of 1; "
            "since p <= 1 and 0 <= (1-alpha*chi) <= 1, the inputs are inconsistent")
    return AbrasiveRegime(
        chi=reg.chi, alpha=reg.alpha, beta=reg.beta, p=reg.p, q=reg.q,
        n_conc=reg.n_conc, n_size=reg.n_size, confidence=reg.confidence,
        notes=notes)


def occupancy_ratio(conc: float, conc_ref: float,
                    conc_half: Optional[float]) -> Optional[float]:
    """Saturating concentration ratio (1-exp) — ``None`` if C_half is unknown."""
    if conc_half is None:
        return None
    return am.occupancy_ratio(float(conc), float(conc_ref), float(conc_half))


def apparent_conc_exponent(conc: float, conc_half: Optional[float]) -> Optional[float]:
    """Local d(ln N)/d(ln C) of the occupancy model: 1 dilute -> 0 saturated."""
    if conc_half is None:
        return None
    return am.occupancy_exponent(float(conc), float(conc_half))


# ── the Kp multiplier ────────────────────────────────────────────────
SATURATION_NOTE = (
    "concentration handled by the site-occupancy model N ~ 1-exp(-C/C_half), "
    "which saturates; a single power law would keep rising without bound")


def mechanical_factor(*, conc: Optional[float], conc_ref: Optional[float],
                      diameter_nm: Optional[float], diameter_ref_nm: Optional[float],
                      regime: AbrasiveRegime,
                      conc_half: Optional[float] = None,
                      hardness_pa: Optional[float] = None,
                      hardness_ref_pa: Optional[float] = None
                      ) -> Tuple[float, List[str], List[str]]:
    """Dimensionless Kp multiplier from abrasive loading, size and film hardness.

    Exactly 1.0 when the slurry equals the pack's reference slurry, so a
    literature-calibrated Kp is never rescaled by default.
    """
    notes: List[str] = list(regime.notes)
    warnings: List[str] = []
    factor = 1.0

    # concentration
    if conc is not None and conc_ref:
        occ = occupancy_ratio(conc, conc_ref, conc_half)
        if occ is not None:
            factor *= occ
            n_app = apparent_conc_exponent(conc, conc_half)
            notes.append(
                f"concentration {conc:g} vs reference {conc_ref:g} (C_half={conc_half:g}): "
                f"occupancy ratio {occ:.4f}; apparent local exponent {n_app:.3f}. "
                + SATURATION_NOTE)
            if n_app is not None and n_app < 0.2:
                warnings.append(
                    f"abrasive concentration {conc:g} is deep in saturation "
                    f"(apparent exponent {n_app:.2f}); adding more particles will "
                    "barely change the rate, and the model's sensitivity there is low")
        else:
            ratio = (float(conc) / float(conc_ref)) ** regime.n_conc
            factor *= ratio
            notes.append(
                f"concentration {conc:g} vs reference {conc_ref:g}: power law with "
                f"computed n_C = {regime.n_conc:.3f} -> {ratio:.4f}")
            warnings.append(
                "no saturation concentration (C_half) available for this slurry, so a "
                "single power law is used; it cannot saturate and will over-predict "
                "at high loading. Supply C_half to fix this.")

    # particle size
    if diameter_nm is not None and diameter_ref_nm:
        ratio = (float(diameter_nm) / float(diameter_ref_nm)) ** regime.n_size
        factor *= ratio
        notes.append(
            f"particle size {diameter_nm:g} nm vs reference {diameter_ref_nm:g} nm: "
            f"computed n_d = {regime.n_size:.3f} -> {ratio:.4f} "
            "(sign is regime-dependent: count and depth terms oppose each other)")
        if abs(regime.n_size) < 1e-6 and abs(float(diameter_nm) - float(diameter_ref_nm)) > 1e-9:
            notes.append(
                "size cancellation: in the elastic, fully load-sharing monolayer "
                "regime n_d = -q(1-alpha*chi)+beta = -2(1-2/3)+2/3 = 0 exactly. "
                "Smaller particles are more numerous but each carries less load, "
                "and the two effects cancel — so size-independence here is a "
                "structural prediction, NOT the input being ignored. Measured "
                "size dependence in this regime therefore indicates something "
                "outside the model (aggregation, size-dependent chemistry, or a "
                "different contact branch).")
        if regime.confidence == "unverified":
            warnings.append(
                "the particle-size term rests on an undetermined contact branch; "
                "supply the per-particle contact stress and the softened surface "
                "hardness to decide elastic vs plastic, which is what sets n_d's sign")

    # chemically softened surface hardness — the chemistry coupling channel
    if hardness_pa and hardness_ref_pa:
        ratio = (float(hardness_ref_pa) / float(hardness_pa)) ** 1.5
        factor *= ratio
        notes.append(
            f"surface hardness {hardness_pa:.3e} Pa vs reference {hardness_ref_pa:.3e} Pa: "
            f"MRR ~ H^-1.5 -> {ratio:.4f} (chemistry enters mechanics only here)")

    if regime.confidence in ("unverified", "estimated"):
        warnings.append(
            f"abrasive regime confidence is '{regime.confidence}': at least one of "
            "load sharing, elastic/plastic branch or supply geometry was not "
            "determined from data, so the exponents are structural estimates")
    return factor, notes, warnings
