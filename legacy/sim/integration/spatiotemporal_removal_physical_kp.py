"""
GW 접촉모델 기반 물리적 Kp(gw_preston_link.py)를 spatiotemporal_removal.py의
시공간 결합 제거량 필드에 "선택적으로" 연결 — 2026-09-05 08시 회차 진행 로그에서
Lv4로 명시 유보했던 항목의 해소.

기존 6개 파일(spatiotemporal_removal.py, gw_preston_link.py, wiwnu_pattern_combined.py,
wiwnu.py, pattern_density.py, process_time.py, 그리고 preston.py/kinematics.py)은
1바이트도 수정하지 않는다 — 이 파일에서는 순수 import만 사용한다.

────────────────────────────────────────────────────────────────────
아이디어
────────────────────────────────────────────────────────────────────
기존 thickness_field()는 스칼라 Kp를 wiwnu.mrr_radial -> preston.mrr_profile에
그대로 넘겨 MRR(r) = Kp * P(r) * <|v|>_theta 를 계산한다(모든 반경 r에서 동일 Kp).

GW-link 모델(gw_preston_link.py)은 MRR = alpha_removal * n_contacts(P) * V 라는
미시적 대안을 준다. 국소압력 P(r) = p_norm_fn(r/R_w)를 알면, 국소 "유효 Kp"를
    Kp_eff(r) := alpha_removal * n_contacts_at(P(r)) / P(r)
로 정의한다. 이러면 Kp_eff(r) * P(r) * V(r) = alpha_removal * n_contacts_at(P(r)) * V(r)
= GW-link MRR과 대수적으로 정확히 같아진다(새 물리가정이 아니라 항등식 재배열).

wiwnu.mrr_radial / preston.mrr_profile은 반경 전체에 대해 스칼라 kp 하나만 받는
시그니처라 r마다 다른 kp_eff(r)를 넘길 수 없다. 따라서 이 모듈은 그 반경 루프
구조만 로컬로 재구현하되(중복 코드 발생 감수 — "기존 파일 무수정" 원칙이 우선),
실제 Preston 대수(Kp*P*V)는 preston.local_mrr()을 그대로 재사용해 새 물리연산을
추가하지 않는다.

alpha_removal은 gw_preston_link.calibrate_alpha_removal(P_ref, V_ref, kp_lit)로
문헌 캘리브레이션한다(P_ref=20.7kPa, V_ref=0.8 m/s, kp_lit=1e-13 — gw_preston_link.py
기존 self-test와 동일 캘리브레이션 지점).

주의(스코프): 이 모듈은 "선택적" 확장이다 — 기존 thickness_field(kp=상수)는 여전히
그대로 쓸 수 있고, 이 모듈은 그 대안을 나란히 제공할 뿐 대체하지 않는다.

실행: python3 sim/integration/spatiotemporal_removal_physical_kp.py -> self-test 결과 stdout.
"""
from __future__ import annotations

import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "tier1_empirical"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "tier2_physics"))

from kinematics import rpm_to_rads
from preston import local_mrr
from process_time import removed_thickness
from gw_preston_link import n_contacts_at, calibrate_alpha_removal


def kp_eff_at(P_pa, alpha_removal):
    """국소 유효 Kp(P) = alpha_removal * n_contacts_at(P) / P.

    Kp_eff(P) * P * V == alpha_removal * n_contacts_at(P) * V (GW-link MRR)이 되도록
    정의한 항등식 재배열 — 새 물리 가정 아님.
    """
    return alpha_removal * n_contacts_at(P_pa) / P_pa


def mrr_radial_physical_kp(R_w, r_cc, rpm_w, rpm_p, p_norm_fn, alpha_removal,
                           n_r=401, n_theta=721):
    """반경별 시간평균 MRR[m/s], GW-link 물리적 Kp_eff(r) 사용.

    wiwnu.mrr_radial + preston.mrr_profile과 동일한 루프 구조를 새로 작성한다
    (기존 함수들은 반경 전체에 스칼라 kp 하나만 받는 시그니처라 r마다 다른 kp를
    넘길 수 없어서). 실제 Kp*P*V 대수는 preston.local_mrr()을 그대로 재사용한다.

    반환: (rs, mrr, kp_eff_vals) — kp_eff_vals는 참고/진단용(반경별 유효 Kp).
    """
    rs = np.linspace(0.0, R_w, n_r)
    th = np.linspace(0.0, 2 * np.pi, n_theta, endpoint=False)
    ww, wp = rpm_to_rads(rpm_w), rpm_to_rads(rpm_p)
    out = np.empty_like(rs)
    kp_eff_vals = np.empty_like(rs)
    for i, r in enumerate(rs):
        p = p_norm_fn(r / R_w)
        kp_eff = kp_eff_at(p, alpha_removal)
        kp_eff_vals[i] = kp_eff
        m = local_mrr(r * np.cos(th), r * np.sin(th), ww, wp, r_cc, p, kp_eff)
        out[i] = m.mean()
    return rs, out, kp_eff_vals


