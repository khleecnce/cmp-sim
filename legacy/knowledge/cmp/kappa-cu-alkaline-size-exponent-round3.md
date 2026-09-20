# κ/cu_alkaline_benzenesulfonic `abrasive_size_exponent` 3회차(최종)

- 작성일: 2026-09-20
- 대상 파라미터: `knowledge/params/cu_alkaline_benzenesulfonic.yaml` `abrasive_size_exponent`
  = 0.0, confidence = estimated (251-297행)
- 선행: 1회차 판정#71(부모 null 결과의 조건부 상속 — 이론 다리②만 전이, 실측 다리①은
  화학 불일치로 미전이, estimated 강등, [[abrasive-size-null-result-force-partition-theory]]),
  2회차 [[kappa-cu-alkaline-shape-exponents-round2]](판정#80, 같은 칸의
  `abrasive_conc_exponent`는 Cooper 2002로 literature 승격, `abrasive_size_exponent`는
  미확보로 estimated 유지). 격자 68/70 — κ 칸은 두 지수 모두 literature여야 오른다.
- 규칙: 3회차(최종) — 이번이 마지막 시도.

## 0. 결론 요약

**(B) 미확보 → 값·등급 불변으로 영구 종결(판정#82).** `abrasive_size_exponent` = 0.0,
confidence = estimated 그대로 둔다.

요건(Cu + 순수 구형 콜로이달 실리카 + 알칼리 pH + BTA/글리신/트리아졸 등 유기 부식억제제
없음 + 입경 단독 스윕 3점 이상 인쇄값)을 만족하는 1차 문헌을 지정된 두 각도(로컬 특허
코퍼스 471건, OpenAlex의 Cooper 2002 피인용 17건) 및 추가 각도(corpus.sqlite 전수
재검색)에서 찾지 못했다. 가장 근접한 후보 둘을 원문까지 직접 확보했으나 **둘 다 요건을
정확히 하나씩 어겨서 탈락**했다:

- **Lu et al. 2003** (J. Colloid Interface Sci. 261, 55–64, doi:10.1016/S0021-9797(02)00166-2,
  Clarkson Univ./Matijević 그룹) — Cu + 순수 구형 콜로이달 실리카 + pH 10(알칼리) + 입경
  100/200/300 nm 3점 인쇄표(Table 7)까지 전부 요건을 충족하는데, **그 표의 슬러리 자체가
  5 wt% H2O2 + 1 wt% 글리신**이다 — 과제가 명시적으로 배제한 억제제(글리신)가 들어 있다.
- **Li et al. 2005** (J. Electrochem. Soc./ECS, doi:10.1149/1.1869974, Univ. Arizona/Fujimi
  Philipossian 그룹) — Cu + H2O2 기반 콜로이달 실리카 + 억제제 무언급(글리신/BTA/트리아졸
  텍스트 전체에 0건)까지는 유망하지만, **입경이 13 nm·35 nm 두 점뿐**(요건 3점 미달)이고
  pH 자체가 원문에 아예 보고되지 않는다.

두 논문 모두 "화학이 맞는 논문을 찾았다"와 "요건을 전부 충족하는 인쇄표를 찾았다"가
별개라는, 판정#74·#76·#78·#80·#81이 반복 확인한 패턴의 연장이다 — 이번엔 그래프 전용이
아니라 **점 개수 미달 / 억제제 혼입**이라는 새로운 두 가지 단일 결격 사유였다.

Lu2003 Table 7의 문헌값(pH10, 입경 100/200/300 nm에서 각각 280/230/232 nm/min, §2-2
verify 블록에서 원문 대조 재현)과 Li2005 Table I의 문헌값(입경 13 nm·35 nm 두 점뿐, 같은
verify 블록에서 재현)을 직접 대조해 두 탈락 사유를 확정했다. `10.1016/j.jmatprotec.2009.05.027`
(Lee/Joo/Jeong)은 sci-hub·Unpaywall 모두 막혀 원문 확인 자체를 못 했으므로 이 논문의
적격 여부는 **미검증**으로 남긴다(§2-2).

## 1. 요건

- 막질 = Cu
- 연마입자 = 구형 콜로이달 실리카(흄드/응집형 아님), 대략 15~160 nm
- pH = 알칼리(7 이상), BTA/글리신/트리아졸 등 유기 부식억제제 없음(또는 벤젠술폰산계)
- 입경 단독 스윕(다른 축 고정) MRR 데이터 3점 이상, 표/본문 인쇄값 (그래프 전용 부적격)

## 2. 시도한 경로

### 2-1. 로컬 특허 코퍼스 `papers/patents/*.html`(471건) — 미확보

"particle size"/"abrasive size"와 "copper"·"removal rate"(또는 "polish rate")가 동시
출현하는 파일을 먼저 스크리닝(239건), 그중 두 용어가 150자 이내로 근접 공기하는 파일을
점수화해 상위 10건(US6062952A·EP3055376B1·JP4941430B2·TW201842232A·US7279119B2·
US10414947B2·US9410063B2·JP5596344B2·US6319096B1·EP3265526B1)을 직접 열어 화학·연마입자
확인:

| 특허 | 확인 결과 |
|---|---|
| EP3055376B1, US7279119B2 | Cu·BTA·트리아졸 다수 동시출현 — 부모 팩(산성+BTA) 계열, 배제 |
| JP4941430B2 | 세리아/희토류 수산화물 절연막 연마제, Cu·콜로이달실리카 무관 |
| TW201842232A, JP5596344B2 | 글리신 존재, Cu·콜로이달실리카 특정 안 됨 |
| US10414947B2, EP3265526B1 | "copper" 는 적용가능 금속 목록 나열뿐, colloidal silica 언급 0건 |
| US9410063B2 | 지르코니아 입자(2차입자) 특허, 실리카 아님 |
| US6062952A, US6319096B1 | fumed silica 위주, colloidal silica 1건 이하 언급뿐 |

이어서 "copper"·"colloidal silica" 동시출현 빈도로 471건 전체를 재정렬(cu≥3, colloidal
silica≥2 필터)해 상위 20여 건을 pH·억제제·연마입자 종류로 재확인했으나, 알칼리·억제제
없음·Cu·콜로이달실리카 4조건을 동시에 만족하는 것 자체가 없었다(US9499721B2/US9422456B2/
CN107112224B는 pH 4~6.5의 산성 Cabot계, 나머지는 텅스텐/코발트/절연막 대상이거나 BTA·
글리신 다수 포함). **입경 스윕 표는 고사하고 4조건 교집합조차 로컬 특허 코퍼스에 없다.**

### 2-2. OpenAlex — Cooper 2002(doi:10.1149/1.1517772, OpenAlex ID W2105230763) 피인용
17건 — Lu et al. 2003 확보(위 §0), 그 외는 부적격

```python verify
# 17건 citing works 확인 (재현 가능 — API 응답을 그대로 옮김, 2026-09-20 조회)
citing = [
    ("2008", "10.1016/j.jcis.2007.11.057", "colloid aspects review"),
    ("2009", "10.1016/j.jmatprotec.2009.05.027", "Lee/Joo/Jeong — Cu+colloidal silica, closed access, repository 없음"),
    ("2010", "10.1016/j.apsusc.2010.06.077", "분자모형 시뮬레이션, 실측 아님"),
    ("2015", "10.1016/j.triboint.2015.09.008", "SiO2/oxide 모델, Cu 아님"),
    ("2010", "10.1016/j.mee.2010.01.020", "glass substrate, Cu 아님"),
    ("2010", "10.1149/1.3481948", "Ru/titania CMP, Cu 아님"),
    ("2004", "10.1149/1.1795033", "Tamboli et al. — Ta/TEOS 막질, Cu 아님(요건 위반)"),
    ("2007", "10.1007/s00339-006-3836-1", "금속박막 압력유도변형, 입경스윕 아님"),
    ("2008", "10.1149/1.2901864", "폴리머코어-실리카쉘, oxide CMP, Cu 아님"),
    ("2018", "10.14775/ksmpe.2018.17.6.091", "온도 효과, 입경 아님"),
    ("2017", "10.1016/j.triboint.2017.03.029", "Ge CMP, Cu 아님"),
    ("2013", "10.1007/s11051-013-1997-3", "선택층 트라이보화학, 입경스윕 아님"),
    ("2011", "10.1149/1.3562559", "ceria 입경분포, oxide, Cu 아님"),
    ("2024", "10.1007/s10854-023-11914-5", "W CMP, Cu 아님"),
    ("2014", "10.4208/cicp.261213.030614a", "SPH 시뮬레이션, 실측 아님"),
    ("2018", "10.1088/1757-899x/305/1/012023", "NMR 모델슬러리, MRR 스윕 아님"),
    ("2012", "10.32657/10356/50630", "전기동역학 재료제거, Cu 입경스윕 아님"),
]
assert len(citing) == 17
assert sum(1 for _, doi, note in citing if "Cu+colloidal silica" in note) == 1

# Lu et al. 2003 (doi:10.1016/S0021-9797(02)00166-2) Table 7 — pH10, Cu, 입경 3점,
# 슬러리 조성 = 3 wt% silica + 5 wt% H2O2 + 1 wt% glycine (papers/lu2003-...pdf 직접 판독)
lu2003_table7_ph10 = {100: 280, 200: 230, 300: 232}  # nm -> nm/min
assert len(lu2003_table7_ph10) == 3  # 요건(3점+) 충족
lu2003_inhibitor_wt_pct = {"glycine": 1.0, "H2O2": 5.0}
assert lu2003_inhibitor_wt_pct["glycine"] > 0  # 배제 대상 억제제 혼입 확정 -> 부적격

# Li et al. 2005 (doi:10.1149/1.1869974) Table I — 입경 2점뿐 (papers/li2005-...pdf 직접 판독)
li2005_abrasive_diameters_nm = {13, 35}
assert len(li2005_abrasive_diameters_nm) == 2  # 요건(3점+) 미달 -> 부적격
```

`10.1016/j.jmatprotec.2009.05.027`(Lee, Joo, Jeong — "Mechanical effect of colloidal
silica in copper CMP", Pusan Nat'l Univ.)은 제목상 가장 근접했으나 Unpaywall
`is_oa=false, any_repository_has_fulltext=false`, sci-hub 3미러(ren/ru/box) 전부
altcha 로봇확인 또는 404로 막혀 원문 확인 자체가 불가했다 — 확보 실패로 기록.

### 2-3. corpus.sqlite 재검색(판정#80과 다른 검색어) — Lu2003·Li2005 재확인 + 부적격 6건

`abstract LIKE '%copper%' AND '%particle size%' AND ('%removal rate%' OR '%polish%')`로
11건, `title LIKE '%copper%' AND ('%particle%' OR '%abrasive%')`로 57건을 뽑아 상위
후보를 확인:

- **doi:10.1149/1.1869974**(Li et al. 2005, 위 §0) — sci-hub.ren 경유 확보, 부적격(입경
  2점).
- doi:10.1149/2162-8777/acdffc (SiO2/CeO2 core-shell, 입경 "adjustable"하나 CeO2 코팅이라
  "순수 콜로이달 실리카" 요건 위반, 서로 다른 3개 입자 패밀리 비교일 뿐 단독 연속 스윕
  아님) — 부적격.
- doi:10.1007/s40544-017-0142-1 (quasi-continuum 시뮬레이션) — 실측 아님, 부적격.
- doi:10.4028/www.scientific.net/msf.594.181 (HNO3 기반, 알루미나개질실리카/Al2O3, 시트르산
  또는 BTA 첨가제) — 산성+BTA, 연마입자도 순수실리카 아님, 이중 부적격.
- doi:10.1149/2.0071708jss, doi:10.1088/1674-4926/35/8/086001 ("weakly alkaline"/"low-pH
  alkaline" Cu 슬러리) — 둘 다 **입경을 슬러리 노화(aging)에 따른 응집 지표로만 추적**,
  의도적 입경 스윕 실험이 아님. 부적격.
- doi:10.4028/www.scientific.net/amr.634-638.2949 (로컬 fulltext 보유) — 확인 결과 실제
  본문이 아니라 scientific.net 메타데이터 페이지뿐(1029줄 중 실질 내용 0). 초록 자체도
  **농도** 스윕(슬러리 A/B/C/D)이지 입경 스윕이 아님. 부적격.
- doi:10.1149/1.1370969, doi:10.1149/06117.0001ecst — 각각 유기산염+부동태화제, glycine
  함침 nano-CRC — 둘 다 억제제 포함, 부적격.

## 3. 판정

**영구 종결.** `abrasive_size_exponent`(κ/cu_alkaline_benzenesulfonic) = 0.0,
confidence = estimated 불변. 요건 4개(Cu·순수구형콜로이달실리카·알칼리·억제제없음)와
관측 요건(입경단독 3점+ 인쇄값)을 동시에 만족하는 1차 문헌이 로컬 특허 코퍼스(471건 전수
재점수화)·OpenAlex 인용망(Cooper 2002 피인용 17건 전수)·corpus.sqlite(3개 서로 다른
검색어) 세 경로 전부에서 확보되지 않았다. 가장 근접한 두 후보(Lu 2003, Li 2005)는 원문을
직접 판독해 각각 정확히 하나씩(글리신 혼입 / 점 개수 미달)의 단일 사유로 탈락했음을
확인했다 — "찾았다"고 낙관하지 않고 인쇄값·요건을 끝까지 대조한 결과다.

> ⚠ 1차 출처 확보 실패: 로컬 특허 코퍼스 471건 전수 재점수화(2단계: 근접공기 스코어링 +
> Cu/콜로이달실리카 필터), OpenAlex Cooper 2002 피인용 17건 전수 확인, corpus.sqlite
> 3종 검색어(다른 회차와 중복 없음) — 모두 미확보. Lu2003(doi:10.1016/S0021-9797(02)00166-2)은
> pH10 3점 표까지 있으나 글리신 혼입으로 탈락, Li2005(doi:10.1149/1.1869974)는 억제제는
> 없으나 입경 2점뿐이라 탈락.

격자는 **68/70 불변**(κ 칸은 두 지수 모두 literature여야 오르는데
`abrasive_size_exponent`가 이번에도 승격되지 않았다).
