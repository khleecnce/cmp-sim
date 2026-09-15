"""패드 유효 탄성률 E'(T) 온도의존 모델 (로그-선형 구간보간) + WLF shift factor 유틸.

지식 근거: knowledge/materials/pad-viscoelasticity-temp-frequency-dma.md §2, §3.1, §6
구현 요청: pad-material PROFILE.md "구현 요청" 우선순위 높음·중간 2건 (S21)

계약 (엔진과의 경계):
  이 모듈은 순수 함수 라이브러리다. engine.py / models.py에 등록하지 않는다.
  사유: Preston Kp에 실제로 연결하려면 Recipe에 온도 필드가 필요한데 지금 없다
  (docs/ARCHITECTURE.md §4 스키마 부채). frictional_heating_arrhenius.py,
  metal_contamination_surface.py와 같은 지위 — "산출값 하나"를 계산하는 함수만 제공한다.

  Kp_eff(T) = Kp0*(E*(T0)/E*(T))^m 훅은 이번 범위 밖이다(노트가 실측 대조 전까지
  OFF라고 명시, PROFILE.md 우선순위 "낮음").

보간 방식에 대한 메모:
  노트 §1은 "tanh 또는 로그-시그모이드 보간"을 제안했으나, 문헌(Cabot 특허 Table 1B)은
  함수형 피팅 파라미터가 아니라 25/50/80 °C 3개 이산 앵커점만 준다. 임의로 tanh에
  피팅하면 새 숫자(피팅 파라미터)를 지어내는 것이므로, 대신 로그-선형 구간보간
  (piecewise log-linear interpolation)을 쓴다 — 앵커점을 정확히 통과하고, E'가
  전이구간에서 지수적으로 감소하는 형태를 자연스럽게 표현하며, 새 상수가 없다.

미검증 사항 (노트 그대로, 지어내지 않음):
  - CMP 패드 전용 WLF(C1, C2)는 미확보 — wlf_log_aT의 기본값은 보편상수(17.44, 51.6 K)이며
    CMP PU에 피팅된 값이 아니다.
  - Cabot Table 1B는 1 Hz DMA·인장모드 값이며, CMP 하중모드(압축)·주파수(§5 추정 ~2e4 Hz
    asperity 스케일)로의 외삽은 검증되지 않았다.

함수:
  e_pad_loglinear(T_C, T_points_C, E_points_MPa)  -> 로그-선형 구간보간 E' [MPa], 범위 밖은 clamp
  e_pad_from_table(T_C, pad_id)                   -> CABOT_TABLE_1B 룩업 + e_pad_loglinear
  wlf_log_aT(T, Tr, C1, C2)                       -> log10(a_T), WLF 식
  wlf_reparametrize(C1, C2, dT)                   -> 기준온도 dT 이동 시 (C1', C2')
"""
from __future__ import annotations

import numpy as np

# Cabot Microelectronics US20170087688A1 Table 1B (freepatentsonline 원문 확인),
# knowledge/materials/pad-viscoelasticity-temp-frequency-dma.md §3.1 표 그대로.
# DMA 조건: TA Q800, 인장 multi-frequency controlled strain, 1 Hz, 30 µm, 5 °C/min.
CABOT_TABLE_1B = {
    "1A": {"T_C": [25, 50, 80], "E_MPa": [2127, 215, 5]},
    "1B": {"T_C": [25, 50, 80], "E_MPa": [1725, 204, 5]},
    "1C": {"T_C": [25, 50, 80], "E_MPa": [1413, 276, 5]},
    "1D": {"T_C": [25, 50, 80], "E_MPa": [1590, 317, 5]},
    "1E": {"T_C": [25, 50, 80], "E_MPa": [1474, 441, 8]},
    "D100": {"T_C": [25, 50, 80], "E_MPa": [1000, 141, 19]},
}


def e_pad_loglinear(T_C, T_points_C, E_points_MPa):
    """앵커점 사이를 log(E')-T 선형보간한 E'(T) [MPa].

    T_points_C는 오름차순, 3개 이상의 앵커점을 처리한다. 범위 밖(T < min 또는
    T > max)은 최근접 앵커값으로 clamp한다 — 노트가 Tg 근방 전이구간만 다루므로
    범위 밖 외삽은 물리적 근거가 없다(외삽 금지).

    Parameters
    ----------
    T_C : array_like
        조회 온도 [°C]
    T_points_C : array_like
        앵커 온도점 [°C], 오름차순
    E_points_MPa : array_like
        각 앵커점의 E' [MPa], 모두 양수

    Returns
    -------
    ndarray (또는 float, T_C가 스칼라면 스칼라)
    """
    T_points_C = np.asarray(T_points_C, dtype=float)
    E_points_MPa = np.asarray(E_points_MPa, dtype=float)
    if T_points_C.shape != E_points_MPa.shape:
        raise ValueError("T_points_C와 E_points_MPa의 길이가 다름")
    if T_points_C.size < 2:
        raise ValueError("앵커점이 2개 미만 — 보간 불가")
    if np.any(np.diff(T_points_C) <= 0):
        raise ValueError("T_points_C는 오름차순 정렬된 값이어야 함")
    if np.any(E_points_MPa <= 0):
        raise ValueError("E_points_MPa는 모두 양수여야 함(log 보간)")

    T_scalar_in = np.ndim(T_C) == 0
    T_arr = np.atleast_1d(np.asarray(T_C, dtype=float))
    T_clamped = np.clip(T_arr, T_points_C[0], T_points_C[-1])

    log_E = np.log(E_points_MPa)
    log_E_interp = np.interp(T_clamped, T_points_C, log_E)
    result = np.exp(log_E_interp)

    return result[0] if T_scalar_in else result


