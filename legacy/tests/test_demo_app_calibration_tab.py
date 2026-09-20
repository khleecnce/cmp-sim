"""sim/demo_app.py 탭3(캘리브레이션) 테스트 — S10.

AppTest로 file_uploader에 실제 파일을 주입하기 어려워(Streamlit AppTest는
UploadedFile 합성을 지원하지 않음), CSV→record 변환은 demo_app._csv_to_record
순수 함수를 직접 단위테스트한다(과제 지시 사항). 앱 로드/탭 개수/비업로드 상태는
AppTest로, verdict 렌더링 규칙은 demo_app._success_message 순수 함수로 검증한다.

sim/calibration/ 원본 무수정은 `git diff --stat sim/calibration sim/engine.py`로
별도 확인한다(이 파일은 그 모듈들을 import만 해서 심볼이 여전히 존재하는지 확인).
"""
from pathlib import Path

import pandas as pd
import pytest
from streamlit.testing.v1 import AppTest

import sim.demo_app as demo_app

APP_PATH = str(Path(__file__).resolve().parent.parent / "sim" / "demo_app.py")


def _npw_df():
    return pd.DataFrame({
        "r_mm": [5.0, 40.0, 80.0, 120.0, 140.0],
        "theta_deg": [0.0, 30.0, 60.0, 90.0, 120.0],
        "thickness_nm": [120.0, 110.0, 95.0, 80.0, 60.0],
    })


# ═══════════════════════════════ ① 앱 로드 + 탭 3개

def test_app_loads_with_three_tabs():
    at = AppTest.from_file(APP_PATH, default_timeout=60)
    at.run()
    assert len(at.exception) == 0
    assert len(at.tabs) == 3


# ═══════════════════════════════ ② CSV 미업로드 — 예외 없이 안내만, 자동 실행 없음

def test_no_csv_uploaded_shows_guidance_without_running_pipeline():
    at = AppTest.from_file(APP_PATH, default_timeout=60)
    at.run()
    assert len(at.exception) == 0
    infos = [i.value for i in at.info]
    assert any("NPW CSV" in v for v in infos)
    # StageRecord 표 제목이 아직 없어야 한다(파이프라인이 자동 실행되지 않음).
    headers = [h.value for h in at.subheader]
    assert not any("단계별 실행 기록" in h for h in headers)


# ═══════════════════════════════ ③ _csv_to_record — 정상 변환(polar)

def test_csv_to_record_polar_success():
    record = demo_app._csv_to_record(
        _npw_df(), coord_kind="polar", value_col="thickness_nm", value_unit="nm",
        wafer_id="W-CSV-1", wafer_diameter_mm=300, notch_direction="Bottom",
        edge_exclusion_mm=3.0, series_id="csv-series",
        r_col="r_mm", r_unit="mm", theta_col="theta_deg", theta_unit="deg",
    )
    assert record["wafer_id"] == "W-CSV-1"
    assert record["coord_kind"] == "polar"
    assert len(record["points"]) == 5
    assert record["points"][0]["r_m"] == pytest.approx(0.005)
    assert record["points"][0]["value"] == pytest.approx(120.0)
    assert record["points"][0]["unit"] == "nm"

    # 이렇게 만든 record는 실제로 ingest.ingest_record()를 통과해야 한다(계약 확인).
    from sim.calibration import ingest
    result = ingest.ingest_record(record)
    assert result.n_rows == 5


# ═══════════════════════════════ ④ run_calibration까지 실제로 구동(순수 함수 경로로)

def test_csv_record_feeds_run_calibration_and_produces_stage_records():
    record = demo_app._csv_to_record(
        _npw_df(), coord_kind="polar", value_col="thickness_nm", value_unit="nm",
        wafer_id="W-CSV-2", wafer_diameter_mm=300, notch_direction="Bottom",
        edge_exclusion_mm=0.0, r_col="r_mm", r_unit="mm", theta_col="theta_deg", theta_unit="deg",
    )
    from sim.calibration import pipeline
    run = pipeline.run_calibration("oxide_silica", record)
    names = {s.name for s in run.stages}
    assert {"priors", "ingest_npw", "fit_npw", "ingest_ptw", "fit_ptw"} <= names
    assert run.verdict in {"calibrated", "partial", "uncalibrated", "failed"}


# ═══════════════════════════════ ⑤ _csv_to_record — 필수 열 누락은 조용히 채우지 않고 실패

def test_csv_to_record_missing_required_column_raises():
    with pytest.raises(ValueError, match="필수 열 매핑이 비어 있다"):
        demo_app._csv_to_record(
            _npw_df(), coord_kind="polar", value_col="thickness_nm", value_unit="nm",
            wafer_id="W-CSV-3", wafer_diameter_mm=300, notch_direction="Bottom",
            edge_exclusion_mm=0.0, r_col=None, theta_col="theta_deg",
        )


