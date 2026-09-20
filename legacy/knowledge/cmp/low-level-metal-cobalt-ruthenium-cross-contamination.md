<!-- V2-SECTION: R2-slurry | 공동: R5-wafer | 분배완료 2026-09-08 | 근거: chemistry, colloid, passivation, pourbaix, zeta | 정본: ARCHITECTURE-V2.md §3 -->
# 저농도 금속 잔류 제어·Co/Ru 신소재 오염·세정 후 재오염(cross-contamination) — 2015년 이후 리뷰

> 에이전트: surface-contamination Lv3-1 | 작성일: 2026-09-08
> 선행: [[post-cmp-adsorption-cleaning-chemistry]] [[metal-contamination-device-impact-irds-limits]]
> [[surface-chemistry-cu-w-pourbaix-passivation]] [[post-cmp-metallic-contamination-sources]]
> [[wafer-surface-metal-detection-txrf-vpdicpms-sims-xps]] [[colloid-zeta-dlvo-slurry-stability]]

## 1. 왜 필요한가 — Lv2까지의 "Cu/W + 1×10¹⁰" 그림이 깨지는 세 지점
Lv2-2까지는 (i) 흡착의 역과정으로 세정을 설계하고 (ii) ITRS FEP 스펙 1×10¹⁰ atoms/cm²를 목표로 삼았다
([[metal-contamination-device-impact-irds-limits]] §5). 그러나 2015년 이후 문헌은 세 가지를 바꾼다.
1. **배선 금속이 Cu/W에서 Co(라이너·M0/M1)와 Ru(배리어·라이너)로 확장** — Co는 Cu보다 훨씬 비(卑)하고
   Ru는 Cu보다 귀(貴)하므로 같은 세정액 안에서 갈바닉 쌍의 방향과 크기가 달라진다(§3).
2. **저농도 금속 잔류의 목표가 검출한계 근처로 내려감** — IRDS 2024는 UPW 금속을 원소별 <1 ppt(24원소, Co 포함)로
   두고, 노트 [39]에서 "Metals removal should be maintained at non-detect limits"라고 명시한다(§2, 1차 xlsx 확인).
3. **세정 장비 자체가 오염원** — PVA 브러시의 흡착·재방출(brush loading)과 세정조 carry-over가 "세정 후 재오염"의
   주경로임이 2019–2025년 논문들로 정량화되고 있다(§4).

## 2. 저농도 금속 잔류 제어 — 목표치(IRDS 2024·ITRS 2.0)와 달성 수준
### 2.1 허용치 원문 (1차: IRDS 2024 Yield Enhancement 표 파일 `papers/irds2024-ye-tables.xlsx`, irds.ieee.org)
| 항목 | 값 | 출처(표·행) |
|---|---|---|
| 게이트 스택 non-ionic metals(Ca, Fe, Ni, Cu, Zn) 표면 한계 | **2×10¹⁰ at/cm²**, 대책 DHF 또는 SC1 | Table YE6 row 15 (IRDS 2024) |
| 게이트 유전막 mobile ions(ionic metals) | 2×10¹⁰ at/cm², 대책 DI/HCl/SC2 | Table YE6 row 14 (IRDS 2024) |
| 후면·TSV·buried rail에서 게이트로 확산하는 Cu·금속이온 | 2×10¹⁰ at/cm², "New" 항목 | Table YE6 row 18 (IRDS 2024) |
| UPW 금속(Al…Zn + Pt, 24원소, **Co 포함**) | 원소별 <1 ppt, 2024–2030 동일 | Table YE3(2024) row 76 (IRDS 2024) |
| 49% HF 금속(24원소, Co 포함) POP | 20 ppt → 10 ppt로 하향 | Table YE3(2024) row 86 (IRDS 2024) |
| 29% NH₄OH 금속(Ru·Pt·Pd 포함 목록) | <0.046 → <0.031 µg/m² | Table YE3(2024) row 481 (IRDS 2024) |
| ITRS 2.0 FEP 표면 금속 스펙 | 1E10 atoms/cm² (각주 [14]) | [[metal-contamination-device-impact-irds-limits]] §5 |

