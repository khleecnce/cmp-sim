<!-- V2-SECTION: R4-disk | 분배완료 2026-09-08 | 근거: diamond, grit, 다이아, 디스크 | 정본: ARCHITECTURE-V2.md §3 -->
# CVD 다이아몬드 디스크와 패턴화 그릿 배열 — 최신 1차 문헌 리뷰 (2011–2023)

> disk-design Lv3-1 | 작성일: 2026-09-08
> 선행: [[diamond-grit-mesh-bonding]] (본딩 3종) [[conditioner-grit-design-space]] (§8 Entegris Planargem CVD 앱노트)
> [[conditioner-grit-density-protrusion-cutrate]] (돌출 높이 균일성) [[conditioner-grit-wear-scratch-lifetime]]
> [[../materials/disk-design-pad-roughness-asperity-relation]] (Lv2-2: EHWA CVD 1.3K vs ABT, McAllister 2019)
> [[../materials/hertz-gw-contact-mechanics]] [[conditioner-asperity-population-balance]] [[../cmp/preston-luo-dornfeld-mrr]]
> 스코프: 디스크 **제조 방식**(CVD 다이아 피막 패턴 돌기·PCD 조각·정렬 전착·배향 제어 브레이징·
> 클러스터/방사 배열·자기회피 난수 배열)이 **활성 그릿 비율·돌출 높이 분포·PCR·패드 Ra·MRR·수명**에
> 미치는 영향만 다룬다. 스윕·하중 레시피는 disk-kinematics 영역이라 다루지 않는다.

## 1. 왜 이 단원인가 — "2만 5천 개 중 실제로 깎는 그릿은 10% 미만"

[[conditioner-grit-density-protrusion-cutrate]]에서 3M(Pysher 2010)의 "돌출 높이 균일화 →
결함 67~75개 → 0~9개" 데이터로 **돌출 높이 균일성**이 디스크 설계의 핵심 변수임을 확인했고,
[[../materials/disk-design-pad-roughness-asperity-relation]] §2.5에서 EHWA CVD 팁 1,300개 디스크가
ABT 수만 개 다이아 디스크와 전혀 다른 패드 마이크로텍스처를 만드는 것을 보았다. 이 단원의 질문은
그 다음이다: **종래 전착/브레이징 디스크의 "그릿 로또"(크기·형상·배향·높이가 제각각이라 소수만
접촉)를 제조 방식으로 없애면 정량적으로 무엇이 얼마나 좋아지는가.** 2011년 이후 1차 문헌 5건과
특허 1건을 원문 기준으로 정리한다.

Tsai et al.(2014)의 서술이 문제를 요약한다: "A typical diamond disk contains over 25,000 grits, but
less than 10% of diamond grits are engaged in cutting the polishing pad." (원문 §2, DOI:
10.1155/2014/913812). Saint-Gobain 특허(US8657652B2)는 같은 현상을 돌출 높이 확률분포로 정량화했다
— 종래 전착(Conventional-A)·브레이징(Conventional-B) 디스크의 활성 그릿 비율은 각각 약 25%·30%,
SARD 디스크는 75% 이상(정규화 높이 0.5 이상을 활성으로 정의).

### 1.1 설계 계보 (이 노트에서 다루는 6가지 접근)

| 접근 | 그릿/팁의 정체 | 배열 | 본딩 | 1차 출처 | 원문 |
|---|---|---|---|---|---|
| CVD 다이아 피막 패턴 돌기 | Si₃N₄ 기판을 연삭해 만든 50×50 µm² 돌기 위 12 µm HF-CVD 다이아 피막 | 규칙 격자(간격 고정) | 피막 자체(본딩 없음) | Kim & Kang (2011) IJMTM 51:565 | 전문 |
| 방사·클러스터 브레이징(RCADD) | 천연 다이아 그릿 3~4개/클러스터, 소형 디스크 24장을 양면 조립 | 방사형 + 클러스터 | 브레이징(특수합금) | Tsai et al. (2014) MPE | 전문(OA) |
| 배향 제어("N type") | 145 µm 그릿을 세워 점접촉만 만들도록 배향 | 규칙 pitch 480 µm | 전착(Shinhan) | Shin et al. (2018) IJAMT 97:563 | 전문 |
| 정렬 전착(ordered) | 100/210 µm 그릿, 12 부채꼴 섹터 규칙 배열 | 규칙 | 전착 | Guo et al. (2023) IJAMT 128:1029 | 프리프린트 전문 |
| 자기회피 난수 배열(SARD) | 76~126 µm 큐보옥타헤드론, 배타반경 > 그릿 최대반경 | 난수+최소간격 | 브레이즈 테이프/포일 | Saint-Gobain US8657652B2 (2014) | 특허 전문 |
| PCD 조각(ADD) | 소결 PCD 블록을 깎아 동일 형상 팁 | 규칙 | 없음(일체형) | Tsai (2010) JMPT 210:1095 | **미확보** — Tsai 2014 재인용만 |

