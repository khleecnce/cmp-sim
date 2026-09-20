"""disk_active_grit_fraction.py 회귀 테스트 — _self_test()의 항목을 pytest화.

노트 knowledge/equipment/cvd-diamond-disk-patterned-grit-array.md §2, §3.2 verify 블록의
균일분포 오더 추정·문헌 상수만 재현한다(새 문헌 숫자 없음).
"""
import pytest

import disk_active_grit_fraction as dagf


def test_active_fraction_uniform_three_points():
    h_lo, h_hi = 40.0, 90.0
    f_5 = dagf.active_fraction_uniform(h_lo, h_hi, 5.0)
    f_10 = dagf.active_fraction_uniform(h_lo, h_hi, 10.0)
    f_15 = dagf.active_fraction_uniform(h_lo, h_hi, 15.0)
    assert abs(f_5 - 0.10) < 1e-9
    assert abs(f_10 - 0.20) < 1e-9
    assert abs(f_15 - 0.30) < 1e-9
    # 노트 §2 assert 그대로: 5µm→10%(>=0.05), 15µm→30%(<=0.35) 경계
    assert 0.05 <= f_5
    assert f_15 <= 0.35


def test_active_fraction_uniform_clamp_upper():
    # engage_depth(100) > h_hi-h_lo(50) -> f_a는 1.0으로 clamp
    f_a = dagf.active_fraction_uniform(40.0, 90.0, 100.0)
    assert abs(f_a - 1.0) < 1e-9


def test_active_fraction_uniform_negative_raises():
    with pytest.raises(ValueError):
        dagf.active_fraction_uniform(40.0, 90.0, -5.0)


def test_active_fraction_single_height():
    assert abs(dagf.active_fraction_single_height() - 1.0) < 1e-9


def test_n_effective_arithmetic():
    assert abs(dagf.n_effective(25000, 0.2) - 5000.0) < 1e-9


def test_rcadd_cdd_effective_ratio_reproduces_2_8x():
    ratios = dagf.known_effective_ratios()
    assert abs(ratios["rcadd_eff"] - 484.0 / 10000.0) < 1e-9
    assert abs(ratios["cdd_eff"] - 432.0 / 25000.0) < 1e-9
    assert 2.5 < ratios["ratio"] < 3.0
    assert abs(ratios["ratio"] - 2.8) < 0.1


def test_disk_active_grit_fraction_uniform_mode():
    out = dagf.disk_active_grit_fraction("uniform", 10.0, 25000, h_lo=40.0, h_hi=90.0)
    assert set(out.keys()) == {"f_active", "n_effective"}
    assert abs(out["f_active"] - 0.20) < 1e-9
    assert abs(out["n_effective"] - 5000.0) < 1e-9


def test_disk_active_grit_fraction_single_height_mode():
    out = dagf.disk_active_grit_fraction("single_height", 10.0, 1300)
    assert abs(out["f_active"] - 1.0) < 1e-9
    assert abs(out["n_effective"] - 1300.0) < 1e-9


def test_disk_active_grit_fraction_measured_histogram_not_implemented():
    with pytest.raises(NotImplementedError):
        dagf.disk_active_grit_fraction("measured histogram", 10.0, 1000)
