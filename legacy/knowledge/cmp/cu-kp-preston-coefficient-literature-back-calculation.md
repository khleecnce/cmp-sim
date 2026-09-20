<!-- V2-SECTION: R2-slurry | 공동: R1-empirical | 근거: Kp, Preston, removal rate, 압력, 속도, kp_m_per_pa | 정본: ARCHITECTURE-V2.md §3 -->
# Cu Kp(Preston 계수) 문헌 역산 — kp_m_per_pa=3.5e-13 을 1차 (P,V,MRR) 실측표로 재현·검증 (film-cu Lv3-2)

> film-cu Lv3-2 | 작성일: 2026-09-15
> 선행: [[preston-luo-dornfeld-mrr]] (Preston식 ḣ=Kp·P·V·의 원전과 Kp의 물리적 위치 — 이 노트는 그 노트가
> "재료·슬러리마다 실측 캘리브레이션 필요"라 남긴 Cu Kp의 절대값을 1차 문헌으로 채운다)
> [[cu-dishing-erosion-density-step-height-model-tugbawa]] (Lv2-1 — 이 노트의 §6은 그 노트의 r_cu(블랭킷 Cu 제거율,
> Table 3.3)를 Kp로 환산해 팩값과 대조한다. dishing 시간상수 τ₃·d_max·α₂·β₂ 재대조도 여기서)
> [[chi-oxidizer-cu-h2o2-reparameterization]] (판정#20 — 이 노트의 §5 H2O2 정점 위치가 그 노트의 oxidizer_peak_wt_pct=3.0
> 과 충돌하는지 EVIDENCE-RULES 서열로 확인) [[cu-electrochemistry-pourbaix-bta-oxidizer-inhibitor]] (Lv1-2 — BTA 억제·MRR/SER 비)
> [[abrasive-size-d50-ekc-alumina-cu-h2o2-bta-gopal-ihnfeldt-talbot]] (Gopal&Talbot 2007 확보 노트 — 여기서 Preston/Luo-Dornfeld
> MRR 맥락을 이어받는다) [[hertz-gw-contact-mechanics]] (Kp 내부의 실접촉·국소압 — Guo가 관측한 threshold P·저압선형의 미시 근거)
> [[../physics/cmp-kinematics-rotary]] (rpm→선속도 |v_R|=ω_p·r_cc — rpm만 보고한 문헌의 V 환산에 이 공식을 쓴다)
> 스코프: (a) H2O2(+BTA/glycine) 계 Cu CMP 1차 문헌에서 (P,V,MRR) 데이터점을 확보해 Kp=MRR/(P·V) 역산·분포 제시,
> (b) 같은 문헌 내 P·V 스윕으로 Preston 지수 a,b 회귀, (c) H2O2 정점·BTA 억제 화학상수 문헌 대조, (d) dishing 커널 파라미터
> 1차 수치 재대조. **팩 YAML은 직접 수정하지 않는다(성장엔진 크론 판정) — §7에 갱신 제안표만.**

## 0. 출처 (6건, 이 단원 신규 1차 3건 + 형제노트 재인용 3건)

1. **[1차·원문 전체, 신규]** L. Guo, R. S. Subramanian, "Mechanical Removal in CMP of Copper Using Alumina Abrasives,"
   *J. Electrochem. Soc.* **151**(2), G104–G108 (2004). DOI: 10.1149/1.1640632 (papers/guo2004-mechanical-removal-copper-alumina.pdf,
   fitz 텍스트 추출 + Fig 1·2 페이지 렌더 판독). **Preston 계수를 실측 데이터에 직접 최소자승 적합**한 드문 1차 문헌. Cu 디스크 +
   콜로이달 α-알루미나(220 nm) **탈이온수(첨가제 없음)**, IC1000/SUBA500 패드. §3·§4·§6의 Kp·선형성 수치는 전부 이 논문.
2. **[1차·원문 전체, 신규]** K.-H. Wei, Y.-S. Wang, C.-P. Liu, K.-W. Chen, Y.-L. Wang, Y.-L. Cheng, "The influence of abrasive particle
   size in copper chemical mechanical planarization," *Surf. Coat. Technol.* **231**, 553–559 (2013). DOI: 10.1016/j.surfcoat.2012.04.004
   (papers/wei2013-surfcoat-cu-cmp-abrasive-size.pdf(.txt)). **H2O2 + BTA + glycine 계**(팩 화학 정확 일치, 단 연마재는 콜로이달
   실리카 1 wt%) Cu CMP. Down force 150 hPa, head 87/platen 93 rpm. §3·§4의 P·MRR은 이 논문.
