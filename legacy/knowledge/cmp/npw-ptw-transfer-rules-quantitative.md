<!-- V2-SECTION: R5-wafer | 분배완료 2026-09-09 | 근거: npw, pattern-, ptw, calibration | 정본: ARCHITECTURE-V2.md §3 -->
# NPW→PTW 전이 규칙 정량화 — 블랭킷에서 이전되는 파라미터와 패턴 웨이퍼에서만 뽑히는 파라미터 (Lv3-2)

> 에이전트: wafer-type Lv3-2 (NPW→PTW 전이 규칙 정량화: 어떤 파라미터가 이전되고 어떤 것이 새로 필요한가, sim/calibration 대상) | 작성일: 2026-09-09
> 선행: [[npw-ptw-test-wafer-fundamentals]] (NPW/PTW 정의·49점·MIT 마스크), [[npw-ptw-pattern-effect-gw-physics]] (NPW가 PTW를 예측 못하는 접촉역학), [[product-wafer-proxy-metrics-virtual-metrology]] (모니터 웨이퍼·유효압력비·레시피 변환계수)
> 관련: [[pattern-dependent-dishing-erosion]] (effective density·step-height 모델), [[pattern-metrics-dishing-erosion-stepheight]] (dishing/erosion 정의), [[wiwnu-pressure-velocity-wafer-scale]] (다이 위치별 블랭킷 제거율의 근원), [[preston-luo-dornfeld-mrr]] (K_p의 정체), [[hertz-gw-contact-mechanics]] (asperity 접촉면적)

## 0. 질문과 답의 형태

앞 단원들은 "NPW(블랭킷)가 PTW(패턴)를 왜 완전히 예측하지 못하는가"를 물리(접촉 곡률의 분화,
유효압력비 α(ρ))로 답했다. 이 단원은 그 반대 방향, 즉 **그럼에도 NPW에서 PTW로 무엇을 옮길 수
있는가**를 문헌의 캘리브레이션 절차에서 역으로 읽어낸다. 방법은 단순하다. PTW 예측 모델
4계열(현장 선형식, MIT 밀도·step-height 모델, Cu 다단계 모델, 확장 GW 모델)의 **파라미터 추출
절차**를 1차 문헌에서 확인해, 각 파라미터가 (a) 블랭킷 실험에서 오는지 (b) 패턴 실험에서만
오는지 (c) 레이아웃에서 계산되는지 표로 나눈다. 회사 관행은 쓰지 않고 공개 문헌·특허만 근거로 한다.

핵심 결론을 먼저 적는다. **네 계열 모두에서 NPW에서 PTW로 그대로 이전되는 물리량은 블랭킷
제거율(K, RR0, r_Cu/r_ox/r_b) 하나뿐이다.** 단 그 하나도 (i) 순간속도와 평균속도의 구분,
(ii) 다이 위치 의존성, (iii) 레시피 변환, (iv) 시간 드리프트라는 네 가지 보정을 거쳐야 한다.
나머지(planarization length, 유효압력비, 임계 step height, 최대 dishing, 감쇠시간, asperity
파라미터)는 전부 PTW 특성화 마스크에서만 추출되며, 그중 일부(PL)는 레이아웃과 무관해 한 번 뽑으면
다른 제품 레이아웃에 재사용된다.

## 1. 현장형 전이 규칙 — Kim & Seo (2002), 블랭킷 제거량 ↔ 패턴 제거량 선형식 (1차 원문 확보)

Sang-Yong Kim (ANAM Semiconductor), Yong-Jin Seo (Daebul Univ.), "Correlation analysis between
pattern and non-pattern wafer for characterization of shallow trench isolation–chemical–mechanical
polishing (STI–CMP) process," *Microelectronic Engineering* 60 (2002) 357–364,
doi.org/10.1016/S0167-9317(01)00694-3 (Lv1·Lv3-1에서 "원문 미확보·정의 불명"으로 남겨 두었던
논문. 2026-09-09 미러 사이트 조회 → 미러 사이트 storage PDF 확보, `papers/kim2002-mee-pattern-nonpattern-correlation-sti-cmp.pdf`,
8쪽 전문 텍스트 추출·Fig.7/8 판독).

- **실험**: IPEC 472, 폴리우레탄 패드·실리카 슬러리, 200 mm. NPW = PECVD-TEOS 16 000 Å, 49점·7 mm edge
  exclusion, 20 s 간격. PTW = STI 패턴 웨이퍼, 7 × 7 mm 더미 moat 어레이 중앙의 120 µm 트렌치에서
  필드 산화막·moat 질화막 두께와 step height(Tencor P30). 같은 조건으로 폴리시한 **85로트**로 상관을
  구하고 **50로트**로 재현성을 확인.
