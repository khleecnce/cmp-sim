# 고선택비 Poly 슬러리와 무결함(low-defect) Poly CMP — 폴리케이션 무연마재·비-Preston 문턱압력

> 에이전트: film-poly-si Lv3-1 | 작성일: 2026-09-13
> 선행: [[film-poly-si-oxide-selectivity-gate-cmp-window]] (Lv2-1 — poly:oxide 선택비의 방향 두 가지, 오버폴리시 마진 번역식),
> [[film-poly-si-3dnand-har-poly-cmp-dishing]] (Lv2-2 — 선택비↑ → 디싱↑의 역설, 억제인자 χ_down 요청),
> [[film-poly-si-alkaline-dissolution-ph-kinetics]] (Lv1-2 — OH⁻ 용해와 아민의 3축 시너지),
> [[film-poly-si-doping-grain-cmp]] (Lv1-1 — 결정립·돌기가 조도의 기원)
> 관련: [[film-nitride-selectivity-ceria-chemistry]] (나이트라이드 쪽 선택비 위계 — 이 노트는 poly:nitride 수치를 채운다),
> [[hertz-gw-contact-mechanics]] (§6 입자당 접촉압·압입깊이 검산), [[gw-nominal-vs-local-pressure]] (공칭압→asperity압),
> [[../cmp/preston-luo-dornfeld-mrr]] (§5의 "비-Preston"이 무엇에서 벗어나는가), [[../cmp/post-cmp-defect-classification-and-inspection]] (결함 7종 분류),
> [[../cmp/delta-scratch-damage-d99-oversize-particle-model]] (Δ = (d99/d99_ref)^n — 무연마재에서 이 팩터가 사라지는 이유),
> [[../cmp/lpc-scratch-density-tail-correlation]] (대입자 꼬리 → 스크래치), [[pad-3dprinted-nonporous-lowdefect-review]] (패드 쪽 저결함 접근)

## 0. 출처 (6건 — 1차 원문 전체 4건, 학회 발표논문 1건, 초록만 1건; 단원 상한 6건 준수)

1. **[1차·원문 전체 9쪽]** Penta, N. K., Dandu Veera, P. R., Babu, S. V. (2011), "Role of Poly(diallyldimethylammonium
   chloride) in Selective Polishing of Polysilicon over Silicon Dioxide and Silicon Nitride Films," *Langmuir* 27(7),
   3502–3510, DOI: 10.1021/la104257k — https://doi.org/10.1021/la104257k
   (papers/penta2011-langmuir-pdadmac-poly-selectivity.pdf, 표 1–4·본문 직접 판독). **이 단원의 중심 문헌** — poly:oxide와
   poly:nitride 선택비를 한 논문에서 동시에 주는 유일한 확보본.
2. **[1차·원문 전체 7쪽]** Penta, N. K., Dandu Veera, P. R., Babu, S. V. (2011), "Charge Density and pH Effects on
   Polycation Adsorption on Poly-Si, SiO₂, and Si₃N₄ Films and Impact on Removal During Chemical Mechanical Polishing,"
   *ACS Appl. Mater. Interfaces* 3(10), 4126–4132, DOI: 10.1021/am2010114 — https://doi.org/10.1021/am2010114
   (papers/penta2011-acsami-polycation-charge-density-poly-selectivity.pdf). 1번의 후속 — 폴리케이션 6종을 스윕해
   **전하밀도가 손잡이**임을 보인다. 초록이 이 계열을 "**a low-defect option**"으로 규정한다.
3. **[1차·원문 전체 7쪽, OA CC BY-NC-ND]** Lagudu, U. R. K., Korkmaz, S., Gowda, A., Penta, N. K., Babu, S. V. (2019),
   "Reactive Liquids for Non–Prestonian Chemical Mechanical Polishing of Polysilicon Films," *ECS J. Solid State Sci.
   Technol.* 8(5), P3040–P3046, DOI: 10.1149/2.0081905jss — https://doi.org/10.1149/2.0081905jss
   (papers/lagudu2019-ecsjss-nonprestonian-poly-reactive-liquids.pdf). **문턱압력**으로 디싱을 끄는 경로.
4. **[1차·원문 전체 8쪽]** Jeon, S., Hong, J., Hong, S., Kanade, C., Park, K., Seok, H., Kim, H., Lee, S., Kim, T. (2021),
   "Investigation of abrasive-free slurry for polysilicon buffing chemical mechanical planarization," *Mater. Sci.
   Semicond. Process.* 128, 105755, DOI: 10.1016/j.mssp.2021.105755 — https://doi.org/10.1016/j.mssp.2021.105755
   (papers/jeon2021-mssp-abrasive-free-poly-buffing.pdf). 무결함 축의 **정량 조도 데이터**(AFM Ra 4점).
5. **[학회 발표논문·전문 4쪽, DOI 없음]** Kim, E., Choi, S., Seok, H., Kang, C., Kim, T., "Mechanochemically Enhanced
   Selective Material Removal during poly-Si CMP by Nanocontact-induced Dissolution," NCCAVS CMP User Group / ICPT
   발표논문 P42 — https://nccavs-usergroups.avs.org/wp-content/uploads/2023/01/P42-EKim.pdf
   (papers/kim-nccavs-icpt-poly-si-mechanochemical-selective.pdf). SKKU + SK hynix DRAM CMP. **게재연도가 문서에
   표기돼 있지 않다**(업로드 경로가 2023-01) — 연도는 **확인 못 함**. SCOPE 가중치 0.5(학회 발표자료)로 취급하고
   메커니즘 수치는 §9(E)에서 우리가 직접 재계산해 대조한다.
6. **[초록만 — 본문 미확보, E5]** Dang, S., Xiao, C., Li, J., Jiang, Y., Franklin, S. E., Qian, L., Chen, L. (2025),
   "Achieving highly selective polishing of polysilicon over oxide and nitride films via ethylenediamine-modulated
   interfacial mechanochemistry," *J. Manuf. Process.* (2025-12), DOI: 10.1016/j.jmapro.2025.11.011 —
   https://doi.org/10.1016/j.jmapro.2025.11.011. 라이선스는 CC-BY이지만 ScienceDirect가 봇 요청을 403으로 막고
   Elsevier TDM API는 키를 요구해 **전문을 확보하지 못했다**. Crossref/OpenAlex 기탁 초록만 인용한다.

**범위 밖으로 뺀 것(찾았지만 제외)**: US10119048B1·US20120094489A1 등 "poly 제거율을 **억제**하는" 슬러리 특허군은 방향이
반대인 리플레이스먼트 게이트 공정이며 이미 [[film-poly-si-oxide-selectivity-gate-cmp-window]] §4가 다뤘다. Penta의
북챕터 "Abrasive-free and ultra-low abrasive CMP processes"(Elsevier, 2016/2022)는 SCOPE 금지 소스(교과서)에 가까워 제외.
Dandu 2010(Colloids Surf. A)·Lee/Kraft PEI 등은 §8 표에 **2차 인용**으로만 등장시키고 상한 6건에 넣지 않았다.

## 1. 왜 이 단원인가 — Lv2까지의 두 미해결 문제

