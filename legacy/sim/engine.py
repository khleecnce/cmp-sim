"""
FabSim 통합 엔진 — 입력(Recipe) → 시뮬레이션 → 출력(WaferResult) 단일 API.

왜 이 파일이 있나 (2026-09-05 사용자 지시 "시뮬레이션 툴은 언제 착수?" → 지금):
  tier1/tier2 모듈은 각자 인자 시그니처가 달라 따로 논다. 새 물리가 어디에 붙는지 기준이 없다.
  이 파일이 그 기준이다. 물리 모듈은 1바이트도 고치지 않고 여기서 조립만 한다.

원칙
  1. Recipe(입력)와 WaferResult(출력)는 dataclass — 스키마가 코드다. 필드 추가 = 스키마 변경 = 커밋 로그에 남는다.
  2. 출력 지표는 sim/metrics/uniformity.py(wafer-metrology 소유)가 계산한다. 엔진은 두께 필드만 만든다.
  3. 물리 모듈은 `Model` 프로토콜로 등록한다. 지금은 Preston 반경 모델 하나. tier2/캘리브레이션은 같은 자리에 끼운다.
  4. 없는 것은 None. 지어내지 않는다 (roughness·contamination은 담당 에이전트 활성 전까지 None).

사용
  >>> from sim.engine import Recipe, simulate
  >>> r = Recipe(wafer="NPW", film="oxide", pressure_psi=3.0, rpm_wafer=60, rpm_platen=55, time_s=60)
  >>> res = simulate(r)
  >>> res.metrics.ttv_nm, res.metrics.radial_range_pct, res.metrics.cv_pct
"""
from __future__ import annotations

import math
import re
import sys
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Callable, Dict, List, Literal, Optional, Protocol

import numpy as np

# 물리 모듈은 스크립트 직접 실행을 전제로 bare import를 쓴다 (tests/conftest.py와 동일 처리)
_ROOT = Path(__file__).resolve().parent
for _p in ("tier1_empirical", "tier2_physics", "integration"):
    _d = str(_ROOT / _p)
    if _d not in sys.path:
        sys.path.insert(0, _d)
if str(_ROOT.parent) not in sys.path:
    sys.path.insert(0, str(_ROOT.parent))

from sim.metrics.uniformity import compute_metrics, UniformityMetrics  # noqa: E402
from sim.params import ParamPack, load_pack, available_packs  # noqa: E402
from sim.chemistry import chemistry_factor, ChemistryEffect  # noqa: E402,F401
from sim.factors import compute_factors, mrr_multiplier, coverage, Factor  # noqa: E402
from sim.equipment_outputs import compute_outputs, Output  # noqa: E402

PSI_TO_PA = 6894.757


# ───────────────────────────────────────────────────────────── 입력 스키마
@dataclass
class Recipe:
    """한 번의 CMP 런을 정의하는 모든 입력. 각 필드의 소유 에이전트를 주석으로 남긴다.

    ⚠ 물리 상수는 여기가 아니라 **파라미터 팩**(knowledge/params/*.yaml)이 소유한다.
      Recipe는 "이번 런에 사람이 정하는 것"(압력·rpm·시간)만 담는다.
      기본값 None인 필드는 팩에서 채워진다 — from_pack()이 그 일을 한다.
      이렇게 나눠야 "팩만 바꿔서 Cu를 돌린다"가 성립한다.
    """
    # 어떤 물성 묶음으로 돌릴 것인가 — 이 한 줄이 시뮬레이션의 정체성이다
    pack: str = "oxide_silica"
    # wafer-type / film-*
    wafer: Literal["NPW", "PTW"] = "NPW"
    film: Optional[str] = None              # None이면 팩의 film
    wafer_radius_m: Optional[float] = None
    # tool-platen-head
    pressure_psi: Optional[float] = None
    rpm_wafer: Optional[float] = None
    rpm_platen: Optional[float] = None
    center_offset_m: Optional[float] = None     # r_cc: 웨이퍼 중심–플래튼 중심 거리
    zone_pressures_psi: Optional[List[float]] = None   # 멀티존 헤드. None=균일
    zone_edges_norm: Optional[List[float]] = None      # 존 경계 (0~1, 정규화 반경)
    edge_pressure_amp: float = 0.0          # 엣지 압력 집중 진폭 (0=없음)
    time_s: float = 60.0
    # slurry-* / pad-* / disk-* — 팩이 소유. None이면 팩값
    kp_m_per_pa: Optional[float] = None
    # wafer-metrology — 측정 체계
    n_points: Optional[int] = None
    edge_exclusion_m: Optional[float] = None
    # 초기 두께 (잔막 계산용). None이면 제거량만 보고
    initial_thickness_nm: Optional[float] = None
    # 자유 확장 (캘리브레이션 태그, 로트 ID 등)
    meta: Dict[str, str] = field(default_factory=dict)
    # 팩 값을 이번 런에만 덮어쓴다 — 민감도 스캔·DOE의 통로.
    # 팩 파일을 고치지 않고 "이 값만 5% 올리면?"을 물을 수 있어야 한다.
    pack_overrides: Dict[str, float] = field(default_factory=dict)

    # 팩에서 채워야 하는 필드 → 팩의 키 이름
    _FROM_PACK = {
        "film": "film", "wafer_radius_m": "wafer_radius_m",
        "pressure_psi": "pressure_psi", "rpm_wafer": "rpm_wafer",
        "rpm_platen": "rpm_platen", "center_offset_m": "center_offset_m",
        "kp_m_per_pa": "kp_m_per_pa", "n_points": "n_points",
        "edge_exclusion_m": "edge_exclusion_m",
    }

    def resolve(self) -> "ResolvedRecipe":
        """팩을 읽어 빈 필드를 채운다. 없는 값은 KeyError로 즉시 실패한다.

        조용한 기본값을 쓰지 않는 게 핵심이다 — Cu 팩을 돌렸는데 산화막 Kp가
        말없이 쓰이면 결과 전체가 거짓말이 된다.
        """
        pk = load_pack(self.pack)
        if self.pack_overrides:
            # 이번 런에만 적용되는 덮어쓰기. 원본 팩은 건드리지 않는다(캐시 오염 방지).
            import copy as _copy
            from sim.params import Param
            pk = _copy.deepcopy(pk)
            for k, v in self.pack_overrides.items():
                if k in pk.params:
                    p = pk.params[k]
                    pk.params[k] = Param(key=k, value=v, unit=p.unit, source=p.source,
                                         confidence=p.confidence,
                                         note=(p.note + " [런 오버라이드]").strip())
                else:
                    pk.params[k] = Param(key=k, value=v, confidence="unverified",
                                         note="런 오버라이드 — 팩에 없던 값")
        vals = {}
        used: List[str] = []
        for attr, key in self._FROM_PACK.items():
            cur = getattr(self, attr)
            if cur is None:
                vals[attr] = pk.get(key)     # 없으면 ParamMissing
                used.append(key)
            else:
                vals[attr] = cur
        return ResolvedRecipe(base=self, pack=pk, used_keys=used, **vals)


@dataclass
class ResolvedRecipe:
    """팩으로 빈칸을 채운 뒤의 레시피 — 모델은 이것만 본다(전부 non-None)."""
    base: Recipe
    pack: ParamPack
    used_keys: List[str]
    film: str
    wafer_radius_m: float
    pressure_psi: float
    rpm_wafer: float
    rpm_platen: float
    center_offset_m: float
    kp_m_per_pa: float
    n_points: int
    edge_exclusion_m: float

    # 팩에 없는(사람이 정하는) 필드는 원본에서 그대로 위임
    @property
    def wafer(self) -> str: return self.base.wafer
    @property
    def time_s(self) -> float: return self.base.time_s
    @property
    def zone_pressures_psi(self): return self.base.zone_pressures_psi
    @property
    def zone_edges_norm(self): return self.base.zone_edges_norm
    @property
    def edge_pressure_amp(self) -> float: return self.base.edge_pressure_amp
    @property
    def initial_thickness_nm(self): return self.base.initial_thickness_nm
    @property
    def meta(self) -> Dict[str, str]: return self.base.meta

    def p(self, key: str):
        """팩 값 직접 조회 — 모델이 추가 물성을 필요로 할 때."""
        v = self.pack.get(key)
        if key not in self.used_keys:
            self.used_keys.append(key)
        return v