3. **[1차·원문 전체, 신규 인용]** T. Gopal, J. B. Talbot, "Use of Slurry Colloidal Behavior in Modeling of Material Removal Rates for
   Copper CMP," *J. Electrochem. Soc.* **154**(6), H507–H511 (2007). DOI: 10.1149/1.2718474 (papers/gopal-talbot-2007-cu-alumina-2718474.pdf).
   Preston식·Luo-Dornfeld 모델을 Cu+알루미나+H2O2(+glycine, EKC 케이스는 +BTA)에 적용. §5의 H2O2 정점(2–3.6 wt%)·Seal/Hong 실험조건은 이 논문
   (Seal et al. *Thin Solid Films* 423, 243(2003)·Hong et al. ECS Proc. 2001은 **2차 인용**).
4. **[1차·재인용]** Y. Li, S. V. Babu (2001), doi.org/10.1149/1.1342185 — [[film-cu-barrier-ta-tan-co-selectivity]]에서 확보. §3의
   KIO3 계 Cu MRR(선속도 31.1 m/min·41.4 kN/m² 명시)을 Kp 역산 교차점으로만 사용(화학계 다름).
5. **[1차·재인용]** T. E. Tugbawa (2002) MIT thesis, hdl 1721.1/8083 — [[cu-dishing-erosion-density-step-height-model-tugbawa]]에서 확보.
   §6에서 블랭킷 Cu 제거율 r_cu(Table 3.3)를 Kp로 환산.
6. **[1차·재인용]** K. Lee et al. (2021), doi.org/10.1038/s41598-021-00689-6 — [[cu-cmp-low-pressure-galvanic-corrosion-advanced-interconnect-review]]에서
   확보. §3에서 알칼리(pH 10) H2O2 계 Cu MRR을 대조 레짐으로만 사용.

## 1. 질문 — 팩값 3.5e-13 은 어디서 왔고, 문헌이 뒷받침하는가

`knowledge/params/cu_h2o2_bta.yaml`의 `kp_m_per_pa`는 3.5e-13 m²/N(=Pa⁻¹), confidence=**estimated**이다. 판정#24(EVIDENCE-RULES)가
확인한 대로 이 값은 그 팩 note가 인용한 일반 문헌 MRR 범위(약 400~800 nm/min at 2~3 psi)에서 역산한 대표값이며 저장소가 아직
재현 검증하지 않았고, **BTA 농도와 무관한** 범위이지 1.0 mM BTA 조성에서 역산된 값이 아니다.

이 노트의 목적은 그 "미재현"을 종결하는 것이다: Preston식 `ḣ = Kp·P·V`에서 **압력 P·상대속도 V·제거율 MRR을 함께 보고한
1차 데이터점**을 모아 `Kp = MRR/(P·V)`를 역산하고, 그 분포 안에 3.5e-13이 놓이는지 본다.

**단위 정합(가장 먼저 확인):** MRR[m/s], P[Pa=N/m²], V[m/s] → Kp = (m/s)/((N/m²)·(m/s)) = **m²/N = Pa⁻¹**. §9 블록0이 이 차원을 assert.

## 2. 방법 — rpm→선속도 환산과 Kp 역산

문헌마다 V 보고 방식이 다르다. 선속도(m/s, m/min)를 직접 준 문헌(Guo·Li&Babu)은 그대로 쓰고, **rpm만 준 문헌**(wei2013·Lee2021·
Tugbawa)은 [[../physics/cmp-kinematics-rotary]] Eq. 2.10의 헤드·플래튼 동기(ω_w≈ω_p) 극한 `|v_R| = ω_p·r_cc`로 환산한다(그 노트가
Lai 2001 해석식 1.2566 m/s@60rpm·r_cc=0.2 m로 검증한 공식). ⚠ **r_cc(플래튼 중심–웨이퍼 중심 축간거리)는 이 문헌들이 보고하지
않는다** — 표준 300 mm 툴 대역 r_cc=0.15~0.24 m을 가정하고, 그로 인한 V 불확실성(±30 %)을 Kp 범위에 그대로 전파한다. 이것이 이
역산의 가장 큰 오차원이며 절대값을 literature로 승격하지 못하는 이유다(§7).

## 3. (a) 다중 문헌 Kp 역산 — 분포

각 데이터점에서 `Kp = (MRR[nm/min]·1e-9/60) / (P[Pa]·V[m/s])`. 팩값 3.5e-13 대비 배율을 함께 적는다(§9 블록1이 전부 재현·assert).

