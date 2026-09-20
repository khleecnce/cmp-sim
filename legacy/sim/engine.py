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
from dataclasses import dataclass, field, asdict, fields as _fields
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
from sim.equipment import load_equipment_pack  # noqa: E402
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
    # 컨디셔너 디스크 장비팩(knowledge/equipment/packs/*.yaml) 선택 — 선택 필드.
    # None=지금까지와 완전히 동일 동작. 값을 줘도 이번 회차는 스키마만 세우는
    # 단계라 어떤 물리 계산에도 쓰지 않는다(sim/equipment.py 참조, 백로그 ㉺).
    conditioner_disk: Optional[str] = None

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
        # 장비팩(컨디셔너 디스크) — 선택. 지정 안 하면 None(MRR 경로 무영향).
        # 없는 팩 이름이면 load_equipment_pack이 FileNotFoundError로 즉시 실패한다
        # (params.py 선례와 동일 — 조용히 무시하지 않는다).
        equipment_pack = (load_equipment_pack(self.conditioner_disk)
                          if self.conditioner_disk is not None else None)
        return ResolvedRecipe(base=self, pack=pk, used_keys=used,
                              equipment_pack=equipment_pack, **vals)


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
    # 컨디셔너 디스크 장비팩 — base.conditioner_disk가 None이면 None(스키마 신설
    # 회차라 어떤 물리 계산도 이 필드를 읽지 않는다. 진단 표시에만 쓰인다).
    equipment_pack: Optional[ParamPack] = None

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
# summary()에서 제외할 필드 — 배열 프로파일과 이미 가공해 실은 구조체만.
# 진단 스칼라를 여기 추가하지 마라(그게 2026-09-16에 고친 결함 그 자체다).
_SUMMARY_EXCLUDE = frozenset({
    "recipe", "radius_m", "mrr_nm_per_min", "removed_nm", "remaining_nm",
    "metrics", "factors", "equipment_outputs", "notes", "provenance",
})


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
    cof_qf_used: Optional[float] = None            # Q_f(열수지)가 실제로 쓴 μ
    cof_estimate_vs_qf_ratio: Optional[float] = None
    cof_consistency_note: Optional[str] = None
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
    # GW 역문제(명목압력→분리거리) 런타임 해 진단 — MRR과 무관. sim/tier2_physics/
    # gw_pressure_solve.py::local_contact_state + gw_contact.py::plasticity_index/
    # gw_analytic_ratio. base.yaml의 real_contact_area_ratio(estimated, 3psi 대표값) note가
    # "압력 의존성을 정식으로 넣으려면 GW를 런타임에 풀어야 한다"고 자백한 것을 실행해
    # 정적 팩값과 런타임 해의 괴리를 gw_static_pack_ratio_deviation으로 노출한다.
    # GW 5개 패드 파라미터(_gw_contact_linearity_diagnostic과 동일 키)가 없으면 조용히 None.
    gw_solved_separation_m: Optional[float] = None
    gw_real_contact_area_ratio: Optional[float] = None
    gw_real_contact_pressure_pa: Optional[float] = None
    gw_static_pack_ratio_deviation: Optional[float] = None
    gw_plasticity_index: Optional[float] = None
    gw_contact_regime_note: Optional[str] = None
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
    # 그루브 마모 -> 슬러리 유동 상태 진단 (MRR 무관).
    # sim/tier2_physics/pad_groove_wear_flow.py
    pad_groove_residual_fraction: Optional[float] = None
    pad_groove_wear_stage: Optional[str] = None
    pad_groove_conductance_ratio: Optional[float] = None
    pad_groove_flow_note: Optional[str] = None
    # 억제제 Langmuir 피복률 포화도 진단 (MRR 무관).
    # sim/tier2_physics/slurry_components.py
    inhibitor_theta_equilibrium: Optional[float] = None
    inhibitor_theta_headroom: Optional[float] = None
    inhibitor_conc_discrimination: Optional[float] = None
    inhibitor_saturation_note: Optional[str] = None
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
    # 마찰열 ΔT_ss → Arrhenius 화학반응속도 배율 진단 — MRR과 무관. sim/tier2_physics/
    # frictional_heating_arrhenius.py::arrhenius_rate_ratio + Shin et al. 2025(Materials
    # 18(19) 4461, DOI 10.3390/ma18194461) §4 표 겉보기 Ea(재료별: SiO2 8.75 / Cu 151.7
    # kJ/mol — Ta 29.9는 팩에 대응 막질이 없어 미사용). Ea 미보고 막질(sic_4h·w)이거나
    # theta_steady_state_delta_T_k·platen_coolant_temp_c 중 하나라도 없으면 조용히 None.
    # ⚠ MRR에 곱하지 않는다 — Kp가 이미 특정 공정온도에서 역산된 값이라 곱하면 이중 계상.
    thermal_chemical_rate_ratio: Optional[float] = None
    thermal_chemical_ea_kj_mol: Optional[float] = None
    thermal_chemical_film: Optional[str] = None
    thermal_chemical_note: Optional[str] = None
    # 컨디셔너 디스크 노화 → PCR(t) 감쇠 진단 — MRR과 무관, 새 물리 아님. sim/tier2_physics/
    # conditioner_pcr_decay.py::pcr_decay(원본 무수정). ⚠ sim/factors.py::_f_gamma가 이미
    # 같은 함수로 이 PCR 노화 배수를 MRR 경로(Γ)에 반영 중이다 — 이 필드는 그 내부값을
    # 밖으로 드러내는 가시화이며 MRR에 다시 곱하지 않는다. cond_disk_usage_hours·
    # pad_pcr_anchor_hours·pad_pcr_anchor_ratio가 팩에 전부 있을 때만 채워진다(현재 5팩은
    # usage=0이라 배수가 항상 1.0이 정상). τ(≈27.4h)는 Entegris 백서가 재인용한 Palmgren
    # 2004(원문 미확보, 2차 인용) 역산값. simulate_conditioned_wear()(재생항 계수는
    # fab-sim 자체 최소확장 가정, 정량 미보증)는 등록하지 않는다.
    conditioner_pcr_aging_ratio: Optional[float] = None
    conditioner_pcr_tau_hours: Optional[float] = None
    conditioner_disk_usage_hours: Optional[float] = None
    conditioner_pcr_note: Optional[str] = None
    # 패드 유효 탄성률 E'(T) 온도의존 연화 진단 — MRR과 무관, 진단 전용. sim/tier2_physics/
    # pad_viscoelastic_temperature.py::e_pad_from_table(원본 무수정), Cabot US20170087688A1
    # Table 1B. T_op = platen_coolant_temp_c + theta_steady_state_delta_T_k. 팩이 pad_dma_id를
    # 선언하지 않으면(현재 5팩 전부 미선언) 조용히 None — 패드 ID를 지어내지 않는다.
    # Kp_eff(T) 훅은 넣지 않는다(모듈 docstring: 실측 대조 전까지 OFF).
    pad_modulus_at_temp_mpa: Optional[float] = None
    pad_modulus_ref_25c_mpa: Optional[float] = None
    pad_modulus_softening_ratio: Optional[float] = None
    pad_viscoelastic_note: Optional[str] = None
    # 디스크 설계 스펙(그릿 개수 N·그릿 크기 D) 변경의 GW 파라미터(Ra, Rpk, λ) 상대 배율
    # 진단 — MRR과 무관. sim/tier2_physics/disk_gw_relative_scaling.py::ra_relative/
    # rpk_relative/lambda_relative(원본 무수정). Kwon 2013(doi:10.1016/j.triboint.2013.08.008)
    # Ra∝N^-0.23·Rpk∝N^-0.62, Sun 2009(hdl:10150/194898) λ∝D^0.35(고하중 작업가설 중간값,
    # 저하중 λ_rel=1). disk_gw_ref_grit_count/size·disk_gw_target_grit_count/size 네 키가
    # 팩에 전부 선언될 때만 계산한다(현재 5팩 전부 미선언이라 항상 None이 정상 — "기준
    # 디스크"를 지어내지 않는다). disk_gw_high_load 미선언이면 λ_relative는 하중 레짐을
    # 임의로 고르지 않고 None으로 두며, note에 고하중/저하중 두 값만 병기한다.
    disk_gw_ra_relative: Optional[float] = None
    disk_gw_rpk_relative: Optional[float] = None
    disk_gw_lambda_relative: Optional[float] = None
    disk_gw_scaling_note: Optional[str] = None
    # 단일 연마입자 소성 접촉(plowing) 진단 — MRR과 무관, 진단 전용. sim/tier2_physics/
    # particle_chemomechanical_synergy.py::plastic_plowing(원본 무수정). F=P_nominal/η
    # (η=active_particle_density_per_m2, confidence=estimated), R=abrasive_size_nm/2,
    # H=film_bulk_hardness_pa. film_bulk_hardness_pa 미선언(현재 sti_ceria)이면 조용히
    # None. chemomechanical_amplification()(H_soft 필요, 팩에 없음)은 호출하지 않는다.
    particle_load_n: Optional[float] = None
    particle_indent_depth_nm: Optional[float] = None
    particle_plow_area_nm2: Optional[float] = None
    particle_contact_note: Optional[str] = None
    # 레시피 전이 work function 진단 — MRR과 무관, 진단 전용. sim/tier2_physics/
    # recipe_conversion_factor.py::work_function/RECIPE_TABLE(원본 무수정), US20060116785A1
    # 식(1)·표 1·표 2. F(X,Y,Z) = f(다운포스 rr.pressure_psi, 슬러리유량 sfr_ml_min, 플래튼
    # rpm rr.rpm_platen)는 런 하나만으로 계산 가능 — 모듈 docstring이 "미등록"이라 선언한
    # 것은 "레시피 간 전이"(두 레시피 비교) 개념이 Recipe 스키마에 없다는 뜻이지, 현재 런의
    # F(X,Y,Z) 자체를 못 낸다는 뜻이 아니다. sfr_ml_min이 팩에 없으면(현재 5팩 전부 base.yaml
    # 상속으로 있음) 조용히 None. 특허 표 1(ILD/STI/IMD)의 X/Y/Z 범위를 벗어나면 clamp하지
    # 않고 note에 외삽 경고만 붙인다.
    recipe_work_function: Optional[float] = None
    recipe_wf_vs_ild_ref: Optional[float] = None
    recipe_conversion_note: Optional[str] = None
    # Cu dishing에 의한 선저항 증가율 진단 — MRR과 무관, 진단 전용. sim/tier2_physics/
    # electrical_thickness_extraction.py::dishing_delta_R_fraction(원본 무수정), Chang,
    # Cao, Spanos, IEEE TED 51(10) 1577-1583 (2004), doi.org/10.1109/TED.2004.834898 표I·
    # Fig.6. film=="cu"(데이터 필드 판별, 판정#34) + linewidth_um(meta,
    # _cu_dishing_erosion_tugbawa_diagnostic과 동일 스키마) + remaining_nm(initial_thickness_nm
    # 설정 시에만 존재) 전부 있어야 값을 낸다 — 현재 5팩 기본 실행은 linewidth_um을 선언하지
    # 않아 항상 None이 정상이다. R_dish_um=40.0은 이 공정의 실측이 아니라 Chang et al. 2004
    # 문헌 테스트구조 최소제곱 추출값(note에 항상 경고). cu_thickness_from_resistance·liner_*
    # (실측 R·라이너 두께 필요)는 호출하지 않는다.
    electrical_dishing_delta_r_pct: Optional[float] = None
    electrical_dishing_r_dish_um: Optional[float] = None
    electrical_resistance_note: Optional[str] = None
    # Archard↔Preston 가교 진단 — MRR과 무관, 순수 가시화. sim/tier2_physics/
    # tribology_basics.py::archard_wear_depth 원본 docstring이 스스로 적어둔 대응
    # (Preston dot h = Kp·P·V 와 구조 동일 — Kp≈k/H)을 실행해, 기존 Kp를 무차원
    # Archard 마모계수 k = Kp·H로 환산하고 knowledge/physics/tribology-friction-wear-
    # stribeck.md §"Archard 오더 대조"의 연강 pin-on-disk 앵커(k=1e-3)와 오더 대조한다.
    # ⚠ 오더가 겹친다는 것은 sanity check일 뿐 "CMP가 순수 Archard 연마마모"를 뜻하지
    # 않는다 — CMP는 화학적 연화가 개입한 화학기계 복합과정이고, 1e-3 앵커는 연강
    # pin-on-disk 예시값이지 CMP 재료계 실측이 아니다. 이 진단으로 어떤 팩터의
    # confidence도 올리지 않는다. film_bulk_hardness_pa가 팩에 없으면 조용히 None.
    archard_wear_coefficient: Optional[float] = None
    archard_reference_k: Optional[float] = None
    archard_order_ratio: Optional[float] = None
    # Hersey 수(η·V/P, 관례상 차원 모호 — 모듈 docstring 자백) — slurry_viscosity_pa_s가
    # 있는 팩에서만 오더 확인용으로 낸다. cmp_sommerfeld_number(_lubrication_diagnostics,
    # 무차원 So=η·V/(P·δeff))와는 δeff 항 유무로 값이 다르다 — 중복 계산이 아니다.
    tribology_hersey_number: Optional[float] = None
    tribology_note: Optional[str] = None
    # 세리아 Ce3+ 산소공공 x·정전인력 진단 — MRR과 무관, 진단 전용. sim/tier2_physics/
    # ceria_redox_selectivity.py::ce3_fraction/electrostatic_attraction(원본 무수정).
    # x=f/2는 ce3_fraction이 이 팩 **고유선언**(has_own)일 때만 계산한다 —
    # sic_ceria_h2o2(base: sti_ceria)가 has()였다면 STI 실측 Ce3+분율을 조용히
    # 상속받았을 것(04dc440 κ 농도항 상속 판정#48과 같은 하이진 결함 유형). 정전인력은
    # iep_ceria=abrasive_iep_ph, iep_silica=wafer_iep_ph(둘 다 has_own), pH=slurry_ph를
    # electrostatic_attraction에 그대로 넣는다 — iep_silica는 지어낸 상수가 아니라
    # sti_ceria가 이미 이 노트 §4를 출처로 고유선언한 필드를 재사용한 것
    # (sim/factors.py::_ph_ceria_window_term의 iep_wafer와 동일 관례). abrasive_iep_ph
    # 단독 선언 여부로는 세리아 계를 판별할 수 없다(oxide_silica도 실리카 자신의
    # abrasive_iep_ph=2.5를 선언) — 세 키(ce3_fraction·abrasive_iep_ph·wafer_iep_ph)
    # 모두 has_own을 요구해 현재 5팩 중 sti_ceria 하나에만 걸리게 한다(판정#34: 팩
    # 이름 하드코딩 금지, 데이터로 판별). oxide_nitride_selectivity·
    # h2o2_boost_selectivity(실측 nitride MRR·미검증 boost_factor 필요)·
    # is_chemisorption/chemisorption_energy_kj_mol(DFT 흡착에너지 필요)은 호출하지
    # 않는다 — 어느 팩도 그 입력을 갖고 있지 않다.
    ceria_oxygen_vacancy_x: Optional[float] = None
    ceria_electrostatic_attraction: Optional[int] = None
    ceria_redox_note: Optional[str] = None
    # 패드 공정 하중주파수 역진단(Maxwell 점탄성, S12) — MRR과 완전히 독립, 진단 전용.
    # sim/tier2_physics/viscoelastic_maxwell.py 엔진 등록. ω_asperity/De_asperity는 GW
    # 패드 파라미터+asperity_height_distribution=exponential일 때 산출된다(2026-09-16
    # 정정, _pad_loading_frequency_diagnostic 독스트링 참조).
    pad_loading_omega_rot_rad_s: Optional[float] = None
    pad_loading_omega_asperity_rad_s: Optional[float] = None
    pad_relaxation_time_threshold_s: Dict[str, Optional[float]] = field(
        default_factory=lambda: {"rot": None, "asperity": None})
    pad_deborah_number: Dict[str, Optional[Dict[str, float]]] = field(
        default_factory=lambda: {"rot": None, "asperity": None})
    pad_loading_frequency_note: Optional[str] = None
    # 산화물/연마입자 표면전하 부호(IEP 기준) 진단 — MRR과 무관, 진단 전용. sim/tier2_physics/
    # chelation_surface_charge.py::oxide_surface_charge_sign(원본 무수정) 엔진 등록.
    # slurry_ph·abrasive가 5팩 전부에 있어 부호는 항상 나온다(문헌 IEP표에 없는
    # 연마입자면 None). abrasive_iep_pack_deviation_ph는 팩이 abrasive_iep_ph를
    # 선언했을 때만(cu_h2o2_bta·w_fe_oxidizer는 미선언이라 None).
    abrasive_surface_charge_sign: Optional[str] = None
    abrasive_iep_literature_ph: Optional[float] = None
    abrasive_iep_pack_deviation_ph: Optional[float] = None
    abrasive_surface_charge_note: Optional[str] = None
    # 디스크 접촉통계(η_c, A_f) -> Preston Kp 상대 진단 — MRR과 무관, 진단 전용. sim/tier2_physics/
    # disk_preston_contact_decomposition.py::eta_over_af(원본 무수정) 엔진 등록. η_c·A_f는
    # _gw_contact_state_diagnostic과 동일 GW 런타임 해(local_contact_state)에서 구한다(새 상수
    # 없음). K_p ∝ η_c/A_f는 모듈 스스로 자백한 PROVISIONAL 선형가정이라 절대 스케일하지
    # 않는다(preston_coefficient_contact_scaling·disk_preston_contact_scaling 미호출).
    # disk_contact_scale_factor는 5팩 어디에도 기준 디스크 스펙이 없어 항상 None.
    disk_contact_eta_c_m2: Optional[float] = None
    disk_contact_a_f: Optional[float] = None
    disk_contact_eta_over_af: Optional[float] = None
    disk_contact_scale_factor: Optional[float] = None
    disk_preston_contact_note: Optional[str] = None
    # 블랭킷 Cu 순간 포화속도 a1 대비 평균 rate r_avg(t) 과소평가 진단 — MRR과 무관,
    # 진단 전용. sim/tier2_physics/blanket_rate_transfer.py::blanket_rate_average(원본
    # 무수정, eq.3.52) 엔진 등록. 표 3.3(Tugbawa 2002) 4실험 값만 쓰고 대표값(평균)은
    # 내지 않는다(min~max 범위). film != "cu"거나 time_s<=0이면 조용히 None.
    blanket_transient_avg_to_inst_ratio_range: Optional[tuple] = None
    blanket_transient_underestimate_pct_range: Optional[tuple] = None
    blanket_transient_note: Optional[str] = None
    # 컨디셔너 디스크 장비팩 로드 여부 — MRR과 완전히 무관, 스키마 신설 회차(백로그 ㉺)라
    # 물리값은 절대 산출하지 않는다. sim/equipment.py::load_equipment_pack()이 실제로
    # 읽었는지와 그 요약만 보고한다. Recipe.conditioner_disk가 None이면 둘 다 None.
    conditioner_disk_pack: Optional[str] = None
    conditioner_disk_note: Optional[str] = None
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
        out: Dict = {
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
        # 진단 필드 자동 노출 — 손으로 유지하던 목록이 실제로 뒤처져 있었다.
        # 2026-09-16 실측: WaferResult 필드 125개 중 summary()가 내보내던 것은 37개뿐이라
        # 그간 등록된 진단 88개(gw_pressure_solve·tribology_basics·slurry_components·
        # blanket_rate_transfer 등)가 CLI(--json)·API 응답에서 통째로 보이지 않았다.
        # 등록만 하고 사용자에게 도달하지 않으면 등록이 아니다.
        # 제외 대상은 요약에 담을 수 없는 것뿐이다(_SUMMARY_EXCLUDE): 배열 프로파일은
        # CLI --profile / API가 별도 경로로 내보내고, metrics·factors·equipment_outputs·
        # notes는 위에서 이미 가공해 실었으며, provenance는 API가 직접 싣는다.
        # 그 외 스칼라·문자열·튜플·dict 진단은 전부 자동으로 나간다.
        for _f in _fields(self):
            if _f.name in _SUMMARY_EXCLUDE or _f.name in out:
                continue
            out[_f.name] = getattr(self, _f.name)
        return out


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


class PatternDensityEffectivePressureModel:
    """Tier1 선택형(opt-in): PTW 패턴밀도별 유효압력비를 Preston MRR에 곱한다.

    근거: Sorooshian(2005) §3.3 실측표(sim/tier2_physics/npw_ptw_effective_pressure.py) —
    패턴 웨이퍼의 융기(up) 피처에 실제로 걸리는 접촉압력 P_eff/P_applied을 밀도별로
    실측했다. Preston: MRR = Kp·P·V. Kp는 blanket NPW에서 역산되므로
    up-area 제거율 = Kp·P_eff·V = ratio × blanket Preston MRR — 이중계상이 아니다.

    사용자가 이 모델을 **명시적으로** 선택했을 때만 돈다. 조건 미달(NPW·density
    미지정/표 밖·pressure 표 밖)이면 조용한 blanket 폴백 없이 ValueError로 크게
    실패한다 — 조용히 넘어가면 "패턴 효과를 넣었다"는 거짓말이 되기 때문이다.
    """
    name = "tier1.pattern_density_effective_pressure"
    _TEMP_C = 23.0   # 표의 상온 행 고정 — notes()가 이 근거 없음을 항상 명시한다

    def mrr_radial(self, recipe: "ResolvedRecipe", radius_m: np.ndarray) -> np.ndarray:
        if recipe.wafer != "PTW":
            raise ValueError(
                f"{self.name}은 PTW 전용이다 — wafer={recipe.wafer!r}에는 적용할 수 없다 "
                "(NPW는 blanket이라 패턴밀도 유효압력 개념이 없다)")
        density = _meta_pattern_density(recipe)
        if density is None or density not in (0.10, 0.50, 0.90):
            raise ValueError(
                f"{self.name}은 recipe.meta['pattern_density']가 {{0.10, 0.50, 0.90}} 중 "
                f"정확히 하나여야 한다 — 받은 값: {density!r} (조용한 보간·외삽 없음)")
        if recipe.pressure_psi not in (3, 7):
            raise ValueError(
                f"{self.name}은 pressure_psi가 {{3, 7}} 중 하나여야 한다 — "
                f"받은 값: {recipe.pressure_psi!r} (표에 3·7psi만 있고 그 사이 보간 근거가 "
                "문헌에 없다)")
        import npw_ptw_effective_pressure as EPR   # sim/tier2_physics (1바이트도 수정 안 함)
        ratio = EPR.table_ratio(density, recipe.pressure_psi, self._TEMP_C)
        return ratio * PrestonRadialModel().mrr_radial(recipe, radius_m)

    def notes(self, recipe: "ResolvedRecipe") -> List[str]:
        return [
            f"{self.name}: 표 온도 23℃ 고정 — 실제 패드표면 온도를 표 온도"
            "(10/23/35/45)에 매핑할 근거가 없다 (Sorooshian 2005 §3.3).",
            "이 값은 융기(up) 피처의 step-height 국면 제거율이지 다이 평균 제거율도, "
            "평탄화 완료 후 제거율도 아니다 — 시간에 따라 ratio가 1로 수렴하는 과정은 "
            "미모델링.",
            "ratio는 3점(0.10/0.50/0.90) 실측 조회값이다 — 그 사이 밀도는 지원하지 않는다.",
            "비교 대상인 Boning 1/ρ 모델(10/2/1.11배)은 저밀도에서 실측을 4배 이상 "
            "과대예측한다 — 이 모델은 그쪽을 쓰지 않는다.",
        ]


_MODELS: Dict[str, Model] = {}


def register(model: Model) -> None:
    _MODELS[model.name] = model


register(PrestonRadialModel())
register(PatternDensityEffectivePressureModel())

# PTW 패턴 효과를 MRR 경로에 반영하는 모델들. simulate()가 "패턴 모델을 안 썼다" 경고를
# 띄울지 판단하는 데만 쓴다. 판정#65(EVIDENCE-RULES): 둘 다 등록돼 있으나 근거 등급은
# 같지 않다 — 기본 권장은 실측표 기반 effective_pressure 쪽이다.
_PATTERN_MODELS = frozenset({
    "tier1.pattern_density",                      # Boning 1/ρ (sim/models.py, 폐형식 가정)
    "tier1.pattern_density_effective_pressure",   # Sorooshian 2005 §3.3 실측표
})


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
        # ⚠ 전이 파라미터를 팩에서 읽는다. 이전에는 CLR.cof_stribeck(so) 로만 호출해
        # base.yaml 의 cof_boundary·cof_hydro_coeff·cof_transition_alpha 3개 키가
        # 완전한 dead code 였다(모듈 기본값 0.30/8.0/40.0 이 우연히 같은 값이라
        # 증상이 보이지 않았음 — cof_boundary 를 3배로 흔들어도 출력 비트 불변이었다).
        kw = {}
        if rr.pack.has("cof_boundary"):
            kw["mu_bl"] = float(rr.p("cof_boundary"))
        if rr.pack.has("cof_hydro_coeff"):
            kw["c_hydro"] = float(rr.p("cof_hydro_coeff"))
        if rr.pack.has("cof_transition_alpha"):
            kw["alpha_tr"] = float(rr.p("cof_transition_alpha"))
        cof_est = CLR.cof_stribeck(so, **kw)
        out["lubrication_regime"] = CLR.regime_from_lambda(lam)
        out["cmp_sommerfeld_number"] = so
        out["cof_stribeck_estimate"] = cof_est

        # μ 일관성 진단: Q_f(Θ 열수지)가 쓰는 μ 와 이 추정치를 같은 문서에서 대조한다.
        if "mu_bl" in kw:
            mu_qf = kw["mu_bl"]
            out["cof_qf_used"] = mu_qf
            out["cof_estimate_vs_qf_ratio"] = cof_est / mu_qf if mu_qf else None
            out["cof_consistency_note"] = (
                f"Q_f(Θ 열수지)는 μ={mu_qf:.4g}(cof_boundary, confidence=literature)를 쓰고, "
                f"Stribeck 추정치는 {cof_est:.4g} (비 {cof_est / mu_qf:.4f}). "
                "⚠ 이 둘은 독립 추정이 아니다 — cof_stribeck(So)는 mu_bl=cof_boundary 를 "
                "입력으로 받아 전이항 f=exp(-alpha_tr·So)로 깎은 값이므로, 차이 전부가 "
                "alpha_tr·c_hydro(둘 다 confidence=estimated, 노트 §6이 '임의·정성 재현'이라 "
                "명시)에서 나온다. 따라서 Q_f에는 문헌등급인 cof_boundary 를 그대로 쓰고 "
                "이 추정치를 대입하지 않는다(EVIDENCE-RULES: literature > estimated). "
                "Q_f∝μ 이므로 μ 오차는 ΔT_ss에 선형 전파되고, Ea가 큰 막(Cu 151.7 kJ/mol)에서는 "
                "thermal_chemical_rate_ratio 를 수십 % 이상 흔든다 — 절대값을 신뢰하지 말 것.")
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


def _meta_pattern_density(rr: "ResolvedRecipe") -> Optional[float]:
    """meta['pattern_density']를 float로 읽는다. 없으면 None.

    Recipe.meta 는 `Dict[str, str]` 로 선언돼 있고, 실제 생산자 3곳
    (`sim/cli.py`·`sim/studio.py`·`sim/calibration/fit_ptw.py`)이 전부 `str(...)`로
    넣는다 — 즉 문자열이 규약이고, 캐스팅하지 않는 소비자 쪽이 결함이다.
    `_cu_dishing_erosion_tugbawa_diagnostic`은 이미 `float(meta[...])`로 읽고 있었다.

    2026-09-19(판정#65 후속): 이 캐스팅이 없어서 CLI·Studio에서 밀도를 0.5로 줘도
    `'0.5' != 0.50`이라 유효압력 진단이 조용히 스킵되고 있었다. 더 나쁜 것은 그때
    붙던 사유 문구가 "0.5는 표에 없는 값(지원: 0.10/0.50/0.90)"이라 **지원 목록에
    있는 값을 없다고 말하는** 거짓 안내였다는 점이다.

    숫자로 해석되지 않으면 지어내지 않고 None(호출자가 스킵 사유를 남긴다).
    """
    raw = rr.meta.get("pattern_density")
    if raw is None:
        return None
    try:
        return float(raw)
    except (TypeError, ValueError):
        return None


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
    density = _meta_pattern_density(rr)
    if density is None:
        if rr.meta.get("pattern_density") is not None:
            out["_note"] = (f"pattern_density={rr.meta.get('pattern_density')!r}를 숫자로 "
                            "읽을 수 없다 — 유효압력 진단 스킵")
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
        # ⚠ 단위 정정(2026-09-16, Max워커): 팩 키 `pad_height_beta_inv_m`는 지수분포의
        # **스케일 1/β [m]**(=2.0e-6 m)이고, gw_contact.exp_pdf(z,beta)=β·exp(-βz)가 받는
        # 인자는 **감쇠율 β [1/m]**다. 역수를 취하지 않고 그대로 넘기면 β가 5e5 배 작아져
        # 분리거리 d가 21.6 km(!)로 풀린다. base.yaml `real_contact_area_ratio` note가
        # 기록한 GW 해(d=7.62 µm, 실접촉비 1.393e-3, 접촉자리 4.434e6 /m²)는 β=1/(2.0e-6)
        # 로 풀어야 재현된다 — 아래 역수 변환이 그 재현을 보장한다.
        pad = dict(E_star=rr.p("pad_E_star_pa"), R=rr.p("pad_asperity_radius_m"),
                   beta=1.0 / rr.p("pad_height_beta_inv_m"),
                   eta=rr.p("pad_asperity_density_m2"),
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


def _gw_contact_state_diagnostic(rr: "ResolvedRecipe") -> Dict[str, object]:
    """GW 역문제(명목압력→분리거리) 런타임 해 진단 — MRR 경로와 완전히 독립적인 진단 계산.

    근거: sim/tier2_physics/gw_pressure_solve.py::local_contact_state(gw_numeric 재사용),
    gw_contact.py::plasticity_index/gw_analytic_ratio. base.yaml의 real_contact_area_ratio
    (confidence=estimated) note가 "압력에 따라 변하는 값이므로 3 psi 부근에서만 유효하다.
    압력 의존성을 정식으로 넣으려면 GW를 런타임에 풀어야 한다"고 자백한 것을 실행한다.
    GW 5개 패드 파라미터(_gw_contact_linearity_diagnostic과 동일 키)가 팩에 없으면
    조용히 None. 압력은 zone별 루프 없이 rr.pressure_psi(center) 1점만 쓴다(범위 밖).
    """
    out: Dict[str, object] = {
        "gw_solved_separation_m": None,
        "gw_real_contact_area_ratio": None,
        "gw_real_contact_pressure_pa": None,
        "gw_static_pack_ratio_deviation": None,
        "gw_plasticity_index": None,
        "gw_contact_regime_note": None,
    }
    pad_keys = ("pad_E_star_pa", "pad_asperity_radius_m", "pad_height_beta_inv_m",
                "pad_asperity_density_m2", "pad_nominal_area_m2")
    missing = [k for k in pad_keys if not rr.pack.has(k)]
    if missing:
        out["gw_contact_regime_note"] = (
            f"GW 패드 파라미터 미선언({', '.join(missing)}) — 접촉상태 진단 스킵")
        return out
    try:
        import gw_pressure_solve as GWP   # sim/tier2_physics (1바이트도 수정 안 함)
        import gw_contact as GWC          # sim/tier2_physics (1바이트도 수정 안 함)
        E_star = rr.p("pad_E_star_pa")
        R = rr.p("pad_asperity_radius_m")
        # ⚠ 단위: 팩 키는 스케일 1/β [m], 모듈이 받는 인자는 감쇠율 β [1/m]. 역수 변환 필수
        # (미변환 시 d가 21.6 km로 풀린다 — _gw_contact_linearity_diagnostic 주석 참조).
        sigma_z = rr.p("pad_height_beta_inv_m")   # 지수분포: 표준편차 = 스케일 = 1/β [m]
        beta = 1.0 / sigma_z                       # 감쇠율 β [1/m]
        eta = rr.p("pad_asperity_density_m2")
        A_n = rr.p("pad_nominal_area_m2")
        P_center = rr.pressure_psi * PSI_TO_PA
        state = GWP.local_contact_state(P_center, A_n, beta, eta, E_star, R)
    except Exception as e:
        out["gw_contact_regime_note"] = f"GW 접촉상태 진단 실패({e}) — None으로 둠"
        return out

    out["gw_solved_separation_m"] = float(state["d"])
    out["gw_real_contact_area_ratio"] = float(state["contact_area_fraction"])
    out["gw_real_contact_pressure_pa"] = float(state["p_r_mean"])

    notes = [
        f"압력은 zone별 루프 없이 center 1점(rr.pressure_psi={rr.pressure_psi} psi)만 사용 "
        "— zone별 GW 해는 범위 밖"]

    try:
        analytic_ratio = GWC.gw_analytic_ratio(beta, E_star, R)   # A_r/W (d-무관 폐형식)
        if state["W"] > 0:
            numeric_ratio = state["A_r"] / state["W"]
            rel_dev = abs(numeric_ratio - analytic_ratio) / analytic_ratio
            if rel_dev > 0.01:
                notes.append(
                    f"⚠ 해석적 폐형식(gw_analytic_ratio) A_r/W 대비 수치해 상대편차 "
                    f"{rel_dev * 100:.2f}% > 1%")
    except Exception as e:
        notes.append(f"해석적 폐형식 교차검증 실패({e})")

    if rr.pack.has("real_contact_area_ratio"):
        static_ratio = float(rr.p("real_contact_area_ratio"))
        if static_ratio > 0:
            out["gw_static_pack_ratio_deviation"] = out["gw_real_contact_area_ratio"] / static_ratio
            notes.append(
                f"런타임 해 {out['gw_real_contact_area_ratio']:.4e} vs 정적 팩값 "
                f"real_contact_area_ratio={static_ratio:.4e}"
                f"(confidence={rr.pack.param('real_contact_area_ratio').confidence}) "
                f"— 배율 {out['gw_static_pack_ratio_deviation']:.3f}배")
    else:
        notes.append("팩이 real_contact_area_ratio 미선언 — 정적값 대비 괴리 계산 스킵")

    H = float(rr.p("pad_asperity_hardness_max_pa")) if rr.pack.has("pad_asperity_hardness_max_pa") else None
    dist = rr.p("asperity_height_distribution") if rr.pack.has("asperity_height_distribution") else None
    if H is None:
        notes.append("pad_asperity_hardness_max_pa 미선언 — 소성지수 계산 스킵")
    elif dist != "exponential":
        notes.append(
            f"asperity_height_distribution={dist!r}(exponential 아님) — sigma_z 지어내지 않고 "
            "소성지수 계산 스킵")
    else:
        # sigma_z는 위에서 pad_height_beta_inv_m(스케일=표준편차)로 이미 잡았다 — beta(감쇠율)를
        # 넣으면 안 된다(두 값은 서로 역수, 여기서 혼동하면 psi가 5e5 배 어긋난다).
        try:
            psi = float(GWC.plasticity_index(E_star, H, sigma_z, R))
            out["gw_plasticity_index"] = psi
            regime = "탄성(psi<0.6)" if psi < 0.6 else ("소성(psi>1)" if psi > 1 else "전이영역(0.6~1)")
            notes.append(
                f"소성지수 psi={psi:.4f} → {regime} [미검증 판정기준: Johnson Contact Mechanics "
                "1985 Ch.13 통상기준, gw_contact.py 독스트링이 2차 출처 교차검증 필요·미검증이라 "
                "표기]. H=pad_asperity_hardness_max_pa(단일 패드 1종 측정, 다른 패드로의 이식은 추정)")
        except Exception as e:
            notes.append(f"소성지수 계산 실패({e})")

    out["gw_contact_regime_note"] = " | ".join(notes)
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


def _pad_groove_wear_flow_diagnostic(rr: "ResolvedRecipe") -> Dict[str, object]:
    """그루브 마모 → 슬러리 유동 상태 진단 — MRR 경로와 완전히 독립.

    근거: sim/tier2_physics/pad_groove_wear_flow.py(원본 1바이트도 수정 안 함,
    self-test PASS), knowledge/materials/pad-groove-wear-flow-change-end-of-life.md
    §2·§4·§5. 인용 문헌은 그 모듈 docstring 그대로(US8192257B2, US11938584B2,
    Mu 2016 doi:10.1016/j.mee.2016.02.035, Irfan 2025 doi:10.3390/jmmp9030095).

    입력 관례는 `_pad_groove_eol_diagnostic`과 **완전히 동일**하다 — 같은 문서 안에서
    두 진단이 다른 D0·다른 시간축을 쓰면 숫자가 서로 모순되기 때문이다:
      D0 = pack.groove_depth_mm * 1000 [μm] (base.yaml 0.76mm, literature)
      t  = meta.pad_hours [h] (컨디셔닝 시간 = 연마 시간 가정)
      c  = pack.pad_cut_rate_um_per_h [μm/h] — 팩 미선언이면 스킵(하드코딩 거부,
           풀컨택트 43.4 vs 분할 22.2 중 어느 쪽인지 팩이 정하지 않았다).
           현재 5팩 전부 미선언이라 항상 None이 정상이다.

    그루브 **절대 폭** w는 팩의 `groove_width_um`(600 μm = 0.6 mm, Mu 2016 패드 B,
    confidence=literature)을 쓴다. 모듈 기본값 0.5 mm(Irfan 2025 §2.3 기하)는
    **쓰지 않는다** — 우리 팩이 자기 이름으로 폭을 선언하고 있으므로 그쪽이 우선이다
    (판정#34의 has_own 우선 원칙과 같은 취지). 어느 값을 썼는지 note에 항상 밝힌다.

    ⛔ **호출하지 않는 함수 4개**(입력이 Recipe/팩 어디에도 없어 지어내야 하기 때문):
      - residence_time_s / slurry_volumes_cm3 / groove_wear_flow_state
        → h_land_um(land 위 슬러리 필름 두께)·q_actual_cm3_per_s(실유량)가 없다.
      - micron_cabot_life_wafers → 입력이 **wafer당** 마모량인데 우리는 **시간당**
        (μm/h)만 갖고 있고, 시간→wafer 환산(웨이퍼/시간)이 어느 팩에도 없다.
    이 경계는 tests/test_pad_groove_wear_flow_diagnostic.py가 ast로 기계 고정한다.

    ⚠ `wear_stage`의 임계값 0.7/0.35는 **PROVISIONAL**이다 — 모듈 docstring이 스스로
    "노트 §4의 모델 제안이며 Liu/Irfan 0.29~0.33, Cabot 0.20, Micron 0.2~0.4 범위 안에서
    이 에이전트가 고른 값"이라고 밝힌다. 단계 라벨을 공정 판정 근거로 쓰면 안 된다.

    ⚠ D가 0으로 clamp되는 구간(EOL 초과)에서는 컨덕턴스가 정의되지 않으므로(급수해가
    h=0에서 발산) 0.0으로 내고 note에 경고를 명시한다 — 조용한 clamp 금지.
    """
    out: Dict[str, object] = {"pad_groove_residual_fraction": None,
                              "pad_groove_wear_stage": None,
                              "pad_groove_conductance_ratio": None,
                              "pad_groove_flow_note": None}
    if not rr.pack.has("pad_cut_rate_um_per_h"):
        out["pad_groove_flow_note"] = (
            "pad_cut_rate_um_per_h 미선언 — 43.4(풀컨택트)/22.2(분할) 중 어느 "
            "컨디셔닝 방식인지 팩이 정하지 않아 그루브 유동 진단 스킵 "
            "(pad_groove_eol 진단과 동일 사유)")
        return out
    if not rr.pack.has("groove_depth_mm"):
        out["pad_groove_flow_note"] = (
            "groove_depth_mm 미선언 — 초기 그루브 깊이 D0를 지어낼 수 없어 스킵")
        return out
    if not rr.pack.has("groove_width_um"):
        out["pad_groove_flow_note"] = (
            "groove_width_um 미선언 — 컨덕턴스 계산에 필요한 그루브 절대 폭을 "
            "모듈 기본값 0.5mm로 대신 채우지 않고 스킵(지어내기 금지)")
        return out
    try:
        import pad_groove_wear_flow as PGWF   # sim/tier2_physics (1바이트도 수정 안 함)
        c = float(rr.p("pad_cut_rate_um_per_h"))
        hours = float(rr.meta.get("pad_hours", 0) or 0)
        d0_um = float(rr.pack.param("groove_depth_mm").value) * 1000.0  # mm -> um
        w_um = float(rr.pack.param("groove_width_um").value)
        w_mm = w_um / 1000.0
        d_um = PGWF.groove_depth_um(d0_um, c, hours)
        residual = PGWF.residual_depth_fraction(d_um, d0_um)
        stage = PGWF.wear_stage(d_um, d0_um)
        if d_um <= 0.0:
            cond_ratio = 0.0
            eol_warn = (
                "⚠ EOL 초과 — D(t)가 0으로 clamp됐다(누적 마모 "
                f"{c * hours:.1f} μm ≥ D0 {d0_um:g} μm). 컨덕턴스 급수해가 h=0에서 "
                "정의되지 않아 컨덕턴스비를 0.0으로 내보낸다(계산값이 아니라 경계값). ")
        else:
            cond_ratio = PGWF.conductance_ratio(d_um, d0_um, w_mm)
            eol_warn = ""
    except Exception as e:
        out["pad_groove_flow_note"] = f"그루브 마모-유동 진단 실패({e}) — None으로 둠"
        return out
    out["pad_groove_residual_fraction"] = float(residual)
    out["pad_groove_wear_stage"] = str(stage)
    out["pad_groove_conductance_ratio"] = float(cond_ratio)
    out["pad_groove_flow_note"] = (
        f"{eol_warn}"
        f"컨디셔닝 시간 = 연마 시간 가정(meta.pad_hours={hours:g}h, "
        "pad_groove_eol 진단과 동일 관례). "
        f"D0={d0_um:g} μm, c={c:g} μm/h → D(t)={d_um:.1f} μm, 잔존비={residual:.4f}. "
        f"컨덕턴스비 G(D)/G(D0)={cond_ratio:.4f} (직사각 덕트 Poiseuille 급수해, "
        f"h³ 의존이라 잔존비보다 급하게 떨어진다). "
        f"그루브 절대 폭은 팩 선언값 groove_width_um={w_um:g} μm(={w_mm:g}mm, "
        "Mu 2016 패드 B)을 썼다 — 모듈 기본값 0.5mm(Irfan 2025 §2.3 기하)는 쓰지 않는다. "
        f"단계='{stage}' ⚠PROVISIONAL: 임계 0.7/0.35는 모듈이 스스로 '노트 §4의 모델 "
        "제안(Liu/Irfan 0.29~0.33·Cabot 0.20·Micron 0.2~0.4 범위 중 선택)'이라 밝힌 값이다. "
        "⚠ 진단 전용 — MRR에 영향 없음. residence_time_s·slurry_volumes_cm3·"
        "groove_wear_flow_state(h_land_um·q_actual 부재)와 micron_cabot_life_wafers"
        "(시간→wafer 환산 부재)는 호출하지 않는다.")
    return out


def _inhibitor_saturation_diagnostic(rr: "ResolvedRecipe") -> Dict[str, object]:
    """억제제 Langmuir 피복률 포화도 진단 — MRR 경로와 완전히 독립(진단 전용).

    근거: sim/tier2_physics/slurry_components.py::langmuir_coverage/K_from_dG_ads
    (원본 1바이트도 수정 안 함), sim/inhibitor_pairs.py(쌍 표),
    knowledge/cmp/bta-inhibitor-langmuir-K-effective-cu-cmp-falsification.md
    §5·§6, EVIDENCE-RULES 판정#17.

    **이 진단이 답하는 질문**: "이 팩의 억제제 항이 농도 변화에 아직 반응하는가?"
    판정#17이 정량 반증한 고장 방식은 다음이었다 — K_eq(평형 흡착상수)를 정상상태
    θ에 그대로 대입하면 θ가 이미 0.996/0.998로 포화해 BTA 0.1 wt%와 0.25 wt%의
    모델 예측비가 0.9926(사실상 무변화)이 되고, 실측비 0.6462와 34.6pp 어긋난다.
    즉 **숫자는 나오지만 농도 축이 죽어 있는 상태**이고, MRR 출력만 봐서는 그게
    보이지 않는다. 이 진단은 그 상태를 기계가 읽을 수 있는 필드로 꺼낸다.

    산출:
      inhibitor_theta_equilibrium   : θ = KC/(1+KC), 팩 선언 농도에서의 피복률
      inhibitor_theta_headroom      : 1-θ (포화까지 남은 여유). 0에 가까우면 죽은 축
      inhibitor_conc_discrimination : θ(2C)/θ(C). 농도를 2배로 올렸을 때 피복률이
                                      몇 배 되는가. 1.000에 붙으면 **농도를 구분하지
                                      못한다**(판정#17이 반증한 바로 그 상태)
      inhibitor_saturation_note     : K 출처·경고

    **K 조회 경로는 `sim/chemistry.py::_inhibitor_term`과 글자 그대로 같은 우선순위**를
    따른다(쌍 표 → 팩 ΔG → 팩 K). 두 곳이 다른 K를 쓰면 같은 문서 안에서 θ가 모순되므로
    순서를 복제하되, **chemistry.py는 1바이트도 고치지 않는다**.

    ⚠ MRR에 곱하지 않는다 — `_inhibitor_term`이 이미 같은 θ를 소비해 ψ 배수를 만들고
    있다. 여기서 다시 곱하면 이중계상이다(판정#15 `conditioner_pcr_decay` 선례와 동일
    구조). 이 진단은 **가시화**일 뿐이다.

    ⚠ θ의 절대값을 신뢰하지 마라. cu_h2o2_bta의 K는 평형 ΔG에서 나온 K_eq이고,
    판정#17이 "이 경로(정상상태 θ)에 K_eq를 직접 쓰는 것"을 반증했다. 역산된 K_eff
    후보(183·249.7 L/mol)는 계가 다른(알칼리+알루미나) 데이터에서 나와 이 산성 팩에
    **채택하지 않았다** — 그래서 여기서도 K_eff를 임의로 대입하지 않는다. 이 진단이
    내는 것은 "현행 파라미터가 만드는 θ가 얼마나 포화됐나"라는 **현행 모델의 자기
    진단**이지, 참값 주장이 아니다.

    억제제 파라미터가 없는 팩(현재 oxide_silica·sic_ceria_h2o2·sti_ceria)은
    조용히 None + 스킵사유 — 산화막 계엔 금속 부식억제제가 없는 것이 정상이다.
    """
    out: Dict[str, object] = {"inhibitor_theta_equilibrium": None,
                              "inhibitor_theta_headroom": None,
                              "inhibitor_conc_discrimination": None,
                              "inhibitor_saturation_note": None}
    if not rr.pack.has("inhibitor_mM"):
        out["inhibitor_saturation_note"] = (
            f"inhibitor_mM 팩 '{rr.pack.name}'에 없음 — 억제제 포화도 진단 스킵 "
            "(산화막 계엔 금속 부식억제제가 없는 것이 정상)")
        return out
    try:
        import slurry_components as SC   # sim/tier2_physics (1바이트도 수정 안 함)
        from sim.inhibitor_pairs import lookup_dG, K_from_dG

        C_molar = float(rr.p("inhibitor_mM")) * 1e-3
        # K 조회 우선순위를 sim/chemistry.py::_inhibitor_term과 동일하게 복제한다.
        K = None
        k_src = None
        inhib = rr.pack.get_or("inhibitor_species", None)
        subst = rr.pack.get_or("substrate_species", None)
        if inhib and subst:
            pair = lookup_dG(str(inhib), str(subst))
            if pair is not None:
                K = K_from_dG(pair.dG_kJ_per_mol)
                k_src = (f"쌍 표({inhib}×{subst}) ΔG={pair.dG_kJ_per_mol:.2f} kJ/mol "
                         f"[{pair.confidence}]")
        if K is None and rr.pack.has("inhibitor_dG_ads_kJ"):
            K = SC.K_from_dG_ads(float(rr.p("inhibitor_dG_ads_kJ")) * 1000.0)
            k_src = "팩 inhibitor_dG_ads_kJ (단일 ΔG 폴백 — 쌍 검증 안 됨)"
        if K is None and rr.pack.has("inhibitor_K_L_per_mol"):
            K = float(rr.p("inhibitor_K_L_per_mol"))
            k_src = "팩 inhibitor_K_L_per_mol (직접 선언)"
        if K is None:
            out["inhibitor_saturation_note"] = (
                "inhibitor_mM은 있으나 흡착상수(쌍 표·ΔG·K 전부 부재) — θ를 지어낼 수 "
                "없어 스킵(_inhibitor_term도 같은 조건에서 항을 건너뛴다)")
            return out
        theta = SC.langmuir_coverage(C_molar, K)
        theta_2c = SC.langmuir_coverage(2.0 * C_molar, K)
        if theta <= 0.0:
            out["inhibitor_saturation_note"] = (
                f"θ={theta:g} — 0 이하라 농도 판별비를 정의할 수 없어 스킵")
            return out
        discrimination = theta_2c / theta
    except Exception as e:
        out["inhibitor_saturation_note"] = f"억제제 포화도 진단 실패({e}) — None으로 둠"
        return out
    out["inhibitor_theta_equilibrium"] = float(theta)
    out["inhibitor_theta_headroom"] = float(1.0 - theta)
    out["inhibitor_conc_discrimination"] = float(discrimination)
    # 판정#17이 반증한 상태(θ 포화로 농도축 사망)를 정량 경고로 꺼낸다.
    if discrimination < 1.01:
        verdict = (
            f"🔴 농도축 포화 — 농도를 2배로 올려도 θ가 {discrimination:.4f}배밖에 "
            "안 변한다(<1.01). 이 팩에서 억제제 농도를 스윕해도 MRR은 거의 안 움직인다. "
            "**민감도 0을 '억제제가 영향 없다'로 읽지 마라** — 아래 두 원인이 같은 신호를 "
            "내므로 팩마다 근거를 따로 확인해야 한다: (a) 실계가 실제로 그 농도에서 포화한다 "
            "(문헌이 플래토를 직접 실측한 경우 — 이건 모델이 맞는 것이다), (b) K가 잘못된 "
            "경로로 들어와 θ가 실제보다 일찍 포화한다(EVIDENCE-RULES 판정#17이 "
            "Len/McNeill/Gamble 2000 실측으로 cu 계에서 정량 반증한 고장: 모델 예측비 0.9926 "
            "vs 실측 0.6462, 34.6pp). **이 진단은 (a)와 (b)를 구분하지 못한다** — 신호만 낸다. ")
    elif discrimination < 1.10:
        verdict = (f"⚠ 농도축 둔감 — 2배 농도에서 θ가 {discrimination:.4f}배. "
                   "포화 근처라 억제제 스윕의 분해능이 낮다. ")
    else:
        verdict = (f"농도축 살아있음 — 2배 농도에서 θ가 {discrimination:.4f}배. ")
    # 팩별 근거 주석 — (a)/(b) 구분은 문헌이 있는 팩에 한해 여기서만 단다.
    # 지어내지 않는다: 아래 두 팩 외에는 원인 귀속을 하지 않는다.
    if str(rr.pack.name) == "w_fe_oxidizer":
        verdict += (
            "【이 팩의 근거】Lee & Seo 2022(Appl. Sci. 12(3) 1227, "
            "doi:10.3390/app12031227) §3.3이 피콜린산 1.5 wt%→5.0 wt%에서 **추가 억제 없음**"
            "(정지식각 11 A/min·제거율 85 A/min 유지)을 직접 실측했다 — 즉 이 팩의 운전점"
            "(1.5 wt% = 121.8 mM)이 **문헌이 측정한 포화 플래토 위**에 있다. 그러므로 여기서의 "
            "포화는 위 (a)이며 판정#17의 고장이 아니다. 다만 같은 근거노트 §7이 모델의 포화가 "
            "**너무 이르다**고 기록했다 — 0.5 wt%에서 이미 θ=0.978이라 강한 억제를 예측하지만 "
            "원문 §3.2는 0.5 wt%를 '억제 실패 수준'으로 정성 서술한다(원문에 0.5 wt% 정지식각 "
            "수치가 없어 확정 불가, RESPONSE_CONFLICT 후보로 미해소). 즉 **플래토 위에서는 맞고 "
            "문턱 아래에서는 미검증**이다. ")
    elif str(rr.pack.name) == "cu_h2o2_bta":
        verdict += (
            "【이 팩의 근거】판정#17이 이 팩의 K_eq 경로를 반증했다 — 위 K는 쌍 표"
            "(bta×cu)에서 왔고 팩의 단일 ΔG(-35.4 kJ/mol, K_eq≈2.87e4)를 쓰는 경로보다 "
            "포화가 덜하다. 역산 K_eff 후보(183·249.7 L/mol)는 계가 다른 알칼리+알루미나 "
            "데이터라 채택하지 않았다(임의 대입 금지). ")
    out["inhibitor_saturation_note"] = (
        f"{verdict}"
        f"C={C_molar * 1e3:g} mM, K={K:.4g} L/mol(출처: {k_src}) → θ={theta:.6f}, "
        f"여유(1-θ)={1.0 - theta:.6g}. "
        "⚠ 진단 전용 — MRR에 곱하지 않는다(_inhibitor_term이 이미 같은 θ를 소비해 "
        "ψ 배수를 만들고 있어 이중계상이 된다). "
        "⚠ θ 절대값은 참값 주장이 아니다 — 판정#17이 'K_eq를 정상상태 θ에 직접 대입하는 "
        "경로'를 반증했고, 역산 K_eff 후보(183·249.7 L/mol)는 계가 다른 알칼리+알루미나 "
        "데이터라 이 팩에 채택하지 않았다(임의 대입 금지).")
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


def _thermal_chemical_diagnostic(rr: "ResolvedRecipe",
                                  theta_ss: Dict[str, object]) -> Dict[str, object]:
    """마찰열 ΔT_ss → Arrhenius 화학반응속도 배율 진단 — MRR 경로와 완전히 독립적인 진단 계산.

    근거: sim/tier2_physics/frictional_heating_arrhenius.py::arrhenius_rate_ratio (원본 무수정),
    knowledge/physics/frictional-heating-temperature-arrhenius-coupling.md §4 — Shin et al. 2025,
    *Materials* 18(19) 4461, DOI 10.3390/ma18194461("Process Temperature Control for Low Dishing
    in CMP", Crossref로 실존 확인) 실측 겉보기 활성화에너지 표(SiO2 8.75 / Ta 29.9 / Cu
    151.7 kJ/mol). Ea·lnA 상수는 이 진단이 새로 선언하지 않고 원본 모듈의
    SHIN2025_EA_J_MOL dict를 그대로 읽는다(단일 출처 — 값을 두 곳에 중복 하드코딩하면
    나중에 한쪽만 고쳐 어긋나는 사고가 난다).

    **Ea는 재료(막질)별이다**(rr.film로 분기 — 판정#34: 팩 이름이 아니라 데이터 필드).
    Shin 2025 표에 값이 없는 막질(sic_4h·w — Ta는 팩에 대응 막질이 없어 애초에 미사용)은
    지어내지 않고 None + 스킵사유.

    **기준온도 T1**은 절대온도를 지어내지 않는다. base.yaml의 platen_coolant_temp_c
    (literature, Shin 2025 균형점 30 ℃)를 쓴다 — 이 값이 정확히 _theta_steady_state_
    diagnostic()이 이미 가정하는 "공급 슬러리·플래튼·주변 공기가 같은 온도"라는 공통 싱크
    T0와 같은 근거·같은 조건이다(노트 §8.2). T2 = T1 + ΔT_ss(theta_ss 진단 결과). 팩이
    platen_coolant_temp_c를 선언하지 않거나 theta_ss가 입력 미비로 None이면 이 진단도
    조용히 None — 임의 상온 25 ℃ 등을 기본값으로 넣지 않는다.

    ⚠ **이 배율을 MRR에 곱하지 않는다.** Kp가 이미 특정 공정온도에서 역산된 값이므로
    곱하면 이중 계상이다(2026-09-06 Cu MRR 20배 붕괴와 같은 사고 패턴 — factors.py
    결합 지점 주석 참조). 진단 필드로만 낸다.

    confidence 판단: Shin 2025의 Ea는 노트 §7이 경고하듯 특정 슬러리(barrier)·특정 툴
    (POLI-500) 조건값이다 — 슬러리 화학·산화제가 바뀌면 달라진다. literature 상한이고
    verified는 아니다(note에 항상 이 한계를 실어 보낸다).
    """
    out: Dict[str, object] = {"thermal_chemical_rate_ratio": None,
                              "thermal_chemical_ea_kj_mol": None,
                              "thermal_chemical_film": None,
                              "thermal_chemical_note": None}
    film_to_shin_key = {"cu": "Cu", "oxide": "SiO2"}
    key = film_to_shin_key.get(rr.film)
    if key is None:
        out["thermal_chemical_note"] = (
            f"film='{rr.film}' — Shin et al. 2025(DOI 10.3390/ma18194461) 겉보기 활성화에너지 "
            f"표에 이 막질의 1차값이 없음(SiO2/Ta/Cu만 보고) — 지어내지 않고 스킵")
        return out
    delta_t = theta_ss.get("theta_steady_state_delta_T_k")
    if delta_t is None:
        out["thermal_chemical_note"] = (
            "theta_steady_state_delta_T_k가 None(Θ 정상상태 열수지 입력 미비) — T2를 지어낼 "
            "수 없어 열-화학 반응속도 배율 진단도 스킵")
        return out
    if not rr.pack.has("platen_coolant_temp_c"):
        out["thermal_chemical_note"] = (
            "platen_coolant_temp_c 팩에 없음 — 기준온도 T1(공급 슬러리·플래튼 공통 싱크)을 "
            "지어낼 수 없어 스킵")
        return out
    try:
        import frictional_heating_arrhenius as FHA   # sim/tier2_physics (1바이트도 수정 안 함)
        Ea = FHA.SHIN2025_EA_J_MOL[key]
        T1 = float(rr.p("platen_coolant_temp_c")) + 273.15
        T2 = T1 + float(delta_t)
        ratio = FHA.arrhenius_rate_ratio(Ea, T1, T2)
    except Exception as e:
        out["thermal_chemical_note"] = f"열-화학 Arrhenius 배율 계산 실패({e}) — None으로 둠"
        return out
    out["thermal_chemical_rate_ratio"] = float(ratio)
    out["thermal_chemical_ea_kj_mol"] = Ea / 1e3
    out["thermal_chemical_film"] = rr.film
    out["thermal_chemical_note"] = (
        f"film='{rr.film}' Ea={Ea / 1e3:.2f} kJ/mol(Shin et al. 2025, Materials 18(19) 4461, "
        f"DOI 10.3390/ma18194461 §4 표 — barrier 슬러리·POLI-500 툴 조건값, 슬러리 화학·산화제가 "
        f"바뀌면 달라짐, 노트 §7). T1={T1:.2f} K(platen_coolant_temp_c, 공통 싱크 가정), "
        f"T2=T1+ΔT_ss={T2:.2f} K. 반응속도 배율={ratio:.3f}x. "
        f"⚠ MRR에 곱하지 않음(진단 전용) — Kp가 이미 특정 공정온도에서 역산된 값이라 곱하면 "
        f"이중 계상.")
    return out


def _pad_viscoelastic_diagnostic(rr: "ResolvedRecipe",
                                  theta_ss: Dict[str, object]) -> Dict[str, object]:
    """패드 유효 탄성률 E'(T) 온도의존 연화 진단 — MRR 경로와 완전히 독립.

    근거: sim/tier2_physics/pad_viscoelastic_temperature.py::e_pad_from_table (원본 무수정),
    CABOT_TABLE_1B = Cabot US20170087688A1 Table 1B(freepatentsonline 원문 확인, 25/50/80 °C
    앵커 6개 패드), knowledge/materials/pad-viscoelasticity-temp-frequency-dma.md §2,§3.1,§6.

    이 진단이 등록 가능해진 이유: 모듈 docstring은 "Recipe에 온도 필드가 없다"를 미등록
    사유로 들었지만, 그 전제는 _theta_steady_state_diagnostic()이 이미 ΔT_ss(theta_ss 진단
    결과, 공통 싱크 대비 정상상태 온도상승)를 산출하면서 깨졌다. T_op = T_coolant + ΔT_ss로
    공정온도를 근사해 입력으로 쓴다. T_coolant는 새 상수를 만들지 않고 _thermal_chemical_
    diagnostic()과 동일하게 base.yaml의 platen_coolant_temp_c(literature)를 재사용한다.

    ⚠ **Kp_eff(T) 훅은 넣지 않는다.** 모듈 docstring이 "이번 범위 밖, 실측 대조 전까지 OFF"
    라고 명시했다 — 이 진단은 순수 가시화이고 MRR에 어떤 영향도 주지 않는다.

    **패드 ID를 지어내지 않는다.** CABOT_TABLE_1B의 1A~1E·D100이 FabSim 팩의 실제 패드
    (IC1000류 등)와 동일 제품이라는 근거가 없다. 팩이 `pad_dma_id`를 명시 선언할 때만
    계산한다 — 현재 5팩 전부 미선언이라 항상 None이 정상이다(pad_groove_eol과 동일 지위).

    **범위 밖 외삽 금지**: e_pad_loglinear는 25/50/80 °C 범위 밖을 최근접 앵커로 clamp한다
    (모듈 자체 동작, 고치지 않는다). clamp가 실제로 일어났으면 note에 반드시 그 사실을
    남긴다 — 조용한 clamp 값 출력 금지.

    ΔT_ss가 None(theta_ss 입력 미비)이거나 platen_coolant_temp_c가 팩에 없으면 조용히 None.

    한계(모듈 docstring·노트 §5 그대로 전파, 지어내지 않음): Cabot Table 1B는 1 Hz DMA
    인장모드 값이고, CMP는 압축모드·asperity 스케일 고주파(노트 §5 추정 ~2e4 Hz)라 이 값을
    CMP 하중조건에 그대로 쓰는 것은 검증되지 않았다. 80 °C E'=5 MPa 같은 값은 Tg를 지난
    고무상이라 CMP 실제 운전온도(보통 <60 °C)와 맞는지도 확인되지 않았다.
    """
    out: Dict[str, object] = {"pad_modulus_at_temp_mpa": None,
                              "pad_modulus_ref_25c_mpa": None,
                              "pad_modulus_softening_ratio": None,
                              "pad_viscoelastic_note": None}
    if not rr.pack.has("pad_dma_id"):
        out["pad_viscoelastic_note"] = (
            "pad_dma_id 미선언 — Cabot Table 1B(1A~1E/D100)가 이 팩의 실제 패드와 동일 "
            "제품이라는 근거가 없어 계산 스킵(현재 5팩 전부 미선언이라 항상 None이 정상)")
        return out
    delta_t = theta_ss.get("theta_steady_state_delta_T_k")
    if delta_t is None:
        out["pad_viscoelastic_note"] = (
            "theta_steady_state_delta_T_k가 None(Θ 정상상태 열수지 입력 미비) — 공정온도 T_op를 "
            "지어낼 수 없어 패드 연화 진단도 스킵")
        return out
    if not rr.pack.has("platen_coolant_temp_c"):
        out["pad_viscoelastic_note"] = (
            "platen_coolant_temp_c 팩에 없음 — 기준온도 T_coolant를 지어낼 수 없어 스킵")
        return out
    try:
        import pad_viscoelastic_temperature as PVT   # sim/tier2_physics (1바이트도 수정 안 함)
        pad_id = rr.p("pad_dma_id")
        T_coolant = float(rr.p("platen_coolant_temp_c"))
        T_op = T_coolant + float(delta_t)
        row = PVT.CABOT_TABLE_1B[pad_id]
        t_min, t_max = row["T_C"][0], row["T_C"][-1]
        e_op = PVT.e_pad_from_table(T_op, pad_id)
        e_ref = PVT.e_pad_from_table(25.0, pad_id)
        ratio = e_op / e_ref
    except Exception as e:
        out["pad_viscoelastic_note"] = f"패드 연화 진단 실패({e}) — None으로 둠"
        return out
    out["pad_modulus_at_temp_mpa"] = float(e_op)
    out["pad_modulus_ref_25c_mpa"] = float(e_ref)
    out["pad_modulus_softening_ratio"] = float(ratio)
    clamp_note = ""
    if T_op < t_min or T_op > t_max:
        clamp_note = (f" ⚠ T_op={T_op:.1f}°C가 Cabot Table 1B 앵커범위[{t_min:g},{t_max:g}]°C "
                      f"밖 — e_pad_loglinear가 최근접 앵커({t_min if T_op < t_min else t_max:g}°C)"
                      f"로 clamp했다(외삽 아님, 근사 저하).")
    out["pad_viscoelastic_note"] = (
        f"pad_dma_id='{pad_id}', T_op=T_coolant+ΔT_ss={T_coolant:.1f}+{delta_t:.1f}="
        f"{T_op:.1f}°C. E'(T_op)={e_op:.1f} MPa, E'(25°C)={e_ref:.1f} MPa, "
        f"softening_ratio={ratio:.4f}.{clamp_note} "
        "⚠ 진단 전용, MRR에 영향 없음(Kp_eff(T) 훅은 이번 범위 밖, OFF 유지). "
        "Cabot Table 1B는 1 Hz DMA 인장모드 값 — CMP 압축모드·asperity 고주파(~2e4 Hz, "
        "노트 §5 추정) 하중조건으로의 적용은 검증되지 않았다. 80°C E'=5 MPa 같은 Tg 이후 "
        "고무상 값이 CMP 실제 운전온도(보통 <60°C)와 맞는지도 확인되지 않았다.")
    return out


def _pad_loading_frequency_diagnostic(rr: "ResolvedRecipe") -> Dict[str, object]:
    """공정 하중 주파수 ω → 패드 이완시간 임계값(역진단) — MRR 경로와 완전히 독립.

    근거: sim/tier2_physics/viscoelastic_maxwell.py::maxwell_storage_loss/tan_delta
    (원본 무수정), sim/tier2_physics/gw_pressure_solve.py::local_contact_state,
    sim/tier2_physics/gw_contact.py::hertz_contact_area(둘 다 원본 무수정),
    sim/tier1_empirical/kinematics.py::rpm_to_rads/speed_stats(원본 무수정),
    knowledge/materials/pad-viscoelasticity-dma.md §3(Maxwell 모델 수식),
    §4(CMP 패드 실측 τ_creep 미확보 자백), §7(a)(ω=1/τ0 → E'/E=0.5 항등식), §8(개정).

    §4가 자백하듯 CMP 패드 실측 τ0(이완시간)를 확보하지 못했다 — τ0를 지어내 De=τ0·ω를
    내지 않는다. 대신 **역방향 진단**: 공정 하중 주파수 ω_process 후보를 기존 literature
    등급 필드에서만 유도하고, τ0 없이도 계산되는 실질 정보인 τ_crit=1/ω(그 주파수에서
    탄성/점성 경계가 되는 임계 이완시간)를 낸다.

    후보 (A) 플래튼 회전 ω_rot = 2π·rpm_platen/60 [rad/s] — 패드 위 한 점이 웨이퍼 아래를
    지나는 주기. rr.rpm_platen(base.yaml, confidence=literature)만으로 항상 계산된다.

    후보 (B) asperity 접촉 주기 ω_asperity = 2π·V_rel/(2a) — 2026-09-16 정정: 이전 회차가
    "구조적으로 계산 불가"라 적었으나 **틀렸다**. GW 지수분포 해에서는 평균 압입깊이가
    닫힌형으로 나온다 — A_r = πRηA_n·(1/β)·e^(−βd), n = ηA_n·e^(−βd) 이므로
    δ_mean = A_r/(πR·n) = 1/β 가 **d에 무관한 정확한 항등식**이다(지수분포 memoryless
    성질, gw_contact.py 독스트링의 gw_analytic_ratio 유도와 같은 적분). 이는 새 통계
    가정이 아니라 팩이 이미 literature 등급으로 선언한 asperity_height_distribution=
    exponential에서 직접 유도되는 수학적 귀결이다. 그래서 GW 5개 패드 파라미터
    (_gw_contact_state_diagnostic과 동일 키)가 선언돼 있고 asperity_height_distribution
    이 정확히 "exponential"일 때만 δ_mean=1/β → 2a=hertz_contact_area(δ_mean,R)에서
    접촉폭 → ω_asperity=2π·V/(2a)를 실제로 계산한다(V는 다른 모든 진단과 동일하게
    kin.speed_stats(...)["mean"]). 다른 분포(예: gaussian)면 이 항등식이 성립하지 않아
    지어내지 않고 None + 스킵사유로 둔다.

    τ0가 팩에 pad_relaxation_time_s로 선언될 때만(현재 어느 팩도 미선언 — 항상 None이
    정상) rot·asperity 두 축 모두 De=τ0·ω, E'/E, E''/E, tanδ를
    viscoelastic_maxwell.maxwell_storage_loss/tan_delta로 실제 계산한다(E=1.0 무차원
    스프링 계수 — 모듈 자체 규약, 비율만 의미). 두 축은 서로 다른 물리 주기이므로
    평균내거나 하나를 대표값으로 고르지 않는다.
    """
    out: Dict[str, object] = {
        "pad_loading_omega_rot_rad_s": None,
        "pad_loading_omega_asperity_rad_s": None,
        "pad_relaxation_time_threshold_s": {"rot": None, "asperity": None},
        "pad_deborah_number": {"rot": None, "asperity": None},
        "pad_loading_frequency_note": None,
    }
    notes: List[str] = []
    from sim.tier1_empirical import kinematics as kin

    omega_rot = kin.rpm_to_rads(rr.rpm_platen)
    if rr.rpm_platen <= 0 or omega_rot <= 0:
        notes.append(f"rpm_platen={rr.rpm_platen} <= 0 — ω_rot 계산 불가, 스킵")
        out["pad_loading_frequency_note"] = " | ".join(notes)
        return out
    out["pad_loading_omega_rot_rad_s"] = float(omega_rot)
    out["pad_relaxation_time_threshold_s"]["rot"] = float(1.0 / omega_rot)
    notes.append(
        f"ω_rot=2π·rpm_platen/60={omega_rot:.4f} rad/s(rpm_platen={rr.rpm_platen:g}) — "
        f"플래튼 회전주기 기준. τ_crit_rot=1/ω_rot={1.0/omega_rot:.4f} s "
        "(패드 이완시간이 이보다 길면 이 주파수에서 탄성 지배, 짧으면 점성 지배)")

    omega_asp = None
    # _gw_contact_state_diagnostic과 동일 키 튜플 재사용(새 게이트 만들지 않음)
    pad_keys = ("pad_E_star_pa", "pad_asperity_radius_m", "pad_height_beta_inv_m",
                "pad_asperity_density_m2", "pad_nominal_area_m2")
    missing_pad = [k for k in pad_keys if not rr.pack.has(k)]
    dist = rr.p("asperity_height_distribution") if rr.pack.has("asperity_height_distribution") else None
    if missing_pad:
        notes.append(
            f"ω_asperity 스킵 — GW 패드 파라미터 미선언({', '.join(missing_pad)}): "
            "δ_mean=1/β 항등식을 풀 입력이 없음")
    elif dist != "exponential":
        notes.append(
            f"ω_asperity 스킵 — asperity_height_distribution={dist!r}(exponential 아님): "
            "δ_mean=1/β는 지수분포 memoryless 항등식이라 다른 분포에서는 성립하지 않고, "
            "지어낼 수 없음")
    else:
        try:
            import gw_pressure_solve as GWP   # sim/tier2_physics (1바이트도 수정 안 함)
            import gw_contact as GWC          # sim/tier2_physics (1바이트도 수정 안 함)
            E_star = rr.p("pad_E_star_pa")
            R = rr.p("pad_asperity_radius_m")
            # ⚠ 단위: 팩 키는 스케일 1/β [m], 모듈이 받는 인자는 감쇠율 β [1/m]. 역수 변환
            # 필수(미변환 시 d가 21.6 km로 풀린 전례, _gw_contact_state_diagnostic 주석 참조).
            beta = 1.0 / rr.p("pad_height_beta_inv_m")
            eta = rr.p("pad_asperity_density_m2")
            A_n = rr.p("pad_nominal_area_m2")
            P_center = rr.pressure_psi * PSI_TO_PA
            state = GWP.local_contact_state(P_center, A_n, beta, eta, E_star, R)
            # δ_mean = A_r/(π·R·n) = 1/β (지수분포 GW 해의 정확한 항등식, d와 무관)
            delta_mean = state["A_r"] / (math.pi * R * state["n_contacts"])
            area = GWC.hertz_contact_area(delta_mean, R)   # = πRδ (원본 무수정)
            a = math.sqrt(area / math.pi)
            L = 2.0 * a
            V_mean = kin.speed_stats(rr.wafer_radius_m, rr.center_offset_m,
                                     rr.rpm_wafer, rr.rpm_platen)["mean"]
            omega_asp = 2.0 * math.pi * V_mean / L
        except Exception as e:
            notes.append(f"ω_asperity 계산 실패({e}) — None으로 둠")
            omega_asp = None
        else:
            out["pad_loading_omega_asperity_rad_s"] = float(omega_asp)
            out["pad_relaxation_time_threshold_s"]["asperity"] = float(1.0 / omega_asp)
            ratio = omega_asp / omega_rot
            notes.append(
                f"ω_asperity=2π·V/(2a)={omega_asp:.4e} rad/s(V={V_mean:.4f} m/s, "
                f"δ_mean={delta_mean:.4e} m=1/β[지수분포 항등식, asperity_height_distribution="
                f"exponential 전제], 2a={L:.4e} m) — 애스퍼리티가 접촉폭 L=2a를 한 번 지나가는 "
                f"주기 기준. τ_crit_asperity=1/ω_asperity={1.0/omega_asp:.4e} s. "
                f"ω_asperity/ω_rot={ratio:.3e}배 — 두 축은 서로 다른 물리 주기(플래튼 1회전 "
                "주기 vs 애스퍼리티가 접촉폭을 지나는 주기)라 평균내거나 하나를 대표값으로 "
                "고르지 않는다. GW 5개 패드 파라미터는 base.yaml 상속이라 팩마다 값이 다르지 "
                "않다(팩별 차이를 시사하지 않음).")

    if not rr.pack.has("pad_relaxation_time_s"):
        notes.append(
            "pad_relaxation_time_s 미선언 — τ0(패드 실측 이완시간)를 지어낼 수 없어 "
            "De(rot/asperity 모두), E'/E, E''/E, tanδ는 None. τ_crit만 유효 정보.")
        out["pad_loading_frequency_note"] = " | ".join(notes)
        return out
    try:
        import viscoelastic_maxwell as VM   # sim/tier2_physics (1바이트도 수정 안 함)
        tau0 = float(rr.p("pad_relaxation_time_s"))
        omegas = {"rot": omega_rot}
        if omega_asp is not None:
            omegas["asperity"] = omega_asp
        for axis, omega in omegas.items():
            Es, El = VM.maxwell_storage_loss([omega], 1.0, tau0)
            td = VM.tan_delta(Es, El)
            de = tau0 * omega
            out["pad_deborah_number"][axis] = {
                "tau0_s": tau0, "De": float(de),
                "E_storage_ratio": float(Es[0]), "E_loss_ratio": float(El[0]),
                "tan_delta": float(td[0]),
            }
            regime = ("탄성(저장) 지배" if de > 1 else
                      ("점성(손실) 지배" if de < 1 else "전이(De=1, E'/E=0.5)"))
            notes.append(
                f"τ0={tau0:.4g}s(팩 선언값) → De_{axis}=τ0·ω_{axis}={de:.4g} → {regime}, "
                f"E'/E={float(Es[0]):.4f}, E''/E={float(El[0]):.4f}, tanδ={float(td[0]):.4f}")
    except Exception as e:
        notes.append(f"τ0 선언되어 있으나 Deborah 수 계산 실패({e}) — None으로 둠")
    out["pad_loading_frequency_note"] = " | ".join(notes)
    return out


def _disk_gw_scaling_diagnostic(rr: "ResolvedRecipe") -> Dict[str, object]:
    """디스크 설계 스펙(그릿 개수 N, 그릿 크기 D) 변경이 GW 접촉모델 파라미터
    (Ra, Rpk, λ)에 미치는 상대 배율 진단 — MRR 경로와 완전히 독립.

    근거: sim/tier2_physics/disk_gw_relative_scaling.py::ra_relative/rpk_relative/
    lambda_relative(원본 무수정). Kwon et al. (2013), Tribology International 67, 272-277,
    doi.org/10.1016/j.triboint.2013.08.008 — Ra∝N^-0.23, Rpk∝N^-0.62(Fig.2 3점 회귀).
    Sun (2009) PhD dissertation, Univ. of Arizona, http://hdl.handle.net/10150/194898 —
    λ∝D^0.35(고하중 ≈8 lb 근방, §4 종합 0.3~0.4 작업가설의 중간값), λ_rel≈1(저하중
    ≈3.6 lb 이하, 그릿 크기 무관).

    ⚠ **절대값 아님, 배율뿐.** 이 모듈은 (N_ref, D_ref) -> (N_target, D_target) 상대
    배율만 계산한다 — 절대 Ra/Rpk/λ(µm 실측치)는 모듈 docstring이 명시적으로
    캘리브레이션 파라미터로 남긴 것이라 여기서도 만들어내지 않는다.

    **"기준 디스크"를 지어내지 않는다.** disk_gw_ref_grit_count/disk_gw_ref_grit_size와
    disk_gw_target_grit_count/disk_gw_target_grit_size 네 키를 팩이 전부 선언할 때만
    계산한다(현재 5팩 전부 미선언이라 항상 None이 정상 — pad_groove_eol·
    pad_viscoelastic과 동일 지위). 어느 팩에도 이 키를 새로 박아 넣지 않는다.

    **λ 하중 레짐을 임의로 고르지 않는다.** disk_gw_high_load(bool)가 팩에 선언돼
    있으면 그 레짐 하나로 λ_rel을 낸다. 미선언이면 고하중(λ∝D^0.35)·저하중(그릿
    크기 무관, λ_rel=1) 두 값을 note에 병기만 하고 disk_gw_lambda_relative는
    None으로 둔다(평균 내거나 하나를 임의로 고르지 않는다 — Sun 2009 §3.3은 하중별로
    물리 자체가 달라진다고 서술한다).

    ⚠ **disk_preston_contact_decomposition의 Kp 스케일링 훅은 끌어오지 않는다** — 그
    모듈은 스스로 PROVISIONAL·"캘리브레이션 없이 정량예측 금지"라고 선언했다. 이
    진단은 그 모듈과 완전히 무관하다.

    **grade는 다루지 않는다** — 이 진단은 grade 필드를 아예 입력받지 않는다(Kwon 2013
    §2.1은 grade 625/640/925 3점 관찰만 있고 회귀하지 않아 모듈 자체가 grade의 수치
    변환을 하지 않는다).

    한계(모듈 docstring 그대로 전파): λ의 0.35는 Sun 2009 §4가 명시한 0.3~0.4
    작업가설 범위의 중간값이지 회귀값이 아니다. surface finish(D 구간분기 0.71/0.23
    포화, leveled 배율)는 이 진단이 다루는 3개 GW 파라미터(Ra, Rpk, λ)에 포함되지
    않아 노출하지 않는다.
    """
    out: Dict[str, object] = {"disk_gw_ra_relative": None,
                              "disk_gw_rpk_relative": None,
                              "disk_gw_lambda_relative": None,
                              "disk_gw_scaling_note": None}
    need = ("disk_gw_ref_grit_count", "disk_gw_ref_grit_size",
            "disk_gw_target_grit_count", "disk_gw_target_grit_size")
    missing = [k for k in need if not rr.pack.has(k)]
    if missing:
        out["disk_gw_scaling_note"] = (
            f"⚠ 디스크 GW 상대 배율 진단 스킵 — 팩에 없음: {', '.join(missing)} "
            "(기준/대상 디스크 스펙을 지어낼 수 없음, 현재 5팩 전부 미선언이라 항상 "
            "None이 정상)")
        return out
    try:
        import disk_gw_relative_scaling as DGW   # sim/tier2_physics (1바이트도 수정 안 함)
        N_ref = float(rr.pack.get("disk_gw_ref_grit_count"))
        D_ref = float(rr.pack.get("disk_gw_ref_grit_size"))
        N_target = float(rr.pack.get("disk_gw_target_grit_count"))
        D_target = float(rr.pack.get("disk_gw_target_grit_size"))
        ra_rel = DGW.ra_relative(N_ref, N_target)
        rpk_rel = DGW.rpk_relative(N_ref, N_target)
        lam_hi = DGW.lambda_relative(D_ref, D_target, high_load=True)
        lam_lo = DGW.lambda_relative(D_ref, D_target, high_load=False)
    except Exception as e:
        out["disk_gw_scaling_note"] = f"⚠ 디스크 GW 상대 배율 계산 실패({e}) — None으로 둠"
        return out
    out["disk_gw_ra_relative"] = float(ra_rel)
    out["disk_gw_rpk_relative"] = float(rpk_rel)
    if rr.pack.has("disk_gw_high_load"):
        high_load = bool(rr.pack.get("disk_gw_high_load"))
        lam_rel = lam_hi if high_load else lam_lo
        out["disk_gw_lambda_relative"] = float(lam_rel)
        load_note = f"disk_gw_high_load={high_load} 선언값 사용, λ_rel={lam_rel:.4f}."
    else:
        load_note = (
            f"disk_gw_high_load 미선언 — 하중 레짐을 임의로 고르지 않음: "
            f"고하중(λ∝D^0.35) λ_rel={lam_hi:.4f}, 저하중(그릿 크기 무관) λ_rel={lam_lo:.4f} "
            "두 값만 병기, 대표값 없음(평균 금지).")
    out["disk_gw_scaling_note"] = (
        f"N_ref={N_ref:g}->N_target={N_target:g}, D_ref={D_ref:g}->D_target={D_target:g}. "
        f"Ra_rel={ra_rel:.4f}(Kwon 2013 Ra∝N^-0.23), Rpk_rel={rpk_rel:.4f}"
        f"(Kwon 2013 Rpk∝N^-0.62). {load_note} "
        "⚠ 진단 전용, MRR에 영향 없음(disk_preston_contact_decomposition의 Kp 스케일링 훅과 "
        "무관 — 그 모듈은 PROVISIONAL, 캘리브레이션 없이 정량예측 금지를 선언했다). "
        "grade(sharp/blunt)는 수치 변환하지 않음(Kwon 2013 §2.1 3점 관찰, 회귀 없음). "
        "λ 지수 0.35는 Sun 2009 §4의 0.3~0.4 작업가설 범위 중간값(회귀값 아님).")
    return out


def _particle_contact_diagnostic(rr: "ResolvedRecipe") -> Dict[str, object]:
    """단일 연마입자 소성 접촉(plowing) 진단 — MRR 경로와 완전히 독립.

    근거: sim/tier2_physics/particle_chemomechanical_synergy.py::plastic_plowing
    (원본 무수정, self-test 5/5 PASS), knowledge/cmp/particle-wafer-interaction-mechanical-
    chemical-balance.md §2·§3·§4.

    이 진단이 등록 가능해진 이유: 모듈 docstring이 "미등록"이라 선언한 것은 Preston Kp로의
    **정량 연결식**이 없다는 뜻이다(chemomechanical_amplification, 즉 화학연화 전후 H 비율에
    따른 증폭비 — 아래 참조). 단일입자 소성 압입/plowing 자체를 진단 필드로 내는 것은 그와
    별개이고, 필요한 입력이 base.yaml에 이미 있다: active_particle_density_per_m2(GW 수치적분
    유래, 3 psi 대표값), abrasive_size_nm(팩별 실측 평균 입경), film_bulk_hardness_pa(팩별
    나노압입 벌크경도, sti_ceria만 미선언).

    입자당 하중 F: 명목압력 P를 활성입자 면밀도 η로 나눈다.
      F = (P·A_n) / (η·A_n) = P/η [Pa / m^-2 = Pa·m^2 = N]
    A_n(pad_nominal_area_m2)은 분자·분모에서 소거된다 — "명목압력이 누르는 명목면적 내
    활성입자 전체가 그 하중을 나눠 받는다"는 GW 활성입자 정의(η 자체의 유래) 그대로다.
    입자 반경 R = abrasive_size_nm/2(직경→반경, 팩 note가 "mean diameter"/"diam"으로 명시).

    ⚠ **η(active_particle_density_per_m2)는 confidence=estimated**다(GW 수치적분, 3 psi
    부근에서만 유효 — base.yaml 주석). 이 진단이 그 confidence를 올리지 않는다. F는 η에
    선형 반비례이므로 F도 η의 추정 성격을 그대로 물려받는다.
    2026-09-16 재판정(knowledge/cmp/active-particle-density-load-per-particle-audit.md):
    F=P/η 유도 자체는 η의 정의(GW 접촉 자리 수/명목면적)와 정합적임을 확인했다 — 유도 오류가
    아니다. 대신 η가 "패드 돌기 접촉 자리"를 "활성입자"로 등치하는 단층 가정이 Luo(2001,
    doi:10.1109/66.920723)를 직접 인용·확장한 동일 저자 폐형식과 4~5자릿수 어긋남을 정량
    확인했다(위 노트 §2.3) — δ_p≥R 경고가 그 근거를 인용한다.

    ⚠ **chemomechanical_amplification()은 호출하지 않는다.** H_soft(화학연화 후 경도)가
    5팩 어디에도 없고, 노트 §6이 스스로 "실제 연화 정도는 슬러리별 미검증"이라 못박았다 —
    지어내면 근거 없는 수치가 제품 출력이 된다(tests/test_particle_contact_diagnostic.py가
    이 경계를 grep으로 기계 고정한다).

    탄성 레짐 판정(single_particle_elastic_contact의 p_max vs H)은 내지 않는다 — 입자-막
    등가탄성계수 E*를 구하려면 두 재료의 영률·포아송비가 필요한데 어느 팩에도 없다(입자는
    실리카/알루미나/세리아, 막은 산화막/Cu/SiC/W로 재료쌍마다 다르고 지어낼 수 없다).

    film_bulk_hardness_pa 미선언(현재 sti_ceria만 해당) 또는 rr.pressure_psi 없음(Recipe
    필수 필드라 항상 있음)이면 조용히 None + 사유.

    물리적으로 말이 안 되는 결과(압입깊이 ≥ 입자반경)가 나와도 값을 감추지 않고 note에
    경고를 명시한다(조용한 clamp 금지, 판정 지침).
    """
    out: Dict[str, object] = {"particle_load_n": None,
                              "particle_indent_depth_nm": None,
                              "particle_plow_area_nm2": None,
                              "particle_contact_note": None}
    if not rr.pack.has("film_bulk_hardness_pa"):
        out["particle_contact_note"] = (
            f"film_bulk_hardness_pa 팩 '{rr.pack.name}'에 없음 — 소성 압입 계산에 필요한 "
            "벌크경도 H를 지어낼 수 없어 스킵(현재 sti_ceria만 미선언이 정상)")
        return out
    if not rr.pack.has("abrasive_size_nm"):
        out["particle_contact_note"] = (
            f"abrasive_size_nm 팩 '{rr.pack.name}'에 없음 — 입자 반경 R을 지어낼 수 없어 스킵")
        return out
    if not rr.pack.has("active_particle_density_per_m2"):
        out["particle_contact_note"] = (
            "active_particle_density_per_m2 base.yaml에 없음 — 입자당 하중 F를 지어낼 "
            "수 없어 스킵")
        return out
    try:
        import particle_chemomechanical_synergy as PCS   # sim/tier2_physics (1바이트도 수정 안 함)
        H = float(rr.p("film_bulk_hardness_pa"))
        R = float(rr.p("abrasive_size_nm")) / 2.0 * 1e-9
        eta = float(rr.p("active_particle_density_per_m2"))
        P_nominal = rr.pressure_psi * PSI_TO_PA
        F = P_nominal / eta
        delta_p, A_f = PCS.plastic_plowing(F, R, H)
    except Exception as e:
        out["particle_contact_note"] = f"입자 접촉 진단 계산 실패({e}) — None으로 둠"
        return out
    out["particle_load_n"] = float(F)
    out["particle_indent_depth_nm"] = float(delta_p) * 1e9
    out["particle_plow_area_nm2"] = float(A_f) * 1e18
    warn = ""
    if delta_p >= R:
        warn = (f" ⚠ 압입깊이 δ_p({delta_p*1e9:.3f} nm)가 입자반경 R({R*1e9:.3f} nm) 이상 — "
                "소성 plowing 근사(δ<<R 가정)가 깨진 영역이다. 값을 감추지 않고 그대로 내되 "
                "이 결과의 물리적 신뢰도는 낮다. 원인은 η(GW 접촉 자리 밀도)를 활성입자 밀도로 "
                "등치하는 단층 가정 — Luo(NSF/UC SMART 프리프린트, [1]=Luo&Dornfeld 2001 "
                "doi:10.1109/66.920723 직접 인용·확장)의 포화 활성입자식 N/A'=4/(π·d²)(입자 자체 "
                "투영면적으로 접촉영역을 채우는 밀도)과 대조하면 이 팩의 η가 접촉영역 기준으로 "
                "환산해도 4~5자릿수 작다(knowledge/cmp/active-particle-density-load-per-particle-"
                "audit.md §2.3) — '패드 돌기 자리'(간격 ~수십 µm)와 '슬러리 입자'(간격 수백 nm)를 "
                "동일시한 것 자체가 문헌과 어긋난다는 뜻이다.")
    out["particle_contact_note"] = (
        f"film='{rr.film}', H={H/1e9:.2f} GPa, R={R*1e9:.1f} nm(abrasive_size_nm/2), "
        f"P_nominal={rr.pressure_psi:g} psi. F=P/η={F*1e9:.3f} nN "
        f"(η=active_particle_density_per_m2={eta:.3e} /m², confidence=estimated — GW 수치적분 "
        "유래, 3 psi 부근 대표값. pad_nominal_area_m2는 F=P·A_n/(η·A_n) 계산에서 소거됨). "
        f"δ_p={delta_p*1e9:.3f} nm, A_f={A_f*1e18:.3f} nm².{warn} "
        "⚠ 진단 전용, MRR에 영향 없음(Preston Kp 연결식 없음 — 모듈 docstring 그대로). "
        "chemomechanical_amplification()(화학연화 H_soft 필요)은 호출하지 않음 — H_soft가 "
        "5팩 어디에도 없고 슬러리별 미검증(노트 §6). 탄성 레짐 판정은 입자-막 E*(영률·"
        "포아송비 필요, 팩에 없음)가 없어 내지 않음.")
    return out


def _recipe_conversion_diagnostic(rr: "ResolvedRecipe") -> Dict[str, object]:
    """레시피 전이 work function F(X,Y,Z) 진단 — MRR 경로와 완전히 독립.

    근거: sim/tier2_physics/recipe_conversion_factor.py::work_function/RECIPE_TABLE
    (원본 무수정), knowledge/cmp/product-wafer-proxy-metrics-virtual-metrology.md §2.2·
    §6 verify (A). 1차 문헌: US20060116785A1 식(1)·표 1·표 2·청구항 6.

    이 진단이 등록 가능해진 이유: 모듈 docstring이 "미등록"이라 선언한 것은 Recipe 스키마에
    **"레시피 간 전이"** — 즉 두 레시피를 나란히 놓고 비교하는 개념 — 자체가 없다는 뜻이다
    (recipe_conversion_factor(recipe_from, recipe_to)는 그래서 조립 못 함). 하지만 work
    function F(X,Y,Z) = f(다운포스, 슬러리유량, 플래튼rpm) 자체는 **현재 런 하나**의 X,Y,Z만
    있으면 계산된다 — X=rr.pressure_psi(Recipe 필수 필드), Z=rr.rpm_platen(Recipe/팩,
    base.yaml=55.0), Y=sfr_ml_min(팩, 현재 5팩 전부 base.yaml 상속 150.0 mL/min, literature).
    Y가 팩에 없으면(가정: 향후 팩이 sfr_ml_min을 지우는 경우) 지어내지 않고 스킵한다.

    recipe_wf_vs_ild_ref = F(now)/F(ILD 표1 기준)은 특허 표 2의 "레시피 A→B 변환계수"와
    **같은 종류의 수치이지만 다른 비교**다 — 표 2는 표 1의 이산 레시피끼리(ILD→STI, ILD→IMD)
    비이고, 여기는 "현재 런 vs 표 1의 ILD"다. 이 구분을 note에 명시한다(혼동 방지).

    ⚠ **외삽 경고**: 식(1)은 표 1(ILD/STI/IMD)의 X∈[4.0,4.6] psi, Y∈[100,200] ml/min,
    Z∈[63,108] rpm 범위에서 적합된 경험식이다(RECIPE_TABLE에서 직접 min/max를 읽는다 —
    범위를 새 상수로 박지 않는다). 현재 5팩의 rpm_platen=55(범위 밖)·pressure_psi=3.0
    (범위 밖)이라 사실상 항상 경고가 붙는다 — clamp하지 않고 값은 그대로 내되 note에
    범위 밖임을 명시한다.
    """
    out: Dict[str, object] = {"recipe_work_function": None,
                              "recipe_wf_vs_ild_ref": None,
                              "recipe_conversion_note": None}
    if not rr.pack.has("sfr_ml_min"):
        out["recipe_conversion_note"] = (
            f"sfr_ml_min 팩 '{rr.pack.name}'에 없음 — 슬러리 유량 Y를 지어낼 수 없어 스킵")
        return out
    try:
        import recipe_conversion_factor as RCF   # sim/tier2_physics (1바이트도 수정 안 함)
        X = float(rr.pressure_psi)
        Y = float(rr.p("sfr_ml_min"))
        Z = float(rr.rpm_platen)
        F = RCF.work_function(X, Y, Z)
        ild = RCF.RECIPE_TABLE["ILD"]
        F_ild = RCF.work_function(ild["downforce_psi"], ild["slurry_flow_ml_min"],
                                   ild["platen_rpm"])
        ratio = F / F_ild
    except Exception as e:
        out["recipe_conversion_note"] = f"레시피 전이 work function 계산 실패({e}) — None으로 둠"
        return out
    out["recipe_work_function"] = float(F)
    out["recipe_wf_vs_ild_ref"] = float(ratio)
    xs = [v["downforce_psi"] for v in RCF.RECIPE_TABLE.values()]
    ys = [v["slurry_flow_ml_min"] for v in RCF.RECIPE_TABLE.values()]
    zs = [v["platen_rpm"] for v in RCF.RECIPE_TABLE.values()]
    warn_parts = []
    if not (min(xs) <= X <= max(xs)):
        warn_parts.append(f"X(다운포스)={X:g} psi가 표1 범위[{min(xs):g},{max(xs):g}] 밖")
    if not (min(ys) <= Y <= max(ys)):
        warn_parts.append(f"Y(슬러리유량)={Y:g} ml/min가 표1 범위[{min(ys):g},{max(ys):g}] 밖")
    if not (min(zs) <= Z <= max(zs)):
        warn_parts.append(f"Z(플래튼rpm)={Z:g}가 표1 범위[{min(zs):g},{max(zs):g}] 밖")
    warn = (" ⚠ 외삽 경고(식(1)은 표1 범위 안에서 적합된 경험식, clamp 없이 값 그대로): "
            + "; ".join(warn_parts)) if warn_parts else ""
    out["recipe_conversion_note"] = (
        f"pack='{rr.pack.name}'. F(X={X:g} psi, Y={Y:g} ml/min, Z={Z:g} rpm)={F:.4f} "
        f"(US20060116785A1 식(1)). F(ILD 기준, X={ild['downforce_psi']:g}, "
        f"Y={ild['slurry_flow_ml_min']:g}, Z={ild['platen_rpm']:g})={F_ild:.4f}. "
        f"recipe_wf_vs_ild_ref=F(now)/F(ILD)={ratio:.4f} — 표 2의 ILD→STI/ILD→IMD 변환계수"
        "(1.12/1.41)와 같은 종류지만 다른 비교(표 2는 표 1의 이산 레시피끼리의 비, 이건 현재 "
        f"런 대 표1-ILD의 비)다.{warn} ⚠ 진단 전용, MRR에 영향 없음. sfr_ml_min은 현재 5팩 "
        "전부 base.yaml 상속(150 mL/min, literature) — 팩별 실측 차이 미확보.")
    return out


def _electrical_resistance_diagnostic(rr: "ResolvedRecipe",
                                       remaining_nm: Optional[np.ndarray]) -> Dict[str, object]:
    """Cu dishing에 의한 선저항 증가율(%) 진단 — MRR 경로와 완전히 독립.

    근거: sim/tier2_physics/electrical_thickness_extraction.py::dishing_delta_R_fraction
    (원본 무수정), Chang, Cao, Spanos, "Modeling the Electrical Effects of Metal Dishing
    Due to CMP for On-Chip Interconnect Optimization," IEEE TED 51(10) 1577-1583 (2004),
    doi.org/10.1109/TED.2004.834898 — 표 I, Fig.6 segment 모델.

    이 진단이 등록 가능해진 이유: 모듈 docstring의 "engine.py에 미등록"은
    cu_thickness_from_resistance(실측 선저항 R -> 두께 역산, 역방향)에 대해서만 사실이다 —
    실측 R이 여전히 없다. 반면 dishing_delta_R_fraction(w, R_dish, t)은 실측 R이 필요 없는
    순방향 예측(dishing이 선저항을 몇 % 올리는가)이고, 입력이 이미 엔진에 있다:
    - linewidth_um: _cu_dishing_erosion_tugbawa_diagnostic이 이미 요구·사용하는 meta 필드
      (스키마가 이미 존재). cu_dishing_tugbawa_nm(같은 진단이 내는 dishing 깊이)은 여기서
      쓰지 않는다 — dishing_delta_R_fraction은 Chang 2004의 독립적인 R_dish 곡률반경
      세그먼트 모델이지 Tugbawa dishing 깊이를 재료로 삼는 합성이 아니다(다른 모델, 섞지 않음).
    - t_um(배선 두께): remaining_nm(= initial_thickness_nm - removed, 이 런이 simulate()
      안에서 실제로 낸 잔막. remaining/remaining_nm 지역변수를 그대로 전달받는다)의 반경
      평균을 um로 환산해 쓴다 — 모듈 기본값 0.5 um를 쓰지 않는다. initial_thickness_nm이
      Recipe에 없으면(현재 5팩 기본 실행이 그렇다) remaining_nm이 None이라 스킵한다.

    ⚠ R_dish_um=40.0은 이 공정의 dishing 곡률 실측이 아니라 Chang et al. 2004 표 I에서 그
    논문 자신의 테스트 구조로부터 최소제곱 추출한 값이다(문헌 상수) — note에 항상 경고로
    명시한다. 팩/meta가 R_dish_um을 선언하는 스키마는 없다(현재도, 앞으로도 지어내지 않음).

    cu_thickness_from_resistance·liner_parallel_resistance_ratio·liner_neglect_error_fraction·
    is_liner_negligible은 호출하지 않는다 — 실측 R·라이너 두께가 필요해 값을 지어내야 하고,
    모듈 docstring이 미등록이라 선언한 부분은 이 함수들에 대해 여전히 유효하다.

    Cu 계 판별은 팩 이름이 아니라 데이터 필드 rr.film == "cu"로 한다(판정#34: 메커니즘/
    데이터로 판단, 이름 하드코딩 금지 — _cu_pourbaix_diagnostic과 동일 관례). 선저항 모델
    자체가 금속 배선(Cu) 전용이라 film != "cu"면(산화막·SiC 등 절연/비도전 막) 조용히 None.
    """
    out: Dict[str, object] = {"electrical_dishing_delta_r_pct": None,
                              "electrical_dishing_r_dish_um": None,
                              "electrical_resistance_note": None}
    if rr.film != "cu":
        out["electrical_resistance_note"] = (
            f"film='{rr.film}' != 'cu' — 선저항 모델은 금속(Cu) 배선 전용, 스킵")
        return out
    linewidth_um = rr.meta.get("linewidth_um")
    if linewidth_um is None:
        out["electrical_resistance_note"] = (
            "PTW 패턴 레이아웃 선폭(linewidth_um) meta 미지정 — dishing 선저항 영향 계산 스킵")
        return out
    if remaining_nm is None:
        out["electrical_resistance_note"] = (
            "initial_thickness_nm 미지정 — 잔막(remaining_nm) 없음, 배선두께 t_um을 이 런의 "
            "실측 없이 지어낼 수 없어 스킵")
        return out
    try:
        import electrical_thickness_extraction as ETE   # sim/tier2_physics (1바이트도 수정 안 함)
        w_um = float(linewidth_um)
        t_um = float(np.mean(remaining_nm)) / 1000.0
        if t_um <= 0:
            out["electrical_resistance_note"] = (
                f"잔막 반경평균 t_um={t_um:.4f} <= 0(오버폴리시) — dishing 선저항 영향 계산 스킵")
            return out
        R_dish_um = 40.0
        delta_r_pct = ETE.dishing_delta_R_fraction(w_um, R_dish_um=R_dish_um, t_um=t_um)
    except Exception as e:
        out["electrical_resistance_note"] = f"dishing 선저항 영향 계산 실패({e}) — None으로 둠"
        return out
    out["electrical_dishing_delta_r_pct"] = float(delta_r_pct)
    out["electrical_dishing_r_dish_um"] = R_dish_um
    out["electrical_resistance_note"] = (
        f"pack='{rr.pack.name}'. w={w_um:g} um, t={t_um:.4f} um(remaining_nm 반경평균), "
        f"R_dish={R_dish_um:g} um(⚠ 이 공정 실측이 아니라 Chang et al. 2004 표I 최소제곱 "
        "추출값, 문헌 테스트구조 곡률이며 이 레시피의 dishing 곡률이 아님) -> dishing에 의한 "
        f"선저항 증가 {delta_r_pct:.2f}% (Chang et al. 2004 doi.org/10.1109/TED.2004.834898 "
        "Fig.6 segment 모델). 실측 R 기반 두께 역산·라이너 보정은 호출하지 않음(입력 없음).")
    return out


def _tribology_archard_diagnostic(rr: "ResolvedRecipe") -> Dict[str, object]:
    """Archard↔Preston 가교 진단 — MRR 경로와 완전히 독립적인 순수 가시화.

    근거: sim/tier2_physics/tribology_basics.py::archard_wear_depth 원본 docstring
    ("Preston 식 dot h = Kp·P·V 와 구조 동일 — Kp≈k/H"), knowledge/physics/
    tribology-friction-wear-stribeck.md §"Archard 오더 대조"(연강 pin-on-disk
    k=1e-3 앵커). k = Kp·H(무차원 Archard 마모계수)로 환산해 오더 타당성만
    대조한다 — 새 물리가 아니고, 어떤 팩터의 confidence도 올리지 않는다.
    ⚠ 한계(note에 항상 명시): Archard k는 연마마모(abrasive wear) 계수이고 CMP는
    화학적 연화가 개입한 화학기계 복합과정이다 — 오더가 겹친다고 "CMP가 순수
    Archard 마모"인 것은 아니다. 앵커 k=1e-3은 연강 pin-on-disk 예시값이지 CMP
    재료계 실측이 아니다.
    film_bulk_hardness_pa가 팩에 없으면(kp_m_per_pa는 Recipe 필수값이라 항상 있음)
    Archard 3필드 전부 조용히 None. Hersey 수는 hersey_number()가 스스로 "관례에
    따라 차원이 달라지므로(무차원이 아닐 수 있음) 오더 확인용"이라 자백해, 이미
    무차원임이 확실한 cmp_sommerfeld_number(_lubrication_diagnostics)와 중복 계산
    하지 않고 slurry_viscosity_pa_s가 있는 팩에서만 η·V/P 형태로 별도로 낸다
    (속도 V는 _lubrication_diagnostics와 동일하게 kin.speed_stats(...)["mean"]).
    stribeck_cof·archard_wear_volume은 호출하지 않는다(전자는 alpha=50.0 등 근거
    없는 정성 파라미터가 박혀 있고 cof_stribeck_estimate와 중복, 후자는 하중 W·
    미끄럼거리 L의 절대값이 Recipe에 없음).
    """
    out: Dict[str, object] = {"archard_wear_coefficient": None, "archard_reference_k": None,
                              "archard_order_ratio": None, "tribology_hersey_number": None,
                              "tribology_note": None}
    if not rr.pack.has("film_bulk_hardness_pa"):
        out["tribology_note"] = "film_bulk_hardness_pa 팩에 없음 — Archard k 환산 스킵"
        return out
    try:
        import tribology_basics as TB   # sim/tier2_physics (1바이트도 수정 안 함)
        H = float(rr.p("film_bulk_hardness_pa"))
        Kp = float(rr.kp_m_per_pa)
        # k·P·L/H (archard_wear_depth) 를 L로 나누면 k·P·V/H — Preston Kp·P·V와 구조가
        # 같아지는 지점이 k=Kp·H다(모듈 docstring이 스스로 적은 대응, 새 유도 아님).
        k = Kp * H
        ref_k = 1e-3   # 연강 pin-on-disk 예시(tribology-friction-wear-stribeck.md §"Archard 오더 대조")
        ratio = k / ref_k
    except Exception as e:
        out["tribology_note"] = f"Archard k 환산 실패({e}) — None으로 둠"
        return out
    out["archard_wear_coefficient"] = k
    out["archard_reference_k"] = ref_k
    out["archard_order_ratio"] = ratio
    notes = [
        f"Archard k = Kp·H = {k:.4e}(Kp={Kp:.2e} m/Pa · H={H:.2e} Pa) — 연강 pin-on-disk "
        f"예시 k=1e-3(tribology-friction-wear-stribeck.md §'Archard 오더 대조') 대비 "
        f"{ratio:.3f}배, 같은 오더(1e-5~1e-1)에 있다는 sanity check일 뿐이다. Archard k는 "
        "연마마모(abrasive wear) 계수이고 CMP는 화학적 연화가 개입한 화학기계 복합과정이라 "
        "오더가 겹친다고 'CMP가 순수 Archard 마모'인 것은 아니다. 앵커 k=1e-3은 연강 "
        "pin-on-disk 예시값이지 CMP 재료계 실측이 아니다 — 이 진단으로 어떤 팩터의 "
        "confidence도 올리지 않는다."
    ]
    if rr.pack.has("slurry_viscosity_pa_s"):
        try:
            from sim.tier1_empirical import kinematics as kin
            eta = float(rr.p("slurry_viscosity_pa_s"))
            U_mean = kin.speed_stats(rr.wafer_radius_m, rr.center_offset_m,
                                     rr.rpm_wafer, rr.rpm_platen)["mean"]
            P = rr.pressure_psi * PSI_TO_PA
            hersey = TB.hersey_number(eta, U_mean, P)
            out["tribology_hersey_number"] = hersey
            notes.append(
                f"Hersey 수(η·V/P, V=kin.speed_stats mean) = {hersey:.4e} — 모듈 docstring이 "
                "'관례에 따라 차원이 달라지므로(무차원이 아닐 수 있음) 오더 확인용'이라 자백해 "
                "여기서도 오더 확인용으로만 낸다. cmp_sommerfeld_number(무차원, "
                "_lubrication_diagnostics)와 값이 다른 이유: So=η·V/(P·δeff)는 유효필름두께 "
                "δeff 항이 있어 무차원이지만 Hersey는 그 항이 없다 — 같은 η·V·P를 쓰지만 "
                "δeff배만큼 다르다(중복 계산 아님)."
            )
        except Exception as e:
            notes.append(f"Hersey 수 계산 실패({e}) — tribology_hersey_number None으로 둠")
    out["tribology_note"] = " ".join(notes)
    return out


def _ceria_redox_diagnostic(rr: "ResolvedRecipe") -> Dict[str, object]:
    """세리아 Ce3+ 산소공공 x·정전인력 진단 — MRR 경로와 완전히 독립적인 순수 가시화.

    근거: sim/tier2_physics/ceria_redox_selectivity.py::ce3_fraction/
    electrostatic_attraction(원본 무수정), knowledge/cmp/ceria-slurry-ce-redox-selectivity.md
    §2(산소공공-Ce3+ 전하균형)·§4(세리아-실리카 IEP 정전인력).

    이 진단이 등록 가능해진 이유: 모듈 docstring의 "Recipe에 pH·H2O2 농도 필드가 없어
    engine.Model로 조립할 입력이 없다"는 전제는 이제 일부만 맞다 — slurry_ph(base.yaml +
    전 팩)·abrasive_iep_ph(oxide_silica·sti_ceria)·ce3_fraction(sti_ceria)이 이미 팩에
    있다(_electrical_resistance_diagnostic 등록·5c9d1ac와 같은 구조: "미등록 사유가
    일부에만 해당하면 그 일부만 순방향으로 등록"). H2O2 **농도**(wt%)는 애초에 이 모듈이
    실제로 요구하는 인자가 아니라서 이 판단과 무관하다.

    x = f/2 (ce3_fraction(x)=2x의 역산, 왕복 항등식은 테스트로 고정). ce3_fraction이 이
    팩 **고유 선언**(has_own)일 때만 계산한다 — has()(상속 포함)를 썼다면 sic_ceria_h2o2
    (base: sti_ceria)가 STI 실측 Ce3+ 분율 0.15를 조용히 물려받았을 것이다. 이건
    04dc440(κ 농도항이 실리카 부모 20wt%를 상속해 판정#48로 끊어낸 것)과 같은 유형의
    하이진 결함이라 has_own으로 미리 막는다.

    정전인력은 electrostatic_attraction(iep_ceria, iep_silica, pH)에
    iep_ceria=abrasive_iep_ph, pH=slurry_ph를 그대로 넣는다. **iep_silica는 지어내지
    않는다** — 노트 §4·§6(b)가 "함수 인자로 노출하되 기본 상수로 박지 않는다(호출측이
    노트 §7 값 6.8/2.5를 명시 전달)"고 적었지만, YAML에 그 값을 새 키로 박는 것도
    금지돼 있다. 대신 팩이 **이미 갖고 있는** wafer_iep_ph를 쓴다: sti_ceria가 이 팩
    고유로 선언한 wafer_iep_ph=2.5는 "실리카 산화막 표면 IEP"이고 출처가 바로 이 노트
    §4다(knowledge/params/sti_ceria.yaml). 노트가 쓴 값(2.5)과 값은 같지만 하드코딩이
    아니라 sim/factors.py::_ph_ceria_window_term이 iep_wafer로 쓰는 것과 동일한, 이미
    출처가 달린 필드를 재사용한 것이다.

    ⚠ abrasive_iep_ph **단독** 선언 여부로 "세리아 계"를 판별하면 안 된다 — grep으로
    재확인한 결과 oxide_silica도 abrasive_iep_ph=2.5(실리카 **자신**의 IEP)를 선언해
    걸린다. 그래서 ce3_fraction·abrasive_iep_ph·wafer_iep_ph **세 키 모두** has_own을
    요구해, 이 조합이 실제로 5팩 중 sti_ceria 하나에만 걸리게 한다(판정#34: 팩 이름이
    아니라 데이터로 판별). abrasive_iep_ph·wafer_iep_ph가 둘 다 own이어야 하므로
    oxide_silica(own abrasive_iep_ph는 있으나 own wafer_iep_ph 없음)·sic_ceria_h2o2
    (own abrasive_iep_ph 없음, own wafer_iep_ph=4.9는 SiC 전용이라 애초에 세리아-실리카
    쌍이 아님)는 정전인력도 스킵된다.

    oxide_nitride_selectivity(실측 oxide/nitride MRR 필요, 엔진은 nitride MRR을 내지
    않음)·h2o2_boost_selectivity(boost_factor=3.0 모듈 스스로 미검증 표기)·
    is_chemisorption/chemisorption_energy_kj_mol(DFT 흡착에너지 eV 필요, 어느 팩도 없음)은
    호출하지 않는다 — test_forbidden_functions_never_called이 ast로 기계 고정한다.
    선택비 절대값(35-70, 59-80)은 어떤 형태로도 결과에 넣지 않는다(모듈이 슬러리·패드·
    압력 의존 캘리브레이션 대상이라고 명시).
    """
    out: Dict[str, object] = {"ceria_oxygen_vacancy_x": None,
                              "ceria_electrostatic_attraction": None,
                              "ceria_redox_note": None}
    notes: List[str] = []
    try:
        import ceria_redox_selectivity as CRS   # sim/tier2_physics (원본 무수정)
    except Exception as e:
        out["ceria_redox_note"] = f"ceria_redox_selectivity import 실패({e}) — None으로 둠"
        return out

    if rr.pack.has_own("ce3_fraction"):
        f = float(rr.p("ce3_fraction"))
        x = f / 2.0
        out["ceria_oxygen_vacancy_x"] = x
        notes.append(f"x=f/2={x:g}(f=ce3_fraction={f:g}, 팩 고유선언)")
    else:
        notes.append(
            "ce3_fraction 이 팩 고유선언 아님(미선언 또는 상속) — 산소공공 x 스킵")

    if (rr.pack.has_own("abrasive_iep_ph") and rr.pack.has_own("wafer_iep_ph")
            and rr.pack.has("slurry_ph")):
        iep_ceria = float(rr.p("abrasive_iep_ph"))
        iep_silica = float(rr.p("wafer_iep_ph"))
        ph = float(rr.p("slurry_ph"))
        attraction = CRS.electrostatic_attraction(iep_ceria, iep_silica, ph)
        out["ceria_electrostatic_attraction"] = attraction
        notes.append(
            f"electrostatic_attraction(iep_ceria={iep_ceria:g}[abrasive_iep_ph], "
            f"iep_silica={iep_silica:g}[wafer_iep_ph], pH={ph:g}[slurry_ph])={attraction} "
            "(-1=인력/0=무전하/+1=반발)")
    else:
        notes.append(
            "abrasive_iep_ph·wafer_iep_ph 둘 다 이 팩 고유선언이어야 정전인력 계산 — "
            "하나라도 없거나 상속값이면 스킵(oxide_silica는 abrasive_iep_ph가 세리아가 "
            "아니라 실리카 자신의 IEP라 own wafer_iep_ph 부재로 걸러짐)")

    out["ceria_redox_note"] = f"pack='{rr.pack.name}'. " + "; ".join(notes)
    return out


# 판정#34: 팩 이름 하드코딩 금지 — abrasive 데이터 필드 값으로만 문헌 IEP 표를 조회한다.
_ABRASIVE_TO_IEP_KEY = {"silica": "SiO2", "ceria": "CeO2", "alumina": "Al2O3"}


def _abrasive_surface_charge_diagnostic(rr: "ResolvedRecipe") -> Dict[str, object]:
    """산화물/연마입자 표면전하 부호(IEP 기준) 진단 — MRR 경로와 완전히 독립적인 순수 가시화.

    근거: sim/tier2_physics/chelation_surface_charge.py::oxide_surface_charge_sign
    (원본 무수정, IEP 문헌표만 읽는다), knowledge/cmp/post-cmp-adsorption-cleaning-
    chemistry.md §3·§6(C)·§7.

    모듈 docstring은 "Recipe에 pH·이온세기·킬레이트 농도 필드가 없어 조립 불가"라고
    통째로 미등록 사유를 달았지만, oxide_surface_charge_sign(oxide, pH)이 실제로 쓰는
    입력(slurry_ph, abrasive)은 **5팩 전부에 이미 있다** — 이온세기·킬레이트 농도가
    필요한 나머지 함수들(chelation_conditional_logK 등)만 여전히 입력이 없다.
    _ceria_redox_diagnostic·_electrical_resistance_diagnostic과 같은 구조로 "미등록
    사유가 일부에만 해당하면 그 일부만 순방향으로 등록"한다.

    abrasive 값 → 모듈 IEP 키는 데이터 필드로만 분기한다(판정#34, 팩 이름 하드코딩
    금지) — silica→SiO2, ceria→CeO2, alumina→Al2O3. 매핑 딕셔너리는 여기(엔진)에 두되
    실제 IEP 숫자는 모듈의 `CSC.IEP`를 직접 읽는다(사본을 만들면 모듈이 바뀔 때 조용히
    어긋난다). 표에 없는 연마입자는 지어내지 않고 스킵한다.

    **교차검증(핵심)**: 팩이 자체적으로 abrasive_iep_ph를 선언한 경우(oxide_silica=2.5,
    sti_ceria=6.8, sic_ceria_h2o2=6.8 상속) 문헌표 값(SiO2=2.0, CeO2=6.8)과 대조해
    괴리를 `abrasive_iep_pack_deviation_ph`로 그대로 노출한다 — 둘 중 하나를 조용히
    고르지 않는다. oxide_silica는 0.5 pH 괴리가 실제로 있다(팩 2.5 vs 문헌 2.0).

    커버리지 확장: 기존 `_colloid_stability_diagnostic`은 abrasive_iep_ph가 팩에
    선언된 경우만 동작해 cu_h2o2_bta·w_fe_oxidizer(알루미나, IEP 미선언) 2팩을
    스킵한다. 이 진단은 문헌표(Al2O3=9.5, Zhang 2024)만으로 부호를 낼 수 있어 그
    2팩도 커버한다 — abrasive_iep_pack_deviation_ph는 None(대조 기준이 없으니)이지만
    부호 자체는 나온다.

    CeO2 취약성: Ederer 2025 실측범위(CSC.CEO2_IEP_LIT_RANGE=5.21~9.40)가 넓어
    단일값 6.8 판정이 취약하다. 범위 하한/상한에서 재계산해 부호가 뒤집히면
    note에 명시한다(예: sti_ceria pH=5.5는 IEP=6.8과 1.3 pH 차이뿐이라 하한
    5.21을 쓰면 부호가 '+'→'-'로 실제로 뒤집힌다).

    ⚠ §7 그대로 전파: IEP는 벌크 분말/유리 표면값이고 CMP 후 실제 박막 IEP는
    미확보 — 부호(+/0/-)만 판정하고 |ζ| 크기는 다루지 않는다.

    chelation_conditional_logK·logK_at_I·log_alpha_H·free_metal_fraction은 호출하지
    않는다 — 이온세기 I·킬레이트 리간드 농도가 Recipe·팩 어디에도 없고, cu_h2o2_bta가
    선언한 chelator_species=glycine은 모듈 리간드 표(EDTA·Cit)에 없어 대체할 근거가
    없다. hf_solution_pH도 호출하지 않는다 — DHF 세정 공정변수(HF wt%)가 Recipe에
    없고, 이 엔진은 연마 단계를 모사하지 세정 단계를 모사하지 않는다.
    test_forbidden_functions_never_called이 ast로 기계 고정한다.
    """
    out: Dict[str, object] = {"abrasive_surface_charge_sign": None,
                              "abrasive_iep_literature_ph": None,
                              "abrasive_iep_pack_deviation_ph": None,
                              "abrasive_surface_charge_note": None}
    if not (rr.pack.has("slurry_ph") and rr.pack.has("abrasive")):
        out["abrasive_surface_charge_note"] = (
            f"slurry_ph 또는 abrasive 팩 '{rr.pack.name}'에 없음 — 표면전하 진단 스킵")
        return out
    abrasive = str(rr.p("abrasive"))
    iep_key = _ABRASIVE_TO_IEP_KEY.get(abrasive)
    if iep_key is None:
        out["abrasive_surface_charge_note"] = (
            f"연마입자 '{abrasive}'는 문헌 IEP 매핑(silica/ceria/alumina)에 없음 — "
            "지어내지 않고 스킵")
        return out
    try:
        import chelation_surface_charge as CSC   # sim/tier2_physics (원본 무수정, import만)
        if iep_key not in CSC.IEP:
            out["abrasive_surface_charge_note"] = (
                f"모듈 IEP 표에 '{iep_key}' 없음 — 지어내지 않고 스킵")
            return out
        ph = float(rr.p("slurry_ph"))
        iep_lit = float(CSC.IEP[iep_key])
        sign = CSC.oxide_surface_charge_sign(iep_key, ph)
    except Exception as e:
        out["abrasive_surface_charge_note"] = f"표면전하 진단 실패({e}) — None으로 둠"
        return out

    out["abrasive_surface_charge_sign"] = sign
    out["abrasive_iep_literature_ph"] = iep_lit

    notes = [f"abrasive='{abrasive}'→IEP키='{iep_key}', 문헌IEP={iep_lit:g}pH "
             f"(sim/tier2_physics/chelation_surface_charge.py::IEP), slurry_ph={ph:g} "
             f"→ 부호='{sign}'(pH<IEP→'+', pH>IEP→'-', pH==IEP→'0'; 표면 양전하일수록 '+')"]

    if rr.pack.has("abrasive_iep_ph"):
        pack_iep = float(rr.p("abrasive_iep_ph"))
        deviation = pack_iep - iep_lit
        out["abrasive_iep_pack_deviation_ph"] = deviation
        if abs(deviation) > 1e-9:
            notes.append(
                f"⚠ 팩 선언 abrasive_iep_ph({pack_iep:g})가 문헌표값({iep_lit:g})과 "
                f"{deviation:+.2f} pH 다르다 — 둘 중 하나를 조용히 고르지 않고 "
                "필드로 둘 다 노출한다(팩 선언값은 부호 판정에 쓰지 않는다, "
                "부호는 문헌표값 기준)")
        else:
            notes.append(
                f"팩 선언 abrasive_iep_ph({pack_iep:g})가 문헌표값({iep_lit:g})과 일치")
    else:
        notes.append(
            "팩이 abrasive_iep_ph 미선언 — 기존 _colloid_stability_diagnostic이 스킵하던 "
            "팩(cu_h2o2_bta·w_fe_oxidizer 계열)도 문헌표만으로 부호 판정 가능 "
            "(abrasive_iep_pack_deviation_ph=None, 대조 기준 없음)")

    if iep_key == "CeO2":
        lo, hi = CSC.CEO2_IEP_LIT_RANGE
        sign_lo = "+" if ph < lo else ("-" if ph > lo else "0")
        sign_hi = "+" if ph < hi else ("-" if ph > hi else "0")
        if sign_lo != sign or sign_hi != sign:
            flips = []
            if sign_lo != sign:
                flips.append(f"하한{lo:g}→'{sign_lo}'")
            if sign_hi != sign:
                flips.append(f"상한{hi:g}→'{sign_hi}'")
            notes.append(
                f"⚠ CeO2 IEP는 합성법별 실측범위가 {lo:g}~{hi:g}pH로 넓다(Ederer 2025) — "
                f"단일값 {iep_lit:g} 판정은 취약하다. 이 pH({ph:g})에서는 "
                f"{', '.join(flips)}로 부호가 뒤집힌다(기준부호 '{sign}')")
        else:
            notes.append(
                f"CeO2 실측범위(Ederer 2025) {lo:g}~{hi:g}pH 전체에서 이 pH({ph:g})는 "
                f"부호 '{sign}'로 안정적이다")

    notes.append("⚠ IEP는 벌크 분말/유리 표면값(Brugnoli 2023/Ederer 2025/Zhang 2024) — "
                 "CMP 후 실제 박막 IEP는 미확보(모듈 §7). 부호(+/0/-)만 판정하고 |ζ| 크기는 "
                 "다루지 않는다.")

    out["abrasive_surface_charge_note"] = f"pack='{rr.pack.name}'. " + "; ".join(notes)
    return out


def _disk_preston_contact_diagnostic(rr: "ResolvedRecipe") -> Dict[str, object]:
    """디스크 접촉통계(η_c, A_f) -> Preston Kp 상대 진단 — MRR 경로와 완전히 독립적인 순수 가시화.

    근거: sim/tier2_physics/disk_preston_contact_decomposition.py::eta_over_af(원본 무수정),
    sim/tier2_physics/gw_pressure_solve.py::local_contact_state, gw_contact.py(둘 다
    _gw_contact_state_diagnostic과 동일 경로 재사용, 원본 무수정), knowledge/materials/
    disk-design-pad-roughness-asperity-relation.md §2.3·§3.4(b). 근거 원본: Sun (2009) PhD
    dissertation, Univ. of Arizona, http://hdl.handle.net/10150/194898, Ch.7.2 Fig.7.14/7.15,
    Eq.7.14.

    ⚠ PROVISIONAL 경고 전파(모듈 docstring 자백 그대로): "K_p ∝ η_c/A_f" 단순 비례식은
    노트가 검증한 유일한 정성적 관계(η_c/A_f가 클수록 K_p/MRR도 크다는 방향성)를 가장
    단순한 선형 형태로 옮긴 것일 뿐이다 — 비례상수가 1인지, 지수가 정확히 1인지는 어느
    출처도 회귀하지 않았다. 그래서 이 진단은 preston_coefficient_contact_scaling·
    disk_preston_contact_scaling을 호출하지 않는다(진단만 낼 거면 부를 이유가 없다,
    test_forbidden_functions_never_called이 ast로 기계 고정) — Kp·MRR에 아무것도 곱하지
    않고 η_c/A_f 절대 지표만 노출한다. fragment_contact_separation도 호출하지 않는다 —
    입력 a_f_intrinsic(파편 없는 고유 실접촉면적)이 Recipe·팩·GW 해 어디에도 없어
    지어내면 파편 기여도가 통째로 창작된다.

    η_c(#/m²)=n_contacts/A_n, A_f(=A_r/A_n)는 GW 런타임 해(local_contact_state,
    _gw_contact_state_diagnostic과 동일 5개 패드 파라미터·동일 압력점 rr.pressure_psi
    center 1점)에서 직접 계산한다 — 새 상수를 팩에 박지 않는다. A_f는
    _gw_contact_state_diagnostic이 내는 gw_real_contact_area_ratio와 정확히 같은 값이어야
    한다(같은 문서 안에서 두 진단이 다른 접촉면적을 내면 모순). η_c/A_f 자체는 반드시
    disk_preston_contact_decomposition.py::eta_over_af 원본 함수로 구한다(직접 나눗셈
    재구현 금지).

    scale_factor(=현재/기준 배율)는 항상 None이다 — grep 확인 결과 5팩 어디에도 기준
    디스크 스펙(disk_*_ref류)이 선언돼 있지 않다(disk_gw_ref_grit_count/size는
    _disk_gw_scaling_diagnostic 전용의 별개 그릿-스펙 배율 키이며 이 진단의 기준이 아니다).
    scale_factor = (η/A)/(η/A)_ref는 기준 디스크 조건이 있어야 의미가 있으므로, 임의
    기준을 지어내 배율을 통째로 조작하지 않고 None + 사유로 둔다.

    ⚠ GW 5개 패드 파라미터가 base.yaml 상속이라 5팩 전부 같은 η_c·A_f·η_c/A_f를 낸다 —
    팩별 차이를 시사하면 오해를 준다.

    GW 5개 패드 파라미터(pad_E_star_pa 등)가 팩에 없거나 asperity_height_distribution이
    정확히 "exponential"이 아니면 조용히 None + 스킵사유(지수분포 전제 없이는 GW 해 자체가
    이 노트가 검증한 식과 무관해진다).
    """
    out: Dict[str, object] = {
        "disk_contact_eta_c_m2": None,
        "disk_contact_a_f": None,
        "disk_contact_eta_over_af": None,
        "disk_contact_scale_factor": None,
        "disk_preston_contact_note": None,
    }
    pad_keys = ("pad_E_star_pa", "pad_asperity_radius_m", "pad_height_beta_inv_m",
                "pad_asperity_density_m2", "pad_nominal_area_m2")
    missing = [k for k in pad_keys if not rr.pack.has(k)]
    if missing:
        out["disk_preston_contact_note"] = (
            f"GW 패드 파라미터 미선언({', '.join(missing)}) — 디스크 접촉통계 진단 스킵")
        return out
    dist = rr.p("asperity_height_distribution") if rr.pack.has("asperity_height_distribution") else None
    if dist != "exponential":
        out["disk_preston_contact_note"] = (
            f"asperity_height_distribution={dist!r}(exponential 아님) — GW 지수분포 전제가 "
            "깨져 η_c·A_f 계산 스킵(지어내지 않음)")
        return out
    try:
        import gw_pressure_solve as GWP   # sim/tier2_physics (1바이트도 수정 안 함)
        import disk_preston_contact_decomposition as DPC   # sim/tier2_physics (원본 무수정)
        E_star = rr.p("pad_E_star_pa")
        R = rr.p("pad_asperity_radius_m")
        # ⚠ 단위: 팩 키는 스케일 1/β [m], 모듈이 받는 인자는 감쇠율 β [1/m]. 역수 변환
        # 필수(미변환 시 d가 21.6 km로 풀린 전례, _gw_contact_state_diagnostic 주석 참조).
        beta = 1.0 / rr.p("pad_height_beta_inv_m")
        eta = rr.p("pad_asperity_density_m2")
        A_n = rr.p("pad_nominal_area_m2")
        P_center = rr.pressure_psi * PSI_TO_PA
        state = GWP.local_contact_state(P_center, A_n, beta, eta, E_star, R)
        eta_c = state["n_contacts"] / A_n
        a_f = state["contact_area_fraction"]
        eta_af = DPC.eta_over_af(eta_c, a_f)
    except Exception as e:
        out["disk_preston_contact_note"] = f"디스크 접촉통계 진단 실패({e}) — None으로 둠"
        return out

    out["disk_contact_eta_c_m2"] = float(eta_c)
    out["disk_contact_a_f"] = float(a_f)
    out["disk_contact_eta_over_af"] = float(eta_af)

    out["disk_preston_contact_note"] = (
        f"pack='{rr.pack.name}'(GW 파라미터 base.yaml 상속 — 5팩 전부 동일값). "
        f"η_c={eta_c:.6e} #/m²(=n_contacts/A_n, GW 런타임 해 P={rr.pressure_psi:g}psi center "
        "1점, _gw_contact_state_diagnostic과 동일 경로 재사용), "
        f"A_f={a_f:.6e}(=A_r/A_n, _gw_contact_state_diagnostic의 gw_real_contact_area_ratio와 "
        f"동일 값), η_c/A_f={eta_af:.6e}"
        "(disk_preston_contact_decomposition.py::eta_over_af, Sun 2009 Ch.7.2 Eq.7.14 정의). "
        "⚠ PROVISIONAL: K_p ∝ η_c/A_f 선형가정(비례상수·지수 모두 미검증)은 노트 §3.4(b)/§5가 "
        "확인한 방향성(η_c/A_f 클수록 K_p/MRR도 큼)만 신뢰하고, 캘리브레이션 없이 정량 예측에 "
        "쓰면 안 된다(모듈 자백 그대로) — 그래서 이 진단은 Kp·MRR에 아무것도 곱하지 않는다. "
        "기준 디스크 스펙(disk_*_ref류) 팩 미선언 — disk_contact_scale_factor는 지어내지 않고 "
        "None으로 둔다.")
    return out


def _conditioner_pcr_aging_diagnostic(rr: "ResolvedRecipe") -> Dict[str, object]:
    """컨디셔너 디스크 노화에 따른 Pad Cut Rate(PCR) 감쇠 진단 — MRR 경로와 완전히 독립.

    근거: sim/tier2_physics/conditioner_pcr_decay.py::pcr_decay·calibrate_tau_from_anchor
    (원본 무수정). 앵커는 Entegris Inc. application note(4435-7548ENT-1213)가 서술하는
    "50시간 사용된 디스크의 PCR이 초기값의 16%로 하락"인데, 이 문서 자체는 그 수치를
    **Palmgren 2004(CMP-MIC Conf. Proc.)를 재인용한 것이고 원문은 미확보**다(모듈
    docstring·EVIDENCE-RULES 판정#14). 이 2차 인용 성격을 note에 항상 명시한다.

    ⚠ **여기서 내보내는 것은 `pcr_decay` 하나뿐이다.** 같은 모듈의
    `simulate_conditioned_wear()`(패드 asperity 재생항 C1_cond*sqrt(z0-z))는 등록하지
    않는다 — 그 함수형·계수는 문헌식이 아니라 fab-sim이 세운 최소 확장 가정이고, 모듈
    self-test 스스로 "방향(정성적 순위)만 검증, 정량 미보증"이라 자백한다. 근거 없는
    수치를 제품 출력으로 내보내지 않는다.

    ⚠ **이중 계상 아님, 가시화임.** sim/factors.py::_f_gamma가 이미 `cond_disk_usage_hours`가
    있을 때 이 모듈의 `pcr_decay`를 호출해 PCR aging 배수 A=pcr_now/pcr_ref를 Γ(컨디셔닝
    부하, MRR 경로)에 곱하고 있다(gamma-conditioning-load-confidence-basis.md §3). 이 진단
    필드는 Γ가 내부적으로 이미 소비 중인 그 값을 사용자에게 보여주는 것이지 새 물리가
    아니다 — **MRR에 다시 곱하지 않는다.**

    입력: `cond_disk_usage_hours`(디스크 사용시간) + `pad_pcr_anchor_hours`/
    `pad_pcr_anchor_ratio`(팩에 선언된 앵커점 — 모듈 하드코딩 ENTEGRIS_ANCHOR_* 상수 대신
    팩 값으로 tau를 역산해, 이 진단이 팩이 선언한 값과 항상 정합되게 한다). 셋 중 하나라도
    팩에 없으면 지어내지 않고 스킵(현재 5팩은 세 키 모두 선언돼 있어 항상 계산되지만,
    `cond_disk_usage_hours=0.0`이 기준값이라 배수는 항상 1.0 — 감쇠 없음이 정상이다.
    사용자가 이 값을 올렸을 때만 진단이 살아난다).
    """
    out: Dict[str, object] = {"conditioner_pcr_aging_ratio": None,
                              "conditioner_pcr_tau_hours": None,
                              "conditioner_disk_usage_hours": None,
                              "conditioner_pcr_note": None}
    need = ("cond_disk_usage_hours", "pad_pcr_anchor_hours", "pad_pcr_anchor_ratio")
    missing = [k for k in need if not rr.pack.has(k)]
    if missing:
        out["conditioner_pcr_note"] = (
            f"⚠ 컨디셔너 PCR 노화 진단 스킵 — 팩에 없음: {', '.join(missing)}")
        return out
    try:
        import conditioner_pcr_decay as CPD   # sim/tier2_physics (1바이트도 수정 안 함)
        t_hours = float(rr.pack.get("cond_disk_usage_hours"))
        anchor_hours = float(rr.pack.get("pad_pcr_anchor_hours"))
        anchor_ratio = float(rr.pack.get("pad_pcr_anchor_ratio"))
        tau = CPD.calibrate_tau_from_anchor(anchor_hours, anchor_ratio)
        ratio = CPD.pcr_decay(t_hours, 1.0, tau)
    except Exception as e:
        out["conditioner_pcr_note"] = f"⚠ 컨디셔너 PCR 노화 계산 실패({e}) — None으로 둠"
        return out
    out["conditioner_pcr_aging_ratio"] = float(ratio)
    out["conditioner_pcr_tau_hours"] = float(tau)
    out["conditioner_disk_usage_hours"] = t_hours
    out["conditioner_pcr_note"] = (
        f"컨디셔너 디스크 사용시간 t={t_hours:.2f}h → PCR/PCR0={ratio:.4f}(τ={tau:.2f}h, "
        f"앵커 {anchor_hours:.0f}h→{anchor_ratio:.2f} 역산). τ는 Entegris 백서가 재인용한 "
        f"Palmgren 2004(원문 미확보, 2차 인용, EVIDENCE-RULES 판정#14) 기반 — 정량 신뢰도가 "
        f"원문 미확보만큼 낮다. sim/factors.py::_f_gamma가 이미 같은 함수로 이 배수를 MRR "
        f"경로(Γ)에 반영 중이다 — 이 필드는 그 내부값의 가시화이며 새 물리가 아니다. "
        f"MRR에 다시 곱하지 않는다. t=0(신품)에서는 배수=1.0(감쇠 없음)이 기준조건이고 "
        f"정상이다.")
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


def _blanket_rate_transient_diagnostic(rr: "ResolvedRecipe") -> Dict[str, object]:
    """블랭킷 Cu 순간 포화속도 a1 대비 평균 rate r_avg(t)의 과소평가 — MRR 경로와 완전히 독립적인 순수 가시화.

    근거: sim/tier2_physics/blanket_rate_transfer.py::blanket_rate_average(원본 무수정,
    eq.3.52), knowledge/cmp/npw-ptw-transfer-rules-quantitative.md §3·§6 verify (B)
    (Tugbawa 2002, MIT EECS PhD thesis, dspace.mit.edu/handle/1721.1/8083, 표 3.3).

    모듈 docstring의 미등록 사유("Recipe에 시간축 스키마가 없다")는 **역방향** fit_blanket_rate
    (실측 (t, 제거량) 시계열로 a1/a2/τ를 역추정)에만 해당한다. 순방향 eq.3.52는 이 런의
    rr.time_s 하나만 있으면 계산되므로 그 범위에서만 등록한다. fit_blanket_rate는 호출하지
    않는다(test_blanket_rate_transient_diagnostic.py가 ast로 기계 고정).

    상수(a1, a2, τ)는 표 3.3의 **4실험 값만** 쓴다(지어내지 않음, 노트 §3/§6이 정본).
    4실험은 공정조건(압력·rpm)이 서로 달라 대표값(평균)을 내지 않고 **min~max 범위**로만
    보고한다(EVIDENCE-RULES: 상반된/분산된 관측을 평균내지 않는다).

    적용 대상은 **블랭킷 Cu**로 제한한다(rr.film == "cu", 판정#34: 팩 이름이 아니라 데이터
    필드로 판별). 표 3.3은 Cu 실측이라 다른 막질에 전이할 근거가 없다.

    팩 기본 운전점(3.0 psi, 55 rpm)은 표 3.3의 어느 실험(2~5 psi, 43~75 rpm)과도 일치하지
    않는다 — 내삽·보간하지 않고 값은 범위로 내되, note에 운전점 불일치 경고를 항상 싣는다
    (조용한 clamp·보간 금지).

    t<=0이면 eq.3.52가 정의되지 않아(AR(t)/t) 스킵한다.
    """
    out: Dict[str, object] = {
        "blanket_transient_avg_to_inst_ratio_range": None,
        "blanket_transient_underestimate_pct_range": None,
        "blanket_transient_note": None,
    }
    if rr.film != "cu":
        out["blanket_transient_note"] = (
            f"Cu 계 아님(film='{rr.film}') — Tugbawa 2002 표 3.3은 블랭킷 Cu 실측이라 "
            f"다른 막질에 전이할 근거가 없어 스킵")
        return out
    t = rr.time_s
    if t <= 0:
        out["blanket_transient_note"] = (
            f"time_s={t:g} <= 0 — eq.3.52 평균 rate r_avg(t)=AR(t)/t가 t>0에서만 정의돼 스킵")
        return out
    try:
        import blanket_rate_transfer as BRT   # sim/tier2_physics (1바이트도 수정 안 함)
    except Exception as e:
        out["blanket_transient_note"] = f"blanket_rate_transfer 로드 실패({e}) — None으로 둠"
        return out
    # (Tugbawa 2002) 표 3.3, knowledge/cmp/npw-ptw-transfer-rules-quantitative.md §3/§6:
    # a1[Å/s], a2[Å], tau[s], 압력[psi], rpm — 노트 원문이 정본
    table_3_3 = {
        1: (249.5, 3986.6, 16.4, 5.0, 63.0),
        2: (120.0, 924.0, 9.71, 2.0, 43.0),
        3: (159.0, 1176.0, 7.7, 4.0, 75.0),
        4: (239.6, 1424.0, 6.3, 5.0, 63.0),
    }
    ratios = []
    for a1, a2, tau, _p_psi, _rpm in table_3_3.values():
        r_avg = BRT.blanket_rate_average(t, a1, a2, tau)
        ratios.append(r_avg / a1)
    ratio_lo, ratio_hi = min(ratios), max(ratios)
    pct_lo, pct_hi = (1.0 - ratio_hi) * 100.0, (1.0 - ratio_lo) * 100.0
    out["blanket_transient_avg_to_inst_ratio_range"] = (ratio_lo, ratio_hi)
    out["blanket_transient_underestimate_pct_range"] = (pct_lo, pct_hi)
    exp_str = ", ".join(f"{p_psi:g}psi/{rpm:g}rpm" for _, _, _, p_psi, rpm in table_3_3.values())
    out["blanket_transient_note"] = (
        f"t={t:g}s에서 r_avg(t)/a1 문헌 4실험(표 3.3) 범위 {ratio_lo:.4f}~{ratio_hi:.4f} "
        f"(60 s류 관행 평균이 포화 순간속도 a1 대비 {pct_lo:.1f}~{pct_hi:.1f}% 낮음). "
        f"⚠ 이 팩의 운전점(pressure_psi={rr.pressure_psi:g}, rpm_platen={rr.rpm_platen:g})은 "
        f"표 3.3 4실험({exp_str}) 중 어느 것과도 일치하지 않아 이 범위는 오더 참고용이다 — "
        f"내삽·보간하지 않는다. 우리 팩의 kp_m_per_pa도 문헌 평균 MRR에서 역산된 값이라 "
        f"같은 편향을 상속할 수 있다.")
    return out


def _conditioner_disk_diagnostic(rr: "ResolvedRecipe") -> Dict[str, object]:
    """컨디셔너 디스크 장비팩 로드 여부 진단 — MRR 경로와 완전히 독립.

    백로그 ㉺(장비팩 스키마 신설, S12-RESIDUAL-JUDGMENT.md §2-2) 회차의 스키마만
    세우는 단계라, 팩이 로드돼도 어떤 물리 계산에도 쓰지 않는다. Recipe.conditioner_disk가
    None이면(지금까지의 기본 동작) 둘 다 None — MRR·notes 모두 이전과 완전히 동일하다.
    """
    out: Dict[str, object] = {"conditioner_disk_pack": None, "conditioner_disk_note": None}
    if rr.base.conditioner_disk is None:
        return out
    pack = rr.equipment_pack
    out["conditioner_disk_pack"] = pack.name
    out["conditioner_disk_note"] = (
        f"장비팩 '{pack.name}' 로드됨(값 {len(pack.params)}개) — "
        "스키마 신설 회차라 어떤 물리 계산에도 사용하지 않는다(진단 표시 전용)")
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
    if rr.wafer == "PTW" and model not in _PATTERN_MODELS:
        notes.append("PTW인데 패턴 모델을 쓰지 않았다 — "
                     "model='tier1.pattern_density_effective_pressure'(Sorooshian 2005 실측표, "
                     "판정#65 권장) 또는 'tier1.pattern_density'(Boning 1/ρ)로 실행하라. "
                     "지금 값은 NPW 등가")
    # 윤활 레짐 진단 — MRR 경로와 완전히 독립. 팩에 슬러리 점도·패드 Ra가 없으면 조용히 None.
    lube = _lubrication_diagnostics(rr)
    if lube.get("_note"):
        notes.append(lube["_note"])
    elif lube["lubrication_regime"] is not None:
        notes.append("윤활 레짐 진단(So·λ·COF)은 λ≈So 근사(δeff≈σ 가정)이며 "
                     "COF 절대값은 정성적 오더 추정, 실측 캘리브레이션 필요 "
                     "(knowledge/physics/cmp-lubrication-regimes.md §5,§7)")
        if lube.get("cof_consistency_note"):
            notes.append(lube["cof_consistency_note"])
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
    # GW 역문제 런타임 해(local_contact_state) 진단 — MRR 경로와 완전히 독립. GW 패드
    # 파라미터 없으면 조용히 None. real_contact_area_ratio 정적 팩값과의 괴리를 노출한다.
    gw_state = _gw_contact_state_diagnostic(rr)
    if gw_state["gw_contact_regime_note"]:
        notes.append(gw_state["gw_contact_regime_note"])
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
    # 그루브 마모 -> 슬러리 유동 상태 진단 — MRR 경로와 완전히 독립.
    # pad_cut_rate_um_per_h 팩 미선언이면 조용히 None(현재 5팩 전부 미선언).
    pad_groove_flow = _pad_groove_wear_flow_diagnostic(rr)
    if pad_groove_flow["pad_groove_flow_note"]:
        notes.append(pad_groove_flow["pad_groove_flow_note"])
    # 억제제 Langmuir 피복률 포화도 진단 — MRR 경로와 완전히 독립(가시화 전용).
    # inhibitor_mM 미선언 팩(산화막 계 3팩)은 조용히 None + 스킵사유.
    inhib_sat = _inhibitor_saturation_diagnostic(rr)
    if inhib_sat["inhibitor_saturation_note"]:
        notes.append(inhib_sat["inhibitor_saturation_note"])
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
    # 마찰열 ΔT_ss → Arrhenius 화학반응속도 배율 진단 — MRR 경로와 완전히 독립. Ea 미보고
    # 막질(sic_4h·w)이거나 theta_ss·platen_coolant_temp_c 중 하나라도 없으면 조용히 None.
    thermal_chem = _thermal_chemical_diagnostic(rr, theta_ss)
    if thermal_chem["thermal_chemical_note"]:
        notes.append(thermal_chem["thermal_chemical_note"])
    # 컨디셔너 디스크 노화 PCR(t) 감쇠 진단 — MRR 경로와 완전히 독립(가시화, 새 물리 아님).
    # cond_disk_usage_hours·pad_pcr_anchor_hours·pad_pcr_anchor_ratio 중 하나라도 팩에
    # 없으면 조용히 None(현재 5팩은 전부 선언돼 있어 usage=0 -> 배수=1.0으로 항상 계산됨).
    cond_pcr = _conditioner_pcr_aging_diagnostic(rr)
    if cond_pcr["conditioner_pcr_note"]:
        notes.append(cond_pcr["conditioner_pcr_note"])
    # 패드 유효 탄성률 E'(T) 온도의존 연화 진단 — MRR 경로와 완전히 독립(진단 전용).
    # pad_dma_id 팩 미선언이면 조용히 None(현재 5팩 전부 미선언이라 항상 None이 정상).
    pad_visco = _pad_viscoelastic_diagnostic(rr, theta_ss)
    if pad_visco["pad_viscoelastic_note"]:
        notes.append(pad_visco["pad_viscoelastic_note"])
    # 패드 공정 하중주파수 역진단(Maxwell 점탄성) — MRR 경로와 완전히 독립(진단 전용).
    # pad_relaxation_time_s 팩 미선언이면 De는 조용히 None(현재 전 팩 미선언이라 항상
    # None이 정상). ω_asperity는 GW 패드 파라미터+exponential 분포 선언 시 산출된다
    # (2026-09-16 정정, 함수 독스트링 참조).
    pad_loading_freq = _pad_loading_frequency_diagnostic(rr)
    if pad_loading_freq["pad_loading_frequency_note"]:
        notes.append(pad_loading_freq["pad_loading_frequency_note"])
    # 디스크 설계 스펙(N, D) 상대 배율 -> GW 파라미터(Ra, Rpk, λ) 진단 — MRR 경로와
    # 완전히 독립. 기준/대상 디스크 스펙(disk_gw_ref_*/disk_gw_target_*) 팩 미선언이면
    # 조용히 None(현재 5팩 전부 미선언이라 항상 None이 정상).
    disk_gw = _disk_gw_scaling_diagnostic(rr)
    if disk_gw["disk_gw_scaling_note"]:
        notes.append(disk_gw["disk_gw_scaling_note"])
    # 단일 연마입자 소성 접촉(plowing) 진단 — MRR 경로와 완전히 독립.
    # film_bulk_hardness_pa 팩 미선언(현재 sti_ceria만 해당)이면 조용히 None.
    particle_contact = _particle_contact_diagnostic(rr)
    if particle_contact["particle_contact_note"]:
        notes.append(particle_contact["particle_contact_note"])
    # 레시피 전이 work function 진단 — MRR 경로와 완전히 독립.
    # sfr_ml_min 팩 미선언이면 조용히 None(현재 5팩 전부 base.yaml 상속이라 항상 값을 낸다).
    recipe_conv = _recipe_conversion_diagnostic(rr)
    if recipe_conv["recipe_conversion_note"]:
        notes.append(recipe_conv["recipe_conversion_note"])
    # Cu dishing 선저항 증가율 진단 — MRR 경로와 완전히 독립. linewidth_um(meta)·
    # remaining_nm(initial_thickness_nm 설정 시에만) 둘 다 없으면 조용히 None
    # (현재 5팩 기본 실행은 linewidth_um 미선언이라 항상 None이 정상).
    elec_r = _electrical_resistance_diagnostic(rr, remaining)
    if elec_r["electrical_resistance_note"]:
        notes.append(elec_r["electrical_resistance_note"])
    # Archard↔Preston 가교 진단 — MRR 경로와 완전히 독립. film_bulk_hardness_pa
    # 팩 미선언이면 조용히 None(현재 5팩 전부 선언돼 있어 항상 값을 낸다).
    tribo = _tribology_archard_diagnostic(rr)
    if tribo["tribology_note"]:
        notes.append(tribo["tribology_note"])
    # 세리아 Ce3+ 산소공공 x·정전인력 진단 — MRR 경로와 완전히 독립. ce3_fraction·
    # abrasive_iep_ph·wafer_iep_ph 세 키 모두 이 팩 고유선언이어야 값을 낸다
    # (현재 5팩 중 sti_ceria만 해당, 나머지는 조용히 None).
    ceria_redox = _ceria_redox_diagnostic(rr)
    if ceria_redox["ceria_redox_note"]:
        notes.append(ceria_redox["ceria_redox_note"])
    # 산화물/연마입자 표면전하 부호(IEP) 진단 — MRR 경로와 완전히 독립(가시화 전용).
    # slurry_ph·abrasive 둘 다 5팩 전부에 있어 항상 값을 낸다(문헌표에 없는 연마입자면
    # 조용히 None). abrasive_iep_ph 팩 선언과 문헌표 값을 대조해 괴리를 노출한다.
    abrasive_charge = _abrasive_surface_charge_diagnostic(rr)
    if abrasive_charge["abrasive_surface_charge_note"]:
        notes.append(abrasive_charge["abrasive_surface_charge_note"])
    # 디스크 접촉통계(η_c, A_f) -> Preston Kp 상대 진단 — MRR 경로와 완전히 독립(진단 전용,
    # PROVISIONAL 선형가정이라 절대 Kp·MRR에 곱하지 않는다). GW 패드 파라미터 없거나
    # exponential 분포가 아니면 조용히 None.
    disk_preston = _disk_preston_contact_diagnostic(rr)
    if disk_preston["disk_preston_contact_note"]:
        notes.append(disk_preston["disk_preston_contact_note"])
    # 블랭킷 Cu 순간 포화속도 a1 대비 평균 rate 과소평가 진단 — MRR 경로와 완전히 독립
    # (진단 전용). film != "cu"이거나 time_s<=0이면 조용히 None.
    blanket_transient = _blanket_rate_transient_diagnostic(rr)
    if blanket_transient["blanket_transient_note"]:
        notes.append(blanket_transient["blanket_transient_note"])
    # 컨디셔너 디스크 장비팩 로드 진단 — MRR 경로와 완전히 독립. conditioner_disk가
    # None이면(기본값) 조용히 None(현재 전체 레시피가 기본값이라 항상 None이 정상).
    cond_disk = _conditioner_disk_diagnostic(rr)
    if cond_disk["conditioner_disk_note"]:
        notes.append(cond_disk["conditioner_disk_note"])
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
                       cof_qf_used=lube.get("cof_qf_used"),
                       cof_estimate_vs_qf_ratio=lube.get("cof_estimate_vs_qf_ratio"),
                       cof_consistency_note=lube.get("cof_consistency_note"),
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
                       gw_solved_separation_m=gw_state["gw_solved_separation_m"],
                       gw_real_contact_area_ratio=gw_state["gw_real_contact_area_ratio"],
                       gw_real_contact_pressure_pa=gw_state["gw_real_contact_pressure_pa"],
                       gw_static_pack_ratio_deviation=gw_state["gw_static_pack_ratio_deviation"],
                       gw_plasticity_index=gw_state["gw_plasticity_index"],
                       gw_contact_regime_note=gw_state["gw_contact_regime_note"],
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
                       pad_groove_residual_fraction=pad_groove_flow["pad_groove_residual_fraction"],
                       pad_groove_wear_stage=pad_groove_flow["pad_groove_wear_stage"],
                       pad_groove_conductance_ratio=pad_groove_flow["pad_groove_conductance_ratio"],
                       pad_groove_flow_note=pad_groove_flow["pad_groove_flow_note"],
                       inhibitor_theta_equilibrium=inhib_sat["inhibitor_theta_equilibrium"],
                       inhibitor_theta_headroom=inhib_sat["inhibitor_theta_headroom"],
                       inhibitor_conc_discrimination=inhib_sat["inhibitor_conc_discrimination"],
                       inhibitor_saturation_note=inhib_sat["inhibitor_saturation_note"],
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
                       thermal_chemical_rate_ratio=thermal_chem["thermal_chemical_rate_ratio"],
                       thermal_chemical_ea_kj_mol=thermal_chem["thermal_chemical_ea_kj_mol"],
                       thermal_chemical_film=thermal_chem["thermal_chemical_film"],
                       thermal_chemical_note=thermal_chem["thermal_chemical_note"],
                       conditioner_pcr_aging_ratio=cond_pcr["conditioner_pcr_aging_ratio"],
                       conditioner_pcr_tau_hours=cond_pcr["conditioner_pcr_tau_hours"],
                       conditioner_disk_usage_hours=cond_pcr["conditioner_disk_usage_hours"],
                       conditioner_pcr_note=cond_pcr["conditioner_pcr_note"],
                       pad_modulus_at_temp_mpa=pad_visco["pad_modulus_at_temp_mpa"],
                       pad_modulus_ref_25c_mpa=pad_visco["pad_modulus_ref_25c_mpa"],
                       pad_modulus_softening_ratio=pad_visco["pad_modulus_softening_ratio"],
                       pad_viscoelastic_note=pad_visco["pad_viscoelastic_note"],
                       disk_gw_ra_relative=disk_gw["disk_gw_ra_relative"],
                       disk_gw_rpk_relative=disk_gw["disk_gw_rpk_relative"],
                       disk_gw_lambda_relative=disk_gw["disk_gw_lambda_relative"],
                       disk_gw_scaling_note=disk_gw["disk_gw_scaling_note"],
                       particle_load_n=particle_contact["particle_load_n"],
                       particle_indent_depth_nm=particle_contact["particle_indent_depth_nm"],
                       particle_plow_area_nm2=particle_contact["particle_plow_area_nm2"],
                       particle_contact_note=particle_contact["particle_contact_note"],
                       recipe_work_function=recipe_conv["recipe_work_function"],
                       recipe_wf_vs_ild_ref=recipe_conv["recipe_wf_vs_ild_ref"],
                       recipe_conversion_note=recipe_conv["recipe_conversion_note"],
                       electrical_dishing_delta_r_pct=elec_r["electrical_dishing_delta_r_pct"],
                       electrical_dishing_r_dish_um=elec_r["electrical_dishing_r_dish_um"],
                       electrical_resistance_note=elec_r["electrical_resistance_note"],
                       archard_wear_coefficient=tribo["archard_wear_coefficient"],
                       archard_reference_k=tribo["archard_reference_k"],
                       archard_order_ratio=tribo["archard_order_ratio"],
                       tribology_hersey_number=tribo["tribology_hersey_number"],
                       tribology_note=tribo["tribology_note"],
                       pad_loading_omega_rot_rad_s=pad_loading_freq["pad_loading_omega_rot_rad_s"],
                       pad_loading_omega_asperity_rad_s=pad_loading_freq["pad_loading_omega_asperity_rad_s"],
                       pad_relaxation_time_threshold_s=pad_loading_freq["pad_relaxation_time_threshold_s"],
                       pad_deborah_number=pad_loading_freq["pad_deborah_number"],
                       pad_loading_frequency_note=pad_loading_freq["pad_loading_frequency_note"],
                       ceria_oxygen_vacancy_x=ceria_redox["ceria_oxygen_vacancy_x"],
                       ceria_electrostatic_attraction=ceria_redox["ceria_electrostatic_attraction"],
                       ceria_redox_note=ceria_redox["ceria_redox_note"],
                       abrasive_surface_charge_sign=abrasive_charge["abrasive_surface_charge_sign"],
                       abrasive_iep_literature_ph=abrasive_charge["abrasive_iep_literature_ph"],
                       abrasive_iep_pack_deviation_ph=abrasive_charge["abrasive_iep_pack_deviation_ph"],
                       abrasive_surface_charge_note=abrasive_charge["abrasive_surface_charge_note"],
                       disk_contact_eta_c_m2=disk_preston["disk_contact_eta_c_m2"],
                       disk_contact_a_f=disk_preston["disk_contact_a_f"],
                       disk_contact_eta_over_af=disk_preston["disk_contact_eta_over_af"],
                       disk_contact_scale_factor=disk_preston["disk_contact_scale_factor"],
                       disk_preston_contact_note=disk_preston["disk_preston_contact_note"],
                       blanket_transient_avg_to_inst_ratio_range=blanket_transient[
                           "blanket_transient_avg_to_inst_ratio_range"],
                       blanket_transient_underestimate_pct_range=blanket_transient[
                           "blanket_transient_underestimate_pct_range"],
                       blanket_transient_note=blanket_transient["blanket_transient_note"],
                       conditioner_disk_pack=cond_disk["conditioner_disk_pack"],
                       conditioner_disk_note=cond_disk["conditioner_disk_note"],
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