- IRDS 2024 YE 본문(`papers/irds2024-ye.txt`, 49쪽)에는 "Target levels of critical metals is redefined. For some metals,
  this target level is below limits of detection of most advanced metrology"라는 문장이 있다(IRDS 2024, Challenges 절).
  즉 저농도 제어의 병목은 이제 세정 화학이 아니라 **측정**이다([[wafer-surface-metal-detection-txrf-vpdicpms-sims-xps]]).
- **정직 표기**: IRDS 2024 표 어디에도 Co·Ru **표면 잔류(atoms/cm²)** 한계는 없다. YE6 row 15의 금속 목록은 Ca, Fe, Ni,
  Cu, Zn뿐이고, Co는 UPW·약액(ppt) 목록에만, Ru는 NH₄OH 약액 목록에만 나온다. Co/Ru 표면 허용치는 **로드맵 미정의**다.

### 2.2 달성 수준 — 기능수(전해이온수)·나노버블·킬레이트
- **전해 이온수(EW)**: Yamanaka et al. 1999(Langmuir 15, doi.org/10.1021/la981153r, 초록만 확인·본문 유료). 3실 전해조로
  10 mM HCl에서 만든 양극수(anode water)에 상온 침지하면 Si 웨이퍼 위 Cu가 **>10¹² → <10¹⁰ atoms/cm²**로 제거되며,
  기구는 Cl⁻의 양극 산화로 생긴 ClO⁻의 산화력 + 산성 pH이다. 약품 사용량은 SC-2(수% HCl/H₂O₂, 60–70 °C) 대비 1/100 이하.
  음극수(cathode water)는 post-CMP SiO₂ 입자를 **>20 000개 → <100개**로 제거(환원전위 + 초음파 캐비테이션)(Yamanaka et al. 1999).
  달성치 <10¹⁰은 IRDS 2024 YE6 2×10¹⁰의 절반, ITRS FEP 1E10과 같은 오더 — §6(C)에서 배수 대조.
- **나노버블(MNB)**: Guan et al. 2025 리뷰(Nanomaterials 15, 480, doi.org/10.3390/nano15070480, PMC11990430, 본문 확인).
  CO₂ 마이크로·나노버블 세정은 잔류 CeO₂를 순수 대비 **1/10**로 줄이고(리뷰의 [104] 재인용), O₂-MNB의 제타전위가
  **−45~−34 mV**로 공기-MNB보다 음성이라 금속 이온 흡착능이 크다고 서술한다(Guan et al. 2025). 단 이 리뷰는 반도체 사례를
  2차 인용하며 atoms/cm² 수치는 없다 — **금속 잔류에 대한 MNB 효과는 정량 미검증**.
- **표면 나노버블(SN)의 한계**: Bilotto et al. 2024(Langmuir, doi.org/10.1021/acs.langmuir.4c02862, PMC11697338)는 용매-물
  교환(SWE)의 입자제거율 80–90%를 인정하면서도 "SWE가 SN을 만들고 표면을 세정한다"는 것 외에 **SN이 세정 원인이라는
  실험적 증명은 없다**고 비판한다(Bilotto et al. 2024). 산성 PS 나노입자는 SWE로 제거되지 않았다. → 기구 불명 기술.
- **킬레이트 + 억제제(Cu/Co)**: Seo, Vegi, Babu 2019(ECS JSS 8, P379, doi.org/10.1149/2.0011908jss, CC-BY)의 En 50 mM pH 11
  + Cys 0.75 mM + UA 9.25 mM 레시피는 Lv2-2 §5.1에 정리했다. 이 논문은 유기잔류·실리카 제거와 갈바닉 억제를 다루며
  **금속 잔류 atoms/cm² 값은 보고하지 않는다**(초록·본문 확인). Co 세정 후 TXRF 잔류값을 주는 OA 1차 논문은 이번 조사에서
  **확보 못 함**(Cheng et al. 2021 Colloids Surf A doi.org/10.1016/j.colsurfa.2021.127189, Zhang et al. 2025 doi.org/10.1016/j.colsurfa.2024.135721
  — 모두 유료, 초록도 미확보).