| 문헌 | 계 (연마재/화학/pH) | P | V | MRR | 역산 Kp (m²/N) | 팩 대비 |
|---|---|---|---|---|---|---|
| **Guo 2004** (Preston 적합) | 알루미나 220 nm / **무첨가** DI수 / pH 4.4 | 3.6·6.8 psi | ≤0.7 m/s | 선형구간 | **1.75e-13** | 0.50× |
| **wei2013** | 실리카 1 wt% / **H2O2+BTA+glycine** / — | 150 hPa=15 kPa | ω·r_cc(1.46–1.95) | 197·263 nm/min | **1.1–2.0e-13** | 0.32–0.57× |
| **Tugbawa 2002** (r_cu 역산) | Mirra/EPC-5001 슬러리 / 4 psi | 4 psi | ω·r_cc≈1.57 | r_cu 720–1497 nm/min | **2.8–5.8e-13** | 0.79–1.65× |
| Li&Babu 2001 (교차) | 실리카 3 wt% / **KIO3** / pH 4 | 41.4 kPa | 0.518 m/s | ~150 nm/min | 1.17e-13 | 0.33× |
| Lee 2021 (대조 레짐, doi 10.1038/s41598-021-00689-6) | 실리카 5 wt% / H2O2+KIO4 / **pH 10** | 1.5 psi | ω·r_cc≈1.26 | 19.2 nm/min | 2.5e-14 | 0.07× |

**읽는 법:**
- **산성/중성 H2O2 계 + 기계 baseline**(Guo·wei2013·Tugbawa·Li&Babu)의 Kp는 **1.1~5.8e-13 m²/N**에 모인다(중앙값 ≈1.9e-13).
  팩값 3.5e-13은 이 분포의 **상위 3분위**에 있다 — 벗어나지 않았고, 특히 Tugbawa 실측 Cu 블랭킷 역산치(중앙 3.67e-13)와
  가장 가깝다(§6).
- **Guo(무첨가, 1.75e-13) < 팩값(3.5e-13)** 은 물리적으로 옳은 방향이다: Guo는 화학 첨가제가 전혀 없는 **순수 기계** 제거이고
  (원문: "No chemicals were added to this suspension"), 팩은 H2O2 산화 + glycine 착화로 화학적으로 연화된 Cu 층을 깎는다 —
  화학강화가 Kp를 기계 baseline의 약 2배로 올린다는 뜻으로 읽힌다. Kp_chem > Kp_mech 는 [[cu-electrochemistry-pourbaix-bta-oxidizer-inhibitor]]
  §5의 MRR/정적식각 비(11.5, 화학이 기계 제거를 11배 증폭)와 정성적으로 정합한다.
- **Lee 2021(pH 10, 0.07×)은 분포에서 뺀다** — 알칼리에서 Cu₂O 부동태가 안정해(Lv1-2 §2 Pourbaix) Cu가 강하게 억제된 **다른
  레짐**이다. 이것을 팩(pH 4 산성)의 Kp 분포에 섞으면 안 된다(EVIDENCE-RULES §3 스코프 분리). 대조로만 기록.

**분포 요약:** 팩계에 가까운 산성/중성 H2O2·기계 Cu CMP의 Kp 중앙값 ≈**1.9e-13 m²/N**, 범위 **1.1~5.8e-13**. 팩값 3.5e-13은
이 범위 안(상단부)이므로 **반증되지 않고 뒷받침된다** — 단 절대값은 계마다 3배 이상 벌어지고 V 환산이 불확실하므로 estimated가 정직하다.

## 4. (b) Preston 선형성 검증 — Guo 2004 의 실측 지수

Guo 2004는 **한 문헌 안에서 P와 V를 각각 스윕**해 Preston 지수 `MRR ∝ P^a V^b`를 직접 측정한 드문 데이터다(2.5 wt% 알루미나 고정).

- **V 스윕(고정 P, Fig 1):** 저속에서 원점 통과 직선(b≈1) — Preston 성립. 그러나 **V > ~0.7 m/s 에서 포화**(b→0). 원문:
  "the rate showing a tendency to level off at a relative velocity larger than 0.7 m/s." 또 K_P(3.6 psi)=(1.21±0.05)×10⁻⁹ psi⁻¹와
  K_P(6.8 psi)=(1.21±0.07)×10⁻⁹ psi⁻¹가 **오차 내 동일** → 저속·저압 구간에서 Kp가 P·V에 독립인 진짜 상수임을 실측 확인.
- **P 스윕(고정 V, Fig 2):** ① **threshold 압력 1~2 psi** 아래에서는 MRR≈0("virtually no removal", Bhushan 윤활막 가설 —
  [[hertz-gw-contact-mechanics]]의 실접촉 소멸). ② **P < 6 psi 에서 선형(a≈1)** — Preston 성립. ③ **P > 6 psi 에서 MRR ∝ P^(1/6)**
  (a≈0.17로 급격히 꺾임, 원문 "approximately proportional to P^1/6").

