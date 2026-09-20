"""pad_glazing_jeong2024.py 회귀 테스트 — _self_test()의 항목을 pytest화.

노트 knowledge/materials/pad-glazing-mechanism-mrr-decay.md §4 (A)(B)의 값만 재현한다
(새 문헌 숫자 없음). relative_mrr_proxy 관련 테스트는 정성(방향성)만 확인한다 — 모듈
docstring의 '정직 기록'(피크 시점·t=10 상대값이 Fig.9와 어긋남)을 참조.
"""
import numpy as np

import pad_glazing_jeong2024 as pg


def test_contact_loss_2psi_10min():
    t_tab, N_tab, _ = pg.contact_count_table()
    loss = 1 - N_tab[2][-1] / N_tab[2][0]
    assert abs(loss - 0.486) < 0.005


def test_tau_5psi_shorter_than_2psi():
    assert pg.contact_decay_tau_min(5) < pg.contact_decay_tau_min(2)


def test_eq4_muR_2psi_10min():
    assert abs(pg.mean_asperity_radius_um(2, 10.0) - 19.6) < 0.1


def test_radius_growth_ratio_range():
    ratio = pg.radius_growth_ratio(2, 10.0)
    assert 2.0 < ratio < 3.0


def test_contact_decay_tau_rejects_unsupported_pressure():
    import pytest
    with pytest.raises(ValueError):
        pg.contact_decay_tau_min(2.5)


def test_relative_mrr_proxy_nonmonotonic_rise_then_fall():
    """비단조 상승-후-하강 패턴 존재 여부만 확인 (정성). 값·피크 시점을 Fig.9와 비교하지 않는다."""
    ts = np.arange(0, 11, 1.0)
    proxy_vals = np.array([pg.relative_mrr_proxy(2, t) for t in ts])
    peak_idx = int(np.argmax(proxy_vals))
    assert 0 < peak_idx < len(ts) - 1, "피크가 구간 내부(t=0..10 사이)에 있어야 비단조 상승-후-하강"
    assert np.all(np.diff(proxy_vals[:peak_idx + 1]) > 0), "피크 이전은 단조 상승이어야 함"
    assert np.all(np.diff(proxy_vals[peak_idx:]) < 0), "피크 이후는 단조 하강이어야 함"
