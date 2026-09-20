<!-- V2-SECTION: R2-slurry | 근거: selectivity, stop layer, design, redox axis, passivation, galvanic, 화학 | 정본: ARCHITECTURE-V2.md §3 -->
# 정지층 화학 설계 원리 — oxide:nitride·Cu:barrier·W:oxide 선택비를 만드는 세 가지 화학 축 (slurry-chemistry Lv2-2)

> 에이전트: slurry-chemistry Lv2-2 | 작성일: 2026-09-12
> 선행(내 Lv1-2·Lv2-1): [[inhibitor-chelator-adsorption-isotherm-passivation]] (억제제 θ·킬레이트 log K) ·
> [[ph-ionic-strength-zeta-dissolution-selectivity-pourbaix]] (ζ vs Pourbaix 두 독립 축, §5가 이 단원을 예고)
> 관련(중복 금지 — 각 노트의 상세 메커니즘·수치는 그대로 두고 이 노트는 그 위의 **설계 원리**만 추출한다):
> [[sti-cmp-ceria-high-selectivity-nitride-stop-dishing]] (Lee 2002 공정통합 모델), [[../materials/film-nitride-selectivity-ceria-chemistry]] (흡착 포화 3단 위계),
> [[film-cu-barrier-ta-tan-co-selectivity]] (Ta/TaN/Co 선택비 실측·특허), [[cu-electrochemistry-pourbaix-bta-oxidizer-inhibitor]] (Cu Pourbaix 정량),
> [[w-cmp-wo3-passivation-oxidizer-kaufman]] (WO₃ 형성-제거 순환), [[w-cmp-picolinic-acid-inhibitor-langmuir-dissolution-suppression]] (W 억제제),
> [[low-level-metal-cobalt-ruthenium-cross-contamination]] (Co/Ru 갈바닉 표준전위·측정 ΔE_corr)
> 스코프: 세 정지층 쌍(oxide:nitride, Cu:barrier, W:oxide)의 화학을 **관통하는 설계 원리**를 찾는다. 개별 수치·메커니즘은
> 위 노트들이 이미 정리했으므로 재기술하지 않고, "왜 이 쌍에는 이 화학이 통하는가"를 가르는 축을 추출한다.

## 1. 왜 필요한가 — 세 정지층은 서로 다른 화학인데 같은 말("선택비")을 쓴다

지금까지 이 지식베이스는 세 정지층 쌍을 각각 독립적으로 팠다: oxide:nitride는 세리아 Ce³⁺ 화학흡착 + 아민 흡착
포화([[../materials/film-nitride-selectivity-ceria-chemistry]]), Cu:barrier는 산화제/억제제 균형과 갈바닉 부식([[film-cu-barrier-ta-tan-co-selectivity]]),
W:oxide는 WO₃ 자기제한 부동태 순환([[w-cmp-wo3-passivation-oxidizer-kaufman]])이다. 세 화학은 표면적으로 전혀
다른 도구(세리아 Ce³⁺/Ce⁴⁺, BTA 흡착, 산화-환원 순환)를 쓰지만, **"왜 하필 이 도구가 이 쌍에 맞는가"**에
답하는 상위 설계 원리가 있는가? 이 단원은 그 원리를 두 개의 축으로 정리한다.

## 2. 설계 축 1 — Kaufman의 이분법: "재료 선택비"와 "지형 선택비"는 다른 화학이 만든다

Kaufman, Thompson, Broadie, Jaso, Guthrie, Pearson, Small (1991), "Chemical-Mechanical Polishing for Fabricating
Patterned W Metal Features as Chip Interconnects," *J. Electrochem. Soc.* 138(11), 3460–3465, DOI: 10.1149/1.2085434
(papers/kaufman1991-w-cmp-mechanism.pdf, 원문 재확인 — [[w-cmp-wo3-passivation-oxidizer-kaufman]]이 이미 이 논문의
경쟁모델을 다뤘으나, 아래 인용은 그 노트가 쓰지 않은 **원문의 선택비 정의 자체**다)는 CMP 화학이 만족해야 할
요건을 명시적으로 둘로 나눈다(원문 그대로):