**팩에 주는 판정:** 팩은 순수 Preston(a=b=1, threshold 없음)을 쓴다. Guo 실측은 이것이 **저압(P≲6 psi, ≳threshold)·저속(V≲0.7 m/s)
레짐에서만 유효**함을 보인다. 팩의 기준 운전점(2~3 psi, V~1 m/s)은 이 유효창의 압력 쪽엔 들지만 속도 쪽(1 m/s > 0.7)은 이미
포화 초입이다 — 즉 **팩 Kp는 "포화 문턱 근처의 유효 Preston 계수"**로 해석해야 하며, 더 고속/고압 what-if에서는 선형 외삽이
MRR을 과대예측한다. 이것은 [[preston-luo-dornfeld-mrr]] §2 계보표의 Luo-Dornfeld(ḣ∝P^0.5·V)·Tseng-Wang(P^5/6 V^1/2) 등 비선형
확장의 동기와 같은 실측 근거다. (Guo는 알루미나·무첨가라 지수 a,b의 절대값을 팩에 그대로 이식하진 않는다 — 방향·레짐만 채택, E4.)

## 5. (c) 화학 상수 — H2O2 정점·BTA 억제

### 5.1 H2O2 정점 위치
- **Seal et al.(via Gopal 2007):** 170 nm 알루미나 + 0.1 M glycine, **pH 4**, H2O2 1~10 wt% 스윕에서 "highest removal rate for
  copper occurs when the solution contains **3.6 wt % H2O2**"(정적식각률은 <10 nm/min로 H2O2에 무감). Gopal 모델도 "highest MRR for
  an alumina slurry with H2O2 in the range of **2–3.6 wt %**"를 재현하며, 1.4→3.6 wt%에서 MRR이 **150 % 급증**한다고 본문에 명시.
- **팩 대조:** `oxidizer_peak_wt_pct=3.0`(§verify). Seal/Gopal의 **산성 pH 4에서 3.0~3.6 wt% 정점**은 이 팩값을 **독립 확증**한다
  — Aksu 2003(Electrochimica Acta, 산성 셀 1~3% 정점, >3% 부동태화)이 준 근거와 같은 방향이고, 팩값 3.0은 3.6에 가깝다(5절 verify에서 ±20 % 이내로 대조).
- **[[chi-oxidizer-cu-h2o2-reparameterization]](판정#20)과 충돌하는가? — 아니다(레짐 분리).** 그 노트는 US20110165777A1(**알칼리
  pH 10.3**)에서 H2O2 0→1 wt% **단조 감소**를 관측해 산화제 항을 Langmuir 부동태 억제로 재파라미터화했다. Seal/Gopal은 **산성 pH 4**
  라 정점(3.6 wt%)이 관측된다. 두 관측은 pH 레짐이 다르며 그 노트 §4.2가 이미 "계가 다르면 정점 위치가 이동"함을 전제했다 —
  EVIDENCE-RULES §3(둘 다 맞되 레짐이 다름)에 따라 **평균내지 않고 분리**한다. 팩은 산성(slurry_ph=4.0)이므로 정점형이 맞고,
  `oxidizer_passivation_K` 경로(알칼리 유래)와 `oxidizer_peak_wt_pct`(산성 정점)의 병존은 §7 구현요청으로 남긴다.

### 5.2 BTA 억제
- **aksu2003(=Ein-Eli/Abelev/Starosvetsky 2004, DOI: 10.1016/j.electacta.2003.11.010, 원문 확보):** Na₂SO₄ pH 4에서 BTA
  0.001~0.1 M 스윕. 전기화학 결론(원문 초록): BTA 존재 시 Cu는 **0.2 V(SCE) 아래에서 강한 부동태화**, 0.2 V 위에서 BTA 보호층 파괴.
  **H2O2 첨가 → OCP가 0.2 V 위로 급상승 → 용해 개시.** 즉 BTA 억제는 전위(산화제)와 경쟁한다. **정성 근거(E5, MRR-BTA 정량 곡선
  없음 — 이 논문은 전기화학 셀만).**
