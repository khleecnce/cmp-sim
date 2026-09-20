"""slurry_components.py 엔진 등록 회귀 — 억제제 Langmuir 피복률 포화도 진단 4종.

근거: sim/tier2_physics/slurry_components.py::langmuir_coverage/K_from_dG_ads
(원본 무수정), sim/inhibitor_pairs.py, EVIDENCE-RULES 판정#17,
knowledge/cmp/bta-inhibitor-langmuir-K-effective-cu-cmp-falsification.md §5·§6.

이 진단의 존재 이유: 판정#17이 반증한 고장(θ 포화로 농도축이 죽어 MRR이 억제제
농도에 반응하지 않는 상태)은 MRR 출력만 봐서는 안 보인다. 진단 필드로 꺼낸다.

⛔ MRR에 곱하지 않는다 — _inhibitor_term이 이미 같은 θ를 소비한다(이중계상 금지).
⛔ mrr_oxidizer(판정#19가 (n,C_peak) 완전축퇴로 폐기)는 호출하지 않는다 —
   test_forbidden_functions_never_called이 ast로 기계 고정한다.
"""
import ast
import inspect
import math

import numpy as np

import sim.engine as E
from sim.engine import Recipe, simulate, _inhibitor_saturation_diagnostic
from sim.params import Param
import slurry_components as SC

_METAL_PACKS = ["cu_h2o2_bta", "w_fe_oxidizer"]
_OXIDE_PACKS = ["oxide_silica", "sic_ceria_h2o2", "sti_ceria"]


def test_oxide_packs_skip_with_reason():
    """산화막 계 3팩엔 금속 부식억제제가 없다 — None + 스킵사유가 정상."""
    for pack in _OXIDE_PACKS:
        rr = Recipe(pack=pack, time_s=60).resolve()
        assert not rr.pack.has("inhibitor_mM"), pack
        out = _inhibitor_saturation_diagnostic(rr)
        assert out["inhibitor_theta_equilibrium"] is None, pack
        assert out["inhibitor_conc_discrimination"] is None, pack
        assert "inhibitor_mM" in out["inhibitor_saturation_note"], pack


def test_metal_packs_produce_all_fields():
    for pack in _METAL_PACKS:
        res = simulate(Recipe(pack=pack, time_s=60))
        assert res.inhibitor_theta_equilibrium is not None, pack
        assert 0.0 < res.inhibitor_theta_equilibrium < 1.0, pack
        assert res.inhibitor_theta_headroom is not None, pack
        assert res.inhibitor_conc_discrimination is not None, pack
        assert res.inhibitor_saturation_note is not None, pack
        # 항등식: headroom == 1 - theta
        assert math.isclose(res.inhibitor_theta_headroom,
                            1.0 - res.inhibitor_theta_equilibrium, rel_tol=1e-12), pack
        # 판별비는 항상 1 이상(Langmuir θ는 농도에 단조증가)이고 2 이하
        # (θ(2C)/θ(C) = (1+KC)/(1+2KC)*2 <= 2, C→0 극한에서만 2에 접근)
        assert 1.0 <= res.inhibitor_conc_discrimination <= 2.0, pack