## 3. Co/Ru 신소재의 오염·부식 특이성 — 표준전위·Pourbaix·측정 E_corr
### 3.1 표준환원전위(1차 데이터: Vanýsek, "Electrochemical Series," CRC Handbook, `papers/crc-vanysek-electrochemical-series.pdf`)
| 반쪽반응 | E°/V (SHE, 25 °C) | 의미 |
|---|---|---|
| Co²⁺ + 2e → Co | **−0.28** | Cu보다 0.62 V 비(卑) → Cu/Co 쌍에서 **Co가 양극(용해)** |
| Co(OH)₂ + 2e → Co + 2OH⁻ | −0.73 | 알칼리에서 Co는 더 쉽게 산화 |
| Cu²⁺ + 2e → Cu | **0.3419** | Lv2-2 §2의 무전해 석출 논리와 동일 값 |
| Ru²⁺ + 2e → Ru | **0.455** | Cu보다 0.11 V 귀(貴) → Cu/Ru 쌍에서 **Cu가 양극** |
| Ru³⁺ + e → Ru²⁺ | 0.2487 | — |
| RuO₂ + 4H⁺ + 2e → Ru²⁺ + 2H₂O | 1.120 | 산성·고전위에서 Ru 산화물 → 가용/휘발종 경로 |
| RuO₄ + e → RuO₄⁻ | 1.00 | RuO₄(휘발·독성) 생성 영역의 상한 |
| Ti²⁺ + 2e → Ti | −1.630 | Co/Ti 쌍(라이너/배리어)에서 열역학적으로는 Ti가 양극 |
| Ta₂O₅ + 10H⁺ + 10e → 2Ta + 5H₂O | −0.750 | Ta 배리어는 산화물 부동태 |
| WO₃ + 6H⁺ + 6e → W + 3H₂O | −0.090 | [[surface-chemistry-cu-w-pourbaix-passivation]] §3 |

### 3.2 측정 부식전위 — 열역학 서열은 맞고 크기는 다르다
- **Cu/Ru (Lee et al. 2021, Sci Rep 11, doi.org/10.1038/s41598-021-00689-6, PMC8551296, 본문·표 확인)**: 0.05 M KIO₄ + 3% H₂O₂,
  pH 10.0에서 E_corr Cu **−0.27 V**, Ru **0.22 V** → ΔE_oc **0.49 V**(Table 1). 니코틴산 0.05 M 첨가 시 Cu 0.36 V, Ru 0.45 V로
  ΔE **0.09 V**; Cu Rp 5704 → 49 897 Ω·cm²(억제효율 88.57%), Cu 제거율 95.98 → 26.23 Å/30 s, 선택비 3.86 → 1.05(Lee et al. 2021).
  피리딘 고리의 π-역결합이 Cu 산화물에 선택 흡착한다는 해석. 표준전위차 0.113 V보다 측정 ΔE_oc가 4배 크다 — 산화제(IO₄⁻)가
  Ru를 더 귀하게 만드는 **혼합전위** 효과이며 §6(A)에서 "불일치"로 기록한다.
- **Ru 단독 (Xu et al. 2021, RSC Adv 12, 228, doi.org/10.1039/d1ra08243d, PMC8978706, 본문·표 확인)**: 0.15 wt% H₂O₂, pH 9에서
  Ru E_corr 0.173 V(EDA 0 mM) → 0.082 V(40 mM), J_corr 5.843×10⁻⁶ → 1.111×10⁻⁴ A/cm²(Table 1). EDA는 Ru 금속이 아니라
  **Ru 산화물(RuO₂·2H₂O, RuO₃)** 과 착물을 만들어 다공질 산화층을 남기고, Ru 표면 IEP가 4–6이라 pH 9에서 음전하인 실리카와
  반발하던 것을 EDA가 중화한다(Xu et al. 2021). MBTA 100 ppm + SDBS 300 ppm으로 Ru/Cu ΔE_corr **17 mV**, 선택비 1.13:1.
  저자들은 "ΔE_corr < 20 mV일 때만 갈바닉 부식이 제어된다"고 쓴다(Xu et al. 2021, 자체 인용 기준 — **미검증 경험칙**).
- **Ru의 고유 위험**: 산성·고전위에서 **독성·휘발성 RuO₄** 생성 — Xu et al. 2021은 이를 피하려 모든 용액을 pH 9로 고정했고,
  Adv Sci 2023 리뷰(doi.org/10.1002/advs.202207321, PMC10427378)도 같은 경고를 반복한다. 따라서 Ru 세정은 Cu의 산성
  세정(DHF·시트르산)을 그대로 쓸 수 없고 **알칼리 창**이 강제된다.