리뷰 출처: Li, Baisie, Zhang, "Diamond disc pad conditioning in chemical mechanical polishing",
*Advances in CMP* (Elsevier), DOI: 10.1016/b978-0-08-100165-3.00013-9 — 서지만 Crossref 확인(전문
미확보, 본 노트에서 수치 인용 안 함). Guo(2023)가 이 장을 인용해 "정렬 배열 디스크는 그릿 수가 적어
절삭 효율은 낮지만 돌출 높이 균일성이 높고 수명이 크게 늘어난다"고 요약한다(2차 인용).

## 2. CVD 다이아 피막 패턴 돌기 디스크 — Kim & Kang (2011)

출처: Y.-C. Kim, S.-J. L. Kang, "Novel CVD diamond-coated conditioner for improved performance in
CMP processes", *Int. J. Machine Tools & Manufacture* 51, 565–568 (2011), DOI:
10.1016/j.ijmachtools.2011.02.008. 원문 전체 `papers/kim-kang2011-ijmtm-cvd-diamond-coated-conditioner.pdf`
(유료, 미러 사이트 경유). 제1저자 소속 이메일이 ehwadia.co.kr — 즉 [[../materials/disk-design-pad-roughness-asperity-relation]]
§2.5의 **EHWA CVD 디스크(45×45 µm² 팁 1,300개)의 원형 논문**이다.

### 2.1 제조
- Si₃N₄ 디스크(∅108 mm)를 크리프 피드 연삭으로 가공해 **50×50 µm² 돌기**를 규칙 배열로 만든 뒤
  HF-CVD(57 V, 350 A, Hunatech HNT 1200)로 **12 µm 두께 다이아 피막** 증착. Raman·XRD로 고품질
  다이아 확인(본문 서술, 스펙트럼 수치 없음).
- 비교 대상(종래): SUS ∅108 mm 기판에 80 mesh 다이아 그릿 전착(Ni 본드). 그릿 높이 분포
  **40~90 µm**(Fig.1a 히스토그램). CVD 디스크는 돌기 높이가 일정(Fig.1b, 단일 높이).

### 2.2 실측 (IC1010 패드, POLI-762, 헤드/컨디셔너 하중 6 lb/6 lb, 플래튼/헤드 93/87 rpm, 슬러리 150 mL/min, N=5)

| 지표 | 종래(Ni 전착 80 mesh) | CVD 패턴 돌기 | 비고 |
|---|---|---|---|
| PCR 시간 변동(10 h) | ±10 µm/h | ±3 µm/h | 본문 "73 mm/710 mm"는 ±3/±10 µm의 OCR 깨짐 — Fig.2a 축 단위 µm/hr로 확인 |
| PCR 절대값 | CVD보다 높음 | 종래보다 낮음 | Fig.2a 판독 어려움 — 절대값 **미판독** |
| 패드 Ra 추이(1→10 h) | 1.8 → 2.0 µm 증가 | 변화 없음 | Fig.2b |
| 패드 SEM(10 h) | 기공 심하게 찢김 | 초기 형상 유지 | Fig.3 |
| W-슬러리(5 wt% H₂O₂/KIO₃) 20 h 부식 | 금속 기판 심한 부식 | 변화 없음 | Fig.4 |
| 디스크 수명 | 기준 | ≥2배(12 µm 피막 균일 마모) | 수명 기준 정의 본문 없음 |
| 산화막 RR(300 mm, 5 min) | 3,565 Å/min | 3,931 Å/min | Fig.5, "약 10% 높음" |

저자 해석: 돌기 높이가 일정해 **돌기당 접촉압이 균일** → PCR 변동이 작고 기공이 찢기지 않으며,
asperity 수가 많아져 슬러리 입자 보유량이 늘어 RR이 오른다. **주의**: PCR은 CVD가 *낮다*. 즉 CVD
디스크는 "덜 깎으면서 더 균일하게" 방향이며, 이는 [[conditioner-grit-design-space]] §8의 Planargem
앱노트(PCR·Ra 10~50 h 안정)와 같은 결론이다.

