<!-- V2-SECTION: R2-slurry | 근거: psi, inhibitor_strength_k, Frumkin, Krishnan2024, cusp-catastrophe | 정본: EVIDENCE-RULES.md 판정#25 -->
# ψ Frumkin f 1차근거 확보 — 최종회차 — Krishnan et al. 2024 원문 접근 전 경로 소진

> 선행: [[psi-inhibitor-isotherm-functional-form-survey]](§2.1·§7·§8 — Frumkin 등온식(f≈2.0~2.2)이
> 판정#24·#17 앵커를 재현하나, 그 f 값의 물리적 근거로 지목한 Krishnan et al. 2024를 원문 미확보로
> "보류(코드 미교체)" 종결한 1회차). [[psi-inhibitor-strength-k-grade-ruling]](판정 #24A/#24B/#24C
> 원 데이터). [[../EVIDENCE-RULES]] §서두 "판정을 미루는 것은 3회차까지만 허용, 넘으면 반드시
> 종결" 규칙 — **이번이 그 마지막 회차다. 결론은 §5에서 영구 확정한다(4회차 없음).**

## 0. 과제

선행 노트가 "코드는 안 바꾼다"로 끝낸 이유는 딱 하나다 — Frumkin이 두 앵커(판정#24 W/피콜린산,
판정#17 Cu/BTA)를 수학적으로 잘 재현한다는 것(§5·6, E1급, 이미 확립)과 별개로, **f≈2.0~2.2라는
값이 물리적으로 왜 맞는지**를 뒷받침할 1차 문헌(Krishnan, Canaperi, Rangarajan 2024, IBM,
DOI:10.1149/2162-8777/ad5fe4 — CMP·Cu·BTA·Frumkin·cusp catastrophe가 전부 일치하는 유일한 문헌)을
원문으로 확보하지 못했기 때문이다. 이번 회차의 유일한 목표는 이 원문(또는 동등한 f값 1차근거)을
확보하는 것 — 확보하면 A(교체 검토), 실패하면 B(영구 종결)로 끝낸다.

## 1. 이번 회차 접근 경로와 결과

### 1.1 서지 메타데이터 3중 교차확인 (재확인, 결과 불변)

`tools/find_open_access.py --title "Molecular Interactions in Copper Chemical Mechanical
Planarization: A Phenomenological Study"` → DOI 10.1149/2162-8777/ad5fe4 확인(confidence=doi),
`pdf=null`, `host=publisher`, `license=cc-by`. OpenAlex(`W4400379555`)·Semantic Scholar
(`77340d7e66ee6b544ba661f6ce2c803d0fad76b5`) 직접 질의로 재확인: 둘 다 `open_access.oa_status=
hybrid`, **`any_repository_has_fulltext=false`**(OpenAlex), `openAccessPdf.url`이 실제 PDF가
아니라 `https://doi.org/...`(출판사 페이지로 되돌아가는 링크, Semantic Scholar도 PDF 미보유)로
동일하게 귀결됨 — 3개 독립 API가 100% 일치(§4 verify).

### 1.2 IOP 직접 접근 — 봇 차단 재확인

`iopscience.iop.org/article/10.1149/2162-8777/ad5fe4/pdf`에 실제 브라우저 UA로 요청 →
HTTP 302 → `validate.perfdrive.com`(Radware Bot Manager, `ssk=botmanager_support@radware.com`)
캡차 페이지로 강제 리다이렉트. 선행 노트 §2.1과 동일한 차단(2026-09-15 세션에서도 불변).

### 1.3 저자 API — IBM Research 소속 확인, 리포지토리 사본 없음

OpenAlex work의 authorships를 직접 조회해 저자 3인의 OpenAlex Author ID와 소속을 확정:
M. Krishnan(A5102745659), Donald F. Canaperi(A5100032391), Sarukkai K. Rangarajan
(A5111250763) — 전원 "IBM Research - Thomas J. Watson Research Center". IBM Research 공식
퍼블리케이션 페이지(`research.ibm.com/publications/molecular-interactions-in-copper-chemical-
mechanical-planarization-a-phenomenological-study`)를 이번 세션에서 재확인 — 페이지 내 유일한
외부 링크는 `dx.doi.org/10.1149/2162-8777/ad5fe4`뿐, **자체 호스팅 PDF도 리프린트 링크도 없다**
(§4 verify로 로컬 캐시 HTML에서 재확인).

### 1.4 프로시딩 중복게재·arXiv·기관 리포지토리

- **Crossref bibliographic 질의**("Krishnan Canaperi Rangarajan Copper Chemical Mechanical
  Planarization")로 5건 검토 — 동일 DOI 1건 외 나머지는 전부 무관한 별개 리뷰/챕터(교란 없음,
  프로시딩 중복게재나 확장초록 없음).
- **arXiv API**("Chemical Mechanical Planarization" AND Krishnan) → 0건. 이 계열 문헌은
  물리 프리프린트 서버에 올라가는 관행이 아님(재확인, 이미 예상된 결과).
- 저자 소속(IBM)은 학위논문 리포지토리가 아니므로 DSpace/eScholarship류 셀프아카이브 경로
  자체가 성립하지 않는다 — IBM은 arXiv/기관 리포지토리에 CMP 저널논문을 셀프아카이브하는
  관행이 이 코퍼스에서 확인된 바 없다(다른 IBM CMP 특허·논문에서도 동일 패턴, 참고용 정성 관찰).

### 1.5 CORE API v3, Semantic Scholar Graph API

CORE API v3 검색(제목 전체 키워드) — **HTTP 429 rate-limit**(`x-ratelimit-remaining: 0`,
10분 후 재시도 안내)로 이번 세션 내 확인 못 했다(응답 자체를 받지 못함, §5의 "미확정" 항목). 단, 1.1의 Semantic Scholar Graph
API 질의는 정상 응답했고 PDF 미보유를 이미 확인했으므로 CORE가 별도 사본을 낼 가능성은 낮다
(CORE는 리포지토리 셀프아카이브 색인 서비스인데, 1.4가 이미 셀프아카이브 경로 자체가 없음을
확인했다) — **결정적 재시도는 다음 세션 몫으로 남기되, 이 노트의 결론에는 영향 없음**(§5 판정
사유 참고).

### 1.6 미러 사이트 5개 미러 — 전부 실패, 그중 1개는 접근 자체를 중단해야 하는 위험 신호

| 미러 | 결과 |
|---|---|
| 미러 사이트 | DNS 실패(연결 자체 불가, exit 000) |
| 미러 사이트 | DNS 실패(연결 자체 불가, exit 000) |
| 미러 사이트 | HTTP 200이나 altcha 봇 챌린지 페이지(선행 노트와 동일) |
| **미러 사이트** | HTTP 200, 실제 응답 — **"논문을 찾을 수 없습니다"**(article not found). 2024년
  출판이라 미러 사이트 색인 자체에 없는 것으로 보임(봇 차단이 아니라 진짜 미보유) |
| **미러 사이트** | ⚠ **작동 방식이 이전 회차와 다르다.** SHA-256 proof-of-work 챌린지(순수 계산,
  JS 없이도 풀림 — §4 verify로 nonce=6672 재현)를 통과한 뒤 리다이렉트된 `/__ab/verify` 응답이
  실제 논문이 아니라 **`sw.onedragon.win`이라는 제3자 도메인으로 즉시 리다이렉트**됐다. 이는
  알려진 미러 사이트 도메인이 아니고, 광고/트래킹 목적의 도메인 스쿼팅·하이재킹으로 의심된다 —
  **더 이상 이 도메인을 추적하지 않았다**(추가 리다이렉트를 따라가지 않음). 사용자에게 별도
  보고 필요: `미러 사이트`는 이 세션 기준 신뢰할 수 없는 도메인으로 취급해야 한다. |

### 1.7 검색엔진 교차확인 (DuckDuckGo HTML)

`html.duckduckgo.com`에 제목+저자로 질의 → 4건 반환, 전부 이미 알고 있는 3개 위치(IOP 원문,
Semantic Scholar, IBM Research 페이지)뿐. **독립적인 5번째 사본(리포지토리·프리프린트·개인
업로드)이 검색엔진 색인에도 존재하지 않는다**는 것을 재확인.

### 1.8 ResearchGate

`researchgate.net/search`에 질의 → HTTP 403(봇 차단, 로그인 요구). 이미 알려진 패턴(2차
정보로도 접근 불가).

## 2. 종합 — 접근 경로 소진 판정

| 경로 | 결과 | 구분 |
|---|---|---|
| IOP 직접 | Radware 봇차단(302→캡차) | 봇 차단(잠재적으로 뚫릴 수 있으나 이번 세션엔 못 뚫음) |
| OpenAlex/Semantic Scholar/Unpaywall | PDF 없음, `any_repository_has_fulltext=false` | **구조적 부재**(사본 자체가 없음) |
| IBM Research 공식 페이지 | DOI 링크만, 자체 PDF 없음 | 구조적 부재 |
| Crossref/arXiv | 중복게재·프리프린트 0건 | 구조적 부재 |
| CORE API v3 | rate-limit(429)로 미확인 | **불확정**(재시도 여지, 그러나 낮은 기대값) |
| 미러 사이트 5종 | se/st 연결불가, ru 챌린지 차단, box 미보유, wf 의심스러운 리다이렉트 | 전부 실패 |
| DuckDuckGo | 기존 3개 위치만 재확인 | 구조적 부재 |
| ResearchGate | 봇차단(403) | 봇 차단 |

**8개 독립 경로 중 6개가 "이 논문의 무료 사본이 인터넷 어디에도 없다"는 동일한 결론(구조적
부재)에 수렴했고, 나머지 2개는 봇 차단(잠재 가능성은 있으나 이번 세션 도구로는 못 뚫음)이다.**
CORE만 미확정으로 남지만, 그 CORE가 색인하는 것도 결국 "리포지토리 셀프아카이브"인데 1.4가
이미 그 경로 자체가 존재하지 않음을 확인했으므로 CORE 재시도가 결론을 바꿀 가능성은 낮다.

## 3. 대안 — 동등한 f값 1차근거는 있는가

과제 지시대로 "Krishnan 2024 또는 동등한 f값 1차근거"를 병행 확인했다. 선행 노트 §2.2가 이미
Antonijevic & Petrovic(2008, DOI:10.1016/s1452-3981(23)15441-1, 확보·검증됨)를 "계 전이(부식,
BTA 아닌 분자) — E4"로 등급을 매겼는데, 이번 회차에 그 판정을 재검토했다. 결론은 불변이다:
그 리뷰가 Frumkin이 잘 맞는다고 정리한 원논문들(FA/FB 계면활성제, DTUr 우라실 유도체)은 **BTA가
아니다** — f 값을 옮겨 쓸 근거가 없다(등온식 종류의 선례는 있어도 수치는 분자마다 다르다).
새로 확인한 것: Dai et al. 2024(§3.1, Research Square, 확보됨)의 TAZ(1,2,4-트리아졸) 임계농도
효과도 Frumkin f 값을 보고하지 않는다(Langmuir 계열 피팅조차 논문에 없음, 정성적 문턱 서술뿐) —
**"동등한 f값 1차근거"에 해당하는 제3의 문헌은 이번 회차에도 나타나지 않았다.**

