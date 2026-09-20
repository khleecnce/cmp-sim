<!-- V2-SECTION: R2-slurry | 공동: R5-wafer | 분배완료 2026-09-08 | 근거: chemistry, colloid, dlvo, ph, slurry | 정본: ARCHITECTURE-V2.md §3 -->
# Post-CMP 흡착 메커니즘과 제거 화학 — 제타전위·pH·킬레이트(시트르산·EDTA)·희석 HF·오존수·RCA, 막질별 세정 레시피

> 에이전트: surface-contamination Lv2-2 | 작성일: 2026-09-07
> 선행: [[post-cmp-metallic-contamination-sources]] [[metal-contamination-device-impact-irds-limits]] [[wafer-surface-metal-detection-txrf-vpdicpms-sims-xps]] [[colloid-zeta-dlvo-slurry-stability]] [[surface-chemistry-cu-w-pourbaix-passivation]] [[ceria-slurry-ce-redox-selectivity]] [[particle-wafer-interaction-mechanical-chemical-balance]]

## 1. 왜 필요한가 — "흡착의 역과정"으로 세정을 설계한다
Lv1-1([[post-cmp-metallic-contamination-sources]])에서 오염원을, Lv2-1([[metal-contamination-device-impact-irds-limits]])에서
허용치(ITRS FEP 스펙 1×10¹⁰ atoms/cm²)를 확인했다. 이 단원은 **금속 이온·입자가 왜 표면에 붙는가**(흡착
메커니즘)를 먼저 세우고, 그 각각의 구동력을 끊는 화학(킬레이트·산·산화제·pH)을 대응시킨다. 세정 레시피는
암기 대상이 아니라 "표면전하 부호(ζ, IEP) × 이온의 착화 평형(logK, pH) × 막질의 부식 창(Pourbaix)"
세 축의 교집합에서 유도되는 것임을 보이는 게 목표다. §6에서 (A) EDTA logK의 이온세기 보정, (B) pH별 조건부
안정도상수 K′, (C) IEP 기반 표면전하 부호를 코드로 재현한다.

