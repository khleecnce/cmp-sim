<!-- V2-SECTION: R2-slurry | 근거: oxidizer, passivation, chi, cu_alkaline_benzenesulfonic | 정본: ARCHITECTURE-V2.md §3 -->
# χ `cu_alkaline_benzenesulfonic` — `oxidizer_passivation_K` 승격 판정 (판정#74)

> 작성일: 2026-09-19 | 대상: `knowledge/params/cu_alkaline_benzenesulfonic.yaml::oxidizer_passivation_K`
> 선행: [[chi-oxidizer-cu-h2o2-reparameterization]](판정#20, K=0.8232 최초 적합·§7 한계 3항이
> 이 과제의 전제), [[cu-cmp-ph-mechanism]](cu_ph_alkaline_k 출처, R²=0.9971)
> 판정#73(cu_h2o2_bta held-out ρ 진단)의 다음 워커 회차.

## 0. 배경 — 무엇이 바뀌었는가

`cu_alkaline_benzenesulfonic` 팩은 2026-09-19 `cu_h2o2_bta`에서 분리된 알칼리 step-2 Cu
계(pH 9, 억제제 없음, 콜로이달 실리카, 벤젠술폰산)다. χ의 `oxidizer_passivation_K=0.8232`는
판정#20에서 `cu_h2o2_bta`에 처음 적합됐지만, 그 적합 출처(US20110165777A1 TABLE 2, pH 10.3 +
벤젠술폰산 1.0 wt% + 콜로이달 실리카)는 실제로는 산성·BTA·알루미나·글리신 계인
`cu_h2o2_bta`가 아니라 **이 새 팩의 조성과 정확히 일치**한다. 판정#20 §7 한계 3항은 같은
특허의 TABLE 1(KOH 0.59 wt%, pH 11.1)에서 모델·실측이 어긋나는 것을 "이 팩(당시
cu_h2o2_bta)에 pH 항이 산화제 항과 결합돼 있지 않아 미해결"로 남겼다. 이 새 팩은
`cu_ph_alkaline_k`/`cu_ph_alkaline_ref`라는 알칼리 pH 가지를 실제로 갖고 있으므로, 한계 3의
전제가 바뀌었는지를 이번 회차에서 검사한다.

## 1. 0단계 — 사실 재확인

### 1.1 YAML — 관련 키 (직접 읽음, `knowledge/params/cu_alkaline_benzenesulfonic.yaml`)

| 키 | 값 | confidence | 출처 |
|---|---|---|---|
| `oxidizer_passivation_K` | 0.8232 (1/wt%) | estimated | US20110165777A1 TABLE 2, 4점 최소자승 |
| `oxidizer_ref_wt_pct` | 1.0 wt% | literature | Kp 역산 조건과 동일 |
| `cu_ph_alkaline_k` | 0.3329 (1/pH) | literature | US9200180B2 TABLE 4 Ex.15-19, 5점 R²=0.9971 |
| `cu_ph_alkaline_ref` | 9.0 (pH) | literature | 팩 운전점(기준배수 위반 수정, 2026-09-19) |
| `cu_ph_acid_k` | 0.1428 (1/pH) | literature | 상속(산성역, 이 팩 운전 대역 밖) |

### 1.2 `sim/chemistry.py::_oxidizer_term` — passivation 분기 (L283-296, 직접 읽음)

```
if pack.has("oxidizer_passivation_K"):
    K = float(pack.get("oxidizer_passivation_K"))
    theta = float(SC.oxidizer_coverage_langmuir(C, K))
    theta_ref = float(SC.oxidizer_coverage_langmuir(C_ref, K))
    ...
    return floor + (1.0 - floor) * (1.0 - theta) / (1.0 - theta_ref)
```
산화제 항은 **C(농도)만의 함수**다. pH는 이 함수의 어떤 입력에도 나타나지 않는다.

### 1.3 `sim/factors.py::_f_chi` — pH 분기와 confidence 계산 (직접 읽음)

pH 항은 산화제 항과 **별개의 term**으로 계산돼 `terms` 딕셔너리에 각각 담기고
(`sim/factors.py` L1438-1444), 최종 χ 값은 `val = terms["oxidizer"] * terms["ph_cu_acidic"]`처럼
**단순 곱**이다(L1462-1466) — pH항과 산화제항 사이에 교차(coupling) 항은 어디에도 없다.

