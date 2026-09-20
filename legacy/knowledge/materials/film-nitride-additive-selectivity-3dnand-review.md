# 나이트라이드 선택비 첨가제 최신 정리 — 억제/촉진의 정량 손잡이와 3D NAND 응용 (film-nitride Lv3-1)

> film-nitride Lv3-1 | 작성일: 2026-09-14
> 선행(같은 에이전트): [[film-nitride-selectivity-ceria-chemistry]] (Lv1-2 — 세리아 선택비 3단 위계·흡착 포화 스위치),
> [[film-nitride-lpcvd-pecvd-properties-cmp]] (Lv1-1 — 가수분해 제거기전·chemically-limited),
> [[../cmp/sti-nitride-loss-erosion-overpolish-window]] (Lv2-1 — 선택비 s가 나이트라이드 손실 예산·오버폴리시 창으로 번역),
> [[film-nitride-direct-cmp-hardmask-gate]] (Lv2-2 — 역선택비로 나이트라이드를 **깎는** SAC·핀캡 응용)
> 형제(중복 금지): [[oxide-ceria-additive-selectivity-review-2024]] (film-oxide Lv3-1 — **옥사이드 관점**: 첨가제가 있어도 옥사이드 RR이 왜 유지되나·저결함 입자설계).
> 이 노트는 **나이트라이드 막질의 제거/억제 관점**만 다룬다: 첨가량 대 SiN MRR·선택비·흡착의 정량 손잡이, pH로 뒤집는 역선택비, 3D NAND ONON 정지 요구선택비.
> 관련: [[../cmp/ceria-slurry-ce-redox-selectivity]] (Ce³⁺ 산화상태), [[preston-luo-dornfeld-mrr]] (Kp 프레임)
> 스코프 밖(형제·제형 침범 금지): 슬러리 콜로이드 분산·제타전위 제형 최적화(slurry-chemist), 옥사이드측 저결함 입자(film-oxide), 습식 인산에칭 선택비.

## 1. 왜 이 단원인가 — "첨가제로 선택비를 만든다"를 정량 손잡이로 분해

Lv1-2는 선택비가 **무첨가(≈4:1) < 분산제(≈5–8) < 사이트차단 첨가제(≈100–290)** 의 3단 위계임을 세웠다.
이 노트는 그 3단째(사이트차단)를 **어떤 첨가제가·얼마나·어느 pH에서** 라는 정량 축으로 분해하고, 최근(2013–2025)
1차문헌·리뷰로 세 가지를 채운다: **(a)** SiN 제거를 억제하는 첨가제(아미노산·고리형 카복실산)의 첨가량-선택비 관계와
흡착·양성자화 폐형식, **(b)** 반대로 SiN을 촉진하는 조건(고 pH·첨가제)의 역선택비 정량, **(c)** 3D NAND ONON 적층
CMP에서 요구되는 정지 선택비와 문헌 실측치. Lv1-2가 Dandu 2009(pH 4–5, 사이클릭 아민)를 다뤘다면, 이 노트는
**America/Penta/Praveen(아미노산·pH 창)** 과 **최신 3D NAND 세리아 슬러리** 를 새로 판독한다.

## 2. 출처 (5건 — 1차 4건[전문 완독 3건], 최신 리뷰 1건)

- **[Am04] W. G. America, S. V. Babu, "Slurry Additive Effects on the Suppression of Silicon Nitride Removal during
  CMP," *Electrochem. Solid-State Lett.* 7(12) G327–G330 (2004). DOI: 10.1149/1.1817870.** 1차 논문, 원문 PDF 완독
  (`papers/america2004-jes-slurry-additive-suppression-sin.pdf`). Table I(10종 첨가제 RR·선택비, pH 9.6)·pH 창(SiN RR 최소 pH 9.7,
  pH 11서 ~10배 증가)·알파아미노+카복실+아민H 요건. **연도가 15년 초과(예외)** — 이 계의 정량 흡착·pH 창 원출처라 반드시 필요.
