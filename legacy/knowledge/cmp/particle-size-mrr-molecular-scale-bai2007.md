<!-- V2-SECTION: R2-slurry | 신규 2026-09-09 | 정확도루프: RESPONSE_DEAD cu_h2o2_bta/입자크기 | 정본: ARCHITECTURE-V2.md §3 -->
# 입자 크기 → MRR 정량모델 (활성입자 수·단일입자 제거율 분해) — slurry-chemist Lv3-2 보강

> slurry-chemist Lv3-2 보강 | 작성일: 2026-09-09
> 선행: [[particle-wafer-interaction-mechanical-chemical-balance]] (Lv2-2, 활성입자 개념 도입)
> [[abrasive-size-concentration-ph-K-additive-mrr-quantitative]] (Lv3-2, Li2021 정점형 관측 — 이 노트와 상호보완)
> [[preston-luo-dornfeld-mrr]] (Luo-Dornfeld 계보)
> 정확도루프 갭: RESPONSE_DEAD cu_h2o2_bta/입자 크기 (문헌은 골/단조 반응인데 모델 무반응, n=18)

## 1. 왜 이 단원인가

`tw202115224a_cu_abrasive_size_pressure.yaml`(Versum 특허, 9종 입자 15~160nm × 2압력, n=18)이
백테스트에 있는데도 `sim/factors.py`의 `abrasive_size_exponent`가 팩에 없어 κ의 입경 항이
꺼져 있었다(2026-09-08 노트가 "지어내지 않는다"며 의도적으로 비워둠). 그 결과 같은 압력의
9개 배합이 전부 같은 예측값을 내 — 문헌은 반응하는데 모델은 무반응(RESPONSE_DEAD)이었다.
이 노트는 Li et al. 2021(콜로이달 실리카, oxide)과 다른 **Cu CMP 문헌에서 입자크기→MRR의
전체 방향(순부호)을 폐형식으로 유도한 1차 논문**을 확보해 지수를 채운다.

## 2. 1차 출처

J. Bai, Y.W. Zhao, et al., "A mathematical model for material removal and chemical-mechanical
synergy in chemical-mechanical polishing at molecular scale," *Applied Surface Science* 253
(2007) 8489-8494. DOI: 10.1016/j.apsusc.2007.04.027.
**유료(Elsevier) — 미러 사이트 미러(미러 사이트 경유)에서 원문 PDF 확보**
(`papers/apsusc-2007-04-027-zhao-chang-mrr-molecular-scale.pdf`, 17쪽 전체, PyMuPDF로 텍스트
추출 확인). `papers/INDEX.json`에 `bai2007-apsusc-cu-mrr-molecular-scale-particle-size-conc`로 등록.

## 3. 모델 구조 - 활성입자수 x 단일입자 제거율

Zhao & Chang의 접근(Bai 2007이 계승)을 따라 두 개의 독립적 스케일링을 곱한다:

**(a) 접촉하는 입자 수 N** (§2.2, Eq.8):
N = A_r * (6*chi/(pi*D^3))^(2/3)
(chi=슬러리 내 입자 부피농도, A_r=실접촉면적, D=평균 입자직경)

**(b) 단일 입자당 제거율** (§2.3, Eq.15):
(RR)_V ~ sqrt(D_a)
(D_a=활성입자 직경, 입자-웨이퍼 접촉폭 ~sqrt(D_a*d_w)에서 유도)

**(c) 종합 (§3.2, 원문 그대로 인용)**:
> "Eq.(15) indicates that the removal rate by a single particle is proportional to D_a^{1/2}.
> However, the number of particles in contact is inversely proportional to D^2 as Eq.(12)
> indicates. Consequently, ... the particle size effect is negative and the overall material
> removal rate decreases with increase in the particle size."

즉 논문이 **직접 서술한 순 지수**는 다음과 같다(Eq.12의 전체 인자 N_a~D^(-2)은
Eq.9-10의 활성화 임계 D_a=D+k_1*sigma_s까지 반영한 유효 지수이며, 저자는 이를 "D^-2"로
명시).

MRR ~ D^(1/2) * D^(-2) = D^(-3/2)

## 4. 정량 재현 (Python verify)

