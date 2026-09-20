<!-- V2-SECTION: (분배 대상 아님, tool-post-clean 독자 학습) | 작성 2026-09-13 | tool-post-clean Lv2-1 -->
# Post-CMP 세정액 화학 — 암모니아(SC-1)·시트르산·계면활성제·부식 방지제의 네 축과 상호 견제

> 에이전트: tool-post-clean Lv2-1 | 작성일: 2026-09-13
> 선행: [[post-cmp-tool-cleaning-contamination-types-sources]](Lv1-1, 오염 종류·발생원) [[post-cmp-pva-brush-scrub-contact-shear-zeta]]
> (Lv1-2, 브러시-웨이퍼 제타전위·접촉역학) [[colloid-zeta-dlvo-slurry-stability]](제타전위·DLVO 정의, 부모 상속)
> [[cu-electrochemistry-pourbaix-bta-oxidizer-inhibitor]](Cu-H₂O Pourbaix·Cu(OH)₂ 용해도곱 — 이 노트 §6(D)가 그 상수를
> 재사용해 알칼리 세정액 pH가 왜 위험역인지 교차확인한다) [[inhibitor-chelator-adsorption-isotherm-passivation]]
> (BTA/시트르산의 흡착등온식·안정도상수 — **CMP 폴리시 단계**의 억제제/킬레이트 화학이며, 이 노트는 그 다음
> 공정 단계인 **세정 단계**의 세정액 조성만 다룬다. 등온식·log K는 재기술하지 않는다)
>
> **스코프**: post-CMP 세정액(브러시 스크럽·메가소닉에 쓰이는 액상 화학)의 네 성분 — (1) 암모니아(SC-1/APM,
> TMAH 포함 알칼리원), (2) 시트르산 기반 세정액, (3) 계면활성제, (4) 부식 방지제 — 가 입자 제거·금속이온
> 오염·기판/배선 부식이라는 세 목표를 어떻게 동시에(때로는 상충하며) 다루는지를 문헌 수치로 정리한다.

## 1. 왜 네 가지를 따로 안 보고 "세정액 화학" 하나로 묶어야 하는가

Post-CMP 세정은 슬러리 잔류물(연마입자·금속이온·유기 억제제)을 제거해야 하지만, 그 제거 자체가 새로운
손상을 만들 수 있다는 점에서 CMP 폴리시 단계의 화학과 근본적으로 다른 제약을 진다 — 폴리시는 "제거율"이
목적이지만 세정은 "무손상 제거"가 목적이다. 고전적 RCA 세정의 SC-1(NH₄OH:H₂O₂:H₂O)이 그 원형이다:
알칼리 조건이 입자·유기물 제거에는 최적이지만, 동시에 Si를 에칭하고 금속이온을 재석출시키며(원래 SC-2로
제거하던 문제), Cu 배선이 노출된 post-CMP 맥락에서는 부식까지 일으킨다(Martin, Baeyens, Hub, Mertens,
Kolbesen, "Alkaline cleaning of silicon wafers: additives for the prevention of metal contamination,"
*Microelectronic Engineering* 45, 197–208, 1999, DOI: 10.1016/S0167-9317(99)00150-1 — 전문 확보,
`papers/martin1999-mee-alkaline-cleaning-additives-metal-contamination.pdf`, fitz 텍스트 추출). 이 논문의
Table 1이 이 노트의 뼈대다: SC-1은 "입자·유기물 제거"를 얻지만 "Si 에칭·표면조도·금속이온 재석출"을 대가로
치르고, 시트르산·계면활성제·부식 방지제는 각각 그 대가의 **한 축씩**을 깎는 첨가제다. 이하 §2–5에서 네
성분을 각각 보고, §6에서 넷이 만드는 트레이드오프 구조를 정리한다.

## 2. 암모니아(SC-1/APM, TMAH 포함) — 입자 제거 메커니즘과 에칭이라는 대가

