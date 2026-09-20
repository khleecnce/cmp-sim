<!-- V2-SECTION: R1-equipment | 공동: R5-wafer | 분배완료 2026-09-08 | 근거: endpoint, epd, friction, sampling, thermal | 정본: ARCHITECTURE-V2.md §3 -->
# CMP 계측 전략 — 인라인(통합) 계측 vs 오프라인 계측, 가상 계측(VM), 계측 샘플링 최적화 (Lv3-1 최신 리뷰)

> 에이전트: wafer-metrology Lv3-1 | 작성일: 2026-09-08
> 선행: [[wafer-metrology-thickness-methods]] (두께 계측 원리), [[uniformity-metrics-definitions-standards]] (WIWNU·49점 체계 — 본 노트는 지표 정의를 재탕하지 않음), [[wafer-surface-roughness-afm-scan-scale-dependence]], [[pattern-metrics-dishing-erosion-stepheight]]
> 관련: [[../equipment/cmp-tool-endpoint-thermal-slurry-delivery]] (in-situ EPD 하드웨어), [[../physics/friction-cof-monitoring-endpoint-detection]] (마찰 EPD — in-situ 신호의 물리), [[preston-luo-dornfeld-mrr]] (VM 물리 특징의 근거식), [[wafer-type-metrology-techniques-suitability]] (형제 노트 — NPW/PTW 기법 적합성, 침범하지 않음), [[wiwnu-pressure-velocity-wafer-scale]]

## 0. 목적과 경계

CMP에서 "무엇을 어떻게 측정할 것인가"는 세 층위로 나뉜다: (i) **in-situ 종점검출**(폴리싱 중, 웨이퍼 위에서 — 마찰·모터전류·와전류·광학), (ii) **인라인/통합 계측**(integrated metrology, IM — 툴 안 또는 툴 옆에서 폴리싱 직후 웨이퍼별 두께), (iii) **오프라인/독립 계측**(standalone — 로트 단위로 빼내어 정밀 측정). 여기에 (iv) **가상 계측**(virtual metrology, VM — 장비 센서(FDC) 데이터로 계측치를 *예측*)과 (v) **샘플링 최적화**(어느 로트·어느 웨이퍼·웨이퍼 위 어느 점을 잴 것인가)가 얹힌다. 이 노트는 (ii)~(v)의 트레이드오프와 정량 문헌값을 다룬다. (i)의 물리는 [[../physics/friction-cof-monitoring-endpoint-detection]]에 이미 있으므로 구분만 한다. 지표 정의(WIWNU·TTV·49점 체계)는 [[uniformity-metrics-definitions-standards]]에서 확정됐으므로 재론하지 않는다.

**한 줄 결론**: 계측은 "정보량 ↔ 사이클타임·비용"의 거래다. 문헌은 (a) 통합 계측은 *웨이퍼별 빠른 피드백*(dynamic-time W2W 루프), 오프라인 계측은 *정밀하지만 늦은 로트 피드백*(constant-time L2L 루프)이라는 역할 분담(AMD 특허 US6645780), (b) VM은 측정 안 한 웨이퍼의 값을 채워 R2R 제어의 관측 공백을 메우되 예측오차에 따른 가중치가 필요(IBM 특허 US9240360; Jebri et al. 2017), (c) 샘플링은 static → adaptive → dynamic으로 진화했고(Nduhura-Munga et al. 2013), 웨이퍼 내 측정점은 공간상관을 이용하면 **50점 → 7점(7배 축소)에서 프로파일 재구성 NMSE 0.96 %**(McLoone et al. 2018)까지 줄일 수 있음을 보여준다.

## 1. 인라인(통합) 계측 vs 오프라인 계측 — in-situ EPD와의 구분

### 1.1 세 층위의 정의 (1차: AMD 특허 US6645780, 원문 텍스트 확인)

AMD의 "Method and apparatus for combining integrated and offline metrology for process control"(US6645780, freepatentsonline 텍스트 확인)은 세 용어를 다음처럼 가른다:
- **integrated metrology data** = "inline metrology data that is acquired by a metrology tool integrated into a processing tool" — 툴 내장 계측기가 "during, or immediately following a manufacturing process" 취득하는 실시간/준실시간 데이터.
- **inline metrology data**(넓은 의미) = "metrology data acquired by a standalone metrology tool yielding data associated with a particular processing operation" — 즉 독립 계측기라도 공정 흐름 안에서 특정 공정 직후에 재면 인라인.
- **offline metrology data** = "metrology data that is not part of the production flow" — 전기 테스트·수율 등, 그리고 "offline metrology data results become available too late for performing such downstream modifications in a timely manner"라고 지연 문제를 명시.

특허의 핵심 주장은 두 피드백 루프의 분리다: 통합 계측 → **dynamic time process control = wafer-to-wafer feedback loop**(같은 로트 안에서 다음 웨이퍼 보정), 오프라인 계측(+통합 계측) → **constant time process control = lot-to-lot feedback**(다음 로트 보정). 즉 인라인의 가치는 정밀도가 아니라 **지연(latency)**이다. 어느 쪽 보정이 우선하는지는 실시예로 양쪽 다 열어 둠("process modifications dictated by analysis of integrated metrology data may take priority ... In an alternative embodiment ... offline ... may take priority").

### 1.2 in-situ EPD와의 구분