```python verify
# Kim & Kang 2011 (DOI 10.1016/j.ijmachtools.2011.02.008) Fig.5·Fig.2a 문헌값 재현
RR_conv, RR_cvd = 3565.0, 3931.0            # Å/min, Fig.5 범례 명시값
gain = RR_cvd / RR_conv - 1
print(f"RR 이득 = {gain*100:.1f}%  (저자 서술 '약 10%')")
assert abs(gain - 0.10) < 0.01, "RR 이득이 저자 서술 10%와 1%p 이상 어긋남"

pcr_var_conv, pcr_var_cvd = 10.0, 3.0       # ±µm/h, 본문(OCR '710 mm','73 mm' → ±10, ±3 µm 판독)
print(f"PCR 변동 축소 = {pcr_var_conv/pcr_var_cvd:.2f}배")
assert pcr_var_conv / pcr_var_cvd > 3.0

# 종래 그릿 높이 분포 40~90 µm(Fig.1a) → 균일분포 가정 시 '활성 그릿 비율' 오더 추정(§6 모델과 연결)
h_lo, h_hi = 40.0, 90.0
for engage in (5.0, 10.0, 15.0):            # 최고 그릿 기준 패드 침투 깊이 µm (가정값, 미검증)
    frac = engage / (h_hi - h_lo)
    print(f"  침투 {engage:.0f} µm → 활성 비율 {frac*100:.0f}%")
assert 0.05 <= 5.0/(h_hi-h_lo) and 15.0/(h_hi-h_lo) <= 0.35, \
    "40~90 µm 균일분포 + 5~15 µm 침투는 활성 10~30% 오더여야 함(Tsai '<10%', 특허 25~30%와 같은 자릿수)"
```

## 3. 패턴화 배열 (1) — 방사·클러스터 브레이징 RCADD: Tsai et al. (2014)

출처: M. Y. Tsai, C. H. Chen, J. H. Chiang, T. S. Yeh, "Development and Analysis of Double-Faced
Radial and Cluster-Arranged CMP Diamond Disk", *Mathematical Problems in Engineering* 2014, 913812,
DOI: 10.1155/2014/913812 (CC-BY, Wayback 보존 PDF `papers/tsai2014-mpe-radial-cluster-arranged-diamond-disk.pdf`).
동기: 450 mm 웨이퍼용 1,050 mm 패드(면적 0.385 → 0.866 m², 2.25배)를 ∅100 mm 디스크로 깎으려면
**활성 그릿 수**를 늘려야 한다.

### 3.1 설계
- ∅20 mm SUS 소형 디스크에 그릿을 **중심→외주 방사형**, **클러스터당 3~4개**로 배치하고 특수합금
  브레이징(액상 브레이즈가 표면장력으로 그릿을 타고 올라 넓게 지지). 소형 디스크 12장×양면 = 24장을
  ∅108 mm 양면 홈 기판에 에폭시로 붙이고 금속 정반으로 **레벨링**.
- 그릿 총수: RCADD **10,000개** vs 종래(CDD) **25,000개**.

### 3.2 실측 (컨디셔너 10 rpm, 패드 40 rpm, 스윕 5 mm/s, 하중 약 3 kg; 연마 Westech 372M, 4 psi, SS-25 슬러리)

| 지표 | CDD | RCADD | 출처 |
|---|---|---|---|
| PCR 1 h | 24 µm/h | 47 µm/h | Fig.7a, "약 2배" |
| PCR 20 h 감소율 | >16% | 6% | 본문 |
| 스크래치 선 수(아크릴 10 kg 긁기) | 432 | 484 | Fig.8 |
| 활성 팁 효율(선 수/그릿 수) | 1.7% | 4.8% | 본 노트 계산 |
| 산화막 MRR | ≈1,506 Å/min | ≈2,100 Å/min | Fig.10, 저자 "약 28% 높음" |
| 패드 Ra | 낮음 | 높음 | Fig.7b 절대값 **미판독** |
| 패드 기공 SEM(40 h) | 형상 불명·칩 잔류 | 원형 유지 | Fig.11 |

저자는 Tso & Ho(2007) 패드 마모율 경험식 PWR = K_D·V_D·R·A·λ·d₀·(P/H_P)^1.5(λ = 유효 작업 그릿 수)와
방향이 맞는다고만 서술(계수값 없음). **MRR 이득 "28%"는 (2100−1506)/2100로 RCADD를 분모로 둔
값**이며 통상 정의(CDD 분모)로는 39%다 — 아래 verify에서 두 정의를 모두 계산해 저자 수치의 산출
방식을 역추적했다.

```python verify
# Tsai et al. 2014 (DOI 10.1155/2014/913812) 문헌값 재현
import math
A_700, A_1050 = math.pi*0.35**2, math.pi*0.525**2
print(f"패드 면적 {A_700:.3f} → {A_1050:.3f} m², 비 {A_1050/A_700:.2f}")
assert abs(A_700-0.385) < 0.001 and abs(A_1050-0.866) < 0.001 and abs(A_1050/A_700-2.25) < 0.01

pcr_cdd, pcr_rcadd = 24.0, 47.0             # µm/h, Fig.7a 1 h
assert 1.9 <= pcr_rcadd/pcr_cdd <= 2.1, "PCR '약 2배' 불일치"

lines_cdd, lines_rcadd = 432, 484           # Fig.8 스크래치 선 수
grits_cdd, grits_rcadd = 25000, 10000
eff_cdd, eff_rcadd = lines_cdd/grits_cdd, lines_rcadd/grits_rcadd
print(f"활성 팁 효율 CDD {eff_cdd*100:.2f}% / RCADD {eff_rcadd*100:.2f}% (비 {eff_rcadd/eff_cdd:.1f}배)")
assert eff_cdd < 0.10 and eff_rcadd < 0.10, "두 디스크 모두 '<10% 활성' 서술과 부합해야"
assert 2.5 < eff_rcadd/eff_cdd < 3.0

mrr_cdd, mrr_rcadd = 1506.0, 2100.0         # Å/min, Fig.10 본문 근사값
gain_conv = mrr_rcadd/mrr_cdd - 1           # 통상 정의(CDD 분모)
gain_auth = (mrr_rcadd-mrr_cdd)/mrr_rcadd   # 저자 정의 역추적(RCADD 분모)
print(f"MRR 이득: 통상 {gain_conv*100:.0f}% / 저자식 {gain_auth*100:.0f}% (저자 서술 28%)")
assert abs(gain_auth-0.28) < 0.01, "저자 28%는 RCADD 분모여야 재현됨"
assert abs(gain_conv-0.39) < 0.01, "통상 정의로는 39% — 노트 본문에 두 값 병기"
```

