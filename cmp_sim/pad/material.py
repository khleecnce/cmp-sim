"""Pad material and surface state -> GW contact input.

Resolution order for every pad number
-------------------------------------
1. Explicit value on the ``Pad`` object.
2. Derived from another explicit pad value (Shore D -> modulus).
3. The parameter pack's reference pad (``pad_*`` keys in ``base.yaml``).

The pack's reference pad is also what the contact factor is normalised
against, because the pack's Kp was calibrated with that pad in the loop.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

from cmp_sim.models import contact_gw as cg
from cmp_sim.core.state import Pad

#: pack keys that define the reference pad surface
PACK_KEYS = ("pad_E_star_pa", "pad_asperity_radius_m",
             "pad_asperity_density_m2", "pad_height_beta_inv_m")


def reference_pad_state(resolved) -> cg.PadContactState:
    """The pad the pack's Kp was calibrated on."""
    return cg.PadContactState(
        e_star_pa=float(resolved.p("pad_E_star_pa")),
        asperity_radius_m=float(resolved.p("pad_asperity_radius_m")),
        asperity_density_m2=float(resolved.p("pad_asperity_density_m2")),
        height_sigma_m=float(resolved.p("pad_height_beta_inv_m")),
    )


def pad_state(pad: Pad, resolved,
              film_youngs_modulus_pa: Optional[float] = None
              ) -> Tuple[cg.PadContactState, List[str], List[str]]:
    """Build the GW state of the *actual* pad in this recipe."""
    notes: List[str] = []
    warnings: List[str] = []
    ref = reference_pad_state(resolved)

    e_star = ref.e_star_pa
    if pad.youngs_modulus_pa:
        e_star = cg.equivalent_modulus_pa(
            float(pad.youngs_modulus_pa),
            **({"e_wafer_pa": film_youngs_modulus_pa} if film_youngs_modulus_pa else {}))
        notes.append(f"E* {e_star:.3e} Pa from pad Young's modulus "
                     f"{float(pad.youngs_modulus_pa):.3e} Pa (Hertz reduced modulus)")
    elif pad.shore_d:
        e_pad = cg.shore_d_to_youngs_modulus_pa(pad.shore_d)
        e_star = cg.equivalent_modulus_pa(
            e_pad,
            **({"e_wafer_pa": film_youngs_modulus_pa} if film_youngs_modulus_pa else {}))
        notes.append(f"E* {e_star:.3e} Pa from Shore D {pad.shore_d} "
                     f"(-> E_pad {e_pad:.3e} Pa, Qi 2003 correlation)")
        if not cg.shore_d_conversion_is_in_range(pad.shore_d):
            warnings.append(
                f"Shore D {pad.shore_d} is outside the 20-60 validity range of the "
                "hardness-to-modulus correlation; E* is an extrapolation")
    else:
        notes.append(f"pad modulus not given — using the pack reference pad "
                     f"E* {e_star:.3e} Pa")

    state = cg.PadContactState(
        e_star_pa=e_star,
        asperity_radius_m=float(pad.asperity_radius_m or ref.asperity_radius_m),
        asperity_density_m2=float(pad.asperity_density_m2 or ref.asperity_density_m2),
        height_sigma_m=float(pad.roughness_beta_inv_m or ref.height_sigma_m),
    )
    return state, notes, warnings


#: confidence levels at which the pack's reference pad may be used as a baseline
TRUSTED_CONFIDENCE = ("verified", "literature", "measured", "owner-provided")


def reference_pad_is_trustworthy(resolved) -> bool:
    """Is the pack's reference pad a real pad, or just an order-of-magnitude guess?

    ``kappa = A_r(pad) / A_r(reference)`` is only meaningful if the reference
    really is the pad the pack's Kp was calibrated with. When the reference
    values are merely ``estimated``, the ratio measures the distance from a
    guess, not a physical difference.

    Inheriting the shared ``base`` pad is the same problem wearing a better
    grade: those are literature values for a generic polyurethane pad, not a
    record of the pad THIS pack's Kp was fitted on. Only a pack that declares
    the reference pad itself may have kappa applied.
    """
    for key in PACK_KEYS:
        param = resolved.pack.params.get(key)
        if param is None or param.confidence not in TRUSTED_CONFIDENCE:
            return False
        if getattr(param, "owner", None) in (None, "base"):
            return False
    return True


def contact_factor_for(recipe, resolved,
                       film_youngs_modulus_pa: Optional[float] = None
                       ) -> Dict[str, Any]:
    """Solver hook: dimensionless Kp multiplier ``kappa`` from pad contact."""
    ref = reference_pad_state(resolved)
    state, notes, warnings = pad_state(recipe.pad, resolved, film_youngs_modulus_pa)

    same = (state.e_star_pa == ref.e_star_pa
            and state.asperity_radius_m == ref.asperity_radius_m
            and state.asperity_density_m2 == ref.asperity_density_m2
            and state.height_sigma_m == ref.height_sigma_m)
    if same:
        return {"name": "kappa_contact", "value": 1.0,
                "notes": notes + ["GW contact: pad equals the pack reference pad, "
                                  "kappa = 1.0 exactly (no double counting)"],
                "warnings": warnings, "state": state}

    pressure_pa = resolved.pressure_pa
    factor, f_notes, f_warnings = cg.contact_factor(state, ref, pressure_pa)

    # ── is the baseline real? ────────────────────────────────────────
    if not reference_pad_is_trustworthy(resolved):
        weak = [k for k in PACK_KEYS
                if (resolved.pack.params.get(k) is None
                    or resolved.pack.params[k].confidence not in TRUSTED_CONFIDENCE)]
        return {
            "name": "kappa_contact", "value": None,
            "notes": notes + f_notes + [
                f"GW contact factor computed as {factor:.3f} but NOT applied to Kp "
                "— reported as a diagnostic only"],
            "warnings": warnings + f_warnings + [
                "pad contact correction NOT applied: the pack's reference pad is "
                f"itself only estimated ({', '.join(weak)}), so kappa would measure "
                "the distance from a guess rather than a real pad difference. "
                "Applying it inflates the rate by that arbitrary ratio. The pack's "
                "Kp already contains whichever pad it was calibrated with; to use "
                "this correction, give the reference pad's properties a real source "
                "in the pack. Pad-to-pad comparisons at a fixed reference are still "
                "meaningful — the diagnostic value is in the notes."],
            "state": state, "diagnostic_kappa": factor}

    return {"name": "kappa_contact", "value": factor,
            "notes": notes + f_notes, "warnings": warnings + f_warnings,
            "state": state}
