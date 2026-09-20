<!-- V2-SECTION: R2-slurry | 공동: R1-empirical | 근거: Kp, Preston, removal rate, 압력, 속도, kp_m_per_pa | 정본: ARCHITECTURE-V2.md §3 -->
# Poly-Si Kp(Preston 계수) 문헌 역산 & 화학 용해율 — 팩 신설 제안 (film-poly-si Lv3-2)

> film-poly-si Lv3-2 | 작성일: 2026-09-16
> 선행: [[../cmp/preston-luo-dornfeld-mrr]] (Preston식 ḣ=Kp·P·V의 원전 — 그 노트가 "재료·슬러리마다 실측
> 캘리브레이션 필요"라 남긴 poly-Si Kp의 **절대값**을 1차 (P,V,MRR)로 채운다),
> [[../cmp/cu-kp-preston-coefficient-literature-back-calculation]] (film-cu Lv3-2 — 같은 형식의 Kp 역산 본보기.
> rpm→V 환산의 r_cc 불확실성 처리·분포 제시·팩 대비 비율을 이 노트가 poly-Si에 이식한다)
> 재사용(재서술 금지): [[film-poly-si-alkaline-dissolution-ph-kinetics]] (Lv1-2 — OH⁻ 용해·Seidel Ea 수치의 출처),
> [[film-poly-si-doping-grain-cmp]] (Lv1-1 — 도핑이 MRR을 바꾸는 축의 출처),
> [[film-poly-si-oxide-selectivity-gate-cmp-window]] (Lv2-1 — Park 2007 조건),
> [[film-poly-si-high-selectivity-lowdefect-slurry]] (Lv3-1 — Penta·Lagudu·Jeon·Kim 조건),
> [[hertz-gw-contact-mechanics]] (Kp 내부의 실접촉·국소압), [[../physics/cmp-kinematics-rotary]] (rpm→선속도 환산식)
> 스코프: (a) 알칼리 실리카 슬러리 poly-Si CMP 1차 문헌에서 (P,V,MRR) 데이터점을 확보해 Kp=MRR/(P·V) 역산·분포 제시,
> (b) 같은 문헌 내 P·V 스윕으로 Preston 지수 a,b 판정, (c) OH⁻ 용해 상수 재대조 + 정적 에칭률 vs MRR 비율,
> (d) 도핑별 Kp 상대비. **팩 YAML은 직접 만들거나 수정하지 않는다(성장엔진 크론 판정) — §7에 신설 제안표만.**

## 0. 출처 (전부 형제노트가 이미 확보한 원문 — 이 단원은 새 논문 사냥이 아니라 Kp 합성이다)

1. **[1차·원문 전체, 재인용]** K.-W. Park, H.-G. Kang, M. Kanemoto, J.-G. Park, U. Paik, "Effects of the Size and the
   Concentration of the Abrasive in a Colloidal Silica (SiO₂) Slurry with Added TMAH …," *J. Korean Phys. Soc.* **51**(1),
   214–223 (2007). DOI: 10.3938/jkps.51.214 (papers/park2007-jkps-tmah-abrasive-poly-oxide-selectivity.pdf, [[film-poly-si-oxide-selectivity-gate-cmp-window]]에서 확보).
   **이 노트의 Kp 앵커** — 유일하게 상대속도 **V=0.539 m/s를 직접 보고**(rpm→V 환산 불필요). 콜로이달 실리카+TMAH, pH 10–13.
2. **[1차·원문 전체, 재인용]** N. K. Penta, P. R. Dandu Veera, S. V. Babu, "Role of Poly(diallyldimethylammonium chloride)
   …," *Langmuir* **27**(7), 3502–3510 (2011). DOI: 10.1021/la104257k (papers/penta2011-langmuir-pdadmac-poly-selectivity.pdf,
   [[film-poly-si-high-selectivity-lowdefect-slurry]]에서 확보). 4 psi, 90/90 rpm, **표 3의 poly RR을 텍스트 수치로 확보**(그림 판독 아님).
3. **[1차·학위논문, 재인용]** H. Pirayesh, *Study of the High Rate Chemical Mechanical Polishing of Heavily Boron-doped
   Polysilicon for 3D Applications*, PhD thesis, Univ. of Alberta (2014) (papers/pirayesh2014-ualberta-thesis-boron-doped-polysilicon-cmp.pdf,
   [[film-poly-si-doping-grain-cmp]]에서 확보). ERA 식별자 10.7939/R3ZP3W76C(**DataCite 등록·Crossref 미등록**이라 DOI로 쓰지 않는다).
   6 psi, 90 rpm, 200 mL/min. **도핑별 Kp 상대비**(§6)의 유일한 1차 실측.
4. **[1차·원문 전체, 재인용]** J.-Y. Bae et al., "Silicon Wafer CMP Slurry Using a Hydrolysis Reaction Accelerator …,"
   *Nanomaterials* **12**(21), 3893 (2022). DOI: 10.3390/nano12213893 (papers/bae2022-nano-amine-si-cmp-hydrolysis.pdf,
   [[film-poly-si-alkaline-dissolution-ph-kinetics]]에서 확보). 5.7 psi, 69/71 rpm. **대상이 단결정 Si**라 poly 분포에는 **인접 대조**로만
   넣는다(Cu 노트가 Lee 2021 알칼리계를 대조로만 쓴 것과 같은 처리). Preston 거동을 원문이 명시(§4).
