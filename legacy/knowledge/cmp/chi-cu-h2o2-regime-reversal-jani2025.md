<!-- V2-SECTION: R2-slurry | 근거: oxidizer, chi, 화학, passivation, chelator, regime | 정본: ARCHITECTURE-V2.md §3 -->
# χ `cu_h2o2_bta` 산화제 항 — 착화제·pH 레짐에서 **부호가 뒤집힌다** (판정#29 2회차)

> 작성일: 2026-09-15 | 대상: `knowledge/params/cu_h2o2_bta.yaml::oxidizer_passivation_K`,
> `sim/chemistry.py::_oxidizer_term`
> 선행: [[chi-oxidizer-cu-h2o2-reparameterization]](판정#20, K=0.8232 도입),
> [[chi-cu-h2o2-independent-refit-us9200180b2]](판정#29 1회차, 독립 재적합 K*=0.218 → 승격 기각)
> 과제: C2 잔여 1칸(χ/cu_h2o2_bta) — "새 1차 출처로 값을 대조해 confidence 승격".

## 1. 질문

판정#29 1회차는 **같은 방향(단조 감소)** 의 두 데이터셋에서 나온 K가 3.8배 어긋난다는
것까지만 밝히고 승격을 기각했다. 남은 질문은 "그 3.8배가 조성 차이 때문인가, 아니면
함수형 자체가 이 팩의 **운전점**에서 틀렸는가"였다. 이번 회차는 세 번째 독립 데이터셋을
확보해 그 질문에 답한다.

## 2. 새 1차 출처 (이번 회차 신규 확보)

Charmy Jani, Ravitej Venkataswamy, Jihoon Seo, Sitaraman Krishnan,
"Revisiting the Roles of Chelator, Inhibitor, Oxidant, and Abrasive in High-Rate Copper CMP",
*ECS Journal of Solid State Science and Technology* **14**(4), 044003, 2025.
doi:10.1149/2162-8777/adc59e — **CC-BY 오픈액세스**(Crossref license 확인),
전문 HTML 로컬 보관: `papers/jani2025-revisiting-roles-cu-cmp.html`, INDEX 등록.

공정(원문 Experimental, 전 실험 고정): CETR-CP-4 벤치탑 폴리셔, IK4250H 패드(DuPont),
**3.0 psi**, **platen 90 rpm**, 슬러리 **150 mL/min**, 매 실험 전 1분 다이아몬드 컨디셔닝,
2인치 Cu 디스크, 질량감량법(밀도 8.96 g/cm³, 면적 20.27 cm²), **슬러리 pH 3.0 고정**,
실리카 Z-평균 입경 33 nm.

Table I(조성) × Table II(Cu RR)에서 **오직 H₂O₂만 바뀌고 나머지가 전부 같은** 3조를
그대로 옮겼다(실리카 6 wt%, 옥살산 0.08 M, 글리신 0 M, DOSS 0.001 M 고정):

| Expt # | H₂O₂ (wt%) | Cu RR (nm/min) | 기준(3 wt%) 대비 배수 |
|---|---|---|---|
| 30 | 3 | 2282 | 1.000 |
| 31 | 4 | 2533 | 1.110 |
| 32 | 6 | 2578 | 1.130 |

읽은 방법: `read_method: table` — 인쇄된 표의 숫자다(그래프 판독 아님).

## 3. 결과 — 방향이 반대다 (정량 편차가 아니라 부호 반증)

지금까지의 Cu 산화제 관측 3계열을 한 축에 놓으면:

| 출처 | pH | 착화제 | 억제제 | H₂O₂ 스윕 | 방향 | 등급 |
|---|---|---|---|---|---|---|
| US20110165777A1 TABLE 2 (판정#20 적합용, https://patents.google.com/patent/US20110165777A1/en) | 10.3 | 없음 | BTA 100 ppm | 0→1 wt% | **감소** (18.7→12.1) | E2 |
| US9200180B2 TABLE 1-b Ex.5/6/7 (판정#29 1회차, https://patents.google.com/patent/US9200180B2) | 알칼리 | 벤젠술폰산 | 없음 | 1→5 wt% | **감소** (11.8→7.7) | E2 |
| **Jani 2025 Expt 30/31/32 (이번 회차)** | **3.0** | **옥살산 0.08 M** | 없음 | 3→6 wt% | **증가** (2282→2578) | **E2** |

현행 코드(`oxidizer_passivation_K=0.8232`, 피복-억제 분기)는 3→6 wt% 구간에서 배수
**0.647**(−35.3 %)을 예측하는데 실측은 **1.130**(+13.0 %)이다. 정량 편차가 아니라
**부호가 반대**다(§6 블록1이 assert 로 고정).

세 계열은 서로 모순되지 않는다 — **레짐이 다르다.** 알칼리·무착화제에서는 CuO 부동태막이
두꺼워져 억제(감소), 산성·착화제 존재에서는 산화된 Cu(II)가 옥살산/글리신 착물로 즉시
용해되어 산화가 율속이 된다(증가, 고농도에서 포화). 이 해석은 Jani 2025 회귀표의
`[H2O2](3,7)` 계수 **+96.38 (p=0.0185, 유의)** 와 `[H2O2]*[H2O2]` **−115.88 (p=0.222,
비유의)** 가 직접 지지한다 — 조사 구간에서 1차항은 양(+)이고 곡률은 통계적으로 확인되지
않는다(§6 블록2).

## 4. 이 팩에 대한 판정 — 승격이 아니라 **레짐 불일치(BIAS)** 다

`cu_h2o2_bta` 의 운전점은 `slurry_ph=4.0`, 기준 조성이 **글리신 1 wt% + BTA 1 mM +
H₂O₂ 3 wt%** 다(`abrasive_wt_pct` note, 출처 US20080090500A1 TABLE 4, https://patents.google.com/patent/US20080090500A1/en). 즉 **산성 ×
착화제 존재** — 위 표의 셋째 행과 같은 레짐이고, K=0.8232 를 적합한 첫째 행(알칼리 ×
무착화제)과는 **다른 레짐**이다.

따라서 판정#29 1회차의 "3.8배 불일치"는 적합 잡음도 조성 미세차도 아니라, **형상
파라미터를 자기 운전점이 아닌 레짐에서 역산한 결과**다. 새 데이터로 값을 대조해 등급을
올릴 수 있는 종류의 갭이 아니다.

**조치: 값·등급·코드 전부 변경 없음.** `oxidizer_passivation_K=0.8232`, confidence
`estimated` 그대로다. 이유:
- 승격은 불가 — 세 번째 1차 출처가 값을 확증하기는커녕 **부호를 반증**했다.
- 값 교체도 불가 — Jani 계열로 촉진형 K 를 다시 적합하면 이 팩의 **다른** 데이터셋
  (알칼리 계열)에서 부호가 틀려진다. 두 지수를 평균내는 것은 EVIDENCE-RULES 가 금지한다.
- 올바른 해소는 **팩 분리**(산성×착화제 가지 / 알칼리×무착화제 가지)이며, 그것은
  confidence 승격 과제(C2)가 아니라 BIAS 과제다. §7에 구현 요청으로 남긴다.

배수 1.0 계약은 이 판정과 무관하게 유지된다 — 기준 농도 `oxidizer_ref_wt_pct=3.0` 에서
피복-억제 분기는 항등적으로 1.0 이므로, **기준 조건의 예측값은 이 노트로 전혀 바뀌지 않는다.**
바뀌는 것은 "H₂O₂ 를 스윕할 때 이 팩의 예측을 믿을 수 있는 구간"의 선언뿐이다.

## 5. 한계 (정직한 부기)

- n=3, 단일 실험실·단일 장비다. 곡률(포화/정점) 유무는 이 3점으로 판별 불가 —
  Jani 회귀의 2차항이 비유의한 것도 "곡률이 없다"가 아니라 "구간 내에서 확인 안 됨"이다.
- 이 계열에는 **BTA 가 없다**. 팩에는 있다. BTA 는 ψ(억제제) 항이 따로 담지만,
  BTA 가 산화제 항의 *형상*까지 바꾸지 않는다는 보장은 이 데이터에 없다 — **미검증**.
- 착화제가 옥살산이고 팩 기준 조성은 글리신이다 — 같은 "산성×착화제" 레짐으로 묶었으나
  착화제 종에 따른 차이는 **미검증**(Jani 회귀에서 글리신 계수는 −440.91 로 옥살산
  +536.63 과 부호가 반대다. 두 착화제를 동일시하면 안 된다는 직접 증거).
- 절대값: 이 조건에서 엔진 예측은 10284 nm/min, 실측 2282 nm/min(4.5배 과대).
  절대 MRR 은 여전히 주장 불가 — 순위 전용이다.

## 6. 검증 (실행되는 assert)

```python verify
# 블록1: 현행 코드 경로가 Jani 계열에서 '부호 반대'를 낸다는 것을 실제 코드로 확인
import sys
sys.path.insert(0, ".")
from sim.tier2_physics.slurry_components import oxidizer_coverage_langmuir as theta

K_STORED = 0.8232          # knowledge/params/cu_h2o2_bta.yaml (판정#20)
FLOOR = 0.15               # oxidizer_mech_floor 기본값
C_REF = 3.0                # oxidizer_ref_wt_pct

def f_passivation(C, K=K_STORED, floor=FLOOR, C_ref=C_REF):
    t, tr = theta(C, K), theta(C_ref, K)
    return floor + (1.0 - floor) * (1.0 - t) / (1.0 - tr)

# 기준 농도에서 배수는 항등적으로 1.0 (이 노트가 그 계약을 건드리지 않음을 확인)
assert abs(f_passivation(C_REF) - 1.0) < 1e-12, "기준 조건 배수 1.0 계약이 깨졌다"

# Jani 2025 Table I x Table II — Expt 30/31/32 (실리카 6, 옥살산 0.08M, 글리신 0, DOSS 0.001)
OBS = {3.0: 2282.0, 4.0: 2533.0, 6.0: 2578.0}
obs_ratio = {C: v / OBS[3.0] for C, v in OBS.items()}

pred_36 = f_passivation(6.0) / f_passivation(3.0)
obs_36 = obs_ratio[6.0]
print(f"3->6 wt%: 실측 배수 {obs_36:.3f} vs 현행모델 {pred_36:.3f}")
assert obs_36 > 1.0, "실측은 증가여야 한다 (2282 -> 2578)"
assert pred_36 < 1.0, "현행 피복-억제 분기는 감소를 예측해야 한다"
assert abs(obs_36 - 1.130) < 0.001 and abs(pred_36 - 0.647) < 0.001, \
    f"노트 §3 표값(1.130 / 0.647)과 어긋남: {obs_36:.3f} / {pred_36:.3f}"
print("=> 부호 반증 확정: 실측 +13.0%, 모델 -35.3% (정량 편차가 아니라 방향이 반대)")

# 단조 증가인가 (3점 전부)
vals = [OBS[c] for c in sorted(OBS)]
assert vals == sorted(vals), "Jani 계열은 H2O2에 대해 단조 증가여야 한다"
```

```python verify
# 블록2: Jani 2025 회귀표(Table III)의 H2O2 항 부호·유의성이 위 방향과 일치하는지
# 원문 Table III 인쇄값을 상수로 박고 검사한다 (doi:10.1149/2162-8777/adc59e)
H2O2_COEF, H2O2_P = 96.38, 0.0185          # 1차항
H2O2_SQ_COEF, H2O2_SQ_P = -115.88, 0.2222  # 2차항
OXALIC_COEF, GLYCINE_COEF = 536.63, -440.91

assert H2O2_COEF > 0 and H2O2_P < 0.05, \
    "원문 회귀에서 H2O2 1차항은 양이고 유의해야 한다 (촉진 방향)"
assert H2O2_SQ_P > 0.05, \
    "2차항(곡률)은 비유의 — '정점 없음'이 아니라 '구간 내 미확인'으로 써야 한다"
# 착화제 종에 따라 부호가 갈린다 = 착화제를 하나로 묶으면 안 된다는 직접 증거(§5 한계)
assert OXALIC_COEF > 0 > GLYCINE_COEF, \
    "옥살산과 글리신의 계수 부호가 갈리는 것이 §5 한계 서술의 근거다"
print(f"회귀: [H2O2]={H2O2_COEF:+.2f} (p={H2O2_P}), [H2O2]^2={H2O2_SQ_COEF:+.2f} (p={H2O2_SQ_P})")
print("=> 촉진 방향은 유의, 곡률은 미확인 — 노트 §3 서술과 정합")
```

```python verify
# 블록3: 세 계열이 '평균낼 수 없는 별개 레짐'임을 수치로 — 한 개의 K로 동시에 맞출 수 없다
import sys
sys.path.insert(0, ".")
from sim.tier2_physics.slurry_components import oxidizer_coverage_langmuir as theta

def f_pass(C, K, floor=0.15, C_ref=3.0):
    t, tr = theta(C, K), theta(C_ref, K)
    return floor + (1.0 - floor) * (1.0 - t) / (1.0 - tr)

# 알칼리 계열 (US9200180B2 Ex.5/6/7) — 감소
ALK = {1.0: 11.8, 2.5: 9.2, 5.0: 7.7}
# 산성+착화제 계열 (Jani 2025 Expt 30/31/32) — 증가
ACID = {3.0: 2282.0, 4.0: 2533.0, 6.0: 2578.0}

def sse(K, obs, anchor):
    f_a = f_pass(anchor, K)
    return sum((f_pass(C, K) / f_a - v / obs[anchor]) ** 2 for C, v in obs.items())

# 피복-억제 함수형은 K>0 어디서도 증가할 수 없다 — 산성 계열을 구조적으로 못 담는다
for K in (0.05, 0.2184, 0.8232, 3.0):
    assert f_pass(6.0, K) < f_pass(3.0, K), f"K={K}에서도 피복-억제 분기는 단조 감소다"
print("=> 어떤 K를 골라도 피복-억제 분기는 증가를 표현할 수 없다 (값 재추정으로 해소 불가)")

# 알칼리 계열에는 잘 맞는다 (판정#29 1회차 K*=0.2184 재현) — 즉 함수형이 틀린 게 아니라
# '적용 레짐'이 틀렸다
best_K = min([k / 10000 for k in range(1, 50000)], key=lambda K: sse(K, ALK, 1.0))
print(f"알칼리 계열 독립 최적 K = {best_K:.4f}")
assert abs(best_K - 0.2184) < 0.01, f"판정#29 1회차 K*=0.2184가 재현돼야 한다 (got {best_K})"
print("=> 같은 함수형이 알칼리 레짐에서는 식별되고 산성-착화제 레짐에서는 부호부터 틀린다")
```

## 7. 구현 요청 (소프트웨어 부문 — BIAS, C2 아님)

- **무엇을**: `cu_h2o2_bta` 를 레짐 좌표로 분리한다. 산성(pH<6) × 착화제 존재 가지는
  촉진-포화형(`oxidizer_langmuir_K`), 알칼리 × 무착화제 가지는 현행 피복-억제형
  (`oxidizer_passivation_K`). 두 가지는 **상호배타**이며 팩 상속(base)으로 나눈다.
- **근거 노트**: 이 노트 §3 표 + [[chi-cu-h2o2-independent-refit-us9200180b2]].
- **검증에 쓸 문헌값**: 산성 가지 = Jani 2025 Expt 30/31/32 배수 1.000/1.110/1.130,
  알칼리 가지 = US9200180B2 Ex.5/6/7 배수 1.000/0.780/0.653.
- **선결 조건**: 팩에 착화제(chelator) 선언 축이 없다. `chelator_species` /
  `chelator_M` 를 먼저 도입해야 게이트를 걸 수 있다 — 없는 상태로 pH 만으로 가르면
  판정#37(알칼리 가지)과 축이 겹쳐 이중 계상이 난다.
- **우선순위**: 중. 기준 조건 예측값은 안 바뀌고(배수 1.0 항등), H₂O₂ 스윕 예측만
  개선된다. 다만 현 상태로는 산성 계에서 **방향이 틀린 예측**을 내므로 경고는 즉시 필요.

## 8. 새로 도출한 지식

1. Cu CMP 산화제 항의 부호는 산화제 농도가 아니라 **착화제·pH 레짐**이 정한다.
   같은 H₂O₂ 3→6 wt% 변화가 한 레짐에서는 −35 %, 다른 레짐에서는 +13 % 다.
2. 그러므로 "Cu 산화제 항"을 팩 하나에 단일 함수형으로 두는 것은 구조적으로 불가능하다 —
   K 를 아무리 잘 적합해도 부호를 못 바꾼다(§6 블록3이 assert 로 고정).
3. 착화제끼리도 묶을 수 없다: 같은 회귀에서 옥살산 +536.63, 글리신 −440.91 로 부호가 갈린다.

## 9. 구현 결과 (판정#41)

### 9.0 0단계 — 글리신 레짐 데이터 직접 확인 (전수탐색 결과)

로컬 원문(`papers/jani2025-revisiting-roles-cu-cmp.html`)의 Table I(조성, 실험 1~35)
× Table II(Cu RR)를 파이썬으로 전량 파싱해, (실리카, 옥살산, 글리신, DOSS) 4축을
고정하고 H₂O₂ 만 바뀌는 실험군을 전수탐색했다(코드: 아래 §9.4 verify 블록에 고정).

**결과: 글리신 > 0 인 조건에서 H₂O₂ 만 바뀌는 실험쌍은 35개 실험 전체에 걸쳐**
**단 하나도 없다.** H₂O₂ 만 단독으로 바뀌는 그룹은 정확히 둘뿐이고 **둘 다 글리신=0**
(옥살산 단독계)이다:

| 고정 조건 (실리카,옥살산,글리신,DOSS) | 실험# → H2O2(wt%) → Cu RR(nm/min) |
|---|---|
| (6, 0.08, 0, 0.001) | 30→3→2282, 31→4→2533, 32→6→2578 (기존 §3 표, **증가**) |
| (0, 0.08, 0, 0.001) | 33→6→2326, 16→7→2070 (신규 발견, **감소**) |

둘째 행은 이번 전수탐색에서 새로 드러난 사실이다: 같은 옥살산-단독(글리신=0) 계라도
**실리카 농도(0 vs 6 wt%)에 따라 H₂O₂ 방향성 자체가 갈린다** — 실리카 6에서는 증가,
실리카 0에서는 감소. 즉 §3에서 이미 "산성×착화제=증가"로 일반화한 서술도 실리카 조건을
붙여야 정확하다(실리카 ≥6 wt%, 옥살산 착화제). 이 사실을 §5 한계에 추가한다(§9.5).

**판단(과제 지시 §0 분기)**: 글리신 데이터가 없으므로 **"없으면" 분기**를 따른다 —
옥살산 데이터(실리카 6 조건, Expt 30/31/32)로 산성×착화제 가지를 세우되,
**confidence 는 literature 로 승격하지 않는다.** 글리신 방향은 미검증 상태로 남긴다
(아래 §9.1~§9.3 구현 및 §9.5 정직한 한계 서술 참조).

### 9.1 착화제 선언 축 (선결조건)

`knowledge/params/cu_h2o2_bta.yaml`에 `chelator_species`(=`glycine`, verified — 이미
`abrasive_wt_pct` note에 있던 "글리신 1 wt%"의 조회 키 승격)와 `chelator_M`(=0.1332
mol/L, estimated)을 신설했다. 글리신 MW=75.07 g/mol, **밀도 1.0 g/mL 근사**(슬러리
실측 밀도 미확보, 희박 수용액 가정)로 1 wt% → 10 g/L → 0.1332 mol/L. 다른 4팩에는
선언하지 않는다 — 미선언은 "착화제 없음"으로 취급되지 지어낸 기본값을 넣지 않는다.

### 9.2 `_oxidizer_term` 레짐 게이트

`sim/chemistry.py::_oxidizer_term`에 기존 `oxidizer_langmuir_K`/`oxidizer_passivation_K`
분기 **앞에** 상호배타 게이트를 신설했다: 팩이 `oxidizer_acid_chelator_K`를 선언하고
`slurry_ph`·`chelator_M`이 모두 있고 `slurry_ph < 6 AND chelator_M > 0`이면 촉진-포화형
`f(C) = φ + (1-φ)·θ(C)/θ(C_ref)`(θ는 기존 `oxidizer_coverage_langmuir` 재사용)를 쓴다.
분기 조건은 팩 이름이 아니라 `slurry_ph`/`chelator_M` 필드값으로만 판정한다(판정#34
원칙). 게이트를 안 만족하면(착화제·pH 미선언, 또는 pH≥6) notes에 사유를 남기고 조용히
기존 경로로 폴백한다 — 이 경로가 다른 4팩(oxide_silica/sic_ceria_h2o2/sti_ceria/
w_fe_oxidizer)이 `oxidizer_acid_chelator_K`를 선언하지 않으므로 비트 단위로 불변임을
보장한다(§9.4 계약테스트 + `tests/test_oxidizer_acid_chelator_gate.py`).

`oxidizer_acid_chelator_K=0.7935`는 §9.0의 Expt 30/31/32 3점에 φ=0.15 고정, K 1개만
최소자승 적합(잔차 최대 3.8%@4wt%) — `oxidizer_passivation_K=0.8232`를 적합했던 것과
동일한 방법론(1자유도, 항상 φ 고정)이다.

### 9.3 검증 — 백테스트 부호 정합 & qa_loop

`validation/datasets/jani2025_cu_h2o2_acidic_chelator.yaml`을 `in_scope: false` →
**`in_scope: true` + `used_for_calibration: true`**로 바꿨다. `used_for_calibration:
true`인 이유: 이 3점이 바로 `oxidizer_acid_chelator_K`를 적합한 데이터라서, held-out
ρ로 세면 자기 채점이 된다(F4 자기채점 검사와 동일 원칙) — 그래서 qa_loop의 "유의
평균 ρ" 계산에서 제외되도록 표시했다. 이 데이터셋의 역할은 "모델이 맞혔다"는 held-out
증거가 아니라 "부호가 반증(ρ=-1.000)에서 정합으로 바뀌었다"를 보여주는 재현 확인이다.

실행 결과:
- `pytest -q`: 788 passed(추가 6/1 = 신규 7건 포함). 기존 실패 1건
  (`tests/test_sensitivity.py::test_oxidizer_sensitivity_sign_follows_passivation`)은
  판정#20 시절 "cu_h2o2_bta는 전 구간 음수(억제)"라는, 바로 이 판정이 반증한 가정을
  검사하고 있었다 — 회귀가 아니라 이 판정이 고치는 대상이므로 테스트를 갱신했다
  (양수/촉진 방향으로, 근거 이 노트 §9 인용).
- `tools/completion.py check`: 격자 49/50 **불변**. χ/cu_h2o2_bta confidence는 여전히
  `estimated`다 — 글리신 미검증이라 승격 근거가 없다(§9.0). 격자를 50/50으로 채우려고
  등급을 올리지 않는다(과제 지시 최우선 금지 사항).
- `tools/qa_loop.py run --strict`: PASS, 유의 평균 ρ **0.9442로 불변**(신규 데이터셋이
  `used_for_calibration`으로 유의 집계에서 빠지므로 예상대로). 격리·플래그 목록에
  `jani2025_cu_h2o2_acidic_chelator` 관련 신규 이슈 없음.

### 9.4 계약테스트

`tests/test_oxidizer_acid_chelator_gate.py` 신설(10 테스트, 요구된 6건 이상):
① 다른 4팩 `_oxidizer_term` 비트불변(notes에 판정#41 문구 없음) ② cu_h2o2_bta 실팩
기준조건(C=C_ref=3.0wt%) 배수 항등 1.0 ③ 산성×착화제 가지 3→4→6wt% 단조 증가
④ `chelator_M` 미선언 시 기존(`oxidizer_passivation_K`) 경로와 완전히 같은 값으로
폴백 ⑤ `slurry_ph` 미선언 시 폴백 ⑥ pH≥6(알칼리)이면 착화제가 있어도 게이트 미충족
→ 억제형 경로(배수<1) ⑦ Jani 2025 Expt 30/31/32 재현오차 5% 이내.

```python verify
# Jani 2025 Expt 30/31/32 재현 — 노트 §9.2의 K=0.7935가 실측 배수를 재현하는가
import sys
sys.path.insert(0, ".")
from sim.chemistry import _oxidizer_term

class FakePack:
    def __init__(self, **kw):
        self.d = kw
    def has(self, k): return k in self.d
    def get(self, k): return self.d[k]
    def get_or(self, k, dv): return self.d.get(k, dv)

BASE = dict(oxidizer_ref_wt_pct=3.0, oxidizer_acid_chelator_K=0.7935,
            oxidizer_passivation_K=0.8232, slurry_ph=3.0, chelator_M=0.08)
OBS = {3.0: 2282.0, 4.0: 2533.0, 6.0: 2578.0}
obs_ratio = {C: v / OBS[3.0] for C, v in OBS.items()}

preds = {}
for C in (3.0, 4.0, 6.0):
    d = dict(BASE); d["oxidizer_wt_pct"] = C
    notes = []
    preds[C] = _oxidizer_term(FakePack(**d), notes)
    assert any("판정#41" in n for n in notes), f"C={C}: 게이트가 안 켜졌다"

assert abs(preds[3.0] - 1.0) < 1e-9, "기준조건 배수는 항등적으로 1.0"
for C in (4.0, 6.0):
    err = abs(preds[C] - obs_ratio[C]) / obs_ratio[C]
    print(f"C={C}: 예측 {preds[C]:.4f} vs 실측 {obs_ratio[C]:.4f} (오차 {err:.1%})")
    assert err < 0.05, f"C={C}: 재현오차 {err:.1%}가 5%를 넘는다"
assert preds[6.0] > preds[4.0] > preds[3.0], "부호가 바로잡혔다 — 단조 증가"
print("=> Jani 2025 3점 재현 PASS, 부호 반증(ρ=-1.0)이 정합으로 바뀌었다")
```

### 9.5 한계 (정직한 부기, §5 갱신)

- §5의 "착화제 종 미검증(옥살산≠글리신)" 한계는 §9.0 전수탐색으로 **여전히 해소되지
  않았다** — 글리신 존재 조건의 H2O2 단독 스윕 데이터가 원문에 구조적으로 없다.
  `oxidizer_acid_chelator_K`는 옥살산 데이터의 **방향 대리(proxy)**이지 글리신 실측이
  아니다. confidence를 `estimated`로 고정한 이유가 이것이다.
- **신규 발견(§9.0)**: 옥살산-단독(글리신=0) 계 안에서도 실리카 농도에 따라 방향이
  갈린다(실리카 6wt%: 증가, 실리카 0wt%: 감소, Expt 16/33). 즉 "산성×착화제 = 증가"
  일반화는 최소한 "실리카 ≥6wt%" 조건이 붙어야 하는데, 이 팩의 `abrasive_wt_pct` 기준은
  3.0wt%다 — 적합에 쓴 실리카 조건(6wt%)과 팩의 실사용 실리카 조건이 다르다는 뜻이고,
  이 축은 게이트에 넣지 않았다(미검증 축을 하나 더 얹으면 과적합이다).
- n=3, 단일 실험실 — §5의 기존 한계(BTA 부재, 곡률 미확인)는 그대로 유효하다.
- `validation/…jani2025…yaml`을 `used_for_calibration: true`로 표시했으므로 held-out
  ρ 0.9442는 이 판정으로 **움직이지 않는다** — "정확도가 좋아졌다"가 아니라 "구조적
  반증이 사라졌다(부호 정합)"는 것이 이 판정이 주장하는 전부다.

### 9.6 게이트가 드러낸 기존 데이터셋 결함 (부수 발견, 수정함)

게이트를 넣고 qa_loop을 처음 돌렸을 때 `us9200180b2_cu_h2o2_series`의 ρ가 조용히
**1.0 → −1.0**으로 뒤집였다(격리 대상이라 게이트 PASS/FAIL엔 안 걸렸지만 방향이
틀렸다). 원인: 이 데이터셋(및 `us9200180b2_cu_abrasive_series`)은 실제로 **pH
8.5~10 알칼리·벤젠술폰산계**(노트 프로즈에 이미 그렇게 적혀 있었다)인데 `overrides`에
`slurry_ph`를 넣지 않았다 — 게이트가 없던 시절엔 pH가 산화제 항에 전혀 안 쓰여
무해했지만, 이제 오버라이드가 없으면 팩 기본값(slurry_ph=4.0, chelator_M=0.1332,
둘 다 게이트 조건을 만족)으로 조용히 새 산성×착화제 경로를 잘못 탄다.

원문 특허(`papers/patents/US9200180B2.html`) TABLE 1-b/TABLE 3에서 Example별
정밀 pH를 직접 파싱해 옮겼다(9.5/9.1/8.5 및 9.2/9.8/9.8/10.0 — 기존 노트의
"8.5~9.5" 근사보다 정밀), 착화제 미해당을 `chelator_M: 0.0`으로 명시했다. 수정 후
두 데이터셋 모두 ρ·mape·scale이 이 판정 이전 값으로 정확히 복원됐다(qa_loop
run_index #163, `validation/ledger.jsonl` 확인). 다른 `cu_h2o2_bta` 데이터셋
전수 점검 결과 — `oxidizer_wt_pct`가 조건마다 고정값이거나(C=C_ref 또는 상수) `slurry_ph`
오버라이드가 이미 있어(≥6 또는 독립적으로 게이트를 걸러냄) 추가 결함은 없었다.

교훈: 레짐 게이트를 넣으면 "이전엔 안 쓰이던 필드"가 갑자기 의미를 가진다 —
새 게이트가 참조하는 필드는 그 필드를 프로즈로만 언급하고 오버라이드하지 않은
기존 데이터셋 전체를 감사해야 한다.
