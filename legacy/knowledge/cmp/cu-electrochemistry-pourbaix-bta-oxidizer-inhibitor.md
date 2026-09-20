<!-- V2-SECTION: R2-slurry | 공동: R5-wafer | 분배완료 2026-09-09 | 근거: chemistry, passivation, pourbaix, BTA, 전기화학 | 정본: ARCHITECTURE-V2.md §3 -->
# Cu 전기화학 심화 — Pourbaix 정량 경계, BTA 패시베이션 막의 실체, 산화제-억제제 균형 (film-cu Lv1-2)

> film-cu Lv1-2 | 작성일: 2026-09-09
> 선행: [[surface-chemistry-cu-w-pourbaix-passivation]] (Pourbaix 축의 정성 원리·Nernst 기울기 −59.1 mV/pH·Cu 다중 표면종 —
> 그 노트는 "정량 경계값 미검증"을 한계로 남겼다. 이 노트는 그 빈칸을 채운다: 표준전위 1차표에서
> Cu-H₂O 경계선을 **직접 계산**해 문헌 도표와 대조하고, BTA 막을 XPS·QCM 실측으로 정량화한다)
> [[cu-cmp-three-step-process-slurry-requirements]] (3단계 공정·rate quench — 이 노트 §6이 그 "Cu²⁺ 농도가 억제제 효과를
> 떨어뜨린다"는 특허 서술의 전기화학적 근거를 제공한다)
> [[slurry-components-overview]] (Kaufman 경쟁모델·BTA Langmuir 흡착 K=2.9e4) [[post-cmp-adsorption-cleaning-chemistry]]
> [[pattern-dependent-dishing-erosion]] [[preston-luo-dornfeld-mrr]] [[particle-wafer-interaction-mechanical-chemical-balance]]
> 스코프: (1) Cu-H₂O Pourbaix 경계의 **수치**(E°→Nernst→도표 대조), (2) H₂O₂의 실측 산화환원전위가 열역학값과 왜 다른가,
> (3) Cu-BTA 막의 열역학적 안정영역·화학조성·두께·형성속도, (4) 산화제/억제제 비가 정적식각·MRR·소프트랜딩을 어떻게 가르는가.
> 3단계 공정 파라미터(압력·MRR)는 형제 노트에 있으므로 재기술하지 않는다.

## 1. 1차 출처

- **Tamilmani, S. (2005)**, *Dissolution, corrosion and environmental issues in chemical mechanical planarization of copper*,
  Ph.D. dissertation, The University of Arizona (지도: S. Raghavan). 핸들 http://hdl.handle.net/10150/280774 — UA 리포지토리
  DSpace API로 251쪽 PDF 전문 확보(`papers/tamilmani2005-ua-thesis-cu-cmp-dissolution-corrosion.pdf`, fitz 텍스트 추출·그림 렌더
  판독). §3.1.1(STABCAL 계산법·자유에너지표 3.1), §4.1.1 Cu-H₂O 도표(그림 4.1), §4.1.4 Cu-BTAH-H₂O 도표(그림 4.4),
  §4.2.4.3 XPS(표 4.3), §4.2.5.1 QCM 패시베이션 속도론(그림 4.19–4.23). 이하 "Tamilmani 2005"로 표기.
- **Tamilmani, Huang, Raghavan, Small (2002)**, "Potential-pH Diagrams of Interest to Chemical Mechanical Planarization of Copper,"
  *J. Electrochem. Soc.* 149(12) G638, DOI: https://doi.org/10.1149/1.1516224 — Crossref로 DOI·저자·권호 확인. 위 학위논문
  §4.1의 저널판이지만 IOP PDF는 봇차단(HTTP 429)·초록도 S2/Unpaywall에 없음 → **본문 미확보**, 학위논문을 1차로 삼는다.
- **CRC Handbook of Chemistry and Physics, "Electrochemical Series" (P. Vanýsek)** — 공개 사본
  https://diverdi.colostate.edu/all_courses/CRC%20reference%20data/electrochemical%20series.pdf
  (`papers/crc-vanysek-electrochemical-series.pdf`, 10쪽, fitz 추출). 표 자체가 인용하는 원저는 Milazzo 1978·Bard, Parsons,
  Jordan *Standard Potentials in Aqueous Solutions* 1985·Bratsch 1989. 이 노트의 모든 E° 상수는 이 표에서 그대로 가져왔다
  (판본 연도는 PDF에 명기돼 있지 않음 — 판본 불명).
- **Lee, H. (2023)**, "Material Removal Characteristics of Abrasive-Free Cu CMP Using Electrolytic Ionization," *Micromachines*
  14(2) 272, DOI: https://doi.org/10.3390/mi14020272 , PMC9966509 — Europe PMC fullTextXML로 전문 확보. 산업형 Cu 슬러리 조성
  (H₂O₂/구연산/BTA)과 정적식각률·MRR 실측치의 1차 출처.
- **Lee, K. et al. (2021)**, "Galvanic corrosion inhibition from aspect of bonding orbital theory in Cu/Ru barrier CMP,"
  *Sci. Rep.* 11, DOI: https://doi.org/10.1038/s41598-021-00689-6 , PMC8551296 — 억제제 흡착이 Cu의 E_corr를 올리는 실측(니코틴산,
  BTA 아님)의 보조 출처. 저자는 Lee K, Sun S, Lee G, Yoon G, Kim D, Hwang J, Jeong H, Song T, Paik U (Crossref 확인).
