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
    #: True when the supply question (p, q) was DECIDED rather than defaulted.
    #: Kept separate from ``confidence``, which is the minimum over all three
    #: axes: a decided supply must not be able to raise an overall grade that
    #: chi or alpha is still holding down, and an undecided chi must not make
    #: the run claim the supply axis is open when it is not.
    supply_decided: bool = False
    notes: List[str] = field(default_factory=list)

    def as_dict(self) -> Dict[str, Any]:
        return {"chi": round(self.chi, 4), "alpha": round(self.alpha, 4),
                "beta": round(self.beta, 4), "p": round(self.p, 4),
                "q": round(self.q, 4),
                "n_conc": round(self.n_conc, 4), "n_size": round(self.n_size, 4),
                "confidence": self.confidence,
                "supply_decided": self.supply_decided, "notes": self.notes}


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


def _supply_from_lubrication(lubrication: Optional[str]
                             ) -> Tuple[Optional[str], str]:
    """Decide the SUPPLY question from the lubrication regime, not from a gap.

    The third regime question (``legacy/sim/abrasive_mechanics.decide_supply``)
    asks whether the pad-wafer gap admits ONE layer of particles or several,
    because that sets ``p`` and ``q`` in

        n_C = p (1 - alpha*chi),    n_d = -q (1 - alpha*chi) + beta

    It is answered from ``gap_m / d_p``, and the solver hands it
    ``pad_wafer_gap_m`` — a key no pack declares and no caller sets (it is in
    ``tests/test_pack_key_wiring.KNOWN_NON_PACK_KEYS`` as "solved quantity").
    So the decision was NEVER MADE in any run of this corpus: every call took
    the ``None`` branch, which returns the monolayer values with confidence
    ``estimated`` and announces "the pad-wafer gap is unknown".

    THE MEAN FLUID FILM IS NOT THAT GAP, and substituting it would be a bug
    -----------------------------------------------------------------------
    The same run already solves a mean fluid film thickness ``h`` from sourced
    lubrication physics and publishes it under ``slurry_supply``. It is
    tempting to feed that to ``gap_m``, and it is wrong. ``decide_supply``'s
    gap is the clearance at the place where particles are LOADED — between a
    pad asperity summit and the wafer — whereas ``h`` is averaged over the
    whole wafer including the grooves and the un-contacted valleys.

    Which of the two applies is exactly what the lambda ratio decides
    (``lambda = h / sigma_pad``, Bhushan):

    * ``lambda < 1`` (boundary): the fluid film is THINNER than the pad
      roughness. Asperities touch the wafer and carry the load, and a particle
      is only loaded where it is trapped in such a contact — so the local
      clearance there is one particle diameter by definition and the supply is
      a MONOLAYER. ``p = 1, q = 2`` is then a derived result, not an
      assumption, and the confidence is that of the lubrication solve.
    * ``lambda >= 1`` (mixed / full film): part or all of the load is carried
      hydrodynamically, the clearance at a loaded site is no longer pinned to
      the particle, and this argument does NOT license a verdict. The axis
      stays undetermined and says so.

    Measured on this corpus (``tools/supply_gap_probe.py``): all 49 runnable
    datasets are boundary, ``lambda`` 0.002..0.148, every one below 1 by at
    least a factor of 6.7 — so the monolayer branch is decided everywhere here,
    and the "unknown gap" note was never true.

    What would have happened with the naive wiring is worth recording, because
    it is the failure this function exists to avoid: ``h/d`` exceeds
    ``decide_supply``'s 1.5 threshold on 20 of those 49 datasets (up to 26x),
    which would have cut ``p`` from 1.0 to 0.46 and HALVED every derived
    concentration exponent on a third of the corpus — on the strength of a
    quantity measured in the wrong place. And it would have been nearly
    invisible: only 5 of 49 predicted rates move at all when the supply branch
    is forced, because each pack's own measured exponent overrides the derived
    one (``tools/supply_gap_reachability_probe.py``). A wrong number that
    changes almost nothing is the hardest kind to find later.

    Returns ``(verdict, why)`` where ``verdict`` is ``"monolayer"`` or ``None``.
    """
    lub = str(lubrication or "").lower()
    if lub == "boundary":
        return ("monolayer",
                "supply DECIDED as monolayer from the lubrication regime: "
                "lambda = h/sigma < 1, so the fluid film is thinner than the "
                "pad roughness, asperities carry the load, and a particle is "
                "loaded only where it is trapped in an asperity contact — "
                "where the clearance is one particle diameter by definition. "
                "p = 1, q = 2 is therefore derived, not assumed. The MEAN "
                "fluid film is deliberately not used as the gap: it is "
                "averaged over grooves and un-contacted valleys, and on this "
                "corpus it would wrongly report multilayer on 20 of 49 runs")
    if lub in ("mixed", "full_film", "full-film", "fullfilm"):
        return (None,
                f"supply still UNDETERMINED: lubrication is '{lub}', so part "
                "or all of the load is carried hydrodynamically and the "
                "clearance at a loaded site is no longer pinned to the "
                "particle diameter. The monolayer argument is licensed only "
                "in boundary lubrication and is not extrapolated here")
    return (None, "")


