"""tribology_basics.py 엔진 등록 회귀 — Archard↔Preston 가교 진단(WaferResult 필드 5종).

근거: sim/tier2_physics/tribology_basics.py::archard_wear_depth/hersey_number
(원본 무수정), knowledge/physics/tribology-friction-wear-stribeck.md §"Archard 오더 대조"
(연강 pin-on-disk 예시 k=1e-3). k = Kp·H(무차원 Archard 마모계수 환산)는 새 물리가 아니라
기존 Kp를 문헌 공통 척도로 옮겨 오더 타당성만 보는 가시화다 — 어떤 팩터의 confidence도
올리지 않는다. Hersey 수는 관례상 차원이 모호해(모듈 docstring 자백) 오더 확인용으로만
낸다(slurry_viscosity_pa_s가 있는 팩만).

⛔ stribeck_cof(alpha=50.0 등 근거 없는 정성 파라미터, cof_stribeck_estimate와 중복)·
archard_wear_volume(하중 W·미끄럼거리 L 절대값이 Recipe에 없음)은 절대 호출하지 않는다
— test_forbidden_functions_never_called이 ast로 기계 고정한다.
"""
import ast
import copy
import inspect

import pytest

import sim.engine as E
from sim.engine import Recipe, simulate, _tribology_archard_diagnostic, PSI_TO_PA
import tribology_basics as TB

_ALL_PACKS = ["cu_h2o2_bta", "oxide_silica", "sic_ceria_h2o2", "sic_alumina_kmno4",
              "sti_ceria", "w_fe_oxidizer"]

# Max워커가 미리 계산한 환산값 — 절대값을 못 박는다(상대성만 보는 테스트는 단위 버그를 못 잡는다).
_EXPECTED_K = {
    "cu_h2o2_bta": 4.20e-4,
    "oxide_silica": 9.00e-4,
    # 2026-09-16 판정#49: sic_ceria_h2o2 가 Kp 를 자기선언하면서(상속된 Si 산화막
    # Kp 2.2e-13 → 4H-SiC 실측 역산 1.4144e-15) k = Kp·H 가 같은 배수로 내려갔다.
    # 5.72e-3 은 산화막 Kp 에 SiC 경도를 곱한 값이었다 — 물리적으로 의미 없는 조합.
    # 새 값 1.4144e-15 × 2.6e10 Pa = 3.67744e-5 (여전히 Archard 문헌 창 1e-5~1e-1 안).
    "sic_ceria_h2o2": 3.67744e-5,
    # 신설 팩(산성 KMnO4/알루미나, 판정#49-B): 4.9872e-15 × 2.6e10 Pa
    "sic_alumina_kmno4": 1.296672e-4,
    "sti_ceria": 1.98e-3,
    "w_fe_oxidizer": 3.36e-3,
}


def test_five_packs_match_expected_k_exactly():
    for pack, expected in _EXPECTED_K.items():
        rr = Recipe(pack=pack, time_s=60).resolve()
        out = _tribology_archard_diagnostic(rr)
        assert out["archard_wear_coefficient"] == pytest.approx(expected, rel=1e-6), pack


def test_five_packs_k_within_archard_literature_order():
    for pack in _ALL_PACKS:
        rr = Recipe(pack=pack, time_s=60).resolve()
        out = _tribology_archard_diagnostic(rr)
        k = out["archard_wear_coefficient"]
        assert k is not None
        assert 1e-5 <= k <= 1e-1, f"{pack}: k={k} 밖 Archard 문헌 오더 창"
        assert out["archard_reference_k"] == pytest.approx(1e-3)
        assert out["archard_order_ratio"] == pytest.approx(k / 1e-3, rel=1e-9)


def test_missing_film_bulk_hardness_pa_skips_with_reason():
    rr = Recipe(pack="oxide_silica", time_s=60).resolve()
    rr.pack = copy.deepcopy(rr.pack)
    del rr.pack.params["film_bulk_hardness_pa"]
    out = _tribology_archard_diagnostic(rr)
    assert out["archard_wear_coefficient"] is None
    assert out["archard_reference_k"] is None
    assert out["archard_order_ratio"] is None
    assert "film_bulk_hardness_pa" in out["tribology_note"]


