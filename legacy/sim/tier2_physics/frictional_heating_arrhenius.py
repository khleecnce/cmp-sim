"""마찰열 → 계면 온도 → Arrhenius 화학반응속도 결합 (CMP 열-화학 커플링).

지식 근거: knowledge/physics/frictional-heating-temperature-arrhenius-coupling.md §2-4-6
구현 요청: tribologist Lv2-2 (BACKLOG 수신함 → S17)

계약 (엔진과의 경계):
  이 모듈은 "온도가 화학반응속도(→화학 MRR)를 몇 배 바꾸는가"만 답한다.
  마찰동력 q=μPV를 낼지, 그 μ·P·V를 어디서 가져올지는 호출자(엔진/chemistry.py)의
  책임이다 — 이 모듈은 순수 함수 묶음이고 Recipe/팩을 모른다.

  절대 온도값(정상상태 T_ss)은 "슬러리 전량냉각 상한"이라는 명시된 근사다(§6 (2)).
  실제 삼분배(슬러리/웨이퍼/패드) 비율은 미검증 — 노트 §7에 그대로 남는다.
  이 모듈이 그 한계를 지어내서 메우지 않는다.

함수:
  friction_heat_flux(mu, P, V)                      -> q [W/m^2]
  friction_power(q, area_m2)                        -> Q_f [W]
  mean_temp_rise_upper_bound(Q_f, rho, cp, flow_m3_s) -> dT [K] (슬러리 전량냉각 상한)
  arrhenius_rate(Ea_J_mol, lnA, T_K)                -> RR (빈도인자 단위와 동일 오더)
  arrhenius_rate_ratio(Ea_J_mol, T1_K, T2_K)        -> RR(T2)/RR(T1)
"""
from __future__ import annotations

import math
from dataclasses import dataclass

R_GAS = 8.314  # J/(K mol)


def friction_heat_flux(mu: float, pressure_pa: float, velocity_mps: float) -> float:
    """단위면적당 마찰 발열 q = mu*P*V [W/m^2].

    근거: knowledge/physics/frictional-heating-temperature-arrhenius-coupling.md §2
    """
    return mu * pressure_pa * velocity_mps


def friction_power(heat_flux_w_m2: float, area_m2: float) -> float:
    """전체 마찰동력 Q_f = q * A [W]."""
    return heat_flux_w_m2 * area_m2


def mean_temp_rise_upper_bound(power_w: float, rho_kg_m3: float, cp_j_kgk: float,
                                flow_m3_s: float) -> float:
    """마찰열 전량이 슬러리 유량으로 제거된다는 에너지균형 **상한** 온도상승 [K].

    dT = Q_f / (mdot * cp),  mdot = rho * flow_m3_s

    ⚠ 상한 추정이다 — 실제 삼분배(슬러리/웨이퍼/패드) 비율은 미검증(노트 §7).
    """
    mdot = rho_kg_m3 * flow_m3_s
    if mdot <= 0:
        raise ValueError("유량이 0 이하 — 온도상승 계산 불가")
    return power_w / (mdot * cp_j_kgk)


def arrhenius_rate(Ea_j_mol: float, lnA: float, T_kelvin: float) -> float:
    """Arrhenius 반응속도 RR = A*exp(-Ea/RT). lnA·Ea는 문헌 재료별 상수.

    근거: Shin et al. 2025, Materials 18(19) 4461, DOI 10.3390/ma18194461.
    """
    return math.exp(lnA) * math.exp(-Ea_j_mol / (R_GAS * T_kelvin))


def arrhenius_rate_ratio(Ea_j_mol: float, T1_kelvin: float, T2_kelvin: float) -> float:
    """T1→T2 사이 반응속도 배율 = exp[(Ea/R)*(1/T1 - 1/T2)]. lnA는 배율에서 상쇄된다."""
    return math.exp((Ea_j_mol / R_GAS) * (1.0 / T1_kelvin - 1.0 / T2_kelvin))


# 문헌값(Shin et al. 2025) — 화학 팩이 아직 이 값을 갖지 않는 재료는 호출자가
# 팩에서 명시적으로 채워야 한다. 여기서는 "재현 검증용 참조표"로만 둔다(코드가 곧
# 진실의 원천이 되어 팩을 우회하면 안 되므로 chemistry.py/pack에서는 이 dict를 쓰지 않는다).
SHIN2025_EA_J_MOL = {
    "SiO2": 8.75e3,
    "Ta": 29.9e3,
    "Cu": 151.7e3,
}
SHIN2025_LNA = {
    "SiO2": 9.7,
    "Ta": 18.1,
    "Cu": 66.3,
}
PAD_THERMAL_CONDUCTIVITY_W_MK = 0.02  # Shin et al. 2025


@dataclass
class ThermalChemicalResult:
    """한 런의 마찰열-화학 커플링 결과 + 근거 추적."""
    heat_flux_w_m2: float
    friction_power_w: float
    delta_T_upper_bound_k: float
    T_ss_kelvin: float
    rate_ratio_vs_ref: float

    def describe(self) -> str:
        return (f"q={self.heat_flux_w_m2:.0f} W/m^2, Q_f={self.friction_power_w:.0f} W, "
                f"ΔT_상한={self.delta_T_upper_bound_k:.1f} K, "
                f"반응속도 배율(기준 대비)={self.rate_ratio_vs_ref:.2f}x")


def thermal_chemical_coupling(mu: float, pressure_pa: float, velocity_mps: float,
                               area_m2: float, rho_kg_m3: float, cp_j_kgk: float,
                               flow_m3_s: float, T_ref_kelvin: float,
                               Ea_j_mol: float) -> ThermalChemicalResult:
    """전체 사슬 q → Q_f → ΔT(상한) → T_ss → Arrhenius 배율(T_ref 대비).

    호출자는 pack에서 mu(또는 tribology_basics.stribeck_cof 결과)·P·V·유량·재료 Ea를
    가져와 넘긴다. 이 함수는 그 값들을 검증하지 않는다(값의 출처는 호출자 책임).
    """
    q = friction_heat_flux(mu, pressure_pa, velocity_mps)
    Qf = friction_power(q, area_m2)
    dT = mean_temp_rise_upper_bound(Qf, rho_kg_m3, cp_j_kgk, flow_m3_s)
    T_ss = T_ref_kelvin + dT
    ratio = arrhenius_rate_ratio(Ea_j_mol, T_ref_kelvin, T_ss)
    return ThermalChemicalResult(heat_flux_w_m2=q, friction_power_w=Qf,
                                  delta_T_upper_bound_k=dT, T_ss_kelvin=T_ss,
                                  rate_ratio_vs_ref=ratio)
