"""
Jeong et al. 2024 (Materials 17, 1817, doi.org/10.3390/ma17081817) 실측 기반 —
컨디셔닝 없는 연마에서 접촉점 수 N(t) 감소·평균 asperity 반경 μR(t) 증가를 재현하고,
그 곱으로 "접촉당 힘×개수"의 가장 거친 근사인 relative_mrr_proxy(t)를 구성한다.

지식 근거: knowledge/materials/pad-glazing-mechanism-mrr-decay.md (pad-lifecycle Lv2-1) §2.1,
§2.2, §4 (A)(B). 이 모듈은 그 노트 §4 verify 블록의 로직을 순수함수로 옮긴 것이며,
새로운 문헌 숫자를 도입하지 않는다 — Table 1 원문 표, Eq.4 계수, 노트에서 이미 검증된
지수감쇠 피팅 로직 그대로다.

이 모듈이 존재하는 배경(S13 판정): wear_aware_kp_physical.py의 GW discrete Monte-Carlo는
"고정 명목압력 하 asperity 집단이 얇아지면 접촉점 수 n(t)가 증가한다"고 예측했다
(그 모듈 self-test, corr≈-0.998). 그런데 Jeong 2024의 실측(Table 1)은 정반대로 접촉점
수가 **감소**하며, 동시에 MRR도 감소한다(Fig.9). 이 모듈은 그 실측 방향(접촉점 감소)을
정량 재현하고, "접촉수 감소를 반경 증가가 부분 보상해 MRR이 접촉수만큼 급락하지는
않는다"는 노트 §2.3의 서술을 relative_mrr_proxy로 최소 근사한다.

**relative_mrr_proxy는 거친 근사다** — "접촉당 힘"을 평균반경 μR로만 근사했고(반경↑ =
접촉당 힘↑ 이라는 최소 가정), 실제 압입깊이·유효탄성계수가 들어간 Hertz 접촉력이나
Jeong 2024 §4.2의 3-모드(탄성/탄소성/소성) MRR 공식(Eq.20)은 구현하지 않는다(범위 밖).
따라서 relative_mrr_proxy(t)의 절대값이나 피크 시점을 Fig.9 실측 MRR과 정량 비교하는
것은 근거 없는 정밀도 주장이 된다 — 이 모듈의 self-test는 "초기 상승 후 하강하는
비단조 패턴이 존재하는가"라는 방향성만 확인한다.

⚠️ 정직 기록 (self-test 실행 결과, 2026-09-07): 애초 기대는 "t<=3분 부근에서 최댓값을
찍고 그 이후 단조감소해 t=10분에는 t=0분보다 낮아진다"(Fig.9의 2 psi 피크가 t=3분인
것과 형태를 맞춘 추측)였으나, 실제 relative_mrr_proxy(2, t)를 t=0..10(1분 간격)으로
계산하면 **피크는 t≈7분**이고, t=10분 값(≈1.21)은 t=0분 값(1.0)보다 여전히 **높다**
(t=0..10 구간에서는 초기값 아래로 떨어지지 않음 — t≈18~19분 부근에서야 1.0 아래로
내려간다, 확인용으로 범위를 넓혀 계산해봄). 즉 "상승 후 하강"이라는 정성적 형태 자체는
재현되지만, 피크 시점과 t=10 시점의 상대값은 Fig.9 실측과 어긋난다. 원인은 이 근사가
반경 증가율(선형, Eq.4)과 접촉점 지수감쇠(tau≈13.7 min @ 2psi)만으로 만든 것이라
Jeong 2024가 실제로 서술한 압입깊이 감소와 반경 증가의 경쟁(§4.2) 타이밍을 재현하지
못하기 때문으로 보인다(미검증, 추정). 이 근사를 정량 캘리브레이션에 쓰지 말 것 —
방향성 확인(비단조성 존재)까지만 사용 가치가 있다.

실행: python3 pad_glazing_jeong2024.py -> self-test 결과 stdout.
"""
import numpy as np


def mean_asperity_radius_um(p_psi, t_min):
    """Eq.4 (노트 §2.2, §4 (B)) 그대로: μR = (0.28*p + 0.621)*t + 5.45*exp(0.18*p) [µm]."""
    return (0.28 * p_psi + 0.621) * t_min + 5.45 * np.exp(0.18 * p_psi)


def contact_count_table():
    """Jeong et al. 2024 Table 1 원문 표 그대로 (노트 §2.1, §4 (A)와 동일 딕셔너리).

    반환: (t_tab, N_tab, N_cond)
      t_tab: {psi: [측정 시각(min), ...]}
      N_tab: {psi: [접촉점 수, ...]} (t_tab과 같은 순서, Bef.=t=0)
      N_cond: {psi: 10분 연마 후 1분 컨디셔닝한 접촉점 수}
    """
    t_tab = {2: [0, 1, 2, 3, 4, 5, 10], 3: [0, 1, 2, 3, 4, 5, 10],
              4: [0, 1, 2, 3, 4, 5, 10], 5: [0, 1, 2, 3, 4, 5]}
    N_tab = {2: [109, 121, 103, 113, 97, 91, 56], 3: [106, 103, 116, 110, 98, 96, 52],
              4: [121, 118, 101, 99, 80, 82, 60], 5: [114, 96, 72, 81, 60, 46]}
    N_cond = {2: 114, 3: 120, 4: 110, 5: 108}
    return t_tab, N_tab, N_cond


