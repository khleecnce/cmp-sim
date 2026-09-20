<!-- V2-SECTION: R5-wafer | 분배완료 2026-09-08 | 근거: dishing, erosion, pattern- | 정본: ARCHITECTURE-V2.md §3 -->
# 패턴 지표의 문헌 정의 — dishing·erosion·step height·잔막(residual)·엣지 롤오프: 측정 구조물과 판정 기준

> 에이전트: wafer-metrology Lv2-2 | 작성일: 2026-09-07
> 선행: [[uniformity-metrics-definitions-standards]] [[wafer-metrology-thickness-methods]] [[pattern-dependent-dishing-erosion]] [[wafer-surface-roughness-afm-scan-scale-dependence]]
> 관련: [[npw-ptw-pattern-effect-gw-physics]] (NPW가 PTW를 예측 못하는 물리) [[wiwnu-pressure-velocity-wafer-scale]] (엣지 압력특이점)

## 0. 목적과 원칙

[[uniformity-metrics-definitions-standards]]가 blanket 웨이퍼의 반경/polar 지표(TTV·WIWNU·CV·radial)를 문헌에서
확정했다면, 이 노트는 **패턴 웨이퍼(PTW)의 die/feature 스케일 지표**를 같은 원칙으로 확정한다. 지표 정의는
회사 관행이 아니라 **공개 문헌·표준·특허**에서 가져오고, 정의가 갈리면 병기하되 기준은 문헌이다. 이 노트의
정의가 곧 `sim/metrics/`의 패턴 지표 출력 스키마가 된다(구현은 PROFILE.md 구현요청으로 인계).

이 단원에서 확인한 핵심 사실: (1) dishing/erosion은 **기준면(reference)이 무엇인가**에 따라 정의가 셋으로
갈린다. (2) 스텝하이트 자체에는 ISO 표준이 없고 **교정 표준 측정법(ISO 5436-1)**의 직선피팅을 빌려 쓴다.
(3) "엣지 롤오프"는 웨이퍼 기하(SEMI ROA/ZDD/ESFQR)와 CMP 제거율 엣지 프로파일이라는 **두 개의 다른 개념**이
같은 이름으로 불린다. (4) "잔막(residual)"도 잔류 금속(결함)과 잔여 막두께(연속량)의 두 뜻이 있다.

## 1. 용어 정의 — 출처별 병기

### 1.1 Cu dishing / oxide erosion (damascene)

| 출처 | dishing 정의 | erosion 정의 | 기준면 |
|---|---|---|---|
| Park et al. 1998 VMIC (MIT/SEMATECH, 원문 확인) | "the vertical distance between the **final oxide level** and the lowest point within the copper line after CMP" | "the difference between the oxide thickness **as deposited** and the oxide thickness after CMP" | dishing: 인접 최종 oxide면 / erosion: 증착두께 |
| Pan et al. 1999 CMP-MIC (AMAT/MIT, 원문 확인) | 필드 oxide 손실을 **따로 분리**한 뒤 "the amount of recess of patterned copper or oxide **relative to the field oxide surface**" | 동일(필드 oxide면 기준 어레이 oxide 함몰) | 필드 oxide 표면 (field oxide loss는 별도 항) |
| Steigerwald et al. 1994 JECS (초록 확인) | Cu 구조 **폭**에 강하게 의존, 밀도엔 미미 | SiO₂ erosion은 **패턴밀도**에 강하게 의존, 선폭엔 무관 | — (의존성만 초록에 명시) |
| IBM US5723874 (1998, 특허 텍스트 확인) | "non-planarity caused by accelerated polishing at the center of relatively large conductors ... primarily caused by deformation of the pad" | "occurs where there is insufficient oxide to act as a CMP stop ... oxide can be thinned down" | 전기 전도도(두께) 감소량으로 환산 |
| Noh, Saka & Chun (MIT LMP, dspace 원문 확인) | — | **wafer-level e1** = 국소 기준점 대비 원래 유전체 두께로부터의 overpolish 양, **die-level e2** = 같은 die 안 기준점(blanket 영역) 대비 유전체 두께차 | die 내 blanket 영역 |

- 1차 출처: Park, Tugbawa, Yoon, Boning et al., "Pattern and Process Dependencies in Copper Damascene CMP
  Processes," *VMIC* 1998 — https://boning.mit.edu/wp-content/uploads/2022/11/Pattern-and-Process-Dependencies-in-Copper-Damascene-Chemical-Mechanical-Polishing-Processes.pdf (PDF 원문 확인, papers/park1998-vmic-cu-damascene.pdf)
- Pan, Li, Wijekoon, Tsai, Redeker (Applied Materials) + Park, Tugbawa, Boning (MIT), "Copper CMP and Process
  Control," *CMP-MIC* 1999 — https://boning.mit.edu/wp-content/uploads/2022/11/Copper-CMP-and-Process-Control.pdf (PDF 원문 확인)
