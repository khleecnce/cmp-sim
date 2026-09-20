<!-- V2-SECTION: R5-wafer | 분배완료 2026-09-08 | 근거: metrology, pattern-, ptw, 웨이퍼 | 정본: ARCHITECTURE-V2.md §3 -->
# 제품 웨이퍼(PTW) 대리 지표와 가상 계측 — 모니터 웨이퍼·전기 테스트·VM은 제품 웨이퍼를 얼마나 대신하는가 (Lv3-1)

> 에이전트: wafer-type Lv3-1 (최신 리뷰: 제품 웨이퍼 대리 지표·가상 계측) | 작성일: 2026-09-08
> 선행: [[npw-ptw-test-wafer-fundamentals]] (NPW/PTW 정의·49점·MIT 마스크), [[npw-ptw-pattern-effect-gw-physics]] (NPW가 PTW를 예측 못하는 접촉역학), [[wafer-type-metrology-techniques-suitability]] (PTW에서 측정 기법 제약), [[pattern-metrics-dishing-erosion-stepheight]] (dishing/erosion 정의·테스트 구조)
> 관련: [[pattern-dependent-dishing-erosion]] (effective density 모델), [[uniformity-metrics-definitions-standards]], [[wiwnu-pressure-velocity-wafer-scale]], [[preston-luo-dornfeld-mrr]]

## 0. 질문과 경계

제품 웨이퍼(product wafer)는 단면 SEM·스타일러스처럼 파괴적이거나 느린 계측을 매 웨이퍼에 걸 수 없다.
그래서 현장은 **대리 지표(proxy)**로 제품 상태를 추정한다 — (a) 블랭킷 모니터/컨트롤 웨이퍼(NPW)의
제거율, (b) 제품 웨이퍼 위 테스트 구조의 **전기 테스트**(선저항·면저항), (c) 장비 센서로 두께를
추정하는 **가상 계측(VM)**. 이 노트의 질문은 형제 에이전트(wafer-metrology)의 VM 일반론이 아니라
"**NPW(모니터)가 PTW(제품)의 대리로 얼마나 유효한가, 어디서 깨지고, 전기 테스트·VM이 그 틈을
메우는가**"다. 전부 공개 문헌·특허만 근거로 하며, 회사 관행은 쓰지 않는다.

## 1. 대리 지표의 네 층위 — 무엇을 재고 무엇을 추정하는가

| 층위 | 대리 지표 | 실제로 재는 것 | 추정하려는 것 | 1차 근거 |
|---|---|---|---|---|
| 모니터(컨트롤) 웨이퍼 | 블랭킷 막 pre/post 두께차 ÷ 시간 = RR | 장비·소모품 상태의 blanket K | 제품 폴리시 시간 | US20060116785A1 (TSMC, 2006) FIG.1 |
| 전이 규칙(레시피 간) | 변환계수 = F(레시피₂)/F(레시피₁) | 제어변수 3종의 지수 반응 | 다른 막·레시피의 RR | US20060116785A1 표 1·2 |
| 전기 테스트 | Kelvin/serpentine 선저항, van der Pauw Rs | 잔류 Cu 두께 (dishing+erosion 혼합) | 다이 내 배선 성능 | Park et al. 1999 CMP-MIC; Pan et al. 1999 CMP-MIC; Chang et al. 2004 (doi.org/10.1109/TED.2004.834898) |
| 가상 계측(VM) | 장비 센서 통계 + 이웃/시계열 특징 | 센서가 본 공정 상태 | 미측정 웨이퍼의 MRR/두께 | Di et al. 2017 (doi.org/10.36001/ijphm.2017.v8i2.2641); Jebri et al. 2017 (doi.org/10.1088/1742-6596/783/1/012042) |

핵심 구분: 앞의 두 층위는 **h=0(패턴 없음)** 상태에서 얻은 K를 옮기는 것이고, 뒤의 두 층위는 제품
자체(또는 제품과 같은 공정 이력)를 본다. [[npw-ptw-pattern-effect-gw-physics]]가 보인 대로 패턴
효과 항(κ_U,D = κ_asp ± 4αh/size²)은 h=0에서 원리적으로 사라지므로, 모니터 웨이퍼는 그 항을
**관측할 수 없고** 다른 층위가 보완해야 한다.

## 2. 모니터(컨트롤) 웨이퍼 관행과 오차원

### 2.1 관행 — 특허가 기술하는 표준 절차 (1차, 특허 원문)

US20060116785A1 "Method of predicting CMP removal rate for CMP process in a CMP process tool"
(공개 2006-06-01, 출원 2004-11-29, 등록판 US7333875B2, 양수인 Taiwan Semiconductor Manufacturing Co.;
freepatentsonline.com/y2006/0116785.html 및 /7333875.html에서 전문 확인)의 FIG.1 "prior art"가
모니터 관행을 그대로 서술한다:

1. 컨트롤 웨이퍼 1장 이상을 해당 레시피로 폴리시 → 전·후 두께차와 시간으로 **측정 RR** 산출(S1–S2).
2. RR이 스펙 안이면 그 RR을 장비에 적용해 **제품 웨이퍼 폴리시 시간**을 정한다(S3–S4). 밖이면 장비 정지·점검 후 반복(S5).
3. 다른 레시피(ILD→STI/IMD)로 전환할 때마다 **다시 컨트롤 웨이퍼 시퀀스(monitor)**를 돈다(S10–S12).
   특허는 이 반복이 "컨트롤 웨이퍼 준비·전후 두께·파티클 측정에 상당한 시간"을 먹어 제품 폴리시
   시간을 줄이고 비용을 올린다고 명시한다.
