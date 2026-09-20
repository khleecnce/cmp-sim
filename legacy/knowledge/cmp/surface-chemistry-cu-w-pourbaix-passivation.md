<!-- V2-SECTION: R2-slurry | 분배완료 2026-09-08 | 근거: chemistry, passivation, ph, pourbaix, 화학 | 정본: ARCHITECTURE-V2.md §3 -->
# 금속 CMP 표면 화학반응 — Cu/W(/Mo) Pourbaix·passivation 메커니즘

> 에이전트: slurry-chemist Lv2-1 | 작성일: 2026-09-05
> [[slurry-components-overview]] [[colloid-zeta-dlvo-slurry-stability]] [[preston-luo-dornfeld-mrr]]

## 1. 왜 필요한가
[[slurry-components-overview]]에서 Kaufman 경쟁모델(산화→막 형성→기계적 제거→재노출의 동적
평형)을 총론으로 다뤘다. 이번 단원은 그 "산화막이 무엇이고 왜 그 pH·전위 구간에서 생기는가"를
Pourbaix(전위-pH) 열역학과 실측 반응식으로 파고든다. 목표는 슬러리 pH·산화제 선택이 **어떤
고체상**(금속/산화물/이온)을 안정화하는지 예측하고, 그 상이 왜 "무른 막"이 되어 CMP에 유리한지
설명하는 것.

## 2. Pourbaix 다이어그램 기초 — Nernst 식의 두 축
전위-pH 다이어그램의 각 경계선은 Nernst 식에서 나온다. 반응 `aOx + mH⁺ + ne⁻ = bRed + (H2O)`에서:

$$E = E^0 - \frac{0.0591}{n}\log\frac{[Red]^b}{[Ox]^a} - \frac{0.0591\,m}{n}\,\text{pH}$$

- **수직선**(전위 무관, pH만 결정): H⁺가 반응식에 없는 산-염기 평형(예: 이온↔산화물 침전) —
  용해도곱만으로 결정.
- **수평선**(pH 무관): H⁺도 e⁻도 없는 순수 산화환원(예: Cu²⁺/Cu⁰가 pH 독립적인 이유는 H⁺가
  관여 안 하기 때문).
- **기울어진 선**(pH·전위 둘 다 관여): 기울기 = **−0.0591·(m/n) V/pH** (25°C). m=n이면 표준
  기울기 **−59.1 mV/pH**(예: 산화막/금속 경계 다수), m=2n이면 절반인 −29.6 mV/pH.
  출처: 표준 전기화학 교과서 관계식(Bard & Faulkner류 Nernst 식 일반형, 2차 인용 — Pourbaix
  원저 The Atlas of Electrochemical Equilibria in Aqueous Solutions, 1966은 유료라 직접 미확인).

## 3. 텅스텐(W) CMP — Fe(NO₃)₃/H₂O₂ 산화, WO₃ 무른 막
1차 인용(초록·2차 인용 수준, 원문 유료 확인 불가로 명시):
- Kim et al., *Applied Surface Science* 517 (2020) — "Tungsten passivation layer (WO₃) formation
  mechanisms during CMP in the presence of oxidizers" (ScienceDirect S0169433220326192)
- Krishnan, Nalaskowski, Cook, *Chem. Rev.* 110 (2010) 178–204 — "Chemical Mechanical
  Planarization: Slurry Chemistry, Materials, and Mechanisms" (ACS, 원문 유료 — 초록/발췌만 확인)

핵심 메커니즘(여러 2차 인용 교차 일치):
- W 표면은 산성 pH 영역에서 강한 산화제와 접촉 시 **WO₃ 산화막**으로 덮인다(Pourbaix 다이어그램
  상 산성 영역에 WO₃ passivation 영역 존재 — Krishnan review 인용).
- 정적(비연마) 조건에서는 Fe(NO₃)₃·KIO₃ 존재 시 W 용해가 "거의 없거나 극히 낮음" — 즉
  passivation막이 형성되면 **더 이상의 화학적 용해를 스스로 억제**한다(자기제한적 부동태).
  이는 Kaufman 모델의 "무른 막이 기계적으로만 벗겨져야 지속적 제거가 일어난다"는 가정과
  정합적: 화학적 용해(dynamic etch)만으로는 MRR이 거의 없고, 연마입자의 기계적 박리가
  필수적이라는 뜻.
