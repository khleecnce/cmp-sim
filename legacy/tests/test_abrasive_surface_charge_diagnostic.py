"""chelation_surface_charge.py 엔진 등록 회귀 — 연마입자/산화물 표면전하 부호 진단.

근거: sim/tier2_physics/chelation_surface_charge.py::oxide_surface_charge_sign
(원본 무수정), knowledge/cmp/post-cmp-adsorption-cleaning-chemistry.md §3·§6(C)·§7.

이 진단이 등록 가능해진 이유: 모듈 docstring의 미등록 사유("Recipe에 pH·이온세기·
킬레이트 농도 필드가 없다")는 절반만 맞다 — slurry_ph·abrasive는 5팩 전부에 있어
oxide_surface_charge_sign(oxide, pH)은 지금 계산 가능하다. 이온세기·킬레이트 농도가
필요한 나머지 함수(chelation_conditional_logK 등)는 여전히 입력이 없어 호출하지
않는다(test_forbidden_functions_never_called이 ast로 고정).

절대값을 못 박는다 — 상대적 성질만 보는 테스트는 GW β 역수 누락으로 분리거리가
21.6 km로 풀린 사례를 8건 전부 통과시킨 전례가 있다(엔진 주석 참조).
"""
import ast
import inspect
import math

import numpy as np
import pytest

import sim.engine as E
from sim.engine import Recipe, simulate, _abrasive_surface_charge_diagnostic
from sim.params import Param
import chelation_surface_charge as CSC

_ALL_PACKS = ["cu_h2o2_bta", "oxide_silica", "sic_ceria_h2o2", "sti_ceria", "w_fe_oxidizer"]

# Max워커 사전계산 — pack -> (abrasive, slurry_ph, expected sign)
_EXPECTED_SIGN = {
    "cu_h2o2_bta": "+",       # alumina, pH 4.0 < IEP 9.5
    "oxide_silica": "-",      # silica, pH 10.5 > IEP 2.0
    "sic_ceria_h2o2": "-",    # ceria, pH 10.0 > IEP 6.8
    "sti_ceria": "+",         # ceria, pH 5.5 < IEP 6.8
    "w_fe_oxidizer": "+",     # alumina, pH 2.5 < IEP 9.5
}


def test_all_five_packs_produce_exact_expected_sign():
    for pack in _ALL_PACKS:
        res = simulate(Recipe(pack=pack, time_s=60))
        assert res.abrasive_surface_charge_sign == _EXPECTED_SIGN[pack], pack
        assert res.abrasive_surface_charge_note is not None, pack


def test_literature_iep_values_exact():
    """문헌표(CSC.IEP) 값을 그대로 재현 — SiO2=2.0, CeO2=6.8, Al2O3=9.5."""
    expected_iep = {
        "cu_h2o2_bta": 9.5,
        "oxide_silica": 2.0,
        "sic_ceria_h2o2": 6.8,
        "sti_ceria": 6.8,
        "w_fe_oxidizer": 9.5,
    }
    for pack, iep in expected_iep.items():
        rr = Recipe(pack=pack, time_s=60).resolve()
        out = _abrasive_surface_charge_diagnostic(rr)
        assert out["abrasive_iep_literature_ph"] == pytest.approx(iep), pack


def test_oxide_silica_deviation_is_plus_half():
    """oxide_silica는 팩 선언 IEP(2.5) - 문헌 IEP(2.0) = +0.5 pH 괴리를 노출한다."""
    rr = Recipe(pack="oxide_silica", time_s=60).resolve()
    out = _abrasive_surface_charge_diagnostic(rr)
    assert out["abrasive_iep_pack_deviation_ph"] == pytest.approx(0.5)
    assert "0.5" in out["abrasive_surface_charge_note"] or "+0.50" in out["abrasive_surface_charge_note"]


def test_ceria_packs_deviation_is_zero():
    """sti_ceria·sic_ceria_h2o2는 팩 선언 IEP와 문헌 CeO2=6.8이 정확히 일치한다."""
    for pack in ("sti_ceria", "sic_ceria_h2o2"):
        rr = Recipe(pack=pack, time_s=60).resolve()
        out = _abrasive_surface_charge_diagnostic(rr)
        assert out["abrasive_iep_pack_deviation_ph"] == pytest.approx(0.0)


