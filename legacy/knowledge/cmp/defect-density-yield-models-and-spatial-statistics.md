<!-- V2-SECTION: R2-slurry(연계) | 작성 2026-09-14 | defect-scientist Lv2-2 -->
# 결함 밀도 → 수율 폐형식 모델(Poisson·Murphy·Seeds·음이항/Stapper)과 결함 맵 공간 통계 — CMP 결함(스크래치·잔류입자·부식)에의 적용

> 에이전트: defect-scientist Lv2-2 | 작성일: 2026-09-14
> 선행(반드시 먼저 읽음):
> [[post-cmp-defect-classification-and-inspection]] (Lv1-1 — 결함 7종 조작적 경계·검사장비·**IRDS killer=½피치** 규칙. 이 노트 §3의 killer ratio는 그 §5 규칙을 수율식의 θ로 받는다),
> [[scratch-physics-source-signatures]] (Lv1-2 — 스크래치 발생원별 형상·궤적(디스크 그릿=긴 호). 이 노트 §4의 공간 signature 귀속에서 그 궤적 결론을 받는다),
> [[corrosion-pit-defect-morphology-density-inspection]] (Lv2-1 — 부식 결함 개수/wafer·**edge-ring 편중**(Choi r=145–148mm). 이 노트 §4-D의 비무작위성 검정 대상)
> 관련: [[lpc-scratch-density-tail-correlation]] (스크래치 개수-LPC 회귀 — 이 노트가 쓰는 D0(스크래치)의 상류), [[delta-scratch-damage-d99-oversize-particle-model]] (손상지수), [[metal-contamination-device-impact-irds-limits]]
>
> **스코프(결함→수율 통계만)**: (a) 결함밀도 D0 → 다이 수율 Y의 **폐형식**(Poisson `Y=exp(-A·D0)`, Murphy, Seeds, 음이항/Stapper `Y=(1+A·D0/α)^-α`)과 클러스터 파라미터 α, CMP 결함의 **killer ratio·critical area**, (b) 결함 맵의 **공간 통계**(join-count·공간무작위성 검정·클러스터링·edge 편중)와 CMP **원인 귀속**, (c) 1차 문헌 정량값(D0 /cm², α 범위, 스크래치 kill 확률). **제외**(형제/타 단원): 검사 장비·분류 체계(Lv1-1), **ML 자동분류**(Lv3-1 — Koo 2021의 DBSCAN 군집 자체는 재서술 않고 그 **공간무작위성 검정 통계**만 취함), 공정→결함 확률 역모델(Lv3-2).

## 0. 출처 (신규 3건 + 데이터셋 1건 + 선행노트 재조명; scope 상한 6건 내)

1. **[정본·전문 미확보(IEEE 유료·미러 사이트 이 세션 봉쇄)]** J. A. Cunningham, "The use and evaluation of yield models in integrated circuit manufacturing," *IEEE Trans. Semicond. Manuf.* 3(2), 60–71 (1990), DOI: 10.1109/66.53188 (Crossref 검증 완료; scope의 `before_year=1990` 규칙상 **1990=경계값이라 허용**, `tools/scope.py --check`로 확인). Poisson·Murphy·Seeds·음이항 4모델을 한 프레임에서 비교한 **정본 참조**. 원문 수치는 미확보라 인용하지 않고, **폐형식과 극한관계는 §6에서 python으로 재현**해 근거로 삼는다(EVIDENCE §"assert가 증거").
2. **[학회·전문 확보, arXiv OA]** Y. Feng, K. Ma, "Chiplet Actuary: A Quantitative Cost Model and Multi-Chiplet Architecture Exploration," *DAC '22* (ACM), DOI: 10.1145/3489517.3530428 (arXiv:2203.12268; `papers/feng2022-dac-chiplet-actuary-yield-cost-model.pdf`). 식(1) `Y=(1+DS/c)^-c`(음이항/Seeds 공용형, [1]=Cunningham 1990 인용)과 **현대노드 대표 파라미터** D=0.08–0.20(/cm² 해석)·클러스터 c=3–10을 준다(Fig 2). 이 D·c는 **대표 엔지니어링 값**(저자 표현 "realistic parameters")이지 통제 실측이 아니므로 값은 E5, 폐형식은 E2로 등급 분리.
3. **[1차·전문 확보, CC-BY]** J. Koo, S. Hwang, "A Unified Defect Pattern Analysis of Wafer Maps Using Density-Based Clustering," *IEEE Access* 9, 78873–78882 (2021), DOI: 10.1109/ACCESS.2021.3084221 (`papers/koo2021-ieee-access-wafer-defect-density-clustering.pdf`, Hanyang 리포지토리 CC-BY 사본). §II join-count(JC) 통계·**공간무작위성 검정(SRT)**·이항 이웃 null 모델·core-point 통계, §III WM811k(p≈0.14)·실 DRAM(p=0.18) 검정. §4의 공간 통계는 전부 이 논문.
4. **[데이터셋 출처, 전문 미확보]** M.-J. Wu, J.-S.-R. Jang, J.-L. Chen, "Wafer Map Failure Pattern Recognition and Similarity Ranking for Large-Scale Data Sets," *IEEE Trans. Semicond. Manuf.* 28(1), 1–12 (2015), DOI: 10.1109/TSM.2014.2364237 — WM811k(811,457맵/46,393로트, 9패턴 라벨)의 원 출처. Koo 2021이 인용한 데이터셋 사실만 재인용(**2차 인용**).

