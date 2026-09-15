"""P4 unit tests — chemistry through the softened-hardness channel."""
import math

import pytest

from cmp_sim.core.solver import resolve, simulate
from cmp_sim.core.state import (Abrasive, Additive, Pad, Recipe, Slurry, Tool,
                                Wafer)
from cmp_sim.models import chemical_rate as cr


# ── the coupling channel ─────────────────────────────────────────────
def test_softening_the_surface_raises_removal_by_the_three_halves_power():
    """MRR ~ H^(-3/2): halving the effective hardness gives 2^1.5 = 2.83x."""
    assert cr.hardness_ratio_to_mrr_factor(0.5) == pytest.approx(2.0 ** 1.5, rel=1e-12)
    assert cr.hardness_ratio_to_mrr_factor(1.0) == pytest.approx(1.0, rel=1e-12)
    assert cr.hardness_ratio_to_mrr_factor(0.25) == pytest.approx(8.0, rel=1e-12)


def test_hardness_ratio_must_be_positive():
    with pytest.raises(ValueError):
        cr.hardness_ratio_to_mrr_factor(0.0)


# ── Langmuir ─────────────────────────────────────────────────────────
def test_langmuir_coverage_saturates():
    """theta = KC/(1+KC) -> 1. Beyond ~1/K more additive changes almost nothing,
    which is why a term that keeps rising with concentration is wrong."""
    assert cr.langmuir_coverage(0.0, 1000.0) == 0.0
    assert cr.langmuir_coverage(1.0 / 1000.0, 1000.0) == pytest.approx(0.5, rel=1e-9)
    assert cr.langmuir_coverage(1.0, 1000.0) > 0.999


def test_langmuir_is_monotonic():
    vals = [cr.langmuir_coverage(c, 100.0) for c in (0.001, 0.01, 0.1, 1.0)]
    assert vals == sorted(vals)


# ── Arrhenius ────────────────────────────────────────────────────────
def test_arrhenius_is_unity_at_the_reference_temperature():
    assert cr.arrhenius_factor(25.0, 25.0, 50.0) == pytest.approx(1.0, rel=1e-12)


def test_arrhenius_matches_the_closed_form():
    ea, t, t_ref = 50.0, 45.0, 25.0
    expected = math.exp(-(ea * 1e3 / 8.314462618)
                        * (1.0 / (t + 273.15) - 1.0 / (t_ref + 273.15)))
    assert cr.arrhenius_factor(t, t_ref, ea) == pytest.approx(expected, rel=1e-12)


def test_higher_activation_energy_means_stronger_temperature_sensitivity():
    """A chemically limited film responds to platen heating; a mechanically
    limited one (Ea -> 0) does not."""
    weak = cr.arrhenius_factor(45.0, 25.0, 10.0)
    strong = cr.arrhenius_factor(45.0, 25.0, 80.0)
    assert 1.0 < weak < strong


def test_a_20C_rise_with_50kJ_per_mol_roughly_triples_the_rate():
    """Standard chemical-kinetics rule of thumb; 50 kJ/mol is mid-range for CMP."""
    assert 2.5 < cr.arrhenius_factor(45.0, 25.0, 50.0) < 4.0


def test_cooling_below_the_reference_slows_the_reaction():
    assert cr.arrhenius_factor(15.0, 25.0, 50.0) < 1.0


# ── pack integration ─────────────────────────────────────────────────
def _resolved(film, pack, **slurry_kw):
    return resolve(Recipe(wafer=Wafer(film=film), slurry=Slurry(pack=pack, **slurry_kw)))


@pytest.mark.parametrize("film,pack", [
    ("cu", "cu_h2o2_bta"), ("w", "w_fe_oxidizer"), ("sti", "sti_ceria"),
])
def test_factor_is_exactly_unity_at_each_packs_reference_composition(film, pack):
    """The anti-double-counting invariant: a pack's Kp already contains its own
    chemistry, so the chemical multiplier must be 1.0 there."""
    eff = cr.chemical_factor(_resolved(film, pack))
    assert eff.factor == pytest.approx(1.0, rel=1e-6), (film, eff.terms)


def test_a_pack_without_chemistry_says_so_rather_than_implying_it_modelled_it():
    eff = cr.chemical_factor(_resolved("oxide", "oxide_silica"))
    assert eff.factor == pytest.approx(1.0)
    assert not eff.active
    assert any("inactive" in w for w in eff.warnings)