- **메커니즘**: SC-1의 알칼리 조건은 Si 표면과 대부분의 연마입자(실리카·세리아·알루미나)를 모두 음전하로
  만들어 정전 반발로 재부착을 억제한다(폴리시 단계 슬러리 안정화와 같은 원리, [[colloid-zeta-dlvo-slurry-stability]]).
  다만 암모니아의 역할은 그 이상이다 — Ikarashi, Yoshino, Nakajima, Miyata, Miyazawa, Jaques, Foster, Uno,
  Takatoh, Fukuma, "Inhibition of Silica Nanoparticle Adhesion to Poly(vinyl alcohol) Surfaces by
  Ammonia-Mediated Hydration," *ACS Appl. Nano Mater.* 4, 71–83, 2021, DOI: 10.1021/acsanm.0c02308 (**초록만
  확인**, 원문 미확보)는 AFM 힘측정으로 암모니아가 PVA 브러시-실리카 입자 간 부착력을 낮추는 효과가 "정전
  상호작용만으로는 설명 안 됨"을 보이고, 분자동역학으로 암모니아가 PVA-물 계면의 수소결합망을 재배열시켜
  PVA를 국소적으로 팽윤(swelling)시키는 **입체 반발(steric repulsion)** 을 유도한다고 제시한다 — 즉 SC-1의
  세정력은 정전 반발 + 입체 반발의 이중 기구다(이 논문은 수치 힘 값을 abstract에 명시하지 않아 정성 결론만
  인용).
- **정량 트레이드오프(에칭 vs 입자제거)**: Park, Lee, Kim, "Particle Removal and Its Mechanism on Hydrophobic
  Silicon Wafer in Highly Diluted NH4OH Solutions with an Added Surfactant," *Jpn. J. Appl. Phys.* 40, 6182,
  2001, DOI: 10.1143/jjap.40.6182 (**초록만 확인**)는 SC-1과 동등 pH의 0.2 vol% NH₄OH 단독 용액에서 80°C 시
  Si 에칭률 **92 Å/min**, 계면활성제(임계미셀농도 50 ppm) 첨가 시 **2.4 Å/min**로 감소했다고 보고한다(§7
  재현에서 이 비율을 계산). 동시에 입자 제거효율(PRE)은 80°C·계면활성제 첨가 조건에서 **95% 초과**로
  보고된다 — 즉 "에칭을 줄이면서 제거효율은 유지"가 계면활성제 첨가의 존재 이유다(계면활성제 역할은 §4에서
  더 다룸).
- **TMAH로의 확장과 부식 문제**: 최근 post-Cu-CMP 세정은 SC-1의 NH₄OH 대신 **TMAH**(tetramethylammonium
  hydroxide, pH 14급 강알칼리원)를 쓰는 경우가 많다 — Goswami, Koskey, Mukherjee, Chyan, "Study of Pyrazole
  as Copper Corrosion Inhibitor in Alkaline Post Chemical Mechanical Polishing Cleaning Solution," *ECS J.
  Solid State Sci. Technol.* 3, P293–P297, 2014, DOI: 10.1149/2.0011410jss (**초록만 확인**)의 배경 설명대로,
  이 강알칼리 조건은 유기잔류·입자 제거에는 유리하지만 노출된 Cu 배선의 부식·리세스를 가속한다 — §5로
  이어지는 문제.

## 3. 시트르산 기반 세정액 — 제타전위 반전 + 금속이온 킬레이션의 이중 작용

시트르산(citric acid, pKa 3.2/4.9/6.4 — [[inhibitor-chelator-adsorption-isotherm-passivation]] §5가 이미
정리)은 CMP 폴리시 슬러리에서는 금속 착화제로 쓰이지만, 세정액에서는 **표면 제타전위 제어제**로도 작동한다.
Kim, Prasad, Kwon, Kim, Busnaina, Park, "Citric Acid and NaIO4 Based Alkaline Cleaning Solution for Particle
Removal during Post-Ru CMP Cleaning," *J. Electrochem. Soc.* 158, H1052, 2011, DOI: 10.1149/1.3621343
(**초록만 확인**)은 post-Ru-CMP 세정에서 알루미나 잔류입자 제거를 다룬다:
- 1000 ppm 시트르산 첨가만으로 **pH 10**에서 알루미나 입자와 Ru 표면이 **둘 다 음의 제타전위**를 갖게 되어
  정전 반발이 생기고, 힘-거리(force-distance) 측정으로 이 pH에서 알루미나-Ru 부착력이 최소임을 확인했다.