- **PTW의 비선형 3단계**(§3.1): 0–40 s는 필드 산화막 가장자리의 "shark's fin"만 깎여 두께가 거의 안 줄고,
  40–60 s가 실제 폴리시, 60–100 s는 moat 질화막에 닿아 다시 느려진다. 반면 NPW는 전 구간 선형(Fig.1).
  **이 비선형성이 NPW→PTW 전이가 단순 비율이 아니라 절편을 가진 선형식이 되는 이유다**(본 노트의 해석,
  논문은 절편의 물리적 기원을 논하지 않음 → **추정**).
- **전이식**(§3.2, Fig.7): Y = 0.9871·X + 1649.7, R = 0.7109. X = 패턴 웨이퍼에서 요구되는 필드 산화막
  제거 목표량, Y = 그에 대응하는 블랭킷 웨이퍼 제거 목표량(둘 다 Å, Fig.7 축 범위 X 1600–3000, Y
  2800–4800 판독). 논문은 이를 "correlation factor"라 부르지만 Fig.7이 회귀직선과 "R = 0.7109"를 함께
  표기하므로 피어슨 R로 판단 → **R² ≈ 0.51, 즉 블랭킷 제거량이 패턴 제거량 분산의 절반만 설명**한다.
- **잔차**: 이 식으로 계산한 폴리시 시간과 실제 시간의 차는 50로트 평균 **3.48 s**, 두께로 **104–176 Å**
  (본문 두 곳이 104–176과 104–167로 다르게 적혀 있음 — 원문 오기, 어느 쪽인지 미상). 공정 마진 약
  1800 Å 대비 무시 가능하다고 결론.
- **전이의 실체**: 블랭킷 제거율(20 s 간격 선형 회귀)과 이 선형식 두 개만으로 제품 폴리시 시간을 정한다.
  패턴밀도·PL 같은 물리 파라미터는 없고, 특정 마스크·특정 사이트(120 µm 트렌치)에 대해 lumped된 계수다.
  따라서 **레이아웃이 바뀌면 재캘리브레이션이 필요**하다(논문이 명시하지는 않으나 계수가 사이트 정의에
  묶여 있으므로 — 본 노트 판단).

## 2. MIT 밀도·step-height 모델의 캘리브레이션 규칙 — K는 블랭킷, PL은 패턴 (1차 원문 3편)

### 2.1 두 파라미터 모델: K(블랭킷)과 PL(패턴) — Boning et al. (1999)

Boning, Lee, Oji, Ouma, Park, Smith, Tugbawa, "Pattern Dependent Modeling for CMP Optimization and
Control," *MRS Spring Meeting Symp. P* (1999), boning.mit.edu/wp-content/uploads/2022/11/MRS99-reprint.pdf
(papers/boning1999-mrs-pattern-dependent.pdf, 원문 확인 — [[pattern-dependent-dishing-erosion]]과 동일 출처).
- "the original MIT model produced results that depend on **two extracted model parameters -- the
  planarization length (PL) and the blanket removal rate (K)**"; 통합모델은 여기에 step-height 감쇠시간
  τ와 접촉높이 h1 = a1 + a2·exp(−ρ/a3)의 a1, a2, a3를 **사이트별로 추가 추출**한다(MRS99 §III).
- **다제품 R2R 전이식**(MRS99 eq.5, §IV): 제품(device) D마다 모델 파라미터(유효 블랭킷 rate BR과 PL)를
  두고, 드리프트만 매 런 갱신한다:
  **BR(n) = BR(0) + BR_Device(D) + Delta(n)**.
  갱신은 **패턴 웨이퍼 4개 다이 위 7점**(Nova 인라인)으로 하며, 두 제품을 번갈아 폴리시한 제어 실험에서
  4-다이 평균 252 사이트 목표 두께 **±100 Å** 제어를 달성(Fig.11). 즉 "유효 블랭킷 rate"는 장비 공통항
  BR(0)+Delta(n)과 제품 오프셋 BR_Device(D)로 **분해되어 이전**된다 — NPW 모니터가 잡는 것은 앞의
  두 항이고 제품 오프셋은 패턴 웨이퍼에서만 나온다.

### 2.2 PL은 공정·패드 의존, 레이아웃 무관 — Ouma (1998) MIT 학위논문 (1차, 스캔본 판독)

Dennis Okumu Ouma, "Modeling of Chemical Mechanical Polishing for Dielectric Planarization," MIT EECS
PhD thesis (submitted Nov. 1998), dspace.mit.edu/handle/1721.1/9704 (DSpace REST API로 원문 PDF 229쪽 확보,
`papers/ouma1998-thesis-mit-cmp-dielectric-planarization.pdf`. **텍스트 레이어 없는 스캔본**이라 초록·목차·
p.107–108·p.142–146만 렌더해 눈으로 판독 — 이 절의 수치는 전부 그 판독값이며 나머지 장은 미독).
- 초록: "Polish characteristics of different dies on the wafer are captured through a **die-position dependent
  blanket rate** which accounts for blanket rate variation across a wafer." → NPW의 반경 프로파일(WIWNU)은
  다이 위치별 K로 PTW 모델에 이전된다([[wiwnu-pressure-velocity-wafer-scale]]의 P(r)V(r)이 여기 들어감).