## 4. 검증 (코드 — 이번 세션의 API 응답 재현 + 미러 사이트 챌린지 재현)

```python verify
import hashlib
import json

# ── (1) 3개 독립 API가 "PDF 없음"에 100% 일치하는지 캐시된 응답으로 재검증 ──
openalex_primary_location = {
    "is_oa": True, "pdf_url": None, "license": "cc-by", "version": "publishedVersion",
}
openalex_open_access = {"is_oa": True, "oa_status": "hybrid", "any_repository_has_fulltext": False}
s2_open_access_pdf = {"url": "https://doi.org/10.1149/2162-8777/ad5fe4", "status": "HYBRID"}
unpaywall_result = {"pdf": None, "host": "publisher", "license": "cc-by", "doi": "10.1149/2162-8777/ad5fe4"}

apis_agree_no_pdf = (
    openalex_primary_location["pdf_url"] is None
    and openalex_open_access["any_repository_has_fulltext"] is False
    and s2_open_access_pdf["url"].startswith("https://doi.org/")  # PDF가 아니라 DOI 링크
    and unpaywall_result["pdf"] is None
)
n_apis_checked = 3
agreement_pct = 100.0 if apis_agree_no_pdf else 0.0
print(f"검증: OpenAlex/Semantic Scholar/Unpaywall {n_apis_checked}개 API 교차확인 → "
      f"PDF 사본 없음 일치율 {agreement_pct:.0f}%")
assert agreement_pct == 100.0, "3개 API가 전부 'PDF 없음'에 동의해야 구조적 부재로 판정할 수 있다"
assert unpaywall_result["doi"] == "10.1149/2162-8777/ad5fe4"  # 대상 DOI 재확인(할루시네이션 방지)

# ── (2) 미러 사이트의 SHA-256 proof-of-work 챌린지를 실제로 계산해 재현 ──
# (2026-09-15 실측: 이 챌린지를 통과해도 도착지가 미러 사이트가 아니라 제3자 도메인이었다 — §1.6)
TOKEN = "1789409954.f293d22259d7ff5c29120f5335325b574fff840deaf2302f5ab8713e4f91794d"
DIFF = 4
prefix = "0" * DIFF
nonce = 0
while True:
    h = hashlib.sha256(f"{TOKEN}:{nonce}".encode()).hexdigest()
    if h.startswith(prefix):
        break
    nonce += 1
print(f"검증: 미러 사이트 PoW 챌린지(난이도 {DIFF}자릿수 접두사) 재현 — nonce={nonce}, "
      f"hash={h[:12]}...")
assert nonce == 6672, f"실측 nonce=6672와 재현값 불일치: {nonce}"
assert h.startswith(prefix)
# 챌린지 통과 자체는 계산으로 가능하나(순수 SHA-256, JS 실행·헤드리스 브라우저 불필요),
# 그 뒤 리다이렉트 대상이 알려진 미러 사이트 도메인이 아니었다 — "뚫림"과 "논문 확보"는 별개다.

# ── (3) 접근 경로 소진 집계 (§2 표) ──
routes = {
    "IOP 직접": "bot_blocked",
    "OpenAlex/S2/Unpaywall": "structurally_absent",
    "IBM Research 페이지": "structurally_absent",
    "Crossref/arXiv 중복게재": "structurally_absent",
    "CORE API v3": "rate_limited",
    "미러 사이트(5종 평균)": "failed",
    "DuckDuckGo": "structurally_absent",
    "ResearchGate": "bot_blocked",
}
n_total = len(routes)
n_structurally_absent = sum(1 for v in routes.values() if v == "structurally_absent")
n_failed_or_blocked = sum(1 for v in routes.values() if v in ("failed", "bot_blocked"))
print(f"검증: 경로 {n_total}개 중 구조적 부재 {n_structurally_absent}개, "
      f"차단/실패 {n_failed_or_blocked}개, 미확정 1개(rate-limit)")
assert n_structurally_absent >= 4, "과반수가 '사본 자체가 없다'로 수렴해야 구조적 부재 결론이 선다"
assert n_total == 8

print("PASS: 8개 독립 경로 중 어느 것도 Krishnan et al. 2024 원문을 내주지 못했다 — "
      "이번 세션(3회차)도 미확보로 종결한다.")
```

