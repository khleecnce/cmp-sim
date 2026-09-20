<!-- V2-SECTION: R2-slurry | 근거: 입자 경도, Hertz, 압입, 제거체적 | 정본: ARCHITECTURE-V2.md §3 -->
# 입자 경도(실리카/세리아/알루미나)와 Hertz(소성) 압입 → 입자당 제거체적 모델

> 에이전트: slurry-abrasive Lv2-1(잔여분, 경도·Hertz 압입) | 작성일: 2026-09-11
> 선행: [[../materials/hertz-gw-contact-mechanics]](탄성 Hertz 접촉·GW 통계모델, 반드시 먼저 읽을 것)
> [[preston-luo-dornfeld-mrr]] [[luo-dornfeld-integrated-cmp-framework]]
> [[abrasive-manufacturing-colloidal-fumed-silica-ceria]](Lv1-1, 절대경도 미확보를 이 노트로 이월한다고 명시한 바로 그 과제)
> [[ceria-slurry-ce-redox-selectivity]] [[w-cmp-wo3-passivation-oxidizer-kaufman]]

## 0. 이 노트가 [[../materials/hertz-gw-contact-mechanics]]와 다른 점 (중복 방지)
`hertz-gw-contact-mechanics.md`는 **탄성(Hertz) 접촉** — 패드 asperity가 웨이퍼에 눌릴 때
힘-압입깊이 관계 F∝u^(3/2)를 다룬다. 이 노트는 그 asperity 접촉 안에 낀 **슬러리 입자 하나**가
웨이퍼 표면을 어떻게 "긁어 제거"하는지, 즉 **소성(plastic) 압입** — 입자가 리지드 압입자처럼
웨이퍼에 파고들어 재료를 제거하는 모델을 다룬다. 탄성 vs 소성의 전이 기준(Tabor 소성지수
ψ=(E*/H)√(δ/R))은 부모 노트 §5가 이미 "Lv2-2에서 다룸"으로 명시적으로 유보해 두었으므로
이 노트에서 새로 만들지 않고 그대로 넘긴다(중복 유도 금지).

## 1. 출처
1차 논문(전문 확보·통독): Jianfeng Luo, "Material Removal Regions in Chemical Mechanical
Polishing: Coupling Effects of Slurry Chemicals, Abrasive Size Distribution and Wafer-Pad
Contact Area, Part 1," UC Berkeley 기술보고서(NSF/UC SMART 지원), 2002. 오픈액세스 PDF
(2026-09-11 확보, 6쪽 논문의 21쪽 리프린트판 — 실제로는 21페이지 판, `papers/luo-dornfeld-material-removal-regions-part1.pdf`, escholarship.org/uc/item/0n2575s1 영구링크에서 다운로드,
790,075 bytes 확인). 동일 내용의 도서챕터 판본 DOI(Crossref API 실존 확인,
2026-09-11): **doi:10.1007/978-3-662-07928-7_5** ("Material Removal Regions in CMP: Coupling
Effects...", in *Integrated Modeling of Chemical Mechanical Planarization for Sub-Micron IC
Fabrication*, Springer, 2004) — [[luo-dornfeld-integrated-cmp-framework]]가 이미 인용한
같은 책의 리뷰챕터(_2)의 자매챕터(_5)다.

이 논문은 그 자체가 **Luo & Dornfeld(2001)의 후속·확장**이며, 핵심 압입-제거체적 식(본 노트
§2 Eq.11)은 원 논문에서 그대로 가져온 것("From Equation 11 in [1]")이라고 명시한다.
원 논문: J. Luo, D. A. Dornfeld, "Material Removal Mechanism in Chemical Mechanical
Polishing: Theory and Modeling," *IEEE Trans. Semicond. Manuf.* 14(2), pp.112–133, 2001.
**doi:10.1109/66.920723**(Crossref API 실존 확인, 2026-09-11) — IEEE 유료 저널, OA 경로
없음(`find_open_access.py --title` 조회, 무료 사본 미발견) — **원문 직접 확인 못함, 미검증**.
따라서 이 노트의 수식·수치는 전부 2002년 Part-1 논문(직접 읽음)이 원 논문을 인용한 형태로만
확보한 것이며, 원 논문 자체의 유도과정(Section 표기, Fig. 번호 등)은 대조하지 못했다.

