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


#: MRR ~ d**n, grouped by ABRASIVE MATERIAL rather than by film or by pack.
#:
#: Provenance: ``tools/size_derived_probe.py`` regressed every size sweep in the
#: corpus with >=3 distinct diameters at otherwise matched conditions and kept
#: the groups with r2 >= 0.5. The measured exponents span -0.45..+1.00, so a
#: SINGLE exponent (derived or fitted) is falsified — that verdict is pinned by
#: ``tests/test_size_exponent_is_material_property.py``. What the same probe
#: shows is that the scatter is ORGANISED BY ABRASIVE: the stdev of the material
#: means is 0.51 while the stdev of residuals WITHIN a material is 0.16 (3.2x).
#: Two alumina sweeps 15 years and 20x in diameter apart agree to 0.09; one
#: silica slurry set sits near zero on THREE different films in the same runs.
#:
#: So this table is a RE-ATTRIBUTION, not a derivation. It moves a constant from
#: per-pack scope (where each pack fitted its own) to per-material scope (where
#: several independent sweeps share one), which is fewer constants for the same
#: data — the project's scoring rule for progress. It is NOT derived physics: the
#: ordering does not track abrasive hardness (alumina 20 > silica 8 > ceria 6 GPa
#: is not the measured order silica < alumina < ceria/silica < ceria). The
#: chemical-tooth reading — a chemically active abrasive removes in proportion to
#: its reacted contact footprint, which grows with d, while an inert abrasive at
#: fixed solids loading trades particle count against contact area and cancels —
#: is a HYPOTHESIS consistent with the ordering, with only k=1 pure-ceria support.
#:
#: ``k`` is the number of independent sweeps and ``spread`` their range. A k=1
#: row must never be read as well-supported, which is why both are carried here
#: and surfaced in the note the solver attaches.
SIZE_EXPONENT_BY_ABRASIVE: Dict[str, Dict[str, Any]] = {
    "colloidal_silica": {
        "value": -0.13, "k": 3, "spread": (-0.45, 0.10),
        "sweeps": ("bouvet2002_ti_silica_size_sweep (-0.45)",
                   "bouvet2002_w_silica_size_sweep (-0.05)",
                   "wei2026_sic_silica_size_sweep (+0.10)"),
        "confidence": "low",
    },
    "alumina": {
        "value": 0.28, "k": 2, "spread": (0.24, 0.33),
        "sweeps": ("su2011_sic_alumina_size_sweep (+0.24, 1000-3500 nm)",
                   "lai2001_cu_alumina_size_sweep (+0.33, 50-1000 nm)"),
        "confidence": "low",
    },
    "ceria": {
        "value": 1.00, "k": 1, "spread": (1.00, 1.00),
        "sweeps": ("son2021_oxide_ceria_size_sweep (+1.00, 3-100 nm, r2 0.98)",),
        "confidence": "low",
    },
}

#: Mixed ceria-on-silica ("core-shell") particles measure +0.80 (k=2,
#: us20190127607a1 HDP-oxide +0.75 and TEOS +0.85). They are kept OUT of the
#: table above because the DB has no canonical key for the composite and
#: resolving them onto either parent material would assert a composition the
#: patent does not give.
SIZE_EXPONENT_COMPOSITE_NOTE = (
    "ceria/silica composite particles measure +0.80 (k=2, US20190127607A1), "
    "between the inert-silica and pure-ceria ends, but are not in this table "
    "because they resolve to neither parent material")


#: MRR ~ C_wt ** (+1/3) — a DERIVED, abrasive-INDEPENDENT concentration law.
#:
#: DERIVATION (Li 2021 surface-area-limited branch; Cook 1990 supply limit).
#: No constant is fitted here; the exponent falls out of geometry:
#:   1. At weight fraction C and particle diameter d the volumetric particle
#:      count is n ~ C / d**3.
#:   2. Only particles inside the pad-wafer gap remove material, and the gap
#:      admits a monolayer, so the participating count is the 2-D projection of
#:      the 3-D population: n_gap ~ n**(2/3) ~ C**(2/3) / d**2.
#:   3. The wafer load is set by the tool, not by the slurry, so the load per
#:      participating particle falls as 1 / n_gap. Under Luo-Dornfeld plastic
#:      indentation the volume removed per particle per pass scales as its
#:      load to the power 1/2 ... carrying Li 2021's algebra through gives
#:      MRR ~ n_gap * load**(1/2) ~ n_gap**(1/2) ~ C**(1/3).
#: The two competing branches predict different exponents (dilute active-count
#: limit +1, fully-saturated load-sharing 0), so this is a falsifiable choice,
#: not a curve shape with a free index.
#:
#: MEASURED CHECK (``tools/conc_derived_probe.py``, 18 sweeps / 16 with r2>=0.5):
#:   median m = +0.33, mean +0.28, sd 0.29; 13/16 groups within 0.25 of +1/3.
#: The material hypothesis that WORKED for the size exponent FAILS here:
#: between-material stdev 0.37 vs within-material 0.22 is only 1.6x, below the
#: 2x bar STATUS.md set in advance, and the three well-sampled materials agree
#: to 0.04 (diamond +0.30, silica +0.33, ceria +0.34) — the scatter is within
#: materials, not between them, which is the signature of ONE shared law.
#: Saturation is separately falsified: if the response were Langmuir-type the
#: chord slope would fall as the sweep's mean concentration rises, and the
#: correlation is +0.06 (essentially zero) over a 0.01-9 wt% span.
#:
#: This REMOVES a constant rather than renaming one: five packs each fitted
#: their own value (+0.227, +0.3333, +0.3333, -0.4295, -0.406) and two of those
#: are already +1/3 by another route.
#:
#: ⚠ WHAT IT DOES NOT COVER. Three dissenting groups are recorded rather than
#: excluded: entegris2022 SiC/alumina (-0.41, r2 0.92, 0.1-5 wt%) and two SiC
#: ceria groups from one DOE (-0.31 and +0.65 at identical 2-6 wt%, i.e. the
#: same slurry disagrees with itself by ~1.0 across pressure levels). All three
#: are SiC — a film hard enough that indentation, not reacted-layer supply, may
#: set the rate, which is the regime where branch (a) rather than (c) applies.
#: So this law is a FALLBACK for a swapped abrasive with no sweep of its own; it
#: does not override a pack's own measured value, and it never touches
#: ``abrasive_conc_half_wt_pct``, which is a wt% with units and plausibly
#: depends on pad and film rather than on the law above.
DERIVED_CONC_EXPONENT = 1.0 / 3.0

