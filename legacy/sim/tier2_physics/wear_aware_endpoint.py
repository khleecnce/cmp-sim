"""
패드 마모 드리프트를 반영한 엔드포인트 시간 통합 모듈.

배경: process_time.py는 Preston MRR이 시간에 따라 변하지 않는다는 정상상태
가정 위에서 removed_thickness = MRR*t, endpoint_time = target/MRR_ref로
단순 적분한다. 그러나 pad_wear_glazing.py는 컨디셔닝이 없을 때 asperity
마모(glazing)로 MRR(t)이 실제로는 단조 감소함을 이산 Monte-Carlo로 보였다.
이 모듈은 새 물리 지식을 추가하지 않고, 두 모듈이 이미 검증한 결과를
그대로 이어붙여(pad_wear_glazing의 MRR(t) 시계열을 사다리꼴 적분) 정상상태
가정(v0)이 무컨디셔닝 장시간 폴리싱에서 실제보다 얼마나 낙관적인
엔드포인트 예측을 내는지 정량화한다.

pad_wear_glazing.py / process_time.py는 수정하지 않고 import만 한다.

실행: python3 wear_aware_endpoint.py -> self-test 결과 stdout.
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "tier1_empirical"))

import numpy as np

from pad_wear_glazing import simulate_pad_wear
from process_time import endpoint_time


def cumulative_removed_thickness_drift(t_arr, mrr_arr) -> np.ndarray:
    """MRR(t) 시계열을 사다리꼴 적분해 누적 제거두께를 구한다 [m].

    반환 배열의 shape은 t_arr과 동일하며, [0]=0 (t_arr[0]까지 누적 제거두께).
    """
    t_arr = np.asarray(t_arr, dtype=float)
    mrr_arr = np.asarray(mrr_arr, dtype=float)
    cum = np.zeros_like(t_arr)
    if len(t_arr) > 1:
        dt = np.diff(t_arr)
        trap = 0.5 * (mrr_arr[1:] + mrr_arr[:-1]) * dt
        cum[1:] = np.cumsum(trap)
    return cum


def endpoint_time_drift(target_thickness_m: float, t_arr, mrr_arr) -> float:
    """누적 제거두께가 target_thickness_m에 도달하는 시각 [s]을 선형보간으로 구한다."""
    t_arr = np.asarray(t_arr, dtype=float)
    cum = cumulative_removed_thickness_drift(t_arr, mrr_arr)

    if target_thickness_m > cum[-1]:
        raise RuntimeError(
            f"target_thickness_m={target_thickness_m:.4e}m이 시뮬레이션 구간 내 "
            f"누적 제거두께 최대값({cum[-1]:.4e}m)에 도달하지 못함. "
            "pad_wear_glazing.simulate_pad_wear()의 n_steps/dt를 늘리거나 "
            "target_thickness_m을 낮춰라."
        )

    return float(np.interp(target_thickness_m, cum, t_arr))


def compare_naive_vs_drift(target_thickness_m: float, pad_wear_kwargs: dict | None = None) -> dict:
    """정상상태(v0) 순진한 예측과 마모 드리프트 인지 예측을 비교한다.

    "순진한 예측"은 process_time.py를 드리프트 사실을 모른 채 그대로 쓸 때 실제로
    벌어지는 일 — 공정 시작 시점의 초기 MRR(mrr_arr[0])을 종료까지 그대로 쓴다고
    가정하는 것 — 을 재현한다.
    """
    kwargs = pad_wear_kwargs or {}
    r = simulate_pad_wear(**kwargs)
    t_arr, mrr_arr = r["t"], r["MRR"]

    t_naive = endpoint_time(target_thickness_m, mrr_arr[0])
    t_drift = endpoint_time_drift(target_thickness_m, t_arr, mrr_arr)
    optimism_pct = (t_drift - t_naive) / t_naive * 100.0

    return {
        "t_naive": t_naive,
        "t_drift": t_drift,
        "optimism_pct": optimism_pct,
        "t_arr": t_arr,
        "mrr_arr": mrr_arr,
    }


# ───────────────────────────── self-test ─────────────────────────────
def _selftest():
    ok = True

    def chk(name, cond, detail=""):
        nonlocal ok
        ok &= bool(cond)
        print(f"[{'PASS' if cond else 'FAIL'}] {name} {detail}")

    # 1) 적분 일관성: cumulative의 마지막 값 == np.trapezoid(전체 구간) 상대오차 <1e-9
    r = simulate_pad_wear(n_steps=40)
    t_arr, mrr_arr = r["t"], r["MRR"]
    cum = cumulative_removed_thickness_drift(t_arr, mrr_arr)
    full_trapz = np.trapezoid(mrr_arr, t_arr)
    rel_err1 = abs(cum[-1] - full_trapz) / full_trapz
    chk("cumulative 적분 마지막 값이 np.trapezoid(전체구간)과 일치",
        rel_err1 < 1e-9, f"cum[-1]={cum[-1]:.6e}, trapz={full_trapz:.6e}, rel_err={rel_err1:.2e}")

    # 2) 드리프트 없음(C1=0) 극한에서 process_time.py로 정확히 축소되는 회귀 검증
    r0 = simulate_pad_wear(n_steps=40, C1=0.0)
    t0, mrr0 = r0["t"], r0["MRR"]
    mrr_spread = (mrr0.max() - mrr0.min()) / mrr0.mean()
    target_const = 0.5 * cumulative_removed_thickness_drift(t0, mrr0)[-1]
    t_drift0 = endpoint_time_drift(target_const, t0, mrr0)
    t_v0 = endpoint_time(target_const, mrr0[0])
    rel_err2 = abs(t_drift0 - t_v0) / t_v0
    chk("C1=0(마모 없음) 극한에서 endpoint_time_drift가 process_time.endpoint_time과 일치",
        rel_err2 < 0.01,
        f"MRR 변동폭={mrr_spread:.2e}(거의 상수), t_drift={t_drift0:.4f}s, t_v0={t_v0:.4f}s, rel_err={rel_err2:.2%}")

    # 3) 정성적 방향: optimism_pct > 0
    # MRR이 마모로 단조 감소하므로, "초기 MRR이 끝까지 유지된다"고 가정하는 naive는
    # 실제 평균 MRR보다 큰 값으로 나누어 시간을 계산 -> t_naive를 과소평가(실제보다 빨리
    # 끝난다고 낙관) -> t_drift가 t_naive보다 커서 optimism_pct가 항상 양수가 된다.
    target_drift = 0.5 * cumulative_removed_thickness_drift(r["t"], r["MRR"])[-1]
    cmp = compare_naive_vs_drift(target_drift, pad_wear_kwargs={"n_steps": 40})
    chk("optimism_pct > 0 (naive가 실제보다 빨리 끝난다고 낙관)",
        cmp["optimism_pct"] > 0,
        f"t_naive={cmp['t_naive']:.4f}s, t_drift={cmp['t_drift']:.4f}s, optimism_pct={cmp['optimism_pct']:.2f}%")

    # 4) 목표두께 도달 불가 시 RuntimeError
    r4 = simulate_pad_wear(n_steps=40)
    huge_target = cumulative_removed_thickness_drift(r4["t"], r4["MRR"])[-1] * 1000.0
    raised = False
    try:
        endpoint_time_drift(huge_target, r4["t"], r4["MRR"])
    except RuntimeError:
        raised = True
    chk("도달 불가능한 target에 대해 RuntimeError 발생", raised)

    print("\nOVERALL:", "PASS" if ok else "FAIL")
    return ok


if __name__ == "__main__":
    import sys
    print("=== wear_aware_endpoint.py self-test ===")
    sys.exit(0 if _selftest() else 1)
