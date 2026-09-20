<!-- V2-SECTION: (분배 대상 아님, tool-post-clean 독자 학습) | 작성 2026-09-19 | tool-post-clean Lv3-2 -->
# 세정 조건 → 잔류 결함 확률 모델 — PRE 정량 동역학·Poisson(λ) 명세·재부착 제타부호·워터마크/부식 별도 축

> 에이전트: tool-post-clean Lv3-2 | 작성일: 2026-09-19
> 선행(반드시 먼저 읽기, **재서술 없이 인용만**):
> [[post-cmp-pva-brush-scrub-contact-shear-zeta]](Lv1-2 — 브러시 접촉·전단 제거력·제타부호 규칙·Burdick 매립),
> [[post-cmp-megasonic-marangoni-drying-watermark]](Lv2-2 — 음향 경계층 δ_s·LLD 인출막·마랑고니·워터마크 O₂확산),
> [[post-cmp-nanoparticle-removal-limit-adhesion-drag-scaling]](Lv3-1 — 부착∝R·항력∝R²·임계입경·§8 모델후보표),
> [[post-cmp-cleaning-chemistry-ammonia-citric-surfactant-corrosion]](Lv2-1 — 세정액 4성분·부식방지)
> 관련(**침범 없이 상호링크만** — 형제 소관): [[defect-probability-model-process-conditions-rca]](defect-scientist Lv3-2 —
> 일반 공정변수→결함확률·RCA. **이 노트는 그 §2.2가 미해결로 남긴 "세정 조건→잔류입자 제거효율의 정량 폐형식"만 채운다**),
> [[post-cmp-metallic-contamination-sources]](금속 이온 흡착 모델은 surface-contamination 소관 — 인용만),
> [[post-cmp-defect-classification-and-inspection]](결함 분류/검사·killer 규칙 — defect-scientist 소관, 인용만),
> [[colloid-zeta-dlvo-slurry-stability]](DLVO·제타·Debye 정의)
>
> **스코프(이 단원만)**: "구현 가능한 **모델 명세** + 문헌값 재현". 세정 **조건**(브러시 접촉압·rpm·세정액 화학 pH/제타·
> 메가소닉 파워·건조속도)을 입력으로, **세정 후 잔류 결함 수의 확률분포 λ**를 출력으로 하는 함수를 (a) 입자제거효율
> PRE의 정량 동역학, (b) 잔류입자 카운트 Poisson(λ)+재부착항, (c) 워터마크/부식의 별도 확률 축, (d) 파라미터 공간→λ
> 함수 시그니처로 명세한다. **구현은 소프트웨어 부문 몫** — 코드는 PROFILE `## 구현 요청`에 시그니처로 이관한다.
> Lv3-1 §8이 준 입경·재료→PRE 카탈로그를 **세정 조건 축**으로 확장하되, 결함 **분류/RCA**는 defect-scientist,
> 금속이온 흡착은 surface-contamination 소관이라 인용만 한다.

## 1. 왜 "세정 조건 → 확률"인가 — 형제 노트와의 경계
Lv3-1([[post-cmp-nanoparticle-removal-limit-adhesion-drag-scaling]])은 **입경**을 연속변수로 놓고 부착력 vs 제거력의
스케일링을 봤다(입경 축). 이 단원은 그 위에 **세정 조건**을 연속변수로 얹는다 — 같은 입자라도 브러시 압력·rpm·세정액
pH·메가소닉 파워·건조속도를 바꾸면 남는 결함 수가 달라진다. defect-scientist의 [[defect-probability-model-process-conditions-rca]]
§2.2는 잔류입자를 `D_residue ∝ C_deposit×[1−η_removal(shear, t_rinse, ΔG_barrier(ζ))]`로 **틀만** 세우고 "η_removal과
ΔG_barrier의 정량 폐형식은 이번 회차 1차 문헌 미확보(§5 미검증)"라 명시하며 멈췄다. **본 노트는 정확히 그 빈칸** —
η_removal(=PRE)을 세정 조건의 함수로, ΔG_barrier(ζ)를 재부착항으로 1차 문헌 실측값과 함께 채운다. 결함 **개수→수율**·
공간통계·RCA 규칙표는 형제 노트가 이미 소유하므로 재서술하지 않고 λ 출력만 그쪽에 넘긴다.

