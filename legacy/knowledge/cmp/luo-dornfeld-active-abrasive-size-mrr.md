<!-- V2-SECTION: R2-slurry | 정확도루프 RESPONSE_DEAD cu_h2o2_bta/입자크기 대응 -->
# 활성 입자 수·입경분포 → MRR 폐형식 (Luo-Dornfeld Part 1, 2003)

> slurry-chemist Lv3-2 보강 | 작성일: 2026-09-11
> 선행: [[particle-wafer-interaction-mechanical-chemical-balance]] (Lv2-2, 접촉역학 δ_p=F/(2πR·H))
> [[abrasive-size-concentration-ph-K-additive-mrr-quantitative]] (Lv3-2, Li2021 정점형 서술)
> [[preston-luo-dornfeld-mrr]] (계보)
> 스코프: slurry-chemist(colloid-particle 축) — `tools/scope.py --agent slurry-chemist --check` ✓ 허용.

## 1. 왜 이 단원인가

`tools/accuracy_gaps.py --next`가 RESPONSE_DEAD(score 95)로 지목: TW202115224A 데이터셋
(연마입자 종류 9종, 15~160nm, n=18)에서 실측은 같은 압력 안에서도 MRR이 최대 2배 갈리는데
(예: 2.5psi에서 620.4~849.3 nm/min), 모델은 abrasive_size_exponent가 팩에 없어 압력만
반응하고 입경축엔 완전히 무반응이다. Li2021(80nm 정점형) 노트는 이미 있지만 지수를
"문헌이 확정 못함"으로 두고 아예 항을 끈 상태였다 — 이번 단원은 **다른 1차 문헌**에서
지수 없이도 방향성을 낼 수 있는 폐형식을 찾아 부분 배선한다.

## 2. 1차 출처

J. Luo, D. A. Dornfeld, "Material Removal Regions in Chemical Mechanical Polishing: Coupling
Effects of Slurry Chemicals, Abrasive Size Distribution and Wafer-Pad Contact Area, Part 1",
UC SMART/NSF 후원 기술보고서, 2003(UC eScholarship 공개, 후에 IEEE Trans. Semicond. Manuf.
16(3), 469-476로 출판 — doi:10.1109/tsm.2003.815199, IEEE판은 유료/미러 사이트 미러도 Cloudflare
차단으로 미확보). **본 노트는 eScholarship 무료 전문(OA, Unpaywall 미인덱스지만 URL 직접
확인)을 직접 판독**: https://escholarship.org/uc/item/0n2575s1 (PDF:
`papers/luo-dornfeld-material-removal-regions-part1.pdf`, 21p, 실제로 열어 §"average size"
섹션 원문 확인 — 아래 인용은 OCR 아님, PyMuPDF 텍스트 추출 직접 대조).

## 3. 핵심 폐형식 (원문 Eq. 1-2)

저자는 [1-2](Luo-Dornfeld 2001, 접촉역학 원논문)의 모델을 확장해, 상부 연질 부동태층이
전면을 덮은 영역(Region 1, 저농도)에서:

```
MRR = k1 · C / Hw1^(3/2) · [(x_avg + 3σ)² / x_avg³] · P^(1/2)
```

- `x_avg`: 입자 평균 지름, `σ`: 입경분포 표준편차, `C`: 입자 중량농도, `Hw1`: 상부 연질층 경도, `P`: 압력.
- 저자 서술(원문 그대로, p.7): "note that if x_avg+3σ/σ in part 2 of Equation (1) is
  approximately constant, the portion of active abrasive number is almost independent of
  abrasive size distribution, which is the case for the experimental data from [3]
  (Bielmann et al. 1999) to be used in the second part of this paper."
  → 즉 **σ가 x_avg에 비례(CV 일정)하면 활성입자비 자체는 입경과 거의 무관**해지고, 괄호항
  `(x_avg+3σ)²/x_avg³`만 입경 의존성을 담당한다.

### σ=CV·x_avg 가정 시 형태

σ = k_cv · x_avg (일정 CV) 를 대입하면:

```
f(x_avg) = (x_avg + 3·k_cv·x_avg)² / x_avg³ = (1+3k_cv)² / x_avg
```

즉 **CV가 입경과 무관하게 일정하다면 이 항은 1/x_avg에 정확히 비례** — 단조 감소다.
이건 Li2021이 관측한 "80nm 정점형"과 다르다. 두 문헌이 서로 다른 물리 제약(Luo는
활성입자비 근사, Li는 압입/표면적 경쟁모델)을 쓰고 있어 **어느 쪽이 이 팩의 실측을
지배하는지는 이 노트 하나로 결정할 수 없다** — 미검증으로 남긴다.

```python verify
# Luo-Dornfeld 2003 Part 1, Eq.1-2 (papers/luo-dornfeld-material-removal-regions-part1.pdf, p.6-7)
# f(x_avg) = (x_avg+3*sigma)^2 / x_avg^3, sigma = k_cv * x_avg (원문 "if constant" 가정)
def f_size(x_avg, k_cv):
    sigma = k_cv * x_avg
    return (x_avg + 3*sigma)**2 / x_avg**3

# 원문 주장: CV 일정 가정 하에서 f_size ~ (1+3*k_cv)^2 / x_avg, 즉 1/x_avg에 정확히 비례
k_cv = 0.2
xs = [15.0, 27.0, 50.0, 125.0, 160.0]
vals = [f_size(x, k_cv) for x in xs]

# 닫힌형 예측과 수치 계산 일치 확인
closed_form = [(1+3*k_cv)**2 / x for x in xs]
for v, c in zip(vals, closed_form):
    assert abs(v - c) / c < 1e-9, "닫힌형 유도 오류"

# 단조 감소(원문 서술대로 CV 일정 시 활성입자비는 입경과 무관, 이 항만 1/x)
for i in range(len(vals)-1):
    assert vals[i] > vals[i+1], f"f_size가 {xs[i]}->{xs[i+1]}에서 단조감소가 아님"

print(f"k_cv={k_cv}: x_avg 15->160nm 사이 f_size 비율 = {vals[0]/vals[-1]:.2f}배 "
      f"(1/x_avg 비례이므로 이론값 {xs[-1]/xs[0]:.2f}와 일치해야 함)")
assert abs(vals[0]/vals[-1] - xs[-1]/xs[0]) < 1e-6
```

## 4. TW202115224A 데이터셋과의 대조 (부분 대조 — 정성만)

원문 폐형식을 "CV 일정" 가정으로 TW202115224A(2.5psi, 9종 입경)에 그대로 적용하면
1/x_avg 단조감소를 예측하지만, 실측(620.4→514.0→441.4→761.8→849.3 nm/min, 입경
15→27→50→125→160nm)은 **50nm 이후 오히려 증가**한다. 이는 다음 두 가지로 설명 가능하나
둘 다 이 문헌만으로는 확인 불가(미검증):
1. 실측 배합이 입경뿐 아니라 **입자 형상(구형→누에고치형→응집체)**도 함께 바뀐다
   (배합6부터 "누에고치형"·"응집체" — TW202115224A 원문 표1). Luo 모델은 구형 가정.
2. CV가 실제로는 입경에 비례하지 않을 수 있다(원문이 "if approximately constant"라고
   조건부로 서술 — 항상 성립한다고 주장하지 않음).

```python verify
# TW202115224A 실측(2.5psi 조건만, 특허 실시예 표2) vs Luo 1/x_avg 예측 형태 대조
xs = [15.0, 27.0, 50.0, 125.0, 160.0]
mrr_measured = [620.4, 514.0, 441.4, 761.8, 775.7]  # nm/min, 2.5psi

# Luo 1/x_avg 예측(정규화, 15nm 기준)
pred = [xs[0]/x for x in xs]
pred_scaled = [p * mrr_measured[0] for p in pred]

# 15->50nm 구간은 예측방향(감소) 일치
assert mrr_measured[2] < mrr_measured[0], "15->50nm 실측 감소 방향은 Luo 예측과 일치"
# 50->160nm 구간은 예측방향(계속감소)과 실측(오히려 증가)이 불일치 -> 모델 한계 확인
assert mrr_measured[4] > mrr_measured[2], "50->160nm 실측은 증가 - Luo 1/x 단조감소 예측과 불일치"
print("15->50nm: 방향 일치(감소). 50->160nm: 방향 불일치(Luo 예측 감소, 실측 증가)")
print("결론: Luo 폐형식은 이 데이터셋의 절반(저입경 구간)만 방향을 맞춘다 - 부분 모델")
```

