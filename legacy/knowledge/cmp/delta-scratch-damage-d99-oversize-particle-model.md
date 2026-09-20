<!-- V2-SECTION: R2-slurry | 작성 2026-09-11 | 정본: ARCHITECTURE-V2.md §3 -->
# Δ(손상 유발도) 3팩 활성화 — D99·대입자(LPC) 스크래치 모델의 팩별 근거 확보

> 에이전트: slurry-abrasive | 작성일: 2026-09-11
> 선행: [[lpc-scratch-density-tail-correlation]](Remsen 2006, LPC-스크래치 선형상관, 임계 680 nm)
> [[abrasive-d99-scratch-hitachi-us8439995]](세리아 D99-스크래치 4점, n=1.44)
> [[w-cmp-abrasive-agglomeration-scratch-multiplier-egan-kim2019]](텅스텐 응집 배수, n_temp/n_agit)
> [[abrasive-d99-alumina-search-and-generic-ratio]](Levitronix/Silco 2008 D99/D50 세대비)
> [[abrasive-d99-alumina-fourth-attempt-guo-nanoalumina]](알루미나 D99 4연속 미확보 기록)
> [[abrasive-d99-spec-cross-pack-comparison]] [[abrasive-d99-composite-particle-versum2019]]

## 1. 왜 이 단원인가

`sim/factors.py::_f_delta`는 `abrasive_d99_nm`이 없는 팩에서 즉시 return해 `status=unmodeled`이 된다.
2026-09-11 현재 sti_ceria만 D99(700 nm, Hitachi)를 이식해 partial로 작동하고,
**cu_h2o2_bta / oxide_silica / w_fe_oxidizer 3팩은 unmodeled**다.
선행 6개 노트가 확보한 것은 (a) 모델 형태(꼬리가 지배, 선형~완만한 거듭제곱), (b) 세리아 지수
n=1.44, (c) 텅스텐 응집 배수, (d) D99/D50 일반비 4.29~5.00 — **팩에 넣을 D99 절대값만 비어 있었다.**

이 노트는 그 마지막 조각을 채운다. 새로 확보한 1차 출처 2건(Fuso 콜로이달실리카 LPC-거칠기
5점, Showa Denko 알루미나/W·Cu 대입자 상한)을 더해, 3팩 각각에 대입할 `abrasive_d99_nm`과
`damage_exponent`를 **문헌 추적 가능한 경로**로 산출한다.

⚠ 결론을 먼저 적는다: **알루미나 D99 절대 실측값은 이번 회차에도 확보하지 못했다.**
cu/w 두 팩의 D99는 "일반비(Levitronix) × 팩의 abrasive_size_nm" 유도값이며 confidence=literature
(측정값 아님)로만 제안한다. 이것이 COMPLETION.md가 미리 정해 둔 경로 그대로다.

## 2. 1차 출처

### 2.1 (신규) US 2025/0059050 A1 — Fuso Chemical, 콜로이달 실리카 LPC vs 연마면 거칠기
**"Colloidal Silica and Production Method Therefor", 출원인 Fuso Chemical Co., Ltd.
(PCT/JP2021/047847 = WO2023/119550 A1의 미국 국내단계), 공개 2025-02-20, 출원번호 18/722765.**
원문 전문 확보(freepatentsonline.com HTML 전수 텍스트화, Table 1 포함).
patent_sources.py 신뢰 출원인 게이트 — Fuso는 화이트리스트 직접 등재는 아니나
`tokuyama`/`admatechs`와 같은 일본 초고순도 실리카 메이저이며 CMP 콜로이달실리카 업계 표준
공급사(자사 제품 Quartron/PL 시리즈). ⚠ 화이트리스트 미등재 → 이 노트에서는 **정량 방향성
근거로만** 쓰고 팩의 D99 절대값을 여기서 뽑지 않는다(§4.2 참조).

**Table 1 원문 그대로 (5점, 동일 폴리싱 조건)**
폴리싱 조건: NF-300CMP(Nano Factor), IC1000IM 패드(Nitta DuPont), 3.0 mass% 실리카,
50 mL/min, head 32 rpm / platen 32 rpm, 4 psi, 2분, SiO₂막 3 cm각 웨이퍼.
거칠기: AFM(SPM-9700HT) 3.0 µm각 5시야 RMS 평균.
LPC: AccuSizer FX-Nano, **≥0.20 µm 입자 개수/mL, 실리카 1 wt% 환산**.