## 4. 패턴화 배열 (2) — 배향 제어 "N type": Shin et al. (2018)

출처: C. Shin, A. Kulkarni, K. Kim, H. Kim, S. Jeon, E. Kim, Y. Jin, T. Kim, "Diamond structure-dependent
pad and wafer polishing performance during chemical mechanical polishing", *Int. J. Adv. Manuf. Technol.*
97, 563–571 (2018), DOI: 10.1007/s00170-018-1956-3. 원문 전체 `papers/shin2018-ijamt-diamond-orientation-conditioner.pdf`
(유료, 미러 사이트). 디스크 제조 Shinhan Diamond, 공저 Samsung 메모리 CMP팀.

### 4.1 디스크 (Table 1, ∅4 in, 전착)

| | C1 | C2 | C3 | N |
|---|---|---|---|---|
| 그릿 크기 (µm) | 145 | 145 | 205 | 145 |
| pitch (µm) | 480 | 600 | 480 | 480 |
| 배향 | 면접촉(기판에 면으로 안착) | 〃 | 〃 | **점접촉(그릿을 세움)** |

핵심 아이디어: 그릿을 기판에 **면**으로 안착시키면 제조는 안정적이지만 패드와도 면접촉이 되어
침투가 얕고, 그릿을 **세워** 꼭짓점이 위로 오게 하면 점접촉이 되어 같은 크기·pitch에서도 침투가
깊어진다. N type은 높이 평균이 더 높고 표준편차는 더 작다(Fig.2b, 수치 미기재).

### 4.2 원뿔 압입 모델 (Table 2) 와 실측

저자는 그릿을 강체 원뿔(측면-패드 각 θ)로 보고 Sneddon형 관계 d = (π/2)·c·tanθ(d 압입깊이, c 접촉반경)와
p(r) = E·tanθ/(2(1−ν²))·cosh⁻¹(c/r)를 썼다. Table 2 원문 그대로:

| | C1 | C2 | C3 | N |
|---|---|---|---|---|
| Max. pressure ("Pa" 표기) | 3.55 | 3.72 | 3.55 | 17.1 |
| 접촉반경 c (µm) | 17.1 | 22.7 | 17.1 | 7.18 |
| 압입깊이 d (µm) | 4.74 | 6.29 | 4.74 | 11.3 |

"Max. pressure" 단위 Pa는 물리적으로 말이 안 되며(cosh⁻¹은 r→0에서 발산) 어느 r에서 계산했는지
본문에 없다 — **단위·정의 불명, 상대값만 참고**. 실측: 정규화 총접촉부피 NTCV C형 0.7~1 vs N형 0.4;
PWR C형 ≈0.3 mm/h, N형은 "약 3배 낮음"; COF N형 0.56(최저, PVDF 필름 접촉면적 신호와 같은 순서);
MRR(세리아, 3 psi, 2 min) N형 ≈3,500 Å/min = **C1의 1.6배**; Rpk는 N형 최고·C3 최저, Rvk는 정반대,
MRR은 Rpk와 상관(Rvk와는 무관) — [[../materials/disk-design-pad-roughness-asperity-relation]] §2.1의
Kwon 2013 결론(Rpk가 MRR 지표)과 독립 재확인.