Lv2-1은 "선택비를 어떻게 올리는가"(TMAH 농도 → 25:1→45:1→33:1)를, Lv2-2는 "선택비를 올리면 디싱이 커진다"는 역설을
남겼다. Lv3-1은 그 둘을 동시에 공격하는 **최신 슬러리 설계**를 본다. 축은 두 개다.

- **고선택비 축**: poly:oxide뿐 아니라 **poly:nitride**까지 동시에 확보해야 한다. FinFET/RMG 흐름에서 poly 오버버든 아래
  정지층이 산화막일 수도 나이트라이드일 수도 있기 때문이다(Penta 2011 Langmuir 서론, Lagudu 2019 서론).
- **무결함 축**: 제거율을 올리려고 고형분을 올리면 응집·대입자가 스크래치를 만든다
  ([[../cmp/lpc-scratch-density-tail-correlation]], [[../cmp/delta-scratch-damage-d99-oversize-particle-model]]).
  선택비를 올리려고 폴리머를 넣으면 유기 잔사가 세정 문제를 만든다(Kim NCCAVS 서론). 두 손잡이가 결함과 정면충돌한다.

이 단원이 확인한 답은 하나의 문장으로 요약된다: **연마입자를 빼고(무연마재/저고형분), 제거의 기계 항을 "패드–폴리머–막"
브리징으로 대체하며, 압력에 문턱을 심는다.** 아래 §2–§7이 각 조각의 1차 근거다.

## 2. 고선택비 축 ① — Penta 2011(Langmuir): poly:oxide = poly:nitride ≈ 600

### 2.1 시편·공정
CETR 폴리셔, **4 psi**, 캐리어/플래튼 90/90 rpm, 슬러리 120 mL/min, IC1000 패드, 1분 연마. 막: LPCVD poly-Si 2000 nm
(~610 °C), 열산화막 2000 nm(~900 °C), LPCVD 나이트라이드 500 nm(~790 °C). RR은 2장×16점 = 32점의 산술평균.
연마입자: 세리아 d_mean ≈ 180 nm, 콜로이달 실리카 d_mean ≈ 50 nm, 각 1 wt%. 첨가제: PDADMAC(MW ≈ 200,000) 250 ppm, pH 10.

### 2.2 표 3 (pH 10) — 이 단원의 핵심 수치
| 슬러리 | poly-Si RR (nm/min) | oxide RR (nm/min) | nitride RR (nm/min) | 연마 후 poly 접촉각 (°) |
|---|---|---|---|---|
| 1 % 세리아 | 245 ± 26 | 381 ± 20 | 86 ± 3 | 63 ± 8 |
| 1 % 세리아 + 250 ppm PDADMAC | **559 ± 30** | **1 ± 1** | **1 ± 1** | < 20 |
| modified 세리아(원심세척) | 226 ± 11 | 527 ± 22 | 156 ± 30 | 61 ± 5 |
| 1 % 실리카 | 230 ± 27 | 1 ± 1 | 1 ± 1 | 67 ± 7 |
| 1 % 실리카 + 250 ppm PDADMAC | **636 ± 69** | **1 ± 1** | **1 ± 1** | < 20 |
| modified 실리카(원심세척) | 397 ± 31 | 1 ± 1 | 1 ± 1 | 55 ± 8 |

→ **poly:oxide = poly:nitride = 559(세리아) / 636(실리카)**, 원문 결론은 "~600 over both of them". 무연마재(250 ppm
PDADMAC 수용액 단독)도 pH 10에서 poly RR ≈ 600 nm/min, oxide·nitride는 전 pH 2–10에서 측정 불가(0 nm/min)다.

**⚠ 이 선택비는 하한이다.** oxide/nitride RR이 "1 ± 1 nm/min"으로 **불확실도가 값과 같다**. 최악(RR = 2 nm/min)을 가정하면
선택비 하한은 280, 최선(RR → 0)에서는 발산한다. §9(A)에서 이 전파를 명시적으로 계산한다. Lv2-1·Lv2-2의 두 자릿수~네
자릿수 선택비와 나란히 놓을 때 **"600"을 점추정으로 쓰면 안 된다**.

### 2.3 무첨가 세리아는 선택비의 **부호**가 반대다
1 % 세리아 단독은 poly 245 / oxide 381 → **poly:oxide = 0.64**, 즉 산화막이 poly보다 빨리 깎인다(세리아-실리카 화학친화,
[[film-nitride-selectivity-ceria-chemistry]]·[[../cmp/ceria-slurry-ce-redox-selectivity]]와 같은 Ce³⁺ 논리). PDADMAC 250 ppm은
이 값을 0.64 → 559로 **869배 반전**시킨다(§9(A)). "선택비를 올린다"가 아니라 **부호를 뒤집는다**가 정확한 서술이다.

### 2.4 메커니즘 — 브리징 인력과 결합에너지 위계
저자들의 제안(원문 §Proposed Mechanism, Figs. 11–12):

1. PDADMAC의 OH⁻/Cl⁻가 표면 Si–Si를 분극시키고, 양전하 질소가 그 음의 쌍극자에 이온–쌍극자 결합한다
   (Lv1-2 §2의 Si + 4OH⁻ → Si(OH)₄ + 4e⁻ 위에 얹히는 단계).
2. PDADMAC은 **IC1000 패드에도** 흡착한다(ζ: pad IEP 3.2 → 250 ppm에서 전 pH 2–10 구간 ≥ +70 mV; 물로 헹궈도 ~+60 mV 잔존).
   poly-Si 막도 IEP 3.3 → ≥ +40 mV, 연마·헹굼 후에도 +45 mV.
3. 따라서 폴리머가 **패드와 막을 잇는 다리(bridging attraction)**를 만들고, CMP의 전단이 이 다리를 당긴다.
4. 끊어지는 것은 다리가 아니라 **밑에 있는 가장 약한 결합**이다. 원문 표 2의 결합해리에너지(kcal/mol): Si–Si 54 <
   Si–H 70 = Si–C 70 < Si–N 78 < Si–Cl 95 < Si–O 113 < Si–F 132. 즉 **Si–Si < 브리징 결합력 < Si–N/Si–O**라는 부등식이
   선택비의 정체다 — poly에서는 Si–Si가 먼저 끊어지고, 산화막·나이트라이드에서는 다리가 먼저 끊어져 아무것도 제거되지 않는다.
   §9(A)는 이 부등식이 브리징 결합력을 **54–78 kcal/mol(2.34–3.38 eV)** 구간으로 가둔다는 것만 확인한다 — 이 구간 안의
   실측값은 원문에 없다(**미검증**).