in-situ 종점검출(마찰·모터전류·와전류·광학)은 **절대 두께가 아니라 변화점(전이)**을 보며, 폴리싱을 *멈추는 시점*을 정하는 장치다([[../physics/friction-cof-monitoring-endpoint-detection]] §1, [[../equipment/cmp-tool-endpoint-thermal-slurry-delivery]]). 통합 계측은 폴리싱 *후* 절대 두께(또는 잔막)를 재서 *다음 웨이퍼 레시피*(시간·압력)를 고치는 장치다. 둘은 시간축(공정 중 vs 공정 후)·출력(전이 시각 vs 두께)·제어 대상(현재 웨이퍼 vs 다음 웨이퍼)이 다르므로 서로 대체하지 않는다 — `knowledge/components/metrology.yaml`의 `measurement_mode` enum(standalone_offline / integrated_metrology_iim / in_situ_endpoint)이 이 3분법이다.

### 1.3 트레이드오프 표 (정성 — 출처별)

| 축 | 통합(인라인) 계측 | 오프라인(독립) 계측 | 출처 |
|---|---|---|---|
| 지연 | 웨이퍼 직후, W2W 루프 가능 | 로트 완료 후, "too late" 우려 | US6645780 |
| 제어 루프 | dynamic-time(W2W) | constant-time(L2L, R2R) | US6645780 |
| 생산 흐름 침습성 | "generally less intrusive" | 웨이퍼를 흐름에서 빼냄(extracting ... from the manufacturing flow) | US6645780 |
| 측정 포인트 수·정밀도 | 문헌 정량값 **미확보**(벤더 자료·2차 기사만) | 고밀도 맵·정밀(예: 참조용) | 미검증 — §6 |
| 사이클타임 영향 | 작음(툴 내 처리) | "high cost, non-value added operation that impacts significantly on cycle time" | McLoone et al. 2018 초록 |
| 커버리지 | 매 웨이퍼 가능 | "Metrology ... covers only a small fraction of sampled wafers" | Kang et al. 2009 초록 |

Rao et al. (ISSM 2000, DOI: 10.1109/issm.2000.993700, "Run-to-run process control of oxide CMP using integrated metrology")는 산화막 CMP에서 통합 계측+폐루프 제어가 공정 제어와 처리량을 개선했다고 검색 스니펫이 요약하나, **원문·초록 모두 미확보(IEEE 유료, S2 초록 비공개)** — 제목·DOI만 Crossref로 실존 확인. 정량값은 인용하지 않는다.

## 2. 가상 계측(Virtual Metrology, VM)

### 2.1 정의와 위치 (Moyne & Iskandar 2017, CC-BY 원문 확인; Kang et al. 2009 초록; Dreyfus et al. 2021 초록)

- Moyne & Iskandar (2017, *Processes* 5(3):39, DOI: 10.3390/pr5030039, 원문 확인): "PdM and VM determine relationships between equipment data (trace or processed, e.g., through FD) and maintenance and metrology measurement data, respectively." 그리고 "Metrology measurement prediction using VM is being leveraged to reduce cycle times due to metrology delay and improve process capability." 단, 같은 논문이 "Isolated successes in PdM, VM, and predictive scheduling have been reported; however, challenges still exist"라고 못 박는다 — VM은 2017년 시점에 **보편 배치 기술이 아니었다**.
- Kang et al. (2009, *Expert Syst. Appl.*, DOI: 10.1016/j.eswa.2009.05.053, **초록만 확인**): "Virtual metrology (VM) ... enables to predict every wafer's metrology measurements based on production equipment data and preceding metrology results." — 입력이 장비 데이터 **+ 선행 계측치**라는 점이 중요(§2.3의 시계열 특징과 일치).
- Dreyfus et al. (2021, *Int. J. Prod. Res.*, DOI: 10.1080/00207543.2021.1976433, **초록만 확인**): 199편 체계적 리뷰. VM 구성요소를 "quality estimators and drift detectors"로, 응용을 "machine control and sampling decision systems"로 정리 — 즉 VM은 §3 샘플링 결정과 직결된다.

### 2.2 CMP VM의 공개 벤치마크 — PHM Society 2016 Data Challenge (Di, Jia & Lee 2017, 원문 확인)

CMP VM 논문 대부분이 사내 데이터라 성능 비교가 불가능한데, 유일한 공개 벤치마크가 PHM 2016 데이터 챌린지(CMP 툴 센서 → 웨이퍼별 평균 MRR 예측)다. 우승팀 논문 Di, Jia & Lee (2017, *Int. J. Prognostics Health Manag.* 8(2), DOI: 10.36001/ijphm.2017.v8i2.2641, CC-BY 원문 확인)에서:

- **데이터**: 훈련 MRR 레코드 1981건, 테스트·검증 각 424 웨이퍼; 레시피 3종(Stage×Chamber 조합 Cond1/2/3)별로 MRR 범위가 달라 **레시피별 개별 모델**. 평가지표 MSE. 참가 24팀.
- **입력 센서(Table 1)**: 소모품 사용량(backing film·pad·polishing table·dresser table·membrane·pressurized sheet), 압력(chamber, main outer/center/ripple/edge air bag, **retaining ring**), 슬러리 유량 A/B/C, 회전수(wafer/stage/head), dressing water 상태. 즉 [[preston-luo-dornfeld-mrr]]의 P·V 항과 패드/디스크 마모 상태가 그대로 특징이 된다. 모터전류·마찰 신호는 **이 데이터셋에 없다**(마찰 EPD 신호와의 결합은 미검증 영역).
- **특징 추출(Table 3, 125개)**: MRR 시차(time lag) 11개, 사용량-최근접이웃 MRR 10개, 챔버별 폴리싱 시간, 사용량·압력·유량의 평균/표준편차/AUC, 회전수 평균. 물리 근거: Preston ARR=K·P·V와 dressing rate ∝ K_D·U_D(Tso & Ho 2007 재인용)를 MRR=f(F_s,P,V,U_P,U_D)로 축약.
- **모델**: persistent(r_t=r_{t−1}), KNN, 선형회귀, tree bagging, SVR 5종을 Monte-Carlo CV 오차 e=mean(ε)+3·std(ε)로 가중평균 w=(1/e³)/Σ(1/e³).
- **성능(Table 5, 테스트 MSE)**: 통합 7.07 / persistent 8.23 / KNN 9.60 / SVR 7.44 / LR 7.32 / tree bagging 7.22 / Deep Belief Network(Wang, Gao & Yan 2017, DOI: 10.1016/j.cirp.2017.04.013) 7.29. 상위 5팀(Table 6): 7.07, 7.4, 7.4, 7.4, 7.5. §4 블록 1에서 재현·대조.
- **교훈**: (1) 딥러닝(DBN 7.29)이 잘 튜닝한 tree bagging(7.22)보다 **못했다** — 데이터 규모(≈2000건)에서 특징공학이 모델 복잡도를 이긴다. (2) persistent 모델(8.23)이 KNN(9.60)보다 나음 → MRR은 **시계열 성질이 강함**(패드 마모 드리프트, [[../materials/pad-wear-glazing-mrr-decay]]). (3) 저자 스스로 "trained models need updates periodically ... to adapt to the changing settings and recipes"라 하여 **모델 유지보수**가 미해결임을 인정.

후속 벤치마크 값: Zhang, Jiang & Wang (2021, ICCPR, DOI: 10.1145/3497623.3497679) Wide & Deep이 MSE 6.33(기존 최고 6.72 대비)이라고 검색 스니펫이 전하나 **초록·본문 미확인(ACM 403) — 미검증**. Li, Wu & Yu (2019, *J. Manuf. Sci. Eng.*, DOI: 10.1115/1.4042051) stacking(RF+GBT+ERT)은 초록에 수치 없음. 따라서 본 노트가 기계 검증한 값은 Di 2017 표뿐이다.

### 2.3 VM의 입력·모델·지표 — 일반화 (2차 정리)

- **입력 특징(FDC)**: 압력(존별 에어백·리테이닝링), 회전수, 슬러리 유량, 소모품 사용량·시간, 폴리싱 시간, 그리고 **선행 웨이퍼의 실측/예측치**(Kang 2009; Di 2017의 time lag). Breidung et al. (2025, *J. Intell. Manuf.*, DOI: 10.1007/s10845-025-02753-8, CC-BY이나 Springer/Fraunhofer 봇차단으로 **초록만 확인**): 고혼합·대량 팹 실데이터로 **불균일도와 공간분해 MRR**을 예측하며 SHAP 중요도에서 "polishing time and carrier rotation are among the most critical factors" — 즉 VM 출력이 평균 MRR을 넘어 **반경 프로파일/WIWNU**로 확장되는 흐름(정량 R²·RMSE는 본문 미확보로 **미검증**).
- **모델 계보**(Di 2017 서론 재인용): 선형 — PLS(Geladi & Kowalski 1986), locally-weighted PLS(Hirai & Kano 2015), lasso; 비선형 — NN, SVR, 준지도 SVR(Kang, Kim & Cho 2016), DBN(Wang 2017); 전략 — global vs local/Just-In-Time Learning(Jebri et al. 2016: 로컬 모델이 global 편향을 줄이나 유사 사례가 적으면 성능 저하).
- **성능 지표**: MSE/RMSE(절대 단위), R², 그리고 "relative RMSE = RMSE / σ(target)"(검색 결과 스니펫, CVD VM 논문 — 출처 확인 못 함, **출처 불명**). 실무적으로는 예측오차가 **실측 계측 반복성**보다 작아야 VM이 계측을 대체할 수 있다는 논리이나 CMP에서 이 비교를 수치로 보인 1차 문헌은 **미확보**.

### 2.4 APC(R2R) 연계 — VM 값을 어떻게 제어에 넣는가

- IBM 특허 US9240360 "Run-to-run control utilizing virtual metrology in semiconductor manufacturing"(2016 등록, freepatentsonline 요지 확인): 실측 오차(metrology error)와 VM 예측오차(prediction error)에 **각각 신뢰도 가중치**를 두어 다음 런 파라미터를 제어 — "assigning a first weight to the metrology error and a second weight to the prediction error, the first and second weights being indicative of a confidence in the metrology error and prediction error". 목적은 "maximizing a time between actual metrology measurements" — 즉 VM의 존재 이유가 **샘플링 간격 확대**임을 특허 청구항이 명시.
- Jebri, El Adel, Graton, Ouladsine & Pinaton (2017, *J. Phys.: Conf. Ser.* 783:012042, DOI: 10.1088/1742-6596/783/1/012042, IOP/HAL 봇차단으로 **초록만 확인**): "missing data ... derived from a measurement sampling strategies"를 수정 JITL VM으로 채워 R2R 루프에 넣고 STMicroelectronics Rousset CMP 데이터로 검증, "contribution of the estimated data is shown in product quality improvement" — 개선 **정량값은 초록에 없음**. 동일 저자 IFAC 2017(DOI: 10.1016/j.ifacol.2017.08.980)도 미확보.
- 원리(§4 블록 4 합성 검증): 로트당 1/5 웨이퍼만 실측하는 EWMA R2R에서 미측정 웨이퍼를 VM으로 채우면, VM 오차가 공정 드리프트보다 작을 때만 출력 분산이 준다 — VM 오차가 크면 오히려 해롭다. 그래서 US9240360의 가중치가 필요하다.

