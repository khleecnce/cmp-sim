# CMP 억제제 추가 쌍 — 표면 흡착 자유에너지(ΔG_ads) 문헌 조사

조사일: 2026-09-15 · 조사자: FabSim 문헌 서브에이전트
대상: (1) benzenesulfonic acid × Cu, (2) malonic acid × W, (3) benzotriazole(BTA) × Ta/TaN

> **결론 먼저: 3개 쌍 모두 1차 공개 문헌에서 ΔG_ads 수치를 확보하지 못했다.**
> 지어내지 않았다. 아래에 무엇을 어떻게 찾았는지, 그리고 값을 얻기 위한 대체 경로를 남긴다.
> 배경 규칙은 [[inhibitor-beyond-monolayer]] 및 `sim/inhibitor_pairs.py` 주석과 동일하게 적용했다:
> **ΔG_ads 는 (분자 × 기질) 쌍의 성질이다. 다른 기질/다른 분자에서 옮겨 적지 않는다.**

---

## 1. 요약 표

| 쌍 | ΔG [kJ/mol] | K [L/mol] | 측정법 | 등온식 | 조건 | 출처 DOI | 등급 |
|---|---|---|---|---|---|---|---|
| **benzenesulfonic acid × Cu** | **미확보** | 미확보 | — | — | — | — | — |
| **malonic acid × W** | **미확보** | 미확보 | — | — | — | — | — |
| **BTA × Ta 또는 TaN** | **미확보** | 미확보 | — | — | — | — | — |

### 참고 줄 — 값을 옮겨 적으면 안 되는 인접 쌍 (등록 금지, 경계값 참고용)

> ⚠ 아래 세 줄은 **목표 쌍이 아니다.** 분자가 다르거나(설폰아마이드 ≠ 설폰산) 기질이 다르다.
> `inhibitor_pairs.py` 에 등록하면 안 된다. 4절의 부등식 경계 설정에만 쓴다.

| 인접 쌍 | ΔG [kJ/mol] | K | 측정법 | 등온식 | 조건 | 출처 DOI | 등급 |
|---|---|---|---|---|---|---|---|
| sulfathiazole (4-amino-N-(1,3-thiazol-2-yl)**benzenesulfonamide**) × Cu | −33.47 | 13253 dm³/mol | 분극곡선(PDP) + EIS | Langmuir | 0.1 M NaCl, 실온(40–60 °C 별도 시험), pH 미명시(중성 NaCl) | 10.1134/s2070205114040200 (Crossref 실존 확인) | literature (원문 PDF 미열람, 초록·2차 전사 기반) |
| 4-aminobenzene**sulfonamide** (ABSA) × Cu | 수치 미확보 | 미확보 | PDP, CV, 정전위 i–t, DFT/MP2 | Langmuir | 1.0 M HCl | 10.5006/1.3665357 (Crossref 실존 확인) | unverified (ΔG 표 미열람) |
| malonic acid **dihydrazide (MAD)** × **Ni** | −6.426 | 절편 0.2312 (K 단위 미명시) | 전기화학 분극 + 수소발생법 | Langmuir | 1 M H₂SO₄, 30 °C | Arab. J. Chem. (Part II, dihydrazide/Ni) — DOI 미확인 | unverified |

---

## 2. 쌍별 상세

### 2-1. benzenesulfonic acid × Cu — 미확보 (최우선 과제, 계속 추적 필요)

**왜 필요한가 (컨텍스트 재확인).** US9200180B2 계열은 benzenesulfonic acid 1 wt% + H₂O₂ 1 wt% 조성에서
Cu 6.4 nm/min 을 보고한다. 같은 Cu CMP 인 us20110186542a1 계열(620.4 nm/min)과 100배 차이이고,
이 차이는 억제제 항으로만 설명된다. 즉 이 쌍은 FabSim MRR 절대값 예측의 **직접적 차단 요인**이다.

**찾은 것.**
- benzenesulfonic acid(C₆H₅SO₃H) 자체를 구리 부식 억제제로 쓴 전기화학 논문을 **한 편도 찾지 못했다.**
  Crossref `benzenesulfonic acid inhibition copper` 질의는 화합물 사전 항목(Hawley, USP-NF, SDS)과
  염료·PFAS·폴리아스파르트산 유도체만 반환했다.