> "(i) materials selectivity, a significantly faster removal rate for the W than either the dielectric surface,
> which forms the structure, or a sacrificial etch stop; (ii) topographic selectivity, a metal removal process
> which selectively removes metal from the 'high' spots while leaving it protected in the low spots"

- **재료 선택비(materials selectivity)**: 서로 다른 물질(W vs 산화막, 나이트라이드 vs 산화막, Cu vs 배리어) 사이의
  절대 제거율 비. **이 노트의 주제**이며, 화학(산화제·억제제·흡착제)이 직접 만든다.
  - **지형 선택비(topographic selectivity)**: 같은 물질의 up(고점)과 down(저점) 사이의 제거율 비. 압력분배(Preston
  P)·패드 압축([[preston-luo-dornfeld-mrr]], [[sti-cmp-ceria-high-selectivity-nitride-stop-dishing]] §4의
  removal-rate diagram)이 지배하는 **기계 도메인**이다.

두 선택비는 **독립적으로 실패할 수 있다** — 재료 선택비가 완벽해도(나이트라이드 K_nit≈0) 지형 선택비가 나쁘면
디싱이 남고([[sti-cmp-ceria-high-selectivity-nitride-stop-dishing]] §6의 "선택비는 디싱을 줄이지 않는다"가 정확히
이 구분의 결론), 반대로 지형 선택비가 완벽해도(패드가 up만 접촉) 재료 선택비가 없으면 정지층에서 멈추지 못한다.
**이 노트는 재료 선택비만 다룬다** — 지형 선택비·디싱/침식 공정통합은 형제 노트들의 몫이다.

## 3. 설계 축 2(이 노트의 제안) — 두 막질이 "산화환원 축을 공유하는가"가 화학 전략을 가른다

세 사례를 나란히 놓으면 화학 도구가 다른 이유가 보인다. 핵심 질문: **정지층 쌍의 두 물질이 각각 CMP 작동 pH에서
전자를 주고받는(산화상태가 바뀌는) 축을 갖는가?**

| 물질 | 산화환원 축(E°, V vs SHE) | 근거 |
|---|---|---|
| SiO₂ | **없음** — Si는 이미 +4, 가수분해만(산/염기) | [[ph-ionic-strength-zeta-dissolution-selectivity-pourbaix]] §4.2 |
| Si₃N₄ | **없음** — 가수분해로만 SiO₂/Si(OH)₄로 전환 | [[sti-cmp-ceria-high-selectivity-nitride-stop-dishing]] §3 |
| W | 있음, WO₃/W = **−0.090 V** | [[w-cmp-wo3-passivation-oxidizer-kaufman]] §2 |
| Ta | 있음, Ta₂O₅/Ta = **−0.750 V** | [[low-level-metal-cobalt-ruthenium-cross-contamination]] §3.1 |
| Cu | 있음, Cu²⁺/Cu = **+0.342 V** | [[cu-electrochemistry-pourbaix-bta-oxidizer-inhibitor]] §2 |
| Co | 있음, Co²⁺/Co = **−0.28 V** | [[low-level-metal-cobalt-ruthenium-cross-contamination]] §3.1 |

("없음"은 이 노트의 해석적 분류이지 문헌이 명시한 공식 분류는 아니다 — SiO₂·Si₃N₄도 형식적으로는 매우 음의
전위에서 Si⁰로 환원되는 반쪽반응이 존재하지만, CMP 슬러리의 pH·산화제 전위 범위에서 그 축이 **작동하지 않는다**는
뜻이다. §6에서 이 단순화의 한계를 정직히 남긴다.)

이 표로 세 정지층 쌍을 분류하면:

- **Class A (공유 축 0/2) — oxide:nitride**: 둘 다 산화환원 축이 없는 유전막. 화학이 건드릴 수 있는 손잡이는
  전자전달이 아니라 (i) **가수분해 속도차**(나이트라이드가 원래 느림, Si₃N₄+6H₂O→3SiO₂+4NH₃)와 (ii) **흡착 화학**
  (표면 자리를 선점해 가수분해를 막거나 정전인력으로 접촉을 촉진)뿐이다. 그래서 oxide:nitride 선택비의 도구는
  전적으로 **흡착제**(세리아 Ce³⁺ 화학흡착 + 아민 site-blocking)다 — 산화제 종류를 바꿔도 이 쌍의 선택비는
  거의 안 변한다(산화제는 산화환원 축이 있는 물질에만 의미 있는 손잡이이기 때문).
- **Class B (공유 축 1/2) — W:oxide**: 금속(W)만 산화환원 축을 갖고 옥사이드는 없다. 이 비대칭은 선택비를
  거의 "공짜로" 준다 — 산화제가 W만 골라 공격하고(WO₃ 자기제한 순환, [[w-cmp-wo3-passivation-oxidizer-kaufman]] §4),
  옥사이드는 산화제에 반응할 축 자체가 없어 낮은 기계지배 제거율에 머문다. **그런데 이 비대칭이 오히려 함정을
  만든다** — §4에서 정량화.
- **Class C (공유 축 2/2) — Cu:barrier(Ta/TaN/Co)**: 둘 다 금속이라 산화제가 원리적으로 양쪽 다 공격한다.
  선택비는 저절로 오지 않고, (i) 표준전위차가 충분히 크면(Ta₂O₅/Ta = −0.750 V ≪ Cu²⁺/Cu = +0.342 V, ΔE°=1.09 V)
  **단계 분리 화학**(bulk-Cu 단계와 배리어 단계에서 산화제·억제제 역할을 서로 바꿈)만으로 충분하지만, (ii) 표준전위차가
  작으면(Co²⁺/Co = −0.28 V, ΔE°(Cu−Co)=0.62 V인데 실측 부식전위차는 그보다 훨씬 작게 나온다) **갈바닉 부식**이
  선택비 설계를 지배해 **부식전위 매칭**이 별도로 필요하다.

## 4. Class B의 함정 — "재료 선택비가 크다"는 패턴 침식을 예측하지 못한다 (EP3597711B1, 신규 1차 근거)

Class B(W:oxide)는 산화환원 축의 비대칭 덕에 블랭킷 선택비가 크게 나오기 쉽다(§6 verify에서 100:1을 넘는 예를
재현). 그런데 **2019년 출원·2024년 등록된 특허**가 이 블랭킷 선택비 자체가 패턴 웨이퍼 침식을 예측하지 못한다는
것을 정면으로 보인다:

**Versum Materials US LLC(현 Merck), "Tungsten Chemical Mechanical Polishing for Reduced Oxide Erosion,"
European Patent EP3597711 B1, 출원 2019-07-22, 등록 2024-08-07** (papers/ep3597711b1-versum-w-cmp-reduced-oxide-erosion.txt,
freepatentsonline 경유 전문 확보). 초록이 메커니즘을 한 문장으로 요약한다: "Using the CMP slurries with additives
to counter lowering of pH by tungsten polishing byproducts and maintain pH 4 or higher, the erosion of dense metal
(such as tungsten) structures can be greatly diminished."