## 2. Luo-Dornfeld 단일입자 소성압입 모델 — 수식(원문 그대로, 2026-09-11 이미지 대조로 OCR 오류 정정)

가정: 슬러리 입자(지름 x)는 웨이퍼(또는 웨이퍼 표면의 무른 passivation/hydration층)보다
훨씬 단단한 **강체 압입자**로 취급된다(리지드 인덴터 가정 — 아래 §4에서 실리카는 이 가정이
아슬아슬하게 깨진다는 것을 수치로 보인다). 압입은 탄성이 아니라 **소성**이므로, 접촉압력은
Hertz의 탄성 p_max 공식이 아니라 웨이퍼 경도 H에 근접한다는 표준 압입 가정(Tabor)을 쓴다:

```
단일 입자에 걸리는 힘         F = 0.25·π·x²·P                                  (원문 Eq.11 표기, 여기 §2 Eq. a)
접촉면적/점유면적 비          A''/A' = P/H_w2   (원문 "Equation (4) in [1]")     (§2 Eq. b)
단위시간당 단일입자 제거량    V̄ol_removed = (√2/4)·x²·(P/H_w2)^(3/2)·V          (§2 Eq. c, 원문 "From Equation 11 in [1]")
```
여기서 x=x_avg-a(활성 입자 크기), P=접촉압력, H_w2=웨이퍼(또는 그 표면층)의 유효 경도,
V=웨이퍼-패드 상대속도. **V̄ol_removed는 이름과 달리 정적 "부피"가 아니라 V가 1승으로 곱해진
"단일 입자당 부피 제거율"(부피/시간)이다** — 원문이 이를 N개 입자에 곱해 그대로 MRR(제거율,
Eq.14 `MRR=N·V̄ol_removed`)을 만들기 때문에 차원상 rate여야 앞뒤가 맞는다(원문에 명시적 차원
설명은 없음 — 이 해석은 본 노트가 Eq.14의 좌우변 차원을 맞추기 위해 추가한 것, **미검증**
표기하되 Preston형 K·P·V 구조와 일치한다는 정황증거는 있다, [[preston-luo-dornfeld-mrr]]).

핵심 지수: **제거체적(율)은 경도의 3/2제곱에 반비례**(H_w2^(-3/2)). 이 3/2 지수는 압력이
아니라 접촉면적이 A∝(F/H)이고 그 위에 다시 Hertz형 압력-면적 관계(A'∝(1+m1x)^(2/3), 본
논문 Eq.9)가 곱해지며 나오는 결과로, 원문이 별도 섹션에서 "The exponent 3/2 of the hardness
term...accelerates this change"라고 직접 강조한다(원문 §2, region 1→2 전이 논의).

농도-비포화 영역(saturation 이전)에서는 같은 경도 지수가 그대로 유지되어
`MRR ∝ C·H_w^(-3/2)·[(x_avg+3σ)²/x_avg³]·P0^(1/2)`(원문 Eq.2/6-b)가 나온다 — **웨이퍼 경도가
낮을수록(즉 무른 재료·무른 passivation층일수록) 제거율은 3/2제곱으로 민감하게 커진다.**

## 3. 실측 하드니스·모듈러스 값 (원문 §2.2에 명시된 수치, 직접 읽고 대조)
Luo(2002) 본문이 직접 인용하는 수치(오더 확인용, 저자 스스로도 "around"로 근사치임을 명시):
- 접촉압력 P ≈ 10⁶ Pa("around 10⁶ Pa [1]")
- 웨이퍼(유효) 경도 H_w: 텅스텐 ≈ 10⁹ Pa(=1 GPa), 실리콘옥사이드·실리콘 ≈ 10¹⁰ Pa(=10 GPa)
  — 원문이 인용하는 [34]: G. Fu, A. Chandra, S. Guha, G. Subhash, "A plasticity-based model
  of material removal in chemical-mechanical polishing (CMP)," *IEEE Trans. Semicond. Manuf.*
  14(4), pp.406-417, 2001(원문에서 재인용만 확인, [34] 자체는 원문 미접근 — 미검증)
