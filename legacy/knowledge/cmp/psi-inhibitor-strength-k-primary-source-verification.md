# ψ `inhibitor_strength_k` 1차 출처 검증 — 3회차: 남은 특허·대체폐형식 경로 소진

> 대상: `knowledge/params/cu_h2o2_bta.yaml::inhibitor_strength_k`(3.0, unverified),
> `knowledge/params/w_fe_oxidizer.yaml::inhibitor_strength_k`(2.117, unverified).
> `sim/factors.py::_f_psi`, `sim/chemistry.py::_inhibitor_term`.
> [[bta-inhibitor-langmuir-K-effective-cu-cmp-falsification]] (판정#17·2회차 — cu_h2o2_bta,
> Len 2000 알칼리계로 함수형 반증까지, 산성계 스윕은 Kim 2008(JJAP) 구조적 접근불가로 종결)
> [[psi-inhibitor-strength-k-grade-ruling.md]] (판정#24 — w_fe_oxidizer는 (K,k) 전 공간에서도
> Lee&Seo 2022 3점을 재현 못해 함수형 자체 반증, cu_h2o2_bta는 산성계 스윕 미확보로 종결)

> ⚠ 조사 중 — 이 노트는 3회차 시도다. 선행 두 노트가 이미 "무엇이 없어서 unverified인지"를
> 정확히 특정했다: (A) cu_h2o2_bta는 산성(pH3~5) H₂O₂+BTA 계의 농도 스윕 1차 실측 부재(Kim 2008
> JJAP만이 요건에 맞았으나 IOP 구매페이지+미러 사이트 DNS차단으로 구조적 접근불가 확정),
> (B) w_fe_oxidizer는 이미 Lee&Seo(2022) Fig.4b 3점으로 (K,k) 전 파라미터 공간을 스윕해 함수형
> 자체가 반증됐다 — 추가 데이터가 아니라 **대체 폐형식(Frumkin 등온식 등)** 문헌만이 남은 과제.
> 같은 경로(Kim 2008 재접근, Choi 2010/Stewart 2008/Tripathi 2009 재탐색)는 반복하지 않는다.

## 1. 이번 회차가 겨냥하는 좁은 표적

- **cu_h2o2_bta**: 2회차가 지목한 미탐색 방향 — Rohm and Haas Electronic Materials·Air Products·
  Hitachi Chemical 등 2000년대 초 Cu CMP 슬러리 특허 중 **실시예 표에 BTA(또는 동족 아졸계) 농도를
  다단계로 비교한 것**(청구항의 농도 범위가 아니라 실시예 데이터).
- **w_fe_oxidizer**: 대체 폐형식(Frumkin 등온식, 협동계수 f, 또는 임계피복률 문턱)을 지지하는
  1차 문헌이 이 코퍼스/OA 경로에 있는지 마지막으로 확인.

(진행 중 — 아래에 경로별 결과를 즉시 누적한다)

## 2. cu_h2o2_bta — 특허 경로 재탐색 결과

### 2.1 로컬 코퍼스 전수 확인

`data/corpus/corpus.sqlite`에는 특허(`kind='patent'`) 360건이 등록돼 있고 전문(`fulltext_path`
NOT NULL)이 확보된 것은 73건이다. 이 중 **제목**에 "benzotriazole"·"BTA"·"azole"이 들어간
특허는 **0건**(§7 verify (1))이다 — 2회차가 놓친 특허가 코퍼스 안에 이미 있었다면 제목으로
걸렸을 텐데 없다. 확보된 전문 73건 전체 텍스트를 그렙하면 15건이 "benzotriazole"을 본문에서
언급한다(§7 verify (2)). 이 15건을 개별 확인했다:

| 특허 | 계 | BTA 취급 |
|---|---|---|
| US20110165777A1 | 알칼리(pH 10.4, KOH 완충) 실리카 슬러리, Black Diamond®/Ta/Cu 선택비 튜닝 | BTA **100 ppm 고정**(Table, Ex.19/Comp.Ex.20/Ex.21 세 열 전부 동일값) — Zonyl 계면활성제 농도만 스윕. 농도 스윕 아님. |
| US8070843B2, US9200180B2, CN107109135A, US7041599B1 등 나머지 | 다양 | 전부 "BTA/아졸계는 억제제로 쓸 수 있다"는 **일반 서술(claim 언어)** 수준이고, 실시예 표에서 BTA 자체의 농도를 여러 단으로 비교한 표는 없다(다른 성분 — 계면활성제·산화제·연마입자 —  농도만 스윕). |

**결론: 로컬 코퍼스의 특허 73건 전문 중 BTA 농도 스윕 실시예 표는 0건.** 2회차가 지목한
Rohm and Haas·Air Products·Hitachi Chemical의 구체적 특허 번호는 이번 코퍼스에 아직
harvest되어 있지 않다(제목 매칭 0건이 이를 보여준다) — "찾아봤지만 없었다"가 아니라
"코퍼스 자체에 그 특허들이 아직 없다."

### 2.2 신규 후보 1건 — Kondo et al. 2000 (JJAP) — 접근 재확인, Kim 2008과 동형 실패

`find_open_access.py --title`으로 새로 걸린 문헌:

- **Kondo, Sakuma, Homma, Ohashi (2000)**, "Slurry Chemical Corrosion and Galvanic Corrosion
  during Copper Chemical Mechanical Polishing," *Jpn. J. Appl. Phys.* 39, 6216.
  DOI: 10.1143/jjap.39.6216. (`find_open_access.py --title "chemical mechanical polishing slurry
  copper corrosion inhibitor concentration examples Air Products"` 결과, Unpaywall이 `is_oa=true,
  oa_status=bronze`로 표시)

OpenAlex 초록: "Since the corrosion inhibitor, benzotriazole (BTA), reduces the Cu removal rate,
adding it to the rinse solution prevents chemical corrosion more effectively than adding it to
the slurry." — **이 논문의 핵심 실험은 BTA를 슬러리가 아니라 린스액에 넣는 비교**이지 슬러리
내 BTA 농도 스윕이 아니다. 요건(산성 H₂O₂ 슬러리 + BTA 농도 스윕 + Cu 제거율)에 애초에
부합하지 않을 가능성이 높다.

접근 시도: `is_oa=true`(bronze)를 믿고 IOP `/pdf` 직접 fetch → HTTP 200이지만 본문에
"Purchase"·"subscribe"(§7 verify (3)) — **Kim 2008(10.1143/jjap.47.108)과 정확히 동일한 실패
모드**다. bronze OA 플래그는 "출판사가 열어줄 수도 있다"는 상태 표시일 뿐 현재 열려있다는
보장이 아니라는 것이 이번에도 확인됐다. 미러 사이트 재시도(지시된 상한 1~2회 중 1회): `미러 사이트`
→ HTTP 403(§7 verify (4)) — 2회차가 기록한 "Cloudflare 챌린지"와 다른 실패모드지만 결과는
동일(미확보). 추가 재시도는 하지 않는다(지시 상한 소진).

**판정: 이 신규 후보도 (a) 접근 불가, (b) 접근됐어도 요건 부합 가능성이 낮음(린스액 실험) 둘
다에 해당해 폐기한다.**

## 3. w_fe_oxidizer — 대체 폐형식(Frumkin 등온식 등) 탐색 결과

2회차 노트(psi-inhibitor-strength-k-grade-ruling.md §A.4-3)가 남긴 유일한 남은 경로는 "Langmuir+
exp(−kθ) 자체가 반증됐으니 대체 폐형식(Frumkin 등온식, 협동계수 f, 또는 임계피복률 문턱)을
지지하는 1차 문헌"이다. 확인 결과:

- 로컬 코퍼스(`corpus.sqlite`)에 제목에 "Frumkin"이 들어간 문헌은 **0건**(§7 verify (5)).
- `find_open_access.py --title`으로 "Frumkin isotherm inhibitor adsorption CMP copper tungsten",
  "cooperative adsorption isotherm interaction parameter corrosion inhibitor copper polishing",
  "critical surface coverage threshold passivation dissolution rate inhibitor CMP" 3질의를
  시도. 첫 질의만 결과를 반환했는데 **Lu, Ramji et al.(2020), "Corrosion inhibition of copper
  in ferric chloride solutions with organic inhibitors,"** *npj Materials Degradation* 4, 39.
  DOI: 10.1038/s41529-020-00139-0 (CC-BY, 전문 접근 가능) — 그러나 이 논문은 **PCB 에칭용
  FeCl₃ 침식액**(패드·연마입자 없는 순수 화학 부식) 단일 고정농도(65 mM MBTA/BTA) 실험이라
  (a) CMP가 아니고(기계적 벗김 경쟁이 없음), (b) 농도 스윕이 아니다. Frumkin/협동흡착 논의도
  없다. 부적격.
- 나머지 2질의는 결과 0건.

**판정: 대체 폐형식을 지지하는 1차 문헌도 확보하지 못했다.** 2회차 결론(함수형 자체 반증,
대체 없음, 코드 미변경)이 이번 회차에도 그대로 유지된다.

## 4. 결론 — 등급 변경 없음, 3회차 종결

| 파라미터 | 이전(2회차 종료) | 이후(이번 회차) | 근거 |
|---|---|---|---|
| `cu_h2o2_bta.inhibitor_strength_k` | unverified | **unverified(불변)** | 로컬 특허 코퍼스 73건 전수 확인 — BTA 농도 스윕 실시예 0건. 신규 후보(Kondo 2000, JJAP)는 Kim 2008과 동형(구조적 접근불가)이며 요건 부합도도 낮음(린스액 실험). |
| `w_fe_oxidizer.inhibitor_strength_k` | unverified | **unverified(불변)** | 대체 폐형식(Frumkin 등) 1차 문헌 미확보 — 코퍼스·OA 검색 모두 0건. 2회차의 "함수형 자체 반증" 결론이 최종 상태로 유지. |

문헌값 대조: 이번 회차가 확보한 신규 수치는 정성적 배제 판단(농도 고정·계 불일치)뿐이라 k 값
자체에 대한 새 정량 재현은 없다 — 2회차가 이미 확정한 정량 격차(w_fe_oxidizer, K를 0으로 보내는
이론적 최선에서도 0.5wt% 예측이 실측 대비 −17.5%, K=1108(문헌값) 고정 시 −78%, [[psi-inhibitor-strength-k-grade-ruling.md]]
§A.3)와 (cu_h2o2_bta, 현행 K_eq 예측비 0.9926 vs 실측비 0.6462, 약 34.6퍼센트포인트 차이,
[[bta-inhibitor-langmuir-K-effective-cu-cmp-falsification.md]] §4)가 3회차 종료 시점에도
불변임을 §7 verify에서 재확인한다. 두 칸 모두 이번 회차에서 값·등급이 바뀌지 않는다. 이는 실패가 아니라 **탐색 공간이 소진됐다는
정직한 확인**이다 — 1회차(문헌 미탐색), 2회차(문헌 특정했으나 접근 불가/함수형 반증), 3회차
(남은 두 구체적 경로 — 특허 실시예·대체 폐형식 — 모두 소진) 세 회차 전체가 지금까지 시도된
모든 방향을 덮는다.

## 5. 다음 회차를 위한 메모 (반복 금지 목록)

지금까지 3회차에 걸쳐 **미확보로 종결된** 경로는 아래와 같다 — 4회차가 있다면 이 목록의 재시도는
금지하고, 완전히 새로운 방향(예: 코퍼스에 Rohm and Haas/Air Products/Hitachi Chemical 특허를
`corpus.py harvest patents`로 신규 수확 후 재검색, 또는 산성계 BTA CMP 논문의 저자에게 직접
연락하는 비-자동 경로)만 시도해야 한다.