# ───────────────────────────────────────────────────────────── 출력 스키마
@dataclass
class WaferResult:
    recipe: Recipe
    radius_m: np.ndarray                 # 반경 격자
    mrr_nm_per_min: np.ndarray           # 반경별 제거율
    removed_nm: np.ndarray               # 반경별 제거량 (time_s 후)
    remaining_nm: Optional[np.ndarray]   # 잔막 (initial_thickness 있을 때)
    metrics: UniformityMetrics           # WIWNU·TTV·radial TTV·CV 등 — wafer-metrology 정의
    # 담당 에이전트 활성 전까지 None — 지어내지 않는다
    roughness_ra_nm: Optional[float] = None        # wafer-metrology Lv2-1
    dishing_nm: Optional[float] = None             # PTW만. pattern_density 연결 시
    erosion_nm: Optional[float] = None
    metal_contamination: Optional[Dict[str, float]] = None   # surface-contamination
    defect_density: Optional[float] = None         # defect-scientist
    # 윤활 레짐 진단 — MRR과 무관한 순수 진단. tribologist Lv2 (cmp-lubrication-regimes.md)
    lubrication_regime: Optional[str] = None       # "boundary"/"mixed"/"hydrodynamic"
    cmp_sommerfeld_number: Optional[float] = None
    cof_stribeck_estimate: Optional[float] = None
    # 슬러리 필름두께 스케일 진단 — MRR과 무관. Thakurta(2001) Eq.19 z0
    # (cmp-slurry-flow-lubrication-film-thickness.md). z0는 h_min의 스케일이지 정확한 값이 아니다.
    film_z0_scale_um: Optional[float] = None
    film_lubrication_note: Optional[str] = None
    # PTW 유효압력/인가압력 비 진단 — MRR과 무관. Sorooshian(2005) §3.3 실측표 조회.
    ptw_effective_pressure_ratio: Optional[float] = None
    ptw_effective_pressure_note: Optional[str] = None
    # Cu 오버폴리시 dishing/erosion 닫힌 시간해 — MRR과 무관한 별도 계산 경로(Tugbawa 2002).
    # dishing_nm/erosion_nm(위, 아직 어떤 모델도 채운 적 없음)과 이름을 분리해 충돌을 피한다.
    # cu_h2o2_bta 팩 + PTW + meta에 패턴 레이아웃(선폭/스페이스/밀도)·r_cu/r_ox 실측이
    # 전부 있을 때만 채워진다 — 하나라도 없으면 조용히 None.
    cu_dishing_tugbawa_nm: Optional[float] = None
    cu_erosion_tugbawa_nm: Optional[float] = None
    cu_dishing_tugbawa_note: Optional[str] = None
    # DLVO 콜로이드 응집 위험 정성 진단 — MRR과 무관. IEP 거리 기반(정량 zeta 없음).
    # slurry_ph·abrasive_iep_ph가 팩에 둘 다 있을 때만 채워진다 — 하나라도 없으면 조용히 None.
    colloid_distance_from_iep_ph: Optional[float] = None
    colloid_stability_risk: Optional[str] = None       # "high"/"medium"/"low"
    colloid_stability_note: Optional[str] = None
    # GW 접촉역학 기반 Preston Kp 물리 분해 진단 — MRR과 무관. gw_preston_link.py
    # (self-test 4/4 PASS)의 n_contacts(P) 선형성·alpha_removal 역산을 이 레시피의
    # 실제 압력조건에 그대로 적용한다. pad_E_star_pa 등 GW 5개 패드 파라미터가
    # 팩에 없으면 조용히 None.
    gw_contact_linearity_max_dev: Optional[float] = None
    gw_kp_physical_to_lit_ratio: Optional[float] = None
    gw_contact_note: Optional[str] = None
    # Θ 정상상태 열저항 네트워크 진단 — MRR과 무관. White 2003 원문 에너지균형 이식
    # (frictional-heating-temperature-arrhenius-coupling.md §8). 공통 싱크 T₀ 대비 ΔT_ss[K]와
    # 슬러리/패드/공기 3분배. pad_thickness_m·pad_thermal_conductivity_w_mk 없으면 조용히 None.
    # ⚠ 절대온도가 아니다(싱크 온도 미지) — _f_theta()의 비율 압축을 대체하지 않는다.
    theta_steady_state_delta_T_k: Optional[float] = None
    theta_heat_partition: Optional[Dict[str, float]] = None   # {"slurry","pad","air"} 합=1
    theta_steady_state_note: Optional[str] = None
    # Cu-H2O Pourbaix E-무관(수직·pH축) 진단 — MRR과 무관. sim/tier2_physics/cu_pourbaix.py.
    # Recipe에 전극전위 필드가 없어 stable_phase()는 호출하지 않고, E와 무관한 수직선/삼중점
    # pH만 낸다. slurry_ph가 없거나 rr.film != "cu"이면 조용히 None.
    cu_pourbaix_vertical_ph: Optional[float] = None
    cu_pourbaix_triple_point_ph: Optional[float] = None
    cu_pourbaix_soluble_domain: Optional[bool] = None
    cu_pourbaix_note: Optional[str] = None
    # 패드 그루브 깊이 소진 EOL 진단 — MRR과 무관. sim/tier2_physics/pad_groove_eol.py.
    # 팩이 pad_cut_rate_um_per_h를 선언하지 않으면(현재 5팩 전부 미선언) 조용히 None —
    # 43.4(풀컨택트)/22.2(분할컨택트) μm/h 중 어느 쪽인지 하드코딩으로 고르지 않는다.
    pad_groove_cumulative_wear_um: Optional[float] = None
    pad_groove_eol_hours: Optional[float] = None
    pad_groove_exhausted: Optional[bool] = None
    pad_groove_note: Optional[str] = None
    # 갈바닉 부식 방향·Cu 수산화물 전이 pH 진단 — MRR과 무관. sim/tier2_physics/galvanic_hydroxide_ph.py.
    # 접촉 상대 금속 필드가 Recipe/팩에 없어(현재 5팩 전부 미선언) 갈바닉 필드는 항상 None이
    # 정상이다 — Co/Ru 등을 임의로 골라 넣지 않는다. 수산화물 전이 pH는 rr.film == "cu"이고
    # slurry_ph가 있을 때만 채워진다(log_a_cu 관례는 cu_pourbaix_note와 동일).
    galvanic_anode_metal: Optional[str] = None
    galvanic_delta_e0_v: Optional[float] = None
    hydroxide_transition_ph: Optional[float] = None
    hydroxide_precipitation_expected: Optional[bool] = None
    galvanic_hydroxide_note: Optional[str] = None
    # 컨디셔너 스윕 궤적 PCR(r) 상대 프로파일 요약 진단 — MRR과 무관. sim/tier2_physics/
    # conditioner_sweep_kinematics.py(Zheng, Zhao & Lu 2023, PMC10536193, Eq.1-9 재현).
    # 기구 고정 치수(R_p·R_a·disk_radius·n_d·beta_s·beta_max)를 어떤 팩도 선언하지 않아
    # (Zheng et al. Table 1은 RPM·하중·스윕범위(mm)만 보고) 현재 5팩 전부 미선언이라
    # 항상 None이 정상이다 — 하드코딩으로 채우지 않는다.
    conditioner_sweep_profile_uniformity: Optional[float] = None   # CV=sigma/mu, 낮을수록 균일
    conditioner_sweep_edge_center_ratio: Optional[float] = None    # 바깥링평균/안쪽링평균
    conditioner_sweep_note: Optional[str] = None
    # 패드 글레이징(컨디셔닝 없는 연마)에 의한 접촉점 감소·asperity 반경 증가 진단 —
    # MRR과 무관. Jeong et al. 2024 Table 1/Eq.4. 적용범위가 좁다: Table 1에 있는
    # 압력(2/3/4/5 psi) + 컨디셔닝 없음(cond_duty_pct==0) + t<=측정상한일 때만 채워진다.
    pad_glazing_contact_ratio: Optional[float] = None       # N(t)/N0
    pad_glazing_radius_growth_ratio: Optional[float] = None  # μR(t)/μR(0)
    pad_glazing_relative_mrr_proxy: Optional[float] = None   # 거친 근사, 방향성만
    pad_glazing_note: Optional[str] = None
    # 금속막 표면 산화막 반응의 Pourbaix 경계선 Nernst pH 기울기 진단 — MRR과 무관.
    # 금속막(cu/w)일 때만 채워진다. 산화막·SiC 팩은 대응 반응식이 없어 None.
    pourbaix_nernst_slope_mv_per_ph: Optional[float] = None
    pourbaix_self_limiting_reactions: Optional[int] = None
    pourbaix_nernst_note: Optional[str] = None
    model: str = ""
    notes: List[str] = field(default_factory=list)
    # 병합 파라미터 (ARCHITECTURE-V2 §2) — 이 런에서 각 축이 얼마였나.
    # UI가 "무엇을 만지면 무엇이 바뀌나"를 그리는 근거이자, 미모델링 축을 드러내는 통로.
    factors: Dict[str, "Factor"] = field(default_factory=dict)
    # 장비 출력값 (설정값이 아니라 저절로 도출되는 것) — ARCHITECTURE-V2 §1-①.
    # 패드 온도·모터 전류·마찰계수. 실제 툴에서 엔지니어가 읽는 진단 신호다.
    equipment_outputs: Dict[str, "Output"] = field(default_factory=dict)
    # 이 결과가 어떤 물성에서 나왔나 — 숫자의 출처 추적
    pack: str = ""
    film: str = ""
    provenance: Dict[str, Dict[str, str]] = field(default_factory=dict)

    def summary(self) -> Dict:
        m = self.metrics
        return {
            "model": self.model, "pack": self.pack,
            "wafer": self.recipe.wafer, "film": self.film,
            "mean_mrr_nm_min": float(np.mean(self.mrr_nm_per_min)),
            "ttv_nm": m.ttv_nm, "radial_range_pct": m.radial_range_pct,
            "radial_maxring_range_nm": m.radial_maxring_range_nm, "cv_pct": m.cv_pct,
            "wiwnu_halfrange_pct": m.wiwnu_halfrange_pct, "wiwnu_3sigma_pct": m.wiwnu_3sigma_pct,
            "roughness_ra_nm": self.roughness_ra_nm, "dishing_nm": self.dishing_nm,
            "metal_contamination": self.metal_contamination,
            "lubrication_regime": self.lubrication_regime,
            "cmp_sommerfeld_number": self.cmp_sommerfeld_number,
            "cof_stribeck_estimate": self.cof_stribeck_estimate,
            "film_z0_scale_um": self.film_z0_scale_um,
            "film_lubrication_note": self.film_lubrication_note,
            "ptw_effective_pressure_ratio": self.ptw_effective_pressure_ratio,
            "ptw_effective_pressure_note": self.ptw_effective_pressure_note,
            "cu_dishing_tugbawa_nm": self.cu_dishing_tugbawa_nm,
            "cu_erosion_tugbawa_nm": self.cu_erosion_tugbawa_nm,
            "cu_dishing_tugbawa_note": self.cu_dishing_tugbawa_note,
            "colloid_distance_from_iep_ph": self.colloid_distance_from_iep_ph,
            "colloid_stability_risk": self.colloid_stability_risk,
            "colloid_stability_note": self.colloid_stability_note,
            "gw_contact_linearity_max_dev": self.gw_contact_linearity_max_dev,
            "gw_kp_physical_to_lit_ratio": self.gw_kp_physical_to_lit_ratio,
            "gw_contact_note": self.gw_contact_note,
            "theta_steady_state_delta_T_k": self.theta_steady_state_delta_T_k,
            "theta_heat_partition": self.theta_heat_partition,
            "theta_steady_state_note": self.theta_steady_state_note,
            "factors": {k: f.to_dict() for k, f in self.factors.items()},
            "factor_coverage": coverage(self.factors) if self.factors else None,
            "equipment_outputs": {k: o.to_dict()
                                  for k, o in self.equipment_outputs.items()},
            "notes": self.notes,
        }


# ───────────────────────────────────────────────────────────── 모델 등록
class Model(Protocol):
    name: str
    def mrr_radial(self, recipe: "ResolvedRecipe", radius_m: np.ndarray) -> np.ndarray: ...
    # 선택: 모델이 자기 한계를 스스로 보고한다(미해결 물리·미검증 가정).
    # 구현하지 않아도 되지만, 아는 한계를 숨기면 그게 할루시네이션이다.
    def notes(self, recipe: "ResolvedRecipe") -> List[str]: ...


class PrestonRadialModel:
    """Tier1: Preston MRR = Kp·P·V, V는 kinematics.py 상대속도장의 자전 평균. 압력은 wiwnu.py 프로파일."""
    name = "tier1.preston_radial"

    def mrr_radial(self, recipe: "ResolvedRecipe", radius_m: np.ndarray) -> np.ndarray:
        import wiwnu as W            # sim/tier1_empirical/wiwnu.py (1바이트도 수정 안 함)
        p0 = recipe.pressure_psi * PSI_TO_PA
        if recipe.zone_pressures_psi:
            # wiwnu.p_zoned는 경계가 [0, ..., 1] (len=N+1)이어야 한다.
            # Recipe.zone_edges_norm은 끝점만 준다(len=N) → 0을 앞에 붙인다.
            # 이걸 안 하면 searchsorted가 전부 같은 존으로 보내 존압력이 무시된다
            # (2026-09-05 test_zone_pressure_applied가 잡은 실제 버그).
            edges = list(recipe.zone_edges_norm or
                         np.linspace(0, 1, len(recipe.zone_pressures_psi) + 1)[1:])
            if edges[0] != 0.0:
                edges = [0.0] + edges
            pfn = W.p_zoned(np.asarray(edges),
                            np.asarray(recipe.zone_pressures_psi) * PSI_TO_PA)
        elif recipe.edge_pressure_amp > 0:
            pfn = W.p_edge_concentration(p0, amp=recipe.edge_pressure_amp)
        else:
            pfn = W.p_uniform(p0)
        rs, mrr = W.mrr_radial(recipe.wafer_radius_m, recipe.center_offset_m,
                               recipe.rpm_wafer, recipe.rpm_platen, recipe.kp_m_per_pa,
                               pfn, n_r=len(radius_m))
        # wiwnu.mrr_radial은 자기 격자를 쓴다 → 요청 격자로 보간
        return np.interp(radius_m, rs, mrr)


