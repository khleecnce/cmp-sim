"""NPW 반경방향 잔차 보정 (Tier3, GP) — ORG.md §7.4/§7.6 M3 게이트 3/3.

역할 경계(sim/calibration/series_scale.py 상단 docstring이 정본):

    구조(shape) : 함수 형태·지수·부호·게이트·정점 위치 → 물리에서 유도된다.
    축척(scale)·잔차 : 장비·측정계마다 다르고 데이터의 몫이다.

이 모듈은 그 "잔차" 층이다. sim.engine.simulate(pack) 이 낸 반경 프로파일을
진실로 놓고, 그 위에 남는 반경방향 계통 편차(residual)만 비모수(가우시안
과정, GP)로 학습한다. **물리식·지수·YAML 값은 한 글자도 건드리지 않는다** —
sim/factors.py·sim/engine.py·sim/chemistry.py·sim/params.py·
knowledge/params/*.yaml 은 읽기만 한다.

이 모듈에는 문헌값·물리상수가 하나도 없다. GP 하이퍼파라미터(길이척도 l,
신호분산 sigma_f, 노이즈 sigma_n)는 전부 학습 데이터에서 주변우도(marginal
likelihood) 최대화로 적합한다 — 지어내거나 문헌에서 가져오지 않는다.

관측량 선택 근거
────────────────
data/synthetic/SYN-OXIDE-SILICA-001.json 의 notes: 이 합성 웨이퍼의 value는
``sim.engine.simulate(pack='oxide_silica')`` 반경 프로파일(Recipe 기본값
``wafer="NPW"``, ``time_s=60.0`` — 둘 다 Recipe 기본값과 정확히 같다) + 가우시안
측정노이즈다. 생성기(tools/make_synthetic_wafer.py)를 직접 대조하면 진실값으로
쓴 필드는 ``WaferResult.removed_nm``(반경별 제거량, 단위 nm)이고, 기록 단위는
그대로 ``"nm"``이다. ingest.py 의 ``unit_canonical`` 도 "nm"은 정준 단위 집합에
이미 속해 있어 변환 없이 "nm" 그대로 남는다(sim/calibration/ingest.py
``_CANONICAL_UNITS``). 따라서:

  · unit_canonical == "nm"        → WaferResult.removed_nm 과 대조한다.
  · unit_canonical == "nm_per_min" → WaferResult.mrr_nm_per_min 과 대조한다
    (같은 논리를 속도 단위 계열로 확장한 것 — 두 필드 다 Recipe 기본값 실행
    결과에서 그대로 나온다).
  · 그 외 단위(kPa·m_per_s 등 — 두께도 속도도 아닌 관측량)는 이 Tier3 잔차
    정의가 성립하지 않으므로 ValueError.
"""
from __future__ import annotations

import pathlib
import sys
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import numpy as np                                            # noqa: E402
from scipy import linalg as sla                                # noqa: E402
from scipy.optimize import minimize                            # noqa: E402

__all__ = [
    "NPWCorrection", "fit", "fit_residuals", "apply",
]

_Z95 = 1.959963984540054  # 표준정규 97.5% 분위수 (95% 양측 CI)


@dataclass
class NPWCorrection:
    """반경방향 잔차 GP 적합 결과. apply() 가 이 객체로 보정을 낸다."""
    pack: str
    n_train: int
    n_dropped: Dict[str, int]
    hyperparams: Dict[str, float]     # {"l_mm", "sigma_f", "sigma_n"} — 적합 실패/거부 시 {}
    loo_rmse_gp: float
    loo_rmse_baseline: float
    improved: bool
    converged: bool
    notes: List[str]
    # apply() 재계산에 필요한 학습 데이터 — to_prior_dict() 직렬화 대상이 아니다.
    r_train_mm: Optional[np.ndarray] = field(default=None, repr=False)
    residual_train: Optional[np.ndarray] = field(default=None, repr=False)

    def to_prior_dict(self) -> dict:
        """PTW 전이 훅(ORG §7): 적합된 하이퍼파라미터를 순수 dict로 직렬화한다.

        "NPW 보정치가 PTW의 초기값이 된다"(ORG §7) — fit_ptw.py(이번 과제 밖)가
        이 dict를 prior로 읽어갈 수 있게, 학습 원자료(r_train_mm 등) 없이
        재현 가능한 요약만 담는다. 파일에 쓰지 않는다.
        """
        return {
            "pack": self.pack,
            "n_train": self.n_train,
            "n_dropped": dict(self.n_dropped),
            "hyperparams": dict(self.hyperparams),
            "loo_rmse_gp": self.loo_rmse_gp,
            "loo_rmse_baseline": self.loo_rmse_baseline,
            "improved": self.improved,
            "converged": self.converged,
            "notes": list(self.notes),
        }