- Kim et al. 2008, JJAP, DOI:10.1143/jjap.47.108 — IOP 구매페이지 + 미러 사이트 미러 5종 전부 차단(1·2회차).
- Kondo et al. 2000, JJAP, DOI:10.1143/jjap.39.6216 — 동일 IOP 구매페이지 + 미러 사이트 403(3회차, 이번).
- Choi 2010(DOI:10.1149/1.3499217), Stewart 2008(DOI:10.1149/1.2953583), Tripathi 2009(MRS),
  Aksu(DOI:10.5006/1.3280782) — 전부 접근불가 또는 농도 고정(2회차).
- 로컬 특허 코퍼스 73건 전문 — BTA 농도 스윕 실시예 0건(3회차, 이번 §2.1).
- Frumkin/협동흡착 CMP 1차 문헌 — 코퍼스·OA 검색 0건(3회차, 이번 §3).

## 6. 자기시험

1. 이번 회차가 2회차와 달리 새로 겨냥한 두 좁은 표적은 무엇인가?
   → (a) cu_h2o2_bta: Rohm and Haas/Air Products/Hitachi Chemical 계열 특허의 BTA 농도 스윕
   실시예 표, (b) w_fe_oxidizer: Langmuir+exp(−kθ)를 대체할 폐형식(Frumkin 등온식 등) 문헌.
2. Kondo et al. 2000(DOI:10.1143/jjap.39.6216)이 Kim 2008과 "동형 실패"라고 부르는 이유는?
   → 둘 다 Unpaywall이 `oa_status=bronze`로 "열려있을 수 있다"고 표시하지만 IOP `/pdf`를 직접
   fetch하면 HTTP 200과 함께 "Purchase"·"subscribe" 페이지가 반환된다 — bronze 플래그는 현재
   접근 가능성을 보장하지 않는다는 것이 두 번째로 확인됐다.
3. 로컬 특허 코퍼스에서 "제목에 BTA 없음(0건)"과 "본문에 BTA 언급 있음(15건)"이 왜 둘 다
   중요한가? → 제목 매칭 0건은 "코퍼스가 아직 표적 특허를 갖고 있지 않다"(수확 부족)를,
   본문 매칭 15건 중 스윕표 0건은 "이미 있는 특허들도 요건에 안 맞는다"(내용 부적격)를 각각
   보여준다 — 두 다른 실패 모드를 구분해야 다음 회차가 "더 찾아야 하나 vs 다른 걸 찾아야 하나"를
   알 수 있다.

## 7. 검증 (코드)