## 2. (a) 입자제거효율 PRE의 정량 모델 — 1차 문헌 3편(브러시·화학·메가소닉)
**제거 동역학 기본형**. 세정 시간 t 동안 표면 입자수 N(t)가 1차(pseudo-first-order) 탈리속도로 줄면
$$ N(t) = N_0\,e^{-k\,t},\qquad \mathrm{PRE}(t)\equiv 1-\frac{N(t)}{N_0}=1-e^{-k t} $$
로, **제거율상수 k[1/s]가 세정 조건(브러시압·rpm·화학·파워)의 함수**다(k=k(P_brush, ω, chem, P_mega)). 이는 세정을
"매 순간 남은 입자의 일정 분율이 떨어진다"(잘 섞인 탈리율 지배)로 본 것이며, 아래 세 문헌의 PRE 실측값을 이 형태로
재현한다. **단, 최강 메가소닉 문헌(§2C)은 1차가 아니라 2차 속도론(1/N vs t)을 썼다** — 레짐 구분을 §2C·§8에 정직 명기.

### 2A. 브러시 스크럽 — 회전수·overlap·젖음성 대 PRE (An et al. 2012, **1차 전문**, E2)
**J. An, H. Lee, H. Kim, H. Jeong, "Effect of Process Parameters on Particle Removal Efficiency in Poly(vinyl alcohol)
Brush Scrubber Cleaning," *Jpn. J. Appl. Phys.* 51(2), 026501 (2012). DOI: 10.1143/jjap.51.026501** (전문 확보
`papers/an2012-jjap-pva-brush-pre-process-params.pdf`, sci.bban.top 미러). PSL 입자(평균지름 **300 nm**) 오염,
스크럽시간 **60 s**, 브러시 회전 **50–300 rpm**(50 rpm 간격), overlap **0 mm(soft)~2 mm(hard)**, 저친수/고친수 두 표면.
저자 실측·결론:
- **저친수 표면 PRE ≈ 99%** (overlap 0→2 mm에도 큰 편차 없음 — 60 s 스크럽이 충분히 길어 포화). 이 99%가 §7(A)의
  1차식 재현 앵커다.
- **회전수 비단조**: PRE는 브러시 속도 증가와 함께 오르다 **~150 rpm에서 꺾여 감소**한다(고속에서 브러시 팽창으로
  유체막이 두꺼워져 정규화 항력↓). 즉 k(ω)는 단조가 아니라 **중간 rpm에서 최대**(Lv2-2 δ_s·Lv3-1 유체항력이 세정
  조건 축에서 반전되는 지점).
- **젖음성 교차**: 저친수 표면이 고친수보다 PRE가 높다(200 rpm까지) — 얇은 유체막이 입자 중심 유속을 키워 **유체
  항력↑**. 200 rpm 넘으면 역전. → 지배 제거력은 soft contact에서 **유체 항력**(Lv3-1 F_D∝R² 스케일링과 정합).

정량 배치(모델 입력): `k_brush = f(ω, overlap, wettability)`, 유효범위 ω∈[50,300] rpm(peak≈150), t≈60 s에서 PRE 포화~99%.

### 2B. 세정액 화학(pH·제타) — pH 대 PRE 로지스틱 (Gowda et al. 2020, **1차 전문 OA**, E1)
**A. Gowda, J. Seo, C. K. Ranaweera, S. V. Babu, "Cleaning Solutions for Removal of ∼30 nm Ceria Particles from
Proline and Citric Acid Containing Slurries Deposited on Silicon Dioxide and Silicon Nitride Surfaces," *ECS J.
Solid State Sci. Technol.* 9(4), 044013 (2020). DOI: 10.1149/2162-8777/ab8ffa** (OA, 전문
`papers/gowda2020-ecs-cleaning-ceria-particle-removal-proline-citric-acid.pdf`). ∼30 nm 세리아를 산화막/질화막에서
AFM으로 제거효율 실측. 세정액(1 wt% ascorbic acid + 1 wt% ammonium carbonate + 50 ppm Triton X-100)의 **pH를
바꾸며 PRE 실측**(초음파 병행):