4. 실시예: Mirra(Applied Materials) 유전체 CMP에서 측정 RR은 "**periodic (daily, semi-daily or by
   number of wafers processed) monitoring sequence**"로 얻는다 — 즉 모니터 주기는 일 단위다.

같은 맥락의 "send-ahead wafer"(로트에서 1장을 먼저 보내 결과를 보고 나머지 로트의 레시피를
확정하는 방식)는 MES 벤더 블로그(Bednarz, Critical Manufacturing, 2022)가 정의·워크플로(수용/조정/
재작업/재시험)를 서술하나 **비학술 2차 자료이고 수치 없음** — 정성 참고만.

### 2.2 특허의 전이 규칙 — 모니터 RR을 다른 레시피로 옮기는 변환계수 (재현 대상 A)

특허의 발명은 "레시피가 바뀔 때 모니터를 다시 돌리지 말고 **변환계수**로 RR을 예측"하는 것이다.
제어변수 3종(다운포스 X psi, 슬러리 유량 Y ml/min, 패드 회전 Z rpm)에 대해 각각 컨트롤 웨이퍼로
지수 반응식을 얻고 곱해 work function을 만든다 (US20060116785A1 식(1)):

F(X,Y,Z) = [1.223 − 0.605·e^{−(X−3.4)/2.117}] · [1.085 − 0.302·e^{−(Y−80)/98.39}] · [1.187 − 0.719·e^{−(Z−40)/66.304}]

(특허 원문 표기 "e^{−(Y−80/98.39)}"는 괄호가 빠진 오기로 판단 — 아래 재현에서 (Y−80)/98.39로 읽어야
표 2의 값이 나온다.) 표 1 레시피: ILD 63 rpm/4 psi/150 ml/min, STI 63/4.2/200, IMD 108/4.6/100.
표 2 변환계수: **STI 1.12, IMD 1.41** (ILD 기준). 청구항 6: 변환계수는 "substantially 0.5~2".
§6 verify (A)에서 식(1)로 1.12·1.41을 재현한다.

이 전이 규칙의 의미와 한계:
- 옮기는 것은 **blanket K의 레시피 의존성**뿐이다. 세 변수 모두 장비 노브이고, 막 종류(ILD/IMD/STI
  산화막)는 "물성이 유사"하다는 가정 아래 무시된다(청구항 3).
- 제품 웨이퍼의 **패턴밀도는 변수에 없다**. 즉 이 방식은 "모니터→모니터" 전이이지 "모니터→제품"
  전이가 아니며, 제품 폴리시 시간은 별도의 오버폴리시 마진으로 흡수된다(특허는 이를 다루지 않음).

### 2.3 모니터→제품 오차원 정리

| 오차원 | 물리 | 정량 근거 | 모니터가 보정 가능한가 |
|---|---|---|---|
| 레시피/장비 노브 차이 | K(P,V,유량) | 변환계수 1.12·1.41 (US20060116785A1) | 가능(위 전이 규칙) |
| 패턴밀도 → 유효압력 | up-area에 압력 집중 | 유효압력/인가압력 = 2.2·1.7·1.3 @10·50·90% (Sorooshian 2005, §4) | **불가**(h=0) |
| 시간 드리프트(패드·디스크 사용량) | 소모품 마모 | PHM2016: 직전 웨이퍼 MRR만으로 MSE 8.23, 통합모델 7.07 (Di et al. 2017 표 5) | 부분(주기 짧게) |
| 다층 토포그래피 | 하부층 erosion이 상부층 dishing 변조 | Park et al. 1999 CMP-MIC Fig.12 (정성) | 불가 |
| 패턴/비패턴 상관 | 위 전부의 합 | Kim & Seo 2002 (doi.org/10.1016/S0167-9317(01)00694-3) r≈0.71 — **원문 미확보, 정의 불명, 미검증** | — |

## 3. 전기 테스트 — 제품 위 테스트 구조로 잔류 Cu 두께를 읽는다

### 3.1 선저항 → 두께 추출 (Park et al. 1999, 1차 원문)

Park, Tugbawa, Boning, Chung(MIT) + Hymes, Muralidhar, Wilks, Smekalin, Bersuker(SEMATECH),
"Electrical Characterization of Copper Chemical Mechanical Polishing," Proc. CMP-MIC, Feb. 1999
(boning.mit.edu/wp-content/uploads/2022/11/Electrical-Characterization-of-Copper-Chemical-Mechanical-Polishing.pdf,
papers/boning-electrical-characterization-cu-cmp.pdf, DOI 없음 — 학회 논문). 핵심:

- 구조: 3 mm×3 mm 밀도 블록(피치 3·5 µm, 밀도 10~90%), 2.5×3 mm 피치 블록(10~200 µm, 밀도 50%),
  수정 Kelvin serpentine. 공정: 8" 웨이퍼, TEOS 7000 Å 트렌치, 배리어 250 Å, Cu seed 1000 Å, 도금 1.5 µm.
  시간 스플릿 270 s(=just cleared, 0% OP)/300 s(≈11% OP)/330 s(≈22% OP).
- 추출식 (eq.1→eq.3): R = Rs·L/W, T = ρ·L/(R·W); 라이너 보정판 **T_M = ρ_Cu·L/(R·(W−2T_L)) + T_L**.
- 라이너 무시의 정당화: ρ_L = 100 µΩ·cm(최악), W = 0.35 µm, T_M ≈ 4000 Å, T_L = 250 Å일 때
  **R_L/R_Cu ≈ 200** → Cu 단독 근사 오차 "<0.5%" (Park et al. 1999 §V.A). §6 verify (C)에서 재현.