```python verify
# Shin et al. 2018 (DOI 10.1007/s00170-018-1956-3) Table 2 역산 — d = (π/2)·c·tanθ 로 θ 복원
import math
c = {"C1":17.1, "C2":22.7, "C3":17.1, "N":7.18}      # µm
d = {"C1":4.74, "C2":6.29, "C3":4.74, "N":11.3}      # µm
pmax = {"C1":3.55, "C2":3.72, "C3":3.55, "N":17.1}   # 원문 'Pa' 표기, 정의 불명
theta = {k: math.degrees(math.atan(2*d[k]/(math.pi*c[k]))) for k in c}
for k in c: print(f"{k}: θ = {theta[k]:.1f}°")
assert abs(theta["C1"]-theta["C2"]) < 0.2 and abs(theta["C1"]-theta["C3"]) < 0.2, \
    "C형 3종은 같은 θ(≈10°)를 가정한 것으로 재현되어야"
assert 9.5 < theta["C1"] < 10.5 and 44 < theta["N"] < 46, "N형 θ≈45°, C형 θ≈10° 재현"

# 압력비 검산: p ∝ E·tanθ 이면 N/C1 = tanθ_N/tanθ_C1 — Table 2 비와 비교
ratio_model = math.tan(math.radians(theta["N"])) / math.tan(math.radians(theta["C1"]))
ratio_table = pmax["N"]/pmax["C1"]
print(f"압력비 모델 {ratio_model:.2f} vs Table 2 {ratio_table:.2f} → 차이 {abs(ratio_model/ratio_table-1)*100:.0f}%")
assert 0.7 < ratio_table/ratio_model < 1.0, "표 압력비가 tanθ 비와 15~20% 어긋남 — 불일치 기록(정의 불명)"

# NTCV 재현 시도: TCV = π c³ tanθ /(k·pitch). 그릿 수 ∝ 1/pitch² 가정으로 정규화
pitch = {"C1":480, "C2":600, "C3":480, "N":480}
tcv = {k: math.pi*c[k]**3*math.tan(math.radians(theta[k]))/pitch[k]**2 for k in c}
mx = max(tcv.values()); ntcv = {k: v/mx for k, v in tcv.items()}
print("NTCV(1/pitch² 정규화):", {k: round(v,2) for k,v in ntcv.items()}, " 논문: C형 0.7~1, N형 0.4")
assert 0.6 <= ntcv["C1"] <= 1.0 and ntcv["N"] < ntcv["C1"], "C형 0.7~1 범위·N형 최저는 재현"
assert ntcv["N"] < 0.35, "N형 0.4는 정확히 재현되지 않음(0.28) — k·정규화 방식 불명으로 기록"

mrr_gain, pwr_ratio = 1.6, 1/3           # 본문: MRR 1.6배(C1 대비), PWR 약 1/3
print(f"MRR/PWR 비(N vs C1) ≈ {mrr_gain/pwr_ratio:.1f}배 — 본 노트 유도값(논문 미기재)")
assert 4.5 < mrr_gain/pwr_ratio < 5.0
```

**재현 결과 정직 기록**: θ 복원(C≈10°, N≈45°)과 C형 NTCV 0.7~1은 재현됐지만, Table 2 압력비(4.8)는
tanθ 비(5.7)와 15% 어긋나고 N형 NTCV는 0.28로 논문 0.4에 못 미친다 — 저자의 k·정규화·압력 산출점이
본문에 없어 **부분 재현**으로 남긴다.

## 5. 패턴화 배열 (3) — 정렬 전착 디스크의 돌출 높이 실측: Guo et al. (2023)

출처: Z. Guo, S. Yang, Z. Wen, J. Li, J. Cheng, "Characterization and dressing effect of CMP diamond disc
conditioner with ordered abrasive distribution", *Int. J. Adv. Manuf. Technol.* 128, 1029–1048 (2023),
DOI: 10.1007/s00170-023-11965-2. 저널판은 Springer 봇차단으로 미확보, **Research Square 프리프린트 v1**
(DOI: 10.21203/rs.3.rs-2408757/v1, CC-BY, Wayback 보존) 전문을 읽음 —
`papers/guo2023-ijamt-ordered-abrasive-conditioner-preprint.pdf`. 저널판과 수치가 다를 수 있음(**추정**: 동일).

### 5.1 돌출 높이 측정법과 결과
전착 정렬 디스크(12 부채꼴 섹터, 섹터당 수백 개) 2종(그릿 100 µm, 210 µm). 광학 측정은 다이아 굴절
때문에 오차가 커서 **파라핀 왁스 복제**(녹여 덮고 굳힌 뒤 공초점 현미경으로 "구멍" 깊이 측정)를 제안.

| 그릿 | 평균 돌출 | 분포 폭 | 돌출/그릿 비 | 반경 방향 경향 |
|---|---|---|---|---|
| 100 µm | 32.68 µm | ≤30 µm | 0.33 | 중심부 높고 외주 낮음 |
| 210 µm | 102.54 µm | 45 µm | 0.49 | 〃 |

### 5.2 컨디셔닝 실험 (∅203 mm PU 패드, 1.35 kgf, 100 rpm, DIW 200 mL/min, 10/20/30 min)
2 h 연마로 완전 막힌 패드를 두 디스크 모두 30 min에 회복. 210 µm 디스크는 Ra가 100 µm 대비
+0.48/+2.12/+1.42%(10/20/30 min)로 거의 같지만 Ra **분포 표준편차**가 0.7 이상(30 min 0.9 이상)으로
불균일. 접촉각(소수성 회복 지표): 새 패드 약 110°, 2 h 연마 후 약 60°, 100 µm 디스크 10/20/30 min
92.35/101.82/102.09°, 210 µm 78.82/96.79/104.2°. "재료 제거 효율"은 반경 60 mm 위치 최대에서 100 µm
디스크 1,223 µm/h, 210 µm 디스크 323 µm/h — 저자 해석은 "같은 하중에서 210 µm 디스크는 돌출 분포가
넓어 관여 그릿 수가 가장 적다". **이 두 값은 통상 PCR(수십 µm/h)의 10~50배라 국소 최대 깊이율로
추정되며 절대값은 미검증**, 비(3.8배)만 참고.