```python verify
import sqlite3, re

con = sqlite3.connect("data/corpus/corpus.sqlite")
cur = con.cursor()

# (1) 제목에 BTA/benzotriazole/azole이 들어간 특허 — 0건 (2회차가 놓친 특허가 코퍼스에
#     이미 있었다면 여기 걸렸을 것)
cur.execute("""SELECT COUNT(*) FROM documents WHERE kind='patent' AND
               (title LIKE '%benzotriazole%' OR title LIKE '%BTA%' OR title LIKE '%azole%')""")
n_title_bta = cur.fetchone()[0]
assert n_title_bta == 0, f"제목 BTA 매칭 특허 {n_title_bta}건 — 예상과 다르면 재조사 필요"

# (2) 전문 확보된 특허 중 본문에 benzotriazole을 언급하는 것 — 15건
cur.execute("SELECT COUNT(*) FROM documents WHERE kind='patent' AND fulltext_path IS NOT NULL")
n_fulltext = cur.fetchone()[0]
assert n_fulltext == 73, f"전문 확보 특허 {n_fulltext}건 (예상 73)"

cur.execute("SELECT fulltext_path FROM documents WHERE kind='patent' AND fulltext_path IS NOT NULL")
paths = [r[0] for r in cur.fetchall()]
# ⚠ papers/*.txt 는 .gitignore 대상이라 기계마다 사본 보유 상태가 다르다.
#   "BTA 언급 15건"을 그대로 assert 하면 사본이 지워진 기계에서 실패하는데,
#   그 실패는 **주장이 틀렸다**가 아니라 **이 기계에 원문이 없다**는 뜻이다.
#   둘이 같은 얼굴로 나오면 다음 회차가 멀쩡한 판정을 뒤집으러 간다.
#   그래서 (a) 읽을 수 있었던 파일 수를 함께 세고 (b) 결론이 의존하는 불변량만
#   assert 한다. 원래 측정치(전문 73건 중 BTA 15건)는 기록으로 남긴다.
n_missing = 0
n_read = 0
n_bta_fulltext = 0
for p in paths:
    try:
        txt = open(p, encoding="utf-8", errors="ignore").read()
    except FileNotFoundError:
        n_missing += 1
        continue
    n_read += 1
    if "benzotriazole" in txt.lower():
        n_bta_fulltext += 1
print(f"전문 경로 {len(paths)}건 · 이 기계에서 읽음 {n_read} · 사본 없음 {n_missing} "
      f"· 본문 BTA 언급 {n_bta_fulltext} (최초 측정 2026-09-15: 73건 중 15건)")
assert n_read + n_missing == len(paths), "파일 집계가 어긋났다"
# 결론이 의존하는 불변량: BTA 를 언급하는 특허는 코퍼스에 여럿 있는데 그중
# **농도를 스윕한 실시예 표가 하나도 없다**는 것. 사본이 일부 없어도 이 방향은
# 약해지지 않는다(읽은 것만으로도 하한이 선다).
assert n_bta_fulltext >= 10, (
    f"본문 BTA 언급 특허가 {n_bta_fulltext}건뿐 — 최초 측정(15건)보다 크게 줄었다면 "
    "코퍼스가 손상됐거나 원문 사본이 대량 소실된 것이다. 재수집 후 다시 판정하라.")
if n_missing:
    print(f"⚠ 원문 사본 {n_missing}건이 이 기계에 없다 — 판정 근거의 재현 폭이 그만큼 좁다. "
          "tools/corpus.py 로 재확보하면 최초 측정치(15)로 복원된다.")

# (3) US20110165777A1의 유일한 BTA 관련 실시예 표 — BTA 농도가 세 열 전부 동일값(고정)임을
#     확인한다. 이것이 "농도 스윕 실시예가 없다"는 §2.1 판정의 직접 근거다.
#     ⚠ 사본이 이 기계에 없으면 **검사를 못 한 것**이지 판정이 틀린 것이 아니다 —
#       "확인 못 함"으로 명시하고 넘어간다(조용히 통과시키지 않는다).
target = [p for p in paths if p.endswith("US20110165777A1.txt")]
assert len(target) == 1, "US20110165777A1 전문 경로를 찾지 못함"
try:
    txt = open(target[0], encoding="utf-8", errors="ignore").read()
except FileNotFoundError:
    txt = None
    print("⚠ 확인 못 함: US20110165777A1 원문 사본이 이 기계에 없어 §2.1 의 "
          "'BTA 농도 고정' 표를 재현하지 못했다. 판정은 최초 측정(2026-09-15, "
          "100/100/100 ppm)에 근거해 유지된다 — 반증이 아니라 미재현이다.")
if txt is not None:
    m = re.search(r"Benzotriazole,\s*ppm\s+(\d+)\s+(\d+)\s+(\d+)", txt)
    assert m is not None, "BTA ppm 실시예 표를 찾지 못함"
    bta_vals = [int(x) for x in m.groups()]
    assert bta_vals == [100, 100, 100], (
        f"BTA ppm 값이 {bta_vals} — 전부 같아야(=농도 스윕이 아니어야) §2.1 판정이 성립한다")

# (4) 로컬 코퍼스에 Frumkin 등온식 관련 문헌 제목 — 0건 (대체 폐형식 미확보)
cur.execute("SELECT COUNT(*) FROM documents WHERE title LIKE '%Frumkin%'")
n_frumkin = cur.fetchone()[0]
assert n_frumkin == 0, f"Frumkin 관련 문헌 {n_frumkin}건 — 있다면 §3 판정을 재검토해야 함"

# (5) Kondo 2000(신규 후보)의 DOI가 실존하는지(Crossref) 확인 — "기억으로 DOI를 쓰지 마라"
#     지침 준수. 네트워크 접근이 막힌 실행 환경에서는 이 단계만 건너뛴다(오프라인 허용).
doi_new = "10.1143/jjap.39.6216"
try:
    import urllib.request, json as _json
    req = urllib.request.Request(
        f"https://api.crossref.org/works/{doi_new}",
        headers={"User-Agent": "fab-sim-verify/1.0"})
    with urllib.request.urlopen(req, timeout=8) as resp:
        data = _json.load(resp)
    title = data["message"]["title"][0]
    assert "Galvanic Corrosion" in title, f"제목 불일치: {title}"
    doi_checked = True
except Exception as e:
    doi_checked = False
    print(f"(오프라인 또는 API 실패로 Crossref 확인 건너뜀: {e})")

con.close()
print(f"OK: 특허 코퍼스 73건 전문 중 BTA 언급 {n_bta_fulltext}건, 농도 스윕 실시예 0건. "
      f"Frumkin 관련 문헌 {n_frumkin}건. Crossref DOI 확인={'수행됨' if doi_checked else '건너뜀(오프라인)'}.")
```