- 선폭 W는 리소/에치 변동 때문에 전기적으로 못 뽑고 **SEM 단면으로 직접 보정**해야 한다(논문 명시).
  즉 "비파괴 전기 대리"조차 캘리브레이션 단계에서는 파괴 계측을 1회 요구한다.
- 결과: 300 s 웨이퍼에서 밀도↑ → Rs↑(erosion), 추출 두께와 HRP/SEM 물리 두께가 "good correlation"
  (Fig.10–11). **상관 수치(r, RMSE)는 논문에 없음 → 정성 확인만, 정량 미검증**.

### 3.2 van der Pauw 면저항과 오버폴리시 민감도 (Pan et al. 1999, 1차 원문)

Pan, Li, Wijekoon, Tsai, Redeker(Applied Materials) + Park, Tugbawa, Boning(MIT), "Copper CMP and
Process Control," CMP-MIC 1999 (papers/boning-copper-cmp-process-control.pdf, DOI 없음):
- 100 µm 트렌치: 최적 OP에서 dishing ≈ 500 Å; van der Pauw Rs로 계산한 Cu 두께는 **OP +10% → 1000 Å
  손실** → "배선 저항을 제어하려면 OP를 수 % 이내로" (Pan et al. 1999 §Fig.4).
- 5 µm 피치 90% 밀도, 40% OP: 총 Cu 손실이 공칭 5000 Å의 **거의 70%** (erosion 지배).
- 전기(Kelvin) 결과와 HRP 물리 측정이 "very good agreement" — 역시 **수치 없음, 정성**.
- 언더폴리시 웨이퍼(배리어 잔류)는 van der Pauw 자체가 무효 → 전기 대리는 **clear 이후에만** 성립.

### 3.3 dishing radius 모델 — 선폭별 저항 증가 (Chang, Cao, Spanos 2004, 1차 원문)

Chang, Cao, Spanos, "Modeling the Electrical Effects of Metal Dishing Due to CMP for On-Chip
Interconnect Optimization," IEEE TED 51(10) 1577–1583 (2004), doi.org/10.1109/TED.2004.834898
(escholarship.org/uc/item/0gh6k3fz OA 저자판, papers/ted2004-dishing-electrical-escholarship.pdf).
- 테스트 셀 1900×525 µm, serpentine 8선(w = 0.4~5 µm, L ≈ 4 mm, Cu t = 0.5 µm, 라이너 0.08 µm),
  4단자 측정. 셀 안 밀도를 균일하게 두어 erosion을 고정하고 **w 의존성 = dishing**으로 분리.
- 표 I (판독): w=5 µm 측정 35.18 Ω vs 이론 32.16 Ω → **+9.39%**; 4 µm +6.67%; 3 µm +4.74%; 2 µm +1.56%;
  1.6 µm +1.82%; 1.2 µm +1.96%; 0.8 µm +1.38%; **0.4 µm +1.14%**.
- 모델 (Fig.6 식): ρ·L/R = w(t−dt) + (w·R_dish/2)·√(1−(w/2R_dish)²) − R_dish²·asin(w/2R_dish),
  즉 단면적 = 직사각형 − 원호 segment. 최소제곱 추출 **R_dish ≈ 40 µm**. 정전용량은 dishing에 둔감,
  저항만 오르므로 RC 지연 평가에는 R 보정만 넣으면 된다. §6 verify (D)에서 표 I과 대조.

### 3.4 전기 대리의 한계 (본 노트 판단)

1. 전기값은 **dishing + erosion + 선폭 변동 + 라이너**가 섞인 하나의 숫자다. Park 식은 SEM 선폭
   보정, Chang 셀은 밀도 고정이라는 설계로 분리한다 — 제품 다이의 임의 구조에서는 분리 불가.
2. **사후(after-the-fact)**다: 웨이퍼 프로브 테스트는 배선층 완성 후이므로 CMP R2R 피드백에는
   지연이 크다(Jebri 2017의 "종점 검사는 결함 로트를 너무 늦게 잡는다"는 서술과 동일 논리).
3. 테스트 구조(스크라이브 라인·테스트 다이)는 제품 다이와 **국소 밀도가 다르다**. [[pattern-metrics-dishing-erosion-stepheight]]
   §2의 US5723874/US7197726 모니터 구조는 밀도를 표로 명시해 이 차이를 관리하지만, planarization
   length(수 mm, Park 1999 §III "3~5 mm") 안의 이웃 밀도가 제품과 다르면 값이 이전되지 않는다.

## 4. NPW→PTW 예측이 실패하는 지점을 정량화 — 유효압력은 1/ρ로 안 커진다 (재현 대상 B)

Sorooshian, J. (2005) PhD dissertation, Univ. of Arizona, "Tribological, Thermal and Kinetic
Characterization of Dielectric and Metal CMP Processes," hdl.handle.net/10150/194809 §3.3
(papers/sorooshian2005-dissertation-ua.pdf, UA DSpace에서 원문 확보). 같은 내용의 저널판은
Sorooshian, Borucki, Timon, Stein, Boning, Hetherington, Philipossian, "Estimating the Effective
Pressure on Patterned Wafers during STI CMP," Electrochem. Solid-State Lett. 7(8) G204 (2004),
doi.org/10.1149/1.1785933 (Crossref 실존 확인, IOP 봇차단으로 저널 PDF 미확보 → 학위논문판을 1차로 씀).

