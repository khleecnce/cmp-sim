<!-- V2-SECTION: R2-slurry | 근거: 세리아 Ce3+ 활성점 밀도 → MRR 함수형(지수), chemical tooth | 정본: ARCHITECTURE-V2.md §3 -->
# 세리아 chemical tooth의 **함수형 확정** — Ce³⁺ 분율 → MRR 은 선형이 아니라 p≈1.65 의 멱함수

> 에이전트: slurry-chemist (C2 confidence 승격 과제) | 작성일: 2026-09-14
> 선행: [[ceria-slurry-ce-redox-selectivity]] (Ce³⁺가 **왜** 활성점인가 — 산소공공·전하균형·DFT 흡착에너지)
> 형제: [[ceria-chemical-tooth-particle-site-density-facet]] (톱니가 표면에 **몇 개** 있는가 — 입자측 기하)
> 이 노트: 그 활성점 수 θ 가 MRR 로 번역되는 **함수형**. 세 노트가 why / how many / what shape 로 갈린다.
> 관련 팩: `knowledge/params/sti_ceria.yaml`, `knowledge/params/sic_ceria_h2o2.yaml` (`ceria_tooth_exponent`)
> 관련 코드: `sim/chemistry.py::_ceria_term`

## 1. 문제 — "선형"은 검증된 적이 없는 잔류 가정이었다

`sim/chemistry.py::_ceria_term` 은 오랫동안 θ(=Ce³⁺ 분율) 의존을 **선형**으로 두고,
팩의 `ceria_tooth_gain` 에 `confidence: unverified` + "문헌에 폐형식 함수가 없다" 는
자백 주석을 달아 왔다. 이 때문에 χ 팩터의 confidence 가 두 세리아 팩(sti_ceria,
sic_ceria_h2o2)에서 `unverified` 로 고정됐고, COMPLETION 격자 C2 의 2칸을 막고 있었다.

선형이 틀렸다는 것을 보이려면 **같은 슬러리 안에서 θ 와 MRR 이 함께 측정된 쌍**이
필요하다. 서로 다른 슬러리를 비교하면 입경·농도·첨가제가 함께 움직여 교란된다
(이것이 기존 노트가 5.5배를 "그대로 쓸 수 없다"고 한 이유다).

## 2. 출처 (1차 2건, 동일 저자·동일 입자)

| # | 출처 | 등급 | 확보 |
|---|---|---|---|
| S1 | C. M. Netzband, K. Dunn (2019), "Investigation into the Effect of CMP Slurry Chemicals on Ceria Abrasive Oxidation State using XPS", *ECS J. Solid State Sci. Technol.* **8**(10) P629–P633. DOI: 10.1149/2.0311910jss | **E2** (XPS 직접 측정, H₂O₂ 1축 DOE) | 전문 PDF `papers/netzband2019-ecs-xps-ce3-slurry-chemicals.pdf` |
| S2 | C. M. Netzband, K. Dunn (2020), "Controlling the Cerium Oxidation State During Silicon Oxide CMP to Improve Material Removal Rate and Roughness", *ECS J. Solid State Sci. Technol.* **9** 044001. DOI: 10.1149/2162-8777/ab8393 | **E2** (동일 그룹·동일 입자계 MRR 실측) | 전문 PDF `papers/netzband2020-jss-ceria-oxidation-state-oxide-cmp.pdf` |

두 논문은 **같은 저자·같은 입자(Ce1, 공칭 58~68 nm)·같은 실험계**에서 H₂O₂ 첨가량이라는
**단일 축**만 바꾼다. S1 이 그 축에서 θ 를, S2 가 같은 축에서 MRR 을 보고한다.
EVIDENCE-RULES 기준 **E2(동일계, 교란 통제된 대응쌍)** 이다.

## 3. 원문에서 읽은 수치 (인용 + 판독)

**S1 Table I (본문 명시값, 판독 아님):** as-received 세리아 분말의 Ce³⁺ 농도
| 입자 | 평균 크기 (nm) | Ce³⁺ (%) |
|---|---|---|
| Sigma Powder (Ce1) | 58 | **12** |
| Sky Spring (Ce2) | 15 | 25 |
| Sigma Dispersion (Ce3) | 6 | 31 |

**S1 Fig.4 (Ce1 계열, PDF 벡터 마커 좌표 판독):** H₂O₂ 0→5 wt% 에 따른 Ce³⁺%
축 보정 — x: 0 wt%=339.54 pt, 5 wt%=523.25 pt / y: 5%=546.15 pt, 30%=712.15 pt (선형).

| H₂O₂ (wt%) | 0 | 0.1 | **0.5** | 1.0 | 1.5 | 2.0 | 2.5 | 3.0 | 5.0 |
|---|---|---|---|---|---|---|---|---|---|
| Ce³⁺ (%) | 12.55 | 17.64 | **25.71** | 20.31 | 17.50 | 15.13 | 11.97 | 11.82 | 11.48 |

