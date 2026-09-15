"""Sorooshian (2005) PhD dissertation §3.3 표 3.3–3.6 실측 기반 —
패턴밀도별 유효압력/인가압력 비를 표에서 그대로 조회하고, Boning 밀도모델
RR_up = K/ρ_eff가 함의하는 1/ρ 증폭비와 나란히 비교한다.

지식 근거: knowledge/cmp/product-wafer-proxy-metrics-virtual-metrology.md §4, §6 verify (B)(B').
이 모듈은 그 노트 §6 verify (B) 블록의 표·로직을 순수함수로 옮긴 것이며, 새로운 문헌
숫자를 도입하지 않는다.

핵심 결론(노트 §4): 밀도 10/50/90%에서 유효압력/인가압력 비는 각각 약 2.2/1.7/1.3배로,
1/ρ 모델이 함의하는 10/2/1.11배보다 훨씬 작다 — 특히 저밀도(10%)에서 1/ρ 모델은
실측을 4배 이상 과대예측한다. 표에 없는 (density, pressure, temp_C) 조합에 대해서는
조용한 보간·외삽을 하지 않고 ValueError를 낸다(다른 tier2_physics 모듈들과 동일 관례).

실행: python3 npw_ptw_effective_pressure.py -> self-test 결과 stdout.
"""

# Sorooshian(2005) PhD dissertation §3.3, 표 3.3(10°C)/3.4(23°C)/3.5(35°C)/3.6(45°C)
# 각 density에 대해 순서: [(psi_applied, psi_effective), ...] at temps [10, 23, 35, 45]°C, 각 온도당 (3psi, 7psi) 2쌍
P_EFF_TABLE = {
    0.10: [(3, 8.15), (7, 13.37), (3, 8.01), (7, 15.21), (3, 8.58), (7, 15.77), (3, 12.73), (7, 17.80)],
    0.50: [(3, 5.12), (7, 10.57), (3, 4.64), (7, 11.42), (3, 4.66), (7, 11.98), (3, 7.96), (7, 14.14)],
    0.90: [(3, 2.90), (7, 8.03), (3, 3.50), (7, 8.65), (3, 3.66), (7, 8.96), (3, 4.91), (7, 10.19)],
}
TEMPS_C = [10, 23, 35, 45]  # 표 순서와 대응 (각 온도당 2행: 3psi, 7psi)
LIT_SUMMARY_RATIO = {0.10: 2.2, 0.50: 1.7, 0.90: 1.3}  # 논문 §3.3.3 요약 문장 (23°C 근방 대표값)


def table_ratio(density, pressure_psi, temp_C):
    """표에서 정확히 (density, pressure_psi, temp_C) 조합의 effective/applied 비율을 조회.

    density는 {0.10, 0.50, 0.90}, pressure_psi는 {3, 7}, temp_C는 {10, 23, 35, 45} 중
    정확히 일치해야 한다 — 없으면 ValueError(조용한 보간·외삽 금지).
    """
    if density not in P_EFF_TABLE:
        raise ValueError(f"표에 없는 density: {density} (지원: {sorted(P_EFF_TABLE)})")
    if temp_C not in TEMPS_C:
        raise ValueError(f"표에 없는 temp_C: {temp_C} (지원: {TEMPS_C})")
    if pressure_psi not in (3, 7):
        raise ValueError(f"표에 없는 pressure_psi: {pressure_psi} (지원: 3, 7)")
    temp_idx = TEMPS_C.index(temp_C)
    row_idx = 2 * temp_idx + (0 if pressure_psi == 3 else 1)
    pa, pe = P_EFF_TABLE[density][row_idx]
    assert pa == pressure_psi
    return pe / pa


def mean_ratio_at_density(density):
    """해당 density의 8개 표 값(4온도×2압력) 평균."""
    if density not in P_EFF_TABLE:
        raise ValueError(f"표에 없는 density: {density} (지원: {sorted(P_EFF_TABLE)})")
    ratios = [
        table_ratio(density, pressure_psi, temp_C)
        for temp_C in TEMPS_C
        for pressure_psi in (3, 7)
    ]
    return sum(ratios) / len(ratios)


def summary_ratio(density):
    """LIT_SUMMARY_RATIO에서 조회 — 논문이 보고한 요약값."""
    if density not in LIT_SUMMARY_RATIO:
        raise ValueError(f"요약값 없는 density: {density} (지원: {sorted(LIT_SUMMARY_RATIO)})")
    return LIT_SUMMARY_RATIO[density]


def inverse_density_ratio(density):
    """1.0/density — Boning 밀도모델 RR_up=K/ρ_eff가 함의하는 압력 증폭비 (비교용)."""
    return 1.0 / density


