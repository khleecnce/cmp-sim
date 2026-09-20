"""민감도·기여 분해 계약 테스트.

사용자 지시(2026-09-06): "각 요소를 나눠서 적용... 각각의 요소가 얼마나 performance
기여에 영향을 주는지, 변화시켰을때 어떻게 바뀔건지 예측해"

이 파일이 지키는 것: **민감도 0의 서로 다른 의미가 뒤섞이지 않는가.**
0이 '영향 없음'/'이미 최적'/'모델 한계'/'미구현' 중 무엇인지 구분하지 못하면
사용자가 "이 손잡이는 쓸모없다"고 정반대로 오판한다.
"""
import sys
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from sim.engine import Recipe, simulate  # noqa: E402
import sim.models  # noqa: E402,F401
from sim.sensitivity import (FACTORS, CANCELLED_BY_CALIBRATION,  # noqa: E402
                             Sensitivity, decompose, elasticity,
                             rank_factors)

BY_KEY = {f.key: f for f in FACTORS}
CU = Recipe(pack="cu_h2o2_bta", time_s=60)


# ── 물리 구조가 지수로 재현되는가 ───────────────────────────
def test_preston_pressure_elasticity_is_unity():
    """Preston MRR = Kp·P·V ⟹ 압력 탄성도는 정확히 1.0.

    이건 튜닝 결과가 아니라 물리 구조다. 1이 아니면 모델이 깨진 것이다.
    """
    s = elasticity(CU, BY_KEY["pressure_psi"], metric="mrr")
    assert s is not None
    assert s.elasticity == pytest.approx(1.0, abs=0.02)
    assert s.stable


def test_velocity_elasticity_is_near_unity():
    """속도도 Preston상 선형. 플래튼 회전수가 상대속도를 지배한다."""
    s = elasticity(CU, BY_KEY["rpm_platen"], metric="mrr")
    assert s is not None
    assert 0.8 < s.elasticity < 1.2


# ── 민감도 0의 네 가지 의미 ─────────────────────────────────
def test_optimum_is_not_confused_with_no_effect():
    """탄성도 0의 네 의미('이미 최적'/'무영향'/'미모델링'/'상쇄됨')를 구분하는가.

    회귀 방어: 이 상태들은 숫자가 똑같이 0.000으로 보이는데 의미는 정반대다.
    실제로 산화제가 '미모델링'으로 오진됐었다(2026-09-06).

    ⚠ 2026-09-14(EVIDENCE-RULES 판정#20) 이전에는 이 판별을 cu_h2o2_bta 산화제가
    정점(3.0 wt%)에 앉아 있다는 전제로 엔진을 통해 걸었다. 그 전제 자체가 대상계
    실측으로 반증됐고(레거시 단봉 경로 → Langmuir 부동태 억제 경로로 교체,
    knowledge/cmp/chi-oxidizer-cu-h2o2-reparameterization.md), 이제 어느 저장 팩도
    레거시 정점 경로를 쓰지 않는다. 그래서 판별 **로직 자체**를 직접 건다 —
    보호 대상(0의 의미가 뒤섞이지 않는 것)은 그대로이고, 더 이상 참이 아닌
    물리 전제에 의존하지 않는다.
    """
    def mk(elast, curv, modeled=True, key="oxidizer_wt_pct"):
        return Sensitivity(factor=BY_KEY[key], metric="mrr", base_value=1.0,
                           base_metric=1.0, elasticity=elast, leverage=0.0,
                           stable=True, modeled=modeled, curvature=curv)

    # (a) 이미 최적 — 1차 0, 2차 음수
    at_peak = mk(0.0, -0.53)
    assert at_peak.at_optimum()
    assert "정점" in at_peak.direction()

    # (b) 진짜 무영향 — 1차 0, 2차도 0. (a)와 숫자는 같지만 의미가 정반대다.
    flat = mk(0.0, 0.0)
    assert not flat.at_optimum()
    assert flat.direction() == "무영향"

    # (c) 미모델링 — 엔진이 이 인자를 아예 안 쓴다
    unmodeled = mk(0.0, 0.0, modeled=False)
    assert not unmodeled.at_optimum()
    assert unmodeled.direction() == "미모델링"

    # (d) 캘리브레이션 상쇄 — 0이지만 '무관'이 아니라 모델 구조 문제
    cancelled = mk(0.0, 0.0, modeled=False, key="pad_E_star_pa")
    assert cancelled.direction() == "상쇄됨"

    # 네 상태가 서로 다른 라벨로 갈라져야 한다(뒤섞이면 이 테스트의 존재 이유가 사라진다)
    labels = {at_peak.direction(), flat.direction(),
              unmodeled.direction(), cancelled.direction()}
    assert len(labels) == 4, f"0의 네 의미가 구분되지 않는다: {labels}"


