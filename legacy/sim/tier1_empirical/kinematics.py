"""
CMP 회전식(rotary) 폴리셔 운동학 — 웨이퍼-패드 상대속도 분포.

담당 에이전트: process-integrator (Lv1-2)
근거 지식노트: knowledge/physics/cmp-kinematics-rotary.md
                knowledge/equipment/cmp-tool-architecture.md

────────────────────────────────────────────────────────────────────
모델
────────────────────────────────────────────────────────────────────
웨이퍼 중심 O_w, 플래튼(패드) 중심 O_p, 두 회전축 간 거리 r_cc.
웨이퍼 중심 기준 좌표계(x, y), y축은 O_w→O_p 반대 방향(문헌 관례).
각속도 ω_w(헤드), ω_p(플래튼) [rad/s], 둘 다 같은 부호(동일 방향 회전).

웨이퍼 위 점 P(x, y)에서 패드에 대한 상대속도 (Lai 2001, MIT PhD thesis Eq. 2.11):

    v_x = -(ω_w - ω_p) * y
    v_y =  (ω_w - ω_p) * x - ω_p * r_cc
    |v| = sqrt(v_x^2 + v_y^2)                          ... Eq. (2.10)

핵심 귀결 (Eq. 2.12):  ω_w = ω_p 이면
    v_x = 0,  v_y = -ω_p * r_cc  →  |v| = ω_p * r_cc  (웨이퍼 전면에서 동일)
즉 헤드-플래튼 RPM이 같으면 상대속도가 웨이퍼 전면에서 완전 균일하며,
그 방향은 웨이퍼 좌표계에서 ω_w/2π 주파수로 회전 → 등방성 폴리싱.

동등한 극좌표 표현 (Hasni et al. 2026, JJMIE Eq. 3):
    |v| = ω_p * r_cc * sqrt( (r*mu)^2 + 2*r*mu*cos(theta) + 1 )
    r = beta / R_w (무차원 반경),  mu = (R_w / r_cc) * (1 - Rs),  Rs = ω_w/ω_p
  두 표현은 동일하다: Lai식을 전개하면
    |v|^2 = (w_p r_cc)^2 [ (r*mu)^2 + 2 r*mu*cos(theta) + 1 ],  mu = (R_w/r_cc)(1-Rs)
  (dw = w_w - w_p 이므로 dw*r/(w_p r_cc) = -r*mu, 부호가 cos항에 흡수됨.)
  → 기준속도 v_ref = w_p * r_cc 대비 비균일도는 엣지(r=1)에서
        (max-min)/v_ref = |1+mu| - |1-mu| = 2*|mu|   (|mu| <= 1)
    실제 웨이퍼 면적평균 대비로는 평균이 v_ref보다 아주 조금 크므로
    (max-min)/mean 은 2|mu|보다 약간 작다 (mu=0.25에서 24.95% vs 25.00%).

────────────────────────────────────────────────────────────────────
검증 결과 (2026-09-03 실행, 이 파일 하단 self-test)
────────────────────────────────────────────────────────────────────
1) ω_w = ω_p (Rs=1.0), 300mm 웨이퍼(R_w=150mm), r_cc=200mm, 60/60 rpm:
   |v| = 1.256637 m/s = ω_p·r_cc 예측값과 정확히 일치,
   웨이퍼 전면 std = 0.00e+00, (max-min)/mean = 0.00e+00
   →  Lai(2001) Eq.(2.12) "헤드-플래튼 동속이면 상대속도 전면 균일" 재현 OK.
2) Rs != 1: (max-min)/(ω_p·r_cc) = 2|mu| 해석해와 상대오차 < 1e-12.
   50/60rpm → 25.0000%,  55/60 → 12.5000%,  66/60 → 15.0000%,  72/60 → 30.0000%.
   (면적평균 기준으로는 각각 24.95 / 12.49 / 14.99 / 29.92%로 살짝 작다.)
3) Cartesian(Lai Eq.2.11) ↔ 극좌표(JJMIE Eq.3) 최대 절대차 2.22e-16 m/s (동일식 확인).
4) Rs=1일 때 Preston 반경 프로파일 편차 0.00e+00 (완전 평탄),
   Rs=50/60일 때 edge/center 시간평균 MRR 비 = 1.00391 (엣지가 빠름).
   → RPM 불일치는 "엣지 fast" 형태의 WIWNU를 만든다는 정성적 결론과 일치.
5) ⚠️ 미검증/문헌 모순: JJMIE(2026)는 R_w=50mm, 웨이퍼/패드 59/71 rpm에서
   속도 범위 0.664~0.696 m/s(평균 0.680, ±2.4%)라 보고하나,
   같은 논문 Eq.(3)에 그 조건을 넣으면 mean=ω_p·r_cc=0.680 → r_cc=91.5mm,
   mu=(50/91.5)(1-59/71)=0.0924 → ±9.2%가 되어 약 4배 불일치한다.
   본 모듈은 Lai(MIT) 유도식을 정본으로 채택하고 JJMIE 보고수치는 채택하지 않음.
"""
from __future__ import annotations