- Steigerwald, Zirpoli, Murarka, Price, Gutmann, "Pattern Geometry Effects in the Chemical-Mechanical Polishing
  of Inlaid Copper Structures," *J. Electrochem. Soc.* (1994), https://doi.org/10.1149/1.2059241 (Crossref 실존
  확인·OpenAlex 초록 확인, **본문 유료·미확보**)
- Fayolle & Romagna, "Copper CMP evaluation: planarization issues," *Microelectron. Eng.* (1997),
  https://doi.org/10.1016/s0167-9317(97)00104-4 — Park 1998이 "erosion의 line-space 의존"의 선행으로 인용. 서지만
  확인, **초록·본문 미확보(2차 인용)**.
- Noh, Saka, Chun, "A Mechanical Model for Erosion in Copper CMP," MIT dspace
  https://dspace.mit.edu/bitstream/handle/1721.1/3746/IMST012.pdf (원문 확인).

**판정**: 세 정의는 필드 oxide 손실(field loss)을 어디에 넣느냐만 다르다.
`총 Cu 두께손실 = field oxide loss + oxide erosion + Cu dishing` (Pan 1999 Fig.8; Park 1998도 dishing+erosion=총손실)
이 항등식을 스키마의 상위 개념으로 두고, **default 기준면은 Pan식(필드 oxide면, field loss 별도 보고)**을 채택한다.
이유: 프로파일러 스캔에서 직접 얻는 양(필드면=0 기준 함몰)이고, 증착두께 기준(Park식)은 별도의 광학 두께측정을
요구한다. 두 값의 차이가 곧 field loss이므로 셋을 모두 출력하면 어느 정의로도 환산된다.

### 1.2 Step height — CMP 문맥의 두 상태
- **클리어 전(pre-clear) 잔여 스텝**: 금속 오버버든이 남아 있을 때 라인 위/사이 높이차. Pan 1999: "For wafers
  with less than 100% polish time ... Any measured step height was the remaining step height after partial polish."
  Boning 1999 MRS: "remaining local step height (or height differences in the oxide over patterned features and
  between patterned features)" — ILD CMP에서는 밀도효과에 의한 global nonplanarity보다 통상 작다.
- **클리어 후**: "For wafers with 100% or greater polish time ... The measured step height was then the amount of
  copper dishing" (Pan 1999) — 즉 클리어 후 스텝하이트 = dishing(또는 recess). 스키마에서 step height 필드는
  반드시 **클리어 여부(stage)**를 메타로 동반해야 한다.
- 스텝 계산 알고리즘(장비 공통): "There are no specific ISO standards covering the measurement of step heights.
  However ... there is a standard that outlines how these calibration standards should be measured (ISO 5436-1:2000)"
  (Taylor Hobson, Mills, *Tutorial – Step Height Measurement*, 벤더 자료 원문 확인). 최소제곱식
  `Z = aX + b + hδ` (δ=+1 높은 영역/−1 낮은 영역), **step = 2h**, 전이부 인접영역 제외. NIST(Vorburger et al.,
  *NIST Surface Roughness and Step Height Calibrations*, nist.gov PDF 원문 확인)도 단면 스텝은 양쪽 직선 최소제곱
  피팅 후 스텝 에지에서 외삽, 양면 스텝은 두 전이의 평균(NIST 알고리즘) 또는 ISO 5436-1 알고리즘을 쓴다.
  ISO 5436-1 원문 자체는 **미확보**(유료), 두 벤더/기관 문서로 2차 확인.

### 1.3 Recess · micro-dishing · edge-over-erosion(EOE)
- **recess**: 클리어 후 금속(또는 STI oxide)이 주변면보다 낮은 상태의 일반 명칭. KLA HRP 제품자료는 post-CMP
  항목을 "copper dishing, erosion, and recess"로 나열(kla.com HRP-260 페이지, 벤더 스니펫·2차). Park 1999 ECS
  다층 논문은 M1 어레이 함몰을 "array recess"로 부른다(원문 확인).
- **micro-dishing / edge-over-erosion**: Ortleb et al. 2008 SPIE(45 nm Cu CMP, HRP-350),
  https://doi.org/10.1117/12.772951 (초록 확인, 본문 미확보): "As feature sizes continue to shrink, micro-dishing and
  edge-over-erosion become important to characterize and control." EOE = 대형 어레이의 **가장자리**에서 중앙보다
  erosion이 큰 현상(W CMP의 "fang"과 동일 개념) — Lee et al. *IEEE TSM* 2016, https://doi.org/10.1109/tsm.2016.2631145
  (제목·DOI 확인, 정의는 검색 스니펫 **2차·미검증**).

### 1.4 잔막(residual) — 두 뜻을 분리
1. **잔류 금속/배리어(residue, 결함량)**: 클리어 불충분(underpolish) 시 필드에 남는 Cu/배리어 조각. Park 1998의
   "0% overpolish (just cleared)" 정의: "both the copper and the barrier material on top of the oxide in large
   unpatterned oxide regions have been completely removed". Pan 1999: 의도적 underpolish 웨이퍼에서 "surface
   barrier residue was observed over the van der Pauw test structure. This renders the electrical testing invalid".
   판정은 **0 허용(전기 단락)**이며 연속 지표가 아니라 검사(광학/전기)로 잡는다. Lai(MIT 박사논문 ch.6,
   web.mit.edu/cmp/publications/thesis/jiunyulai/ch6.pdf, 원문 확인)는 반사율로 subdie별 **잔류 Cu 분율**을 맵핑.
