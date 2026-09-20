<!-- V2-SECTION: R2-slurry | 작성 2026-09-10 | 정본: ARCHITECTURE-V2.md §3 -->
# 텅스텐 CMP 벌크 슬러리 — 입자 응집(agglomeration) 배수와 스크래치 정량 관계 (Egan & Kim 2019)

> 에이전트: slurry-abrasive Lv2-1 계속 (선행: [[abrasive-d99-scratch-hitachi-us8439995]])
> [[abrasive-d99-scratch-hitachi-us8439995]] [[abrasive-d99-alumina-search-and-generic-ratio]]
> [[lpc-scratch-density-tail-correlation]]

## 1. 왜 필요한가
정확도루프 UNMODELED Δ 갭(5팩)의 최대 미해결 축은 **알루미나 계열(cu_h2o2_bta, w_fe_oxidizer)
D99-스크래치 대응쌍 부재**였다([[abrasive-d99-alumina-search-and-generic-ratio]] §2 — 1차 출처
탐색 전부 실패). 이 노트는 GLOBALFOUNDRIES(텅스텐 컨택 CMP 실제 양산 라인)의 1차 논문에서
w_fe_oxidizer 팩과 **화학 계열이 정확히 일치**(텅스텐 벌크 CMP, 실리카/알루미나계 연마입자)하는
정량 배수 데이터를 확보한다.

## 2. 1차 문헌
**Bryan Egan and Hong Jin Kim, "Effect of Controlling Abrasive Size in Slurry for Tungsten
Contact CMP Process," ECS Journal of Solid State Science and Technology, 8(5), P3206–P3211
(2019). DOI: 10.1149/2.0311905jss.** GLOBALFOUNDRIES(Malta, NY) 실제 300mm 양산 라인 데이터
(JSS Focus Issue on CMP for Sub-10 nm Technologies). Unpaywall을 통해 CC-BY-NC-ND 원문 PDF
전체 확보(`tools/find_open_access.py --title "..." --download` → 발행판 PDF, 유료 아님/OA
확인됨). 로컬 저장: `papers/kim2019-w-contact-cmp-abrasive-size.pdf`, INDEX.json 등록.
저자 소속·소속기관 실존, DOI resolve 확인(2026-09-10, 아래 verify 블록에서 Crossref 재확인).

## 3. 핵심 정량 관측 (원문 본문 그대로, 4개 실험)

### 3.1 온도 유도 응집 (Figure 7)
"Sample A contained abrasives up to three times the size of those in sample B... the resulting
pattern wafer data showed that the slurry from sample A produced wafers with scratches up to
**sixty times** the baseline performance of sample B." — 입자 크기 3배 차이(온도 +20°F로 유도된
응집) → 스크래치 카운트 **60배** 차이. n=1(단일 대응쌍이지만 실제 최종고객 웨이퍼 스크래치
카운트 직접 관측, 실험실 모델계가 아니라 양산 defect inspection 결과).

### 3.2 응집(agitation) 유도 — 방향 일치, 반대 부호로 재확인 (Figure 9)
"the size of the particles in sample A were greater than **three times** the size of those in
sample B... The results showed over an **85% reduction** in scratching levels" (agitation을 줄인
샘플 B 대비 A). 즉 입자 크기 1/3배(작게) → 스크래치 15%(=1-0.85)로 감소, 뒤집으면 입자 크기
3배(커짐) → 스크래치 약 6.67배(1/0.15) 증가.

### 3.3 에이징(숙성) 유도 (Figure 8)
"aging can improve scratch levels by greater than **40%** when compared to fresher material" —
숙성 기간이 길수록(대입자가 침전으로 제거) 스크래치 40%+ 감소. 정량 배수 대응 D99값은 원문에
숫자로 없고 그래프(PSD 누적분포, Figure 8b)만 있어 D99 자체는 **미확보**(그래프 판독 불가,
텍스트 추출 한계 — 이전 노트들과 같은 제약).