- 알루미나 연마입자의 실제 영률 E_a ≈ 500 GPa — 원문이 인용하는 [5]: Q. Luo, S. Ramarajan,
  S. V. Babu, "Modification of the Preston equation for the chemical-mechanical polishing of
  copper," *Thin Solid Films* 335, pp.160-167, 1998(재인용만 확인, [5] 원문 미접근 — 미검증)
- 패드(폴리머) 영률 E_p ≈ 1 GPa — 원문이 인용하는 [34]

## 4. 입자 경도 비교 — 실리카 vs 세리아 vs 알루미나 (독립 1차 문헌, 직접 대조)
`hertz-gw-contact-mechanics.md`와 §2 모델 둘 다 "입자가 웨이퍼보다 훨씬 단단하다(리지드
인덴터)"는 것을 암묵적으로 가정한다. 실제 3대 CMP 연마입자의 절대 경도값을 독립 1차 문헌에서
모아 이 가정이 항상 성립하는지 검토한다.

| 입자/재료 | 경도 | 영률 | 출처(1차, DOI/PMC 확인) | 접근 |
|---|---|---|---|---|
| 알루미나(Al₂O₃) | Mohs 9(정성) | E≈500 GPa(연마입자 실측, §3) | Mohs: Wang et al. 2024, *Materials* 17(3):679, doi:10.3390/ma17030679, PMC10856169(4H-SiC CMP 알루미나 연마 논문 — "Al2O3 is a well-known abrasive material with high hardness (Mohs hardness 9)") | 전문 확인(WebFetch) |
| 세리아(CeO₂, 벌크) | H=6.44±0.72 GPa(나노압입, 상온) | E=167.6±12.5 GPa(상온) | doi:10.3390/ma19102134, PMC13208460, *Materials* 2026 — "고온 나노압입" 논문 Table 1 상온(RT) 행 | 전문 확인(WebFetch, Table1 인용) — **주의: 이 논문은 원자로 대체연료(surrogate fuel) 목적의 벌크 CeO₂ 펠릿을 측정한 것이지 CMP용 슬러리 나노입자가 아니다. 같은 CeO₂ 결정상이라는 근거로만 오더 참고, 슬러리 입자 고유 표면효과(나노스케일 결함밀도 등)는 미반영 — 미검증** |
| 실리카(SiO₂, 용융/비정질) | Vickers H=7.3±0.3 GPa(상온) | (E≈72 GPa, 별도 표준값 — 이 논문 자체 수치 아님, 교차참고) | Michel, Serbena, Lepienski, "Effect of temperature on hardness and indentation cracking of fused silica," *J. Non-Cryst. Solids* 352, pp.3550-3555, 2006, doi:10.1016/j.jnoncrysol.2006.02.113 | **초록/2차 요약만 확인 — Elsevier 유료, OA 경로 없음(`find_open_access.py` 조회 결과 없음), 원문 PDF 미확보, 미검증** |

**핵심 발견(수치로 확인, §5 코드)**: 실리카(H≈7.3 GPa)는 §3에서 확인한 SiO₂ 웨이퍼(막) 자체의
유효 경도(≈10 GPa, Fu et al. 2001 재인용치)보다 오히려 **낮거나 비슷한 오더**다 — 즉 실리카
입자가 SiO₂ 웨이퍼를 압입하는 "리지드 인덴터" 가정이 하드코어하게 성립하지 않는다. 반면
알루미나(Mohs 9, E=500 GPa)는 텅스텐(H≈1 GPa)이나 SiO₂(H≈10 GPa) 어느 쪽에 비해도 압도적으로
단단해 리지드 인덴터 가정이 잘 맞는다. 이는 [[abrasive-manufacturing-colloidal-fumed-silica-ceria]]
§(Lv1-1 Q3)가 "절대 경도를 확보 못해 상대 서열만 안다"고 남긴 잔여 질문에 대해, **실리카가
SiO2 CMP에서 순수 기계적 압입만으로 작동한다고 보기 어렵다는 정량적 근거**를 제공한다 —
Cook(1990)의 수화층(hydrated softer layer, ≡SiOH) 메커니즘(§2의 Luo-Dornfeld 이중층 모델이
채택한 바로 그 가정: H_w1≪H_w2)이 왜 필요한지를 경도 수치로 뒷받침한다.

