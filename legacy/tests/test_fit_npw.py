"""sim/calibration/fit_npw.py 계약 테스트 — ORG.md §7.4/§7.6 M3 게이트 3/3.

여기서 고정하는 것:
  ① 합성 웨이퍼(SYN-OXIDE-SILICA-001) 왕복 — ingest → fit → LOO RMSE 실측치
     (개선 여부를 강제로 통과시키지 않고 실제 측정값을 그대로 고정한다)
  ② 알려진 매끄러운 잔차 곡선 회수
  ③ 순수 노이즈 — 안전장치가 구조를 지지하지 않는다고 판단하는지
  ④ n<5 거부 경로 (예외가 아니라 사유가 담긴 정상 반환)
  ⑤ 외삽 가드 — 학습 범위 밖은 보정 0 + extrapolated=True
  ⑥ is_excluded/is_missing/is_outlier 행이 실제로 학습에서 빠지는지(카운트 대조)
  ⑦ 하이퍼파라미터 적합 재현성(같은 seed → 같은 값)
  ⑧ Cholesky 지터 경로(거의 중복된 학습 반경)
  ⑨ 읽기전용 계약 — sim/factors.py·sim/engine.py·knowledge/params/*.yaml 불변
  ⑩ to_prior_dict() 직렬화 왕복
  ⑪ 관측 단위가 nm/nm_per_min이 아니면 ValueError
  ⑫ 엔진 격자 밖 측정점은 외삽하지 않고 버림(out_of_grid)
"""
from __future__ import annotations

import ast
import json
import pathlib

import numpy as np
import pytest

from sim.calibration import fit_npw, ingest

ROOT = pathlib.Path(__file__).resolve().parent.parent
SYNTHETIC_DIR = ROOT / "data" / "synthetic"

_PROTECTED_FILES = [
    ROOT / "sim" / "factors.py",
    ROOT / "sim" / "engine.py",
    ROOT / "sim" / "params.py",
    ROOT / "sim" / "chemistry.py",
    *sorted((ROOT / "knowledge" / "params").glob("*.yaml")),
]


def _record(points, *, wafer_diameter_mm=300, edge_exclusion_mm=3.0,
            notch_direction="Bottom", series_id="oxide_silica", wafer_id="W-FIT-TEST"):
    return {
        "wafer_id": wafer_id,
        "wafer_diameter_mm": wafer_diameter_mm,
        "notch_direction": notch_direction,
        "edge_exclusion_mm": edge_exclusion_mm,
        "coord_kind": "polar",
        "series_id": series_id,
        "points": points,
    }


def _point(r_m, value, unit="nm", theta_rad=0.0):
    return {"r_m": r_m, "theta_rad": theta_rad, "value": value, "unit": unit}


# ═══════════════════════════════ ① 합성 웨이퍼 왕복 — 실측치 그대로 고정

def test_synthetic_wafer_roundtrip_matches_measured_loo_rmse():
    record = json.loads((SYNTHETIC_DIR / "SYN-OXIDE-SILICA-001.json").read_text(encoding="utf-8"))
    res = ingest.ingest_record(record)
    assert res.n_excluded == 0 and res.n_missing == 0 and res.n_outliers == 0

    corr = fit_npw.fit("oxide_silica", res, seed=0, n_restarts=5)

    assert corr.n_train == res.n_rows
    assert corr.converged is True
    # 실측치(2026-09-19, seed=0, n_restarts=5) 그대로 고정 — 개선 폭이 크지 않다는
    # 사실 자체가 결과다(측정노이즈가 지배적이고 진짜 반경 구조가 거의 없는 합성
    # 데이터라 GP가 크게 이길 이유가 없다). 통과시키려고 고른 숫자가 아니다.
    assert corr.loo_rmse_baseline == pytest.approx(1.5648304964228874, rel=1e-6)
    assert corr.loo_rmse_gp == pytest.approx(1.5620652877637398, rel=1e-6)
    assert corr.improved is True  # 근소하지만 baseline보다 낫다 — LOO가 직접 판정한 결과


# ═══════════════════════════════ ② 알려진 매끄러운 잔차 곡선 회수

def test_known_smooth_curve_is_recovered_within_tolerance():
    r = np.linspace(0.0, 140.0, 30)
    true_curve = 3.0 * np.sin(r / 40.0)
    y = true_curve + np.random.default_rng(42).normal(0.0, 0.05, size=len(r))

    corr = fit_npw.fit_residuals("known-curve", r, y, seed=1, n_restarts=6)
    assert corr.improved is True
    assert corr.converged is True

    mean, ci_lo, ci_hi, extrapolated = fit_npw.apply(corr, r)
    assert not extrapolated.any()
    max_abs_err = np.max(np.abs(mean - true_curve))
    assert max_abs_err < 0.1  # 노이즈 sigma=0.05의 2배 이내 회수
    assert np.all(ci_lo <= mean) and np.all(mean <= ci_hi)


