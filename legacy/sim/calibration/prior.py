"""Tier1/2 물리모델에서 사전 분포(prior)를 만든다 — ORG.md §7.4.

고객 데이터가 도착하기 전에, 우리 물리모델이 각 파라미터를 **얼마나 확신하는지**를
기계가 읽을 수 있는 로그정규 분포로 내놓는다. 그래야 소량의 실측(M3 ingest.py 경로)
만으로도 베이지안 보정이 가능하다.

이 모듈은 sim/engine.py 의 Model 이 아니다. Recipe/WaferResult 스키마와 무관한
독립 유틸리티다(normalize.py·series_scale.py·ptw_vm_schema.py·ingest.py 와 동일한 지위).

series_scale.py 의 경계(같은 파일 상단 docstring)를 이 모듈도 그대로 따른다:

    구조(shape) : 함수 형태·지수·부호·게이트·정점 위치 → 물리에서 유도된다.
    축척(scale) : Kp, 계열별 배율 → 장비·측정계마다 다르고 데이터의 몫이다.

prior.py 는 **읽기 전용**이다 — sim/factors.py·sim/engine.py·sim/params.py·
knowledge/params/*.yaml 을 한 글자도 쓰지 않는다. 이 파일이 하는 일은:

  1) 팩 YAML 이 이미 선언한 값(mu)을 그대로 읽고,
  2) 그 값에 붙은 confidence 등급에서 **폭(sigma_log)만** 유도하고,
  3) 그 폭으로 로그정규 표본을 뽑아 MRR 사전예측분포를 만드는 것.

mu 는 절대 지어내지 않는다. sigma 의 절대 폭도 대부분 지어내지 않되 — 유일하게
literature 등급만 근거가 있다: EVIDENCE-RULES.md 판정#55 가 같은 재료계 문헌
3편(Gong 2024·Wang 2021·Chen 2015) 대조로 확정한 "k*=MRR/(P·rpm) 문헌 간 정상
산포 ≈1.5배"를 1-시그마 로그폭으로 그대로 쓴다. 나머지 등급(verified/measured/
estimated)은 그 기준의 상대 배수이고 **미검증 — 이 프로젝트의 운영 규약이지
문헌값이 아니다**.

unverified(및 정의되지 않은) confidence 는 prior 를 만들지 않는다 — 근거 없는
값에 그럴듯한 분포를 씌우면 그게 오염이다(COMPLETION.md).
"""
from __future__ import annotations

import math
import pathlib
import sys
from dataclasses import dataclass
from typing import Dict, Optional

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import numpy as np                                    # noqa: E402

from sim.params import ParamPack, load_pack            # noqa: E402

__all__ = [
    "ParamPrior", "PriorExcluded",
    "confidence_to_log_sigma", "build_param_priors", "build_kp_prior",
    "sample_priors", "prior_predictive_mrr",
]


class PriorExcluded(ValueError):
    """confidence=unverified(또는 미정의) 값은 prior를 만들지 않는다.

    근거 없는 값에 분포 폭을 지어 붙이면 오염이다 — build_param_priors 는 이
    예외를 잡아 해당 파라미터를 결과에서 명시적으로 제외한다.
    """


@dataclass
class ParamPrior:
    """파라미터 하나의 사전 분포 — mu 는 팩이 선언한 현재 값 그대로, 지어내지 않는다."""
    name: str
    mu: float               # 중심값 = 팩 YAML 선언값
    sigma_log: float        # ln(X) ~ N(ln(mu), sigma_log^2) 의 1-시그마 로그폭
    confidence: str         # verified/measured/literature/estimated
    source: Optional[str]   # 팩 YAML 이 선언한 출처 문자열 그대로
    rationale: str          # 왜 이 sigma인지 한 문장


# ──────────────────────────────────────────────────────────────
# confidence → sigma_log
# ──────────────────────────────────────────────────────────────

# 판정#55(EVIDENCE-RULES.md #55, 2026-09-16): 같은 재료계(산성 KMnO4+알루미나+SiC)
# 독립 문헌 3편(Gong 2024 doi:10.3390/ma17030679 · Wang 2021 doi:10.1149/2162-8777/ac12de ·
# Chen 2015 doi:10.1016/j.apsusc.2015.10.158)의 k*=MRR/(P·rpm) 이 서로 ≈1.5배 안에
# 모인다(E3, 인쇄값 직접 대조) — 이것이 literature 등급 1-시그마 로그폭의 유일한 실측 근거다.
_LOG_SIGMA_LITERATURE = math.log(1.5)

