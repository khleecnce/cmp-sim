"""electrical_thickness_extraction.py 회귀 테스트.

노트 knowledge/cmp/product-wafer-proxy-metrics-virtual-metrology.md §6 verify (C)/(D)
블록의 숫자·허용오차를 그대로 옮긴다(새 문헌 숫자 없음).
"""
import electrical_thickness_extraction as ete


# ── (C) Park et al. 1999 §V.A: 라이너/Cu 저항비 ~200, 병렬 무시 오차 <0.5% ──────

def test_liner_parallel_resistance_ratio_rho_cu_2_0_matches_literature_200():
    r = ete.liner_parallel_resistance_ratio(0.35, 0.40, 0.025, 100.0, 2.0)
    assert 150 <= r <= 250


def test_liner_neglect_error_fraction_below_half_percent_for_1_7_and_2_0():
    for rho_Cu in (1.7, 2.0):
        r = ete.liner_parallel_resistance_ratio(0.35, 0.40, 0.025, 100.0, rho_Cu)
        assert ete.liner_neglect_error_fraction(r) < 0.005


def test_liner_neglect_error_fraction_exceeds_half_percent_at_2_2_boundary():
    r = ete.liner_parallel_resistance_ratio(0.35, 0.40, 0.025, 100.0, 2.2)
    err = ete.liner_neglect_error_fraction(r)
    assert err > 0.005
    assert abs(err - 0.0053) < 0.001


def test_is_liner_negligible_threshold_100():
    assert ete.is_liner_negligible(200.0, 100.0) is True
    assert ete.is_liner_negligible(50.0, 100.0) is False
    assert ete.is_liner_negligible(100.0, 100.0) is True


# ── cu_thickness_from_resistance: Park 예시 역산 + naive 근사와의 방향성 ─────

def test_cu_thickness_from_resistance_reproduces_park_example():
    # R을 T_M=0.40 um이 나오도록 역산 후, 순방향 함수가 같은 T_M을 재현하는지 확인
    R_ohm = (2.0 * 1e-2) * 1000.0 / ((0.40 - 0.025) * (0.35 - 2 * 0.025))
    T_M = ete.cu_thickness_from_resistance(R_ohm, 1000.0, 0.35, 0.025, rho_Cu_uohm_cm=2.0)
    assert abs(T_M - 0.40) < 1e-6


def test_cu_thickness_from_resistance_liner_correction_exceeds_naive_approximation():
    R_ohm = 177.8
    T_lined = ete.cu_thickness_from_resistance(R_ohm, 1000.0, 0.35, 0.025, rho_Cu_uohm_cm=2.0)
    T_naive = (2.0 * 1e-2) * 1000.0 / (R_ohm * 0.35)
    assert T_lined > T_naive


def test_cu_thickness_from_resistance_sanity_across_inputs():
    for R_ohm, L_um, W_um, T_L_um in [(100.0, 500.0, 0.5, 0.03), (300.0, 2000.0, 0.8, 0.05)]:
        T_lined = ete.cu_thickness_from_resistance(R_ohm, L_um, W_um, T_L_um, rho_Cu_uohm_cm=2.0)
        T_naive = (2.0 * 1e-2) * L_um / (R_ohm * W_um)
        assert T_lined > T_naive
        assert T_lined > 0


# ── (D) Chang et al. 2004 표 I vs dishing-radius 모델(R_dish=40um, t=0.5um) ──

def test_dishing_delta_r_fraction_5um_matches_9_39_within_30pct():
    d5 = ete.dishing_delta_R_fraction(5.0)
    assert abs(d5 - 9.39) / 9.39 < 0.30
    assert 10.0 < d5 < 13.0


def test_dishing_delta_r_fraction_table_i_w_ge_2um_within_30pct():
    tableI = [(5, 9.39), (4, 6.67), (3, 4.74), (2, 1.56)]
    for w, meas in tableI:
        model = ete.dishing_delta_R_fraction(w)
        assert abs(model - meas) / meas < 0.30


def test_dishing_delta_r_fraction_0_4um_below_model_range():
    # w=0.4 um은 문헌 1.14%이나 모델은 dishing만 반영해 훨씬 작음(모델 범위 밖임을 기록)
    d04 = ete.dishing_delta_R_fraction(0.4)
    assert d04 < 0.2


def test_dishing_delta_r_fraction_monotonic_in_width():
    widths = [0.4, 0.8, 1.2, 1.6, 2.0, 3.0, 4.0, 5.0]
    values = [ete.dishing_delta_R_fraction(w) for w in widths]
    assert all(values[i] < values[i + 1] for i in range(len(values) - 1))