```python verify
# Guo et al. 2023 (DOI 10.1007/s00170-023-11965-2, 프리프린트 10.21203/rs.3.rs-2408757/v1) 문헌값 재현
grit  = {"100": 100.0, "210": 210.0}
mean  = {"100": 32.68, "210": 102.54}     # µm, §6 결론 1
spread= {"100": 30.0,  "210": 45.0}       # µm, Fig.9 분포 폭
for k in grit:
    print(f"{k} µm: 돌출/그릿 {mean[k]/grit[k]:.2f}, 폭/평균 {spread[k]/mean[k]:.2f}")
assert abs(mean["100"]/grit["100"]-0.33) < 0.01 and abs(mean["210"]/grit["210"]-0.49) < 0.01
# 상대 분포폭은 작은 그릿이 더 넓다(0.92 vs 0.44) — 절대폭은 큰 그릿이 넓다(45 vs 30)
assert spread["100"]/mean["100"] > spread["210"]/mean["210"] and spread["210"] > spread["100"]

eff = {"100": 1223.0, "210": 323.0}       # µm/h (국소 최대, 절대값 미검증)
print(f"제거효율 비 100/210 = {eff['100']/eff['210']:.1f}배")
assert 3.5 < eff["100"]/eff["210"] < 4.0

ca_new, ca_used = 110.0, 60.0             # ° 접촉각
ca_100 = [92.35, 101.82, 102.09]; ca_210 = [78.82, 96.79, 104.2]
rec_100 = [(x-ca_used)/(ca_new-ca_used) for x in ca_100]
rec_210 = [(x-ca_used)/(ca_new-ca_used) for x in ca_210]
print("접촉각 회복률 100 µm:", [round(r,2) for r in rec_100], " 210 µm:", [round(r,2) for r in rec_210])
assert rec_100[0] > rec_210[0] and rec_100[1] > rec_210[1], "10·20 min에서는 100 µm 디스크가 빨리 회복"
assert rec_210[2] > rec_100[2], "30 min에서는 210 µm가 역전(104.2 > 102.09) — 저자 '균일성' 주장은 분포로 판단"
```

## 6. 자기회피 난수 배열(SARD) — Saint-Gobain 특허 US8657652B2 (2014)

출처: Puthanangady et al., "Optimized CMP conditioner design for next generation oxide/metal CMP",
US8657652B2 (출원 2008-08-21, 등록 2014-02-25), Saint-Gobain Abrasives. 전문 `papers/US8657652.txt`
(freepatentsonline). SARD 자체는 US 2006/0010780 "Abrasive tools made with a self-avoiding abrasive
grain array"에 정의: 2D 난수 좌표를 생성하되 **이웃과의 최소 거리 k**(배타반경 > 그릿 최대반경)를
강제 → 반복 패턴도 없고(규칙 배열이 패드에 주기성을 새기는 문제 회피) 다이아 없는 빈 영역도 없다
(순수 난수의 문제 회피). 청구항 1: 활성 그릿(정규화 높이 0.5 이상) 비율 > 75%; 청구항 7: 농도
> 620 개/cm², 50 wt% 이상 < 75 µm; 청구항 4: 패드 Ra < 1.8 µm.

### 6.1 Table 1 (ex-situ 12 lbf, 이중적층 PU 패드)

| 디스크 | 형상 | 크기 (µm) | 배열 | 농도(임의단위) | 본딩 | 패드 Ra (µm) | PCR(임의단위) |
|---|---|---|---|---|---|---|---|
| SGA-A | 큐보옥타헤드론 | 76 | SARD | 32 | 브레이즈 | 1.44 | 1 |
| SGA-B | 절두옥타헤드론 | 76 | SARD | 32 | 브레이즈 | 1.54 | 1.2 |
| SGA-C | 절두옥타헤드론 | 126 | SARD | 16 | 브레이즈 | 1.88 | 1 |
| Conventional-A | 불규칙 큐보옥타 | 151 | 규칙 패턴 | 6 | 전착 | 1.86 | 1.4 |
| Conventional-B | 불규칙 blocky | 181 | 난수 | 2 | 브레이즈 | 1.97 | 0.7 |

