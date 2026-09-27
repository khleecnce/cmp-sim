r"""The GW summit density is inert BY DERIVATION, and the pad-hardness advice
is conditional -- both re-measured here, never pinned as literals.

Two findings, one error class
----------------------------
`tools/declared_key_response_census.py` asks the direction the existing
`pack_key_wiring_audit` cannot see: not *does every key the engine reads exist
in a pack?* but *does every key a pack DECLARES move anything?* That is
`docs/limits.md` §20's hardest inert case, because nothing can report it --
`apply_overrides` warns only about UNDECLARED keys, and `inert_axis_scan`
enumerates only axes the corpus happens to sweep.

1. `asperity_density_per_m2` / `asperity_ref_density_per_m2` are declared by
   all fourteen packs with a literature source, and move the rate by **exactly
   nothing**. That is CORRECT Greenwood-Williamson physics, not a missing wire:
   with exponential summit heights the load balance fixes the separation so
   that eta cancels out of `A_r/A_0`, `p_r` and the contact count. It then
   cancels a second time inside `kappa = A_r(pad)/A_r(ref)`. Inert is fine;
   silently inert is not, so the reason is now declared and asserted.

2. `pad_hardness_shore_d`'s declaration told the caller to "put the value on
   the pad to reach the term", and `test_the_pad_object_is_the_path_that_
   reaches_the_contact_layer` certified that advice by asserting the Shore D
   was CONVERTED. Conversion is not reach. Measured end to end, the
   recommended path moves the rate on **one** of the packs that declare the
   key -- the others withhold kappa because their reference pad is inherited
   rather than measured -- and on that one pack the response runs 1.90x at 60D,
   13.9x at 40D, and raises `ContactSolverOutOfRange` at 30D, because the
   summits saturate and the exponential-tail result kappa rests on is void.
   §20's rule is that a "put it here instead" path must be tested for not being
   equally inert; the weaker assertion let advice that is inert on most packs
   pass as a route.

Everything below is measured against the shipping solver at test time. A
literal would go stale the moment a pack gains a measured reference pad -- and
going stale silently is the failure these tests exist to prevent.
"""
from __future__ import annotations

import pytest

from cmp_sim.api import run_recipe
from cmp_sim.core.declined_axes import DECLINES_AXIS
from cmp_sim.core.params import available_packs, load_pack
from cmp_sim.models.contact_gw import PadContactState
from cmp_sim.slurry.formulation import UNREAD_BY_THE_RATE

#: Film for each pack, so a run is never gated for being off-material.
PACK_FILM = {
    "oxide_silica": "oxide", "oxide_silica_anionic": "oxide",
    "oxide_silica_aminosilane": "oxide",
    "oxide_silica_calibrated_pad": "oxide", "sti_ceria": "oxide",
    "cu_h2o2_bta": "cu", "cu_alkaline_benzenesulfonic": "cu",
    "w_fe_oxidizer": "w", "poly_si_alkaline": "poly_si",
    "si_substrate_alkaline": "si", "snag_solder": "snag",
    "sic_ceria_h2o2": "sic", "sic_alumina_kmno4": "sic",
    "dlc_zirconia_permanganate": "dlc",
}

ETA_KEYS = ("asperity_density_per_m2", "asperity_ref_density_per_m2")


def _run(pack, *, pad=None, params=None, psi=3.0):
    recipe = {
        "model": "auto",
        "wafer": {"film": PACK_FILM[pack], "n_radial": 11},
        "slurry": {"pack": pack},
        "tool": {"pressure_psi": psi, "rpm_platen": 60, "rpm_head": 60,
                 "time_s": 60.0, "flow_ml_min": 200.0},
    }
    if pad:
        recipe["pad"] = pad
    if params:
        recipe["params"] = params
    return run_recipe(recipe)


def _rate(result):
    return float(result["removal_rate_A_per_min"])


def _texts(result):
    return list(result.get("warnings") or []) + list(result.get("notes") or [])


def _packs_declaring(key):
    out = []
    for name in sorted(available_packs()):
        if name not in PACK_FILM:
            continue
        param = load_pack(name).params.get(key)
        if param is not None and param.value not in (None, 0):
            out.append(name)
    return out


# ── 1. the derivation, measured on the contact model itself ──────────────

def test_the_gw_real_area_fraction_does_not_depend_on_summit_density():
    """The claim the declaration rests on, checked without the solver.

    This is the whole reason the inertness is acceptable. If it ever fails,
    the declaration is asserting a cancellation that no longer happens and the
    key must be re-wired rather than re-declared.
    """
    pressure_pa = 3.0 * 6894.757
    base = dict(e_star_pa=2.5e8, asperity_radius_m=50e-6, height_sigma_m=2.0e-6)
    fractions, pressures, counts = [], [], []
    for mult in (0.25, 0.5, 1.0, 2.0, 4.0):
        state = PadContactState(asperity_density_m2=2.0e8 * mult, **base)
        fractions.append(state.real_area_fraction(pressure_pa))
        pressures.append(state.mean_real_pressure_pa(pressure_pa))
        counts.append(state.n_contacts(pressure_pa))

    for label, values in (("A_r/A_0", fractions), ("p_r", pressures),
                          ("n_contacts", counts)):
        spread = (max(values) - min(values)) / values[2]
        assert spread < 1e-6, (
            f"{label} moved {spread:.3e} over a 16x summit-density range, so "
            "eta no longer cancels and the inertness declaration for "
            "asperity_density_per_m2 is now false")


