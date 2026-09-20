<!-- V2-SECTION: R2-slurry | 근거: oxidizer, chi, 화학, passivation, Langmuir | 정본: ARCHITECTURE-V2.md §3 -->
# χ `cu_h2o2_bta` `oxidizer_passivation_K` — US9200180B2 독립 재적합 시도 (승격 기각)

> 작성일: 2026-09-15 | 대상: `knowledge/params/cu_h2o2_bta.yaml::oxidizer_passivation_K`
> 선행: [[chi-oxidizer-cu-h2o2-reparameterization]](판정#20, K=0.8232를 US20110165777A1
> TABLE 2 4점에 최소자승 적합, US9200180B2는 §6.1에서 **방향(랭킹)만** 교차확인하고
> 피팅에는 쓰지 않음)
> 과제 출처: `validation/C2-RESIDUAL-CLASSIFICATION.md` χ/cu_h2o2_bta 행 —
> "US9200180B2 Ex.5/6/7에 동일 함수형으로 독립 K를 재적합해 판정#20의 K=0.8232와
> 정합하는지 확인, 정합하면 estimated→literature 승격."

## 1. 질문

판정#20(2026-09-14, EVIDENCE-RULES.md)은 `oxidizer_passivation_K=0.8232`를
US20110165777A1(2011 공개, https://patents.google.com/patent/US20110165777A1/en,
4점, calibration)에만 적합했고, US9200180B2(Air Products, 2015,
https://patents.google.com/patent/US9200180B2, Ex.5/6/7)는 **다른 조성**(BTA 없음,
벤젠술폰산 2wt%, 알칼리)이라 방향(랭킹) 일치만 확인하고 크기는 검증하지 않았다(§6.1).
이 노트는 US9200180B2의 3점을 **그 자체로 독립 재적합**해서 나오는 K가 0.8232와
정합하는지를 검사한다. 신규 문헌 탐색은 불요 — 두 데이터셋 모두 이미 저장소에 있다.

## 2. 데이터 (신규 탐색 없음, 기확보 파일 그대로 인용)

`validation/datasets/us9200180b2_cu_h2o2_series.yaml`에 이미 저장된 값을 그대로 쓴다
(출처: US9200180B2, Air Products and Chemicals/현 Versum·Merck, TABLE 1-b Examples 5/6/7,
"CMP composition having benzenesulfonic acid and per-compound oxidizing agents", 2015,
https://patents.google.com/patent/US9200180B2 — 콜로이달 실리카 3wt%, 벤젠술폰산 2wt%,
2.0 psi 고정, H2O2만 스윕):

| Example | H2O2 (wt%) | Cu RR (nm/min) |
|---|---|---|
| 5 | 1.0 | 11.8 |
| 6 | 2.5 | 9.2 |
| 7 | 5.0 | 7.7 |

C=0 앵커가 없다(1 wt%가 최저 관측점) — 비율은 C=1.0 기준으로 정규화한다(판정#20 §6.1의
교차확인 코드(block3)와 동일 관례).

## 3. 방법 — 동일 함수형, K만 독립 자유도

`sim/chemistry.py::_oxidizer_term`의 `oxidizer_passivation_K` 분기를 그대로 쓴다:
`f(C) = φ + (1-φ)·(1-θ(C))/(1-θ(C_ref))`, `θ(C)=K·C/(1+K·C)`.
φ(`oxidizer_mech_floor`)는 판정#20과 동일하게 **고정**(0.15, 팩 미선언 기본값 — 이
데이터셋 자체가 3점뿐이라 φ까지 자유도로 풀면 식별이 더 나빠진다, 판정#20 §5가 이미
4점에서도 이 축퇴를 지적함). C_ref는 두 값으로 각각 시도한다: (a) 팩의 실제
`oxidizer_ref_wt_pct=3.0`(모델이 실제로 쓰는 기준점), (b) 이 데이터셋 자체의 최저관측점
C=1.0(교차확인 코드가 쓴 정규화 기준). 자유 파라미터는 K 하나.

## 4. 결과 — 독립 K는 K_stored=0.8232와 정합하지 않는다

§7 블록1·2가 이 표 전체를 코드로 재현·assert한다.