- (DOI만 확인, 본문·초록 모두 미확보) Deshpande, Kuiry, Klimov, Obeng, Seal (2004), "CMP of Copper: Role of Oxidants and
  Inhibitors," *J. Electrochem. Soc.* 151(11) G788, DOI: https://doi.org/10.1149/1.1806395 — 제목이 이 단원과 정확히 일치하나
  IOP 차단으로 읽지 못했다. 이 노트의 어떤 수치도 이 논문에서 가져오지 않았다.

## 2. Cu-H₂O Pourbaix 경계 — 표준전위표에서 직접 유도

형제 노트 §2의 일반형 Nernst 식을 Cu 계에 실제로 대입한다. 25 °C, k = (RT/F)·ln10 = 0.05916 V. CRC 표 값(V vs SHE):

| CRC 표 반응 (환원 방향) | E° (V) | 이 노트에서의 용도 |
|---|---|---|
| Cu²⁺ + 2e⁻ = Cu | 0.3419 | Cu²⁺/Cu 수평선 |
| Cu⁺ + e⁻ = Cu | 0.521 | Cu⁺ 불균화 판정 |
| Cu²⁺ + e⁻ = Cu⁺ | 0.153 | Cu⁺ 불균화 판정 |
| Cu₂O + H₂O + 2e⁻ = 2Cu + 2OH⁻ | −0.360 | Cu/Cu₂O 경사선 (산성형으로 변환) |
| Cu(OH)₂ + 2e⁻ = Cu + 2OH⁻ | −0.222 | Cu(OH)₂ 용해도곱 → Cu²⁺/Cu(OH)₂ 수직선 |
| 2Cu(OH)₂ + 2e⁻ = Cu₂O + 2OH⁻ + H₂O | −0.080 | Cu₂O/Cu(OH)₂ 경사선 |
| H₂O₂ + 2H⁺ + 2e⁻ = 2H₂O | 1.776 | H₂O₂ 산화제 상한 (§3) |
| O₂ + 2H⁺ + 2e⁻ = H₂O₂ | 0.695 | H₂O₂ 환원제 상한 (§3) |

알칼리형(OH⁻ 표기) 반응을 산성형으로 바꾸려면 물의 자동해리(pK_w = 14.00)를 더한다: E°(산성형) = E°(알칼리형) + k·pK_w.
그러면 각 경계선은 (a = 용존 Cu 활동도):

1. **Cu²⁺/Cu (수평)**: E = 0.3419 + (k/2)·log a → a = 10⁻⁴에서 **0.2236 V**, 10⁻⁶에서 0.1644 V.
2. **Cu/Cu₂O (기울기 −k)**: 2Cu + H₂O = Cu₂O + 2H⁺ + 2e⁻, E° = −0.360 + 14k = **0.4682 V**, E = 0.4682 − 0.05916·pH.
   pH 14에서 −0.360 V(정의상 CRC 값으로 되돌아감), pH 8에서 −0.005 V.
3. **Cu²⁺/Cu₂O (기울기 +k)**: 2Cu²⁺ + H₂O + 2e⁻ = Cu₂O + 2H⁺, E° = 2·0.3419 − 0.4682 = **0.2156 V**,
   E = 0.2156 + 0.05916·pH + 0.05916·log a. 이 선이 1번 수평선과 만나는 **삼중점 pH = (0.3419 − 0.2156 − (k/2)log a)/k**
   → a = 10⁻⁴에서 **4.14**, 10⁻⁶에서 5.14.
4. **Cu²⁺/Cu(OH)₂ (수직)**: log K_sp = −2(0.3419 − (−0.222))/k = **−19.06**; 수직선 pH = (log K_sp + 2pK_w − log a)/2
   → a = 10⁻⁴에서 **6.47**, 10⁻⁶에서 7.47.
5. **Cu₂O/Cu(OH)₂ (기울기 −k)**: E° = −0.080 + 14k = 0.748 V, E = 0.748 − 0.05916·pH.
6. **Cu⁺ 불균화**: 2Cu⁺ = Cu + Cu²⁺, log K = (0.521 − 0.153)/k = **+6.22** → 착화제 없는 물에서 Cu⁺(aq)는 열역학적으로
   불안정하며, 그래서 Cu-H₂O 도표에는 Cu⁺(aq) 영역이 없다. §4의 BTA가 하는 일이 바로 이 Cu⁺를 고체 착체로 **안정화**하는 것.

### 2.1 Tamilmani 2005 그림 4.1과의 대조 (그림 판독, 렌더 220 dpi, 판독오차 ±0.03 V·±0.15 pH)

