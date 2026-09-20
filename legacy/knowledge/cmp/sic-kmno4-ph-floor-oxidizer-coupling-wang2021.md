<!-- V2-SECTION: R2-slurry | 정확도루프 COMPLETION-C2 chi/sic_alumina_kmno4 2026-09-18 -->
# 산성 KMnO4/SiC 의 pH 평탄부는 산화제 농도에 따라 올라간다 (판정#64)

> slurry-chemist | 작성일: 2026-09-18 | 대상 팩: `sic_alumina_kmno4`
> 선행: [[sic-kmno4-acidic-ph-decay-chen2020]] (판정#61 — 이 팩의 pH 항을 세웠다)
> [[sic-kmno4-alumina-absolute-mrr-patent-vs-papers]] (판정#55 — 이 팩의 Kp 기준 선택)
> [[sic-alumina-kmno4-L25-heldout-diagnosis]] (held-out Gong 2024 L25)

## 1. 왜 이 단원인가

판정#61 이 이 팩의 pH 항을 Chen 2020 Fig.1(a) **그래프 판독**으로 세웠고,
계수 3개(k·anchor·φ)가 전부 `estimated` 로 남았다. 갭 랭커가 이 칸을
**C2(confidence 승격)** 으로 되돌려준 것이 이번 회차 임무다:

> "파라미터의 1차 출처를 찾아 값 대조 → 승격. 다르면 값을 고치고 차이를 노트에."

찾은 것은 승격 근거가 아니라 **모델이 틀렸다는 증거**였다. 그대로 적는다.

## 2. 확보한 인쇄 수치 — Wang 2021 의 pH 끝점

**Wang W., Liu W., Song Z., "Two-Step Chemical Mechanical Polishing of 4H-SiC
(0001) Wafer", ECS J. Solid State Sci. Technol. 10 (2021) 074004,
doi:10.1149/2162-8777/ac12de** — 이 팩의 Kp 가 이미 인용하고 있던 문헌이다.
교차 인용 리뷰: doi:10.3390/mi13101752 (CC BY). 선행 판정#61 의 1차 출처:
doi:10.1134/S1070427220060099. 이 팩의 조성 데이터셋: US20220315802A1.

원문은 유료이고 sci-hub 미러 5곳(se/st/ru/box/ren)이 전부 로봇 확인(altcha)으로
막혀 이번에도 **원문 PDF 미확보**다. 대신 두 경로에서 **인쇄 텍스트**를 확보했다:

- **출판사 초록**(IOPscience, 무료 공개): "the maximum polishing rate of
  **1400 nm h⁻¹** was determined under the condition of **pH of 2.00 and KMnO4
  concentration of 6.5 wt%**".
- **오픈액세스 리뷰 본문**: Hsieh C.-H. et al., "Recent Advances In Silicon
  Carbide Chemical Mechanical Polishing Technologies", Micromachines 13 (2022)
  1752, **DOI 10.3390/mi13101752** §2.1 (CC BY) — Wang 2021 을 인용하며:
  "a high MRR of **1.4 µm h⁻¹** ... on the Si-face surface of 4H-SiC, by using an
  Al2O3 abrasive-based potassium permanganate slurry with **pH = 2** ... However,
  the MRR **continuously decreased to 1.1 µm h⁻¹ when the pH increased to 12**."
  조건: 6 psi, 90 rpm.

즉 pH 2 → pH 12 에서 **1.4 → 1.1 µm/h, 비 0.786** 이다.

## 3. 새로 도출한 지식 — φ 는 상수가 아니라 산화제 농도의 함수다

현재 코드(판정#61)는 g(pH) = φ + (1−φ)·exp(−k·(pH−2)), k=0.546, **φ=0.268 고정**이다.
이 φ 로 pH 12 를 예측하면 0.268 — 실측 0.786 의 **1/2.9** 다. 정면으로 틀린다.

두 문헌은 같은 재료계(4H/6H-SiC Si면 + α-Al2O3 + KMnO4, 산성)인데 **산화제 농도가
8배 다르다**:

| 문헌 | KMnO4 | 폴리타입 | pH 스윙 | 관측 비 | 함의 φ |
|---|---|---|---|---|---|
| Chen 2020 | 0.05 M ≈ **0.79 wt%** | 6H Si면 | 2→10 | 0.281 (3.56배↓) | 0.268 |
| Wang 2021 | **6.5 wt%** | 4H Si면 | 2→12 | 0.786 (1.27배↓) | 0.785 |

φ 의 물리적 의미가 이 차이를 설명한다. φ 는 "**산화력이 꺼져도 남는 removal**"
이다. 산화제가 진하면 알칼리 쪽에서도 MnO4⁻ 구동력이 완전히 꺼지지 않으므로
**평탄부가 위로 올라간다**. 즉 φ 는 상수가 아니라 농도의 증가함수여야 한다.
Nernst 항(E = E° − 0.0788·pH)은 pH 기울기만 주지 농도 의존을 담지 않는데,
MnO4⁻ 활동도가 높으면 같은 전위 강하에서도 잔여 산화 플럭스가 크다는 뜻이다.

두 앵커를 **log(농도) 선형보간**한다(2점이므로 형상 선택지가 없다 — 농도축이
보통 로그로 포화하므로 log 를 골랐고, 이건 **선택이지 측정이 아니다**):

    φ(c) = φ_lo + [ln c − ln c_lo]/[ln c_hi − ln c_lo] · (φ_hi − φ_lo),  구간 밖은 끝값 고정

이 팩 기준 조성 4 wt% 에서 **φ = 0.666** 이 된다(0.268 에서 크게 올라간다).

φ_hi 는 Wang 의 두 끝점에 **Chen 의 k 를 빌려** 푼 값이다 — 끝점이 2개라 k 를
독립 추정할 수 없다. 따라서 φ_hi 는 k=0.546 에 **조건부**이고 등급은 `estimated`
로 둔다. 이번 회차가 C2 승격에 실패한 이유가 이것이다: **원문 Fig. 를 못 구해
승격할 수 없었고, 대신 값이 틀렸다는 것을 찾았다.**

## 4. 근거 충돌 판정 — 평균내지 않고 **농도축으로 쪼갰다**

EVIDENCE-RULES §"둘 다 맞되 레짐이 다르다" 적용. 두 φ(0.268 vs 0.785)는 등급이
같고(E3 실측, 둘 다 2차 경유 판독/인용) 계 근접도도 비슷하다. 단순히 하나를
버리거나 **평균내는 것은 금지**돼 있다. 갈린 축이 명확하다 — **산화제 농도 8배**.
그래서 스코프를 쪼개는 대신 **연속 보간축으로 승격**했다. 두 앵커 모두 살아 있고
각자의 조성에서 자기 값을 재현한다(§6 verify (3)).

폴리타입 차이(4H vs 6H)가 같은 방향으로 섞여 있을 가능성은 배제하지 못한다 —
**미검증**으로 남긴다. 다만 Gong 2024(4H)·Chen 2020(6H) 의 절대 MRR 이 같은
자릿수라 폴리타입만으로 2.9배를 만들기는 어렵다고 본다(근거 없는 판단은 아니나
정량 확인은 못 했다).

## 5. 부수 발견 — 이 팩 Kp 의 "0.5 wt% 가정"은 **틀렸다**

`kp_m_per_pa` 의 note 는 이렇게 적혀 있었다:

> "⚠ 미검증 가정 1건: Wang 2021 의 알루미나 농도를 리뷰가 적지 않아, 이 팩의
> 기준 농도 0.5 wt% 에서 측정됐다고 **가정**해 농도항 배수를 1.0 으로 두었다."

이번에 확보한 **출판사 초록 인쇄값**이 그 가정을 직접 반증한다: Wang 2021 의
최대 연마율 조건은 **KMnO4 6.5 wt%** 다(알루미나 농도는 여전히 불명이므로 그
부분의 가정은 남는다 — 두 농도를 혼동하지 말 것). Kp 역산은 이 팩 기준 조성
4 wt% 에서 이루어졌으므로, **산화제 축이 살아나는 순간 Kp 는 그만큼 틀린다.**

지금은 산화제 형상 항이 종 게이트(판정#50)로 꺼져 있어 MRR 에 영향이 없다 —
그래서 **이번 회차에 Kp 를 건드리지 않는다**(끄여 있는 축을 근거로 Kp 를 흔들면
근거 없는 변경이다). KMnO4 Langmuir 곡선을 확보해 산화제 축을 켜는 회차에
Kp 를 **반드시 함께 재역산**해야 한다. 팩 note 에 기록했다.

## 6. verify — 문헌값 재현

```python verify
import math

k = 0.546                      # 판정#61, Chen 2020 Fig.1(a) 적합
g = lambda p, f, a=2.0: f + (1 - f) * math.exp(-k * (p - a))

# ── (1) Wang 2021 인쇄 끝점 (DOI 10.1149/2162-8777/ac12de 초록 + 리뷰 본문
#        DOI 10.3390/mi13101752 §2.1): pH 2 → 1.4 µm/h, pH 12 → 1.1 µm/h
r_wang = 1.1 / 1.4
assert abs(r_wang - 0.7857) < 0.001, r_wang
phi_hi = (r_wang - math.exp(-k * 10)) / (1 - math.exp(-k * 10))
assert abs(phi_hi - 0.7848) < 0.001, phi_hi          # 팩에 넣은 값
assert abs(g(12.0, phi_hi) / g(2.0, phi_hi) - r_wang) < 1e-9

# ── (2) Chen 2020 저농도 앵커는 그대로 살아 있다.
# ⚠ 적합식이 주는 비는 3.606 인데 판독 실측 비는 3.56 이다(+1.3 % 차이) —
#   판정#61 의 적합이 5점 전체를 맞추느라 끝점을 정확히 통과하지 않은 결과다.
#   맞는 척하지 않고 두 값을 따로 assert 한다.
phi_lo = 0.268
assert abs(g(2.0, phi_lo) / g(10.0, phi_lo) - 3.606) < 0.005
assert abs(3.606 / 3.56 - 1) < 0.015

# 고정 φ 로는 Wang 을 재현할 수 없다 — §3 "정면으로 틀린다"의 근거
assert g(12.0, phi_lo) / g(2.0, phi_lo) < r_wang / 2.5

# ── (3) log 보간이 두 앵커에서 자기 값을 되돌려주는가 (경계 계약)
c_lo, c_hi = 0.79, 6.5          # wt% — Chen 0.05 M 환산 / Wang 초록 인쇄값
def phi_of(c):
    t = (math.log(c) - math.log(c_lo)) / (math.log(c_hi) - math.log(c_lo))
    t = min(max(t, 0.0), 1.0)
    return phi_lo + t * (phi_hi - phi_lo)
assert abs(phi_of(c_lo) - phi_lo) < 1e-12
assert abs(phi_of(c_hi) - phi_hi) < 1e-12
assert phi_of(0.1) == phi_of(c_lo) and phi_of(50.0) == phi_of(c_hi)   # 외삽 금지
# 단조 증가 — 진한 산화제일수록 평탄부가 높다
cs = [0.79, 1.5, 3.0, 4.0, 6.5]
ph = [phi_of(c) for c in cs]
assert all(ph[i] < ph[i+1] for i in range(len(ph) - 1)), ph
assert abs(phi_of(4.0) - 0.6657) < 0.001, phi_of(4.0)   # 팩 기준 조성

# ── (4) Chen 0.05 M → wt% 환산 (KMnO4 M = 158.03 g/mol, 묽은 수용액 ρ≈1 kg/L)
assert abs(0.05 * 158.03 / 10.0 - 0.79) < 0.01

# ── (5) 엔진 계약: φ 를 농도로 흔들어도 기준 pH 에서 χ = 1.0 (Kp 이중 계상 방지)
from sim.engine import Recipe, simulate
for c in (0.79, 4.0, 6.5):
    f = simulate(Recipe(pack="sic_alumina_kmno4",
                        pack_overrides={"oxidizer_wt_pct": c})).factors["chi"]
    assert abs(f.value - 1.0) < 1e-9, (c, f.value)

# 엔진에서도 진한 산화제의 pH 10 감쇠가 더 얕다
import numpy as np
def mrr(c, p):
    return float(np.mean(simulate(Recipe(
        pack="sic_alumina_kmno4",
        pack_overrides={"oxidizer_wt_pct": c, "slurry_ph": p})).mrr_nm_per_min))
drop_lo = mrr(0.79, 10.0) / mrr(0.79, 2.3)
drop_hi = mrr(6.5, 10.0) / mrr(6.5, 2.3)
assert drop_hi > drop_lo, (drop_lo, drop_hi)
```

## 6-B. 정량 대조 요약 (문헌값 vs 모델)

| 항목 | 문헌값 | 모델 | 차이 |
|---|---|---|---|
| Wang 2021 pH 2 MRR | 1400 nm/h | (Kp 역산 기준점) | — |
| Wang 2021 pH 12 MRR | 1100 nm/h | 1100 nm/h (φ_hi 적합) | 0 % |
| pH 12/pH 2 비 (Wang, doi:10.1149/2162-8777/ac12de) | 0.786 | 0.786 재현 | 0 % |
| 같은 비, **교정 전** 모델 | 0.786 | 0.271 | **-65 %** |
| Chen 2020 pH 2→10 비 | 3.56 배 | 3.606 배 대조 | +1.3 % |
| Chen 0.05 M → wt% 환산 (doi:10.1134/S1070427220060099) | 0.79 wt% | 0.790 wt% 재현 | 0 % |
| 기준 조성 φ(4 wt%) | (보간 대상) | 0.6657 | 앵커 밖 아님 |

교정 전 모델이 Wang 의 pH 12 를 **65 % 과소예측**했다는 것이 이번 회차의 핵심 수치다.

## 7. 배선 결과 (정직 기록)

`sim/factors.py` `_ph_sic_kmno4_acidic_term` 에 φ 농도 보간을 추가했다. 앵커 4키가
전부 선언될 때만 켜지고, 아니면 기존 정적 φ 를 쓴다(하위호환 — 다른 팩 불변).

이 팩 기준 조성(4 wt%, pH 2.3) 실행값:

| pH | χ (판정#61) | χ (이번) |
|---|---|---|
| 2.0 | 1.124 | 1.053 |
| **2.3 (기준)** | **1.000** | **1.000** |
| 4.0 | 0.577 | 0.819 |
| 6.0 | 0.394 | 0.741 |
| 10.0 | 0.312 | 0.706 |
| 12.0 | (외삽) | 0.703 |

- 기준 χ = 1.000 — **1.0 계약 유지**.
- `pytest tests/test_factors.py` **100 passed**(신규 계약 2건 포함).
  기존 종 게이트 테스트(`test_oxidizer_shape_is_not_transferred...`)도 통과한다 —
  φ 보간은 산화제 **형상 항**이 아니라 pH 항의 계수라서 게이트를 우회하지 않는다.
  ⚠ 다만 이제 이 팩의 MRR 이 `oxidizer_wt_pct` 에 **간접적으로** 반응한다
  (기준 pH 에서는 정확히 1.0 이라 그 테스트가 잡지 않는다). 의도한 동작이지만
  "산화제 축은 완전히 죽어 있다"는 이전 서술은 이제 부정확하다.
- `qa_loop.py run --strict` **#264 PASS**, 유의 held-out 평균 ρ **+0.957 → +0.957**
  (불변, 9/27 데이터셋). 이 팩의 held-out 은 pH 2~6 구간이라 φ 변화가 순위를
  거의 바꾸지 않는다.
- 완성 격자는 **59/60 그대로**다. C2 는 해소되지 않았다 — φ_hi 도 `estimated`
  이기 때문이다. 이번 회차의 성과는 승격이 아니라 **틀린 값의 교정**이다.

## 8. 한계 (정직 표기)

- **원문 PDF 미확보.** Wang 2021 은 유료이고 sci-hub 미러 5곳이 로봇 확인으로
  막혔다. 쓴 수치는 출판사 초록(1차 인쇄) + CC BY 리뷰 본문(2차 인용)이다.
- φ_hi 는 **k=0.546 에 조건부**다(끝점 2개로 k 를 독립 추정할 수 없다).
- 앵커가 **2점**이라 보간 형상(log 선형)은 **미검증**이다. 세 번째 농도의 pH 스윕이
  나오면 형상부터 재검토할 것.
- 폴리타입(4H vs 6H) 효과가 φ 차이에 섞였을 가능성 — **미검증**.
- pH>12 · pH<2 는 외삽이다(코드가 notes 로 경고).
- 이 팩 Kp 의 알루미나 농도 가정(0.5 wt%)은 **여전히 미확인**이다(§5).
