"""galvanic_hydroxide_ph.py 엔진 등록 회귀 — WaferResult 진단 필드 5종
(갈바닉 부식 방향·Cu 수산화물 전이 pH 진단).

근거: sim/tier2_physics/galvanic_hydroxide_ph.py, knowledge/cmp/
low-level-metal-cobalt-ruthenium-cross-contamination.md §3.1·§3.3·§7.
용존 Cu 농도 관례(log_a_cu 미선언 시 -4.0)는 _cu_pourbaix_diagnostic()과
동일하다 — 같은 문서 안에서 두 진단이 다른 숫자를 내면 안 된다.
접촉 상대 금속(contact_metal)은 현재 5팩 전부 미선언이라 갈바닉 필드는
시뮬레이션 기본 경로에서 항상 None이 정상이다.
"""
import numpy as np
import pytest

import sim.engine as E
from sim.engine import Recipe, simulate, _galvanic_hydroxide_diagnostic
from sim.params import Param
import galvanic_hydroxide_ph as GHP


def test_cu_pack_default_fills_transition_ph_but_not_galvanic():
    rr = Recipe(pack="cu_h2o2_bta", time_s=60).resolve()
    assert not rr.pack.has("log_a_cu")
    assert not rr.pack.has("contact_metal")
    out = _galvanic_hydroxide_diagnostic(rr)
    assert out["hydroxide_transition_ph"] is not None
    assert out["hydroxide_precipitation_expected"] is not None
    assert out["galvanic_anode_metal"] is None
    assert out["galvanic_delta_e0_v"] is None
    assert out["galvanic_hydroxide_note"] is not None
    assert "팩 미선언" in out["galvanic_hydroxide_note"]
    assert "방향만 신뢰" in out["galvanic_hydroxide_note"]


def test_non_cu_film_all_none_with_skip_reason():
    rr = Recipe(pack="oxide_silica", time_s=60).resolve()
    assert rr.film != "cu"
    out = _galvanic_hydroxide_diagnostic(rr)
    assert out["hydroxide_transition_ph"] is None
    assert out["hydroxide_precipitation_expected"] is None
    assert out["galvanic_anode_metal"] is None
    assert out["galvanic_delta_e0_v"] is None
    assert out["galvanic_hydroxide_note"] is not None
    assert f"film='{rr.film}'" in out["galvanic_hydroxide_note"]


def test_transition_ph_matches_module_direct_call():
    rr = Recipe(pack="cu_h2o2_bta", time_s=60).resolve()
    out = _galvanic_hydroxide_diagnostic(rr)
    expected = GHP.hydroxide_transition_pH("Cu", 1e-4)
    assert out["hydroxide_transition_ph"] == expected


def test_precipitation_flag_flips_across_transition_ph():
    trans_ph = GHP.hydroxide_transition_pH("Cu", 1e-4)

    recipe_under = Recipe(pack="cu_h2o2_bta", time_s=60,
                          pack_overrides={"slurry_ph": trans_ph - 0.5})
    rr_under = recipe_under.resolve()
    out_under = _galvanic_hydroxide_diagnostic(rr_under)
    assert out_under["hydroxide_precipitation_expected"] is False

    recipe_over = Recipe(pack="cu_h2o2_bta", time_s=60,
                         pack_overrides={"slurry_ph": trans_ph + 0.5})
    rr_over = recipe_over.resolve()
    out_over = _galvanic_hydroxide_diagnostic(rr_over)
    assert out_over["hydroxide_precipitation_expected"] is True


def test_contact_metal_injection_yields_galvanic_pair():
    rr = Recipe(pack="cu_h2o2_bta", time_s=60).resolve()
    rr.pack.params["contact_metal"] = Param(
        key="contact_metal", value="Co", unit="", source="test-probe",
        confidence="estimated")
    out = _galvanic_hydroxide_diagnostic(rr)
    assert out["galvanic_anode_metal"] == "Co"
    assert out["galvanic_delta_e0_v"] == pytest.approx(0.6219, abs=1e-3)


def test_galvanic_hydroxide_diagnostic_does_not_change_mrr():
    # 이 진단을 계산하든 안 하든 mrr_nm_per_min은 비트 단위로 동일해야 한다 —
    # MRR 경로와 완전히 독립적인 진단이라는 계약.
    r = Recipe(pack="cu_h2o2_bta", time_s=60)
    res_with = simulate(r)

    orig = E._galvanic_hydroxide_diagnostic
    E._galvanic_hydroxide_diagnostic = lambda rr: {
        "galvanic_anode_metal": "Co",
        "galvanic_delta_e0_v": 999.0,
        "hydroxide_transition_ph": 1.0,
        "hydroxide_precipitation_expected": True,
        "galvanic_hydroxide_note": "test-probe",
    }
    try:
        res_forced = simulate(r)
    finally:
        E._galvanic_hydroxide_diagnostic = orig

    assert np.array_equal(res_with.mrr_nm_per_min, res_forced.mrr_nm_per_min)
    assert res_forced.galvanic_delta_e0_v == 999.0
