"""State dataclasses — the full input/output contract of CMP-Sim.

Design rules
------------
* Everything a user can physically change on a polisher is a field here.
* Fields left as ``None`` are resolved from the parameter packs
  (``cmp_sim/data/params`` first, then the inherited ``legacy/knowledge/params``).
  A missing physical constant raises ``ParamMissing`` — never a silent default.
* Units are SI internally; user-facing convenience fields carry their unit in
  the name (``pressure_psi``, ``rpm_platen``).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

import numpy as np


# ──────────────────────────────────────────────────────────────────────
# Slurry
# ──────────────────────────────────────────────────────────────────────
@dataclass
class Additive:
    """One slurry additive at one concentration.

    ``role`` is the functional class used by the chemistry layer
    (oxidizer / inhibitor / complexant / surfactant / dispersant /
    accelerator / buffer / biocide). It is resolved from the additive
    database when omitted.
    """
    name: str
    conc_mM: Optional[float] = None
    conc_wt_pct: Optional[float] = None
    role: Optional[str] = None


@dataclass
class Abrasive:
    """Abrasive particle population.

    ``kind`` is ``None`` by default, NOT "silica". The old "silica" default was
    harmless only while the abrasive type had no effect on the prediction. Once
    the type was wired in (``slurry/abrasive_effects.py``), that default started
    claiming every unspecified recipe was a silica slurry — so a ceria validation
    dataset, which states its pack but not its abrasive, was read as "silica run
    through the ceria pack", i.e. an abrasive SWAP, and had its ceria exponents
    withdrawn. ``None`` means "not stated", and the engine then uses the pack's
    own ``reference_abrasive``, which is what the pack was calibrated with.
    """
    kind: Optional[str] = None            # silica | ceria | alumina | zirconia | diamond | none
    conc_wt_pct: Optional[float] = None
    d50_nm: Optional[float] = None
    d99_nm: Optional[float] = None       # large-particle tail -> defect proxy
    shape: str = "spherical"             # spherical | aggregated | faceted | cocoon
    density_kg_m3: Optional[float] = None
    hardness_gpa: Optional[float] = None
    iep_ph: Optional[float] = None


@dataclass
class Slurry:
    abrasive: Abrasive = field(default_factory=Abrasive)
    additives: List[Additive] = field(default_factory=list)
    ph: Optional[float] = None
    ionic_strength_M: Optional[float] = None
    viscosity_pa_s: Optional[float] = None
    zeta_mv: Optional[float] = None
    temperature_c: Optional[float] = None
    pack: Optional[str] = None           # parameter pack name (e.g. "oxide_silica")


# ──────────────────────────────────────────────────────────────────────
# Consumables
# ──────────────────────────────────────────────────────────────────────
@dataclass
class Pad:
    name: str = "IC1000"
    #: True only when the caller AFFIRMATIVELY chose this pad by name.
    #:
    #: The consumables catalogue (``cmp_sim/pad/catalog.py``) fills blank pad
    #: properties from the NAMED pad, and it must only do that for a pad someone
    #: actually picked. `name` has a default of "IC1000" for backward
    #: compatibility, and there are two ways to arrive at it without choosing:
    #: a config that never mentions a pad, and a `Pad()` built directly in code
    #: or in a test. Applying IC1000's published Shore D and groove geometry in
    #: either case would move existing answers on the strength of a default —
    #: measured: it silently removed the contact factor from
    #: tests/test_phase_gates.py by making the pad differ from the pack
    #: reference. So the flag defaults to False (not chosen) and
    #: `recipe_from_dict` raises it when a name is actually supplied. The
    #: conservative default is the correct one: an unset flag means "inert".
    #: Same discipline as `Wafer.film_was_defaulted`, opposite polarity, for
    #: exactly that reason.
    name_was_chosen: bool = False
    shore_d: Optional[float] = None
    youngs_modulus_pa: Optional[float] = None
    porosity: Optional[float] = None
    groove: str = "k-groove"
    groove_width_mm: Optional[float] = None
    groove_depth_mm: Optional[float] = None
    groove_pitch_mm: Optional[float] = None
    asperity_radius_m: Optional[float] = None
    asperity_density_m2: Optional[float] = None
    roughness_beta_inv_m: Optional[float] = None
    use_hours: float = 0.0


@dataclass
class Disk:
    name: str = "generic-diamond"
    grit_mesh: Optional[int] = None
    grit_size_um: Optional[float] = None
    grit_density_mm2: Optional[float] = None
    down_force_n: Optional[float] = None
    sweep_rpm: Optional[float] = None
    duty_cycle: float = 1.0              # in-situ = 1.0, ex-situ < 1
    hours_used: float = 0.0


# ──────────────────────────────────────────────────────────────────────
# Tool
# ──────────────────────────────────────────────────────────────────────
@dataclass
class Tool:
    pressure_psi: float = 3.0
    rpm_platen: float = 60.0
    rpm_head: float = 57.0
    flow_ml_min: float = 200.0
    zone_pressures_psi: Optional[List[float]] = None
    zone_edges_norm: Optional[List[float]] = None
    retaining_ring_psi: Optional[float] = None
    platen_temp_c: Optional[float] = None
    center_offset_m: Optional[float] = None   # r_cc
    time_s: float = 60.0


# ──────────────────────────────────────────────────────────────────────
# Wafer
# ──────────────────────────────────────────────────────────────────────
#: Sentinel meaning "the caller did not say". A plain default of "oxide" made
#: an omitted film silently return the oxide rate - the film sets the removal
#: mechanism, the plausibility envelope and the maturity grade, so guessing it
#: is guessing the answer. The default is kept for backward compatibility with
#: existing configs but is now reported rather than assumed silently.
FILM_DEFAULTED = "oxide"


@dataclass
class Wafer:
    film: str = FILM_DEFAULTED           # oxide | cu | w | poly_si | si | snag
    #: True when `film` came from the default rather than from the caller.
    film_was_defaulted: bool = False
    diameter_mm: float = 300.0
    initial_thickness_nm: Optional[float] = None
    pattern_density: Optional[float] = None
    pitch_um: Optional[float] = None
    n_radial: int = 81


@dataclass
class Recipe:
    """A complete simulation input."""
    slurry: Slurry = field(default_factory=Slurry)
    pad: Pad = field(default_factory=Pad)
    disk: Disk = field(default_factory=Disk)
    tool: Tool = field(default_factory=Tool)
    wafer: Wafer = field(default_factory=Wafer)
    model: str = "preston"
    #: Direct parameter-pack overrides, e.g. ``{"kp_m_per_pa": 2.0e-13}``.
    #: This is how a user supplies a number the literature does not publish --
    #: their own measured Preston coefficient, for instance. Values set here
    #: win over the pack and are reported in the provenance as owner-supplied,
    #: so they can never be mistaken for a sourced value.
    params: Dict[str, Any] = field(default_factory=dict)
    #: Measured removal rates from the owner's own tool, each with the
    #: conditions it was measured at:
    #:     [{"rate_A_per_min": 1450, "pressure_psi": 3, "rpm_platen": 60}, ...]
    #: The model fits itself to these and reports a cross-validated accuracy,
    #: so more measurements make the prediction converge on the real tool.
    measurements: List[Dict[str, Any]] = field(default_factory=list)
    meta: Dict[str, Any] = field(default_factory=dict)


# ──────────────────────────────────────────────────────────────────────
# Output
# ──────────────────────────────────────────────────────────────────────
@dataclass
class Result:
    model: str
    film: str
    radius_m: np.ndarray
    mrr_nm_per_min: np.ndarray
    mean_rr_nm_per_min: float
    mean_rr_angstrom_per_min: float
    wiwnu_percent: float
    removed_nm: np.ndarray
    remaining_nm: Optional[np.ndarray] = None
    factors: Dict[str, float] = field(default_factory=dict)
    provenance: Dict[str, Any] = field(default_factory=dict)
    notes: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    extras: Dict[str, Any] = field(default_factory=dict)

    def summary(self) -> Dict[str, Any]:
        out = {
            "model": self.model,
            "film": self.film,
            "removal_rate_A_per_min": round(self.mean_rr_angstrom_per_min, 1),
            "removal_rate_nm_per_min": round(self.mean_rr_nm_per_min, 3),
            "wiwnu_percent": (None if self.wiwnu_percent is None
                              else round(self.wiwnu_percent, 3)),
            "radial_profile": {
                "radius_mm": [round(float(r) * 1e3, 2) for r in self.radius_m],
                "mrr_A_per_min": [round(float(v) * 10.0, 1) for v in self.mrr_nm_per_min],
            },
            "factors": {k: round(float(v), 4) for k, v in self.factors.items()},
            "notes": self.notes,
            "warnings": self.warnings,
        }
        if self.remaining_nm is not None:
            out["remaining_thickness_nm"] = {
                "center": round(float(self.remaining_nm[0]), 2),
                "edge": round(float(self.remaining_nm[-1]), 2),
                "mean": round(float(np.mean(self.remaining_nm)), 2),
            }
        out.update({k: v for k, v in self.extras.items()})
        return out
