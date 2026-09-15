"""
Cu-H2O Pourbaix(전위-pH) 경계 함수 — CRC 표준전위표에서 직접 유도.

배경 지식: knowledge/cmp/cu-electrochemistry-pourbaix-bta-oxidizer-inhibitor.md
(film-cu Lv1-2) §2 (경계 유도) · §7 verify 1 (코드 대조).

핵심 물리 (노트 §2):
    25 degC, k = (RT/F)*ln(10) = 0.05916 V. CRC 표(Vanysek, papers/crc-vanysek-
    electrochemical-series.pdf) 반쪽반응 6개의 E0(V vs SHE)에서 Cu-H2O 경계선을
    Nernst 식으로 유도해 Tamilmani 2005 (UA 학위논문, hdl 10150/280774) 그림 4.1
    판독값과 대조한다 (노트 §2.1, ±0.03 V / ±0.15 pH 내 일치).

CuO 관련 경계는 구현하지 않는다: CRC 표에 CuO 반쪽반응이 없어 CuO의 ΔG_f°를
1차값으로 확보하지 못했다(노트 §2.2, §8). 대신 Cu(OH)2 경계(준안정상, 방향만
CuO보다 낮은 pH/낮은 전위 쪽으로 검증됨)를 대용으로 쓰고, 이 모듈 전체에서
"Cu(OH)2 (CuO 자리 대용, 미검증)"라고만 표기한다 — CuO라고 단정하지 않는다.
"""

from __future__ import annotations

import math

# CRC 'Electrochemical Series' (Vanysek) 표 값, V vs SHE — papers/ PDF 표에서 그대로
E0_CU2_CU = 0.3419        # Cu2+ + 2e- = Cu
E0_CU1_CU = 0.521         # Cu+ + e- = Cu
E0_CU2_CU1 = 0.153        # Cu2+ + e- = Cu+
E0_CU2O_ALK = -0.360      # Cu2O + H2O + 2e- = 2Cu + 2OH-
E0_CUOH2_ALK = -0.222     # Cu(OH)2 + 2e- = Cu + 2OH-
E0_2CUOH2_CU2O_ALK = -0.080  # 2Cu(OH)2 + 2e- = Cu2O + 2OH- + H2O

K_NERNST = 0.05916  # V, (RT/F)*ln(10) @ 25 degC (노트 §2)
PKW = 14.00


def cu2_cu_boundary_V(log_a_cu: float) -> float:
    """Cu2+/Cu 수평선 (노트 §2 식 1): E = E0 + (k/2)*log_a_cu.

    log_a_cu=-4 -> 0.2236 V (Tamilmani 2005 그림 4.1 판독 0.22 V),
    log_a_cu=-6 -> 0.1644 V (판독 0.16 V).
    """
    return E0_CU2_CU + (K_NERNST / 2.0) * log_a_cu


def cu_cu2o_boundary_V(pH: float) -> float:
    """Cu/Cu2O 경사선 (노트 §2 식 2), 기울기 -k.

    2Cu + H2O = Cu2O + 2H+ + 2e-, E0(산성형) = -0.360 + 14*k = 0.4682 V.
    pH=8 -> -0.005 V, pH=13 -> -0.301 V (Tamilmani 2005 그림 4.1 판독 각각
    약 0.00 V, 약 -0.30 V).
    """
    E0_acid = E0_CU2O_ALK + K_NERNST * PKW  # 0.4682 V
    return E0_acid - K_NERNST * pH


def cu2_cu2o_boundary_V(pH: float, log_a_cu: float) -> float:
    """Cu2+/Cu2O 경사선 (노트 §2 식 3), 기울기 +k.

    2Cu2+ + H2O + 2e- = Cu2O + 2H+, E0 = 2*0.3419 - 0.4682 = 0.2156 V.
    """
    E0_acid_Cu2O = E0_CU2O_ALK + K_NERNST * PKW
    E0 = 2.0 * E0_CU2_CU - E0_acid_Cu2O  # 0.2156 V
    return E0 + K_NERNST * pH + K_NERNST * log_a_cu


