"""연마 입자의 하중·개수 역학 — 지수를 **계산**하는 절차.

이 모듈의 존재 이유
──────────────────
지금까지 농도·입경 지수는 팩마다 사람이 숫자로 적어 넣는 값이었다
(abrasive_conc_exponent, abrasive_size_exponent). 그건 이론이 아니라
**그 슬러리에서 회귀한 결과**다. 새 슬러리를 넣으려면 또 사람이 정해줘야 하고,
정해주는 근거는 그 슬러리의 데이터뿐이다 — 즉 예측이 아니라 사후 설명이다.

여기서는 지수를 **받지 않는다.** 대신 세 가지 물리 질문에 답하면 지수가 나온다:

    MRR = (접촉 입자 수 N_a) × (입자 하나가 제거하는 양 Q₁)

    N_a : 공급이 정하는 개수          → 지수 p (농도), q (크기)
    Q₁  : 단일입자 법칙                → 지수 α (하중), β (크기)
    F   : 입자 하나가 받는 하중        → 하중 분배 분율 χ

    로그 미분하면 닫힌 형태가 나온다:
        n_C = p · (1 − α·χ)
        n_d = − q · (1 − α·χ) + β

세 질문(입력 → 판단 기준 → 출력)
────────────────────────────────
① 하중을 누가 지는가 (χ)
   입력: 명목 압력, 실접촉면적의 압력 의존성, 입자 수 밀도
   판단: 압력을 올릴 때 접촉 자리 수가 함께 늘어나는가
         늘어남 → 입자가 하중을 나눠 진다 (χ→1)
         안 늘어남 → 돌기가 지고 입자는 국소 하중만 (χ→0)
   출력: χ ∈ [0, 1]

② 제거가 탄성인가 소성인가 (α)
   입력: 입자당 접촉 응력, 제거되는 표면층의 유효 경도
   판단: 접촉 응력 ≳ 표면층 경도 → 소성 (α = 3/2)
         접촉 응력 ≪ 표면층 경도 → 탄성 (α = 2/3)
   출력: α

③ 공급이 단층인가 다층인가 (p, q)
   입력: 패드-웨이퍼 간극, 입자 직경
   판단: 간극 ≈ 입자 직경 → 단층 (p=1, q=2)
         간극 ≫ 입자 직경 → 유효 p < 1
   출력: p, q

판단 기준에 물질명이 없다. 어떤 연마입자·어떤 막질이든 같은 질문에 답한다.

구조적 결과 (전수 검증됨)
────────────────────────
- n_C ≤ 1 이 **구조적 상한**이다. p ≤ 1 이고 0 ≤ (1−αχ) ≤ 1 이므로.
  따라서 문헌의 "4/3"은 이 분해 안에서 나올 수 없다 — 인용하려면 왜 분해 밖인지
  설명해야 한다.
- n_C = 1/3 은 "표면적 지배"가 아니라 **탄성 접촉(α=2/3) + 완전 하중분배(χ=1)**
  의 서명이다. 이름이 물리를 오도해 왔다.
- n_C < 0 은 χ ≈ 1 인 과밀 레짐에서만 나온다.

⚠ 더 중요한 한계 — 지수 자체가 농도의 함수다
────────────────────────────────────────────
자리 점유가 포화하면 겉보기 지수는 측정 창에 따라 움직인다:

    N_a = n_s · (1 − exp(−C/C_h))
    n_loc(λ) = λ·exp(−λ) / (1 − exp(−λ)),   λ = C/C_h

λ→0 에서 1(선형), λ→∞ 에서 0(포화). 같은 물리에서 겉보기 지수가 0.98 → 0.01
로 변한다. 그러므로 **단일 지수를 쓰는 것 자체가 근사**이고, 포화 농도를 아는
계에서는 점유 모델을 직접 쓰는 편이 옳다. 이 모듈은 둘 다 제공한다.

참고: _knowledge_audit/colloid.md §5.3~5.7 (3인자 분해와 전수 검증)
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Dict, List, Optional

# 단일입자 제거 법칙의 하중 지수 α — 접촉 역학이 정하는 값이지 자유 파라미터가 아니다.
ALPHA_PLASTIC = 1.5      # 소성 plowing: 압입 깊이가 하중에 선형, 단면적이 깊이^1.5
ALPHA_ELASTIC = 2.0 / 3  # 탄성(Hertz) 접촉면적: a² ∝ F^(2/3)
ALPHA_MOLECULAR = 0.0    # 분자 스케일 제거: 하중 무관

# 단일입자 법칙의 크기 지수 β — α 와 짝을 이룬다. 둘을 따로 고르면 안 된다.
#   소성 plowing   Q₁ ∝ F^1.5 / d       → α=1.5,   β=-1
#   탄성 접촉면적  Q₁ ∝ F^(2/3)·d^(2/3) → α=2/3,   β=+2/3
#   분자 스케일    Q₁ ∝ d^0.5 (F 무관)  → α=0,     β=+0.5
BETA_FOR_ALPHA: Dict[float, float] = {
    ALPHA_PLASTIC: -1.0,
    ALPHA_ELASTIC: 2.0 / 3.0,
    ALPHA_MOLECULAR: 0.5,
}

# 공급 형태가 정하는 개수 지수
P_MONOLAYER = 1.0        # 단층: 개수 ∝ C
Q_MONOLAYER = 2.0        # 단층: 개수 ∝ 1/d²
Q_FIXED_GAP = 3.0        # 고정 간극에 채워지는 경우 ∝ 1/d³


@dataclass
class LoadRegime:
    """세 질문의 답 + 그로부터 계산된 지수."""
    chi: float                     # 하중 분배 분율 [0,1]
    alpha: float                   # 단일입자 하중 지수
    beta: float                    # 단일입자 크기 지수
    p: float                       # 공급의 농도 지수
    q: float                       # 공급의 크기 지수
    notes: List[str] = field(default_factory=list)
    confidence: str = "estimated"

    @property
    def n_conc(self) -> float:
        """농도 지수 — 계산되는 값."""
        return self.p * (1.0 - self.alpha * self.chi)

    @property
    def n_size(self) -> float:
        """입경 지수 — 계산되는 값."""
        return -self.q * (1.0 - self.alpha * self.chi) + self.beta

    def explain(self) -> str:
        return (f"n_C = p(1−αχ) = {self.p:g}·(1−{self.alpha:.3g}·{self.chi:.3g}) "
                f"= {self.n_conc:+.3f} · "
                f"n_d = −q(1−αχ)+β = {self.n_size:+.3f}")


def decide_alpha(contact_stress_pa: Optional[float],
                 surface_hardness_pa: Optional[float],
                 notes: List[str]) -> tuple[float, str]:
    """② 제거가 탄성인가 소성인가.

    입력: 입자당 접촉 응력, 제거되는 표면층의 유효 경도
    판단: 응력/경도 비. ≳1 이면 소성, ≪1 이면 탄성.
    출력: α 와 근거 등급

    ⚠ 표면층 유효 경도는 **벌크 경도가 아니다.** 화학적으로 변질된 얇은 층의
    경도이고, 이 값의 절대치는 공개 문헌에서 확보되지 않았다(_knowledge_audit
    mechanics.md 의 최대 병목). 값이 없으면 판정하지 않고 그 사실을 신고한다 —
    기본값을 놓으면 "모름"이 "탄성으로 판정됨"으로 둔갑한다.
    """
    if contact_stress_pa is None or surface_hardness_pa is None or surface_hardness_pa <= 0:
        notes.append(
            "⚠ α 미판정: 입자당 접촉 응력 또는 표면층 유효 경도를 모른다. "
            "이 둘의 비가 탄성/소성을 가르는데, 표면층 경도(벌크가 아닌 변질층)는 "
            "공개 문헌에 절대값이 없다. 판정 없이 기본값을 놓으면 '모름'이 "
            "'판정됨'으로 둔갑하므로 판정을 보류한다.")
        return ALPHA_ELASTIC, "unverified"

    ratio = contact_stress_pa / surface_hardness_pa
    if ratio >= 1.0:
        notes.append(
            f"α 판정: 접촉응력/표면층경도 = {ratio:.2f} ≥ 1 → 소성 압입 레짐 "
            f"(α = {ALPHA_PLASTIC})")
        return ALPHA_PLASTIC, "literature"
    if ratio <= 0.3:
        notes.append(
            f"α 판정: 접촉응력/표면층경도 = {ratio:.2f} ≪ 1 → 탄성 접촉 레짐 "
            f"(α = {ALPHA_ELASTIC:.3f})")
        return ALPHA_ELASTIC, "literature"
    # 전이 구간 — 한쪽으로 단정하지 않고 선형 보간하되 등급을 낮춘다
    t = (ratio - 0.3) / 0.7
    a = ALPHA_ELASTIC + t * (ALPHA_PLASTIC - ALPHA_ELASTIC)
    notes.append(
        f"⚠ α 전이구간: 접촉응력/표면층경도 = {ratio:.2f} 는 탄성·소성 경계다. "
        f"α={a:.3f} 로 보간했으나 이 구간은 단일 법칙이 성립하지 않는다.")
    return a, "estimated"


def decide_chi(area_pressure_exponent: Optional[float],
               notes: List[str]) -> tuple[float, str]:
    """① 하중을 누가 지는가.

    입력: 실접촉면적의 압력 의존 지수 (A_r ∝ P^m 의 m)
    판단: 접촉 자리 수가 압력에 비례해 늘면 입자가 하중을 나눠 진다.
          m → 1 이면 자리 지배 (χ → 1), m → 0 이면 공급 지배 (χ → 0).
    출력: χ 와 근거 등급

    왜 이 진단인가: 입자가 총 하중을 나눠 지는지는 직접 못 본다. 대신 압력을
    올렸을 때 접촉 자리가 함께 늘어나는지를 본다 — 늘어난다면 하중이 입자들에게
    재분배되고 있다는 뜻이다.
    """
    if area_pressure_exponent is None:
        notes.append(
            "⚠ χ 미판정: 실접촉면적의 압력 의존성을 모른다. χ 는 농도·입경 지수의 "
            "**부호까지** 정하므로, 모르는 채로 기본값을 쓰면 경향이 반대로 나올 수 "
            "있다. 진단하려면 압력을 바꾸며 반포화 농도가 따라 움직이는지 본다.")
        return 1.0, "unverified"
    m = max(0.0, min(1.0, float(area_pressure_exponent)))
    notes.append(
        f"χ 판정: 실접촉면적 ∝ P^{m:.2f} → 하중 분배 분율 χ = {m:.2f} "
        f"({'자리 지배(입자가 하중을 나눠 짐)' if m > 0.7 else '공급 지배(돌기가 하중을 짐)'})")
    return m, "literature"


def decide_supply(gap_m: Optional[float], d_p_m: Optional[float],
                  notes: List[str]) -> tuple[float, float, str]:
    """③ 공급이 단층인가 다층인가.

    입력: 패드-웨이퍼 간극, 입자 직경
    판단: 간극/직경 비. ≈1 이면 단층, ≫1 이면 여러 겹이 들어가 유효 지수가 낮아진다.
    출력: (p, q) 와 근거 등급
    """
    if gap_m is None or d_p_m is None or d_p_m <= 0:
        notes.append(
            "⚠ 공급 형태 미판정: 패드-웨이퍼 간극을 모른다. 단층으로 가정한다 "
            "(p=1, q=2). 간극이 입자보다 훨씬 크면 실제 지수는 이보다 낮다.")
        return P_MONOLAYER, Q_MONOLAYER, "estimated"

    ratio = gap_m / d_p_m
    if ratio <= 1.5:
        notes.append(f"공급 판정: 간극/입경 = {ratio:.2f} → 단층 (p=1, q=2)")
        return P_MONOLAYER, Q_MONOLAYER, "literature"
    # 여러 겹이 들어가면 접촉에 참여하는 것은 그중 일부다.
    # 참여 분율이 겹 수에 반비례한다고 보면 p_eff = 1/ratio^(1/3) 꼴이 된다.
    p_eff = ratio ** (-1.0 / 3.0)
    notes.append(
        f"⚠ 공급 판정: 간극/입경 = {ratio:.2f} > 1.5 → 다층. 접촉에 참여하는 "
        f"분율만큼 유효 지수가 낮아진다 (p_eff = {p_eff:.3f}). "
        "이 감쇠 형태는 기하 논증이며 문헌 폐형식이 아니다.")
    return p_eff, Q_MONOLAYER, "estimated"


def occupancy_exponent(c: float, c_half: float) -> float:
    """자리 점유 모델의 **국소** 농도 지수.

    n_loc(λ) = λ·exp(−λ) / (1 − exp(−λ)),  λ = C / C_half

    단일 지수가 근사인 이유를 그대로 보여준다: λ→0 에서 1(선형),
    λ→∞ 에서 0(포화). 지수를 인용하려면 어느 λ 에서인지 함께 말해야 한다.
    """
    if c_half <= 0 or c <= 0:
        return 1.0
    lam = c / c_half
    if lam < 1e-6:
        return 1.0
    if lam > 60:
        return 0.0
    return lam * math.exp(-lam) / (1.0 - math.exp(-lam))


def occupancy_ratio(c: float, c_ref: float, c_half: float) -> Optional[float]:
    """포화를 담은 농도 배수 — 단일 멱함수를 대체한다.

    N_a ∝ 1 − exp(−C/C_half) 이므로 기준 대비 배수는 그 비다.
    C_half 를 모르면 None 을 돌려준다(지어내지 않는다).
    """
    if c_half is None or c_half <= 0 or c_ref <= 0:
        return None
    if c <= 0:
        return 0.0
    num = 1.0 - math.exp(-c / c_half)
    den = 1.0 - math.exp(-c_ref / c_half)
    if den <= 0:
        return None
    return num / den


def resolve_regime(
    *,
    area_pressure_exponent: Optional[float] = None,
    contact_stress_pa: Optional[float] = None,
    surface_hardness_pa: Optional[float] = None,
    gap_m: Optional[float] = None,
    d_p_m: Optional[float] = None,
    beta: float = 0.0,
) -> LoadRegime:
    """세 질문에 답해 레짐을 확정하고 지수를 계산한다.

    입력에 물질명이 없다 — 전부 측정 가능한 물리량이다.
    모르는 것이 있으면 그 사실이 notes 와 confidence 에 남는다.
    """
    notes: List[str] = []
    chi, c1 = decide_chi(area_pressure_exponent, notes)
    alpha, c2 = decide_alpha(contact_stress_pa, surface_hardness_pa, notes)
    p, q, c3 = decide_supply(gap_m, d_p_m, notes)

    order = ["unverified", "estimated", "literature", "measured", "verified"]
    conf = min([c1, c2, c3], key=lambda x: order.index(x) if x in order else 0)

    reg = LoadRegime(chi=chi, alpha=alpha, beta=beta, p=p, q=q,
                     notes=notes, confidence=conf)
    notes.append(reg.explain())

    # 구조적 상한 확인 — 계산 결과가 이론 범위를 벗어나면 입력이 틀린 것이다.
    if reg.n_conc > 1.0 + 1e-9:
        notes.append(
            f"⚠ 계산된 농도 지수 {reg.n_conc:.3f} 가 구조적 상한 1 을 넘었다. "
            "p ≤ 1 이고 0 ≤ (1−αχ) ≤ 1 이므로 이는 입력이 모순이라는 뜻이다.")
    return reg
