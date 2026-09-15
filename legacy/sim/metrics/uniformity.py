"""균일도·두께 지표 라이브러리 — wafer-metrology 에이전트 소유 (엔진 출력 스키마).

정의 확정 (2026-09-06, wafer-metrology Lv1-2, `agents/wafer-metrology/PROFILE.md` "구현 요청"):
근거 노트 `knowledge/cmp/uniformity-metrics-definitions-standards.md` (게이트 2종 통과).
사용자 회사 관행 정의를 그대로 옮기지 않는다 — 문헌 정의를 default로 삼고, 회사 관행은
별도 필드명으로 병기한다 (ORG 절대원칙).

확정 정의:
  TTV            = t_max − t_min                        [nm]  (SEMI MF1530; Kao & Chung 2021 Eq.1.5)
  CV             = σ / μ × 100                            [%]  (통계 표준. 1σ WIWNU와 수학적으로 동일)
  WIWNU 3σ (default) = 3σ / mean × 100                    [%]  (US6922603B1 특허 — "the WIWNU metric")
  WIWNU half-range   = (max−min)/(2·mean) × 100           [%]  (Luo & Dornfeld형)
  radial (문헌 default) = 방위각 평균 반경프로파일 t̄(r)의 σ 또는 range / mean × 100
                          — 단일 표준식 없음(문헌의 실제 상태). 이 코드는 반경 링별 평균을
                          t̄(r) 근사로 쓴다(축대칭 profile 입력이면 링 평균≈그 반경의 값 자체).
  radial_maxring_range (회사 관행, 별도 필드) = 반경 링별 (max−min) 중 최대 — 문헌 근거 약함, default 아님.

WIWNU는 산업 표준이 없다(process-integrator 판단, wiwnu-pressure-velocity 노트) → 전 변형 병기 원칙.
값만 인용하지 말고 정의를 함께 보고할 것.

입력은 두 형태를 받는다:
  1) 반경 프로파일 (radius[], value[])            — 시뮬레이터 출력, 축대칭 가정
  2) 측정 포인트 (x[], y[], value[])               — 실측. 반경 링은 r을 n_rings로 등분
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Optional
from numpy.typing import ArrayLike

import numpy as np


@dataclass
class UniformityMetrics:
    n_points: int
    mean_nm: float
    min_nm: float
    max_nm: float
    sigma_nm: float
    ttv_nm: float
    # radial — 문헌 default: 방위각 평균 반경프로파일(링 평균) t̄(r)의 σ/range
    ring_mean_nm: list                 # 링별 평균 두께 — t̄(r) 근사
    radial_sigma_pct: float            # 100·σ(ring_mean)/mean  (문헌 default 후보 1)
    radial_range_pct: float            # 100·(max-min of ring_mean)/(2·mean)  (문헌 default 후보 2)
    # radial — 회사 관행 (별도 필드, default 아님, 문헌 근거 약함)
    radial_maxring_range_nm: float     # 링별 (max−min) 중 최대
    radial_maxring_range_ring: int     # 어느 링에서 최대가 났나 (0=중심)
    ring_ttv_nm: list                  # 링별 내부 TTV(max-min) 전부 (보고서 그래프용)
    cv_pct: float
    wiwnu_halfrange_pct: float
    wiwnu_3sigma_pct: float
    edge_rebound_nm: Optional[float]
    definition: str = (
        "TTV=max-min(SEMI MF1530) | CV=σ/μ·100 | WIWNU_3σ=3σ/mean·100(US6922603B1,default) | "
        "WIWNU_hr=(max-min)/(2·mean)·100 | radial(문헌default)=σ or range of 방위각평균반경프로파일t̄(r) "
        "(근사=링평균) | radial_maxring_range=회사관행(링별 max-min의 최대, 별도필드·default아님) | "
        "근거: knowledge/cmp/uniformity-metrics-definitions-standards.md"
    )

    def as_dict(self):
        return asdict(self)


def _ring_index(r: np.ndarray, r_max: float, n_rings: int) -> np.ndarray:
    idx = np.floor(r / r_max * n_rings).astype(int)
    return np.clip(idx, 0, n_rings - 1)


def compute_metrics(radius_m: ArrayLike, value_nm: ArrayLike,
                    n_points: int = 81, n_rings: int = 8) -> UniformityMetrics:
    """반경 프로파일 입력. 축대칭 가정 → 각 반경이 곧 하나의 링.
    n_rings로 프로파일을 링으로 묶어 radial 지표를 계산한다(실측 8링 관행과 맞춤)."""
    r = np.asarray(radius_m, float)
    v = np.asarray(value_nm, float)
    return _metrics_from_rings(r, v, n_points=n_points, n_rings=n_rings)


def compute_metrics_points(x_m: ArrayLike, y_m: ArrayLike, value_nm: ArrayLike,
                           n_rings: int = 8) -> UniformityMetrics:
    """실측 포인트 입력 (x,y). 반경으로 변환해 링을 나눈다."""
    x = np.asarray(x_m, float); y = np.asarray(y_m, float); v = np.asarray(value_nm, float)
    r = np.hypot(x, y)
    return _metrics_from_rings(r, v, n_points=len(v), n_rings=n_rings)


def _metrics_from_rings(r: np.ndarray, v: np.ndarray, n_points: int, n_rings: int) -> UniformityMetrics:
    if len(v) == 0:
        raise ValueError("빈 입력")
    mean = float(np.mean(v)); sig = float(np.std(v, ddof=0))
    vmin = float(np.min(v)); vmax = float(np.max(v))
    r_max = float(np.max(r)) if np.max(r) > 0 else 1.0
    ring = _ring_index(r, r_max, n_rings)
    ring_ttv = []
    ring_mean = []
    for k in range(n_rings):
        vk = v[ring == k]
        ring_ttv.append(float(vk.max() - vk.min()) if len(vk) > 1 else 0.0)
        ring_mean.append(float(vk.mean()) if len(vk) else float("nan"))
    valid_means = np.array([m for m in ring_mean if not np.isnan(m)])
    radial_sigma_pct = (100 * float(np.std(valid_means, ddof=0)) / mean) if mean and len(valid_means) else float("nan")
    radial_range_pct = (100 * (float(valid_means.max()) - float(valid_means.min())) / (2 * mean)) if mean and len(valid_means) else float("nan")
    radial_maxring_range = max(ring_ttv)
    ring_argmax = int(np.argmax(ring_ttv))
    # 엣지 리바운드: 마지막 링 평균 − 그 안쪽 링 평균
    edge = None
    if n_rings >= 2:  # noqa
        last = v[ring == n_rings - 1]; prev = v[ring == n_rings - 2]
        if len(last) and len(prev):
            edge = float(last.mean() - prev.mean())
    return UniformityMetrics(
        n_points=int(n_points), mean_nm=mean, min_nm=vmin, max_nm=vmax, sigma_nm=sig,
        ttv_nm=vmax - vmin,
        ring_mean_nm=ring_mean,
        radial_sigma_pct=radial_sigma_pct, radial_range_pct=radial_range_pct,
        radial_maxring_range_nm=radial_maxring_range, radial_maxring_range_ring=ring_argmax,
        ring_ttv_nm=ring_ttv,
        cv_pct=(sig / mean * 100.0) if mean else float("nan"),
        wiwnu_halfrange_pct=((vmax - vmin) / (2 * mean) * 100.0) if mean else float("nan"),
        wiwnu_3sigma_pct=(3 * sig / mean * 100.0) if mean else float("nan"),
        edge_rebound_nm=edge,
    )


def _selftest():
    # 1) 완전 균일 → 전 지표 0
    r = np.linspace(0, 0.147, 81); v = np.full(81, 500.0)
    m = compute_metrics(r, v)
    assert m.ttv_nm == 0 and m.radial_maxring_range_nm == 0 and m.cv_pct == 0, m
    assert m.radial_sigma_pct == 0 and m.radial_range_pct == 0, m
    # 2) 선형 기울기 500→520: TTV=20, 각 링 내부TTV ≈ 20/8 → radial_maxring ≈ 2.5, 엣지 리바운드 +
    v = np.linspace(500, 520, 81)
    m = compute_metrics(r, v)
    assert abs(m.ttv_nm - 20) < 1e-9, m.ttv_nm
    assert 2.0 < m.radial_maxring_range_nm < 3.0, m.radial_maxring_range_nm
    assert m.edge_rebound_nm is not None and m.edge_rebound_nm > 0
    # 선형 프로파일은 방위각 변동이 없으므로 radial_range_pct ≈ WIWNU half-range(≈전체 TTV 기반)에 근접해야 함
    assert m.radial_range_pct > 0 and m.radial_range_pct <= m.wiwnu_halfrange_pct + 1e-6, (m.radial_range_pct, m.wiwnu_halfrange_pct)
    # 3) 중심 링만 튀는 경우: radial_maxring_range 최대가 링 0에서
    v = np.full(81, 500.0); v[:5] = [500, 510, 500, 490, 500]
    m = compute_metrics(r, v)
    assert m.radial_maxring_range_ring == 0 and abs(m.radial_maxring_range_nm - 20) < 1e-9, (m.radial_maxring_range_ring, m.radial_maxring_range_nm)
    # 4) 포인트 입력 = 프로파일 입력과 같은 정의
    th = np.linspace(0, 2 * np.pi, 81, endpoint=False)
    rr = np.linspace(0, 0.147, 81)
    mp = compute_metrics_points(rr * np.cos(th), rr * np.sin(th), np.linspace(500, 520, 81))
    assert abs(mp.ttv_nm - 20) < 1e-9
    # 5) CV 정의 (문헌: CV ≡ 1σ WIWNU, 항등식)
    v = np.array([100.0, 110.0]); m = compute_metrics(np.array([0.0, 0.1]), v, n_rings=1)
    assert abs(m.cv_pct - (5 / 105 * 100)) < 1e-9
    # 6) 정의 항등식: 3σ WIWNU = 3 × CV(=1σ WIWNU)
    assert abs(m.wiwnu_3sigma_pct - 3 * m.cv_pct) < 1e-9, (m.wiwnu_3sigma_pct, m.cv_pct)
    print("metrics self-test 6/6 PASS")


if __name__ == "__main__":
    _selftest()
