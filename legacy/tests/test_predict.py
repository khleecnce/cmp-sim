"""sim/calibration/predict.py 계약 테스트 — ORG.md §7.4 M3-4.

전부 합성 데이터만 쓴다(실측·회사데이터 금지). 여기서 고정하는 것:
  ① correction=None — 물리모델만, sigma_nm/CI 없음, 물리값 절대치(단위버그 방지)
  ② NPW 층만 적용 — corrected_nm이 physics_nm + fit_npw.apply()와 정확히 일치
  ③ NPW+PTW 두 층 합 — corrected_nm이 두 층 합과 일치
  ④ improved=False 층은 layers_applied에서 빠지고 사유가 note에 남음
  ⑤ GP 학습 범위 밖 질의는 extrapolation_flags=True + sigma_nm이 오히려 넓어짐
     (fit_npw.apply()가 CI를 0으로 뭉개는 것과 달리 predict.py는 진짜 사후표준편차를 씀)
  ⑥ 물리 엔진 격자 밖 질의는 조용히 clamp하지 않고 ValueError
  ⑦ pack 불일치 거부
  ⑧ deviation_pct가 크면(>20%) note에 경고
"""
from __future__ import annotations

import pathlib
import sys

import numpy as np
import pytest

ROOT = pathlib.Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sim.calibration import fit_npw, fit_ptw, predict  # noqa: E402
from sim.engine import Recipe, simulate                 # noqa: E402

PACK = "oxide_silica"


def _npw_fixture(seed=1, n_restarts=6):
    r = np.linspace(0.0, 140.0, 30)
    true_curve = 3.0 * np.sin(r / 40.0)
    y = true_curve + np.random.default_rng(42).normal(0.0, 0.05, size=len(r))
    corr = fit_npw.fit_residuals(PACK, r, y, seed=seed, n_restarts=n_restarts)
    assert corr.improved is True and corr.hyperparams  # 픽스처 전제 — 실측으로 확인됨
    return corr, r, true_curve


def _ptw_fixture():
    npw_corr, r, npw_true = _npw_fixture()
    ptw_true = 1.5 * np.cos(r / 25.0)
    y_raw = npw_true + ptw_true + np.random.default_rng(3).normal(0.0, 0.05, size=len(r))
    ptw_corr = fit_ptw.fit_residuals(PACK, r, y_raw, npw_corr, seed=0, n_restarts=5)
    assert ptw_corr.improved is True and ptw_corr.hyperparams  # 픽스처 전제 — 실측으로 확인됨
    return ptw_corr, r


# ═══════════════════════════════ ① correction=None — 물리값 절대치

def test_no_correction_uses_physics_only_with_absolute_value():
    result = predict.predict_radial(PACK, [0.0], correction=None)

    # 2026-09-19 sim.engine.simulate(Recipe(pack='oxide_silica'))로 독립 계산한 절대값.
    # 상대검사만으로는 단위 스케일 버그(예: nm과 km 혼동)를 못 잡는다 — 절대치 고정.
    assert result.physics_nm[0] == pytest.approx(142.9594184006129, rel=1e-9)

    direct = simulate(Recipe(pack=PACK))
    assert result.physics_nm[0] == pytest.approx(direct.removed_nm[0], rel=1e-12)

    assert result.corrected_nm[0] == pytest.approx(result.physics_nm[0])
    assert result.sigma_nm is None
    assert result.lo_nm is None and result.hi_nm is None
    assert result.layers_applied == []
    assert result.extrapolation_flags.tolist() == [False]
    assert result.deviation_nm[0] == pytest.approx(0.0)
    assert result.deviation_pct[0] == pytest.approx(0.0)
    assert "correction=None" in result.note or "물리모델" in result.note


# ═══════════════════════════════ ② NPW 층만

def test_npw_only_layer_matches_fit_npw_apply():
    corr, r, _ = _npw_fixture()
    result = predict.predict_radial(PACK, r, correction=corr)

    assert result.layers_applied == ["npw"]
    engine_result = simulate(Recipe(pack=PACK))
    physics = np.interp(r, engine_result.radius_m * 1000.0, engine_result.removed_nm)
    npw_mean, _, _, npw_extrap = fit_npw.apply(corr, r)

    assert np.allclose(result.physics_nm, physics)
    assert np.allclose(result.corrected_nm, physics + npw_mean)
    assert np.array_equal(result.extrapolation_flags, npw_extrap)
    assert result.sigma_nm is not None
    assert np.all(np.isfinite(result.sigma_nm)) and np.all(result.sigma_nm > 0.0)
    assert np.all(result.lo_nm <= result.corrected_nm) and np.all(result.corrected_nm <= result.hi_nm)


