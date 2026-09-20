<!-- V2-SECTION: R2-slurry | 정본: ARCHITECTURE-V2.md §3 -->
# 경쟁 Langmuir 흡착 K_i 문헌표 — Cu·Fe·Co·W·Al·Mn(·Ru 미확보) 산화물/실리카 표면 흡착 평형상수 (1단계: 문헌만)

> 에이전트: surface-contamination | 작성일: 2026-09-18, 갱신: 2026-09-18(2회차, Ru·Mn·Al 보충)
> 선행: [[post-cmp-residual-metal-prediction-langmuir-scm]] [[post-cmp-metallic-contamination-sources]]

## 1. 왜 필요한가

`sim/tier2_physics/competitive_metal_langmuir.py`의 경쟁 Langmuir 함수는 금속마다 K_i를 받는
자리(`metals: {이름: (K_i, C_i_free)}`)가 있지만, 현재 모듈 안에 실제 박혀 있는 문헌값은
**Cr 하나**(K_CR=1e6 L/mol, Loewenstein·Charpin·Mertens 1999 오더값)뿐이다
([[post-cmp-residual-metal-prediction-langmuir-scm]] §2·§7). 이 노트는 Cu·Fe·Co·W(+Co 관련
James&Healy)·**Al**(2회차, Dugger et al. 1964)·**Mn**(2회차, Coughlin & Stone 1995, 침철석
타계값)의 표면 금속흡착 평형상수를 1차 문헌에서 확보한다. **Ru는 1·2회차 모두 확보 실패**
(§8). 이 과제는 문헌 정리만이며, `sim/`는 0줄도 건드리지 않았다.

## 2. 확보 결과 요약

| 금속 | 1차 문헌 | scope --check | 표면 | 상태 |
|---|---|---|---|---|
| Fe | Schindler et al. 1976 | ✓ 허용 | 실리카(Silikagel H) | 확보(조건부 SCM 상수) |
| Cu | Schindler et al. 1976 **+** Sun 2007(기존 노트) | ✓ 허용 (둘 다) | 실리카(Aerosil 200 / TEOS 산화막) | 확보(두 독립 1차, 값이 갈림 — §5) |
| Co | James & Healy 1972 Part I | ✓ 허용 | 실리카(SiO₂) | **부분 확보** — Langmuir/SCM형 K_i가 아니라 다른 정의(§3.3) |
| W | Gustafsson 2003 | ✓ 허용 | 페리하이드라이트(수산화철, **실리카·알루미나 아님**) | 확보하되 표면 불일치 명시(§3.4) |
| Ru | — | — | — | **1차 미확보**(1·2회차 모두 실패, §8) |
| Mn | Coughlin & Stone 1995 | ✓ 허용 | 침철석(α-FeOOH, goethite, **실리카·알루미나 아님**) | **확보**(TLM, 표면 불일치 명시, 정의체계 D′ 신설, §3.6) |
| Al | Dugger, Stanton, Irby, McConnell, Cummings, Maatman 1964 | ✓ 허용 | 실리카젤(Davison Code 40, 산세척, BET 498 m²/g) | **확보**(열역학적 이온교환 K, 정의체계 E 신설, §3.5) |

Cr(기존 Loewenstein 1999)까지 포함하면 K_i 문헌표에 **8개 금속 종**(Cr·Fe·Cu·Co·W·Al·Mn, Cu는
중복 2건)이 기록된다 — 1회차 종료 시점(6개)에서 **Al·Mn 2개 증가**, Ru는 2회차도 실패.

## 3. K_i 표 — 정의별로 분리 (섞지 않음, §4 참고)

### 3.1 표 A — Langmuir 사이트경쟁 K_i (기존 노트, 대조용 그대로 인용)
| 금속종 | 흡착체 | pH | 이온세기 | K_i (L/mol) | 정의 | 온도 | 출처 |
|---|---|---|---|---|---|---|---|
| Cr³⁺ | 친수성 화학산화막 Si(100) | 3 (단독실험) | 미기재(희석 HNO₃, 배경전해질 농도 불명) | ≈10⁶ (오더값, 저자 "about") | σ=σ0·K[M]/(1+K_H[H+]+K[M]) (Langmuir 사이트경쟁, Eq.22) | 20 °C | Loewenstein·Charpin·Mertens 1999 |
| H⁺ | 〃 | — | 〃 | K_H≈10³ (오더값, 저자 "probably") | 〃 | 20 °C | 〃 |

이 값은 이미 `sim/tier2_physics/competitive_metal_langmuir.py`의 `K_CR`/`K_H_DEFAULT`와 동일 —
재인용만, 이 노트에서 새로 만든 수치 없음.

### 3.2 표 B — Schindler 1976 조건부 표면착화 상수 *K₁′, *β₂′ (실리카, 25 °C)
반응: `≡SiOH + Mᶻ⁺ ⇌ (≡SiO)M^(z-1)+ + H⁺` (*K₁′), `2≡SiOH + Mᶻ⁺ ⇌ (≡SiO)₂M^(z-2)+ + 2H⁺` (*β₂′).
전위차 ψ=0 근사(Eq.10)를 적용한 **조건부**(intrinsic, 특정 이온세기에서) 상수 — 정의상
무차원(몰분율 비, 미검증 재확인은 §6).

| 금속이온 | 흡착체 | 이온세기(배경전해질) | pH | log*K₁′ | log*β₂′ | 온도 | 출처 |
|---|---|---|---|---|---|---|---|
| Fe³⁺ | Silikagel H (실리카젤, BET 3.72×10⁹ cm²/kg) | 3 M NaClO₄ | 적정범위 −log[H⁺]≈1–8 (단일 pH 아님, 전 구간 적합) | −1.77 (±0.04) | −4.22 (±0.06) | 25 °C | Schindler, Fürst, Dick, Wolf 1976 |
| Cu²⁺ | Aerosil 200 (실리카, BET 1.60×10⁹ cm²/kg) | 1 M NaClO₄ | 〃 | −5.52 (±0.13) | −11.19 (±0.02) | 25 °C | 〃 |

(논문은 Cd²⁺·Pb²⁺도 같은 표에 보유하나 이번 과제 목표 금속(Cu·Fe·Co·W·Ru)에 없어 표에서 뺐다.)

### 3.3 Co — James & Healy (1972) Part I: **Langmuir/SCM형 K_i 미기재** (정의 불일치, 정직 표기)
- 출처: R. O. James, T. W. Healy, "Adsorption of Hydrolyzable Metal Ions at the Oxide–Water
  Interface. I. Co(II) Adsorption on SiO₂ and TiO₂ as Model Systems", *J. Colloid Interface
  Sci.* 40(1), 42–52 (1972), doi:10.1016/0021-9797(72)90172-5 (원문 PDF
  `papers/james1972-jcis-co-adsorption-sio2-tio2-model-systems.pdf`, sci-hub.kr에서 제목·저자·
  DOI 대조 후 확보).
