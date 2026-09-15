"""실측 데이터를 받아 모델을 **축척 차원에서만** 보정한다.

왜 축척만인가
────────────
모델식이 책임지는 것과 데이터가 책임지는 것은 다르다(docs/COMPLETION-CRITERIA.md).

    구조(shape) : 함수 형태·지수·부호·게이트·정점 위치
                  → 물리에서 유도된다. **데이터로 맞추지 않는다.**
                  안 맞으면 구조가 틀린 것이고 구조를 고쳐야 한다.

    축척(scale) : Kp, 계열별 배율, 재료쌍 상수
                  → 장비·측정계마다 다르다. 원리적으로 그 계에서 역산된다.
                  **이것이 데이터의 몫이다.**

이 경계를 지키지 않으면 데이터를 넣을수록 시뮬레이터가 회귀식이 된다.
실제로 계통편향이 데이터셋마다 0.004~53.8 배로 흩어지는데, 이 폭을
보정항으로 흡수하면 그 항은 물리가 아니라 그 데이터셋의 지문이 된다.

무엇을 하는가
────────────
1) 계열(series) 단위로 **배율 하나**를 역산한다 — 자유도 1개/계열.
   기하평균 비를 쓴다: s = exp(mean(ln(obs/pred))).
   이것은 피팅이 아니라 단위 환산에 가깝다 — 형상을 전혀 바꾸지 않는다.

2) 그 배율을 적용한 뒤 **남는 형상오차**를 보고한다.
   이것이 진짜 모델 갭이며, 데이터를 더 넣어도 줄지 않는다면 구조 문제다.

3) 데이터 투입량에 따라 오차가 **단조 감소**하는지 학습곡선을 그린다.
   감소하지 않으면 "데이터를 넣어도 나아지지 않는다" = 구조 한계다.

⚠ 하지 않는 것
  · 지수·함수형·게이트 변경
  · 계열별로 다른 물리 상수 부여
  · held-out 데이터를 캘리브레이션에 사용
"""

from __future__ import annotations

import json
import math
import pathlib
import sys
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence, Tuple

ROOT = pathlib.Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import numpy as np                                    # noqa: E402

CALIB_STORE = ROOT / "validation" / "series_scales.json"

__all__ = [
    "SeriesScale", "fit_series_scale", "apply_scale",
    "learning_curve", "CalibrationReport",
]


@dataclass
class SeriesScale:
    """한 계열(장비·측정계)의 축척 보정.

    자유도는 **1개**다. 형상을 바꾸지 않으므로 순위 지표에 영향이 없다.
    """
    series: str
    scale: float
    n_points: int
    residual_mape: float          # 배율 적용 후 남는 형상오차
    ci_low: float = float("nan")  # 부트스트랩 신뢰구간
    ci_high: float = float("nan")
    notes: List[str] = field(default_factory=list)

    def __repr__(self) -> str:
        return (f"SeriesScale({self.series}: ×{self.scale:.4g}, "
                f"n={self.n_points}, 잔여 {self.residual_mape:.1f}%)")


def fit_series_scale(pred: Sequence[float], obs: Sequence[float],
                     series: str = "?",
                     n_boot: int = 200,
                     rng_seed: int = 0) -> Optional[SeriesScale]:
    """예측/실측에서 배율 하나를 역산한다.

    기하평균 비를 쓰는 이유: MRR 은 곱셈적으로 어긋난다(배율 오차).
    산술평균 비는 큰 값에 끌려가므로 로그 공간에서 평균한다.

    부트스트랩으로 신뢰구간을 낸다 — 점 하나로 뽑은 배율은 불확실하고,
    그 불확실성을 숨기면 "1점만 넣어도 맞는다"는 거짓 인상을 준다.
    """
    p = np.asarray(pred, dtype=float)
    o = np.asarray(obs, dtype=float)
    m = np.isfinite(p) & np.isfinite(o) & (p > 0) & (o > 0)
    if m.sum() < 1:
        return None
    p, o = p[m], o[m]

    logr = np.log(o / p)
    scale = float(np.exp(np.mean(logr)))
    resid = np.abs(p * scale - o) / o
    mape = float(np.mean(resid) * 100)

    lo = hi = float("nan")
    if p.size >= 2:
        rng = np.random.default_rng(rng_seed)
        boots = []
        for _ in range(n_boot):
            idx = rng.integers(0, p.size, p.size)
            boots.append(float(np.exp(np.mean(logr[idx]))))
        lo, hi = float(np.percentile(boots, 2.5)), float(np.percentile(boots, 97.5))

    notes = []
    if p.size == 1:
        notes.append("⚠ 1점으로 뽑은 배율 — 신뢰구간을 낼 수 없다. "
                     "형상오차는 이 배율로 검증되지 않는다(자기 자신과 비교).")
    if mape > 30.0:
        notes.append(f"⚠ 배율을 맞춰도 형상오차가 {mape:.0f}% 남는다 — "
                     "축척 문제가 아니라 **구조 문제**다. 데이터를 더 넣어도 "
                     "줄지 않는다.")
    return SeriesScale(series, scale, int(p.size), mape, lo, hi, notes)


