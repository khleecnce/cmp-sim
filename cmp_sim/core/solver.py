"""Solver — resolve a Recipe against parameter packs and run a model.

Resolution order for every physical constant
--------------------------------------------
1. The value explicitly set on the Recipe (user input wins).
2. The parameter pack (``Slurry.pack``, or the film default map below).
3. ``ParamMissing`` — never a silent default.

The ``factors`` dict on the result holds dimensionless multipliers applied to
Kp. They are all 1.0 at a pack's reference condition so that adding a physics
layer cannot silently re-scale a literature-calibrated Kp.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional

import numpy as np

from cmp_sim.core.params import ParamMissing, ParamPack, load_pack
from cmp_sim.core.state import Recipe, Result
from cmp_sim.core.units import psi_to_pa
from cmp_sim.models import preston as preston_model

# Film -> default parameter pack. Packs are inherited from legacy/knowledge/params
# (FabSim) unless overridden in cmp_sim/data/params.
FILM_PACK: Dict[str, str] = {
    "oxide": "oxide_silica",
    "oxide_ceria": "sti_ceria",
    "sti": "sti_ceria",
    "cu": "cu_h2o2_bta",
    "w": "w_fe_oxidizer",
    "sic": "sic_ceria_h2o2",
    "poly_si": "poly_si_alkaline",
    "si": "si_substrate_alkaline",
    "snag": "snag_solder",
}

#: fitted factor name -> the pack key the solver reads it from
FACTOR_PARAM = {
    "pressure_exponent": "pressure_exponent",
    "velocity_exponent": "velocity_exponent",
    # These land on keys the existing physics layers already read, so a fitted
    # value replaces the literature one in place rather than bolting on a
    # parallel term that could double-count it.
    "abrasive_half_wt_pct": "abrasive_conc_half_wt_pct",
    "abrasive_size_exponent": "abrasive_size_exponent",
    "oxidizer_langmuir_K": "oxidizer_langmuir_K",
    "activation_energy_kj_per_mol": "chem_activation_energy_kj_per_mol",
}

FactorFn = Callable[["ResolvedRecipe"], Dict[str, Any]]
_FACTOR_HOOKS: List[FactorFn] = []


def register_factor(fn: FactorFn) -> FactorFn:
    """Register a Kp multiplier hook. Hook returns
    ``{"name": str, "value": float, "notes": [...], "warnings": [...]}``."""
    _FACTOR_HOOKS.append(fn)
    return fn


def clear_factors() -> None:
    _FACTOR_HOOKS.clear()


@dataclass
class ResolvedRecipe:
    """A Recipe with every physical constant resolved to a number."""
    recipe: Recipe
    pack: ParamPack
    used_keys: List[str] = field(default_factory=list)
    formulation_notes: List[str] = field(default_factory=list)
    formulation_warnings: List[str] = field(default_factory=list)
    #: blanket rate [m/s], filled in once the rate layers have run (P6 needs it)
    blanket_rate_m_per_s: Optional[float] = None
    #: fit to the owner's measurements, when any were supplied
    calibration: Any = None
    #: Kp estimated from material properties, when none was available
    estimate: Any = None
    #: physical factors fitted to owner measurements
    factor_fit: Any = None
    #: how well established CMP is on this film
    maturity: Any = None
    #: the resolved model profile; decides which physics layers run
    profile: Any = None
    #: the detected physical situation
    situation: Any = None
    #: what the abrasive TYPE in this recipe does (AbrasiveResolution)
    abrasive_resolution: Any = None
    #: what the named pad/disk supplied (ConsumableResolution)
    consumables: Any = None

    # ── pack access ────────────────────────────────────────────
    def p(self, key: str) -> Any:
        v = self.pack.get(key)          # raises ParamMissing when absent
        if key not in self.used_keys:
            self.used_keys.append(key)
        return v

    def p_or(self, key: str, default: Any) -> Any:
        if key in self.pack.params:
            return self.p(key)
        return default

    def has(self, key: str) -> bool:
        return key in self.pack.params

    # ── geometry / tool ───────────────────────────────────────
    @property
    def wafer_radius_m(self) -> float:
        w = self.recipe.wafer
        if w.diameter_mm:
            return float(w.diameter_mm) * 1e-3 / 2.0
        return float(self.p("wafer_radius_m"))

    @property
    def center_offset_m(self) -> float:
        t = self.recipe.tool
        return float(t.center_offset_m if t.center_offset_m is not None
                     else self.p("center_offset_m"))

    @property
    def pressure_pa(self) -> float:
        return psi_to_pa(self.recipe.tool.pressure_psi)

    @property
    def zone_pressures_pa(self) -> Optional[List[float]]:
        zp = self.recipe.tool.zone_pressures_psi
        return [psi_to_pa(p) for p in zp] if zp else None

    @property
    def kp_base(self) -> float:
        """The Preston coefficient, or a refusal that explains itself.

        A pack is allowed to leave Kp null — that is how an honestly unknown
        value is recorded. What must not happen is the null reaching float()
        and surfacing as "float() argument must be ... not 'NoneType'", which
        says nothing about which film or which number is missing.
        """
        value = self.p("kp_m_per_pa")
        if value is None:
            param = self.pack.params.get("kp_m_per_pa")
            note = ""
            if param is not None and getattr(param, "note", None):
                first = str(param.note).strip().splitlines()[0]
                note = f" The pack says: {first}"
            raise ParamMissing(
                f"no Preston coefficient is available for film "
                f"'{self.recipe.wafer.film}' (pack '{self.pack.name}'). "
                f"kp_m_per_pa is null, which means it has not been sourced "
                f"rather than that it is zero, so no removal rate can be "
                f"computed.{note} Supply one in a pack override, or pass a "
                f"different pack with slurry.pack.")
        return float(value)


def resolve(recipe: Recipe) -> ResolvedRecipe:
    """Load the pack for this recipe and overlay the user's formulation.

    The formulation overlay is what makes the simulator respond to composition:
    without it, changing the oxidizer or the abrasive loading would leave the
    pack values (and therefore the answer) untouched.
    """
    name = recipe.slurry.pack or FILM_PACK.get(recipe.wafer.film)
    if not name:
        raise ParamMissing(
            f"no parameter pack for film '{recipe.wafer.film}'. "
            f"Set slurry.pack explicitly or add the film to FILM_PACK. "
            f"Known films: {sorted(FILM_PACK)}"
        )
    # An explicit pack used to let wafer.film through unchecked, so asking for
    # film 'cu' with pack 'oxide_silica' silently returned the OXIDE rate under
    # a copper label - and asking for a film that does not exist at all returned
    # a number as if it did. Both are confidently wrong answers, which is the
    # failure mode this simulator exists to avoid.
    # Case and surrounding space are typing noise, not meaning: 'Cu' and 'cu'
    # are the same film, and refusing one of them teaches nothing. A name that
    # is genuinely not in the table is a different matter and is refused below.
    film = str(recipe.wafer.film or "").strip()
    if film and film not in FILM_PACK and film.lower() in FILM_PACK:
        film = film.lower()
        recipe.wafer.film = film
    if not film:
        raise ParamMissing(
            "wafer.film is required: the film sets the removal mechanism, the "
            "plausibility envelope and the maturity grade, none of which can be "
            f"inferred from the slurry alone. Known films: {sorted(FILM_PACK)}")
    if film not in FILM_PACK:
        near = [f for f in FILM_PACK if f.startswith(film.lower()[:2])]
        raise ParamMissing(
            f"unknown film '{film}'. The run was refused rather than returning "
            "the rate for whatever pack was loaded, which would be a wrong "
            f"answer wearing the right label. Known films: {sorted(FILM_PACK)}"
            + (f". Did you mean {near}?" if near else "")
            + (f". Note film names are lower-case: try '{film.lower()}'"
               if film.lower() in FILM_PACK else ""))
    expected = FILM_PACK[film]
    pack = load_pack(name)

    from cmp_sim.slurry.formulation import apply_overrides, to_overrides
    form = to_overrides(recipe.slurry)
    notes = list(form.notes)
    warnings = list(form.warnings)
    # A mismatch is warned about, not refused: trying a tungsten slurry on
    # copper is a legitimate screening experiment. But the pack's Kp was
    # back-calculated on ITS film, so the absolute rate transfers to another
    # film only by coincidence.
    if getattr(recipe.wafer, "film_was_defaulted", False):
        warnings.append(
            f"wafer.film was not stated, so '{film}' was assumed. The film "
            "selects the removal mechanism, the plausibility envelope and the "
            "maturity grade, so this is a guess at the answer rather than a "
            f"harmless default. State it explicitly: {sorted(FILM_PACK)}")
    if name != expected:
        warnings.append(
            f"pack '{name}' is the reference pack for a different film "
            f"(film '{film}' normally uses '{expected}'). The pack's Kp was "
            f"back-calculated from a measurement on that other film, so the "
            f"absolute rate here is not anchored to anything measured on "
            f"'{film}' - treat it as a ranking between recipes. Supply "
            f"measurements: to calibrate it to this film.")
    if form.overrides:
        pack, apply_notes = apply_overrides(pack, form.overrides)
        warnings.extend(apply_notes)

    # Owner measurements come before explicit params: fitting to real data is
    # the better source, but an explicitly stated number still wins over a fit.
    calibration = None
    if getattr(recipe, "measurements", None):
        from cmp_sim.core import calibration as calib

        offset = float(recipe.tool.center_offset_m
                       if recipe.tool.center_offset_m is not None
                       else pack.params["center_offset_m"].value)
        parsed = calib.from_dicts(recipe.measurements)
        calibration = calib.calibrate(parsed, center_offset_m=offset)

        # Beyond the scale: unlock whichever physical factors the data can
        # actually identify. Anything the data cannot see stays at its
        # literature value, with a note saying why.
        from cmp_sim.core import factor_fit as ff

        factor_result = ff.fit_factors(parsed, center_offset_m=offset,
                                       pressure_ref_psi=recipe.tool.pressure_psi)
        if factor_result.unlocked:
            overrides = {"kp_m_per_pa": factor_result.kp_m_per_pa}
            overrides.update({FACTOR_PARAM[k]: v
                              for k, v in factor_result.values.items()
                              if k in FACTOR_PARAM})
            pack, ff_notes = apply_overrides(
                pack, overrides,
                source=f"fitted to {factor_result.n_points} owner measurement(s)")
            warnings.extend(ff_notes)
            # the factor fit supersedes the scale-only calibration
            calibration.kp_m_per_pa = factor_result.kp_m_per_pa
            calibration.cv_mape = factor_result.cv_mape
            if factor_result.residuals:
                calibration.residuals = factor_result.residuals
        notes.extend(factor_result.notes)
        warnings.extend(factor_result.warnings)

        if calibration.kp_m_per_pa and not factor_result.unlocked:
            pack, fit_notes = apply_overrides(
                pack, {"kp_m_per_pa": calibration.kp_m_per_pa},
                source=f"fitted to {calibration.n_points} owner measurement(s)")
            warnings.extend(fit_notes)
            notes.extend(calibration.notes)
            warnings.extend(calibration.warnings)

    # Explicit params: are applied BEFORE the estimate, so that an owner who
    # overrides the hardness (or clears it) changes what the estimate sees.
    # Applying them afterwards let the estimator read a value the user had
    # already replaced.
    if recipe.params:
        pack, apply_notes = apply_overrides(
            pack, dict(recipe.params), source="owner-provided (recipe.params)")
        warnings.extend(apply_notes)
        notes.append(
            "owner-supplied parameters override the pack: "
            + ", ".join(sorted(recipe.params)))

    # If no Kp exists anywhere, fall back to the Archard estimate from hardness.
    # Ranked below both measurements and an explicit params: value, because it
    # is an order-of-magnitude correlation rather than a measurement.
    estimate = None
    kp_param = pack.params.get("kp_m_per_pa")
    kp_missing = kp_param is None or getattr(kp_param, "value", None) is None
    if kp_missing and not (recipe.params or {}).get("kp_m_per_pa"):
        from cmp_sim.models import first_principles as fp

        estimate = fp.estimate_for_pack(
            pack, recipe.wafer.film,
            temp_c=(recipe.slurry.temperature_c
                    if recipe.slurry.temperature_c is not None else 25.0),
            pressure_psi=recipe.tool.pressure_psi)
        if estimate.ok:
            pack, est_notes = apply_overrides(
                pack, {"kp_m_per_pa": estimate.kp_m_per_pa},
                source="estimated from hardness (Archard), not measured")
            warnings.extend(est_notes)
            notes.extend(estimate.notes)
            warnings.extend(estimate.warnings)
        else:
            warnings.extend(estimate.warnings)

    # Named pad/disk -> properties, from the sourced consumables catalogue.
    # Done here, before any physics layer reads the pad, so every layer sees the
    # same pad. Explicit values on the Pad/Disk object keep priority; a property
    # the catalogue does not publish stays None and is disclosed rather than
    # invented.
    from cmp_sim.pad.catalog import apply_catalog

    consumables = apply_catalog(recipe.pad, recipe.disk)
    notes.extend(consumables.notes)
    warnings.extend(consumables.warnings)

    rr = ResolvedRecipe(recipe=recipe, pack=pack,
                        formulation_notes=notes, formulation_warnings=warnings)
    rr.consumables = consumables
    rr.calibration = calibration
    rr.estimate = estimate
    rr.factor_fit = factor_result if recipe.measurements else None
    return rr


def _models_table() -> Dict[str, str]:
    """Selectable models = profiles + the legacy aliases + auto."""
    from cmp_sim.core.profiles import ALIASES, PROFILES
    out = {name: p.description for name, p in PROFILES.items()}
    out["auto"] = "pick the profile that fits the detected situation"
    for alias, target in ALIASES.items():
        out[alias] = (f"alias for '{target}'" if target
                      else "resolved per situation (same as 'auto')")
    return out


MODELS: Dict[str, str] = _models_table()


def _exponent_hook(rr: ResolvedRecipe) -> Dict[str, Any]:
    """Apply pressure/velocity exponents fitted to the owner's measurements.

    Preston fixes both at 1. When the owner's data say otherwise, the departure
    is applied here as a multiplier relative to this run's own conditions, so
    the fit is reproduced at the conditions it was made at and extrapolates by
    the fitted power elsewhere.
    """
    out: Dict[str, Any] = {}
    n_p = rr.p_or("pressure_exponent", None)
    n_v = rr.p_or("velocity_exponent", None)
    if n_p is None and n_v is None:
        return out

    import numpy as np

    from cmp_sim.models import uniformity as un

    factor = 1.0
    notes = []
    if n_p is not None and abs(float(n_p) - 1.0) > 1e-9:
        # relative to the pressure the fit was referenced to, which is this
        # run's own pressure: the multiplier is 1.0 there by construction.
        factor *= 1.0
        notes.append(
            f"pressure exponent {float(n_p):.3f} fitted from your data "
            "(Preston assumes 1.000)")
    if n_v is not None and abs(float(n_v) - 1.0) > 1e-9:
        _r, v = un.relative_speed_profile(
            rr.wafer_radius_m, rr.center_offset_m,
            rr.recipe.tool.rpm_head, rr.recipe.tool.rpm_platen)
        v_mean = float(np.mean(v))
        v_ref = float(rr.p_or("velocity_ref_m_s", v_mean) or v_mean)
        if v_mean > 0 and v_ref > 0:
            factor *= (v_mean / v_ref) ** (float(n_v) - 1.0)
        notes.append(
            f"velocity exponent {float(n_v):.3f} fitted from your data "
            "(Preston assumes 1.000)")
    if notes:
        out = {"name": "fitted_exponents", "value": factor, "notes": notes}
    return out


def _passivation_threshold_hook(rr: ResolvedRecipe) -> Dict[str, Any]:
    """Threshold-Preston for films that must have a passivation layer sheared
    off before removal starts (P4 x P1 coupling).

    Derivation, measured support and the partial falsification kept with it are
    in ``cmp_sim/models/passivation_threshold.py``. The hook only fires when the
    PACK declares both constants, so a film with no measured threshold keeps
    plain Preston rather than inheriting a borrowed one.
    """
    yield_psi = rr.p_or("passivation_yield_pressure_psi", None)
    k_l = rr.p_or("inhibitor_langmuir_K_per_ppm", None)
    if yield_psi is None or k_l is None:
        return {}
    inhibitor_ppm = rr.p_or("inhibitor_ppm", None)
    if inhibitor_ppm is None:
        # A declared threshold with no inhibitor loading is a gap, not a zero:
        # assuming 0 ppm would silently claim P0 = 0 and hide the missing input.
        return {"name": "passivation_threshold", "value": 1.0,
                "warnings": ["pack declares a passivation shear threshold but "
                             "no inhibitor_ppm is set for this run — the "
                             "threshold was NOT applied"]}

    from cmp_sim.models.passivation_threshold import (
        passivation_threshold_factor)

    pressure_psi = rr.pressure_pa / 6894.757293168361
    res = passivation_threshold_factor(pressure_psi, float(inhibitor_ppm),
                                       float(yield_psi), float(k_l))
    return {"name": "passivation_threshold", "value": res.factor,
            "notes": res.notes, "warnings": res.warnings, "terms": res.terms}


def _kappa_contact_hook(rr: ResolvedRecipe) -> Dict[str, Any]:
    """P2 — pad contact mechanics."""
    if not rr.profile.enabled("contact"):
        return {}
    from cmp_sim.pad.catalog import pad_equals_pack_reference
    from cmp_sim.pad.material import contact_factor_for

    # Selecting the pad the pack was CALIBRATED on must not rescale the rate.
    # kappa is a ratio against the pack's reference pad, so if the catalogue's
    # published Shore D is pushed through the Qi correlation while the reference
    # pad's E* was measured directly on that same physical pad, the two numbers
    # disagree by construction and kappa moves the rate by nothing but that
    # disagreement. Measured on oxide_silica_calibrated_pad: 1.9x for choosing
    # IC1000, the very pad its Kp is anchored to.
    if pad_equals_pack_reference(rr):
        name = rr.consumables.pad_name
        return {"name": "kappa_contact", "value": 1.0, "notes": [
            f"GW contact: '{name}' IS the pad this pack's Kp was calibrated on "
            f"(reference_pad_name), so kappa = 1.0 exactly. Applying the "
            f"correlation-derived modulus against the pack's directly measured "
            f"reference pad would rescale the rate by the disagreement between "
            f"two descriptions of the same pad, not by any physical difference."]}

    out = contact_factor_for(rr.recipe, rr)
    out.pop("state", None)
    return out


def _abrasive_type_hook(rr: ResolvedRecipe) -> Dict[str, Any]:
    """Which ABRASIVE is this, and what does swapping it change?

    Runs before ``_abrasive_hook`` because it rewrites the very exponents that
    hook reads. Before this existed, ``slurry.abrasive.kind`` had no effect on
    the rate at all: silica, ceria, alumina, zirconia and diamond returned a
    bit-identical 1601 A/min on examples/oxide_baseline.yaml.
    """
    from cmp_sim.slurry import abrasive_effects as ae

    kind = getattr(rr.recipe.slurry.abrasive, "kind", None)
    reference = rr.p_or("reference_abrasive", None)
    declares = {k: (rr.p_or(k, None) is not None) for k in ae.ABRASIVE_SCOPED_KEYS}
    res = ae.resolve(kind=kind, film=str(rr.recipe.wafer.film or ""),
                     reference_kind=reference, pack_declares=declares)
    rr.abrasive_resolution = res

    # Rewrite the pack in place so the downstream abrasive hook reads the
    # exponents scoped to the abrasive ACTUALLY used, not the pack's own.
    from sim.params import Param
    for key, value in res.overrides.items():
        mat_why = res.material_scoped.get(key)
        rr.pack.params[key] = Param(
            key=key, value=value, unit="dimensionless",
            source=(f"abrasive_effects.SIZE_EXPONENT_BY_ABRASIVE: {res.kind} "
                    f"(material-scoped, film-independent)" if mat_why
                    else f"abrasives.yaml: {res.kind} on {rr.recipe.wafer.film}"),
            confidence="literature",
            note=(mat_why if mat_why else
                  "scoped to the abrasive in this recipe, replacing the pack's "
                  f"value for '{res.reference_kind}'"),
            owner="abrasive_effects")
    for key, why in res.withdrawn.items():
        rr.pack.params[key] = Param(
            key=key, value=None, unit="dimensionless",
            source=f"withdrawn by abrasive_effects for {res.kind}",
            confidence="unverified", note=why, owner="abrasive_effects")

    out: Dict[str, Any] = {"notes": res.notes, "warnings": res.warnings,
                           "abrasive_type": res.as_dict()}
    if res.relative_rate is not None:
        out["name"] = "abrasive_type"
        out["value"] = res.relative_rate
    return out


def _abrasive_hook(rr: ResolvedRecipe) -> Dict[str, Any]:
    """P3 — abrasive count / size / load mechanics."""
    if not rr.profile.enabled("abrasive"):
        return {}
    from cmp_sim.models import luo_dornfeld as ld

    # When the abrasive was swapped and no exponents exist for the one actually
    # used, the composition axis is UNKNOWN, not neutral. Falling through to the
    # derived exponent is the specific trap this project already paid for: a
    # null abrasive_size_exponent selected a derived -0.84 whose sign was wrong
    # for 8 of 10 measured sweeps. So the axis is reported as unevaluated and
    # the rate stays at the reference composition rather than being moved by a
    # number that belongs to a different abrasive.
    res = getattr(rr, "abrasive_resolution", None)
    if res is not None and res.withdrawn and not res.overrides:
        return {"name": "chi_abrasive", "value": None,
                "notes": [],
                "warnings": [
                    f"abrasive loading and particle size were NOT applied: the "
                    f"exponents in this pack were fitted for "
                    f"'{res.reference_kind}' and the abrasive in this recipe is "
                    f"'{res.kind}', for which the abrasive database has no fitted "
                    f"concentration or size exponent on film "
                    f"'{rr.recipe.wafer.film}'. The derived exponent was NOT used "
                    f"as a fallback: it once had the wrong SIGN on 8 of 10 "
                    f"measured sweeps, so substituting it would move the rate in "
                    f"a direction nothing measured. Supply measurements: with "
                    f"'{res.kind}' at two loadings and two sizes to unlock this "
                    f"axis."]}

    # PER-AXIS withdrawal. Until 2026-09-28 the check above was all-or-nothing
    # (``withdrawn and not overrides``), which was safe only while a swap either
    # supplied BOTH exponents or neither. The derived concentration law
    # (DERIVED_CONC_EXPONENT) broke that assumption: it always supplies the conc
    # exponent, so ``overrides`` is never empty, the guard above stopped firing,
    # and a WITHDRAWN size exponent fell through as a null — which luo_dornfeld
    # reads as "use the derived size exponent", i.e. exactly the falsified -0.84
    # whose sign was wrong on 8 of 10 measured sweeps. A diamond run's rate moved
    # 6.8x over a 10x size step on a withdrawn axis before this was caught.
    # An axis that was withdrawn must be INERT, not defaulted, so each axis is
    # neutralised independently by removing its reference point: with no
    # reference the ratio has nothing to be relative TO, which is how the rest of
    # this hook already expresses "not applied".
    withdrawn_axes = set((res.withdrawn or {}).keys()) if res is not None else set()

    conc = rr.p_or("abrasive_wt_pct", None)
    d50 = rr.p_or("abrasive_size_nm", None)
    # `abrasive_d50_nm` is the same quantity under a different name, and it is
    # the name most of the measured datasets use. Reading only one of the two
    # meant a size override was ACCEPTED and then silently dropped: quadrupling
    # the particle diameter returned a bit-identical rate. An ignored input is
    # the most dangerous kind of bug here, because the run still looks like an
    # answer to the question that was asked.
    if d50 is None:
        d50 = rr.p_or("abrasive_d50_nm", None)
    d50_ref = rr.p_or("abrasive_ref_size_nm", None)
    conc_ref = rr.p_or("abrasive_ref_wt_pct", None)
    axis_warnings: List[str] = []
    if res is not None and "abrasive_size_exponent" in withdrawn_axes:
        d50_ref = None
        axis_warnings.append(
            f"the particle-SIZE axis was NOT applied for '{res.kind}': "
            f"{res.withdrawn['abrasive_size_exponent']}. The derived exponent "
            f"was not substituted — it had the wrong sign on 8 of 10 measured "
            f"sweeps. The concentration axis was still applied (derived law).")
    if res is not None and "abrasive_conc_exponent" in withdrawn_axes:
        conc_ref = None
        axis_warnings.append(
            f"the abrasive-LOADING axis was NOT applied for '{res.kind}': "
            f"{res.withdrawn['abrasive_conc_exponent']}")
    if conc is None and d50 is None:
        return {"name": "chi_abrasive", "value": None,
                "notes": ["abrasive mechanics inactive: the pack declares neither "
                          "abrasive_wt_pct nor abrasive_size_nm"]}

    # The GW layer tells us how the real contact area responds to pressure,
    # which is precisely the input the load-sharing question needs.
    from cmp_sim.pad.material import pad_state, reference_pad_state
    try:
        state, _n, _w = pad_state(rr.recipe.pad, rr)
        p_lo, p_hi = 0.5 * rr.pressure_pa, 2.0 * rr.pressure_pa
        a_lo = state.real_area_fraction(p_lo)
        a_hi = state.real_area_fraction(p_hi)
        area_pressure_exponent = float(np.log(a_hi / a_lo) / np.log(p_hi / p_lo))
    except Exception:                                    # pragma: no cover
        area_pressure_exponent = None

    # The situation was already detected before physics was chosen, so its
    # non-circular contact branch is available here and supersedes the
    # particle-contact-stress route that is null in every pack.
    detected_branch = None
    situation = getattr(rr, "situation", None)
    if situation is not None:
        detected_branch = getattr(situation, "contact_branch", None)
    regime = ld.resolve_regime(
        contact_branch=detected_branch,
        area_pressure_exponent=area_pressure_exponent,
        contact_stress_pa=rr.p_or("particle_contact_stress_pa", None),
        surface_hardness_pa=rr.p_or("film_surface_hardness_pa", None),
        gap_m=rr.p_or("pad_wafer_gap_m", None),
        particle_diameter_m=(float(d50) * 1e-9) if d50 else None,
    )
    factor, notes, warnings = ld.mechanical_factor(
        conc=conc, conc_ref=conc_ref, diameter_nm=d50, diameter_ref_nm=d50_ref,
        regime=regime, conc_half=rr.p_or("abrasive_conc_half_wt_pct", None),
        measured_size_exponent=rr.p_or("abrasive_size_exponent", None),
        measured_conc_exponent=rr.p_or("abrasive_conc_exponent", None))
    if conc is not None and not conc_ref:
        warnings.append(
            "the pack has no abrasive_ref_wt_pct, so the concentration term has no "
            "reference point and abrasive loading does not affect the result")
    return {"name": "chi_abrasive", "value": factor,
            "notes": notes, "warnings": axis_warnings + warnings,
            "regime": regime.as_dict()}


def _supply_diagnostic(rr: ResolvedRecipe) -> Dict[str, Any]:
    """P5 — slurry supply and lubrication regime. Diagnostic, not a Kp factor.

    Starvation is reported rather than applied: how sharply the centre droops
    at a given flow depends on groove pattern and injection geometry, which we
    cannot derive. A profile is applied only when the pack supplies a
    calibrated starvation length.
    """
    from cmp_sim.models import uniformity as un
    from cmp_sim.slurry.rheology import derive as derive_slurry, water_viscosity_pa_s

    tool = rr.recipe.tool
    temp_c = (rr.recipe.slurry.temperature_c
              if rr.recipe.slurry.temperature_c is not None else 25.0)

    viscosity = rr.recipe.slurry.viscosity_pa_s
    if viscosity is None:
        conc = rr.p_or("abrasive_wt_pct", None)
        density = rr.p_or("abrasive_density_kg_m3", None)
        if conc and density:
            viscosity = derive_slurry(float(conc), float(density),
                                      temp_c=temp_c).viscosity_pa_s
        else:
            viscosity = water_viscosity_pa_s(temp_c)

    _rs, v = un.relative_speed_profile(rr.wafer_radius_m, rr.center_offset_m,
                                       tool.rpm_head, tool.rpm_platen, n_radial=21)
    mean_speed = float(np.mean(v))

    pad = rr.recipe.pad
    roughness = float(pad.roughness_beta_inv_m or rr.p("pad_height_beta_inv_m"))
    groove_depth_m = (float(pad.groove_depth_mm) * 1e-3) if pad.groove_depth_mm else None
    gfq = 0.25
    if pad.groove_width_mm and pad.groove_pitch_mm:
        gfq = float(pad.groove_width_mm) / float(pad.groove_pitch_mm)

    state = un.diagnose_supply(
        flow_ml_min=tool.flow_ml_min, wafer_radius_m=rr.wafer_radius_m,
        mean_speed_m_s=mean_speed, pressure_pa=rr.pressure_pa,
        viscosity_pa_s=float(viscosity), pad_roughness_m=roughness,
        groove_depth_m=groove_depth_m, groove_area_fraction=gfq)
    return {"name": "_supply", "value": None, "notes": state.notes,
            "warnings": state.warnings, "supply": state.as_dict(),
            "supply_state": state, "mean_speed_m_s": mean_speed}


def _defect_diagnostic(rr: ResolvedRecipe) -> Dict[str, Any]:
    """P8 — scratch-risk index. Diagnostic only; never multiplied into MRR."""
    from cmp_sim.models import defect_proxy as dp

    risk = dp.evaluate(
        d99_nm=rr.p_or("abrasive_d99_nm", None),
        d99_ref_nm=rr.p_or("abrasive_ref_d99_nm", None),
        exponent=rr.p_or("damage_exponent", None),
        aggregate_ratio=rr.p_or("aggregate_ratio", None),
        d50_nm=rr.p_or("abrasive_size_nm", None),
        pad_hardness_pa=rr.p_or("pad_asperity_hardness_max_pa", None),
        film_hardness_pa=rr.p_or("film_bulk_hardness_pa", None),
        # Every pack declares this with its own citation; until now the model
        # hardcoded 680 nm and the pack key could not reach any output.
        scratch_threshold_nm=rr.p_or("scratch_threshold_nm", None),
        film=rr.recipe.wafer.film,
    )
    return {"name": "_defect", "value": None, "notes": risk.notes,
            "warnings": risk.warnings, "defect": risk.as_dict()}


def _pad_life_diagnostic(rr: ResolvedRecipe) -> Dict[str, Any]:
    """P7 — pad glazing and conditioner ageing. Diagnostic only.

    The drift is reported rather than applied to Kp: the inherited MRR proxy
    peaks at ~7 min against a measured ~3 min, so using it as a multiplier
    would claim a precision the data does not support.
    """
    from cmp_sim.pad import wear

    pad, disk = rr.recipe.pad, rr.recipe.disk
    if not (pad.use_hours or disk.hours_used):
        return {}
    state = wear.evaluate(
        pressure_psi=rr.recipe.tool.pressure_psi,
        polish_minutes=float(pad.use_hours) * 60.0,
        disk_hours=float(disk.hours_used),
        glazing_rate=rr.p_or("pad_glazing_rate", None),
        conditioning_rate=rr.p_or("pad_conditioning_rate", None),
    )
    return {"name": "_pad_life", "value": None, "notes": state.notes,
            "warnings": state.warnings, "pad_life": state.as_dict()}


def _pattern_diagnostic(rr: ResolvedRecipe) -> Dict[str, Any]:
    """P6 — dishing and erosion for a patterned wafer. Diagnostic only."""
    from cmp_sim.models import pattern_density as pdm

    w = rr.recipe.wafer
    if w.pattern_density is None:
        return {}
    pl = rr.p_or("planarization_length_m", None)
    if not pl:
        return {"name": "_pattern", "value": None, "warnings": [
            "a pattern density was given but this pack has no planarization "
            "length, so pattern effects were NOT computed. The planarization "
            "length is a pad/process property and is not guessed"]}

    step0 = rr.p_or("initial_step_height_m", None)
    # The initial step height is an APPLICATION choice, not a material constant:
    # poly-Si spans 190 nm (logic/STI) to >=5 um (MEMS), a 25x range, and
    # planarisation time is linear in it. A pack can only carry one value, so
    # the assumption is stated rather than left inside the pack file where
    # nobody reads it.
    if step0:
        param = rr.pack.params.get("initial_step_height_m")
        scale = ""
        if param is not None and getattr(param, "note", None):
            head = str(param.note).strip().splitlines()[0]
            scale = f" Pack says: {head}"
        rr_notes_step = (
            f"initial step height {float(step0) * 1e9:.0f} nm is the pack's "
            f"assumed application scale, not a property of the film. "
            f"Planarisation time is linear in it, so override "
            f"initial_step_height_m under params: if your layer differs."
            + scale)
    else:
        rr_notes_step = None

    if not step0:
        return {"name": "_pattern", "value": None, "warnings": [
            "a pattern density was given but no initial step height "
            "(initial_step_height_m) is available, so step-height evolution "
            "was NOT computed"]}

    # Uniform density array across one die; a real layout map is a future input.
    span = float(rr.p_or("die_size_m", 0.02))
    x = np.linspace(0.0, span, 201)
    rho = np.full_like(x, float(w.pattern_density))

    res = pdm.evaluate(
        blanket_rate_m_per_s=float(rr.blanket_rate_m_per_s or 0.0),
        rho_local=rho, x_m=x, planarization_length_m=float(pl),
        initial_step_m=float(step0), time_s=rr.recipe.tool.time_s,
        rate_stop_m_per_s=rr.p_or("stop_layer_rate_m_per_s", None),
        dishing_max_m=rr.p_or("dishing_max_m", None),
        oxide_sensitivity_b=rr.p_or("oxide_dishing_sensitivity_b", None),
        overpolish_time_s=float(rr.p_or("overpolish_time_s", 0.0)),
    )
    out = res.as_dict()
    notes = out.pop("notes", [])
    warnings = out.pop("warnings", [])
    if rr_notes_step:
        notes.insert(0, rr_notes_step)
    return {"name": "_pattern", "value": None, "notes": notes,
            "warnings": warnings, "pattern": out}


def _chemistry_hook(rr: ResolvedRecipe) -> Dict[str, Any]:
    """P4 — slurry chemistry through the softened-hardness channel."""
    if not rr.profile.enabled("chemistry"):
        return {}
    from cmp_sim.models.chemical_rate import chemical_factor

    temp_c = (rr.recipe.slurry.temperature_c
              if rr.recipe.slurry.temperature_c is not None
              else rr.recipe.tool.platen_temp_c)
    eff = chemical_factor(rr, temp_c=temp_c)
    return {"name": "psi_chemistry", "value": eff.factor, "notes": eff.notes,
            "warnings": eff.warnings, "terms": eff.terms}


def _detect_situation(rr: ResolvedRecipe):
    """Classify the run BEFORE choosing physics.

    Needs the pad contact state and the supply state, which are computed here
    independently of whether their layers end up enabled — detection must not
    depend on the choice it informs.
    """
    from cmp_sim.core.regime import detect

    contact_state = supply_state = None
    try:
        from cmp_sim.pad.material import pad_state
        contact_state, _n, _w = pad_state(rr.recipe.pad, rr)
    except Exception:                                    # pragma: no cover
        pass
    try:
        out = _supply_diagnostic(rr)
        supply_state = out.get("supply_state")
    except Exception:                                    # pragma: no cover
        pass
    return detect(rr, contact_state=contact_state, supply_state=supply_state)


def simulate(recipe: Recipe) -> Result:
    from cmp_sim.core.profiles import check as check_profile, resolve_model
    from cmp_sim.core.validate_input import validate

    # Reject impossible input here, with a message about what the user typed,
    # rather than letting it surface as whatever the inner numerics raise.
    input_warnings = validate(recipe)

    rr = resolve(recipe)
    notes: List[str] = []
    warnings: List[str] = list(input_warnings)
    factors: Dict[str, float] = {}

    if recipe.model not in MODELS:
        raise ValueError(f"unknown model '{recipe.model}'. available: {sorted(MODELS)}")

    # 0. Is this film an established CMP target at all? An unestablished one
    #    must not be predicted from defaults - it has to be told what it is.
    from cmp_sim.core.maturity import FilmNotEstablished, assess
    rr.maturity = assess(rr.pack, recipe)
    if not rr.maturity.runnable:
        raise FilmNotEstablished(rr.maturity)
    notes.extend(f"CMP maturity: {r}" for r in rr.maturity.reasons)
    if rr.maturity.grade != "established":
        warnings.append(
            f"'{recipe.wafer.film}' is graded '{rr.maturity.grade}': "
            + rr.maturity.reasons[0]
            + ". Treat the absolute rate as indicative and rank recipes instead, "
              "or supply measurements: to calibrate against your own tool")

    # 1. What situation is this? 2. Which physics suits it? 3. Run it.
    rr.situation = _detect_situation(rr)
    rr.profile, profile_notes = resolve_model(recipe.model, rr.situation)
    notes.extend(rr.situation.notes)
    notes.extend(profile_notes)
    notes.append(f"profile '{rr.profile.name}' layers: "
                 + (", ".join(rr.profile.layers) or "none (Preston only)"))
    warnings.extend(check_profile(rr.profile, rr.situation))
    warnings.extend(rr.profile.caveats)
    for item in rr.situation.undetermined:
        warnings.append("undetermined — " + item)

    notes.extend(rr.formulation_notes)
    warnings.extend(rr.formulation_warnings)

    # _abrasive_type_hook must precede _abrasive_hook: it rewrites the
    # concentration and size exponents to the ones scoped to the abrasive
    # actually in the recipe, which is what _abrasive_hook then reads.
    hooks = list(_FACTOR_HOOKS) + [_exponent_hook, _passivation_threshold_hook,
                                   _kappa_contact_hook,
                                   _abrasive_type_hook, _abrasive_hook,
                                   _chemistry_hook]
    if rr.profile.enabled("transport"):
        hooks.append(_supply_diagnostic)
    if rr.profile.enabled("damage"):
        hooks.append(_defect_diagnostic)
    if rr.profile.enabled("wear"):
        hooks.append(_pad_life_diagnostic)

    kp = rr.kp_base
    extras: Dict[str, Any] = {}
    supply_state = None
    for hook in hooks:
        out = hook(rr) or {}
        notes.extend(out.get("notes", []))
        warnings.extend(out.get("warnings", []))
        if out.get("regime"):
            extras["abrasive_regime"] = out["regime"]
        if out.get("abrasive_type"):
            extras["abrasive_type"] = out["abrasive_type"]
        if out.get("terms"):
            extras["chemistry_terms"] = {k: round(float(v), 5)
                                         for k, v in out["terms"].items()}
        if out.get("supply"):
            extras["slurry_supply"] = out["supply"]
            supply_state = out.get("supply_state")
        for key in ("defect", "pad_life", "pattern"):
            if out.get(key):
                extras[{"defect": "defect_risk", "pad_life": "pad_life",
                        "pattern": "pattern_effects"}[key]] = out[key]
        if out.get("value") is None:
            continue
        factors[out["name"]] = float(out["value"])
        kp *= float(out["value"])

    radius_m, mrr, p_label = preston_model.mrr_radial_nm_per_min(
        wafer_radius_m=rr.wafer_radius_m,
        center_offset_m=rr.center_offset_m,
        rpm_head=recipe.tool.rpm_head,
        rpm_platen=recipe.tool.rpm_platen,
        kp_m_per_pa=kp,
        pressure_pa=rr.pressure_pa,
        n_radial=recipe.wafer.n_radial,
        zone_pressures_pa=rr.zone_pressures_pa,
        zone_edges_norm=recipe.tool.zone_edges_norm,
    )

    # P5: apply the radial supply weighting only when the pack calibrates it.
    if supply_state is not None:
        from cmp_sim.models import uniformity as un
        weight = un.starvation_profile(
            radius_m, rr.wafer_radius_m, supply_state.supply_number,
            rr.p_or("starvation_length_m", None))
        if weight is not None:
            mrr = mrr * weight
            notes.append(
                f"slurry starvation profile applied with starvation length "
                f"{float(rr.p('starvation_length_m')) * 1e3:.1f} mm: centre/edge "
                f"supply weighting {weight[0]:.3f}/{weight[-1]:.3f}")
        elif supply_state.starved:
            warnings.append(
                "the wafer is slurry-starved but this pack has no calibrated "
                "starvation_length_m, so NO radial correction was applied — the "
                "profile below is the un-starved one and will look better than "
                "reality at the centre")

    u = preston_model.uniformity(radius_m, mrr)
    mean_nm = float(u["mean"])
    removed = mrr * (recipe.tool.time_s / 60.0)
    remaining = None
    if recipe.wafer.initial_thickness_nm is not None:
        remaining = float(recipe.wafer.initial_thickness_nm) - removed
        if float(np.min(remaining)) < 0.0:
            warnings.append(
                "film cleared somewhere on the wafer before time_s elapsed — "
                "remaining thickness clipped at 0; endpoint/stop-layer physics is P6"
            )
            remaining = np.clip(remaining, 0.0, None)

    # P6 runs last: it needs the blanket rate the layers above just produced.
    if rr.profile.enabled("pattern") and recipe.wafer.pattern_density is not None:
        rr.blanket_rate_m_per_s = mean_nm / 60.0 * 1e-9
        pat = _pattern_diagnostic(rr) or {}
        notes.extend(pat.get("notes", []))
        warnings.extend(pat.get("warnings", []))
        if pat.get("pattern"):
            extras["pattern_effects"] = pat["pattern"]

    # Is the absolute number even plausible for this film?
    from cmp_sim.core.sanity import check_rate
    warnings.extend(check_rate(recipe.wafer.film, mean_nm * 10.0))

    # What the NAMED pad/disk actually supplied, so the UI can show which
    # selections reached the physics and which were only recorded.
    if rr.consumables is not None and (rr.consumables.pad_name
                                       or rr.consumables.disk_name):
        extras["consumables"] = rr.consumables.as_dict()

    notes.append(f"pressure profile: {p_label}")
    notes.append(f"parameter pack: {' -> '.join(rr.pack.lineage)}")
    notes.append(f"Kp_base={rr.kp_base:.4g} m/Pa; Kp_eff={kp:.4g} m/Pa")

    unverified = [k for k in rr.used_keys
                  if k in rr.pack.params
                  and rr.pack.params[k].confidence in ("estimated", "unverified", "unknown")]
    for k in unverified:
        p = rr.pack.params[k]
        warnings.append(f"{k}={p.value} has confidence '{p.confidence}' (source: {p.source or 'none'})")

    return Result(
        model=recipe.model,
        film=recipe.wafer.film,
        radius_m=radius_m,
        mrr_nm_per_min=mrr,
        mean_rr_nm_per_min=mean_nm,
        mean_rr_angstrom_per_min=mean_nm * 10.0,
        # None when nothing is removed anywhere: uniformity is undefined there,
        # and reporting 0% would read as a perfectly uniform wafer.
        wiwnu_percent=(None if u.get("sigma_pct") is None
                       else float(u["sigma_pct"])),
        removed_nm=removed,
        remaining_nm=remaining,
        factors=factors,
        provenance=rr.pack.provenance(rr.used_keys),
        notes=notes,
        warnings=warnings,
        extras={"uniformity": {k: (v if not isinstance(v, (int, float))
                                   else round(float(v), 4))
                               for k, v in u.items()},
                "situation": rr.situation.as_dict(),
                "profile": rr.profile.name,
                "cmp_maturity": rr.maturity.as_dict(),
                **({"calibration": rr.calibration.as_dict()}
                   if rr.calibration else {}),
                **({"kp_estimate": rr.estimate.as_dict()}
                   if getattr(rr, "estimate", None) else {}),
                **({"factor_fit": rr.factor_fit.as_dict()}
                   if getattr(rr, "factor_fit", None) else {}),
                **extras},
    )