- **Cu/Co (Seo et al. 2019)**: En 50 mM pH 11에서 ΔE_corr ≈40 mV, Cys+UA 첨가로 ≈5 mV, I_gc ≈0.7 µA/cm²(Seo et al. 2019).
  표준전위차 0.62 V 대비 측정 40 mV — En이 Cu²⁺·Co²⁺를 모두 강하게 착화해 두 금속의 전위를 함께 끌어내리기 때문이다.
- **Co/Ti**: Wang et al. 2025(Mater Chem Phys, doi.org/10.1016/j.matchemphys.2024.130293)가 음이온 계면활성제(AESA)로 Co–Ti
  전위차를 줄였다고 하나 **제목·검색 스니펫만 확인, 수치 미확보**. Co 리뷰(Wang, Zhang, Tan 2025 J Mater Chem C,
  doi.org/10.1039/d5tc02573g)도 초록만 확인.

### 3.3 Co의 용해 거동 — Cu보다 약 2 pH 단위 높은 수산화물 전이 (1차: USGS PHREEQC `minteq.v4.dat`, NIST46.4 태그)
Co(OH)₂(s) + 2H⁺ = Co²⁺ + 2H₂O log K = **13.094**; Cu(OH)₂(s) + 2H⁺ = Cu²⁺ + 2H₂O log K = **8.674**(`papers/phreeqc-minteq.v4.dat`).
따라서 같은 농도 C에서 수산화물이 석출되기 시작하는 pH는 pH* = (log K − log C)/2 이고 Co가 Cu보다 (13.094−8.674)/2 = **2.21**
높다. 100 ppm 기준 Cu는 pH 5.7, Co는 pH 7.9 — 즉 **중성~약알칼리 세정액에서 Cu²⁺는 이미 Cu(OH)₂/CuO 입자로 바뀌지만
Co²⁺는 이온으로 남아 정전흡착·브러시 흡수 대상이 된다**. §6(B)에서 Bisht et al. 2022의 "Cu 전이 pH ≈6" 관찰과 대조.
Co–EDTA log K 18.17, Cu–EDTA 20.5, Co–시트르산 6.19, Cu–시트르산 7.57(minteq) — Co 착물이 Cu보다 1~2 로그 약하므로
같은 킬레이트 농도에서 Co의 유리 이온 분율이 Cu보다 크다([[post-cmp-adsorption-cleaning-chemistry]] §4.2의 K′ 논리 적용).

## 4. 세정 후 재오염(cross-contamination) — PVA 브러시·세정조·린스
### 4.1 브러시 흡착·재방출 메커니즘
- **입자 제거 자체는 롤링+유체항력**: Xu et al. 2004(JVST B 22, 2844, doi.org/10.1116/1.1815319, 초록 확인) — 34 nm SiO₂는
  브러시가 직접 들어올리지 못하고 **롤링**으로 떨어지며, 브러시–웨이퍼 사이는 평균적으로 유체윤활 영역이라 **유체역학적
  항력**이 지배적 제거력이다. → 브러시가 "닿아서" 떼는 게 아니므로, 브러시에 실린 오염물은 같은 유체막을 통해 되돌아온다.
- **incoming 브러시 자체가 오염원**: Lee et al. 2019(Polymer Testing 77, doi.org/10.1016/j.polymertesting.2019.105921, 초록 확인) —
  새 PVA 브러시에서 초음파 break-in 10분으로 0.8–4 µm 불용성 입자와 PDMS·SDS 등 가용성 유기물을 추출, 이들이 웨이퍼로 전사됨.
- **Cu 이온 → 브러시 loading (Bisht et al. 2022, ICPT 발표문, `papers/bisht2022-icpt-pva-brush-cu-ions.pdf`, 전문 확인; 동일 그룹의
  Appl Surf Sci 2025 (doi.org/10.1016/j.apsusc.2025.162858)는 초록 미확보)**:
  - 실리카(IEP 2–3)만 있을 때 브러시 loading은 pH 3에서 크고(정전 인력·수소결합) pH ≥7에서 최소(브러시·실리카 모두 음전하).
  - Cu 이온 100 ppm 침지: pH 3에서는 이온 상태라 DIW 린스로 대부분 제거되지만, **pH ≈6에서 Cu(OH)₂로 전이**(그들의 [14])해
    pH 7에서 바늘형 석출물이 브러시에 실리고, pH 11에서는 CuO 큰 입자가 된다. ICP-AES Cu 함량은 **pH 7 > 3 > 11**이며,
    pH 7·11 시료는 린스 후에도 Cu가 브러시 내부에 남는다 — **Cu(II)–PVA 착물** 형성(그들의 [15], Hojo 1974) 때문.
  - 실리카 + Cu 이온 공존: Cu 10 ppm부터 loading이 늘고 **100 ppm 이상에서 심각**. Cu²⁺가 실리카 표면에 내부권 흡착해
    Cu(II)–silica 복합체가 되어 브러시와 더 강하게 결합한다는 가설(Bisht et al. 2022).
