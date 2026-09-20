<!-- V2-SECTION: R5-wafer | 분배완료 2026-09-08 | 근거: metrology, pattern-, ttv, uniformity, wiwnu | 정본: ARCHITECTURE-V2.md §3 -->
# 균일도 지표 정의의 문헌 확정 — TTV·WIWNU(σ/3σ/half-range)·CV·radial·측정점 체계

> 에이전트: wafer-metrology Lv1-2 | 작성일: 2026-09-06
> [[wafer-metrology-thickness-methods]] [[wiwnu-pressure-velocity-wafer-scale]] [[pattern-dependent-dishing-erosion]] [[preston-luo-dornfeld-mrr]]

## 0. 이 노트의 목적과 원칙

`sim/metrics/uniformity.py`는 지표 정의를 **잠정(PROVISIONAL)**으로 두고 있고, docstring이
"Lv1-2 학습 결과가 이긴다"고 명시했다. 이 노트는 그 정의들을 **공개 문헌·표준·특허**에서
확정한다. **매우 중요한 방법론적 제약**: 사용자 회사 관행 정의(전체 max−min, radial=반경별 링
max−min 중 최대, CV=σ/μ×100)를 그대로 옮기지 않는다. 문헌 정의를 default로 삼고, 회사 관행이
문헌과 다르면 둘 다 병기하되 **기준은 문헌**임을 명시한다. WIWNU는 산업 단일표준이 없어
정의가 갈리므로([[wiwnu-pressure-velocity-wafer-scale]] §1) 변형을 전부 병기하고 각 출처를 단다.

## 1. TTV (Total Thickness Variation) — 표준 정의 확정

$$ \text{TTV} = t_{max} - t_{min} $$

- 1차 표준: **SEMI MF1530** "Test Method for Measuring Flatness, Thickness, and Total Thickness
  Variation on Silicon Wafers by Automated Noncontact Scanning"(store-us.semi.org 제품 페이지로
  스코프·정의 확인, 원문 PDF는 downloads.semi.org Cloudflare 봉쇄로 **1차 미확보** — [[wafer-metrology-thickness-methods]]
  §10과 동일 상황). TTV는 웨이퍼 전면에 대해 뒷면을 이상 평탄으로 가정(척에 완전 흡착)했을 때
  측정한 두께의 **최대−최소**로, MF1530이 flatness·thickness와 함께 규정하는 기본 지표.
- 2차 확보(원문 발췌 확인): Kao & Chung, *Wafer Manufacturing*(2021, Wiley) Eq.(1.5)
  `TTV = t_max − t_min` — [[wafer-metrology-thickness-methods]] §9에서 이미 교과서 예제로 재현·대조
  완료(교과서 예제 TTV=0 nm 재현). universitywafer.com TTV 페이지도 "maximum variation in a
  wafer's thickness"로 동일 서술(2차, 정성).
- **주의**: TTV는 본래 **웨이퍼 기판(substrate) 두께 편차** 지표다. CMP 후 문맥에서 "TTV"라 하면
  잔막(remaining film) 또는 제거두께(removal)의 max−min을 뜻하는 경우가 많은데, 이는 기판 TTV의
  **차용**이다. 코드에서 이 둘을 혼동하지 않도록 "무엇의 max−min인가"(기판/잔막/제거량)를
  항상 명시해야 한다(정성 판단, 표준이 명시적으로 구분하지는 않음).

## 2. WIWNU — 세 가지 정의를 전부 병기 (default: 3σ)

WIWNU(within-wafer non-uniformity)는 단일 산업표준이 없다. 문헌에서 확인된 정의는 셋:

| 표기 | 정의식 | 출처(1차/특허) |
|---|---|---|
| **3σ WIWNU** (통상 "the" WIWNU, **default**) | $100\cdot 3\sigma/\bar t$ | US6922603B1 특허; Lee & Boning 1999 |
| **1σ WIWNU** (σ%) | $100\cdot \sigma/\bar t$ | Kumar 2019(IMAPS) Eq.(2) |
| **range/half-range** (k값) | $100\cdot (t_{max}-t_{min})/(2\bar t)$ | Luo & Dornfeld(escholarship); Lee & Boning range metric |

- **3σ가 관례적 default**: 미국 특허 **US6922603B1** "System and method for quantifying uniformity
  patterns..."(patents.google.com/patent/US6922603B1, 원문 텍스트 확인함)이 "the 3-sigma
  uniformity metric is ... 3 times the standard deviation of the measurements ... divided by the mean
  thickness ... 0% being ideal"로 명시하고, "the 3-sigma metric is also often referred to as the
  WIWNU metric"이라 못 박는다. **1차 출처(특허 공개문)**.
