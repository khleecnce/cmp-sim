# κ 입자 형상(shape) 축 — 2차 인용 상호모순 재판정 + TW202115224A 형상 배수 실측

> Max워커 위임 | 작성일: 2026-09-19
> 선행: [[abrasive-shape-effect-purespherical-subset-nonmonotonic]] §2 (RSC 리뷰 vs
> ScienceDirect 초록 상호모순, 원문 미확보로 미반영 종결)
> EVIDENCE-RULES.md 판정#2 (같은 상호모순, "보류 — 원문 확보를 과제로 지정" 상태 → 이 노트가
> 판정#68로 갱신)

## 0. 결론 먼저

- Kim et al. 2021(Powder Technology, 원 논쟁의 당사자 논문) **원문 미확보 — 이번 회차도 실패**.
  경로 5종을 모두 도구로 직접 확인했다(§1).
- 대신 **TW202115224A(held-out 특허 데이터) 자체를 형상 축으로 재정량**했고(§2),
  **독립 1차 문헌 1편(ma15217525, 세리아/유리계, 로컬 전문 확보)** 이 같은 방향을 확인했다(§3).
- 판정: **"비구형(응집체/불규칙) 입자가 구형보다 MRR이 높다"** 쪽 채택. RSC 리뷰의 "59% 감소"는
  근거 서열에서 패배(§4).
- **배선하지 않는다.** 정밀한 배수(1.39배)의 유일한 출처가 held-out 데이터라서다(§5).

## 1. 원문 확보 시도 — Kim et al. 2021

Kim, Eungchul et al., "Shape classification of fumed silica abrasive and its effects on
chemical mechanical polishing," Powder Technology 381 (2021) 451-458,
DOI: 10.1016/j.powtec.2020.11.058.

도구로 직접 확인한 5개 경로, 전부 실패:

1. `tools/find_open_access.py --title "..."` → DOI만 매칭, OA 링크 없음(실행 결과 그대로).
2. OpenAlex API(`api.openalex.org/works/https://doi.org/10.1016/j.powtec.2020.11.058`) →
   `"is_oa": false, "oa_status": "closed", "any_repository_has_fulltext": false`.
3. Unpaywall API(`api.unpaywall.org/v2/...`) → `"is_oa": false, "oa_locations": []`.
4. Semantic Scholar Graph API → `"openAccessPdf": {"url": "", "status": null}`.
5. sci-hub 미러 3종(sci-hub.se 타임아웃, sci-hub.st 타임아웃, sci-hub.ru→sci-hub.kr 리다이렉트) —
   sci-hub.kr 은 altcha 로봇 확인 페이지만 반환(2026-09-10 이전 회차와 동일 증상 재현,
   `/tmp` 응답 크기 7363바이트로 동일한 캡차 페이지임을 확인). ⚠ sci-hub.wf 는 지시대로
   시도하지 않았다(3자 도메인 하이재킹 의심, 사용자 지시로 사용 금지).

저자 소속(Sungkyunkwan University, SK Group) 리포지토리(`pure.skku.edu`)도 WebFetch가
403을 반환해 접근 불가. **원문 미확보 — 정직하게 종결한다.**

## 2. TW202115224A 형상 배수 재현(호출자 실측치 독립 재계산)

`validation/datasets/tw202115224a_cu_abrasive_size_pressure.yaml` 표2(n=18)를 배합 라벨의
형상 표기("구형" vs "누에고치형"/"응집체")로 재분류하고, 압력별 평균으로 정규화한 뒤
Mann-Whitney U(단측, 구형 < 비구형)를 돌렸다. 아래는 **이 노트 작성자가 원본 YAML에서
직접 다시 계산한 값**이며, 호출자(Max워커)가 보고한 수치와 독립적으로 일치했다.

