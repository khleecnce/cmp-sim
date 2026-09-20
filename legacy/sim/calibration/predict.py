"""보정된 예측 + 신뢰구간 + 이론 대비 편차 진단 — ORG.md §7.4 M3-4.

fit_npw.NPWCorrection / fit_ptw.PTWCorrection 이 이미 적합한 GP 보정을 물리
엔진(sim.engine.simulate) 예측 위에 얹어서 "최종 예측값 + 그 값을 얼마나
믿어야 하는가"를 하나로 묶는다. 이 모듈은 새 GP를 적합하지 않는다 — 적합은
fit_npw.fit/fit_ptw.fit의 몫이고, 여기서는 이미 적합된 결과를 읽기만 한다
(fit_npw.py·fit_ptw.py·prior.py·sim/engine.py 는 전부 읽기 전용, 한 글자도
바꾸지 않는다).

━━ sigma_nm 설계 — apply()의 "외삽 시 0으로 감쇠"를 그대로 믿지 않는 이유 ━━
fit_npw.apply()/fit_ptw.apply_ptw()는 학습 범위 밖(외삽) 질의점에서 mean과
ci_lo/ci_hi를 **전부 0**으로 강제한다(그 모듈들의 "안전장치 2" — 보정값 자체를
믿지 않겠다는 뜻). 하지만 CI 폭까지 0으로 접으면 "외삽 구간에서 불확실성이
사라진다"는 반대 의미로 읽혀 위험하다 — 실제 GP 사후분산은 학습 데이터에서
멀어질수록 사전분산(sigma_f^2+sigma_n^2)으로 커져야 정상이다(GPML 2006 §2.2).
그래서 이 모듈은:
  · mean(보정값)은 apply()/apply_ptw()가 낸 값을 그대로 믿는다(외삽 시 0).
  · sigma_nm은 fit_npw._rbf/_safe_cholesky를 그대로 재사용해 **마스킹 이전의
    진짜 GP 사후표준편차**를 다시 계산한다 — 외삽 구간에서 실제로 넓어진다.
  (fit_ptw.py가 fit_npw._rbf/_safe_cholesky를 이미 같은 방식으로 재사용하고
  있어 이 파일의 재사용도 이 코드베이스의 기존 관행과 같은 결이다.)

CI는 이 모듈 자체 기준으로 90%(z=1.6448536269514722, 표준정규 95번째
분위수)를 쓴다 — fit_npw/fit_ptw 내부의 95% CI(_Z95=1.95996..., 그 모듈들의
docstring이 "95% 양측 CI"라고 명시)와는 별도의 상수다. 서로 다른 신뢰수준을
같은 이름(_Z95)으로 섞어 쓰면 폭 라벨이 거짓말이 되므로 이 모듈만의 _Z90을 둔다.
"""
from __future__ import annotations

import pathlib
import sys
from dataclasses import dataclass, field
from typing import Dict, List, Optional

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import numpy as np                                            # noqa: E402
from scipy import linalg as sla                                # noqa: E402

from sim.calibration import fit_npw, fit_ptw                   # noqa: E402

__all__ = ["PredictionResult", "predict_radial"]

_Z90 = 1.6448536269514722  # 표준정규 95번째 분위수 (양측 90% CI) — fit_npw._Z95와 다른 상수


@dataclass
class PredictionResult:
    """반경 배열 하나에 대한 예측 결과 — 모든 배열 필드는 radius_mm과 같은 길이."""
    radius_mm: np.ndarray
    physics_nm: np.ndarray        # 무보정 엔진 예측(removed_nm)
    corrected_nm: np.ndarray      # physics_nm + 적용된 보정 층 합
    sigma_nm: Optional[np.ndarray]   # GP 사후표준편차. 보정이 없거나 활성 층이 하나도 없으면 None
    lo_nm: Optional[np.ndarray]      # 90% CI 하한 (sigma_nm이 None이면 None)
    hi_nm: Optional[np.ndarray]      # 90% CI 상한
    deviation_nm: np.ndarray      # corrected_nm - physics_nm (= 적용된 보정의 합)
    deviation_pct: np.ndarray     # deviation_nm / physics_nm * 100 (physics_nm==0인 점은 nan)
    layers_applied: List[str]     # 예: ["npw"], ["npw", "ptw"], [] (전부 미적용/보정없음)
    extrapolation_flags: np.ndarray  # bool — 이 반경이 GP 학습 범위 밖(외삽)인가
    note: str


def _layer_active(correction) -> bool:
    """fit_npw.apply()/fit_ptw.ptw_layer()가 층을 켜는 조건과 정확히 동일한 판정.

    correction이 None이면 활성 아님. NPWCorrection이든 PTWCorrection이든
    improved/hyperparams/n_train 세 필드의 이름과 의미가 같아 그대로 재사용한다.
    """
    if correction is None:
        return False
    return bool(correction.improved and correction.hyperparams and correction.n_train >= 5)


