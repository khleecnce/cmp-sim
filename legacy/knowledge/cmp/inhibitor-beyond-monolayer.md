<!-- V2-SECTION: R2-slurry | 근거: inhibitor, adsorption, multilayer, BET, dG_ads, isotherm | 정본: ARCHITECTURE-V2.md §3 -->
# 억제제 — 단분자층 포화 이후에도 억제가 세지는 이유(다층 흡착·응축)와 분자명 없이 흡착상수를 얻는 절차

> 대상: `sim/chemistry.py::_inhibitor_term`, `knowledge/params/cu_h2o2_bta.yaml::inhibitor_dG_ads_kJ`·
> `inhibitor_strength_k`, `knowledge/params/w_fe_oxidizer.yaml::inhibitor_K_L_per_mol`.
> 선행(반드시 먼저): [[bta-inhibitor-langmuir-K-effective-cu-cmp-falsification]] (판정#17 — 평형 K를 정상상태
> θ에 대입하는 것이 반증됨. **이 노트는 그 반증의 "다른 원인 축"을 제시한다** — 그 노트는 K가 너무 크다고
> 봤고, 이 노트는 *등온식 자체가 단분자층에 갇혀 있다*고 본다. 두 진단은 배타적이지 않다, §6.)
> [[inhibitor-chelator-adsorption-isotherm-passivation]] (Langmuir↔Frumkin·ΔG=−35.4 kJ/mol의 도입 경로)
> [[cu-electrochemistry-pourbaix-bta-oxidizer-inhibitor]] (Cu(I)-BTA 중합막 2–4 분자층의 XPS·QCM 실체)
> [[w-cmp-picolinic-acid-inhibitor-langmuir-dissolution-suppression]] (W/피콜린산 Langmuir K=1108 L/mol)
> [[cu-bta-concentration-sweep-patent-examples]] (판정#26 — 산성계 BTA 농도스윕표 3회차 미확보·종결)

**결론 요약**
1. 포화 이후에도 억제가 세지는 것은 **모델 고장이 아니라 실재하는 물리**다 — 흡착이 단분자층에서
   멈출 물리적 이유가 없고, 2층 이상(다층)이 계속 쌓이며 부식저항이 **층수에 선형으로** 더해진다.
   1차 근거: Kokalj 2026a/2026b (Corros. Sci., 오픈액세스 전문 확보).
2. 맞는 등온식은 **Langmuir가 아니라 BET-n 다층 등온식**이며, 억제효율은 Kokalj의
   "저항 직렬(resistance-in-series)" 사상식으로 피복률에 연결된다(§3, 폐형식 전부 전사).
3. 이 틀의 입력은 **전부 분자명이 아닌 물성**이다: ΔG₁,ads / ΔG₂,ads / m(분자당 보호 사이트 수,
   분자 단면적에서) / q(막 치밀도 = 저항비) / n(최대 층수). 새 억제제는 이 5개만 주면 돌아간다(§4).
4. `_inhibitor_term`의 현행 Langmuir는 30→50 mM 에서 **0.139 %** 변화를 예측한다. 같은 구간에서
   BET-n 은 파라미터에 따라 **9.8 % ~ 44 %** 를 예측한다 — 실측 37 % 를 **포함하는** 대역이다(§5, verify 재현).
   ⚠ 이 37 % 의 1차 **출처 불명**이다(§5.1) — 대역이 그것을 포함한다는 사실은 계수 확정 근거가 아니다.
   결정적 조건: **응축농도 c_cond = 1/K₂ 가 30 mM과 50 mM 사이에 있을 때**만 37 %가 나온다.

---

## 1. 질문과, 이 노트가 반증하는 암묵적 가정

현행 `_inhibitor_term`:

    잔여율 = exp(−k·θ),  θ = K·C/(1+K·C),  K = exp(−ΔG_ads/RT)/55.5

ΔG_ads = −35.4 kJ/mol → K = 28,759 L/mol(§7 verify에서 재현; 팩 노트의 28,676은 c_H₂O=55.5 를
쓴 값이고 55.34 를 쓰면 28,759 — 0.3 % 차이, 아래 §7에서 둘 다 계산해 둔다).
이 K에서는 1 mM 에서 이미 θ=0.9664 고 30 mM θ=0.998842, 50 mM θ=0.999305 라
**30→50 mM 예측 변화가 0.139 %** 다. 실측은 8.27 → 5.25 (−36.5 %)다.

**암묵적 가정: "흡착은 단분자층에서 끝난다."** Kokalj 2026a 가 정면으로 부정한다(원문 그대로):

> "However, there is no fundamental physical reason why adsorption on flat surfaces should be
>  limited to a monolayer."
> — Kokalj (2026a), *Corros. Sci.* **258**, 113323, DOI: 10.1016/j.corsci.2025.113323

그리고 왜 문헌 전체가 이 가정을 못 알아챘는지까지 설명한다 — 억제효율 η는 정의상 1을 넘을 수 없어
(bounded) **다층의 신호가 η에 가려진다**. 즉 "θ ≈ η" 라는 관행적 근사가 곧 단분자층 가정이다.

---

## 2. 포화 이후에도 억제가 세지는 물리 — 후보 4개와 판정

| 후보 메커니즘 | 근거 상태 | 판정 |
|---|---|---|
| **(A) 다층 흡착(BET) + 표면 응축** | Kokalj 2026a/2026b 폐형식 + Xing et al. LB 막 실측 | **채택** — 유일하게 폐형식과 실측 앵커를 둘 다 가짐 |
| **(B) Cu(I)-BTA 중합막 성장** | Bastidas 2005, Notoya&Poling 1981(막두께 1.3–127 nm 실측) | **채택(보조)** — (A)의 Cu계 물질적 실체. 별도 항 아님 |
| (C) Frumkin 측면인력(f>0) | Bastidas 2005 (f = 1.39~2.50, BTA/Cu) | 부분 채택 — **포화 전 기울기**는 설명하나 포화 **후** 증가는 못 만듦 |
| (D) 재생속도/기계적 벗김 경쟁 | Len 2000, 판정#17 | 직교 축 — K_eff 를 낮출 뿐, 포화 후 단조증가를 만들지 못함 |

### 2.1 왜 (C) Frumkin 은 답이 아닌가 (중요)
Frumkin 은 K·C = θ/(1−θ)·exp(−2fθ) 로 **θ의 상승을 가파르게** 만들지만, θ의 상한은 여전히 1 이다.
θ가 1에 붙은 뒤에는 어떤 f 를 넣어도 더 이상 변하지 않는다. Bastidas 2005 도 직접 관측한다(원문):

> "(iii) at high BTA concentrations θ is independent of the BTA concentration."
> — Bastidas, Gómez, Cano (2005), *Rev. Metal.* **41**(2), DOI: 10.3989/revmetalm.2005.v41.i2.192

**즉 Frumkin 으로 갈아타도 30→50 mM 문제는 안 풀린다.** 단분자층 등온식인 한 전부 같은 벽에 부딪힌다
(Temkin, Hill-de Boer, Parsons, Flory-Huggins 모두 θ≤1). 층수 i 라는 **새 자유도**가 필요하다.

### 2.2 (A)의 실측 앵커 — 층수에 선형인 부식저항
Kokalj 2026b 가 인용하는 Xing et al. 의 Langmuir–Blodgett 실험: 스테아르산 단분자층을 **세어가며**
Fe 전극에 쌓았더니 분극저항이 층수에 거의 **선형**으로 증가했다. 이것이 다층이 계속 세지는 이유의
직접 실측이다. Kokalj 2026b 가 이 관측을 식으로 옮긴 것이 §3 의 R = R₀ + R₁ + (i−1)R₂ 다.

---

## 3. 채택 모델 — Kokalj 다층 억제효율(폐형식 전사)

### 3.1 저항 직렬 사상 (Kokalj 2026b Eq. 2–8)
i 개 단분자층이 덮인 표면의 부식저항:

    R = R₀ + R₁ + (i−1)·R₂ = R₀₁ + (i−1)·R₂      (i ≥ 1)          … (2)

- R₀ = 맨 표면 저항, R₁ = **첫 층(화학흡착)** 의 저항, R₂ = **이후 한 층(물리흡착)** 의 저항.
억제효율 η = 1 − R_blank/R 를 대입하면(원문 Eq. 3–5):

    η = η₁ + η₂…ᵢ,   η₂…ᵢ = (i−1)/(i + q),   **q = R₀₁/R₂ − 1**        … (5),(6)
    η₁ᵐᵃˣ = R₁/R₀₁                                                      … (8)

**q 의 물리적 의미 = 막 치밀도의 역수축.** q 가 크면 물리흡착 층 하나의 저항 R₂ 가 작다 =
같은 보호를 얻는 데 더 많은 층이 필요하다. Kokalj 2026b 가 Xing et al. 데이터에 맞춰 얻은 실측 피팅값:
**η₁ᵐᵃˣ = 0.66, q = 2.38** (원문 §2.1). q>0 이 일반적이라고 원문이 명시한다(첫 층이 더 강하므로).

### 3.2 층수 분포 = BET 등온식 (Kokalj 2026b Eq. 15–18, 22)
i 층에만 정확히 덮인 표면분율 θᵢ:

    θᵢ = w·θ₀·xⁱ,    x = c·K₂,    w = K₁/K₂                          … (15)–(17)
    θ₀(n) = 1 / [ 1 + w·x·(1−xⁿ)/(1−x) ]        (BET-n)               … (22)

- **K₁** = 맨 표면 위 흡착(첫 층) 평형상수, **K₂** = 흡착층 *위*에 얹히는 흡착(2층 이상) 평형상수.
- 둘 다 치환흡착 관례로 ΔG 에서 온다(원문 Eq. 33):

      Kᵢ = (1/c_H₂O)·exp(−ΔG°ᵢ,ads/RT),   c_H₂O = **55.34 M** (25 °C)   … (33)

### 3.3 전체 억제효율 (Kokalj 2026b Eq. 23) — 이것이 최종 구현식
    η(n) = η₁ᵐᵃˣ·(1 − θ₀(n)^(m/η₁ᵐᵃˣ)) + (1−η₁ᵐᵃˣ)·w·θ₀(n)·Σ_{i=2..n} [(i−1)/(i+q)]·xⁱ   … (23)

여기서 **m = 저피복률에서 억제제 분자 1개가 보호하는 표면 사이트 수**(원문 정의, Ref.[6]에서 옴).
달성 가능한 최대 효율은 1 미만이다(원문 Eq. 24):

    η_max(n) = η₁ᵐᵃˣ + (1−η₁ᵐᵃˣ)·(n−1)/(n+q) < 1                      … (24)

**이것이 `_inhibitor_term` 이 구조적으로 못 만들던 "하한(floor)"을 자연스럽게 준다** —
판정#17 §6 이 "Langmuir θ와 exp(−kθ) 조합은 하한이 없어 Len 2000 의 플래토를 구조적으로 못 만든다"고
기록한 바로 그 한계가, 다층 모델에서는 Eq.(24) 로 **자동으로 해결**된다. 이것은 이 노트가 판정#17 의
미해결 항목을 건드리는 유일한 지점이다.

### 3.4 응축농도 — 30→50 mM 문제의 핵심
    c_cond = 1/K₂                                                       … (26)

x = c·K₂ = 1 인 지점. 여기서 BET 피복률이 발산(무한 다층 성장 개시)한다. 원문:

> "Physically, x = 1 corresponds to condensation of the adsorbate on the surface, i.e., the onset of
>  unbounded multilayer growth within the BET adsorption model."

그리고 2026b 는 c_cond 직전에 곡선이 급격히 꺾이는 현상에 이름을 붙였다 — **super-coverage effect**:

> "This pronounced curvature just before c_cond is referred to as the super-coverage effect."

**§5 에서 보이듯, 실측 37 % 하락은 c_cond 가 30~50 mM 구간에 들어올 때만 재현된다.**

---

## 4. 분자명 없이 ΔG_ads 를 얻는 절차 (추상화 요건의 답)

이 모델의 입력은 5개뿐이고 **전부 분자명이 아니다**:

| 입력 | 물리적 의미 | 분자명 없이 얻는 경로 |
|---|---|---|
| **ΔG₁,ads** | 맨 금속 위 첫 층 흡착 자유에너지 | (a) 측정: §4.1, (b) 계산: §4.2 |
| **ΔG₂,ads** | 흡착층 *위* 흡착(물리흡착) 자유에너지 | §4.1 (c/η 플롯은 ΔG₁만 줌 — §4.3 경고) |
| **m** | 분자 1개가 보호하는 사이트 수 | **분자 단면적 / 금속 사이트 면적** (§4.4) |
| **q** | R₀₁/R₂ − 1 = 막 치밀도 | EIS 저항 피팅 (§4.1c) |
| **n** | 최대 층수 | 막두께 실측(QCM/XPS/타원계) ÷ 분자층 두께 |

### 4.1 측정 표준 절차 (분자를 몰라도 그 분자에 대해 수행 가능)
**(a) 전기화학 임피던스(EIS) — 권장 1순위.**
농도 스윕 → 각 농도에서 전하이동저항 R_ct → η = 1 − R_ct(blank)/R_ct(c) → **c/η vs c 플롯**.
y절편이 1/K₁ 에 해당(§4.3 조건부). Kokalj 2026a 가 다층에서도 이 절편이 **맨 표면 흡착(=ΔG₁)** 을
준다고 증명했다(원문):

> "the resulting value — and, consequently, the derived standard adsorption Gibbs energy —
>  corresponds to adsorption on the bare surface. This outcome can be attributed to the c → 0
>  extrapolation, where monolayer adsorption dominates."

**(b) QCM/EQCM — 질량 직접 측정.** θ 를 η 대리변수 없이 직접 얻는 유일한 경로. 다층 식별에는
이쪽이 결정적이다(Kokalj 2026b: θ vs c 플롯에서 Langmuir 는 1에서 포화, BET-n 은 계속 증가).
CMP 맥락의 선례: Cu-BTA 막 QCM 형성속도([[cu-electrochemistry-pourbaix-bta-oxidizer-inhibitor]]),
2-MBT/Cu EQCM(§표 5행).

**(c) 분극곡선(potentiodynamic).** i_corr 로 η 계산. q 는 EIS 등가회로의 R_f(막저항)/R_ct 분해에서.

**(d) 중량법(gravimetric).** Bastidas 2005 가 쓴 방법 — 장비 문턱이 가장 낮으나 시간해상도 없음.

### 4.2 분자구조에서 ΔG 를 *예측*하는 경로 (측정 없이)
Castillo-Robles et al. (2024), "Molecular modeling applied to corrosion inhibition: a critical review,"
*npj Mater. Degrad.* **8**, 72, DOI: 10.1038/s41529-024-00478-2 (오픈액세스).
이 리뷰는 CI 모델링이 반드시 고려해야 할 **6개 축(A1–A6)** 을 정의한다(원문):

> "(A1) the electronic properties of isolated inhibitors, (A2) the interaction of the inhibitor with
>  the surface, (A3) the surface model, (A4) the effect of the anodic and cathodic zones on the
>  surface, (A5) the solvent effects, and (A6) the electrodes' potential effects."

그리고 **관행적 한계를 명시적으로 경고**한다 — 대부분의 논문이 A1–A3 만 하고 A4–A6 을 빼먹으며,
A1(HOMO-LUMO, 쌍극자, 분극률, 분자부피, 고립전자쌍) 만으로는 **예측이 안 된다**:

> "However, a knowledge of these properties alone is insufficient for predicting and understanding
>  inhibition and must be combined with A2-A6."

**⚠ 이 노트의 판정: HOMO-LUMO/Fukui 같은 A1 양자화학 기술자만으로 ΔG_ads 를 팩에 넣는 것은
근거 없음(E5).** 예측 경로를 쓰려면 A2(표면과의 상호작용 = 흡착에너지 직접 DFT 계산)가 최소 요건이다.
같은 리뷰가 지목하는 작용기 원리(분자명 없는 일반 규칙)는 다음 하나뿐이다:

> "These are usually constituted by elements with lone pair electrons, such as O, N, P, or S, and/or
>  aromatic rings with delocalized π electrons, or certain functional groups such as amines (-NH2),
>  carboxylic acids (-COOH), alcohols (-OH), phenols, amino acids"

이것은 **순위 규칙(어떤 분자가 흡착할 가능성이 있나)** 이지 **정량 ΔG** 가 아니다. 그대로 쓸 것.

### 4.3 ⚠ c/η 플롯의 함정 (반드시 읽을 것)
Kokalj 2026a 의 핵심 경고: 다층 흡착이 일어나고 있어도 **c/η vs c 플롯은 거의 직선으로 보인다.**

> "in experiments — where only a limited number of data points are typically obtained — these
>  features are often not distinctive enough to allow multilayer identification."

즉 **"Langmuir 로 잘 맞았다(R²=0.99)"는 단분자층의 증거가 아니다.** 판정#17 이 다룬 팩의
ΔG=−35.4 도, [[w-cmp-picolinic-acid...]] 의 "Langmuir R²=0.994 > Freundlich 0.825" 판정도
이 함정에 해당한다 — **R² 로는 다층을 배제할 수 없다.** 다층 식별은 θ 직접측정(QCM)으로만 가능하다.
또한 다층일 때 c/η 절편에서 나온 ΔG 는 **ΔG₁ 이지 "그 억제제의 ΔG" 가 아니다** (§4.1a 인용).

### 4.4 m 을 분자 단면적에서 얻기 (분자명 없는 경로)
Bastidas 2005 가 실제로 수행한 절차 — 분자 투영면적을 계산해 배향/치환 물분자 수를 정한다.
BTA 실측값: **수직 배향 ≈ 20 Å², 수평 배향 ≈ 38 Å²** (원문). 이를 금속 표면 사이트 면적으로 나누면
m 이 된다. **이 절차는 분자명이 아니라 "분자 단면적"이라는 물성만 쓰므로 새 억제제에 그대로 적용된다.**
(⚠ 원문 스스로 경고: Frumkin 으로 물분자 1개 이상 치환이 나오는 모순은 "한 흡착 사이트가 물분자
*무리*에 점유돼 있기 때문"으로 해석된다 — m 은 정수가 아니어도 된다. Kokalj 도 m=1/3, 3 을 쓴다.)

---

## 5. 정량 검증 — BET-n 은 30→50 mM 을 만들 수 있는가

§7 verify 블록이 전부 재현한다. 요약:

| 모델 | 30→50 mM 예측 하락 | 실측 대비 |
|---|---|---|
| 현행 Langmuir (ΔG=−35.4, k=3.0) | **0.139 %** | 실측 36.5 % — **265배 부족** |
| BET-n, Kokalj 예시값(ΔG₁=−30, ΔG₂=−20, n=10, q=2, m=1, η₁ᵐᵃˣ=0.7) | **9.8 %** | 방향 맞음, 크기 부족 |
| BET-n, ΔG₂=−18 (c_cond=38.9 mM), n=10, q=2, η₁ᵐᵃˣ=0.5~0.7 | **44.3 / 44.4 %** | 실측을 **넘김** |
| BET-n, ΔG₂=−18, n=10, q=6, η₁ᵐᵃˣ=0.9 | **30.5 %** | 실측을 **밑돎** |

**구조적 결론(파라미터 피팅이 아니라 구조의 성질):**
실측 36.5 % 는 위 3·4행 사이에 있다 — 즉 **BET-n 은 실측을 괄호 안에 넣는다**. 결정적 조건은
파라미터 미세조정이 아니라 **c_cond = 1/K₂ 의 위치**다:
- ΔG₂ = −20 → c_cond = 17.4 mM → 30 mM에서 **이미 응축 지나침** → 30~50 구간이 둔감 → 9.8 %
- ΔG₂ = −18 → c_cond = 38.9 mM → **30과 50 사이** → super-coverage 구간을 통과 → 30~44 %
- ΔG₂ = −22, −16, −14 는 §7 스캔에서 30~45 % 대역을 전혀 만들지 못했다.

⚠ **이것은 "ΔG₂ = −18 kJ/mol 이다"라는 주장이 아니다.** ΔG₂ 는 미확인이다. 주장은
**"관측된 37 % 하락은 응축농도가 그 농도구간에 있다는 뜻이며, 이는 QCM으로 반증 가능한 예측"** 이다.

### 5.1 ⚠ 실측 8.27 → 5.25 의 출처 — 미확인
과제 설명이 준 이 수치쌍의 **1차 출처를 이 회차에 확인하지 못했다.** `~/fab-sim` 전체를
스캔했으나(knowledge/·sim/·tests/·data/) 30 mM/50 mM 억제제 농도와 8.27/5.25 제거율을 함께
담은 파일이 없다. 단위(nm/min? Å/min?)·억제제 종류·계(pH·산화제)·측정법도 미상이다.
**따라서 §5 표의 "실측 36.5 %"는 이 노트가 검증한 값이 아니라 과제가 제시한 값을 그대로 옮긴 것이다 — 출처 불명·미검증.**
EVIDENCE-RULES 기준 **E5(출처 미확인)** 로 표기한다. 계수 확정에 쓰기 전에 출처를 먼저 확보할 것.

### 5.2 팩 안에 이미 있는 농도스윕 실측표 (검증용, 출처 확인됨)

**[A] Len, McNeill, Gamble (2000)** — BTA/Cu, 알칼리 NH₄OH+알루미나계.
DOI: 10.1557/proc-613-e7.4.1. (전문 `papers/kim-mrs613-bta-nh4oh-cu-cmp.pdf`, 판정#17에서 확보)

| BTA (wt%) | BTA (mM) | Cu 제거율 (nm/min) |
|---|---|---|
| 0 | 0 | 400 |
| 0.1 | 8.395 | 65 |
| 0.25 | 20.987 | 42 |
| 0.5 | 41.974 | ~42 ("little effect") |
| 0.75 | 62.962 | ~42 ("little effect") |

**[B] Lee & Seo (2022)** — 피콜린산/W, H₂O₂ 4 wt%, 콜로이달 실리카.
DOI: 10.3390/app12031227 (CC-BY).

| 피콜린산 (wt%) | 정지식각 (Å/min) | CMP 제거율 (Å/min) |
|---|---|---|
| 0 | 90 | 120 |
| 1.5 | 11 | 85 |
| 5.0 | ~11 (포화) | ~85 (포화) |

**⚠ 문헌이 갈라지는 지점 — 평균내지 말 것.**
[A]·[B] 는 고농도에서 **플래토(더 안 세짐)** 를 보이는데, 과제가 제시한 8.27→5.25 는
고농도에서 **계속 세짐**을 보인다. 이 둘은 같은 계가 아니다:
- [A]·[B] 가 플래토인 조건: **CMP 중(기계적 벗김 있음)**. [A] 원문이 직접 귀속한다 — 제거가
  거의 전적으로 기계적이 됨 = 기계적 하한. Kokalj Eq.(24) 의 η_max<1 과 같은 구조다.
- 계속 세지려면: **응축농도가 그 구간 안**(§5) 이거나, 기계적 하한 아래로 아직 안 내려간 경우.
즉 갈림의 축은 "억제제 종류"가 아니라 **(i) c_cond 의 위치와 (ii) 기계적 하한까지의 여유** 다.

---

## 6. 판정#17 과의 관계 — 두 진단은 배타적이지 않다

| | 판정#17 (K_eff) | 이 노트 (다층) |
|---|---|---|
| 진단 | K 가 너무 크다 (평형값을 정상상태에 오용) | 등온식이 단분자층에 갇혀 있다 |
| 처방 | K_eff = K_eq/(1+k_abrade/k_desorb) ≈ 183~250 L/mol | BET-n + Kokalj η 사상 |
| 못 푸는 것 | 플래토(하한)를 구조적으로 못 만듦 (원문 §6 자인) | 기계적 벗김을 표현 안 함 |
| 푸는 것 | 기계적 벗김을 명시 | 포화 후 단조증가 + 하한 Eq.(24) |

**두 축은 직교한다.** 다층 모델을 쓰면서도 K₁·K₂ 를 평형값이 아닌 정상상태 유효값으로 둘 수 있다.
판정#17 을 번복하지 않는다 — 그 노트가 "Langmuir θ와 exp(−kθ) 의 조합 자체가 하한을 못 만든다"고
남긴 **미해결 한계**에 대해, 이 노트가 §3.3 Eq.(24) 라는 구조적 해답을 제시할 뿐이다.

## 6.1 ⚠ 구현 전 반드시 알아야 할 제약
1. **자유 파라미터가 1개(K) → 5개(ΔG₁,ΔG₂,m,q,n)로 늘어난다.** 판정#26 이 이미 종결한 사실 —
   산성계 BTA 농도스윕표가 없다 — 때문에 **cu_h2o2_bta 팩에서 이 5개를 동시 식별하는 것은 불가능하다.**
   구현하더라도 대부분 unverified 로 남는다. 이 노트는 그 갭을 해소하지 않는다.
2. Kokalj 모델은 **부식(정지식각) 억제효율**의 모델이지 **CMP 제거율**의 모델이 아니다.
   [B] 가 실측으로 보인 비대칭(정지식각 8.2배 억제 vs 제거율 1.41배 억제)이 그대로 남는다 —
   η 를 제거율 감소로 옮기는 사상은 이 노트 범위 밖이며 **추가 가정 없이는 정당화되지 않는다.**
3. q=0 특수해(Kokalj 2026a)는 폐형식이 있다(Eq. 30–32). q>0 는 유한합(BET-n)으로만 계산된다.

---

## 7. 재현 검증

```python verify
import math

R = 8.314462618; T = 298.15
C_H2O_KOKALJ = 55.34   # Kokalj 2026b Eq.(33), 25 degC
C_H2O_PACK   = 55.5    # 팩/판정#17 이 쓴 값

def K_from_dG(dG_kJ, cH2O=C_H2O_KOKALJ):
    return math.exp(-dG_kJ * 1000.0 / (R * T)) / cH2O

# --- (1) 현행 팩 Langmuir 재현: 30->50 mM 이 사실상 무변화임을 확인
K_pack = K_from_dG(-35.4, C_H2O_PACK)
assert abs(K_pack - 28676) < 60, K_pack          # 판정#17 의 28,676 재현
K_l = K_from_dG(-35.4)                            # c_H2O=55.34 판
assert abs(K_l - 28759) < 60, K_l
th = lambda c, K: K*c/(1+K*c)
assert abs(th(1e-3, K_l) - 0.966397) < 1e-5
ratio_langmuir = math.exp(-3.0*(th(50e-3,K_l) - th(30e-3,K_l)))
assert abs(ratio_langmuir - 0.998613) < 1e-5, ratio_langmuir
drop_langmuir = 100*(1-ratio_langmuir)
assert drop_langmuir < 0.2, drop_langmuir         # 0.139 % — 사실상 구분 불가
print(f"현행 Langmuir 30->50mM 하락 = {drop_langmuir:.3f} %")

# --- (2) Kokalj 2026b BET-n 다층 모델 (Eq. 15,17,22,23)
def bet_n(c, dG1, dG2, n):
    K1, K2 = K_from_dG(dG1), K_from_dG(dG2)
    x = c*K2; w = K1/K2
    if abs(x-1.0) < 1e-12: x = 1.0 - 1e-12
    theta0 = 1.0/(1.0 + w*x*(1.0-x**n)/(1.0-x))          # Eq.(22)
    theta_i = [w*theta0*x**i for i in range(1, n+1)]      # Eq.(15)
    return theta0, theta_i

def eta_multilayer(c, dG1, dG2, n, q, m, e1max):          # Eq.(23)
    theta0, theta_i = bet_n(c, dG1, dG2, n)
    e1 = e1max*(1.0 - theta0**(m/e1max))
    e2 = sum((1.0-e1max)*(i-1)/(i+q)*theta_i[i-1] for i in range(2, n+1))
    return e1 + e2

# Eq.(24): 최대 효율이 1 미만 -> 판정#17 이 못 만들던 '하한'이 구조적으로 나온다
def eta_max(n, q, e1max): return e1max + (1-e1max)*(n-1)/(n+q)
assert eta_max(10, 2.0, 0.7) < 1.0
assert abs(eta_max(10, 2.0, 0.7) - (0.7 + 0.3*9/12)) < 1e-12
print(f"Eq.(24) 최대효율(n=10,q=2,e1max=0.7) = {eta_max(10,2.0,0.7):.4f} < 1  (하한 존재)")

# Eq.(26): 응축농도
c_cond = lambda dG2: 1.0/K_from_dG(dG2)
assert abs(c_cond(-20.0)*1000 - 17.35) < 0.05
assert abs(c_cond(-18.0)*1000 - 38.94) < 0.10
print(f"c_cond(dG2=-20) = {c_cond(-20.0)*1000:.2f} mM ; c_cond(-18) = {c_cond(-18.0)*1000:.2f} mM")

# --- (3) Kokalj 예시 파라미터: 방향은 맞으나 크기 부족
e30 = eta_multilayer(30e-3, -30, -20, 10, 2.0, 1.0, 0.7)
e50 = eta_multilayer(50e-3, -30, -20, 10, 2.0, 1.0, 0.7)
drop_kokalj = 100*(1-(1-e50)/(1-e30))
assert 9.0 < drop_kokalj < 11.0, drop_kokalj
assert drop_kokalj > 60*drop_langmuir      # Langmuir 보다 최소 60배 민감
print(f"BET-n (Kokalj 예시값) 30->50mM 하락 = {drop_kokalj:.1f} %  (Langmuir의 {drop_kokalj/drop_langmuir:.0f}배)")

# --- (4) 핵심 주장: c_cond 가 30~50 mM 안에 들어와야 ~37 % 가 나온다
hits = []
for dG2 in (-14, -16, -18, -20, -22):
    for n in (10, 40, 100):
        for q in (0, 2, 6):
            for e1max in (0.5, 0.7, 0.9):
                a = eta_multilayer(30e-3, -30, dG2, n, q, 1.0, e1max)
                b = eta_multilayer(50e-3, -30, dG2, n, q, 1.0, e1max)
                d = 100*(1-(1-b)/(1-a))
                if 30.0 < d < 45.0:
                    hits.append((dG2, n, q, e1max, d))
assert len(hits) > 0, "30~45% 대역을 만드는 파라미터가 없다"
# 30~45 % 를 만든 모든 조합의 dG2 가 -18 하나로 수렴 -> c_cond 가 30~50 mM 사이
assert set(h[0] for h in hits) == {-18}, sorted(set(h[0] for h in hits))
assert 30e-3 < c_cond(-18.0) < 50e-3       # 응축이 관측구간 '안'에 있다
print(f"30~45% 를 만드는 조합 {len(hits)}개, 전부 dG2=-18 (c_cond={c_cond(-18.0)*1000:.1f} mM, 30~50mM 구간 내부)")
for h in hits: print(f"   dG2={h[0]} n={h[1]} q={h[2]} e1max={h[3]} -> {h[4]:.1f} %")

# --- (5) 반례 확인: 단분자층 등온식은 어떤 f 로도 포화 후 증가를 못 만든다 (Frumkin)
def theta_frumkin(c, K, f, lo=1e-12, hi=1-1e-12):
    for _ in range(200):                     # 이분법: K*c = th/(1-th)*exp(-2 f th)
        mid = 0.5*(lo+hi)
        if mid/(1-mid)*math.exp(-2*f*mid) < K*c: lo = mid
        else: hi = mid
    return 0.5*(lo+hi)
for f in (0.0, 1.39, 2.50):                  # Bastidas 2005 실측 f 범위
    t30, t50 = theta_frumkin(30e-3, K_l, f), theta_frumkin(50e-3, K_l, f)
    assert t50 - t30 < 0.01, (f, t50-t30)    # 포화 후 변화량이 1 % 미만
print("Frumkin(f=0/1.39/2.50): 30->50mM theta 변화 모두 <1 % — 측면인력으로는 안 풀린다")
print("PASS: Langmuir 무감각 재현, BET-n 폐형식 재현, Eq.(24) 하한 존재, c_cond 위치가 결정적임을 확인")
```

---

## 8. 1차 출처

- **[K1] Kokalj, A. (2026a).** "Estimating standard adsorption Gibbs energy from corrosion inhibition
  efficiencies: A case of multilayer adsorption." *Corrosion Science* **258**, 113323.
  DOI: **10.1016/j.corsci.2025.113323**. 오픈액세스 전문 확보: `papers/kokalj2026-multilayer-dGads.pdf`
  (DiRROS id=35366, 13쪽). BET 다층 + η 사상, q=0 특수해 폐형식.
- **[K2] Kokalj, A. (2026b).** "A generalized model of corrosion inhibition efficiency for multilayer
  adsorption." *Corrosion Science* **261**, 113626. DOI: **10.1016/j.corsci.2026.113626**.
  오픈액세스 전문 확보: `papers/kokalj2026-generalized-multilayer.pdf` (DiRROS id=38936, 9쪽).
  **§3 의 Eq.(2)–(33) 은 전부 이 PDF 원문에서 직접 전사**했다. q 일반화, super-coverage effect.
- **[K3] Kokalj, A. (2023).** "On the estimation of standard adsorption free energy from corrosion
  inhibition efficiencies." *Corros. Sci.* **217**, 111139. DOI: 10.1016/j.corsci.2023.111139.
  ([K1][K2] 의 단층 η₁ 모델 = Eq.(35) 의 출처. **본문 미독 — 서지 앵커로만 사용**.)
- **[K4] Kokalj, A. (2023).** "On the use of the Langmuir and other adsorption isotherms in corrosion
  inhibition." *Corros. Sci.* **217**, 111112. DOI: 10.1016/j.corsci.2023.111112. (**미독**)
- **[W] Walczak, M.S., Morales-Gil, P., Lindsay, R. (2019).** "Determining Gibbs energies of adsorption
  from corrosion inhibition efficiencies: Is it a reliable approach?" *Corros. Sci.* **155**, 182–185.
  DOI: 10.1016/j.corsci.2019.04.040. (θ≈η 근사를 처음 반증한 논문. **미독 — [K1][K3] 경유 인용**.)
- **[B] Bastidas, D.M., Gómez, R.R., Cano, E. (2005).** "The isotherm slope. A criterion for studying the
  adsorption mechanism of benzotriazole on copper in sulphuric acid." *Rev. Metal.* **41**(2).
  DOI: **10.3989/revmetalm.2005.v41.i2.192**. 오픈액세스(DIGITAL.CSIC hdl:10261/21192).
  Frumkin 최적합, f·ΔG 표, 분자 투영면적 20/38 Å².
- **[C] Castillo-Robles, J.M., de Freitas Martins, E., Ordejón, P., Cole, I. (2024).**
  "Molecular modeling applied to corrosion inhibition: a critical review." *npj Mater. Degrad.* **8**, 72.
  DOI: **10.1038/s41529-024-00478-2** (오픈액세스). A1–A6 축, A1-만-쓰기 경고.
- **[K] Kim, Y.-S., Kim, J.-G. (2016).** "Electrochemical and Quantum Chemical Studies of 1,2,3-Benzotriazole
  as Inhibitor for Copper and Steel in Simulated Tap Water." *Mater. Trans.*
  DOI: **10.2320/matertrans.m2016310**.
- **[Kh] Khadom, A.A., Yaro, A.S., Kadhum, A.A.H. (2010).** "Adsorption mechanism of benzotriazole for
  corrosion inhibition of copper-nickel alloy in hydrochloric acid." *J. Chil. Chem. Soc.* **55**(1).
  DOI: **10.4067/s0717-97072010000100035** (오픈액세스).
- **[L] Len, V.S.C., McNeill, D.W., Gamble, H.S. (2000).** *MRS Proc.* **613**, E7.4.1.
  DOI: **10.1557/proc-613-e7.4.1**. (판정#17에서 확보, §5.2 [A])
- **[S] Lee, K., Seo, J. (2022).** *Applied Sciences* **12**(3), 1227. DOI: **10.3390/app12031227** (CC-BY).
  (§5.2 [B])
- **[M] "Direct measurement of the adsorption kinetics of 2-mercaptobenzothiazole on a microcrystalline
  copper surface."** *Revista de Metalurgia*.
  URL: https://revistademetalurgia.revistas.csic.es/index.php/revistademetalurgia/article/view/1377
  ⚠ **DOI 미확인** — 이 회차에 DOI를 확정하지 못했다. 값 인용 시 이 한계를 함께 적을 것.
- **[X] Xing et al.** — LB 막 층수-분극저항 선형성. **[K2] Ref.[3] 경유 2차 인용, 원문 미확보.**
  §2.2 의 실측 앵커가 2차 인용이라는 점은 이 노트의 약한 고리다(E3).

### 8.1 서로 다른 억제제의 ΔG_ads / K 실측치 (요구사항 3)

| # | 억제제 | 기질 / 계 | 측정법 | 등온식 | K | ΔG_ads (kJ/mol) | 출처 |
|---|---|---|---|---|---|---|---|
| 1 | BTA | Cu / 모사 수돗물 | 전기화학(분극·EIS)+양자화학 | Langmuir | 3294.9 L/mol | **−30.02** | [K] 10.2320/matertrans.m2016310 |
| 2 | BTA | **Fe(steel)** / 모사 수돗물 | 동일 (#1과 **같은 논문·같은 방법**) | Langmuir | 123.62 L/mol | **−21.89** | [K] 동일 |
| 3 | BTA | Cu-Ni 합금 / 5 % HCl, 35 °C | 중량법 | Langmuir | 5.586 L/g | **−22.093** | [Kh] 10.4067/s0717-97072010000100035 |
| 3b | BTA | 동일, 45 / 55 °C | 동일 | Langmuir | 4.762 / 4.762 L/g | **−22.389 / −23.093** | [Kh] 동일 |
| 3c | BTA | 동일, 35→55 °C | 동일 | **Freundlich** | 0.883→0.879 L/g | **−17.37 → −18.485** | [Kh] 동일 |
| 3d | BTA | 동일, 35→55 °C | 동일 | 속도론-열역학 | 3.67→8.803 L/g | **−21.018 → −24.768** | [Kh] 동일 |
| 4 | BTA | Cu / 0.001–0.01 M H₂SO₄, 298–328 K | 중량법 | **Frumkin** (f=1.39–2.50) | k=431–1361 | **−27.2 ~ −30.0** | [B] 10.3989/revmetalm.2005.v41.i2.192 |
| 5 | **2-MBT** | Cu / 물 | **EQCM** | Langmuir (R²=0.91–0.98) | 미보고 | **−5.59** | [M] ⚠DOI 미확인 |
| 6 | **피콜린산** | **W** 산화물 / H₂O₂ 4 wt% | CMP 정지식각 | Langmuir (R²=0.994) | b=0.009 L/mg → **1108 L/mol** | ΔG 미보고 | [S] 10.3390/app12031227 |
| 7 | **6-TTA** | Cu | **SERS** | Langmuir | **BTA의 약 3배** | BTA보다 **610 cal/mol(=2.55 kJ/mol) 더 음(陰)** | Chem. Phys. Lett. **287**(3–4) 449–454 (1998) ⚠DOI 미확인 |
| 8 | (팩 현행값) | Cu / H₂O₂+BTA | — | Langmuir | 28,676 L/mol | **−35.4** | 폐형식 없음 — **unverified** |

**⚠ 문헌이 갈라지는 지점 — 평균내지 마라. 갈림의 축은 3개다:**
1. **기질**: 같은 BTA·같은 논문·같은 방법인데 Cu −30.02 vs Fe −21.89 (#1 vs #2, 차 8.1 kJ/mol).
   → **ΔG_ads 는 "억제제의 성질"이 아니라 "억제제×기질 쌍의 성질"이다.** 팩에 억제제 이름만으로
   ΔG 를 넣는 구조 자체가 틀렸다.
2. **적용한 등온식**: 같은 원자료(#3/3c/3d)에서 Langmuir −22.09 / Freundlich −17.37 / 속도론 −21.02.
   **최대 4.7 kJ/mol 차이가 "어떤 등온식을 골랐나"만으로 생긴다.** K(=exp) 로는 6배 차이다.
3. **측정법**: 2-MBT EQCM −5.59 (#5, 물리흡착 영역) vs BTA류 −22~−30 (화학흡착 경계).
   EQCM 은 θ 를 직접 재고 나머지는 η 를 θ 대리로 쓴다 — §4.3 함정에 해당하는 계통차다.

**팩 현행값 −35.4 (#8)는 위 실측 어느 것보다도 강하다** — 확인된 BTA 실측 대역은 −22 ~ −30 이며,
−35.4 는 그 바깥이다. 판정#17 이 이 값을 unverified 로 둔 것과 정합적이며, 이 노트는 그 값의
**절대값에 문헌적 근거가 없음**을 추가로 확인한다(대체값을 제시하지는 않는다 — §6.1 제약 1).

### 8.2 이 노트가 확인하지 못한 것 (미확인 목록)
- 과제가 제시한 **8.27 → 5.25 (30→50 mM)의 1차 출처**. 억제제 종류·단위·계 전부 미상(§5.1).
- **ΔG₂,ads(2층 이상 흡착)의 실측치** — 어떤 억제제에 대해서도 한 건도 확보하지 못했다.
  §5 의 ΔG₂=−18 은 "실측을 재현하려면 여기 있어야 한다"는 **역산 요구조건**이지 측정값이 아니다.
- **q, n, m 의 CMP계 실측치.** q=2.38·η₁ᵐᵃˣ=0.66 은 [K2]가 **Fe/스테아르산 LB막**에서 얻은 값이며
  Cu/BTA·W/피콜린산에 이식할 근거가 없다.
- [X] Xing et al. 원문, [K3][K4][W] 본문.