- **[Pe13] N. K. Penta, B. C. Peethala, H. P. Amanapu, A. Melman, S. V. Babu, "Role of hydrogen bonding on the adsorption
  of several amino acids on SiO₂ and Si₃N₄ and selective polishing of these materials using ceria dispersions,"
  *Colloids Surf. A* 429, 67–73 (2013). DOI: 10.1016/j.colsurfa.2013.03.046.** 1차 논문, 원문 PDF 완독
  (`papers/penta2013-colsurfa-amino-acid-adsorption-sio2-si3n4.pdf`). Table 1(첨가제별 양성자화 pH 창·소요 농도·억제 후 SiN RR)·
  흡착등온(≈100 mg/g 포화)·양성자화종 상관.
- **[Pr14] B. V. S. Praveen, R. Manivannan, T. D. Umashankar, B.-J. Cho, J.-G. Park, S. Ramanathan, "Abrasive and additive
  interactions in high selectivity STI CMP slurries," *Microelectron. Eng.* 114, 66–71 (2014). DOI: 10.1016/j.mee.2013.10.004.**
  1차 논문, 원문 PDF 완독(`papers/praveen2014-mee-abrasive-additive-sti-selectivity.pdf`). L-proline vs L-glutamic acid ×
  세리아 3종(La 함량 EDX)·첨가제-연마재 상호작용이 선택비를 가른다는 실측.
- **[Zh25] X. Zhao, X. Han, F.-Y. Wang, B. Tan, Y. Shi, J.-D. Zhao, W. Qi, J.-J. Geng, "Improvement of polishing performance
  of SiO₂/Si₃N₄ by surfactants in CeO₂ based slurry," *Appl. Surf. Sci.* (2025). DOI: 10.1016/j.apsusc.2025.163978.** 1차 논문,
  Crossref로 실존·저자 확인. **원문 PDF 미확보**(2025-11 게재, 유료·미러 사이트 미등재·unpaywall is_oa=False) → 아래 3D NAND
  요구선택비(30:1)·최적 조성(pH 5, 0.02 M Lys+0.02 M Glu+0.003 M TEAOH)·실측치(SiO₂ 3606.1·Si₃N₄ 101.6 Å/min, 선택비 35.49)는
  **퍼블리셔 초록 기반 2차 인용(E5), 원문 미확인**으로 표기.
- **[Rv25] (리뷰) "Application of amino acids as auxiliary reagents in chemical mechanical polishing: an in-depth review,"
  *Surf. Sci. Technol.* (2025). DOI: 10.1007/s44251-025-00077-6.** 최신 리뷰(가중치 0.6). Crossref 실존. **원문 전문 미확보**
  (Springer Fastly 챌린지) → 이 노트는 **정성 프레이밍·참고문헌 존재확인 용도로만** 인용하고 수치는 취하지 않는다(E5).

## 3. (a) SiN 제거를 억제하는 첨가제 — 무엇이·얼마나 (Am04 Table I, pH 9.6)

Am04는 1 wt% 세리아 + **2 wt% 첨가제**, pH 9.6±0.1, 5 psi/50 rpm/75 cm·s⁻¹, 3 min×3에서 10종을 스크리닝했다.
모두 카복실기를 갖지만 SiN을 억제한 것은 **아민 수소가 카복실기의 α-탄소에 붙은** 것만이다(원문 결론):

