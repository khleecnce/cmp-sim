"""cu_dishing_erosion_tugbawa.py 검증 — knowledge/cmp/cu-dishing-erosion-density-step-height-model-tugbawa.md
§7 verify 1-3의 정량값을 그대로 pytest 테스트로 이전.

출처: Tugbawa 2002 MIT 학위논문(Table 3.9), Tugbawa et al. 2001 CMP-MIC Fig 3-4.
"""
import numpy as np
import pytest

import cu_dishing_erosion_tugbawa as CDE

# Tugbawa 2002 Table 3.9 (실험세트 #1, Mirra, EPC-5001, 4 psi, 75 rpm)
R_CU = 159.0            # Å/s (a1, t >> tau_r=7.7 s)
R_OX_NOER = 4.34        # Å/s 엣지라운딩 미포함 추출값
R_OX_ER, C, S_C = 2.22, 3.04, 22.5   # 엣지라운딩 포함 추출값
D_MAX = 333.0           # Å, Table 3.9 B(=d_max at w=s=1µm 기준 아님 — verify 1에서는 상수 d_max로 직접 씀)


# ── verify 1(a): Hooke 압력 보존 (모듈 API 밖 — 배경 물리, eq 3.31-3.32 직접 재현) ──
def test_pressure_conservation():
    for phi in (0.1, 0.5, 0.9):
        for d_over_dmax in (0.0, 0.3, 1.0):
            P1 = 1.0
            P_ox = P1 + P1 * (phi / (1 - phi)) * d_over_dmax
            P_cu = P1 * (1 - d_over_dmax)
            assert abs((1 - phi) * P_ox + phi * P_cu - P1) < 1e-12


# ── verify 1(b): D_ss에서 RR_cu == RR_ox == Y1 (eq 3.33-3.34 교점) ──
def test_dss_matches_removal_rate_equality():
    for phi in (0.3, 0.5, 0.9):
        d = CDE.steady_state_dishing_tugbawa(R_CU, R_OX_ER, phi, D_MAX)
        RR_cu = R_CU * (1 - d / D_MAX)
        RR_ox = R_OX_ER + R_OX_ER * (phi / (1 - phi)) * (d / D_MAX)
        assert abs(RR_cu - RR_ox) / RR_ox < 1e-9
        assert abs(RR_ox - CDE.erosion_rate_Y1(R_CU, R_OX_ER, phi)) < 1e-9


# ── verify 1(c): 고립선 극한(Φ→0) D_ss → d_max(1 − r_ox/r_cu) ──
def test_dss_isolated_line_limit():
    d_ss = CDE.steady_state_dishing_tugbawa(R_CU, R_OX_ER, 1e-9, D_MAX)
    assert abs(d_ss - D_MAX * (1 - R_OX_ER / R_CU)) < 1e-6


# ── verify 1(d): Y1은 Φ에 단조증가 (erosion ∝ 밀도) ──
def test_y1_monotonic_in_density():
    phis = np.linspace(0.05, 0.95, 19)
    y1s = [CDE.erosion_rate_Y1(R_CU, R_OX_ER, p) for p in phis]
    assert np.all(np.diff(y1s) > 0)


# ── verify 1(e): Fig 3.14 판독 대조 (90%/50% 어레이, 92→110s) ──
def test_fig314_90pct_array_within_10pct():
    slope90 = (2850 - 1750) / (110 - 92)   # Å/s
    rox_eff = CDE.edge_rounding_psi(1.0, C, S_C) * R_OX_ER
    y90 = CDE.erosion_rate_Y1(R_CU, rox_eff, 0.9)
    assert abs(y90 - slope90) / slope90 < 0.10, (y90, slope90)


def test_fig314_50pct_array_overpredicts_25_to_55pct():
    slope50 = (540 - 330) / (110 - 92)     # Å/s
    rox_eff = CDE.edge_rounding_psi(1.0, C, S_C) * R_OX_ER
    y50 = CDE.erosion_rate_Y1(R_CU, rox_eff, 0.5)
    assert 0.25 < (y50 - slope50) / slope50 < 0.55, (y50, slope50)


def test_psi_correction_needed_for_90pct_array():
    slope90 = (2850 - 1750) / (110 - 92)
    y90_no_psi = CDE.erosion_rate_Y1(R_CU, R_OX_NOER, 0.9)
    assert y90_no_psi < 0.6 * slope90


# ── verify 2: Tugbawa 2001 Fig 4 기울기에서 유효 r_ox 부풀림 역산 (IPEC 472, 1단계) ──
def test_tugbawa2001_effective_rox_inflation():
    r_cu = 135.0
    r_ox_meas = 1.5
    slope80 = (2150 - 380) / (148 - 92)    # Å/s, 80% 밀도
    slope33 = (800 - 0) / (148 - 94)       # Å/s, 33% 밀도

    def r_from_Y1(y, phi):
        return y * r_cu * (1 - phi) / (r_cu - y * phi)

    r80, r33 = r_from_Y1(slope80, 0.80), r_from_Y1(slope33, 0.33)

    # 측정 블랭킷값 1.5 Å/s로는 두 기울기를 설명 못 한다
    assert CDE.erosion_rate_Y1(r_cu, r_ox_meas, 0.80) < slope80 / 4
    assert CDE.erosion_rate_Y1(r_cu, r_ox_meas, 0.33) < slope33 / 6
    # 역산한 유효 r_ox는 두 밀도에서 30% 이내로 서로 근접, 측정값의 5-7배(논문 "6-10배"와 같은 오더)
    assert abs(r80 - r33) / max(r80, r33) < 0.30, (r80, r33)
    assert 5 <= r80 / r_ox_meas <= 7 and 6 <= r33 / r_ox_meas <= 7.5


