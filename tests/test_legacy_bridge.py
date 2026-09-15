"""The inherited assets must stay importable and loadable — this is the wiring gate."""
from cmp_sim.core import legacy_bridge as lb
from cmp_sim.core.params import ParamMissing, available_packs, load_pack


def test_legacy_tree_is_present():
    assert lb.LEGACY_ROOT.is_dir()
    assert (lb.LEGACY_ROOT / "HANDOVER.md").exists() or (lb.LEGACY_ROOT / "HANDOFF.md").exists()
    assert lb.LEGACY_PACK_DIR.is_dir()
    assert lb.LEGACY_DATASETS.is_dir()


def test_legacy_modules_expose_the_functions_we_wrap():
    assert callable(lb.legacy_preston.mrr_profile)
    assert callable(lb.legacy_preston.wafer_avg_mrr)
    assert callable(lb.legacy_kinematics.relative_velocity)
    assert callable(lb.legacy_wiwnu.wiwnu)
    assert callable(lb.legacy_wiwnu.p_zoned)


def test_inherited_packs_are_visible_through_the_two_tier_loader():
    packs = available_packs()
    for expected in ("base", "oxide_silica", "cu_h2o2_bta", "w_fe_oxidizer", "sti_ceria"):
        assert expected in packs


def test_pack_inheritance_and_provenance():
    pk = load_pack("sti_ceria")
    assert pk.lineage[0] == "base"
    assert pk.get("kp_m_per_pa") > 0
    prov = pk.provenance(["kp_m_per_pa"])
    assert prov["kp_m_per_pa"]["source"]
    assert prov["kp_m_per_pa"]["confidence"] in (
        "verified", "literature", "estimated", "unverified", "unknown")


def test_missing_parameter_raises_instead_of_defaulting():
    import pytest
    pk = load_pack("base")
    with pytest.raises(ParamMissing):
        pk.get("definitely_not_a_real_parameter")