# ═══════════════════════════════ ③ 순수 노이즈 — 안전장치

def test_pure_noise_is_rejected_or_length_scale_collapses():
    rng = np.random.default_rng(1)
    r = np.linspace(0.0, 140.0, 60)
    y = rng.normal(0.0, 1.0, size=len(r))

    corr = fit_npw.fit_residuals("pure-noise", r, y, seed=1, n_restarts=6)
    # 구조가 없으면 improved=False 이거나(안전장치 1) 길이척도가 사실상 0으로
    # 붕괴한다(사전평균으로 수렴) — 둘 중 하나는 반드시 성립해야 한다.
    assert (corr.improved is False) or (corr.hyperparams["l_mm"] < 1.0)


# ═══════════════════════════════ ④ n<5 거부 경로

def test_fewer_than_five_points_rejected_without_exception():
    r = np.array([1.0, 2.0, 3.0])
    y = np.array([0.1, 0.2, 0.1])
    corr = fit_npw.fit_residuals("too-few", r, y)
    assert corr.n_train == 3
    assert corr.improved is False
    assert corr.hyperparams == {}
    assert any("< 5" in note for note in corr.notes)

    mean, ci_lo, ci_hi, extrapolated = fit_npw.apply(corr, np.array([1.5, 2.5]))
    assert np.all(mean == 0.0) and np.all(ci_lo == 0.0) and np.all(ci_hi == 0.0)


def test_zero_points_rejected_without_exception():
    corr = fit_npw.fit_residuals("empty", np.array([]), np.array([]))
    assert corr.n_train == 0
    assert corr.improved is False
    assert np.isnan(corr.loo_rmse_baseline)


# ═══════════════════════════════ ⑤ 외삽 가드

def test_extrapolation_flag_zeroes_correction_outside_training_range():
    r = np.linspace(0.0, 140.0, 30)
    true_curve = 3.0 * np.sin(r / 40.0)
    y = true_curve + np.random.default_rng(42).normal(0.0, 0.05, size=len(r))
    corr = fit_npw.fit_residuals("extrap", r, y, seed=1, n_restarts=6)
    assert corr.improved is True

    far_query = np.array([-500.0, 5000.0])
    mean, ci_lo, ci_hi, extrapolated = fit_npw.apply(corr, far_query)
    assert extrapolated.all()
    assert np.all(mean == 0.0)
    assert np.all(ci_lo == 0.0) and np.all(ci_hi == 0.0)

    near_query = np.array([r.mean()])
    _, _, _, extrapolated_near = fit_npw.apply(corr, near_query)
    assert not extrapolated_near.any()


# ═══════════════════════════════ ⑥ is_excluded/is_missing/is_outlier 카운트 대조

def test_excluded_missing_outlier_rows_are_dropped_and_counted():
    valid_points = [_point(0.01 * i, 142.0 + 0.1 * i) for i in range(8)]
    excluded_point = _point(0.149, 142.35)  # FQA=150/2-3=147mm < 149mm → excluded(값은 정상범위)
    missing_point = _point(0.05, None)
    outlier_point = _point(0.06, 5000.0)    # 나머지 값들(~142~143)과 크게 벗어남
    record = _record(valid_points + [excluded_point, missing_point, outlier_point])

    res = ingest.ingest_record(record)
    assert res.n_excluded == 1
    assert res.n_missing == 1
    assert res.n_outliers == 1

    corr = fit_npw.fit("oxide_silica", res, seed=0, n_restarts=3)
    assert corr.n_dropped["excluded"] == 1
    assert corr.n_dropped["missing"] == 1
    assert corr.n_dropped["outlier"] == 1
    assert corr.n_train == res.n_rows - 1 - 1 - 1


# ═══════════════════════════════ ⑦ 하이퍼파라미터 재현성

def test_hyperparameter_fit_is_reproducible_given_seed():
    r = np.linspace(0.0, 140.0, 20)
    y = np.sin(r / 30.0) + np.random.default_rng(1).normal(0.0, 0.1, size=len(r))
    corr1 = fit_npw.fit_residuals("rep", r, y, seed=99, n_restarts=5)
    corr2 = fit_npw.fit_residuals("rep", r, y, seed=99, n_restarts=5)
    assert corr1.hyperparams == corr2.hyperparams
    assert corr1.loo_rmse_gp == corr2.loo_rmse_gp


# ═══════════════════════════════ ⑧ Cholesky 지터 경로