# ──────────────────────────────────────────────────────────────
# GP 커널 · Cholesky (Rasmussen & Williams, GPML 2006, Alg. 2.1)
# ──────────────────────────────────────────────────────────────

def _rbf(r1: np.ndarray, r2: np.ndarray, sigma_f: float, l: float) -> np.ndarray:
    d = r1[:, None] - r2[None, :]
    return (sigma_f ** 2) * np.exp(-(d ** 2) / (2.0 * l ** 2))


def _safe_cholesky(K: np.ndarray) -> Tuple[np.ndarray, float]:
    """K = L L^T. 실패하면 지터를 1e-10부터 10배씩 최대 6회 얹어 재시도한다.

    수치오차로 K가 양정치가 아닐 만큼 관측 반경이 거의 중복될 때를 대비한
    가드다 — GPML Alg. 2.1의 표준 관행. 6회 모두 실패하면 명확한 예외를 던진다
    (조용히 넘어가지 않는다).
    """
    n = K.shape[0]
    jitter = 0.0
    last_err: Optional[Exception] = None
    for _ in range(6):
        try:
            L = sla.cholesky(K + jitter * np.eye(n), lower=True)
            return L, jitter
        except sla.LinAlgError as exc:
            last_err = exc
            jitter = 1e-10 if jitter == 0.0 else jitter * 10.0
    raise sla.LinAlgError(
        f"Cholesky가 지터 6회 재시도(최대 {jitter:.1e})로도 수렴하지 않았다: {last_err}"
    )


def _neg_log_marginal_likelihood(log_theta: np.ndarray, r: np.ndarray, y: np.ndarray) -> float:
    if not np.all(np.isfinite(log_theta)):
        return 1e10
    l, sigma_f, sigma_n = np.exp(log_theta)
    n = len(r)
    with np.errstate(over="ignore", invalid="ignore", divide="ignore"):
        K = _rbf(r, r, sigma_f, l) + (sigma_n ** 2) * np.eye(n)
    if not np.all(np.isfinite(K)):
        return 1e10  # 옵티마이저가 exp() 오버플로/0으로 나눔 구간을 헤맬 때의 가드
    try:
        L, _ = _safe_cholesky(K)
    except sla.LinAlgError:
        return 1e10  # 이 하이퍼파라미터 지점은 옵티마이저가 피하도록 큰 값을 준다
    alpha = sla.cho_solve((L, True), y)
    nll = 0.5 * float(y @ alpha) + float(np.sum(np.log(np.diag(L)))) + 0.5 * n * np.log(2.0 * np.pi)
    return nll if np.isfinite(nll) else 1e10


# 로그공간 탐색 경계 — 물리상수가 아니라 오버플로/언더플로 방지용 수치 가드일
# 뿐이다(exp(±30)까지도 float64에서 안전). 데이터 스케일과 무관하게 고정.
_LOG_THETA_BOUNDS = [(-30.0, 30.0)] * 3


