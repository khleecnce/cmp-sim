"""슬롯 아키텍처 — 시뮬레이션 파이프라인을 갈아끼울 수 있는 단위로 쪼갠다.

왜 (2026-09-05 사용자: "클릭만으로 갈아끼울 수 있는 인터페이스"):
  기존 engine.Model은 모델 하나가 압력·속도·Kp·적분을 전부 담당했다. 그래서
  "GW 접촉모델만 바꾸고 압력 프로파일은 그대로" 같은 조합이 불가능했다.
  파이프라인을 슬롯으로 쪼개면 조합이 가능해지고, 그게 곧 UI의 클릭 단위가 된다.

파이프라인:
    Recipe
      → [pressure]  반경별 압력 P(r) [Pa]
      → [velocity]  반경별 상대속도 V(r) [m/s]
      → [kp]        Preston 계수 Kp(r, P, V) [m/Pa] — 상수일 수도, 물리 유도일 수도
      → [removal]   MRR(r) = f(Kp, P, V) [m/s]
      → [pattern]   PTW 패턴 보정 (NPW면 통과)
      → [wear]      패드 마모 시간 보정 (미해결 시 통과)
    → WaferResult

각 구현(Impl)은 자기 출처(어느 노트·어느 에이전트)와 검증 상태를 신고한다.
근거 없는 구현은 UI에서 빨갛게 뜬다 — 숨길 수 없게.
"""
from __future__ import annotations

import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Dict, List, Optional

import numpy as np

_ROOT = Path(__file__).resolve().parent
for _p in ("tier1_empirical", "tier2_physics", "integration"):
    _d = str(_ROOT / _p)
    if _d not in sys.path:
        sys.path.insert(0, _d)

PSI_TO_PA = 6894.757

# 슬롯 정의 — 순서가 곧 파이프라인 순서
SLOT_ORDER = ["pressure", "velocity", "kp", "removal", "pattern", "wear"]
SLOT_LABEL = {
    "pressure": "압력 분포 P(r)",
    "velocity": "상대속도 V(r)",
    "kp": "Preston 계수 Kp",
    "removal": "제거율 적분",
    "pattern": "PTW 패턴 보정",
    "wear": "패드 마모 보정",
}
SLOT_OWNER = {
    "pressure": "tool-platen-head",
    "velocity": "process-integrator",
    "kp": "pad-mechanic / slurry-chemist",
    "removal": "cmp-integrator",
    "pattern": "wafer-type / film-*",
    "wear": "pad-lifecycle",
}


@dataclass
class Impl:
    """슬롯에 꽂히는 구현 하나."""
    id: str
    slot: str
    label: str
    fn: Callable
    # 출처 — 이게 없으면 UI가 경고한다
    note: Optional[str] = None          # knowledge/... 경로
    module: Optional[str] = None        # sim/... 경로
    agent: Optional[str] = None         # 작성 에이전트
    verified: bool = False              # 문헌값 재현 테스트가 있는가
    warning: Optional[str] = None       # 알려진 한계 (있으면 결과 notes에 실림)
    params: Dict[str, str] = field(default_factory=dict)   # 조절 가능한 파라미터 설명

    @property
    def status(self) -> str:
        if self.warning:
            return "warn"
        if not self.note:
            return "unsourced"
        return "verified" if self.verified else "sourced"


_REG: Dict[str, Dict[str, Impl]] = {s: {} for s in SLOT_ORDER}


def register(impl: Impl) -> None:
    _REG[impl.slot][impl.id] = impl


def slots() -> Dict[str, Dict[str, Impl]]:
    return _REG


def default_config() -> Dict[str, str]:
    """슬롯별 기본 선택 — 가장 근거가 확실한 것."""
    return {
        "pressure": "zoned_or_uniform",
        "velocity": "kinematics_rotational_avg",
        "kp": "constant",
        "removal": "preston",
        "pattern": "none",
        "wear": "none",
    }


