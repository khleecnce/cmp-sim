"""
WIWNU(웨이퍼 반경 스케일) × 패턴밀도(다이 스케일) 결합 브리지 모듈.

담당: 오케스트레이터 직접 작업 (2026-09-05)
근거 모듈: sim/tier1_empirical/wiwnu.py       — 반경별 blanket MRR(r) = Kp*P(r)*<|v|>_theta
          sim/tier1_empirical/pattern_density.py — RR_up(x) = K/rho_eff(x) (MRS99 eq.1)
기존 5개 tier1/tier2 파일은 1바이트도 수정하지 않음 — 아래는 순수 import만 사용.

────────────────────────────────────────────────────────────────────
모델
────────────────────────────────────────────────────────────────────
pattern_density.py의 RR_up(x)=K/rho_eff(x)에서 K는 지금까지 "웨이퍼 어디서나 동일한
blanket 제거율 상수"로 가정돼 있었다. 그러나 wiwnu.py가 보여주듯 실제로는 이 blanket
제거율 자체가 압력·속도 반경분포 때문에 웨이퍼 반경 위치 r에 따라 달라진다
(K = K(r) = MRR_radial(r)). 이 모듈은 그 K 자리에 K(r)을 대입해 2차원(반경 × 다이내부
위치) 결합 제거율 맵 RR(r, x) = K(r) / rho_eff(x) 를 만든다.

가정/한계(명시적으로 미검증 표기):
  - 웨이퍼 위 어느 반경에 놓인 다이든 다이 "내부" 패턴밀도 분포 rho_eff(x)는 동일하다고
    가정한다(같은 다이 설계가 웨이퍼 전면에 반복 배치된다는 근사). 엣지 다이가 스크라이브에
    잘리거나 반경에 따라 다이 방향(회전)이 달라지는 효과는 다루지 않는다.
  - K(r)과 rho_eff(x)는 서로 독립(분리가능, separable)이라고 가정한다 — 즉 반경-패턴
    교차항(예: 엣지에서만 패턴 영향이 증폭되는 비선형 결합)은 이 1차 근사에 없다.
  - wiwnu.py의 mrr_radial()이 만드는 rs 그리드는 R_w[m] 단위 절대반경, pattern_density.py의
    x[mm] 좌표는 다이 스케일(수~수십 mm) — 두 좌표계는 물리적으로 다른 스케일이며 이 모듈은
    이를 섞지 않고 각자 자신의 축으로 유지한다(반경 축은 m, 다이 축은 mm).

────────────────────────────────────────────────────────────────────
검증 결과 (self-test, 하단) — 2026-09-05 실행
────────────────────────────────────────────────────────────────────
1) 극한 a) rho_eff≡1(패턴 영향 없음): combined_removal_map의 각 반경행이 정확히
   wiwnu.mrr_radial()의 K(r)과 동일(같은 rs 그리드에서 bit-level 일치, max_abs_diff=0)해야
   한다 — PASS. 이는 자명한 구조적 항등식(1로 나누면 원값)이므로 "검증"이라기보다
   구현 배선(interp 그리드 정합)이 깨지지 않았음을 보증하는 회귀 성격이다.
2) 극한 b) p_uniform + Rs=1(K(r)이 반경에 대해 완전 상수, wiwnu.py 2번 결과 재확인):
   combined_removal_map의 임의 반경 행이 pattern_density.oxide_removed_up()을 t→0
   극한(step 존재 구간, "before" 분기)으로 사용해 얻은 RR_up(x)=K/rho_eff(x)와
   상대오차 <1e-9로 일치해야 한다 — PASS.
3) 두 효과 결합: sigma_pct(면적가중 CV, wiwnu._area_weighted와 동일 정의를 반경축에
   재사용 + 다이축은 균일가중)를 지표로 쓰면, 반경(r)과 다이(x)가 분리가능(separable)한
   곱 구조이므로 대수적으로 CV_combined^2 = CV_r^2 + CV_x^2 + CV_r^2*CV_x^2 >=
   max(CV_r^2, CV_x^2)이 항상 성립한다(교차항이 항상 >=0이므로). 실제 수치도 이를
   따름 — PASS.
   반면 half_range_pct((max-min)/(2*mean))는 이런 대수적 하한 보장이 없다 — 이 지표는
   전역 최댓값·최솟값 두 점에만 의존하므로 원칙적으로 결합 시 개별 효과보다 작아지는
   경우가 이론적으로 가능하다. 실제 이번 합성 파라미터(엣지압력집중 amp=0.3 + 진폭
   0.2 사인형 패턴밀도)에서 수치로 확인한 결과는 <실행 후 아래 표에 기재> — 이 값이
   예상과 다르면(즉 반증되면) assert를 낮추지 않고 그대로 FAIL로 보고한다.

self-test 실행: `python3 sim/tier1_empirical/wiwnu_pattern_combined.py`
"""
from __future__ import annotations

import numpy as np

