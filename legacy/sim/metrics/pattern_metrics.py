"""패턴 지표 라이브러리 — wafer-metrology 에이전트 소유 (엔진 출력 스키마).

근거 노트: `knowledge/cmp/pattern-metrics-dishing-erosion-stepheight.md` (게이트 2종 통과),
`agents/wafer-metrology/PROFILE.md` "구현 요청"(Lv2-2, 신설 [High]).

이 모듈은 프로파일러 1D 스캔(x, z)·광학 두께맵·반경 두께 프로파일을 입력으로 다음을 계산한다:
  step_height_iso5436          — ISO 5436-1형 교정표준 측정법의 최소제곱 스텝하이트(노트 §1.2, §6(C))
  dishing_erosion_from_profile — Cu damascene dishing/erosion, default 기준면=필드 oxide면(Pan 1999식,
                                  노트 §1.1). field_loss가 주어지면 Park 1998식(증착두께 기준) 환산도 병기.
  roa                          — SEMI M77형 Roll-Off Amount. convention 필수(default 없음, 노트 §1.5 §6(D):
                                  "규약 없는 ROA 수치는 비교 불가").
  itrs_allowance               — "10%×배선높이" 판정 규칙(ITRS 2007 Table INTC2a, 노트 §5, §6(A)).
  residual_metal_fraction / remaining_thickness — 잔막의 두 뜻(결함량 vs 연속 잔여두께, 노트 §1.4)을
                                  필드명으로 분리.

고용주의 사내 실측 데이터는 쓰지 않는다 — 공개문헌(ITRS, IBM/SunEdison/Corning 특허, Taylor Hobson)만 근거.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Optional
from numpy.typing import ArrayLike

import numpy as np


# ---------------------------------------------------------------------------
# (1) ISO 5436-1형 스텝하이트
# ---------------------------------------------------------------------------

@dataclass
class StepHeightResult:
    step_height_nm: float
    slope: float
    curvature: Optional[float]
    residual_std: float

    def as_dict(self):
        return asdict(self)


def step_height_iso5436(x: ArrayLike, z: ArrayLike, regions: ArrayLike,
                         exclude_transition_width: Optional[float] = None,
                         remove_curvature: bool = False) -> StepHeightResult:
    """ISO 5436-1형 교정표준 측정법의 최소제곱 스텝하이트(Taylor Hobson, Mills 튜토리얼;
    노트 §1.2, §6(C)).

    모델: Z = a*X + b + h*delta  (delta: regions에서 +1=높은 영역, -1=낮은 영역), step = 2h.
    remove_curvature=True면 2차항(c*X^2)까지 동시 피팅해 기판 곡률을 제거한다(노트 §6 (C'):
    곡률을 제거하지 않으면 단순 직선피팅은 ~10% 자릿수 오차를 낸다).

    exclude_transition_width가 주어지면 각 스텝 경계(delta 부호가 바뀌는 x 위치)로부터
    그 폭 이내의 점을 피팅에서 제외한다(ISO 5436-1 정신: 전이부 인접영역 제외).
    """
    x = np.asarray(x, float)
    z = np.asarray(z, float)
    delta = np.asarray(regions, float)
    if not (x.shape == z.shape == delta.shape):
        raise ValueError("x, z, regions는 같은 길이여야 한다")
    if not np.all(np.isin(delta, (-1.0, 1.0))):
        raise ValueError("regions는 +1(높은 영역)/-1(낮은 영역)만 허용한다")

    mask = np.ones_like(x, dtype=bool)
    if exclude_transition_width is not None and exclude_transition_width > 0:
        boundary_idx = np.flatnonzero(np.diff(delta) != 0)
        boundaries_x = 0.5 * (x[boundary_idx] + x[boundary_idx + 1])
        for bx in boundaries_x:
            mask &= np.abs(x - bx) >= exclude_transition_width

    cols = [x[mask], np.ones(mask.sum()), delta[mask]]
    if remove_curvature:
        cols.insert(1, x[mask] ** 2)
    A = np.column_stack(cols)
    coeffs, *_ = np.linalg.lstsq(A, z[mask], rcond=None)
    if remove_curvature:
        a, c, b, h = coeffs
        curvature = float(c)
    else:
        a, b, h = coeffs
        curvature = None

    fitted = np.sum(A * coeffs, axis=1)  # (avoid A@coeffs: spurious Accelerate BLAS FPE warning on some macOS builds)
    residual_std = float(np.std(z[mask] - fitted, ddof=0))
    return StepHeightResult(step_height_nm=float(2 * h), slope=float(a),
                             curvature=curvature, residual_std=residual_std)


# ---------------------------------------------------------------------------
# (2) Dishing / erosion — Pan 1999식 default, Park 1998식 병기
# ---------------------------------------------------------------------------

@dataclass
class DishingErosionResult:
    dishing_nm: float
    erosion_nm: float
    field_loss_nm: Optional[float]
    total_loss_nm: float
    reference: str
    stage: str

    def as_dict(self):
        return asdict(self)


def dishing_erosion_from_profile(x: ArrayLike, z: ArrayLike,
                                  field_mask: ArrayLike, line_mask: ArrayLike,
                                  array_mask: ArrayLike,
                                  field_loss_nm: Optional[float] = None,
                                  stage: str = "post_clear") -> DishingErosionResult:
    """Cu damascene dishing/erosion — default 기준면은 Pan et al. 1999(CMP-MIC)식:
    field oxide 표면을 0으로 두고, 그 아래로의 함몰량을 dishing(line_mask 최저점 기준)·
    erosion(array_mask 평균 기준)으로 잡는다(노트 §1.1). 총손실 항등식:
    총 Cu 두께손실 = field_loss + erosion + dishing (Pan 1999 Fig.8).

    field_loss_nm(광학 두께계로 별도 측정한 필드 oxide 손실, Park 1998식 계산에 필요)이
    주어지면 reference="as_deposited" 환산값(증착두께 기준, Park 1998식)도 total_loss_nm에
    반영해 함께 낼 수 있도록 field_loss_nm을 결과에 실어 보고한다.

    stage: "pre_clear_step"(클리어 전 잔여 스텝) 또는 "post_clear_dishing"(클리어 후 =
    dishing 그 자체, Pan 1999) — 노트 §1.2. 필수 메타로 그대로 반환한다.
    """
    x = np.asarray(x, float)
    z = np.asarray(z, float)
    field_mask = np.asarray(field_mask, bool)
    line_mask = np.asarray(line_mask, bool)
    array_mask = np.asarray(array_mask, bool)
    if not (field_mask.any() and line_mask.any() and array_mask.any()):
        raise ValueError("field_mask, line_mask, array_mask 모두 최소 1점 필요")

    field_level = float(np.mean(z[field_mask]))
    dishing_nm = field_level - float(np.min(z[line_mask]))
    erosion_nm = field_level - float(np.mean(z[array_mask]))

    reference = "field_oxide"
    total_loss_nm = erosion_nm + dishing_nm
    if field_loss_nm is not None:
        total_loss_nm += field_loss_nm
        reference = "as_deposited"

    return DishingErosionResult(dishing_nm=dishing_nm, erosion_nm=erosion_nm,
                                 field_loss_nm=field_loss_nm, total_loss_nm=total_loss_nm,
                                 reference=reference, stage=stage)


# ---------------------------------------------------------------------------
# (3) ROA — 규약 필수 (노트 §1.5, §6(D): "규약 없는 ROA 수치는 비교 불가")
# ---------------------------------------------------------------------------

ROA_CONVENTIONS = {
    # US10600634 (SunEdison 2020): 300 mm 웨이퍼, R=150mm 기준 반경 비율
    "sunedison_300mm": {"p1_frac": 0.827, "p2_frac": 0.933, "p3_frac": 0.987, "radius_mm": 150.0},
    # US9829310 (Corning 2017): 엣지에서 6mm/3mm 지점 (반경 기준 R-6, R-3, R)
    "edge_3_6mm": {"edge_p1_mm": 6.0, "edge_p2_mm": 3.0, "edge_p3_mm": 0.0},
}


def roa(r: ArrayLike, t: ArrayLike, convention: str) -> float:
    """SEMI M77형 Roll-Off Amount(ROA). convention은 필수 파라미터이며 default가 없다 —
    노트 §1.5·§6(D)가 보인 것처럼 기준점(P1,P2,P3) 규약이 출처마다 달라 같은 프로파일에서도
    값이 수배 차이 나므로, 규약을 명시하지 않은 ROA는 비교 불가능하다.

    P1, P2로 1차 기준선을 피팅해 P3까지 외삽하고, P3에서의 실측값과 기준선의 차이를 ROA로
    반환한다(음수 = 롤오프, 즉 엣지가 기준선보다 낮음).

    convention: "sunedison_300mm" (P1/P2/P3 = 82.7%/93.3%/98.7% of R=150mm) 또는
    "edge_3_6mm" (엣지에서 6mm/3mm/0mm 지점, Corning US9829310).
    """
    if convention not in ROA_CONVENTIONS:
        raise ValueError(
            f"convention은 필수이며 {sorted(ROA_CONVENTIONS)} 중 하나여야 한다 (받음: {convention!r}). "
            "규약 없는 ROA는 정의상 비교 불가(노트 §1.5)."
        )
    r = np.asarray(r, float)
    t = np.asarray(t, float)
    cfg = ROA_CONVENTIONS[convention]
    if "radius_mm" in cfg:
        R = cfg["radius_mm"]
        rp1, rp2, rp3 = cfg["p1_frac"] * R, cfg["p2_frac"] * R, cfg["p3_frac"] * R
    else:
        r_edge = float(np.max(r))
        rp1 = r_edge - cfg["edge_p1_mm"]
        rp2 = r_edge - cfg["edge_p2_mm"]
        rp3 = r_edge - cfg["edge_p3_mm"]

    z1, z2, z3 = np.interp([rp1, rp2, rp3], r, t)
    zref = z1 + (z2 - z1) * (rp3 - rp1) / (rp2 - rp1)
    return float(z3 - zref)


# ---------------------------------------------------------------------------
# (4) ITRS "10%×배선높이" 규칙 (노트 §5, §6(A))
# ---------------------------------------------------------------------------

def itrs_allowance(pitch_nm: float, aspect_ratio: float, frac: float = 0.10) -> float:
    """ITRS 로드맵식 두께손실 허용치 판정: height = (pitch/2)*aspect_ratio(반피치=선폭이 배선
    높이로 환산되는 배율), allowance = frac*height. ITRS 2007 Table INTC2a의 erosion 행이
    이 규칙(frac=0.10)의 반올림임을 9개 연도 전부 ±0.5nm 이내로 재현했다(노트 §6(A))."""
    height_nm = (pitch_nm / 2.0) * aspect_ratio
    return frac * height_nm


# ---------------------------------------------------------------------------
# (5) Residual — 결함량(이산 판정) vs 잔여 막두께(연속량), 노트 §1.4
# ---------------------------------------------------------------------------

def residual_metal_fraction(measured_map: ArrayLike, threshold: float = 0.0) -> float:
    """잔류 금속(결함) 판정 — Park 1998/Pan 1999: 배리어/Cu 잔류는 0 허용(전기 단락을 일으키므로
    연속 지표가 아니라 검사값). measured_map에서 threshold를 초과하는 지점의 비율을 반환한다.
    반환값이 0이 아니면 그 자체로 결함(underpolish) 신호이며, "약간 남았다"는 정도 비교는
    문헌상 의미가 없다(노트 §1.4-1)."""
    m = np.asarray(measured_map, float)
    if m.size == 0:
        raise ValueError("빈 입력")
    return float(np.mean(m > threshold))


def remaining_thickness(as_deposited_nm: float, removed_nm: float) -> float:
    """잔여 막두께(연속량) = 증착두께 − 제거량 (노트 §1.4-2). erosion(Park식)은 이 값의
    감소분과 같은 개념이지만, 결함 판정인 residual_metal_fraction과는 필드명을 분리한다."""
    return as_deposited_nm - removed_nm