| 경계 | 이 노트 계산 | 그림 4.1 판독 (a = 10⁻⁴ 실선) | 비고 |
|---|---|---|---|
| Cu²⁺/Cu 수평선 | 0.224 V | 0.22 V | 일치 (Tamilmani 2005 그림 4.1) |
| 〃 a = 10⁻⁶ 점선 | 0.164 V | 0.16 V | 일치 (Tamilmani 2005 그림 4.1) |
| Cu/Cu²⁺/Cu₂O 삼중점 | pH 4.14 | pH ≈ 4.2 | 일치 (Tamilmani 2005 그림 4.1) |
| Cu/Cu₂O 선 @pH 8 | −0.005 V | ≈ 0.00 V | 일치 (Tamilmani 2005 그림 4.1) |
| Cu/Cu₂O 선 @pH 13 | −0.301 V | ≈ −0.30 V | 일치 (Tamilmani 2005 그림 4.1) |
| Cu²⁺/CuO 수직선 | (CuO ΔG_f° 미확보 — 계산 불가) | pH ≈ 5.65 (점선 6.7) | Cu(OH)₂ 대체계산 6.47 — §2.2 |
| Cu₂O/CuO 선 절편 | (동상) | 절편 ≈ 0.64 V, 기울기 ≈ −0.060 V/pH | Cu(OH)₂ 대체계산 0.748 V — §2.2 |

### 2.2 맞지 않는 부분을 정직하게: CuO vs Cu(OH)₂
CRC 표에는 CuO의 반쪽반응이 없고 Cu(OH)₂만 있다. 그림 4.1은 STABCAL(Huang, Montana Tech, ver. 2000)의 ΔG_f° 데이터베이스로
**CuO**를 안정상으로 그렸다. Cu(OH)₂는 CuO보다 열역학적으로 덜 안정한(준안정) 상이므로, Cu(OH)₂ 기준 경계는 CuO 기준 경계보다
(i) Cu²⁺/산화물 수직선은 **더 높은 pH**에, (ii) Cu₂O/2가 산화물 경사선은 **더 높은 전위**에 있어야 한다. 실제로
6.47 > 5.65(pH)·0.748 > 0.64(V)로 **방향은 맞지만 크기 차이(0.8 pH, 0.10 V)는 CuO ΔG_f° 없이는 검증 불가** — 미검증으로 남긴다.
(참고: 형제 노트 [[surface-chemistry-cu-w-pourbaix-passivation]] §4가 인용한 Gamagedara & Roy 2024의 pH 8 실측 표면종이
Cu(OH)₂·Cu₂O·CuO **혼재**였던 것과 정합적 — 준안정 Cu(OH)₂가 먼저 생기고 CuO로 탈수된다.)

## 3. 산화제 H₂O₂의 "실측 산화환원전위"는 열역학값보다 1 V 가까이 낮다 — 혼합전위

Tamilmani 2005 그림 4.1에는 **4 % H₂O₂ 용액의 백금전극 실측 산화환원전위**가 pH 2/4/6/8에서 사각형으로 찍혀 있다
(판독: 0.68 / 0.48 / 0.50 / 0.41 V vs SHE, ±0.05 V). 4 wt% ≈ 40 g/L ÷ 34.01 g/mol ≈ 1.18 M로 잡고 두 열역학 선을 그리면:
- 산화제로서의 상한 H₂O₂/H₂O: E = 1.776 − k·pH + (k/2)·log[H₂O₂] → pH 2에서 1.66 V, pH 8에서 1.30 V.
- 환원제로서의 상한 O₂/H₂O₂ (p_O₂ = 1 atm 가정): E = 0.695 − k·pH − (k/2)·log[H₂O₂] → pH 2에서 0.58 V, pH 8에서 0.22 V.

실측값 0.41–0.68 V는 **두 선 사이**에 있고 H₂O₂/H₂O 선보다 0.9–1.0 V 낮다(§7 verify 2). 해석: H₂O₂는 산화제이면서 동시에
환원제(O₂로 산화됨)이므로 전극에서 읽히는 것은 H₂O₂ 분해(2H₂O₂ → O₂ + 2H₂O)의 두 반쪽반응이 만드는 **혼합전위**이지,
H₂O₂/H₂O 쌍의 Nernst 전위가 아니다. CMP 설계에 주는 함의: "H₂O₂는 E° 1.776 V의 강산화제"라는 교과서 수치로 Cu의 상을 예측하면
틀린다 — **Cu 표면이 실제로 보는 전위는 0.4–0.7 V대**이고, 그래서 그림 4.1에서 H₂O₂ 점들이 pH 2–4에서는 Cu²⁺ 영역(용해),
pH 6–8에서는 CuO 영역 **하단 가장자리**(막 형성)에 걸린다. 형제 노트의 "Cu²⁺/Cu⁰ 경계가 pH 무관"이라는 서술과 결합하면,
산성 H₂O₂ 슬러리에서 Cu가 산화막 없이 곧장 용해되는 이유(정적식각의 열역학적 허용)가 전위-pH 좌표 위에서 그대로 읽힌다.

같은 논문의 문헌 정리(§2.2.2.2, 2차 인용): Cu 용해속도는 H₂O₂ 슬러리에서 pH 증가와 함께 떨어져 pH 6 이상에서는 용해가 없고
(Anderson 2003 UA 석사논문 인용), Du et al. 2004(JES 151 G230)는 pH 4 산성 슬러리에서 **MRR이 1 % H₂O₂에서 최대 후 감소**하며
저농도에서는 전기화학적 용해가, 고농도에서는 "산화막의 기계적 제거 후 용해"가 율속임을 보고했다 — 원문 미확보, Tamilmani 2005
본문 서술만 확인. 이는 [[slurry-components-overview]]의 Kaufman 경쟁모델(산화제 농도 정점)과 같은 현상이며, 이 노트의 전위-pH
언어로는 "H₂O₂ 농도↑ → 혼합전위↑ → Cu²⁺ 영역에서 CuO 영역으로 이동 → 부동태막이 두꺼워져 기계 제거가 율속"이 된다.