_MODELS: Dict[str, Model] = {}


def register(model: Model) -> None:
    _MODELS[model.name] = model


register(PrestonRadialModel())


def _lubrication_diagnostics(rr: "ResolvedRecipe") -> Dict[str, object]:
    """윤활 레짐 진단(So·λ·COF) — MRR 경로와 완전히 독립적인 진단 계산.

    근거: knowledge/physics/cmp-lubrication-regimes.md §2,§5 (self-test 11/11 PASS).
    slurry_viscosity_pa_s·pad_ra_m이 팩에 없으면(tribologist 미적용 팩) roughness_ra_nm과
    같은 지위로 조용히 None — 지어내지 않는다.
    """
    out: Dict[str, object] = {"lubrication_regime": None, "cmp_sommerfeld_number": None,
                              "cof_stribeck_estimate": None}
    if not (rr.pack.has("slurry_viscosity_pa_s") and rr.pack.has("pad_ra_m")):
        return out
    try:
        import cmp_lubrication_regime as CLR   # sim/tier2_physics (1바이트도 수정 안 함)
        from sim.tier1_empirical import kinematics as kin
        mu = rr.p("slurry_viscosity_pa_s")
        Ra = rr.p("pad_ra_m")
        p_mean = rr.pressure_psi * PSI_TO_PA
        U_mean = kin.speed_stats(rr.wafer_radius_m, rr.center_offset_m,
                                 rr.rpm_wafer, rr.rpm_platen)["mean"]
        # groove 가중항은 미검증(노트 §2) → δeff≈Ra 근사만 쓴다
        d_eff = CLR.delta_eff(Ra, 0.0, 1.0)
        so = CLR.cmp_sommerfeld(mu, U_mean, p_mean, d_eff)
        lam = so   # λ≈So 근사(δeff≈σ 가정, 노트 §5) — 정량 항등식 아님
        out["lubrication_regime"] = CLR.regime_from_lambda(lam)
        out["cmp_sommerfeld_number"] = so
        out["cof_stribeck_estimate"] = CLR.cof_stribeck(so)
    except Exception as e:
        out["_note"] = f"윤활 레짐 진단 실패({e}) — lubrication_regime 등 None으로 둠"
    return out


def _film_thickness_diagnostic(rr: "ResolvedRecipe") -> Dict[str, object]:
    """슬러리 필름두께 길이 스케일 z0 진단 — MRR 경로와 완전히 독립적인 진단 계산.

    근거: sim/tier2_physics/slurry_film_lubrication.py (Thakurta et al. 2001 Eq.19,
    knowledge/physics/cmp-slurry-flow-lubrication-film-thickness.md §4).
    z0 = sqrt(2·μ·ω2·R1·R2 / P_app). 모듈 docstring이 명시하듯 z0는 무차원화 기준
    길이 스케일이며 정확한 최소필름두께 h_min이 아니다(전체 2-D Reynolds PDE 수치해 미이식).
    slurry_viscosity_pa_s가 팩에 없으면 roughness_ra_nm과 같은 지위로 조용히 None.
    """
    out: Dict[str, object] = {"film_z0_scale_um": None, "film_lubrication_note": None}
    if not rr.pack.has("slurry_viscosity_pa_s"):
        return out
    try:
        import slurry_film_lubrication as SFL   # sim/tier2_physics (1바이트도 수정 안 함)
        from sim.tier1_empirical import kinematics as kin
        mu = rr.p("slurry_viscosity_pa_s")
        omega2 = kin.rpm_to_rads(rr.rpm_platen)
        R1 = rr.wafer_radius_m
        R2 = rr.center_offset_m
        P_app = rr.pressure_psi * PSI_TO_PA
        z0_m = SFL.z0_length_scale(mu, omega2, R1, R2, P_app)
        out["film_z0_scale_um"] = float(z0_m) * 1e6
        out["film_lubrication_note"] = (
            "film_z0_scale_um은 Thakurta(2001) Eq.19의 길이 스케일 z0이며 정확한 최소필름두께 "
            "h_min이 아니다 — h_min/z0는 d0/z0 등 무차원군의 함수이고 전체 2-D Reynolds PDE "
            "수치해는 미이식 (knowledge/physics/cmp-slurry-flow-lubrication-film-thickness.md §4,§7)")
    except Exception as e:
        out["_note"] = f"필름두께 스케일 진단 실패({e}) — film_z0_scale_um None으로 둠"
    return out


def _effective_pressure_diagnostic(rr: "ResolvedRecipe") -> Dict[str, object]:
    """PTW 유효압력/인가압력 비 진단 — MRR 경로와 완전히 독립적인 진단 계산.

    근거: sim/tier2_physics/npw_ptw_effective_pressure.py (Sorooshian(2005) §3.3 실측표).
    PTW이고 rr.meta에 pattern_density가 있을 때만 계산한다. 표에 정확히 없는 density면
    (지원: 0.10/0.50/0.90) 조용한 보간·외삽 없이 None + 스킵 사유를 note로 남긴다
    — 이 모듈이 스스로 ValueError를 내는 설계이므로 그걸 그대로 정직하게 옮긴다.
    """
    out: Dict[str, object] = {"ptw_effective_pressure_ratio": None,
                              "ptw_effective_pressure_note": None}
    if rr.wafer != "PTW":
        return out
    density = rr.meta.get("pattern_density")
    if density is None:
        return out
    try:
        import npw_ptw_effective_pressure as EPR   # sim/tier2_physics (1바이트도 수정 안 함)
        ratio = EPR.effective_pressure_ratio(density)
    except ValueError as e:
        out["_note"] = (f"pattern_density={density}는 표에 없는 값(지원: 0.10/0.50/0.90) — "
                        f"유효압력 진단 스킵 ({e})")
        return out
    out["ptw_effective_pressure_ratio"] = ratio
    out["ptw_effective_pressure_note"] = (
        "Sorooshian(2005) §3.3 실측표 조회값. 1/density 모델(Boning) 대비 훨씬 작음 — "
        "1/ρ 모델은 저밀도에서 실측을 과대예측(§4)")
    return out


def _theta_steady_state_diagnostic(rr: "ResolvedRecipe") -> Dict[str, object]:
    """Θ 정상상태 열저항 네트워크 진단 — MRR 경로와 완전히 독립적인 진단 계산.

    근거: sim/tier2_physics/cmp_theta_steady_state_heat_balance.py (White 2003 Eq.4-10 원문,
    Harmand 2013 회전원판 층류 h, knowledge/physics/frictional-heating-temperature-arrhenius-
    coupling.md §8). Q_f = μ·P·A·V (μ=cof_boundary: CMP는 boundary~mixed 레짐), V = ω_p·r_cc
    (근사 매칭 회전, 노트 §8.2). 슬러리는 물 근사(ρ=1000, c_p=4180 — 모듈 상수).
    pad_thickness_m·pad_thermal_conductivity_w_mk·cof_boundary·sfr_ml_min 중 하나라도 팩에
    없으면 조용히 None — 지어내지 않는다. 결과는 공통 싱크 대비 ΔT_ss[K]이지 절대온도가 아니다.
    """
    out: Dict[str, object] = {"theta_steady_state_delta_T_k": None,
                              "theta_heat_partition": None,
                              "theta_steady_state_note": None}
    need = ("pad_thickness_m", "pad_thermal_conductivity_w_mk", "cof_boundary", "sfr_ml_min")
    if not all(rr.pack.has(k) for k in need):
        return out
    try:
        import cmp_theta_steady_state_heat_balance as HB   # sim/tier2_physics (1바이트도 수정 안 함)
        from sim.tier1_empirical import kinematics as kin
        mu = float(rr.p("cof_boundary"))
        L_pad = float(rr.p("pad_thickness_m"))
        k_pad = float(rr.p("pad_thermal_conductivity_w_mk"))
        flow = float(rr.p("sfr_ml_min")) * 1e-6 / 60.0
        if flow <= 0 or L_pad <= 0 or rr.rpm_platen <= 0:
            return out
        P = rr.pressure_psi * PSI_TO_PA
        A_w = math.pi * rr.wafer_radius_m ** 2
        omega = kin.rpm_to_rads(rr.rpm_platen)
        V = omega * rr.center_offset_m
        Qf = HB.friction_power_w(mu, P, A_w, V)
        A_ring = HB.heated_annulus_area_m2(rr.center_offset_m, rr.wafer_radius_m)
        pad_r = rr.center_offset_m + rr.wafer_radius_m     # 가열 고리 최외곽 = 층류 판정 반경
        res = HB.steady_state_heat_balance(Qf, flow, A_ring, L_pad, omega,
                                           max(A_ring - A_w, 0.0), pad_r, k_pad_w_mk=k_pad)
        out["theta_steady_state_delta_T_k"] = float(res.delta_T_ss_k)
        out["theta_heat_partition"] = {k: float(v) for k, v in res.partition().items()}
        out["theta_steady_state_note"] = (
            f"Θ 정상상태 열수지(White 2003 원문 이식): {res.describe()}"
            f"{'' if res.laminar else ' ⚠ Re_r>1.8e5 — 층류 h 상관식 범위 밖'}. "
            "공통 싱크 대비 ΔT이며 절대온도 아님. 웨이퍼/헤드 경로·L_pad 유효길이·슬러리 완전열교환은 "
            "미검증(노트 §8.5) — Θ confidence는 estimated 유지")
    except Exception as e:
        out["theta_steady_state_note"] = f"Θ 정상상태 열수지 진단 실패({e}) — None으로 둠"
    return out