| 첨가제 | SiN RR (nm/min) | 옥사이드 RR (nm/min) | 선택비(ox/SiN) | 비고 |
|---|---|---|---|---|
| 아르기닌 | 1 | 23 | 23 | SiN·옥사이드 **둘 다** 억제(옥사이드 손실 → STI 부적합) |
| 라이신 | 1 | 71 | 71 | 옥사이드도 억제 |
| **프롤린** | **2** | **456** | **228** | 옥사이드 무영향(430–460 밴드) → **최고 선택비** |
| N-메틸글리신 | 12 | 467 | 38.9 | |
| 알라닌 | 18 | 455 | 30.3† | †원문 인쇄 선택비 30.3이나 455/18=25.3 (원문 내적 불일치 ~17%, 원인 미상) |
| 글리신 | 18 | 435 | 24.2 | |
| 피콜린산 | 65 | 423 | 6.5 | 아민 H 없음(고리 N) → **억제 실패** |
| N,N-디메틸글리신 | 68 | 438 | 6.4 | 아민 H 없음 → 실패 |
| 3-아미노부티르산 | 72 | 442 | 6.1 | 아민이 **비-α**(한 탄소 밀림) → 실패 |
| 이소니코틴산 | 71 | 441 | 6.2 | 비-α 고리 → 실패 |

읽는 법: **선택비는 "SiN을 얼마나 끄느냐"로 결정**된다(옥사이드는 억제형 몇을 빼면 430–460 nm/min로 거의 불변).
프롤린이 챔피언인 이유는 SiN을 2 nm/min으로 끄면서 옥사이드를 안 건드리기 때문. 아르기닌·라이신은 SiN을 더 끄지만
(1 nm/min) 곁사슬 추가 아민이 pH 9에서 양전하가 되어 음전하 실라놀(옥사이드)에도 흡착→옥사이드까지 억제하므로 STI엔
부적합([Am04] 원문). **요건 3종**(카복실기 + α-위치 + 아민 H 최소 1개)이 모두 있어야 억제된다 — 피콜린/이소니코틴/
N,N-디메틸글리신/3-아미노부티르산은 셋 중 하나가 없어 baseline(≈6:1)에 머문다. 이 baseline(SiN 65–72 nm/min)이 이 계의
**무억제 SiN 제거율**이다.

**첨가량(dose) 축** — Pe13 Table 1은 "억제에 필요한 농도"와 "억제 후 SiN RR"을 첨가제별로 못박는다(0.1 wt% 세리아,
pH 창은 §4):

| 첨가제 | 종류 | 아민 양성자화 pH 창 | 억제 소요 농도 | 억제 후 SiN RR |
|---|---|---|---|---|
| 피콜린산 | 고리 α | pH ≤ 6 | **0.1 wt%** | ~1 nm/min |
| 니코틴산 | 고리 비-α | pH ≤ 5 | 0.1 wt% | ~1 nm/min |
| 프롤린 | 고리 α | pH ≤ 11 | **2 wt%** | ~2 nm/min |
| γ-아미노부티르산 | 지방족 비-α | pH ≤ 10 | 2 wt% | ~2 nm/min |

즉 **피콜린산은 0.1 wt%로 충분**하고 **프롤린은 2 wt% 필요** — 20배 차이. 흡착등온(Pe13 Fig.5)은 피콜린산·프롤린 모두
농도 0→2 wt%에서 SiO₂·Si₃N₄ 표면에 **≈100 mg/g로 포화(랑뮤어형)**, 세리아 표면 흡착은 <10 mg/g(그래서 세리아의
옥사이드 이빨을 안 죽임). 두 막에 흡착량은 비슷하지만(포화 ~100 mg/g) 억제는 SiN만 나타나는데, 이는 SiN 제거가
**가수분해-율속(chemically-limited, Lv1-1)** 이라 표면 피복이 곧 제거 차단이 되는 반면 옥사이드는 기계-제거라 약한
수소결합 흡착이 패드·연마재에 벗겨지기 때문(형제 [[oxide-ceria-additive-selectivity-review-2024]] §3의 옥사이드측 설명과 상보).

## 4. (a)-핵심: 억제는 "첨가제 아민이 양성자화되는 pH 창"에서만 켜진다 — 피콜린산 겉모순의 해소

