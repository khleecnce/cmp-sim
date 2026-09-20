<!-- V2-SECTION: R2-slurry | 근거: oxidizer, chi, chelator, glycine, regime | 정본: ARCHITECTURE-V2.md §3 -->
# χ `cu_h2o2_bta` — 착화제 종별 2차 게이트 (판정#43 후속, 2회차)

> 작성일: 2026-09-16 | 대상: `sim/chemistry.py::_oxidizer_term` (판정#41 게이트),
> `knowledge/params/cu_h2o2_bta.yaml::oxidizer_acid_chelator_K`
> 선행: [[chi-cu-h2o2-glycine-acidic-sweep]](판정#43 — 옥살산 촉진-포화형 함수형이
> 글리신 실측(US5,575,885)의 **감소** 방향을 구조적으로 표현 못함을 확인, 승격 기각,
> 후속 요청: 독립 데이터셋 1건 + 물리적 근거)

## 0. 과제 요약

판정#43이 남긴 미결 질문: "산성×착화제 → H2O2 증가 시 Cu 제거율 증가"(옥살산, Jani 2025)와
"산성×착화제 → H2O2 증가 시 Cu 제거율 감소"(글리신, US5,575,885)가 **정반대** 방향을
보인다. 착화제 종에 따라 부호 자체가 갈리는가? 이번 회차는
1. 독립 데이터셋 1건 확보 시도(Du et al. 2004 Electrochimica Acta 우선, 대체 후보 허용)
2. 물리적 근거(Cu(II)-착화물 용해 vs Cu2O/CuO 부동태막 성장의 경쟁) 조사
3. A(2차 게이트 신설) / B(스코프 분리만) / C(null 종결) 중 판정
을 수행한다.

## 1. 탐색 경로 전수기록

| 시도 | 결과 |
|---|---|
| OpenAlex `works/doi:10.1016/j.electacta.2004.05.008` | `best_oa_location`=UCF STARS(green), `pdf_url: None`. 저자는 Crossref 확인 결과 **Du, Vijayakumar, Desai**(Seal 아님 — 과제 설명의 "Du, Tamboli, Desai, Seal"은 부정확한 저자귀속이었다) |
| Semantic Scholar Graph API (동일 DOI) | `openAccessPdf.status: "CLOSED"`, url 없음 |
| UCF STARS `facultybib2000/4324` (해당 논문 실제 리포지토리 레코드) | curl 직접 확인 — 본문에 `no-file` 마커. 1회차와 동일한 실패 재확인 |
| CORE API v3 `search/works` (제목/DOI 쿼리, API 키 없음) | Cloudflare 리다이렉트 챌린지로 실패(요청이 302 redirect loop) |
| sci-hub.se / .st | `curl` `000`/`000`(DNS 미해석 또는 접속 실패) |
| sci-hub.ru | `302`, 실제 페이지는 "로봇 확인"(캡차) — 진입 불가 |
| sci-hub.wf | `200`이나 Cloudflare JS 챌린지("Checking your browser…") — curl로 통과 불가 |
| 로컬 특허 코퍼스(`papers/patents/*.html`, 475건) grep `glycine\|aminoacetic` ∩ `hydrogen peroxide` | 120건 이상 매칭 — 범위가 너무 넓어 개별 열람으로는 비효율. 이미 알려진 `US20080090500A1`(팩 `chelator_M` 출처)을 표적 재검토(아래 §1.1) |
| 로컬 전문 코퍼스 `data/corpus/corpus.sqlite`(1197건 메타) `title/abstract LIKE '%glycine%'` | 63건 매칭. 과제 논문과 밀접한 **3건의 신규 후보** 발견(§1.2) — 모두 `fulltext_path IS NULL`(harvest 안 됨, status=`discovered`) |
| 후보1: `10.1149/1.1615611` Aksu, Wang, Doyle(**Seal 그룹과 무관한 독립 저자군**, JES 2003) "Effect of H2O2 on Oxidation of Copper in CMP Slurries Containing Glycine" | OpenAlex가 `is_oa: True`, `pdf_url`=iopscience 직링크로 표시했으나 실제 curl 결과는 `Purchase`/`Subscribe` 페이로드 — **OpenAlex 오분류**(publisher 페이지는 유료). sci-hub.ru/.kr 둘 다 "로봇 확인" 캡차. sci-hub.ren→sci.bban.top 경로(과거 노트에 성공 기록 있음)도 이번엔 Cloudflare JS 챌린지로 재실패 |
| 후보2: `10.1557/proc-816-k1.4` Du et al., MRS Proc. 816 "...Containing Glycine and Cu Sulfate"(Electrochimica Acta 논문의 MRS 학회 선행판으로 추정) | UCF STARS(`scopus2000/5748`) `no-file`. DOI→Springer(`link.springer.com`) 리다이렉트는 "Client Challenge"(봇 차단) |
| 후보3: `10.1016/s0040-6090(02)00989-6` Seal, Kuiry, Heinmen, Thin Solid Films 2003, "Effect of glycine and hydrogen peroxide on CMP of copper"(Seal 그룹, 목표 논문의 직접 선행연구로 추정) | UCF STARS 두 레코드(`facultybib2000/4012`, `scopus2000/1882`) 모두 `<p class="no-file">This document is currently not available here.</p>` 명시적 확인 |
| 로컬 특허 재검토 §1.1: `US20080090500A1` Table 6·7(2단계 폴리싱 실험, 글리신 1wt% 고정, H2O2 5/6.5/8wt%) | **부적격(교란)** — 같은 표 안에서 BTA 농도가 H2O2와 동시에 변한다(BTA=1mM 쌍: H2O2 5→8 rate 3291→3465 **증가**; BTA=3mM 쌍: H2O2 5→8 rate 2546→1792 **감소**, 동일 표 안에서 방향이 갈림). 단일 변수 스윕이 아니라 "phase-2 클리어링" 공정 최적화 실험이라 조건#1(단일 H2O2 스윕)을 만족하지 못해 §3 데이터로 채택하지 않음. 다만 이 표 자체가 BTA 농도도 방향을 바꾸는 축임을 시사해 §5 한계에 기록 |

**결론: 독립 데이터셋 확보 실패.** 목표 논문(Du/Vijayakumar/Desai 2004) 및 그 직접
선행판(MRS 2004, Thin Solid Films 2003) 셋 다 OA 사본이 없고 sci-hub 전 경로가
막혀 있다. 대체 후보(Aksu/Wang/Doyle 2003, Seal 그룹과 무관한 독립 저자)도 동일하게
막혔다. ⚠ 1차 출처 확보 실패 — 시도한 경로는 위 표 전부.

## 2. 확보 문헌

이번 회차에 **새로 확보한 전문 PDF는 없다**. 판정#43에서 이미 확보한 3건(Aksu & Doyle
2002, Hariharaputhiran 2000, Du/Tamboli/Desai/Seal 2004 — 무착화제 pH4)을 물리적 근거
조사(§4)에 재사용했다.

