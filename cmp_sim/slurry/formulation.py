"""Map a human slurry formulation onto the pack keys the physics layers read.

Why this layer exists
---------------------
The physics modules consume engine keys (`oxidizer_wt_pct`, `inhibitor_conc_mM`,
`abrasive_wt_pct`, `slurry_ph`, ...). A formulator thinks in components:
"60 nm ceria at 1.5 wt%, 5 mM BTA, pH 4, 1 wt% H2O2". This module translates
the second into the first.

Two rules make it honest
------------------------
1. **An input that is not wired must not be silently dropped.** Discarding an
   input while still returning a confident-looking number is the worst possible
   behaviour, so unmapped components come back as warnings attached to the run.
2. **A role must be resolved, not guessed.** An additive's functional role
   (oxidizer / inhibitor / complexant / surfactant ...) comes from the additive
   database or from the user; an unrecognised name is reported, never assumed
   to be inert.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import yaml

from cmp_sim.core.declined_axes import DECLINES_AXIS
from cmp_sim.core.params import OWN_PACK_DIR, Param, ParamPack
from cmp_sim.core.state import Additive, Slurry

ADDITIVE_DB_PATH = OWN_PACK_DIR / "additives.yaml"
ABRASIVE_DB_PATH = OWN_PACK_DIR / "abrasives.yaml"

#: additive role -> the pack keys that carry its concentration
# Key names must match what the physics layers actually read
# (legacy/sim/chemistry.py: inhibitor_mM, oxidizer_wt_pct, ...). A plausible but
# wrong name means the input is accepted and then silently ignored, which is the
# exact failure this module exists to prevent.
ROLE_TO_KEYS: Dict[str, Tuple[str, ...]] = {
    "oxidizer": ("oxidizer_wt_pct",),
    "inhibitor": ("inhibitor_mM",),
    "passivator": ("inhibitor_mM",),
    "complexant": ("complexant_mM",),
    "chelator": ("complexant_mM",),
    "surfactant": ("surfactant_mM",),
    "dispersant": ("dispersant_mM",),
}

#: roles the physics layers currently consume
WIRED_ROLES = {"oxidizer", "inhibitor", "passivator"}


#: Parsed database YAML keyed by (path, mtime_ns, size), mirroring the pack
#: loader's cache in core/params.py. The abrasive database is 125 KB and is now
#: consulted several times per run by slurry/abrasive_effects.py, so re-parsing
#: it each time made the test suite take minutes instead of seconds. The mtime
#: is part of the key so editing the database takes effect immediately: a stale
#: cache during a data-tuning session would be a silent wrong answer.
_DB_CACHE: Dict[Tuple[str, int, int], Dict[str, Any]] = {}


def _load_db(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}
    try:
        st = path.stat()
        key = (str(path), st.st_mtime_ns, st.st_size)
    except OSError:                                      # pragma: no cover
        return yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    hit = _DB_CACHE.get(key)
    if hit is None:
        hit = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        _DB_CACHE[key] = hit
    # Callers only READ these trees (lookups and value extraction), so the
    # shared instance is handed out directly rather than deep-copied - copying
    # 125 KB per lookup was most of the cost this cache exists to remove.
    return hit


def additive_database() -> Dict[str, Any]:
    return _load_db(ADDITIVE_DB_PATH).get("additives", {}) or {}


def abrasive_database() -> Dict[str, Any]:
    return _load_db(ABRASIVE_DB_PATH).get("abrasives", {}) or {}


def _lookup(db: Dict[str, Any], name: str) -> Optional[Tuple[str, Dict[str, Any]]]:
    """Resolve a name against entry keys and their aliases (case-insensitive)."""
    key = str(name).strip().lower().replace("-", "_").replace(" ", "_")
    if key in db:
        return key, db[key]
    for entry_key, entry in db.items():
        aliases = [str(a).strip().lower().replace("-", "_").replace(" ", "_")
                   for a in (entry or {}).get("aliases", [])]
        if key in aliases:
            return entry_key, entry
    return None


def resolve_role(additive: Additive) -> Tuple[Optional[str], Optional[str]]:
    """Return ``(role, note)``. The user's explicit role always wins."""
    if additive.role:
        return additive.role.strip().lower(), None
    hit = _lookup(additive_database(), additive.name)
    if hit:
        key, entry = hit
        role = (entry or {}).get("role")
        if role:
            return str(role).strip().lower(), f"'{additive.name}' resolved to role '{role}' via the additive database entry '{key}'"
    return None, (f"'{additive.name}' is not in the additive database and no role was "
                  "given, so its effect cannot be modelled")


