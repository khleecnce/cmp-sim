"""P2 unit tests — Greenwood-Williamson contact mechanics.

These assert the *physics claims* the layer is built on, not a code snapshot.
"""
import pytest

from cmp_sim.models import contact_gw as cg


@pytest.fixture(scope="module")
def ref_pad():
    """IC1000-class reference: E* 1 GPa, R 5 um, eta 2e8 /m2, sigma_z 0.3 um.
    Values and their sources live in legacy/knowledge/params/base.yaml."""
    return cg.PadContactState(e_star_pa=1.0e9, asperity_radius_m=5.0e-6,
                              asperity_density_m2=2.0e8, height_sigma_m=0.3e-6)


@pytest.fixture(scope="module")
def load_scan(ref_pad):
    return cg.verify_load_independence(ref_pad)


# ── the three GW claims ──────────────────────────────────────────────
def test_mean_real_contact_pressure_is_load_independent(load_scan):
    """GW 1966: with exponential summit heights, p_r = W/A_r does not depend on
    load. This is why Preston's MRR ~ P holds. Pressure spans 7-96 kPa here."""
    assert load_scan["p_r_spread_rel"] < 1e-6, load_scan["p_r_spread_rel"]


def test_real_contact_area_is_linear_in_load(load_scan):
    assert load_scan["a_r_over_p_spread_rel"] < 1e-6


def test_contact_count_is_linear_in_load(load_scan):
    """Raising the down-force recruits more contacts rather than loading each
    one harder — the microscopic origin of the Preston linearity."""
    assert load_scan["n_over_p_spread_rel"] < 1e-6


def test_numeric_solution_agrees_with_the_closed_form_ratio(ref_pad, load_scan):
    """p_r from the inverse solve must equal 1/(A_r/W) from the analytic ratio."""
    expected = 1.0 / load_scan["analytic_a_r_over_w"]
    got = load_scan["p_r_mean_pa"][0]
    assert abs(got - expected) / expected < 1e-3


def test_real_contact_is_a_small_fraction_of_nominal_area(ref_pad):
    """A polyurethane pad touches the wafer over well under 1% of its area at
    CMP pressures — the reason local contact pressure is ~100x nominal."""
    frac = ref_pad.real_area_fraction(20.7e3)
    assert 1e-6 < frac < 1e-2, frac


def test_local_pressure_greatly_exceeds_nominal(ref_pad):
    nominal = 20.7e3
    assert ref_pad.mean_real_pressure_pa(nominal) > 100.0 * nominal


# ── pad property dependence (this is what makes the layer useful) ────
def test_softer_pad_gives_more_real_contact_area(ref_pad):
    soft = cg.PadContactState(e_star_pa=3.0e8, asperity_radius_m=5.0e-6,
                              asperity_density_m2=2.0e8, height_sigma_m=0.3e-6)
    f, notes, _warn = cg.contact_factor(soft, ref_pad, 20.7e3)
    assert f > 1.0
    assert notes


def test_contact_factor_is_exactly_unity_for_the_reference_pad(ref_pad):
    """No double counting: a pack's Kp was calibrated on its reference pad, so
    the contact factor must be 1.0 there."""
    f, _notes, _warn = cg.contact_factor(ref_pad, ref_pad, 20.7e3)
    assert f == pytest.approx(1.0, rel=1e-9)


def test_rougher_pad_has_fewer_but_more_heavily_loaded_contacts(ref_pad):
    rough = cg.PadContactState(e_star_pa=1.0e9, asperity_radius_m=5.0e-6,
                               asperity_density_m2=2.0e8, height_sigma_m=1.0e-6)
    assert rough.mean_real_pressure_pa(20.7e3) > ref_pad.mean_real_pressure_pa(20.7e3)
    assert rough.real_area_fraction(20.7e3) < ref_pad.real_area_fraction(20.7e3)


def test_denser_asperities_increase_contact_count(ref_pad):
    dense = cg.PadContactState(e_star_pa=1.0e9, asperity_radius_m=5.0e-6,
                               asperity_density_m2=8.0e8, height_sigma_m=0.3e-6)
    assert dense.n_contacts(20.7e3) > ref_pad.n_contacts(20.7e3)


def test_dn_dp_slope_is_positive_and_reproducible(ref_pad):
    slope = ref_pad.dn_dp_per_pa()
    assert slope > 0
    assert ref_pad.dn_dp_per_pa([10e3, 30e3, 60e3]) == pytest.approx(slope, rel=1e-3)


# ── validity boundary ────────────────────────────────────────────────
def test_elastic_assumption_holds_for_a_pad_on_oxide(ref_pad):
    """Plasticity index psi = (E*/H) sqrt(sigma/R). For a soft pad against a
    7 GPa oxide psi << 1, so elastic GW applies."""
    assert ref_pad.plasticity_index(7.0e9) < 1.0


def test_plasticity_index_rises_for_a_soft_film(ref_pad):
    """SnAg solder (H ~ 0.2 GPa) is far softer, pushing the contact plastic —
    the elastic result must not be trusted there."""
    assert ref_pad.plasticity_index(0.2e9) > ref_pad.plasticity_index(7.0e9)


# ── Shore D correlation ──────────────────────────────────────────────
def test_shore_d_to_modulus_is_the_right_order_for_ic1000():
    """IC1000 is quoted at 55-60 Shore D and measures a few hundred MPa."""
    e = cg.shore_d_to_youngs_modulus_pa(57.0)
    assert 1.0e8 < e < 1.0e9, e


def test_shore_d_to_modulus_is_monotonic():
    vals = [cg.shore_d_to_youngs_modulus_pa(s) for s in (30, 40, 50, 60)]
    assert vals == sorted(vals)


def test_shore_d_range_guard():
    assert cg.shore_d_conversion_is_in_range(57.0)
    assert not cg.shore_d_conversion_is_in_range(85.0)


def test_equivalent_modulus_is_pad_dominated():
    """E* must sit just below the pad modulus: the wafer is ~200x stiffer."""
    e_pad = 3.2e8
    e_star = cg.equivalent_modulus_pa(e_pad)
    assert 0.9 * e_pad < e_star < 1.3 * e_pad


def test_equivalent_modulus_accounts_for_a_hard_film():
    """Against 450 GPa SiC E* is marginally higher than against 70 GPa oxide."""
    soft_film = cg.equivalent_modulus_pa(3.2e8, e_wafer_pa=7.0e10)
    hard_film = cg.equivalent_modulus_pa(3.2e8, e_wafer_pa=4.5e11)
    assert hard_film > soft_film
