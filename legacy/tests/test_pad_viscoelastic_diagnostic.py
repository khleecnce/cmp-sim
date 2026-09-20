"""pad_viscoelastic_temperature.py 엔진 등록 회귀 — WaferResult 진단 필드 4종
(패드 유효 탄성률 E'(T) 온도의존 연화 진단).

근거: sim/tier2_physics/pad_viscoelastic_temperature.py::e_pad_from_table(원본 무수정),
Cabot US20170087688A1 Table 1B. T_op = platen_coolant_temp_c + theta_steady_state_delta_T_k
(_theta_steady_state_diagnostic()이 이미 산출). pad_dma_id는 현재 5팩 전부 미선언이라
시뮬레이션 기본 경로에서 항상 None이 정상이다 — 패드 ID를 지어내지 않는다.
"""
import numpy as np
import pytest

import sim.engine as E
from sim.engine import (Recipe, simulate, _pad_viscoelastic_diagnostic,
                         _theta_steady_state_diagnostic)
from sim.params import Param
import pad_viscoelastic_temperature as PVT

_ALL_PACKS = ["cu_h2o2_bta", "oxide_silica", "sic_ceria_h2o2", "sti_ceria", "w_fe_oxidizer"]


def test_all_packs_none_without_pad_dma_id():
    for pack in _ALL_PACKS:
        rr = Recipe(pack=pack, time_s=60).resolve()
        assert not rr.pack.has("pad_dma_id")
        theta_ss = _theta_steady_state_diagnostic(rr)
        out = _pad_viscoelastic_diagnostic(rr, theta_ss)
        assert out["pad_modulus_at_temp_mpa"] is None
        assert out["pad_modulus_ref_25c_mpa"] is None
        assert out["pad_modulus_softening_ratio"] is None
        assert out["pad_viscoelastic_note"] is not None
        assert "미선언" in out["pad_viscoelastic_note"]


def test_pad_dma_id_injection_matches_module_direct_call():
    rr = Recipe(pack="cu_h2o2_bta", time_s=60).resolve()
    rr.pack.params["pad_dma_id"] = Param(
        key="pad_dma_id", value="1B", unit="", source="test-probe", confidence="estimated")
    theta_ss = _theta_steady_state_diagnostic(rr)
    delta_t = theta_ss["theta_steady_state_delta_T_k"]
    assert delta_t is not None
    T_coolant = float(rr.p("platen_coolant_temp_c"))
    out = _pad_viscoelastic_diagnostic(rr, theta_ss)

    expected_op = PVT.e_pad_from_table(T_coolant + delta_t, "1B")
    expected_ref = PVT.e_pad_from_table(25.0, "1B")
    assert out["pad_modulus_at_temp_mpa"] == expected_op
    assert out["pad_modulus_ref_25c_mpa"] == expected_ref
    assert out["pad_modulus_softening_ratio"] == pytest.approx(expected_op / expected_ref)


def test_softening_ratio_below_one_when_temp_rises():
    # T_coolant=30 + ΔT_ss>0 이므로 T_op>25 — E'는 온도 상승에 따라 단조감소하므로
    # softening_ratio(=E'(T_op)/E'(25°C))는 1 미만이어야 한다(연화 방향).
    rr = Recipe(pack="cu_h2o2_bta", time_s=60).resolve()
    rr.pack.params["pad_dma_id"] = Param(
        key="pad_dma_id", value="1B", unit="", source="test-probe", confidence="estimated")
    theta_ss = _theta_steady_state_diagnostic(rr)
    out = _pad_viscoelastic_diagnostic(rr, theta_ss)
    assert out["pad_modulus_softening_ratio"] < 1.0


def test_out_of_range_clamp_warning_in_note():
    # platen_coolant_temp_c를 60°C로 올리면 T_op=60+ΔT_ss(~28)≈88°C > 80°C(Table 1B 상한)
    # — e_pad_loglinear가 조용히 clamp하므로, 이 진단은 그 사실을 note에 반드시 남겨야 한다.
    recipe = Recipe(pack="cu_h2o2_bta", time_s=60,
                    pack_overrides={"platen_coolant_temp_c": 60.0})
    rr = recipe.resolve()
    rr.pack.params["pad_dma_id"] = Param(
        key="pad_dma_id", value="1B", unit="", source="test-probe", confidence="estimated")
    theta_ss = _theta_steady_state_diagnostic(rr)
    T_op = float(rr.p("platen_coolant_temp_c")) + theta_ss["theta_steady_state_delta_T_k"]
    assert T_op > 80.0
    out = _pad_viscoelastic_diagnostic(rr, theta_ss)
    assert out["pad_modulus_at_temp_mpa"] == PVT.e_pad_from_table(80.0, "1B")
    assert "clamp" in out["pad_viscoelastic_note"]
    assert "80" in out["pad_viscoelastic_note"]


def test_pad_viscoelastic_diagnostic_does_not_change_mrr():
    # 이 진단을 계산하든 안 하든 mrr_nm_per_min은 비트 단위로 동일해야 한다 —
    # MRR 경로와 완전히 독립적인 진단 전용 필드라는 계약.
    r = Recipe(pack="cu_h2o2_bta", time_s=60)
    res_with = simulate(r)

    orig = E._pad_viscoelastic_diagnostic
    E._pad_viscoelastic_diagnostic = lambda rr, theta_ss: {
        "pad_modulus_at_temp_mpa": 999.0,
        "pad_modulus_ref_25c_mpa": 1.0,
        "pad_modulus_softening_ratio": 999.0,
        "pad_viscoelastic_note": "test-probe",
    }
    try:
        res_forced = simulate(r)
    finally:
        E._pad_viscoelastic_diagnostic = orig

    assert np.array_equal(res_with.mrr_nm_per_min, res_forced.mrr_nm_per_min)
    assert res_forced.pad_modulus_at_temp_mpa == 999.0


def test_original_module_unmodified():
    # 원본 모듈 1바이트도 수정 안 함 확인 — 상수값·함수 시그니처 고정.
    assert PVT.CABOT_TABLE_1B["1B"]["T_C"] == [25, 50, 80]
    assert PVT.CABOT_TABLE_1B["1B"]["E_MPa"] == [1725, 204, 5]
    assert set(PVT.CABOT_TABLE_1B.keys()) == {"1A", "1B", "1C", "1D", "1E", "D100"}
    import inspect
    sig = inspect.signature(PVT.e_pad_from_table)
    assert list(sig.parameters) == ["T_C", "pad_id"]
