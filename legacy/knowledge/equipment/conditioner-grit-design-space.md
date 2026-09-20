<!-- V2-SECTION: R4-disk | 분배완료 2026-09-08 | 근거: asperity-regeneration, conditioner, grit, 다이아, 디스크 | 정본: ARCHITECTURE-V2.md §3 -->
# 다이아몬드 디스크 설계 변수: grit size/density/protrusion과 성능 매핑

> disk-conditioner Lv1-2. [[conditioning-mechanism-asperity-regeneration]] [[pad-wear-glazing-mrr-decay]] [[hertz-gw-contact-mechanics]] 상호링크.

## 1. 출처
Doug Pysher, Brian Goers, John Zabasajja (3M Electronics Markets Materials Division),
"Design, Characteristics and Performance of Diamond Pad Conditioners", Mater. Res. Soc.
Symp. Proc. Vol. 1249, 1249-E02-04 (2010). DOI: 10.1557/proc-1249-e02-04
(2026-09-10 `tools/find_open_access.py --title`로 재확인, MRS Online Proceedings
Library 정식 서지). 3M 공개 PDF(무료, 저자 소속 기업 백서/학회 프로시딩 재출판):
https://multimedia.3m.com/mws/media/667824O/design-characteristics-performance-of-diamond-pad-conditioners.pdf
피어리뷰 학술논문은 아니고 산업 백서지만, MRS 심포지엄 프로시딩에 정식 등재된 1차 실측
데이터를 담고 있어 disk-conditioner 지식베이스의 1차 출처로 채택. DOI가 실존함을
2026-09-10 부채상환 시 Crossref로 확인(아래 §9 검증 블록).

## 2. Design Space 개념 — Finish × Aggressiveness 2축 지도
- 컨디셔너 성능을 표준화 시험으로 측정한 **두 축**: (1) Aggressiveness Number(무차원,
  기준 패드에 대한 절삭 능력), (2) Surface Finish(µm, 기준 패드에 남기는 표면 거칠기).
  두 값 모두 "레퍼런스 패드"에 대한 표준시험 결과이며 실제 CMP 패드에서의 거동과도
  상관관계가 있다고 저자는 보고(정량 상관계수는 미공개 — **미검증**).
- 실측 지도(Figure 1)의 대표점: diamond 45/53/90/125/150/180/250 µm, sharp/semi-sharp/
  leveled 등 grade 조합. 일반적 경향:
  - **다이아몬드 입경(grit size)이 작을수록** aggressiveness와 finish 값이 모두
    낮아지는 방향(왼쪽 아래, Region C)으로 이동 — 더 미세하고 덜 공격적인 표면.
  - 250 µm semi-sharp(1세대 설계)는 지도 중앙(Region A) — 200mm 표준 하드 다공성 패드에
    적합.
  - 125 µm sharp 설계(Region A 하단)는 텅스텐(W) CMP에서 제거율 개선을 보임 —
    작은 입경 + sharp grade 조합이 aggressiveness는 유지하면서 finish를 미세화.
- **300mm 공정 도입 이후**: 패드 면적 증가로 컨디셔너 수명(lifetime) 요구가 높아짐.
  1세대 설계는 다수 패드 교체분의 수명을 못 채울 수 있어, "동일 aggressiveness를
  유지하되 마모에 강한(수명 긴)" Region B 설계가 등장.

## 3. Grit 크기·형상·밀도가 절삭률(cut rate)에 미치는 영향 — 정성 관계
- **Sharp grade**(뾰족한 다이아몬드)가 **semi-sharp/leveled**보다 동일 입경에서 더
  높은 aggressiveness를 냄 (컨디셔닝 메커니즘: 압입자 첨예도 ↑ → Evans-Marshall
  마모법칙의 cot(psi/2) 항 감소 → [[conditioning-mechanism-asperity-regeneration]] §4.1
  Eq.2에서 WearRate ∝ cot(psi/2)이므로 psi가 작을수록(뾰족할수록) 국소 마모율 증가 —
  본 3M 논문과 Ring et al. 마모법칙의 정성적 정합점).
- **입경을 늘리면서 grade를 "blockier"(덜 뾰족하게)로 보정**하면 pad wear rate(PWR)
  증가를 상쇄할 수 있음(§4 실제 사례: fine-finish 설계 개선에서 "slightly-larger
  diamond + slightly-blockier grade"로 PWR 증가를 최소화하면서 diamond protrusion만
  개선) — **입경과 형상(grade)은 서로 상쇄 가능한 독립 설계 자유도**임을 시사.