def abrasive_properties(kind: str) -> Tuple[Dict[str, Any], Optional[str]]:
    """Density / hardness / IEP etc. for an abrasive kind, from the database."""
    hit = _lookup(abrasive_database(), kind)
    if not hit:
        return {}, (f"abrasive '{kind}' is not in the abrasive database, so its "
                    "density, hardness and isoelectric point are unknown")
    key, entry = hit
    props = {}
    for name, spec in ((entry or {}).get("properties", {}) or {}).items():
        if isinstance(spec, dict):
            if spec.get("value") is not None:
                props[name] = spec["value"]
        elif spec is not None:
            props[name] = spec
    return props, None


@dataclass
class FormulationOverrides:
    """Pack-key overrides derived from a formulation, plus what was ignored."""
    overrides: Dict[str, Any] = field(default_factory=dict)
    notes: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    def as_dict(self) -> Dict[str, Any]:
        return {"overrides": dict(self.overrides), "notes": self.notes,
                "warnings": self.warnings}


def to_overrides(slurry: Slurry) -> FormulationOverrides:
    """Translate a ``Slurry`` into pack-key overrides."""
    out = FormulationOverrides()

    if slurry.ph is not None:
        out.overrides["slurry_ph"] = float(slurry.ph)
        out.notes.append(f"pH {slurry.ph} -> slurry_ph")

    ab = slurry.abrasive
    if ab.conc_wt_pct is not None:
        out.overrides["abrasive_wt_pct"] = float(ab.conc_wt_pct)
        out.notes.append(f"abrasive {ab.conc_wt_pct} wt% -> abrasive_wt_pct")
    if ab.d50_nm is not None:
        out.overrides["abrasive_size_nm"] = float(ab.d50_nm)
        out.notes.append(f"abrasive D50 {ab.d50_nm} nm -> abrasive_size_nm")
    if ab.d99_nm is not None:
        out.overrides["abrasive_d99_nm"] = float(ab.d99_nm)
        out.notes.append(f"abrasive D99 {ab.d99_nm} nm -> abrasive_d99_nm (defect proxy)")
    if ab.shape and ab.shape != "spherical":
        out.warnings.append(
            f"particle shape '{ab.shape}' is recorded but not yet wired into the "
            "removal model; only its defect-risk implication is reported")

    for add in slurry.additives:
        role, note = resolve_role(add)
        if note:
            (out.notes if role else out.warnings).append(note)
        if not role:
            continue
        keys = ROLE_TO_KEYS.get(role)
        if not keys:
            out.warnings.append(
                f"additive '{add.name}' has role '{role}', which no physics layer "
                "consumes yet — its concentration was NOT applied to the result")
            continue
        value = add.conc_wt_pct if "wt_pct" in keys[0] else add.conc_mM
        if value is None:
            out.warnings.append(
                f"additive '{add.name}' (role {role}) has no concentration in the "
                f"unit the model needs ({keys[0]}), so it was not applied")
            continue
        for k in keys:
            out.overrides[k] = float(value)
        out.notes.append(f"{add.name} ({role}) {value} -> {', '.join(keys)}")
        if role not in WIRED_ROLES:
            out.warnings.append(
                f"role '{role}' is mapped to a pack key but no physics term reads it yet")

    return out