선행 노트에서 **수율 축으로 재조명**(원 수치는 그 노트가 E1으로 검증; 여기선 D0·θ로만 재사용):
[[post-cmp-defect-classification-and-inspection]] §5(IRDS 2024 YE: killer=½피치, 관리임계=¼피치; 스크래치 유발입자 POU 30/mL) · §2.1(Remsen 2006 스크래치 계수 길이≥50µm) / [[corrosion-pit-defect-morphology-density-inspection]] §1.1(Choi 2022 부식 0/12/363 ea·edge r145–148mm) / [[scratch-physics-source-signatures]] §7(Kwon 2013 디스크 그릿 스크래치=곡률 0.24–0.50m 긴 호).

## 1. 왜 결함밀도→수율 폐형식이 결함 과학의 종점인가

Lv1–Lv2-1에서 CMP 결함을 유형별로 **세고(개수/wafer)·재고(크기)·위치지었다**. 그러나 "스크래치가 wafer당 몇 개"라는 숫자가 공정 판단이 되려면 **다이 수율 Y**로 번역돼야 한다. 그 번역기가 결함밀도-수율 폐형식이다. 이 노트의 세 주장:

> **(1)** 같은 결함밀도 D0라도 모델(Poisson/Murphy/Seeds/음이항)에 따라 예측 Y가 크게 갈리며, 그 차이를 지배하는 단 하나의 물리량이 **클러스터 파라미터 α**다(=결함이 무작위인가 뭉치는가). **(2)** CMP 결함은 전부가 killer가 아니다 — D0 전체가 아니라 **killer ratio θ를 곱한 유효밀도 θ·D0**가 수율을 죽인다. **(3)** 결함 맵의 **공간 통계**(무작위 vs 국부)는 그 자체가 원인 진단 신호이고, α와 θ의 상류에 있다.

즉 α와 θ와 공간 패턴은 서로 다른 세 축이 아니라 **같은 결함맵의 세 얼굴**이다. 클러스터링이 강할수록 α는 작아지고(§2), 공간무작위성 검정은 H0를 기각하며(§4), 원인은 "무작위 입자"가 아니라 "국부 공정 이상"으로 좁혀진다.

## 2. 폐형식 수율 모델 4종과 클러스터 파라미터 α (a)

다이 하나에 걸리는 **평균 결함수** `λ = A·D0` (A=critical area 또는 다이 면적 cm², D0=결함밀도 /cm²)를 입력으로:

| 모델 | 폐형식 | 가정(결함 공간분포) | 음이항 특수화 |
|---|---|---|---|
| **Poisson** | `Y = exp(-λ)` | 완전 무작위(공간 독립) | α → ∞ |
| **Murphy** (삼각/감마 근사) | `Y = ((1-exp(-λ))/λ)²` | D0가 다이 간 변동 | (별도 함수, 극한 아님) |
| **Seeds** (지수) | `Y = 1/(1+λ)` | D0가 지수분포로 변동(강한 클러스터) | α = 1 |
| **음이항(Stapper)** | `Y = (1+λ/α)^(-α)` | D0가 감마분포로 변동, α=클러스터 파라미터 | 일반형 |