2. **잔여 막두께(remaining film thickness, 연속량)**: 유전체·나이트라이드 stop층의 CMP 후 남은 두께.
   `remaining = as-deposited − removed`. erosion(Park식)은 정확히 어레이 위 remaining oxide의 감소량이며, STI에서는
   "remaining nitride"가 같은 역할(활성영역 밀도에 따라 달라짐 — 특허 검색 스니펫, **2차**). 이 값은
   [[wafer-metrology-thickness-methods]]의 광학 두께계로 잰다(Park 1998: Tencor UV1250).

### 1.5 엣지 롤오프 — 웨이퍼 기하 지표 vs CMP 엣지 프로파일
**(a) 웨이퍼 기하(SEMI)**: 폴리시드 실리콘 웨이퍼의 엣지 수 mm에서 두께/표면높이가 기준선 아래로 떨어지는 양.
- **ROA(Roll-Off Amount)**: SEMI M77 "Test Method for Determining Wafer Near-Edge Geometry Using Roll-Off Amount,
  ROA" (M77-1015, Reapproved 0421; store-us.semi.org 제품페이지 스코프 확인, **원문 PDF 미확보**). 특허
  US10600634(SunEdison 2020, 텍스트 확인)는 "SEMI M69: Practice for Determining Wafer Near-Edge Geometry using
  Roll-off Amount, ROA (Preliminary) (2007)"와 Kimura et al. *JJAP* 38 (1999)를 원류로 인용 — M69→M77 승계 여부는
  **미확인**. 정의: 반경 위 두 점 P1·P2로 기준선 R(1차 직선 또는 3차 다항)을 피팅하고, 엣지 근처 P3와 기준선의
  수직거리가 ROA. front/back/thickness ROA 세 종류. **기준점 규약이 출처마다 다르다**: US10600634은 300 mm에서
  P1·P2 = 중심에서 120·140 mm(청구항은 반경의 82.7%·93.3%), P3 = 98.7%(148 mm; 변형 98.0/99.3%). Corning
  US9829310(2017, 텍스트 확인)은 P1·P2 = **엣지에서 3 mm·6 mm**, 45° 간격 8방위 측정. §6(D)에서 같은 프로파일에
  두 규약을 적용하면 ROA가 4배 다름을 재현 — **규약 없는 ROA 수치는 비교 불가**(WIWNU와 같은 교훈).
- **ZDD**: SEMI M68 (M68-0720) "radial double derivative of z" — 엣지 곡률 지표(스코프 확인, 원문 미확보).
- **ESFQR/ESFQD/ESBIR**: SEMI M67 (M67-0720) — 엣지 섹터 site flatness 지표(스코프 확인, 섹터 각도·길이 원문
  미확보). SEMI M70은 partial-site flatness. 모두 SEMI M1·MF1530 체계에 속한다.
**(b) CMP 엣지 프로파일**: 리테이너링·멤브레인 압력 특이점([[wiwnu-pressure-velocity-wafer-scale]])으로 엣지 수 mm의
제거율이 중심과 달라지는 것. Xie & Boning 2005 MRS, https://doi.org/10.1557/proc-867-w5.1 (초록 스니펫): 웨이퍼/리테이너링
압력·갭·패드 탄성률에 따라 "several millimeters into the wafer from the edge can polish either more quickly or more
slowly". Fukuda et al. 2012 *JJAP* 51 05EF01, https://doi.org/10.7567/jjap.51.05ef01 (초록 확인): 웨이퍼 고유
롤오프와 노치가 CMP 제거율 프로파일에 미치는 영역·강도를 규명(정량값은 본문 **미확보**). → 스키마에서는
`edge_rolloff_wafer_geometry(ROA)`와 `edge_removal_profile`을 **별도 필드**로 둔다.

## 2. 측정 구조물(테스트 스트럭처) — 문헌에서 확인된 설계

