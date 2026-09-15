"""런 저장소 (Run Store) — 모든 시뮬레이션 실행과 실측 데이터를 SQLite에 쌓는다.

사용자 지시 (2026-09-08):
  "실행 할때마다 DB에 저장해서 다음 시뮬레이션 데이터 산출에 반영될 수 있게해.
   특히 엑셀이나 다른 포맷 real data 파일을 넣으면 그냥 그대로 빅데이터가
   프로그램에 입력되도록 하고싶어."

두 종류의 레코드를 한 DB에 둔다:
  runs          — 시뮬레이션 실행 (입력 + 출력 + 팩터 + 장비 출력값)
  measurements  — 실측 (엑셀/CSV에서 들어온 것). 컬럼 매핑은 tools/ingest_measurement.py 재사용

⚠ "다음 시뮬레이션에 반영"의 정직한 의미
  실측이 쌓인다고 모델이 저절로 똑똑해지지 않는다. 반영되는 경로는 두 가지뿐이고
  둘 다 **명시적**이다:
   1. 캘리브레이션: 같은 조건의 실측/예측 비를 Kp 보정계수로 쓴다 (`calibration_factor()`).
      절대값(Kp)만 건드리고 형상(물리)은 건드리지 않는다 — 절대값·형상 분리 원칙.
   2. 백테스트: 실측이 validation 데이터셋으로 변환되어 순위 재현을 검사한다.
  조용히 모델을 바꾸는 것은 하지 않는다. 실측이 반영됐으면 결과 notes에 그 사실이 실린다.

⚠ 재직사 데이터 금지 원칙은 여기서도 유효하다. DB 파일은 data/ 아래(.gitignore)에
  두고 절대 커밋하지 않는다. 사용자 개인 소유 장비 데이터는 예외지만 그래도 커밋 금지.
"""
from __future__ import annotations

import json
import sqlite3
import time
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional
import os

ROOT = Path(__file__).resolve().parents[1]
DB_DIR = Path(os.environ["FABSIM_STORE_DIR"]) if os.environ.get("FABSIM_STORE_DIR") else ROOT / "data" / "store"
DB_PATH = DB_DIR / "fabsim.sqlite"

_SCHEMA = """
CREATE TABLE IF NOT EXISTS runs (
  id            TEXT PRIMARY KEY,
  ts            REAL NOT NULL,
  pack          TEXT NOT NULL,
  film          TEXT,
  wafer         TEXT,
  model         TEXT,
  inputs_json   TEXT NOT NULL,   -- Recipe 필드 + pack_overrides (사람이 정한 것 전부)
  mrr_mean      REAL,
  ttv_nm        REAL,
  cv_pct        REAL,
  factors_json  TEXT,            -- 병합 파라미터 10개
  outputs_json  TEXT,            -- 장비 출력값
  summary_json  TEXT NOT NULL,   -- 전체 summary (재현용)
  calibrated_by TEXT             -- 이 런에 적용된 실측 보정 id (없으면 NULL)
);
CREATE INDEX IF NOT EXISTS idx_runs_pack_ts ON runs(pack, ts);

CREATE TABLE IF NOT EXISTS measurements (
  id            TEXT PRIMARY KEY,
  ts            REAL NOT NULL,
  source_file   TEXT NOT NULL,   -- 원본 파일명 (내용은 저장 안 함)
  run_label     TEXT,
  pack_hint     TEXT,            -- 사용자가 지정한 팩 (없으면 NULL)
  conditions_json TEXT NOT NULL, -- 압력·rpm·시간 등 (없으면 {})
  mrr_mean      REAL,            -- 실측 평균 MRR (nm/min), 계산 가능할 때만
  n_points      INTEGER,
  points_json   TEXT NOT NULL,   -- 반경/두께 포인트 원본
  quality_json  TEXT NOT NULL,   -- ingest가 판정한 결측·경고
  note          TEXT
);
CREATE INDEX IF NOT EXISTS idx_meas_ts ON measurements(ts);

CREATE TABLE IF NOT EXISTS imports (
  id            TEXT PRIMARY KEY,
  ts            REAL NOT NULL,
  filename      TEXT NOT NULL,
  n_rows        INTEGER,
  n_measurements INTEGER,
  warnings_json TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS settings (
  key           TEXT PRIMARY KEY,
  value_json    TEXT NOT NULL,
  ts            REAL NOT NULL
);
"""


def get_setting(key: str, default: Any = None) -> Any:
    """UI 설정(팩터 기호 등) — 없으면 default."""
    with _conn() as c:
        r = c.execute("SELECT value_json FROM settings WHERE key=?", (key,)).fetchone()
    return json.loads(r["value_json"]) if r else default


def set_setting(key: str, value: Any) -> None:
    with _conn() as c:
        c.execute("INSERT OR REPLACE INTO settings (key, value_json, ts) VALUES (?,?,?)",
                  (key, _j(value), time.time()))


