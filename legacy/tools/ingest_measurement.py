#!/usr/bin/env python3
"""실측 데이터 수집기 — CSV/XLSX/JSON을 읽어 표준 형식으로 검증·저장한다.

  python3 tools/ingest_measurement.py <파일> --run-id run01
  python3 tools/ingest_measurement.py --schema        # 어떤 컬럼을 받나
  python3 tools/ingest_measurement.py <파일> --peek   # 저장 없이 구조만 확인

설계 원칙 — **모르는 것을 추정해 채우지 않는다.**
컬럼 이름이 안 맞으면 무엇이 있고 무엇이 없는지 말한다. 조건(압력·회전수·시간)이
없으면 "이 데이터로는 시뮬레이션 비교가 불가능하다"고 명시한다. 억지로 매칭해서
그럴듯한 비교 리포트를 내는 것이 최악이다.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "customer" / "raw"
PARSED = ROOT / "data" / "customer" / "parsed"

# 컬럼 별칭 — 실무 파일이 제각각이라 넓게 받는다
ALIASES = {
    "radius_mm": ["radius", "r", "반경", "radius_mm", "r_mm", "위치", "position",
                  "반경mm", "radiusmm", "반경(mm)", "r(mm)"],
    "x_mm": ["x", "x_mm", "x축", "xpos"],
    "y_mm": ["y", "y_mm", "y축", "ypos"],
    "point": ["point", "pt", "site", "no", "번호", "포인트", "측정점", "index"],
    "thickness_pre_nm": ["pre", "pre_nm", "before", "initial", "전", "초기두께",
                         "thickness_pre", "pre_thickness", "t0"],
    "thickness_post_nm": ["post", "post_nm", "after", "final", "후", "잔막",
                          "thickness_post", "post_thickness", "t1", "thickness"],
    "removed_nm": ["removed", "removal", "제거량", "removed_nm", "delta", "diff"],
    "mrr_nm_min": ["mrr", "rr", "removal_rate", "제거율", "mrr_nm_min", "rate"],
}

# 공정 조건 별칭
COND_ALIASES = {
    "pressure_psi": ["pressure", "psi", "압력", "down_force", "downforce", "df"],
    "rpm_wafer": ["rpm_wafer", "head_rpm", "carrier_rpm", "웨이퍼rpm", "head"],
    "rpm_platen": ["rpm_platen", "platen_rpm", "table_rpm", "플래튼rpm", "platen"],
    "time_s": ["time", "time_s", "polish_time", "시간", "sec", "duration"],
    "slurry": ["slurry", "슬러리", "slurry_name"],
    "flow_ml_min": ["flow", "flow_rate", "유량", "flow_ml_min"],
    "pad": ["pad", "패드", "pad_type"],
    "film": ["film", "막질", "material", "layer"],
    "wafer_diameter_mm": ["wafer_diameter", "diameter", "직경", "size"],
    "temperature_c": ["temp", "temperature", "온도", "temperature_c"],
}


def _norm(s: str) -> str:
    return re.sub(r"[\s_\-\(\)\[\]/]", "", str(s)).lower()


def map_columns(cols: List[str], aliases: Dict[str, List[str]]) -> Dict[str, str]:
    """실제 컬럼 → 표준 키. 애매하면 매핑하지 않는다."""
    out = {}
    norm_cols = {_norm(c): c for c in cols}
    for std, alts in aliases.items():
        for a in [std] + alts:
            n = _norm(a)
            if n in norm_cols:
                out[std] = norm_cols[n]
                break
        else:
            # 부분일치는 유일할 때만 (모호하면 포기 — 잘못 매칭이 더 나쁘다)
            hits = [c for n, c in norm_cols.items()
                    if any(_norm(a) in n for a in [std] + alts) and c not in out.values()]
            if len(hits) == 1:
                out[std] = hits[0]
    return out


def read_table(path: Path) -> tuple:
    """(rows: List[dict], columns: List[str], meta: dict)"""
    suf = path.suffix.lower()
    if suf in (".csv", ".txt", ".tsv"):
        import csv
        delim = "\t" if suf == ".tsv" else None
        with open(path, encoding="utf-8-sig", errors="replace") as f:
            sample = f.read(4096)
            f.seek(0)
            if delim is None:
                try:
                    delim = csv.Sniffer().sniff(sample, delimiters=",;\t").delimiter
                except Exception:
                    delim = ","
            rd = csv.DictReader(f, delimiter=delim)
            rows = [dict(r) for r in rd]
            cols = list(rd.fieldnames or [])
        return rows, cols, {"format": "csv", "delimiter": delim}
    if suf in (".xlsx", ".xls"):
        try:
            import openpyxl
        except ImportError:
            raise SystemExit("XLSX를 읽으려면: .venv/bin/pip install openpyxl")
        wb = openpyxl.load_workbook(path, data_only=True)
        ws = wb.active
        if ws is None:
            raise SystemExit("활성 시트가 없다")
        data = list(ws.iter_rows(values_only=True))
        if not data:
            return [], [], {"format": "xlsx", "sheet": ws.title}
        # 헤더 행 추정: 문자열이 가장 많은 첫 5행 중
        hdr_i = max(range(min(5, len(data))),
                    key=lambda i: sum(1 for v in data[i] if isinstance(v, str)))
        cols = [str(c) if c is not None else f"col{j}"
                for j, c in enumerate(data[hdr_i])]
        rows = [dict(zip(cols, r)) for r in data[hdr_i + 1:]
                if any(v is not None for v in r)]
        return rows, cols, {"format": "xlsx", "sheet": ws.title,
                            "header_row": hdr_i + 1, "sheets": wb.sheetnames}
    if suf == ".json":
        d = json.loads(path.read_text())
        rows = d if isinstance(d, list) else d.get("rows", [])
        cols = list(rows[0].keys()) if rows else []
        return rows, cols, {"format": "json"}
    raise SystemExit(f"지원하지 않는 형식: {suf} (csv/tsv/xlsx/json)")


def _num(v) -> Optional[float]:
    if v is None or v == "":
        return None
    try:
        return float(str(v).replace(",", "").strip())
    except ValueError:
        return None


def extract_conditions(rows: List[dict], cols: List[str]) -> Dict[str, Any]:
    """공정 조건 추출 — 컬럼에 있거나, 모든 행이 같은 값이면 조건으로 본다."""
    cm = map_columns(cols, COND_ALIASES)
    out = {}
    for std, col in cm.items():
        vals = {r.get(col) for r in rows if r.get(col) not in (None, "")}
        if len(vals) == 1:
            v = vals.pop()
            out[std] = _num(v) if _num(v) is not None else str(v)
    return out


def ingest(path: Path, run_id: str, peek: bool = False) -> Dict[str, Any]:
    rows, cols, meta = read_table(path)
    if not rows:
        raise SystemExit("데이터 행이 없다")

    cm = map_columns(cols, ALIASES)
    cond = extract_conditions(rows, cols)

    # 측정값 추출
    pts = []
    for r in rows:
        p = {}
        for std, col in cm.items():
            v = _num(r.get(col))
            if v is not None:
                p[std] = v
        if p:
            pts.append(p)

    # 파생: pre/post → removed
    for p in pts:
        if "removed_nm" not in p and "thickness_pre_nm" in p and "thickness_post_nm" in p:
            p["removed_nm"] = p["thickness_pre_nm"] - p["thickness_post_nm"]
    t = cond.get("time_s")
    if t:
        for p in pts:
            if "mrr_nm_min" not in p and "removed_nm" in p:
                p["mrr_nm_min"] = p["removed_nm"] / (float(t) / 60.0)

    # 무엇이 되고 무엇이 안 되는지 — 정직하게
    blockers, warns = [], []
    has_pos = any("radius_mm" in p for p in pts) or \
        all(k in cm for k in ("x_mm", "y_mm"))
    has_val = any(k in p for p in pts for k in
                  ("removed_nm", "mrr_nm_min", "thickness_post_nm"))
    if not has_val:
        blockers.append("측정값 없음 — 두께(pre/post)·제거량·제거율 중 하나가 필요하다")
    if not has_pos:
        warns.append("위치 정보 없음(반경 또는 x,y) — 균일도 지표는 계산해도 "
                     "반경 프로파일 비교는 불가. 평균값만 비교한다")
    for k, label in (("pressure_psi", "압력"), ("time_s", "시간")):
        if k not in cond:
            blockers.append(f"{label} 없음 — 시뮬레이션 조건을 맞출 수 없다")
    if "rpm_wafer" not in cond or "rpm_platen" not in cond:
        warns.append("회전수 정보 부족 — 팩 기본값으로 대체하면 속도 항이 실제와 다르다")
    if "film" not in cond:
        warns.append("막질 미지정 — 팩을 사람이 골라야 한다")

    unmapped = [c for c in cols if c not in cm.values() and c not in
                extract_conditions(rows, cols) and
                c not in map_columns(cols, COND_ALIASES).values()]

    result = {
        "run_id": run_id,
        "source_file": path.name,
        "ingested_at": datetime.now().isoformat(timespec="seconds"),
        "format": meta,
        "n_points": len(pts),
        "column_mapping": cm,
        "conditions": cond,
        "unmapped_columns": unmapped,
        "blockers": blockers,
        "warnings": warns,
        "comparable": not blockers,
        "points": pts,
    }

    if not peek:
        PARSED.mkdir(parents=True, exist_ok=True)
        out = PARSED / f"{run_id}.json"
        out.write_text(json.dumps(result, ensure_ascii=False, indent=1))
        # 저장소 밖(테스트 tmp 등)일 수 있으므로 relative_to를 강제하지 않는다
        try:
            result["_saved"] = str(out.relative_to(ROOT))
        except ValueError:
            result["_saved"] = str(out)
    return result


def print_report(r: Dict[str, Any]):
    print(f"■ 수집 — {r['source_file']}  (run_id: {r['run_id']})")
    print(f"  형식 {r['format'].get('format')} · 측정점 {r['n_points']}개\n")
    print("  인식한 컬럼")
    for std, col in r["column_mapping"].items():
        print(f"    {std:<20} ← '{col}'")
    if r["unmapped_columns"]:
        print(f"\n  ⚠ 매핑 못 한 컬럼: {', '.join(map(str, r['unmapped_columns'][:12]))}")
        print("    (이름을 바꾸거나 --schema 로 인식되는 이름을 확인하십시오)")
    print("\n  공정 조건")
    if r["conditions"]:
        for k, v in r["conditions"].items():
            print(f"    {k:<20} {v}")
    else:
        print("    (없음)")
    if r["blockers"]:
        print("\n  ✗ 비교 불가 — 다음이 없다:")
        for b in r["blockers"]:
            print(f"    · {b}")
    if r["warnings"]:
        print("\n  ⚠ 주의:")
        for w in r["warnings"]:
            print(f"    · {w}")
    if r.get("_saved"):
        print(f"\n  저장 → {r['_saved']}")
    if r["comparable"]:
        print(f"\n  다음: .venv/bin/python tools/validate_model.py --run-id {r['run_id']}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("file", nargs="?")
    ap.add_argument("--run-id")
    ap.add_argument("--schema", action="store_true")
    ap.add_argument("--peek", action="store_true", help="저장 없이 구조만")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    if a.schema:
        print("■ 인식하는 컬럼 이름 (대소문자·공백·언더바 무시)\n")
        print("  [측정값]")
        for k, v in ALIASES.items():
            print(f"    {k:<20} {', '.join(v[:6])}")
        print("\n  [공정 조건] — 모든 행이 같은 값이면 조건으로 인식")
        for k, v in COND_ALIASES.items():
            print(f"    {k:<20} {', '.join(v[:5])}")
        print("\n  최소 요구: 측정값 1종 + 압력 + 시간")
        print("  없는 항목은 비워도 된다. 추정해서 채우지 않는다.")
        return 0

    if not a.file:
        ap.error("파일 경로 또는 --schema 필요")
    p = Path(a.file)
    if not p.exists():
        p2 = RAW / a.file
        if p2.exists():
            p = p2
        else:
            raise SystemExit(f"파일 없음: {a.file}")
    rid = a.run_id or p.stem
    r = ingest(p, rid, peek=a.peek)
    if a.json:
        r.pop("points", None)
        print(json.dumps(r, ensure_ascii=False, indent=2))
    else:
        print_report(r)
    return 0 if r["comparable"] else 1


if __name__ == "__main__":
    sys.exit(main())