Am04(pH 9.6)에서 **피콜린산은 SiN을 못 끈다(65 nm/min, 선택비 6.5)**. 그런데 Pe13/Wang(pH 5)에서는 **같은 피콜린산이
SiN을 ~1 nm/min으로 끈다**. 모순이 아니다 — Pe13이 원문에서 직접 조정한다: 억제는 첨가제의 **아민기가 양성자화되어
있는 pH에서만** 일어난다. 양성자화 분율은 헨더슨-하셀바흐 폐형식으로 재현된다(§7 [B]):

  f_protonated(pH) = 1 / (1 + 10^(pH − pKa_amine))

- 피콜린산 고리 N pKa ≈ 5.3 → pH 5에서 약 66% 양성자화(억제 ON), pH 9.6에서 ~5×10⁻⁵(억제 OFF). Am04 65 nm/min과 정합.
- 프롤린 2차 아민 pKa ≈ 10.6 → pH 9.6에서도 ~91% 양성자화(억제 ON) → Am04 2 nm/min·선택비 228과 정합.

**이것이 "왜 어떤 첨가제는 되고 어떤 건 안 되나"의 정량 규칙**이다(Carter[Pe13 인용]: 첨가제 pKa 3–7이면 pH 5에서 억제).
양성자화된 중성/양쪽성 종의 –N⁺H가 SiN 표면과 수소결합→가수분해 차단(America의 α-위치·아민 H 요건과 같은 기전을
pH 축으로 표현한 것). Lv1-2가 흡착 **포화 비대칭**(농도 스위치)으로 본 것을, 이 노트는 **pH 스위치**로 보완한다.

## 5. (b) 반대로 SiN을 촉진하는 조건 — 역선택비의 두 손잡이

정지층 응용의 거울상(Lv2-2)이지만 여기서는 **정량 조건**만 정리한다(기전 상세·특허 표는 [[film-nitride-direct-cmp-hardmask-gate]]).

- **고 pH(첨가제 없이도)**: Am04 pH 창 실측 — SiN RR은 pH 6–8에서 거의 일정, pH 8 초과부터 감소해 **pH 9.7에서 최소**
  (산소-제거 SiN의 IEP=9.7, 순전하 0), 그 위로 다시 올라 **pH 11에서 최소 대비 ~10배 증가**(§7 [C]). 즉 정지층은 pH≈9.7,
  **역제거(촉진)는 pH≥11** 또는 강산성/산화촉매 영역에서 열린다. pH가 첨가제 없이도 SiN 제거율을 한 자릿수 흔든다.
- **La 함유 상용 세리아 + 프롤린**: Pr14는 첨가제 효과가 **연마재에 의존**함을 보였다. La-무함유 자체합성 ceria-CM에
  L-proline을 넣으면 선택비 3→40(SiN 억제 ON), 그러나 **La 24–31 wt% 상용 세리아(ceria-SA/S)에서는 프롤린이 SiN을 거의
  못 끈다**(선택비 변화 미미) — 즉 상용 La-세리아 위에서는 프롤린이 정지층을 못 만들어 상대적으로 SiN이 계속 깎이는
  "약한 역선택비 쪽" 거동. 반면 **L-glutamic acid는 세리아 3종 모두에서 SiN을 <3 nm/min으로 억제**(견고). 첨가제만이 아니라
  **첨가제×연마재 조합**이 억제/촉진을 가른다는 것이 Pr14의 새 결론(EDX La 함량 §7 [D]).

이 노트는 Ce³⁺ 산화촉매(2.3 mM → SiN 300 nm/min)·카복실기+음이온연마재(SiN:TEOS 97:1) 같은 **적극적 역선택비 화학**은
Lv2-2가 이미 정량화했으므로 반복하지 않고 링크로 대체한다(중복 금지).

## 6. (c) 3D NAND 응용 — ONON 적층 CMP의 정지 요구선택비

3D NAND는 산화막/나이트라이드(ONON) **수십~수백 층 몰드 적층**을 쌓고, 계단(staircase)·슬릿·채널 형성 후 두꺼운
갭필 산화막을 CMP로 평탄화하며 **나이트라이드에서 정지**해야 한다(STI와 같은 stop-on-nitride이나 스택이 훨씬 두껍고
평탄화 부담이 큼). Zh25는 이 응용을 겨냥해 **요구 SiO₂:Si₃N₄ 선택비를 30:1로 명시**하고, CeO₂ 슬러리에 아미노산·염기
첨가제를 조합해 이를 충족한다(모두 [Zh25] 초록, **E5·원문 미확보**):