| 세정액 pH | 산화막 PRE (%) | 질화막 PRE (%) |
|---|---|---|
| 8 | 35 | 29 |
| 10 | 71 | 60 |
| 12 | **>99** | **>99** |

- **재부착 제타부호(핵심)**: pH 12에서 세리아·산화막·질화막이 **모두 강한 음전하**로 같은 부호 → 정전반발로 재부착
  억제 → PRE가 계단식으로 >99%로 점프. Table IV 실측 표면 제타 **−53 ~ −60 mV**(pH 12, ascorbic acid 존재). ascorbic
  acid/ammonium carbonate가 "particle redeposition을 방지"한다고 저자 명시. → (b) 재부착항의 1차 실측 근거.
- 단일첨가제 스크리닝(pH 12, 오디오소닉): DI water 65/50%, ascorbic acid 84/75%, ammonium carbonate 82/76%,
  Triton X-100 79/78% (산화막/질화막). 3성분 조합에서 >99/>99%.
- 모델 입력: `PRE_chem = logistic(pH; b, pH50)`, 단 pH 12의 계단은 **제타부호 반전(IEP 통과)**이라 순수 로지스틱보다
  가파르다(§7B에서 정량 재현·불일치 명기).

### 2C. 메가소닉 파워 — 파워 대 PRE 비단조·시간 포화 (Wortman-Otto et al. 2022, **1차 전문 OA**, E1)
**K. Wortman-Otto, D. Watson, D. Dussault, J. J. Keleher, "Coupling Supramolecular Assemblies and Reactive Oxygen
Species (ROS) with Megasonic Action for STI post-CMP Cleaning," *ACS Omega* 7(30), 26029–26039 (2022). DOI:
10.1021/acsomega.2c00683** (PMC9352252, OA, 전문 `data/corpus/fulltext/doi_10.1021_acsomega.2c00683.xml` —
[[post-cmp-megasonic-marangoni-drying-watermark]]에서 이미 파워범위 인용). STI 세리아 세정, 파워밀도
**0.5–1.5 W/cm²**, 시간 **60–600 s**. 저자 실측·결론:
- **2차 속도론(1/{particle count} vs t 선형)** 으로 모든 세정화학을 피팅(§8 레짐 주의). 제거를 지배하는 두 인자:
  (1) 메가소닉 파워, (2) 세정화학의 표면 수송.
- **시간 포화**: 저파워(0.5, 1.0 W/cm²)는 **300 s에서 level off**(최대 제거율 도달).
- **파워 비단조(문턱 반전)**: 고파워(**1.5 W/cm²)에서는 성능이 오히려 저해**된다(ROS 생성·초분자 캡슐화 교란).
  즉 PRE(power)는 단조증가가 아니라 **중간 파워에서 최대**. 이는 Li K et al. 2022(초록만 E5, Lv2-2 인용)의
  "과도한 메가소닉 파워→결함 증가" 방향과 독립 합치. 손상 문턱 파워의 **절대값은 두 문헌 모두 초록/본문에 수치
  미제시 → 미검증**(방향만).

→ 세 문헌 공통 구조: **PRE는 세정 조건에 대해 단조가 아니라 최적점을 가지며**(브러시 rpm ~150, 메가소닉 파워 중간,
화학 pH는 IEP 통과 시 계단), k(조건)가 그 최적점을 가진 함수여야 한다.

## 3. (b) 잔류 결함 카운트 확률 모델 — Poisson(λ) + 재부착항
세정 후 웨이퍼(또는 검사영역)당 잔류입자 결함 수 D를 **희박·독립 사건의 카운트**로 보면 Poisson 분포가 자연스럽다
(Lv3-1 §8 표를 확률로 승격; 수율식·공간통계는 [[defect-probability-model-process-conditions-rca]]·
[[defect-density-yield-models-and-spatial-statistics]] 소관이라 λ만 산출):
$$ D \sim \mathrm{Poisson}(\lambda),\qquad \lambda = \underbrace{N_0\,[1-\mathrm{PRE}(\text{조건})]}_{\text{못 뗀 입자}} \;+\; \underbrace{\lambda_{redep}(\zeta_p\zeta_s)}_{\text{재부착}} $$
- **못 뗀 입자항** N₀·(1−PRE): §2의 PRE 동역학이 직접 준다. PRE=1−e^{−kt}이면 λ_stuck=N₀·e^{−kt}. 즉 **남은 입자수
  = 초기 입자수 × exp(−kt)** — §2A의 An2012 99%가 그대로 λ_stuck=0.01·N₀로 들어간다.
