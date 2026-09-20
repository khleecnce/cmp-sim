"""ceria_redox_selectivity.py 엔진 등록 회귀 — 세리아 산소공공 x·정전인력 진단(WaferResult 필드 3종).

근거: sim/tier2_physics/ceria_redox_selectivity.py::ce3_fraction/electrostatic_attraction
(원본 무수정), knowledge/cmp/ceria-slurry-ce-redox-selectivity.md §2(전하균형)·§4(IEP 정전인력).

이 진단이 등록 가능해진 이유는 sim/engine.py::_ceria_redox_diagnostic 문서화 참조.
oxide_nitride_selectivity·h2o2_boost_selectivity·is_chemisorption·
chemisorption_energy_kj_mol은 절대 호출하지 않는다 — test_forbidden_functions_never_called이
ast로 기계 고정한다.
"""
import ast
import inspect
import subprocess
from pathlib import Path

import pytest

import sim.engine as E
from sim.engine import Recipe, simulate, _ceria_redox_diagnostic
import ceria_redox_selectivity as CRS

_ALL_PACKS = ["cu_h2o2_bta", "oxide_silica", "sic_ceria_h2o2", "sti_ceria", "w_fe_oxidizer"]


def test_sti_ceria_oxygen_vacancy_x_exact():
    rr = Recipe(pack="sti_ceria", time_s=60).resolve()
    out = _ceria_redox_diagnostic(rr)
    assert out["ceria_oxygen_vacancy_x"] == pytest.approx(0.075, abs=1e-12)


def test_f_equals_2x_roundtrip_identity():
    rr = Recipe(pack="sti_ceria", time_s=60).resolve()
    f = rr.pack.get("ce3_fraction")
    out = _ceria_redox_diagnostic(rr)
    x = out["ceria_oxygen_vacancy_x"]
    assert CRS.ce3_fraction(x) == pytest.approx(f, abs=1e-12)


def test_packs_without_own_ce3_fraction_skip_with_reason():
    for pack in ("cu_h2o2_bta", "oxide_silica", "w_fe_oxidizer", "sic_ceria_h2o2"):
        rr = Recipe(pack=pack, time_s=60).resolve()
        out = _ceria_redox_diagnostic(rr)
        assert out["ceria_oxygen_vacancy_x"] is None, pack
        assert out["ceria_redox_note"] is not None


def test_packs_without_own_iep_pair_skip_electrostatic_with_reason():
    for pack in ("cu_h2o2_bta", "oxide_silica", "w_fe_oxidizer", "sic_ceria_h2o2"):
        rr = Recipe(pack=pack, time_s=60).resolve()
        out = _ceria_redox_diagnostic(rr)
        assert out["ceria_electrostatic_attraction"] is None, pack
        assert out["ceria_redox_note"] is not None


def test_all_five_packs_run_without_exception():
    for pack in _ALL_PACKS:
        r = Recipe(pack=pack, time_s=60)
        res = simulate(r)
        assert res.ceria_redox_note is not None


def test_mrr_unaffected_by_ceria_redox_diagnostic():
    r = Recipe(pack="sti_ceria", pressure_psi=20.7e3 / 6894.757, time_s=60,
               rpm_wafer=60, rpm_platen=60)
    res = simulate(r)
    assert res.mrr_nm_per_min.shape == res.radius_m.shape
    assert (res.mrr_nm_per_min > 0).all()


def test_electrostatic_attraction_value_derived_from_pack_fields():
    # 하드코딩한 기대치가 아니라 sti_ceria 팩에서 직접 읽은 값으로 기대치를 세운다.
    rr = Recipe(pack="sti_ceria", time_s=60).resolve()
    iep_ceria = rr.pack.get("abrasive_iep_ph")
    iep_silica = rr.pack.get("wafer_iep_ph")
    ph = rr.pack.get("slurry_ph")
    expected = CRS.electrostatic_attraction(iep_ceria, iep_silica, ph)
    out = _ceria_redox_diagnostic(rr)
    assert out["ceria_electrostatic_attraction"] == expected


def test_forbidden_functions_never_called():
    tree = ast.parse(inspect.getsource(E))
    called_names = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            fn = node.func
            if isinstance(fn, ast.Name):
                called_names.add(fn.id)
            elif isinstance(fn, ast.Attribute):
                called_names.add(fn.attr)
    forbidden = {"oxide_nitride_selectivity", "h2o2_boost_selectivity",
                 "is_chemisorption", "chemisorption_energy_kj_mol"}
    hit = forbidden & called_names
    assert not hit, (
        f"engine.py가 {hit}를 실제로 호출한다 — oxide_nitride_selectivity/"
        "h2o2_boost_selectivity/is_chemisorption/chemisorption_energy_kj_mol은 실측 "
        "nitride MRR·DFT 흡착에너지 등 이 엔진에 없는 입력이 필요해 지어낸 값으로 "
        "계산한 결과가 제품 출력이 되면 안 된다.")


def test_original_module_untouched():
    result = subprocess.run(
        ["git", "diff", "--stat", "HEAD", "--",
         "sim/tier2_physics/ceria_redox_selectivity.py"],
        capture_output=True, text=True,
        cwd=str(Path(__file__).resolve().parent.parent))
    assert result.stdout.strip() == "", f"원본 모듈이 수정됨: {result.stdout}"