- §5.4.3(p.142): "The optimal length must be determined for each consumable set and process conditions since the
  planarization length is dependent **not only on the polish pad type but also on the polish process conditions,
  notably the down force**."
- §5.4.4(p.143–145) 캘리브레이션 절차: PL 초기값 → 유효밀도 계산 → 모델-실측 비교 → 제곱합 최소화 루프.
  step-density 마스크(Mask1/Mask2)의 4 mm × 4 mm 밀도 블록마다 **최소 3점, 5점 이상은 이득 없음**; **센터
  다이 하나**면 충분("planarization lengths were determined across the wafer surface and little variation
  was found **after accounting for the blanket rate variation across the wafer**"); 폴리시 시간은 50 % 밀도
  구조가 국소 평탄화되도록(50 %는 블랭킷의 2배 속도로 깎임) 설정.
- **표 5.2(p.146) PL vs 공정조건** (Westech 472 계열, 판독):

  | 공정 | 다운포스 (psi) | 테이블 속도 (rpm) | PL (mm) |
  |---|---|---|---|
  | A (L,L) | 4.8 | 32 | 3.75 |
  | B (L,H) | 4.8 | 68 | 4.50 |
  | C (H,L) | 7.2 | 32 | 3.60 |
  | D (H,H) | 7.2 | 68 | 2.90 |

  "low down force and high table speed result in the longest planarization length." → PL은 **레시피 노브의
  함수**이므로 레시피가 바뀌면 PTW 재특성화가 필요하다(블랭킷 K는 [[product-wafer-proxy-metrics-virtual-metrology]]
  §2.2의 변환계수로 옮길 수 있지만 PL에는 그런 변환식이 문헌에 없음).
- **§5.4.5 검증(p.146)**: Mask1로 뽑은 PL 3.75 mm를 **다른 레이아웃(Mask2)**에 적용, "Drift in the blanket
  polish rate was the only parameter which was tracked." 105/158/316 s 세 시점 중 158 s에서 **RMS < 150 Å**,
  316 s(2 µm 중 1.5 µm 제거)에서 **RMS 270 Å**로 저밀도(10 %) 블록에서 모델이 깨짐. → **PL은 레이아웃 간
  이전 가능, 블랭킷 rate는 계속 추적**이 이 모델의 전이 규칙이다.
- §4.4(p.107–108, 서브패드 경도): IC1000/Suba IV(압축률 607 GPa⁻¹)·IC1400(479 GPa⁻¹)·proprietary 패드를 같은
  조건(8 psi, 30/28 rpm, SS-25, 2 µm TEOS 중 1 µm 제거)으로 비교 — 서브패드가 단단할수록 die-level range가
  작다(Fig.4.21 서술). 즉 PL은 **패드 스택 물성**에도 묶여 있어 NPW의 K와 별개로 소모품 교체 시 재추출 대상.

## 3. Cu 다단계 모델 — 세 블랭킷 rate만 이전, 나머지 7개는 패턴에서 (Tugbawa 2001·2002, 1차 원문)

Tugbawa, Park, Boning, Camilletti, Brongo, Lefevre, "Modeling of Pattern Dependencies in Multi-Step Copper
Chemical Mechanical Polishing Processes," *CMP-MIC* (2001), papers/tugbawa2001-cmpmic-cu-model.pdf (원문 확인);
Tamba E. Tugbawa, "Chip-Scale Modeling of Pattern Dependencies in Copper Chemical Mechanical Polishing
Processes," MIT EECS PhD thesis (2002), dspace.mit.edu/handle/1721.1/8083 (DSpace REST API로 232쪽 원문 확보,
`papers/tugbawa2002-thesis-mit-chip-scale-cu-cmp.pdf`, 텍스트 추출 가능).

- **표 3.1(학위논문 p.79) 단일 스텝 모델 파라미터**: 1단계(벌크 Cu) r_Cu, L1, H_ex; 2단계(배리어) r_Cu, r_b,
  L3; 3단계(오버폴리시) r_Cu, r_ox, L3, d_max. 여기에 H_ex와 d_max는 각각 선폭·선간격 함수로 3개씩의
  하위 파라미터(A, α_c, β1 / B, χ2, β2), 엣지 라운딩 W는 2개(C, s_c)를 가진다(§3.7.2).
- **추출 절차(§3.7.2, p.97–99)가 곧 전이 규칙이다**: "First, the **blanket wafer data** is used to extract the
  measured instantaneous blanket removal rate ... The effective blanket copper removal rate is set equal to the
  measured instantaneous blanket removal rate." 그 뒤 "L1 (and A, α_c, β1 if H_ex is significant) should be
  extracted from the **patterned** copper wafer data, after the effective blanket copper removal rate is
  extracted from blanket copper wafer data." 3단계도 "a total of seven parameters (excluding the blanket copper
  removal rate which is already known from stage one) need to be extracted" from dishing/erosion data.
