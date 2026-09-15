"""
GW 모델 역문제: 명목압력 P -> 힘평형을 만족하는 분리거리 d -> 실접촉압력/접촉점수.

지식 근거: knowledge/materials/gw-nominal-vs-local-pressure.md
  - Yang et al. 2024 PMC11051262 (Eq.20 MRR 3-모드 가중합 = "접촉점수 증가"가 MRR의 1차 경로)
  - GW 1966 A_r∝W 하중무관 비율(원논문 미확보, gw_contact.py Lv2-1 폐형식 유도로 대체검증)

이 모듈은 tier2_physics/gw_contact.py의 gw_numeric()을 그대로 재사용한다(중복 재구현 금지).
목적: "명목압력을 올리면 실접촉압력(p_r=W/A_r)은 거의 안 변하고 접촉점 수(n)가 늘어난다"는
지식노트 §2의 정성적 결론을 수치로 확인(sanity check). preston.py에는 아직 연결하지 않는다
(Lv3-2에서 Kp의 물리적 분해로 정식 연결 예정 — 이번엔 GW 역문제 풀이 골격만 완성).

실행: python3 gw_pressure_solve.py -> self-test 결과 stdout.
"""
import math
from scipy.optimize import brentq

from gw_contact import gw_numeric, gw_analytic_ratio


def solve_separation(P_nominal, A_n, beta, eta, E_star, R, d_bracket=None):
    """
    명목압력 P_nominal(Pa)을 만족하는 분리거리 d를 이분법(Brent)으로 구한다.
    W(d) = gw_numeric(d, ...)["W"] 는 d의 단조감소함수이므로 유일해 존재.
    d_bracket: (d_lo, d_hi) 탐색구간, 없으면 sigma_z(=1/beta) 오더로 자동 설정.
    반환: d (m)
    """
    W_target = P_nominal * A_n

    def f(d):
        return gw_numeric(d, beta, eta, A_n, E_star, R)["W"] - W_target

    if d_bracket is None:
        sigma_z = 1.0 / beta
        d_lo, d_hi = -5 * sigma_z, 30 * sigma_z
    else:
        d_lo, d_hi = d_bracket

    # d_lo에서 W(d_lo) > W_target, d_hi에서 W(d_hi) < W_target 이어야 브라켓 성립
    f_lo, f_hi = f(d_lo), f(d_hi)
    if f_lo * f_hi > 0:
        # 브라켓 확장 (자동 안전장치)
        d_hi = d_lo + (d_hi - d_lo) * 4
        f_hi = f(d_hi)
        if f_lo * f_hi > 0:
            raise RuntimeError(f"브라켓 실패: f(d_lo)={f_lo:.3e}, f(d_hi)={f_hi:.3e}")

    d_star = brentq(f, d_lo, d_hi, xtol=1e-15, rtol=1e-12)
    return d_star


def local_contact_state(P_nominal, A_n, beta, eta, E_star, R):
    """
    명목압력에서 분리거리 d를 풀고, 그 결과로 실접촉압력 p_r=W/A_r, 접촉점수 n을 계산.
    반환: dict(d, n_contacts, A_r, W, p_r_mean, contact_area_fraction)
    """
    d = solve_separation(P_nominal, A_n, beta, eta, E_star, R)
    r = gw_numeric(d, beta, eta, A_n, E_star, R)
    p_r_mean = r["W"] / r["A_r"] if r["A_r"] > 0 else float("inf")
    return {
        "d": d,
        "n_contacts": r["n_contacts"],
        "A_r": r["A_r"],
        "W": r["W"],
        "p_r_mean": p_r_mean,
        "contact_area_fraction": r["A_r"] / A_n,
    }


