"""단일 연마입자 접촉역학 + 화학-기계 시너지 정량 (CMP 입자스케일).

지식 근거: knowledge/cmp/particle-wafer-interaction-mechanical-chemical-balance.md
  §2 (Hertz 탄성접촉), §3 (탄성/소성 전이), §4 (화학연화→plowing 체적 증폭)
구현 요청: slurry-chemist Lv2-2

계약 (엔진과의 경계):
  이 모듈은 아직 Preston Kp로의 정량 연결식이 없는 순수 함수 라이브러리다
  (노트 §6 명시, S17 frictional_heating_arrhenius와 동일 지위). engine/models.py에
  등록하지 않는다.

미검증 사항 (노트 §6 그대로, 지어내지 않음):
  - 입자당 하중 F(수 nN~수백 nN)는 활성입자 통계에서 나오는 값으로, 여기선
    오더만 채택하고 절대값은 실측 캘리브레이션 대상 — 미검증.
  - 경도 H(SiO2 8-9 GPa, Cu 1-2 GPa, 연화막 <1 GPa)는 나노압입 2차 인용 오더값.
    §4 시너지 배수(4배·8배)는 H 비율에 대한 상대적·해석적 결과(delta∝1/H, V∝H^-1.5)라
    정확하지만, 실제 연화 정도는 슬러리별 미검증.
  - Luo-Dornfeld MRR∝P^0.5·V의 지수는 원문(유료) 폐형식 유도를 직접 재현하지 못하고
    DOI 실존확인 + 2차 인용으로만 확인. 이 모듈은 그 미시 구성요소(단일입자 소성
    plowing)만 독립 재현한다.
  - plowing 홈 단면 A_f 근사(구형 압자, delta<<R)는 절삭효율 1(파낸 것 전부 제거)
    가정 — 실제 ploughing vs cutting 구분은 미해결.

함수:
  effective_modulus(E1, nu1, E2, nu2)              -> E* [Pa]
  single_particle_elastic_contact(F, R, E_star)    -> (a, delta, p_max)
  plastic_plowing(F, R, H)                         -> (delta_p, A_f)
  chemomechanical_amplification(H_hard, H_soft, F, R) -> dict(depth_ratio, volume_ratio)
"""
from __future__ import annotations

import math


def effective_modulus(E1: float, nu1: float, E2: float, nu2: float) -> float:
    """등가탄성계수 E*. 1/E* = (1-nu1^2)/E1 + (1-nu2^2)/E2.

    근거: 지식노트 §2.
    """
    return 1.0 / ((1 - nu1 ** 2) / E1 + (1 - nu2 ** 2) / E2)


def single_particle_elastic_contact(F: float, R: float, E_star: float) -> tuple[float, float, float]:
    """단일 연마입자 Hertz 탄성접촉. F[N], R[m], E_star[Pa] -> (a, delta, p_max)[m, m, Pa].

    근거: 지식노트 §2.
      a = (3FR/4E*)^(1/3)
      delta = a^2/R
      p_max = 0.4*(E*^2 F/R^2)^(1/3)
    """
    a = (3 * F * R / (4 * E_star)) ** (1 / 3)
    delta = a ** 2 / R
    p_max = 0.4 * (E_star ** 2 * F / R ** 2) ** (1 / 3)
    return a, delta, p_max


def plastic_plowing(F: float, R: float, H: float) -> tuple[float, float]:
    """소성 압입(plowing). F[N], R[m], H[Pa] -> (delta_p, A_f)[m, m^2].

    근거: 지식노트 §4.
      F = H*pi*a_p^2  ⟹  a_p = sqrt(F/(pi*H))
      delta_p = a_p^2/(2R) = F/(2*pi*R*H)
      A_f = (4/3)*sqrt(2R)*delta_p^1.5
    """
    a_p = math.sqrt(F / (math.pi * H))
    delta_p = a_p ** 2 / (2 * R)
    A_f = (4 / 3) * math.sqrt(2 * R) * delta_p ** 1.5
    return delta_p, A_f


def chemomechanical_amplification(H_hard: float, H_soft: float, F: float, R: float) -> dict:
    """경질(H_hard)->연화(H_soft) 전이 시 압입/체적 증폭비.

    근거: 지식노트 §4 (H 4배↓ → depth 4배, volume 8배 재현의 일반화).
    """
    delta_hard, A_hard = plastic_plowing(F, R, H_hard)
    delta_soft, A_soft = plastic_plowing(F, R, H_soft)
    return {
        "depth_ratio": delta_soft / delta_hard,
        "volume_ratio": A_soft / A_hard,
    }


def _self_test() -> bool:
    results = []

    # --- Test 1: E* (SiO2-SiO2) ---
    Estar = effective_modulus(73e9, 0.17, 73e9, 0.17)
    ok1 = abs(Estar / 1e9 - 37.6) < 0.5
    results.append(("E* SiO2-SiO2 ~= 37.6 GPa", ok1, f"{Estar/1e9:.2f} GPa"))

    # --- Test 2: 대표값 F=50nN 정밀 대조 (접촉응력·압입깊이) ---
    R = 50e-9
    a, delta, pmax = single_particle_elastic_contact(50e-9, R, Estar)
    ok2 = abs(pmax / 1e9 - 1.22) < 0.05 and abs(delta * 1e9 - 0.271) < 0.01
    results.append(("F=50nN: p_max~=1.22GPa, delta~=0.271nm", ok2,
                     f"p_max={pmax/1e9:.3f} GPa, delta={delta*1e9:.3f} nm"))

    # --- Test 3: 접촉응력 GPa 오더 / 압입 sub-nm 오더 (F=10/50/100nN) ---
    order_ok = True
    detail = []
    for F in (10e-9, 50e-9, 100e-9):
        a, d, p = single_particle_elastic_contact(F, R, Estar)
        detail.append(f"F={F*1e9:.0f}nN p={p/1e9:.2f}GPa d={d*1e9:.3f}nm")
        if not (0.5e9 < p < 5e9 and 0.05e-9 < d < 1e-9):
            order_ok = False
    results.append(("접촉응력 GPa 오더 / 압입 sub-nm 오더 (F=10,50,100nN)", order_ok, "; ".join(detail)))

    # --- Test 4: 화학연화 H 4배↓ -> depth 4배, volume 8배 ---
    amp = chemomechanical_amplification(2.0e9, 0.5e9, 50e-9, R)
    ok4 = abs(amp["depth_ratio"] - 4.0) < 0.01 and abs(amp["volume_ratio"] - 8.0) < 0.05
    results.append(("H 4배↓ -> depth_ratio~=4.0, volume_ratio~=8.0", ok4, str(amp)))

    # --- Test 5: 하중 2배 -> 제거체적 2^1.5배 ---
    _, A1 = plastic_plowing(50e-9, R, 1e9)
    _, A2 = plastic_plowing(100e-9, R, 1e9)
    ratio = A2 / A1
    ok5 = abs(ratio - 2 ** 1.5) < 0.02
    results.append(("하중 2배 -> 제거체적 2^1.5배", ok5, f"ratio={ratio:.3f} vs {2**1.5:.3f}"))

    print("=== particle_chemomechanical_synergy.py self-test ===")
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