## 3. 계측 샘플링 최적화

### 3.1 로트/웨이퍼 샘플링: static → adaptive → dynamic (Nduhura-Munga et al. 2013, 원문 확인)

Nduhura-Munga, Rodriguez-Verjan, Dauzère-Pérès, Yugma, Vialletelle & Pinaton (2013, *IEEE Trans. Semicond. Manuf.* 26(2):188–195, DOI: 10.1109/TSM.2013.2256943, 원문 확인 — 대상은 CMP 한정이 아닌 팹 전체 계측(두께·스텝하이트 포함)):
- **정의**: static — 생산 시작 시 고정 규칙(예: 5로트에 1로트); adaptive — 시작 규칙을 공정 상태(SPC/APC)에 따라 조정; dynamic — 규칙 없이 **실시간**으로 계측 용량과 로트 정보에 따라 측정할 로트/웨이퍼를 선택.
- **핵심 개념 "material at risk"** = 한 생산 툴에서 두 계측 사이에 처리된 로트 수. "if the sampling plan is to control one lot every five lots, the objective is to limit the material at risk to not more than five."
- **정량 보고(산업 배치, 원문 인용)**: Motorola 테스트 비용 1/10(Shumaker et al. 2003); 자동 push-pull 샘플링으로 생산성 +2 %(Kwang & Chin 2008); TSMC 용량의존 샘플링으로 검사툴 가동률 +10 %(Song-Bor et al. 2003); Intel AMS 리스크 스코어로 excursion −30 %(Mouli et al. 2007); ST IPC 지표로 material at risk −30 % 이상(Nduhura Munga et al. 2011). 리뷰가 지적하듯 "actual performances are never published"인 경우가 많고 이 수치들은 각 사 자체 보고(**2차 인용**).
- **한계**: adaptive는 계측 작업량이 시간에 따라 요동, dynamic은 "predictive" 샘플링(아직 도착 안 한 로트 선점)이 미해결. Hyung (2008) — "When the process is very stable, dynamic sampling has no effects, whereas it is effective when data have large step disturbances."

### 3.2 웨이퍼 내 측정점(site) 최적화 — FSCA + 동적 공간 샘플링 (McLoone, Johnston & Susto 2018, 저자원고 확인)

McLoone, Johnston & Susto (2018, *IEEE Trans. Autom. Sci. Eng.* 15(4):1692–1703, DOI: 10.1109/TASE.2017.2786213, QUB 저장소 accepted manuscript 확인; 산업 사례는 Seagate 헤드 공정 — CMP가 아니라 **박막 두께 맵**이므로 방법론만 이식):
- **문제**: 후보 V=50 사이트, N=316 웨이퍼의 이력 데이터에서 최소 사이트 집합을 골라 나머지를 선형회귀(WMR)로 복원.
- **FSCA**(Forward Selection Component Analysis): 전체 사이트 분산을 가장 잘 설명하는 사이트를 순차 선택·deflation; 누적설명분산(CVE) ≥ τ(99 %)에서 멈춤. PCA 성분수 φ_PCA는 필요 사이트 수의 **하한**(φ_PCA ≤ k* ≤ rank(X)).
- **결과(Table I)**: PCA 5성분에서 CVE 99.07 %, FSCA 7사이트에서 99.02 % → "7-fold reduction in metrology (V/k*)". Table II(K=100 MC, 67 % 훈련): 7사이트 FSCA 재구성 NMSE 0.96 %(무작위 7사이트는 2.53 %). §4 블록 2에서 표 전체 재현.
- **동적 샘플링(SDS)**: 고정 축소 플랜은 "previously unseen spatially localized process behaviour may go undetected" → 미측정 사이트를 FSCA 사이트 주위로 군집화하고 매 웨이퍼 군집당 1개씩 돌아가며 측정. 지표 **MSSI**(최대 사이트 샘플링 간격; 정적 플랜은 ∞)와 **WOI** = (⌈V/V_m⌉−1)/MSSI ×100. Table IV: 국소 이상 검출률 정적 FSCA 43.8 % vs 동적 SDS-Corr 100 %(평균 검출까지 8.76 웨이퍼). 즉 **재구성 정확도(정적 FSCA 최상) ↔ 관측가능성(동적)**의 트레이드오프.
- **CMP 이식 시 유의**: CMP 두께 맵은 방위각 대칭성이 강해([[wiwnu-pressure-velocity-wafer-scale]]) φ_PCA가 더 작을 가능성이 크지만, 리테이닝링·엣지 특이점([[../equipment/cmp-retaining-ring-wear-edge-profile]])은 외곽 사이트를 빼면 재구성이 아니라 **외삽**이 되어 실패한다 — §4 블록 3의 합성 예. CMP 실데이터 FSCA 결과는 **문헌 미확보**.