- **α의 의미**: 음이항은 "다이별 결함수 ~ 감마-Poisson 혼합"이며 α는 감마의 형상모수다. `α=(µ/σ)²`(평균²/분산)로, **α가 작을수록 결함밀도의 다이간 산포가 크다=강하게 뭉친다**. α→∞면 산포 0=Poisson, α=1이면 Seeds. Murphy는 음이항의 특수값이 아니라 삼각분포 근사에서 나온 별도 폐형식으로 Poisson과 Seeds **사이**에 놓인다(§6-A에서 4모델 대소관계 재현).
- **클러스터링은 수율을 "올린다"(같은 D0에서)**: 결함이 뭉치면 이미 죽은 다이에 결함이 겹쳐 붙어 "낭비"되므로, 무작위(Poisson)보다 살아남는 다이가 많다. 그래서 α 유한이면 항상 `Y_음이항 > Y_Poisson`(§6-A). **Poisson으로 수율을 예측하면 실제(클러스터)보다 비관적**이며, 이 편차가 결함맵 공간통계(§4)를 봐야 하는 통계적 이유다.
- **현대노드 대표값(Feng & Ma 2022, Fig 2)**: D0(/cm²)=3nm 0.20 / 5nm 0.11 / 7nm 0.09 / 14nm 0.08, 재배선층(RDL) 0.05, Si 인터포저 0.06; 클러스터 c(=α)=로직 10, RDL 3, SI 6. 신공정일수록 D0가 높다(0.08→0.20). 이 값들을 식 `Y=(1+D0·S/c)^-c`에 넣으면 14nm 1cm² 다이 92.3%, 800mm² 다이 53.8%로 현실적 범위가 나와 **D가 /mm²가 아니라 /cm² 단위임이 역으로 확인된다**(§6-B). ⚠ 이 D·c는 저자가 "realistic parameters"로 택한 대표값이지 단일 팹의 통제 실측이 아니므로 **값은 미검증(E5)**, 폐형식만 E2.

## 3. killer ratio θ와 critical area — CMP 결함은 전부 죽이지 않는다 (a)(c)

수율식의 D0는 "검출된 모든 결함"이 아니라 **소자를 죽이는 결함(killer)의 밀도**여야 한다. CMP 결함을 그대로 D0에 넣으면 수율을 과소추정한다.