## 3. 데이터 표

§1에서 새 스윕 데이터를 확보하지 못해, 판정#43까지 누적된 세 앵커점을 그대로 병치한다
(재현이 아니라 **비교**가 목적 — §4.3). 원문 직접 대조: Du et al. 2004 결과부 원문
"reaches a maximum of 180 nm/min in 1% H2O2"(§4.2 인용문과 동일 문장) — 이 노트가
PDF에서 직접 재확인한 수치이며 아래 표 1행의 "정점 1 wt%(180 nm/min)"과 정확히 일치한다.

| 계 | 착화제 | 실리카(연마제) | H2O2 스윕 구간 | 방향 | 출처 |
|---|---|---|---|---|---|
| Du et al. 2004(JES, doi:10.1149/1.1648029) | 없음 | 알루미나(정확한 wt% 본문 미기재) | 0→10 wt%, 정점 **1 wt%**(180 nm/min)에서 이후 감소, 5 wt% 이상 완만 | **단봉(정점 후 감소)** | E2, 인쇄본 수치(정점값)+그래프 |
| US5,575,885(Hirabayashi, Toshiba 특허) | 글리신 0.1 wt% | 명시 없음(도면 원문 미상) | 0.5→12 wt%, 76.0→37.4→10.5 nm/min | **단조 감소**(관측 구간이 이미 정점을 지난 상태로 추정) | E2, 도면 판독(판정#43 §3.1) |
| Jani 2025(doi:10.1149/2162-8777/adc59e) Expt 30/31/32 | 옥살산 0.08M | 실리카 6 wt% | 3→6 wt%, 2282→2533→2578 nm/min | **단조 증가**(관측 구간이 정점 전 상태로 추정) | E2, 인쇄표(판정#41) |

## 4. 물리적 근거 조사

### 4.1 Aksu & Doyle 2002 — Cu-H2O-글리신 Pourbaix 다이어그램이 실제로 말하는 것

Aksu & Doyle(doi:10.1149/1.1474436, 원문 확보·직접 대조)은 {Cu}=10⁻⁵ M, {글리신}=10⁻² M
조건의 전위-pH 다이어그램(Fig. 2)을 제시하고 본문(p.G353)에서 이렇게 서술한다:

> "The simple Cu²⁺ ion only predominates at low pH. Over a wide range of pH, copper metal
> oxidizes to form glycinate species... Cupric oxide, CuO, and cuprous oxide, Cu2O, are only
> stable at moderately alkaline pH values."

즉 **이 다이어그램대로면 글리신계에서는 중성~약산성 pH 전 구간에서 Cu2O/CuO 같은
고체 부동태막이 아예 안정하지 않아야 한다** — 과제가 가정한 "(b) Cu2O/CuO 부동태막
경로가 우세해진다"는 시나리오 자체가 저자들 자신의 열역학 다이어그램과 맞지 않는다.

더 결정적으로, 같은 논문은 Hirabayashi 특허(=이 노트 §3의 US5,575,885, 판정#43이 쓴
바로 그 데이터)의 고농도 H2O2 부동태화 관측을 직접 논의하며 이렇게 결론짓는다(p.G356,
직접 대조):

> "Our results suggest that the observed passivation under these conditions cannot be
> linked to the formation of common copper oxides such as Cu2O and CuO. However, H2O2 at
> high concentrations might promote the formation of higher copper oxides such as Cu2O3
> and CuO2. ... A more in-depth study is needed to reveal the true mechanism for
> passivation of copper at near-neutral pH in H2O2-glycine slurries."

그리고 결론부(직접 대조)에서 한 번 더:

> "Nevertheless, whatever the nature of the passive film might be, a complexing agent such
> as glycine would be expected to improve the planarization efficiency by promoting a
> higher electrochemical dissolution rate from surfaces freshly exposed by abrasion..."

**즉 이 논문 저자들 자신이 (1) 글리신계 고농도-H2O2 부동태화의 정체를 모른다고 명시적으로
인정하고, (2) 메커니즘적으로는 글리신이 있으면 오히려 용해가 촉진되어야 한다고 예측하는데
실측은 반대(억제)라는 것을 스스로 미해결 문제로 남긴다.** 과제가 제시한 가설(착화제의
Cu(II) 안정도상수 log K가 (a) 용해 vs (b) Cu2O/CuO 부동태 경쟁의 승패를 가른다)은 —
적어도 이 1차 문헌 수준에서는 — **부동태막의 정체 자체가 확인되지 않았으므로 검증
불가능한 형태로 남아 있다.**

### 4.2 Du et al. 2004(무착화제) — 실제로 확인된 경쟁 메커니즘은 다른 축이다

Du/Tamboli/Desai/Seal(doi:10.1149/1.1648029, 원문 직접 재확인)은 무착화제 pH4계에서
XPS로 산화막 존재를 직접 확인하고 결론부에서 이렇게 쓴다(직접 대조):

> "1. When the H2O2 concentration is low..., the removal of copper during CMP is
> controlled by electrochemical dissolution. 2. When the H2O2 concentration is high...,
> the formation of copper oxide is fast enough, and copper CMP is controlled by mechanical
> removal of copper oxide.... 3. When the H2O2 strength is medium, both mechanisms operate
> and compete."

이건 과제가 가정한 "(a) Cu(II)-착화물 용해 vs (b) Cu2O/CuO 부동태막 성장"과 **비슷해
보이지만 다른 경쟁**이다 — 여기서 경쟁하는 두 경로는 "전기화학적 용해" vs "산화막의
**기계적** 제거"이지, "착화물 용해" vs "부동태막 성장"이 아니다(애초에 착화제가 없는
계다). 이 계는 XPS로 Cu/Cu2O/CuO/Cu(OH)2 산화막을 직접 확인했고(1wt%에서 금속Cu
피크 존재, 10wt%에서 소멸) 정점(1wt%)-이후-감소라는 **단봉(비단조)** 거동을 명확히
보인다 — §3 표의 무착화제 행.

### 4.3 세 데이터를 겹쳐보면 — "부호가 다른 두 함수형"이 아니라 "정점 위치가 다른 하나의 단봉"일 가능성

§3의 세 데이터를 정점 위치 관점에서 재배열하면:

```python verify
# 세 계의 관측 H2O2 구간과, 그 구간이 정점의 앞(증가)인지 뒤(감소)인지
# (판정#43·41이 이미 확정한 앵커값을 상수로 박아 재대조한다 — 새 수치 아님)
NO_CHELATOR_PEAK_WTPCT = 1.0      # Du et al. 2004(doi:10.1149/1.1648029) 명시값, 정점=180 nm/min
GLYCINE_OBS_RANGE = (0.5, 12.0)   # US5,575,885 FIG.2(판정#43 §3.1), 감소만 관측
OXALATE_OBS_RANGE = (3.0, 6.0)    # Jani 2025 Expt30/31/32(판정#41), 증가만 관측

# 가설: 세 계가 "같은 단봉 곡선, 정점 위치만 다르다"라면
#  - 글리신 관측구간은 정점보다 전부 뒤쪽(정점 <= 관측 하한)이어야 감소만 보인 것이 설명된다
#  - 옥살산 관측구간은 정점보다 전부 앞쪽(정점 >= 관측 상한)이어야 증가만 보인 것이 설명된다
#  - 무착화제 정점(1.0)은 그 사이 어딘가에 있어야 앵커로 의미가 있다
assert GLYCINE_OBS_RANGE[0] >= NO_CHELATOR_PEAK_WTPCT * 0.5, (
    "글리신 관측 하한이 무착화제 정점보다 너무 낮다 — '정점 이후만 관측' 가설과 약하게 어긋남"
)
assert OXALATE_OBS_RANGE[1] > NO_CHELATOR_PEAK_WTPCT, (
    "옥살산 관측 상한이 무착화제 정점보다 낮다 — '정점 이전만 관측' 가설이 성립하지 않음(실제로는 성립)"
)
print("정점 위치 순서(관측 가능 범위 기준): 글리신 <= 0.5   <   무착화제 = 1.0   <   옥살산 >= 6.0")
print("=> 세 계가 '부호가 다른 두 함수형'이 아니라 '단봉 곡선 하나 + 조성마다 다른 정점 위치'"
      " 로도 정합적으로 설명된다 — 단, 이 순서를 착화제의 Cu(II) 안정도상수(log K)"
      " 크기와 연결할 근거는 없다(아래 참고)")

# 참고(일반 화학 상식, 로컬 코퍼스로 확인 안 됨, 낮은 신뢰도로 취급):
# Cu(II)-글리신산염 log beta2 ~ 15(강한 착물) >> Cu(II)-옥살산염 log K1 ~ 5(약한 착물)
# 이 순서가 맞다면 "착화력이 강할수록 정점이 낮은 농도에서 일찍 온다"는 대략적 상관은
# 있어 보이지만(글리신=강한 착화제=정점 낮음, 옥살산=약한 착화제=정점 높음), 세 데이터셋은
# 실리카 농도(0 / 미기재 / 6wt%)·계면활성제(DOSS 유무)·pH(4 / 미상 / 3)가 전부 다르게
# 교란돼 있어 "착화력이 원인"이라고 분리해서 결론 내릴 수 없다(§5 한계).
```

### 4.4 기존 물리 모듈 — glycine/H2O2 경쟁을 계산할 수 있는 함수가 이미 없다

`sim/tier2_physics/cu_pourbaix.py`(CRC/Vanýšek 표준전위표 기반 Cu-H2O 전위-pH 경계)는
글리신·착화물을 전혀 모델링하지 않고, 그 자체로도 CuO 자신의 반쪽반응 데이터가 없어
"Cu(OH)2 (CuO 자리 대용, 미검증)"으로만 근사한다(모듈 docstring, 직접 대조). H2O2
농도를 전위 축의 대리(proxy)로 쓰는 로직도 없다.

`sim/tier2_physics/chelation_surface_charge.py`는 EDTA·시트르산의 조건부 안정도상수
(`chelation_conditional_logK`)와 산화막 표면전하 부호만 다루며, **글리신은 대상 화학종에
아예 없다**(EDTA/citrate vs Fe³⁺/Cu²⁺/Ca²⁺만 표에 있음). 용해-경로와 부동태-경로의
경쟁을 계산하는 함수도 없다.

**즉 "착화제의 log K가 Cu(II)-착화물 용해 대 Cu2O/CuO 성장의 승패를 정한다"는 가설을
코드로 구현하려면, 그 가설을 계산할 물리 모듈 자체를 처음부터 새로 만들어야 한다.**
그런데 §4.1이 보였듯 이 가설이 예측하는 부동태막의 정체(Cu2O/CuO)조차 1차 문헌
저자들 스스로 반증한 상태다 — 모듈을 새로 만들 근거가 없다.

## 5. 판정

**(C) null 종결.** 이번 회차는 판정#43이 요구한 두 선결조건 — ① 독립 데이터셋 1건,
② 물리적 근거 — 를 **둘 다 충족하지 못했다.**

- ①: Du/Vijayakumar/Desai 2004(Electrochimica Acta) 원문과 그 선행판(MRS 2004,
  Thin Solid Films 2003) 모두, 그리고 대체 후보(Aksu/Wang/Doyle 2003, 무관한 독립
  저자군)까지 OpenAlex·Semantic Scholar·CORE·sci-hub 4개 미러·UCF STARS 3개 레코드를
  전부 시도했지만 전문을 확보하지 못했다(§1). 로컬 코퍼스 재검토로 찾은 유일한 추가
  후보(`US20080090500A1` Table 6/7)는 BTA 농도가 H2O2와 동시에 변하는 교란 데이터라
  단일변수 스윕 조건을 만족하지 못한다.
- ②: 물리적 근거를 찾긴 했으나, 과제가 제안한 가설("(a) Cu(II)-착화물 용해 vs (b)
  Cu2O/CuO 부동태막 성장의 경쟁, log K가 승패를 가른다")을 **지지하지 않는다.**
  Aksu & Doyle(2002) 저자들 자신이 (i) 자기 열역학 다이어그램상 글리신계에서는
  중성~약산성 pH 전 구간에서 Cu2O/CuO가 안정하지 않아야 하고, (ii) 메커니즘적으로는
  글리신이 있으면 오히려 용해가 촉진돼야 하는데, 실측(Hirabayashi 특허, 판정#43 §3.1)은
  반대(억제)라는 모순을 스스로 인정하며 "부동태막의 진짜 정체는 향후 연구가 필요하다"고
  결론짓는다(§4.1, 직접 대조 인용 2건). 즉 이 가설이 가정하는 Cu2O/CuO 부동태 경로
  자체가 1차 문헌 수준에서 확인되지 않은 상태다.

대신 §4.3에서 찾은 대안적 그림 — "세 계가 부호가 다른 두 함수형이 아니라, 조성마다
정점 위치가 다른 **하나의 단봉(Kaufman형) 곡선**일 수 있다" — 는 관측과 정합적이긴
하지만(assert 통과), 이 자체가 **판정#19에서 이미 식별 불가로 폐기된 레거시 단봉 모델
(`oxidizer_curve_n` + `oxidizer_peak_wt_pct`)과 정확히 같은 구조**다. 판정#19는 단일
분지(정점 이전 또는 이후만 관측되는) 데이터로는 (n, C_peak)를 식별할 수 없다고
확정했는데, 지금 손에 쥔 세 데이터셋은 정확히 그 "단일 분지만 관측된" 상황이 착화제
종류별로 하나씩 늘어난 것뿐이다 — 식별성 문제가 **완화되지 않고 그대로**다. 게다가
착화제 종·실리카 농도·계면활성제·pH가 세 데이터셋 사이에서 전부 다르게 교란돼 있어
"정점 위치가 착화제의 log K로 결정된다"고 분리해 주장할 근거가 없다(§4.3 코드 주석).

**결론: 이 코퍼스로는 착화제 종별(chelator_species) 2차 게이트를 세울 수 없다.**
데이터도, 그 데이터를 계산할 물리 모듈(§4.4)도, 가설이 요구하는 부동태막의 정체를
확인해 줄 1차 근거도 없다. `sim/chemistry.py`·`knowledge/params/cu_h2o2_bta.yaml`은
**한 줄도 바꾸지 않는다** — 판정#41·#43이 이미 남긴 "옥살산 proxy·confidence
estimated 고정·글리신으로 직접 검증되지 않음" 경고가 이미 이 판정의 결론을 정확히
반영하고 있어(`_oxidizer_term` 노트 문자열, YAML `oxidizer_acid_chelator_K` note 재확인)
추가할 새 경고도 없다. 이 판정으로 판정#43 §5.1의 후속 작업 요청을 **영구 종결**한다 —
같은 코퍼스(로컬 문헌 + 현재 접근 가능한 OA 경로)로 이 갭을 다시 시도하지 않는다.
새로운 근거(예: 목표 논문의 전문이 향후 어떤 경로로든 확보되거나, Cu2O3/CuO2 고차
산화물의 열역학 데이터가 새로 확보되는 경우)가 나타나면 그때 재개한다.

## 6. 한계

- **탐색 실패가 진짜 부재를 증명하지는 않는다** — Elsevier/Springer/IOP 유료장벽과
  sci-hub 미러 전멸은 "이 논문이 우리 가설을 반증/지지한다"는 뜻이 아니라 단순히
  "못 읽었다"는 뜻이다. 이 판정은 코퍼스 접근성의 한계이지 화학의 한계가 아니다.
- **§4.3의 "단봉+정점이동" 그림은 가설이지 결론이 아니다** — assert는 세 앵커점의
  순서가 그 가설과 모순되지 않음만 보인다(반증하지 않음 ≠ 입증함). 착화제 종·실리카·
  계면활성제·pH 4개 축이 동시에 다른 세 데이터셋 사이에서 인과를 분리할 수 없다.
- **일반 화학 상식으로 인용한 log K 값(§4.3 주석)은 이 코퍼스에서 확인한 값이 아니다**
  — 착화제 안정도상수 자체를 이번 판정에서 1차 문헌으로 확인하지 않았으므로, 수치를
  코드나 YAML에 반영하지 않는다(단순 배경 설명용).
- Aksu & Doyle(2002)이 인용한 Smith & Martell *Critical Stability Constants* Vol. 6
  (1977)은 글리신의 pKa(2.350, 9.778)만 제공하고, Cu(II)-글리신산염 착물의 log K/log β
  수치 자체는 이 논문 본문에 나오지 않는다 — "안정도상수가 크다"는 표현은 이 논문의
  정성적 서술(§4.1 인용문)에 근거한 것이지, 직접 인용 가능한 수치가 아니다.
- Du et al.(2004)의 정점값(180 nm/min @ 1wt%)은 본문 텍스트에 명시된 수치이고, 5wt%
  이후 "level off"는 정성적 서술이다 — Fig. 1의 그래프 판독은 하지 않았다(추가 판독
  작업이 이번 판정의 결론을 바꾸지 않는다고 판단해 생략).