def resolve_regime(*, area_pressure_exponent: Optional[float] = None,
                   contact_stress_pa: Optional[float] = None,
                   surface_hardness_pa: Optional[float] = None,
                   gap_m: Optional[float] = None,
                   particle_diameter_m: Optional[float] = None,
                   contact_branch: Optional[str] = None,
                   lubrication: Optional[str] = None,
                   ) -> AbrasiveRegime:
    """Answer the three questions -> exponents. Inherited implementation.

    ``contact_branch`` is the non-circular route to alpha. The inherited
    ``decide_alpha`` needs a per-particle contact stress, which Luo-Dornfeld
    *defines* as the film hardness — so sourcing it independently is circular
    and it is null in every pack. The pad-limited load criterion in
    ``core.regime`` decides the same branch from the measured pad hardness, the
    film modulus and the film hardness, with particle size cancelling out. When
    it has reached a verdict, that verdict sets alpha directly.

    ``lubrication`` is the same kind of route to the SUPPLY question (p, q).
    See ``_supply_from_lubrication`` for the derivation and for why the mean
    fluid film must NOT be handed to ``gap_m`` instead.
    """
    branch_alpha = {"plastic": ALPHA_PLASTIC, "elastic": ALPHA_ELASTIC}
    from_branch = branch_alpha.get(str(contact_branch or "").lower())
    if from_branch is not None:
        alpha_probe, alpha_conf = from_branch, "literature"
        alpha_source = (
            f"{'plastic plowing' if from_branch == ALPHA_PLASTIC else 'elastic Hertz'}"
            " branch, from the pad-limited load criterion (measured pad "
            "hardness vs the film's modulus and hardness; particle size "
            "cancels) rather than from a particle contact stress, which "
            "Luo-Dornfeld defines as the hardness and so cannot be sourced "
            "independently")
    elif str(contact_branch or "").lower() == "transition":
        alpha_probe = 0.5 * (ALPHA_ELASTIC + ALPHA_PLASTIC)
        alpha_conf = "estimated"
        alpha_source = (
            "elastic-plastic transition band from the pad-limited load "
            "criterion: this film sits within 3x of the boundary, where the "
            "measured spread in pad hardness (s.d. as large as the mean) means "
            "different asperities put particles on different sides. Alpha is "
            "the midpoint and no single contact law strictly applies")
    else:
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

    # ── the SUPPLY question, answered where the gap is unknown ───────────
    # The inherited layer takes the gap route and, with no gap, returns the
    # monolayer values while declaring the axis undecided. The lubrication
    # regime decides the SAME question from a quantity the run does solve.
    # See _supply_from_lubrication for the derivation and for why the mean
    # fluid film must not simply be substituted for the gap.
    supply_verdict = None
    if gap_m is None:
        supply_verdict, supply_why = _supply_from_lubrication(lubrication)
        if supply_why:
            notes.append(supply_why)
        if supply_verdict == "monolayer":
            # The VALUES do not change (p=1, q=2 either way); what changes is
            # that they are now a derived result rather than a stated
            # assumption, so the regime no longer floors its own confidence on
            # an axis it has in fact decided. Nothing else may be upgraded
            # here: chi and alpha have their own evidence.
            import dataclasses as _dc
            assert reg.p == am.P_MONOLAYER and reg.q == am.Q_MONOLAYER, (
                "the inherited no-gap fallback is no longer the monolayer "
                f"pair (p={reg.p}, q={reg.q}); the derivation in "
                "_supply_from_lubrication agrees with p=1, q=2 only")
            if reg.confidence == "estimated":
                reg = _dc.replace(reg, confidence="literature")

    # The inherited resolve_regime recomputes alpha internally from the contact
    # stress (legacy/sim/abrasive_mechanics.py, decide_alpha), so it discards
    # the branch decided above and keeps only the beta derived from it. Rather
    # than editing the legacy module or duplicating its algebra, a LoadRegime is
    # rebuilt with the corrected alpha and ITS OWN n_conc/n_size properties are
    # read back — so the exponent relations stay defined in exactly one place.
    if from_branch is not None or str(contact_branch or "").lower() == "transition":
        import dataclasses

        corrected = dataclasses.replace(
            reg, alpha=alpha_probe, beta=beta_for_alpha(alpha_probe))
        notes.append(
            f"alpha was set to {corrected.alpha:.4f} by the pad-limited load "
            f"criterion, replacing the {reg.alpha:.4f} the inherited layer "
            "computes from a particle contact stress that no pack can source "
            f"non-circularly. {corrected.explain()}")
        # STRUCTURAL CONSISTENCY. The exponent relations assume
        # 0 <= 1 - alpha*chi <= 1. The plastic branch (alpha = 3/2) violates
        # that whenever chi > 2/3: full single-layer load sharing plus plastic
        # indentation gives a NEGATIVE concentration exponent, i.e. "more
        # abrasive removes less", which the model's own bound forbids.
        #
        # This is a real incompatibility between two axes, not a rounding
        # detail, and the honest response is to refuse the combination rather
        # than publish n_C < 0. chi comes from the measured area-pressure
        # exponent, so the two cannot simply be overridden independently.
        product = corrected.alpha * corrected.chi
        if product > 1.0 + 1e-9:
            notes.append(
                f"the pad-limited criterion says {contact_branch} "
                f"(alpha = {corrected.alpha:.3f}) but the measured load sharing "
                f"gives chi = {corrected.chi:.3f}, and alpha*chi = "
                f"{product:.3f} > 1 breaks the structural bound "
                "0 <= 1-alpha*chi <= 1 that the exponent relations rest on. "
                "Taken literally it would mean more abrasive removes less. "
                "The branch is reported but the EXPONENTS are left on the "
                "inherited elastic values, because alpha and chi are not "
                "independently adjustable: chi is derived from the measured "
                "area-pressure exponent, and a plastic branch with near-total "
                "load sharing is outside the model's validity. Resolving it "
                "needs a measured concentration sweep for this film")
            corrected = dataclasses.replace(
                corrected, alpha=reg.alpha, beta=reg.beta,
                confidence="unverified")
        # The legacy confidence was floored by its own undetermined alpha; that
        # axis is now decided, so the floor comes from chi and supply instead.
        elif corrected.confidence == "unverified" and alpha_conf != "unverified":
            order = ["unverified", "estimated", "literature", "measured", "verified"]
            others = [c for c in (getattr(corrected, "chi_confidence", None),
                                  getattr(corrected, "supply_confidence", None))
                      if c in order]
            corrected = dataclasses.replace(
                corrected, confidence=(min(others, key=order.index) if others
                                       else alpha_conf))
        reg = corrected
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
        supply_decided=(supply_verdict is not None or gap_m is not None),
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
                      hardness_ref_pa: Optional[float] = None,
                      measured_size_exponent: Optional[float] = None,
                      measured_conc_exponent: Optional[float] = None,
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
            # LOAD SHARING APPLIES TO THE SATURATING BRANCH TOO.
            #
            # `occ` is the ratio of ACTIVE PARTICLE COUNTS, N(C)/N(C_ref). It is
            # not the rate ratio. This module's own derivation (see the header)
            # gives the rate as
            #
            #     MRR ~ N * F_particle^alpha,   F_particle = chi * P / N
            #     =>  MRR ~ N^(1 - alpha*chi)
            #
            # which is exactly where the power-law branch's exponent
            # n_C = p * (1 - alpha*chi) comes from, with N ~ C^p. Raising `occ`
            # to the first power therefore sets (1 - alpha*chi) = 1, i.e. it
            # asserts chi = 0 (every particle carries a load INDEPENDENT of how
            # many others are present) — the opposite of the load sharing the
            # same call has just resolved, and a claim no branch of the
            # decomposition can produce. The two branches described the same
            # physics with different exponents: the saturating branch was
            # steeper than the power law it replaced.
            #
            # MEASURED: on the four iso-condition silica-on-oxide loading series
            # of US9499721B2 the model's log-log slope was +0.85 against a
            # measured +0.15..+0.53, i.e. it reproduced the very "+1.0, keeps
            # rewarding abrasive" behaviour C_half was introduced to remove.
            # With the load-sharing exponent restored it is +0.33, inside the
            # measured band, and that dataset's shape error falls 22.9% -> 8.2%.
            #
            # No constant is added: the exponent is (1 - alpha*chi) = n_C / p,
            # read from the regime this call already resolved. p = 0 (no
            # particle-supply response at all) would make that undefined, and in
            # that case the count does not respond to loading either, so the
            # occupancy ratio carries no information and is left at 1.0.
            share = (regime.n_conc / regime.p) if regime.p else 0.0
            # Structural bound: 0 <= 1 - alpha*chi <= 1 (see header). Clamping
            # keeps a pathological pack from inverting the sign of the axis.
            share = min(1.0, max(0.0, float(share)))
            occ = float(occ) ** share
            factor *= occ
            n_app = apparent_conc_exponent(conc, conc_half)
            if n_app is not None:
                n_app *= share
            notes.append(
                f"concentration {conc:g} vs reference {conc_ref:g} (C_half={conc_half:g}): "
                f"occupancy ratio {occ:.4f} (count ratio raised to the "
                f"load-sharing exponent 1-alpha*chi = {share:.3f}); apparent "
                f"local exponent {n_app:.3f}. " + SATURATION_NOTE)
            if n_app is not None and n_app < 0.2:
                warnings.append(
                    f"abrasive concentration {conc:g} is deep in saturation "
                    f"(apparent exponent {n_app:.2f}); adding more particles will "
                    "barely change the rate, and the model's sensitivity there is low")
        else:
            # A MEASURED exponent beats the derived one, exactly as for size.
            # Without this the pack's own sourced value was READ AND IGNORED:
            # sti_ceria carries abrasive_conc_exponent = -0.43 from Dandu 2009
            # Fig. 2a ("0.25% ceria gave HIGHER oxide RR than 0.5 and 1%"), yet
            # the model applied a positive derived exponent and returned MORE
            # rate for MORE ceria -- the opposite sign to the measurement the
            # pack cites, and 21,004 A/min against a 200-6,000 published band.
            n_conc = regime.n_conc
            if measured_conc_exponent is not None:
                n_conc = float(measured_conc_exponent)
                notes.append(
                    f"concentration exponent n_C = {n_conc:+.3f} taken from a "
                    f"MEASURED sweep in this pack, overriding the derived "
                    f"{regime.n_conc:+.3f}. The derivation assumes more "
                    "particles means more cutting points; in a ceria system "
                    "that is chemically rate-limited the measurement can go "
                    "the other way")
            ratio = (float(conc) / float(conc_ref)) ** n_conc
            factor *= ratio
            notes.append(
                f"concentration {conc:g} vs reference {conc_ref:g}: power law with "
                f"n_C = {n_conc:.3f} -> {ratio:.4f}")
            warnings.append(
                "no saturation concentration (C_half) available for this slurry, so a "
                "single power law is used; it cannot saturate and will over-predict "
                "at high loading. Supply C_half to fix this.")

    # particle size
    if diameter_nm is not None and diameter_ref_nm:
        # A MEASURED exponent beats the derived one. The derivation gives a
        # single number from alpha, beta, chi and q, but ten measured sweeps
        # show the exponent belongs to the ABRASIVE rather than to the film:
        #
        #   ceria    n = +0.87  (3 sweeps,  3-211 nm, oxide)
        #   alumina  n = +0.29  (2 sweeps, 50-3500 nm, Cu and SiC)
        #   silica   n = -0.05  (5 sweeps, 12-160 nm, five different films)
        #
        # Within one abrasive the sweeps agree; across abrasives they do not
        # share a sign. Ceria removes silica chemically at the contact (Cook
        # 1990: one SiO2 molecule per 24 collisions against one per 5e8 for
        # silica), so a larger ceria particle carries a proportionally larger
        # reacted footprint. Silica abrades mechanically - the regime this
        # derivation assumes, where the size dependence cancels - which is why
        # the derived value is right for silica and wrong by a sign for ceria.
        n_size = regime.n_size
        if measured_size_exponent is not None:
            n_size = float(measured_size_exponent)
            notes.append(
                f"particle-size exponent n_d = {n_size:+.3f} taken from "
                f"MEASURED sweeps for this abrasive, overriding the derived "
                f"{regime.n_size:+.3f}. The derivation yields one number from "
                "the contact branch and load sharing, and it assumes purely "
                "mechanical indentation; measured exponents run -0.45 to +1.0 "
                "and split cleanly by abrasive (ceria +0.87, alumina +0.29, "
                "silica -0.05), so one value cannot hold everywhere")
        ratio = (float(diameter_nm) / float(diameter_ref_nm)) ** n_size
        factor *= ratio
        notes.append(
            f"particle size {diameter_nm:g} nm vs reference {diameter_ref_nm:g} nm: "
            f"n_d = {n_size:.3f} -> {ratio:.4f} "
            "(sign is regime-dependent: count and depth terms oppose each other)")
        if abs(n_size) < 1e-6 and abs(float(diameter_nm) - float(diameter_ref_nm)) > 1e-9:
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
        # Name only the axes that are ACTUALLY open. The blanket wording
        # ("load sharing, elastic/plastic branch or supply geometry") was
        # accurate when none of the three could be decided; now that the
        # supply axis is derived from the lubrication regime, listing it
        # anyway would report a gap that has been closed — the same class of
        # untrue statement that the gap wiring itself fixed.
        open_axes = ["load sharing", "elastic/plastic branch"]
        if not regime.supply_decided:
            open_axes.append("supply geometry")
        warnings.append(
            f"abrasive regime confidence is '{regime.confidence}': at least one of "
            + ", ".join(open_axes[:-1]) + f" or {open_axes[-1]}"
            + " was not determined from data, so the exponents are structural "
              "estimates"
            + ("" if not regime.supply_decided else
               ". The supply geometry is NOT among them: it was decided as a "
               "monolayer from the lubrication regime"))
    return factor, notes, warnings