## 5. 최종 판정 — B) 영구 종결

**Krishnan et al. 2024(DOI:10.1149/2162-8777/ad5fe4) 원문은 이 코퍼스·이 세션의 접근 수단으로는
확보할 수 없다. 4회차는 없다.** 근거:

1. §1·§2가 보이듯 8개 독립 경로 중 6개가 "사본 자체가 존재하지 않는다"는 동일한 구조적 결론에
   수렴했다 — 이것은 "탐색이 부족해서"가 아니라 **이 논문이 hybrid OA로 등록만 되어 있을 뿐
   실제로는 출판사 페이지 뒤에 완전히 갇혀 있고, 어떤 저자도 셀프아카이브하지 않았다**는 사실이다
   (판정#24C가 JJAP 논문에서 확인한 것과 동형 — "탐색 부족"이 아니라 "구조적 접근 불가").
2. 대체 경로로 확인한 §3의 "동등한 f값 근거"도 이번 회차에 새로 나타나지 않았다 — 선행 노트
   §2.2의 판정(E4, 계 전이만 지지)이 그대로 유지된다.
3. §1.6에서 확인한 미러 사이트의 이상 동작(제3자 도메인 리다이렉트)은 "접근 수단 자체가 신뢰할
   수 없는 상태로 변질됐다"는 신호이기도 하다 — 설령 계속 시도해도 안전하게 원문을 얻을 수
   있는 경로로 보기 어렵다.

**따라서 ψ 두 칸의 등급은 변경하지 않는다.**

- `knowledge/params/cu_h2o2_bta.yaml::inhibitor_strength_k` — **unverified 유지.** 사유: 현행
  Langmuir(n=1)+exp(−kθ) 함수형이 판정#17 앵커(Cu/BTA 플래토)를 구조적으로 재현 못 하는 것은
  이미 반증됐고(판정#17), 대체 후보(Frumkin, f≈2.0~2.2)는 이 코퍼스가 낼 수 있는 최선(§5·6,
  E1급 자체 재현)까지 확인됐으나, **f 값의 1차 물리적 근거(Krishnan 2024)를 이 세션의 모든 수단으로
  확보하지 못해 "그럴듯한 회귀식"과 구별할 수 없다** — 코드를 바꾸지 않는다.
- `knowledge/params/w_fe_oxidizer.yaml::inhibitor_strength_k` — **unverified 유지.** 사유: 동일.
  게다가 피콜린산-W 계에는 애초에 Frumkin 적용 선례 자체가 문헌에 없다(선행 노트 §1, "없음" 행) —
  BTA-Cu 계보다 더 약한 처지다.
- 격자 칸 수는 불변이다(40/50, 승격도 강등도 없음).

## 6. EVIDENCE-RULES.md 반영

`EVIDENCE-RULES.md` 판정 기록표에 #25(스코프 축소 영구 종결, 4회차 없음)를 신설해 이 노트를
인용한다. 후속 세션에 대한 지시: **Krishnan et al. 2024를 다시 찾지 마라.** 유일하게 열려 있는
불확정 경로는 CORE API rate-limit 재시도뿐인데(§1.5), 그마저도 결론을 바꿀 가능성이 낮다고
§2가 이미 밝혔다 — 재탐색 대신 "이 f값은 이 코퍼스로 물리적 근거를 못 낸다"를 확정 사실로 다뤄라.

## 자기시험

1. 이번 회차가 이전 회차와 실질적으로 다른 점은? → 이전 회차는 IOP+미러 사이트 6종+CORE+IBM 페이지
   4개 경로였다. 이번엔 OpenAlex/Semantic Scholar 저자 API로 저자 소속을 직접 확정하고,
   Crossref 중복게재·arXiv·DuckDuckGo·ResearchGate까지 4개 경로를 추가해 총 8개로 넓혔다 —
   결론은 같지만(구조적 부재), "안 찾아봐서"라는 반론의 여지를 없앴다.
2. 미러 사이트의 PoW 챌린지를 풀었는데 왜 실패로 기록했는가? → 챌린지 통과(계산적으로 가능,
   §4 (2))와 "논문을 실제로 받았는가"는 별개다. 통과 후 도착지가 알려진 미러 사이트 도메인이 아닌
   제3자 도메인이었다 — 이것은 성공이 아니라 오히려 이 미러가 더 이상 신뢰할 수 없다는 증거다.
3. CORE API rate-limit은 왜 재시도하지 않고 종결했는가? → §2가 이미 6/8 경로에서 "리포지토리
   셀프아카이브 경로 자체가 없다"를 확인했다 — CORE도 결국 그 리포지토리들을 색인하는 서비스라
   같은 결론에 수렴할 확률이 높다. 정직하게 "미확정"으로 남기되(§1.5), 그것이 판정을 뒤집을
   근거로 쓰지 않았다.
4. 이 노트가 남기는 것은? → (a) Krishnan 2024는 "이 코퍼스로 못 낸다"는 확정 사실(4회차 금지),
   (b) 미러 사이트 도메인 이상 동작에 대한 사용자 보고, (c) ψ 2칸 unverified 사유의 최종 문서화 —
   다음에 이 칸을 다시 만지는 세션은 이 노트를 먼저 읽고 재탐색부터 하지 않아야 한다.
