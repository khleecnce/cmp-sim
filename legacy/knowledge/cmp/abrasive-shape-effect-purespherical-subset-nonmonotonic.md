<!-- V2-SECTION: R2-slurry | 신규 2026-09-10 | 정확도루프: RESPONSE_DEAD cu_h2o2_bta/입자크기(2회차 계속) | 정본: ARCHITECTURE-V2.md §3 -->
# 입자 형상 효과 문헌 확인 + TW202115224A 순수구형 부분집합 재검정 — cu_h2o2_bta 입경 RESPONSE_DEAD 재시도(5차)

> slurry-chemist Lv3-2 보강(계속) | 작성일: 2026-09-10
> 선행: [[particle-size-mrr-molecular-scale-bai2007]] (§7.5 QA FAIL로 Bai2007 D^-1.5 철회)
> [[abrasive-d99-alumina-fourth-attempt-guo-nanoalumina]] (같은 회차대 알루미나 D99 탐색 종결)
> 정확도루프 갭: RESPONSE_DEAD cu_h2o2_bta/입자 크기 — "문헌은 valley(n=18)인데 모델 무반응"

## 1. 이번 회차 가설과 결과 요약(먼저 결론)

Bai2007(§7.5)이 QA 루프에서 FAIL한 뒤 노트가 제안한 대안 "(a) 순수 구형만 골라 부분집합
회귀"를 이번 회차에 실제로 실행했다. **결과: 순수 구형 부분집합(n=6/압력)에서도 입경-MRR
상관은 거의 없다(Spearman ρ≈0.03~0.15, 유의하지 않음)** — 즉 §5에서 제안한 "형상효과 혼입"
가설이 완전한 설명이 아니었다. **이 팩터를 이번 회차에도 배선하지 않는다.**

## 2. 형상 효과 자체는 문헌상 실존한다(1차 확보 실패, 2차 인용으로 방향만 확인)

Eungchul Kim et al., "Shape classification of fumed silica abrasive and its effects on
chemical mechanical polishing," *Powder Technology* 381 (2021) 451-458.
DOI: 10.1016/j.powtec.2020.11.058. **원문 미확보** — Unpaywall `is_oa: false`(확인,
`api.unpaywall.org/v2/10.1016/j.powtec.2020.11.058` 응답), 미러 사이트/.se/.st/.box
전부 이번 회차 접속 시 캡차(altcha) 페이지만 반환해 자동 크롤링 불가(2026-09-10 실측,
이전 회차들의 성공 사례와 달리 이번엔 5개 미러 전부 인간 캡차 요구 — 미러 사이트 접근성이
매 회차 다르다는 것을 기록해둔다). **원문 미확보, 이하는 2차 인용**.

2차 인용원: RSC *J. Mater. Chem. C* 리뷰 "Recent advances in design and preparation of
abrasives for CMP"(pubs.rsc.org/tc/article/14/11/4248/1233451, 웹검색 스니펫으로만 확인,
전문 접근 실패)가 Kim et al. 2021을 인용하며 정량 수치를 명시: **"...decreasing the MRR
by 59%"** — 범프형(bumpy) fumed silica 입자가 구형(spherical) 콜로이달 실리카 대비
**같은 직경에서 MRR을 59% 낮춘다**는 서술. ScienceDirect 초록(sciencedirect.com/science/
article/pii/S0032591020311177, 초록만 확인)도 정성적으로 일치: "a bumpy spherical
abrasive in the fumed silica slurry had a shallower penetration depth but a higher removal
rate than those of colloidal silica" — 이 초록 서술은 **RSC 리뷰의 59% 감소 서술과
방향이 반대**로 읽힌다(초록: bumpy가 MRR 더 높음, 리뷰: bumpy가 MRR 59% 낮음). 두 2차
소스가 서로 모순되므로, **이 수치는 sim에 반영하지 않는다** — 원문을 못 읽은 상태에서
모순되는 2차 인용 중 하나를 임의로 채택하는 것은 규칙 위반(할루시네이션 방지 규칙2:
확인 못 했으면 확인 못 했다고 쓴다). "미검증 — 원문 미확보, 2차 인용 상호모순" 표기로
남긴다.

## 2.1 정량 재현(2차 인용 수치 자체의 오더만 확인, sim 반영과는 별개)

```python verify
# RSC 리뷰 2차 인용: 범프형(bumpy) vs 구형(spherical) 동일직경 MRR 비 = 1 - 0.59 = 0.41배
# (원문 미확보 — 이 블록은 "59%"라는 숫자 자체가 물리적으로 말이 되는 범위인지만 확인한다)
bumpy_over_spherical = 1 - 0.59  # = 0.41
assert 0.0 < bumpy_over_spherical < 1.0, "0~100% 감소 범위 밖이면 서술 자체가 모순"
print(f"RSC 리뷰 2차 인용: bumpy/spherical MRR 비 = {bumpy_over_spherical:.2f} "
      f"(원문 미확보, ScienceDirect 초록과 방향 모순 — sim 미반영)")
```

## 3. TW202115224A 순수 구형 부분집합 재정량(이번 회차 신규 분석)

문헌값 대조: 2.5psi 15nm 584.8 nm/min → 50nm 441.4 nm/min → 160nm 775.7 nm/min
(Versum Materials 2021 표2 — patents.google.com/patent/TW202115224A) —
입경 증가에 단조 감소도 증가도 아닌 밸리형 궤적을 보인다. 이 궤적이 단일 멱함수 지수로
근사되지 않음을 아래 Spearman 재현으로 검증한다.


