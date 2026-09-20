"""competitive_metal_langmuir.py 회귀 테스트.

knowledge/cmp/post-cmp-residual-metal-prediction-langmuir-scm.md §6(A) python verify
블록의 assert 값을 그대로 재현한다 (임의 임계값 없음, 새 숫자 없음).
"""
import math

import competitive_metal_langmuir as cml


# ---------------------------------------------------------------------------
# §6(A) — Cr [M] 지수, 자리분율, pH3·10nM Cu 오더
# ---------------------------------------------------------------------------

def test_cr_concentration_exponent_matches_table_vi():
    """pH 3에서 pM 8->5([Cr] 1e-8->1e-5)일 때 log10(sigma비)/3 ~= 0.73 (Table VI n'=0.73)."""
    lo = cml.competitive_langmuir_surface({"Cr": (cml.K_CR, 1e-8)}, pH=3.0)["Cr"]
    hi = cml.competitive_langmuir_surface({"Cr": (cml.K_CR, 1e-5)}, pH=3.0)["Cr"]
    n_model = math.log10(hi / lo) / 3
    assert abs(n_model - 0.73) < 0.05


def test_site_fraction_of_sio2_surface_density():
    """sigma0 / 8e14(SiO2 표면 밀도) ~= 0.4% (논문 "0.4%")."""
    frac = cml.SIGMA0_DEFAULT / 8e14
    assert 0.003 < frac < 0.005


def test_ph3_10nm_cu_order_of_magnitude():
    """pH3, 10nM Cu(K_Cu를 K_Cr로 근사, 오더검증만): Table I 실측 0.9~1.7e10과 같은 자릿수."""
    sigma = cml.competitive_langmuir_surface({"Cu": (cml.K_CR, 1e-8)}, pH=3.0)["Cu"]
    assert 1e9 < sigma < 1e11


# ---------------------------------------------------------------------------
# 계약 테스트 — 단일 금속 항등성, 다중 금속 Theta 일관성
# ---------------------------------------------------------------------------

def test_single_metal_matches_no_competition_formula():
    """단일 금속 특례가 경쟁항 없는 sigma = sigma0*K*C/(1+K_H*H+K*C)와 일치."""
    K_M, C_M, pH = 1e6, 1e-6, 4.0
    H = 10 ** (-pH)
    expected = cml.SIGMA0_DEFAULT * K_M * C_M / (1 + cml.K_H_DEFAULT * H + K_M * C_M)
    result = cml.competitive_langmuir_surface({"M": (K_M, C_M)}, pH=pH)
    assert math.isclose(result["M"], expected, rel_tol=1e-12)


def test_theta_equals_sum_of_sigma_over_sigma0_for_multiple_metals():
    """여러 금속을 동시에 넣었을 때 Theta == sum(sigma_i)/sigma0."""
    metals = {
        "Cr": (1e6, 1e-6),
        "Cu": (1e6, 1e-7),
        "Fe": (1e5, 1e-5),
    }
    result = cml.competitive_langmuir_surface(metals, pH=4.0)
    theta = result.pop("_theta")
    assert math.isclose(theta, sum(result.values()) / cml.SIGMA0_DEFAULT, rel_tol=1e-12)
