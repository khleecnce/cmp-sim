"""P6 — pattern effects: step-height evolution, dishing and erosion.

A blanket rate is not what a fab buys. On a patterned wafer the same recipe
removes material at different rates in dense and isolated regions, which is
what produces dishing (metal recessed below the surrounding oxide) and erosion
(the whole dense array sinking).

MIT pattern-density framework
-----------------------------
Boning et al., "Pattern Dependent Modeling for CMP Optimization and Control",
MRS Spring 1999; Stine et al., IEEE Trans. Semicond. Manuf. 11, 1 (1998);
Ouma, MIT PhD thesis 1999.

1. **Effective density.** The pad is stiff over a planarization length `PL`,
   so it averages the layout:

       rho_eff(x) = (w * rho_local)(x)

   Ouma derives an elliptic kernel from elastic pad bending; the inherited
   implementation uses a normalised Gaussian of width `PL`, which is an
   approximation and is declared as one.

2. **Density-weighted removal.** Raised features carry the whole load, so

       RR_up(x) = K / rho_eff(x)

   Dense regions spread the load over more features, so they polish *slower*
   and end up thicker. This inverse-density law is the core prediction.

3. **Step-height evolution, two regimes.**
   * incompressible pad (Grillaert): only the up-areas are touched, the step
     falls linearly and vanishes at `t_c = rho h0 / K`;
   * compressible pad (Burke/Tseng): once the pad contacts the down-areas the
     step decays exponentially, `h = h_c exp(-(t-t_c)/tau)`.
   The unified model (Smith) switches between them at a contact height
   `h1 = a1 + a2 exp(-rho/a3)`.

4. **Overpolish steady state.** During overpolish, metal and oxide rates move
   in opposite directions with dishing depth `d`:

       r_metal(d) = RR_m (1 - d/d_max)             (deeper dish -> less contact)
       r_oxide(d) = RR_ox/(1 - rho_m) (1 + b d)

   Setting them equal gives the steady-state dishing `d_ss`, the maximum
   observed dishing: dishing does not grow without bound, it self-limits where
   the two rates balance.

Selectivity
-----------
Selectivity `S = RR_metal / RR_stop` is what makes a stop layer work. High
selectivity protects the stop layer but *worsens* dishing, because the metal
keeps receding while the surround does not. That trade-off is computed, not
assumed.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

from cmp_sim.core.legacy_bridge import legacy_pattern

NAME = "pattern_density"


# ── layout -> effective density ──────────────────────────────────────
def effective_density(x_m: np.ndarray, rho_local: np.ndarray,
                      planarization_length_m: float) -> np.ndarray:
    """Pad-averaged pattern density (inherited Gaussian-kernel implementation)."""
    if planarization_length_m <= 0:
        raise ValueError("planarization length must be positive")
    return legacy_pattern.effective_density(np.asarray(x_m, float),
                                            np.asarray(rho_local, float),
                                            float(planarization_length_m))


def up_area_rate(blanket_rate: float, rho_eff: np.ndarray) -> np.ndarray:
    """RR_up = K / rho_eff — dense regions polish slower."""
    rho = np.asarray(rho_eff, float)
    if np.any(rho <= 0):
        raise ValueError("effective density must be positive everywhere")
    return float(blanket_rate) / rho


# ── step height ──────────────────────────────────────────────────────
def step_height(t_s: float, blanket_rate: float, rho_eff: np.ndarray,
                initial_step_m: float, pad_compressible: bool = False,
                tau_s: Optional[float] = None,
                contact_step_m: Optional[float] = None) -> np.ndarray:
    """Step height after time `t_s`.

    Incompressible pad: the step falls linearly at `K/rho` and reaches zero at
    `t_c = rho h0 / K` (inherited ``step_height_incompressible``).

    Compressible pad: the pad reaches the down-areas while a residual step
    `h_c` remains, after which the step decays exponentially with time constant
    `tau` (inherited ``step_height_compressible``). The crossover time is when
    the linear law would have worn the step down to `h_c`:

        t_c = rho (h0 - h_c) / K

    so the two branches meet continuously at `h_c`.
    """
    rho = np.asarray(rho_eff, float)
    linear = legacy_pattern.step_height_incompressible(
        float(t_s), float(blanket_rate), rho, float(initial_step_m))
    if not pad_compressible:
        return linear
    if tau_s is None or tau_s <= 0:
        raise ValueError(
            "a compressible pad needs a step-decay time constant tau; without it "
            "the post-contact regime is undefined and must not be guessed")
    h_c = float(contact_step_m if contact_step_m is not None
                else 0.1 * float(initial_step_m))
    if not 0.0 < h_c < float(initial_step_m):
        raise ValueError("the contact step height must lie between 0 and the initial step")

    t_c = rho * (float(initial_step_m) - h_c) / float(blanket_rate)
    decayed = h_c * np.exp(-(float(t_s) - t_c) / float(tau_s))
    return np.where(float(t_s) < t_c, linear, decayed)


def planarization_time_s(blanket_rate: float, rho_eff: float,
                         initial_step_m: float) -> float:
    """t_c = rho * h0 / K — when the step closes in the incompressible regime.

    It is proportional to the local density, so dense regions planarize last.
    That spread in clearing time is what forces overpolish, and overpolish is
    what causes dishing and erosion.
    """
    return float(rho_eff) * float(initial_step_m) / float(blanket_rate)


def contact_height_m(rho_eff: np.ndarray, a1: float, a2: float, a3: float):
    """Unified-model contact height h1 = a1 + a2 exp(-rho/a3) (MRS99 Eq. 4),
    the residual step at which a compressible pad touches the down-areas."""
    return legacy_pattern.contact_height(np.asarray(rho_eff, float),
                                         float(a1), float(a2), float(a3))


# ── dishing / erosion ────────────────────────────────────────────────
def steady_state_dishing_m(rate_metal: float, rate_oxide: float,
                           metal_density: float, dishing_max_m: float,
                           oxide_sensitivity_b: float) -> float:
    """Dishing where the metal and oxide rates balance (inherited)."""
    if not 0.0 <= metal_density < 1.0:
        raise ValueError("metal pattern density must lie in [0, 1)")
    return float(legacy_pattern.steady_state_dishing(
        float(rate_metal), float(rate_oxide), float(metal_density),
        float(dishing_max_m), float(oxide_sensitivity_b)))


def erosion_m(rate_oxide: float, metal_density: float, overpolish_time_s: float
              ) -> float:
    """Oxide loss in the array during overpolish.

    The oxide spaces carry the load alone once the metal has dished, so they
    see the blanket rate divided by their area fraction `(1 - rho_m)`.
    """
    if not 0.0 <= metal_density < 1.0:
        raise ValueError("metal pattern density must lie in [0, 1)")
    return float(rate_oxide) / (1.0 - float(metal_density)) * float(overpolish_time_s)


def selectivity(rate_film: float, rate_stop: float) -> float:
    if rate_stop <= 0:
        raise ValueError("stop-layer rate must be positive to define selectivity")
    return float(rate_film) / float(rate_stop)


@dataclass
class PatternResult:
    rho_eff: np.ndarray
    up_rate: np.ndarray
    step_m: np.ndarray
    dishing_m: Optional[float] = None
    erosion_m: Optional[float] = None
    selectivity: Optional[float] = None
    notes: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    def as_dict(self) -> Dict[str, Any]:
        out: Dict[str, Any] = {
            "effective_density": {"min": round(float(np.min(self.rho_eff)), 4),
                                   "max": round(float(np.max(self.rho_eff)), 4)},
            # up_rate is in m/s: metres -> angstrom (1e10) and seconds -> minutes
            # (60). Multiplying by 10 instead silently reported 0.0 A/min for
            # every real rate, contradicting this object's own notes.
            "up_area_rate_A_per_min": {
                "min": round(float(np.min(self.up_rate)) * 1e10 * 60.0, 1),
                "max": round(float(np.max(self.up_rate)) * 1e10 * 60.0, 1)},
            "step_height_nm": {"min": round(float(np.min(self.step_m)) * 1e9, 2),
                                "max": round(float(np.max(self.step_m)) * 1e9, 2)},
            "notes": self.notes, "warnings": self.warnings,
        }
        if self.dishing_m is not None:
            out["dishing_nm"] = round(self.dishing_m * 1e9, 2)
        if self.erosion_m is not None:
            out["erosion_nm"] = round(self.erosion_m * 1e9, 2)
        if self.selectivity is not None:
            out["selectivity"] = round(self.selectivity, 2)
        return out


def evaluate(*, blanket_rate_m_per_s: float, rho_local: np.ndarray,
             x_m: np.ndarray, planarization_length_m: float,
             initial_step_m: float, time_s: float,
             rate_stop_m_per_s: Optional[float] = None,
             dishing_max_m: Optional[float] = None,
             oxide_sensitivity_b: Optional[float] = None,
             overpolish_time_s: float = 0.0) -> PatternResult:
    """Full pattern evaluation for one die layout."""
    notes: List[str] = []
    warnings: List[str] = []

    rho_eff = effective_density(x_m, rho_local, planarization_length_m)
    up = up_area_rate(blanket_rate_m_per_s, rho_eff)
    step = step_height(time_s, blanket_rate_m_per_s, rho_eff, initial_step_m)

    notes.append(
        f"effective density {float(np.min(rho_eff)):.3f}-{float(np.max(rho_eff)):.3f} "
        f"over a planarization length of {planarization_length_m * 1e3:.2f} mm "
        "(Gaussian kernel approximating Ouma's elliptic pad-bending kernel)")
    notes.append(
        f"up-area rate spans {float(np.min(up)) * 6e11:.0f}-{float(np.max(up)) * 6e11:.0f} "
        "A/min: RR = K/rho_eff, so dense regions polish slower and clear last")

    # When the step reaches zero the wafer is planar and every further second is
    # overpolish -- which is exactly when dishing and erosion accrue. Reporting
    # only "step height 0.0 nm" hides that: it reads as a perfect result rather
    # than as "planarised 86 s ago and still polishing".
    if blanket_rate_m_per_s > 0:
        t_clear = float(np.max(rho_eff)) * float(initial_step_m) / float(blanket_rate_m_per_s)
        notes.append(
            f"the step clears at t = {t_clear:.0f} s in the densest region "
            f"(rho_eff {float(np.max(rho_eff)):.2f})")
        if time_s > t_clear:
            over = time_s - t_clear
            warnings.append(
                f"planarisation completed at {t_clear:.0f} s but the recipe "
                f"polishes for {time_s:.0f} s, so {over:.0f} s ({over / time_s:.0%} "
                f"of the step) is overpolish on a flat surface. A step height of "
                f"0 nm here means 'cleared long ago', not 'just right' -- this is "
                f"the regime where dishing and erosion accumulate")

    dishing = erosion = sel = None
    rho_m = float(np.max(rho_eff))
    if rate_stop_m_per_s:
        sel = selectivity(blanket_rate_m_per_s, rate_stop_m_per_s)
        notes.append(f"selectivity film:stop = {sel:.1f}")
        if sel > 50.0:
            warnings.append(
                f"selectivity {sel:.0f}:1 protects the stop layer but makes dishing "
                "worse: the metal keeps receding while the surround does not")

    if dishing_max_m and oxide_sensitivity_b is not None and rate_stop_m_per_s:
        dishing = steady_state_dishing_m(
            blanket_rate_m_per_s, rate_stop_m_per_s, rho_m,
            dishing_max_m, oxide_sensitivity_b)
        notes.append(
            f"steady-state dishing {dishing * 1e9:.1f} nm at pattern density "
            f"{rho_m:.2f}: metal and oxide rates balance there, so dishing "
            "self-limits rather than growing without bound")
    else:
        warnings.append(
            "dishing not computed: it needs the stop-layer rate, the maximum "
            "dishing depth and the oxide sensitivity b from the pack — these are "
            "layout- and slurry-specific and are not guessed")

    if overpolish_time_s > 0 and rate_stop_m_per_s:
        erosion = erosion_m(rate_stop_m_per_s, rho_m, overpolish_time_s)
        notes.append(
            f"erosion {erosion * 1e9:.1f} nm after {overpolish_time_s:.0f} s of "
            f"overpolish at density {rho_m:.2f}")

    return PatternResult(rho_eff=rho_eff, up_rate=up, step_m=step,
                         dishing_m=dishing, erosion_m=erosion, selectivity=sel,
                         notes=notes, warnings=warnings)
