"""C4 held-out ρ 구조적 상한(rank ceiling) 회귀 — 판정#91.

⚠ 절대값을 고정한다(상대적 성질만 검사하지 않는다). 과거에 21,600km 버그가
  "0보다 크다"류의 상대 검사만으로 통과한 전례가 있다(이 프로젝트 관례).
  tw202115224a의 ρ_ceiling과 그룹 수는 특정 숫자로 고정한다.
"""
import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "validation"))

import backtest  # noqa: E402
from tools.rank_ceiling import (  # noqa: E402
    compute_all, optimal_group_order_rho, brute_force_group_order_rho,
    n_groups, group_by_prediction,
)

DATASET_DIR = ROOT / "validation" / "datasets"


def _dataset_result(stem):
    for r in backtest.run_all():
        if r.dataset == stem:
            return r
    raise AssertionError(f"{stem} not found in backtest.run_all()")


# ═══════════════ tw202115224a — 절대값 고정 (근사 12그룹이 아니라 실제 2그룹) ═══════════════

def test_tw202115224a_ceiling_absolute_value_and_group_count():
    """실제 backtest._recipe_from + simulate 경로로 그룹을 지으면 12개가 아니라
    **2개**다 — abrasive_size_exponent=0.0(판정#1) 때문에 abrasive_size_nm 채널이
    현재 완전히 무력하고, 조건에 걸쳐 유일하게 살아 있는 입력은 pressure_psi뿐이다.
    이 2그룹의 최적 배치에서 나오는 ρ_ceiling은 **현재 실제 ρ와 정확히 같다**
    (현재 순서가 이미 최적이라 달성률 100%) — 판정#91의 핵심 발견.
    """
    r = _dataset_result("tw202115224a_cu_abrasive_size_pressure")
    g = n_groups(r.predicted)
    assert g == 2, f"고유 입력 그룹 수가 2가 아니다: {g}"
    ceil_rho = optimal_group_order_rho(r.predicted, r.observed)
    assert ceil_rho == pytest.approx(0.71745, rel=1e-3)
    # 현재 실제 ρ가 상한과 사실상 같다(이미 최적 순서) — 개선 여지가 없다는 뜻
    assert r.spearman == pytest.approx(ceil_rho, rel=1e-6)


def test_tw202115224a_ceiling_p_significant():
    r = _dataset_result("tw202115224a_cu_abrasive_size_pressure")
    ceil_rho = optimal_group_order_rho(r.predicted, r.observed)
    p = backtest.perm_p_value(ceil_rho, r.n)
    assert p == pytest.approx(0.0007, abs=2e-4)


# ═══════════════ 폐형식 == 전수 순열 (G≤8) ═══════════════

def test_closed_form_matches_brute_force_permutation_search():
    """폐형식(그룹을 관측 평균순위로 정렬)이 최적이라는 주장을 G≤8인 실제
    데이터셋들에서 전수 순열 탐색과 대조해 기계로 확인한다."""
    checked = 0
    for r in backtest.run_all():
        if r.n < 3 or not r.predicted or np.isnan(r.spearman):
            continue
        g = n_groups(r.predicted)
        if g > 8:
            continue
        closed = optimal_group_order_rho(r.predicted, r.observed)
        brute = brute_force_group_order_rho(r.predicted, r.observed)
        assert closed == pytest.approx(brute, abs=1e-9), (
            f"{r.dataset}: 폐형식={closed} != 전수탐색={brute}")
        checked += 1
    assert checked >= 5, f"G≤8 데이터셋이 너무 적어 대조가 약하다: {checked}건"


def test_closed_form_matches_brute_force_synthetic_cases():
    """실제 데이터셋 외에 합성 사례로도 폐형식=전수탐색을 확인한다(그룹 크기가
    고르지 않은 경우 포함)."""
    cases = [
        ([1.0, 1.0, 2.0, 2.0, 3.0], [5.0, 1.0, 9.0, 2.0, 7.0]),
        ([1.0, 1.0, 1.0, 2.0, 3.0, 3.0], [4.0, 9.0, 1.0, 3.0, 8.0, 2.0]),
        ([1.0, 2.0, 2.0, 2.0, 3.0], [10.0, 3.0, 6.0, 1.0, 8.0]),
    ]
    for pred, obs in cases:
        closed = optimal_group_order_rho(pred, obs)
        brute = brute_force_group_order_rho(pred, obs)
        assert closed == pytest.approx(brute, abs=1e-9), (pred, obs, closed, brute)


