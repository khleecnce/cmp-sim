<!-- V2-SECTION: R2-slurry | 근거: oxidizer, Kaufman, passivation, Langmuir-Hinshelwood, Fenton, 산화제 | 정본: ARCHITECTURE-V2.md §3 -->
# χ 산화제 농도 곡선 지수 oxidizer_curve_n — Langmuir-Hinshelwood 자기차단 유도 + Lim(2013) 실측 대조

> Max워커 | 작성일: 2026-09-14
> 선행: [[w-cmp-wo3-passivation-oxidizer-kaufman]] [[w-cmp-fenton-catalyst-abrasive-alumina-silica]]
> [[oxidizer-redox-potential-decomposition-metal-suitability]] [[cu-electrochemistry-pourbaix-bta-oxidizer-inhibitor]]
> 대상: `sim/tier2_physics/slurry_components.py::mrr_oxidizer` 의 형상지수 `n` —
> `knowledge/params/cu_h2o2_bta.yaml`·`knowledge/params/w_fe_oxidizer.yaml`의 `oxidizer_curve_n`.

## 1. 질문

`mrr_oxidizer(C, C_peak, mrr_peak, n) = mrr_peak·(n+1)x / (1 + n·x^((n+1)/n))`, `x=C/C_peak`
는 산화제 농도에 대해 단봉(Kaufman 경쟁) 곡선을 낸다. `n`은 정점 이후 감소의 완만도다.
현재 `cu_h2o2_bta.yaml`은 n=2.0(confidence=**unverified**, 주석 자체가 "현상론 형상
파라미터, 미검증"이라고 자백), `w_fe_oxidizer.yaml`은 n=3.0(confidence=**estimated**,
출처는 **US20110186542A1** — KPS(과황산칼륨)+H₂O₂+다이아몬드 연마입자 W CMP 특허, 15조건
격자적합). 이 값들을 반응속도론에서 닫힌 형태로 유도할 수 있는가? 유도가 값을 못 주면
n을 그대로 두고 그 사실을 기록한다(EVIDENCE-RULES §4 원칙).

## 2. 1차 출처

- **Kaufman et al. (1991)**, "Chemical-Mechanical Polishing for Fabricating Patterned W Metal
  Features as Chip Interconnects," *J. Electrochem. Soc.* 138(11), 3460. DOI: 10.1149/1.2085434
  — 원문 PDF 확보·직접 판독(`papers/kaufman1991-w-cmp-mechanism.pdf`, pdfplumber 텍스트화
  `papers/kaufman1991-w-cmp-mechanism.pdf.txt`). **§7 확인: 원문은 이 농도 범위에서 "polish
  rates are proportional to the concentration of chemical constituents"라고만 말한다 —
  즉 Kaufman 자신은 정점-감소 곡선의 지수를 준 적이 없다.** 단봉 형태 자체는 이 논문의
  화학(WO₃ 부동태)+기계(연마) 경쟁 메커니즘에서 나온 codebase의 해석이지, Kaufman이 실측한
  닫힌 형태가 아니다 — 이 사실 자체가 정직성 기록 대상이다(§6).
- **Lim, Park, Park (2013)**, "Effect of iron(III) nitrate concentration on tungsten
  chemical-mechanical-planarization performance," *Appl. Surf. Sci.* 282, 512–517.
  DOI: 10.1016/j.apsusc.2013.06.003 (원문 PDF 확보·직접 판독, `papers/lim2013-apsusc-fe-nitrate-w-cmp.pdf`
  → `papers/lim2013-apsusc-fe-nitrate-w-cmp.pdf.txt`. 조건: 1.0 wt% H₂O₂ 고정, pH 2.3,
  6 psi, 70 rpm, 4 wt% 콜로이달 실리카, Fe(NO₃)₃ 농도만 스윕).
  **⚠ 파일 확인 결과 `papers/lee2013-fe-nitrate-w-cmp.pdf`는 이 파일과 바이트 단위로 완전히
  동일하다(`diff` 무출력)** — 별개 논문이 아니라 Lim 2013의 중복 사본이다. "Lee 2013"이라는
  독립 출처는 존재하지 않는다(과제 지시문의 papers 목록 오류로 판단, §6에 기록).
