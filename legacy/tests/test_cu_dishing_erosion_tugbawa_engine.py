"""cu_dishing_erosion_tugbawa.py 엔진 등록 회귀 — WaferResult 진단 필드 3종
(cu_dishing_tugbawa_nm · cu_erosion_tugbawa_nm · cu_dishing_tugbawa_note).

MRR 경로와 완전히 독립인 진단이다. cu_h2o2_bta 팩 + PTW + meta에 패턴 레이아웃
(pattern_density/linewidth_um/space_um)과 블랭킷 실측(r_cu_angstrom_s/r_ox_angstrom_s)이
전부 있을 때만 채워지고, 그 외엔 조용히 None(지어내지 않는다).
"""
import cu_dishing_erosion_tugbawa as CDE

from sim.engine import Recipe, simulate

FULL_META = {
    "pattern_density": 0.5, "linewidth_um": 1.0, "space_um": 1.0,
    "r_cu_angstrom_s": 159.0, "r_ox_angstrom_s": 2.22,
}


def test_non_cu_pack_leaves_fields_none():
    res = simulate(Recipe(pack="oxide_silica", wafer="PTW", meta=dict(FULL_META)))
    assert res.cu_dishing_tugbawa_nm is None
    assert res.cu_erosion_tugbawa_nm is None
    assert res.cu_dishing_tugbawa_note is None


def test_npw_wafer_leaves_fields_none():
    res = simulate(Recipe(pack="cu_h2o2_bta", wafer="NPW", meta=dict(FULL_META)))
    assert res.cu_dishing_tugbawa_nm is None
    assert res.cu_erosion_tugbawa_nm is None
    assert res.cu_dishing_tugbawa_note is None


def test_ptw_without_layout_meta_skips_with_note():
    res = simulate(Recipe(pack="cu_h2o2_bta", wafer="PTW"))
    assert res.cu_dishing_tugbawa_nm is None
    assert res.cu_erosion_tugbawa_nm is None
    assert res.cu_dishing_tugbawa_note == "PTW 패턴 레이아웃 정보(선폭/스페이스/밀도) 없음 — 계산 스킵"
    assert res.cu_dishing_tugbawa_note in res.notes


def test_ptw_without_removal_rates_skips_with_note_and_no_literature_default():
    meta = {"pattern_density": 0.5, "linewidth_um": 1.0, "space_um": 1.0}
    res = simulate(Recipe(pack="cu_h2o2_bta", wafer="PTW", meta=meta))
    assert res.cu_dishing_tugbawa_nm is None
    assert res.cu_erosion_tugbawa_nm is None
    assert "r_cu_angstrom_s" in res.cu_dishing_tugbawa_note
    assert "r_ox_angstrom_s" in res.cu_dishing_tugbawa_note


def test_ptw_full_meta_matches_module_directly():
    res = simulate(Recipe(pack="cu_h2o2_bta", wafer="PTW", meta=dict(FULL_META)))
    assert res.cu_dishing_tugbawa_nm is not None
    assert res.cu_erosion_tugbawa_nm is not None
    expected = CDE.cu_overpolish_dishing_erosion(
        r_cu=159.0, r_ox_measured=2.22, phi_cu=0.5, w=1.0, s=1.0, t_overpolish=60.0)
    assert abs(res.cu_dishing_tugbawa_nm - expected["dishing_nm"]) < 1e-9
    assert abs(res.cu_erosion_tugbawa_nm - expected["erosion_nm"]) < 1e-9
    s = res.summary()
    assert s["cu_dishing_tugbawa_nm"] == res.cu_dishing_tugbawa_nm
    assert s["cu_erosion_tugbawa_nm"] == res.cu_erosion_tugbawa_nm


def test_ptw_uses_recipe_time_s_as_overpolish_time():
    res30 = simulate(Recipe(pack="cu_h2o2_bta", wafer="PTW", time_s=30.0, meta=dict(FULL_META)))
    res90 = simulate(Recipe(pack="cu_h2o2_bta", wafer="PTW", time_s=90.0, meta=dict(FULL_META)))
    assert res30.cu_erosion_tugbawa_nm < res90.cu_erosion_tugbawa_nm


def test_diagnostic_does_not_affect_mrr():
    base = simulate(Recipe(pack="cu_h2o2_bta", wafer="PTW"))
    with_meta = simulate(Recipe(pack="cu_h2o2_bta", wafer="PTW", meta=dict(FULL_META)))
    assert (base.mrr_nm_per_min == with_meta.mrr_nm_per_min).all()
