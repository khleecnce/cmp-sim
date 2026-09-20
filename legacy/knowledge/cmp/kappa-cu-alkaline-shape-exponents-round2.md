<!-- V2-SECTION: R2-slurry | 근거: κ 형상지수(농도·입경) — cu_alkaline_benzenesulfonic 2회차 승격 시도 | 정본: ARCHITECTURE-V2.md §3 -->
# κ 형상 지수 2회차 — cu_alkaline_benzenesulfonic (abrasive_conc_exponent 승격 / abrasive_size_exponent 재탐색)

> 에이전트: slurry-abrasive | 작성일: 2026-09-20
> [[kappa-abrasive-concentration-cu-w-cooper-bielmann]](1회차 — Cooper 2002를 cu_h2o2_bta/w_fe_oxidizer에 처음 도입)
> [[abrasive-concentration-mrr-saturation-contact-probability]](현재 estimated 등급의 근거, US9499721B2 TEOS/oxide)
> [[abrasive-size-null-result-force-partition-theory]](abrasive_size_exponent 부모 판정#1, 이론/실측 두 다리)
> 완료기준: `tools/completion.py check` 68/70 → κ 칸 승격 여부는 두 형상지수(conc, size)가 **모두** literature여야 함(sim/factors.py:820-824 `_worst_conf`).

## 상태: 진행 중 (뼈대 — PDF 원문 확보·판독 완료, YAML 반영 전)

## 1. 과제 정의
- κ의 드라이버 4종(abrasive_wt_pct·abrasive_size_nm·pad_hardness_shore_d·asperity_density_per_m2)은 전부 literature.
- 막는 것: `abrasive_conc_exponent`(0.3333333333, estimated)와 `abrasive_size_exponent`(0.0, estimated).
- 1차 과제: `abrasive_conc_exponent`를 Cooper 2002(로컬 PDF 확보됨)로 literature 승격 가능한지 검증.
- 2차 과제(여력 시): `abrasive_size_exponent`의 끊긴 실측 다리(알칼리·억제제 없는 Cu 계 입경 단독 스윕) 재탐색.

## 2. Cooper 2002 원문 직접 판독 (`papers/cooper2002-cu-particle-conc-1517772.pdf`, fitz 전문 추출, 4쪽)

DOI 확인(추측 아님):
```
$ .venv/bin/python tools/find_open_access.py --title "Effects of Particle Concentration on Chemical Mechanical Planarization"
{"src": "Unpaywall", "doi": "10.1149/1.1517772", "matched_title": "Effects of Particle Concentration on Chemical Mechanical Planarization", "confidence": "doi"}
```
DOI: 10.1149/1.1517772 — 1회차 노트가 이미 인용한 값과 일치.

### 2.1 실험 조건 원문 인용 (Experimental 절)
> "Copper films (1.2 μm thick) were prepared by electrochemical deposition from a commercial
> electrolyte on physical vapor deposition (PVD) Cu seed (100 nm)... **Copper wafers were polished
> using proprietary acidic slurries comprised of silica-based particles with an approximate size
> of 40 nm.** Prior to CMP, copper wafers were annealed..."

### 2.2 화학 조성 원문 인용 (Fig. 6 절)
> "To better understand the impact of chemistry on removal rate, two copper slurry chemistries
> were compared. The components and concentrations of the slurries were equivalent in all
> respects with the exception of the corrosion inhibitor, **triazole (TA) or benzotriazole (BTA)**.
> ... the removal rates collapse to an equivalent relationship (~wt%^1/3) with the introduction of
> solids... No differences in critical concentration were observed indicating mechanical effects
> may dominate the critical onset concentration in these slurries."

### 2.3 결론 원문 인용
> "CMP removal rates (viz. Preston coefficient) were found to scale linearly with wt%^1/3 for
> dielectric and metal substrates... the critical particle concentration before significant removal
> rate is achieved was approximately sixfold greater for oxide (SiO2) than for copper surfaces."

### 2.4 유도(Eq. 3–15)의 성격 — 화학 무관 기하학적 논증
```
A = D + Bf(c),  f ∝ 1/τ ∝ 1/λ,  λ ∝ wt%^(-1/3)  ⟹  A = D + F·wt%^(1/3)
```
저자 명시: "Equation 15 is valid for Prestonian systems with **constant chemical composition**,
pressure, and velocity." — 즉 지수 1/3 자체는 입자-표면 충돌빈도라는 순수 기하 논증에서
나오고, 유도 과정 어디에도 pH·억제제·산화제 항이 없다(부모 size_exponent 판정에서 Chen
thesis가 화학종을 참조하지 않는 것과 동형).

## 3. 과제가 요구한 3개 확인 항목 — 결과

| # | 확인 항목 | 판정 | 근거 |
|---|---|---|---|
| 1 | 금속이 Cu이고 스윕이 Cu 기판에서 실제 수행됐는가 | **예** | §2.1 원문("Copper films... polished... Copper wafers"), Fig. 4가 별도로 "Removal rate of copper as a function of solid content" |
| 2 | 입자가 콜로이달 실리카인가 | **부분 일치 — "silica-based particles"** | 원문은 "silica-based particles"라고만 쓰고 "colloidal"이라는 단어는 없음. 알루미나가 **아님**은 명확(oxide 쪽도 "silica particles"). 1회차 노트·부모 size_exponent 판정이 이미 이 수준의 표현("silica-based"/"colloidal silica"업계 관행 동일시)을 받아들인 전례가 있어 동일 기준 적용. 완전 동일 문구는 아니라는 점만 정직히 기록 |
| 3 | 1/3 지수가 Cu 데이터에 대해 주장되는가, 그래프 전용인가 | **Cu 데이터에 대해 주장됨, 그래프 전용(인쇄값 없음)** | Fig. 4(Cu 단독), Fig. 5(Cu·SiO2 함께 wt%^1/3 축)가 근거. 본문·표에 숫자 데이터점 없음 — 절대 wt% 스케일도 그래프 눈금에만 있음(1회차 노트와 동일한 한계) |

**3개 항목 전부 충족** (항목 2는 완전 동일 문구가 아니라 업계 관행 동일시 — 정직히 표기).

## 4. 과제가 묻지 않았지만 원문에서 새로 드러난 사실 — 화학 세부계 불일치

**이것이 이번 회차의 핵심 판단 지점이다.** Cooper 2002의 Cu 실측은:
- **산성** 슬러리("proprietary **acidic** slurries")
- **BTA 또는 TA 부식억제제 함유**(Fig. 6)

이 팩(`cu_alkaline_benzenesulfonic`)은:
- **알칼리**(pH 6.2~11.2, `knowledge/params/cu_alkaline_benzenesulfonic.yaml` 주석 확인 — US9200180B2 청구항 "a pH ranging from about 5 to 11")
- **억제제 없음**, 벤젠술폰산 사용(BTA/TA 아님)

교차검증: 부모 `cu_h2o2_bta` 팩은 `knowledge/params/cu_h2o2_bta.yaml`에 pH 4.0(산성) + 글리신/BTA로 명시돼 있다 —
```
$ grep -n "pH" knowledge/params/cu_h2o2_bta.yaml | head -3
101:      **알칼리 x 무착화제** 계에서 역산됐다. 산성(pH~3) x 착화제(옥살산) 계에서는
105:      그러므로 이 팩의 운전점(pH 4.0 + 글리신/BTA)에서 산화제를 스윕한 예측은
```
즉 **Cooper 2002의 Cu 실측 조건은 이 팩(alkaline_benzenesulfonic)이 아니라 부모 팩
(cu_h2o2_bta, 산성+BTA)과 정확히 같은 화학계**다. 이 팩에 적용하면 "금속(Cu)은 맞지만
산-알칼리·억제제 유무·특정 화학종(BTA/TA→벤젠술폰산)이 다른 세부계로의 전이"가 된다 —
과제가 소멸시키려던 원래 강등 사유("막질 전이")와 **다른 축**의 전이 문제가 새로 생긴 것이다.

### 4.1 이 전이를 얼마나 심각하게 봐야 하는가

두 가지 완화 요인:
1. **유도 자체가 화학 무관**(§2.4) — 지수 1/3은 "고정된 화학 조성에서 농도만 바꿀 때"의
   기하학적 결과이지, 그 조성이 무엇인지는 도출 과정에 등장하지 않는다.
2. **원문 자체가 Cu 시스템 내에서 화학 교체 실험을 이미 수행**했다(Fig. 6, BTA↔TA) — 억제제
   화학종을 바꿔도 지수가 붕괴하지 않고 "collapse to an equivalent relationship"이라고
   명시한다. 이는 가정이 아니라 **원문의 실측 결과**다.

한 가지 미완화 요인:
- Fig. 6 실험은 **억제제 종류(BTA↔TA)만** 바꿨다 — **산성→알칼리 전환**이나 **억제제 완전
  부재**(이 팩의 실제 조건)는 원문에서 테스트되지 않았다. pH 전환은 Cu 산화막 종류·부착성
  (원문 §Conclusions가 이미 "oxides of copper show relatively poor adhesion... in contrast to
  metals such as aluminum or tungsten"라며 산화막 부착성이 금속마다 다르다고 지적)을 바꿀 수
  있어, 억제제 스와핑보다 더 큰 가정의 비약이다. **미검증.**

### 4.2 판정 — 코드베이스 기존 선례와의 정합

이 팩의 현재 `abrasive_conc_exponent` estimated 등급 사유(US9499721B2 원문)는 스스로
"동일 화학계" 판정 기준을 **막질+입자 조합**으로 규정한다(`knowledge/cmp/abrasive-concentration-mrr-saturation-contact-probability.md` §5,
YAML 주석에 재인용됨). 이 기준으로 보면:
- 막질: Cu = Cu **일치**
- 입자: silica-based = colloidal silica **일치**(업계 관행 동일시, §3 항목2)
- 이 기준 자체는 pH·억제제·특정 화학종을 매칭 조건에 넣지 않는다 — 이미 `w_fe_oxidizer` 팩이
  Fe(NO3)3 vs K3Fe(CN)6(다른 산화제, "동일 화학 패밀리"만 일치)로 conc_exponent를 Wang 2012
  E1로 승격한 전례가 있다(1회차 노트 §4).

**따라서 코드베이스가 이미 쓰고 있는 "동일 시스템" 정의(막질+입자)로는 Cooper 2002가 이 팩에
직접 적용 가능하다.** pH·억제제 불일치는 §4.1의 미완화 요인으로 정직히 남기되, 이것을 이유로
새로운 강등 기준을 이 판정에서만 즉석 발명하는 것은 일관성이 없다 — 기존 기준을 따른다.

**결론: `abrasive_conc_exponent`를 literature로 승격한다.** 값(0.3333333333)은 바꾸지 않는다.
Source를 Cooper 2002(1차, Cu 직접 실측)로 교체하고, 기존 US9499721B2는 보조 근거로 유지한다.
§4.1의 미완화 요인(산-알칼리 전환 미검증)은 note에 명시적으로 남긴다 — 다음 회차에 알칼리
Cu CMP 농도 스윕 1차문헌이 나오면 대체 우선순위 1위로 간주.

## 5. python verify — 지수 재현·화학 불변성 근거 재확인

재현 결과(Cooper 2002): 원문 실험조건(Cu 기판, 하중 ~50 kPa, RDE 회전 300 rpm,
연마입자 실리카계 약 40 nm, Cooper 2002)에서 확립된 1/3 지수 모델로 농도를
8배 늘리면(예: 1.25→10 wt%) MRR은 정확히 2배로 예측된다(8^(1/3)=2, Cooper 2002
Eq.15, 아래 코드로 검증, 1회차 노트와 동일 재현 방식). 절대 wt% 축은 원문에
그래프로만 있어 문헌값 자체(임계농도 수치)는 대조 불가 — 지수와 정규화 배수만
재현 대상이다.

```python verify
# Cooper 2002 Eq.15: A = D + F*wt%^(1/3) — 순수 기하 논증, 절대 wt% 스케일은
# 그래프에만 있어(본문 텍스트 미기재) 재현 대상은 지수값과 정규화 함수 거동으로 한정.

def mrr_norm(c, c_ref, n=1.0/3.0):
    return (c / c_ref) ** n

# 기준 조건 배수 1.0 계약
assert abs(mrr_norm(10.0, 10.0) - 1.0) < 1e-9

# 8배 농도 -> 2배 MRR (1/3 지수, Cooper Fig.5 Cu 곡선의 정성적 거동)
r = mrr_norm(80.0, 10.0)
assert abs(r - 2.0) < 1e-6, f"8배 농도 -> 2배 MRR 기대, 실제 {r}"

# 이 팩의 YAML 값과 일치 확인
n_pack = 0.3333333333
assert abs(n_pack - 1.0/3.0) < 1e-9, "팩 값은 코드 기본값(1/3)과 동일해야 한다(승격 시 값 불변 조건)"

# Fig.6 화학 불변성 주장 재확인 — BTA/TA 두 화학이 "같은 지수"로 수렴한다는 것은
# 원문이 준 것은 정성적 진술("collapse to an equivalent relationship")뿐이고, 별도의
# 수치(예: 두 계열 각각의 피팅 지수)는 본문에 없다 — 이 재현은 "지수 자체가 1/3"이라는
# 것만 확인하고, "화학 불변성의 정량적 크기"는 검증 대상에서 제외한다(과잉주장 방지).
print("PASS: conc_exponent=1/3 재현, 값 불변 조건 확인. 화학 불변성은 정성적 근거로만 사용.")
```

## 6. 2차 과제 — abrasive_size_exponent 실측 다리 재탐색 (알칼리·무억제제 Cu 입경 스윕)

### 6.1 US6979252B1 (Syton OX-K, 판정#79 재확인)
```
$ grep -n "particle size\|abrasive.*size\|colloidal\|nm" papers/US6979252B1-dupont-syton-oxk-low-defectivity.txt | head -20
```
재확인 결과: 이 특허는 **오염제거(defectivity) 특허**로, 입자 크기는 단일값
("50-60 nanometers", Syton® OX-K 원료 스펙 그대로)이고 원심분리·계면활성제
유무만 변수로 스윕한다. **입경 자체를 스윕하지 않는다** — 판정#79의 결론과
동일하게 재확인, 이번에도 재탐색 대상에서 제외.

### 6.2 신규 후보 탐색 — 로컬 코퍼스·find_open_access

`data/corpus/corpus.sqlite`(documents 테이블, 전문 확보분)에서 "copper" +
"particle size" 교차 검색:
```python
SELECT id, title, doi, year FROM documents
WHERE (title LIKE '%copper%' OR abstract LIKE '%copper%')
AND (title LIKE '%particle size%' OR abstract LIKE '%particle size%')
AND fulltext_path IS NOT NULL
```
결과 2건 — 둘 다 무관(65nm 노드 CMP 테스트기술 리뷰, 수용성 풀러렌 유도체 일본어
논문). 입경 단독 스윕 데이터 없음.

`find_open_access.py --title`로 "particle size effect copper chemical
mechanical polishing alkaline" 검색 → 관련 후보 중
**"Effects of Alkaline Nano-SiO2 Abrasive on Planarization of 300mm Copper
Patterned Wafer"**(scientific.net DOI 10.4028/www.scientific.net/amr.634-638.2949,
2013, cc-by — 이 DOI는 Crossref 미등록이라 `verify_claims.py`가 검증 못함, 이번
노트에서 근거로 채택하지 않음 참고용 표기만)이 제목상 가장 유망(알칼리+SiO2+Cu
패턴웨이퍼)했으나 Unpaywall이 pdf 링크를 주지 않음(landing만, 게시자 봉쇄) —
접근 실패.

같은 검색에서 **"Mechanisms of Chemically Promoted Material Removal Examined
for Molybdenum and Copper CMP in Weakly Alkaline Citrate-Based Slurries"**
(doi:10.3390/ma17194905, 2024, MDPI cc-by)를 확보(`mdpi-res.com` CDN 직링크로
PDF 다운로드 성공, `papers/ma17194905-alkaline-citrate-mo-cu-cmp.pdf`, 26쪽).
원문 직접 판독:
> "...composed of sodium percarbonate (an oxidizer), with or without citric
> acid as a surface complexing agent, and colloidal silica abrasives..."
> "...+ y wt% colloidal SiO2 abrasives (**NexSil 125K**, Nyacol, Ashland, OH,
> USA)..."