# ═══════════════════════════════ ③ NPW+PTW 합

def test_npw_plus_ptw_layers_sum_correctly():
    ptw_corr, r = _ptw_fixture()
    result = predict.predict_radial(PACK, r, correction=ptw_corr)

    assert result.layers_applied == ["npw", "ptw"]
    engine_result = simulate(Recipe(pack=PACK, wafer="PTW"))
    physics = np.interp(r, engine_result.radius_m * 1000.0, engine_result.removed_nm)
    npw_mean, _, _, _ = fit_npw.apply(ptw_corr.npw_correction, r)
    ptw_mean, _, _, _ = fit_ptw.ptw_layer(ptw_corr, r)

    assert np.allclose(result.physics_nm, physics)
    assert np.allclose(result.corrected_nm, physics + npw_mean + ptw_mean)
    # 두 층이 독립 GP라는 가정(fit_ptw.apply_ptw와 동일 규약) — 분산합이 각 층보다 크다
    sd_npw_only = predict._gp_sd(ptw_corr.npw_correction.hyperparams, ptw_corr.npw_correction.r_train_mm, r)
    assert np.all(result.sigma_nm >= sd_npw_only - 1e-9)


# ═══════════════════════════════ ④ improved=False 층 스킵

def test_improved_false_layer_is_skipped_not_applied():
    r_small = np.array([10.0, 20.0, 30.0])
    y_small = np.array([0.1, 0.2, 0.1])
    corr = fit_npw.fit_residuals(PACK, r_small, y_small)  # n=3 < 5 → improved=False
    assert corr.improved is False and corr.hyperparams == {}

    result = predict.predict_radial(PACK, [50.0], correction=corr)
    assert result.layers_applied == []
    assert result.sigma_nm is None
    assert result.corrected_nm[0] == pytest.approx(result.physics_nm[0])
    assert "미적용" in result.note


# ═══════════════════════════════ ⑤ 외삽 플래그 + CI 확장

def test_extrapolation_flag_widens_ci_instead_of_silently_shrinking():
    corr, r, _ = _npw_fixture()  # 학습 범위 r in [0, 140]
    result = predict.predict_radial(PACK, [70.0, 145.0], correction=corr)

    assert result.extrapolation_flags.tolist() == [False, True]
    # 안전장치: 외삽점의 보정 평균은 0으로 감쇠 → corrected == physics 그대로
    assert result.corrected_nm[1] == pytest.approx(result.physics_nm[1])
    # 하지만 sigma는 마스킹되지 않아 외삽점에서 오히려 넓어져야 한다(사전분산 회귀)
    assert result.sigma_nm[1] > result.sigma_nm[0]
    assert (result.hi_nm[1] - result.lo_nm[1]) > (result.hi_nm[0] - result.lo_nm[0])
    assert "외삽" in result.note


# ═══════════════════════════════ ⑥ 물리 엔진 격자 밖 — 조용한 clamp 금지

def test_query_outside_physics_grid_raises_instead_of_clamping():
    with pytest.raises(ValueError):
        predict.predict_radial(PACK, [500.0], correction=None)


# ═══════════════════════════════ ⑦ pack 불일치 거부

def test_pack_mismatch_between_correction_and_call_rejected():
    corr, r, _ = _npw_fixture()
    corr.pack = "different_pack"
    with pytest.raises(ValueError):
        predict.predict_radial(PACK, r, correction=corr)


# ═══════════════════════════════ ⑧ 큰 편차 경고

def test_large_deviation_pct_warns_in_note():
    r_train = np.linspace(0.0, 140.0, 10)
    huge_corr = fit_npw.NPWCorrection(
        pack=PACK, n_train=10, n_dropped={}, hyperparams={"l_mm": 50.0, "sigma_f": 100.0, "sigma_n": 0.01},
        loo_rmse_gp=0.1, loo_rmse_baseline=1.0, improved=True, converged=True, notes=[],
        r_train_mm=r_train, residual_train=np.full(10, 100.0),
    )
    result = predict.predict_radial(PACK, [70.0], correction=huge_corr)
    assert abs(result.deviation_pct[0]) > 20.0
    assert "⚠" in result.note or "뒤집" in result.note
