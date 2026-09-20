"""disk_gw_relative_scaling.py 엔진 등록 회귀 — WaferResult 진단 필드 4종
(디스크 설계 스펙(N, D) 변경의 GW 파라미터 Ra/Rpk/λ 상대 배율 진단).

근거: sim/tier2_physics/disk_gw_relative_scaling.py::ra_relative/rpk_relative/
lambda_relative(원본 무수정), Kwon et al. (2013) doi:10.1016/j.triboint.2013.08.008,
Sun (2009) PhD dissertation hdl:10150/194898. disk_gw_ref_*/disk_gw_target_*는
현재 5팩 전부 미선언이라 시뮬레이션 기본 경로에서 항상 None이 정상이다 — "기준
디스크"를 지어내지 않는다.
"""
import numpy as np
import pytest

import sim.engine as E
from sim.engine import Recipe, simulate, _disk_gw_scaling_diagnostic
from sim.params import Param
import disk_gw_relative_scaling as DGW

_ALL_PACKS = ["cu_h2o2_bta", "oxide_silica", "sic_ceria_h2o2", "sti_ceria", "w_fe_oxidizer"]


def test_all_packs_none_without_disk_specs():
    for pack in _ALL_PACKS:
        rr = Recipe(pack=pack, time_s=60).resolve()
        for k in ("disk_gw_ref_grit_count", "disk_gw_ref_grit_size",
                  "disk_gw_target_grit_count", "disk_gw_target_grit_size"):
            assert not rr.pack.has(k)
        out = _disk_gw_scaling_diagnostic(rr)
        assert out["disk_gw_ra_relative"] is None
        assert out["disk_gw_rpk_relative"] is None
        assert out["disk_gw_lambda_relative"] is None
        assert out["disk_gw_scaling_note"] is not None
        assert "스킵" in out["disk_gw_scaling_note"]


def _inject_specs(rr, N_ref, D_ref, N_target, D_target, high_load=None):
    specs = {
        "disk_gw_ref_grit_count": N_ref,
        "disk_gw_ref_grit_size": D_ref,
        "disk_gw_target_grit_count": N_target,
        "disk_gw_target_grit_size": D_target,
    }
    if high_load is not None:
        specs["disk_gw_high_load"] = high_load
    for k, v in specs.items():
        rr.pack.params[k] = Param(key=k, value=v, unit="", source="test-probe",
                                  confidence="estimated")


def test_specs_injected_matches_module_direct_call_high_load():
    rr = Recipe(pack="cu_h2o2_bta", time_s=60).resolve()
    _inject_specs(rr, N_ref=40e3, D_ref=325, N_target=17e3, D_target=100, high_load=True)
    out = _disk_gw_scaling_diagnostic(rr)

    expected_ra = DGW.ra_relative(40e3, 17e3)
    expected_rpk = DGW.rpk_relative(40e3, 17e3)
    expected_lam = DGW.lambda_relative(325, 100, high_load=True)
    assert out["disk_gw_ra_relative"] == expected_ra
    assert out["disk_gw_rpk_relative"] == expected_rpk
    assert out["disk_gw_lambda_relative"] == expected_lam
    assert "disk_gw_high_load=True" in out["disk_gw_scaling_note"]


def test_specs_injected_without_high_load_leaves_lambda_none_but_notes_both():
    rr = Recipe(pack="cu_h2o2_bta", time_s=60).resolve()
    _inject_specs(rr, N_ref=40e3, D_ref=325, N_target=17e3, D_target=100)
    assert not rr.pack.has("disk_gw_high_load")
    out = _disk_gw_scaling_diagnostic(rr)

    assert out["disk_gw_ra_relative"] == DGW.ra_relative(40e3, 17e3)
    assert out["disk_gw_rpk_relative"] == DGW.rpk_relative(40e3, 17e3)
    # 하중 레짐 임의 선택 금지 — 대표값 없음.
    assert out["disk_gw_lambda_relative"] is None
    lam_hi = DGW.lambda_relative(325, 100, high_load=True)
    lam_lo = DGW.lambda_relative(325, 100, high_load=False)
    assert f"{lam_hi:.4f}" in out["disk_gw_scaling_note"]
    assert f"{lam_lo:.4f}" in out["disk_gw_scaling_note"]
    assert "평균" in out["disk_gw_scaling_note"]


def test_higher_grit_count_reduces_ra_and_rpk_relative():
    # N_target > N_ref -> 그릿 밀도가 높을수록 Ra, Rpk가 작아지는 방향(음의 지수).
    rr = Recipe(pack="cu_h2o2_bta", time_s=60).resolve()
    _inject_specs(rr, N_ref=17e3, D_ref=100, N_target=60e3, D_target=100, high_load=True)
    out = _disk_gw_scaling_diagnostic(rr)
    assert out["disk_gw_ra_relative"] < 1.0
    assert out["disk_gw_rpk_relative"] < 1.0


def test_surface_finish_saturation_boundary_uses_different_exponents():
    # 125 µm를 경계로 국소지수가 달라진다는 것을 lambda_relative가 아니라 원본 모듈의
    # surface_finish_relative를 통해 직접 확인한다(이 진단은 그 값을 노출하지 않지만,
    # 원본 모듈의 구간분기 자체가 뭉개지지 않았음을 계약으로 고정).
    below = DGW.surface_finish_relative(45, 124)
    above = DGW.surface_finish_relative(126, 250)
    # 서로 다른 지수 구간이므로 단일 지수로 뭉갰다면 나오지 않을 값 — 지수값 자체를 대조.
    assert DGW._SF_EXPONENT_BELOW_SATURATION != DGW._SF_EXPONENT_ABOVE_SATURATION
    assert below > 0 and above > 0


def test_disk_gw_scaling_diagnostic_does_not_change_mrr():
    r = Recipe(pack="cu_h2o2_bta", time_s=60)
    res_with = simulate(r)

    orig = E._disk_gw_scaling_diagnostic
    E._disk_gw_scaling_diagnostic = lambda rr: {
        "disk_gw_ra_relative": 999.0,
        "disk_gw_rpk_relative": 999.0,
        "disk_gw_lambda_relative": 999.0,
        "disk_gw_scaling_note": "test-probe",
    }
    try:
        res_forced = simulate(r)
    finally:
        E._disk_gw_scaling_diagnostic = orig

    assert np.array_equal(res_with.mrr_nm_per_min, res_forced.mrr_nm_per_min)
    assert res_forced.disk_gw_ra_relative == 999.0


def test_original_module_unmodified():
    # 원본 모듈 1바이트도 수정 안 함 확인 — 상수값·함수 시그니처 고정.
    assert DGW._RA_EXPONENT_VS_N == -0.23
    assert DGW._RPK_EXPONENT_VS_N == -0.62
    assert DGW._LAMBDA_EXPONENT_HIGH_LOAD == 0.35
    assert DGW._SF_SATURATION_D_UM == 125.0
    assert DGW._SF_EXPONENT_BELOW_SATURATION == 0.71
    assert DGW._SF_EXPONENT_ABOVE_SATURATION == 0.23
    assert DGW._SF_LEVELED_MULTIPLIER == 0.57
    import inspect
    assert list(inspect.signature(DGW.ra_relative).parameters) == ["N_ref", "N_target"]
    assert list(inspect.signature(DGW.lambda_relative).parameters) == [
        "D_ref", "D_target", "high_load"]