이 팩은 `cu_ph_acid_k`를 own 선언했으므로(1차 패스) pH 분기로 `_ph_cu_acidic_term`이
선택된다(L1384). 이 함수는 내부에서 pH·억제제 유무로 4레짐을 나누고, 이 팩의 조건
(알칼리·억제제 없음)에서는 `cu_ph_alkaline_k`/`cu_ph_alkaline_ref`를 읽어
`exp(-k·(pH-k_ref))`를 반환한다(`sim/factors.py` L1154-1163).

**confidence 계산 (L1487-1495, 직접 읽음)** — χ의 confidence를 결정하는 실제 코드:
```
if "oxidizer" not in terms:
    oxidizer_shape_keys = ()
elif pk.has("oxidizer_langmuir_K"):
    oxidizer_shape_keys = ("oxidizer_langmuir_K",)
elif pk.has("oxidizer_passivation_K"):
    oxidizer_shape_keys = ("oxidizer_passivation_K",)
else:
    oxidizer_shape_keys = ("oxidizer_curve_n", "oxidizer_peak_wt_pct")
f.confidence = _worst_conf(
    _pack_conf(pk, "oxidizer_wt_pct", "slurry_ph", "ce3_fraction"),
    _pack_conf(pk, *oxidizer_shape_keys, "ph_peak", "ceria_tooth_gain",
               "w_ph_acid_k", "sic_kmno4_ph_acid_k"))
```
**이 목록에 `cu_ph_acid_k`도 `cu_ph_alkaline_k`도 들어 있지 않다.** 즉 χ의 confidence는
pH 계수의 등급과 무관하게 오직 `oxidizer_passivation_K` 하나(이 팩에서 실제 켜진 유일한
산화제 형상 키)에 의해 결정된다 — `_pack_conf(pk, "oxidizer_passivation_K", "ph_peak", ...)`에서
나머지 키는 이 팩에 없어 스킵되고 `oxidizer_passivation_K`(estimated)만 남는다.
`_pack_conf(pk, "oxidizer_wt_pct", "slurry_ph", "ce3_fraction")` 쪽은 둘 다 literature라
상한이 아니다. `_worst_conf(literature, estimated) = estimated` — 이것이 §0의 C2 미충족
원인이다. **χ를 literature로 승격하려면 `oxidizer_passivation_K` 자체의 등급을 올리는 것이
유일한 길이고, pH 항의 등급은 이 계산에 전혀 관여하지 않는다** — §2에서 확인.

### 1.4 US20110165777A1 원문 재대조 (`papers/patents/US20110165777A1.html`, 직접 파싱)

TABLE 1(L2510-2775)과 TABLE 2(L2780-3020)를 HTML에서 태그를 벗겨 표 셀을 직접 재구성했다.

**TABLE 2** (KOH 0.41 wt%, 벤젠술폰산 1.0 wt%, 콜로이달 실리카 5 wt%, Zonyl FSN 500 ppm
고정, BTA 100 ppm, pH 10.3) — Cu RR (Å/min): Comp.Ex.10(H2O2=0)=187, Ex.11(0.25)=140,
Ex.12(0.5)=129, Ex.13(1.0)=121. ÷10 → 18.7/14.0/12.9/12.1 nm/min. **판정#20 노트의 전사값과
정확히 일치 — 전사 오류 없음.**

**TABLE 1** (KOH 0.59 wt%, 벤젠술폰산 1.0 wt%, 콜로이달 실리카 5 wt%, BTA 100 ppm, pH 11.1) —
Zonyl FSN 0 ppm 열(Comp.Ex.1/3/5/7)의 Cu RR (Å/min): H2O2=1.0→160, 3.0→158, 5.0→154,
7.0→157(원문 표기는 "Ex.8"이나 H2O2·FSN 값으로 보면 Comp.Ex.7이다 — 특허 원문 자체의
표기 중복, 우리 전사 오류가 아니다). ÷10 → 16.0/15.8/15.4/15.7 nm/min. **판정#20 노트의
전사값(t1_obs)과 정확히 일치 — 전사 오류 없음.** 원문 본문([0107]) 자신도 "removal rate
range stayed between 146 Å/min to 160 Å/min ... over the entire H2O2 concentration
tested"라고 명시해 이 평탄함이 저자 스스로도 주목한 사실임을 확인했다.

## 2. 1단계 — 한계 3 검사 (TABLE 1 재현, pH 보정)