활성 그릿 비율(Fig.6, 정규화 높이 0.5 기준): Conventional-A 약 25%, Conventional-B 약 30%,
SGA-A 75% 이상. Conventional-B 평균 돌출은 SGA-A·Conventional-A의 약 3배. 활성 그릿 수 비
SGA-A/Conv-A = (32×0.75)/(6×0.25) = 16(특허 본문 식).

### 6.2 CMP 성능 (Table 2·3)

| | SGA Lab: SGA-B / Conv-A | Fab1: SGA-B / Conv-A | Fab2(패턴 웨이퍼): SGA-A / Conv-A |
|---|---|---|---|
| MRR | 2,589 / 2,427 Å/min | 5,860 / 5,327 Å/min | 110% / 100% |
| WIWNU | 10.4 / 11.2 % | 9.2 / 10.3 % | — |
| 결함(임의단위) | — | 220 / 330 | — |
| 패드 수명 | — | — | 135% / 100% |

Fig.7: 300 mm 패턴 웨이퍼 산화막 트렌치 잔여 깊이가 SGA-A에서 유의하게 큼 = 디싱 개선. 저자 기전:
작은 그릿·높은 활성 비율이 만드는 **잔 텍스처**가 슬러리 응집체를 덜 가둬 국소 과절삭을 막는다.

```python verify
# US8657652B2 Table 1~3 문헌값 재현
active_ratio = (32*0.75)/(6*0.25)
print(f"활성 그릿 수 비 SGA-A/Conv-A = {active_ratio:.0f}")
assert active_ratio == 16.0

lab = (2589.0, 2427.0); fab1 = (5860.0, 5327.0)
g_lab, g_fab1 = lab[0]/lab[1]-1, fab1[0]/fab1[1]-1
print(f"MRR 이득 Lab {g_lab*100:.1f}% / Fab1 {g_fab1*100:.1f}% / Fab2 표기 10%")
assert 0.06 < g_lab < 0.07 and 0.095 < g_fab1 < 0.105
defect_cut = 1 - 220/330
print(f"결함 감소 {defect_cut*100:.0f}%")
assert abs(defect_cut - 1/3) < 0.01

# Table 1: 같은 SARD·같은 크기·같은 농도에서 형상만 바꾼 A→B: Ra +7%, PCR +20%
ra = {"A":1.44, "B":1.54, "C":1.88, "convA":1.86, "convB":1.97}
pcr = {"A":1.0, "B":1.2, "C":1.0, "convA":1.4, "convB":0.7}
assert ra["B"] > ra["A"] and pcr["B"] > pcr["A"], "절두옥타(sharp)가 큐보옥타보다 Ra·PCR 모두 큼"
# 크기 76→126 µm(농도 32→16)로 Ra 1.44→1.88 — Lv2-2의 surface finish ∝ D^0.57 규칙과 대조
pred = ra["A"]*(126/76)**0.57
print(f"3M 규칙 예측 Ra(126 µm) = {pred:.2f} µm vs 특허 1.88 µm (오차 {abs(pred/ra['C']-1)*100:.0f}%)")
assert abs(pred/ra["C"]-1) < 0.05, "타사 특허 데이터가 3M D^0.57 규칙과 5% 이내 — 교차 검증"
assert ra["convB"] > ra["convA"] and pcr["convB"] < pcr["convA"], \
    "난수 브레이징 Conv-B: Ra 최고이면서 PCR 최저(활성 그릿 2 농도·3배 돌출)"
```

**교차 검증 발견**: 3M(Pysher 2010, [[../materials/disk-design-pad-roughness-asperity-relation]] §2.2)의
surface finish ∝ D^0.57 규칙을 Saint-Gobain 특허 SGA-A→SGA-C(76→126 µm)에 적용하면 1.92 µm로
특허 실측 1.88 µm와 2% 차이 — 서로 다른 제조사·다른 시험에서 같은 크기 지수가 나온다.

## 7. 종합 — "활성 그릿 비율"이 공통 변수다

| 접근 | 활성 그릿 비율 | 돌출 높이 균일성 | PCR | 패드 Ra | MRR | 수명·안정성 | 출처 |
|---|---|---|---|---|---|---|---|
| 종래 전착/브레이징 | <10%(Tsai) ~ 25–30%(특허) | 폭 50 µm(40–90) | 기준 | 높음(1.86–1.97) | 기준 | PCR 20 h −16%↑ | Kim 2011, Tsai 2014, US8657652 |
| CVD 패턴 돌기 | ≈100%(단일 높이) | 최고 | **낮음**, 변동 ±3 | 안정(1.8 유지) | +10% | 수명 ≥2배, 부식 無 | Kim & Kang 2011 |
| 방사·클러스터 브레이징 | 4.8%(1.7%의 2.8배) | 레벨링 | 2배 | 높음 | +39%(저자 표기 28%) | 20 h −6% | Tsai 2014 |
| 배향 제어 점접촉 | — | σ 감소(수치 없음) | 1/3 | Rpk 최고 | 1.6배 | 패드 수명↑ | Shin 2018 |
| 정렬 전착 | — | 폭 30 µm(100 µm 그릿) | 100 µm가 210 µm의 3.8배 | 비슷, 분포 균일 | — | — | Guo 2023 |
| SARD 브레이즈 | >75% | 3배 낮은 평균 돌출 | 1.0–1.2 | **낮음**(1.44–1.54) | +7~10% | 패드 수명 +35%, 결함 −33% | US8657652 |

