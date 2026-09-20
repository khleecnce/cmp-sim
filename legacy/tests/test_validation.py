"""실측 검증 도구 계약 — 잘못된 판정을 내면 여기서 걸린다.

이 테스트들이 지키는 것: 검증기가 "맞았다"고 거짓말하지 않을 것.
"""
import csv
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))


def _write_csv(path, rows, header):
    with open(path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(rows)


@pytest.fixture
def synth(tmp_path, monkeypatch):
    """엔진 출력으로 합성 실측을 만든다 — 정답을 아는 상태에서 판정을 검사."""
    import sim.models  # noqa: F401
    from sim.engine import Recipe, simulate
    import ingest_measurement as ing
    import validate_model as val

    monkeypatch.setattr(ing, "PARSED", tmp_path)
    monkeypatch.setattr(val, "PARSED", tmp_path)

    rec = Recipe(pack="oxide_silica", pressure_psi=3.0, rpm_wafer=60,
                 rpm_platen=55, time_s=60, n_points=49)
    res = simulate(rec, model="tier2.gw_physical_kp")
    return {"tmp": tmp_path, "r_mm": res.radius_m * 1000,
            "mrr": res.mrr_nm_per_min, "ing": ing, "val": val}


def _make_run(s, name, values):
    rows = [[i, round(r, 2), 1000.0, round(1000 - v, 4), 3.0, 60, 55, 60, "oxide"]
            for i, (r, v) in enumerate(zip(s["r_mm"], values), 1)]
    p = s["tmp"] / f"{name}.csv"
    _write_csv(p, rows, ["point", "반경", "pre", "post", "압력",
                         "rpm_wafer", "rpm_platen", "시간", "막질"])
    return s["ing"].ingest(p, name)


def test_ingest_maps_korean_and_english_columns(synth):
    r = _make_run(synth, "t1", synth["mrr"])
    cm = r["column_mapping"]
    assert cm.get("radius_mm") == "반경"
    assert cm.get("thickness_pre_nm") == "pre"
    assert r["conditions"]["pressure_psi"] == 3.0
    assert r["conditions"]["time_s"] == 60.0
    assert r["comparable"], r["blockers"]


def test_ingest_blocks_when_conditions_missing(synth, tmp_path):
    """압력·시간이 없으면 '비교 가능'이라고 말하면 안 된다."""
    p = tmp_path / "bad.csv"
    _write_csv(p, [[i, 1000 - v] for i, v in enumerate(synth["mrr"], 1)],
               ["no", "두께"])
    r = synth["ing"].ingest(p, "bad")
    assert not r["comparable"]
    assert any("압력" in b for b in r["blockers"])
    assert any("시간" in b for b in r["blockers"])


def test_ingest_derives_mrr_from_pre_post_and_time(synth):
    r = _make_run(synth, "t2", synth["mrr"])
    got = np.array([p["mrr_nm_min"] for p in r["points"]])
    assert np.allclose(got, synth["mrr"], atol=1e-3)


def test_level_error_detected_and_kp_recovered(synth):
    """절대값만 1.4배 다르면 Kp 역산이 그 배율을 찾아야 한다."""
    _make_run(synth, "lvl", synth["mrr"] * 1.4)
    run = synth["val"].load_run("lvl")
    r = synth["val"].scan_kp(run, "oxide_silica", "tier2.gw_physical_kp")
    assert 1.35 < r["factor"] < 1.45, f"Kp 배율 {r['factor']}"
    assert abs(r["after_fit"]["level"]["bias_pct"]) < 1.0


def test_shape_mismatch_not_excused_by_low_rmse(synth):
    """시뮬이 반경 변동을 거의 못 만드는데 '일치'라고 하면 안 된다.

    2026-09-06 실제 버그: 실측 진폭 12.1% vs 시뮬 0.10%인데 RMSE가 3.4%라
    '대체로 일치'로 판정했다. 평탄한 예측이 RMSE에서 유리해지는 함정.
    """
    edge = 1 + 0.12 * (synth["r_mm"] / synth["r_mm"].max()) ** 3
    _make_run(synth, "shape", synth["mrr"] * edge / edge.mean())
    run = synth["val"].load_run("shape")
    c = synth["val"].compare(run, "oxide_silica", "tier2.gw_physical_kp")
    assert abs(c["level"]["bias_pct"]) < 5, "절대값은 맞아야 한다"
    assert "불일치" in c["shape"]["verdict"], c["shape"]["verdict"]
    assert c["shape"]["amplitude_ratio"] < 0.5


def test_perfect_match_is_recognized(synth):
    """엔진 출력을 그대로 넣으면 절대값·형상 모두 일치해야 한다(자기검증)."""
    _make_run(synth, "same", synth["mrr"])
    run = synth["val"].load_run("same")
    c = synth["val"].compare(run, "oxide_silica", "tier2.gw_physical_kp")
    assert abs(c["level"]["bias_pct"]) < 0.5
    assert "불일치" not in c["shape"]["verdict"]


def test_customer_data_never_committed():
    """실측 데이터가 저장소에 들어가면 안 된다."""
    gi = (ROOT / ".gitignore").read_text()
    assert "data/customer/" in gi
    tracked = subprocess.run(
        ["git", "ls-files", "data/customer/"], cwd=ROOT,
        capture_output=True, text=True).stdout.split()
    assert all(f.endswith("README.md") for f in tracked), \
        f"실측 데이터가 커밋되어 있다: {tracked}"
