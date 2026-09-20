"""particle_chemomechanical_synergy.py 엔진 등록 회귀 — WaferResult 진단 필드 4종
(단일 연마입자 소성 접촉/plowing 진단).

근거: sim/tier2_physics/particle_chemomechanical_synergy.py::plastic_plowing(원본 무수정),
knowledge/cmp/particle-wafer-interaction-mechanical-chemical-balance.md §2·§3·§4.
F = P_nominal/η(active_particle_density_per_m2, confidence=estimated), R = abrasive_size_nm/2,
H = film_bulk_hardness_pa. sti_ceria는 film_bulk_hardness_pa를 base(oxide_silica)에서
상속받으므로 현재 5팩 전부 값을 낸다 — 스킵 경로는 팩 키를 인위로 지워야 재현된다.

⛔ chemomechanical_amplification()(H_soft 필요, 5팩 어디에도 없음)은 절대 호출하지 않는다
— 아래 test_amplification_never_called이 grep으로 기계 고정한다.
"""
import ast
import copy
import inspect

import pytest

import sim.engine as E
from sim.engine import Recipe, simulate, _particle_contact_diagnostic, PSI_TO_PA
import particle_chemomechanical_synergy as PCS

_ALL_PACKS = ["cu_h2o2_bta", "oxide_silica", "sic_ceria_h2o2", "sti_ceria", "w_fe_oxidizer"]


def test_all_five_packs_produce_value_or_documented_skip():
    for pack in _ALL_PACKS:
        rr = Recipe(pack=pack, time_s=60).resolve()
        out = _particle_contact_diagnostic(rr)
        assert out["particle_contact_note"] is not None
        has_value = out["particle_load_n"] is not None
        if has_value:
            assert out["particle_indent_depth_nm"] is not None
            assert out["particle_plow_area_nm2"] is not None
        else:
            assert out["particle_indent_depth_nm"] is None
            assert out["particle_plow_area_nm2"] is None
            assert "없음" in out["particle_contact_note"]
    # 현재 지식 상태: sti_ceria가 oxide_silica로부터 film_bulk_hardness_pa를 상속하므로
    # 5팩 전부 값을 낸다(스킵 0건이 정상 — base.yaml/오ide_silica.yaml 확인 결과).
    vals = [_particle_contact_diagnostic(Recipe(pack=p, time_s=60).resolve())["particle_load_n"]
            for p in _ALL_PACKS]
    assert all(v is not None for v in vals)


def test_missing_film_bulk_hardness_pa_skips_with_reason():
    rr = Recipe(pack="oxide_silica", time_s=60).resolve()
    rr.pack = copy.deepcopy(rr.pack)
    del rr.pack.params["film_bulk_hardness_pa"]
    out = _particle_contact_diagnostic(rr)
    assert out["particle_load_n"] is None
    assert out["particle_indent_depth_nm"] is None
    assert out["particle_plow_area_nm2"] is None
    assert "film_bulk_hardness_pa" in out["particle_contact_note"]
    assert "없음" in out["particle_contact_note"]


def test_missing_abrasive_size_nm_skips_with_reason():
    rr = Recipe(pack="oxide_silica", time_s=60).resolve()
    rr.pack = copy.deepcopy(rr.pack)
    del rr.pack.params["abrasive_size_nm"]
    out = _particle_contact_diagnostic(rr)
    assert out["particle_load_n"] is None
    assert "abrasive_size_nm" in out["particle_contact_note"]


def test_missing_active_particle_density_skips_with_reason():
    rr = Recipe(pack="oxide_silica", time_s=60).resolve()
    rr.pack = copy.deepcopy(rr.pack)
    del rr.pack.params["active_particle_density_per_m2"]
    out = _particle_contact_diagnostic(rr)
    assert out["particle_load_n"] is None
    assert "active_particle_density_per_m2" in out["particle_contact_note"]


def test_numeric_identity_reproduces_module_direct_call():
    """F=P/η, R=abrasive_size_nm/2를 넣은 plastic_plowing() 직접 호출과 항등이어야 한다."""
    rr = Recipe(pack="cu_h2o2_bta", time_s=60).resolve()
    out = _particle_contact_diagnostic(rr)
    H = float(rr.p("film_bulk_hardness_pa"))
    R = float(rr.p("abrasive_size_nm")) / 2.0 * 1e-9
    eta = float(rr.p("active_particle_density_per_m2"))
    F_expected = rr.pressure_psi * PSI_TO_PA / eta
    delta_expected, A_expected = PCS.plastic_plowing(F_expected, R, H)
    assert out["particle_load_n"] == pytest.approx(F_expected)
    assert out["particle_indent_depth_nm"] == pytest.approx(delta_expected * 1e9)
    assert out["particle_plow_area_nm2"] == pytest.approx(A_expected * 1e18)


