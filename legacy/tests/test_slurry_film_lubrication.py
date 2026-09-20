"""slurry_film_lubrication.py의 self-test 항목을 pytest화한 회귀 테스트."""
import math

from slurry_film_lubrication import (
    z0_length_scale,
    h_min_scaling,
    h_min_wafer_rotation_effect,
    h_min_curvature_effect,
)


def test_z0_order_of_magnitude_matches_paper():
    mu = 5e-3
    omega2 = 60 * 2 * math.pi / 60.0
    R1 = 4 * 0.0254
    R2 = 7 * 0.0254
    P_app = 21e3
    z0 = z0_length_scale(mu, omega2, R1, R2, P_app)
    assert 1e-6 < z0 < 1e-3


def test_z0_decreases_with_pressure():
    mu, omega2, R1, R2 = 5e-3, 6.283, 0.1016, 0.1778
    z0_low = z0_length_scale(mu, omega2, R1, R2, 10e3)
    z0_high = z0_length_scale(mu, omega2, R1, R2, 40e3)
    assert z0_high < z0_low


def test_h_min_scaling_increases_with_velocity():
    mu, P_app = 5e-3, 21e3
    h_slow = h_min_scaling(mu, 0.3, P_app)
    h_fast = h_min_scaling(mu, 1.2, P_app)
    assert h_fast > h_slow


def test_h_min_scaling_decreases_with_porosity_and_compressibility():
    mu, U, P_app = 5e-3, 0.75, 21e3
    h_k0 = h_min_scaling(mu, U, P_app, k_porosity=0.0)
    h_k1 = h_min_scaling(mu, U, P_app, k_porosity=2.0)
    assert h_k1 < h_k0
    h_c0 = h_min_scaling(mu, U, P_app, c_compress=0.0)
    h_c1 = h_min_scaling(mu, U, P_app, c_compress=2.0)
    assert h_c1 < h_c0


def test_wafer_rotation_offsets_pad_inflow():
    h_low = h_min_wafer_rotation_effect(omega1=0.2)
    h_high = h_min_wafer_rotation_effect(omega1=2.0)
    assert h_high < h_low


def test_curvature_has_interior_maximum():
    d0_values = [1e-6, 5e-6, 10e-6, 15e-6, 25e-6]
    h_curv = [h_min_curvature_effect(d0) for d0 in d0_values]
    imax = h_curv.index(max(h_curv))
    assert 0 < imax < len(d0_values) - 1


def test_p_app_zero_raises():
    import pytest
    with pytest.raises(ValueError):
        h_min_scaling(5e-3, 0.75, 0.0)