def _fit_hyperparams(r: np.ndarray, y: np.ndarray, *, seed: int, n_restarts: int
                      ) -> Tuple[float, float, float, bool]:
    """음의 로그주변우도를 다중 시작점 L-BFGS-B로 최소화한다. 반환: (l, sigma_f, sigma_n, converged)."""
    r_span = float(r.max() - r.min())
    if r_span <= 0.0:
        r_span = 1.0
    y_std = float(np.std(y))
    if y_std <= 0.0:
        y_std = 1e-6

    rng = np.random.default_rng(seed)
    starts = [(r_span / 4.0, y_std, 0.1 * y_std + 1e-6)]
    for _ in range(max(n_restarts - 1, 0)):
        l0 = r_span * rng.uniform(0.05, 1.5)
        sf0 = y_std * rng.uniform(0.1, 3.0)
        sn0 = y_std * rng.uniform(0.01, 1.0) + 1e-6
        starts.append((l0, sf0, sn0))

    best = None
    for l0, sf0, sn0 in starts[:max(n_restarts, 1)]:
        x0 = np.log(np.array([l0, sf0, sn0], dtype=float))
        x0 = np.clip(x0, _LOG_THETA_BOUNDS[0][0], _LOG_THETA_BOUNDS[0][1])
        res = minimize(_neg_log_marginal_likelihood, x0, args=(r, y), method="L-BFGS-B",
                        bounds=_LOG_THETA_BOUNDS)
        if best is None or res.fun < best.fun:
            best = res

    l, sigma_f, sigma_n = np.exp(best.x)
    return float(l), float(sigma_f), float(sigma_n), bool(best.success)


def _loo_errors(r: np.ndarray, y: np.ndarray, l: float, sigma_f: float, sigma_n: float
                 ) -> Tuple[np.ndarray, np.ndarray]:
    """폐형식 leave-one-out (Rasmussen & Williams eq. 5.12).

    mu_i - y_i = alpha_i / [K^-1]_ii,  sigma_i^2 = 1 / [K^-1]_ii — 각 점을 실제로
    빼고 재적합할 필요 없이 K^-1의 대각만으로 전체 LOO 잔차를 한 번에 낸다.
    """
    n = len(r)
    K = _rbf(r, r, sigma_f, l) + (sigma_n ** 2) * np.eye(n)
    L, _ = _safe_cholesky(K)
    alpha = sla.cho_solve((L, True), y)
    K_inv = sla.cho_solve((L, True), np.eye(n))
    diag_inv = np.diag(K_inv)
    loo_err = alpha / diag_inv          # mu_{-i} - y_i
    loo_var = 1.0 / diag_inv
    return loo_err, loo_var


# ──────────────────────────────────────────────────────────────
# 공개 API
# ──────────────────────────────────────────────────────────────

def fit_residuals(pack: str, r_mm: np.ndarray, residual: np.ndarray, *,
                   n_dropped: Optional[Dict[str, int]] = None,
                   seed: int = 0, n_restarts: int = 5) -> NPWCorrection:
    """이미 계산된 (반경, 잔차) 쌍에서 GP를 적합한다 — fit() 이 위임하는 핵심 로직.

    engine/ingest 왕복 없이 잔차 배열을 직접 넣을 수 있어, GP 자체의 성질
    (알려진 곡선 회수, 순수 노이즈 거부, n<5 거부, 재현성, 지터 경로)을 물리
    엔진과 분리해 테스트할 수 있다.

    §안전장치 1(자기 검증): 기준선(보정 안 함, 잔차 예측 0)의 LOO RMSE와
    GP의 LOO RMSE를 대조한다. GP가 기준선보다 나쁘거나 같으면 improved=False —
    apply()는 이 플래그를 보고 보정을 아예 적용하지 않는다.
    §안전장치 3(표본 부족 거부): 유효 학습점이 5개 미만이면 적합 자체를
    시도하지 않고, 예외 대신 사유가 담긴 정상 반환을 한다.
    """
    r = np.asarray(r_mm, dtype=float)
    y = np.asarray(residual, dtype=float)
    n_train = len(r)
    dropped = dict(n_dropped) if n_dropped is not None else {}

    if n_train < 5:
        baseline = float(np.sqrt(np.mean(y ** 2))) if n_train > 0 else float("nan")
        return NPWCorrection(
            pack=pack, n_train=n_train, n_dropped=dropped, hyperparams={},
            loo_rmse_gp=float("nan"), loo_rmse_baseline=baseline,
            improved=False, converged=False,
            notes=[f"유효 학습점 {n_train}개 < 5 — GP 적합을 거부한다. 물리모델(보정 0)만 사용."],
            r_train_mm=r, residual_train=y,
        )

    notes: List[str] = []
    l, sigma_f, sigma_n, converged = _fit_hyperparams(r, y, seed=seed, n_restarts=n_restarts)
    if not converged:
        notes.append("L-BFGS-B가 최선 재시작 기준으로도 수렴하지 않았다 — 하이퍼파라미터 신뢰도 낮음.")

    loo_err, _loo_var = _loo_errors(r, y, l, sigma_f, sigma_n)
    loo_rmse_gp = float(np.sqrt(np.mean(loo_err ** 2)))
    loo_rmse_baseline = float(np.sqrt(np.mean(y ** 2)))
    improved = loo_rmse_gp < loo_rmse_baseline
    if not improved:
        notes.append(
            f"LOO RMSE(GP)={loo_rmse_gp:.6g} >= LOO RMSE(기준선,보정없음)={loo_rmse_baseline:.6g} "
            "— 데이터가 구조를 지지하지 않는다. 보정을 적용하지 않는다(물리모델 그대로)."
        )

    hyperparams = {"l_mm": l, "sigma_f": sigma_f, "sigma_n": sigma_n}
    return NPWCorrection(
        pack=pack, n_train=n_train, n_dropped=dropped, hyperparams=hyperparams,
        loo_rmse_gp=loo_rmse_gp, loo_rmse_baseline=loo_rmse_baseline,
        improved=improved, converged=converged, notes=notes,
        r_train_mm=r, residual_train=y,
    )