#: Keys the ENGINE reads directly, even when a pack never declares them.
#:
#: These are written by the factor fitter (core/factor_fit.py FACTOR_PARAM)
#: and consumed by the solver. They are legitimately absent from every pack: a
#: pack states the physics it was calibrated with, while these are what a
#: user's own measurements OVERRIDE it with.
#:
#: Without this list the override warning fired on exactly the values the
#: fitter had just proven from data — telling the user "recorded but may not
#: affect the result" about a pressure exponent that provably did affect it
#: (fitted 0.792, and 0.792 measured back out of the returned rate). A warning
#: that contradicts the run it is attached to costs more than it protects.
CONSUMED_BY_THE_ENGINE = frozenset({
    "pressure_exponent",
    "velocity_exponent",
    "abrasive_size_exponent",
    "abrasive_conc_exponent",
    "abrasive_conc_half_wt_pct",
    "abrasive_half_wt_pct",
    "oxidizer_langmuir_K",
    "activation_energy_kj_per_mol",
})


#: Keys a pack legitimately DECLARES but which no removal-rate term reads, with
#: the reason. Being declared is exactly why these were the hard case: the
#: "not declared by pack" warning above never fires for them, so setting one
#: changed nothing and the run said nothing about it -- indistinguishable, to a
#: reader, from a model that weighed the input and found it unimportant.
#: Found by ``tools/inert_axis_scan.py`` (3 of its 4 ``silent`` axes).
#:
#: Each entry costs ZERO constants: nothing here is a claim about physics, only
#: a statement of which path the value has to travel to reach a term.
#:
#: Each message carries the machine-readable ``[DECLINES_AXIS: ...]`` marker
#: (``core.declined_axes``) as well as its prose. The prose alone was not
#: enough: the validation scorer recognised only the word "GATED", so a block
#: sweeping one of these keys was scored as an ordinary prediction that
#: happened to be constant -- reproducing the `flat` baseline exactly and
#: counting toward the headline median as though physics had been tested.
UNREAD_BY_THE_RATE: Dict[str, str] = {
    "pad_hardness_shore_d": (
        f"{DECLINES_AXIS}pad_hardness_shore_d] "
        "'pad_hardness_shore_d' was set on the PACK, and no physics term reads "
        "it there: pad stiffness reaches the model only through the GW "
        "contact layer, which takes the hardness from the Pad OBJECT "
        "(pad: {shore_d: ...}, or youngs_modulus_pa) and converts it with the "
        "Qi correlation. Setting the pack key instead leaves the contact "
        "factor at the pack's reference pad, so the predicted rate does not "
        "move with pad hardness. Put the value on the pad to reach the term. "
        "⚠ That recommended path is CONDITIONAL, measured: kappa is applied "
        "only when the pack declares its OWN reference pad with a real source "
        "(pad/material.py::reference_pad_is_trustworthy). On a pack that "
        "inherits the generic base pad the Pad object is converted and then "
        "kappa is WITHHELD as a diagnostic, so the rate does not move there "
        "either -- read the diagnostic kappa in the notes. And where it IS "
        "applied the response is only bounded above ~55 Shore D: at 3 psi the "
        "summits saturate (51.6% at 55D, 100% at 45D), which voids the "
        "exponential-tail result kappa rests on, and below ~35D the GW solver "
        "has no solution at all and raises ContactSolverOutOfRange."),
    "asperity_density_per_m2": (
        f"{DECLINES_AXIS}asperity_density_per_m2] "
        "'asperity_density_per_m2' does not move the removal rate, and this is "
        "GW physics rather than a missing wire -- the summit density CANCELS "
        "exactly. In Greenwood-Williamson with exponential summit heights the "
        "load balance fixes the separation d so that adding summits both adds "
        "contacts and shares the same total load among more of them: the real "
        "area fraction A_r/A_0, the mean real pressure p_r and the contact "
        "count at a given nominal pressure are all independent of eta "
        "(measured over a 16x range: relative spread 1.1e-10, i.e. float "
        "noise). Since kappa = A_r(pad)/A_r(reference), eta cancels a second "
        "time in the ratio. What DOES move the contact factor is E* "
        "(pad modulus), the summit radius R and the height spread sigma -- put "
        "those on the Pad object. eta is still read for the SATURATION "
        "diagnostic (the fraction of summits in contact), which is the "
        "validity boundary of everything above, so it is not ignored."),
    "asperity_ref_density_per_m2": (
        f"{DECLINES_AXIS}asperity_ref_density_per_m2] "
        "'asperity_ref_density_per_m2' is the reference partner of "
        "'asperity_density_per_m2' and is inert for the same structural "
        "reason: the summit density cancels out of the GW real-area fraction, "
        "so a RATIO of two densities cancels twice over. See the declaration "
        "for asperity_density_per_m2 for the measurement and for the pad "
        "properties that do reach the rate."),
    "abrasive_d99_nm": (
        f"{DECLINES_AXIS}abrasive_d99_nm] "
        "'abrasive_d99_nm' does not enter the removal rate and no physics term "
        "reads it for the rate, by design: the large-particle tail is read only "
        "by the defect-risk proxy (scratch width and depth). Removal is carried "
        "by the D50 population, while the tail makes scratches, so changing D99 "
        "alone moves defect_risk and leaves the rate unchanged. Vary "
        "abrasive_size_nm / abrasive_d50_nm to move the rate."),
    "cond_disk_usage_hours": (
        f"{DECLINES_AXIS}cond_disk_usage_hours] "
        "'cond_disk_usage_hours' is declared by several packs and no "
        "removal-rate term reads it: conditioner ageing reaches the model "
        "only through the P7 pad-life DIAGNOSTIC, which is reported and "
        "deliberately NOT applied to Kp -- the inherited MRR proxy peaks at "
        "~7 min against a measured ~3 min, so using it as a rate multiplier "
        "would claim a precision the data does not support. Unusually there "
        "is no 'put it here instead' path: moving the value onto the disk "
        "object (disk: {hours_used: ...}) populates pad_life in the result "
        "but leaves the rate equally unchanged, and recommending it would "
        "swap one silent inertness for another. Read pad_life for the drift. "
        "Unblock the rate path with a pad-life series measuring removal rate "
        "against disk hours at one pad and one slurry, which would give the "
        "proxy a time constant rather than only a shape."),
}


def apply_overrides(pack: ParamPack, overrides: Dict[str, Any],
                    source: str = "user recipe") -> Tuple[ParamPack, List[str]]:
    """Return a copy of ``pack`` with overrides applied.

    Overriding a value the pack never declared is reported: the physics term
    that would consume it may not exist, in which case the input has no effect.
    """
    notes: List[str] = []
    params = dict(pack.params)
    for key, value in overrides.items():
        known = key in params
        params[key] = Param(key=key, value=value,
                            unit=params[key].unit if known else "",
                            source=source, confidence="owner-provided",
                            note="set from the recipe formulation", owner="recipe")
        if not known and key not in CONSUMED_BY_THE_ENGINE:
            notes.append(
                f"'{key}' is not declared by pack '{pack.name}', so no physics term "
                "may read it — the input is recorded but may not affect the result")
        elif known and key in UNREAD_BY_THE_RATE:
            # Declared by the pack AND accepted, yet no rate term consumes it.
            # Without this the run was inert and mute, which reads as "the
            # model considered your pad hardness and it did not matter".
            notes.append(UNREAD_BY_THE_RATE[key])
    return (ParamPack(name=pack.name, description=pack.description, params=params,
                      lineage=list(pack.lineage) + ["recipe"]),
            notes)