### 2.5 "자유 폴리머가 있어야 한다" — modified 입자 대조군이 증명한다
원심세척으로 자유 PDADMAC을 제거한 **modified 세리아**는 oxide 527 / nitride 156 nm/min으로 **억제가 완전히 풀린다**(무첨가
세리아보다도 높다). poly RR도 226으로 무첨가(245)와 8 % 이내로 같다. TGA: 세척 후 세리아 표면 잔류 폴리머 ~0.1 wt%,
실리카·나이트라이드 입자는 ~2 wt%. → **세리아에는 PDADMAC이 약하게 붙고 실리카에는 강하게 붙는다.** 반면 modified
실리카는 poly RR 397(무첨가 230의 1.7배)로 부분적 효과를 유지한다. 억제 메커니즘이 "입자 표면 개질"이 아니라 **자유 폴리머가
입자와 피연마막 사이 접촉을 차단하는 것**(Shimono의 PVP-세리아 관찰과 같은 구도)임을 뜻한다. §9(A)에서 assert.

pH 2의 표 4가 보조 증거다: 1 % 실리카 ζ −15 mV / oxide 13 / nitride 33 nm/min → modified 실리카 ζ +31 mV / oxide 4 /
nitride 1 nm/min. 흡착층이 남으면 정전 인력이 회복돼도 **기계적 작용이 차단된다**.

## 3. 고선택비 축 ② — Penta 2011(ACS AMI): 손잡이는 전하밀도다

같은 그룹이 250 ppm 고정, pH 2–10에서 폴리케이션 6종을 스윕했다(무연마재 수용액). pH 10 기준:

| 폴리케이션 | 전하밀도 서열(원문 §4.1) | poly-Si RR (nm/min) | oxide / nitride RR |
|---|---|---|---|
| PDADMAC · PDEE · PAAm · PEI | 최고(동률) | **500–600** | ~0 |
| PAA-DADMAC 공중합체 | 중간 | PAA < x < PDADMAC (구간만) | ~0 |
| PAA(폴리아크릴아마이드) | 최저 | **~50** | ~0 |
| (무첨가 DI water) | — | ~200 | ~0 |

읽어야 할 두 가지:
1. **전하밀도 서열과 제거율 서열이 어긋나지 않는다**(§9(B)). 저자들은 이를 마이카 실험(Rojas et al.: MAPTAC 100 % → 30 %로
   전하밀도를 낮추자 pull-off force가 ~300 → ~5 mN/m)에 기대어 "전하밀도 → pull-off force → 브리징 강도"로 해석한다.
   이 연쇄의 poly-Si 계 직접 측정(AFM pull-off)은 **원문에 없다 — 추정**.
2. **PAA는 무첨가보다도 poly를 4배 억제한다**(200 → 50 nm/min). 즉 폴리머 첨가 = 가속이 아니다. 전하밀도가 낮으면 같은
   폴리머 골격이 **억제제**로 뒤집힌다 — §4의 PEG(비이온) 억제와 같은 계열의 현상이다.

초록이 이 계열을 "**These solutions offer a low-defect option for the processing of emerging FinFET devices**"로 규정한
것이 이 단원 제목의 문헌 근거다. 다만 **이 논문에도 결함 계수 데이터는 없다** — "무연마재이므로 연마입자 유래 결함이 없다"는
논리적 주장이며, 실측 결함 데이터는 §4의 Jeon 2021 조도가 이 노트가 확보한 유일한 정량치다.

## 4. 무결함 축 ① — Jeon 2021: 무연마재 + PEG 패시베이션의 조도 정량

대상 공정은 **poly 버핑 CMP**(어닐 후 결정립계 돌기 제거 + 잔류입자 제거). LPCVD poly-Si 200 nm, 250 ppm PDADMAC에
PEG(MW 1000)를 0–10000 ppm 첨가.

AFM Ra (5 × 5 µm, 원문 §3.3):

| 조건 | Ra (nm) |
|---|---|
| 연마 전(어닐 후 돌기) | 3.58 |
| 1 wt% 실리카 슬러리 | 0.94 (돌기 잔존 + **잔류 실리카 입자 관찰됨**) |
| 250 ppm PDADMAC (무연마재) | 0.52 |
| 250 ppm PDADMAC + 750 ppm PEG | **0.42** |

→ PDADMAC 대비 **19.2 %**, 실리카 슬러리 대비 **55.3 %** 개선(§9(D)에서 재계산 일치). **무연마재가 연마재보다 조도가 낮다**는
직접 대조가 이 논문의 값어치다 — §2·§3의 "무연마재이므로 결함이 적을 것"이라는 논리 주장을 처음으로 수치로 받친다.

**메커니즘**: PEG가 poly-Si 표면에 흡착해 패시베이션층을 만들고 PDADMAC의 접근을 방해한다(ATR-FTIR·XPS·접촉각·ζ). 정적
식각량은 PEG 첨가로 207 Å로 떨어지고 5000–10000 ppm에서 ~22 Å까지 억제된다.

**양날이다**: PEG 1000 ppm을 넘기면 Ra가 다시 0.52 nm 위로 **올라간다** — 억제가 너무 강해 돌기가 다 제거되지 않기 때문이다.
즉 조도 최적점(750 ppm)은 "충분히 억제하되 돌기는 깎을 만큼"의 좁은 창이며, 이것은 §5의 문턱압력과 **같은 형태의 설계**다
(억제층을 어떤 조건에서 깨느냐).

## 5. 무결함 축 ② — Lagudu 2019: 압력에 문턱을 심어 디싱을 끈다

Lv2-2가 남긴 역설("선택비를 올리면 D_ss → d_max")에 대한 이 문헌의 답은 **선택비가 아니라 압력 응답을 바꾸는 것**이다.

### 5.1 관측
GnP Poli-500, 87/93 rpm, 200 mL/min, IC1000 k-groove, 1–4 psi. 네이티브 산화막은 1 wt% 실리카 pH 3.5 · 1 psi 예비연마로 제거.

- 250 ppm PDADMAC / DADMAC / 구아니딘 카보네이트(GC) 단독: 1–4 psi에서 RR이 **거의 선형** → Prestonian. 1·2 psi 실측은
  80–270 nm/min 구간.
- 250 ppm Brij 35(비이온 계면활성제) 첨가 @1 psi: RR 26 nm/min — 억제되지만 0은 아니다.
- 250 ppm **CPB**(cetylpyridinium bromide, 양이온 계면활성제) @1 psi: **0 nm/min**. 그러나 100·50 ppm에서도 1–4 psi
  **전 구간이 0** — 과억제로 공정 자체가 불가능하다.
- **25 ppm CPB**에서만 원하는 비-Preston 거동: 문턱 아래 ~0, 문턱 위에서 급상승. 4 psi에서 세 아민 모두 300–350 nm/min,
  **문턱압력은 PDADMAC 1.5 / DADMAC 2.5 / GC 1.0 psi**로 아민 종류가 문턱을 옮긴다.

### 5.2 메커니즘
CPB가 poly-Si에 강하게 흡착해 패시베이션한다. 압력이 문턱을 넘으면 패드가 CPB–poly 결합을 끊고, 그제서야 PDADMAC의 질소가
분극된 Si–Si의 음의 쌍극자에 접근한다(§2.4의 브리징이 그 위에서 작동). 즉 **문턱압력 = CPB 탈착에 필요한 기계적 일**이며,
CPB 농도가 그 문턱을 이동시킨다(25 ppm에서 유한, ≥50 ppm에서 4 psi로도 못 넘음).