`validation/datasets/tw202115224a_cu_abrasive_size_pressure.yaml`에서 형상 라벨이
"구형"인 배합만(15/27/50/160nm — 125/140nm은 "누에고치형"/"응집체"라 제외) 골라
압력별로 Spearman 상관을 재계산했다.

```python verify
from scipy.stats import spearmanr

# TW202115224A 순수 구형(spherical) 부분집합만: (size_nm, pressure_psi, mrr_nm_per_min)
data = [
    (15, 2.5, 620.4), (15, 1.5, 408.4),
    (15, 2.5, 549.2), (15, 1.5, 345.1),
    (27, 2.5, 514.0), (27, 1.5, 371.2),
    (27, 2.5, 562.9), (27, 1.5, 351.9),
    (50, 2.5, 441.4), (50, 1.5, 310.9),
    (160, 2.5, 775.7), (160, 1.5, 457.4),
]  # 출처: validation/datasets/tw202115224a_cu_abrasive_size_pressure.yaml (TW202115224A 표2)
   # 50nm은 "Nalco 50nm 구형" 배합5만(배합6 "Fuso 50nm 누에고치형"은 제외)

results = {}
for p in (2.5, 1.5):
    xs = [d[0] for d in data if d[1] == p]
    ys = [d[2] for d in data if d[1] == p]
    rho, pv = spearmanr(xs, ys)
    results[p] = (rho, pv, len(xs))
    print(f"P={p}psi: 순수구형 부분집합 n={len(xs)}, Spearman rho={rho:.3f}, p={pv:.3f}")

# 가설: 형상을 통제하면 입경-MRR 상관이 뚜렷해질 것(§5 Bai2007 노트의 제안)
# 실측: 둘 다 |rho| < 0.2, p > 0.7 — 유의한 상관 없음. 가설 기각.
for p, (rho, pv, n) in results.items():
    assert abs(rho) < 0.3, f"P={p}: 예상외로 강한 상관(|rho|={abs(rho):.2f}) — 재검토 필요"
    assert pv > 0.5, f"P={p}: 예상외로 유의(p={pv:.3f}) — 재검토 필요"
print("결론: 형상(구형)을 통제해도 15/27/50/160nm 구간에서 입경-MRR 유의상관 없음 "
      "— Bai2007 D^-1.5도, 단순 형상분리 가설도 이 팩(n=6/압력)으로는 지지되지 않는다.")
```

**해석(정직하게)**: n=6/압력이라는 표본 크기 자체가 valley 패턴(50nm 국소최저, 27nm과
160nm 양쪽에서 회복)을 통계적으로 구분하기엔 너무 작다. 15→27→50→160nm 관측값
(2.5psi 평균: 584.8→538.4→441.4→775.7)은 U자형(50nm에서 최저)처럼 보이지만, 순위상관
검정으로는 그 형태를 단조 멱함수(어떤 지수든)로 포착할 수 없다는 것이 이번 재현의
요지다 — **단조 지수 모델 자체가 이 데이터 형태와 구조적으로 안 맞는다**(밸리형은
멱함수가 아니라 최소 2차식 이상이 필요하나, n=4개 입경 수준으로는 2차식도 과적합
위험이 크다).

## 4. 결론 및 다음 단계

- **이 회차도 `abrasive_size_exponent`(또는 그 어떤 단조 멱함수형 팩터)를 cu_h2o2_bta에
  배선하지 않는다** — §3 재정량이 순수구형 부분집합에서도 단조 모델을 반박했다.
- 형상 효과(§2)는 문헌상 존재가 시사되나 **1차 원문 미확보 + 2차 인용 간 모순**이라
  현시점에서 sim에 넣을 수 없다. `abrasive_shape` 카테고리 팩터(구형/응집체/누에고치형
  이산 분류)를 도입하려면 Kim et al. 2021 원문 확보가 선행돼야 한다 — 다음 회차
  후보로 남긴다(미러 사이트 접근성이 회차마다 다르므로 재시도 가치 있음).
- **RESPONSE_DEAD 갭 판단**: 5차 연속(Bai2007 §7.5 FAIL 포함 시 2차) 시도가 모두
  이 데이터셋(n=18, valley 패턴)을 단조 함수로 설명하는 데 실패했다. 이 경로는
  `accuracy_gaps.py --skip`으로 다음 갭으로 넘기고, 근본 원인(밸리 패턴 자체가
  형상+입경 교락으로 단일 축 분해 불가능할 가능성)을 slurry-abrasive PROFILE.md에
  기록한다.

## 5. 미검증 사항

- Kim et al. 2021 원문 미확보 — §2의 59% 수치는 2차 인용이며 다른 2차 인용(초록)과
  방향이 모순돼 신뢰도 낮음. **sim에 미반영, 향후 원문 확보 시 재확인 필요**.
- TW202115224A의 형상 라벨("구형"/"누에고치형"/"응집체")은 특허 실시예 텍스트에
  의존 — 제조사(Nalco/Fuso/JGC) SEM 이미지 원본은 미확인, 특허 서술을 그대로 신뢰.
- n=6/압력은 통계적으로 매우 작은 표본 — "유의상관 없음"은 "상관이 없다"는 증명이
  아니라 "이 표본으로는 검출 못 함"이라는 약한 주장이다.

## 6. 자기시험

→ [[../../agents/slurry-chemist/EXAMS.md]] Lv3-2 보강 문항 참조(§9에 이어 3문항 추가 예정).