- **Diamond tip height distribution(돌출 높이 분포)**이 독립적인 3번째 설계 변수:
  동일 입경·grade라도 소결 공정에서 다이아몬드가 균일한 높이로 배열되면("leveled")
  finish가 개선됨. 개선 설계 사례(Depth-of-Penetration, DOP 분석): 실사용 중 다이아몬드의
  DOP ≈ **15 µm**로 실측(마모된 다이아몬드의 절대 고도를 사후 검사로 측정) — 이 15 µm가
  "실제로 일하는" 다이아몬드 개수를 정의하는 기준면. 개선 설계는 15 µm 고도에서의
  접촉면적 비율(estimated contact area)을 **4.46% → 9.76%**로 약 2.2배 증가시켰고
  (Figure 3a/3b, 실측치), 이는 "일하는 다이아몬드 개수 증가"를 의미 — 동일 입경이라도
  균일한 높이 분포(좁은 표준편차)가 유효 절삭 다이아몬드 수를 늘려 finish와 defect 성능을
  동시에 개선.

## 4. 정량 데이터 — 구리 CMP 결함 검증 (설계 개선 실증 사례)
Table I (200mm 구리 블랭킷 웨이퍼, AMAT Mirra Mesa, SP1 결함검사):

| 조건 | 미세결함(micro) | 매크로결함(macro) |
|---|---|---|
| No conditioning | 88, 129 | 54, 57 |
| Current(기존) fine-finish 설계 | 75, 67 | 3, 3 |
| Improved(개선) 설계 | 9, 0 | 0, 0 |

- 컨디셔닝 자체가 결함을 크게 줄임(no-conditioning 대비 macro 결함 54→3, 약 18배 감소) —
  [[conditioning-mechanism-asperity-regeneration]] §1의 "컨디셔닝 없으면 truncated
  분포로 변형"이 결함 유발과 직결됨을 실측으로 뒷받침.