# ══════════════════════════════════════════════ pressure
def _p_uniform_or_zoned(recipe, r, cfg):
    P0 = recipe.pressure_psi * PSI_TO_PA
    rn = r / max(recipe.wafer_radius_m, 1e-9)
    if recipe.zone_pressures_psi:
        edges = list(recipe.zone_edges_norm or
                     np.linspace(0, 1, len(recipe.zone_pressures_psi) + 1)[1:])
        if edges[0] != 0.0:
            edges = [0.0] + edges
        P = np.full_like(r, recipe.zone_pressures_psi[-1] * PSI_TO_PA)
        for i, pz in enumerate(recipe.zone_pressures_psi):
            lo, hi = edges[i], edges[i + 1] if i + 1 < len(edges) else 1.0
            P[(rn >= lo) & (rn <= hi)] = pz * PSI_TO_PA
        return P
    return P0 * (1.0 + recipe.edge_pressure_amp * rn ** 4)


def _p_gw_local(recipe, r, cfg):
    """GW 접촉역학: 공칭압 → asperity 국소압. 근거: gw-nominal-vs-local-pressure"""
    import gw_contact as gw
    P_nom = _p_uniform_or_zoned(recipe, r, cfg)
    out = np.empty_like(P_nom)
    for i, p in enumerate(P_nom):
        try:
            res = gw.gw_contact_from_load(W=float(p) * 1e-4, A_n=1e-4)
            out[i] = res.get("p_real", p) if isinstance(res, dict) else p
        except Exception:
            out[i] = p
    return out


register(Impl("zoned_or_uniform", "pressure", "존압력 / 균일 + 엣지집중",
              _p_uniform_or_zoned,
              note="knowledge/cmp/wiwnu-pressure-velocity-wafer-scale",
              module="sim/tier1_empirical/wiwnu.py",
              agent="process-integrator", verified=True,
              params={"zone_pressures_psi": "존별 압력", "edge_pressure_amp": "엣지 집중 진폭"}))
register(Impl("gw_local", "pressure", "GW 국소 접촉압 (asperity)",
              _p_gw_local,
              note="knowledge/materials/gw-nominal-vs-local-pressure",
              module="sim/tier2_physics/gw_contact.py",
              agent="pad-mechanic", verified=False,
              warning="asperity 국소압 변환은 공칭압 대비 스케일이 크게 달라 "
                      "Kp 재캘리브레이션 없이 쓰면 절대값이 틀린다. 실험용."))


# ══════════════════════════════════════════════ velocity
def _v_rotational_avg(recipe, r, cfg):
    """자전 평균 상대속도. 근거: cmp-kinematics-rotary (verify 블록 통과)"""
    import kinematics as kin
    w_w = kin.rpm_to_rads(recipe.rpm_wafer)
    w_p = kin.rpm_to_rads(recipe.rpm_platen)
    th = np.linspace(0, 2 * np.pi, 181)
    out = np.empty_like(r)
    Rw = max(recipe.wafer_radius_m, 1e-9)
    for i, rr in enumerate(r):
        v = kin.relative_speed_polar(np.full_like(th, rr / Rw), th,
                                     w_w, w_p, recipe.center_offset_m, Rw)
        out[i] = float(np.mean(v))
    return out


def _v_constant(recipe, r, cfg):
    """Rs=1 근사: 전면 |v| = ω_p·r_cc 상수."""
    import kinematics as kin
    return np.full_like(r, kin.rpm_to_rads(recipe.rpm_platen) * recipe.center_offset_m)


register(Impl("kinematics_rotational_avg", "velocity", "자전 평균 (반경별)",
              _v_rotational_avg,
              note="knowledge/physics/cmp-kinematics-rotary",
              module="sim/tier1_empirical/kinematics.py",
              agent="process-integrator", verified=True,
              params={"rpm_wafer": "웨이퍼 rpm", "rpm_platen": "플래튼 rpm",
                      "center_offset_m": "중심간 거리 r_cc"}))