def _cu_dishing_erosion_tugbawa_diagnostic(rr: "ResolvedRecipe") -> Dict[str, object]:
    """Cu 오버폴리시 dishing/erosion 닫힌 시간해 진단 — MRR 경로와 완전히 독립.

    근거: sim/tier2_physics/cu_dishing_erosion_tugbawa.py (Tugbawa 2002 eq 3.37-3.42, 3.46, 3.49).
    cu_h2o2_bta 팩 + PTW + meta에 pattern_density·linewidth_um·space_um(패턴 레이아웃)이 전부
    있어야 d_max·Φ_cu를 계산할 수 있다. r_cu_angstrom_s·r_ox_angstrom_s(블랭킷 유효 제거율)는
    레시피 kp_m_per_pa에서 유도하지 않는다(압력×속도 스케일이 다름) — meta에 실측으로 명시된
    값만 쓰고, 문헌 캘리브레이션 상수(a1=159 Å/s 등)를 몰래 기본값으로 쓰지 않는다. 하나라도
    없으면 조용한 보간·외삽 없이 None + 스킵 사유 note.
    """
    out: Dict[str, object] = {"cu_dishing_tugbawa_nm": None, "cu_erosion_tugbawa_nm": None,
                              "cu_dishing_tugbawa_note": None}
    if rr.base.pack != "cu_h2o2_bta" or rr.wafer != "PTW":
        return out
    meta = rr.meta
    missing_layout = [k for k in ("pattern_density", "linewidth_um", "space_um") if k not in meta]
    if missing_layout:
        out["cu_dishing_tugbawa_note"] = "PTW 패턴 레이아웃 정보(선폭/스페이스/밀도) 없음 — 계산 스킵"
        return out
    if "r_cu_angstrom_s" not in meta or "r_ox_angstrom_s" not in meta:
        out["cu_dishing_tugbawa_note"] = (
            "PTW r_cu_angstrom_s/r_ox_angstrom_s(블랭킷 실측 제거율) meta 미지정 — 문헌 캘리브레이션 "
            "상수를 대신 쓰지 않고 계산 스킵")
        return out
    try:
        import cu_dishing_erosion_tugbawa as CDE   # sim/tier2_physics (1바이트도 수정 안 함)
        result = CDE.cu_overpolish_dishing_erosion(
            r_cu=float(meta["r_cu_angstrom_s"]), r_ox_measured=float(meta["r_ox_angstrom_s"]),
            phi_cu=float(meta["pattern_density"]), w=float(meta["linewidth_um"]),
            s=float(meta["space_um"]), t_overpolish=rr.time_s)
    except Exception as e:
        out["cu_dishing_tugbawa_note"] = f"Tugbawa dishing/erosion 계산 실패({e}) — None으로 둠"
        return out
    out["cu_dishing_tugbawa_nm"] = result["dishing_nm"]
    out["cu_erosion_tugbawa_nm"] = result["erosion_nm"]
    out["cu_dishing_tugbawa_note"] = "; ".join(result["notes"]) if result["notes"] else None
    return out


def _colloid_stability_diagnostic(rr: "ResolvedRecipe") -> Dict[str, object]:
    """DLVO 콜로이드 응집 위험 정성 진단(IEP 거리) — MRR 경로와 완전히 독립적인 진단 계산.

    근거: sim/tier2_physics/dlvo_colloid.py stability_qualitative()
    (knowledge/cmp/colloid-zeta-dlvo-slurry-stability.md §5). 팩에 정량 zeta potential·
    이온세기 실측값이 없어(지어내지 않음) |pH-IEP| 거리만으로 판정하는 경량 정성 함수다.
    slurry_ph·abrasive_iep_ph가 둘 다 팩에 있을 때만 계산 — cu_h2o2_bta·w_fe_oxidizer처럼
    abrasive_iep_ph가 없는 팩은 roughness_ra_nm과 같은 지위로 조용히 None.
    """
    out: Dict[str, object] = {"colloid_distance_from_iep_ph": None,
                              "colloid_stability_risk": None,
                              "colloid_stability_note": None}
    if not (rr.pack.has("slurry_ph") and rr.pack.has("abrasive_iep_ph")):
        return out
    try:
        import dlvo_colloid as DLVO   # sim/tier2_physics (기존 함수 무수정, 신규 함수만 사용)
        ph = rr.p("slurry_ph")
        iep = rr.p("abrasive_iep_ph")
        result = DLVO.stability_qualitative(ph, iep)
    except Exception as e:
        out["colloid_stability_note"] = f"콜로이드 안정성 진단 실패({e}) — None으로 둠"
        return out
    out["colloid_distance_from_iep_ph"] = result["distance_from_iep_ph"]
    out["colloid_stability_risk"] = result["risk"]
    out["colloid_stability_note"] = result["note"]
    return out


def _gw_contact_linearity_diagnostic(rr: "ResolvedRecipe") -> Dict[str, object]:
    """GW 접촉모델 → Preston Kp 물리 분해 진단 — MRR 경로와 완전히 독립적인 진단 계산.

    근거: sim/tier2_physics/gw_preston_link.py (self-test 4/4 PASS),
    knowledge/materials/gw-nominal-vs-local-pressure.md,
    knowledge/materials/hertz-gw-contact-mechanics.md.
    이 레시피의 실제 압력범위(zone_pressures_psi가 있으면 그 값들, 없으면
    0.5x/1x/1.5x P_center 3점)에서 n_contacts(P)의 P-선형성을 재확인하고,
    이 팩 조건(P=rr.pressure_psi, Kp=rr.kp_m_per_pa)에서 alpha_removal을 역산해
    Kp_physical = alpha_removal * dn/dP 을 구한다(정의상 이 지점에서는 항등식).
    pad_E_star_pa 등 GW 5개 패드 파라미터가 팩에 없으면 조용히 None — 지어내지 않는다.
    """
    out: Dict[str, object] = {"gw_contact_linearity_max_dev": None,
                              "gw_kp_physical_to_lit_ratio": None,
                              "gw_contact_note": None}
    pad_keys = ("pad_E_star_pa", "pad_asperity_radius_m", "pad_height_beta_inv_m",
                "pad_asperity_density_m2", "pad_nominal_area_m2")
    if not all(rr.pack.has(k) for k in pad_keys):
        return out
    try:
        import gw_preston_link as GWL   # sim/tier2_physics (1바이트도 수정 안 함)
        from sim.tier1_empirical import kinematics as kin
        pad = dict(E_star=rr.p("pad_E_star_pa"), R=rr.p("pad_asperity_radius_m"),
                   beta=rr.p("pad_height_beta_inv_m"), eta=rr.p("pad_asperity_density_m2"),
                   A_n=rr.p("pad_nominal_area_m2"))
        P_center = rr.pressure_psi * PSI_TO_PA
        if rr.zone_pressures_psi:
            P_points = [p * PSI_TO_PA for p in rr.zone_pressures_psi]
        else:
            P_points = [0.5 * P_center, P_center, 1.5 * P_center]
        n_points = [GWL.n_contacts_at(P, **pad) for P in P_points]
        slope, intercept = GWL.linear_fit_slope(P_points, n_points)
        max_dev = max(abs((slope * P + intercept) - n) / n
                      for P, n in zip(P_points, n_points))
        U_mean = kin.speed_stats(rr.wafer_radius_m, rr.center_offset_m,
                                 rr.rpm_wafer, rr.rpm_platen)["mean"]
        alpha_removal = GWL.calibrate_alpha_removal(P_center, U_mean, rr.kp_m_per_pa, **pad)
        kp_physical = alpha_removal * slope
        ratio = kp_physical / rr.kp_m_per_pa
    except Exception as e:
        out["gw_contact_note"] = f"GW 접촉선형성 진단 실패({e}) — None으로 둠"
        return out
    out["gw_contact_linearity_max_dev"] = max_dev
    out["gw_kp_physical_to_lit_ratio"] = ratio
    out["gw_contact_note"] = (
        f"선형성 잔차 최대 {max_dev * 100:.1f}%(압력범위 {min(P_points) / 1e3:.1f}~"
        f"{max(P_points) / 1e3:.1f} kPa), GW-link/문헌 Kp 비 = {ratio:.3f}")
    return out


def _cu_pourbaix_diagnostic(rr: "ResolvedRecipe") -> Dict[str, object]:
    """Cu-H2O Pourbaix E-무관(수직·pH축) 진단 — MRR 경로와 완전히 독립적인 진단 계산.

    근거: sim/tier2_physics/cu_pourbaix.py (self-test 10/10 PASS),
    knowledge/cmp/cu-electrochemistry-pourbaix-bta-oxidizer-inhibitor.md.
    stable_phase()는 전극전위 E_V를 요구하지만 Recipe에 전극전위 필드가 없고
    산화제 농도에서 E를 환산할 1차 근거도 없다 — 그래서 E를 지어내 stable_phase()를
    부르지 않고, E와 무관한 수직선(Cu2+/Cu(OH)2 대용 경계) pH와 삼중점 pH만 낸다.
    log_a_cu(용존 Cu 활동도 로그)는 어떤 팩도 선언하지 않아 모듈 기본값 -4.0을 쓴다
    (note에 명시, YAML에 새로 넣지 않는다). Cu 계 판별은 팩 이름이 아니라 데이터
    필드 rr.film == "cu"로 한다(판정#34: 메커니즘/데이터로 판단, 이름 하드코딩 금지).
    slurry_ph가 없거나 film != "cu"면 조용히 None.
    """
    out: Dict[str, object] = {"cu_pourbaix_vertical_ph": None,
                              "cu_pourbaix_triple_point_ph": None,
                              "cu_pourbaix_soluble_domain": None,
                              "cu_pourbaix_note": None}
    if not rr.pack.has("slurry_ph"):
        out["cu_pourbaix_note"] = "slurry_ph 팩에 없음 — Cu Pourbaix 진단 스킵"
        return out
    if rr.film != "cu":
        out["cu_pourbaix_note"] = f"Cu 계 아님(film='{rr.film}') — Cu Pourbaix 진단 스킵"
        return out
    try:
        import cu_pourbaix as CUP   # sim/tier2_physics (1바이트도 수정 안 함)
        ph = rr.p("slurry_ph")
        if rr.pack.has("log_a_cu"):
            log_a_cu = rr.p("log_a_cu")
            log_a_note = f"log_a_cu={log_a_cu} 팩 선언값 사용"
        else:
            log_a_cu = -4.0
            log_a_note = "log_a_cu=-4.0 기본값 가정, 팩 미선언"
        vert_ph = CUP.cu2_cuoh2_vertical_pH(log_a_cu)
        triple_ph = CUP.triple_point_pH(log_a_cu)
    except Exception as e:
        out["cu_pourbaix_note"] = f"Cu Pourbaix 진단 실패({e}) — None으로 둠"
        return out
    out["cu_pourbaix_vertical_ph"] = vert_ph
    out["cu_pourbaix_triple_point_ph"] = triple_ph
    out["cu_pourbaix_soluble_domain"] = ph < vert_ph
    out["cu_pourbaix_note"] = (
        f"{log_a_note}. 전극전위 E 무관 수직선/삼중점 pH만 계산(Recipe에 전극전위 필드 없음, "
        f"산화제 농도→E 환산 1차 근거 없어 stable_phase() 미호출) — 수직선 pH={vert_ph:.2f}, "
        f"삼중점 pH={triple_ph:.2f}. Cu(OH)2는 CuO 자리 대용, 미검증(CRC 표에 CuO 반쪽반응 없음).")
    return out


