<!-- V2-SECTION: R2-slurry(연계) | 작성 2026-09-14 | defect-scientist Lv2-1 -->
# 부식·피트 결함의 형상·크기·밀도와 슬러리·공정 화학 의존성 — 그리고 스크래치·잔류입자와의 구별 신호

> 에이전트: defect-scientist Lv2-1 | 작성일: 2026-09-14
> 선행(반드시 먼저 읽음):
> [[cu-cmp-low-pressure-galvanic-corrosion-advanced-interconnect-review]] (film-cu Lv3-1 소유 — Cu/Ru·Cu/Mo 갈바닉·국부용해 **메커니즘**. 이 노트는 그 메커니즘을
>   재서술하지 않고 **결함 산출물(형상·개수·밀도)** 관점으로만 받는다),
> [[post-cmp-cleaning-chemistry-ammonia-citric-surfactant-corrosion]] (tool-post-clean Lv2-1 — 세정액 4축. 이 노트 §2의 "억제제 농도↑→유기·입자 결함↑"는 그 노트의
>   부식방지제 축과 짝을 이룬다),
> [[post-cmp-defect-classification-and-inspection]] (defect-scientist Lv1-1 — 결함 7종의 조작적 경계·검사장비. 이 노트 §1·§3은 그 노트의 "정적에칭 850/1200 Å/min·pit
>   정의·갈바닉 2–32 µA/cm²·dark-field·convex/concave"를 **부식 결함 축으로 확장**한다. 중복 서술 대신 링크로 참조)
> 관련: [[scratch-physics-source-signatures]] (Lv1-2 — 스크래치 형상 신호. §3의 구별에서 대비축) [[cu-electrochemistry-pourbaix-bta-oxidizer-inhibitor]] (BTA·Pourbaix — film-cu 소유)
> [[metal-contamination-device-impact-irds-limits]] [[pattern-dependent-dishing-erosion]]
> [[defect-density-yield-models-and-spatial-statistics]](Lv2-2 — 여기 §1.1의 edge-ring(r145–148mm)·부식 개수(0/12/363)를 **공간 비무작위성 검정·수율 폐형식**으로 받는다)
>
> **스코프(결함 관점만)**: (a) 부식·피트 결함의 **형상·크기·밀도** 정량(개수/wafer, 위치, 산화막 두께, 노듈 지름), (b) 슬러리·공정 화학 변수(pH·산화제 H₂O₂·억제제 BTA/MBTA
> 농도·세정/린스 시간·가압)→**부식 결함 밀도**의 실측 정량 관계, (c) 부식 결함을 **스크래치·잔류입자와 구별하는 신호**(검사 채널·형상·조성). **제외**(형제 영역): 갈바닉·혼합전위·
> Pourbaix 메커니즘 자체(film-cu/film-w), 억제제 흡착 등온식(inhibitor-chelator 노트), 세정액 조성 설계(tool-post-clean).

## 0. 출처 (2건 신규 1차 논문 + 선행 노트 상호링크 재조명; scope 상한 6건 내)

1. **[1차·원문 전체 확보]** S.-H. Choi, M. E. Kreider, A. C. Nielander, M. B. Stevens, G. Kamat, J. E. Koo, K. H. Bae, H. Kim, I. Y. Yoon, B. U. Yoon, K. Hwang,
   D. U. Lee, T. F. Jaramillo, "Origins of wear-induced tungsten corrosion defects in semiconductor manufacturing during tungsten chemical mechanical polishing,"
   *Appl. Surf. Sci.* 598, 153767 (2022), doi.org/10.1016/j.apsusc.2022.153767 (Samsung R&D + Stanford/SLAC SUNCAT; OSTI green OA purl 1984662;
   papers/choi2022-apsusc-w-corrosion-defects-wear-induced.pdf). §1·§2·§3의 W 부식 결함 개수/맵(Fig 3)·edge 위치·3 nm 산화막·용해 실측(Fig 7)·4종 부식 분류·검사법은 전부 이 논문.
   DOI Crossref 검증 완료(제목·저널·연도 일치).
2. **[1차·원문 전체 확보, CC-BY]** H.-Y. Ryu, B.-J. Cho, N. P. Yerriboina, C.-H. Lee, J.-K. Hwang, S. Hamada, Y. Wada, H. Hiyama, J.-G. Park,
   "Selection and Optimization of Corrosion Inhibitors for Improved Cu CMP and Post-Cu CMP Cleaning," *ECS J. Solid State Sci. Technol.* 8(5), P3058–P3062 (2019),
   doi.org/10.1149/2.0101905jss (한양대 J.-G. Park 그룹; CC-BY 4.0; papers/ryu2019-ecs-jss-cu-cmp-corrosion-inhibitor-selection.pdf). §2의 BTA/MBTA 농도→정적/동적 에칭·
   입자 결함 개수·제거효율(Fig 2·Fig 8)은 이 논문. 그림 수치는 fitz 2× 렌더 판독(Read)으로 추출 — **판독오차 ±5 % 명시**.

선행 노트에서 **결함 관점으로 재인용**(원 수치는 그 노트가 검증; 여기서는 부식 결함 축으로만 재조명):
[[post-cmp-defect-classification-and-inspection]] §3.1(Tamilmani 2005: 정적에칭 850 vs 연마 1200 Å/min → 저지대 과잉용해=피트, 0.01 M BTA로 정적에칭 <1 Å/min; Cu-SHA 석출 노듈
200 nm; 갈바닉 2–32 µA/cm²) · §6(dark-field·convex/concave·KLA·SPOS 검사) / [[cu-cmp-low-pressure-galvanic-corrosion-advanced-interconnect-review]](Cu/Ru ΔE_corr 0.49 V) /
IRDS 2024 YE(killer = 피치의 1/2). 이들은 **E1(그 노트에서 검증됨)**이며 여기서는 재유도하지 않는다.

## 1. 부식·피트 결함의 형상·크기·밀도 — "얼마나 크고 몇 개인가"

결함 밀도 모델(Lv2-2)로 넘어가려면 부식 결함도 스크래치처럼 **개수·크기·위치의 조작적 수치**를 가져야 한다. Lv1-1이 피트를 "국소 과잉용해가 남긴 함몰"로 정의만 했다면, 이 절은
1차 실측으로 그 정의에 숫자를 붙인다.

### 1.1 개수/wafer와 웨이퍼 내 위치 — Choi et al. 2022 (W 플러그, 300 mm)
Choi et al.(2022)은 로직 IC 양산에서 **PMOS 트랜지스터에 연결된 W 플러그**가 외부 입사에너지 없이도 부식되는 현상을 KLA 웨이퍼 스캐너로 계수했다. 핵심 정량:

- **개수는 0개에서 수백 개까지 공정조건으로 움직인다.** 가압 스플릿(0.5 psi, DIW 린스 중)에서 결함 개수(ea/wafer): 무가압 **0개** → edge 존 가압 **12개**(웨이퍼 가장자리에만) →
  center/middle/edge 전면 가압 **363개**(전면 분포)(Choi 2022, Fig 3b). 즉 부식 결함 밀도는 슬러리 청정도가 아니라 **가압·린스라는 공정 변수의 함수**다(§2).
- **위치는 edge에 국소화된다.** 저자는 이 부식이 300 mm 웨이퍼의 **반경 145–148 mm**(즉 최외곽 2 mm 링, 면적으로는 전체의 ~3.9 %, verify C)에서 발생한다고 명시한다. edge 존
  가압만 준 조건 2에서 결함이 정확히 그 링에 몰리는 것이 이를 뒷받침한다. **부식 결함의 "웨이퍼 내 분포"는 그 자체가 진단 신호다** — 무작위(입자)나 방사·선형(스크래치)과 달리
  edge-ring 편중은 압력/린스 불균일을 가리킨다(§3).
- **결함의 세로 구조 = 산화막의 유무.** 정상 W 플러그는 표면에 **~3 nm의 W 산화막(Zone 1: W+O)**이 남고 그 아래는 금속 W(Zone 2)다. 이 3 nm 부동태막이 남아 있으면 DIW 린스를
  70 s까지 늘려도 부식 결함이 **0개**지만, 막이 벗겨지면 그 자리가 용해되어 결함이 된다(Choi 2022). 즉 **부식 결함의 최소 크기 척도는 3 nm급 산화막 두께**이고, 결함은 이 막이
  국소적으로 제거된 뒤 하부 금속이 용해되며 자란다.

### 1.2 부식 결함의 형태 — 함몰(피트)과 석출(노듈)의 두 방향
부식 결함은 "파여서"만 생기지 않는다. Lv1-1 §3.1이 정리한 Tamilmani(2005)의 두 형태를 결함 크기 축으로 재조명한다:
- **함몰형(피트)**: 정적에칭 850 Å/min이 연마 1200 Å/min의 71 %로 저지대까지 녹여 평탄화를 원리적으로 막고, 그 국소 과잉용해가 표면에 남긴 함몰이 피트다(원 수치는 Lv1-1에서 검증).
- **석출형(노듈)**: Cu-SHA(하이드록실아민) 착물이 표면에 재석출해 **지름 최대 200 nm의 구형 노듈**로 자라다 떨어져 나간다(Tamilmani 2005, Lv1-1 재인용). 워터마크·잔사 결함의
  크기 앵커다. 즉 "부식 결함"은 피트(음각)와 노듈(양각)의 **양 방향**을 포함하며, 이 부호 차이가 §3의 검사 신호(concave vs convex)로 직결된다.

## 2. 슬러리·공정 화학 변수 → 부식 결함 밀도 (정량 관계)

이 절이 이 단원의 핵심이다: **어떤 화학·공정 변수가 부식 결함 개수를 얼마나 바꾸는가**를 실측 표/그림으로 못 박는다.

### 2.1 산화제(H₂O₂)와 억제제(BTA/MBTA) 농도 → 에칭·입자 결함 — Ryu et al. 2019 (Cu)
Ryu et al.(2019)은 10 mM 시트르산 + 5 wt% H₂O₂ + 10 mM 억제제(BTA 또는 5-메틸벤조트리아졸 MBTA), pH 3, 1 µm 전기도금 Cu에서 정적/동적 에칭과 세정 후 입자 개수를 측정했다.

- **산화제가 부식(에칭)을 켠다.** H₂O₂ 없으면 정적에칭 ~2 nm/min으로 무시할 수준이지만, 5 wt% H₂O₂를 넣으면 억제제 없는 Cu 정적에칭이 **~39 nm/min**으로 ~20배 뛴다
  (Ryu 2019, Fig 2a). 즉 부식 결함의 1차 구동원은 산화제이고, 억제제는 그것을 되돌리는 장치다.
- **억제제 농도가 에칭(=부식속도)을 억누른다.** 5 wt% H₂O₂ 하에서 정적에칭(nm/min): 무억제제 **39** → BTA 10 mM **8.5** → MBTA 10 mM **3.7**. 억제효율(=1−r/r₀)로 환산하면
  BTA **78 %**, MBTA **90 %**(verify A). 동적에칭도 같은 순서(410→235→150 nm/min)다. **MBTA가 BTA보다 같은 농도에서 더 강한 억제제**라는 것이 저자 결론이며, 이는
  메틸기의 유발효과로 트라이아졸 N의 고립전자쌍 반응성이 커지기 때문(메커니즘은 film-cu/inhibitor 영역, 여기선 결함 결과만).
- **역설: 억제제 농도↑ → 입자·유기 결함 개수↑.** 억제제가 만드는 소수성 Cu-억제제 착막이 오히려 연마입자(100 nm 실리카)를 더 붙들어, 세정 후 남는 입자 개수(ea/352 µm²,
  FE-SEM 계수)가 억제제 농도에 따라 크게 갈린다(Ryu 2019, Fig 8): 오염 직후 개수가 **MBTA 10 mM 1350 > BTA 10 mM 500 > MBTA 3 mM 180 > 무억제제 100**. 즉 강한 억제제를
  고농도로 쓰면 부식(피트)은 막아도 **입자·유기 결함이 한 자릿수 늘어난다.** 저자 처방은 "**낮은 농도의 강한 억제제**"(MBTA 3 mM)로, 3 mM MBTA가 10 mM BTA와 **동등한 억제효율**을
  내면서 오염 입자는 1/3(180 vs 500)이다. **부식 결함과 입자 결함은 억제제 농도라는 한 손잡이의 양 끝에 있다** — 이 트레이드오프가 결함 최소화의 실제 제약이다.
- **입자 제거효율(PRE)도 억제제가 좌우한다.** PRE(%) = (n_오염 − n_세정)/n_오염 × 100. Fig 8 판독: MBTA 10 mM **26 %**, BTA 10 mM **31 %**, MBTA 3 mM **66 %**, 무억제제 **62 %**
  (verify B). 고농도 억제제일수록 착막이 입자를 강하게 붙들어 **세정으로도 덜 떨어진다**(PRE↓). 이는 [[post-cmp-cleaning-chemistry-ammonia-citric-surfactant-corrosion]] §5의
  "BTA는 폴리시엔 필수, 세정엔 잔류물"이라는 서술을 개수로 정량화한 것이다.

### 2.2 세정·린스 공정과 pH → W 부식 결함 밀도 — Choi et al. 2022
Cu가 산화제·억제제 농도의 함수라면, Choi의 W 사례는 **후속 세정 공정(DIW 린스·메가소닉·가압)**과 **pH**가 부식 결함을 만든다는 것을 보인다.

- **DIW 린스 시간↑ → W 부식 결함↑.** 부식 결함 개수(ea)는 린스 0 s에서 **0개**, 220 s에서 **53개**까지 대체로 단조증가한다(Choi 2022, Fig 3a; 산포 큼). 저자 해석: 린스가 길수록
  플러그 위 3 nm W 산화막이 더 벗겨져 하부 W가 노출·용해된다. **부식 결함은 "오염물이 붙어서"가 아니라 "보호막이 벗겨져서" 생긴다** — 잔류입자(지형이 세정을 막아 생김,
  [[post-cmp-defect-classification-and-inspection]] §2.3)와 정반대의 인과다.
- **메가소닉 세정 시간**은 60 s까지 결함이 완만히 늘다 70 s에서 급증(Choi 2022) — 임계시간이 존재.
- **pH가 W 용해량을 자릿수로 가른다.** 유동셀 용출(0.4 mL/min) 실측: **알칼리 pH 11(0.001 M KOH)**에서 0.9 V vs RHE일 때 W 용출 **~1800 ppb**(최대, 전위 낮추면 감소)인 반면,
  **산성 pH 2(0.01 M HClO₄)**에서는 전위와 무관하게 **50–60 ppb**로 ~30배 낮다(Choi 2022, Fig 7c·7d). 즉 W는 산성에서 WO₃ 부동태로 안정, 알칼리·산화전위에서 WO₄²⁻로 녹아
  결함이 된다. 세정액이 알칼리(희석 NH₄OH pH 11.0)라는 점이 W 부식의 화학적 조건을 만든다(측정 pH: DI 6.8, 희석 NH₄OH 11.0, HF 2.5). 이 용출량을 Faraday로 등가 산화전류로
  환산하면 1800 ppb ↔ ~38 µA(n=6, 유량 0.4 mL/min; verify D)로, "얼마나 녹는가"가 결함 개수의 상류 변수임을 정량으로 잇는다.
- **부식의 4가지 결(저자 분류)**: ① 슬러리 화학과 W의 광유도 화학부식, ② 이종금속 접촉 갈바닉부식(메커니즘은 film-w 영역), ③ W 갭필 시임(seam) 보이드로 화학이 침투해 생기는
  결함, ④ 특정 패턴밀도에서 W 플러그의 비정상 산화(레이아웃 의존). Choi가 실제로 보고한 것은 ①(PMOS 연결 플러그)이다. **부식 결함은 단일 기전이 아니라 이 네 결이 겹친다**는 점이
  Lv2-2 밀도 모델에서 인자 분리를 요구한다.

## 3. 부식 결함 vs 스크래치·잔류입자 — 구별 신호 (검사 채널·형상·조성·분포)

같은 웨이퍼 스캐너가 잡은 점이 부식 피트인지 스크래치인지 입자인지 갈라야 원인 역추적이 된다. Lv1-1 §6이 정리한 검사 물리를 부식 축으로 확장한다.

| 구별축 | 부식·피트(음각)/노듈(양각) | 스크래치 | 잔류입자 |
|---|---|---|---|
| **형상 대칭** | 피트: 등방적 원형 함몰 / 노듈: 등방적 돌기 | **이방적 선형 홈, 길이 ≥ 50 µm**(Remsen 2006, Lv1-1) | 준구형 이물 |
| **음/양각 부호** | 피트=concave, 노듈=convex 둘 다 가능 | concave(홈) | convex(돌기) |
| **암시야 채널** | 원형이라 방향성 없음 → 협·광 채널 대칭 산란 | 정반사 방향(협채널 DNN)으로 편향 산란 | 광채널(DWN) 우세 |
| **웨이퍼 내 분포** | **edge-ring·패턴밀도 편중**(Choi: r 145–148 mm) | 긴 호(디스크 그릿) 또는 무작위 선 | 무작위 또는 지형(플러그) 국소 |
| **조성(SEM-EDS)** | 하부 금속 + 산화물(W+O, Cu-O), 이물 없음 | 모재와 동일 조성 | 이질 원소(Si·O = 슬러리, C = 유기) |
| **화학 의존성** | 산화제·pH·억제제 농도·린스시간으로 개수 급변(§2) | 입도분포 꼬리(LPC)로 개수 결정 | 슬러리 청정도·지형 |

핵심 세 가지:
- **형상만으로는 못 가른다 — 조성·분포·화학반응을 함께 봐야 한다.** Choi(2022)는 W 부식을 "기계적/화학적 기준 하나만으로 분류할 수 없다"고 명시하고, KLA 스캔으로 개수를 잡은 뒤
  **SEM-EDS·XPS로 산화물(W+O) 조성과 3 nm Zone 구조**를 확인해 부식으로 확정했다. 부식 결함의 결정적 신호는 **하부 금속의 산화물 존재**(이물이 아님)와 **edge/패턴밀도 편중 분포**다.
- **암시야 이중채널 부호**: 스크래치는 협채널(정반사 방향)로 산란이 편향돼 채널 크기비가 커지지만, 피트/노듈은 방향성이 없어 두 채널이 대칭이다 — Lv1-1 §6이 정리한 convex(입자)/
  concave(스크래치) 상관도에 **"등방(부식) vs 이방(스크래치)"** 축을 더한다. (이 이중채널 부호 규칙은 업체 검사기 설명이며 부식 피트 적용은 이 노트의 추론 — **미검증**, §6.)
- **인과 방향이 반대라 관리 대상이 다르다.** 잔류입자는 지형이 세정을 막아 생기고(세정 강화로 안 빠짐, Yu 2009), 부식 결함은 세정이 보호막을 벗겨 생긴다(린스↑→결함↑, Choi 2022).
  같은 "세정 강화"가 한쪽은 해결, 다른 쪽은 악화 — 따라서 **먼저 부식/입자를 구별해야 처방이 갈린다.**

## 4. python verify — 문헌값 재현

```python verify
import math

# ── (A) Ryu et al. 2019 (doi 10.1149/2.0101905jss) Fig 2 판독: 정적/동적 에칭(nm/min)과 억제효율 ──
# 슬러리 10 mM 시트르산 + 5 wt% H2O2 + 10 mM 억제제, pH3. 그림 판독값(±5%).
static_woH2O2 = 2.0                      # 무억제제, H2O2 없음 → 부식 거의 없음
static = {"none": 39.0, "BTA": 8.5, "MBTA": 3.7}   # w/ H2O2
dynamic = {"none": 410.0, "BTA": 235.0, "MBTA": 150.0}
# 산화제가 부식을 ~20배 켠다
assert static["none"] / static_woH2O2 > 15, "H2O2가 Cu 정적에칭을 자릿수로 올린다는 서술과 불일치"
# 억제효율 = 1 - r/r0
eff_static = {k: 1 - v / static["none"] for k, v in static.items() if k != "none"}
assert abs(eff_static["BTA"] - 0.782) < 0.01 and abs(eff_static["MBTA"] - 0.905) < 0.01, eff_static
# MBTA가 BTA보다 강한 억제제(정적·동적 모두)
assert static["MBTA"] < static["BTA"] and dynamic["MBTA"] < dynamic["BTA"]
# 동적 > 정적 (확산 우세)
assert all(dynamic[k] > static[k] for k in static), "동적에칭이 정적보다 커야 함(저자 서술)"
print(f"(A) H2O2 정적에칭 {static_woH2O2}->{static['none']} nm/min({static['none']/static_woH2O2:.0f}x); "
      f"억제효율 BTA {eff_static['BTA']:.0%}, MBTA {eff_static['MBTA']:.0%}")

# ── (B) Ryu et al. 2019 Fig 8 판독: 입자 결함 개수(ea/352µm²)와 제거효율 PRE ──
# (오염직후, 세정후, 그림에 병기된 PRE%)
part = {"MBTA10": (1350, 1000, 26), "BTA10": (500, 330, 31), "MBTA3": (180, 60, 66), "none": (100, 40, 62)}
for k, (n0, n1, pre_fig) in part.items():
    pre_calc = (n0 - n1) / n0 * 100
    assert abs(pre_calc - pre_fig) <= 5.0, f"{k}: PRE 재현 {pre_calc:.0f} vs 그림 {pre_fig} (판독오차 초과)"
# 억제제 농도↑ → 오염 입자↑ (역설): 10 mM 억제제가 무억제제보다 많다
assert part["MBTA10"][0] > part["none"][0] and part["BTA10"][0] > part["none"][0]
# MBTA 3 mM이 BTA 10 mM보다 오염 적음(저자 처방: 낮은 농도의 강한 억제제)
assert part["MBTA3"][0] < part["BTA10"][0], "3 mM MBTA 오염이 10 mM BTA보다 적어야 함(Fig 8)"
ratio = part["MBTA10"][0] / part["MBTA3"][0]
assert ratio > 5, f"MBTA 10mM vs 3mM 오염비 {ratio:.1f}"
print(f"(B) PRE 재현 오차 ≤5%p; 오염 MBTA10 {part['MBTA10'][0]} vs MBTA3 {part['MBTA3'][0]} ({ratio:.1f}배); "
      f"억제제 농도가 부식↓·입자↑의 손잡이")

# ── (C) Choi et al. 2022 (doi 10.1016/j.apsusc.2022.153767) Fig 3: 부식 결함 개수와 edge 위치 ──
zonal = {"none": 0, "edge": 12, "full": 363}     # 0.5 psi 가압 스플릿, ea/wafer
assert zonal["none"] == 0 < zonal["edge"] < zonal["full"]
assert zonal["full"] / zonal["edge"] > 25, "전면가압이 edge가압보다 한 자릿수 많은 결함"
# DIW 린스 시간: 0 s 0개 → 220 s 53개 (단조증가 경향)
rinse = {0: 0, 220: 53}
assert rinse[220] > rinse[0]
# edge 부식 위치: 300 mm 웨이퍼(r=150 mm) r=145~148 mm 링의 면적분율
r_out, r_in, r_wafer = 148.0, 145.0, 150.0
frac_edge = (r_out**2 - r_in**2) / r_wafer**2
assert 0.03 < frac_edge < 0.05, f"edge 링 면적분율 {frac_edge:.3f}"
print(f"(C) 가압 0/12/363 ea (전면/edge {zonal['full']/zonal['edge']:.0f}x); 린스 0->220s: 0->53개; "
      f"edge 링(145-148mm) 면적 {frac_edge:.1%} of 300mm wafer")

# ── (D) Choi 2022 Fig 7: W 용출량 → Faraday 등가 산화전류(부식량↔결함 연결) ──
# pH11(KOH) 0.9V vs RHE에서 ~1800 ppb W, pH2(HClO4) ~55 ppb. 유량 0.4 mL/min.
F = 96485.33          # C/mol
M_W = 183.84          # g/mol
n_W = 6               # W(0) -> W(VI) in WO4^2-
flow_L_s = 0.4e-3 / 60.0                          # 0.4 mL/min -> L/s
def equiv_current_uA(ppb):
    conc_g_L = ppb * 1e-6                         # ppb = µg/L = 1e-6 g/L
    mol_s = conc_g_L * flow_L_s / M_W             # mol/s of W dissolved
    return n_W * F * mol_s * 1e6                  # µA
I_alk = equiv_current_uA(1800.0)
I_acid = equiv_current_uA(55.0)
assert 35 < I_alk < 40, f"알칼리 등가전류 {I_alk:.1f} µA"
assert abs(I_alk / I_acid - 1800/55) < 1e-6       # 선형 환산이므로 비율 보존
assert I_alk / I_acid > 30, "알칼리/산성 용출비 ~30배 (W 부동태의 pH 의존)"
print(f"(D) W 용출 1800 ppb ↔ 등가 산화전류 {I_alk:.1f} µA (n=6, 0.4 mL/min); "
      f"산성 55 ppb ↔ {I_acid:.2f} µA → {I_alk/I_acid:.0f}배")

# ── (E) W 용해 반응식 화학량론 검증 (Choi 2022 본문 식, pH별) ──
# pH 4-6.5:  W + 4H2O = WO4^2- + 8H+ + 6e-
# pH 6.5-12.5: W + 8OH- = WO4^2- + 4H2O + 6e-
def check_balance(reactants, products, electrons_right):
    # 각 dict: element 원자수 합 + charge
    for el in set(list(reactants) + list(products)):
        if el == "charge":
            continue
        assert reactants.get(el, 0) == products.get(el, 0), f"{el} 불균형: {reactants.get(el,0)} vs {products.get(el,0)}"
    # 전하 균형: 좌 = 우 + (-1)*electrons (전자는 우변)
    assert reactants["charge"] == products["charge"] - electrons_right, "전하 불균형"
# 산성식: 좌 W + 4H2O ; 우 WO4^2- + 8H+ + 6e-
check_balance({"W":1,"O":4,"H":8,"charge":0}, {"W":1,"O":4,"H":8,"charge":-2+8}, 6)
# 알칼리식: 좌 W + 8OH- ; 우 WO4^2- + 4H2O
check_balance({"W":1,"O":8,"H":8,"charge":-8}, {"W":1,"O":4+4,"H":8,"charge":-2}, 6)
print("(E) W→WO4^2- 반응식(산성·알칼리) 원자·전하·전자수(n=6) 균형 OK")

# ── (F) 부식 결함 크기 척도 vs 검사 해상도 (선행 노트 연결) ──
# W 산화막 3 nm(부식 최소척도), Cu-SHA 노듈 200 nm, 광학지형 해상도 1.7 µm (Lee 2024, Lv1-1)
oxide_nm, nodule_nm, opt_res_nm = 3.0, 200.0, 1700.0
assert opt_res_nm / oxide_nm > 500, "3 nm 산화막은 광학 지형해상도로 직접 못 봄 → 개수는 산란/반사대비로 계수"
assert nodule_nm < opt_res_nm, "200 nm 노듈도 광학 지형해상도(1.7µm) 미만 → SEM 필요"
print(f"(F) 부식 최소척도 산화막 {oxide_nm} nm, 노듈 {nodule_nm} nm << 광학해상도 {opt_res_nm/1000:.1f} µm "
      f"→ 부식 결함 확정은 SEM-EDS/XPS 조성 확인이 필수(Choi 2022)")
```

수계산 대조 (Ryu et al. 2019 Fig 2·8, doi 10.1149/2.0101905jss; Choi et al. 2022 Fig 3·7, doi 10.1016/j.apsusc.2022.153767): (A) H₂O₂로 정적에칭 2→39 nm/min(~20배), 억제효율 BTA 78 %·MBTA 90 %; (B) PRE 26/31/66/62 % 그림값 ±5 %p 재현, 오염 MBTA10 1350 vs MBTA3 180(7.5배); (C) 가압
0/12/363 ea, edge 링 면적 3.9 %; (D) 1800 ppb ↔ 등가 38 µA, 산성/알칼리 33배; (E) W 반응식 균형; (F) 3 nm·200 nm ≪ 1.7 µm. 기계 실행은 §9 자가검사에서 `verify_claims.py`로 확인.

## 5. 근거 등급·충돌 판정 (EVIDENCE-RULES 서열)

| 주장 | 근거 | 등급 |
|---|---|---|
| W 부식 결함 개수 = 가압·린스의 함수(0/12/363 ea, 린스 220 s에 53개) | Choi 2022 양산 웨이퍼 KLA 실측 | E1(W) |
| W 부식은 edge(r 145–148 mm)·PMOS 플러그에 국소화 | Choi 2022 실측 | E1(W) |
| 산화제 H₂O₂가 Cu 부식(에칭)을 ~20배 켬, 억제제 농도로 78–90 % 억제 | Ryu 2019 정적/동적 에칭 실측 | E1(Cu) |
| 억제제 농도↑ → 입자·유기 결함 개수↑(역설), MBTA 3 mM이 최적 | Ryu 2019 Fig 8 FE-SEM 계수 | E1(Cu) |
| W 용해 pH 의존(알칼리 1800 vs 산성 55 ppb) | Choi 2022 유동셀 실측 | E1(W) |
| 피트는 등방 concave, 스크래치는 이방 선형(≥50 µm) | Remsen 2006(스크래치)·Choi 2022(부식) | E1 |
| 암시야 이중채널로 부식(등방) vs 스크래치(이방) 분리 | 업체 검사기 설명 + 이 노트 추론 | E5→미검증 |

충돌 없음(두 1차 논문은 서로 다른 금속계·다른 변수를 다뤄 상충하지 않는다). **Cu(Ryu)와 W(Choi)의 결과를 하나의 지수로 합치지 않는다** — 산화제·pH·억제제의 부호와 크기가 금속마다
다르므로 **팩별 분기**로 둔다(EVIDENCE-RULES §절차 3). 부식 결함 밀도의 지배변수: Cu는 **억제제·산화제 농도**, W는 **세정 pH·린스시간·산화막 잔존**.

## 6. 한계·미확보·미검증

- **정량은 상대·조건부다.** Choi Fig 3a는 산포가 커(같은 린스시간에 11·13·22개 공존) 단조증가 "경향"이지 함수식이 아니다. 개수-시간 회귀식은 이 논문에 없다 — **미확보**.
- **피트 직경(nm)의 직접 실측은 확보하지 못했다.** Choi는 개수·위치·산화막 두께(3 nm)를, Tamilmani는 노듈 지름(200 nm)을 주지만, **개별 피트의 지름·깊이 분포**를 준 1차 표는
  이번 범위(2건 + 선행)에서 없다 — Lv2-2/Lv3에서 SEM 단면 통계를 우선 확보 과제로 남긴다.
- **Ryu 수치는 그림 판독(±5 %)이다.** 본문에 절대 에칭·개수 수치가 없어 fitz 렌더 후 Read로 눈금 판독했다. Fig 8 BTA 10 mM PRE는 판독 34 %지만 그림 병기값 31 %를 채택(3 %p 차이).
- **§3 암시야 이중채널의 부식 피트 적용은 추론(E5→미검증).** 원 규칙은 입자/스크래치 구별용이고, "피트가 등방 대칭 산란"이라는 확장은 이 노트의 추론이다. 부식 피트를 이중채널로
  실제 분리한 1차 실측은 확보 못 함.
- **갈바닉·혼합전위·Pourbaix 메커니즘은 다루지 않았다**(형제 영역: [[cu-cmp-low-pressure-galvanic-corrosion-advanced-interconnect-review]], film-w). 이 노트는 그 결과인
  결함의 형상·개수·검사만 취했다.
- **구현 요청은 PROFILE.md 구현요청 섹션에 기재**(부식 결함 밀도 = f(산화제·억제제 농도, pH, 린스시간, 산화막잔존)의 팩별 확률항). sim/은 건드리지 않았다.

## 7. 자기시험
→ [[../../agents/defect-scientist/EXAMS.md]] Lv2-1 문항 참조.
