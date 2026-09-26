"""Named consumables: pad and conditioner-disk catalogue.

WHY THIS MODULE EXISTS
----------------------
An engineer picks a pad by product name ("IC1000"), not by typing a Shore D.
The tool UI therefore needs a name -> property mapping, and that mapping is
DATA: it lives in ``cmp_sim/data/consumables.yaml`` with a source and a
confidence on every number, exactly like a parameter pack. The web layer only
reads it through the API and holds no consumable number of its own.

THREE RULES, all of which exist because of failures this repo already had
------------------------------------------------------------------------
1. An explicit value on the ``Pad``/``Disk`` object always wins. The catalogue
   fills blanks; it never overwrites what the user typed.
2. A property the catalogue does not publish stays ``None`` and is reported.
   Politex has no published Shore D in any source held here, so selecting it
   changes nothing and the engine SAYS so — the same discipline
   ``abrasive_effects`` applies when no published rate ratio exists.
3. Selecting the pad a pack was CALIBRATED on must not rescale the rate.
   ``kappa_contact`` is a ratio against the pack's reference pad; if the
   catalogue's Shore D is fed through the Qi correlation while the reference
   pad's E* came from a direct measurement of the same physical pad, the two
   disagree by construction and kappa moves the rate by that disagreement
   alone. Measured, that was a 1.9x error on ``oxide_silica_calibrated_pad``.
   So a pack may declare ``reference_pad_name``, and when the recipe names that
   same pad with no user override, the contact factor is pinned to 1.0.
"""
from __future__ import annotations

import copy
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import yaml

DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "consumables.yaml"

#: Catalogue property -> the ``Pad`` dataclass field it fills.
PAD_FIELD_MAP = {
    "shore_d": "shore_d",
    "groove_width_mm": "groove_width_mm",
    "groove_depth_mm": "groove_depth_mm",
    "groove_pitch_mm": "groove_pitch_mm",
}

#: Catalogue property -> the ``Disk`` dataclass field it fills.
DISK_FIELD_MAP = {
    "grit_size_um": "grit_size_um",
    "grit_density_mm2": "grit_density_mm2",
}

_CACHE: Dict[str, Any] = {}


def _raw() -> Dict[str, Any]:
    key = str(DATA_FILE)
    st = DATA_FILE.stat()
    stamp = (st.st_mtime_ns, st.st_size)
    if _CACHE.get("key") != (key, stamp):
        _CACHE["data"] = yaml.safe_load(DATA_FILE.read_text(encoding="utf-8")) or {}
        _CACHE["key"] = (key, stamp)
    return copy.deepcopy(_CACHE["data"])


def pad_catalog() -> Dict[str, Any]:
    return dict(_raw().get("pads", {}) or {})


def disk_catalog() -> Dict[str, Any]:
    return dict(_raw().get("disks", {}) or {})


def _lookup(table: Dict[str, Any], name: Optional[str]) -> Tuple[Optional[str], Dict[str, Any]]:
    """Case/punctuation-insensitive name lookup. Returns (canonical, entry)."""
    if not name:
        return None, {}
    want = str(name).strip().lower().replace("-", "").replace("_", "").replace(" ", "")
    for key, entry in table.items():
        k = key.lower().replace("-", "").replace("_", "").replace(" ", "")
        if k == want:
            return key, (entry or {})
    return None, {}


@dataclass
class ConsumableResolution:
    """What the catalogue supplied, what it refused, and why."""
    pad_name: Optional[str] = None
    disk_name: Optional[str] = None
    #: field -> value actually written onto the recipe object
    filled: Dict[str, Any] = field(default_factory=dict)
    #: field -> source string for everything filled
    sources: Dict[str, str] = field(default_factory=dict)
    #: field -> reason a published value does not exist
    unpublished: Dict[str, str] = field(default_factory=dict)
    notes: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    @property
    def pad_is_catalogued(self) -> bool:
        return self.pad_name is not None

    def as_dict(self) -> Dict[str, Any]:
        return {"pad": self.pad_name, "disk": self.disk_name,
                "filled": dict(self.filled), "sources": dict(self.sources),
                "unpublished": dict(self.unpublished)}


def _spec_value(spec: Any) -> Tuple[Any, str, str]:
    """(value, source, confidence) from a catalogue entry that may be scalar."""
    if isinstance(spec, dict):
        return spec.get("value"), str(spec.get("source") or ""), str(
            spec.get("confidence") or "unknown")
    return spec, "", "unknown"