### 3.3 측정점 축소가 검출력에 미치는 영향 — 통계 원리

측정점 n개 평균의 표준오차는 SE = σ/√n (독립 잡음 가정). 49점 → 9점이면 SE가 √(49/9)=2.33배 커진다. 그러나 이는 **잡음 항**뿐이고, 실제 손실은 (a) 외곽 사이트 반경이 줄어 엣지 롤오프/링 효과를 못 보는 **체계 편향**, (b) WIWNU의 range형 정의는 점 수가 줄면 **항상 과소추정**(max−min은 부분집합에서 작아짐)이라는 두 가지가 지배한다. §4 블록 3에서 합성 프로파일로 세 효과를 분리해 확인(합성 검증 — 문헌 상수 아님).

## 4. 정량 재현 (python verify)

### 블록 1 — Di, Jia & Lee 2017 PHM 2016 CMP VM 벤치마크 표 재현·정합성

```python verify
# Di, Jia & Lee (2017) IJPHM 8(2), DOI: 10.36001/ijphm.2017.v8i2.2641 — Table 4/5/6 상수(원문 확인)
test_mse = {"integrated": 7.07, "persistent": 8.23, "knn": 9.60, "svr": 7.44,
            "lr": 7.32, "treebag": 7.22, "dbn_wang2017": 7.29}      # Table 5 (testing)
top5 = [7.07, 7.4, 7.4, 7.4, 7.5]                                    # Table 6 (24팀 중 상위 5)
overall_cv = {"persistent": (8.78, 0.92), "knn": (11.21, 1.29), "svr": (6.23, 0.85),
              "lr": (7.76, 0.91), "treebag": (6.48, 0.68), "integrated": (6.18, 0.77)}  # Table 4 Overall (mean, std)
cond1_cv = {"persistent": (7.55, 1.27), "knn": (8.78, 5.43), "svr": (5.54, 1.30),
            "lr": (5.77, 1.10), "treebag": (5.65, 0.33)}            # Table 4 Cond1 (mean, std)

# (a) 통합 모델이 테스트/CV 모두 최저 MSE
assert min(test_mse, key=test_mse.get) == "integrated"
assert min(overall_cv, key=lambda k: overall_cv[k][0]) == "integrated"
# (b) 챌린지 1위 MSE == 논문 통합 모델 테스트 MSE
assert abs(top5[0] - test_mse["integrated"]) < 1e-9 and top5 == sorted(top5)
# (c) 최고 단일모델(tree bagging) 대비 개선폭 — 약 2 %에 불과(딥러닝 DBN은 tree bagging보다 나쁨)
best_single = min(v for k, v in test_mse.items() if k != "integrated")
impr = (best_single - test_mse["integrated"]) / best_single * 100
assert 1.5 < impr < 3.0, impr
assert test_mse["dbn_wang2017"] > test_mse["treebag"]
# (d) persistent(시계열) < KNN(사용량 이웃): MRR의 시계열 성질이 사용량 유사성보다 강함
assert test_mse["persistent"] < test_mse["knn"] and overall_cv["persistent"][0] < overall_cv["knn"][0]
# (e) 가중치 식 w = (1/e^3)/Σ(1/e^3), e = mean+3·std — 논문의 ε 벡터는 미공개이므로 Table 4 Cond1 (mean,std)를 대입한 근사
e = {k: m + 3 * s for k, (m, s) in cond1_cv.items()}
raw = {k: 1 / e[k] ** 3 for k in e}
w = {k: v / sum(raw.values()) for k, v in raw.items()}
assert abs(sum(w.values()) - 1) < 1e-12
assert max(w, key=w.get) == "treebag" and min(w, key=w.get) == "knn"   # std 최소 모델이 최대 가중치
assert w["treebag"] > 0.45 and w["knn"] < 0.02
print(f"Di2017: 통합 MSE {test_mse['integrated']} (1위), 최고단일 {best_single} 대비 {impr:.1f}% 개선; "
      f"Cond1 가중치 treebag {w['treebag']:.2f}, lr {w['lr']:.2f}, svr {w['svr']:.2f}, persist {w['persistent']:.2f}, knn {w['knn']:.3f}")
```

### 블록 2 — McLoone, Johnston & Susto 2018 FSCA 사이트 축소·동적 샘플링 표 재현

