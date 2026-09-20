"""pad_viscoelastic_temperature.py 회귀 테스트.

지식노트의 python verify 블록 assert 값을 그대로 재현한다 (임의 임계값 없음, 새 숫자 없음):
  knowledge/materials/pad-viscoelasticity-temp-frequency-dma.md §3.1, §6
"""
import numpy as np
import pytest

import pad_viscoelastic_temperature as pvt


# ---------------------------------------------------------------------------
# §6(1) — WLF 재매개화
# ---------------------------------------------------------------------------

def test_wlf_reparametrize_matches_literature():
    """(17.44, 51.6) + dT=50 -> (8.86, 101.6), 0.03% 이내 (노트 §6(1) assert abs<0.01)."""
    C1, C2 = pvt.wlf_reparametrize(17.44, 51.6, 50.0)
    assert abs(C1 - 8.86) < 0.01
    assert abs(C2 - 101.6) < 1e-9
    assert C1 == pytest.approx(8.857, abs=1e-3)


def test_wlf_shift_identity_across_reparametrization():
    """두 매개화(Tr=Tg vs Tr=Tg+50)가 임의 온도에서 같은 상대 shift를 주는지."""
    Tg = 0.0
    C1_new, C2_new = pvt.wlf_reparametrize(17.44, 51.6, 50.0)
    for T in (Tg + 60, Tg + 80, Tg + 100):
        lhs = pvt.wlf_log_aT(T, Tg, 17.44, 51.6) - pvt.wlf_log_aT(Tg + 50, Tg, 17.44, 51.6)
        rhs = pvt.wlf_log_aT(T, Tg + 50, C1_new, C2_new)
        assert abs(lhs - rhs) < 1e-9


def test_wlf_log_aT_at_60c_tg_43p6():
    """60°C, Tg=43.6°C(Cabot 1D DSC)에서 log_aT가 -4.3~-4.1 사이 (노트 §6(1) assert)."""
    la = pvt.wlf_log_aT(60.0, 43.6)
    assert -4.3 < la < -4.1


# ---------------------------------------------------------------------------
# §3.1 — Cabot US20170087688A1 Table 1B 앵커점 재현
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("pad_id", sorted(pvt.CABOT_TABLE_1B))
def test_e_pad_from_table_reproduces_all_anchor_points(pad_id):
    """모든 6개 패드에서 25/50/80°C 앵커점 3개 모두 오차 0으로 재현(보간이므로)."""
    row = pvt.CABOT_TABLE_1B[pad_id]
    for T, E in zip(row["T_C"], row["E_MPa"]):
        assert pvt.e_pad_from_table(float(T), pad_id) == pytest.approx(E, abs=1e-9)


def test_e_pad_from_table_1d_specific_anchors():
    """PROFILE.md 예시 값 그대로: 1D 25°C=1590, 80°C=5 MPa."""
    assert pvt.e_pad_from_table(25.0, "1D") == pytest.approx(1590, abs=1e-9)
    assert pvt.e_pad_from_table(80.0, "1D") == pytest.approx(5, abs=1e-9)


def test_e_pad_midpoint_matches_loglinear_formula():
    """50°C 중간값이 e_pad_loglinear의 로그선형 공식과 정확히 일치하는지(수식 자체 검증)."""
    row = pvt.CABOT_TABLE_1B["1D"]
    manual = np.exp(np.interp(50.0, row["T_C"], np.log(row["E_MPa"])))
    assert pvt.e_pad_from_table(50.0, "1D") == pytest.approx(manual, abs=1e-9)


def test_e_pad_from_table_clamps_outside_range():
    """범위 밖 조회는 최근접 앵커로 clamp — 외삽 없음."""
    assert pvt.e_pad_from_table(10.0, "1D") == pvt.e_pad_from_table(25.0, "1D")
    assert pvt.e_pad_from_table(100.0, "1D") == pvt.e_pad_from_table(80.0, "1D")


# ---------------------------------------------------------------------------
# e_pad_loglinear 입력 가드 (문헌값 아님 — 순수함수 계약)
# ---------------------------------------------------------------------------

def test_loglinear_rejects_mismatched_lengths():
    with pytest.raises(ValueError):
        pvt.e_pad_loglinear(50.0, [25, 50, 80], [1000, 141])


def test_loglinear_rejects_non_ascending_points():
    with pytest.raises(ValueError):
        pvt.e_pad_loglinear(50.0, [80, 50, 25], [19, 141, 1000])


def test_loglinear_rejects_nonpositive_E():
    with pytest.raises(ValueError):
        pvt.e_pad_loglinear(50.0, [25, 50, 80], [1000, 0, 19])


def test_e_pad_from_table_rejects_unknown_pad_id():
    with pytest.raises(ValueError):
        pvt.e_pad_from_table(50.0, "unknown-pad")