def test_k_lookup_matches_chemistry_module_priority():
    """K 조회 우선순위가 sim/chemistry.py::_inhibitor_term과 같은 값을 낸다.

    두 곳이 다른 K를 쓰면 같은 결과 문서 안에서 θ가 모순된다.
    cu_h2o2_bta: 쌍 표(bta×cu, ΔG=-30.02) 우선 — 팩의 단일 ΔG(-35.4)가 아니다.
    w_fe_oxidizer: 쌍 표에 (picolinic_acid × w) 없음 → 팩 K(1108) 폴백.
    """
    from sim.inhibitor_pairs import lookup_dG, K_from_dG

    rr_cu = Recipe(pack="cu_h2o2_bta", time_s=60).resolve()
    out_cu = _inhibitor_saturation_diagnostic(rr_cu)
    pair = lookup_dG("bta", "cu")
    assert pair is not None
    k_pair = K_from_dG(pair.dG_kJ_per_mol)
    expected_theta = SC.langmuir_coverage(
        float(rr_cu.p("inhibitor_mM")) * 1e-3, k_pair)
    assert math.isclose(out_cu["inhibitor_theta_equilibrium"], expected_theta,
                        rel_tol=1e-12)
    # 팩의 단일 ΔG(-35.4 → K_eq≈2.87e4)로 계산한 값과는 **다르다**(쌍이 우선).
    k_eq_pack = SC.K_from_dG_ads(float(rr_cu.p("inhibitor_dG_ads_kJ")) * 1000.0)
    theta_eq = SC.langmuir_coverage(float(rr_cu.p("inhibitor_mM")) * 1e-3, k_eq_pack)
    assert not math.isclose(out_cu["inhibitor_theta_equilibrium"], theta_eq, rel_tol=1e-6)
    assert "쌍 표" in out_cu["inhibitor_saturation_note"]

    rr_w = Recipe(pack="w_fe_oxidizer", time_s=60).resolve()
    out_w = _inhibitor_saturation_diagnostic(rr_w)
    assert lookup_dG("picolinic_acid", "w") is None  # 쌍 표에 없음
    expected_w = SC.langmuir_coverage(float(rr_w.p("inhibitor_mM")) * 1e-3,
                                      float(rr_w.p("inhibitor_K_L_per_mol")))
    assert math.isclose(out_w["inhibitor_theta_equilibrium"], expected_w, rel_tol=1e-12)


def test_w_fe_oxidizer_flags_saturation_and_attributes_it_to_literature():
    """w_fe_oxidizer(피콜린산 121.8mM, K=1108)는 θ=0.9926으로 포화 — 🔴 신고.

    ⚠ 이 포화는 **판정#17의 고장이 아니다**. Lee & Seo 2022(doi:10.3390/app12031227)
    §3.3이 1.5wt%→5.0wt%에서 추가 억제 없음을 직접 실측했으므로, 이 팩의 운전점은
    문헌이 측정한 포화 플래토 위에 있다 — 모델이 맞는 쪽이다.

    진단이 지켜야 할 계약은 두 가지다:
      (1) 포화 신호 자체는 낸다(🔴) — 민감도 0을 사용자가 '억제제 무영향'으로
          오독하지 않게 한다.
      (2) 원인을 (a)실계 포화 / (b)K 오경로(판정#17)로 **구분하지 못한다**고 밝히고,
          이 팩에 대해서는 문헌 근거로 (a)임을 명시한다. 원인을 단정하면 안 된다.
    """
    res = simulate(Recipe(pack="w_fe_oxidizer", time_s=60))
    assert res.inhibitor_theta_equilibrium > 0.99
    assert res.inhibitor_conc_discrimination < 1.01
    note = res.inhibitor_saturation_note
    assert "🔴" in note
    # (2) 원인 미구분을 명시하고, 이 팩은 문헌 실측 플래토로 귀속한다.
    assert "(a)와 (b)를 구분하지 못한다" in note
    assert "10.3390/app12031227" in note
    assert "판정#17의 고장이 아니다" in note
    # 문턱 아래 미검증도 정직하게 남아 있어야 한다(§7 RESPONSE_CONFLICT).
    assert "문턱 아래에서는 미검증" in note
    # 현행 파라미터(121.8 mM, K=1108 L/mol)의 닫힌형 값과 정확히 일치
    KC = 1108.0 * 121.8e-3
    assert math.isclose(res.inhibitor_theta_equilibrium, KC / (1.0 + KC), rel_tol=1e-9)


def test_saturation_verdict_never_asserts_a_cause_for_unknown_packs():
    """문헌 귀속이 없는 팩에는 원인을 단정하지 않는다(지어내기 금지).

    cu_h2o2_bta·w_fe_oxidizer 외의 팩을 포화 상태로 만들어도 (a)/(b) 귀속 문장이
    붙으면 안 된다 — 붙으면 근거 없는 원인 주장이 제품 출력이 된다.
    """
    rr = Recipe(pack="cu_h2o2_bta", time_s=60).resolve()
    rr.pack.name = "synthetic_probe_pack"
    rr.pack.params["inhibitor_mM"] = Param(
        key="inhibitor_mM", value=1000.0, unit="mM",
        source="test-probe", confidence="estimated")
    out = _inhibitor_saturation_diagnostic(rr)
    assert out["inhibitor_conc_discrimination"] < 1.01
    note = out["inhibitor_saturation_note"]
    assert "🔴" in note
    assert "【이 팩의 근거】" not in note      # 귀속 문장 없음
    assert "10.3390/app12031227" not in note   # 남의 팩 문헌을 끌어오지 않음


