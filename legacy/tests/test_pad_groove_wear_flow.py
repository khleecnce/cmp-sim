"""pad_groove_wear_flow.py 회귀 테스트.

노트 knowledge/materials/pad-groove-wear-flow-change-end-of-life.md §5 verify
(A)/(A')/(B)/(D)/(E) 블록의 숫자·허용오차를 그대로 옮긴다(새 문헌 숫자 없음).
(A')는 US8192257B2 "6000-8000 wafers" 불일치 기록(§5 A')이며 함수화 대상이 아니라서
assert가 아니라 이 docstring에만 남긴다: std_wafers(6000~8000) * 0.25 μm/wafer =
1.5-2.0 mm 누적마모 > 통상 초기 그루브 깊이 상한 1.25 mm — 같은 마모율로는 재현 안 됨.
"""
import math

import pad_groove_wear_flow as gw


# ── (A) US8192257B2 x US11938584B2 ──────────────────────────────────────────

def test_arithmetic_exhaustion_limit_1000_wafers():
    assert abs(250.0 / 0.25 - 1000) < 1e-9


def test_micron_life_600_800_residual_20_40_pct():
    D1_um, wear = 250.0, 0.25
    remain_hi = D1_um - 600 * wear
    remain_lo = D1_um - 800 * wear
    assert (remain_lo, remain_hi) == (50.0, 100.0)
    frac_lo, frac_hi = remain_lo / D1_um, remain_hi / D1_um
    assert abs(frac_lo - 0.20) < 1e-9 and abs(frac_hi - 0.40) < 1e-9


def test_micron_cabot_life_wafers_matches_micron_upper_bound():
    N_cabot = gw.micron_cabot_life_wafers(250.0, 0.25, usable_fraction=0.80)
    assert 600 <= N_cabot <= 800
    assert N_cabot == 800.0


# ── groove_depth_um / residual_depth_fraction ───────────────────────────────

def test_groove_depth_um_linear_decay():
    assert gw.groove_depth_um(250.0, 0.25, 100.0) == 225.0


def test_groove_depth_um_clamped_at_zero():
    assert gw.groove_depth_um(250.0, 0.25, 5000.0) == 0.0


def test_residual_depth_fraction():
    assert abs(gw.residual_depth_fraction(100.0, 250.0) - 0.40) < 1e-9


# ── wear_stage 3단계 경계 ────────────────────────────────────────────────────

def test_wear_stage_initial_boundary():
    assert gw.wear_stage(70.0, 100.0) == "initial"
    assert gw.wear_stage(69.999, 100.0) == "mid"


def test_wear_stage_end_of_life_boundary():
    assert gw.wear_stage(35.0, 100.0) == "mid"
    assert gw.wear_stage(34.999, 100.0) == "end_of_life"


def test_wear_stage_initial_and_end_of_life_extremes():
    assert gw.wear_stage(100.0, 100.0) == "initial"
    assert gw.wear_stage(0.0, 100.0) == "end_of_life"


# ── (D) Mu 2016 Table 2 재현 (3 PSI, film 15 μm, 200 mm 웨이퍼, D0=400 μm) ─

GFQ = {'A': 300 / 1500, 'B': 600 / 1800, 'C': 900 / 2100}
TABLE2_3PSI = {  # pad: (V_land, V_groove) [cm3]
    'A': (0.38, 2.66),
    'B': (0.31, 4.41),
    'C': (0.27, 5.64),
}


def test_slurry_volumes_cm3_land_reproduction_within_3pct():
    for pad, (vl_lit, _) in TABLE2_3PSI.items():
        V_land, _, _ = gw.slurry_volumes_cm3(400.0, GFQ[pad], 15.0)
        assert abs(V_land - vl_lit) / vl_lit < 0.03


def test_slurry_volumes_cm3_groove_residual_3_to_7pct():
    for pad, (_, vg_lit) in TABLE2_3PSI.items():
        _, V_groove, _ = gw.slurry_volumes_cm3(400.0, GFQ[pad], 15.0)
        resid = abs(V_groove - vg_lit) / vg_lit
        assert 0.03 < resid < 0.07


def test_slurry_volumes_cm3_groove_dominates_land():
    for pad, (vl_lit, vg_lit) in TABLE2_3PSI.items():
        assert vg_lit / vl_lit >= 6.9


def test_residence_time_s_pad_a_projection_400_to_250um():
    gfq_A = GFQ['A']
    _, _, V_total_400 = gw.slurry_volumes_cm3(400.0, gfq_A, 15.0)
    tau_A3 = 9.2
    q_actual = V_total_400 / tau_A3
    tau_250 = gw.residence_time_s(250.0, gfq_A, 15.0, q_actual)
    assert 6.0 < tau_250 < 6.4


# ── (E) Irfan 2025 기하 (w=0.5 mm, D0=0.75 mm=750 um) ───────────────────────

def test_conductance_ratio_at_half_life_depth():
    r50 = gw.conductance_ratio(500.0, 750.0, 0.5)
    assert 0.45 < r50 < 0.50


def test_conductance_ratio_at_end_of_life_depth():
    r25 = gw.conductance_ratio(250.0, 750.0, 0.5)
    assert 0.09 < r25 < 0.11


def test_conductance_ratio_drops_faster_than_depth_ratio():
    r50 = gw.conductance_ratio(500.0, 750.0, 0.5)
    r25 = gw.conductance_ratio(250.0, 750.0, 0.5)
    assert r25 < r50 < 1
    assert r25 < 250.0 / 750.0
    assert r50 < 500.0 / 750.0


def test_rectangular_channel_conductance_swaps_wide_narrow():
    assert gw.rectangular_channel_conductance(0.5, 0.75) == gw.rectangular_channel_conductance(0.75, 0.5)


# ── 종합 함수 통합 테스트 ────────────────────────────────────────────────────

def test_groove_wear_flow_state_matches_individual_functions():
    D0_um, cut_rate, GFQ_A, h_land, q_actual, t = 400.0, 0.25, GFQ['A'], 15.0, 0.3141, 600.0
    state = gw.groove_wear_flow_state(D0_um, cut_rate, GFQ_A, h_land, q_actual, t)

    D_um = gw.groove_depth_um(D0_um, cut_rate, t)
    assert state["D_um"] == D_um
    assert state["residual_fraction"] == gw.residual_depth_fraction(D_um, D0_um)
    assert state["stage"] == gw.wear_stage(D_um, D0_um)
    assert state["tau_s"] == gw.residence_time_s(D_um, GFQ_A, h_land, q_actual)
    assert state["conductance_ratio"] == gw.conductance_ratio(D_um, D0_um, 0.5)

    V_land, V_groove, V_total = gw.slurry_volumes_cm3(D_um, GFQ_A, h_land)
    assert state["V_land_cm3"] == V_land
    assert state["V_groove_cm3"] == V_groove
    assert state["V_total_cm3"] == V_total

    assert abs(D_um - 250.0) < 1e-9
    assert state["stage"] == "mid"
