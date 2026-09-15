"""
Greenwood-Williamson(GW) 통계적 asperity 접촉모델 + Hertz 단일접촉 공식.

지식 근거: knowledge/materials/hertz-gw-contact-mechanics.md
  - Hertz: Zhu, "Tutorial on Hertz Contact Stress" (Univ. Arizona OPTI521, 2012)
  - GW: Greenwood & Williamson 1966 (Proc. R. Soc. A 295) 표준 정식화,
    2차 교차검증: Yang et al. 2024 PMC11051262 (CMP 패드 asperity, 지수/로그정규 분포),
    "Rough Surface Contact Modelling—A Review" (Lubricants/MDPI, 2022) — 선형 A_r-W 관계.

이 모듈은 아직 preston.py/kinematics.py에 연결하지 않는다 (Lv2-2에서 K_p 물리적 분해 예정).
목적: 지수분포 GW 모델의 해석적 결과(A_r ∝ W, 계수 = sqrt(π·R·β)/E*)를
수치 적분으로 재현해 문헌 주장("실접촉면적은 하중에 선형 비례하며 분리거리 d와 무관")을
sanity check 한다.

실행: python3 gw_contact.py  → self-test 결과 stdout.
"""
import math
from scipy import integrate
import numpy as np


def hertz_force(delta, E_star, R):
    """단일 구형 asperity의 Hertz 힘. F = (4/3) E* sqrt(R) delta^(3/2), delta>=0."""
    if delta <= 0:
        return 0.0
    return (4.0 / 3.0) * E_star * math.sqrt(R) * delta ** 1.5


def hertz_contact_area(delta, R):
    """단일 asperity 접촉면적 (원형, a = sqrt(R*delta)) -> area = pi*R*delta."""
    if delta <= 0:
        return 0.0
    return math.pi * R * delta


def exp_pdf(z, beta):
    """asperity 높이분포 phi(z) = beta * exp(-beta z), z>=0."""
    return beta * math.exp(-beta * z) if z >= 0 else 0.0


def gw_numeric(d, beta, eta, A_n, E_star, R, z_max_factor=60):
    """
    GW 모델을 수치적분으로 계산 (지수분포 가정).
    반환: dict(n_contacts, A_r, W)  — 전부 SI 단위 가정.

    n = eta*A_n * ∫_d^∞ phi(z) dz
    A_r = pi*R*eta*A_n * ∫_d^∞ (z-d) phi(z) dz
    W   = (4/3)E*sqrt(R)*eta*A_n * ∫_d^∞ (z-d)^1.5 phi(z) dz
    """
    z_max = d + z_max_factor / beta  # 지수분포 꼬리 충분히 포함
    n_frac, _ = integrate.quad(lambda z: exp_pdf(z, beta), d, z_max)
    area_int, _ = integrate.quad(lambda z: (z - d) * exp_pdf(z, beta), d, z_max)
    force_int, _ = integrate.quad(lambda z: (z - d) ** 1.5 * exp_pdf(z, beta), d, z_max)

    n_contacts = eta * A_n * n_frac
    A_r = math.pi * R * eta * A_n * area_int
    W = (4.0 / 3.0) * E_star * math.sqrt(R) * eta * A_n * force_int
    return {"n_contacts": n_contacts, "A_r": A_r, "W": W}


def gw_analytic_ratio(beta, E_star, R):
    """
    지수분포의 memoryless 성질을 이용한 닫힌형 A_r/W 비율 (d에 무관).
    유도(지식노트 §4):
      ∫(z-d)phi dz = (1/beta) e^{-beta d}
      ∫(z-d)^1.5 phi dz = Gamma(2.5)/beta^1.5 * e^{-beta d}
      => A_r = pi*R*eta*A_n*(1/beta)*e^{-beta d}
         W   = (4/3)E*sqrt(R)*eta*A_n*Gamma(2.5)/beta^1.5 * e^{-beta d}
      => A_r/W = (pi*R/beta) / [ (4/3)E*sqrt(R)*Gamma(2.5)/beta^1.5 ]
               = (3*pi/(4*E*)) * sqrt(R) * beta^0.5 / Gamma(2.5)
      Gamma(2.5) = 3*sqrt(pi)/4  (표준값)
      => A_r/W = (3*pi/(4*E*)) * sqrt(R*beta) / (3*sqrt(pi)/4)
               = (pi/(E*)) * sqrt(R*beta) / sqrt(pi)
      A_r/W = sqrt(pi*R*beta) / E*

    ⚠ 2026-09-14 수정: 이전 독스트링 최종행이 (3*sqrt(pi)/(4*E*))*sqrt(R/beta) 로
      적혀 있었으나 **차원이 틀렸다**. A_r/W는 m^2/N = 1/Pa 여야 하는데
      sqrt(R/beta) = sqrt(m*m) = m 이라 m/Pa 가 된다. 올바른 형태는
      sqrt(pi*R*beta) 로, beta[1/m]가 곱해져 무차원이 되어야 1/Pa 가 맞는다.
      기본 파라미터(E*=1e9, R=5e-6, beta=1/0.3e-6)에서 구식은 1.63e-15,
      정식은 7.24e-09 로 **6자릿수 차이**가 난다.
      코드 gw_analytic_ratio() 구현과 그 위 유도 단계는 처음부터 올바랐고,
      최종 정리행만 오기였다 (수치검증이 통과해 온 이유).

    아래 수치검증에서 이 폐형식과 gw_numeric() 결과의 A_r/W을 비교한다.
    """
    gamma_2p5 = 0.75 * math.sqrt(math.pi)  # Gamma(5/2) = (3/4)*sqrt(pi), 표준값
    ratio = (math.pi * R / 1.0) / ((4.0 / 3.0) * E_star * math.sqrt(R) * gamma_2p5 / beta ** 0.5)
    # 위 식은 e^{-beta d} 항이 분자분모 상쇄되어 사라진 것 (d-무관 핵심 결과)
    return ratio


