<!-- V2-SECTION: R2-slurry | 근거: 텅스텐 CMP 의 pH → MRR 관계(산성역), 산화제 매개 -->
# 텅스텐 CMP 의 pH 의존성은 **산화제가 있을 때만** 존재한다 — 산성역 로그선형 k≈0.116/pH

> 에이전트: slurry-chemist (χ PARTIAL 갭 — w_fe_oxidizer 팩에 pH 통로가 없었다) | 작성일: 2026-09-15
> 선행: [[tungsten-cmp-oxidizer-passivation-kaufman-model]] 계열 · [[chi-oxidizer-concentration-curve-exponent-derivation]]
> 관련 팩: `knowledge/params/w_fe_oxidizer.yaml` (`w_ph_acid_k`, `ph_ref`)
> 관련 코드: `sim/factors.py::_ph_w_acidic_term`

## 1. 문제 — W 팩의 χ 는 산화제 농도 하나만 보고 있었다

`accuracy_gaps.py --next` 가 준 최우선 갭은 **PARTIAL χ (terms=['oxidizer'], 3팩)** 였다.
`w_fe_oxidizer` 팩에서 χ 의 drivers 에 `slurry_ph` 가 등록돼 있는데도 실제 항은
`oxidizer` 하나뿐이다 — **pH 를 바꿔도 출력이 안 변한다.** 실리카 산화막 계열은
`_ph_peak_term`(Li 2021 정점형), 세리아 계열은 `_ph_ceria_electrostatic_term`(IEP 창)을
갖고 있지만, 금속 W 계에는 대응하는 항이 없었다. 산화막의 정점형을 그대로 빌려오면
메커니즘이 달라 부호까지 틀릴 수 있다(세리아에서 ρ=−0.525 로 드러났던 것과 같은 결함).

## 2. 출처 (1차 전문 확보)

| # | 출처 | 등급 | 확보 |
|---|---|---|---|
| S1 | J. Stojadinović, D. Bouvet, S. Mischler (2016), "Prediction of Removal Rates in Chemical–Mechanical Polishing (CMP) Using Tribocorrosion Modeling", *J. Bio- Tribo-Corros.* **2**:8. DOI: 10.1007/s40735-016-0041-4 | **E2** (동일 슬러리계, pH 만 HCl 로 바꾼 대응쌍 4조) | 전문 PDF `papers/stojadinovic2016-tribocorrosion-w-cmp.pdf` |
| S2 | 같은 논문 §5.1.1 의 Nernst 유도 (W + 3H₂O → WO₃ + 6H⁺ + 6e⁻) | E2 (폐형식 유도) | 위와 동일 |

S1 Table 1 이 이 노트의 근거다. **3 % 실리카(12 nm) 고정, KIO₃ 농도 4수준 고정,
장비·압력(5 psi)·회전수(50/60 rpm)·유량 전부 고정한 채 HCl 로 pH 만 5 → 2 로 내린**
대응쌍이다. 교란이 통제된 1축 DOE 이므로 EVIDENCE-RULES 의 E2 에 해당한다.

## 3. 원문 수치 (Table 1, 인용 — 판독 아님)

| KIO₃ (wt%) | RR @ pH 5 (Å/min) | RR @ pH 2 (Å/min) | 비 (pH2/pH5) |
|---|---|---|---|
| 0.0 | 40 | 25 | **0.625** |
| 0.1 | 140 | 200 | 1.429 |
| 0.5 | 750 | 1150 | 1.533 |
| 2.0 | 1500 | 1950 | 1.300 |
| 4.0 | 1600 | NA | — |

부수 사실(같은 표): OCP 가 pH 5 → 2 에서 전 구간 양의 방향으로 이동
(예: 0.5 % KIO₃ 에서 −356 → −75 mV), 논문은 이를 RR 증가의 원인으로 지목한다.

## 4. 새로 도출한 지식 — pH 효과는 **산화제 매개**다 (부호가 뒤집힌다)

표의 첫 행이 결정적이다. **산화제가 없으면 pH 를 내려도 MRR 이 오히려 줄어든다**
(40 → 25, 비 0.625). 산화제가 있는 세 조건에서만 비가 1.30~1.53 로 일관되게 1 을 넘는다.
즉 pH 는 W 를 직접 깎는 게 아니라 **산화(WO₃ 생성) 구동력을 통해서만** MRR 에 들어온다.
이것은 S2 의 Nernst 식과 정합한다: E_rev = −0.119 − 0.059·pH 이므로 pH 5→2 에서
구동 전위가 0.177 V 커진다(논문 서술 "180 mV" 와 일치). 산화제가 없으면 이 구동력을
실현할 산화종이 없으므로 전위 이득이 MRR 로 번역되지 않는다.

**함수형**: 산화제 존재 3조건의 비를 로그평균하면 ln(ratio)=0.3488 (Δ pH = 3),
로그선형 계수 **k = 0.1163 /pH unit**. 즉

    f(pH) = exp(−k · (pH − pH_ref)),  k = 0.1163

지수형을 고른 이유는 (a) 열역학 구동력이 pH 에 선형(Nernst)이고 (b) 속도가 구동력에
지수적으로 반응하는 것이 전기화학의 표준(Tafel)이기 때문이다 — 임의의 곡선맞춤이 아니다.
다만 Tafel 기울기로부터 k 를 독립 유도한 것은 아니므로 **등급은 literature(E2)**, verified 아님.