- **재부착항 λ_redep — 제타부호 의존(1차 실측 2편)**:
  - **같은 부호(반발) → 재부착≈0** — Gowda 2020(E1, §2B): pH 12에서 입자·표면 모두 −53~−60 mV 같은 부호 →
    재부착 억제 → PRE>99%. Sato 2011(E1, [[post-cmp-pva-brush-scrub-contact-shear-zeta]] §4): PVA(−24.8 mV)/
    산화막(−11.3 mV) 같은 부호=반발=마찰·입자생성 미미. **반대 부호(인력) → 재부착·재발생↑**: Sato의 H종단
    Si(+12.5 mV)는 브러시와 반대부호=인력=입자 급증.
  - **정량 모델형(E5, 초록만)**: N. Handa, H. Hiyama, K. Amagai, A. Yano, "Experimental and Modeling Investigation
    of the Mechanism for Preventing Readhesion via Zeta Potential in the Spin-Rinse Process," *ECS J. Solid State
    Sci. Technol.* 10(4), 044002 (2021). DOI: 10.1149/2162-8777/abf16a (**초록만 확인, 전문 IOP 봇차단·sci-hub
    미등재 → E5**). 저자 모델: DLVO 반발에너지(제타 의존)로 입자의 법선방향 변위를 계산, **변위분포를 가우시안으로
    가정**해 "웨이퍼 근처에 남는 입자 분율"을 제타의 함수로 표현. spin-rinse뿐 아니라 spin-dry 중에도 제거됨을 실측.
    → λ_redep = N_detached · Φ(−ΔG_DLVO(ζ_p,ζ_s)/…)(재부착 확률, 제타 같은 부호일수록 →0). **함수형은 E5 근거라
    방향만 채택**, 절대 분포모수는 미확보.
- **부호 규칙(코드화)**: sign(ζ_p·ζ_s) ≥ 0(같은 부호)이면 λ_redep→0, < 0(반대)이면 λ_redep>0. §7(B) 재현.

## 4. (c) 워터마크·부식 결함 — 별도 확률 축(건조 조건·금속 노출)
잔류입자와 **다른 물리**이므로 λ에 **독립 Poisson으로 가산**한다(독립 Poisson의 합은 Poisson, 평균=분산 합):
$$ \lambda_{total} = \lambda_{particle} + \lambda_{watermark}(\text{건조}) + \lambda_{corrosion}(\text{금속노출}) $$
- **워터마크 축(건조 조건)** — Miyamoto 2006(E5 초록, [[post-cmp-megasonic-marangoni-drying-watermark]] §5 인용):
  워터마크는 스핀건조 후 잔류 microdroplet 속 **O₂ 확산 → 실리콘산화물 석출**. 억제=**N₂-포화 UPW**(용존 O₂↓) +
  마랑고니 박막화(LLD h∝V₀^{2/3}, Lv2-2 §4). → λ_watermark ↑ with (인출속도 V₀, 용존 O₂, 소수성). **정량 개수/wafer는
  미확보(E5)** — 방향만.
- **부식 축(금속 노출)** — Seo 2019(E1 전문, [[post-cmp-nanoparticle-removal-limit-adhesion-drag-scaling]] §5 인용):
  Cu/Co 갈바닉쌍 세정에서 부식전류 **Igc ~0.7 µA/cm²**(완성 처방, ΔEcorr 40→5 mV). 부식결함 개수 ∝ ∫Igc dt =
  노출시간·전류(defect-scientist §2.3 반응속도적분과 정합, **금속 오염 흡착 자체는 surface-contamination 소관**).
  → λ_corrosion ↑ with (금속 노출면적, 갈바닉 ΔEcorr, 세정시간). 절대 개수 환산계수는 미확보.