register(Impl("constant_rs1", "velocity", "Rs=1 상수 근사",
              _v_constant,
              note="knowledge/physics/cmp-kinematics-rotary",
              module="sim/tier1_empirical/kinematics.py",
              agent="process-integrator", verified=True,
              warning="Rs≠1이면 반경 의존을 놓친다. 빠른 스루풋 추정용."))


# ══════════════════════════════════════════════ kp
def _kp_constant(recipe, r, P, V, cfg):
    return np.full_like(r, recipe.kp_m_per_pa)


def _kp_gw_physical(recipe, r, P, V, cfg):
    """GW 접촉점 수에서 Kp를 유도. 근거: gw_preston_link (pad-mechanic Lv3-2)"""
    import gw_preston_link as gpl
    P_ref, V_ref = float(np.mean(P)), float(np.mean(V))
    alpha = gpl.calibrate_alpha_removal(P_ref, V_ref, recipe.kp_m_per_pa)
    mrr = np.array([gpl.mrr_gw_link(p, v, alpha) for p, v in zip(P, V)])
    with np.errstate(divide="ignore", invalid="ignore"):
        return np.where(P * V > 0, mrr / (P * V), recipe.kp_m_per_pa)


register(Impl("constant", "kp", "상수 Kp (Preston 원형)",
              _kp_constant,
              note="knowledge/cmp/preston-luo-dornfeld-mrr",
              module="sim/tier1_empirical/preston.py",
              agent="process-integrator", verified=False,
              warning="Kp=1.6e-13은 오더값(출처: 공학계산기 FAQ, 미검증). "
                      "실데이터 캘리브레이션(M3) 대상 1순위.",
              params={"kp_m_per_pa": "Preston 계수"}))
register(Impl("gw_physical", "kp", "GW 접촉역학 유도 Kp",
              _kp_gw_physical,
              note="knowledge/materials/gw-nominal-vs-local-pressure",
              module="sim/tier2_physics/gw_preston_link.py",
              agent="pad-mechanic", verified=True,
              params={"kp_m_per_pa": "캘리브레이션 기준 Kp"}))


# ══════════════════════════════════════════════ removal
def _mrr_preston(recipe, r, P, V, Kp, cfg):
    return Kp * P * V


register(Impl("preston", "removal", "Preston MRR = Kp·P·V",
              _mrr_preston,
              note="knowledge/cmp/preston-luo-dornfeld-mrr",
              module="sim/tier1_empirical/preston.py",
              agent="process-integrator", verified=True))


# ══════════════════════════════════════════════ pattern (PTW)
def _pat_none(recipe, r, mrr, cfg):
    return mrr, []


def _pat_incompressible(recipe, r, mrr, cfg):
    """비압축 극한: MRR_up = MRR_blanket / rho_eff (Stine 1997)"""
    if recipe.wafer != "PTW":
        return mrr, ["NPW: 패턴 보정 없음"]
    rho = float(getattr(recipe, "meta", getattr(recipe, "base", recipe).meta if hasattr(recipe, "base") else {}).get("pattern_density", 0.5) or 0.5)
    notes = [f"PTW up-area = 블랭킷/ρ (ρ={rho:g}, 비압축 극한, Stine 1997). 초기 단계에만 유효."]
    if rho < 0.15:
        notes.append(f"⚠ ρ={rho:g} < 0.15 — 1/ρ 발산. ρ=0.15로 클램프.")
        rho = 0.15
    return mrr / min(max(rho, 0.15), 1.0), notes


register(Impl("none", "pattern", "보정 없음 (NPW)",
              _pat_none, note="—", verified=True))
