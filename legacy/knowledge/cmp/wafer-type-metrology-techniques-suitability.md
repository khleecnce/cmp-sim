<!-- V2-SECTION: R5-wafer | 공동: R3-pad | 분배완료 2026-09-08 | 근거: metrology, npw, pattern-, ptw, wafer- | 정본: ARCHITECTURE-V2.md §3 -->
# NPW vs PTW에서 측정 기법의 적합성 — 엘립소미터·스타일러스·AFM·XRF: 막질별 적용 한계와 패턴 웨이퍼 제약 (Lv2-2)

> 에이전트: wafer-type Lv2-2 (측정 기법 — 엘립소미터·프로파일러·AFM·XRF의 막질별 적합성과 오차) | 작성일: 2026-09-07
> 선행: [[npw-ptw-test-wafer-fundamentals]] (NPW 49점 체계·PTW 마스크), [[npw-ptw-pattern-effect-gw-physics]] (up/down 영역 분화), [[wafer-metrology-thickness-methods]] (두께 계측 원리 — SE/SR/EC/4PP/XRF 일반론), [[uniformity-metrics-definitions-standards]] (WIWNU 정의)
> 관련: [[wafer-surface-roughness-afm-scan-scale-dependence]] (AFM 스캔 크기 의존성), [[pattern-metrics-dishing-erosion-stepheight]] (dishing/erosion 정의·측정 구조물 — 형제 wafer-metrology 소유, 본 노트는 침범하지 않음)

## 0. 목적과 경계

형제 노트 [[wafer-metrology-thickness-methods]]가 "각 기법이 **어떤 막을** 잴 수 있는가"를 다뤘다면,
이 노트는 wafer-type의 관점에서 "**같은 막이라도 NPW(블랭킷)와 PTW(패턴)에서 왜 쓸 수 있는 기법이
달라지는가**"를 문헌으로 확정한다. 지표 정의(dishing·erosion·step height)는
[[pattern-metrics-dishing-erosion-stepheight]] 소유이므로 재정의하지 않고, 여기서는 **측정 스팟 크기 vs
패턴 피치·측정 패드 크기, 투과 깊이, 탐침 기하** 세 가지 물리적 제약으로 적합성을 정리한다.

핵심 주장(§1–§5에서 근거 제시):
1. NPW에서는 막 전체가 균질하므로 스팟이 커도 되고(엘립소미터 mm급, XRF 40 mm까지), 결과가 "그 막 두께"다.
2. PTW에서는 피처 폭이 0.1–10 µm이고 측정 패드가 통상 100 µm × 100 µm(US7095511, 1차 특허 원문)라,
   스팟이 패드보다 크면 **패턴이 섞인 평균값**이 나와 두께로 해석할 수 없다.
3. 따라서 PTW의 "두께"는 (a) 패드 안에 들어가는 소스팟 광학계, (b) 접촉식 단차(스타일러스/AFM), (c) 전기적 방법
   중 하나로 잰다. XRF처럼 스팟이 mm급인 기법은 PTW에서 **면적가중 평균 두께**만 준다.

## 1. 측정 스팟 vs 패턴 — PTW 제약의 공통 물리

**측정 패드와 피처 크기 (1차, 특허 원문 텍스트 확인)**: Filmetrics의 US7095511 "Method and apparatus for
high-speed thickness mapping of patterned thin films" (freepatentsonline.com/7095511.html 전문 확인)는
제품 웨이퍼가 "**0.1 µm to 10 µm** 폭의 피처로 패턴되어 있고, 이 영역은 막 특성 측정에 부적합하므로 별도의
측정 pad를 두는데, 면적 손실을 줄이기 위해 **통상 약 100 µm × 100 µm**로 만든다. 이 작은 패드 크기가
측정 스팟 크기와 패드 위치 탐색 양쪽에서 장비에 도전이 된다"고 명시한다. 같은 특허의 실시예 스팟은
**약 50 µm × 50 µm**다.

**소스팟 엘립소미터의 실제 한계 (1차, 특허 원문)**: KLA-Tencor US9574992 "Single wavelength ellipsometry with
improved spot size capability" (freepatentsonline.com/9574992.html)는 **40 µm × 40 µm 타깃**에서 pupil stop/
field stop로 타깃 밖(패턴)에서 반사된 빛을 차단해야 tool-to-tool 매칭 **0.02 Å**를 달성한다고 서술한다 —
즉 소스팟 SE의 정확도를 제한하는 것은 광학계 자체가 아니라 **타깃 가장자리 회절과 패턴 혼입광**이다
(특허 eq.(1)–(3): 총 조도 I = I_in + I_out + I_int, 간섭항 I_int가 오염 신호).

