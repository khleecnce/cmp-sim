"""CMP 슬러리 필름두께 스케일링 모델 — Thakurta et al. (2001) 3-D Reynolds 윤활이론의
정성적 재현 (전체 2-D PDE 수치해는 미이식, §7 지식노트 명시).

지식 근거: knowledge/physics/cmp-slurry-flow-lubrication-film-thickness.md
  - Thakurta, Borst, Schwendeman, Gutmann, Gill, "Three-Dimensional Chemical Mechanical
    Planarization Slurry Flow Model Based on Lubrication Theory",
    J. Electrochem. Soc. 148(4) G207-G214 (2001). DOI: 10.1149/1.1355691
    (papers/thakurta2001_slurry_flow_lubrication.pdf, 미러 사이트 경유 확보)

핵심 아이디어(원 논문 Eq.19):
    z0 = sqrt(2 * mu * omega2 * R1 * R2 / P_app)   [길이 스케일]
논문 Fig.6c는 h_min/z0가 무차원군 d0/z0의 함수로 수렴함을 보이고(웨이퍼/패드 각속도비,
반경비 고정 시), Fig.6a/b/7a/7b는 개별 파라미터(P_app, omega, mu, d0, k, c)에 대한
h_min의 정성적 방향(단조증가/감소/극값)을 보인다. 이 모듈은:
  1. z0 스케일 자체를 그대로 구현(무차원화 공식, 파라미터 조합 검증 가능)
  2. §5 지식노트 표의 8개 정성 부호(방향성)를 하나씩 대응하는 최소 물리 모델로 재현
     (전체 PDE 없이 "부호가 문헌과 일치하는가"만 확인 — 정성 sanity check)
  3. 웨이퍼 곡률(d0)의 비단조(극댓값 존재)는 명시적으로 이 모듈에서 재현(§5 표 항목 중
     유일하게 부호 반전이 있는 항목이라 별도 함수로 분리)

실행: python3 slurry_film_lubrication.py  → self-test PASS/FAIL 카운트.
"""
import math


# ---------------------------------------------------------------------------
# 1. 무차원 길이 스케일 z0 (Thakurta et al. Eq.19)
# ---------------------------------------------------------------------------
def z0_length_scale(mu, omega2_rad_s, R1, R2, P_app):
    """z0 = sqrt(2*mu*omega2*R1*R2 / P_app)  [m]
    mu: 슬러리 점도[Pa·s], omega2: 패드 각속도[rad/s], R1: 웨이퍼반경[m],
    R2: 웨이퍼중심-패드중심 거리[m], P_app: 인가압력[Pa]."""
    return math.sqrt(2.0 * mu * omega2_rad_s * R1 * R2 / P_app)


# ---------------------------------------------------------------------------
# 2. 정성적 h_min 스케일링 모델 (§5 지식노트 표의 부호를 재현하는 최소 모델)
#    실제 논문은 2-D 비선형 Reynolds PDE + 뉴턴법으로 h_min을 계산하지만,
#    여기서는 "필름두께 ~ z0 * f(무차원군)" 형태의 monotone 근사로 부호만 재현한다.
# ---------------------------------------------------------------------------
def h_min_scaling(mu, U, P_app, k_porosity=0.0, c_compress=0.0):
    """정성 스케일링: h_min ~ z0-형 항 * (다공성 감쇠) * (압축성 감쇠).
    U: 웨이퍼-패드 상대속도[m/s] (= omega*R2, 케이스 세팅에 따라 대체 가능)
    문헌 §5: h_min은 (U/P_app)^(1/2)에 비례(단조증가), 점도 mu에도 비례(단조증가),
    다공성 k·압축성 c가 커지면 h_min이 감소(Fig.8a,b) — 두 감쇠항은 (1+k'), (1+c')
    형태의 단조감소 인자로 근사(정성 부호만 목적, 논문의 정량 곡선 형태 아님)."""
    if P_app <= 0:
        raise ValueError("P_app > 0 이어야 함")
    base = mu * math.sqrt(U / P_app)  # (U/P_app)^(1/2)에 비례 + 점도 비례(둘 다 단조증가)
    porosity_damping = 1.0 / (1.0 + k_porosity)
    compress_damping = 1.0 / (1.0 + c_compress)
    return base * porosity_damping * compress_damping


