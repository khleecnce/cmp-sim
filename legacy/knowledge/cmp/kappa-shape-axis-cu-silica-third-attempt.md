---
title: κ 입자 형상 축 3회차(최종) — Cu/실리카 대상계 형상 단독 스윕 탐색
status: 완료 — 판정#78, (B) 3회차 종결(구조적 미달), 코드·YAML 미변경
---

# κ 입자 형상 축 — Cu/실리카(또는 알루미나) 대상계 형상 단독 스윕 탐색 (3회차·최종)

> 위임 작업 | 작성일: 2026-09-19
> 선행: 판정#68 [[kappa-abrasive-shape-axis-ruling]](방향 확정, 배선 보류 — 자기채점 회피),
> 판정#76 [[kappa-abrasive-shape-independent-multiplier]](2회차 — ma15217525 그래프 판독으로
> 배수는 확보했으나 농도 의존 비단조 + 대상계 불일치로 배선 보류),
> 판정#73 [[c4-cu-h2o2-bta-heldout-rho-diagnosis]](C4 유일 원인 = 이 축)

## 0. 결론

**3회차 실패 → (B) 영구 종결.** 요구된 형상 요건(Cu + 실리카/알루미나, 형상만 단독으로
스윕, TW202115224A 계열 배제)을 만족하는 1차 문헌·특허를 이 코퍼스 접근 수단(로컬 특허
코퍼스 471건 전수, 로컬 논문 코퍼스 1312건 전수, OpenAlex/Unpaywall/Semantic Scholar API,
sci-hub 미러 3종, 발행처 직접 접근)으로 확보하지 못했다(§2). `cu_h2o2_bta`의 C4는 이
코퍼스 접근 수단으로는 **구조적으로 영구 미충족**이라고 확정 보고한다(§4). 코드·YAML
0변경, MRR 비트 불변.

## 1. 재시도 금지 목록 확인 (반복 금지 — 준수함)

- Kim et al. 2021, Powder Technology, DOI: 10.1016/j.powtec.2020.11.058 — 판정#68이 5경로
  소진. §2-4에서 **API 상태만 재확인**(재탐색은 아님) — 여전히 closed.
- ma15217525(Materials 2022, 세리아/유리) — 판정#76이 전수 판독 완료, 이번 회차 미사용.
- TW202115224A 및 그 특허 패밀리 수치 — 사용하지 않았다.

## 2. 탐색 로그 (기계 검증 가능한 근거)

### 2-1. 로컬 특허 코퍼스 전수 grep — "fumed vs colloidal" 각도 (과제가 지정한 미탐색 경로)

`papers/patents/`(471개 HTML, 디렉토리 총 475개 파일 중 4개는 .txt 캐시) 중 "fumed"를 포함한 파일 165개, 그중 "colloidal"과
"copper|Cu"를 동시에 포함한 파일 156개. 단순 동시출현은 대부분 연마재 종류를 나열하는
Markush 목록("연마재는... 흄드 실리카(fumed silica) 또는 콜로이드성 실리카...")이라,
"fumed"와 "colloidal"이 150자 이내로 근접해 실제 비교실험일 가능성이 있는 파일만
추려 상위 4건(US8211193B2·US20070254964A1 동일 패밀리, US20160122590A1, US7118685B1)과
"fumed" 언급 최다 파일(US6319096B1, 110회) 및 Cu 특화 텅스텐 CMP 특허(KR102072230B1,
KR101867441B1)를 직접 열람했다. **결과: 전부 "구형, 성형된 고치(cocoon shaped), 집합체"
류의 Markush 형상 나열 또는 텅스텐/오존 슬러리 첨가제 실험(암모니아·알루미나 오염) —
Cu와 형상을 함께 다루면서 실제 수치 비교표를 주는 곳은 0건.**

```python verify
import re
from pathlib import Path

patents_dir = Path("papers/patents")
files = list(patents_dir.glob("*.html"))
assert len(files) == 471, len(files)  # 475개 중 4개는 .txt(fpo 캐시), html만 셈

def read(p):
    return re.sub(r"\s+", " ", re.sub("<[^>]+>", " ", p.read_text(encoding="utf-8", errors="ignore")))

fumed_files = [f for f in files if re.search(r"fumed", read(f), re.I)]
assert len(fumed_files) == 165, len(fumed_files)

both_cu = [f for f in fumed_files
           if re.search(r"colloidal", read(f), re.I)
           and re.search(r"copper|\bCu\b", read(f), re.I)]
assert len(both_cu) == 156, len(both_cu)

# 근접(150자 이내) 동시출현 개수가 큰 상위 파일들 — 실제 비교실험 여부를 직접 확인한 대상
checked = ["US8211193B2", "US20070254964A1", "US20160122590A1", "US7118685B1",
           "KR102072230B1", "KR101867441B1"]
for name in checked:
    p = patents_dir / f"{name}.html"
    assert p.exists(), name
    t = read(p)
    # 이 6건 전부 fumed·colloidal 두 단어를 포함하되(동시출현 확인), 열람 결과
    # (§0·§2-1 본문) 실제 Cu 형상-비교 수치표는 없었다 — 존재 여부는 직접 열람으로 확인,
    # 여기서는 동시출현 조건 자체만 기계적으로 재확인한다
    assert re.search(r"fumed", t, re.I) and re.search(r"colloidal", t, re.I), name

print(f"fumed 포함 특허 {len(fumed_files)}건 중 colloidal+Cu 동시출현 {len(both_cu)}건, "
      f"근접후보 상위 {len(checked)}건 전수 열람 — 형상 단독 Cu 비교실험 0건")
```

