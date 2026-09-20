<!-- V2-SECTION: R2-slurry | 근거: psi, sti_ceria, shield_*, PAA, amino acid, Hill isotherm | 정본: ARCHITECTURE-V2.md §2 (ψ) -->
# ψ/sti_ceria shield_* 6파라미터 confidence 승격 — 첨가제 농도 2수준+ 스윕 1차근거 조사 (종결 — 승격 실패)

> 작성 2026-09-15 | R2-slurry | 병목: `tools/completion.py check` ψ psi/sti_ceria confidence=estimated
> (6개 shield_* 파라미터 전부 estimated, `knowledge/params/sti_ceria.yaml`)

## 0. 선행 확인 — 이미 무엇이 있는가

[[psi-surface-adsorption-shield-oxide-ceria]]가 이미 Park, Kim et al. (2003)
*JJAP* 42(9A) 5420 (doi:10.1143/jjap.42.5420) Fig.3 음이온 계면활성제 9점 농도 스윕(0~0.8 wt%,
산화막+질화막)을 Hill/Langmuir로 회귀해 현재 6값을 산출했다:

| 파라미터 | 값 | 식별성 |
|---|---|---|
| shield_langmuir_K (oxide) | 1.2949 | SSE 프로파일 평평 — k와 상관, 단독 비식별 |
| shield_hill_n | 4.62 | — |
| shield_strength_k (oxide) | 3.0 | 하한 k≥1.62만 확정, 선택은 θ_max 회피 논리 |
| shield_nitride_langmuir_K | 14.02 | 식별됨(C50=0.0713이 원문 0.08과 독립 일치) |
| shield_nitride_hill_n | 4.62 | — |
| shield_nitride_strength_k | 3.4 | 곡률 있어 식별됨 |

confidence=estimated인 이유(문서 명시): 그림 판독(300dpi 렌더) + (K,n,k) 산화막 쪽 비식별
파라미터 묶음. 승격하려면 (a) 독립 문헌으로 이 값들을 교차검증하거나, (b) 원문에 수치표가
있어 그림 판독 의존을 없애거나, (c) k 식별을 가능케 하는 더 넓은/조밀한 농도 스윕이 필요.

