<!-- V2-SECTION: R2-slurry | 근거: oxidizer, passivation, chi, cu_alkaline_benzenesulfonic | 정본: ARCHITECTURE-V2.md §3 -->
# χ `cu_alkaline_benzenesulfonic` — `oxidizer_passivation_K` 독립 재적합 2회차 (판정#81)

> 작성일: 2026-09-20 | 대상: `knowledge/params/cu_alkaline_benzenesulfonic.yaml::oxidizer_passivation_K`
> 선행: [[chi-cu-alkaline-benzenesulfonic-oxidizer-passivation-ruling]](판정#74, 1회차 기각)
> 과제: US20110165777A1 TABLE 2 4점이 아닌 **독립적인** 알칼리 Cu H2O2 농도 스윕(3점 이상)을
> 찾아 K를 재적합하고 두 값이 수렴하는지 검사한다.

## 0. 요건 (재확인)

- 막질 = Cu
- pH ≥ 7 (알칼리)
- 억제제: 벤젠술폰산계 또는 없음 (BTA/글리신/트리아졸계는 불일치 → 부적격)
- H2O2 농도 단독 스윕(다른 축 고정), MRR 인쇄값 3점 이상

## 1. 조사 상태

> 완료 — 5개 후보 확보·확인, 전부 부적격(§2·§3). 승격 기각, estimated 유지.

### 이미 소진 확인된 경로 (재탐색 금지)
- US9200180B2 자신: 산화제 스윕 없음(pH 스윕만)
- US6979252B1(Syton OX-K): 산화제 스윕 없음
- US20110165777A1 TABLE 2: 현재 K의 출처 자체(비독립)

### 탐색 로그

#### 후보 1 — Lin & Du (Fujimi), "Effect of H2O2 Concentration and Slurry Dilution on Removal
Rate and Surface Quality for a Cu Slurry", *ECS Transactions* 18(1) 485-490 (2009),
DOI: 10.1149/1.3096490 — **부적격**

- 확보 경로: `find_open_access.py`가 IOP 링크만 반환(직접 접근 차단) → sci-hub.ru가
  제목 일치 확인 → sci-hub.red storage 직링크로 PDF 확보(`papers/lin2009-ecs-h2o2-cu-slurry.pdf`).
- 제목·초록 모두 정확히 이 과제(콜로이달 실리카 Cu 슬러리, H2O2 wt% 스윕, 제거율)에 부합해
  보였으나, 원문 확인 결과:
  1. **막질/조성**: 콜로이달 실리카 + "Cu complexing agent" + "Cu corrosion inhibitor"
     (성분명 비공개, 벤젠술폰산 여부 확인 불가) — 화학 일치 미확인.
  2. **pH**: 본문 어디에도 pH 값이 인쇄돼 있지 않다 — 알칼리 요건 충족 여부는 미검증(확인 못 함).
  3. **결정적 결격— 그래프 전용**: Cu 제거율 vs H2O2 wt%(Fig.1, Fig.2)가 산점도 그래프로만
     제시되고 본문·표에 인쇄된 수치가 전혀 없다(피크 위치 "0.90 wt%"만 텍스트로 서술,
     제거율 자체의 인쇄값 없음). ⚠ **그래프 전용, 인쇄값 없음 — 부적격 처리**(과제 지시
     "그래프 전용이면 부적격 처리" 그대로 적용).
- 참고로 이 논문의 형상(급상승 후 완만한 감쇠·"threshold")은 정성적으로 우리 팩의
  Langmuir 부동태 형상과 같은 방향이지만, 인쇄값이 없어 재적합에 쓸 수 없다.

#### 후보 2 — Wang Aochen et al., "Electrochemical investigation of copper chemical
mechanical planarization in alkaline slurry without an inhibitor", J. Semicond. 35(2)
026003 (2014), DOI: 10.1088/1674-4926/35/2/026003 — **부적격**

- 확보 경로: sci-hub.ru 제목 일치 확인 → sci-hub.red storage 직링크
  (`papers/wang2014-jsemicond-cu-alkaline-noinhibitor.pdf`).
- 화학 일치는 좋다: 콜로이달 실리카 0.3 vol% + FA/O II 킬레이트제(0.5~5 vol%) + 비이온
  계면활성제 3 vol%, **전용 부식억제제 없음**("alkaline slurry without an inhibitor"),
  pH = KOH/H3PO4로 **10**(알칼리 요건 충족). H2O2를 0~2 vol%로 스윕(Fig.1b, 4계열
  × FA/O II 농도).
- **결정적 결격 — 그래프 전용**: 제거율 vs H2O2(Fig. 1b)가 산점도 그래프로만 제시되고
  본문에는 "0.5 vol% H2O2가 최적"이라는 정성적 서술만 있다. 표 형태의 인쇄값이 없다.
  ⚠ **그래프 전용, 인쇄값 없음 — 부적격 처리**.
- 이 논문이 인용한 선행 연구([9] Wang Chenwei et al., *J. Semicond.* 33(11) 116001, 2012,
  "Planarization properties of an alkaline slurry without an inhibitor on copper patterned
  wafer CMP")가 이 "무억제제 알칼리 Cu" 계의 원출처로 보인다 — 다음 후보로 확인.

#### 후보 3 — Wang Chenwei et al., "Planarization properties of an alkaline slurry without an
inhibitor on copper patterned wafer CMP", J. Semicond. 33(11) 116001 (2012),
DOI: 10.1088/1674-4926/33/11/116001 — **부적격**

- 확보 경로: `find_open_access.py --title`로 DOI 확인 → sci-hub.ru 제목 일치 → sci-hub.red
  storage 직링크(`papers/wang2012-jsemicond-alkaline-noinhibitor-pattern.pdf`).
- 화학은 요건에 부합(콜로이달 실리카 + FA/O 킬레이트제 + 비이온 계면활성제, **무억제제**,
  BTA 첨가 슬러리 B·C와 비교 대조군으로 존재).
- **결정적 결격 — H2O2 스윕 자체가 없다**: H2O2는 **3.3 vol%로 고정**돼 있고, 스윕 축은
  BTA 농도(0/1 mM/3 mM)다(본문 "Hydrogen peroxide 3.3 vol% ... was used as an oxidizing
  agent"). 요건이 요구하는 "H2O2 농도 단독 스윕"이 원천적으로 존재하지 않는다 — 부적격.

#### 후보 4 — Miranda, Imonigie, Moll, "Interaction Effects of Slurry Chemistry on Chemical
Mechanical Planarization of Electroplated Copper", 2004 IEEE WMED, DOI: 10.1109/WMED.2004.1297359
— **부적격** (기존 로컬 텍스트 재검토, 신규 확보 아님)

- 로컬에 이미 `papers/miranda2004-wmed-cu-cmp-ph-h2o2.txt`로 존재(exa web_fetch로 이전에
  확보됨). 재검토 사유: 2×2 요인설계에 pH 고수준=8.0(알칼리 요건 충족)이 포함돼 있어
  이번 과제와 관련 있는지 재확인.
- Cabot 5001 알루미나 슬러리(pH ~8로 배치), H2O2 저/고 2수준(1.5/3.5 %)의 **2×2 전체
  요인설계**. pH=8.0(고정) 조건에서 H2O2 저(1.5%)→고(3.5%) 제거율이 1743→243 Å/min
  (Table 3).
- **결정적 결격 — 점수 부족**: 고정 pH에서 H2O2 값이 **2점뿐**(요건 3점 이상 미달). 또한
  Cabot 5001은 상용 슬러리로 억제제/성분이 비공개(알루미나 연마입자, 벤젠술폰산·무억제제
  여부 확인 불가) — 화학 요건도 미확인. 이중 결격으로 부적격 처리.

#### 후보 5 — Du, Tamboli, Desai, Seal, "Mechanism of Copper Removal during CMP in Acidic
H2O2 Slurry", *J. Electrochem. Soc.* 151(4) G230-G235 (2004), DOI: 10.1149/1.1648029 — **부적격**
(기존 로컬 PDF 재검토)

- 로컬에 이미 `papers/du2004-jes-mechanism-cu-removal-acidic-h2o2-slurry.pdf` 존재. 원문
  직접 재확인: **pH 4(산성)**로 명시(제목 자체가 "Acidic H2O2 Slurry"), 알루미나 연마입자,
  억제제 없음. Fig. 1에 H2O2 0~10 vol% 제거율 곡선(1%에서 피크 180 nm/min, 이후 감소)이
  있으나 **그래프 전용**이다. 본문 재현 대조 문헌값 180 nm/min(1% H2O2 피크 제거율, doi:10.1149/1.1648029 결론 문단 인쇄값)이 유일한 인쇄 수치이고, 나머지 점은 그래프 판독이 필요해 인쇄표로 볼 수 없다.
- **이중 결격**: (1) pH 4 산성 — 요건(pH≥7) 위반, (2) 그래프 전용 — 인쇄값 부족. 부적격.

#### 탐색 범위 — 로컬 특허 코퍼스 재확인 (Rohm&Haas/Fujimi 계열 ~330건)

- US20110165777A1/US9200180B2 계열 벤젠술폰산 실사용(마쿠시 상투구가 아닌 실제 배합
  성분으로서) 특허를 로컬 471건 HTML 전수에서 재확인했다: 실제 배합에 벤젠술폰산이
  등장하는 특허는 **이 두 건 외에 없다**(§1 예비조사, `grep`으로 "benzenesulfonic acid"가
  Markush 상투구가 아닌 "N wt% benzenesulfonic acid" 패턴으로 등장하는 특허를 46건 중
  전수 대조 → JP5314329B2 1건뿐이었고 그마저 도데실벤젠술폰산을 **계면활성제**로,
  BTA를 억제제로 쓰는 **산성**(pH 3.5) 계여서 부적격이었다).
- Rohm and Haas/Fujimi 공동 어사이니 특허(~196건, `Cu`·`removal rate` 다출현 37건으로
  압축) 중 H2O2 wt%를 열로 갖는 표 + Cu 제거율 표가 공존하는 특허는 **찾지 못했다**
  (EP1485440B1/US20090029553A1은 표 24개 중 H2O2 스윕형이 없이 예시 간 단일 비교표만
  존재, US8114775B2는 철-붕소 개질 실리카·아스코르브산 첨가제 계로 화학 불일치,
  US7931714B2는 "removal rate" 표 자체가 없음).

## 2. 결론 — 관찰된 패턴

5개 독립 문헌 후보(학술논문 3편 + 특허성격 데이터 2편)를 확보해 원문을 직접 읽었다.
**전부 부적격**이었고, 실패 사유가 흥미로운 패턴으로 갈린다:

1. **화학·pH 요건은 비교적 쉽게 충족된다** — 알칼리·무억제제 Cu 계(Wang2012/2014
   Hebei 그룹) 자체는 문헌에 존재한다.
2. **그러나 H2O2 농도를 "단독 스윕"하며 3점 이상 인쇄값을 남긴 사례가 하나도 없다.**
   학술 논문(Lin2009, Wang2014, Du2004)은 하나같이 그래프로만 제시했고, Wang2012는
   애초에 H2O2를 고정하고 억제제만 스윕했다. 특허(Miranda2004)는 점수가 2점뿐이었다.
3. 이는 §0 요건 자체가 이 코퍼스에서 만족되기 극히 어려운 조합임을 시사한다:
   **"pH≥7 & 벤젠술폰산/무억제제 & H2O2 인쇄표 3점+"**의 교집합이 US20110165777A1
   TABLE 2(현재 K의 출처) 자신 말고는 로컬·OA로 접근 가능한 범위에서 확인되지 않았다.

## 3. 판정 — estimated 유지 (승격 기각), 3회차 여지는 남긴다

**판정: `oxidizer_passivation_K`(0.8232, `1/wt%`)는 estimated로 유지한다.** 독립 재적합을
시도할 데이터셋 자체를 확보하지 못했으므로(요건을 만족하는 인쇄표가 없음), 두 값이
서로 수렴하는지는 비교할 수 없었다 — [[chi-cu-alkaline-benzenesulfonic-oxidizer-passivation-ruling]]
(판정#74) §3.2가 지적한 한계 1(잔차 11.9%)은 이번 회차에서도 해소되지 않았다.

⚠ **1차 출처 확보 실패**: 시도한 경로 — (a) 로컬 특허 코퍼스 471건 grep 전수(벤젠술폰산
실사용 필터, Rohm&Haas/Fujimi 어사이니 필터, Cu+removal-rate 다출현 필터), (b)
corpus.sqlite 1,719건 fulltext grep(benzenesulfonic+H2O2+copper 동시출현), (c)
`find_open_access.py --title`/Unpaywall(IOP 직접 차단), (d) sci-hub.ru→sci-hub.red storage
경유 PDF 확보(3편 신규), (e) 로컬 기존 PDF 2편 재검토. 5편 모두 원문을 직접 읽어 부적격
사유를 확인했다.

**3회차 여지**: 남긴다. 종결(=구조적 부재 확정)을 제안하지 않는 이유는, 이번 탐색이
**로컬 코퍼스 + OA/sci-hub로 접근 가능한 범위**에 한정됐고, 특히 특허 코퍼스는
Rohm&Haas/Fujimi 두 어사이니로만 좁혔다 — 다른 어사이니(Cabot, Hitachi, JSR, Applied
Materials 계열)의 알칼리 Cu 벌크 슬러리 특허는 전수조사하지 못했다. 3회차 후보:
- Cabot 계열 알칼리 Cu 벌크 슬러리 특허(메모리 노트 [[fabsim-w-bulk-buff-two-stage-refs]]가
  가리키는 Cabot 특허군과 인접한 계열)에서 H2O2 wt% Example 표를 찾는다.
- Hebei 그룹의 후속 논문(Chen Rui, Jiang Mengting 등 "새로운 약알칼리 슬러리" 계열,
  §1 후보 2 PDF의 "You may also be interested in" 목록에 다수 나열됨)을 개별 확보해
  H2O2 축 인쇄표 유무를 확인한다 — 이번 회차는 시간상 확인하지 못했다.

## 4. verify — 사실 재확인 (수치 주장의 코드 근거)

```python verify
import sys, math
sys.path.insert(0, ".")
from sim.chemistry import _oxidizer_term

class FakePack:
    def __init__(self, **kw):
        self.d = kw
        self.name = "fake"
    def has(self, k): return k in self.d
    def get(self, k): return self.d[k]
    def get_or(self, k, dv): return self.d.get(k, dv)

# 현재 YAML 값이 이번 회차에서 변경되지 않았음을 확인 (승격/재적합 없음)
import yaml
doc = yaml.safe_load(open("knowledge/params/cu_alkaline_benzenesulfonic.yaml"))
pack = doc["params"]
K_current = pack["oxidizer_passivation_K"]["value"]
conf_current = pack["oxidizer_passivation_K"]["confidence"]
peak_current = pack["oxidizer_peak_wt_pct"]["value"]
peak_conf = pack["oxidizer_peak_wt_pct"]["confidence"]
assert K_current == 0.8232, f"K 값이 회차 중 변경됨: {K_current}"
assert conf_current == "estimated", f"confidence가 승격됨: {conf_current} (이번 회차는 유지 판정)"
assert peak_current == 1.0 and peak_conf == "estimated", "oxidizer_peak_wt_pct도 이번 회차에서 변경되지 않아야 한다"
print(f"확인: oxidizer_passivation_K={K_current} ({conf_current}), "
      f"oxidizer_peak_wt_pct={peak_current} ({peak_conf}) — 이번 회차 미변경")

# 후보4 Miranda2004: 고정 pH(=8.0, 알칼리)에서 H2O2 2점뿐임을 재확인 (요건 3점 미달)
h2o2_low, h2o2_high = 1.5, 3.5
rr_low, rr_high = 1743, 243  # Table 3, pH-High 행
n_points_at_fixed_ph = 2
assert n_points_at_fixed_ph < 3, "요건은 H2O2 축 3점 이상 — Miranda2004는 미달이어야 부적격 판단이 성립"
print(f"확인: Miranda2004 고정 pH=8.0에서 H2O2={h2o2_low}/{h2o2_high}% 2점뿐 "
      f"(RR={rr_low}/{rr_high} Å/min) — 3점 미달로 부적격")

# 판정#74가 확인한 pH×산화제 독립곱 구조가 이번 회차 코드 변경으로 깨지지 않았는지 재확인
def ox_ratio(C, K=0.8232, Cref=1.0):
    notes = []
    f0 = _oxidizer_term(FakePack(oxidizer_wt_pct=Cref, oxidizer_ref_wt_pct=Cref,
                                  oxidizer_passivation_K=K), notes)
    fC = _oxidizer_term(FakePack(oxidizer_wt_pct=C, oxidizer_ref_wt_pct=Cref,
                                  oxidizer_passivation_K=K), notes)
    return fC / f0

r7 = ox_ratio(7.0)
assert abs(r7 - 0.379) < 0.01, f"판정#74 §5 재현값(0.379)과 어긋남: {r7:.4f} — 코드 회귀 가능성"
print(f"확인: ox_ratio(C=7)={r7:.4f} — 판정#74 §5와 동일(코드 변경 없음 재확인)")
```

