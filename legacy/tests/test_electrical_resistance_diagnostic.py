"""electrical_thickness_extraction.py 엔진 등록 회귀 — WaferResult 진단 필드 3종
(Cu dishing 선저항 증가율 진단, dishing_delta_R_fraction).

근거: sim/tier2_physics/electrical_thickness_extraction.py::dishing_delta_R_fraction
(원본 무수정), Chang, Cao, Spanos, IEEE TED 51(10) 1577-1583 (2004),
doi.org/10.1109/TED.2004.834898 표 I·Fig.6.

이 진단은 cu_thickness_from_resistance(실측 R -> 두께 역산, 여전히 미등록)와는 별개다 —
dishing_delta_R_fraction은 실측 R이 필요 없는 순방향 예측이라 등록 가능해졌다. film=="cu"
(데이터 필드 판별) + linewidth_um(meta) + remaining_nm(initial_thickness_nm 설정 시에만
존재) 셋 다 있어야 값을 낸다. 현재 5팩 기본 실행은 linewidth_um을 선언하지 않아 항상
None(스킵)이 정상이다 — 스킵 경로는 meta를 인위로 채워야 재현된다.

⛔ 원본 모듈 electrical_thickness_extraction.py는 1바이트도 수정하지 않는다 — import만.
"""
import pytest

import sim.engine as E
from sim.engine import Recipe, simulate, _electrical_resistance_diagnostic
import electrical_thickness_extraction as ETE

_ALL_PACKS = ["cu_h2o2_bta", "oxide_silica", "sic_ceria_h2o2", "sti_ceria", "w_fe_oxidizer"]


def test_default_five_packs_all_skip_with_reason():
    """현재 지식 상태: 5팩 어디에도 linewidth_um meta가 없어 전부 스킵이 정상."""
    for pack in _ALL_PACKS:
        rr = Recipe(pack=pack, time_s=60).resolve()
        out = _electrical_resistance_diagnostic(rr, None)
        assert out["electrical_dishing_delta_r_pct"] is None
        assert out["electrical_dishing_r_dish_um"] is None
        assert out["electrical_resistance_note"] is not None


def test_non_cu_film_skips_even_with_full_meta():
    """film != 'cu'면 linewidth_um·initial_thickness_nm을 다 채워도 스킵(선저항 모델은
    금속 배선 전용)."""
    res = simulate(Recipe(pack="oxide_silica", time_s=60, initial_thickness_nm=800.0,
                          meta={"linewidth_um": 1.0}))
    assert res.electrical_dishing_delta_r_pct is None
    assert "cu" in res.electrical_resistance_note.lower() or "Cu" in res.electrical_resistance_note
    assert res.electrical_resistance_note in res.notes


def test_cu_missing_linewidth_skips_with_reason():
    rr = Recipe(pack="cu_h2o2_bta", time_s=60, initial_thickness_nm=800.0).resolve()
    out = _electrical_resistance_diagnostic(rr, None)
    assert out["electrical_dishing_delta_r_pct"] is None
    assert "linewidth_um" in out["electrical_resistance_note"]


def test_cu_missing_initial_thickness_skips_with_reason():
    """initial_thickness_nm 미지정이면 simulate()의 remaining이 None이라 진단도 None을 받는다."""
    res = simulate(Recipe(pack="cu_h2o2_bta", time_s=60, meta={"linewidth_um": 1.0}))
    assert res.remaining_nm is None
    assert res.electrical_dishing_delta_r_pct is None
    assert "initial_thickness_nm" in res.electrical_resistance_note

    rr = Recipe(pack="cu_h2o2_bta", time_s=60, meta={"linewidth_um": 1.0}).resolve()
    out = _electrical_resistance_diagnostic(rr, None)
    assert out["electrical_dishing_delta_r_pct"] is None
    assert "initial_thickness_nm" in out["electrical_resistance_note"]


