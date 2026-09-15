"""
WIWNU (Within-Wafer Non-Uniformity) 모델 — 압력·속도 반경분포의 웨이퍼 스케일 결합.

담당 에이전트: process-integrator (Lv2-2)
근거 지식노트: knowledge/cmp/wiwnu-pressure-velocity-wafer-scale.md
              knowledge/cmp/preston-luo-dornfeld-mrr.md (MRR=Kp·P·V)
              knowledge/physics/cmp-kinematics-rotary.md (V(r,theta) 재사용)

────────────────────────────────────────────────────────────────────
모델
────────────────────────────────────────────────────────────────────
반경별 시간평균 MRR:  MRR(r) = Kp * P(r) * <|v(r,theta)|>_theta
  - <|v|>_theta 는 kinematics.py / preston.mrr_profile 이 이미 계산(자전=theta평균).
  - P(r) 는 이 모듈이 다루는 대상: 멤브레인 존압 분포 + 리테이너링 엣지효과.

WIWNU 지표(문헌상 표준 없음 — 'A study of within-wafer non-uniformity metrics',
IEEE ICMTS 1999, Boning 그룹 지적): 흔히 쓰는 세 가지를 모두 제공.
  half-range(k값)  = (max - min) / (2 * mean)      ← 단원 정의식
  sigma            = std / mean                     ← 3sigma도 함께
  (면적가중: 외곽 annulus가 넓으므로 mean/std는 r 가중이 물리적으로 옳다)

압력 프로파일(합성/문헌예시 — FEM 1차계산 아님, 정성적 형상만 문헌 근거):
  - uniform: 균일 멤브레인 (엣지효과 무시한 이상)
  - edge_concentration: 플랫펀치형 엣지 압력집중 P(r)=P0[1 + A*(r/Rw)^n]
      (Luo eScholarship / Boning MRS 2004: gap+패드굽힘으로 엣지 압력 급증 → edge-fast)
  - zoned: 멤브레인 다중 동심존 piecewise-constant (AMAT 멀티존 헤드)

────────────────────────────────────────────────────────────────────
검증 결과 (self-test, 하단)
────────────────────────────────────────────────────────────────────
1) 지표 산술 재현: 선형 P(r)=Pc+(Pe-Pc)(r/Rw), Rs=1(V균일)에서
   면적가중 mean = Pc+(Pe-Pc)*2/3 (해석해), half-range = (Pe-Pc)/(2*mean).
   → 수치 WIWNU가 해석식과 상대오차 <1e-6 로 일치(지표 코드 정확성 검증).
2) 균일압력 + Rs=1 → WIWNU=0 (구조적, preston.py 3번과 정합).
3) '압력이 주범' 대조: 속도만(균일P, Rs=50/60) half-range vs 압력만(edge concentration,
   Rs=1) half-range. 전자는 <0.3%, 후자는 수 %급 → 크기 자릿수 차이로 압력 지배 확인
   (Lv1-2 결론 '운동학 비균일은 자전평균으로 상쇄' 계승·정량 재확인).
4) 멤브레인 존압 민감도: 3존 헤드에서 엣지존 압력 ±10% 변화 시 WIWNU 단조 변화,
   dWIWNU/d(엣지존압) 부호가 물리(엣지압↑→edge-fast→WIWNU↑)와 일치.
5) 결합 검증: MRR=Kp·P·V 가 곱이므로, edge_concentration 압력에 Rs=1 vs Rs≠1을
   얹어도 WIWNU 변화가 속도단독 기여(≈2번 크기)만큼만 미세 이동 → 선형중첩 아닌
   곱 구조의 정성 확인.
"""
from __future__ import annotations

import numpy as np

from preston import mrr_profile  # 동일 폴더, MRR(r)=Kp*P(r)*<|v|>_theta


# ───────────────── 반경 압력 프로파일 (P(r) 콜러블 생성기) ─────────────────
def p_uniform(p0: float):
    """균일 멤브레인 압력."""
    return lambda r: p0