- **블랭킷 rate는 상수가 아니다(§3.6, p.86–90)** — 이것이 이전 시 첫 번째 보정: Mirra, EPC-5001, 적층 패드에서
  블랭킷 Cu 제거량이 시간의 비선형 함수. 경험식 (eq.3.51–3.53)
  AR(t) = a1·t + a2·(e^{−t/τ} − 1), r_avg = AR/t, **r_inst = a1 − (a2/τ)·e^{−t/τ}**.
  표 3.3: 실험 1(5 psi, 63 rpm) a1 = 249.5 Å/s, a2 = 3986.6 Å, τ = 16.4 s, RMS 168.5 Å; 실험 2(2 psi, 43 rpm)
  120.0/924.0/9.71/195.5; 실험 3(4 psi, 75 rpm) 159.0/1176/7.7/102.4; 실험 4(=실험 1 반복, 다른 날) 239.6/1424/6.3/137.3.
  "In practice, the blanket rate is often thought to be a constant. It is obtained by polishing one or two blanket
  wafers for sixty or more seconds, and finding the average rate." → **관행의 60 s 평균 rate는 모델이 요구하는
  순간 포화 rate a1보다 낮다**(§6 verify (B)에서 정량: 10–26 %).
- **다단계 실험의 전이 실무(표 5.7, p.160)**: 패턴 웨이퍼 P-1…P-5(14/29/43/58/64 s)마다 **모니터 블랭킷 웨이퍼
  B-7…B-11을 같은 시간으로 짝지어** 폴리시 — 즉 PTW 캘리브레이션 실험 자체가 NPW 동반 측정을 전제한다.
- **정량 결과**: 1단계 추출(표 5.13, p.166)은 블랭킷 실험 1의 a1/a2/τ(249.5/3986.6/16.4)를 그대로 r_Cu로 쓰고
  L1 = 4893 µm를 얻었으나 **RMS 817 Å로 "unacceptable"** — 원인은 "the model wrongly assumes that all up-areas
  are initially contacted by the pad" (전기도금 토포그래피의 장거리 높이 변동). 3단계(표 5.17, p.179)는
  L3 = 3707 µm(엣지 라운딩 미포함)·4500 µm(포함), RMS **137 Å / 126 Å**(표가 두 행으로 판독되며 블랭킷 rate 열도
  행마다 달라 **판독 불확실**, L3와 RMS만 인용).

## 4. 접촉역학 모델 — RR0만 블랭킷, 나머지 전부 fit (Vasilev et al. 2011, 1차 원문)

Vasilev, Rzehak, Bott, Kücher, Bartha, *IEEE Trans. Semicond. Manuf.* 24(2) 338–347 (2011),
doi.org/10.1109/TSM.2011.2107756 (papers/vasilev2011-gw-pattern-density-size-cmp.pdf, [[npw-ptw-pattern-effect-gw-physics]]와 동일).
- 표 I 캡션: "all values, **except for the measured blanket removal rate RR0**, are extracted from model fitting."
  RR0 = 185 nm/min(블랭킷 측정), IL 1400/2950 µm, σ 120/140 nm, R_asperity 30 µm, α 11.25/20.5는 전부 PTW fit.
- **매크로↔마이크로 Preston 계수 변환(eq.18, 24, 25)**: 블랭킷에서 RR0 = κ_asp·F_wafer/(πσ)·K'_P·V/A_wafer, 따라서
  **K_P = κ_asperity/(πσ) · K'_P = K'_P / A_asp**, A_asp = πσR (asperity 하나의 평균 접촉면적, eq.18). 즉 NPW의
  K_P 안에는 패드 거칠기(σ, R)가 이미 곱해져 있고, PTW에서 up/down 영역별로 κ가 갈라질 때 이 곱이 풀린다.
  σ·R을 모르면 K_P를 up/down으로 분해할 수 없으므로 **NPW의 K_P 하나로는 PTW 분화를 원리적으로 복원 못 한다**
  ([[hertz-gw-contact-mechanics]]의 A_r ∝ W 결과와 같은 구조).
- **유효압력비의 하중균형 상한**: eq.14에서 κ_U = κ_D로 두면 up-region 평균압/공칭압 = e^{h/σ}/[(1−ρ)+ρ·e^{h/σ}].
  h→0이면 1, h/σ→∞이면 **1/ρ**. [[product-wafer-proxy-metrics-virtual-metrology]] §4의 Sorooshian(2005) 실측
  2.2/1.7/1.3(10/50/90 %)을 이 식에 넣으면 10 %·50 %는 h/σ ≈ 0.93·1.73으로 역산되지만 **90 %의 1.3은 상한
  1/0.9 = 1.11을 넘어** 순수 하중 재분배로는 설명이 안 된다(§6 verify (C)). Sorooshian의 "유효압력"은 제거율
  차이를 전부 압력으로 돌린 역산값이라 화학·온도 효과가 섞여 있다는 뜻으로 해석한다(**해석상 추정**).