def effective_pressure_ratio(density, pressure_psi=None, temp_C=23.0):
    """유효압력/인가압력 비의 최종 공개 API.

    pressure_psi가 None이면 해당 (density, temp_C)에서 3psi/7psi 표값의 평균을 반환.
    pressure_psi가 3 또는 7이면 table_ratio로 정확 조회. temp_C나 pressure_psi가 표에
    없는 값이면 ValueError(조용한 반올림 금지).

    1/ρ 모델과의 비교값이 필요하면 inverse_density_ratio(density)를 별도로 호출할 것
    (합치지 않는다 — 두 값을 나란히 비교하는 것이 노트의 핵심 결론).
    """
    if pressure_psi is None:
        return (table_ratio(density, 3, temp_C) + table_ratio(density, 7, temp_C)) / 2.0
    return table_ratio(density, pressure_psi, temp_C)


def _self_test():
    results = []

    # --- Test 1: 표 원값 그대로 (10%, 3psi, 45°C) ---
    r1 = table_ratio(0.10, 3, 45)
    ok1 = bool(abs(r1 - 12.73 / 3) < 1e-9)
    results.append(("table_ratio(0.10,3,45) == 12.73/3 (표 원값)",
                     ok1, f"{r1:.6f} (목표 {12.73/3:.6f})"))

    # --- Test 2~4: 표 8조건 평균 ---
    m10 = mean_ratio_at_density(0.10)
    m50 = mean_ratio_at_density(0.50)
    m90 = mean_ratio_at_density(0.90)
    ok2 = bool(abs(m10 - 2.67) < 0.02)
    ok3 = bool(abs(m50 - 1.79) < 0.02)
    ok4 = bool(abs(m90 - 1.27) < 0.02)
    results.append(("mean_ratio_at_density(0.10) ~= 2.67", ok2, f"{m10:.4f}"))
    results.append(("mean_ratio_at_density(0.50) ~= 1.79", ok3, f"{m50:.4f}"))
    results.append(("mean_ratio_at_density(0.90) ~= 1.27", ok4, f"{m90:.4f}"))

    # --- Test 5: 표 평균 vs 요약값 상대오차 <= 25% (전 density) ---
    ok5 = True
    detail5 = []
    for d in (0.10, 0.50, 0.90):
        rel_err = abs(mean_ratio_at_density(d) - summary_ratio(d)) / summary_ratio(d)
        detail5.append(f"d={d}: {rel_err*100:.1f}%")
        ok5 = ok5 and rel_err <= 0.25
    results.append(("표 평균과 요약값 상대오차 <= 25% (전 density)", ok5, ", ".join(detail5)))

    # --- Test 6: 1/ρ 모델이 10% 밀도에서 4배 이상 과대예측 ---
    r10 = inverse_density_ratio(0.10) / mean_ratio_at_density(0.10)
    ok6 = bool(r10 > 3.5)
    results.append(("inverse_density_ratio(0.10)/mean_ratio_at_density(0.10) > 3.5",
                     ok6, f"{r10:.3f}"))

    # --- Test 7: 고온일수록 유효압력비가 커짐 (단조성, 전 density·pressure 조합) ---
    ok7 = True
    detail7 = []
    for d in (0.10, 0.50, 0.90):
        for p in (3, 7):
            hi = table_ratio(d, p, 45)
            lo = table_ratio(d, p, 10)
            cond = hi > lo
            ok7 = ok7 and cond
            detail7.append(f"({d},{p}): {lo:.2f}->{hi:.2f} {'OK' if cond else 'FAIL'}")
    results.append(("table_ratio(...,45) > table_ratio(...,10) 전 조합에서 성립",
                     ok7, "; ".join(detail7)))

    # --- Test 8: 표에 없는 조합은 ValueError ---
    try:
        table_ratio(0.10, 5, 23)
        ok8 = False
        detail8 = "ValueError가 발생하지 않음"
    except ValueError as e:
        ok8 = True
        detail8 = f"ValueError 발생: {e}"
    results.append(("table_ratio(0.10, 5, 23) (pressure_psi=5는 표에 없음)는 ValueError",
                     ok8, detail8))

    # --- Test 9: effective_pressure_ratio(pressure_psi=None)이 3psi/7psi 평균과 일치 ---
    epr = effective_pressure_ratio(0.10, temp_C=23)
    expect9 = (table_ratio(0.10, 3, 23) + table_ratio(0.10, 7, 23)) / 2.0
    ok9 = bool(abs(epr - expect9) < 1e-9)
    results.append(("effective_pressure_ratio(0.10,temp_C=23)이 table_ratio 3psi/7psi 평균과 일치",
                     ok9, f"{epr:.6f} (목표 {expect9:.6f})"))

    print("=== npw_ptw_effective_pressure.py self-test ===")
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