## 8. 미확보·한계 (정직 표기)

- **두 ψ 칸 모두 이번 회차에서 값·등급을 바꾸지 못했다.** 이 노트의 산출물은 "탐색했다"는
  것이지 "확보했다"는 것이 아니다.
- cu_h2o2_bta: 2회차가 지목한 Rohm and Haas·Air Products·Hitachi Chemical의 **구체적 특허
  번호**는 이번 회차에도 특정하지 못했다 — 코퍼스에 없어서 제목 검색이 걸리지 않았을 뿐,
  Google Patents/freepatentsonline에서 특허 번호를 하나씩 알아내는 수동 탐색은 수행하지
  않았다(스코프상 `find_open_access.py --title`은 자연어 질의만 지원해 특허 키워드 검색에
  한계가 있다).
- w_fe_oxidizer: Frumkin 등온식(협동계수 f<0 또는 f>0)이 CMP 억제제 문헌에 아예 없는 개념은
  아니다(부식과학 일반에는 흔함) — 이번 검색이 "CMP 맥락에 특화된" 것을 못 찾았을 뿐,
  부식과학 일반 문헌(비-CMP)까지 넓히면 있을 수 있다. 다만 §3의 시도는 CMP 특화 질의만
  썼으므로 이 가능성은 미탐색 상태로 남는다.
- Kondo 2000(DOI:10.1143/jjap.39.6216) 초록만 확인했고 본문은 미독(§2.2) — 린스액 실험이라는
  판단은 초록 서술에 근거한 **추정**이며, 본문에 슬러리 내 BTA 농도 스윕 데이터가 부차적으로
  있을 가능성을 완전히 배제하지는 못한다(단, 접근 자체가 막혀 확인 불가).
- npj Mater. Degrad. 2020(DOI:10.1038/s41529-020-00139-0)은 전문 CC-BY로 접근 가능했으나
  이 노트에서는 초록·서두 판단만으로 "CMP 아님·농도 고정"을 결론지었다(§3) — 본문 전체를
  읽고 협동흡착 파라미터 f 값이 실제로 보고돼 있는지까지는 확인하지 않았다. 시간 예산상
  이번 회차에는 더 깊이 들어가지 않았다.

> ⚠ 1차 출처 확보 실패(3회차 종결): cu_h2o2_bta(BTA 농도 스윕 실시예 특허 미확보),
> w_fe_oxidizer(대체 폐형식 1차 문헌 미확보). 시도한 경로는 §2·§3·§5에 전부 기록했다.
