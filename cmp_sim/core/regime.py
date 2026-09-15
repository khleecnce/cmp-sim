"""Situation detection — which physical regime is this run actually in?

Why this exists
---------------
Which model is appropriate is not a property of the *film*; it is a property of
the *situation*. SiC and sapphire are different films in the same regime (hard,
chemically rate-limited). Cu at 1.5 psi and Cu at 4 psi are the same film in
different regimes — and US6918821B2 shows Preston fits one and not the other.

So the simulator classifies the run from computable physical quantities, then
recommends the model bundle that suits it and complains when the chosen bundle
does not. Nothing here is declared by the user; it is all derived.

Axes
----
``contact_branch``    elastic / plastic / transition
    From the single-particle contact stress against the softened surface
    hardness. This is what sets alpha and beta in P3, so it decides whether the
    Hertz or the plowing law applies.

``asperity_regime``   elastic / plastic  (pad summits, not particles)
    Plasticity index psi = (E*/H) sqrt(sigma/R). Above ~1 the summits flow
    plastically and the Greenwood-Williamson load-independent result fails.

``load_regime``       unsaturated / saturated
    Fraction of pad summits in contact. Past ~50% the exponential-tail result
    that underwrites Preston's pressure linearity no longer holds.

``lubrication``       boundary / mixed / full_film
    lambda = h_film / roughness. CMP must be boundary-lubricated; a full film
    means the abrasive never reaches the wafer and removal collapses.

``film_class``        soft_metal / metal / dielectric / hard_ceramic
    By bulk hardness, because hardness is what the mechanics actually sees.

``rate_limit``        mechanical / mixed / chemical
    Hard, chemically inert films are chemically limited: a P*V law cannot
    explain them no matter how Kp is chosen.

``topography``        blanket / patterned
``pad_state``         fresh / worn
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

# ── thresholds, with their basis ─────────────────────────────────────
#: particle contact stress / surface hardness: below this the contact is elastic
ELASTIC_STRESS_RATIO = 0.5
#: at or above this it is fully plastic (hardness = load per plastic area)
PLASTIC_STRESS_RATIO = 1.0
#: plasticity index above which pad asperities flow plastically (Greenwood-Williamson 1966)
PLASTICITY_INDEX_LIMIT = 1.0
#: summit-contact fraction above which the GW exponential-tail result is void
SATURATION_LIMIT = 0.50
#: lambda = h/sigma regime boundaries (Bhushan, Introduction to Tribology)
LAMBDA_BOUNDARY = 1.0
LAMBDA_FULL_FILM = 3.0
#: film hardness class boundaries [Pa]
HARDNESS_SOFT = 2.0e9            # Cu ~1 GPa, SnAg ~0.2 GPa
HARDNESS_HARD_CERAMIC = 15.0e9   # SiC ~25-30 GPa, sapphire ~20 GPa

#: Hardness alone cannot separate a metal from a dielectric: W (~4-7 GPa) and
#: thermal oxide (~7-9 GPa) overlap, yet they polish by different mechanisms
#: (oxidise-then-abrade vs hydrolyse-then-abrade) and need different chemistry.
#: Material family therefore comes from the pack or the film name, and hardness
#: only splits soft/hard WITHIN a family.
METAL_FILMS = {"cu", "w", "co", "ru", "ta", "tan", "ti", "tin", "al", "snag", "ni", "pt"}
DIELECTRIC_FILMS = {"oxide", "sti", "oxide_ceria", "teos", "peteos", "bpsg",
                    "sin", "sion", "low_k", "quartz", "glass"}
SEMICONDUCTOR_FILMS = {"poly_si", "si", "sic", "ge", "sige", "gan", "sapphire"}


def _pad_limited_branch(resolved, h_surf, h_bulk, s) -> Optional[float]:
    """Decide elastic vs plastic from the pad-limited load, without a particle
    contact stress. Sets ``s.contact_branch`` and returns Lambda, or None if
    the inputs are absent.

    Lambda = 48 * Hp * Ec^2 / (pi^2 * Hc^3)   > 1 means plastic

    from P_max = pi R^2 Hp against P_Y = (pi^3/48) Hc^3/Ec^2 R^2 (Hertz +
    Tresca, Saka 2008 CIRP Eq. 3 and Eusner 2009 JES Eq. 3). R cancels, so the
    branch is particle-size independent.

    Non-circular because Hp is the PAD hardness, measured directly by
    nanoindentation of a wet pad, whereas the particle contact stress is
    *defined* as the film hardness in the Luo-Dornfeld formulation.
    """
    h_pad = resolved.p_or("pad_wet_nanohardness_pa", None)
    modulus = resolved.p_or("film_youngs_modulus_pa", None)
    hardness = h_surf or h_bulk
    if not (h_pad and modulus and hardness):
        return None

    h_pad = float(h_pad)
    modulus = float(modulus)
    hardness = float(hardness)
    lam = 48.0 * h_pad * modulus ** 2 / (math.pi ** 2 * hardness ** 3)

    # Near 1.0 the criterion is a coin toss and the measured pad hardness has a
    # standard deviation comparable to its mean (0.05 +/- 0.06 GPa), so a band
    # rather than a hard threshold.
    if lam > 3.0:
        s.contact_branch = "plastic"
    elif lam < 0.33:
        s.contact_branch = "elastic"
    else:
        s.contact_branch = "transition"

    s.metrics["pad_limited_plasticity_lambda"] = round(lam, 4)
    which = "surface" if h_surf else "bulk"
    s.notes.append(
        f"contact branch from the pad-limited load criterion: Lambda = "
        f"{lam:.3g} (pad hardness {h_pad/1e9:.3g} GPa, film modulus "
        f"{modulus/1e9:.3g} GPa, {which} hardness {hardness/1e9:.3g} GPa) "
        f"-> {s.contact_branch}. Particle size cancels out of this criterion")
    if not h_surf:
        s.undetermined.append(
            "contact_branch was decided from BULK rather than surface hardness "
            f"(Lambda = {lam:.3g}). Chemistry moves the surface hardness of one "
            "metal across two orders of magnitude, and Lambda goes as 1/Hc^3, "
            "so a 2x error in hardness is an 8x error in Lambda. The branch is "
            "reported but a surface measurement would be worth having")
    if 0.33 <= lam <= 3.0:
        # Independent of the hardness caveat above: a marginal Lambda needs
        # saying even when the hardness is well sourced, and especially when it
        # is not, since the two uncertainties compound.
        s.undetermined.append(
            f"contact_branch is marginal (Lambda = {lam:.3g}, within 3x of the "
            "elastic/plastic boundary). The pad hardness this rests on has a "
            "standard deviation as large as its mean across 36 measurements of "
            "one pad, so this film sits where the branch genuinely depends on "
            "which asperity a particle happens to meet")
    return lam


@dataclass
class Situation:
    """The regime this run is in, derived from the recipe."""
    contact_branch: str = "unknown"
    asperity_regime: str = "unknown"
    load_regime: str = "unknown"
    lubrication: str = "unknown"
    film_class: str = "unknown"
    rate_limit: str = "unknown"
    topography: str = "blanket"
    pad_state: str = "fresh"
    metrics: Dict[str, float] = field(default_factory=dict)
    notes: List[str] = field(default_factory=list)
    undetermined: List[str] = field(default_factory=list)

    def as_dict(self) -> Dict[str, Any]:
        return {
            "contact_branch": self.contact_branch,
            "asperity_regime": self.asperity_regime,
            "load_regime": self.load_regime,
            "lubrication": self.lubrication,
            "film_class": self.film_class,
            "rate_limit": self.rate_limit,
            "topography": self.topography,
            "pad_state": self.pad_state,
            "metrics": {k: round(float(v), 5) for k, v in self.metrics.items()},
            "notes": self.notes,
            "undetermined": self.undetermined,
        }


def material_family(film: str, pack_family: Optional[str] = None) -> str:
    """metal / dielectric / semiconductor, from the pack or the film name."""
    if pack_family:
        return str(pack_family).strip().lower()
    f = str(film).strip().lower()
    if f in METAL_FILMS:
        return "metal"
    if f in DIELECTRIC_FILMS:
        return "dielectric"
    if f in SEMICONDUCTOR_FILMS:
        return "semiconductor"
    return "unknown"


def classify_film(hardness_pa: Optional[float], film: str = "",
                  pack_family: Optional[str] = None) -> str:
    """Family first, hardness second.

    Hardness alone puts W and thermal oxide in the same bin even though they
    remove by different mechanisms, so the family decides the class and
    hardness only splits soft from hard inside it.
    """
    family = material_family(film, pack_family)
    h = float(hardness_pa) if hardness_pa else None

    if family == "metal":
        if h is None:
            return "metal"
        return "soft_metal" if h < HARDNESS_SOFT else "metal"
    if family == "dielectric":
        return "dielectric"
    if family == "semiconductor":
        if h is None:
            return "semiconductor"
        return "hard_ceramic" if h >= HARDNESS_HARD_CERAMIC else "semiconductor"

    # Unknown family: fall back to hardness, and say the class is uncertain.
    if h is None:
        return "unknown"
    if h < HARDNESS_SOFT:
        return "soft_metal"
    return "hard_ceramic" if h >= HARDNESS_HARD_CERAMIC else "dielectric"


def classify_contact_branch(stress_pa: Optional[float],
                            hardness_pa: Optional[float]) -> str:
    """Elastic vs plastic single-particle contact.

    Undetermined when either quantity is missing — the softened surface hardness
    in particular is rarely published, and guessing it would silently decide the
    exponents in P3.
    """
    if not stress_pa or not hardness_pa:
        return "unknown"
    ratio = float(stress_pa) / float(hardness_pa)
    if ratio >= PLASTIC_STRESS_RATIO:
        return "plastic"
    if ratio <= ELASTIC_STRESS_RATIO:
        return "elastic"
    return "transition"


def classify_lubrication(lambda_ratio: Optional[float]) -> str:
    if lambda_ratio is None:
        return "unknown"
    if lambda_ratio < LAMBDA_BOUNDARY:
        return "boundary"
    if lambda_ratio < LAMBDA_FULL_FILM:
        return "mixed"
    return "full_film"


def classify_rate_limit(film_class: str, chemistry_active: bool) -> str:
    """Is removal limited by the mechanics or by the surface reaction?

    Hard ceramics are inert and extremely hard, so the surface reaction sets the
    pace. Metals polish by oxidise-then-abrade, so they are chemically coupled
    whenever a reactive slurry is present. Dielectrics are mechanically
    dominated but pH-sensitive through surface hydrolysis.
    """
    if film_class == "hard_ceramic":
        return "chemical"
    if film_class in ("soft_metal", "metal"):
        return "mixed" if chemistry_active else "mechanical"
    if film_class == "semiconductor":
        return "mixed" if chemistry_active else "mechanical"
    if film_class == "dielectric":
        return "mixed" if chemistry_active else "mechanical"
    return "unknown"


def detect(resolved, contact_state=None, supply_state=None) -> Situation:
    """Classify a resolved recipe. Every axis that cannot be determined from
    available data is reported in ``undetermined`` rather than guessed."""
    s = Situation()
    rec = resolved.recipe

    # ── film hardness ────────────────────────────────────────────────
    h_bulk = resolved.p_or("film_bulk_hardness_pa", None)
    h_surf = resolved.p_or("film_surface_hardness_pa", None)
    s.film_class = classify_film(h_bulk, rec.wafer.film,
                                 resolved.p_or("material_family", None))
    if h_bulk:
        s.metrics["film_bulk_hardness_gpa"] = float(h_bulk) / 1e9
    elif s.film_class in ("metal", "semiconductor"):
        s.undetermined.append(
            "soft/hard split within the family: the pack declares no "
            "film_bulk_hardness_pa, so a soft metal cannot be told from a hard one")
    elif s.film_class == "unknown":
        s.undetermined.append(
            f"film_class: '{rec.wafer.film}' is not a known material family and the "
            "pack declares neither material_family nor film_bulk_hardness_pa")

    # ── single-particle contact branch ───────────────────────────────
    # Preferred route: the pad-limited load criterion, which needs NO particle
    # contact stress and is therefore not circular. Derived from Saka/Eusner:
    #
    #   yield load on the film (Hertz + Tresca)   P_Y   = (pi^3/48) Hc^3/Ec^2 R^2
    #   maximum load a pad asperity can apply     P_max = pi R^2 Hp
    #   plastic when P_max > P_Y, i.e.   Lambda = 48 Hp Ec^2 / (pi^2 Hc^3) > 1
    #
    # R cancels exactly, so the branch does not depend on particle size - which
    # matches Eusner's own finding that scratch width and depth are independent
    # of polishing pressure and pad topography. Crucially this uses the PAD
    # hardness, an independently measured quantity (Eusner 2009 Fig. 15: 36
    # nanoindentation measurements of a wet IC1000, mean 0.05 GPa, max 0.31),
    # instead of the particle contact stress that Luo-Dornfeld defines as equal
    # to the film hardness.
    #
    # The trap this avoids: Hp (~0.05 GPa) is a load over the particle's
    # CROSS-SECTION, not over the much smaller particle/film contact area.
    # Comparing Hp directly against Hc would call copper elastic, which is
    # wrong. Only the load comparison above is valid.
    lam = _pad_limited_branch(resolved, h_surf, h_bulk, s)
    stress = resolved.p_or("particle_contact_stress_pa", None)
    if lam is not None:
        pass                      # branch already set by _pad_limited_branch
    elif stress and h_surf:
        s.contact_branch = classify_contact_branch(stress, h_surf)
        s.metrics["contact_stress_over_hardness"] = float(stress) / float(h_surf)
    elif stress and h_bulk:
        # Falling back to BULK hardness is not a neutral substitution, and the
        # error does not even have a known sign. It is tempting to assume the
        # chemically modified surface is SOFTER than the bulk, but the only
        # direct measurement in Cu/H2O2/BTA chemistry contradicts that: an
        # oxidiser grows Cu2O/CuO, which is HARDER than copper (Ihnfeldt &
        # Talbot 2008 measured 3.24 GPa on a film whose bulk is ~1.2 GPa, and
        # bulk cuprite at 17.0-17.5 GPa), while alkaline glycine+H2O2 softens
        # the same metal to 0.28 GPa. Across that study the surface hardness of
        # one metal spans 0.05-20 GPa purely by chemistry and pH. So the bulk
        # ratio is reported as provisional with the direction of its error
        # explicitly unknown.
        s.contact_branch = "unknown"
        s.metrics["contact_stress_over_bulk_hardness"] = float(stress) / float(h_bulk)
        provisional = classify_contact_branch(stress, h_bulk)
        s.undetermined.append(
            "contact_branch: film_surface_hardness_pa (the chemically modified "
            f"surface) is absent, so only a bulk-hardness ratio of "
            f"{float(stress) / float(h_bulk):.3f} could be formed, suggesting "
            f"'{provisional}'. Treat that as provisional and note that the error "
            "has no known sign: an oxidiser can make the surface HARDER than the "
            "bulk (metal oxides) or softer (hydroxides/complexes), and the same "
            "metal has been measured across two orders of magnitude depending on "
            "chemistry and pH. This axis sets the sign of the particle-size "
            "exponent in P3")
    else:
        missing = [k for k, v in (("particle_contact_stress_pa", stress),
                                  ("film_surface_hardness_pa", h_surf)) if not v]
        _ = missing
        s.undetermined.append(
            "contact_branch: missing " + " and ".join(missing) +
            ". Note that in the Luo-Dornfeld formulation the particle contact "
            "stress is SET EQUAL to the film hardness by assumption, so sourcing "
            "it independently is circular unless it comes from a direct "
            "measurement. Without this axis P3 uses the elastic branch, which "
            "fixes the sign of the particle-size exponent")

    # ── pad asperities ───────────────────────────────────────────────
    if contact_state is not None and h_bulk:
        psi = contact_state.plasticity_index(float(h_bulk))
        s.metrics["plasticity_index"] = psi
        s.asperity_regime = "plastic" if psi > PLASTICITY_INDEX_LIMIT else "elastic"
        sat = contact_state.saturation(resolved.pressure_pa)
        s.metrics["summit_saturation"] = sat
        s.load_regime = "saturated" if sat > SATURATION_LIMIT else "unsaturated"

    # ── lubrication ──────────────────────────────────────────────────
    if supply_state is not None:
        s.metrics["lambda_ratio"] = supply_state.lambda_ratio
        s.metrics["supply_number"] = supply_state.supply_number
        s.lubrication = classify_lubrication(supply_state.lambda_ratio)

    # ── rate limiting ────────────────────────────────────────────────
    chem_keys = ("oxidizer_wt_pct", "inhibitor_mM", "ce3_fraction", "slurry_ph")
    chemistry_active = any(resolved.has(k) for k in chem_keys)
    s.rate_limit = classify_rate_limit(s.film_class, chemistry_active)

    # ── topography and pad state ─────────────────────────────────────
    s.topography = "patterned" if rec.wafer.pattern_density is not None else "blanket"
    s.pad_state = "worn" if (rec.pad.use_hours or rec.disk.hours_used) else "fresh"

    s.notes.append(
        f"situation: {s.film_class} film, {s.rate_limit}-limited, "
        f"{s.contact_branch} particle contact, {s.lubrication} lubrication, "
        f"{s.load_regime} pad load, {s.topography}, {s.pad_state} pad")
    return s