- 이 논문은 등온선(흡착밀도 vs pH·농도)을 Stern–Grahame 이중층 모델로 해석해 **특이흡착
  자유에너지 φ**(Eq.5, Grahame식)만 보고한다 — Loewenstein의 몰농도 기반 질량작용 K_i(L/mol)나
  Schindler의 조건부 표면착화 *K₁′와 **정의가 다르다**(전기이중층 특이흡착 포텐셜이지, 표면
  자리 경쟁이나 배위결합 반응의 평형상수가 아니다). 따라서 **같은 표에 넣지 않는다.**
  - TiO₂ 위 Co²⁺: φ ≈ −5.5, −5.0, −4.1 kcal/mol (각각 10⁻⁵, 10⁻⁴, 10⁻³ M, pH 5.6=PZC 근방).
  - SiO₂ 위 Co²⁺: φ ≈ −2.2 kcal/mol (10⁻²~10⁻⁴ M) — **저자 스스로 "pH 2.0까지의 외삽이라
    불확실하다(unreliable)"고 명시**. 이온세기·배경전해질 농도는 본문에 구체 수치 없음
    (미기재).
  - K_i로 변환 안 함: φ→K 변환은 표면전위 ψ(≠0)와 흡착자리 밀도를 알아야 하는데 이 논문은
    SiO₂ 쪽에서 그 값을 안 준다(TiO₂만 EDL 특성이 잘 맞다고 서술). 환산 근거가 없으므로
    **환산하지 않는다**(작업지시 "환산 근거가 없으면 환산하지 마라").
  - Part III(같은 저자, doi:10.1016/0021-9797(72)90174-9, "열역학 모델")가 ΔG°ads 같은 수치를
    더 줄 가능성이 있지만, sci-hub 접근이 반복 캡차("로봇 확인")로 막혀 **이번 회차에는
    원문을 못 봤다** — 미확보로 남긴다(§8).

### 3.4 W — Gustafsson 2003 DLM 상수 (표면 불일치 명시: 페리하이드라이트, 실리카·알루미나 아님)
- 출처: J. P. Gustafsson, "Modelling molybdate and tungstate adsorption to ferrihydrite",
  *Chem. Geol.* 200(1–2), 105–115 (2003), doi:10.1016/S0009-2541(03)00161-X (원문 PDF
  `papers/gustafsson2003-chemgeo-molybdate-tungstate-ferrihydrite.pdf`, KTH DiVA 리포지토리
  OA).
- ⚠ **이 논문의 흡착체는 신선 페리하이드라이트(수산화철, HFO)다 — 과제가 요구한 "실리카·
  알루미나 표면"이 아니다.** CMP 관련 텅스텐 이온(WO₄²⁻, 음이온!) 흡착 SCM 문헌 중 이번
  탐색에서 primary로 확보 가능했던 것이 이것뿐이었다(§8, OpenAlex/Crossref로 알루미나·실리카
  대상 텅스텐산 흡착 논문을 찾지 못함). **타계(iron oxide) 전이값 — 실리카 표면 예측에
  직접 쓰면 안 된다.**
- 조건: 0.01 M NaNO₃, pH 3–10, 25 °C, 총 Fe 3×10⁻⁴~3×10⁻³ M, WO₄²⁻ 초기농도 50 µM, DLM
  (Dzombak & Morel 1990 diffuse-layer model), FITEQL 4.0 비선형 회귀.
- 반응(Table 2): D4. `≡FeOH + WO₄²⁻ + 2H⁺ ⇌ ≡FeOW(OH)₅ + H₂O` (완전 양성자화 단좌표);
  D6. `≡FeOH + WO₄²⁻ + H⁺ ⇌ ≡FeOHWO₄²⁻ + H₂O` (부분 양성자화).
- log K_D4,INT(가중평균) = **19.31**(총Fe 2개 런에서 수렴 위해 고정, 1개 런만 σ=0.064로 자유적합);
  log K_D6,INT(가중평균) = **6.40**(σ 0.037/0.046/0.13, 3개 런 모두 자유적합) — 단위는 D4가
  [H⁺]⁻² 항을 포함해 D6과 정의(반응식의 H⁺ 차수)가 달라 **두 상수를 서로 비교하면 안 된다**
  (같은 표 안에서도 반응식이 다르면 값을 섞어 해석 금지).
- 정의: DLM intrinsic 상수는 전기이중층 보정(o-plane 전위)을 포함한 질량작용 상수로,
  Schindler의 ψ=0 근사 *K₁′나 Loewenstein의 순수 몰농도 K_i와도 정의가 다르다(§4).

### 3.5 Al — Dugger et al. 1964 열역학적 이온교환 상수 (실리카젤, 정의체계 E 신설)
- 출처: D. L. Dugger, J. H. Stanton, B. N. Irby, B. L. McConnell, W. W. Cummings, R. W. Maatman,
  "The Exchange of Twenty Metal Ions with the Weakly Acidic Silanol Group of Silica Gel", *J.
  Phys. Chem.* 68(4), 757–760 (1964), doi:10.1021/j100786a007 (원문 PDF
  `papers/dugger1964-jpc-exchange-twenty-metal-ions-silanol-silica-gel.pdf`, sci-hub.ru→
  storage.sci-hub.red에서 확보, PDF 첫 페이지 제목·저자·DOI를 sci-hub 랜딩 페이지 citation
  메타데이터와 대조해 오염 없음 확인).
- 흡착체: Davison Code 40 실리카젤(6–12 mesh), Ahrland·Grenthe·Norén 절차로 산세척해 표면이
  완전히 실라놀(−SiOH)형임을 확인(문헌 인용, ref 8). 공극부피 0.40 mL/g, BET 표면적 498 m²/g.
  **이 논문에 Mn·Ru는 없다** — 표 II·표 I 전체(22개 양이온: Li·Na·K·Mg·Ca·Sr·Ba·Al·Sc·Cr·Fe·
  Co·Ni·Cu·Zn·Ag·Cd·La·Sm·Gd·Th·UO₂)를 PyMuPDF로 렌더링해 육안 대조했고 Mn·Ru 행은 존재하지
  않는다(§6 (5)에서 이 22종 리스트를 기계적으로 assert).