**경사 입사에 의한 타원 스팟**: 엘립소미터는 비수직 입사(통상 70°)라 원형 빔이 표면에서 1/cos θ 배로
늘어난다. 이 기하는 자명하며 §7 verify (B)에서 계산한다 — 50 µm 빔이 70°에서 **146 µm** 장축이 되어
100 µm 패드를 벗어난다(1차 수치 50 µm·100 µm는 US7095511, 계산은 본 노트).

**XRF 스팟**: Malvern Panalytical 2830 ZT 웨이퍼 XRF 응용노트(Cu/TaNx 스택, 2013, 기업자료 **2차**)는 스팟
직경 **40 mm**, 측정시간 100 s를 명시 — 이는 NPW 전용 조건이고 PTW에서는 다이 여러 개가 스팟에 들어간다.

## 2. 분광 엘립소메트리(SE) — 투명 유전체 전용, 금속 불가, PTW에서는 소스팟+패드 필요

### 2.1 원리와 두께 정보의 출처
ρ = r_p/r_s = tan Ψ · e^{iΔ}. 단일막(공기/막/기판)에서 r = (r₀₁ + r₁₂e^{−2iβ})/(1 + r₀₁r₁₂e^{−2iβ}),
β = 2π(d/λ)·n₁cos θ₁ — 두께 d는 위상 β를 통해서만 들어오며, **막이 투명해야(k₁≈0) 기판 반사 r₁₂가 살아
남아 간섭이 생긴다**. Garcia-Caurel, De Martino, Gaston, Yan(2013, "Application of Spectroscopic Ellipsometry and
Mueller Ellipsometry to Optical Characterization," arxiv.org/abs/1210.1076 — **1차, 원문 PDF 확보**,
`papers/garcia-caurel2013-se-mueller-review-arxiv1210.1076.pdf`)의 서술: SE는 "transparent or low absorbing
thin films with thickness ranging from less than a nanometer to several micrometers"를 특성화하며, "NIR은
가시광에서 강하게 흡수하는 재료의 두께를 정하는 데 필요"하고, Δ가 0° 또는 180° 근처(두꺼운 투명막·고흡수
시료)에서 정확도가 떨어진다(회전 편광자형의 |Δ| 문제). 격자(패턴) 시료는 표준 SE가 아니라 **RCWA로 피팅하는
Mueller 엘립소메트리/스캐터로메트리**로 다룬다(같은 논문 Fig.13, RCWA 시뮬레이션 피팅 서술).

### 2.2 막질별 적합성
- **SiO₂/TEOS(ILD·STI), SiN**: 투명 → 1순위. 원리·SE vs SR 비교는 [[wafer-metrology-thickness-methods]] §2–3.
  Δ의 두께 주기 d_period = λ/(2√(n₁²−sin²θ)) — 632.8 nm·70°·SiO₂(n=1.457)에서 **284 nm** (§7 verify (B)에서
  Fresnel 모델로 자기일관 확인). 주기를 넘는 두꺼운 막은 단파장 단독으로는 모호하고 분광(다파장)이 필요 —
  Nanofilm Surface Analysis 응용노트(2008, "SiO2 — Thickness measurement of SiO2 layer on Si-wafer",
  irida.es/docs/aplicaciones/elipsometria/Application_note_SiO2.pdf, 기업자료 **2차**, 원문 PDF 확보)도
  30–90 nm 범위 맵핑에서 532 nm 대신 781 nm를 골라 Δ–두께 관계의 모호성을 피했다고 서술.
- **Poly-Si**: 반투명 — 흡수 적은 장파장 쪽으로 옮겨 측정([[wafer-metrology-thickness-methods]] §2, Horiba 2차).
- **Cu, W (불투명 금속)**: HORIBA "Advantages of spectroscopic ellipsometry"(horiba.com, 2차·원문 확인) —
  "optically opaque samples, such as metal films greater than about **50 nm**, ellipsometry can only determine
  optical properties and NOT thickness"; J.A. Woollam FAQ(jawoollam.com, 2차·원문 확인) — "absorbing film must be
  thin enough (typically < 50 nm)". 물리적 근거는 침투깊이: Cu의 소광계수 k=3.408 (632.8 nm, Johnson & Christy
  1972, doi.org/10.1103/PhysRevB.6.4370 — refractiveindex.info CC0 데이터파일 `papers/optical_constants/
  main_Cu_nk_Johnson.yml`에서 보간, 1차 논문 원문은 미확보·데이터 테이블만 확인)에서 강도 침투깊이
  d_p = λ/(4πk) ≈ **14.8 nm** → 50 nm 막을 왕복하면 기판 정보가 e^{−100/14.8} ≈ 0.1%로 감쇠(§7 verify (A)).
  CMP 후 Cu 배선(수백 nm)·W 플러그는 **SE로 두께 측정 불가** — EC/4PP/XRF로 간다.
  Stenzel et al.(2019, *Coatings* 9(3):181, doi.org/10.3390/coatings9030181, CC-BY)은 10–60 nm Cu·Au 박막을
  투과/반사 분광으로 특성화 — 얇은 금속막 광학상수는 두께 의존(Drude 감쇠 증가)이라 초박막에서도 n,k,d 동시
  피팅이 필요함을 시사(초록만 확인, PDF는 mdpi 봇차단으로 **본문 미확보**).