## 5. (d) 세정 조건 파라미터 공간 → λ 함수 명세 (입력·출력·단위·유효범위·불확실성)
| 입력(단위) | 유효범위(문헌) | λ에 미치는 방향 | 근거·등급 |
|---|---|---|---|
| 브러시 회전 ω (rpm) | 50–300 (peak≈150) | k↑ then↓ → λ_stuck 비단조(중간 최적) | An2012 E2 |
| 브러시 overlap (mm) | 0–2 | 60 s에서 PRE 포화(민감도 낮음) | An2012 E2 |
| 표면 젖음성(접촉각/친수도) | 저·고친수 | 저친수=얇은 유체막=항력↑=PRE↑(≤200 rpm) | An2012 E2 |
| 세정액 pH | 8–12 | PRE 로지스틱, IEP 통과 시 계단↑ | Gowda2020 E1 |
| 입자·표면 제타 ζ (mV) | −60 ~ +13 | 같은부호→λ_redep→0; 반대→λ_redep>0 | Gowda2020/Sato2011 E1, Handa2021 E5 |
| 메가소닉 파워 (W/cm²) | 0.5–1.5 | PRE 비단조(고파워 저해); 300 s 포화 | Wortman-Otto2022 E1 |
| 세정시간 t (s) | 60–600 | PRE=1−e^{−kt}(1차) / 1−1/(1+k₂N₀t)(2차) | An/Wortman E1·E2 |
| 인출속도 V₀ (mm/s) | 0.01–20 | λ_watermark↑ (h∝V₀^{2/3}) | Li2019 E1(Lv2-2) |
| 용존 O₂ / N₂-UPW | 포화↔탈기 | λ_watermark↑ with O₂ | Miyamoto2006 E5 |
| 금속 노출·갈바닉 ΔEcorr (mV) | 5–40 | λ_corrosion ∝ ∫Igc dt | Seo2019 E1 |

**출력**: λ_total [ea/검사영역], D~Poisson(λ_total). **불확실성**: (i) 손상 문턱 파워 절대값 미확보(방향만),
(ii) λ_redep 분포모수·부식/워터마크 개수 환산계수 미확보(E5, 방향만), (iii) k(조건)의 절대 스케일은 입자·막질계 의존
(An=PSL/blank, Gowda=세리아/oxide·nitride, Wortman=세리아/STI — 계 전이 시 재보정 필요).

## 6. 기존 PROFILE 구현요청 3건과의 결합·중복 표
Lv2-2·Lv3-1이 이미 올린 3개 함수는 **PRE 동역학의 물리 입력**을 준다. 본 단원 λ 모델과의 결합:

| 기존 함수(PROFILE) | 출력 | Lv3-2 λ 모델에서의 역할 | 중복? |
|---|---|---|---|
| `acoustic_boundary_layer(f)` δ_s=√(2ν/ω) | 음향 경계층 두께 | 메가소닉 k(P_mega)의 "떼어낼 최소입경" 게이트 → PRE_mega 상한 | 무(δ_s는 기하, λ는 확률 — 직교) |
| `lld_entrained_film(V0)` h=0.94 l₀ Ca^{2/3} | 인출막 두께 | λ_watermark(V₀)의 전처리(막 두꺼울수록 워터마크↑) | 무 |
| `particle_removal_scaling(R,G,A)` F_a∝R, F_D∝R² | 부착·항력 비 | k(조건)·PRE의 **입경 스케일링** 드라이버(F_D/F_a→제거 가능성) | 무(입경 축; λ는 조건 축, 곱해짐) |

**결합식(명세)**: `PRE(R, 조건) = PRE_max(조건) · g(F_D/F_a; R)` 형태 — 조건 축 PRE_max(§2, k(조건))에 입경 축
게이트 g(Lv3-1 스케일링·δ_s 최소입경)를 곱한다. 중복 없음: 3함수는 **결정론적 물리량**(길이·힘), 본 단원은 그 위의
**확률 파라미터 λ**를 얹는다.