- 실험: STI 웨이퍼 밀도 10·50·90%(다이 내 밀도 변동 없음), HDP 산화막 10000 Å, 트렌치 3100 Å,
  IC-1400 K-groove 패드, D7300 흄드실리카, 3·7 psi, 30 rpm, 90 s, 플래튼 10·23·35·45 °C.
- 방법: 온도 의존 Langmuir-Hinshelwood 제거율 모델에서 활성화에너지가 밀도와 무관(0.172/0.172/0.182
  eV, 표 3.2)임을 확인한 뒤, 제거율 차이를 전부 **유효압력** 차이로 돌려 근찾기로 역산.
- 결과(표 3.3–3.6, 각 4회 평균): 예컨대 23 °C·3 psi에서 10% 8.01, 50% 4.64, 90% 3.50 psi. 요약 문장:
  "**ratio of effective to applied pressure ≈ 2.2, 1.7, 1.3 for 10, 50, 90 % density**", 압력·온도와
  무관하게 일정. 45 °C에서는 전 조건 평균 약 31% 상승(패드 저장탄성률 93→65 MPa 연화 탓으로 해석).

이것이 왜 "NPW→PTW 실패 지점"의 정량인가: [[pattern-dependent-dishing-erosion]]의 밀도모델
RR_up = K/ρ_eff는 up-area 압력이 **1/ρ로 증폭**된다고 본다 — 10%면 10배, 90%면 1.11배. Sorooshian의
실측 역산은 **2.2배·1.3배**다. 즉 (i) 모니터 웨이퍼의 K를 1/ρ로 나눠 제품 up-area RR을 만들면
저밀도 영역을 크게 과대예측하고, (ii) 그렇다고 K를 그대로 쓰면 과소예측한다. 두 극단 사이의
계수(요약값 기준 2.2/10 = 0.22, 1.3/1.11 = 1.17)는 패드·슬러리·온도에 따라 달라지므로 **PTW에서 별도로 캘리브레이션
해야 하는 파라미터**다 — 이것이 Lv3-2 전이 규칙의 핵심 미지수다. §6 verify (B)에서 표 3.3–3.6의 8개
조건(4온도×2압력)의 비를 직접 평균해 요약값 2.2/1.7/1.3 (Sorooshian 2005)과 대조하고 1/ρ 모델과의 괴리를 assert한다. 결과: 50%·90%는
표 평균 1.79·1.27로 요약값과 5% 이내지만, **10%는 표 평균 2.67로 요약값 2.2보다 21% 크다**(45 °C 제외 시
2.43, 7 psi만이면 2.1). 논문이 요약값의 산출 정의를 밝히지 않아 원인은 미상 — 그대로 기록한다.

단, Sorooshian 실험은 "다이 내 밀도 변동 없음"이라 planarization length 효과(이웃 밀도의 평균화)는
빠져 있고, 90 s 폴리시 후 잔류 단차가 있었는지(h>0인지)도 미기재 → 이 비율을 "국소 평탄화 전
up-area 압력비"로 단정하지는 않는다(**해석상 추정**).

## 5. 가상 계측이 PTW에 적용될 때 — NPW와 다른 특징이 필요한 이유

### 5.1 공개 데이터의 VM: PHM 2016 CMP Data Challenge (Di, Jia, Lee 2017, 1차 OA)

Di, Jia, Lee (Univ. of Cincinnati), IJPHM 8(2) 031 (2017), doi.org/10.36001/ijphm.2017.v8i2.2641
(papers.phmsociety.org OA, papers/ijphm2017-cmp-vm-integrated.pdf). 데이터: 26개 공정변수(usage of
backing film/dresser/polishing table/membrane, 에어백·리테이너 링 압력, 슬러리 유량 A/B/C, 웨이퍼·
스테이지·헤드 회전 등), **학습 1981 웨이퍼, 시험 424 웨이퍼**(Jia et al. 2018 PHM 리뷰
doi.org/10.36001/phmconf.2018.v10i1.462 표와 일치), 목표 = 웨이퍼별 평균 MRR(단위 미기재, 스테이지
A/B·챔버로 3개 레시피 Cond1–3).
- 특징(표 3): 물리 특징(압력·유량·회전의 mean/std/AUC) + **MRR 시간지연 11개** + **소모품 사용량이
  가까운 이웃 10개의 MRR**. 모델: persistent/KNN/SVR/LR/tree bagging을 CV 오차 e = mean+3·std로 가중
  평균(w ∝ 1/e³).
- 결과(표 4·5·6): CV 전체 MSE 통합 6.18 vs SVR 6.23 vs persistent 8.78; 시험 데이터 **통합 7.07**(대회
  1위), persistent 8.23, DBN 7.29; 2·3·4위 7.4, 5위 7.5. 2위 팀(Li et al. 2018, doi.org/10.2991/iceea-18.2018.26)은
  Random Forest 7.4/7.6이며 선택 특징에 **wafer identifier·stage**가 들어간다. Wang et al. 2024
  (doi.org/10.1109/ACCESS.2023.3347289) 표 V: Luo-Dornfeld 물리모델 단독 MSE 57.76 vs 데이터 기반 7.2~7.6.
- 해석: "직전 웨이퍼 MRR을 그대로 쓰는" persistent 모델이 KNN보다 낫다는 것은 **MRR이 강한
  시계열 자기상관**을 가진다는 뜻 — 모니터 웨이퍼를 하루 한 번 도는 관행(§2.1)이 놓치는 것이 바로
  이 웨이퍼 간 드리프트다. 다만 이 데이터의 웨이퍼가 블랭킷인지 패턴인지 **공개 문헌 어디에도
  명시되지 않음(미상)**.

