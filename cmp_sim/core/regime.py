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
    stress = resolved.p_or("particle_contact_stress_pa", None)
    s.contact_branch = classify_contact_branch(stress, h_surf or h_bulk)
    if stress and (h_surf or h_bulk):
        s.metrics["contact_stress_over_hardness"] = float(stress) / float(h_surf or h_bulk)
    else:
        s.undetermined.append(
            "contact_branch: needs particle_contact_stress_pa and the softened "
            "film_surface_hardness_pa. The softened hardness is rarely published; "
            "without it P3 assumes the elastic branch, which sets the sign of the "
            "particle-size exponent")

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
