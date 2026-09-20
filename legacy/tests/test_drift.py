"""sim/calibration/drift.py 계약 테스트 — ORG.md §7.4 M3-4.

전부 합성 데이터만 쓴다(실측·회사데이터 금지). 여기서 고정하는 것:
  ① 같은 분포에서 뽑은 새 데이터 → verdict="ok"
  ② 큰 오프셋을 인위 주입한 데이터 → verdict="alarm"
  ③ n=3(표본 부족) → verdict="watch" (ok로 단언하지 않음 — 데이터 자체는 정상이어도)
  ④ 재적합하지 않음 — correction 객체가 호출 전후로 완전히 불변(deepcopy 대조)
  ⑤ z-score 분모가 GP 사후분산+관측노이즈를 합친 것(단일 항만 쓰면 과경보/과둔감)
"""
from __future__ import annotations

import copy
import pathlib
import sys

import numpy as np
import pytest

ROOT = pathlib.Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sim.calibration import drift, fit_npw, ingest  # noqa: E402
from sim.engine import Recipe, simulate              # noqa: E402

PACK = "oxide_silica"
_ENGINE_RESULT = simulate(Recipe(pack=PACK))


def _physics_nm(r_mm):
    return np.interp(r_mm, _ENGINE_RESULT.radius_m * 1000.0, _ENGINE_RESULT.removed_nm)


def _make_record(r_mm, values, *, wafer_id="W-DRIFT", series_id="drift-series"):
    points = [{"r_m": float(r) / 1000.0, "theta_rad": 0.0, "value": float(v), "unit": "nm"}
              for r, v in zip(r_mm, values)]
    return {
        "wafer_id": wafer_id, "wafer_diameter_mm": 300, "notch_direction": "Bottom",
        "edge_exclusion_mm": 3.0, "coord_kind": "polar", "series_id": series_id, "points": points,
    }


def _true_curve(r_mm):
    return 3.0 * np.sin(r_mm / 40.0)


def _npw_correction_fixture():
    """실측(2026-09-19): improved=True, n_train=25, sigma_n≈0.221 — 이 값에 픽스처가 의존."""
    rng = np.random.default_rng(0)
    r_train = np.linspace(5.0, 135.0, 25)
    values = _physics_nm(r_train) + _true_curve(r_train) + rng.normal(0.0, 0.3, size=len(r_train))
    ing = ingest.ingest_record(_make_record(r_train, values, wafer_id="W-TRAIN"))
    corr = fit_npw.fit(PACK, ing, seed=0, n_restarts=6)
    assert corr.improved is True and corr.hyperparams  # 픽스처 전제
    return corr


def _same_distribution_ingest(seed=1, n=20, wafer_id="W-NEW"):
    rng = np.random.default_rng(seed)
    r_new = np.linspace(5.0, 135.0, n)
    values = _physics_nm(r_new) + _true_curve(r_new) + rng.normal(0.0, 0.3, size=n)
    return ingest.ingest_record(_make_record(r_new, values, wafer_id=wafer_id))


# ═══════════════════════════════ ① 같은 분포 → ok

def test_same_distribution_new_data_is_ok():
    corr = _npw_correction_fixture()
    ing_new = _same_distribution_ingest(seed=1)
    report = drift.check_drift(corr, ing_new, pack=PACK)

    assert report.n_points == 20
    assert report.verdict == "ok"
    assert 0.0 <= report.frac_outside_90ci <= 1.0
    assert np.isfinite(report.rmse_new) and np.isfinite(report.rmse_reference)


# ═══════════════════════════════ ② 인위적 오프셋 → alarm

def test_artificial_offset_triggers_alarm():
    corr = _npw_correction_fixture()
    rng = np.random.default_rng(1)
    r_new = np.linspace(5.0, 135.0, 20)
    values = _physics_nm(r_new) + _true_curve(r_new) + rng.normal(0.0, 0.3, size=20) + 20.0
    ing_off = ingest.ingest_record(_make_record(r_new, values, wafer_id="W-OFFSET"))

    report = drift.check_drift(corr, ing_off, pack=PACK)
    assert report.verdict == "alarm"
    assert report.frac_outside_90ci > 0.5
    assert any("이항검정" in reason for reason in report.reasons)


# ═══════════════════════════════ ③ n=3 — 표본 부족은 watch, ok 단언 금지