def h_min_wafer_rotation_effect(omega1, omega2_fixed=1.0, alpha=1.0, beta=0.6):
    """§5 표: '웨이퍼 회전속도만 증가(패드 고정)'는 h_min을 감소시킨다(패드에 의한
    슬러리 유입 효과를 웨이퍼 자전이 상쇄) — 유일하게 회전방향이 반대효과인 항목.
    최소 모델: h_min ~ alpha*omega2_fixed - beta*omega1  (omega1 항이 상쇄 방향으로 작용).
    beta < alpha 가정(패드 유입 효과가 웨이퍼 상쇄효과보다 강함, 완전 상쇄는 아님)."""
    return alpha * omega2_fixed - beta * omega1


def h_min_curvature_effect(d0, d0_peak=10e-6, width=8e-6, amplitude=1.0):
    """§5 표: 웨이퍼 곡률(dome height) d0 증가 → h_min 극댓값 존재(비단조).
    최소 모델: 가우시안형 극대 함수로 "d0=d0_peak 근처에서 최댓값, 그 밖에서는 감소"
    라는 정성 형태(비단조, 극대 1개)만 재현 — 실제 물리적 형태(수렴유로+기울기보정
    상쇄)의 근사가 아니라 '극값이 존재한다'는 사실 자체를 확인하는 용도."""
    return amplitude * math.exp(-((d0 - d0_peak) ** 2) / (2 * width ** 2))


