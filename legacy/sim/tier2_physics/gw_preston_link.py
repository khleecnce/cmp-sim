"""
GW 접촉모델 → Preston Kp 물리적 분해 + 문헌값(STI MRR) 재현 (pad-mechanic Lv3-2, 커리큘럼 최종단원).

지식 근거:
  knowledge/materials/gw-nominal-vs-local-pressure.md (§2: p_r=W/A_r는 P와 거의 무관한 상수,
    n_contacts(P)는 P에 거의 선형 비례 — Lv2-2에서 이미 수치확인, 오차<0.1%/<2e-15)
  knowledge/materials/hertz-gw-contact-mechanics.md (Hertz+GW 폐형식/수치 기반)
  sim/tier1_empirical/preston.py (Kp=1e-13 m^2/N 오더체크, STI 254.05 nm/min 문헌값)

────────────────────────────────────────────────────────────────────
아이디어 (Kp의 물리적 분해)
────────────────────────────────────────────────────────────────────
Preston 현상론: MRR = Kp * P * V  (Kp는 재료/화학 lump 상수, 물리적 기원 불명)

GW 미시모델(Lv2-2 결론)이 주는 대안적 그림:
  MRR = alpha_removal * n_contacts(P) * V
  여기서 alpha_removal [m^3/s per contact per (m/s)] 는 "접촉점 1개가 단위 상대속도당
  깎아내는 부피율" — 화학(슬러리)·기계(패드/입자 경도) lump 상수. n_contacts(P)는
  gw_pressure_solve.local_contact_state()로 계산되는 접촉점수(순수 기하/역학량, 화학 무관).

Lv2-2에서 n_contacts(P)가 P에 (거의) 선형 비례함을 이미 확인했으므로, 이 대안 모델은
Preston의 "MRR ∝ P" 현상론적 선형성을 **미시적으로 재현**한다:
  MRR = alpha_removal * n_contacts(P) * V ≈ alpha_removal * (dn/dP) * P * V
  → Kp_physical := alpha_removal * (dn/dP)   (P에 무관한 상수여야 Preston과 정합)

이 모듈은:
  1) n_contacts(P)의 P-선형성을 3개 압력점(14/48/96 kPa, Lv2-2와 동일 조건 재사용)에서
     재확인하고 dn/dP 기울기를 회귀로 구한다.
  2) preston.py의 문헌 캘리브레이션 지점(P=20.7 kPa, Kp=1e-13 m^2/N → MRR≈254.05 nm/min,
     STI 대표값, ACS Langmuir 2026 baseline, preston.py §2 인용)에서 alpha_removal을
     역산한다: alpha_removal = Kp_lit * P_ref / n_contacts(P_ref).
  3) 역산된 alpha_removal을 고정한 채 다른 두 압력(14, 96 kPa)에서 GW-link MRR을 예측하고,
     원래 Preston(Kp=1e-13 상수) 예측과 비교한다 → 두 모델이 서로 다른 미시가정(순수 선형 P
     vs GW n(P))에서 출발했음에도 예측이 수 % 이내로 수렴하는지가 "문헌값 재현" 검증이다.

주의(스코프): alpha_removal 자체는 화학종속 lump 상수라 이 모델이 예측하는 항이 아니다
(Lv2-2 스코프 한계와 동일). 검증 대상은 어디까지나 "GW 기하모델만으로 Preston의 P-선형성이
왜 성립하는지 설명되는가"이다 — Kp의 절대값 예측이 아님(명시).

실행: python3 gw_preston_link.py -> self-test 결과 stdout.
"""
import sys
import os
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "tier1_empirical"))

import numpy as np

from gw_pressure_solve import local_contact_state
from kinematics import rpm_to_rads


# 공통 GW 파라미터 (gw_contact.py/gw_pressure_solve.py self-test와 동일 오더, 지식노트 §4 근거)
#
# ⚠ 이 값들은 **기본값일 뿐 진실이 아니다.** 2026-09-06부터 파라미터 팩
# (knowledge/params/*.yaml)이 실제 소유자이고, 엔진은 pad_* 키를 읽어 아래 함수들의
# 인자로 주입한다. 여기 남은 상수는 이 파일을 단독 실행(self-test)할 때만 쓰인다.
# 다른 패드를 쓰고 싶으면 이 파일이 아니라 팩을 고쳐라.
_E_STAR = 1e9
_R = 5e-6
_BETA = 1.0 / 0.3e-6
_ETA = 1e11
_A_N = 1e-4  # 1 cm^2


def n_contacts_at(P_pa, E_star=None, R=None, beta=None, eta=None, A_n=None):
    """명목압력 P에서 GW 접촉점수 n(P). local_contact_state 얇은 래퍼.

    패드 물성을 인자로 받는다(None이면 모듈 기본값) — 팩이 다른 패드를 물릴 수 있게.
    """
    r = local_contact_state(P_pa,
                            _A_N if A_n is None else A_n,
                            _BETA if beta is None else beta,
                            _ETA if eta is None else eta,
                            _E_STAR if E_star is None else E_star,
                            _R if R is None else R)
    return r["n_contacts"]


def linear_fit_slope(P_list, n_list):
    """n(P) ≈ slope*P + intercept 최소자승 적합, slope(=dn/dP) 반환."""
    P_arr = np.asarray(P_list, dtype=float)
    n_arr = np.asarray(n_list, dtype=float)
    A = np.vstack([P_arr, np.ones_like(P_arr)]).T
    slope, intercept = np.linalg.lstsq(A, n_arr, rcond=None)[0]
    return slope, intercept