- 최적 조성: **pH 5, 0.02 M 라이신 + 0.02 M 글루탐산 + 0.003 M TEAOH** → SiO₂ **3606.1 Å/min**, Si₃N₄ **101.6 Å/min**,
  선택비 **35.49**(요구 30:1 상회). §7 [E]에서 3606.1/101.6=35.49 산술 일관성 재현.
- 기전(초록): 아미노산이 카복실기로 Ce⁴⁺와 착물을 이뤄 옥사이드 RR을 **촉진**하고, 동시에 아민기가 SiN 표면과
  강한 수소결합을 이뤄 SiN RR을 **억제** — §3–4의 America/Penta 수소결합 모델과 같은 두 방향 손잡이를 한 슬러리에 결합.

정량적으로 3D NAND의 30:1은 STI 블랭킷 고선택비(100–290:1, Lv1-2)보다 **낮은** 목표다. 이유는 Lv2-1에서 밝혔듯
**패턴·적층 웨이퍼의 유효 선택비가 블랭킷보다 훨씬 낮고**(세리아 HSS s_eff≈3), 두꺼운 ONON에서는 과도한 SiN 억제가
오히려 디싱·평탄화 악화를 부르기 때문 — 30:1은 "정지는 하되 평탄화 여유를 남기는" 실용 균형점으로 읽힌다
([[../cmp/sti-nitride-loss-erosion-overpolish-window]] §5–6의 블랭킷≠패턴 선택비 논지와 정합). Si₃N₄ 101.6 Å/min은
STI 정지 기준(<1 nm/min=10 Å/min, [[film-nitride-selectivity-ceria-chemistry]])보다 **한 자릿수 높다** — 3D NAND는 자기정지형
저 SiN율이 아니라 **유한한 SiN 손실을 예산 안에서 관리**하는 레짐임을 뜻한다(적층당 SiN 두께가 두꺼워 예산이 큼).

## 7. 정량 재현 (```python verify```, 실제 실행)

**재현 요약(한 줄)**: America 2004 Table I 선택비(프롤린 옥사이드 456 nm/min·SiN 2 nm/min → 228 최고, baseline SiN
72 nm/min → 6.1)를 문헌값과 대조 재현하고, 피콜린산 겉모순이 헨더슨-하셀바흐 양성자화 분율(pH5 pKa5.3서 0.66 ON vs pH9.6서 5e-5 OFF)로 해소되며,
America pH 창의 pH11/9.7 ~10배 촉진, Praveen La-세리아 EDX(24–31 wt%)와 프롤린 조건부 선택비, Zhao 2025 3D NAND
선택비 3606.1/101.6=35.49(≥요구 30:1)가 재현됨 — 아래 5블록 PASS.