def fit(pack: str, ingest_result, *, model: str = "tier1.preston_radial",
        seed: int = 0, n_restarts: int = 5) -> NPWCorrection:
    """ingest.IngestResult(또는 그 pyarrow table) → 물리 예측과의 잔차 → GP 적합.

    is_excluded/is_missing/is_outlier 가 True인 행은 학습에서 제외한다. 남은
    행의 반경이 엔진 격자 범위를 벗어나면 외삽하지 않고 버리며 사유를 기록한다
    (out_of_grid). 관측 단위는 모듈 docstring의 판단 근거를 그대로 따른다 —
    "nm"은 removed_nm, "nm_per_min"은 mrr_nm_per_min과 대조하고, 그 외 단위는
    ValueError.
    """
    from sim.engine import Recipe, simulate  # 지연 임포트 — 순환 임포트 회피(prior.py와 동일 패턴)

    table = ingest_result.table if hasattr(ingest_result, "table") else ingest_result

    r_mm = np.asarray(table.column("r_mm").to_pylist(), dtype=float)
    value_raw = table.column("value_canonical").to_pylist()
    unit_raw = table.column("unit_canonical").to_pylist()
    is_excluded = np.asarray(table.column("is_excluded").to_pylist(), dtype=bool)
    is_missing = np.asarray(table.column("is_missing").to_pylist(), dtype=bool)
    is_outlier = np.asarray(table.column("is_outlier").to_pylist(), dtype=bool)

    n_dropped = {
        "excluded": int(np.sum(is_excluded)),
        "missing": int(np.sum(is_missing)),
        "outlier": int(np.sum(is_outlier)),
        "out_of_grid": 0,
    }

    keep = ~(is_excluded | is_missing | is_outlier)
    r_kept = r_mm[keep]
    value_kept = np.asarray([value_raw[i] for i in range(len(value_raw)) if keep[i]], dtype=float)
    unit_kept = [unit_raw[i] for i in range(len(unit_raw)) if keep[i]]

    unit_set = set(unit_kept)
    if len(unit_set) > 1:
        raise ValueError(f"관측 단위가 학습 대상 행 안에서 혼재한다: {sorted(unit_set)}")

    recipe = Recipe(pack=pack)
    result = simulate(recipe, model=model)
    engine_r_mm = result.radius_m * 1000.0

    if not unit_set:
        obs_unit = None
        engine_field = result.removed_nm  # 사용되지 않음 — n_train=0으로 조기 반환됨
    else:
        obs_unit = next(iter(unit_set))
        if obs_unit == "nm":
            if result.removed_nm is None:
                raise ValueError("unit_canonical='nm'인데 WaferResult.removed_nm 이 None이다 (time_s<=0?)")
            engine_field = result.removed_nm
        elif obs_unit == "nm_per_min":
            engine_field = result.mrr_nm_per_min
        else:
            raise ValueError(
                f"관측량 단위 {obs_unit!r} 는 NPW 잔차 정의를 지원하지 않는다 "
                "('nm'→removed_nm, 'nm_per_min'→mrr_nm_per_min만 지원)."
            )

    r_grid_min, r_grid_max = float(engine_r_mm.min()), float(engine_r_mm.max())
    in_grid = (r_kept >= r_grid_min) & (r_kept <= r_grid_max)
    n_out = int(np.sum(~in_grid))
    n_dropped["out_of_grid"] = n_out

    notes: List[str] = []
    if n_out:
        notes.append(
            f"{n_out}개 측정점이 엔진 반경 격자 범위 [{r_grid_min:.4f}, {r_grid_max:.4f}] mm "
            "밖 — 외삽하지 않고 버렸다."
        )

    r_use = r_kept[in_grid]
    value_use = value_kept[in_grid]
    pred = np.interp(r_use, engine_r_mm, engine_field)
    residual = value_use - pred

    result_obj = fit_residuals(pack, r_use, residual, n_dropped=n_dropped, seed=seed, n_restarts=n_restarts)
    result_obj.notes = notes + result_obj.notes
    return result_obj


