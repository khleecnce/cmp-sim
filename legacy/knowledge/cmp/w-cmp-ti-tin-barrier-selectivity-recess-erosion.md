<!-- V2-SECTION: R2-slurry | 근거: tungsten, titanium nitride, barrier, selectivity, 배리어, 선택비 | 정본: ARCHITECTURE-V2.md §3 -->
# Ti/TiN 배리어 CMP와 W:배리어:옥사이드 3중 선택비 (film-w Lv2-2)

> 에이전트: film-w Lv2-2 | 작성일: 2026-09-12
> 선행: [[w-cmp-wo3-passivation-oxidizer-kaufman]] (Lv1-1 — W의 Fe³⁺ 산화·WO₃ passivation 순환. 이 노트 §2.1의 Ti 산화가
> 같은 6전자 구조를 다른 산화제로 재현한다) [[w-cmp-fenton-catalyst-abrasive-alumina-silica]] (Lv1-2 — 알루미나/실리카
> 연마재 선택) [[w-cmp-plug-recess-coring-keyhole-overpolish-window]] (Lv2-1 — W 리세스·산화막 버프 공정창. 이 노트가
> 다루는 배리어 클리어 단계는 그 버프 단계의 **앞** 또는 **대체**에 해당) [[film-cu-barrier-ta-tan-co-selectivity]] (자매
> 에이전트 film-cu Lv2-2 — Cu:배리어(Ta/TaN/Co):옥사이드 3중 선택비. 이 노트는 그 구조를 W:Ti/TiN:옥사이드로
> 반복하되, **동일 선택비 크기라도 정반대 설계 목표(억제 vs 클리어)로 쓰이는 경우**가 있다는 점에서 갈라진다)
> 스코프: (1) 왜 W CMP에 배리어 전용 화학이 필요한가 — **상반된 두 공정 목표**(로컬인터커넥트 동시제거 vs
> W게이트 stop-on-barrier 억제), (2) Ti·TiN의 산화·용해 거동(과황산염 vs NaClO, 순환반응 메커니즘), (3) 배리어
> 슬러리 조성(알루미나/실리카·이중 산화제·계면활성제 억제제), (4) W:배리어:옥사이드 3중 선택비가 리세스/에로전에
> 미치는 영향 — 선택비는 **높을수록 좋은 게 아니라 창(window)이 있다**.

## 0. 출처 (3건, 특허 1차·원문전체 2건 + 논문 초록 1건)

1. **[1차·원문 전체]** S. C. Avanzino, C. M.-C. Woo, D. M. Schonauer, P. A. Burke (Assignee: Advanced Micro Devices,
   Inc.), "Chemical-Mechanical Polishing Slurry Formulation and Method for Tungsten and Titanium Thin Films," US
   Patent 5,916,855, filed 1997-03-26, issued 1999-06-29. USPTO PatFT 원문 PDF 직접 확보
   (`papers/avanzino1999-us5916855-w-ti-cmp-slurry.pdf`, 16쪽 전문 통독 — Google Patents는 접속 시 503, freepatentsonline은
   ECONNRESET로 실패해 `image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/5916855` 직링크로 원문 PDF 확보).
   §2.1·§3·§4의 W/Ti 제거율·선택비·dishing/erosion 표(Table I–VI)는 전부 이 특허 명세서 원문.
2. **[1차·원문 전체]** H.-F. Hou, W. Ward, M.-C. Yeh, C.-P. Tsai (Assignee: Cabot Microelectronics Corporation), "CMP
   Method for Suppression of Titanium Nitride and Titanium/Titanium Nitride Removal," US Patent 9,752,057 B2, filed
   2015-02-06, issued 2017-09-05. USPTO PatFT 원문 PDF 직접 확보 (`papers/hou2017-us9752057-tin-suppression-cmp.pdf`,
   13쪽 전문 통독 — 동일 직링크 방식). §2.3·§3의 TiN 억제 계면활성제·pH·연마재 데이터(Fig.1–5, Example 1–5)는 이
   특허 명세서 원문.
