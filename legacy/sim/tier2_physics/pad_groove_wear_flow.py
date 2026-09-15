"""
그루브 마모(깊이 감소)에 따른 슬러리 유동 상태 변화 — 순수함수 라이브러리.

지식 근거: knowledge/materials/pad-groove-wear-flow-change-end-of-life.md (pad-structure
Lv3-2) §2, §4, §5. 이 모듈은 그 노트 §5 verify (A)/(A')/(B)/(D)/(E) 블록의 로직·숫자를
그대로 옮긴 것이며, 새로운 문헌 숫자를 도입하지 않는다. 사용된 문헌·특허:
- US8192257B2 (Micron, "Method of manufacture of constant groove depth pads", 2012) — 초기
  깊이 250 μm, 컷레이트 0.25 μm/wafer, 수명 600-800 wafers.
- US11938584B2 (CMC Materials/Cabot, "...constant groove volume", 2024) — 그루브 부피
  사용 가능 상한 80%, 하한 20%.
- Mu et al. (2016), Microelectron. Eng. 157, 60-63, doi.org/10.1016/j.mee.2016.02.035 —
  V_total = V_land + V_groove 반응기 모델, Table 2 (3 PSI, 필름두께 15 μm, 200 mm 웨이퍼).
- Irfan et al. (2025), J. Manuf. Mater. Process. 9(3), 95,
  doi.org/10.3390/jmmp9030095 — §2.3 기하(w=0.5 mm, d=0.75→0.25 mm), CFD 정성 경향.
- Liu et al. (2024), ECS J. Solid State Sci. Technol., doi.org/10.1149/2162-8777/ad83ef —
  초록만(신선 슬러리 분율 850 μm 72.34% → 250 μm 100.00%); 이 모듈에는 직접 반영하지
  않는다(§2.1의 CSTR 외삽은 노트의 모델 해석일 뿐 별도 검증 함수로 옮기지 않음).

engine.py/models.py에 등록하지 않는다: Recipe에 그루브 초기깊이·컨디셔닝 절대시간(t)·
q_actual 필드가 없어 S24(pad_groove_eol.py)와 동일한 지위로 engine 미등록 상태다.

실행: python3 pad_groove_wear_flow.py -> self-test 결과 stdout.
"""
import math


def groove_depth_um(D0_um, cut_rate_um_per_unit, t):
    """D(t) = D0 - cut_rate*t [μm], 0 미만으로는 내려가지 않게 clamp (물리적 하한)."""
    return max(0.0, D0_um - cut_rate_um_per_unit * t)


def residual_depth_fraction(D_um, D0_um):
    """잔존 깊이비 D/D0 (무차원)."""
    return D_um / D0_um


def wear_stage(D_um, D0_um):
    """노트 §4 표의 3단계 유동 상태 플래그.

    잔존비 >= 0.7 -> "initial", 0.35 <= 잔존비 < 0.7 -> "mid", 잔존비 < 0.35 -> "end_of_life".
    이 임계값(0.7/0.35)은 노트 §4의 모델 제안이며 Liu/Irfan 0.29-0.33, Cabot 0.20,
    Micron 0.2-0.4의 범위 안에서 이 에이전트가 고른 값 — PROVISIONAL.
    """
    frac = residual_depth_fraction(D_um, D0_um)
    if frac >= 0.7:
        return "initial"
    if frac >= 0.35:
        return "mid"
    return "end_of_life"


def slurry_volumes_cm3(D_um, GFQ, h_land_um, wafer_diameter_mm=200.0):
    """(V_land, V_groove, V_total) [cm3] — Mu 2016 반응기 모델의 기하 재현.

    V_land = (1-GFQ) * A_wafer_cm2 * h_land_cm, V_groove = GFQ * A_wafer_cm2 * D_cm.
    노트 §5 (D) 검증 블록의 vl_calc/vg_calc와 정확히 같은 형태(Mu 2016 Table 2 재현).
    """
    radius_cm = (wafer_diameter_mm / 2.0) / 10.0
    A_wafer_cm2 = math.pi * radius_cm ** 2
    h_land_cm = h_land_um * 1e-4
    D_cm = D_um * 1e-4
    V_land = (1 - GFQ) * A_wafer_cm2 * h_land_cm
    V_groove = GFQ * A_wafer_cm2 * D_cm
    V_total = V_land + V_groove
    return V_land, V_groove, V_total


def residence_time_s(D_um, GFQ, h_land_um, q_actual_cm3_per_s, wafer_diameter_mm=200.0):
    """MRT tau(D) = V_total(D) / q_actual [s] (Mu 2016 반응기 모델, 노트 §2.1/§5 D)."""
    _, _, V_total = slurry_volumes_cm3(D_um, GFQ, h_land_um, wafer_diameter_mm)
    return V_total / q_actual_cm3_per_s


def rectangular_channel_conductance(w_mm, h_mm):
    """직사각 덕트 Poiseuille 컨덕턴스(표준 급수해, 짧은 변을 h로 취함). 노트 §2.3/§5(E)."""
    w, h = w_mm, h_mm
    if h > w:
        w, h = h, w
    s = sum(math.tanh(n * math.pi * w / (2 * h)) / n ** 5 for n in range(1, 199, 2))
    return w * h ** 3 / 12 * (1 - 192 * h / (math.pi ** 5 * w) * s)