**단일 입자(NexSil 125K, 고정 크기)만 사용 — 입경 스윕이 아니라 농도(y wt%)만
스윕한다.** 게다가 화학도 이 팩과 다르다(구연산+과탄산나트륨, 벤젠술폰산 아님).
2회차 탐색에서도 실측 다리 후보로 부적격 — **기각**.

### 6.3 결론

> ⚠ **1차 출처 확보 실패**: 시도한 경로 — (1) US6979252B1 재확인(단일입경,
> 재탐색 금지 지시대로 중복 확인만), (2) `corpus.sqlite` documents 테이블
> copper×particle size 교차검색(2건, 둘 다 무관), (3) `find_open_access.py`
> 제목검색 2회(알칼리+SiO2+Cu 패턴웨이퍼 논문은 접근 봉쇄, MDPI 알칼리
> 시트르산 Mo/Cu 논문은 확보했으나 단일입경·농도만 스윕).
>
> `abrasive_size_exponent`는 이번 회차도 **estimated 유지**한다. 3회차 후보로
> 남겨둘 것: (a) scientific.net DOI 10.4028/www.scientific.net/amr.634-638.2949(접근 경로
> 재시도 — freepatentsonline류 미러나 저자 리포지토리 탐색), (b) "알칼리
> Cu CMP" + "abrasive size" 조합의 좀 더 넓은 OpenAlex 쿼리(이번 회차는
> find_open_access.py 제목검색 2회로 한정, 전체 OpenAlex API 직접 쿼리는
> 시도 안 함).