### 5.3 왜 이것이 무결함·저디싱인가 — 이 노트의 유도
Preston([[../cmp/preston-luo-dornfeld-mrr]])은 MRR = K_p·P·V로 **P → 0에서만 MRR → 0**이다. 패턴 웨이퍼에서 up 영역이
평탄화된 뒤에도 down(트렌치) 영역에는 유한한 압력이 남으므로 디싱이 계속 자란다 — Lv2-2 §2.3의 "단차 재성장"이 바로 그것이다.
문턱형 슬러리는 **MRR = k(P − P_th)⁺** 이므로 down 영역 압력이 P_th 아래로 떨어지는 순간 제거가 **정확히 0**이 된다.
Lv2-2 PROFILE [P2]가 요청한 "χ_down ∈ [0,1] 화학 억제 인자"는, 이 문헌에서 **압력 문턱이라는 물리적 형태**로 실체가 있다.

공정창을 계산해 보면(§9(C)): up 영역 압력증폭 f를 Sorooshian 2004(DOI 10.1149/1.1785933, STI 산화막 초록, 밀도 50 %에서
P_eff/P = 1.7 — **E5 전이, 방향만**)로 잡을 때, PDADMAC+CPB(P_th = 1.5 psi)의 공칭압 창은 **0.88–1.50 psi**다. 이 창 안에서는
up이 깎이고 down은 0이다. 창 폭이 문턱의 41 %에 불과하므로 **압력 제어 정밀도가 곧 디싱 성능**이라는 함의가 나온다.

### 5.4 문턱-Preston 모델의 자기정합 검사
4 psi RR(300–350)과 문턱압력으로 기울기 k = RR/(4 − P_th)를 역산하면 PDADMAC 130, DADMAC 217, GC 108 nm/min/psi다.
CPB 없는 Prestonian RL의 기울기 구간(80–135 nm/min/psi, 1·2 psi 실측 80–270에서 원점통과 가정 — Lagudu et al. 2019, DOI: 10.1149/2.0081905jss)과 대조하면 **PDADMAC과
GC는 구간 안, DADMAC은 상한을 60 % 초과**한다(§9(C)). 즉 "CPB는 Preston 직선을 오른쪽으로 평행이동시킬 뿐"이라는 단순
해석은 PDADMAC·GC에서만 성립하고 DADMAC에서는 깨진다 — **원인 미상**(그래프를 판독하지 않고 서술 구간만 썼다는 한계 포함,
§10).

## 6. 저고형분 반연마재 대안 — Kim et al. (NCCAVS/ICPT P42)과 Hertz 검산

무연마재 노선의 경쟁 노선은 **고형분을 극단적으로 낮추고 기계 항을 나노접촉 유발 용해로 대체**하는 것이다. SKKU + SK hynix의
이 발표논문은 실리카 0.1 wt% + TBAF(테트라부틸암모늄 플루오라이드) 조합으로 poly:oxide **선택비 > 420**, MRR **50배** 향상,
슬러리의 **99.8 % 이상이 물**이라고 보고한다. 논리는 (i) 국소 압력이 Si 격자를 왜곡시켜 결합에너지를 낮추고(Morse 퍼텐셜 +
Arrhenius), (ii) F⁻ 치환이 쉬워지며, (iii) 알칼리 조건에서 불소는 대부분 단일불소로 존재해 **산화막은 HF₂⁻/H₂F₂ 없이는 안
깎인다**는 것 — Lv1-2 §3의 "Si는 OH⁻로 깎이고 SiO₂는 활성화에너지가 더 높다"와 같은 계열의 화학적 선택비다.

**우리가 검산한 것(§9(E))** — 발표논문의 접촉역학 수치는 정의를 밝히지 않아 그대로 쓰면 안 된다:
- 공칭 2 psi → 패드 asperity 0.86 MPa는 **접촉면적률 1.60 %**를 뜻한다([[gw-nominal-vs-local-pressure]]의 통상 범위와 같은 자릿수).
- "입자 위 148 MPa"는 **Hertz 접촉압이 아니다.** 134 nN / 148 MPa를 면적으로 되풀면 지름 34.0 nm(명기된 30 nm보다 13 % 큼)
  → 즉 **입자 투영면적 기준 공칭압**이다. 같은 힘을 실제 Hertz로 풀면(실리카/Si, E* ≈ 47 GPa, R = 15 nm) 평균 접촉압은
  **4236 MPa로 29배** 크다.
- 압입깊이 3.4 Å는 **E* ≈ 131 GPa를 가정해야 재현된다**(우리 역산). 이는 Si 벌크 영률(⟨100⟩ 130 GPa)과 사실상 같은 값이므로,
  저자들이 **실리카 대응면의 탄성을 무시하고 Si 단일 재료 탄성률**을 썼다는 뜻이다. 실리카/Si 복합 E* = 47 GPa로 풀면 6.7 Å로
  **정확히 2.0배** 깊어진다. 어느 쪽이 옳은지는 원문이 가정을 적지 않아 **판정 불가 — 미검증**. 우리 모델에는
  [[hertz-gw-contact-mechanics]]의 복합 E* 정의를 쓴다(서열 판정 불필요 — 정의 차이일 뿐 충돌이 아니다).

## 7. 최신 동향 — Dang et al. 2025 (초록만, E5)

초록 원문(Crossref/OpenAlex 기탁본) 요지: EDA(에틸렌디아민)의 **–NH₂**가 OH⁻와 시너지로 poly-Si 표면에 친수성 반응층을
만들고, 나노웨어 시험으로 그 층의 기계적 내마모성이 낮음을 확인했으며, **DFT로 –NH₂와 산화막/나이트라이드 표면 반응의
에너지장벽이 poly-Si보다 훨씬 높음**을 보였다. 최적 EDA 무연마재 슬러리는 **poly-Si MRR > 1000 nm/min(700 % 이상 증가)**,
산화막/나이트라이드는 최소, poly 표면조도 **0.3 nm**.

- "700 % 이상 증가"를 문자 그대로 받으면 기준 MRR ≈ 125 nm/min으로, Penta ACS AMI의 무첨가 poly RR(pH 10, 200 nm/min)과
  **같은 자릿수**다(§9(D)).
- 조도 0.3 nm는 Jeon 2021의 최적치 0.42 nm보다 낮다. 다만 막 두께·초기 조도·스캔 크기가 다르므로 **직접 비교는 부당**하다.
- 이 논문은 Lv1-2 §4의 Bae 2022(EDA 0.10 wt% + 60 nm 실리카, 552.8 nm/min)와 **같은 아민, 다른 연마재 조건**이다.
  Bae는 실리카가 있고 Dang은 무연마재인데 Dang이 2배 가까이 빠르다 — 이 차이가 진짜인지 조건 차인지는 **본문 없이 판정 불가**.

**전문을 못 봤으므로 이 절의 수치는 어떤 모델 상수로도 쓰지 않는다**(SCOPE: E5 단독 채택 금지).

## 8. 선택비 사다리 — 기존 노트와 교차 대조