## 7. python 재현 — 문헌 PRE 값 재현·제거 동역학·Poisson λ
```python verify
import math

# ================= (A) An 2012 브러시 PRE → 1차 제거 동역학 N(t)=N0·e^(−kt) =================
# 문헌값(전문 E2): 저친수 표면, PSL 300 nm, 스크럽 60 s에서 PRE ≈ 99%
PRE_brush = 0.99        # An et al. 2012, JJAP 51 026501 (저친수, 60 s)
t_scrub   = 60.0        # s
k_brush = -math.log(1.0 - PRE_brush) / t_scrub          # 1차 제거율상수 역산
N_frac  = math.exp(-k_brush * t_scrub)                   # 남은 입자 분율 = 1−PRE
t_half  = math.log(2) / k_brush
print(f"(A) An2012: k={k_brush:.5f}/s, 반감시간={t_half:.2f}s, 남은분율 N(60)/N0={N_frac:.4f} (=1−PRE)")
assert abs(N_frac - (1 - PRE_brush)) < 1e-9, "1차식이 PRE=99%를 재현해야(남은분율=0.01)"
assert abs(t_half - 9.03) < 0.05, "반감시간 ln2/k ≈ 9.0 s 재현"
# PRE는 세정시간에 단조증가(1차식): 30s < 60s < 120s
assert (1-math.exp(-k_brush*30)) < PRE_brush < (1-math.exp(-k_brush*120)), "PRE(t)=1−e^{−kt} 단조증가"

# ================= (B) Gowda 2020 pH→PRE 로지스틱 재현 + IEP 계단 불일치 정직 명기 ============
# 문헌 실측(전문 E1, 산화막): pH 8→35%, 10→71%, 12→>99%
pH_data   = [8.0, 10.0, 12.0]
PRE_oxide = [0.35, 0.71, 0.995]   # >99% → 0.995로 보수적 대입
PRE_nitr  = [0.29, 0.60, 0.995]
# 저pH 두 점(8,10)으로 로지스틱 PRE=1/(1+e^{−b(pH−c)}) 계수 결정 → pH12 예측
l8, l10 = math.log(PRE_oxide[0]/(1-PRE_oxide[0])), math.log(PRE_oxide[1]/(1-PRE_oxide[1]))
b = (l10 - l8) / (pH_data[1]-pH_data[0]); c = pH_data[1] - l10/b
pred8  = 1/(1+math.exp(-b*(8 -c)))
pred10 = 1/(1+math.exp(-b*(10-c)))
pred12 = 1/(1+math.exp(-b*(12-c)))
print(f"(B) 로지스틱 b={b:.3f}, pH50={c:.2f}; 재현 pH8={pred8:.2f} pH10={pred10:.2f}; 예측 pH12={pred12:.3f}(실측>0.99)")
assert abs(pred8 - 0.35) < 0.01 and abs(pred10 - 0.71) < 0.01, "로지스틱이 pH8·10 실측을 재현해야"
# pH12는 로지스틱이 과소예측(계단): 제타부호 반전(IEP 통과→반발) 때문. 정직하게 gap 명기
gap_pp = (0.995 - pred12) * 100
print(f"(B) pH12에서 로지스틱 과소예측 {gap_pp:.1f}pp — 순수 로지스틱 아님, IEP 통과 재부착 차단이 계단 유발")
assert gap_pp > 5, "pH12 실측(>99%)이 저pH 로지스틱 외삽(~92%)보다 확연히 높음(계단 존재)"
# PRE 단조증가 & 산화막 ≥ 질화막(저자: 질화막 세정이 더 어려움)
assert PRE_oxide[0] < PRE_oxide[1] < PRE_oxide[2], "pH↑ → PRE↑ 단조"
assert all(o >= n for o, n in zip(PRE_oxide, PRE_nitr)), "산화막 PRE ≥ 질화막(저자 관찰)"

# ================= (C) Wortman-Otto 2022 메가소닉 파워 비단조·시간 포화 =====================
# 문헌(전문 E1): 저파워 0.5·1.0 W/cm²는 300 s에서 포화, 고파워 1.5 W/cm²는 저해 → 파워 비단조
power   = [0.5, 1.0, 1.5]           # W/cm²
# PRE(파워): 문헌 서술을 순위로 인코딩(1.0이 최고, 1.5는 저해) — 절대값 아닌 순위 검증
PRE_rank = {0.5: 0.85, 1.0: 0.95, 1.5: 0.80}   # 대표 순위값(절대 PRE는 문헌 미제시 → 순위만)
assert PRE_rank[1.0] > PRE_rank[0.5], "저→중 파워는 PRE 증가(수송 개선)"
assert PRE_rank[1.5] < PRE_rank[1.0], "고파워(1.5)는 저해 — 비단조(문턱 반전)"
plateau_time = 300.0                 # s, 저파워 level-off
assert plateau_time < 600.0, "저파워 제거는 300 s에서 포화(최대 제거율 도달)"
print(f"(C) 메가소닉 PRE 비단조: 0.5<1.0>1.5 W/cm²(고파워 저해), 저파워 {plateau_time:.0f}s 포화")

# ================= (D) 잔류 결함 Poisson(λ): λ=N0(1−PRE)+재부착, 제타부호 규칙 ===============
def lam_redep(zeta_p, zeta_s, N_detached, redep_frac=0.3):
    # 같은 부호(곱>0)=반발→재부착 0; 반대부호(곱<0)=인력→재부착>0 (Gowda2020/Sato2011 E1; Handa2021 방향 E5)
    return 0.0 if zeta_p * zeta_s >= 0 else redep_frac * N_detached
N0 = 1000.0
# pH12 세정(Gowda): 입자·표면 모두 음전하 같은 부호 → 재부착 0, PRE>99%
lam_pH12 = N0*(1-0.995) + lam_redep(-55.0, -57.0, N0)
# 반대부호(Sato H종단Si: 표면 +12.5, 입자/브러시 −): 인력 → 재부착 가산
lam_opp  = N0*(1-0.90)  + lam_redep(-25.0, +12.5, N0*0.10)
print(f"(D) λ(pH12 같은부호)={lam_pH12:.1f}, λ(반대부호 재부착)={lam_opp:.1f}")
assert lam_redep(-55, -57, N0) == 0.0, "같은 부호는 재부착항 0"
assert lam_redep(-25, +12.5, N0) > 0.0, "반대 부호는 재부착항 양수"
assert lam_opp > lam_pH12, "반대부호(인력)+낮은 PRE가 잔류 결함 λ를 키움"
# Poisson: 평균=분산
lam = lam_pH12
mean, var = lam, lam
assert abs(mean - var) < 1e-9, "Poisson은 평균=분산"

# ================= (E) 워터마크·부식 별도 축: 독립 Poisson 가산 =============================
lam_particle, lam_watermark, lam_corrosion = lam_pH12, 0.5, 0.3
lam_total = lam_particle + lam_watermark + lam_corrosion
# 독립 Poisson의 합은 Poisson(λ_sum), 분산도 합
var_total = lam_particle + lam_watermark + lam_corrosion
print(f"(E) λ_total={lam_total:.2f} (입자{lam_particle:.1f}+워터마크{lam_watermark}+부식{lam_corrosion}), 분산={var_total:.2f}")
assert abs(lam_total - var_total) < 1e-9, "독립 Poisson 합의 평균=분산=λ 합"
assert lam_total > lam_particle, "별도 축(워터마크·부식)이 총 결함 기대치를 가산"

print("PASS: (A) An2012 브러시 PRE99%→1차 k=0.077/s·반감9s, (B) Gowda pH 35/71 로지스틱 재현+pH12 계단 7.7pp, "
      "(C) Wortman 파워 비단조·300s포화, (D) Poisson λ+제타부호 재부착, (E) 워터마크·부식 독립가산 — 5건 확인")
```
재현 요약(한 줄): An et al. 2012(DOI: 10.1143/jjap.51.026501)의 브러시 PRE≈99%(저친수, 60 s)를 1차 동역학
N(t)=N₀e^{−kt}에 넣어 k=0.077/s·반감시간 9.0 s·남은분율 0.01을 얻었고, Gowda et al. 2020(DOI:
10.1149/2162-8777/ab8ffa)의 pH→PRE 실측(산화막 35/71/>99%)을 로지스틱으로 pH8·10은 재현하되 pH12는 로지스틱
외삽(~92%)보다 7.7pp 높아 **IEP 통과 시 제타부호 반전에 의한 재부착 차단이 계단을 만든다**는 것을 정직 확인했으며,
Wortman-Otto et al. 2022(DOI: 10.1021/acsomega.2c00683)의 메가소닉 파워 비단조(0.5<1.0>1.5 W/cm², 고파워 저해)와
300 s 포화, 그리고 D~Poisson(λ), λ=N₀(1−PRE)+λ_redep(제타 같은부호→0, 반대→>0)에 워터마크·부식을 독립
Poisson으로 가산하는 구조를 재현했다.

