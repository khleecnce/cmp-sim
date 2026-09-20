"""마찰열-Arrhenius 커플링 계약/문헌재현 테스트.

근거: knowledge/physics/frictional-heating-temperature-arrhenius-coupling.md §6
      (지식노트의 python verify 블록 수치를 그대로 재현 — change-detector 아님,
       문헌·해석해 대조값을 assert한다)
"""
import math
import sys
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parent.parent
_TIER2 = _ROOT / "sim" / "tier2_physics"
for p in (str(_ROOT), str(_TIER2)):
    if p not in sys.path:
        sys.path.insert(0, p)

from frictional_heating_arrhenius import (  # noqa: E402
    friction_heat_flux, friction_power, mean_temp_rise_upper_bound,
    arrhenius_rate, arrhenius_rate_ratio, thermal_chemical_coupling,
    SHIN2025_EA_J_MOL, SHIN2025_LNA, R_GAS,
)


def test_heat_flux_matches_ma2023_condition():
    """Ma et al. 2023 조건(mu=0.3, P=0.05MPa, V=0.75m/s) -> q=uPV=11250 W/m^2."""
    q = friction_heat_flux(mu=0.3, pressure_pa=0.05e6, velocity_mps=0.75)
    assert abs(q - 11250) < 1


def test_friction_power_matches_white2003_order_of_magnitude():
    """200mm 웨이퍼에서 Q_f가 White et al.(2003) 200~300W 오더와 일치."""
    q = friction_heat_flux(mu=0.3, pressure_pa=0.05e6, velocity_mps=0.75)
    A = math.pi * 0.1 ** 2
    Qf = friction_power(q, A)
    assert 100 < Qf < 700  # White 2003 재인용 200~300W와 같은 오더


def test_temp_rise_upper_bound_matches_shin2025_order():
    """전량냉각 상한 dT가 Shin et al.(2025) 실측 수~수십C(무제어~36C) 오더와 일치."""
    rho, cp, flow = 1000.0, 4180.0, 150e-6 / 60  # 물기반, 150 mL/min
    for Qh in (200.0, 300.0):
        dT = mean_temp_rise_upper_bound(Qh, rho, cp, flow)
        assert 5 < dT < 40


def test_arrhenius_ratio_reproduces_shin2025_cu_selectivity():
    """30->50C: Cu ~41.5x, Ta ~2.08x, SiO2 ~1.24x — 문헌 핵심 주장 정량 재현."""
    T1, T2 = 303.15, 323.15
    r_cu = arrhenius_rate_ratio(SHIN2025_EA_J_MOL["Cu"], T1, T2)
    r_ta = arrhenius_rate_ratio(SHIN2025_EA_J_MOL["Ta"], T1, T2)
    r_ox = arrhenius_rate_ratio(SHIN2025_EA_J_MOL["SiO2"], T1, T2)
    assert 35 < r_cu < 50
    assert 1.1 < r_ox < 1.4
    assert r_cu > 20 * r_ox  # Cu가 oxide보다 훨씬 온도민감 -> 선택비 급변


def test_arrhenius_rate_matches_shin2025_cu_room_temp_order():
    """Cu lnA=66.3, Ea=151.7kJ/mol @303K -> 수백 A/min 오더 (Shin: 30C 부근 400~500)."""
    RR = arrhenius_rate(SHIN2025_EA_J_MOL["Cu"], SHIN2025_LNA["Cu"], 303.15)
    assert 100 < RR < 2000


def test_full_chain_end_to_end_ratio_positive_and_gt_one_when_heating():
    """전체 사슬(q->Qf->dT->T_ss->배율)이 가열 시 배율>1을 낸다 (Cu, 방향성 계약)."""
    res = thermal_chemical_coupling(
        mu=0.3, pressure_pa=0.05e6, velocity_mps=0.75,
        area_m2=math.pi * 0.1 ** 2, rho_kg_m3=1000.0, cp_j_kgk=4180.0,
        flow_m3_s=150e-6 / 60, T_ref_kelvin=303.15, Ea_j_mol=SHIN2025_EA_J_MOL["Cu"])
    assert res.rate_ratio_vs_ref > 1.0
    assert res.T_ss_kelvin > 303.15
    assert res.heat_flux_w_m2 > 0


def test_mean_temp_rise_rejects_zero_flow():
    with pytest.raises(ValueError):
        mean_temp_rise_upper_bound(200.0, 1000.0, 4180.0, 0.0)


def test_softening_exponent_not_used_here_module_is_pure_thermal():
    """이 모듈은 chemistry.py의 경도-연화 지수(1.5)를 다루지 않는다 — 경계 확인용 계약 테스트.

    (열-화학 결합은 아직 sim.chemistry에 연결되지 않았다. BACKLOG S17 남은 작업으로 명시.)
    """
    import frictional_heating_arrhenius as fha
    assert not hasattr(fha, "SOFTENING_EXPONENT")