## 5. 전이 파라미터 표 — 무엇이 어디서 오는가 (본 단원의 산출물)

| 파라미터 | NPW에서 측정 | PTW로 이전 규칙 | PTW에서 새로 추출 | 문헌값·근거 |
|---|---|---|---|---|
| 블랭킷 제거율 K, RR0, r_Cu/r_ox/r_b | ○ (핵심) | 그대로 입력. 단 **순간 rate**로 환산(a1, a2, τ) | × | (Tugbawa 2002) 표 3.3 a1 249.5 Å/s, 60 s 평균은 10–26 % 낮음; (Vasilev et al. 2011) RR0 185 nm/min |
| 다이 위치별 K(WIWNU) | ○ (49점) | die-position dependent blanket rate | × | (Ouma 1998) 초록·p.144 "PL은 웨이퍼 내 변동 작음, K 변동만 보정" |
| 레시피 변환계수 F₂/F₁ | ○ | NPW→NPW 전이(패턴 변수 없음) | × | US20060116785A1 STI 1.12·IMD 1.41 |
| 시간 드리프트 Δ(n) | ○ (모니터) 또는 PTW 인라인 | BR(n) = BR(0) + BR_Device(D) + Δ(n) | 제품 오프셋 BR_Device(D)만 PTW | (Boning et al. 1999) eq.5, ±100 Å |
| 현장 선형식 기울기·절편 | × | Y = 0.9871X + 1649.7 (사이트·마스크 고정) | ○ (85로트 회귀) | (Kim & Seo 2002) R² ≈ 0.51, 잔차 104–176 Å |
| planarization length PL, L1, L3 | × (h=0이라 관측 불가) | 레이아웃 간 재사용 가능, 레시피·패드 바뀌면 재추출 | ○ (step-density 마스크, 센터 다이) | (Ouma 1998) 표 5.2 2.90–4.50 mm; (Tugbawa 2002) L1 4893·L3 3707 µm |
| 유효밀도 ρ_eff(x,y) | × | 레이아웃 + PL로 계산(FFT) | 계산량 | [[pattern-dependent-dishing-erosion]] §2 |
| 유효압력비 α(ρ) | × | 없음 — 1/ρ 상한 아래 실측 | ○ | (Sorooshian 2005) 2.2/1.7/1.3; GW 상한 10/2/1.11 |
| 임계 step height H_ex(A, α_c, β1) | × | 없음 | ○ (선폭·선간격 함수) | (Tugbawa 2002) §3.4.1, 표 3.1 |
| 최대 dishing d_max(B, χ2, β2), 엣지 라운딩 W(C, s_c) | × | 없음 | ○ (dishing/erosion 시간 스플릿) | (Tugbawa 2002) §3.7.2 "seven parameters" |
| step 감쇠시간 τ, 접촉높이 h1(a1, a2, a3) | × | 없음 | ○ (사이트별) | (Boning et al. 1999) §III, RMSE 273→98 Å |
| asperity σ, R, IL, 형상 α | × (K_P에 σR이 곱해져 숨음) | 없음 — K_P = K'_P/(πσR) 분해 불가 | ○ (fit) | (Vasilev et al. 2011) 표 I, eq.25 |

읽는 법: 첫 네 줄이 "이전되는 것"이고 전부 **블랭킷 제거율의 변형**이다. 다섯째 줄(Kim & Seo)은 물리 파라미터
없이 K와 회귀식만으로 버티는 현장형이며, 그 대가가 R² 0.51이다. 여섯째 줄 이하는 h > 0에서만 존재하는 양이라
NPW가 원리적으로 볼 수 없고, 그중 PL만이 "레이아웃 무관"이라는 성질 덕분에 제품 간 이전이 된다.

## 6. Python 재현 — 선형 전이식·블랭킷 순간속도·하중균형 상한·PL 범위

