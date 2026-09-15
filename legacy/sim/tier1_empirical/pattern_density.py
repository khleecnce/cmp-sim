"""
패턴 밀도 의존 CMP 모델 (dishing/erosion, MIT effective-density / step-height).

담당 에이전트: process-integrator (Lv3-1)
근거 지식노트: knowledge/cmp/pattern-dependent-dishing-erosion.md
              knowledge/cmp/wiwnu-pressure-velocity-wafer-scale.md (국소 P 증폭과 연결)
              knowledge/cmp/preston-luo-dornfeld-mrr.md (blanket rate K = Kp·P·V)

────────────────────────────────────────────────────────────────────
모델 (출처: Boning et al., MRS Spring 1999 "Pattern Dependent Modeling for
      CMP Optimization and Control"; Stine et al., IEEE TSM 1998; Ouma PhD 1999)
────────────────────────────────────────────────────────────────────
1) Effective density (유효밀도):
     rho_eff(x) = (w * rho_local)(x)     ← 국소 밀도맵과 가중필터 w의 컨볼루션
   w 의 특성길이 = planarization length PL. (Ouma의 물리적 커널은 탄성패드 굽힘
   변형 프로파일 → 타원형(elliptic) 가중; 여기서는 정규화 가우시안으로 근사.
   정확한 elliptic 적분형(MRS99 eq.2)은 재현하지 않음 — 노트에 미검증 표기.)

2) Density-based 제거율 (MRS99 eq.1):
     RR_up(x) = K / rho_eff(x)
   즉 raised(볼록) 영역 제거율은 유효밀도에 반비례. 밀한 곳(rho_eff 큼)은 하중이
   여러 피처로 분산 → 국소압 작음 → 느리게 깎임 → 두껍게 남음.
   -> 최종 산화막 두께맵이 rho_eff 맵과 직접 대응(MRS99 본문 서술).

3) Step-height 진화 두 레짐:
   (a) 비압축성 패드(Grillaert): 패드가 down영역에 안 닿음 → up만 K/rho로 깎임 →
       step 이 선형 감소, 시간 t_c = rho*h0/K 에 소멸.
   (b) 압축성 패드(Burke/Tseng): step reduction rate ∝ 남은 step → step 지수감쇠
       h(t) = h_c * exp(-(t - t_c)/tau).
   통합모델(Smith): 접촉높이 h1 = a1 + a2*exp(-rho/a3) 에서 (a)->(b) 전이.

4) Overpolish dishing/erosion (removal-rate diagram, MRS99 Fig.13):
     Cu(트렌치) 제거율 = RR_m*(1 - d/dmax)         (dishing d 증가 시 선형 감소)
     oxide(스페이스) 제거율 = RR_ox/(1 - rho_m) * (1 + b*d)  (d 증가 시 증가)
   두 rate가 같아지는 정상상태 dishing d_ss 가 관측 최대 dishing.

검증 결과는 하단 self-test 참조.
"""
from __future__ import annotations

import numpy as np


# ────────────────────────────────────────────────────────────────
# 1) Effective density
# ────────────────────────────────────────────────────────────────
def gaussian_weight(dx: np.ndarray, PL: float) -> np.ndarray:
    """정규화 가우시안 가중필터. 특성길이 PL(=planarization length)을 표준편차로.

    Ouma의 물리적 커널은 탄성패드 굽힘에서 유도한 타원형(elliptic)이며 이 가우시안은
    tractable 근사다(노트 미검증 표기). 핵심 성질(정규화·PL 스케일 평활)만 재현.
    """
    w = np.exp(-0.5 * (dx / PL) ** 2)
    return w / w.sum()  # 합=1 정규화 (uniform in -> same uniform out 보장)


def effective_density(x: np.ndarray, rho_local: np.ndarray, PL: float) -> np.ndarray:
    """국소 밀도맵을 PL 스케일 가중필터로 컨볼루션 → 유효밀도(1D)."""
    dx0 = x[1] - x[0]
    half = int(np.ceil(4 * PL / dx0))
    kx = np.arange(-half, half + 1) * dx0
    w = gaussian_weight(kx, PL)
    # 경계는 edge 값으로 반사(패딩) — 유한 die 근사
    padded = np.pad(rho_local, half, mode="edge")
    return np.convolve(padded, w, mode="valid")


