"""pad_groove_eol.py 엔진 등록 회귀 — WaferResult 진단 필드 4종(패드 그루브 EOL 진단).

근거: sim/tier2_physics/pad_groove_eol.py (self-test 9/9 PASS),
knowledge/materials/pad-thickness-groove-depth-monitoring-replacement-economics.md
(Son & Lee 2021, Appl. Sci. 11(8) 3521, doi:10.3390/app11083521) §2.
컷레이트 c는 팩이 pad_cut_rate_um_per_h를 선언할 때만 계산한다(하드코딩 금지) —
현재 5팩 전부 미선언이라 시뮬레이션 기본 경로에서는 항상 None이 정상이다.
MRR 경로와 독립인 진단 필드라 mrr_nm_per_min은 건드리지 않는다.
"""
import numpy as np

import sim.engine as E
from sim.engine import Recipe, simulate, _pad_groove_eol_diagnostic
from sim.params import Param
import pad_groove_eol as PGE


def test_none_without_cut_rate():
    # 5팩 전부 pad_cut_rate_um_per_h를 선언하지 않는다 — 스킵되는 것이 정상.
    rr = Recipe(pack="cu_h2o2_bta", time_s=60).resolve()
    assert not rr.pack.has("pad_cut_rate_um_per_h")
    out = _pad_groove_eol_diagnostic(rr)
    assert out["pad_groove_cumulative_wear_um"] is None
    assert out["pad_groove_eol_hours"] is None
    assert out["pad_groove_exhausted"] is None
    assert out["pad_groove_note"] is not None
    assert "pad_cut_rate_um_per_h" in out["pad_groove_note"]


def test_none_in_full_simulate_for_all_default_packs():
    res = simulate(Recipe(pack="cu_h2o2_bta", time_s=60))
    assert res.pad_groove_cumulative_wear_um is None
    assert res.pad_groove_eol_hours is None
    assert res.pad_groove_exhausted is None
    assert res.pad_groove_note is not None


def test_cumulative_wear_matches_c_times_hours():
    recipe = Recipe(pack="cu_h2o2_bta", time_s=60, meta={"pad_hours": "10"})
    rr = recipe.resolve()
    rr.pack.params["pad_cut_rate_um_per_h"] = Param(
        key="pad_cut_rate_um_per_h", value=43.4, unit="um/h",
        source="test-probe", confidence="estimated")
    out = _pad_groove_eol_diagnostic(rr)
    assert out["pad_groove_cumulative_wear_um"] == 43.4 * 10.0


def test_eol_hours_matches_groove_depth_mm_conversion():
    recipe = Recipe(pack="cu_h2o2_bta", time_s=60, meta={"pad_hours": "1"})
    rr = recipe.resolve()
    rr.pack.params["pad_cut_rate_um_per_h"] = Param(
        key="pad_cut_rate_um_per_h", value=43.4, unit="um/h",
        source="test-probe", confidence="estimated")
    out = _pad_groove_eol_diagnostic(rr)
    d0_um = rr.pack.param("groove_depth_mm").value * 1000.0
    assert d0_um == 760.0
    expected = PGE.groove_eol_hours(43.4, d0_um)
    assert out["pad_groove_eol_hours"] == expected


def test_exhausted_flips_across_eol_hours():
    d0_um = 760.0
    c = 43.4
    eol_h = PGE.groove_eol_hours(c, d0_um)

    recipe_under = Recipe(pack="cu_h2o2_bta", time_s=60,
                          meta={"pad_hours": str(eol_h - 1.0)})
    rr_under = recipe_under.resolve()
    rr_under.pack.params["pad_cut_rate_um_per_h"] = Param(
        key="pad_cut_rate_um_per_h", value=c, unit="um/h",
        source="test-probe", confidence="estimated")
    out_under = _pad_groove_eol_diagnostic(rr_under)
    assert out_under["pad_groove_exhausted"] is False

    recipe_over = Recipe(pack="cu_h2o2_bta", time_s=60,
                         meta={"pad_hours": str(eol_h + 1.0)})
    rr_over = recipe_over.resolve()
    rr_over.pack.params["pad_cut_rate_um_per_h"] = Param(
        key="pad_cut_rate_um_per_h", value=c, unit="um/h",
        source="test-probe", confidence="estimated")
    out_over = _pad_groove_eol_diagnostic(rr_over)
    assert out_over["pad_groove_exhausted"] is True


def test_pad_groove_diagnostic_does_not_change_mrr():
    # 이 진단을 계산하든 안 하든 mrr_nm_per_min은 비트 단위로 동일해야 한다 —
    # MRR 경로와 완전히 독립적인 진단이라는 계약.
    r = Recipe(pack="cu_h2o2_bta", time_s=60, meta={"pad_hours": "10"})
    res_with = simulate(r)

    orig = E._pad_groove_eol_diagnostic
    E._pad_groove_eol_diagnostic = lambda rr: {
        "pad_groove_cumulative_wear_um": 999.0,
        "pad_groove_eol_hours": 1.0,
        "pad_groove_exhausted": True,
        "pad_groove_note": "test-probe",
    }
    try:
        res_forced = simulate(r)
    finally:
        E._pad_groove_eol_diagnostic = orig

    assert np.array_equal(res_with.mrr_nm_per_min, res_forced.mrr_nm_per_min)
    assert res_forced.pad_groove_cumulative_wear_um == 999.0