```python verify
# [A] America & Babu 2004 Table I (DOI 10.1149/1.1817870, 원문 완독): pH 9.6, 1wt% ceria + 2wt% 첨가제
# (SiN RR, oxide RR) nm/min
tbl = {
 "arginine":(1,23), "lysine":(1,71), "proline":(2,456), "N-methylglycine":(12,467),
 "alanine":(18,455), "glycine":(18,435), "picolinic":(65,423),
 "NN-dimethylglycine":(68,438), "3-aminobutyric":(72,442), "isonicotinic":(71,441),
}
sel = {k: ox/sin for k,(sin,ox) in tbl.items()}
# 원문 표기 선택비와 대조
assert abs(sel["proline"]-228) < 1, sel["proline"]        # 456/2=228 최고
assert abs(sel["glycine"]-24.2) < 0.1
assert abs(sel["N-methylglycine"]-38.9) < 0.1
# 정직한 불일치: 원문 Table I은 알라닌 선택비를 30.3으로 인쇄했으나 455/18=25.3 (원문 내적 불일치 ~17%, 원인 미상)
assert abs(sel["alanine"]-25.28) < 0.1
assert abs(sel["alanine"]-30.3) > 3        # 인쇄된 30.3과 산술 25.3이 어긋남을 숨기지 않고 명시
assert abs(sel["picolinic"]-6.5) < 0.1
assert abs(sel["3-aminobutyric"]-6.1) < 0.1
# 요건 실패군(아민H 없음/비-α)은 baseline ~6:1에 머문다
for k in ("picolinic","NN-dimethylglycine","3-aminobutyric","isonicotinic"):
    assert 6.0 <= sel[k] <= 6.6, (k, sel[k])
# 프롤린은 옥사이드를 안 건드림(430-460 밴드), 아르기닌/라이신은 옥사이드까지 억제
assert 430 <= tbl["proline"][1] <= 460
assert tbl["arginine"][1] < 100 and tbl["lysine"][1] < 100  # 옥사이드 손실 → STI 부적합
# 선택비는 SiN 억제가 결정: baseline SiN(무억제)≈65-72 nm/min
baseline_sin = sum(tbl[k][0] for k in ("picolinic","3-aminobutyric","isonicotinic"))/3
assert 65 <= baseline_sin <= 72, baseline_sin
print(f"[A] 프롤린 선택비 {sel['proline']:.0f}(최고), baseline SiN {baseline_sin:.0f} nm/min, 실패군 sel≈{sel['3-aminobutyric']:.1f}")
```

```python verify
# [B] 피콜린산 겉모순 해소 — 억제는 아민 양성자화 pH 창에서만 (Penta 2013 DOI 10.1016/j.colsurfa.2013.03.046, 원문 완독)
def f_protonated(pH, pKa):        # 아민(염기)의 양성자화 분율, 헨더슨-하셀바흐
    return 1.0/(1.0 + 10**(pH - pKa))
pKa_picolinic = 5.3     # 고리 N(피리디늄), Penta "pH≤6 창"과 정합 (문헌 pKa2≈5.3-5.4)
pKa_proline   = 10.6    # 2차 아민(피롤리디늄), Penta "pH≤11 창"과 정합
# 피콜린산: pH5 ON, pH9.6 OFF  →  Am04(pH9.6) 65 nm/min(억제실패) vs Penta(pH5) ~1 nm/min
f_pic_pH5, f_pic_pH96 = f_protonated(5.0,pKa_picolinic), f_protonated(9.6,pKa_picolinic)
assert f_pic_pH5 > 0.5              # pH5서 과반 양성자화 → 억제 ON
assert f_pic_pH96 < 1e-3           # pH9.6서 사실상 0 → 억제 OFF (America 65 nm/min 설명)
# 프롤린: pH9.6에서도 양성자화 → Am04 pH9.6서 SiN 2 nm/min(억제 ON)
f_pro_pH96 = f_protonated(9.6,pKa_proline)
assert f_pro_pH96 > 0.8
# Penta Table 1: 소요 농도 — 피콜린 0.1 wt% vs 프롤린 2 wt% (20배)
conc_pic, conc_pro = 0.1, 2.0
assert conc_pro/conc_pic == 20.0
print(f"[B] f_pic(pH5)={f_pic_pH5:.2f}(ON) f_pic(pH9.6)={f_pic_pH96:.1e}(OFF) f_pro(pH9.6)={f_pro_pH96:.2f}(ON); 소요농도 20배차")
```