## 4. BTA 패시베이션 — 열역학(안정영역)과 실체(조성·두께·속도)

### 4.1 Cu-BTAH-H₂O 도표 (Tamilmani 2005 §4.1.4, 그림 4.4; Cu·BTAH 활동도 모두 10⁻⁴)
BTAH(C₆H₅N₃)의 ΔG_f°는 문헌에 없어 저자가 **기 여도법(group contribution)으로 추정**(표 3.1: BTAH +52.3, Cu(BTA) +54.48 kcal/mol)
했고, Cu-BTA 착체 자유에너지는 Tromans 1998(JES 145) 형성상수로 계산했다 — 즉 이 도표의 BTA 경계는 **추정 열역학 데이터**에
기반하며 저자 스스로 검증용으로 시트르산 이온 추정치(−278.3 vs 문헌 −277.89 kcal/mol)를 제시한 수준이다. 그림 4.4 판독:
- **CuBTA(s) 안정영역은 pH ≈ 2.7–9.8, 전위 −0.1 ~ +0.45 V**의 쐐기 모양. Cu²⁺/Cu 수평선(0.22 V) 바로 위, Cu 영역 바로 위에
  얹혀 있어 **Cu 금속이 산화되기 시작하는 바로 그 전위대**를 차지한다. 그 위(고전위)는 pH<5.6에서 Cu²⁺, pH>5.6에서 CuO.
- pH > 9.8에서는 Cu₂O가 CuBTA를 밀어낸다(알칼리 슬러리에서 BTA 효과가 약해지는 열역학적 이유). 본문: "Cu-BTA stability region
  will expand with the increase in BTAH concentration" — 활동도 10⁻⁴는 0.1 mM 수준으로 산업 슬러리(수 mM)보다 낮다.
- 0.001 M BTAH + 4 % H₂O₂ 실측 전위(원형): pH 2에서 0.71, pH 4에서 0.60, pH 6에서 0.55, pH 8에서 0.41 V(±0.05). 본문 결론:
  **중성 pH에서는 CuBTA/CuO 경계에, 산성에서는 Cu²⁺ 영역에** 떨어진다. → 산성 H₂O₂ 슬러리에서 BTA는 열역학적으로 "안정한 상"이
  아니라 **속도론적으로 버티는 막**이다(§4.3의 속도 데이터가 이를 뒷받침).

### 4.2 막의 실체 — XPS (Tamilmani 2005 §4.2.4.3, 0.5 M 하이드록실아민 + 0.01 M BTA, pH 6, 1 min 노출)
- 원자농도 Cu 15.48 / C 56.08 / O 8.21 / N 20.22 at%. **C/N = 2.8**(BTA 분자 C₆N₃의 3에 근접) → 표면에 BTA 존재.
- Cu 2p에 **shake-up 위성 피크 없음**(Cu²⁺ 부재), Auger에 Cu⁺ 571.0 eV 강피크·Cu⁰ 568.0 eV 약피크 → 막은 **1가 구리(Cu(I))-BTA**.
  Cu:C:N = 1:3.6:1.3(이론 1:6:3)로 Cu 과잉인 것은 X선이 막 아래 금속 Cu까지 투과하기 때문이라고 해석(막이 얇다는 방증).
- 구조: 탈양성자화된 N1이 Cu⁺에 결합하고 이웃 BTA의 N3가 배위결합해 **고분자 사슬 [Cu(I)BTA]ₙ**을 이룸(저자가 문헌 구조를
  그림 4.16b로 제시; Notoya-Poling SIMS의 [Cu₂(BTA)]⁺…[Cu₅(BTA)₄]⁺ 단편도 §2.2.5.2.1에서 인용). §2의 6번(Cu⁺ 불균화)과
  연결: 수용액에서 불안정한 Cu⁺가 BTA⁻와 불용성 고분자를 만들어 고정된다.

### 4.3 두께와 형성속도 — QCM (Tamilmani 2005 §4.2.5.1, 그림 4.19–4.23)
- 억제제 없는 0.5 M 하이드록실아민(pH 6)에서 Cu 질량손실 **≈ 50 µg/cm²/min**. BTA 0.01 M 포함 용액에 담그면 **질량이 즉시
  증가**해 최대 0.14 µg/cm² 후 0.12 µg/cm²에서 4 min 이상 정체 → 용해 정지.
- 0.12 µg/cm² = **6.06 × 10¹⁴ BTA 분자/cm²**. 단분자층 소요량은 수직 배향(단면 30 Å²)이면 3.3 × 10¹⁴, 수평(60 Å²)이면
  1.6 × 10¹⁴ → 막은 **2–4 분자층**. 첫 층은 Cu(I)-BTA 화학결합, 위층은 물리흡착.
