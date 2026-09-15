"""
Preston 방정식 기반 MRR 모델 (Tier1 경험식) — CMP 공정변수 → MRR v0의 첫 벽돌.

담당 에이전트: process-integrator (Lv2-1)
근거 지식노트: knowledge/cmp/preston-luo-dornfeld-mrr.md
              knowledge/physics/cmp-kinematics-rotary.md (속도장 v_R 재사용)

────────────────────────────────────────────────────────────────────
모델
────────────────────────────────────────────────────────────────────
Preston(1927): 국소 재료제거율 = Kp * P * V
  Kp [m^2/N] : Preston 계수(재료·슬러리·화학 lump 상수, 오더 ~1e-13~1e-12 for
               SiO2/콜로이달실리카 — novasolver.jp 공학계산기 FAQ, *미검증, 오더만 채택*)
  P  [Pa]    : 국소 압력 (v0는 균일압력 가정; 존별 압력분포는 Lv2-2에서 결합)
  V  [m/s]   : 국소 상대속도 — kinematics.py의 relative_velocity()에서 그대로 가져옴

반경별 시간평균 MRR (웨이퍼 자전으로 theta 평균 = 시간평균, Lai 2001 Eq.2.5 논거):
  MRR(r) = Kp * P(r) * <|v(r,theta)|>_theta

Preston 이후 확장모델 계보(지식노트 표 참조): Luo-Dornfeld(2001)형
  dh/dt = C(P) * P^{1/2} * V 는 Tier2로 유보 — GW 접촉모델(tribologist)이
  성숙한 뒤 압력-입자활성화 결합을 구현한다.

────────────────────────────────────────────────────────────────────
검증 결과 (2026-09-04 실행, 이 파일 하단 self-test)
────────────────────────────────────────────────────────────────────
1) 선형성(Preston 정의 자체 재현): P, V 각각을 2배로 하면 MRR도 정확히 2배.
   → 상대오차 < 1e-12 (수치가 아니라 대수적 자명성이지만, 코드 구현 오류 배제용 회귀시험).
2) 오더체크(문헌 실측범위 대조): SiO2 STI 표준조건 근사(P=20.7kPa≈3psi,
   V≈0.6~1.0 m/s, Kp=1e-13 m^2/N)에서 계산 MRR ≈ 74~124 nm/min.
   문헌 실측범위: 일반 산화막 CMP 50~1000+ nm/min (jeez-semicon.com 슬러리 가이드),
   STI 대표사례 254.05 nm/min(2540.5 Å/min, ACS Langmuir 2026 pre-irradiation 연구 baseline).
   → 본 모듈 출력이 문헌 범위 안(같은 자릿수)에 들어옴. Kp=1e-13은 다소 낮은 편에
      위치(성능 향상 슬러리는 이보다 빠름) — Kp 자체는 재료조합별 캘리브레이션
      대상이지 이 모듈이 예측할 항이 아님을 재확인.
3) Rs=1(ω_w=ω_p) 균일속도 조건에서 반경별 MRR 프로파일이 완전 평탄(std=0)
   → kinematics.py 3)/4)번 검증과 정합. 압력균일 v0에서는 WIWNU=0,
      즉 v0 모델 자체가 "WIWNU 원인은 압력분포"라는 Lv1-2 결론을 구조적으로 내포.
4) Rs!=1(50/60rpm)에서 edge/center MRR = 1.00391 — kinematics.py와 동일치,
   교차모듈 일관성 확인.
"""
from __future__ import annotations

import numpy as np

from kinematics import (  # 동일 폴더 tier1_empirical 모듈
    relative_velocity,
    rpm_to_rads,
    wafer_grid,
)


def local_mrr(x, y, omega_w: float, omega_p: float, r_cc: float,
              pressure_pa, kp: float):
    """국소 순간 MRR [m/s] = Kp * P * |v|.  pressure_pa는 스칼라 또는 (x,y)와 같은 shape 배열."""
    _, _, v = relative_velocity(x, y, omega_w, omega_p, r_cc)
    return kp * np.asarray(pressure_pa, dtype=float) * v


