"""
시공간 결합 제거량 필드 RR(r,x)*t -> thickness(r,x,t) 조립 레이어.

담당: process-integrator Lv3-2 (통합 시뮬레이터 아키텍처 설계·조립, sim 전체 오너
      — 커리큘럼 최종 단원, 이수일 2026-09-05).
근거 지식노트: knowledge/cmp/luo-dornfeld-integrated-cmp-framework.md
              (Luo & Dornfeld 2003 리뷰 — "Preston식이 3-스케일을 잇는 인터페이스",
               §4-5, Fig.6 통합 프레임워크)

────────────────────────────────────────────────────────────────────
설계 원칙 (지식노트 §5 결정사항 그대로 구현)
────────────────────────────────────────────────────────────────────
1) 기존 5개 tier1/tier2 모듈은 1바이트도 수정하지 않는다(순수 import만).
2) 새 물리가정을 추가하지 않는다 — 이 모듈은 "조립(assembly)"만 한다:
     RR(r,x) [wiwnu_pattern_combined.combined_removal_map, 정상상태]
       × t   [process_time.removed_thickness의 선형시간적분 로직, 새 가정 없음]
     = thickness(r,x,t)
3) GW/Preston-Kp 물리적 분해(gw_preston_link.py)와의 연결은 이번 단원 스코프 밖
   (지식노트 §5-3: Kp가 함수형이 되면 기존 kp=상수 시그니처의 self-test들이 깨질
   회귀 위험이 있어 Lv4로 유보). 이 모듈의 kp는 여전히 preston.py와 동일한 상수.

────────────────────────────────────────────────────────────────────
검증 결과 (self-test, 하단) — 2026-09-05 실행
────────────────────────────────────────────────────────────────────
1) 선형성: thickness_field(t=120s) == 2 * thickness_field(t=60s) (상대오차 <1e-9)
   — process_time.py 1번 검증(1차원)이 2차원 필드에서도 깨지지 않음을 확인.
2) 극한 a) rho_eff≡1: thickness_field가 wiwnu 단독 K(r)*t와 각 반경행에서 bit-level
   일치(wiwnu_pattern_combined.py 극한a 검증의 시간축 확장).
3) endpoint_time과의 정합: 임의 (r,x) 셀에서 target/RR(r,x) == endpoint_time(target,
   RR(r,x)) (동일 함수 재사용이므로 항등, 배선 검증).
4) 다이-스케일 CV(변동계수)가 시간에 무관(정상상태 RR의 선형 시간배율이므로 t가
   상쇄) — thickness_field(t1)와 thickness_field(t2)의 CV가 동일함을 확인
   (물리적으로 자명하지만, "적분 후 지표까지 시간불변성이 깨지지 않는지" 배선검증).
"""
from __future__ import annotations

import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "tier1_empirical"))

from wiwnu_pattern_combined import combined_removal_map, _area_weighted_2d
from process_time import removed_thickness, endpoint_time


def thickness_field(radial_positions, die_rho_eff_map, R_w, r_cc, rpm_w, rpm_p,
                    kp, p_norm_fn, t_sec, n_r=401):
    """RR(r,x) 정상상태 맵을 시간 t_sec만큼 선형적분한 제거두께 필드[m].

    반환 dict: {"rs", "K_r", "rho_eff", "RR", "thickness"} — RR/K_r/rho_eff는
    wiwnu_pattern_combined.combined_removal_map()의 출력을 그대로 통과시키고,
    "thickness"만 이 모듈이 process_time.removed_thickness()로 새로 계산한다.
    """
    res = combined_removal_map(radial_positions, die_rho_eff_map, R_w, r_cc,
                               rpm_w, rpm_p, kp, p_norm_fn, n_r=n_r)
    # removed_thickness(rs, mrr, t)는 rs를 shape 정합용으로만 받고 mrr*t를 반환한다
    # (process_time.py 원 시그니처, 1차원 전용) — 2차원 RR에도 mrr 자리에 그대로
    # 넣으면 broadcasting으로 동일 연산(원소별 곱)이 성립한다(del rs로 미사용이므로
    # shape 요구가 없음. 새 코드 작성 없이 기존 함수 재사용).
    thick = removed_thickness(res["RR"], res["RR"], t_sec)
    res["thickness"] = thick
    return res


def endpoint_time_at(target_thickness_m, rr_value):
    """단일 (r,x) 셀에서 목표두께 도달시간 — process_time.endpoint_time 얇은 래퍼.

    호출부가 RR[i,j] 값을 직접 뽑아 넘기는 용도(2차원 필드 전체에 대한 엔드포인트
    맵이 필요하면 vectorize해서 호출).
    """
    return endpoint_time(target_thickness_m, rr_value)