## 2. 흡착 메커니즘 세 가지 — Mouche·Tardif·Derrien(1995)의 분류
세정액 속 금속이 Si/SiO₂ 표면에 붙는 경로는 세 가지로 정리된다(L. Mouche, F. Tardif, J. Derrien, "Mechanisms of
Metallic Impurity Deposition on Silicon Substrates Dipped in Cleaning Solution," *J. Electrochem. Soc.* 142(7),
2395 (1995), https://doi.org/10.1149/1.2044308 — **초록만 확인**, 본문 유료):
(i) **물리흡착**(van der Waals), (ii) **화학흡착**(표면과 전자 공유 — 실라놀 Si–O⁻와 양이온의 착화·이온교환),
(iii) **금속 치환**(전기화학적 전자 이동 — 귀금속 Cu²⁺가 Si를 산화시키며 Cu⁰로 석출). 초록은 **이온세기**와
**불순물·표면의 극성(전하)**이 용액→표면 이동을 지배하는 변수라고 명시한다. 이것이 곧 이 노트의 골격이다:
- (ii)의 정전기적 구동력은 [[colloid-zeta-dlvo-slurry-stability]]의 전기이중층으로 기술된다. 표면 ζ<0(pH>IEP)이면
  양이온이 Boltzmann 인자 exp(−zeψ/kT)만큼 표면에 농축된다(Lv1-1 §6(C)에서 ζ=−40 mV, Cu²⁺ 농축 ≈22배 재현).
- (iii)는 Cu에 특유하다. Cu²⁺/Cu(+0.34 V)가 Si의 산화전위보다 높아 HF 속 H-종단 Si 위에서 Cu가 **무전해 석출**된다
  — 이것이 "DHF 세정은 Fe엔 좋지만 Cu엔 위험"한 이유의 전기화학적 근거([[surface-chemistry-cu-w-pourbaix-passivation]] §4의
  Cu 환원전위 참조; 석출 속도 정량은 **미검증**).
- 세정은 (ii)엔 **pH·킬레이트**, (iii)엔 **산화제(H₂O₂·O₃)**, 입자엔 **정전반발+화학결합 절단**으로 대응한다.

## 3. 표면전하: IEP(등전점)와 pH — 어느 pH에서 무엇이 끌리는가
| 산화물 | IEP (pH) | 출처 |
|---|---|---|
| SiO₂(실리카 유리) | **2** | Brugnoli et al., *Langmuir* 39, 5527 (2023), PMC10116594, https://doi.org/10.1021/acs.langmuir.3c00304 — "silica glass surface has a net negative charge (IEP = 2)" |
| CeO₂(세리아) | **6.8** (실측 5.21–9.40, 합성법 의존) | Brugnoli 2023 "ceria surface is neutral (IEP = 6.8)"; Ederer et al., *RSC Adv.* 15, 38391 (2025), PMC12519946, https://doi.org/10.1039/d5ra05301c Table 2 (Ce-CARB 6.12 / Ce-UREA 6.87 / Ce-PER 9.40 / Ce-HMT 8.21 / Ce-AMN 5.21) |
| α-Al₂O₃(알루미나) | **~9.5**(세척 후; 미세척 8.5–9) | Zhang, Zhang, Gao, *Heliyon* 10, e38280 (2024), PMC11462379, https://doi.org/10.1016/j.heliyon.2024.e38280 — ζ>+40 mV @pH<6, −60~−70 mV @pH 12 |

- **원리**: 표면 M–OH가 pH<IEP에서 M–OH₂⁺(양), pH>IEP에서 M–O⁻(음)로 바뀐다(Brugnoli 2023 식(1),(2)).
  실리카는 거의 모든 세정 pH에서 **음전하**라 양이온(Cu²⁺·Fe³⁺·K⁺·Ca²⁺)을 끌어들이고, 세리아는 IEP 6.8 아래(대개
  STI 세리아 슬러리 pH)에서 **양전하**라 음전하 실리카 표면에 정전기적으로 달라붙는다 — 세리아 잔류입자가
  산화막 위에 남는 정전기적 이유. (여기에 Ce–O–Si 화학결합이 겹친다, §5.3.)
- **pH를 올리면**(SC-1/알칼리 post-CMP, pH≈10–11) 세 산화물 모두 음전하 → 입자–웨이퍼 **정전반발**이 생겨
  입자 제거에 유리하지만, 동시에 실리카 |ζ|가 커져 **양이온 정전흡착은 강해진다** — 그래서 알칼리 세정엔
  반드시 **킬레이트제**가 동반된다(§4). 반대로 **pH를 IEP 이하로 내리면**(DHF) 실리카 음전하가 사라져 Cu²⁺
  정전흡착 구동력이 꺼진다(Lv1-1 §3의 논리). §6(C)에서 DHF 0.5 wt%의 pH≈1.9(HF pKa 3.17)와 부호표를 재현.
- 재현 요약(한 줄): §6(C)에서 CeO₂ IEP 6.8은 Ederer 2025 실측 범위 5.21–9.40 pH 안에 들고, pH 5.0에서 CeO₂(+)/SiO₂(−) 이부호, pH 11.0에서 세 산화물 모두 (−)임을 문헌값 IEP로 대조 확인(Brugnoli et al. 2023, https://doi.org/10.1021/acs.langmuir.3c00304).

## 4. 킬레이트 화학 — 안정도상수 logK, 이온세기, 조건부 상수 K′(pH)
### 4.1 문헌값 (1차: USGS PHREEQC `minteq.v4.dat`, 출처태그 NIST46.2; OA 논문 2건)
| 착물 | logK (I=0, MINTEQ/NIST46.2) | logK (I=0.1, OA 논문) |
|---|---|---|
| Fe³⁺–EDTA | 27.7 | 25.1 (Kontoghiorghes 2020 Table 3; Palden 2020) |
| Cu²⁺–EDTA | 20.5 | 18.8 (Kontoghiorghes) / 18.7 (Palden, 25 °C μ=0.1) |
| Ca²⁺–EDTA | 12.42 | (OA 문헌값 **미확보**) |
| Fe³⁺–Cit | 13.1 | — |
| Cu²⁺–Cit | 7.57 (출처태그 SCD2.62) | — |
| Ca²⁺–Cit | 4.87 | — |
| 시트르산 logβ₁/β₂/β₃ | 6.396 / 11.157 / 14.285 (pKa 6.40·4.76·3.13) | — |
| EDTA logβ₁…β₅ | 10.948 / 17.221 / 20.34 / 22.5 / 24.0 | — |

출처: (a) USGS PHREEQC v3 열역학 데이터베이스 `minteq.v4.dat` (Id 2819690·2319691·1509690·2819671·2319671·1509671,
각 항목 주석에 "log K source: NIST46.2"), https://raw.githubusercontent.com/usgs-coupled/phreeqc3/master/database/minteq.v4.dat
(원파일 확보, papers/phreeqc-minteq.v4.dat). NIST SRD 46(Martell & Smith) 자체는 배포 중단(nist.gov/srd/nist46 "discontinued"
확인)이라 **NIST 원표는 미확보, MINTEQ가 인용한 값을 채택**. (b) G.J. Kontoghiorghes, C.N. Kontoghiorghe, *Cells* 9, 1456
(2020), PMC7349684, https://doi.org/10.3390/cells9061456 Table 3 (EDTA: Fe³⁺ 25.1, Cu²⁺ 18.8, Zn²⁺ 16.5). (c) T. Palden,
L. Machiels, B. Onghena, M. Regadío, K. Binnemans, *RSC Adv.* 10, 42147 (2020), PMC9057912, https://doi.org/10.1039/d0ra08517k
(25 °C, μ=0.1: Fe(III)–EDTA 25.1, Fe(II)–EDTA 14.33, Cu–EDTA 18.7, Zn–EDTA 16.44).
- **두 값의 차이는 오류가 아니라 이온세기 효과다.** §6(A)에서 Davies 식(A=0.509, I=0.1)으로 I=0 값을 보정하면
  Fe–EDTA 25.13, Cu–EDTA 18.79로 OA 문헌값 25.1·18.75와 0.05 이내 일치. 재현 요약(한 줄): Davies 보정 EDTA logK 25.13/18.79 vs 문헌값 25.1/18.75 — 상대차 0.1 %·0.2 % 이내로 대조 일치(Palden et al. 2020, https://doi.org/10.1039/d0ra08517k).
- **선택성 순서 Fe³⁺ ≫ Cu²⁺ ≫ Ca²⁺**는 EDTA·시트르산 모두 동일 — 세정액이 Ca(경도 성분)에 소모되기보다 Fe·Cu를
  우선 잡는다. 단 시트르산은 EDTA보다 Cu에서 13, Fe에서 15 log 단위 약하다.

### 4.2 조건부 안정도상수 K′(pH) — 왜 킬레이트 세정은 알칼리에서 하는가
리간드가 양성자화되면 금속과 경쟁한다(Ringbom): K′ = K / α_H, α_H = 1 + Σβₙ[H⁺]ⁿ. §6(B) 재현 결과:
- pH 3: logK′ EDTA Fe/Cu/Ca = 16.1/8.9/0.8, 시트르산 7.6/2.0/−0.7 → **산성에선 시트르산이 Cu를 거의 못 잡고 Ca는 착화
  불가**(logK′<0). Fe³⁺만 여전히 착화된다.
- pH 7: EDTA 23.7/16.5/8.4, 시트르산 13.0/7.5/4.8.
- pH 11: EDTA 27.4/20.2/12.1, 시트르산 13.1/7.6/4.9 → α_H→1, 본래 logK 회복.
- Seo 2019(§5.1)의 조건(킬레이트 50 mM, pH 11)에서 유리 Cu²⁺ 분율 ≈ 1/(1+K′·C_L): EDTA 1.2×10⁻¹⁹, 시트르산
  5.4×10⁻⁷ — 둘 다 정전흡착에 쓸 유리 Cu²⁺를 사실상 소거. (Cu(OH)₂ 침전·Cu 가수분해(minteq: CuOH⁺ logK −7.497)는
  무시한 단순화 — 알칼리에서 실제 유리 Cu²⁺는 더 낮다. 절대값은 **추정**.)
- **설계 함의**: 알칼리 pH는 (a) 산화물 ζ 음전하로 입자 반발, (b) 킬레이트 K′ 극대화의 두 효과를 동시에 얻는 대신
  실리카 양이온 정전흡착이 커지므로 킬레이트가 필수라는 결론이 정량적으로 닫힌다. 산성 세정(DHF·시트르산 단독)은
  정전흡착 자체를 끄는 대신 Cu 무전해 석출 위험(§2 (iii))을 감수한다.

## 5. 세정 화학 각론과 막질별 레시피
### 5.1 Cu/Co 배선 post-CMP — 알칼리 + 킬레이트 + 부식억제, BTA 잔류 제거
1차(OA, CC-BY 본문 확인): J. Seo, S. Vegi, S.V. Babu, "Post-CMP Cleaning Solutions for the Removal of Organic
Contaminants with Reduced Galvanic Corrosion at Copper/Cobalt Interface…," *ECS J. Solid State Sci. Technol.* 8, P379
(2019), https://doi.org/10.1149/2.0011908jss.
- 시트르산·글리신·EDTA·에틸렌디아민(En)을 **각 50 mM, pH 11**에서 비교 — Cu–BTA·Co–BTA·실리카(75 nm) 제거엔 **En**이
  최선. 접촉각: 처녀 Cu/Co ≈57° → 10 mM BTA 노출 후 82–83° → En 세정 후 ≈57°(BTA 완전 제거의 지표).
- 문제는 **갈바닉 부식**: En 단독은 ΔE_corr 40 mV, Cu I_corr 123.0 µA/cm², Co I_corr 12.9 µA/cm²(Table II). 억제제
  시스테인(Cys) 0.75 mM + 요산(UA) 9.25 mM 첨가 시 ΔE_corr ≈5 mV, I_gc ≈0.7 µA/cm², Cu 6.1 / Co 8.9 µA/cm²(Table IV).
  즉 Cu/Co 세정은 "킬레이트로 잔류 제거 ↔ 부식 억제" 사이의 창(window) 설계다.
- BTA 제거의 다른 사례: Tang et al., *J. Semicond.* 36, 066001 (2015), https://doi.org/10.1088/1674-4926/36/6/066001 —
  알칼리 FA/O II 킬레이트 + FA/O I 계면활성제로 BTA·CuO·SiO₂ 입자 제거, 계면 부식 없음(**초록만 확인**, 조성 수치 미확보).
- Pourbaix 관점([[surface-chemistry-cu-w-pourbaix-passivation]] §4): 알칼리에서 Cu는 Cu₂O/CuO 부동태 영역이므로 산성보다
  안전하고, 킬레이트는 Cu(II) 종의 용해도를 올려 산화물 잔류·Cu–BTA 막을 벗겨낸다. 산성 킬레이트(시트르산 단독)는
  §4.2에서 본 대로 Cu K′가 낮고, 활성 용해 영역이라 Cu 손실 위험 → Cu 배선엔 알칼리 레시피가 표준(정성 결론).

### 5.2 RCA 세정(SC-1/SC-2)과 금속 침착의 역설
- 기원: W. Kern, "The Evolution of Silicon Wafer Cleaning Technology," *J. Electrochem. Soc.* 137, 1887 (1990),
  https://doi.org/10.1149/1.2086825 — 초록: "hot alkaline and acidic hydrogen peroxide solutions… 'RCA Standard Clean'"
  (**초록만 확인**, 원배합비·온도는 본문 미확보). 배합비의 실사용 예(OA 원문 확인): Liu et al., *Surf. Interfaces* 21,
  100690 (2020), https://doi.org/10.1016/j.surfin.2020.100690 — "NH₄OH : H₂O₂ : H₂O = 1 : 1 : 5 (SC-1) 15 min… HCl : H₂O₂ :
  H₂O = 1 : 1 : 5 (SC-2) 15 min to remove metallic contaminants"(온도 미기재). Kern 원논문의 SC-2 비(1:1:6 등)는 **미검증**.
- **SC-1(APM)**: 알칼리 + H₂O₂. 산화막 미세 식각(H₂O₂가 Si 산화, NH₄OH가 SiO₂ 용해)과 음전하 반발로 **입자·유기물**
  제거. 그러나 알칼리에서 실리카 ζ≪0 → **Fe·Zn 등 금속이 오히려 침착**한다. Anttila, Tilli, Schaekers, Claeys, *J.
  Electrochem. Soc.* 139, 1180 (1992), https://doi.org/10.1149/1.2069362 초록: "Hot APM… results in iron deposition on
  silicon… strongly dependent on the quality of the peroxide", 노화 APM에선 Zn↑, HPM(HCl/H₂O₂) 후 Fe는 "much lower",
  Cu는 공급사·용액·시간에 무관하게 일정(**초록 확인**, atoms/cm² 표값 미확보). 이것이 §3·§4의 예측(알칼리 → 양이온
  정전흡착↑, 킬레이트 없으면 침착)과 정확히 같은 방향이다.
- **SC-2(HPM)**: 산성 + 산화제. pH<IEP로 실리카 음전하를 죽이고, H⁺가 Fe³⁺·Al³⁺·Ca²⁺ 등을 이온교환으로 탈착시키며,
  H₂O₂가 Cu⁰ 석출을 막고 Cl⁻가 약한 착화제로 작용 → **금속 제거** 단계. 순서가 SC-1→SC-2인 이유는 SC-1이 남긴 금속을
  SC-2가 걷어내기 때문(Anttila 1992: "if HPM is used, all the tested chemical grades give essentially the same metal
  contamination levels").
- **희석 산 세정**: Anttila & Tilli, *J. Electrochem. Soc.* 139, 1751 (1992), https://doi.org/10.1149/1.2069488 초록 —
  HF·HCl·HNO₃·CH₃COOH를 1:100–1:10⁶으로 희석해도 Fe가 "well below the 10¹⁰ at/cm²"; 단 **HF는 Fe를 더 많이 남기면서도
  표면재결합속도는 더 낮았다**(H-종단 표면의 전기적 패시베이션 효과) — "금속 잔류량 ≠ 전기적 열화"라는 Lv2-1의 교훈과 맞닿는다.

### 5.3 산화막(STI/ILD) post-CMP — 세리아 잔류의 화학결합 절단, DHF
- 세리아는 정전기(§3)만이 아니라 **Ce–O–Si 결합**으로 붙는다([[ceria-slurry-ce-redox-selectivity]], Lv1-1 §2). 1차: J. Seo,
  A. Gowda, S.V. Babu, "Almost Complete Removal of Ceria Particles Down to 10 nm Size from Silicon Dioxide Surfaces," *ECS J.
  Solid State Sci. Technol.* 7(5) (2018), https://doi.org/10.1149/2.0131805jss — 표준 SC-1은 10 nm 세리아에 <20%, 30 nm ~58%,
  90 nm ~94% 제거에 그치지만, **등몰 H₂O₂/NH₄OH(또는 KOH) pH≈13, [HO₂⁻] 4.13–4.18 mol/L**에서 세 크기 모두 ~99%. 기구:
  고pH에서 생긴 **퍼하이드록실 HO₂⁻가 Ce–O–Si의 O–Si를 친핵치환으로 절단**(결합에너지 Ce–O 790 > Si–O 452 > O–O 210
  kJ/mol 인용). 작은 입자일수록 Ce³⁺ 표면분율↑(10 nm 26.3%, 30 nm 18.4%, 90 nm 15.0%) → 결합 사이트↑ → 제거 난도↑.
  즉 "입자 작을수록 안 떨어진다"는 Lv1-1 서술의 정량 근거.
- **DHF**: SiO₂ 자체를 수 Å~nm 식각해 흡착층째 **리프트오프**. 식각 활성종은 (HF)₂ 이합체(Verhaverbeke et al., *J.
  Electrochem. Soc.* 141, 2852 (1994), https://doi.org/10.1149/1.2059243 — **초록만 확인**, 식각률 수치 미확보). DHF pH≈1.9(§6(C))
  는 실리카 IEP 근처라 재흡착 정전인력이 없고, HF₂⁻·F⁻는 Fe³⁺·Al³⁺와 약한 착물을 만든다(minteq HF₂⁻ logK 3.75). 단 Cu 무전해
  석출 위험(§2) → DHF는 **산화막·Si 표면 전용**, Cu 노출면엔 금기.
- 산화막 레시피의 골격: (1) 알칼리 킬레이트/HO₂⁻ 세정(입자·Ce–O–Si 절단) → (2) DHF 짧게(잔류 금속 리프트오프) →
  (3) 필요시 오존수(유기물·재산화). 순서와 시간은 공정별 캘리브레이션 대상(**미검증**).

### 5.4 오존수(DIO₃) — 유기물 산화와 화학산화막 재형성
- De Smedt, Vinckier, Cornelissen, De Gendt, Heyns, *J. Electrochem. Soc.* 147, 1124 (2000), https://doi.org/10.1149/1.1393323
  초록: 오존수 Si 산화는 중성 pH 부근에서 O₃ 농도에 의존하다가 **>15 mg/L에서 농도의존 소멸**, 20–50 °C 온도효과 없음,
  로그형 성장(Fehnler식) — 즉 오존수는 자기제한적 얇은 화학산화막을 만든다(포화 두께 수치는 **미확보**).
- Claes et al., *J. Electrochem. Soc.* 148, G118 (2001), https://doi.org/10.1149/1.1346618 초록: 프탈산디옥틸·스테아르산·BHT·
  실록산·계면활성제·n-펜타데칸 단분자층을 재현성 있게 증착하고 오존 세정으로 제거 평가(MIR-FTIR·TOF-SIMS) — 오존수의
  역할은 **유기잔류(BTA·계면활성제·에어본 유기물) 산화 분해**(제거율 수치 **미확보**).
- Hattori, Osaka, Okamoto, Saga, *J. Electrochem. Soc.* 145, 3278 (1998), https://doi.org/10.1149/1.1838798 초록: 상온 매엽식
  스핀에서 **오존수 10 s ↔ DHF 10 s를 교대 반복** → 입자·금속·유기물을 짧은 시간에 제거하고 미세거칠기 증가 없음. 기구는
  "O₃로 오염물을 산화막에 가두고 → HF로 산화막째 벗김"의 반복(농도·사이클 수·atoms/cm² 수치 **미확보**).

### 5.5 막질별 요약표 (정성 — 본 노트 근거)
| 막질 | 주 오염 | 권장 화학 | 금기/주의 | 근거 |
|---|---|---|---|---|
| Cu/Co 배선 | Cu–BTA·Co–BTA, 실리카, Cu²⁺ | 알칼리(pH≈11) + 킬레이트(En 등) + Cys/UA 억제제 | 산성·DHF(Cu 용해·석출), 킬레이트 단독(갈바닉 ΔE_corr↑) | Seo 2019; §4.2 |
| W(+Fe 촉매) | Fe·K, WO₃ 잔류 | 알칼리 킬레이트 → 산성 헹굼(SC-2형) | 강산성에서 W 재산화/부식 | Anttila 1992; [[surface-chemistry-cu-w-pourbaix-passivation]] §3 (**정성, 미검증**) |
| SiO₂(STI/ILD) | 세리아(Ce–O–Si), K·Ca·Fe | 고pH H₂O₂/NH₄OH(HO₂⁻) → DHF 리프트오프 → DIO₃ | DHF 과식각(단차), 알칼리 단독은 금속 침착 | Seo 2018; Hattori 1998; §3 |
| Si(H-종단) | Fe·Cu·유기물 | DIO₃/DHF 교대, SC-2 | SC-1 마지막 사용 시 Fe 침착 | Hattori 1998; Anttila 1992 |

## 6. python 재현 — (A) Davies 이온세기 보정 (B) K′(pH) (C) IEP·DHF pH·전하 부호
```python verify
import math
# ===== (A) EDTA 안정도상수: I=0 (USGS PHREEQC minteq.v4.dat, 출처태그 NIST46.2) → Davies 보정 → I=0.1 문헌값 대조 =====
A_DH = 0.509                       # Debye-Hückel A (25°C, log10 기준) — 교과서 상수
I = 0.1                            # mol/L, PMC 문헌값 조건 (Palden 2020: 25°C, μ=0.1)
f_dav = math.sqrt(I)/(1+math.sqrt(I)) - 0.3*I
def logK_at_I(logK0, zM, zL):
    zML = zM + zL
    return logK0 - A_DH*f_dav*(zM**2 + zL**2 - zML**2)
edta_I0 = {'Fe3+': (27.7, 3), 'Cu2+': (20.5, 2), 'Ca2+': (12.42, 2)}   # minteq.v4.dat log_k (I=0)
edta_lit01 = {'Fe3+': 25.1, 'Cu2+': 18.75}   # Kontoghiorghes 2020 Table3 (25.1/18.8), Palden 2020 (25.1/18.7) — 평균 18.75
pred = {}
for m,(k0,z) in edta_I0.items():
    pred[m] = logK_at_I(k0, z, -4)
    lit = edta_lit01.get(m)
    print(f"EDTA-{m}: logK(I=0)={k0:5.2f} → Davies I=0.1 예측 {pred[m]:5.2f}"
          + (f" | 문헌(I=0.1) {lit:5.2f} | 차 {pred[m]-lit:+.2f}" if lit else " | I=0.1 OA 문헌값 미확보"))
    if lit: assert abs(pred[m]-lit) < 0.3, f"{m}: Davies 예측과 문헌 0.3 log 단위 이상 불일치"
assert pred['Fe3+'] > pred['Cu2+'] > pred['Ca2+'], "선택성 순서 Fe3+ > Cu2+ > Ca2+ 이어야"

# ===== (B) 조건부 안정도상수 K'(pH) — Ringbom α_H 보정 (I=0, minteq 양성자화 β) =====
beta_edta = [10.948, 17.221, 20.34, 22.5, 24.0]     # log β_n : n H+ + EDTA4- (minteq)
beta_cit  = [6.396, 11.157, 14.285]                 # log β_n : n H+ + Cit3- (minteq, NIST46.2)
K0 = {'EDTA': {'Fe3+': 27.7, 'Cu2+': 20.5, 'Ca2+': 12.42},
      'Cit':  {'Fe3+': 13.1, 'Cu2+': 7.57, 'Ca2+': 4.87}}  # minteq (Cu-Cit 출처태그 SCD2.62, 나머지 NIST46.2)
def log_alpha_H(betas, pH):
    return math.log10(1 + sum(10**(b - n*pH) for n, b in enumerate(betas, 1)))
Kc = {}
for pH in (3.0, 7.0, 11.0):
    aE, aC = log_alpha_H(beta_edta, pH), log_alpha_H(beta_cit, pH)
    for L, betas, aH in (('EDTA', beta_edta, aE), ('Cit', beta_cit, aC)):
        for m, k in K0[L].items():
            Kc[(L, m, pH)] = k - aH
    print(f"pH {pH:4.1f}: logα_H EDTA={aE:5.2f} Cit={aC:5.2f} | logK' EDTA Fe/Cu/Ca = "
          f"{Kc[('EDTA','Fe3+',pH)]:5.1f}/{Kc[('EDTA','Cu2+',pH)]:5.1f}/{Kc[('EDTA','Ca2+',pH)]:5.1f} | "
          f"Cit Fe/Cu/Ca = {Kc[('Cit','Fe3+',pH)]:5.1f}/{Kc[('Cit','Cu2+',pH)]:5.1f}/{Kc[('Cit','Ca2+',pH)]:5.1f}")
for L in ('EDTA','Cit'):
    for m in ('Fe3+','Cu2+','Ca2+'):
        assert Kc[(L,m,3.0)] < Kc[(L,m,7.0)] < Kc[(L,m,11.0)], "pH↑ → K'↑ (양성자 경쟁 감소) 이어야"
assert Kc[('Cit','Ca2+',3.0)] < 0 < Kc[('Cit','Fe3+',3.0)], "pH3 시트르산: Ca는 착화 불가, Fe3+는 여전히 착화"
# Seo 2019 조건(킬레이트 50 mM, pH 11)에서 유리 Cu2+ 분율 ≈ 1/(1+K'·C_L)
C_L = 0.050
for L in ('EDTA','Cit'):
    fr = 1/(1 + 10**Kc[(L,'Cu2+',11.0)]*C_L)
    print(f"  pH11, {L} 50 mM: 유리 Cu2+ 분율 ≈ {fr:.1e}")
    assert fr < 1e-5, "50 mM 킬레이트에서 유리 Cu2+는 1e-5 이하로 억제되어야"

# ===== (C) 산화물 IEP와 세정 pH에서의 표면전하 부호 =====
IEP = {'SiO2': 2.0, 'CeO2': 6.8, 'Al2O3': 9.5}   # Brugnoli 2023 (SiO2 2, CeO2 6.8), Zhang 2024 (α-Al2O3 ~9.5, 세척 후)
ceo2_range = (5.21, 9.40)                        # Ederer 2025 Table 2, 합성법별 IEP
assert ceo2_range[0] <= IEP['CeO2'] <= ceo2_range[1], "CeO2 IEP 6.8이 실측 범위 밖"
# DHF 0.5 wt% 의 pH: HF pKa 3.17 (minteq) → 약산 평형 [H+]
C_HF = 0.5/100*1.0/20.01*1000/1.0   # 0.5 wt% ≈ 5 g/L / 20.01 g/mol = 0.25 mol/L
Ka = 10**-3.17
H = (-Ka + math.sqrt(Ka**2 + 4*Ka*C_HF))/2
pH_dhf = -math.log10(H)
print(f"DHF 0.5wt%({C_HF:.3f} M) pH ≈ {pH_dhf:.2f} (HF pKa 3.17, minteq)")
assert 1.5 < pH_dhf < 2.5
def sign(ox, pH): return '+' if pH < IEP[ox] else ('0' if pH == IEP[ox] else '-')
for name, pH in (('DHF', pH_dhf), ('약산성(세리아 STI슬러리 근방)', 5.0), ('중성수', 7.0), ('SC-1/알칼리 post-CMP', 11.0)):
    print(f"  {name:20s} pH {pH:5.2f}: " + ' '.join(f"{ox}{sign(ox,pH)}" for ox in IEP))
assert sign('SiO2', pH_dhf) == '+' and sign('CeO2', pH_dhf) == '+' and sign('Al2O3', pH_dhf) == '+'
assert all(sign(ox, 11.0) == '-' for ox in IEP), "pH11에서 세 산화물 모두 음전하 → 입자-웨이퍼 정전반발"
assert sign('CeO2', 5.0) == '+' and sign('SiO2', 5.0) == '-', "pH5에서 세리아(+)·실리카(−) 이부호 → 재흡착 인력 구간"
assert sign('CeO2', 7.0) == '-', "pH7은 CeO2 IEP 6.8 바로 위 — 약음전하(반발 미약)"
print("PASS")
```
- (A) Davies 보정으로 MINTEQ(I=0) → I=0.1 예측 Fe–EDTA 25.13, Cu–EDTA 18.79; OA 문헌값 25.1·18.75와 차 +0.03/+0.04
  (0.3 log 단위 허용 내 **일치**). Ca–EDTA 예측 10.71은 I=0.1 OA 대조값을 못 구해 **미검증**으로 남긴다.
- (B) K′(pH)는 세 pH 모두 단조증가, Fe>Cu>Ca. pH 3 시트르산–Ca logK′=−0.7(착화 불가), 50 mM·pH 11에서 유리 Cu²⁺ 분율
  EDTA 1.2e-19 / 시트르산 5.4e-7 — 가수분해·침전 무시한 상한 **추정**.
- (C) DHF 0.5 wt% pH 1.90(HF pKa 3.17)에서 SiO₂·CeO₂·Al₂O₃ 전부 양전하, pH 11에서 전부 음전하, pH 5에서 CeO₂(+)/SiO₂(−)
  이부호 — §3·§5의 정성 논리와 정합. IEP 자체는 문헌 상수를 박은 것이므로 이 블록은 IEP "재현"이 아니라 IEP로부터의
  **부호 추론 검증**이다.

## 7. 한계 (정직 표기)
- Kern 1990·Hattori 1998·Anttila 1992(2편)·Mouche 1995·De Smedt 2000·Claes 2001·Verhaverbeke 1994·Tang 2015는 IOPscience
  봇 차단으로 **초록만 확인**했다. 본문의 atoms/cm² 표값·오존 농도·사이클 수·식각률·RCA 원배합 온도는 **미확보**.
- 안정도상수 1차 출처(NIST SRD 46)는 배포 중단이라 USGS PHREEQC `minteq.v4.dat`의 NIST46.2 태그 값을 채택했다. Cu–시트르산
  logK 7.57은 출처태그가 SCD2.62(IUPAC SC-Database)로 다르다. 시트르산 I=0.1 OA 문헌값은 **미확보**.
- §4.2 K′는 리간드 양성자화만 보정(금속 가수분해·수산화물 침전·혼합 착물·HCit⁻ 착물 무시). 알칼리에서 Cu(OH)₂·CuO 상과의
  경쟁은 Pourbaix 노트와 결합해 Lv3-2 모델에서 다뤄야 한다.
- §3 IEP는 벌크 분말·유리 표면값(Brugnoli·Ederer·Zhang)이며, CMP 후 실제 박막(TEOS·HDP·low-k)의 IEP·ζ(pH) 곡선은 **미확보**.
  실리카 ζ(pH) 수치 곡선도 1차 데이터를 못 구해 Lv1-1의 예시값(−20/−40/−60 mV)에 의존한다(**미검증**).
- W 막질 레시피(§5.5)는 본 노트에서 1차 출처를 확보하지 못한 **정성 추정**이다.

## 8. 구현 요청 후보(→ PROFILE.md)
- `chelation_conditional_logK(ligand, metal, pH, I)`: §6(A)(B)의 Davies+Ringbom 순수함수. 검증값: Fe–EDTA 25.1/Cu–EDTA 18.7(I=0.1).
- `oxide_surface_charge_sign(oxide, pH)` + IEP 테이블(SiO₂ 2, CeO₂ 6.8[5.2–9.4], Al₂O₃ 9.5): Lv1-1 Boltzmann 흡착모델의 입력.

## 9. 자기시험
→ [[../../agents/surface-contamination/EXAMS.md]] Lv2-2 문항 참조.