# ────────────────────────────────────────────────────────────────
# 2)+3a) Stine 비압축성(density) 모델: 산화막 제거량(raised area)
# ────────────────────────────────────────────────────────────────
def oxide_removed_up(t: float, K: float, rho_eff: np.ndarray,
                     h0: float) -> np.ndarray:
    """raised(up) 영역에서 시간 t 까지 깎인 산화막 두께.

    step 존재 구간(t < t_c=rho*h0/K): 제거량 = (K/rho)*t
    평탄화 후(t > t_c): 제거량 = h0 + K*(t - t_c)  (blanket rate K)
    """
    rho = np.asarray(rho_eff, float)
    t_c = rho * h0 / K            # 국소 평탄화 시각(밀도 종속)
    before = (K / rho) * t
    after = h0 + K * (t - t_c)
    return np.where(t < t_c, before, after)


def step_height_incompressible(t: float, K: float, rho_eff: np.ndarray,
                               h0: float) -> np.ndarray:
    """비압축성 패드: step 선형감소 h(t)=max(h0 - (K/rho)*t, 0)."""
    rho = np.asarray(rho_eff, float)
    return np.maximum(h0 - (K / rho) * t, 0.0)


# ────────────────────────────────────────────────────────────────
# 3b) 압축성 패드: step 지수감쇠
# ────────────────────────────────────────────────────────────────
def step_height_compressible(t: np.ndarray, h_c: float, t_c: float,
                             tau: float) -> np.ndarray:
    """접촉시각 t_c 이후 step 지수감쇠 h = h_c*exp(-(t-t_c)/tau)."""
    t = np.asarray(t, float)
    return np.where(t <= t_c, h_c, h_c * np.exp(-(t - t_c) / tau))


def contact_height(rho_eff: np.ndarray, a1: float, a2: float,
                   a3: float) -> np.ndarray:
    """통합모델 접촉높이 h1 = a1 + a2*exp(-rho/a3) (MRS99 eq.4)."""
    return a1 + a2 * np.exp(-np.asarray(rho_eff, float) / a3)


# ────────────────────────────────────────────────────────────────
# 4) Overpolish removal-rate diagram → 정상상태 dishing
# ────────────────────────────────────────────────────────────────
def steady_state_dishing(RR_m: float, RR_ox: float, rho_m: float,
                         dmax: float, b: float) -> float:
    """Cu rate = oxide rate 가 되는 정상상태 dishing d_ss.

    Cu:    r_cu(d)  = RR_m * (1 - d/dmax)          (d↑ → 감소)
    oxide: r_ox(d)  = RR_ox/(1-rho_m) * (1 + b*d)   (d↑ → 증가)
    두 식을 같게 두고 d 에 대해 풀면 d_ss.
    """
    A = RR_ox / (1.0 - rho_m)
    # RR_m - RR_m/dmax * d = A + A*b*d
    #  d*(RR_m/dmax + A*b) = RR_m - A
    d_ss = (RR_m - A) / (RR_m / dmax + A * b)
    return float(np.clip(d_ss, 0.0, dmax))