def test_unit_conversion_radius_and_outputs():
    """abrasive_size_nm(직경, nm) -> R(반경, m) 변환과 m->nm 역변환이 맞는지."""
    rr = Recipe(pack="w_fe_oxidizer", time_s=60).resolve()
    diameter_nm = float(rr.p("abrasive_size_nm"))
    out = _particle_contact_diagnostic(rr)
    H = float(rr.p("film_bulk_hardness_pa"))
    eta = float(rr.p("active_particle_density_per_m2"))
    F = rr.pressure_psi * PSI_TO_PA / eta
    R_m = diameter_nm / 2.0 * 1e-9
    delta_p_m, A_f_m2 = PCS.plastic_plowing(F, R_m, H)
    assert out["particle_indent_depth_nm"] == pytest.approx(delta_p_m * 1e9)
    assert out["particle_plow_area_nm2"] == pytest.approx(A_f_m2 * 1e18)
    # nm^2 값이 m^2 값의 1e18배(면적이라 1e9^2)인지 별도로 확인
    assert A_f_m2 * 1e18 == pytest.approx(out["particle_plow_area_nm2"])


def test_mrr_bit_invariant_regardless_of_particle_diagnostic_inputs():
    """particle_contact 진단 입력을 바꿔도(또는 지워도) MRR·제거량은 비트 단위로 불변."""
    base = Recipe(pack="oxide_silica", time_s=60)
    res_base = simulate(base)

    rr_probe = Recipe(pack="oxide_silica", time_s=60).resolve()
    rr_probe.pack = copy.deepcopy(rr_probe.pack)
    del rr_probe.pack.params["film_bulk_hardness_pa"]
    assert _particle_contact_diagnostic(rr_probe)["particle_load_n"] is None

    res_override = simulate(Recipe(pack="oxide_silica", time_s=60,
                                   pack_overrides={"film_bulk_hardness_pa": 1.0}))
    assert (res_base.mrr_nm_per_min == res_override.mrr_nm_per_min).all()
    assert (res_base.removed_nm == res_override.removed_nm).all()
    # 오버라이드로 H를 바꿨으니 particle_indent_depth_nm 자체는 달라져야 한다
    # (진단이 실제로 그 입력을 쓰고 있다는 확인) — 하지만 MRR은 위에서 이미 불변 확인.
    assert res_override.particle_indent_depth_nm != res_base.particle_indent_depth_nm


def test_amplification_never_called():
    """chemomechanical_amplification()은 H_soft(화학연화 후 경도)가 팩에 없어 호출 금지.

    inspect.getsource + ast로 **실제 함수호출 노드**만 본다 — docstring·주석에 함수명을
    설명 목적으로 적는 것(이 파일 자체를 포함)은 오탐이면 안 된다.
    """
    tree = ast.parse(inspect.getsource(E))
    called_names = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            fn = node.func
            if isinstance(fn, ast.Name):
                called_names.add(fn.id)
            elif isinstance(fn, ast.Attribute):
                called_names.add(fn.attr)
    assert "chemomechanical_amplification" not in called_names, (
        "engine.py가 chemomechanical_amplification()을 실제로 호출한다 — H_soft가 어느 "
        "팩에도 없고 노트 §6이 슬러리별 미검증이라 못박았다. 지어낸 화학연화 경도로 계산한 "
        "증폭비가 제품 출력이 되면 안 된다.")


def test_physical_implausibility_warning_fires():
    """δ_p >= R(소성 plowing 근사가 깨짐)일 때 note에 경고가 실제로 실린다."""
    fired = False
    for pack in _ALL_PACKS:
        rr = Recipe(pack=pack, time_s=60).resolve()
        out = _particle_contact_diagnostic(rr)
        if out["particle_indent_depth_nm"] is None:
            continue
        R_nm = float(rr.p("abrasive_size_nm")) / 2.0
        if out["particle_indent_depth_nm"] >= R_nm:
            assert "⚠" in out["particle_contact_note"]
            assert "입자반경" in out["particle_contact_note"]
            fired = True
    assert fired, "현재 5팩 조건에서 최소 1건은 δ_p>=R 경고가 발동해야 하는데 하나도 없었다"


def test_estimated_confidence_not_upgraded():
    """active_particle_density_per_m2의 estimated 출처가 note에 명시되고, confidence 자체는
    이 진단이 손대지 않는다(팩 param 객체 confidence 불변)."""
    rr = Recipe(pack="oxide_silica", time_s=60).resolve()
    before = rr.pack.param("active_particle_density_per_m2").confidence
    out = _particle_contact_diagnostic(rr)
    after = rr.pack.param("active_particle_density_per_m2").confidence
    assert before == after == "estimated"
    assert "estimated" in out["particle_contact_note"]
