"""
컨디셔너 자체의 성능 노화(aging) — Pad Cut Rate(PCR) 시간적 감쇠 모델.

지식 근거: knowledge/equipment/conditioner-disk-pad-cutting-model.md (disk-conditioner Lv2-1)
  1차 출처(정량 앵커): Entegris Inc., "Development and Performance Data of a New CVD Diamond
  CMP Pad Conditioner" (2013, 공개 application note, 4435-7548ENT-1213) 본문 서술 —
  "상용공정에서 50시간 사용된 디스크의 평균 PCR이 초기값 대비 지수적으로 감소해 16%로
  떨어졌을 때(~4 mils/hour) 교체됨" (원출처는 이 문서가 재인용한 Palmgren 2004,
  CMP-MIC Conf. Proc. — 원문 미확보, 2차 인용).
  질적 대조군: 동일 문서 Case Study 2/4/5 — 개선설계(Planargem)는 10~50시간 동안
  PCR·Ra가 "안정"(stability)하다고 서술 → tau가 매우 크거나 발산하는 한계로 모델링.

이 모듈은 pad_wear_glazing.py를 재사용/확장한다(기존 함수 무수정, import만) — 컨디셔너
자체가 노화되면 절삭(cut, 재생)이 약해져 패드 마모(wear)를 상쇄하는 힘이 줄어들고, 그 결과
방치했을 때보다는 느리지만 이상적 컨디셔너보다는 빠르게 asperity 평균 높이가 감소한다는
가설을 세우고 수치로 검증한다.

모델:
  1. PCR(t_cond) = PCR_inf + (PCR_0 - PCR_inf) * exp(-t_cond / tau)   -- 지수 감쇠
     tau는 앵커(t_anchor, ratio=PCR(t_anchor)/PCR_0)로 역산: PCR_inf=0 근사 시
       tau = -t_anchor / ln(ratio)
  2. 컨디셔너가 있는 in-situ 마모 ODE (Ring et al. §4.3 "컨디셔너 절삭이 지배적" 확장):
       dz/dt = -C1_wear * sqrt(max(z-d,0))              (기존 wear_step_borucki와 동일 항, 웨이퍼측 마모)
             + C1_cond * (PCR(t_cond)/PCR_0) * sqrt(max(z0-z,0))   (컨디셔너 재생/절삭 항, 새로 추가)
     두 번째 항은 "컨디셔너가 원래 높이 z0(신품 asperity 평균)를 향해 표면을 되깎는다"는
     정성적 서술(Lawing 2004, Lv1-1)의 최소 정량화이며, PCR(t)/PCR_0=1(신품 컨디셔너)일 때
     재생력이 최대이고 컨디셔너가 노화되면(PCR↓) 재생력도 비례해서 약해진다.
     **주의**: 이 재생항의 함수형(sqrt(z0-z), 계수 C1_cond)은 문헌에서 직접 가져온 식이
     아니라 fab-sim이 세운 최소 확장 가정이다 — self-test는 "방향"(정성적 순위)만 검증하고
     정량값은 미보증으로 명시한다.

실행: python3 conditioner_pcr_decay.py -> self-test 결과 stdout.
"""
import math
import numpy as np

from pad_wear_glazing import sample_heights, solve_separation_discrete, total_load_discrete


def pcr_decay(t, PCR0, tau, PCR_inf=0.0):
    """PCR(t) = PCR_inf + (PCR0-PCR_inf)*exp(-t/tau). tau<=0이면 즉시 PCR_inf."""
    if tau <= 0:
        return PCR_inf
    return PCR_inf + (PCR0 - PCR_inf) * math.exp(-t / tau)


def calibrate_tau_from_anchor(t_anchor, ratio, PCR_inf_frac=0.0):
    """
    실측 앵커(t_anchor 시점에 PCR이 초기값의 ratio배로 떨어짐)로 tau를 역산.
    PCR_inf_frac: PCR_inf = PCR_inf_frac * PCR0 (완전 소진이면 0).
    반환: tau (t_anchor와 동일 시간단위)
    """
    if not (0 < ratio < 1):
        raise ValueError("ratio는 (0,1) 구간이어야 함")
    # (ratio - PCR_inf_frac) = (1-PCR_inf_frac)*exp(-t/tau)
    numerator = ratio - PCR_inf_frac
    denom = 1.0 - PCR_inf_frac
    if numerator <= 0:
        raise ValueError("PCR_inf_frac이 ratio보다 크면 안 됨(음수 로그)")
    return -t_anchor / math.log(numerator / denom)


# Entegris 문서 앵커: 50시간에 PCR이 초기값의 16%로 하락, PCR_inf≈0 근사
ENTEGRIS_ANCHOR_T_HOURS = 50.0
ENTEGRIS_ANCHOR_RATIO = 0.16
TAU_AGING_HOURS = calibrate_tau_from_anchor(ENTEGRIS_ANCHOR_T_HOURS, ENTEGRIS_ANCHOR_RATIO)


