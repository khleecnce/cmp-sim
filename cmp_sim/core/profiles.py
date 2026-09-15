"""Model profiles — pick the physics that suits the situation.

The problem with a ladder
-------------------------
``preston -> gw_preston -> full`` bundles choices that are physically
independent. A user cannot say "plastic contact branch, but no transport layer",
and "full" implies more physics is always better, which is false: applying a
chemistry term to a pack whose Kp already contains that chemistry double counts
it, and applying the Greenwood-Williamson correction against a guessed reference
pad inflates every rate.

So layers are orthogonal switches, and a **profile** is a named bundle chosen
for a *situation* rather than for a film. Films with different names can share a
profile (SiC and sapphire are both hard and chemically limited); one film can
need different profiles at different operating points (US6918821B2 copper fits
Preston at 4 psi and not at 1.5 psi).

Each profile declares where it applies. ``recommend()`` ranks profiles against a
detected ``Situation``; ``check()`` warns when the chosen profile does not fit
what the run actually is. The user still chooses — the simulator just refuses to
stay quiet about a mismatch.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Tuple

from cmp_sim.core.regime import Situation

#: the orthogonal physics layers a profile can switch on
LAYERS = ("contact", "abrasive", "chemistry", "transport", "pattern", "wear", "damage")


@dataclass
class Profile:
    """A named bundle of layers, with the situations it suits."""
    name: str
    description: str
    layers: Tuple[str, ...]
    #: preferred single-particle contact branch: "auto" | "elastic" | "plastic"
    contact_branch: str = "auto"
    suits: Dict[str, Tuple[str, ...]] = field(default_factory=dict)
    caveats: List[str] = field(default_factory=list)

    def enabled(self, layer: str) -> bool:
        return layer in self.layers

    def fit(self, situation: Situation) -> Tuple[int, int, List[str]]:
        """Score against a situation: (matched axes, mismatched axes, reasons)."""
        matched = mismatched = 0
        reasons: List[str] = []
        for axis, wanted in self.suits.items():
            actual = getattr(situation, axis, "unknown")
            if actual in ("unknown", None):
                continue                      # undetermined cannot count either way
            if actual in wanted:
                matched += 1
                reasons.append(f"{axis}={actual} suits this profile")
            else:
                mismatched += 1
                reasons.append(
                    f"{axis}={actual} but this profile targets {'/'.join(wanted)}")
        return matched, mismatched, reasons

    def as_dict(self) -> Dict[str, Any]:
        return {"name": self.name, "description": self.description,
                "layers": list(self.layers), "contact_branch": self.contact_branch,
                "suits": {k: list(v) for k, v in self.suits.items()},
                "caveats": self.caveats}


# ── the profiles ─────────────────────────────────────────────────────
PROFILES: Dict[str, Profile] = {}


def register(p: Profile) -> Profile:
    PROFILES[p.name] = p
    return p


register(Profile(
    name="preston_baseline",
    description="Preston only: MRR = Kp*P*V on nominal pressure. The reference "
                "every other profile is measured against.",
    layers=(),
    caveats=["No contact, chemistry or transport physics. Changing the "
             "formulation will not change the answer."],
))

register(Profile(
    name="mechanical_screening",
    description="Preston plus pad contact and abrasive mechanics, no chemistry. "
                "For comparing pads and abrasive loadings at fixed chemistry.",
    layers=("contact", "abrasive", "transport", "damage"),
    suits={"rate_limit": ("mechanical",), "topography": ("blanket",)},
))

register(Profile(
    name="soft_metal_plastic",
    description="Soft metals (Cu, SnAg): plastic single-particle contact, "
                "oxidizer/inhibitor chemistry through the softened surface.",
    layers=("contact", "abrasive", "chemistry", "transport", "damage"),
    contact_branch="plastic",
    suits={"film_class": ("soft_metal",), "topography": ("blanket",)},
    caveats=["A soft film pushes the contact plastic, so the elastic "
             "Greenwood-Williamson result for the pad is the weaker assumption "
             "here — check the plasticity index in the situation report."],
))

register(Profile(
    name="hard_metal_passivation",
    description="Hard metals (W): Fenton-type oxidation forms a passivating "
                "film that is then abraded. Rate follows the oxidizer.",
    layers=("contact", "abrasive", "chemistry", "transport", "damage"),
    suits={"film_class": ("metal",), "topography": ("blanket",)},
    caveats=["W is the most scratch-sensitive system in the defect model "
             "(damage exponent 2.54 vs 1.44 for ceria systems)."],
))

register(Profile(
    name="dielectric_blanket",
    description="Oxide and other dielectrics on blanket wafers: elastic contact, "
                "pH-driven chemistry, ceria chemical tooth where applicable.",
    layers=("contact", "abrasive", "chemistry", "transport", "damage"),
    contact_branch="elastic",
    suits={"film_class": ("dielectric",), "topography": ("blanket",)},
))

register(Profile(
    name="dielectric_patterned",
    description="Patterned dielectric: adds density-dependent step-height "
                "evolution, dishing and erosion. What a fab actually buys.",
    layers=("contact", "abrasive", "chemistry", "transport", "pattern", "damage"),
    contact_branch="elastic",
    suits={"film_class": ("dielectric",), "topography": ("patterned",)},
))

register(Profile(
    name="metal_patterned",
    description="Patterned metal (damascene): dishing and erosion against a "
                "stop layer, driven by selectivity.",
    layers=("contact", "abrasive", "chemistry", "transport", "pattern", "damage"),
    suits={"film_class": ("soft_metal", "metal"), "topography": ("patterned",)},
    caveats=["High selectivity protects the stop layer but deepens dishing — "
             "the trade-off is computed, not assumed."],
))

register(Profile(
    name="chemically_limited",
    description="Hard, inert materials (SiC, sapphire): the surface reaction "
                "sets the pace, not P*V. Use for ranking compositions only.",
    layers=("chemistry", "abrasive", "transport", "damage"),
    suits={"film_class": ("hard_ceramic",), "rate_limit": ("chemical",)},
    caveats=["A mechanical P*V law cannot fit these systems whatever Kp is "
             "chosen — in the SiC DOE, pH and flow outrank pressure. Absolute "
             "rate from this profile is not trustworthy; rankings are.",
             "The pad contact layer is deliberately OFF: its correction is "
             "swamped by the chemical term here."],
))

register(Profile(
    name="pad_life_study",
    description="Everything, plus pad glazing and conditioner ageing. For "
                "rate-drift over pad life rather than a single wafer.",
    layers=("contact", "abrasive", "chemistry", "transport", "wear", "damage"),
    suits={"pad_state": ("worn",)},
    caveats=["Pad-wear data covers 10 min of polishing at 2-5 psi; beyond that "
             "the fit is extrapolated and degenerates."],
))


#: Layers that are OVERLAYS, not alternatives: if the situation calls for one,
#: it is added to whichever profile fits, rather than competing with it. Pad
#: wear and pattern effects describe extra circumstances, not a different
#: theory of removal, so a worn patterned Cu wafer should not have to choose
#: between "metal_patterned" and "pad_life_study".
OVERLAY_RULES: Tuple[Tuple[str, str, Tuple[str, ...]], ...] = (
    ("pad_state", "wear", ("worn",)),
    ("topography", "pattern", ("patterned",)),
)


def apply_overlays(profile: Profile, situation: Situation) -> Tuple[Profile, List[str]]:
    """Add situation-driven overlay layers to a chosen profile."""
    extra: List[str] = []
    notes: List[str] = []
    for axis, layer, triggers in OVERLAY_RULES:
        if getattr(situation, axis, None) in triggers and not profile.enabled(layer):
            extra.append(layer)
            notes.append(
                f"overlay '{layer}' added because {axis}="
                f"{getattr(situation, axis)}")
    if not extra:
        return profile, notes
    merged = Profile(
        name=f"{profile.name}+{'+'.join(extra)}",
        description=profile.description,
        layers=tuple(profile.layers) + tuple(extra),
        contact_branch=profile.contact_branch,
        suits=dict(profile.suits),
        caveats=list(profile.caveats),
    )
    return merged, notes

#: backward-compatible aliases for the original ladder
ALIASES = {
    "preston": "preston_baseline",
    "gw_preston": "mechanical_screening",
    "full": None,        # resolved per situation; see resolve_model()
}


def recommend(situation: Situation, top: int = 3) -> List[Tuple[Profile, int, List[str]]]:
    """Rank profiles for a situation, best first."""
    scored = []
    for p in PROFILES.values():
        matched, mismatched, reasons = p.fit(situation)
        if not p.suits:
            continue                          # baseline is never "recommended"
        scored.append((p, matched - 2 * mismatched, reasons))
    scored.sort(key=lambda t: -t[1])
    return scored[:top]


def check(profile: Profile, situation: Situation) -> List[str]:
    """Warn where the chosen profile does not fit the detected situation."""
    warnings: List[str] = []
    matched, mismatched, reasons = profile.fit(situation)
    if mismatched:
        bad = [r for r in reasons if " but this profile targets " in r]
        best = recommend(situation, top=1)
        suggestion = f" Consider '{best[0][0].name}'." if best else ""
        warnings.append(
            f"profile '{profile.name}' does not match the detected situation: "
            + "; ".join(bad) + "." + suggestion)

    # physics-level mismatches that matter regardless of the profile's own targets
    if situation.load_regime == "saturated" and profile.enabled("contact"):
        warnings.append(
            "pad summits are saturated, so the Greenwood-Williamson "
            "exponential-tail result (and Preston's pressure linearity with it) "
            "no longer holds — the contact correction is unreliable at this point")
    if situation.asperity_regime == "plastic" and profile.enabled("contact"):
        warnings.append(
            "plasticity index > 1: pad asperities flow plastically, so the "
            "elastic Greenwood-Williamson contact model is outside its validity range")
    if situation.lubrication == "full_film":
        warnings.append(
            "a full hydrodynamic film separates pad and wafer: abrasives cannot "
            "reach the surface, so any predicted removal here is meaningless")
    if situation.rate_limit == "chemical" and not profile.enabled("chemistry"):
        warnings.append(
            "this system is chemically rate-limited but the chemistry layer is "
            "off, so the dominant physics is not being modelled")
    if situation.topography == "patterned" and not profile.enabled("pattern"):
        warnings.append(
            "the wafer is patterned but the pattern layer is off: dishing and "
            "erosion are not computed, and the blanket rate shown will not be "
            "what the die sees")
    if situation.pad_state == "worn" and not profile.enabled("wear"):
        warnings.append(
            "pad or conditioner hours were given but the wear layer is off, so "
            "rate drift over pad life is not reflected")
    return warnings


def auto(situation: Situation) -> Tuple[Profile, List[str]]:
    """Best-fitting profile for a situation, plus any overlays it needs."""
    ranked = recommend(situation, top=1)
    base = ranked[0][0] if (ranked and ranked[0][1] > 0) else PROFILES["dielectric_blanket"]
    return apply_overlays(base, situation)


def resolve_model(name: str, situation: Situation) -> Tuple[Profile, List[str]]:
    """Map a user's model name to a profile.

    ``auto`` picks by situation. The legacy ladder names still work; ``full``
    now means "the profile that suits this run", which is what it was trying to
    approximate.
    """
    notes: List[str] = []
    if name in ("auto", "full"):
        p, overlay_notes = auto(situation)
        notes.append(f"model '{name}' resolved to profile '{p.name}': {p.description}")
        notes.extend(overlay_notes)
        return p, notes
    if name in ALIASES and ALIASES[name]:
        p = PROFILES[ALIASES[name]]
        notes.append(f"model '{name}' is an alias for profile '{p.name}'")
        return p, notes
    if name in PROFILES:
        # An explicitly named profile is respected as given: no overlays are
        # bolted on, because the user asked for exactly that physics. check()
        # still warns if the situation needs something the profile lacks.
        return PROFILES[name], notes
    raise ValueError(
        f"unknown model/profile '{name}'. Available profiles: "
        f"{sorted(PROFILES)}; aliases: {sorted(ALIASES)}; or 'auto'.")