# 등급별 배율 — "등급이 낮을수록 넓다"는 순서(순단조)만 주장한다.
# ⚠ 절대 배율(0.25 / 0.5 / 1.0 / 2.0)은 미검증 — 이 프로젝트의 운영 규약이지
#   문헌값이 아니다. literature(1.0)만 위 판정#55 에서 유도됐다.
_CONFIDENCE_MULTIPLIER: Dict[str, float] = {
    "verified": 0.25,
    "measured": 0.5,
    "literature": 1.0,
    "estimated": 2.0,
}

_RATIONALE: Dict[str, str] = {
    "verified": ("verified 등급 — 표준·교차 확인된 값. literature 산포(판정#55, "
                 "≈1.5배)의 1/4 로그폭(미검증 — 프로젝트 운영 규약)."),
    "measured": ("measured 등급 — 이 재료계에서 직접 역산/측정. literature 산포"
                 "(판정#55, ≈1.5배)의 1/2 로그폭(미검증 — 프로젝트 운영 규약)."),
    "literature": ("literature 등급 — EVIDENCE-RULES.md 판정#55 가 같은 재료계 "
                   "문헌 3편 대조로 확정한 k*=MRR/(P·rpm) 정상 산포 ≈1.5배를 "
                   "1-시그마 로그폭으로 그대로 쓴다."),
    "estimated": ("estimated 등급 — 문헌 대표값의 외삽/대표치. literature 산포"
                  "(판정#55, ≈1.5배)의 2배 로그폭(미검증 — 프로젝트 운영 규약)."),
}


def confidence_to_log_sigma(confidence: str) -> float:
    """confidence 등급 → 로그정규 1-시그마 폭. unverified/미정의 등급은 PriorExcluded."""
    if confidence not in _CONFIDENCE_MULTIPLIER:
        raise PriorExcluded(
            f"confidence={confidence!r} 는 prior를 만들지 않는다 "
            f"(지원 등급: {sorted(_CONFIDENCE_MULTIPLIER)})."
        )
    return _LOG_SIGMA_LITERATURE * _CONFIDENCE_MULTIPLIER[confidence]


# ──────────────────────────────────────────────────────────────
# 팩 → ParamPrior
# ──────────────────────────────────────────────────────────────

def build_param_priors(pack: str) -> Dict[str, ParamPrior]:
    """팩이 선언한 수치 파라미터 전부에서 prior를 만든다.

    문자열 파라미터(막질명·연마입자 종류 등 — 구조를 정의하는 축)는 분포를
    가질 수 없으므로 건너뛴다. unverified(및 미정의) confidence 도 건너뛴다
    (PriorExcluded, "설계 제약 3" — 근거 없는 값에 분포를 씌우지 않는다).
    """
    pk: ParamPack = load_pack(pack)
    out: Dict[str, ParamPrior] = {}
    for key, p in pk.params.items():
        if not isinstance(p.value, (int, float)) or isinstance(p.value, bool):
            continue
        try:
            sigma = confidence_to_log_sigma(p.confidence)
        except PriorExcluded:
            continue
        out[key] = ParamPrior(
            name=key, mu=float(p.value), sigma_log=sigma,
            confidence=p.confidence, source=(p.source or None),
            rationale=_RATIONALE[p.confidence],
        )
    return out


def build_kp_prior(pack: str) -> ParamPrior:
    """Preston 계수 kp_m_per_pa 하나의 prior. build_param_priors(pack)["kp_m_per_pa"]와 동일.

    Kp 는 Recipe.kp_m_per_pa 로 엔진에 직접 꽂히는 유일한 팩 파라미터라
    (sim/engine.py Recipe._FROM_PACK) prior_predictive_mrr 이 이것만 골라 쓴다.
    """
    pk = load_pack(pack)
    p = pk.param("kp_m_per_pa")
    sigma = confidence_to_log_sigma(p.confidence)   # unverified면 여기서 PriorExcluded
    return ParamPrior(
        name="kp_m_per_pa", mu=float(p.value), sigma_log=sigma,
        confidence=p.confidence, source=(p.source or None),
        rationale=_RATIONALE[p.confidence],
    )


