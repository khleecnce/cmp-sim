"""sim/calibration/pipeline.py 계약 테스트 — ORG.md §7.6 M3-5.

이 파일이 처음으로 5개 캘리브레이션 모듈(ingest→prior→fit_npw→fit_ptw)을
한 사슬로 실제로 돌려서 M5 데모 경로("CSV 업로드 → NPW 보정 → PTW 예측")가
기계적으로 성립하는지 확인한다. 전부 합성 데이터만 쓴다(실측·회사데이터 금지).

여기서 고정하는 것:
  ① 전체 사슬 정상 경로(NPW만) — 실측 LOO RMSE 그대로 고정
  ② NPW+PTW 경로 — 두 층 모두 improved=True, verdict="calibrated"
  ③ ptw_source 없음 → fit_ptw 단계 skipped, reason에 사유 명시
  ④ is_npw_equivalent=True인 ptw_input → fit_ptw 거부되고 사유 기록, verdict="partial"
  ⑤ 선행(fit_npw) 실패 → 후속(fit_ptw) skipped, reason에 선행 단계 이름("fit_npw") 포함
  ⑥ evaluate_new_lot: 같은 분포 → ok, 오프셋 주입 → alarm
  ⑦ 단방향 — pipeline 실행 후 npw_correction 하이퍼파라미터가 독립적으로 재계산한
     fit_npw.fit 결과와 정확히 같다(PTW 적합이 이를 되돌려 고치지 않았다는 증거)
  ⑧ improved=False를 성공으로 포장하지 않는다 — 순수 노이즈 입력 → verdict="uncalibrated"
  ⑨ M5 데모 스모크 — run.npw_correction/ptw_correction을 predict.predict_radial에
     그대로 먹여서 유한한 예측값이 나오는지(사슬의 출력이 실제로 소비 가능한지)
"""
from __future__ import annotations

import numpy as np
import pytest

from sim.calibration import fit_npw, ingest, pipeline, predict
from sim.calibration.ptw_vm_schema import PTWVMInput
from sim.engine import Recipe, simulate

PACK = "oxide_silica"
_ENGINE_RESULT = simulate(Recipe(pack=PACK))


def _physics_nm(r_mm):
    return np.interp(r_mm, _ENGINE_RESULT.radius_m * 1000.0, _ENGINE_RESULT.removed_nm)


def _true_curve(r_mm):
    return 3.0 * np.sin(r_mm / 40.0)


def _ptw_curve(r_mm):
    return 2.0 * np.cos(r_mm / 30.0)


def _make_record(r_mm, values, wafer_id, series_id="pipe-series", unit="nm"):
    points = [{"r_m": float(r) / 1000.0, "theta_rad": 0.0, "value": float(v), "unit": unit}
              for r, v in zip(r_mm, values)]
    return {
        "wafer_id": wafer_id, "wafer_diameter_mm": 300, "notch_direction": "Bottom",
        "edge_exclusion_mm": 3.0, "coord_kind": "polar", "series_id": series_id, "points": points,
    }


def _npw_record(seed=0, wafer_id="W-PIPE-NPW"):
    r_train = np.linspace(5.0, 135.0, 25)
    rng = np.random.default_rng(seed)
    values = _physics_nm(r_train) + _true_curve(r_train) + rng.normal(0.0, 0.3, size=len(r_train))
    return _make_record(r_train, values, wafer_id), r_train


def _ptw_record(seed=5, wafer_id="W-PIPE-PTW"):
    r_train = np.linspace(5.0, 135.0, 25)
    rng = np.random.default_rng(seed)
    values = (_physics_nm(r_train) + _true_curve(r_train) + _ptw_curve(r_train)
              + rng.normal(0.0, 0.05, size=len(r_train)))
    return _make_record(r_train, values, wafer_id), r_train


def _mixed_unit_record():
    """schema는 통과하지만(둘 다 유효 enum) fit_npw.fit이 거부하는 단위 혼재 레코드."""
    points = [
        {"r_m": 0.01, "theta_rad": 0.0, "value": 10.0, "unit": "nm"},
        {"r_m": 0.02, "theta_rad": 0.0, "value": 5.0, "unit": "kPa"},
        {"r_m": 0.03, "theta_rad": 0.0, "value": 8.0, "unit": "nm"},
        {"r_m": 0.04, "theta_rad": 0.0, "value": 9.0, "unit": "nm"},
        {"r_m": 0.05, "theta_rad": 0.0, "value": 7.0, "unit": "nm"},
    ]
    return {
        "wafer_id": "W-MIX", "wafer_diameter_mm": 300, "notch_direction": "Bottom",
        "edge_exclusion_mm": 0.0, "coord_kind": "polar", "series_id": "mix", "points": points,
    }