def _conn() -> sqlite3.Connection:
    DB_DIR.mkdir(parents=True, exist_ok=True)
    c = sqlite3.connect(DB_PATH)
    c.row_factory = sqlite3.Row
    c.executescript(_SCHEMA)
    return c


def _j(x: Any) -> str:
    return json.dumps(x, ensure_ascii=False, default=_default)


def _default(o):
    try:
        import numpy as np
        if isinstance(o, (np.floating, np.integer)):
            return o.item()
        if isinstance(o, np.ndarray):
            return o.tolist()
    except ImportError:
        pass
    if hasattr(o, "to_dict"):
        return o.to_dict()
    return str(o)


# ═══════════════════════════════════════════════ runs

def save_run(summary: Dict[str, Any], inputs: Dict[str, Any],
             calibrated_by: Optional[str] = None) -> str:
    """시뮬레이션 결과 한 건을 저장하고 id를 돌려준다."""
    rid = uuid.uuid4().hex[:12]
    m = summary.get("metrics") or {}
    with _conn() as c:
        c.execute(
            "INSERT INTO runs VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (rid, time.time(), summary.get("pack", ""), summary.get("film"),
             summary.get("wafer"), summary.get("model"), _j(inputs),
             summary.get("mean_mrr_nm_min"),
             m.get("ttv_nm") if isinstance(m, dict) else summary.get("ttv_nm"),
             m.get("cv_pct") if isinstance(m, dict) else summary.get("cv_pct"),
             _j(summary.get("factors")), _j(summary.get("equipment_outputs")),
             _j(summary), calibrated_by))
    return rid


def recent_runs(limit: int = 50, pack: Optional[str] = None) -> List[Dict[str, Any]]:
    with _conn() as c:
        if pack:
            rows = c.execute("SELECT id,ts,pack,film,model,mrr_mean,ttv_nm,cv_pct,"
                             "inputs_json,calibrated_by FROM runs WHERE pack=? "
                             "ORDER BY ts DESC LIMIT ?", (pack, limit)).fetchall()
        else:
            rows = c.execute("SELECT id,ts,pack,film,model,mrr_mean,ttv_nm,cv_pct,"
                             "inputs_json,calibrated_by FROM runs "
                             "ORDER BY ts DESC LIMIT ?", (limit,)).fetchall()
    out = []
    for r in rows:
        d = dict(r)
        d["inputs"] = json.loads(d.pop("inputs_json") or "{}")
        out.append(d)
    return out


def get_run(rid: str) -> Optional[Dict[str, Any]]:
    with _conn() as c:
        r = c.execute("SELECT * FROM runs WHERE id=?", (rid,)).fetchone()
    if not r:
        return None
    d = dict(r)
    for k in ("inputs_json", "factors_json", "outputs_json", "summary_json"):
        d[k[:-5]] = json.loads(d.pop(k) or "null")
    return d


# ═══════════════════════════════════════════════ measurements

def save_measurement(source_file: str, conditions: Dict[str, Any],
                     points: List[Dict[str, Any]], quality: Dict[str, Any],
                     run_label: Optional[str] = None,
                     pack_hint: Optional[str] = None,
                     note: Optional[str] = None) -> str:
    mid = uuid.uuid4().hex[:12]
    mrr = _mean_mrr(points, conditions)
    with _conn() as c:
        c.execute(
            "INSERT INTO measurements VALUES (?,?,?,?,?,?,?,?,?,?,?)",
            (mid, time.time(), source_file, run_label, pack_hint, _j(conditions),
             mrr, len(points), _j(points), _j(quality), note))
    return mid


def _mean_mrr(points: List[Dict[str, Any]], cond: Dict[str, Any]) -> Optional[float]:
    """포인트에서 평균 MRR을 낼 수 있으면 낸다. 못 내면 None — 지어내지 않는다."""
    vals = [p.get("mrr_nm_min") for p in points if p.get("mrr_nm_min") is not None]
    if vals:
        return float(sum(vals) / len(vals))
    rem = [p.get("removed_nm") for p in points if p.get("removed_nm") is not None]
    if not rem:
        pre = [p.get("thickness_pre_nm") for p in points]
        post = [p.get("thickness_post_nm") for p in points]
        if all(a is not None and b is not None for a, b in zip(pre, post)) and pre:
            rem = [a - b for a, b in zip(pre, post)]
    t = cond.get("time_s")
    if rem and t:
        return float(sum(rem) / len(rem) / (float(t) / 60.0))
    return None


def list_measurements(limit: int = 100) -> List[Dict[str, Any]]:
    with _conn() as c:
        rows = c.execute("SELECT id,ts,source_file,run_label,pack_hint,mrr_mean,"
                         "n_points,conditions_json,quality_json,note FROM measurements "
                         "ORDER BY ts DESC LIMIT ?", (limit,)).fetchall()
    out = []
    for r in rows:
        d = dict(r)
        d["conditions"] = json.loads(d.pop("conditions_json") or "{}")
        d["quality"] = json.loads(d.pop("quality_json") or "{}")
        out.append(d)
    return out


