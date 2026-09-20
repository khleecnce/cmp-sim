"""엔진 등록 모델 — 물리 모듈을 engine.Model 계약으로 감싼다.

왜 이 파일이 있나 (2026-09-05 사용자: "시뮬레이션 툴 제작은 언제 착수하냐고"):
  tier1/tier2 모듈 24개가 각자 다른 시그니처로 따로 놀았다. 엔진에 등록된 건 1개뿐.
  이 파일이 "물리 모듈 라이브러리"를 "제품"으로 바꾸는 접합부다.

각 모델의 규약:
  - Recipe(입력) → radius별 MRR [m/s] 반환. 그 외 부수효과 금지.
  - 자기가 못 하는 것은 notes에 적는다. 지어내지 않는다.
  - 근거 노트 경로를 docstring에 남긴다 (verify_claims.py --trace 대상).
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import List, Optional

import numpy as np

_ROOT = Path(__file__).resolve().parent
for _p in ("tier1_empirical", "tier2_physics", "integration"):
    _d = str(_ROOT / _p)
    if _d not in sys.path:
        sys.path.insert(0, _d)

from sim.engine import Recipe, ResolvedRecipe, register, PSI_TO_PA  # noqa: E402
from sim.tier1_empirical import kinematics as kin  # noqa: E402
from sim.tier1_empirical import wiwnu  # noqa: E402


def _velocity_profile(recipe: ResolvedRecipe, radius_m: np.ndarray) -> np.ndarray:
    """반경별 상대속도 [m/s] — 자전 평균. 근거: knowledge/physics/cmp-kinematics-rotary"""
    w_w = kin.rpm_to_rads(recipe.rpm_wafer)
    w_p = kin.rpm_to_rads(recipe.rpm_platen)
    # 회전대칭 자전 평균: |v|의 방위각 평균을 반경별로
    th = np.linspace(0, 2 * np.pi, 181)
    out = np.empty_like(radius_m)
    for i, r in enumerate(radius_m):
        v = kin.relative_speed_polar(np.full_like(th, r / max(recipe.wafer_radius_m, 1e-9)),
                                     th, w_w, w_p, recipe.center_offset_m,
                                     recipe.wafer_radius_m)
        out[i] = float(np.mean(v))
    return out


def _pressure_profile(recipe: ResolvedRecipe, radius_m: np.ndarray) -> np.ndarray:
    """반경별 압력 [Pa]. 존압력 지정 시 그것을, 아니면 균일+엣지집중."""
    P0 = recipe.pressure_psi * PSI_TO_PA
    rn = radius_m / max(recipe.wafer_radius_m, 1e-9)
    if recipe.zone_pressures_psi:
        edges = recipe.zone_edges_norm or list(
            np.linspace(0, 1, len(recipe.zone_pressures_psi) + 1))[1:]
        P = np.full_like(radius_m, recipe.zone_pressures_psi[-1] * PSI_TO_PA)
        lo = 0.0
        for pz, hi in zip(recipe.zone_pressures_psi, edges):
            P[(rn >= lo) & (rn < hi)] = pz * PSI_TO_PA
            lo = hi
        return P
    return P0 * (1.0 + recipe.edge_pressure_amp * rn ** 4)


# ────────────────────────────────────────────── Tier2: GW 접촉 → 물리적 Kp
class GWPhysicalKpModel:
    """Kp를 상수가 아니라 GW 접촉역학에서 유도한다.

    근거 노트: knowledge/materials/hertz-gw-contact-mechanics,
              knowledge/materials/gw-nominal-vs-local-pressure
    구현 출처: sim/tier2_physics/gw_preston_link.py (pad-mechanic Lv3-2)

    핵심: MRR ∝ n_contacts(P)·V. GW에서 n_contacts는 P에 거의 선형이므로
    Preston(MRR ∝ P·V)이 왜 성립하는지가 설명된다 — Kp가 패드 표면 통계
    (밀도 η, 곡률반경 R, 조도 σ)에서 나온다.

    ⚠ 미검증: alpha_removal은 문헌 Kp에서 역산한 값이다(1점 캘리브레이션).
    독립적인 문헌값이 없어 절대값은 Preston과 같고, 의미는 P 의존성의 물리적 근거다.
    """
    name = "tier2.gw_physical_kp"

    def __init__(self, kp_ref: Optional[float] = None):
        self.kp_ref = kp_ref

    @staticmethod
    def _pad_params(recipe: ResolvedRecipe) -> dict:
        """패드 물성을 팩에서 읽어 물리 모듈 인자로 넘긴다.

        이게 "팩을 바꾸면 다른 시뮬레이션"의 실제 배선이다. 팩에 pad_*가 없으면
        ParamMissing으로 죽는다 — 조용히 IC1000 기본값을 쓰면 결과가 거짓말이 된다.
        """
        return {
            "E_star": recipe.p("pad_E_star_pa"),
            "R": recipe.p("pad_asperity_radius_m"),
            "beta": 1.0 / recipe.p("pad_height_beta_inv_m"),
            "eta": recipe.p("pad_asperity_density_m2"),
            "A_n": recipe.p("pad_nominal_area_m2"),
        }

    def mrr_radial(self, recipe: ResolvedRecipe, radius_m: np.ndarray) -> np.ndarray:
        import gw_preston_link as gpl
        P = _pressure_profile(recipe, radius_m)
        V = _velocity_profile(recipe, radius_m)
        kp = self.kp_ref if self.kp_ref is not None else recipe.kp_m_per_pa
        pad = self._pad_params(recipe)
        # 기준점(면적평균)에서 alpha 역산 → 반경별 n_contacts로 MRR 분포
        P_ref = float(np.mean(P))
        V_ref = float(np.mean(V))
        alpha = gpl.calibrate_alpha_removal(P_ref, V_ref, kp, **pad)
        return np.array([gpl.mrr_gw_link(p, v, alpha, **pad) for p, v in zip(P, V)])


# ────────────────────────────────────────────── Tier2: 패드 마모 시간 이력
class WearAwareModel:
    """패드 마모의 시간 이력. ⚠ **미해결 물리 모순을 안고 있다 — 덮지 않는다.**

    근거 노트: knowledge/materials/pad-wear-glazing-mrr-decay
    구현 출처: sim/tier2_physics/wear_aware_kp_physical.py (pad-mechanic Lv3-1)

    모순 (2026-09-05 엔진 통합 중 재확인, corr = -0.998):
      - ad-hoc 모델: 마모 → 접촉압 p_r 감소 → MRR **감소** (glazing 관찰과 일치)
      - GW 물리 모델: 마모 → asperity 평탄화 → n_contacts **증가**(3033→3564)
        → MRR ∝ n·V 이면 MRR **증가**
      두 곡선의 상관계수가 -0.998, 즉 정반대다. 어느 쪽이 옳은지 아직 모른다.

    가설: 마모는 접촉점 수를 늘리지만 점당 하중을 낮춘다. MRR ∝ n·V는 점당
    제거효율이 일정하다고 가정하는데, 실제로는 국소압이 임계치 아래로 내려가면
    제거가 급감할 수 있다(Preston의 압력 하한). 이걸 확인하려면 pad-lifecycle
    에이전트의 학습(G3)과 실데이터가 필요하다.

    **따라서 이 모델은 시간 보정을 적용하지 않고, 모순을 notes로 보고한다.**
    추측으로 한쪽을 고르면 그게 곧 할루시네이션이다.
    """
    name = "tier2.wear_aware"

    def mrr_radial(self, recipe: ResolvedRecipe, radius_m: np.ndarray) -> np.ndarray:
        return GWPhysicalKpModel().mrr_radial(recipe, radius_m)

    def notes(self, recipe: ResolvedRecipe) -> List[str]:
        hours = float(recipe.meta.get("pad_hours", 0) or 0)
        if hours <= 0:
            return []
        return [
            f"패드 사용 {hours:g}h 입력됨 — 그러나 시간 보정을 적용하지 않았다. "
            "ad-hoc 모델(MRR 감소)과 GW 물리 모델(MRR 증가)이 정반대다(corr=-0.998, "
            "knowledge/materials/pad-wear-glazing-mrr-decay). 어느 쪽이 옳은지 "
            "미해결이므로 새 패드 기준값을 반환한다. 해결: pad-lifecycle 에이전트(G3) "
            "+ 실데이터 캘리브레이션(M3)."
        ]


# ────────────────────────────────────────────── Tier1: PTW 패턴 밀도
class PatternDensityModel:
    """PTW: 패턴 밀도가 국소 압력을 올려 제거를 가속한다 (up-area 우선 연마).

    근거 노트: knowledge/cmp/pattern-dependent-dishing-erosion
    구현 출처: sim/tier1_empirical/pattern_density.py (process-integrator Lv3-1)

    Recipe.meta['pattern_density'] (0~1, 기본 0.5)로 평균 패턴 밀도를 받는다.
    MRR_up = MRR_blanket / rho_eff  (비압축 패드 극한, Stine 1997)

    ⚠ NPW에서는 사용하지 않는다(패턴이 없으므로).
    ⚠ 미검증: 평활 길이 PL은 문헌 대표값. 실제 값은 툴·패드마다 다르다.

    ⚠⚠ 판정#65(EVIDENCE-RULES, 2026-09-19) — **근거 등급이 낮은 쪽이다.**
    1/ρ는 "하중이 융기 면적에만 분산된다"는 기하 가정에서 나온 폐형식(E4)이고,
    Sorooshian(2005) §3.3은 같은 양(P_eff/P_applied)을 밀도·압력·온도별로 직접
    실측했다(E3, 대상계 실측). 실측 대비 이 모델은 ρ=0.10에서 2.50배,
    ρ=0.50에서 1.29배 과대예측한다(ρ=0.90에서만 0.95배로 근접).
    → 밀도 0.10/0.50/0.90 · 3 또는 7 psi 조건이면
      `tier1.pattern_density_effective_pressure`를 쓰라. 이 모델은 그 격자 밖
      밀도(연속값)를 다뤄야 할 때의 폴백으로만 남긴다.
    """
    name = "tier1.pattern_density"
    RHO_MIN = 0.15   # 이 아래는 1/rho 발산 — 비압축 극한이 깨진다

    def mrr_radial(self, recipe: ResolvedRecipe, radius_m: np.ndarray) -> np.ndarray:
        base = GWPhysicalKpModel().mrr_radial(recipe, radius_m)
        if recipe.wafer != "PTW":
            return base
        rho = float(recipe.meta.get("pattern_density", 0.5) or 0.5)
        rho = min(max(rho, self.RHO_MIN), 1.0)
        return base / rho

    def notes(self, recipe: ResolvedRecipe) -> List[str]:
        if recipe.wafer != "PTW":
            return ["NPW: 패턴 효과 없음 — 블랭킷 등가로 계산"]
        rho = float(recipe.meta.get("pattern_density", 0.5) or 0.5)
        out = [
            f"PTW up-area MRR = 블랭킷/ρ_eff (ρ={rho:g}, 비압축 패드 극한, Stine 1997). "
            "장시간 후 step height가 사라지면 이 식은 성립하지 않는다 — 초기 단계에만 유효.",
            "⚠ 판정#65: 1/ρ는 기하 가정 폐형식(E4)이며 Sorooshian(2005) §3.3 실측표 대비 "
            "ρ=0.10에서 2.50배·ρ=0.50에서 1.29배 과대예측한다. 밀도가 0.10/0.50/0.90이고 "
            "3 또는 7 psi면 tier1.pattern_density_effective_pressure(E3 실측)를 쓰라."
        ]
        if rho < self.RHO_MIN:
            out.append(f"⚠ ρ={rho:g} < {self.RHO_MIN} — 1/ρ가 발산해 비현실적이다. "
                       f"ρ={self.RHO_MIN}로 클램프했다. 저밀도 영역은 압축성 패드 모델이 필요하다"
                       "(pattern_density.step_height_compressible, 미연결).")
        out.append("dishing/erosion 미산출 — steady_state_dishing()이 금속/산화막 MRR 비를 "
                   "요구하는데 막질별 Kp가 아직 없다(film-cu·film-w 대기).")
        return out


def register_all() -> List[str]:
    """엔진에 전부 등록. import 시 자동 호출된다."""
    for m in (GWPhysicalKpModel(), WearAwareModel(), PatternDensityModel()):
        register(m)
    from sim.engine import available_models
    return available_models()


register_all()
