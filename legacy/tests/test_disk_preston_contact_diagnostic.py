"""disk_preston_contact_decomposition.py 엔진 등록 회귀 — 디스크 접촉통계(η_c, A_f) 진단.

근거: sim/tier2_physics/disk_preston_contact_decomposition.py::eta_over_af(원본 무수정),
sim/tier2_physics/gw_pressure_solve.py::local_contact_state, gw_contact.py(둘 다 원본
무수정, _gw_contact_state_diagnostic과 동일 경로 재사용),
knowledge/materials/disk-design-pad-roughness-asperity-relation.md §2.3·§3.4(b).

이 모듈은 스스로 "K_p ∝ η_c/A_f 단순 비례식은 어느 출처도 회귀하지 않은 PROVISIONAL
가정"이라고 자백한다 — 그래서 이 진단은 preston_coefficient_contact_scaling·
disk_preston_contact_scaling을 호출하지 않고(ast로 기계 고정) η_c/A_f 절대 지표만
낸다. 기준 디스크 스펙(disk_*_ref류)이 5팩 어디에도 없어 scale_factor는 항상 None.

절대 스케일을 못 박는다 — 상대적 성질만 보는 테스트는 GW β 역수 누락으로 분리거리가
21.6 km로 풀린 사례를 8건 전부 통과시킨 전례가 있다(엔진 주석 참조). Max워커 사전계산
GW 런타임 해(oxide_silica, 3 psi, base.yaml 상속): d=7.618088e-06 m,
A_f(=A_r/A_n)=1.392942e-03, n_contacts=443.387185567497, A_n=1e-4 m^2.
"""
import ast
import inspect
import math

import numpy as np
import pytest

import sim.engine as E
from sim.engine import (
    Recipe, simulate, _disk_preston_contact_diagnostic, _gw_contact_state_diagnostic,
    PSI_TO_PA,
)
from sim.params import available_packs, Param
import gw_pressure_solve as GWP
import disk_preston_contact_decomposition as DPC

_ALL_PACKS = [p for p in available_packs() if p != "base"]

_EXPECTED_A_N = 1e-4          # m^2, base.yaml pad_nominal_area_m2
_EXPECTED_N_CONTACTS = 443.387185567497
_EXPECTED_A_F = 1.392942e-03
_EXPECTED_ETA_C = _EXPECTED_N_CONTACTS / _EXPECTED_A_N
_EXPECTED_ETA_OVER_AF = _EXPECTED_ETA_C / _EXPECTED_A_F


def test_all_packs_eta_over_af_filled_and_absolute_scale_fixed():
    # GW 파라미터는 base.yaml 상속이라 전 팩이 같은 절대값이어야 한다(21,600km 오답이
    # 상대 테스트만으로 8건 통과한 전례 있어 상대비교만으로 두지 않는다).
    for pack in _ALL_PACKS:
        rr = Recipe(pack=pack, time_s=60).resolve()
        out = _disk_preston_contact_diagnostic(rr)
        assert out["disk_contact_eta_over_af"] is not None, pack
        assert out["disk_contact_eta_over_af"] == pytest.approx(
            _EXPECTED_ETA_OVER_AF, rel=1e-6), pack
        assert out["disk_preston_contact_note"] is not None, pack


def test_eta_c_computed_directly_from_a_n_and_n_contacts():
    rr = Recipe(pack="oxide_silica", time_s=60).resolve()
    A_n = rr.p("pad_nominal_area_m2")
    assert A_n == pytest.approx(_EXPECTED_A_N)
    out = _disk_preston_contact_diagnostic(rr)
    assert out["disk_contact_eta_c_m2"] == pytest.approx(_EXPECTED_ETA_C, rel=1e-6)
    # η_c/A_f는 반드시 원본 eta_over_af() 함수로 재현되어야 한다(직접 나눗셈 재구현 금지)
    assert out["disk_contact_eta_over_af"] == pytest.approx(
        DPC.eta_over_af(out["disk_contact_eta_c_m2"], out["disk_contact_a_f"]), rel=1e-12)


def test_a_f_matches_gw_contact_state_diagnostic_exactly():
    # 같은 문서 안에서 두 진단이 다른 접촉면적을 내면 모순이다 — 정확히 같은 값이어야 한다.
    for pack in _ALL_PACKS:
        rr = Recipe(pack=pack, time_s=60).resolve()
        disk_out = _disk_preston_contact_diagnostic(rr)
        gw_out = _gw_contact_state_diagnostic(rr)
        assert disk_out["disk_contact_a_f"] == gw_out["gw_real_contact_area_ratio"], pack
        assert disk_out["disk_contact_a_f"] == pytest.approx(_EXPECTED_A_F, rel=1e-6), pack


def test_none_when_gw_pad_params_missing():
    rr = Recipe(pack="oxide_silica", time_s=60).resolve()
    del rr.pack.params["pad_E_star_pa"]
    out = _disk_preston_contact_diagnostic(rr)
    assert out["disk_contact_eta_c_m2"] is None
    assert out["disk_contact_a_f"] is None
    assert out["disk_contact_eta_over_af"] is None
    assert "pad_E_star_pa" in out["disk_preston_contact_note"]