## 5. 새로 도출한 지식 — 팩 파라미터로 옮길 것 / 옮기지 않을 것

- **옮긴다**: `abrasive_size_cv`(입경분포 CV, k_cv) 파라미터를 신설하면 `_f_kappa`에
  `(1+3·CV)²/x_avg` 형태의 폐형식 항을 **저입경 구간 한정 근사**로 추가할 수 있다.
  단, §4에서 확인했듯 50nm 이상에서는 방향이 깨지므로 **적용범위를 명시**해야 한다
  (예: `abrasive_size_valid_range_nm: [15, 50]` 같은 게이트).
- **옮기지 않는다**: 입경-형상 결합효과(구형 vs 응집체)는 이 문헌에 없다 — 문헌 없음으로
  남긴다. 지어내지 않는다.
- 구현요청은 §6에 남긴다(소프트웨어 부문이 backlog로 가져감 — 2026-09-05 지시대로
  직접 코딩하지 않음). 단, 이 단원의 "수식 Python 재현(sanity check)"은 §3-4의
  verify 블록으로 이미 수행했다(구현이 아니라 검증).

## 6. 구현 요청 (소프트웨어 부문 BACKLOG용)

- 무엇을: `sim/factors.py` `_f_kappa`에 `abrasive_size_cv` 파라미터가 팩에 있을 때
  `(1+3·CV)²/x_avg` 항을 추가하되, `abrasive_size_valid_range_nm`(기본 [0, 50]) 밖의
  `abrasive_size_nm`이면 이 항을 끄고 기존처럼 notes에 "⚠ Luo 폐형식 적용범위(≤50nm)
  밖 — 미적용"을 남긴다.
- 근거 노트: 본 노트 §3(폐형식 유도)·§4(적용범위 확인).
- 검증에 쓸 문헌값: TW202115224A 2.5psi 15/27/50nm 구간(620.4/514.0/441.4 nm/min) —
  ρ가 이 3점 한정으로는 음의 방향(단조감소)을 맞혀야 한다. 전체 9점 데이터셋의 ρ는
  형상효과가 섞여 있어 이 항 하나로 개선을 기대하지 않는다(§4 결론).
- 우선순위: 낮음 — 적용범위가 좁아(15-50nm) 이 갭(RESPONSE_DEAD 95점)을 완전히
  해소하지 못한다. 근본 해소에는 입자 형상 파라미터(별도 갭)가 필요.

## 7. 한계 및 미검증 목록

- IEEE 출판본(2003, doi:10.1109/tsm.2003.815199)은 미러 사이트 미러가 Cloudflare 챌린지로
  막혀 미확보 — UC eScholarship 기술보고서(같은 저자·같은 제목·NSF/SMART 후원 명시,
  동일 내용으로 추정)로 대체. **출판본과 100% 동일한지는 미검증.**
- σ=CV·x_avg 가정 자체가 원문의 "if approximately constant" 조건부 서술이지 항상
  성립하는 법칙이 아니다 — 미검증.
- 입자 형상(구형/누에고치형/응집체)이 MRR에 미치는 정량 효과는 이 문헌에 없음 —
  **문헌 없음**, 별도 조사 필요.
- TW202115224A 2.5psi 4번째 값(125nm, 761.8nm/min)은 Luo 예측(단조감소)과도 이미
  불일치하므로 §4는 15-50nm 구간만 한정해 서술했다 — 전체 9점 fit이 아니다.

## 상호링크
[[particle-wafer-interaction-mechanical-chemical-balance]] [[abrasive-size-concentration-ph-K-additive-mrr-quantitative]] [[preston-luo-dornfeld-mrr]] [[abrasive-size-null-result-force-partition-theory]]