def test_cu_full_inputs_produce_value_matching_module_directly():
    import numpy as np

    recipe = Recipe(pack="cu_h2o2_bta", time_s=60, initial_thickness_nm=800.0,
                    meta={"linewidth_um": 5.0})
    res = simulate(recipe)
    assert res.electrical_dishing_delta_r_pct is not None
    assert res.electrical_dishing_r_dish_um == pytest.approx(40.0)
    t_um = float(np.mean(res.remaining_nm)) / 1000.0
    expected = ETE.dishing_delta_R_fraction(5.0, R_dish_um=40.0, t_um=t_um)
    assert res.electrical_dishing_delta_r_pct == pytest.approx(expected)


def test_patent_table1_reproduced_via_module_self_test_values():
    """Chang et al. 2004 표 I 재현: 모듈 자체 _self_test()가 이미 검증한 문헌값을
    그대로 재사용(수치를 새로 발명하지 않는다). w=5,4,3,2 um 전부 30% 이내."""
    table_i = [(5, 9.39), (4, 6.67), (3, 4.74), (2, 1.56)]
    for w, lit in table_i:
        model_val = ETE.dishing_delta_R_fraction(w)
        assert abs(model_val - lit) / lit < 0.30


def test_mrr_bit_invariant_regardless_of_electrical_inputs():
    """electrical_resistance 진단 입력(meta/initial_thickness_nm)을 바꿔도 MRR·제거량은
    비트 단위로 불변."""
    base = simulate(Recipe(pack="cu_h2o2_bta", time_s=60))
    with_full = simulate(Recipe(pack="cu_h2o2_bta", time_s=60, initial_thickness_nm=800.0,
                                meta={"linewidth_um": 5.0}))
    assert (base.mrr_nm_per_min == with_full.mrr_nm_per_min).all()

    with_diff_linewidth = simulate(Recipe(pack="cu_h2o2_bta", time_s=60,
                                          initial_thickness_nm=800.0,
                                          meta={"linewidth_um": 1.0}))
    assert (with_full.mrr_nm_per_min == with_diff_linewidth.mrr_nm_per_min).all()
    assert (with_full.removed_nm == with_diff_linewidth.removed_nm).all()
    # 오버라이드로 linewidth를 바꿨으니 진단값 자체는 달라져야 한다(입력을 실제로 쓴다는 확인).
    assert with_full.electrical_dishing_delta_r_pct != with_diff_linewidth.electrical_dishing_delta_r_pct


def test_forbidden_functions_never_called():
    """cu_thickness_from_resistance·liner_*(실측 R·라이너 두께 필요, 지어내야 함)는
    engine.py 어디서도 실제로 호출되지 않는다.

    inspect.getsource + ast로 **실제 함수호출 노드**만 본다 — docstring·주석에 함수명을
    설명 목적으로 적는 것(이 진단 자체의 docstring을 포함)은 오탐이면 안 된다
    (particle_chemomechanical_synergy의 test_amplification_never_called 선례와 동일 패턴).
    """
    import ast
    import inspect

    tree = ast.parse(inspect.getsource(E))
    called_names = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            fn = node.func
            if isinstance(fn, ast.Name):
                called_names.add(fn.id)
            elif isinstance(fn, ast.Attribute):
                called_names.add(fn.attr)
    forbidden = {"cu_thickness_from_resistance", "liner_parallel_resistance_ratio",
                "liner_neglect_error_fraction", "is_liner_negligible"}
    hit = forbidden & called_names
    assert not hit, (
        f"engine.py가 {hit}를 실제로 호출한다 — 실측 선저항 R·라이너 두께가 어느 팩에도 "
        "없어 지어낸 값으로 계산한 결과가 제품 출력이 되면 안 된다.")


def test_original_module_untouched():
    """원본 모듈 electrical_thickness_extraction.py는 1바이트도 수정하지 않는다 — git diff가
    비어 있어야 한다(트래킹된 파일 기준)."""
    import subprocess
    result = subprocess.run(
        ["git", "diff", "--stat", "HEAD", "--",
         "sim/tier2_physics/electrical_thickness_extraction.py"],
        capture_output=True, text=True,
        cwd=str(__import__("pathlib").Path(__file__).resolve().parent.parent))
    assert result.stdout.strip() == "", f"원본 모듈이 수정됨: {result.stdout}"
