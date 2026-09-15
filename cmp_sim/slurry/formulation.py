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


def _load_db(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


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
        if not known:
            notes.append(
                f"'{key}' is not declared by pack '{pack.name}', so no physics term "
                "may read it — the input is recorded but may not affect the result")
    return (ParamPack(name=pack.name, description=pack.description, params=params,
                      lineage=list(pack.lineage) + ["recipe"]),
            notes)