- **killer ratio θ**: `λ_killer = A·D0·θ`, θ=검출결함 중 killer 분율. killer 절반이면 수율손실(1−Y)도 대략 절반으로 준다(λ 작을 때 1−Y≈λ; §6-B'). 즉 결함 **총량**을 줄이는 것과 **killer 분율**을 줄이는 것이 같은 효과를 낼 수 있고, 후자가 종종 값싸다.
- **critical area 관점의 killer 판정(IRDS, 선행 §5 E1)**: 입자·잔사는 크기가 **배선 피치의 ½를 초과할 때 killer**(브리지), 전도성 입자는 그보다 작아도 killer. 즉 θ는 **결함 크기분포의 꼬리**(임계크기 초과분)로 결정된다. M1 피치 38–45nm면 ½피치≈19–22.5nm가 임계이고, 관리임계는 그 절반(¼피치)이다.
- **CMP 결함별 kill 성격(선행 E1 종합, 스크래치 1개당 kill 확률은 상수가 아니다)**:
  - **스크래치**: Eusner 실측 평균 폭 ~100nm·깊이 ~4nm([[scratch-physics-source-signatures]] §4)는 Cu막(~1µm)의 0.5%라 **단독 killer가 되기 어렵고 개수통계로 관리**. 단 꼬리의 6µm급 하드 응집체가 낸 스크래치나 배선을 가로지르는 브리지는 killer → **kill 확률은 스크래치 폭·위치의 함수이지 "1개당 상수"가 아니다**.
  - **잔류입자**: Yu 2009은 특정 잔류입자가 M1–콘택트 간 Cu 필라멘트 브리지(단락)의 **직접 경로**임을 단면 TEM으로 확인 → 이 유형은 **kill 확률≈1(확정 killer)**([[post-cmp-defect-classification-and-inspection]] §2.3).
  - **부식(피트/노듈)**: Choi 2022의 edge-ring 부식은 PMOS 연결 W 플러그를 침식 → 국소 kill이지만 개수가 공정(가압·린스)으로 0~363 사이를 오간다([[corrosion-pit-defect-morphology-density-inspection]]).
  - ⚠ **미검증**: "스크래치 1개당 kill 확률"의 단일 실측값(예: p_kill=0.xx)을 준 15년내 1차 문헌은 이번 범위에서 확보하지 못했다 — kill 확률은 크기·위치 의존이라 IRDS 임계크기 규칙으로 **꼬리 분율 θ**를 쓰는 것이 문헌이 실제 관리하는 방식이다.

## 4. 결함 맵 공간 통계 — 무작위 vs 국부, 그리고 CMP 원인 귀속 (b)

α와 θ의 상류에는 "이 결함들이 공간적으로 뭉쳐 있는가"라는 질문이 있다. Koo & Hwang 2021은 이를 **가설검정**으로 못박는다(패턴을 ML로 분류하는 것은 Lv3-1 영역이므로 여기선 **검정 통계**만 취한다).

- **전역(무작위) vs 국부(체계) 결함(Koo 2021 §I)**: 전역 결함은 청정도·온도변동 등으로 wafer에 **무작위** 분포(공간 독립), 국부 결함은 소재취급·장비이상 등으로 **특정 공간패턴**(scratch·zone·ring·center·edge-ring 등)을 만든다. 수율 관점에서 전역은 α 큰(Poisson형), 국부는 α 작은(강클러스터) 결함이다.
- **join-count(JC) 통계와 공간무작위성 검정(SRT)(Koo §II-A, Moran 1948·Hansen 1997 기반)**: wafer bin map을 격자로 보고 인접 두 칩의 상태로 0-0/0-1/1-1 조인을 센다(1=불량). H0(공간 독립, 불량률 p) 아래 총조인 c에 대해 `E[c11]=c·p²`, `E[c00]=c(1-p)²`, `E[c01]=2c·p(1-p)`이고 합은 정확히 c다(§6-C). **관측 c11이 null 기대 c·p²를 크게 넘으면** 불량이 뭉쳐 있다는 뜻이라 H0를 기각 → "국부(체계) 결함"으로 판정. 스크래치형 국부대는 c11 분율이 p²의 여러 배로 뛴다(§6-C 시뮬: p=0.14에서 랜덤 0.019 vs 국부 0.13).
- **이웃 null 모델과 core-point 검정(Koo §II-B)**: 불량칩의 ε-이웃 내 불량수 `Y ~ Binomial(m, p)`, king-move면 이웃수 m=2ε(ε+1)로 원문은 적는다. core-point 확률 `Q=Pr(Y≥k)`, 임계 k는 **누적확률 C=0.90에서 `Pr(Y≥k) ≤ 1-C`를 만족하는 최소 k**로 정한다(§6-C). ⚠ **미검증(원문 표기 차이)**: 체비쇼프거리 ≤ε의 king 이웃수는 표준적으로 `4ε(ε+1)`(ε=1이면 8)인데 원문은 `2ε(ε+1)`(ε=1이면 4)로 적어 **정확히 2배 차이**다 — 원문이 무향 조인(i<j)을 절반으로 센 정의로 보이나 본문에 명시가 없어 원인 미상. §6-C의 core-point 검정은 이웃수 m을 인자로 두어 이 차이와 무관하게 성립함을 보인다.
- **CMP 원인 귀속(공간 signature → 소모품/공정)**: Koo가 인용하는 일반 귀속(scratch→식각, zone→소재취급, ring→증착)은 **CMP 전용이 아니다**. CMP 결함의 공간 signature는 선행 노트의 E1 실측에서 온다 —
  - **긴 호(arc) 스크래치** = 디스크 그릿 탈락(곡률 0.24–0.50m, [[scratch-physics-source-signatures]] §7): 웨이퍼맵에서 scratch 패턴, 국부 c11↑.
  - **edge-ring 편중** = 부식(가압·린스 불균일, Choi r=145–148mm, [[corrosion-pit-defect-morphology-density-inspection]]): 결함이 최외곽 3.9% 링에만 몰리면 국부밀도가 **25.6배**로 뛰어(§6-D) SRT가 H0를 강하게 기각 → "무작위 입자"가 아니라 "공정 불균일"로 진단. 이것이 §3의 θ·D0에서 D0(부식)이 공정변수의 함수인 이유와 직결된다.
  - **무작위 산발** = 슬러리 입자(LPC 꼬리, [[lpc-scratch-density-tail-correlation]]): 공간 독립 → Poisson형(α 큼).

## 5. 1차/대표 정량값 요약 (c)

| 양 | 값 | 단위 | 출처·등급 |
|---|---|---|---|
| D0 (현대노드 총결함밀도) | 3nm 0.20 / 5nm 0.11 / 7nm 0.09 / 14nm 0.08 | /cm² | Feng&Ma 2022 대표값 (E5) |
| D0 (RDL / Si 인터포저) | 0.05 / 0.06 | /cm² | Feng&Ma 2022 (E5) |
| 클러스터 파라미터 α(=c) | 로직 10, SI 6, RDL 3 | — | Feng&Ma 2022 (E5) |
| α 모델 극한 | Poisson α→∞, Seeds α=1 | — | 폐형식 재현 (E2, §6-A) |
| killer 임계크기 | ½피치(비전도) / ¼피치=관리임계 | 배선피치 | IRDS 2024 YE (E1, 선행 §5) |
| WM811k 불량률 p | ≈0.14(공개) / 0.18(실 DRAM) | — | Koo 2021 (E1) |
| edge-ring 면적분율 | 3.9%(r145–148mm) → 25.6배 국부밀도 | — | Choi 2022(E1)+본노트 계산 |

## 6. python verify — 폐형식·극한·공간통계 재현

```python verify
# ── (A) 4모델 폐형식과 음이항 극한 (Cunningham 1990 정본형 재현) ──
import math
Yp  = lambda l: math.exp(-l)                                   # Poisson
Ys  = lambda l: 1.0/(1.0+l)                                    # Seeds(지수)
Ym  = lambda l: ((1.0-math.exp(-l))/l)**2 if l>0 else 1.0      # Murphy(삼각근사)
Ynb = lambda l,a: (1.0+l/a)**(-a)                              # 음이항(Stapper)
for l in [0.3,0.5,1.0,2.0,5.0]:
    assert abs(Ynb(l,1e6)-Yp(l)) < 1e-4,  "α→∞이 Poisson으로 안 감"     # α→∞ ⇒ Poisson
    assert abs(Ynb(l,1.0)-Ys(l)) < 1e-12, "α=1이 Seeds와 불일치"        # α=1 ⇒ Seeds
    assert Yp(l) <= Ym(l) <= Ys(l)+1e-9,  "Murphy가 Poisson~Seeds 밖"   # Murphy는 사이
    assert Ynb(l,3) > Yp(l),               "클러스터링이 수율을 못 올림"  # 클러스터링 이득
print("(A) 4모델 대소관계: Poisson ≤ Murphy ≤ Seeds, 음이항 극한(α→∞=Poisson, α=1=Seeds) OK")
print(f"    예 λ=2: Poisson {Yp(2):.3f} < Murphy {Ym(2):.3f} < NB(α=3) {Ynb(2,3):.3f} < Seeds {Ys(2):.3f}")

# ── (B) Feng&Ma 2022 현대노드 D0·c → 다이 수율, /cm² 단위 확인 ──
nodes={"3nm":(0.20,10),"5nm":(0.11,10),"7nm":(0.09,10),"14nm":(0.08,10),"RDL":(0.05,3),"SI":(0.06,6)}
assert nodes["3nm"][0]>nodes["5nm"][0]>nodes["7nm"][0]>nodes["14nm"][0]   # 신공정일수록 D0↑
# D를 /cm², 면적을 cm²로 해석하면 현실적 수율(1cm²≈92%, 8cm²≈54%)이 나온다
Y14_1 =(1+0.08*1.0/10)**(-10);  assert 0.90<Y14_1<0.94
Y14_8 =(1+0.08*8.0/10)**(-10);  assert 0.50<Y14_8<0.57
Y3_8  =(1+0.20*8.0/10)**(-10);  assert 0.15<Y3_8<0.35
print(f"(B) 14nm D0=0.08/cm² c=10: 1cm² {Y14_1*100:.1f}% / 8cm² {Y14_8*100:.1f}%  (→ D는 /cm² 단위)")
# 같은 λ=D0·S에서 클러스터(c=10 유한) > Poisson
D,c,S=0.09,10,4.0
assert (1+D*S/c)**(-c) > math.exp(-D*S)
print(f"    7nm 4cm²: 음이항 {(1+D*S/c)**(-c)*100:.1f}% > Poisson {math.exp(-D*S)*100:.1f}% (클러스터 이득)")

# ── (B') killer ratio θ: 유효 λ = A·D0·θ (IRDS ½피치, 선행 §5 E1) ──
A_cm2, D0 = 1.0, 0.09
Y_all = math.exp(-A_cm2*D0*1.0)      # θ=1 (전부 killer로 가정)
Y_half= math.exp(-A_cm2*D0*0.5)      # θ=0.5 (killer 절반)
r = (1-Y_half)/(1-Y_all)
assert 0.45 < r < 0.55, "killer 절반이면 수율손실도 ~절반이어야(λ 작을 때)"
print(f"(B') killer 절반↓ ⇒ 수율손실 {(1-Y_all)*100:.2f}%→{(1-Y_half)*100:.2f}% (비 {r:.2f}) "
      f"— D0 총량이 아니라 θ·D0가 수율을 죽인다")

# ── (C) 공간통계: join-count null·이항 core-point·k선택 (Koo 2021 §II) ──
from scipy import stats
import numpy as np
# 원문 이웃수 표기 2ε(ε+1) vs 표준 체비쇼프 king 이웃수 4ε(ε+1) — 2배 차이(정직 표기)
for eps in [1,2,3]:
    std=4*eps*(eps+1); koo=2*eps*(eps+1)
    assert std==2*koo
print("(C1) king 이웃수: 표준 4ε(ε+1)=[8,24,48] vs 원문 2ε(ε+1)=[4,12,24] (2배차, 원인 미상·미검증)")
# core-point 확률 Q=Pr(Y≥k), Y~B(m,p); m을 인자로 둬 이웃수 정의와 무관하게 성립
p=0.14; m=4*2*(2+1)   # ε=2, 표준 이웃수 24
C=0.90
k=min(kk for kk in range(0,m+1) if (1-stats.binom.cdf(kk-1,m,p)) <= 1-C)
Q=1-stats.binom.cdf(k-1,m,p)
assert Q <= 1-C and (1-stats.binom.cdf(k-2,m,p)) > 1-C   # k는 규칙을 만족하는 최소값
print(f"(C2) p={p}, m={m} → 임계 k={k}, Q=Pr(Y≥{k})={Q:.4f} (≤{1-C:.2f}; C=0.90 규칙)")
# join-count null: E[c11]=c·p², E[c00]=c(1-p)², E[c01]=2c·p(1-p), 합=c
ct=1000.0; E11=ct*p**2; E00=ct*(1-p)**2; E01=2*ct*p*(1-p)
assert abs((E11+E00+E01)-ct) < 1e-9
print(f"(C3) join-count null 합 {E11+E00+E01:.0f}=c; E[c11]/c=p²={p**2:.4f} (관측이 이보다 크면 클러스터)")
# 국부(스크래치) 결함대는 c11 분율이 p²의 여러 배 — 20x20 격자 시뮬
def c11_frac(G):
    R,Cc=G.shape; n=s=0
    for i in range(R):
        for j in range(Cc):
            for di,dj in [(0,1),(1,0),(1,1),(1,-1)]:
                ii,jj=i+di,j+dj
                if 0<=ii<R and 0<=jj<Cc: n+=1; s+=G[i,j]*G[ii,jj]
    return s/n
rng=np.random.default_rng(0); R=20; pf=0.14
rand=(rng.random((R,R))<pf).astype(int)
clus=np.zeros((R,R),int); clus[8:12,2:18]=1               # 스크래치형 국부대
fr_r=c11_frac(rand); fr_c=c11_frac(clus)
assert abs(fr_r-pf**2) < 0.03 and fr_c > 5*pf**2
print(f"(C4) c11 분율: 랜덤 {fr_r:.4f}(≈p²={pf**2:.4f}) vs 국부(스크래치) {fr_c:.4f} → SRT가 H0 기각")

# ── (D) CMP 부식 edge-ring(Choi 2022, 선행 E1)의 국부밀도 증폭 ──
r_out,r_in,r_w=148.0,145.0,150.0
frac_edge=(r_out**2-r_in**2)/r_w**2
enh=1.0/frac_edge
assert 20<enh<30 and 0.03<frac_edge<0.05
print(f"(D) edge 링(145-148mm) 면적 {frac_edge:.3%} → 결함이 링에만 몰리면 국부밀도 {enh:.1f}배 "
      f"(공간 비무작위성 강함 → '무작위 입자' 아님, 공정 불균일로 귀속)")
print("\nALL BLOCKS PASS")
```

수계산 대조(Cunningham 1990 정본형 §6-A; Feng&Ma 2022 Fig 2 §6-B; Koo&Hwang 2021 §II의 §6-C; Choi 2022 §6-D): (A) 4모델 대소 Poisson≤Murphy≤음이항≤Seeds, 음이항 극한 α→∞=Poisson·α=1=Seeds; (B) 14nm 0.08/cm² 1cm² 다이 92.3%로 D가 /cm² 단위임 확인; (B') killer 절반이면 수율손실 8.61%→4.40%(~절반); (C) 이항 core-point 임계 k·join-count null(E[c11]=c·p²)·국부대 c11↑; (D) edge-ring 면적 3.9%→국부밀도 25.6배. 기계 실행은 §9 자가검사에서 `verify_claims.py`로 확인.

## 7. 근거 등급·충돌 판정 (EVIDENCE-RULES 서열)

| 주장 | 근거 | 등급 |
|---|---|---|
| Poisson/Murphy/Seeds/음이항 폐형식과 극한관계(α→∞=Poisson, α=1=Seeds) | 폐형식 유도 + python 재현(§6-A), Cunningham 1990 정본 | E2 |
| 클러스터링이 같은 D0에서 수율을 올린다 | 음이항>Poisson 재현(§6-A/B) | E2 |
| 현대노드 D0=0.08–0.20/cm², α(c)=3–10 | Feng&Ma 2022 대표 파라미터(통제실측 아님) | E5 |
| killer ratio θ·D0가 유효밀도, 임계=½피치 | IRDS 2024 YE(선행 §5, E1) + 산술(§6-B') | E1→E2 |
| 잔류입자 kill 확률≈1(브리지 직접경로) | Yu 2009 단면 TEM(선행 §2.3, E1) | E1 |
| join-count null·core-point 검정·SRT | Koo&Hwang 2021 §II + python 재현(§6-C) | E1/E2 |
| edge-ring 부식은 공간 비무작위(국부밀도 25.6배) | Choi 2022 edge 위치(선행, E1) + 계산(§6-D) | E1 |

**충돌 없음**(폐형식 모델들은 서로 배타가 아니라 α로 이어진 한 족(family)이고, 공간통계·killer ratio는 다른 축이라 상충하지 않는다). **Poisson과 음이항을 평균내지 않는다** — α로 분기한다(EVIDENCE §금지). 현대노드 D0/α 값(E5)은 폐형식(E2)과 **등급을 분리**해 표기했고, 값은 오더 참고로만 쓴다.

## 8. 한계·미확보·미검증

- **α의 통제 실측값을 준 15년내 1차 문헌은 미확보**. Feng&Ma의 c=3–10은 대표 엔지니어링 값(E5)이고 Cunningham 1990 정본은 IEEE 유료·미러 사이트 이 세션 봉쇄로 **전문 미확보** — 폐형식·극한은 python으로 재현했으나 "실제 팹의 α 분포"는 이 노트가 확정하지 못한다. Lv3에서 wafer probe bin map 기반 α 추출 1차 문헌(예: windowing 기법) 확보를 과제로 남긴다.
- **"스크래치 1개당 kill 확률"의 단일 실측값은 미검증** — kill 확률은 크기·위치 의존이라 상수가 아니며, 문헌은 IRDS 임계크기(½피치)로 **꼬리 분율 θ**를 관리한다(§3). CMP 결함 유형별 p_kill 표(스크래치/입자/부식 각각)는 SEM 리뷰-전기시험 상관 1차 데이터가 필요하다 — 미확보.
- **Koo 2021의 이웃수 표기 2ε(ε+1)는 표준 4ε(ε+1)의 절반**이라 원인 미상으로 §6-C에서 정직 표기했다. core-point 검정은 이웃수를 인자로 둬 이 차이와 무관하게 성립한다.
- **CMP 공간패턴→원인 귀속의 CMP 전용 1차 매핑은 부분적**. Koo의 일반 귀속(scratch→식각 등)은 CMP가 아니며, CMP signature(그릿 호·edge 링)는 선행 E1에서 가져왔다. "CMP center/ring 패턴 = 연마 비균일"의 직접 1차 실측은 이번 범위에서 확보 못 함(정성 수준).
- **구현 요청은 PROFILE.md**에 기재(θ·D0 유효밀도 + 4모델 폐형식 + JC/SRT 공간검정). sim/은 건드리지 않았다.

## 9. 자기시험
→ [[../../agents/defect-scientist/EXAMS.md]] Lv2-2 문항 참조.