def local_blanket_rate_physical_kp(r, R_w, r_cc, rpm_w, rpm_p, p_norm_fn, alpha_removal,
                                   n_r=401):
    """반경 r[m](스칼라 또는 배열)에서 blanket MRR K_eff(r).

    wiwnu_pattern_combined.local_blanket_rate와 동일 인터페이스/구조(np.interp 보간),
    물리적 Kp_eff(r) 버전.
    """
    rs, mrr, _ = mrr_radial_physical_kp(R_w, r_cc, rpm_w, rpm_p, p_norm_fn, alpha_removal,
                                        n_r=n_r)
    return np.interp(np.asarray(r, dtype=float), rs, mrr)


def combined_removal_map_physical_kp(radial_positions, die_rho_eff_map, R_w, r_cc,
                                     rpm_w, rpm_p, p_norm_fn, alpha_removal, n_r=401):
    """RR[i, j] = K_eff(r_i) / rho_eff(x_j).

    wiwnu_pattern_combined.combined_removal_map과 동일 구조, 물리적 Kp_eff(r) 버전.
    """
    radial_positions = np.asarray(radial_positions, dtype=float)
    die_rho_eff_map = np.asarray(die_rho_eff_map, dtype=float)
    K_r = local_blanket_rate_physical_kp(radial_positions, R_w, r_cc, rpm_w, rpm_p,
                                        p_norm_fn, alpha_removal, n_r=n_r)
    RR = K_r[:, None] / die_rho_eff_map[None, :]
    return {"rs": radial_positions, "K_r": K_r, "rho_eff": die_rho_eff_map, "RR": RR}


def thickness_field_physical_kp(radial_positions, die_rho_eff_map, R_w, r_cc, rpm_w, rpm_p,
                                p_norm_fn, V_ref, P_ref, kp_lit, t_sec, n_r=401):
    """GW-link 물리적 Kp_eff(r) 기반 시공간 두께 필드.

    spatiotemporal_removal.thickness_field()와 동일 출력 구조(dict:
    rs, K_r, rho_eff, RR, thickness) + 참고용 alpha_removal 필드 추가.

    V_ref/P_ref/kp_lit: alpha_removal 캘리브레이션 지점(gw_preston_link.calibrate_alpha_removal
    로 문헌값 역산, 기존 gw_preston_link.py self-test와 동일 캘리브레이션 지점을 쓰면
    "정의상 거의 항등"이 재현된다).
    """
    alpha_removal = calibrate_alpha_removal(P_ref, V_ref, kp_lit)
    res = combined_removal_map_physical_kp(radial_positions, die_rho_eff_map, R_w, r_cc,
                                           rpm_w, rpm_p, p_norm_fn, alpha_removal, n_r=n_r)
    thick = removed_thickness(res["RR"], res["RR"], t_sec)
    res["thickness"] = thick
    res["alpha_removal"] = alpha_removal
    return res