import numpy as np

RPM = 2.0 * np.pi / 60.0  # rpm → rad/s


def rpm_to_rads(rpm: float) -> float:
    return rpm * RPM


def relative_velocity(x, y, omega_w: float, omega_p: float, r_cc: float):
    """웨이퍼 좌표 (x,y)[m]에서 패드 대비 상대속도 성분과 크기 [m/s].

    omega_w, omega_p: rad/s.  r_cc: 회전축 간 거리 [m].
    """
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    dw = omega_w - omega_p
    vx = -dw * y
    vy = dw * x - omega_p * r_cc
    return vx, vy, np.hypot(vx, vy)


def relative_speed_polar(r_norm, theta, omega_w: float, omega_p: float,
                         r_cc: float, R_w: float):
    """JJMIE(2026) Eq.(3) 형태의 극좌표 상대속도 크기 [m/s]."""
    Rs = omega_w / omega_p
    mu = (R_w / r_cc) * (1.0 - Rs)
    rm = np.asarray(r_norm, dtype=float) * mu
    return omega_p * r_cc * np.sqrt(rm**2 + 2.0 * rm * np.cos(theta) + 1.0)


def kinematic_number(R_w: float, r_cc: float, rpm_w: float, rpm_p: float) -> float:
    """운동학 수 mu = (R_w/r_cc)(1 - Rs).  |mu|가 속도 비균일도의 척도."""
    return (R_w / r_cc) * (1.0 - rpm_w / rpm_p)


def wafer_grid(R_w: float, n_r: int = 121, n_t: int = 360):
    """웨이퍼 원판 위 극좌표 격자 (엣지 r=R_w를 정확히 포함). 반환: (x, y, w).

    w = 면적 가중치(r dr dtheta 비례) — 면적평균을 올바르게 내기 위함.
    """
    r = np.linspace(0.0, R_w, n_r)
    t = np.linspace(0.0, 2 * np.pi, n_t, endpoint=False)
    R, T = np.meshgrid(r, t, indexing="ij")
    return R * np.cos(T), R * np.sin(T), R


def speed_stats(R_w: float, r_cc: float, rpm_w: float, rpm_p: float, n_r: int = 121):
    """웨이퍼 전면 상대속도 통계 (순간값; 회전대칭이라 시불변).

    nu_ref = (max-min)/v_ref, v_ref = w_p*r_cc  → 해석해 2|mu|와 정확히 일치.
    nu_range = (max-min)/면적평균  → 실무에서 쓰는 정의.
    """
    X, Y, W = wafer_grid(R_w, n_r)
    _, _, v = relative_velocity(X, Y, rpm_to_rads(rpm_w), rpm_to_rads(rpm_p), r_cc)
    v = v.ravel(); w = W.ravel()
    mean = float(np.average(v, weights=w))
    var = float(np.average((v - mean) ** 2, weights=w))
    v_ref = rpm_to_rads(rpm_p) * r_cc
    return {
        "mean": mean, "min": float(v.min()), "max": float(v.max()),
        "std": var ** 0.5,
        "nu_ref": float((v.max() - v.min()) / v_ref),
        "nu_range": float((v.max() - v.min()) / mean),
        "cv": float(var ** 0.5 / mean),
        "mu": kinematic_number(R_w, r_cc, rpm_w, rpm_p),
    }


