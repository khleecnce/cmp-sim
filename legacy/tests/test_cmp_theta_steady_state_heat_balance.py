"""Θ 정상상태 열저항 네트워크 — 문헌재현 + 엔진 진단필드 회귀.

근거: knowledge/physics/frictional-heating-temperature-arrhenius-coupling.md §8
      (White 2003 원문 Eq.3/5/9/10, Harmand 2013 회전원판 층류 h, Shin 2025 조건 3분배).
      change-detector가 아니라 문헌 수치를 assert한다.
"""
import math
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
_TIER2 = _ROOT / "sim" / "tier2_physics"
for p in (str(_ROOT), str(_TIER2)):
    if p not in sys.path:
        sys.path.insert(0, p)

from cmp_theta_steady_state_heat_balance import (  # noqa: E402
    friction_power_w, slurry_conductance_w_k, pad_conduction_conductance_w_k,
    rotating_disk_h_air, rotating_disk_reynolds, heated_annulus_area_m2,
    steady_state_heat_balance, RE_LAMINAR_LIMIT, _self_test,
)
from sim.engine import Recipe, simulate  # noqa: E402

IN, FT, PSI = 0.0254, 0.3048, 6894.757


def test_self_test_passes():
    assert _self_test()


def test_white2003_mechanical_power_eq3():
    """8 in 웨이퍼, 6 psi, 3.14 ft/s: c_f 0.25 → 320.95 W, 0.18 → 231.11 W (White 2003 Eq.3)."""
    A8 = math.pi * (4 * IN) ** 2
    assert abs(friction_power_w(0.25, 6 * PSI, A8, 3.14 * FT) - 320.95) < 2
    assert abs(friction_power_w(0.18, 6 * PSI, A8, 3.14 * FT) - 231.11) < 2


def test_white2003_conduction_and_slurry_conductance():
    """Eq.5 q_cond=41.44 W(14 K), Eq.9 ṁc_p=17.40 W/K."""
    assert abs(pad_conduction_conductance_w_k(0.02, 0.19, 1.27e-3) * 14 - 41.44) < 0.5
    assert abs(slurry_conductance_w_k(4.17e-6, 1040.0, 4010.0) - 17.40) < 0.05


def test_white2003_network_vs_measured_9p1():
    """병렬 네트워크 ΔT_ss(232 W, 1 rpm) ≈ 11.3 K — 실측 9.1 °C 대비 30% 이내, 슬러리 85%."""
    A8 = math.pi * (4 * IN) ** 2
    r = steady_state_heat_balance(232.0, 4.17e-6, 0.19, 1.27e-3, 2 * math.pi / 60,
                                  0.19 - A8, 0.30, rho_slurry=1040.0, cp_slurry=4010.0)
    assert 11.0 < r.delta_T_ss_k < 11.6
    assert abs(r.delta_T_ss_k - 9.1) / 9.1 < 0.30
    assert 0.80 < r.partition()["slurry"] < 0.90


def test_harmand_sqrt_omega_and_laminar():
    w93 = 93 * 2 * math.pi / 60
    assert abs(rotating_disk_h_air(2 * w93) / rotating_disk_h_air(w93) - math.sqrt(2)) < 1e-9
    assert rotating_disk_reynolds(w93, 0.25) < RE_LAMINAR_LIMIT
    assert 6 < rotating_disk_h_air(w93) < 8
    assert rotating_disk_h_air(0.0) == 0.0


def test_shin2025_partition_and_bounds():
    """Shin 2025 조건: ΔT_ss 12~13 K < 상한 16.5~17.5 K, 분배 슬러리 70~78/패드 15~23/공기 5~10%."""
    w93 = 93 * 2 * math.pi / 60
    A200 = math.pi * 0.1 ** 2
    A_ring = heated_annulus_area_m2(0.14, 0.1)
    assert abs(A_ring - 4 * math.pi * 0.14 * 0.1) < 1e-12
    Qf = friction_power_w(0.30, 2 * PSI, A200, w93 * 0.14)
    s = steady_state_heat_balance(Qf, 150e-6 / 60, A_ring, 1.27e-3, w93, A_ring - A200, 0.25)
    assert 12.0 < s.delta_T_ss_k < 13.0
    assert 16.5 < s.delta_T_all_slurry_upper_bound_k < 17.5
    p = s.partition()
    assert abs(sum(p.values()) - 1.0) < 1e-12
    assert 0.70 < p["slurry"] < 0.78 and 0.15 < p["pad"] < 0.23 and 0.05 < p["air"] < 0.10
    # 실측 ΔT≈15 K(Fig.7a)는 중앙값과 상한 사이 — 정직 판정(노트 §8.4)
    assert s.delta_T_ss_k < 15.0 < s.delta_T_all_slurry_upper_bound_k


# ── 엔진 진단 필드 ──────────────────────────────────────────────────────
def test_engine_fills_theta_steady_state_fields_from_base_pack():
    res = simulate(Recipe(pack="oxide_silica", time_s=60))
    assert res.theta_steady_state_delta_T_k is not None
    assert res.theta_steady_state_delta_T_k > 0
    part = res.theta_heat_partition
    assert set(part) == {"slurry", "pad", "air"}
    assert abs(sum(part.values()) - 1.0) < 1e-9
    assert part["slurry"] > 0.5            # 슬러리 수송이 지배 (노트 §8.4)
    s = res.summary()
    assert s["theta_steady_state_delta_T_k"] == res.theta_steady_state_delta_T_k
    assert s["theta_heat_partition"] == part
    assert "estimated 유지" in res.theta_steady_state_note


def test_engine_theta_ss_scales_with_flow_and_pressure_and_mrr_untouched():
    base = simulate(Recipe(pack="oxide_silica", time_s=60))
    lo_flow = simulate(Recipe(pack="oxide_silica", time_s=60,
                              pack_overrides={"sfr_ml_min": 75.0}))
    hi_p = simulate(Recipe(pack="oxide_silica", time_s=60, pressure_psi=6.0))
    assert lo_flow.theta_steady_state_delta_T_k > base.theta_steady_state_delta_T_k
    assert hi_p.theta_steady_state_delta_T_k > base.theta_steady_state_delta_T_k
    # 진단이 MRR 경로에 곱해지지 않았음: 유량만 바꾼 런의 MRR은 기준과 동일
    assert float(lo_flow.mrr_nm_per_min.mean()) == float(base.mrr_nm_per_min.mean())


def test_engine_theta_ss_quietly_none_without_pad_thickness():
    """팩에 pad_thickness_m이 없으면 진단 3필드 전부 None, 실패 노트도 없이 조용히 — 지어내지 않는다."""
    from sim.engine import _theta_steady_state_diagnostic
    rr = Recipe(pack="oxide_silica", time_s=60).resolve()
    del rr.pack.params["pad_thickness_m"]
    out = _theta_steady_state_diagnostic(rr)
    assert out == {"theta_steady_state_delta_T_k": None, "theta_heat_partition": None,
                   "theta_steady_state_note": None}
