"""tools/make_demo_csv.py + data/demo/*.csv 테스트 — M5 데모 데이터 게이트.

sim/calibration/·sim/engine.py는 여기서도 읽기만 한다(수정 대상 아님).
"""
from __future__ import annotations

import pathlib

import pandas as pd
import pytest

from tools import make_demo_csv

ROOT = pathlib.Path(__file__).resolve().parent.parent
DEMO_DIR = ROOT / "data" / "demo"


def _record_from_df(df, *, wafer_id: str):
    from sim.demo_app import _csv_to_record
    return _csv_to_record(
        df, coord_kind="polar", value_col="thickness_nm", value_unit="nm",
        wafer_id=wafer_id, wafer_diameter_mm=300, notch_direction="Bottom",
        edge_exclusion_mm=0.0, r_col="r_mm", r_unit="mm",
        theta_col="theta_deg", theta_unit="deg",
    )


# ① 결정성 — 같은 시드 → 비트 동일 CSV

def test_make_demo_csv_deterministic_same_seed():
    df1 = make_demo_csv.make_npw_df(seed=111)
    df2 = make_demo_csv.make_npw_df(seed=111)
    pd.testing.assert_frame_equal(df1, df2)

    df_drift1 = make_demo_csv.make_npw_drifted_df(seed=222)
    df_drift2 = make_demo_csv.make_npw_drifted_df(seed=222)
    pd.testing.assert_frame_equal(df_drift1, df_drift2)


# ② 생성된 CSV → _csv_to_record → ingest.validate_record 스키마 오류 0건

@pytest.mark.parametrize("filename", [
    "npw_oxide_silica.csv", "ptw_oxide_silica.csv", "npw_oxide_silica_drifted.csv",
])
def test_generated_csv_passes_ingest_schema(filename):
    from sim.calibration import ingest
    df = pd.read_csv(DEMO_DIR / filename)
    record = _record_from_df(df, wafer_id=f"DEMO-{filename}")
    errors = ingest.validate_record(record)
    assert errors == []
    result = ingest.ingest_record(record)
    assert result.n_rows == len(df)


# ③ 정상 CSV로 run_calibration verdict == "calibrated"

def test_npw_csv_calibrates():
    from sim.calibration import pipeline
    df = pd.read_csv(DEMO_DIR / "npw_oxide_silica.csv")
    record = _record_from_df(df, wafer_id="DEMO-NPW-CAL")
    run = pipeline.run_calibration("oxide_silica", record)
    assert run.verdict == "calibrated"
    assert run.npw_correction is not None
    assert run.npw_correction.improved is True


# ④ drifted CSV는 evaluate_new_lot에서 정상 CSV보다 큰 편차를 보고한다

def test_drifted_csv_shows_larger_drift_than_clean_lot():
    from sim.calibration import pipeline
    npw_df = pd.read_csv(DEMO_DIR / "npw_oxide_silica.csv")
    drifted_df = pd.read_csv(DEMO_DIR / "npw_oxide_silica_drifted.csv")

    run = pipeline.run_calibration(
        "oxide_silica", _record_from_df(npw_df, wafer_id="DEMO-NPW-REF"),
    )
    assert run.verdict == "calibrated"

    clean_report = pipeline.evaluate_new_lot(
        run, _record_from_df(npw_df, wafer_id="DEMO-NPW-CLEAN-LOT"),
    )
    drift_report = pipeline.evaluate_new_lot(
        run, _record_from_df(drifted_df, wafer_id="DEMO-NPW-DRIFT-LOT"),
    )

    assert drift_report.rmse_new > clean_report.rmse_new
    assert drift_report.frac_outside_90ci > clean_report.frac_outside_90ci
    assert drift_report.verdict == "alarm"
    assert clean_report.verdict == "ok"


# ⑤ CSV/README에 "SYNTHETIC" 표기가 실제로 들어 있다

@pytest.mark.parametrize("filename", [
    "npw_oxide_silica.csv", "ptw_oxide_silica.csv", "npw_oxide_silica_drifted.csv",
])
def test_csv_has_synthetic_marker_column(filename):
    df = pd.read_csv(DEMO_DIR / filename)
    assert "data_source" in df.columns
    assert (df["data_source"] == "SYNTHETIC").all()


def test_readme_declares_synthetic():
    text = (DEMO_DIR / "README.md").read_text(encoding="utf-8")
    assert "SYNTHETIC" in text
    assert "실측 아님" in text