- 산화제 종류(H₂O₂ 단독 vs Fe(NO₃)₃ 단독 vs 혼합)에 따라 WO₃ 막의 형성 경로(Fenton 반응 경유
  ·OH 라디컬 생성 등)와 막 두께·치밀도가 달라져 MRR·선택비가 변한다 — Fe(NO₃)₃ 촉매 + H₂O₂
  혼합이 Fenton형 ·OH 생성으로 W 산화를 가속한다는 보고(ScienceDirect S0169433213011021,
  2013, "Effect of iron(III) nitrate concentration on W CMP performance").

## 4. 구리(Cu) CMP — H₂O₂ 산화, Cu(OH)₂/Cu₂O/CuO 다중 표면종, 착화제 경쟁
1차 인용: Gamagedara & Roy, *Materials* 17(19) 4905 (2024), MDPI 오픈액세스(CC BY),
PMC11477894 — "Mechanisms of Chemically Promoted Material Removal Examined for Molybdenum
and Copper CMP in Weakly Alkaline Citrate-Based Slurries". Clarkson Univ., tribo-전기화학
(OCP·EIS·potentiodynamic) 실측 논문.

핵심 반응식(원문 Eq. 8–12, pH=8 약알칼리 조건):
- 착화제(CA=구연산) 없을 때 H₂O₂가 표면 OH⁻ 공급원 역할을 하는 혼합전위(mixed-potential)
  반응으로 Cu가 산화:
  - `Cu + 2OH⁻ → Cu(OH)₂ + 2e⁻` (Eq.9), 혼합형: `Cu + H₂O₂ → Cu(OH)₂` (Eq.11)
  - `2Cu + 2OH⁻ → Cu₂O + H₂O + 2e⁻` (Eq.10), 혼합형: `2Cu + H₂O₂ → Cu₂O + H₂O` (Eq.12)
  - 부가로 `Cu(OH)₂ → CuO + H₂O`(탈수) — 즉 **Cu(OH)₂·Cu₂O·CuO 세 표면종이 동시에** 기계적
    제거 대상 "무른 막"을 구성.
- CA(구연산, pH=8에서 우세종 Cit³⁻) 첨가 시, 이 표면종들이 재용해되어 구리-구연산 착물
  `(Cu₂Cit₂H₋₂)⁴⁻`을 형성(Eq. 원문 13 부근) — 즉 착화제는 **막을 더 깎아 계속 새 금속면을
  노출**시키는 역할([[slurry-components-overview]]의 "과-passivation 억제"와 정합).
- 무착화제 상태에서도 미량의 `Cu²⁺ + H₂O → CuOH⁺ + H⁺` 가수분해로 낮은 static etch rate(SER)가
  존재 — 완전한 부동태가 아니라 느린 배경 용해가 항상 공존함을 실측으로 확인.
- **정량 관계식(원문 Eq.1-2)**: `MRR = RR_w + RR_c + RR_wc + RR_cw`(순수마모+순수부식+마모유발
  부식+부식유발마모), 화학지배 CMP에서는 `MRR ≈ f·CR(P) + RR_cw`로 단순화(f는 막형성/제거
  속도비 스케일 인자). 이는 [[slurry-components-overview]]의 Kaufman 정성모델을 정량 항으로
  분해한 것과 같은 계열.
- **실측 정성 결과**: 실리카 농도를 늘리면 Mo·Cu MRR 모두 증가(Luo-Dornfeld 활성입자 수 증가와
  정합, [[preston-luo-dornfeld-mrr]]), CA 첨가는 두 금속 모두 MRR을 올리되 Mo에서 효과가 더
  뚜렷함(Mo-citrate 착물 `MoH⁻¹Cit(OH)₂`이 순수 몰리브덴산막보다 기계적으로 더 무름).

## 5. 종합 — CMP 설계 관점의 pH·산화제 선택 원리
| 재료 | 대표 산화제 | 대표 표면종(무른 막) | 착화제 역할 |
|---|---|---|---|
| W | Fe(NO₃)₃, H₂O₂ | WO₃ (자기제한적 부동태) | 미미(주로 산화제 촉매 조합으로 조절) |
| Cu | H₂O₂ | Cu(OH)₂ / Cu₂O / CuO | 구연산·글리신 등이 재용해로 과-passivation 억제 |
| Mo | 과탄산나트륨(SPC) | MoO₃·2H₂O / MoO₃ | 구연산이 MoH⁻¹Cit(OH)₂ 착물 형성해 막을 더 무르게 |

