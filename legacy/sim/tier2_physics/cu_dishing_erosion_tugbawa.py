"""Cu CMP 오버폴리시 dishing/erosion — Hooke 압력분배 닫힌 시간해 (Tugbawa 2002).

담당 에이전트: film-cu (Lv2-1)
근거 지식노트: knowledge/cmp/cu-dishing-erosion-density-step-height-model-tugbawa.md §2·§3.2·§3.3·§6·§7

────────────────────────────────────────────────────────────────────
`sim/tier1_empirical/pattern_density.py::steady_state_dishing`는 유전체 쪽 기울기를 자유 파라미터
b로 두지만, Tugbawa 2002 eq 3.33은 그 기울기를 Φ/((1−Φ)·d_max)로 **고정**한다(압력 보존에서
유도, 자유 파라미터가 아님). 이 모듈은 그 닫힌 해(eq 3.37–3.42, 3.46, 3.49)를 그대로 구현한다.
기존 `steady_state_dishing`은 건드리지 않는다 — 대체가 아니라 공존한다.

⚠ 캘리브레이션 상수 경고: `cu_overpolish_dishing_erosion`의 기본 파라미터(Table 3.9 "#1 Stacked
pad, ψ 포함" 행: B=333.0 Å, α₂=0.303, β₂=0.259, s_l=100 µm, C=3.04, s_c=22.5 µm)는 Tugbawa의
**특정 장비(Mirra)·특정 슬러리(EPC-5001)·특정 마스크(MIT-SEMATECH 854)**에서 추출된 값이다.
다른 장비/슬러리/마스크 레이아웃에 그대로 쓰면 안 된다 — 새 실측이 있으면 params= 로 갈아끼운다.
r_cu·r_ox(블랭킷 유효 제거율)는 이 모듈이 기본값을 갖지 않는다 — 호출자가 실측/레시피값을
명시적으로 줘야 한다(조용한 문헌 상수 보간·외삽 금지).

단위: r_cu, r_ox는 Å/s, d_max·D_ss·dishing/erosion 중간계산은 Å, w·s(선폭·스페이스)는 µm
(eq 3.46의 w₀=s₀=1 µm 정규화가 암묵적으로 들어있다 — w, s를 µm로 바로 넣으면 된다).
공개 API `cu_overpolish_dishing_erosion()`의 반환값은 프로젝트 관례(WaferResult의 `_nm` 필드)에
맞춰 **nm**로 변환해서 낸다(내부 Å 값 / 10).

정적식각(SER) 하한은 이 모듈의 범위가 아니다(노트 §6, 별도 후속 P2 — film-cu Pourbaix/SER 연결).
"""
from __future__ import annotations

import math
from typing import Dict, List, Optional

# Tugbawa 2002 Table 3.9 "#1 Stacked pad, ψ 포함" — Mirra·EPC-5001·MIT-SEMATECH 854 마스크 전용값
DEFAULT_PARAMS: Dict[str, float] = {
    "B": 333.0,       # Å (eq 3.46)
    "alpha2": 0.303,  # 선폭 지수
    "beta2": 0.259,   # 스페이스 지수
    "s_l": 100.0,     # µm, 스페이스 포화 length scale
    "C": 3.04,        # 엣지라운딩 진폭 (eq 3.49)
    "s_c": 22.5,      # µm, 엣지라운딩 length scale
}

_CALIBRATION_WARNING = (
    "⚠ Table 3.9 캘리브레이션값 — 다른 장비/슬러리에 그대로 쓰면 안 됨 "
    "(Tugbawa 2002 Mirra·EPC-5001·MIT-SEMATECH 854 마스크 전용, params=로 교체 가능)"
)
_OVERPOLISH_WARNING = "⚠ 모델 과대예측 영역(§4.2) — 장거리 높이차 항 미포함, 캘리브레이션 데이터 밖"


def steady_state_dishing_tugbawa(r_cu: float, r_ox: float, phi_cu: float, d_max: float) -> float:
    """정상상태 dishing D_ss (Tugbawa 2002 eq 3.39).

    D_ss = d_max·(r_cu − r_ox)·(1−Φ_cu) / [r_cu(1−Φ_cu) + r_ox·Φ_cu]
    자유 파라미터 없음 — 유전체 기울기 Φ/((1−Φ)·d_max)가 압력 보존에서 고정된 결과.
    """
    return d_max * (r_cu - r_ox) * (1.0 - phi_cu) / (r_cu * (1.0 - phi_cu) + r_ox * phi_cu)


def tau3(r_cu: float, r_ox: float, phi_cu: float, d_max: float) -> float:
    """dishing 포화 시간상수 τ₃ (Tugbawa 2002 eq 3.40), 단위 초(r_cu·r_ox가 Å/s일 때)."""
    return d_max * (1.0 - phi_cu) / (r_cu * (1.0 - phi_cu) + r_ox * phi_cu)


def erosion_rate_Y1(r_cu: float, r_ox: float, phi_cu: float) -> float:
    """정상상태 erosion 속도 Y₁ (Tugbawa 2002 eq 3.41) — Φ_cu에 단조증가."""
    return r_cu * r_ox / (r_cu * (1.0 - phi_cu) + r_ox * phi_cu)