def apply_catalog(pad, disk) -> ConsumableResolution:
    """Fill blank pad/disk fields from the catalogue, in place.

    Mutates the dataclasses it is given, because the solver resolves a recipe
    once and every downstream layer must see the same pad.
    """
    res = ConsumableResolution()

    pads = pad_catalog()
    # A pad NAME that came from the dataclass default is not a choice. Filling
    # IC1000's published properties into every recipe that never mentioned a pad
    # would move existing answers on the strength of a default.
    pad_name = getattr(pad, "name", None) if getattr(
        pad, "name_was_chosen", False) else None
    canon, entry = _lookup(pads, pad_name)
    if pad_name and canon is None:
        res.warnings.append(
            f"pad '{pad.name}' is not in the consumables catalogue, so no pad "
            f"property was filled from a source; the pack's reference pad is "
            f"used instead. Known pads: {sorted(pads)}. Type the properties "
            f"directly (Shore D, grooves) to model an uncatalogued pad.")
    if canon:
        res.pad_name = canon
        for prop, fieldname in PAD_FIELD_MAP.items():
            value, source, conf = _spec_value(entry.get(prop))
            current = getattr(pad, fieldname, None)
            if current is not None:
                if value is not None and float(current) != float(value):
                    res.notes.append(
                        f"{fieldname} = {current} was given explicitly and keeps "
                        f"priority over the catalogue's {value} for {canon}")
                continue
            if value is None:
                res.unpublished[fieldname] = source or (
                    f"not published for {canon} in any source held here")
                continue
            setattr(pad, fieldname, float(value))
            res.filled[fieldname] = float(value)
            res.sources[fieldname] = f"consumables.yaml pads.{canon}.{prop} " \
                                     f"[{conf}] {source}".strip()
        if res.filled:
            res.notes.append(
                f"pad '{canon}': " + ", ".join(
                    f"{k}={v}" for k, v in sorted(res.filled.items()))
                + " filled from the consumables catalogue (sources in provenance)")
        if res.unpublished:
            res.warnings.append(
                f"pad '{canon}': no published value exists for "
                f"{', '.join(sorted(res.unpublished))} in the sources held here, "
                f"so those properties are NOT published and do NOT reach the "
                f"rate — the pack's own reference pad is used for them. Selecting "
                f"this pad cannot move the prediction through them, and no number "
                f"was invented.")

    disks = disk_catalog()
    dcanon, dentry = _lookup(disks, getattr(disk, "name", None))
    if getattr(disk, "name", None) and dcanon is None:
        res.warnings.append(
            f"conditioner disk '{disk.name}' is not in the consumables "
            f"catalogue. Known disks: {sorted(disks)}.")
    if dcanon:
        res.disk_name = dcanon
        unwired: List[str] = []
        for prop, fieldname in DISK_FIELD_MAP.items():
            spec = dentry.get(prop)
            value, source, conf = _spec_value(spec)
            wired = bool(isinstance(spec, dict) and spec.get("wired"))
            if getattr(disk, fieldname, None) is not None:
                continue
            if value is None:
                res.unpublished[fieldname] = source
                continue
            setattr(disk, fieldname, float(value))
            res.filled[fieldname] = float(value)
            res.sources[fieldname] = f"consumables.yaml disks.{dcanon}.{prop} " \
                                     f"[{conf}] {source}".strip()
            if not wired:
                unwired.append(fieldname)
        if unwired:
            res.warnings.append(
                f"disk '{dcanon}': {', '.join(sorted(unwired))} is recorded but "
                f"does NOT reach the removal rate. The conditioning model reacts "
                f"to the conditioning DUTY (down force, sweep, hours), not to the "
                f"grit design: the grit -> pad-asperity mapping has no determined "
                f"proportionality constant in the literature held here "
                f"(legacy/knowledge/performance/disk.yaml, status pack_only). "
                f"Changing the disk will therefore not change the number, and "
                f"pretending otherwise would be a fitted constant in disguise.")
    return res


def reference_pad_name(resolved) -> Optional[str]:
    """The pad name a pack declares its Kp was calibrated on, if any."""
    try:
        value = resolved.p_or("reference_pad_name", None)
    except Exception:                                   # pragma: no cover
        return None
    return str(value) if value else None


def pad_equals_pack_reference(resolved) -> bool:
    """True when this run's pad IS the pack's calibration pad, unmodified.

    Then the pack's Kp already contains this pad and any contact correction
    would double-count it — see the module docstring for the measured size of
    that error.
    """
    ref = reference_pad_name(resolved)
    cons = getattr(resolved, "consumables", None)
    if not ref or cons is None or not cons.pad_name:
        return False
    if cons.pad_name.lower() != ref.lower():
        return False
    # Any pad property the USER typed makes this a different pad from the
    # calibration one, so the correction must apply again.
    user_typed = {k for k in PAD_FIELD_MAP.values()
                  if getattr(resolved.recipe.pad, k, None) is not None
                  and k not in cons.filled}
    return not user_typed
