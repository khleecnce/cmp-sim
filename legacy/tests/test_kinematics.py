"""kinematics.py 회귀 테스트 — kinematics.py 하단 _selftest()의 5개 검증 항목을 pytest화.

물리 로직은 재구현하지 않고 kinematics.py의 함수를 그대로 호출해 assert한다.
"""
import numpy as np
import pytest

import kinematics as km

R_W = 0.150  # m, 300mm 웨이퍼
R_CC = 0.200  # m
RPM = 60.0


def test_rs1_uniform_speed():
    """Rs=1(omega_w=omega_p)이면 웨이퍼 전면 상대속도가 완전 균일 (Lai Eq. 2.12)."""
    s = km.speed_stats(R_W, R_CC, RPM, RPM)
    expect = km.rpm_to_rads(RPM) * R_CC
    assert s["std"] < 1e-12
    assert abs(s["mean"] - expect) < 1e-12


@pytest.mark.parametrize("rpm_w", [50.0, 55.0, 66.0, 72.0])
def test_nonuniformity_matches_2mu_analytic(rpm_w):
    """비균일도 nu_ref = (max-min)/v_ref 가 해석해 2|mu|와 일치."""
    s = km.speed_stats(R_W, R_CC, rpm_w, 60.0)
    pred = 2.0 * abs(s["mu"])
    assert abs(s["nu_ref"] - pred) / pred < 1e-12


def test_cartesian_matches_polar_form():
    """Lai(직교좌표) 식과 JJMIE(극좌표) 식이 수치적으로 동일."""
    th = np.linspace(0, 2 * np.pi, 37)
    rn = np.array([0.25, 0.5, 0.75, 1.0])[:, None]
    ww, wp = km.rpm_to_rads(55.0), km.rpm_to_rads(60.0)
    x = rn * R_W * np.cos(th)
    y = rn * R_W * np.sin(th)
    _, _, v_cart = km.relative_velocity(x, y, ww, wp, R_CC)
    v_pol = km.relative_speed_polar(rn, th, ww, wp, R_CC, R_W)
    assert float(np.max(np.abs(v_cart - v_pol))) < 1e-12


def test_rs1_preston_profile_flat():
    """Rs=1이면 반경별 Preston MRR 프로파일이 완전 평탄."""
    rs, mrr = km.preston_mrr_profile(R_W, R_CC, 60.0, 60.0, 20.7e3, 1.0e-13)
    flat = float((mrr.max() - mrr.min()) / mrr.mean())
    assert flat < 1e-12


def test_rs_neq1_edge_faster_than_center():
    """RPM 불일치(Rs!=1)이면 시간평균 MRR이 엣지에서 더 빠름 (edge-fast WIWNU)."""
    rs, mrr = km.preston_mrr_profile(R_W, R_CC, 50.0, 60.0, 20.7e3, 1.0e-13)
    assert mrr[-1] > mrr[0]
