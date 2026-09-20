"""rank_only(절대값 순위전용) 플래그의 계약 — 근거 없는 면제를 막는다.

왜 테스트가 필요한가 (2026-09-16, EVIDENCE-RULES 판정#55):
  `rank_only: true` 는 "백테스트의 계통편향 판정에서 이 데이터셋을 뺀다"는
  강한 스위치다. 근거 없이 켤 수 있으면 그 순간 백테스트는 모델 실력이 아니라
  **선별의 결과**가 된다(tools/outlier_rules.py 서문과 같은 위험).

  그래서 두 가지를 코드로 고정한다:
    1. `rank_only_ruling`(근거 문자열)이 없으면 플래그는 **무시된다**.
    2. 플래그가 켜져도 **순위 지표(ρ·τ·p)는 전혀 바뀌지 않는다** —
       빼는 것은 데이터가 아니라 절대값 판정이다.
"""
from __future__ import annotations

import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
for p in (str(ROOT), str(ROOT / "validation")):
    if p not in sys.path:
        sys.path.insert(0, p)

import backtest  # noqa: E402

DS = ROOT / "validation" / "datasets"
ENTEGRIS = DS / "entegris2022_us20220315802a1_sic_alumina_conc.yaml"


def test_ruling_required_for_rank_only(tmp_path):
    """근거 문자열이 없으면 플래그가 무시되고 경고가 남는다."""
    raw = yaml.safe_load(ENTEGRIS.read_text(encoding="utf-8"))
    raw["rank_only"] = True
    raw.pop("rank_only_ruling", None)
    f = tmp_path / "no_ruling.yaml"
    f.write_text(yaml.safe_dump(raw, allow_unicode=True), encoding="utf-8")

    r = backtest.run_dataset(f)
    assert r.rank_only is False, "근거 없는 rank_only 가 그대로 인정됐다"
    assert any("근거 없는 절대값 면제" in n for n in r.notes)


def test_rank_only_does_not_touch_ranking(tmp_path):
    """플래그를 껐다 켜도 순위 지표는 비트 단위로 같아야 한다."""
    raw = yaml.safe_load(ENTEGRIS.read_text(encoding="utf-8"))
    assert raw.get("rank_only") is True, "이 테스트는 판정#55 대상 데이터셋을 전제한다"

    off = dict(raw)
    off["rank_only"] = False
    f = tmp_path / "off.yaml"
    f.write_text(yaml.safe_dump(off, allow_unicode=True), encoding="utf-8")

    a = backtest.run_dataset(ENTEGRIS)
    b = backtest.run_dataset(f)

    assert a.rank_only is True and b.rank_only is False
    assert a.spearman == b.spearman
    assert a.kendall == b.kendall
    assert a.p_value == b.p_value
    assert a.n == b.n
    # 절대값 관련 수치도 계산 자체는 그대로 남는다(가리는 게 아니라 판정에서만 뺀다)
    assert a.scale_factor == b.scale_factor
    assert a.mape_pct == b.mape_pct


def test_entegris_ruling_is_substantive():
    """판정#55 의 근거가 데이터셋에 실제로 적혀 있는가."""
    raw = yaml.safe_load(ENTEGRIS.read_text(encoding="utf-8"))
    ruling = str(raw.get("rank_only_ruling", ""))
    assert len(ruling) > 200, "근거가 한 줄짜리면 판정이 아니라 변명이다"
    for token in ("Preston", "Gong", "knowledge/cmp/"):
        assert token in ruling, f"근거에 {token} 가 없다"
    assert raw.get("used_for_calibration") is False


def test_bias_gap_skips_rank_only():
    """갭 랭커가 rank_only 데이터셋을 BIAS 로 다시 올리지 않는다."""
    from tools.accuracy_gaps import gaps_bias
    names = {g.get("dataset") for g in gaps_bias()}
    assert ENTEGRIS.stem not in names, (
        "종결 판정이 있는 데이터셋이 갭 랭킹에 다시 올라왔다 — "
        "크론이 매 회차 같은 판정을 뒤집으려 든다")