def mrr_gw_link(P_pa, V_mps, alpha_removal, **pad):
    """GW-link 모델: MRR = alpha_removal * n_contacts(P) * V."""
    return alpha_removal * n_contacts_at(P_pa, **pad) * V_mps


def mrr_preston_direct(P_pa, V_mps, kp):
    """순수 Preston: MRR = Kp * P * V (preston.py와 동일 정의, 여기선 재구현 없이 직접 계산)."""
    return kp * P_pa * V_mps


def calibrate_alpha_removal(P_ref_pa, V_ref_mps, kp_lit, **pad):
    """문헌 캘리브레이션점(P_ref, Kp_lit)에서 alpha_removal 역산."""
    mrr_ref = mrr_preston_direct(P_ref_pa, V_ref_mps, kp_lit)
    n_ref = n_contacts_at(P_ref_pa, **pad)
    return mrr_ref / (n_ref * V_ref_mps)


def mrr_to_nm_per_min(mrr_m_per_s: float) -> float:
    return mrr_m_per_s * 1e9 * 60.0


# ───────────────────────────── self-test ─────────────────────────────
def _self_test():
    ok = True

    def chk(name, cond, detail=""):
        nonlocal ok
        ok &= bool(cond)
        print(f"[{'PASS' if cond else 'FAIL'}] {name} {detail}")

    # --- 1) n_contacts(P) 선형성 재확인 (Lv2-2와 동일 3점) ---
    P_points = [14e3, 48e3, 96e3]
    n_points = [n_contacts_at(P) for P in P_points]
    slope, intercept = linear_fit_slope(P_points, n_points)
    resid = [abs((slope * P + intercept) - n) / n for P, n in zip(P_points, n_points)]
    max_resid = max(resid)
    chk("n_contacts(P) 선형적합 잔차 < 1e-6", max_resid < 1e-6,
        f"max_resid={max_resid:.3e}, slope(dn/dP)={slope:.6e} /Pa")

    # --- 2) 문헌 캘리브레이션(STI 254.05 nm/min @ P=20.7kPa) ---
    # V: preston.py docstring의 STI 표준조건 근사 V~0.6-1.0 m/s 중간값 채택(명시)
    P_ref = 20.7e3
    V_ref = 0.8
    kp_lit = 1e-13
    alpha_removal = calibrate_alpha_removal(P_ref, V_ref, kp_lit)
    mrr_ref_direct = mrr_preston_direct(P_ref, V_ref, kp_lit)
    mrr_ref_gw = mrr_gw_link(P_ref, V_ref, alpha_removal)
    chk("캘리브레이션점에서 GW-link == Preston-direct (정의상 항등)",
        abs(mrr_ref_gw / mrr_ref_direct - 1.0) < 1e-9,
        f"direct={mrr_to_nm_per_min(mrr_ref_direct):.2f} nm/min, "
        f"gw_link={mrr_to_nm_per_min(mrr_ref_gw):.2f} nm/min "
        f"(문헌: STI 254.05 nm/min, ACS Langmuir 2026 baseline)")

    # --- 3) 캘리브레이션점 자체가 문헌값 오더 재현 확인 ---
    rate_nm_min = mrr_to_nm_per_min(mrr_ref_direct)
    in_range = 50.0 <= rate_nm_min <= 1000.0
    chk("캘리브레이션 MRR이 문헌범위(50-1000 nm/min) 안",
        in_range, f"model={rate_nm_min:.1f} nm/min")

    # --- 4) 외삽: 다른 두 압력점에서 GW-link vs 순수 Preston 비교 ---
    # (같은 alpha_removal 고정, n(P)의 미세 비선형성만큼만 Preston과 갈라져야 함)
    max_dev = 0.0
    detail_lines = []
    for P in [14e3, 48e3, 96e3]:
        mrr_gw = mrr_gw_link(P, V_ref, alpha_removal)
        mrr_pr = mrr_preston_direct(P, V_ref, kp_lit)
        dev = abs(mrr_gw / mrr_pr - 1.0)
        max_dev = max(max_dev, dev)
        detail_lines.append(
            f"P={P/1e3:.0f}kPa: GW-link={mrr_to_nm_per_min(mrr_gw):.2f}, "
            f"Preston-direct={mrr_to_nm_per_min(mrr_pr):.2f} nm/min, dev={dev:.3e}"
        )
    chk("GW-link vs Preston-direct 외삽 편차 < 1e-4 (n(P) 선형성 덕분)",
        max_dev < 1e-4, f"max_dev={max_dev:.3e}")
    for line in detail_lines:
        print("   ", line)

    print(f"\nalpha_removal(캘리브레이션 역산) = {alpha_removal:.6e} m^3/(s*contact*(m/s))")
    print(f"Kp_physical = alpha_removal * dn/dP = {alpha_removal * slope:.6e} "
          f"(vs 문헌 Kp={kp_lit:.1e} m^2/N, 참고: 정의상 정확히 재현되는 항등식임을 위 확인함)")

    print(f"\n{'ALL PASS' if ok else 'SOME FAILED'}")
    return ok


if __name__ == "__main__":
    success = _self_test()
    raise SystemExit(0 if success else 1)
