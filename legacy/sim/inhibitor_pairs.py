"""억제제-기질 **쌍**의 흡착 자유에너지를 다룬다.

왜 이 파일이 필요한가
────────────────────
팩에는 `inhibitor_dG_ads_kJ` 가 하나뿐이었다. 억제제를 바꿔도 같은 값을 쓴다.
그 결과 한 억제제용 상수가 다른 억제제에 그대로 적용돼, 흡착상수가
5,700 배 어긋난 상태로 예측이 나왔다.

문헌이 말하는 것(knowledge/cmp/inhibitor-beyond-monolayer.md):

    ΔG_ads 는 "억제제의 성질"이 아니라 **"억제제 × 기질 쌍의 성질"**이다.
    같은 논문·같은 방법인데 값이 갈린다 — 기질이 다르면 다른 값이다.

따라서 이것은 계수 하나를 고치는 문제가 아니라 **입력 구조**의 문제다.
쌍을 키로 갖지 않는 한 새 억제제가 올 때마다 같은 실패가 반복된다.

무엇을 하는가
────────────
1) (억제제, 기질) 쌍을 키로 ΔG 를 조회한다. 쌍이 없으면 **거부**한다 —
   비슷한 값으로 대체하지 않는다. 그것이 지금까지의 실패 원인이었다.

2) 쌍이 없을 때 **R8(측정 명세)** 를 발행한다: "이 값을 이렇게 재 오시오."
   문헌에 없다고 멈추는 것도, 아무 값이나 넣는 것도 답이 아니다.

3) 등급을 함께 돌려준다. 다른 기질에서 이식한 값은 절대 verified 가 아니다.

⚠ 하지 않는 것
  · 쌍이 없을 때 유사 분자·유사 기질 값으로 대체 (이것이 5,700배 오차의 원인)
  · 데이터에서 ΔG 역산 (관측 3점으로 미지수 2개는 자유도 0 = 피팅)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

R_GAS = 8.314462618          # J/(mol·K)
WATER_MOLAR = 55.34          # mol/L — 물의 몰농도(표준상태 기준 변환용)

__all__ = ["PairDG", "lookup_dG", "K_from_dG", "measurement_spec", "PAIR_TABLE"]


@dataclass(frozen=True)
class PairDG:
    """(억제제, 기질) 쌍의 흡착 자유에너지."""
    inhibitor: str
    substrate: str
    dG_kJ_per_mol: float
    method: str
    source: str
    confidence: str
    notes: Tuple[str, ...] = field(default_factory=tuple)


# ──────────────────────────────────────────────────────────────
# 쌍 표 — 기질이 다르면 다른 줄이다. 이식하지 않는다.
#
# ⚠ 이 표에 값을 추가할 때 지켜야 할 규칙
#   1) 기질을 반드시 적는다. "BTA" 만으로는 줄을 만들 수 없다.
#   2) 측정법을 적는다. 다층 흡착일 때 Langmuir 절편에서 나온 값은
#      ΔG1(첫층)일 뿐 "그 억제제의 ΔG" 가 아니다(문헌 경고).
#   3) 다른 기질에서 가져온 값은 confidence 를 올리지 않는다.
# ──────────────────────────────────────────────────────────────
PAIR_TABLE: Dict[Tuple[str, str], PairDG] = {}


def register(p: PairDG) -> None:
    PAIR_TABLE[(p.inhibitor.lower(), p.substrate.lower())] = p


# ── 쌍이 성질임을 보여주는 결정적 증거 ────────────────────────
# 아래 두 줄은 **같은 논문·같은 방법**인데 값이 8 kJ/mol 갈린다.
# 기질만 다르다. 이것이 "이식 금지" 규칙의 실측 근거다.
register(PairDG(
    "bta", "cu", -30.02, "전기화학(분극·EIS)+양자화학, Langmuir",
    "10.2320/matertrans.m2016310", "literature",
    ("K=3294.9 L/mol (모사 수돗물)",
     "같은 논문의 Fe 값과 8.13 kJ/mol 차 — 기질 의존의 직접 증거",),
))
register(PairDG(
    "bta", "fe", -21.89, "전기화학(분극·EIS)+양자화학, Langmuir",
    "10.2320/matertrans.m2016310", "literature",
    ("K=123.62 L/mol — Cu 대비 K 가 27배 작다",
     "⚠ 이 값을 Cu 에 쓰면 안 된다. 같은 논문이 두 값을 따로 보고했다.",),
))
register(PairDG(
    "bta", "cu-ni", -22.093, "중량법, Langmuir (35 °C)",
    "10.4067/s0717-97072010000100035", "literature",
    ("합금은 순금속과 다른 쌍이다",),
))
register(PairDG(
    "2-mbt", "cu", -5.59, "EQCM, Langmuir (R²=0.91–0.98)",
    "DOI 미확인 — 2차 인용", "unverified",
    ("⚠ 물리흡착 영역의 낮은 값 — 이런 크기도 실제로 보고된다",
     "EQCM 은 θ 를 직접 재므로 다층 판별이 가능한 방법이다",),
))


def lookup_dG(inhibitor: str, substrate: str) -> Optional[PairDG]:
    """쌍으로 조회한다. 없으면 None — **대체하지 않는다.**

    None 을 받았을 때 호출자가 할 일은 유사 값으로 채우는 것이 아니라
    measurement_spec() 을 사용자에게 제시하는 것이다.
    """
    return PAIR_TABLE.get((inhibitor.lower(), substrate.lower()))


def K_from_dG(dG_kJ_per_mol: float, temp_K: float = 298.15) -> float:
    """ΔG → 흡착 평형상수 K [L/mol].

    K = exp(−ΔG/RT) / 55.34

    55.34 로 나누는 이유: 흡착 등온식의 표준상태가 물의 몰농도를 기준으로
    정의된다(문헌 표준). 이 인자를 빼면 K 가 55 배 커진다.
    """
    return float(pow(2.718281828459045, -dG_kJ_per_mol * 1000.0 / (R_GAS * temp_K))
                 / WATER_MOLAR)


def measurement_spec(inhibitor: str, substrate: str) -> List[str]:
    """쌍이 표에 없을 때 발행하는 측정 명세 (R8).

    "문헌에 없다"는 실패가 아니다. 무엇을 어떻게 재면 되는지 말해주는 것은
    제품 기능이다 — 새 슬러리를 넣으려면 이 측정이 필요하다고 알려준다.
    """
    return [
        f"[R8 측정 명세] ({inhibitor} × {substrate}) 쌍의 ΔG_ads 가 없다.",
        "",
        "  ⚠ 다른 기질에서 측정한 값을 쓰면 안 된다. ΔG_ads 는 억제제 단독의",
        "    성질이 아니라 **쌍**의 성질이다 — 기질이 바뀌면 값이 바뀐다.",
        "",
        "  1순위: EIS 농도 스윕",
        "     · 실제 슬러리 pH·산화제 조건에서 억제제 농도를 5점 이상 스윕",
        "     · 전하전달저항 R_ct 로 피복률 θ 를 환산",
        "     · c/θ vs c 플롯의 절편에서 K, K 에서 ΔG",
        "",
        "     ⚠ 함정: c/θ 플롯은 **다층 흡착에서도 거의 직선으로 보인다**.",
        "       'Langmuir R²=0.99' 는 단분자층의 증거가 아니다.",
        "       다층이면 절편에서 나온 값은 ΔG1(첫층)일 뿐이다.",
        "",
        "  2순위: QCM 또는 EQCM",
        "     · θ 를 질량 변화로 **직접** 측정한다",
        "     · 다층 여부를 가릴 수 있는 유일한 결정적 경로다",
        "",
        "  왜 계산으로 대신할 수 없나:",
        "     HOMO-LUMO·Fukui 같은 분자 기술자만으로 ΔG 를 넣는 것은",
        "     문헌이 명시적으로 불충분하다고 경고한다. 표면 흡착에너지를",
        "     직접 계산하는 수준(기질 슬랩 포함)이 필요하며, 그 계산은",
        "     측정보다 비싸다.",
        "",
        "  이 값이 없는 동안 이 모델이 할 수 있는 것:",
        "     · 억제제 농도의 **순위 예측** — 농도가 오르면 제거율이 내린다",
        "     · 절대값 예측 — **할 수 없다**. 축척과 K 가 동시에 미지다.",
    ]
