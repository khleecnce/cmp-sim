"""friction_cof_epd.py 회귀 테스트.

지식 근거: knowledge/physics/friction-cof-monitoring-endpoint-detection.md
  §2 마찰신호 사슬, §4 소신호·검출지연 트레이드오프, §6 python verify 블록.

구성:
  1. 정의 항등 (노트 §6 (1)(2)) — 같은 입력으로 같은 값 재현.
  2. Li 2017 산술 (노트 §6 (3)(4)) — dP=1630 W, contrast 5.4%, delay 4.94 s, over 18.8 nm.
     노트에서 이미 검증된 값을 코드로 이전하는 것이지 새 계산이 아니다.
  3. 합성신호 종단 (노트에 없던 새 검증) — step+가우시안 잡음 합성신호에 이동평균+계단검출을
     걸어, 검출 인덱스가 이론 지연 detection_delay_s(60, 12.15)에 해당하는 샘플 수(=60)만큼
     전이점 뒤에 나타나는지 정량 assert. 이게 없으면 "수식만 베낀 것"이다.
  4. 신호처리 기본 성질·오검출 방지·입력 검증.

⚠ 합성신호는 실측 재현이 아니다(알고리즘 검증용). 노트 §8의 미검증 항목(K_t 절대값,
재료별 COF 절대표, 전이방향)은 여기서도 검증하지 않는다.
"""
import math

import numpy as np
import pytest

import friction_cof_epd as epd

# ---------------------------------------------------------------------------
# 공통 상수 (노트 §6 (1)(2) 입력 그대로)
# ---------------------------------------------------------------------------
PSI = 6894.76
P_PA = 3 * PSI                 # W CMP 전형 3 psi
A_M2 = math.pi * 0.15 ** 2     # 300 mm 웨이퍼
V_MPS = 0.70                   # 상대 미끄럼속도 (Lai 2001 thesis)
MU = 0.4                       # W CMP boundary COF 대표값(0.1~0.7) — 노트 §8: 가정값
R_C = 0.20                     # 웨이퍼중심 반경 [m] — 장비상수, 노트 §8: 절대값 미검증

# Li 2017 (PMC6190379) — 노트 §6 (3)(4) 값 그대로
LI_BASE, LI_AFTER = 30300.0, 28670.0
LI_RATE_HZ, LI_HALF = 12.15, 60
LI_RR = 229.0


# ===========================================================================
# 1. 정의 항등 (노트 §6 (1)(2))
# ===========================================================================

def test_cof_definition_identity():
    """§6 (1): F_n=P·A≈1462 N, F_s=μ·F_n≈585 N, COF=F_s/F_n=μ 정확히 성립."""
    F_n = epd.normal_force(P_PA, A_M2)
    F_s = epd.shear_force(MU, P_PA, A_M2)
    assert F_n == pytest.approx(1462, abs=1)          # 노트 §6: F_n≈1462 N
    assert F_s == pytest.approx(585, abs=1)           # 노트 §6: F_s≈585 N
    assert epd.cof_from_forces(F_s, F_n) == pytest.approx(MU, abs=1e-12)
    assert 500 < F_n < 2000                           # 노트 §6 (1) 범위 assert 그대로


def test_motor_power_equals_shear_times_velocity_and_friction_heat():
    """§6 (2): τ·ω == F_s·V == μPVA (=Q_f, ≈409 W). 기하 항등 + 마찰발열 항등."""
    F_s = epd.shear_force(MU, P_PA, A_M2)
    omega = V_MPS / R_C
    tau = epd.platen_torque(F_s, R_C)
    P_fric = epd.motor_power_friction(tau, omega)
    Q_f = MU * P_PA * V_MPS * A_M2
    assert tau == pytest.approx(117.0, abs=0.1)       # 노트 §6 출력: tau=117.0 Nm
    assert P_fric == pytest.approx(F_s * V_MPS, rel=1e-12)
    assert P_fric == pytest.approx(Q_f, rel=1e-12)
    assert P_fric == pytest.approx(409, abs=1)        # 노트 §6: 409 W (White 2003 200~300 W 동오더)
    assert 100 < Q_f < 1000


def test_motor_power_matches_frictional_heating_module():
    """S17 frictional_heating_arrhenius.friction_power와 같은 물리량임을 교차 확인 (노트 §2)."""
    fha = pytest.importorskip("frictional_heating_arrhenius")
    F_s = epd.shear_force(MU, P_PA, A_M2)
    P_fric = epd.motor_power_friction(epd.platen_torque(F_s, R_C), V_MPS / R_C)
    Q_f = fha.friction_power(fha.friction_heat_flux(MU, P_PA, V_MPS), A_M2)
    assert P_fric == pytest.approx(Q_f, rel=1e-12)