def test_cu_pack_concentration_axis_is_alive():
    """cu_h2o2_bta는 쌍 표 K(3283 L/mol)를 써서 θ=0.767 — 농도축이 살아 있다.

    팩의 단일 ΔG(-35.4, K_eq≈2.87e4)를 썼다면 θ=0.966으로 포화 쪽이었을 것이다 —
    쌍 표 우선이 실제로 더 나은 분해능을 준다는 것을 수치로 고정한다.
    """
    res = simulate(Recipe(pack="cu_h2o2_bta", time_s=60))
    assert res.inhibitor_theta_equilibrium < 0.90
    assert res.inhibitor_conc_discrimination > 1.10
    assert "농도축 살아있음" in res.inhibitor_saturation_note
    # 팩 단일 ΔG 경로였다면 포화였을 것이라는 대조
    k_eq = SC.K_from_dG_ads(-35.4 * 1000.0)
    theta_eq = SC.langmuir_coverage(1.0e-3, k_eq)
    assert theta_eq > 0.95
    assert theta_eq > res.inhibitor_theta_equilibrium


def test_discrimination_monotonically_falls_with_concentration():
    """농도를 올릴수록 판별비가 1에 수렴한다(Langmuir 포화). 물리적 단조성."""
    prev = None
    for mM in (0.01, 0.1, 1.0, 10.0, 100.0):
        rr = Recipe(pack="cu_h2o2_bta", time_s=60).resolve()
        rr.pack.params["inhibitor_mM"] = Param(
            key="inhibitor_mM", value=mM, unit="mM",
            source="test-probe", confidence="estimated")
        out = _inhibitor_saturation_diagnostic(rr)
        d = out["inhibitor_conc_discrimination"]
        if prev is not None:
            assert d < prev, (mM, d, prev)
        prev = d
    assert prev < 1.01  # 100 mM에서는 사실상 사망


def test_missing_adsorption_constant_skips_without_inventing():
    """inhibitor_mM은 있는데 K·ΔG·쌍이 전부 없으면 지어내지 않고 스킵."""
    rr = Recipe(pack="w_fe_oxidizer", time_s=60).resolve()
    for key in ("inhibitor_K_L_per_mol", "inhibitor_dG_ads_kJ",
                "inhibitor_species", "substrate_species"):
        rr.pack.params.pop(key, None)
    out = _inhibitor_saturation_diagnostic(rr)
    assert out["inhibitor_theta_equilibrium"] is None
    assert "흡착상수" in out["inhibitor_saturation_note"]


def test_diagnostic_does_not_change_mrr():
    r = Recipe(pack="cu_h2o2_bta", time_s=60)
    res_ref = simulate(r)

    orig = E._inhibitor_saturation_diagnostic
    E._inhibitor_saturation_diagnostic = lambda rr: {
        "inhibitor_theta_equilibrium": 0.999999,
        "inhibitor_theta_headroom": 1e-6,
        "inhibitor_conc_discrimination": 1.0,
        "inhibitor_saturation_note": "test-probe",
    }
    try:
        res_forced = simulate(r)
    finally:
        E._inhibitor_saturation_diagnostic = orig

    assert np.array_equal(res_ref.mrr_nm_per_min, res_forced.mrr_nm_per_min)
    assert np.array_equal(res_ref.remaining_nm, res_forced.remaining_nm)
    assert res_forced.inhibitor_theta_equilibrium == 0.999999


