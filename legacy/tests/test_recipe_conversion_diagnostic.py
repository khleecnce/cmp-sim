"""recipe_conversion_factor.py 엔진 등록 회귀 — WaferResult 진단 필드 3종
(레시피 전이 work function F(X,Y,Z) 진단).

근거: sim/tier2_physics/recipe_conversion_factor.py::work_function/RECIPE_TABLE
(원본 무수정), knowledge/cmp/product-wafer-proxy-metrics-virtual-metrology.md §2.2·
§6 verify (A). 1차 문헌: US20060116785A1 식(1)·표 1·표 2·청구항 6.

F(X,Y,Z) = work_function(rr.pressure_psi, sfr_ml_min, rr.rpm_platen). sfr_ml_min은
5팩 전부 base.yaml 상속(150.0 mL/min, literature)이라 현재 5팩 전부 값을 낸다 — 스킵
경로는 팩 키를 인위로 지워야 재현된다.

⛔ 원본 모듈 recipe_conversion_factor.py는 1바이트도 수정하지 않는다 — import만.
"""
import copy

import pytest

import sim.engine as E
from sim.engine import Recipe, simulate, _recipe_conversion_diagnostic
import recipe_conversion_factor as RCF

_ALL_PACKS = ["cu_h2o2_bta", "oxide_silica", "sic_ceria_h2o2", "sti_ceria", "w_fe_oxidizer"]


def test_all_five_packs_produce_value_or_documented_skip():
    for pack in _ALL_PACKS:
        rr = Recipe(pack=pack, time_s=60).resolve()
        out = _recipe_conversion_diagnostic(rr)
        assert out["recipe_conversion_note"] is not None
        has_value = out["recipe_work_function"] is not None
        if has_value:
            assert out["recipe_wf_vs_ild_ref"] is not None
        else:
            assert out["recipe_wf_vs_ild_ref"] is None
            assert "없음" in out["recipe_conversion_note"]
    # 현재 지식 상태: 5팩 전부 base.yaml에서 sfr_ml_min을 상속하므로 스킵 0건이 정상.
    vals = [_recipe_conversion_diagnostic(Recipe(pack=p, time_s=60).resolve())["recipe_work_function"]
            for p in _ALL_PACKS]
    assert all(v is not None for v in vals)


def test_missing_sfr_ml_min_skips_with_reason():
    rr = Recipe(pack="oxide_silica", time_s=60).resolve()
    rr.pack = copy.deepcopy(rr.pack)
    del rr.pack.params["sfr_ml_min"]
    out = _recipe_conversion_diagnostic(rr)
    assert out["recipe_work_function"] is None
    assert out["recipe_wf_vs_ild_ref"] is None
    assert "sfr_ml_min" in out["recipe_conversion_note"]
    assert "없음" in out["recipe_conversion_note"]


def test_numeric_identity_reproduces_module_direct_call():
    """F=work_function(P,Y,Z)를 넣은 직접 호출과 항등이어야 한다."""
    rr = Recipe(pack="cu_h2o2_bta", time_s=60).resolve()
    out = _recipe_conversion_diagnostic(rr)
    X = float(rr.pressure_psi)
    Y = float(rr.p("sfr_ml_min"))
    Z = float(rr.rpm_platen)
    F_expected = RCF.work_function(X, Y, Z)
    ild = RCF.RECIPE_TABLE["ILD"]
    F_ild_expected = RCF.work_function(ild["downforce_psi"], ild["slurry_flow_ml_min"],
                                        ild["platen_rpm"])
    assert out["recipe_work_function"] == pytest.approx(F_expected)
    assert out["recipe_wf_vs_ild_ref"] == pytest.approx(F_expected / F_ild_expected)


def test_patent_table2_sti_imd_conversion_factor_reproduced():
    """특허 표 2 재현: ILD 기준 STI 1.12, IMD 1.41 (US20060116785A1). 이 진단이 올바른
    원본 함수·상수를 그대로 참조한다는 유일한 기계적 증거."""
    ild = RCF.RECIPE_TABLE["ILD"]
    sti = RCF.RECIPE_TABLE["STI"]
    imd = RCF.RECIPE_TABLE["IMD"]
    ratio_sti = RCF.recipe_conversion_factor(ild, sti)
    ratio_imd = RCF.recipe_conversion_factor(ild, imd)
    assert ratio_sti == pytest.approx(1.12, abs=0.01)
    assert ratio_imd == pytest.approx(1.41, abs=0.01)


def test_mrr_bit_invariant_regardless_of_recipe_conversion_inputs():
    """recipe_conversion 진단 입력을 바꿔도(또는 지워도) MRR·제거량은 비트 단위로 불변."""
    base = Recipe(pack="oxide_silica", time_s=60)
    res_base = simulate(base)

    rr_probe = Recipe(pack="oxide_silica", time_s=60).resolve()
    rr_probe.pack = copy.deepcopy(rr_probe.pack)
    del rr_probe.pack.params["sfr_ml_min"]
    assert _recipe_conversion_diagnostic(rr_probe)["recipe_work_function"] is None

    res_override = simulate(Recipe(pack="oxide_silica", time_s=60,
                                   pack_overrides={"sfr_ml_min": 300.0}))
    assert (res_base.mrr_nm_per_min == res_override.mrr_nm_per_min).all()
    assert (res_base.removed_nm == res_override.removed_nm).all()
    # 오버라이드로 Y를 바꿨으니 recipe_work_function 자체는 달라져야 한다
    # (진단이 실제로 그 입력을 쓰고 있다는 확인) — 하지만 MRR은 위에서 이미 불변 확인.
    assert res_override.recipe_work_function != res_base.recipe_work_function


def test_out_of_range_extrapolation_warning_fires():
    """현재 5팩(pressure_psi=3.0, rpm_platen=55)은 특허 표1 범위(psi 4.0~4.6, rpm 63~108)
    밖이므로 최소 1건은 외삽 경고가 note에 실제로 실려야 한다."""
    fired = False
    for pack in _ALL_PACKS:
        rr = Recipe(pack=pack, time_s=60).resolve()
        out = _recipe_conversion_diagnostic(rr)
        if out["recipe_work_function"] is None:
            continue
        if "외삽 경고" in out["recipe_conversion_note"]:
            assert "⚠" in out["recipe_conversion_note"]
            fired = True
    assert fired, "현재 5팩 조건에서 최소 1건은 표1 범위 밖 외삽 경고가 발동해야 하는데 하나도 없었다"


def test_original_module_untouched():
    """원본 모듈 recipe_conversion_factor.py는 1바이트도 수정하지 않는다 — git diff가
    비어 있어야 한다(트래킹된 파일 기준)."""
    import subprocess
    result = subprocess.run(
        ["git", "diff", "--stat", "HEAD", "--", "sim/tier2_physics/recipe_conversion_factor.py"],
        capture_output=True, text=True, cwd=str(__import__("pathlib").Path(__file__).resolve().parent.parent))
    assert result.stdout.strip() == "", f"원본 모듈이 수정됨: {result.stdout}"


def test_wf_vs_ild_ref_differs_from_patent_table2_semantics():
    """recipe_wf_vs_ild_ref(현재 런 vs 표1-ILD)는 표 2의 이산 레시피간 비(ILD→STI/IMD)와
    다른 비교라는 note의 명시적 설명이 실제로 실린다."""
    rr = Recipe(pack="oxide_silica", time_s=60).resolve()
    out = _recipe_conversion_diagnostic(rr)
    assert "다른 비교" in out["recipe_conversion_note"] or "표 1의 이산 레시피" in out["recipe_conversion_note"]
