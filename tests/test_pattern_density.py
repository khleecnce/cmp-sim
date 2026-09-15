"""P6 unit tests — pattern density, step height, dishing and erosion."""
import numpy as np
import pytest

from cmp_sim.models import pattern_density as pd


def _layout(n=401, span_m=0.02, dense=0.8, sparse=0.2):
    """Half the die dense, half sparse — the classic pattern-density test case."""
    x = np.linspace(0.0, span_m, n)
    rho = np.where(x < span_m / 2.0, dense, sparse)
    return x, rho


# ── effective density ────────────────────────────────────────────────
def test_effective_density_smooths_the_layout_over_the_planarization_length():
    """The pad cannot see a step change in density: at the dense/sparse
    boundary the effective density must vary smoothly between the two levels.
    (Far from the boundary it still equals the local value, since the kernel is
    normalised and the layout is locally flat.)"""
    x, rho = _layout()
    eff = pd.effective_density(x, rho, 1.0e-3)
    mid = len(x) // 2
    window = eff[mid - 40:mid + 40]
    assert 0.2 < float(np.min(window)) < float(np.max(window)) < 0.8
    assert np.all(np.diff(window) < 0)          # monotonic dense -> sparse
    assert eff[mid] == pytest.approx(0.5, abs=0.02)   # symmetric at the edge


def test_a_longer_planarization_length_smooths_more():
    x, rho = _layout()
    short = pd.effective_density(x, rho, 2.0e-4)
    long_ = pd.effective_density(x, rho, 3.0e-3)
    assert float(np.ptp(long_)) < float(np.ptp(short))


def test_a_uniform_layout_is_unchanged_by_smoothing():
    x = np.linspace(0.0, 0.02, 201)
    rho = np.full_like(x, 0.5)
    assert np.allclose(pd.effective_density(x, rho, 1e-3), 0.5, rtol=1e-6)


def test_planarization_length_must_be_positive():
    x, rho = _layout()
    with pytest.raises(ValueError):
        pd.effective_density(x, rho, 0.0)


# ── the inverse-density law ──────────────────────────────────────────
def test_dense_regions_polish_slower():
    """RR_up = K/rho_eff. This is the central prediction of the MIT model:
    dense arrays clear last and end up thicker."""
    rates = pd.up_area_rate(1.0e-9, np.array([0.2, 0.5, 0.8]))
    assert rates[0] > rates[1] > rates[2]
    assert rates[0] / rates[2] == pytest.approx(4.0, rel=1e-12)


def test_zero_density_is_rejected_rather_than_producing_infinite_rate():
    with pytest.raises(ValueError):
        pd.up_area_rate(1e-9, np.array([0.5, 0.0]))


# ── step height ──────────────────────────────────────────────────────
def test_step_falls_linearly_and_reaches_zero_at_the_predicted_time():
    K, rho, h0 = 1.0e-9, np.array([0.5]), 500.0e-9
    t_c = pd.planarization_time_s(K, 0.5, h0)
    assert t_c == pytest.approx(0.5 * h0 / K, rel=1e-12)
    assert pd.step_height(0.0, K, rho, h0)[0] == pytest.approx(h0, rel=1e-12)
    assert pd.step_height(t_c / 2, K, rho, h0)[0] == pytest.approx(h0 / 2, rel=1e-9)
    assert pd.step_height(t_c, K, rho, h0)[0] == pytest.approx(0.0, abs=1e-18)


def test_step_never_goes_negative():
    K, rho, h0 = 1e-9, np.array([0.3, 0.6]), 400e-9
    assert np.all(pd.step_height(1e5, K, rho, h0) >= 0.0)


def test_dense_regions_planarize_later():
    """t_c is proportional to density: the spread in clearing time is what
    forces overpolish, which is what causes dishing."""
    assert (pd.planarization_time_s(1e-9, 0.8, 500e-9)
            > pd.planarization_time_s(1e-9, 0.2, 500e-9))


def test_compressible_pad_decays_exponentially_and_joins_continuously():
    K, rho, h0, h_c, tau = 1.0e-9, np.array([0.5]), 500e-9, 50e-9, 20.0
    t_c = 0.5 * (h0 - h_c) / K
    at_c = pd.step_height(t_c, K, rho, h0, pad_compressible=True,
                          tau_s=tau, contact_step_m=h_c)[0]
    assert at_c == pytest.approx(h_c, rel=1e-6)
    later = pd.step_height(t_c + tau, K, rho, h0, pad_compressible=True,
                           tau_s=tau, contact_step_m=h_c)[0]
    assert later == pytest.approx(h_c * np.exp(-1.0), rel=1e-6)
    assert later > 0.0            # never reaches zero, unlike the linear branch