### 2.1 구조적 이유로 pH 보정이 원천적으로 무력하다

§1.2-1.3에서 확인한 대로 χ = (산화제 항, C만의 함수) × (pH 항, pH만의 함수)이고 둘 사이에
교차항이 없다. TABLE 1의 모든 행은 **pH가 11.1로 고정**돼 있다(H2O2만 스윕). 따라서 같은
표 안에서 농도비 C/C=1을 취하면 pH 항은 분자·분모에서 정확히 상쇄된다:

```
χ(C, pH=11.1) / χ(1, pH=11.1)
  = [ox(C)·ph(11.1)] / [ox(1)·ph(11.1)]
  = ox(C) / ox(1)
```

즉 **`cu_ph_alkaline_k`를 어떤 값으로 두어도 TABLE 1 안에서의 상대 비율 예측은 한 비트도
바뀌지 않는다** — pH 보정이 "그래도 안 맞는다"가 아니라 이 아키텍처에서는 **적용 자체가
무의미(no-op)**하다. §7 verify 블록에서 이를 실제 코드로 확인한다(순수 산화제항 비율과
pH항까지 포함한 "보정" 비율이 부동소수 오차 이내로 동일함을 assert).

### 2.2 TABLE 1 자체의 통계적 판정력

FSN=0 부분집합 4점(H2O2 1/3/5/7 wt% → 16.0/15.8/15.4/15.7 nm/min)에 단순 선형회귀:
r=−0.671, slope=−0.065 nm/min/wt%, t=−1.281(df=2), **p=0.329(양측)** — 5% 수준에서
유의하지 않다. n=4로는 통계적 검정력이 낮다는 것 자체가 사실이나, 같은 표 8개 값
전체(146~182 Å/min, 평균 158.25, 이상치 Ex.8=182 제외 시 평균 154.9·표준편차≈4.5,
변동계수 ≈3%)의 산포가 조성 변화(H2O2 1→7 wt%, FSN 0→250 ppm)와 무관하게 이 정도로
작다 — 즉 노이즈 바닥이 **~3~4%대**로 좁다. 반면 모델(K=0.8232)이 예측하는 1→7 wt% 배수
변화는 산화제 항만으로 1.000→0.379(−62.1%, §7 계산)다. 노이즈 바닥의 15배 이상 큰
불일치이므로 "표본이 작아 판정력이 없다(null)"로 덮기에는 격차가 너무 크다.

### 2.3 결론 — (ii) 진짜 함수형 한계 (보정으로 해소되지 않음)

세 선택지 중 **(ii)**: pH 보정을 실제로 적용해도(§2.1) TABLE 1의 평탄함과 모델 예측의
간극은 조금도 줄지 않는다 — 그 이유가 (iii)처럼 "TABLE 1 데이터에 판정력이 없어서"가
아니라, **pH와 산화제가 독립 곱으로 모델링돼 있어 pH항이 원천적으로 C-의존적 형태를
바꿀 수 없기 때문**이다. 판정#20 §7 한계 3항이 예견한 "pH 커플링 미모델링"은 이번 회차로
**정확히 확인**됐다: 팩에 pH 가지가 생겼다는 사실 자체는 이 결합(coupling)을 만들지
않는다 — `cu_ph_alkaline_k`는 독립 가지일 뿐 산화제×pH 교차항이 아니다. 교차항을 만드는
것은 이번 과제 범위 밖(§4의 다음 회차 요건)이다. ⚠ 실제로 pH×산화제 교차항을 도입하면
TABLE 1의 평탄함을 설명할 수 있는지는 **미검증**이다 — 이번 회차는 "현재 구조로는
안 된다"만 확인했고, "어떤 구조를 쓰면 되는지"는 시도하지 않았다.

## 3. 2단계 — 승격 여부 판정

### 3.1 근거 서열 재평가 — 계 변경의 효과

`oxidizer_passivation_K`의 출처(US20110165777A1 TABLE 2)는 이 팩 분리 이전에는 **E4**
(다른 계 cu_h2o2_bta로의 전이 — 조성이 안 맞았다)였으나, 분리 후에는 **대상계 자기 통제
스윕**이 됐다 — 등급을 다시 매기면 **E2**(1차 문헌 폐형식 유도, 단 "저자 본인 검증"은
아니고 우리가 직접 재적합)에 해당한다. E4→E2는 실질적 상향이지만, EVIDENCE-RULES의
서열은 **충돌 판정**(두 근거가 맞설 때 어느 쪽을 채택할지)을 위한 것이고, `literature`
confidence 문턱은 별도로 **재현 정밀도·식별성**을 요구한다(§3.2) — 계가 맞아졌다고
자동으로 문턱을 넘지는 않는다.

