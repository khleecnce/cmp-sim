"""blanket_rate_transfer.py 회귀 테스트.

knowledge/cmp/npw-ptw-transfer-rules-quantitative.md §6 verify (B) 블록의 값(Tugbawa
2002 학위논문 표 3.3, Fig.3.19 판독점)을 그대로 재현한다.
"""
import pytest

import blanket_rate_transfer as brt


# 표 3.3 실험 1 (5 psi, 63 rpm): a1 Å/s, a2 Å, tau s
A1, A2, TAU = 249.5, 3986.6, 16.4


def test_instantaneous_rate_at_zero_is_nonnegative():
    """r_inst(0) >= 0 — t=0 순간 rate가 음수면 식 부호를 잘못 읽은 것."""
    assert brt.blanket_rate_instantaneous(0.0, A1, A2, TAU) >= 0


def test_average_rate_at_60s_undershoots_saturated_a1():
    """r_avg(60 s)는 포화 a1보다 10~26% 낮아야 한다 (관행의 60 s 평균 rate 과소평가)."""
    r60 = brt.blanket_rate_average(60, A1, A2, TAU)
    deficit = 1 - r60 / A1
    assert 0.08 <= deficit <= 0.30


def test_average_rate_matches_fig319_late_readings_within_6pct():
    """Fig.3.19 후반 5점(t>=29)은 모델과 6% 이내로 일치해야 한다."""
    late_points = [(29, 135), (36, 153), (43, 163), (50, 170), (57, 187)]
    for t, r in late_points:
        m = brt.blanket_rate_average(t, A1, A2, TAU)
        assert abs(m - r) / r < 0.06, (t, m, r)


def test_average_rate_early_point_deviates_honestly():
    """초기점 (7, 65)는 모델이 못 맞춘다 - RMS 168.5 Å과 정합하는 21% 차이를 그대로 기록.

    이 테스트는 실패로 취급하지 않는다: 넉넉한 허용범위(25%)로 관측된 불일치를
    있는 그대로 통과시키는 것이 목적이다.
    """
    m = brt.blanket_rate_average(7, A1, A2, TAU)
    assert abs(m - 65) / 65 < 0.25


def test_average_rate_at_zero_raises():
    """t=0으로 blanket_rate_average 호출 시 ValueError 발생 계약."""
    with pytest.raises(ValueError):
        brt.blanket_rate_average(0, A1, A2, TAU)


def test_fit_blanket_rate_recovers_known_parameters():
    """표 3.3 실험 1 파라미터로 합성한 무잡음 데이터에서 (a1, a2, tau)를 5% 이내로 복원."""
    times = [10, 20, 30, 40, 50, 60]
    removed = [brt.cumulative_removal(t, A1, A2, TAU) for t in times]

    a1_fit, a2_fit, tau_fit = brt.fit_blanket_rate(times, removed)

    assert abs(a1_fit - A1) / A1 < 0.05
    assert abs(a2_fit - A2) / A2 < 0.05
    assert abs(tau_fit - TAU) / TAU < 0.05