def conductance_ratio(D_um, D0_um, w_mm):
    """G(D)/G(D0) — 채널 컨덕턴스비, 깊이비보다 급하게 감소(노트 §2.3/§5 E, 자체 유도)."""
    return (rectangular_channel_conductance(w_mm, D_um / 1000.0)
            / rectangular_channel_conductance(w_mm, D0_um / 1000.0))


def micron_cabot_life_wafers(D1_um, wear_um_per_wafer, usable_fraction=0.80):
    """Cabot 80% 사용 가능 기준 대입 -> wafers (US11938584B2 80% x US8192257B2 250um/0.25um 조합, 노트 §5 A)."""
    return usable_fraction * D1_um / wear_um_per_wafer


def groove_wear_flow_state(D0_um, cut_rate_um_per_unit, GFQ, h_land_um, q_actual_cm3_per_s,
                            t, w_mm=0.5, wafer_diameter_mm=200.0):
    """시각 t에서의 그루브 마모·유동 상태 종합 dict.

    w_mm 기본값 0.5mm는 Irfan 2025 §2.3 기하값(문헌 근거)이며 컨덕턴스 계산 전용이다 —
    GFQ(면적비=폭/피치)와는 별개 축. 이 값이 없으면 컨덕턴스 계산이 불가능하다(그루브 폭
    자체는 GFQ=폭/피치 비율일 뿐 절대 mm가 아니므로, 컨덕턴스 계산에는 절대 폭이 필요).

    반환: {"D_um", "residual_fraction", "stage", "tau_s", "conductance_ratio",
           "V_land_cm3", "V_groove_cm3", "V_total_cm3"}
    """
    D_um = groove_depth_um(D0_um, cut_rate_um_per_unit, t)
    residual_fraction = residual_depth_fraction(D_um, D0_um)
    stage = wear_stage(D_um, D0_um)
    tau_s = residence_time_s(D_um, GFQ, h_land_um, q_actual_cm3_per_s, wafer_diameter_mm)
    cond_ratio = conductance_ratio(D_um, D0_um, w_mm)
    V_land, V_groove, V_total = slurry_volumes_cm3(D_um, GFQ, h_land_um, wafer_diameter_mm)
    return {
        "D_um": D_um,
        "residual_fraction": residual_fraction,
        "stage": stage,
        "tau_s": tau_s,
        "conductance_ratio": cond_ratio,
        "V_land_cm3": V_land,
        "V_groove_cm3": V_groove,
        "V_total_cm3": V_total,
    }


def _self_test():
    results = []

    # --- Test 1: US8192257B2 산술 소진 한계 1000 wafers ---
    N_full = 250.0 / 0.25
    ok1 = bool(abs(N_full - 1000) < 1e-9)
    results.append(("250/0.25 == 1000 wafers 산술 소진 한계", ok1, f"N_full={N_full}"))

    # --- Test 2: Cabot 80% 기준 -> 800 wafers = Micron 상한 ---
    N_cabot = micron_cabot_life_wafers(250.0, 0.25, 0.80)
    ok2 = bool(600 <= N_cabot <= 800 and abs(N_cabot - 800.0) < 1e-9)
    results.append(("micron_cabot_life_wafers(250, 0.25, 0.80) == 800", ok2, f"N_cabot={N_cabot}"))

    # --- Test 3: groove_depth_um 0 clamp ---
    D_over = groove_depth_um(250.0, 0.25, 2000.0)
    ok3 = bool(D_over == 0.0)
    results.append(("groove_depth_um clamp at 0", ok3, f"D={D_over}"))

    # --- Test 4: wear_stage 경계 ---
    ok4 = bool(wear_stage(70.0, 100.0) == "initial" and wear_stage(69.999, 100.0) == "mid"
               and wear_stage(35.0, 100.0) == "mid" and wear_stage(34.999, 100.0) == "end_of_life")
    results.append(("wear_stage 0.7/0.35 경계", ok4, "initial/mid/end_of_life 경계 확인"))

    # --- Test 5: Mu 2016 Table 2 Pad A 3PSI ---
    gfq_A = 300 / 1500
    V_land, V_groove, V_total = slurry_volumes_cm3(400.0, gfq_A, 15.0)
    ok5 = bool(abs(V_land - 0.38) / 0.38 < 0.03 and 0.03 < abs(V_groove - 2.66) / 2.66 < 0.07)
    results.append(("slurry_volumes_cm3 Pad A 3PSI 재현", ok5,
                     f"V_land={V_land:.3f} (목표 0.38), V_groove={V_groove:.3f} (목표 2.66)"))

    # --- Test 6: 컨덕턴스비 (Irfan 2025 기하) ---
    r50 = conductance_ratio(500.0, 750.0, 0.5)
    r25 = conductance_ratio(250.0, 750.0, 0.5)
    ok6 = bool(0.45 < r50 < 0.50 and 0.09 < r25 < 0.11)
    results.append(("conductance_ratio Irfan 2025 기하", ok6, f"r50={r50:.3f}, r25={r25:.3f}"))

    # --- Test 7: groove_wear_flow_state 종합 ---
    state = groove_wear_flow_state(400.0, 0.25, gfq_A, 15.0, 0.3141, t=600.0)
    ok7 = bool(abs(state["D_um"] - 250.0) < 1e-9 and state["stage"] == "mid")
    results.append(("groove_wear_flow_state 종합", ok7, f"D_um={state['D_um']}, stage={state['stage']}"))

    print("=== pad_groove_wear_flow.py self-test ===")
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