```python verify
from scipy.stats import mannwhitneyu, spearmanr
import numpy as np

# 출처: validation/datasets/tw202115224a_cu_abrasive_size_pressure.yaml
# (TW202115224A "Low dishing copper chemical mechanical planarization", Versum Materials,
#  실시예1 표2). 배합 라벨의 형상 표기를 그대로 옮겼다: "구형"=sph, "누에고치형"/"응집체"=비구형.
data = [
    (15, 2.5, 'sph', 620.4), (15, 1.5, 'sph', 408.4),
    (15, 2.5, 'sph', 549.2), (15, 1.5, 'sph', 345.1),
    (27, 2.5, 'sph', 514.0), (27, 1.5, 'sph', 371.2),
    (27, 2.5, 'sph', 562.9), (27, 1.5, 'sph', 351.9),
    (50, 2.5, 'sph', 441.4), (50, 1.5, 'sph', 310.9),
    (50, 2.5, 'cocoon', 845.3), (50, 1.5, 'cocoon', 569.5),
    (125, 2.5, 'cocoon', 761.8), (125, 1.5, 'cocoon', 487.4),
    (140, 2.5, 'agg', 849.3), (140, 1.5, 'agg', 482.4),
    (160, 2.5, 'sph', 775.7), (160, 1.5, 'sph', 457.4),
]

# 압력별 원시평균(정규화 전) — 호출자 보고치와 대조
for p, expect in ((2.5, (577.2666666666668, 818.7999999999998)),
                   (1.5, (374.15000000000003, 513.1))):
    sph = [d[3] for d in data if d[1] == p and d[2] == 'sph']
    non = [d[3] for d in data if d[1] == p and d[2] != 'sph']
    m_sph, m_non = np.mean(sph), np.mean(non)
    assert abs(m_sph - expect[0]) < 1e-6 and abs(m_non - expect[1]) < 1e-6, \
        f"P={p}: 재계산 {m_sph:.4f}/{m_non:.4f} != 보고치 {expect}"

ratio25 = 818.7999999999998 / 577.2666666666668
ratio15 = 513.1 / 374.15000000000003
assert abs(ratio25 - 1.418) < 0.001, ratio25
assert abs(ratio15 - 1.371) < 0.001, ratio15

# 압력별 평균으로 정규화 후 형상 이분류 Mann-Whitney(단측, 구형 < 비구형)
norm = []
for p in (2.5, 1.5):
    vals = [d[3] for d in data if d[1] == p]
    m = np.mean(vals)
    for d in data:
        if d[1] == p:
            norm.append((d[0], d[2], d[3] / m))

sph_n = [v for (_, shape, v) in norm if shape == 'sph']
non_n = [v for (_, shape, v) in norm if shape != 'sph']
u, pval = mannwhitneyu(sph_n, non_n, alternative='less')
assert abs(pval - 0.000377) < 0.00001, f"p={pval}"
assert abs((np.mean(non_n) / np.mean(sph_n)) - 1.3947) < 0.001

# 구형 내부: 입경-정규화MRR 상관 — 형상을 통제해도 입경 축은 여전히 null(판정#1 유지)
sph_sizes = [s for (s, shape, v) in norm if shape == 'sph']
sph_vals = [v for (s, shape, v) in norm if shape == 'sph']
rho, pv = spearmanr(sph_sizes, sph_vals)
assert abs(rho - 0.0873) < 0.001 and abs(pv - 0.7872) < 0.001, (rho, pv)

print(f"압력별 배수: 2.5psi={ratio25:.3f}배, 1.5psi={ratio15:.3f}배")
print(f"정규화 Mann-Whitney(구형<비구형, 단측): p={pval:.6f}, 배수={np.mean(non_n)/np.mean(sph_n):.4f}")
print(f"구형 내부 입경-MRR: rho={rho:.4f}, p={pv:.4f} (여전히 비유의 — 판정#1 null 유지)")
```