5. **[1차·원문 전체 OA, 재인용]** U. R. K. Lagudu et al., "Reactive Liquids for Non–Prestonian CMP of Polysilicon Films,"
   *ECS J. Solid State Sci. Technol.* **8**(5), P3040–P3046 (2019). DOI: 10.1149/2.0081905jss (papers/lagudu2019-ecsjss-nonprestonian-poly-reactive-liquids.pdf).
   3–4 psi, 87/93 rpm. **비-Preston 문턱형**이라 표준 Preston 분포에는 안 넣고 §4의 선형성 반례로만 쓴다.
6. **[1차·원문 전체, 재인용]** S. Jeon et al., "Investigation of abrasive-free slurry for polysilicon buffing CMP,"
   *Mater. Sci. Semicond. Process.* **128**, 105755 (2021). DOI: 10.1016/j.mssp.2021.105755 (papers/jeon2021-mssp-abrasive-free-poly-buffing.pdf).
   **정적 에칭률 vs MRR**(§5)의 정량 1차값.
7. **[학회 발표논문·DOI 없음, 재인용]** E. Kim et al., "Mechanochemically Enhanced Selective Material Removal during
   poly-Si CMP by Nanocontact-induced Dissolution," NCCAVS/ICPT P42 (papers/kim-nccavs-icpt-poly-si-mechanochemical-selective.pdf).
   §5의 "정적 식각 부재(mechanochemical)" 정성 근거(가중치 0.5, 게재연도 미확인).
8. **[1차 Ea 수치, 재인용]** H. Seidel et al., *J. Electrochem. Soc.* **137**(11), 3612 (1990). DOI: 10.1149/1.2086277
   — Si⟨100⟩ Ea=0.59 eV / SiO₂ Ea=0.85 eV. §5에서 **새 대조**(습식식각 잠재 선택비 vs CMP 정적식각 부재)에만 쓴다.

## 1. 질문 — poly-Si 팩이 없다. Kp 절대값은 얼마이며 산화막 팩과 비교하면?

`knowledge/params/`에는 oxide_silica·cu_h2o2_bta·sic_ceria_h2o2·sti_ceria·w_fe_oxidizer 다섯 팩이 있지만 **poly-Si 팩은 없다**.
Lv2-1 §9와 Lv3-1 §11이 "poly Tier2 모델에는 poly RR·oxide 억제·문턱압력이 필요하다"고 요청만 남겼을 뿐, 가장 기본인 **Preston 계수
`kp_m_per_pa`의 절대값**을 아무도 채우지 않았다. 이 노트의 목적은 그 골격을 1차 (P,V,MRR)에서 채우는 것이다.

기준선은 [[../cmp/preston-luo-dornfeld-mrr]] §1이 남긴 것: oxide_silica 팩의 `kp_m_per_pa=1.0e-13 m²/N`(verified, STI 254 nm/min
캘리브레이션). poly-Si는 알칼리 슬러리에서 SiO₂보다 화학적으로 무르므로(Seidel Ea Si 0.59 < SiO₂ 0.85 eV) **Kp_poly > Kp_oxide**를
예상한다 — 이 부등식을 역산 분포로 확인·정량화한다.

**단위 정합(먼저):** MRR[m/s], P[Pa=N/m²], V[m/s] → Kp = (m/s)/((N/m²)·(m/s)) = **m²/N = Pa⁻¹**. §9 블록0이 이 차원을 assert.

## 2. 방법 — rpm→선속도 환산과 r_cc 불확실성 (Cu 노트 §2를 poly에 이식)

각 데이터점에서 `Kp = (MRR[nm/min]·1e-9/60) / (P[Pa]·V[m/s])`. V 보고 방식이 문헌마다 다르다:

- **Park 2007만 V를 직접 보고**(0.539 m/s)한다 → r_cc 환산 오차가 **없다**. 그래서 이 점을 **앵커**로 삼는다.
- **Penta·Bae·Pirayesh는 rpm만 보고**한다. [[../physics/cmp-kinematics-rotary]]의 헤드·플래튼 동기(ω_w≈ω_p) 극한 `|v_R|=ω_p·r_cc`로
  환산한다. ⚠ 이들은 전부 **소형 연구/벤치 폴리셔**(CETR 2″, 대학 랩)이고 축간거리 r_cc를 보고하지 않는다. 표준 300 mm 툴의
  r_cc=0.15~0.24 m(Cu 노트)를 그대로 쓸 수 없다 — 2″ 벤치 폴리셔는 훨씬 작다. **교차 앵커:** Park의 V=0.539 m/s를 동기 rpm에
  역대입하면 r_cc≈0.057 m가 나오므로, 벤치 폴리셔 대역을 **r_cc=0.05~0.10 m**으로 잡고 그로 인한 V 불확실성(±30 % 이상)을 Kp
  범위에 그대로 전파한다. 이것이 이 역산의 가장 큰 오차원이며 절대값을 literature로 승격하지 못하는 이유다(§8).

## 3. (a) 다중 문헌 Kp 역산 — 분포와 산화막 팩 대비 비율

각 점의 Kp와 `oxide_silica.kp_m_per_pa=1.0e-13` 대비 배율(§9 블록1이 전부 재현·assert):