def _stage(run, name):
    for s in run.stages:
        if s.name == name:
            return s
    raise KeyError(name)


# ═══════════════════════════════ ① 전체 사슬 — NPW만

def test_full_chain_npw_only_matches_measured_values():
    record, _ = _npw_record()
    run = pipeline.run_calibration(PACK, record, seed=0, n_restarts=6)

    assert _stage(run, "priors").status == "ok"
    assert _stage(run, "ingest_npw").status == "ok"
    assert _stage(run, "fit_npw").status == "ok"
    assert _stage(run, "ingest_ptw").status == "skipped"
    assert _stage(run, "fit_ptw").status == "skipped"

    assert run.npw_correction is not None
    assert run.ptw_correction is None
    assert run.npw_correction.n_train == 25
    assert run.npw_correction.improved is True
    # 실측치(2026-09-19, seed=0, n_restarts=6) 그대로 고정 — 절대값 assert.
    assert run.npw_correction.loo_rmse_baseline == pytest.approx(1.9829812278214525, rel=1e-6)
    assert run.npw_correction.loo_rmse_gp == pytest.approx(0.24090826395349643, rel=1e-6)
    assert run.verdict == "calibrated"


# ═══════════════════════════════ ② NPW+PTW 경로

def test_full_chain_npw_plus_ptw():
    npw_record, _ = _npw_record(seed=0)
    ptw_record, _ = _ptw_record(seed=5)
    ptw_input = PTWVMInput(product_id="P1", layer="M1", die_density_mean=0.4, local_density=0.4)

    run = pipeline.run_calibration(
        PACK, npw_record, ptw_source=ptw_record, ptw_input=ptw_input, seed=0, n_restarts=8
    )

    for name in ("priors", "ingest_npw", "fit_npw", "ingest_ptw", "fit_ptw"):
        assert _stage(run, name).status == "ok", (name, _stage(run, name).reason)

    assert run.npw_correction.improved is True
    assert run.ptw_correction is not None
    assert run.ptw_correction.improved is True
    assert run.verdict == "calibrated"
    assert "NPW+PTW" in run.note


# ═══════════════════════════════ ③ ptw_source 없음 → skipped + 사유

def test_missing_ptw_source_skips_with_reason():
    record, _ = _npw_record()
    run = pipeline.run_calibration(PACK, record)

    ptw_stage = _stage(run, "fit_ptw")
    assert ptw_stage.status == "skipped"
    assert "ptw_source" in ptw_stage.reason
    assert run.ptw_correction is None


# ═══════════════════════════════ ④ is_npw_equivalent=True → 거부 + 사유

def test_npw_equivalent_ptw_input_rejected_with_reason():
    npw_record, _ = _npw_record()
    equivalent_input = PTWVMInput(product_id="P1", layer="M1", die_density_mean=0.3)  # local_density/topography 없음

    run = pipeline.run_calibration(
        PACK, npw_record, ptw_source=npw_record, ptw_input=equivalent_input, seed=0, n_restarts=6
    )

    ptw_stage = _stage(run, "fit_ptw")
    assert ptw_stage.status == "skipped"
    assert "is_npw_equivalent" in ptw_stage.reason
    assert run.verdict == "partial"
    # fit_ptw.fit이 실제로 호출됐다는 증거 — 거부 결과 객체 자체는 반환된다(우회 없음).
    assert run.ptw_correction is not None
    assert run.ptw_correction.n_train == 0
    assert run.ptw_correction.hyperparams == {}


# ═══════════════════════════════ ⑤ 선행 실패 → 후속 skipped(선행 이름 포함)

def test_upstream_failure_skips_downstream_with_named_reason():
    mixed = _mixed_unit_record()
    ptw_input = PTWVMInput(product_id="P1", layer="M1", die_density_mean=0.4, local_density=0.4)

    run = pipeline.run_calibration(PACK, mixed, ptw_source=mixed, ptw_input=ptw_input)

    assert _stage(run, "ingest_npw").status == "ok"
    assert _stage(run, "fit_npw").status == "failed"

    ptw_stage = _stage(run, "fit_ptw")
    assert ptw_stage.status == "skipped"
    assert "fit_npw" in ptw_stage.reason

    assert run.npw_correction is None
    assert run.ptw_correction is None
    assert run.verdict == "failed"