- **W post-CMP에서의 금속 이온·브러시**: Jalalzai et al. 2025(Surfaces and Interfaces, doi.org/10.1016/j.surfin.2025.106939)는
  산화막·PVA 브러시 위 금속 이온 오염과 제거를 다루나 **제목만 확인(초록·본문 미확보)**.

### 4.2 장비 파라미터와 재오염량 (Han et al. 2025, ECS JSS 14, doi.org/10.1149/2162-8777/adcc54, 초록 확인·본문 유료)
break-in 수행, 브러시 갭 **−1.5 mm**(더 강한 접촉)까지 접근, 브러시 회전 **400 rpm**에서 잔류 ≈**100개**, 웨이퍼 회전 100 rpm,
스크럽 후 DIW 린스와 **브러시 코어를 통한 DIW 공급**, 측면 노즐 배치가 재오염을 크게 줄였다(Han et al. 2025) — 모두
"브러시에 실린 오염을 유체로 씻어내는" 조작이며 Xu et al. 2004의 유체항력 지배 결론과 정합한다.

### 4.3 세정조·약액 carry-over 와 CuO 링
Kim et al. 2017(ECS JSS 6, P542, doi.org/10.1149/2.0191708jss, OA 초록 확인): 세정 노즐 배치 때문에 약액 농도가 낮은 영역이
생기고, 거기서 유기잔류가 안 벗겨진 채 **브러시–웨이퍼 직접 고체접촉**이 일어나 cross-contamination과 CuO 링 잔류가 형성된다.
→ carry-over의 본질은 "화학 공급이 끊긴 국소 영역"이다. 비접촉 대안으로 Wortman-Otto et al. 2022(ACS Omega,
doi.org/10.1021/acsomega.2c00683, PMC9352252)는 STI post-CMP에서 브러시가 비균일 약액 전달·전단력·brush loading 결함을
만든다고 보고 초분자 세정제 + 메가소닉을 제안한다(정성, 본문 확인).

### 4.4 재흡착 억제 화학 — 이 노트의 종합
1. **pH 창을 금속별로 다시 그린다**: Cu는 pH ≳6에서 수산화물 입자(브러시 loading 주범)가 되므로 산성 린스 또는 킬레이트로
   이온 상태 유지; Co는 pH ≲8에서 이온이라 오히려 정전흡착·PVA 착물 위험 → 알칼리+킬레이트; Ru는 RuO₄ 때문에 산성 금지.
2. **킬레이트 농도는 유리 이온을 없앨 만큼**: Lv2-2 §6(B)의 유리 Cu²⁺ 분율 계산을 Co(log K 1~2 낮음)에 재적용해야 한다.
3. **브러시는 소모품이 아니라 반응기**: break-in·코어 DIW·갭 관리(Han 2025)와 브러시 컨디셔닝 용액(Bisht 2022 제안)이 필요.
4. **측정이 병목**: IRDS 2024 "below limits of detection"(§2.1) — 브러시 내부 Cu처럼 웨이퍼에 없는 저장고는 TXRF로 안 보인다.

## 5. 한계 (정직 표기)
- Co 세정 후 **atoms/cm² 실측치를 주는 1차 논문을 확보하지 못했다**. Cheng 2021·Zhang 2025·Wang 2025(Co–Ti)·Jalalzai 2025·
  Bisht 2025는 제목 또는 초록 수준이며 Elsevier 초록조차 Crossref/OpenAlex/Semantic Scholar에 없었다.