- 2 min 먼저 용해시킨 뒤 BTA를 넣으면(case B) 질량이 **0.5 µg/cm²**까지 더 크게 증가 — 계면에 쌓인 Cu 이온이 BTA와 착체를
  이뤄 **침전**하기 때문(흡착이 아니라 침전). 이것이 [[cu-cmp-three-step-process-slurry-requirements]] §4 rate quench의 물리:
  패드 위 Cu²⁺가 많으면 BTA는 표면 단분자 패시베이션이 아니라 두껍고 느슨한 Cu-BTA 침전물을 만들어 슬러리 BTA를 소모하고
  막 품질을 떨어뜨린다.
- OCP: BTA 포함 용액에서 즉시 **0.11 V vs SHE**로 고정, BTA 없이 용해 중에는 0.07 V, BTA 투입 수 초 내 0.12 V로 상승.
  Tafel 추정 용해속도는 전 구간 **< 0.8 Å/min**(억제제 없는 경우의 환산값 ≈ 560 Å/min 대비, §7 verify 3).
- 보조 실측(Lee K. et al. 2021, PMC8551296, Cu 막, pH 10, 억제제는 니코틴산): E_corr −0.27 → +0.36 V, R_p 5704 → 49,897 Ω·cm²
  (억제효율 88.6 %) — 억제제 흡착이 Cu의 부식전위를 양의 방향으로 밀어 올리는 일반 거동을 BTA 외 분자에서도 확인.

## 5. 산화제-억제제 균형이 제거속도·정지(soft-landing)를 결정하는 방식

전위-pH 좌표에서 "어느 상이 안정한가"는 **산화제가 정하고**, 그 상이 실제로 얼마나 빨리 생기고 벗겨지는가는 **억제제와 기계력이
정한다**. 세 실측 축을 합치면:

| 축 | 억제제 없음 | 억제제 있음 (BTA) | 출처 |
|---|---|---|---|
| 정적 용해(pH 6, 하이드록실아민) | ≈ 50 µg/cm²/min (≈ 560 Å/min 환산) | < 0.8 Å/min | Tamilmani 2005 §4.2.5 |
| 부식전위 | 0.07 V | 0.11–0.12 V | Tamilmani 2005 그림 4.22 |
| 막 | 없음(계속 용해) | Cu(I)-BTA 2–4층, 즉시 형성 | Tamilmani 2005 §4.2.4–4.2.5 |

산업형 H₂O₂ 슬러리에서의 같은 균형(Lee H. 2023, PMC9966509, 표 1·그림 4·10): 조성 **H₂O₂ 3.00 wt% / 구연산 0.20 wt% /
BTA 0.05 wt% / 탈이온수 96.75 wt%, pH ≈ 3.7**(연마입자 없는 abrasive-free 용액). 이 조성에서 **정적식각률 26.4 nm/min**,
같은 용액으로 폴리싱하면 **MRR 302.5 nm/min**(인가전압 0 V 조건) → **MRR/정적식각 ≈ 11.5**. 즉 (i) pH 3.7 산성이라 §3의
H₂O₂ 혼합전위(≈0.5 V)는 Cu²⁺ 영역 — 열역학적으로 용해가 허용되고 BTA 0.05 wt%(≈4 mM)가 그것을 26 nm/min으로 눌러 놓는다;
(ii) 패드가 닿는 곳에서는 막이 계속 벗겨져 11배 빠르게 제거된다. 이 비율이 곧 **평탄화 선택성**이다: 패드가 닿지 않는 저지대
(트렌치 바닥)는 정적식각률로만 깎이고 고지대는 MRR로 깎이므로, 비가 클수록 [[pattern-dependent-dishing-erosion]]의 dishing이
작다. Tamilmani 2005 §2.2.5.2는 극단 사례로 질산 슬러리(폴리시 1.8 µm/min vs 정적식각 0.9 µm/min, 비 2)가 평탄화에 부적합함을
든다(Carpio 1995 재인용, 원문 미확보).

**소프트랜딩과의 연결**: 배리어 노출 직전에는 (a) 압력을 낮춰 기계적 막 제거 속도(MRR 항)를 줄이고, (b) 산화제 대비 억제제
비를 높여 정적식각 항을 더 낮춘다 — 두 조작 모두 "MRR/정적식각 비"를 유지하면서 절대 MRR만 낮추는 방향이다. 억제제만 늘리면
Cu-BTA 다층이 두꺼워져 MRR이 떨어지고(위 QCM에서 층수가 Cu 이온 농도에 민감), 산화제만 늘리면 §3의 Du 2004 정점 너머에서
막이 두꺼워져 역시 MRR이 떨어지는 대신 정적식각은 그대로라 비가 나빠진다. 그래서 두 농도는 독립 변수가 아니라 **비율로**
설계된다 — 이것이 형제 노트 특허의 "소프트랜딩 슬러리 = 벌크 슬러리 + 첨가제"라는 서술의 전기화학적 의미다.

## 6. 산화막 성장은 율속이 아니다 — Steigerwald 가정의 반례 (Tamilmani 2005 §2.1.4.2, 2차 인용)
Tamilmani 2005는 3 M H₂O₂·pH 6에서 산화막 성장속도 ≈ **10 Å/min**(장시간 속도론)인데 소형 폴리셔 MRR은 **80 Å/min**이었음을
들어, "산화막이 자라고 그것을 벗긴다"는 순차 모델이 모든 화학조건에서 성립하지는 않는다고 지적한다(Anderson 2003 석사논문 재인용).
MRR이 막 성장의 8배라는 것은 패드 접촉 순간의 **단기 산화 속도가 장시간 성장속도보다 훨씬 크거나**, 막 없는 금속면의 직접 용해·
마모가 병행한다는 뜻 — [[particle-wafer-interaction-mechanical-chemical-balance]]의 "마모유발 부식(RR_wc)" 항이 필요한 근거.