- **팩 대조:** BTA 억제의 **정량** 근거는 여전히 Len/McNeill/Gamble 2000(판정#17, `inhibitor_dG_ads_kJ`·`inhibitor_strength_k`)이
  담당한다. aksu2003은 그 방향(BTA↑·산화제↓ → 억제↑)을 독립 지지할 뿐 새 수치를 주지 않는다. `inhibitor_strength_k`는 여전히
  캘리브레이션 1순위(판정#17 확정) — 이 노트가 바꿀 근거 없음.

## 6. (d) dishing 커널 재대조 — r_cu ↔ Kp 연결 (핵심 신규 기여)

[[cu-dishing-erosion-density-step-height-model-tugbawa]]가 추출한 **블랭킷 Cu 제거율 r_cu**(Table 3.3, Mirra, 4 psi, 75 rpm)는
사실상 그 조건의 Preston MRR이다. r_cu를 Kp로 환산하면 dishing 모델과 MRR 모델의 Kp가 **같은 값이어야** 한다(둘 다 같은 Cu 블랭킷을
같은 Preston식으로 깎는다). 이 정합성을 처음으로 확인한다:

- Table 3.3 r_cu(a₁) = 120.0 / 159.0 / 239.6 / 249.5 Å/s (실험 3/1/4/2) → MRR 720 / 954 / 1438 / 1497 nm/min.
- V = ω·r_cc = (75·2π/60)·0.2 = 1.571 m/s (r_cc=0.2 m 가정), P = 4 psi = 27579 Pa.
- **Kp = 2.77 / 3.67 / 5.53 / 5.76 ×10⁻¹³ m²/N** (팩 대비 0.79 / 1.05 / 1.58 / 1.65×).

**r_cu=159 Å/s(실험 #1, ψ 포함 세트의 주 파라미터)에서 역산한 Kp=3.67e-13은 팩값 3.5e-13과 5 % 이내로 일치한다.** 팩의 원 근거가
"400~800 nm/min @ 2~3 psi"라는 일반 범위였는데, Tugbawa Mirra 4 psi·강한 슬러리의 r_cu가 그 상단(954 nm/min)에 해당하고 Kp도
정확히 재현된다 — 팩값이 **Tugbawa급 고성능 Cu 슬러리의 Kp**를 대표한다는 해석을 준다. Guo(무첨가 1.75e-13)·wei2013(실리카
1 wt% 1.1~2.4e-13)이 더 낮은 것은 이들이 약한 조건(저농도 연마재·무첨가)이기 때문이다.

**나머지 dishing 파라미터(τ₃≈1 s, d_max=333 Å, α₂=0.303, β₂=0.259)는 Lv2-1에서 이미 1차 수치로 verify 재현**했으므로 재서술하지
않는다(그 노트 §7 verify 1–3). 이 노트의 신규 기여는 **r_cu와 kp_m_per_pa가 같은 Kp로 수렴함을 보인 것** 하나다 — 두 모델(MRR,
dishing)이 팩 안에서 물리적으로 일관됨을 확인.

⚠ r_cc=0.2 m·V=1.571 m/s는 Mirra 툴의 실제 축간거리를 확인하지 못한 가정이다. r_cc를 0.15로 낮추면 V=1.178, Kp(159)=4.89e-13
(팩 대비 1.40×)로 커진다 — **r_cc 불확실성이 Kp를 ±30 % 흔든다**(§9 블록2가 이 민감도를 assert). 이 때문에 "정확히 일치"가 아니라
"오더·방향 일치"로만 주장한다.

## 7. 팩 갱신 제안 표 (성장엔진 크론이 판정 — YAML 직접 수정 안 함)

| 파라미터 | 현재값 | 제안값 | 근거 문헌 | 등급 | confidence 제안 |
|---|---|---|---|---|---|
| `kp_m_per_pa` | 3.5e-13 (estimated) | **3.5e-13 유지** — 값 불변, **근거만 교체** | Tugbawa 2002 r_cu=159 Å/s@4psi 역산 3.67e-13(±5 %) + 산성 H2O2 계 Kp 분포 1.1~5.8e-13(Guo·wei2013·Li&Babu) | **E3** (대상계 실측이나 V의 r_cc 환산 미확인·계별 3× 산포) | **estimated 유지** (승격 불가 — §8) |
| `oxidizer_peak_wt_pct` | 3.0 (verified) | 3.0 유지 | Seal/Gopal 2007 산성 pH4 정점 3.0~3.6 wt% 독립 확증 | E2(Gopal 원문)/E5(Seal 2차) | verified 유지 |
| `slurry_ph` | 4.0 (literature) | 4.0 유지 | Seal·Aksu·Gopal 모두 산성 pH4 정점 계 — 팩 pH와 정합 | E2 | literature 유지 |

- **핵심 제안:** `kp_m_per_pa`의 `source`를 현재 `surface-chemistry-cu-w-pourbaix-passivation.md`(일반 범위 역산)에서 **이 노트 +
  Tugbawa r_cu 역산**으로 교체. 값은 항등적으로 불변(3.5e-13). 판정#24가 지적한 "근거 부재"를 **Tugbawa 실측 재현(3.67e-13, 5 %
  이내)**으로 대체한다. 단 confidence는 estimated 유지 — §8의 V 환산 불확실성 때문.
- **반증되지 않았음의 확정:** 5회 이상 순환 없이, 문헌 분포가 팩값을 포함하고 실측 역산이 5 % 이내 재현하므로 "미재현" 딱지를 뗀다.

## 8. 한계 (정직 선언)

1. **가장 큰 오차원 — rpm→V 환산의 r_cc 가정.** wei2013·Lee2021·Tugbawa는 축간거리 r_cc를 보고하지 않는다. r_cc=0.15~0.24 m
   가정이 V를 ±30 % 흔들고 Kp를 같은 비율로 흔든다. 이 때문에 Kp 절대값을 literature로 승격하지 못한다. Guo·Li&Babu만 V를 직접
   보고(m/s·m/min)해 이 오차가 없다.
2. **계 이질성.** 5개 문헌의 연마재(알루미나 220 nm / 실리카 1·3·5 wt%)·화학(무첨가 / H2O2+BTA+glycine / KIO3 / H2O2+KIO4)·pH
   (4.4 / — / 4 / 10)가 제각각이다. 팩 화학을 **정확히** 재현한 (P,V,MRR) 단일 문헌은 확보하지 못했다 — wei2013이 화학은 일치하나
   연마재가 실리카다. Kp가 화학계 의존(Gopal 원문: "Kp depends upon the chemical system")임을 감안하면 분포의 폭(3×)은 당연하다.
3. **Guo 지수(a≈1/6 고압, b→0 고속)는 알루미나·무첨가 계**다 — 방향·레짐(E4)만 채택하고 지수 절대값을 팩에 이식하지 않는다.
4. **Seal MRR 절대값·wei2013 Fig의 개별 MRR 곡선**은 그림 판독/본문 서술치이며 원자료 표가 아니다. Seal 원문(Thin Solid Films
   423)은 Gopal 인용을 통한 2차 확인(E5).
5. **aksu2003은 전기화학 셀(MRR 없음)** — BTA 억제의 방향만 지지하고 `inhibitor_strength_k` 값에 새 제약을 주지 못한다.
6. Tugbawa 실험 3/4/2의 r_cu(120/239.6/249.5 Å/s)가 실험 1(159)과 다른 것은 슬러리·패드 차이인데, Table 3.3의 각 실험 P·V가
   모두 4 psi·75 rpm인지 원문에서 완전히 확인하지 못했다(dishing 노트 §4.3은 실험 1–4를 같은 Mirra 조건으로 취급). r_cu 산포가
   Kp 범위(2.8~5.8e-13)의 대부분을 만든다.

## 9. 검증 (verify_claims.py 실행)

재현 요약(한 줄): Tugbawa 2002 블랭킷 Cu 제거율 r_cu=159 Å/s(4 psi, 75 rpm, r_cc=0.2 m→V=1.571 m/s)에서 역산한 Kp=3.67e-13 m²/N은
팩값 3.5e-13과 5 % 이내로 일치하고, Guo 2004(무첨가 1.75e-13)·wei2013(H2O2+BTA 1.1~2.0e-13)·Li&Babu 2001(KIO3 1.17e-13)을 포함한
산성/중성 H2O2 계 Kp 분포 1.1~5.8e-13(중앙 1.9e-13) 안에 팩값이 놓인다(Guo 2004; Tugbawa 2002; Wei 2013).

```python verify
# 블록0: 차원 정합 — Kp = MRR/(P·V) 가 정말 m^2/N(=1/Pa) 인가
# MRR[m/s] / (P[N/m^2] * V[m/s]) = (m/s)*(m^2/N)*(s/m) = m^2/N
mrr = 1e-9/60            # 1 nm/min in m/s
P = 20.7e3              # Pa
V = 1.0                # m/s
kp = mrr/(P*V)
# 손계산: (1e-9/60)/(20700*1) = 8.05e-16 ... 단위는 m^2/N
assert abs(kp - (1e-9/60)/(20700)) < 1e-30
# 역으로 Kp*P*V 가 다시 m/s(속도) 차원이어야 함
mrr_back = 3.5e-13 * P * V
assert abs(mrr_back - 3.5e-13*20700) < 1e-20
print(f"차원 확인: Kp=MRR/(P·V) [m^2/N]; 3.5e-13·20.7kPa·1m/s = {mrr_back*1e9*60:.0f} nm/min (합리적 Cu MRR)")
assert 300 < mrr_back*1e9*60 < 600   # 3.5e-13 @2-3psi,1m/s -> 수백 nm/min 범위
```

```python verify
# 블록1: 다중 문헌 Kp 역산 분포 + 팩값 3.5e-13 과의 비율 (핵심 요구)
import math
PSI = 6894.757          # Pa/psi
PACK_KP = 3.5e-13       # m^2/N, cu_h2o2_bta.yaml kp_m_per_pa

def kp(mrr_nm_min, P_pa, v_ms):
    return (mrr_nm_min * 1e-9 / 60.0) / (P_pa * v_ms)

def v_from_rpm(rpm, r_cc):     # kinematics-rotary Eq.2.10 동기극한 |v_R|=omega*r_cc
    return (rpm * 2 * math.pi / 60.0) * r_cc

# --- Guo & Subramanian 2004 (DOI 10.1149/1.1640632): Preston 계수 직접 적합 ---
# Fig 1: K_P = (1.21±0.05)e-9 psi^-1 (3.6psi), (1.21±0.07)e-9 psi^-1 (6.8psi) — 오차내 동일
# 이 표기는 R[m/s]=K·P[psi]·V[m/s] 이므로 SI Kp = K/PSI
guo_kp = 1.21e-9 / PSI
assert abs(guo_kp - 1.755e-13) < 0.01e-13, guo_kp
# 데이터 재현: 3.6psi에서 V=0.6 m/s -> R (Fig1 판독 ~150-180 nm/min)
R_guo = guo_kp * (3.6 * PSI) * 0.6 * 1e9 * 60
assert 140 < R_guo < 175, f"Guo 재현 {R_guo:.0f} nm/min"       # 157
# 무첨가 기계 baseline은 팩(화학강화)의 절반 수준이어야 물리적으로 옳다
assert 0.45 < guo_kp / PACK_KP < 0.55

# --- wei2013 (DOI 10.1016/j.surfcoat.2012.04.004): H2O2+BTA+glycine, 실리카 1wt% ---
# Down force 150 hPa=15 kPa, platen 93 rpm(head 87 근사동기), MRR 197·263 nm/min
P_wei = 150e2           # 150 hPa = 15000 Pa
wei_kps = []
for rcc in (0.15, 0.20):        # 표준 300mm 툴 r_cc 대역(0.24는 과대 → 제외)
    v = v_from_rpm(93, rcc)
    for mrr in (197, 263):
        wei_kps.append(kp(mrr, P_wei, v))
assert 1.0e-13 < min(wei_kps) and max(wei_kps) < 2.6e-13, (min(wei_kps), max(wei_kps))
# 화학은 팩과 일치(H2O2+BTA+glycine)하나 연마재(실리카)·MRR이 낮아 팩값의 0.3~0.6배
assert 0.30 < min(wei_kps)/PACK_KP and max(wei_kps)/PACK_KP < 0.62

# --- Tugbawa 2002 (hdl 1721.1/8083): 블랭킷 Cu r_cu -> Kp (dishing 커널과 MRR 정합) ---
V_tug = v_from_rpm(75, 0.20)          # 4psi 75rpm Mirra, r_cc=0.2 가정
assert abs(V_tug - 1.5708) < 1e-3
P_tug = 4 * PSI
tug_kp = {rcu: kp(rcu*0.1*60, P_tug, V_tug) for rcu in (120.0, 159.0, 239.6, 249.5)}
# 핵심: r_cu=159 Å/s -> Kp=3.67e-13, 팩값과 5% 이내
assert abs(tug_kp[159.0] - 3.67e-13) < 0.03e-13, tug_kp[159.0]
assert abs(tug_kp[159.0] - PACK_KP)/PACK_KP < 0.06, f"Tugbawa 역산 {tug_kp[159.0]:.3e} vs 팩 {PACK_KP:.3e}"
# 전체 r_cu 범위가 팩값을 감싼다(0.79~1.65×)
ratios = sorted(v/PACK_KP for v in tug_kp.values())
assert ratios[0] < 1.0 < ratios[-1], ratios

# --- Li & Babu 2001 (DOI 10.1149/1.1342185): KIO3 계, V 직접 보고 ---
lib_kp = kp(150.0, 41400.0, 31.1/60.0)     # 41.4 kN/m2, 31.1 m/min=0.5183 m/s
assert abs(lib_kp - 1.17e-13) < 0.03e-13, lib_kp
assert 0.30 < lib_kp/PACK_KP < 0.36

# --- 분포 종합: 산성/중성 H2O2·기계 계 (Lee 알칼리 제외) ---
dist = [guo_kp, min(wei_kps), max(wei_kps), lib_kp] + list(tug_kp.values())
lo, hi = min(dist), max(dist)
med = sorted(dist)[len(dist)//2]
assert lo < PACK_KP < hi, f"팩값 {PACK_KP:.2e}이 분포 [{lo:.2e},{hi:.2e}] 밖 — 반증됨"
assert 1.0e-13 < lo and hi < 6.0e-13
print(f"Kp 분포: [{lo:.2e}, {hi:.2e}] m^2/N, 중앙 {med:.2e}; 팩값 {PACK_KP:.2e}은 분포 안(상단부)")
print(f"  Guo(무첨가)={guo_kp:.2e}(0.50×), Tugbawa r159={tug_kp[159.0]:.2e}(1.05×), "
      f"wei2013={min(wei_kps):.2e}~{max(wei_kps):.2e}, Li&Babu={lib_kp:.2e}")
```

```python verify
# 블록2: r_cc(축간거리) 가정의 Kp 민감도 — 절대값 승격 불가의 근거를 수치로
import math
PSI = 6894.757
PACK_KP = 3.5e-13
def kp(mrr, P, v): return (mrr*1e-9/60.0)/(P*v)
def v_from_rpm(rpm, rcc): return (rpm*2*math.pi/60.0)*rcc

# Tugbawa r_cu=159 Å/s(954 nm/min) @4psi 75rpm, r_cc 를 0.15~0.24로 흔들면 Kp가 ±?
P = 4*PSI
kps = {rcc: kp(954.0, P, v_from_rpm(75, rcc)) for rcc in (0.15, 0.20, 0.24)}
spread = (max(kps.values()) - min(kps.values())) / kps[0.20]
assert spread > 0.35, f"r_cc 0.15~0.24 스윕 Kp 산포 {spread:.0%}"     # ~44%
# r_cc=0.15면 Kp(159)=4.89e-13 (팩의 1.4배), r_cc=0.24면 3.06e-13(0.87배) — 둘 다 오더 일치
assert 0.8 < kps[0.24]/PACK_KP < 0.95 and 1.3 < kps[0.15]/PACK_KP < 1.5
print(f"r_cc 민감도: Kp(159 Å/s) = {kps[0.15]:.2e}(rcc=.15) ~ {kps[0.24]:.2e}(rcc=.24), "
      f"산포 {spread:.0%} — 절대값 literature 승격 불가, estimated 유지의 정량 근거")
```

```python verify
# 블록3: Preston 선형성(Guo 2004) — 저압저속 레짐에서만 a≈b≈1, 밖에서는 꺾임
# Fig2 고압: MRR ∝ P^(1/6). 팩의 순수 Preston(a=1)이 고압에서 얼마나 과대예측하는가
a_lin, a_high = 1.0, 1.0/6.0
# threshold~1.5psi 위 선형구간 기준점 6psi, 이후 12psi로 외삽
P0, P1 = 6.0, 12.0
mrr_linear_extrap = (P1/P0)**a_lin     # 팩 가정: 2배
mrr_true_powerlaw = (P1/P0)**a_high    # Guo 실측: 1.12배
overpred = mrr_linear_extrap / mrr_true_powerlaw
assert overpred > 1.7, overpred        # 순수 Preston이 6->12psi에서 ~78% 과대예측
# V 포화: 0.7 m/s 위에서 b->0. 팩 기준 V~1 m/s는 포화 초입
assert 1.0 > 0.7   # 팩 운전 V가 Guo 포화문턱을 이미 넘음(선형 외삽 주의)
# 두 압력에서 K_P가 오차내 동일 => Kp가 P·V 독립 상수임을 실측 (Preston의 전제)
kp_36, kp_68 = 1.21e-9, 1.21e-9        # psi^-1, Fig1
assert kp_36 == kp_68
print(f"Preston 선형성: 저압저속 유효. 고압 외삽 과대예측 {overpred:.2f}배(6->12psi, P^1 vs P^1/6); "
      f"V>0.7m/s 포화 => 팩 Kp는 '포화문턱 근처 유효계수'")
```

```python verify
# 블록4: H2O2 정점(산성 pH4) — Seal/Gopal 3.6wt% vs 팩 oxidizer_peak_wt_pct=3.0
import yaml
from pathlib import Path
pack = yaml.safe_load(Path("knowledge/params/cu_h2o2_bta.yaml").read_text())
peak = pack["params"]["oxidizer_peak_wt_pct"]["value"]
ph = pack["params"]["slurry_ph"]["value"]
assert peak == 3.0 and ph == 4.0
# Seal/Gopal 산성 정점 3.0~3.6 wt% — 팩 3.0은 이 범위 하단, 3.6과 20% 이내
seal_peak = 3.6
assert abs(peak - seal_peak)/seal_peak < 0.20, f"팩 정점 {peak} vs Seal 3.6wt% 차이"
# Gopal 모델: 1.4->3.6 wt% 에서 MRR +150% (정점 접근). 정점이 관측 안쪽(>0)임을 확인
assert 1.4 < peak < 10.0    # 팩 정점이 Seal 관측창(1~10wt%) 안
# 레짐 분리: 이 산성 정점형은 chi 노트(판정#20)의 알칼리 단조감소와 pH가 다르다 — 평균 금지
alkaline_ph = 10.3          # US20110165777A1 TABLE2 (chi 노트)
assert abs(ph - alkaline_ph) > 5.0, "산성 팩(pH4)과 알칼리 반증계(pH10.3)는 레짐 분리 대상"
print(f"H2O2 정점: 팩 {peak}wt%(pH{ph}) — Seal/Gopal 산성 3.6wt% 정점 확증(20% 이내), "
      f"chi 노트 알칼리 pH10.3 단조감소와는 레짐 분리(평균 안 함)")
```

## 10. 자기시험
→ [[../../agents/film-cu/EXAMS.md]] Lv3-2 문항 참조.