# ────────────────────────────────────────────────────────────────
# self-test
# ────────────────────────────────────────────────────────────────
def _selftest() -> None:
    rng = np.random.default_rng(0)
    passed = 0
    total = 0

    def check(name, cond, detail=""):
        nonlocal passed, total
        total += 1
        ok = bool(cond)
        passed += ok
        print(f"  [{'PASS' if ok else 'FAIL'}] {name}  {detail}")

    print("pattern_density.py self-test")

    # T1: 가중필터 정규화 → 균일 밀도 입력이면 동일 균일 출력 (편향 없음)
    x = np.linspace(0, 20.0, 2001)            # mm
    rho_u = np.full_like(x, 0.5)
    reff_u = effective_density(x, rho_u, PL=3.0)
    check("weight normalized: uniform-in→uniform-out",
          np.allclose(reff_u, 0.5, atol=1e-9),
          f"max dev={np.max(np.abs(reff_u-0.5)):.2e}")

    # T2: effective density 는 step 밀도를 PL 스케일로 평활 (edge overshoot 없음,
    #     경계에서 두 평탄값 사이 단조전이) — 밀도맵이 매끄러워짐
    rho_step = np.where(x < 10.0, 0.2, 0.8)
    reff_s = effective_density(x, rho_step, PL=2.0)
    within = (reff_s >= 0.2 - 1e-6) & (reff_s <= 0.8 + 1e-6)
    # 전이폭이 유한(≈ 수*PL)해야: 0.3~0.7 구간이 존재
    trans = np.sum((reff_s > 0.3) & (reff_s < 0.7))
    check("effective density smooths step density (no overshoot)",
          within.all() and trans > 10,
          f"range=[{reff_s.min():.3f},{reff_s.max():.3f}], transition pts={trans}")

    # T3: 밀도 모델 핵심 불변량 — step 구간에서 (제거량 × rho_eff) = K·t (상수)
    #     즉 밀한 곳은 덜 깎이고 성긴 곳은 더 깎인다(제거량 ∝ 1/rho).
    K = 3000.0   # A/min (blanket)
    h0 = 6000.0  # A step
    rho_vals = np.array([0.2, 0.4, 0.6, 0.8])
    t = 0.5      # min, t_c=rho*h0/K = rho*2 min → 모두 step 구간(t<t_c: rho>0.25)
    rho_in = rho_vals[rho_vals > t * K / h0]     # step 아직 존재하는 것만
    removed = oxide_removed_up(t, K, rho_in, h0)
    invariant = removed * rho_in
    check("density model invariant: removed*rho_eff = K*t (step regime)",
          np.allclose(invariant, K * t, rtol=1e-12),
          f"K*t={K*t:.1f}, spread={np.ptp(invariant):.2e}")
    check("denser region removes less (thicker oxide remains)",
          np.all(np.diff(removed) < 0),
          f"removed(rho={rho_in})={np.round(removed,1)}")

    # T4: 비압축성 step 은 t_c=rho*h0/K 에 정확히 소멸(선형)
    rho1 = 0.5
    t_c = rho1 * h0 / K
    h_just_before = step_height_incompressible(t_c * 0.999, K, np.array([rho1]), h0)[0]
    h_at = step_height_incompressible(t_c, K, np.array([rho1]), h0)[0]
    check("incompressible step vanishes at t_c=rho*h0/K",
          h_at <= 1e-6 and h_just_before > 0,
          f"t_c={t_c:.3f}min, h(t_c)={h_at:.2e}, h(0.999 t_c)={h_just_before:.1f}")

    # T5: 압축성 step 지수감쇠 — 합성데이터에서 tau 회수(로그선형 피팅)
    tau_true = 0.8
    h_c, t_c2 = 1200.0, 0.3
    tt = np.linspace(t_c2, t_c2 + 3.0, 60)
    h = step_height_compressible(tt, h_c, t_c2, tau_true)
    h_noisy = h * (1 + 0.01 * rng.standard_normal(h.size))
    slope = np.polyfit(tt - t_c2, np.log(h_noisy), 1)[0]
    tau_fit = -1.0 / slope
    check("compressible step: recover tau from synthetic decay",
          abs(tau_fit - tau_true) / tau_true < 0.02,
          f"tau_true={tau_true}, tau_fit={tau_fit:.4f}")

    # T6: 접촉높이 단조 — 밀도 높을수록 h1 낮음(a2>0), 극한값 a1
    r = np.array([0.1, 0.5, 0.9])
    h1 = contact_height(r, a1=200.0, a2=2000.0, a3=0.3)
    check("contact height h1 decreases with density → a1",
          np.all(np.diff(h1) < 0) and abs(h1[-1] - (200 + 2000*np.exp(-3))) < 1e-6,
          f"h1={np.round(h1,1)}")

    # T7: 정상상태 dishing — Cu rate 와 oxide rate 가 d_ss 에서 실제로 같은지 대입검증
    RR_m, RR_ox, rho_m, dmax, b = 3000.0, 1000.0, 0.5, 2000.0, 0.0008
    d_ss = steady_state_dishing(RR_m, RR_ox, rho_m, dmax, b)
    r_cu = RR_m * (1 - d_ss / dmax)
    r_ox = RR_ox / (1 - rho_m) * (1 + b * d_ss)
    check("steady-state dishing: Cu rate == oxide rate at d_ss",
          abs(r_cu - r_ox) < 1e-6 and 0 < d_ss < dmax,
          f"d_ss={d_ss:.1f} A, r_cu={r_cu:.2f}, r_ox={r_ox:.2f}")
    # 물리 sanity: 필드 oxide 제거(=erosion)가 느릴수록 Cu는 더 깊이 dishing 되어야
    #  두 rate가 균형 → 낮은 oxide rate → 더 큰 dishing (Cu가 필드를 못 따라감).
    d_low_ox = steady_state_dishing(RR_m, 800.0, rho_m, dmax, b)
    check("lower oxide (field) removal rate → MORE dishing",
          d_low_ox > d_ss,
          f"d_ss(RRox=1000)={d_ss:.1f} vs d_ss(RRox=800)={d_low_ox:.1f}")

    print(f"\n{passed}/{total} PASS")
    if passed != total:
        raise SystemExit(1)


if __name__ == "__main__":
    _selftest()