def _pad_groove_eol_diagnostic(rr: "ResolvedRecipe") -> Dict[str, object]:
    """패드 그루브 깊이 소진 EOL 진단 — MRR 경로와 완전히 독립적인 진단 계산.

    근거: sim/tier2_physics/pad_groove_eol.py (self-test 9/9 PASS),
    knowledge/materials/pad-thickness-groove-depth-monitoring-replacement-economics.md
    (Son & Lee 2021, Appl. Sci. 11(8) 3521, doi:10.3390/app11083521) §2.
    누적 컨디셔닝 시간 t는 recipe.meta의 pad_hours를 쓴다(sim/models.py의
    tier2.wear_aware, sim/slots.py가 이미 같은 값을 쓴다) — 컨디셔닝 시간과
    연마 시간이 동일하다고 가정한다(Recipe에 컨디셔닝 전용 시간 필드가 없다).
    컷레이트 c는 절대 하드코딩하지 않는다 — 팩이 pad_cut_rate_um_per_h를
    선언할 때만 계산하고, 없으면 스킵한다(풀컨택트 43.4 μm/h vs 분할컨택트
    22.2 μm/h 중 어느 쪽인지 팩이 정하지 않았으므로 임의로 고르지 않는다 —
    현재 5팩 전부 미선언이라 항상 None이 정상이다). 초기 그루브 깊이 D0는
    base.yaml의 groove_depth_mm(0.76mm=760um, confidence literature)을
    mm->um 환산만 해서 쓴다 — 새 값을 YAML에 넣지 않는다. glazing EOL 시각을
    내는 로직이 엔진에 없어(factors.py의 S 팩터는 정상상태 두께/포화도만 내고
    EOL 시각을 내지 않는다) OR 결합(replacement_time_hours)은 호출하지 않고
    그루브 EOL만 낸다.
    """
    out: Dict[str, object] = {"pad_groove_cumulative_wear_um": None,
                              "pad_groove_eol_hours": None,
                              "pad_groove_exhausted": None,
                              "pad_groove_note": None}
    if not rr.pack.has("pad_cut_rate_um_per_h"):
        out["pad_groove_note"] = (
            "pad_cut_rate_um_per_h 미선언 — 43.4(풀컨택트)/22.2(분할) 중 어느 "
            "컨디셔닝 방식인지 팩이 정하지 않아 스킵")
        return out
    try:
        import pad_groove_eol as PGE   # sim/tier2_physics (1바이트도 수정 안 함)
        c = rr.p("pad_cut_rate_um_per_h")
        hours = float(rr.meta.get("pad_hours", 0) or 0)
        d0_um = rr.pack.param("groove_depth_mm").value * 1000.0  # mm -> um
        cum = PGE.cumulative_wear_um(c, hours)
        eol_h = PGE.groove_eol_hours(c, d0_um)
        exhausted = PGE.groove_exhausted(cum, d0_um)
    except Exception as e:
        out["pad_groove_note"] = f"패드 그루브 EOL 진단 실패({e}) — None으로 둠"
        return out
    out["pad_groove_cumulative_wear_um"] = cum
    out["pad_groove_eol_hours"] = eol_h
    out["pad_groove_exhausted"] = exhausted
    out["pad_groove_note"] = (
        f"컨디셔닝 시간과 연마 시간이 동일하다고 가정(meta.pad_hours={hours:g}h 사용). "
        f"c={c:g} μm/h, D0={d0_um:g} μm(groove_depth_mm={d0_um / 1000.0:g}mm). "
        f"누적마모={cum:.1f} μm, 그루브 EOL={eol_h:.2f} h. "
        f"glazing EOL 미산출이라 OR 결합 미수행.")
    return out


def _galvanic_hydroxide_diagnostic(rr: "ResolvedRecipe") -> Dict[str, object]:
    """갈바닉 부식 방향·Cu 수산화물 전이 pH 진단 — MRR 경로와 완전히 독립적인 진단 계산.

    근거: sim/tier2_physics/galvanic_hydroxide_ph.py, knowledge/cmp/
    low-level-metal-cobalt-ruthenium-cross-contamination.md §3.1(표준환원전위)·
    §3.3(수산화물 전이 pH)·§7(한계).

    (1) 수산화물 전이 pH: Cu 계 판별은 팩 이름이 아니라 데이터 필드 rr.film == "cu"로
    한다(판정#34). 용존 Cu 농도는 _cu_pourbaix_diagnostic()과 완전히 같은 관례를
    쓴다 — 팩이 log_a_cu를 선언하면 C=10**log_a_cu, 미선언이면 모듈 기본값 -4.0을
    가정한다(note에 명시, YAML에 새로 넣지 않는다). 같은 문서 안에서 두 진단이 다른
    가정을 쓰면 숫자가 모순되므로 관례를 통일했다.
    (2) 갈바닉 쌍 방향: 접촉 상대 금속 필드가 Recipe/팩 어디에도 없다. 팩이
    contact_metal을 선언할 때만 계산하고(현재 5팩 전부 미선언이라 항상 None이 정상),
    Co나 Ru를 '보통 그렇다'며 임의로 골라 넣지 않는다.
    한계(모듈 docstring): ΔE_corr 실제 크기는 표준전위로 예측 불가(Lee 2021 4배,
    Seo 2019 1/15) — 방향(anode/cathode)만 신뢰할 것. 금속 가수분해·박막 실제 IEP는
    미반영.
    """
    out: Dict[str, object] = {"galvanic_anode_metal": None,
                              "galvanic_delta_e0_v": None,
                              "hydroxide_transition_ph": None,
                              "hydroxide_precipitation_expected": None,
                              "galvanic_hydroxide_note": None}
    try:
        import galvanic_hydroxide_ph as GHP   # sim/tier2_physics (1바이트도 수정 안 함)
    except Exception as e:
        out["galvanic_hydroxide_note"] = f"갈바닉/수산화물 진단 실패({e}) — None으로 둠"
        return out

    notes: List[str] = []
    if rr.film != "cu":
        notes.append(f"Cu 계 아님(film='{rr.film}') — 수산화물 전이 pH 스킵")
    elif not rr.pack.has("slurry_ph"):
        notes.append("slurry_ph 팩에 없음 — 수산화물 전이 pH 스킵")
    else:
        try:
            ph = rr.p("slurry_ph")
            if rr.pack.has("log_a_cu"):
                log_a_cu = rr.p("log_a_cu")
                log_a_note = f"log_a_cu={log_a_cu} 팩 선언값 사용"
            else:
                log_a_cu = -4.0
                log_a_note = "log_a_cu=-4.0 기본값 가정, 팩 미선언"
            trans_ph = GHP.hydroxide_transition_pH("Cu", 10 ** log_a_cu)
            out["hydroxide_transition_ph"] = trans_ph
            out["hydroxide_precipitation_expected"] = ph > trans_ph
            notes.append(
                f"{log_a_note}. Cu(OH)2 전이 pH={trans_ph:.2f}, slurry_ph={ph:.2f} → "
                f"{'전이 pH 위(수산화물 침전 영역)' if ph > trans_ph else '전이 pH 아래(용존 영역)'}.")
        except Exception as e:
            notes.append(f"수산화물 전이 pH 계산 실패({e}) — None으로 둠")

    if not rr.pack.has("contact_metal"):
        notes.append("접촉 상대 금속 미선언 — 갈바닉 쌍 판정 스킵")
    else:
        film_to_metal = {"cu": "Cu"}
        film_metal = film_to_metal.get(rr.film)
        if film_metal is None:
            notes.append(f"film='{rr.film}'에 대응하는 금속명 매핑 없음 — 갈바닉 쌍 판정 스킵")
        else:
            try:
                contact_metal = rr.p("contact_metal")
                pair = GHP.galvanic_pair_direction(film_metal, contact_metal)
                out["galvanic_anode_metal"] = pair["anode"]
                out["galvanic_delta_e0_v"] = pair["delta_E0_V"]
                notes.append(
                    f"갈바닉 쌍({film_metal}-{contact_metal}): 양극={pair['anode']}, "
                    f"ΔE0={pair['delta_E0_V']:.4f} V(방향만 신뢰, 실제 크기 아님).")
            except Exception as e:
                notes.append(f"갈바닉 쌍 판정 실패({e}) — None으로 둠")

    notes.append(
        "한계: ΔE_corr 실제 크기는 표준전위로 예측 불가(Lee 2021 4배, Seo 2019 1/15) — "
        "방향만 신뢰할 것. 금속 가수분해·박막 실제 IEP는 미반영.")
    out["galvanic_hydroxide_note"] = " ".join(notes)
    return out