def test_the_quantities_that_do_move_the_contact_factor_still_move_it():
    """Non-vacuity: the test above passes trivially if the model is dead."""
    pressure_pa = 3.0 * 6894.757
    base = dict(e_star_pa=2.5e8, asperity_radius_m=50e-6,
                asperity_density_m2=2.0e8, height_sigma_m=2.0e-6)
    reference = PadContactState(**base).real_area_fraction(pressure_pa)
    for key in ("e_star_pa", "asperity_radius_m", "height_sigma_m"):
        altered = dict(base)
        altered[key] = base[key] * 3.0
        moved = PadContactState(**altered).real_area_fraction(pressure_pa)
        assert abs(moved - reference) / reference > 0.1, (
            f"{key} x3 moved the real-area fraction by "
            f"{100 * abs(moved - reference) / reference:.3f}%, so the "
            "cancellation test above is measuring a dead model")


@pytest.mark.parametrize("key", ETA_KEYS)
def test_the_summit_density_keys_are_inert_and_say_so(key):
    packs = _packs_declaring(key)
    assert packs, f"no pack declares {key}; this test has nothing to check"
    pack = packs[0]
    base = _rate(_run(pack))
    result = _run(pack, params={key: load_pack(pack).params[key].value * 3.0})
    assert _rate(result) == pytest.approx(base, rel=1e-9), (
        f"{key} now moves the rate; the declaration calling it a structural "
        "cancellation is stale and must be replaced by the derivation that "
        "now applies")
    said = [t for t in _texts(result) if f"{DECLINES_AXIS}{key}]" in t]
    assert said, (
        f"{key} is inert and nothing in the run says so -- from outside that "
        "is indistinguishable from the model weighing it and finding it "
        f"unimportant. Run warnings were {_texts(result)[:4]}")
    text = said[0]
    assert "cancel" in text.lower(), text
    for pointer in ("E*", "sigma"):
        assert pointer in text or "asperity_density_per_m2" in text, text


def test_the_summit_density_still_reaches_the_saturation_diagnostic():
    """Both halves of the "it goes somewhere else" claim (§20).

    The declaration says eta is still read for the saturation boundary. If it
    were not, "not ignored" would be an excuse rather than a location.
    """
    pressure_pa = 3.0 * 6894.757
    base = dict(e_star_pa=2.5e8, asperity_radius_m=50e-6, height_sigma_m=2.0e-6)
    sparse = PadContactState(asperity_density_m2=5.0e7, **base)
    dense = PadContactState(asperity_density_m2=8.0e8, **base)
    assert sparse.saturation(pressure_pa) > 4.0 * dense.saturation(pressure_pa), (
        "summit saturation must respond to summit density, or the claim that "
        "eta is read by the validity boundary is false")


# ── 2. the pad-hardness advice, priced end to end ────────────────────────

def test_the_recommended_pad_path_is_measured_not_assumed():
    """`Pad.shore_d` must move the rate on at least one pack that declares the
    inert pack key -- and the declaration must admit it does not on the rest.

    Asserting only that the Shore D was CONVERTED (the previous test) certifies
    advice that can be inert wherever kappa is withheld.
    """
    packs = _packs_declaring("pad_hardness_shore_d")
    assert packs, "no pack declares pad_hardness_shore_d"

    reached, withheld = [], []
    for pack in packs:
        try:
            base = _rate(_run(pack))
        except Exception:
            # An unestablished film refuses to run from pack defaults at all
            # (`core.maturity`). That refusal is a separate, tested policy and
            # says nothing about where pad hardness is read, so the pack is not
            # evidence either way here.
            continue
        try:
            moved = _rate(_run(pack, pad={"name": "probe", "shore_d": 60.0}))
        except Exception:                       # out of the solver's range
            withheld.append(pack)
            continue
        (reached if abs(moved - base) / base > 1e-6 else withheld).append(pack)

    assert reached or withheld, (
        "no pack declaring pad_hardness_shore_d could be run, so this test is "
        "vacuous -- check core.maturity rather than deleting it")

    assert reached, (
        "the declaration tells the caller to put the hardness on the Pad "
        "object, and on no pack does that move the rate -- the advice is a "
        "second silent failure")
    if withheld:
        text = UNREAD_BY_THE_RATE["pad_hardness_shore_d"]
        assert "CONDITIONAL" in text, (
            f"the recommended path is inert on {len(withheld)} of "
            f"{len(packs)} packs ({withheld[:3]}) and the declaration does "
            "not say the advice is conditional")
        assert "reference_pad_is_trustworthy" in text or "reference pad" in text


def test_the_reached_pad_response_states_its_validity_bound():
    """Where kappa IS applied, softer pads leave the GW tail -- say so.

    kappa runs 1.9x at 60D and 13.9x at 40D on the one pack that applies it,
    and the solver has no solution at 30D. A 13.9x rate multiplier with no
    stated bound would read as a prediction.
    """
    pack = "oxide_silica_calibrated_pad"
    if pack not in PACK_FILM:
        pytest.skip("the pack that applies kappa is no longer shipped")
    soft = _run(pack, pad={"name": "probe", "shore_d": 45.0})
    saturation_warned = [w for w in (soft.get("warnings") or [])
                         if "summits in contact" in w]
    assert saturation_warned, (
        "a soft pad saturates the summits, which voids the exponential-tail "
        "result kappa rests on; the run must say so rather than returning a "
        "large multiplier silently")
    text = UNREAD_BY_THE_RATE["pad_hardness_shore_d"]
    assert "saturate" in text.lower(), text
    assert "ContactSolverOutOfRange" in text, text
