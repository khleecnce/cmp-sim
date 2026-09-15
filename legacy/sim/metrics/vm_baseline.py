"""가상 계측(VM) 베이스라인 유틸 — 순수함수 라이브러리 (엔진 미등록, S17/S19/S20과 동일 지위).

근거 노트: `knowledge/cmp/inline-virtual-metrology-sampling-optimization.md` §2.2(블록1), §2.4(블록4), §5-3.
이 모듈은 노트가 이미 python verify로 검증한 로직을 재사용 가능한 함수로 옮긴 것이며,
Recipe/WaferResult 스키마에 시계열·FDC 센서 필드가 없어 engine.py에 등록하지 않는다.
"""
from __future__ import annotations

from typing import Callable

import numpy as np


def mc_cv_weight(errors: dict[str, tuple[float, float]]) -> dict[str, float]:
    """Di, Jia & Lee (2017) IJPHM 8(2) 블록1 가중식: e = mean+3·std, w = (1/e^3)/Σ(1/e^3).

    입력: 모델명 -> (mean, std) Monte-Carlo CV 오차.
    """
    e = {k: mean + 3 * std for k, (mean, std) in errors.items()}
    raw = {k: 1 / e[k] ** 3 for k in e}
    total = sum(raw.values())
    return {k: v / total for k, v in raw.items()}


def weighted_ensemble_predict(predictions: dict[str, float], weights: dict[str, float]) -> float:
    """Σ(w_i · pred_i). predictions와 weights의 키 집합이 다르면 ValueError."""
    if set(predictions.keys()) != set(weights.keys()):
        raise ValueError("predictions와 weights의 키 집합이 일치해야 함")
    return sum(weights[k] * predictions[k] for k in predictions)


class PersistentPredictor:
    """r_t = r_{t-1} — Di 2017의 persistent 모델(직전 실측값을 다음 예측으로 사용)."""

    def __init__(self) -> None:
        self._last: float | None = None

    def predict(self) -> float:
        if self._last is None:
            raise ValueError("아직 관측값이 없어 예측할 수 없음")
        return self._last

    def update(self, observed: float) -> None:
        self._last = observed


def _as_feature_matrix(X: np.ndarray, n_features: int | None = None) -> np.ndarray:
    """X를 (n_samples, n_features) 2차원 배열로 정규화. 1차원 입력은 단일 특징으로 취급."""
    X = np.asarray(X, dtype=float)
    if X.ndim == 1:
        X = X.reshape(-1, 1) if n_features in (None, 1) else X.reshape(1, -1)
    return X


def linear_regression_baseline(X: np.ndarray, y: np.ndarray) -> Callable[[np.ndarray], np.ndarray]:
    """numpy.linalg.lstsq 기반 최소자승 선형회귀 — fit 후 predict 클로저를 반환 (sklearn 불사용)."""
    X_fit = _as_feature_matrix(X)
    y = np.asarray(y, dtype=float)
    X_design = np.column_stack([X_fit, np.ones(X_fit.shape[0])])
    coef, *_ = np.linalg.lstsq(X_design, y, rcond=None)
    beta, intercept = coef[:-1], coef[-1]
    n_features = X_fit.shape[1]

    def predict(X_new: np.ndarray) -> np.ndarray:
        X_new = _as_feature_matrix(X_new, n_features)
        return X_new @ beta + intercept

    return predict


def vm_confidence_weight(sigma_metrology: float, sigma_vm: float) -> float:
    """PROVISIONAL — US9240360은 가중치를 구체적 공식으로 명시하지 않음, inverse-variance는 표준적 선택으로 채택.

    반환값은 실측(metrology) 오차에 대한 상대 신뢰 가중치:
    w_metrology = (1/sigma_metrology^2) / (1/sigma_metrology^2 + 1/sigma_vm^2)
    """
    inv_met = 1 / sigma_metrology ** 2
    inv_vm = 1 / sigma_vm ** 2
    return inv_met / (inv_met + inv_vm)