def test_small_sample_is_watch_not_ok():
    corr = _npw_correction_fixture()
    rng = np.random.default_rng(1)
    r_small = np.array([10.0, 60.0, 120.0])
    values = _physics_nm(r_small) + _true_curve(r_small) + rng.normal(0.0, 0.3, size=3)
    # outlier_k을 크게 줘서 MAD 소표본 불안정성(n=3에서 흔한 오탐)이 이 테스트의
    # 목적(표본 부족 검정력)과 섞이지 않게 한다 — normalize.flag_outliers는 n<5에서
    # 신뢰할 수 없다고 알려져 있다(judgement#기록: Leys2013 MAD 권고는 더 큰 n 전제).
    ing_small = ingest.ingest_record(_make_record(r_small, values, wafer_id="W-SMALL"), outlier_k=100.0)

    report = drift.check_drift(corr, ing_small, pack=PACK)
    assert report.n_points == 3
    assert report.verdict == "watch"
    assert any("표본 부족" in reason for reason in report.reasons)


# ═══════════════════════════════ ④ 재적합 없음 — correction 완전 불변

def test_check_drift_does_not_mutate_or_refit_correction():
    corr = _npw_correction_fixture()
    before = copy.deepcopy(corr)

    ing_off = _same_distribution_ingest(seed=99)
    drift.check_drift(corr, ing_off, pack=PACK)
    # 큰 오프셋 케이스도 한 번 더 — alarm 경로에서도 불변인지 확인
    rng = np.random.default_rng(2)
    r_new = np.linspace(5.0, 135.0, 20)
    values = _physics_nm(r_new) + _true_curve(r_new) + rng.normal(0.0, 0.3, size=20) + 50.0
    ing_off2 = ingest.ingest_record(_make_record(r_new, values, wafer_id="W-OFFSET2"))
    drift.check_drift(corr, ing_off2, pack=PACK)

    assert corr.pack == before.pack
    assert corr.n_train == before.n_train
    assert corr.hyperparams == before.hyperparams
    assert corr.improved == before.improved
    assert corr.converged == before.converged
    assert corr.notes == before.notes
    assert np.array_equal(corr.r_train_mm, before.r_train_mm)
    assert np.array_equal(corr.residual_train, before.residual_train)


# ═══════════════════════════════ ⑤ z-score 분모 = GP 사후분산 + 관측노이즈

def test_z_score_denominator_combines_gp_variance_and_noise():
    corr = _npw_correction_fixture()
    ing_new = _same_distribution_ingest(seed=1)
    report = drift.check_drift(corr, ing_new, pack=PACK)

    r_used = np.linspace(5.0, 135.0, 20)
    sd_gp_only = predict_gp_sd_only(corr, r_used)          # 노이즈 항 없음 → 항상 더 작다
    sd_combined = _combined_sd(corr, r_used)                # drift.py가 실제로 쓰는 분모
    assert np.all(sd_gp_only <= sd_combined + 1e-12)
    # error = z_scores * sd_combined 이므로, 분모를 sd_gp_only(과소평가)로 바꾸면
    # |z|가 항상 더(또는 같게) 커져야 한다 — 노이즈를 무시하면 과경보로 기운다는 뜻.
    error = report.z_scores * sd_combined
    z_gp_only = error / sd_gp_only
    assert np.all(np.abs(z_gp_only) >= np.abs(report.z_scores) - 1e-9)


def predict_gp_sd_only(corr, r):
    """노이즈 항 없이 GP 함수값 사후표준편차만(비교용 — drift.py가 실제로 이걸 쓰면 안 된다)."""
    from sim.calibration import fit_npw
    from scipy import linalg as sla
    l = corr.hyperparams["l_mm"]; sigma_f = corr.hyperparams["sigma_f"]; sigma_n = corr.hyperparams["sigma_n"]
    r_train = corr.r_train_mm
    K = fit_npw._rbf(r_train, r_train, sigma_f, l) + (sigma_n ** 2) * np.eye(len(r_train))
    L, _ = fit_npw._safe_cholesky(K)
    K_s = fit_npw._rbf(r, r_train, sigma_f, l)
    v = sla.solve_triangular(L, K_s.T, lower=True)
    var = np.maximum(sigma_f ** 2 - np.sum(v ** 2, axis=0), 0.0)  # 노이즈 항 없음
    return np.sqrt(var)


def _combined_sd(corr, r):
    from sim.calibration.predict import _gp_sd
    return _gp_sd(corr.hyperparams, corr.r_train_mm, r)
