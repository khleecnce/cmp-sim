"""판정#58 계약 — Cu·W 절대값 BIAS 3건 판정의 회귀 방지.

배경(EVIDENCE-RULES 판정#58, 2026-09-18):
  갭 랭커 최상위 BIAS 3건 중 하나(`us9200180b2_cu_ph_alkaline_sweep`)는 팩 파라미터
  `cu_ph_alkaline_k`를 역산한 바로 그 캘리브레이션 데이터였다 — `used_for_calibration:
  true`인데도 `gaps_bias()`가 걸러내지 않아 자기순환(E6 변종)이 났다. 나머지 둘
  (`us9200180b2_cu_abrasive_series`, `us8070843b2_w_h2o2_series`)은 정의역 외삽으로
  판정해 rank_only 로 절대값만 면제했다. 이 계약이 지키는 것:
    1. `gaps_bias()`는 used_for_calibration 데이터셋을 다시 올리지 않는다
       (판정#55 의 rank_only 스킵과 같은 성격의 필터).
    2. 두 rank_only 데이터셋의 근거 문자열이 근거 없이 비어 있지 않다.
    3. F4 로 격리됐던 두 데이터셋이 audit_verified 로 해제돼 있다.
"""
from __future__ import annotations

import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
for p in (str(ROOT), str(ROOT / "validation")):
    if p not in sys.path:
        sys.path.insert(0, p)

DS = ROOT / "validation" / "datasets"
ALKALINE_SWEEP = DS / "us9200180b2_cu_ph_alkaline_sweep.yaml"
ABRASIVE_SERIES = DS / "us9200180b2_cu_abrasive_series.yaml"
H2O2_SERIES = DS / "us9200180b2_cu_h2o2_series.yaml"
W_H2O2_SERIES = DS / "us8070843b2_w_h2o2_series.yaml"


def test_alkaline_sweep_is_calibration_not_heldout():
    """이 데이터셋은 cu_ph_alkaline_k 의 캘리브레이션 출처다 — held-out으로 재판정하면 순환이다.

    ⚠ 2026-09-19: 팩 이름이 `cu_h2o2_bta` → `cu_alkaline_benzenesulfonic` 으로
    바뀌었다. 이 표(pH 6.2~9.9, 콜로이달 실리카 10 wt%, 벤젠술폰산, **BTA 없음**)의
    조성이 산성·BTA 팩과 달라 알칼리 계를 별도 팩으로 분리했기 때문이다.
    판정#58 이 지키려던 것은 **팩 이름이 아니라 '역산 출처를 held-out 으로 다시
    채점하지 않는다'는 계약**이므로, 이름을 새 팩으로 갱신하되 그 계약(아래
    used_for_calibration 과 gaps_bias 필터)은 그대로 둔다.
    분리 근거: 부모 팩으로 예측하면 obs/pred 퍼짐이 1.06배(형상은 맞고 축척만
    193배 틀림) — 축척만 틀린 것은 정의상 Kp 문제이고 Kp 는 계마다 역산된다.
    """
    raw = yaml.safe_load(ALKALINE_SWEEP.read_text(encoding="utf-8"))
    assert raw.get("used_for_calibration") is True
    assert raw.get("pack") == "cu_alkaline_benzenesulfonic"


def test_gaps_bias_skips_used_for_calibration():
    """갭 랭커가 캘리브레이션 데이터셋을 BIAS 로 다시 올리지 않는다(판정#58)."""
    from tools.accuracy_gaps import gaps_bias
    names = {g.get("dataset") for g in gaps_bias()}
    assert ALKALINE_SWEEP.stem not in names, (
        "used_for_calibration 데이터셋이 BIAS 갭에 다시 올라왔다 — 자기순환(E6) 재발")


def test_gaps_bias_skips_rank_only_targets_of_ruling58():
    """판정#58 이 rank_only 로 면제한 두 데이터셋도 BIAS 에서 빠진다."""
    from tools.accuracy_gaps import gaps_bias
    names = {g.get("dataset") for g in gaps_bias()}
    assert ABRASIVE_SERIES.stem not in names
    assert W_H2O2_SERIES.stem not in names


def test_cu_abrasive_series_ruling_is_substantive():
    raw = yaml.safe_load(ABRASIVE_SERIES.read_text(encoding="utf-8"))
    assert raw.get("rank_only") is True
    ruling = str(raw.get("rank_only_ruling", ""))
    assert len(ruling) > 200, "근거가 한 줄짜리면 판정이 아니라 변명이다"
    for token in ("판정#58", "TABLE 3", "TABLE 4"):
        assert token in ruling, f"근거에 {token} 가 없다"


def test_w_h2o2_series_ruling_is_substantive():
    raw = yaml.safe_load(W_H2O2_SERIES.read_text(encoding="utf-8"))
    assert raw.get("rank_only") is True
    ruling = str(raw.get("rank_only_ruling", ""))
    assert len(ruling) > 200, "근거가 한 줄짜리면 판정이 아니라 변명이다"
    for token in ("판정#58", "고정연마입자", "Preston"):
        assert token in ruling, f"근거에 {token} 가 없다"


def test_ruling_required_still_enforced_for_ruling58_datasets():
    """근거 문자열을 지우면 두 데이터셋 모두 rank_only 가 무시돼야 한다(판정#55 가 만든 계약)."""
    import backtest  # noqa: E402

    for path in (ABRASIVE_SERIES, W_H2O2_SERIES):
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
        raw.pop("rank_only_ruling", None)
        tmp = path.with_suffix(".no_ruling_tmp.yaml")
        try:
            tmp.write_text(yaml.safe_dump(raw, allow_unicode=True), encoding="utf-8")
            r = backtest.run_dataset(tmp)
            assert r.rank_only is False, f"{path.stem}: 근거 없는 rank_only 가 그대로 인정됐다"
        finally:
            tmp.unlink(missing_ok=True)


def test_f4_quarantine_cleared_by_audit_verified():
    """cu_abrasive_series·cu_h2o2_series 는 F4 오탐이 해소돼 감사에서 격리 대상이 아니다.

    ⚠ update_quarantine()은 validation/quarantine.json 에 실제로 쓰기 때문에 여기서
    호출하지 않는다 — audit_dataset() 결과만으로 "격리 조건에 해당하지 않음"을 확인한다.
    """
    import tools.qa_loop as qa_loop

    results = {r["dataset"]: r for r in qa_loop.audit_all({})}
    for stem in (ABRASIVE_SERIES.stem, H2O2_SERIES.stem):
        result = results[stem]
        assert result["verified_by_human"] is True, (
            f"{stem}: audit_verified 가 감사에서 인정되지 않았다")
        assert result["flags"] == []