## 7. 코드 재현 (verify)

```python verify
# verify 1 — Cu-H2O Pourbaix 경계를 CRC 표준전위(papers/crc-vanysek-electrochemical-series.pdf)에서 유도해
# Tamilmani 2005 (UA 학위논문 hdl 10150/280774) 그림 4.1 판독값과 대조한다.
import math
R, F, T = 8.314462, 96485.33, 298.15
k = R*T/F*math.log(10)                       # 0.05916 V
assert abs(k - 0.05916) < 1e-4

# CRC 'Electrochemical Series' (Vanýsek) 표 값, V vs SHE — 기억이 아니라 papers/ PDF 8쪽 표에서 옮김
E0_Cu2_Cu   = 0.3419    # Cu2+ + 2e = Cu
E0_Cu1_Cu   = 0.521     # Cu+ + e = Cu
E0_Cu2_Cu1  = 0.153     # Cu2+ + e = Cu+
E0_Cu2O_alk = -0.360    # Cu2O + H2O + 2e = 2Cu + 2OH-
E0_CuOH2_alk = -0.222   # Cu(OH)2 + 2e = Cu + 2OH-
E0_2CuOH2_Cu2O_alk = -0.080  # 2Cu(OH)2 + 2e = Cu2O + 2OH- + H2O
pKw = 14.00

# (2) Cu/Cu2O 경사선: 알칼리형 -> 산성형
E0_Cu2O_acid = E0_Cu2O_alk + k*pKw                    # 0.468 V
line_Cu_Cu2O = lambda pH: E0_Cu2O_acid - k*pH
# (3) Cu2+/Cu2O 경사선 (기울기 +k)
E0_Cu2_Cu2O = 2*E0_Cu2_Cu - E0_Cu2O_acid               # 0.216 V
# (4) Cu(OH)2 용해도곱
logKsp = -2*(E0_Cu2_Cu - E0_CuOH2_alk)/k               # -19.06
# (6) Cu+ 불균화
logK_disp = (E0_Cu1_Cu - E0_Cu2_Cu1)/k                 # +6.22

def horiz(a):  return E0_Cu2_Cu + k/2*math.log10(a)
def triple_pH(a): return (E0_Cu2_Cu - E0_Cu2_Cu2O - k/2*math.log10(a))/k
def pH_CuOH2(a): return (logKsp + 2*pKw - math.log10(a))/2

# Tamilmani 2005 그림 4.1 판독값 (a=1e-4 실선, 220 dpi 렌더, ±0.03 V / ±0.15 pH)
fig = {"horiz_1e-4": 0.22, "horiz_1e-6": 0.16, "triple_pH_1e-4": 4.2,
       "Cu_Cu2O_pH8": 0.00, "Cu_Cu2O_pH13": -0.30,
       "CuO_vertical_1e-4": 5.65, "Cu2O_CuO_intercept": 0.64}

print(f"Cu2+/Cu 수평선: a=1e-4 {horiz(1e-4):.4f} V (그림 {fig['horiz_1e-4']}), a=1e-6 {horiz(1e-6):.4f} V (그림 {fig['horiz_1e-6']})")
assert abs(horiz(1e-4) - fig["horiz_1e-4"]) < 0.03
assert abs(horiz(1e-6) - fig["horiz_1e-6"]) < 0.03
print(f"Cu/Cu2O 산성형 E0 = {E0_Cu2O_acid:.4f} V; pH14 -> {line_Cu_Cu2O(14):.3f} V (CRC 알칼리값 {E0_Cu2O_alk} 복원)")
assert abs(line_Cu_Cu2O(14) - E0_Cu2O_alk) < 1e-9
print(f"Cu/Cu2O @pH8 {line_Cu_Cu2O(8):+.3f} V (그림 {fig['Cu_Cu2O_pH8']:+.2f}), @pH13 {line_Cu_Cu2O(13):+.3f} V (그림 {fig['Cu_Cu2O_pH13']:+.2f})")
assert abs(line_Cu_Cu2O(8) - fig["Cu_Cu2O_pH8"]) < 0.03
assert abs(line_Cu_Cu2O(13) - fig["Cu_Cu2O_pH13"]) < 0.03
print(f"Cu2+/Cu2O E0 = {E0_Cu2_Cu2O:.4f} V, 삼중점 pH(a=1e-4) = {triple_pH(1e-4):.2f} (그림 {fig['triple_pH_1e-4']}), a=1e-6 -> {triple_pH(1e-6):.2f}")
assert abs(triple_pH(1e-4) - fig["triple_pH_1e-4"]) < 0.15
# 활동도 100배 감소 -> 삼중점 pH +1.00 (해석적 성질)
assert abs((triple_pH(1e-6) - triple_pH(1e-4)) - 1.0) < 1e-9
print(f"Cu+ 불균화 log K = {logK_disp:+.2f} (>0 이므로 Cu+(aq) 영역이 도표에 없음)")
assert logK_disp > 5

# 맞지 않는 부분: CuO ΔGf°가 CRC 표에 없어 Cu(OH)2로 대체 -> 준안정상이므로 경계가 CuO보다 높은 pH/높은 E에 있어야 함
pH_ox = pH_CuOH2(1e-4)
E0_Cu2O_CuOH2_acid = E0_2CuOH2_Cu2O_alk + k*pKw
print(f"Cu2+/Cu(OH)2 수직선 pH = {pH_ox:.2f} vs 그림 Cu2+/CuO {fig['CuO_vertical_1e-4']} (차이 {pH_ox-fig['CuO_vertical_1e-4']:+.2f} pH, CuO 데이터 없어 미검증)")
print(f"Cu2O/Cu(OH)2 절편 = {E0_Cu2O_CuOH2_acid:.3f} V vs 그림 Cu2O/CuO 절편 {fig['Cu2O_CuO_intercept']} (차이 {E0_Cu2O_CuOH2_acid-fig['Cu2O_CuO_intercept']:+.3f} V, 미검증)")
assert pH_ox > fig["CuO_vertical_1e-4"], "준안정 Cu(OH)2 경계가 CuO 경계보다 낮은 pH면 열역학 순서가 뒤집힌 것"
assert E0_Cu2O_CuOH2_acid > fig["Cu2O_CuO_intercept"]
assert abs(pH_ox - fig["CuO_vertical_1e-4"]) > 0.5, "0.8 pH 차이를 '일치'로 위장하지 않는다"
print("OK verify1: Cu2+/Cu·Cu/Cu2O·삼중점은 그림 4.1과 ±0.03 V/±0.15 pH 내 일치, CuO 경계는 Cu(OH)2 대체로 방향만 확인")
```