| 계열 | poly RR (nm/min) | oxide RR (nm/min) | poly:oxide | poly:nitride | 출처 |
|---|---|---|---|---|---|
| 콜로이달 실리카 + TMAH | (역산 180–270) | 4–6 (고정) | 25 → 45 → 33 (피크형) | — | Park 2007, Lv2-1 §2 |
| 실리카 1.5 wt% + 알콕실화 디아민 | 176–518 | 0.2–6.2 | 69–1832 | — | US10822524B2, Lv2-2 §2.2 |
| α-아미노산(아르기닌·라이신) 2 wt% + 실리카/세리아 | ~550 | — | ~130 | ~260 | **2차 인용** (Penta 2011 서론이 인용한 Natarajan·Dandu) |
| α-아미노산 **무연마재** | > 650 | ~0 | — | — | **2차 인용** (Lagudu 2019 서론이 인용한 Dandu et al.) |
| PEI + 실리카/세리아 | ~500 | < 2 | > 250 | > 250 | **2차 인용** (Lagudu 2019 서론이 인용한 Lee·Kraft) |
| **폴리케이션 250 ppm(무연마재 또는 저고형분)** | **559–636** | **≤ 2** | **≥ 280 (하한)** | **≥ 280 (하한)** | Penta 2011 Langmuir §2 |
| 실리카 0.1 wt% + TBAF | — (50배 향상만 보고) | — | > 420 | — | Kim NCCAVS §6 |
| EDA 무연마재 | > 1000 | "minimal" | — | — | Dang 2025 **초록만** |

세로로 읽으면 규칙이 하나 보인다: **선택비의 계단은 poly를 더 빨리 깎아서가 아니라 산화막을 더 깊이 끄면서 올라간다.**
Park 2007의 산화막 4–6 nm/min은 Penta의 ≤ 2 nm/min보다 2–6배 높고, 그동안 poly RR은 오히려 2–3배 낮다(§9(F)).
Lv2-1 §6이 "화학이 부여하는 잠재 선택비(~2.8 × 10⁴:1)가 CMP에서 200배 압축된다"고 했는데, 압축을 푸는 방법이
**"기계 항을 산화막에서 떼어내는 것"**임을 이 단원이 보여준다 — 무연마재는 기계 항 자체를 없애고, 문턱형은 기계 항에 조건을 건다.

## 9. Python 재현 & 문헌 대조

**재현 요약**: Penta 2011 Langmuir(DOI 10.1021/la104257k) 표 3에서 poly:oxide = poly:nitride = 559·636 을 재계산해 원문 서술 "~600"과 대조하고 하한 280 을 전파, 표 2 결합에너지로 브리징 결합력 구간 54–78 kcal/mol 을 산출; Penta 2011 ACS AMI(DOI 10.1021/am2010114) 전하밀도 서열 대조; Lagudu 2019(DOI 10.1149/2.0081905jss) 문턱압력 1.0–2.5 psi 와 역산 기울기 108–217 nm/min/psi 대조; Jeon 2021(DOI 10.1016/j.mssp.2021.105755) 조도 개선 19.2 % · 55.3 % 재현; Kim NCCAVS 압입깊이 3.4 Å 의 등가탄성률 131 GPa 역산; 노트 간 선택비 사다리 대조 — 아래 6블록.

```python verify
# ── (A) Penta 2011 Langmuir(DOI 10.1021/la104257k) 표 2·3·4: 선택비, 자유폴리머 요건, 결합에너지 위계 ──
# 표 3 (pH 10): {슬러리: (poly RR, oxide RR, nitride RR)} — 단위 nm/min
T3 = {"1% ceria":                    (245, 381, 86),
      "1% ceria + 250 ppm PDADMAC":  (559,   1,  1),
      "modified ceria":              (226, 527, 156),
      "1% silica":                   (230,   1,  1),
      "1% silica + 250 ppm PDADMAC": (636,   1,  1),
      "modified silica":             (397,   1,  1)}
sel = {k: (p / o, p / n) for k, (p, o, n) in T3.items()}
# (a1) PDADMAC 슬러리의 poly:oxide·poly:nitride = 559 / 636 → 원문 결론 "~600"
for k in ("1% ceria + 250 ppm PDADMAC", "1% silica + 250 ppm PDADMAC"):
    so, sn = sel[k]
    assert so == sn and 500 <= so <= 700, (k, so, sn)
# (a2) 무첨가 세리아는 poly:oxide < 1 — 선택비의 부호가 반대다
assert sel["1% ceria"][0] < 1.0 < sel["1% ceria"][1], sel["1% ceria"]
flip = sel["1% ceria + 250 ppm PDADMAC"][0] / sel["1% ceria"][0]
assert flip > 800, flip                       # 0.64 → 559 : 869배 반전
# (a3) 선택비는 '하한'이다 — oxide/nitride RR이 1 ± 1 nm/min(측정한계)이라 상한은 발산
lo = 559 / (1 + 1)
assert lo == 279.5
# (a4) 자유 PDADMAC이 있어야 oxide/nitride가 억제된다: 원심세척한 modified 세리아는 억제 실패
assert T3["modified ceria"][1] > T3["1% ceria"][1] and T3["modified ceria"][2] > T3["1% ceria"][2]
assert abs(T3["modified ceria"][0] - T3["1% ceria"][0]) / T3["1% ceria"][0] < 0.10   # poly RR은 무첨가와 동일(8 %)
# (a5) 반면 실리카는 세척 후에도 폴리머가 남아(TGA 2 % vs 세리아 0.1 %) poly RR을 부분적으로 올린다
assert T3["modified silica"][0] > T3["1% silica"][0] * 1.5
assert T3["modified silica"][0] < T3["1% silica + 250 ppm PDADMAC"][0]
# (a6) 표 2 결합해리에너지(kcal/mol) → 원문 메커니즘 부등식 Si-Si < 브리징 < Si-N/Si-O 가 가두는 구간
BDE = {"Si-Si": 54, "Si-H": 70, "Si-C": 70, "Si-N": 78, "Si-Cl": 95, "Si-O": 113, "Si-F": 132}
assert BDE["Si-Si"] == min(BDE.values())
lo_b, hi_b = BDE["Si-Si"], min(BDE["Si-N"], BDE["Si-O"])
assert lo_b < hi_b
KCAL_EV = 0.0433641                              # 1 kcal/mol = 0.0433641 eV
print(f"(A) 선택비 poly:oxide=poly:nitride = {sel['1% ceria + 250 ppm PDADMAC'][0]:.0f}(세리아)/"
      f"{sel['1% silica + 250 ppm PDADMAC'][0]:.0f}(실리카) → 원문 '~600'; 하한 {lo:.0f}; "
      f"무첨가 세리아 poly:oxide {sel['1% ceria'][0]:.2f}에서 {flip:.0f}배 반전; "
      f"브리징 결합력 구간 {lo_b}-{hi_b} kcal/mol = {lo_b*KCAL_EV:.2f}-{hi_b*KCAL_EV:.2f} eV")
# (a7) 표 4 (pH 2): 흡착층이 남으면 정전 부호가 뒤집혀도 기계적 작용이 차단된다
T4 = {"1% silica": (-15, 13, 33), "1% silica + 250 ppm PDADMAC": (35, 1, 1), "modified silica": (31, 4, 1)}
assert T4["1% silica"][0] < 0 < T4["modified silica"][0]
assert T4["modified silica"][1] < T4["1% silica"][1] / 3 and T4["modified silica"][2] < T4["1% silica"][2] / 10
print(f"(A2) pH 2 modified silica: zeta {T4['1% silica'][0]}→{T4['modified silica'][0]} mV, "
      f"oxide {T4['1% silica'][1]}→{T4['modified silica'][1]} nm/min, "
      f"nitride {T4['1% silica'][2]}→{T4['modified silica'][2]} nm/min")
```