def plasticity_index(E_star, H, sigma_z, R):
    """
    Greenwood-Williamson 소성지수 psi = (E*/H) * sqrt(sigma_z/R).
    psi < 0.6 이면 대체로 탄성 접촉 지배, psi > 1 이면 소성 접촉 지배로 통상 해석됨
    (Johnson, Contact Mechanics 1985, Ch.13 표준 판정기준 — 2차 출처 교차검증 필요, 미검증 표기).
    """
    return (E_star / H) * math.sqrt(sigma_z / R)


def _self_test():
    results = []

    # --- Test 1: Hertz 3/2승 비선형성 (u 2배 -> F는 2^1.5배) ---
    E_star = 1e9  # 1 GPa 등가탄성계수 (폴리우레탄 패드 오더, pad-viscoelasticity 노트 참조)
    R = 5e-6      # 5 um asperity 반경 (CMP 패드 asperity 전형 오더)
    F1 = hertz_force(1e-7, E_star, R)
    F2 = hertz_force(2e-7, E_star, R)
    ratio = F2 / F1
    expect = 2 ** 1.5
    ok1 = abs(ratio - expect) / expect < 1e-9
    results.append(("Hertz F~delta^1.5 스케일링 (2배 압입 -> 2^1.5=2.828배 힘)", ok1, f"{ratio:.6f} vs {expect:.6f}"))

    # --- Test 2: 접촉면적 a^2 = R*delta 관계 (area = pi*R*delta) 일관성 ---
    delta = 1.5e-7
    area = hertz_contact_area(delta, R)
    a = math.sqrt(area / math.pi)
    ok2 = abs(a ** 2 - R * delta) / (R * delta) < 1e-9
    results.append(("Hertz 접촉반경 a^2=R*delta 일관성", ok2, f"a^2={a**2:.3e} vs R*delta={R*delta:.3e}"))

    # --- Test 3: GW 지수분포 A_r/W 비율, 수치적분 vs 폐형식, d(분리거리) 3개 값에서 불변성 ---
    beta = 1.0 / 0.3e-6  # sigma_z = 0.3 um (패드 asperity 높이 표준편차 오더)
    eta = 1e11           # 1/m^2, asperity 밀도 오더 (전형적 거친표면 1e9~1e12 /m^2 범위)
    A_n = 1e-4           # 1 cm^2 명목접촉면적 (예시)
    ratios_numeric = []
    for d in [0.0, 0.2e-6, 0.5e-6]:
        r = gw_numeric(d, beta, eta, A_n, E_star, R)
        ratios_numeric.append(r["A_r"] / r["W"])
    analytic = gw_analytic_ratio(beta, E_star, R)
    max_dev = max(abs(rn - analytic) / analytic for rn in ratios_numeric)
    ok3 = max_dev < 1e-3
    results.append(
        ("GW 지수분포: A_r/W 비율이 d(분리거리)에 무관 + 폐형식 일치",
         ok3,
         f"numeric={ratios_numeric}, analytic={analytic:.6e}, max_dev={max_dev:.2e}")
    )

    # --- Test 4: A_r가 W에 대해 선형인지 (기울기 = analytic ratio) 직접 확인 ---
    d_fixed = 0.3e-6
    # d를 고정하고 eta(=asperity 밀도, 하중과 함께 스케일)를 바꿔 W, A_r 쌍을 생성
    etas = [0.5e11, 1e11, 2e11, 4e11]
    Ws, Ars = [], []
    for e in etas:
        r = gw_numeric(d_fixed, beta, e, A_n, E_star, R)
        Ws.append(r["W"]); Ars.append(r["A_r"])
    slope = np.polyfit(Ws, Ars, 1)[0]
    ok4 = abs(slope - analytic) / analytic < 1e-3
    results.append(("A_r vs W 선형회귀 기울기 = 폐형식 A_r/W", ok4, f"slope={slope:.6e} vs analytic={analytic:.6e}"))

    # --- Test 5: 소성지수 오더체크 (전형적 CMP 패드 조건에서 psi 계산, 오더만 확인) ---
    H = 50e6  # 50 MPa, 폴리우레탄 경도 오더 (문헌: Shore D60 폴리우레탄 대략 수십 MPa 압입경도, 미검증 오더값)
    psi = plasticity_index(E_star, H, 0.3e-6, R)
    ok5 = 0.01 < psi < 100  # 오더 범위 내인지만 확인(정밀 판정 아님)
    results.append(("소성지수 psi 오더 확인(참고용, 미검증 정밀도)", ok5, f"psi={psi:.3f}"))

    print("=== gw_contact.py self-test ===")
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