### 3.2 잔차 11.9%의 코퍼스 내 비교 기준 (grep으로 직접 확인, 임의 문턱 금지)

동일 코퍼스에서 "최소자승 적합 + literature" 조합과 "최소자승 적합 + estimated 유지"
조합을 실제로 찾아 비교했다:

| 키 (팩) | 점수 | 잔차/R² | confidence | 근거 |
|---|---|---|---|---|
| `cu_ph_acid_k` (cu_h2o2_bta) | 12 | **최대 7.3%**, R²=0.954 | **literature** | `knowledge/cmp/cu-cmp-ph-mechanism.md` |
| `cu_ph_alkaline_k` (이 팩) | 5 | R²=0.9971 (오차 그 자체는 미보고, R² 기준 최대 수 % 대) | **literature** | 같은 노트, TABLE 4 Ex.15-19 |
| `chelator_suppression_a` (cu_h2o2_bta) | 2 통제쌍 | **−4.5%/+3.6%** | **estimated** (식별성 약화·조성 조건 상이로 하한) | [[psi-glycine-chelator-suppression-cu-jani2025]] |
| `oxidizer_acid_chelator_K` (cu_h2o2_bta, 판정#41/47) | 3~4 | **최대 3.8%** | **estimated** (proxy 종·식별 실패로 하한) | [[chi-cu-h2o2-regime-reversal-jani2025]] |
| `oxidizer_passivation_K` (이 팩, 이번 대상) | 4 | **최대 11.9%** | estimated (판정 대상) | 이 노트 |

이 코퍼스에서 `literature`를 받은 사례(7.3%, R²=0.954/0.9971)는 전부 **잔차 한 자릿수
%대**이고, 잔차가 그보다 작은 3.8~4.5%조차 (판정#41·#47, [[chi-cu-h2o2-regime-reversal-jani2025]])
**다른 이유로 estimated에 머문 사례가 이미 존재**한다. `oxidizer_passivation_K`의 11.9%는 이 코퍼스가
literature로 승격시킨 어떤 사례보다도 크고, 점수도 더 적다(n=4 vs 12) — **잔차 크기
기준만으로도 이 코퍼스의 기존 literature 문턱에 못 미친다.**

### 3.3 식별성 재실행 (§5 판정#20 원 검사를 이번 회차에서 직접 재실행)

```python verify
import sys, math
sys.path.insert(0, ".")
from sim.tier2_physics.slurry_components import oxidizer_coverage_langmuir as theta

mrr_obs = {0.0: 18.7, 0.25: 14.0, 0.5: 12.9, 1.0: 12.1}
obs_ratio = {C: v / mrr_obs[0.0] for C, v in mrr_obs.items()}

def f_hand(C, K, floor=0.15, Cref=3.0):
    t, tr = theta(C, K), theta(Cref, K)
    return floor + (1.0 - floor) * (1.0 - t) / (1.0 - tr)

def sse(K):
    f0 = f_hand(0.0, K)
    return sum((f_hand(C, K) / f0 - r) ** 2 for C, r in obs_ratio.items())

K0 = 0.8232
sse0 = sse(K0)
ratio_3x = sse(3 * K0) / sse0
ratio_low = sse(K0 / 3) / sse0
print(f"SSE(K0)={sse0:.5f}, 3배 교란 비={ratio_3x:.2f}, 1/3배 교란 비={ratio_low:.2f}")

# 판정#20의 5배 기준(EVIDENCE-RULES #20)과 대조 — 판정#47이 같은 기준으로 "3.04배<5배=식별
# 실패"를 판정한 바 있다. 여기서는 두 방향 다 5배를 넘어야 식별 확인.
assert ratio_3x > 5.0, f"3배 교란 시 SSE 악화가 5배 미달({ratio_3x:.2f}) — 식별 실패"
assert ratio_low > 5.0, f"1/3배 교란 시 SSE 악화가 5배 미달({ratio_low:.2f}) — 식별 실패"
print("=> K는 이 4점에 대해 식별 가능(5배 기준 통과) — 판정#20 원 결론과 일치, 새로 바뀐 것 없음")
```

식별성은 여전히 확인되지만(3배·1/3배 교란 모두 5배 기준을 넘음, 판정#20·#47과 동일 기준),
이것은 **한계 1(잔차 11.9%)이나 한계 2(φ 외부값)를 해소하지 못한다** — 식별 가능함과
값이 정밀함은 다른 문제다. K가 "이 4점에서 유일하게 최적인 값"이라는 것과 "이 값이
literature 수준으로 정밀하다"는 것은 별개 주장이다.

### 3.4 φ 축퇴(한계 2) — 변경 없음

판정#20 §5가 이미 확인한 대로 φ(=`oxidizer_mech_floor`)를 K와 동시에 자유롭게 풀면
SSE 최소값이 φ=0.05~0.50에서 2배 이내로 거의 평평하다(약한 축퇴) — 이 팩이 φ에 대한
자기 관측을 갖고 있지 않다는 사실은 이번 회차에서 바뀌지 않았다(팩 YAML에
`oxidizer_mech_floor` 키가 없다, §1.1 표에 없음 = 4계 수렴 외부값 0.15를 그대로 상속).
**한계 2는 그대로 남는다.**

### 3.5 종합 판정 — **estimated 유지**

세 한계 중:
- 한계 1(잔차 11.9%) — §3.2 코퍼스 비교로 **미달 확정**(literature 사례보다 크고 표본은 적음).
- 한계 2(φ 외부값 축퇴) — **미해소**(이번 회차에 새 관측 없음).
- 한계 3(pH 커플링) — **재검사했고 미해소로 재확인**(§2, pH 보정이 구조적으로 no-op).

계가 E4→E2로 재분류된 것(§3.1)은 실질적 개선이지만, `literature` confidence는 계 근접도
만으로 주는 등급이 아니라 **재현 정밀도**를 함께 요구한다(§3.2 비교표가 이 코퍼스의
실제 기준이다). 세 한계 중 하나도 해소되지 않았으므로 **승격하지 않는다.**

⚠ 격자를 채우려는 유인이 있었지만(C2 4칸 중 하나), 근거 없이 등급을 올리는 것은 오염이다
— 유지가 정직한 결론이다.

## 4. 다음 회차 요건 (승격을 재시도하려면)

승격이 가능해지려면 다음 중 하나가 필요하다:
1. **한계 1 해소**: 같은 조성(알칼리·벤젠술폰산·콜로이달실리카·억제제 없음)의 **독립적인
   추가 H2O2 스윕**(TABLE 2와 다른 pH 또는 다른 실험 배치) 5점 이상, 재적합 시 잔차가
   7% 대(§3.2의 literature 실사례 수준) 이내로 줄어야 한다.
2. **한계 2 해소**: 이 팩 고유의 φ(=`oxidizer_mech_floor`) 관측 — 산화제 0 wt%에 가까운
   조건에서 순수 기계적 제거율만 측정한 통제 데이터.
3. **한계 3 해소 경로 변경**: pH×산화제 **교차항**을 새로 도입하는 모델 재구조화(이번
   과제 범위 밖, 사용자 승인 필요) — 그 전에는 TABLE 1이 채점 대상이 되어서는 안 된다
   (§2.3에 따라 이 데이터셋은 `in_scope: false` 또는 교차확인 전용으로 유지해야 한다).

## 5. 코드 재현 (verify)

```python verify
# TABLE 1/TABLE 2 전사값이 US20110165777A1 원문(로컬 papers/patents/US20110165777A1.html)과
# 일치하는지, 그리고 pH 보정이 구조적으로 no-op임을 실제 코드로 확인한다.
import sys, math
sys.path.insert(0, ".")
from sim.chemistry import _oxidizer_term
import math as _m

class FakePack:
    def __init__(self, **kw):
        self.d = kw
        self.name = "fake"
    def has(self, k): return k in self.d
    def get(self, k): return self.d[k]
    def get_or(self, k, dv): return self.d.get(k, dv)

def ox_ratio(C, K=0.8232, Cref=1.0):
    notes = []
    f0 = _oxidizer_term(FakePack(oxidizer_wt_pct=Cref, oxidizer_ref_wt_pct=Cref,
                                  oxidizer_passivation_K=K), notes)
    fC = _oxidizer_term(FakePack(oxidizer_wt_pct=C, oxidizer_ref_wt_pct=Cref,
                                  oxidizer_passivation_K=K), notes)
    return fC / f0

def ph_alkaline(ph, k=0.3329, ref=9.0):
    return math.exp(-k * (ph - ref))

t1_C = [1.0, 3.0, 5.0, 7.0]
t1_obs = {1.0: 16.0, 3.0: 15.8, 5.0: 15.4, 7.0: 15.7}  # 원문 재대조 완료(§1.4)
obs_ratio = {C: t1_obs[C] / t1_obs[1.0] for C in t1_C}

# pH를 TABLE1의 실제 pH(11.1, 전 행 고정)로 "보정"해도 결과가 순수 산화제항 비율과
# 소수점 단위로 동일해야 한다 — no-op 주장의 직접 검증.
ph_const = ph_alkaline(11.1)
for C in t1_C:
    pure = ox_ratio(C)
    corrected = (ox_ratio(C) * ph_const) / (ox_ratio(1.0) * ph_const)
    assert abs(pure - corrected) < 1e-12, f"C={C}: pH 보정이 결과를 바꿈 — no-op 주장 반증됨"
print("확인: pH(11.1) 보정을 곱해도 TABLE1 내부 비율은 1e-12 이내로 완전히 동일 (no-op 확정)")

model_ratio_7 = ox_ratio(7.0)
print(f"모델(산화제항만, K=0.8232): C=7 wt% 비율={model_ratio_7:.4f} "
      f"(1→7 wt% 감소 {100*(1-model_ratio_7):.1f}%)")
print(f"실측(TABLE1, FSN=0): C=7 wt% 비율={obs_ratio[7.0]:.4f} "
      f"(1→7 wt% 변화 {100*(1-obs_ratio[7.0]):.1f}%)")
assert model_ratio_7 < 0.5, "모델이 큰 감소를 예측해야 불일치 주장이 성립"
assert 0.9 < obs_ratio[7.0] < 1.1, "실측은 거의 평평해야 불일치 주장이 성립"

# TABLE1 FSN=0 4점 회귀 유의성 (§2.2)
xs = t1_C
ys = [t1_obs[C] for C in t1_C]
n = len(xs)
mx, my = sum(xs) / n, sum(ys) / n
sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
sxx = sum((x - mx) ** 2 for x in xs)
syy = sum((y - my) ** 2 for y in ys)
r = sxy / math.sqrt(sxx * syy)
df = n - 2
t_stat = r * math.sqrt(df / (1 - r ** 2))
print(f"TABLE1 FSN=0 회귀: r={r:.4f}, t={t_stat:.3f}, df={df} (|t|<4.303 → p>0.05, 5점 미달로 비유의)")
assert abs(t_stat) < 4.303, "df=2에서 5% 유의수준 임계값(4.303)을 넘으면 유의미한 추세로 재판정 필요"
print("=> n=4로는 5% 수준에서 유의한 추세를 확인할 수 없다 (통계적으로 비유의)")

# 식별성 재실행 (§3.3, 판정#20/#47과 같은 5배 기준)
from sim.tier2_physics.slurry_components import oxidizer_coverage_langmuir as theta_fn

mrr_obs2 = {0.0: 18.7, 0.25: 14.0, 0.5: 12.9, 1.0: 12.1}
obs_ratio2 = {C: v / mrr_obs2[0.0] for C, v in mrr_obs2.items()}

def f_hand(C, K, floor=0.15, Cref=3.0):
    t, tr = theta_fn(C, K), theta_fn(Cref, K)
    return floor + (1.0 - floor) * (1.0 - t) / (1.0 - tr)

def sse(K):
    f0 = f_hand(0.0, K)
    return sum((f_hand(C, K) / f0 - r) ** 2 for C, r in obs_ratio2.items())

K0 = 0.8232
sse0 = sse(K0)
r3 = sse(3 * K0) / sse0
r13 = sse(K0 / 3) / sse0
print(f"식별성: SSE(3K)/SSE(K)={r3:.2f}, SSE(K/3)/SSE(K)={r13:.2f} (5배 기준, 판정#20/#47)")
assert r3 > 5.0 and r13 > 5.0, "식별성 기준(5배) 미달 — 판정#20 원 결론과 어긋남"
print("=> 식별성은 여전히 확인됨(변경 없음) — 그러나 이는 잔차 크기(한계1)·φ 축퇴(한계2)를 해소하지 않는다")
```