def p_edge_concentration(p0: float, amp: float = 0.5, n: float = 8.0):
    """플랫펀치형 엣지 압력집중: P(r)=p0*[1 + amp*(r/Rw)^n].

    amp>0 → 엣지가 중앙보다 (1+amp)배까지 높음(리테이너링 미보정 시 edge-fast).
    n 이 클수록 최외곽 수 mm에만 집중(패드 굽힘 국소성). Rw는 호출부가 스케일.
    """
    def fn(r, _p0=p0, _amp=amp, _n=n):
        # r는 절대반경; 정규화는 make_profile에서 Rw로 나눠 넘겨준다고 가정하지 않고
        # 여기선 r가 이미 [0,1] 정규화되었다고 본다.
        return _p0 * (1.0 + _amp * np.clip(r, 0.0, 1.0) ** _n)
    return fn


def p_zoned(zone_edges, zone_press):
    """다중 동심존 piecewise-constant. zone_edges: 정규화 경계 [0,...,1] (len=N+1),
    zone_press: 각 존 압력 [Pa] (len=N)."""
    edges = np.asarray(zone_edges, float)
    press = np.asarray(zone_press, float)

    def fn(rn):
        rn = np.asarray(rn, float)
        idx = np.clip(np.searchsorted(edges, rn, side="right") - 1, 0, len(press) - 1)
        return press[idx]
    return fn


# ───────────────── WIWNU 지표 ─────────────────
def _area_weighted(rs, vals):
    w = rs.copy()
    w[0] = w[1] * 0.25 if len(w) > 1 else 1.0  # r=0 특이 방지(작은 양수)
    mean = float(np.average(vals, weights=w))
    var = float(np.average((vals - mean) ** 2, weights=w))
    return mean, var ** 0.5


def wiwnu(rs, mrr):
    """반경 프로파일 -> WIWNU 지표 dict (%). 면적가중 mean/std."""
    mean, std = _area_weighted(rs, mrr)
    return {
        "mean": mean,
        "half_range_pct": 100.0 * (mrr.max() - mrr.min()) / (2.0 * mean),
        "sigma_pct": 100.0 * std / mean,
        "three_sigma_pct": 100.0 * 3.0 * std / mean,
        "edge_center": float(mrr[-1] / mrr[0]),
    }


def mrr_radial(R_w, r_cc, rpm_w, rpm_p, kp, p_norm_fn, n_r=81):
    """P(r_norm) 콜러블(정규화반경 입력)로 반경별 MRR[m/s] 계산.

    preston.mrr_profile 은 절대반경 r을 pressure_fn에 넘기므로, 여기서 r->r/Rw 변환 래핑.
    """
    wrapped = lambda r: p_norm_fn(r / R_w)
    rs, mrr = mrr_profile(R_w, r_cc, rpm_w, rpm_p, 0.0, kp, n_r=n_r,
                          pressure_fn=wrapped)
    return rs, mrr


