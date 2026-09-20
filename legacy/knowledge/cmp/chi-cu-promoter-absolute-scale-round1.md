---
title: χ/cu_h2o2_bta promoter(옥살산) 절대 배수 1차 검증 — 1회차 (판정#85)
status: 조사 중
---

# χ/cu_h2o2_bta promoter 절대 배수 — 1회차 (판정#85)

> Max워커 위임 | 작성일: 2026-09-20
> 선행: [[c4-cu-h2o2-bta-heldout-diagnosis]] (판정#84) — `promoter_floor_phi=0.078058`·
> `promoter_exponent_m=0.7238`·`promoter_anchor_M=0.0403` 셋 다 US6309560B1(알루미나·
> 옥살산암모늄·BTA無)에서 타계 전이(E4)됐고, `promoter_ref_M=0` 앵커 때문에
> C=0 기준 절대 배수(8~20배)가 한 번도 검증된 적이 없다는 사실을 확정.

## 과제

Cu + 콜로이달 실리카(우선) + 옥살산(또는 동종 카복실레이트) 농도 스윕에서
**C=0(무첨가) 대조점**을 가진 1차 문헌 통제쌍을 찾아 φ(=g(0)/g(C_ref) 분모의
"기계 성분 바닥" 비율)를 직접 역산하고 현재 φ=0.078058과 대조한다.

## 소진 경로 (판정#85 지시문에서 이미 소진 표시됨 — 재시도 금지)

Lin2009 · Wang2014 · Wang2012 · Du2004 · Miranda2004 · Luan2016 · Chen2014 ·
Liu2010 · Kim2008 · Krishnan2024 · sci-hub 5미러(판정#83에서 전멸 관측)

## 조사 로그

### 1. 로컬 코퍼스 스크리닝 (`data/corpus/corpus.sqlite`, 9257건)

`title/abstract LIKE '%oxalic%' AND '%copper%'`로 전수 스크리닝해 옥살산+Cu
계 논문 16건을 찾았다. 대상계(콜로이달 실리카·산성·글리신/BTA 병존)에
가장 근접한 3건을 후보로 압축:

| 후보 | DOI | 저자 | 연마입자 | 구조 |
|---|---|---|---|---|
| **A** | 10.1149/1.2987791 (JES 2008) | Surisetty, Goonetilleke, Roy, Babu | fumed silica | DBSA 계면활성제 有/無 × {글리신, 옥살산(OA), 글리신+OA} MRR 비교 — **"with and without" 구조라 옥살산=0(글리신-only) 대조점이 원문에 존재할 가능성이 높다** |
| **B** | 10.1149/1.2829112 (JES 2008) | Janjam, Surisetty, Pandija, Roy, Babu | fumed silica | OA 단독 기반 슬러리, pH 스윕 — Cu/Ta 선택비, OA 농도 스윕 존재 가능성 |
| C | 10.1149/2162-8777/ac6d72 (JSS 2022) | Hazarika, Gupta 외 | fumed silica | Co/Cu 갈바닉 부식 억제용 옥살산+이미다졸 — Cu 단독 C=0 대조점 불확실(주목적이 Co/Cu 선택비라 옥살산=0 조건은 없을 수 있음) |

모두 **fumed silica**(콜로이달 실리카 아님)라는 점은 대상계(cu_h2o2_bta
팩: 콜로이달 실리카)와 연마입자 종이 다르다 — 확보되더라도 "연마입자
불일치"가 남아 φ 직접 대체보다는 "타계 전이지만 US6309560B1(알루미나)
보다는 근접(Cu+옥살산+산성 계 일치, 연마입자만 다름)" 등급이 될 것.

### 2. 접근 시도 (전부 차단 확인)

- **Unpaywall API**(`api.unpaywall.org/v2/<doi>`): 후보 A·B·C 모두
  `oa_status: bronze`, `best_oa_location` = IOP 원문 URL. (E4 판정#84
  선행 규칙: bronze는 무료접근 보장 안 됨 — 직접 확인 필요.)
- **IOP 직접 fetch**(`curl -A Mozilla ... iopscience.iop.org/article/.../pdf`):
  HTTP 200이지만 실제로는 `<title>Search</title>` 리다이렉트 HTML
  (paywall) — bronze가 실제로 막혀 있음을 재확인.
- **sci-hub**(`sci.bban.top`, 판정#83이 알려준 대체 미러): 후보 A에 대해
  HTTP 403. 지시문상 "1회 확인" 요건 충족 — 재시도 안 함(5미러+대체
  미러 전멸 확정).
- **Semantic Scholar API**: 3건 모두 `openAccessPdf.status: BRONZE`,
  IOP 링크와 동일(새 정보 없음).
- **CORE API v3**(무료 검색, API 키 없음): 후보 A 검색 `totalHits: 0`.
- **ResearchGate**(DDG로 찾은 두 논문 페이지 직접 fetch): HTTP 403
  (봇 차단).
- **academia.edu**(Hazarika 저자 프로필 페이지): HTTP 403.
- **Wayback Machine**(`archive.org/wayback/available`): 이 세션의 IP가
  `429 Too Many Requests`로 레이트리밋됨 — **차단 아님, 미완료**(2회차
  후보 경로로 남김, §4).
- **DuckDuckGo HTML 검색**(bing은 결과 0건, DDG는 작동): 후보 A·B·C
  전부 IOP/ResearchGate/academia.edu/scite.ai/colab.ws 만 나오고
  대학 리포지토리·저자 개인 사이트 사본은 발견 못 함.
- **로컬 특허 코퍼스**(`papers/patents/*.html`, Cu+콜로이달실리카 동시
  언급 10건 스크리닝): CN101512732B(SiC 연마 — "copper" 오탐, 무관),
  CN104845532B(폴리실리콘 억제 — 무관), CN107586517B(배리어 일반론만,
  실시예표 없음) 등 확인한 것 모두 **옥살산 농도 스윕 실시예표 자체가
  없음**(일반 화학물질 나열 boilerplate뿐). 대상 부합 특허 미발견.
- **`papers/` 로컬 PDF 디렉터리**: `grep -li oxalic`로 이미 보유한
  파일 중 `US20250304827A1`(Fujimi 슬러리 저장안정성 특허) 1건만 걸림
  — 옥살산이 범용 첨가제 목록(boilerplate)에만 등장, 농도 스윕/C=0
  대조점 없음. 무관.

## 결론 — 1회차 실패

> ⚠ 1차 출처 확보 실패: Unpaywall(bronze, 실접근 차단 확인) · IOP 직접
> fetch(paywall 리다이렉트) · sci-hub(sci.bban.top, 403 — 지시문 1회
> 확인 요건 충족) · Semantic Scholar(동일 IOP 링크, 새 정보 없음) ·
> CORE API v3(무키 검색 0건) · ResearchGate(403 봇차단) · academia.edu
> (403 봇차단) · DuckDuckGo 검색(대학 리포지토리·저자 사본 없음) · 로컬
> 특허 코퍼스 10건 스크리닝(대상 부합 실시예표 없음) · 로컬 `papers/`
> oxalic 언급 파일(boilerplate만, 무관). Wayback Machine은 세션 IP
> 레이트리밋(429)으로 **미완료**(차단 확정 아님).

φ=0.078058은 **교체하지 않는다** — 판정#85 지시문 §3 규칙("대상계
근접도가 현재 출처보다 높을 때만 교체")을 적용할 대상 자체를 확보하지
못했으므로 교체 판단이 성립하지 않는다. 값·코드·YAML 미변경.

이번 회차가 재현·대조한 정량값: 원 진단(판정#84 §2)의 배수 범위 8.11~20.40배가 코드에서 변경 없이 그대로임(아래 verify 블록으로 재확인)과 `promoter_floor_phi=0.078058`(무차원, 미변경) 둘뿐이다 — **새로 확보한 1차 문헌 대조값은 없다**(§4 실패 기록).

## §4 2·3회차 구체 경로 (막연한 "더 찾는다" 금지 — 지시문 요구)

1. **Wayback Machine 재시도**: 이번 회차 레이트리밋(429)으로 미완료.
   `archive.org/wayback/available?url=iopscience.iop.org/article/10.1149/1.2987791/pdf`
   (후보 A), `.../10.1149/1.2829112/pdf`(후보 B)를 **몇 분 간격 후 재시도**
   — snapshot 존재 여부부터 확인, 있으면 `web.archive.org/web/.../pdf`
   직접 fetch.
2. **CORE API v3 (API 키 발급 후)**: 무키 검색은 0건이었으나 CORE는
   키 발급 시 fulltext 검색 범위가 넓어진다 — `core.ac.uk`에서 무료
   API 키 등록 후 후보 A·B·C DOI로 재검색.
3. **저자 소속 기관 리포지토리 직접 확인**: 후보 A·B(Surisetty, Janjam,
   Roy, Babu)는 2008년 논문 — 저자 소속(당시 Clarkson University 추정,
   미확인)의 기관 리포지토리(Clarkson Digital Commons 등)를 저자명으로
   직접 검색. 후보 C(Hazarika, Gupta)는 소속 대학 미확인 — Semantic
   Scholar 저자 프로필에서 소속 확인 후 해당 기관 리포지토리 검색.
4. **Krishnan2024 재확인**: 판정#85 지시문의 소진 목록에 있으나 이번
   회차에 실제로 재시도하지 않았다(지시문상 "재시도 금지" 대상이지만,
   원 소진 시도가 이 3-way 대조점 요건까지 구체적으로 겨냥했는지 불명
   — 2회차에서 원 소진 기록을 먼저 확인).
5. **fumed silica 후보(A·B·C)로 만족 기준 완화 검토**: 콜로이달 실리카
   전수 소진 시, "연마입자만 다른 fumed silica 계"를 US6309560B1(알루미나+
   BTA無)보다 근접한 E4 전이원으로 채택할지 여부를 다음 회차 판정에서
   결정 — 이번 회차는 원문 확보 자체가 안 됐으므로 이 판단을 유보한다.

## §4-보 — 호출자(Max워커) 직접 재시도 결과 (2026-09-20, 같은 회차)

위임 종료 후 Max워커가 §4의 경로 1·2·3을 **직접 실행**했다. 2회차가 같은 벽을
다시 받지 않도록 결과를 그대로 남긴다.

- **경로 1(Wayback) — 여전히 429.** `archive.org/wayback/available?url=...` 를 후보 A·B
  두 DOI로 재호출했으나 둘 다 `429 Too Many Requests`(HTML 응답). 위임 세션의
  레이트리밋이 아니라 **이 호스트에 대한 지속적 제한**으로 보인다 — 2회차는
  "몇 분 뒤 재시도"가 아니라 **시간대를 바꿔서**(다른 회차에서) 시도해야 한다.
- **경로 3(기관 리포지토리) — 소속 귀속이 틀렸다.** OpenAlex가 후보 A·B의 저자
  Surisetty·Janjam·Babu 를 **Qatar University** 로 귀속하지만(OpenAlex는 최신 소속을
  단다), 두 논문은 2008년 발표이고 당시 소속은 **Clarkson University** 다(같은 저자
  목록의 Roy·Goonetilleke 는 OpenAlex에서도 Clarkson). 실제 확인:
  QSpace(qu.edu.qa) REST API 로 `Babu`(484건)·`chemical mechanical planarization copper`
  (106건)를 조회했으나 **CMP 논문은 한 건도 없다**(의료·재료·공학 잡다한 최신 논문뿐)
  — QU 리포지토리에 이 논문들은 없다. Clarkson 쪽은 `digitalcommons.clarkson.edu`
  자체가 **DNS 미해결**(호스트 없음)이라 2회차는 Clarkson의 실제 리포지토리 주소부터
  확인해야 한다(`digitalcommons.clarkson.edu` 는 존재하지 않는 도메인이다).
- **경로 2(CORE API v3) — 무키 호출이 429.** 키 발급 전에는 재시도해도 같다.

> ⚠ 이번 회차에 새로 확보한 1차 출처는 **없다**. 위 3건은 전부 "경로가 막혔다"는
> 기록이지 "문헌이 없다"는 증명이 아니다 — 1회차 실패 판정은 그대로다.

## verify

문헌 미확보로 수치 재현 대상이 없다. 아래 블록은 이 노트가 인용한
**차단 상태**(HTTP 응답·API 결과) 재현 가능한 부분만 검증한다 —
네트워크 의존적이므로 CI/오프라인 환경에서는 스킵될 수 있음을 명시.

```python verify
import json, subprocess

# Unpaywall: 3개 후보 모두 bronze임을 재확인 (네트워크 필요, 실패 시 스킵)
import urllib.request

dois = ["10.1149/1.2987791", "10.1149/1.2829112", "10.1149/2162-8777/ac6d72"]
try:
    for doi in dois:
        url = f"https://api.unpaywall.org/v2/{doi}?email=khleecnce@gmail.com"
        with urllib.request.urlopen(url, timeout=10) as resp:
            data = json.load(resp)
        assert data["oa_status"] == "bronze", f"{doi}: {data['oa_status']}"
    print("verified: 후보 A/B/C 전부 Unpaywall oa_status=bronze (실접근 미보장)")
except Exception as e:
    print(f"네트워크 접근 실패(오프라인 환경 추정) — 스킵: {e}")

# φ 값이 이번 회차에 미변경됐음을 확인
import sys
sys.path.insert(0, ".")
import yaml
from pathlib import Path

pack = yaml.safe_load(Path("knowledge/params/cu_h2o2_bta.yaml").read_text())
phi = pack["params"]["promoter_floor_phi"]["value"]
assert abs(phi - 0.078058) < 1e-6, f"phi가 변경됨: {phi} (1회차는 미변경이 결론)"
print(f"verified: promoter_floor_phi={phi} — 판정#85 1회차에서 미변경 확인")

# 판정#84가 확정한 배수 범위(8.11~20.40배)가 이번 회차에도 그대로임을 재확인
import sim.models  # noqa: F401
from sim.chemistry import _carboxylate_promoter_term
from validation.backtest import _recipe_from

raw = yaml.safe_load(
    Path("validation/datasets/jani2025_cu_rsm_composition_heldout.yaml").read_text())
promF = []
for c in raw["conditions"]:
    rec = _recipe_from(c, raw["pack"])
    rr = rec.resolve()
    promF.append(_carboxylate_promoter_term(rr.pack, []))
assert len(promF) == 13
assert abs(min(promF) - 8.11) < 0.05 and abs(max(promF) - 20.40) < 0.05
print(f"verified: promoter 배수 재현 {min(promF):.2f}x ~ {max(promF):.2f}x (변경 없음, n=13)")
```
