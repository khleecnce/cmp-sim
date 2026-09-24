"""Abrasive-TYPE-scoped physics: what changes when you swap ceria for silica.

Why this module exists
----------------------
Before it, ``slurry.abrasive.kind`` was accepted, stored, used to look up a
density for the viscosity estimate — and had **no effect whatsoever on the
predicted removal rate**. Running ``examples/oxide_baseline.yaml`` with
``kind: silica``, ``ceria``, ``alumina``, ``zirconia`` and ``diamond`` returned
a bit-identical 1601 A/min five times. That is the worst failure mode this
project recognises: an input accepted and silently discarded, with a confident
number returned as if the question had been answered.

Two things genuinely depend on the abrasive chemistry, and they are handled
separately here because they have different evidence:

1. **The concentration and size exponents are properties of the ABRASIVE, not
   of the film.** Measured sweeps split by abrasive and do not even share a
   sign (silica -0.05, alumina +0.29, ceria +0.87 on the same oxide film — see
   ``oxide_silica.yaml:abrasive_size_exponent``). A pack states the exponents
   for the abrasive it was calibrated with. If the user runs a different
   abrasive through that pack, the pack's exponents are *wrong for this run*
   and must be replaced by the ones scoped to the abrasive actually used, or
   the run must say the response is unknown. Silently keeping them is how a
   ceria sweep gets predicted with silica's sign.

2. **The absolute rate scale changes too**, and that is much harder to source.
   A pack's ``kp_m_per_pa`` was back-calculated from a measurement that already
   contained its own abrasive, so swapping the abrasive invalidates the scale.
   Only a *published, same-tool, same-recipe* comparison licenses a numeric
   ratio. Where one exists it lives in ``abrasives.yaml:relative_rate`` with its
   citation. Where none exists, this module refuses to invent one: it returns no
   factor and attaches a warning that the absolute rate is not anchored to the
   abrasive in the recipe, so the run must be read as a ranking.

Hardness ranking is deliberately NOT used as a silent fallback. Mohs order does
not predict CMP rate (ceria is softer than alumina and removes oxide faster;
silica is softer than the sapphire it polishes), so a hardness ratio dressed up
as a rate ratio would be a fabricated number wearing a citation.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

from cmp_sim.slurry.formulation import _load_db, ABRASIVE_DB_PATH, _lookup

#: Exponent keys that are scoped to the abrasive, not to the film. These are the
#: engine key names the solver's abrasive hook reads.
ABRASIVE_SCOPED_KEYS = ("abrasive_size_exponent", "abrasive_conc_exponent",
                        "abrasive_conc_half_wt_pct")

#: DB field name -> engine key name.
_DB_TO_ENGINE = {
    "size_exponent": "abrasive_size_exponent",
    "conc_exponent": "abrasive_conc_exponent",
    "saturation_conc_wt_pct": "abrasive_conc_half_wt_pct",
}


def _db() -> Dict[str, Any]:
    return _load_db(ABRASIVE_DB_PATH) or {}


def abrasive_entry(kind: str) -> Tuple[Optional[str], Dict[str, Any]]:
    """Canonical DB key and entry for an abrasive name or alias."""
    hit = _lookup((_db().get("abrasives", {}) or {}), str(kind or ""))
    if not hit:
        return None, {}
    return hit[0], (hit[1] or {})


def canonical_kind(kind: str) -> Optional[str]:
    return abrasive_entry(kind)[0]


def _spec_value(spec: Any) -> Tuple[Optional[float], Optional[str], Optional[str]]:
    """Unpack a ``{value, source, confidence}`` cell. Returns (value, source, confidence)."""
    if not isinstance(spec, dict):
        return (None, None, None)
    v = spec.get("value")
    if v is None:
        return (None, None, None)
    try:
        return (float(v), spec.get("source"), spec.get("confidence"))
    except (TypeError, ValueError):
        return (None, None, None)


@dataclass
class AbrasiveResolution:
    """What the abrasive in this recipe does, and what it could not be told."""
    kind: Optional[str] = None
    reference_kind: Optional[str] = None
    matches_reference: bool = True
    #: engine key -> value, scoped to the abrasive actually used
    overrides: Dict[str, Any] = field(default_factory=dict)
    #: engine key -> why the pack's value was dropped without a replacement
    withdrawn: Dict[str, str] = field(default_factory=dict)
    relative_rate: Optional[float] = None
    relative_rate_source: Optional[str] = None
    notes: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    #: True when the absolute scale cannot be anchored to this abrasive
    ranking_only: bool = False

    def as_dict(self) -> Dict[str, Any]:
        return {
            "kind": self.kind,
            "reference_kind": self.reference_kind,
            "matches_reference": self.matches_reference,
            "overrides": dict(self.overrides),
            "withdrawn": dict(self.withdrawn),
            "relative_rate": self.relative_rate,
            "relative_rate_source": self.relative_rate_source,
            "ranking_only": self.ranking_only,
            "notes": list(self.notes),
            "warnings": list(self.warnings),
        }


def _relative_rate(film: str, kind: str, reference_kind: str
                   ) -> Tuple[Optional[float], Optional[str], Optional[str]]:
    """Published rate ratio ``kind / reference_kind`` on ``film``, or None.

    Reads ``abrasives.yaml:relative_rate[film][kind]``, each entry declaring the
    reference abrasive it was measured against. A ratio measured against a
    different reference is NOT rescaled here — chaining two independent ratios
    multiplies their errors and both were measured on different tools.
    """
    table = (_db().get("relative_rate", {}) or {}).get(film, {}) or {}
    spec = table.get(kind)
    if not isinstance(spec, dict):
        return (None, None, None)
    declared_ref = spec.get("reference")
    value, source, confidence = _spec_value(spec)
    if value is None:
        return (None, None, spec.get("note"))
    if declared_ref != reference_kind:
        return (None, None,
                f"the published {kind}/{declared_ref} ratio on {film} cannot be "
                f"applied here because this pack's reference abrasive is "
                f"'{reference_kind}', and chaining ratios measured on different "
                f"tools multiplies their errors")
    return (value, source, confidence)


def resolve(kind: Optional[str], film: str, reference_kind: Optional[str],
            pack_declares: Dict[str, bool]) -> AbrasiveResolution:
    """Decide what an abrasive swap does to this run.

    Parameters
    ----------
    kind:
        ``slurry.abrasive.kind`` as the user wrote it (alias or canonical).
    film:
        Wafer film, used to scope the per-film exponents in the DB.
    reference_kind:
        The abrasive the pack's ``kp_m_per_pa`` was calibrated with, i.e.
        ``reference_abrasive`` in the pack. ``None`` means the pack never said,
        which is itself reported: without it an abrasive swap cannot be detected.
    pack_declares:
        ``{engine_key: True}`` for abrasive-scoped keys the pack gives a
        non-null value for. Used to explain what is being replaced.
    """
    out = AbrasiveResolution()
    if not kind:
        return out

    canon, entry = abrasive_entry(kind)
    out.kind = canon
    if canon is None:
        out.warnings.append(
            f"abrasive '{kind}' is not in the abrasive database, so none of its "
            "concentration or size behaviour can be applied: the run uses this "
            "pack's reference abrasive instead and the rate is not anchored to "
            f"'{kind}'")
        out.ranking_only = True
        return out

    ref_canon = canonical_kind(reference_kind) if reference_kind else None
    out.reference_kind = ref_canon
    if ref_canon is None:
        out.warnings.append(
            "this pack does not declare reference_abrasive, so the simulator "
            "cannot tell whether the abrasive in this recipe is the one the "
            f"pack's Kp was calibrated with. '{canon}' was accepted but its "
            "abrasive-specific response could not be checked against the "
            "pack's own")
        return out

    if canon == ref_canon:
        out.matches_reference = True
        out.notes.append(
            f"abrasive '{canon}' is the abrasive this pack was calibrated with, "
            "so the abrasive-type factor is exactly 1.0 by construction (the "
            "pack's Kp already contains it)")
        return out

    # --- the abrasive was swapped -------------------------------------------
    out.matches_reference = False
    film_block = ((entry.get("film_effects", {}) or {}).get(film, {}) or {})

    for db_field, engine_key in _DB_TO_ENGINE.items():
        value, source, _conf = _spec_value(film_block.get(db_field))
        if value is not None:
            out.overrides[engine_key] = value
            out.notes.append(
                f"{engine_key} = {value:g} taken from the {canon}-on-{film} "
                f"entry, replacing the value this pack states for "
                f"'{ref_canon}' (source: {source})")
        elif pack_declares.get(engine_key):
            out.withdrawn[engine_key] = (
                f"the pack's {engine_key} was fitted for '{ref_canon}' and the "
                f"measured exponents split by ABRASIVE rather than by film — "
                f"they do not even share a sign — so it was withdrawn rather "
                f"than reused for '{canon}'. No fitted {db_field} for "
                f"{canon}-on-{film} exists in the abrasive database")

    ratio, source, note = _relative_rate(film, canon, ref_canon)
    if ratio is not None:
        out.relative_rate = ratio
        out.relative_rate_source = source
        out.notes.append(
            f"absolute rate scaled by the published {canon}/{ref_canon} ratio "
            f"of {ratio:g}x on {film} (source: {source})")
    else:
        out.ranking_only = True
        detail = f" {note}" if note else ""
        out.warnings.append(
            f"abrasive '{canon}' is not the abrasive this pack was calibrated "
            f"with ('{ref_canon}'), and no published same-recipe rate ratio for "
            f"{canon} vs {ref_canon} on {film} is available, so the ABSOLUTE "
            f"rate below is still anchored to '{ref_canon}'. A hardness ranking "
            f"was deliberately not substituted: Mohs order does not predict CMP "
            f"rate (ceria is softer than alumina and removes oxide faster). "
            f"Read this run as a ranking, or supply measurements: with "
            f"'{canon}' to calibrate it.{detail}")

    mechanism = film_block.get("mechanism")
    ref_mech = (((abrasive_entry(ref_canon)[1].get("film_effects", {}) or {})
                 .get(film, {}) or {}).get("mechanism"))
    if mechanism and ref_mech and mechanism != ref_mech:
        out.notes.append(
            f"removal mechanism differs: '{canon}' on {film} — {mechanism}")
    if not film_block:
        out.warnings.append(
            f"the abrasive database has no entry for '{canon}' on film '{film}', "
            "so nothing abrasive-specific could be applied for this pairing")

    return out