- 반응(본문 Reaction I): `m(−SiOH) + Mⁿ⁺ ⇌ M(O−Si−)_m + mH⁺` — **m=n으로 가정**(금속이온의
  전하 전부가 한 번에 교환된다고 가정, Al³⁺이면 m=3). 이는 Schindler(정의 B)가 반응을
  1개·2개 프로톤 방출 단계(*K₁′, *β₂′)로 쪼갠 것과 **근본적으로 다른 화학양론**이다. 또한
  표준상태를 "무한희석 흡착거동을 외삽해 얻은, 완전피복 표면"으로 잡고(전기이중층 보정
  없음, ψ 항 자체가 논문에 없음), log K′를 금속이온 농도 C_M→0으로 **외삽**해 열역학적 K를
  얻는다(Schindler의 고정 이온세기 조건부 상수, Gustafsson의 DLM 정전보정 상수와도 다름).
  **따라서 A/B/C/D 어디에도 맞지 않아 새 정의체계 E로 분리한다**(§4).
- 조건(Al³⁺, 각주 c·f): pH 1.00–2.70(적정범위), 평형농도 0.01–0.6 M Al(NO₃)₃(하한 0.01–0.05 M,
  상한 0.3–0.6 M) — **고정 배경전해질 없음**(Schindler류와 달리 염 자체의 이온세기가 실험마다
  달라짐, C→0 외삽으로 이 문제를 우회한다고 저자가 명시).
- 값(Table I, pK = −log K, 5개 온도):

  | 온도(°C) | pK (플롯에 쓰인 log K′ 개수) |
  |---|---|
  | 5  | 9.6 (10) |
  | 20 | 8.5 (20) |
  | 35 | 7.9 (10) |
  | 50 | 7.5 (5) |
  | 65 | 6.4 (8) |

  (평균오차 ±0.2 pK 단위, 저자 명시)
- 값(Table II, 25°C=298K로 보간한 열역학 함수, 단일-금속-산소 결합당 자유에너지 포함):
  ΔF°₂₉₈ = **11.5 kcal/mol**, ΔH° = **21.6 kcal/mol**(흡열), ΔS°₂₉₈ = **34.0 e.u.**(cal/mol/K),
  ΔF₂°/m (−SiO⁻–Al 결합 1개당 자유에너지) = **−5.8 kcal/mol**.
- **김·Ru와 마찬가지로 실리카젤 표면흡착 K_i를 CMP 슬러리(습식 콜로이드 실리카)에 직접 쓸 때
  주의**: Dugger의 실리카젤은 건조·소성된 다공성 겔(Davison Code 40)이며 CMP 슬러리의 습식
  콜로이드 실리카(Aerosil/TEOS류, §3.2 Schindler·기존 Sun)와 표면 제법이 다르다 — E2(동일계
  폐형식, 표면제법 차이)로 분류한다(§5 Cu 사례와 같은 논리, 단 Al은 대안 문헌이 없어 스코프
  분리 없이 이 값 하나만 표에 올린다).

### 3.6 Mn — Coughlin & Stone 1995 TLM 상수 (표면 불일치 명시: 침철석, 실리카·알루미나 아님, 정의 D′)
- 출처: B. R. Coughlin, A. T. Stone, "Nonreversible Adsorption of Divalent Metal Ions (Mn(II),
  Co(II), Ni(II), Cu(II), and Pb(II)) onto Goethite: Effects of Acidification, Fe(II) Addition,
  and Picolinic Acid Addition", *Environ. Sci. Technol.* 29(9), 2445–2455 (1995),
  doi:10.1021/es00009a042 (원문 PDF
  `papers/coughlin1995-est-divalent-metal-ions-goethite-nonreversible.pdf`, sci-hub.ru→
  storage.sci-hub.red에서 확보, sci-hub 랜딩 citation 메타데이터와 PDF 1페이지 저자·제목
  대조로 오염 없음 확인).
- ⚠ **흡착체는 침철석(α-FeOOH, goethite)이다 — 실리카·알루미나가 아니다.** W(§3.4
  Gustafsson)와 같은 사유로 **타계(iron oxide) 전이값**임을 표에 그대로 남긴다. 이번 회차
  탐색에서도 실리카·알루미나 대상 Mn²⁺ 흡착 SCM 1차 문헌은 찾지 못했다(§8).
- 조건: 10 mM NaNO₃(이온세기 고정 배경전해질), pH 3–8(아세트산/HEPES 완충), 침철석 표면적
  47.5 m²/g, 자리밀도 7.0 sites/nm², 침철석 로딩 1.0–10.0 g/L, 총 Mn²⁺ 농도 µM 수준(원문
  "5.0 µM total Me²⁺" 계열 실험과 동일 스케일). **온도 명시 없음**(상온으로 추정, 저자가
  본문에 값을 적지 않아 미기재로 남긴다).
- 모델: **삼중층모델(Triple Layer Model, TLM)** — Hayes & Leckie(1987, ref 6) 파라미터를
  그대로 채용(내부층 정전용량 1.1 F/m², 외부층 정전용량 0.20 F/m², 표면 프로톤화 log*K
  +5.80/−11.10, 전해질 흡착 log*K −8.80/−7.60). **W(§3.4)의 DLM(Dzombak–Morel 확산층모델)과
  전기이중층 처리 방식이 다르다** — TLM은 내부·외부 두 개의 정전용량 평면을 명시적으로
  갖는 반면 DLM은 확산층 하나만 가정한다. 따라서 같은 "정전보정 포함 질량작용 상수"라도
  **D(Gustafsson DLM)와 곧바로 병합하지 않고 D′로 분리**한다(§4).
- 반응(Table 2, Eq.5): `≡SOH + Mn²⁺ ⇌ ≡SOMn⁺ + H⁺` — Fe²⁺만 예외적으로 다른 화학양론
  (Eq.6, `≡SOH+Fe²⁺+H₂O⇌≡SOFeOH⁰+2H⁺`)을 쓴다고 저자가 명시; Mn²⁺·Co²⁺·Ni²⁺·Cu²⁺·Pb²⁺는
  모두 Eq.5 화학양론을 공유한다(Schindler류 정의 B의 반응식과 형태는 같지만 TLM 정전보정이
  들어간다는 점이 다름 — B와도 병합 금지).
- 값(Table 2, log K_ads, TLM intrinsic 상수): **Mn²⁺ = −1.9**(오차범위 본문 미기재).
  같은 표의 다른 금속(비교용, 이 노트의 K_i 표에는 안 올림): Co²⁺ −0.8, Ni²⁺ −0.7,
  Cu²⁺ +2.5, Pb²⁺ +2.1 — Irving–Williams 순서(Mn≪Co≈Ni<Cu, Pb는 이온반경 예외)와 일치한다고
  저자가 서술(§6에서 이 순서를 정량 재현).