def _gp_sd(hyperparams: Dict[str, float], r_train: np.ndarray, r_query: np.ndarray) -> np.ndarray:
    """마스킹 이전의 진짜 GP 사후표준편차 — fit_npw.apply()의 var 계산과 동일한 식.

    y_train(관측 잔차)에는 의존하지 않는다 — GP 사후분산은 평균(alpha)과 달리
    입력 위치(r_train, r_query)와 커널 하이퍼파라미터만의 함수다(GPML eq. 2.24).
    fit_npw.apply()가 학습 범위 밖에서 이 값을 0으로 뭉개는 것과 달리, 이 함수는
    그 마스킹을 하지 않는다 — 그래서 외삽 구간에서 실제로 커진다.
    """
    l = hyperparams["l_mm"]
    sigma_f = hyperparams["sigma_f"]
    sigma_n = hyperparams["sigma_n"]
    K = fit_npw._rbf(r_train, r_train, sigma_f, l) + (sigma_n ** 2) * np.eye(len(r_train))
    L, _ = fit_npw._safe_cholesky(K)
    K_s = fit_npw._rbf(r_query, r_train, sigma_f, l)
    v = sla.solve_triangular(L, K_s.T, lower=True)
    var = (sigma_f ** 2) - np.sum(v ** 2, axis=0)
    var = np.maximum(var, 0.0) + sigma_n ** 2
    return np.sqrt(var)


