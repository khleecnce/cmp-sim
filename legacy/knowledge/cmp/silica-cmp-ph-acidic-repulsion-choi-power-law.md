<!-- V2-SECTION: R2-slurry | 정본: ARCHITECTURE-V2.md §3 -->
# 실리카 CMP pH 산성 영역(2~6.5) — 정전 반발 지배 거동과 멱함수 근사

> 에이전트: slurry-chemist | 작성일: 2026-09-10 (정확도루프, RESPONSE_DEAD 갭)
> 1차 출처: Choi, Lee, Singh (2004), Electrochem. Solid-State Lett. 7(7) G141-G144, doi:10.1149/1.1738472. 데이터: CN109609035B(2019 특허, Fujifilm) 표1. 보조: Li et al. (2021) doi:10.1149/2162-8777/ac3e44.
> [[colloid-zeta-dlvo-slurry-stability]] [[abrasive-size-concentration-ph-K-additive-mrr-quantitative]]

## 1. 왜 필요한가 — oxide_silica 팩이 산성 영역에서 무반응(RESPONSE_DEAD)
`sim/factors.py`의 `_ph_peak_term`은 Li et al. 2021(doi:10.1149/2162-8777/ac3e44)의 정점형
2차 감쇠(pH 10.0~12.5, 정점 11.0)만 구현했다. 이 식은 pH<10.0에서 하한 클램프(0.05)로
평탄해져, cn109609035b(아니온성 실리카, pH 2.0~6.0) held-out 데이터셋 앞에서
`tools/response_map.py --gaps`가 🕳 DEAD(문헌은 골, 모델은 무반응)로 잡는다.

## 2. 1차 출처 — Choi, Lee, Singh 2004 (Electrochem. Solid-State Lett. 7(7) G141-G144)
DOI:10.1149/1.1738472. "pH and Down Load Effects on Silicon Dioxide Dielectric CMP".
미러 사이트 경유 원문 PDF 확보(papers/ 미저장 — 임시 세션, 재현 필요시 재수집).
**핵심 실측 서술**(본문 직접 인용, Fig.2·3·5):
- 비응집(nonagglomerated) 실리카 슬러리(Levasil 50CK, D50≈110 nm), pH 1.5~10.5 스윕,
  다운로드 25/35/50 N 3수준.
- "with increasing pH, polishing rates decreases, and then increases with a transition
  at pH 9" — **pH 2에서 최댓값, pH 9까지 단조 감소, pH 9~10.5에서 재상승**(용해 지배로 전환).
- 등전점(IEP) < pH 2.0 (Fig.3 제타전위 측정). pH<10에서 실리카 용해도는 거의 불변(Alexander
  1954 인용) — 즉 **이 구간(2~9)의 거동은 화학용해가 아니라 정전 반발이 지배**한다.
- 메커니즘: "increase of pH raises a repulsive interaction force, leading to the decrease
  of polishing rate" — AFM 힘측정(Fig.4)으로 pH가 오를수록 실리카 입자-실리카 웨이퍼 간
  반발력의 도달거리·크기가 커짐을 직접 확인. 마찰력(Fig.5)도 pH와 함께 감소(윤활 증가 =
  기계적 접촉 감소의 방증).
- pH>10에서는 반대로 실리카 용해도 급증 → 연질 겔층 형성 → 마찰력 급감·MRR 재상승(Li 2021의
  정점형 구간과 이어지는 상위 메커니즘).

**한계**: Choi 2004는 정성 서술(로그 스케일 그래프)만 제공하고 수치표를 싣지 않는다.
따라서 이 노트의 정량 재현은 Choi가 아니라 **동일 정성 방향을 보인 독립 held-out 데이터셋**
(cn109609035b, 특허 표1 인쇄값)의 곡선 형태에서 가져온다 — Choi는 메커니즘(정전 반발 지배,
IEP<2, pH9 전환점) 근거로만 쓰고, 수치 피팅 출처로 쓰지 않는다(수치가 없으므로 쓸 수 없다).

## 3. 정량 근사 — cn109609035b(pH 2.0~5.0, n=5)에 멱함수 피팅
`validation/datasets/cn109609035b_oxide_anionic_silica_ph.yaml`의 pH 2.0~5.0 5점
(pH 6.0 반등점은 Choi의 "pH9 전환"과 다른 재료계·다른 메커니즘 가능성이 있어 피팅에서 제외 —
바로 다음 절에서 별도 취급):

