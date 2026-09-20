"""실측/합성 웨이퍼 측정 레코드 수집 — 스키마 검증 → 정준 단위 → 파케이.

지식 근거: agents/ORG.md §7.4(데이터 파이프라인) · §7.6(M3 게이트).
좌표 정준화·단위 환산·이상치 플래그·엣지제외는 sim/calibration/normalize.py 를
그대로 재사용한다(재구현 금지 — 이 모듈은 그 위에 스키마 검증과 파케이 직렬화만 얹는다).

이 모듈은 sim/engine.py 의 Model 이 아니다. Recipe/WaferResult 스키마와 무관한
독립 유틸리티다(normalize.py·series_scale.py·ptw_vm_schema.py 와 동일한 지위).

원칙(normalize.py §0 계승): 정규화는 손실이 있어선 안 된다(가역). 원 단위·원
좌표계·notch·EE·이상치 파라미터를 전부 provenance 와 parquet 메타데이터에 보존한다.
이상치·엣지제외 행은 삭제하지 않고 플래그만 남긴다.

⚠ data/customer/ 는 [.gitignore] 대상이다 — 고객 데이터는 절대 커밋 금지
(ORG.md §7.5, 익명화 후에도 금지). 이 모듈이 읽는 것은 data/schema 로 검증된
합성/공개 데이터뿐이어야 한다.
"""
from __future__ import annotations

import json
import pathlib
from dataclasses import dataclass
from typing import Dict, List, Optional

import jsonschema
import numpy as np
import pyarrow as pa
import pyarrow.parquet as pq

from sim.calibration import normalize

_SCHEMA_PATH = (pathlib.Path(__file__).resolve().parent.parent.parent
                / "data" / "schema" / "wafer_measurement.schema.json")

# normalize 가 아는 "이미 정준단위인" 값 — _SCALAR_FACTORS.values() 의 canonical_unit +
# rpm 의 canonical_unit(m_per_s). 하드코딩하지 않고 normalize 에서 역산해 드리프트를 막는다.
_CANONICAL_UNITS = {cu for cu, _ in normalize._SCALAR_FACTORS.values()} | {"m_per_s"}

_PROVENANCE_KEY = b"fabsim_ingest_meta"

__all__ = [
    "IngestResult", "load_schema", "validate_record", "ingest_record",
    "write_parquet", "read_parquet",
]


@dataclass
class IngestResult:
    """스키마 검증을 통과한 웨이퍼 측정 레코드를 정준 단위 tidy 테이블로 옮긴 결과.

    provenance 는 원 단위·원 좌표계·notch·EE·이상치 method/k·원본 레코드 전체를
    보존한다 — parquet 로 왕복해도 원 값을 복원할 수 있어야 한다(가역 원칙).
    """
    table: "pa.Table"
    n_rows: int
    n_excluded: int
    n_missing: int
    n_outliers: int
    schema_version: str
    provenance: dict


def load_schema(path: Optional[pathlib.Path] = None) -> dict:
    p = pathlib.Path(path) if path is not None else _SCHEMA_PATH
    return json.loads(p.read_text(encoding="utf-8"))


def validate_record(record: dict, schema: Optional[dict] = None) -> List[str]:
    """JSON Schema 검증 오류 메시지 목록을 반환한다(빈 리스트=통과).

    예외를 던지지 않는다 — 호출측(ingest_record)이 거부 정책을 정한다.
    normalize 가 모르는 단위/notch 값은 스키마의 enum 이 이미 걸러낸다.
    """
    sch = schema if schema is not None else load_schema()
    validator = jsonschema.Draft202012Validator(sch)
    errors = sorted(validator.iter_errors(record), key=lambda e: list(e.path))
    return [f"{'/'.join(str(p) for p in e.path) or '(root)'}: {e.message}" for e in errors]


def _canonical_coords(record: dict) -> normalize.CanonicalCoords:
    kind = record["coord_kind"]
    notch_dir = record["notch_direction"]
    points = record["points"]
    if kind == "polar":
        coords = ([p["r_m"] for p in points], [p["theta_rad"] for p in points])
    elif kind == "cartesian":
        coords = ([p["x_m"] for p in points], [p["y_m"] for p in points])
    elif kind == "die":
        coords = (
            [p["col"] for p in points], [p["row"] for p in points],
            [p["pitch_x_m"] for p in points], [p["pitch_y_m"] for p in points],
            [p["col0"] for p in points], [p["row0"] for p in points],
            [p["x0_m"] for p in points], [p["y0_m"] for p in points],
        )
    else:  # pragma: no cover — validate_record가 이미 걸러냄
        raise ValueError(f"알 수 없는 coord_kind: {kind!r}")
    return normalize.to_canonical_coords(coords, notch_dir, kind)


def _convert_value(value: Optional[float], unit: str, radius_m: Optional[float]):
    """단일 측정값을 정준 단위로 변환한다. value=None이면 (None, None)."""
    if value is None:
        return None, None
    if unit in normalize._SCALAR_FACTORS:
        cv = normalize.to_canonical_units(value, unit)
        return float(cv.value), cv.canonical_unit
    if unit == "rpm":
        cv = normalize.to_canonical_units(value, unit, radius_m=radius_m)
        return float(cv.value), cv.canonical_unit
    if unit in _CANONICAL_UNITS:
        return float(value), unit
    # validate_record가 스키마 enum으로 이미 걸렀어야 하는 경로 — 방어적 실패.
    raise ValueError(f"지원하지 않는 단위: {unit!r} (스키마 검증을 우회했는가?)")