def test_none_when_distribution_not_exponential():
    rr = Recipe(pack="oxide_silica", time_s=60).resolve()
    rr.pack.params["asperity_height_distribution"] = Param(
        key="asperity_height_distribution", value="gaussian", unit="-",
        source="test-probe", confidence="estimated")
    out = _disk_preston_contact_diagnostic(rr)
    assert out["disk_contact_eta_c_m2"] is None
    assert out["disk_contact_a_f"] is None
    assert out["disk_contact_eta_over_af"] is None
    assert "exponential" in out["disk_preston_contact_note"]


def test_scale_factor_always_none_no_reference_disk_declared():
    # 5팩 어디에도 기준 디스크 스펙(disk_*_ref류)이 없다(grep 확인) — 임의 기준을 지어내
    # 배율을 만들지 않는다. eta_over_af는 채워지는데 scale_factor만 None인 것을 확인.
    for pack in _ALL_PACKS:
        rr = Recipe(pack=pack, time_s=60).resolve()
        out = _disk_preston_contact_diagnostic(rr)
        assert out["disk_contact_eta_over_af"] is not None, pack
        assert out["disk_contact_scale_factor"] is None, pack
        assert "기준 디스크" in out["disk_preston_contact_note"]


def test_forbidden_functions_never_called():
    """PROVISIONAL 선형가정으로 Kp를 실제 스케일하는 함수·파편분리 함수는 호출하지 않는다.

    - preston_coefficient_contact_scaling / disk_preston_contact_scaling: "K_p ∝ η_c/A_f"
      선형가정(비례상수·지수 미검증)의 산물을 실제로 만들어낸다 — 진단만 낼 거면 부를
      이유가 없다.
    - fragment_contact_separation: 입력 a_f_intrinsic(파편 없는 고유 실접촉면적)이
      Recipe·팩·GW 해 어디에도 없다.
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
    forbidden = {"preston_coefficient_contact_scaling", "disk_preston_contact_scaling",
                 "fragment_contact_separation"}
    hit = forbidden & called
    assert not hit, f"engine.py가 {hit}를 호출한다 — PROVISIONAL 선형가정을 실제 스케일에 쓴다"


def test_diagnostic_does_not_change_mrr():
    r = Recipe(pack="oxide_silica", time_s=60)
    res_ref = simulate(r)

    orig = E._disk_preston_contact_diagnostic
    E._disk_preston_contact_diagnostic = lambda rr: {
        "disk_contact_eta_c_m2": 999.0,
        "disk_contact_a_f": 999.0,
        "disk_contact_eta_over_af": 999.0,
        "disk_contact_scale_factor": 999.0,
        "disk_preston_contact_note": "test-probe",
    }
    try:
        res_forced = simulate(r)
    finally:
        E._disk_preston_contact_diagnostic = orig

    assert np.array_equal(res_ref.mrr_nm_per_min, res_forced.mrr_nm_per_min)
    assert np.array_equal(res_ref.remaining_nm, res_forced.remaining_nm)
    assert res_forced.disk_contact_eta_over_af == 999.0


def test_all_packs_full_simulate_wires_the_field():
    for pack in _ALL_PACKS:
        res = simulate(Recipe(pack=pack, time_s=60))
        assert res.disk_contact_eta_over_af is not None
        assert res.disk_contact_eta_over_af == pytest.approx(_EXPECTED_ETA_OVER_AF, rel=1e-6)
        assert res.disk_contact_scale_factor is None
        assert res.disk_preston_contact_note is not None


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


def test_original_disk_preston_contact_module_unmodified():
    _git_diff_clean_or_skip(
        ["sim/tier2_physics/disk_preston_contact_decomposition.py"],
        "disk_preston_contact_decomposition.py")


def test_original_gw_modules_unmodified():
    _git_diff_clean_or_skip(
        ["sim/tier2_physics/gw_pressure_solve.py", "sim/tier2_physics/gw_contact.py"],
        "gw_pressure_solve.py/gw_contact.py")


def test_local_contact_state_reused_matches_manual_solve():
    # eta_over_af가 gw_pressure_solve.local_contact_state를 실제로 재사용하는지 대조
    rr = Recipe(pack="oxide_silica", time_s=60).resolve()
    E_star = rr.p("pad_E_star_pa")
    R = rr.p("pad_asperity_radius_m")
    beta = 1.0 / rr.p("pad_height_beta_inv_m")
    eta = rr.p("pad_asperity_density_m2")
    A_n = rr.p("pad_nominal_area_m2")
    P_center = rr.pressure_psi * PSI_TO_PA
    state = GWP.local_contact_state(P_center, A_n, beta, eta, E_star, R)
    assert state["n_contacts"] == pytest.approx(_EXPECTED_N_CONTACTS, rel=1e-9)
    assert state["contact_area_fraction"] == pytest.approx(_EXPECTED_A_F, rel=1e-6)

    out = _disk_preston_contact_diagnostic(rr)
    assert out["disk_contact_eta_c_m2"] == pytest.approx(
        state["n_contacts"] / A_n, rel=1e-12)
    assert out["disk_contact_a_f"] == pytest.approx(state["contact_area_fraction"], rel=1e-12)