```python verify
# McLoone, Johnston & Susto (2018) IEEE TASE 15(4):1692–1703, DOI: 10.1109/TASE.2017.2786213 — Table I/II/III/IV 상수(저자원고 확인)
import math
V, N, tau = 50, 316, 99.0
pca_cve  = [41.05, 70.20, 88.35, 98.47, 99.07, 99.43, 99.64, 99.72, 99.79, 99.85]   # Table I(a) 누적 설명분산 %
fsca_cve = [38.81, 67.86, 86.28, 96.68, 97.87, 98.53, 99.02, 99.42, 99.60, 99.69]   # Table I(b)
phi_pca = next(k for k, v in enumerate(pca_cve, 1) if v >= tau)
k_star  = next(k for k, v in enumerate(fsca_cve, 1) if v >= tau)
assert phi_pca == 5 and k_star == 7, (phi_pca, k_star)          # 본문: φ_PCA=5, k*=7
assert phi_pca <= k_star                                         # 하한 관계 φ_PCA ≤ k*
assert all(p >= f for p, f in zip(pca_cve, fsca_cve))            # PCA가 각 k에서 FSCA 이상 설명(최적성)
assert round(V / k_star) == 7                                    # "7-fold reduction"

# Table II: 재구성 NMSE % (K=100 MC) — Vm: (Random, FSCA, RDS, CDS, SDS-Corr, SDS-NMSE)
t2 = {2: (48.87, 36.54, 48.68, 43.79, 46.64, 46.64), 3: (26.80, 18.35, 27.43, 21.35, 24.05, 23.58),
      4: (11.61, 3.51, 11.76, 8.40, 8.19, 8.29),     5: (6.66, 2.45, 6.26, 2.81, 4.00, 3.93),
      6: (3.60, 1.64, 3.73, 1.93, 2.35, 2.48),       7: (2.53, 0.96, 2.64, 1.29, 1.43, 1.44),
      8: (1.65, 0.70, 1.79, 0.80, 1.01, 1.06),       9: (1.25, 0.51, 1.35, 0.57, 0.74, 0.67)}
for vm, (rnd, fsca, rds, cds, sdc, sdn) in t2.items():
    assert fsca < rnd                       # FSCA 선택이 무작위 선택보다 항상 우수
    assert fsca <= cds <= max(sdc, sdn) <= rds + 1e-9 or fsca <= min(sdc, sdn) <= rds  # 정적FSCA ≤ 동적 ≤ RDS
    assert fsca < sdc < rds and fsca < sdn < rds
# k*=7에서 검증 NMSE 0.96 % ↔ 훈련 CVE 99.02 %: 100−NMSE 와 CVE 차이 < 0.5 %p
assert abs((100 - t2[7][1]) - fsca_cve[6]) < 0.5

# Table III: WOI % — CDS 열은 "Vm−1 고정 + 1개 순환"이므로 MSSI_CDS = V − Vm 로 닫힌 형태 재현
t3_cds = {2: 50.0, 3: 34.0, 4: 26.1, 5: 20.0, 6: 18.2, 7: 16.3, 8: 14.3, 9: 12.2}
for vm, woi_lit in t3_cds.items():
    mssi_min = math.ceil(V / vm) - 1                 # 이론 최소 MSSI(균형 군집)
    mssi_cds = V - vm                                # 순환 사이트 V−(Vm−1)개 → 간격 V−Vm
    woi = mssi_min / mssi_cds * 100
    assert abs(woi - woi_lit) <= 0.1, (vm, woi, woi_lit)   # 8행 전부 ±0.1 %p
# RDS는 모든 사이트를 균등 순환 → WOI 100 (Table III RDS 열 전부 100)
# Table IV: 국소 이상 검출률 %와 평균 검출 웨이퍼 수
t4 = {"Random": (29.7, 1.12), "FSCA": (43.8, 1.14), "RDS": (100, 7.32), "CDS": (99.8, 24.41),
      "SDS-Corr": (100, 8.76), "SDS-NMSE": (100, 11.09)}
assert t4["FSCA"][0] < 50 and t4["SDS-Corr"][0] == 100          # 정적 플랜은 절반 이상 놓침
assert t4["RDS"][1] < t4["SDS-Corr"][1] < t4["SDS-NMSE"][1] < t4["CDS"][1]   # 검출 지연 순서 = WOI 순서
print(f"McLoone2018: φ_PCA={phi_pca}, k*={k_star} (V={V}, {V/k_star:.1f}배 축소), FSCA-7 NMSE {t2[7][1]}% vs Random {t2[7][0]}%; "
      f"CDS WOI 8행 닫힌형 재현 OK; 정적 FSCA 검출률 {t4['FSCA'][0]}% vs SDS-Corr {t4['SDS-Corr'][0]}%")
```

### 블록 3 — 측정점 축소의 세 효과 분리 (합성 검증 — 문헌 상수 아님)