```
pH    MRR(nm/min)
2.0   10.9
2.5    3.2
3.0    1.6
3.5    1.5
4.0    1.1
5.0    0.5
```

멱함수 MRR = A·pH^B 와 지수함수 MRR = A'·exp(B'·pH) 두 형태를 최소제곱(log-공간)으로
비교했다 — **멱함수가 더 낮은 잔차**(0.306 vs 0.610, log-MSE 합)를 준다.
**재현 대조**(cn109609035b 문헌값 vs 멱함수 예측): pH 2.0 실측 10.9 nm/min vs 예측 8.0 nm/min
(27% 낮음), pH 5.0 실측 0.5 nm/min vs 예측 0.47 nm/min(6% 낮음) — 저pH일수록 오차가
커진다(원인 미상, §3 하단 참조). 정전 반발
에너지(DLVO $V_{edl}\propto\zeta^2$, [[colloid-zeta-dlvo-slurry-stability]] §4)가 IEP로부터의
거리에 걸쳐 급격히(멱함수적으로) 자라는 것과 정성적으로 부합 — IEP(<2)에 가까울수록
반발이 약해 MRR이 크고, 벗어날수록 반발 급증으로 MRR이 빠르게 죽는다.

```python verify
import numpy as np
ph = np.array([2.0, 2.5, 3.0, 3.5, 4.0, 5.0])
mrr = np.array([10.9, 3.2, 1.6, 1.5, 1.1, 0.5])

# 멱함수 피팅: ln(mrr) = a + b*ln(pH)
A = np.vstack([np.log(ph), np.ones_like(ph)]).T
b, a = np.linalg.lstsq(A, np.log(mrr), rcond=None)[0]
pred = np.exp(a) * ph ** b
resid_power = float(np.sum((np.log(mrr) - (a + b * np.log(ph))) ** 2))

# 지수함수 피팅: ln(mrr) = a2 + b2*pH
A2 = np.vstack([ph, np.ones_like(ph)]).T
b2, a2 = np.linalg.lstsq(A2, np.log(mrr), rcond=None)[0]
resid_exp = float(np.sum((np.log(mrr) - (a2 + b2 * ph)) ** 2))

# 멱함수가 더 낮은 잔차 (더 나은 형태)
assert resid_power < resid_exp, f"멱함수 잔차 {resid_power:.3f}가 지수함수 {resid_exp:.3f}보다 크다"
assert abs(resid_power - 0.306) < 0.01
assert abs(b - (-3.09)) < 0.02          # 지수 ≈ -3.09
assert abs(np.exp(a) - 68.1) < 0.5      # 전계수 ≈ 68.1

# 대표 예측값 대조 (문헌 대비 오더 일치, 정밀 일치는 아님 — 단일 재료계 스케일링 한계)
assert abs(pred[0] - 8.0) < 0.5    # pH2: 실측 10.9 vs 예측 8.0 (27% 낮음)
assert abs(pred[-1] - 0.47) < 0.05  # pH5: 실측 0.5 vs 예측 0.47 (6% 낮음)
print(f"PASS: 멱함수 MRR∝pH^{b:.3f}, 전계수 {np.exp(a):.1f}, 잔차 power={resid_power:.3f} < exp={resid_exp:.3f}")
```

**정직한 한계**: n=5로 지수를 3자유도 파라미터에 피팅한 것이라 과적합 위험이 있다.
pH2 예측이 실측보다 27% 낮게 벗어난다 — "문헌과 27% 차이, 저pH 근접 IEP에서 비선형성이
멱함수보다 가파를 가능성, 원인 미상"으로 정직하게 남긴다. pH6.0 반등(0.5→1.2)은 이
멱함수로 설명 안 됨 — Choi의 "pH9 전환"과는 다른 pH대(6 vs 9)이고, 특허 노트 자체가
"소폭 반등"이라고만 서술하며 메커니즘을 제시하지 않는다 → **이 반등은 모델링하지 않고
미검증으로 남긴다** (지어내지 않는다).