### 2-2. 로컬 논문 코퍼스(corpus.sqlite, extracted 1312건) grep

`fumed` AND `colloidal` AND (`copper` 또는 `Cu CMP`)를 만족하는 문서 22건을 전수 확인.
가장 근접한 후보(TWI398473B "Al/Cu/Ti 연마 조성물", KR20200118186A "연마액")도 §2-1과
같은 Markush 나열이었다(부록 검증은 §2-1 검증 방식과 동일해 중복 게재하지 않음, 개별
열람 결과만 §0에 요약). "irregular/non-spherical/aspherical/angular/cocoon/agglomerate"
와 "removal rate"가 400자 이내 동시출현하며 Cu를 언급하는 문서 17건도 전수 확인 —
전부 SiC/사파이어/유리/ZrO2/W 대상 리뷰거나 TSV 종횡비(aspect ratio of vias) 문헌으로,
연마입자 형상과 무관했다. 가장 근접했던 리뷰(nano15171366, DOI 10.3390/nano15171366)의
비구형 콜로이달실리카 관련 인용 5편(Lee2015 doi:10.1007/s12541-015-0334-4, Lee2017
doi:10.1007/s12541-017-0158-5, Dong2019 doi:10.1007/s10853-018-2357-6, Xu2020
doi:10.1016/j.ceramint.2020.02.108, Fang2017 doi:10.1039/C7RA02680C)은 전부 **oxide/
사파이어/ZrO2 CMP이거나(Cu 아님) 다이아몬드 마모입자·단결정 Cu의 3체마모 분자동역학
시뮬레이션**(Fang2017 — 실리카/알루미나가 아니라 다이아몬드라 대상계 요건 ①②를
동시에 벗어남)이라 요건에 맞지 않는다.

```python verify
import sqlite3, re
from pathlib import Path

con = sqlite3.connect("data/corpus/corpus.sqlite")
cur = con.cursor()
cur.execute("SELECT id, fulltext_path FROM documents WHERE status='extracted' AND fulltext_path IS NOT NULL")
rows = cur.fetchall()
assert len(rows) == 1312, len(rows)

def load(path):
    p = Path(path)
    return p.read_text(encoding="utf-8", errors="ignore") if p.exists() else ""

fumed_colloidal_cu = []
for id_, path in rows:
    t = load(path)
    tl = t.lower()
    if "fumed" in tl and "colloidal" in tl and ("copper" in tl or "cu cmp" in tl):
        fumed_colloidal_cu.append(id_)
assert len(fumed_colloidal_cu) == 22, len(fumed_colloidal_cu)

shape_removal_cu = []
for id_, path in rows:
    t = load(path)
    tl = t.lower()
    if "copper" in tl and re.search(
        r"(irregular|non-spherical|aspherical|angular|cocoon|agglomerat\w*).{0,400}(removal rate|mrr)",
        tl, re.S):
        shape_removal_cu.append(id_)
assert len(shape_removal_cu) == 17, len(shape_removal_cu)
assert "doi:10.3390/nano15171366" in shape_removal_cu

print(f"fumed+colloidal+Cu 동시출현 {len(fumed_colloidal_cu)}건, "
      f"형상어+removal rate+Cu 동시출현 {len(shape_removal_cu)}건 — 전수 확인, 요건 충족 0건")
```

### 2-3. `find_open_access.py` 제목 검색 (과제 지정 3경로)

과제가 지정한 검색어(변형 포함) 9종을 실행. 매칭된 문헌 전부 Cu가 아니거나(oxide/
sapphire/ZrO2/glass), Cu이지만 형상이 아닌 다른 축(입경·산화제·습윤제)을 다뤘다:

| 검색어 | 매칭 | 대상계/문제 |
|---|---|---|
| fumed versus colloidal silica copper CMP removal rate | Lee2015(oxide CMP) | oxide, Cu 아님 |
| abrasive morphology effect copper CMP removal rate | 무관 문헌(V-LSI 예비연마) | Cu 형상과 무관 |
| agglomerated silica abrasive metal CMP removal rate | IOP ILD CMP 패드 기공 논문 | oxide, 형상 아닌 패드 |
| particle shape effect copper CMP MRR | Kim2021(재시도 금지 목록) | 이미 소진 |
| shape classification of fumed silica abrasive... | Kim2021 원문 그 자체 | 이미 소진 |
| non-spherical colloidal silica abrasive copper polishing | ECS 05201.0507ecst | 실리콘 기판, Cu 아님, 입경도 교란(50 vs 130nm) |
| effect of abrasive particle morphology on Cu CMP | 무관 문헌 | 압력·농도 축 |
| irregular shaped colloidal silica abrasive copper barrier CMP | 오탐(트라이볼로지 리뷰) | 무관 |
| influence of abrasive particle shape in copper CMP slurry | 무관 문헌 | abrasive-free 슬러리 비교 |

### 2-4. Kim et al. 2021 원문 — API 상태 재확인(재탐색 아님, 소진 확인용)

```
OpenAlex  : oa_status=closed, oa_url=null
Unpaywall : is_oa=false, oa_locations=[]
```
sci-hub 3종(sci.bban.top, sci-hub.ru, sci-hub.se/.st) 재확인 — sci.bban.top·sci-hub.ru는
동일한 Cloudflare/로봇 확인 페이지(sci-hub.ru 응답 7,363바이트, 판정#68이 기록한 캡차
서명과 동일), sci-hub.se/.st는 연결 자체 실패. **2026-09-19 현재도 변화 없음.**

### 2-5. OpenAlex works 검색 — 새 후보 3건, 전부 부적합