def test_alumina_packs_have_no_pack_iep_but_sign_still_computed():
    """cu_h2o2_bta·w_fe_oxidizer는 abrasive_iep_ph 미선언 — deviation은 None이지만
    부호는 나온다(기존 _colloid_stability_diagnostic이 스킵하던 팩을 새로 커버)."""
    for pack in ("cu_h2o2_bta", "w_fe_oxidizer"):
        rr = Recipe(pack=pack, time_s=60).resolve()
        assert not rr.pack.has("abrasive_iep_ph"), pack
        # 기존 콜로이드 진단은 이 팩들을 스킵한다는 것을 대조로 고정
        res = simulate(Recipe(pack=pack, time_s=60))
        assert res.colloid_stability_note is None, pack
        out = _abrasive_surface_charge_diagnostic(rr)
        assert out["abrasive_iep_pack_deviation_ph"] is None, pack
        assert out["abrasive_surface_charge_sign"] == _EXPECTED_SIGN[pack], pack


def test_ceo2_range_lower_bound_flips_sti_ceria_sign():
    """CeO2 실측범위 하한(5.21)을 쓰면 sti_ceria(pH 5.5) 부호가 '+'→'-'로 뒤집힌다.

    5.5 > 5.21 이므로 IEP가 하한까지 내려가면 표면전하 부호가 반대가 된다 —
    단일값 6.8 판정의 취약성을 직접 재현해 note에 남긴다.
    """
    rr = Recipe(pack="sti_ceria", time_s=60).resolve()
    ph = float(rr.p("slurry_ph"))
    lo, hi = CSC.CEO2_IEP_LIT_RANGE
    assert lo == pytest.approx(5.21)
    assert ph > lo  # 5.5 > 5.21
    sign_at_68 = "+" if ph < 6.8 else ("-" if ph > 6.8 else "0")
    sign_at_lo = "+" if ph < lo else ("-" if ph > lo else "0")
    assert sign_at_68 == "+"
    assert sign_at_lo == "-"
    assert sign_at_68 != sign_at_lo
    out = _abrasive_surface_charge_diagnostic(rr)
    assert "뒤집힌다" in out["abrasive_surface_charge_note"]


def test_unmapped_abrasive_skips_without_inventing():
    """abrasive를 표에 없는 값(zirconia)으로 오버라이드하면 전부 None + 사유."""
    rr = Recipe(pack="cu_h2o2_bta", time_s=60).resolve()
    rr.pack.params["abrasive"] = Param(
        key="abrasive", value="zirconia", unit=None,
        source="test-probe", confidence="estimated")
    out = _abrasive_surface_charge_diagnostic(rr)
    assert out["abrasive_surface_charge_sign"] is None
    assert out["abrasive_iep_literature_ph"] is None
    assert out["abrasive_iep_pack_deviation_ph"] is None
    assert "zirconia" in out["abrasive_surface_charge_note"]
    assert "스킵" in out["abrasive_surface_charge_note"]


def test_missing_slurry_ph_or_abrasive_skips():
    rr = Recipe(pack="cu_h2o2_bta", time_s=60).resolve()
    rr.pack.params.pop("slurry_ph", None)
    out = _abrasive_surface_charge_diagnostic(rr)
    assert out["abrasive_surface_charge_sign"] is None
    assert "스킵" in out["abrasive_surface_charge_note"]


def test_bulk_powder_warning_propagated():
    """모듈 §7 경고(벌크 분말/유리 표면값, CMP 후 실제 박막 IEP 미확보)를 전파한다."""
    res = simulate(Recipe(pack="cu_h2o2_bta", time_s=60))
    assert "벌크 분말" in res.abrasive_surface_charge_note
    assert "박막" in res.abrasive_surface_charge_note