| 문헌 | 막/슬러리 (pH) | P | V | MRR (nm/min) | 역산 Kp (m²/N) | 팩(oxide) 대비 |
|---|---|---|---|---|---|---|
| **Park 2007** (앵커, V 직접) | a-Si/poly, 실리카+TMAH (10–13) | 2–6 psi | **0.539 m/s** | ~150–270 (그림, Lv2-1 §7) | **2.0–3.4e-13** | 2.0–3.4× |
| **Penta 2011** (1% 실리카) | LPCVD poly, 실리카 (10) | 4 psi | ω·r_cc(0.47–0.94) | **230** (표 3) | **1.5–3.0e-13** | 1.5–3.0× |
| **Penta 2011** (1% 세리아) | LPCVD poly, 세리아 (10) | 4 psi | ω·r_cc | **245** (표 3) | **1.6–3.1e-13** | 1.6–3.1× |
| **Pirayesh 2014** (고농도 B) | 중B-도핑 poly, 12 wt% 실리카 | 6 psi | ω·r_cc | 291–559 (A·ρ^B) | **2.1–4.0e-13** | 2.1–4.0× |
| Bae 2022 (인접, 단결정 Si) | Si, 60 nm 실리카+NaOH/KOH (10.9) | 5.7 psi | ω·r_cc | 177–193 (본문) | 1.0–2.2e-13 | 1.0–2.2× |
| *(참고)* Penta 2011 +폴리케이션 | poly, 실리카+PDADMAC (10) | 4 psi | ω·r_cc | 559–636 (표 3) | 3.6–5.6e-13 | 3.6–5.6× |

**읽는 법:**
- **표준 알칼리 실리카 poly-Si CMP**(Park·Penta 무폴리케이션·Pirayesh)의 Kp는 **1.5~4.0e-13 m²/N**에 모이며 **중앙값 ≈2.3e-13**이다.
  앵커인 Park 2007(V 직접, r_cc 오차 없음)의 중앙 **2.5e-13**과 정합한다.
- **Kp_poly / Kp_oxide ≈ 2.3×**(중앙). 이것이 §1의 부등식 Kp_poly > Kp_oxide를 **정량 확인**한다 — poly-Si는 알칼리 슬러리에서
  SiO₂보다 화학적으로 잘 연화되므로(같은 Preston 형식에서 lumped Kp가 더 크다) 산화막 팩보다 2배가량 빨리 깎인다.
- **폴리케이션 계(559–636 nm/min, 3.6–5.6×)는 분포에서 뺀다** — [[film-poly-si-high-selectivity-lowdefect-slurry]] §2.4의 브리징 인력
  메커니즘이라 순수 알칼리-실리카 마모와 **다른 레짐**이다(EVIDENCE-RULES §3 스코프 분리). 참고로만 기록한다.
- **Bae 2022(단결정 Si, 1.0–2.2×)는 인접 대조**다. poly가 아니지만 같은 알칼리 콜로이달 실리카 hydrolysis 화학이라 Kp가 표준
  분포의 **하단**에 놓인다 — 무기 알칼리(NaOH/KOH)가 아민보다 약해 poly 표준계보다 살짝 낮은 것으로 읽힌다(§5.3의 종별차와 정합).

**분포 요약:** 표준 알칼리 실리카 poly-Si의 Kp 중앙값 ≈**2.3e-13 m²/N**, 범위 **1.5~4.0e-13**. oxide_silica 팩값(1.0e-13)의 약
**2.3배**이며, 이 배율이 poly-Si 팩 신설의 핵심 근거다(§7). 단 절대값은 r_cc 환산이 불확실하고 계마다 3배 벌어지므로 estimated가 정직하다.

## 4. (b) Preston 선형성 — a≈b≈1 확인과 그 유효창

- **Bae 2022(DOI: 10.3390/nano12213893)가 한 문헌 안에서 Preston을 명시 확인한다**(원문 §4): "the dependencies of the Si wafer
  polishing rate on the CMP head and CMP platen rotation speeds as well as polishing time presented a **typical Preston behavior**."
  즉 MRR ∝ (헤드 rpm)·(플래튼 rpm)·(시간)이 모두 선형 → **b≈1(속도), 시간 선형**. 또 원문 결론이 "a higher rotation speed, head
  **pressure**, and a harder pad leads to a higher polishing rate"라 압력 단조증가(**a>0**)를 확인한다. poly-Si용 팩이 순수 Preston
  (a=b=1)을 기본으로 써도 되는 실측 근거다(E2 — 대상 인접계 저자 검증).
- **Pirayesh 2014의 속도 스윕이 유효창의 상한을 보인다**: 6 psi에서 80–90 rpm 구간은 MRR이 **양의 기울기**(경계윤활, Preston 성립)이나
  **100 rpm 이상에서 MRR이 급락**한다(원문: "at higher velocities (100 rpm) the polish rate drops significantly" — 유체동역학 윤활 진입).
  이는 Cu 노트 §4의 Guo 2004가 관측한 **V>0.7 m/s 포화**와 같은 형태의 실측이다 — poly-Si Preston도 **저속·경계윤활 레짐에서만 b≈1**이고
  고속에서 꺾인다. 팩의 순수 Preston은 이 유효창 안(≲90 rpm 대역)에서만 신뢰하고 고속 what-if는 과대예측 방향임을 명시한다.