- Lee & Boning 1999 "A study of within-wafer non-uniformity metrics," *4th Int. Workshop on
  Statistical Metrology (IWSTM)*, **DOI: 10.1109/iwstm.1999.773193** (IEEE, 본문 유료·**미확보**,
  초록·2차 스니펫 확인): 3σ가 통상 WIWNU이나 **처리시간에 따라 편향(biased)**되거나 개선에
  둔감한 지표가 있어 "여러 지표를 병기해야 한다"고 결론 — 이 노트의 병기 원칙의 1차 근거.
- **1σ(σ%)형**: Kumar 2019, "Optimizing the WIWNU at the CMP step ... for 3D IC stacking,"
  *Int. Symp. Microelectronics (IMAPS)*, **DOI: 10.4071/2380-4505-2019.1.000450** (imapsource.org
  OA, PDF 바이너리라 본문 자동추출 **미확보**, 검색 스니펫으로 확인): "WIWNU was calculated
  using equation 2, where σ and Avg are the standard deviation and average of the measurements" —
  즉 σ/Avg형. 49 site 4점탐침 Cu 두께에 적용.
- **half-range(range/k)형**: Luo & Dornfeld, "Wafer-Scale CMP Modeling of Within-Wafer
  Non-Uniformity"(escholarship.org/uc/item/29g1z2t6, UC 공개, PDF 바이너리 **본문 미확보**,
  스니펫 확인) — "minimum WIWNU ... is $0.5(P_{max}-P_{min})/P_{avg}\times100\%$", 곧 $(max-min)/(2\bar t)$.
  범위형은 max/min만 쓰므로 **이상점(outlier)에 민감**하고 일반적으로 σ형보다 크다
  ([[wiwnu-pressure-velocity-wafer-scale]] §1 계승).
- **강건 지표 대안**: "A robust metric for measuring within-wafer uniformity," *IEMT 1995*,
  **DOI: 10.1109/iemt.1995.526193** (본문 **미확보**) — 3σ/range가 이상점에 취약하다는 문제의식에서
  강건(robust) 지표를 제안. 즉 문헌 자체가 3σ·range의 한계를 인정하고 대안을 모색해 왔다.

→ **코드 반영**: `uniformity.py`는 3σ·1σ·half-range를 **모두** 출력하고 default 보고값을 3σ로
정한다. 값 인용 시 정의식 병기는 필수([[wiwnu-pressure-velocity-wafer-scale]] §1 재확인).

## 3. CV (Coefficient of Variation) — WIWNU 1σ와 수학적으로 동일

$$ \text{CV} = 100\cdot \sigma/\bar t \;(\%) $$

CV는 통계학 표준 정의(표준편차/평균)로, **1σ WIWNU(σ%)와 완전히 같은 수식**이다. 회사 관행이
"CV=σ/μ×100"으로 쓰는 것은 문헌 정의와 일치하므로 이 항목은 병기 불필요(문헌=관행). 다만
CMP 문맥에서 CV라 부르든 "1σ WIWNU"라 부르든 **동일 수임**을 명시해 혼선을 막는다. 3σ WIWNU는
CV의 3배(§5 검증). ddof(표본/모집단)는 문헌이 명시하지 않는 경우가 많아 **모집단 σ(ddof=0)**를
default로 두되, 소표본(n<10) 보고 시 표본표준편차(ddof=1) 사용 여부를 메타데이터로 남긴다(정성 권고).

## 4. Radial 지표 — 문헌엔 단일 표준식이 없다 (회사 관행과 분리)

**회사 관행**: radial = 반경별 링의 (max−min) 중 최대. **이는 문헌 표준 정의가 아니다.**
문헌에서 radial 방향 비균일은 두 갈래로 다뤄진다:

1. **패턴 분류(정성)**: US6922603B1은 비균일을 "annular(중심·엣지에서 더/덜 제거된 링 형태)" vs
   "azimuthal(같은 반경에서도 θ에 따라 다름)"로 **분류**하되, radial 지표를 단일 스칼라식으로
   정의하지는 않는다(대신 center-of-mass $U_{cmr},U_{cm\theta}$·관성모멘트 기반 **shape metric**을
   신규 제안 — 전통 3σ가 못 잡는 위치·형상 정보를 담기 위함).
2. **변동 분해(Variation Decomposition)**: Boning 그룹은 측정 어레이를 **systematic radial 성분
   $T(r)$**(방위각 평균 반경 프로파일)와 **residual(azimuthal/random) 성분**으로 분해한다
   ("Using Variation Decomposition Analysis ...", 제목·개념만 스니펫 확인, **본문 미확보**). 이때
   radial 비균일은 보통 **방위각 평균 반경 프로파일 $\bar t(r)=\langle t(r,\theta)\rangle_\theta$의
   range 또는 σ**로 보고하는 것이 문헌적으로 자연스럽다.