- 관련 분자로 존재하는 것: **benzenesulfon아마이드** 계열(sulfathiazole, ABSA)과
  **알킬벤젠설포네이트**(SDBS, LABSA, 트리에탄올암모늄 도데실벤젠설포네이트).
  전자는 -SO₂NH- 로 아민/티아졸 질소가 흡착점이라 -SO₃⁻ 단독 흡착과 다른 분자다.
  후자는 C12 알킬 사슬의 소수성 자기조립이 흡착을 지배해 벤젠설폰산과 다른 쌍이다.
- CMP 문헌에서 LABSA(도데실벤젠설폰산)는 **post-CMP 세정 계면활성제**로 등장하며(입자 제거),
  구리 표면 ΔG_ads 는 보고되지 않는다.

**해석.** benzenesulfonic acid 는 pKa ≈ −2.8 로 CMP pH 전 영역에서 완전히 해리된
**벤젠설포네이트 음이온**이다. 강한 무기산 잔기 성격이라 Cu 표면에 배위 결합할 질소·황 lone pair 가 없고,
따라서 고전적 "유기 억제제" 연구 대상에서 벗어나 있다. 그래서 문헌이 비어 있을 가능성이 높다.
US9200180B2 에서의 억제 작용은 **분자 흡착이 아니라 산성화·황산염 유사 음이온에 의한
Cu 표면 상태 변화(황산염 흡착/Cu₂O 안정화)** 일 수 있다.
→ 이 가설이 맞다면 ΔG_ads 항 자체가 잘못된 모델링 축일 수 있으므로 4절의 측정 명세로 먼저 검증해야 한다.

### 2-2. malonic acid × W — 미확보

**찾은 것.**
- **"Use of Malonic Acid in Chemical-Mechanical Polishing (CMP) of Tungsten",
  MRS Proc. 477, 115 (1997), DOI `10.1557/proc-477-115`** — Crossref 실존 확인.
  W-CMP 에서 말론산을 다룬 **유일한 직접 1차 문헌**이었다.
  **초록 전문을 확보해 확인한 결과: 이 논문은 ΔG_ads 를 보고하지 않는다. 배제 확정.**
  초록 원문(전사):
  > "The use of malonic acid as an additive in alumina slurries used for the chemical mechanical
  > polishing (CMP) of tungsten has been explored for the reduction of particulate contamination.
  > The principal objective of this work was to delineate conditions under which alumina
  > contamination on polished surfaces could be reduced. **The interaction between malonic acid and
  > alumina particles** has been investigated through **electrokinetic and adsorption measurements**.
  > At suitable malonic acid concentrations and pH values, tungsten and alumina surfaces develop a
  > negative **zeta potential** resulting in conditions conducive to reduced particulate contamination."

  즉 이 논문의 흡착 측정 대상은 **말론산 × 알루미나 연마입자**이지 **말론산 × W 표면**이 아니고,
  측정량도 자유에너지가 아니라 **제타전위**다. 말론산의 역할은 억제제가 아니라
  **입자 오염 저감용 분산제/전하 조절제**다.
  → **다음 작업자는 이 DOI 를 다시 파지 마라. 본문을 구해도 원하는 값은 없다.**
- 인접: `10.1116/1.581790` "Studies on passivation behavior of tungsten in application to CMP" (JVST, 1999) —
  W 부동태화는 다루지만 말론산 등온식은 미확인.
- W 기질 억제제로 ΔG_ads 가 보고된 예: **benzethonium chloride (BTC) × W**,
  DOI `10.1016/j.jcis.2023.04.012` (J. Colloid Interface Sci., 2023, 중성·알칼리 post-CMP).
  Langmuir 등온식을 썼다고 2차 인용에 나오나 **본문 미열람이라 수치 미확보**.
  이것은 말론산이 아니므로 값 이식 금지. 단 "W 기질에서 Langmuir ΔG 를 실제로 잰 선례"로서
  4절 측정 명세의 방법론 템플릿이 된다.

**해석.** 말론산은 W-CMP 에서 **억제제라기보다 착화제(complexing agent)** 로 작동한다
(WO₃/WO₄²⁻ 용해 촉진·억제 양면). 부식 억제제 문헌에서 다이카복실산 단독의 금속 표면 ΔG 는
드물고, 있더라도 Fe/Ni 기질이다(예: malonic acid dihydrazide × Ni = −6.426 kJ/mol, 1 M H₂SO₄, 30 °C).
**그 값은 분자도 다르고(dihydrazide) 기질도 다르므로(Ni) W 에 쓰면 안 된다.**

### 2-3. BTA × Ta 또는 TaN — 미확보