def get_measurement(mid: str) -> Optional[Dict[str, Any]]:
    with _conn() as c:
        r = c.execute("SELECT * FROM measurements WHERE id=?", (mid,)).fetchone()
    if not r:
        return None
    d = dict(r)
    for k in ("conditions_json", "points_json", "quality_json"):
        d[k[:-5]] = json.loads(d.pop(k) or "null")
    return d


def save_import(filename: str, n_rows: int, n_meas: int, warnings: List[str]) -> str:
    iid = uuid.uuid4().hex[:12]
    with _conn() as c:
        c.execute("INSERT INTO imports VALUES (?,?,?,?,?,?)",
                  (iid, time.time(), filename, n_rows, n_meas, _j(warnings)))
    return iid


# ═══════════════════════════════════════════════ 실측 → 시뮬레이션 반영

@dataclass
class Calibration:
    """실측이 시뮬레이션에 반영되는 **유일한 통로**.

    같은 팩·비슷한 조건의 실측 MRR과 모델 예측 MRR의 비(중앙값)를 Kp 보정계수로
    쓴다. 형상(반경 프로파일·팩터)은 건드리지 않는다 — 절대값과 형상을 분리해
    보고해야 진단이 된다(절대값은 상수 하나로 고쳐지고 형상은 모델을 고쳐야 한다).
    """
    factor: float                # Kp에 곱할 배수 (1.0 = 보정 없음)
    n_used: int                  # 근거가 된 실측 건수
    ids: List[str]               # 어떤 실측을 썼나
    spread: Optional[float]      # 비의 분산(IQR/중앙값) — 크면 조건이 섞인 것
    note: str

    def to_dict(self) -> Dict[str, Any]:
        return {"factor": self.factor, "n_used": self.n_used, "ids": self.ids,
                "spread": self.spread, "note": self.note}


def calibration_factor(pack: str, predict_mrr, conditions_match=None,
                       min_n: int = 3) -> Calibration:
    """DB의 실측으로 이 팩의 Kp 보정계수를 낸다.

    predict_mrr(conditions: dict) -> float  : 그 조건에서 모델이 내는 평균 MRR
    conditions_match(cond) -> bool          : 어떤 실측을 쓸지 (None이면 팩 힌트 일치만)

    ⚠ 실측이 min_n 미만이면 보정하지 않는다(factor=1.0). 실측 한두 건으로 Kp를
      흔들면 그게 노이즈인지 신호인지 구분이 안 된다.
    """
    rows = [m for m in list_measurements(limit=1000)
            if m.get("mrr_mean") is not None
            and (m.get("pack_hint") == pack)
            and (conditions_match is None or conditions_match(m["conditions"]))]
    if len(rows) < min_n:
        return Calibration(1.0, len(rows), [], None,
                           f"실측 {len(rows)}건 < 최소 {min_n}건 — 보정하지 않음. "
                           "실측이 더 쌓여야 Kp를 흔들 근거가 된다.")
    ratios, ids = [], []
    for m in rows:
        try:
            pred = float(predict_mrr(m["conditions"]))
        except Exception:
            continue
        if pred > 0:
            ratios.append(float(m["mrr_mean"]) / pred)
            ids.append(m["id"])
    if len(ratios) < min_n:
        return Calibration(1.0, len(ratios), ids, None,
                           "조건을 모델에 넣을 수 없는 실측이 많아 보정하지 않음.")
    ratios.sort()
    med = ratios[len(ratios) // 2]
    q1, q3 = ratios[len(ratios) // 4], ratios[(3 * len(ratios)) // 4]
    spread = (q3 - q1) / med if med else None
    note = (f"실측 {len(ratios)}건 중앙값 비 {med:.3f} → Kp ×{med:.3f}. "
            f"산포 IQR/중앙값={spread:.2f}." if spread is not None else "")
    if spread is not None and spread > 0.5:
        note += (" ⚠ 산포가 크다 — 서로 다른 조건(패드 수명·슬러리 로트)이 섞였을 "
                 "가능성. 조건별로 나눠 보정하라.")
    return Calibration(med, len(ratios), ids, spread, note)


def stats() -> Dict[str, Any]:
    with _conn() as c:
        nr = c.execute("SELECT COUNT(*) FROM runs").fetchone()[0]
        nm = c.execute("SELECT COUNT(*) FROM measurements").fetchone()[0]
        ni = c.execute("SELECT COUNT(*) FROM imports").fetchone()[0]
        by_pack = {r[0]: r[1] for r in
                   c.execute("SELECT pack, COUNT(*) FROM runs GROUP BY pack")}
        mp = {r[0]: r[1] for r in
              c.execute("SELECT pack_hint, COUNT(*) FROM measurements GROUP BY pack_hint")}
    return {"runs": nr, "measurements": nm, "imports": ni,
            "runs_by_pack": by_pack, "measurements_by_pack": mp,
            "db_path": str(DB_PATH)}
