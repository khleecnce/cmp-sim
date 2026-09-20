"""sim/calibration/ingest.py — 스키마 검증·정준화·파케이 왕복을 잠근다.

M3 게이트(agents/ORG.md §7.4/§7.6) 항목: data/schema + sim/calibration/ingest.py.
가장 중요한 계약은 가역성이다 — normalize.py §0 원칙("정규화는 손실이 있어선
안 된다")을 ingest.py 도 그대로 승계한다. 이 파일은 그 계약이 코드에서
드리프트하지 않는지를 잠근다.
"""
from __future__ import annotations

import ast
import json
import pathlib
import subprocess

import jsonschema
import numpy as np
import pytest

from sim.calibration import ingest, normalize

ROOT = pathlib.Path(__file__).resolve().parent.parent
SCHEMA_PATH = ROOT / "data" / "schema" / "wafer_measurement.schema.json"
SYNTHETIC_DIR = ROOT / "data" / "synthetic"


def _base_record(**overrides):
    record = {
        "wafer_id": "W-TEST-1",
        "wafer_diameter_mm": 300,
        "notch_direction": "Bottom",
        "edge_exclusion_mm": 3.0,
        "coord_kind": "polar",
        "series_id": "test-series",
        "points": [
            {"r_m": 0.0, "theta_rad": 0.0, "value": 100.0, "unit": "nm"},
            {"r_m": 0.05, "theta_rad": 0.0, "value": 14.5, "unit": "psi"},
            {"r_m": 0.148, "theta_rad": 0.0, "value": None, "unit": "nm"},
            {"r_m": 0.02, "theta_rad": 1.0, "value": 500.0, "unit": "angstrom"},
            {"r_m": 0.03, "theta_rad": 2.0, "value": 60.0, "unit": "rpm", "radius_m": 0.15},
            {"r_m": 0.01, "theta_rad": 0.5, "value": 101.0, "unit": "nm"},
            {"r_m": 0.015, "theta_rad": 0.7, "value": 99.0, "unit": "nm"},
        ],
    }
    record.update(overrides)
    return record


# 1. 스키마 파일이 유효한 JSON Schema다
def test_schema_file_is_valid_json_schema():
    schema = ingest.load_schema()
    jsonschema.Draft202012Validator.check_schema(schema)


# 2. notch_direction enum이 normalize.NOTCH_ANGLES_RAD 키와 정확히 일치
def test_notch_direction_enum_matches_normalize():
    schema = ingest.load_schema()
    enum = set(schema["properties"]["notch_direction"]["enum"])
    assert enum == set(normalize.NOTCH_ANGLES_RAD.keys())


# 3. unit enum이 normalize가 아는 단위(= _SCALAR_FACTORS 키 ∪ 'rpm' ∪ 그 정준 출력단위)를
#    전부 포함하고, 그 밖의(normalize가 모르는) 값은 없다.
def test_unit_enum_matches_normalize_known_units():
    schema = ingest.load_schema()
    enum = set(schema["$defs"]["point"]["properties"]["unit"]["enum"])
    scalar_units = set(normalize._SCALAR_FACTORS.keys())
    canonical_units = {cu for cu, _ in normalize._SCALAR_FACTORS.values()} | {"m_per_s"}
    known = scalar_units | {"rpm"} | canonical_units

    assert scalar_units <= enum, "normalize._SCALAR_FACTORS 키가 enum에서 빠졌다"
    assert "rpm" in enum
    assert enum <= known, f"normalize가 모르는 단위가 스키마에 들어감: {enum - known}"


def test_ingest_record_rejects_unit_normalize_does_not_know():
    record = _base_record()
    record["points"][0]["unit"] = "furlong_per_fortnight"
    errs = ingest.validate_record(record)
    assert errs, "정의되지 않은 단위는 validate_record가 거부해야 한다"
    with pytest.raises(ValueError):
        ingest.ingest_record(record)


