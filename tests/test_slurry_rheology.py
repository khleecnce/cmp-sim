"""Slurry property derivation — checked against independent published values."""
import pytest

from cmp_sim.slurry import rheology as rh


# ── water viscosity vs the CRC Handbook ──────────────────────────────
@pytest.mark.parametrize("temp_c,expected_pa_s", [
    (20.0, 1.002e-3),
    (25.0, 0.890e-3),
    (40.0, 0.653e-3),
])
def test_water_viscosity_matches_handbook_within_2pct(temp_c, expected_pa_s):
    """Vogel fit vs CRC Handbook of Chemistry and Physics tabulated values."""
    got = rh.water_viscosity_pa_s(temp_c)
    assert abs(got - expected_pa_s) / expected_pa_s < 0.02, (temp_c, got, expected_pa_s)


def test_water_viscosity_decreases_with_temperature():
    assert rh.water_viscosity_pa_s(60) < rh.water_viscosity_pa_s(25) < rh.water_viscosity_pa_s(5)


# ── wt% -> volume fraction (mass balance) ────────────────────────────
def test_volume_fraction_is_exact_mass_balance():
    """30 wt% silica (2200 kg/m3) in water: phi = (0.3/2200)/((0.3/2200)+(0.7/997))."""
    phi = rh.volume_fraction_from_wt_pct(30.0, 2200.0)
    expected = (0.3 / 2200.0) / ((0.3 / 2200.0) + (0.7 / 997.0))
    assert phi == pytest.approx(expected, rel=1e-12)
    assert phi < 0.30          # denser particles -> volume fraction below weight fraction


def test_zero_and_invalid_loading():
    assert rh.volume_fraction_from_wt_pct(0.0, 2200.0) == 0.0
    with pytest.raises(ValueError):
        rh.volume_fraction_from_wt_pct(120.0, 2200.0)


# ── Krieger-Dougherty ────────────────────────────────────────────────
def test_kd_reduces_to_einstein_in_the_dilute_limit():
    eta0 = 1.0e-3
    for phi in (1e-4, 1e-3):
        kd = rh.krieger_dougherty_viscosity(phi, eta0)
        ein = rh.einstein_viscosity(phi, eta0)
        assert abs(kd - ein) / ein < 2e-3, phi


def test_kd_exceeds_einstein_at_practical_loading_and_is_monotonic():
    eta0 = 1.0e-3
    assert rh.krieger_dougherty_viscosity(0.2, eta0) > rh.einstein_viscosity(0.2, eta0)
    vals = [rh.krieger_dougherty_viscosity(p, eta0) for p in (0.05, 0.10, 0.20, 0.35)]
    assert vals == sorted(vals)


def test_kd_refuses_to_extrapolate_past_jamming():
    with pytest.raises(ValueError):
        rh.krieger_dougherty_viscosity(0.70, 1.0e-3)


# ── ionic strength and Debye length ──────────────────────────────────
def test_ionic_strength_of_a_1_1_salt():
    """0.01 M KCl: I = 0.5*(0.01*1 + 0.01*1) = 0.01 M."""
    I = rh.ionic_strength_M({"KCl": {"conc_M": 0.01, "charge": 1, "n_ions": 2}})
    assert I == pytest.approx(0.01, rel=1e-12)


def test_ionic_strength_of_a_divalent_salt_is_higher():
    mono = rh.ionic_strength_M({"s": {"conc_M": 0.01, "charge": 1, "n_ions": 2}})
    di = rh.ionic_strength_M({"s": {"conc_M": 0.01, "charge": 2, "n_ions": 2}})
    assert di == pytest.approx(4.0 * mono, rel=1e-12)


def test_debye_length_of_1mM_monovalent_is_about_9_6_nm():
    """Textbook value: kappa^-1 ~ 0.304/sqrt(I) nm for a 1:1 electrolyte,
    i.e. ~9.6 nm at 1 mM (Israelachvili, Intermolecular and Surface Forces)."""
    assert rh.debye_length_nm(1e-3) == pytest.approx(9.6, rel=0.05)


def test_debye_length_shrinks_as_salt_rises():
    assert rh.debye_length_nm(1e-1) < rh.debye_length_nm(1e-3) < rh.debye_length_nm(1e-5)


# ── end-to-end derivation ────────────────────────────────────────────
def test_derive_flags_electrostatic_repulsion_for_silica_on_oxide_at_high_ph():
    p = rh.derive(12.0, 2200.0, ph=10.5, abrasive_iep_ph=2.5, film_iep_ph=2.7)
    assert p.zeta_sign_abrasive == "negative" and p.zeta_sign_film == "negative"
    assert "repulsive" in p.electrostatic_regime
    assert p.viscosity_pa_s > rh.water_viscosity_pa_s(25.0)
    assert p.debye_length_nm > 0


def test_derive_flags_attraction_for_ceria_on_oxide_at_mid_ph():
    """Ceria IEP ~7, silica-oxide IEP ~2.5: at pH 5 ceria is positive and the
    oxide negative, hence electrostatic attraction — the window ceria STI
    slurries are formulated in."""
    p = rh.derive(1.0, 7215.0, ph=5.0, abrasive_iep_ph=7.0, film_iep_ph=2.5)
    assert p.zeta_sign_abrasive == "positive" and p.zeta_sign_film == "negative"
    assert "attractive" in p.electrostatic_regime


def test_derive_warns_when_ionic_strength_comes_from_ph_only():
    p = rh.derive(5.0, 2200.0, ph=4.0)
    assert any("lower bound" in w for w in p.warnings)


def test_measured_values_override_derived_ones():
    p = rh.derive(5.0, 2200.0, ph=4.0, measured_viscosity_pa_s=3.0e-2,
                  measured_zeta_mv=-45.0)
    assert p.viscosity_pa_s == 3.0e-2
    assert p.zeta_sign_abrasive == "negative"
    assert any("measured viscosity" in n for n in p.notes)


def test_weak_zeta_raises_an_agglomeration_warning():
    p = rh.derive(5.0, 2200.0, ph=4.0, measured_zeta_mv=-8.0)
    assert any("agglomeration" in w for w in p.warnings)


def test_abrasive_without_density_is_an_error_not_a_guess():
    with pytest.raises(ValueError):
        rh.derive(10.0, None, ph=7.0)