```python verify
# ── (B) Penta 2011 ACS AMI(DOI 10.1021/am2010114): 폴리케이션 전하밀도 서열 vs poly RR 서열 ──
# 원문 §3.1 서술값 (pH 10, 250 ppm, 무연마재). 구간으로만 준 값은 구간 그대로 둔다(그래프 미판독).
RR = {"PDADMAC": (500, 600), "PDEE": (500, 600), "PAAm": (500, 600), "PEI": (500, 600),
      "PAA-DADMAC": (50, 500),      # 원문: "PAA보다 높고 PDADMAC보다 낮다" — 구간만 확정
      "PAA": (50, 50), "DI water": (200, 200)}
CD_RANK = {"PDADMAC": 3, "PDEE": 3, "PAAm": 3, "PEI": 3, "PAA-DADMAC": 2, "PAA": 1}  # 원문 §4.1 전하밀도 서열
# (b1) 전하밀도가 높은 쪽의 RR이 낮은 쪽보다 확실히 위인지 (구간이 겹치면 '반증 못 함'으로 분류)
strict, overlap = [], []
for i in CD_RANK:
    for j in CD_RANK:
        if CD_RANK[i] > CD_RANK[j]:
            (lo_i, hi_i), (lo_j, hi_j) = RR[i], RR[j]
            assert hi_i > hi_j, (i, j)                 # 서열 위반은 없어야 한다
            (strict if lo_i > hi_j else overlap).append((i, j))
assert len(strict) == 4 and len(overlap) == 5          # 고전하 4종 vs PAA만 완전분리, PAA-DADMAC이 낀 5쌍은 구간 중첩
# (b2) PAA는 무첨가 DI water보다 poly RR을 4배 억제 — '폴리머 첨가 = 가속'이 아니다
supp = RR["DI water"][0] / RR["PAA"][0]
assert supp == 4.0, supp
# (b3) 고전하밀도 4종의 증폭배수 (DI water 200 nm/min 대비)
amp_lo, amp_hi = RR["PDADMAC"][0] / 200, RR["PDADMAC"][1] / 200
assert (amp_lo, amp_hi) == (2.5, 3.0)
# (b4) Langmuir 표 3의 PDADMAC poly RR(559·636)이 이 구간과 정합한지 교차확인
for v in (559, 636):
    assert RR["PDADMAC"][0] <= v <= RR["PDADMAC"][1] * 1.06, v    # 636은 상한 600을 6 % 초과(연마재 첨가 조건)
print(f"(B) 전하밀도 서열이 RR 서열과 모순 없음(완전분리 {len(strict)}쌍, 구간중첩 {len(overlap)}쌍); "
      f"PAA 억제 {supp:.1f}배, 고전하밀도 증폭 {amp_lo:.1f}-{amp_hi:.1f}배 (DI water 200 nm/min 기준)")
```

```python verify
# ── (C) Lagudu 2019(DOI 10.1149/2.0081905jss): 비-Preston 문턱압력·Preston 기울기 정합·패턴 공정창 ──
P_TH = {"PDADMAC": 1.5, "DADMAC": 2.5, "GC": 1.0}          # psi, 문턱압력 (원문 Fig.3·4 서술)
RR_4PSI = (300, 350)                                        # nm/min, "all around 300-350 nm/min at 4 psi"
RR_LOW_BAND = (80, 270)                                     # nm/min, CPB 없는 Prestonian RL의 1·2 psi 실측 구간
# (c1) CPB 25 ppm만 문턱을 만든다. 50 ppm 이상은 1-4 psi 전 구간을 0으로 눌러 공정 자체를 없앤다
CPB_SWEEP = {250: 0.0, 100: 0.0, 50: 0.0, 25: None}         # None = 비-Preston(문턱 존재)
assert all(v == 0.0 for k, v in CPB_SWEEP.items() if k >= 50)
assert CPB_SWEEP[25] is None
# (c2) 문턱-Preston 모델 RR = k(P - P_th)의 기울기를 4 psi 값으로 역산
mid = sum(RR_4PSI) / 2
k = {a: mid / (4.0 - p) for a, p in P_TH.items()}
k_band = (RR_LOW_BAND[0] / 1.0, RR_LOW_BAND[1] / 2.0)       # Prestonian 기울기 구간(원점통과 가정)
inside = {a: k_band[0] <= v <= k_band[1] for a, v in k.items()}
assert inside["PDADMAC"] and inside["GC"] and not inside["DADMAC"], (k, k_band)
dev = (k["DADMAC"] - k_band[1]) / k_band[1]
assert dev > 0.5, dev                                       # DADMAC은 상한을 60 % 초과 — 숨기지 않음
# (c3) 억제제 비교 (1 psi, 250 ppm): 비이온 Brij 35는 26 nm/min까지만, 양이온 CPB는 0
assert 26 / mid < 0.10                                      # Brij 35 잔류율 8 %
# (c4) 패턴 공정창: up 압력증폭 f에서 down은 문턱 아래, up은 문턱 위가 되는 공칭압 구간
#      f = 1.7 은 Sorooshian 2004(DOI 10.1149/1.1785933, STI 산화막 초록값 밀도 50 %) — E5 전이, 방향만
f = 1.7
win = {a: (p / f, p) for a, p in P_TH.items()}
for a, (lo, hi) in win.items():
    assert lo < hi and (hi - lo) / hi > 0.4                 # 창 폭이 문턱의 41 %
assert abs(win["PDADMAC"][0] - 0.882) < 1e-3
print(f"(C) 문턱압력 {P_TH} psi; 역산 기울기 "
      f"{ {a: round(v,1) for a, v in k.items()} } nm/min/psi vs Prestonian 구간 {k_band} → "
      f"PDADMAC·GC 정합, DADMAC {dev*100:.0f} % 초과; 공칭압 창(f={f}) PDADMAC "
      f"{win['PDADMAC'][0]:.2f}-{win['PDADMAC'][1]:.2f} psi")
```