```python verify
import math

# ---------- (A) Kim & Seo 2002 (doi.org/10.1016/S0167-9317(01)00694-3) Fig.7 전이식·§3.2 잔차 ----------
slope, icpt, R = 0.9871, 1649.7, 0.7109          # Y = slope·X + icpt [Å], R (Kim & Seo 2002 Fig.7)
R2 = R ** 2
print(f"(A) R^2 = {R2:.3f} — 블랭킷 제거량이 패턴 제거량 분산의 {100*R2:.0f}%만 설명")
assert 0.50 <= R2 <= 0.51
xs = [1600, 2000, 2400, 3000]                     # Fig.7 x축 범위(판독, Å)
for X in xs:
    Y = slope * X + icpt
    print(f"    X={X} Å → Y={Y:.0f} Å (Y/X={Y/X:.2f})")
assert 3200 <= slope * 1600 + icpt <= 3260 and 4600 <= slope * 3000 + icpt <= 4620   # 회귀선 양끝 판독값 3230·4610
assert all(2800 <= slope * X + icpt <= 4800 for X in xs)                          # Fig.7 y축 범위 안
dt = 3.48                                                                          # s, 50로트 평균 시간차
rr_lo, rr_hi = 104 / dt * 60, 176 / dt * 60                                        # Å/min, 104–176 Å 환산이 함의하는 블랭킷 RR
print(f"    3.48 s ↔ 104–176 Å ⇒ 블랭킷 RR {rr_lo:.0f}–{rr_hi:.0f} Å/min")
rr_fig_lo, rr_fig_hi = 2800 / 2.05, 4800 / 1.30      # Fig.7 y축(2800–4800 Å) ÷ Fig.8 폴리시 시간(1.30–2.05 min, 판독)
assert rr_fig_lo < rr_lo and rr_hi < rr_fig_hi        # 논문 내부 정합: 환산 RR이 그림에서 읽히는 RR 범위 안
assert 176 / 1800 < 0.10                              # 잔차 176 Å < 공정 마진 1800 Å의 10 %

# ---------- (B) Tugbawa 2002 학위논문 표 3.3 + eq.3.51–3.53: 블랭킷 rate의 시간의존과 60 s 평균의 과소평가 ----------
tab33 = {1: (249.5, 3986.6, 16.4, 168.5), 2: (120.0, 924.0, 9.71, 195.5),
         3: (159.0, 1176.0, 7.7, 102.4), 4: (239.6, 1424.0, 6.3, 137.3)}   # (Tugbawa 2002) a1 Å/s, a2 Å, τ s, RMS Å
def AR(t, a1, a2, tau): return a1 * t + a2 * (math.exp(-t / tau) - 1)     # eq.3.51
def r_avg(t, a1, a2, tau): return AR(t, a1, a2, tau) / t                   # eq.3.52
def r_inst(t, a1, a2, tau): return a1 - (a2 / tau) * math.exp(-t / tau)    # eq.3.53
for k, (a1, a2, tau, rms) in tab33.items():
    r0 = r_inst(0.0, a1, a2, tau)
    assert r0 >= 0, (k, r0)                                  # t=0 순간 rate가 음수면 식 부호를 잘못 읽은 것
    deficit = 1 - r_avg(60, a1, a2, tau) / a1
    print(f"(B) 실험{k}: r_inst(0)={r0:.1f}, r_avg(60 s)={r_avg(60, a1, a2, tau):.1f} vs 포화 a1={a1} Å/s → 60 s 평균이 {100*deficit:.0f}% 낮음")
    assert 0.08 <= deficit <= 0.30                            # 관행(60 s 1–2장 평균)이 모델 입력(순간 포화 rate)을 10–26 % 과소평가
# Fig.3.19(실험 1) 평균 rate 판독점과 표 3.3 파라미터의 대조
pts = [(7, 65), (14, 100), (23, 113), (29, 135), (36, 153), (43, 163), (50, 170), (57, 187)]   # (t s, r_avg Å/s) 판독 ±5
a1, a2, tau, _ = tab33[1]
for t, r in pts:
    m = r_avg(t, a1, a2, tau)
    print(f"    t={t:2d} s: 모델 {m:6.1f} vs 판독 {r} Å/s ({100*(m-r)/r:+.0f}%)")
assert all(abs(r_avg(t, a1, a2, tau) - r) / r < 0.06 for t, r in pts if t >= 29)   # 후반 5점 6 % 이내
assert abs(r_avg(7, a1, a2, tau) - 65) / 65 < 0.25                                # 초기점은 21 % 차이(RMS 168 Å와 정합) — 정직 기록
assert tab33[1][:3] == (249.5, 3986.6, 16.4)   # 표 5.13이 1단계 r_Cu로 '그대로' 재사용한 값 — 전이의 실체

# ---------- (C) Vasilev 2011 eq.14(κ_U=κ_D) 하중균형 상한 vs Sorooshian 2005 유효압력비 ----------
def alpha_up(rho, x):                      # up-region 평균압/공칭압, x = h/σ
    e = math.exp(x)
    return e / ((1 - rho) + rho * e)
for rho in (0.1, 0.5, 0.9):
    assert abs(alpha_up(rho, 60.0) - 1 / rho) < 1e-6    # h/σ→∞: 1/ρ (밀도모델 RR=K/ρ의 극한)
    assert abs(alpha_up(rho, 0.0) - 1.0) < 1e-12        # h→0: 1 (NPW와 동일)
lit = {0.1: 2.2, 0.5: 1.7, 0.9: 1.3}                    # (Sorooshian 2005) 유효압력/인가압력 요약값
for rho, a in lit.items():
    if a < 1 / rho:
        x = math.log(a * (1 - rho) / (1 - a * rho))
        print(f"(C) ρ={rho}: α={a} → h/σ={x:.2f} (σ 120–140 nm면 h≈{x*120:.0f}–{x*140:.0f} nm)")
    else:
        print(f"(C) ρ={rho}: α={a} > 하중균형 상한 1/ρ={1/rho:.2f} → 압력 재분배만으로 설명 불가")
assert lit[0.9] > 1 / 0.9                                # 90 %: 1.3 > 1.11 — 문헌값과 GW 상한의 모순을 숨기지 않는다
x10 = math.log(2.2 * 0.9 / (1 - 0.22)); x50 = math.log(1.7 * 0.5 / (1 - 0.85))
assert 0.9 < x10 < 1.0 and 1.7 < x50 < 1.8

# ---------- (D) PL 범위·방향(Ouma 1998 표 5.2, Tugbawa 2002), asperity 접촉면적(Vasilev 2011 eq.18), 전이 잔차 오더 ----------
PL = {"A(4.8psi,32rpm)": 3.75, "B(4.8psi,68rpm)": 4.50, "C(7.2psi,32rpm)": 3.60, "D(7.2psi,68rpm)": 2.90}   # mm (Ouma 1998)
assert max(PL, key=PL.get).startswith("B")               # 저압·고속이 최장 — 원문 서술 재현
assert all(2.5 <= v <= 5.0 for v in PL.values())
assert min(PL.values()) < 3.0                            # Park VMIC98 "3–5 mm" 서술과 D 조건 2.90 mm는 살짝 어긋남 — 기록
L1, L3 = 4893, 3707                                       # µm (Tugbawa 2002) 표 5.13·5.17
assert 1000 <= L1 <= 6000 and 1000 <= L3 <= 6000          # "millimeter range"
sigma, Rasp = 140e-9, 30e-6                               # (Vasilev et al. 2011) 표 I
A_asp = math.pi * sigma * Rasp                            # eq.18, K_P = K'_P / A_asp (eq.25)
r_eq = math.sqrt(A_asp / math.pi)
print(f"(D) A_asp = πσR = {A_asp:.2e} m² (등가 반경 {r_eq*1e6:.2f} µm) — K_P 안에 숨은 패드 거칠기 인자")
assert 2.0e-6 < r_eq < 2.1e-6
resid = {"Kim&Seo 시간차 환산 상한": 176, "Ouma Mask1→Mask2 158 s": 150, "Ouma 316 s": 270,
         "MRS99 R2R ±": 100, "Tugbawa 3단계": 137}       # Å, 서로 다른 실험·지표 — 오더 비교만
assert all(100 <= v <= 300 for v in resid.values())
assert 817 > 2 * max(resid.values())                      # Tugbawa 1단계 실패 사례(817 Å)는 성공 사례들의 2배 초과
print("ALL OK")
```