def preston_mrr_profile(R_w: float, r_cc: float, rpm_w: float, rpm_p: float,
                        pressure_pa: float, kp: float, n_r: int = 41):
    """반경별 Preston MRR 프로파일 [m/s].  MRR(r) = kp * P * <|v|>_theta.

    시간평균: 웨이퍼가 자전하므로 반경 r의 점은 theta 전체를 균일히 훑는다
    (Lai Eq. 2.5의 등방성 논거) → theta 평균이 곧 시간평균.
    """
    rs = np.linspace(0.0, R_w, n_r)
    th = np.linspace(0.0, 2 * np.pi, 721, endpoint=False)
    ww, wp = rpm_to_rads(rpm_w), rpm_to_rads(rpm_p)
    out = []
    for r in rs:
        _, _, v = relative_velocity(r * np.cos(th), r * np.sin(th), ww, wp, r_cc)
        out.append(kp * pressure_pa * v.mean())
    return rs, np.array(out)


# ───────────────────────────── self-test ─────────────────────────────
def _selftest():
    ok = True

    def chk(name, cond, detail=""):
        nonlocal ok
        ok &= bool(cond)
        print(f"[{'PASS' if cond else 'FAIL'}] {name} {detail}")

    # 1) Rs = 1 → 완전 균일 (Lai Eq. 2.12)
    R_w, r_cc, rpm = 0.150, 0.200, 60.0
    s = speed_stats(R_w, r_cc, rpm, rpm)
    expect = rpm_to_rads(rpm) * r_cc
    chk("Rs=1 uniform speed", s["std"] < 1e-12 and abs(s["mean"] - expect) < 1e-12,
        f"|v|={s['mean']:.6f} m/s (예측 {expect:.6f}), std={s['std']:.2e}, NU={s['nu_range']:.2e}")

    # 2) 비균일도 = 2|mu| 해석식
    for rpm_w in (50.0, 55.0, 66.0, 72.0):
        s = speed_stats(R_w, r_cc, rpm_w, 60.0)
        pred = 2.0 * abs(s["mu"])
        chk(f"NU=2|mu| @ {rpm_w:.0f}/60rpm",
            abs(s["nu_ref"] - pred) / pred < 1e-12,
            f"수치 {s['nu_ref']*100:.4f}% vs 해석 {pred*100:.4f}% "
            f"(면적평균기준 {s['nu_range']*100:.3f}%)")

    # 3) Cartesian(Lai) ↔ Polar(JJMIE) 동등성
    th = np.linspace(0, 2 * np.pi, 37)
    rn = np.array([0.25, 0.5, 0.75, 1.0])[:, None]
    ww, wp = rpm_to_rads(55.0), rpm_to_rads(60.0)
    # theta 정의 동일(웨이퍼 x축 기준). dw*r/(wp*r_cc) = -r*mu 로 부호가 흡수됨.
    x = rn * R_w * np.cos(th)
    y = rn * R_w * np.sin(th)
    _, _, v_cart = relative_velocity(x, y, ww, wp, r_cc)
    v_pol = relative_speed_polar(rn, th, ww, wp, r_cc, R_w)
    d = float(np.max(np.abs(v_cart - v_pol)))
    chk("Lai(Cartesian) == JJMIE(polar)", d < 1e-12, f"max|Δ|={d:.2e} m/s")

    # 4) Preston 프로파일: Rs=1이면 반경 무관 평탄
    rs, mrr = preston_mrr_profile(R_w, r_cc, 60.0, 60.0, 20.7e3, 1.0e-13)
    flat = float((mrr.max() - mrr.min()) / mrr.mean())
    chk("Rs=1 Preston MRR flat", flat < 1e-12,
        f"프로파일 편차 {flat:.2e}, MRR={mrr.mean()*6e10:.1f} nm/min")

    # 5) 시간평균 상대속도는 Rs와 무관하게 반경에 따라 증가 (엣지 빠름)
    rs2, mrr2 = preston_mrr_profile(R_w, r_cc, 50.0, 60.0, 20.7e3, 1.0e-13)
    chk("Rs!=1 edge-fast profile", mrr2[-1] > mrr2[0],
        f"edge/center = {mrr2[-1]/mrr2[0]:.5f}")

    print("\nOVERALL:", "PASS" if ok else "FAIL")
    return ok


if __name__ == "__main__":
    import sys
    print("=== CMP rotary kinematics self-test ===")
    sys.exit(0 if _selftest() else 1)
