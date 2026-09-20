"""cu_pourbaix.py 엔진 등록 회귀 — WaferResult 진단 필드 4종(Cu-H2O Pourbaix E-무관 진단).

근거: sim/tier2_physics/cu_pourbaix.py (self-test 10/10 PASS),
knowledge/cmp/cu-electrochemistry-pourbaix-bta-oxidizer-inhibitor.md.
Recipe에 전극전위 필드가 없어 stable_phase()는 호출하지 않고, E와 무관한
수직선(Cu2+/Cu(OH)2 대용 경계)·삼중점 pH만 낸다. MRR 경로와 독립인 진단
필드라 mrr_nm_per_min은 건드리지 않는다.
"""
import numpy as np

import sim.engine as E
from sim.engine import Recipe, simulate, _cu_pourbaix_diagnostic
import cu_pourbaix as CUP


def test_none_without_slurry_ph():
    rr = Recipe(pack="cu_h2o2_bta", time_s=60).resolve()
    del rr.pack.params["slurry_ph"]
    out = _cu_pourbaix_diagnostic(rr)
    assert out["cu_pourbaix_vertical_ph"] is None
    assert out["cu_pourbaix_triple_point_ph"] is None
    assert out["cu_pourbaix_soluble_domain"] is None
    assert out["cu_pourbaix_note"] is not None


def test_none_for_non_cu_film():
    # film != "cu"인 팩(oxide_silica는 slurry_ph가 있지만 Cu 계가 아니다)은 조용히 None.
    res = simulate(Recipe(pack="oxide_silica", time_s=60))
    assert res.cu_pourbaix_vertical_ph is None
    assert res.cu_pourbaix_triple_point_ph is None
    assert res.cu_pourbaix_soluble_domain is None
    assert res.cu_pourbaix_note is not None


def test_filled_for_cu_pack():
    res = simulate(Recipe(pack="cu_h2o2_bta", time_s=60))
    assert res.cu_pourbaix_vertical_ph is not None
    assert res.cu_pourbaix_triple_point_ph is not None
    assert res.cu_pourbaix_soluble_domain is not None
    assert res.cu_pourbaix_note is not None


def test_vertical_ph_matches_module_function_exactly():
    # 팩이 log_a_cu를 선언하지 않으므로 모듈 기본값 -4.0이 쓰인다.
    rr = Recipe(pack="cu_h2o2_bta", time_s=60).resolve()
    out = _cu_pourbaix_diagnostic(rr)
    expected = CUP.cu2_cuoh2_vertical_pH(-4.0)
    assert out["cu_pourbaix_vertical_ph"] == expected
    assert out["cu_pourbaix_triple_point_ph"] == CUP.triple_point_pH(-4.0)


def test_soluble_domain_flips_across_vertical_ph():
    rr = Recipe(pack="cu_h2o2_bta", time_s=60).resolve()
    vert_ph = CUP.cu2_cuoh2_vertical_pH(-4.0)

    rr.pack.params["slurry_ph"].value = vert_ph - 1.0
    out_below = _cu_pourbaix_diagnostic(rr)
    assert out_below["cu_pourbaix_soluble_domain"] is True

    rr.pack.params["slurry_ph"].value = vert_ph + 1.0
    out_above = _cu_pourbaix_diagnostic(rr)
    assert out_above["cu_pourbaix_soluble_domain"] is False


def test_cu_pourbaix_diagnostic_does_not_change_mrr():
    # 이 진단을 계산하든 안 하든 mrr_nm_per_min은 비트 단위로 동일해야 한다 —
    # MRR 경로와 완전히 독립적인 진단이라는 계약.
    r = Recipe(pack="cu_h2o2_bta", time_s=60)
    res_with = simulate(r)

    orig = E._cu_pourbaix_diagnostic
    E._cu_pourbaix_diagnostic = lambda rr: {
        "cu_pourbaix_vertical_ph": None,
        "cu_pourbaix_triple_point_ph": None,
        "cu_pourbaix_soluble_domain": None,
        "cu_pourbaix_note": None,
    }
    try:
        res_without = simulate(r)
    finally:
        E._cu_pourbaix_diagnostic = orig

    assert np.array_equal(res_with.mrr_nm_per_min, res_without.mrr_nm_per_min)
    assert res_without.cu_pourbaix_vertical_ph is None