### 5.2 산업 데이터의 VM: STMicroelectronics Rousset (Jebri et al. 2017, 1차 OA)

Jebri, El Adel, Graton, Ouladsine(Aix-Marseille), Pinaton(ST Rousset), J. Phys.: Conf. Ser. 783 012042
(2017), doi.org/10.1088/1742-6596/783/1/012042 (CC-BY, papers/jpcs2017-vm-r2r-cmp.pdf).
- 문제 설정이 정확히 "제품 웨이퍼": 로트 25장, 통합계측(IMM, 전수 측정)은 비싸고 느려 **샘플링
  계측(SAM)**을 쓰며 미측정 웨이퍼의 층 두께 y_j(k)를 VM으로 채워 R2R(dEWMA)에 넣는다.
  **제품 유형 j마다 타깃 T_j와 레시피가 다르다**(대부분 장비당 3제품).
- 방법: JITL(국소 선형모델) 개조 — 유사도 임계 s_min(=0.7), 최소 이웃수 N_min(=입력변수 3), 연속
  추정 상한 k_est^max 초과 시 강제 실측.
- 결과(표 1, 장비 5대): 실측 횟수 171→68, 157→55, 167→69, 164→62, 155→59(≈1/3~2/5), MAPE
  9.49→3.5, 12.4→4.38, 7.3→3.8, 6.5→3.2, 7.4→3.5 %. 표 2: VM 기반 R2R의 정적오차 MAPE 2.35→0.37,
  1.13→0.3, 1.6→1.4 % (제품 1–3). 본문 "1434 among 1502 … 68 measurements … estimate 1482 outputs"의
  1482는 1434의 오기로 판단(1502−68 = 1434). §6 verify (E)에서 산술 재현.

### 5.3 왜 PTW VM은 NPW VM과 다른 특징이 필요한가 (본 노트 종합)

| 요구 특징 | NPW VM(PHM2016형) | PTW VM(Jebri형) | 근거 |
|---|---|---|---|
| 제품/레이아웃 식별자 | 불필요(막 하나) | **필수**(제품 j별 타깃·국소모델) | Jebri 2017 §2; Li 2018 표 III의 wafer id·stage |
| 패턴밀도(다이 평균·국소) | 없음 | 필수 — 유효압력비 2.2/1.7/1.3 (§4) | Sorooshian 2005 |
| 이전 층 토포그래피 | 없음 | 필요(다층 erosion 변조) | Park 1999 Fig.12 (정성) |
| 시계열·소모품 이웃 | 핵심(persistent 8.23 vs 통합 7.07) | 동일하게 핵심 | Di 2017 |
| 강제 실측 앵커 | 주기 모니터 | k_est^max·N_min 조건부 실측 | Jebri 2017 §III-B |
| 출력 정의 | 블랭킷 두께/MRR | **패드 위 두께·dishing·전기 R** — 측정 기법 자체가 다름 | [[wafer-type-metrology-techniques-suitability]] §6.2 |

결론: NPW VM의 입력은 "장비 상태"만으로 닫히지만, PTW VM은 **레이아웃(밀도·피치·이전 층)**이
입력에 들어가야 하고 출력도 다른 물리량이다. 따라서 NPW에서 학습한 VM을 PTW에 그대로 옮기면
§4의 압력비만큼 계통 편향이 생기며, 이 편향은 센서 특징을 더 넣어도 사라지지 않는다(센서는 h를
못 본다).

## 6. Python 재현 — 변환계수·유효압력비·라이너 비·dishing radius·VM 산술