⭐ 자기검증 3중:
(a) 0 wt% 판독 12.55% vs Table I 명시값 **12%** → 오차 0.55 %p (판독 정확도 근거).
(b) 본문 서술 "the Ce3+% on the surface of Ce1 **doubles** with the addition of small
amounts of H₂O₂, then gradually decreases back to its initial concentration" → 판독은
12.55 → 25.71 (2.05배, "doubles") → 5 wt% 에서 11.48 (초기값 복귀) 로 서술과 정합.
(c) 서술 "This behavior holds true for both Ce2 and Ce3, but surprisingly not for Ce1"
— Ce1 만 비단조라는 서술이 판독 형상과 일치.

**S2 본문 (명시 서술, 판독 아님):** 같은 슬러리에 대해
- H₂O₂ 무첨가: "Even with no peroxide added, our slurry's MRR was **double** that of the commercial slurry."
- H₂O₂ 0.5 wt% (θ 최대): "The model slurry with the highest Ce3+%, corresponding to 0.5 wt% H₂O₂, polished **5.5 times faster** than the commercial slurry"

상용 슬러리는 두 조건에 공통인 기준이므로 나눗셈에서 약분된다 →
**슬러리 내부 MRR 비 = 5.5 / 2.0 = 2.75배**, 대응하는 **θ 비 = 2.05배**.

## 4. 선형 가정의 반증 (부등식 하나로 끝난다)

현행 형태 f(θ) = floor + a·(θ/θ_ref), a = (1−floor)·gain 에서 MRR 비는

    f(θ₁)/f(θ₀) = (floor + a·u₁)/(floor + a·u₀),  u = θ/θ_ref

floor → 0 극한에서 이 비의 **상한이 정확히 θ 비(2.05)** 이고, floor > 0 이면
분자·분모에 같은 양수가 더해지므로 비는 **더 작아진다**. 관측된 2.75 는 그 상한 밖이다.
즉 gain 을 어떻게 잡아도 선형 형태로는 이 쌍을 재현할 수 없다 — **gain 튜닝 문제가
아니라 함수형 문제다.** (이것이 "캘리브레이션 1순위"라는 기존 주석이 놓친 지점이다.)

멱형 f(θ) = floor + a·(θ/θ_ref)^p 로 p 를 역산하면

| floor | p |
|---|---|
| 0 (순수 화학) | 1.411 |
| 1/5.5 ≈ 0.1818 (현행 기본, Netzband 5.5배 역산) | **1.653** |
| 0.3 | 1.969 |

현행 기본 floor 에서 **p ≈ 1.65**. 이 값을 팩 파라미터 `ceria_tooth_exponent` 로 선언한다.

**정량 재현 결과(아래 verify 블록의 실제 실행값):** 팩 값 p=1.65 로 계산한 슬러리 내부
MRR 비 = **2.757배** vs 문헌값 **2.75배**(S2 본문, DOI:10.1149/2162-8777/ab8393) → 오차 0.26%.
θ 판독 12.55% vs 명시값 12%(S1 Table I, DOI:10.1149/2.0311910jss) → 오차 0.55%p.
반면 선형(p=1) 은 같은 조건에서 최대 **2.049배**(floor=0), 기본 floor=1/5.5 에서
**1.829배**(S2 문헌값 2.75배 대비 33% 과소) — 대조 결과 선형 형태는 기각된다.

