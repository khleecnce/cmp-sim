"""
컨디셔닝-패드마모 결합모델: asperity 분포 폭(표준편차) 진화 — Lv3-2 (disk-conditioner).

지식 근거: knowledge/equipment/conditioner-asperity-population-balance.md (disk-conditioner Lv3-1)
  1차 출처: Ring, Prasad, Dirksen, "Dynamic CMP Pad Asperity Population Balance for
  Conditioning and Polishing" (저자 공개 PDF, https://my.che.utah.edu/~ring/Publications-PDFs/J-120.pdf)
  — 선형 마모율 dz/dt = -A*(z+d) 가정 하의 similarity solution(Eq.7-9):
      eta_z(z,t) = eta_z0( (z+d)*exp(2*A*t) - d )
  즉 asperity 높이 분포는 시간에 따라 "좌표축이 exp(2At)로 지수 압축"되며 형태를 유지한다
  (self-similar). 이 노트 §5가 명시한 설계 판단에 따라, 전체 PDE를 이식하지 않고
  **기존 conditioner_pcr_decay.py(스칼라 평균 높이 모델)에 "분포 폭(표준편차)" 2번째
  상태량만 추가하는 최소 확장**으로 구현한다.

결합 방식 (conditioner_pcr_decay.py 재사용, 무수정 — import만):
  conditioner_pcr_decay.pcr_decay(t, PCR0, tau)로 컨디셔너 노화에 따른 "오늘의 유효 절삭력"
  PCR(t)/PCR0 in [0,1]을 얻고, 이를 similarity 상수 A의 시간의존 스케일로 사용:
      A_eff(t) = A0 * PCR(t)/PCR0
  즉 컨디셔너가 노화될수록(PCR 하락) 분포를 좁히는 힘(A)도 비례해서 약해진다 — 이는
  conditioner_pcr_decay.py의 기존 가정("컨디셔너 재생력이 PCR(t)/PCR0에 비례")과
  구조적으로 동일한 원리를 분포폭 축에 적용한 것.

  누적 스케일 인자는 시간에 따라 변하는 A_eff(t)를 적분해야 하므로(닫힌형 대신) 이산
  시간적분으로 처리한다:
      s(t+dt) = s(t) * exp(2*A_eff(t)*dt),   sigma(t) = sigma(0) / s(t)
  (좌표가 exp(2At)배 압축되면 그 분포의 표준편차는 1/exp(2At)배로 줄어든다 — Eq.9의
  선형 재스케일링 성질에서 직접 유도되는 사실, 정규분포·지수분포 둘 다 스케일링에 대해
  '표준편차가 스케일 인자에 반비례'하는 성질을 만족하므로 분포 종류에 무관하게 성립).

  A0(초기 similarity 상수)는 문헌에서 fit parameter로만 제공되어(Lv3-1 §6 한계 명시)
  공개 정량값이 없다 — 이 모듈은 A0를 "48시간 컨디셔닝으로 표준편차가 절반이 되는" 정성적
  기준으로 임의 캘리브레이션한다(**정량 예측치 아님, 정성 시연용 값으로 코드·문서 양쪽에
  명시**).

한계(정직 표기): 이 모듈은 population balance PDE 전체를 풀지 않고 "표준편차만" 추적하는
1차 모멘트 근사다. 분포의 고차 형태(왜도 등, Fig.1의 정규->지수 형태 전이 자체)는
재현하지 않으며, similarity solution이 원래 가정하는 대상(전체 pdf)의 부분 정보만 취한다.
따라서 이 모듈의 self-test는 "표준편차가 좁아지는 방향과 상대적 순위"만 검증하고, 절대
표준편차 예측값은 미보증이다.

실행: python3 conditioner_asperity_distribution.py -> self-test 결과 stdout.
"""
import math
import numpy as np

from pad_wear_glazing import sample_heights
from conditioner_pcr_decay import pcr_decay, TAU_AGING_HOURS


def scale_factor_series(A0, tau_hours, n_steps, dt_hours, PCR0_norm=1.0):
    """
    이산 시간적분으로 누적 스케일 인자 s(t) 계산.
    s(0)=1, s(t+dt) = s(t)*exp(2*A_eff(t)*dt), A_eff(t)=A0*PCR(t)/PCR0.
    반환: (t_arr, s_arr) — s_arr[i]는 t_arr[i] 시점의 누적 스케일 인자.
    """
    t_arr = np.array([i * dt_hours for i in range(n_steps)])
    s = 1.0
    s_arr = [s]
    for i in range(n_steps - 1):
        t = t_arr[i]
        pcr_now = pcr_decay(t, PCR0_norm, tau_hours)
        A_eff = A0 * (pcr_now / PCR0_norm)
        s = s * math.exp(2.0 * A_eff * dt_hours)
        s_arr.append(s)
    return t_arr, np.array(s_arr)


def sigma_series(sigma0, A0, tau_hours, n_steps, dt_hours, PCR0_norm=1.0):
    """표준편차 시계열: sigma(t) = sigma0 / s(t)."""
    t_arr, s_arr = scale_factor_series(A0, tau_hours, n_steps, dt_hours, PCR0_norm)
    return t_arr, sigma0 / s_arr