**C_ref=3.0(팩 기준점) 사용:**

| 지표 | 값 |
|---|---|
| 최소자승 최적 K | **0.2184** |
| SSE(K*) | 0.001565 |
| K*/K_stored | **0.265** (약 3.8배 작다) |
| 재현 오차 (C=2.5) | +4.21% |
| 재현 오차 (C=5.0) | −3.39% |

**C_ref=1.0(데이터셋 자체 기준) 사용:** 최적 K=0.2372, SSE=0.001391, K*/K_stored=0.288 —
C_ref 선택에 거의 무관하게 **독립 K는 0.21~0.24 대역**에 수렴한다.

식별성(SSE(K)가 뾰족한 단일 최소인가, 판정#19 축퇴와 대비): K를 0.3배로 낮추면
SSE가 34배(0.0516/0.00157), 3배로 올리면 37배(0.0584/0.00157) 나빠진다 — **3점뿐이지만
K는 뚜렷이 식별된다**(축퇴 아님).

**K_stored=0.8232를 이 데이터셋에 그대로 적용(교차확인, C_ref=3.0)하면:**

| C | 실측 비율 | 모델 비율(K=0.8232) | 오차 |
|---|---|---|---|
| 1.0 | 1.000 | 1.000 | 0% |
| 2.5 | 0.780 | 0.631 | **−19.1%** |
| 5.0 | 0.653 | 0.411 | **−37.0%** |

판정#20 §6.1이 이미 "방향(단조감소) 일치, 크기는 모델이 더 가파르다"고 정직하게
기록했던 바로 그 어긋남이다 — 이번 독립 재적합은 그 어긋남의 **크기**를 정량화한다:
K_stored를 그대로 쓰면 오차가 최대 37%인데, K를 이 데이터셋에 맞춰 독립적으로 다시
추정하면 오차가 4% 이내로 줄고 그 최적 K가 K_stored의 1/4~1/3.5에 불과하다.

## 5. 판정 — 승격 기각

**정합 기준**: 두 독립 데이터셋에서 같은 함수형으로 각각 적합한 K가 서로의 불확실성
범위 안에 들어야 "독립 검증"이라 부를 수 있다. 여기서는 K*(US9200180B2 단독)=0.22가
K_stored(US20110165777A1 단독)=0.82의 **3.5~3.8배**만큼 벗어난다 — 우연한 적합 잡음
(4점·3점 각각의 측정 산포)으로 설명하기에는 너무 크다. **정합하지 않는다.**

원인은 판정#20 §6.1과 §7이 이미 정직하게 기록해 둔 조성 차이다: US9200180B2 Ex.5/6/7은
**BTA(부동태 억제제) 없음**, 벤젠술폰산 2wt%, 알칼리(pH 8.5~9.5, 데이터셋 노트) 조성이고,
K_stored의 근거인 US20110165777A1 TABLE 2는 **BTA 100ppm 존재**, 산성에 가까운 pH 10.3
조성이다. BTA 유무 자체가 `oxidizer_passivation_K`가 표현하는 부동태 메커니즘과 상호작용할
개연성이 높은데(부동태 억제제가 있으면 같은 H2O2 농도에서도 부동태 진행이 달라짐), 두 팩
모두 이 상호작용을 모델링하지 않는다. 즉 **두 데이터셋은 화학적으로 같은 K를 공유할
이유가 애초에 약하다** — 정합 실패가 우연이 아니라 구조적으로 설명 가능하다.

**결론: `oxidizer_passivation_K`의 confidence를 literature로 승격하지 않는다.**
값(0.8232)·confidence(estimated) 둘 다 **변경 없음**. YAML·코드 변경 없음.
이것은 "재현 못 하면 승격하지 않는다"는 과제 지시의 정직한 이행이다 — 물리적 근거
없이 지수·보정항을 추가해 두 데이터셋을 동시에 맞추려 시도하지 않았다(그런 자유도를
추가할 1차 근거가 없다, BTA 커플링 항은 이 코드베이스의 어느 문헌도 정량으로 주지 않는다).

## 6. 한계

1. C=0 앵커가 US9200180B2에 없어 절대 배수가 아니라 C=1.0 기준 비율로만 비교했다 —
   판정#20 §6.1 교차확인과 같은 관례이지 이번에 새로 도입한 편의가 아니다.
2. 3점·1자유도라 식별은 되지만(§4) 신뢰구간은 넓다 — K*=0.22가 "정확한 값"이라는
   주장은 아니다. 이 노트의 결론은 "K*=0.22"를 채택하자는 것이 아니라(그러면 다른
   조성 데이터로 팩 값을 바꾸는 것이 되어 §5가 지적한 조성 불일치를 무시하게 된다),
   **K_stored와 독립 K가 정합하지 않는다는 사실** 하나뿐이다.
3. BTA 유무·pH 차이가 실제로 K를 이동시키는 정량 메커니즘(예: BTA 흡착이 H2O2 부동태
   흡착 사이트와 경쟁하는 Langmuir 공동흡착식)은 이 코드베이스의 어느 문헌도 주지 않는다
   — §5의 설명은 정성적 개연성이지 검증된 메커니즘이 아니다.

## 7. 코드 재현 (verify)

```python verify
# 블록1: US9200180B2 3점 독립 최소자승 재적합 — 코드 경로(chemistry_factor) 직접 호출
import sys
sys.path.insert(0, ".")
from sim.chemistry import chemistry_factor
from sim.tier2_physics.slurry_components import oxidizer_coverage_langmuir as theta

class FakePack:
    def __init__(self, **kw):
        self.d = kw
        self.name = "fake"
    def has(self, k): return k in self.d
    def get(self, k): return self.d[k]
    def get_or(self, k, dv): return self.d.get(k, dv)

def f_code(C, K, C_ref):
    return chemistry_factor(FakePack(
        abrasive="alumina",
        oxidizer_wt_pct=C, oxidizer_ref_wt_pct=C_ref,
        oxidizer_passivation_K=K,
    )).factor

def f_hand(C, K, floor=0.15, C_ref=3.0):
    t, tr = theta(C, K), theta(C_ref, K)
    return floor + (1.0 - floor) * (1.0 - t) / (1.0 - tr)

# 코드 경로와 손 유도 교차검증
for C, K, Cref in ((1.0, 0.8232, 3.0), (2.5, 0.5, 1.0), (5.0, 1.2, 3.0)):
    a, b = f_code(C, K, Cref), f_hand(C, K, C_ref=Cref)
    assert abs(a - b) < 1e-9, f"코드/손유도 불일치: {a} vs {b}"
print("코드 경로(chemistry_factor)와 폐형식 손 유도 1e-9 이내 일치 확인")

# 데이터 (원문 실시예표 그대로 전사, 판정#20 §6.1과 동일 값)
obs = {1.0: 11.8, 2.5: 9.2, 5.0: 7.7}
obs_ratio = {C: v / obs[1.0] for C, v in obs.items()}
expected_ratio = {1.0: 1.0, 2.5: 0.7796610169491525, 5.0: 0.6525423728813559}
for C, r in obs_ratio.items():
    assert abs(r - expected_ratio[C]) < 1e-9

def sse(K, C_ref):
    f1 = f_hand(1.0, K, C_ref=C_ref)
    return sum((f_hand(C, K, C_ref=C_ref) / f1 - r) ** 2 for C, r in obs_ratio.items())

def grid_min(C_ref, lo=0.001, hi=10.0, step=0.0002):
    bK, bS = None, 1e9
    K = lo
    while K <= hi:
        s = sse(K, C_ref)
        if s < bS:
            bS, bK = s, K
        K += step
    return bK, bS

K_star_3, S_star_3 = grid_min(3.0)
K_star_1, S_star_1 = grid_min(1.0)
print(f"C_ref=3.0(팩 기준): K*={K_star_3:.4f}, SSE={S_star_3:.6f}")
print(f"C_ref=1.0(데이터 기준): K*={K_star_1:.4f}, SSE={S_star_1:.6f}")

K_STORED = 0.8232
assert abs(K_star_3 - 0.2184) < 0.002
assert abs(K_star_1 - 0.2372) < 0.002
ratio_3 = K_star_3 / K_STORED
ratio_1 = K_star_1 / K_STORED
print(f"K*/K_stored: C_ref=3.0 -> {ratio_3:.3f}, C_ref=1.0 -> {ratio_1:.3f}")
assert ratio_3 < 0.35 and ratio_1 < 0.35, "독립 K가 K_stored의 35% 미만이어야 '정합 실패'가 성립"

# 독립 재적합의 재현 오차 (C_ref=3.0 기준) — 표(§4)의 +4.21%/-3.39%를 그대로 재현
print("독립 재적합(K*=0.2184) 재현 오차:")
expected_err_pct = {1.0: 0.0, 2.5: 4.21, 5.0: -3.39}
for C, r in obs_ratio.items():
    f1 = f_hand(1.0, K_star_3, C_ref=3.0)
    pred = f_hand(C, K_star_3, C_ref=3.0) / f1
    err = 100 * (pred - r) / r if r else 0.0
    print(f"  C={C}: obs={r:.4f} pred={pred:.4f} err%={err:+.2f}")
    assert abs(err) < 6.0, f"독립 재적합 오차 {err:.1f}%가 6%를 넘음"
    assert abs(err - expected_err_pct[C]) < 0.01, (
        f"C={C} 재현오차 {err:.2f}%가 노트 §4 표값 {expected_err_pct[C]:+.2f}%와 어긋남")
print("=> 독립 재적합은 자기 데이터를 6% 이내로 재현한다(식별 가능, 축퇴 아님) "
      "— §4 표의 +4.21%/-3.39%와 1e-2 이내 일치")
```

```python verify
# 블록2: 식별성(SSE 단일최소) + K_stored를 이 데이터셋에 강제 적용했을 때의 오차
import sys
sys.path.insert(0, ".")
from sim.tier2_physics.slurry_components import oxidizer_coverage_langmuir as theta

def f_hand(C, K, floor=0.15, C_ref=3.0):
    t, tr = theta(C, K), theta(C_ref, K)
    return floor + (1.0 - floor) * (1.0 - t) / (1.0 - tr)

obs = {1.0: 11.8, 2.5: 9.2, 5.0: 7.7}
obs_ratio = {C: v / obs[1.0] for C, v in obs.items()}

def sse(K, C_ref=3.0):
    f1 = f_hand(1.0, K, C_ref=C_ref)
    return sum((f_hand(C, K, C_ref=C_ref) / f1 - r) ** 2 for C, r in obs_ratio.items())

K_star = 0.2184
s_star = sse(K_star)
# 식별성 — 최적값에서 벗어나면 잔차가 뚜렷이 나빠지는가
for mult in (0.3, 3.0):
    s_far = sse(K_star * mult)
    assert s_far > 10 * s_star, f"K*x{mult}에서 SSE가 10배 이상 나빠져야 식별성 성립 (got {s_far/s_star:.1f}x)"
    print(f"SSE(K*x{mult})/SSE(K*) = {s_far/s_star:.1f}x")
print("=> 3점뿐이지만 K는 뚜렷이 식별된다(축퇴 아님)")

# K_stored를 그대로 적용했을 때의 오차 — 판정#20 §6.1이 정성적으로만 남긴 것을 정량화
K_STORED = 0.8232
print("\nK_stored=0.8232를 그대로 적용한 재현 오차 (C_ref=3.0):")
errs = {}
for C, r in obs_ratio.items():
    f1 = f_hand(1.0, K_STORED, C_ref=3.0)
    pred = f_hand(C, K_STORED, C_ref=3.0) / f1
    err = 100 * (pred - r) / r if r else 0.0
    errs[C] = err
    print(f"  C={C}: obs={r:.4f} pred={pred:.4f} err%={err:+.2f}")
assert errs[2.5] < -15.0 and errs[5.0] < -30.0, "K_stored 적용 오차가 기록된 크기(-19%/-37% 근방)여야 함"
assert abs(errs[2.5]) > 3 * abs(0.0421 * 100 / 4.21), "K_stored 오차가 독립재적합 오차보다 뚜렷이 커야 '정합 실패' 결론이 성립"
print("=> K_stored 적용 오차(최대 -37%)가 독립 재적합 오차(최대 4.2%)보다 뚜렷이 크다 — 정합 실패 확정")
```
