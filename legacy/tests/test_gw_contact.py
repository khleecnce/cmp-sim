"""gw_contact.py 회귀 테스트 — 하단 _self_test()의 5개 검증 항목을 pytest화.

물리 로직은 재구현하지 않고 gw_contact.py의 함수를 그대로 호출해 assert한다.
"""
import math

import numpy as np

import gw_contact as gw

E_STAR = 1e9  # Pa, 등가탄성계수 오더
R = 5e-6  # m, asperity 반경 오더


def test_hertz_force_scales_as_delta_power_1p5():
    """압입깊이 2배 -> 힘은 2^1.5배 (Hertz 비선형 스케일링)."""
    F1 = gw.hertz_force(1e-7, E_STAR, R)
    F2 = gw.hertz_force(2e-7, E_STAR, R)
    ratio = F2 / F1
    expect = 2 ** 1.5
    assert abs(ratio - expect) / expect < 1e-9


def test_hertz_contact_radius_consistency():
    """접촉면적으로부터 역산한 반경 a에 대해 a^2 = R*delta가 성립."""
    delta = 1.5e-7
    area = gw.hertz_contact_area(delta, R)
    a = math.sqrt(area / math.pi)
    assert abs(a ** 2 - R * delta) / (R * delta) < 1e-9


def test_gw_area_load_ratio_independent_of_separation():
    """지수분포 GW 모델의 A_r/W 비율이 분리거리 d와 무관하며 폐형식과 일치."""
    beta = 1.0 / 0.3e-6
    eta = 1e11
    A_n = 1e-4
    ratios_numeric = []
    for d in [0.0, 0.2e-6, 0.5e-6]:
        r = gw.gw_numeric(d, beta, eta, A_n, E_STAR, R)
        ratios_numeric.append(r["A_r"] / r["W"])
    analytic = gw.gw_analytic_ratio(beta, E_STAR, R)
    max_dev = max(abs(rn - analytic) / analytic for rn in ratios_numeric)
    assert max_dev < 1e-3


def test_area_vs_load_slope_matches_analytic_ratio():
    """asperity 밀도 eta를 바꿔가며 만든 (W, A_r) 쌍의 선형회귀 기울기가 폐형식과 일치."""
    beta = 1.0 / 0.3e-6
    A_n = 1e-4
    d_fixed = 0.3e-6
    etas = [0.5e11, 1e11, 2e11, 4e11]
    Ws, Ars = [], []
    for e in etas:
        r = gw.gw_numeric(d_fixed, beta, e, A_n, E_STAR, R)
        Ws.append(r["W"])
        Ars.append(r["A_r"])
    slope = np.polyfit(Ws, Ars, 1)[0]
    analytic = gw.gw_analytic_ratio(beta, E_STAR, R)
    assert abs(slope - analytic) / analytic < 1e-3


def test_plasticity_index_order_of_magnitude():
    """소성지수 psi가 GW 1966 소성판정 임계(gw_contact.py:87, psi>1)와 일치 (TEST-AUDIT §3-A #6).

    H=50e6(모듈 주석: "미검증 오더값")에서 psi≈4.9 → psi>1이므로 GW1966 판정으로는
    소성접촉 지배(gw_contact.py:87 "psi>1이면 소성 접촉 지배"). knowledge/materials/
    pad-hardness-porosity-measurement-methods.md는 IC1000/IC1010 경도를 Shore D60으로만
    보고하고(§1), Shore D→Pa 환산식은 ASTM D2240 원문 미확보로 그 노트에 의도적으로
    없다(§2) — 따라서 문헌 H(Pa)로 정밀 대조는 불가능하고, 대신 범위를 기존 4자릿수
    (0.01~100)에서 1자릿수(1~10)로 좁혀 GW1966 임계와의 정성적 일치만 확인한다.
    """
    H = 50e6
    psi = gw.plasticity_index(E_STAR, H, 0.3e-6, R)
    assert 1.0 < psi < 10.0