# ---------------------------------------------------------------------------
# self-test
# ---------------------------------------------------------------------------
def _tests():
    results = []

    def check(name, cond, detail=""):
        results.append((name, bool(cond), detail))

    # --- z0 스케일: 논문 샘플 케이스 근처 값으로 오더 확인 ---
    # mu=5e-3 Pa·s, omega2=60rpm=6.283 rad/s, R1=4in=0.1016m, R2=7in=0.1778m, P_app=21kPa
    mu = 5e-3
    omega2 = 60 * 2 * math.pi / 60.0  # 60rpm -> rad/s
    R1 = 4 * 0.0254
    R2 = 7 * 0.0254
    P_app = 21e3
    z0 = z0_length_scale(mu, omega2, R1, R2, P_app)
    check("z0 오더가 마이크로미터~수십 마이크로미터 (논문 h_min=36um과 같은 오더)",
          1e-6 < z0 < 1e-3, f"z0={z0*1e6:.2f} um")

    # --- z0 vs 논문 h_min 정량 대조 (느슨한 오더체크의 대체가 아니라 추가) ---
    # 지식노트 §5 앵커: 위 조건(d0=10um 포함)에서 논문 결과 h_min=36um.
    # z0는 h_min의 정확한 값이 아니라 무차원화 기준 스케일(§4)이므로, 비율 h_min/z0가
    # 상수 오더(O(1), 0.3~3배)인지를 확인한다. 범위를 벗어나면 억지로 범위를 넓히지 않고
    # FAIL 그대로 둔다(원인 미상으로 기록) — 할루시네이션 방지 규칙.
    # [2026-09-08 관측] z0=232.48um, ratio=0.1548 → 범위(0.3~3.0) 밖, 이 check는 FAIL 상태.
    #   z0가 논문 h_min보다 약 6.5배 큼. 원인 미상(Eq.19 인용 오류 가능성, 혹은 h_min/z0가
    #   d0/z0 무차원군의 함수(Fig.6c)라 d0=10um 조건에서 O(1)이 아닐 가능성 등 미확인).
    #   범위를 넓혀 통과시키지 않았음.
    h_min_lit = 36e-6
    ratio = h_min_lit / z0
    print(f"  z0={z0*1e6:.2f} um, 논문 h_min=36.00 um, ratio h_min/z0={ratio:.4f}")
    check("z0 정량 대조: 0.3 < h_min(논문 36um)/z0 < 3.0 (O(1) 스케일 비율)",
          0.3 < ratio < 3.0,
          f"ratio={ratio:.4f} — 범위 밖이면 원인 미상, 범위를 넓히지 말 것")

    # --- z0 단조성: P_app 증가 -> z0 감소 (분모에 있으므로) ---
    z0_lowP = z0_length_scale(mu, omega2, R1, R2, 10e3)
    z0_highP = z0_length_scale(mu, omega2, R1, R2, 40e3)
    check("z0: P_app 증가 -> 감소 (문헌: 압력증가->필름 얇아짐과 방향 일치)",
          z0_highP < z0_lowP, f"low={z0_lowP:.3e}, high={z0_highP:.3e}")

    # --- z0 단조성: omega2(패드속도) 증가 -> z0 증가 ---
    z0_slow = z0_length_scale(mu, 2 * math.pi, R1, R2, P_app)
    z0_fast = z0_length_scale(mu, 4 * math.pi, R1, R2, P_app)
    check("z0: 패드속도 증가 -> 증가 (문헌: 속도증가->필름 두꺼워짐과 방향 일치)",
          z0_fast > z0_slow, f"slow={z0_slow:.3e}, fast={z0_fast:.3e}")

    # --- h_min_scaling: P_app 증가 -> 감소 ---
    h_lowP = h_min_scaling(mu, 0.75, 10e3)
    h_highP = h_min_scaling(mu, 0.75, 40e3)
    check("h_min_scaling: P_app 증가 -> 감소 (Fig.6a 방향)",
          h_highP < h_lowP, f"low={h_lowP:.3e}, high={h_highP:.3e}")

    # --- h_min_scaling: U(속도) 증가 -> 증가 ---
    h_slowU = h_min_scaling(mu, 0.3, P_app)
    h_fastU = h_min_scaling(mu, 1.2, P_app)
    check("h_min_scaling: 상대속도 증가 -> 증가 (Fig.6a 방향)",
          h_fastU > h_slowU, f"slow={h_slowU:.3e}, fast={h_fastU:.3e}")

    # --- h_min_scaling: 점도 증가 -> 증가 ---
    h_lowmu = h_min_scaling(1e-3, 0.75, P_app)
    h_highmu = h_min_scaling(1e-2, 0.75, P_app)
    check("h_min_scaling: 점도 증가 -> 증가 (Fig.6b 방향)",
          h_highmu > h_lowmu, f"low={h_lowmu:.3e}, high={h_highmu:.3e}")

    # --- h_min_scaling: 다공성 k 증가 -> 감소 (Fig.8a) ---
    h_k0 = h_min_scaling(mu, 0.75, P_app, k_porosity=0.0)
    h_k1 = h_min_scaling(mu, 0.75, P_app, k_porosity=2.0)
    check("h_min_scaling: 패드 다공성 증가 -> 감소 (Fig.8a 방향)",
          h_k1 < h_k0, f"k=0: {h_k0:.3e}, k=2: {h_k1:.3e}")

    # --- h_min_scaling: 압축성 c 증가 -> 감소 (Fig.8b) ---
    h_c0 = h_min_scaling(mu, 0.75, P_app, c_compress=0.0)
    h_c1 = h_min_scaling(mu, 0.75, P_app, c_compress=2.0)
    check("h_min_scaling: 패드 압축성 증가 -> 감소 (Fig.8b 방향)",
          h_c1 < h_c0, f"c=0: {h_c0:.3e}, c=2: {h_c1:.3e}")

    # --- 웨이퍼 자전 상쇄효과: omega1 증가 -> h_min(대리량) 감소 ---
    h_rot_low = h_min_wafer_rotation_effect(omega1=0.2)
    h_rot_high = h_min_wafer_rotation_effect(omega1=2.0)
    check("웨이퍼 회전속도 증가(패드 고정) -> 감소 (Fig.7a 반대효과 방향)",
          h_rot_high < h_rot_low, f"low_omega1={h_rot_low:.3f}, high_omega1={h_rot_high:.3f}")

    # --- 곡률 극값 존재 확인 (비단조) ---
    d0_values = [1e-6, 5e-6, 10e-6, 15e-6, 25e-6]
    h_curv = [h_min_curvature_effect(d0) for d0 in d0_values]
    imax = h_curv.index(max(h_curv))
    check("웨이퍼 곡률 h_min: 내부(양끝 아님)에서 극댓값 존재 (Fig.7b 비단조성)",
          0 < imax < len(d0_values) - 1, f"imax={imax}, values={[f'{v:.3f}' for v in h_curv]}")

    # 출력
    npass = sum(1 for _, c, _ in results if c)
    for name, cond, detail in results:
        print(f"  [{'PASS' if cond else 'FAIL'}] {name}"
              + (f"  ({detail})" if detail else ""))
    print(f"\n{npass}/{len(results)} PASS")
    return npass == len(results)


if __name__ == "__main__":
    ok = _tests()
    raise SystemExit(0 if ok else 1)