def triple_point_pH(log_a_cu: float) -> float:
    """Cu/Cu2+/Cu2O 삼중점 pH (노트 §2 식 3, 수평선과 경사선의 교점).

    pH = (E0_Cu2_Cu - E0_Cu2_Cu2O - (k/2)*log_a_cu) / k.
    log_a_cu=-4 -> pH 4.14 (판독 약 4.2), log_a_cu=-6 -> pH 5.14.
    """
    E0_acid_Cu2O = E0_CU2O_ALK + K_NERNST * PKW
    E0_cu2_cu2o = 2.0 * E0_CU2_CU - E0_acid_Cu2O
    return (E0_CU2_CU - E0_cu2_cu2o - (K_NERNST / 2.0) * log_a_cu) / K_NERNST


def cu2_cuoh2_vertical_pH(log_a_cu: float) -> float:
    """Cu2+/Cu(OH)2 수직선 pH (노트 §2 식 4) — CuO 자리에 Cu(OH)2 대용, 미검증.

    log_Ksp = -2*(E0_Cu2_Cu - E0_CuOH2_alk)/k = -19.06 (준안정 Cu(OH)2 기준).
    pH = (log_Ksp + 2*pKw - log_a_cu) / 2.
    log_a_cu=-4 -> pH 6.47, log_a_cu=-6 -> pH 7.47.
    실제 CuO 경계(그림 4.1 판독 pH 약 5.65)는 CRC 표에 CuO 반쪽반응이 없어
    계산 불가 — 이 값은 그 대용이며 방향만(더 높은 pH) 검증됐다(노트 §2.2).
    """
    log_Ksp = -2.0 * (E0_CU2_CU - E0_CUOH2_ALK) / K_NERNST  # -19.06
    return (log_Ksp + 2.0 * PKW - log_a_cu) / 2.0


def cu2o_cuoh2_boundary_V(pH: float) -> float:
    """Cu2O/Cu(OH)2 경사선 (노트 §2 식 5), 기울기 -k — CuO 자리 대용, 미검증.

    E0 = -0.080 + 14*k = 0.748 V, E = 0.748 - k*pH.
    실제 Cu2O/CuO 경계(그림 4.1 판독 절편 약 0.64 V)의 대용이며 방향만
    (더 높은 전위) 검증됐다(노트 §2.2).
    """
    E0 = E0_2CUOH2_CU2O_ALK + K_NERNST * PKW  # 0.748 V
    return E0 - K_NERNST * pH


def cu_plus_disproportionation_logK() -> float:
    """Cu+ 불균화 평형상수 log K (노트 §2 식 6): 2Cu+ = Cu + Cu2+.

    log K = (E0_Cu1_Cu - E0_Cu2_Cu1)/k ~= +6.22. 양수이므로 착화제 없는
    물에서 Cu+(aq)는 열역학적으로 불안정 — Cu-H2O 도표에 Cu+(aq) 영역이
    없는 이유(노트 §2 식 6).
    """
    return (E0_CU1_CU - E0_CU2_CU1) / K_NERNST


def stable_phase(pH: float, E_V: float, log_a_cu: float = -4.0) -> str:
    """(pH, E, log_a_Cu) 입력에서 안정상을 판정한다.

    반환값은 "Cu" / "Cu2+" / "Cu2O" / "Cu(OH)2 (CuO 자리 대용, 미검증)" 중 하나.
    CuO 자체는 CRC 표에 ΔG_f°/반쪽반응이 없어 계산 불가(노트 §2.2, §8) —
    이 함수는 Cu(OH)2 경계를 그 자리에 대용으로 쓰며, 그 상 이름을 CuO라고
    단정하지 않는다.

    판정 순서 (노트 §2 도표 구조 그대로):
    1. E가 삼중점 pH 기준 저전위측 경계(Cu2+/Cu 수평선 또는 Cu/Cu2O 경사선)
       아래면 금속 Cu.
    2. 금속 위 영역에서, pH가 Cu2+/Cu(OH)2 수직선보다 낮으면 Cu2+ 계열
       (저 pH: Cu2+, 삼중점 위 pH에서는 Cu2O가 먼저 나오므로 2->3 순서로 검사).
    3. 그 외에는 Cu2O 또는 Cu(OH)2 대용 산화물(경사선 위/아래로 구분).
    """
    pH_triple = triple_point_pH(log_a_cu)
    pH_vert = cu2_cuoh2_vertical_pH(log_a_cu)

    if pH <= pH_triple:
        # 저 pH 영역: 저전위측 경계는 Cu2+/Cu 수평선
        e_metal_bound = cu2_cu_boundary_V(log_a_cu)
        if E_V <= e_metal_bound:
            return "Cu"
        if pH <= pH_vert:
            return "Cu2+"
        return "Cu(OH)2 (CuO 자리 대용, 미검증)"
    else:
        # 고 pH 영역: 저전위측 경계는 Cu/Cu2O 경사선
        e_metal_bound = cu_cu2o_boundary_V(pH)
        if E_V <= e_metal_bound:
            return "Cu"
        if pH <= pH_vert:
            e_ox_bound = cu2_cu2o_boundary_V(pH, log_a_cu)
            return "Cu2+" if E_V > e_ox_bound else "Cu2O"
        e_ox2_bound = cu2o_cuoh2_boundary_V(pH)
        return "Cu(OH)2 (CuO 자리 대용, 미검증)" if E_V > e_ox2_bound else "Cu2O"