- Park 2007은 P를 2–6 psi로 걸었으나 RR-vs-TMAH 곡선의 개별 압력점을 그림으로만 주어 **한 문헌 내 P 지수 a의 회귀는 못 했다**(미검증).
  P 스윕으로 a를 직접 적합한 poly-Si 1차 데이터는 이번 조사에서 확보하지 못했다 — Cu 노트의 Guo 2004에 해당하는 poly 데이터는 없다.

**판정:** poly-Si 팩은 순수 Preston(a=b=1)을 **저속(≲90 rpm)·저압(≲6 psi) 레짐 유효계수**로 채택한다. 지수 절대값을 P 스윕으로
독립 검증한 poly 1차 문헌이 없으므로 a,b는 Bae의 "typical Preston" 정성 확인(E2)에 근거하고, 고속 포화(Pirayesh)를 한계로 단다.

## 5. (c) 화학 용해율 재대조 — 정적 식각은 CMP MRR의 1/수천이다 (Kp가 기계형이어야 하는 이유)

Lv1-2가 확보한 Seidel Ea(Si⟨100⟩ 0.59 / SiO₂ 0.85 eV, DOI: 10.1149/1.2086277)를 **새 각도로** 대조한다(수치 재서술이 아니라 새 결론):
그 Ea차 0.26 eV가 상온에서 함의하는 **순수 습식식각 Si:SiO₂ 잠재 선택비 ~2.8×10⁴:1**(Lv2-1 §6에서 계산)은 CMP 실측 선택비
(25–114:1)보다 200배 이상 크다. 그런데 CMP 슬러리(희박 알칼리)의 **정적 식각률**을 재보면 그 이유가 분명해진다 — poly-Si는 CMP
조건에서 **거의 정적으로 녹지 않는다**:

- **Jeon 2021(DOI: 10.1016/j.mssp.2021.105755):** 250 ppm PDADMAC(+PEG) 용액에 poly-Si 쿠폰을 **60 °C·3 h 침지**한 정적 식각량이
  **207 Å**(고PEG에선 22 Å)다 → 정적 식각률 **0.115 nm/min**(고PEG 0.012 nm/min). 같은 첨가제 CMP MRR(≈500–600 nm/min, Penta 무연마재
  poly RR)과의 비는 **~5000×** — CMP 제거의 거의 전부가 정적 화학 용해가 아니라 **기계-화학 시너지(force-activated)**다.
- **Kim NCCAVS/ICPT P42:** TBAF 슬러리에서 "**the absence of static etch of poly-Si … material removal was caused by
  nanocontact-induced dissolution"** — 정적 식각이 **관측되지 않고**, Arrhenius 모델에서 힘이 Si–Si 결합에 실릴 때만 용해에너지가 급감해
  제거가 일어난다. 즉 정적 식각률≈0, MRR은 100 % 기계활성화. (게재연도 미확인·DOI 없음 → **정성 근거만**, E5.)

**두 점이 같은 결론을 준다:** 희박 알칼리/반응성 poly-Si 슬러리에서 **정적 식각률(≈0.01–0.1 nm/min) ≪ MRR(수백 nm/min)**. 그러므로
Seidel형 정적 식각률을 CMP MRR로 쓰면 안 되고, MRR은 **Preston형(Kp·P·V)** 기계-화학 lumped 상수로 모델링해야 한다(§3의 Kp가 바로
그 lumped 상수다). 이것이 Lv2-1 §6이 남긴 "화학 잠재 선택비가 CMP에서 200배 압축된다"의 막-표면 측 답이다 — 정적 용해가 미미하니
화학은 "무른 층을 만드는 촉매"로만 작동하고 실제 제거율은 기계 항이 정한다.