def test_compressible_pad_without_tau_is_an_error_not_a_guess():
    with pytest.raises(ValueError):
        pd.step_height(1.0, 1e-9, np.array([0.5]), 500e-9, pad_compressible=True)


def test_contact_height_decreases_with_density():
    h = pd.contact_height_m(np.array([0.1, 0.5, 0.9]), 20e-9, 200e-9, 0.3)
    assert h[0] > h[1] > h[2]


# ── dishing and erosion ──────────────────────────────────────────────
def test_steady_state_dishing_is_bounded_by_dmax():
    d = pd.steady_state_dishing_m(rate_metal=5e-9, rate_oxide=1e-10,
                                  metal_density=0.5, dishing_max_m=100e-9,
                                  oxide_sensitivity_b=1e6)
    assert 0.0 <= d <= 100e-9


def test_dishing_self_limits_where_the_two_rates_balance():
    """At d_ss the metal and oxide rates are equal, which is why dishing
    saturates instead of growing forever."""
    rm, rox, rho_m, dmax, b = 5e-9, 2e-10, 0.4, 120e-9, 5e6
    d = pd.steady_state_dishing_m(rm, rox, rho_m, dmax, b)
    r_metal = rm * (1 - d / dmax)
    r_oxide = rox / (1 - rho_m) * (1 + b * d)
    assert r_metal == pytest.approx(r_oxide, rel=1e-6)


def test_higher_selectivity_gives_deeper_dishing():
    """The trade-off a slurry designer must live with: protecting the stop
    layer means the metal recedes further."""
    shallow = pd.steady_state_dishing_m(5e-9, 1.0e-9, 0.4, 120e-9, 5e6)
    deep = pd.steady_state_dishing_m(5e-9, 5.0e-11, 0.4, 120e-9, 5e6)
    assert deep > shallow


def test_erosion_grows_with_density_and_overpolish_time():
    a = pd.erosion_m(1e-10, 0.3, 30.0)
    b = pd.erosion_m(1e-10, 0.8, 30.0)
    c = pd.erosion_m(1e-10, 0.8, 60.0)
    assert b > a
    assert c == pytest.approx(2.0 * b, rel=1e-12)


def test_density_outside_zero_to_one_is_rejected():
    with pytest.raises(ValueError):
        pd.erosion_m(1e-10, 1.0, 30.0)
    with pytest.raises(ValueError):
        pd.steady_state_dishing_m(5e-9, 1e-10, 1.2, 100e-9, 1e6)


def test_selectivity_needs_a_positive_stop_rate():
    assert pd.selectivity(5e-9, 1e-10) == pytest.approx(50.0, rel=1e-12)
    with pytest.raises(ValueError):
        pd.selectivity(5e-9, 0.0)


# ── end-to-end ───────────────────────────────────────────────────────
def test_evaluate_reports_dishing_when_given_the_parameters():
    x, rho = _layout()
    res = pd.evaluate(blanket_rate_m_per_s=5e-9, rho_local=rho, x_m=x,
                      planarization_length_m=1e-3, initial_step_m=500e-9,
                      time_s=60.0, rate_stop_m_per_s=1e-10,
                      dishing_max_m=120e-9, oxide_sensitivity_b=5e6,
                      overpolish_time_s=30.0)
    d = res.as_dict()
    assert d["dishing_nm"] > 0
    assert d["erosion_nm"] > 0
    assert d["selectivity"] == pytest.approx(50.0, rel=1e-6)


def test_evaluate_refuses_to_invent_dishing_without_its_parameters():
    x, rho = _layout()
    res = pd.evaluate(blanket_rate_m_per_s=5e-9, rho_local=rho, x_m=x,
                      planarization_length_m=1e-3, initial_step_m=500e-9,
                      time_s=60.0)
    assert res.dishing_m is None
    assert any("not computed" in w for w in res.warnings)


def test_high_selectivity_is_warned_as_a_dishing_risk():
    x, rho = _layout()
    res = pd.evaluate(blanket_rate_m_per_s=5e-9, rho_local=rho, x_m=x,
                      planarization_length_m=1e-3, initial_step_m=500e-9,
                      time_s=60.0, rate_stop_m_per_s=1e-11)
    assert any("dishing worse" in w or "dishing" in w for w in res.warnings)
