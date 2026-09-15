"""장비 출력값 (Derived Equipment Outputs) — ARCHITECTURE-V2.md §1-①.

사용자 지시(2026-09-08):
  "설정값말고도 출력값이 있어야해. 즉 우리가 넣는 값이 아니라 저절로 도출되는
   패드온도, carrier current(마찰) 등 장비적인 요소를 대입해."

이 구분이 왜 중요한가
────────────────────
실제 폴리셔 앞에 선 엔지니어는 두 종류의 숫자를 본다:
  - **설정값**: 자기가 넣는 것 (압력·RPM·SFR·컨디셔너 하중)
  - **출력값**: 장비가 알려주는 것 (패드 온도, 모터 전류, 진동)

출력값은 공정이 정상인지 판정하는 신호다. 모터 전류가 튀면 패드가 glazing된
것이고, 온도가 올라가면 화학속도가 변한다. **설정값만 있는 시뮬레이터는
'돌려보는 것'이지 '진단하는 것'이 아니다.**

⚠ 이 모듈은 물리 모듈을 새로 쓰지 않는다. 이미 검증된 tier2 모듈
(friction_cof_epd, frictional_heating_arrhenius)을 조립만 한다.
"""
from __future__ import annotations

import math
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from sim.engine import ResolvedRecipe

_ROOT = Path(__file__).resolve().parent
for _tier in ("tier1_empirical", "tier2_physics", "tier3_surrogate"):
    _p = str(_ROOT / _tier)
    if _p not in sys.path:
        sys.path.insert(0, _p)

PSI_TO_PA = 6894.757


@dataclass
class Output:
    """장비가 '저절로 내놓는' 값 하나."""
    key: str
    label: str
    value: Optional[float]
    unit: str
    status: str = "computed"        # computed | unmodeled
    confidence: str = "unverified"
    sources: List[str] = field(default_factory=list)
    note: str = ""

    def to_dict(self) -> Dict:
        return {"key": self.key, "label": self.label, "value": self.value,
                "unit": self.unit, "status": self.status,
                "confidence": self.confidence, "sources": self.sources,
                "note": self.note}


def _unmodeled(key: str, label: str, unit: str, why: str) -> Output:
    return Output(key=key, label=label, value=None, unit=unit,
                  status="unmodeled", note=why)


