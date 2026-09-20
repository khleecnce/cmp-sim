"""slurry_film_lubrication.py 엔진 등록 회귀 — WaferResult 진단 필드 2종
(film_z0_scale_um · film_lubrication_note).

노트 knowledge/physics/cmp-slurry-flow-lubrication-film-thickness.md §5 앵커 조건
(P_app=21kPa, ω2=60rpm, R1=4in, R2=7in, μ=0.005 Pa·s)을 pack_overrides로 재현한다.
MRR 경로와 독립인 진단 필드라 mrr_nm_per_min은 건드리지 않는다.
"""
import math

from slurry_film_lubrication import z0_length_scale

from sim.engine import PSI_TO_PA, Recipe, simulate

# §5 앵커 조건
MU = 5e-3
RPM_PLATEN = 60.0
R1 = 4 * 0.0254      # 0.1016 m
R2 = 7 * 0.0254      # 0.1778 m
P_APP = 21e3         # Pa


def _anchor_recipe(pressure_pa: float = P_APP) -> Recipe:
    return Recipe(pressure_psi=pressure_pa / PSI_TO_PA, rpm_wafer=RPM_PLATEN,
                  rpm_platen=RPM_PLATEN, wafer_radius_m=R1, center_offset_m=R2,
                  pack_overrides={"slurry_viscosity_pa_s": MU})


def test_simulate_fills_z0_matching_module_value():
    res = simulate(_anchor_recipe())
    assert res.film_z0_scale_um is not None
    expected_um = z0_length_scale(MU, 2 * math.pi, R1, R2, P_APP) * 1e6   # ≈232.48 µm
    assert abs(res.film_z0_scale_um - expected_um) / expected_um < 0.01
    # summary()에도 실려야 한다
    s = res.summary()
    assert s["film_z0_scale_um"] == res.film_z0_scale_um
    assert s["film_lubrication_note"] == res.film_lubrication_note


def test_higher_pressure_lowers_z0():
    # z0 = sqrt(2μω2R1R2/P_app) — 분모에 P_app이 있으니 압력↑ → z0↓
    lo = simulate(_anchor_recipe(10e3))
    hi = simulate(_anchor_recipe(40e3))
    assert hi.film_z0_scale_um < lo.film_z0_scale_um


def test_note_present_and_mrr_path_untouched():
    res = simulate(_anchor_recipe())
    assert res.film_lubrication_note is not None
    assert isinstance(res.film_lubrication_note, str)
    # MRR 경로는 이 진단과 무관하게 그대로여야 한다
    assert res.mrr_nm_per_min.shape == res.radius_m.shape