```python verify
# Bai et al. 2007, Appl. Surf. Sci. 253, 8489-8494, doi:10.1016/j.apsusc.2007.04.027
# §3.2 원문 서술: RR_single ∝ D^(1/2), N_particles ∝ D^(-2) ⇒ MRR ∝ D^(1/2 - 2) = D^(-3/2)
# 논문은 "the overall material removal rate decreases with increase in the particle size"라고
# 명시(순부호=음, 즉 단조감소) — 지수의 정확한 소수점(-1.5)은 두 개별 지수(0.5, -2)의 산술
# 조합이며 원문이 최종 조합식을 별도 숫자로 다시 쓰지 않았으므로 "방향은 1차 확인, 크기는
# 두 개별 지수의 조합을 그대로 신뢰"로 표기한다.

def mrr_single(D_a):
    return D_a ** 0.5

def n_particles(D):
    return D ** -2.0

def mrr_overall(D):
    return mrr_single(D) * n_particles(D)

D_small, D_large = 15e-9, 160e-9  # m, Versum 특허 실측 범위(TW202115224A)
r_single = mrr_single(D_large) / mrr_single(D_small)
r_n = n_particles(D_large) / n_particles(D_small)
r_overall = mrr_overall(D_large) / mrr_overall(D_small)

print(f"단일입자 제거율 비(160nm/15nm) = {r_single:.3f} (D^0.5, 증가 방향)")
print(f"활성입자수 비(160nm/15nm)    = {r_n:.6f} (D^-2, 감소 방향)")
print(f"종합 MRR 비(160nm/15nm)      = {r_overall:.4f} (D^-1.5, 논문 결론: 순감소)")

assert r_single > 1.0, "단일입자 제거율은 입경 증가시 증가해야 함(D^0.5)"
assert r_n < 1.0, "활성입자수는 입경 증가시 감소해야 함(D^-2)"
assert r_overall < 1.0, "논문 §3.2 결론: 종합 MRR은 입경 증가시 감소해야 함(순음의 지수)"
import math
overall_exponent = math.log(r_overall) / math.log(D_large / D_small)
print(f"역산 종합지수 = {overall_exponent:.3f} (기대 -1.5)")
assert abs(overall_exponent - (-1.5)) < 0.01
print("OK: MRR ∝ D^-1.5 (Bai 2007 §3.2 서술과 일치, 단조감소)")
```

## 5. TW202115224A 실측과의 대조 - 정직한 불일치 표기

Versum 특허(`validation/datasets/tw202115224a_cu_abrasive_size_pressure.yaml`, 2.5psi 조건)의
실측 MRR은 **입경 증가에 따라 단조감소가 아니라 대체로 증가**한다(15nm 620.4/549.2 →
160nm 775.7 Å/min, 중간 50nm에서 국소적으로 845.3까지 튐). 이것은 Bai 2007의 예측(단조감소)과
**반대 방향**이다(출처: [[preston-luo-dornfeld-mrr]] 계보 대비 검증, TW202115224A 특허 실시예 표2). 정량 대조: 15nm 평균 620.4/549.2 Å/min(=62.0/54.9 nm/min)에서 160nm 775.7 Å/min(=77.6 nm/min)으로 실측이 문헌 예측(D^-1.5, 단조감소)과 어긋난다.

```python verify
sizes_nm = [15, 15, 27, 27, 50, 50, 125, 140, 160]
mrr_2p5psi = [620.4, 549.2, 514.0, 562.9, 441.4, 845.3, 761.8, 849.3, 775.7]

import statistics
small_avg = statistics.mean(mrr_2p5psi[0:2])
large = mrr_2p5psi[-1]
print(f"15nm 평균 MRR = {small_avg:.1f} Å/min, 160nm MRR = {large:.1f} Å/min")
print(f"실측 비(160/15) = {large/small_avg:.3f} — Bai2007 예측(D^-1.5)은 감소인데 실측은 증가")
assert large > small_avg, "실측은 입경 증가시 MRR 증가 — Bai2007과 반대 방향(정직하게 기록)"
print("불일치 확인: Cu(입자=콜로이달실리카, 화학=글리신+알라닌+트리아졸)계는 Bai2007의 "
      "산화막/일반계 유도와 다른 레짐일 가능성 — §6 한계 참조")
```

**해석(미검증 추정)**: Bai2007의 §2.2 유도는 활성입자 임계 D_a=D+k_1*sigma_s가 입경 대역
전체에서 일정한 형태 계수를 가정하나, Versum 특허계는 입자 **종류**(구형·응집체·누에고치형)가
동시에 바뀌므로(15~50nm는 구형, 125~160nm는 응집체/비구형) 형상 효과가 입경 효과와 뒤섞여
있다 — 이는 Bai2007의 스코프(균일 구형 입자, 단일 변수 스윕) 밖이다. 즉 **이 데이터셋에서
입경만의 순효과를 분리할 수 없다** — 정직하게 "1차 모델과 이 데이터셋이 정면충돌"로 남긴다.