def test_motor_current_is_proportional_only():
    """I=τ/K_t 비례식만 제공 (K_t 절대값 미검증 — 노트 §8). τ 2배 → I 2배, K_t≤0 거부."""
    Kt = 0.5                                          # 노트 §6 (2)에서 쓴 임의 상수
    tau = 117.0
    assert epd.motor_current(tau, Kt) == pytest.approx(tau / Kt)
    assert epd.motor_current(2 * tau, Kt) == pytest.approx(2 * epd.motor_current(tau, Kt))
    with pytest.raises(ValueError):
        epd.motor_current(tau, 0.0)


def test_cof_zero_normal_force_raises():
    with pytest.raises(ValueError):
        epd.cof_from_forces(1.0, 0.0)


# ===========================================================================
# 2. Li 2017 산술 재현 (노트 §6 (3)(4))
# ===========================================================================

def test_li2017_step_contrast():
    """§6 (3): 30,300→28,670 W → dP=1630 W, contrast=5.4% (소신호)."""
    dP, contrast = epd.step_contrast(LI_BASE, LI_AFTER)
    assert dP == pytest.approx(1630.0, abs=1e-9)
    assert contrast == pytest.approx(0.054, abs=0.0005)   # 1630/30300 = 0.0538
    assert 0.03 < contrast < 0.08                          # 노트 §6 (3) 범위 assert 그대로


def test_li2017_delay_and_over_polish():
    """§6 (4): N=60, R=12.15 Hz → 지연 4.94 s(<5 s); RR=229 nm/min → 과연마 18.8 nm(<20 nm)."""
    delay = epd.detection_delay_s(LI_HALF, LI_RATE_HZ)
    over = epd.over_polish_nm(delay, LI_RR)
    assert delay == pytest.approx(60 / 12.15, rel=1e-12)
    assert delay == pytest.approx(4.94, abs=0.005)
    assert over == pytest.approx(18.8, abs=0.05)
    assert delay < 5.0 and over < 20.0                     # 노트 §6 (4) assert 그대로


def test_li2017_reference_table_consistent_with_note():
    """모듈 참조표 LI2017이 노트 §6 값과 일치(지어낸 값 없음)."""
    assert epd.LI2017["P_base_w"] == LI_BASE
    assert epd.LI2017["P_after_w"] == LI_AFTER
    assert epd.LI2017["sample_rate_hz"] == LI_RATE_HZ
    assert epd.LI2017["half_span"] == LI_HALF
    assert epd.LI2017["rr_teos_nm_per_min"] == LI_RR


def test_headley2019_correlation_ordering():
    """§6 (5): PMC vs 전단력 r=0.955 > PMC vs COF r=0.758 — 모터전류는 COF계가 아니라 전단력계."""
    h = epd.HEADLEY2019
    assert h["r_pmc_sf"] > h["r_pmc_cof"]
    assert h["R2_pmc_sf"] > h["R2_pmc_cof"]
    assert h["R2_pmc_sf"] == pytest.approx(h["r_pmc_sf"] ** 2, abs=0.02)   # 0.912 vs 0.916


# ===========================================================================
# 3. 합성신호 종단 검증 (핵심 — 노트에 없던 새 검증)
# ===========================================================================
# 설계: baseline 30,300 W → 28,670 W 계단(Li 2017 값), 잡음 σ=50 W, T=600에서 전이,
#       총 1200 샘플(≈99 s @ 12.15 Hz). 121점 이동평균(N=60), threshold = contrast/2 ≈ 0.027
#       (평활 후 계단의 50% 교차점을 잡기 위함 — 모듈 docstring 지침).
# 허용오차 ±3 샘플 근거: 평활 후 잡음 σ_MA = 50/√121 ≈ 4.5 W, 121점 창에서 계단 기울기
#       ≈ 1630/121 ≈ 13.5 W/샘플 → 잡음에 의한 교차점 요동 ≈ 0.3 샘플. min_persist=5는
#       단발 잡음 스파이크 오검출 방지용이며 반환 인덱스는 이동시키지 않는다.
N_SAMPLES, T_IDX, NOISE_W, SEED = 1200, 600, 50.0, 42
BASELINE_WIN = 200
THRESHOLD = 0.027
TOL_SAMPLES = 3


@pytest.fixture(scope="module")
def li_synthetic():
    return epd.synthetic_transition_signal(LI_BASE, LI_AFTER, N_SAMPLES, LI_RATE_HZ,
                                           T_IDX, NOISE_W, seed=SEED)