def apply(correction: NPWCorrection, radius_mm) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """(mean_correction, ci_lo, ci_hi, extrapolated_mask) — 반경 격자에 보정을 낸다.

    §안전장치 1: correction.improved 가 False 면(또는 하이퍼파라미터가 없으면)
    보정을 전혀 적용하지 않는다 — 전부 0, 물리 예측을 그대로 쓰라는 신호다.
    §안전장치 2: 학습 반경 범위 밖이거나 최근접 학습점까지 거리가 적합된
    길이척도 l 보다 먼 점은 보정을 0으로 감쇠시키고 extrapolated=True로 표시한다
    (GP는 데이터에서 멀어지면 사전평균=0으로 돌아가야 한다).
    """
    r_query = np.atleast_1d(np.asarray(radius_mm, dtype=float))

    if not correction.improved or not correction.hyperparams or correction.n_train < 5:
        zeros = np.zeros_like(r_query)
        return zeros, zeros.copy(), zeros.copy(), np.zeros_like(r_query, dtype=bool)

    l = correction.hyperparams["l_mm"]
    sigma_f = correction.hyperparams["sigma_f"]
    sigma_n = correction.hyperparams["sigma_n"]
    r_train = correction.r_train_mm
    y_train = correction.residual_train

    K = _rbf(r_train, r_train, sigma_f, l) + (sigma_n ** 2) * np.eye(len(r_train))
    L, _ = _safe_cholesky(K)
    alpha = sla.cho_solve((L, True), y_train)

    K_s = _rbf(r_query, r_train, sigma_f, l)          # (m, n)
    mean = K_s @ alpha
    v = sla.solve_triangular(L, K_s.T, lower=True)     # (n, m)
    var = (sigma_f ** 2) - np.sum(v ** 2, axis=0)
    var = np.maximum(var, 0.0) + sigma_n ** 2           # 사후 분산 + 노이즈
    sd = np.sqrt(var)

    dist_to_nearest = np.min(np.abs(r_query[:, None] - r_train[None, :]), axis=1)
    out_of_range = (r_query < r_train.min()) | (r_query > r_train.max())
    extrapolated = out_of_range | (dist_to_nearest > l)

    mean = np.where(extrapolated, 0.0, mean)
    ci_lo = np.where(extrapolated, 0.0, mean - _Z95 * sd)
    ci_hi = np.where(extrapolated, 0.0, mean + _Z95 * sd)

    return mean, ci_lo, ci_hi, extrapolated