### 2.3 NPW→PTW 전환 시 제약
| 제약 | NPW | PTW |
|---|---|---|
| 스팟 크기 | mm급 스팟 무방(FilmTek SE 3 mm, Bruker 제품 페이지 2차) | 패드 100 µm 안에 타원 스팟(장축 = 빔/cos θ)이 들어가야 함 — 50 µm 빔 70° → 146 µm(초과), 25 µm 마이크로스팟 → 73 µm |
| 혼입광 | 없음 | 패드 밖 패턴 반사·가장자리 회절이 Δ를 오염(US9574992 eq.1–3) |
| 모델 | 단일막 Fresnel | 패턴이 스팟에 들어오면 유효매질 또는 RCWA(Garcia-Caurel et al. 2013) — 두께 단독 피팅 불가 |
| 측정 대상 | 막 두께 그 자체 | 패드 = 국소 넓은 영역(down/up 중 하나) → 패턴 밀도 효과가 평균된 값이 아니라 **특정 밀도 영역의 값**임을 메타데이터에 남겨야 함(§6.2 이관) |

이미징 엘립소미터(Nanofilm EP³, 2차)는 "classic SE의 마이크로스팟이 최대 약 **40 µm** 측면분해능, EP³는
2 µm ROI"라고 서술 — 패드 없이 PTW 국소 두께를 재는 대안이나 학술 검증은 이 세션에서 확보 못 함(**2차**).

## 3. 스타일러스 프로파일러 — 단차(step)만, 두께 절대값 불가, 트렌치 폭 < 팁 직경이면 바닥 도달 불가

**1차 출처**: Vorburger, Renegar, Zheng, Song, Soons, Silver, "NIST Surface Roughness and Step Height Calibrations,
Measurement Conditions and Sources of Uncertainty" (NIST, `papers/nist-surface-roughness-step-height-calibrations.pdf`,
**원문 PDF 확보**; 발행연도 미기재, 참고문헌 최신이 2014 → 2014년 이후 문서로 추정, DOI 없음).
- 스타일러스 반경 **1.52 µm ± 0.15 µm (k=2)**, 횡 샘플링 간격 0.125 µm, 조도 필터 λc 0.8 mm·λs 2.5 µm(ASME B46.1-2009).
- 조도 불확도 성분(5): "**팁 반경보다 작은 공간파장은 감도가 줄거나 아예 측정되지 않는다**". 단차(step height)
  측정에서는 성분 5·6(수평분해능·잡음)이 오프셋을 만들지 않고 랜덤 변동 s에만 기여.
- 단차 알고리즘: 단측 스텝은 양쪽 최소제곱 직선을 스텝 가장자리로 외삽(NIST 알고리즘), 또는 ISO 5436-1:2000.
- Table 3(Talystep 기준) 측정계 표준불확도 u(I): 마스터 H=0.02937 µm일 때 **0.023·X**, H=0.3024 µm → 0.0046·X,
  H=1.0157 µm → 0.0025·X (X = 측정 단차). 즉 30 nm급 단차의 상대 표준불확도 ≈ 2.3%, 1 µm급 ≈ 0.25%
  (§7 verify (D)에서 절대값 환산).
- 팁 크기 효과(Renegar, Soons, Muralikrishnan, Villarrubia, Zheng, Vorburger, Song 2012, ICSM3; NIST 게시 초록만
  확인, **본문 미확보**): 직사각 프로파일에서 peak 폭 > valley 폭이면 팁이 클수록 Ra가 작게, 반대면 크게 측정 —
  **오차 부호가 패턴 기하(라인/스페이스 비)에 의존**한다. CMP PTW의 라인/스페이스 어레이에 그대로 적용되는 경고.