DERIVED_CONC_EXPONENT_WHY = (
    "derived surface-area-limited concentration exponent m = +1/3 "
    "(MRR ~ C**(1/3); Li 2021 branch, Cook 1990 supply limit): the gap admits "
    "a monolayer so n_gap ~ C**(2/3), and load per particle falls as 1/n_gap, "
    "leaving C**(1/3) with NO fitted constant. Measured corpus median is +0.33 "
    "over 16 sweeps (13/16 within 0.25); unlike the size exponent this one is "
    "NOT a material property (between/within 1.6x, below the 2x bar) and "
    "saturation is falsified (corr of slope with mean wt% = +0.06). Dissenters "
    "are all SiC, where indentation rather than reacted-layer supply may set "
    "the rate")


def _db() -> Dict[str, Any]:
    return _load_db(ABRASIVE_DB_PATH) or {}


def material_size_exponent(kind: str) -> Tuple[Optional[float], Optional[str]]:
    """Material-scoped ``MRR ~ d**n`` exponent for ``kind``, with provenance.

    Returns ``(None, None)`` for an abrasive with no measured sweep — deliberately
    NOT a derived fallback. A null here is read downstream as "the size axis is
    unknown for this abrasive"; the one time a derived exponent was substituted
    it carried the wrong SIGN on 8 of 10 measured sweeps.
    """
    row = SIZE_EXPONENT_BY_ABRASIVE.get(str(kind or ""))
    if not row:
        return (None, None)
    lo, hi = row["spread"]
    return (float(row["value"]),
            f"material-scoped size exponent for {kind}: n = {row['value']:+.2f} "
            f"from k={row['k']} independent sweep(s) spanning {lo:+.2f}..{hi:+.2f} "
            f"[{'; '.join(row['sweeps'])}]. Re-attribution of a per-pack fitted "
            f"constant to the material that the sweeps show actually carries it "
            f"(between-material stdev 0.51 vs within-material 0.16); NOT derived "
            f"from hardness, which predicts a different order")


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
    #: engine key -> provenance, for values borrowed from the MATERIAL-scoped
    #: table rather than from a film-scoped sweep of this exact pairing
    material_scoped: Dict[str, str] = field(default_factory=dict)
    #: engine key -> derivation, for values supplied by a LAW with no fitted
    #: constant (as opposed to ``material_scoped``, which is a re-attributed
    #: fitted constant). Kept separate so a report can never present a borrowed
    #: measurement as derived physics, or vice versa.
    derived: Dict[str, str] = field(default_factory=dict)
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
            "material_scoped": dict(self.material_scoped),
            "derived": dict(self.derived),
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
            continue
        # No film-scoped sweep for this abrasive. For the SIZE exponent only,
        # fall back to the MATERIAL-scoped value: the corpus shows the exponent
        # is organised by abrasive material and transfers ACROSS films within one
        # material (bouvet2002's silica sits near zero on Ti, W and oxide in the
        # same runs; the two alumina sweeps agree to 0.09 on SiC and Cu), whereas
        # it does not transfer across materials at all. This is not licensed for
        # the CONCENTRATION keys: no equivalent cross-film check has been run on
        # them, so they still withdraw rather than borrow.
        if engine_key == "abrasive_size_exponent":
            mat_value, mat_why = material_size_exponent(canon)
            if mat_value is not None:
                out.overrides[engine_key] = mat_value
                out.material_scoped[engine_key] = mat_why or ""
                out.notes.append(
                    f"{engine_key} = {mat_value:+g} for '{canon}' — {mat_why}. "
                    f"This pack's own value was fitted for '{ref_canon}' and is "
                    f"not transferable across abrasive materials")
                continue
        # The CONCENTRATION exponent takes the DERIVED +1/3 instead, because the
        # material split that licensed the size table was tested here and FAILED
        # (between/within 1.6x < the 2x bar), while the derived surface-area law
        # lands on the corpus median exactly. See DERIVED_CONC_EXPONENT above for
        # the derivation, the measured check and the SiC dissenters. Note this is
        # a law, not a borrow: it is abrasive-independent by construction, so no
        # per-material k or spread attaches to it.
        if engine_key == "abrasive_conc_exponent":
            out.overrides[engine_key] = DERIVED_CONC_EXPONENT
            out.derived[engine_key] = DERIVED_CONC_EXPONENT_WHY
            out.notes.append(
                f"{engine_key} = {DERIVED_CONC_EXPONENT:+.4f} — "
                f"{DERIVED_CONC_EXPONENT_WHY}. Replaces this pack's value, "
                f"which was fitted for '{ref_canon}'")
            continue
        if pack_declares.get(engine_key):
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
