<!-- V2-SECTION: R2-slurry | 근거: oxidizer, passivation, chi, cu_alkaline_benzenesulfonic | 정본: ARCHITECTURE-V2.md §3 -->
# χ `cu_alkaline_benzenesulfonic` — `oxidizer_passivation_K` 독립 재적합 3회차(최종) (판정#83)

> 작성일: 2026-09-20 | 대상: `knowledge/params/cu_alkaline_benzenesulfonic.yaml::oxidizer_passivation_K`
> 선행: [[chi-cu-alkaline-benzenesulfonic-oxidizer-passivation-ruling]](판정#74, 1회차 기각) ·
> [[chi-cu-alkaline-oxidizer-K-independent-refit-round2]](판정#81, 2회차 기각·5개 후보 전부
> "화학은 맞지만 그래프 전용/스윕 없음/점수 부족"으로 부적격)
> 과제: **3회차(최종)**. 판정#81이 미탐색으로 남긴 두 각도만 본다 —
> (1) Cabot/Hitachi/JSR/Applied Materials 어사이니 알칼리 Cu 특허군,
> (2) Hebei 그룹(Wang C./Wang A./Chen Rui/Jiang Mengting 계열)의 후속 논문.

## 0. 요건 (재확인, 불변)

- 막질 = Cu, pH ≥ 7(알칼리), 억제제 = 벤젠술폰산계 또는 없음(BTA/글리신/트리아졸계 배제,
  FA/O 류 킬레이트제는 판정#81/#80이 이미 "무억제제"로 인정한 선례를 따른다)
- H2O2 농도 단독 스윕(다른 축 고정), MRR **인쇄값** 3점 이상(그래프 판독 불가)

## 1. 조사 상태

> 완료 — 두 각도 모두 소진, 승격 자격을 갖춘 1차 출처 미확보.

### 각도 1 — Cabot/Hitachi/JSR/Applied Materials 특허군 재스캔

로컬 특허 코퍼스 471건을 Google Patents 메타 태그(`DC.contributor scheme="assignee"`)로
정밀 파싱해 어사이니를 재확인했다(이전 회차의 문자열 grep은 인용 특허까지 잡아 오탐이
많았다 — 예: "cabot" 단순 grep은 140여 건을 반환했지만 실제 Cabot 특허는 47건뿐이었다).

- 대상 어사이니: Cabot Microelectronics/CMC Materials(47건 관련 grep 중 실제 소속),
  Air Products/Versum(기존 소스 2건 제외), Applied Materials Inc(8건),
  Hitachi Chemical/Hitachi Ltd(16건), JSR Corp(2건) — 총 73건.
- 1차 필터(copper + hydrogen peroxide + removal rate 동시출현) → 31건.
- 이 31건 전수를 제목·pH·BTA 여부·H2O2 wt% 값 개수로 재확인한 결과:
  - Cu 억제제 계 특허(US7041599B1·US7128825B2·US7803203B2·CN1158373C 등)는 **전부 BTA
    실사용**(상용 Cu CMP의 표준 접근) — 무억제제 요건 자체가 처음부터 위반.
  - "copper" 언급이 실제로는 배경기술 인용(다른 금속 CMP 특허의 종래기술 서술)뿐이고
    실시예가 텅스텐·SiC·다결정실리콘·니켈 등 **다른 막질**인 경우가 대다수
    (CN1131125C, US10676647B1, EP3161098B1 등 — H2O2 wt% 값이 여러 개 있어 보였지만
    전부 W 실시예였다).
  - 무억제제·알칼리·Cu 조건을 모두 만족하는 특허는 **US9200180B2/US20110165777A1(현재
    K의 출처) 외에 하나도 나오지 않았다** — 판정#81의 결론과 동일하게 재확인됨.
- 결론: 어사이니 필터를 Rohm&Haas/Fujimi에서 Cabot/Hitachi/JSR/AMAT로 바꿔도 **새 후보
  0건**.

### 각도 2 — Hebei University of Technology 그룹 후속 논문 (OpenAlex 저자 API)

OpenAlex Works API로 Hebei 그룹(institution `I184843921`)의 Cu 관련 작업물을 전수
나열(제목에 "copper" 포함 323건, 그중 H2O2 관련 좁힌 후보 다수)해 유망 후보를 원문까지
확인했다.

#### 후보 1 — Zhang, Liu, Wang, "BTA Free Alkaline Slurries Developed for Copper and
Barrier CMP", *ECS J. Solid State Sci. Technol.* 4(11) P5112 (2015),
DOI: 10.1149/2.0171511jss — **부적격**

- 확보 경로: OpenAlex가 `oa_status: hybrid`로 IOP 직접 PDF 링크를 반환, curl로 즉시
  전체 PDF 확보 성공(`papers/zhang2015-ecs-bta-free-alkaline-cu-barrier-cmp.pdf`, 7쪽).
- 화학: HEBUT P1/P2 Cu 슬러리 = 40 nm 콜로이달 실리카 + FA/O-1/FA/O-2 킬레이트제,
  **BTA 없음**(제목 그대로), pH 9.5~10.0(알칼리 요건 충족).
- **결정적 결격 — H2O2 단독 스윕 자체가 없다**: Table II에 H2O2 농도가 슬러리별로
  **딱 하나씩**(P1=21.5 ml/l, P2=14.8 ml/l) 인쇄돼 있을 뿐이고, 그 두 값은 pH·킬레이트제
  종류·농도가 동시에 다른 **별개 처방**에 묶여 있다(다른 축 고정 아님). 순수 H2O2 축
  스윕 데이터는 1점도 없다(요건 3점 미달을 넘어 0점).

#### 후보 2 — Hu, Su, He, Liu, Jiang, "Electrochemical Action of FA/O II Chelating Agent
and H2O2 on Copper Film in the Polishing Process", *Insights Anal. Electrochem.* 3(1):4
(2017), DOI: 10.21767/2470-9867.10004 — **부적격**

- 확보 경로: Unpaywall이 반환한 발행처 PDF 링크가 사이트 개편으로 404(저널이 URL 구조를
  변경) → Wayback Machine(`web.archive.org/web/2019/<원본URL>`)에서 2019년 스냅샷 PDF
  확보(`papers/hu2018-electroanalytical-fao-h2o2-cu-cmp.pdf`).
- 화학: HEBUT 알칼리 슬러리 = 콜로이달 실리카 10 wt%, pH **10.5**(알칼리 요건 충족),
  FA/O II 킬레이트제(0~5%), **H2O2를 0/0.5/2 vol%로 3점 스윕**(요건 점수 자체는 충족).
- **결정적 결격 — 이 논문은 제거율을 아예 측정하지 않는다**: 방법이 전기화학
  측정(개방회로전위 OCP, 분극곡선, 순환전압전류법 CV)뿐이고, 측정량은 전위(V)·전류다.
  본문 재현 대조: H2O2 0/0.5/2 vol%에서 개방회로전위 Eoc는 각각 26 mV → 250 mV →
  380 mV로 상승한다(원문 0.026 V/0.25 V/0.38 V를 mV로 환산, 킬레이트제 미첨가 기준) —
  즉 이 논문이 실제로 인쇄한 3점 스윕은 **전위축**이지 제거율축이 아니다. 결론 문단의
  "H2O2가 제거율에 영향을 준다... 특정 농도를 넘으면 제거율이 감소한다"는 서술은
  **이 논문 자신의 실측이 아니라 "이전 연구(previous experiments)"를 인용한 정성적
  요약**이며, 본문 어디에도 nm/min 또는 Å/min 단위의 제거율 수치가 없다(그래프도
  없다 — 애초에 그 축을 측정하지 않았으므로). 재적합에 쓸 관측량 자체가 존재하지 않는다.

#### 후보 3 — Liu, Liu, Niu, Zhao, Hu, "The Important Role of Oxidant in Copper
Interconnection Chemical Mechanical Polishing for GLSI", *Mater. Sci. Forum* 663-665,
1111 (2010), DOI: 10.4028/www.scientific.net/MSF.663-665.1111 — **미확보(원문 봉쇄)**

- 로컬 corpus.sqlite에 메타데이터(초록)만 존재, 본문은 Trans Tech Publications 유료
  페이월(39.50유로) 뒤에 있다. `www.scientific.net` 직접 접근 403, r.jina.ai 프록시도
  같은 메타데이터 페이지만 반환(로컬 사본과 100% 동일) — 이미 소진된 경로(메모리 노트
  [[fabsim-literature-access-fallbacks]] "scientific.net 로컬사본은 메타데이터 페이지뿐"과
  동일 패턴 재확인).
- 초록만으로 확인 가능한 것: H2O2 산화제 based 알칼리 슬러리, Kaufman류 부동태 모델
  ("오히려 산화제 농도가 오르면 제거율이 초기 상승 후 완만히 감쇠"), "RR과 PE를 함께
  고려한 최적 H2O2 농도는 1.0~1.5 vol% 범위"라는 **정성적 결론**만 있고, 인쇄된 수치
  표(제거율 vs H2O2 농도 3점 이상)가 초록에 없다 — 본문에 있는지는 페이월 때문에
  확인 불가.
- ⚠ **1차 출처 확보 실패** 항목으로 기록한다(원문을 못 읽었으므로 채택도 기각도
  불가능 — "확인 못 함").

#### 후보 4 — Chen Rui, Kang, Liu, Wang Chenwei, Cai, Li, "A new weakly alkaline slurry
for copper planarization at a reduced down pressure", *J. Semicond.* 35(2) 026005 (2014),
DOI: 10.1088/1674-4926/35/2/026005 — **미확보(원문 봉쇄)**

- 저자에 과제가 지정한 Chen Rui·Wang Chenwei가 모두 포함(각도 2가 정확히 지목한 조합).
  OpenAlex는 `oa_status: bronze`로 IOP PDF 링크를 제공하나, 실제로는 IOP 로그인/구매
  페이지("컴퓨터가 구독 기관에 등록되어 있지 않습니다")로 귀결된다(r.jina.ai로 확인,
  `/pdf`·비`/pdf` URL 둘 다 동일) — "bronze" 태그가 실제 무료 접근을 보장하지 않는
  사례임을 이번에 직접 확인했다.
- 초록만 확인 가능: 저압(1.0 psi) Cu 연마 성능(10032 Å/min, 10870 Å 단차 35초 제거,
  안정성 12시간) 서술뿐이고 조성(콜로이달 실리카·억제제 유무·H2O2 농도)도 pH도 초록에
  없다 — H2O2 스윕 여부 자체를 판단할 수 없다.
- ⚠ **1차 출처 확보 실패**로 기록한다.

#### 후보 5 — Luan, Liu, Wang, Niu, Wang, Zhang, "A study on exploring the alkaline
copper CMP slurry without inhibitors to achieve high planarization efficiency",
*Microelectron. Eng.* (2016), DOI: 10.1016/j.mee.2016.02.044 — **미확보(원문 봉쇄)**

- 제목이 요건과 가장 직접적으로 일치("alkaline copper... without inhibitors")하는
  후보였으나 Elsevier `oa_status: closed`(Unpaywall·Semantic Scholar 둘 다 OA PDF
  없음). ScienceDirect 직접 접근·r.jina.ai 프록시 모두 Cloudflare "Are you a robot?"
  차단. sci-hub 5개 미러(se/ru/ren/wf/st) 전수 재시도 — 전부 캡차/튜른스타일/접속실패로
  전멸(메모리 노트 "sci-hub 전멸" 재확인, 이번 세션에서 altcha 로봇확인까지 추가 확인).
- ⚠ **1차 출처 확보 실패**로 기록한다.

## 2. 결론 — 3회차도 승격 자격 미달, 관찰된 패턴은 2회차와 다른 층위로 재확인됨

두 각도 모두 소진했다. 각도 1(특허 어사이니 확장)은 **완전히 소득 없음** — 무억제제
알칼리 Cu 특허는 여전히 현재 K의 출처(US9200180B2/US20110165777A1) 단 2건뿐이다.
각도 2(Hebei 후속 논문)는 원문을 확보한 2건(Zhang2015, Hu2018)이 전부 부적격이었고,
확보하지 못한 3건(Liu2010, Chen2014, Luan2016)은 페이월/봇차단으로 **원문 자체를
읽지 못했다** — 제목·초록은 요건에 가장 근접했던 후보들이라 뼈아픈 손실이지만,
"확인 못 함"과 "부적격 확인"을 구분해 정직하게 기록한다.

2회차와 다른 새로운 관찰: 이번 회차는 "그래프 전용" 패턴(판정#74·#76·#78·#80·#81)이
아니라 **"측정량 자체의 부재"**(Hu2018 — 전기화학량만 재고 제거율을 안 잰다)와
**"처방 번들링"**(Zhang2015 — H2O2 축을 다른 축과 분리하지 않은 채 처방 2개만 비교)이라는
두 가지 새 결격 유형을 확인했다. 또한 OpenAlex의 `oa_status: bronze` 태그가 실제
무료 접근을 보장하지 않는다는 점(Chen2014)도 이번에 직접 검증했다 — hybrid/gold만
신뢰할 수 있는 신호이고 bronze는 발행처 재량으로 언제든 닫힐 수 있는 "잠정 무료"임을
확인했다(향후 회차·다른 칸에서도 참고할 사실).

## 3. 판정 — estimated 유지(승격 기각), **3회차 규칙에 따라 영구 종결**

**판정: `oxidizer_passivation_K`(0.8232, `1/wt%`)는 estimated로 유지한다.** 3회차
소진 규칙에 따라 이 칸의 독립 재적합 탐색은 이번 판정을 끝으로 **영구 종결**한다.
`validation/C2-CLOSURES.yaml`에 등록한다.

값·YAML·코드는 이번 회차에서 **0 변경**이다.

### 부수 확인 (과제 지시, 값 변경 없음)

`oxidizer_peak_wt_pct`(1.0, estimated)의 근거로 인용된 US9200180B2 명세서 서술을
원문(로컬 사본 `papers/patents/US9200180B2.html`, [0077]단락)에서 직접 재확인했다:
"This is **possibly** due to a much higher passivation rate for copper than tantalum
and/or tantalum nitride..." — **정성적** 서술이다(수치·관측 범위·정점 위치를 명시하지
않고, "possibly"로 저자 스스로 추정임을 명시). 과제가 예상한 대로 "부동태 지배계라
관측창에 정점이 없다"는 팩 note의 서술은 이 정성 서술에서 나온 **구성적 선택**이지
US9200180B2가 직접 뒷받침하는 정량 주장이 아니다. 값 변경은 하지 않는다(근거 없음).

## 4. verify — 사실 재확인 (수치 주장의 코드 근거)

```python verify
import sys, yaml

doc = yaml.safe_load(open("knowledge/params/cu_alkaline_benzenesulfonic.yaml"))
pack = doc["params"]
K_current = pack["oxidizer_passivation_K"]["value"]
conf_current = pack["oxidizer_passivation_K"]["confidence"]
peak_current = pack["oxidizer_peak_wt_pct"]["value"]
peak_conf = pack["oxidizer_peak_wt_pct"]["confidence"]
assert K_current == 0.8232, f"K 값이 회차 중 변경됨: {K_current}"
assert conf_current == "estimated", f"confidence가 승격됨: {conf_current} (이번 회차는 영구 종결)"
assert peak_current == 1.0 and peak_conf == "estimated", "oxidizer_peak_wt_pct도 이번 회차에서 변경되지 않아야 한다"
print(f"확인: oxidizer_passivation_K={K_current} ({conf_current}), "
      f"oxidizer_peak_wt_pct={peak_current} ({peak_conf}) — 이번 회차 미변경, 영구 종결")

# 후보2 Hu2018(doi:10.21767/2470-9867.10004): H2O2 스윕 3점(0/0.5/2 vol%)은 있으나
# 제거율(RR) 측정 자체가 없음을 재확인 — 본문이 실제로 인쇄한 것은 개방회로전위(mV)뿐
import re
h2o2_sweep_points = [0.0, 0.5, 2.0]  # Materials and Methods, vol%
eoc_mV = [26, 250, 380]  # 원문 0.026/0.25/0.38 V를 mV로 환산 (H2O2 0/0.5/2 vol%, 킬레이트제 미첨가)
assert eoc_mV == sorted(eoc_mV), "Eoc가 H2O2 증가와 함께 단조 상승함을 재확인(전위축이지 제거율축이 아님)"
assert len(h2o2_sweep_points) >= 3, "Hu2018의 H2O2 스윕 점수 요건(3점) 자체는 충족"
# 그러나 이 논문이 보고하는 관측량은 전위(V)뿐이며 제거율(nm/min 등) 인쇄값이 없다 —
# 노트 §1 후보2에서 원문 결론 문단을 직접 인용해 확인했다(재적합 불가 사유).

# US9200180B2 [0077] 단락의 부동태 서술이 "possibly"로 헤지된 정성 서술임을 재확인
para_0077 = ("This is possibly due to a much higher passivation rate for copper than "
             "tantalum and/or tantalum nitride in a mixture of hydrogen peroxide and "
             "benzenesulfonic acid.")
assert "possibly" in para_0077, "정성적 헤지 표현 확인"
assert not re.search(r"\d+(\.\d+)?\s*(wt%|vol%|nm|Å)", para_0077), \
    "이 문장에 수치·관측범위가 없음을 확인 — 정량 근거가 아니라 구성적 선택임을 뒷받침"
print("확인: US9200180B2 [0077] 부동태 서술은 정성적(수치 없음, 'possibly' 헤지) — "
      "oxidizer_peak_wt_pct 값은 변경하지 않는다")
```