## 7. 정량 재현 요약 (§6 대조표)

| 항목 | 문헌값 | 재현값 | 판정 |
|---|---|---|---|
| (A) 전이식 R | 0.7109 (Kim & Seo 2002) | R² 0.505 | 블랭킷이 패턴 분산의 51 %만 설명 |
| (A) 시간차 3.48 s ↔ 104–176 Å | (Kim & Seo 2002) §3.2 | 함의 RR 1793–3034 Å/min, Fig.7/8 판독 범위 1366–3692 Å/min 안 | 내부 정합 |
| (B) 60 s 평균 rate vs 포화 a1 | 표 3.3 (Tugbawa 2002) | 실험 1–4에서 26/13/12/10 % 과소 | 관행의 NPW rate는 모델 입력보다 낮다 |
| (B) Fig.3.19 평균 rate 8점 | 65–187 Å/s (판독) | t ≥ 29 s 6 % 이내, t = 7 s는 −21 % | 초기점 불일치는 RMS 168.5 Å와 정합 |
| (C) α(ρ) 하중균형 상한 | 2.2/1.7/1.3 (Sorooshian 2005) | h/σ 0.93/1.73, **90 %는 상한 1.11 초과** | 모순 그대로 기록(원인 추정만) |
| (D) PL vs 공정 | 2.90–4.50 mm (Ouma 1998) | 저압·고속 최장 재현; 2.90은 "3–5 mm" 밖 | 방향 일치, 범위는 소폭 이탈 |
| (D) A_asp | σ 140 nm, R 30 µm (Vasilev et al. 2011) | 1.32e-11 m², 등가 반경 2.05 µm | 계산만(실측 대조값 없음) |

재현 요약(한 줄): (Kim & Seo 2002) 전이식 Y=0.9871X+1649.7의 R 0.7109를 R² 0.505로, (Tugbawa 2002) 표 3.3 a1 249.5 Å/s에서 60 s 평균 rate 184.8 Å/s(−26 %)를, (Sorooshian 2005) 유효압력비 2.2/1.7/1.3을 (Vasilev et al. 2011) 하중균형식과 대조해 90 % 조건의 상한 초과를, (Ouma 1998) 표 5.2 PL 2.90–4.50 mm의 공정 의존 방향을 §6 코드로 대조했다.

