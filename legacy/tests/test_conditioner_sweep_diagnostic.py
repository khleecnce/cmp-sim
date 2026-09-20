"""conditioner_sweep_kinematics.py 엔진 등록 회귀 — WaferResult 진단 필드 3종
(컨디셔너 스윕 PCR(r) 상대 프로파일 요약: CV·edge/center 비).

근거: sim/tier2_physics/conditioner_sweep_kinematics.py (Zheng, Zhao & Lu 2023,
Micromachines 14(9) 1683, PMC10536193, Eq.1-9 재현), knowledge/equipment/
conditioner-sweep-kinematics-pcr-profile.md.

기구 고정 치수(R_p·R_a·disk_radius·n_d·beta_s·beta_max)는 팩이 cond_arm_pivot_radius_m·
cond_arm_length_m·cond_disk_radius_m·cond_disk_rpm·cond_sweep_beta_start_rad·
cond_sweep_beta_range_rad를 선언할 때만 계산한다(하드코딩 금지) — 현재 5팩 전부
미선언이라 시뮬레이션 기본 경로에서는 항상 None이 정상이다.

비용 판단: pcr_radial_profile(duration_s=20.0, dt=0.01, n_particles=12, r_bins=20) —
이 진단이 실제로 쓰는 인자 조합 — 은 로컬 .venv python 실측 약 3.7~3.8ms/call로
100ms 문턱(engine.py의 opt-in 기준)에 한참 못 미친다. 그래서 _conditioner_sweep_diagnostic은
meta 플래그 없이 필수 파라미터가 팩에 있으면 항상 계산한다(engine.py 함수 docstring에
같은 측정치가 적혀 있다). 모듈 자체에 난수(np.random)가 없어(R_i·theta_i0는 np.linspace
균등샘플) 시드 고정 없이도 결정론적이다.

MRR 경로와 독립인 진단 필드라 mrr_nm_per_min은 건드리지 않는다.
"""
import math

import numpy as np

import sim.engine as E
from sim.engine import Recipe, simulate, _conditioner_sweep_diagnostic
from sim.params import Param

# self-test와 무관한 임의의 소형 기하값 — R_p-R_a-disk_radius<0이라 팔이 패드 중심 부근까지
# 닿을 수 있어 안쪽 링도 non-zero가 된다(edge_center_ratio가 유한하려면 필요).
_TEST_GEOM = {
    "cond_arm_pivot_radius_m": 50.0,
    "cond_arm_length_m": 45.0,
    "cond_disk_radius_m": 30.0,
    "cond_disk_rpm": 73.0,
    "cond_sweep_beta_start_rad": 0.0,
    "cond_sweep_beta_range_rad": math.pi,
}


def _rr_with_geom(pack="cu_h2o2_bta", time_s=60, meta=None):
    recipe = Recipe(pack=pack, time_s=time_s, meta=meta or {})
    rr = recipe.resolve()
    for k, v in _TEST_GEOM.items():
        rr.pack.params[k] = Param(key=k, value=v, unit="test", source="test-probe",
                                  confidence="estimated")
    return rr


def test_none_without_required_geometry():
    # 5팩 전부 기구 고정 치수를 선언하지 않는다 — 스킵되는 것이 정상.
    rr = Recipe(pack="cu_h2o2_bta", time_s=60).resolve()
    for k in ("cond_arm_pivot_radius_m", "cond_arm_length_m", "cond_disk_radius_m",
             "cond_disk_rpm", "cond_sweep_beta_start_rad", "cond_sweep_beta_range_rad"):
        assert not rr.pack.has(k)
    out = _conditioner_sweep_diagnostic(rr)
    assert out["conditioner_sweep_profile_uniformity"] is None
    assert out["conditioner_sweep_edge_center_ratio"] is None
    assert out["conditioner_sweep_note"] is not None
    assert "cond_arm_pivot_radius_m" in out["conditioner_sweep_note"]


def test_none_in_full_simulate_for_default_packs():
    res = simulate(Recipe(pack="cu_h2o2_bta", time_s=60))
    assert res.conditioner_sweep_profile_uniformity is None
    assert res.conditioner_sweep_edge_center_ratio is None
    assert res.conditioner_sweep_note is not None


def test_profile_uniformity_cv_finite_positive_when_geometry_declared():
    rr = _rr_with_geom()
    out = _conditioner_sweep_diagnostic(rr)
    cv = out["conditioner_sweep_profile_uniformity"]
    assert cv is not None
    assert np.isfinite(cv)
    assert cv > 0.0


def test_edge_center_ratio_finite_and_physically_plausible():
    rr = _rr_with_geom()
    out = _conditioner_sweep_diagnostic(rr)
    ratio = out["conditioner_sweep_edge_center_ratio"]
    assert ratio is not None
    assert np.isfinite(ratio)
    # 상대 스크래치 거리 비율이므로 0보다 크고, 극단적으로 비정상적인 값(예: 1e6배)은 아니어야 한다.
    assert 0.0 < ratio < 1000.0


def test_deterministic_repeat_call():
    # 모듈은 np.random을 쓰지 않는다(R_i·theta_i0가 np.linspace 균등샘플) —
    # 시드 없이도 같은 입력에 같은 출력이 나와야 한다.
    rr1 = _rr_with_geom()
    rr2 = _rr_with_geom()
    out1 = _conditioner_sweep_diagnostic(rr1)
    out2 = _conditioner_sweep_diagnostic(rr2)
    assert out1["conditioner_sweep_profile_uniformity"] == out2["conditioner_sweep_profile_uniformity"]
    assert out1["conditioner_sweep_edge_center_ratio"] == out2["conditioner_sweep_edge_center_ratio"]

    out1b = _conditioner_sweep_diagnostic(rr1)
    assert out1["conditioner_sweep_profile_uniformity"] == out1b["conditioner_sweep_profile_uniformity"]


def test_conditioner_sweep_diagnostic_does_not_change_mrr():
    # 이 진단을 계산하든 안 하든 mrr_nm_per_min은 비트 단위로 동일해야 한다 —
    # MRR 경로와 완전히 독립적인 진단이라는 계약.
    r = Recipe(pack="cu_h2o2_bta", time_s=60)
    res_with = simulate(r)

    orig = E._conditioner_sweep_diagnostic
    E._conditioner_sweep_diagnostic = lambda rr: {
        "conditioner_sweep_profile_uniformity": 999.0,
        "conditioner_sweep_edge_center_ratio": 1.0,
        "conditioner_sweep_note": "test-probe",
    }
    try:
        res_forced = simulate(r)
    finally:
        E._conditioner_sweep_diagnostic = orig

    assert np.array_equal(res_with.mrr_nm_per_min, res_forced.mrr_nm_per_min)
    assert res_forced.conditioner_sweep_profile_uniformity == 999.0
