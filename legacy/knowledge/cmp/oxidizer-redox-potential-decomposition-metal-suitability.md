<!-- V2-SECTION: R2-slurry | 분배완료 2026-09-08 | 근거: chemistry, oxidizer, redox, 산화제, 화학 | 정본: ARCHITECTURE-V2.md §3 -->
# CMP 산화제 화학 — H₂O₂·KIO₃·Fe(NO₃)₃의 산화전위·분해속도·금속별 적합성

> 에이전트: slurry-chemistry Lv1-1 | 작성일: 2026-09-10
> [[surface-chemistry-cu-w-pourbaix-passivation]] [[slurry-components-overview]] [[cu-electrochemistry-pourbaix-bta-oxidizer-inhibitor]] [[ceria-slurry-ce-redox-selectivity]] [[metal-contamination-device-impact-irds-limits]] [[preston-luo-dornfeld-mrr]]

## 1. 왜 필요한가 — "무른 막을 만드는 엔진"의 열역학·속도론
[[slurry-components-overview]]와 [[surface-chemistry-cu-w-pourbaix-passivation]]는 산화제가 **맨금속→무른 산화막**을 만들고(Kaufman 경쟁모델) 연마입자가 그 막을 벗긴다는 **메커니즘**을 정성적으로 다뤘다. 이 노트는 그 앞단 — **"어떤 산화제가 왜 그 금속을 산화할 수 있는가"** 를 표준환원전위(E°)로 정량화하고, 산화제 자체의 **분해 속도**(슬러리 수명·현장혼합 이유)와 **금속 오염 적합성**(front-end vs back-end)을 파고든다. CMP 3대 산화제는 학위논문에서도 명시된 대로 **과산화수소 H₂O₂·질산철 Fe(NO₃)₃·요오드산칼륨 KIO₃** 이다(McAllister, "Novel Studies in Silicon Dioxide, Copper and Tungsten Chemical Mechanical Planarization," PhD dissertation, Univ. of Arizona, 2019, §1.1.3 — papers/mcallister2019-dissertation-ua.pdf, 원문 확보·직접 인용: "The most common oxidizers are hydrogen peroxide, ferric nitrate and potassium iodate").

## 2. 표준환원전위 E° — 세 산화제의 "산화력" 순위
출처(1차 레퍼런스, 직접 판독): P. Vanýsek, "Electrochemical Series," *CRC Handbook of Chemistry and Physics*(Physical Chemistry handbook 판, /tmp에서 fitz로 표 직접 추출). 25°C, vs SHE(표준수소전극).

| 반쪽반응(산성) | E° (V) | 비고 |
|---|---|---|
| H₂O₂ + 2H⁺ + 2e⁻ → 2H₂O | **+1.776** | 가장 강한 산화제 |
| 2IO₃⁻ + 12H⁺ + 10e⁻ → I₂ + 6H₂O | +1.195 | (I₂까지 환원 경로) |
| IO₃⁻ + 6H⁺ + 6e⁻ → I⁻ + 3H₂O | **+1.085** | (I⁻까지 완전 환원, CMP에서 흔히 채택) |
| Fe³⁺ + e⁻ → Fe²⁺ | **+0.771** | 셋 중 가장 약함, 1전자 |
| (참고) O₂ + 4H⁺ + 4e⁻ → 2H₂O | +1.229 | 용존산소 |
| (참고) O₂ + 2H⁺ + 2e⁻ → H₂O₂ | +0.695 | H₂O₂ 산화(→O₂) 반쪽 |

금속 쪽 상대전극(같은 표, 산성):

| 반쪽반응 | E° (V) |
|---|---|
| WO₃ + 6H⁺ + 6e⁻ → W + 3H₂O | **−0.090** |
| WO₂ + 4H⁺ + 4e⁻ → W + 2H₂O | −0.119 |
| Cu²⁺ + 2e⁻ → Cu | **+0.342** |
| (참고) MoO₂ + 4H⁺ + 4e⁻ → Mo + 4H₂O | −0.152 |