# ═══════════════ 모든 입력이 고유하면 상한 = 1.0 ═══════════════

def test_all_unique_inputs_ceiling_is_exactly_one():
    """⚠ '입력이 고유하면 상한 1.0'은 **관측값도 전부 고유할 때만** 성립한다.
    입력(예측)이 전부 고유해도(그룹수==n) 관측 쪽에 동점이 있으면, Spearman의
    동점 평균순위를 자유(비동점) 예측으로는 정확히 재현할 수 없어 상한이 1.0
    미만이 된다 — 실제로 gong2024_4hsic_alumina_kmno4_L25(n=25, 관측 고유값 12개)가
    그룹수==n=25인데도 상한 0.9909로 나와 이 구분을 직접 드러냈다. 그래서 이
    테스트는 '그룹수==n'뿐 아니라 '관측값도 전부 고유'인 데이터셋만 골라 검사한다.
    """
    found = False
    for r in backtest.run_all():
        if r.n < 3 or not r.predicted or np.isnan(r.spearman):
            continue
        obs_unique = len(set(round(float(o), 9) for o in r.observed))
        if n_groups(r.predicted) == r.n and obs_unique == r.n:
            ceil_rho = optimal_group_order_rho(r.predicted, r.observed)
            assert ceil_rho == pytest.approx(1.0, abs=1e-9), (
                f"{r.dataset}: 예측·관측 모두 고유한데 상한이 1.0이 아니다: {ceil_rho}")
            found = True
    assert found, "예측·관측이 모두 고유한 held-out 데이터셋이 하나도 없다"


def test_ties_in_observations_cap_ceiling_below_one_even_with_unique_predictions():
    """위 함정의 반대쪽을 직접 고정한다: 예측이 전부 고유해도 관측에 동점이 있으면
    상한이 1.0 미만이어야 한다(반증되면 폐형식 계산이 관측 쪽 동점을 무시하고
    있다는 뜻)."""
    r = _dataset_result("gong2024_4hsic_alumina_kmno4_L25")
    assert n_groups(r.predicted) == r.n
    obs_unique = len(set(round(float(o), 9) for o in r.observed))
    assert obs_unique < r.n, "이 회귀의 전제(관측 동점)가 데이터셋 변경으로 깨졌다"
    ceil_rho = optimal_group_order_rho(r.predicted, r.observed)
    assert ceil_rho < 1.0 - 1e-6
    assert ceil_rho == pytest.approx(0.99092, rel=1e-3)


# ═══════════════ 구조적으로 영원히 유의 불가한 2건 ═══════════════

def test_hong2007_ceiling_p_not_significant():
    r = _dataset_result("hong2007_cu_ads_bta_polish_rate")
    ceil_rho = optimal_group_order_rho(r.predicted, r.observed)
    p = backtest.perm_p_value(ceil_rho, r.n)
    assert p is not None and p >= backtest.BacktestResult.P_THRESHOLD, (
        f"hong2007 상한 p={p} — 유의해졌다면 구조적 봉쇄 주장이 깨진 것이다")


def test_us9200180b2_benzenesulfonic_ceiling_p_not_significant():
    r = _dataset_result("us9200180b2_cu_benzenesulfonic_series")
    ceil_rho = optimal_group_order_rho(r.predicted, r.observed)
    p = backtest.perm_p_value(ceil_rho, r.n)
    assert p is not None and p >= backtest.BacktestResult.P_THRESHOLD, (
        f"us9200180b2_cu_benzenesulfonic_series 상한 p={p}")


# ═══════════════ 실제 ρ는 상한을 넘을 수 없다 ═══════════════

def test_actual_rho_never_exceeds_ceiling_anywhere():
    """넘으면 계산 결함이다 — 상한은 정의상 도달 가능한 최댓값이다."""
    results = compute_all()
    assert results, "compute_all()이 아무것도 반환하지 않는다"
    for r in results:
        assert r.actual_rho <= r.rho_ceiling + 1e-6, (
            f"{r.dataset}: actual={r.actual_rho} > ceiling={r.rho_ceiling}")