**막질**: 접촉식이라 SiO₂/SiN/poly/Cu/W 모두 무관하게 잰다. 단, 재는 것은 **표면 높이차**이지 두께가 아니다 —
PTW의 dishing(금속 vs 주변 산화막 높이차)·erosion(어레이 vs 필드 높이차)·step height에는 1순위,
NPW의 "잔막 두께"에는 부적합(기준면이 없다; 에지 마스킹 후 에칭 스텝을 만들면 가능하나 파괴적).

**PTW 제약(기하, 본 노트 계산)**: 반경 R 팁은 폭 w < 2R 트렌치 바닥에 닿지 못하고(원뿔각 무시 시), 바닥에
닿더라도 w−2R 구간만 진짜 바닥이다. R=1.52 µm(NIST) → **w < 3.04 µm 트렌치는 깊이가 과소평가**. US7095511의
피처 폭 0.1–10 µm 중 하위 대부분이 여기 해당 → 스타일러스 dishing 측정은 **넓은 패드·큰 피치 어레이에서만
유효**하고 sub-µm 구조는 AFM(§4)이 참조 측정이 된다([[pattern-metrics-dishing-erosion-stepheight]] §3의
"Park 1998: Tencor P10 프로파일 + AFM 검증"과 일관).

## 4. AFM — nm 조도·sub-µm 국소 단차, 처리량 최저, 픽셀 피치·팁 반경이 오차 지배

**1차 출처**: Ahn, Choi, Miller, Song, No, Hong (2019), "Measurement Anomaly of Step Width in Calibration Grating
using Atomic Force Microscopy," arxiv.org/abs/1909.09508 (**원문 PDF 확보**, `papers/ahn2019-afm-step-width-anomaly-arxiv1909.09508.pdf`).
- 실리콘 격자를 픽셀 피치 3.91–625 nm(스캔 1 µm×1 µm ~ 40 µm×40 µm, 64²~1024² 픽셀)로 스캔. 측정 스텝 폭이
  **1300 nm → 108 nm**로, 스텝 높이는 172 → 184 nm로 변함. SEM 기준값 폭 **115.9 ± 10.4 nm**, 높이 **187.3 ± 6.2 nm**
  — 3.91 nm 피치에서만 일치. "스텝 폭에 **최소 4픽셀**"이 필요하다는 결론(팁 stick-slip/dragging). 팁 반경 30 nm·
  높이 12.5 µm는 최대 30 nm 차이만 설명 — 실제 71.4 nm 차이의 주원인은 픽셀 피치. **RMS 조도는 피치에 둔감**
  (Ahn et al. 2019 초록 수치 그대로: 77.6 nm로 수렴, 변동 <1 nm).
- 함의: AFM 높이(단차·dishing 깊이)는 픽셀 피치에 비교적 강건(172→184 nm, SEM 대비 최대 8% 과소)하지만 **폭·형상은
  피치와 팁에 매우 민감**. PTW에서 sub-µm 라인 dishing 프로파일을 AFM으로 잴 때 스캔 크기를 키우면 픽셀 피치가
  커져(40 µm/512 px ≈ 78 nm) 폭이 수배 과대 측정될 수 있다 — §7 verify (C).

**NPW에서의 역할**: 두께 정보 없음. 조도(Ra·Rq) 전용 — 스캔 크기 의존성은 [[wafer-surface-roughness-afm-scan-scale-dependence]].
**PTW에서의 역할**: sub-µm dishing·edge-over-erosion의 **참조 측정**(형제 노트 §3). 스캔 범위 수십 µm라 다이 맵은 불가.
막질: 전 막질 가능(접촉/탭핑), 단 Cu는 표면 산화·부식이 조도에 섞인다(정성, 이 세션 1차 미확보 → **추정**).

## 5. XRF — 금속막 두께·조성, 스팟 mm급 → NPW 전용, PTW에선 면적가중 평균

