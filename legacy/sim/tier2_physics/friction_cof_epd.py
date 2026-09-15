"""마찰기반 종점검출(friction-based EPD) 신호모델 — 전단력→토크→모터동력 사슬 + 계단검출.

지식 근거: knowledge/physics/friction-cof-monitoring-endpoint-detection.md
  §2 (COF 정의·마찰신호 사슬), §3 (모터전류/전단력 EPD 원리, Li 2017 계단),
  §4 (소신호·검출지연 트레이드오프), §6 (python verify 블록 문헌 대조값)
구현 요청: tribologist Lv3-1 (BACKLOG 수신함 → S20)

계약 (엔진과의 경계):
  이 모듈은 순수 함수 라이브러리다. engine.py / models.py에 등록하지 않는다.
  사유: Recipe는 단발 런 스냅샷이라 시계열(모터전력·토크 신호)을 담을 스키마가 없다
  (docs/ARCHITECTURE.md §4 스키마 부채에 기록됨). S17 frictional_heating_arrhenius,
  S19 particle_chemomechanical_synergy와 같은 지위다. 여기서는 "신호 → 종점검출"
  알고리즘 자체와 그 지연·과연마 산술만 구현·검증한다.

미검증 사항 (노트 §6·§8 그대로, 지어내지 않음):
  - 모터 토크상수 K_t, 웨이퍼중심 반경 r_c, 플래튼/캐리어 토크분배, baseline
    (베어링·리테이너링·컨디셔너) 크기는 모두 **장비 종속·절대값 미검증**.
    motor_current()는 비례식 I=τ/K_t만 제공하고 절대전류를 예측하지 않는다.
  - 재료별(Cu/Ta/oxide-패드) COF 절대값 표는 1차 미확보. μ=0.4는 W CMP boundary
    대표값(0.1~0.7 범위) **가정**이며 전이방향(상승/하강)의 정량 대소는 미검증.
    그래서 detect_step_transition()의 기본 방향은 "any"(상승/하강 무관)이다.
  - Li 2017 값(30,300→28,670 W, 12.15 Hz, N=60, 229 nm/min)은 해당 툴/스택
    (Cu/Ti/TEOS)의 실측이며, 소신호(~5%)·지연-과연마 구조만 일반화 가능.
  - synthetic_transition_signal()은 **실측 재현이 아니다** — 알고리즘 검증용 합성신호.

함수:
  마찰신호 사슬 (§2):
    shear_force(mu, P, A)             -> F_s = mu*P*A [N]
    normal_force(P, A)                -> F_n = P*A [N]
    cof_from_forces(F_s, F_n)         -> mu = F_s/F_n
    platen_torque(F_s, r_c)           -> tau = F_s*r_c [N m]
    motor_power_friction(tau, omega)  -> P = tau*omega [W]  (= F_s*V = mu*P*V*A = Q_f)
    motor_current(tau, Kt)            -> I = tau/K_t [A]  (K_t 절대값 미검증)
  종점검출 신호처리 (§3, §4):
    step_contrast(baseline, after)                       -> (dP, dP/baseline)
    moving_average(signal, half_span, mode)              -> 평활 신호
    detect_step_transition(signal, baseline_window, threshold_fraction, ...) -> idx|None
    detection_delay_s(half_span, sample_rate_hz)         -> half_span / R [s]
    over_polish_nm(delay_s, removal_rate_nm_per_min)     -> delay*RR/60 [nm]
    detect_endpoint(...)                                 -> EpdResult (사슬 묶음)
  합성 신호 (검증용):
    synthetic_transition_signal(...)                     -> step + 가우시안 노이즈
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import numpy as np


# ---------------------------------------------------------------------------
# 1. 마찰신호 사슬 (노트 §2)
# ---------------------------------------------------------------------------

def normal_force(pressure_pa: float, area_m2: float) -> float:
    """수직력(down force) F_n = P * A [N]. 근거: 노트 §2."""
    return pressure_pa * area_m2


def shear_force(mu: float, pressure_pa: float, area_m2: float) -> float:
    """전단력(마찰/drag force) F_s = mu * P * A [N] (Amontons). 근거: 노트 §2."""
    return mu * normal_force(pressure_pa, area_m2)


def cof_from_forces(shear_force_n: float, normal_force_n: float) -> float:
    """마찰계수 COF = F_shear / F_normal (힘센서법 EPD의 산출식). 근거: 노트 §2·§3."""
    if normal_force_n == 0:
        raise ValueError("수직력이 0 — COF 정의 불가")
    return shear_force_n / normal_force_n


def platen_torque(shear_force_n: float, r_c_m: float) -> float:
    """웨이퍼 마찰이 플래튼에 거는 저항 토크 tau ≈ F_shear * r_c [N m].

    r_c = 웨이퍼 중심의 플래튼축 기준 반경. 근거: 노트 §2.
    """
    return shear_force_n * r_c_m


def motor_power_friction(torque_nm: float, omega_rad_s: float) -> float:
    """모터 마찰동력 P = tau * omega [W].

    항등(노트 §2): tau*omega = F_s*r_c*(V/r_c) = F_s*V = mu*P*V*A = q*A = Q_f.
    즉 모터가 마찰을 이기며 쓰는 동력 == 계면 마찰발열
    (frictional_heating_arrhenius.friction_power와 같은 물리량의 두 얼굴).
    """
    return torque_nm * omega_rad_s


def motor_current(torque_nm: float, torque_constant_nm_per_a: float) -> float:
    """모터전류 I = tau / K_t [A] (DC/BLDC 비례식).

    ⚠ K_t(토크상수)는 장비상수로 절대값 미검증(노트 §8). 비례성만 제공한다.
    """
    if torque_constant_nm_per_a <= 0:
        raise ValueError("토크상수 K_t는 양수여야 한다")
    return torque_nm / torque_constant_nm_per_a


# ---------------------------------------------------------------------------
# 2. 종점검출 신호처리 (노트 §3, §4)
# ---------------------------------------------------------------------------

def step_contrast(baseline: float, after: float) -> tuple[float, float]:
    """계단 크기 dP = baseline - after 와 소신호 대비 contrast = dP / baseline.

    Li 2017: 30,300 → 28,670 W → dP=1630 W, contrast≈5.4% (노트 §4·§6 (3)).
    """
    if baseline == 0:
        raise ValueError("baseline이 0 — contrast 정의 불가")
    dP = baseline - after
    return dP, dP / baseline


def moving_average(signal: np.ndarray, half_span: int, mode: str = "centered") -> np.ndarray:
    """이동평균. half_span=N이면 창 길이 window = 2N+1 (Li 2017: N=60 → 121점).

    mode="centered": 출력[i] = mean(signal[i-N : i+N+1]). 오프라인(사후) 평활.
        ⚠ 실시간에서는 출력[i]가 샘플 i+N이 도착해야 계산 가능하므로
        실질 지연 = N 샘플 = detection_delay_s(N, R) (노트 §4).
    mode="causal": 출력[i] = mean(signal[i-2N : i+1]). 과거 2N+1점만 사용하는
        실시간 평활. 계단의 50% 교차점이 계단 위치에서 N 샘플 뒤에 나타나므로
        centered의 실시간 지연과 동일한 N 샘플 지연이 출력 자체에 드러난다.

    가장자리: 창을 신호 범위로 잘라 부분창 평균(zero-padding 편향 없음).
    """
    x = np.asarray(signal, dtype=float)
    n = x.size
    if half_span < 0:
        raise ValueError("half_span은 0 이상이어야 한다")
    if n == 0:
        return x.copy()
    if half_span == 0:
        return x.copy()
    csum = np.concatenate(([0.0], np.cumsum(x)))
    idx = np.arange(n)
    if mode == "centered":
        lo = np.clip(idx - half_span, 0, n)
        hi = np.clip(idx + half_span + 1, 0, n)
    elif mode == "causal":
        window = 2 * half_span + 1
        lo = np.clip(idx - window + 1, 0, n)
        hi = idx + 1
    else:
        raise ValueError(f"mode는 'centered' 또는 'causal': {mode!r}")
    return (csum[hi] - csum[lo]) / (hi - lo)


def detect_step_transition(signal: np.ndarray, baseline_window: int,
                           threshold_fraction: float, min_persist: int = 1,
                           direction: str = "any") -> Optional[int]:
    """baseline 대비 threshold_fraction 이상 변화가 처음 **지속**되는 인덱스.

    baseline = mean(signal[:baseline_window]) (전이 전 구간이어야 한다 — 호출자 책임).
    threshold = threshold_fraction * |baseline|.
    탐색은 baseline_window 이후부터. 편차가 threshold를 넘는 상태가 min_persist 샘플
    연속으로 유지되는 첫 구간의 **시작 인덱스**를 반환(확인용 min_persist는 실시간
    지연을 min_persist-1 샘플 추가하지만 반환 인덱스는 이동시키지 않는다).
    없으면 None.

    direction: "any"(|편차|, 기본) | "down"(감소만) | "up"(증가만).
      기본이 "any"인 이유: 재료전이의 μ 변화 방향(상승/하강)은 슬러리 화학에 따라
      뒤집힐 수 있어 노트 §8에서 미검증으로 남겨두었기 때문.

    소신호 설계 지침(노트 §4): Li 2017 계단은 baseline의 ~5.4%. 이동평균 후 계단의
    50% 교차를 잡으려면 threshold_fraction ≈ contrast/2 (≈0.027)로 둔다.
    """
    x = np.asarray(signal, dtype=float)
    n = x.size
    if not (0 < baseline_window < n):
        raise ValueError("baseline_window는 0 < w < len(signal)이어야 한다")
    if threshold_fraction <= 0:
        raise ValueError("threshold_fraction은 양수여야 한다")
    if min_persist < 1:
        raise ValueError("min_persist는 1 이상이어야 한다")
    base = float(x[:baseline_window].mean())
    if base == 0:
        raise ValueError("baseline 평균이 0 — 상대 임계값 정의 불가")
    thr = threshold_fraction * abs(base)
    dev = x - base
    if direction == "down":
        flag = dev <= -thr
    elif direction == "up":
        flag = dev >= thr
    elif direction == "any":
        flag = np.abs(dev) >= thr
    else:
        raise ValueError(f"direction은 'any'|'down'|'up': {direction!r}")
    flag[:baseline_window] = False
    if min_persist == 1:
        hits = np.flatnonzero(flag)
        return int(hits[0]) if hits.size else None
    runs = np.convolve(flag.astype(int), np.ones(min_persist, dtype=int), mode="valid")
    hits = np.flatnonzero(runs >= min_persist)
    return int(hits[0]) if hits.size else None


def detection_delay_s(half_span: int, sample_rate_hz: float) -> float:
    """이동평균 검출지연 T = N / R [s]. Li 2017: N=60, R=12.15 Hz → 4.94 s (<5 s). 노트 §4·§6 (4)."""
    if sample_rate_hz <= 0:
        raise ValueError("샘플링 주파수는 양수여야 한다")
    return half_span / sample_rate_hz


def over_polish_nm(delay_s: float, removal_rate_nm_per_min: float) -> float:
    """검출지연 동안의 과연마 = delay * RR / 60 [nm]. Li 2017: 4.94 s × 229 nm/min → 18.8 nm (<20 nm)."""
    return delay_s * removal_rate_nm_per_min / 60.0


@dataclass
class EpdResult:
    """평활 → 계단검출 → 지연·과연마 산술을 한 번에 묶은 결과."""
    detected_idx: Optional[int]        # 평활신호에서 임계 교차가 처음 지속되는 인덱스
    realtime_idx: Optional[int]        # 실시간에 그 판정이 가능한 샘플 인덱스(centered면 +half_span)
    half_span: int
    sample_rate_hz: float
    theoretical_delay_s: float         # N/R
    over_polish_nm: Optional[float]    # 이론 지연 × RR (RR 미지정이면 None)

    def describe(self) -> str:
        return (f"detected_idx={self.detected_idx}, realtime_idx={self.realtime_idx}, "
                f"N={self.half_span}, R={self.sample_rate_hz} Hz, "
                f"delay={self.theoretical_delay_s:.2f} s, over-polish="
                f"{'n/a' if self.over_polish_nm is None else f'{self.over_polish_nm:.1f} nm'}")


def detect_endpoint(signal: np.ndarray, sample_rate_hz: float, half_span: int,
                    baseline_window: int, threshold_fraction: float,
                    mode: str = "centered", min_persist: int = 1, direction: str = "any",
                    removal_rate_nm_per_min: Optional[float] = None) -> EpdResult:
    """이동평균 + 계단검출 + 지연/과연마 산술 사슬.

    realtime_idx: centered 평활은 출력[i]가 샘플 i+N 도착 후 계산되므로 detected_idx+N,
    causal 평활은 출력 자체가 실시간이므로 detected_idx 그대로.
    """
    sm = moving_average(signal, half_span, mode=mode)
    idx = detect_step_transition(sm, baseline_window, threshold_fraction,
                                 min_persist=min_persist, direction=direction)
    rt = None if idx is None else (idx + half_span if mode == "centered" else idx)
    delay = detection_delay_s(half_span, sample_rate_hz)
    over = None if removal_rate_nm_per_min is None else over_polish_nm(delay, removal_rate_nm_per_min)
    return EpdResult(detected_idx=idx, realtime_idx=rt, half_span=half_span,
                     sample_rate_hz=sample_rate_hz, theoretical_delay_s=delay,
                     over_polish_nm=over)


# ---------------------------------------------------------------------------
# 3. 합성 신호 생성기 (검증용)
# ---------------------------------------------------------------------------

def synthetic_transition_signal(baseline_w: float, after_w: float, n_samples: int,
                                sample_rate_hz: float, transition_idx: int,
                                noise_std_w: float, seed: Optional[int] = 0) -> np.ndarray:
    """계단(step) + 가우시안 백색잡음 합성 모터전력 신호.

    ⚠ **실측 재현이 아니다.** Li 2017의 실제 신호는 ~30 s에 걸친 완만한 전이 + 유동·거칠기
    요동이며, 여기서는 알고리즘(이동평균·계단검출·지연 산술) 검증만을 위해 이상적 계단과
    독립 가우시안 잡음을 쓴다. sample_rate_hz는 시간축 해석(샘플↔초)용으로만 받는다.

    signal[i] = baseline_w (i < transition_idx) / after_w (i >= transition_idx) + N(0, noise_std_w²)
    """
    if n_samples <= 0:
        raise ValueError("n_samples는 양수여야 한다")
    if not (0 <= transition_idx <= n_samples):
        raise ValueError("transition_idx는 [0, n_samples] 범위여야 한다")
    if sample_rate_hz <= 0:
        raise ValueError("샘플링 주파수는 양수여야 한다")
    if noise_std_w < 0:
        raise ValueError("noise_std_w는 0 이상이어야 한다")
    clean = np.full(n_samples, float(baseline_w))
    clean[transition_idx:] = float(after_w)
    rng = np.random.default_rng(seed)
    return clean + rng.normal(0.0, noise_std_w, n_samples)


# ---------------------------------------------------------------------------
# 문헌 참조값 (노트 §6 그대로 — 재현 검증용 참조표, 팩/엔진이 우회하지 않도록 여기만 둔다)
# ---------------------------------------------------------------------------
LI2017 = {
    # Li, Lu, Luo, Micromachines 8(6) 177, 2017, doi 10.3390/mi8060177, PMC6190379
    "P_base_w": 30300.0,
    "P_after_w": 28670.0,
    "sample_rate_hz": 12.15,
    "half_span": 60,            # 121점 이동평균
    "rr_teos_nm_per_min": 229.0,  # TEOS 제거율 (과연마 산정 기준)
}
HEADLEY2019 = {
    # Headley et al., ECS JSST 8(10) P634, 2019, doi 10.1149/2.0251910jss — 특정 툴/슬러리 케이스평균
    "r_pmc_sf": 0.955, "R2_pmc_sf": 0.916,
    "r_pmc_cof": 0.758, "R2_pmc_cof": 0.608,
}


def _self_test() -> bool:
    import math
    results = []

    # --- Test 1: 노트 §6 (1) COF 정의 항등 ---
    psi = 6894.76
    P = 3 * psi
    A = math.pi * 0.15 ** 2
    V = 0.70
    mu = 0.4
    F_n = normal_force(P, A)
    F_s = shear_force(mu, P, A)
    cof = cof_from_forces(F_s, F_n)
    ok1 = abs(cof - mu) < 1e-9 and 500 < F_n < 2000
    results.append(("§6(1) COF=F_s/F_n=mu, F_n 500~2000 N", ok1,
                    f"F_n={F_n:.0f} N, F_s={F_s:.0f} N, COF={cof:.2f}"))

    # --- Test 2: 노트 §6 (2) tau*omega == F_s*V == mu*P*V*A (=Q_f, 409 W) ---
    r_c = 0.20
    omega = V / r_c
    tau = platen_torque(F_s, r_c)
    P_fric = motor_power_friction(tau, omega)
    Q_f = mu * P * V * A
    ok2 = abs(P_fric - F_s * V) < 1e-6 and abs(P_fric - Q_f) < 1e-6 and 100 < Q_f < 1000
    results.append(("§6(2) tau*omega == F_s*V == mu*P*V*A (수백 W)", ok2,
                    f"tau={tau:.1f} Nm, P_fric={P_fric:.0f} W, Q_f={Q_f:.0f} W"))

    # --- Test 3: 노트 §6 (3) Li 2017 dP=1630 W, contrast≈5.4% ---
    dP, c = step_contrast(LI2017["P_base_w"], LI2017["P_after_w"])
    ok3 = abs(dP - 1630) < 1 and 0.03 < c < 0.08
    results.append(("§6(3) Li2017 dP=1630 W, contrast~5.4%", ok3, f"dP={dP:.0f} W, contrast={c*100:.1f}%"))

    # --- Test 4: 노트 §6 (4) delay=4.94 s(<5), over-polish=18.8 nm(<20) ---
    delay = detection_delay_s(LI2017["half_span"], LI2017["sample_rate_hz"])
    over = over_polish_nm(delay, LI2017["rr_teos_nm_per_min"])
    ok4 = delay < 5.0 and over < 20.0 and abs(delay - 4.94) < 0.01 and abs(over - 18.8) < 0.1
    results.append(("§6(4) Li2017 delay=4.94 s(<5), over-polish=18.8 nm(<20)", ok4,
                    f"delay={delay:.2f} s, over={over:.1f} nm"))

    # --- Test 5: 합성신호 종단 — causal 121점 MA에서 검출 인덱스 ≈ T + N (±3 샘플) ---
    R = LI2017["sample_rate_hz"]
    N = LI2017["half_span"]
    T = 600
    sig = synthetic_transition_signal(LI2017["P_base_w"], LI2017["P_after_w"], 1200, R, T,
                                      noise_std_w=50.0, seed=42)
    res_c = detect_endpoint(sig, R, N, baseline_window=200, threshold_fraction=0.027,
                            mode="causal", min_persist=5, removal_rate_nm_per_min=229.0)
    expected = T + round(detection_delay_s(N, R) * R)   # = T + 60
    err_c = None if res_c.detected_idx is None else res_c.detected_idx - expected
    ok5 = err_c is not None and abs(err_c) <= 3
    results.append(("합성신호(causal MA): 검출 idx == T+N (±3 샘플) → 이론지연 4.94 s 재현", ok5,
                    f"detected={res_c.detected_idx}, expected={expected}, err={err_c} 샘플, "
                    f"measured delay={(res_c.detected_idx - T) / R if err_c is not None else float('nan'):.2f} s"))

    # --- Test 6: 합성신호 종단 — centered MA는 오프라인 idx ≈ T, 실시간 idx ≈ T+N ---
    res_ct = detect_endpoint(sig, R, N, baseline_window=200, threshold_fraction=0.027,
                             mode="centered", min_persist=5)
    ok6 = (res_ct.detected_idx is not None and abs(res_ct.detected_idx - T) <= 3
           and abs(res_ct.realtime_idx - expected) <= 3)
    results.append(("합성신호(centered MA): 오프라인 idx ≈ T, 실시간 idx ≈ T+N", ok6,
                    f"detected={res_ct.detected_idx}, realtime={res_ct.realtime_idx}, T={T}, T+N={expected}"))

    # --- Test 7: 계단 없는 잡음신호 → None (오검출 없음) ---
    flat = synthetic_transition_signal(LI2017["P_base_w"], LI2017["P_base_w"], 1200, R, T,
                                       noise_std_w=50.0, seed=42)
    res_f = detect_endpoint(flat, R, N, baseline_window=200, threshold_fraction=0.027, mode="causal")
    ok7 = res_f.detected_idx is None
    results.append(("계단 없는 잡음신호 → None", ok7, f"detected={res_f.detected_idx}"))

    # --- Test 8: 노트 §6 (5) Headley 2019 상관 대소 ---
    h = HEADLEY2019
    ok8 = h["r_pmc_sf"] > h["r_pmc_cof"] and h["R2_pmc_sf"] > h["R2_pmc_cof"] \
        and abs(h["R2_pmc_sf"] - h["r_pmc_sf"] ** 2) < 0.02
    results.append(("§6(5) Headley2019 r(PMC,SF)=0.955 > r(PMC,COF)=0.758", ok8, str(h)))

    print("=== friction_cof_epd.py self-test ===")
    n_pass = 0
    for name, ok, detail in results:
        status = "PASS" if ok else "FAIL"
        if ok:
            n_pass += 1
        print(f"[{status}] {name}\n    {detail}")
    print(f"\n{n_pass}/{len(results)} PASS")
    return n_pass == len(results)


if __name__ == "__main__":
    import sys
    success = _self_test()
    sys.exit(0 if success else 1)