def test_glycine_not_in_module_ligand_table():
    """cu_h2o2_bta가 선언한 chelator_species=glycine은 모듈 리간드 표에 없다.

    글리신을 EDTA/시트르산으로 대체하는 것은 근거 없는 치환이므로, 이 진단은
    킬레이트 관련 함수를 아예 호출하지 않는다(아래 ast 테스트가 기계 고정).
    """
    rr = Recipe(pack="cu_h2o2_bta", time_s=60).resolve()
    assert rr.p("chelator_species") == "glycine"
    assert "glycine" not in CSC.K0            # {"EDTA": ..., "Cit": ...}
    assert "glycine" not in CSC.BETAS


def test_forbidden_functions_never_called():
    """이온세기·킬레이트 농도 경로, DHF 세정 경로 함수는 engine.py 어디서도 호출되지 않는다.

    - chelation_conditional_logK/logK_at_I/log_alpha_H/free_metal_fraction: 이온세기 I·
      킬레이트 리간드 농도가 Recipe·팩 어디에도 없다. cu_h2o2_bta의 chelator_species=
      glycine도 모듈 리간드 표(EDTA·Cit)에 없어 대체할 근거가 없다.
    - hf_solution_pH: DHF 세정 공정변수(HF wt%)가 Recipe에 없고, 이 엔진은 연마
      단계를 모사하지 세정 단계를 모사하지 않는다.
    """
    tree = ast.parse(inspect.getsource(E))
    called = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            fn = node.func
            if isinstance(fn, ast.Name):
                called.add(fn.id)
            elif isinstance(fn, ast.Attribute):
                called.add(fn.attr)
    forbidden = {"chelation_conditional_logK", "logK_at_I", "log_alpha_H",
                 "free_metal_fraction", "hf_solution_pH"}
    hit = forbidden & called
    assert not hit, f"engine.py가 {hit}를 호출한다 — 입력 미확보 상태에서 지어낸 경로다"


def test_diagnostic_does_not_change_mrr():
    r = Recipe(pack="sti_ceria", time_s=60)
    res_ref = simulate(r)

    orig = E._abrasive_surface_charge_diagnostic
    E._abrasive_surface_charge_diagnostic = lambda rr: {
        "abrasive_surface_charge_sign": "0",
        "abrasive_iep_literature_ph": 999.0,
        "abrasive_iep_pack_deviation_ph": 999.0,
        "abrasive_surface_charge_note": "test-probe",
    }
    try:
        res_forced = simulate(r)
    finally:
        E._abrasive_surface_charge_diagnostic = orig

    assert np.array_equal(res_ref.mrr_nm_per_min, res_forced.mrr_nm_per_min)
    assert np.array_equal(res_ref.remaining_nm, res_forced.remaining_nm)
    assert res_forced.abrasive_surface_charge_sign == "0"


def _git_diff_clean_or_skip(paths, label):
    """워킹트리에서 `git diff --quiet <paths>` 를 검사한다.

    ⚠ `.githooks/pre-push`는 `git archive HEAD | tar -x`로 만든 임시 디렉토리
    (git 워킹트리가 아님)에서 테스트를 돌리므로, 거기선 `git diff`가 128을 반환해
    무조건 실패한다 — is-inside-work-tree를 먼저 확인해 그 환경에서는 skip한다.
    """
    import subprocess
    root = E.__file__.rsplit("/sim/", 1)[0]
    inside = subprocess.run(["git", "rev-parse", "--is-inside-work-tree"],
                            cwd=root, capture_output=True, text=True)
    if inside.returncode != 0 or inside.stdout.strip() != "true":
        pytest.skip("git 워킹트리가 아님(pre-push archive 등) — 원본 무수정 검사 스킵")
    result = subprocess.run(["git", "diff", "--quiet", "--"] + list(paths), cwd=root)
    assert result.returncode == 0, f"{label}에 diff가 있다 — 원본 무수정 위반"


def test_original_chelation_surface_charge_module_unmodified():
    _git_diff_clean_or_skip(
        ["sim/tier2_physics/chelation_surface_charge.py"],
        "chelation_surface_charge.py")