def _pourbaix_nernst_diagnostic(rr: "ResolvedRecipe") -> Dict[str, object]:
    """금속막 표면 산화막 반응의 Pourbaix 경계선 Nernst pH 기울기 진단 — MRR 경로와 완전히 독립.

    근거: sim/tier2_physics/pourbaix_nernst_slope.py (원본 무수정),
    knowledge/cmp/surface-chemistry-cu-w-pourbaix-passivation.md (slurry-chemist Lv2-1).
    반응 a·Ox + m·H+ + n·e- = b·Red 의 Nernst 식에서 전위-pH 경계선 기울기는
    dE/dpH = -(RT/F)·ln10·(m/n) = -59.16·(m/n) mV/pH (25 degC). 이 관계 자체는
    Pourbaix Atlas 원저 없이도 Nernst 식에서 독립 유도되므로 유료벽과 무관하다.

    **이 진단이 무엇을 말해주는가**: m==n인 반응(H+ 1개당 전자 1개)은 표준 -59.16 mV/pH
    계열이고, 화학양론적으로 치밀한 산화막(WO3·Cu(OH)2)을 만드는 전형적 passivation
    반응이다. 즉 "이 막질의 부동태는 pH를 1 올릴 때 전위 창이 몇 mV 내려가는가"를 준다.
    ψ(표면 흡착 보호) 팩터의 물리적 배경을 읽는 용도이지, ψ 값을 계산하는 경로가 아니다.

    **적용 범위**: 금속막일 때만 계산한다. 판정#34 원칙에 따라 팩 이름이 아니라 데이터
    필드 rr.film로 판별한다(현재 cu·w). 산화막(oxide)·SiC(sic_4h)는 모듈의
    CMP_SURFACE_REACTIONS에 대응 반응식이 없어 조용히 None + 스킵사유를 낸다 —
    세리아-실리카 Si-O-Ce "chemical tooth"는 산화환원 반응이 아니라 애초에 Nernst
    기울기가 정의되지 않는다(전자 이동이 없으면 pH축 위 수직선).

    **n==0 반응은 제외한다**: 모듈의 반응 목록에는 Cu(OH)2 -> CuO + H2O(탈수, 산-염기형)이
    참고용으로 들어 있는데 전자가 오가지 않아 Nernst 기울기가 미정의다(모듈 자신도
    nernst_ph_slope에서 n==0에 ValueError를 던진다). 이 진단은 n>0인 산화환원 반응만
    집계한다. ⚠ 원본 모듈의 is_self_limiting_type()은 m==n을 보므로 m=n=0인 그 탈수
    반응에도 True를 돌려준다 — 원본을 고치지 않는 대신 여기서 n>0 필터를 먼저 적용해
    그 사례가 집계에 섞이지 않게 한다.

    한계(노트 그대로 전파): 반응식의 m·n 계수는 Gamagedara & Roy 2024
    (Materials 17(19) 4905, PMC11477894, CC BY)와 Krishnan et al. Chem.Rev.2010의
    **2차 인용 정리**다. 기울기 공식 자체는 1차 유도지만 어떤 반응이 이 계에서 실제
    지배적인지는 슬러리 조성·전위에 달려 있고, 이 진단은 그것을 판정하지 않는다.
    """
    out: Dict[str, object] = {"pourbaix_nernst_slope_mv_per_ph": None,
                              "pourbaix_self_limiting_reactions": None,
                              "pourbaix_nernst_note": None}
    film_to_reaction_key = {"cu": "Cu", "w": "W"}
    key = film_to_reaction_key.get(rr.film)
    if key is None:
        out["pourbaix_nernst_note"] = (
            f"film='{rr.film}' — 금속막이 아니라 Pourbaix 표면 반응식이 없어 Nernst "
            f"기울기 진단 스킵(전자 이동이 없는 계는 pH축 위 수직선이라 dE/dpH 미정의)")
        return out
    try:
        import pourbaix_nernst_slope as PNS   # sim/tier2_physics (1바이트도 수정 안 함)
        # 반응식 좌변(->  앞)의 화학종 토큰에 대상 금속이 있는지로 고른다.
        # startswith는 "2Cu + 2OH- -> Cu2O ..."처럼 계량계수가 앞에 붙은 반응식을
        # 놓친다(실측: Cu가 2건 중 1건만 잡혔다). 좌변만 보는 이유는 Cu(OH)2 ->
        # CuO 같은 생성물 쪽 등장으로 오매칭되는 것을 막기 위해서다.
        def _lhs_has_metal(name: str) -> bool:
            lhs = name.split("->")[0]
            return re.search(rf"(?<![A-Za-z]){re.escape(key)}(?![a-z])", lhs) is not None
        rxns = [r for r in PNS.CMP_SURFACE_REACTIONS
                if r.n > 0 and _lhs_has_metal(r.name)]
        if not rxns:
            out["pourbaix_nernst_note"] = (
                f"film='{rr.film}'에 대응하는 산화환원 반응식이 모듈 목록에 없음 — 스킵")
            return out
        slopes = [r.slope_mV_per_pH() for r in rxns]
        n_self_lim = sum(1 for r in rxns if r.is_self_limiting_type())
    except Exception as e:
        out["pourbaix_nernst_note"] = f"Nernst 기울기 진단 실패({e}) — None으로 둠"
        return out
    # 모든 반응이 같은 기울기면 그 값을, 갈리면 대표값을 내지 않고 None으로 둔다
    # (평균은 어느 문헌도 지지하지 않는 창작이다 — EVIDENCE-RULES "두 지수를 평균내지 마라").
    uniq = sorted(set(round(x, 6) for x in slopes))
    detail = "; ".join(f"{r.name.split(' (')[0]}: m={r.m}, n={r.n}, "
                       f"{r.slope_mV_per_pH():.2f} mV/pH" for r in rxns)
    if len(uniq) == 1:
        out["pourbaix_nernst_slope_mv_per_ph"] = float(uniq[0])
        rep = f"전 반응 동일 기울기 {uniq[0]:.2f} mV/pH"
    else:
        rep = (f"반응마다 기울기가 갈림({uniq}) — 어느 반응이 지배적인지 이 진단은 "
               f"판정하지 않으므로 대표값을 내지 않는다(평균 금지)")
    out["pourbaix_self_limiting_reactions"] = n_self_lim
    out["pourbaix_nernst_note"] = (
        f"film='{rr.film}' 금속막 Pourbaix 경계선 dE/dpH = -59.16·(m/n) mV/pH (25 degC). "
        f"{rep}. m==n(치밀 산화막 passivation 계열) 반응 {n_self_lim}/{len(rxns)}건. {detail}. "
        f"⚠ 반응식 m·n 계수는 2차 인용(Gamagedara & Roy 2024 PMC11477894, "
        f"Krishnan et al. 2010) — 기울기 공식은 Nernst 식 1차 유도지만 이 계에서 어느 "
        f"반응이 지배적인지는 판정하지 않는다. ψ 팩터 계산 경로가 아니라 배경 진단이다.")
    return out


def _pad_glazing_diagnostic(rr: "ResolvedRecipe") -> Dict[str, object]:
    """패드 글레이징에 의한 접촉점 감소·asperity 반경 증가 진단 — MRR 경로와 완전히 독립.

    근거: sim/tier2_physics/pad_glazing_jeong2024.py (self-test 6/6 PASS, 원본 무수정),
    knowledge/materials/pad-glazing-mechanism-mrr-decay.md (Jeong et al. 2024,
    Materials 17, 1817, doi:10.3390/ma17081817) Table 1 · Eq.4.

    **적용 범위를 좁게 잡은 이유** — 이 모듈은 다른 진단보다 전제가 훨씬 까다롭다.
    세 관문을 전부 통과할 때만 계산하고, 하나라도 어긋나면 지어내지 않고 스킵한다:

    (1) 컨디셔닝이 없어야 한다. Jeong 2024의 Table 1/Fig.9는 **컨디셔닝 없이** 연마한
        패드를 측정한 것이다(Table 1의 N_cond 열이 보여주듯 1분만 컨디셔닝해도 접촉점
        수가 초기값 수준으로 회복된다: 2psi에서 56 -> 114). in-situ 컨디셔닝이 도는
        공정에 이 감쇠곡선을 그대로 씌우면 근거 없는 외삽이다. 팩의 cond_duty_pct가
        0일 때만 계산한다(base.yaml 기본값은 100 = in-situ 연속이므로 **현재 5팩은
        전부 스킵이 정상**이다).
    (2) 압력이 Table 1에 있어야 한다(2·3·4·5 psi). tau는 표 데이터 최소자승 피팅으로
        압력마다 따로 나오며 모듈이 그 외 압력에 ValueError를 던진다 — 보간하지 않는다
        (특히 5 psi의 tau=6.0 min은 2~4 psi의 13.6~13.8 min에서 급락해, 사이 값을
        선형보간할 근거가 없다).
    (3) 시간이 측정 구간 안이어야 한다. Table 1의 측정 상한은 2~4 psi에서 10분,
        5 psi에서 5분이다. 그 너머는 지수감쇠 외삽이라 계산하지 않는다.

    시간 축으로는 **이번 런의 연마시간 rr.time_s**를 쓴다 — meta의 pad_hours가 아니다.
    S13 판정(~/software/BACKLOG.md)이 이미 지적했듯 pad_hours는 컨디셔닝 사이클을 포함한
    패드 **누적 사용 시간(h)**이고, Jeong 2024의 t는 컨디셔닝 없는 **단일 연마의 경과
    분(min)**이라 척도가 다르다. 두 축을 잇는 매핑은 문헌에 없다.

    한계(원본 모듈 docstring의 "정직 기록" 그대로 전파): relative_mrr_proxy는
    contact_ratio x radius_growth_ratio라는 가장 거친 근사이고, 실제 압입깊이·유효
    탄성계수·Jeong 2024 §4.2의 3-모드 MRR 공식(Eq.20)은 들어 있지 않다. self-test에서
    피크 시점(t≈7분)과 t=10분 상대값(1.21 > 1.0)이 Fig.9 실측과 어긋난다는 것이 이미
    확인돼 있다. **정량 캘리브레이션에 쓰지 말 것** — 비단조성 존재라는 방향성까지만
    사용 가치가 있다. note에 이 경고를 항상 실어 보낸다.
    """
    out: Dict[str, object] = {"pad_glazing_contact_ratio": None,
                              "pad_glazing_radius_growth_ratio": None,
                              "pad_glazing_relative_mrr_proxy": None,
                              "pad_glazing_note": None}
    if not rr.pack.has("cond_duty_pct"):
        out["pad_glazing_note"] = (
            "cond_duty_pct 팩 미선언 — 컨디셔닝 유무를 알 수 없어 글레이징 진단 스킵 "
            "(Jeong 2024는 컨디셔닝 없는 연마 실측이라 in-situ 공정에 그대로 쓸 수 없다)")
        return out
    duty = rr.p("cond_duty_pct")
    if duty != 0:
        out["pad_glazing_note"] = (
            f"cond_duty_pct={duty:g}% (컨디셔닝 있음) — 글레이징 감쇠 진단 스킵. "
            f"Jeong 2024 Table 1은 컨디셔닝 없는 연마 실측이고, 같은 표가 1분 컨디셔닝만으로 "
            f"접촉점 수가 초기 수준으로 회복됨을 보인다(2psi: 56→114). 외삽하지 않는다.")
        return out
    try:
        import pad_glazing_jeong2024 as PGJ   # sim/tier2_physics (1바이트도 수정 안 함)
        t_tab, _n_tab, _n_cond = PGJ.contact_count_table()
    except Exception as e:
        out["pad_glazing_note"] = f"패드 글레이징 진단 로드 실패({e}) — None으로 둠"
        return out
    p_psi = rr.pressure_psi
    p_key = int(round(p_psi))
    if abs(p_psi - p_key) > 1e-9 or p_key not in t_tab:
        out["pad_glazing_note"] = (
            f"pressure_psi={p_psi:g} — Jeong 2024 Table 1에 없는 압력(있는 값: "
            f"{sorted(t_tab)} psi)이라 스킵. tau가 압력마다 표 피팅으로 따로 나오고 "
            f"5 psi에서 6.0 min으로 급락(2~4 psi는 13.6~13.8 min)해 보간 근거가 없다.")
        return out
    t_min = rr.time_s / 60.0
    t_max = max(t_tab[p_key])
    if t_min > t_max:
        out["pad_glazing_note"] = (
            f"연마시간 {t_min:.2f} min > Table 1의 {p_key} psi 측정 상한 {t_max:g} min "
            f"— 지수감쇠 외삽이라 계산하지 않는다.")
        return out
    try:
        cr = float(PGJ.contact_ratio(p_key, t_min))
        rg = float(PGJ.radius_growth_ratio(p_key, t_min))
        proxy = float(PGJ.relative_mrr_proxy(p_key, t_min))
    except Exception as e:
        out["pad_glazing_note"] = f"패드 글레이징 진단 실패({e}) — None으로 둠"
        return out
    out["pad_glazing_contact_ratio"] = cr
    out["pad_glazing_radius_growth_ratio"] = rg
    out["pad_glazing_relative_mrr_proxy"] = proxy
    out["pad_glazing_note"] = (
        f"컨디셔닝 없음(cond_duty_pct=0), {p_key} psi, 연마 {t_min:.2f} min 기준: "
        f"접촉점비 N/N0={cr:.4f}, 반경증가배율={rg:.4f}, relative_mrr_proxy={proxy:.4f}. "
        f"⚠ proxy는 '접촉당 힘x개수'의 가장 거친 근사(반경만으로 접촉력 근사)이며 "
        f"Jeong 2024 §4.2 3-모드 MRR 공식 미구현 — self-test에서 피크시점·t=10 상대값이 "
        f"Fig.9 실측과 어긋남이 확인됐다. 정량 캘리브레이션 금지, 방향성(비단조성)만 볼 것.")
    return out


