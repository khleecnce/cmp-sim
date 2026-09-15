"""Raw 측정 정규화 유틸 — 좌표계·단위 통일, 결측/이상치 클리닝.

지식 근거: knowledge/data/wafer-coordinate-units-outlier-cleaning.md §1-3
(cmp-data-engineer Lv2-1, agents/cmp-data-engineer/PROFILE.md "구현 요청").
검증 문헌값은 §5 verify 블록을 그대로 승격한 것 — tests/test_normalize.py.

원칙(노트 §0): 정규화는 손실이 있어선 안 된다(가역). 원 좌표계·단위·EE·클리닝
파라미터를 메타데이터로 보존해 재현 가능하게 두고, 변환식만 표준으로 고정한다.

이 모듈은 sim/engine.py에 미등록인 독립 유틸리티다(다른 S-item들과 동일한 지위,
Recipe 스키마 없음).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

import numpy as np
from numpy.typing import ArrayLike

# US7539552B2 NOTCH_DIRECTION: 0/1/2/3 = Bottom/Right/Top/Left.
# SEMI M20 정준계는 Bottom(노치=-y)을 기준 배향으로 삼는다(노트 §1.1).
NOTCH_ANGLES_RAD: Dict[str, float] = {
    "Bottom": 0.0,
    "Right": np.pi / 2,
    "Top": np.pi,
    "Left": -np.pi / 2,
}


@dataclass
class CanonicalCoords:
    """M20 정준계(원점=중심, +x=오른쪽, +y=위, 노치=-y)로 변환된 좌표.

    원 좌표계·kind·notch_dir을 메타데이터로 보존해 가역적이다(노트 §0 원칙).
    """
    x_m: np.ndarray
    y_m: np.ndarray
    source_kind: str
    source_notch_dir: str
    source_meta: dict = field(default_factory=dict)


def to_canonical_coords(coords, notch_dir: str, kind: str) -> CanonicalCoords:
    """웨이퍼 좌표를 SEMI M20 정준계(중심원점, 노치=-y)로 변환한다.

    notch_dir: US7539552B2식 4값 열거형 — 'Bottom'/'Right'/'Top'/'Left'.
        원본 좌표에서 노치가 실제로 향하고 있던 방향. 정준화는 그 방향이
        -y로 오도록 원점 중심 회전을 적용한다(노트 §1.1·§1.3).
    kind: 'polar' | 'cartesian' | 'die'.
        - 'polar': coords = (r_m, theta_rad) 배열 쌍. 먼저 x=r*cosθ, y=r*sinθ로
          데카르트 변환한 뒤(노트 §1.2) 노치 회전을 적용한다.
        - 'cartesian': coords = (x_m, y_m) 배열 쌍. 노치 회전만 적용한다.
        - 'die': coords = (col, row, pitch_x, pitch_y, col0, row0, x0, y0).
          아핀 변환 x=x0+(c-c0)*px, y=y0+(r0-r)*py (행축 부호반전 필수,
          US7539552B2 UCS — 노트 §1.3) 후 노치 회전을 적용한다.
    """
    if notch_dir not in NOTCH_ANGLES_RAD:
        raise ValueError(f"notch_dir는 Bottom/Right/Top/Left 중 하나여야 함: {notch_dir!r}")

    if kind == "polar":
        r, theta = coords
        r = np.asarray(r, float)
        theta = np.asarray(theta, float)
        x = r * np.cos(theta)
        y = r * np.sin(theta)
    elif kind == "cartesian":
        x, y = coords
        x = np.asarray(x, float)
        y = np.asarray(y, float)
    elif kind == "die":
        c, r, px, py, c0, r0, x0, y0 = coords
        c = np.asarray(c, float)
        r = np.asarray(r, float)
        x = x0 + (c - c0) * px
        y = y0 - (r - r0) * py  # 행축 부호반전 (r0-r) — 이미지좌표(행 증가=아래)를 물리좌표(행 증가=위)로
    else:
        raise ValueError(f"kind는 polar/cartesian/die 중 하나여야 함: {kind!r}")

    # 노치가 notch_dir 방향에 있는 원 좌표계를, 노치가 -y(Bottom)에 오도록 회전.
    # notch_dir='Bottom'이면 phi=0(회전 없음). 'Right'면 원점에서 -90도 회전해
    # 원래 +x(Right)에 있던 노치가 -y로 온다 — 즉 phi = -NOTCH_ANGLES_RAD[notch_dir].
    phi = -NOTCH_ANGLES_RAD[notch_dir]
    cos_p, sin_p = np.cos(phi), np.sin(phi)
    x_c = x * cos_p - y * sin_p
    y_c = x * sin_p + y * cos_p

    meta: dict = {}
    if kind == "die":
        meta = {"pitch_x": px, "pitch_y": py, "col0": c0, "row0": r0, "x0": x0, "y0": y0}

    return CanonicalCoords(
        x_m=x_c, y_m=y_c,
        source_kind=kind, source_notch_dir=notch_dir, source_meta=meta,
    )


@dataclass
class CanonicalValue:
    """정준(내부) 단위로 변환된 값. 원 단위 문자열을 메타로 보존한다(노트 §2)."""
    value: np.ndarray
    canonical_unit: str
    source_unit: str


# 노트 §2 표: 두께 nm, 제거율 nm/min, 압력 kPa, 속도 m/s가 정준(내부) 단위.
_SCALAR_FACTORS: Dict[str, tuple] = {
    # unit -> (canonical_unit, factor) : canonical = value * factor
    "angstrom": ("nm", 0.1),                    # 1 Å = 0.1 nm (정의)
    "angstrom_per_s": ("nm_per_min", 6.0),       # 1 Å/s = 6 nm/min (=0.1*60, 정의)
    "psi": ("kPa", 6.894757),                    # 1 psi = 6.894757 kPa (NIST SP811 정의값)
}


def to_canonical_units(value: ArrayLike, unit: str, *, radius_m: Optional[float] = None) -> CanonicalValue:
    """값을 정준(내부) 단위로 변환한다. 원 단위 문자열은 메타로 보존한다.

    지원 unit: 'angstrom'(→nm, ×0.1), 'angstrom_per_s'(→nm_per_min, ×6),
    'psi'(→kPa, ×6.894757), 'rpm'(→m_per_s, v=2*pi*r*N/60, radius_m 필수).
    노트 §2 표에 없는 단위는 지원하지 않는다(지어내지 않음).
    """
    v = np.asarray(value, float)
    if unit == "rpm":
        if radius_m is None:
            raise ValueError("unit='rpm'은 radius_m이 필요함 (v=2*pi*r*N/60)")
        canonical = 2.0 * np.pi * radius_m * (v / 60.0)
        return CanonicalValue(value=canonical, canonical_unit="m_per_s", source_unit=unit)
    if unit in _SCALAR_FACTORS:
        canonical_unit, factor = _SCALAR_FACTORS[unit]
        return CanonicalValue(value=v * factor, canonical_unit=canonical_unit, source_unit=unit)
    raise ValueError(f"지원하지 않는 단위: {unit!r} (노트 §2에 없는 값은 지어내지 않음)")


@dataclass
class OutlierFlags:
    """이상치 플래그 결과. 삭제가 아니라 플래그만(노트 §3.2) — 원값은 그대로 보존."""
    values: np.ndarray
    is_outlier: np.ndarray  # bool 배열
    method: str
    k: float
    reason: List[Optional[str]]


def flag_outliers(values: ArrayLike, method: str = "mad", k: Optional[float] = None) -> OutlierFlags:
    """이상치를 검출해 플래그한다(삭제하지 않음). 원값+사유를 함께 반환.

    method='mad'(default, Leys et al. 2013): MAD = 1.4826*median(|xi-median(x)|),
        |xi-median| > k*MAD 이면 이상치. default k=2.5(논문 권고).
    method='iqr' (Tukey): [Q1-k*IQR, Q3+k*IQR] 밖. default k=1.5.
    method='sigma': mean±k*sigma 밖 — 옵션으로만 제공, default로 쓰지 않는다
        (노트 §3.2: 이상치가 sigma를 부풀려 마스킹함, Leys 2013).
    """
    v = np.asarray(values, float)
    reason: List[Optional[str]] = [None] * len(v)

    if method == "mad":
        kk = 2.5 if k is None else k
        med = np.median(v)
        mad = 1.4826 * np.median(np.abs(v - med))
        dev = np.abs(v - med)
        is_outlier = dev > kk * mad if mad > 0 else np.zeros_like(v, dtype=bool)
        for i in np.flatnonzero(is_outlier):
            reason[i] = f"mad: |x-median|={dev[i]:.4g} > {kk}*MAD={kk*mad:.4g}"
    elif method == "iqr":
        kk = 1.5 if k is None else k
        q1, q3 = np.percentile(v, [25, 75])
        iqr = q3 - q1
        lo, hi = q1 - kk * iqr, q3 + kk * iqr
        is_outlier = (v < lo) | (v > hi)
        for i in np.flatnonzero(is_outlier):
            reason[i] = f"iqr: x={v[i]:.4g} outside [{lo:.4g}, {hi:.4g}]"
    elif method == "sigma":
        # 옵션 제공만 — default 아님(노트 §3.2: sigma는 이상치 자체에 오염되어 마스킹됨).
        kk = 3.0 if k is None else k
        mean, sd = v.mean(), v.std(ddof=0)
        is_outlier = np.abs(v - mean) > kk * sd if sd > 0 else np.zeros_like(v, dtype=bool)
        for i in np.flatnonzero(is_outlier):
            reason[i] = f"sigma(비권장): |x-mean|>{kk}*sigma"
    else:
        raise ValueError(f"method는 mad/iqr/sigma 중 하나여야 함: {method!r}")

    return OutlierFlags(values=v, is_outlier=is_outlier, method=method, k=kk, reason=reason)


@dataclass
class EdgeExclusionFlags:
    """엣지제외/결측 구분 플래그. 'excluded'(정의상 측정범위밖)와 'missing'(NaN,
    실측 실패)은 서로 다른 사유이므로 섞지 않는다(노트 §3.1)."""
    r_mm: np.ndarray
    excluded: np.ndarray   # bool — FQA 밖 (SEMI M1)
    missing: np.ndarray    # bool — 입력이 NaN이었던 결측
    ee_mm: float
    D_mm: float


def apply_edge_exclusion(r, ee_mm: float, D_mm: float) -> EdgeExclusionFlags:
    """반경 r(mm)이 FQA 경계(D_mm/2 - ee_mm)보다 크면 'excluded'로 마스크한다.

    NaN 입력은 'missing'으로 별도 플래그한다 — excluded와 missing은 서로 다른 사유이므로
    섞으면 안 된다(노트 §3.1: EE 안쪽은 결측이 아니라 정의상 측정 범위 밖).
    """
    r_arr = np.asarray(r, float)
    missing = np.isnan(r_arr)
    fqa_radius_mm = D_mm / 2.0 - ee_mm
    excluded = np.where(missing, False, r_arr > fqa_radius_mm)
    return EdgeExclusionFlags(r_mm=r_arr, excluded=excluded, missing=missing, ee_mm=ee_mm, D_mm=D_mm)