| 구조 | 파라미터 | 목적 | 출처 |
|---|---|---|---|
| MIT area mask | 솔리드 블록 20 µm×20 µm ~ 3 mm×3 mm, 내부 패턴(솔리드/50% 라인/adder M1) | dishing vs 블록 크기 | Park 1998 §II.B |
| MIT pitch mask | 수직 라인, 피치 2–1000 µm, 밀도 50% 고정 | dishing·erosion vs 피치(선폭) | Park 1998 |
| MIT density mask | 밀도 4–100%, 피치 250 µm 고정; 마스크 외형 12 mm×12 mm | erosion vs 밀도 | Park 1998 (oxide CMP 특성화에도 사용) |
| AMAT 100 µm 트렌치 | 100 µm 트렌치/100 µm 스페이스 어레이 + 인접 고립 100 µm 트렌치 | 광폭선 dishing vs overpolish(HRP) | Pan 1999 |
| AMAT 5 µm 피치 루프 | 50%: 2.5/2.5 µm 단일루프·더미동반루프·어레이(2200×2160 µm, 15 활성루프 Kelvin); 90%: 4.5 µm 선/0.5 µm 스페이스 | erosion 지배 손실, 전기-물리 대조 | Pan 1999 |
| van der Pauw | 시트저항→Cu 두께 vs overpolish | 전기적 총손실 | Pan 1999 |
| IBM dishing monitor (US5723874) | 정사각 도체 9세트: 한 변 200/150/100/75/50/30/20/10 µm(+1세트), 세트 간 20 µm 길이 도체 5개 직렬, 4점 측정 | 도체 크기별 dishing → 전도도 감소 | 특허 텍스트 |
| IBM erosion monitor (US5723874) | 이중 서펜타인, 피치 1.4–2.0 µm, space ratio 30–62.5%(= oxide폭/피치), 길이 ~1.2–1.8 m | 밀도별 erosion → 저항 | 특허 표(§6(B) 재현) |
| PDF Solutions MT-Kelvin (US7197726B2) | DUT / local neighborhood(차폐선 0.5 µm L/S) / global neighborhood 3층 제어; L1 3–6 µm, L2 100–600 µm; 스네이크 DUT; LoopNEST(결함 NEST + Kelvin 루프) | dishing(DUT 선폭 변화) vs erosion(global L/S 변화) **분리 DOE**; interaction distance(수백 µm) 추출 | 특허 텍스트 |
| MIT 다층 마스크 | M1 어레이 1250×1610 µm, M2 1250×800 µm, direct/half/dual overlap, via로 패드 연결 | M1 erosion이 M2 폴리시에 미치는 효과 | Park 1999 ECS (원문 확인) |
| ITRS 기준 구조 | "500 µm square array, 50% area density"(erosion), "100 µm wide feature"(dishing), "80% area density" 최대폭 글로벌 | 로드맵 요구치의 기준 구조 | ITRS 2007 Interconnect Table INTC2a/2b |

공통 설계 원리(Park 1998·US7197726 종합): dishing은 **선폭**, erosion은 **밀도와 oxide 스페이스**로 자극하므로
두 축을 독립으로 스윕하는 pitch(밀도 고정)·density(피치 고정) 마스크 쌍이 기본이고, 전기 구조는 스네이크/서펜타인으로
저항을 키워 분해능을 올린다. Cu의 interaction distance가 50–100 µm(Park 1998) ~ 수백 µm(US7197726)로 oxide의
3–5 mm보다 훨씬 짧아([[pattern-dependent-dishing-erosion]] §4) 구조물이 mm급으로 클 필요는 없다.

## 3. 측정법과 기기

- **접촉식 프로파일러(stylus/HRP)**: dishing·step의 기본 측정. Park 1998: Tencor P10 프로파일로미터로 dishing 측정,
  **AFM으로 검증**; Pan 1999: HRP(High Resolution Profiler)로 100 µm 트렌치·5 µm 어레이 스캔(필드면=0). KLA HRP-260
  제품자료: 2D/3D 스텝 nm~327 µm, long-scan 모드로 "copper CMP dishing and erosion", DuraSharp 스타일러스로
  dishing/erosion/recess(벤더 페이지, 2차). Ortleb 2008(HRP-350): 검색 스니펫상 2 µm/s, 200 Hz, 10 nm 점간격
  (**미검증**). Bruker Dektak XTL 제품자료도 "CMP dishing, erosion, and roll off amount (ROA)"를 항목으로 명시(2차).
- **광학 두께계**: erosion(투명 oxide 잔여두께)은 프로파일이 아니라 두께로 잰다 — Park 1998: Tencor UV1250, SEM으로
  선폭·oxide 두께 교차검증. 원리는 [[wafer-metrology-thickness-methods]] §2–3.
- **전기 측정**: Kelvin 4점(IBM 특허·Pan 루프), 2점 서펜타인(IBM erosion monitor — 저항이 커서 접촉저항 무시),
  van der Pauw(Pan). 두께 ∝ 전도도 = 1/저항. 장점: 불투명 금속 두께를 비파괴로 대량 측정; 단점: 배리어 잔류 시
  무효(Pan), 선폭이 매우 작으면 리소/배리어 효과가 지배(US7197726).
- **AFM**: 미세선폭(sub-µm) dishing·EOE의 참조 측정. 스캔 크기 의존성 주의는
  [[wafer-surface-roughness-afm-scan-scale-dependence]]와 동일 원리(조도 성분이 섞임).
- **웨이퍼 기하(ROA)**: 스타일러스 또는 단일점 광학 프로브, 8방위(45° 간격) 평균(US9829310); 상용 기하 측정기(KLA
  WaferSight 등)가 ROA를 내장 계산(US10600634).

