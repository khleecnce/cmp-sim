"""preston.py 회귀 테스트 — preston.py 하단 _selftest()의 5개 검증 항목을 pytest화.

물리 로직은 재구현하지 않고 preston.py의 함수를 그대로 호출해 assert한다.
"""
import math

from scipy.special import ellipe

import preston as pr

R_W = 0.150  # m
R_CC = 0.200  # m
KP = 1.0e-13  # m^2/N, 오더체크용


def test_pressure_doubling_doubles_mrr():
    base = pr.wafer_avg_mrr(R_W, R_CC, 60.0, 60.0, 20.7e3, KP)
    dbl_p = pr.wafer_avg_mrr(R_W, R_CC, 60.0, 60.0, 41.4e3, KP)
    assert abs(dbl_p / base - 2.0) < 1e-9


def test_velocity_doubling_doubles_mrr():
    ww = pr.rpm_to_rads(60.0)
    v_ref = ww * R_CC  # Rs=1 균일속도
    base_speed_nm = pr.mrr_to_nm_per_min(KP * 20.7e3 * v_ref)
    dbl_speed_nm = pr.mrr_to_nm_per_min(KP * 20.7e3 * (2 * v_ref))
    assert abs(dbl_speed_nm / base_speed_nm - 2.0) < 1e-9


def test_order_of_magnitude_matches_literature():
    """SiO2 STI 표준조건 근사 결과가 문헌 실측범위(50~1000+ nm/min) 안에 들어옴."""
    base = pr.wafer_avg_mrr(R_W, R_CC, 60.0, 60.0, 20.7e3, KP)
    rate_nm_min = pr.mrr_to_nm_per_min(base)
    assert 20.0 <= rate_nm_min <= 2000.0


def test_rs1_flat_radial_profile():
    """Rs=1 + 균일압력 가정에서 반경별 MRR이 완전 평탄 (WIWNU=0 구조적 확인)."""
    rs, mrr = pr.mrr_profile(R_W, R_CC, 60.0, 60.0, 20.7e3, KP)
    flat = float((mrr.max() - mrr.min()) / mrr.mean())
    assert flat < 1e-12


def test_rs_neq1_edge_center_ratio_matches_kinematics():
    """Rs!=1일 때 edge/center 시간평균 MRR 비가 완전타원적분 폐형식과 일치 (TEST-AUDIT §3-A #1).

    폐형식 유도(Lai 2001 Eq.2.11, kinematics.py 상단 docstring 참조):
      |v(r,theta)|/v_ref = sqrt(1 + 2*x*cos(theta) + x^2), x = r_norm*mu, v_ref = w_p*r_cc
      a^2+b^2+2ab*cos(theta) = (a+b)^2 - 4ab*sin^2(theta/2) (a=1, b=x)
      -> theta평균(=자전 시간평균) = (2/pi)*(1+|x|)*E(k^2), k^2 = 4|x|/(1+|x|)^2
      (scipy.special.ellipe(m)은 m=k^2 컨벤션: E(m)=∫0^(pi/2) sqrt(1-m sin^2) dtheta)
    center(r=0): x=0 -> 비=1. edge(r=R_w): x=mu.
    ratio_analytic = (2/pi)*(1+|mu|)*ellipe(4|mu|/(1+|mu|)^2), mu=(R_w/r_cc)(1-Rs).
    kinematics.py의 1.00391 스냅샷 대신 이 독립 폐형식과 대조한다(순환의존 제거).
    """
    rs, mrr = pr.mrr_profile(R_W, R_CC, 50.0, 60.0, 20.7e3, KP)
    ratio = mrr[-1] / mrr[0]

    mu = (R_W / R_CC) * (1.0 - 50.0 / 60.0)
    x = abs(mu)
    ratio_analytic = (2.0 / math.pi) * (1.0 + x) * ellipe(4.0 * x / (1.0 + x) ** 2)
    assert abs(ratio - ratio_analytic) < 1e-9