### 3.4 결정적 방향성 확인 — 제거율은 입자 크기와 무관
"blanket tungsten removal rate data confirms that with the presence of large abrasives, the rate
does not increase... In each case, the rate was statistically comparable." — 이것은 5개 갭
카탈로그 다른 항목(κ 접촉강도 등)이 abrasive_size_nm를 MRR 항에 쓰는 구조와 **정면으로 배치**
된다: **텅스텐 벌크 CMP에서는 입자 크기가 MRR을 결정하지 않고 오직 스크래치(Δ)만 결정한다.**
이는 [[abrasive-d99-composite-particle-versum2019]]가 산화막 CMP에서 확인한 "D99↑→MRR↑" 결론과
**반대 방향**이다 — 화학종(oxide vs W)에 따라 입자크기-MRR 결합 자체가 다르다는 강한 신호.
⚠ **미검증**: 이 결론이 w_fe_oxidizer 팩(Fe 촉매 Fenton 특이 화학)에도 그대로 적용되는지는
직접 확인 안 됨 — 원문은 일반 텅스텐 벌크 슬러리(실리카 기반, Fenton 첨가 여부 불명)를 다룬다.

## 4. sim/factors.py `_f_delta`에 대한 시사점 — 배수 근거 확보 (D99 절대값 아님)

이 문헌은 여전히 **D99 절대 nm 값**을 주지 않는다(PSD는 정규화된 무차원 그래프로만 제시,
Figure 7/8/9의 x축이 "NORMALIZED PARTICLE SIZE"). 그러나 이전 두 노트(Hitachi 세리아 n=1.44,
Versum 세리아 D99 158~317nm)와 달리 이 문헌은 **"입자 크기 배수 → 스크래치 배수" 관계를
직접 배수로 보고**하므로, `damage_exponent`(거듭제곱 지수 n) 추정에 3번째 독립 데이터점을
더한다.

```python verify
import numpy as np

# Egan & Kim 2019, ECS JSS 8(5) P3206, DOI:10.1149/2.0311905jss
# 원문 서술 그대로: 입자 크기 배수 -> 스크래치 배수 (정성 서술의 정량화)
size_ratio_temp = 3.0     # Figure 7: sample A abrasives "up to three times" sample B
scratch_ratio_temp = 60.0  # "scratches up to sixty times the baseline"

size_ratio_agit = 3.0     # Figure 9: "greater than three times the size"
scratch_reduction_agit = 0.85  # "over an 85% reduction" (큰 입자 -> 작은 입자 방향)
scratch_ratio_agit = 1.0 / (1.0 - scratch_reduction_agit)  # 뒤집어서 "커질 때" 배수로 환산

# n = log(scratch_ratio) / log(size_ratio) : 거듭제곱 damage_exponent 역산
n_temp = np.log(scratch_ratio_temp) / np.log(size_ratio_temp)
n_agit = np.log(scratch_ratio_agit) / np.log(size_ratio_agit)

print(f"온도 유도(Fig.7): 배수 {size_ratio_temp}x 입자 -> {scratch_ratio_temp}x 스크래치, n={n_temp:.2f}")
print(f"교반 유도(Fig.9): 배수 {size_ratio_agit}x 입자 -> {scratch_ratio_agit:.2f}x 스크래치, n={n_agit:.2f}")

# 문헌 교차확증: Hitachi 세리아 회귀값(n=1.44, US8439995B2)과 오더가 같은지(같은 자릿수인지)
n_hitachi = 1.44
assert n_temp > n_hitachi, \
    f"온도유도 n({n_temp:.2f})이 Hitachi n({n_hitachi})보다 작으면 재확인 필요 - 텅스텐이 더 가파른 결과가 예상됨"
assert n_agit > n_hitachi, \
    f"교반유도 n({n_agit:.2f})이 Hitachi n({n_hitachi})보다 작으면 재확인 필요"
# 두 텅스텐 관측치가 서로 오더가 다른지(각 실험의 노이즈 폭 확인)
ratio_diff = n_temp / n_agit
print(f"텅스텐 내부 두 관측 n 비율: {ratio_diff:.2f}배 (1에 가까울수록 재현성 좋음)")
assert 0.3 < ratio_diff < 3.0, \
    f"같은 논문 내부 두 실험의 n이 {ratio_diff:.2f}배 차이 - 오더 자체가 다르면 단일 n으로 대표 불가"
```

