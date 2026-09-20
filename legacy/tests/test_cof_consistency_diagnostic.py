# -*- coding: utf-8 -*-
"""μ(마찰계수) 일관성 진단 계약 테스트 — 백로그 ㉹ / S12 종결 판정 ⑤ 후속.

배경(2026-09-16 Max워커 실측):
  엔진은 마찰계수를 두 곳에서 쓴다.
    (a) `_theta_steady_state_diagnostic` 의 Q_f = μ·P·A·V  → μ = cof_boundary
    (b) `_lubrication_diagnostics` 의 `cof_stribeck_estimate`
  (b)는 원래 `CLR.cof_stribeck(so)` 로만 호출돼 **팩 YAML의 3개 키
  (cof_boundary·cof_hydro_coeff·cof_transition_alpha)가 완전한 dead code** 였다.
  모듈 기본인자(0.30/8.0/40.0)가 base.yaml 값과 우연히 같아 증상이 보이지 않았다 —
  cof_boundary 를 0.15/0.45 로 흔들어도 출력이 비트 단위로 불변이었다.

이 테스트가 고정하는 것:
  1. 3개 키가 실제로 소비된다(dead code 재발 차단) — 되돌리면 FAIL 한다.
  2. 기본값에서 이전 값과 **비트 단위로 동일**(순수 결함 수정, 회귀 아님).
  3. 두 μ 가 독립 추정이 **아님**(비가 항상 <1, 차이는 estimated 파라미터에서만 나옴).
  4. MRR 경로 무관.
"""
import math
import pytest

from sim.engine import Recipe, simulate

LUBE_PACKS = ["oxide_silica", "sic_alumina_kmno4", "sic_ceria_h2o2", "sti_ceria"]
NO_LUBE_PACKS = ["cu_h2o2_bta", "w_fe_oxidizer"]


def _s(pack, **ov):
    return simulate(Recipe(pack=pack, pack_overrides=ov or {})).summary()


def test_cof_boundary_key_is_actually_consumed():
    """cof_boundary 가 dead 가 아님 — 값을 바꾸면 Stribeck 추정치가 따라 움직인다."""
    base = _s("oxide_silica")["cof_stribeck_estimate"]
    hi = _s("oxide_silica", cof_boundary=0.45)["cof_stribeck_estimate"]
    lo = _s("oxide_silica", cof_boundary=0.15)["cof_stribeck_estimate"]
    assert base is not None and hi is not None and lo is not None
    assert lo < base < hi, f"단조성 실패: {lo} < {base} < {hi}"
    # 실측 절대값(회귀 고정). dead code 로 되돌리면 셋 다 0.2261642863205939 가 된다.
    assert hi == pytest.approx(0.322212, rel=1e-5)
    assert lo == pytest.approx(0.130116, rel=1e-5)


def test_transition_alpha_key_is_actually_consumed():
    """alpha_tr↑ → 접촉분율 f=exp(-alpha_tr·So) 감소 → COF 하락."""
    a10 = _s("oxide_silica", cof_transition_alpha=10.0)["cof_stribeck_estimate"]
    a40 = _s("oxide_silica", cof_transition_alpha=40.0)["cof_stribeck_estimate"]
    a80 = _s("oxide_silica", cof_transition_alpha=80.0)["cof_stribeck_estimate"]
    assert a80 < a40 < a10, f"단조성 실패: {a80} < {a40} < {a10}"
    assert a10 == pytest.approx(0.279764, rel=1e-5)
    assert a80 == pytest.approx(0.177605, rel=1e-5)


def test_hydro_coeff_key_is_actually_consumed():
    """c_hydro↑ → 유체전단항 (1-f)·c_hydro·So 증가 → COF 상승."""
    c8 = _s("oxide_silica", cof_hydro_coeff=8.0)["cof_stribeck_estimate"]
    c20 = _s("oxide_silica", cof_hydro_coeff=20.0)["cof_stribeck_estimate"]
    assert c20 > c8
    assert c20 == pytest.approx(0.274266, rel=1e-5)