- Yamanaka 1999의 <10¹⁰ atoms/cm²는 초록 수치이고 TXRF/VPD 어느 방법인지 미확인. 나노버블의 금속 잔류 효과는 미검증.
- §3.1 표준전위는 CRC 핸드북 값(활동도 1)이며 실제 세정액의 혼합전위와 다르다 — §6(A)가 그 차이를 그대로 보여준다.
- §3.3의 Co(OH)₂ log K(13.094)는 minteq 표기상 ΔH가 0으로 비어 있어 온도 보정 불가, I=0 값이다.
- "ΔE_corr < 20 mV" 기준(Xu 2021)은 저자 인용 경험칙이며 1차 근거 미확인. Co/Ti 열역학 방향(Ti 양극)은 TiN·부동태막 때문에
  실제와 다를 수 있다(미검증).

## 6. python 재현 — (A) 갈바닉 방향·크기 (B) Co vs Cu 수산화물 전이 pH (C) 달성 잔류 vs IRDS 배수
재현 요약(한 줄): 표준전위차 Cu–Co 0.62 V·Ru–Cu 0.11 V 방향과 측정 ΔE 40 mV(Seo et al. 2019)·490 mV(Lee et al. 2021) 대조, Cu(OH)₂ 전이 pH 5.7 vs 관찰 6(Bisht et al. 2022) 대조, 달성 <1e10 atoms/cm²(Yamanaka et al. 1999) vs IRDS 2e10 배수 0.5 대조.

```python verify
import math
# ===== (A) 갈바닉 방향 — CRC Vanýsek E°(SHE) vs 측정 E_corr =====
E0 = {"Co": -0.28, "Cu": 0.3419, "Ru": 0.455, "Ti": -1.630}   # V, CRC Handbook 'Electrochemical Series' (papers/crc-vanysek-electrochemical-series.pdf)
def anode(a, b):  # 더 비(卑)한 쪽이 양극(용해)
    return a if E0[a] < E0[b] else b
assert anode("Cu", "Co") == "Co" and anode("Cu", "Ru") == "Cu" and anode("Co", "Ti") == "Ti"
dE_CuCo = E0["Cu"] - E0["Co"]; dE_RuCu = E0["Ru"] - E0["Cu"]
assert abs(dE_CuCo - 0.62) < 0.01 and abs(dE_RuCu - 0.113) < 0.005
# 측정값 대조
lee_Ecorr = {"Cu": -0.27, "Ru": 0.22}          # V, Lee et al. 2021 Table 1, 0.05 M KIO4 + 3% H2O2, pH 10 (PMC8551296)
lee_dE = lee_Ecorr["Ru"] - lee_Ecorr["Cu"]
assert abs(lee_dE - 0.49) < 0.005                # 논문 본문 ΔE_oc 0.49 V 재현
assert lee_Ecorr["Ru"] > lee_Ecorr["Cu"]         # 방향(Ru 음극·Cu 양극)은 열역학과 일치
ratio_RuCu = lee_dE / dE_RuCu                    # ≈4.3 — 크기는 불일치(산화제 IO4-의 혼합전위)
assert ratio_RuCu > 3, "측정 ΔE가 표준전위차보다 3배 이상 큼 — 열역학 값으로 크기 예측 불가(정직 기록)"
seo_dE_En, seo_dE_inh = 0.040, 0.005             # V, Seo et al. 2019 (En 50 mM pH 11 / +Cys 0.75 mM+UA 9.25 mM)
assert seo_dE_En < dE_CuCo / 10, "En 착화로 Cu/Co 측정 ΔE가 표준전위차의 1/10 미만 — 크기 불일치(착화에 의한 전위 이동)"
xu_dE = 0.017                                     # V, Xu et al. 2021 MBTA+SDBS 첨가 후 Ru/Cu
assert xu_dE < 0.020 and seo_dE_inh < 0.020       # 두 논문 모두 '억제 성공' 판정이 20 mV 미만 영역
print(f"(A) ΔE°: Cu-Co {dE_CuCo:.3f} V (Co 양극), Ru-Cu {dE_RuCu:.3f} V (Cu 양극); Lee2021 측정 {lee_dE:.2f} V = 표준의 {ratio_RuCu:.1f}배(불일치), "
      f"Seo2019 측정 {seo_dE_En*1e3:.0f}→{seo_dE_inh*1e3:.0f} mV = 표준의 {seo_dE_En/dE_CuCo:.3f}배(불일치, 착화 효과)")

# ===== (B) Co vs Cu 수산화물 전이 pH — minteq.v4.dat (NIST46.4) 용해도상수 =====
logK = {"Cu(OH)2": 8.674, "Co(OH)2": 13.094}     # M(OH)2 + 2H+ = M2+ + 2H2O, papers/phreeqc-minteq.v4.dat PHASES
MW = {"Cu": 63.546, "Co": 58.9332}
C_ppm = 100.0                                     # Bisht et al. 2022 침지 실험 농도
def pH_star(metal):
    C = C_ppm * 1e-3 / MW[metal]                  # g/L → mol/L
    return (logK[metal + "(OH)2"] - math.log10(C)) / 2
pH_Cu, pH_Co = pH_star("Cu"), pH_star("Co")
assert abs(pH_Cu - 6.0) < 0.5, f"Cu(OH)2 전이 pH {pH_Cu:.2f} — Bisht 2022 관찰 '≈6'과 0.5 이상 차이"
assert 2.0 < pH_Co - pH_Cu < 2.5                  # Co가 Cu보다 ~2.2 pH 단위 늦게 석출
sat = lambda m, pH: 10 ** (logK[m + "(OH)2"] - 2 * pH)   # mol/L
assert sat("Co", 11) / sat("Cu", 11) > 1e4        # pH 11에서도 Co2+ 용해도가 Cu2+보다 4자릿수 이상 큼
print(f"(B) 100 ppm 전이 pH: Cu {pH_Cu:.2f} (관찰 ≈6, 차 {pH_Cu-6:+.2f}), Co {pH_Co:.2f}; pH 11 포화 [Co2+] {sat('Co',11):.1e} M vs [Cu2+] {sat('Cu',11):.1e} M")

# ===== (C) 달성 잔류 vs 허용치 배수 =====
achieved = 1e10                                   # atoms/cm², Yamanaka et al. 1999 양극수 "<10^10" (상한값 채택)
before = 1e12                                     # atoms/cm², 동 논문 ">10^12"
irds2024_ye6 = 2e10                               # at/cm², IRDS 2024 Table YE6 row 15 (non-ionic metals Ca,Fe,Ni,Cu,Zn)
itrs_fep = 1e10                                   # atoms/cm², ITRS 2.0 각주[14] (Lv2-1 노트)
assert before / achieved >= 100                   # 두 자릿수 이상 저감
assert achieved / irds2024_ye6 == 0.5 and achieved / itrs_fep == 1.0
print(f"(C) 양극수 세정 {before:.0e}→<{achieved:.0e} atoms/cm² (≥{before/achieved:.0f}배 저감); IRDS2024 YE6 대비 {achieved/irds2024_ye6:.1f}배, ITRS FEP 대비 {achieved/itrs_fep:.1f}배(경계)")
```