def ingest_record(record: dict, *, outlier_method: str = "mad",
                   outlier_k: Optional[float] = None) -> IngestResult:
    """스키마 검증 → 정준 좌표/단위 변환 → 엣지제외/이상치 플래그 → tidy 테이블.

    스키마 위반은 여기서 거부한다(ValueError) — normalize.to_canonical_units 가
    모르는 단위로 죽기 전에, 알려진 단위 집합인지부터 validate_record 에서 먼저 본다.
    """
    schema = load_schema()
    errors = validate_record(record, schema)
    if errors:
        raise ValueError("스키마 검증 실패:\n" + "\n".join(errors))

    points = record["points"]
    n_rows = len(points)
    cc = _canonical_coords(record)
    x_m = np.asarray(cc.x_m, float)
    y_m = np.asarray(cc.y_m, float)
    r_mm = np.hypot(x_m, y_m) * 1000.0

    ee = normalize.apply_edge_exclusion(r_mm, record["edge_exclusion_mm"], record["wafer_diameter_mm"])

    value_raw: List[Optional[float]] = []
    unit_raw: List[str] = []
    value_canonical: List[Optional[float]] = []
    unit_canonical: List[Optional[str]] = []
    value_missing = np.zeros(n_rows, dtype=bool)
    raw_point_json: List[str] = []

    for i, p in enumerate(points):
        v = p.get("value")
        u = p["unit"]
        radius_m = p.get("radius_m")
        vc, uc = _convert_value(v, u, radius_m)
        value_raw.append(v)
        unit_raw.append(u)
        value_canonical.append(vc)
        unit_canonical.append(uc)
        value_missing[i] = v is None
        raw_point_json.append(json.dumps(p, ensure_ascii=False, sort_keys=True))

    is_missing = value_missing | np.asarray(ee.missing, dtype=bool)

    present_idx = [i for i in range(n_rows) if not value_missing[i]]
    is_outlier = np.zeros(n_rows, dtype=bool)
    outlier_reason: List[Optional[str]] = [None] * n_rows
    used_k = outlier_k
    if present_idx:
        present_vals = [value_canonical[i] for i in present_idx]
        flags = normalize.flag_outliers(present_vals, method=outlier_method, k=outlier_k)
        used_k = flags.k
        for j, i in enumerate(present_idx):
            is_outlier[i] = bool(flags.is_outlier[j])
            outlier_reason[i] = flags.reason[j]

    n_excluded = int(np.sum(ee.excluded))
    n_missing = int(np.sum(is_missing))
    n_outliers = int(np.sum(is_outlier))
    schema_version = schema.get("version", "unknown")

    provenance = {
        "schema_version": schema_version,
        "wafer_id": record["wafer_id"],
        "wafer_diameter_mm": record["wafer_diameter_mm"],
        "notch_direction": record["notch_direction"],
        "edge_exclusion_mm": record["edge_exclusion_mm"],
        "coord_kind": record["coord_kind"],
        "series_id": record.get("series_id"),
        "notes": record.get("notes"),
        "outlier_method": outlier_method,
        "outlier_k": used_k,
        "raw_record": record,
    }

    table = pa.table({
        "row_index": pa.array(list(range(n_rows)), type=pa.int64()),
        "wafer_id": pa.array([record["wafer_id"]] * n_rows, type=pa.string()),
        "series_id": pa.array([record.get("series_id")] * n_rows, type=pa.string()),
        "x_m": pa.array(x_m, type=pa.float64()),
        "y_m": pa.array(y_m, type=pa.float64()),
        "r_mm": pa.array(r_mm, type=pa.float64()),
        "value_raw": pa.array(value_raw, type=pa.float64()),
        "unit_raw": pa.array(unit_raw, type=pa.string()),
        "value_canonical": pa.array(value_canonical, type=pa.float64()),
        "unit_canonical": pa.array(unit_canonical, type=pa.string()),
        "is_excluded": pa.array(ee.excluded, type=pa.bool_()),
        "is_missing": pa.array(is_missing, type=pa.bool_()),
        "is_outlier": pa.array(is_outlier, type=pa.bool_()),
        "outlier_reason": pa.array(outlier_reason, type=pa.string()),
        "raw_point_json": pa.array(raw_point_json, type=pa.string()),
    })
    meta = {
        "n_rows": n_rows, "n_excluded": n_excluded, "n_missing": n_missing,
        "n_outliers": n_outliers, "schema_version": schema_version,
        "provenance": provenance,
    }
    table = table.replace_schema_metadata({_PROVENANCE_KEY: json.dumps(meta, ensure_ascii=False)})

    return IngestResult(
        table=table, n_rows=n_rows, n_excluded=n_excluded, n_missing=n_missing,
        n_outliers=n_outliers, schema_version=schema_version, provenance=provenance,
    )


def write_parquet(result: IngestResult, path) -> pathlib.Path:
    p = pathlib.Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    pq.write_table(result.table, str(p))
    return p


def read_parquet(path) -> "pa.Table":
    return pq.read_table(str(path))