# ──────────────────────────────────────────────────────────────
# 표본 추출
# ──────────────────────────────────────────────────────────────

def sample_priors(priors: Dict[str, ParamPrior], n: int, seed: int) -> Dict[str, np.ndarray]:
    """각 prior에서 n개씩 로그정규 표본을 뽑는다. ln(X) ~ N(ln(mu), sigma_log^2).

    median(X) = mu 가 되도록 잡는다(X = mu * exp(sigma_log * Z)) — 표본의
    기하평균이 mu 로 수렴한다(산술평균이 아니다. 로그정규는 산술평균이 더 크다).
    """
    rng = np.random.default_rng(seed)
    out: Dict[str, np.ndarray] = {}
    for name, pr in priors.items():
        z = rng.normal(0.0, 1.0, size=n)
        out[name] = pr.mu * np.exp(pr.sigma_log * z)
    return out


# ──────────────────────────────────────────────────────────────
# prior predictive — Kp 표본을 엔진에 그대로 통과시킨다
# ──────────────────────────────────────────────────────────────

def prior_predictive_mrr(pack: str, n: int = 200, seed: int = 0) -> dict:
    """Kp 사전분포 표본을 sim.engine.simulate 에 그대로 통과시켜 MRR 사전예측분포를 낸다.

    경로: 각 표본마다 ``Recipe(pack=pack, kp_m_per_pa=sample)`` 을 만들어
    ``simulate()`` 를 호출한다 — 엔진은 1바이트도 수정하지 않는다. Kp 는
    Preston MRR=Kp·P·V 의 순수 축척 상수라 이 경로가 "구조는 손대지 않고
    폭만 전파한다"는 설계 제약과 정확히 들어맞는다.

    Kp 외 파라미터(연마입자 지수·산화제 게이트·pH 연화율 등)는
    build_param_priors(pack) 로 prior 는 만들어지지만, 이 함수는 그것들을
    엔진에 통과시키지 않는다 — 그 파라미터들은 대부분 **구조**(지수·게이트·
    재료축)를 인코딩하고 있어서, 한꺼번에 로그정규로 흔들면 series_scale.py
    가 금지한 "계열별 물리 상수 부여"를 이 함수가 프리셋 형태로 우회하는
    셈이 된다(설계 제약 5). 반환값의 excluded_params 에 파라미터별 사유를 남긴다.
    """
    from sim.engine import Recipe, simulate  # 지연 임포트 — 순환 임포트 회피

    kp_prior = build_kp_prior(pack)
    kp_samples = sample_priors({"kp_m_per_pa": kp_prior}, n, seed)["kp_m_per_pa"]

    mrr_samples = np.empty(n, dtype=float)
    for i, kp in enumerate(kp_samples):
        result = simulate(Recipe(pack=pack, kp_m_per_pa=float(kp)))
        mrr_samples[i] = float(np.mean(result.mrr_nm_per_min))

    deterministic = simulate(Recipe(pack=pack))
    deterministic_mrr = float(np.mean(deterministic.mrr_nm_per_min))

    all_priors = build_param_priors(pack)
    excluded_reason = (
        "Kp 외 파라미터는 이 프리셋에서 엔진에 통과시키지 않는다 — 지수·게이트·"
        "재료축 등 구조(shape)를 인코딩할 수 있어, 로그정규로 일괄 흔들면 "
        "series_scale.py 가 금지한 '계열별 물리 상수 부여'를 우회하는 셈이 된다 "
        "(설계 제약 5). 필요하면 sample_priors() 로 개별 표본을 뽑아 "
        "Recipe(pack_overrides=...) 로 직접 실험하라."
    )
    excluded_params = {name: excluded_reason for name in all_priors if name != "kp_m_per_pa"}

    return {
        "pack": pack,
        "n": n,
        "seed": seed,
        "kp_prior": kp_prior,
        "mrr_samples_nm_per_min": mrr_samples,
        "median_nm_per_min": float(np.median(mrr_samples)),
        "mean_nm_per_min": float(np.mean(mrr_samples)),
        "ci90_low_nm_per_min": float(np.percentile(mrr_samples, 5)),
        "ci90_high_nm_per_min": float(np.percentile(mrr_samples, 95)),
        "deterministic_mrr_nm_per_min": deterministic_mrr,
        "excluded_params": excluded_params,
    }