```python verify
# verify 2 — 4% H2O2의 실측 산화환원전위(Tamilmani 2005 그림 4.1 사각점 판독, ±0.05 V)는
# H2O2/H2O Nernst 전위가 아니라 O2/H2O2 ~ H2O2/H2O 사이의 혼합전위임을 수치로 보인다. E0는 CRC 표.
import math
k = 8.314462*298.15/96485.33*math.log(10)
E0_H2O2_H2O = 1.776   # H2O2 + 2H+ + 2e = 2H2O   (CRC)
E0_O2_H2O2  = 0.695   # O2 + 2H+ + 2e = H2O2     (CRC)
c_H2O2 = 40.0/34.01   # 4 wt% ≈ 40 g/L -> 1.18 mol/L (밀도 1 g/mL 근사)
measured = {2: 0.68, 4: 0.48, 6: 0.50, 8: 0.41}   # V vs SHE, 그림 판독
for pH, Em in measured.items():
    E_up = E0_H2O2_H2O - k*pH + k/2*math.log10(c_H2O2)      # 산화제 상한
    E_lo = E0_O2_H2O2  - k*pH - k/2*math.log10(c_H2O2)      # 환원제 상한 (pO2=1 atm)
    gap = E_up - Em
    print(f"pH {pH}: 실측 {Em:.2f} V | O2/H2O2 {E_lo:.3f} < 실측 < H2O2/H2O {E_up:.3f} | 열역학 상한과 차이 {gap:.2f} V")
    assert E_lo - 0.05 < Em < E_up, "실측 혼합전위가 두 반쪽반응 사이를 벗어남"
    assert gap > 0.85, "실측이 H2O2/H2O Nernst값에 근접한다면 혼합전위 해석이 틀린 것"
# 실측 전위가 Cu2+/Cu 수평선(0.224 V @1e-4)보다 높아 모든 pH에서 Cu 산화는 열역학적으로 허용
assert all(v > 0.224 for v in measured.values())
print("OK verify2: 4% H2O2 실측 0.41–0.68 V는 Nernst 상한보다 0.9–1.0 V 낮은 혼합전위, Cu 산화는 전 pH에서 허용")
```