def apply_scale(pred: Sequence[float], s: SeriesScale) -> np.ndarray:
    return np.asarray(pred, dtype=float) * s.scale


# ──────────────────────────────────────────────────────────────
# 학습곡선 — "데이터를 넣으면 나아지는가"를 직접 잰다
# ──────────────────────────────────────────────────────────────

@dataclass
class CalibrationReport:
    series: str
    curve: List[Tuple[int, float]]      # (투입 점수, held-out 절대오차 %)
    monotone: bool
    verdict: str
    notes: List[str] = field(default_factory=list)


def learning_curve(pred: Sequence[float], obs: Sequence[float],
                   series: str = "?",
                   rng_seed: int = 0,
                   n_repeat: int = 50) -> Optional[CalibrationReport]:
    """k 점으로 배율을 뽑아 **나머지 점**에서 오차를 잰다.

    이것이 제품 기능의 직접 측정이다: "고객이 자기 데이터를 k 점 넣으면
    절대값 오차가 얼마가 되는가."

    ⚠ 반드시 held-out 으로 잰다. 배율을 뽑은 점에서 오차를 재면
      항상 좋아 보인다(자기 채점).
    """
    p = np.asarray(pred, dtype=float)
    o = np.asarray(obs, dtype=float)
    m = np.isfinite(p) & np.isfinite(o) & (p > 0) & (o > 0)
    p, o = p[m], o[m]
    n = p.size
    if n < 3:
        return None

    rng = np.random.default_rng(rng_seed)
    curve: List[Tuple[int, float]] = []
    for k in range(1, min(n, 8)):
        errs = []
        for _ in range(n_repeat):
            idx = rng.permutation(n)
            fit_i, test_i = idx[:k], idx[k:]
            if test_i.size == 0:
                continue
            s = float(np.exp(np.mean(np.log(o[fit_i] / p[fit_i]))))
            e = np.abs(p[test_i] * s - o[test_i]) / o[test_i]
            errs.append(float(np.mean(e)))
        if errs:
            curve.append((k, float(np.mean(errs)) * 100))

    if len(curve) < 2:
        return None

    ys = [y for _, y in curve]
    # 단조 감소 판정 — 잡음을 허용해 첫값 대비 마지막값으로 본다
    improved = ys[-1] < ys[0] * 0.98
    flat = abs(ys[-1] - ys[0]) / max(ys[0], 1e-9) < 0.02

    if improved:
        verdict = "✅ 데이터를 넣을수록 좋아진다 — 축척 학습이 작동한다"
    elif flat:
        verdict = ("⚠ 데이터를 넣어도 평평하다 — 남은 오차는 축척이 아니라 "
                   "형상이다. 구조를 고쳐야 한다.")
    else:
        verdict = ("🔴 데이터를 넣을수록 나빠진다 — 계열 안에 서로 다른 물리가 "
                   "섞여 있다(계열 분할 필요).")

    return CalibrationReport(series, curve, improved, verdict)


def save_scales(scales: Dict[str, SeriesScale]) -> pathlib.Path:
    """역산한 배율을 저장한다 — 다음 실행에서 재사용.

    ⚠ 이 파일은 **캘리브레이션 산출물**이지 물리 상수가 아니다.
      팩 YAML 에 섞어 넣으면 장비 지문이 물리인 척하게 된다.
    """
    CALIB_STORE.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "_주의": ("이 파일은 장비·측정계별 축척 보정값이다. 물리 상수가 아니므로 "
                "knowledge/params/ 로 옮기지 마라. 형상에는 영향이 없다."),
        "scales": {k: {"scale": v.scale, "n": v.n_points,
                       "residual_mape": v.residual_mape,
                       "ci": [v.ci_low, v.ci_high]}
                   for k, v in scales.items()},
    }
    CALIB_STORE.write_text(json.dumps(payload, ensure_ascii=False, indent=1),
                           encoding="utf-8")
    return CALIB_STORE
