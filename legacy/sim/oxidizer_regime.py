"""산화제 농도–제거율 관계의 **부호를 계산한다**.

왜 이 모듈이 필요한가
─────────────────────
같은 산화제(과산화수소)를 같은 막질(구리)에 쓴 두 공개 특허가 **반대 부호**를
보인다. 한쪽은 농도를 올릴수록 제거율이 줄고, 다른 쪽은 는다. 막질 이름으로는
이 둘을 가를 수 없다 — 즉 "이 막질은 증가형"이라는 표는 **답이 아니다**.
(그런 표는 새 막질이 오면 무력해진다.)

문헌이 주는 골격 (Kaufman 순환 + 트라이보코로전)
─────────────────────────────────────────────
금속계 제거는 순환이다: 산화막 생성 → 입자가 벗김 → 노출면 재산화.
Stojadinović–Mischler 는 이 순환의 제거율을 다음 비례로 준다:

    MRR ∝ Q(C) / √( H_film(C) )                                    ... (A)

    Q(C)      : 부동태화 전하밀도 — 막이 얼마나 자라는가 (산화제가 결정)
    H_film(C) : 그 막의 기계적 강도 — 얼마나 벗기기 어려운가 (막이 결정)

두 항 **모두** 산화제 농도 C의 함수다. 그러므로 부호는 물질이 아니라
두 항의 **경쟁**으로 정해진다. (A)의 로그미분:

    d ln MRR / d ln C = e_Q(C) − ½·e_H(C)

    e_Q = d ln Q      / d ln C    (≥0, 전기화학적으로 포화하며 0으로 수렴)
    e_H = d ln H_film / d ln C    (막이 치밀·불용화되면 >0)

    ⇒  sign(dMRR/dC) = sign( e_Q − ½·e_H )                         ... (B)

이것이 판정 기준이다. **물질명이 한 글자도 들어가지 않는다.**
새 막질이 와도 e_Q, e_H 두 양만 있으면 부호가 계산되어 나온다.

핵심 통찰 — 증가형과 감소형은 다른 함수가 아니다
──────────────────────────────────────────────
(B)에서 e_Q 는 포화하고(농도가 높아질수록 0으로 감소) e_H 는 보통 유지되거나
커진다. 따라서 충분히 넓은 농도 구간을 보면 **어떤 계든** 처음엔 증가하다
언젠가 꺾인다 — 즉 본래 단봉형이다.

    "증가형"으로 보이는 계 = 정점 C* 가 관측 구간보다 **오른쪽**에 있는 것
    "감소형"으로 보이는 계 = 정점 C* 가 관측 구간보다 **왼쪽**에 있는 것

그러므로 새 함수형을 추가할 이유가 없다. 부족했던 것은 함수형이 아니라
**C* 를 조성으로부터 계산하는 링크**였다. 지금까지 C* 는 팩에 사람이 적어
넣는 상수였고, 그래서 새 슬러리마다 사람이 값을 정해줘야 했다.

⚠ 이 모듈이 하지 않는 것
    절대 MRR 예측. 원 모델조차 실측 대비 한 자릿수 과대였다(저자 자인,
    활성 입자 피복률을 1로 가정한 탓). 여기서는 **부호와 순위**만 다룬다.

⚠ 정적 비율 규칙을 쓰지 않는 이유
    "산화막이 모재보다 무르면 증가형" 같은 규칙은 문헌이 지지하지 않는다.
    같은 금속에 대해 "산화물이 더 단단하다"와 "표면층은 금속보다 무르다"가
    동시에 서술된다. 모순이 아니라, 정적 비율이 애초에 판정량이 아니기
    때문이다. (B)가 요구하는 것은 비율이 아니라 **농도에 대한 도함수**다.

출처: _knowledge_audit/oxidizer_sign.md (1차 출처 15건, DOI 전건 확인)
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import List, Optional, Tuple

__all__ = [
    "OxidizerRegime",
    "SATURATION_ELASTICITY",
    "peak_concentration",
    "sign_of_slope",
    "derive_oxidizer_regime",
]


# ── 전기화학적 포화 ─────────────────────────────────────────────
# Q(C) 는 무한히 자라지 않는다. 부동태막이 완성되면 더 넣어도 전하밀도가
# 늘지 않는다(관측: 농도 1% 부근에서 포화 시작, OCP·Q·RR 동시 포화).
# 가장 단순하면서 그 거동을 담는 형태는 Langmuir 형 포화다:
#
#     Q(C) = Q_max · C / (C + K_sat)
#     e_Q(C) = d ln Q / d ln C = K_sat / (C + K_sat)
#
# 검산: C ≪ K_sat → e_Q → 1 (선형 영역)
#       C = K_sat → e_Q = 0.5
#       C ≫ K_sat → e_Q → 0 (완전 포화, 더 넣어도 막이 안 자람)
#
# K_sat 는 "그 계에서 막이 절반쯤 포화하는 농도"이고 전위계단법으로 측정된다.
SATURATION_ELASTICITY = "langmuir"


@dataclass
class OxidizerRegime:
    """산화제 농도에 대한 거동 판정 결과."""

    peak_wt_pct: float          # C* — 정점 농도 (계산된 값)
    e_Q_at_ref: float           # 기준 농도에서의 생성 탄성도
    e_H: float                  # 강도 탄성도 (농도 무관 상수로 취급)
    behavior: str               # "increasing" | "peaked" | "decreasing"
    basis: str                  # 어떻게 나왔는지 (감사 추적용)
    notes: List[str]

    def __repr__(self) -> str:
        return (f"OxidizerRegime(C*={self.peak_wt_pct:.3g} wt%, "
                f"e_Q={self.e_Q_at_ref:.3f}, e_H={self.e_H:.3f}, "
                f"{self.behavior})")


def peak_concentration(k_sat: float, e_H: float) -> Optional[float]:
    """정점 농도 C* 를 **계산**한다 — 사람이 고르는 값이 아니다.

    정점은 (B) 가 0 이 되는 곳이다:

        e_Q(C*) = ½·e_H
        K_sat / (C* + K_sat) = ½·e_H
        C* = K_sat · (2/e_H − 1)

    읽는 법:
        e_H → 0  (막이 아무리 두꺼워져도 안 단단해짐) → C* → ∞
                 = 정점이 무한히 밀림 = **관측 구간에서는 증가형**
        e_H = 1  → C* = K_sat              (정점이 포화 농도와 일치)
        e_H = 2  → C* = 0
                 = 정점이 원점 = **처음부터 끝까지 감소형**
        e_H > 2  → C* < 0 (물리적으로 존재하지 않음)
                 = 어떤 농도에서도 늘지 않음 = 감소형

    즉 **e_H = 2 가 부호가 뒤집히는 임계**다. 이 값은 (A) 식의 √ 에서
    나온다 — 강도가 제거를 방해하는 효과가 제곱근으로 약화되므로,
    생성이 최대로 기여해도(e_Q=1) 강도가 그 두 배로 자라면 진다.

    반환:
        C* (wt%). 정점이 존재하지 않으면(e_H ≥ 2) None.
    """
    if k_sat <= 0:
        return None
    if e_H <= 0:
        # 강도가 농도와 무관하거나 오히려 무 → 정점 없음, 계속 증가
        return math.inf
    if e_H >= 2.0:
        # 강도 증가가 생성을 항상 이김 → 정점이 원점 이하 = 감소만
        return None
    return k_sat * (2.0 / e_H - 1.0)


def sign_of_slope(C: float, k_sat: float, e_H: float) -> float:
    """농도 C 에서의 기울기 부호 (+1 / 0 / −1).

    식 (B) 를 그대로 평가한다.
    """
    if k_sat <= 0:
        return 0.0
    e_Q = k_sat / (C + k_sat)
    d = e_Q - 0.5 * e_H
    return math.copysign(1.0, d) if abs(d) > 1e-12 else 0.0


def _classify(c_lo: float, c_hi: float, k_sat: float, e_H: float) -> str:
    """관측 구간 양 끝의 기울기 부호로 거동을 분류한다.

    문헌 권고 그대로: 두 끝점 부호 조합이 거동을 결정한다.
        (+,+) → 증가형   (정점이 구간 오른쪽 밖)
        (+,−) → 단봉형   (정점이 구간 안)
        (−,−) → 감소형   (정점이 구간 왼쪽 밖)
    """
    s_lo = sign_of_slope(c_lo, k_sat, e_H)
    s_hi = sign_of_slope(c_hi, k_sat, e_H)
    if s_lo > 0 and s_hi > 0:
        return "increasing"
    if s_lo <= 0 and s_hi <= 0:
        return "decreasing"
    return "peaked"


def derive_oxidizer_regime(
    pack,
    c_window: Optional[Tuple[float, float]] = None,
) -> Optional[OxidizerRegime]:
    """팩의 물성으로부터 산화제 거동을 유도한다.

    필요한 입력 (둘 다 물질명 없는 측정량):
        oxidizer_saturation_wt_pct : K_sat — 부동태막이 절반 포화하는 농도.
                                     전위계단법 Q(C) 곡선에서 읽는다.
        film_hardness_elasticity   : e_H = d ln H_film / d ln C.
                                     AFM 마모깊이 대 농도 기울기의 음수로
                                     대용 측정 가능.

    ⚠ 두 값이 없으면 **추정하지 않고 None 을 돌려준다.**
      지어낸 값으로 부호를 정하면 그것은 예측이 아니라 창작이다.
      호출부는 None 을 받으면 기존 경로(팩 선언 정점)로 물러나되,
      그 사실을 근거 등급에 반영해야 한다.
    """
    notes: List[str] = []

    if not pack.has("oxidizer_saturation_wt_pct"):
        return None
    if not pack.has("film_hardness_elasticity"):
        return None

    k_sat = float(pack.get("oxidizer_saturation_wt_pct"))
    e_H = float(pack.get("film_hardness_elasticity"))

    if k_sat <= 0:
        notes.append("⚠ 포화 농도가 0 이하 — 유도 불가")
        return None

    c_star = peak_concentration(k_sat, e_H)

    # 관측 창: 주어지지 않으면 팩의 현재 농도 주변으로 잡는다.
    if c_window is None:
        c_now = float(pack.get_or("oxidizer_wt_pct", k_sat))
        lo, hi = max(c_now * 0.1, 1e-6), max(c_now * 3.0, k_sat * 3.0)
    else:
        lo, hi = c_window

    behavior = _classify(lo, hi, k_sat, e_H)
    e_Q_ref = k_sat / (float(pack.get_or("oxidizer_wt_pct", k_sat)) + k_sat)

    if c_star is None:
        notes.append(
            f"강도 탄성도 e_H={e_H:.2f} ≥ 2 — 어떤 농도에서도 생성 기여를 "
            "이긴다. 정점이 존재하지 않고 전 구간 감소형이다.")
        c_star_val = 0.0
    elif math.isinf(c_star):
        notes.append(
            f"강도 탄성도 e_H={e_H:.2f} ≤ 0 — 막이 두꺼워져도 단단해지지 "
            "않는다. 정점이 관측 범위 밖으로 밀리며 증가형으로 보인다.")
        c_star_val = math.inf
    else:
        c_star_val = c_star
        notes.append(
            f"정점 농도 C*={c_star:.3g} wt% 가 계산되어 나왔다 "
            f"(K_sat={k_sat:.3g}, e_H={e_H:.2f}). 팩에 적힌 값이 아니다.")

    return OxidizerRegime(
        peak_wt_pct=c_star_val,
        e_Q_at_ref=e_Q_ref,
        e_H=e_H,
        behavior=behavior,
        basis=f"C* = K_sat·(2/e_H − 1); K_sat={k_sat:.4g}, e_H={e_H:.4g}",
        notes=notes,
    )