def test_oxidizer_sensitivity_sign_follows_passivation():
    """cu_h2o2_bta 산화제 탄성도는 전 구간 음수여야 한다(부동태 억제 지배).

    [EVIDENCE-RULES 판정#41→#47] 판정#41은 이 팩이 산성(pH<6)×착화제(chelator_M>0)
    조건이면 무조건 촉진-포화형(`oxidizer_acid_chelator_K`, 옥살산 데이터로 적합)을
    타도록 게이트를 신설해 이 테스트가 한때 "전 구간 양수"를 요구했었다. 그런데
    판정#43이 이 팩의 실제 착화제(**글리신**) 1차 데이터(US5,575,885)를 그 가지에
    대보니 부호가 반대(단조 감소)로 구조적 반증됐고, 판정#45가 "옥살산과 글리신을
    하나의 레짐으로 묶은 것 자체가 과도한 일반화"라고 판정했다. 판정#47이 게이트를
    착화제 종 특이적으로 좁혀(`oxidizer_acid_chelator_species` != `chelator_species`
    면 폴백) 이 팩을 원래 자기 레짐인 `oxidizer_passivation_K`(부동태 억제)로
    되돌렸다 — 부호가 다시 뒤집힌 것은 회귀가 아니라 BIAS 수정이다.
    근거: knowledge/cmp/chi-oxidizer-gate-chelator-species-specificity.md
    """
    for C in (1.0, 3.0, 6.0):
        r = Recipe(pack="cu_h2o2_bta", time_s=60,
                   pack_overrides={"oxidizer_wt_pct": C})
        s = elasticity(r, BY_KEY["oxidizer_wt_pct"], metric="mrr")
        assert s is not None
        assert s.elasticity < -0.05, (
            f"C={C} wt%: 이 팩의 실제 레짐(산성×글리신)은 부동태 억제라 산화제를 "
            f"더 넣으면 MRR이 낮아져야 한다 — got {s.elasticity:.4f}")

    # 민감도가 살아 있는가 — '미모델링'과 구분되어야 한다(산화제 오진 회귀 방어)
    s_mid = elasticity(Recipe(pack="cu_h2o2_bta", time_s=60,
                              pack_overrides={"oxidizer_wt_pct": 3.0}),
                       BY_KEY["oxidizer_wt_pct"], metric="mrr")
    assert abs(s_mid.elasticity) > 1e-3, "산화제 축이 죽어 있으면 안 된다"


def test_pad_properties_are_flagged_as_cancelled_not_irrelevant():
    """패드 물성이 0으로 나오는 건 모델 구조 문제이지 '무관'이 아니다.

    GW alpha 역산이 n_contacts 변화를 정확히 상쇄한다(E* 0.5/1/2 GPa에서
    n=6357/3179/1589인데 MRR은 셋 다 99.36으로 동일). 실측 2점이 있어야 풀린다.
    """
    s = elasticity(CU, BY_KEY["pad_E_star_pa"], metric="mrr")
    assert s is not None
    assert abs(s.elasticity) < 1e-6
    assert s.factor.key in CANCELLED_BY_CALIBRATION
    assert s.direction() == "상쇄됨"
    assert "캘리브레이션" in s.note or "실측" in s.note


def test_unmodeled_factors_say_so_explicitly():
    """엔진이 안 쓰는 인자는 그 사실을 명시해야 한다 — 침묵은 거짓말이다."""
    s = elasticity(CU, BY_KEY["abrasive_size_nm"], metric="mrr")
    assert s is not None
    assert s.direction() == "미모델링"
    assert s.note and ("연결" in s.note or "않" in s.note)