**결과 해석(정직하게)**: (A) 갈바닉 **방향**(Co 양극, Cu/Ru 쌍에서는 Cu 양극)은 CRC 표준전위와 두 측정 논문이 일치하지만,
**크기**는 Lee 2021이 표준의 ≈4배, Seo 2019가 ≈1/15로 어긋난다 — 산화제·킬레이트가 만드는 혼합전위 때문이며 표준전위로
ΔE_corr을 예측할 수 없다(불일치를 assert로 명시). (B) minteq 용해도상수로 계산한 Cu(OH)₂ 전이 pH 5.7은 Bisht 2022의 관찰
"≈6"과 0.3 이내로 맞고, Co는 7.9로 2.2 단위 높다 — Co/Cu 세정 pH 창이 달라야 하는 정량 근거. (C) 전해 양극수의 <10¹⁰은
IRDS 2024 YE6(2×10¹⁰)의 0.5배로 만족, ITRS FEP 1E10과는 경계값 — 1999년 기술이 이미 오늘 허용치 오더에 있었고, 그래서 이후
진보는 "더 낮게"가 아니라 "검출한계 이하로·재오염 없이"라는 방향이 된 것이다.

## 7. 구현 요청 후보(→ PROFILE.md)
- `galvanic_pair_direction(metalA, metalB)` (E° 표 + 부호 판정) 와 `hydroxide_transition_pH(metal, C)` (minteq log K) — Lv3-2 잔류 예측 모델의
  "이온 상태 vs 입자 상태" 분기 입력. 검증값은 §6(A)(B) 그대로.

## 8. 자기시험
→ [[../../agents/surface-contamination/EXAMS.md]] Lv3-1 문항 참조.