def predict_radial(pack: str, radius_mm, *, correction=None,
                    recipe_overrides: Optional[dict] = None,
                    model: str = "tier1.preston_radial") -> PredictionResult:
    """물리 예측(sim.engine.simulate) + (있으면) GP 보정 층을 얹어 최종 예측을 낸다.

    correction: None | fit_npw.NPWCorrection | fit_ptw.PTWCorrection.
      None이면 물리모델 예측만 낸다 — sigma_nm/lo_nm/hi_nm은 전부 None
      (§설계 제약 1: "없는 불확실성을 지어내지 마라". prior.py의 파라미터
      사전분포로 별도 불확실성을 추정할 수도 있으나 이 함수는 시도하지 않는다
      — 그건 다른 축의 불확실성(파라미터)이지 이 GP 잔차층의 불확실성이 아니다).
    recipe_overrides: sim.engine.Recipe 생성자에 그대로 전달하는 필드 덮어쓰기
      (예: {"time_s": 30.0, "pressure_psi": 3.0}). "wafer"를 주지 않으면
      correction이 PTWCorrection일 때만 wafer="PTW"로 자동 지정한다(그 외엔
      Recipe 기본값 "NPW").
    """
    from sim.engine import Recipe, simulate  # 지연 임포트 — fit_npw.py/fit_ptw.py와 동일 패턴

    r_query = np.atleast_1d(np.asarray(radius_mm, dtype=float))
    notes: List[str] = []

    if correction is not None and getattr(correction, "pack", pack) != pack:
        raise ValueError(
            f"predict_radial(pack={pack!r})가 다른 팩으로 적합된 correction.pack="
            f"{correction.pack!r}를 받았다 — 팩이 다르면 잔차 정의가 성립하지 않는다."
        )

    overrides = dict(recipe_overrides) if recipe_overrides else {}
    if "wafer" not in overrides:
        overrides["wafer"] = "PTW" if isinstance(correction, fit_ptw.PTWCorrection) else "NPW"
    recipe = Recipe(pack=pack, **overrides)
    result = simulate(recipe, model=model)
    if result.removed_nm is None:  # pragma: no cover — 방어적, 현재 엔진 경로는 항상 배열을 낸다
        raise ValueError("WaferResult.removed_nm 이 None이다 (time_s<=0?) — 예측을 낼 수 없다.")
    engine_r_mm = result.radius_m * 1000.0
    r_grid_min, r_grid_max = float(engine_r_mm.min()), float(engine_r_mm.max())
    out_of_physics = (r_query < r_grid_min) | (r_query > r_grid_max)
    if np.any(out_of_physics):
        raise ValueError(
            f"질의 반경 중 {int(np.sum(out_of_physics))}개가 물리 엔진 격자 범위 "
            f"[{r_grid_min:.4f}, {r_grid_max:.4f}] mm 밖이다 — 조용히 clamp하지 않는다. "
            "recipe_overrides로 wafer_radius_m/edge_exclusion_m을 조정하거나 질의 반경을 좁혀라."
        )
    physics_nm = np.interp(r_query, engine_r_mm, result.removed_nm)

    layers_applied: List[str] = []
    correction_mean = np.zeros_like(r_query)
    sd_sq = np.zeros_like(r_query)
    have_sd = False
    extrapolated = np.zeros_like(r_query, dtype=bool)

    if correction is None:
        notes.append("correction=None — 물리모델 예측만 사용. sigma_nm/CI 없음(지어내지 않음).")
    elif isinstance(correction, fit_npw.NPWCorrection):
        mean, _, _, extrap = fit_npw.apply(correction, r_query)
        correction_mean = mean
        extrapolated = extrap
        if _layer_active(correction):
            sd_sq = sd_sq + _gp_sd(correction.hyperparams, correction.r_train_mm, r_query) ** 2
            have_sd = True
            layers_applied.append("npw")
        else:
            reason = correction.notes[-1] if correction.notes else "사유 없음"
            notes.append(f"NPW 층 미적용(improved=False 또는 표본 부족): {reason}")
        if np.any(extrap):
            notes.append(
                f"{int(np.sum(extrap))}개 질의점이 NPW GP 학습 범위 밖(외삽) — 보정 평균은 0으로 "
                "감쇠했지만(fit_npw.apply 안전장치), sigma_nm은 마스킹하지 않은 진짜 GP 사후표준편차라 "
                "이 구간에서 오히려 넓어진다(사전분산으로 회귀하는 정상 거동)."
            )
    elif isinstance(correction, fit_ptw.PTWCorrection):
        npw_c = correction.npw_correction
        npw_mean, _, _, npw_extrap = fit_npw.apply(npw_c, r_query) if npw_c is not None else (
            np.zeros_like(r_query), None, None, np.zeros_like(r_query, dtype=bool))
        ptw_mean, _, _, ptw_extrap = fit_ptw.ptw_layer(correction, r_query)
        correction_mean = npw_mean + ptw_mean
        extrapolated = npw_extrap | ptw_extrap

        if npw_c is not None and _layer_active(npw_c):
            sd_sq = sd_sq + _gp_sd(npw_c.hyperparams, npw_c.r_train_mm, r_query) ** 2
            have_sd = True
            layers_applied.append("npw")
        else:
            reason = (npw_c.notes[-1] if (npw_c is not None and npw_c.notes) else "사유 없음")
            notes.append(f"NPW 층 미적용(improved=False 또는 표본 부족): {reason}")

        if _layer_active(correction):
            sd_sq = sd_sq + _gp_sd(correction.hyperparams, correction.r_train_mm, r_query) ** 2
            have_sd = True
            layers_applied.append("ptw")
        else:
            reason = correction.notes[-1] if correction.notes else "사유 없음"
            notes.append(f"PTW 층 미적용(improved=False 또는 표본 부족): {reason}")

        if np.any(extrapolated):
            notes.append(
                f"{int(np.sum(extrapolated))}개 질의점이 NPW 또는 PTW GP 학습 범위 밖(외삽) — "
                "보정 평균은 0으로 감쇠했지만 sigma_nm은 마스킹하지 않은 값이라 이 구간에서 넓어진다."
            )
    else:
        raise TypeError(
            f"correction은 None | fit_npw.NPWCorrection | fit_ptw.PTWCorrection 이어야 한다: "
            f"{type(correction)!r}"
        )

    corrected_nm = physics_nm + correction_mean
    sigma_nm = np.sqrt(sd_sq) if have_sd else None
    lo_nm = corrected_nm - _Z90 * sigma_nm if sigma_nm is not None else None
    hi_nm = corrected_nm + _Z90 * sigma_nm if sigma_nm is not None else None

    deviation_nm = correction_mean
    with np.errstate(divide="ignore", invalid="ignore"):
        deviation_pct = np.where(physics_nm != 0.0, deviation_nm / physics_nm * 100.0, np.nan)
    if np.any(physics_nm == 0.0):
        notes.append("일부 질의점에서 physics_nm=0 — deviation_pct는 해당 점에서 nan(0으로 나누지 않음).")
    if np.any(np.abs(deviation_pct[~np.isnan(deviation_pct)]) > 20.0) if np.any(~np.isnan(deviation_pct)) else False:
        notes.append(
            "⚠ 일부 질의점에서 |deviation_pct| > 20% — 보정(GP)이 물리모델을 크게 뒤집고 있다. "
            "캘리브레이션이 물리를 덮어쓰는 정도이니 이 보정을 그대로 신뢰하기 전에 근본 원인을 살펴라."
        )

    return PredictionResult(
        radius_mm=r_query, physics_nm=physics_nm, corrected_nm=corrected_nm,
        sigma_nm=sigma_nm, lo_nm=lo_nm, hi_nm=hi_nm,
        deviation_nm=deviation_nm, deviation_pct=deviation_pct,
        layers_applied=layers_applied, extrapolation_flags=extrapolated,
        note=" | ".join(notes) if notes else "",
    )
