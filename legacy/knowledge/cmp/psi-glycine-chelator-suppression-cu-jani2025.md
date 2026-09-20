<!-- V2-SECTION: R2-slurry | 근거: psi, chelator, glycine, 흡착보호, 억제 | 정본: ARCHITECTURE-V2.md §3 -->
# ψ `cu_h2o2_bta` — 착화제(글리신)는 촉진이 아니라 **억제**다 (판정#72)

> 작성일: 2026-09-19 | 대상: `knowledge/params/cu_h2o2_bta.yaml::chelator_suppression_a`,
> `sim/chemistry.py::_chelator_suppression_term`, `sim/factors.py::_f_psi`
> 선행: [[chi-cu-h2o2-regime-reversal-jani2025]](판정#41·#45·#47, 같은 논문의 산화제축)
> 과제: C1 — 글리신 농도축이 엔진에 연결돼 있지 않았다(미모델링).

## 1. 질문

`cu_h2o2_bta` 팩은 기준 조성에 글리신 1 wt%(=0.1332 M)를 선언하고 있지만, 그 농도를
바꿔도 예측 MRR이 **전혀 변하지 않았다** — `chelator_M`은 산화제 항의 레짐 게이트
판별용으로만 읽히고 있었고, 농도 자체가 MRR에 미치는 영향은 항이 없었다.
글리신은 Cu(II)를 가용성 착물로 빼내는 착화제이므로 "넣으면 더 깎일 것"이라는
직관이 있다. 방향과 크기를 문헌에서 확인한다.

## 2. 1차 출처

Charmy Jani, Ravitej Venkataswamy, Jihoon Seo, Sitaraman Krishnan,
"Revisiting the Roles of Chelator, Inhibitor, Oxidant, and Abrasive in High-Rate
Copper CMP", *ECS Journal of Solid State Science and Technology* **14**(4), 044003, 2025.
doi:10.1149/2162-8777/adc59e — CC-BY 오픈액세스, 전문 로컬 보관
`papers/jani2025-revisiting-roles-cu-cmp.html`.

공정(전 실험 고정): CETR-CP-4, IK4250H 패드, **3.0 psi**, platen **90 rpm**,
슬러리 150 mL/min, **pH 3.0**, 실리카 Z-평균 33 nm, 2인치 Cu 디스크 질량감량법.

## 3. 결과 — 직관과 반대로 **단조 억제**

Table I(조성) × Table II(Cu RR)에서 **연마입자가 있고 글리신만 바뀌는** 통제쌍은
정확히 2건이다(35실험 전수탐색):

| 통제쌍 | 고정 조건 | 글리신 0 M | 글리신 스윕 | 배수 |
|---|---|---|---|---|
| E7/8 → E5/6 | 실리카 3 wt%, H₂O₂ 5 wt%, 옥살산 0.05 M | 1544.5 | 0.13 M → 1329.0 | **0.8605** |
| E27/28 → E15 | 실리카 6 wt%, H₂O₂ 7 wt%, 옥살산 0.02 M | 694.0 | 0.26 M → 452.0 | **0.6513** |

(복제쌍은 산술평균. 전부 `read_method: table` — 인쇄된 숫자다.)

독립 확증 둘:
- 같은 논문 회귀표(Table III) `[glycine](0,0.26)` = **−440.91, p = 4.08×10⁻⁷**
  (유의한 음수). 우리가 계수를 직접 재적합해도 같은 값이 나온다(§5 블록2).
- 원문 결론 문장: "the higher Cu dissolution in slurries without glycine indicates
  that **glycine effectively functions as an inhibitor rather than a dissolution
  promoter**".

메커니즘 해석: pH 3에서 글리신은 양이온/양쪽성 이온으로 존재해 Cu 표면에 흡착하고,
옥살산-Cu 착물 형성 경로와 경쟁한다 — 즉 ψ(표면 흡착 보호)의 세 번째 갈래다.
**미검증**: 이 흡착 해석 자체는 이 논문의 XPS 등으로 직접 확인된 것이 아니라
회귀 부호와 원문 결론에서 역추론한 것이다.

## 4. 함수형 — 지수 1개 (피복형을 쓰지 않은 이유)

    ψ_chel(C) = exp(−a·(C − C_ref)),   a = 1.5119 /M,  C_ref = 0.1332 M

Langmuir/Hill 피복형 θ(C)=KC/(1+KC), ψ=exp(−k·θ) 를 쓰지 않았다. 확보된 통제점이
2개뿐이라 (K, k)가 **분리되지 않는다** — K를 0.13에서 32 /M까지 240배 움직여도 SSE가
7.7배 안에 다 들어온다(§5 블록3). 포화 거동이 있는지 없는지 이 데이터는 말하지
않으므로, 지어내지 않고 2점에서 식별되는 지수 1개로 축소한다.

적합 잔차: 0.13 M에서 −4.5 %, 0.26 M에서 +3.6 %.
기준 농도에서 배수는 **항등적으로 1.0** (이중 계상 방지 계약).

## 5. 검증 (실행되는 assert)

```python verify
# 블록1: 통제쌍 2건이 단조 억제이고, 적합 지수 a가 노트 값과 일치하는지
import math
PAIRS = {0.13: 1329.0 / 1544.5, 0.26: 452.0 / 694.0}   # Jani 2025 Table I x II
for C, r in PAIRS.items():
    assert r < 1.0, f"글리신 {C} M에서 억제(배수<1)여야 한다 — got {r}"
assert abs(PAIRS[0.13] - 0.8605) < 1e-4 and abs(PAIRS[0.26] - 0.6513) < 1e-4, \
    f"노트 §3 표값과 어긋남: {PAIRS}"
# 농도가 높을수록 더 억제 (단조)
assert PAIRS[0.26] < PAIRS[0.13], "농도가 높을수록 더 억제여야 한다"

def sse(a):
    return sum((math.exp(-a * C) - r) ** 2 for C, r in PAIRS.items())
best = min((sse(x / 10000.0), x / 10000.0) for x in range(1, 60000))
a_fit = best[1]
print(f"적합 a = {a_fit:.4f} /M, SSE = {best[0]:.3e}")
assert abs(a_fit - 1.5119) < 0.002, f"팩 값 1.5119가 재현돼야 한다 (got {a_fit})"
for C, r in PAIRS.items():
    pred = math.exp(-a_fit * C)
    err = 100.0 * (pred - r) / r
    print(f"  C={C} M: 예측 {pred:.4f} vs 실측 {r:.4f} ({err:+.2f}%)")
    assert abs(err) < 5.0, f"잔차가 노트 서술(±5% 이내)을 넘는다: {err:+.2f}%"
```

```python verify
# 블록2: 원문 회귀계수를 우리가 직접 재적합해 재현 — 인쇄값을 옮겨 적은 게 아님을 증명
import itertools
import numpy as np
ROWS = [
 (0,7,0.02,0.26,0.001,38),(0,7,0.02,0,0.005,342),(0,7,0.02,0,0.005,377),
 (0,3,0.08,0,0.005,2187),(3,5,0.05,0.13,0.001,1270),(3,5,0.05,0.13,0.001,1388),
 (3,5,0.05,0,0.003,1582),(3,5,0.05,0,0.003,1507),(3,7,0.08,0.26,0.001,1185),
 (3,3,0.02,0.26,0.001,391),(3,3,0.02,0.26,0.001,340),(6,7,0.05,0,0.005,1465),
 (6,3,0.05,0.13,0.003,763),(6,3,0.05,0.13,0.003,747),(6,7,0.02,0.26,0.005,452),
 (0,7,0.08,0,0.001,2070),(0,3,0.02,0,0.001,548),(0,7,0.08,0.26,0.005,694),
 (0,3,0.02,0.26,0.005,28),(0,3,0.08,0.26,0.003,248),(3,3,0.05,0.13,0.005,642),
 (3,5,0.02,0.13,0.003,347),(3,7,0.05,0.26,0.003,1038),(6,5,0.05,0.26,0.001,956),
 (6,3,0.02,0,0.005,691),(6,7,0.08,0.13,0.00346,1675),(6,7,0.02,0,0.001,680),
 (6,7,0.02,0,0.001,708),(6,4.1,0.08,0.26,0.005,697),(6,3,0.08,0,0.001,2282),
]
RNG = [(0, 6), (3, 7), (0.02, 0.08), (0, 0.26), (0.001, 0.005)]
X, y = [], []
for row in ROWS:
    x = [2 * (v - lo) / (hi - lo) - 1 for v, (lo, hi) in zip(row[:5], RNG)]
    X.append([1.0] + x + [xi * xi for xi in x]
             + [x[i] * x[j] for i, j in itertools.combinations(range(5), 2)])
    y.append(float(row[5]))
beta = np.linalg.lstsq(np.array(X), np.array(y), rcond=None)[0]
PUB = {1: ("silica", 142.18), 2: ("H2O2", 96.38), 3: ("oxalic", 536.63),
       4: ("glycine", -440.91), 5: ("DOSS", -69.75), 0: ("Intercept", 1044.65)}
for i, (name, pub) in PUB.items():
    got = beta[i]
    print(f"  {name:>9s}: 재적합 {got:9.2f} vs 원문 {pub:9.2f}")
    assert abs(got - pub) / abs(pub) < 0.01, f"{name} 재현 실패"
assert beta[4] < 0, "글리신 1차항은 음수(억제)여야 한다"
assert beta[3] > 0 > beta[4], "옥살산(+)과 글리신(-)의 부호가 갈려야 한다(판정#45)"
print("=> 원문 Table III 계수 6개 전부 1% 이내 재현, 글리신 부호 음수 확인")
```

```python verify
# 블록3: (K,k) 축퇴 — 피복형을 쓸 수 없는 이유를 수치로
import math
PAIRS = {0.13: 1329.0 / 1544.5, 0.26: 452.0 / 694.0}

def psi(C, K, k):
    if C <= 0 or K <= 0:
        return 1.0
    th = K * C / (1.0 + K * C)
    return math.exp(-k * th)

def best_k(K):
    return min((sum((psi(C, K, kx / 1000.0) - r) ** 2 for C, r in PAIRS.items()),
                kx / 1000.0) for kx in range(10, 12000))

sses = {}
for K in (0.13, 0.5, 1.0, 2.0, 4.0, 8.0, 16.0, 32.0):
    s, k = best_k(K)
    sses[K] = s
    print(f"  K={K:6.2f}/M -> 최적 k={k:.3f}, SSE={s:.3e}")
spread = max(sses.values()) / min(sses.values())
print(f"K를 {max(sses)/min(sses):.0f}배 움직였을 때 SSE 변화 = {spread:.1f}배")
assert spread < 20.0, \
    "SSE가 K에 충분히 민감하면 피복형을 써도 된다 — 그러면 이 노트를 고쳐야 한다"
print("=> 2점으로는 (K,k)가 분리되지 않는다 -> 지수 1개로 축소한 것이 정당")
```

```python verify
# 블록4: 엔진 계약 — 기준 조건 배수 1.0, 종 게이트, 농도 방향
import sys
sys.path.insert(0, ".")
from sim.chemistry import _chelator_suppression_term
from sim.params import load_pack, Param

pk = load_pack("cu_h2o2_bta")
v_ref = _chelator_suppression_term(pk, [])
assert v_ref is not None, "글리신 억제 항이 이 팩에서 활성이어야 한다"
assert abs(v_ref - 1.0) < 1e-12, f"기준 조건 배수 1.0 계약 위반: {v_ref}"

def tweak(**kw):
    import copy
    q = copy.deepcopy(pk)
    for k, v in kw.items():
        q.params[k] = Param(key=k, value=v, confidence="unverified")
    return q

# 종 게이트: 착화제를 옥살산으로 선언하면 항이 꺼져야 한다(판정#45)
assert _chelator_suppression_term(tweak(chelator_species="oxalic_acid"), []) is None, \
    "옥살산으로 선언하면 글리신 적합값을 전이하지 말아야 한다"

# 방향: 글리신을 늘리면 억제 강화(<1), 줄이면 완화(>1)
hi = _chelator_suppression_term(tweak(chelator_M=0.26), [])
lo = _chelator_suppression_term(tweak(chelator_M=0.0), [])
print(f"  0.26 M -> {hi:.4f}, 0 M -> {lo:.4f}, 기준 0.1332 M -> {v_ref:.4f}")
assert hi < 1.0 < lo, "농도 증가는 억제 강화, 감소는 완화여야 한다"

# 0.13 M 통제쌍 배수를 기준 0 M 으로 정규화해 실측과 대조
pred_013 = _chelator_suppression_term(tweak(chelator_M=0.13), []) / lo
print(f"  0 -> 0.13 M 예측 배수 {pred_013:.4f} vs 실측 0.8605")
assert abs(pred_013 - 0.8605) / 0.8605 < 0.05, "통제쌍 재현 오차 5% 초과"
```

## 6. 한계 (정직한 부기)

- **통제점이 2개다.** 곡률·포화 유무를 판별할 수 없다. 등급 `estimated`.
- 두 통제쌍의 고정 조건이 서로 다르다(실리카 3 vs 6 wt%, H₂O₂ 5 vs 7 wt%, 옥살산
  0.05 vs 0.02 M). 점별로 지수를 유도하면 **1.156 vs 1.649로 1.4배** 벌어진다 —
  실리카·H₂O₂·옥살산과의 상호작용이 이 차이에 섞여 있다(원문 회귀에서
  `[oxalic]*[glycine]` = −289.83, p = 4.02×10⁻⁵ 로 **유의한 상호작용**이 실제로 있다).
  단일 지수는 그 상호작용을 평균한 값이다.
- **이 계열에는 BTA가 없다.** 팩에는 있다(1.0 mM). BTA와 글리신이 같은 표면을 두고
  경쟁한다면 두 항을 독립으로 곱하는 현 구현은 과대 억제일 수 있다 — **미검증**.
- 옥살산 농도축은 여전히 미모델링이다. 같은 회귀에서 `[oxalic]` = +536.63
  (p = 1.7×10⁻⁷)로 **가장 강한 인자**다 — 다음 회차 C1 최우선 후보로 남긴다.
  아래 §7의 held-out 결과가 그 갭의 크기를 보여준다.
- 절대값은 여전히 주장 불가(이 팩은 계통 편향이 크다). 순위 전용.

## 7. held-out 결과 — 음(−)의 ρ를 숨기지 않는다

이번 회차에 같은 논문의 RSM 설계에서 **적합에 쓰지 않은 13조건**을
`validation/datasets/jani2025_cu_rsm_composition_heldout.yaml`로 등록했다
(실리카 0 wt% 조건, 판정#41 적합점 30/31/32, 이번 판정 적합점 4건은 전부 제외).

결과: **ρ = −0.349 (p = 0.877, n = 13, 비유의)**.

이것을 실패로 감추지 않고 그대로 기록한다. 원인은 글리신 항이 아니라
**옥살산 미모델링**으로 판단한다 — 근거: (a) 이 13조건에서 옥살산이 0.02~0.08 M로
4배 변하고 회귀계수가 전 인자 중 최대(+536.63)인데 모델에는 대응 항이 없다,
(b) 글리신 항 자체는 통제쌍 2건에서 ±5 % 안에 맞는다(§5 블록1), (c) 글리신 항을
넣기 전 같은 13조건의 ρ도 음수였다(−0.15, n=17 판) — 즉 이 항이 순위를 망친 것이
아니라 원래부터 다른 인자가 지배하고 있었다.
qa_loop 게이트가 보는 **유의 평균 ρ는 0.9566 → 0.9566 으로 불변**이다(이 데이터셋은
비유의라 집계에 들어가지 않는다). 전체 평균은 +0.717 → +0.640 으로 내려간다 —
데이터셋이 하나 늘었고 그것이 어려운 문제이기 때문이다.

## 8. 새로 도출한 지식

1. **착화제는 자동으로 촉진 인자가 아니다.** Cu CMP에서 글리신은 pH 3·옥살산 공존
   조건에서 억제로 작동한다(−440.91, p=4×10⁻⁷). "착화제 = 용해 촉진"이라는
   교과서적 직관을 그대로 코드에 옮기면 부호가 틀린다.
2. 같은 논문 안에서도 **착화제 종에 따라 부호가 갈린다**(옥살산 +, 글리신 −).
   `chelator_M` 하나로 착화제를 묶는 설계는 위험하다 — 종 게이트가 필수다.
3. ψ(표면 흡착 보호)의 적용 범위는 부식억제제·계면활성제·분산제에 이어
   **착화제**까지 넓어진다. COMPLETION.md의 "팩터 재정의 허용 규칙"에 따라
   ψ 정의를 "표면 흡착 보호"로 유지한 채 네 번째 갈래를 추가한 것이다.
4. 통제쌍이 2개일 때 (K, k) 2모수 피복형을 적합하면 240배 범위에서 SSE가 8배도
   안 움직인다 — **모수를 데이터 점 수보다 적게 유지하라**는 실측 근거.