- 여기에 Ru 에천트인 NaIO₄를 pH 10·시트르산 용액에 0.01 M 수준으로 더하면 입자 제거효율(PRE)이 **97%**까지
  올라간다 — "정전 반발만으로는 부족하고, 표면을 살짝 들뜨게 하는(lift-off) 화학적 보조가 필요하다"는
  것이 저자들의 결론이다.
- 이 결과는 §2의 SC-1 원리(표면을 동일부호로 맞춰 반발 유도)와 같은 물리를 시트르산·중성 근처 pH에서
  재현한 것이며, 강알칼리(SC-1/TMAH, pH 9.5–14) 없이도 낮은 pH(10 vs 14)에서 유사한 반발 효과를 낼 수
  있다는 점에서 "덜 부식성인 대안"으로 제시된다(단, 이 논문은 Ru/알루미나 계에 한정되고, Cu/실리카 계에
  같은 수치가 적용된다는 근거는 이 노트에 없다 — **미검증**, 계 의존적일 가능성).

## 4. 계면활성제 — 에칭 억제·미셀 형성·재부착 방지라는 세 가지 일

§2에서 본 대로 계면활성제의 첫 번째 역할은 **Si 표면 흡착을 통한 에칭 억제**(92→2.4 Å/min, Park et al.
2001)다. 두 번째 역할은 임계미셀농도(CMC) 위·아래에서 다르게 나타난다 — Ng, Kundu, Kulkarni, Liang, "Role
of Surfactant Molecules in Post-CMP Cleaning," *J. Electrochem. Soc.* 155, H64, 2008, DOI: 10.1149/1.2806173
(**초록만 확인**)은 트라이볼로지 셋업으로 세정을 모사해, 음이온 계면활성제(alcohol ether sulfate)
농도가 CMC를 넘으면 친수성 입자 표면에 **이중층(bilayer) 미셀 흡착**이 생긴다고 보고한다 — 단분자층
흡착(입자-표면 반발 강화)과 달리 이중층은 소수성 꼬리가 바깥을 향해 재응집·재부착 경로를 만들 수 있다는
함의이며, 저자들은 이를 "계면활성제 농도를 CMC 근처로 관리해야 하는 이유"로 제시한다(정량적 최적 농도값은
abstract에 없어 **미확보**). 세 번째 역할은 §2·§3에서 이미 다룬 정전 반발의 보조 — 비이온·음이온 계면활성제
자체도 표면에 흡착해 유효 전하를 바꾸므로, 순수 무기 이온(NH₄⁺, citrate)만으로 조정한 제타전위에 추가
자유도를 준다(이 노트가 인용한 세 논문 모두 정성적으로만 동의하며, 셋을 하나의 통일된 등온식으로 엮은
문헌은 이 노트 범위에서 찾지 못했다 — **미검증**).

## 5. 부식 방지제 — 알칼리 세정액에서 Cu를 지키는 저농도 억제제

§2 말미의 문제(TMAH 강알칼리 세정이 Cu를 부식시킴)에 대한 문헌의 답이 Goswami et al. (2014, 위 인용)이다:
- 8 wt% TMAH(pH 14) 단독에서 Cu 부식은 심각하지만, **1 mM 피라졸(pyrazole)** 첨가만으로 부식 방지가 되며,
  XPS로 Cu-피라졸 착물 형성이 확인된다.
- 같은 조건에서 비교 기준으로 쓴 **10 mM BTA**(benzotriazole, [[cu-electrochemistry-pourbaix-bta-oxidizer-inhibitor]]
  §4가 이미 Cu(I)-BTA 중합막을 XPS/QCM으로 정량한 그 억제제)보다도 피라졸이 더 낮은 Cu 부식 속도(**<1
  Å/min**)를 낸다 — 즉 **10분의 1 농도**로 더 나은 보호를 얻는다.
- 접촉각 측정에서 피라졸 처리 Cu 표면이 BTA 처리 표면보다 상대적으로 친수성이었다는 보고도 있다 — 이는
  §4의 계면활성제 재부착 논리와 연결되는 지점이다(친수성 표면은 소수성 유기 잔류물의 재흡착 구동력이
  작다는 것이 일반적 콜로이드 논리이지만, 이 논문 자체가 그 인과를 직접 증명하지는 않는다 — **추정**).
