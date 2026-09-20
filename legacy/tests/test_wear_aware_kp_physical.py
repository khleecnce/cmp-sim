"""wear_aware_kp_physical.py 회귀 테스트 — _self_test()의 항목을 pytest화.

주의(정직성): 이 모듈은 당초 가설("ad-hoc MRR=c_w*p_r와 물리기반 MRR=alpha_removal*n*V가
같은 방향으로 감쇠하고 상관계수가 높다")을 실제로는 반증했다 — n_contacts(t)는 감소가
아니라 증가하고, 두 정규화 곡선은 corr≈-0.998로 거의 완벽히 역상관이다(원인 추정은
wear_aware_kp_physical.py 상단 docstring "불일치 발견" 절 참조). 따라서 아래 테스트는
"당초 기대대로 단조감소/고상관"을 assert하지 않고, **실제로 관측된 방향과 부호**를
회귀 고정한다(수치를 조작해 거짓 PASS를 만들지 않기 위함).
"""
import numpy as np

import wear_aware_kp_physical as wkp
import pad_wear_glazing as pwg


def test_new_loop_matches_original_simulate_pad_wear():
    """동일 seed/파라미터에서 새 루프가 원본 simulate_pad_wear()를 수치적으로 정확히 재현."""
    r_orig = pwg.simulate_pad_wear(n_steps=30)
    r_new = wkp.simulate_pad_wear_with_contacts(n_steps=30)
    assert np.max(np.abs(r_new["MRR_adhoc"] - r_orig["MRR"]) / (np.abs(r_orig["MRR"]) + 1e-300)) < 1e-12
    for k in ("t", "p_r", "mean_height", "d"):
        assert np.max(np.abs(r_new[k] - r_orig[k]) / (np.abs(r_orig[k]) + 1e-300)) < 1e-12


def test_n_contacts_discrete_matches_definition():
    heights = np.array([0.1, 0.5, 0.9, 1.5, 2.0])
    d = 0.9
    assert wkp.n_contacts_discrete(heights, d) == int(np.sum(heights > d)) == 2


def test_n_contacts_actually_increases_under_fixed_pressure_wear():
    """실제 관측(불일치 발견): 명목압력 고정 하에서 마모가 진행되면 n_contacts(t)는
    감소가 아니라 증가한다(분리거리 d가 평균높이보다 더 빨리 내려가기 때문)."""
    r = wkp.simulate_pad_wear_with_contacts(n_steps=40)
    n = r["n_contacts"]
    assert n[-1] > n[0]
    assert np.all(np.diff(n) >= 0)


def test_normalized_curves_are_strongly_anticorrelated_not_matched():
    """당초 가설(상관계수 > 0.9)은 반증됨 — 실제로는 corr < -0.9 (거의 완벽한 역상관)."""
    cmp = wkp.compare_adhoc_vs_physical(pad_wear_kwargs={"n_steps": 40})
    assert cmp["corr"] < -0.9


def test_c1_zero_limit_n_contacts_constant():
    """회귀성 검증: 마모 없음(C1=0) 극한에서 n_contacts(t)는 상수여야 한다."""
    r0 = wkp.simulate_pad_wear_with_contacts(n_steps=40, C1=0.0)
    n0 = r0["n_contacts"]
    spread = (n0.max() - n0.min()) / n0.mean()
    assert spread < 1e-9