def calibrate_A0_from_halving_time(t_half_hours):
    """
    '이상적(노화 없음) 컨디셔너 하에서 t_half_hours 시간이면 표준편차가 절반이 된다'는
    정성적 기준으로 A0 역산 (tau=inf, 즉 PCR(t)/PCR0=1 상수 가정):
      exp(2*A0*t_half) = 2  =>  A0 = ln(2) / (2*t_half)
    **정량 실측 캘리브레이션이 아니라 정성 시연 기준값**(문헌에 공개 A값 없음, Lv3-1 §6).
    """
    return math.log(2.0) / (2.0 * t_half_hours)


# 정성 시연 기준: 48시간 이상적 컨디셔닝으로 표준편차 절반 (임의 기준, 미검증 정량값)
T_HALF_HOURS = 48.0
A0_DEFAULT = calibrate_A0_from_halving_time(T_HALF_HOURS)


def apply_similarity_scaling(heights, d, A, t):
    """
    Eq.9 좌표 변환을 실제 asperity 높이 표본 배열에 직접 적용 (검증용 명시적 구현).
    z_new = (z - d)*exp(2*A*t) + d  (d를 원점으로 한 스케일링, z>=d인 asperity만 대상 —
    d는 GW 접촉모델의 분리거리 상당 기준선; 이 self-test에서는 d=0의 단순화로 원점 스케일링만
    확인한다).
    """
    return (heights - d) * math.exp(2.0 * A * t) + d


def _self_test():
    results = []
    n = 200000
    rng = np.random.default_rng(7)

    # --- Test 1: t=0에서 스케일 인자=1 (항등) ---
    t_arr, s_arr = scale_factor_series(A0_DEFAULT, float("inf"), n_steps=1, dt_hours=1.0)
    ok1 = bool(abs(s_arr[0] - 1.0) < 1e-12)
    results.append(("t=0에서 누적 스케일 인자 s(0)=1 (항등)", ok1, f"s(0)={s_arr[0]}"))

    # --- Test 2: 이상적 컨디셔너(tau=inf)에서 정확히 t_half 시간에 표준편차 절반 ---
    sigma0 = 8.112e-6  # Lv3-1 지식노트 인용 Table1 실측 sigma0(=8.112um, m 단위 환산)
    n_steps = int(T_HALF_HOURS) + 1
    t_arr2, sig_arr2 = sigma_series(sigma0, A0_DEFAULT, float("inf"), n_steps=n_steps, dt_hours=1.0)
    ratio_at_half = sig_arr2[-1] / sigma0
    ok2 = bool(abs(ratio_at_half - 0.5) < 0.02)  # 이산적분 근사오차 허용
    results.append(("이상적 컨디셔너 하 t=48h에서 sigma/sigma0≈0.5 (캘리브레이션 정의 자기재현)",
                     ok2, f"sigma(48h)/sigma0={ratio_at_half:.4f}"))

    # --- Test 3: 노화 컨디셔너(tau=TAU_AGING_HOURS)는 이상적 컨디셔너보다 표준편차 축소가 느림 ---
    t_arr3, sig_aging = sigma_series(sigma0, A0_DEFAULT, TAU_AGING_HOURS, n_steps=n_steps, dt_hours=1.0)
    ok3 = bool(sig_aging[-1] > sig_arr2[-1])
    results.append(("노화 컨디셔너의 t=48h 표준편차가 이상적 컨디셔너보다 큼 (분포 폭 축소가 더 느림, 정성적 순위)",
                     ok3, f"sigma_aging(48h)={sig_aging[-1]:.4e} > sigma_ideal(48h)={sig_arr2[-1]:.4e}"))

    # --- Test 4: 표준편차는 시간에 따라 단조 비증가 (물리적으로 조건화는 분포를 넓히지 않음) ---
    ok4 = bool(np.all(np.diff(sig_arr2) <= 1e-15))
    results.append(("이상적 컨디셔너 하 sigma(t) 단조 비증가", ok4,
                     f"sigma(0)={sig_arr2[0]:.4e} -> sigma({t_arr2[-1]:.0f}h)={sig_arr2[-1]:.4e}"))

    # --- Test 5: 실제 정규분포 표본에 similarity 스케일링을 직접 적용했을 때, 표본 표준편차가
    #     apply_similarity_scaling 후 이론 예측(1/exp(2At))과 일치 (분포-불문 스케일링 성질 검증) ---
    heights = rng.normal(loc=50e-6, scale=sigma0, size=n)
    A_test = A0_DEFAULT
    t_test = 20.0
    scaled = apply_similarity_scaling(heights, d=0.0, A=A_test, t=t_test)
    theory_ratio = math.exp(2.0 * A_test * t_test)  # std(scaled)/std(original) 예측값
    empirical_ratio = float(scaled.std() / heights.std())
    ok5 = bool(abs(empirical_ratio - theory_ratio) / theory_ratio < 1e-3)
    results.append(("정규분포 표본에 similarity 스케일링 직접 적용 시 std(scaled)/std(original)이 이론(exp(2At))과 일치",
                     ok5, f"이론비={theory_ratio:.6f}, 실측비={empirical_ratio:.6f} (n={n} 표본)"))

    print("=== conditioner_asperity_distribution.py self-test ===")
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