**적용 게이트**: 이 항은 팩이 `w_ph_acid_k` 를 선언할 때만 켜진다. 산화제가 없는 W 계
(비 0.625)는 부호가 반대이므로 이 항으로 덮으면 안 된다 — 그 레짐은 스코프 밖으로 둔다
(EVIDENCE-RULES "둘 다 맞되 레짐이 다르다" → 스코프 분리).

## 5. 정량 재현

```python verify
import math
# S1 Table 1 (원문 인용값), 3% 실리카 12nm, KIO3 4수준, pH만 5→2 (HCl)
tab = {0.0: (40, 25), 0.1: (140, 200), 0.5: (750, 1150), 2.0: (1500, 1950)}

# (1) 산화제 없을 때는 부호가 반대다 — 이 항의 적용 게이트 근거
assert tab[0.0][1] / tab[0.0][0] < 1.0
assert abs(tab[0.0][1] / tab[0.0][0] - 0.625) < 1e-9

# (2) 산화제 존재 3조건은 모두 1을 넘고 1.30~1.54 대역에 모인다
ratios = [tab[c][1] / tab[c][0] for c in (0.1, 0.5, 2.0)]
assert all(r > 1.0 for r in ratios)
assert 1.29 < min(ratios) and max(ratios) < 1.54

# (3) 로그평균에서 k 를 역산 → 0.1163 /pH
k = sum(math.log(r) for r in ratios) / len(ratios) / 3.0
assert abs(k - 0.11628) < 5e-5, k

# (4) 이 k 로 각 조건을 예측했을 때 오차 ±10% 이내 (완벽하진 않다 — 그대로 기록)
pred = math.exp(k * 3.0)
errs = [(pred - r) / r * 100.0 for r in ratios]
assert max(abs(e) for e in errs) < 10.0, errs
assert abs(errs[0]) < 1.0      # 0.1% KIO3: -0.8%
assert 7.0 < abs(errs[1]) < 8.0  # 0.5%: -7.6%
assert 8.0 < abs(errs[2]) < 10.0 # 2.0%: +9.0%

# (5) Nernst 교차검증: W + 3H2O -> WO3 + 6H+ + 6e-, dE/dpH = -0.059 V
#     논문 §5.1.1 은 pH 5->2 에서 180 mV 라고 적는다.
dE = 0.059 * 3.0
assert abs(dE - 0.177) < 1e-9
assert abs(dE - 0.180) < 0.005     # 논문 명시값과 3 mV 이내

# (6) 팩 기준조건(pH 2.5 = ph_ref)에서 팩터는 정확히 1.0 (이중계상 방지 계약)
f = lambda ph, ref=2.5: math.exp(-k * (ph - ref))
assert abs(f(2.5) - 1.0) < 1e-12
assert f(2.0) > 1.0 and f(4.0) < 1.0      # 산성일수록 빠르다
assert abs(f(2.0) - 1.0599) < 1e-3
print("OK k=%.5f  f(2.0)=%.4f f(2.5)=%.4f f(4.0)=%.4f" % (k, f(2.0), f(2.5), f(4.0)))
```

## 6. 한계 (숨기지 않는다)

1. **대리계다.** S1 의 산화제는 KIO₃(+ HCl), 우리 팩은 Fe(NO₃)₃ 다. 막질(W)·pH 영역
   (2~5)·산화 경로(WO₃ 부동태)는 같으나 산화제 화학종이 다르다 → E2 가 아니라 **E2/E3
   경계**로 본다. 같은 논문 Table 1 의 Fe(NO₃)₃ 계열(0.02 % 에서 pH 3.0, 0.05 % 에서
   pH 2.5)은 pH 와 농도가 동시에 움직여 교란돼 있어 k 를 뽑는 데 쓰지 않았다.
2. **2점 할선이다.** pH 2 와 5 두 점뿐이라 pH 2~5 **밖은 외삽 금지**. 코드에서 범위를
   벗어나면 노트에 경고를 남긴다.
3. **k 의 산포.** 3조건의 개별 k 는 0.0875~0.1426 (±22 %). 로그평균을 쓴 것이므로
   불확실도가 이만큼 남아 있다. confidence 를 verified 로 올리지 않은 이유다.
   지수형(Tafel) 가정 자체는 **미검증**이다 — 2점 할선에서는 지수형과 선형을 구별할 수
   없다. 3점 이상이 확보되면 재판정해야 한다.
4. **알칼리역은 다른 이야기다.** Xu 2022 (doi:10.3390/mi13050762, 전문 코퍼스 보유)는
   pH 7→12 에서 W MRR 이 6.69→13.67 µm/h 로 **증가**한다고 보고한다 — 용해 지배 레짐이라
   부호가 반대다. CMP 실무 W 슬러리는 산성이므로 이 노트는 산성역으로 스코프를 한정하고,
   알칼리역은 "다른 레짐, 미모델링"으로 남긴다. 두 레짐의 경계 pH 는 **추정**이며
   (문헌이 명시하지 않음) 코드에서 경계를 두지 않고 범위 밖 경고로만 처리했다.
5. **RR 절대값은 우리 팩과 다르다**(장비·압력 상이). 이 항은 **배수**만 가져온다.