```python verify
# 합성 검증(문헌값 아님): 49점 vs 9점에서 (a) 잡음 SE ∝ 1/√n, (b) range형 WIWNU 과소추정, (c) 엣지 외삽 편향
import numpy as np
rng = np.random.default_rng(7)
R = 150.0                                                 # mm, 300 mm 웨이퍼
# 49점: 중심1 + 링 3개(8/16/24점) — US6922603B1 체계([[uniformity-metrics-definitions-standards]])
def ring(n, r): return [(r, 2*np.pi*i/n) for i in range(n)]
sites49 = [(0.0, 0.0)] + ring(8, 48.0) + ring(16, 96.0) + ring(24, 144.0)
sites9  = [(0.0, 0.0)] + ring(4, 70.0) + ring(4, 120.0)   # 흔한 9점형(중심+4+4), 최외곽 120 mm
def profile(r, edge=0.0):
    # 잔막 두께 nm: 엣지로 갈수록 얇아지는 완만한 2차 + 엣지 3 mm 급격 롤오프(리테이닝링 특이점 모사)
    return 1000.0 - 8.0 * (r / R) ** 2 - edge * np.exp(-(R - r) / 3.0)
def measure(sites, edge, sigma):
    r = np.array([s[0] for s in sites]); return profile(r, edge) + rng.normal(0, sigma, len(r))

# (a) 잡음만(edge=0, sigma=1 nm): 평균의 SE 비율 ≈ sqrt(49/9)=2.33
m49 = [measure(sites49, 0, 1.0).mean() for _ in range(4000)]
m9  = [measure(sites9,  0, 1.0).mean() for _ in range(4000)]
ratio = np.std(m9) / np.std(m49)
assert abs(ratio - np.sqrt(49 / 9)) / np.sqrt(49 / 9) < 0.10, ratio

# (b) range형 WIWNU(half-range %)는 부분집합에서 항상 ≤ 전체: 잡음 없이 결정적으로 확인
t49 = measure(sites49, 0, 0.0); t9 = measure(sites9, 0, 0.0)
hr = lambda t: (t.max() - t.min()) / (2 * t.mean()) * 100
assert hr(t9) < hr(t49)
under_b = (1 - hr(t9) / hr(t49)) * 100

# (c) 엣지 롤오프 40 nm(3 mm 스케일): 9점 최외곽 120 mm는 롤오프를 전혀 못 보고, 49점 144 mm도 일부만 봄
t49e = measure(sites49, 40.0, 0.0); t9e = measure(sites9, 40.0, 0.0)
r_dense = np.linspace(0, 147, 2000); true_hr = hr(profile(r_dense, 40.0))
assert abs(hr(t9e) - hr(t9)) < 1e-3            # 9점: 롤오프 유무에 사실상 무감(<0.001 %p)
assert hr(t49e) > hr(t9e)                      # 49점: 감지는 하되
assert hr(t49e) < true_hr                      # 147 mm(3 mm 엣지제외)까지 잰 참값보다는 작음
print(f"SE비 {ratio:.2f} (이론 2.33); 9점 half-range 과소추정 {under_b:.0f}%; "
      f"엣지 롤오프 40 nm: 참 HR {true_hr:.2f}% / 49점 {hr(t49e):.2f}% / 9점 {hr(t9e):.2f}%")
```

### 블록 4 — VM으로 미측정 웨이퍼를 채운 EWMA R2R (합성 검증 — US9240360 가중치 논리의 재현)

```python verify
# 합성 검증(문헌값 아님): 제거량 = k_t·time, k_t 랜덤워크 드리프트. 로트 5매 중 1매 실측(static 1/5) vs VM 보강 vs 전수.
import numpy as np
def run(sigma_vm, sample_every=5, n=20000, lam=0.3, sigma_k=0.004, sigma_met=1.0, seed=3):
    rng = np.random.default_rng(seed); target = 300.0; k = 3.0; k_hat = 3.0; out = []
    for i in range(n):
        k += rng.normal(0, sigma_k)                       # 패드 마모형 드리프트
        t = target / k_hat                                # 제어: 추정 k로 시간 결정
        removed = k * t; out.append(removed)
        if i % sample_every == 0:                         # 실측 웨이퍼
            y = removed + rng.normal(0, sigma_met)
        elif sigma_vm is not None:                        # VM 웨이퍼(예측오차 sigma_vm)
            y = removed + rng.normal(0, sigma_vm)
        else:
            continue                                      # 미측정 — 갱신 없음
        k_hat = lam * (y / t) + (1 - lam) * k_hat         # EWMA 갱신
    return np.std(np.array(out[2000:]) - target)
s_full  = run(sigma_vm=None, sample_every=1)   # 전수 실측(상한 성능)
s_15    = run(sigma_vm=None)                   # 1/5 실측만
s_vmgood = run(sigma_vm=2.0)                   # VM 오차 2 nm(실측의 2배)
s_vmbad  = run(sigma_vm=30.0)                  # VM 오차 30 nm(드리프트보다 훨씬 큼)
assert s_full < s_vmgood < s_15, (s_full, s_vmgood, s_15)     # 좋은 VM은 샘플링 공백을 메움
assert s_vmbad > s_15, (s_vmbad, s_15)                        # 나쁜 VM을 실측과 같은 가중으로 넣으면 해로움 → US9240360의 신뢰도 가중 필요
print(f"출력 σ(nm): 전수 {s_full:.2f} < VM(σ2) {s_vmgood:.2f} < 1/5실측 {s_15:.2f} < VM(σ30) {s_vmbad:.2f}")
```

## 5. FabSim 적용 요약 (구현 요청은 PROFILE.md "## 구현 요청"에 기재)

1. **계측 모드 3분법을 스키마에**: `measurement_mode` ∈ {in_situ_endpoint, integrated_inline, standalone_offline} + `latency_class` ∈ {W2W, L2L} (US6645780). 엔진 출력에 "이 값이 어느 층위에서 왔는가"를 붙여야 VM/실측 혼합 시 추적이 된다.
2. **샘플링 플랜 객체**: 로트 샘플링(static 1/n, material_at_risk 계산 — Nduhura-Munga 2013) + 사이트 플랜(49/9/FSCA-선택 목록 + MSSI/WOI — McLoone 2018). 시뮬레이터가 "전 프로파일"을 알고 있으므로 **샘플링 손실을 정량화하는 실험**이 가능하다(블록 3 방식).
3. **VM 프로토타입**: 시뮬레이터의 P·V·패드 마모·시간을 특징으로 Di 2017형 가중 앙상블(persistent+LR+tree bagging)을 만들고, 합성 데이터에서 MSE·R²를 보고 — 실데이터 문헌값(Di 2017 MSE 7.07, 단위 nm/min 추정·원문 미명시)은 **레시피·툴 종속이라 직접 비교 불가**, 상대 순위(persistent<KNN, 앙상블<단일)만 재현 목표.