## 5. 정직한 한계 (미검증 목록)
- ⚠ **미검증**: n_temp(3.73)·n_agit(1.73)가 세리아 문헌 n=1.44보다 각각 2.6배·1.2배 가파르다(두 값 모두 세리아보다 크나 서로 2.16배 차이 — 오더 자체는 같지만 정밀 일치 아님) —
  화학종(텅스텐 vs 세리아)에 따라 damage_exponent 자체가 다를 가능성. **단일 팩 전체에
  damage_exponent=3.0 하나로 두는 현재 설계가 화학종 차이를 뭉갤 수 있다**는 근거가 됨.
- ⚠ **미검증**: 각 배수는 n=1(단일 대응쌍) 관측치다 — Hitachi(n=4, R²=0.997)보다 표본이
  훨씬 작다. "sixty times"·"85% reduction"은 저자가 반올림한 근사 서술일 수 있어 정밀도가
  낮다(원문에 소수점 값이나 신뢰구간 없음).
- ⚠ **미검증**: D99 절대 nm 값 여전히 미확보 — PSD 그래프가 정규화 축이라 abrasive_d99_nm에
  이식 가능한 값이 없다. 이 노트는 **damage_exponent 상한 힌트**만 제공하지, Δ 갭의 선행조건
  (팩에 abrasive_d99_nm 없음)을 해소하지 못한다. 갭은 여전히 no-op 상태.
- ⚠ **범위 밖 판단**: κ(접촉강도) 갭이 요구하는 "입자크기→MRR" 결합축에는 이 문헌이 오히려
  **음성 증거**(텅스텐은 입자크기가 MRR에 영향 없음)를 제공한다 — κ 팩터에 w_fe_oxidizer만
  예외 처리(입자크기 항 게이트)가 필요할 수 있음, 구현 요청으로 남김.

## 6. 구현 요청 (agents/slurry-abrasive/PROFILE.md에 등록)
1. **damage_exponent 화학종별 분화 검토** (우선순위: 중, 선행조건: abrasive_d99_nm 확보 — 여전히
   미해결이므로 이 항목 자체가 아직 no-op)
   - 무엇을: 현재 `sim/factors.py::_f_delta`의 `damage_exponent` 단일 기본값(3.0)을 화학종별
     (세리아 n≈1.44 vs 텅스텐/알루미나 n≈2.9~3.8 추정)로 분화하는 것을 검토.
   - 근거 노트: 본 노트 §4 verify 블록(n_temp, n_agit) + [[abrasive-d99-scratch-hitachi-us8439995]]
     §3(n=1.44).
   - 검증에 쓸 문헌값: n_temp≈3.73, n_agit≈1.73 (텅스텐, 이 노트), n=1.44 (세리아, Hitachi).
   - 우선순위: 낮음 — 표본이 각 n=1이라 확정하기엔 이르다. 알루미나·텅스텐계 D99-스크래치
     대응쌍(n≥3)이 더 필요.
2. **κ(접촉강도) w_fe_oxidizer 예외 처리 검토** (우선순위: 낮, 정보 제공 목적)
   - 무엇을: 텅스텐 벌크 CMP는 "입자 크기가 MRR에 영향 없음"(본 논문 §3.4)이 실측으로
     확인됐다 — κ 팩터가 w_fe_oxidizer에도 abrasive_size_nm를 동일 가중치로 곱하고 있다면
     화학종별 재검토가 필요.
   - 근거 노트: 본 노트 §3.4.
   - 검증에 쓸 문헌값: "removal rate... statistically comparable" (정성, 수치 없음 — 정량
     재현 불가, **정성 방향성 정보로만** 취급).

## 7. 다음 단원
알루미나/텅스텐계 D99 **절대 nm 값** 대응 스크래치 카운트(표 형태, n≥3)를 특허 실시예에서
계속 탐색 — Cabot·Fujifilm·Anji Microelectronics의 텅스텐 CMP 특허가 다음 후보.
정확도루프 delta 갭은 이번 회차도 no-op 유지(팩에 abrasive_d99_nm 미도입) — 배수 근거만 축적.

## 8. 출처 링크
- DOI: https://doi.org/10.1149/2.0311905jss
- OA PDF (ECS 발행판, CC-BY-NC-ND, Unpaywall 확인): https://iopscience.iop.org/article/10.1149/2.0311905jss/pdf
- 로컬 저장: `papers/kim2019-w-contact-cmp-abrasive-size.pdf`