**같은 입경(50 nm)에서의 직접 대조**(형상만 다르고 입경이 우연히 일치하는 유일한 짝):
Nalco 50 nm 구형 2.5 psi = 441.4 nm/min vs Fuso 50 nm 누에고치형 2.5 psi = 845.3 nm/min →
**1.915배**. 이 한 쌍은 입경 교란이 없는 순수 형상 대조이며, 전체 배수(1.39배)보다도 크다 —
형상 효과가 입경 교란으로 부풀려진 착시가 아니라는 방향의 근거다(단 n=1 쌍이라 통계적
주장은 아니다).

## 3. 독립 1차 문헌 — ma15217525 (세리아/유리 CMP, 다른 계)

Kim et al. 2021을 못 구해 "동일 물음을 다루는 다른 1차 문헌"을 로컬 코퍼스
(`data/corpus/corpus.sqlite`)에서 찾았다. DOI 10.3390/ma15217525, *Materials* 15(21):7525
(2022), "The Effects of Precursors on the Morphology and Chemical Mechanical Polishing
Performance of Ceria-Based Abrasives" — gold OA(CC-BY), 로컬 전문 확보
(`data/corpus/fulltext/doi_10.3390_ma15217525.xml`, JATS XML, status=extracted).

이 논문은 전구체를 바꿔 세리아 연마입자를 세 형상(F=박편형/불규칙, S=방추형, N=구형에
가까움)으로 합성하고, TFT-LCD 유리 기판 CMP에서 슬러리 농도(0~9 wt%)를 스윕하며 MRR을
직접 실측했다(중력법). 본문 인용(원문 그대로, 필자가 XML을 직접 파싱해 확인):

> "The MRR of F-abrasives is higher, and the MRR of N-abrasives is lower at the same
> concentration than F-abrasives. **The shape of F-abrasives is irregular and angular, so
> the MRR is higher.** By contrast, the morphology and size of N-abrasives are more
> uniform, so the MRR of N-abrasives is lower than F-abrasives at the same concentration."

> "Although F-abrasives have a higher MRR (>500 nm/min), more scratches (Ra > 2 nm) are
> caused by their irregular morphology... N-abrasives obtained by N-precursors... achieves
> a high MRR (9 wt.%, 555 nm/min) but also reaches excellent polishing quality... including
> the lower Ra (<1.5 nm) and fewer scratches."

즉 **불규칙/각진(비구형) 형상이 구형보다 같은 조건에서 MRR이 높다**는 것이 이 논문 자신의
실측 결론이다. 정확한 F/S/N MRR 수치는 본문 표가 아니라 Figure 7b(그래프)에만 있고, 이
논문의 XML 전문에는 좌표 데이터가 없어(그림 이미지 자체를 로컬에서 확보하지 못함)
**정밀 배수는 미검증**으로 남긴다 — 확보한 것은 방향(비구형>구형)과 대략적 크기
(">500" vs "555", 즉 최소 배수는 1.0 미만에 가까울 수도 있어 TW202115224A의 1.39배와
직접 비교는 불가)뿐이다.

```python verify
# ma15217525 본문이 명시한 두 숫자만 오더 확인(정밀 배수 주장 아님 — 방향 확인용)
f_abrasive_mrr_min = 500.0   # "higher MRR (>500 nm/min)" — 하한값만 명시
n_abrasive_mrr_at_9wt = 555.0  # "9 wt.%, 555 nm/min"
# 본문 서술: 같은 농도에서 F(비구형) > N(구형). 9wt%에서 N=555면 F(같은 농도)는 555보다 커야
# 서술과 모순이 없다 — 이 부등식 하나만 기계적으로 확인한다(정밀 배수는 확인 못함, 유지).
assert f_abrasive_mrr_min <= n_abrasive_mrr_at_9wt, \
    "본문 서술(F가 같은 농도에서 N보다 높음)과 인용한 두 숫자가 모순되지 않는지 최소 확인"
print("ma15217525: F(비구형) > N(구형) 방향, 정밀 배수는 그래프 전용이라 확인 못함")
```