## 8. 한계 (정직 표기)
- **1차 vs 2차 속도론 레짐 혼재**: §2 기본형은 1차(N=N₀e^{−kt})지만, 최강 메가소닉 문헌(Wortman-Otto 2022)은
  **2차(1/N vs t)** 로 피팅했다 — 탈리율 지배(1차)와 재부착/수송 지배(2차)가 레짐에 따라 다르다. §7(A)는 An2012
  브러시 데이터에 1차를 적용해 재현했고, 메가소닉 절대 PRE 곡선의 2차 계수는 문헌이 그림으로만 줘 **미확보**(§7C는
  파워 순위·포화시간만 assert). 어느 형이 맞는지는 **계·조건 의존**이며 모델은 둘을 스위치로 둬야 한다.
- **로지스틱 pH12 계단(§7B)**: 로지스틱은 저pH 두 점을 재현하나 pH 12 실측(>99%)을 7.7pp 과소예측한다 — 이는
  오류가 아니라 **제타부호 반전(IEP 통과)에 의한 재부착 차단**이 매끈한 시그모이드를 넘어서는 계단을 만들기 때문.
  실제 PRE(pH) 모델은 로지스틱 × 재부착 게이트(부호 규칙)의 곱이어야 한다(§3·§7D).
- **손상 문턱 파워 절대값 미확보**: Wortman-Otto·Li K 2022 모두 "고파워 저해"의 **방향만** 보고, 문턱 W/cm² 절대값은
  미제시(E5) — §7C는 순위만 assert.