def simulate_conditioned_wear(
    n_asperity=20000,
    beta=1.0 / 0.3e-6,
    R=5e-6,
    E_star=1e9,
    P_app=20e3,
    A_n=1e-4,
    C1_wear=2e-6,
    C1_cond=2e-6,
    PCR0_norm=1.0,       # 정규화 PCR0 (무차원, PCR(t)/PCR0가 재생력 스케일)
    tau_hours=TAU_AGING_HOURS,
    n_steps=40,
    dt_hours=1.0,
    seed=42,
):
    """
    컨디셔너가 노화(tau_hours)하며 동작하는 상황에서 asperity 평균 높이·정상상태 접촉압력의
    시간적 추이를 시뮬레이션. tau_hours=float('inf')로 두면 "이상적(노화 없음) 컨디셔너"
    극한이 된다 (Entegris Planargem "stability" 사례에 대응).
    """
    rng = np.random.default_rng(seed)
    heights = sample_heights(n_asperity, beta, rng)
    z0 = float(heights.mean())  # 신품 평균 asperity 높이 (컨디셔너 재생 목표값)
    W_target = P_app * A_n

    t_arr, meanh_arr, pr_arr, pcr_norm_arr = [], [], [], []

    for step in range(n_steps):
        t = step * dt_hours
        d = solve_separation_discrete(heights, W_target, E_star, R,
                                       d_bracket=(-5.0 / beta, float(heights.max())))
        W = total_load_discrete(heights, d, E_star, R)
        from pad_wear_glazing import total_area_discrete
        A_r = total_area_discrete(heights, d, R)
        p_r = W / A_r if A_r > 0 else float("nan")

        pcr_now = pcr_decay(t, PCR0_norm, tau_hours)

        t_arr.append(t)
        meanh_arr.append(float(heights.mean()))
        pr_arr.append(p_r)
        pcr_norm_arr.append(pcr_now / PCR0_norm)

        delta_wear = np.clip(heights - d, 0.0, None)
        dz_wear = C1_wear * np.sqrt(delta_wear) * dt_hours
        delta_regen = np.clip(z0 - heights, 0.0, None)
        dz_regen = C1_cond * (pcr_now / PCR0_norm) * np.sqrt(delta_regen) * dt_hours

        heights = heights - dz_wear + dz_regen

    return {
        "t": np.array(t_arr),
        "mean_height": np.array(meanh_arr),
        "p_r": np.array(pr_arr),
        "pcr_norm": np.array(pcr_norm_arr),
    }


def _self_test():
    results = []

    # --- Test 1: 캘리브레이션된 tau로 앵커 재현 (50h -> 16%) ---
    ratio_check = pcr_decay(ENTEGRIS_ANCHOR_T_HOURS, 1.0, TAU_AGING_HOURS)
    ok1 = bool(abs(ratio_check - ENTEGRIS_ANCHOR_RATIO) < 1e-9)
    results.append(("캘리브레이션된 tau로 Entegris 앵커(50h->16%) 정확히 재현",
                     ok1, f"PCR(50h)/PCR0={ratio_check:.6f} (목표 {ENTEGRIS_ANCHOR_RATIO}), tau={TAU_AGING_HOURS:.3f}h"))

    # --- Test 2: tau -> inf 극한에서 PCR(t) = PCR0 상수 (Planargem "stability" 극한) ---
    pcr_inf_tau = pcr_decay(1000.0, 1.0, float("inf"))
    ok2 = bool(abs(pcr_inf_tau - 1.0) < 1e-12)
    results.append(("tau->inf 극한에서 PCR(t)=PCR0 상수 (Planargem 안정성 극한 재현)",
                     ok2, f"PCR(1000h)/PCR0={pcr_inf_tau}"))

    # --- Test 3: PCR(t)는 t에 대해 단조 비증가 (물리적으로 컨디셔너는 회복되지 않음) ---
    ts = np.linspace(0, 100, 50)
    pcrs = np.array([pcr_decay(t, 1.0, TAU_AGING_HOURS) for t in ts])
    ok3 = bool(np.all(np.diff(pcrs) <= 1e-15))
    results.append(("PCR(t) 단조 비증가 (컨디셔너 자연 회복 없음)",
                     ok3, f"PCR(0)={pcrs[0]:.4f} -> PCR(100h)={pcrs[-1]:.4f}"))

    # --- Test 4: 노화하는 컨디셔너(tau=TAU_AGING_HOURS) vs 이상적 컨디셔너(tau=inf) 비교 ---
    # 가설: 노화 컨디셔너 하에서는 재생력이 시간에 따라 약해지므로, 이상적 컨디셔너보다
    # 평균 asperity 높이가 더 많이 감소해야 한다 (patd 마모 방향의 정성적 순위 확인).
    r_aging = simulate_conditioned_wear(tau_hours=TAU_AGING_HOURS, n_steps=40, dt_hours=1.0)
    r_ideal = simulate_conditioned_wear(tau_hours=float("inf"), n_steps=40, dt_hours=1.0)
    h_aging_final = r_aging["mean_height"][-1]
    h_ideal_final = r_ideal["mean_height"][-1]
    ok4 = bool(h_aging_final < h_ideal_final)
    results.append(("노화 컨디셔너 하 평균 asperity 높이가 이상적 컨디셔너보다 더 많이 감소 (정성적 방향 확인, 정량 미보증)",
                     ok4, f"h_aging(40h)={h_aging_final:.4e}m < h_ideal(40h)={h_ideal_final:.4e}m ? "
                          f"(h_aging={h_aging_final:.4e}, h_ideal={h_ideal_final:.4e})"))

    # --- Test 5: 컨디셔닝 완전 부재(C1_cond=0)가 가장 심한 마모를 보임 (경계 사례, pad_wear_glazing.py와 정합) ---
    r_none = simulate_conditioned_wear(tau_hours=TAU_AGING_HOURS, C1_cond=0.0, n_steps=40, dt_hours=1.0)
    h_none_final = r_none["mean_height"][-1]
    ok5 = bool(h_none_final < h_aging_final < h_ideal_final)
    results.append(("컨디셔닝 부재 < 노화 컨디셔너 < 이상적 컨디셔너 순으로 평균 높이 유지 (3단계 순위 확인)",
                     ok5, f"h_none={h_none_final:.4e} < h_aging={h_aging_final:.4e} < h_ideal={h_ideal_final:.4e}"))

    print("=== conditioner_pcr_decay.py self-test ===")
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