```python verify
# ── (D) Jeon 2021(DOI 10.1016/j.mssp.2021.105755) 조도 재현 + Dang 2025(DOI 10.1016/j.jmapro.2025.11.011) 초록 대조 ──
Ra = {"연마 전(어닐 후 돌기)": 3.58, "1 wt% 실리카 슬러리": 0.94,
      "250 ppm PDADMAC": 0.52, "250 ppm PDADMAC + 750 ppm PEG": 0.42}          # nm, 원문 §3.3
imp_pdad = 1 - Ra["250 ppm PDADMAC + 750 ppm PEG"] / Ra["250 ppm PDADMAC"]
imp_sil  = 1 - Ra["250 ppm PDADMAC + 750 ppm PEG"] / Ra["1 wt% 실리카 슬러리"]
assert abs(imp_pdad * 100 - 19.2) < 0.1, imp_pdad          # 원문 초록 "19.2 %"
assert abs(imp_sil * 100 - 55.3) < 0.1, imp_sil            # 원문 초록 "55.3 %"
# 무연마재가 연마재보다 조도가 낮다 — '연마입자 제거 = 결함원 제거'의 정량 근거
assert Ra["250 ppm PDADMAC"] < Ra["1 wt% 실리카 슬러리"]
assert Ra["연마 전(어닐 후 돌기)"] / Ra["250 ppm PDADMAC + 750 ppm PEG"] > 8
# PEG의 양날: 정적 식각은 207 → ~22 Å로 억제되지만 1000 ppm 초과에서 조도는 다시 나빠진다
etch = {"250-1000 ppm PEG": 207.0, "5000·10000 ppm PEG": 22.0}                  # Å, 원문 §3.1
assert etch["250-1000 ppm PEG"] / etch["5000·10000 ppm PEG"] > 9
Ra_opt_ppm, Ra_worse_above = 750, 1000
assert Ra_opt_ppm < Ra_worse_above
# Dang 2025 초록(전문 미확보, E5): poly MRR > 1000 nm/min, "increase of over 700 %", 조도 0.3 nm
dang_mrr, dang_gain, dang_ra = 1000.0, 7.0, 0.30
base_implied = dang_mrr / (1 + dang_gain)                                       # +700 % → 기준값 = 1/8
assert 100 < base_implied < 200, base_implied              # 무첨가 poly RR 200 nm/min(Penta ACS AMI)과 같은 자릿수
assert dang_ra < Ra["250 ppm PDADMAC + 750 ppm PEG"]
print(f"(D) 조도 개선 {imp_pdad*100:.1f} % / {imp_sil*100:.1f} % (문헌값 19.2 / 55.3 %) 재현; "
      f"3.58 → 0.42 nm ({Ra['연마 전(어닐 후 돌기)']/Ra['250 ppm PDADMAC + 750 ppm PEG']:.1f}배); "
      f"Dang 2025가 함의하는 기준 MRR {base_implied:.0f} nm/min, 조도 {dang_ra} nm")
```

```python verify
# ── (E) Kim et al.(NCCAVS/ICPT P42, DOI 없음) 반연마재 TBAF: 접촉역학 수치의 정의 역추적 ──
import math
P_NOM_PSI, P_ASP_MPA, P_PART_MPA, F_NN, DELTA_A, D_PART_NM = 2.0, 0.86, 148.0, 134.0, 3.4, 30.0
PSI_KPA = 6.894757                                        # 1 psi = 6.894757 kPa
# (e1) 공칭 2 psi → asperity 0.86 MPa 는 접촉면적률 1.6 %를 뜻한다
A_ratio = (P_NOM_PSI * PSI_KPA * 1e3) / (P_ASP_MPA * 1e6)
assert 0.015 < A_ratio < 0.017, A_ratio
# (e2) "입자 위 148 MPa"는 Hertz 접촉압이 아니라 입자 투영면적 기준 공칭압이다
r_implied = math.sqrt((F_NN * 1e-9) / (P_PART_MPA * 1e6) / math.pi)
d_implied = 2 * r_implied * 1e9
assert abs(d_implied - D_PART_NM) / D_PART_NM < 0.15, d_implied     # 34.0 nm — 명기 30 nm보다 13 % 큼
E_star_sio2_si = 1 / ((1 - 0.17 ** 2) / 70e9 + (1 - 0.22 ** 2) / 130e9)   # 실리카/Si 복합 E* ≈ 47 GPa
R = D_PART_NM / 2 * 1e-9
a = (3 * (F_NN * 1e-9) * R / (4 * E_star_sio2_si)) ** (1 / 3)
p_hertz = (F_NN * 1e-9) / (math.pi * a * a) / 1e6
assert p_hertz / P_PART_MPA > 20, (p_hertz, P_PART_MPA)   # 4236 MPa vs 148 MPa → 29배, 정의가 다르다
# (e3) 압입깊이 3.4 Å를 Hertz로 되풀면 저자들이 쓴 등가탄성률이 나온다
E_star_implied = 3 * (F_NN * 1e-9) * R / (4 * (math.sqrt(DELTA_A * 1e-10 * R)) ** 3)
assert abs(E_star_implied / 1e9 - 131) < 2, E_star_implied / 1e9      # 131 GPa ≈ Si 벌크 영률(⟨100⟩ 130 GPa)
delta_soft = (a * a / R) * 1e10
assert abs(delta_soft / DELTA_A - 2.0) < 0.05, delta_soft             # 복합 E*로 풀면 6.7 Å — 정확히 2.0배
# (e4) 결론부 수치: poly:oxide > 420, MRR 50배, 물 99.8 % 이상, 실리카 0.1 wt%
SEL, MRR_GAIN, WATER, SOLID_WT = 420.0, 50.0, 0.998, 0.001
assert SEL > 400 and (1 - WATER) < 0.0021 and MRR_GAIN == 50.0
assert SOLID_WT * 100 == 0.1 and SOLID_WT <= (1 - WATER) + 1e-12
print(f"(E) 접촉면적률 {A_ratio*100:.2f} %; 148 MPa 역산 입경 {d_implied:.1f} nm"
      f"(명기 30 nm 대비 +{(d_implied/D_PART_NM-1)*100:.0f} %); Hertz 평균접촉압 {p_hertz:.0f} MPa"
      f"(=투영압의 {p_hertz/P_PART_MPA:.0f}배); 3.4 Å가 함의하는 E* {E_star_implied/1e9:.0f} GPa, "
      f"복합 E*=47 GPa면 {delta_soft:.1f} Å")
```