def test_synthetic_signal_reproducible_and_shaped(li_synthetic):
    """seed 고정 → 동일 신호. 전이 전/후 평균이 각각 baseline/after에 잡음 σ/√n 이내."""
    again = epd.synthetic_transition_signal(LI_BASE, LI_AFTER, N_SAMPLES, LI_RATE_HZ,
                                            T_IDX, NOISE_W, seed=SEED)
    assert np.array_equal(li_synthetic, again)
    assert li_synthetic.shape == (N_SAMPLES,)
    se = NOISE_W / math.sqrt(T_IDX)                    # ≈2.0 W
    assert li_synthetic[:T_IDX].mean() == pytest.approx(LI_BASE, abs=5 * se)
    assert li_synthetic[T_IDX:].mean() == pytest.approx(LI_AFTER, abs=5 * se)


def test_end_to_end_causal_detection_reproduces_theoretical_delay(li_synthetic):
    """핵심: causal 121점 MA + 계단검출 → 검출 idx = T + N (±3 샘플), 즉 지연 ≈ 4.94 s 재현."""
    sm = epd.moving_average(li_synthetic, LI_HALF, mode="causal")
    idx = epd.detect_step_transition(sm, BASELINE_WIN, THRESHOLD, min_persist=5)
    assert idx is not None
    delay_samples = epd.detection_delay_s(LI_HALF, LI_RATE_HZ) * LI_RATE_HZ   # = 60 (정확히)
    assert delay_samples == pytest.approx(LI_HALF, rel=1e-12)
    expected = T_IDX + round(delay_samples)
    assert abs(idx - expected) <= TOL_SAMPLES
    # 시간 단위로도: 측정 지연 vs 이론 4.94 s
    measured_delay_s = (idx - T_IDX) / LI_RATE_HZ
    assert measured_delay_s == pytest.approx(epd.detection_delay_s(LI_HALF, LI_RATE_HZ),
                                             abs=TOL_SAMPLES / LI_RATE_HZ)


def test_end_to_end_centered_detection_offline_vs_realtime(li_synthetic):
    """centered MA: 오프라인 검출 idx ≈ T (±3), 실시간 판정가능 idx = idx + N ≈ T + N."""
    res = epd.detect_endpoint(li_synthetic, LI_RATE_HZ, LI_HALF, BASELINE_WIN, THRESHOLD,
                              mode="centered", min_persist=5, removal_rate_nm_per_min=LI_RR)
    assert res.detected_idx is not None
    assert abs(res.detected_idx - T_IDX) <= TOL_SAMPLES
    assert abs(res.realtime_idx - (T_IDX + LI_HALF)) <= TOL_SAMPLES
    assert res.theoretical_delay_s == pytest.approx(4.94, abs=0.005)
    assert res.over_polish_nm == pytest.approx(18.8, abs=0.05)
    assert "18.8 nm" in res.describe()


def test_detect_endpoint_causal_wrapper_matches_manual_chain(li_synthetic):
    """detect_endpoint(causal)는 moving_average+detect_step_transition 수동 사슬과 동일."""
    res = epd.detect_endpoint(li_synthetic, LI_RATE_HZ, LI_HALF, BASELINE_WIN, THRESHOLD,
                              mode="causal", min_persist=5)
    sm = epd.moving_average(li_synthetic, LI_HALF, mode="causal")
    manual = epd.detect_step_transition(sm, BASELINE_WIN, THRESHOLD, min_persist=5)
    assert res.detected_idx == manual
    assert res.realtime_idx == manual                  # causal은 출력 자체가 실시간
    assert res.over_polish_nm is None                  # RR 미지정


@pytest.mark.parametrize("seed", list(range(10)))
def test_end_to_end_delay_stable_across_seeds(seed):
    """seed=42 한 번의 요행이 아님을 확인: 10개 seed에서 검출 idx = T+N ±3 (실측 ±1)."""
    sig = epd.synthetic_transition_signal(LI_BASE, LI_AFTER, N_SAMPLES, LI_RATE_HZ,
                                          T_IDX, NOISE_W, seed=seed)
    res = epd.detect_endpoint(sig, LI_RATE_HZ, LI_HALF, BASELINE_WIN, THRESHOLD,
                              mode="causal", min_persist=5)
    assert res.detected_idx is not None
    assert abs(res.detected_idx - (T_IDX + LI_HALF)) <= TOL_SAMPLES


def test_over_polish_from_measured_delay_matches_li2017(li_synthetic):
    """합성 검출지연(샘플)을 초로 환산해 과연마를 계산하면 Li 2017의 18.8 nm(<20 nm)와 일치."""
    res = epd.detect_endpoint(li_synthetic, LI_RATE_HZ, LI_HALF, BASELINE_WIN, THRESHOLD,
                              mode="causal", min_persist=5)
    measured_delay_s = (res.detected_idx - T_IDX) / LI_RATE_HZ
    over = epd.over_polish_nm(measured_delay_s, LI_RR)
    # ±3 샘플 → ±0.25 s → ±0.94 nm
    assert over == pytest.approx(18.8, abs=TOL_SAMPLES / LI_RATE_HZ * LI_RR / 60 + 0.05)
    assert over < 20.0


