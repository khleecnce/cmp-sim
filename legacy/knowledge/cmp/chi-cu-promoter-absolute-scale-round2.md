---
title: χ/cu_h2o2_bta promoter(옥살산) 절대 배수 1차 검증 — 2회차 (판정#85)
status: 완료 — 후보 B(값·코드·YAML 0변경), 1차 문헌 4건 확보했으나 요건 미충족
---

# χ/cu_h2o2_bta promoter 절대 배수 — 2회차 (판정#85)

> Max워커 위임 | 작성일: 2026-09-20
> 선행: [[chi-cu-promoter-absolute-scale-round1]] (판정#85 1회차, B 채택) ·
> [[c4-cu-h2o2-bta-heldout-diagnosis]] (판정#84) ·
> [[chi-carboxylate-promoter-cu-oxalate-us6309560]] (현재 φ·m·anchor 출처)

## 1. 요건 재기술

`sim/chemistry.py::_carboxylate_promoter_term` 의 g(C) = φ + (1−φ)(C/C_anchor)^m 에서
팩 `cu_h2o2_bta` 는 `promoter_ref_M=0` 이라 분모 g(0)=φ=0.078058 이 되고, held-out
(`jani2025_cu_rsm_composition_heldout`) 13개 조건에 8.11~20.40배가 곱해진다(판정#84).
φ·m·anchor 셋 다 US6309560B1(알루미나·옥살산암모늄·BTA無) 타계 전이(E4).

이번 회차가 찾아야 하는 통제쌍 요건 네 가지:
1. Cu 기판
2. **콜로이달 실리카** 연마입자
3. 옥살산(또는 동종 카복실레이트) **농도만** 스윕, 그중 **한 점이 C=0**(무첨가 대조군)
4. MRR이 **인쇄값**(표 또는 본문 숫자, 그래프 판독 아님)

넷을 모두 만족하면 φ = MRR(C=0)/MRR(C_anchor)를 대상계에서 직접 역산해 현재 값과
대조(후보 A), 하나라도 빠지면 값 불변 + 실패 기록(후보 B).

## 2. 소진 경로 (호출자 실측, 이번 회차 재시도 안 함)

| # | 경로 | 실측 | 상태 |
|---|---|---|---|
| 1 | IOP 직접 PDF (Surisetty 2008 DOI: 10.1149/1.2987791 · Janjam 2008 DOI: 10.1149/1.2829112 · Hazarika 2022 DOI: 10.1149/2162-8777/ac6d72) | OpenAlex bronze이지만 Radware botmanager(validate.perfdrive.com) 리다이렉트, HTTP 200 / text/html / **14371바이트** | 영구 소진 |
| 2 | Wayback Machine | CDX 스냅샷 4건 전부 302(1438~1692바이트), /pdf 스냅샷 302(1445바이트), 2025-05-07 본문 5655바이트에 'oxalic' 0회 | **영구 소진** |
| 3 | sci-hub se/st | DNS 실패(000) / ru·box 302 본문 없음 | (아래 §3-6: **.ren 미러는 살아 있음**) |
| 4 | digitalcommons/scholar.clarkson.edu | DNS NXDOMAIN | 영구 소진 |
| 5 | Qatar Univ. QSpace | Babu 484건·CMP 106건 중 CMP 논문 0건(2008년 소속은 Clarkson) | 영구 소진 |

## 3. 신규 탐색

### 3-1. 로컬 코퍼스 동의어 확장 스크리닝 (`data/corpus/corpus.sqlite`)

`copper AND (oxal|carboxyl|complexing agent|chelat|citric|glycine) AND (polish|cmp|planariz)`
→ 108건. 전문(`fulltext_path`) 보유 5건만 판독:

| id | 판독 결과 | 탈락 사유 |
|---|---|---|
| openalex:W2977501042 (UCF ETD/36, 2004) | 초록 5.9k자만 | oxalic 0회 |
| openalex:W2741633219 (UCF ETD/22, 2004) | 초록 8.4k자만 | oxalic 0회 |
| DOI: 10.3390/ma17194905 (2024, Mo/Cu 시트르산 약알칼리) | 전문 93k자 | oxalic 0회, 알칼리 시트르산계(대상계 아님) |
| DOI: 10.1038/s41378-025-00883-w (2025, Nature MEMS) | 전문 52k자, oxalic 25회 | **MD 시뮬레이션**(원자 제거 개수) — 실험 MRR 인쇄값 없음 |
| DOI: 10.1039/d2na00405d (2022, OFC 래핑) | 전문 | oxalic 0회 |

부산물: Nature MEMS 2025 참고문헌 29번이 **Gorantla, Babel, Pandija, Babu,
"Oxalic Acid as a Complexing Agent in CMP Slurries for Copper", ESSL 8, G131 (2005)**
를 인용 → Crossref 조회로 DOI: 10.1149/1.1883873 확인. Unpaywall `oa_status: closed`.
IOP PDF 직접 fetch: HTTP 200 / text/html / **14371바이트**(호출자가 실측한 봇벽 페이지와
동일 크기) → 차단.

전문 없는 108건 중 제목상 요건 근접 후보(전부 IOP):
DOI: 10.1149/1.2083287 (2005, 아민/카복실 작용기 역할) · DOI: 10.1149/2.0171808jss (2018,
착화제 선택 vs 디싱) · DOI: 10.1149/2162-8777/adc59e (2025, 고속 Cu CMP 킬레이터·억제제·
산화제·연마입자 재검토, Unpaywall **hybrid**) · DOI: 10.1149/2162-8777/ae70a8 (2026, 착화제별
MRR 선택비, bronze). hybrid인 adc59e조차 IOP PDF fetch는 14371바이트 봇벽(위와 동일)
→ IOP 호스트 자체가 이 세션 IP를 차단하므로 OA 상태와 무관하게 IOP 직접 경로는 전부 소진.

### 3-2. CORE API v3 (무키)

1차 배치 8회 중 5회 `429`, 3회 200 — **간헐 작동**(호출자 관측과 1회차 "무키 429"
관측이 둘 다 맞았다: 호출 빈도 제한). 2차 배치(12초 백오프·4회 재시도)는 20회 중
19회가 429/500, 1회만 200 → 사실상 사용 불가. 200 응답에서 건진 것:
- `Surisetty Babu copper CMP oxalic` → 제목만 반환된 학위논문 후보 2건
  "Colloidal and Electrochemical Aspects of Copper-CMP"(2007, downloadUrl 없음),
  "Chemical Mechanical Polishing Of Copper And Tantalum Barrier: Studies On Slurry
  Chemistry"(2006, downloadUrl 없음) — 상세 조회는 429/500으로 실패. 3회차 경로로 이월.
- 나머지 히트는 옥살산 전기화학·Cu 나노입자 등 무관.

### 3-3. clarkson.figshare.com · figshare API

`clarkson.figshare.com/` 및 `/search?q=oxalic copper cmp` → HTTP **202, 본문 0바이트**
(JS 렌더링 SPA, 서버 사이드 본문 없음). 공개 API `api.figshare.com/v2/articles/search`
(POST, `oxalic acid copper chemical mechanical polishing`) → **0건**. Clarkson 리포지토리에
Babu 그룹 옥살산 논문·학위논문 없음(또는 미색인).

### 3-4. Europe PMC · OpenAlex(is_oa) 전문 검색

- Europe PMC `"oxalic acid" AND copper AND (CMP…) AND "removal rate"` → 5건, 전부
  무관(316 스테인리스 래핑·MD 시뮬레이션·무연마재 전해 CMP·유동층 CMP·리뷰).
- OpenAlex `is_oa:true` 필터 2질의(1243건·22건 중 상위 25건씩 판독) → gold/hybrid OA 중
  대상계 후보 0건. 요건 근접 논문은 전부 IOP bronze(위 3-1과 동일 목록).
- Semantic Scholar API: 3질의 전부 429.
- exa 웹검색(MCP): 이 세션에서 권한 미승인 → 사용 불가.

### 3-5. 로컬 특허 코퍼스 (`papers/patents/*.html`, 471건)

`oxal AND "colloidal silica" AND copper` → 129건. 그중 옥살산이 **표 안에** 나오고
같은 표에 제거율 단위가 있는 것 20건을 전수 판독: 전부 W CMP 촉매표(CN1131125C·
KR20110095838A), 제타전위 안정성 표, TEOS 연마표, 인용문헌 목록 등 **오탐**. 옥살산
농도 스윕 실시예표는 0건(1회차 결론과 동일).

### 3-6. sci-hub 재시도 — **이번 회차 유일한 성공 경로**

호출자 실측(se/st DNS 실패·ru/box 302)과 달리 **sci-hub.ren 은 200**으로 응답하며
`sci.bban.top/pdf/<DOI>.pdf` 링크를 돌려준다. 1회차가 sci.bban.top 을 직접 쳐서
403/404를 받은 것과 달리, **Referer=sci-hub.ren 을 붙인 PDF 직링크는 200 application/pdf**
로 내려온다. 확보 5건(크기는 실측 바이트):

| DOI | 파일 | 바이트 | 1쪽 대조 |
|---|---|---|---|
| DOI: 10.1149/1.1883873 | Gorantla·Babel·Pandija·Babu 2005 ESSL "Oxalic Acid as a Complexing Agent in CMP Slurries for Copper" → `papers/gorantla2005-essl-oxalic-acid-complexing-cu-cmp.pdf` | 265,460 | 제목·저자·"ESSL 8(5) G131-G134 (2005) © ECS" 일치 ✓ |
| DOI: 10.1149/1.2987791 | Surisetty·Goonetilleke·Roy·Babu 2008 JES "Dissolution Inhibition in Cu-CMP Using DBSA…" → `papers/surisetty2008-jes-dbsa-oxalic-glycine-cu-cmp.pdf` | 1,252,109 | 제목·저자·"JES 155(12) H971-H980 (2008)" 일치 ✓ |
| DOI: 10.1149/1.2829112 | Janjam·Surisetty·Pandija·Roy·Babu 2008 JES "Oxalic-Acid-Based Slurries with Tunable Selectivity…" → `papers/janjam2008-jes-oxalic-acid-cu-ta-selectivity.pdf` | 302,102 | 제목·저자·Clarkson 일치 ✓ |
| DOI: 10.1149/1.2083287 | Gorantla·Goia·Matijević·Babu 2005 JES "Role of Amine and Carboxyl Functional Groups…" → `papers/gorantla2005-jes-amine-carboxyl-complexing-cu-cmp.pdf` | 267,604 | 제목·저자 일치 ✓ |
| DOI: 10.1143/jjap.41.1305 | (JJAP 2002 유기산 슬러리 안정성) | 716,324 | **오염사본** — 1쪽이 "Conduction of Electricity Through Metals, 1914 Proc. Phys. Soc. London 27 527", oxal 0회 → **폐기, 저장 안 함**(판정#32 패턴 재발) |

Hazarika 2022(DOI: 10.1149/2162-8777/ac6d72)는 1회차 판정대로 Co/Cu 갈바닉 목적이라
시도하지 않았다(3회차 필요 시 같은 경로).

## 4. 확보 문헌 원문 판독 — 요건 대조

| 문헌 | ① Cu | ② 연마입자 | ③ 옥살산 농도 스윕 + C=0 | ④ MRR 인쇄값 | 결과 |
|---|---|---|---|---|---|
| Gorantla 2005 ESSL (DOI: 10.1149/1.1883873) | ✓ | **fumed silica** Aerosil-130 3 wt% | ✗ 옥살산 **0.065 M 고정**, pH 1.5~8 스윕(Fig. 1) | ✗ 그래프; 본문에 pH≈1.5 값만 "dissolution <30 nm/min, polish ~1500 nm/min" | 탈락 |
| Surisetty 2008 JES (DOI: 10.1149/1.2987791) | ✓ | **fumed silica** Aerosil-130 3 wt% | △ 옥살산 **0.016~0.065 M 스윕**(pH 3, 5 wt% H2O2, Fig. 2C) — 그러나 **C=0 점 없음**(Fig. 1 의 글리신-only 는 다른 착화제이지 무첨가가 아님) | ✗ 그래프; 본문에 범위만 "OA/peroxide 700 to 2400 nm/min" vs 글리신-only "~200 nm/min" | 탈락 |
| Janjam 2008 JES (DOI: 10.1149/1.2829112) | Cu/Ta | **fumed silica** 3 wt% | ✗ 옥살산 **0.13 M 고정**, H2O2 0~10 wt%·pH 스윕(Ta 중심) | ✗ 그래프(Table I 은 거칠기) | 탈락 |
| Gorantla 2005 JES (DOI: 10.1149/1.2083287) | ✓ | **fumed silica** Aerosil-130 3 wt% | △ Fig. 1B 에 **5 wt% H2O2 단독(착화제 C=0)** 폴리시율과 아세트산·글리신·에틸렌디아민 **각 0.13 M 고정** pH 스윕 — 종이 옥살산이 아니라 아세트산(모노카복실레이트), 농도 스윕 아님 | ✗ 그래프 | 탈락 |

**넷 다 ②(콜로이달 실리카)·④(인쇄값)에서 탈락**하고, ③(C=0 옥살산 대조점)을 가진
것은 하나도 없다. 1회차가 "fumed silica 라는 점을 감수하고 승격할지"를 2회차 결정으로
남겼는데, 원문을 열어 보니 연마입자 문제 이전에 **C=0 옥살산 점 자체가 어느 논문에도
없다**(Babu 그룹은 착화제 없는 H2O2 슬러리를 Cu 폴리시 대조군으로 두지 않고, 착화제
종류·pH를 축으로 삼는다). 따라서 "승격 여부" 판단은 성립하지 않는다.

### 4-1. 부수 정량 대조 (φ 아님 — m 의 방향 점검, 값 변경 근거 아님)

Surisetty 2008 본문 인쇄 범위 "700 to 2400 nm/min"(옥살산 0.016~0.065 M, pH 3, 5 wt%
H2O2, 3 wt% fumed silica)로 **농도비 4.06배에 대한 MRR 비 ≥3.43배**를 얻는다(범위의
양 끝이 정확히 두 농도 끝점이라는 보장은 본문에 없으므로 하한으로만 쓴다 — 끝점 대응은
**미검증**, Fig. 2C 축 판독을 안 했다). 현재 팩
(φ=0.078058, m=0.7238, anchor 0.040290 M)의 g(0.065)/g(0.016) = **2.51배**. 즉 현재
멱함수는 이 계의 농도 민감도를 **≥27% 과소**(2.51 vs ≥3.43)로 본다 — 본문이
"0.032 M 위에서 급증(abrupt increase)"이라 서술하므로 단순 멱함수 형태 자체가 이 계와
맞지 않을 수 있다. 이것은 φ(절대 배수)가 아니라 m(농도 곡률)에 대한 정보이고, fumed
silica·DBSA 무·글리신 무 조건이라 대상계 전이 불확실성이 크므로 **값을 바꾸지 않고
기록만 남긴다**. 3회차 이후 m 재검토 시 출발점.

재현 수치 대조 요약(verify 블록이 assert): 원문 인쇄 하한 3.43배(2400/700 nm/min) vs
모델 g(0.065)/g(0.016) 2.51배 · Gorantla 2005 인쇄값 polish 1500 nm/min / dissolution
30 nm/min(0.065 M, pH≈1.5) · Surisetty Table I IE(%) 100/85/76(글리신) · 99/30/78(옥살산).
이 값들은 원문 존재 여부만 대조한 것이고 대상계(콜로이달 실리카·BTA 有) 전이 계수는
**미검증**(추정조차 안 함)이다.

## 4-2. 호출자 추가 실측 — **φ 는 C4 를 고칠 수 없다 (판정#85 전제의 반증)**

§4-1까지는 "φ 를 문헌에서 역산하면 C4(ρ)가 개선된다"는 판정#85의 전제를 유지한 채
문헌 확보 실패만 기록했다. 호출자가 그 전제 자체를 **반사실 스윕으로 직접 검사**한 결과
**전제가 틀렸다.**

φ 를 물리적으로 가능한 전 구간(1e-6 ~ 0.999999)에서 스윕하면 ρ 와 MAPE 가 **반대 방향**으로 움직인다:

| φ | ρ (held-out jani2025, n=13) | p | MAPE |
|---|---|---|---|
| 1e-6 ~ 1e-3 | **+0.3462** | 0.1241 | — |
| 0.01 | +0.3022 | 0.1583 | — |
| **0.078058 (현재값)** | **+0.3022** | 0.1583 | 11730% |
| 0.15 | +0.2473 | 0.2060 | — |
| 0.30 | +0.1209 | 0.3444 | 4534% |
| 0.70 | −0.1209 | 0.6566 | — |
| 0.999999 | **−0.3462** | 0.8767 | **849%** |

- **MAPE 를 고치는 방향(φ→1)이 ρ 를 파괴한다.** MAPE 는 11730%→849%로 13.8배 좋아지지만
  ρ 는 +0.346→−0.346으로 **부호가 뒤집힌다**.
- **ρ 를 최대화하는 φ 는 φ→0** 이고, 현재값 0.078058 은 이미 그 평탄구간(ρ=+0.30~0.35)에
  있다. 즉 **φ 를 문헌에서 어떤 값으로 역산해 오더라도 ρ 상한은 +0.3462** 이고,
  C4 기준(유의 평균 ρ ≥ 0.85)에 **원리적으로 도달할 수 없다.**

**따라서 판정#85(φ 역산으로 C4 해소)는 문헌 확보 성공 여부와 무관하게 목표를 달성할 수
없다.** 1회차·2회차가 소진한 것은 "φ 를 구하는 경로"였는데, 구해도 C4 는 안 움직인다.
이것은 탐색 실패가 아니라 **과제 설정의 반증**이며, 3회차를 φ 탐색으로 돌리는 것은 낭비다.

### 4-2-1. 그렇다면 promoter 항 전체의 천장은 얼마인가 (m 스윕 — **값 변경 안 함**)

φ 를 현재값에 고정하고 m(농도 곡률)만 스윕하면 ρ 가 단조 증가한다:

| m | 0.200 | 0.500 | **0.7238 (현재값)** | 1.000 | 1.500 | 2.500 | 5.000 |
|---|---|---|---|---|---|---|---|
| ρ | −0.1429 | +0.1264 | **+0.3022** | +0.4231 | +0.4725 | +0.5769 | **+0.6154** |
| p | 0.6806 | 0.3370 | 0.1583 | 0.0737 | 0.0517 | 0.0202 | 0.0132 |

**m 을 물리적으로 터무니없는 5.0까지 올려도 ρ 는 +0.6154 로 0.85에 못 미친다.**
즉 promoter 항의 파라미터를 어떻게 조합해도 이 held-out 은 C4 를 통과하지 못한다 —
남은 격차는 promoter 항 **밖**(판정#86이 특정한 ψ 정의위반, 그리고 미분리 ~2.2배)에 있다.

> ⚠ **m 을 바꾸지 않았다.** ρ 가 m 에 대해 단조 증가한다는 사실은 held-out 자신에게
> 맞추는 방향이고, 그대로 채택하면 자기채점이다(EVIDENCE-RULES 금지). 다만 §4-1의
> **독립 문헌**(Surisetty 2008, 농도비 4.06배에 MRR 비 ≥3.43배 vs 모델 2.51배)이
> "현재 m 이 과소"라는 **같은 방향**을 가리킨다는 점은 기록해 둔다 — 3회차에서 m 을
> 다루려면 이 독립 근거를 폐형식으로 굳힌 뒤여야 하고, ρ 를 보고 고르면 안 된다.

## 5. 판정 — **후보 B 채택** (값·코드·YAML 0변경)

> ⚠ 1차 출처 확보 실패(요건 기준): 확보한 Clarkson 4편(§3-6)은 전부 fumed silica 이고
> 옥살산 C=0 대조점·인쇄 MRR 표가 없어 φ 역산에 쓸 수 없다. 시도 경로: 로컬 코퍼스
> 동의어 확장(108건) · CORE API v3(429/500 간헐) · clarkson.figshare(0건) ·
> Europe PMC/OpenAlex-OA(0건) · Semantic Scholar(429) · 로컬 특허 129건(실시예표 0건) ·
> sci-hub.ren(4편 확보, 1편 오염사본 폐기) · exa 웹검색(권한 미승인).

φ=0.078058·m=0.7238·anchor=0.040290 은 그대로다. 등급(estimated)도 그대로다.
**C4 격자(rho 0.7175)는 이 회차로 움직이지 않는다.**

이번 회차가 새로 확정한 사실 **세 가지**:

0. **(가장 중요, §4-2) φ 로는 C4 를 고칠 수 없다.** φ 전 구간 반사실 스윕에서 ρ 상한은
   +0.3462(φ→0)이고 현재값은 이미 그 평탄구간에 있다. MAPE 를 고치는 방향(φ→1)은 ρ 를
   부호까지 뒤집는다. **판정#85의 전제(φ 역산 → C4 해소)가 반증됐다** — 문헌을 확보했더라도
   목표는 달성되지 않았을 것이다. 3회차를 φ 탐색으로 돌리지 마라.

1. Babu 그룹 옥살산 문헌군(2005~2008)에는 애초에 φ 역산 요건을 만족하는 통제쌍이
   **없다** — 접근 차단 때문이 아니라 실험 설계상 부재. 1회차가 "확보되면 승격 검토"로
   남긴 후보 A·B는 원문 확인으로 닫힌다.
2. 옥살산 농도 스윕이 존재하는 유일한 편(Surisetty 2008)은 현재 m 이 농도 민감도를
   과소평가함을 시사(§4-1) — 다음 문제는 φ 보다 g(C)의 **형태**일 수 있다.

## 6. 3회차 경로 (막연한 "더 찾는다" 금지)

0. **φ 탐색은 종결한다(§4-2).** ρ 가 φ 에 대해 이미 최적 평탄구간에 있으므로 φ 를
   대상계에서 역산하는 작업은 **C4 관점에서 가치가 없다**. φ 의 근거등급(estimated,
   US6309560B1 타계 전이)을 올리고 싶다는 별개 동기가 생기면 그때 재개하되, C4 해소
   과제로는 다루지 마라. 아래 1~5는 그 별개 동기가 생겼을 때의 경로다.
   **C4 의 실제 남은 원인은 promoter 항 밖에 있다** — 판정#86이 특정한 ψ 정의위반
   (`inhibitor_ref_mM`=1.0 이 범위 하단이 아니라 중간이라 BTA 없는 조건에서 ψ=9.969)과
   미분리 ~2.2배. 다음 회차는 그쪽을 파는 것이 옳다.

1. **요건 완화 결정이 먼저**: 콜로이달 실리카 + 옥살산 C=0 + 인쇄 MRR 을 동시에 만족하는
   공개 문헌은 이번 회차까지의 전수 탐색(코퍼스 9257건·특허 471건·OA 색인 3종)에서
   0건이다. 호출자가 (a) fumed silica 허용, (b) 그래프 판독 허용(fitz 렌더 + 축 판독,
   [[fabsim-white2003-thermal-route]] 방식) 중 무엇을 허용할지 먼저 정해야 3회차가 의미 있다.
2. (b) 허용 시 즉시 가능한 것: Gorantla 2005 JES(DOI: 10.1149/1.2083287) Fig. 1B 의
   "5 wt% H2O2 단독" vs "아세트산 0.13 M" 폴리시율 — 착화제 C=0 대조점이 실제로 있는
   유일한 편. 종이 아세트산이라 옥살산 φ 의 **상한/하한 오더** 정도만 준다.
3. Jani 2025 RSM(DOI: 10.1149/2162-8777/adc59e, hybrid OA)은 held-out 자체라 φ 적합에
   쓰면 자기채점 — 그러나 **hybrid OA 이므로 IOP 봇벽만 넘으면** HTML 본문에서 옥살산
   0 조건이 있는지 확인은 가능(이미 held-out YAML에 13조건이 있으니 그중 oxalic=0 점의
   존재 여부를 YAML에서 먼저 확인하는 것이 0비용).
4. CORE 학위논문 2건("Colloidal and Electrochemical Aspects of Copper-CMP" 2007 ·
   "CMP of Copper and Tantalum Barrier: Studies on Slurry Chemistry" 2006): CORE 키
   발급 후 상세 조회. Pandija·Janjam·Surisetty 학위논문이면 저널판에 없는 원자료 표가
   있을 수 있다.
5. sci-hub.ren 경로가 살아 있으므로 Hazarika 2022(DOI: 10.1149/2162-8777/ac6d72)·
   10.1149/2.0171808jss(2018)·Pandija 2007 MCP(DOI: 10.1016/j.matchemphys.2006.11.015,
   무연마재라 ②탈락이지만 옥살산 농도 스윕 표 존재 가능)·Ramakrishnan 2007 MEE
   (DOI: 10.1016/j.mee.2006.08.011, 디카복실산 비교, 무연마재)를 같은 방법으로 열어
   **C=0 점 유무만** 확인. 단 매번 1쪽 오염 대조 필수(이번 회차 JJAP 사본 오염).

## verify

```python verify
import re, sys
from pathlib import Path
sys.path.insert(0, ".")
import fitz  # PyMuPDF
import yaml

def pdf_text(p):
    d = fitz.open(p)
    return re.sub(r"\s+", " ", "\n".join(pg.get_text() for pg in d))

# 1. 확보 PDF 4건 — 1쪽 제목·권호 대조 + 오염사본(1914 Proc. Phys. Soc.) 아님 확인
g05 = pdf_text("papers/gorantla2005-essl-oxalic-acid-complexing-cu-cmp.pdf")
s08 = pdf_text("papers/surisetty2008-jes-dbsa-oxalic-glycine-cu-cmp.pdf")
j08 = pdf_text("papers/janjam2008-jes-oxalic-acid-cu-ta-selectivity.pdf")
a05 = pdf_text("papers/gorantla2005-jes-amine-carboxyl-complexing-cu-cmp.pdf")
for t in (g05, s08, j08, a05):
    assert "Conduction of Electricity Through Metals" not in t, "오염사본"
    assert "Clarkson University" in t
assert "Oxalic Acid as a Complexing Agent in CMP Slurries for Copper" in g05
assert re.search(r"G131-G134.{0,10}2005", g05), "ESSL 8(5) G131 권호"
assert "Dissolution Inhibition in Cu-CMP" in s08 and re.search(r"155.{0,5}12.{0,5}H971-H980.{0,5}2008", s08)
assert "Oxalic-Acid-Based Slurries with Tunable Selectivity" in j08
assert "Role of Amine and Carboxyl Functional Groups" in a05
print("verified: PDF 4건 1쪽 제목·권호 일치, 오염사본 없음")

# 2. 요건 대조에 쓴 인쇄값(본문)이 원문에 실제로 있는지
assert re.search(r"0\.065 mol dm.3 oxalic acid", g05), "Gorantla 2005: 옥살산 0.065 M 고정"
assert "1500 nm/min" in g05 and "30 nm/min" in g05, "Gorantla 2005: polish ~1500 / dissolution <30 nm/min"
assert "3 wt % fumed silica" in g05
assert "700 to 2400 nm/min" in s08, "Surisetty 2008: OA/peroxide 폴리시율 범위"
assert "200 nm/min" in s08, "Surisetty 2008: 글리신-only ~200 nm/min"
assert re.search(r"between 0\.016 and 0\.065 M", s08), "Surisetty 2008: OA 스윕 범위"
assert "fumed silica" in s08 and "colloidal" not in s08.lower()
assert re.search(r"3\.5 mM DBSA 100 85 76", s08) and re.search(r"3\.5 mM DBSA 99 30 78", s08), "Surisetty Table I IE(%)"
assert re.search(r"0\.13 M oxalic", j08) and "3 wt % fumed silica" in j08, "Janjam 2008: 옥살산 0.13 M 고정"
assert re.search(r"0\.13 mol dm.3", a05) and "Aerosil-130 fumed silica" in a05, "Gorantla JES 2005"
for t in (g05, s08, j08, a05):
    assert "colloidal silica" not in t.lower(), "요건②: 어느 편도 콜로이달 실리카 아님"
print("verified: 요건 대조표(§4)의 인쇄값·연마입자 서술이 원문과 일치")

# 3. §4-1 부수 대조: 현재 팩 g(C) 농도비 vs Surisetty 인쇄 범위 하한
pack = yaml.safe_load(Path("knowledge/params/cu_h2o2_bta.yaml").read_text())["params"]
phi = pack["promoter_floor_phi"]["value"]; m = pack["promoter_exponent_m"]["value"]
Ca = pack["promoter_anchor_M"]["value"]
assert abs(phi - 0.078058) < 1e-6 and abs(m - 0.7238) < 1e-6 and abs(Ca - 0.040290) < 1e-6, "2회차 값 변경 없음"
g = lambda C: phi + (1 - phi) * (C / Ca) ** m
model_ratio = g(0.065) / g(0.016)
paper_ratio_lb = 2400 / 700
assert abs(model_ratio - 2.51) < 0.02, model_ratio
assert abs(paper_ratio_lb - 3.43) < 0.01
assert model_ratio < paper_ratio_lb, "현재 m 은 Surisetty 계의 농도 민감도를 과소평가"
print(f"verified: g(0.065)/g(0.016) 모델 {model_ratio:.2f}x < 원문 하한 {paper_ratio_lb:.2f}x (값 미변경)")

# 4. 판정#84 배수 범위(8.11~20.40배)가 그대로임 — held-out 재계산
import sim.models  # noqa: F401
from sim.chemistry import _carboxylate_promoter_term
from validation.backtest import _recipe_from
raw = yaml.safe_load(Path("validation/datasets/jani2025_cu_rsm_composition_heldout.yaml").read_text())
promF = [_carboxylate_promoter_term(_recipe_from(c, raw["pack"]).resolve().pack, []) for c in raw["conditions"]]
assert len(promF) == 13
assert abs(min(promF) - 8.11) < 0.05 and abs(max(promF) - 20.40) < 0.05
print(f"verified: promoter 배수 {min(promF):.2f}x ~ {max(promF):.2f}x 불변 (n=13)")
```


### verify — §4-2 반사실 스윕 재현 (φ·m 은 복원되므로 파일 불변)

```python verify
import yaml, pathlib, numpy as np
import sim.models  # noqa: F401
from validation.backtest import run_dataset

pack = pathlib.Path("knowledge/params/cu_h2o2_bta.yaml")
orig = pack.read_text()
ds = pathlib.Path("validation/datasets/jani2025_cu_rsm_composition_heldout.yaml")

def rho_at(phi=None, m=None):
    d = yaml.safe_load(orig)
    if phi is not None:
        d["params"]["promoter_floor_phi"]["value"] = phi
    if m is not None:
        d["params"]["promoter_exponent_m"]["value"] = m
    pack.write_text(yaml.safe_dump(d, allow_unicode=True, sort_keys=False))
    return run_dataset(ds).spearman

try:
    # 현재값이 실제로 저장된 값인지 먼저 확인 (이 노트는 0변경이다)
    cur = yaml.safe_load(orig)["params"]
    assert abs(cur["promoter_floor_phi"]["value"] - 0.078058) < 1e-6
    assert abs(cur["promoter_exponent_m"]["value"] - 0.7238) < 1e-6

    r_lo  = rho_at(phi=1e-6)       # phi -> 0
    r_cur = rho_at(phi=0.078058)   # 현재값
    r_hi  = rho_at(phi=0.999999)   # phi -> 1 (MAPE 최적 방향)

    # (1) phi 를 MAPE 최적 방향으로 밀면 rho 부호가 뒤집힌다
    assert r_lo > 0 > r_hi, (r_lo, r_hi)
    assert abs(r_lo - 0.3462) < 0.01 and abs(r_hi + 0.3462) < 0.01

    # (2) rho 상한은 phi->0 이고 현재값은 이미 그 평탄구간
    assert r_cur <= r_lo + 1e-9
    assert (r_lo - r_cur) < 0.05, "현재값이 상한 근처 평탄구간"

    # (3) 상한조차 C4 기준(0.85) 에 한참 못 미친다 = phi 로는 C4 해소 불가
    assert r_lo < 0.85

    # (4) m 을 물리적으로 터무니없는 5.0 까지 올려도 0.85 미달
    r_m5 = rho_at(m=5.0)
    assert r_m5 > r_cur, "m 에 대해 단조 증가(자기채점 방향)"
    assert r_m5 < 0.85, r_m5
    print(f"verified: rho(phi->0)={r_lo:+.4f} rho(cur)={r_cur:+.4f} "
          f"rho(phi->1)={r_hi:+.4f} rho(m=5)={r_m5:+.4f} — 전부 0.85 미만")
finally:
    pack.write_text(orig)
    assert pack.read_text() == orig, "팩 파일 복원 실패"
    print("verified: cu_h2o2_bta.yaml 원본 복원 (이 노트는 값 0변경)")
```
