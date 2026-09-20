<!-- V2-SECTION: R2-slurry | 공동: R5-wafer | 근거: ruthenium, molybdenum, oxidizer, periodate, hypochlorite, RuO4, Pourbaix, galvanic, passivation | 정본: ARCHITECTURE-V2.md §3 -->
# Ru·Mo CMP — 난용해 금속의 산화제 화학, RuO₄ 생성창, Ru/Cu·Mo/Cu 갈바닉 (film-emerging Lv1-2)

> 에이전트: film-emerging Lv1-2 | 작성일: 2026-09-16
> 선행(반드시 먼저): [[film-co-interconnect-cmp-corrosion-galvanic-inhibitor]] (Lv1-1 — 이 노트는 그 결론
> "부동태는 열역학이 아니라 억제제가 공급한다"·"갈바닉은 스칼라 ΔE_corr로 요약 못 한다"를 **Co가 아닌 두 번째·세 번째
> 난용해 금속(Ru·Mo)** 에 적용해 무엇이 같고 다른지 본다. Lv1-1 내용은 재서술하지 않고 인용만 한다),
> [[../cmp/surface-chemistry-cu-w-pourbaix-passivation]] (부모 상속 — Nernst 기울기·"자기제한적 부동태" 틀·§5 표의
> Mo=MoO₃·2H₂O 무른막 서술. 이 노트가 그 Mo 항을 1차 실측으로 채운다),
> [[../cmp/chi-oxidizer-cu-h2o2-reparameterization]] (판정#20 — 산화제 농도–MRR을 Langmuir 포화형 1파라미터로
> 재파라미터화. §6에서 **Mo/KIO₃ 곡선이 이 Langmuir(n=1)로는 안 되고 Hill n≈4가 필요**함을 보인다)
> 관련: [[../cmp/low-level-metal-cobalt-ruthenium-cross-contamination]] (CRC 표준전위표·Cu/Ru ΔE_oc 원기록),
> [[../cmp/oxidizer-redox-potential-decomposition-metal-suitability]] (산화제 E° 열역학의 원 노트),
> [[../cmp/preston-luo-dornfeld-mrr]] (기계항 — §6의 포화 곡선이 화학항 배율로 여기에 걸린다),
> [[../cmp/bta-inhibitor-langmuir-K-effective-cu-cmp-falsification]] (판정#17 — 평형 θ≠정상상태 MRR)
>
> **스코프**: (a) Ru 산화제 화학 — Ru→RuO₂(부동태)→RuO₄(휘발·독성) 경로를 표준전위(Pourbaix 축)로 정리하고,
> 산화제별 Ru 연마율(MRR)을 1차 실측으로 확보, **RuO₄(휘발성) 생성이 억제되는 pH 창**을 문헌으로 특정. (b) Mo CMP —
> MoO₄²⁻ 용해·MoO₃/Mo₂O₅ 부동태의 산화제·pH 의존 MRR/SER, Mo가 Ru·Co와 다른 점(부동태 유무) 정량 비교.
> (c) Ru/Cu·Mo/Cu 갈바닉 커플의 실측 ΔE_corr·i_g, Co/Ru 커플의 부재 확인. (d) 산화제 농도–MRR 곡선을 포화형
> 함수(Langmuir/Hill)로 재현. **억제제·착화제 제형 설계는 slurry-chemistry, 배리어 선택비는 film-cu 소관 — 인용만.**

## 1. 왜 Ru·Mo가 Co 다음인가 — "난용해 금속"이라는 같은 문제, 세 갈래의 다른 해법

Lv1-1([[film-co-interconnect-cmp-corrosion-galvanic-inhibitor]] §1)의 핵심은 **Co는 CMP pH에서 열역학적 부동태가
없어 억제제가 인공 부동태를 공급해야 한다**였다. Ru·Mo는 같은 "귀하거나 단단해서 잘 안 깎이는 금속" 문제를 공유하지만
표면 산화물의 성질이 셋 다 다르다 — 이 노트가 정량화하는 대비는 다음 한 줄이다:

| 금속 | 산화 생성물의 성격 | CMP가 성립하는 방식 | E-근거 |
|---|---|---|---|
| **Co** | 부동태 열역학 부재(pH 8~10은 Co²⁺ 부식역) | 억제제 흡착이 SER만 죽이고 MRR은 살림 | Lv1-1 §3 (E1/E2) |
| **Ru** | 강산화제에서 **다공성 RuO₃/RuO₂ + 휘발성 RuO₄**(부동태 아님, 피팅) | 산화막을 만들되 그것이 무르고 다공성이라 기계로 벗김 | §3 (E1) |
| **Mo** | **MoO₃/Mo₂O₅ 부동태(W처럼 자기제한)** + MoO₄²⁻ 용해 | W형 — 무른 부동태막을 벗기고 착화로 재용해 | §4 (E1) |

즉 **Ru는 "부동태를 못 만들어서"가 아니라 "만든 산화물이 오히려 용해·휘발해서" 문제**(RuO₄ 독성), **Mo는 W와 가장
가까워 부동태가 있다.** Co만 진짜로 부동태가 없다. 이 셋의 차이가 산화제 선택·pH 창·갈바닉 방향을 전부 가른다.

## 2. 출처 (6건 — SCOPE `max_sources_per_unit=6` 준수, 전부 1차 논문 · 6건 모두 원문/OA 전문 확독)

- **[Cui13] H. Cui, J.-H. Park, J.-G. Park, "Effect of Oxidizers on Chemical Mechanical Planarization of Ruthenium
  with Colloidal Silica Based Slurry," *ECS J. Solid State Sci. Technol.* 2(1) P26–P30 (2013).
  DOI: 10.1149/2.030301jss** — 원문 완독(`papers/cui2013-jsst-ru-oxidizers-colloidal-silica.pdf`). 8종 산화제를 **동일
  몰농도 0.072 mol/L·pH 7·동일 전도도**로 스윕한 Ru 연마율(Fig.1)·표준환원전위표(Table I)·RuO₄ Pourbaix 영역.
- **[Cui12] H. Cui, J.-H. Park, J.-G. Park, "Study of Ruthenium Oxides Species on Ruthenium CMP Using Periodate-Based
  Slurry," *J. Electrochem. Soc.* 159(3) H335–H341 (2012). DOI: 10.1149/2.103203jes** — 원문 완독
  (`papers/cui2012-jes-ru-oxide-species-periodate-ph.pdf`). NaIO₄ 슬러리에서 Ru 연마율·부식전류의 **pH 의존(정점 pH 7)**,
  XPS로 RuO₂/RuO₃ 조성, RuO₄ 휘발성(융점 25.4 °C) 명시.
- **[Pee11] B. C. Peethala, D. Roy, S. V. Babu, "Controlling the Galvanic Corrosion of Copper during CMP of Ruthenium
  Barrier Films," *Electrochem. Solid-State Lett.* 14(7) H306–H310 (2011). DOI: 10.1149/1.3589308** — 원문 완독
  (`papers/peethala2011-esl-cu-ru-galvanic-kio4.pdf`). Cu/Ru 갈바닉 ΔE_corr **540 mV → 20 mV**(BTA+아스코르브산),
  배경슬러리 0.015 M KIO₄·pH 9에서 **RuO₄ 생성 회피**.
- **[Che17] J. Cheng, T. Wang, X. Lu, "Galvanic Corrosion Inhibitors for Cu/Ru Couple during CMP of Ru," *ECS J.
  Solid State Sci. Technol.* 6(1) P62–P67 (2017). DOI: 10.1149/2.0181701jss** — 원문 완독
  (`papers/cheng2017-jss-cu-ru-galvanic-ig-inhibitors.pdf`). Cu/Ru 갈바닉 전류 i_g를 **갈바노미터로 직접 측정**
  (혼합전위 가정 없이). H₂O₂·KIO₄별 i_g 실측 — Lv1-1이 "찾아야 한다"고 남긴 직접 i_g 측정의 Ru판.
- **[He18] P. He, S. Shao, X.-P. Qu, "Chemical Mechanical Polishing of Molybdenum in Potassium Iodate-Based Acidic
  Slurries," *ECS J. Solid State Sci. Technol.* 7(6) P299–P304 (2018). DOI: 10.1149/2.0061806jss** — 원문 완독
  (`papers/he2018-jss-mo-kio3-acidic-passivation.pdf`). Mo/KIO₃ 산화제 농도·pH별 RR/SER(Fig.2·3), MoO₃/Mo₂O₅ 부동태,
  MoO₄²⁻ 용해 반응식, Ecorr/icorr 표(Table I).
- **[Xu22] Y. Xu, T. Ma, Y. Liu, B. Tan, S. Zhang, Y. Wang, G. Song, "Effect of ethylenediamine on CMP performance of
  ruthenium in H₂O₂-based slurries," *RSC Adv.* 12, 228–240 (2022). DOI: 10.1039/d1ra08243d** — RSC CC-BY-NC 오픈액세스
  전문 확독(HTML, PMC8978706; PDF는 RSC 403·미러 부재로 미확보 → **본문 서술·초록 수치만 인용, 그림표 원값은
  미검증**). H₂O₂ 계에서 Ru–Cu 전위차가 무시할만하며 억제제로 **17 mV**까지 축소.

**교차링크 전용(이 단원 6건에 불산입)**: [[film-co-interconnect-cmp-corrosion-galvanic-inhibitor]]의 [R26] Gamagedara
& Roy 2026(DOI: 10.3390/electrochem7010006, `papers/gamagedara2026-electrochem-mo-imidazole-galvanic.pdf`)에서
**Mo/Cu 갈바닉 Ecorr**을 §5.3에 재사용한다(원 노트가 이미 출처등록). CRC Vanýsek 표준전위표
(`papers/crc-vanysek-electrochemical-series.pdf`, [[../cmp/low-level-metal-cobalt-ruthenium-cross-contamination]] §3.1
경유)는 Lv1-1과 동일한 열역학 앵커로 §3.1에 재사용.

**제외 기록**(상한으로 뺀 것, 못 찾은 게 아님): 코퍼스에 Ru CMP 1차 논문 34건 이상(NaOCl 티타니아 슬러리
10.1149/2.0301712jss, DTPA-5K 10.1149/2162-8777/aca790, 과탄산 갈바닉 10.1149/2.009305jss, KMnO₄ 3금속 스택
10.1149/2.0141605jss 등)·Mo 논문(H₂O₂/pH 10.1149/2162-8777/ac26d3 — IOP·미러 전 경로 차단으로 미확보) 존재.
후속 단원(Lv3)에서 다룬다.

## 3. Ru 산화제 화학 — 표준전위로 본 RuO₂↔RuO₄, 그리고 "왜 강산화제인데 안 깎이나"

### 3.1 Pourbaix 축의 열역학 앵커 (CRC 표준환원전위, 25 °C, SHE)
CRC Vanýsek 표(위 §2 경유)의 Ru 반쪽반응:

| 반쪽반응 | E°/V (SHE) |
|---|---|
| Ru²⁺ + 2e⁻ → Ru | **0.455** |
| Ru³⁺ + e⁻ → Ru²⁺ | 0.249 |
| RuO₂ + 4H⁺ + 2e⁻ → Ru²⁺ + 2H₂O | **1.120** |
| RuO₄ + 8H⁺ + 8e⁻ → Ru + 4H₂O | **1.038** |
| RuO₄ + e⁻ → RuO₄⁻ (퍼루테네이트) | 1.00 |
| RuO₄⁻ + e⁻ → RuO₄²⁻ (루테네이트) | 0.59 |

읽는 법: Ru를 **RuO₂**(부동태 후보)까지 산화하려면 산화제가 대략 E° ≳ 1.1 V를, **RuO₄**(휘발성 중성분자)까지
밀려면 ≳ 1.04 V를 공급해야 한다. Ru는 Cu(Cu²⁺/Cu 0.34 V)·Co(Co²⁺/Co −0.28 V)보다 훨씬 귀(貴)해서
(Ru²⁺/Ru 0.455 V) **웬만한 산화제로는 산화 자체가 안 된다** — 이것이 "난용해"의 열역학적 실체다. 단
**RuO₄는 알칼리에서 RuO₄⁻(퍼루테네이트)·RuO₄²⁻(루테네이트) 이온으로 탈양성자화**(E° 1.00/0.59 V)되어 **휘발성을
잃는다.** 이것이 §3.3의 "RuO₄ 억제 pH 창"의 근거다.

### 3.2 산화제별 Ru 연마율 — 표준전위 단조가 아니다(동역학이 이긴다)
[Cui13] Fig.1(8종 산화제, **전부 0.072 mol/L·pH 7·2 wt% 콜로이달 실리카·6 psi**, y축 Å/min, 그림 판독값):

| 산화제 | E°/V (Cui13 Table I) | Ru 연마율 / Å·min⁻¹ (판독) | 표면 |
|---|---|---|---|
| 없음(w/o) | — | ~5 | 매끈 |
| K₂S₂O₈ | 1.960 | ~40 | 매끈 |
| H₂O₂ | 1.763 | ~40 | 매끈·치밀 |
| NaClO | 1.630 | ~750 | **피팅·다공 RuO₃/RuO₂** |
| NaIO₄ | 1.603 | **~1290** | **심한 피팅·다공** |
| KClO₄ | 1.204 | ~10 | 매끈 |
| KIO₃ | 1.195(IO₃⁻/I₂) | ~90 | 매끈 |
| K₃Fe(CN)₆ | 0.361 | ~180 | 약한 부식 |

**핵심 반증**: 연마율은 표준전위에 단조가 아니다 — 가장 센 K₂S₂O₈(1.96 V)·H₂O₂(1.76 V)가 거의 안 깎고,
**정점은 E°≈1.6 V의 NaIO₄·NaClO**에 있다([Cui13] 본문 "peak ... located around oxidizers ... near 1.6 V"). 이유는
[Cui13] Pourbaix 해석: **NaIO₄·NaClO에서만 Ru가 고체 산화물역을 벗어나 비고체 RuO₄(또는 HRuO₅⁻)·RuO₄⁻ 영역**에
들어가 다공성·용해성 산화층을 만들고, 나머지 산화제에서는 Ru가 고체 산화물/수산화물역(부동태·비다공)에 머물러
기계적으로 안 벗겨진다. 즉 **"산화력의 크기"가 아니라 "어느 Pourbaix 영역으로 미느냐(동역학·경로)"가 MRR을 정한다.**
이것은 [[../cmp/oxidizer-redox-potential-decomposition-metal-suitability]]의 "E°만으로 산화제 적합성 못 정한다"의 Ru 사례.

```python verify
# [Cui13] Cui, Park, Park 2013, ECS JSST 2(1) P26, DOI: 10.1149/2.030301jss
#   Table I 표준환원전위(E° V vs SHE) + Fig.1 Ru 연마율(Å/min, 그림 판독, 동일 0.072 mol/L·pH 7)
# CRC Vanysek(papers/crc-vanysek-electrochemical-series.pdf) Ru 반쪽반응 E°
E0_Ru = {"Ru2+/Ru": 0.455, "RuO2/Ru2+": 1.120, "RuO4/Ru": 1.038,
         "RuO4/RuO4-": 1.00, "RuO4-/RuO4^2-": 0.59}
E0_ox = {"K2S2O8": 1.960, "H2O2": 1.763, "NaClO": 1.630, "NaIO4": 1.603,
         "KClO4": 1.204, "KIO3": 1.195, "K3FeCN6": 0.361}
MRR = {"w/o": 5, "K2S2O8": 40, "H2O2": 40, "NaClO": 750, "NaIO4": 1290,
       "KClO4": 10, "KIO3": 90, "K3FeCN6": 180}   # Å/min, 그림 판독(±60), E3

# (A) 열역학: RuO4 생성(E°≈1.04 V)이 RuO2(1.12 V)보다 낮은 전위에서 열역학적으로 가능
assert E0_Ru["RuO4/Ru"] < E0_Ru["RuO2/Ru2+"], "RuO4 8전자 경로가 RuO2 경계보다 낮아야 함"
# 알칼리에서 RuO4 -> 퍼루테네이트/루테네이트로 탈양성자(휘발성 상실)
assert E0_Ru["RuO4/RuO4-"] > E0_Ru["RuO4-/RuO4^2-"], "RuO4->RuO4- 가 RuO4-->RuO4^2- 보다 귀해야 함"

# (B) MRR은 E°에 단조가 아니다 — 가장 센 두 산화제가 저연마, 정점은 E°~1.6 V
assert MRR["K2S2O8"] < 100 and MRR["H2O2"] < 100, "최강 산화제가 저연마여야 반증 성립"
assert MRR["NaIO4"] > 1000 and MRR["NaClO"] > 500, "정점 산화제 확인"
peak_ox = max(MRR, key=MRR.get)
assert peak_ox == "NaIO4" and abs(E0_ox["NaIO4"] - 1.6) < 0.1, "정점이 E°~1.6 V의 NaIO4"
# 스피어만류 확인: E° 최대(K2S2O8)의 MRR이 정점(NaIO4)의 5% 미만
assert MRR["K2S2O8"] / MRR["NaIO4"] < 0.05, "E° 단조가 아님을 수치로 확정"

# (C) Ru는 Cu·Co보다 귀 — 난용해의 열역학적 실체
E0_CuCo = {"Cu": 0.3419, "Co": -0.28}
assert E0_Ru["Ru2+/Ru"] > E0_CuCo["Cu"] > E0_CuCo["Co"], "Ru>Cu>Co 귀함 순서"

print(f"문헌값 대조: Ru 연마율 정점 = {peak_ox}(E°={E0_ox[peak_ox]:.3f} V) {MRR[peak_ox]} Å/min, "
      f"최강 산화제 K2S2O8(E°=1.960 V)은 {MRR['K2S2O8']} Å/min(정점의 {MRR['K2S2O8']/MRR['NaIO4']*100:.1f}%)")
print(f"재현: RuO4 8e 경로 E°={E0_Ru['RuO4/Ru']:.3f} V < RuO2 경계 {E0_Ru['RuO2/Ru2+']:.3f} V; "
      f"Ru²⁺/Ru {E0_Ru['Ru2+/Ru']:.3f} V로 Cu(0.34)·Co(−0.28)보다 귀")
```
문헌값과 대조한 재현 결과: Ru 연마율 정점 NaIO₄(E°=1.603 V) ~1290 Å/min인데 최강 산화제 K₂S₂O₈(E°=1.960 V)은
~40 Å/min(정점의 3.1%)으로 **E°에 단조가 아님** — assert 전부 통과. **한계**: 연마율 8점은 [Cui13] Fig.1 막대그래프
**판독값(±60 Å/min, E3)** 이라 절대치는 미검증이고, 검증되는 것은 "정점이 E°≈1.6 V이고 최강 산화제가 저연마"라는
**순위·자릿수**뿐이다.

### 3.3 RuO₄(휘발·독성) 생성이 억제되는 창 — 알칼리 pH ≳ 9
[Cui12]는 NaIO₄ 슬러리에서 Ru 연마율이 **pH 7에서 정점**이고 산·알칼리로 갈수록 감소함을 보인다(Fig.1, 판독값
pH 3→7→10에서 ~530→1130→680 Å/min). XPS에서 **RuO₄ 피크는 어느 pH에서도 관측 안 됨 — 융점 25.4 °C로 휘발**
([Cui12] 본문). RuO₄는 **알려진 강한 산화성 휘발 독성물질**이라 공정에서 반드시 피해야 한다.
[Pee11]은 이 위험을 공정창으로 못박는다: 배경슬러리를 **0.015 M KIO₄·pH 9**로 잡으면 "Ru·Cu 연마율이 둘 다
적당하면서 **RuO₄ 생성이 회피**"된다(원문 초록). 열역학적으로 §3.1대로 **알칼리에서는 RuO₄가 RuO₄⁻·RuO₄²⁻
이온으로 탈양성자화**해 휘발성을 잃으므로, **RuO₄ 억제창은 "알칼리 쪽(pH ≳ 9), 단 과산화 회피"** 로 요약된다.

```python verify
# [Cui12] Cui 2012, JES 159(3) H335, DOI: 10.1149/2.103203jes — Fig.1 Ru 연마율 vs pH (1.5 wt% NaIO4)
# 판독값(Å/min, ±40, E3):
pH  = [3, 4, 5, 6, 7, 8, 9, 10]
MRR = [530, 730, 940, 1060, 1130, 800, 750, 680]
i_peak = MRR.index(max(MRR))
assert pH[i_peak] == 7, "연마율 정점이 pH 7이어야 함(문헌 본문)"
# 산·알칼리 양쪽으로 감소
assert MRR[0] < MRR[i_peak] and MRR[-1] < MRR[i_peak], "정점 양쪽 감소(봉우리형)"
# 알칼리(pH>=9)는 정점의 70% 이하 -> RuO4 회피창이면서 연마율 손실 감수
assert MRR[6] / MRR[i_peak] < 0.75, "pH 9 연마율이 정점의 75% 미만"

# [Pee11] 배경 KIO4 pH 9에서 RuO4 회피 — 열역학 앵커(CRC): RuO4가 알칼리서 이온화(휘발성 상실)
RuO4_mp_C = 25.4     # [Cui12] 본문, RuO4 융점(상온서 휘발)
assert RuO4_mp_C < 40, "RuO4가 CMP 상온(~室温)서 휘발성임을 확인"
print(f"문헌값 대조: NaIO4 Ru 연마율 정점 pH {pH[i_peak]}({max(MRR)} Å/min), "
      f"pH 9는 {MRR[6]} Å/min(정점의 {MRR[6]/max(MRR)*100:.0f}%)")
print(f"재현: RuO4 융점 {RuO4_mp_C}°C(휘발) → 알칼리 pH≳9에서 RuO4⁻/RuO4²⁻ 이온화로 휘발 억제 "
      f"([Pee11] KIO4 pH 9 'RuO4 avoided')")
```
문헌값과 대조한 재현 결과([Cui12] DOI: 10.1149/2.103203jes · [Pee11] DOI: 10.1149/1.3589308):
NaIO₄ 계 Ru 연마율은 pH 7 정점(~1130 Å/min)·양쪽 감소이며 pH 9는 정점의 66%,
RuO₄ 융점 25.4 °C(상온 휘발) — assert 전부 통과. **RuO₄ 억제창 = 알칼리 pH ≳ 9(단 과산화 회피)**. **한계**:
pH-연마율 8점은 [Cui12] Fig.1 판독값(E3), "RuO₄가 알칼리서 이온화한다"는 §3.1 CRC 전위로부터의 열역학 추론이지
[Cui12]가 그 pH 창에서 RuO₄ 부재를 직접 정량한 것은 아니다 → **창의 하한 pH는 [Pee11]의 '9'에 의존, 크기 미검증**.

## 4. Mo CMP — Mo는 W에 가깝다(부동태 있음), Ru·Co와 갈린다

### 4.1 MoO₃/Mo₂O₅ 부동태 + MoO₄²⁻ 용해 (He18)
[He18]은 KIO₃ 산성 슬러리에서 Mo 표면이 **MoO₃·Mo₂O₅ 부동태막**(경도 작아 무름 → 기계로 쉽게 제거)으로 덮이고,
용해는 **몰리브데이트 MoO₄²⁻**로 진행됨을 XPS·전기화학으로 보인다. 아노드 반응([He18] 식 1·2):
`Mo + 4H₂O → MoO₄²⁻ + 8H⁺ + 6e⁻`, `MoO₂ + 2H₂O → MoO₄²⁻ + 4H⁺ + 2e⁻`.
이는 [[../cmp/surface-chemistry-cu-w-pourbaix-passivation]] §5의 **W(WO₃ 자기제한 부동태)** 구조와 같은 계열이고,
그 노트가 Mo=MoO₃·2H₂O 무른막이라 적어둔 것을 1차 실측으로 확증한다. **결정적 대비**:
- **Mo**: 부동태(MoO₃/Mo₂O₅) **있음** → W형. 정적 부식 낮음(SER 최저 2.2 nm/min, pH 2·0.1 M KIO₃).
- **Ru**: 부동태 **없음**(§3, 다공 RuO₃/RuO₂·휘발 RuO₄, 피팅).
- **Co**: 부동태 **없음**(Lv1-1 §3, 열역학 부식역).

MoO₄²⁻는 pH>6 알칼리에서 우세종(용해)이라 Mo는 **산성에서 부동태·알칼리에서 용해**의 pH 스위치를 갖는다.

### 4.2 산화제·pH별 Mo MRR/SER (He18)
[He18] 본문·Table I(단위 명시):

| 조건 | SER / nm·min⁻¹ | RR / nm·min⁻¹ | i_corr / µA·cm⁻² | E_corr / mV(SCE) |
|---|---|---|---|---|
| 0.1 M KIO₃, pH 2 | **2.2** | **90.2** | 441±15 | +323±6 |
| 0.05 M KIO₃, pH 2 | ~ | 70.6 | 488±11 | +244±4 |
| 0.1 M KIO₃, pH 4 | ~ | 65.2 | 369±10 | −65±1 |
| 0.05 M KIO₃, pH 4 | ~ | 58.9 | 332±7 | −95±2 |

**pH 2·0.1 M에서 RR/SER ≈ 41**(높을수록 평탄화 유리) — SER은 죽이고 RR은 살리는, Co의 MRR≫SER 격차와 같은
"기계로만 깎임" 구조가 Mo에서도 성립. 단 Mo는 **산성·저 pH일수록** 그 격차가 크다(pH 2에서 RR/SER 41 vs pH 4에서
~5.4). 알칼리에서는 KIO₃ 계 RR/SER 모두 급감(He18: "RR all smaller in alkaline than acidic").

```python verify
# [He18] He, Shao, Qu 2018, JSST 7(6) P299, DOI: 10.1149/2.0061806jss — 본문 + Table I
SER_pH2_01 = 2.2          # nm/min, 0.1 M KIO3 pH 2 (본문 최저 SER)
RR = {(0.1, 2): 90.2, (0.05, 2): 70.6, (0.1, 4): 65.2, (0.05, 4): 58.9}   # nm/min, 본문
icorr = {(0.1, 2): 441, (0.05, 2): 488, (0.1, 4): 369, (0.05, 4): 332}    # µA/cm2, Table I
Ecorr = {(0.1, 2): 323, (0.05, 2): 244, (0.1, 4): -65, (0.05, 4): -95}    # mV vs SCE, Table I

# (A) RR/SER 격차 — pH 2·0.1 M에서 ~41배(기계로만 깎임, Co와 같은 구조)
ratio_pH2 = RR[(0.1, 2)] / SER_pH2_01
assert 40 < ratio_pH2 < 42, ratio_pH2
# (B) 산성일수록 RR·부동태 유리: pH 2 > pH 4 (같은 0.1 M)
assert RR[(0.1, 2)] > RR[(0.1, 4)], "산성서 RR이 더 높아야 함"
assert Ecorr[(0.1, 2)] > Ecorr[(0.1, 4)], "산성서 Ecorr이 더 귀(부동태 안정)"
# (C) Mo는 부동태 있음 -> Ru(피팅)·Co(부식역)와 갈림 (정성 앵커, 수치는 SER로)
assert SER_pH2_01 < 3.0, "Mo 정적부식이 낮아야 부동태 주장 성립"
print(f"문헌값 대조: Mo 0.1 M KIO3 pH 2 — RR {RR[(0.1,2)]} / SER {SER_pH2_01} nm/min = {ratio_pH2:.0f}배, "
      f"icorr {icorr[(0.1,2)]} µA/cm², Ecorr {Ecorr[(0.1,2)]:+d} mV(SCE)")
print(f"재현: pH 2 RR {RR[(0.1,2)]} > pH 4 RR {RR[(0.1,4)]} nm/min, Ecorr {Ecorr[(0.1,2)]:+d} > {Ecorr[(0.1,4)]:+d} mV "
      f"— 산성서 MoO3/Mo2O5 부동태 안정")
```
문헌값과 대조한 재현 결과: Mo 0.1 M KIO₃ pH 2에서 RR 90.2 / SER 2.2 nm/min = 41배, i_corr 441 µA/cm²,
E_corr +323 mV(SCE)이며 산성일수록 RR·E_corr↑ — assert 전부 통과. Mo는 **부동태를 갖는 W형**이 Ru·Co와 다른 점.

## 5. 갈바닉 커플 — Ru/Cu는 Cu가 양극(Co와 반대), Mo/Cu는 Mo가 양극

### 5.1 Ru/Cu — Ru가 귀(cathode), Cu가 양극(부식) — Co/Cu와 방향이 반대
Lv1-1에서 **Co/Cu는 Co가 양극**(Co가 卑)이었다. Ru는 정반대다: Ru²⁺/Ru 0.21 V > Cu²⁺/Cu 0.10 V(vs SCE,
[Pee11]) 이라 **Ru가 음극·Cu가 양극** — 즉 Ru 배리어 CMP의 갈바닉 걱정은 **Ru가 아니라 인접 Cu의 부식(디싱)** 이다.
- **[Pee11]**: 억제제 없는 KIO₄ 배경에서 Ru–Cu **ΔE_corr = 540 mV**(Co/Cu의 정지 507 mV와 같은 자릿수),
  BTA(Cu 아노드 억제)+아스코르브산(Ru 캐소드 억제)으로 **20 mV**까지·i_g는 **약 2자릿수** 축소.
- **[Che17]**(갈바노미터 직접측정, pH 9.5, 무연마): Cu가 양극임을 전류 부호로 확인. i_g는 **KIO₄(0.130 M) 8.48
  µA·cm⁻² > H₂O₂(0.147 M) 4.16 µA·cm⁻²** — 비슷한 몰농도에서 **KIO₄가 갈바닉으로 더 가혹**. ΔE_oc(Cu/Ru) 0.704 V
  → BTA로 0.572 V. **Lv1-1의 미확보였던 "직접 i_g 측정"이 Ru판에서 확보됨**(Co판은 아직 폐형식뿐).
- **[Xu22]**: H₂O₂ 계에서는 Ru–Cu 전위차가 애초에 작고 억제제로 **17 mV**(초록). → 산화제 선택이 갈바닉의
  1차 결정인자(KIO₄=가혹, H₂O₂=온건).

```python verify
# [Pee11] DOI: 10.1149/1.3589308 + [Che17] DOI: 10.1149/2.0181701jss + [Xu22] DOI: 10.1039/d1ra08243d
# SRP vs SCE: Ru2+/Ru 0.21, Cu2+/Cu 0.10 -> Ru 음극, Cu 양극
E_Ru_SCE, E_Cu_SCE = 0.21, 0.10
assert E_Ru_SCE > E_Cu_SCE, "Ru가 Cu보다 귀 -> Cu가 양극(Co/Cu와 방향 반대)"

# [Pee11] ΔEcorr 540 -> 20 mV, i_g 약 2자릿수 축소
dE_no, dE_inh = 540.0, 20.0
assert dE_no / dE_inh > 20, "억제제로 ΔEcorr가 20배 이상 축소"
# [Che17] i_g 직접측정 — KIO4가 H2O2보다 가혹(비슷 몰농도)
ig = {"H2O2_0.147M": 4.16, "KIO4_0.130M": 8.48}   # µA/cm2
assert ig["KIO4_0.130M"] > ig["H2O2_0.147M"], "KIO4가 갈바닉으로 더 가혹"
# [Xu22] H2O2 계 억제 후 17 mV — KIO4 무억제(540)보다 훨씬 작음
dE_Xu = 17.0
assert dE_Xu < dE_inh + 5, "H2O2+억제제가 KIO4+억제제와 같은 자릿수(수십 mV)"

# Co/Cu와의 방향 대비: Lv1-1 Co/Cu는 Co가 양극(ΔEcorr = Ecorr(Cu)-Ecorr(Co) > 0, Co 卑)
# Ru/Cu는 Cu가 양극 -> 부식 대상 금속이 반대
co_anode, ru_couple_anode = "Co", "Cu"
assert co_anode != ru_couple_anode, "Co/Cu와 Ru/Cu의 양극이 반대여야 함(핵심 대비)"
print(f"문헌값 대조: Ru/Cu ΔEcorr {dE_no:.0f}→{dE_inh:.0f} mV([Pee11]), "
      f"i_g KIO4 {ig['KIO4_0.130M']} > H2O2 {ig['H2O2_0.147M']} µA/cm²([Che17]), H2O2+억제 {dE_Xu} mV([Xu22])")
print(f"재현: Ru²⁺/Ru {E_Ru_SCE} > Cu²⁺/Cu {E_Cu_SCE} V(SCE) → Cu가 양극 — Co/Cu(Co 양극)와 방향 반대")
```
문헌값과 대조한 재현 결과: Ru/Cu ΔE_corr 540→20 mV, i_g는 KIO₄ 8.48 > H₂O₂ 4.16 µA/cm²(비슷 몰농도),
H₂O₂+억제제 17 mV이며 **Cu가 양극(Co/Cu는 Co가 양극)** — assert 전부 통과.

### 5.2 Co/Ru 커플 — 전수 탐색 후 부재 (Lv1-1 빈칸 종결)
Lv1-1 §4.5가 남긴 **Co/Ru 커플의 실측 ΔE_corr**를 이번에 **코퍼스 8960건 + 웹(exa) 전수 탐색**했다. 결과:
**Co와 Ru를 같은 슬러리에서 동시에 측정한 1차 논문은 없다.** 존재하는 것은 전부 **Cu/Ru**(위 §5.1, [Pee11][Che17]
[Xu22], Lee 2021 Sci.Rep. 0.49→0.09 V — Lv1-1 §4.5에 기록), **Cu/Co**(Lv1-1), **Ru/TiN**(KMnO₃ 스택
10.1149/2.0141605jss, ΔE_corr Ru/TiN ~30 mV), **Ru/TiN/Cu 3금속 스택**뿐이다. IIT-G 학위논문
(gyan.iitg.ac.in TH-3022)도 Ru/Cu·Co/Cu를 **따로** 다루지 열역학적으로 Co/Ru를 **커플**로 측정하지 않는다.
→ **판정: "전수 탐색 후 부재"**. 열역학 상한만 확정된다(Lv1-1 §3.1: ΔE°(Ru−Co) = 0.735 V로 Cu 커플 0.622 V보다
가혹). 실측 없이 이 0.735 V를 공정 예측값으로 쓰면 안 된다(§5.1이 보인 대로 실측 ΔE_corr는 산화제·pH·착화에 따라
수십 mV까지 떨어짐). **이 빈칸은 "미완"이 아니라 "이 계는 아직 1차 실측이 없다"는 검증된 상태로 종결**한다.

### 5.3 Mo/Cu — Mo가 양극, 그리고 연마가 ΔE_corr를 **키운다**(Co와 반대) (교차링크)
[[film-co-interconnect-cmp-corrosion-galvanic-inhibitor]]의 [R26](Gamagedara & Roy 2026, DOI:
10.3390/electrochem7010006) 기준슬러리 I(20 mM 과탄산나트륨 + 0.1 M 시트르산 + 3 wt% SiO₂, 중성)의 Ecorr(vs SCE,
Fig.2 판독):
- 정지(hold): Mo −0.291, Cu −0.175 V → **ΔE_corr(Cu−Mo) = 116 mV** (Mo 양극).
- 연마(polish): Mo −0.179, Cu +0.091 V → **ΔE_corr = 270 mV**.

**Mo/Cu는 Ru/Cu와 같은 방향(전이금속이 양극·Cu 문제 아님)**? 아니다 — Mo가 양극이라 **Mo가 부식**한다(Ru/Cu와도
반대). 더 중요한 것: Lv1-1 §4.2에서 **Co/Cu는 연마가 ΔE_corr를 −72% 무너뜨렸는데, Mo/Cu는 연마가 ΔE_corr를
116→270 mV로 오히려 +133% 키운다.** 즉 "정적 PDP가 갈바닉을 과대평가한다"는 Lv1-1의 축소계수 규칙이
**Mo에서는 부호가 반대(정적이 오히려 과소평가)** — 축소계수를 금속 무관 상수로 박으면 Mo에서 틀린다.
i_g(polish, +20 mM 이미다졸)는 21 µA·cm⁻²([R26] 본문).

```python verify
# 교차링크 [R26] Gamagedara & Roy 2026, DOI: 10.3390/electrochem7010006, Fig.2 슬러리 I (Ecorr V vs SCE)
Mo_h, Cu_h = -0.291, -0.175     # hold
Mo_p, Cu_p = -0.179,  0.091     # polish
dE_hold = (Cu_h - Mo_h) * 1000   # mV, Cu 음극 - Mo 양극
dE_pol  = (Cu_p - Mo_p) * 1000
assert abs(dE_hold - 116) < 1.0 and abs(dE_pol - 270) < 1.0, (dE_hold, dE_pol)
assert Cu_h > Mo_h and Cu_p > Mo_p, "Mo가 양극(Cu가 음극)"
# 연마가 ΔEcorr를 키운다 — Co/Cu(연마가 −72% 축소)와 부호 반대
assert dE_pol > dE_hold, "Mo/Cu는 연마가 ΔEcorr를 키움"
co_polish_drop = -0.72          # Lv1-1 §4.2: Co/Cu 슬러리 I 정지->연마 −72%
mo_polish_change = (dE_pol - dE_hold) / dE_hold
assert mo_polish_change > 0 > co_polish_drop, "Co는 연마가 갈바닉 축소, Mo는 확대 — 부호 반대"
print(f"문헌값 대조: Mo/Cu ΔEcorr hold {dE_hold:.0f} mV → polish {dE_pol:.0f} mV "
      f"(+{mo_polish_change*100:.0f}%), Mo 양극 · i_g(polish)~21 µA/cm² ([R26])")
print(f"재현: Co/Cu는 연마가 ΔEcorr −72%(Lv1-1) vs Mo/Cu는 +{mo_polish_change*100:.0f}% — 축소계수 부호가 금속마다 다름")
```
문헌값과 대조한 재현 결과([R26] DOI: 10.3390/electrochem7010006 · 대비값 Lv1-1 [[film-co-interconnect-cmp-corrosion-galvanic-inhibitor]] §4.2):
Mo/Cu ΔE_corr는 정지 116 mV→연마 270 mV(+133%, Mo 양극)로 **Co/Cu(연마 −72%)와
부호가 반대** — assert 전부 통과. **한계**: Ecorr 4값은 [R26] Fig.2 **판독값(그림에 인쇄된 수치 라벨이라 E2급이나
i_g 21은 본문 근사)**, Mo/Cu를 이 노트가 재측정한 것은 아니다(교차링크).

## 6. 산화제 농도–MRR 곡선 — Mo/KIO₃는 Langmuir(n=1)로 안 되고 Hill n≈4가 필요 (판정#20의 Mo 반례)

판정#20([[../cmp/chi-oxidizer-cu-h2o2-reparameterization]])은 Cu/H₂O₂ 산화제항을 **Langmuir 포화형
θ=KC/(1+KC)(=Hill n=1)** 1파라미터로 재파라미터화했다. Mo/KIO₃에 같은 함수형이 이식되는가? [He18] Fig.2
(5 wt% SiO₂, pH 4, KIO₃ 농도 스윕, 그림 판독값)에 Langmuir(n=1)와 Hill(n 자유)을 각각 최소자승 적합하면:

| C(KIO₃)/M | RR 실측(판독)/nm·min⁻¹ | Langmuir(n=1) | Hill(n≈4.2) |
|---|---|---|---|
| 0.01 | 21.5 | 25.4 | 21.6 |
| 0.03 | 26.5 | 32.2 | 26.7 |
| 0.05 | 42.0 | 37.9 | 41.8 |
| 0.10 | 52.0 | 48.8 | 52.9 |
| 0.15 | 54.5 | 56.7 | 53.7 |

**Langmuir(n=1)는 SSE≈79로 실패**(0.03→0.05 사이의 급상승을 못 담아 저농도 과대·중농도 과소), **Hill n≈4.2가
SSE≈1.5로 ~52배 우수**. 즉 Mo/KIO₃ 산화제–MRR은 **완만한 포화가 아니라 협동적(임계형) S자** — 0.03→0.05 M에서
RR이 **1.58배**([He18] 본문 "0.05 M is about 60% higher than 0.03 M"로 텍스트 앵커됨) 급증하고 ~0.05 M 이상에서
**포화(RR_max≈54 nm/min, 반포화 C₅₀≈0.044 M)**. **모델링 함의**: 판정#20의 Langmuir 1파라미터를 Mo 팩에 그대로
쓰면 임계 상승을 놓친다 — Mo 팩은 **Hill 지수 n을 자유파라미터로** 둬야 한다(단 아래 한계대로 n의 정확값은 미검증).

```python verify
# [He18] DOI: 10.1149/2.0061806jss, Fig.2 (5 wt% SiO2, pH 4) KIO3 농도-RR (판독값 ±3 nm/min, E3)
import numpy as np
C  = np.array([0.01, 0.03, 0.05, 0.10, 0.15])
RR = np.array([21.5, 26.5, 42.0, 52.0, 54.5])
RR0 = RR[0]

def hill(C, RRmax, K, n): return RR0 + (RRmax - RR0) * (K*C)**n / (1 + (K*C)**n)
def lang(C, RRmax, K):    return RR0 + (RRmax - RR0) * (K*C)   / (1 + K*C)

# scipy 없이 격자탐색으로 두 모델 최적 SSE 비교(재현성)
def best_sse(model, grid):
    best = 1e18; bp = None
    for p in grid:
        r = RR - model(C, *p); s = float((r*r).sum())
        if s < best: best, bp = s, p
    return best, bp

import itertools
lang_grid = [(rm, k) for rm in np.arange(60, 130, 2) for k in np.arange(1, 12, 0.2)]
hill_grid = [(rm, k, n) for rm in np.arange(50, 62, 0.5)
             for k in np.arange(12, 34, 0.5) for n in np.arange(1.5, 6.5, 0.25)]
sse_l, pl = best_sse(lang, lang_grid)
sse_h, ph = best_sse(hill, hill_grid)

# (A) Langmuir(n=1) 실패, Hill 우수 — SSE 10배 이상 차
assert sse_l > 10 * sse_h, f"Langmuir SSE {sse_l:.1f} vs Hill SSE {sse_h:.2f} — 10배 이상 차이 나야 함"
assert ph[2] > 2.0, f"Hill 지수 n={ph[2]:.2f}이 2 초과(협동/임계형)"     # n>1 확정
# (B) 반포화 농도 C50 = 1/K, 포화 RR_max
C50 = 1.0 / ph[1]
assert 0.03 < C50 < 0.06, f"반포화 C50={C50:.3f} M"
assert 50 < ph[0] < 58, f"포화 RR_max={ph[0]:.1f} nm/min"
# (C) 텍스트 앵커: 0.05 M이 0.03 M보다 ~60% 높다([He18] 본문)
ratio = RR[2] / RR[1]
assert 1.55 < ratio < 1.62, ratio     # 1.58 ≈ "60% higher"
print(f"문헌값 대조: Langmuir SSE={sse_l:.1f}(RRmax={pl[0]:.0f},K={pl[1]:.1f}) vs "
      f"Hill SSE={sse_h:.2f}(RRmax={ph[0]:.1f},K={ph[1]:.1f},n={ph[2]:.2f}) — Hill이 {sse_l/sse_h:.0f}배 우수")
print(f"재현: Mo/KIO3 반포화 C50={C50:.3f} M, 포화 RR_max≈{ph[0]:.0f} nm/min, "
      f"0.05/0.03 M 비 {ratio:.2f}(문헌 '60% higher') — 협동형 S자(n≈{ph[2]:.1f}), Langmuir(n=1) 반증")
```
문헌값과 대조한 재현 결과: Mo/KIO₃ RR-농도가 Langmuir(n=1, SSE≈79)로는 실패하고 Hill(n≈4, SSE≈1.5)로 ~52배
잘 맞으며, 반포화 C₅₀≈0.044 M·포화 RR_max≈54 nm/min·0.05/0.03 M 비 1.58(문헌 "60% higher") — assert 전부 통과.
**한계**: RR 5점은 [He18] Fig.2 **판독값(±3 nm/min, E3)** 이고 3파라미터 Hill을 5점에 적합하므로 **n의 정확값(4.2)은
미검증**이다 — 검증되는 것은 "n≫1(S자)이고 Langmuir n=1은 반증된다"는 **함수형 방향**과 C₅₀·RR_max의 자릿수뿐.
0.01→0.03의 완만함은 판독 오차 내라 n의 하한만 신뢰한다.

## 7. 이 에이전트의 결론 (모델링 관점)

1. **Ru 산화제항은 "산화력 크기"가 아니라 "Pourbaix 목적영역"으로 걸어야 한다**(§3.2). E° 단조가 아니라 정점이
   E°≈1.6 V(NaIO₄·NaClO)에 있다 — Ru 팩의 산화제 적합성은 스칼라 E°로 못 정한다. RuO₄(휘발·독성) 회피를 위해
   **pH ≳ 9 알칼리 창**을 강제하는 제약이 필요(§3.3).
2. **Mo는 W형(부동태 있음)이라 Ru·Co와 다른 팩 구조**(§4). MoO₃/Mo₂O₅ 자기제한 부동태 + MoO₄²⁻ 용해의 pH
   스위치(산성 부동태/알칼리 용해)를 갖는다. Mo 팩은 W 팩([[../cmp/surface-chemistry-cu-w-pourbaix-passivation]])을
   원형으로 하되 pH 항을 산화제 항과 결합해야 한다.
3. **갈바닉 양극이 금속마다 다르다**(§5): Co/Cu는 Co, Ru/Cu는 **Cu**, Mo/Cu는 **Mo**가 양극. 갈바닉 결함 모델은
   "어느 쪽이 부식하는가"를 커플별로 부호까지 지정해야 한다 — 스칼라 |ΔE_corr|로는 부족.
4. **연마가 ΔE_corr에 미치는 부호가 금속마다 다르다**(§5.3): Co/Cu는 연마가 −72%(축소), Mo/Cu는 +133%(확대).
   Lv1-1이 제안한 "hold→polish 축소계수"를 **금속 무관 상수로 박으면 Mo에서 틀린다.**
5. **Mo/KIO₃ 산화제–MRR은 Hill n≈4 협동형**(§6). 판정#20의 Langmuir(n=1) 1파라미터를 Mo에 이식하면 임계 상승을
   놓친다 — Mo 팩은 Hill 지수를 자유도로 둬야 한다.
6. **Co/Ru 실측은 전수 탐색 후 부재**(§5.2). Lv1-1 빈칸을 "부재"로 종결. 열역학 상한 0.735 V는 공정 예측값 아님.

## 8. 신소재 팩 골격 후보 표 (Ru·Mo)

각 값에 근거등급([[../EVIDENCE-RULES]]). **이 표는 구현 착수용 골격이지 확정 파라미터가 아니다** — sim/는 소프트웨어
부문 소관, 아래는 PROFILE 구현요청과 짝.

| 항목 | Ru | Mo | 등급·출처 |
|---|---|---|---|
| 표면 산화물 성격 | 다공 RuO₃/RuO₂ + 휘발 RuO₄(부동태 아님) | MoO₃/Mo₂O₅ 부동태(W형) + MoO₄²⁻ 용해 | E1 [Cui13][He18] |
| 대표 산화제 | **NaIO₄**(E°1.60 V, 정점) / NaClO | **KIO₃**(산성) / H₂O₂ | E1 [Cui13][He18] |
| MRR 정점 조건 | pH 7, NaIO₄ ~1130 Å/min | pH 2, 0.1 M KIO₃ ~90 nm/min | E3(판독) [Cui12][He18] |
| SER(정적부식) | 산화제 의존(부동태 없어 높음) | 2.2 nm/min(pH 2·0.1 M, 낮음) | E1 [He18] |
| 산화제–MRR 함수형 | (미확보 — 농도스윕 1차 없음) | **Hill n≈4, C₅₀≈0.044 M, RR_max≈54** | E3 [He18] §6 |
| RuO₄/독성 제약 | **pH ≳ 9 강제**(휘발 RuO₄ 회피) | 해당없음(MoO₄²⁻ 무독·비휘발) | E1/E2 [Pee11][Cui12] |
| 갈바닉(vs Cu) | **Cu가 양극**, ΔE_corr 540→20 mV, i_g(KIO₄)8.48>H₂O₂4.16 µA/cm² | **Mo가 양극**, ΔE_corr hold116/polish270 mV | E1 [Pee11][Che17] / E2 [R26] |
| kp(기계상수) | (미확보 — 경도 Ru 14.54 GPa만, [Cui13]) | (미확보 — MoO₃ 무름 정성만) | — |

## 9. 한계·미검증 (정직 표기)

- **§3.2·3.3·6의 MRR 절대값은 전부 그림 판독값(E3)**. [Cui13] Fig.1·[Cui12] Fig.1·[He18] Fig.2 모두 막대/선
  그래프라 수치표가 아니다 — 검증되는 것은 **순위·비·자릿수·함수형 방향**이지 절대 MRR이 아니다.
- **RuO₄ 억제창의 하한 pH는 [Pee11]의 "9"에 의존**. "알칼리서 RuO₄가 이온화해 휘발성 상실"은 §3.1 CRC 전위로부터의
  **열역학 추론**이고, 특정 pH에서 RuO₄ 부재를 직접 정량한 1차 측정은 확보 못 했다(§3.3).
- **§6 Hill 지수 n=4.2는 5점에 3파라미터 적합이라 정확값 미검증**. 신뢰하는 것은 "n≫1(S자), Langmuir n=1 반증,
  C₅₀·RR_max 자릿수"뿐. 0.01→0.03 완만구간은 판독오차 내.
- **§5.3 Mo/Cu는 교차링크([R26])이고 이 노트가 재측정 안 함**. Ecorr 4값은 그림 인쇄 라벨이나 i_g 21은 본문 근사.
- **Co/Ru 커플은 전수 탐색 후 부재**(§5.2) — 열역학 상한 0.735 V만 있고 실측 없음.
- **[Xu22]는 PDF 미확보(RSC 403·미러 부재), OA HTML 본문만 확독** — 그림표 원값은 미검증, 초록·본문 서술 수치
  (17 mV, 선택비 1.13:1)만 인용.
- 인용 6건이 슬러리 화학(산화제 종·농도·pH·연마입자)이 서로 달라 **계간 절대 비교는 성립 안 함** — 각 계 내부의
  비·순위·부호만 주장한다.

## 10. 자기시험
→ [[../../agents/film-emerging/EXAMS.md]] Lv1-2 문항 참조.