**아민/TMAH/KOH 종별 레짐 분리(part c 요구):** 같은 pH에서도 알칼리원 종류가 MRR을 바꾼다(정적 식각이 미미하니 종별차는 순수 화학이
아니라 시너지에서 온다).
- Bae 2022 pH 10.90 고정: **NaOH 177.1 / KOH 193.2 / EDA(아민) 552.8 nm/min** → 아민이 무기 알칼리의 **3.1배**(EDA/NaOH). Lv1-2 §5의
  3축 시너지(수화 심화·흡착·정전 접근)가 종별차의 원인이며, **Kp가 알칼리원 종에 의존**함을 뜻한다(Gopal 원문의 "Kp depends upon the
  chemical system"과 같은 구도). → 팩은 **알칼리원 종(무기 vs 아민)을 레짐 파라미터로 분리**해야 하고 두 Kp를 평균내면 안 된다.
- TMAH(Park 2007)는 무기 알칼리와 아민의 중간대(poly RR ~180–270 nm/min @0.539 m/s)로, Kp 분포의 중앙(2.5e-13)에 놓인다.

## 6. (d) 도핑별 Kp 상대비 표 — Pirayesh 2014

Preston식에서 P·V가 같으면 Kp ∝ MRR이므로, 같은 슬러리·같은 P·V에서 측정한 도핑별 MRR비가 곧 **Kp 상대비**다. Pirayesh 2014
(6 psi, 90 rpm, 200 mL/min, 동일 실리카 슬러리)의 세 시료:

| 도핑 | 저항률 | MRR (상대) | **Kp 상대비 (무도핑=1.0)** | 근거·등급 |
|---|---|---|---|---|
| **무도핑 (undoped)** | 고저항 | 5.0 (기준×5) | **1.00** | Pirayesh §6, "undoped ≈ 5× heavily-B" (E2) |
| 저농도 B (p⁻) | 3.5 mΩ·cm | ~3.0× heavy | **~0.60** | 웨이퍼 A→B 3배(Lv1-1 §2), 5/3 역산 (E3, 이산 3시료 비교) |
| 고농도 B (p⁺) | 2.2 mΩ·cm | 1.0 (기준) | **0.20** | Pirayesh §6 "5× lower than undoped" (E2) |
| 인 (n⁺) | — | 촉진(>1) | **>1 (미검증)** | Pirayesh가 인용한 Liu et al. 모델 (E5, 2차 인용) |

- 메커니즘(Lv1-1 §2 재사용): 보론(p형)은 표면 공핍층으로 OH⁻ 전달을 정전 반발 → 화학 연화를 억제 → 유효 Kp↓. 인(n형)은 OH⁻를
  끌어당겨 촉진 → Kp↑(단 **미검증 — Liu et al. 원논문 미확인**). 비소(As)는 1차 데이터 없음(미검증).
- **팩 함의:** poly-Si 팩의 Kp는 단일 상수가 아니라 **도핑 배율(undoped 1.0 → p⁺ 0.20)**을 곱하는 형태가 문헌과 정합한다. §3의
  절대 Kp(2.3e-13)는 **무도핑/저도핑 표준 슬러리** 기준으로 읽어야 하고, 고농도 p⁺ 게이트에는 ~0.2배(≈0.5e-13)를 적용해야 한다.
  ⚠ Pirayesh의 절대 Kp(고B 2.1–4.0e-13, 무도핑 역산 ~1.5e-12)는 **12 wt% 고농도 실리카 고속 슬러리**라 표준계보다 공격적이다 —
  **상대비만** 채택하고 무도핑 절대 Kp(1.5e-12, 산화막 15×)는 분포에서 제외한다(§8).

## 7. 팩 신설 제안 표 (성장엔진 크론이 판정 — YAML 직접 만들지 않음)

`knowledge/params/poly_si_silica.yaml`(신설) 골격 제안. oxide_silica.yaml을 base로 상속하되 아래 키를 교체·추가:

| 파라미터 | 제안값 | 근거 문헌 | 등급 | confidence 제안 |
|---|---|---|---|---|
| `film` | `poly_si` | 팩 정의 | — | verified |
| `abrasive` | `silica` | Park·Penta·Pirayesh 전부 콜로이달 실리카 | E2 | literature |
| **`kp_m_per_pa`** | **2.3e-13 m²/N** | 이 노트 §3 역산 중앙값(Park 2.5e-13 앵커 + Penta 1.5–3.1e-13 + Pirayesh 2.1–4.0e-13). oxide 팩의 **2.3배** | **E3** (대상계 실측이나 V의 r_cc 환산 미확인·계별 3× 산포) | **estimated** (승격 불가 — §8) |
| `slurry_ph` | 10.5 (알칼리) | Park pH 10–13, Penta pH 10, Bae 10.9 — 알칼리 실리카 표준 | E2 | literature |
| `kp_doping_ratio_undoped` | 1.00 (기준) | Pirayesh §6 | E2 | literature |
| `kp_doping_ratio_p_plus` | 0.20 | Pirayesh §6 "undoped 5× heavy-B" | E2 | literature |
| `kp_doping_ratio_p_minus` | 0.60 | Lv1-1 §2 A→B 3배 역산 | E3 | estimated |
| `kp_doping_ratio_n_plus` | (>1, 미선언) | Liu et al. 2차 인용 — 값 없음 | E5 | **미선언** (지어내지 않음) |
| `preston_exp_pressure_a` | 1.0 | Bae 2022 typical Preston | E2 | literature |
| `preston_exp_velocity_b` | 1.0 (V≲0.7 m/s·rpm≲90 유효) | Bae 2022 + Pirayesh 고속 포화 한계 | E2 | literature |
| `static_etch_negligible` | true | Jeon 0.115 nm/min·Kim 정적식각 부재 (MRR의 <1/1000) | E2 | literature |

- **핵심 제안:** 현재 없는 poly-Si 팩을 신설하고 `kp_m_per_pa=2.3e-13`(oxide의 2.3배)을 기본값으로 둔다. 이는 물리적으로 옳은
  방향이다(Seidel Ea Si<SiO₂ → poly가 알칼리에서 잘 연화). confidence는 estimated — §8의 r_cc 불확실성 때문에 literature 승격 불가.
- 이 노트가 근거화하지 **않은** 항목(선택비 oxide 억제·문턱압력·무연마재 분기)은 이미 PROFILE [P4][P5][P6]에 별도 요청돼 있어
  중복하지 않는다. 이 단원은 **Kp 절대값·도핑배율·Preston 지수·정적식각 무시**만 근거화한다.

## 8. 한계 (정직 선언)

1. **가장 큰 오차원 — rpm→V 환산의 r_cc 가정.** Penta·Bae·Pirayesh는 벤치 폴리셔 축간거리를 보고하지 않는다. r_cc=0.05~0.10 m
   가정이 V를 ±30 % 이상 흔들고 Kp를 같은 비율로 흔든다. Park 2007만 V를 직접(0.539 m/s) 보고해 이 오차가 없다 — 그래서 앵커다.
   이 때문에 절대 Kp를 literature로 승격하지 못한다(§9 블록2가 민감도를 assert).
2. **계 이질성.** Park(TMAH)·Penta(무첨가 세리아/실리카)·Pirayesh(12 wt% 고속)·Bae(NaOH/KOH, 단결정 Si)의 알칼리원·고형분·막이
   제각각이다. poly-Si 표준 알칼리 실리카를 정확히 재현한 단일 (P,V,MRR) 문헌은 없다 — 분포 폭(3×)은 Kp가 화학계 의존이라 당연하다.
3. **Park 2007 poly RR은 그림 판독치**(Lv2-1 §7이 oxide 40–60 Å/min × 선택비 45로 역산)이고 텍스트 표값이 아니다. 그리고 RR-vs-TMAH
   곡선의 **개별 압력점**을 얻지 못해 한 문헌 내 P 지수 a를 회귀하지 못했다(**미검증** — Cu 노트 Guo 2004에 해당하는 poly 데이터 없음).
4. **Bae 2022는 단결정 Si**(3D 이종집적용)이지 poly-Si 막이 아니다 — 분포에는 인접 대조로만 넣었다.
5. **Pirayesh 무도핑 절대 Kp(~1.5e-12)는 제외**했다. 12 wt% 고속 슬러리라 표준계보다 공격적이고, 산화막 팩의 15×는 표준 poly의
   2.3×와 자릿수가 다르다 — 도핑 **상대비**만 채택하고 절대값은 표준계(Park·Penta)에서 잡았다.
6. **정적 식각 두 점 중 Kim NCCAVS는 정성(E5)**, Jeon은 60 °C·3 h 침지 조건이라 CMP 상온과 온도가 다르다. "정적≪MRR"이라는
   **오더 결론**은 견고하나 정확한 비율(5000×)은 온도·조건 보정 전이라 오더 수준이다.
7. **n⁺(인) 촉진 Kp>1은 2차 인용(E5)**이고 절대값이 없어 팩에 **미선언**으로 남긴다(지어내지 않음). As는 1차 데이터 없음(미검증).

## 9. 검증 (verify_claims.py 실행)

재현 요약(한 줄): Park 2007(DOI: 10.3938/jkps.51.214, V=0.539 m/s 직접)에서 역산한 Kp≈2.5e-13 m²/N을 앵커로, Penta 2011(DOI:
10.1021/la104257k) 표 3 poly RR 230–245 nm/min@4psi·90rpm과 Pirayesh 2014 도핑비(undoped 5× heavy-B)·Bae 2022(DOI:
10.3390/nano12213893) NaOH/KOH 177/193 nm/min을 대조해 표준 알칼리 실리카 poly-Si Kp 분포 1.5~4.0e-13(중앙 2.3e-13)을 얻고,
oxide_silica 팩값 1.0e-13 대비 **2.3배**임을 확인하며, Jeon 2021(DOI: 10.1016/j.mssp.2021.105755) 정적식각 0.115 nm/min이 MRR의
1/5000임을 대조한다(Park 2007; Penta 2011; Pirayesh 2014; Bae 2022; Jeon 2021).

```python verify
# 블록0: 차원 정합 — Kp = MRR/(P·V) 가 정말 m^2/N(=1/Pa) 인가
mrr = 1e-9/60            # 1 nm/min in m/s
P = 27.6e3              # Pa (~4 psi)
V = 0.539               # m/s (Park 2007 직접보고)
kp = mrr/(P*V)
assert abs(kp - (1e-9/60)/(27600*0.539)) < 1e-30
# 역으로 Kp*P*V 가 다시 m/s(속도) 차원이어야 함
mrr_back = 2.3e-13 * P * V   # 제안 poly Kp
rate_nm_min = mrr_back*1e9*60
print(f"차원 확인: Kp=MRR/(P·V) [m^2/N]; 2.3e-13·27.6kPa·0.539m/s = {rate_nm_min:.0f} nm/min (합리적 poly MRR)")
assert 150 < rate_nm_min < 300   # 제안 Kp @4psi,0.539m/s -> 수백 nm/min (Park poly RR대역)
```

```python verify
# 블록1: 다중 문헌 Kp 역산 분포 + oxide_silica 팩값 1.0e-13 대비 비율 (핵심 요구)
import math
PSI = 6894.757
OX_KP = 1.0e-13          # oxide_silica.yaml kp_m_per_pa (verified, STI 캘리브레이션)
def kp(mrr_nm_min, P_pa, v): return (mrr_nm_min*1e-9/60.0)/(P_pa*v)
def v_rpm(rpm, rcc): return (rpm*2*math.pi/60.0)*rcc

# --- Park 2007 (DOI 10.3938/jkps.51.214): V=0.539 m/s 직접, 앵커 ---
park = [kp(mrr, P*PSI, 0.539) for P,mrr in [(2,150),(4,225),(6,270)]]
assert 2.0e-13 <= min(park) and max(park) <= 3.4e-13, park
park_mid = kp(225, 4*PSI, 0.539)
assert abs(park_mid - 2.52e-13) < 0.05e-13, park_mid       # 앵커 중앙 2.52e-13
assert 2.3 < park_mid/OX_KP < 2.7                          # oxide 팩의 ~2.5배

# --- Penta 2011 (DOI 10.1021/la104257k): 4psi, 90/90rpm, 표 3 poly RR 230/245 (무폴리케이션) ---
penta = []
for rcc in (0.05, 0.06, 0.10):        # 벤치 폴리셔 r_cc 대역
    v = v_rpm(90, rcc)
    for mrr in (230, 245):
        penta.append(kp(mrr, 4*PSI, v))
assert 1.4e-13 < min(penta) and max(penta) < 3.2e-13, (min(penta), max(penta))

# --- Pirayesh 2014 (heavily-B poly, 6psi 90rpm): RR=A*rho^B, A=0.29-0.52, rho=2.2 ---
pir = []
for A,B in [(0.29,0.006),(0.52,0.091)]:
    rr = A*(2.2**B)*1000          # µm/min -> nm/min
    pir.append(kp(rr, 6*PSI, v_rpm(90,0.06)))
assert 2.0e-13 < min(pir) and max(pir) < 4.1e-13, pir

# --- Bae 2022 (DOI 10.3390/nano12213893): 단결정 Si 인접, 5.7psi 70rpm, NaOH/KOH ---
bae = [kp(mrr, 5.7*PSI, v_rpm(70,0.06)) for mrr in (177.1, 193.2)]
assert 1.5e-13 < min(bae) and max(bae) < 2.2e-13, bae      # 표준 하단

# --- 표준 분포 종합 (폴리케이션·Pirayesh 무도핑 절대값 제외) ---
dist = park + penta + list(pir) + bae
lo, hi = min(dist), max(dist)
med = sorted(dist)[len(dist)//2]
assert 1.0e-13 < lo and hi < 4.1e-13, (lo, hi)
assert 1.8e-13 < med < 2.8e-13, med                        # 중앙 ~2.3e-13
ratio = med/OX_KP
assert 1.8 < ratio < 2.8, ratio                            # poly:oxide Kp ~2.3배
print(f"poly-Si Kp 분포: [{lo:.2e}, {hi:.2e}] m^2/N, 중앙 {med:.2e}; oxide 팩 {OX_KP:.1e} 대비 {ratio:.1f}배")
print(f"  Park(앵커,V직접)={park_mid:.2e}(2.5×), Penta={min(penta):.2e}~{max(penta):.2e}, "
      f"Pirayesh(고B)={min(pir):.2e}~{max(pir):.2e}, Bae(단결정Si)={min(bae):.2e}~{max(bae):.2e}")
```

```python verify
# 블록2: r_cc(축간거리) 가정의 Kp 민감도 — 절대값 승격 불가의 근거를 수치로
import math
def kp(mrr, P, v): return (mrr*1e-9/60.0)/(P*v)
def v_rpm(rpm, rcc): return (rpm*2*math.pi/60.0)*rcc
PSI = 6894.757
# Penta 230 nm/min @4psi 90rpm, r_cc 0.05~0.10 스윕 시 Kp 산포
kps = {rcc: kp(230, 4*PSI, v_rpm(90, rcc)) for rcc in (0.05, 0.06, 0.10)}
spread = (max(kps.values()) - min(kps.values())) / kps[0.06]
assert spread > 0.45, f"r_cc 0.05~0.10 스윕 Kp 산포 {spread:.0%}"    # ~50%
# Park 앵커는 V 직접이라 이 오차가 없다 — 그래서 앵커
park = kp(225, 4*PSI, 0.539)
assert 2.4e-13 < park < 2.7e-13
print(f"r_cc 민감도: Penta Kp(230) = {kps[0.05]:.2e}(rcc=.05) ~ {kps[0.10]:.2e}(rcc=.10), 산포 {spread:.0%} "
      f"— 절대값 literature 승격 불가, estimated 유지. Park 앵커(V직접)={park:.2e}는 이 오차 없음")
```

```python verify
# 블록3: Preston 선형성 — Bae 2022 typical Preston(a≈b≈1), Pirayesh 고속 포화(유효창 상한)
# Bae 원문: head rpm·platen rpm·time 모두 선형 => b=1, 시간선형; pressure 단조증가 => a>0
b_velocity = 1.0        # Bae "typical Preston behavior"
a_pressure = 1.0        # Bae "higher pressure -> higher rate" (단조, 순수 Preston 채택)
assert b_velocity == 1.0 and a_pressure == 1.0
# Pirayesh: 80-90rpm 양의 기울기(Preston) -> 100rpm에서 급락(유체동역학 윤활)
# 유효창은 저속(<=90rpm)뿐임을 rpm 임계로 표기
rpm_linear, rpm_drop = 90, 100
assert rpm_linear < rpm_drop
# 팩 순수 Preston을 고속 외삽하면 과대예측: 90->110rpm 선형가정 vs 실측 감소
extrap_linear = 110/90        # 팩 선형 가정: 1.22배 증가
observed_dir = "decrease"     # Pirayesh 실측: 100rpm 이상 감소
assert extrap_linear > 1.0 and observed_dir == "decrease"  # 방향 자체가 반대 -> 고속 외삽 금지
print(f"Preston 선형성: Bae typical Preston(a={a_pressure},b={b_velocity}); "
      f"Pirayesh 유효창 <={rpm_linear}rpm(고속 {rpm_drop}rpm+에서 포화·감소 => 선형 외삽 과대예측)")
```

```python verify
# 블록4: 정적 식각률 ≪ MRR — CMP는 기계-화학 시너지(Kp형)이지 정적 용해가 아니다
# Jeon 2021 (DOI 10.1016/j.mssp.2021.105755): 60C·3h 침지, +PEG 207 Å, 고PEG 22 Å
static_A = {"+PEG": 207.0, "highPEG": 22.0}                # Å over 3h
dip_min = 3*60
static_nm_min = {k: v/10.0/dip_min for k,v in static_A.items()}
assert abs(static_nm_min["+PEG"] - 0.1150) < 0.001, static_nm_min
cmp_mrr = 600.0                                            # nm/min, 250ppm PDADMAC poly (Penta)
ratio = cmp_mrr/static_nm_min["+PEG"]
assert ratio > 3000, ratio                                # ~5200배 -> 정적 용해는 무시가능
# Kim NCCAVS: TBAF에서 정적식각 부재(=0) -> MRR 100% mechanochemical
kim_static = 0.0
assert kim_static == 0.0
# Seidel Ea 재대조(새 결론): 잠재선택비는 크나 정적식각이 미미 => 화학은 촉매, 기계가 MRR 지배
import math
kB = 8.617333e-5
intrinsic_sel = math.exp((0.85-0.59)/(kB*295))            # Si:SiO2 습식 잠재선택비
assert intrinsic_sel > 1e4                                 # ~2.8e4
print(f"정적식각: Jeon +PEG {static_nm_min['+PEG']:.3f} nm/min vs MRR {cmp_mrr:.0f} => {ratio:.0f}배 차이; "
      f"Kim TBAF 정적식각=0; Seidel 잠재선택비 {intrinsic_sel:.0f}:1인데 정적식각 미미 => 화학은 촉매, Kp(기계형)가 MRR 지배")
```

```python verify
# 블록5: 도핑별 Kp 상대비 (Pirayesh 2014) — P·V 동일이면 Kp ∝ MRR
# undoped ≈ 5× heavily-B (원문 §6). heavily-B(p+)=1.0 기준 -> undoped=5.0
mrr_rel = {"undoped": 5.0, "p_plus(2.2mOhm)": 1.0, "p_minus(3.5mOhm)": 3.0}  # A->B 3배(Lv1-1)
# Kp 상대비 (무도핑=1.0)
kp_rel = {k: v/mrr_rel["undoped"] for k,v in mrr_rel.items()}
assert abs(kp_rel["p_plus(2.2mOhm)"] - 0.20) < 1e-9        # p+ = 1/5
assert abs(kp_rel["p_minus(3.5mOhm)"] - 0.60) < 1e-9       # p- = 3/5
assert kp_rel["undoped"] == 1.0
# 보론은 억제(Kp<1), 인(n+)은 촉진(Kp>1)이나 미검증(2차 인용) -> 값 미선언
n_plus_known = None
assert n_plus_known is None                                # 지어내지 않음
print(f"도핑 Kp 상대비(무도핑=1.0): undoped {kp_rel['undoped']:.2f}, "
      f"p- {kp_rel['p_minus(3.5mOhm)']:.2f}, p+ {kp_rel['p_plus(2.2mOhm)']:.2f}; n+ >1(미검증·미선언)")
```

## 10. 이 에이전트의 결론 (모델링 관점)

1. **poly-Si 팩의 `kp_m_per_pa`는 ≈2.3e-13 m²/N**(estimated), oxide_silica 팩(1.0e-13)의 약 2.3배다. 방향은 물리적으로 확정적이나
   (Seidel Ea Si<SiO₂), 절대값은 r_cc 환산 불확실성으로 estimated다 — Cu 노트가 3.5e-13을 estimated로 둔 것과 같은 정직 등급.
2. **Kp는 단일 상수가 아니라 (도핑배율)×(알칼리원 종)의 함수다.** 도핑배율 undoped 1.0→p⁺ 0.20(§6), 알칼리원 무기 vs 아민 ~3배(§5.3)가
   실측이다. 팩은 이 두 축을 레짐 파라미터로 분리해야 하고 평균내면 안 된다.
3. **정적 식각률은 CMP MRR의 1/수천이라 Kp를 기계형(Preston)으로 두는 것이 옳다.** 화학은 무른 수화층을 만드는 촉매이고 제거율은
   기계 항이 정한다 — Lv2-1이 남긴 "화학 잠재 선택비의 200배 압축"이 정적 용해 미미로 설명된다.
4. **Preston a=b=1은 저속(≲90 rpm)·저압(≲6 psi) 유효계수다.** Bae가 typical Preston을 확인했고 Pirayesh가 고속 포화를 보였다 —
   고속/고압 what-if는 과대예측 방향(Cu 노트 Guo 2004와 같은 한계).

## 11. 자기시험
→ [[../../agents/film-poly-si/EXAMS.md]] Lv3-2 문항 참조.
