"""tier1.pattern_density_effective_pressure 모델 회귀 테스트.

Sorooshian(2005) §3.3 실측표(sim/tier2_physics/npw_ptw_effective_pressure.py, 1바이트도
수정 안 함)의 유효압력/인가압력 비를 Preston blanket MRR에 곱하는 선택형(opt-in) 모델.
명시적으로 골랐을 때만 돌며, 게이트 미충족이면 조용한 blanket 폴백 없이 ValueError로
크게 실패해야 한다(등록만 됐다고 아무 레시피에서나 조용히 값을 내주면 안 됨).
"""
import numpy as np
import pytest

import npw_ptw_effective_pressure as EPR

from sim.engine import Recipe, simulate, _MODELS

MODEL = "tier1.pattern_density_effective_pressure"


def test_model_registered():
    assert MODEL in _MODELS


def test_density_010_3psi_matches_table_ratio_exactly():
    recipe = Recipe(wafer="PTW", meta={"pattern_density": 0.10})
    base = simulate(recipe, model="tier1.preston_radial")
    with_model = simulate(recipe, model=MODEL)
    ratio = EPR.table_ratio(0.10, 3, 23)
    assert abs(ratio - 8.01 / 3) < 1e-9
    assert np.allclose(with_model.removed_nm, ratio * base.removed_nm, rtol=1e-9)


def test_density_050_3psi_absolute_ratio():
    ratio = EPR.table_ratio(0.50, 3, 23)
    assert abs(ratio - 4.64 / 3) < 1e-9


def test_density_090_3psi_absolute_ratio():
    ratio = EPR.table_ratio(0.90, 3, 23)
    assert abs(ratio - 3.50 / 3) < 1e-9


def test_density_050_7psi_absolute_ratio():
    recipe = Recipe(wafer="PTW", pressure_psi=7.0, meta={"pattern_density": 0.50})
    base = simulate(recipe, model="tier1.preston_radial")
    with_model = simulate(recipe, model=MODEL)
    ratio = EPR.table_ratio(0.50, 7, 23)
    assert abs(ratio - 11.42 / 7) < 1e-9
    assert np.allclose(with_model.removed_nm, ratio * base.removed_nm, rtol=1e-9)


def test_npw_raises_value_error():
    recipe = Recipe(wafer="NPW", meta={"pattern_density": 0.50})
    with pytest.raises(ValueError):
        simulate(recipe, model=MODEL)


def test_missing_pattern_density_raises_value_error():
    recipe = Recipe(wafer="PTW")
    with pytest.raises(ValueError):
        simulate(recipe, model=MODEL)


def test_pattern_density_outside_table_raises_value_error():
    recipe = Recipe(wafer="PTW", meta={"pattern_density": 0.30})
    with pytest.raises(ValueError):
        simulate(recipe, model=MODEL)


def test_pressure_psi_outside_table_raises_value_error():
    recipe = Recipe(wafer="PTW", pressure_psi=4.0, meta={"pattern_density": 0.50})
    with pytest.raises(ValueError):
        simulate(recipe, model=MODEL)


def test_default_model_npw_removed_nm_bit_invariant():
    """기본 모델(tier1.preston_radial)의 출력은 이 모델 추가 전후로 비트 단위 불변이어야 한다."""
    res = simulate(Recipe(wafer="NPW"))
    assert res.removed_nm.shape == (81,)
    assert abs(float(res.removed_nm[0]) - 142.95941840061286) < 1e-9
    assert abs(float(res.removed_nm[-1]) - 143.11903585308139) < 1e-9


def test_notes_disclose_limitations():
    recipe = Recipe(wafer="PTW", meta={"pattern_density": 0.10})
    res = simulate(recipe, model=MODEL)
    joined = " ".join(res.notes)
    assert "23" in joined
    assert "up" in joined or "융기" in joined


# ───────────────────────────────── 판정#65 (EVIDENCE-RULES, 2026-09-19)
# 두 패턴 모델(Boning 1/ρ vs Sorooshian 실측표)이 같은 양에 대해 다른 값을 낸다는
# 사실 자체를 고정한다. 누군가 조용히 한쪽을 다른 쪽에 맞추거나(평균·보정계수),
# 1/ρ 모델을 삭제하면 이 테스트가 깨진다 — 둘 다 금지다(§3 스코프 분할).
def test_two_pattern_models_disagree_ruling65():
    import sim.models  # noqa: F401  (Boning 모델 등록 부작용)
    from sim.engine import Recipe, simulate

    # 판정#65 본문에 기록한 실행값. 1/ρ 는 저밀도일수록 실측 대비 과대예측한다.
    expected_overpredict = {0.10: 2.4964, 0.50: 1.2929, 0.90: 0.9522}
    for rho, exp in expected_overpredict.items():
        r = Recipe(n_points=41, time_s=60, wafer="PTW", pressure_psi=3.0,
                   meta={"pattern_density": rho})
        boning = simulate(r, model="tier1.pattern_density").metrics.mean_nm
        measured = simulate(
            r, model="tier1.pattern_density_effective_pressure").metrics.mean_nm
        assert boning / measured == pytest.approx(exp, rel=1e-3), (
            f"ρ={rho}: 1/ρ 대 실측표 배수가 {boning/measured:.4f} — 판정#65 기록값 {exp}와 "
            "다르다. 두 모델을 수렴시키거나 평균내는 것은 판정#65가 금지한 조치다.")

    # 저밀도에서 가장 크게 어긋난다는 것이 이 판정의 핵심 — 방향을 고정한다.
    assert expected_overpredict[0.10] > expected_overpredict[0.50] > expected_overpredict[0.90]


def test_boning_model_carries_ruling65_warning():
    """1/ρ 모델을 계속 쓸 수는 있지만, 쓸 때 근거 등급이 낮다는 사실이 출력에 남아야 한다."""
    import sim.models  # noqa: F401
    from sim.engine import Recipe, simulate

    r = Recipe(n_points=41, time_s=60, wafer="PTW", pressure_psi=3.0,
               meta={"pattern_density": 0.10})
    notes = " ".join(simulate(r, model="tier1.pattern_density").notes)
    assert "판정#65" in notes
    assert "pattern_density_effective_pressure" in notes


def test_ptw_warning_recognizes_new_pattern_model():
    """신규 패턴 모델을 골랐는데 'NPW 등가'라는 거짓 경고가 붙으면 안 된다(기존 버그)."""
    import sim.models  # noqa: F401
    from sim.engine import Recipe, simulate

    r = Recipe(n_points=41, time_s=60, wafer="PTW", pressure_psi=3.0,
               meta={"pattern_density": 0.50})
    notes = " ".join(
        simulate(r, model="tier1.pattern_density_effective_pressure").notes)
    assert "NPW 등가" not in notes
    # 반대로 패턴 모델을 안 쓰면 경고가 실제로 붙어야 한다
    base_notes = " ".join(simulate(r, model="tier1.preston_radial").notes)
    assert "NPW 등가" in base_notes