**핵심**: 산화력 순위 H₂O₂ ≫ IO₃⁻ > Fe³⁺. 산화제가 금속을 산화하는 열역학 구동력은 셀전위 `E_cell = E°(산화제) − E°(금속)`이고, `E_cell>0`이면 열역학적으로 산화가 자발적(ΔG = −nFE_cell < 0). W는 표준전위가 매우 낮아(−0.090 V) 세 산화제 **모두** 자발 산화하나, Cu(+0.342 V)에 대해서는 Fe³⁺의 구동력이 확 줄어든다. §5에서 코드로 재현.

## 3. H₂O₂의 자발적 분해 — 왜 슬러리 수명이 짧고 현장혼합(point-of-use)을 하는가
H₂O₂는 산화제인 **동시에** 스스로 불균등화(disproportionation)하는 열역학적 불안정 화학종이다:

$$2\,\text{H}_2\text{O}_2 \rightarrow 2\,\text{H}_2\text{O} + \text{O}_2\uparrow$$

이는 위 표의 두 반쪽반응 합이다 — 환원(H₂O₂→2H₂O, +1.776 V)과 산화(H₂O₂→O₂, +0.695 V의 역). 셀전위 = 1.776 − 0.695 = **+1.081 V > 0** → **자발**. 즉 H₂O₂는 "가만 둬도 물+산소로 붕괴하려는" 화학종이고, 상온에서 붕괴가 느린 것은 순전히 **속도론적 활성화 장벽** 덕이다. 이 장벽을 **전이금속(Fe·Cu·Mn 등)이 촉매**로 낮춘다:

- **Fenton형 촉매 사이클**(Fe(NO₃)₃가 촉매로 작동하는 경로): `Fe²⁺ + H₂O₂ → Fe³⁺ + OH⁻ + ·OH` (빠름), 이어 `Fe³⁺ + H₂O₂ → Fe²⁺ + HO₂· + H⁺` (느림, 율속). 순반응은 H₂O₂ 촉매분해 + 하이드록실 라디컬(·OH) 생성.
- 생성된 ·OH는 강산화종이라 W 산화를 **가속**한다 — Fe+H₂O₂ 혼합 슬러리가 단독보다 W 제거율이 높은 이유([[surface-chemistry-cu-w-pourbaix-passivation]] §3의 Fenton 서술과 정합).
- 대가: **슬러리 pot-life 단축**. H₂O₂가 소모·기포화되므로 산업 W/Cu CMP는 H₂O₂를 연마 직전에 섞는 **현장혼합(point-of-use blending)** 을 표준으로 한다.

속도론 앵커(2차 인용, DOI는 기계검증됨): J. De Laat & H. Gallard, "Catalytic Decomposition of Hydrogen Peroxide by Fe(III) in Homogeneous Aqueous Solution: Mechanism and Kinetic Modeling," *Environ. Sci. Technol.* 33(16):2726–2732 (1999), https://doi.org/10.1021/es981171v. Fe²⁺+H₂O₂ 속도상수 k₁≈63 M⁻¹s⁻¹, Fe³⁺+H₂O₂ 개시단계는 ~10⁴배 느림(k≈2×10⁻³ M⁻¹s⁻¹ 오더) — **개별 k 절대값은 2차 인용(원문 유료 미독), 오더·순위만 채택**. §5에서 순위를 코드로 재현.

**KIO₃·Fe(NO₃)₃는 이런 자기분해가 없다**: 요오드산염·질산철은 안정한 염이라 저장 중 붕괴·기포·라디컬 생성이 없다. → **저장안정성은 KIO₃·Fe(NO₃)₃ 우위, 그러나 오염 문제(§4)로 상쇄**.