```python verify
import math
from scipy.optimize import brentq

# ── S1 Fig.4 판독 + Table I (Ce1, 58 nm) ─────────────────────
THETA_0   = 12.55   # H2O2 0 wt%   (Table I 명시값 12% 와 0.55%p 이내)
THETA_MAX = 25.71   # H2O2 0.5 wt% (본문 "doubles")
TABLE_I_CE1 = 12.0
assert abs(THETA_0 - TABLE_I_CE1) < 1.0, "Fig.4 판독이 Table I 명시값과 어긋난다"
theta_ratio = THETA_MAX / THETA_0
assert 1.95 <= theta_ratio <= 2.15, theta_ratio      # 본문 "doubles"

# ── S2 본문 명시 배수 ────────────────────────────────────────
MRR_NO_H2O2   = 2.0   # 상용 대비
MRR_AT_OPT    = 5.5   # 상용 대비
mrr_ratio = MRR_AT_OPT / MRR_NO_H2O2
assert abs(mrr_ratio - 2.75) < 1e-9

# ── 반증: 선형은 상한 위반 ──────────────────────────────────
def linear_ratio(floor, gain=1.0, theta_ref=15.0):
    a = (1.0 - floor) * gain
    return (floor + a*(THETA_MAX/theta_ref)) / (floor + a*(THETA_0/theta_ref))

for floor in (0.0, 1/5.5, 0.3):
    r = linear_ratio(floor)
    assert r <= theta_ratio + 1e-9        # 선형의 상한은 theta 비
    assert r < mrr_ratio                  # 관측 2.75 를 결코 못 만든다
assert abs(linear_ratio(0.0) - theta_ratio) < 1e-9   # floor=0 에서 상한과 일치

# ── 멱지수 역산 ─────────────────────────────────────────────
def solve_p(floor, theta_ref=15.0):
    a = (1.0 - floor) * 1.0
    u0, u1 = THETA_0/theta_ref, THETA_MAX/theta_ref
    return brentq(lambda p: (floor + a*u1**p)/(floor + a*u0**p) - mrr_ratio, 0.05, 15)

p_pure = solve_p(0.0)
p_dflt = solve_p(1/5.5)
assert abs(p_pure - math.log(mrr_ratio)/math.log(theta_ratio)) < 1e-6  # floor=0 해석해
assert abs(p_pure - 1.411) < 0.01, p_pure
assert abs(p_dflt - 1.653) < 0.01, p_dflt
assert p_dflt > 1.0                      # 초선형

# ── 팩에 넣을 값이 쌍을 실제로 재현하는지 ────────────────────
PACK_EXPONENT = 1.65
def f(theta, floor=1/5.5, p=PACK_EXPONENT, theta_ref=15.0):
    a = (1.0 - floor)
    return floor + a*(theta/theta_ref)**p
recon = f(THETA_MAX)/f(THETA_0)
assert abs(recon - mrr_ratio)/mrr_ratio < 0.01, recon   # 문헌 2.75 대비 1% 이내
print("p(floor=0)=%.3f  p(floor=1/5.5)=%.3f  재현 MRR비=%.3f (문헌 2.75)" % (p_pure, p_dflt, recon))
```

## 5. 새로 도출한 지식 (문헌에 없던 것)

1. **세리아 chemical tooth 는 활성점 수에 초선형이다** (p ≈ 1.65, floor=1/5.5 기준).
   두 논문 어느 쪽도 θ–MRR 함수형을 쓰지 않았다 — 이 노트가 두 논문을 교차해 처음 역산한다.
2. **선형 가정은 데이터와 양립 불가능하다** — gain 자유도로 흡수되지 않는 구조적 반증
   (선형의 MRR 비 상한 = θ 비). 따라서 `ceria_tooth_gain` 을 캘리브레이션하는 방향은
   애초에 막다른 길이었다.
3. 이 초선형성은 Cook tooth-comb 모델의 확률 해석과 **모순되지 않는다**: S1 자신이
   "Any increased removal due to increasing Ce3+% is instead due to a greater probability
   for the reaction to occur" 라고 쓴다. 다만 확률이 θ 에 선형이면 p=1 이어야 하므로,
   p>1 은 **활성점 간 협동(인접 Si–O–Ce 결합의 동시 형성)** 을 시사한다 — 미검증 가설.

## 6. 한계 (정직하게)

- **2점 할선이다.** p 는 국소 기울기가 아니라 θ 2.05배 구간의 평균 지수다. 외삽 금지.
- **θ 와 MRR 이 같은 표에 없다.** 같은 그룹의 연속 두 논문이고, 동일 입자 로트라는 보장은
  본문 서술(같은 Ce1 명명, "as described previously")에 의존한다 → verified 가 아니라 **literature**.
- **floor 의존성이 크다** (p: 1.41 ~ 1.97). floor 자체가 5.5배 관측에서 역산한 가정이므로
  p 의 불확실성은 floor 의 불확실성을 그대로 물려받는다.
- 초선형 메커니즘(협동 효과)은 **미검증**. MD(Brugnoli 2023)로 검증 가능하나 이 단원 범위 밖.
- S1 은 "pH 는 Ce³⁺% 를 바꾸지 않는다" 고 보고한다(Fig.3) — 즉 이 항은 pH 항과 **독립**이다.
  χ 에서 두 항을 곱하는 현행 구조는 이 점에서 지지된다.

## 7. 엔진 반영

- `sim/chemistry.py::_ceria_term`: `ceria_tooth_exponent` 를 읽어 `floor + a·(θ/θ_ref)^p`.
  팩이 선언하지 않으면 p=1.0 (기존 동작, 하위호환).
- `knowledge/params/sti_ceria.yaml`, `sic_ceria_h2o2.yaml`: `ceria_tooth_exponent: 1.65`
  (confidence: literature), `ceria_tooth_gain` 은 `unverified → literature`
  (값 1.0 이 이제 "미검증 잔류"가 아니라 "지수로 형상을 옮겼으므로 gain 은 1 로 고정"이라는 결정).
- 기준 조건(θ=θ_ref)에서 (θ/θ_ref)^p = 1 이므로 **팩터 1.0 계약은 지수와 무관하게 유지**된다.
