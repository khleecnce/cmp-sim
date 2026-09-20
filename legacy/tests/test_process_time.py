"""process_time.py 회귀 테스트 — process_time.py 하단 _selftest()의 4개 검증 항목을 pytest화.

물리 로직은 재구현하지 않고 process_time.py(및 그것이 의존하는 preston.py)의 함수를
그대로 호출해 assert한다.
"""
import numpy as np

import process_time as pt
import preston as pr

R_W = 0.150  # m
R_CC = 0.200  # m
KP = 1.0e-13


def test_removed_thickness_linear_in_time():
    rs, mrr = pr.mrr_profile(R_W, R_CC, 60.0, 60.0, 20.7e3, KP)
    th_60 = pt.removed_thickness(rs, mrr, 60.0)
    th_120 = pt.removed_thickness(rs, mrr, 120.0)
    ratio = float(np.max(np.abs(th_120 / th_60 - 2.0)))
    assert ratio < 1e-9


def test_endpoint_time_halves_when_mrr_doubles():
    rs, mrr = pr.mrr_profile(R_W, R_CC, 60.0, 60.0, 20.7e3, KP)
    target = 100e-9  # 100 nm
    mrr_ref = mrr.mean()
    t_base = pt.endpoint_time(target, mrr_ref)
    t_double = pt.endpoint_time(target, 2.0 * mrr_ref)
    assert abs(t_double / t_base - 0.5) < 1e-9


def test_rs1_uniform_pressure_wiwnu_near_zero():
    rs1, mrr1 = pr.mrr_profile(R_W, R_CC, 60.0, 60.0, 20.7e3, KP)
    w1 = pt.wiwnu_percent(mrr1)
    assert w1 < 1e-9


def test_rs_neq1_wiwnu_small_positive_order():
    """Rs=50/60일 때 WIWNU가 작은 양수 (정밀값이 아닌 오더 확인, kinematics.py/preston.py의
    edge/center=1.00391과 정합하는 0.4% 근방 예상)."""
    rs2, mrr2 = pr.mrr_profile(R_W, R_CC, 50.0, 60.0, 20.7e3, KP)
    w2 = pt.wiwnu_percent(mrr2)
    assert 0.0 < w2 < 5.0