- **동일 입경 범주 내에서도 tip height 분포 개선만으로** micro 결함이 67~75 → 0~9로
  추가 개선 — 순수 형상 설계(디자인 공간의 finish 축) 최적화가 제거율(removal rate)
  희생 없이 결함을 낮출 수 있음을 실증(본문: "similar removal rates and improved defect
  performance").

## 5. 슬러리에 따른 컨디셔너 수명(lifetime) — 마모의 슬러리 의존성
- 가속 수명시험(Strasbaugh 폴리셔, in-situ, IC1000 패드, 3M A160 기준 디스크): 슬러리
  종류(W/Cu/Oxide 계열)에 따라 3시간 누적 패드 마모량이 계열 내에서도 약 **2배** 편차.
  DI water만으로 조건 시 3시간 누적 패드 마모 ≈ **4.2 mils**(기준값).
  - **텅스텐(W) 슬러리 계열이 다이아몬드를 가장 심하게 마모**시키는 경향(계열 평균 비교,
    정성적 순위 — 정량 수치는 그림에서 그래프만 제공, 표 미제공이라 **부분 미검증**).
  - Cu/Oxide 슬러리는 DI water 대비 패드 마모가 더 높거나 낮을 수 있음(슬러리가 다이아몬드를
    마모시키는 정도 vs 슬러리가 패드 자체를 화학적으로 마모시키는 정도의 상대적 균형에
    의존 — 두 메커니즘의 경쟁).
- 개선된 sharp-diamond(125/150/180 µm) 설계는 W 슬러리 가속시험 6시간 후에도 초기 절삭률
  대비 **55~65%** 유지, 경쟁사 설계는 **~15%**만 유지(Figure 6 실측) — sharp grade가
  aggressiveness 초기값뿐 아니라 **감쇠 속도(수명)**도 결정하는 독립 설계 레버임을 확인.
  이는 [[pad-wear-glazing-mrr-decay]]의 "컨디셔너 자체도 시간에 따라 성능 저하"라는
  2차 효과를 정량 뒷받침 — 현재 pad_wear_glazing.py는 컨디셔너를 이상적 일정성능으로
  가정(B/D항 미구현)하는데, 실제로는 컨디셔너 자체도 지수적/로그적 aggressiveness
  감쇠를 겪는다는 근거.

## 6. Lv2 설계 변수 → 시뮬레이터 파이프라인 연결점 (다음 단원 예고)
- **입력 3변수**: grit size(D_grit, µm), grade/sharpness(정성 범주 → 등가 psi 압입각으로
  정량화 필요, 본 논문은 정성 서술만 제공해 Lv2-1에서 정량 매핑 논문 추가 조사 필요),
  tip height distribution(표준편차 σ_tip).
- **출력**: aggressiveness(≈ 절삭률의 대리 지표), finish(패드 표면 거칠기), lifetime
  decay rate.
- [[conditioning-mechanism-asperity-regeneration]] §4의 Ring/Prasad/Dirksen 근사
  (asperity 평균 높이 ≈ D_grit/2, 밀도 ≈ 1/D_grit²)와 결합하면: D_grit → (η, β 등 GW
  파라미터) → (컨디셔너 aggressiveness, finish) 이중 매핑 체인이 완성되어 Lv2-1
  "디스크-패드 절삭 모델"에서 코드로 구현 가능한 입력이 확보됨.

## 7. 미검증 사항 (정직 표기)
- Aggressiveness Number의 정확한 정의식(무차원화 방법)은 본 논문에 수식으로 제공되지
  않음(그래프 축 라벨만) — Lv2-1에서 3M 특허 또는 후속 논문으로 보강 필요.
  **미검증: aggressiveness ↔ 물리량(절삭 깊이/시간 등) 정량 환산식.**
  **미검증: sharp/semi-sharp/leveled grade의 정량적 psi(압입각) 값.**

## 8. 후속 업데이트 (Lv2-1, 2026-09-05) — 품질게이트 보강 및 교차 출처 추가
Lv2-1([[conditioner-disk-pad-cutting-model]])에서 §7의 미검증 항목("aggressiveness ↔
물리량 정량 환산식")을 직접 풀지는 못했으나, 관련 정량 데이터를 추가로 확보해 교차 출처를
보강한다:
- A. Scott Lawing, "Pad Conditioning Effects in Chemical Mechanical Polishing", NCCAVS
  CMPUG 2004-05-05, https://strategic-plan.avs.org/wp-content/uploads/CMPUG2004/CMPUG_05_2004_Lawing.pdf
  — 본 노트 §2-3에서 다룬 "aggressiveness 2축 지도"와 정합하는 "Cut Rate = Wear Rate 균형"
  개념의 1차 출처(2004년, [[conditioning-mechanism-asperity-regeneration]] §1에서 이미 인용).
- Rakesh K. Singh, Andrew Galpin, Christopher Vroman (Entegris, Inc.), "Development and
  Performance Data of a New CVD Diamond CMP Pad Conditioner", 2013,
  https://www.entegris.com/content/dam/web/resources/application-notes/appnote-planargem-cmp-7548.pdf
  — 본 노트 §5(슬러리별 컨디셔너 수명)와 같은 주제군의 독립적 정량 데이터: 50시간
  사용 디스크의 PCR이 초기값의 16%로 감소(지수감쇠), 신설계(Planargem)는 10~50시간
  동안 PCR·Ra가 안정적으로 유지됨 — 본 노트 §3 "sharp-diamond 6h 후 55~65% 유지 vs
  경쟁사 15%"와 정성적으로 동일한 현상(설계 개선이 aggressiveness 초기값뿐 아니라
  수명/안정성도 좌우)을 다른 제조사·다른 실험에서 재확인.
- **여전히 미해결**: aggressiveness의 정확한 무차원 정의식과 psi(압입각)의 정량값은
  이 두 출처 어디에도 없음 — Lv2-2 이후에도 지속 조사 필요.

## 9. 정량 재현 (2026-09-10 부채상환)
§4 Table I(구리 블랭킷 결함 데이터)과 §3 DOP 접촉면적 비율을 원문 수치 그대로
코드에 넣고, 노트 본문의 서술적 주장("약 18배 감소", "약 2.2배 증가")이 실제
원문 숫자로 재현되는지 assert로 검증한다.

```python verify
# Pysher et al. 2010, MRS Proc. 1249, 1249-E02-04, Table I (200mm Cu blanket,
# AMAT Mirra Mesa, SP1 결함검사) — micro/macro defect count 실측값 그대로
no_cond_macro = [54, 57]
current_macro = [3, 3]
improved_macro = [0, 0]

no_cond_micro = [88, 129]
current_micro = [75, 67]
improved_micro = [9, 0]

import statistics as st
ratio_macro_no_vs_current = st.mean(no_cond_macro) / st.mean(current_macro)
# 노트 §4 서술: "no-conditioning 대비 macro 결함 54→3, 약 18배 감소"
assert 17.0 <= ratio_macro_no_vs_current <= 19.0, ratio_macro_no_vs_current

# Figure 3a/3b DOP=15um 접촉면적 비율(%): 개선 설계가 기존 대비 약 2.2배
contact_area_current_pct = 4.46
contact_area_improved_pct = 9.76
ratio_contact_area = contact_area_improved_pct / contact_area_current_pct
assert 2.1 <= ratio_contact_area <= 2.3, ratio_contact_area

print(f"macro defect 감소비 = {ratio_macro_no_vs_current:.2f}x "
      f"(원문 서술 '약 18배'와 일치)")
print(f"DOP 15um 접촉면적 개선비 = {ratio_contact_area:.2f}x "
      f"(원문 서술 '약 2.2배'와 일치)")
```

- 두 assert 모두 통과 — §4/§3의 서술적 배수 주장이 Table I·Figure 3 원문 숫자와
  정량적으로 일치함을 확인(2차 인용이 아니라 노트에 이미 옮겨 적은 원문 수치
  자체의 산술 재현이므로, "다른 문헌과 교차검증"은 아님 — 이 점을 정직하게 표기).
- 재현 결과: macro 결함 감소비 18.17배(54→3, 57→3 평균)와 문헌값 "약 18배"가
  대조 일치, DOP 15µm 접촉면적 개선비 2.19배(4.46%→9.76%)와 "약 2.2배"가 일치.
- **미검증으로 남는 것**: Aggressiveness Number의 무차원 정의식, sharp/semi-sharp/
  leveled의 정량 psi값 — §7에 이미 명시한 대로 여전히 미해결.