def _self_test():
    results = []

    # 공통 파라미터 (gw_contact.py self-test와 동일 오더 재사용, 지식노트 §4 근거)
    E_star = 1e9
    R = 5e-6
    beta = 1.0 / 0.3e-6
    eta = 1e11
    A_n = 1e-4  # 1 cm^2

    # --- Test 1: solve_separation 왕복 검증 (d로 W 계산 -> 그 W를 다시 P로 넣어 d 복원) ---
    d_true = 0.4e-6
    W_at_d_true = gw_numeric(d_true, beta, eta, A_n, E_star, R)["W"]
    P_equiv = W_at_d_true / A_n
    d_recovered = solve_separation(P_equiv, A_n, beta, eta, E_star, R)
    err1 = abs(d_recovered - d_true) / d_true
    ok1 = err1 < 1e-6
    results.append(("solve_separation 왕복 정확도 (d->W->P->d)", ok1,
                     f"d_true={d_true:.6e}, d_recovered={d_recovered:.6e}, rel_err={err1:.2e}"))

    # --- Test 2: 명목압력 3구간(14/48/96 kPa, Lai 실험범위 오더)에서 p_r_mean 거의 불변 ---
    pressures = [14e3, 48e3, 96e3]  # Pa (14, 48, 96 kPa)
    states = [local_contact_state(P, A_n, beta, eta, E_star, R) for P in pressures]
    p_r_values = [s["p_r_mean"] for s in states]
    p_r_mean_avg = sum(p_r_values) / len(p_r_values)
    max_rel_dev = max(abs(v - p_r_mean_avg) / p_r_mean_avg for v in p_r_values)
    ok2 = max_rel_dev < 1e-3
    results.append(("6.9배 압력변화(14->96kPa)에도 평균 실접촉압력 p_r 거의 불변 (<0.1%)", ok2,
                     f"p_r={[f'{v:.4e}' for v in p_r_values]} Pa, max_rel_dev={max_rel_dev:.2e}"))

    # --- Test 3: p_r_mean이 analytic A_r/W 비율의 역수와 일치 (Lv2-1 폐형식과 정합) ---
    analytic_ratio = gw_analytic_ratio(beta, E_star, R)  # A_r/W
    expected_p_r = 1.0 / analytic_ratio
    err3 = abs(p_r_mean_avg - expected_p_r) / expected_p_r
    ok3 = err3 < 1e-3
    results.append(("p_r_mean = 1/(A_r/W 폐형식) 정합 (gw_contact.py Lv2-1과 교차검증)", ok3,
                     f"p_r_mean={p_r_mean_avg:.6e} vs 1/analytic_ratio={expected_p_r:.6e}, rel_err={err3:.2e}"))

    # --- Test 4: 접촉점수 n(d)는 압력에 거의 선형 (압력 3배 증가시 접촉점수도 근사 비례 증가) ---
    n_values = [s["n_contacts"] for s in states]
    # n/W 비율이 거의 상수인지 (n도 지수분포 memoryless로 W와 함께 선형 스케일)
    n_over_W = [n / s["W"] for n, s in zip(n_values, states)]
    n_over_W_avg = sum(n_over_W) / len(n_over_W)
    max_dev4 = max(abs(v - n_over_W_avg) / n_over_W_avg for v in n_over_W)
    ok4 = max_dev4 < 5e-2  # n/W는 e^{-beta d}가 분자분모에서 완전 상쇄되지 않아 A_r/W보다 느슨한 허용치
    results.append(("접촉점수 n도 하중 W에 대략 비례 (n/W 변동 <5%)", ok4,
                     f"n={[f'{v:.4e}' for v in n_values]}, n/W={[f'{v:.4e}' for v in n_over_W]}, max_dev={max_dev4:.2e}"))

    # --- Test 5: 압력 증가 -> 접촉면적비(A_r/A_n) 증가, 물리적으로 타당한 방향 ---
    fracs = [s["contact_area_fraction"] for s in states]
    ok5 = fracs[0] < fracs[1] < fracs[2]
    results.append(("압력 증가 -> 실접촉면적비 단조증가 (물리적 타당성)", ok5, f"fracs={fracs}"))

    print("=== gw_pressure_solve.py self-test ===")
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