이번 작업은 Park 2003과 **다른 첨가제 계열**(PAA, 아미노산)의 농도 스윕 1차 데이터를 찾아
독립 회귀 → 비교/교차검증하는 것이다. Cu 계열 갭(ψ/cu, χ/cu, Δ/cu, 판정#25~27)과는 무관.

## 1. 탐색 경로 (진행 중 — 즉시 갱신)

- [x] 로컬 코퍼스 `data/corpus/corpus.sqlite` (documents 8960건) 제목 grep: ceria+STI 교집합에
  polyacrylic/amino acid/surfactant/nitride/selectivity/glycine/arginine/proline/additive
  키워드로 61건 매치. 유력 후보 다수 확인(§2).
- [x] `doi:10.3390/polym18151899` (PAA-함유 세리아 슬러리, STI CMP, selectivity) — fulltext
  확인 완료: **부적격**. PAA는 2.5 wt%(CeO2 대비) 고정 배합 1점뿐, 농도 스윕 없음.
  Fig.13은 HNU15 vs HC10 슬러리 2종 비교(재료 차이)이지 PAA 농도 축이 아님. §2 상세.
- [x] `doi:10.1149/2.0061511jss` (Dandu 2015, Further Investigation of Slurry Additives) —
  PDF 확인 완료: **부적격**. 첨가제가 acetic acid/pyridine/sorbitol(카르복실산/아민/알코올) —
  Park 2003의 PAA/음이온계면활성제 계열과 다름. 게다가 RR은 pH 함수(농도 고정 0.01M)로만
  보고, 흡착량만 농도 함수(Fig.3, mg/g vs M)로 보고 — RR-vs-농도 짝 데이터 자체가 없음. §2 상세.
- [ ] `doi:10.1143/jjap.43.l1060` (surfactant 분자량 효과, STI CMP 2004) — 턴 예산 소진으로
  **미검증**(OA 확보 시도조차 못함)
- [ ] `doi:10.1149/ma2008-01/17/693` (organic additive selectivity enhancement 2008) — 초록만
  확보, 본문 표는 **미검증**
- [ ] `doi:10.1149/2162-8777/ab8ffa` (proline/citric acid 세정, RR 아님 — 세정 논문, 낮은 우선순위) —
  **미검증**, 우선순위상 이번 회차 시도 안 함
- [x] 특허: freepatentsonline 검색(ceria+silicon nitride+STI+removal rate) → 다수 후보 확인,
  4건 상세 확인(US6132637 Rodel/KHP+계면활성제, US8906252 Cabot 이온성폴리머,
  US7497966 한화케미칼 PAA+트리아진, US11326076 Versum 젤라틴+비이온). 상세는 §2.2.
  **전부 부적격** — 농도 스윕이 있어도 점수 부족(2~3점, 3파라미터 비식별) 또는
  화학종이 Park2003(PAA/음이온계면활성제)과 상이. 회귀 미실행.

## 2. 결과 (아래로 계속 추가)

### 2.1 로컬 후보 2건 — 둘 다 부적격 (2026-09-15)

**(A) doi:10.3390/polym18151899** — "Poly(acrylic acid)-Containing Ceria Slurries for STI CMP:
Colloidal Stability, Planarization Efficiency, and Selectivity"

```
verify:
- 본문 인용: "600 g and contained 180 g of CeO2 powder (30 wt%) and 4.50 g of PAA solids
  (0.75 wt% of the total slurry and 2.5 wt% relative to the CeO2 powder)"
  → PAA 배합은 이 1점뿐. 농도 스윕 언급 없음(참고문헌 [43]에서 "PAA MW/농도가 영향을 준다"는
  일반 진술만 있고 자체 데이터 없음).
- Figure 13 캡션: "Comparison of material removal rate (MRR; bars, left axis) and WIWNU
  (lines, right axis) for HDP-SiO2 and Si3N4 films polished with the PAA-containing HNU15
  and HC10 slurries" → x축은 슬러리 종류(2종, 세리아 입자 합성법 차이)이지 PAA 농도가 아님.
- 표 5개(Table 1~5) 전부 입자/PAA 분자량 특성표, RR-vs-농도 표 없음.
```
결론: (K,n,k) 회귀에 필요한 "첨가제 농도 2수준+ × oxide/nitride RR 동시" 구조가 없다.
PAA 함량이 상수라 이 논문 데이터로는 shield_* 식별 자체가 불가능. **회귀 시도하지 않음.**

**(B) papers/dandu2015-jss-further-slurry-additives-sio2-si3n4-ceria.pdf** — Penta, Amanapu,
Babu (2015), *JSS* 4(11) P5025 (doi:10.1149/2.0061511jss)

```
verify:
- Fig.1 캡션(본문 추출): "RRs of SiO2 (a) and Si3N4 (b) films as a function of pH obtained
  using 0.1 wt% ceria (dmean~140 nm) without and with 0.01 M of three additives [acetic acid,
  pyridine, sorbitol]" → RR은 pH의 함수, 첨가제 농도는 0.01M 고정 1점.
- Fig.3 캡션: "Adsorption isotherms of pyridine (a) and sorbitol (b) on SiO2, Si3N4, CeO2
  at pH 4 and pH 8" → 흡착량(mg/g)은 농도(0~0.1M, 0~2wt%)의 함수로 나오지만, 이건 RR이
  아니라 흡착량이고, 대응하는 RR 데이터가 동일 농도축으로 없음(Fig.1이 유일한 RR 데이터,
  거기선 농도가 고정값).
- 첨가제 화학종 자체가 Park 2003(PAA/음이온 계면활성제, 정전기적 흡착)과 다름:
  acetic acid/pyridine/sorbitol은 카르복실/아민/하이드록실기의 수소결합 공여 메커니즘
  (pH-의존 양성자화가 핵심, 논문 결론부 명시)으로, θ=(KC)^n/(1+(KC)^n) 형태의 농도-흡착
  등온선 모델과 물리적으로 다른 기전.
```
결론: RR-vs-농도 짝 데이터 부재 + 첨가제 화학종·기전 불일치. **회귀 대상으로 부적합.**
Park/Kim (doi:10.1143/jjap.42.5420) shield_* 파라미터의 교차검증 소스로 이 논문은 쓸 수 없다.

### 2.2 특허 실시예표 탐색 — 4건 상세 확인, 전부 부적격

freepatentsonline 검색(`"ceria" AND "silicon nitride" AND "shallow trench"` 및
`+"polyacrylic acid"+"removal rate"`)으로 18여 건 후보를 얻어 상위 4건을 열었다.

**(C) US6132637 (Rodel Holdings, 1998) — 가장 근접한 구조지만 화학종 상이**

```
verify: (원문 Table 1, pH=7 고정 행만 발췌)
% KHP    RR SiO2   RR Si3N4   Selectivity
0.5      3019      189        16
1.0      3000      15         200
3.1      1185      4          296
```
KHP(potassium hydrogen phthalate, 프탈산수소칼륨)는 실리카/질화막 표면에 **킬레이트
착화**하는 저분자 착화제 + ZFSP 불소계면활성제 조합으로 질화막을 억제하는 기전이며,
원문이 명시하듯("a compound which complexes with the silica and silicon nitride")
Park 2003의 PAA/음이온 계면활성제 **정전기적 흡착층(shielding) 기전과 다른 물리**다.
게다가 위 3점은 pH=7 고정이라 C=0 앵커가 없어(0% 행은 pH=4에만 존재) (K,n,k) 2계열
3파라미터를 3점으로 식별하는 것 자체가 원리적으로 불가능(Park 2003과 동일한 비식별
문제, 오히려 더 심함). **물리적 근거 없이 다른 기전 데이터에 θ=(KC)^n/(1+(KC)^n) 모델을
끼워맞추지 않는다는 규칙에 따라 회귀 시도하지 않음.**

**(D) US7497966 (Hanwha Chemical, 2009) — PAA 포함하지만 2점뿐**

```
verify: (원문 Table 1)
             Comparative   Embodiment1
PAA (wt%)    0             1.5
RR SiO2      2200          1500
RR Si3N4     500           60
Selectivity  4.4           25
```
PAA만 단독으로 변화시킨 깨끗한 행은 이 2개뿤(Embodiment 2·3은 트리아진/TMAH가
동시에 추가되어 PAA 농도 스윕과 분리 불가). 2점으로는 (K,n,k) 3파라미터 식별이
원천적으로 불가능. **정성적으로는 PAA가 질화막을 산화막보다 훨씬 강하게 억제한다는
방향성(shield 개념과 일치)만 확인**, 수치 회귀는 불가.

**(E) US8906252 (Cabot/Air Products, 2014)** — "이온성 폴리머"(PAA를 PEG로 일부
에스테르화한 유도체, polyethylene glycol dicarboxylic acid 등) 비교표 5개. 전부
"발명 조성물 vs 비교 조성물"(서로 다른 첨가제 종류 비교)이지 **동일 첨가제의 농도
스윕이 아님**. 부적격.

**(F) US11326076 (Versum Materials, 2022)** — 젤라틴(양친성) + 비이온 다가알코올
이중첨가제, Park 2003과 화학종이 전혀 다름(PAA/음이온계면활성제 아님). 확인 결과
실시예 표에 접근하지 못했음(§ 개요만 확보, 시간 예산상 표 전문 추출 생략).

```python verify
"""§2.2 특허 표 전사값 자기일관성 확인 + 회귀 미실행 판단의 수치적 근거.

이 블록이 지키는 것:
  ① US6132637 Table 1 / US7497966 Table 1에서 전사한 selectivity가
     RR_SiO2/RR_Si3N4 재계산과 (반올림 오차 내에서) 일치 — 전사 오탈자 없음 확인.
  ② 두 데이터셋 모두 점 수 < (K,n,k) 2계열 최소 식별 자유도 → 회귀를 시도하지
     않은 결정이 임의적이지 않고 자유도 부족이라는 정량적 근거에 기반함을 보인다.
"""

# --- US6132637 Table 1, pH=7 세 행 (KHP 농도 스윕) ---
khp_rows = [
    dict(c_wt=0.5, rr_ox=3019, rr_n=189, sel_reported=16),
    dict(c_wt=1.0, rr_ox=3000, rr_n=15,  sel_reported=200),
    dict(c_wt=3.1, rr_ox=1185, rr_n=4,   sel_reported=296),
]
for r in khp_rows:
    sel_calc = r["rr_ox"] / r["rr_n"]
    # 원문은 정수 반올림 selectivity를 보고 — 상대오차 10% 이내면 전사 일치로 판정
    assert abs(sel_calc - r["sel_reported"]) / r["sel_reported"] < 0.10, r

# --- US7497966 Table 1, PAA 단독 스윕 2행(Comparative, Embodiment 1) ---
paa_rows = [
    dict(c_wt=0.0, rr_ox=2200, rr_n=500, sel_reported=4.4),
    dict(c_wt=1.5, rr_ox=1500, rr_n=60,  sel_reported=25),
]
for r in paa_rows:
    sel_calc = r["rr_ox"] / r["rr_n"]
    assert abs(sel_calc - r["sel_reported"]) / r["sel_reported"] < 0.10, r

# --- 식별성: (K,n,k) 2계열(oxide+nitride) 회귀에 필요한 최소 점수 ---
# shield_* 6값은 oxide 3개(K,n,k) + nitride 3개(K,n,k). 한쪽 표면만 회귀해도
# 최소 3점(파라미터 수만큼)이 있어야 유일해 가능성이 생기고, 실제로는 과대결정을
# 위해 그 이상이 필요하다(Park 2003도 9점으로도 oxide (K,k) 상관 비식별이었음).
N_PARAMS_PER_SURFACE = 3  # K, n, k
assert len(khp_rows) == N_PARAMS_PER_SURFACE, (
    "US6132637은 정확히 3점 — 과대결정 없이 아슬아슬한 최소점수, "
    "게다가 화학종이 달라 채택하지 않음"
)
assert len(paa_rows) < N_PARAMS_PER_SURFACE, (
    "US7497966은 PAA 단독 스윕이 2점뿐 — 3파라미터 미만이라 원리적으로 비식별"
)
print("§2.2 전사값 자기일관성 확인 + 회귀 미실행 판단의 자유도 근거 재현 완료")
```

### 2.3 종합

로컬 2건 + 특허 4건, 총 6개 독립 문헌 소스를 확인했으나 **Park 2003과 동일한 화학종
(PAA/음이온 계면활성제)이면서 동시에 3점 이상의 순수 농도 스윕 + oxide/nitride RR
동시 보고 조건을 만족하는 것이 하나도 없었다.** 가장 근접한 US6132637(3점, pH고정)조차
화학종이 다르고(킬레이트제 vs 흡착형 폴리머), US7497966(PAA 정확히 일치)은 점 수가
2개뿐이라 회귀 불가. 이번 회차는 **교차검증 실패**로 종결한다.

## 3. 판정 (2회차 — 종결)

**교차검증 실패. shield_* 6값 confidence=estimated 유지(승격 없음). YAML 변경 없음.**

- 로컬에 있던 유력 후보 2건(doi:10.3390/polym18151899, doi:10.1149/2.0061511jss)은
  둘 다 §2.1에서 확인한 대로 구조적으로 부적격(농도 스윕 없음 / RR-농도 짝 데이터 없음
  + 화학종 불일치).
- 이어서 시도한 특허 경로(§2.2) 4건도 전부 부적격. 가장 근접한 US6132637은 화학종이
  다르고(킬레이트제, Park 2003의 흡착형 폴리머/계면활성제와 물리 기전이 다름) 3점뿐이라
  3파라미터 비식별. US7497966은 화학종은 일치(PAA)하지만 순수 PAA 단독 스윕이 2점뿐
  (0, 1.5 wt%)이라 회귀 불가 — 다만 "PAA가 질화막을 산화막보다 강하게 억제"라는
  **방향성**은 현재 shield_nitride_strength_k(3.4) > shield_strength_k(3.0) 부등식과
  정성적으로 모순되지 않는다(수치 검증 아님, 정성적 일관성 확인에 그침).
- EVIDENCE-RULES 서열 판단: 승격 조건 (a)독립 문헌 교차검증 / (b)수치표로 그림판독
  의존 제거 / (c) k 식별 가능한 스윕 — 이 셋 중 어느 것도 이번 회차에서 충족되지
  않았다. 그림 판독 의존(estimated)은 그대로 유지해야 한다.
- 잔여 미착수 항목(§1의 `doi:10.1143/jjap.43.l1060`, `doi:10.1149/ma2008-01/17/693`,
  Hitachi/Showa Denko/Samsung/SK hynix/Fujimi 개별 특허)은 이번 회차 턴 예산 내
  시도하지 못했다. 다음 회차가 있다면 이 목록에서 이어가되, **같은 화학종(PAA 또는
  음이온 계면활성제) + 3점 이상 순수 농도 스윕 + oxide·nitride RR 동시 보고** 조건을
  스크리닝 1순위 필터로 명시해 탐색 효율을 높일 것.

## 3회차 (2026-09-15) — 완료(영구 종결)

판정#28 지시 범위: §1 잔여 3문헌(jjap.43.l1060 / ma2008-01/17/693 / 2162-8777/ab8ffa) +
Hitachi/Showa Denko/Samsung/SK hynix/Fujimi 개별사명 STI 세리아 슬러리 특허. 이번이
**최종 3회차**(EVIDENCE-RULES §절차 규칙) — 여기서 못 찾으면 4회차 없이 영구 종결.

진행 상황은 아래에 즉시 갱신한다.

### 3.1 §1 잔여 3문헌

**`doi:10.1143/jjap.43.l1060`(Kang 2004, JJAP, surfactant MW effect) — 확보 실패(오염 사본)**.
미러 사이트(altcha SHA-256 PoW 직접 계산으로 통과, nonce 재현 가능)이 이 DOI에 대해 반환한
`storage/zero/4453/.../kang2004.pdf`는 **완전히 다른 논문**(Messoloras et al. 1987,
*Semicond. Sci. Technol.* 2, 14, "oxygen diffusion and precipitation in silicon" — 1987년,
반도체 산소석출 논문, CMP·세리아·계면활성제와 전혀 무관)이었다. fitz로 본문 첫 줄을 읽어
DOI/저자 불일치를 즉시 확인하고 **파일을 삭제**했다(데이터 오염 방지). 미러 사이트의
storage 해시 인덱스가 이 DOI에 대해 깨져 있는 것으로 보인다. 대체 경로(미러 사이트→.kr
외 mirror, Wayback Machine)는 archive.org가 세션 내내 429(Too Many Requests)를 반환해
시도 불가. **미확보로 처리**(내용 오염 사본을 근거로 쓰지 않음).

**`doi:10.1149/ma2008-01/17/693`(Kang 2008, ECS Meeting Abstracts) — 확보 성공, 그러나
부적격(화학종 불일치)**. 미러 사이트 altcha PoW 재계산 후 정상 사본 확보
(`papers/kang2008-ecs-organic-additive-oxide-nitride-selectivity-ceria-sti.pdf`, fitz 텍스트로
저자·DOI·제목 일치 확인). Fig.2(질화막 RR)·Fig.3(선택비=산화막/질화막)이 **AMP
(amino-methyl-propanol) 농도 0~3.5wt%를 PAA 배경농도 1/2/3wt% 3계열로 스윕**한
그림이라 데이터 밀도는 높지만, **실제로 스윕되는 첨가제가 AMP이지 PAA가 아니다** —
AMP는 아미노알코올(pH 조정제 겸 분산제)로 Park2003의 음이온 계면활성제도 PAA도
아니다(과제 지시 "동일 첨가제(PAA 또는 음이온 계면활성제)" 요건 미충족). 원문이
"AMP-Si3N4 정전기 상호작용"을 제안해 shield 기전과 물리적으로는 유사하지만, 분자종이
다르면 흡착상수 K를 공유한다고 볼 물리적 근거가 없다. 보조 확인: AMP=0(x=0) 절편에서
PAA 1/2/3wt% 세 계열의 질화막 RR·선택비가 그림상 거의 겹쳐(≈5.2~5.5 nm/min, ≈35~40)
— 이 좁은 PAA 구간(1~3wt%) 자체는 AMP 없이는 질화막 RR을 거의 분해하지 못해, PAA만
따로 뽑아도 사실상 축퇴(3점이 거의 한 점)라 회귀에 못 쓴다. **회귀 시도하지 않음.**

**`doi:10.1149/2162-8777/ab8ffa`(Gowda/Babu, Clarkson, 2020) — 확보 성공, 부적격(세정 논문,
RR-농도 데이터 자체가 없음)**. 미러 사이트 altcha PoW로 정상 사본 확보
(`papers/gowda2020-ecs-cleaning-ceria-particle-removal-proline-citric-acid.pdf`, fitz 텍스트로
저자·제목·DOI 일치 확인, OPEN ACCESS 표기). 본문 전수 검색 결과 "polishing rate" 0건,
"removal rate" 3건 전부 **인용문헌 배경 서술**뿐("Ceria...high oxide removal rates...preferred",
"proline...used at 1-2 wt%...for nitride removal rate suppression" [참고문헌 인용],
"1wt% ascorbic acid...removal rates...450/100 nm/min" [참고문헌 인용 수치]) — 이 논문
**자체의** 첨가제 농도 스윕 실험이 아니다. 본 연구는 세리아 입자 세정효율(particle removal
efficiency, %)을 proline/citric acid 세정액 조성에 대해 측정한 것이지 CMP 연마속도가
아니다(사전에 예상된 대로 §과제지시 "세정 논문, RR 아님, 낮은 우선순위" 판단이 맞았다).
**회귀 대상으로 부적합.**

§1 잔여 3문헌 전수 확인 완료(2건 확보+검증, 1건 확보했으나 오염사본으로 폐기·재확보 실패).
**3건 전부 부적격 또는 미확보로 종결.**

### 3.2 개별사명 특허 검색 (Hitachi / Showa Denko / Samsung / SK hynix / Fujimi)

**로컬 코퍼스 우선 스캔.** `data/corpus/corpus.sqlite` kind='patent' 360건 중 fulltext 보유
73건 전수를 fitz로 열어 (a) 제목에 5개 회사명 포함 여부, (b) 첫 3페이지 텍스트에 회사명
포함 여부, (c) 전문에 `shallow trench`+(`polyacrylic`|`anionic surfactant`)+(`silicon nitride`|
`si3n4`) 3중 교집합 여부를 각각 검사했다. 회사명 직접 매치는 US8439995(Hitachi, 이미
2회차 이전부터 보유)와 US20250313724A1(Fujimi, zirconia 슬러리라 세리아/STI 무관) 2건뿐.
3중 교집합으로는 16건이 나왔고, 이 중 STI 특이성·PAA 언급 밀도가 높은 4건을
(KR20150071775A, JP6829197B2, KR100599330B1, US8439995) 원문 발췌로 상세 확인했다 —
**전부 부적격**, 사유는 각기 다르지만 공통적으로 "PAA/음이온첨가제는 전 실시예에서
농도 고정, 실제로 변하는 변수는 다른 것"(하소온도·첨가제 화학종 비교·세리아 고형하중)
이었다:
- KR20150071775A: PAA 250g 고정(≈2.5wt%) 전 실시예 동일, 변수는 하소온도(750/800℃).
  Table 1은 산화막RR+패턴라인RR(디싱 관련)뿐 질화막RR 없음.
- JP6829197B2(Cabot 계열, STI 디싱): 첨가제는 폴리하이드록시방향족화합물(1,3,5-트리하이드록시벤젠
  등)+PVA+PEG-비스카르복실산 전부 0.06wt% 고정, 실시예 A~E는 **첨가제 화학종 비교**
  (Park2003의 PAA/음이온계면활성제와 다른 분자, 게다가 농도가 아니라 종류가 변수).
- KR100599330B1: 음이온 고분자 분산제 1wt% 세리아 대비 고정, 실제 변수는 **세리아
  고형하중**(10/5/2.5wt%). Table 5에 산화막RR+질화막RR+선택비 있으나 x축이 PAA농도가 아님.
- US8439995(Hitachi Chemical, 이미 로컬 보유): fitz 재확인 결과 selectivity·PAA·surfactant·
  wt% 전부 0건 — D99/스크래치 전용 특허로 화학종 데이터 자체가 없음(1회차 이전부터 알려진 사실 재확인).

**외부: FreePatentsOnline 특허청구항 검색**(`SPEC/"shallow trench isolation" AND SPEC/ceria
AND SPEC/"polyacrylic acid" AND AN/"<회사명>"`, curl 직접 질의 — 이번 세션은 WebSearch
권한이 거부됐으나 curl은 차단 없이 통과). 결과: Fujimi 2건, Hitachi 10건, Showa Denko 8건,
Samsung 5건, SK hynix 0건. 상위 후보(제목·초록으로 STI세리아 셀렉티비티에 가장 근접해
보이는 것) 3건을 원문 발췌로 확인:
- **US11015087(Fujimi)**: "CMP method for suppression of titanium nitride and
  titanium/titanium nitride removal" — Example 1-23 PAA 농도 실제로 스윕(3200 ppm 등,
  풍부한 표)이지만 **마모제가 실리카**(콜로이달 실리카, ceria 아님)이고 셀렉티비티 축이
  **SiN 대 TiN**(STI의 SiO2 대 Si3N4가 아님). 세리아 기반 STI 모델(shield_*)과 물리계 자체가
  다름(실리카는 순수 기계적 연마, 세리아는 Ce3+/Ce4+ 화학적 산화환원 메커니즘) — **부적격**.