## 4. 금속별 적합성 — 오염(contamination) 관점이 실제 선택을 가른다
열역학(§2)상 셋 다 W·Cu를 산화할 수 있다면, 실제 선택은 **속도론 + 금속오염 + 선택비**가 정한다. 특히 **도입 금속이온의 소자 오염 위험**([[metal-contamination-device-impact-irds-limits]])이 결정적:

| 산화제 | 도입 이온 | 오염 위험 | 주 용도 |
|---|---|---|---|
| **H₂O₂** | 없음(→H₂O+O₂) | **최저** — 금속프리, 분해산물 청정 | Cu/W 두루, front-end 선호 |
| **Fe(NO₃)₃** | Fe³⁺ | **높음** — Fe는 Si 내 deep-level trap(소수캐리어 수명 킬러) | 주로 back-end W plug, 오염 우려로 축소 추세 |
| **KIO₃** | K⁺, I | **중간** — K⁺는 이동성 알칼리이온(게이트산화막 신뢰성 위협) | 특수 용도, front-end 회피 |

- **H₂O₂**: 분해산물이 물·산소뿐이라 금속오염이 없어 가장 범용적이나(불안정성은 현장혼합·안정제로 관리), 산화력이 가장 강해 억제제(BTA 등) 없이는 Cu를 과부식.
- **Fe(NO₃)₃**: Fe는 실리콘 밴드갭 중앙 근처 깊은 준위를 만들어 극미량(10¹⁰ atoms/cm² 오더)도 소자 특성을 해친다([[metal-contamination-device-impact-irds-limits]]) → 알루미나 연마 강산성(pH≈2.5) W plug 슬러리에 국한, 최신 라인은 Fe-free로 이동. Fe³⁺는 pH 비의존 산화제(§5.3)라 강산성에서도 산화력 유지가 장점.
- **KIO₃**: 자체는 안정·청정하지만 K⁺(이동성 알칼리)와 요오드 잔류가 front-end에 부담. 상대적으로 온건한 산화력(+1.085 V)으로 선택비 제어에 쓰이나 범용성은 낮다.

## 5. 정량 재현 (코드) — 세 개의 assert 증명
핵심 대조 결과 먼저: §5.2는 H₂O₂ 불균등화 ΔG를 전기화학 경로(Vanýsek CRC E°)와 표준생성깁스(CRC ΔfG°) 두 방법으로 **대조**해 문헌값끼리 **1.15% 이내 일치**를 재현한다(서로 독립인 두 데이터셋이 수렴하므로 우연 아님; Nernst 기울기 근거는 [[surface-chemistry-cu-w-pourbaix-passivation]]).

### 5.1 산화 구동력 순위 & W/Cu 자발성
```python verify
# CMP 3대 산화제의 금속 산화 열역학. E°는 Vanysek(CRC Handbook)에서 직접 판독.
F = 96485.0  # C/mol

# 표준환원전위 (V vs SHE, 25°C) — CRC/Vanysek 전기화학 시리즈
E = {
    'H2O2': 1.776,   # H2O2 + 2H+ + 2e- -> 2H2O
    'IO3':  1.085,   # IO3- + 6H+ + 6e- -> I- + 3H2O
    'Fe':   0.771,   # Fe3+ + e- -> Fe2+
    'WO3_W':  -0.090,  # WO3 + 6H+ + 6e- -> W + 3H2O
    'Cu':      0.342,  # Cu2+ + 2e- -> Cu (표는 0.3419, 3자리 반올림)
}

# 산화력 순위: H2O2 > IO3- > Fe3+
assert E['H2O2'] > E['IO3'] > E['Fe'], "산화제 E° 순위가 문헌과 어긋남"

# 셀전위 E_cell = E(산화제) - E(금속). >0 이면 산화 자발(dG<0)
for metal, Em in [('W', E['WO3_W']), ('Cu', E['Cu'])]:
    for ox in ('H2O2', 'IO3', 'Fe'):
        Ecell = E[ox] - Em
        # W는 셋 다 자발 산화해야 한다(E°가 매우 낮음)
        if metal == 'W':
            assert Ecell > 0, f"{ox}가 W를 산화 못함? Ecell={Ecell:.3f}"
        print(f"{ox:5s} + {metal}: E_cell={Ecell:+.3f} V")

# 대표 정량: H2O2에 의한 W 산화 (WO3 형성, n=6 전자)
Ecell_H2O2_W = E['H2O2'] - E['WO3_W']   # +1.866 V
dG_kJ = -6 * F * Ecell_H2O2_W / 1000.0   # kJ per mol 반응
assert abs(Ecell_H2O2_W - 1.866) < 1e-3
assert dG_kJ < -1000  # 강한 자발성 (-1080 kJ/mol 오더)
print(f"H2O2->W(WO3), n=6: E_cell=+1.866 V, dG={dG_kJ:.0f} kJ/mol (강한 자발)")

# Fe3+의 Cu 산화 구동력은 W 대비 확 줄어든다(선택성의 씨앗)
assert (E['Fe'] - E['Cu']) < (E['Fe'] - E['WO3_W'])
print(f"Fe3+ 구동력: W {E['Fe']-E['WO3_W']:+.3f} V vs Cu {E['Fe']-E['Cu']:+.3f} V")
```