def test_no_step_no_detection():
    """계단 없는 잡음신호(σ=50 W, 같은 seed) → None. 오검출 없음."""
    flat = epd.synthetic_transition_signal(LI_BASE, LI_BASE, N_SAMPLES, LI_RATE_HZ,
                                           T_IDX, NOISE_W, seed=SEED)
    res = epd.detect_endpoint(flat, LI_RATE_HZ, LI_HALF, BASELINE_WIN, THRESHOLD, mode="causal")
    assert res.detected_idx is None and res.realtime_idx is None


def test_threshold_above_contrast_misses_step(li_synthetic):
    """threshold_fraction(8%) > contrast(5.4%)면 계단을 못 잡는다 — 소신호 설계 지침의 역방향 확인."""
    sm = epd.moving_average(li_synthetic, LI_HALF, mode="causal")
    assert epd.detect_step_transition(sm, BASELINE_WIN, 0.08) is None
    assert epd.detect_step_transition(sm, BASELINE_WIN, THRESHOLD) is not None


def test_direction_filter(li_synthetic):
    """Li 2017 계단은 하강: direction='down'은 잡고 'up'은 None (방향 대소는 §8 미검증이라 기본 any)."""
    sm = epd.moving_average(li_synthetic, LI_HALF, mode="causal")
    assert epd.detect_step_transition(sm, BASELINE_WIN, THRESHOLD, direction="down") is not None
    assert epd.detect_step_transition(sm, BASELINE_WIN, THRESHOLD, direction="up") is None


# ===========================================================================
# 4. 신호처리 기본 성질 · 입력 검증
# ===========================================================================

def test_moving_average_basic_properties():
    x = np.arange(20, dtype=float)
    assert np.array_equal(epd.moving_average(x, 0), x)                     # N=0 → 항등
    c = epd.moving_average(x, 2, mode="centered")
    # 내부점: 5점 중심평균은 선형신호에서 자기 자신
    assert c[2:-2] == pytest.approx(x[2:-2])
    # 가장자리: 부분창 평균 (zero-padding 편향 없음) — c[0]=mean(0,1,2)=1
    assert c[0] == pytest.approx(1.0)
    k = epd.moving_average(x, 2, mode="causal")
    # causal 5점: 내부점은 x[i]-2 (과거 5점 평균)
    assert k[4:] == pytest.approx(x[4:] - 2.0)
    const = np.full(50, 7.5)
    assert epd.moving_average(const, 10) == pytest.approx(const)
    with pytest.raises(ValueError):
        epd.moving_average(x, -1)
    with pytest.raises(ValueError):
        epd.moving_average(x, 2, mode="bogus")


def test_moving_average_causal_step_crosses_half_at_plus_half_span():
    """잡음 없는 이상 계단: causal (2N+1)점 MA는 계단 위치 T에서 정확히 N 샘플 뒤에 50% 교차 →
    detection_delay_s = N/R 의 이산 근거."""
    N, T = 60, 600
    clean = epd.synthetic_transition_signal(LI_BASE, LI_AFTER, 1200, LI_RATE_HZ, T, 0.0, seed=0)
    sm = epd.moving_average(clean, N, mode="causal")
    half = (LI_BASE + LI_AFTER) / 2
    idx_half = int(np.flatnonzero(sm <= half)[0])
    assert idx_half == T + N


def test_detect_step_transition_input_validation():
    sig = np.ones(10)
    with pytest.raises(ValueError):
        epd.detect_step_transition(sig, 0, 0.05)
    with pytest.raises(ValueError):
        epd.detect_step_transition(sig, 10, 0.05)
    with pytest.raises(ValueError):
        epd.detect_step_transition(sig, 3, 0.0)
    with pytest.raises(ValueError):
        epd.detect_step_transition(sig, 3, 0.05, min_persist=0)
    with pytest.raises(ValueError):
        epd.detect_step_transition(np.zeros(10), 3, 0.05)    # baseline 0


def test_synthetic_signal_input_validation():
    with pytest.raises(ValueError):
        epd.synthetic_transition_signal(1.0, 0.5, 0, 10.0, 0, 0.1)
    with pytest.raises(ValueError):
        epd.synthetic_transition_signal(1.0, 0.5, 10, 10.0, 11, 0.1)
    with pytest.raises(ValueError):
        epd.synthetic_transition_signal(1.0, 0.5, 10, 0.0, 5, 0.1)
    with pytest.raises(ValueError):
        epd.synthetic_transition_signal(1.0, 0.5, 10, 10.0, 5, -0.1)
    with pytest.raises(ValueError):
        epd.detection_delay_s(60, 0.0)