# ── 레버리지: 탄성도만으로는 부족하다 ───────────────────────
def test_leverage_accounts_for_practical_range():
    """탄성도가 같아도 조절 가능 폭이 크면 레버리지가 커야 한다.

    압력(1.5~5.0psi)과 플래튼rpm(30~120)은 둘 다 탄성도 ~1.0이지만
    회전수의 조절 폭이 넓어 실무 영향력이 더 크다.
    """
    p = elasticity(CU, BY_KEY["pressure_psi"], metric="mrr")
    v = elasticity(CU, BY_KEY["rpm_platen"], metric="mrr")
    assert p.elasticity == pytest.approx(v.elasticity, abs=0.05), "탄성도는 비슷해야"
    assert v.leverage > p.leverage, "조절 폭이 넓은 쪽이 레버리지가 커야 한다"


def test_ranking_puts_actionable_factors_first():
    """순위 1위는 실제로 돌릴 수 있는 인자여야 한다(레버리지 0이 위로 오면 안 됨)."""
    ranked = rank_factors(CU, metric="mrr")
    assert ranked[0].leverage > 0
    assert ranked[-1].leverage == pytest.approx(0.0, abs=1e-6)


# ── 지표 간 상충 ────────────────────────────────────────────
def test_mrr_and_uniformity_can_disagree():
    """같은 인자가 MRR과 균일도에 반대로 작용할 수 있어야 한다.

    이 상충을 못 보면 "MRR 올리는 법"만 알려주고 고객의 진짜 합격 기준
    (균일도)을 망치는 도구가 된다.
    """
    pairs = []
    for f in FACTORS:
        a = elasticity(CU, f, metric="mrr")
        b = elasticity(CU, f, metric="ttv")
        if a and b and abs(a.elasticity) > 1e-3:
            pairs.append((a.elasticity, b.elasticity))
    assert pairs, "비교할 인자가 없다"
    assert any(x > 0 and y < 0 for x, y in pairs), \
        "MRR↑ + TTV↓ (양쪽 개선) 조합이 하나는 있어야 한다"


# ── 기여 분해 ───────────────────────────────────────────────
def test_decomposition_accounts_for_total_change():
    """요소별 배수의 곱 × 상호작용 잔차 = 전체 변화."""
    mod = Recipe(pack="cu_h2o2_bta", time_s=60, pressure_psi=4.5,
                 pack_overrides={"inhibitor_mM": 0.3})
    contribs, total, _ = decompose(mod)
    assert contribs, "바뀐 인자가 있는데 기여가 비었다"
    prod = 1.0
    for c in contribs:
        prod *= c.factor_x
    assert prod == pytest.approx(total, rel=0.02), \
        f"기여 곱({prod})이 전체 변화({total})와 안 맞는다"


def test_decomposition_separates_domains():
    """기계 변경과 화학 변경이 각각 자기 영역으로 분류돼야 한다."""
    mod = Recipe(pack="cu_h2o2_bta", time_s=60, pressure_psi=4.5,
                 pack_overrides={"inhibitor_mM": 0.3})
    contribs, _, _ = decompose(mod)
    domains = {c.domain for c in contribs}
    assert "mechanical" in domains and "chemical" in domains


def test_pack_override_actually_changes_result():
    """pack_overrides가 실제로 먹혀야 한다.

    회귀 방어: oxidizer_ref_wt_pct가 팩에 없으면 로더가 '현재 농도'로 폴백해
    항상 자기 자신과 비교하게 되고 배수가 영원히 1.0이 된다(실제 발생).
    """
    import numpy as np
    base = float(np.mean(simulate(CU).mrr_nm_per_min))
    off = float(np.mean(simulate(Recipe(
        pack="cu_h2o2_bta", time_s=60,
        pack_overrides={"oxidizer_wt_pct": 9.0})).mrr_nm_per_min))
    assert off != pytest.approx(base, rel=1e-6), \
        "산화제를 3배로 올렸는데 MRR이 그대로다 — override가 안 먹고 있다"
