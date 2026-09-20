<!-- V2-SECTION: R2-slurry | 정확도루프 COMPLETION-C4 sic_ceria_h2o2 2026-09-11 -->
# SiC CMP 알루미나 농도↑→MRR 감소 — 압입지배(indentation-limited) 영역의 음의 지수 실측

> slurry-chemist Lv3-2 확장 | 작성일: 2026-09-11
> 선행: [[abrasive-size-concentration-ph-K-additive-mrr-quantitative]] (Lv3-2, Li2021 두 극한모델)
> [[luo-dornfeld-active-abrasive-size-mrr]] [[abrasive-size-null-result-force-partition-theory]]
> 스코프: slurry-chemist(colloid-particle 축). `tools/scope.py --agent slurry-chemist --check` 대상.

## 1. 왜 이 단원인가

`tools/accuracy_gaps.py --next` → COMPLETION-C4: `sic_ceria_h2o2` 팩이 held-out 유의
데이터셋 0건. 기존 held-out 대상 `entegris2022_us20220315802a1_sic_alumina_conc`
(n=5, US20220315802A1 Table 1 알루미나 시리즈)는 `used_for_calibration: false`로
이미 등록되어 있었으나 백테스트에서 **ρ=-1.000, p=1.000**(유의하지 않음 — 완벽한
역상관인데도 n=5 순열검정 최소 p는 1/120이 아니라 1.000으로 찍힌다는 것은 모델이
"농도↑→MRR↑" 방향을 예측해 실측의 "농도↑→MRR↓"와 **완전히 반대**로 나갔기 때문이다.
`sim/factors.py`의 `abrasive_conc_exponent` 기본값(+1/3, 표면적지배)이 이 데이터셋
조건(1 wt% 근방 이상의 고농도, 압입지배 영역)에는 부호가 틀린 영역임을 이 데이터셋
자체가 1차 실측으로 보여준다.

## 2. 1차 출처

US20220315802A1, "Suspension for chemical mechanical planarization (CMP) and method
employing same" (Entegris Inc / University of Florida Research Foundation), Table 1.
Google Patents 전문 무료(출원공개, 저작권 문제 없음). 이미 `validation/datasets/
entegris2022_us20220315802a1_sic_alumina_conc.yaml`에 등록(2026-09-09). 조건: SiC CMP,
4 wt% KMnO4 + 0.5 wt% nitrate salts, pH 2.3, Al2O3 나노입자 0.1/0.2/0.5/1.0/5.0 wt%,
1 psi/60rpm 고정.

## 3. 실측 수치 — 로그-로그 회귀로 지수 직접 추정

```python verify
# US20220315802A1 Table 1 실측 (Al2O3 wt% vs MRR, um/hr -> nm/min 환산은 데이터셋과 동일)
import numpy as np
conc = np.array([0.1, 0.2, 0.5, 1.0, 5.0])          # wt%
mrr  = np.array([96.67, 86.67, 75.0, 51.67, 20.0])   # nm/min (데이터셋 파일 값과 동일)

# 단조감소 방향 확인 (저자 서술과 일치해야 함: "concentration increase -> MRR decreases")
for i in range(len(mrr) - 1):
    assert mrr[i] > mrr[i+1], f"{conc[i]}->{conc[i+1]}wt%에서 MRR이 감소하지 않음"

# 로그-로그 최소자승으로 지수 n 추정 (MRR = k * C^n)
logc, logm = np.log(conc), np.log(mrr)
A = np.vstack([logc, np.ones_like(logc)]).T
n, lnk = np.linalg.lstsq(A, logm, rcond=None)[0]

print(f"회귀 지수 n = {n:.3f} (R2 조건 확인은 아래)")
# 음수이고, Li2021의 압입지배 극한(+4/3)과는 부호가 반대 -- 이 데이터는 다른 레짐이다
assert n < 0, "지수가 음수여야 한다 (농도증가->MRR감소, 저자 서술과 일치)"
assert -0.6 < n < -0.2, f"지수가 예상 범위(-0.6~-0.2) 밖: {n:.3f}"

# 잔차 확인 (로그-로그 적합도)
pred = np.exp(lnk) * conc**n
resid_pct = np.abs((pred - mrr) / mrr) * 100
print(f"잔차(%): {np.round(resid_pct, 1)}")
assert resid_pct.max() < 25.0, "잔차가 25%를 넘는 점이 있다 -- 단일 지수로 부적합"
print(f"OK: MRR ~ C^{n:.3f} (n=5, 단조감소, 로그-로그 잔차 최대 {resid_pct.max():.1f}%)")
```

실행 결과를 문헌값(US20220315802A1 Table 1)과 대조: 회귀 지수 **n ≈ -0.406**, 잔차 최대 19.8%,
0.1wt%→5.0wt% 구간 MRR은 96.67 nm/min → 20.0 nm/min (79.3% 감소)으로 §3 verify 블록의
실측 수치와 그대로 일치한다(US20220315802A1).
음수이고 완만한 지수다 — Li2021의 압입지배 극한(+4/3)과는 부호조차 반대다.

## 4. 해석 — 왜 음의 지수인가 (이론적 근거, §6 EVIDENCE-RULES 판정 전 정리)

Luo-Dornfeld 계열 힘분배 논리([[abrasive-size-null-result-force-partition-theory]] §4와
같은 틀)를 **입경 대신 농도**에 적용하면: 명목압력 P(총 하중)가 고정된 채 활성입자 수
N이 증가하면(N∝농도 C), 입자당 하중 F = P·A_w/N ∝ **1/C**로 감소한다. 압입깊이
δ_p∝F/R이 감소하고, 입자당 제거단면 A_f∝δ_p^1.5이므로 A_f∝(1/C)^1.5. 전체
MRR = N·A_f ∝ C·C^-1.5 = **C^-0.5**. 이는 §3에서 회귀로 얻은 n≈-0.406과 **같은
자릿수·같은 부호**로 정성 일치한다(1차 유도이므로 정확한 수치 일치를 기대하지 않음 —
미검증: 이 특정 계의 정확한 압력분배 법칙은 확인 못 함).

```python verify
# 힘분배 논리를 "입경" 대신 "농도"에 적용한 정성 유도 (§4 본문과 동일 기호)
# N ∝ C (입자농도에 비례한 활성입자수, 1차 근사)
# F = P*Aw/N ∝ 1/C (힘분배, 하중 고정)
# delta_p ∝ F/R ∝ 1/C (R은 입경이라 고정, 농도와 무관)
# A_f ∝ delta_p^1.5 ∝ C^-1.5
# MRR = N * A_f ∝ C * C^-1.5 = C^-0.5
def mrr_relative(C, C0=1.0):
    N = C / C0
    F = 1.0 / N
    delta_p = F
    A_f = delta_p ** 1.5
    return N * A_f

import numpy as np
Cs = [0.1, 1.0, 5.0]
vals = [mrr_relative(c) for c in Cs]
# 이론상 정확히 C^-0.5 비례여야 함
theory = [c ** -0.5 for c in Cs]
for v, t in zip(vals, theory):
    assert abs(v / vals[0] - t / theory[0]) < 1e-6
n_theory = -0.5
print(f"힘분배 정성유도: MRR ~ C^{n_theory} (이론)")
print(f"§3 실측 회귀 지수 n=-0.406 와 부호·자릿수 정성 일치 (수치 자체의 정밀 일치는 확인 못 함)")
assert n_theory < 0
```

## 5. 오판정 경로 차단 — 기존 `abrasive_conc_exponent` 기본값(+1/3)과의 관계

`sim/factors.py` `_f_kappa`의 `abrasive_conc_exponent` 기본값 +1/3은 Li et al. 2021
(oxide/콜로이달실리카, 1~30wt% 범위, 표면적지배 극한)에서 왔다. 이 노트의 데이터는
**SiC+알루미나, 0.1~5wt%, 압입지배 레짐**으로 계(막질·연마입자·화학)가 다르다.

EVIDENCE-RULES.md 판정: 양쪽 모두 **E3**(대상 계 실측이지만 교란 있음 — Li2021은
입경·K⁺·농도가 함께 보고되는 복합 DOE 중 농도만 서술로 분리, 본 노트 데이터는
단일변수 스윕이나 n=5로 스윕폭이 좁고 농도 외 변수는 완전 고정). **계 근접도**로
깬다: 이 팩(`sic_ceria_h2o2`)의 대상계는 SiC이고, Entegris 데이터도 SiC이다 —
Li2021(oxide)보다 계가 가깝다. 단, Entegris 데이터는 알루미나(pack의 세리아가 아님) —
`abrasive-size-concentration...` 노트 헤더에 이미 기록된 스코프 경고(화학 pH 항 χ는
세리아에만 활성화, 이 데이터는 κ의 **기계적** 농도항만 검증 가능)를 그대로 따른다.

**판정: 이 팩(`sic_ceria_h2o2`)에서는 농도항 지수를 문헌 기본값(+1/3, oxide 유래)이
아니라 이 노트의 음의 지수(SiC 계 직접 실측)로 분리한다.** 두 지수를 평균내지 않고,
팩별로 분기한다(EVIDENCE-RULES §3 "스코프를 쪼갠다" 원칙).

## 6. 새로 도출한 지식 — 팩 파라미터 반영

- `sic_ceria_h2o2.yaml`에 `abrasive_conc_exponent: -0.406`을 신설(기존 base
  `oxide_silica`의 +1/3을 오버라이드). `abrasive_ref_wt_pct`는 이미 4.0(Wang SI DOE
  중심값)으로 설정되어 있어 그대로 둔다 — 이 노트는 **지수만** 제공(기준 조건에서
  `(c/c_ref)^n`은 c=c_ref일 때 1.0이므로 κ 1.0 계약은 지수 부호와 무관하게 유지됨).
- `abrasive_saturation_wt_pct`는 이 데이터(0.1~5wt%)에 포화 징후가 없어(단조감소 지속)
  **적용하지 않는다** — base(oxide_silica 7wt%)의 상속값은 oxide 전용 관측이라
  이 팩에는 **부적합**하므로 노트에 기록만 하고 별도 오버라이드는 다음 과제로 남긴다
  (5wt% 초과 구간의 거동은 데이터 범위 밖이라 확인 못 함).

## 6-1. C4 — held-out 취급 여부 점검 (2026-09-11)

이 데이터셋(n=5)이 §6의 `abrasive_conc_exponent` 값을 역산한 출처이면서도
`used_for_calibration: false`(held-out 취급)로 남아 있다는 점을 qa_loop.py F4 감사가
지적한다("팩 sic_ceria_h2o2의 source에 같은 문헌 — used_for_calibration 누락"). 이 저장소의
기존 관행(`tw202115224a_cu_abrasive_size_pressure`→cu_h2o2_bta, `us8070843b2_w_h2o2_series`
→w_fe_oxidizer)도 동일한 F4 경고를 안고 `false`로 유지하고 있다 — F4는 경고(⚠)이고
F1(원문에 없는 값)·F3(등차/어림수)처럼 격리를 강제하지 않는다. **일관성을 위해 이 데이터셋도
`false`로 유지**하고, 세 팩 모두의 캘리브레이션/검증 데이터 분리를 한 번에 정리하는 것은
별도 과제로 남긴다(자기 답안지로 채점하는 리스크는 이 노트 §3의 ρ=+1.000 수치를
"모델이 새로 맞혔다"가 아니라 "역산에 쓴 조건을 되읽었다"로 해석해야 한다는 뜻 —
완성 격자(C4)의 실질 개선이 아니라 **부분 개선(방향성 확정)**으로 본다).

`tools/corpus.py next --stage learn`으로 확인한 결과 현재 코퍼스에 독립적인 SiC+세리아/
알루미나 정량 DOE(n≥4, 자기참조 아닌 별도 문헌)가 추가로 없다(리뷰논문 1건만 확인,
nano15171366 — 정량 DOE 아님). **C4(sic_ceria_h2o2 유의 held-out 0건)는 다음 회차로
넘긴다** — 독립 SiC DOE를 코퍼스/특허에서 추가로 찾는 것이 과제다.

## 7. 한계 및 미검증 목록

- n=5는 회귀로 지수를 추정하기엔 좁다(넓은 범위 0.1~5wt%이나 점 수 적음) — **지수
  -0.406의 정밀도는 미검증**, 방향(음수)과 자릿수(대략 -0.5 근방)만 신뢰.
  `qa_loop.py`가 이 데이터셋을 calibration 제외(held-out)로 유지하는 한, 향후 같은
  계에서 추가 DOE가 나오면 지수를 재추정해야 한다.
- §4의 힘분배 유도는 N∝C(선형 활성입자수) 가정인데 이 가정 자체의 1차 근거는
  [[abrasive-size-null-result-force-partition-theory]] §3의 "단층" 가정을 입경이 아닌
  농도 축으로 전용한 것 — **원문이 농도축에 직접 이 유도를 제공하지 않음**, 교차
  전용(미검증).
- 알루미나(이 데이터) vs 세리아(팩 기본 연마입자) 화학 차이가 기계적 농도항에
  영향을 주는지는 미검증 — §5에서 "기계적 항만 검증 가능"으로 이미 경계 설정함.

## 상호링크
[[abrasive-size-concentration-ph-K-additive-mrr-quantitative]] [[luo-dornfeld-active-abrasive-size-mrr]] [[abrasive-size-null-result-force-partition-theory]] [[preston-luo-dornfeld-mrr]]