def test_diagnostic_does_not_change_mrr():
    r = Recipe(pack="cu_h2o2_bta", time_s=60)
    res_with = simulate(r)

    orig = E._tribology_archard_diagnostic
    E._tribology_archard_diagnostic = lambda rr: {
        "archard_wear_coefficient": 999.0,
        "archard_reference_k": 1e-3,
        "archard_order_ratio": 999999.0,
        "tribology_hersey_number": None,
        "tribology_note": "test-probe",
    }
    try:
        res_forced = simulate(r)
    finally:
        E._tribology_archard_diagnostic = orig

    assert (res_with.mrr_nm_per_min == res_forced.mrr_nm_per_min).all()
    assert res_forced.archard_wear_coefficient == 999.0


def test_kp_roundtrip_identity():
    for pack in _ALL_PACKS:
        rr = Recipe(pack=pack, time_s=60).resolve()
        out = _tribology_archard_diagnostic(rr)
        k = out["archard_wear_coefficient"]
        H = rr.p("film_bulk_hardness_pa")
        recovered_kp = k / H
        assert recovered_kp == pytest.approx(rr.kp_m_per_pa, rel=1e-9)


def test_note_mentions_chemomechanical_and_pin_on_disk_limits():
    rr = Recipe(pack="oxide_silica", time_s=60).resolve()
    out = _tribology_archard_diagnostic(rr)
    assert "화학기계 복합" in out["tribology_note"]
    assert "pin-on-disk" in out["tribology_note"]


def test_hersey_choice_documented():
    # (a)를 골랐다: slurry_viscosity_pa_s가 있는 팩(oxide_silica 등)에서만 Hersey를 낸다.
    rr = Recipe(pack="oxide_silica", time_s=60).resolve()
    assert rr.pack.has("slurry_viscosity_pa_s")
    out = _tribology_archard_diagnostic(rr)
    assert out["tribology_hersey_number"] is not None
    assert "오더 확인용" in out["tribology_note"]
    assert "cmp_sommerfeld_number" in out["tribology_note"]

    # slurry_viscosity_pa_s가 없는 팩(cu_h2o2_bta)에서는 None으로 둔다.
    rr2 = Recipe(pack="cu_h2o2_bta", time_s=60).resolve()
    assert not rr2.pack.has("slurry_viscosity_pa_s")
    out2 = _tribology_archard_diagnostic(rr2)
    assert out2["tribology_hersey_number"] is None

    # 직접 호출한 hersey_number와 일치 확인 — kin.speed_stats mean을 그대로 쓴다.
    from sim.tier1_empirical import kinematics as kin
    eta = rr.p("slurry_viscosity_pa_s")
    U_mean = kin.speed_stats(rr.wafer_radius_m, rr.center_offset_m,
                             rr.rpm_wafer, rr.rpm_platen)["mean"]
    P = rr.pressure_psi * PSI_TO_PA
    expected = TB.hersey_number(eta, U_mean, P)
    assert out["tribology_hersey_number"] == pytest.approx(expected, rel=1e-9)


def test_forbidden_functions_never_called():
    """stribeck_cof(근거 없는 정성 파라미터, cof_stribeck_estimate와 중복)·
    archard_wear_volume(하중 W·미끄럼거리 L 절대값이 Recipe에 없음)은 engine.py
    어디서도 실제로 호출되지 않는다.

    inspect.getsource + ast로 **실제 함수호출 노드**만 본다 — docstring·주석에
    함수명을 설명 목적으로 적는 것(이 진단 자체의 docstring 포함)은 오탐이면 안 된다.
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
    forbidden = {"stribeck_cof", "archard_wear_volume"}
    hit = forbidden & called_names
    assert not hit, (
        f"engine.py가 {hit}를 실제로 호출한다 — stribeck_cof는 근거 없는 정성 파라미터가 "
        "박혀 있고 cof_stribeck_estimate와 중복, archard_wear_volume은 하중 W·미끄럼거리 L "
        "절대값이 Recipe에 없어 지어낸 값으로 계산한 결과가 제품 출력이 되면 안 된다.")


def test_original_module_untouched():
    """원본 모듈 tribology_basics.py는 1바이트도 수정하지 않는다 — git diff가
    비어 있어야 한다(트래킹된 파일 기준)."""
    import subprocess
    result = subprocess.run(
        ["git", "diff", "--stat", "HEAD", "--",
         "sim/tier2_physics/tribology_basics.py"],
        capture_output=True, text=True,
        cwd=str(__import__("pathlib").Path(__file__).resolve().parent.parent))
    assert result.stdout.strip() == "", f"원본 모듈이 수정됨: {result.stdout}"