- BTA가 CMP 폴리시 단계에서는 필수(패시베이션)이지만 세정 단계에서는 **제거 대상 잔류물**이 된다는 점이
  중요하다 — [[inhibitor-chelator-adsorption-isotherm-passivation]]가 다룬 "BTA 흡착"은 폴리시 중 보호막
  형성이고, 이 노트가 다루는 "세정액 속 부식 방지제"는 그 BTA를 씻어내는 동안 Cu가 무방비 상태가 되지
  않도록 **다른(또는 더 약한) 억제제로 임시 대체**하는 화학이다 — 서로 다른 공정 단계의 서로 다른 목적임을
  분명히 해둔다.

## 6. 네 화학의 상호작용 정리

| 성분 | 주 목적 | 부작용/대가 | 완화 수단 |
|---|---|---|---|
| 암모니아(NH₄OH/TMAH) | 표면 음전하화→입자 정전반발, 유기물 제거 | Si 에칭, Cu 부식(TMAH pH14 특히) | 계면활성제(에칭↓), 부식 방지제(Cu 보호) |
| 시트르산 | 저pH(≈10)에서도 표면 반발 유도 + 금속이온 킬레이션 | 부착력 최소 조건이 계(Ru/알루미나 등) 의존적 | NaIO₄ 등 보조 에천트로 PRE 보강 |
| 계면활성제 | 에칭 억제(흡착 패시베이션), 정전반발 보조 | CMC 초과 시 이중층→재응집 가능성 | 농도를 CMC 근방으로 관리 |
| 부식 방지제(피라졸 등) | Cu 부식 억제(폴리시 단계 BTA를 대체) | 폴리시 단계 BTA 자체는 세정 단계에서 잔류물 | 저농도 고효율 억제제로 치환 |

넷은 독립 축이 아니라 서로의 대가를 상쇄하도록 짝지어 쓰인다는 것이 이 표의 요지다 — 어느 하나만 강화하면
(예: 암모니아 농도만 올려 세정력을 높이면) 다른 축(에칭·부식)이 반드시 악화된다.

## 7. python 재현 — 문헌 수치 재계산 + 사촌 노트 상수 재사용 교차확인

```python verify
import math

# (A) Park, Lee, Kim (2001), JJAP 40, 6182 — NH4OH(0.2 vol%, 80C) 계면활성제 첨가 전후 Si 에칭률
etch_no_surf_A_per_min = 92.0
etch_with_surf_A_per_min = 2.4
suppression_ratio = etch_no_surf_A_per_min / etch_with_surf_A_per_min
print(f"(A) NH4OH 80C, 계면활성제(CMC 50 ppm) 첨가 시 Si 에칭 억제비 = {suppression_ratio:.1f}배 (92->2.4 A/min)")
assert 30 < suppression_ratio < 45, "문헌값(92, 2.4 A/min)으로 계산한 억제비가 예상 범위(30~45배)를 벗어남"

# (B) Kim et al. (2011), JES 158, H1052 — 1000 ppm citric acid + 0.01 M NaIO4, pH 10, PRE
PRE_percent_B = 97.0
assert PRE_percent_B > 95.0, "문헌이 보고한 최고 PRE(97%)가 저자 주장(>95%) 기준에 못 미침"

# (C) Goswami et al. (2014), ECS JSST 3, P293 — 8wt% TMAH(pH14), 동일 조건 억제제 농도 비교
conc_BTA_mM = 10.0       # 비교 기준 농도(BTA)
conc_pyrazole_mM = 1.0   # 피라졸이 더 낮은 부식속도(<1 A/min)를 내는 데 쓴 농도
conc_ratio_C = conc_BTA_mM / conc_pyrazole_mM
print(f"(C) 동일 알칼리(8wt% TMAH, pH14) 조건, 피라졸은 BTA 대비 {conc_ratio_C:.0f}분의 1 농도로 더 낮은 Cu 부식속도 달성")
assert conc_ratio_C == 10.0

# (D) [[cu-electrochemistry-pourbaix-bta-oxidizer-inhibitor]]가 CRC E0로부터 이미 유도한 Cu(OH)2 용해도곱을
#     그대로 재사용(재계산 아님) — 알칼리 세정액 pH가 이 침전 문턱보다 훨씬 위에 있음을 교차확인
logKsp_CuOH2 = -19.06   # 해당 노트 §식(4): -2*(E0_Cu2+/Cu - E0_Cu(OH)2/Cu)/k
pKw = 14.00


def pH_CuOH2_onset(activity_Cu2plus):
    return (logKsp_CuOH2 + 2 * pKw - math.log10(activity_Cu2plus)) / 2


a_Cu2_typical = 1e-4  # 같은 노트가 쓴 관례치(오더 근사, 실측 세정액 농도 아님)
pH_precip = pH_CuOH2_onset(a_Cu2_typical)
pH_SC1_lower_bound = 9.5   # Martin et al. 1999, Fig.1 EDTA 안정영역 하한(SC-1 통상 동작 pH)
pH_TMAH = 14.0             # Goswami et al. 2014

print(f"(D) Cu(OH)2 침전 개시 pH(a=1e-4 가정) = {pH_precip:.2f}; SC-1 하한 {pH_SC1_lower_bound}, TMAH {pH_TMAH}와 비교")
assert pH_SC1_lower_bound > pH_precip, "SC-1 동작 pH가 Cu(OH)2 침전 문턱보다 낮으면 '왜 부식방지제가 필요한가'라는 §5 논지가 무너짐"
assert pH_TMAH > pH_precip, "TMAH 동작 pH가 Cu(OH)2 침전 문턱보다 낮으면 §2/§5의 강알칼리-부식 연결이 무너짐"

print("PASS: (A) NH4OH+계면활성제 에칭억제 38배, (B) 시트르산계 PRE>95%, "
      "(C) 부식방지제 10배 저농도 우위, (D) 알칼리 세정 pH가 Cu(OH)2 침전 문턱을 모두 상회 — 4건 확인")
```