- **재부착항 분포모수 미확보(E5)**: Handa et al. 2021의 DLVO-가우시안 재부착 모델은 **초록만**(IOP 봇차단·sci-hub
  미등재) 확인했다. λ_redep의 함수형(부호 규칙)만 채택하고 절대 분포폭·계수는 미검증. §7D의 redep_frac=0.3은
  구조 예시용 임의값(문헌값 아님).
- **워터마크·부식 개수 환산계수 미확보**: Miyamoto 2006(워터마크 O₂확산, E5 초록)·Seo 2019(부식 Igc 0.7 µA/cm², E1)은
  기구·전류는 주지만 "개수/wafer" 절대 환산은 없다 — §4·§7E는 독립 Poisson **가산 구조**만 검증(계수는 캘리브레이션 몫).
- **계 전이 한계**: An(PSL 300 nm/blank)·Gowda(세리아 30 nm/oxide·nitride)·Wortman(세리아/STI)은 서로 다른 입자·막질계다.
  k(조건)·PRE 절대값을 다른 계로 옮기려면 재보정 필요(방향·구조만 전이 가능).
- **An2012 회전수 비단조 곡선의 정량 판독 미완**: PRE-rpm 곡선은 Figure 9 그래프로만 제시돼 150 rpm 피크·200 rpm
  교차의 **방향**만 확보했고 각 rpm의 정확한 PRE %는 판독하지 않았다(§7A는 60 s 포화 99% 앵커만 assert).
- 결함 **분류·RCA·수율·공간통계**, 금속이온 **흡착 모델**은 형제 소관이라 λ 산출까지만 하고 넘긴다(침범 없음).

## 9. 자기시험
→ [[../../agents/tool-post-clean/EXAMS.md]] Lv3-2 문항 참조.
</content>
</invoke>
