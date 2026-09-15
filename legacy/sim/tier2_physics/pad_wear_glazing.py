"""
패드 마모(glazing) → MRR 시간 드리프트 이산(discrete Monte-Carlo) 모델.

지식 근거: knowledge/materials/pad-wear-glazing-mrr-decay.md
  1차 출처: Shi & Ring, "CMP pad wear and polish-rate decay modeled by asperity
  population balance with fluid effect", Wear (2010),
  https://my.che.utah.edu/~ring/Publications-PDFs/J-135.pdf (저자 공개 PDF, 무료).
  이 노트가 인용하는 Borucki(2002)/Stein et al.(1996)/Oliver/Lawing 원문은 미확보
  (2차 인용, "미검증" 표기).

이 모듈은 gw_contact.py의 hertz_force/hertz_contact_area를 재사용하고(중복 재구현 금지),
gw_pressure_solve.py와 동일한 "명목압력 -> 하중평형 분리거리" 아이디어를 개별 asperity
집단(Monte-Carlo 표본)에 대해 이산적으로 반복 적용한다. Shi&Ring의 유체결합/PDE 해석해는
이번 범위에서 구현하지 않음(지식노트 §3에 명시) — 대신 Borucki 극한(유체 없음, 순수 asperity
하중분담)에서 Archard 마모법칙을 오일러 시간적분으로 적용해 정성적 거동만 재현한다:
  (1) 컨디셔닝 없이 방치하면 asperity 평균 높이가 단조 감소한다 (Oliver 실측 정성적 일치)
  (2) 그 결과 MRR(t) = c_w * p_r(t) (p_r=평균 실접촉압력=W/A_r) 도 단조 감소한다
  (3) 감쇠는 초반에 빠르고 후반에 느려지는(수확체감) 형태를 보인다 — 큰 asperity가 먼저
      깎이고 남은 것들의 마모속도(∝sqrt(z-d))가 점점 작아지기 때문 (지식노트 §2.3 Eq.10)

실행: python3 pad_wear_glazing.py -> self-test 결과 stdout.
"""
import math
import numpy as np
from scipy.optimize import brentq

from gw_contact import hertz_force, hertz_contact_area


def sample_heights(n, beta, rng):
    """지수분포 asperity 높이 표본. phi(z)=beta*exp(-beta z)."""
    return rng.exponential(1.0 / beta, size=n)


def total_load_discrete(heights, d, E_star, R):
    """분리거리 d에서 접촉 중인 asperity들의 총 하중 W(d)."""
    delta = heights - d
    delta = np.clip(delta, 0.0, None)
    # 벡터화된 Hertz: F = (4/3)E*sqrt(R)*delta^1.5
    return float(np.sum((4.0 / 3.0) * E_star * math.sqrt(R) * delta ** 1.5))


def total_area_discrete(heights, d, R):
    """분리거리 d에서 접촉 중인 asperity들의 총 실접촉면적 A_r(d)."""
    delta = heights - d
    delta = np.clip(delta, 0.0, None)
    return float(np.sum(math.pi * R * delta))


def solve_separation_discrete(heights, W_target, E_star, R, d_bracket=None):
    """이산 asperity 집단에 대해 W(d)=W_target을 만족하는 d를 브렌트법으로 구한다."""
    def f(d):
        return total_load_discrete(heights, d, E_star, R) - W_target

    if d_bracket is None:
        d_lo, d_hi = float(heights.min()) - 1e-9, float(heights.max())
    else:
        d_lo, d_hi = d_bracket

    f_lo, f_hi = f(d_lo), f(d_hi)
    if f_lo * f_hi > 0:
        # W_target이 최대 가능 하중(d=d_lo일 때)보다 크면 못 맞춤 -> 물리적으로 비정상 케이스
        raise RuntimeError(f"브라켓 실패: f(d_lo)={f_lo:.3e}, f(d_hi)={f_hi:.3e} (W_target이 범위를 벗어남)")
    return brentq(f, d_lo, d_hi, xtol=1e-15, rtol=1e-12)


def wear_step_borucki(heights, d, C1, dt):
    """
    Archard 마모법칙(유체 없는 Borucki 극한): dz/dt = -C1*sqrt(max(z-d,0))
    (지식노트 §2.3: L/A ∝ delta^0.5 이므로 dz/dt ∝ delta^0.5로 lump된 계수 C1 사용).
    heights를 in-place로 갱신하지 않고 새 배열을 반환.
    """
    delta = np.clip(heights - d, 0.0, None)
    dz = C1 * np.sqrt(delta) * dt
    new_heights = heights - dz
    # 물리적으로 asperity 높이는 d 아래로는 더 깎일 게 없음 (접촉 안 하므로) - clip 안전장치
    return new_heights


def simulate_pad_wear(
    n_asperity=20000,
    beta=1.0 / 0.3e-6,
    R=5e-6,
    E_star=1e9,
    P_app=20e3,       # 20 kPa 명목압력 (CMP 전형 오더)
    A_n=1e-4,         # 명목 접촉면적 1 cm^2
    c_w=1e-8,         # MRR 스케일 계수(임의 오더, self-test용 — 물리적 캘리브레이션 아님)
    C1=2e-6,          # 마모속도 계수 (임의 오더, self-test용 — 안정적 오일러 적분 위해 튜닝)
    n_steps=40,
    dt=1.0,
    seed=42,
):
    """
    컨디셔닝 없이(B=D=0, Shi&Ring 표기) n_steps 동안 패드 마모를 진행시키며
    MRR(t), 평균 실접촉압력 p_r(t), 평균 asperity 높이를 기록.
    반환: dict(t, MRR, p_r, mean_height, d)
    """
    rng = np.random.default_rng(seed)
    heights = sample_heights(n_asperity, beta, rng)
    W_target = P_app * A_n

    t_arr, mrr_arr, pr_arr, meanh_arr, d_arr = [], [], [], [], []

    for step in range(n_steps):
        t = step * dt
        d = solve_separation_discrete(heights, W_target, E_star, R,
                                       d_bracket=(-5.0 / beta, float(heights.max())))
        W = total_load_discrete(heights, d, E_star, R)
        A_r = total_area_discrete(heights, d, R)
        p_r = W / A_r if A_r > 0 else float("nan")
        mrr = c_w * p_r

        t_arr.append(t)
        mrr_arr.append(mrr)
        pr_arr.append(p_r)
        meanh_arr.append(float(heights.mean()))
        d_arr.append(d)

        heights = wear_step_borucki(heights, d, C1, dt)

    return {
        "t": np.array(t_arr),
        "MRR": np.array(mrr_arr),
        "p_r": np.array(pr_arr),
        "mean_height": np.array(meanh_arr),
        "d": np.array(d_arr),
    }