3. **[초록만]** D.-H. Feng, R.-B. Wang, A.-X. Xu, F. Xu, W.-L. Wang, W.-L. Liu, Z.-T. Song, "Mechanism of
   titanium–nitride chemical mechanical polishing," *Chin. Phys. B* 30(2), 028301 (2021), DOI:
   10.1088/1674-1056/abc161 (OpenAlex `abstract_inverted_index` 재구성으로 초록 전문 확인 — iopscience 본문 PDF는
   Cloudflare/JS 챌린지로 curl 직접 확보 실패, cpb.iphy.ac.cn도 Vue SPA라 정적 스크레이핑 불가, 미러 사이트 미러
   (미러 사이트 캡차, 미러 사이트 Cloudflare)도 모두 차단 — **본문 미확보, 초록 수치만 인용**). §2.2의 TiN 순환반응
   메커니즘·MRR·선택비 수치는 이 초록 그대로다. **주의**: 이 논문은 상변화메모리(PCM) 제조 맥락의 TiN CMP이며
   로직 W-plug의 TiN 배리어와 같은 슬러리/조건인지는 확인 못함 — 화학적 기전(순환 산화-제거)만 일반화해 인용한다.

## 1. 왜 별도 배리어 화학이 필요한가 — 두 가지 상반된 공정 목표

W CMP에서 Ti/TiN은 항상 W 아래 글루층(barrier/adhesion layer)으로 깔린다(Ti가 접착, TiN이 확산방지). 그런데
**이 배리어를 CMP가 어떻게 대해야 하는지는 응용에 따라 정반대**다(Avanzino 1999 서론, Hou 2017 배경):