**찾은 것.**
- BTA × Cu 문헌은 포화 상태지만(리뷰 `10.1016/j.corsci.2010.05.002`, Langmuir 원조 `10.1179/000705981798274850`,
  Cu(111) DFT+분광 `10.1021/acs.langmuir.8b03528`), **Ta/TaN 기질에 대한 BTA 흡착 등온식·ΔG 는 검색되지 않았다.**
- barrier CMP 문헌(`10.1557/proc-767-f6.3` "Selectivity Studies On Tantalum Barrier Layer In Copper CMP",
  `10.1149/1.2912978` Cu/TaN 선택비)은 **제거율 선택비**만 다루고 흡착 열역학은 없다.
- CMP 계열 BTA 이론 논문(`10.1016/j.mee.2022.111833`)은 **Cu 와 Co** 에 대한 것이고 Ta/TaN 은 없다.
  코발트용은 `10.1016/j.apsusc.2024.161684` 가 있으나 역시 Co 기질이다.

**해석.** BTA 는 Cu(I)–BTA 폴리머 형성이 작용 기구의 핵심인데, Ta/TaN 은 Ta₂O₅ 로 즉시 부동태화되어
BTA 가 결합할 d-밴드 금속 사이트를 노출하지 않는다. 실무적으로 barrier CMP 에서 BTA 는
**Ta 를 억제하지 않고 Cu 만 억제해 선택비를 만드는 용도**로 쓴다.
즉 **BTA × Ta 의 ΔG_ads 는 "작아서 아무도 안 쟀다"가 실체일 가능성이 높다.**
이것 자체가 모델링에 쓸 수 있는 정보다(3절 하단 참조).

---

## 3. 미확보 절 — 시도한 검색 전량 기록

다음 작업자가 같은 길을 다시 걷지 않도록 실제 실행한 질의를 그대로 남긴다.

**사용한 인덱스/API**
- Crossref REST (`query.bibliographic`) — 6회
- OpenAlex (`search`, `filter=fulltext.search`, `filter=title_and_abstract.search`) — 14회
- Europe PMC (`resultType=core`, 불리언 질의) — 5회
- Semantic Scholar Graph API — 대부분 HTTP 429 로 차단됨(1회만 성공)
- 웹 검색(ddgs/exa 폴백) — 9회
- 브라우저: **Chrome 미기동으로 사용 불가** (`chrome-not-running`). Google Scholar·ScienceDirect 직접 열람 못 함.
- `web_extract`: 백엔드가 ddgs(검색 전용)라 **URL 본문 추출 기능이 비활성**. ScienceDirect 본문 접근 실패.

**실제 질의 문자열**
- `benzenesulfonic acid copper corrosion inhibitor adsorption free energy`
- `benzenesulfonic acid copper adsorption free energy Langmuir kJ/mol`
- `"benzenesulfonic acid" copper "free energy of adsorption" Langmuir inhibitor`
- `benzenesulfonic acid inhibition copper`
- `benzenesulfonate copper adsorption DFT`
- `sodium dodecylbenzenesulfonate copper adsorption free energy corrosion`
- `dodecylbenzene sulfonate copper corrosion inhibition adsorption isotherm`
- `"benzenesulfonic" AND "corrosion inhibitor"` (Europe PMC)
- `"benzene sulfonic acid" copper CMP inhibitor removal rate adsorption mechanism`
- `malonic acid tungsten adsorption isotherm EIS corrosion inhibitor`
- `malonic acid tungsten corrosion inhibitor adsorption`
- `malonic acid tungsten polishing passivation adsorption`
- `malonic acid tungsten chemical mechanical polishing inhibitor`
- `"malonic acid" AND "tungsten" AND "adsorption"` (Europe PMC)
- `tungsten corrosion inhibitor adsorption isotherm free energy` / `... Langmuir kJ`
- `"tungsten" AND "Langmuir" AND "free energy of adsorption" AND "inhibitor"` (Europe PMC)
- `benzotriazole tantalum nitride adsorption corrosion`
- `benzotriazole tantalum adsorption free energy`
- `benzotriazole TaN chemical mechanical polishing inhibition`
- `tantalum benzotriazole corrosion inhibition barrier CMP adsorption`
- `Ta TaN barrier CMP corrosion inhibitor adsorption isotherm free energy`
- `"benzotriazole" AND "tantalum"` (Europe PMC)