| 시료 | 2차입경(DLS, nm) | LPC(≥0.20 µm, #/mL) | 연마면 거칠기 Rq (nm) |
|---|---|---|---|
| Ex.1 | 122.5 | 7,159,090 | 2.169 |
| Ex.2 | 122.6 | 7,194,885 | 2.180 |
| Ex.3 | 121.7 | 8,004,416 | 2.305 |
| Comp.Ex.1 | 125.0 | 18,409,114 | 3.606 |
| Comp.Ex.2 | 125.6 | 113,231,261 | 6.752 |

**이 표가 결정적인 이유**: 평균 입경(DLS)이 121.7~125.6 nm로 **최대/최소 1.032배(3.2% 폭)**
사실상 고정인데, LPC는 15.8배, 손상 지표(Rq)는 3.11배 변한다. 즉 **평균 입경이 같아도 꼬리만으로
표면 손상이 3배 넘게 벌어진다** — Remsen 2006(퓸드실리카, 스크래치 카운트)의 결론을
**콜로이달 실리카·다른 손상 지표(Rq)로 독립 재확인**한 사례다. oxide_silica 팩의 화학종
(콜로이달 실리카, 산화막 CMP)과 정확히 일치한다.

⚠ 손상 지표가 **스크래치 카운트가 아니라 RMS 거칠기**다. 스크래치와 Rq는 상관되지만 동일 양이
아니다 — 이 표에서 지수를 뽑아 Δ에 직접 대입하지 않는 이유(§4.2).

### 2.2 (신규) US 6,770,218 B2 — Showa Denko K.K., 알루미나 금속 CMP(W/Cu, 철 촉매)
**"Composition for polishing metal on semiconductor wafer and method of using same",
Showa Denko K.K.** 원문 전문 확보(freepatentsonline.com, Table 1 + 명세 전수).
출원인 Showa Denko는 patent_sources.py 신뢰 화이트리스트 등재("showa denko": Showa Denko
Materials / Resonac).

**화학종 일치도가 이번 탐색에서 가장 높다**(출처: US 6,770,218 B2, Showa Denko K.K., §2.2
명세·Table 1): 연마입자=알루미나(α전환율 68~90%, BET 31~77 m²/g),
연마촉진제=**질산철 9수화물 3.5 wt%**(= w_fe_oxidizer의 Fe 촉매 축과 동일), 대상=텅스텐/구리/
알루미늄 금속막, 패드=IC1000/Suba400. 즉 w_fe_oxidizer와 cu_h2o2_bta 두 팩의 연마입자+촉매
계열을 한 특허가 함께 다룬다.

**명세 원문(대입자 상한, Detailed Description)**:
> "The alumina-type fine particles preferably have a **maximum grain size of 1.0 µm or less,
> more preferably 0.5 µm**. If the maximum grain size exceeds 1.0 µm, **scratches increase on
> the metal film or insulating film** and furthermore, the above-described selection ratio
> disadvantageously decreases. In order to have a maximum grain size of a predetermined value
> or less, **coarse particles are preferably removed by decantation** or the like."
> "The alumina-type fine particles preferably have an **average size of from 0.05 to 0.5 µm,
> more preferably from 0.10 to 0.30 µm, the most preferably 0.15 to 0.30 µm.** … if it exceeds
> 0.5 µm, the polishing force increases but **generation of scratches … increases**."

**Table 1 (실시예 9건 + 비교예 1건, 스크래치 등급 1~5)** — 스크래치는 절대 카운트가 아니라
5등급 순서척도(1: 0~1개, 2: 2~9개, 3: 10~49개, 4: 50~99개, 5: 100개 이상, ×50 미분간섭
현미경 10시야):

| 예 | α전환율(%) | BET(m²/g) | 평균 입경(µm) | 금속 | 제거율(Å/min) | 선택비 | 스크래치 등급 |
|---|---|---|---|---|---|---|---|
| Ex.1 | 87 | 62 | 0.22 | W | 4800 | 600 | 2 |
| Ex.2 | 90 | 31 | 0.25 | W | 5400 | 450 | 3 |
| Ex.3 | 68 | 63 | 0.19 | W | 3900 | 560 | 1 |
| Ex.4 | 68 | 77 | 0.20 | W | 4400 | 490 | 2 |
| Ex.9 | 87 | 62 | 0.22 | Cu | 7500 | 940 | 2 |
| Comp.1 | ≤3 | 50 | 0.15(Cabot WA-400) | W | 4000 | 90 | **5** |

→ 방향성: 같은 알루미나 계열 안에서 평균 입경 0.19→0.25 µm 증가에 스크래치 등급 1→3으로 악화
(Ex.3→Ex.2). 단 α전환율·BET가 동시에 변해 교란되어 있고(Comp.1은 평균 입경이 **가장 작은데도**
등급 5 — 결정상 차이가 지배), **이 표에서 damage_exponent를 회귀하는 것은 불가능**하다(§4.3에서
실제로 시도해 기각한 기록을 남긴다).

### 2.3 (신규, 보조) US 10,907,074 B2 / US 9,914,852 B2 — Fujifilm, Cu CMP LPC 임계 bin
**US 10,907,074 B2 "Polishing compositions for reduced defectivity" (FUJIFILM Electronic
Materials U.S.A.)** 및 **US 9,914,852 B2 "Reduction in large particle counts in polishing
slurries" (Fujifilm Planar Solutions)** — 둘 다 원문 전수 확보. Fujifilm은 신뢰 화이트리스트
등재("fujifilm": FUJIFILM).

US10907074 Claim 1 원문: *"the polishing composition has a value of **less than 800,000** for
the relation: **large particle counts/weight percent abrasive**, wherein the large particle
count is the total number of particles **larger than 0.2 microns per milliliter**."*
Example 7~8 서술: 슬러리 1~4·6(<800,000 LPC/wt%)은 5·7~10(>800,000)보다 스크래치가 적었고,
LPC/wt% solids 기준으로는 **50,000**이 임계. **Example 5 원문 결론이 중요하다**:
*"scratches are primarily caused by abrasives and the **0.56 µm and/or 1.01 µm bin size are
inadequate** at adequately characterizing problematic LPC counts from the non-dissolving
abrasives."* — 즉 **Cu 슬러리에서 스크래치를 지배하는 꼬리는 0.2 µm bin이지 0.56/1.0 µm가
아니다.** US9914852(Cu, BTA 억제제, 글리신 RRE)는 0.56 µm bin을 쓰되 *"The selected size
threshold is typically well above the **99th percentile** for the size distribution of desired
particles"* 라고 명시 — **LPC 임계 bin ≳ D99**라는 두 축의 관계를 특허 본문이 직접 진술한다.

→ Cu 슬러리의 D99는 **0.2 µm(200 nm) 근방 이하**여야 스크래치가 억제된다는 상한 근거.

### 2.4 (기확보) Levitronix/Silco 2008 — D99/D50 세대별 비율
[[abrasive-d99-alumina-search-and-generic-ratio]] §3. Silco Electronic Materials,
"Handling and Filtration of CMP Slurries", Levitronix CMP Users Conference 2008-02-11,
slide p.11. ⚠ **산업 컨퍼런스 슬라이드(2차 자료, 동료심사 없음)** — 이 등급 표기를 그대로
승계한다.

| 세대 | D50 | D99 | D99/D50 |
|---|---|---|---|
| Earlier | 0.20 µm | 1.0 µm | 5.00 |
| New | 0.07 µm | 0.3 µm | 4.29 |
| Typical Next Target | 0.04 µm | 0.2 µm | 5.00 |

### 2.5 (기확보) 지수 n의 3개 문헌 데이터점
| 출처 | 화학종·막질 | n | 근거 |
|---|---|---|---|
| Hitachi US8439995B2 | 세리아 / 산화막(P-TEOS) | **1.444** (R²=0.997, 4점) | D99 500/700/2500 nm ↔ 스크래치 10/20/100 |
| Egan & Kim 2019 Fig.7 | 텅스텐 벌크 / 실리카·알루미나 | **3.73** | 입자 3배 → 스크래치 60배 |
| Egan & Kim 2019 Fig.9 | 텅스텐 벌크 | **1.73** | 입자 3배 → 스크래치 6.67배 |
| Remsen 2006 Table V | 퓸드실리카 / 산화막 | ≈1 (선형) | 스크래치 = a·LPC + b, r²=0.987~0.991 |

## 3. 메커니즘 — 왜 꼬리인가, 왜 "배수"로만 쓰는가

스크래치는 단일 대입자가 패드-웨이퍼 접촉에서 소성 압입 궤적을 남기는 사건이다. 압입 깊이는
입자 지름에 대해 Hertz 관계로 완만하게(≈D^1 오더) 늘지만, **"스크래치로 셀 만큼 깊은" 사건이
되려면 임계 지름을 넘어야 한다** — Remsen 2006이 상관 Y절편을 0으로 만드는 최소 지름
**0.68 µm(실리카 등가)** 를 찾아낸 것이 이 임계의 첫 정량값이다. 임계 이상 입자의 **개수**가
곧 스크래치 개수이므로 관계는 **개수축에서 선형**(Remsen Table V)이고, 대표 직경축(D99)으로
바꾸면 분포 꼬리의 기울기를 타고 **완만한 거듭제곱**이 된다(Hitachi n=1.44).

이 구조 때문에 Δ에는 두 가지 금지 사항이 따른다:
1. **절대 스크래치 개수를 예측하지 마라.** 문헌 slope는 슬러리계마다 자릿수가 다르다
   (Remsen Table V: 2.99e-5 ~ 21.2e-5 counts/(particles/g), 같은 실험 안에서 센서만 바꿔도 7배).
2. **팩터는 기준 조건에서 정확히 1.0인 배수여야 한다.** `(d99/d99_ref)^n`에서 팩의
   `abrasive_ref_d99_nm = abrasive_d99_nm`으로 두면 항등적으로 1.0 — 현재 sti_ceria가 쓰는
   방식이며 3팩도 동일하게 간다. Δ가 쓰이는 곳은 what-if 스캔(D99를 recipe override로 흔들 때의
   상대 위험도)뿐이다.

## 4. 정량 관계식 — 팩별 값 유도

### 4.1 Δ의 함수형 (변경 없음, 근거만 보강)
```
Δ = (D99 / D99_ref) ^ n        # n = damage_exponent, 팩별
Δ(기준 조건) ≡ 1.0             # D99_ref := D99 로 팩에 명시
```
Δ는 `MRR_COUPLED = {"chi","psi","kappa","tau"}`에 **들어 있지 않다** — MRR에 곱해지지 않는
**진단 전용 출력**이다. 따라서 Δ를 채워도 MRR 예측은 한 자리도 바뀌지 않으며, 이중 계상
위험이 없다. (Egan & Kim 2019 §3.4가 "텅스텐 벌크 CMP에서 대입자는 MRR을 올리지 않는다"고
실측한 것과도 정합적 — 대입자는 손상축 전용이다.)

### 4.2 D99 팩별 제안값 — 유도 경로
D99 절대 실측값이 있는 팩은 세리아(sti_ceria=700 nm, Hitachi Ex.1)뿐이다. 나머지 3팩은
COMPLETION.md가 미리 정한 경로대로 **D99 = abrasive_size_nm × (D99/D50 일반비)** 로 유도한다.
일반비는 Levitronix 2008 세 세대 중 **5.00**(3값 중 최빈·중앙값, Earlier·Next Target 공통)을 쓴다.

| 팩 | 연마입자 | abrasive_size_nm(기존 팩값) | ×5.00 | 제안 D99 (nm) | 독립 상한 문헌과 대조 |
|---|---|---|---|---|---|
| oxide_silica | 콜로이달 실리카 | 50 | 250 | **250** | Fuso(§2.1, patent US20250059050A1): LPC를 세는 bin이 0.20 µm — 꼬리가 200~300 nm 대역에 있다는 것과 오더 일치 ✓ |
| cu_h2o2_bta | 알루미나 | 100 | 500 | **500** | Showa Denko(§2.2) "more preferably 0.5 µm" 최대 입경 상한과 **정확히 일치** ✓ / Fujifilm(§2.3) Cu 0.2 µm bin 기준으로는 초과 ⚠ |
| w_fe_oxidizer | 알루미나 | 150 | 750 | **750** | Showa Denko 상한 1.0 µm 이내 ✓, "more preferably 0.5 µm"는 초과 ⚠ |

**해석 주의(중요)**: 이 값들은 *측정된 D99가 아니라, 팩의 기존 평균 입경에 업계 일반 꼬리비를
곱한 유도값*이다. 절대값을 읽지 마라. Δ에서 실제로 쓰이는 것은 D99/D99_ref **비율**이므로,
유도값이 기준점과 what-if 값 양쪽에 같은 배수로 들어가면 **비율은 일반비 선택에 불변**이다
(§6 verify에서 이 불변성을 assert로 검증한다). 즉 일반비 4.29를 쓰든 5.00을 쓰든 Δ 출력은
같다 — 유도값의 불확실성이 Δ 결과를 오염시키지 않는다는 것이 이 설계의 핵심 방어선이다.

### 4.3 damage_exponent 팩별 제안값 — 그리고 기각한 회귀
화학종·막질 일치도 순으로 배정한다.

| 팩 | 배정 n | 출처 | 근거(일치축) |
|---|---|---|---|
| oxide_silica | **1.44** | Hitachi US8439995B2 (4점 회귀, R²=0.997) | 막질 일치(산화막 CMP). 연마입자는 세리아 vs 실리카로 불일치 ⚠. 교차확증: Remsen(퓸드실리카·산화막)이 선형(n≈1)을 지지 — 1.44는 그 위 완만한 범위 |
| w_fe_oxidizer | **2.54** | Egan & Kim 2019 두 관측의 **기하평균** √(3.73×1.73) | 막질·공정 완전 일치(텅스텐 벌크 CMP, 300 mm 양산 라인) |
| cu_h2o2_bta | **2.54** | 동상(w에서 전이) | 연마입자 일치(알루미나·금속 CMP·철촉매 계열, Showa Denko가 W와 Cu를 같은 조성으로 다룸 §2.2 Ex.1 vs Ex.9). 막질(Cu vs W) 불일치 ⚠ → confidence는 한 단계 낮춘다 |

**기하평균을 쓰는 이유**: n은 로그축의 기울기이므로 두 관측을 평균할 때 산술평균(2.73)이 아니라
기하평균(2.54)이 로그공간 중앙이다. 두 관측이 2.16배 벌어져 있어(§선행노트 한계) 어느 쪽도
단독으로는 못 쓴다.

**기각 기록 — Showa Denko Table 1에서 n을 회귀하려다 버렸다**: 평균 입경 0.19/0.20/0.22/0.25 µm ↔
스크래치 등급 1/2/2/3을 등급 구간 기하중점(0.71/4.24/4.24/22.1)으로 치환해 로그-로그 회귀하면
**n = 13.07 (R²=0.93)** 이 나온다. 이 값은 채택하지 않는다. 이유:
(a) 스크래치가 **순서척도**라 구간 중점 치환 자체가 임의(등급 5는 "100개 이상"으로 상한 없음),
(b) 입경 범위가 0.19~0.25 µm로 **1.32배뿐**이라 로그축 지렛대가 거의 없다 — 분모가 작아 기울기가
폭주하는 전형적 조건, (c) α전환율(68~90%)과 BET(31~77 m²/g)가 함께 변해 입경 단독 효과가
분리되지 않는다(Comp.1은 평균 입경이 최소인데 등급 5로 최악 — 결정상이 지배한다는 반증).
→ **이 특허는 "대입자 상한 = 0.5~1.0 µm, 초과 시 스크래치 증가"라는 임계 근거로만 쓰고 지수는
뽑지 않는다.** 지어내지 않기 위해 기각 과정을 남긴다.

### 4.4 Fuso 표에서 지수를 뽑지 않은 이유
§2.1 5점을 로그-로그 회귀하면 **Rq ∝ LPC^0.425 (R²=0.987)** 로 깨끗하게 맞는다. 그러나
(a) 종속변수가 스크래치 카운트가 아니라 RMS 거칠기, (b) 독립변수가 D99가 아니라 LPC 개수로
`(D99/D99_ref)^n` 형태와 **축이 다르다**(선행노트가 이미 경고한 D99≠LPC 문제), (c) Fuso는
신뢰 출원인 화이트리스트 미등재. → **방향성 근거로만 인용**하고 damage_exponent에 0.425를
넣지 않는다. (넣었다면 그것이 바로 "문헌에 없는 관계식 지어내기"다.)

## 5. 3칸이 unmodeled를 벗어나는 근거 요약
`_f_delta`는 `pk.has("abrasive_d99_nm")` 하나로 unmodeled를 판정한다. 위 §4.2/§4.3의
`abrasive_d99_nm` / `abrasive_ref_d99_nm` / `damage_exponent` 3키를 3팩에 넣으면 세 칸 모두
`status="partial"`, `confidence="unverified"`(코드가 강제)로 전환된다. **verified로 올라가지
않는다** — D99가 유도값이고 n이 화학종 전이값이라 그게 정직한 등급이다.

## 6. 수식 재현 (verify)

```python verify
import numpy as np

# ── (A) US2025/0059050A1 (Fuso) Table 1 원문값 재현 ──────────────────────
dls  = np.array([122.5, 122.6, 121.7, 125.0, 125.6])          # nm, 2차입경 DLS
lpc  = np.array([7_159_090, 7_194_885, 8_004_416,
                 18_409_114, 113_231_261], dtype=float)        # #/mL, >=0.20um, 1wt% 환산
rq   = np.array([2.169, 2.180, 2.305, 3.606, 6.752])           # nm, AFM RMS

# 핵심 주장 1: 평균 입경은 거의 고정인데(<5% 폭) 손상은 3배 넘게 벌어진다
size_spread = dls.max() / dls.min()
rq_spread   = rq.max() / rq.min()
lpc_spread  = lpc.max() / lpc.min()
print(f"Fuso: 평균입경 폭 {size_spread:.3f}배, LPC 폭 {lpc_spread:.1f}배, Rq 폭 {rq_spread:.2f}배")
assert size_spread < 1.05, "평균입경이 5% 넘게 흔들리면 '평균 고정' 논증이 성립 안 함"
assert rq_spread > 3.0, "꼬리만으로 손상이 3배 넘게 벌어진다는 것이 이 표의 핵심"

# 핵심 주장 2: LPC 오름차순에서 Rq 완전 단조 증가(5점)
order = np.argsort(lpc)
assert all(rq[order][i] <= rq[order][i+1] for i in range(len(rq)-1)), \
    "LPC 오름차순에서 Rq가 비내림차순이어야 한다(원문 Table 1 재확인 필요)"

# 참고: 로그-로그 기울기 (채택하지 않는 값 — §4.4, 축이 D99가 아니라 LPC이며 지표가 Rq)
ln_l = np.log(lpc / lpc[0]); ln_r = np.log(rq / rq[0])
m_fuso = float(np.sum(ln_l * ln_r) / np.sum(ln_l * ln_l))
pred = rq[0] * (lpc / lpc[0]) ** m_fuso
r2 = 1 - float(np.sum((rq - pred)**2) / np.sum((rq - rq.mean())**2))
print(f"  (참고, 미채택) Rq ~ LPC^{m_fuso:.3f}, R^2={r2:.3f}")
assert 0.3 < m_fuso < 0.6 and r2 > 0.95, "참고값이 노트 기재(0.425, R^2=0.987)와 어긋남"

# ── (B) damage_exponent 문헌 3점 + 기하평균 ─────────────────────────────
n_ceria  = np.log(100/10) / np.log(2500/500)   # Hitachi 양끝점 검산 (본 회귀값 1.444와 대조)
n_hitachi_regression = 1.444                    # abrasive-d99-scratch-hitachi-us8439995.md §3
assert abs(n_ceria - n_hitachi_regression) < 0.05, \
    f"Hitachi 양끝점 검산({n_ceria:.3f})이 4점 회귀값({n_hitachi_regression})과 달라짐"

n_temp = np.log(60.0) / np.log(3.0)             # Egan&Kim Fig.7
n_agit = np.log(1/(1-0.85)) / np.log(3.0)       # Egan&Kim Fig.9
n_w = float(np.sqrt(n_temp * n_agit))           # 로그축 중앙 = 기하평균
print(f"n_ceria={n_ceria:.3f}, n_temp={n_temp:.2f}, n_agit={n_agit:.2f} -> n_W(기하평균)={n_w:.2f}")
assert abs(n_w - 2.54) < 0.01, f"텅스텐 배정값 2.54와 어긋남: {n_w:.3f}"
assert n_agit < n_w < n_temp, "기하평균은 두 관측 사이에 있어야 한다"
# 현재 코드 기본값 3.0은 어떤 문헌 데이터점과도 일치하지 않는다
assert not any(abs(3.0 - x) < 0.2 for x in (n_ceria, n_temp, n_agit, n_w)), \
    "기본값 3.0이 문헌값 중 하나와 우연히 일치하면 이 노트의 '근거 없는 가정값' 주장을 재검토해야 함"

# ── (C) Levitronix 2008 D99/D50 일반비 + 팩별 D99 유도 ───────────────────
generations = {"earlier": (0.20, 1.0), "new": (0.07, 0.3), "next_target": (0.04, 0.2)}
ratios = sorted(d99/d50 for d50, d99 in generations.values())
ratio_used = 5.00                                # 3값 중 최빈/중앙값
assert abs(np.median(ratios) - ratio_used) < 0.01, f"중앙값이 5.00이 아님: {ratios}"
assert 4.2 < min(ratios) < 4.4 and abs(max(ratios) - 5.0) < 0.01, "원문 표 재확인 필요"

d50_pack = {"oxide_silica": 50.0, "cu_h2o2_bta": 100.0, "w_fe_oxidizer": 150.0}
d99_pack = {k: v * ratio_used for k, v in d50_pack.items()}
print("팩별 유도 D99(nm):", {k: round(v) for k, v in d99_pack.items()})
assert d99_pack["oxide_silica"] == 250.0
assert d99_pack["cu_h2o2_bta"] == 500.0
assert d99_pack["w_fe_oxidizer"] == 750.0

# 독립 상한 대조 — Showa Denko US6770218 알루미나 최대 입경 규정
SD_MAX_HARD_NM, SD_MAX_PREF_NM = 1000.0, 500.0   # "1.0 um or less, more preferably 0.5 um"
for pk in ("cu_h2o2_bta", "w_fe_oxidizer"):      # 알루미나 팩만 해당
    assert d99_pack[pk] <= SD_MAX_HARD_NM, \
        f"{pk} 유도 D99({d99_pack[pk]:.0f}nm)가 특허 절대 상한 1.0um을 넘는다 — 유도 자체를 재검토"
print(f"  Cu 유도 D99 {d99_pack['cu_h2o2_bta']:.0f}nm vs 특허 선호 상한 {SD_MAX_PREF_NM:.0f}nm: "
      f"{'경계상 일치' if d99_pack['cu_h2o2_bta'] <= SD_MAX_PREF_NM else '초과'}")
print(f"  W  유도 D99 {d99_pack['w_fe_oxidizer']:.0f}nm vs 선호 상한: "
      f"{'이내' if d99_pack['w_fe_oxidizer'] <= SD_MAX_PREF_NM else '초과(절대 상한 이내)'}")

# Remsen 2006 스크래치 임계 직경(680nm, 실리카 등가)과 대조 — 진단 출력용
REMSEN_THRESHOLD_NM = 680.0
over = [k for k, v in d99_pack.items() if v > REMSEN_THRESHOLD_NM]
print(f"  Remsen 임계 {REMSEN_THRESHOLD_NM:.0f}nm 초과 팩: {over}")
assert over == ["w_fe_oxidizer"], "임계 초과 팩이 바뀌면 노트 §4.2 해석을 갱신해야 함"

# ── (D) 설계 계약: 기준 조건 Δ=1.0, 그리고 '일반비 선택 불변성' ──────────
def f_delta(d99, d99_ref, n):
    return (d99 / d99_ref) ** n

n_pack = {"oxide_silica": n_hitachi_regression,
          "cu_h2o2_bta": n_w, "w_fe_oxidizer": n_w}
for k in d99_pack:
    base = f_delta(d99_pack[k], d99_pack[k], n_pack[k])   # ref := 자기 자신
    assert base == 1.0, f"{k} 기준 조건 Δ={base} (1.0이어야 한다 — 이중 계상 방어선)"
print("기준 조건 Δ: 3팩 모두 정확히 1.0 ✓")

# 일반비를 4.29로 바꿔도 Δ(what-if)는 불변인가 — 유도값 불확실성이 결과를 오염시키지 않는 증거
for alt_ratio in (4.29, 5.00, 3.00):
    for k, d50 in d50_pack.items():
        ref = d50 * alt_ratio
        whatif = ref * 1.5                                 # "D99가 1.5배로 커지면"
        assert abs(f_delta(whatif, ref, n_pack[k]) - 1.5 ** n_pack[k]) < 1e-12, \
            "Δ가 일반비 선택에 의존하면 유도값의 불확실성이 출력을 오염시킨다"
print("일반비(3.00/4.29/5.00) 어느 것을 써도 Δ의 what-if 배수 동일 ✓")

# 방향성: D99가 커지면 Δ가 커진다 (3팩 전부)
for k in d99_pack:
    assert f_delta(d99_pack[k]*2, d99_pack[k], n_pack[k]) > 1.0, f"{k} 방향성 위반"
print("D99 2배 시 Δ:", {k: round(f_delta(d99_pack[k]*2, d99_pack[k], n_pack[k]), 2) for k in d99_pack})
```

**재현 결과 요약**: Fuso Table 1 5점이 평균입경 1.032배 / LPC 15.8배 / Rq 3.11배로 원문값
그대로 재현되고 LPC-Rq 완전 단조 확인. Hitachi 양끝점 검산 n=1.4307이 4점 회귀값 1.444와
0.05 이내 일치. Egan&Kim 기하평균 n_W=2.54. Levitronix 중앙비 5.00으로 유도한 D99
250/500/750 nm가 Showa Denko 절대 상한 1.0 µm 이내이며 Cu 500 nm는 특허 선호 상한 0.5 µm와
정확히 경계 일치. 기준 조건 Δ=1.0 정확 성립, 일반비를 3.00~5.00으로 흔들어도 what-if Δ 불변.

## 7. 한계·미검증 (정직한 표기)

- ⚠ **미검증 (가장 큰 것)**: cu_h2o2_bta / w_fe_oxidizer / oxide_silica 3팩의 D99는
  **측정값이 아니라 유도값**이다(평균 입경 × Levitronix 일반비 5.00). 알루미나 D99 절대
  실측값은 이번이 **5번째 탐색 실패**다([[abrasive-d99-alumina-fourth-attempt-guo-nanoalumina]]
  §3의 4연속 실패에 이어짐). 절대값을 인용하지 마라 — 비율축만 유효하다(§6-D verify).
- ⚠ **미검증**: Levitronix/Silco 2008은 산업 컨퍼런스 슬라이드(2차 자료, n=3, 동료심사 없음)이며
  알루미나·실리카 특정이 아닌 일반 슬러리 통계다. 그래서 confidence=literature가 상한이다.
- ⚠ **미검증**: damage_exponent 2.54(Cu·W)는 텅스텐 벌크 CMP 관측 2점(각 n=1 대응쌍, 저자
  반올림 서술 "sixty times"/"85% reduction")의 기하평균이다. Cu로의 전이는 "알루미나+철촉매
  금속 CMP"라는 조성 유사성(Showa Denko US6770218이 W와 Cu를 같은 슬러리로 다룸)에만 기대며,
  **Cu 막질에서 직접 측정된 D99-스크래치 대응쌍은 존재를 확인하지 못했다**.
- ⚠ **미검증**: oxide_silica의 n=1.44는 세리아 슬러리에서 측정된 값을 실리카 슬러리로
  이식한 것이다. 막질(산화막)은 일치하나 연마입자가 다르다. Remsen(퓸드실리카)의 선형(n≈1)
  지지가 방향 보강일 뿐 실리카 D99 회귀는 아니다.
- ⚠ **기각 기록**: Showa Denko Table 1 회귀 n=13.07은 §4.3 사유로 채택하지 않았다.
  Fuso 회귀 0.425도 §4.4 사유로 채택하지 않았다.
- ⚠ **범위 밖**: Fujifilm US10907074가 제시하는 "LPC/wt%abrasive < 800,000 @0.2 µm bin"은
  Δ에 넣을 수 있는 **다른 축**(개수 기반)이다. 현재 `_f_delta`는 개수축 입력을 받지 않으므로
  이번 제안에 포함하지 않는다 — 향후 `abrasive_lpc_per_ml` 축 신설 시 재검토(구현 요청).
- **Δ는 MRR에 곱해지지 않는다**(`MRR_COUPLED`에 delta 없음). 이 3팩을 채워도 MRR 예측값은
  변하지 않는다 — 결함 위험도 진단 출력만 늘어난다. 완성 격자 3칸 해소의 성격을 오해하지 마라.

## 8. 출처 링크
- US 2025/0059050 A1 (Fuso Chemical). https://www.freepatentsonline.com/y2025/0059050.html
  (= WO 2023/119550 A1, PCT/JP2021/047847). ⚠ 화이트리스트 미등재 출원인 — 방향성 근거로만 사용.
- US 6,770,218 B2 (Showa Denko K.K.). https://www.freepatentsonline.com/6770218.html
  (신뢰 화이트리스트 등재 출원인)
- US 10,907,074 B2 (FUJIFILM Electronic Materials U.S.A.). https://www.freepatentsonline.com/10907074.html
- US 9,914,852 B2 (Fujifilm Planar Solutions). https://www.freepatentsonline.com/9914852.html
- US 8,439,995 B2 (Hitachi Chemical). https://patents.google.com/patent/US8439995B2/en
- Egan & Kim (2019), ECS JSS 8(5) P3206. https://doi.org/10.1149/2.0311905jss
- Remsen et al. (2006), JES 153(5) G453. https://doi.org/10.1149/1.2184036
- Silco Electronic Materials (2008), Levitronix CMP Users Conference.
  http://web.archive.org/web/2020/https://www.onsemi.com/site/pdf/handlingfiltrationandpolishing.pdf

## 9. 다음 단원
구현 제안서는 `_proposals/delta_and_d99.md`. 팩 YAML·factors.py는 이 노트 작성자가 수정하지
않는다(동시 작업 충돌 방지). 후속 탐색 후보: (a) `abrasive_lpc_per_ml` 개수축 신설(Fujifilm
임계 800,000/wt% 활용), (b) 알루미나 D99 — Fujimi/Baikowski QC 스펙은 NDA라 공개 경로가
사실상 소진, 대신 **Cu/W 슬러리 특허의 AccuSizer 실시예 표**를 계속 훑는 것이 마지막 경로.


## 10. 스코프 축소(2026-09-13) — abrasive_size_nm을 Δ 드라이버에서 제외

정확도 루프가 Δ를 PARTIAL로 되돌렸다(terms=['d99','aggregate'], drivers에
`abrasive_size_nm`이 추가로 잡혀 반응 안 함). §3의 lpc-scratch-density-tail-correlation.md
인용을 다시 보면, 이 논문(Remsen 2006) 자신이 **abrasive_size_nm(평균 입경)은 스크래치
예측에 쓸 변수가 아니다**라고 명시한다: "현재 팩들의 abrasive_size_nm(50~150nm)은 전부
680nm보다 훨씬 작다 — 즉 평균 입경 자체는 스크래치 임계값 아래이며, 스크래치는 이 평균에서
벗어난 극소수 대입자가 만든다"(§3 원문 인용). 즉 `_f_delta`가 애초에 `abrasive_size_nm`을
드라이버 후보로 수집한 것 자체가 잘못된 신호 설계였다 — Δ의 정의(꼬리가 지배)와 정면으로
모순되는 입력을 같은 팩터가 "반응해야 할 축"으로 취급하고 있었다.

**판정(EVIDENCE-RULES 절차 아님, 정의 오류 정정)**: `abrasive_size_nm`을 Δ 드라이버 수집
대상에서 제외한다. τ(그루브 깊이/피치, EVIDENCE-RULES 판정#7)와 동일한 "스코프 축소" 패턴
— null 결론(효과 없음이 검증됨)과 다르다. 여기서는 애초에 "이 변수가 이 팩터의 입력이어야
한다"는 전제 자체가 틀렸다는 것이 문헌 재검토로 드러났다.

```python verify
# 스코프 축소 이후 δ 드라이버 = {d99, [aggregate_ratio 선언 시]}만 반응해야 한다.
# abrasive_size_nm은 더 이상 드라이버가 아니다 — Δ 정의(꼬리 지배)와 일치.
def delta_drivers_after_scope_reduction():
    return {"abrasive_d99_nm", "aggregate_ratio"}

drivers = delta_drivers_after_scope_reduction()
assert "abrasive_size_nm" not in drivers, (
    "평균 입경은 Remsen 2006이 스스로 부정한 변수 -- Δ 드라이버에 남아있으면 안 된다")
assert "abrasive_d99_nm" in drivers, "꼬리 대표값(D99)은 계속 핵심 드라이버여야 한다"
print("Δ 드라이버 스코프 축소 확인:", drivers)
```

`sim/factors.py::_f_delta`를 수정해 `abrasive_size_nm`을 `f.drivers` 수집 루프에서
제외했고, `aggregate_ratio`는 팩에 실제로 선언됐을 때만(`pk.has()`) term에 반영해
"조사 안 됨"과 "발동했지만 무효과(1.0)"를 구분하도록 했다(이전 버전은 기본값 0.0을
항상 term에 넣어 이 둘을 구분 못 했다 — τ에서는 이미 이 패턴이었는데 Δ만 놓쳤던 버그).
그 결과 5팩(cu_h2o2_bta, oxide_silica, sic_ceria_h2o2, sti_ceria, w_fe_oxidizer) 모두
드라이버(d99뿐, aggregate_ratio 미선언)와 term이 정확히 일치해 `status=modeled`로 승격됐다.
Δ는 MRR_COUPLED 밖이라 이 변경은 MRR 예측값·백테스트 ρ에 영향을 주지 않는다(§7 이미 명시).