def e_pad_from_table(T_C, pad_id):
    """CABOT_TABLE_1B[pad_id]로 e_pad_loglinear 호출하는 편의 함수."""
    if pad_id not in CABOT_TABLE_1B:
        raise ValueError(f"알 수 없는 pad_id: {pad_id} (가능: {sorted(CABOT_TABLE_1B)})")
    row = CABOT_TABLE_1B[pad_id]
    return e_pad_loglinear(T_C, row["T_C"], row["E_MPa"])


def wlf_log_aT(T, Tr, C1=17.44, C2=51.6):
    """WLF shift factor log10(a_T) = -C1*(T-Tr) / (C2+(T-Tr)).

    근거: knowledge/materials/pad-viscoelasticity-temp-frequency-dma.md §2, §6(1).
    기본값 C1=17.44, C2=51.6 K는 WLF 1955(doi:10.1021/ja01619a008) 초록의
    Tr=Tg 보편상수 — **CMP PU 전용으로 피팅된 값이 아니다**. Tg 이상(≥ Tg) 구간에서만
    쓸 것(노트 §2.1: Tg 아래는 Arrhenius형이 필요, WLF 적용 대상이 아님).
    """
    return -C1 * (T - Tr) / (C2 + (T - Tr))


def wlf_reparametrize(C1, C2, dT):
    """기준온도를 dT만큼 올릴 때 재매개화: (C1', C2') = (C1*C2/(C2+dT), C2+dT).

    근거: 노트 §2, §6(1). 두 상수쌍은 독립 데이터가 아니라 같은 WLF 식의 기준온도
    이동에 따른 재표기임을 나타낸다.
    """
    C1_new = C1 * C2 / (C2 + dT)
    C2_new = C2 + dT
    return C1_new, C2_new


def _self_test() -> bool:
    results = []

    # --- (1) WLF 재매개화: (17.44, 51.6) + dT=50 -> (8.86, 101.6), 0.03% 이내 ---
    C1_calc, C2_calc = wlf_reparametrize(17.44, 51.6, 50.0)
    ok1 = abs(C1_calc - 8.86) < 0.01 and abs(C2_calc - 101.6) < 1e-9
    results.append(("§6(1) WLF 재매개화 (17.44,51.6)+dT50 -> (8.86,101.6)", ok1,
                     f"C1'={C1_calc:.3f}, C2'={C2_calc}"))

    # --- (2) shift 항등식: 두 매개화가 같은 상대 shift를 주는지 ---
    Tg = 0.0
    ok2 = True
    for T in (Tg + 60, Tg + 80, Tg + 100):
        lhs = wlf_log_aT(T, Tg, 17.44, 51.6) - wlf_log_aT(Tg + 50, Tg, 17.44, 51.6)
        rhs = wlf_log_aT(T, Tg + 50, C1_calc, C2_calc)
        ok2 = ok2 and abs(lhs - rhs) < 1e-9
    results.append(("§6(1) shift 항등식 수치 확인", ok2, "재매개화 두 곡선 일치"))

    # --- (3) 60°C, Tg=43.6°C 에서 log_aT가 -4.3~-4.1 사이 ---
    la = wlf_log_aT(60.0, 43.6)
    ok3 = -4.3 < la < -4.1
    results.append(("§6(1) log_aT(60°C, Tg=43.6°C) in (-4.3,-4.1)", ok3, f"{la:.3f}"))

    # --- (4) Cabot Table 1B 앵커점 정확 재현 (6개 패드 x 3개 앵커점) ---
    ok4 = True
    for pad_id, row in CABOT_TABLE_1B.items():
        for T, E in zip(row["T_C"], row["E_MPa"]):
            ok4 = ok4 and abs(e_pad_from_table(float(T), pad_id) - E) < 1e-9
    results.append(("§3.1 Cabot Table 1B 앵커점 정확 재현 (6패드x3점)", ok4, "모든 앵커점 오차 0"))

    # --- (5) 중간값 보간 sanity: 50°C가 로그선형 공식과 일치 ---
    row = CABOT_TABLE_1B["1D"]
    manual = np.exp(np.interp(50.0, row["T_C"], np.log(row["E_MPa"])))
    ok5 = abs(e_pad_from_table(50.0, "1D") - manual) < 1e-9
    results.append(("§1 중간값(50°C) 로그선형 공식 일치", ok5, f"{manual:.3f} MPa"))

    # --- (6) 범위 밖 clamp ---
    ok6 = (e_pad_from_table(10.0, "1D") == e_pad_from_table(25.0, "1D")
           and e_pad_from_table(100.0, "1D") == e_pad_from_table(80.0, "1D"))
    results.append(("범위 밖 clamp (10°C->25°C, 100°C->80°C)", ok6, "clamp 확인"))

    print("=== pad_viscoelastic_temperature.py self-test ===")
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
