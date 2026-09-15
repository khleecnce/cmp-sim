"""
Cu CMP 잔류 두께의 전기적(선저항) 추출 — 순수함수 라이브러리.

지식 근거: knowledge/cmp/product-wafer-proxy-metrics-virtual-metrology.md (wafer-type
Lv3-1) §3.1, §3.3, §6 verify (C)/(D) 블록. 이 모듈은 그 노트의 로직·문헌 숫자를 그대로
옮긴 것이며, 새로운 값을 도입하지 않는다. 사용된 문헌:
- Park, Tugbawa, Boning, Chung et al., "Electrical Characterization of Copper Chemical
  Mechanical Polishing," Proc. CMP-MIC (1999) — eq.1-3: R = Rs*L/W, T = rho*L/(R*W),
  라이너 보정 T_M = rho_Cu*L/(R*(W-2*T_L)) + T_L. §V.A: W=0.35 um, T_M~4000 A,
  T_L=250 A, rho_L=100 uOhm*cm(최악)일 때 R_L/R_Cu ~ 200, 병렬 무시 오차 <0.5%.
- Chang, Cao, Spanos, "Modeling the Electrical Effects of Metal Dishing Due to CMP for
  On-Chip Interconnect Optimization," IEEE TED 51(10) 1577-1583 (2004),
  doi.org/10.1109/TED.2004.834898 — 표 I (w=5/4/3/2/1.6/1.2/0.8/0.4 um 선폭별 dR%),
  Fig.6 dishing-radius segment 모델, 최소제곱 추출 R_dish ~ 40 um.

engine.py/models.py에 등록하지 않는다: Recipe에 전기 테스트(선저항 R, 테스트 구조
치수) 스키마가 없어 S17/S19 계열과 동일한 지위로 engine 미등록 상태다.

단위: R_ohm[Ohm], L/W/T_L/T_M[um], rho_*_uohm_cm[uOhm*cm]. rho(uOhm*cm)를 R(Ohm)*
길이(um) 조합과 맞추려면 uOhm*cm -> Ohm*um 변환계수 1e-2가 필요하다(1 uOhm*cm =
1e-6 Ohm*cm = 1e-6*1e4 Ohm*um = 1e-2 Ohm*um) — cu_thickness_from_resistance가 이를
반영한다. liner_parallel_resistance_ratio 등 면적비 계산은 rho 비율(무차원)만 쓰므로
uOhm*cm 그대로 노트 §6 (C)와 동일하게 둔다.

실행: python3 electrical_thickness_extraction.py -> self-test 결과 stdout.
"""
import math


def cu_thickness_from_resistance(R_ohm, L_um, W_um, T_L_um, rho_Cu_uohm_cm=2.0):
    """T_M = rho_Cu*L/(R*(W-2*T_L)) + T_L [um] (Park et al. 1999 eq.1-3, 라이너 보정판).

    rho_Cu_uohm_cm(uOhm*cm) -> Ohm*um 변환계수 1e-2 적용(모듈 docstring 참조).
    """
    return (rho_Cu_uohm_cm * 1e-2) * L_um / (R_ohm * (W_um - 2 * T_L_um)) + T_L_um


def liner_parallel_resistance_ratio(W_um, T_M_um, T_L_um, rho_L_uohm_cm, rho_Cu_uohm_cm):
    """R_L/R_Cu — 노트 §6 (C) ratio_RL_RCu 그대로 (Park et al. 1999 eq.2 단면적비 x 저항률비)."""
    A_Cu = (T_M_um - T_L_um) * (W_um - 2 * T_L_um)
    A_L = 2 * T_M_um * T_L_um + (W_um - 2 * T_L_um) * T_L_um
    return (rho_L_uohm_cm / rho_Cu_uohm_cm) * (A_Cu / A_L)


def liner_neglect_error_fraction(R_L_over_R_Cu):
    """라이너를 무시하고 Cu 단독으로 두께를 추출할 때의 상대 오차 = 1/(1+R_L/R_Cu) (Park et al. 1999 §V.A)."""
    return 1.0 / (1.0 + R_L_over_R_Cu)


def is_liner_negligible(R_L_over_R_Cu, threshold=100.0):
    """R_L/R_Cu >= threshold면 라이너 무시가 안전(True), 미만이면 경고 대상(False)."""
    return R_L_over_R_Cu >= threshold


