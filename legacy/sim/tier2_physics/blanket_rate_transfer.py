"""NPW 블랭킷 순간속도 전이 함수 - 60 s 평균 rate와 모델이 요구하는 순간 포화 rate a1의 괴리.

지식 근거: knowledge/cmp/npw-ptw-transfer-rules-quantitative.md §3, §6 verify (B)
  (Tugbawa 2002, MIT EECS PhD thesis, dspace.mit.edu/handle/1721.1/8083, 표 3.3, eq.3.51-3.53)

계약 (엔진과의 경계):
  이 모듈은 순수 함수 라이브러리다. engine.py / models.py에 등록하지 않는다.
  사유: Recipe에 시간축(시계열 폴리시 진행) 스키마가 없어 engine.Model로 조립할
  입력이 아직 없다. 다른 tier2_physics의 미등록 모듈들(S17 이하)과 같은 지위.

함수:
  cumulative_removal(t, a1, a2, tau)       -> eq.3.51: 누적 제거량 AR(t) [Å]
  blanket_rate_average(t, a1, a2, tau)     -> eq.3.52: 평균 rate r_avg(t) = AR(t)/t [Å/s]
  blanket_rate_instantaneous(t, a1, a2, tau) -> eq.3.53: 순간 rate r_inst(t) [Å/s]
  fit_blanket_rate(times, removed)         -> (times, removed) 관측쌍에서 (a1, a2, tau) 역추정
"""
from __future__ import annotations

import math


def cumulative_removal(t: float, a1: float, a2: float, tau: float) -> float:
    """eq.3.51: 누적 제거량 AR(t) [Å]. a1: 포화 순간속도[Å/s], a2: [Å], tau: 시상수[s]."""
    return a1 * t + a2 * (math.exp(-t / tau) - 1)


def blanket_rate_average(t: float, a1: float, a2: float, tau: float) -> float:
    """eq.3.52: 평균 rate r_avg(t) = AR(t)/t [Å/s]. t<=0이면 ValueError."""
    if t <= 0:
        raise ValueError("t must be > 0 for average rate")
    return cumulative_removal(t, a1, a2, tau) / t


def blanket_rate_instantaneous(t: float, a1: float, a2: float, tau: float) -> float:
    """eq.3.53: 순간 rate r_inst(t) = a1 - (a2/tau)*exp(-t/tau) [Å/s]."""
    return a1 - (a2 / tau) * math.exp(-t / tau)


def fit_blanket_rate(times, removed):
    """(times[s], removed[Å]) 쌍으로부터 (a1, a2, tau) 최소제곱 역추정.

    scipy가 있으면 scipy.optimize.curve_fit, 없으면 numpy 기반 grid search(tau)
    + 선형 최소제곱(a1, a2) 서브피팅으로 구현한다. 초기값/그리드는 전달된
    데이터 스케일에서 산출한다(문헌값을 지어내 초기값으로 쓰지 않는다).

    prerequisite: len(times) >= 3.
    """
    times = list(times)
    removed = list(removed)
    if len(times) < 3:
        raise ValueError("fit_blanket_rate requires at least 3 (t, removed) pairs")

    t_span = max(times) - min(times)
    if t_span <= 0:
        raise ValueError("times must span a positive range")
    tau0 = t_span / 3.0
    a1_0 = (removed[-1] - removed[-2]) / (times[-1] - times[-2]) if times[-1] != times[-2] else removed[-1] / times[-1]
    a2_0 = max(abs(removed[0]), 1.0)

    try:
        from scipy.optimize import curve_fit

        def model(t, a1, a2, tau):
            return a1 * t + a2 * (math.e ** (-t / tau) - 1)

        popt, _ = curve_fit(model, times, removed, p0=[a1_0, a2_0, tau0], maxfev=10000)
        return tuple(popt)
    except ImportError:
        pass

    import numpy as np

    times_arr = np.asarray(times, dtype=float)
    removed_arr = np.asarray(removed, dtype=float)

    best = None
    tau_candidates = np.linspace(t_span / 50.0, t_span * 3.0, 400)
    for tau in tau_candidates:
        basis = np.column_stack([times_arr, np.exp(-times_arr / tau) - 1])
        coeffs, *_ = np.linalg.lstsq(basis, removed_arr, rcond=None)
        a1, a2 = coeffs
        pred = basis @ coeffs
        sse = float(np.sum((pred - removed_arr) ** 2))
        if best is None or sse < best[0]:
            best = (sse, a1, a2, tau)

    _, a1, a2, tau = best
    return float(a1), float(a2), float(tau)