## 4. 패턴 의존성 — 판정 기준을 세울 때 알아야 할 경향

- **dishing ↑ with 선폭**(Park 1998 Fig.4a·5; Steigerwald 1994 초록) — 고정 밀도에서 피치가 크면 dishing↑.
  Boning 1999 MRS는 최대 dishing d_max가 선폭의 함수라고 "conjecture"(Fig.14) — 함수형은 **미확정**.
- **erosion ↑ with 밀도**(Park 1998 Fig.7; Steigerwald 초록), 그리고 **작은 oxide 스페이스에서 급증**(Park Fig.6,
  Fayolle 1997과 일치·Steigerwald와는 상이). **break point = oxide 스페이스 ≈100 µm**: 250 µm 피치 마스크에서
  밀도 60% 부근, 50% 밀도 피치 마스크에서 피치 ≈200 µm. 이보다 넓은 스페이스는 패드 하중을 지지해 erosion이
  작고 dishing이 크며, 좁으면 oxide 가속연마로 erosion↑·dishing↓(밀도 60–70%에서 dishing 최대 후 급락).
- **총 정규화 Cu 손실 ∝ log(피치)** (50% 밀도, 큰 피치 영역, Park Fig.8) — 정규화 데이터라 절대값 **미확보**.
- **시간거동**: Pan 1999(5 µm 50%): "copper dishing reached a constant value quickly after the CMP reached barrier,
  while oxide erosion continued to increase as the overpolish was increased"(W CMP와 동일). Tugbawa 2001 CMP-MIC
  (mtlsites.mit.edu/researchgroups/Metrology/PAPERS/Tugbawa-CMPMIC2001.pdf, 원문 확인): 1단계에서 dishing은
  증가 후 **포화**, erosion은 계속 증가; 2단계(유전체 rate > Cu rate 슬러리)에서는 dishing이 **감소**하고 erosion은
  계속 증가 — 즉 스펙은 dishing과 erosion을 **따로** 잡아야 하고 overpolish에 대한 민감도가 다르다.
- **공정 파라미터**: 경향(선폭·밀도 의존)은 조건에 무관하게 같고, 절대량은 down force·속도·multistep에 따라 곡선이
  평행이동(Park 1998; Stavreva et al.과 상이). Pan 1999: overpolish +10% → Cu 손실 +1000 Å(vdP) →
  "overpolish time would need to be controlled to within a few percent".

## 5. 판정 스펙 예시(nm) — 문헌·로드맵에서 확인된 수치

**ITRS 2007 Interconnect, Table INTC2a/2b (semiconductors.org PDF 원문 확인, papers/itrs2007-interconnect.pdf)**

| 항목(원문 행 이름) | 2007 | 2010 | 2013 | 2015 | 2022 |
|---|---|---|---|---|---|
| Cu thinning at minimum pitch due to erosion (nm), **10% × height**, 50% area density, 500 µm square array | 12 | 8 | 6 | 5 | (long-term 표 별도) |
| Cu thinning global wiring due to dishing (nm), **100 µm wide feature** | 24 | 16 | 12 | 10 | 5 |
| Cu thinning of maximum width global wiring due to dishing and erosion (nm), 10% × height, 80% area density | 230 | 240 | 250 | 260 | 290 |

- 규칙의 실체: erosion 행은 **배선높이(반피치×A/R)의 10%**를 정수 반올림한 값 — §6(A)에서 9개 연도 전부 ±0.5 nm
  이내로 재현. 즉 ITRS의 판정 기준은 절대 nm가 아니라 **"interconnect height의 10%"라는 비율 규칙**이고, 기준
  구조(500 µm 정사각 어레이, 50% 밀도 / 100 µm 광폭선 / 80% 밀도 최대폭)를 함께 명시한다. 글로벌 최대폭 행은
  글로벌 배선 치수 행을 이 세션에서 추출하지 못해 **재현 미시도**.
- ITRS 본문: "For copper CMP, minimization of erosion and dishing will be necessary to meet performance needs as the
  wiring thickness is scaled." 검색 스니펫의 "총 스텝하이트 <10 nm(22 nm 노드 이후)"는 출처 문서를 특정 못해
  **미검증**.
- **실측 오더(1999)**: Pan 1999 — 최적 overpolish에서 100 µm 트렌치 dishing ≈500 Å(50 nm); 목표 Cu 두께 ≈5000 Å;
  제어 실패 시 손실이 목표의 50%까지; 5 µm 피치 90% 밀도·40% overpolish에서 총손실 ≈70%(erosion 지배).
  §6(E): 이 50 nm는 ITRS-2007의 100 µm 요구치 24 nm의 2.08배 — 8년 사이 요구치가 절반 이하로 강화됐음을
  두 1차 문서로 대조.
- **STI**: MRS99는 STI를 oxide dishing·nitride erosion으로 같은 틀에 두고 nitride 가속 erosion을 미해결로 남김
  (원문). 검색 스니펫의 "필드폭 5 µm 이하 ≈0 nm → 4 mm에서 200 nm"(Solid State Technology 계열 기사로 추정)는
  출처 문서를 확보 못해 **미검증**; Chang 2005 MRS "A Dishing Model for STI CMP" https://doi.org/10.1557/proc-867-w5.5 는
  서지만 확인.