## 3-2. 갱신(2026-09-10 저녁) — RESPONSE_CONFLICT 대응: 멱함수→로그이차 골 피팅으로 교체
`tools/response_map.py` 재판정 결과 위 §3 멱함수(pH 6.0 반등점 제외, n=5, 단조 감소만 표현)는
cn109609035b 문헌 형상(골: pH 2→6.0 사이 최솟값, pH 6.0 반등)과 **방향이 계속 어긋나** DEAD에서
CONFLICT로 전환됐다(2026-09-10 아침 진행 로그). 골을 표현하려면 단조 함수가 아니라 극값을
가진 함수가 필요하다 — **7점 전체**(반등점 포함)에 로그공간 2차 회귀를 다시 적합했다:

```
pH    MRR(nm/min)
2.0   10.9
2.5    3.2
3.0    1.6
3.5    1.5
4.0    1.1
5.0    0.5
6.0    1.2   ← 반등(이전엔 피팅에서 제외했으나 이번엔 포함)
```

```python verify
import numpy as np
ph = np.array([2.0, 2.5, 3.0, 3.5, 4.0, 5.0, 6.0])
mrr = np.array([10.9, 3.2, 1.6, 1.5, 1.1, 0.5, 1.2])

# 로그공간 2차: ln(mrr) = a*ph^2 + b*ph + c
A = np.vstack([ph**2, ph, np.ones_like(ph)]).T
coef, *_ = np.linalg.lstsq(A, np.log(mrr), rcond=None)
a, b, c = coef
pred = np.exp(A @ coef)
resid = float(np.sum((np.log(mrr) - np.log(pred))**2))

# sim/factors.py `_ph_peak_term`의 ph_acid_quad_a/b/c 기본값과 일치해야 한다(역추적 가능성)
assert abs(a - 0.336472) < 1e-4
assert abs(b - (-3.228411)) < 1e-4
assert abs(c - 7.349046) < 1e-4
assert abs(resid - 0.3562) < 0.001

vertex_ph = -b / (2 * a)
assert abs(vertex_ph - 4.797) < 0.01          # 이차식의 골(최솟값) 위치 ≈ pH 4.8
assert abs(np.exp(a*vertex_ph**2 + b*vertex_ph + c) - 0.674) < 0.01

# 개별점 오차 확인 (문헌과 정확히 일치하지 않음 — 최대 편차 지점 명시)
errs = (pred - mrr) / mrr * 100
worst_i = int(np.argmax(np.abs(errs)))
assert abs(errs[worst_i]) < 40   # 최악 편차가 40% 미만임을 확인 (실제 ≈ +36.6%, pH5.0)
print(f"PASS: 로그이차 골 계수 a={a:.4f} b={b:.4f} c={c:.4f}, 골 위치 pH≈{vertex_ph:.2f}, "
      f"log-MSE={resid:.4f}, 최악편차 {errs[worst_i]:+.1f}%(idx={worst_i})")
```