def _conditioner_sweep_diagnostic(rr: "ResolvedRecipe") -> Dict[str, object]:
    """컨디셔너 스윕 궤적 PCR(r) 상대 프로파일 요약 진단 — MRR 경로와 완전히 독립적인 진단 계산.

    근거: sim/tier2_physics/conditioner_sweep_kinematics.py (Zheng, Zhao & Lu 2023,
    Micromachines 14(9) 1683, PMC10536193, Eq.1-9 재현), knowledge/equipment/
    conditioner-sweep-kinematics-pcr-profile.md. 반경별 누적 스크래치 거리 히스토그램은
    Preston형(k·P가 반경에 무관하다는 가정 하에) PCR(r)의 **상대적 형상**만 준다(절대값
    아님 — 모듈 docstring 명시). 이 진단은 그 형상을 두 스칼라로 요약한다: 변동계수
    CV=sigma/mu(낮을수록 패드가 반경에 걸쳐 균일하게 깎임), 바깥쪽 링 평균/안쪽 링 평균.

    비용 측정(2026-09-15, .venv python, 아래와 동일 인자로 timeit): duration_s=20.0,
    dt=0.01(2000 스텝) × n_particles=12 × r_bins=20 → 약 3.8ms/call
    (conditioner_sweep_kinematics.pcr_radial_profile 직접 호출, 로컬 측정치). 100ms 미만이라
    opt-in 플래그 없이 항상 계산한다 — 테스트 스위트 전체 실행시간에 미치는 영향은 무시할
    수준(회귀 실측: 이 진단이 실행되는 유일한 경로는 신규 테스트가 pack_overrides로 주입하는
    경우뿐이고, 실제 팩 5종은 전부 필수 입력 미선언이라 스킵 분기만 탄다). 수치해석 파라미터
    (duration_s·dt·n_particles·r_bins)는 문헌값이 아니라 이 함수의 기본 인자다 — YAML에
    넣지 않는다.

    필요 입력 R_p(패드 기준 팔 중심 궤도 반경)·R_a(팔 길이)·disk_radius(디스크 반경)·
    n_d(디스크 자전 RPM)·beta_s(스윕 시작각)·beta_max(스윕 범위, 라디안)는 어떤 팩도
    선언하지 않는다 — Zheng et al. Table 1은 RPM·하중·스윕범위(mm)만 보고하고, 이 모델이
    요구하는 기구 고정 치수(R_p·R_a·disk_radius)와 각도(beta_s·beta_max)는 지식노트에
    옮겨진 적이 없다. 지어내지 않고 스킵한다(현재 5팩 전부 미선언이라 항상 None이 정상).
    n_p(패드 RPM)는 rr.rpm_platen, n_a(스윕 속도)는 팩의 cond_sweep_cpm을 그대로 쓴다
    (둘 다 base.yaml에 이미 선언됨). cond_sweep_cpm 자체의 한계(노트 원문 경고: "스윕
    왕복수를 독립변수로 스윕해 PCR/MRR을 측정한 논문은 없다", 범위 9~19·2.1배)가 이
    진단에도 그대로 전파된다.

    모듈 한계(docstring §7 그대로): 실제 다이아몬드 전기도금 배치 패턴 대신 디스크 반경
    균등분포 샘플로 근사, self-test는 정성적 특징만 확인(정량 검증 아님).
    """
    out: Dict[str, object] = {"conditioner_sweep_profile_uniformity": None,
                              "conditioner_sweep_edge_center_ratio": None,
                              "conditioner_sweep_note": None}
    required = ["cond_arm_pivot_radius_m", "cond_arm_length_m", "cond_disk_radius_m",
                "cond_disk_rpm", "cond_sweep_beta_start_rad", "cond_sweep_beta_range_rad"]
    missing = [k for k in required if not rr.pack.has(k)]
    if missing:
        out["conditioner_sweep_note"] = (
            f"{', '.join(missing)} 팩에 없음 — 컨디셔너 스윕 PCR 프로파일 진단 스킵 "
            f"(Zheng et al. Table 1은 RPM·하중·스윕범위(mm)만 보고, 이 기구 고정 치수·각도는 "
            f"어떤 팩도 선언하지 않음)")
        return out
    try:
        import conditioner_sweep_kinematics as CSK   # sim/tier2_physics (1바이트도 수정 안 함)
        R_p = rr.p("cond_arm_pivot_radius_m")
        R_a = rr.p("cond_arm_length_m")
        disk_radius = rr.p("cond_disk_radius_m")
        n_d = rr.p("cond_disk_rpm")
        beta_s = rr.p("cond_sweep_beta_start_rad")
        beta_max = rr.p("cond_sweep_beta_range_rad")
        n_p = rr.rpm_platen
        n_a = rr.p("cond_sweep_cpm")
        duration_s, dt, n_particles, r_bins = 20.0, 0.01, 12, 20
        bin_centers, pca = CSK.pcr_radial_profile(
            duration_s=duration_s, dt=dt, R_p=R_p, R_a=R_a, disk_radius=disk_radius,
            n_p=n_p, n_a=n_a, n_d=n_d, beta_s=beta_s, beta_max=beta_max,
            n_particles=n_particles, r_bins=r_bins)
        mu = float(np.mean(pca))
        sigma = float(np.std(pca))
        cv = sigma / mu if mu > 0 else None
        half = len(pca) // 2
        inner_mean = float(np.mean(pca[:half])) if half > 0 else None
        outer_mean = float(np.mean(pca[half:])) if half > 0 else None
        ratio = (outer_mean / inner_mean) if (inner_mean is not None and inner_mean > 0) else None
    except Exception as e:
        out["conditioner_sweep_note"] = f"컨디셔너 스윕 PCR 진단 실패({e}) — None으로 둠"
        return out
    cv_str = f"{cv:.4f}" if cv is not None else "N/A(mu<=0)"
    ratio_str = f", edge/center={ratio:.4f}" if ratio is not None else ""
    out["conditioner_sweep_profile_uniformity"] = cv
    out["conditioner_sweep_edge_center_ratio"] = ratio
    out["conditioner_sweep_note"] = (
        f"PCR(r) 상대 프로파일(절대값 아님, k·P 반경무관 가정) 요약. "
        f"n_p={n_p:g} RPM(rpm_platen), n_a={n_a:g} cpm(cond_sweep_cpm, ⚠ 스윕 왕복수 독립변수 "
        f"스윕 문헌 없음, 범위 9~19), n_d={n_d:g} RPM, R_p={R_p:g}/R_a={R_a:g}/"
        f"disk_radius={disk_radius:g}m. 수치해석: duration_s={duration_s:g}, dt={dt:g}"
        f"({int(duration_s / dt)}스텝), n_particles={n_particles}, r_bins={r_bins}"
        f"(전부 재현용 함수 기본값, 문헌값 아님 — 비용 측정 약 3.8ms/call이라 opt-in 없이 "
        f"항상 계산). CV={cv_str}{ratio_str}. 한계: 실제 다이아몬드 배치 패턴 미반영"
        f"(균등분포 근사), self-test는 정성적 특징만 확인(정량 검증 아님).")
    return out