def cv_percent_2d(RR_or_thickness):
    """다이-스케일 CV(변동계수, %) — _area_weighted_2d의 sigma_pct 별칭.

    RR과 thickness는 스칼라 t배만 다르므로(RR*t) CV는 시간에 불변이다(self-test 4).
    이 함수는 편의상 어느 배열을 넣어도 동작하도록 rs 그리드 재계산 없이
    균일가중(모든 셀 동일 가중)으로 근사한 CV를 반환 — 반경 면적가중이 필요하면
    wiwnu_pattern_combined._area_weighted_2d(rs, RR)을 직접 호출할 것(이 함수는
    빠른 sanity-check용 근사).
    """
    arr = np.asarray(RR_or_thickness, dtype=float)
    mean = float(arr.mean())
    std = float(arr.std())
    return 100.0 * std / mean


# ───────────────────────────── self-test ─────────────────────────────
def _selftest():
    ok = True

    def chk(name, cond, detail=""):
        nonlocal ok
        ok &= bool(cond)
        print(f"[{'PASS' if cond else 'FAIL'}] {name} {detail}")

    from wiwnu import p_uniform, p_edge_concentration, mrr_radial, wiwnu
    from pattern_density import effective_density

    R_w, r_cc, kp = 0.150, 0.200, 1.0e-13
    n_r = 401

    x_die = np.linspace(0.0, 20.0, 401)  # mm
    rho_local = 0.5 + 0.2 * np.sin(2 * np.pi * x_die / 4.0)
    rho_eff_die = effective_density(x_die, rho_local, PL=3.0)

    rs_ref, _ = mrr_radial(R_w, r_cc, 50.0, 60.0, kp,
                           p_edge_concentration(20.7e3, amp=0.30, n=8), n_r=n_r)

    pfn = p_edge_concentration(20.7e3, amp=0.30, n=8)

    # 1) 선형성: t=120s가 t=60s의 정확히 2배
    res60 = thickness_field(rs_ref, rho_eff_die, R_w, r_cc, 50.0, 60.0, kp, pfn, 60.0,
                            n_r=n_r)
    res120 = thickness_field(rs_ref, rho_eff_die, R_w, r_cc, 50.0, 60.0, kp, pfn, 120.0,
                             n_r=n_r)
    ratio = float(np.max(np.abs(res120["thickness"] / res60["thickness"] - 2.0)))
    chk("thickness_field linear in t (120s = 2x 60s)", ratio < 1e-9,
        f"max|ratio-2|={ratio:.2e}")

    # 2) 극한 a) rho_eff≡1 -> 결합 두께가 wiwnu 단독 K(r)*t 와 행 단위로 일치
    rho_ones = np.ones(51)
    res_a = thickness_field(rs_ref, rho_ones, R_w, r_cc, 50.0, 60.0, kp, pfn, 90.0,
                            n_r=n_r)
    _, mrr_ref = mrr_radial(R_w, r_cc, 50.0, 60.0, kp, pfn, n_r=n_r)
    expect = mrr_ref[:, None] * 90.0
    max_abs_diff = float(np.max(np.abs(res_a["thickness"] - expect)))
    chk("극한a) rho_eff=1 -> 결합두께가 K(r)*t와 bit-level 일치",
        max_abs_diff < 1e-15, f"max_abs_diff={max_abs_diff:.2e}")

    # 3) endpoint_time 배선 검증: 임의 셀에서 target/RR == endpoint_time_at
    i, j = 10, 200
    rr_cell = float(res60["RR"][i, j])
    target = 50e-9  # 50nm
    t_direct = target / rr_cell
    t_via = endpoint_time_at(target, rr_cell)
    chk("endpoint_time_at 배선 == 직접 나눗셈(항등)",
        abs(t_via - t_direct) / t_direct < 1e-12,
        f"direct={t_direct:.4f}s, via={t_via:.4f}s")

    # 4) CV 시간 불변성: RR*t의 CV는 t와 무관해야 함
    cv60 = cv_percent_2d(res60["thickness"])
    cv120 = cv_percent_2d(res120["thickness"])
    rel = abs(cv120 - cv60) / cv60
    chk("다이-스케일 CV는 시간에 불변(RR*t의 선형배율 상쇄)",
        rel < 1e-9, f"CV(60s)={cv60:.4f}%, CV(120s)={cv120:.4f}%, rel={rel:.2e}")

    print(f"\n참고: thickness_field(90s) 평균 제거두께 = "
          f"{res_a['thickness'].mean()*1e9:.2f} nm, "
          f"CV(면적비가중 근사) = {cv_percent_2d(res_a['thickness']):.3f}%")

    print("\nOVERALL:", "PASS" if ok else "FAIL")
    return ok


if __name__ == "__main__":
    import sys as _sys
    print("=== 시공간 결합 제거량 필드 (integration layer) self-test ===")
    _sys.exit(0 if _selftest() else 1)