def _erosion_rate_Y2(r_cu: float, r_ox: float, phi_cu: float) -> float:
    """eq 3.42 — dishing_time_evolution/erosion_time_evolution의 전이항 계수. 공개 API 아님."""
    return r_ox * phi_cu / (r_cu * (1.0 - phi_cu) + r_ox * phi_cu)


def d_max_from_linewidth_space(w: float, s: float, B: float, alpha2: float, beta2: float,
                               s_l: float = 100.0) -> float:
    """d_max(w, s) 경험식 (Tugbawa 2002 eq 3.46), w·s 단위 µm, w₀=s₀=1 µm 암묵.

    d_max = B·w^α₂·s^β₂   (0 ≤ s < s_l)
          = B·w^α₂·s_l^β₂ (s ≥ s_l)   ← 스페이스 포화(dishing length scale)
    """
    s_eff = min(s, s_l)
    return B * (w ** alpha2) * (s_eff ** beta2)


def edge_rounding_psi(s: float, C: float, s_c: float) -> float:
    """엣지 라운딩 승수 ψ(s) (Tugbawa 2002 eq 3.49) — 좁은 스페이스일수록 r_ox 증폭.

    ψ(s) = C·e^(−s/s_c) + 1,  s→∞에서 1로 수렴(라운딩 효과 소멸).
    """
    return C * math.exp(-s / s_c) + 1.0


def dishing_time_evolution(t: float, t3: float, d2: float, D_ss: float, tau3_s: float) -> float:
    """D_cu(t) (Tugbawa 2002 eq 3.37) — d₂(배리어클리어 시 dishing)에서 D_ss로 지수 포화."""
    return d2 * math.exp(-(t - t3) / tau3_s) + D_ss * (1.0 - math.exp(-(t - t3) / tau3_s))


def erosion_time_evolution(t: float, t3: float, Y1: float, Y2: float, D_ss: float, d2: float,
                           tau3_s: float) -> float:
    """E_ox(t) (Tugbawa 2002 eq 3.38) — 정상상태 뒤 Y₁ 기울기의 선형 증가 + 초기 전이항."""
    return Y1 * (t - t3) + Y2 * (D_ss - d2) * (math.exp(-(t - t3) / tau3_s) - 1.0)


def cu_overpolish_dishing_erosion(r_cu: float, r_ox_measured: float, phi_cu: float,
                                  w: float, s: float, t_overpolish: float,
                                  params: Optional[Dict[str, float]] = None) -> Dict[str, object]:
    """Cu 오버폴리시 dishing/erosion 종합 계산 — d_max·ψ(s)·D_ss·τ₃까지 한 번에.

    입력: r_cu·r_ox_measured(Å/s, 블랭킷 유효 제거율, 호출자가 명시), phi_cu(유효 Cu 밀도 Φ),
    w·s(선폭·스페이스, µm), t_overpolish(오버폴리시 경과시간, 초 — stage-three 시작을
    t3=0으로 두고 그 시점 dishing d2=0으로 가정: 배리어클리어 단계 데이터가 이 모듈 범위 밖이라
    노트 §4.4/§5가 말하는 stage-two 연계는 별도 확장 대상).

    params 생략 시 Table 3.9 "#1 Stacked pad, ψ 포함" 캘리브레이션값(DEFAULT_PARAMS) 사용 —
    다른 장비/슬러리에는 그대로 쓰면 안 된다(모듈 docstring·notes 경고 참조).

    반환: {"dishing_nm", "erosion_nm", "d_ss_nm", "tau3_s", "notes": [...]}  (nm 단위, 내부 Å/10)
    """
    used_default = params is None
    p = dict(DEFAULT_PARAMS) if params is None else dict(params)
    s_l = p.get("s_l", 100.0)

    d_max = d_max_from_linewidth_space(w, s, p["B"], p["alpha2"], p["beta2"], s_l)
    r_ox_eff = r_ox_measured * edge_rounding_psi(s, p["C"], p["s_c"])

    D_ss = steady_state_dishing_tugbawa(r_cu, r_ox_eff, phi_cu, d_max)
    tau3_s = tau3(r_cu, r_ox_eff, phi_cu, d_max)
    Y1 = erosion_rate_Y1(r_cu, r_ox_eff, phi_cu)
    Y2 = _erosion_rate_Y2(r_cu, r_ox_eff, phi_cu)

    dishing_A = dishing_time_evolution(t_overpolish, 0.0, 0.0, D_ss, tau3_s)
    erosion_A = erosion_time_evolution(t_overpolish, 0.0, Y1, Y2, D_ss, 0.0, tau3_s)

    notes: List[str] = []
    if used_default:
        notes.append(_CALIBRATION_WARNING)
    if erosion_A > 3000.0 or phi_cu > 0.95:
        notes.append(_OVERPOLISH_WARNING)

    return {
        "dishing_nm": dishing_A / 10.0,
        "erosion_nm": erosion_A / 10.0,
        "d_ss_nm": D_ss / 10.0,
        "tau3_s": tau3_s,
        "notes": notes,
    }