## 5. 정량 재현 — 두 가지 검증

```python verify
import numpy as np

# ---- (A) 경도 지수(3/2)·압력 지수(1/2) 스케일링 법칙의 대수적 재현 ----
# 원문 Eq.2/6-b: MRR ∝ C * Hw^(-3/2) * [(xavg+3sigma)^2/xavg^3] * P0^(1/2)
def mrr_scaling(C, Hw, xavg, sigma, P0, k=1.0):
    return k * C * Hw**(-1.5) * (xavg + 3*sigma)**2 / xavg**3 * P0**0.5

base = dict(C=1.0, Hw=1e10, xavg=100e-9, sigma=10e-9, P0=1e6)
mrr_base = mrr_scaling(**base)

# 경도를 2배로 올리면 MRR은 정확히 2^-1.5배가 되어야 한다(원문이 명시한 지수)
mrr_2x_hw = mrr_scaling(**{**base, 'Hw': base['Hw']*2})
ratio_hw = mrr_2x_hw / mrr_base
assert abs(ratio_hw - 2**-1.5) < 1e-9, f"경도 지수 3/2 재현 실패: {ratio_hw} != {2**-1.5}"

# 압력을 4배로 올리면 MRR은 정확히 2배(4^0.5)가 되어야 한다
mrr_4x_p0 = mrr_scaling(**{**base, 'P0': base['P0']*4})
ratio_p0 = mrr_4x_p0 / mrr_base
assert abs(ratio_p0 - 2.0) < 1e-9, f"압력 지수 1/2 재현 실패: {ratio_p0} != 2.0"

print(f"(A) 경도 2배 -> MRR x{ratio_hw:.4f}(기대 {2**-1.5:.4f}), "
      f"압력 4배 -> MRR x{ratio_p0:.4f}(기대 2.0000) — 원문 Eq.2/6-b 지수 재현 OK")

# ---- (B) "경도만으로 예측한 W vs 산화막 상대 제거율"이 실측과 얼마나 어긋나는가 ----
# 원문 §2.2 실측치(직접 인용): Hw(W) ~= 1e9 Pa, Hw(SiO2/Si) ~= 1e10 Pa
Hw_W = 1e9
Hw_SiO2 = 1e10

# 경도 항(Hw^-3/2)만 놓고 볼 때, 같은 P,V,입자크기라면 텅스텐이 산화막보다 몇 배 빨리 깎여야 하는가
predicted_ratio_W_over_SiO2 = (Hw_SiO2 / Hw_W) ** 1.5
assert abs(predicted_ratio_W_over_SiO2 - 10**1.5) < 1e-6

# 실측(문헌, 이미 검증된 다른 노트에서 인용): W CMP 대표 제거율 130 nm/min(범위 ~400까지,
# w-cmp-wo3-passivation-oxidizer-kaufman.md), 일반 산화막 CMP 범위 50~1000 nm/min,
# STI 대표사례 254.05 nm/min (둘 다 preston-luo-dornfeld-mrr.md에서 이미 문헌 대조된 값)
w_representative_nm_min = 130.0
oxide_representative_nm_min = 254.05
actual_ratio_W_over_oxide = w_representative_nm_min / oxide_representative_nm_min

print(f"(B) 경도항만으로 예측한 W/SiO2 제거율비 = {predicted_ratio_W_over_SiO2:.1f}배 "
      f"(Hw 3/2제곱 법칙 그대로 적용)")
print(f"    실측 W/산화막 대표 제거율비 = {actual_ratio_W_over_oxide:.2f}배 "
      f"(W {w_representative_nm_min} / 산화막 {oxide_representative_nm_min} nm/min)")

# 예측(~31배)과 실측(~0.5배)이 오더 자체가 다르다는 것을 명시적으로 확인 —
# "재현 성공"으로 거짓 포장하지 않는다.
mismatch_factor = predicted_ratio_W_over_SiO2 / actual_ratio_W_over_oxide
assert mismatch_factor > 20, (
    f"경도항 단독 예측과 실측 제거율비가 예상보다 가깝다({mismatch_factor:.1f}배 차이) — "
    f"재확인 필요"
)
print(f"    -> 불일치 배율 {mismatch_factor:.1f}배: 벌크 경도 3/2제곱 법칙 '단독'으로는 "
      f"W/산화막 실제 제거율비를 전혀 설명 못함(오더 자체가 틀림)")
```
**결과 해석(정직하게)**: (A)는 원문이 서술한 지수 그대로를 재현한 순수 대수 검증이라 당연히
성공한다(회귀 테스트 성격). (B)가 이 노트의 실질적 발견이다 — **웨이퍼의 "벌크" 경도만으로
텅스텐과 산화막의 실제 CMP 제거율 비를 예측하면 오더 자체(~31배 vs 실측 ~0.5배, 60배 이상
불일치)가 틀린다.** 이는 실패가 아니라 Luo-Dornfeld 이중층 모델(§2, [1-2])이 애초에 왜
필요했는지를 보여주는 증거다 — 실제 CMP는 "벌크 웨이퍼 경도 H_w2"가 아니라 **화학반응이 만든
무른 표면층의 경도 H_w1**(수 GPa 이하로 훨씬 작을 것으로 추정, 이 노트에서 절대값 미확보 —
미검증)에 지배되며, 텅스텐 CMP의 실제 고속 제거는 WO₃ passivation-제거 순환
([[w-cmp-wo3-passivation-oxidizer-kaufman]])이라는 화학적 경로 때문이지 벌크 텅스텐이
기계적으로 무르기 때문이 아니다(텅스텐 벌크는 오히려 경도가 낮은 것으로 나왔지만, 그 낮은
벌크 경도조차 실측 제거율비를 설명하기엔 부족하다 — 화학이 지배적임을 재확인).