## 6. 미확보·한계 (정직성 기록)

- **원문 미확보**: Rao et al. 2000 ISSM(통합 계측 R2R 원조 — 제목·DOI만); Jebri 2017 JPCS/IFAC(HAL·IOP 봇차단, 초록만); Kang 2009 ESWA(초록만); Dreyfus 2021 IJPR(초록만); Breidung 2025 JIM(CC-BY이나 Springer 303→IdP·Fraunhofer Anubis 차단, 초록만); Wang 2017 CIRP(DOI 실존, 본문은 Di 2017 재인용값 7.29만); Zhang 2021 Wide&Deep(ACM 403, 검색 스니펫 6.33 **미검증**); Li 2019 JMSE(초록에 수치 없음); Deivendran et al. 2024 JIM(DOI: 10.1007/s10845-024-02335-0, 제목만).
- **정량 공백**: (a) 통합 계측기의 측정점 수·정밀도·처리량을 오프라인과 나란히 비교한 1차 논문(벤더 백서·semiengineering 기사는 403으로 본문 확인 못 함); (b) CMP 실데이터에서 FSCA/PCA 성분수(McLoone 2018은 헤드 공정); (c) CMP VM의 R²/RMSE를 계측 반복성과 비교한 값; (d) Di 2017 MSE의 물리 단위(논문에 명시 없음 — 데이터셋 MRR 단위 미상).
- **블록 3·4는 합성 검증**이다 — 원리(SE 스케일링, range 과소추정, VM 가중 필요성)만 보이며 문헌 상수를 대조한 것이 아니다.
- Nduhura-Munga 2013의 산업 성과 수치는 리뷰가 재인용한 각 사 자체 보고(**2차 인용**)이며 검증 조건이 공개되지 않았다.

## 7. 출처

| # | 출처 | 확인 수준 |
|---|---|---|
| 1 | Y. Di, X. Jia, J. Lee, "Enhanced Virtual Metrology on Chemical Mechanical Planarization Process using an Integrated Model and Data-Driven Approach," *Int. J. Progn. Health Manag.* 8(2), 2017. DOI: 10.36001/ijphm.2017.v8i2.2641 | 원문(CC-BY PDF, papers/di2017-ijphm-cmp-vm.pdf) |
| 2 | S. McLoone, A. Johnston, G.A. Susto, "A Methodology for Efficient Dynamic Spatial Sampling and Reconstruction of Wafer Profiles," *IEEE Trans. Autom. Sci. Eng.* 15(4):1692–1703, 2018. DOI: 10.1109/TASE.2017.2786213 | 저자원고(QUB 저장소, papers/susto2018-tase-spatial-sampling-wafer.pdf) |
| 3 | J. Nduhura-Munga et al., "A Literature Review on Sampling Techniques in Semiconductor Manufacturing," *IEEE Trans. Semicond. Manuf.* 26(2):188–195, 2013. DOI: 10.1109/TSM.2013.2256943 | 원문(저장소 PDF, papers/nduhura-munga2013-tsm-sampling-review.pdf) |
| 4 | J. Moyne, J. Iskandar, "Big Data Analytics for Smart Manufacturing: Case Studies in Semiconductor Manufacturing," *Processes* 5(3):39, 2017. DOI: 10.3390/pr5030039 | 원문(CC-BY, papers/moyne2017-processes-bigdata.pdf) |
| 5 | AMD, "Method and apparatus for combining integrated and offline metrology for process control," US6645780 | 특허 전문(freepatentsonline 텍스트) |
| 6 | IBM, "Run-to-run control utilizing virtual metrology in semiconductor manufacturing," US9240360 (2016) | 특허 요지·청구항(freepatentsonline) |
| 7 | M.A. Jebri, E.M. El Adel, G. Graton, M. Ouladsine, J. Pinaton, *J. Phys.: Conf. Ser.* 783:012042, 2017. DOI: 10.1088/1742-6596/783/1/012042 | 초록만 |
| 8 | P. Kang, H. Lee, S. Cho, D. Kim, "A virtual metrology system for semiconductor manufacturing," *Expert Syst. Appl.*, 2009. DOI: 10.1016/j.eswa.2009.05.053 | 초록만 |
| 9 | P. Dreyfus, F. Psarommatis, G. May, D. Kiritsis, *Int. J. Prod. Res.*, 2021. DOI: 10.1080/00207543.2021.1976433 | 초록만 |
| 10 | M. Breidung et al., "Process data-driven machine learning for non-uniformity prediction and virtual metrology in chemical mechanical planarization," *J. Intell. Manuf.*, 2025. DOI: 10.1007/s10845-025-02753-8 | 초록만 |
| 11 | P. Wang, R.X. Gao, R. Yan, *CIRP Annals* 66, 2017. DOI: 10.1016/j.cirp.2017.04.013 | DOI 실존, 수치는 [1] 재인용 |
| 12 | Zhang, Jiang, Wang, ICCPR 2021. DOI: 10.1145/3497623.3497679 · Li, Wu, Yu, *J. Manuf. Sci. Eng.*, 2019. DOI: 10.1115/1.4042051 · Rao et al., ISSM 2000. DOI: 10.1109/issm.2000.993700 | 제목·DOI만(미검증) |
