"""PTW 잔차의 잔차 GP 적합 — ORG.md §7 전이 규칙, M3 게이트(fit_npw.py 형제 모듈).

방향성(ORG.md §7, 원문 그대로):
    "NPW 보정치가 PTW의 초기값이 된다. 반대는 아니다. NPW 보정 후 PTW 잔차만 추가 학습."

이 모듈은 그 방향성을 코드로 강제한다:
  · fit()/fit_residuals() 는 npw_correction(NPWCorrection)을 **필수 인자**로 받는다.
    None이면 ValueError로 거부한다(호출자가 실수로 NPW를 거치지 않고 PTW를 단독
    재학습하는 것을 막는다).
  · npw_correction 객체는 읽기만 한다 — 이 모듈 어디서도 그 필드를 대입/변형하지 않는다.
  · PTW 잔차는 반드시 "관측 − 물리모델 − NPW보정(r)" 두 번 뺀 값만 새로 학습한다.
    NPW보정을 빼지 않고 관측 − 물리모델을 그대로 재적합하면 그건 전이가 아니라
    독립 재학습이다 — tests/test_fit_ptw.py 가 이 구분을 고정한다.

핵심 수치(커널·Cholesky·LOO eq.5.12·안전장치)는 재구현하지 않고 fit_npw.py에서
import해 재사용한다. 이 파일이 새로 쓰는 것은: (1) NPW 층을 뺀 "두 번 뺀 잔차"를
만드는 파이프라인, (2) 하이퍼파라미터 초기값을 NPW 값에서 전이하는 다중시작점
생성기(기존 함수가 초기값을 인자로 받지 않아 얇은 래퍼가 필요하다), (3) NPW+PTW
합산 apply, (4) 3자 LOO 안전장치.

이 모듈에는 물리 상수가 하나도 없다.

━━ 하이퍼파라미터 전이 방식 선택 — 초기값만 전이, 페널티 없음 ━━
후보는 세 가지였다:
  (A) 완전 자유 재적합 — NPW 정보를 전혀 안 씀. 이러면 "전이"라는 이름이 무의미해진다.
  (B) 완전 고정 — PTW 최적화를 하지 않고 NPW의 (l, sigma_f, sigma_n)을 그대로 씀.
      PTW엔 패턴밀도발 추가 편차가 얹히므로 최적 길이척도가 NPW와 다를 수 있는데,
      고정하면 그 구조를 원천적으로 못 잡는다.
  (C, 채택) 초기값만 전이 — 다중 시작점 중 첫 시작점을 NPW 값으로 고정하고, 나머지는
      fit_npw와 동일한 무작위 시작점을 쓴 뒤 완전 자유 최적화. NPW가 맞았던 지점
      근처에서 우선 탐색하되, 데이터가 다른 구조를 지지하면 옵티마이저가 자유롭게
      벗어날 수 있다.
  로그공간 가우시안 페널티(예: "폭 0.5")로 (B)와 (C) 사이를 매끄럽게 잇는 방법도
  검토했으나, 그 폭의 근거가 이 프로젝트에 전혀 없다(prior.py가 3곳에서 명시하는
  "confidence 등급별 배율 0.25/0.5/1.0/2.0도 미검증"과 동일한 문제 — 여기서는 그
  최소한의 판정#55 근거조차 없다). 근거 없는 폭을 그럴듯하게 박는 대신 **페널티를
  아예 두지 않고 초기값 전이만 한다** — 이 결정 자체가 미검증 영역을 늘리지 않는
  선택이다.

━━ 발견(2026-09-19 갱신): 기본 경로는 여전히 NPW와 MRR이 동일 — 단, 신규 모델은 연결돼 있다 ━━
sim.engine._MODELS에는 'tier1.preston_radial' 외에 'tier1.pattern_density_effective_pressure'
(Sorooshian 2005 §3.3 실측표, 판정#65)도 **등록되어 있다**. 이 함수의 기본값
model='tier1.preston_radial'로 Recipe(wafer="PTW")를 돌리면 removed_nm/mrr_nm_per_min이
지금도 NPW와 완전히 동일하다(실측, 2026-09-19: np.allclose 통과, test_fit_ptw.py
⑫가 회귀 감시). model='tier1.pattern_density_effective_pressure'를 명시하면 물리 예측이
실제로 달라진다(같은 날 실측: pressure_psi=3, pattern_density=0.50 조건에서
PTW MRR = NPW MRR × 1.5466666666666666, 전 반경에서 상수배 — Preston 식에 밀도별
유효압력비를 곱할 뿐이라 반경 방향 **형상은 바꾸지 않는다**). 참고로 sim/models.py의
구 'tier1.pattern_density'(Boning 1/ρ)는 register_all()이 import 시점에 등록하는데,
fit_ptw.py는 sim.models를 import하지 않으므로 이 모듈이 만드는 실행 컨텍스트에서는
그 이름이 등록돼 있지 않다 — 관련 있는 건 신규 'tier1.pattern_density_effective_pressure'
뿐이다.

이 모듈의 fit()에 그 모델을 넘기면 **이제 실제로 돌아간다**. 단 조건이 좁다:
local_density가 표 격자 {0.10, 0.50, 0.90} 안이고 pressure_psi가 {3, 7}이어야 하며,
그 밖이면 조용히 폴백하지 않고 ValueError로 크게 실패한다(test_fit_ptw.py
test_pattern_density_effective_pressure_grid_gate_via_fit이 양쪽을 고정).

⚠ 이력(같은 날 2026-09-19, 남겨두는 이유는 동형 재발을 막기 위해서다): 처음에는
격자 **안** 값(0.50)도 ValueError가 났다. 원인은 격자가 아니라 **타입**이었다 —
fit()이 meta['pattern_density']를 str(...)로 채우는데(Recipe.meta가 Dict[str, str]로
선언돼 있으므로 생산자 쪽이 규약을 지킨 것이다) 소비자인 엔진이 캐스팅 없이
(0.10, 0.50, 0.90) 리터럴과 비교했다. 같은 결함이 CLI·Studio에도 있었고 — 거기서는
예외조차 안 나고 **진단이 조용히 스킵되면서 "0.5는 표에 없는 값(지원: 0.10/0.50/0.90)"
이라는 거짓 안내**가 붙었다. 엔진에 `_meta_pattern_density()`를 넣어 소비 경계에서
캐스팅하도록 고쳤다.

⚠ 그래도 **기본값은 바꾸지 않는다**(아래 fit() docstring 참고). 이 모델은 밀도별
유효압력비를 Preston 식에 **곱할 뿐**이라 전 반경 상수배이고 반경 방향 **형상은
바꾸지 않는다**(실측: pressure_psi=3·density=0.50에서 ×1.5466666666666666,
np.ptp(ratio) < 1e-9). 즉 반경 잔차를 학습하는 이 모듈의 GP 보정에 새 정보를 주지
않는다 — "연결됐으니 예측이 좋아진다"고 기대할 근거가 없다. 테스트에서 쓰는
"패턴밀도 의존 편차"는 여전히 전부 **인위적으로 주입한 값**이고, 이 모듈이 실제로
계산해내는 값이 아니다(테스트 docstring에 명시).
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
from scipy.optimize import minimize                             # noqa: E402

from sim.calibration import fit_npw                             # noqa: E402
from sim.calibration.fit_npw import NPWCorrection                # noqa: E402
from sim.calibration.ptw_vm_schema import PTWVMInput, is_npw_equivalent  # noqa: E402

__all__ = [
    "PTWCorrection", "fit", "fit_residuals", "apply_ptw", "npw_layer", "ptw_layer",
]

_Z95 = fit_npw._Z95


@dataclass
class PTWCorrection:
    """PTW 잔차(2단계) GP 적합 결과. apply_ptw() 가 NPW 층 + PTW 층 합을 낸다."""
    pack: str
    npw_prior: dict                    # npw_correction.to_prior_dict() 스냅샷 — 전이 근거 기록
    n_train: int
    n_dropped: Dict[str, int]
    hyperparams: Dict[str, float]      # PTW 층 GP 하이퍼파라미터 — 거부/미개선 시 {}
    loo_rmse_uncorrected: float        # (a) 무보정: 관측 − 물리모델
    loo_rmse_npw_only: float           # (b) NPW보정만: 관측 − 물리모델 − NPW층 (GP 적용 전)
    loo_rmse_ptw: float                # (c) NPW+PTW보정: (b)의 잔차에 PTW GP까지 적용한 LOO RMSE
    improved: bool                     # (c) < (b) 인가 — False면 apply_ptw는 NPW 층까지만 적용
    converged: bool
    notes: List[str]
    # apply_ptw 재계산에 필요 — 직렬화 대상 아님(to_dict 제외)
    npw_correction: Optional[NPWCorrection] = field(default=None, repr=False)
    r_train_mm: Optional[np.ndarray] = field(default=None, repr=False)
    residual_train: Optional[np.ndarray] = field(default=None, repr=False)  # NPW 층을 뺀 "두 번 뺀 잔차"

    def to_dict(self) -> dict:
        """JSON 직렬화 가능한 순수 dict — npw_correction 객체·학습 원자료는 제외한다."""
        return {
            "pack": self.pack,
            "npw_prior": dict(self.npw_prior),
            "n_train": self.n_train,
            "n_dropped": dict(self.n_dropped),
            "hyperparams": dict(self.hyperparams),
            "loo_rmse_uncorrected": self.loo_rmse_uncorrected,
            "loo_rmse_npw_only": self.loo_rmse_npw_only,
            "loo_rmse_ptw": self.loo_rmse_ptw,
            "improved": self.improved,
            "converged": self.converged,
            "notes": list(self.notes),
        }


# ──────────────────────────────────────────────────────────────
# 하이퍼파라미터 전이 — 초기값만(위 docstring "채택 (C)" 근거)
# ──────────────────────────────────────────────────────────────

def _fit_hyperparams_transfer(r: np.ndarray, y: np.ndarray, *,
                               npw_hyperparams: Dict[str, float],
                               seed: int, n_restarts: int
                               ) -> Tuple[float, float, float, bool]:
    """다중 시작점 L-BFGS-B — 단 첫 시작점은 NPW 하이퍼파라미터로 고정한다.

    커널·음의 로그주변우도·경계는 fit_npw.py에서 그대로 import해 쓴다(재구현 금지).
    fit_npw._fit_hyperparams는 시작점을 인자로 받지 않으므로, "첫 시작점만 NPW 값으로
    바꾼다"는 전이 특유의 요구를 위해 이 얇은 래퍼가 필요하다 — 나머지 시작점 생성
    로직은 fit_npw._fit_hyperparams와 동일한 분포를 그대로 따른다(일관성).
    """
    r_span = float(r.max() - r.min())
    if r_span <= 0.0:
        r_span = 1.0
    y_std = float(np.std(y))
    if y_std <= 0.0:
        y_std = 1e-6

    rng = np.random.default_rng(seed)
    if npw_hyperparams:
        first = (npw_hyperparams["l_mm"], npw_hyperparams["sigma_f"], npw_hyperparams["sigma_n"])
    else:
        first = (r_span / 4.0, y_std, 0.1 * y_std + 1e-6)
    starts = [first]
    for _ in range(max(n_restarts - 1, 0)):
        l0 = r_span * rng.uniform(0.05, 1.5)
        sf0 = y_std * rng.uniform(0.1, 3.0)
        sn0 = y_std * rng.uniform(0.01, 1.0) + 1e-6
        starts.append((l0, sf0, sn0))

    best = None
    for l0, sf0, sn0 in starts[:max(n_restarts, 1)]:
        x0 = np.log(np.clip(np.array([l0, sf0, sn0], dtype=float), 1e-300, None))
        x0 = np.clip(x0, fit_npw._LOG_THETA_BOUNDS[0][0], fit_npw._LOG_THETA_BOUNDS[0][1])
        res = minimize(fit_npw._neg_log_marginal_likelihood, x0, args=(r, y), method="L-BFGS-B",
                        bounds=fit_npw._LOG_THETA_BOUNDS)
        if best is None or res.fun < best.fun:
            best = res

    l, sigma_f, sigma_n = np.exp(best.x)
    return float(l), float(sigma_f), float(sigma_n), bool(best.success)


# ──────────────────────────────────────────────────────────────
# 공개 API
# ──────────────────────────────────────────────────────────────

def fit_residuals(pack: str, r_mm: np.ndarray, residual_raw: np.ndarray,
                   npw_correction: Optional[NPWCorrection], *,
                   n_dropped: Optional[Dict[str, int]] = None,
                   seed: int = 0, n_restarts: int = 5) -> PTWCorrection:
    """(반경, "관측 − 물리모델" 잔차) → NPW 층을 뺀 뒤 그 위에서만 PTW GP를 적합한다.

    residual_raw 는 **NPW 보정을 아직 빼지 않은** 값이다(관측 − 물리모델). 이 함수가
    NPW 층(fit_npw.apply)을 계산해 빼는 것 자체가 전이 방향성의 핵심이다 — 호출자가
    이미 뺀 값을 넘기면 이 함수가 한 번 더 빼서 이중차감이 되므로, residual_raw의
    정의를 이 docstring과 정확히 맞춰야 한다.

    npw_correction 은 필수다(None이면 ValueError) — ORG §7: "NPW 보정치가 PTW의
    초기값이 된다. 반대는 아니다." 이 함수는 npw_correction의 어떤 필드도 쓰지
    않는다(읽기만, fit_npw.apply를 통해서만 접근).

    §안전장치 1(3자 LOO): (a) 무보정 loo_rmse_uncorrected, (b) NPW보정만
    loo_rmse_npw_only, (c) NPW+PTW보정 loo_rmse_ptw 를 전부 계산한다. (c) >= (b) 면
    improved=False — apply_ptw()는 PTW 층을 얹지 않고 NPW 층까지만 돌려준다.
    §안전장치 3(표본 부족): 유효 학습점 < 5 면 PTW GP 적합을 시도하지 않는다.
    """
    if npw_correction is None:
        raise ValueError(
            "PTW 적합은 NPW 적합 결과(npw_correction)를 필수로 요구한다 (ORG.md §7 전이 "
            "규칙: 'NPW 보정치가 PTW의 초기값이 된다. 반대는 아니다.'). None을 받았다."
        )

    r = np.asarray(r_mm, dtype=float)
    y_raw = np.asarray(residual_raw, dtype=float)
    n_train = len(r)
    dropped = dict(n_dropped) if n_dropped is not None else {}
    npw_prior = npw_correction.to_prior_dict()

    if n_train > 0:
        npw_mean, _, _, _ = fit_npw.apply(npw_correction, r)
    else:
        npw_mean = np.zeros(0)
    y_after_npw = y_raw - npw_mean  # "두 번 뺀 잔차" — 이 함수가 새로 학습하는 대상

    loo_rmse_uncorrected = float(np.sqrt(np.mean(y_raw ** 2))) if n_train > 0 else float("nan")
    loo_rmse_npw_only = float(np.sqrt(np.mean(y_after_npw ** 2))) if n_train > 0 else float("nan")

    if n_train < 5:
        return PTWCorrection(
            pack=pack, npw_prior=npw_prior, n_train=n_train, n_dropped=dropped,
            hyperparams={}, loo_rmse_uncorrected=loo_rmse_uncorrected,
            loo_rmse_npw_only=loo_rmse_npw_only, loo_rmse_ptw=float("nan"),
            improved=False, converged=False,
            notes=[f"유효 학습점 {n_train}개 < 5 — PTW GP 적합을 거부한다. NPW 보정까지만 적용."],
            npw_correction=npw_correction, r_train_mm=r, residual_train=y_after_npw,
        )

    notes: List[str] = []
    l, sigma_f, sigma_n, converged = _fit_hyperparams_transfer(
        r, y_after_npw, npw_hyperparams=npw_correction.hyperparams, seed=seed, n_restarts=n_restarts
    )
    if not converged:
        notes.append("L-BFGS-B가 최선 재시작 기준으로도 수렴하지 않았다 — PTW 하이퍼파라미터 신뢰도 낮음.")
    if npw_correction.hyperparams:
        notes.append(
            f"초기값 전이: 첫 시작점 = NPW 하이퍼파라미터 {npw_correction.hyperparams} "
            "(위 모듈 docstring '채택 (C)' — 페널티 없이 초기값만)."
        )
    else:
        notes.append("NPW 보정에 하이퍼파라미터가 없다(적합 거부/미개선) — 전이할 초기값 없이 기본 시작점 사용.")

    loo_err, _ = fit_npw._loo_errors(r, y_after_npw, l, sigma_f, sigma_n)
    loo_rmse_ptw = float(np.sqrt(np.mean(loo_err ** 2)))
    improved = loo_rmse_ptw < loo_rmse_npw_only
    if not improved:
        notes.append(
            f"LOO RMSE(NPW+PTW)={loo_rmse_ptw:.6g} >= LOO RMSE(NPW보정만)={loo_rmse_npw_only:.6g} "
            "— PTW 층이 구조를 지지하지 않는다. PTW 층을 적용하지 않는다(NPW 보정까지만)."
        )

    hyperparams = {"l_mm": l, "sigma_f": sigma_f, "sigma_n": sigma_n}
    return PTWCorrection(
        pack=pack, npw_prior=npw_prior, n_train=n_train, n_dropped=dropped,
        hyperparams=hyperparams, loo_rmse_uncorrected=loo_rmse_uncorrected,
        loo_rmse_npw_only=loo_rmse_npw_only, loo_rmse_ptw=loo_rmse_ptw,
        improved=improved, converged=converged, notes=notes,
        npw_correction=npw_correction, r_train_mm=r, residual_train=y_after_npw,
    )


def fit(pack: str, ptw_input: PTWVMInput, ingest_result, npw_correction: Optional[NPWCorrection], *,
        model: str = "tier1.preston_radial", seed: int = 0, n_restarts: int = 5) -> PTWCorrection:
    """ingest.IngestResult → 물리 예측과의 잔차(무차감) → NPW 층 차감 → PTW GP 적합.

    ptw_vm_schema.is_npw_equivalent(ptw_input)이 True면(레이아웃도 시계열도 없음)
    PTW 적합 자체를 거부하고 NPW 보정만 담아 반환한다 — §5.3 결론을 코드로 강제.

    관측 단위·엔진 격자 범위 처리·is_excluded/missing/outlier 제외는 fit_npw.fit과
    동일한 규칙을 따른다(재구현이 아니라 같은 판단을 이 파이프라인에도 적용).

    ⚠ model 기본값은 'tier1.preston_radial'로 유지한다 — 바꾸지 마라. wafer="PTW"를
    이 기본 모델로 돌리면 물리 예측은 지금도 NPW와 동일한 수가 나온다(모듈 docstring
    "발견" 참고, test_fit_ptw.py가 회귀 감시).

    model='tier1.pattern_density_effective_pressure'(Sorooshian 2005 §3.3 실측표,
    판정#65)를 넘기는 것은 **이제 가능하다**. 다만 기본값으로 삼지 않는 이유가 둘 있다:
    (1) 적용 조건이 좁다 — local_density ∈ {0.10, 0.50, 0.90}, pressure_psi ∈ {3, 7}
        밖이면 ValueError다. 기본값으로 두면 기존 호출자 대부분이 깨진다.
    (2) 더 중요하게, 이 모델은 전 반경에 **상수배**를 곱할 뿐 반경 방향 형상을 바꾸지
        않는다. 이 모듈이 학습하는 것은 반경 잔차이므로, 스케일만 바뀌는 입력은 GP
        보정에 새 정보를 주지 않는다. 연결 자체는 의미가 있으나(물리 경로가 살아났다)
        **이 모듈의 예측 정확도를 올려주는 종류의 변화는 아니다.**
        """
    from sim.engine import Recipe, simulate  # 지연 임포트 — 순환 임포트 회피(fit_npw.py와 동일 패턴)

    if npw_correction is None:
        raise ValueError(
            "PTW 적합은 NPW 적합 결과(npw_correction)를 필수로 요구한다 (ORG.md §7 전이 규칙)."
        )

    if is_npw_equivalent(ptw_input):
        return PTWCorrection(
            pack=pack, npw_prior=npw_correction.to_prior_dict(), n_train=0, n_dropped={},
            hyperparams={}, loo_rmse_uncorrected=float("nan"), loo_rmse_npw_only=float("nan"),
            loo_rmse_ptw=float("nan"), improved=False, converged=False,
            notes=["ptw_vm_schema.is_npw_equivalent(ptw_input)=True — local_density와 "
                   "prev_layer_topography가 모두 없어 이 PTW 입력은 NPW와 구분되지 않는다 "
                   "(§5.3 결론). PTW 적합을 거부하고 NPW 보정만 반환한다."],
            npw_correction=npw_correction,
        )

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

    meta = {}
    if ptw_input.local_density is not None:
        meta["pattern_density"] = str(ptw_input.local_density)
    recipe = Recipe(pack=pack, wafer="PTW", meta=meta)
    result = simulate(recipe, model=model)
    engine_r_mm = result.radius_m * 1000.0

    if not unit_set:
        obs_unit = None
        engine_field = result.removed_nm
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
                f"관측량 단위 {obs_unit!r} 는 PTW 잔차 정의를 지원하지 않는다 "
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
    residual_raw = value_use - pred

    result_obj = fit_residuals(pack, r_use, residual_raw, npw_correction,
                                n_dropped=n_dropped, seed=seed, n_restarts=n_restarts)
    result_obj.notes = notes + result_obj.notes
    return result_obj


def npw_layer(correction: PTWCorrection, radius_mm) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """PTW 보정 중 NPW 층만 조회한다 — fit_npw.apply를 그대로 위임한다."""
    return fit_npw.apply(correction.npw_correction, radius_mm)


def ptw_layer(correction: PTWCorrection, radius_mm) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """PTW 보정 중 PTW 층만 조회한다(NPW 층 제외). 미개선/거부 시 전부 0.

    수식은 fit_npw.apply와 동일한 GP 사후식이지만 학습 데이터가 "두 번 뺀 잔차"라는
    점만 다르다 — 커널·Cholesky·외삽 가드는 fit_npw.py의 프리미티브를 그대로 쓴다.
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

    K = fit_npw._rbf(r_train, r_train, sigma_f, l) + (sigma_n ** 2) * np.eye(len(r_train))
    L, _ = fit_npw._safe_cholesky(K)
    alpha = sla.cho_solve((L, True), y_train)

    K_s = fit_npw._rbf(r_query, r_train, sigma_f, l)
    mean = K_s @ alpha
    v = sla.solve_triangular(L, K_s.T, lower=True)
    var = (sigma_f ** 2) - np.sum(v ** 2, axis=0)
    var = np.maximum(var, 0.0) + sigma_n ** 2
    sd = np.sqrt(var)

    dist_to_nearest = np.min(np.abs(r_query[:, None] - r_train[None, :]), axis=1)
    out_of_range = (r_query < r_train.min()) | (r_query > r_train.max())
    extrapolated = out_of_range | (dist_to_nearest > l)

    mean = np.where(extrapolated, 0.0, mean)
    ci_lo = np.where(extrapolated, 0.0, mean - _Z95 * sd)
    ci_hi = np.where(extrapolated, 0.0, mean + _Z95 * sd)

    return mean, ci_lo, ci_hi, extrapolated


def apply_ptw(correction: PTWCorrection, radius_mm) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """(mean, ci_lo, ci_hi, extrapolated) = NPW 층 + PTW 층의 합.

    두 층을 독립 GP로 취급해 분산을 더한다(sd_total = sqrt(sd_npw^2 + sd_ptw^2)) —
    두 GP가 서로 다른 학습 데이터(NPW 웨이퍼 vs "NPW 층을 뺀 PTW 잔차)로 독립 적합됐다는
    전제다. extrapolated는 두 층 중 하나라도 외삽이면 True — 어느 한 층을 못 믿으면
    합도 못 믿는다는 보수적 규약. improved=False(§안전장치 1)면 PTW 층은 0이라 이 합은
    자동으로 NPW 층만 반환한다(npw_layer와 동일값).
    """
    r_query = np.atleast_1d(np.asarray(radius_mm, dtype=float))

    npw_mean, npw_lo, npw_hi, npw_extrap = npw_layer(correction, r_query)
    ptw_mean, ptw_lo, ptw_hi, ptw_extrap = ptw_layer(correction, r_query)

    total_mean = npw_mean + ptw_mean
    extrapolated = npw_extrap | ptw_extrap

    sd_npw = (npw_hi - npw_mean) / _Z95
    sd_ptw = (ptw_hi - ptw_mean) / _Z95
    sd_total = np.sqrt(sd_npw ** 2 + sd_ptw ** 2)

    ci_lo = np.where(extrapolated, 0.0, total_mean - _Z95 * sd_total)
    ci_hi = np.where(extrapolated, 0.0, total_mean + _Z95 * sd_total)
    total_mean = np.where(extrapolated, 0.0, total_mean)

    return total_mean, ci_lo, ci_hi, extrapolated