재현 요약(한 줄): 문헌 수치(92→2.4 Å/min, PRE 97%, BTA 10 mM vs 피라졸 1 mM)를 그대로 대입한 비율 계산이
각 논문의 정성 결론(에칭 억제·고효율 제거·저농도 부식방지)과 방향이 일치했고, 사촌 노트가 CRC E°로부터
유도한 Cu(OH)₂ 침전 pH 문턱(a=1e-4 가정 시 6.47)이 SC-1(≥9.5)·TMAH(14) 동작 pH보다 항상 낮아, "알칼리
post-CMP 세정액은 열역학적으로 Cu(OH)₂/CuO 생성역에 있으므로 부식 방지제가 구조적으로 필요하다"는 §5의
주장을 별도 계산으로 뒷받침했다.

## 8. 한계 (정직 표기)

- 본 노트가 인용한 5건의 저널 논문(Park 2001·Ikarashi 2021·Kim 2011·Goswami 2014·Ng 2008) 모두 **초록만
  확인**했다 — IOP/ACS/ECS 원문이 봇 차단되어 abstract에 명시된 수치만 인용했고, 실험 조건의 세부(온도
  프로파일, 정확한 CMC 값 등)는 원문 확인 없이는 **미확보**다.
- §3의 "저pH(시트르산 pH10)로 SC-1급 반발 효과"라는 일반화는 Kim et al. 2011의 Ru/알루미나 계 결과이며,
  Cu/실리카 등 다른 재료계에 그대로 적용된다는 근거는 이 노트에 없다(**미검증**).
- §4의 "계면활성제 CMC 초과 시 재응집 우려"는 Ng et al. 2008이 정성적으로만 제시했고, 이 노트 §6의 표에
  넣은 "완화 수단"란은 본 노트의 종합적 추론이지 단일 문헌이 그 조합을 실험으로 검증한 것은 아니다.
- §7(D)의 a=1e-4 활동도 가정은 사촌 노트([[cu-electrochemistry-pourbaix-bta-oxidizer-inhibitor]])가 쓴 관례치를
  그대로 재사용한 것으로, 실제 post-CMP 세정액 중 Cu²⁺ 농도 실측값이 아니다 — 방향성(알칼리 pH가 침전
  문턱보다 훨씬 높다) 확인용이지 정량 임계농도 주장이 아니다.
- 고용주의 사내 데이터·특정 장비/레시피는 다루지 않았다(공개 문헌 정의만 사용).

## 9. 자기시험
→ [[../../agents/tool-post-clean/EXAMS.md]] Lv2-1 문항 참조.