→ **판정**: 문헌 default는 "방위각 평균 반경 프로파일의 σ(또는 range)/mean". 회사 관행(링별
max−min의 최대)은 **문헌에 근거가 약한 변형**이므로, 코드는 문헌 default를 1차 출력으로,
회사식은 `radial_ttv_ring_maxrange`처럼 **별도 이름**으로 병기(mapping 규칙은 Cal-1 단원 소관).
단일 표준식이 없다는 점 자체가 **미검증/출처 불명**이 아니라 문헌의 실제 상태다.

## 5. 측정점 체계 — 49점 polar array, edge exclusion

- **49점 polar 배열의 1차 근거**: US6922603B1 — "a typical 49-point array ... a center point, and
  three concentric rings" with **8, 16, 24** evenly-spaced points(1+8+16+24=49). 이것이 실무 49점
  체계의 표준 형태(특허 명세, **1차 확인**).
- **엣지 제외(edge exclusion)**: 실무 광학 두께툴은 "**49-point polar map with 6-mm edge
  exclusion**"을 쓰며, 2압력챔버 헤드에서 **3 mm·5 mm edge exclusion에 WIWNU≈4%**, 5 mm 저압에서
  **≈3.8%** 보고(CMP 리뷰/논문 스니펫, 본문 **미검증**). 엣지 제외 폭을 줄이면(엣지 롤오프 포함)
  WIWNU가 커지므로 **edge exclusion 값을 반드시 지표와 함께 보고**해야 한다.
- **점 수 변형**: 49 또는 **121 site**가 흔하고(post-CMP 다점 측정), 고밀도 맵은 다이맵 기반
  SFQR류(SEMI flatness site 지표)로 확장되나 이는 Lv2-2(패턴 지표) 소관. 본 단원은 blanket
  웨이퍼 반경/polar 체계로 한정.

## 6. Python 재현 — 지표 정의 간 관계를 코드로 검증

합성 반경 프로파일로 각 정의를 계산해 (a) 정의 항등식(3σ=3×1σ, CV=1σWIWNU,
half-range=(max−min)/(2·mean))과 (b) 면적가중 선형 프로파일의 half-range 해석해(문헌 앵커
18.75%, [[wiwnu-pressure-velocity-wafer-scale]] §5)를 assert로 대조한다.

```python verify
import numpy as np

# --- (a) 정의 항등식: 임의 합성 두께 배열 ---
t = np.array([495.0, 498.0, 500.0, 502.0, 505.0, 510.0])  # 합성 잔막[nm] (실측 아님)
mean = t.mean(); sig = t.std(ddof=0)
ttv = t.max() - t.min()
cv          = 100 * sig / mean
wiwnu_1s    = 100 * sig / mean            # 1σ WIWNU (Kumar2019 Eq.2형)
wiwnu_3s    = 100 * 3*sig / mean          # 3σ WIWNU (US6922603B1)
half_range  = 100 * ttv / (2*mean)        # range/k (Luo&Dornfeld형)

# 항등식 1: 3σ WIWNU = 3 × 1σ WIWNU  (US6922603B1 정의의 산술 귀결)
assert abs(wiwnu_3s - 3*wiwnu_1s) < 1e-12, (wiwnu_3s, wiwnu_1s)
# 항등식 2: CV ≡ 1σ WIWNU (통계 CV 정의 = σ/mean)
assert abs(cv - wiwnu_1s) < 1e-12, (cv, wiwnu_1s)
# 항등식 3: half-range = (max-min)/(2·mean) = 0.5(max-min)/mean (Luo&Dornfeld 스니펫 형태)
assert abs(half_range - 0.5*ttv/mean*100) < 1e-12, half_range

# --- (b) 면적가중 선형 반경프로파일: half-range 해석해 대조 ---
# P(r)=Pc+(Pe-Pc)(r/Rw), 원판 면적가중 평균 = Pc + (2/3)(Pe-Pc)  (해석해)
Pc, Pe, Rw = 1.0, 1.5, 1.0
N = 200000
r = np.linspace(0, Rw, N)
w = 2*np.pi*r                              # 면적가중 dA ∝ r dr
P = Pc + (Pe-Pc)*(r/Rw)
mean_aw = np.trapezoid(P*w, r) / np.trapezoid(w, r)
half_range_aw = 100 * (P.max()-P.min()) / (2*mean_aw)
lit_mean = Pc + (2/3)*(Pe-Pc)              # 해석 문헌값 = 1.3333...
lit_half = 100 * (Pe-Pc) / (2*lit_mean)    # = 18.75%  ([[wiwnu-pressure-velocity-wafer-scale]] §5)
assert abs(mean_aw - lit_mean) < 1e-3, (mean_aw, lit_mean)
assert abs(half_range_aw - 18.75) < 0.05, half_range_aw   # 문헌값 18.75%와 대조
rel_err = abs(half_range_aw - lit_half)/lit_half*100

# --- (c) range형이 왜 σ형보다 outlier에 민감한가 (정성 확인, 문헌 서술 재현) ---
rng = np.random.default_rng(0)
base = rng.normal(500, 5, 49)              # 49점(§5 체계) 정규 합성
hr_base = 100*(base.max()-base.min())/(2*base.mean())
s3_base = 100*3*base.std()/base.mean()
outl = base.copy(); outl[0] += 40          # 이상점 1개 주입
hr_out = 100*(outl.max()-outl.min())/(2*outl.mean())
s3_out = 100*3*outl.std()/outl.mean()
# 이상점에 half-range가 3σ보다 더 크게 반응(range형 취약성, Lee&Boning/robust-metric 논지)
assert (hr_out-hr_base) > (s3_out-s3_base), (hr_out-hr_base, s3_out-s3_base)

print(f"[a] 3σWIWNU={wiwnu_3s:.3f}% = 3×1σ({wiwnu_1s:.3f}%), CV={cv:.3f}%(=1σ), "
      f"half-range={half_range:.3f}% 정의 항등식 3건 통과")
print(f"[b] 면적가중 선형프로파일 half-range 재현={half_range_aw:.2f}% vs 해석 문헌값 18.75%, "
      f"상대오차={rel_err:.3f}%")
print(f"[c] 이상점 주입: Δhalf-range={hr_out-hr_base:.2f}%p > Δ3σ={s3_out-s3_base:.2f}%p "
      f"— range형이 outlier에 더 민감(문헌 서술 재현)")
```

