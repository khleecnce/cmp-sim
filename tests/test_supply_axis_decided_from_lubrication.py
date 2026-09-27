"""The SUPPLY question is decided from the lubrication regime, not defaulted.

`legacy/sim/abrasive_mechanics.decide_supply` sets p and q — the concentration
and size exponents' supply factors — from the pad-wafer gap. The solver hands
it `pad_wafer_gap_m`, which no pack declares and no caller sets, so in every
run of this corpus the decision was never made: the inherited layer returned
the monolayer pair while announcing "the pad-wafer gap is unknown".

`models/luo_dornfeld._supply_from_lubrication` closes that axis with no new
constant. These tests pin the physics claims, not the code shape.
"""
from __future__ import annotations

import yaml

from cmp_sim.models import luo_dornfeld as ld
from cmp_sim.core.predictive_score import _recipe_for
from cmp_sim.core.validation import dataset_paths
from cmp_sim.api import run_recipe

from sim import abrasive_mechanics as am


def _first_row_regimes():
    out = []
    for path in dataset_paths():
        doc = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        conditions = doc.get("conditions") or []
        if not conditions:
            continue
        try:
            result = run_recipe(_recipe_for(doc, conditions[0]))
        except Exception:
            continue
        out.append((path.stem, result))
    return out


def test_boundary_lubrication_decides_a_monolayer_supply():
    """lambda < 1 means asperities carry the load, so a loaded particle sits in
    a contact whose clearance IS its own diameter. That is the monolayer case."""
    verdict, why = ld._supply_from_lubrication("boundary")
    assert verdict == "monolayer", why
    assert "asperit" in why and "monolayer" in why


def test_hydrodynamic_lubrication_does_not_license_a_verdict():
    """Once the fluid carries load the clearance at a loaded site is no longer
    pinned to the particle, so the argument must NOT be extrapolated. A closure
    that fires everywhere is not a closure."""
    for regime in ("mixed", "full_film"):
        verdict, why = ld._supply_from_lubrication(regime)
        assert verdict is None, f"{regime} must stay undetermined"
        assert "UNDETERMINED" in why
    assert ld._supply_from_lubrication(None) == (None, "")


def test_the_derived_verdict_agrees_with_the_inherited_monolayer_pair():
    """The derivation's whole claim is that p=1, q=2 was the RIGHT default and
    only its justification was missing. If the inherited fallback ever changes,
    that claim stops holding and this must fail rather than silently disagree."""
    reg = am.resolve_regime(area_pressure_exponent=1.0, gap_m=None, d_p_m=None)
    assert (reg.p, reg.q) == (am.P_MONOLAYER, am.Q_MONOLAYER)
    assert (am.P_MONOLAYER, am.Q_MONOLAYER) == (1.0, 2.0)


def test_deciding_the_supply_axis_changes_no_exponent():
    """This closure buys HONESTY, not accuracy: the values are identical, only
    their justification changed. A closure that moved the numbers would mean
    the corpus had been scored on a different model than it now is."""
    common = dict(area_pressure_exponent=1.0, contact_branch="elastic",
                  particle_diameter_m=1e-7)
    undecided = ld.resolve_regime(lubrication=None, **common)
    decided = ld.resolve_regime(lubrication="boundary", **common)
    assert (decided.p, decided.q) == (undecided.p, undecided.q)
    assert decided.n_conc == undecided.n_conc
    assert decided.n_size == undecided.n_size
    assert decided.supply_decided and not undecided.supply_decided


def test_every_scored_dataset_now_has_a_decided_supply_axis():
    """MEASURED, not assumed: all 49 runnable datasets are boundary-lubricated
    (lambda 0.002..0.148, tools/supply_gap_probe.py), so none of them may still
    report the supply geometry as an open question."""
    rows = _first_row_regimes()
    assert len(rows) >= 45, f"only {len(rows)} datasets ran"
    undecided = [name for name, r in rows
                 if not (r.get("abrasive_regime") or {}).get("supply_decided")]
    assert not undecided, f"supply axis still undecided on: {undecided}"


def test_no_run_still_claims_the_supply_geometry_is_unknown():
    """The half-fix that matters. Deciding the axis internally while the
    warning still lists 'supply geometry' as undetermined would leave the user
    reading a gap that has been closed."""
    for name, result in _first_row_regimes():
        for warning in result.get("warnings") or []:
            if "abrasive regime confidence" in warning:
                assert "or supply geometry was not determined" not in warning, (
                    f"{name} still reports the supply axis as open: {warning}")


def test_the_mean_fluid_film_is_not_used_as_the_contact_gap():
    """The bug this guards against. The solved mean film h averages over
    grooves and un-contacted valleys; h/d exceeds decide_supply's 1.5 threshold
    on 20 of 49 datasets and would halve p there. If anyone later wires
    slurry_supply.film_thickness_nm into pad_wafer_gap_m, p stops being 1.0 on
    those runs and this fires."""
    offenders = []
    for name, result in _first_row_regimes():
        supply = result.get("slurry_supply") or {}
        regime = result.get("abrasive_regime") or {}
        if supply.get("lubrication_regime") != "boundary":
            continue
        if regime.get("p") != 1.0:
            offenders.append((name, supply.get("film_thickness_nm"),
                              regime.get("p")))
    assert not offenders, (
        "a boundary-lubricated run reports p != 1, which means the supply "
        f"branch was decided from a gap rather than from the contact: {offenders}")