def test_csv_to_record_unknown_column_raises():
    with pytest.raises(ValueError, match="CSV에 없다"):
        demo_app._csv_to_record(
            _npw_df(), coord_kind="polar", value_col="does_not_exist", value_unit="nm",
            wafer_id="W-CSV-4", wafer_diameter_mm=300, notch_direction="Bottom",
            edge_exclusion_mm=0.0, r_col="r_mm", theta_col="theta_deg",
        )


def test_csv_to_record_empty_wafer_id_raises():
    with pytest.raises(ValueError, match="wafer_id"):
        demo_app._csv_to_record(
            _npw_df(), coord_kind="polar", value_col="thickness_nm", value_unit="nm",
            wafer_id="", wafer_diameter_mm=300, notch_direction="Bottom",
            edge_exclusion_mm=0.0, r_col="r_mm", theta_col="theta_deg",
        )


def test_csv_to_record_die_coord_kind_not_supported():
    with pytest.raises(ValueError, match="die"):
        demo_app._csv_to_record(
            _npw_df(), coord_kind="die", value_col="thickness_nm", value_unit="nm",
            wafer_id="W-CSV-5", wafer_diameter_mm=300, notch_direction="Bottom",
            edge_exclusion_mm=0.0,
        )


# ═══════════════════════════════ ⑥ verdict != calibrated → 성공 문구 없음

def test_success_message_only_for_calibrated_verdict():
    assert demo_app._success_message("calibrated") is not None
    for verdict in ("partial", "uncalibrated", "failed"):
        assert demo_app._success_message(verdict) is None


# ═══════════════════════════════ ⑦ sim/calibration/ 모듈 — import만, 공개 계약 유지

def test_calibration_modules_imported_not_reimplemented():
    from sim.calibration import fit_npw, fit_ptw, ingest, pipeline, predict, prior
    from sim.calibration.ptw_vm_schema import PTWVMInput, is_npw_equivalent

    assert hasattr(pipeline, "run_calibration")
    assert hasattr(pipeline, "evaluate_new_lot")
    assert hasattr(ingest, "ingest_record")
    assert hasattr(predict, "predict_radial")
    assert hasattr(fit_npw, "fit")
    assert hasattr(fit_ptw, "fit")
    assert hasattr(prior, "build_param_priors")
    assert callable(is_npw_equivalent)
    assert PTWVMInput is not None

    # demo_app이 이 심볼들을 그대로 재노출하는지(감싸서 동작을 바꾸지 않았는지).
    assert demo_app.cal_pipeline.run_calibration is pipeline.run_calibration
    assert demo_app.cal_predict.predict_radial is predict.predict_radial


# ═══════════════════════════════ ⑧ 드리프트 섹션 — cal_run 없으면 안 보이고, 탭 개수는 그대로 3

def test_no_cal_run_hides_drift_section_and_tab_count_stays_three():
    at = AppTest.from_file(APP_PATH, default_timeout=60)
    at.run()
    assert len(at.exception) == 0
    assert len(at.tabs) == 3
    headers = [h.value for h in at.subheader]
    assert not any("드리프트 점검" in h for h in headers)


# ═══════════════════════════════ ⑨ cal_run이 session_state에 있으면 드리프트 섹션이 뜬다

def test_cal_run_in_session_state_shows_drift_section():
    from sim.calibration import pipeline

    record = demo_app._csv_to_record(
        _npw_df(), coord_kind="polar", value_col="thickness_nm", value_unit="nm",
        wafer_id="W-CSV-DRIFT", wafer_diameter_mm=300, notch_direction="Bottom",
        edge_exclusion_mm=0.0, r_col="r_mm", r_unit="mm", theta_col="theta_deg", theta_unit="deg",
    )
    run = pipeline.run_calibration("oxide_silica", record)

    at = AppTest.from_file(APP_PATH, default_timeout=60)
    at.session_state["cal_run"] = run
    at.run()
    assert len(at.exception) == 0
    assert len(at.tabs) == 3
    headers = [h.value for h in at.subheader]
    assert any("드리프트 점검" in h for h in headers)
    infos = [i.value for i in at.info]
    assert any("새 로트 CSV" in v for v in infos)
    # 재적합 버튼이 없다 — 드리프트 섹션 버튼은 "드리프트 점검 실행" 하나뿐이어야 한다.
    button_labels = [b.label for b in at.button]
    assert "드리프트 점검 실행" in button_labels
    assert not any("재적합" in lbl for lbl in button_labels)
