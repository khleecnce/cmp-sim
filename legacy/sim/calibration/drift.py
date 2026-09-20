"""새 데이터가 기존 GP 보정과 어긋나는지 감시 — ORG.md §7.4 M3-4 (predict.py 형제 모듈).

역할 경계: 이 모듈은 **보고만 한다**. drift가 감지돼도 재적합(fit_npw.fit/
fit_ptw.fit 재호출)을 이 모듈이 직접 하지 않는다 — 언제/어떻게 재적합할지는
사람 또는 상위 스케줄러(크론)의 판단이다. check_drift()는 인자로 받은
correction 객체의 어떤 필드도 대입하지 않는다(읽기 전용 — 이 경계를
tests/test_drift.py가 불변성 assert로 고정한다).

━━ 임계값 설계 — "자기정합적" 기준만 verdict를 좌우한다 ━━
어떤 문헌도 "RMSE 비율이 얼마 이상이면 드리프트"라고 말하지 않는다(과제
지시사항 그대로). 그래서 verdict를 좌우하는 유일한 기준은 GP 자신의 예측
분포다: 사후표준편차(+관측노이즈)로 정의한 90% CI 밖에 실제로 몇 %가
떨어지는지를, 그 GP가 스스로 예측한 기대치(10%)와 이항검정으로 비교한다
(귀무가설 H0: p=0.10, 대립가설 "더 많이 벗어난다" — 드리프트는 예측이
"나빠지는" 방향만 문제이므로 단측 검정). 이것은 새 임계를 지어낸 게 아니라
GP가 이미 약속한 커버리지(90%)를 스스로 검증하는 것뿐이다.

ratio(=rmse_new/rmse_reference)는 **PROVISIONAL, 문헌근거 없음** — 참고
정보로만 reasons/note에 남기고, verdict를 절대 좌우하지 않는다(과제 지시사항
"휴리스틱 임계를 쓴다면 주 판정으로 쓰지 마라"를 코드로 강제).
"""
from __future__ import annotations

import pathlib
import sys
from dataclasses import dataclass
from typing import List, Optional

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import numpy as np                                        # noqa: E402
from scipy.stats import binomtest                          # noqa: E402

from sim.calibration import fit_npw, fit_ptw                # noqa: E402
from sim.calibration.predict import _gp_sd, _layer_active   # noqa: E402

__all__ = ["DriftReport", "check_drift"]

_Z90 = 1.6448536269514722       # predict.py와 동일한 90% CI z값 — 여기서도 그대로 재사용
_EXPECTED_OUTSIDE_FRAC = 0.10   # 90% CI 밖 기대 비율 — GP 자신이 약속한 커버리지
_MIN_POWER_N = 8                # 이보다 표본이 적으면 이항검정에 검정력이 없다고 본다


@dataclass
class DriftReport:
    n_points: int
    rmse_new: float
    rmse_reference: float          # 적합 당시 LOO RMSE(개선된 층 기준. 없으면 baseline)
    ratio: float                   # rmse_new/rmse_reference — PROVISIONAL, 문헌근거 없음(verdict 미반영)
    z_scores: np.ndarray           # (obs - pred) / sqrt(sigma_gp^2 + sigma_n^2), 활성 층 없으면 전부 nan
    frac_outside_90ci: float       # |z| > 1.6449 인 비율. 활성 층 없으면 nan
    verdict: str                   # "ok" | "watch" | "alarm"
    reasons: List[str]
    note: str


def _reference_rmse(correction, npw_active: bool, ptw_active: Optional[bool] = None) -> float:
    """correction 객체가 이미 들고 있는 적합 당시 LOO RMSE 중, 실제로 적용되는 층에 맞는 값."""
    if isinstance(correction, fit_ptw.PTWCorrection):
        if ptw_active:
            return correction.loo_rmse_ptw
        if npw_active:
            return correction.loo_rmse_npw_only
        return correction.loo_rmse_uncorrected
    # NPWCorrection
    return correction.loo_rmse_gp if npw_active else correction.loo_rmse_baseline