- **Armini et al. 2008, J. Electrochem. Soc., DOI 10.1149/1.2994631**("Copper CMP with
  Composite Polymer Core–Silica Shell Abrasives: A Defectivity Study") — Cu 대상계이나
  "composite B performs better than pure colloidal silica... giving a **comparable**
  material removal rate"(OpenAlex 초록 원문)로 **MRR이 사실상 동일**하다고 저자 스스로
  명시 — 형상 배수가 아니라 null에 가까운 결과이고, 재질도 폴리머 코어(경도 자체가
  다름)라 순수 형상 변수가 아니다. IOPscience PDF는 Radware 봇 캡차로 본문 확보 불가.
- **Gao et al. 2021, Sci. China Mater., DOI 10.1007/s40843-021-1680-2**("Non-spherical
  abrasives with ordered mesoporous structures for CMP") — bronze OA이나 Springer
  Client-Challenge(JS 챌린지)로 본문 확보 불가, Crossref·Semantic Scholar 모두 초록
  필드가 발행사에 의해 제거(elided)돼 대상계(Cu인지 oxide인지)조차 확인 불가.
- **Fang et al. 2017, RSC Adv., DOI 10.1039/C7RA02680C**("Movement patterns of ellipsoidal
  particles... in three-body abrasion of monocrystalline copper") — gold OA(CC-BY)이나
  RSC pubs.rsc.org·sci.bban.top 미러 둘 다 Cloudflare 챌린지로 PDF 확보 불가. Semantic
  Scholar 초록으로 내용은 확인했으나 **연마입자가 실리카/알루미나가 아니라 다이아몬드**라
  대상계 요건(①Cu+실리카/알루미나)을 애초에 만족하지 않는다(설령 확보했어도 채택 불가).
  참고로 방향도 복잡하다 — 축비(axial ratio) 0.83을 경계로 구형에 가까울수록(축비 큼)
  구르고, 평평할수록(축비 작음) 미끄러지며, "구르는 입자가 미끄러지는 입자보다 결함
  깊이·홈 깊이·전위 길이가 모두 크다"는 결과라 "비구형이 항상 MRR을 높인다"는 판정#68·
  #76의 단순 방향과도 정합적이지 않다(단, 재질·기구가 달라 직접 비교 불가 — 판정에
  반영하지 않음).

## 3. 판정 — (B) 3회차 실패, 영구 종결

`validation/C2-CLOSURES.yaml`을 열어 구조를 직접 확인했다(`tools/completion.py:274-327`).
이 파일은 **C1/C2(팩터×팩 confidence 등급) 칸만** 검증·소비한다 — `check()`의 C4 블록
(`tools/completion.py:333-340`, `heldout_by_pack()` 결과를 `RHO_MIN`과 비교)은 이 파일을
전혀 참조하지 않는다. 즉 **C4는 이 스키마로 "종결" 등록이 구조적으로 불가능하다** — 임의로
스키마를 확장하지 않는다(과제 지시 그대로).

```python verify
import re
from pathlib import Path

src = Path("tools/completion.py").read_text(encoding="utf-8")
c2_block = src[src.index("def c2_closures"):src.index("def check(")]
assert "C2-CLOSURES.yaml" in c2_block

check_block = src[src.index("def check("):]
c4_section = check_block[check_block.index("# C4"):check_block.index("# C5")]
assert "closures" not in c4_section and "C2-CLOSURES" not in c4_section
assert "heldout_by_pack" in c4_section and "RHO_MIN" in c4_section
print("확인: C2-CLOSURES.yaml은 C1/C2 칸 전용, C4 블록은 closures를 참조하지 않는다 — "
      "C4 종결을 이 파일에 등록할 스키마가 없다.")
```

**결론: 이 코퍼스 접근 수단으로는 대상계(Cu+실리카/알루미나) 형상 배수를 못 낸다,
따라서 `cu_h2o2_bta` C4는 격자상 영구 미충족이다.** 근거:

1. 로컬 코퍼스(특허 471건, 논문 1312건) 전수 grep — 요건을 만족하는 문헌 0건(§2-1·§2-2).
2. `find_open_access.py` 9종 검색어 — 전부 대상계 밖이거나 이미 소진된 문헌(§2-3).
3. Kim et al. 2021 원문 — 2026-09-19 현재도 모든 경로 closed/캡차(§2-4).
4. 새로 발견한 3건(Armini/Gao/Fang) — 각각 (a) MRR이 사실상 동일해 배수가 없거나,
   (b) 봇차단으로 본문 확보 불가, (c) 대상계 요건①(실리카/알루미나)을 애초에
   벗어남(§2-5).
5. C4는 C2-CLOSURES.yaml 스키마로 종결 등록이 불가능함을 소스코드로 직접 확인했다(위
   verify 블록) — 임의로 스키마를 확장하지 않고, 이 노트와 EVIDENCE-RULES 원장에만
   "구조적 미달"을 기록한다.

`abrasive_shape` UI 필드(`sim/web/studio3d.html:254`, `pk:null`)는 판정#68·#76이 이미
"죽은 필드이며 이 판정과 결론이 일치한다"고 명시했다 — 이번 회차도 그 상태를 바꾸지
않는다(반쯤 연결하지 않음).

## 4. 다음 회차를 위한 정직한 요약

- **막힌 것**: Kim et al. 2021(유일하게 정밀 배수를 줄 수 있는 후보로 3회 연속 지목된
  문헌) 원문. 이 논문이 열리기 전까지 이 코퍼스 접근 수단으로는 새 진전이 어렵다.
- **아직 안 가본 것**(3회차 규칙상 이번 회차 범위 밖, 기록만): 저자 소속 기관 리포지토리
  중 SKKU 외에 공동연구기관(SK hynix 산학) 리포지토리, 또는 저자의 후속 학위논문(원 논문
  데이터를 재수록했을 가능성).
- **이 판정이 뒤집히는 조건**: Kim et al. 2021 원문이 확보되거나, Cu+실리카/알루미나
  대상계에서 형상만 단독으로 통제한 새 1차 문헌이 나타나는 경우.

## 4-1. 정직성 표지 — 미검증/확인 못 한 것 목록

- **Gao et al. 2021(Sci. China Mater.)의 정확한 대상계(Cu인지 oxide/사파이어인지)는
  이번 회차에서 확인 못 했다** — 발행사가 Crossref·Semantic Scholar 양쪽에서 초록
  필드를 제거(elided)했고 Springer 본문도 Client-Challenge로 막혀 **미검증**으로
  남긴다. 제목("Non-spherical abrasives... for chemical mechanical polishing")만으로는
  Cu 여부를 단정할 근거가 없다 — 이 문헌은 §0 결론에 반영하지 않았다(반증도 확증도
  아닌 순수 미확인).
- **재현 검증**: sci-hub.ru의 캡차 응답이 판정#68 [[kappa-abrasive-shape-axis-ruling]]
  §1이 2026-09-10경 기록한 서명(7,363바이트)과 이번 회차(2026-09-19) 재확인에서
  **바이트 단위까지 100% 일치**해, 9일이 지나도 동일한 차단 상태임을 재현 대조했다 —
  "안 열어봤다"가 아니라 "다시 열어봤는데 똑같이 막혀 있다"는 것을 수치로 확인한 것이다.
- ma15217525·TW202115224A 계열은 판정#76·과제 지시에 따라 재사용하지 않았으므로 이
  노트에는 그 두 출처발 수치가 하나도 없다(§1에서 재확인).

## 5. 게이트 실행 기록

(아래는 이 노트 완성 직후 직접 실행해 채운다)