def test_tugbawa2001_tau3_order_of_magnitude():
    r_cu = 135.0
    slope80 = (2150 - 380) / (148 - 92)
    slope33 = (800 - 0) / (148 - 94)

    def r_from_Y1(y, phi):
        return y * r_cu * (1 - phi) / (r_cu - y * phi)

    r80, r33 = r_from_Y1(slope80, 0.80), r_from_Y1(slope33, 0.33)

    def dmax_from(Dss, r, phi):
        return Dss * (r_cu * (1 - phi) + r * phi) / ((r_cu - r) * (1 - phi))

    d80 = dmax_from(265, r80, 0.80)
    d33 = dmax_from(320, r33, 0.33)
    assert abs(d80 - d33) / d33 < 0.05, (d80, d33)

    tau80 = CDE.tau3(r_cu, r80, 0.80, d80)
    tau33 = CDE.tau3(r_cu, r33, 0.33, d33)
    assert 1.5 < tau80 < 3.5 and 1.5 < tau33 < 3.5


# ── verify 3: d_max(w, s) 경험식 — 체감 멱법칙·스페이스 포화·Fig 3.12 지수 ──
def test_dmax_monotonic_concave_and_space_saturates():
    for B, a2, b2 in ((333.0, 0.303, 0.259), (372.4, 0.188, 0.185)):
        w = np.array([0.25, 0.5, 1, 2, 5, 10, 50])
        d = np.array([CDE.d_max_from_linewidth_space(x, 100, B, a2, b2) for x in w])
        assert np.all(np.diff(d) > 0)
        assert np.all(np.diff(d) / np.diff(w) > 0)
        assert np.all(np.diff(np.diff(d) / np.diff(w)) < 0)   # 체감(오목)
        assert CDE.d_max_from_linewidth_space(1, 200, B, a2, b2) == \
            CDE.d_max_from_linewidth_space(1, 100, B, a2, b2)   # s >= s_l 포화
        r10 = (CDE.d_max_from_linewidth_space(10, 100, B, a2, b2) /
               CDE.d_max_from_linewidth_space(1, 100, B, a2, b2))
        assert abs(r10 - 10 ** a2) < 1e-12


def test_dmax_fig312_isolated_line_ratio_matches_alpha2_set1():
    w_m = np.array([0.25, 0.35, 0.5, 1, 2, 5, 10])
    D_m = np.array([250, 270, 330, 660, 1000, 1220, 1400])
    ratio_meas = D_m[-1] / D_m[3]
    assert abs(ratio_meas - 10 ** 0.303) / ratio_meas < 0.10   # #1 alpha2 6% 일치
    assert abs(ratio_meas - 10 ** 0.188) / ratio_meas > 0.20   # #2 alpha2는 27% 과소


def test_edge_rounding_psi_decreases_with_space_and_saturates_to_1():
    psi_narrow = CDE.edge_rounding_psi(1.0, C, S_C)
    psi_wide = CDE.edge_rounding_psi(100.0, C, S_C)
    assert psi_narrow > psi_wide > 1.0
    assert abs(psi_narrow - 3.9) < 0.1


# ── 종합 함수 cu_overpolish_dishing_erosion — dict 스키마·경고 플래그 ──
def test_composite_function_schema_and_calibration_warning():
    out = CDE.cu_overpolish_dishing_erosion(
        r_cu=R_CU, r_ox_measured=R_OX_ER, phi_cu=0.5, w=1.0, s=1.0, t_overpolish=100.0)
    assert set(out) == {"dishing_nm", "erosion_nm", "d_ss_nm", "tau3_s", "notes"}
    assert out["dishing_nm"] > 0
    assert out["erosion_nm"] > 0
    assert any("Table 3.9" in n for n in out["notes"])


def test_composite_function_overpolish_flag_high_density():
    out = CDE.cu_overpolish_dishing_erosion(
        r_cu=R_CU, r_ox_measured=R_OX_ER, phi_cu=0.97, w=1.0, s=1.0, t_overpolish=100.0)
    assert any("과대예측" in n for n in out["notes"])


def test_composite_function_long_time_approaches_steady_state():
    d_max = CDE.d_max_from_linewidth_space(1.0, 1.0, 333.0, 0.303, 0.259)
    r_ox_eff = CDE.edge_rounding_psi(1.0, C, S_C) * R_OX_ER
    d_ss_expected = CDE.steady_state_dishing_tugbawa(R_CU, r_ox_eff, 0.5, d_max)
    out = CDE.cu_overpolish_dishing_erosion(
        r_cu=R_CU, r_ox_measured=R_OX_ER, phi_cu=0.5, w=1.0, s=1.0, t_overpolish=1000.0)
    assert abs(out["dishing_nm"] * 10.0 - d_ss_expected) / d_ss_expected < 1e-3


def test_composite_function_custom_params_skips_default_warning():
    custom = dict(CDE.DEFAULT_PARAMS)
    out = CDE.cu_overpolish_dishing_erosion(
        r_cu=R_CU, r_ox_measured=R_OX_ER, phi_cu=0.5, w=1.0, s=1.0, t_overpolish=100.0,
        params=custom)
    assert not any("Table 3.9" in n for n in out["notes"])