### 5.2 H₂O₂ 자발분해 — 전기화학 vs 생성깁스 두 경로 교차검증
```python verify
# 2 H2O2 -> 2 H2O + O2 가 자발(dG<0)임을 독립 두 방법으로 확인.
F = 96485.0

# (A) 전기화학: E_cell = E(cathode: H2O2/H2O) - E(anode: O2/H2O2)
E_cat = 1.776   # H2O2 + 2H+ + 2e- -> 2H2O
E_an  = 0.695   # O2 + 2H+ + 2e- -> H2O2  (H2O2 산화의 역)
E_disp = E_cat - E_an
assert abs(E_disp - 1.081) < 1e-3, "불균등화 셀전위 오차"
dG_ec = -2 * F * E_disp / 1000.0   # kJ per 2 mol H2O2 (n=2)
assert dG_ec < 0  # 자발

# (B) 표준생성깁스에너지 (CRC): dGf(H2O2,aq)=-134.03, dGf(H2O,l)=-237.14, O2=0 kJ/mol
dGf_H2O2, dGf_H2O = -134.03, -237.14
dG_form = 2*dGf_H2O + 0 - 2*dGf_H2O2   # kJ per 2 mol H2O2
assert dG_form < 0  # 자발

# 두 경로 일치(반올림·데이터 출처 차이로 수 % 오차 허용)
rel = abs(dG_ec - dG_form) / abs(dG_form)
assert rel < 0.03, f"전기화학({dG_ec:.1f})과 생성깁스({dG_form:.1f}) 불일치 {rel:.1%}"
print(f"불균등화 dG: 전기화학 {dG_ec:.1f} kJ vs 생성깁스 {dG_form:.1f} kJ (per 2 mol), 차이 {rel:.1%}")
print("=> H2O2는 열역학적으로 반드시 분해. 상온 안정성은 순전히 속도론 장벽 덕.")

# Fenton 순위: Fe2+ 경로가 Fe3+ 개시보다 압도적으로 빠름 (2차 인용 오더)
k_Fe2, k_Fe3 = 63.0, 2e-3   # M^-1 s^-1, De Laat & Gallard 1999 오더 (절대값 미검증)
assert k_Fe2 / k_Fe3 > 1e4, "Fe2+ 경로 우세 순위가 안 나옴"
print(f"Fenton 속도비 k(Fe2+)/k(Fe3+) ~ {k_Fe2/k_Fe3:.0e} => 미량 Fe2+가 H2O2 분해 촉발")
```