## 4. 근거 서열 판정 (EVIDENCE-RULES.md 형식)

| 근거 | 등급 | 방향 |
|---|---|---|
| RSC 리뷰(Kim2021 인용, 원문 미확보) | **E5** — 2차 인용, 원문 미확보 | 비구형 MRR **59% 감소** |
| ScienceDirect 초록(Kim2021 저자 본인 초록, 전문 미확보) | **E5** — 초록만 확인, 원문 미확보 | 비구형 MRR **증가**("shallower penetration... higher removal rate") |
| **TW202115224A(held-out) 형상 재분류** | **E3** — 대상계(Cu, 콜로이달실리카) 실측, 단 입경도 함께 변하는 교란 있음(§2) | 비구형 MRR **1.395배 증가**(정규화 Mann-Whitney p=0.000377) |
| ma15217525(세리아/유리, 로컬 전문 확보) | 타계 실측(대상계 아님, E1~E6 등급표는 "대상계" 전제라 직접 등급 매김 대상 아님) — 방향 corroboration | 비구형(불규칙) MRR **증가** (§3 원문 인용) |

**판정: E3(TW202115224A) 채택 — E5 두 건보다 등급이 높다(EVIDENCE-RULES §판정절차 1).**
방향은 "비구형이 구형보다 MRR이 높다"이며, 이는 ScienceDirect 초록(같은 방향)과 일치하고
RSC 리뷰의 "59% 감소"와 반대다. 다른 계(세리아/유리)의 직접 실측(ma15217525)이 같은
방향을 독립적으로 재현한다는 점이 이 판정의 강도를 더한다(EVIDENCE-RULES §판정절차 2-②
"독립 확인 수"에 해당하는 방식) — 단 등급표를 직접 적용한 것은 아니고 정성적 보강이다.

**RSC 리뷰의 59% 감소 수치는 폐기한다.** 이 리뷰도 Kim2021을 인용한 2차 소스이므로,
Kim2021 원문을 못 구한 상태에서는 "리뷰가 원문을 잘못 요약했다"고 단정할 근거는 없다 —
다만 대상계 실측(E3)과 타계 실측(corroboration)이 모두 반대 방향이므로, **판정 목적상은
이 수치를 채택하지 않는다**로 충분하다. Kim2021 원문이 확보되면 이 판정은 재검토 대상이다.

## 5. 배선 여부 — 배선하지 않는다

**결론: `abrasive_shape` 류의 키를 어느 팩에도 신설하지 않는다. 코드·YAML 미변경.**

이유:

1. **정밀 배수(1.39배)의 유일한 출처가 held-out 데이터**다.
   `validation/datasets/tw202115224a_cu_abrasive_size_pressure.yaml`의
   `used_for_calibration: false` 는 이미 `abrasive_size_exponent` 판정(#1)의 held-out
   검증용으로 지정돼 있다. 이 데이터에서 역산한 형상 배수를 `cu_h2o2_bta`에 박으면, 같은
   데이터셋이 계산한 ρ가 오르는 것은 **자기 답안지 채점**이지 검증이 아니다(과제 지시 §3의
   경고 그대로).
2. **독립(non-held-out) 1차 문헌은 방향만 주고 배수를 안 준다.** ma15217525(§3)는
   "비구형>구형"이라는 방향은 확실히 말하지만, 정밀 배수는 그래프(Figure 7b)에만 있고
   본문 텍스트로는 하한값(">500")과 한 점(555)만 나와 배수를 계산할 수 없다. 게다가
   대상계(Cu-H2O2-BTA-알루미나)가 아니라 세리아/유리계라 배수를 그대로 전이하는 것도
   근거가 약하다(E4급 전이조차 안 되는, 폐형식 유도가 아닌 그래프 판독 불가 상태).
3. **현재 어느 팩도 `abrasive_shape`(또는 동등 키)를 own 선언하지 않는다** —
   `grep -rn "abrasive_shape" knowledge/params/ sim/` 결과 `knowledge/params/*.yaml` 0건,
   `sim/` 중 유일한 히트는 `sim/web/studio3d.html:254`의 UI 드롭다운(`pk:null`, 엔진에
   연결 안 됨, "Recorded only... literature we hold gives direction... but no calibrated
   exponent"라고 **이미 스스로 적어 둔 죽은 필드**)뿐이다(2026-09-19 확인) — 이 노트의
   결론과 이 UI 주석이 우연히 일치한다. κ 계약상 팩이 own 선언하지 않은 축은 전 팩 스킵이
   정상이며, 그러면 MRR은 비트 단위로 불변이어야 한다 — 이는 새 축을 "추가하지 않을 때"의
   정상 상태이지, 결함이 아니다.
4. `_f_kappa`의 기존 철학(§0 배경, 입경 항 주석 "지수를 지어내지 않는다")과 일관되게,
   **배수를 알 방법이 없으면 배수를 지어내지 않는다**를 형상 축에도 그대로 적용했다.
   설계된 제약(축이 없으면 스킵)과 결함(있어야 할 축이 빠짐)을 가르는 기준은 "데이터가
   있는데 안 썼는가"인데, 여기는 **쓸 수 있는 대상계 데이터가 held-out 뿐**이라 설계된
   제약 쪽이다.
5. **더 나은 경로(과제 지시가 제안한 경로)는 여전히 막혀 있다** — Kim2021 원문 확보가
   선행돼야 "독립 배수로 배선 후 TW202115224A로 검증"이 가능해진다. 이번 회차는 그 경로가
   열리지 않았다.

`abrasive_size_exponent`의 기존 calibration_contact 항목(YAML 참조)은 건드리지 않았다 —
이 판정이 새로 침범한 계산 경로가 없기 때문이다.

## 6. 미검증 사항 (정직한 목록)

- Kim et al. 2021 원문 — **미확보**. RSC 리뷰의 59% 수치가 정확히 무엇을 비교한
  결과인지(입경 통제 여부, 통계량) 확인 못 했다.
- ma15217525의 정밀 F/S/N MRR 배수 — Figure 7b(그래프)만 있고 본문 텍스트/표에는 없어
  **미검증**(방향만 확인).
- Lee et al.(2015, DOI 10.1007/s12541-015-0334-4)/Lee et al.(2017, DOI
  10.1007/s12541-017-0158-5) — "비구형 콜로이달 실리카가 구형보다 RR이 높다"는 검색엔진
  AI 요약으로만 확인했고 원문(OpenAlex `is_oa: false`, ResearchGate "Request PDF"만 존재,
  sci-hub 동일 캡차)은 못 열었다 — **2차 인용(AI 요약) 수준, 판정에는 반영하지 않았다**.
  방향이 같다는 점만 참고 기록.
- TW202115224A 형상 라벨("구형"/"누에고치형"/"응집체")은 특허 실시예 텍스트 표기 그대로이며
  제조사 SEM 원본은 미확인(선행 노트 §5와 동일한 한계, 이번 회차도 재확인 못함).
- 같은 입경(50nm) 직접 대조(1.915배)는 n=1 쌍이라 통계적 주장이 아니라 정성적 방향
  보강용으로만 썼다.

## 7. 게이트 실행 기록

(아래 표는 이 노트 완성 직후 직접 실행해 채운다 — §게이트 참조)

## 8. 자기 점검

이 판정이 뒤집히려면: **확인 못한** Kim2021 원문이 확보되어 RSC 리뷰의 59%(§4, 미검증
수치)가 실제로 원문과 일치한다고 밝혀지거나, TW202115224A와 무관한 대상계(Cu-H2O2-BTA류)
1차 문헌이 반대 방향의 배수를 주는 경우다. 그 전까지는 §4의 판정과 §5의 미배선 결정을
유지한다.