### 5.1 원리와 지수 법칙
X선 여기 → 원소 고유 형광선 강도. 막 자체의 형광은 I = I_∞[1 − exp(−μ̄ρt)] (μ̄: 입사·형광 경로를 합친 유효
질량감쇠계수, ρ: 밀도, t: 두께)로 포화하고, **기판(하지층) 형광은 막을 지나며 I/I₀ = exp[−(μ/ρ)·ρt]로 감쇠**한다.
후자의 형태는 NANO CMS US9644956 "Method and apparatus for measuring thin film thickness using x-ray"
(freepatentsonline.com/9644956.html, **1차 특허 원문**, claim 9: "I/Io = exp[−(μ/ρ)X]")에 그대로 있고, 다층
금속(Au/Ni/Cu)의 동시 두께 결정은 Bell Labs US4162528 "X-ray-fluorescence measurement of thin film thicknesses"
(1979, freepatentsonline.com/4162528.html, **1차**, 참고문헌으로 Bertin 1975 *Principles and Practice of X-ray
Spectrometric Analysis* pp.811–820 인용)이 "AuLα∞" 등 포화강도 파라미터와 기지 두께 표준시료 검량으로 정식화.
- 질량감쇠계수(1차, NIST XCOM 표 physics.nist.gov/PhysRefData/XrayMassCoef/ElemTab/z29.html·z74.html 원문 확인):
  Cu μ/ρ = **52.55 cm²/g @ 8 keV**(Cu Kα 8.05 keV 인접), W μ/ρ = **170.5 cm²/g @ 8 keV**.
  → Cu(ρ=8.96 g/cm³) 1/μ ≈ 21 µm, W(ρ=19.3) 1/μ ≈ 3.0 µm. CMP 후 Cu ≤1.5 µm는 μt ≤ 0.07로 **선형 영역**
  (비선형 오차 <3.5%, §7 verify (E)); W 플러그 수백 nm도 선형. 단 실제 μ̄는 입사각·검출각 기하로 커지므로 위
  값은 **하한**(정직 표기).
- Malvern Panalytical 응용노트(2013, 2차): Cu-Kβ로 Cu, Ta-Lα로 TaNx, N-Kα로 조성 x 동시 측정; 30회 반복
  Cu 787.6 Å에서 RMS 0.140 Å(0.018%), TaNx 498.0 Å에서 0.123 Å — 다층 스택 분리 정밀도의 **2차 수치**. Cu 단독은
  150,000 Å(15 µm)까지, 조성까지 원하면 Cu ≤1,200 Å 제한(Ta-L/Cu-K 중첩·N-K 감쇠 때문, 2차).

### 5.2 막질·웨이퍼 유형별 적합성
- **Cu, W, Ta/TaN 배리어**: 1순위(조성+두께). **SiO₂/SiN/poly**: Si·O·N은 저에너지 형광이라 기판 Si와 구분 불가
  또는 감도 낮음 → 부적합(정성; 이 세션 1차 미확보 → **추정**).