def test_near_duplicate_radii_trigger_jitter_path_without_error():
    r = np.array([10.0, 10.0 + 1e-9, 10.0 + 2e-9, 50.0, 90.0, 130.0])
    y = np.array([1.0, 1.0000001, 0.9999999, 2.0, 1.5, 0.5])
    corr = fit_npw.fit_residuals("dup-radii", r, y, seed=0, n_restarts=3)
    assert corr.n_train == 6
    assert corr.hyperparams  # 예외 없이 적합됨
    mean, ci_lo, ci_hi, extrapolated = fit_npw.apply(corr, r)
    assert np.all(np.isfinite(mean))


# ═══════════════════════════════ ⑨ 읽기전용 계약

def test_read_only_protected_files_unchanged():
    before = {p: p.read_bytes() for p in _PROTECTED_FILES}

    record = json.loads((SYNTHETIC_DIR / "SYN-OXIDE-SILICA-001.json").read_text(encoding="utf-8"))
    res = ingest.ingest_record(record)
    corr = fit_npw.fit("oxide_silica", res, seed=0, n_restarts=3)
    fit_npw.apply(corr, np.linspace(0.0, 140.0, 5))
    corr.to_prior_dict()

    after = {p: p.read_bytes() for p in _PROTECTED_FILES}
    assert before == after


_WRITE_ATTRS = {
    "write_text", "write_bytes", "write", "dump", "safe_dump",
    "save", "save_scales", "writelines",
}


def test_read_only_no_write_calls_ast():
    src = (ROOT / "sim" / "calibration" / "fit_npw.py").read_text(encoding="utf-8")
    tree = ast.parse(src)
    offenders = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        if isinstance(func, ast.Attribute) and func.attr in _WRITE_ATTRS:
            offenders.append(func.attr)
        if isinstance(func, ast.Name) and func.id == "open":
            for kw in node.keywords:
                if kw.arg == "mode" and isinstance(kw.value, ast.Constant) and \
                   any(c in str(kw.value.value) for c in "wax"):
                    offenders.append("open(mode=...)")
    assert not offenders, f"fit_npw.py에 쓰기 패턴이 있다: {offenders}"


# ═══════════════════════════════ ⑩ to_prior_dict 직렬화 왕복

def test_to_prior_dict_round_trips_through_json():
    r = np.linspace(0.0, 140.0, 20)
    y = np.sin(r / 30.0) + np.random.default_rng(1).normal(0.0, 0.1, size=len(r))
    corr = fit_npw.fit_residuals("prior-hook", r, y, seed=99, n_restarts=5)

    d = corr.to_prior_dict()
    round_tripped = json.loads(json.dumps(d))
    assert round_tripped == d
    assert round_tripped["hyperparams"]["l_mm"] == pytest.approx(corr.hyperparams["l_mm"])
    assert round_tripped["pack"] == "prior-hook"


# ═══════════════════════════════ ⑪ 관측 단위 검증

def test_unsupported_observation_unit_raises_value_error():
    points = [_point(0.01 * i, 100.0 + i, unit="kPa") for i in range(8)]
    record = _record(points)
    res = ingest.ingest_record(record)
    with pytest.raises(ValueError):
        fit_npw.fit("oxide_silica", res)


def test_mixed_units_among_kept_rows_raises_value_error():
    points = [_point(0.01 * i, 140.0 + i, unit="nm") for i in range(4)]
    points += [_point(0.05 + 0.01 * i, 2.0 + i, unit="nm_per_min") for i in range(4)]
    record = _record(points)
    res = ingest.ingest_record(record)
    with pytest.raises(ValueError):
        fit_npw.fit("oxide_silica", res)


# ═══════════════════════════════ ⑫ 엔진 격자 밖 측정점 — 외삽 대신 버림

def test_out_of_grid_measurement_dropped_not_extrapolated():
    from sim.engine import Recipe, simulate
    engine_r_max_mm = float(simulate(Recipe(pack="oxide_silica")).radius_m.max() * 1000.0)

    in_grid_points = [_point(0.01 * i, 142.0 + 0.1 * i) for i in range(8)]
    out_of_grid_point = _point((engine_r_max_mm + 1.0) / 1000.0, 142.35)  # 값은 정상범위(outlier 아님)
    record = _record(in_grid_points + [out_of_grid_point], edge_exclusion_mm=0.0)

    res = ingest.ingest_record(record)
    assert res.n_excluded == 0  # edge_exclusion_mm=0 — ingest 단계에서는 안 빠짐

    corr = fit_npw.fit("oxide_silica", res, seed=0, n_restarts=3)
    assert corr.n_dropped["out_of_grid"] == 1
    assert corr.n_train == 8
    assert any("밖" in note for note in corr.notes)