def _self_test():
    results = []

    # --- Test 1: 컨디셔닝 없이 평균 asperity 높이가 단조 감소 (Oliver 실측 정성적 일치) ---
    r = simulate_pad_wear(n_steps=30)
    h = r["mean_height"]
    diffs = np.diff(h)
    ok1 = bool(np.all(diffs <= 1e-15))  # 부동소수 오차 허용한 단조감소(비증가)
    results.append(("무컨디셔닝 시 평균 asperity 높이 단조 비증가 (glazing, Oliver 정성적 일치)",
                     ok1, f"h[0]={h[0]:.4e}m -> h[-1]={h[-1]:.4e}m, max_increase={diffs.max():.2e}"))

    # --- Test 2: MRR(t)이 단조 감소 (무컨디셔닝 rate decay, Shi&Ring/Stein 정성적 일치) ---
    mrr = r["MRR"]
    diffs_mrr = np.diff(mrr)
    ok2 = bool(np.all(diffs_mrr <= 1e-18))
    total_decay_pct = (mrr[0] - mrr[-1]) / mrr[0] * 100
    results.append(("MRR(t) 단조 감소 (컨디셔닝 없는 rate decay)",
                     ok2, f"MRR[0]={mrr[0]:.4e} -> MRR[-1]={mrr[-1]:.4e}, 감쇠={total_decay_pct:.2f}%"))

    # --- Test 3: 감쇠 곡선이 수확체감(초반 감쇠율 > 후반 감쇠율) — Eq.10의 sqrt(delta) 마모속도 특성 ---
    early_drop = mrr[0] - mrr[len(mrr) // 3]
    late_drop = mrr[2 * len(mrr) // 3] - mrr[-1]
    ok3 = bool(early_drop > late_drop)
    results.append(("감쇠 수확체감(초반 감쇠 > 후반 감쇠, 큰 asperity가 먼저 깎임)",
                     ok3, f"초반1/3 감쇠={early_drop:.4e}, 후반1/3 감쇠={late_drop:.4e}"))

    # --- Test 4: 이산 시뮬레이터의 정적(t=0) 결과가 gw_contact.py 연속 GW 모델과 오더 일치 ---
    from gw_contact import gw_numeric
    r0 = simulate_pad_wear(n_steps=1, n_asperity=200000)  # 표본 크게 해서 통계오차 축소
    d0 = r0["d"][0]
    # 동일 파라미터로 연속모델 gw_numeric 호출
    cont = gw_numeric(d0, beta=1.0 / 0.3e-6, eta=200000 / 1e-4, A_n=1e-4, E_star=1e9, R=5e-6)
    W_disc = r0["p_r"][0] * (r0["p_r"][0] and (20e3 * 1e-4) / r0["p_r"][0] * r0["p_r"][0])  # noqa
    # 더 직접적으로: 이산 p_r vs 연속 p_r 비교
    p_r_cont = cont["W"] / cont["A_r"] if cont["A_r"] > 0 else float("nan")
    p_r_disc = r0["p_r"][0]
    rel_err = abs(p_r_disc - p_r_cont) / p_r_cont
    ok4 = bool(rel_err < 0.1)  # Monte-Carlo 표본오차 감안 10% 이내
    results.append(("이산 Monte-Carlo t=0 p_r가 연속 GW gw_numeric()과 오더 일치 (교차검증)",
                     ok4, f"discrete p_r={p_r_disc:.4e} Pa, continuum p_r={p_r_cont:.4e} Pa, rel_err={rel_err:.2%}"))

    # --- Test 5: p_r(=W/A_r)가 시간에 따라 변한다는 것 자체가 Lv2-2 결론(정적 p_r 불변)과 다른 레짐임을 확인 ---
    # Lv2-2는 "고정된 분포에서 압력을 바꿀 때" p_r 불변을 보였다. 여기서는 압력 고정, 분포(heights)가
    # 시간에 따라 변하므로 p_r도 변해야 한다 -- 두 결과가 모순이 아니라 서로 다른 변수를 바꾼 것임을 확인.
    pr = r["p_r"]
    pr_change_pct = abs(pr[-1] - pr[0]) / pr[0] * 100
    ok5 = bool(pr_change_pct > 1.0)  # 유의미하게 변해야 함 (Lv2-2의 <0.1%와 대비)
    results.append(("분포 마모 시 p_r 유의미하게 변화 (Lv2-2 '압력 변화 시 p_r 불변'과 다른 레짐임을 대비 확인)",
                     ok5, f"p_r[0]={pr[0]:.4e} -> p_r[-1]={pr[-1]:.4e}, 변화율={pr_change_pct:.2f}% (Lv2-2 기록: <0.1%)"))

    print("=== pad_wear_glazing.py self-test ===")
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