- **Buxton, Greenstock, Helman, Ross (1988)**, "Critical Review of Rate Constants for Reactions
  of Hydrated Electrons, Hydrogen Atoms and Hydroxyl Radicals," *J. Phys. Chem. Ref. Data* 17,
  513. DOI: 10.1063/1.555805 (원문 PDF 확보, `papers/buxton1988-hydroxyl-radical-rate-constants.pdf`)
  — [[w-cmp-fenton-catalyst-abrasive-alumina-silica]] §2.2가 이미 직접 판독한 반응85·159의
  속도상수(k(•OH+Fe²⁺)=4.3×10⁸, k(•OH+H₂O₂)=2.7×10⁷ M⁻¹s⁻¹)를 그대로 재사용한다(중복 판독 회피).
- **Ein-Eli, Abelev, Starosvetsky (2004; received 2003)**, "Electrochemical aspects of copper
  chemical mechanical planarization (CMP) in peroxide based slurries containing BTA and glycine,"
  *Electrochimica Acta* 49, 1499–1503. DOI: 10.1016/j.electacta.2003.11.010 (원문 PDF 확보·직접
  판독, `papers/aksu2003-electrochimica-bta-glycine-cu-cmp.pdf`). **본문 확인: 이 논문 자신의
  실측이 아니라 refs [3,5],[9,10]을 인용한 서술** — "dissolution rate...found only once the
  peroxide concentration was in the region of 1–3%. Further increase...resulted in reduction
  of dissolution rate [3,5]" (2차 인용, E5). 정량 곡선 없음.
- **Tamilmani (2005)**, UA 학위논문(hdl 10150/280774, 이미 확보·`[[cu-electrochemistry-pourbaix-bta-oxidizer-inhibitor]]`의
  1차 출처) §2.2.2.2가 **Du et al.**(JES 151, G230, 2004)을 2차 인용: "copper CMP removal rate
  reaches a maximum at 1% H₂O₂...decreases...At low peroxide concentrations, removal controlled
  by electrochemical dissolution; at high peroxide levels...controlled by mechanical removal of
  copper oxide and its subsequent dissolution." **정량 수치 없음, 2차 인용(E5).** Du et al. 2004
  원문은 이번 회차에도 미확보(§6).
- **Kremer (1962)**, "The Promoting Effect of Cupric Ions on the Ferric Ion Catalyzed
  Decomposition of Hydrogen Peroxide," *J. Catal.* 1, 351–355. DOI: 10.1016/0021-9517(62)90063-5
  (원문 PDF 확보, `papers/kremer1962-cu-fe-h2o2-decomposition.pdf`). Fe³⁺ 촉매 H₂O₂ 분해가
  [H₂O₂]/[Fe³⁺] 비(R)가 클 때(R>10) 1차 반응이고 R이 작으면 비정상상태로 전이함을 보인다 —
  Cu²⁺는 이 전이점을 이동시키는 촉진제. **W/Fe 계의 정성적 지지(포화형 성장 동역학의 일반적
  존재)로만 쓴다, Cu CMP의 정량 곡선은 없다.**