공통 원리: **① 산화제가 금속 표면을 무른 고체상으로 바꾸고, ② 그 상이 스스로 성장을 멈추는
자기제한적 부동태여야 하며(안 그러면 정적 부식이 폭주해 결함·비선택적 제거), ③ 착화제는
이 부동태를 "적당히" 재용해시켜 기계적 제거와 균형을 맞춘다.** pH는 어떤 고체상/이온종이
열역학적으로 안정한지(Pourbaix 축)를 정하고, 산화제·착화제 농도는 그 상의 생성·용해 속도론을
정한다.

## 6. 한계 (정직 표기)
- Pourbaix 원저(Atlas of Electrochemical Equilibria, 1966)는 유료라 실제 다이어그램 좌표값은
  직접 확인하지 못했다 — §2의 Nernst 관계식 자체(기울기 공식)는 표준 전기화학 이론이라
  독립적으로 유도·검증 가능하지만, W/Cu/Mo 각 상의 정확한 안정 영역 경계(구체적 pH·E 수치)는
  2차 인용(리뷰 논문의 서술)에 의존 — **정성적 방향만 검증, 정량 경계값 미검증**.
- §4의 실측 결과는 실리카 콜로이드+SPC/H₂O₂+구연산 조합의 특정 실험 조건(pH=8, 25–40°C,
  Clarkson Univ. 실험실 규모)에 국한 — 산업 슬러리(BTA 억제제 포함, 다른 산화제 농도)로
  일반화는 미검증.
- RR_cw(부식유발마모)의 정량 기여도는 원문도 "시스템별로 다르다"고만 서술 — 보편 상수 없음.

## 7. 자기시험
→ EXAMS.md Lv2-1 참조.

## 8. 코드 재현 (python verify — CI가 매 push마다 실제 실행)
`sim/tier2_physics/pourbaix_nernst_slope.py`가 Nernst 식의 m/n 기울기 공식을 W/Cu 산화막
경계 반응식에 대입해 표준 −59.1 mV/pH(m=n 경우, CRC Handbook 표준값)를 재현하고, 문헌
반응식(§3-4, Gamagedara & Roy 2024 PMC11477894)이 실제로 이 m=n 계열에 속함을 assert로 확인.

```python verify
import sys
sys.path.insert(0, "sim/tier2_physics")
from pourbaix_nernst_slope import nernst_ph_slope, CMP_SURFACE_REACTIONS

# 표준값 대조: m=n=1 최소 사례 -> -59.16 mV/pH (CRC Handbook RT/F*ln10 @25C)
slope = nernst_ph_slope(1, 1) * 1000.0
assert abs(slope - (-59.16)) < 0.01, f"표준 Nernst 기울기 불일치: {slope} mV/pH"

# W passivation(6,6 몰수배율 다름) 도 동일 기울기로 스케일 불변 확인
w_rx = CMP_SURFACE_REACTIONS[0]
assert abs(w_rx.slope_mV_per_pH() - (-59.16)) < 0.01, f"W 반응 기울기 불일치: {w_rx.slope_mV_per_pH()}"

# Cu Eq.9/Eq.10 (§4 원문 반응식) 모두 m=n 치밀 화학양론 산화막 계열인지 판정
cu9, cu10 = CMP_SURFACE_REACTIONS[1], CMP_SURFACE_REACTIONS[2]
assert cu9.is_self_limiting_type() and cu10.is_self_limiting_type(), "Cu 반응식이 m=n 계열이 아님"

print(f"PASS: 표준기울기={slope:.2f}mV/pH, W={w_rx.slope_mV_per_pH():.2f}mV/pH, Cu Eq9/10 m=n 확인")
```

한계: 이 코드가 검증하는 것은 **Nernst 식의 산술과 반응식 m/n 계수 분류**뿐이다. Pourbaix
다이어그램의 실제 pH·전위 경계좌표(정량값)는 §6에서 밝힌 대로 원저(1966, 유료) 미확인 —
정량 경계값은 여전히 미검증이며, 이 verify 블록은 그 사실을 바꾸지 않는다.
