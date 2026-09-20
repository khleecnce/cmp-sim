"""Δ damage_exponent — R1(소거) 판정 회귀 고정.

EVIDENCE-RULES 판정#31 / knowledge/cmp/delta-damage-exponent-cu-system-primary-data.md
"## 3회차": `damage_exponent`는 Δ가 실제로 쓰이는 방식(MRR 비결합 진단 전용)에서는
`sim/unknown_router.py`의 R1(소거)이 성립한다 — D99 what-if 스윕에서 n을 자릿수로
흔들어도 Δ의 **순위**는 불변이다. 이 파일은 그 결론을 기계로 고정한다.

절대 배수는 n에 강하게 의존한다(순위 무관과 혼동 금지) — 그 편차 자체는
delta-damage-exponent-cu-system-primary-data.md §3.1의 verify 블록이 고정한다.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sim.engine import Recipe                              # noqa: E402
from sim.factors import compute_factors, MRR_COUPLED        # noqa: E402
from sim.unknown_router import cancellation_test            # noqa: E402


def _delta(pack="cu_h2o2_bta", **overrides):
    return compute_factors(Recipe(pack=pack, pack_overrides=overrides).resolve())["delta"]


def test_delta_not_mrr_coupled():
    """Δ가 MRR_COUPLED 밖에 있어야 R1 판정의 전제(진단 전용)가 성립한다."""
    assert "delta" not in MRR_COUPLED


def test_reference_condition_alone_is_flagged_as_unused_not_cancellation():
    """cu 팩의 기준조건(D99=D99_ref=500)만 단독으로 탐침하면 n이 계산 경로에
    들어가지 않아 출력이 비트 단위로 동일하다 — cancellation_test는 이를
    '소거'가 아니라 '미사용'(모델결함 경고)으로 구분해야 한다."""
    def predict(n):
        return [_delta(damage_exponent=n).value]

    cancels, evidence = cancellation_test(predict, [0.5, 1.44, 2.54, 5.0, 10.0])
    assert cancels is False
    assert evidence["미사용"] is True


def test_delta_rank_invariant_under_d99_whatif_sweep_across_digit_spanning_n():
    """D99 what-if 레시피 벡터에 대해 n을 0.5~10.0(자릿수)으로 흔들어도
    Δ의 순위는 그대로다 — (D99/D99_ref)^n이 n>0에서 D99에 단조증가이므로."""
    d99_sweep = [250.0, 350.0, 500.0, 700.0, 1000.0]

    def predict(n):
        return [_delta(abrasive_d99_nm=d, damage_exponent=n).value for d in d99_sweep]

    cancels, evidence = cancellation_test(predict, [0.5, 1.44, 2.54, 5.0, 10.0])
    assert cancels is True
    assert evidence["미사용"] is False
    assert evidence["절대값 로그편차"] > 1.0, (
        "순위는 불변이어도 절대값 편차는 커야 한다 — 순위 소거와 절대 배수 결론은 다르다는 "
        "판정#31의 핵심 구분을 이 회귀가 놓치면 안 된다")


def test_absolute_multiplier_depends_strongly_on_n_even_though_rank_does_not():
    """R1의 한계 — 순위는 n 없이도 보존되지만, D99 2배일 때 Δ가 몇 배인지는
    n에 강하게 의존한다(1.4배~1024배, 탐침 구간 내에서 3자릿수 차이)."""
    ratios = []
    for n in (0.5, 1.44, 2.54, 5.0, 10.0):
        v_lo = _delta(abrasive_d99_nm=500.0, damage_exponent=n).value
        v_hi = _delta(abrasive_d99_nm=1000.0, damage_exponent=n).value
        ratios.append(v_hi / v_lo)

    assert ratios == sorted(ratios), "배수 자체는 n에 대해 단조증가해야 한다"
    assert ratios[0] < 2.0 and ratios[-1] > 100.0, ratios