- **⚠ `papers/kim2020-wo3-passivation-oxidizers.pdf`는 손상/오배치 파일이다.** pdfplumber로
  전문 추출한 결과(`papers/kim2020-wo3-passivation-oxidizers.pdf.txt`) 내용이 WO₃·산화제와
  전혀 무관한 **1990년대 JACC 심장초음파 학회 초록집**이다(예: "Intracardiac Echocardiographic
  Quantification of Atrial Wall Thickness..."). 이 파일은 이번 유도에 **전혀 사용하지 않았다** —
  과제 지시문이 가리킨 자료가 실제로는 존재하지 않는다는 뜻이므로 그대로 기록한다.

## 3. 유도

### 3.1 경쟁의 뼈대
산화제 농도 C가 만드는 순 제거플럭스는 두 과정의 곱이다:
`flux(C) = (생성: C↑ → 반응층/라디컬 공급↑) × (가용성: C↑ → 표면이 보호되어 반응 가능면적↓)`.
정점은 두 factor의 곱이 최대가 되는 지점이다 — 이것이 과제가 요구한 (a)/(b) 경쟁의 수학적 뼈대다.

### 3.2 가장 단순한 닫힌 형태 — Langmuir 흡착 자기차단 (단일 사이트)
표면 반응 사이트 밀도를 1로 정규화하고, 산화제(또는 그 반응중간체)의 Langmuir 흡착
피복률을 `θ(C) = KC/(1+KC)`라 하자(단일 사이트, 경쟁 흡착 없음 — 가장 단순한 L-H 가정).
반응이 "흡착된 산화제 하나 + 인접한 미반응(노출) 사이트 하나"를 필요로 하는 이중자리
기구(가장 흔한 L-H 단분자 표면반응 형태)라면 순 반응속도는
`r(C) ∝ θ(C)·(1-θ(C)) = KC/(1+KC)^2`.
`x=KC`로 무차원화하면 `r(x) = x/(1+x)^2`, 정규화(정점=1)하면 **`g_LH(x) = 4x/(1+x)^2`**.

`dr/dx=0` 조건에서 KC=1(x=1)에 정점(값 1/4, 정규화 후 1.0)이 있고, x→∞에서
`g_LH(x) → 4/x` — **점근 지수 −1**. `mrr_oxidizer`의 점근 형태(§3.3)와 비교하면 이는
`n=1`에 대응한다 — **이것이 이 유도가 주는 가장 단순한 이론적 하한값이다.**

### 3.3 mrr_oxidizer의 점근 꼬리와 n의 의미
`mrr_oxidizer(x)=(n+1)x/(1+n x^{(n+1)/n})`에서 x≫1일 때 분모가 `n x^{(n+1)/n}`에 지배되므로
`mrr_oxidizer(x) → (n+1)/n · x^{-1/n}`. 즉 **n은 "정점 이후 감소가 x^(-1/n)으로 얼마나
완만한가"를 직접 정하는 점근 지수의 역수다.** n=1 → x^-1(가파름), n이 클수록 완만.

### 3.4 왜 단순 L-H 하한(n=1)이 실제보다 가파른가 — 다층/점진적 부동태화
§3.2의 모델은 **단분자층, on/off 이진 차단**을 가정한다. 그러나 Lim(2013) SEM/AFM/XPS
관찰(§4)은 WO₃ 형성이 이진적이지 않고 **점진적으로 치밀해지는 다층 과정**임을 보여준다
(region I: "reduced porous structure", region II: "dense WO₃ layer" — 밀도가 연속적으로
증가). 다층·점진 차단은 같은 방향(농도↑→가용 사이트↓)이지만 **더 완만하게** 접근한다 —
전형적으로 `θ^m·(1-θ)` 류(m>1, 다중 흡착층/직렬 확산장벽)나 Cabrera-Mott형 로그 성장(자기
제한이 지수함수적으로 느려짐)이 이 완만화를 만든다. 이 코드베이스가 가진 문헌들은 W나 Cu
어느 쪽에서도 **다층 차단의 지수(m)나 확산장벽 상수를 독립적으로 주지 않는다** — 따라서
이 방향의 보정을 닫힌 형태로 더 유도할 수는 없다(과제 지시의 "유도가 값을 못 주면 억지로
숫자를 만들지 마라" 조건에 해당). 대신 **실측 곡선의 꼬리 기울기를 직접 재는 것**으로
n을 정한다 — §4.

### 3.5 Fenton 라디컬 경쟁(w_fe_oxidizer 전용 보강 — 정성)
[[w-cmp-fenton-catalyst-abrasive-alumina-silica]] §2.2가 이미 Buxton(1988) 속도상수로
확인한 대로, `•OH + Fe²⁺`(k=4.3×10⁸)가 `•OH + H₂O₂`(k=2.7×10⁷)보다 ~16배 빠르다 — Fe
과잉투입은 스스로 만든 라디컬을 도로 삼킨다(자기소거). 이는 §3.4의 "다층 부동태" 메커니즘과
**독립적인 두 번째 감소 경로**이며, 둘 다 같은 방향(C↑ → 순생산 라디컬/노출면적↓)이므로
W 계의 감소가 Cu(자기소거 촉매가 없는 계, §5.2)보다 더 가파를 이유는 없다 — 오히려 두 경로가
겹치므로 **W가 Cu보다 완만하지 않을 근거는 없다**(같은 차수이거나 W가 더 가파를 잠재적 이유는
있지만, 데이터가 반대로 나온다 — §4·§6에서 정직하게 기록).

## 4. 정량 대조 — Lim(2013) Fig.1 실측 vs 유도

Lim(2013)은 W CMP **정지식각률(SER, 기계작용 없는 순수 화학용해)**과 **연마율(MRR, 기계+화학)**을
Fe(NO₃)₃ 농도(1.0 wt% H₂O₂ 고정)의 함수로 **둘 다** 보고한다 — 이것이 이 유도에서 가장 중요한
사실이다.

| C (Fe(NO₃)₃ wt%) | MRR (Å/min) | SER (Å/min) |
|---|---|---|
| 0 | 56.0 | 37.8 |
| 0.01 | 923.0 | **85.9 (최대)** |
| 0.05 | 1177.0 | 31.1 |
| 0.1 | (region II, "slight" 증가) | 19.3 |
| 0.5 | — | 15.8 |
| 1.0 | — | 12.3 |

단위 환산(1 Å = 0.1 nm): SER 최댓값은 85.9 Å/min = **8.59 nm/min**(0.01 wt%) → 1.0 wt%에서
1.23 nm/min으로 감소한다 (Lim 2013, Fig.1 — 위 §4 표). §7 블록2가 이 5점을 로그-로그 회귀로 재현해 문헌값 85.9 Å/min·12.3 Å/min 과 대조한다.

**MRR은 이 범위(0→1.0 wt%)에서 단조 증가·포화만 보이고 정점을 넘지 않는다**(XPS WO₃ 함량도
같은 포화 트렌드 — region II에서 saturated). **SER은 진짜 단봉이다**: 0.01 wt%에서 최댓값
85.9 Å/min을 찍고 이후 단조 감소해 1.0 wt%에서 12.3(=최댓값의 14%, C=0 기준선 37.8보다도
낮다 — 순수 화학용해가 부동태로 기준선 아래까지 눌린다는 뜻). 이는 §3의 경쟁 구조가 **실제로
관측된다는 직접 증거**이지만, **관측되는 관측량이 MRR이 아니라 SER**이라는 프록시 전이가
있다 — §6에서 이 한계를 명시한다.

SER 감소구간(0.01~1.0 wt%, 5점)의 로그-로그 회귀로 점근 지수를 추출하면(§7 블록2):
**기울기 = −0.398, R²=0.908 → n_fit ≈ 2.52.** 이는 §3.2의 이론적 하한 n=1보다 2.5배
완만하다 — §3.4에서 예견한 방향(다층 부동태가 단순 이진 차단보다 완만함)과 **부호가 일치**한다.

## 5. 결론

### 5.1 w_fe_oxidizer — n: 3.0 → **2.5**, confidence: estimated(유지)
근거 서열 판정(EVIDENCE-RULES #19, §7 표): 기존 n=3.0의 출처(US20110186542A1, KPS+H₂O₂+
다이아몬드 W CMP 특허)는 **Fe가 전혀 없는 화학**(과제·팩이 선언한 "Fe계 산화제"와 오히려
불일치)에서 얻은 값으로 **E4/E5급**(계 불일치 전이)이다. 새 값(n≈2.5)은 **Lim(2013)** —
실제 Fe(NO₃)₃/H₂O₂/W CMP 계의 1차 실측 — 에서 얻었으므로 계 근접도가 명백히 높다(**E3**:
대상계 실측이지만 관측량이 SER이지 MRR이 아니라는 교란이 있음). E3 > E4/E5이므로 1단계에서
새 값 채택. **confidence는 literature로 올리지 않는다** — 이유 셋: (i) SER→MRR 프록시 전이가
검증되지 않았다(§3.4·§6), (ii) 로그-로그 적합 R²=0.908로 판정#12(R²=0.997) 수준의 타이트함에
못 미친다, (iii) 이 값이 걸려 있는 `_pack_conf` 그룹의 형제 키 `oxidizer_peak_wt_pct`
(=6.0 wt%, 같은 KPS+다이아몬드 특허의 외삽값)도 여전히 estimated이므로 — n만 literature로
올려도 χ/w_fe_oxidizer 칸의 confidence는 `oxidizer_peak_wt_pct`에 의해 estimated로 눌린다
(피크 위치를 재보정할 Fe(NO₃)₃-H₂O₂ 계 H₂O₂ 스윕 데이터는 이번 회차에 확보하지 못했다 — §6).

### 5.2 cu_h2o2_bta — n: 2.0 **값 유지**, confidence: unverified → **estimated**
Cu 계는 §3.2의 이론적 하한(n=1)만 확보했고, 정량 실측 곡선은 **끝내 미확보**다(§6, 시도
3건 전부 차단). 하한(n=1)과 W 계에서 관측된 보정비(n_fit/n_theory ≈ 2.5, §4)를 함께 보면
`n ∈ [1, ~3]` 범위가 물리적으로 방어 가능하며, 기존 값 n=2.0은 이 범위 **안에** 있다 —
**바꿀 근거도 없고 틀렸다는 근거도 없다.** 그러나 기존 확신도 "unverified"는 "이 값에 대해
어떤 추론도 한 적 없다"는 뜻이었고, 이제는 이론적 하한 + 교차계 보정 범위라는 **실제 추론이
붙었으므로** unverified(추론 없음)에서 estimated(추론 있음, 정량 실측 없음)로는 올린다.
**literature로는 올리지 않는다** — §3.2/§3.4는 Cu 자체의 실측으로 검증된 적이 없고(§4의
교차대조는 W 데이터), Aksu(2003)·Tamilmani(2005)/Du(2004)는 전부 2차 인용(E5)이라 정량
값을 주지 못한다.

### 5.3 결과적으로 격자는 움직이지 않을 수 있다 — 정직하게 명시
`sim/factors.py::_f_chi`의 confidence는 `_pack_conf(oxidizer_curve_n, oxidizer_peak_wt_pct,
ph_peak, ceria_tooth_gain)`의 **최약값**이다. cu_h2o2_bta는 `oxidizer_curve_n`
estimated→**여전히 estimated**(literature 문턱 미달), w_fe_oxidizer는 `oxidizer_peak_wt_pct`가
이미 estimated로 잡혀 있어 n을 아무리 올려도 그 형제 키에 막힌다. **두 칸 모두 C2(confidence
미달)에서 벗어나지 못할 가능성이 높다** — `tools/completion.py check`의 실측 결과를 그대로
보고한다(§8). 이것은 "근거가 딱 그만큼"이라는 뜻이지 작업 실패가 아니다.

## 6. 한계·미검증 항목 (정직 표기)

1. **species-axis 불일치**: `w_fe_oxidizer.yaml`의 `oxidizer_wt_pct`/`oxidizer_peak_wt_pct`는
   주석상 **H₂O₂** 농도(출처: KPS+다이아몬드 특허)인데, 이 노트가 n을 재보정한 Lim(2013)
   데이터는 **Fe(NO₃)₃** 농도 스윕(H₂O₂는 1.0 wt% 고정)이다. 두 축은 물리적으로 다른
   화학종이다. 과제 지시문 자체가 "Lim 2013 Fig.1이 n을 정량 대조할 수 있는 유일한 실측
   곡선"이라 명시했으므로 이 노트는 **형상지수 n(정점의 뾰족함이라는 무차원 성질)이 화학종
   축과 독립적으로 같은 부동태-경쟁 메커니즘을 반영한다**는 가정 하에 전이했다 — 이 가정은
   검증되지 않았다. `oxidizer_peak_wt_pct`(피크 **위치**)는 화학종에 종속적이므로 전이하지
   않고 그대로 뒀다.
2. **SER≠MRR 프록시**: n_fit=2.52는 정지식각(화학만)에서 얻었다. `oxidizer_curve_n`이
   실제로 곱해지는 것은 기계+화학 MRR이다. Lim(2013)의 MRR 자체는 이 농도범위에서 정점을
   넘지 않아(포화만 관측) 직접 대조가 불가능했다 — §3.5의 정성 논증(같은 방향의 경쟁,
   과잉투입 라디컬 자기소거)으로 전이를 정당화했을 뿐 정량 검증은 아니다.
3. **다층 부동태 지수 m 미확보**: §3.4에서 예견한 `θ^m(1-θ)` 류 보정의 m을 독립적으로 줄
   문헌(WO₃ 두께의 시간/농도 분해능 데이터)을 찾지 못했다 — `papers/kim2020-wo3-passivation-oxidizers.pdf`가
   손상 파일이었고(§2), `papers/lee2013-fe-nitrate-w-cmp.pdf`는 Lim(2013)의 중복이었다.
   과제가 지정한 1차 자료 6편 중 실질적으로 2편(Kaufman 1991, Lim 2013)만 유효했다.
4. **Cu 정량 곡선 탐색 3건 실패**: (a) Lu/Nogami "Effect of H2O2 in Citric Acid Based Copper
   Slurry on Cu Polishing" (DOI:10.1149/1.2393015, IOP) — `find_open_access.py`가 IOP
   publisher PDF를 찾았으나 curl 응답이 HTML(봇 차단), 미러 사이트 미러도 캡차("로봇 확인")
   로 차단. (b) "Effects of hydrogen peroxide and alumina on surface characteristics of
   copper CMP in citric acid slurries" (DOI:10.1016/j.matchemphys.2004.06.007, Elsevier) —
   ScienceDirect 직접 차단, 미러 사이트/st 무응답, 미러 사이트 캡차. (c) "Effect of H2O2 on
   Frictional and Thermal Behaviors in Citric Acid-Based Cu CMP" (DOI:10.1143/jjap.47.5385,
   IOP) — 동일하게 HTML 캡차. EVIDENCE-RULES §3회차 규칙에 따라 이번 회차는 여기서 종결한다
   (다음 회차 재시도 대상으로 남김).
5. **§3.2 L-H 모델과 mrr_oxidizer(n=1) 형태는 점근꼬리 지수만 일치, 전 구간 일치 아님**:
   §7 블록1에서 확인하듯 x∈[0.1,10] 구간 최대 상대편차 40%(x=0.1·10에서 0.60배). n=1이
   "이론적으로 가장 뾰족한 하한"이라는 정성적 결론은 유효하나, mrr_oxidizer 함수족이 L-H
   θ(1-θ)의 정확한 재모수화는 아니다.
6. **Kremer(1962)는 배경 정황일 뿐**: Cu²⁺가 Fe³⁺ 촉매 H₂O₂ 분해의 1차→비정상상태 전이를
   촉진한다는 것은 "성장동역학이 포화형에서 벗어날 수 있다"는 일반적 지지일 뿐, Cu CMP
   제거율 곡선 자체의 수치를 주지 않는다.

## 7. 코드 재현 (verify)

```python verify
# 블록1: L-H 단일사이트 자기차단(theta*(1-theta))의 닫힌 형태와 mrr_oxidizer(n=1) 비교
import math

def mrr_oxidizer(C, C_peak, mrr_peak, n):
    x = C / C_peak
    return mrr_peak * ((n + 1.0) * x) / (1.0 + n * x ** ((n + 1.0) / n))

def lh_normalized(x):
    # theta=Kc/(1+Kc), x=Kc.  theta*(1-theta) = x/(1+x)^2, 정점(x=1)에서 1/4 -> *4 정규화
    return 4.0 * x / (1.0 + x) ** 2

# 정점 위치·값
assert abs(lh_normalized(1.0) - 1.0) < 1e-12, "L-H 정규화형은 x=1에서 정확히 1.0이어야 함"
for x in (0.9, 1.1):
    assert lh_normalized(x) < lh_normalized(1.0), f"x={x}에서 정점보다 커지면 안 됨(단봉 위반)"
print("L-H theta*(1-theta): x=1(KC=1)에서 정점=1.0 확인 (단봉)")

# 점근 꼬리: L-H -> 4/x (지수 -1), mrr_oxidizer(n=1) -> 2/x (지수 -1, 동일 점근지수)
# log(g(x_big)/g(x_big/10)) / log(10) 은 '10배 커질 때 g가 몇 제곱으로 줄어드는가' = -지수.
x_big = 1e6
lh_tail_exp = math.log(lh_normalized(x_big) / lh_normalized(x_big / 10)) / math.log(10.0)
mo_tail_exp = math.log(mrr_oxidizer(x_big, 1.0, 1.0, 1.0) / mrr_oxidizer(x_big / 10, 1.0, 1.0, 1.0)) / math.log(10.0)
print(f"점근 지수: L-H={lh_tail_exp:.4f}, mrr_oxidizer(n=1)={mo_tail_exp:.4f} (둘 다 -1 -> n=1 대응)")
assert abs(lh_tail_exp - (-1.0)) < 1e-3
assert abs(mo_tail_exp - (-1.0)) < 1e-3

# 전 구간 형태 비교 (점근지수는 같지만 전 구간 동일하지 않음 -> 최대 상대편차 정직 기록)
max_dev = 0.0
for x in (0.1, 0.2, 0.5, 1.0, 2.0, 5.0, 10.0):
    r = mrr_oxidizer(x, 1.0, 1.0, 1.0) / lh_normalized(x)
    max_dev = max(max_dev, abs(r - 1.0))
print(f"mrr_oxidizer(n=1) vs L-H 전 구간 최대 상대편차 = {max_dev:.1%}")
assert 0.3 < max_dev < 0.5, "두 함수족은 '같은 점근지수, 다른 전구간 형태' -> 40%대여야 정직한 기록"
print("=> n=1은 '가장 뾰족한 이론적 하한'의 점근 지수로만 유효, 전구간 재모수화는 아님 (한계 §6.5)")
```

```python verify
# 블록2: Lim(2013) Fig.1 SER(정지식각) 실측 — 로그-로그 회귀로 점근지수 n_fit 추출
import math

data = [(0.01, 85.9), (0.05, 31.1), (0.1, 19.3), (0.5, 15.8), (1.0, 12.3)]  # Fe(NO3)3 wt%, SER A/min
xs = [math.log(c) for c, _ in data]
ys = [math.log(v) for _, v in data]
n = len(xs)
mx, my = sum(xs) / n, sum(ys) / n
cov = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
varx = sum((x - mx) ** 2 for x in xs)
slope = cov / varx
intercept = my - slope * mx
ss_res = sum((y - (slope * x + intercept)) ** 2 for x, y in zip(xs, ys))
ss_tot = sum((y - my) ** 2 for y in ys)
r2 = 1 - ss_res / ss_tot
n_fit = -1.0 / slope

print(f"log(SER) = {intercept:.3f} + {slope:.4f}*log(C)  ->  n_fit = -1/slope = {n_fit:.3f}, R^2={r2:.4f}")
assert 2.0 < n_fit < 3.0, f"n_fit={n_fit:.2f} — 문헌 SER 감소구간 재현이 기대범위(2~3) 밖"
assert r2 > 0.85, f"R^2={r2:.3f} — 5점 로그-로그 적합의 최소 신뢰선(0.85) 미달"

# SER은 region I(<=0.01wt%)에서 최댓값을 찍은 뒤 단조감소 -> 최댓값이 곧 정점
ser_vals = [v for _, v in data]
assert ser_vals[0] == max(ser_vals), "관측 최댓값이 C=0.01wt%(표의 첫 점)이어야 함(문헌 서술과 일치)"
assert all(ser_vals[i] > ser_vals[i + 1] for i in range(1, len(ser_vals) - 1)), \
    "0.01wt% 이후로는 단조감소해야 SER '진짜 단봉' 주장이 성립"
print(f"SER 최댓값 {ser_vals[0]} A/min @ 0.01wt% 이후 단조감소 확인 (문헌: region I/II 서술과 정합)")

# n_fit이 L-H 이론 하한(n=1) 대비 몇 배 완만한지
correction = n_fit / 1.0
print(f"보정비 n_fit/n_theory(=1) = {correction:.2f}배 -> §3.4 예견(다층 부동태가 단순 L-H보다 완만)과 부호 일치")
assert correction > 1.5, "다층 부동태 보정이 방향대로면 n_fit이 이론하한보다 뚜렷이 커야 함"
```

```python verify
# 블록3: 결론값 대입 — w_fe(n=2.5)·cu(n=2.0, 이론 하한~교차계 보정 범위 안) 최종 점검
import math

def mrr_oxidizer(C, C_peak, mrr_peak, n):
    x = C / C_peak
    return mrr_peak * ((n + 1.0) * x) / (1.0 + n * x ** ((n + 1.0) / n))

n_w_new, n_w_old = 2.5, 3.0
n_cu = 2.0
n_theory_floor = 1.0
n_fit_w_from_SER = 2.515276489881437

# w_fe: 새 값이 SER 적합값(2.52)에 반올림 오차 수준으로 근접해야 함(채택 근거)
assert abs(n_w_new - n_fit_w_from_SER) < 0.1, "채택값 2.5가 SER 적합 n_fit과 가까워야 함"
print(f"w_fe_oxidizer.oxidizer_curve_n: {n_w_old} -> {n_w_new} (Lim2013 SER 적합 {n_fit_w_from_SER:.2f}에서 반올림)")

# cu: 이론 하한(1.0)과 W 교차계 보정(약 2.5배)이 만드는 방어 가능 범위 [1, ~3] 안에 있는가
lower, upper = n_theory_floor, n_theory_floor * (n_fit_w_from_SER / n_theory_floor)
assert lower <= n_cu <= upper * 1.3, f"cu n={n_cu} — 이론하한~교차계보정 범위[{lower:.1f},{upper*1.3:.1f}] 밖이면 변경 검토 대상"
print(f"cu_h2o2_bta.oxidizer_curve_n: {n_cu} (변경 없음) — 방어범위 [{lower:.1f}, {upper*1.3:.1f}] 안")

# 두 값이 정점 위치·형태에서 실제로 만드는 차이를 정량으로 보여준다 (정점 대비 2배 농도에서)
for label, n_ in (("w_fe(구 n=3.0)", 3.0), ("w_fe(신 n=2.5)", 2.5), ("cu(n=2.0)", 2.0)):
    v = mrr_oxidizer(2.0, 1.0, 1.0, n_)
    print(f"  {label}: 정점 대비 2배 농도에서 배수 = {v:.3f}")
print("=> n이 작을수록(신 w_fe) 정점 이후 감소가 가팔라 과잉투입 페널티가 더 크게 잡힌다")
```