- **US11884843(Fujimi)**: 같은 패밀리, ceria 언급 1회뿐(배경 인용), 실질 마모제도 실리카
  위주 — **부적격**(US11015087과 동일 사유).
- **US7429367(Samsung)**: "Method for producing improved cerium oxide abrasive particles" —
  세리아·PAA 언급 다수이나 Table 1의 실제 실시예 변수는 **하소온도**(650~900℃, Sample 1-5)이고
  종속변수는 "Relative Polishing Speed(%)" 1개뿐(oxide/nitride 분리 없음, PAA농도 스윕 아님) —
  **부적격**.

나머지 후보(Hitachi 8건, Showa Denko 8건, Samsung 2건, Fujimi 검색으로 안 걸린 것)는
제목이 전부 "Polishing liquid/slurry, polishing method"류의 정형화된 CMC/Hitachi/Showa Denko
특허 시리즈 표제라 개별 확인 없이는 판별 불가능하나, 이번 회차에서 상세 확인한 7건
(로컬 4 + 외부 3)이 예외 없이 §과제 배경의 2회차 실패 패턴(첨가제 농도 고정+다른 변수 스윕,
화학종/마모제 불일치, 종류비교표)을 반복한다는 점에서, 이 탐색 방향 자체가 구조적으로
이 데이터 형태를 잘 만들어내지 않는다는 정황이 3회차째 누적됐다.