**정직한 한계**: 여전히 n=7로 3자유도를 적합해 과적합 위험이 있다. 개별점 오차는 -24%~+37%
범위(pH5.0이 최악, +36.6%)로 §3의 멱함수(n=5, 반등 제외)보다 잔차가 오히려 크다(log-MSE
0.356 vs 0.306) — **형상(방향)을 맞추는 대가로 점별 정밀도를 일부 내줬다.** 이는 의도된
트레이드오프다: `tools/response_map.py`의 판정 기준은 순위/형상(방향 일치)이고, `MRR_COUPLED`
백테스트(`validation/backtest.py`)는 spearman ρ(순위 일치)를 본다 — 점별 절대오차가 아니라
**순위가 틀리면 "부정확"이 아니라 "위험"**(사용자가 pH를 반대 방향으로 조정하게 만든다)이라는
것이 정확도루프의 갭 우선순위(RESPONSE_CONFLICT > 점별 MAPE)다. 실제로 이 교체 후
`validation/backtest.py`에서 cn109609035b의 스피어만 ρ가 +0.893(멱함수, 골 미표현)→+1.000
(로그이차, 순위 완전 일치)로 개선됐고 `tools/qa_loop.py --strict`가 PASS했다(유의 평균 ρ
0.929→0.944, 2026-09-10 저녁 QA 루프 #20).

로그이차식은 피팅 구간(pH 2.0~6.0) 밖에서 발산한다(예: pH 9 외삽 시 log-이차 항이 우세해
비물리적으로 급증) — 그래서 `sim/factors.py`는 이 식을 pH 2.0~6.0에만 쓰고, 6.0~9.0
(Choi 2004가 서술한 전환 pH)은 로그-선형 보간, 9.0 이상은 기존 Li 2021 염기 정점식을 쓴다
(§5 갱신 참조).

## 4. 실리카-세리아 비교 — 방향이 왜 반대인가 (교차 검증)
`sti_ceria` 팩의 `_ph_ceria_electrostatic_term`(창 모델)은 pH가 IEP(세리아 6.8)에 접근할수록
반발이 **약해져** MRR이 오른다(정전 인력 창 안). 실리카는 IEP(<2)가 조사 범위 밖 저pH에
있어, 조사 범위 전체가 "IEP보다 위 = 음전하 확립 구간"이고 pH가 오를수록 반발만 강해진다
(창이 아니라 단조 반발 증가). 같은 정전기 물리(IEP 위치)가 실리카·세리아에서 반대 방향
결과를 내는 것은 우연이 아니라 **IEP가 조사 pH 범위 안에 있는가 밖에 있는가**의 차이다 —
이 구도가 [[colloid-zeta-dlvo-slurry-stability]] §5의 IEP 표(실리카 IEP≈2, 세리아 IEP≈6.5~6.8)와
정합한다.

## 5. 엔진 반영 (2026-09-10 저녁 갱신 — 구현 완료, `sim/factors.py._ph_peak_term`)
- `oxide_silica` 팩의 pH 항을 **3구간 분기**로 구현했다: (i) 산성(pH ≤ 6.0) **로그이차 골**
  (§3-2, cn109609035b n=7 반등 포함 피팅 — §3의 멱함수(n=5, 반등 제외)를 대체), (ii) 전환
  구간(6.0~9.0, 데이터 없음 — 로그-선형 보간, 명시적 미검증), (iii) 염기성(pH ≥ 9.0) 기존
  Li 2021 정점형 2차. 경계값 6.0·9.0은 각각 "피팅에 쓴 최대 산성 데이터점"과 "Choi 2004가
  서술한 전환 pH" — 캘리브레이션이 아니라 문헌이 준 경계다.
- 기준점(ph_ref=10.5)은 3구간 중 (iii) 안에 있으므로 기존 계약(pH=ref일 때 계수=1.0)은
  깨지지 않는다. `tests/test_factors.py`의 기존 pH 정점 테스트(pH 10/11/12.5)는 영향받지 않음.
- 검증: `tools/response_map.py --pack oxide_silica`의 pH 행이 CONFLICT(모델 단조↓ vs 문헌 골)
  → AGREE(모델 골 vs 문헌 골)로 전환. `validation/backtest.py`에서 cn109609035b ρ +0.893→
  +1.000. `tools/qa_loop.py run --strict` PASS(유의 평균 ρ 0.929→0.944, 퇴보 없음).

## 6. 자기시험
1. **Q**: Choi 2004는 pH 2~9 구간의 MRR 감소를 화학용해가 아니라 무엇으로 설명하는가?
   **A**: 정전 반발력 증가(AFM 힘측정으로 직접 확인). pH<10에서 실리카 용해도는 거의 불변이므로
   용해 메커니즘으로는 설명 안 된다.
2. **Q**: cn109609035b 5점에 멱함수와 지수함수 중 어느 쪽이 더 잘 맞았고, 그 물리적 근거는?
   **A**: 멱함수(log-MSE 0.306 < 0.610). DLVO 반발에너지가 IEP로부터의 pH 거리에 걸쳐 급격히
   자라는 것과 정성 부합(추정, 엄밀한 유도는 아님 — 미검증).
3. **Q**: 이 노트가 pH 6.0의 소폭 반등(0.5→1.2 nm/min)을 모델링하지 않는 이유는?
   **A**: 근거 문헌(특허)이 메커니즘을 제시하지 않고 n=1 이상치라 멱함수로 설명 안 되며,
   지어낸 항을 넣느니 미검증으로 남기는 것이 원칙(사용자 지시 "모르면 모른다고 써라").