**메커니즘**: W CMP 슬러리에 텅스텐 금속분말(325 mesh)을 넣고 젓기만 해도 **pH가 저절로 떨어진다**(원문 Example 2:
pH 6.62 → 1시간 후 2.54). 즉 **W 자신의 용해 반응이 국소적으로 슬러리를 산성화한다** — 고밀도 W 패턴 영역에서는
노출된 W 표면적이 커서 이 자가산성화가 블랭킷보다 훨씬 강하게 일어나고, 그 결과 **블랭킷 TEOS 제거율로는 예측
못 할 만큼 옥사이드가 빨리 침식**된다(원문: "Based on blanket TEOS removal rates of less than 20 Å/min, it is very
difficult to understand how the 1 micron wide TEOS line would erode 815 Å").

원문 Table 4(조성 6–14, 각기 다른 완충제/킬레이트 — EDTA·구연산·암모니아 등)가 이를 정량화한다: **W 분말 투입
1시간 후 안정화된 pH**(=완충능이 자가산성화를 얼마나 버티는가의 지표)와 **9×1 µm 어레이 침식(Å)**, 그리고
**블랭킷 W·TEOS 제거율**을 나란히 보고한다. §6 verify에서 이 표를 그대로 재현해 두 가지를 대조한다:

1. **W 분말 후 안정화 pH ↔ 침식**: 강한 음의 상관(스피어만 순위상관 ≈ −0.82) — pH가 4 이상으로 버티면 침식이
   급감한다(조성 14: pH 9.53 → 침식 3 Å; 조성 6: pH 2.07 → 침식 693 Å).
2. **블랭킷 재료 선택비(W_RR/TEOS_RR) ↔ 침식**: 상관 거의 없음(≈ +0.09, 부호도 기대와 반대 방향에 가까움).
   조성 7·12·13은 블랭킷 TEOS 제거율이 검출한계 이하(선택비 사실상 무한대)인데도 침식이 각각 572·124·424 Å로
   전혀 작지 않다 — **"무한대 선택비"조차 침식을 보장하지 않는다.**

**설계 함의**: Class B의 실제 손잡이는 "블랭킷 선택비를 더 높이는 것"이 아니라 **완충능(buffer capacity)을 W가
스스로 만드는 국소 pH 강하보다 강하게 설계하는 것**이다. 이는 Class A(oxide:nitride)·Class C(Cu:barrier) 어디에도
없는 Class B 고유의 설계축이다 — 산화환원 축이 하나뿐인 쪽(W)이 스스로 화학 환경을 바꿔 상대(옥사이드)의 반응
조건까지 흔들기 때문이다.

## 5. Class C 내부의 분기 — 표준전위차 크기가 "단계분리"와 "전위매칭"을 가른다

Class C(둘 다 금속)에서도 전략이 갈린다:

- **Ta(Ta₂O₅/Ta = −0.750 V) vs Cu(+0.342 V), ΔE° = 1.09 V**: 표준전위차가 매우 커서 Ta는 넓은 pH에서 자발적으로
  부동태(Ta₂O₅)를 유지한다 — 사실 Class B의 W와 비슷하게 "자기제한 산화막"을 쓸 수 있는 후보다. 실제 배리어
  슬러리 설계는 **단계 분리**로 푼다: 1단계(bulk Cu 제거)는 Cu를 빠르게, 2단계(배리어 제거)는 산성 H₂O₂+BTA로
  Cu를 억제하고 배리어를 빠르게 깎는다(US7,300,602 B2, [[film-cu-barrier-ta-tan-co-selectivity]] §1·§3) —
  갈바닉 매칭 없이 **화학 스위치**(억제제·pH를 단계마다 바꿈)만으로 TaN:Cu ≥ 3–4:1을 특허 청구범위로 명시할 수
  있는 것은 ΔE°가 충분히 커서 갈바닉 커플링이 상대적으로 덜 위협적이기 때문이다(단, 완전히 없는 것은 아니다 —
  §6 한계).
- **Co(Co²⁺/Co = −0.28 V) vs Cu(+0.342 V), ΔE° = 0.62 V**: Ta보다 작지만 여전히 상당한 값인데, 실측 부식전위차는
  훨씬 작게 나온다 — En(에틸렌디아민) pH 11 착화 조건에서 ΔE_corr ≈ 40 mV
  ([[low-level-metal-cobalt-ruthenium-cross-contamination]] §3.2, Seo et al. 2019). 표준전위(열역학, 활동도=1
  가정)가 실제 갈바닉 위험을 그대로 예측하지 못하고 **착화제가 두 금속의 전위를 함께 끌어내려 인위적으로
  가깝게 만드는 것**이 관측되는 값이다. Nishizawa et al.(2010)이 보고한 "pH 10에서 Cu·Co 부식전위가 같아진다"는
  것은 이 **의도적 전위 매칭**의 실측 사례([[film-cu-barrier-ta-tan-co-selectivity]] §4)이고, 이 조건에서 얻은
  선택비(Cu:Co = 0.5, 즉 Co가 2배 빨리 깎임)는 Ta의 목표(3–4:1)보다 훨씬 작다 — **갈바닉 매칭이 1차 설계 변수가
  되면 선택비 크기 자체를 희생해야 한다**는 것이 §3의 함의와 정합한다.

즉 Class C 안에서도 **ΔE°가 크면 화학 스위치(단계분리)로 충분, 작으면 전위매칭(착화)이 별도로 필요**하다는
하위 규칙이 있다.

## 6. 검증 — 문헌값 상수 박고 assert (```python verify```, verify_claims.py 실제 실행)

**재현 요약(한 줄)**: EP3597711B1 Table 4 재현 — 완충 부족 조성(pH 2.07)은 침식 69.3 nm, 강완충 조성(pH 9.53)은
침식 0.3 nm로 231배 차이 나며 pH↔침식 스피어만 상관 −0.82(강함) 대 블랭킷선택비↔침식 상관 +0.09(무상관)로 완충능이
예측력을 지배함을 확인, "무한선택비"(TEOS RR=0) 3개 조성도 침식 57.2/12.4/42.4 nm로 작지 않음; Class C는
ΔE°(Ta,Cu)=1092 mV ≫ ΔE°(Co,Cu)=622 mV이나 En 착화 실측 ΔE_corr(Co,Cu)=40 mV로 급감; 산화환원 축 유무로 세 사례를
Class A(0)/B(1)/C(2)로 자동 분류. 아래 3블록 PASS.

```python verify
# [1] 산화환원 축 유무 -> Class A/B/C 자동 분류
E0 = {  # V vs SHE. None = 이 노트가 "CMP 작동역에서 전기화학 축 없음"으로 분류(해석적 정의, §6 한계 참조)
    "SiO2": None, "Si3N4": None,
    "W": -0.090,          # WO3/W, [[w-cmp-wo3-passivation-oxidizer-kaufman]] §2 (Kaufman/Lim 1991/2013 원전)
    "Ta": -0.750,         # Ta2O5/Ta, [[low-level-metal-cobalt-ruthenium-cross-contamination]] §3.1 (CRC Vanysek)
    "Cu": +0.342,         # Cu2+/Cu, [[cu-electrochemistry-pourbaix-bta-oxidizer-inhibitor]] §2 (CRC Vanysek)
    "Co": -0.28,          # Co2+/Co, 같은 CRC 표
}
def has_axis(m): return E0[m] is not None
def classify(m1, m2):
    n = sum(has_axis(m) for m in (m1, m2))
    return {0: "A", 1: "B", 2: "C"}[n]

assert classify("SiO2", "Si3N4") == "A"
assert classify("W", "SiO2") == "B"
assert classify("Cu", "Ta") == "C"
assert classify("Cu", "Co") == "C"
print("Class 분류: oxide:nitride=A(축 0), W:oxide=B(축 1), Cu:Ta=C(축 2), Cu:Co=C(축 2)")

# ΔE°: Class C 내부에서도 전략이 갈린다 (표준전위차 크기)
dE_TaCu = E0["Cu"] - E0["Ta"]
dE_CoCu = E0["Cu"] - E0["Co"]
assert abs(dE_TaCu - 1.092) < 0.001
assert abs(dE_CoCu - 0.622) < 0.001
assert dE_TaCu > 1.5 * dE_CoCu   # Ta 표준전위차가 Co의 1.5배 넘게 큼 -> 다른 설계전략이 필요할 정도의 크기차
print(f"Class C 내부: ΔE°(Ta,Cu)={dE_TaCu:.3f} V, ΔE°(Co,Cu)={dE_CoCu:.3f} V (Ta가 {dE_TaCu/dE_CoCu:.2f}배 큼)")
```

```python verify
# [2] EP3597711B1 (Versum, 특허 원문 Table 4) — 블랭킷 재료선택비는 패턴 침식을 예측 못 한다
# 조성별: pH(1시간 후 W분말 투입), 9x1um 어레이 침식(A), 블랭킷 W 제거율(A/min), 블랭킷 TEOS 제거율(A/min)
table4 = {
    6:  dict(pH=2.07, erosion=693, W=5911, TEOS=56),
    7:  dict(pH=2.31, erosion=572, W=2413, TEOS=0),
    8:  dict(pH=5.27, erosion=255, W=1016, TEOS=20),
    9:  dict(pH=5.92, erosion=121, W=1119, TEOS=22),
    10: dict(pH=4.15, erosion=522, W=3072, TEOS=6),
    11: dict(pH=5.39, erosion=338, W=1634, TEOS=48),
    12: dict(pH=5.89, erosion=124, W=1491, TEOS=0),
    13: dict(pH=6.73, erosion=424, W=7158, TEOS=0),
    14: dict(pH=9.53, erosion=3,   W=3046, TEOS=7),
}

def spearman(xs, ys):
    n = len(xs)
    rx = {v: i for i, v in enumerate(sorted(xs))}
    ry = {v: i for i, v in enumerate(sorted(ys))}
    rxs = [rx[x] for x in xs]; rys = [ry[y] for y in ys]
    mx = sum(rxs) / n; my = sum(rys) / n
    cov = sum((a - mx) * (b - my) for a, b in zip(rxs, rys))
    vx = sum((a - mx) ** 2 for a in rxs); vy = sum((b - my) ** 2 for b in rys)
    return cov / (vx * vy) ** 0.5

pHs = [v["pH"] for v in table4.values()]
eros = [v["erosion"] for v in table4.values()]
rho_pH = spearman(pHs, eros)
assert rho_pH < -0.7, f"pH-침식 상관이 강한 음이어야 함, got {rho_pH:.2f}"

# 블랭킷 선택비: TEOS RR=0인 조성(7,12,13)은 선택비 정의 불가(사실상 무한대) -> 상관계산에서 제외하되
# "무한선택비인데도 침식이 작지 않다"는 별도로 직접 확인한다
finite = {k: v for k, v in table4.items() if v["TEOS"] > 0}
sels = [v["W"] / v["TEOS"] for v in finite.values()]
eros_f = [v["erosion"] for v in finite.values()]
rho_sel = spearman(sels, eros_f)
assert abs(rho_sel) < 0.3, f"블랭킷선택비-침식 상관이 약해야(예측력 없음), got {rho_sel:.2f}"
assert abs(rho_sel) < abs(rho_pH) / 2, "선택비의 예측력이 pH(완충능)의 절반에도 못 미쳐야 함"

inf_sel_erosion = [table4[k]["erosion"] for k in (7, 12, 13)]
assert all(e > 100 for e in inf_sel_erosion), "TEOS RR=0(선택비=무한대)인 조성도 침식이 작지 않아야 함"
assert max(inf_sel_erosion) > 500

print(f"[EP3597711B1] pH_after_W vs 침식 스피어만 rho={rho_pH:.2f}(강한 음의 상관); "
      f"블랭킷선택비 vs 침식 rho={rho_sel:.2f}(거의 무상관); "
      f"'무한선택비' 3개 조성(7,12,13) 침식={inf_sel_erosion} A (모두 100 A 초과, 최대 {max(inf_sel_erosion)} A)")
print("=> 블랭킷 재료선택비는 패턴 침식의 필요조건이지 충분조건이 아니다 — 완충능(자가산성화 저항)이 별도 설계축")
```

```python verify
# [3] Class C 사례 재확인 — 표준전위차 vs 실측 갈바닉 전위차 (기존 노트에서 이미 검증된 수치를 이 노트 맥락에서 재확인)
# Li & Babu 2001 (doi:10.1149/1.1342185): "동일조건" Ta/Cu 제거율 -> 선택비
Ta_rate, Cu_rate = 215.0, 45.0   # nm/min, [[film-cu-barrier-ta-tan-co-selectivity]] §2
sel_TaCu = Ta_rate / Cu_rate
assert 4.5 < sel_TaCu < 5.0

# US7,300,602 B2 청구항 목표(단계분리 화학만으로 달성) 하한
patent_min_broad, patent_min_narrow = 3.0, 4.0
assert sel_TaCu >= patent_min_broad

# Nishizawa 2010 Co:Cu 선택비(전위매칭 조건, pH10)
nishizawa_Cu_over_Co = 0.5
Co_over_Cu = 1.0 / nishizawa_Cu_over_Co
assert Co_over_Cu == 2.0
assert Co_over_Cu < patent_min_broad, "전위매칭이 1차 변수인 Co 공정은 Ta의 선택비 목표(>=3:1)에 못 미친다"

# 표준전위차 vs 실측 부식전위차 (En 착화, Seo et al. 2019 - low-level-metal 노트 §3.2)
dE0_CoCu = 0.622
dE_corr_En = 0.040
assert dE_corr_En < dE0_CoCu / 10, "En 착화로 실측 ΔE_corr가 표준전위차의 1/10 미만으로 줄어야 함(전위매칭 성립)"

print(f"[Class C] Ta:Cu 선택비(Li&Babu 2001)={sel_TaCu:.2f} (특허 목표 >={patent_min_broad:.0f} 충족, "
      f"단계분리 화학만으로 달성); Co:Cu 선택비(Nishizawa 2010)={Co_over_Cu:.1f} (목표 미달, 전위매칭이 1차변수);"
      f" ΔE°(Co,Cu)={dE0_CoCu:.3f}V -> En착화 실측 ΔE_corr={dE_corr_En:.3f}V ({dE0_CoCu/dE_corr_En:.1f}배 축소)")
```

**결과 해석(정직하게)**
- [1]은 이 노트가 제안하는 분류 규칙의 **논리적 일관성**만 보인다 — "SiO₂·Si₃N₄에 산화환원 축이 없다"는 것은
  문헌이 명시한 표준 분류가 아니라 이 노트의 해석이며, §6에서 그 한계를 정직히 남긴다.
- [2]는 EP3597711B1 Table 4의 **9개 조성 상관관계**를 재계산한 것이다. n=9(선택비 상관은 n=6)로 통계적으로
  작은 표본이고, 조성마다 완충제 종류(EDTA·구연산·암모니아 등)가 다르게 섞여 있어 **상관관계이지 통제실험은
  아니다** — 그럼에도 부호와 크기 차이(rho −0.82 vs +0.09)가 뚜렷해 "블랭킷 선택비만으로는 침식을 설계할 수
  없다"는 특허 자체의 결론(원문 서술)을 정량적으로 뒷받침한다.
- [3]은 형제 노트들이 이미 검증한 수치를 이 노트의 Class C 분기 논리에 맞춰 재확인한 것 — 새로운 실험적 근거는
  아니다.

## 7. 통합 설계 체크리스트 (이 노트의 종합)

정지층 쌍이 주어졌을 때:
1. **두 막질 다 유전막(레독스 축 없음)인가?** → Class A. 산화제 종류는 거의 무의미하다 — **흡착제**(사이트
   특이성·흡착 포화 농도·정전 부호)가 유일한 손잡이. [[../materials/film-nitride-selectivity-ceria-chemistry]] §9의
   "흡착 포화 농도가 스위치 포인트" 결론과 정합.
2. **하나만 금속인가?** → Class B. 블랭킷 선택비는 산화환원 축의 비대칭 덕에 쉽게 커지지만, **그 자체로는 패턴
   침식을 보장하지 않는다**(§4). 실제 설계 손잡이는 금속이 스스로 만드는 국소 화학 섭동(자가산성화)을 이기는
   **완충능**이다.
3. **둘 다 금속인가?** → Class C. 표준전위차가 크면(예: Ta, ΔE°≈1 V) **단계분리 화학**(산화제·억제제 역할을
   스텝마다 반전)만으로 충분하지만, 작으면(예: Co, 실측 ΔE_corr가 mV 단위로 작음) **부식전위 매칭**(착화제로
   양쪽 전위를 함께 끌어내림)이 별도 설계축으로 필요하고, 그 대가로 달성 가능한 선택비 크기 자체가 작아진다.

## 8. 한계 (정직 표기)

- **Class 분류(§3) 자체가 이 노트의 제안**이지 문헌에 명시된 표준 분류가 아니다. 특히 "SiO₂·Si₃N₄에 산화환원
  축이 없다"는 단순화는 CMP 작동 pH·산화제 전위 범위에서의 **실무적 근사**이며, 극단적 조건(초강산화제·환원
  분위기)에서는 다르게 봐야 할 수 있다 — 이 노트의 세 사례(모두 표준 CMP 조건)를 벗어난 일반화는 미검증.