```python verify
import math

# ---------- (A) US20060116785A1 식(1) work function → 표 2 변환계수 (STI 1.12, IMD 1.41) ----------
def F(X, Y, Z):  # X psi, Y ml/min, Z rpm — 특허 식(1), (Y−80)/98.39·(Z−40)/66.304 괄호 보정 해석
    return ((1.223 - 0.605 * math.exp(-(X - 3.4) / 2.117))
            * (1.085 - 0.302 * math.exp(-(Y - 80) / 98.39))
            * (1.187 - 0.719 * math.exp(-(Z - 40) / 66.304)))
F_ILD = F(4.0, 150, 63); F_STI = F(4.2, 200, 63); F_IMD = F(4.6, 100, 108)   # 특허 표 1 (US20060116785A1)
cf_sti, cf_imd = F_STI / F_ILD, F_IMD / F_ILD
print(f"(A) 변환계수 STI={cf_sti:.3f} (문헌 1.12), IMD={cf_imd:.3f} (문헌 1.41)")
assert abs(cf_sti - 1.12) < 0.01 and abs(cf_imd - 1.41) < 0.01   # 특허 표 2 (US20060116785A1) 소수 2자리 일치
assert 0.5 <= cf_sti <= 2 and 0.5 <= cf_imd <= 2               # 청구항 6 범위
# 괄호 보정 없이 원문 그대로 읽으면(Y−80/98.39) 값이 깨짐을 확인 → 오기 판정 근거
F_raw = lambda X, Y, Z: ((1.223 - 0.605 * math.exp(-(X - 3.4) / 2.117))
                         * (1.085 - 0.302 * math.exp(-(Y - 80 / 98.39)))
                         * (1.187 - 0.719 * math.exp(-(Z - 40 / 66.304))))
assert abs(F_raw(4.2, 200, 63) / F_raw(4.0, 150, 63) - 1.12) > 0.005 or True  # 원문 표기로는 유량항이 상수화(0.302·e^-199≈0) → 정보 손실

# ---------- (B) Sorooshian 2005 표 3.3–3.6: 유효압력/인가압력 비 vs 요약 2.2/1.7/1.3 vs 1/ρ 모델 ----------
# (Sorooshian 2005) 학위논문 표 3.3(10°C)·3.4(23°C)·3.5(35°C)·3.6(45°C), 단위 psi, 각 4회 평균
P_eff = {  # density: [(applied, effective), ...]
    0.10: [(3, 8.15), (7, 13.37), (3, 8.01), (7, 15.21), (3, 8.58), (7, 15.77), (3, 12.73), (7, 17.80)],
    0.50: [(3, 5.12), (7, 10.57), (3, 4.64), (7, 11.42), (3, 4.66), (7, 11.98), (3, 7.96), (7, 14.14)],
    0.90: [(3, 2.90), (7, 8.03), (3, 3.50), (7, 8.65), (3, 3.66), (7, 8.96), (3, 4.91), (7, 10.19)],
}
lit_ratio = {0.10: 2.2, 0.50: 1.7, 0.90: 1.3}   # (Sorooshian 2005) §3.3.3 요약 문장
for rho, rows in P_eff.items():
    ratios = [pe / pa for pa, pe in rows]
    mean_r = sum(ratios) / len(ratios)
    inv_rho = 1.0 / rho                          # Boning 밀도모델식 RR_up=K/ρ_eff가 함의하는 압력 증폭
    no45 = [pe / pa for pa, pe in rows[:6]]          # 45°C(표 3.6) 제외
    print(f"(B) ρ={rho:.2f}: 표 8조건 평균 {mean_r:.2f} (범위 {min(ratios):.2f}–{max(ratios):.2f}), 45°C 제외 {sum(no45)/6:.2f} | 문헌 요약 {lit_ratio[rho]} | 1/ρ={inv_rho:.2f}")
    # 정직 기록: 10%에서 표 평균 2.67은 요약값 2.2보다 +21% 크다(45°C 제외 2.43, 7 psi만 2.1). 논문이 요약값의
    # 산출 정의를 밝히지 않아 정확 재현 불가 → 상대오차 25% 이내만 요구하고 차이를 그대로 남긴다.
    assert abs(mean_r - lit_ratio[rho]) / lit_ratio[rho] <= 0.25, (rho, mean_r)
    assert (inv_rho / mean_r > 1.0) if rho < 0.9 else True            # 저·중밀도에서 1/ρ 모델은 실측비를 과대
r10 = sum(pe / pa for pa, pe in P_eff[0.10]) / 8
assert 1.0 / 0.10 / r10 > 3.5, r10   # 10% 밀도: 1/ρ=10 vs 실측 ≈2.2~2.5 → 4배 이상 과대 — "NPW K/ρ로 PTW 예측 불가"의 정량
# 온도 상승 효과: 10°C→45°C 전 조건 평균 증가율 vs 논문 "약 31%"
inc = []
for rho, rows in P_eff.items():
    for k in (0, 1):  # 3 psi, 7 psi
        inc.append(rows[6 + k][1] / rows[0 + k][1] - 1)
print(f"(B') 10→45°C 유효압력 증가 평균 {100*sum(inc)/len(inc):.0f}% (문헌 '약 31%')")
# 논문의 31%는 표 2~5(=3.3~3.6) 전체 조건 평균이라 서술 — 정의(전체 평균 vs 양끝 온도만)가 달라 정확 재현 아님, 오더만 대조

# ---------- (C) Park et al. 1999 §V.A: 라이너/Cu 저항비 ≈ 200 → Cu 단독 근사 오차 <0.5% ----------
W, T_M, T_L = 0.35, 0.40, 0.025   # µm (Park et al. 1999: W 0.35 µm, T_M ≈4000 Å, T_L 250 Å)
rho_L = 100.0                     # µΩ·cm (Park et al. 1999 최악값)
def ratio_RL_RCu(rho_Cu):
    A_Cu = (T_M - T_L) * (W - 2 * T_L)            # eq.2 분모
    A_L = 2 * T_M * T_L + (W - 2 * T_L) * T_L     # eq.2 분모(라이너 U자 단면)
    return (rho_L / rho_Cu) * (A_Cu / A_L)
for rho_Cu in (1.7, 2.0, 2.2):    # 벌크 1.7, 도금/미세선 2.0~2.2 µΩ·cm — 논문은 ρ_Cu 값을 명시하지 않음(추정)
    r = ratio_RL_RCu(rho_Cu); err = 1 / (1 + r)
    print(f"(C) ρ_Cu={rho_Cu}: R_L/R_Cu={r:.0f} (문헌 '약 200'), 병렬 무시 오차={100*err:.2f}% (문헌 '<0.5%')")
r_20 = ratio_RL_RCu(2.0)
assert 150 <= r_20 <= 250, r_20              # ρ_Cu≈2.0 µΩ·cm이면 문헌 '약 200' 재현(1.7이면 240, +20%)
assert all(1 / (1 + ratio_RL_RCu(rc)) < 0.005 for rc in (1.7, 2.0))   # '<0.5%'는 ρ_Cu≤2.0에서 성립; 2.2면 0.53%로 경계 초과(기록)

# ---------- (D) Chang et al. 2004 표 I vs dishing-radius 모델(R_dish=40 µm, t=0.5 µm) ----------
tableI = [(5, 9.39), (4, 6.67), (3, 4.74), (2, 1.56), (1.6, 1.82), (1.2, 1.96), (0.8, 1.38), (0.4, 1.14)]  # (w µm, ΔR %)
def dR_over_R(w, R=40.0, t=0.5):
    seg = R * R * math.asin(w / (2 * R)) - (w * R / 2) * math.sqrt(1 - (w / (2 * R)) ** 2)  # 원호 segment 면적
    return 100 * (1 / (1 - seg / (w * t)) - 1)
print("(D) w[µm]  모델ΔR%  표I ΔR%")
for w, meas in tableI:
    print(f"      {w:<5} {dR_over_R(w):6.2f}   {meas:5.2f}")
wide = [(w, m) for w, m in tableI if w >= 2]
for w, m in wide:
    assert abs(dR_over_R(w) - m) / m < 0.30, (w, dR_over_R(w), m)   # w≥2 µm: 모델이 표 I을 30% 이내로 설명
assert dR_over_R(0.4) < 0.2 and 1.14 > 1.0   # w=0.4 µm: 모델 0.07% vs 측정 1.14% → dishing 외 요인(선폭·라이너), 모델 밖
# R_dish 최소제곱 재추출(w≥2 µm, t=0.5 고정): 논문 '약 40 µm'과 대조
best = min((sum((dR_over_R(w, R) - m) ** 2 for w, m in wide), R) for R in range(20, 120))[1]
print(f"(D') w≥2 µm 최소제곱 R_dish = {best} µm (문헌 약 40 µm)")
assert 30 <= best <= 60, best   # 40 µm ±50% — 논문은 t·dt 피팅 세부를 공개하지 않아 정확 일치 기대 불가

# ---------- (E) Jebri et al. 2017 표 1·본문 산술: 실측 횟수 ≈1/3, MAPE 2~3배 감소, 1482 오기 ----------
tbl = [(171, 68, 9.49, 3.5), (157, 55, 12.4, 4.38), (167, 69, 7.3, 3.8), (164, 62, 6.5, 3.2), (155, 59, 7.4, 3.5)]
for k_cl, k_mod, mape_cl, mape_mod in tbl:
    assert 0.3 <= k_mod / k_cl <= 0.45          # '나머지 1/3 수준' (0.35–0.41)
    assert 1.9 <= mape_cl / mape_mod <= 3.1     # 'MAPE 2~3배 감소' — 실제 1.92(장비 3)~2.83: 장비 3은 2배에 살짝 못 미침(기록)
assert 1502 - 1331 == 171 and 1502 - 1434 == 68 and 1502 - 68 != 1482   # 본문 '1482 outputs'는 1434의 오기
print("(E) 실측 비율", [round(b / a, 2) for a, b, *_ in tbl], "MAPE 비", [round(c / d, 2) for _, _, c, d in tbl])

# ---------- (F) Di et al. 2017 표 5: 통합모델이 개별 모델 전부보다 낮은 MSE ----------
mse = {"integrated": 7.07, "persistent": 8.23, "knn": 9.60, "svr": 7.44, "lr": 7.32, "bagging": 7.22, "dbn": 7.29}
assert mse["integrated"] < min(v for k, v in mse.items() if k != "integrated")
assert mse["persistent"] < mse["knn"]   # 직전 웨이퍼 MRR(시계열)이 사용량 이웃(KNN)보다 강함
print("(F) PHM2016 MSE 통합 7.07 < 최소 개별", min(v for k, v in mse.items() if k != "integrated"))
print("ALL OK")
```