def _self_test() -> None:
    results = []

    v = cu2_cu_boundary_V(-4.0)
    results.append((f"Cu2+/Cu 수평선 log_a=-4 -> {v:.4f} V (그림 0.22)", abs(v - 0.224) < 0.03))
    v = cu2_cu_boundary_V(-6.0)
    results.append((f"Cu2+/Cu 수평선 log_a=-6 -> {v:.4f} V (그림 0.16)", abs(v - 0.164) < 0.03))

    v = cu_cu2o_boundary_V(8.0)
    results.append((f"Cu/Cu2O @pH8 -> {v:+.4f} V (그림 0.00)", abs(v - (-0.005)) < 0.03))
    v = cu_cu2o_boundary_V(13.0)
    results.append((f"Cu/Cu2O @pH13 -> {v:+.4f} V (그림 -0.30)", abs(v - (-0.301)) < 0.03))

    v = triple_point_pH(-4.0)
    results.append((f"삼중점 log_a=-4 -> pH {v:.2f} (그림 4.2)", abs(v - 4.14) < 0.15))
    v = triple_point_pH(-6.0)
    results.append((f"삼중점 log_a=-6 -> pH {v:.2f}", abs(v - 5.14) < 0.15))

    v = cu2_cuoh2_vertical_pH(-4.0)
    results.append((f"Cu2+/Cu(OH)2 수직선 log_a=-4 -> pH {v:.2f}", abs(v - 6.47) < 0.15))
    v = cu2_cuoh2_vertical_pH(-6.0)
    results.append((f"Cu2+/Cu(OH)2 수직선 log_a=-6 -> pH {v:.2f}", abs(v - 7.47) < 0.15))

    v = cu_plus_disproportionation_logK()
    results.append((f"Cu+ 불균화 logK -> {v:+.2f} (기대 +6.22)", abs(v - 6.22) < 0.05))

    # stable_phase 계약 테스트 (방향성)
    r = stable_phase(2.0, 0.3, log_a_cu=-4.0)
    results.append((f"stable_phase(pH2, E0.3) -> {r} (기대 Cu2+)", r == "Cu2+"))
    r = stable_phase(13.0, -0.5, log_a_cu=-4.0)
    results.append((f"stable_phase(pH13, E-0.5) -> {r} (기대 Cu)", r == "Cu"))
    r = stable_phase(8.0, 0.3, log_a_cu=-4.0)
    results.append((f"stable_phase(pH8, E0.3) -> {r} (기대 Cu(OH)2 대용)",
                     r == "Cu(OH)2 (CuO 자리 대용, 미검증)"))
    r = stable_phase(10.0, 0.0, log_a_cu=-4.0)
    results.append((f"stable_phase(pH10, E0.0) -> {r} (기대 Cu2O)", r == "Cu2O"))

    passed = sum(1 for _, ok in results if ok)
    print(f"cu_pourbaix self-test: {passed}/{len(results)} PASS")
    for name, ok in results:
        print(f"  [{'PASS' if ok else 'FAIL'}] {name}")
    assert passed == len(results), "self-test 실패"


if __name__ == "__main__":
    _self_test()
