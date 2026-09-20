"""sim/metrics/vm_baseline.py 계약 테스트.

근거 노트 `knowledge/cmp/inline-virtual-metrology-sampling-optimization.md` §4 블록1의
python verify 코드를 그대로 재현한다 (상수는 노트에서 그대로 가져옴).
"""
import numpy as np
import pytest

from sim.metrics.vm_baseline import (
    PersistentPredictor,
    linear_regression_baseline,
    mc_cv_weight,
    vm_confidence_weight,
    weighted_ensemble_predict,
)


# Di, Jia & Lee (2017) IJPHM 8(2) Table 4/5 상수 (노트 §4 블록1 원문 그대로)
test_mse = {"integrated": 7.07, "persistent": 8.23, "knn": 9.60, "svr": 7.44,
            "lr": 7.32, "treebag": 7.22, "dbn_wang2017": 7.29}
cond1_cv = {"persistent": (7.55, 1.27), "knn": (8.78, 5.43), "svr": (5.54, 1.30),
            "lr": (5.77, 1.10), "treebag": (5.65, 0.33)}


def test_mc_cv_weight_reproduces_note_block1():
    w = mc_cv_weight(cond1_cv)
    assert abs(sum(w.values()) - 1) < 1e-12
    assert max(w, key=w.get) == "treebag"
    assert min(w, key=w.get) == "knn"
    assert w["treebag"] > 0.45
    assert w["knn"] < 0.02


def test_persistent_mse_beats_knn_timeseries_property():
    assert test_mse["persistent"] < test_mse["knn"]


def test_persistent_predictor_lag1_contract():
    series = [10.0, 12.5, 9.0, 15.0, 20.0, 3.0]
    predictor = PersistentPredictor()
    predictor.update(series[0])
    preds = []
    for actual in series[1:]:
        preds.append(predictor.predict())
        predictor.update(actual)
    assert preds == series[:-1]


def test_persistent_predictor_raises_before_first_observation():
    predictor = PersistentPredictor()
    with pytest.raises(ValueError):
        predictor.predict()


def test_linear_regression_baseline_recovers_known_line():
    x = np.linspace(-5, 5, 50)
    y = 2 * x + 1
    predict = linear_regression_baseline(x, y)
    y_pred = predict(x)
    assert np.max(np.abs(y_pred - y)) < 1e-6


def test_vm_confidence_weight_boundary_contract():
    assert vm_confidence_weight(1.0, 1.0) == pytest.approx(0.5)
    assert vm_confidence_weight(1.0, 1e12) == pytest.approx(1.0, abs=1e-9)
    assert vm_confidence_weight(1.0, 1e-9) == pytest.approx(0.0, abs=1e-9)


def test_weighted_ensemble_predict_matches_weighted_sum():
    predictions = {"a": 1.0, "b": 3.0}
    weights = {"a": 0.25, "b": 0.75}
    assert weighted_ensemble_predict(predictions, weights) == pytest.approx(2.5)


def test_weighted_ensemble_predict_key_mismatch_raises():
    with pytest.raises(ValueError):
        weighted_ensemble_predict({"a": 1.0}, {"a": 0.5, "b": 0.5})