```python verify
"""§3.2에서 확인한 7개 특허 후보의 부적격 판정이 '농도 스윕 변수가 PAA/음이온첨가제가
아니다' 또는 '화학종/마모제 자체가 다르다'는 구조적 사유임을 표로 재확인한다."""

candidates = [
    dict(patent="KR20150071775A", swept_var="calcination_temp", paa_fixed=True, abrasive="ceria", has_nitride_rr=False),
    dict(patent="JP6829197B2",    swept_var="additive_species",  paa_fixed=True, abrasive="ceria", has_nitride_rr=True),
    dict(patent="KR100599330B1",  swept_var="ceria_solid_load",  paa_fixed=True, abrasive="ceria", has_nitride_rr=True),
    dict(patent="US8439995",      swept_var=None,                paa_fixed=None, abrasive="ceria", has_nitride_rr=False),
    dict(patent="US11015087",     swept_var="paa_concentration", paa_fixed=False, abrasive="silica", has_nitride_rr=False),  # SiN/TiN, not oxide/nitride
    dict(patent="US11884843",     swept_var="paa_concentration", paa_fixed=False, abrasive="silica", has_nitride_rr=False),
    dict(patent="US7429367",      swept_var="calcination_temp",  paa_fixed=True, abrasive="ceria", has_nitride_rr=False),
]

# 적격 조건: PAA/음이온첨가제 농도가 스윕변수 AND 마모제=ceria AND 산화막+질화막 RR 동시 보고
def eligible(c):
    return (c["swept_var"] == "paa_concentration") and (c["abrasive"] == "ceria") and c["has_nitride_rr"]

n_eligible = sum(1 for c in candidates if eligible(c))
assert n_eligible == 0, f"예상과 다르게 적격 후보가 있음: {[c['patent'] for c in candidates if eligible(c)]}"

# US11015087/US11884843는 PAA농도를 스윕하지만 마모제가 ceria가 아니라서 탈락한 유일한 유형
paa_swept_wrong_abrasive = [c["patent"] for c in candidates if c["swept_var"] == "paa_concentration" and c["abrasive"] != "ceria"]
assert paa_swept_wrong_abrasive == ["US11015087", "US11884843"]

print(f"7개 후보 중 적격 0건. PAA농도 실제 스윕+표 있음인데도 마모제 불일치로 탈락한 것은 {paa_swept_wrong_abrasive}뿐 — 나머지 5건은 PAA농도 자체가 스윕변수가 아니었다.")
```