# 4. 정상 레코드 ingest → n_rows 일치, 단위 환산 정확
def test_ingest_record_converts_units_correctly():
    record = _base_record()
    res = ingest.ingest_record(record)
    assert res.n_rows == len(record["points"])

    d = res.table.to_pydict()
    # psi -> kPa
    i_psi = d["unit_raw"].index("psi")
    assert d["value_canonical"][i_psi] == pytest.approx(14.5 * 6.894757, rel=1e-12)
    assert d["unit_canonical"][i_psi] == "kPa"
    # angstrom -> nm
    i_ang = d["unit_raw"].index("angstrom")
    assert d["value_canonical"][i_ang] == pytest.approx(500.0 * 0.1, rel=1e-12)
    assert d["unit_canonical"][i_ang] == "nm"
    # rpm -> m_per_s
    i_rpm = d["unit_raw"].index("rpm")
    expected = 2.0 * np.pi * 0.15 * (60.0 / 60.0)
    assert d["value_canonical"][i_rpm] == pytest.approx(expected, rel=1e-12)
    assert d["unit_canonical"][i_rpm] == "m_per_s"
    # 이미 정준단위(nm)는 그대로 통과
    i_nm = d["unit_raw"].index("nm")
    assert d["value_canonical"][i_nm] == pytest.approx(d["value_raw"][i_nm], rel=1e-12)


# 5. 엣지제외 행이 삭제되지 않고 플래그만 됨
def test_edge_exclusion_rows_are_flagged_not_dropped():
    record = _base_record()
    res = ingest.ingest_record(record)
    assert res.n_rows == len(record["points"])  # 아무것도 삭제되지 않았다
    assert res.n_excluded >= 1
    d = res.table.to_pydict()
    excluded_idx = [i for i, e in enumerate(d["is_excluded"]) if e]
    assert excluded_idx, "엣지제외 플래그가 하나도 없다 — 테스트 픽스처가 잘못됨"
    # r=0.148mm 근처(웨이퍼 반경 150mm - EE 3mm = 147mm 밖)의 점이 실제로 남아있다
    assert d["r_mm"][excluded_idx[0]] > 147.0


# 6. 이상치 행이 삭제되지 않고 플래그+사유가 남음
def test_outlier_rows_are_flagged_not_dropped():
    record = _base_record()
    # 명백한 이상치 하나 추가 (나머지는 ~100nm대, 이건 10000nm)
    record["points"].append({"r_m": 0.06, "theta_rad": 0.1, "value": 10000.0, "unit": "nm"})
    res = ingest.ingest_record(record)
    assert res.n_rows == len(record["points"])
    assert res.n_outliers >= 1
    d = res.table.to_pydict()
    outlier_idx = [i for i, o in enumerate(d["is_outlier"]) if o]
    assert outlier_idx
    assert d["value_canonical"][outlier_idx[-1]] == pytest.approx(10000.0)
    assert d["outlier_reason"][outlier_idx[-1]] is not None


# 7. 왕복(round-trip): write_parquet -> read_parquet 값·플래그·provenance 보존
def test_parquet_round_trip_preserves_values_flags_provenance(tmp_path):
    record = _base_record()
    res = ingest.ingest_record(record)
    path = ingest.write_parquet(res, tmp_path / "w.parquet")
    table2 = ingest.read_parquet(path)

    d1 = res.table.to_pydict()
    d2 = table2.to_pydict()
    assert d1 == d2

    meta = json.loads(table2.schema.metadata[b"fabsim_ingest_meta"])
    assert meta["provenance"] == res.provenance
    assert meta["n_rows"] == res.n_rows
    assert meta["n_excluded"] == res.n_excluded
    assert meta["n_missing"] == res.n_missing
    assert meta["n_outliers"] == res.n_outliers
    assert meta["schema_version"] == res.schema_version


# 8. 가역성: provenance의 원 단위로 되돌리면 원 값이 복원됨(rel=1e-12)
def test_reversibility_from_provenance_raw_record(tmp_path):
    record = _base_record()
    res = ingest.ingest_record(record)
    path = ingest.write_parquet(res, tmp_path / "w2.parquet")
    table2 = ingest.read_parquet(path)
    meta = json.loads(table2.schema.metadata[b"fabsim_ingest_meta"])
    raw_points = meta["provenance"]["raw_record"]["points"]

    d = table2.to_pydict()
    for i, raw_p in enumerate(raw_points):
        raw_unit = d["unit_raw"][i]
        assert raw_unit == raw_p["unit"]
        raw_value = raw_p["value"]
        if raw_value is None:
            assert d["value_raw"][i] is None
            continue
        assert d["value_raw"][i] == pytest.approx(raw_value, rel=1e-12)
        # 정준값을 원 단위로 되돌리면 원 값이 복원된다
        canonical = d["value_canonical"][i]
        if raw_unit in normalize._SCALAR_FACTORS:
            _, factor = normalize._SCALAR_FACTORS[raw_unit]
            restored = canonical / factor
        elif raw_unit == "rpm":
            radius_m = raw_p["radius_m"]
            restored = canonical / (2.0 * np.pi * radius_m) * 60.0
        else:
            restored = canonical  # 이미 정준단위
        assert restored == pytest.approx(raw_value, rel=1e-12)

        # 각 행에 저장된 raw_point_json 도 원본 포인트와 정확히 같다(값 단위)
        stored = json.loads(d["raw_point_json"][i])
        assert stored["value"] == raw_p["value"]
        assert stored["unit"] == raw_p["unit"]