register(Impl("incompressible", "pattern", "비압축 극한 1/ρ",
              _pat_incompressible,
              note="knowledge/cmp/pattern-dependent-dishing-erosion",
              module="sim/tier1_empirical/pattern_density.py",
              agent="process-integrator", verified=False,
              warning="dishing/erosion 미산출 — 막질별 Kp 필요(film-cu·film-w 대기).",
              params={"pattern_density": "평균 패턴 밀도 ρ (0~1)"}))


# ══════════════════════════════════════════════ wear
def _wear_none(recipe, r, mrr, cfg):
    h = float(getattr(recipe, "meta", getattr(recipe, "base", recipe).meta if hasattr(recipe, "base") else {}).get("pad_hours", 0) or 0)
    if h > 0:
        return mrr, [f"패드 {h:g}h 입력됐으나 보정 없음 — 아래 '모순' 참조"]
    return mrr, []


def _wear_contradiction(recipe, r, mrr, cfg):
    """⚠ 미해결: ad-hoc(MRR↓) vs GW(MRR↑)가 corr=-0.998로 정반대."""
    h = float(getattr(recipe, "meta", getattr(recipe, "base", recipe).meta if hasattr(recipe, "base") else {}).get("pad_hours", 0) or 0)
    if h <= 0:
        return mrr, []
    return mrr, [
        f"패드 {h:g}h — 시간 보정을 적용하지 않았다. ad-hoc 모델(MRR 감소)과 "
        "GW 물리 모델(MRR 증가)이 corr=-0.998로 정반대다. 어느 쪽이 옳은지 "
        "미해결이므로 새 패드 기준값을 반환한다(BACKLOG S13)."
    ]


register(Impl("none", "wear", "보정 없음 (새 패드)",
              _wear_none, note="—", verified=True))
register(Impl("unresolved", "wear", "마모 모순 보고 (보정 안 함)",
              _wear_contradiction,
              note="knowledge/materials/pad-wear-glazing-mrr-decay",
              module="sim/tier2_physics/wear_aware_kp_physical.py",
              agent="pad-mechanic", verified=False,
              warning="ad-hoc과 GW 물리 모델이 정반대(corr=-0.998). 미해결.",
              params={"pad_hours": "패드 누적 사용시간"}))


def run_pipeline(recipe, radius_m: np.ndarray, config: Optional[Dict[str, str]] = None):
    """설정된 슬롯 조합으로 파이프라인 실행. (mrr_m_s, notes, trace) 반환.

    recipe는 ResolvedRecipe(팩 해석 완료)여야 한다. Recipe를 넘기면 resolve()한다.
    슬롯 = 물리 모델 갈아끼우기, 팩 = 물성 갈아끼우기. 두 축은 직교한다.
    """
    if hasattr(recipe, "resolve"):
        recipe = recipe.resolve()
    cfg = {**default_config(), **(config or {})}
    notes: List[str] = []
    trace: List[Dict] = []

    def pick(slot):
        iid = cfg.get(slot)
        if iid not in _REG[slot]:
            raise KeyError(f"슬롯 {slot}에 '{iid}' 없음. 가능: {list(_REG[slot])}")
        im = _REG[slot][iid]
        trace.append({"slot": slot, "impl": im.id, "label": im.label,
                      "status": im.status, "note": im.note, "agent": im.agent})
        if im.warning:
            notes.append(f"[{SLOT_LABEL[slot]}: {im.label}] {im.warning}")
        return im

    P = pick("pressure").fn(recipe, radius_m, cfg)
    V = pick("velocity").fn(recipe, radius_m, cfg)
    Kp = pick("kp").fn(recipe, radius_m, P, V, cfg)
    mrr = pick("removal").fn(recipe, radius_m, P, V, Kp, cfg)
    mrr, n1 = pick("pattern").fn(recipe, radius_m, mrr, cfg)
    mrr, n2 = pick("wear").fn(recipe, radius_m, mrr, cfg)
    notes.extend(n1 + n2)
    return mrr, notes, trace
