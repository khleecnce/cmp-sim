"""P2 integration — the GW contact factor must change the answer, correctly."""
import pytest

from cmp_sim.core.solver import simulate
from cmp_sim.core.state import Pad, Recipe, Slurry, Tool, Wafer


def _recipe(model="gw_preston", **pad_kw):
    return Recipe(model=model,
                  wafer=Wafer(film="oxide", n_radial=21),
                  slurry=Slurry(pack="oxide_silica"),
                  pad=Pad(**pad_kw),
                  tool=Tool(pressure_psi=3.0, rpm_platen=60, rpm_head=60, time_s=60))


def test_default_pad_reproduces_the_preston_result_exactly():
    """With no pad properties given, the pack's reference pad is used, so
    kappa = 1.0 and the GW model must equal plain Preston to the last digit."""
    a = simulate(_recipe(model="preston"))
    b = simulate(_recipe(model="gw_preston"))
    assert b.factors["kappa_contact"] == pytest.approx(1.0, rel=1e-12)
    assert b.mean_rr_nm_per_min == pytest.approx(a.mean_rr_nm_per_min, rel=1e-12)


def test_a_softer_pad_raises_the_rate():
    base = simulate(_recipe())
    soft = simulate(_recipe(shore_d=35.0))
    assert soft.factors["kappa_contact"] > 1.0
    assert soft.mean_rr_nm_per_min > base.mean_rr_nm_per_min


def test_a_harder_pad_lowers_the_rate():
    soft = simulate(_recipe(shore_d=35.0))
    hard = simulate(_recipe(shore_d=60.0))
    assert hard.mean_rr_nm_per_min < soft.mean_rr_nm_per_min


def test_out_of_range_hardness_is_warned_not_silently_extrapolated():
    r = simulate(_recipe(shore_d=85.0))
    assert any("validity range" in w for w in r.warnings)


def test_denser_asperities_raise_the_rate():
    base = simulate(_recipe())
    dense = simulate(_recipe(asperity_density_m2=8.0e8))
    assert dense.factors["kappa_contact"] > 1.0
    assert dense.mean_rr_nm_per_min > base.mean_rr_nm_per_min


def test_rougher_pad_reduces_contact_area_and_rate():
    """A rougher surface concentrates the load on fewer summits: less real
    contact area at the same nominal pressure, hence a lower rate."""
    base = simulate(_recipe())
    rough = simulate(_recipe(roughness_beta_inv_m=1.0e-6))
    assert rough.factors["kappa_contact"] < 1.0
    assert rough.mean_rr_nm_per_min < base.mean_rr_nm_per_min


def test_the_pad_factor_is_reported_with_its_reasoning():
    r = simulate(_recipe(shore_d=45.0))
    assert "kappa_contact" in r.factors
    assert any("GW contact" in n for n in r.notes)
    assert any("Shore D" in n for n in r.notes)


def _rate(psi, **pad_kw):
    rec = _recipe(**pad_kw)
    rec.tool.pressure_psi = psi
    return simulate(rec)


def test_pressure_linearity_survives_the_contact_layer_below_saturation():
    """While contact is confined to the exponential tail of the summit heights,
    GW keeps A_r linear in load, so doubling the pressure doubles the rate even
    with the contact factor on. Checked on a stiff pad, which stays unsaturated."""
    a = _rate(2.0, shore_d=60.0)
    b = _rate(4.0, shore_d=60.0)
    assert not any("saturation" in w for w in a.warnings + b.warnings)
    assert b.mean_rr_nm_per_min == pytest.approx(2.0 * a.mean_rr_nm_per_min, rel=1e-6)


def test_a_saturated_soft_pad_breaks_linearity_and_says_so():
    """A very soft pad brings nearly every summit into contact at CMP pressure.
    Then A_r can no longer grow linearly, the GW exponential-tail result is void,
    and the simulator must warn instead of quietly returning a wrong number."""
    a = _rate(2.0, shore_d=45.0)
    b = _rate(4.0, shore_d=45.0)
    assert any("summits in contact" in w for w in b.warnings), b.warnings
    # and the rate is demonstrably sub-linear in pressure
    assert b.mean_rr_nm_per_min < 2.0 * a.mean_rr_nm_per_min


def test_unknown_model_is_rejected():
    with pytest.raises(ValueError):
        simulate(_recipe(model="nope"))
