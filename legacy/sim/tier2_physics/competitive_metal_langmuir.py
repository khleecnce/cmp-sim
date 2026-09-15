"""post-CMP 잔류 금속 — 경쟁 Langmuir 흡착 모델 (Loewenstein·Charpin·Mertens 1999 Eq.22).

지식 근거: knowledge/cmp/post-cmp-residual-metal-prediction-langmuir-scm.md
  §2 (경쟁 Langmuir 모델·파라미터: sigma0=3e12, K_H~1e3, K_Cr~1e6, 자리분율 0.4%),
  §6(A) python verify 블록 (Cr [M] 지수·자리분율·pH3 10nM Cu 오더 검증)
구현 요청: knowledge/cmp/post-cmp-residual-metal-prediction-langmuir-scm.md §8
  `competitive_langmuir_surface(metals, pH, sigma0=3e12, K_H=1e3)` (surface-contamination Lv3-2 요청1)

계약 (엔진과의 경계):
  이 모듈은 순수 함수 라이브러리다. engine.py / models.py에 등록하지 않는다.
  사유: Recipe에 pH·이온농도 필드가 없어(노트 §7, 스키마 부채) engine.Model로 조립할
  입력이 아직 없다. sim/tier2_physics/chelation_surface_charge.py와 같은 지위 —
  "산출값 하나"를 계산하는 함수만 제공한다.

이 함수는 오더값 검증 라이브러리다 — 정밀 예측을 주장하지 않는다. K_i 표가 없어
(노트 §7) 금속별 K_i는 문헌에서 Cr 하나만 확보했고, 나머지 금속은 오더 근사(K_Cr을
대입)로만 검증했다.

미검증 사항 (노트 §6(A) 결과 해석 문단 그대로, 지어내지 않음):
  경쟁 Langmuir에 논문 오더값(σ0 3×10¹², K_H 10³, K_Cr 10⁶)을 넣으면 Cr의 [M] 지수
  0.74가 문헌 Table VI 0.73과 0.01 이내로 재현되지만, pH 지수는 재현되지 않는다
  (모델 −0.12 vs 문헌 −0.39, 3배 어긋남) — 9종 타금속 경쟁항과 K_H가 오더값이기
  때문이며, 노트는 이 불일치를 assert로 명시했다. 즉 이 함수는 [M] 농도 의존성은
  잘 잡지만 pH 의존성은 정밀하게 재현하지 않는다.

함수:
  competitive_langmuir_surface(metals, pH, sigma0=3e12, K_H=1e3) -> dict
    metals: {금속이름: (K_i [L/mol], C_i_free [mol/L])}
    반환: {금속이름: sigma_i [sites/cm²], "_theta": Theta} (Theta = sum(sigma_i)/sigma0)
"""
from __future__ import annotations

# ---------------------------------------------------------------------------
# 문헌 참조값 (노트 §2·§6(A) 그대로 — 여기 외에 새 숫자 없음)
# ---------------------------------------------------------------------------
SIGMA0_DEFAULT = 3.0e12  # sites/cm², Cr3+ 단독 적합(pH 3, 20°C, 2min) 절편의 역수
K_H_DEFAULT = 1e3        # L/mol, 논문 "probably ~1e3" (오더값)
K_CR = 1e6               # L/mol, 논문 "about 1e6" (오더값, Cr3+ 단독 적합)


def competitive_langmuir_surface(
    metals: dict[str, tuple[float, float]],
    pH: float,
    sigma0: float = SIGMA0_DEFAULT,
    K_H: float = K_H_DEFAULT,
) -> dict:
    """경쟁 Langmuir 표면 흡착 (Loewenstein·Charpin·Mertens 1999 Eq.22).

    sigma_i = sigma0 * K_i*[M_i] / (1 + K_H*[H+] + sum_j K_j*[M_j])

    metals: {금속이름: (K_i [L/mol], C_i_free [mol/L])} — 여러 금속이 공통 분모
      (경쟁항 sum_j K_j*[M_j])를 공유한다.
    pH: [H+] = 10**(-pH)로 변환해 분모에 포함.
    반환: {금속이름: sigma_i [sites/cm²], "_theta": Theta}
      Theta = sum(sigma_i)/sigma0 (총 점유율, 0~1).

    근거: 노트 §2 Eq.22, §6(A). K_H·K_i가 오더값이므로(노트 §7 K_i 표 부재) 이
    함수는 오더값 검증용이며 정밀 예측을 주장하지 않는다(모듈 docstring 참조).
    """
    if pH < 0:
        raise ValueError("pH는 0 이상이어야 한다")
    for name, (K_i, C_i) in metals.items():
        if K_i < 0 or C_i < 0:
            raise ValueError(f"{name}: K_i·C_i는 0 이상이어야 한다")

    H = 10 ** (-pH)
    denom = 1 + K_H * H + sum(K_i * C_i for K_i, C_i in metals.values())

    result: dict = {}
    total_sigma = 0.0
    for name, (K_i, C_i) in metals.items():
        sigma_i = sigma0 * K_i * C_i / denom
        result[name] = sigma_i
        total_sigma += sigma_i

    result["_theta"] = total_sigma / sigma0
    return result
