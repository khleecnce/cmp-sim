<!-- V2-SECTION: R2-slurry | 근거: oxidizer, 산화제, chi, 화학, passivation, Langmuir | 정본: ARCHITECTURE-V2.md §3 -->
# χ `cu_h2o2_bta` 산화제 항 재파라미터화 — 정성적 부호 반증 → Langmuir 부동태 억제항(1파라미터)으로 교체 (판정#20)

> 작성일: 2026-09-14 | 대상: `sim/chemistry.py::_oxidizer_term`, `sim/factors.py::_f_chi`,
> `knowledge/params/cu_h2o2_bta.yaml`
> 선행: [[chi-oxidizer-curve-exponent-identifiability]](판정#19, 이 과제를 이관한 노트),
> [[w-cmp-wo3-passivation-oxidizer-kaufman]], [[bta-inhibitor-langmuir-K-effective-cu-cmp-falsification]]
> 이 노트가 다루는 것은 형상 파라미터 값 재추정(예: `oxidizer_curve_n`의 크기 조정)이 아니라
> **모델 함수형 자체의 부호(sign) 반증과 교체**다 — 같은 축을 다루는
> [[chi-oxidizer-concentration-curve-exponent-derivation]](w_fe n=2.5 재보정, cu n=2.0 유지)와는
> 별개 과제다: 그 노트는 레거시 단봉 곡선의 **지수** 안에서 값을 다듬었고, 이 노트는 cu 계에서
> 레거시 단봉 곡선 자체가 **틀린 부호**를 낸다는 것을 실측으로 확정하고 구조를 바꾼다.

## 1. 질문

판정#19는 `oxidizer_curve_n`+`oxidizer_peak_wt_pct` 2파라미터가 정점 아래 관측만으로
완전축퇴(식별 불가)함을 수치로 증명하고, "문헌 미확보"가 아니라 **재파라미터화(구현) 과제**로
이관했다. `w_fe_oxidizer`는 이미 식별 가능한 1파라미터 Langmuir 피복 촉진항
(`oxidizer_langmuir_K`, `sim/chemistry.py::_oxidizer_term`)으로 교체 완료했다(2026-09-14,
커밋 7b3f42d). `cu_h2o2_bta`는 아직 레거시 그대로다.

이 노트는 그 이관을 cu 팩에 적용한다. 단, 적용 전에 먼저 확인해야 할 것이 있다:
**같은 함수형(Langmuir 촉진, θ가 증가할수록 MRR도 증가)을 그대로 이식해도 되는가?**
w_fe는 Fe(III) 산화제가 많을수록 W가 계속 더 깎이는 계(포화형)였다. Cu+H2O2가 같은 방향인지
저장소 안의 실측으로 먼저 검사한다.

## 2. 근거

### 2.1 대상계 직접 실측 (특허 실시예 표, 저장소 확보)

- **US20110165777A1** (DuPont Air Products, "Method and Slurry for Tuning Low-K Versus Copper
  Removal Rates During CMP", 2011 공개), TABLE 2(KOH 0.41 wt%, Zonyl FSN 500 ppm 고정, 콜로이달
  실리카 5 wt%, 벤젠술폰산 1.0 wt%, BTA 100 ppm, 2.0 psi, Politex 패드 — 산화제 축만 스윕).
  `validation/datasets/us20110165777a1_cu_h2o2_series.yaml`에 저장. H2O2 0/0.25/0.5/1.0 wt%
  → Cu RR 18.7/14.0/12.9/12.1 nm/min(원문 Å/min ÷10). **단조 감소.**
- **US9200180B2** (Air Products/현 Versum·Merck, "CMP composition having benzenesulfonic acid
  and per-compound oxidizing agents", 2015), TABLE 1-b Examples 5/6/7 (콜로이달 실리카 3 wt%,
  벤젠술폰산 2 wt%, 2.0 psi, BTA 없음 — 팩과 조성 다름, 교차확인 전용).
  `validation/datasets/us9200180b2_cu_h2o2_series.yaml`. H2O2 1/2.5/5 wt% → Cu RR
  11.8/9.2/7.7 nm/min. **단조 감소.**
- 두 문헌 모두 **E2급**(1차 문헌, 실시예 표에 직접 인쇄된 폐형식 실측값) — 단 절대 MRR은
  팩 기준(400~800 nm/min, Kp 역산 근거)보다 한 자릿수 이상 낮아 **순위/비율 전용**
  (두 데이터셋 파일 자체가 이 점을 명시).

### 2.2 메커니즘 1차 문헌

- **Ein-Eli, Abelev, Starosvetsky (2004; received 2003)**, "Electrochemical aspects of copper
  chemical mechanical planarization (CMP) in peroxide based slurries containing BTA and glycine,"
  *Electrochimica Acta* 49, 1499–1503. DOI: 10.1016/j.electacta.2003.11.010.
  `papers/aksu2003-electrochimica-bta-glycine-cu-cmp.pdf.txt` 원문 도입부(Introduction, 1500쪽
  왼쪽 단) 직접 확인:
  > "the expected increase in copper dissolution rate with peroxide H2O2 content was found only
  > once the peroxide concentration was in the region of 1–3%. Further increase in H2O2
  > concentration resulted in reduction of dissolution rate [3,5]. Many research groups [1–10]
  > suggested that the decrease in copper etch rate with increase in hydrogen peroxide
  > concentration (>3%) was a result of copper passivation."
  이 문장 자체는 refs [3,5]를 인용한 서술(2차 인용, E5) — 정량 곡선은 없다. 다만 **메커니즘
  방향**(고농도 H2O2 → Cu 표면 부동태화 → 용해/제거율 감소)은 이 논문 저자들의 결론이기도
  하며, 판정#19 노트가 이미 `oxidizer_peak_wt_pct=3.0`을 이 서술로 독립 확증한 바 있다.
- **Kaufman et al. (1991)**, *J. Electrochem. Soc.* 138(11), 3460. DOI: 10.1149/1.2085434.
  `papers/kaufman1991-w-cmp-mechanism.pdf.txt` — 화학(산화막 형성)과 기계(연마 제거) 경쟁
  모델의 원전. W 계 원문이며 정량 형상은 주지 않지만, "생성 대 제거 가능성의 경쟁"이라는
  구조 자체(§3의 뼈대)를 제공한다.

## 3. 단계 1 — 반증을 수치로 확정

현행 레거시 경로(`oxidizer_peak_wt_pct=3.0`, `oxidizer_curve_n=2.0`, `oxidizer_ref_wt_pct=3.0`,
`oxidizer_mech_floor` 미선언→기본값 0.15)를 실제 `sim/chemistry.py::chemistry_factor`로 그대로
호출하면:

| C (wt%) | 모델 f(C) | 모델 비율 f(C)/f(0) | 실측 비율 (TABLE 2, US20110165777A1) |
|---|---|---|---|
| 0.0 | 0.150 | 1.000 | 1.000 |
| 0.25 | 0.353 | 2.353 (**+135%**) | 0.749 (**−25%**) |
| 0.5 | 0.524 | 3.493 (**+249%**) | 0.690 (**−31%**) |
| 1.0 | 0.764 | 5.093 (**+409%**) | 0.647 (**−35%**) |

부호가 반대다 — 정량 편차가 아니라 **정성적 반증**이다(§7 블록1이 이 표 전체를 코드로 재현·assert).

## 4. 단계 2 — 물리에서 유도

### 4.1 경쟁 구조

Kaufman류 경쟁 모델의 뼈대는 두 경로의 곱이다:
`제거율(C) ∝ (산화/연화가 만드는 제거 용이성) × (표면이 실제로 노출돼 있어 그 용이성이
작용할 수 있는 분율)`.

W 계(w_fe_oxidizer)에서는 Fe(III)/H2O2가 만드는 WO3 층이 W보다 무르고, 관측 구간
전체에서 "더 두꺼운 산화막 = 더 쉬운 기계적 제거"가 지배적이라 촉진 방향
(θ↑ → 제거↑, `oxidizer_langmuir_K` 경로)이 맞다.

Cu 계는 다르다. §2.2가 확인한 대로 H2O2 저농도(≲1~3%)에서는 산화막이 표면을 무르게 해
전기화학적 용해를 촉진할 수 있지만, **그 이상에서는 부동태(passivation)가 지배해 오히려
막이 반응 사이트를 덮어 제거 가능 분율을 낮춘다.** 즉 같은 두 경로의 경쟁이지만, 어느 경로가
관측 구간을 지배하는지가 W와 Cu에서 다르다.

### 4.2 관측 구간이 어느 가지에 있는가 — 데이터가 결정한다

§3의 실측은 **0 wt%부터 이미 단조 감소**한다(TABLE 2: 0→0.25→0.5→1.0 wt% 전 구간 감소,
증가 구간이 전혀 없다). US9200180B2(1→2.5→5 wt%, 다른 조성)도 전 구간 감소다. 즉 이
슬러리 화학(콜로이달 실리카 + 벤젠술폰산 + BTA/무억제제, KOH 알칼리 pH 10~11)에서는
**정점이 관측 최저 농도(0 wt%)보다 왼쪽에 있거나, 애초에 이 조성에서 촉진 가지가
관측되지 않는다.** Aksu(2003)가 인용한 1~3% 촉진 구간은 Na2SO4 pH 4의 산성 전기화학
셀 실측(BTA·glycine 존재)이지, 이 알칼리 CMP 슬러리의 조건이 아니다 — 계가 다르면
정점 위치가 이동할 수 있다는 것은 판정#19 자신도 W/Fe 대 Cu에서 이미 인정한 전제다.

**결론: 이 팩의 관측 가능 범위(0~7 wt%)는 부동태 억제가 지배하는 단조 감소 가지 하나로
충분히 설명된다.** 촉진 가지를 별도 파라미터로 세우면(옵션 B, 2파라미터) 그 촉진 가지를
지지하는 관측이 이 팩의 데이터셋에는 전혀 없다 — 판정#19가 경고한 것과 같은 실수
(관측되지 않는 영역에 자유도를 쓰는 것)를 반복하게 된다.

### 4.3 옵션 판단 — **(A) 채택**

- **(A) Langmuir 부동태 억제항 단독, 자유 파라미터 1개(K_pass)** — §4.2가 보인 대로 관측
  전 구간이 감소 가지이므로 촉진 가지에 파라미터를 쓸 근거가 없다. **채택.**
- (B) 촉진×억제 곱, 2파라미터 — 촉진 가지를 지지하는 관측이 이 데이터셋에 없으므로 두 번째
  파라미터가 식별 불가능하다(판정#19와 같은 함정 반복). **기각.**
- (C) 식별 불가/종결 — 데이터가 방향과 대략적 크기(§5)를 모두 주므로 종결할 이유가 없다.
  **기각.**

## 5. 식별성 검사 — (A)의 K_pass가 진짜로 식별되는가

θ(C)=K·C/(1+K·C) (기존 `SC.oxidizer_coverage_langmuir`, `w_fe_oxidizer`의 촉진항과 동일 함수),
부동태 억제항: `f(C) = φ + (1-φ)·(1-θ(C))/(1-θ(C_ref))`, φ=`oxidizer_mech_floor`
(팩 미선언 → 기본값 0.15, 4개 독립 금속막 계 수렴값), C_ref=`oxidizer_ref_wt_pct`=3.0
(기존 팩값 유지, Kp 역산 기준점과 일치시켜 이중계상 방지).

TABLE 2 4점(0/0.25/0.5/1.0 wt%)에 φ=0.15 고정, K_pass 1개만 최소자승으로 맞추면:

| C | 실측 비율 | 모델 비율 (K=0.8232) | 오차 |
|---|---|---|---|
| 0.0 | 1.000 | 1.000 | 0% |
| 0.25 | 0.749 | 0.838 | +11.9% |
| 0.5 | 0.690 | 0.723 | +4.7% |
| 1.0 | 0.647 | 0.570 | −11.9% |

SSE(K)는 K=0.823 근방에서 뾰족한 단일 최소를 갖는다(K=0.1→SSE 0.199, K=0.823→0.0149,
K=3.0→0.254 — §7 블록2). 이는 판정#19의 축퇴 사례(다른 (n,C_peak) 조합이 잔차 0으로
동일하게 재현)와 **질적으로 다르다**: 여기서는 자유 파라미터가 K 하나뿐이고, 그 하나를
다른 값으로 바꾸면 잔차가 뚜렷이 나빠진다 — 식별 가능하다.

⚠ 정직한 부기: φ까지 함께 자유롭게 풀면(2파라미터) SSE 최소값이 φ=0.05~0.50 범위에서
0.0115~0.0155로 크게 다르지 않다(§7 블록2) — 즉 **φ와 K를 동시에 데이터에서 뽑으려 하면
약하게 축퇴한다.** 그래서 φ는 데이터에서 뽑지 않고 `w_fe_oxidizer`와 동일한 방식으로
외부에서 정한 값(4계 독립 수렴 0.12~0.27의 중앙 0.15)을 그대로 쓴다 — 자유 파라미터는
K 하나로 유지된다. 이것이 옵션(B)를 기각한 것과 같은 원칙이다: **식별 안 되는 자유도는
추가하지 않는다.**

## 6. 결론 및 구현

**옵션 (A) 채택.** `sim/chemistry.py::_oxidizer_term`에 세 번째 경로를 추가했다
(`oxidizer_langmuir_K` 촉진 / `oxidizer_passivation_K` 억제 / 레거시 (n,C_peak) — 상호
배타, 우선순위는 이 순서). `cu_h2o2_bta.yaml`에 `oxidizer_passivation_K: 0.8232`
(unit 1/wt%, confidence: **estimated** — 방향은 1차 실측+메커니즘 문헌이 뒷받침하지만
값 자체는 4점 최소자승 적합이고 잔차가 최대 11.9%라 literature 문턱에는 못 미친다)를
추가한다.

레거시 키(`oxidizer_curve_n`, `oxidizer_peak_wt_pct`)는 **삭제하지 않는다** — `w_fe_oxidizer`
선례와 동일하게 비활성 하위호환 값으로 남긴다. `sim/factors.py::_f_chi`의 confidence 소스도
`w_fe_oxidizer` 때와 같은 패턴으로 확장한다: `oxidizer_passivation_K`가 있으면 그 키의 등급을
읽고, 레거시 키는 등급 계산에서 제외한다.

`kp_m_per_pa`(estimated, 문헌 범위 역산)는 건드리지 않는다 — 이 재파라미터화는 상대 배수
함수형 문제이지 절대 MRR 보정이 아니다.

### 6.1 교차확인 (피팅에 쓰지 않음)

- US9200180B2(다른 조성, BTA 없음, 알칼리): 실측 비율(C=1 기준) 1.0/0.780/0.653, 모델
  1.0/0.631/0.411 — **방향(단조 감소) 일치**, 크기는 모델이 더 가파르다(다른 화학종이므로
  당연히 정량 일치는 기대하지 않는다, §7 블록3).
- TABLE 1(같은 특허, KOH 0.59 wt%, pH 11.1, H2O2 1~7 wt%): 실측이 거의 평평(15~18 nm/min,
  측정 산포 지배 — 데이터셋 자신의 경고)한 반면 모델은 1→7 wt%에서 계속 감소(비율
  1.0→0.332)를 예측한다. 이 데이터셋의 pH(11.1)는 TABLE 2(10.3)와 다르고 `cu_h2o2_bta`
  팩에는 pH 항이 이 산화제 항과 결합돼 있지 않다 — **미모델링된 pH 커플링으로 인한
  한계로 기록**하고 K_pass를 이 지점에 맞춰 조정하지 않는다(TABLE 2가 통제가 가장 좋은
  주 근거, TABLE 1은 애초에 정량 근거로 쓰지 말라고 데이터셋 자신이 경고한다).

## 7. 한계

1. K_pass=0.8232는 4점 최소자승 적합값이다 — 잔차 최대 11.9%, R² 미보고(4점 비선형 적합이라
   생략). 문헌에서 직접 준 폐형식 상수가 아니므로 confidence=estimated가 정직하다.
2. φ(=`oxidizer_mech_floor`)는 Cu 계 자체의 관측이 아니라 4개 독립 금속막 계에서 수렴한
   외부값(0.12~0.27 대역의 중앙 0.15)이다. §5가 보인 대로 φ와 K를 동시에 이 데이터에서
   뽑으면 약하게 축퇴하므로, φ는 데이터에서 추정하지 않는다 — 이 팩 고유의 φ 검증은
   미확보.
3. TABLE 1(1~7 wt%, KOH 0.59)에서 모델과 실측이 어긋난다(§6.1) — pH 커플링 미모델링.
4. 촉진 가지(저농도 H2O2에서 MRR이 오히려 오르는 영역, Aksu 2003이 인용한 1~3% 구간)가
   이 슬러리 화학에서 실제로 존재하지 않는지, 아니면 0 wt% 미만(관측 불가능한 음수 농도)
   에 있는지는 이 데이터로 구분할 수 없다 — 어느 쪽이든 관측 범위(≥0 wt%) 안에서는
   단조 감소 가지 하나로 충분히 설명되므로 실무적 차이는 없다.
5. US9200180B2 교차확인은 다른 조성(BTA 없음, 벤젠술폰산 2 wt%, 알칼리)이라 방향만
   신뢰하고 크기는 신뢰하지 않는다(데이터셋 자신의 경고와 동일).

## 8. 코드 재현 (verify)

```python verify
# 블록1: 레거시 경로의 부호 반증 — 실제 sim/chemistry.py::chemistry_factor를 그대로 호출
import sys
sys.path.insert(0, ".")
from sim.chemistry import chemistry_factor

class FakePack:
    def __init__(self, **kw):
        self.d = kw
        self.name = "fake"
    def has(self, k): return k in self.d
    def get(self, k): return self.d[k]
    def get_or(self, k, dv): return self.d.get(k, dv)

def legacy_f(C):
    return chemistry_factor(FakePack(
        abrasive="alumina",
        oxidizer_wt_pct=C, oxidizer_ref_wt_pct=3.0,
        oxidizer_peak_wt_pct=3.0, oxidizer_curve_n=2.0,
    )).factor

legacy = {C: legacy_f(C) for C in (0.0, 0.25, 0.5, 1.0, 3.0, 5.0, 7.0)}
for C, v in legacy.items():
    print(f"legacy f({C})={v:.3f}")

# 팩 기본값(문서화된 핵심 관찰)과 1e-3 이내 일치해야 한다
expected = {0.0: 0.150, 0.25: 0.353, 0.5: 0.524, 1.0: 0.764, 3.0: 1.000, 5.0: 0.951, 7.0: 0.882}
for C, exp in expected.items():
    assert abs(legacy[C] - exp) < 1e-3, f"legacy f({C})={legacy[C]:.3f} != 문서값 {exp}"

# 실측(US20110165777A1 TABLE 2) 비율
mrr_obs = {0.0: 18.7, 0.25: 14.0, 0.5: 12.9, 1.0: 12.1}
obs_ratio = {C: v / mrr_obs[0.0] for C, v in mrr_obs.items()}

# 모델 비율(C=0 기준)
model_ratio = {C: legacy[C] / legacy[0.0] for C in (0.0, 0.25, 0.5, 1.0)}

print("C     모델비율   실측비율")
for C in (0.0, 0.25, 0.5, 1.0):
    print(f"{C:<5} {model_ratio[C]:.3f}      {obs_ratio[C]:.3f}")

# 부호 반증 — C>0에서 모델은 증가(>1), 실측은 감소(<1). 정성적으로 반대.
for C in (0.25, 0.5, 1.0):
    assert model_ratio[C] > 1.30, f"레거시 모델이 C={C}에서 뚜렷이 증가해야 반증이 성립 (got {model_ratio[C]:.3f})"
    assert obs_ratio[C] < 0.80, f"실측이 C={C}에서 뚜렷이 감소해야 반증이 성립 (got {obs_ratio[C]:.3f})"
    assert (model_ratio[C] - 1.0) * (obs_ratio[C] - 1.0) < 0, (
        f"C={C}: 모델 변화량과 실측 변화량의 부호가 같다 — 반증이 성립하지 않음")
print("=> 레거시 경로는 0~1 wt% 구간에서 실측과 정반대 부호를 예측한다 (정성적 반증 확정)")
```

```python verify
# 블록2: 새 Langmuir 부동태 억제항 — 식별성(SSE 단일최소) + 4점 재현 오차
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

def new_f_code(C, K):
    """실제 코드 경로(_oxidizer_term의 oxidizer_passivation_K 분기) 호출."""
    return chemistry_factor(FakePack(
        abrasive="alumina",
        oxidizer_wt_pct=C, oxidizer_ref_wt_pct=3.0,
        oxidizer_passivation_K=K,
    )).factor

def new_f_hand(C, K, floor=0.15, Cref=3.0):
    """폐형식을 손으로 재구현 — 코드 경로와 정확히 일치해야 한다(교차검증)."""
    t, tr = theta(C, K), theta(Cref, K)
    return floor + (1.0 - floor) * (1.0 - t) / (1.0 - tr)

K_STORED = 0.8232
for C in (0.0, 0.25, 0.5, 1.0, 3.0, 5.0, 7.0):
    a, b = new_f_code(C, K_STORED), new_f_hand(C, K_STORED)
    assert abs(a - b) < 1e-9, f"코드 경로와 손 유도가 C={C}에서 어긋남: {a} vs {b}"
print("코드 경로(_oxidizer_term)와 폐형식 손 유도가 전 구간에서 1e-9 이내 일치")

# f(C_ref)=1 항등
assert abs(new_f_code(3.0, K_STORED) - 1.0) < 1e-9

# 최소자승 재현 — TABLE 2 4점
mrr_obs = {0.0: 18.7, 0.25: 14.0, 0.5: 12.9, 1.0: 12.1}
obs_ratio = {C: v / mrr_obs[0.0] for C, v in mrr_obs.items()}

def sse(K):
    f0 = new_f_hand(0.0, K)
    return sum((new_f_hand(C, K) / f0 - r) ** 2 for C, r in obs_ratio.items())

# 격자 탐색으로 최소 위치 확인 (scipy 의존 없이)
best_K, best_sse = None, 1e9
K = 0.01
while K <= 5.0:
    s = sse(K)
    if s < best_sse:
        best_sse, best_K = s, K
    K += 0.0005
print(f"격자탐색 최적 K={best_K:.4f}, SSE={best_sse:.5f} (저장값 {K_STORED})")
assert abs(best_K - K_STORED) < 0.01, "저장된 K가 최소자승 최적값과 어긋난다"

for C, r in obs_ratio.items():
    f0 = new_f_hand(0.0, K_STORED)
    pred = new_f_hand(C, K_STORED) / f0
    err_pct = 100 * (pred - r) / r if r else 0.0
    print(f"C={C}: 실측비율={r:.4f} 모델비율={pred:.4f} 오차={err_pct:+.1f}%")
    assert abs(err_pct) < 15.0, f"C={C} 오차 {err_pct:.1f}%가 15%를 넘음 — 재현 실패"

# 식별성 — SSE(K)가 최적값 근방에서 뾰족한 단일최소인가 (판정#19의 축퇴와 대비)
sse_far_low = sse(best_K * 0.3)
sse_far_high = sse(best_K * 3.0)
assert sse_far_low > 5 * best_sse, "K를 30%로 낮춰도 잔차가 거의 그대로면 축퇴 의심"
assert sse_far_high > 5 * best_sse, "K를 3배로 올려도 잔차가 거의 그대로면 축퇴 의심"
print(f"식별성 확인: SSE(0.3K)={sse_far_low:.4f}, SSE(K*)={best_sse:.5f}, SSE(3K)={sse_far_high:.4f} "
      "— 최적값에서 뚜렷이 벗어나면 잔차가 5배 이상 나빠진다 (단일 자유파라미터가 진짜 식별됨)")

# 정직한 부기 — floor(phi)까지 같이 풀면 약하게 축퇴한다 (그래서 phi는 고정한다)
def sse_2d(K, floor):
    def f(C): return floor + (1.0 - floor) * (1.0 - theta(C, K)) / (1.0 - theta(3.0, K))
    f0 = f(0.0)
    return sum((f(C) / f0 - r) ** 2 for C, r in obs_ratio.items())

def best_K_for_floor(floor):
    bK, bS = None, 1e9
    K = 0.01
    while K <= 5.0:
        s = sse_2d(K, floor)
        if s < bS:
            bS, bK = s, K
        K += 0.001
    return bK, bS

sse_at_floors = [best_K_for_floor(fl)[1] for fl in (0.05, 0.15, 0.27, 0.50)]
print("floor별 최적 SSE:", [f"{s:.4f}" for s in sse_at_floors])
assert max(sse_at_floors) / min(sse_at_floors) < 2.0, (
    "floor를 넓게 흔들어도 최적 SSE가 2배 이내면 (K,floor) 동시자유는 약하게 축퇴 — "
    "그래서 floor를 외부값(0.15)으로 고정하고 K만 자유도로 남긴다")
```

```python verify
# 블록3: 교차확인(피팅 아님) — US9200180B2 랭킹 일치, TABLE 1 불일치를 정직하게 기록
import sys
sys.path.insert(0, ".")
from sim.chemistry import chemistry_factor

class FakePack:
    def __init__(self, **kw):
        self.d = kw
        self.name = "fake"
    def has(self, k): return k in self.d
    def get(self, k): return self.d[k]
    def get_or(self, k, dv): return self.d.get(k, dv)

def new_f(C, K=0.8232):
    return chemistry_factor(FakePack(
        abrasive="alumina",
        oxidizer_wt_pct=C, oxidizer_ref_wt_pct=3.0,
        oxidizer_passivation_K=K,
    )).factor

# US9200180B2: 1 / 2.5 / 5 wt% -> 11.8 / 9.2 / 7.7 nm/min (다른 조성, 랭킹만 확인)
obs = {1.0: 11.8, 2.5: 9.2, 5.0: 7.7}
model = {C: new_f(C) for C in obs}
obs_sorted = sorted(obs, key=lambda c: obs[c], reverse=True)
model_sorted = sorted(model, key=lambda c: model[c], reverse=True)
assert obs_sorted == model_sorted == [1.0, 2.5, 5.0], "랭킹(1<2.5<5 wt%일수록 MRR 낮음)이 어긋남"
print(f"US9200180B2 랭킹 일치 확인: obs 순서={obs_sorted}, model 순서={model_sorted}")

# TABLE 1(KOH0.59, pH11.1): 실측이 거의 평평, 모델은 계속 감소 -> 불일치를 정직하게 수치로 기록
t1_obs = {1.0: 16.0, 3.0: 15.8, 5.0: 15.4, 7.0: 15.7}  # FSN 0ppm 행
t1_obs_ratio = {C: v / t1_obs[1.0] for C, v in t1_obs.items()}
t1_model_ratio = {C: new_f(C) / new_f(1.0) for C in t1_obs}
print("TABLE1 (실측 거의 평평 vs 모델 계속 감소, pH 커플링 미모델링 — 한계 §7-3):")
for C in t1_obs:
    print(f"  C={C}: 실측비율={t1_obs_ratio[C]:.3f}  모델비율={t1_model_ratio[C]:.3f}")
assert max(t1_obs_ratio.values()) - min(t1_obs_ratio.values()) < 0.05, "TABLE1 실측이 실제로 거의 평평한지 확인"
assert max(t1_model_ratio.values()) - min(t1_model_ratio.values()) > 0.5, "모델은 이 구간에서 뚜렷이 갈려야 불일치가 정직하게 드러남"
print("=> TABLE1 불일치는 은폐하지 않고 §7 한계 3항에 기록한다 (pH 11.1 vs 10.3, 팩에 pH 커플링 없음)")
```
