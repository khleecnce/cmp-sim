<!-- V2-SECTION: R2-slurry | 정확도루프 2026-09-10 | 근거: 접촉역학, 입경 반응 | 정본: ARCHITECTURE-V2.md §3 -->
# 입경(abrasive size) → MRR: 힘분배+단층가정 모델의 "무반응(d^0)" 영점결과와 지수 미확정 근거

> slurry-chemist Lv2-2 확장 / process-integrator Lv3-2 관련.
> 정확도 루프 갭: RESPONSE_DEAD `cu_h2o2_bta/입자 크기` (2026-09-10, score 95).
> [[particle-wafer-interaction-mechanical-chemical-balance]] [[preston-luo-dornfeld-mrr]]
> [[abrasive-size-concentration-ph-K-additive-mrr-quantitative]] 상호링크.

## 1. 왜 이 노트가 필요한가
`sim/factors.py` `_f_kappa`의 입경 항은 **지수를 지어내지 않는다**(팩에 `abrasive_size_exponent`가
없으면 무반응). 정확도 루프가 이를 "실측이 변하는데 모델이 무반응"이라고 지적했다(RESPONSE_DEAD).
이 노트는 "왜 무반응이 코드 버그가 아니라 신중한 선택인가"를 **1차 이론 유도로 직접 검증**한다 —
서술이 아니라 계산으로.

## 2. 1차 출처
S. Chen (Iowa State Univ.), "A study on material detachment mechanism in CMP process" (PhD thesis,
2000s), Ch.4 "A Mechanical Model for MRR during CMP", §4.2.3(단층 입자밀도, Eq.4.2.14–4.2.18),
§4.9(MRR 모델, Eq.4.9.1–4.9.7). 무료 공개: https://dr.lib.iastate.edu/bitstreams/a946712d-5717-441d-87f7-61c66c27ca57/download
(2026-09-10 원문 PDF 직접 확보·전문 확인, escholarship 미러가 아닌 원본).
2차 데이터: TW202115224A 특허(Versum Materials, 2021 공개) 실시예1 표2 — 이미
`validation/datasets/tw202115224a_cu_abrasive_size_pressure.yaml`(n=18)에 등록됨.
Li et al. 2021 (doi:10.1149/2162-8777/ac3e44) — 이미 `abrasive-size-concentration-...md`에 등록됨.

## 3. Chen 단층모델 — 입경당 활성입자 면밀도

패드-웨이퍼 간극이 입자 한 겹(단층, thickness=d)이라 가정하면, 슬러리 부피 A_w·d 안에 담기는
입자 수 N은 입자 하나의 부피(∝d³)로 부피를 나눈 값이다(Eq.4.2.14–4.2.18, 원문 그대로):

```
N/A_w ∝ 1/d²   (단층 가정, 입자 부피 ∝ d³, 슬러리 박막두께 ∝ d로 상쇄되어 1개 차수 감소)
```

```python verify
# Chen thesis Eq.4.2.18 (단층가정 면밀도) 재현 — N/Aw ∝ 1/d^2
def areal_density(d, const=1.0):
    return const / d**2

d_small, d_mid, d_large = 15e-9, 50e-9, 160e-9  # TW202115224A 실시예 범위(15~160nm)
n_small = areal_density(d_small)
n_mid = areal_density(d_mid)
n_large = areal_density(d_large)

# 15nm→50nm: (50/15)^2 ≈ 11.1배 감소해야 함
ratio_small_to_mid = n_small / n_mid
assert abs(ratio_small_to_mid - (50/15)**2) < 1e-6, ratio_small_to_mid
# 15nm→160nm: (160/15)^2 ≈ 113.8배 감소해야 함
ratio_small_to_large = n_small / n_large
assert abs(ratio_small_to_large - (160/15)**2) < 1e-6, ratio_small_to_large
print(f"단층가정 면밀도비 15nm/50nm={ratio_small_to_mid:.2f}, 15nm/160nm={ratio_small_to_large:.2f}")
print("PASS: N/Aw ∝ 1/d^2 재현 (Chen thesis Eq.4.2.18)")
```

## 4. 힘분배 결합 — 왜 순진한 모델이 d⁰(무반응)을 예측하는가

명목압력 P(총 하중)가 고정되어 N개 활성입자에 균등 분배된다고 가정하면, 입자당 하중
F = P·A_w/N ∝ **d²**(N∝1/d²이므로). [[particle-wafer-interaction-mechanical-chemical-balance]] §4의
소성 압입 관계 δ_p = F/(2πR·H) (R∝d)를 쓰면:

```
δ_p ∝ F/R ∝ d²/d = d¹
A_f(입자당 제거단면) ∝ R^0.5 · δ_p^1.5 ∝ d^0.5 · d^1.5 = d²
MRR ∝ N · A_f ∝ (1/d²) · d² = d⁰   ← 입경에 무관!
```

```python verify
# 힘분배(F=P*Aw/N, N∝1/d^2) + 단일입자 소성압입(δ_p∝F/R, A_f∝R^0.5·δ_p^1.5) 결합 시
# MRR ∝ N * A_f 의 d-지수를 기호적으로(수치 대입으로) 확인한다.
def mrr_relative(d, P_const=1.0):
    R = d / 2.0
    N = 1.0 / d**2                      # Chen 단층 면밀도
    F = P_const / N                     # 힘분배: F ∝ d^2 (P*Aw 고정, Aw=1 정규화)
    delta_p = F / R                     # 소성압입 ∝ F/R
    A_f = R**0.5 * delta_p**1.5         # 제거단면 (particle-wafer-interaction 노트 §4)
    return N * A_f

vals = {d: mrr_relative(d) for d in (15e-9, 50e-9, 160e-9)}
# 세 크기 모두에서 비율이 1에 근접해야 한다(이론상 정확히 상수, d^0)
r1 = vals[50e-9] / vals[15e-9]
r2 = vals[160e-9] / vals[15e-9]
print(f"MRR(50nm)/MRR(15nm) = {r1:.6f}, MRR(160nm)/MRR(15nm) = {r2:.6f}")
assert abs(r1 - 1.0) < 1e-9 and abs(r2 - 1.0) < 1e-9, \
    "힘분배+단층+소성압입 결합모델은 이론상 정확히 d^0(무반응)이어야 한다"
print("PASS: 순진한 force-partition 모델 → MRR이 입경에 무관(d^0) — 1차 유도로 확인")
```

## 5. 실측과의 대조 — 부호조차 문헌 간 불일치

§4의 영점결과(d⁰)는 "1차 근사가 순진하다"는 뜻이지 "입경이 실제로 무관하다"는 뜻이 아니다.
실측 두 문헌을 대조하면:

- **Li et al. 2021**(oxide/실리카, doi:10.1149/2162-8777/ac3e44): 40→80→130nm에서 MRR이
  **80nm에서 정점**(peaked, 위로 볼록). 압입지배(소경) ↔ 표면적지배(대경) 전환으로 해석.
- **TW202115224A**(Cu, 특허 실시예1 표2, n=18): 15→27→50nm에서 MRR이 **감소**하다가
  50→125→160nm에서 다시 **증가**(valley, 아래로 볼록) — 정확히 반대 형태.

```python verify
# TW202115224A 2.5psi 조건 MRR 실측(특허 표2, Å/min→nm/min 환산치는 데이터셋 파일과 동일)
tw_mrr_2p5psi = {15: 620.4, 27: 514.0, 50: 441.4, 125: 761.8, 160: 775.7}  # nm/min
sizes = sorted(tw_mrr_2p5psi)
vals = [tw_mrr_2p5psi[s] for s in sizes]
min_idx = vals.index(min(vals))
# 최솟값이 양 끝이 아니라 중간(valley)에 있어야 함
assert 0 < min_idx < len(vals) - 1, "TW 데이터가 골(valley) 형태가 아니면 이 주장은 틀림"
assert sizes[min_idx] == 50, f"TW 데이터 최소점은 50nm이어야 함, 실제 {sizes[min_idx]}nm"
print(f"TW202115224A(Cu, 2.5psi): 최소 MRR={vals[min_idx]}nm/min @ {sizes[min_idx]}nm "
      f"— 15nm({vals[0]})과 160nm({vals[-1]}) 양끝보다 낮음 → valley 확인")

# Li 2021 정점형(40/80/130nm) 대비 정성 대조: 방향이 반대(peak vs valley)임을 명시
li2021_shape = "peak(80nm 최대)"
tw_shape = "valley(50nm 최소)"
assert li2021_shape.split("(")[0] != tw_shape.split("(")[0]
print(f"Li 2021(oxide)={li2021_shape} vs TW202115224A(Cu)={tw_shape} — 부호가 반대, "
      "재료계(oxide vs Cu)·화학(강산 콜로이달실리카 vs 중성 실리카+글리신+트리아졸)이 "
      "다르므로 같은 지수를 두 팩에 강제하면 한쪽은 반드시 틀린다.")
```

