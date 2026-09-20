"""QA 루프 계약 — 가짜 데이터 탐지·퇴보 게이트가 실제로 잡는지."""
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import qa_loop as Q  # noqa: E402


def _ds(tmp_path, name, vals, read="digitized", source="doi:10.1000/none", extra=""):
    body = f"source: >\n  {source}\nused_for_calibration: false\npack: oxide_silica\n{extra}conditions:\n"
    for i, v in enumerate(vals):
        body += (f"  - label: c{i}\n    pressure_psi: {1+i}\n    rpm_wafer: 60\n    rpm_platen: 60\n"
                 f"    mrr_nm_per_min: {v}\n    read_method: {read}\n")
    p = tmp_path / f"{name}.yaml"
    p.write_text(body, encoding="utf-8")
    return p


def test_f3_arithmetic_sequence_flagged(tmp_path):
    a = Q.audit_dataset(_ds(tmp_path, "x", [100, 140, 180, 220, 260, 300]), {}, {}, {}, {})
    assert any(f.startswith("F3:MRR이 정확한 등차") for f in a["flags"])


def test_f3_not_flagged_for_printed_table_integers(tmp_path):
    """표에서 옮긴 정수 MRR(mo2026 사례)은 정상 — 어림수 검사는 digitized에만."""
    a = Q.audit_dataset(_ds(tmp_path, "x", [11, 94, 18, 20, 125, 43, 50, 57], read="table"), {}, {}, {}, {})
    assert not any(f.startswith("F3") for f in a["flags"])


def test_f1_values_missing_from_source(tmp_path):
    papers = {"TW202115224A.txt": "removal rate 6,204 / 4,084 Å/min and 5,492"}
    p = _ds(tmp_path, "x", [620.4, 408.4, 549.2, 999.9, 888.8], source="TW202115224A")
    a = Q.audit_dataset(p, papers, {}, {}, {})
    # 3/5 found (천단위 쉼표 + ×10 환산), 2/5 missing → 40% < 50% → clean
    assert a["info"]["values_not_in_source"] == "2/5"
    assert not any(f.startswith("F1") for f in a["flags"])
    p2 = _ds(tmp_path, "y", [1.1, 2.2, 3.3, 4.4], source="TW202115224A")
    a2 = Q.audit_dataset(p2, papers, {}, {}, {})
    assert any(f.startswith("F1") for f in a2["flags"])


def test_f5_too_good_digitized(tmp_path):
    p = _ds(tmp_path, "x", [100, 150, 210])
    a = Q.audit_dataset(p, {}, {}, {}, {"x": {"rho": 1.0, "mape": 2.0}})
    assert any(f.startswith("F5") for f in a["flags"])


def test_f4_self_grading(tmp_path):
    p = _ds(tmp_path, "x", [100, 150, 210], source="doi:10.1149/2162-8777/ac3e44")
    packs = {"oxide_silica": {"some_param": {"source": "Li 2021 doi:10.1149/2162-8777/ac3e44"}}}
    a = Q.audit_dataset(p, {}, {}, packs, {})
    assert any(f.startswith("F4") for f in a["flags"])


def test_human_verified_bypasses(tmp_path):
    p = _ds(tmp_path, "x", [100, 140, 180, 220], extra="audit_verified: true\n")
    a = Q.audit_dataset(p, {}, {}, {}, {})
    assert a["verified_by_human"] and a["flags"] == []


def test_gate_detects_regression():
    prev = {"rows": [{"dataset": "a", "significant": True, "rho": 0.9, "p": 0.01}], "mean_rho_significant": 0.9}
    cur = {"rows": [{"dataset": "a", "significant": True, "rho": 0.7, "p": 0.02}], "mean_rho_significant": 0.7}
    assert Q.gate(cur, prev)["status"] == "FAIL"
    cur2 = {"rows": [{"dataset": "a", "significant": False, "rho": 0.9, "p": 0.2}], "mean_rho_significant": None}
    assert Q.gate(cur2, prev)["status"] == "FAIL"
    cur3 = {"rows": [{"dataset": "a", "significant": True, "rho": 0.88, "p": 0.01}], "mean_rho_significant": 0.88}
    assert Q.gate(cur3, prev)["status"] == "PASS"     # 허용오차 안


def test_gate_first_run_passes():
    assert Q.gate({"rows": [], "mean_rho_significant": None}, None)["status"] == "PASS"


def test_quarantine_rules(tmp_path, monkeypatch):
    monkeypatch.setattr(Q, "QUAR", tmp_path / "q.json")
    audits = [
        {"dataset": "hard", "flags": ["F1:x"], "verified_by_human": False},
        {"dataset": "f2only", "flags": ["F2:x"], "verified_by_human": False},
        {"dataset": "f2f3", "flags": ["F2:x", "F3:y"], "verified_by_human": False},
        {"dataset": "clean", "flags": [], "verified_by_human": False},
    ]
    q = Q.update_quarantine(audits)
    assert "hard" in q and "f2f3" in q
    assert "f2only" not in q and "clean" not in q     # 원문 없음만으로는 격리 안 함
