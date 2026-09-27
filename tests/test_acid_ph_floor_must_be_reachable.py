"""The acid-side pH floor must be REACHABLE before it may hold a number.

Background
----------
``chemical_rate.ph_response`` uses ``ph_acid_mechanical_floor`` only on the
branch where ``pH < ph_peak``, and ``chemical_rate`` clamps the evaluated pH
into the pack's ``ph_valid_range`` *before* that branch is selected (the far
tail of a locally fitted Gaussian is an artefact of the function, not of a
measurement). Composing those two gives a purely structural condition:

    the acid floor can act  <=>  ph_valid_range[0] < ph_peak

When a pack's optimum sits AT the lower edge of the window its constants were
measured over — which is what happens whenever the sweep's lowest pH is also
its highest rate — no admissible query is ever below the peak, and the acid
floor cannot enter any prediction at any pressure, speed or formulation.

Why this matters more than "an unused key"
------------------------------------------
Two packs carried ``0.010`` here at ``confidence: low`` with the source line
"TODO(owner) - order-of-magnitude bound, not a measurement". In ``cu_h2o2_bta``
(ph_peak 3.0, range [3.0, 6.0]) that number was unreachable, so it read as a
sourced physical property of the copper system while being incapable of ever
being tested or refuted. This repo's rule is that an inert term is acceptable
but a SILENTLY inert one is not; an inert *invented number* is worse again,
because the invention is what the reachability would have exposed.

What is pinned
--------------
Not the absence of the constant — a measured acid limb is real physics and the
value may come back. The CONDITION is pinned:

* a pack may hold a non-null acid floor only if that floor is reachable, or if
  the value is 0.0 (which asserts "nothing measured below the optimum" rather
  than asserting a rate);
* a withdrawn one must say what would restore it;
* and the reachability is measured on the SHIPPING solver, not read off the
  constants, so a change to the clamp or to ``ph_response`` re-opens the axis
  automatically.
"""
from __future__ import annotations

import pytest

from cmp_sim.api import run_recipe
from cmp_sim.core.params import load_pack
from cmp_sim.core.predictive_score import PACK_FILM

KEY = "ph_acid_mechanical_floor"
PACKS_WITH_THE_KEY = ["oxide_silica", "cu_h2o2_bta", "oxide_silica_anionic",
                      "oxide_silica_aminosilane", "sti_ceria",
                      "sic_ceria_h2o2"]


def _pack_and_film(name):
    return load_pack(name), PACK_FILM[name]


def _rate(pack_name, film, ph, override: object = ...):
    recipe = {
        "model": "auto",
        "wafer": {"film": film, "n_radial": 11},
        "slurry": {"pack": pack_name, "ph": ph},
        "tool": {"pressure_psi": 4.0, "rpm_platen": 60, "rpm_head": 60,
                 "time_s": 60.0},
    }
    if override is not ...:
        recipe["params"] = {KEY: override}
    value = run_recipe(recipe).get("removal_rate_A_per_min")
    return None if not value else float(value)


def _reachable(pack):
    peak = pack.get_or("ph_peak", None)
    rng = pack.get_or("ph_valid_range", None)
    if peak is None or not isinstance(rng, (list, tuple)) or len(rng) != 2:
        return False
    return float(rng[0]) < float(peak)


@pytest.mark.parametrize("name", PACKS_WITH_THE_KEY)
def test_an_acid_floor_that_cannot_act_may_not_hold_an_invented_number(name):
    pack, _film = _pack_and_film(name)
    param = pack.params.get(KEY)
    if param is None:
        pytest.skip(f"{name} does not declare {KEY}")
    if param.value is None:
        assert "restore only if" in (param.note or "").lower(), (
            f"{name} leaves {KEY} null without stating the measurement that "
            "would restore it. A refusal with no exit condition becomes "
            "permanent by accident.")
        return
    if _reachable(pack):
        return
    assert float(param.value) == 0.0, (
        f"{name} holds {KEY} = {param.value} but its optimum (ph_peak "
        f"{pack.get_or('ph_peak', None)}) is at the lower edge of "
        f"ph_valid_range {pack.get_or('ph_valid_range', None)}, so the pH is "
        "clamped before ph_response can ever select the acid branch. That "
        "number cannot enter any prediction and cannot be refuted by any "
        "measurement — which is how an order-of-magnitude guess passes for a "
        "sourced property. Either widen ph_valid_range with data, or set it "
        "to 0.0 / null with the restoring measurement named.")


@pytest.mark.parametrize("name", ["cu_h2o2_bta", "oxide_silica_anionic"])
def test_the_unreachability_is_measured_on_the_shipping_solver(name):
    """A claim about code paths must be confirmed on the path that ships.

    Reading ``ph_response`` and the clamp is an argument; running the solver
    is the evidence. Scanning far outside the valid range is deliberate — the
    clamped query IS the case under test.
    """
    pack, film = _pack_and_film(name)
    alternative = pack.get_or("ph_mechanical_floor", None)
    assert alternative is not None, (
        f"{name} has no alkaline floor to substitute, so this probe cannot "
        "distinguish 'unreachable' from 'no term at all'")
    assert not _reachable(pack), (
        f"{name} became reachable (ph_valid_range now extends below ph_peak), "
        "so the acid limb is measured territory and this closure is stale: "
        "re-open the axis and fit the floor to the new data")

    moved = []
    for ph in (1.0, 2.0, 3.0, 4.0, 6.0, 8.0, 10.0, 12.0, 13.0):
        base = _rate(name, film, ph)
        alt = _rate(name, film, ph, alternative)
        if base and alt:
            moved.append(abs(alt - base) / base)
    assert moved, "the solver returned no rate at any pH — the probe is broken"
    assert max(moved) < 1e-6, (
        f"{name}: replacing {KEY} moved the rate by {max(moved) * 100:.3f}%, "
        "so it IS reachable and the structural argument above is wrong")


def test_a_reachable_acid_floor_is_not_silently_inert():
    """The other half of the claim: where it IS reachable, it must matter.

    "It goes somewhere else" and "it is switched off here" are excuses unless
    the place it does act is also asserted. sti_ceria measures the acid limb
    (Dandu 2009 sweeps pH 2-10 against an optimum of 4.5), so its floor must
    move the rate — otherwise the whole key is dead and withdrawing it from
    two packs was treating a symptom.
    """
    pack, film = _pack_and_film("sti_ceria")
    assert _reachable(pack)
    base = _rate("sti_ceria", film, 2.0)
    raised = _rate("sti_ceria", film, 2.0, 0.5)
    assert base and raised
    assert raised / base > 2.0, (
        "sti_ceria's acid floor is reachable in principle but does not move "
        f"the rate ({base:.1f} -> {raised:.1f} A/min). Then the key is inert "
        "everywhere and should be removed from the model, not just from the "
        "packs where it is structurally blocked.")
