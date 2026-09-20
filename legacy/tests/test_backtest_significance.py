"""백테스트 통계 판정 계약 테스트.

핵심: **높은 ρ가 곧 증거는 아니다.** 조건 수가 적으면 우연히도 완벽한 순위가
나온다. 이 파일은 그 구분이 무너지지 않게 고정한다.
"""
import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "validation"))

from validation.backtest import (perm_p_value, spearman_rho,   # noqa: E402
                                 BacktestResult, run_all)


def _mk(n, rho, **kw):
    kw.setdefault("in_scope", True)
    return BacktestResult(
        dataset="t", n=n, spearman=rho, kendall=rho,
        pairwise_accuracy=(1 + rho) / 2, mape_pct=10.0, scale_factor=1.0,
        p_value=perm_p_value(rho, n), **kw)


# ═══════════════ n=3의 완벽한 예측은 증거가 아니다

def test_n3_perfect_rank_is_not_significant():
    """n=3에서 ρ=+1.000의 p는 정확히 1/6 ≈ 0.167이다.

    ⚠ 2026-09-08에 실제로 잡은 함정: held-out 평균 ρ=+0.481이 이런 데이터셋
      3개로 부풀려져 있었고, 백테스트는 그것을 "IR·사업계획서에 쓸 수 있는
      유일한 정량 근거"라고 출력했다. 투자자 앞에 들고 갈 숫자가 동전 던지기였다.
    """
    p = perm_p_value(1.0, 3)
    assert p == pytest.approx(1 / 6, abs=1e-9)
    assert not _mk(3, 1.0).significant
    assert "유의하지 않음" in _mk(3, 1.0).verdict()


def test_n4_perfect_rank_is_significant():
    """n=4에서는 1/24 ≈ 0.042로 문턱(0.05)을 겨우 넘는다."""
    assert perm_p_value(1.0, 4) == pytest.approx(1 / 24, abs=1e-9)
    assert _mk(4, 1.0).significant


def test_small_n_cannot_be_significant_structurally():
    """n≤3은 아무리 완벽해도 구조적으로 p<0.05가 불가능하다."""
    for n in (3,):
        assert perm_p_value(1.0, n) > BacktestResult.P_THRESHOLD


def test_p_value_monotonic_in_rho():
    """같은 n에서 ρ가 높을수록 p는 작아야 한다."""
    ps = [perm_p_value(r, 6) for r in (-0.5, 0.0, 0.5, 1.0)]
    assert all(ps[i] >= ps[i + 1] for i in range(len(ps) - 1)), ps


def test_negative_rho_is_never_significant():
    """음의 상관은 '유의한 성능'이 될 수 없다(단측 검정)."""
    assert not _mk(9, -0.525).significant
    assert not _mk(3, -0.5).significant


# ═══════════════ 판정 문구가 거짓말하지 않는다

def test_verdict_prioritises_significance_over_rho():
    """ρ=1.0이어도 유의하지 않으면 '사용 가능'이라 말하면 안 된다."""
    v = _mk(3, 1.0).verdict()
    assert "사용 가능" not in v
    assert "우연" in v


def test_calibration_data_never_counts_as_validation():
    r = _mk(9, 0.99, used_for_calibration=True)
    assert "검증 아님" in r.verdict()


def test_out_of_scope_never_counts():
    r = _mk(50, 0.95, in_scope=False)
    assert "범위밖" in r.verdict()


# ═══════════════ 실제 데이터셋에 대한 회귀

def test_real_datasets_have_at_least_one_significant_heldout():
    """유의한 held-out이 최소 1개는 있어야 한다 — 없으면 '검증했다'가 거짓이 된다."""
    results = run_all()
    held = [r for r in results if not r.used_for_calibration
            and r.in_scope and not np.isnan(r.spearman)]
    assert held, "held-out 데이터셋이 하나도 없다"
    sig = [r for r in held if r.significant]
    assert sig, ("유의한 held-out이 0개다 — 이 상태에서 성능을 주장하면 안 된다. "
                 "조건 수가 많은 데이터셋을 추가하라.")


def test_every_heldout_result_carries_a_p_value():
    for r in run_all():
        if np.isnan(r.spearman):
            continue
        assert r.p_value is not None, f"{r.dataset}에 p값이 없다"


def test_absolute_mrr_is_not_claimed_anywhere():
    """계통 편향이 큰 데이터셋이 다수다 — 절대값 신뢰 금지가 유지돼야 한다."""
    results = run_all()
    held = [r for r in results if r.in_scope and not r.used_for_calibration]
    biased = [r for r in held if r.scale_factor is not None
              and (r.scale_factor < 0.5 or r.scale_factor > 2.0)]
    # 편향이 사라졌다면 그건 좋은 소식이지만, 그때는 이 테스트를 갱신해야 한다.
    assert biased, ("계통 편향이 전부 사라졌다 — 절대값 주장이 가능해졌는지 "
                    "재검토하고 이 테스트를 갱신하라.")
