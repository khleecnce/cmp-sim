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
        return float(self.p("kp_m_per_pa"))


def resolve(recipe: Recipe) -> ResolvedRecipe:
    name = recipe.slurry.pack or FILM_PACK.get(recipe.wafer.film)
    if not name:
        raise ParamMissing(
            f"no parameter pack for film '{recipe.wafer.film}'. "
            f"Set slurry.pack explicitly or add the film to FILM_PACK. "
            f"Known films: {sorted(FILM_PACK)}"
        )
    return ResolvedRecipe(recipe=recipe, pack=load_pack(name))


MODELS: Dict[str, str] = {"preston": "P1 Preston: MRR = Kp*P*V"}


def simulate(recipe: Recipe) -> Result:
    rr = resolve(recipe)
    notes: List[str] = []
    warnings: List[str] = []
    factors: Dict[str, float] = {}

    if recipe.model not in MODELS:
        raise ValueError(f"unknown model '{recipe.model}'. available: {sorted(MODELS)}")

    kp = rr.kp_base
    for hook in _FACTOR_HOOKS:
        out = hook(rr) or {}
        if out.get("value") is None:
            continue
        factors[out["name"]] = float(out["value"])
        kp *= float(out["value"])
        notes.extend(out.get("notes", []))
        warnings.extend(out.get("warnings", []))

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
        wiwnu_percent=float(u["sigma_pct"]),
        removed_nm=removed,
        remaining_nm=remaining,
        factors=factors,
        provenance=rr.pack.provenance(rr.used_keys),
        notes=notes,
        warnings=warnings,
        extras={"uniformity": {k: round(float(v), 4) for k, v in u.items()}},
    )