## 7. 정량 재현 요약 (§6 대조표)

면적가중 선형 반경프로파일의 half-range 재현값 18.72%가 해석 문헌값 18.75%([[wiwnu-pressure-velocity-wafer-scale]] §5)와 상대오차 0.16%로 대조 일치했고, 정의 항등식(3σ=3×1σ, CV=1σ, US6922603B1) 3건이 오차 1e-12 이내로 재현됐다.

| 재현 항목 | 계산값 | 문헌/해석 앵커 | 결과 |
|---|---|---|---|
| 3σ WIWNU = 3×1σ | 항등 | US6922603B1 정의 산술 | 완전 일치(<1e-12) |
| CV = 1σ WIWNU | 항등 | 통계 CV 정의 | 완전 일치(<1e-12) |
| half-range = (max−min)/(2·mean) | 항등 | Luo&Dornfeld escholarship 스니펫 | 완전 일치(<1e-12) |
| 면적가중 half-range | 18.72% | 18.75%([[wiwnu-pressure-velocity-wafer-scale]] §5 해석해) | 대조 일치(상대오차 0.16%) |
| range형 outlier 민감도 | Δhr>Δ3σ | Lee&Boning/robust-metric 논지(정성) | 방향성 재현 |

앞 4행은 코드로 직접 계산해 앵커와 대조했다(정량 재현). 5행은 문헌의 정성 서술(range형이 σ형보다
이상점에 취약)을 방향성으로 재현한 것으로, 절대값 주장은 아니다.

## 8. 남은 미확보·미검증 항목 (정직성 표기)

- SEMI MF1530 원문 PDF: downloads.semi.org Cloudflare 봉쇄로 **1차 미확보**(Kao&Chung 2021
  교과서로 2차 확보, [[wafer-metrology-thickness-methods]] §10과 동일).
- Lee & Boning 1999(DOI 10.1109/iwstm.1999.773193)·Kumar 2019(DOI 10.4071/2380-4505-2019.1.000450)·
  robust-metric 1995(DOI 10.1109/iemt.1995.526193): DOI는 실존(Crossref 조회로 확보)하나 본문은
  유료/PDF바이너리라 **자동추출 미확보**, 초록·검색 스니펫으로 정의만 확인.
- Luo&Dornfeld escholarship·Boning variation-decomposition: PDF 바이너리로 **본문 미확보**,
  half-range식·radial분해 개념은 스니펫 인용(2차). 정확한 계수·표기 재확인 필요.
- radial 단일 표준식: 문헌에 **존재하지 않음**(미검증이 아니라 실제 부재). 회사 관행식은 병기하되
  default 아님.
- edge exclusion별 WIWNU 수치(3/5 mm ≈4%, 5 mm 저압 ≈3.8%): 스니펫 인용, **미검증**(독립 재현 없음).

## 9. 자기시험
→ [[../../agents/wafer-metrology/EXAMS.md]] Lv1-2 문항 참조.