```python verify
# verify 3 — BTA 막 정량 (Tamilmani 2005 QCM/XPS) + 산업 슬러리 MRR/정적식각 비 (Lee H. 2023, PMC9966509)
NA = 6.02214e23
M_BTA = 119.12          # g/mol, C6H5N3 (12.011*6 + 1.008*5 + 14.007*3)
assert abs((12.011*6 + 1.008*5 + 14.007*3) - M_BTA) < 0.01
mass = 0.12e-6          # g/cm2, QCM 정체값 (Tamilmani 2005 §4.2.5.1)
n = mass/M_BTA*NA
print(f"0.12 µg/cm² BTA = {n:.3e} 분자/cm² (문헌 6.06e14)")
assert abs(n - 6.06e14)/6.06e14 < 0.01
n_upright = 1e16/30     # 1 cm² = 1e16 Å², 단면 30 Å²
n_flat    = 1e16/60
print(f"단분자층: 수직 {n_upright:.2e} (문헌 3.3e14), 수평 {n_flat:.2e} (문헌 1.6e14) -> 층수 {n/n_upright:.1f}~{n/n_flat:.1f}")
assert abs(n_upright - 3.3e14)/3.3e14 < 0.02 and abs(n_flat - 1.6e14)/1.6e14 < 0.05
assert 1.5 < n/n_upright < 2.5 and 3.5 < n/n_flat < 4.5   # "2 or 4 layers"
# XPS C/N 비: 원자농도 C 56.08 / N 20.22
CN = 56.08/20.22
print(f"XPS C/N = {CN:.2f} (문헌 2.8, BTA 이론 3)")
assert abs(CN - 2.8) < 0.05
# 억제제 없는 용해 50 µg/cm²/min을 두께속도로 환산 (Cu 밀도 8.96 g/cm³) vs BTA 시 Tafel 추정 <0.8 Å/min
rate_no_inh = 50e-6/8.96*1e8   # Å/min
print(f"억제제 없음 50 µg/cm²/min = {rate_no_inh:.0f} Å/min vs BTA 0.01 M: <0.8 Å/min -> 억제비 >{rate_no_inh/0.8:.0f}배")
assert 500 < rate_no_inh < 600 and rate_no_inh/0.8 > 500
# 산업형 H2O2/구연산/BTA 용액 (Lee H. 2023 표1·그림4·그림10, PMC9966509): 정적식각 26.4 nm/min, MRR 302.5 nm/min (0 V)
ser, mrr = 26.4, 302.5
print(f"Lee 2023: MRR/정적식각 = {mrr/ser:.1f}")
assert 11.0 < mrr/ser < 12.0
# 조성 합계 100 wt% 확인 (표 1)
assert abs(96.75 + 3.00 + 0.20 + 0.05 - 100.0) < 1e-9
print("OK verify3: BTA 2–4층·C/N 2.8·억제비 >500배·MRR/SER 11.5 재현")
```

재현 요약(한 줄): Cu²⁺/Cu 수평선 0.224 V·Cu/Cu₂O 선 pH 8에서 −0.005 V·삼중점 pH 4.14를 CRC E°로 계산해 Tamilmani 2005 그림 4.1 판독값(0.22 V·0.00 V·pH 4.2)과 ±0.03 V 내 대조 일치 (Tamilmani 2005).

## 8. 한계 (정직 표기)

- **CuO의 ΔG_f°(또는 CuO 반쪽반응 E°)를 1차표에서 확보하지 못했다.** 그래서 Cu²⁺/CuO 수직선(그림 5.65)과 Cu₂O/CuO 경사선(절편
  0.64 V)은 계산으로 재현하지 못했고, 준안정 Cu(OH)₂ 대체계산(6.47, 0.748 V)으로 부등호 방향만 확인했다 — 0.8 pH·0.10 V 차이의
  크기는 **미검증**. Pourbaix 원저 Atlas(1966/1974)도 여전히 미확보(형제 노트와 같은 한계).
- 그림 판독값은 220 dpi 렌더를 눈으로 읽은 것(±0.03 V, ±0.15 pH, H₂O₂ 점은 ±0.05 V). Tamilmani 2002 JES 저널판 본문을
  읽지 못해 학위논문 도표와 저널 도표가 동일한지는 확인하지 못했다(같은 저자·같은 시기·같은 STABCAL 계산이므로 동일 추정).
- Cu-BTA 도표의 BTA 열역학 데이터는 저자의 **기여도법 추정치**다(§4.1). CuBTA(s) 영역 경계(pH 2.7–9.8)는 이 추정에 종속되며
  독립 검증은 하지 못했다. 활동도 10⁻⁴(≈0.1 mM)는 산업 슬러리 BTA 농도(수 mM)보다 낮아 실제 영역은 더 넓다(저자 서술, 정량 미제시).
- §4.2–4.3의 XPS·QCM 실측은 **하이드록실아민 0.5 M·pH 6** 계에서 얻은 것이다. H₂O₂ 슬러리에서 Cu(I)-BTA 막의 층수·형성속도가
  같다는 보장은 없다 — Deshpande 2004(H₂O₂+BTA 직접 연구)를 읽지 못해 이 간극을 메우지 못했다. 미검증.
- Du 2004(1 % H₂O₂ MRR 정점)·Anderson 2003(pH 6 이상 용해 없음, 10 vs 80 Å/min)·Carpio 1995(질산 슬러리 정적식각)는 모두
  Tamilmani 2005 본문의 **2차 인용**이며 원문은 확보하지 못했다.
- Lee H. 2023의 MRR/정적식각 비 11.5는 abrasive-free·특정 압력 조건의 단일 실험값이다. 이 비가 dishing을 정량적으로 어떻게
  결정하는지(패드 비접촉 저지대 식각 모델)는 Lv2-1에서 [[pattern-dependent-dishing-erosion]]과 결합해 다뤄야 한다.
- 4 wt% H₂O₂ → 1.18 M 환산은 용액 밀도 1 g/mL 근사이며, 혼합전위 해석에서 p_O₂ = 1 atm 가정은 실제 용존 O₂보다 과대일 수
  있다(그래도 실측이 두 선 사이에 있다는 결론은 log 항이 작아 흔들리지 않음 — verify 2에서 하한에 −0.05 V 여유를 둠).

## 9. 자기시험
→ [[../../agents/film-cu/EXAMS.md]] Lv1-2 문항 참조.

## 10. 구현 요청
→ `agents/film-cu/PROFILE.md` "## 구현 요청" 참조 (Cu-H₂O Pourbaix 경계 함수 + 정적식각/MRR 비 파라미터).