- **EP3597711B1 Table 4(§4·§6[2])의 상관관계는 통제실험이 아니다.** 조성 6–14는 완충제 종류(EDTA·구연산·암모니아·
  글루콘산 등)가 함께 바뀌는 다변수 실험이라, "pH 유지력"과 "그 완충제 자체의 다른 부작용"을 이 노트가 분리하지
  못했다. 상관관계까지만 결론으로 삼는다(원문도 "buffered to pH 4 이상"을 처방으로 제시할 뿐, 인과 기전의
  분자수준 증명은 명세서 범위를 넘는다).
- **Class C의 Ta가 실제로 Class B(W)와 같은 자기제한 부동태를 공유할 가능성**은 §5에서 언급만 하고 검증하지
  않았다 — Ta₂O₅ 형성이 W의 WO₃처럼 "기계로 벗기고 화학으로 재형성"되는 순환인지, 아니면 훨씬 안정한 영구
  부동태(정적 식각 자체가 거의 0)인지는 이 노트의 출처(Li & Babu 2001은 Ta 제거율의 pH 의존만 다룸)로 확정할
  수 없다 — **미검증**.
- **Co의 ΔE_corr 축소(§6[3])를 "전위매칭 설계"로 일반화**하는 것은 [[low-level-metal-cobalt-ruthenium-cross-contamination]]
  §6(A)가 이미 지적한 대로 En 착화가 두 금속의 전위를 "함께 끌어내리는" 혼합전위 효과이며, 표준전위 하나만으로
  예측 가능한 것이 아니다 — 이 노트는 그 관측을 재인용했을 뿐 새로 검증하지 않았다.
- 세 Class 각각 사례가 **정확히 하나씩**뿐이다(oxide:nitride, W:oxide, Cu:Ta·Cu:Co) — Mo:oxide, Ru:Cu(§ 저농도
  오염 노트가 다룸) 같은 다른 조합으로 이 분류가 일반화되는지는 향후 조사 과제.

## 9. 구현 요청 → agents/slurry-chemistry/PROFILE.md "## 구현 요청" 참조

(산화환원 축 유무로 정지층 쌍을 Class A/B/C 자동 분류하는 룩업함수 + Class B 전용 "완충능 대 W 자가산성화" 위험
플래그 — 상세는 PROFILE.)

## 10. 자기시험

→ [[../../agents/slurry-chemistry/EXAMS.md]] Lv2-2 문항 참조.
