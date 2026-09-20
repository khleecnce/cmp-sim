<!-- V2-SECTION: R2-slurry | 근거: chemistry, inhibitor, chelate, BTA, 흡착, 안정도상수 | 정본: ARCHITECTURE-V2.md §3 -->
# 억제제(BTA·TAZ) 흡착·패시베이션 vs 킬레이트(글리신·시트르산) 착화 — 등온식·피복률·안정도상수로 본 "보호 대 용해"의 정량 (slurry-chemistry Lv1-2)

> 에이전트: slurry-chemistry Lv1-2 | 작성일: 2026-09-10
> 선행(반드시 먼저): [[oxidizer-redox-potential-decomposition-metal-suitability]] (산화제가 만드는 "무른 막"의 열역학),
> [[cu-electrochemistry-pourbaix-bta-oxidizer-inhibitor]] (Cu-BTA 막의 XPS·QCM 실체·전위-pH 안정영역 — 그 노트는 막의 **조성·두께·형성속도**를
> 정량했다. 이 노트는 그 앞단·옆단인 **흡착 등온식/피복률 θ**와 **킬레이트 안정도상수 log K**를 채워 중복 없이 쌓는다).
> [[slurry-components-overview]] (BTA Langmuir K≈2.9e4·ΔG≈−35.4 kJ/mol을 이 노트가 Frumkin으로 확장·정직화)
> [[surface-chemistry-cu-w-pourbaix-passivation]] [[cu-cmp-three-step-process-slurry-requirements]] [[preston-luo-dornfeld-mrr]]
> [[low-level-metal-cobalt-ruthenium-cross-contamination]] [[ceria-slurry-ce-redox-selectivity]]
>
> **스코프**: (1) 억제제 흡착의 등온식(Langmuir vs Frumkin)·표면 피복률 θ·흡착자유에너지 ΔG_ads, (2) BTA vs 톨릴트리아졸(TTA/TAZ)의
> 흡착 차이, (3) 킬레이트제(글리신·시트르산)의 금속-리간드 안정도상수 log K와 산해리 pKa, (4) 이 두 힘("보호=억제제 흡착"과
> "용해=킬레이트 착화")이 어떻게 CMP의 정적식각·MRR·평탄화를 정량적으로 가르는가. 막의 조성·두께(Cu(I)-BTA 2–4층)는 선행 노트에 있어
> 재기술하지 않고 **흡착 정량**만 다룬다.

## 1. 1차·핵심 출처 (실존 확인)

- **MINTEQ v4 열역학 데이터베이스** — `papers/phreeqc-minteq.v4.dat` (USGS PHREEQC 배포판 `minteq.v4.dat`, `$Id: 11091 2016-04-21$`).
  이 노트의 **모든 금속-리간드 안정도상수(log K)와 산해리상수는 이 파일에서 직접 판독**했다(줄번호 명시). 원 출처는 MINTEQA2/NIST
  임계안정도상수 컴필레이션(Martell & Smith 계열)이며, 값은 **I=0, 25 °C** 기준(무한희석 외삽)이다 → 실 슬러리 이온강도에서는 조건상수로
  보정 필요(§7 한계).
- **Popuri, Sagi, Alety, Peethala, Amanapu, Patlolla, Babu (2017)**, "Citric Acid as a Complexing Agent in Chemical Mechanical Polishing
  Slurries for Cobalt Films," *ECS J. Solid State Sci. Technol.* 6(9) P594–P602, DOI: https://doi.org/10.1149/2.0111709jss (CC-BY, 전문 확보
  `papers/popuri2017-jsst-co-citric-acid-cmp.pdf`). 시트르산 pKa(3.2/4.9/6.4)·가용성 금속-시트르산 착물의 CMP MRR 상승 역할의 1차 출처.
- **Aksu & Doyle (2001)**, "Electrochemistry of Copper in Aqueous Glycine Solutions," *J. Electrochem. Soc.* 148(1) B51–B57,
  DOI: https://doi.org/10.1149/1.1344532 (Crossref 확인). **본문 IOP 봇차단으로 미독** — ECS 회의초록(`papers/…` 미저장, WebFetch로 판독)과
  후속 CMP 논문에서 결론만 인용: 글리신이 Cu 용해영역을 **크게 확장**, pH 4·9에서 능동 용해, pH 12에서 Cu₂O/CuO로 능동-부동태 전이.