def check_drift(correction, new_ingest_result, *, pack: str,
                 model: str = "tier1.preston_radial") -> DriftReport:
    """새 측정(new_ingest_result)이 기존 correction의 GP 예측분포와 여전히 맞는지 확인한다.

    correction: fit_npw.NPWCorrection | fit_ptw.PTWCorrection (predict.py와 동일 타입).
    new_ingest_result: ingest.IngestResult(또는 그 pyarrow table) — fit_npw.fit/fit_ptw.fit과
      동일한 관측 단위(nm/nm_per_min)·is_excluded/is_missing/is_outlier 규약을 따른다.

    이 함수는 correction을 절대 변형하지 않는다(재적합 없음) — 보고만 한다.
    """
    from sim.engine import Recipe, simulate  # 지연 임포트 — fit_npw.py/fit_ptw.py와 동일 패턴

    if isinstance(correction, fit_ptw.PTWCorrection):
        npw_c = correction.npw_correction
        wafer = "PTW"
    elif isinstance(correction, fit_npw.NPWCorrection):
        npw_c = None
        wafer = "NPW"
    else:
        raise TypeError(
            f"correction은 fit_npw.NPWCorrection | fit_ptw.PTWCorrection 이어야 한다: "
            f"{type(correction)!r}"
        )

    table = new_ingest_result.table if hasattr(new_ingest_result, "table") else new_ingest_result

    r_mm = np.asarray(table.column("r_mm").to_pylist(), dtype=float)
    value_raw = table.column("value_canonical").to_pylist()
    unit_raw = table.column("unit_canonical").to_pylist()
    is_excluded = np.asarray(table.column("is_excluded").to_pylist(), dtype=bool)
    is_missing = np.asarray(table.column("is_missing").to_pylist(), dtype=bool)
    is_outlier = np.asarray(table.column("is_outlier").to_pylist(), dtype=bool)

    keep = ~(is_excluded | is_missing | is_outlier)
    r_kept = r_mm[keep]
    value_kept = np.asarray([value_raw[i] for i in range(len(value_raw)) if keep[i]], dtype=float)
    unit_kept = [unit_raw[i] for i in range(len(unit_raw)) if keep[i]]

    unit_set = set(unit_kept)
    if len(unit_set) > 1:
        raise ValueError(f"관측 단위가 혼재한다: {sorted(unit_set)}")

    recipe = Recipe(pack=pack, wafer=wafer)
    result = simulate(recipe, model=model)
    engine_r_mm = result.radius_m * 1000.0

    if not unit_set:
        r_use = np.array([])
        value_use = np.array([])
    else:
        obs_unit = next(iter(unit_set))
        if obs_unit == "nm":
            engine_field = result.removed_nm
        elif obs_unit == "nm_per_min":
            engine_field = result.mrr_nm_per_min
        else:
            raise ValueError(f"관측량 단위 {obs_unit!r} 는 지원하지 않는다 ('nm'/'nm_per_min'만).")

        r_grid_min, r_grid_max = float(engine_r_mm.min()), float(engine_r_mm.max())
        in_grid = (r_kept >= r_grid_min) & (r_kept <= r_grid_max)
        r_use = r_kept[in_grid]
        value_use = value_kept[in_grid]

    n_points = len(r_use)
    reasons: List[str] = []
    notes: List[str] = []

    if n_points == 0:
        return DriftReport(
            n_points=0, rmse_new=float("nan"), rmse_reference=float("nan"), ratio=float("nan"),
            z_scores=np.array([]), frac_outside_90ci=float("nan"), verdict="watch",
            reasons=["새 데이터에 유효 관측치가 없다(전부 제외/결측/이상치/격자 밖) — 판정 불가."],
            note="유효 관측 0건 — watch로 두고 사람 판단을 기다린다.",
        )

    pred_physics = np.interp(r_use, engine_r_mm, engine_field)
    residual_raw = value_use - pred_physics  # 관측 - 물리모델(NPW/PTW 보정 전)

    if isinstance(correction, fit_ptw.PTWCorrection):
        npw_correction_obj = npw_c  # correction.npw_correction, 위에서 이미 뽑아둠
        npw_active = _layer_active(npw_correction_obj) if npw_correction_obj is not None else False
        ptw_active = _layer_active(correction)
        npw_mean = (fit_npw.apply(npw_correction_obj, r_use)[0] if npw_correction_obj is not None
                    else np.zeros(n_points))
        ptw_mean = fit_ptw.ptw_layer(correction, r_use)[0]
    else:  # NPWCorrection — "npw" 층이 곧 correction 자신이다
        npw_correction_obj = correction
        npw_active = _layer_active(correction)
        ptw_active = None
        npw_mean = fit_npw.apply(correction, r_use)[0]
        ptw_mean = np.zeros(n_points)
    corr_mean = npw_mean + ptw_mean

    corrected_error = residual_raw - corr_mean  # "관측 - (물리모델 + 보정)" = 캘리브레이션 잔여오차
    rmse_new = float(np.sqrt(np.mean(corrected_error ** 2)))

    active_any = npw_active or bool(ptw_active)
    if not active_any:
        rmse_reference = _reference_rmse(correction, npw_active, ptw_active)
        ratio = rmse_new / rmse_reference if rmse_reference not in (0.0, float("nan")) else float("nan")
        reasons.append("보정에 활성 GP 층이 없다(적합 거부/미개선) — 사후분산이 없어 z-score/이항검정을 낼 수 없다.")
        notes.append(f"[PROVISIONAL, 문헌근거 없음] rmse_new/rmse_reference={ratio:.4g} — 참고용, 판정에 사용하지 않음.")
        return DriftReport(
            n_points=n_points, rmse_new=rmse_new, rmse_reference=rmse_reference, ratio=ratio,
            z_scores=np.full(n_points, np.nan), frac_outside_90ci=float("nan"), verdict="watch",
            reasons=reasons, note=" | ".join(notes),
        )

    sd_sq = np.zeros(n_points)
    if npw_active:
        sd_sq = sd_sq + _gp_sd(npw_correction_obj.hyperparams, npw_correction_obj.r_train_mm, r_use) ** 2
    if ptw_active:
        sd_sq = sd_sq + _gp_sd(correction.hyperparams, correction.r_train_mm, r_use) ** 2
    sd_total = np.sqrt(sd_sq)  # 사후분산 + 관측노이즈(sigma_n)가 이미 _gp_sd 안에 합산돼 있다

    z_scores = corrected_error / sd_total
    frac_outside_90ci = float(np.mean(np.abs(z_scores) > _Z90))
    n_outside = int(np.sum(np.abs(z_scores) > _Z90))

    rmse_reference = _reference_rmse(correction, npw_active, ptw_active)
    ratio = rmse_new / rmse_reference if rmse_reference not in (0.0,) and not np.isnan(rmse_reference) else float("nan")
    notes.append(f"[PROVISIONAL, 문헌근거 없음] rmse_new/rmse_reference={ratio:.4g} — 참고용, 판정에 사용하지 않음.")

    if n_points < _MIN_POWER_N:
        verdict = "watch"
        reasons.append(
            f"표본 부족(n={n_points} < {_MIN_POWER_N}) — 이항검정 검정력이 없다. "
            f"90% CI 밖 비율={frac_outside_90ci:.3f}(참고용)이지만 ok로 단언하지 않는다."
        )
    else:
        test = binomtest(n_outside, n_points, _EXPECTED_OUTSIDE_FRAC, alternative="greater")
        p_value = float(test.pvalue)
        if p_value < 0.05:
            verdict = "alarm"
            reasons.append(
                f"90% CI 밖 비율={frac_outside_90ci:.3f}(n={n_points}, 기대 {_EXPECTED_OUTSIDE_FRAC:.2f}) — "
                f"이항검정(H0: p={_EXPECTED_OUTSIDE_FRAC:.2f}, 단측) p={p_value:.4g} < 0.05 → "
                "GP가 스스로 약속한 커버리지를 통계적으로 유의하게 벗어난다."
            )
        else:
            verdict = "ok"
            reasons.append(
                f"90% CI 밖 비율={frac_outside_90ci:.3f}(n={n_points}, 기대 {_EXPECTED_OUTSIDE_FRAC:.2f}) — "
                f"이항검정 p={p_value:.4g} >= 0.05 → 기존 보정과 통계적으로 구분되지 않는다."
            )

    return DriftReport(
        n_points=n_points, rmse_new=rmse_new, rmse_reference=rmse_reference, ratio=ratio,
        z_scores=z_scores, frac_outside_90ci=frac_outside_90ci, verdict=verdict,
        reasons=reasons, note=" | ".join(notes),
    )
