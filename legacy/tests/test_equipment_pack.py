"""장비팩(컨디셔너 디스크) 계약 테스트 — 백로그 ㉺, S12-RESIDUAL-JUDGMENT.md §2-2.

지키는 것:
  1. 장비팩은 화학 팩과 완전히 분리된 로더·디렉토리로 산다(available_packs()에 안 섞임).
  2. 3M E187 TDS 표 값만 실려 있고, 지어낸 값(grit_density_per_cm2/Rpk/engage_depth_um)은
     조회 시 ParamMissing이 뜬다 — 조용한 기본값 없음.
  3. Recipe.conditioner_disk는 선택 필드다. None이면(기본값) MRR이 확장 전과 비트 단위
     불변이고, 값을 줘도(스키마만 세우는 회차라) MRR은 여전히 비트 단위 불변이다.
"""
import sys
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from sim.equipment import load_equipment_pack, available_equipment_packs  # noqa: E402
from sim.params import ParamMissing, available_packs  # noqa: E402
from sim.engine import Recipe, simulate  # noqa: E402
import sim.models  # noqa: E402,F401  (모델 등록)


def test_both_disk_packs_load_with_fixed_grit_size():
    for name in ("3m_e187_260mm", "3m_e187_360mm"):
        pk = load_equipment_pack(name)
        assert pk.get("grit_nominal_size_um") == 181.0


def test_aggressiveness_differs_between_260mm_and_360mm():
    """TDS 표: 260mm 70-90 vs 360mm 55-75 — 캐리어 직경별로 다른 재현."""
    p260 = load_equipment_pack("3m_e187_260mm")
    p360 = load_equipment_pack("3m_e187_360mm")
    assert p260.get("aggressiveness_value_bl_min") != p360.get("aggressiveness_value_bl_min")
    assert p260.get("aggressiveness_value_bl_max") != p360.get("aggressiveness_value_bl_max")
    assert p260.get("aggressiveness_value_bl_min") > p360.get("aggressiveness_value_bl_min")


@pytest.mark.parametrize("key", ["grit_density_per_cm2", "Rpk", "engage_depth_um"])
def test_unconfirmed_fields_raise_not_guess(key):
    """TDS에 없는 값은 지어내지 않는다 — 조회하면 ParamMissing."""
    pk = load_equipment_pack("3m_e187_260mm")
    with pytest.raises(ParamMissing):
        pk.get(key)


def test_unknown_pack_name_raises_clear_error():
    with pytest.raises(FileNotFoundError):
        load_equipment_pack("존재하지_않는_디스크_팩")


def test_available_equipment_packs_lists_both():
    packs = available_equipment_packs()
    assert set(packs) == {"3m_e187_260mm", "3m_e187_360mm"}


def test_chemistry_packs_not_polluted_by_equipment_packs():
    """available_packs()(화학 팩) 결과에 장비팩이 섞이면 안 된다."""
    chem = available_packs()
    assert "3m_e187_260mm" not in chem
    assert "3m_e187_360mm" not in chem


def test_recipe_default_conditioner_disk_is_none():
    assert Recipe().conditioner_disk is None


def test_mrr_unchanged_when_conditioner_disk_none():
    r = Recipe(pack="oxide_silica", time_s=60.0)
    res = simulate(r)
    r2 = Recipe(pack="oxide_silica", time_s=60.0, conditioner_disk=None)
    res2 = simulate(r2)
    assert (res.mrr_nm_per_min == res2.mrr_nm_per_min).all()
    assert res.conditioner_disk_pack is None
    assert res.conditioner_disk_note is None


def test_mrr_unchanged_when_conditioner_disk_given():
    """장비팩을 지정해도(스키마만 세우는 회차) MRR은 비트 단위 불변이어야 한다."""
    baseline = simulate(Recipe(pack="oxide_silica", time_s=60.0))
    with_disk = simulate(Recipe(pack="oxide_silica", time_s=60.0,
                                conditioner_disk="3m_e187_260mm"))
    assert (baseline.mrr_nm_per_min == with_disk.mrr_nm_per_min).all()
    assert with_disk.conditioner_disk_pack == "3m_e187_260mm"
    assert with_disk.conditioner_disk_note is not None


def test_unknown_conditioner_disk_name_raises():
    with pytest.raises(FileNotFoundError):
        simulate(Recipe(pack="oxide_silica", conditioner_disk="없는_디스크"))