def compute_outputs(rr: "ResolvedRecipe") -> Dict[str, Output]:
    """설정값에서 도출되는 장비 출력값 전부.

    계산 불가한 항목은 **지어내지 않고** status='unmodeled' + 이유를 남긴다.
    """
    import friction_cof_epd as FC
    import frictional_heating_arrhenius as FH

    pk = rr.pack
    out: Dict[str, Output] = {}

    P_pa = float(rr.pressure_psi) * PSI_TO_PA
    r_w = float(rr.wafer_radius_m)
    area = math.pi * r_w * r_w
    r_cc = float(rr.center_offset_m)
    omega_p = float(rr.rpm_platen) * 2.0 * math.pi / 60.0
    V = omega_p * r_cc          # 상대속도 대표값 (Rs=1에서 반경 무관)

    # ── ① 마찰계수 ─────────────────────────────────────────
    # ⚠ 여기서 Stribeck 곡선을 새로 쓰지 않는다. tier2의 검증된 구현
    #   (cmp_lubrication_regime.cof_stribeck, self-test PASS)을 그대로 호출한다.
    #
    #   왜 이 주의가 붙어 있나 (2026-09-08 실제 사고):
    #   처음엔 로지스틱 보간을 직접 지어냈다. 그 형태에서는 CMP 전형 조건이
    #   전부 '유체' 가지에 들어가 μ = k_h·So ∝ 1/P 가 되고, 결과적으로
    #   μ·P = 상수 → **마찰 발열이 압력에 전혀 반응하지 않았다.** 다운포스를
    #   1→8 psi로 8배 올려도 패드 온도가 11.632 K로 고정이었다. 물리적으로
    #   말이 안 되는데 코드는 조용히 돌아갔다. 검증된 함수를 쓰면 접촉분율
    #   f = exp(-α·So)가 경계 성분을 살려 이 붕괴가 일어나지 않는다.
    mu = None
    mu_conf = "unverified"
    mu_note = ""
    try:
        import cmp_lubrication_regime as LR
        if pk.has("slurry_viscosity_pa_s") and pk.has("pad_ra_m"):
            eta = float(pk.get("slurry_viscosity_pa_s"))
            ra = float(pk.get("pad_ra_m"))
            So = LR.cmp_sommerfeld(eta, V, P_pa, ra)
            mu = LR.cof_stribeck(
                So,
                mu_bl=float(pk.get_or("cof_boundary", 0.30)),
                c_hydro=float(pk.get_or("cof_hydro_coeff", 8.0)),
                alpha_tr=float(pk.get_or("cof_transition_alpha", 40.0)))
            mu_conf = "estimated"
            mu_note = (f"Stribeck (So={So:.3e}, 경계·혼합 영역). ⚠ COF 절대값은 "
                       "정성적 오더 추정이며 실측 캘리브레이션이 필요하다(노트 §5,§7).")
    except Exception as _e:
        mu_note = f"⚠ 윤활 모듈 호출 실패: {type(_e).__name__}"
    if mu is None:
        mu = float(pk.get_or("cof_boundary", 0.30))
        mu_note = (mu_note + " ⚠ 슬러리 점도·패드 Ra가 없어 Stribeck을 못 풀었다 — "
                   "경계윤활 대표값으로 폴백했다. 윤활 영역 변화가 반영되지 않는다.").strip()
    out["cof"] = Output("cof", "마찰계수 μ", float(mu), "-", "computed", mu_conf,
                        ["knowledge/physics/tribology-friction-wear-stribeck.md",
                         "knowledge/physics/cmp-lubrication-regimes.md"], mu_note)

    # ── ② 마찰력·토크·모터 전류 ────────────────────────────
    F_n = FC.normal_force(P_pa, area)
    F_s = FC.shear_force(mu, P_pa, area)
    torque = FC.platen_torque(F_s, r_cc)
    power = FC.motor_power_friction(torque, omega_p)

    out["friction_force_n"] = Output(
        "friction_force_n", "마찰력 F_s", float(F_s), "N", "computed", "literature",
        ["knowledge/physics/friction-cof-monitoring-endpoint-detection.md"],
        "F_s = μ·P·A (Amontons)")
    out["platen_torque_nm"] = Output(
        "platen_torque_nm", "플래튼 토크 τ", float(torque), "N·m", "computed",
        "literature",
        ["knowledge/physics/friction-cof-monitoring-endpoint-detection.md"],
        "τ ≈ F_s·r_cc")
    out["friction_power_w"] = Output(
        "friction_power_w", "마찰 동력", float(power), "W", "computed", "literature",
        ["knowledge/physics/friction-cof-monitoring-endpoint-detection.md"],
        "P = τ·ω = q·A — 모터가 쓰는 동력과 계면 발열은 같은 물리량이다")

    if pk.has("motor_torque_constant_nm_per_a"):
        kt = float(pk.get("motor_torque_constant_nm_per_a"))
        try:
            cur = FC.motor_current(torque, kt)
            out["carrier_current_a"] = Output(
                "carrier_current_a", "캐리어/플래튼 모터 전류", float(cur), "A",
                "computed", "unverified",
                ["knowledge/physics/friction-cof-monitoring-endpoint-detection.md"],
                "I = τ/K_t. ⚠ K_t는 장비상수라 절대값 미검증 — 비례성(상대 변화)만 "
                "신뢰하라. 종점검출은 절대값이 아니라 변화점을 본다.")
        except ValueError as e:
            out["carrier_current_a"] = _unmodeled(
                "carrier_current_a", "캐리어/플래튼 모터 전류", "A", str(e))
    else:
        out["carrier_current_a"] = _unmodeled(
            "carrier_current_a", "캐리어/플래튼 모터 전류", "A",
            "⚠ 모터 토크상수(motor_torque_constant_nm_per_a)가 팩에 없다. "
            "토크는 계산됐으므로 K_t만 넣으면 전류가 나온다 — 장비별 상수다. "
            "담당 R1-equipment.")

    # ── ③ 패드 온도 상승 ──────────────────────────────────
    # 마찰 발열이 슬러리 유량으로 전부 제거된다는 에너지 균형 = **상한**.
    q = FH.friction_heat_flux(mu, P_pa, V)
    out["heat_flux_w_m2"] = Output(
        "heat_flux_w_m2", "마찰 열유속 q", float(q), "W/m²", "computed", "literature",
        ["knowledge/physics/frictional-heating-temperature-arrhenius-coupling.md"],
        "q = μ·P·V")

    if pk.has("sfr_ml_min"):
        sfr = float(pk.get("sfr_ml_min"))
        flow_m3_s = sfr * 1e-6 / 60.0
        rho = float(pk.get_or("slurry_density_kg_m3", 1000.0))
        cp = float(pk.get_or("slurry_cp_j_kgk", 4180.0))
        try:
            dT = FH.mean_temp_rise_upper_bound(FH.friction_power(q, area),
                                               rho, cp, flow_m3_s)
            t_amb = float(pk.get_or("ambient_temp_c", 22.0))
            out["pad_temp_rise_k"] = Output(
                "pad_temp_rise_k", "패드 온도상승 ΔT", float(dT), "K",
                "computed", "estimated",
                ["knowledge/physics/frictional-heating-temperature-"
                 "arrhenius-coupling.md"],
                "⚠ **상한값이다** — 마찰열 전량이 슬러리로 제거된다는 가정. 실제는 "
                "슬러리/웨이퍼/패드 삼분배이고 그 비율은 미검증(노트 §7). "
                "실제 ΔT는 이보다 작다.")
            out["pad_temp_c"] = Output(
                "pad_temp_c", "패드 온도(추정)", float(t_amb + dT), "°C",
                "computed", "estimated",
                ["knowledge/physics/frictional-heating-temperature-"
                 "arrhenius-coupling.md"],
                f"주변온도 {t_amb:g}°C + ΔT 상한. 절대값보다 **경향**을 보라.")
        except ValueError as e:
            out["pad_temp_rise_k"] = _unmodeled(
                "pad_temp_rise_k", "패드 온도상승 ΔT", "K", str(e))
    else:
        why = ("⚠ SFR(슬러리 유량)이 팩에 없어 냉각항을 못 푼다. 발열(q)은 계산됐다 "
               "— 유량만 넣으면 온도가 나온다. 담당 R1-equipment.")
        out["pad_temp_rise_k"] = _unmodeled("pad_temp_rise_k", "패드 온도상승 ΔT", "K", why)
        out["pad_temp_c"] = _unmodeled("pad_temp_c", "패드 온도(추정)", "°C", why)

    # ── ④ 아직 물리가 없는 출력 — 자리만 두고 숨기지 않는다 ──
    out["vibration"] = _unmodeled(
        "vibration", "진동/음향 신호", "-",
        "⚠ 미모델링: 진동·AE 신호 모델이 없다. 스크래치·패드 이상의 조기 신호로 "
        "실무에서 쓰이지만 엔진에 통로가 없다. 담당 R1-equipment × defect.")
    out["slurry_film_um"] = _unmodeled(
        "slurry_film_um", "슬러리 필름 두께", "µm",
        "⚠ engine의 film_z0_scale_um 진단이 별도로 계산한다 — 여기서 중복 계산하지 "
        "않는다. WaferResult.film_z0_scale_um를 보라.")

    return out


def summarize(outs: Dict[str, Output]) -> Dict[str, object]:
    computed = [k for k, o in outs.items() if o.status == "computed"]
    unmodeled = [k for k, o in outs.items() if o.status == "unmodeled"]
    return {"computed": sorted(computed), "unmodeled": sorted(unmodeled),
            "score": round(len(computed) / max(len(outs), 1), 3)}