- **NPW**: 40 mm 스팟(2차)으로 49점 맵 가능. **PTW**: 스팟 안 여러 다이가 평균되어 측정 강도 ∝ Σ(면적분율 × 두께)
  = **패턴밀도 가중 평균 금속 두께** — 이는 NPW 두께와 물리량이 다르며, dishing/erosion으로 국소 두께가 달라도
  평균은 둔감. μXRF(수십 µm 스팟)면 패드 측정 가능하나 1차 문헌 미확보(Appl. Surf. Sci. 2005 "Determination of layer
  thickness with μXRF"는 제목만 확인, DOI 미확인 → **미검증**).

## 6. 종합 — 막질 × 기법 × 웨이퍼 유형 적합성 표 (§1–§5 근거의 종합, 표 자체는 본 노트 판단)

### 6.1 막질별
| 막질 | SE | 스타일러스 | AFM | XRF |
|---|---|---|---|---|
| SiO₂/TEOS | ◎ 두께·n (투명) | △ 단차만 | △ 조도·국소단차 | ✗ (경원소) |
| SiN | ◎ (흡수 시 파장 이동) | △ | △ | ✗ |
| Poly-Si | ○ (장파장) | △ | △ | ✗ |
| Cu | ✗ (>50 nm 불투명) | △ 단차(dishing) | ○ sub-µm dishing | ◎ 두께·다층 |
| W | ✗ | △ 단차(recess) | ○ | ◎ (1/μ≈3 µm, 선형) |

### 6.2 웨이퍼 유형별 (핵심 결론)
| 기법 | NPW | PTW | PTW에서의 제약 원인 |
|---|---|---|---|
| SE | ◎ 대스팟 OK, 49점 맵 | ○ 소스팟(≤25 µm 빔)+100 µm 패드 필요 | 타원 스팟(1/cos θ), 패드 밖 혼입광·회절(US9574992), 격자면 RCWA 필요 |
| 스타일러스 | △ 두께 불가(단차만) | ◎ dishing/erosion/step(넓은 구조) | 팁 R=1.52 µm → w<3 µm 트렌치 바닥 미도달, 팁 크기 오차 부호가 L/S비에 의존 |
| AFM | △ 조도 전용 | ◎ sub-µm 참조 측정 | 픽셀 피치(≥4 px/폭), 팁 반경, 스캔 범위 ≤ 수십 µm(다이 맵 불가) |
| XRF | ◎ 금속 두께·조성 | △ 면적가중 평균만 | 스팟 40 mm ≫ 다이, 국소 두께 분리 불가 |

**전이 규칙(Lv3-2 예고)**: NPW의 SE/XRF 두께와 PTW의 스타일러스/AFM 단차는 **물리량이 다르다**(두께 vs 높이차).
둘을 잇는 최소 공통 데이터는 "PTW 패드(밀도 명시)에서의 소스팟 SE 두께"이며, 메타데이터 스키마(Cal-1)에는
`spot_size`, `pad_size`, `local_density`, `probe_radius`, `pixel_pitch`를 필수 필드로 넣어야 한다(PROFILE 구현 요청).

## 7. Python 재현 — 침투깊이·스팟 기하·AFM 픽셀 규칙·NIST 불확도·XRF 선형성

재현 요약(한 줄): Cu 침투깊이 14.8 nm(Johnson & Christy 1972 k=3.408 기반)로 50 nm 막 왕복 감쇠 0.1%가 Horiba/Woollam 2차 문턱 "약 50 nm"와 대조 일치; AFM 스텝 높이 184 nm는 SEM 187.3 nm와 2% 이내 재현(Ahn et al. 2019); XRF Cu 1 µm 비선형 2.3%는 NIST XCOM 52.55 cm²/g에서 재현.

```python verify
import math, cmath

# ---------- (A) SE 금속 불투명 한계: Cu 침투깊이 vs "약 50 nm" 2차 문턱 ----------
lam = 632.8                       # nm, He-Ne
k_cu = 3.4081                     # Johnson & Christy 1972 (doi.org/10.1103/PhysRevB.6.4370), refractiveindex.info 보간값
d_p = lam / (4 * math.pi * k_cu)  # 강도 침투깊이 (1/e)
assert abs(d_p - 14.8) < 0.2, d_p
t_opaque = 50.0                   # nm, Horiba/Woollam "about 50 nm" (2차)
substrate_fraction = math.exp(-2 * t_opaque / d_p)   # 왕복 감쇠
assert substrate_fraction < 0.002, substrate_fraction  # 50 nm에서 기판 정보 <0.2% → "두께 불가" 문턱과 정합
# 반대로 10 nm Cu면 왕복 후 26% 남음 → 얇은 금속막은 SE 두께 측정 가능(Woollam "<50 nm" 서술과 방향 일치)
assert 0.2 < math.exp(-2 * 10 / d_p) < 0.3

# ---------- (B) SiO2/Si Fresnel 단일막 모델: Δ 주기 자기일관 + 스팟 타원 ----------
th = math.radians(70.0)
n_air = 1.0
n_ox = 1.457                          # SiO2 @632.8 nm (Malitson 1965 Sellmeier, doi.org/10.1364/JOSA.55.001205)
n_si = complex(3.8827, -0.0196)       # Si @632.8 nm (Aspnes & Studna 1983, doi.org/10.1103/PhysRevB.27.985), n - ik 규약
def psi_delta(d_nm):
    s0, c0 = math.sin(th), math.cos(th)
    c1 = cmath.sqrt(1 - (n_air * s0 / n_ox) ** 2)
    c2 = cmath.sqrt(1 - (n_air * s0 / n_si) ** 2)
    rp01 = (n_ox * c0 - n_air * c1) / (n_ox * c0 + n_air * c1)
    rs01 = (n_air * c0 - n_ox * c1) / (n_air * c0 + n_ox * c1)
    rp12 = (n_si * c1 - n_ox * c2) / (n_si * c1 + n_ox * c2)
    rs12 = (n_ox * c1 - n_si * c2) / (n_ox * c1 + n_si * c2)
    e = cmath.exp(-2j * 2 * math.pi * d_nm / lam * n_ox * c1)
    rp = (rp01 + rp12 * e) / (1 + rp01 * rp12 * e)
    rs = (rs01 + rs12 * e) / (1 + rs01 * rs12 * e)
    rho = rp / rs
    return math.degrees(math.atan(abs(rho))), math.degrees(cmath.phase(rho)) % 360
period = lam / (2 * math.sqrt(n_ox ** 2 - math.sin(th) ** 2))
assert abs(period - 284.2) < 0.5, period
psi0, del0 = psi_delta(0.0)
psi1, del1 = psi_delta(period)
assert abs(psi1 - psi0) < 0.05 and abs(((del1 - del0) + 180) % 360 - 180) < 0.5, (psi0, del0, psi1, del1)
# 얇은 SiO2에서 Δ 감도(계산값, 문헌 대조값 미확보 → 수치 자체는 미검증, 부호·오더만 기록)
slope = (psi_delta(10.0)[1] - del0) / 10.0
assert -3.5 < slope < -2.0, slope    # 약 -2.7 °/nm (본 노트 계산, 1차 문헌 대조 못 함)
# 스팟 타원: 50 µm 빔 @70° → 장축 146 µm > 100 µm 패드(US7095511) ; 25 µm 마이크로스팟 → 73 µm < 100 µm
beam = 50.0
major = beam / math.cos(th)
assert abs(major - 146.2) < 0.5 and major > 100.0
assert 25.0 / math.cos(th) < 100.0

# ---------- (C) AFM 픽셀 피치 규칙 (Ahn et al. 2019, arxiv.org/abs/1909.09508) ----------
w_sem, h_sem = 115.9, 187.3          # nm, SEM 기준값
pitches = [3.91, 19.53, 23.44, 31.25, 39.06, 78.13, 156.25, 312.5, 625.0]
px_over_width = [w_sem / p for p in pitches]
ok = [p for p, n in zip(pitches, px_over_width) if n >= 4]
assert ok == [3.91, 19.53, 23.44], ok   # "최소 4픽셀" 규칙 → 29 nm 이하 피치만 통과; 논문의 39.06 nm 피치는 3픽셀로 탈락
assert w_sem / 4 < 30                    # 필요 피치 ≈ 29 nm
assert abs(1000 / 30 - 33.3) < 0.1       # 논문 서술 "1 µm 스캔에 ≥30점" ↔ 33 nm 피치, 위 29 nm와 같은 오더
h_afm_best = 184.0                       # 최소 피치에서의 AFM 높이
assert abs(h_afm_best - h_sem) / h_sem < 0.02   # 높이는 SEM 대비 2% 이내 재현
assert abs(172.0 - h_sem) / h_sem < 0.09        # 최악 피치에서도 8% 이내 → 높이는 폭보다 강건
assert 1300 / w_sem > 10                        # 폭은 최악 11배 과대 — 폭·형상이 오차 지배

# ---------- (D) NIST Table 3: 단차 측정계 표준불확도 (Vorburger et al., NIST 문서) ----------
table3 = {0.02937: 0.023, 0.3024: 0.0046, 1.0157: 0.0025}   # H(µm): u(I)/X
u_30nm = 0.023 * 30.0    # nm, 30 nm 단차
u_1um = 0.0025 * 1000.0  # nm, 1 µm 단차
assert abs(u_30nm - 0.69) < 0.01 and abs(u_1um - 2.5) < 0.01
assert 0.023 > 0.0046 > 0.0025   # 작은 단차일수록 상대불확도 커짐(표의 단조성)
# 팁 기하: R=1.52 µm 스타일러스는 w<2R 트렌치 바닥 미도달
R_tip = 1.52
assert abs(2 * R_tip - 3.04) < 1e-9

# ---------- (E) XRF 선형성: NIST XCOM μ/ρ (Cu 52.55, W 170.5 cm²/g @8 keV) ----------
rho_cu, rho_w = 8.96, 19.3             # g/cm³ (CRC 표준값)
mu_cu = 52.55 * rho_cu                 # 1/cm
mu_w = 170.5 * rho_w
assert abs(1 / mu_cu * 1e4 - 21.2) < 0.2     # µm
assert abs(1 / mu_w * 1e4 - 3.04) < 0.05
def nonlin(mu, t_um):
    x = mu * t_um * 1e-4
    return 1 - (1 - math.exp(-x)) / x       # 선형 대비 상대 결손
assert nonlin(mu_cu, 1.0) < 0.025            # Cu 1 µm: 2.3%
assert nonlin(mu_cu, 1.5) < 0.035            # Cu 1.5 µm: 3.4%
assert nonlin(mu_w, 0.5) < 0.09              # W 0.5 µm: 8% — W는 Cu보다 빨리 포화
frac_15um = 1 - math.exp(-mu_cu * 15e-4)
assert 0.45 < frac_15um < 0.55               # Malvern "Cu 단독 15 µm까지"(2차)에서 아직 포화 전(51%) → 측정 가능 방향 일치
print(f"(A) Cu d_p={d_p:.1f} nm, 50nm 왕복 잔존={substrate_fraction:.4f}; (B) Δ주기={period:.1f} nm, 박막 Δ기울기={slope:.2f}°/nm, "
      f"스팟 장축={major:.0f} µm; (C) 4px 규칙 통과 피치={ok}; (D) u(30nm)={u_30nm:.2f} nm, u(1µm)={u_1um:.1f} nm; "
      f"(E) 1/μ Cu={1/mu_cu*1e4:.1f} µm, W={1/mu_w*1e4:.2f} µm, Cu 1µm 비선형={nonlin(mu_cu,1.0)*100:.1f}%, 15µm 포화분율={frac_15um:.2f}")
```

## 8. 정량 재현 요약 (§7 대조표)

| 항목 | 계산값 | 비교 문헌값 | 결과 |
|---|---|---|---|
| Cu 침투깊이 d_p @632.8 nm | 14.8 nm | k=3.408 (Johnson & Christy 1972, 1차 데이터표) | 계산 재현 |
| 50 nm Cu 왕복 후 기판 신호 | 0.1% | "약 50 nm 이상 불투명" (Horiba·Woollam, 2차) | 문턱과 정합(기준 0.2%는 본 노트 선택) |
| SiO₂ Δ 두께주기 @70° | 284.2 nm | 해석식 λ/(2√(n²−sin²θ)) | Fresnel 수치모델과 자기일관 (Δ 오차 <0.5°) |
| 박막 SiO₂ Δ 기울기 | −2.7 °/nm | 1차 대조값 미확보 | **미검증**(계산값만) |
| 스팟 장축 50 µm@70° | 146 µm | 패드 100 µm (US7095511) | 초과 → 마이크로스팟 필요, 정량 확인 |
| AFM 4픽셀 규칙 통과 피치 | ≤29 nm (3.91/19.53/23.44 통과) | 논문: 3.91 nm 피치에서 SEM 일치, 39.06 nm 실패 (Ahn et al. 2019) | 재현 일치 |
| AFM 높이 vs SEM | 184 vs 187.3 nm (1.8%) | Ahn et al. 2019 | 재현 일치 |
| NIST 단차 u(I) | 0.69 nm@30 nm, 2.5 nm@1 µm | Table 3 계수 0.023X / 0.0025X | 계수 그대로 환산 |
| XRF 1/μ | Cu 21.2 µm, W 3.04 µm | NIST XCOM 52.55·170.5 cm²/g | 계산 재현 |
| XRF Cu 15 µm 포화분율 | 51% | Malvern "15 µm까지 측정"(2차) | 방향 일치(미포화) |

## 9. 남은 미확보·미검증 항목 (정직성 표기)

- SiO₂/Si Ψ·Δ 실측 대조값(예: 632.8 nm·70°에서 특정 두께의 Ψ,Δ): spectroscopyonline·ResearchGate 페이지 403,
  Nanofilm 노트(2008, 2차 인용)는 피팅 두께(26.21 ± 0.15 nm)만 있고 Ψ/Δ 원값 없음 → Fresnel 모델은 **자기일관성만** 검증, 실측 대조 **미검증**·
  대조 **미완**. 다음 단원 재시도 대상.
- Stenzel et al. 2019 (Coatings): OA(CC-BY)이나 mdpi PDF가 봇 차단(HTML 반환) → **초록만 확인**.
- Renegar et al. 2012 팁 크기 효과: NIST 게시 초록만, 정량 %값 미확보. Hu et al. 2016 (Nanotechnology, AFM 팁 컨볼루션):
  DOI 실존만 확인, 초록 미공개 → 인용하지 않음.
- 이미징 엘립소미터 2 µm ROI, FilmTek 25 µm 마이크로스팟·3 mm 스팟, Malvern 40 mm 스팟·반복도: 전부 **기업자료 2차**.
- XRF에서 Si/O/N 경원소 부적합, Cu 표면산화가 AFM 조도에 섞임: **정성 추정**, 1차 미확보.
- NIST Vorburger 문서의 발행연도: 본문에 미기재(참고문헌 최신 2014) → "2014년 이후"로만 표기.
- μXRF 논문(Appl. Surf. Sci. 2005): 제목만, DOI 미확인.

## 10. 다음 단원과의 연결

- Lv3-1(제품 웨이퍼 대리 지표·가상 계측): §6.2의 "PTW 패드 소스팟 SE"가 제품 웨이퍼 인라인 계측의 실체이며,
  스팟·패드·혼입광 제약이 가상 계측(virtual metrology)이 필요한 이유의 절반이다.
- Lv3-2/Cal-1(전이 규칙·메타데이터 스키마): §6.2 필수 필드(`spot_size`, `pad_size`, `local_density`,
  `probe_radius`, `pixel_pitch`)를 스키마 초안에 반영 — 구현 요청은 PROFILE.md에 기록.