# 9. 스키마 위반(잘못된 unit/notch/음수 EE) -> validate_record가 오류 반환, ingest 거부
@pytest.mark.parametrize("mutate", [
    lambda r: r["points"][0].__setitem__("unit", "bogus_unit"),
    lambda r: r.__setitem__("notch_direction", "Nowhere"),
    lambda r: r.__setitem__("edge_exclusion_mm", -1.0),
    lambda r: r.__setitem__("wafer_diameter_mm", 999),
])
def test_invalid_records_are_rejected(mutate):
    record = _base_record()
    mutate(record)
    errs = ingest.validate_record(record)
    assert errs, f"위반이 감지되지 않았다: {record}"
    with pytest.raises(ValueError):
        ingest.ingest_record(record)


# 10. 합성 데이터 파일 2개가 실제로 스키마를 통과하고 ingest된다
def test_synthetic_files_exist_and_ingest():
    files = sorted(SYNTHETIC_DIR.glob("*.json"))
    assert len(files) >= 2, "data/synthetic/ 에 합성 웨이퍼 파일이 2개 이상 있어야 한다"
    for f in files:
        assert f.stat().st_size < 200_000, f"{f.name} 이 200KB 를 넘는다"
        record = json.loads(f.read_text(encoding="utf-8"))
        errs = ingest.validate_record(record)
        assert not errs, f"{f.name} 스키마 위반: {errs}"
        res = ingest.ingest_record(record)
        assert res.n_rows == len(record["points"])
        assert "_provenance" in record
        assert record["_provenance"].get("warning") == "합성 데이터 — 실측 아님"


# 11. normalize.py / series_scale.py / ptw_vm_schema.py 가 0바이트 수정됨
def test_existing_calibration_modules_untouched():
    # ⚠ 이 검사는 **워킹트리 가드**다 — 그 작업 지시가 세 파일을 건드리지 말라고
    #   했는지 확인할 뿐, HEAD 에 담긴 코드의 계약이 아니다. 그래서 git 워크트리가
    #   아닌 곳에서는 판정 자체가 성립하지 않는다.
    #   .githooks/pre-push 가 HEAD 를 임시 디렉토리로 export 해 pytest 를 돌리는데
    #   거기엔 .git 이 없어 `git diff` 가 128 로 죽고 check=True 가 예외를 냈다 —
    #   로컬 전체 스위트는 통과하는데 push 만 막히는 유형이라 원인을 엉뚱한 곳에서
    #   찾게 된다(2026-09-19 실제로 그랬다). 판정 불가일 때는 실패가 아니라 skip 이다.
    inside = subprocess.run(
        ["git", "rev-parse", "--is-inside-work-tree"],
        cwd=ROOT, capture_output=True, text=True,
    )
    if inside.returncode != 0 or inside.stdout.strip() != "true":
        pytest.skip("git 워크트리가 아니다(클린 export 등) — 워킹트리 가드는 판정 불가")
    result = subprocess.run(
        ["git", "diff", "--stat", "HEAD", "--",
         "sim/calibration/normalize.py",
         "sim/calibration/series_scale.py",
         "sim/calibration/ptw_vm_schema.py"],
        cwd=ROOT, capture_output=True, text=True, check=True,
    )
    assert result.stdout.strip() == "", (
        "normalize.py/series_scale.py/ptw_vm_schema.py 가 수정됐다 — 이 작업 지시는 "
        "이 세 파일을 1바이트도 건드리지 말라고 명시했다:\n" + result.stdout
    )


# 12. ingest가 engine.Recipe/WaferResult에 의존하지 않는다 (import 경계, ast로 고정)
def test_ingest_module_does_not_import_engine():
    src = (ROOT / "sim" / "calibration" / "ingest.py").read_text(encoding="utf-8")
    tree = ast.parse(src)
    imported_modules = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imported_modules.add(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imported_modules.add(node.module)
    forbidden = {m for m in imported_modules if m == "sim.engine" or m.startswith("sim.engine.")}
    assert not forbidden, f"ingest.py가 sim.engine에 의존한다: {forbidden}"
