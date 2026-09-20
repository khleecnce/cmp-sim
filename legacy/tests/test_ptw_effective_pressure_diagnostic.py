"""npw_ptw_effective_pressure.py 엔진 등록 회귀 — WaferResult 진단 필드 2종
(ptw_effective_pressure_ratio · ptw_effective_pressure_note).

Sorooshian(2005) §3.3 실측표 조회값이며 MRR 경로와 완전히 독립인 진단이다.
PTW + rr.meta['pattern_density']가 표에 있는 값(0.10/0.50/0.90)일 때만 채워지고,
그 외엔 조용히 None(지어내지 않는다).
"""
import npw_ptw_effective_pressure as EPR

from sim.engine import Recipe, simulate


def test_npw_wafer_leaves_fields_none():
    res = simulate(Recipe(wafer="NPW", meta={"pattern_density": 0.5}))
    assert res.ptw_effective_pressure_ratio is None
    assert res.ptw_effective_pressure_note is None


def test_ptw_without_pattern_density_leaves_fields_none():
    res = simulate(Recipe(wafer="PTW"))
    assert res.ptw_effective_pressure_ratio is None
    assert res.ptw_effective_pressure_note is None


def test_ptw_density_0_5_matches_module_value():
    res = simulate(Recipe(wafer="PTW", meta={"pattern_density": 0.5}))
    assert res.ptw_effective_pressure_ratio is not None
    # 엔진이 실제로 호출하는 함수와 정확히 일치해야 한다
    expected = EPR.effective_pressure_ratio(0.5)
    assert abs(res.ptw_effective_pressure_ratio - expected) < 1e-9
    # 노트가 인용하는 "대략 1.79"(mean_ratio_at_density, 4온도 평균) 오더와도 크게 벗어나지 않아야 한다
    # — effective_pressure_ratio는 23°C 한 온도만 평균하므로 완전히 같지는 않다(§3.3 온도별 차이)
    assert abs(res.ptw_effective_pressure_ratio - EPR.mean_ratio_at_density(0.5)) < 0.3
    assert res.ptw_effective_pressure_note is not None
    s = res.summary()
    assert s["ptw_effective_pressure_ratio"] == res.ptw_effective_pressure_ratio
    assert s["ptw_effective_pressure_note"] == res.ptw_effective_pressure_note


def test_ptw_density_not_in_table_skips_with_note():
    res = simulate(Recipe(wafer="PTW", meta={"pattern_density": 0.4}))
    assert res.ptw_effective_pressure_ratio is None
    assert res.ptw_effective_pressure_note is None
    assert any("pattern_density=0.4" in n and "표에 없는 값" in n for n in res.notes)


def test_diagnostic_does_not_affect_mrr():
    base = simulate(Recipe(wafer="PTW"))
    with_density = simulate(Recipe(wafer="PTW", meta={"pattern_density": 0.5}))
    assert (base.mrr_nm_per_min == with_density.mrr_nm_per_min).all()