def test_forbidden_functions_never_called():
    """mrr_oxidizer·_argmax_scan은 engine.py 어디서도 호출되지 않는다.

    판정#19가 mrr_oxidizer의 (n, C_peak) 단봉 형상이 정점 아래 관측만으로는
    완전축퇴(식별 불가)임을 수치로 확인했다 — 엔진 출력으로 내보내면 식별
    불가능한 파라미터가 만든 수치가 제품 출력이 된다.
    inhibition_efficiency(IE≈θ)도 호출하지 않는다: 이 진단은 부식 억제효율을
    주장하지 않고 피복률 포화도만 낸다(IE≈θ 근사는 CMP 기계연마 공존계에서
    미검증).
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
    forbidden = {"mrr_oxidizer", "_argmax_scan", "inhibition_efficiency",
                 "dG_ads_from_K"}
    hit = forbidden & called
    assert not hit, f"engine.py가 {hit}를 호출한다 — 판정#19(축퇴)·미검증 근사 경로다"


def test_original_theta_path_untouched():
    """이 진단이 소비하는 θ 경로 자체는 건드리지 않는다.

    ⚠ 2026-09-16 범위 정정: 이 테스트는 원래 `git diff --stat HEAD --
    sim/chemistry.py` 로 **파일 전체를 동결**했다. 그러나 chemistry.py 에는 이
    진단과 무관한 항(산화제·pH 연화·세리아)이 함께 들어 있어, 다른 축을 배선하는
    정당한 편집까지 이 테스트가 막았다(실제로 χ 산화제축 배선에서 걸렸다).
    파일 동결은 "진단이 원본 물리를 바꾸지 않는다"는 의도보다 넓다 —
    **의도한 대상은 θ(피복률) 계산 경로 하나**이므로 그 함수들의 소스만 고정한다.

    여기서 고정하는 것:
      · slurry_components.langmuir_coverage / K_from_dG_ads (진단이 직접 호출)
      · chemistry._inhibitor_term (같은 θ 를 MRR 쪽에서 소비 — 이중계상 경계)
    이 셋 중 하나라도 바뀌면 진단과 MRR 이 서로 다른 θ 를 보게 될 수 있다.
    """
    import hashlib
    import sim.chemistry as CH

    fixed = {
        "slurry_components.langmuir_coverage":
            "ba8d618d5fca2bd422521e9d0bbb08a4",
        "slurry_components.K_from_dG_ads":
            "e5f411beb368c4be5abe48474e402ff3",
        "chemistry._inhibitor_term":
            # 2026-09-19 갱신: 쌍 조회 앞에 `adsorption_ruled_out()` 분기를 추가했다.
            # θ 계산 경로(langmuir_coverage · K_from_dG · k_inhib)는 한 줄도 바뀌지
            # 않았고, 추가된 것은 '메커니즘 부재로 선언된 쌍이면 항을 만들지 않고
            # 근거를 신고한다'는 조기 반환뿐이다. 현재 쌍 키를 선언한 팩은
            # cu_h2o2_bta(bta × cu) 하나이고 그 쌍은 NO_ADSORPTION 에 없으므로
            # 수치 결과는 불변이다(백테스트로 확인). 근거: 미측정과 메커니즘 부재를
            # 같은 None 으로 뭉개면 다음 회차가 존재하지 않는 문헌을 계속 찾는다.
            "397e52f8159ccce1637e9d1604d79887",
    }
    actual = {
        "slurry_components.langmuir_coverage":
            hashlib.md5(inspect.getsource(SC.langmuir_coverage).encode()).hexdigest(),
        "slurry_components.K_from_dG_ads":
            hashlib.md5(inspect.getsource(SC.K_from_dG_ads).encode()).hexdigest(),
        "chemistry._inhibitor_term":
            hashlib.md5(inspect.getsource(CH._inhibitor_term).encode()).hexdigest(),
    }
    changed = [k for k in fixed if fixed[k] != actual[k]]
    assert not changed, (
        f"θ 경로 함수가 수정됐다: {changed}. 진단(engine)과 MRR(chemistry)이 서로 "
        f"다른 피복률을 보게 될 수 있다. 의도한 변경이면 근거를 판정에 남기고 "
        f"이 해시를 갱신하라: { {k: actual[k] for k in changed} }")