- **잔류 금속**: 수치 스펙이 아니라 0 허용(전기 단락·다음 층 결함, Pan Fig.10: M1 과도 dishing → M2 CMP 후 표면
  금속 잔류). 판정은 결함검사/전기 테스트.

## 6. Python 재현 — 정의식·로드맵 규칙·알고리즘·규약 의존성

```python verify
import numpy as np

# ---------- (A) ITRS 2007 Table INTC2a: erosion 허용치 = 10% × 배선높이 재현 ----------
years      = [2007,2008,2009,2010,2011,2012,2013,2014,2015]
m1_pitch   = np.array([136,118,104, 90, 80, 72, 64, 56, 50], float)   # Metal 1 wiring pitch [nm]
m1_ar      = np.array([1.7,1.8,1.8,1.8,1.8,1.8,1.9,1.9,1.9])          # Metal 1 A/R (for Cu)
itrs_eros  = np.array([ 12, 11,  9,  8,  7,  6,  6,  5,  5], float)   # "Cu thinning at min pitch due to erosion (nm), 10%×height, 50% density, 500µm square array"
height     = (m1_pitch/2.0) * m1_ar          # 배선높이 = 반피치(선폭) × A/R
calc_eros  = 0.10 * height
diff       = calc_eros - itrs_eros
print("[A] year  pitch  A/R  height(nm)  10%h  ITRS  diff")
for y,p,a,h,c,i,d in zip(years,m1_pitch,m1_ar,height,calc_eros,itrs_eros,diff):
    print(f"    {y}  {p:5.0f}  {a:.1f}  {h:7.1f}   {c:5.2f}  {i:4.0f}  {d:+.2f}")
assert np.all(np.abs(diff) <= 0.5+1e-9), diff   # 정수 반올림 이내(±0.5 nm)이면 "10%×높이" 규칙 재현
print(f"    → 9개 연도 전부 |차이|≤0.5 nm (max {np.abs(diff).max():.2f} nm): ITRS erosion 행은 0.1×(반피치×A/R)의 반올림")

# ---------- (B) IBM US5723874 erosion monitor 표: space ratio 정의 = oxide폭/pitch, 패턴밀도 = 1−space ratio ----------
# (pitch µm, space ratio %, oxide width µm, wire width µm)  — 특허 표 그대로
ibm = [(2.0,60,1.2,0.8),(2.0,50,1.0,1.0),(2.0,40,0.8,1.2),(2.0,30,0.6,1.4),
       (1.8,61.1,1.1,0.7),(1.8,50,0.9,0.9),(1.8,38.9,0.7,1.1),(1.4,57.1,0.8,0.6),
       (1.6,62.5,1.0,0.6),(1.6,50,0.8,0.8),(1.6,37.5,0.6,1.0)]
for pitch,sr,ox,wire in ibm:
    assert abs(ox/pitch*100 - sr) < 0.06, (pitch,sr,ox)       # space ratio = oxide/pitch (특허 정의)
    assert abs((ox+wire) - pitch) < 1e-9, (pitch,ox,wire)      # oxide + wire = pitch
    rho = wire/pitch                                           # Park VMIC98 정의: density = line width / pitch
    assert abs(rho - (1 - sr/100)) < 6e-4, (rho, sr)           # 패턴밀도 = 1 − space ratio
print(f"[B] IBM 특허 표 11행: space ratio=oxide/pitch, 패턴밀도(Park 정의)=1−space ratio 전부 <0.06%p 일치 (밀도 {min(w/p for p,_,_,w in ibm)*100:.1f}–{max(w/p for p,_,_,w in ibm)*100:.1f}%)")

# ---------- (C) ISO 5436-1형 스텝하이트 최소제곱 (Taylor Hobson: Z = aX + b + hδ, step = 2h) ----------
rng = np.random.default_rng(1)
x = np.linspace(0, 200.0, 2001)             # µm, 200 µm 스캔
h_true = 50.0                               # nm — dishing 스케일의 합성 step
delta = np.where((x>70)&(x<130), -1.0, +1.0)  # 가운데 60 µm 오목(라인), 양옆 볼록(필드)  ← Cu dishing 프로파일 모사
z = 1.0*x + 5.0 + (h_true/2)*delta + rng.normal(0, 0.3, x.size)   # 기울기 1 nm/µm(레벨링 오차) + 0.3 nm 노이즈
# 전이부 근방 무시(ISO 5436-1 정신: 스텝 경계 인접 영역 제외) — 경계 ±5 µm 제외
mask = ~(((x>65)&(x<75)) | ((x>125)&(x<135)))
A = np.column_stack([x[mask], np.ones(mask.sum()), delta[mask]])
a,b,h = np.linalg.lstsq(A, z[mask], rcond=None)[0]
step_fit = 2*h
assert abs(step_fit - h_true) < 1.0, step_fit
print(f"[C] LS 스텝 회수: {step_fit:.2f} nm vs 참값 {h_true} nm (기울기 {a:.3f} nm/µm 동시 추정) — 오차 {abs(step_fit-h_true):.2f} nm")

# Taylor Hobson 예시: 9 µm step + 2 µm 기판 곡률 → 단순 직선피팅이면 "약 10%" 불확도
xs = np.linspace(0, 10.0, 4001)             # mm
sag = 2.0e3 * (1 - (2*(xs-5)/10)**2)        # nm, 포물선 곡률 2 µm sag
dl  = np.where((xs>4)&(xs<6), 1.0, 0.0)     # 가운데 2 mm 위 9 µm step
zs  = sag + 9.0e3*dl
# 단순법: 필드영역 전체에 직선 1개 피팅 → step = mean(step영역) − line
mf = dl==0
p = np.polyfit(xs[mf], zs[mf], 1)
naive = np.mean(zs[~mf] - np.polyval(p, xs[~mf]))
err_naive = abs(naive-9.0e3)/9.0e3
print(f"[C'] 곡률 2 µm 기판 위 9 µm step: 단순 직선피팅 step={naive/1e3:.2f} µm, 오차 {err_naive*100:.1f}% (Taylor Hobson '약 10%'와 대조)")
assert 0.03 < err_naive < 0.30, err_naive   # 같은 자릿수(수~수십 %)면 '곡률 미제거 시 ~10%' 서술 재현으로 간주

# ---------- (D) ROA 정의(US10600634 vs US9829310) — 규약 의존성 ----------
R = 150.0                                                   # 300 mm 웨이퍼 반경 [mm]
f1,f2,f3 = 0.827, 0.933, 0.987                              # SunEdison 특허 청구항/본문 비율
r1,r2,r3 = f1*R, f2*R, f3*R
assert abs(r2-140) < 0.1 and abs(r3-148) < 0.1, (r2,r3)     # 본문 "140 mm", "148 mm"와 일치
mismatch_P1 = r1 - 120.0                                    # 본문 "120 mm"과 82.7%×150 의 불일치
print(f"[D] ROA 기준점: 93.3%→{r2:.1f} mm, 98.7%→{r3:.1f} mm (본문 140/148 mm 일치); 82.7%→{r1:.2f} mm vs 본문 120 mm → {mismatch_P1:+.1f} mm 불일치(특허 내부 모순, 원인 미상)")
assert abs(mismatch_P1) > 3.0                               # 불일치를 숨기지 않고 assert로 고정

# 합성 두께 프로파일: 평탄 + 엣지 6 mm에서 포물선 롤오프(엣지에서 −1000 nm)
r = np.linspace(100, 150, 5001)
t = np.where(r>144, -1000.0*((r-144)/6)**2, 0.0)            # nm, 두께(또는 표면높이) 편차
def roa(rp1, rp2, rp3):
    z1,z2,z3 = np.interp([rp1,rp2,rp3], r, t)
    zref = z1 + (z2-z1)*(rp3-rp1)/(rp2-rp1)                 # 1차 기준선 외삽
    return z3 - zref                                        # 음수 = 롤오프(엣지가 낮음)
roa_sun = roa(120,140,148)                                  # SunEdison: 120/140 → 148 mm
roa_cor = roa(144,147,148)                                  # Corning: 엣지에서 6 mm/3 mm → 같은 148 mm 평가
print(f"    같은 프로파일에서 ROA(SunEdison 120/140/148)={roa_sun:.0f} nm, ROA(Corning 144/147/148)={roa_cor:.0f} nm")
assert roa_sun < 0 and roa_cor < 0                          # 둘 다 롤오프 부호(음수)
assert abs(roa_sun - roa_cor) / abs(roa_sun) > 0.3         # 규약 차이로 30% 이상 다름 → 기준점 명시 없는 ROA는 비교 불가

# ---------- (E) Pan CMP-MIC99 (AMAT/MIT) 실측 오더 vs ITRS 2007 요구치 ----------
pan_dishing_100um_nm   = 500/10          # "approx. 500 Å dishing over a 100 µm trench" (optimum overpolish) → 50 nm
itrs2007_dishing_100um = 24.0            # ITRS 2007 INTC2a "Cu thinning global wiring due to dishing (nm), 100 µm wide feature", 2007년 열
ratio = pan_dishing_100um_nm / itrs2007_dishing_100um
print(f"[E] 1999년 공정 100 µm dishing {pan_dishing_100um_nm:.0f} nm vs ITRS-2007 요구 {itrs2007_dishing_100um:.0f} nm → {ratio:.2f}배 (일치 아님: 8년 뒤 요구치가 절반 이하로 강화)")
assert 1.5 < ratio < 3.0, ratio
pan_total_loss_90pct = 0.70*5000/10      # 90% 밀도, 40% OP: 총손실 ≈ 70% × 5000 Å → nm
pan_extra_op_loss    = 1000/10           # +10% overpolish → +1000 Å Cu loss (vdP 전기측정)
print(f"    90%밀도·40%OP 총 Cu 손실≈{pan_total_loss_90pct:.0f} nm(erosion 지배), overpolish +10%당 손실 +{pan_extra_op_loss:.0f} nm → overpolish 수 % 이내 제어 필요(Pan 결론)")
assert pan_total_loss_90pct > 5*pan_dishing_100um_nm      # 고밀도 어레이 erosion 손실이 광폭선 dishing보다 한 자릿수 크다
```