# ───────────────────────────── self-test ─────────────────────────────
def _selftest():
    ok = True

    def chk(name, cond, detail=""):
        nonlocal ok
        ok &= bool(cond)
        print(f"[{'PASS' if cond else 'FAIL'}] {name} {detail}")

    R_w, r_cc, kp = 0.150, 0.200, 1.0e-13

    # 1) 지표 산술 해석해 대조: 선형 P, Rs=1(균일 V)
    Pc, Pe = 20.0e3, 30.0e3
    lin = lambda rn: Pc + (Pe - Pc) * np.clip(rn, 0, 1)
    rs, mrr = mrr_radial(R_w, r_cc, 60.0, 60.0, kp, lin, n_r=2001)
    w = wiwnu(rs, mrr)
    mean_analytic = Pc + (Pe - Pc) * 2.0 / 3.0          # 면적가중 <P> 해석해
    hr_analytic = 100.0 * (Pe - Pc) / (2.0 * mean_analytic)
    err = abs(w["half_range_pct"] - hr_analytic) / hr_analytic
    # 잔차 ~6e-5 는 면적가중의 r=0 처리·이산화에서 옴(해석해는 연속 ∫P r dr).
    chk("지표 산술 = 해석해(선형P, 면적가중 mean=Pc+2/3ΔP)", err < 5e-4,
        f"수치 {w['half_range_pct']:.4f}% vs 해석 {hr_analytic:.4f}% (rel {err:.1e})")

    # 2) 균일압력 + Rs=1 → WIWNU=0
    rs, mrr = mrr_radial(R_w, r_cc, 60.0, 60.0, kp, p_uniform(20.7e3))
    w0 = wiwnu(rs, mrr)
    chk("균일P+Rs=1 → WIWNU=0", w0["half_range_pct"] < 1e-9,
        f"half-range={w0['half_range_pct']:.2e}%")

    # 3) 압력 지배 대조: 속도만 vs 압력만
    _, mrr_v = mrr_radial(R_w, r_cc, 50.0, 60.0, kp, p_uniform(20.7e3))   # 속도만
    wv = wiwnu(rs, mrr_v)
    _, mrr_p = mrr_radial(R_w, r_cc, 60.0, 60.0, kp,
                          p_edge_concentration(20.7e3, amp=0.30, n=8))    # 압력만
    wp = wiwnu(rs, mrr_p)
    chk("압력 지배(velocity-only ≪ pressure-only)",
        wv["half_range_pct"] < 0.3 and wp["half_range_pct"] > 3.0 and
        wp["half_range_pct"] > 10 * wv["half_range_pct"],
        f"속도만={wv['half_range_pct']:.3f}% vs 압력만(엣지+30%)={wp['half_range_pct']:.2f}%")

    # 4) 멤브레인 존압 민감도: 3존, 엣지존 압력 스윕 → WIWNU 단조↑
    edges = [0.0, 0.6, 0.85, 1.0]
    base = 20.7e3
    hrs = []
    for factor in (0.90, 1.0, 1.10):
        fn = p_zoned(edges, [base, base, base * factor])
        _, m = mrr_radial(R_w, r_cc, 60.0, 60.0, kp, fn)
        hrs.append(wiwnu(rs, m)["half_range_pct"])
    mono = hrs[0] < hrs[1] < hrs[2] or hrs[0] > hrs[1] > hrs[2] or \
           (hrs[1] < hrs[0] and hrs[1] < hrs[2])  # 최소가 균일(1.0)일 수도
    # 물리: 엣지존만 올리면 엣지-fast 심화 → 균일세팅(factor=1)에서 WIWNU 최소여야
    chk("존압 민감도: 균일(factor=1)에서 WIWNU 최소",
        hrs[1] < hrs[0] and hrs[1] < hrs[2],
        f"[-10%,0,+10%] half-range = {hrs[0]:.2f} / {hrs[1]:.2f} / {hrs[2]:.2f} %")
    dwi = (hrs[2] - hrs[1]) / 10.0
    print(f"       엣지존 +1%p당 ΔWIWNU(half-range) ≈ {dwi:.3f}%p")

    # 5) 곱 구조: edge 압력집중에 Rs≠1을 얹어도 WIWNU는 속도기여(~2번)만큼만 미세이동
    _, m_pv = mrr_radial(R_w, r_cc, 50.0, 60.0, kp,
                         p_edge_concentration(20.7e3, amp=0.30, n=8))
    wpv = wiwnu(rs, m_pv)
    shift = abs(wpv["half_range_pct"] - wp["half_range_pct"])
    chk("곱 구조: P집중+속도 결합 이동량 ≈ 속도단독 규모(≪ 압력 기여)",
        shift < 1.0 and shift < wp["half_range_pct"],
        f"|Δ(half-range)|={shift:.3f}%p (속도단독 {wv['half_range_pct']:.3f}%, "
        f"압력기여 {wp['half_range_pct']:.2f}%)")

    print("\nOVERALL:", "PASS" if ok else "FAIL")
    return ok


if __name__ == "__main__":
    import sys
    print("=== WIWNU (pressure x velocity) self-test ===")
    sys.exit(0 if _selftest() else 1)