**훑은 저널/코퍼스**
Corrosion Science, Corrosion (NACE), Electrochimica Acta, J. Colloid Interface Sci., Langmuir,
ECS JSS / J. Electrochem. Soc. / ECS Trans., Microelectronic Engineering, Applied Surface Science,
Materials Transactions, MRS Proceedings, MDPI(Materials/Molecules/Coatings/Lubricants),
Scientific Reports, RSC Advances, npj Materials Degradation, Int. J. Electrochem. Sci.,
J. Serb./Chil. Chem. Soc., Europe PMC 전체.

**왜 못 찾았는가 (원인별)**
1. **benzenesulfonic × Cu** — 논문 자체가 존재하지 않는 것으로 보인다. 설폰산은 강산 해리 음이온이라
   전통적 유기 억제제 스크리닝 대상(N/S 헤테로원자 보유 분자)에서 제외돼 있다.
   검색으로 나오는 것은 전부 설폰**아마이드**이거나 **알킬**벤젠설포네이트 계면활성제다.
2. **malonic acid × W** — 유일 후보 1차 문헌(`10.1557/proc-477-115`)의 초록을 확보해 확인한 결과
   **주제 자체가 다르다**(말론산 × 알루미나 입자의 제타전위 / 입자오염 저감). ΔG_ads 없음 확정.
   말론산은 W-CMP 에서 억제제가 아니라 분산제·착화제로 쓰이므로,
   "말론산 × W 억제 쌍"이라는 전제 자체를 재검토해야 한다.
   → 다음 작업자는 이 DOI 재추적 금지. 대신 `10.1016/j.jcis.2023.04.012`(BTC × W, Langmuir)를
   먼저 열어 **W 기질에서 Langmuir ΔG 를 어떻게 쟀는지 방법론만** 가져와라.
3. **BTA × Ta/TaN** — 물리적으로 측정 동기가 없다(Ta₂O₅ 부동태막이 BTA 결합 사이트를 안 준다).
   문헌 부재가 곧 "약한 흡착"의 간접 증거일 수 있으나, **간접 증거로 수치를 만들지는 않았다.**

**환경 차단 사항 (다음 세션에서 먼저 풀 것)**
- 브라우저 백엔드: Chrome 미기동 → 페이월 우회·Scholar 검색 전면 불가.
- `web.extract_backend` 가 ddgs 로 설정돼 URL 본문 추출 불가 → firecrawl/tavily/exa 중 하나로 교체 필요.
- Semantic Scholar API 무키 상태로 429 빈발 → API 키 설정 권장.
- **`tools/find_open_access.py` 가 깨져 있다 (SyntaxError).** 169행 `미러 사이트_MIRRORS = ...` —
  변수명에 공백이 들어간 한글 식별자라 파이썬이 파싱하지 못한다(179행 `def 미러 사이트(doi):` 도 동일).
  이 도구는 **현재 전혀 실행되지 않는다.** 페이월 폴백 경로가 통째로 죽어 있다는 뜻이다.
  → 다음 작업자는 문헌 조사 전에 이 파일부터 고쳐라(식별자를 `MIRROR_SITES`/`mirror_site` 등으로 치환).
이 넷 중 **하나만 풀려도** 유료 논문 본문 확보 가능성이 크게 오른다.

---

## 4. 대체 경로

### 4-1. 부등식 경계 (값 대입 금지, 경계만)

**benzenesulfonic acid × Cu**
- 같은 Cu 기질·같은 Langmuir·같은 전기화학법으로 측정된 **방향족 설포닐기 보유 분자**의 실측 대역:
  sulfathiazole/Cu = −33.47 kJ/mol (0.1 M NaCl). 이 분자는 티아졸 N 과 아민 N 을 추가로 갖는다.
- 따라서 흡착점이 −SO₃⁻ 산소뿐인 benzenesulfonate 는 **|ΔG| 가 더 작아야 한다**:

      |ΔG_ads(benzenesulfonic × Cu)| < |ΔG_ads(sulfathiazole × Cu)| = 33.47 kJ/mol

- 하한은 물리흡착 하단으로만 제약한다. 2-MBT × Cu = −5.59 kJ/mol 선례가 있으므로
  **−5 kJ/mol 수준의 매우 약한 값도 기각하지 말 것.**

      −34 kJ/mol  <  ΔG_ads(benzenesulfonic × Cu)  <  ~0

  → 이 구간은 너무 넓다. **모델 파라미터로 쓰기에 부적합하다. 반드시 측정하거나 계산해야 한다.**

