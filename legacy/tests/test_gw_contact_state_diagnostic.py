"""gw_pressure_solve.py + gw_contact.py 엔진 등록 회귀 — WaferResult 진단 필드 6종
(GW 역문제 런타임 해 vs base.yaml의 real_contact_area_ratio 정적값 괴리 노출).

근거: sim/tier2_physics/gw_pressure_solve.py::local_contact_state, gw_contact.py::
plasticity_index/gw_analytic_ratio. base.yaml의 real_contact_area_ratio note가
"압력 의존성을 정식으로 넣으려면 GW를 런타임에 풀어야 한다"고 자백한 것을 이 진단이
실행한다. MRR 경로와 독립인 진단 필드라 mrr_nm_per_min은 건드리지 않는다.
"""
import subprocess
from pathlib import Path

import numpy as np
import pytest

import sim.engine as E
from sim.engine import Recipe, simulate, PSI_TO_PA, _gw_contact_state_diagnostic

_PACKS = ["cu_h2o2_bta", "oxide_silica", "sic_ceria_h2o2", "sti_ceria", "w_fe_oxidizer"]
_STATIC_RATIO = 1.393e-3


def test_all_five_packs_fill_real_contact_area_ratio():
    for pack in _PACKS:
        res = simulate(Recipe(pack=pack, time_s=60))
        assert res.gw_real_contact_area_ratio is not None, pack
        assert 0.0 < res.gw_real_contact_area_ratio < 1.0, pack


def test_missing_pad_key_gives_none_with_skip_note():
    rr = Recipe(pack="oxide_silica", time_s=60).resolve()
    del rr.pack.params["pad_E_star_pa"]
    out = _gw_contact_state_diagnostic(rr)
    assert out["gw_real_contact_area_ratio"] is None
    assert out["gw_solved_separation_m"] is None
    assert out["gw_contact_regime_note"] is not None
    assert "pad_E_star_pa" in out["gw_contact_regime_note"]


def test_gw_contact_state_diagnostic_does_not_change_mrr():
    r = Recipe(pack="sti_ceria", time_s=60)
    res_with = simulate(r)

    orig = E._gw_contact_state_diagnostic
    E._gw_contact_state_diagnostic = lambda rr: {
        "gw_solved_separation_m": None,
        "gw_real_contact_area_ratio": None,
        "gw_real_contact_pressure_pa": None,
        "gw_static_pack_ratio_deviation": None,
        "gw_plasticity_index": None,
        "gw_contact_regime_note": None,
    }
    try:
        res_without = simulate(r)
    finally:
        E._gw_contact_state_diagnostic = orig
    assert np.array_equal(res_with.mrr_nm_per_min, res_without.mrr_nm_per_min)


def test_higher_pressure_gives_higher_real_contact_area_ratio():
    rr_lo = Recipe(pack="oxide_silica", pressure_psi=2.0, time_s=60).resolve()
    rr_hi = Recipe(pack="oxide_silica", pressure_psi=4.0, time_s=60).resolve()
    out_lo = _gw_contact_state_diagnostic(rr_lo)
    out_hi = _gw_contact_state_diagnostic(rr_hi)
    assert out_lo["gw_real_contact_area_ratio"] < out_hi["gw_real_contact_area_ratio"]


def test_oxide_silica_deviation_from_static_pack_value_matches_ratio():
    rr = Recipe(pack="oxide_silica", pressure_psi=3.0, time_s=60).resolve()
    out = _gw_contact_state_diagnostic(rr)
    assert out["gw_static_pack_ratio_deviation"] is not None
    expected = out["gw_real_contact_area_ratio"] / _STATIC_RATIO
    assert out["gw_static_pack_ratio_deviation"] == pytest.approx(expected)


def test_plasticity_index_computed_with_unverified_regime_tag():
    rr = Recipe(pack="oxide_silica", time_s=60).resolve()
    out = _gw_contact_state_diagnostic(rr)
    assert out["gw_plasticity_index"] is not None
    assert out["gw_plasticity_index"] > 0.0
    assert "미검증 판정기준" in out["gw_contact_regime_note"]


def test_analytic_vs_numeric_ratio_cross_check_runs():
    # 값 자체를 필드로 노출하진 않지만, 진단이 예외 없이 끝까지 note를 채워야 한다.
    rr = Recipe(pack="sti_ceria", time_s=60).resolve()
    out = _gw_contact_state_diagnostic(rr)
    assert out["gw_contact_regime_note"] is not None


def test_original_modules_untouched():
    repo = Path(__file__).resolve().parent.parent
    result = subprocess.run(
        ["git", "diff", "--stat", "HEAD", "--",
         "sim/tier2_physics/gw_pressure_solve.py", "sim/tier2_physics/gw_contact.py"],
        capture_output=True, text=True, cwd=str(repo))
    assert result.stdout.strip() == "", f"원본 모듈이 수정됨: {result.stdout}"