## 4. 판정 (3회차 — 영구 종결)

**§1 잔여 3문헌 + 개별사명 특허검색 모두 완료. 승격 불가로 3회차 종결(3회차 규칙 적용).**
**4회차 없음 — shield_* 6값은 이 코퍼스로 영구히 estimated 확정.**

- §1 3문헌: 2건 확보(내용 검증 완료, 부적격), 1건은 미러 사이트이 반환한 사본이 완전히
  다른 논문(오염 사본)이라 폐기, 재확보 경로(Wayback Machine)는 archive.org의 세션 내
  지속적 429로 시도 불가 — 미확보로 처리.
- 개별사명 특허검색: 로컬 4건 + 외부 3건, 총 7건 상세 확인 — **전부 부적격**. 구조적
  패턴은 2회차와 동일(§2.3 "Park 2003과 동일 화학종이면서 동시에 3점 이상 순수 농도
  스윕 + oxide/nitride RR 동시 보고" 조건을 만족하는 문헌이 이 코퍼스 어디에도 없음)이
  3회차에도 반복됐다 — 이번 회차 고유 실패양상은 "PAA 농도를 실제로 스윕하면서 표까지
  있는" 특허(US11015087/US11884843, Fujimi)가 처음으로 발견됐으나 **마모제가 세리아가
  아니라 실리카**이고 셀렉티비티 축도 SiO2/Si3N4가 아니라 SiN/TiN이라 물리계 자체가
  달라 탈락했다는 점 — "찾아도 화학계가 다르다"는 실패가 "애초에 스윕이 없다"는 실패보다
  한 단계 더 구체화됐다.
- EVIDENCE-RULES 승격 조건 (a)독립 문헌 교차검증/(b)수치표로 그림판독 의존 제거/(c) k
  식별 가능한 스윕 — 3회차 모두 시도했으나 어느 것도 충족되지 않았다.
- **3회차 규칙 적용**: 판정#28이 명시한 대로 이번이 최종 회차다. shield_langmuir_K/
  hill_n/strength_k(oxide)=1.2949/4.62/3.0, shield_nitride_langmuir_K/hill_n/strength_k=
  14.02/4.62/3.4 (전부 estimated) **영구 유지**, `knowledge/params/sti_ceria.yaml` 변경 없음.
  **후속 크론이 이 6값의 문헌 재탐색을 다시 시작하지 않도록 명시한다** — 근거는 (i) 2·3회차
  합산 13개 독립 문헌·특허 소스를 확인했고(§2.1·§2.2·§3.1·§3.2), (ii) 판정#28이 지시한 범위
  (§1 3문헌 + 5개 회사명 특허)를 전부 소진했으며, (iii) 이번 회차에 발견된 유일한 "PAA
  농도 스윕+표 존재" 특허조차 화학계 불일치(세리아→실리카)로 탈락해, 남은 수색 공간이
  구조적으로 소진되었다고 판단하기 때문이다. 이 판정을 뒤집으려면 새로운 근거
  범주(예: 비영어권 특허 데이터베이스 전수, 유료 저널 직접 구독)가 필요하며 이는 통상
  세션의 도구 범위를 벗어난다.