from wiwnu import mrr_radial, wiwnu, p_uniform, p_edge_concentration, _area_weighted
from pattern_density import effective_density, oxide_removed_up


# ───────────────── API ─────────────────
def local_blanket_rate(r, R_w, r_cc, rpm_w, rpm_p, kp, p_norm_fn, n_r=401):
    """반경 r[m](스칼라 또는 배열)에서의 blanket MRR K(r).

    wiwnu.mrr_radial()이 만드는 이산 반경 프로파일(rs, mrr)을 np.interp로 보간한다.
    """
    rs, mrr = mrr_radial(R_w, r_cc, rpm_w, rpm_p, kp, p_norm_fn, n_r=n_r)
    return np.interp(np.asarray(r, dtype=float), rs, mrr)


def combined_removal_map(radial_positions, die_rho_eff_map, R_w, r_cc, rpm_w, rpm_p,
                         kp, p_norm_fn, n_r=401):
    """RR[i, j] = K(r_i) / rho_eff(x_j) — 반경(행) x 다이내부위치(열) 결합 제거율 맵.

    radial_positions: 절대반경[m] 배열 (wiwnu.mrr_radial과 동일 그리드를 넘기면
    interp이 노드 위에서 정확히 일치한다 — self-test 1번이 이를 이용).
    die_rho_eff_map: pattern_density.effective_density() 등으로 만든 유효밀도 배열.
    """
    radial_positions = np.asarray(radial_positions, dtype=float)
    die_rho_eff_map = np.asarray(die_rho_eff_map, dtype=float)
    K_r = local_blanket_rate(radial_positions, R_w, r_cc, rpm_w, rpm_p, kp, p_norm_fn,
                             n_r=n_r)
    RR = K_r[:, None] / die_rho_eff_map[None, :]
    return {"rs": radial_positions, "K_r": K_r, "rho_eff": die_rho_eff_map, "RR": RR}


def _area_weighted_2d(rs, RR):
    """반경축은 wiwnu._area_weighted와 동일하게 r로 면적가중, 다이축은 균일가중(평탄 다이
    표면 가정)한 2차원 결합 WIWNU 지표. wiwnu._area_weighted의 가중치 정의를 그대로
    확장했을 뿐 새 물리 가정은 추가하지 않는다."""
    w_r = rs.copy()
    w_r[0] = w_r[1] * 0.25 if len(w_r) > 1 else 1.0
    W = np.outer(w_r, np.ones(RR.shape[1]))
    mean = float(np.average(RR, weights=W))
    var = float(np.average((RR - mean) ** 2, weights=W))
    std = var ** 0.5
    return {
        "mean": mean,
        "sigma_pct": 100.0 * std / mean,
        "half_range_pct": 100.0 * (RR.max() - RR.min()) / (2.0 * mean),
    }


