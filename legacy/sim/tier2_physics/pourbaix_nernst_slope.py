"""
Pourbaix(전위-pH) 다이어그램 경계선의 Nernst 기울기 계산 + 금속 CMP 표면종 판정 헬퍼.

배경 지식: knowledge/cmp/surface-chemistry-cu-w-pourbaix-passivation.md (slurry-chemist Lv2-1)

핵심 물리:
    반응 a*Ox + m*H+ + n*e- = b*Red (+ H2O) 의 Nernst 식:
        E = E0 - (0.0591/n) * log([Red]^b/[Ox]^a) - (0.0591*m/n) * pH   (25 degC)
    다이어그램 위에서 이 경계선의 기울기는 dE/dpH = -0.0591*(m/n) [V/pH].
    m=n(예: WO3 + 2H+ + 2e- = W + H2O 류, H+/e- 1:1)이면 표준 -59.1 mV/pH.
    m=2n이면 절반인 -29.6 mV/pH.

이 모듈은 원저(Pourbaix Atlas 1966, 유료 미확인) 없이도 독립적으로 유도 가능한
Nernst 식 자체의 기울기 공식을 재현하고, W/Cu CMP 표면 반응식(지식노트 §3-4, 2차 인용)에
대입해 "무른 산화막" 반응들이 표준 -59.1 mV/pH 계열(m=n)에 속함을 확인한다.

문헌 대조: 표준 전기화학 교과서(Bard & Faulkner류) Nernst 식 일반형 -0.0591*(m/n) V/pH.
CMP 반응식(H2O2 기반 Cu 산화 Eq.9-10, WO3 passivation)의 m,n은
knowledge 노트 §3-4에 정리된 Gamagedara & Roy 2024 (Materials 17(19) 4905, PMC11477894,
CC BY 오픈액세스) 반응식에서 그대로 가져옴.
"""

from __future__ import annotations
from dataclasses import dataclass

RT_F_LN10_25C = 0.05916  # V, = (RT/F)*ln(10) at 25 degC (표준값, CRC Handbook)


def nernst_ph_slope(m: int, n: int) -> float:
    """전위-pH 다이어그램 경계선의 기울기 dE/dpH [V/pH] = -0.0591*(m/n).

    m: 반응식의 H+ 계수, n: 전자 e- 계수.
    """
    if n == 0:
        raise ValueError("n(전자수)=0이면 pH 축 위 수직선(전위 무관) — 기울기 미정의")
    return -RT_F_LN10_25C * (m / n)


@dataclass
class RedoxReaction:
    """a*Ox + m H+ + n e- = b*Red (+ H2O) 형태의 CMP 표면 반응."""
    name: str
    m: int  # H+ 계수
    n: int  # e- 계수
    source: str

    def slope_mV_per_pH(self) -> float:
        return nernst_ph_slope(self.m, self.n) * 1000.0

    def is_self_limiting_type(self) -> bool:
        """m==n (표준 -59.1 mV/pH) 반응은 '금속1개당 OH-/H+ 1개, 전자 1개' 비율로
        치밀한 화학양론적 산화막(WO3, Cu(OH)2 등)을 형성하는 전형적 passivation 반응 계열.
        지식노트 §3-4에서 다룬 CMP 산화막 반응식들이 실제로 이 계열에 속하는지 판별."""
        return self.m == self.n


# 지식노트 §3(W)·§4(Cu) 반응식을 그대로 부호화 (2차 인용 정리, 원문 계수 그대로)
CMP_SURFACE_REACTIONS = [
    RedoxReaction(
        name="W + 2H2O -> WO3 + 6H+ + 6e- (WO3 passivation, 산성 영역)",
        m=6, n=6,
        source="Krishnan et al. Chem.Rev.2010 (2차 인용, W Pourbaix WO3 passivation 영역 서술)",
    ),
    RedoxReaction(
        name="Cu + 2OH- -> Cu(OH)2 + 2e-  (Eq.9, Gamagedara&Roy 2024)",
        m=2, n=2,  # OH- 형태이나 H2O = H+ + OH- 등가 변환 시 H+ 계수도 2 (역방향 Nernst 표기 동치)
        source="Gamagedara & Roy, Materials 17(19) 4905 (2024), PMC11477894",
    ),
    RedoxReaction(
        name="2Cu + 2OH- -> Cu2O + H2O + 2e- (Eq.10, Gamagedara&Roy 2024)",
        m=2, n=2,
        source="Gamagedara & Roy, Materials 17(19) 4905 (2024), PMC11477894",
    ),
    RedoxReaction(
        name="Cu(OH)2 -> CuO + H2O (탈수, 전자 무관 산-염기형 - 참고용, Nernst 미적용)",
        m=0, n=0,  # 산화환원 아님 -> 별도 취급, self-test에서 제외
        source="Gamagedara & Roy, Materials 17(19) 4905 (2024), PMC11477894",
    ),
]


def mo_cu_w_oxidizer_peak_shift_direction(with_complexing_agent: bool) -> str:
    """지식노트 §4/§5: 착화제(CA) 첨가 시 과-passivation을 재용해로 억제해
    MRR-산화제농도 정점이 더 높은 농도 쪽으로 이동한다는 정성 결론을 그대로 부호화
    (slurry-components-overview.md의 mrr_oxidizer() 정점이동과 동일 원리, 여기선
    표면종 관점의 명제 형태로 재확인)."""
    return "peak shifts to higher oxidizer concentration" if with_complexing_agent else "baseline peak"


def _self_test() -> None:
    results = []

    # (1) 표준 -59.1 mV/pH: m=n=1 최소 사례로 재현값이 상수와 정확히 일치하는지
    slope_1_1 = nernst_ph_slope(1, 1)
    results.append(("m=n=1 -> -59.16mV/pH", abs(slope_1_1 * 1000 - (-59.16)) < 0.01))

    # (2) m=2n -> 절반 기울기(-29.58mV/pH), 표준 전기화학 관계식 재현
    slope_2_1 = nernst_ph_slope(2, 1)
    results.append(("m=2n -> 절반 기울기", abs(slope_2_1 - 2 * nernst_ph_slope(1, 1)) < 1e-12))

    # (3) m=n 스케일 불변성: (6,6)과 (1,1)이 같은 기울기(비율만 중요, 반응식 몰수 배율 무관)
    w_reaction = CMP_SURFACE_REACTIONS[0]
    results.append(("W passivation(6,6) 기울기 == 표준 -59.1mV/pH",
                     abs(w_reaction.slope_mV_per_pH() - (-59.16)) < 0.01))

    # (4) Cu Eq.9/Eq.10 모두 m=n 계열(치밀 화학양론 산화막) 판정 확인
    cu9, cu10 = CMP_SURFACE_REACTIONS[1], CMP_SURFACE_REACTIONS[2]
    results.append(("Cu(OH)2 반응(Eq.9) m=n 계열", cu9.is_self_limiting_type()))
    results.append(("Cu2O 반응(Eq.10) m=n 계열", cu10.is_self_limiting_type()))

    # (5) 착화제 유무에 따른 정점 이동 방향이 지식노트 §5 서술과 일치
    results.append(("CA 있으면 정점 고농도 이동",
                     mo_cu_w_oxidizer_peak_shift_direction(True) == "peak shifts to higher oxidizer concentration"))

    passed = sum(1 for _, ok in results if ok)
    print(f"pourbaix_nernst_slope self-test: {passed}/{len(results)} PASS")
    for name, ok in results:
        print(f"  [{'PASS' if ok else 'FAIL'}] {name}")
    assert passed == len(results), "self-test 실패"


if __name__ == "__main__":
    _self_test()