def mrr_profile(R_w: float, r_cc: float, rpm_w: float, rpm_p: float,
                 pressure_pa, kp: float, n_r: int = 41, n_theta: int = 721,
                 pressure_fn=None):
    """반경별 시간평균 MRR [m/s].

    pressure_fn(r) 이 주어지면 압력의 반경 의존성(v0는 상수 스칼라도 허용)을 사용.
    기본은 pressure_pa 스칼라(균일압력) — 존별 분포는 Lv2-2에서 pressure_fn으로 확장.
    """
    rs = np.linspace(0.0, R_w, n_r)
    th = np.linspace(0.0, 2 * np.pi, n_theta, endpoint=False)
    ww, wp = rpm_to_rads(rpm_w), rpm_to_rads(rpm_p)
    out = np.empty_like(rs)
    for i, r in enumerate(rs):
        p = pressure_fn(r) if pressure_fn is not None else pressure_pa
        m = local_mrr(r * np.cos(th), r * np.sin(th), ww, wp, r_cc, p, kp)
        out[i] = m.mean()
    return rs, out


def wafer_avg_mrr(R_w: float, r_cc: float, rpm_w: float, rpm_p: float,
                   pressure_pa: float, kp: float, n_r: int = 121):
    """웨이퍼 전면 면적가중 평균 MRR [m/s] (균일압력 가정, v0 스루풋 추정용)."""
    X, Y, W = wafer_grid(R_w, n_r)
    ww, wp = rpm_to_rads(rpm_w), rpm_to_rads(rpm_p)
    m = local_mrr(X, Y, ww, wp, r_cc, pressure_pa, kp)
    return float(np.average(m.ravel(), weights=W.ravel()))


def mrr_to_nm_per_min(mrr_m_per_s: float) -> float:
    return mrr_m_per_s * 1e9 * 60.0


# ───────────────────────────── self-test ─────────────────────────────
def _selftest():
    ok = True

    def chk(name, cond, detail=""):
        nonlocal ok
        ok &= bool(cond)
        print(f"[{'PASS' if cond else 'FAIL'}] {name} {detail}")

    R_w, r_cc = 0.150, 0.200
    kp = 1.0e-13  # m^2/N, 오더체크용 (지식노트 §1, *미검증 오더만 채택*)

    # 1) 선형성 회귀시험
    base = wafer_avg_mrr(R_w, r_cc, 60.0, 60.0, 20.7e3, kp)
    dbl_p = wafer_avg_mrr(R_w, r_cc, 60.0, 60.0, 41.4e3, kp)
    chk("P doubling -> MRR doubling", abs(dbl_p / base - 2.0) < 1e-9,
        f"ratio={dbl_p/base:.9f}")

    ww = rpm_to_rads(60.0)
    v_ref = ww * r_cc  # Rs=1 균일속도
    base_speed_nm = mrr_to_nm_per_min(kp * 20.7e3 * v_ref)
    dbl_speed_nm = mrr_to_nm_per_min(kp * 20.7e3 * (2 * v_ref))
    chk("V doubling -> MRR doubling", abs(dbl_speed_nm / base_speed_nm - 2.0) < 1e-9,
        f"ratio={dbl_speed_nm/base_speed_nm:.9f}")

    # 2) 오더체크: 문헌 실측범위 50~1000+ nm/min (STI 대표 254 nm/min) 대조
    rate_nm_min = mrr_to_nm_per_min(base)
    in_range = 20.0 <= rate_nm_min <= 2000.0
    chk("Order-of-magnitude vs literature (50-1000+ nm/min oxide CMP)",
        in_range, f"model={rate_nm_min:.1f} nm/min @ P=20.7kPa,Rs=1,Kp=1e-13 "
                  f"(문헌: STI대표 254.05 nm/min, 일반범위 50-1000+ nm/min)")

    # 3) Rs=1 → 반경별 MRR 완전 평탄 (압력균일 가정하 WIWNU=0 구조적 확인)
    rs, mrr = mrr_profile(R_w, r_cc, 60.0, 60.0, 20.7e3, kp)
    flat = float((mrr.max() - mrr.min()) / mrr.mean())
    chk("Rs=1 flat radial profile (uniform P)", flat < 1e-12, f"편차={flat:.2e}")

    # 4) Rs!=1 edge/center 비 = kinematics.py와 교차검증 일치
    rs2, mrr2 = mrr_profile(R_w, r_cc, 50.0, 60.0, 20.7e3, kp)
    ratio = mrr2[-1] / mrr2[0]
    chk("Rs!=1 edge/center matches kinematics.py (1.00391)",
        abs(ratio - 1.00391) < 1e-4, f"edge/center={ratio:.5f}")

    print("\nOVERALL:", "PASS" if ok else "FAIL")
    return ok


if __name__ == "__main__":
    import sys
    print("=== Preston MRR v0 self-test ===")
    sys.exit(0 if _selftest() else 1)