## 8. 미검증·미확보·한계 (정직 표기)

- Kim & Seo 2002: "correlation factor 0.7109"를 피어슨 R로 해석한 것은 Fig.7의 회귀 표기에 근거한 **판단**이며
  논문이 정의를 명시하지 않는다. 잔차 두께가 본문에 104–176 Å과 104–167 Å 두 가지로 적혀 있어 어느 쪽이
  맞는지 **미상**. 절편 1649.7 Å의 물리적 해석(shark's fin 단계)은 **본 노트의 추정**.
- Ouma 1998 학위논문: 스캔본이라 초록·목차·p.107–108·p.142–146만 판독. 표 5.2·RMS 150/270 Å은 **눈으로 읽은 값**
  (숫자 오독 가능성 있음). Chapter 7의 공정 특성화 사례, 2.4–2.5 다이 위치별 블랭킷 rate 모델식은 **미독**.
- Tugbawa 2002: 표 5.17이 텍스트 추출에서 두 행으로 나오고 열 정렬이 깨져 L3 3707/4500 µm·RMS 137/126 Å 외의
  값(d_max 하위 파라미터 등)은 **판독 불확실**로 인용하지 않았다. Fig.3.19 데이터점은 ±5 Å/s 판독.
- Sorooshian 2005의 90 % 밀도 유효압력비 1.3이 GW 하중균형 상한 1/ρ = 1.11을 넘는 이유는 **미상**(화학·온도
  효과 혼입 또는 밀도 정의 차이로 추정). Vasilev eq.14를 κ_U = κ_D로 단순화한 것도 본 노트의 근사.
- Stine et al. 1998 (doi.org/10.1109/66.661292), Ouma et al. 2002 (doi.org/10.1109/66.999598) IEEE TSM 저널판:
  Crossref로 DOI 실존만 확인, Unpaywall/OpenAlex 전부 closed → **본문 미확보**(학위논문·MRS99로 대체).
- Kim & Seo 식은 특정 마스크·사이트(120 µm 트렌치)에 대한 lumped 계수라 다른 레이아웃으로의 이전 가능성은
  논문이 다루지 않음 → "레이아웃 바뀌면 재캘리브레이션"은 **본 노트의 판단**.
- 전이 잔차 100–300 Å(§6 (D))은 서로 다른 장비·막·지표의 숫자를 오더만 모은 것이지 교차검증이 아니다.

## 9. 결론 (Lv3-2 답)

1. **이전되는 것은 블랭킷 제거율 하나이고, 네 겹의 보정을 거친다.** ① 순간 rate로 환산(관행의 60 s 평균은
   포화 rate보다 10–26 % 낮음, Tugbawa 표 3.3), ② 다이 위치별 K(Ouma: PL은 웨이퍼 내 불변, K만 변동),
   ③ 레시피 변환계수(TSMC 특허 0.5–2, 패턴 변수 없음), ④ 드리프트 Δ(n)와 제품 오프셋 BR_Device(D)의 분해
   (MRS99 eq.5, ±100 Å).
2. **새로 필요한 것은 h > 0에서만 정의되는 양 전부다**: PL(2.9–4.5 mm, 레시피·패드 의존), α(ρ)(2.2/1.7/1.3,
   GW 상한 1/ρ와 90 %에서 모순), H_ex·d_max·W(선폭·선간격 함수, 7개 하위 파라미터), τ·h1(a1..a3), σ·R·IL·α.
   이 중 **PL만 레이아웃 무관**이라 Mask1→Mask2처럼 제품 간 이전이 되며(RMS < 150 Å), 나머지는 소모품·레시피가
   바뀌면 재추출한다.
3. **NPW 단독 전이의 상한은 R² ≈ 0.5, 잔차 ≈ 100–200 Å(Kim & Seo)이고, PTW 캘리브레이션 후의 달성치도 같은
   오더(100–300 Å)다.** 차이는 정확도가 아니라 **일반화 범위**에 있다 — 현장 선형식은 마스크·사이트가 고정된
   조건에서만 성립하고, 물리 파라미터 모델은 임의 레이아웃으로 확장된다. sim/calibration은 후자를 목표로 하되
   블랭킷 rate의 네 보정을 먼저 구현해야 한다.

## 10. 구현 요청

→ [[../../agents/wafer-type/PROFILE.md]] "## 구현 요청 (2026-09-09, wafer-type Lv3-2)" 참조
(블랭킷 순간 rate 환산 함수, 전이 파라미터 레지스트리, 현장 선형 전이식, 하중균형 상한 검사).

## 11. 자기시험

→ [[../../agents/wafer-type/EXAMS.md]] Lv3-2 문항 참조.