### 5.3 Nernst pH 의존성 — 왜 Fe³⁺가 강산성 W 슬러리에 맞는가
```python verify
# 산화제 전위의 pH 기울기 dE/dpH = -0.0591 * (m/n)  (m=H+ 계수, n=전자수, 25°C)
# [[surface-chemistry-cu-w-pourbaix-passivation]] §2의 Nernst 기울기 공식 적용.
slope = lambda m, n: -59.1 * m / n   # mV/pH

# H2O2 (m=2,n=2) 와 IO3-/I- (m=6,n=6) 는 둘 다 -59.1 mV/pH (pH 오르면 산화력 약화)
assert abs(slope(2, 2) - (-59.1)) < 1e-6
assert abs(slope(6, 6) - (-59.1)) < 1e-6

# Fe3+/Fe2+ (m=0,n=1): H+ 미관여 -> pH 무관
assert abs(slope(0, 1) - 0.0) < 1e-9
print("H2O2, IO3-/I-: -59.1 mV/pH (pH↑ 시 산화력↓)")
print("Fe3+/Fe2+: 0 mV/pH (pH 무관)")

# 결과 해석: pH 2.5 W 슬러리에서 H2O2 실효전위는 표준 대비 ~ -0.148 V 낮아지지만
# Fe3+는 변화 없음 -> 강산성에서 Fe3+가 상대적으로 유리(단, H+가 반응식에 없어 별도 이점).
dE_H2O2_at_pH25 = slope(2, 2) * 2.5 / 1000.0  # V
assert abs(dE_H2O2_at_pH25 - (-0.148)) < 2e-3
print(f"pH2.5에서 H2O2 전위 이동 {dE_H2O2_at_pH25*1000:.0f} mV, Fe3+ 0 mV")
```

## 6. 종합 — 산화제 선택 원리
1. **열역학(E°)은 "가능/불가능"만 정한다**: W는 E°가 낮아 셋 다 산화 가능, 실제 선택은 속도론·오염·선택비가 결정.
2. **H₂O₂ = 가장 강하지만 스스로 붕괴**: 금속오염 최저(청정 분해산물)라 범용이나 pot-life 짧아 현장혼합 필수. 전이금속(Fe) 존재 시 Fenton으로 분해 가속 + ·OH로 산화 촉진(양날).
3. **Fe(NO₃)₃ = 안정하지만 Fe 오염**: pH 무관 산화력이 강산성 W plug에 맞으나 Fe deep-level trap 문제로 축소.
4. **KIO₃ = 안정·온건하지만 K⁺·요오드 잔류**: 선택비 제어용, front-end 회피.
5. 이 산화 화학이 [[surface-chemistry-cu-w-pourbaix-passivation]]의 passivation막 형성과 [[preston-luo-dornfeld-mrr]] $K_p$의 화학 성분을 채운다.

## 7. 한계/미검증 (정직 표기)
- **E° 값(§2)**은 Vanýsek CRC 표에서 직접 판독한 **표준 열역학값(1차 레퍼런스)** 이나, 실제 슬러리는 착화제·pH·활동도로 **형식전위(formal potential)** 가 표준값에서 벗어난다 — §2 표는 방향성·순위 근거이지 실 슬러리 절대전위가 아니다.
- **Fenton 속도상수 k(§3,§5.2)**: De Laat & Gallard 1999 DOI는 기계검증(Crossref)됐으나 원문 유료로 본문 미독 — 개별 k 절대값은 2차 인용, 코드는 **순위(오더비)만** assert하고 절대값은 신뢰하지 않는다.
- **금속오염 임계치**(Fe deep-level, K⁺ 이동이온)는 [[metal-contamination-device-impact-irds-limits]]에 위임 — 이 노트는 정성 방향만.
- **Nernst pH 기울기(§5.3)**는 이상 활동도·단일 우세종 가정 하의 이론값 — 실제 Pourbaix 경계는 종·농도에 따라 −29.6/−59.1 mV/pH 등으로 갈린다([[surface-chemistry-cu-w-pourbaix-passivation]] §2).

## 8. 자기시험
→ [[../../agents/slurry-chemistry/EXAMS.md]] Lv1-1 문항 참조.