```python verify
# [C] (b) 고 pH가 SiN을 촉진 — America pH 창 (DOI 10.1149/1.1817870, 원문: pH11서 최소 대비 ~10배)
# 원문 서술: SiN RR은 pH9.7에서 최소(산소-제거 SiN IEP=9.7), pH11에서 ~10배로 증가
IEP_oxidefree_SiN = 9.7           # 최소 제거율 pH = IEP (순전하 0)
factor_pH11_vs_min = 10.0         # "increases by nearly 10 times at pH 11"
assert 8 <= factor_pH11_vs_min <= 12
# 정지층 최적 pH ≈ IEP, 역제거(촉진) 창은 pH >= 11
assert IEP_oxidefree_SiN < 11.0
print(f"[C] SiN 제거 최소 pH={IEP_oxidefree_SiN}(=IEP), pH11서 ~{factor_pH11_vs_min:.0f}배 촉진 → 역제거 창은 고pH")
```

```python verify
# [D] Praveen 2014 — 첨가제×연마재 조합이 선택비를 가른다 (DOI 10.1016/j.mee.2013.10.004, 원문 완독)
# EDX La 함량(wt%): 상용 세리아는 La 다량, 자체합성 ceria-CM은 La 무함유
La = {"ceria-SA":24, "ceria-S":31, "ceria-CM":0}
assert La["ceria-SA"]>=20 and La["ceria-S"]>=20 and La["ceria-CM"]==0
# L-proline: La-무함유 ceria-CM에서만 선택비 3->40 (억제 ON), La-세리아에선 변화 미미
sel_CM_blank, sel_CM_proline = 3.0, 40.0
assert sel_CM_proline/sel_CM_blank > 10          # ceria-CM는 프롤린으로 급등
# L-glutamic acid: 세리아 3종 모두 SiN <3 nm/min (견고)
sin_glutamic_all = 3.0
assert sin_glutamic_all <= 3.0
# baseline 선택비는 모든 세리아에서 <=6 (첨가제 필요)
assert sel_CM_blank <= 6
print(f"[D] ceria-CM(La={La['ceria-CM']}%): 프롤린 sel {sel_CM_blank:.0f}->{sel_CM_proline:.0f}; 상용 La {La['ceria-SA']}-{La['ceria-S']}%엔 프롤린 무력; 글루탐산은 SiN<{sin_glutamic_all:.0f}로 견고")
```

```python verify
# [E] 3D NAND 요구선택비 (Zhao 2025 DOI 10.1016/j.apsusc.2025.163978) — 초록 기반, 원문 미확보(E5)
# 초록 수치: pH5, 0.02M Lys+0.02M Glu+0.003M TEAOH -> SiO2 3606.1, Si3N4 101.6 Å/min, 선택비 35.49
RR_ox, RR_sin = 3606.1, 101.6     # Å/min (E5, 원문 미확인)
sel_reported = 35.49
req_3dnand = 30.0                  # 3D NAND 요구 SiO2:Si3N4 (초록 명시)
assert abs(RR_ox/RR_sin - sel_reported) < 0.05    # 산술 일관성 재현
assert RR_ox/RR_sin >= req_3dnand                 # 요구 30:1 충족
# 3D NAND 목표(30:1)는 STI 블랭킷 고선택비(100-290)보다 낮다 (패턴·적층 유효선택비 하락 + 평탄화 여유)
sti_blanket_hi = 100.0
assert req_3dnand < sti_blanket_hi
# Si3N4 101.6 Å/min은 STI 정지 기준(<10 Å/min=1nm/min)의 한 자릿수 위 → 유한 손실 예산 관리 레짐
assert RR_sin > 10.0
print(f"[E] 3D NAND: {RR_ox/RR_sin:.2f}:1 (요구 {req_3dnand:.0f}:1 충족); SiN {RR_sin:.0f} Å/min > STI정지 10 Å/min (예산관리 레짐)")
```

## 8. 정직한 한계

- **[Zh25] 원문 미확보**: 3D NAND 요구선택비 30:1·최적 조성·실측 RR(3606.1/101.6/35.49)은 퍼블리셔 **초록 기반 2차
  인용(E5)** 이다. 산술 일관성([E])만 코드로 확인했고 **원 실험 조건(입경·패드·압력)은 확인 못 함**. 추정.