# ───────────────────────────── self-test ─────────────────────────────
def _self_test():
    ok = True

    def chk(name, cond, detail=""):
        nonlocal ok
        ok &= bool(cond)
        print(f"[{'PASS' if cond else 'FAIL'}] {name} {detail}")

    from spatiotemporal_removal import thickness_field
    from wiwnu import p_uniform, p_zoned, mrr_radial
    from pattern_density import effective_density
    import gw_preston_link as link

    R_w, r_cc = 0.150, 0.200
    rpm_w, rpm_p = 50.0, 60.0
    n_r = 401
    P_ref, V_ref, kp_lit = 20.7e3, 0.8, 1e-13
    t_sec = 60.0

    x_die = np.linspace(0.0, 20.0, 401)  # mm
    rho_local = 0.5 + 0.2 * np.sin(2 * np.pi * x_die / 4.0)
    rho_eff_die = effective_density(x_die, rho_local, PL=3.0)

    # --- 1) 캘리브레이션점 근방 균일압력: 물리기반 Kp_eff(r) 두께 필드가 상수-kp 필드와
    #        정의상 거의 항등(Kp_eff(P_ref) == kp_lit 대수적 항등, n_contacts_at 값과 무관) ---
    pfn_uniform = p_uniform(P_ref)
    rs_ref, _ = mrr_radial(R_w, r_cc, rpm_w, rpm_p, kp_lit, pfn_uniform, n_r=n_r)
    res_const = thickness_field(rs_ref, rho_eff_die, R_w, r_cc, rpm_w, rpm_p, kp_lit,
                                pfn_uniform, t_sec, n_r=n_r)
    res_phys = thickness_field_physical_kp(rs_ref, rho_eff_die, R_w, r_cc, rpm_w, rpm_p,
                                           pfn_uniform, V_ref, P_ref, kp_lit, t_sec, n_r=n_r)
    rel_dev = float(np.max(np.abs(res_phys["thickness"] / res_const["thickness"] - 1.0)))
    chk("균일압력=P_ref 근방: 물리기반 Kp_eff(r) 두께필드 == 상수-Kp 두께필드 (정의상 항등)",
        rel_dev < 1e-6, f"max_rel_dev={rel_dev:.3e}")

    # --- 2) 넓은 압력범위(14~96kPa 존압)에서 물리기반 vs 상수-kp 편차, 정직 보고 ---
    pfn_wide = p_zoned([0.0, 0.33, 0.66, 1.0], [14e3, 48e3, 96e3])
    rs_wide, _ = mrr_radial(R_w, r_cc, rpm_w, rpm_p, kp_lit, pfn_wide, n_r=n_r)
    res_const_w = thickness_field(rs_wide, rho_eff_die, R_w, r_cc, rpm_w, rpm_p, kp_lit,
                                  pfn_wide, t_sec, n_r=n_r)
    res_phys_w = thickness_field_physical_kp(rs_wide, rho_eff_die, R_w, r_cc, rpm_w, rpm_p,
                                             pfn_wide, V_ref, P_ref, kp_lit, t_sec, n_r=n_r)
    rel_dev_w = np.abs(res_phys_w["thickness"] / res_const_w["thickness"] - 1.0)
    max_dev_w = float(np.max(rel_dev_w))
    mean_dev_w = float(np.mean(rel_dev_w))
    chk("넓은 압력범위(14-96kPa)에서 물리기반/상수-kp 편차가 유한하고 안정적으로 계산됨",
        np.isfinite(max_dev_w) and max_dev_w < 0.5,
        f"max_rel_dev={max_dev_w:.3e} ({max_dev_w*100:.4f}%), "
        f"mean_rel_dev={mean_dev_w:.3e} ({mean_dev_w*100:.4f}%)")

    print(f"\n[정직 보고 - 차별점] 압력범위 14-96kPa(존압)에서 물리기반 Kp_eff(r) vs "
          f"상수-Kp 두께필드: 최대편차 = {max_dev_w*100:.4f}%, 평균편차 = {mean_dev_w*100:.4f}%")
    if max_dev_w < 1e-2:
        print("  -> 편차가 실무적으로 무시 가능한 수준(<0.01%). gw_preston_link.py 기존 "
              "self-test가 이미 확인했듯 n_contacts(P)가 14-96kPa 구간에서 거의 완벽히 "
              "선형(잔차<1e-6)이라 Kp_eff(r)이 사실상 상수 kp_lit에서 거의 벗어나지 않기 "
              "때문 -> 이 통합이 주는 정량적 실익은 제한적이다(정성적/구조적 의의는 있음: "
              "Kp가 화학 lump 상수가 아니라 GW 기하량으로 분해된다는 것을 보여줌).")
    else:
        print("  -> 편차가 무시할 수 없는 수준으로 나타남. GW 접촉모델의 n_contacts(P) "
              "비선형성(곡률)이 이 압력범위에서 두께 필드에 실측 가능한 영향을 준다는 뜻.")

    # --- 3) alpha_removal이 gw_preston_link.calibrate_alpha_removal과 정확히 일치 ---
    alpha_expect = link.calibrate_alpha_removal(P_ref, V_ref, kp_lit)
    chk("alpha_removal이 gw_preston_link.calibrate_alpha_removal과 일치(배선 검증)",
        abs(res_phys["alpha_removal"] / alpha_expect - 1.0) < 1e-12,
        f"alpha_removal={res_phys['alpha_removal']:.6e}")

    # --- 4) Kp_eff(P_ref) == kp_lit 대수적 항등(캘리브레이션 정의 그 자체) ---
    kp_eff_ref = kp_eff_at(P_ref, alpha_expect)
    chk("Kp_eff(P_ref) == kp_lit (캘리브레이션 정의상 항등, n_contacts_at 값과 무관)",
        abs(kp_eff_ref / kp_lit - 1.0) < 1e-9, f"Kp_eff(P_ref)={kp_eff_ref:.6e} vs kp_lit={kp_lit:.1e}")

    # --- 5) 극한 rho_eff=1: 물리기반 결합두께도 K_eff(r)*t와 bit-level 일치 ---
    rho_ones = np.ones(51)
    res_phys_ones = thickness_field_physical_kp(rs_ref, rho_ones, R_w, r_cc, rpm_w, rpm_p,
                                                pfn_uniform, V_ref, P_ref, kp_lit, 90.0, n_r=n_r)
    expect = res_phys_ones["K_r"][:, None] * 90.0
    max_abs_diff = float(np.max(np.abs(res_phys_ones["thickness"] - expect)))
    chk("극한a) rho_eff=1 -> 물리기반 결합두께가 K_eff(r)*t와 bit-level 일치",
        max_abs_diff < 1e-15, f"max_abs_diff={max_abs_diff:.2e}")

    print("\nOVERALL:", "PASS" if ok else "FAIL")
    return ok


if __name__ == "__main__":
    print("=== 시공간 결합 제거량 필드 - 물리적 Kp(GW-link) 확장 self-test ===")
    success = _self_test()
    sys.exit(0 if success else 1)