세 갈래 결론:
1. **활성 비율을 올리는 두 길이 서로 반대 방향의 PCR을 낳는다.** CVD 단일 높이(Kim & Kang)와 SARD
   소형 그릿(특허)은 그릿당 하중을 낮춰 **PCR을 낮추거나 유지**하면서 Ra를 낮추고 MRR을 7~10% 올린다.
   반면 레벨링된 클러스터 브레이징(Tsai)과 점접촉 배향(Shin)은 **침투 깊이를 키워** PCR 2배·Rpk↑·MRR
   1.4~1.6배를 얻는다 — 이 차이는 [[../materials/disk-design-pad-roughness-asperity-relation]] §3.4의
   "접촉은 줄어도 접촉당 압력이 오르면 MRR↑" 논리(Sun 2009 Type B)와 같은 축이다.
2. **PCR과 MRR은 분리된다.** Shin(2018) N type은 PWR 1/3인데 MRR 1.6배, Kim & Kang CVD는 PCR이 낮은데
   RR +10%. 즉 [[conditioner-grit-density-protrusion-cutrate]]의 "밀도↑ → PCR↓" 축과 MRR 축은 독립이며,
   MRR을 결정하는 것은 Rpk(정점 통계)다(Shin 2018 Fig.7b, Kwon 2013).
3. **GW 파라미터로의 번역**: 활성 그릿 비율 f_a와 돌출 높이 분포 폭 w는 [[conditioner-asperity-population-balance]]의
   생성항(컨디셔너가 단위시간에 만드는 asperity 수·높이)에 직접 들어간다. f_a·N_total이 유효 절삭점 수,
   w가 그릿당 침투 깊이의 분산을 준다. 이 매핑은 §8 구현 요청으로 넘긴다.

## 8. 구현 요청 (software-lead BACKLOG 인계용 — disk-design은 sim/에 직접 넣지 않음)

**활성 그릿 비율 모델** `f_active(protrusion_pdf, engage_depth)` (우선순위: 중, Lv3-2 절삭 모델의 입력)
- 무엇을: 디스크 돌출 높이 PDF(균일 40–90 µm / 단일 높이 / 측정 히스토그램)와 최고 그릿 기준 침투
  깊이 δ를 받아 활성 비율 f_a = P(h > h_max − δ)를 반환. 유효 절삭점 수 N_eff = f_a·N_total을
  [[conditioner-disk-pad-cutting-model]]의 그릿 밀도 항에 곱한다.
- 검증 문헌값: 종래 디스크 f_a = 25~30%(US8657652 Fig.6, 정규화 높이 0.5 기준), "<10%"(Tsai 2014),
  CVD 단일 높이 → 1.0(Kim & Kang 2011); RCADD/CDD 유효 팁 비 2.8배(Tsai 2014 Fig.8: 484/10,000 vs
  432/25,000).
- 주의: δ는 하중·패드 경도의 함수라 캘리브레이션 파라미터로 남기고, 위 §2 verify의 5~15 µm는 오더
  체크용 가정값이다.

## 9. 미검증·미확보 (정직 표기)
- Tsai (2010) PCD 조각 ADD(DOI: 10.1016/j.jmatprotec.2010.02.021) 및 Tsai & Chen (2011) 유기 본드
  ODD "레벨링 <15 µm"(DOI: 10.1007/s00170-010-3055-y): 서지는 Crossref 확인했으나 미러 사이트 로봇확인으로
  원문 미확보 — "ADD 제조비 종래의 3배 이상", "ODD 팁 레벨링 15 µm 이하면 종래보다 우수"는 Tsai 2014
  §1의 **2차 인용**.
- Kim & Kang (2011) PCR 절대값(Fig.2a)·Tsai (2014) 패드 Ra 절대값(Fig.7b): 그래프 판독 불가로 미판독.
- Shin (2018) Table 2 "Max. pressure (Pa)": 단위·산출 반경 불명. NTCV의 k·정규화 방식 불명(§4 부분 재현).
- Guo (2023) "재료 제거 효율" 1,223/323 µm/h: 절대값 미검증(국소 최대로 추정), 저널판 수치 미대조.
- 특허 Table 1 농도·PCR "임의단위": 절대 개/cm² 미기재(청구항 7의 620 개/cm²만 하한).
- IEEE/VDE 2012 "CVD Diamond-Coated CMP Polishing Pad Conditioner With Asperity Height Variation":
  Crossref DOI 없음, 미확보.

## 10. 자기시험
→ [[../../agents/disk-design/EXAMS.md]] Lv3-1 문항.