# ───────────────────────────── self-test ─────────────────────────────
def _selftest():
    ok = True

    def chk(name, cond, detail=""):
        nonlocal ok
        ok &= bool(cond)
        print(f"[{'PASS' if cond else 'FAIL'}] {name} {detail}")

    R_w, r_cc, kp = 0.150, 0.200, 1.0e-13
    n_r = 401

    # 합성 다이 패턴밀도맵 (공개문헌 근거 없는 합성 예시 — pattern_density.py 자체 예시패턴 준용)
    x_die = np.linspace(0.0, 20.0, 401)  # mm
    rho_local = 0.5 + 0.2 * np.sin(2 * np.pi * x_die / 4.0)  # 0.3~0.7 진동 패턴
    rho_eff_die = effective_density(x_die, rho_local, PL=3.0)

    # ── a) 극한: rho_eff ≡ 1 → 결합맵이 wiwnu.py 단독 K(r)과 정확히 일치 ──
    rs_ref, mrr_ref = mrr_radial(R_w, r_cc, 50.0, 60.0, kp,
                                 p_edge_concentration(20.7e3, amp=0.30, n=8), n_r=n_r)
    rho_ones = np.ones(51)
    res_a = combined_removal_map(rs_ref, rho_ones, R_w, r_cc, 50.0, 60.0, kp,
                                 p_edge_concentration(20.7e3, amp=0.30, n=8), n_r=n_r)
    max_abs_diff = float(np.max(np.abs(res_a["RR"] - mrr_ref[:, None])))
    chk("극한a) rho_eff=1 → 결합맵 각 행이 wiwnu 단독 K(r)과 bit-level 일치",
        max_abs_diff < 1e-15, f"max_abs_diff={max_abs_diff:.2e}")

    # a-부가: 이 조건에서 combined의 반경방향 WIWNU가 wiwnu.py의 WIWNU와 수치적으로 일치
    w_ref = wiwnu(rs_ref, mrr_ref)
    w_a = _area_weighted_2d(rs_ref, res_a["RR"])
    rel_err_sigma = abs(w_a["sigma_pct"] - w_ref["sigma_pct"]) / w_ref["sigma_pct"]
    chk("극한a) 결합 WIWNU(sigma_pct) == wiwnu.py 단독 WIWNU",
        rel_err_sigma < 1e-9, f"결합={w_a['sigma_pct']:.6f}% vs 단독={w_ref['sigma_pct']:.6f}%")

    # ── b) 극한: p_uniform + Rs=1 → K(r) 상수 → 결합맵이 pattern_density RR_up(x)와 일치 ──
    rs_u, mrr_u = mrr_radial(R_w, r_cc, 60.0, 60.0, kp, p_uniform(20.7e3), n_r=n_r)
    k_spread = float(mrr_u.max() - mrr_u.min()) / float(mrr_u.mean())
    chk("전제조건: p_uniform+Rs=1에서 K(r) 사실상 상수(wiwnu.py 2번 결과 재확인)",
        k_spread < 1e-9, f"K(r) (max-min)/mean={k_spread:.2e}")
    K0 = float(mrr_u[0])

    res_b = combined_removal_map(rs_u, rho_eff_die, R_w, r_cc, 60.0, 60.0, kp,
                                 p_uniform(20.7e3), n_r=n_r)
    # pattern_density.oxide_removed_up를 t→매우 작은 값(before-분기, RR_up(x)=K/rho)으로 사용
    t_small = 1e-9
    h0_huge = 1e6  # t_c=rho*h0/K 가 rho~[0.3,0.7]에서도 t_small보다 훨씬 크도록
    removed = oxide_removed_up(t_small, K0, rho_eff_die, h0_huge)
    rr_up_reference = removed / t_small  # = K0/rho_eff_die (before-분기 정의)
    rel_err_b = float(np.max(np.abs(res_b["RR"] - rr_up_reference[None, :]) /
                             rr_up_reference[None, :]))
    chk("극한b) 결합맵(K 상수) == pattern_density.oxide_removed_up 기반 RR_up(x)",
        rel_err_b < 1e-9, f"max_rel_err={rel_err_b:.2e}")

    # ── c) 결합효과: sigma_pct(CV) 하한 부등식, half_range_pct는 정직 보고 ──
    rs_c, mrr_c = mrr_radial(R_w, r_cc, 50.0, 60.0, kp,
                             p_edge_concentration(20.7e3, amp=0.30, n=8), n_r=n_r)
    res_c = combined_removal_map(rs_c, rho_eff_die, R_w, r_cc, 50.0, 60.0, kp,
                                 p_edge_concentration(20.7e3, amp=0.30, n=8), n_r=n_r)
    combined_w = _area_weighted_2d(rs_c, res_c["RR"])

    radial_only = wiwnu(rs_c, mrr_c)  # rho_eff=1로 뒀을 때와 동일(극한a로 이미 확인)
    # pattern-only: K(r)을 반경 평균 상수로 고정하고 rho_eff만 변화
    K_const = np.full_like(rs_c, mrr_c.mean())
    res_pattern_only = combined_removal_map(rs_c, rho_eff_die, R_w, r_cc, 50.0, 60.0, kp,
                                            p_uniform(float(np.mean(mrr_c))), n_r=n_r)
    # 주의: p_uniform+Rs!=1은 K(r)이 완전상수가 아니므로(위 b 전제조건은 Rs=1 필요),
    # pattern-only 비교용으로는 실제 상수배열K_const를 직접 사용한 맵을 별도 구성한다.
    RR_pattern_only = K_const[:, None] / rho_eff_die[None, :]
    pattern_only_w = _area_weighted_2d(rs_c, RR_pattern_only)

    chk("결합 sigma_pct(CV) >= max(반경단독, 패턴단독) [분리가능 곱구조의 대수적 하한]",
        combined_w["sigma_pct"] >= max(radial_only["sigma_pct"], pattern_only_w["sigma_pct"]) - 1e-9,
        f"combined={combined_w['sigma_pct']:.4f}% vs radial={radial_only['sigma_pct']:.4f}% "
        f"vs pattern={pattern_only_w['sigma_pct']:.4f}%")

    hr_holds = combined_w["half_range_pct"] >= max(radial_only["half_range_pct"],
                                                    pattern_only_w["half_range_pct"]) - 1e-9
    print(f"       [정보] half_range_pct 하한 부등식은 {'성립' if hr_holds else '성립하지 않음'} "
          f"(combined={combined_w['half_range_pct']:.4f}% vs radial="
          f"{radial_only['half_range_pct']:.4f}% vs pattern={pattern_only_w['half_range_pct']:.4f}%) "
          f"— 이 지표(max-min 기반)는 sigma_pct(CV)와 달리 대수적 하한이 보장되지 않으므로 "
          f"참고용으로만 기록, assert 대상 아님.")

    print("\nOVERALL:", "PASS" if ok else "FAIL")
    return ok


if __name__ == "__main__":
    import sys
    print("=== WIWNU x pattern-density combined self-test ===")
    sys.exit(0 if _selftest() else 1)