## 6. 결론 — κ의 입경 항을 여전히 미적용 상태로 둔다(코드 변경 없음, 근거 강화만)

1. §4의 1차 유도는 "평균 입경만으로 힘분배+단층+소성압입을 결합하면 정확히 d⁰"임을 **수치로
   확인**했다. 이는 우연이 아니라 지수들이 서로 상쇄되는 구조적 결과다(N∝d⁻², A_f∝d²).
2. 실측 방향 자체가 재료계마다 반대(§5) — Li 2021은 peak, TW202115224A는 valley. 이는 [[abrasive-size-concentration-ph-K-additive-mrr-quantitative]]가 이미 §8에서 지적한 "두 경쟁
   스케일링 모델(표면적 지배 vs 압입 지배) 중 어느 쪽이 우세한지는 재료·화학·조건 의존"이라는
   결론과 정합한다.
3. **따라서 `abrasive_size_exponent`에 단일 값을 팩 전역 기본값으로 넣는 것은 근거 없는 부호
   선택이다.** `sim/factors.py`의 현재 가드(지수가 팩에 명시될 때만 적용)는 유지가 옳다 —
   이 갭(RESPONSE_DEAD)은 "버그"가 아니라 "PSD tail 통계 없이는 풀 수 없는 정직한 미해결"임을
   이 노트가 이론+실측 양쪽에서 확인한 것이다.
4. **다음 단계 후보**(이 노트가 아닌 후속 단원 대상): Bulsara et al.(1997)의 "활성입자는 분포
   꼬리 <0.5%"라는 결과를 정량화하려면 입경 **분포**(PSD, 단일 대표값이 아니라 σ 포함)가
   필요하다 — 이는 현재 팩 스키마(`abrasive_size_nm` 스칼라)의 구조적 한계다. `abrasive_size_nm`을
   `abrasive_size_distribution`(평균+표준편차)으로 확장하는 것이 Lv3급 후속 과제로 남는다.

## 7. 한계/미검증
- §4 유도는 **탄성 Hertz 접촉이 아니라 소성 압입**(plowing) 가정 — 경질 산화막(탄성 지배)에는
  적용이 부적절할 수 있다([[particle-wafer-interaction-mechanical-chemical-balance]] §3 탄성/소성
  전이 참고). TW202115224A는 Cu(연질, 소성 타당)이므로 §4 유도의 적용 대상과 정합하나, Li 2021은
  oxide(경질)라 §4 유도가 직접 적용되지 않는다 — 이것이 두 문헌의 부호가 반대인 한 가지 설명
  후보다(미검증, 추정).
- Chen thesis의 N_in(교차점 밀도, Eq.4.2.10-4.13)은 기하학적으로 N에 대해 비선형(조합론적)일
  수 있어 §4의 N∝1/d² 단순화가 최종 MRR 지수를 정확히 상쇄시키는지는 Chen 자신의 최종
  MRR식(Eq.4.9.7, N_in·ω·b·V_m)에서 재확인이 필요 — 이 노트는 **1차 근사(면밀도×단일입자 체적)**
  만 재현했고, Chen의 완전한 교차모델(Eq.4.9.7)의 d-지수는 별도 검증 대상(미검증).
- 다운포스 순위(압력 반응)는 이미 이 데이터셋으로 검증되고 있다(`tw202115224a_cu_abrasive_size_pressure.yaml`
  자체 note에 명시) — 이 노트는 압력이 아니라 **입경 축만** 다룬다.

## 8. 자기시험
1. Chen thesis 단층모델이 예측하는 N/A_w의 d-지수는? → -2 (Eq.4.2.18, §3 재현).
2. 힘분배+단층+소성압입을 결합하면 MRR의 d-지수는 이론상 몇인가? 왜 그런가? → 0(d⁰),
   N∝d⁻²와 A_f∝d²가 정확히 상쇄되기 때문(§4).
3. Li et al. 2021(oxide)과 TW202115224A(Cu)의 입경-MRR 형태가 반대인 이유로 이 노트가 제시하는
   가설은? → 접촉모드 차이(탄성 vs 소성) — §4 유도는 소성 가정에서만 유효하므로 경질 oxide에는
   적용이 어긋날 수 있음(미검증 가설).