def dishing_delta_R_fraction(w_um, R_dish_um=40.0, t_um=0.5):
    """dishing에 의한 선저항 증가율 [%] — Chang et al. 2004 Fig.6 segment 모델, 노트 §6 (D) 그대로.

    단면적 = 직사각형(w*t) - 원호 segment(R_dish, w). R_dish~40 um는 표 I 최소제곱 추출값.
    """
    R = R_dish_um
    seg = R * R * math.asin(w_um / (2 * R)) - (w_um * R / 2) * math.sqrt(1 - (w_um / (2 * R)) ** 2)
    return 100 * (1 / (1 - seg / (w_um * t_um)) - 1)


def _self_test():
    results = []

    # --- Test 1: R_L/R_Cu ~ 200 @ rho_Cu=2.0 (Park et al. 1999 §V.A) ---
    r_20 = liner_parallel_resistance_ratio(0.35, 0.40, 0.025, 100.0, 2.0)
    ok1 = bool(150 <= r_20 <= 250)
    results.append(("liner_parallel_resistance_ratio rho_Cu=2.0 ~200", ok1, f"r={r_20:.1f}"))

    # --- Test 2: 오차 <0.5% @ rho_Cu 1.7, 2.0 / 2.2에서 경계 초과 ---
    err_17 = liner_neglect_error_fraction(liner_parallel_resistance_ratio(0.35, 0.40, 0.025, 100.0, 1.7))
    err_20 = liner_neglect_error_fraction(liner_parallel_resistance_ratio(0.35, 0.40, 0.025, 100.0, 2.0))
    err_22 = liner_neglect_error_fraction(liner_parallel_resistance_ratio(0.35, 0.40, 0.025, 100.0, 2.2))
    ok2 = bool(err_17 < 0.005 and err_20 < 0.005 and err_22 > 0.005)
    results.append(("liner_neglect_error_fraction <0.5%(1.7,2.0), 2.2 경계 초과", ok2,
                     f"err17={err_17*100:.2f}%, err20={err_20*100:.2f}%, err22={err_22*100:.2f}%"))

    # --- Test 3: Park 예시 재현 R~177.8 Ohm -> T_M~0.4 um ---
    R_ohm = (2.0 * 1e-2) * 1000.0 / ((0.40 - 0.025) * (0.35 - 2 * 0.025))
    T_M = cu_thickness_from_resistance(R_ohm, 1000.0, 0.35, 0.025, rho_Cu_uohm_cm=2.0)
    ok3 = bool(abs(T_M - 0.40) < 1e-6)
    results.append(("cu_thickness_from_resistance 역산 일치", ok3, f"R={R_ohm:.2f} Ohm, T_M={T_M:.4f} um"))

    # --- Test 4: 라이너 보정이 단순 근사(T=rho*L/(R*W))보다 두껍게 나옴(W-2T_L<W) ---
    T_lined = cu_thickness_from_resistance(R_ohm, 1000.0, 0.35, 0.025, rho_Cu_uohm_cm=2.0)
    T_naive = (2.0 * 1e-2) * 1000.0 / (R_ohm * 0.35)
    ok4 = bool(T_lined > T_naive)
    results.append(("라이너 보정 T > naive 근사", ok4, f"T_lined={T_lined:.4f}, T_naive={T_naive:.4f}"))

    # --- Test 5: is_liner_negligible 임계값 ---
    ok5 = bool(is_liner_negligible(200.0, 100.0) is True and is_liner_negligible(50.0, 100.0) is False)
    results.append(("is_liner_negligible 100 임계값", ok5, "200->True, 50->False"))

    # --- Test 6: dishing_delta_R_fraction(5.0) ~ 11.6, 문헌 9.39, 30%이내 ---
    d5 = dishing_delta_R_fraction(5.0)
    ok6 = bool(abs(d5 - 9.39) / 9.39 < 0.30)
    results.append(("dishing_delta_R_fraction(5.0) vs 9.39% (30%이내)", ok6, f"d5={d5:.2f}%"))

    # --- Test 7: 표 I w>=2 um 전부 30% 이내 ---
    tableI = [(5, 9.39), (4, 6.67), (3, 4.74), (2, 1.56)]
    ok7 = all(abs(dishing_delta_R_fraction(w) - m) / m < 0.30 for w, m in tableI)
    results.append(("dishing_delta_R_fraction 표I w>=2um 30%이내", ok7,
                     [round(dishing_delta_R_fraction(w), 2) for w, _ in tableI]))

    # --- Test 8: w=0.4 um은 모델 범위 밖(모델값 << 문헌 1.14%) ---
    d04 = dishing_delta_R_fraction(0.4)
    ok8 = bool(d04 < 0.2)
    results.append(("dishing_delta_R_fraction(0.4) < 0.2% (모델 밖, 문헌 1.14%)", ok8, f"d04={d04:.4f}%"))

    print("=== electrical_thickness_extraction.py self-test ===")
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