- W(§3.4)와 마찬가지로 이 값을 CMP 슬러리(실리카/세리아 콜로이드) 예측에 직접 쓰면 안 된다 —
  흡착체가 다르다(E4, §3.4와 동일 등급).

## 4. 정의 통일 검사 (섞으면 안 되는 이유)

| 정의체계 | 반응/식 | 단위 | 전기이중층 처리 | 출처 |
|---|---|---|---|---|
| A. Langmuir 사이트경쟁 K_i | σ=σ0·K[M]/(1+ΣK_j[M_j]) | L/mol | 없음(암묵적으로 무시) | Loewenstein 1999 (Cr) |
| B. Schindler 조건부 *K₁′/*β₂′ | ≡SiOH+M⇌(≡SiO)M+H⁺ | 무차원(몰분율비) | ψ=0 근사(무시, 명시적 근사) | Schindler 1976 (Fe·Cu) |
| B′. Sun 2007 FITEQL pK1/pK2 | 위와 동일 반응식 | 무차원 | 전체 확산이중층(DDL) 적용 | Sun 2007 (Cu, 기존 노트) |
| C. James&Healy 특이흡착 φ | Grahame 식 Γ=2rC exp(−zeφ/kT) | kcal/mol (자유에너지) | Stern-Grahame 이중층 명시 | James&Healy 1972 (Co) |
| D. Gustafsched(Gustafsson) DLM log K_INT | ≡FeOH+WO₄²⁻+nH⁺⇌착물 | (mol/L)⁻ⁿ 질량작용, o-면 전위 보정 포함 | DLM(확산층+정전보정) | Gustafsson 2003 (W) |
| D′. Coughlin&Stone TLM log K_ads | ≡SOH+Mn²⁺⇌≡SOMn⁺+H⁺ | 무차원(몰농도 질량작용), 내부·외부 이중 정전용량 평면 보정 포함 | TLM(삼중층모델, Hayes&Leckie 파라미터) | Coughlin & Stone 1995 (Mn) |
| E. Dugger 1964 열역학적 완전교환 K | m(−SiOH)+Mⁿ⁺(m=n)⇌M(OSi−)_m+mH⁺, C_M→0 외삽 | pK(무차원, 몰분율 근사)이지만 **m=n 전하 전체 교환**이라 B의 단계별 *K₁′/*β₂′와 화학양론 자체가 다름; 부가로 ΔF₂°/m(kcal/mol, 결합 1개당) 병행 보고 | 없음(ψ 항 자체가 없음, 무한희석 외삽으로 활동도 문제 우회) | Dugger et al. 1964 (Al) |

**B와 B′는 반응식이 동일**(같은 두 자리 유형)하므로 원칙적으로 같은 표에 넣을 수 있다 —
실제로 §5에서 그렇게 비교한다. **A/B/C/D/D′/E는 서로 다른 정의라 절대 같은 열에 넣지 않았다**
(표 A·B·3.3·3.4·3.5·3.6을 분리한 이유). D와 D′는 둘 다 "정전보정 포함 질량작용 상수"라는
점에서 표면적으로 비슷하지만 **이중층 모델 자체가 다르다**(DLM: 확산층 1개, TLM: 정전용량
평면 2개) — 모델이 다르면 같은 반응식이라도 log K_INT 수치가 다른 스케일에 놓이므로 병합하지
않는다. E는 B와 언뜻 비슷해 보이지만(둘 다 −SiOH 반응, 무차원 상수) **화학양론이 다르다** —
B는 1가·2가 프로톤 방출 단계를 각각 K₁′·β₂′로 분리해 다가 이온이라도 부분 중화된 착물을
허용하는 반면, E는 처음부터 m=n(전하 전부 중화)만 가정하고 그 가정 위에서 무한희석 외삽으로
열역학적 K를 구한다. 같은 표에 넣으면 "1개 프로톤 방출 착물"과 "전하 전부 중화 착물"을 같은
숫자로 취급하는 오류가 된다.

## 5. Cu K₁ 값이 갈리는 경우 — 평균내지 않고 스코프를 쪼갠다

같은 반응식(≡SiOH+Cu²⁺⇌≡SiOCu⁺+H⁺)에 대해 두 독립 1차 문헌이 다른 log K₁ 값을 준다:

| 문헌 | 흡착체 | 이온세기 | 방법 | log K₁ |
|---|---|---|---|---|
| Schindler 1976 | Aerosil 200 (건식 실리카) | 1 M NaClO₄ | 전위차적정, 선형(y=x) 회귀, ψ=0 근사 | −5.52 |
| Sun 2007 (기존 노트 §4) | TEOS 산화막 | 0.01 M | FITEQL, 확산이중층모델(DDL) 비선형 회귀 | −4.35 |

차이는 1.17 log 단위(≈14.8배) — **작지 않다**. EVIDENCE-RULES에 따라 평균내지 않는다.
근거 서열로는 둘 다 **E2(동일계 폐형식, 대상계이지만 표면제법·전해질이 다름)**로 같은
등급이라 "더 나은 값"을 고를 근거가 없다 — 대신 **원인이 되는 조건 차이를 스코프로
명시**한다:
1. 흡착체 제법이 다르다 — 건식 실리카젤(Aerosil, 열처리 발열 실리카) vs 습식 TEOS 산화막
   (CMP 슬러리 맥락에 더 가까움).
2. 이온세기가 100배 다르다(1 M vs 0.01 M) — Schindler의 ψ=0 근사는 고이온세기에서 더
   타당하지만 Sun은 저이온세기에서 DDL을 정식으로 풀어 전위항을 명시적으로 넣었다.
3. **두 값 다 "표에 넣되 스코프를 분리해서" 기록한다** — CMP 슬러리(저이온세기, 습식 산화막)
   맥락엔 Sun 2007이 더 가깝고, 고염 세정액(예: SC-1, I~수백 mM) 맥락엔 Schindler가 더
   가깝다는 것이 스코프 분리 기준이다.

## 6. 정량 재현 절 (python verify)

```python verify
import math

# ===== (1) Schindler 1976 Table II Fe3+: Eq.16 Z(pH)가 물리적으로 1~2 범위를 벗어나지 않아야 한다 =====
# Z = "흡착된 M당 방출된 H+ 수" — 반응[1](n=1)만 있으면 Z=1, 반응[2](n=2)만 있으면 Z=2.
logK1_Fe, logB2_Fe = -1.77, -4.22   # Table II, Silikagel H, I=3M NaClO4, 25C
K1_Fe, B2_Fe = 10**logK1_Fe, 10**logB2_Fe
Co_silikagel = 3.6  # mol/kg, Silikagel H 총 실라놀 자리 (본문 "Co = 3.6 mole·kg-1")

def Z_fe(pH):
    H = 10**-pH
    return (K1_Fe + 2*B2_Fe*Co_silikagel/H) / (K1_Fe + B2_Fe*Co_silikagel/H)

z_vals = {pH: Z_fe(pH) for pH in (1, 2, 3, 4, 5)}
for pH, z in z_vals.items():
    assert 1.0 <= z <= 2.0, f"pH{pH}: Z={z} 물리적 범위 밖"
assert z_vals[1] < z_vals[2] < z_vals[3] < z_vals[4]   # Fig.2 추세(저pH→고pH, Z 단조증가)와 방향 일치
assert z_vals[1] < 1.2 and z_vals[4] > 1.9              # 저pH에서 반응[1] 지배, 고pH에서 반응[2] 지배
print(f"(1) Schindler Fe Z(pH): {{{', '.join(f'{p}:{v:.3f}' for p,v in z_vals.items())}}} — 1<=Z<=2 만족, 단조증가")

# ===== (2) Cu K1 두 문헌 정량 대조 (평균내지 않음, 차이만 계산) =====
logK1_Cu_schindler = -5.52   # Aerosil 200, I=1M NaClO4
logK1_Cu_sun = -4.35         # TEOS 산화막, I=0.01M, FITEQL (Sun 2007, 기존 노트 §4 pK1=4.35)
diff_log = logK1_Cu_schindler - logK1_Cu_sun
factor = 10**abs(diff_log)
assert 1.0 < abs(diff_log) < 1.5      # "작지 않은 차이" 정량 확인 (평균 금지 판단의 근거)
assert 14 < factor < 16
print(f"(2) Cu log K1: Schindler {logK1_Cu_schindler} vs Sun {logK1_Cu_sun} → 차이 {diff_log:.2f} log단위 ({factor:.1f}배, 원인: 흡착체·이온세기 다름, §5)")

# ===== (3) Gustafsson 2003 Table 4 텅스텐 D6 가중평균 재현 (Dzombak-Morel 오차전파식) =====
vals = [6.60, 6.21, 6.24]     # log K_D6,INT, 3개 총Fe 농도 런
sigmas = [0.037, 0.046, 0.13]
w = [1/s**2 for s in sigmas]
wavg = sum(v*wi for v, wi in zip(vals, w)) / sum(w)
reported = 6.40
diff_pct = abs(wavg - reported) / reported * 100
assert diff_pct < 1.0   # 논문이 명시한 절차(역분산 가중평균)를 0.58% 이내로 재현
print(f"(3) Gustafsson W D6 가중평균 재계산 {wavg:.3f} vs 논문 {reported} → 차이 {diff_pct:.2f}%")

# ===== (4) 정의 단위 확인: A(L/mol, 유한값)과 B(무차원, <1)는 절대 같은 열에 못 들어간다 =====
K_Cr_A = 1e6   # 표 A, Loewenstein, 정의상 L/mol
K1_Cu_B = 10**logK1_Cu_schindler   # 표 B, Schindler, 정의상 무차원 몰분율비
assert K_Cr_A > 1        # A는 몰농도 역수 크기의 값 (L/mol)
assert K1_Cu_B < 1e-4     # B는 조건부 몰분율비이며 ψ=0 근사에서 항상 <<1
print(f"(4) 정의 확인: K_Cr(A)={K_Cr_A:.0e} L/mol (몰농도 스케일) vs *K1'_Cu(B)={K1_Cu_B:.2e} (무차원, 자릿수부터 다름) — 병합 금지 근거")

# ===== (5) Dugger 1964 Table II Al3+ 행을 PDF에서 기계 추출(육안 아님) =====
import fitz, re

doc = fitz.open("papers/dugger1964-jpc-exchange-twenty-metal-ions-silanol-silica-gel.pdf")
p_dugger = doc[2]   # 원문 p.759, Table II가 있는 페이지
words = p_dugger.get_text("words")

rows = {}
for w in words:
    x0, y0, text = w[0], w[1], w[4]
    if x0 > 300 and 170 <= y0 <= 392:   # 페이지 우측 컬럼(표 영역)만
        rows.setdefault(round(y0), []).append((x0, text))

nums = []
for y in sorted(rows):
    for x, t in sorted(rows[y]):
        m = re.match(r"-?\d+\.\d+", t)
        if m:
            nums.append(float(m.group()))

al_vals = [11.5, 21.6, 34.0, -5.8]   # 표 3.5에 옮겨 적은 ΔF298, ΔH, ΔS, ΔF2/m
found = any(nums[i:i+4] == al_vals for i in range(len(nums) - 3))
assert found, f"Al 행 {al_vals}이 PDF 추출 숫자열에서 연속으로 발견되지 않음: {nums}"
print(f"(5) Dugger 1964 Table II PDF 기계추출: Al3+ 행 {al_vals} 연속 일치 확인(전체 {len(nums)}개 숫자 중)")

# ===== (6) Dugger 1964 전체 텍스트에 Mn·Ru 원소기호(이온형) 부재 확인 (§3.5 "이 논문에 Mn·Ru 없다" 주장) =====
full_text = "".join(pg.get_text() for pg in doc)
assert "Mn" not in full_text, "Mn 토큰이 발견됨 — §3.5 서술과 모순"
ru_hits = re.findall(r"\bRu\d|Ru3\+|RuO4", full_text)   # "Russell"(저자명) 오검출 방지 위해 원소기호 패턴만
assert ru_hits == [], f"Ru 이온 토큰 발견: {ru_hits}"
print("(6) Dugger 1964 전체 텍스트에 Mn 토큰 0회, Ru 이온형 토큰 0회 — 이 논문은 Al만 제공(§3.5)")

# ===== (7) Dugger 1964 Al3+ 열역학 자체정합성: ΔG°298 = ΔH° − T·ΔS°298 재현 =====
dH_al, dS_al, dG_al_reported = 21.6, 34.0, 11.5   # kcal/mol, kcal/mol, e.u.(cal/mol/K), kcal/mol
T298 = 298
dG_al_calc = dH_al - T298 * dS_al / 1000
diff_pct_al = abs(dG_al_calc - dG_al_reported) / dG_al_reported * 100
assert diff_pct_al < 1.0   # 저자가 보고한 ΔF298과 0.28% 이내로 일치해야 함
print(f"(7) Dugger Al3+ ΔG298 재계산 {dG_al_calc:.2f} kcal/mol vs 논문 {dG_al_reported} kcal/mol → 차이 {diff_pct_al:.2f}%")

# ===== (8) Coughlin & Stone 1995 Table 2 Mn2+ log Kads를 PDF에서 기계 추출 =====
doc_cs = fitz.open("papers/coughlin1995-est-divalent-metal-ions-goethite-nonreversible.pdf")
full_cs = "".join(pg.get_text() for pg in doc_cs)
i_tab2 = full_cs.find("TABLE 2")
tab2_block = full_cs[i_tab2:i_tab2 + 1600]
# Table 2 원문 레이아웃: "Kads\n-1.9\n-\n-0.8\n-0.7\n+2.5\n+2.1" (Mn,Fe,Co,Ni,Cu,Pb 순, Fe는 다른 화학양론이라 '-')
m = re.search(r"Kads\s*\n?\s*(-?\d+\.\d+)\s*\n?\s*-\s*\n?\s*(-?\d+\.\d+)\s*\n?\s*(-?\d+\.\d+)\s*\n?\s*\+?(\d+\.\d+)\s*\n?\s*\+?(\d+\.\d+)", tab2_block)
assert m, f"Table 2 Kads 행을 PDF에서 못 찾음: {tab2_block[:400]!r}"
mn_kads, co_kads, ni_kads, cu_kads, pb_kads = float(m.group(1)), float(m.group(2)), float(m.group(3)), float(m.group(4)), float(m.group(5))
assert mn_kads == -1.9, f"Mn log Kads 추출값 {mn_kads} != 표 3.6 기재값 -1.9"
print(f"(8) Coughlin&Stone 1995 Table 2 PDF 기계추출: log Kads(Mn2+, TLM, goethite) = {mn_kads} (Co={co_kads}, Ni={ni_kads}, Cu={cu_kads}, Pb={pb_kads})")

# ===== (9) Irving-Williams 순서 재현: Mn < Co < Ni < Cu (저자가 본문에서 주장한 추세) =====
iw_seq = [mn_kads, co_kads, ni_kads, cu_kads]
assert all(iw_seq[k] < iw_seq[k+1] for k in range(len(iw_seq) - 1)), f"Irving-Williams 순서 불일치: {iw_seq}"
print(f"(9) log Kads 순서 Mn<Co<Ni<Cu 확인: {iw_seq} — 본문의 Irving-Williams 추세 서술과 일치")
```

**결과 해석(정직하게)**: (1) Schindler 1976의 Fe³⁺ Table II 상수를 논문 자신의 Eq.16에 넣으면
Z가 저pH 1.11→고pH 1.999로 물리적으로 요구되는 [1,2] 범위 안에서 단조증가한다 — 원문 Fig.2의
정성적 추세(2−Z가 pH 1~3에서 감소)와 방향이 맞는다. Fig.1의 실제 %ads 곡선은 실험별 A/V
스케일 인자(A′)가 본문에 없어 재현하지 못한다(§3.2 한계). (2) Cu의 두 1차 문헌값은 14.8배
차이가 나며 이는 §5에서 결정한 "평균 금지, 스코프 분리"를 정량으로 뒷받침한다. (3) Gustafsson
2003의 텅스텐 D6 가중평균은 저자가 명시한 Dzombak–Morel 역분산 가중평균 절차로 0.58% 이내
재현된다 — 표 3.4의 log K=6.40 값이 창작이 아니라 원문 절차의 산출물임을 확인. (4) 표 A와
표 B의 K는 자릿수 스케일 자체가 다르므로(L/mol 유한값 vs 무차원 몰분율비<<1) 같은 열에 넣는
것 자체가 정의 오류라는 것을 수치로 보인다. (5)–(6) Dugger 1964 PDF를 PyMuPDF로 기계
판독(육안 아님)해 §3.5의 Al³⁺ 행(ΔF298=11.5, ΔH=21.6, ΔS=34.0, ΔF₂/m=−5.8)이 원문 Table II
숫자열에 실제로 연속 등장함을 확인했고, 전체 텍스트에 Mn 토큰이 전혀 없고 Ru 이온형 토큰도
없음을 확인했다 — "이 논문은 Al만 제공, Mn·Ru는 없다"는 §3.5 서술이 창작이 아님을 기계로
증명. (7) Dugger가 보고한 ΔH°·ΔS°로 ΔG°298을 재계산하면 저자 자신이 보고한 11.5 kcal/mol과
0.28% 이내로 일치한다 — 저자의 온도계수 미분(ΔH,ΔS 산출)과 직접 측정한 ΔG298이 서로 독립
경로로 일치하므로 표 3.5 값이 내적 정합성이 있다. (8) Coughlin & Stone 1995 PDF를 기계
판독해 §3.6의 Mn²⁺ log K_ads=−1.9(TLM, 침철석)가 원문 Table 2에 실제로 있는 값임을 확인.
(9) 같은 표에서 함께 기계추출한 Co²⁺·Ni²⁺·Cu²⁺ 값과 비교하면 Mn<Co<Ni<Cu 순으로 단조증가
하며, 이는 저자가 본문에서 주장한 Irving–Williams 순서와 방향이 일치한다 — 표 3.6의 Mn 값이
표에서 따로 떼어 창작한 숫자가 아니라 원문 표 전체 맥락과 정합함을 보인다.

## 7. 2단계에서 아직 없는 것 — 엔진 등록이 안 되는 이유

이 노트는 K_i를 **문헌에서 확보**했을 뿐이다. `competitive_langmuir_surface()`에 넣으려면
`metals: {이름: (K_i, C_i_free)}`의 **C_i_free(금속이온 유리농도, mol/L)**가 필요한데:
- FabSim의 Recipe/팩 스키마에는 슬러리·세정액의 금속이온 농도 필드가 없다
  ([[post-cmp-residual-metal-prediction-langmuir-scm]] §7과 동일한 결론).
- 이번에 확보한 K_i들도 **정의가 서로 다르다**(§4, 이제 A/B/B′/C/D/D′/E 7개) — 하나의
  `competitive_langmuir_surface` 호출에 표 A(Cr)와 표 B(Fe·Cu)를 그냥 섞어 넣으면 안 된다.
  섞으려면 먼저 Schindler류 조건부 *K₁′를 Loewenstein류 몰농도 K_i로 변환하는 절차가
  필요한데, 그 변환에는 흡착자리 밀도(σ0)와 전위보정(ψ)이 필요하고 지금은 그 변환식 자체가
  검증되지 않았다(§3.3에서 φ→K 변환을 거부한 것과 같은 이유). 2회차에 추가된 D′(Coughlin&
  Stone TLM)·E(Dugger 열역학적 완전교환)도 각각 D(DLM)·B(Schindler 조건부)와 겉보기엔
  비슷해도 전기이중층 모델이나 화학양론이 달라 변환 없이 섞을 수 없다(§4).
- 따라서 2단계는 "C_i_free 스키마 추가"뿐 아니라 "**K_i 정의 변환 절차의 검증**"까지 포함해야
  한다 — 다음 회차가 표만 보고 바로 엔진에 박으면 정의 불일치로 틀린 값이 나온다.

## 8. 정직한 실패·미착수 기록

- **Ru — 1·2회차 모두 확보 실패**. 1회차: OpenAlex·Semantic Scholar(레이트리밋)·Crossref
  질의 모두 무관한 논문만 반환(예: "Ru(III) 암민착물 메조다공성 실리카 그래프팅" 2003 —
  흡착이 아니라 화학적 그래프팅). 2회차(이번 회차)에 **시도한 구체 경로**:
  1. OpenAlex 전문검색 4종("ruthenium adsorption oxide surface complexation constant",
     "ruthenium sorption clay mineral radionuclide oxide surface",
     "ruthenium(III) hydrolysis sorption iron oxide goethite",
     "Ru3+ adsorption oxide surface complexation constant" 등) — 전부 무관 논문만 반환
     (SERS 리뷰, 촉매 담지, 전기화학 등).
  2. 로컬 `papers/INDEX.json`에 이미 등록된 **Ru CMP 1차 문헌 4건**(cui2012 JES, cui2013
     JSST, peethala2011 ESL, xu2022 RSC Adv)을 PyMuPDF로 열어 "adsorption/zeta/log K/
     equilibrium constant/complexation" 키워드를 스캔 — cui2012에 zeta potential 6회
     언급이 있으나 **실리카 입자 자체의 제타전위(pH function)이지 Ru 종의 흡착평형상수가
     아니다**. 나머지 3건은 K_i류 수치 없음.
  3. RuO4 기체상 트랩 문헌(원자력 분야, Ru 방사성핵종 배기가스 포집) 2건을 확인 —
     Spencer et al. 2018 "Initial Assessment of Ruthenium Removal Systems for Tritium
     Pretreatment Off-Gas"(doi:10.2172/1427631, `papers/spencer2017-ornl-ruthenium-capture-
     methods-tritium-offgas.pdf`로 확보, scope --check ✓)와 그 인용 논문(doi:10.2172/1415920)
     을 PyMuPDF로 전수 스캔했으나 **Langmuir/isotherm/평형상수 자체가 없다** — 이 연구는
     기체상 RuO4 제거효율(%)만 보고하는 공학 시험 보고서이며, 애초에 **기체상 흡착이라
     pH·이온세기 조건이 존재하지 않아** 이 노트의 K_i 정의 요구조건(pH·이온세기 병기)을
     구조적으로 만족할 수 없다 — 확보했어도 표에 올릴 수 없는 종류의 문헌임을 확인하고 버림.
  4. OSTI(`osti.gov`) 호스팅 논문 2건(Mn 관련 hematite 논문과 무관하게 Ru 관련도 다수가
     OSTI green OA) 접근 시도 — **`osti.gov`가 이번 세션 네트워크에서 전면 접속 불가**
     (`curl` HTTP 000, 45초 타임아웃 3회 재시도 후 확정). 대체 미러(ORNL 자체
     `info.ornl.gov`)가 있는 보고서는 그걸로 우회했으나(§Mn 참고), Ru 쪽은 대체 미러를
     못 찾음.
  **결론**: CMP·수용액 SCM 맥락에서 Ru 이온(Ru³⁺/RuO₄⁻)의 표면흡착 평형상수를 보고하는
  1차 문헌은 이번 세션 접근 가능 범위에서 존재를 확인하지 못했다. **3회차가 시도할 만한
  남은 경로**: (a) `osti.gov`가 다른 세션에서 접속 가능한지 재확인 후 Ru 방사화학
  흡착(방사성 ¹⁰⁶Ru 토양·점토광물 분배계수 Kd) 문헌 탐색, (b) Crossref를 우회해 Web of
  Science류 상용 DB가 있다면 "ruthenium red" 염료 흡착(생물학 실험시약, 표면 특성화 목적으로
  종종 쓰임 — SCM은 아니지만 흡착 메커니즘 논의가 있을 수 있음, 단 이건 억측이라 검증 안 됨).
- **Mn — 2회차 확보 성공**(Coughlin & Stone 1995, §3.6). 침철석(철산화물) 타계값이며
  실리카·알루미나 대상 Mn²⁺ SCM 문헌은 이번 회차에도 찾지 못했다(ScienceDirect 호스팅
  논문 2건 — Wang et al. 2020 GCA goethite doi:10.1016/j.gca.2020.03.036, MnOx 여과재
  2024 doi:10.1016/j.jwpe.2024.105408 — 은 sci-hub.ru가 두 DOI 모두 "로봇 확인" 캡차로
  차단했고 ScienceDirect 직접 스크레이핑은 JS 렌더링이 필요해 curl로는 셸 페이지만
  받아짐). Hochella et al. 2021 GCA hematite 논문(doi:10.1016/j.gca.2021.05.043)도
  OSTI(1812531) 호스팅이라 위 Ru 항목과 같은 이유로 접속 불가.
- **Al — 2회차 확보 성공**(Dugger et al. 1964, §3.5).
- **Co**: 1차 문헌은 확보(James & Healy 1972 Part I)했으나 K_i 정의의 수치가 아니라 다른
  물리량(특이흡착 자유에너지, SiO₂ 값은 저자가 "unreliable"이라 명시)만 있어 **표 B/A와
  나란히 놓을 수 있는 K_i는 미기재**로 남긴다. Part III(열역학 모델, 같은 저자 1972)가
  ΔG°ads류 수치를 더 줄 가능성이 있으나 sci-hub 캡차("로봇 확인")에 반복 차단되어 이번
  회차에는 못 봤다 — **1차 미확보**로 표기(§3.3).
- **W**: 실리카·알루미나 대상 텅스텐산 흡착 SCM 1차 문헌은 찾지 못했다. 확보한 Gustafsson
  2003은 페리하이드라이트(철산화물) 대상이라 **타계 전이값**이며 그대로 실리카 CMP 예측에
  쓰면 안 된다(§3.4에 경고 명시).
- **네트워크 인프라 관찰(3회차 인계 사항)**: 이번 세션에서 `osti.gov`(DOE OSTI 보고서
  호스트)는 **완전히 접속 불가**(모든 시도 HTTP 000/타임아웃) — OSTI green OA로 표시된
  논문은 우선 "저자 소속기관 자체 리포지토리"(예: `info.ornl.gov`, PNNL 등) 미러를
  DuckDuckGo HTML 검색(`html.duckduckgo.com/html/?q=...`)으로 먼저 찾아라. ScienceDirect는
  curl로는 JS 셸만 받아지므로(OA 라이선스 여부와 무관) **항상 sci-hub나 대체 미러가
  필요**하다. `sci-hub.ru`는 이번 세션에서 간헐적으로 "로봇 확인" 캡차에 걸렸다(같은
  세션 안에서도 DOI별로 성공/실패가 갈림 — Dugger 1964·Coughlin&Stone 1995는 성공,
  Wang 2020·MnOx 2024는 실패) — 실패 시 재시도보다 대체 문헌을 찾는 쪽이 턴 효율적이었다.
  `sci-hub.se`/`sci-hub.st`는 이번 세션도 DNS/연결 실패(HTTP 000, 1회차와 동일).
- **sci-hub 오염 대조**: Dugger 1964·Coughlin & Stone 1995 두 건 모두 **다운로드 직후
  sci-hub 랜딩 페이지의 citation 메타데이터(저자·제목·DOI) 및 PDF 1페이지 본문과 대조해
  오염 없음을 확인**했다(메모리 기록의 sci-hub.kr 오염 사례 경고에 따른 조치).

## 9. 확보 파일

- `papers/schindler1976-jcis-ligand-properties-surface-silanol-fe-cu-cd-pb.pdf` (Fe·Cu SCM)
- `papers/james1972-jcis-co-adsorption-sio2-tio2-model-systems.pdf` (Co, K_i 아닌 φ만)
- `papers/gustafsson2003-chemgeo-molybdate-tungstate-ferrihydrite.pdf` (W, 타계 페리하이드라이트)
- `papers/dugger1964-jpc-exchange-twenty-metal-ions-silanol-silica-gel.pdf` (Al, 정의체계 E)
- `papers/coughlin1995-est-divalent-metal-ions-goethite-nonreversible.pdf` (Mn, 타계 침철석,
  정의체계 D′)
- `papers/spencer2017-ornl-ruthenium-capture-methods-tritium-offgas.pdf` (Ru 기체상 포집
  보고서 — K_i 없음 확인 후 표에는 미반영, §8 기록용으로만 보관)
- 여섯 파일 모두 `papers/INDEX.json`에 등록.

---

## 10. ⚠ 스코프 재검증 — §2 표의 "scope --check ✓" 3건은 **거짓 통과였다** (2026-09-18 Max워커 적발)

위임 세션이 §2 표에 기록한 `scope --check ✓ 허용` 을 Max워커가 수거 시 재실행한 결과,
**연도를 붙이면 결과가 뒤집힌다**:

```
$ .venv/bin/python tools/scope.py --agent surface-contamination --check \
    "The Exchange of Twenty Metal Ions with the Weakly Acidic Silanol Group of Silica Gel"
✓ 허용
$ ... --check "... Silica Gel (1964)"
✗ 제외 — 1964 < before_year 1990 (고전 예외 아님)
```

`tools/scope.py` 의 연도 필터는 **넘겨준 문자열에서 정규식으로 4자리 연도를 찾는다**
(99~103행). 제목만 넘기면 연도가 없어 **필터가 아예 작동하지 않고 ✓ 가 나온다.**
`agents/SCOPE.yaml` 의 `exclude.before_year: 1990` 이 실제로는 적용되지 않은 채
"범위 통과"로 기록된 것이다.

**재실행 결과 (연도 포함):**

| 문헌 | 연도 | 재검증 |
|---|---|---|
| Dugger et al., 실리카젤 20종 금속이온 교환 (Al) | 1964 | **✗ 범위 밖** |
| Schindler et al., 실라놀 리간드 성질 (Fe·Cu) | 1976 | **✗ 범위 밖** |
| James & Healy, 가수분해성 금속이온 흡착 (Co) | 1972 | **✗ 범위 밖** |
| Coughlin & Stone, 침철석 2가 금속이온 (Mn) | 1995 | ✓ 허용 |
| Gustafsson, 몰리브데이트·텅스테이트 페리하이드라이트 (W) | 2003 | ✓ 허용 |

**처리 — 지우지 않고, 승격하지도 않는다:**
1. 위 3건은 **범위 밖으로 표기**한다. 사용자가 정한 경계이고, "넓히고 싶으면 노트에 제안만
   남기고 임의로 넘지 마라"가 명시 규칙이다. `SCOPE.yaml` 은 **고치지 않았다.**
2. 그러나 **삭제하지도 않았다** — 이유: (a) 이 노트는 1단계(문헌 조사)이고 `sim/` 어디에도
   이 값들이 들어가 있지 않다(§7: `C_i_free` 부재로 소비처 0), 즉 **오염 경로가 없다**.
   (b) "범위 밖이라 뺐다"와 "못 찾았다"는 다르다는 것이 SCOPE.yaml `exclude.note` 자신의
   지시이고, 지우면 3회차가 같은 문헌을 다시 파게 된다.
3. **§2·§3 의 해당 행은 이제 "범위 밖(pre-1990), 참고용"으로 읽어야 한다.** 이 값들을 근거로
   어떤 팩터 confidence 도 올리지 않았고 올려서도 안 된다.

**사용자 승인 제안(임의 실행 금지 — 제안만):**
표면착화 상수(SCM) 분야는 1960~70년대 Schindler·James&Healy·Dugger 계열이 **후속 문헌이
계속 인용하는 원 출처**이고, 2000년대 논문들은 대개 이 값을 재인용하거나 재적합한다.
`SCOPE.yaml` 의 `defaults.method.classic_exceptions`(현재 Preston 1927 · Greenwood &
Williamson 1966 · Stine 1997 · Luo & Dornfeld 2001)에 이 3건을 추가하면 **1차 출처를
2차 인용으로 대체해야 하는 역전**을 피할 수 있다. 다만 이는 사용자가 정한 경계를 넓히는
일이므로 **제안만 기록하고 실행하지 않았다.**

**도구 결함 보고(별건, 이 노트 범위 밖):** `--check` 에 제목만 넘기면 연도 필터가 조용히
무력화되는 것은 **감사 도구 자체의 사각지대**다(판정#63 이 다룬 "축 미분류 = 조용한 통과"와
동형). 연도를 못 찾으면 ✓ 를 주지 말고 `⚠ 연도 미상 — 판정 불가` 를 반환하는 편이 안전하다.
`tools/scope.py` 수정은 다른 크론의 소관이라 **여기서는 신고만 한다.**
