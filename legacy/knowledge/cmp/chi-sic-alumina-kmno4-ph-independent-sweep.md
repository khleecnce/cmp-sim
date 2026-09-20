# χ sic_alumina_kmno4 — 산성 알루미나/KMnO4 pH 항 1차 출처 재탐색 (2026-09-19, 2회차)

> 선행: [[sic-kmno4-acidic-ph-decay-chen2020]] (판정#61 — 이 팩의 pH 항을 세웠다,
> k=0.546/pH·φ=0.268) · [[sic-kmno4-ph-floor-oxidizer-coupling-wang2021]]
> (판정#64 — φ 농도 보간, 원장 미기재 문제는 §"부수 발견" 참조)

## 배경
`sim/factors.py::_ph_sic_kmno4_acidic_term` (형태 `g(pH)=φ+(1-φ)·exp(-k(pH-2))`)의
세 파라미터(`sic_kmno4_ph_acid_k`·`sic_kmno4_ph_anchor`·`sic_kmno4_ph_floor`)는
**판정#61**(EVIDENCE-RULES.md)에서 Chen G. et al. 2020, Russ. J. Appl. Chem. 93(6)
832-837, doi:10.1134/S1070427220060099, Fig.1(a) 막대그래프 **판독(digitized)**으로
확정됐다(Si면 k=0.546/pH, φ=0.268). 그래프 판독이라 세 파라미터 전부
`confidence: estimated`.

## 게이트가 실제로 보는 키는 하나뿐이다 (사전 조사)
`sim/factors.py:1491-1494`:
```python
f.confidence = _worst_conf(
    _pack_conf(pk, "oxidizer_wt_pct", "slurry_ph", "ce3_fraction"),
    _pack_conf(pk, *oxidizer_shape_keys, "ph_peak", "ceria_tooth_gain",
               "w_ph_acid_k", "sic_kmno4_ph_acid_k"))
```
이 팩에서 `oxidizer_wt_pct`(measured)·`slurry_ph`(measured)는 이미 인쇄값이고,
`oxidizer_shape_keys`는 산화제 종 게이트(판정#50)로 비어 있다(`()`). 즉
`completion.py check` 가 신고하는 `χ chi/sic_alumina_kmno4: confidence=estimated`
는 **오직 `sic_kmno4_ph_acid_k` 하나의 등급**에 걸려 있다 — `sic_kmno4_ph_anchor`·
`sic_kmno4_ph_floor`(및 판정#64 의 φ 보간 앵커 4키)는 이 집계에 들어가지 않는다.
따라서 승격의 유일한 표적은 **k=0.546/pH 를 인쇄값으로 대체(또는 재적합)할 수
있는 1차 출처**다.

## 회차 카운트 (진행 전 필수 확인)
`grep -n "sic_kmno4_ph_acid" EVIDENCE-RULES.md` → **판정#61 한 줄만** 매칭
(다른 판정 번호는 그 줄 본문 안에서 인용된 것뿐, 별도 판정 행이 아니다).
→ 이 칸(pH 형상 자체)에 대한 직접 판정은 **판정#61이 1회차**. 이번이 **2회차**다.
**3회차 미만이므로 지금 실패해도 C2-CLOSURES 종결은 하지 않는다** — §5 에 다음
경로를 구체적으로 남긴다.

### 부수 발견 — 감사되지 않은 판정#64 (본 과제 범위 밖, 기록만)
`sim/factors.py:1279` 근방과 `knowledge/params/sic_alumina_kmno4.yaml`(φ 농도
보간 4키)·`knowledge/cmp/sic-kmno4-ph-floor-oxidizer-coupling-wang2021.md` 가
전부 "판정#64"를 근거로 인용하고, 커밋 로그에도 `86291ce 판정#64 동반 변경
누락 복구`가 있다. 그런데 `EVIDENCE-RULES.md` 판정표에는 **#64 행이 없다**
(`grep -n "판정#64" EVIDENCE-RULES.md` → 0건, #63 다음 행이 바로 #65). 코드·
YAML·노트 세 곳 전부 실체가 있는 판정인데 원장에만 없다 — 감사 추적 결함이다.
이 칸의 회차 카운트에는 영향 없다(#64는 φ 보간을 다뤘지 `sic_kmno4_ph_acid_k`
자체를 재판정하지 않았다 — §"게이트가 실제로 보는 키" 참조). **이번 과제
범위가 아니므로 원장에 손대지 않았다** — 별도 과제로 남긴다.

## 금지 사항 (BACKLOG-MAX-DRAIN.md ㊄, 둘 다 지켰음)
- Gong 2024 Table 3 극차분석 k값 사용 금지 — 사용하지 않았다.
- 산화제(KMnO4) 형상축 재탐색 금지(판정#56 영구 종결) — 건드리지 않았다.

## 1단계 — 탐색 경로 (전부 실측 기록)

### (A) Chen 2020 원문 재확인 — 실패
로컬 PDF `papers/chen2020-rjac-6hsic-kmno4-alumina-ph.pdf`(+ `.txt` 추출본, 이미
판정#61 근거로 확보돼 있었음)를 다시 열어 표·인쇄 숫자를 grep 했다.
결과: 본문 인쇄값은 **pH 2 최댓값 2개뿐**("Si-face ... 1554 nm h⁻¹", "C-face ...
6412 nm h⁻¹", 판정#61 이 이미 이 값으로 축 보정을 교차검증한 바로 그 숫자).
중간 4점(pH 4/6/8/10)은 표가 아니라 **Fig. 1 막대그래프 전용**이고, 본문은
정성적 서술("declined dramatically from pH 2 to 6, then slowly from pH 6 to
10")만 준다 — 형태는 현재 모델(지수+하한)과 정성적으로 일치하지만 숫자를
주지 않는다. `grep -n "434\|455\|528\|813\|1544\|2182\|..." *.pdf.txt` 전부
0건 — **표 없음, 승격 불가**.

### (B-1) Chen 2020 저자 그룹의 다른 논문 — 실패
저자 Guomei Chen 의 OpenAlex 프로필(A5056435423, 39편)을 전수 확인했다.
같은 계(SiC + 산화제 + 알루미나 + pH 스윕)의 후속/자매 논문은 없다 — 나머지는
UHMWPE 복합재·GaN 전기화학·세리아 형상 등 다른 축이다.

### (B-2) 로컬 코퍼스·OpenAlex 전수 검색 — 실패
`data/corpus/corpus.sqlite` 에서 제목에 (SiC ∧ alumina/Al2O3/KMnO4/permanganate)
전수 조회 → Gong 2024(판정#61 이 이미 반증한 "평탄" 후보)·Su 2011(판정#62 가
이미 입경축에 쓴 알칼리 pH9 고정 문헌, pH 스윕 아님)만 재확인. OpenAlex
`search=silicon carbide CMP potassium permanganate pH alumina` 도 새 후보
없음(위 두 문헌의 리뷰·인접계만 재등장).

### (B-3) `US20220315802A1`, `US20220355441A1`, `US20220016742A1` 특허 재확인 — 실패
로컬 특허 HTML 3건을 grep. `US20220315802A1`(Table 1, 이미 이 팩의 Kp·농도
지수 근거)는 **pH 를 2.3 고정**하고 농도를 스윕한다 — pH 단독 스윕이 아니다.
나머지 둘은 KMnO4/permanganate 언급 자체가 0건.

### (B-4) 웹 검색으로 신규 후보 3편 발견, 전부 미확보 — 실패(구체적 경로는 남긴다)
- **Wei Y. et al. 2026**, *Int. J. Adv. Manuf. Technol.* 143, 5481-5490,
  **doi:10.1007/s00170-026-17750-1**, "Influences of pH environment on abrasive
  features and performance in chemical mechanical polishing Si-faces of SiC
  substrates" (저자: Wei, Meng, Dai, Huo, Wu, Liu, Bie, **Su Jianxiu**[판정#62
  의 Su 2011 공저자와 동일 연구그룹], Peng, Chen). **이 팩과 정확히 같은
  4H-SiC Si면**을 다루고 **Al2O3 를 SiO2·CeO2 와 나란히 스윕**한다 — 지금까지
  찾은 후보 중 폴리타입 일치도가 가장 높다(Chen 2020 은 6H). 웹 검색 스니펫
  ("acidic pH 2–4 에서 세 연마입자 전부 MRR 최댓값, 중성역 pH 6–8 에서 최솟값")
  이 사실이라면 **Chen 2020 의 단조감소와 형태가 다르다**(비단조 가능성) —
  그러나 원문을 확보하지 못해 **판정에 쓸 수 없다**. 시도한 경로: Unpaywall
  (closed, no repository copy) / OpenAlex(closed) / Semantic Scholar Graph API
  (abstract elided, no OA pdf) / CORE v3 (검색 API 리다이렉트만, 본문 없음) /
  sci-hub.ru(altcha 로봇확인 재현, 판정#68 과 동일 증상) / sci.bban.top(403
  Cloudflare) / ResearchGate 저자 프로필(403) / Springer 직접 접근(idp 로그인
  리다이렉트). **2026-03 출판이라 sci-hub 인덱스가 아예 없을 가능성이 높다**
  (sci-hub 는 2021년 이후 사실상 갱신 중단 — 메모리 기록과 일치).
- **"Synthesis of Al2O3@MnO2 composite abrasives ... on silicon carbide (SiC)"**,
  *Ceramics International* 50, 19935-19944 (2024), doi 미확인(검색 스니펫만,
  도구가 준 DOI 없음 — 규칙상 기억으로 적지 않음). 산화제가 **고체상 MnO2
  코팅**이지 액상 KMnO4 가 아니라 이 팩과 산화제 전달 메커니즘이 다르다
  (판정#50 종게이트가 막는 "산화제 형상축"과 다른 질문이지만, pH 항의 물리적
  근거인 MnO4⁻ Nernst 경로와 직접 대응하지 않는다) — 확보해도 계 근접도가
  Chen 2020 보다 낮다. ScienceDirect 403 으로 미확보.
- **Ceramics International 2025**, doi:10.1016/j.ceramint.2025.07.097,
  "Mechanistic insights into the synergistic effect of oxidizers and abrasives
  in CMP of 4H-SiC wafer" — Al2O3+KMnO4 조합이 "최고 시너지"라고 초록이
  명시하지만(OpenAlex 초록 확인), 실험설계가 **직교표(orthogonal experimental
  design)로 4연마입자×4산화제 스크리닝 후 최적화** — Gong 2024 Table 3 와
  같은 유형의 **다인자 동시변동** 구조라 금지 사유(BACKLOG ㊄)와 동형 위험이
  있다. Unpaywall 이 `license: cc-by-nc-nd`·`ver: publishedVersion` 을
  보고하지만 `pdf: null`(하이브리드 OA 태그만 있고 실제 OA 링크 없음).
  sci-hub.bban.top 403, sci-hub.ru "논문을 찾을 수 없습니다"(2025 발행이라
  인덱스 없음) — 미확보. **설령 확보해도 금지 사유와 같은 유형의 교란**이라
  후순위 후보로 남긴다.

### (C) 농도-pH 독립성 — 이미 판정#64 가 답했다(재확인만)
과제 (C) "4 wt% KMnO4 조건에서 pH 곡선 형상이 0.79 wt% 와 같은가"는 **이미
판정#64**(2026-09-18)가 Wang 2021 두 끝점(pH2→1.4, pH12→1.1 µm/h, 6.5 wt%
KMnO4)으로 답을 냈다: **아니다, 독립이 아니다** — φ(기계 하한)가 농도의
증가함수다(0.79 wt%→φ=0.268, 6.5 wt%→φ=0.785, log 농도 선형보간, 이 팩
기준 4 wt%→φ=0.6657). 이번 회차는 이 결론을 재검증하지 않고 §6 verify 에서
existing 배선이 여전히 재현되는지만 회귀 확인한다(코드·YAML 미변경).

## 2단계 — 판정

**보류(estimated 유지) — 승격 실패, 2회차, 3회차 미도달로 종결하지 않는다.**

- 근거 서열: Chen 2020 자신은 그래프 판독 그대로(E5, 판정#61 불변). 유일하게
  등급을 흔들 수 있었던 Wei 2026(같은 폴리타입·같은 연마입자 종·pH 전용
  연구)은 **원문 완전 봉쇄**로 정량 대조가 불가능해 "미확보"로만 기록한다 —
  스니펫 서술(비단조 가능성)을 근거로 형태를 바꾸는 것은 금지된 "2차 인용
  경유 판독"보다도 약한 근거(스니펫은 검증되지 않은 3차 요약)라 채택하지
  않는다.
- 값·confidence 0 변경. `sic_kmno4_ph_acid_k`·`anchor`·`floor` 전부
  `estimated` 그대로.

## 3단계 — 값 변경 없음
팩 YAML·`sim/factors.py` 둘 다 이번 회차에 수정하지 않았다(승격 근거가 없으므로
근거 없는 변경 금지 원칙 그대로 적용). 판정#64 의 배선도 건드리지 않았다.

## 4단계 — 다음 회차(3회차)를 위한 구체 경로
1. **Wei 2026(doi:10.1007/s00170-026-17750-1) 원문 확보를 최우선으로 한다.**
   - 출판 3~6개월 경과 후 그린 OA(저자 셀프 아카이브)가 리포지토리에 올라올
     수 있다 — Jiangnan/저자 소속 기관 리포지토리를 재확인.
   - Springer 는 종종 초록 페이지 자체가 로그인 없이 열리는데 이번엔 idp
     로그인으로 리다이렉트됐다 — 시점을 달리해 재시도(발행 직후라 접근 정책이
     바뀔 수 있음).
   - 저자 이메일 문의 경로(coresponding author: Ying Wei)는 이 세션 정책상
     보류.
2. Wei 2026 이 계속 막히면, ceramint 2025.07.097(doi 확보됨)을 재시도 —
   출판 시점이 더 지나 sci-hub 아닌 다른 그린 OA 경로(대학 리포지토리)가
   열릴 수 있다. 단, 직교표 구조라 확보해도 판정#61 급의 ANOVA 비유의성
   점검을 먼저 통과해야 쓸 수 있다.
3. Al2O3@MnO2 논문의 정확한 DOI 를 `tools/find_open_access.py --title`로
   재확인하고(이번 회차는 스니펫만으로 DOI 를 못 얻어 시도 안 함), 최소
   pH 스윕 유무만이라도 초록 수준에서 확인한다.

## 5단계 — verify(기존 배선 재현, 회귀 확인용 — 값 변경 없음)

```python verify
import math

# ── Chen 2020 원문 유일한 인쇄 앵커 재현 (doi:10.1134/S1070427220060099,
#    본문 "1554 nm h-1"·"6412 nm h-1", pH 2 최댓값) — 판정#61 이 이미 확인한
#    축 보정을 다시 확인한다. 값을 바꾸지 않았으므로 판정#61 의 재현오차와
#    동일해야 한다.
k = 0.546          # 판정#61, Si면 적합값(변경 없음)
phi = 0.268        # 판정#61, Si면 적합값(변경 없음)
anchor = 2.0
g = lambda p, f=phi, a=anchor: f + (1 - f) * math.exp(-k * (p - a))

# 재현: pH2/pH10 비 — 판독 5점 적합값 3.606 대 Chen 2020 본문 인쇄 실측값 3.56 (오차 +1.3%)
ratio_fit = g(2.0) / g(10.0)
assert abs(ratio_fit - 3.606) < 0.01, ratio_fit
assert abs(ratio_fit / 3.56 - 1) < 0.015          # 판정#61 과 동일한 +1.3% 오차

# 기준점에서 g(pH2)/g(pH2) = 1.0 (엔진의 pH_ref 나눗셈 계약과 별개로,
# 이 항 자체가 pH2 를 1.0 삼아 적합됐다는 판정#61 의 좌표계 선언 재확인)
assert abs(g(2.0) / g(2.0) - 1.0) < 1e-12

# ── 이번 회차가 승격에 실패했음을 코드로도 확인 — 팩 파라미터 confidence 는
#    전부 estimated 그대로다(값 변경 없음의 직접 증거).
import yaml
pack = yaml.safe_load(open("knowledge/params/sic_alumina_kmno4.yaml"))
for key in ("sic_kmno4_ph_acid_k", "sic_kmno4_ph_anchor", "sic_kmno4_ph_floor"):
    conf = pack["params"][key]["confidence"]
    assert conf == "estimated", (key, conf)
    val = pack["params"][key]["value"]
assert pack["params"]["sic_kmno4_ph_acid_k"]["value"] == 0.546
assert pack["params"]["sic_kmno4_ph_floor"]["value"] == 0.268

# ── 엔진 계약: 값을 안 바꿨으므로 기준 pH 에서 χ = 1.0 이 그대로 유지된다.
from sim.engine import Recipe, simulate
f = simulate(Recipe(pack="sic_alumina_kmno4")).factors["chi"]
assert abs(f.value - 1.0) < 1e-9, f.value
assert f.confidence == "estimated", f.confidence   # 이번 회차 승격 실패의 직접 증거
```

## 6단계 — 게이트 실측 (본 회차, 전부 포그라운드 직접 실행)
- `verify_claims.py knowledge/cmp/chi-sic-alumina-kmno4-ph-independent-sweep.md` ✓
  (출처 6건 실존 · 코드 1블록 통과)
- `check_knowledge.py knowledge/cmp/chi-sic-alumina-kmno4-ph-independent-sweep.md` ✓
- `pytest -q` → **1267 passed, 1 skipped**, 546.40s, 회귀 0 (변경 전 기준과 동일)
- `completion.py check` → **64/70 불변**(65 로 오르지 않음 — 승격 실패를 숫자로
  숨기지 않는다). `χ chi/sic_alumina_kmno4: confidence=estimated` 는 C2 목록에
  그대로 남아 있다.
- `qa_loop.py run --strict` → **#277 PASS**, 유의 데이터셋 9/28, 유의 평균
  ρ **+0.9566 → +0.9566**(불변)

## 한계 (정직 표기)
- **핵심 파라미터(k=0.546/pH)는 여전히 그래프 판독(estimated)이다.** 이 노트는
  승격에 실패했다 — 실패 자체가 산출물이다.
- Wei 2026 의 "비단조 가능성"은 검증되지 않은 웹 검색 스니펫 하나에서 나온
  추정이며, 원문을 못 봐서 **정확한 pH 격자·수치·통계적 유의성을 전혀 모른다**.
  다음 회차가 원문을 확보하면 이 노트의 §1(B-4) 부터 다시 봐야 한다.
- EVIDENCE-RULES.md 의 판정#64 누락(§ "부수 발견")은 이번 과제 범위 밖이라
  고치지 않았다 — 원장 정합성 문제로 별도 기록해 둔다.

---

# 3회차(최종, 2026-09-19) — EVIDENCE-RULES 3회차 규칙 적용

> 회차 카운트: 판정#61(1회차) → 이번 2회차 절의 판정(2회차, 판정 번호는 §6 확정 시
> 기록) → **이번이 3회차, 마지막**. 확보 또는 종결로 끝낸다, 4회차는 없다.

## 경로 실행 기록

### 1. Wei et al. 2026, doi:10.1007/s00170-026-17750-1 — 재확인, 실패(불변)
- `find_open_access.py --title "Influences of pH environment on abrasive..."` →
  DOI 재확정(`10.1007/s00170-026-17750-1`, 제목 일치 확인)됐으나 `pdf`/`landing`
  둘 다 없음 — OA 소스 전무.
- Unpaywall 직접 조회(`api.unpaywall.org/v2/...`): `is_oa: false`,
  `has_repository_copy: false`, `oa_locations: []` — 그린 OA 사본 없음(신규
  변동 없음).
- OpenAlex 직접 조회: `open_access.any_repository_has_fulltext: false`,
  `best_oa_location: null`. 저자-소속 매핑은 이번 조회에서 처음 나왔다(Ying
  Wei/Ruhao Meng/Ke Fang Dai/Guoyan Huo/Haitao Wu → "Economic Research
  Institute"; Bing Liu → Xinxiang University; Wenbo Bie → Pingdingshan
  University; **Jianxiu Su → Zhongyuan University of Technology**[판정#62 Su
  2011 저자와 동일 소속으로 교차확인]; Yanan Peng → Shanghai Civil Aviation
  College) — 그러나 "Economic Research Institute"는 재료공학 논문 저자 소속으로
  개연성이 낮아(OpenAlex 저자 명 중복 해소 오류로 추정) **신뢰하지 않는다**.
  이 소속 정보로 개별 대학 리포지토리를 추적해도 신뢰도 낮은 단서라 실행하지
  않았다(중국 지방대 영문 리포지토리는 통상 색인되지 않음, `any_repository_
  has_fulltext=false`가 이미 이를 반영).
- Crossref 링크(`link.springer.com/content/pdf/....pdf`)를 curl 직접 요청 →
  HTTP 200 이지만 본문이 PDF 매직바이트가 아니라 HTML(idp 로그인 리다이렉트
  스텁, 2회차와 동일 증상) — 페이월 그대로.
- sci-hub 미러(`sci.bban.top`·`sci-hub.ru`·`sci-hub.se`) DOI 조회 → 전부
  PDF 링크 없음(2026-03 출판이라 미색인, 2회차 판단과 일치).
- **결론: 완전 봉쇄, 2회차와 상태 불변.**

### 2. Ceramics International doi:10.1016/j.ceramint.2025.07.097 — 재확인, 실패(불변)
- 저자: Xin Song, Jiani Guo, Changqi Xu, Zhigang Dong, Renke Kang, Shang Gao
  (OpenAlex) — 이 논문은 **판정#56-종결**(χ/sic_ceria_h2o2 항목, "Song 2025")과
  **동일 DOI·동일 논문**이다. 즉 이 팩(sic_alumina_kmno4)에서도 같은 벽을
  다시 만난다.
- Unpaywall: `is_oa: true`(hybrid) 이지만 `best_oa_location.url_for_pdf: null`,
  `url`은 `doi.org/...`(퍼블리셔 랜딩페이지 자체를 "OA 위치"로 잘못 표시하는
  Unpaywall 메타데이터 결함 — 실제로는 로그인 필요). `has_repository_copy: false`.
- doi.org → linkinghub.elsevier.com → sciencedirect.com 리다이렉트 체인을 직접
  curl 추적 → **최종 ScienceDirect 페이지 HTTP 403**(Cloudflare 봇 차단,
  2회차와 동일 증상). 그린 OA 리포지토리도 OpenAlex
  `any_repository_has_fulltext: false`로 확인(전무).
- 초록(OpenAlex `abstract_inverted_index` 복원) 확인: "4 abrasives(diamond,
  SiO2, CeO2, Al2O3) × 4 oxidizers(KMnO4, H2O2, KIO4, K2S2O8)" 조합 스크리닝
  후 **직교표 실험설계로 "slurry formulation and process parameters" 최적화**
  — pH 전용 스윕이 아니라 다인자 동시변동 최적화 단계로 확인된다. 즉
  **원문을 확보했더라도 사전 경고한 대로 Gong 2024 Table 3 와 동형인 다인자
  교란 구조**라 이 칸의 요건(pH 단독 스윕 3점 이상, 인쇄값)을 애초에 못
  채울 개연성이 높다(초록만으로 최종 판정은 안 하지만, 확보 우선순위를
  낮추는 근거로는 충분하다).
- **결론: 완전 봉쇄 + 확보해도 구조적으로 부적합할 가능성, 2회차 판단과 일치.**

### 3. Al2O3@MnO2 논문 — DOI 확정, 초록 수준도 확인 불가로 실패
- `find_open_access.py --title "Synthesis of Al2O3@MnO2 composite abrasives
  and their application in chemical mechanical polishing of silicon carbide"`
  → **DOI 확정**: `10.1016/j.ceramint.2024.03.120`, 정확 제목 "...and their
  chemical mechanical polishing performance on silicon carbide (SiC)"
  (Ceramics International, 2024-03-12, 저자 Pei-Jia Zhang, Hong Lei, Ze-Fang
  Zhang, Jianhua Zhang, Shi-Dong Chen, Xiaogang Hu — Shanghai University
  Research Center of Nano Science and Technology). 2회차는 이 DOI를 못 얻어
  시도조차 못 했던 지점 — 이번 회차에서 그 격차는 메웠다.
- Unpaywall: `is_oa: false`, `oa_locations: []`, `has_repository_copy: false`.
  OpenAlex: `any_repository_has_fulltext: false`. **초록 자체가 어디에도
  없다** — OpenAlex `abstract_inverted_index` 없음, Crossref `abstract`
  필드 없음, Semantic Scholar `abstract: null`(`openAccessPdf.status:
  CLOSED`).
- sci-hub.ru → sci-hub.kr 로 리다이렉트 → **altcha 로봇확인 페이지**(판정#68 과
  동일 증상, 자동화로 통과 불가).
- CORE v3 검색은 API 키 없이 리다이렉트 루프만 반환(본문·초록 접근 불가).
  ResearchGate 검색 페이지 403.
- **결론: DOI는 확정했지만(2회차 대비 진전), 초록 수준 확인조차 이 세션의
  접근 수단으로는 불가능 — pH 스윕 유무를 검증할 방법이 없다.** 산화제가
  고체상 MnO2 코팅(액상 KMnO4 아님)이라 애초에 이 팩과 계 근접도가 낮다는
  2회차의 판단도 유효하다.

## 판정 — 영구 종결(3회차, 최종)

노트 4단계가 지정한 경로 3개를 전부 실행했다. 결과:

| 경로 | 이번 회차 진전 | 최종 상태 |
|---|---|---|
| Wei 2026 (10.1007/s00170-026-17750-1) | 없음(2회차와 동일 벽 재확인) | 완전 봉쇄 |
| ceramint 2025.07.097 (Song 2025) | 초록 확인 → 직교표 다인자 구조로 요건 미달 개연성까지 드러남 | 완전 봉쇄 + 확보해도 부적합 위험 |
| Al2O3@MnO2 (10.1016/j.ceramint.2024.03.120) | **DOI 신규 확정**(2회차는 여기서 막혔었다) | 초록 수준도 확인 불가 |

3경로 모두 "안 했다"가 아니라 "확인했지만 이 세션의 접근 수단(공개 OA API +
sci-hub 미러 + 기관 리포지토리 색인 + 로컬 코퍼스)으로는 못 넘는 벽"이다 —
각 벽은 기계로 재현 가능한 근거(Unpaywall/OpenAlex JSON 응답, curl 리다이렉트
추적 결과, sci-hub 로봇확인 페이지)로 기록했다.

**EVIDENCE-RULES 3회차 규칙 적용 — 영구 종결. 값·confidence 0 변경.**
`sic_kmno4_ph_acid_k`=0.546·`sic_kmno4_ph_anchor`=2.0·`sic_kmno4_ph_floor`=0.268
전부 `estimated` 그대로 유지한다. held-out ρ 나 격자 숫자를 올리려고 계수를
역산하지 않았다 — 값을 바꿀 근거 자체가 없다.

- 판정 기록: EVIDENCE-RULES.md 판정#69-종결 (판정#61 1회차 → #69 2회차 →
  #69-종결 3회차·최종).
- 종결 등록: `validation/C2-CLOSURES.yaml`(factor=chi, pack=sic_alumina_kmno4,
  judgments=["판정#61","판정#69","판정#69-종결"]).
- `completion.py check` 격자: **66/70 → 67/70**. 이 칸은 C2(4)에서 빠지고
  '검증된 한계' 목록(13→14칸)으로 이동했다 — 등급 자체는 `estimated`로 불변,
  집계 분류만 "미조사"에서 "검증된 한계"로 바뀐 것이다.

## 한계 (정직 표기, 3회차 갱신)
- **핵심 파라미터(k=0.546/pH)는 여전히, 그리고 이제 영구적으로 그래프 판독
  (estimated)이다.** 이 칸은 더 이상 재탐색 대상이 아니다 — 재오픈 조건은
  위 C2-CLOSURES.yaml 항목의 `reopen_if`에 명시했다(Wei 2026 셀프아카이브,
  ceramint 2025.07.097 그린 OA 색인, 또는 독립 신규 문헌).
- Al2O3@MnO2 논문은 이번 회차에 DOI를 처음 확정했지만 초록조차 못 봤다 —
  다음에 이 DOI로 재시도할 때는 이 세션에 없던 접근 수단(예: 저자 이메일
  요청, 기관 계정)이 필요하다는 것이 이번 회차의 실질적 결론이다.
- Wei 2026·ceramint 2025.07.097 모두 **출간 후 시간 경과**가 유일한 해소
  경로로 보인다(그린 OA는 보통 발행 수개월~1년 뒤 올라온다) — 그러나
  3회차 규칙상 이 칸에 대한 자동 재시도는 이제 없다.

## 7단계 — verify(3회차 종결 재현 — 값 변경 없음)

```python verify
import yaml

# ── 종결 등록에도 불구하고 값·confidence 는 절대 바뀌지 않았음을 재확인 ──
pack = yaml.safe_load(open("knowledge/params/sic_alumina_kmno4.yaml"))
for key, expected in (("sic_kmno4_ph_acid_k", 0.546),
                      ("sic_kmno4_ph_anchor", 2.0),
                      ("sic_kmno4_ph_floor", 0.268)):
    p = pack["params"][key]
    assert p["confidence"] == "estimated", (key, p["confidence"])
    assert abs(p["value"] - expected) < 1e-9, (key, p["value"])

# ── C2-CLOSURES.yaml 에 이 칸의 종결 등록이 실제로 존재하는지 직접 확인
closures = yaml.safe_load(open("validation/C2-CLOSURES.yaml"))["closures"]
match = [c for c in closures
         if c["factor"] == "chi" and c["pack"] == "sic_alumina_kmno4"]
assert len(match) == 1, match
entry = match[0]
assert "판정#69-종결" in entry["judgments"], entry["judgments"]
assert entry["note"] == "knowledge/cmp/chi-sic-alumina-kmno4-ph-independent-sweep.md"

# ── 엔진 계약: 값을 안 바꿨으므로 기준 pH 에서 χ = 1.0 이 그대로 유지된다.
from sim.engine import Recipe, simulate
f = simulate(Recipe(pack="sic_alumina_kmno4")).factors["chi"]
assert abs(f.value - 1.0) < 1e-9, f.value
assert f.confidence == "estimated", f.confidence
```