# ═══════════════════════════════ ⑥ evaluate_new_lot — ok / alarm

def test_evaluate_new_lot_ok_and_alarm():
    record, _ = _npw_record(seed=0)
    run = pipeline.run_calibration(PACK, record, seed=0, n_restarts=6)
    assert run.npw_correction.improved is True

    r_new = np.linspace(5.0, 135.0, 20)
    rng = np.random.default_rng(1)

    same_dist_values = _physics_nm(r_new) + _true_curve(r_new) + rng.normal(0.0, 0.3, size=len(r_new))
    ok_record = _make_record(r_new, same_dist_values, "W-NEW-OK")
    ok_report = pipeline.evaluate_new_lot(run, ok_record)
    assert ok_report.verdict == "ok"

    offset_values = (_physics_nm(r_new) + _true_curve(r_new) + 5.0
                      + rng.normal(0.0, 0.3, size=len(r_new)))
    alarm_record = _make_record(r_new, offset_values, "W-NEW-ALARM")
    alarm_report = pipeline.evaluate_new_lot(run, alarm_record)
    assert alarm_report.verdict == "alarm"


# ═══════════════════════════════ ⑦ 단방향 — PTW 적합이 NPW 하이퍼파라미터를 되돌려 고치지 않음

def test_npw_hyperparams_unchanged_after_ptw_fit():
    npw_record, _ = _npw_record(seed=0)
    ptw_record, _ = _ptw_record(seed=5)
    ptw_input = PTWVMInput(product_id="P1", layer="M1", die_density_mean=0.4, local_density=0.4)

    run = pipeline.run_calibration(
        PACK, npw_record, ptw_source=ptw_record, ptw_input=ptw_input, seed=0, n_restarts=8
    )

    # 독립적으로 재계산한 fit_npw.fit(같은 인자)과 정확히 같아야 한다 — PTW 적합이
    # npw_correction을 대입/변형했다면 이 등식이 깨진다.
    independent_npw = fit_npw.fit(PACK, ingest.ingest_record(npw_record), seed=0, n_restarts=8)
    assert run.npw_correction.hyperparams == independent_npw.hyperparams
    assert run.npw_correction.loo_rmse_gp == independent_npw.loo_rmse_gp
    assert run.npw_correction.improved == independent_npw.improved


# ═══════════════════════════════ ⑧ improved=False는 성공으로 포장하지 않는다

def test_pure_noise_is_uncalibrated_not_calibrated():
    r = np.linspace(5.0, 135.0, 25)
    rng = np.random.default_rng(1)  # 실측 확인(2026-09-19): 이 seed는 안정적으로 improved=False
    values = _physics_nm(r) + rng.normal(0.0, 5.0, size=len(r))  # 구조 없는 순수노이즈
    record = _make_record(r, values, "W-NOISE")

    run = pipeline.run_calibration(PACK, record, seed=0, n_restarts=3)

    fit_stage = _stage(run, "fit_npw")
    assert fit_stage.status == "ok"  # fit 자체는 정상 실행됐다 — 예외 아님
    assert fit_stage.metrics["improved"] is False
    assert run.verdict == "uncalibrated"
    assert run.verdict != "calibrated"


# ═══════════════════════════════ ⑨ M5 데모 스모크 — 사슬 출력이 실제로 소비 가능한가

def test_npw_correction_feeds_predict_radial():
    record, r_train = _npw_record(seed=0)
    run = pipeline.run_calibration(PACK, record, seed=0, n_restarts=6)
    assert run.npw_correction.improved is True

    result = predict.predict_radial(PACK, r_train, correction=run.npw_correction)
    assert np.all(np.isfinite(result.corrected_nm))
    assert result.layers_applied == ["npw"]


def test_ptw_correction_feeds_predict_radial():
    npw_record, _ = _npw_record(seed=0)
    ptw_record, r_train = _ptw_record(seed=5)
    ptw_input = PTWVMInput(product_id="P1", layer="M1", die_density_mean=0.4, local_density=0.4)

    run = pipeline.run_calibration(
        PACK, npw_record, ptw_source=ptw_record, ptw_input=ptw_input, seed=0, n_restarts=8
    )
    assert run.ptw_correction.improved is True

    result = predict.predict_radial(PACK, r_train, correction=run.ptw_correction)
    assert np.all(np.isfinite(result.corrected_nm))
    assert result.layers_applied == ["npw", "ptw"]