## 6. sim/ 연결 메모 (구현 요청, 코드 작성은 하지 않음)
- 현재 `sim/tier1_empirical/preston.py`의 Kp는 하드니스에 대해 완전히 불투명한 상수다.
  §2 Eq.2/6-b가 제시하는 `Kp_effective ∝ Hw^(-3/2)`는 [[luo-dornfeld-integrated-cmp-framework]]
  §5(3)이 이미 "함수형 Kp 리팩터는 Lv4로 유보"한 항목과 정확히 같은 자리에 들어간다 — 새 구현
  요청을 추가하지 않고 그 유보 결정에 편승한다(중복 요청 방지).
- §4의 "실리카는 SiO2 대비 리지드 인덴터 가정이 약하다"는 발견은, 만약 향후 화학종별
  `damage_exponent`나 `Kp` 보정 계수를 설계한다면 실리카/SiO2 페어링에는 순수 기계적
  Hw^(-3/2) 항을 그대로 쓰면 안 된다는 정성적 경고로만 남긴다(정량 보정치 없음).

## 7. 미검증 사항 총정리 (정직성 표지)
- 원 논문 Luo & Dornfeld(2001, IEEE, doi:10.1109/66.920723) 원문 미접근 — 모든 수식은 2002년
  Part-1 논문의 재인용을 통해서만 확보.
- §3의 H_w(텅스텐/SiO2) 수치, E_a(알루미나) 수치는 전부 2차 재인용([34],[5], Luo 2002 원문이
  인용한 문헌들) — 그 원문들 자체는 미접근.
- §4 실리카 Vickers 경도(Michel et al. 2006)는 초록/2차 요약 수준만 확인, 원문 PDF 미확보.
- §4 세리아 나노압입 값(doi:10.3390/ma19102134)은 CMP 슬러리 나노입자가 아닌 벌크 원자로
  연료대체재 펠릿 측정치 — 같은 결정상이라는 근거로만 차용, 나노입자 표면 특유의 경도 저하/
  증가 효과는 반영 못함.
- "V̄ol_removed가 사실은 rate(부피/시간)"라는 해석은 본 노트가 Eq.14 차원 정합을 위해 추가한
  것으로, 원문에 명시적 진술은 없음(정황 근거만 있음).
- H_w1(무른 표면층 경도)의 절대값은 어느 문헌에서도 확보하지 못함 — Lv3 이후 과제로 남긴다.