```python verify
# ── (F) 노트 간 선택비 사다리: 계단은 poly 가속이 아니라 oxide 억제로 올라간다 ──
# Park 2007 (Lv2-1 §2, DOI 10.3938/jkps.51.214): oxide RR 40-60 Å/min 고정, 선택비 25→45→33
park_ox_nm = (40 / 10, 60 / 10)                    # Å/min → nm/min = 4-6
park_sel_peak = 45
park_poly = tuple(park_sel_peak * v for v in park_ox_nm)     # 역산 poly RR 180-270 nm/min
assert 150 < park_poly[0] and park_poly[1] < 300, park_poly
# Penta 2011 Langmuir: oxide RR ≤ 2 nm/min (1 ± 1), poly 559-636
penta_ox_max, penta_poly = 2.0, (559, 636)
# (f1) 산화막 억제 배수 — 폴리케이션이 TMAH/실리카보다 2-3배 더 깊이 끈다
ox_gain = (park_ox_nm[0] / penta_ox_max, park_ox_nm[1] / penta_ox_max)
assert ox_gain[0] >= 2.0 and ox_gain[1] == 3.0, ox_gain
# (f2) 동시에 poly RR도 2-3.5배 높다 — 트레이드오프가 아니다
poly_gain = (penta_poly[0] / park_poly[1], penta_poly[1] / park_poly[0])
assert poly_gain[0] > 2.0 and poly_gain[1] < 4.0, poly_gain
# (f3) 선택비 배수는 두 효과의 곱이어야 한다 — 자기정합 확인
sel_gain_direct = (penta_poly[0] / penta_ox_max) / park_sel_peak
sel_gain_product = poly_gain[0] * ox_gain[1]
assert abs(sel_gain_direct - sel_gain_product) / sel_gain_direct < 1e-9, (sel_gain_direct, sel_gain_product)
# (f4) Lv2-2 US10822524B2 최고선택비(1832)는 이 하한(280)보다 크지만 TEOS RR 0.2 nm/min이라 비교 불능 구간이다
us_sel_max, us_teos_min = 1832, 2 / 10                       # Å/min → nm/min
assert us_teos_min < penta_ox_max                            # 둘 다 '검출한계 근처' — 점추정 비교 금지
print(f"(F) 산화막 억제 {ox_gain[0]:.1f}-{ox_gain[1]:.1f}배 × poly 가속 {poly_gain[0]:.2f}-{poly_gain[1]:.2f}배 "
      f"= 선택비 {sel_gain_direct:.1f}배 (45:1 → {penta_poly[0]/penta_ox_max:.0f}:1 하한); "
      f"Lv2-2 특허 최고 {us_sel_max}:1은 TEOS {us_teos_min} nm/min 검출한계라 직접 비교 불가")
```

## 10. 한계 / 미확인 사항

- **"선택비 ~600"은 점추정이 아니라 하한이다.** oxide·nitride RR이 1 ± 1 nm/min이라 상대불확실도 100 %다. §9(A)에서 하한
  280을 전파했지만 상한은 발산한다. 모델 상수로 쓸 때는 **"≥ 280"** 형태로만 써야 한다.
- **결함 계수(defect count) 데이터가 없다.** 이 단원 전체에서 스크래치·LPC·결함밀도를 **직접 센 1차 문헌은 확보하지
  못했다**. "무결함"의 유일한 정량 근거는 Jeon 2021의 AFM Ra 4점이며, 조도는 결함밀도의 대리변수일 뿐이다
  ([[../cmp/post-cmp-defect-classification-and-inspection]]의 7종 분류 중 어느 것도 세지 않았다). Cal-1 과제로 이관.
- **브리징 인력의 절대 크기가 없다.** §2.4의 부등식은 54–78 kcal/mol 구간을 주지만, poly-Si/IC1000 계에서 pull-off force를
  직접 잰 데이터는 원문에 없다(마이카·셀룰로오스 대리 실험만) — **추정**.
- **Lagudu 2019의 RR-압력 곡선을 그래프에서 판독하지 않았다.** §9(C)의 기울기 대조는 본문 서술 구간(80–270, 300–350)만
  쓴 것이라 DADMAC의 60 % 초과가 실제 불일치인지 구간 근사의 산물인지 **판정 불가 — 원인 미상**.
- **§5.3의 공정창(0.88–1.50 psi)은 이 노트의 유도**다. 압력증폭 f = 1.7은 Sorooshian 2004의 **STI 산화막** 초록값을
  전이한 것(E5)이며 poly 계 실측이 아니다. 값이 아니라 **형태**만 채택한다.
- **Kim NCCAVS 발표논문은 게재연도가 문서에 없고 DOI도 없다.** 저자·소속·수치는 PDF 원문에서 직접 읽었지만 동료심사
  여부를 확인 못 했다. §9(E)는 그 수치들을 **우리가 다시 계산해 정의 불일치를 드러낸 것**이지 값을 채택한 것이 아니다.
- **Dang 2025는 초록만**(E5). MRR > 1000 nm/min, 조도 0.3 nm, DFT 에너지장벽 어느 것도 본문 검증 없이 인용했다.
  CC-BY인데도 ScienceDirect 403·Elsevier TDM 키 요구로 막혔다 — 재시도 경로는 저자 기관 리포지토리(西南交通大学) 또는
  1년 뒤 PMC 미러.
- **poly:nitride 선택비의 독립 1차 데이터가 사실상 1건**이다(Penta 2011 Langmuir). §8 표의 나머지 poly:nitride 값
  (~260, > 250)은 전부 **2차 인용**이다. Lv2-1이 poly:oxide를 두 방향으로 채운 것에 비해 nitride 축은 여전히 얇다.
- **온도·속도 의존을 아무도 보고하지 않는다.** 이 단원의 모든 데이터는 단일 온도·단일 속도(90/90 또는 87/93 rpm)이며,
  브리징 인력의 온도 의존은 미확인이다. Preston의 V 항이 폴리케이션 계에서 성립하는지도 **확인 못 함**.

## 11. 이 에이전트의 결론 (모델링 관점)

1. **poly 팩의 선택비는 상수가 아니라 "화학 계열"의 함수다.** 최소 네 계열(TMAH/실리카 25–45, 알콕실화 디아민 69–1832,
   α-아미노산 130–260, 폴리케이션 ≥ 280)이 있고, 계열 간 자릿수 차이는 poly RR이 아니라 **산화막 RR**에서 나온다(§9(F)).
   Tier2 모델은 `poly_oxide_selectivity` 한 숫자가 아니라 **oxide RR 억제인자**를 명시적으로 갖는 편이 문헌과 정합한다.
2. **무연마재 계에서는 Δ(손상 유발도) 팩터가 정의되지 않는다.** [[../cmp/delta-scratch-damage-d99-oversize-particle-model]]의
   Δ = (d99/d99_ref)^n은 연마입자 분포에 걸려 있는데, 연마입자가 없으면 이 축 자체가 사라진다. 팩 스키마에
   `abrasive_free: true` 분기가 필요하다(구현 요청 [P5]).
3. **비-Preston 문턱압력이 Lv2-2 [P2] χ_down의 물리적 실체다.** MRR = k(P − P_th)⁺는 파라미터가 두 개(k, P_th)뿐이고,
   문턱압력은 첨가제(아민 종류·CPB 농도)로 1.0–2.5 psi 범위에서 이동한다는 실측이 있다. Lv2-2가 "흡착 차단 — 추정"으로
   남긴 것을 압력 축의 측정 가능한 파라미터로 바꿀 수 있다.
4. **접촉역학 수치를 문헌에서 그대로 가져오면 안 된다.** §9(E)에서 같은 실험의 "148 MPa"가 Hertz 접촉압의 1/29,
   "3.4 Å"가 복합 E* 기준의 1/2임을 확인했다. 문헌의 접촉량은 **정의를 확인하기 전까지 인용 금지**다.
5. **선택비를 올리는 것과 디싱을 줄이는 것은 여전히 다른 손잡이다.** Lv2-2의 역설은 이 단원에서도 해소되지 않았다 —
   해소한 것은 "선택비를 더 올려서"가 아니라 "압력 응답에 문턱을 심어서"다.

## 12. 자기시험
→ [[../../agents/film-poly-si/EXAMS.md]] Lv3-1 문항 참조.