**BTA × Ta/TaN**
- BTA × Cu = −30.02, BTA × Fe = −21.89, BTA × Cu-Ni = −22.093 (모두 기확보).
- Ta 는 표면이 Ta₂O₅ 산화물이라 금속 d-밴드 배위가 불가하다. 따라서

      |ΔG_ads(BTA × Ta/TaN)| << |ΔG_ads(BTA × Cu)| = 30.02 kJ/mol

  이 부등식은 barrier CMP 에서 BTA 가 Cu/Ta 선택비를 만든다는 공정 사실과 일관된다.
  **수치는 넣지 말고, 모델에서는 "Ta 에 대해 BTA 억제항 ≈ 0" 이라는 경계 조건으로만 쓰라.**
  (이것은 값 추정이 아니라 선택비라는 실측 현상의 직접 반영이다. 주석에 근거를 반드시 남길 것.)

**malonic acid × W** — 경계를 세울 재료가 없다. Ni/dihydrazide 값은 분자·기질 둘 다 달라 무효.
**아무 경계도 제시하지 않는다.**

### 4-2. 측정 명세 (직접 재는 경로)

세 쌍 모두 동일 프로토콜로 잴 수 있다. 참고 템플릿은 W 기질 선례
(benzethonium chloride × W, `10.1016/j.jcis.2023.04.012`).

**장비**
- 포텐시오스탯 (EIS: 100 kHz–10 mHz, 진폭 10 mV rms; PDP: ±250 mV vs OCP, 1 mV/s)
- 3전극 셀: 작업전극 = 연마된 Cu / W / TaN 블랭킷 웨이퍼 쿠폰(1 cm²),
  기준 = Ag/AgCl(sat. KCl), 상대 = Pt 메시
- 보조: EQCM (Au 코팅 AT-cut 결정 위 Cu/W/Ta 스퍼터, 질량 변화 직접 측정 → 다층 판정에 필수)
- 표면 확인: XPS (S 2p / N 1s 피크로 흡착 화학종 확인), 접촉각

**조건 (CMP 실조성에 맞출 것 — 부식 문헌의 1 M HCl 을 그대로 쓰면 CMP 와 무관해진다)**
- benzenesulfonic × Cu: pH 2–4 (US9200180B2 조성 재현), H₂O₂ 1 wt%, 25 °C,
  억제제 농도 5점 이상 (0.1–3 wt%, 몰농도로 환산해 기록)
- malonic × W: pH 2–6, Fe(NO₃)₃ 또는 H₂O₂ 산화제 포함/미포함 2세트, 25 °C
- BTA × TaN: pH 4 및 pH 10 두 점 (Ta₂O₅ 등전점 ~2.9 를 사이에 두고)
- 각 조건 3반복, 온도 25/35/45 °C 로 확장하면 ΔH_ads·ΔS_ads 까지 분리 가능

**플롯과 계산 순서**
1. EIS 의 R_ct 로 θ = 1 − R_ct(0)/R_ct(C) 산출 (PDP 의 i_corr 비로 교차검증)
2. C/θ vs C 직선성 확인 — **단, 이것만으로 단분자층을 주장하지 말 것.**
3. **다층 판별을 먼저 하라**: EQCM 질량이 포화하지 않고 농도에 따라 계속 증가하면 다층이다.
   다층이면 Langmuir 절편에서 나오는 값을 **ΔG₁(첫층)** 으로만 기록하고 BET 로 재피팅한다.
4. K = 1/절편 (C 단위는 mol/L 로 통일 — g/L 로 두면 K 단위가 L/g 가 되어 ΔG 가 어긋난다)
5. **ΔG = −RT·ln(55.34·K)** — 물 몰농도 인자를 반드시 포함하고, 문서에 인자 포함 사실을 명시한다.
   (이 인자 누락 시 ΔG 가 약 +9.9 kJ/mol 만큼 어긋난다.)
6. Langmuir 외에 Frumkin·Temkin 도 함께 피팅해 R² 를 비교 기록한다.

**검증 게이트**: 얻은 ΔG 로 억제율을 역예측해 실측 MRR(US9200180B2 의 Cu 6.4 nm/min)을
±30% 안에서 재현하는지 확인한다. 재현 못 하면 억제 기구가 흡착이 아니라는 신호다(2-1 해석 참조).

### 4-3. DFT 계산 경로

문헌·측정 둘 다 막혔을 때의 최후 경로. **계산값은 반드시 `dft` 등급으로 별도 표기하고
실측 ΔG 와 같은 칸에 넣지 마라** (진공/암시적 용매 DFT 의 E_ads 는 수용액 ΔG_ads 가 아니다).