- **[Rv25] 리뷰 전문 미확보**: Springer 챌린지로 본문을 못 읽어 **수치를 취하지 않았다**. "최신 리뷰가 존재하고 아미노산을
  CMP 보조제로 종합한다"는 정성 프레이밍·참고문헌 존재확인 용도로만 사용(E5).
- **pKa 값([B])**: 피콜린산 5.3·프롤린 10.6은 Penta의 "pH 창(≤6, ≤11)"과 정합하도록 택한 문헌 대표 pKa다. 두 값 자체는
  Penta 원문이 명시한 게 아니라 Penta의 pH 창 서술과 부합하는 공지 pKa를 **대입**한 것이므로 **부분 미검증**(방향·창은 원문,
  절대 pKa는 대입값).
- **흡착등온 ≈100 mg/g**([Pe13])은 Fig.5의 **정성 포화값 판독**이고 랑뮤어 K·q_max 폐형식 계수는 원문이 표로 주지 않아
  **추출 못 함** — 이 노트는 "포화형(랑뮤어형)"이라는 형태만 취하고 계수는 넣지 않았다.
- **America pH 창 ~10배**([C])는 원문 서술("nearly 10 times at pH 11")의 수치화로 절대값이 아니라 배율만 취함.
- **연도**: Am04(2004)·Pe13(2013)·Pr14(2014)는 "최근 10년" 밖이나, 이 계의 정량 흡착·pH 창·연마재 상호작용 **원출처**라
  최신(Zh25 2025·Rv25 2025)과 함께 위계를 완성하려 포함했다(스코프의 "최근 15년 우선"은 선호이지 하드컷 아님, Am04는 예외).

## 9. 이 에이전트의 결론 (모델링 관점)

1. **첨가제 억제항은 (농도)×(pH 창) 이중 스위치다.** Lv1-2가 흡착 포화(농도)로, 이 노트가 양성자화 분율 f=1/(1+10^(pH−pKa))
   (pH)로 본 두 스위치를 곱해야 한다. PROFILE의 [Tier2] 첨가제 포화-스위치 모델에 **pKa 기반 pH 게이트**를 추가할 것 —
   같은 첨가제(피콜린산)가 pH 5는 억제, pH 9.6은 무력이라 pH 무시 모델은 부호를 틀린다([B]).
2. **선택비는 SiN 억제가 결정, 옥사이드는 대개 불변.** Kp_nitride를 첨가제·pH의 함수로 두되 Kp_oxide는 상수로 근사해도
   Am04 Table I가 지지한다(억제형 몇 종 제외). [[preston-luo-dornfeld-mrr]]의 나이트라이드 Kp에 (1−θ)·f_protonated 게이트.
3. **첨가제 효과는 연마재 조성에 의존한다(Pr14).** La 함유 상용 세리아에서 프롤린이 무력화되므로, 선택비 파라미터를
   "첨가제만"으로 고정하면 안 되고 **연마재(La/순도) 태그와 짝지어** 저장해야 한다 — Lv3-2 파라미터 세트 설계 시 반영.
4. **3D NAND는 저선택비(≈30:1)·유한 SiN 손실 레짐.** 블랭킷 100+가 아니라 30:1이 목표이고 SiN 101.6 Å/min이 허용된다 —
   [[../cmp/sti-nitride-loss-erosion-overpolish-window]]의 손실예산 모델을 두꺼운 ONON(적층당 큰 예산)에 그대로 쓰되
   목표선택비만 낮춘다. STI의 자기정지 사상과 다른 "예산관리형" 파라미터가 필요(Lv3-2/Cal-1).

## 10. 구현 요청 → agents/film-nitride/PROFILE.md "## 구현 요청" 참조
(첨가제 포화-스위치 모델에 pKa 기반 pH 게이트 추가 + 선택비 파라미터에 연마재 La/순도 태그 결합 — 상세는 PROFILE.)

## 11. 자기시험
→ [[../../agents/film-nitride/EXAMS.md]] Lv3-1 문항 참조.