- **로컬 인터커넥트(damascene 유사)**: 트렌치에 Ti/TiN/W를 순서대로 채운 뒤, 필드(트렌치 밖 평탄부)의 W·TiN·Ti를
  **전부** 벗겨내 인접 배선 간 단락을 막아야 한다(Avanzino 1999: "the CMP process must totally remove all
  conductive residues of tungsten, TiN, and Ti from the dielectric surface... to prevent shorting between adjacent
  metal lines"). 이 경우 목표는 **TiN·Ti도 W와 "비슷한 속도로" 다 깎이는 것**이고, 남은 문제는 옥사이드에 대한
  선택비뿐이다.
- **W 게이트 stop-on-barrier**: 옥사이드 트렌치에 배리어를 라이닝하고 W를 채운 뒤, W만 배리어의 **평탄부까지**
  깎고 멈춰야 한다(Hou 2017 배경: "a depression in oxide substrate is lined with a portion of the barrier layer and
  filled with the W metal... the tungsten is removed by CMP down to a planar portion of the barrier layer"). 이 경우
  배리어(TiN/Ti/TiN)는 **폴리시 스톱(polish stop)** 이어야 하므로 목표는 정반대 — **TiN 제거율을 최대한 억제**하는
  것이다. 억제가 부족하면 배리어 평탄부까지 갉아먹혀 "게이트 높이 저하(lower gate height)"라는 별도 결함이
  생긴다(Hou 2017 배경).

즉 같은 재료(TiN)에 대해 "선택비를 어느 방향·어느 크기로 설계할 것인가"는 **공정 의도**에 달렸다 — 이 노트
§4가 다루는 3중 선택비 논의는 이 두 레짐을 구분하지 않으면 서로 모순돼 보인다.

## 2. Ti/TiN의 산화·용해 거동

### 2.1 Ti — 과황산암모늄(ammonium persulfate) 산화 (Avanzino 1999 §B)

W가 Fe³⁺(또는 페리시안화물)로 산화되는 것([[w-cmp-wo3-passivation-oxidizer-kaufman]] §2)과 달리, Ti는 별도의
전용 산화제가 필요하다. Avanzino 1999는 "산화전위·Ti와의 착이온 열역학 안정성" 기준으로 산화제를 스크리닝해
**과황산암모늄 (NH₄)₂S₂O₈** 을 최적으로 선정했다(다른 후보: 시트르산·질산세륨암모늄·요오드산칼륨·과산화수소도
가능하나 화학 호환성·안정성 열위). 명세서는 W 산화 반응식만 명시적으로 준다:

  **W + 6Fe³⁺ + 3H₂O → WO₃ + 6Fe²⁺ + 6H⁺**

이는 Kaufman(1991)의 페리시안화물 반응([[w-cmp-wo3-passivation-oxidizer-kaufman]] §2 Eq.[2], `W + 6Fe(CN)₆³⁻ +
3H₂O → WO₃ + 6Fe(CN)₆⁴⁻ + 6H⁺`)과 **리간드만 다르고 6전자 이동 구조는 동일**하다(§6 verify [A]에서 전하수지
재현) — Fe³⁺/Fe²⁺ 산화환원쌍이 W를 WO₃로 부동태화하는 것은 배위환경과 무관한 일반적 메커니즘임을 보여준다.
Ti에 대해서는 명세서가 균형반응식을 주지 않지만, 정량 거동은 명확하다(Table I·II, §6 verify [B]):

- **과황산염은 Ti 제거율을 W보다 훨씬 크게 끌어올린다**: 3wt% Fe(NO₃)₃ 고정 조건에서 과황산염 1wt% 첨가 시
  Ti 제거율이 408→2002 Å/min(**4.9배**)로 뛰지만, W 제거율은 4400→6300 Å/min(1.4배)만 오른다(Table I) — 과황산염이
  "Ti 전용" 산화제라는 설계 의도가 실측으로 확인된다.
  - 참고: 이 반응은 Ti(0)→Ti(IV) 산화(4전자)로, 과황산염(S₂O₈²⁻ + 2e⁻ → 2SO₄²⁻, 표준환원전위 ≈ +2.01 V, 문헌값·
    이 특허에서 직접 측정 안 됨, **2차 인용 수준**)이 Fe³⁺(≈+0.77 V)보다 훨씬 강한 산화제라는 것과 정성적으로
    일치한다 — 순수 열역학 비교이며 이 노트에서 반응속도까지 검증한 것은 아니다.
- **과황산염 농도에 대한 반응이 W와 Ti에서 질적으로 다르다**(Table II, 0.03/0.1/0.3 wt%): Ti는 저농도 구간에서
  기울기가 급변(0.1→0.03 wt%에서 762 Å/min까지 급락)하는 뚜렷한 비선형인 반면, W는 두 구간 기울기가 거의
  같은 "**fairly linear**"(원문 표현)다. §6 verify [B]에서 구간별 기울기비로 재현.

### 2.2 TiN — NaClO 순환반응 메커니즘 (Feng 2021, 초록만)

TiN은 Ti와 달리 안정한 세라믹 질화물이라 산화 메커니즘이 다르다. Feng 2021(초록)은 NaClO(차아염소산나트륨)를
산화제로 쓴 산성 TiN 전용 슬러리에서 XPS·전위동태분극(potentiodynamic polarization)·ICP 분석으로 기전을 규명했다:

- **순환 반응 폴리싱 메커니즘(cyclic reaction polishing mechanism)** — W의 WO₃ passivation 순환(Kaufman 1991)과
  **같은 계열의 그림**: NaClO가 TiN 표면을 얇은 산화막(오초산화물/TiOxNy 계열로 추정, 초록은 조성을 특정하지
  않음)으로 산화시키고, 이 막을 연마입자가 기계적으로 벗겨낸다.
- **결정적 차이**: "정적 부식률과 ICP 결과 모두 TiN이 (직접) 용해되지 않음을 보인다"(초록 원문) — 즉 TiN은
  W·Ti와 달리 **화학적 직접용해 경로가 사실상 없고**, 산화막의 **기계적 제거가 제거율을 전적으로 결정**한다
  (초록: "the mechanical removal process of oxide layer plays a decisive role in the material removal rate"). W도
  정적 식각이 낮을 때는 기계지배 레짐이지만 TiN은 정적 식각 자체가 거의 0이라는 점에서 더 극단적이다.
- 정량치(이 슬러리 한정): MRR 76 nm/min, **TiN:SiO₂ 선택비 128:1**, **TiN:W 선택비 84:1** — TiN이 W와 옥사이드
  양쪽보다 수십 배 빨리 깎이는 **극단적 TiN-선호 화학**이다. 이는 §1의 "로컬 인터커넥트 동시제거"도 "stop-on-
  barrier 억제"도 아닌 **제3의 레짐** — W가 이미 필드에서 완전히 사라진 뒤 옥사이드 위 TiN/Ti만 남은 상태를
  마무리로 벗겨내는 **전용 배리어 클리어 스텝**에 해당한다(§4.3에서 재조명).

### 2.3 TiN 억제 화학 — 계면활성제 흡착 (Hou 2017, 원문)

§1의 stop-on-barrier 레짐에서는 TiN 제거율을 **낮춰야** 한다. Hou 2017(Cabot)은 pH 2–7 산성 슬러리에 **음이온
계면활성제**(알킬아릴 술포네이트, 대표적으로 도데실벤젠술폰산/DBS)를 넣으면 TiN 표면에 흡착막이 형성돼
제거율이 극적으로 억제됨을 보였다:

- Example 1(Fig.2, 여러 계면활성제 스크리닝, pH 2.3, 0.025 wt% 콜로이드 실리카): 억제제 없음 66 Å/min → DBS 7
  Å/min(**89% 억제**), ZETASPERSE 2300 9 Å/min(86% 억제)이 최고 성능. 반대로 SINONATE EHS는 82 Å/min으로
  오히려 **억제 없음보다 높게** 나와, 계면활성제 종류에 따라 방향이 반대가 될 수 있음을 보여준다(음이온
  술포네이트/알킬아릴계가 유효, 일부 술페이트계는 무효).
- Example 4(Fig.4, pH 2–7 스캔, DBS 유/무): 억제율이 pH2·3에서 최고(90%·94%)이고 pH가 오르면 완만히 감소해
  pH7에서 52%까지 떨어진다(§6 verify [C]에서 (무억제-억제)/무억제로 재계산해 문헌 표기 %와 대조, 6개 pH 전부
  ±1%p 이내 일치).
- Example 5(Fig.5, 연마재 10종): DBS 없이는 TiN RR이 연마재에 따라 **500 Å/min(알루미나) ~ 63 Å/min(콜로이드
  실리카)** 로 8배 가까이 갈리는데, DBS를 넣으면 **연마재 무관하게 전부 20 Å/min 이하**로 수렴한다 — 계면활성제
  흡착막이 연마재 종류(경도·형상)보다 지배적인 억제 변수임을 뜻한다.
- Example 3: 고형분(연마재 wt%) 0.025~10%에서도 억제율이 38~100% 범위를 유지하며, 2.5 wt%까지는 TiN RR이
  50 Å/min 아래로 유지되고 10 wt%에서도 71% 억제가 남는다 — 실사용 슬러리의 넓은 농도범위에서 강건하다.

## 3. 배리어 슬러리 조성 — 실제 사례 두 가지

- **로컬인터커넥트/플러그 겸용 슬러리(Avanzino 1999, "LI" 포뮬레이션)**: 저입경(<0.4 µm, 바람직 0.22 µm ± 0.05
  µm) 알루미나를 프탈산염(암모늄수소프탈레이트) 코팅해 표면전하를 중화하고, EVERFLO(지방산/식물유 기반
  현탁제)로 분산시킨 뒤 **두 산화제**(Fe(NO₃)₃ — W용, (NH₄)₂S₂O₈ — Ti용)를 동시에 넣는다. 여기에 염화암모늄을
  화학안정제로 소량 첨가(0.7~2 wt%)해 Fe³⁺/S₂O₈²⁻의 라디칼 부반응(변색)을 억제한다. **연마재를 코팅하고 첨가
  순서를 통제**하는 것 자체가 스크래치·결함을 줄이는 핵심 변수임을 이 특허가 처음 정량화했다(Batch A/B/C
  비교, 결함 2000→<200개로 10배 감소, 첨가순서만 바꿔서).
- **stop-on-barrier 억제 슬러리(Hou 2017)**: 실리카 또는 알루미나(10–300 nm) + 산화제(H₂O₂, 0~5 wt%) + 음이온
  술포네이트 계면활성제(10~50,000 ppm) + 산성 완충(pH 2–7, 바람직 2–5). 연마재·산화제는 [[w-cmp-fenton-catalyst-abrasive-alumina-silica]]와
  같은 계열이지만, **계면활성제가 선택성을 만드는 핵심 첨가물**이라는 점이 다르다 — 알루미나/실리카 자체의
  경도·IEP 차이(그 노트 §3)보다 표면 흡착 화학이 우세하다(§2.3 Example 5).

두 슬러리는 정반대 목표(§1)를 정반대 첨가물(과황산염으로 Ti 산화를 "가속" vs 계면활성제로 TiN 제거를 "억제")로
달성한다 — **배리어 CMP는 단일 화학이 아니라 공정 의도에 따라 갈라지는 두 화학 계열**이라는 것이 이 노트의
핵심 관찰이다.

## 4. W:배리어:옥사이드 3중 선택비와 리세스/에로전

### 4.1 로컬인터커넥트 — 선택비에는 최적 창이 있다 (Avanzino 1999 Table V)

10 µm 피처의 damascene형 W/Ti 라인에서 W:Ti 선택비를 4종 슬러리로 바꿔가며 dishing·erosion을 실측했다:

| 슬러리 | W(Å/min) | Ti(Å/min) | W:Ti | Erosion@50% | Dishing@10µm |
|---|---|---|---|---|---|
| 16 | 5800 | 300 | **19.3:1** | (미보고) | 2900 Å |
| 17 | 5902 | 1488 | 4.0:1 | 1700 Å | 2200 Å |
| 18 | 7539 | 2010 | 3.75:1 | 2000 Å | 1600 Å |
| 19 | 1322 | 1434 | **0.92:1** | 3499 Å | 3000 Å |

선택비가 **극단적으로 높을 때(19.3:1, Ti가 거의 안 깎임)** dishing이 가장 심하고(Ti 잔막 제거에 오버폴리시가
길어져 이미 recessed된 W가 더 파임 — 원문: "dishing and erosion are severe for slurry 16 where the last-removed
film... is polished at a slow rate"), **선택비가 1 미만으로 역전될 때(0.92:1, Ti가 W보다 빨리 깎임)** erosion·dishing
**둘 다 최악**이다(원문: "severe for slurry 19, wherein the W polish rate is slow... long polish times are required to
remove all film residues"). **균형점(3.75~4.0:1)에서 erosion+dishing 합이 최소**가 된다(§6 verify [D]). 즉:

> **선택비는 "높을수록 좋다"가 아니라 "너무 높아도, 1 미만으로 역전돼도 나쁘다"는 창(window)이 있다.**
> [[w-cmp-plug-recess-coring-keyhole-overpolish-window]]의 산화막 버프 트레이드오프(침식 vs 프로트루전, 둘 다
> 0으로 못 만듦)와 같은 형태의 결론 — W CMP는 어느 단계건 "선택비 극대화"가 아니라 "균형 창 찾기"다.

옥사이드에 대해서는 Table III 슬러리 8(프탈레이트 코팅 알루미나 + 과황산염 + EVERFLO)에서 **W:옥사이드 ≈
237:1**(6872/29 Å/min)이 나왔고, 이는 본문이 별도로 명시한 "best mode LI slurry, W:SiO₂ ≈ 240:1"과 자릿수·값
모두 근접한다(§6 verify [D], 1.3% 차). 본문의 "W:Ti = 4.4:1" 서술은 표의 구체적 어느 행과 정확히 대응하는지
특정되지 않으나(**미검증**), Table IV·V 실측 범위(3.06~4.97:1)의 중간값으로 같은 자릿수다.

### 4.2 Stop-on-barrier — 억제 레짐은 선택비 개념이 다르다 (Hou 2017)

§4.1의 "선택비 창"은 배리어가 W와 **함께 완전히 제거되는** 로컬인터커넥트 레짐의 이야기다. Stop-on-barrier
레짐(§1)에서는 배리어가 W 제거 단계 내내 **살아 있어야** 하므로, "선택비가 너무 높아 문제"라는 상한이 없다 —
Example 3(§2.3)이 보이듯 억제제는 고형분 10 wt%까지도 71% 억제를 유지하도록 설계되며, 목표는 W:TiN 선택비를
**가능한 한 크게** 키우는 것이다(단, 이 특허 자체는 W:TiN 정량 선택비 값을 청구항에 명시하지 않는다 —
**미검증**, TiN RR 절대값(<20~50 Å/min)만 특정). 즉 같은 "W:TiN 선택비"라는 지표라도 §4.1처럼 **최적점이 있는
지표**인지 §4.2처럼 **클수록 좋은 지표**인지는 **배리어가 최종적으로 제거 대상인지 스톱 레이어인지**에 달렸다.

### 4.3 별도 TiN 클리어 스텝 — 제3의 레짐 (Feng 2021)

Feng 2021의 TiN:W=84:1·TiN:SiO₂=128:1(§2.2)은 §4.1·§4.2 어느 쪽에도 속하지 않는다 — 이 슬러리가 투입되는
시점에는 필드의 W가 **이미 다 제거된 뒤**라 W에 대한 선택비가 dishing/erosion과 무관하고, 오직 "TiN을 빨리
치우면서 옥사이드는 최대한 보존"만 문제가 된다. 이는 [[film-cu-barrier-ta-tan-co-selectivity]]의 2단계 Cu CMP
구조(1단계: Cu 벌크 제거, 2단계: 배리어 전용 슬러리로 Ta/TaN을 Cu·옥사이드보다 3~4배 빨리 클리어, US7300602
청구항)와 **정확히 같은 논리**다 — W 공정도 로컬인터커넥트처럼 W·TiN을 한 슬러리로 동시 제거하는 대신, 별도
TiN 전용 클리어 스텝을 두면 Cu 공정과 같은 "배리어 최우선 제거" 방향(선택비 수십~백대일)을 쓸 수 있다.
**미검증**: 이 노트의 세 문헌은 서로 다른 논문/특허라 동일 공정 흐름 안에서 실제로 조합되었다는 실측 근거는
없다 — §4.1/§4.2/§4.3은 문헌상 존재가 확인된 **세 개의 선택비 설계 포인트**를 정리한 것이지, 세 단계로 이어진
하나의 실제 공정 레시피가 아니다.

## 5. 한계·불명확

- Feng 2021은 초록만 확보했다 — TiN 슬러리의 연마재 종류·정확한 pH·NaClO 농도, XPS 결합에너지·전위동태
  Ecorr 수치는 이 노트에서 확인 못함(**미검증**). 또한 PCM 응용 맥락이라 로직 W-plug TiN과 조성이 같은지도
  확인 못함.
- Avanzino 1999의 "W:Ti=4.4:1" 서술은 특정 표 행과 매칭이 안 됨(§4.1) — **미검증**.
- Ti의 4전자 산화 반응식은 이 특허에 명시되지 않아 §2.1에서 화학양론을 재구성하지 못했다 — W의 6전자
  반응식만 원문에 있고, Ti는 정성 거동(Table I·II)으로만 뒷받침한다.
- Hou 2017은 W:TiN 정량 선택비를 주지 않는다(TiN 절대 RR만) — §4.2의 "선택비가 클수록 좋다"는 서술은 논리적
  추론이지 이 특허의 직접 주장은 아니다.
- 과황산염의 표준환원전위(+2.01V)는 이 특허 밖 2차 인용 값이다(§2.1) — 실제 반응속도·pH 의존성은 검증 못함.
- §4.3의 "3단계 통합 공정" 서술은 문헌 간 추론적 결합이다(위 명시) — 시뮬레이터에 그대로 이식하면 안 되고,
  Cal-1 실데이터로 실제 공정 흐름을 확인해야 한다.

## 6. 검증 — 문헌값 상수 박고 assert (```python verify```, verify_claims.py 실제 실행)

**재현 요약(한 줄)**: Avanzino 1999(US5916855)의 W 산화식(W+6Fe³⁺+3H₂O→WO₃+6Fe²⁺+6H⁺)이 Kaufman
1991의 페리시안화물식과 동일한 18전하·6전자 구조임을 재현하고, Table I·II에서 과황산염이 Ti 제거율을
W보다 3배 이상 크게(4.9배 vs 1.4배) 끌어올리며 W는 두 농도구간 기울기비 1.13인 "거의 선형", Ti는 기울기비
10.9인 뚜렷한 비선형임을 확인, Hou 2017(US9752057) Fig.4의 pH별 TiN 억제율을 원자료(w/o,w/ RR)에서 직접
재계산해 문헌 표기 %(90,94,78,67,53,52)와 전부 ±1%p 이내로 일치시키며, Table V의 W:Ti 선택비 19.3→4.0→3.75→0.92
순서에서 erosion+dishing 합이 극단(19.3·0.92)에서 커지고 균형점(3.75~4.0)에서 최소가 되는 비단조 관계와
Table III(Avanzino 1999) 슬러리8의 W:옥사이드 237:1이 본문 서술 240:1과 1.3% 이내로 일치함을 재현 —
아래 4블록 PASS.

```python verify
# [A] W 산화 반쪽반응 — Avanzino 1999(bare Fe3+)와 Kaufman 1991(ferricyanide, Lv1-1 노트) 전하·전자수지 비교
# Avanzino: W + 6Fe3+ + 3H2O -> WO3 + 6Fe2+ + 6H+   (US5916855 원문 반응식)
# Kaufman : W + 6Fe(CN)6^3- + 3H2O -> WO3 + 6Fe(CN)6^4- + 6H+  (DOI 10.1149/1.2085434, Lv1-1 노트 Eq.[2])
charge_left  = 0 + 6*(+3) + 0            # W(0) + 6 Fe3+ + 3 H2O(중성)
charge_right = 0 + 6*(+2) + 6*(+1)       # WO3(중성) + 6 Fe2+ + 6 H+
assert charge_left == charge_right == 18
electrons_from_W = 6      # W(0) -> W(+6) in WO3
electrons_to_Fe  = 6 * 1  # 6x (Fe3+ + 1e- -> Fe2+)
assert electrons_from_W == electrons_to_Fe
print(f"[A] 전하수지 {charge_left}={charge_right}, 6전자 이동 일치 -> 리간드(아쿠아 vs 시아노)만 다르고 "
      f"Fe3+/Fe2+ 산화환원쌍의 W 산화 구조는 동일")
```

```python verify
# [B] Table I·II (US5916855) — 과황산염이 Ti를 W보다 훨씬 크게 가속, W는 선형에 가깝고 Ti는 저농도 급락
# Table I: 3wt% Fe(NO3)3 + 0.036wt% cupric nitrate 고정, persulfate 0% vs 1%
W_ctrl, Ti_ctrl = 4400.0, 408.0
W_1pct, Ti_1pct = 6300.0, 2002.0
ratio_Ti = Ti_1pct/Ti_ctrl
ratio_W  = W_1pct/W_ctrl
assert ratio_Ti > ratio_W * 3   # Ti "전용" 산화제 근거: 배수증가가 W의 3배 이상
# Table II: persulfate 0.03/0.1/0.3 wt%에서 W/Ti 제거율 (conc, W, Ti)
pts = [(0.30, 5082.0, 1753.0), (0.10, 4160.0, 1547.0), (0.03, 3875.0, 762.0)]
slope_W_hi  = (pts[0][1]-pts[1][1])/(pts[0][0]-pts[1][0])   # Å/min per wt%, 0.3->0.1
slope_W_lo  = (pts[1][1]-pts[2][1])/(pts[1][0]-pts[2][0])   # 0.1->0.03
slope_Ti_hi = (pts[0][2]-pts[1][2])/(pts[0][0]-pts[1][0])
slope_Ti_lo = (pts[1][2]-pts[2][2])/(pts[1][0]-pts[2][0])
ratio_W_slopes  = max(slope_W_hi,slope_W_lo)/min(slope_W_hi,slope_W_lo)
ratio_Ti_slopes = max(slope_Ti_hi,slope_Ti_lo)/min(slope_Ti_hi,slope_Ti_lo)
assert ratio_W_slopes < 2.0        # W: 두 구간 기울기 2배 이내 -> "fairly linear"(원문 표현)
assert ratio_Ti_slopes > 5.0       # Ti: 저농도에서 기울기 급변 -> "decreases sharply"(원문 표현)
assert ratio_Ti_slopes > ratio_W_slopes * 3
print(f"[B] Ti배수={ratio_Ti:.2f}x vs W배수={ratio_W:.2f}x (Ti전용성); "
      f"W기울기비={ratio_W_slopes:.2f}(선형), Ti기울기비={ratio_Ti_slopes:.2f}(비선형)")
```

```python verify
# [C] US9752057 Example 4(Fig.4) — pH별 TiN RR(w/o DBS, w/DBS)에서 억제율을 직접 재계산해 문헌 표기 %와 대조
fig4 = {2: (139, 14, 90), 3: (272, 16, 94), 4: (166, 36, 78),
        5: (141, 46, 67), 6: (93, 44, 53), 7: (91, 44, 52)}
for ph, (wo, wi, pct) in fig4.items():
    calc = (wo - wi) / wo * 100
    assert abs(calc - pct) <= 1.0, f"pH{ph}: 계산 {calc:.1f}% vs 문헌표기 {pct}%"
best_ph = max(fig4, key=lambda k: fig4[k][2])
assert best_ph in (2, 3)              # 원문: "highest ... suppression levels were attained at pH 2 and 3"
assert fig4[7][2] < fig4[3][2]        # 중성쪽(pH7)이 산성(pH3)보다 억제 약함
print("[C] pH별 재계산 억제율(%):",
      {k: round((v[0]-v[1])/v[0]*100, 1) for k, v in fig4.items()}, "| 최고 억제 pH:", best_ph)
```

```python verify
# [D] Table V(W:Ti 선택비 vs dishing/erosion) 비단조 관계 + Table III 슬러리8 W:oxide 교차확인 (US5916855)
table_v = {
    16: (5800.0, 300.0,  None,   2900.0),
    17: (5902.0, 1488.0, 1700.0, 2200.0),
    18: (7539.0, 2010.0, 2000.0, 1600.0),
    19: (1322.0, 1434.0, 3499.0, 3000.0),
}
ratios = {k: w/ti for k, (w, ti, e, d) in table_v.items()}
assert ratios[16] > ratios[17] > ratios[18] > ratios[19]        # 19.3 > 4.0 > 3.75 > 0.92
assert table_v[16][3] > table_v[17][3]     # 과도한 선택비(19.3:1) -> dishing 큼 (2900 > 2200)
assert table_v[19][3] > table_v[18][3]     # 선택비<1(0.92:1) -> dishing 최악 (3000 > 1600)
combined = {k: (e or 0) + d for k, (w, ti, e, d) in table_v.items() if e is not None}
best = min(combined, key=combined.get)
assert best in (17, 18)   # 균형 선택비(3.75~4.0:1)에서 erosion+dishing 합 최소

W8, Ti8, Ox8 = 6872.0, 1004.0, 29.0     # Table III 슬러리8 (프탈레이트 코팅 알루미나+과황산염+EVERFLO)
sel_W_ox = W8 / Ox8
assert abs(sel_W_ox - 240) / 240 < 0.05          # 본문 "best mode LI slurry ~240:1"과 5% 이내
measured_ratios = [3.06, 3.09, 3.75, 3.97, 3.98, 4.97]   # Table IV(11,12,14,15)+Table V(17,18) 실측 W:Ti
assert min(measured_ratios) < 4.4 < max(measured_ratios) # 본문 "W:Ti=4.4:1" 서술이 실측 범위 안에 있음(자릿수 확인)
print(f"[D] W:Ti 선택비 16>17>18>19 = {ratios[16]:.2f}>{ratios[17]:.2f}>{ratios[18]:.2f}>{ratios[19]:.2f}; "
      f"erosion+dishing 최소 슬러리={best}; W:oxide(슬러리8)={sel_W_ox:.1f}:1 (본문~240:1, {abs(sel_W_ox-240)/240:.1%} 차)")
```

**결과 해석(정직하게)**
- [A]는 원자·전하수지라는 화학의 필연적 제약을 재현한 것으로, 두 문헌이 "우연히 같은 숫자"인지는 이 검증과
  무관하다 — 6전자 반응이라는 **구조**가 서로 다른 산화제(아쿠아 Fe³⁺ vs 헥사시아노철산염)에서도 동일함을
  보인 것.
- [B]·[C]·[D]는 특허 명세서의 표·그림 값을 그대로 옮겨 문헌 서술("fairly linearly", "decreases sharply",
  "highest ... at pH 2 and 3", "severe for slurry 16/19")이 실제 숫자로 성립함을 확인한 것이지, 이 노트가 새로
  측정한 값은 아니다. Table V의 "균형 선택비가 좋다"는 결론은 **이 특정 슬러리 계열·10 µm 피처**에서 얻은
  것이라 다른 피처 크기·다른 화학에서 최적 선택비 숫자(3.75~4.0:1)가 그대로 전이된다는 보장은 없다 — 구조
  (비단조·창이 있음)만 일반화 가능.
- [D]의 "W:Ti=4.4:1" 자릿수 확인은 **매우 느슨한 검증**이다(범위 안에 있다는 것만 확인) — §4.1·§5에 명시한 대로
  특정 표 행과의 정확한 대응은 못 찾았다.

## 7. 이 에이전트의 결론 (W 공정통합 관점)

1. **배리어 CMP는 하나의 화학이 아니라 공정 의도로 갈라지는 최소 두 계열**이다 — (i) 로컬인터커넥트형: TiN·Ti를
   W와 함께 완전 제거, 선택비에 **최적 창**이 있음(§4.1) (ii) stop-on-barrier형: TiN을 폴리시 스톱으로 쓰기 위해
   제거율을 최대한 **억제**(§4.2). sim에 "W:배리어 선택비" 파라미터를 넣을 때는 반드시 어느 레짐인지 태그해야
   한다 — 같은 선택비 값이 한쪽에서는 최적, 다른 쪽에서는 정의조차 다르다.
2. **Ti와 TiN은 산화 메커니즘이 다르다**: Ti는 W처럼 산화제(과황산염)에 의한 능동 산화-제거를 겪지만, TiN은
   정적 용해가 거의 없고 산화막의 **기계적 제거만이 지배**한다(§2.2) — TiN 배리어의 제거율은 화학(산화제
   종류·농도)보다 **압력·연마재 접촉 빈도**에 더 민감할 가능성이 있다(정성적 추론, 이 노트에서 정량 검증 못함).
3. **계면활성제 흡착이 배리어 CMP의 숨은 3번째 손잡이**다 — 연마재 경도·산화제 종류([[w-cmp-fenton-catalyst-abrasive-alumina-silica]])
   못지않게, 술포네이트 계면활성제 흡착이 TiN 선택비를 좌우한다(§2.3, 연마재 종류에 따른 8배 편차를 계면활성제가
   지워버림). W 공정 모델에 배리어 항을 넣을 때 이 변수가 빠지면 안 된다.
4. [[w-cmp-plug-recess-coring-keyhole-overpolish-window]]의 산화막 버프 트레이드오프와 이 노트의 선택비 창은
   **같은 형태의 결론**(둘 다 "극단화하지 말고 균형점을 찾아라") — W CMP 공정 설계는 매 단계 극단 최적화가
   아니라 인접 단계와의 트레이드오프 안에서 창을 찾는 것이 반복되는 패턴이다.

## 8. 구현 요청 → agents/film-w/PROFILE.md "## 구현 요청" 참조

## 9. 자기시험
→ [[../../agents/film-w/EXAMS.md]] Lv2-2 문항 참조.