def contact_decay_tau_min(p_psi):
    """Table 1 데이터에 N=N0*exp(-t/tau) 최소자승 피팅(노트 §4 (A) 로직 그대로)으로 tau[min] 계산.

    2, 3, 4, 5 psi만 지원. 그 외 압력은 Table 1에 데이터가 없으므로 ValueError.
    """
    t_tab, N_tab, _ = contact_count_table()
    if p_psi not in N_tab:
        raise ValueError(f"Table 1에 없는 압력: {p_psi} psi (지원: {sorted(N_tab)})")
    t = np.array(t_tab[p_psi], dtype=float)
    y = np.log(np.array(N_tab[p_psi], dtype=float))
    slope, _ = np.polyfit(t, y, 1)
    return -1.0 / slope


def contact_ratio(p_psi, t_min):
    """N(t)/N0 = exp(-t/tau(p)) — 지수감쇠 피팅으로부터의 접촉점 비율."""
    tau = contact_decay_tau_min(p_psi)
    return np.exp(-t_min / tau)


def radius_growth_ratio(p_psi, t_min):
    """mean_asperity_radius_um(p,t) / mean_asperity_radius_um(p,0) — Eq.4 기준 반경 증가 배율."""
    return mean_asperity_radius_um(p_psi, t_min) / mean_asperity_radius_um(p_psi, 0.0)


def relative_mrr_proxy(p_psi, t_min):
    """"접촉당 힘×개수"의 가장 거친 근사 = contact_ratio(p,t) * radius_growth_ratio(p,t).

    거친 근사임에 유의(모듈 docstring 참조): "접촉당 힘"을 반경만으로 근사했고, 실제
    압입깊이·유효탄성계수 항은 포함하지 않는다. Jeong 2024 §4.2의 3-모드 MRR 공식은
    구현하지 않는다.
    """
    return contact_ratio(p_psi, t_min) * radius_growth_ratio(p_psi, t_min)


def _self_test():
    results = []

    # --- Test 1: Table 1 접촉점 감소율 (2 psi, 10 min) ---
    t_tab, N_tab, N_cond = contact_count_table()
    loss_2psi_10min = 1 - N_tab[2][-1] / N_tab[2][0]
    ok1 = bool(abs(loss_2psi_10min - 0.486) < 0.005)
    results.append(("Table 1: 2 psi 10 min 접촉점 감소율 -48.6% 재현",
                     ok1, f"{loss_2psi_10min*100:.1f}% (목표 -48.6% ±0.5%p)"))

    # --- Test 2: 5 psi가 2 psi보다 빨리 감쇠 (tau 짧음) ---
    tau2 = contact_decay_tau_min(2)
    tau5 = contact_decay_tau_min(5)
    ok2 = bool(tau5 < tau2)
    results.append(("tau(5psi) < tau(2psi) (고압이 더 빨리 감쇠)",
                     ok2, f"tau(2psi)={tau2:.2f} min, tau(5psi)={tau5:.2f} min"))

    # --- Test 3: Eq.4 mu_R(2psi, 10min) ~= 19.6 um ---
    muR_2_10 = mean_asperity_radius_um(2, 10.0)
    ok3 = bool(abs(muR_2_10 - 19.6) < 0.1)
    results.append(("Eq.4 muR(2psi, 10min) ~= 19.6 um",
                     ok3, f"muR={muR_2_10:.3f} um"))

    # --- Test 4: 반경 증가 배율 2.0~3.0배 ---
    ratio_R = radius_growth_ratio(2, 10.0)
    ok4 = bool(2.0 < ratio_R < 3.0)
    results.append(("muR(2psi,10min)/muR(2psi,0min)이 2.0~3.0배 범위",
                     ok4, f"ratio={ratio_R:.3f}"))

    # --- Test 5 (정성): relative_mrr_proxy가 t=0..10에서 비단조(상승 후 하강) 패턴을 보이는가 ---
    # 문헌수치(Fig.9)와 값 자체를 비교하지 않는다 — 패턴(방향) 존재 여부만 확인.
    ts = np.arange(0, 11, 1.0)
    proxy_vals = np.array([relative_mrr_proxy(2, t) for t in ts])
    peak_idx = int(np.argmax(proxy_vals))
    is_interior_peak = 0 < peak_idx < len(ts) - 1
    rises_then_falls = bool(np.all(np.diff(proxy_vals[:peak_idx + 1]) > 0) and
                             np.all(np.diff(proxy_vals[peak_idx:]) < 0))
    ok5 = bool(is_interior_peak and rises_then_falls)
    results.append(("relative_mrr_proxy(2,t)가 t=0..10 구간 내부에서 피크를 찍는 "
                     "비단조(상승 후 하강) 패턴을 보임 (피크 시점·t=10 상대값은 미검증, "
                     "모듈 docstring '정직 기록' 참조)",
                     ok5, f"peak at t={ts[peak_idx]:.0f}min (proxy={proxy_vals[peak_idx]:.4f}), "
                          f"t=0: {proxy_vals[0]:.4f}, t=10: {proxy_vals[-1]:.4f}"))

    # --- Test 6: 지원하지 않는 압력은 ValueError ---
    try:
        contact_decay_tau_min(2.5)
        ok6 = False
        detail6 = "ValueError가 발생하지 않음"
    except ValueError as e:
        ok6 = True
        detail6 = f"ValueError 발생: {e}"
    results.append(("Table 1에 없는 압력(2.5 psi)은 ValueError",
                     ok6, detail6))

    print("=== pad_glazing_jeong2024.py self-test ===")
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