def test_temperature_without_an_activation_energy_is_warned_not_faked():
    eff = cr.chemical_factor(_resolved("cu", "cu_h2o2_bta"), temp_c=60.0)
    assert any("NOT modelled" in w for w in eff.warnings)
    assert "temperature" not in eff.terms


def test_inherited_notes_are_reported_in_english():
    """The inherited layer documents itself in Korean; nothing non-Latin may
    reach the user-facing output. (Typographic dashes are fine.)"""
    eff = cr.chemical_factor(_resolved("cu", "cu_h2o2_bta"))
    for text in eff.notes + eff.warnings:
        assert not any("\uac00" <= ch <= "\ud7a3" or "\u3040" <= ch <= "\u30ff"
                       or "\u4e00" <= ch <= "\u9fff" for ch in text), text


def test_inherited_notes_keep_their_numbers():
    eff = cr.chemical_factor(_resolved("cu", "cu_h2o2_bta"))
    joined = " ".join(eff.notes + eff.warnings)
    assert "values:" in joined


# ── composition response through the full model ──────────────────────
def _cu(model="full", **kw):
    adds = []
    if kw.get("h2o2") is not None:
        adds.append(Additive("hydrogen_peroxide", conc_wt_pct=kw["h2o2"], role="oxidizer"))
    if kw.get("bta") is not None:
        adds.append(Additive("benzotriazole", conc_mM=kw["bta"], role="inhibitor"))
    return simulate(Recipe(
        model=model, wafer=Wafer(film="cu", n_radial=21),
        slurry=Slurry(pack="cu_h2o2_bta", additives=adds, ph=kw.get("ph"),
                      temperature_c=kw.get("temp_c"),
                      abrasive=Abrasive(kind="silica", conc_wt_pct=kw.get("conc"),
                                        d50_nm=kw.get("d50"))),
        tool=Tool(pressure_psi=3.0, rpm_platen=60, rpm_head=60, time_s=60)))


def test_more_inhibitor_lowers_the_copper_rate():
    """BTA passivates copper — the first thing a formulator would check."""
    low = _cu(bta=0.1)
    high = _cu(bta=10.0)
    assert high.mean_rr_nm_per_min < low.mean_rr_nm_per_min
    assert high.factors["psi_chemistry"] < low.factors["psi_chemistry"]


def test_excess_oxidizer_lowers_the_copper_rate_through_thicker_passivation():
    """cu_h2o2_bta uses the passivation branch: past the optimum, more H2O2
    thickens the film and slows removal."""
    assert _cu(h2o2=5.0).mean_rr_nm_per_min < _cu(h2o2=0.5).mean_rr_nm_per_min


def test_a_formulation_change_actually_moves_the_answer():
    """Regression guard for the failure mode where the recipe is accepted but
    never reaches the pack, so every composition returns the same rate."""
    assert _cu(bta=0.1).mean_rr_nm_per_min != _cu(bta=10.0).mean_rr_nm_per_min


def test_the_reference_composition_reproduces_the_plain_preston_rate():
    plain = simulate(Recipe(model="preston", wafer=Wafer(film="cu", n_radial=21),
                            slurry=Slurry(pack="cu_h2o2_bta"),
                            tool=Tool(pressure_psi=3.0, rpm_platen=60, rpm_head=60)))
    full = _cu()
    assert full.mean_rr_nm_per_min == pytest.approx(plain.mean_rr_nm_per_min, rel=1e-6)
    assert all(v == pytest.approx(1.0, rel=1e-6) for v in full.factors.values())


def test_unmapped_additive_is_reported_instead_of_silently_dropped():
    r = simulate(Recipe(
        model="full", wafer=Wafer(film="cu", n_radial=21),
        slurry=Slurry(pack="cu_h2o2_bta",
                      additives=[Additive("mystery_compound_x", conc_mM=5.0)]),
        tool=Tool(pressure_psi=3.0, rpm_platen=60, rpm_head=60)))
    assert any("mystery_compound_x" in w for w in r.warnings)


def test_chemistry_terms_are_exposed_in_the_output():
    r = _cu(bta=5.0)
    assert "chemistry_terms" in r.extras
    assert "inhibitor" in r.extras["chemistry_terms"]