def test_default_values_are_bit_identical_to_pre_fix():
    """결함 수정이지 값 변경이 아니다 — 팩 기본값에서 이전 출력과 비트 동일."""
    assert _s("oxide_silica")["cof_stribeck_estimate"] == 0.2261642863205939
    for p in ("sic_alumina_kmno4", "sic_ceria_h2o2", "sti_ceria"):
        assert _s(p)["cof_stribeck_estimate"] == 0.22067152632990616


def test_two_mu_are_not_independent_estimates():
    """비는 항상 (0,1) — cof_stribeck 은 mu_bl 을 전이항으로 깎은 값이라 초과 불가.

    '두 독립 추정이 어긋난다'로 오독하면 안 된다. 차이 전부가
    alpha_tr·c_hydro(둘 다 confidence=estimated)에서 나온다.
    """
    for p in LUBE_PACKS:
        s = _s(p)
        mu_qf = s["cof_qf_used"]
        est = s["cof_stribeck_estimate"]
        ratio = s["cof_estimate_vs_qf_ratio"]
        assert mu_qf == pytest.approx(0.30)
        assert 0.0 < ratio < 1.0, f"{p}: ratio={ratio}"
        assert ratio == pytest.approx(est / mu_qf, rel=1e-12)


def test_measured_ratios_are_pinned():
    """실측 비 고정 — 24.6~26.4% 낮다."""
    assert _s("oxide_silica")["cof_estimate_vs_qf_ratio"] == pytest.approx(0.753881, rel=1e-5)
    for p in ("sic_alumina_kmno4", "sic_ceria_h2o2", "sti_ceria"):
        assert _s(p)["cof_estimate_vs_qf_ratio"] == pytest.approx(0.735572, rel=1e-5)


def test_note_warns_about_dependence_and_propagation():
    note = _s("oxide_silica")["cof_consistency_note"]
    assert note
    assert "독립 추정이 아니다" in note
    assert "cof_boundary" in note
    assert "estimated" in note


def test_packs_without_viscosity_skip_silently():
    """점도·Ra 미선언 팩은 지어내지 않고 조용히 None."""
    for p in NO_LUBE_PACKS:
        s = _s(p)
        assert s["cof_stribeck_estimate"] is None
        assert s["cof_qf_used"] is None
        assert s["cof_estimate_vs_qf_ratio"] is None
        assert s["cof_consistency_note"] is None


def test_qf_uses_literature_grade_mu_not_the_estimate():
    """Q_f(ΔT_ss)는 cof_boundary 에 선형 — Stribeck 추정치를 대입하지 않았음을 고정.

    EVIDENCE-RULES: cof_boundary=literature > alpha_tr/c_hydro=estimated.
    추정치(0.2262)를 Q_f 에 넣었다면 ΔT_ss 가 28.06 → 21.16 으로 떨어졌을 것이다.
    """
    d1 = _s("oxide_silica")["theta_steady_state_delta_T_k"]
    d2 = _s("oxide_silica", cof_boundary=0.60)["theta_steady_state_delta_T_k"]
    assert d1 == pytest.approx(28.057, rel=1e-3)
    assert d2 == pytest.approx(2 * d1, rel=1e-9)   # Q_f ∝ μ 선형


def test_mrr_is_bit_invariant_under_cof_changes():
    """μ 관련 3개 키는 진단 전용 — MRR 에 단 한 비트도 영향이 없어야 한다."""
    for p in LUBE_PACKS:
        base = simulate(Recipe(pack=p)).mrr_nm_per_min
        for ov in ({"cof_boundary": 0.45},
                   {"cof_transition_alpha": 5.0},
                   {"cof_hydro_coeff": 25.0}):
            got = simulate(Recipe(pack=p, pack_overrides=ov)).mrr_nm_per_min
            assert (got == base).all(), f"{p} {ov} 에서 MRR 변동 — 진단이 MRR 로 샜다"


def test_original_module_untouched():
    """cmp_lubrication_regime.py 는 0바이트 수정."""
    import subprocess, pathlib
    root = pathlib.Path(__file__).resolve().parents[1]
    out = subprocess.run(
        ["git", "diff", "--", "sim/tier2_physics/cmp_lubrication_regime.py"],
        cwd=root, capture_output=True, text=True).stdout
    assert out.strip() == "", f"원본 모듈이 수정됨:\n{out}"