## 7. 정량 재현 요약

ITRS 2007 erosion 허용치 행(12→5 nm, 2007–2015)을 0.1×(반피치×A/R)로 계산해 9개 연도 전부 0.5 nm 이내로 재현했고(ITRS 2007 Table INTC2a 원문), ISO 5436-1형 최소제곱으로 합성 50 nm 스텝을 0.01 nm 오차로 회수했으며, 곡률 2 µm 기판 위 9 µm 스텝의 단순피팅 오차 8.9%는 Taylor Hobson(Mills, 벤더 튜토리얼)의 "약 10%" 서술과 대조 일치했다.

| 재현 항목 | 계산값 | 문헌 앵커 | 결과 |
|---|---|---|---|
| ITRS erosion 행 = 10%×(반피치×A/R) | max 차이 0.48 nm | ITRS 2007 Table INTC2a 원문 | 9/9 연도 반올림 이내 일치 |
| IBM 특허 erosion monitor 표: space ratio=oxide/pitch, 밀도=1−space ratio | 11행 <0.06%p | US5723874 표 원문 | 정의 항등 확인(Park 밀도정의와 호환) |
| ISO 5436-1형 LS 스텝 회수(기울기 동시추정) | 50.01 nm | 합성 참값 50 nm(Taylor Hobson 식) | 오차 0.01 nm |
| 곡률 미제거 시 단순피팅 오차 | 8.9% | Taylor Hobson "약 10%" | 같은 자릿수(정성 서술의 정량 재현) |
| ROA 기준점 규약(SunEdison 93.3/98.7% → 140/148 mm) | 140.0/148.1 mm | US10600634 본문 | 일치; 82.7%↔120 mm는 4 mm **불일치**(특허 내부 모순) |
| 같은 프로파일의 ROA, 두 규약 | −444 vs −111 nm | US10600634 vs US9829310 규약 | 4배 차이 — 규약 병기 없이는 비교 불가 |
| 1999 실측 100 µm dishing vs ITRS-2007 요구 | 50 vs 24 nm(2.08배) | Pan 1999 / ITRS 2007 | 일치 아님(요구치 강화의 정량) |