# ---------------------------------------------------------------------------
# β 단위 회귀 (2026-09-16, Max워커)
#
# 최초 구현은 팩 키 `pad_height_beta_inv_m`(지수분포 **스케일** 1/β = 2.0e-6 m)를
# gw_contact.exp_pdf(z, beta)=β·exp(-βz)의 **감쇠율 β [1/m]** 자리에 역수 변환 없이
# 그대로 넘겼다. 그 결과 분리거리가 d=2.16e7 m(=21,600 km)로 풀리고 실접촉비가
# 2.79e-9(문헌 해의 1/500,000)이 됐는데도 위의 8개 테스트는 전부 통과했다 —
# "0<ratio<1", "압력↑→ratio↑", "deviation == ratio/static" 같은 상대적 성질만
# 검사했기 때문이다. 아래 3건은 **절대 스케일**을 base.yaml이 기록한 GW 해에 고정한다.
#
# 같은 버그가 `_gw_contact_linearity_diagnostic`(선등록, 커밋 a736f95)에도 있었다 —
# 그쪽은 Kp를 GW로 역산했다가 같은 GW로 되돌리는 항등식이라 비(ratio)가 β와 무관하게
# 1.000으로 나와 증상이 보이지 않았다. 함께 고쳤다.
# ---------------------------------------------------------------------------

# base.yaml `real_contact_area_ratio` note의 GW 수치적분 해(2026-09-15 재계산):
#   E*=1.316e8 Pa, R=50 µm, η=2.0e8 /m², 1/β=2.0 µm, A_n=π·0.15² m², W=3 psi×A_n
#   → d=7.62 µm, 실접촉비 1.393e-3, 접촉자리 4.434e6 /m², 실접촉압력 14.9 MPa
_ANCHOR_D_M = 7.62e-6
_ANCHOR_RATIO = 1.393e-3
_ANCHOR_P_R_PA = 14.9e6


def test_separation_matches_base_yaml_documented_gw_solution():
    """d가 asperity 스케일(µm 오더)이어야 한다. β를 역수 변환하지 않으면 2.16e7 m가 나온다."""
    rr = Recipe(pack="oxide_silica", pressure_psi=3.0, time_s=60).resolve()
    out = _gw_contact_state_diagnostic(rr)
    assert out["gw_solved_separation_m"] == pytest.approx(_ANCHOR_D_M, rel=0.01)
    # 스케일 자체를 못 박는다 — km 오더 해는 물리적으로 불가능하다.
    assert 1e-7 < out["gw_solved_separation_m"] < 1e-4


def test_runtime_ratio_reproduces_static_pack_value_within_1pct():
    """런타임 해가 정적 팩값(1.393e-3)을 재현해야 한다 — 같은 입력·같은 코드이므로
    배율이 1.000 근방이 아니면 어느 한쪽 단위가 틀린 것이다."""
    rr = Recipe(pack="oxide_silica", pressure_psi=3.0, time_s=60).resolve()
    out = _gw_contact_state_diagnostic(rr)
    assert out["gw_real_contact_area_ratio"] == pytest.approx(_ANCHOR_RATIO, rel=0.01)
    assert out["gw_real_contact_pressure_pa"] == pytest.approx(_ANCHOR_P_R_PA, rel=0.02)
    assert out["gw_static_pack_ratio_deviation"] == pytest.approx(1.0, rel=0.01)
    # 정적값과 1% 이내로 맞으면 괴리 경고가 note에 붙으면 안 된다.
    assert "⚠" not in out["gw_contact_regime_note"]


def test_analytic_closed_form_matches_numeric_ar_over_w():
    """gw_analytic_ratio(폐형식 A_r/W = sqrt(π·R·β)/E*, d-무관)와 수치해가 1% 이내.

    이 교차검증은 β 단위가 틀리면 깨진다 — 폐형식과 수치해가 같은 β를 받으므로
    둘 다 틀리면 여전히 일치하지만, 아래에서 **폐형식을 문헌 파라미터로 직접**
    계산해 비교하므로 단위 오류가 드러난다.
    """
    import sys, os, math
    sys.path.insert(0, os.path.join(os.path.dirname(E.__file__), "tier2_physics"))
    import gw_contact as GWC
    import gw_pressure_solve as GWP

    E_star, R, inv_beta, eta = 1.316e8, 5.0e-5, 2.0e-6, 2.0e8
    A_n = math.pi * 0.15 ** 2
    beta = 1.0 / inv_beta
    state = GWP.local_contact_state(3.0 * PSI_TO_PA, A_n, beta, eta, E_star, R)
    numeric = state["A_r"] / state["W"]
    analytic = GWC.gw_analytic_ratio(beta, E_star, R)
    assert numeric == pytest.approx(analytic, rel=0.01)
    # 엔진 진단이 쓰는 경로도 같은 β를 쓰는지 확인(역수 변환 누락 시 여기서 깨진다).
    rr = Recipe(pack="oxide_silica", pressure_psi=3.0, time_s=60).resolve()
    out = _gw_contact_state_diagnostic(rr)
    assert out["gw_real_contact_area_ratio"] == pytest.approx(
        state["contact_area_fraction"], rel=1e-6)