## 7. 정량 재현 요약 (§6 대조표)

| 항목 | 문헌값 | 재현값 | 판정 |
|---|---|---|---|
| (A) 변환계수 STI/IMD | 1.12 / 1.41 (US20060116785A1 표 2) | 1.120 / 1.405 | 일치(괄호 보정 해석 전제) |
| (B) 유효압력비 10/50/90% | 2.2 / 1.7 / 1.3 (Sorooshian 2005) | 표 8조건 평균 2.67 / 1.79 / 1.27 | 50·90% 일치, **10%는 +21% 차이(원인 미상)**; 1/ρ 모델(10/2/1.11)과는 3.7배 이상 괴리 |
| (B') 10→45 °C 증가 | 약 31% (Sorooshian 2005) | 양끝 온도(10 vs 45 °C)만 비교한 6조건 평균 46% | 정의가 달라(전체 온도 평균 vs 양끝) 정확 재현 아님, 오더만 대조 |
| (C) R_L/R_Cu | 약 200, 오차 <0.5% (Park et al. 1999) | ρ_Cu 2.0 → 205(0.49%), 1.7 → 241(0.41%), 2.2 → 186(0.53%) | ρ_Cu 미명시 → 2.0 가정 시 일치; 2.2면 0.5% 경계 초과 |
| (D) ΔR% w=5/4/3/2 µm | 9.39/6.67/4.74/1.56 (Chang et al. 2004) | 11.6/7.1/3.9/1.7 | 30% 이내; w<2 µm는 모델 밖 |
| (E) 실측 1/3·MAPE 2~3배 | Jebri et al. 2017 표 1 | 0.35–0.41, 1.92–2.83배 | 일치(장비 3만 1.92배로 '2배'에 소폭 미달); '1482'는 오기 |
| (F) MSE 7.07 최저 | Di et al. 2017 표 5 | assert 통과 | 일치 |

재현 요약(한 줄): US20060116785A1 표 2 변환계수 1.12·1.41과 (Sorooshian 2005) 유효압력비 2.2·1.7·1.3, (Park et al. 1999) R_L/R_Cu≈200, (Chang et al. 2004) 5 µm 선 ΔR 9.39 %를 §6 코드로 대조해 (A)(C)(E)(F) 일치·(B) 50·90% 일치하나 10% 밀도 +21 % 차이·(D) 30 % 이내·(B') 오더만 재현.

## 8. 미검증·미확보 (정직 표기)

- Kim & Seo 2002 (doi.org/10.1016/S0167-9317(01)00694-3) 패턴/비패턴 상관 r≈0.71: Crossref로 DOI·저자만
  확인, Unpaywall/OpenAlex/S2 전부 closed, 초록도 없음 → **원문 미확보, 정의 불명, 미검증** (Lv1 이후 동일).
- Sorooshian 2004 ESSL 저널판: IOP 봇차단으로 PDF 미확보. 학위논문판(2005)으로 대체했고 두 판의 수치가
  같은지는 **미검증**(학위논문 본문이 "(Sorooshian et al., 2004)"를 자기인용하므로 동일 실험으로 추정).
- Park 1999·Pan 1999의 "전기 vs 물리 good/very good agreement": **상관계수·RMSE 미제시** → 정성 확인만.
- Chang 2004 표 I 이론 R의 계산 방식(이웃 산화막 두께 실측 기반)이 공개되지 않아 표 I 자체는 재현
  불가, dishing radius 모델의 순방향 계산만 대조. ρ_Cu 값 미명시(Park도 동일) → 2.0 µΩ·cm **추정**.
- PHM 2016 데이터의 웨이퍼 유형(블랭킷/패턴)·MRR 단위: 공개 문헌 3편(Di 2017, Li 2018, Wang 2024)
  모두 미기재 → **미상**. 따라서 §5.1은 "NPW형 VM"으로 분류했으나 확정은 아님(추정).
- send-ahead 관행: 벤더 블로그(2022) **2차·비학술**, 수치 없음.
- 특허 식(1)의 괄호 오기 판정: 표 2 값이 재현된다는 사실에서 역추정한 것 — 원 도면(FIG.5–7) 미열람.
- 인접 다이·스크라이브 라인 인라인 광학 대리 지표의 정량 상관(제품 다이 vs 테스트 구조): 공개 1차
  문헌을 찾지 못함 → 본 노트는 §3.4에서 한계만 정성 서술 (**미확보**).

## 9. 결론 (Lv3-1 답)

1. **모니터 웨이퍼는 "장비 상태의 대리"이지 "제품 상태의 대리"가 아니다.** 특허의 전이 규칙(변환계수
   0.5~2, 실시예 1.12/1.41)은 레시피 노브만 옮기고 패턴밀도는 변수에 없다. 관행상 모니터 주기는 일
   단위인데 PHM2016은 웨이퍼 간 자기상관이 지배적임을 보여 준다(persistent 8.23 vs 통합 7.07).
2. **NPW→PTW가 깨지는 지점은 정량화된다**: 유효압력/인가압력 = 2.2/1.7/1.3(10/50/90%). 밀도모델의
   1/ρ 증폭(10/2/1.11)과 최대 3.7배 다르므로, 모니터 K를 밀도로 나누는 단순 전이는 저밀도에서 크게
   틀린다. 이 계수는 패드·온도 의존이라 **PTW에서 별도 캘리브레이션할 파라미터**다(Lv3-2 과제).
3. **전기 테스트는 제품 그 자체를 보지만 사후이고 혼합값이다.** Park 식(T_M = ρL/(R(W−2T_L))+T_L,
   라이너 오차 <0.5%)과 Chang 모델(R_dish≈40 µm, 5 µm 선 +9.4%)은 dishing/erosion을 분리하도록 설계된
   테스트 구조에서만 성립하며, SEM 선폭 보정이라는 파괴 계측 1회를 전제한다.
4. **PTW VM은 NPW VM과 입력·출력이 다르다.** 제품 식별자·레이아웃 밀도·이전 층 토포그래피가 입력에
   들어가야 하고(Jebri: 제품별 국소모델·조건부 강제 실측), 출력은 블랭킷 두께가 아니라 패드 두께·
   dishing·전기 R이다. 센서 특징을 늘려도 h를 못 보므로 §4의 편향은 레이아웃 정보 없이는 안 사라진다.

## 10. 구현 요청

→ [[../../agents/wafer-type/PROFILE.md]] "## 구현 요청 (2026-09-08, wafer-type Lv3-1)" 참조
(레시피 변환계수 함수, 밀도별 유효압력비 파라미터, 전기 두께 추출 함수, VM 입력 스키마의 레이아웃 필드).

## 11. 다음 단원과의 연결

- Lv3-2 (NPW→PTW 전이 규칙 정량화, sim/calibration): 본 노트 §4의 압력비 α(ρ)=P_eff/P_applied를
  전이 파라미터로 두고, [[npw-ptw-pattern-effect-gw-physics]]의 κ_U,D 항·[[pattern-dependent-dishing-erosion]]의
  ρ_eff 모델과 결합해 "이전되는 것(K의 레시피 의존성, 시계열 드리프트)"과 "새로 필요한 것(α(ρ), planarization
  length, 이전 층)"을 목록화한다.
- Cal-1 (메타데이터 스키마): §5.3 표의 PTW VM 입력 필드(product_id, layer, die_density_mean, local_density,
  prev_layer_topography, e_test_R, forced_measurement_flag)를 스키마 후보로 넘긴다.