(A)(B)(D 앞부분)은 1차 문서의 수치를 상수로 박고 정의식으로 재계산한 것이라 "재현"이다. (C)(C')는 알고리즘의
자기일관성·감도 검증(합성 데이터)이고, (D 뒷부분)(E)는 두 출처를 대조한 것이지 어느 한쪽의 실측을 재현한 것이
아니다. 절대 dishing/erosion nm의 물리 모델 재현은 [[pattern-dependent-dishing-erosion]] §5(정상상태 d_ss)와 같이
캘리브레이션 없이는 **미검증**으로 남는다.

## 8. 남은 미확보·미검증 (정직성 표기)

- ISO 5436-1:2000, SEMI M1/M67/M68/M70/M77/MF1530 **원문 미확보**(유료·Cloudflare) — 스코프·정의는 벤더 자료(Taylor
  Hobson·NIST)와 store 페이지, 특허 인용으로 2차 확인. SEMI M69(2007 preliminary)→M77 승계 여부 미확인.
- Steigerwald 1994(초록만), Fayolle 1997(서지만), Ortleb 2008(초록만), Xie&Boning 2005(스니펫), Fukuda 2012(초록만),
  Lee 2016 EOE(제목만): 본문 **미확보** — 정의·경향만 인용, 이들의 절대 수치는 노트에 넣지 않았다.
- ITRS 글로벌 최대폭 행(230–290 nm) 재현 미시도(글로벌 배선 치수 행 미추출). "총 스텝하이트 <10 nm" 스니펫 **미검증**.
- STI 필드폭-dishing 수치(≈0→200 nm) 출처 미확정 **미검증**. Ortleb HRP 스캔조건(2 µm/s·200 Hz·10 nm) **미검증**.
- Kimura et al. 1999 JJAP(ROA 원류)는 특허 인용으로만 확인(**2차 인용**). US10600634의 82.7%↔120 mm 불일치는 원인 미상.
- Park 1998·Pan 1999 실측은 dishing/erosion을 **정규화**(Park) 또는 Å 그래프(Pan)로만 제시해 표 형태 절대값은 본문
  인용문에 나온 500 Å·1000 Å·70%·5000 Å만 사용했다.

## 9. 자기시험
→ [[../../agents/wafer-metrology/EXAMS.md]] Lv2-2 문항 참조.
