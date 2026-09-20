"""축척 학습곡선의 집계 배제 규칙을 잠근다.

학습곡선은 **절대오차**를 재는 표다. 그런데 `rank_only: true` 로 판정된 계열은
"이 계열에서 절대값은 쓰지 않는다"가 이미 근거와 함께 확정된 것이므로,
그 계열을 절대오차 평균·판정에 넣으면 "축척 학습이 악화한다"는 **거짓 진단**이 나온다
(2026-09-18 실측: liang2026 이 그 이유로 🔴 악화로 잡혀 '계열 분할 필요'를 가리켰는데,
판정#57 이 이미 원인을 "우리 함수형의 정의역 밖 외삽 + 미모델링 촉매 경로"로 종결한
계열이었다 — 분할은 답이 아니었다).

⚠ 이 테스트는 "지금 결과가 좋다"를 확인하는 것이 아니라 **배제 축 3개가 코드에서
사라지지 않는지**를 확인한다. 배제가 하나라도 빠지면 다음 회차의 작업 지시가 오염된다.
"""
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = (ROOT / "tools" / "calibration_curve.py").read_text(encoding="utf-8")


def test_learning_curve_excludes_three_axes():
    """범위밖 · 캘리브레이션 사용분 · 순위전용 셋 다 집계에서 빠져야 한다."""
    assert "if not in_scope or is_calib or rank_only:" in SRC, (
        "집계 배제 조건에서 축이 빠졌다 — in_scope/used_for_calibration/rank_only "
        "셋을 모두 걸러야 절대오차 평균이 의미를 갖는다."
    )


def test_rank_only_is_actually_read_from_result():
    """rank_only 를 BacktestResult 에서 실제로 읽어야 한다(선언만 하고 안 읽으면 무효)."""
    assert 'getattr(r, "rank_only", False)' in SRC, (
        "rank_only 를 백테스트 결과에서 읽지 않으면 배제 조건이 항상 False 가 되어 "
        "조용히 무력화된다."
    )


def test_rank_only_datasets_exist_and_carry_a_ruling():
    """배제가 남용되지 않도록: rank_only 를 선언한 데이터셋은 근거(ruling)를 반드시 가진다.

    근거 없는 rank_only 는 backtest 로더가 무시하지만, 여기서도 잠가 둔다 —
    '절대오차가 나쁘니 rank_only 를 붙인다'가 되는 순간 이 표는 자기 채점이 된다.
    """
    import yaml

    ds_dir = ROOT / "validation" / "datasets"
    declared = []
    for p in sorted(ds_dir.glob("*.yaml")):
        raw = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
        if raw.get("rank_only"):
            declared.append(p.name)
            ruling = str(raw.get("rank_only_ruling", "") or "").strip()
            assert len(ruling) > 80, (  # noqa: PLR2004
                f"{p.name}: rank_only 를 선언했는데 근거(rank_only_ruling)가 없거나 "
                f"너무 짧다({len(ruling)}자). 절대값을 못 쓰는 이유를 적어야 한다."
            )
    assert declared, "rank_only 데이터셋이 하나도 없다 — 이 테스트가 무의미해졌는지 확인하라."