- **Aksu & Doyle (2002)**, "The Role of Glycine in the Chemical Mechanical Planarization of Copper," *J. Electrochem. Soc.* 149(6) G352–G361,
  DOI: https://doi.org/10.1149/1.1474436 (Crossref 확인, 본문 미독 — 제목·서지만).
- **Antonijevic & Petrovic (2008)**, "Copper Corrosion Inhibitors. A Review," *Int. J. Electrochem. Sci.* 3, 1–28 (오픈액세스, 전문 확보
  `papers/antonijevic2008-ijes-copper-corrosion-inhibitors-review.pdf`, 28쪽). BTA·톨릴트리아졸(TTA)의 흡착 등온식(Langmuir/Frumkin) 귀속과
  Cu(I)BTA 중합막, TTA가 BTA보다 억제효율이 높은 이유(소수성 메틸기)의 리뷰(2차 인용 집합체).
- **Lewis (1981)**, "Adsorption isotherm for the copper–benzotriazole system" — 관련 계열로 BTA-Cu 흡착이 **Frumkin** 등온식에 맞는다는
  고전 보고. (같은 주제의 검증가능 DOI: "A Study on the Adsorption of Benzotriazole on Copper … Inflection Point of the Isotherm,"
  DOI: https://doi.org/10.1023/b:adso.0000046358.35572.4c — Crossref 확인, 본문 미독. Frumkin 귀속의 서지 앵커로만 사용.)
- **선행 노트에서 상속(재기술 안 함)**: Cu(I)-BTA 중합막 XPS/QCM 실체·2–4 분자층·형성속도·Tromans 1998 Cu-BTA E-pH는
  [[cu-electrochemistry-pourbaix-bta-oxidizer-inhibitor]] §4에 있음.

## 2. 두 개의 상반된 화학 — 억제제는 "덮고", 킬레이트는 "녹인다"

CMP 슬러리의 화학 자유도는 [[slurry-components-overview]]가 정성적으로 나눴다. 이 노트는 그 중 정반대 방향으로 작동하는 두 첨가제를
**같은 언어(표면 피복 vs 용액상 착화)**로 정량 비교한다.

| | 억제제 (BTA, TTA/TAZ) | 킬레이트제 (글리신, 시트르산) |
|---|---|---|
| 작용 장소 | **금속/산화물 표면** (흡착) | **용액상** (금속이온과 착물) |
| 정량 척도 | 피복률 θ, 흡착상수 K_ads, ΔG_ads | 안정도상수 log K(ML), log β₂ |
| CMP 효과 | 정적식각↓·dishing↓ (**보호**) | 용해율↑·MRR↑·재석출↓ (**용해**) |
| 방향 | Cu²⁺/Cu 경계 위에 막을 얹어 부동태 | Cu²⁺를 착물로 빼내 Pourbaix 용해영역 확장 |
| 근거 | §3–4, 선행 노트 §4 | §5–6, Aksu&Doyle 2001 |

핵심 통찰: **둘 다 "구동력"이 아니라 "게이트"다.** 산화제(선행 [[oxidizer-redox-potential-decomposition-metal-suitability]])가 열역학적
구동력을, 억제제·킬레이트는 그 구동력이 실제 표면에서 얼마나 발현될지를 여닫는다. 이 게이트 비율이 [[preston-luo-dornfeld-mrr]] $K_p$의
화학 성분이고 [[pattern-dependent-dishing-erosion]]의 dishing 선택성을 정한다.

## 3. 억제제 흡착 등온식 — Langmuir에서 Frumkin으로

### 3.1 Langmuir (선행 overview의 출발점)
[[slurry-components-overview]] §7은 BTA를 **Langmuir 등온식**으로 다뤘다:
$$\theta=\frac{K_{ads}\,C}{1+K_{ads}\,C},\qquad \Delta G^\circ_{ads}=-RT\ln(55.5\,K_{ads})$$
55.5는 물의 몰농도(mol/L)로, 흡착상수를 몰분율 기준으로 환산하는 관례 인자다. ΔG°_ads ≈ −35.4 kJ/mol(overview, **2차 인용·절대값 미검증**)을
넣으면 K_ads ≈ 2.87×10⁴ L/mol → **반포화 농도 C½ = 1/K ≈ 35 µM**, 1 mM BTA에서 θ = 0.966. 즉 **수십 µM~mM의 낮은 BTA로 표면이 거의
포화**된다(§7 verify로 재현). ΔG의 크기(−35 kJ/mol)는 물리흡착(−20)과 화학흡착(−40 kJ/mol)의 경계에 있어, BTA의 첫 층이 Cu(I)과
**화학결합**(선행 노트 XPS: Cu(I)-BTA)임과 정합적이다.

### 3.2 Langmuir의 한계와 Frumkin 확장
Langmuir는 (i) 흡착점이 모두 동등, (ii) 흡착분자 간 **측면 상호작용 없음**을 가정한다. 그러나 BTA는 흡착 후 이웃 분자와
Cu(I)-BTA **중합 사슬**([Cu(I)BTA]ₙ, 선행 노트 §4.2)을 이루므로 측면 상호작용이 명백히 존재한다. 그래서 실험적으로 BTA-Cu 흡착은
**Frumkin 등온식**이 더 잘 맞는다고 보고된다(Antonijevic&Petrovic 2008 리뷰; Lewis 1981; 상기 inflection-point DOI):
$$K_{ads}\,C=\frac{\theta}{1-\theta}\exp(-2f\theta)$$
여기서 **f는 상호작용 파라미터**: f>0이면 인력(협동적, 이미 흡착된 분자가 이웃 흡착을 도움), f<0이면 반발. BTA의 중합 사슬 형성은
**f>0(협동적 흡착)** 에 해당한다. 결과(§7 verify): f>0이면 등온식이 **더 가파르게** 상승 — θ를 0.4→0.6으로 올리는 데 필요한 농도 변화가
Langmuir의 2.25배에서 f=1.5일 때 1.24배로 좁아진다. 이 **협동적·급격한 포화**가 선행 노트 QCM에서 BTA 투입 즉시(수 초) 막이 완성되고
용해가 정지한 현상의 등온식 언어다. (f의 절대값은 계·전위·이온강도 의존이라 **여기 f=1.5는 협동성 시연용 예시값·미검증**, 방향(f>0)만 근거.)

### 3.3 TTA/TAZ — 트리아졸 억제제 계열
톨릴트리아졸(**TTA**, 메틸-BTA)과 1,2,4-트리아졸 유도체(**TAZ** 계열)는 BTA와 같은 트리아졸 고리로 Cu(I)에 배위한다. 리뷰(Antonijevic&Petrovic
2008)의 정성 결론: **TTA가 BTA보다 억제효율이 높다** — 비극성 메틸기가 막의 **소수성**을 높여 물·이온의 침투를 막기 때문(5-alkyl-BTA
계열에서 C6까지 효율↑, C6-BTAH 최적, C12는 저용해도로 효과 소멸). 흡착 귀속은 분자에 따라 갈려, 리뷰는 어떤 트리아졸은 **화학흡착
(Langmuir)**, 어떤 것(예: DTUr)은 **Frumkin**으로 맞는다고 정리한다. 즉 "트리아졸=BTA와 동일"이 아니라 **치환기(메틸·알킬)가 소수성과
흡착등온식을 바꾼다**는 것이 이 계열의 핵심. (정량 ΔG·f 표는 리뷰가 원논문별로 흩어 인용 — 이 노트는 순위·방향만 채택, 절대값은 확인 못 함.)

## 4. Cu-BTA 막의 열역학적 위치 (선행 노트로 위임)
Cu(I)-BTA 막의 **조성**(XPS: C/N≈2.8, Cu(I) 우세)·**두께**(QCM: 0.12 µg/cm² = 2–4 분자층)·**형성속도**(즉시)·**전위-pH 안정영역**
(pH 2.7–9.8, Tromans 1998 기반)은 모두 [[cu-electrochemistry-pourbaix-bta-oxidizer-inhibitor]] §4에서 정량했다. 이 노트의 §3 등온식은
그 막이 "농도에 따라 얼마나 빨리·급격히 덮이는가"의 앞단이다: **θ→1(§3) → 부동태막 형성(선행 §4) → 정적식각 <0.8 Å/min(선행 §4.3)**.

## 5. 킬레이트 안정도상수 — 글리신·시트르산이 Cu를 "빼내는" 힘

### 5.1 산해리상수(pKa) — 리간드가 언제 배위형이 되는가
MINTEQ v4 DB에서 직접 판독(누적 양성자화 상수 → 단계별 pKa 환산, §7 verify):

| 리간드 | 반응(누적) | log β (MINTEQ 줄) | 단계별 pKa |
|---|---|---|---|
| **시트르산** (Cit³⁻) | H⁺+Cit³⁻=HCit²⁻ | 6.396 (L6401) | pKa₃ = 6.40 |
| | 2H⁺+Cit³⁻=H₂Cit⁻ | 11.157 (L6409) | pKa₂ = 4.76 |
| | 3H⁺+Cit³⁻=H₃Cit | 14.285 (L6417) | pKa₁ = 3.13 |
| **글리신** (Gly⁻) | H⁺+Gly⁻=HGly | 9.778 (L9337) | pKa(−NH₃⁺) = 9.78 |
| | 2H⁺+Gly⁻=H₂Gly⁺ | 12.128 (L9345) | pKa(−COOH) = 2.35 |

MINTEQ로 환산한 시트르산 pKa(3.13/4.76/6.40)는 popuri2017이 CMP 문맥에서 쓴 **3.2/4.9/6.4와 독립 교차검증 일치**(§7 verify 1) —
두 출처가 수렴하므로 우연 아님. 함의: 시트르산은 pH 3~6에서 부분탈양성자종(H₂Cit⁻·HCit²⁻)이 우세해 이 pH대에서 금속 결합이 활발하고,
글리신은 카복실이 pH>2.4에서, 아미노가 pH<9.8에서 각각 형태를 바꿔 **중성 pH에서 양쪽성이온(zwitterion)**이 지배적 → 완전 배위형(Gly⁻)은
극소수(§5.3).

### 5.2 금속-리간드 안정도상수 (MINTEQ v4, I=0, 25 °C)

| 착물 | 반응 | log K / log β | MINTEQ 줄 |
|---|---|---|---|
| Cu-글리시네이트 1:1 | Cu²⁺+Gly⁻=Cu(Gly)⁺ | **log K₁ = 8.57** | L9449 |
| Cu-글리시네이트 1:2 | Cu²⁺+2Gly⁻=Cu(Gly)₂ | **log β₂ = 15.7** (→ log K₂ = 7.13) | L9457 |
| Cu-시트레이트 1:1 | Cu²⁺+Cit³⁻=Cu(Cit)⁻ | **log K = 7.57** | L6545 |
| Cu-시트레이트 1:2 | Cu²⁺+2Cit³⁻=Cu(Cit)₂⁴⁻ | log β₂ = 8.9 | L6553 |
| Cu-시트레이트 (양성자화) | Cu²⁺+Cit³⁻+H⁺=CuH(Cit) | log K = 10.87 | L6561 |
| Cu-시트레이트 이량체 | 2Cu²⁺+2Cit³⁻=Cu₂(Cit)₂²⁻ | log β = 16.9 | L6577 |

**읽는 법**: 글리신은 킬레이트(N,O 두 자리) 배위로 log K₁=8.57로 매우 강하고 1:2까지 감(log β₂=15.7). K₁>K₂(8.57>7.13)는 통계·정전
효과의 정상 거동. 시트르산은 세 카복실+하이드록실로 다자리 배위하나 1:1 log K=7.57로 글리신 1:1보다 약간 약하고, 대신 **양성자화·이량체
착물이 다양**(CuHCit log K 10.87, Cu₂Cit₂ 16.9)해 pH·농도에 따라 화학종이 풍부하다 — popuri2017이 CMP에서 관찰한 [M(Cit)₂] 가용성
착물 형성과 정합(popuri는 Co 계지만 시트레이트 배위 화학은 공통).

### 5.3 조건부 안정도와 "용해영역 확장"의 정량 — Aksu&Doyle을 수치로
§5.2의 log K는 **완전 탈양성자 리간드**(Gly⁻·Cit³⁻) 기준이다. 실 pH에서 유효한 것은 **조건부 상수** K′ = K·α_L(α_L=배위형 분율).
글리신은 아미노 pKa=9.78이라 중성 pH에서 Gly⁻ 분율이 작지만, 그럼에도 β₂가 워낙 커서 용해 Cu가 폭증한다. 총 용해 Cu(II)와 유리 Cu²⁺의 비:
$$\frac{[\text{Cu}]_{tot}}{[\text{Cu}^{2+}]}=1+K_1[\text{Gly}^-]+\beta_2[\text{Gly}^-]^2$$
글리신 총 0.01 M(Aksu 조건), pH 7 → [Gly⁻]≈1.7×10⁻⁵ M인데도 이 비가 **≈1.4×10⁶배**(§7 verify 2). 이것이 Aksu&Doyle 2001이
"글리신이 Cu 용해영역을 크게 확장한다"고 한 것의 **정량적 의미**: 킬레이트가 Cu²⁺를 용액으로 빨아내 Pourbaix 상 도표에서 부동태(산화물)
영역을 침식하고 용해영역을 넓힌다. 산화제(막 형성)와 정반대 힘이며, 억제제(BTA, 표면 보호)와도 정반대다.

## 6. 세 힘의 삼각관계가 MRR·평탄화를 정한다
[[slurry-components-overview]] §5의 "삼각관계"를 안정도상수·피복률로 정량화하면:

1. **산화제**: Cu⁰→Cu²⁺/산화막 (구동력, 선행 oxidizer 노트). 없으면 화학제거 0.
2. **킬레이트(글리신·시트르산)**: 산화막·Cu²⁺를 용액으로 착화(§5, log K 7~16) → 용해율↑, [[slurry-components-overview]] §3의 산화제-MRR
   **정점을 고농도로 이동**시키고, 재석출·오염을 막는다([[low-level-metal-cobalt-ruthenium-cross-contamination]]와 연결: Co/Ru 배선도
   킬레이트로 가용화). 과잉이면 오목부까지 등방 용해 → dishing↑.
3. **억제제(BTA/TTA)**: θ→1로 표면을 덮어(§3) 정적식각·오목부 용해를 차단 → dishing↓, 선택성↑.

**정량 균형**: 선행 노트 [[cu-electrochemistry-pourbaix-bta-oxidizer-inhibitor]] §5가 인용한 산업형 슬러리(H₂O₂ 3%/구연산 0.2%/BTA
0.05%, pH 3.7, Lee 2023)에서 **MRR/정적식각 = 11.5** — 이는 (킬레이트+산화제)가 만든 용해 구동력을 BTA 피복률이 오목부에서만 눌러
(θ≈1) 볼록부(패드 접촉·막 마모)에서만 11.5배 빠르게 제거되도록 만든 결과다. 소프트랜딩은 이 비를 유지하며 절대 MRR만 낮추는 조작
(압력↓ + 억제제/산화제 비↑)이다(선행 노트 §5).

## 7. 코드 재현 (verify) — 세 개의 assert 증명

```python verify
# verify 1 — MINTEQ v4 DB(papers/phreeqc-minteq.v4.dat) 누적 양성자화상수에서 단계별 pKa를 유도해
# popuri2017(OA, doi 10.1149/2.0111709jss)의 CMP 문맥 시트르산 pKa(3.2/4.9/6.4)와 독립 교차검증한다.
# 값은 기억이 아니라 DB 줄(L6401/6409/6417, L9337/9345)에서 옮김.
# 시트르산: H+ + Cit3- = HCit2- (6.396), 2H+ = 11.157, 3H+ = 14.285 (누적 log beta)
cit_cum = [6.396, 11.157, 14.285]
pKa3 = cit_cum[0]
pKa2 = cit_cum[1] - cit_cum[0]
pKa1 = cit_cum[2] - cit_cum[1]
print(f"citric pKa1/pKa2/pKa3 = {pKa1:.2f}/{pKa2:.2f}/{pKa3:.2f}")
# popuri2017 본문: pKa1=3.2, pKa2=4.9, pKa3=6.4 (전문 확보 PDF)
popuri = (3.2, 4.9, 6.4)
assert abs(pKa1 - popuri[0]) < 0.15, "pKa1 교차검증 실패"
assert abs(pKa2 - popuri[1]) < 0.20, "pKa2 교차검증 실패"
assert abs(pKa3 - popuri[2]) < 0.05, "pKa3 교차검증 실패"
# 글리신: H+ + Gly- = HGly (9.778), 2H+ = H2Gly+ (12.128)
gly_cum = [9.778, 12.128]
pKa_amino = gly_cum[0]              # -NH3+ 해리 (약 9.8, 교과서값)
pKa_cooh  = gly_cum[1] - gly_cum[0] # -COOH 해리 (약 2.35)
print(f"glycine pKa(amino)/pKa(COOH) = {pKa_amino:.2f}/{pKa_cooh:.2f}")
assert abs(pKa_amino - 9.78) < 0.05 and abs(pKa_cooh - 2.35) < 0.05
print("OK verify1: MINTEQ 시트르산 pKa가 popuri2017과 ±0.2 내 일치, 글리신 pKa는 교과서값 재현")
```

```python verify
# verify 2 — 킬레이트 안정도상수(MINTEQ v4)로 글리신의 "Cu 용해영역 확장"(Aksu&Doyle 2001, doi 10.1149/1.1344532)을 정량 재현.
# Cu2+ + Gly- = Cu(Gly)+  logK1=8.57 (L9449);  Cu2+ + 2Gly- = Cu(Gly)2  logb2=15.7 (L9457)
logK1, logb2 = 8.57, 15.7
K1, b2 = 10**logK1, 10**logb2
logK2 = logb2 - logK1
print(f"Cu-glycinate logK1={logK1}, logK2={logK2:.2f}, logb2={logb2}")
# 단계 안정도상수 순서: K1 > K2 (통계·정전 정상 거동)
assert logK1 > logK2, "K1>K2 위반"
assert abs((logK1 + logK2) - logb2) < 1e-9  # b2 = K1*K2 (로그합)
# 조건부: 글리신 총 0.01 M(Aksu 조건), pH 7. 배위형 Gly- 분율(아미노 pKa 지배)
pKa_amino = 9.778
pH, Lt = 7.0, 0.01
f_gly = 1.0 / (1.0 + 10**(pKa_amino - pH))   # 완전 탈양성자 분율
L = Lt * f_gly
# 총 용해 Cu(II) / 유리 Cu2+
enh = 1 + K1*L + b2*L**2
print(f"pH{pH} [Gly-]={L:.2e} M, 용해 Cu 증대배수 = {enh:.2e}")
assert L < 2e-5, "중성 pH에서 배위형 글리신은 소수여야(zwitterion 지배)"
assert enh > 1e4, "글리신이 Cu 용해영역을 크게 확장(Aksu 서술)해야 함"
# 시트르산 1:1도 강함 (Cu2+ + Cit3- = CuCit-, logK=7.57, L6545) — 글리신 1:1보다 약간 약
assert 7.57 < logK1, "글리신 1:1이 시트르산 1:1보다 강해야(MINTEQ)"
print(f"OK verify2: 0.01M 글리신 pH7이 유리 Cu2+ 대비 용해 Cu를 ~{enh:.0e}배로 증대 => 용해영역 확장 정량화")
```

```python verify
# verify 3 — 억제제 흡착 등온식: Langmuir(overview) 재현 + Frumkin 협동성(측면 인력 f>0)이
# 등온식을 더 가파르게 만듦을 수치로 증명. Langmuir K는 ΔG=-35.4 kJ/mol(overview, 2차 인용)에서.
import math
R, T = 8.314462, 298.15
dG = -35.4e3                       # J/mol (overview §7, 절대값 2차 인용·미검증)
K = math.exp(-dG/(R*T)) / 55.5     # ΔG=-RT ln(55.5 K) -> K (L/mol)
print(f"Langmuir K_ads = {K:.2e} L/mol (overview 2.87e4)")
assert abs(K - 2.87e4)/2.87e4 < 0.02
# Langmuir 피복률
theta = lambda C: K*C/(1+K*C)
C_half = 1.0/K
print(f"반포화 C½ = {C_half*1e6:.1f} µM, θ(1mM) = {theta(1e-3):.3f}")
assert abs(C_half*1e6 - 34.9) < 1.0
assert theta(1e-3) > 0.95          # 1 mM BTA로 거의 포화 -> 낮은 농도로 강한 passivation
# Frumkin: K*C = θ/(1-θ) * exp(-2 f θ). f>0 = 협동적(인력). 같은 θ 구간을 만드는 C 비교.
def C_of_theta(th, f, Kx=1.0):     # Kx는 상대비교라 1로 둠
    return th/((1-th)*Kx*math.exp(2*f*th))
# θ를 0.4 -> 0.6 으로 올리는 데 필요한 농도 변화율
ratio_langmuir = C_of_theta(0.6, 0.0)/C_of_theta(0.4, 0.0)   # f=0 = Langmuir
ratio_frumkin  = C_of_theta(0.6, 1.5)/C_of_theta(0.4, 1.5)   # f=1.5 협동성(시연용 예시값)
print(f"θ:0.4→0.6 농도변화 Langmuir {ratio_langmuir:.2f}배 vs Frumkin(f=1.5) {ratio_frumkin:.2f}배")
assert abs(ratio_langmuir - 2.25) < 0.01
assert ratio_frumkin < ratio_langmuir, "인력 Frumkin이 더 가팔라야(협동적 흡착)"
assert ratio_frumkin < 1.5, "협동성이 뚜렷해야(중합 Cu(I)-BTA 사슬)"
print("OK verify3: BTA는 1mM로 θ>0.96(Langmuir), 중합 측면인력(Frumkin f>0)으로 포화가 더 급격")
```

재현 요약(한 줄): 시트르산 pKa 3.13/4.76/6.40을 popuri2017(3.2/4.9/6.4)과 **대조**해 오차 5% 이내로 수렴, 0.01 M 글리신·pH 7이 유리 Cu²⁺ 대비 용해 Cu를 1.4×10⁶배로 증대, 억제제는 1 mM BTA에서 θ=0.966(Langmuir)이며 Frumkin 측면인력으로 θ:0.4→0.6 농도폭이 2.25배→1.24배로 좁아짐을 재현(§7).

## 8. 한계·정직 표기
- **안정도상수의 이온강도**: MINTEQ v4 log K는 **I=0(무한희석) 25 °C** 값이다. 실 슬러리(I≈0.01–0.1)에서는 활동도계수로 조건상수가
  낮아진다 — §5·verify2의 절대 배수(1.4×10⁶)는 **방향·오더의 증명**이지 실 슬러리 정확값이 아니다(Davies식 보정은 Lv2-1로 위임).
- **글리신 배위형 분율 단순화**: verify2는 아미노 pKa만으로 α를 계산했다(카복실은 pH 7에서 이미 해리 가정). 정확히는 양쪽성이온
  평형·H₂Gly⁺를 모두 포함한 화학종 분포가 필요 — 오더는 안 흔들리나 절대값은 근사.
- **ΔG_ads = −35.4 kJ/mol**은 overview의 WebSearch 요지(2차 인용)이며 1차 논문 전문 미확보. Langmuir K·θ는 이 값에 종속 → **미검증**.
  물리흡착/화학흡착 경계(−20/−40)라는 정성 위치만 신뢰.
- **Frumkin f=1.5는 시연용 예시값**이다. BTA-Cu가 Frumkin에 맞는다는 **방향**(Antonijevic&Petrovic 2008 리뷰·Lewis 1981·inflection DOI)은
  근거가 있으나, 실 f(전위·이온강도 의존)는 이 노트에서 확보하지 못했다 — 협동성의 **부호(f>0)**만 중합막 관찰로 정당화.
- **Aksu&Doyle 2001/2002 본문 미독**(IOP 봇차단). 글리신 용해영역 확장·Cu-글리신 Pourbaix는 회의초록·후속 인용·MINTEQ 상수로
  재구성한 것이며, 저자의 원 도표와 대조하지 못했다.
- **TTA/TAZ 정량**: Antonijevic&Petrovic 2008은 리뷰라 ΔG·f를 원논문별로 흩어 인용 — 이 노트는 "TTA>BTA 효율", "치환기가 흡착등온식을
  바꿈"의 **순위·방향만** 채택. 절대 흡착상수 미검증.
- **Field McCourt McBryde 1974**(citrate 1차 결정, doi 10.1139/v74-458)는 출판사 Cloudflare JS차단으로 전문 확보 실패 — 시트르산 Cu
  상수는 MINTEQ DB(원출처 NIST 컴필레이션)로 대체 확보했고 1974 원논문 값과의 직접 대조는 못 했다.

## 9. 자기시험
→ [[../../agents/slurry-chemistry/EXAMS.md]] Lv1-2 문항 참조.

## 10. 구현 요청
→ `agents/slurry-chemistry/PROFILE.md` "## 구현 요청" 참조 (킬레이트 조건부 안정도상수 → Cu 용해율 스케일러, 억제제 θ → 정적식각 억제인자).