- **수준**: 주기적 평면파 DFT. VASP 또는 Quantum ESPRESSO, PBE + Grimme D3(BJ) 분산 보정.
  컷오프 400–500 eV, k-점 4×4×1 이상.
- **슬래브**:
  - Cu(111) 4–5 층, 하단 2층 고정, 진공 15 Å. p(4×4) 이상 셀(흡착질 상호작용 억제).
  - W(110) 또는 표면 산화 반영 시 WO₃(001) 슬래브.
  - TaN(100) 또는 현실 반영을 위한 비정질 Ta₂O₅ 슬래브 — TaN 금속 표면만 계산하면
    실제 부동태막과 다른 답이 나온다. 이 점을 반드시 문서화할 것.
- **흡착질 상태**: benzenesulfonic 은 CMP pH 에서 해리형(C₆H₅SO₃⁻)로 계산해야 한다.
  중성 분자로 계산하면 실조성과 무관한 값이 된다. 전하 보정(Makov-Payne 등) 필요.
- **용매화**: VASPsol 또는 암시적 용매 + 명시적 물 1–2층. 진공 계산만으로 끝내지 말 것.
- **ΔG 환산**: E_ads → ΔG 는 진동 자유에너지(ZPE, −TΔS_vib)와 물 치환 항
  (Inh(sol) + xH₂O(ads) → Inh(ads) + xH₂O(sol)) 을 명시적으로 포함해야 실측과 비교 가능하다.
  이 환산 절차를 생략한 E_ads 는 실측 ΔG 와 수십 kJ/mol 차이가 난다.

---

## 5. `sim/inhibitor_pairs.py` 에 대한 권고

- 이번 조사 결과로 **새로 등록할 쌍은 없다.** 값 없이 등록하지 마라.
- benzenesulfonic × Cu 는 표에 **"미확보(pending), 출처 없음"** 상태로 명시적 자리를 만들어 두는 편이 낫다.
  현재는 표에 없어서 모델이 억제=0 으로 간주하고 620 nm/min 급을 예측한다.
  **"모른다"와 "억제가 없다"를 코드 수준에서 구분**해야 100배 오차가 침묵하지 않는다.
  (예: `dG=None, status="unmeasured"` → MRR 예측 시 신뢰도 캡을 걸거나 예측 거부)
- BTA × Ta/TaN 은 수치 대신 **"barrier 선택비 근거의 정성 경계(억제항 ≈ 0)"** 로만 반영하고
  근거 주석을 남긴다.

---

## 6. 기계 검증 — "미확보"가 코드에서도 미확보인가

이 노트의 유일한 정량 주장은 **"이 세 쌍은 표에 없다"** 이다. 서술로 남기면
다음 회차가 확인할 방법이 없으므로, 아래 블록이 실제로 조회해 확인한다.
(값을 지어내 등록하면 이 assert 가 깨진다 — 그것이 의도다.)

```python verify
import sys, pathlib
sys.path.insert(0, str(pathlib.Path("sim").resolve().parent))
from sim.inhibitor_pairs import lookup_dG, measurement_spec, K_from_dG

PENDING = [("benzenesulfonic acid", "Cu"), ("malonic acid", "W"),
           ("benzotriazole", "Ta"), ("benzotriazole", "TaN")]

# (1) 세 쌍 모두 미등록 — 유사 분자/유사 기질 값으로 대체되지 않았다
for inh, sub in PENDING:
    assert lookup_dG(inh, sub) is None, f"{inh}x{sub} 가 근거 없이 등록됐다"

# (2) 미등록 쌍은 침묵하지 않고 R8 측정 명세를 발행한다
for inh, sub in PENDING:
    spec = measurement_spec(inh, sub)
    assert spec and any("R8" in s for s in spec), f"{inh}x{sub} 측정명세 없음"

# (3) 환산식 검산: ΔG = -40 kJ/mol → K = exp(40000/RT)/55.34
import math
K = K_from_dG(-40.0)
expected = math.exp(40000.0 / (8.314462618 * 298.15)) / 55.34
assert abs(K - expected) / expected < 1e-9, (K, expected)
# 물 몰농도 인자를 빼면 55.34 배 커진다 — 노트 §5 서술의 수치 확인
assert abs(K * 55.34 - math.exp(40000.0 / (8.314462618 * 298.15))) / \
       math.exp(40000.0 / (8.314462618 * 298.15)) < 1e-9
print("PASS: 4쌍 미등록 확인 · R8 명세 발행 확인 · K 환산 재현")
```