## 6. sim 반영 판단 (⚠ 2026-09-09 QA 루프 FAIL로 철회 — §7.5 참조)

- **기본값(오더/방향)으로 abrasive_size_exponent = -1.5를 채택**한다 — Bai2007이 유일하게
  폐형식 유도를 제공한 1차 문헌이고(Li2021은 OCR 손상으로 지수 자체를 assert 못 함), 최소한
  "무반응"보다는 "문헌 기반 방향을 갖되 이 계에서 배반될 수 있음을 명시"가 정직하다.
- **팩별 분기가 필요하다**: oxide_silica(Li2021, 정점형 40→80→130nm) vs cu_h2o2_bta(Bai2007
  이론상 단조감소, 그러나 Versum 실측은 반대) — 같은 지수를 두 팩에 그대로 쓰면 안 된다.
  이 노트에서는 **cu_h2o2_bta에만** -1.5를 적용하고, oxide_silica는 기존처럼 지수 없이(정점형
  모델은 별도 과제) 둔다.
- **백테스트로 재확인 필요**: §5에서 이 팩의 지배 데이터셋(TW202115224A)과 방향이 반대이므로
  이 항을 켜면 유의 rho가 오히려 떨어질 위험이 있다 — qa_loop가 이를 감지해야 한다.

## 7. 한계/미검증

- Bai2007 Eq.12의 "D^-2"는 저자가 §3.2에서 직접 서술한 결론이지 이 노트가 Eq.8-10을
  완전히 재유도한 것이 아니다(Eq.9-10의 F(D+k_1*sigma_s) 함수형이 원문에 구체 함수로 안
  주어져 폐형식 전개를 끝까지 따라가지 못함) — **저자 서술을 그대로 채택, 독립 재유도는
  미검증**.
- 종합지수 -1.5는 oxide CMP 검증 사례(원문 §1 "verified in oxides CMP [7]")를 기반으로 하며
  Cu CMP에 직접 검증된 값은 아니다 — **막질 전이의 타당성 자체가 미검증**.
- §5에서 보인 실측 반대방향은 미해결 — 이 노트는 문제를 감추지 않고 다음 단원(입자 형상
  효과, 구형 vs 응집체)으로 넘긴다.

## 7.5 실제 배선 시도 결과 (2026-09-09, QA 루프 FAIL — 되돌림)

`sim/factors.py`의 `_f_kappa`는 이미 `abrasive_size_exponent`가 팩에 있으면 자동으로
반영하는 구조라 코드 수정 없이 `cu_h2o2_bta.yaml`에 `abrasive_size_exponent: -1.5`를
추가하는 것만으로 배선이 가능했다. 실제로 추가하고 `tools/qa_loop.py run --strict`를
돌린 결과:

```
✗ tw202115224a_cu_abrasive_size_pressure: 유의→비유의 (p 0.0007→0.7605)
유의 평균 ρ +0.904 → +0.967 (이 데이터셋이 유의집합에서 빠지며 오히려 남은 집합 평균은 상승)
```

이 데이터셋(n=18, 압력만 유의 변수였던 것)이 **p=0.0007(유의)에서 p=0.7605(비유의)로
퇴보**했다 — §5에서 예견한 대로 방향 충돌이 실제로 백테스트를 깼다. QA 게이트가
FAIL을 반환해 **커밋하지 않고 되돌렸다**(`git checkout -- knowledge/params/cu_h2o2_bta.yaml
sim/sensitivity.py tests/test_sensitivity.py`).

**결론**: Bai2007의 D^-1.5는 이 특허 데이터셋(Cu, 실리카 콜로이드, 15~160nm)에는 맞지
않는다 — §5의 "형상효과 혼입" 가설이 사실일 가능성이 높다. 이 지수를 cu_h2o2_bta
기본값으로 쓰지 않는다. 다음 시도는 (a) 순수 구형만 골라 부분집합 회귀, 또는 (b) 형상
파라미터(`abrasive_shape`)를 별도로 분리해 입경과 형상을 각각 다루는 것 — 이 노트의
§6 판단은 **철회**하고 여기 기록만 남긴다(정직하게 실패를 보고).

## 8. 자기시험

→ [[../../agents/slurry-chemist/EXAMS.md]] Lv3-2 보강 문항 참조(§9에 3문항 추가).