# ───────────────────────────────────────────────────────────── 실행
def simulate(recipe: Recipe, model: str = "tier1.preston_radial") -> WaferResult:
    """레시피를 팩으로 해석한 뒤 실행한다.

    핵심 순서: resolve()가 먼저다. 팩에 없는 물성을 요구하면 여기서 KeyError로
    죽는다 — 조용히 기본값을 쓰고 그럴듯한 숫자를 뱉는 것보다 낫다.
    """
    if model not in _MODELS:
        raise KeyError(f"등록되지 않은 모델: {model}. 사용 가능: {list(_MODELS)}")
    rr = recipe.resolve()          # ← 팩 해석. 여기가 이 설계의 전부다.
    notes: List[str] = []
    r_max = rr.wafer_radius_m - rr.edge_exclusion_m
    radius = np.linspace(0.0, r_max, rr.n_points)
    impl = _MODELS[model]
    mrr_m_s = impl.mrr_radial(rr, radius)
    # ── 병합 파라미터 결합 (ARCHITECTURE-V2.md §2 · sim/factors.py) ────────
    # ⚠ 여기서 chemistry_factor()를 직접 곱하지 않는다. factors.χ가 그것을
    #   승계했으므로 둘 다 곱하면 **화학을 두 번 센다** — 2026-09-06 Cu MRR
    #   20배 붕괴가 정확히 그 사고였다. 결합 지점은 이 한 곳뿐이다.
    #   MRR에 곱해지는 것은 factors.MRR_COUPLED(κ·χ·ψ)만이고, 나머지 팩터
    #   (Λ Π Θ Γ τ Δ S)는 진단·설계 정보로만 실린다.
    factors = compute_factors(rr)
    fmult, fnotes = mrr_multiplier(factors)
    mrr_m_s = mrr_m_s * fmult
    notes.append(f"병합 파라미터 MRR 배수 ×{fmult:.4f}")
    notes.extend(fnotes)
    for _f in factors.values():
        notes.extend(_f.notes)
    # ── 장비 출력값 — 설정값에서 저절로 도출되는 진단 신호 ──────────────
    # MRR 경로와 완전히 독립이다. 실패해도 시뮬레이션은 계속돼야 한다.
    try:
        eq_outputs = compute_outputs(rr)
    except Exception as _e:
        eq_outputs = {}
        notes.append(f"⚠ 장비 출력값 계산 실패: {type(_e).__name__}: {_e}")
    # 모델이 스스로 한계를 보고할 기회 — 지어내지 않고 모르는 것을 드러낸다
    if hasattr(impl, "notes"):
        notes.extend(impl.notes(rr))  # type: ignore[attr-defined]
    mrr_nm_min = mrr_m_s * 1e9 * 60.0
    removed = mrr_nm_min * (rr.time_s / 60.0)
    remaining = None
    if rr.initial_thickness_nm is not None:
        remaining = rr.initial_thickness_nm - removed
        if np.any(remaining < 0):
            notes.append("잔막 음수 — 오버폴리시. time_s 또는 initial_thickness 확인")
    if rr.wafer == "PTW" and model != "tier1.pattern_density":
        notes.append("PTW인데 패턴 모델을 쓰지 않았다 — model='tier1.pattern_density'로 실행하라. "
                     "지금 값은 NPW 등가")
    # 윤활 레짐 진단 — MRR 경로와 완전히 독립. 팩에 슬러리 점도·패드 Ra가 없으면 조용히 None.
    lube = _lubrication_diagnostics(rr)
    if lube.get("_note"):
        notes.append(lube["_note"])
    elif lube["lubrication_regime"] is not None:
        notes.append("윤활 레짐 진단(So·λ·COF)은 λ≈So 근사(δeff≈σ 가정)이며 "
                     "COF 절대값은 정성적 오더 추정, 실측 캘리브레이션 필요 "
                     "(knowledge/physics/cmp-lubrication-regimes.md §5,§7)")
    # 슬러리 필름두께 스케일 z0 진단 — MRR 경로와 완전히 독립. 팩에 슬러리 점도가 없으면 조용히 None.
    film = _film_thickness_diagnostic(rr)
    if film.get("_note"):
        notes.append(film["_note"])
    elif film["film_lubrication_note"] is not None:
        notes.append(film["film_lubrication_note"])
    # PTW 유효압력비 진단 — MRR 경로와 완전히 독립. PTW+pattern_density 없으면 조용히 None.
    eff_p = _effective_pressure_diagnostic(rr)
    if eff_p.get("_note"):
        notes.append(eff_p["_note"])
    elif eff_p["ptw_effective_pressure_ratio"] is not None:
        notes.append(eff_p["ptw_effective_pressure_note"])
    # Cu dishing/erosion(Tugbawa) 진단 — MRR 경로와 완전히 독립. 필요 meta 없으면 조용히 None.
    cu_de = _cu_dishing_erosion_tugbawa_diagnostic(rr)
    if cu_de["cu_dishing_tugbawa_note"]:
        notes.append(cu_de["cu_dishing_tugbawa_note"])
    # DLVO 콜로이드 응집 위험 진단 — MRR 경로와 완전히 독립. slurry_ph·abrasive_iep_ph 없으면 조용히 None.
    colloid = _colloid_stability_diagnostic(rr)
    if colloid["colloid_stability_note"]:
        notes.append(colloid["colloid_stability_note"])
    # GW 접촉역학 선형성/Preston Kp 물리분해 진단 — MRR 경로와 완전히 독립. GW 패드 파라미터
    # (pad_E_star_pa 등) 없으면 조용히 None.
    gw_contact = _gw_contact_linearity_diagnostic(rr)
    if gw_contact["gw_contact_note"]:
        notes.append(gw_contact["gw_contact_note"])
    # Θ 정상상태 열저항 네트워크 진단 — MRR 경로와 완전히 독립. 패드 두께·열전도도 없으면 조용히 None.
    theta_ss = _theta_steady_state_diagnostic(rr)
    if theta_ss["theta_steady_state_note"]:
        notes.append(theta_ss["theta_steady_state_note"])
    # Cu-H2O Pourbaix E-무관 진단 — MRR 경로와 완전히 독립. slurry_ph 없거나
    # film != "cu"면 조용히 None.
    cu_pourbaix = _cu_pourbaix_diagnostic(rr)
    if cu_pourbaix["cu_pourbaix_note"]:
        notes.append(cu_pourbaix["cu_pourbaix_note"])
    # 패드 그루브 깊이 소진 EOL 진단 — MRR 경로와 완전히 독립. pad_cut_rate_um_per_h
    # 팩 미선언이면 조용히 None(현재 5팩 전부 미선언이라 항상 None이 정상).
    pad_groove = _pad_groove_eol_diagnostic(rr)
    if pad_groove["pad_groove_note"]:
        notes.append(pad_groove["pad_groove_note"])
    # 갈바닉 부식 방향·Cu 수산화물 전이 pH 진단 — MRR 경로와 완전히 독립. 접촉 상대
    # 금속(contact_metal) 팩 미선언이면 갈바닉 필드는 조용히 None(현재 5팩 전부 미선언).
    galvanic_hydroxide = _galvanic_hydroxide_diagnostic(rr)
    if galvanic_hydroxide["galvanic_hydroxide_note"]:
        notes.append(galvanic_hydroxide["galvanic_hydroxide_note"])
    # 컨디셔너 스윕 PCR(r) 프로파일 요약 진단 — MRR 경로와 완전히 독립. 기구 고정 치수
    # (R_p·R_a·disk_radius·n_d·beta_s·beta_max) 팩 미선언이면 조용히 None(현재 5팩 전부 미선언).
    cond_sweep = _conditioner_sweep_diagnostic(rr)
    if cond_sweep["conditioner_sweep_note"]:
        notes.append(cond_sweep["conditioner_sweep_note"])
    # 패드 글레이징(컨디셔닝 없는 연마) 접촉점 감쇠 진단 — MRR 경로와 완전히 독립.
    # cond_duty_pct!=0(컨디셔닝 있음)·Table 1 밖 압력·측정상한 초과 시 조용히 None
    # (현재 5팩 전부 cond_duty_pct=100이라 항상 None이 정상).
    pad_glaze = _pad_glazing_diagnostic(rr)
    if pad_glaze["pad_glazing_note"]:
        notes.append(pad_glaze["pad_glazing_note"])
    # 금속막 Pourbaix 경계선 Nernst pH 기울기 진단 — MRR 경로와 완전히 독립.
    # 금속막(cu/w)이 아니면 조용히 None + 스킵사유.
    pourbaix_nernst = _pourbaix_nernst_diagnostic(rr)
    if pourbaix_nernst["pourbaix_nernst_note"]:
        notes.append(pourbaix_nernst["pourbaix_nernst_note"])
    # 이 런에 실제로 쓰인 값 중 검증 안 된 것을 결과에 실어 보낸다.
    # 팩 전체가 아니라 '쓰인 것'만 — 안 쓴 값의 미검증은 이 결과와 무관하다.
    weak = [k for k in rr.used_keys
            if rr.pack.has(k) and rr.pack.param(k).confidence in
            ("estimated", "unverified", "unknown")]
    if weak:
        notes.append(
            f"⚠ 미검증 물성 사용: {', '.join(sorted(weak))} "
            f"(팩 '{rr.pack.name}'). 절대값을 신뢰하지 말고 경향만 보라. "
            f"해결: 실데이터 캘리브레이션.")
    metrics = compute_metrics(radius, removed if remaining is None else remaining,
                              n_points=rr.n_points)
    return WaferResult(recipe=recipe, radius_m=radius, mrr_nm_per_min=mrr_nm_min,
                       removed_nm=removed, remaining_nm=remaining, metrics=metrics,
                       lubrication_regime=lube["lubrication_regime"],
                       cmp_sommerfeld_number=lube["cmp_sommerfeld_number"],
                       cof_stribeck_estimate=lube["cof_stribeck_estimate"],
                       film_z0_scale_um=film["film_z0_scale_um"],
                       film_lubrication_note=film["film_lubrication_note"],
                       ptw_effective_pressure_ratio=eff_p["ptw_effective_pressure_ratio"],
                       ptw_effective_pressure_note=eff_p["ptw_effective_pressure_note"],
                       cu_dishing_tugbawa_nm=cu_de["cu_dishing_tugbawa_nm"],
                       cu_erosion_tugbawa_nm=cu_de["cu_erosion_tugbawa_nm"],
                       cu_dishing_tugbawa_note=cu_de["cu_dishing_tugbawa_note"],
                       colloid_distance_from_iep_ph=colloid["colloid_distance_from_iep_ph"],
                       colloid_stability_risk=colloid["colloid_stability_risk"],
                       colloid_stability_note=colloid["colloid_stability_note"],
                       gw_contact_linearity_max_dev=gw_contact["gw_contact_linearity_max_dev"],
                       gw_kp_physical_to_lit_ratio=gw_contact["gw_kp_physical_to_lit_ratio"],
                       gw_contact_note=gw_contact["gw_contact_note"],
                       theta_steady_state_delta_T_k=theta_ss["theta_steady_state_delta_T_k"],
                       theta_heat_partition=theta_ss["theta_heat_partition"],
                       theta_steady_state_note=theta_ss["theta_steady_state_note"],
                       cu_pourbaix_vertical_ph=cu_pourbaix["cu_pourbaix_vertical_ph"],
                       cu_pourbaix_triple_point_ph=cu_pourbaix["cu_pourbaix_triple_point_ph"],
                       cu_pourbaix_soluble_domain=cu_pourbaix["cu_pourbaix_soluble_domain"],
                       cu_pourbaix_note=cu_pourbaix["cu_pourbaix_note"],
                       pad_groove_cumulative_wear_um=pad_groove["pad_groove_cumulative_wear_um"],
                       pad_groove_eol_hours=pad_groove["pad_groove_eol_hours"],
                       pad_groove_exhausted=pad_groove["pad_groove_exhausted"],
                       pad_groove_note=pad_groove["pad_groove_note"],
                       galvanic_anode_metal=galvanic_hydroxide["galvanic_anode_metal"],
                       galvanic_delta_e0_v=galvanic_hydroxide["galvanic_delta_e0_v"],
                       hydroxide_transition_ph=galvanic_hydroxide["hydroxide_transition_ph"],
                       hydroxide_precipitation_expected=galvanic_hydroxide["hydroxide_precipitation_expected"],
                       galvanic_hydroxide_note=galvanic_hydroxide["galvanic_hydroxide_note"],
                       conditioner_sweep_profile_uniformity=cond_sweep["conditioner_sweep_profile_uniformity"],
                       conditioner_sweep_edge_center_ratio=cond_sweep["conditioner_sweep_edge_center_ratio"],
                       conditioner_sweep_note=cond_sweep["conditioner_sweep_note"],
                       pad_glazing_contact_ratio=pad_glaze["pad_glazing_contact_ratio"],
                       pad_glazing_radius_growth_ratio=pad_glaze["pad_glazing_radius_growth_ratio"],
                       pad_glazing_relative_mrr_proxy=pad_glaze["pad_glazing_relative_mrr_proxy"],
                       pad_glazing_note=pad_glaze["pad_glazing_note"],
                       pourbaix_nernst_slope_mv_per_ph=pourbaix_nernst["pourbaix_nernst_slope_mv_per_ph"],
                       pourbaix_self_limiting_reactions=pourbaix_nernst["pourbaix_self_limiting_reactions"],
                       pourbaix_nernst_note=pourbaix_nernst["pourbaix_nernst_note"],
                       model=model, notes=notes, factors=factors,
                       equipment_outputs=eq_outputs,
                       pack=rr.pack.name, film=rr.film,
                       provenance=rr.pack.provenance(rr.used_keys))


def available_models() -> List[str]:
    return list(_MODELS)


if __name__ == "__main__":
    import json
    # 같은 엔진·같은 조건에 팩만 갈아끼운다 — 이게 이 설계의 목적이다
    for pack in ("oxide_silica", "sti_ceria", "cu_h2o2_bta"):
        r = Recipe(pack=pack, time_s=60, initial_thickness_nm=800.0, edge_pressure_amp=0.15)
        res = simulate(r)
        s = res.summary()
        print(f"[{pack:14s}] film={s['film']:6s} "
              f"MRR={s['mean_mrr_nm_min']:7.1f} nm/min  TTV={s['ttv_nm']:6.1f} nm")
