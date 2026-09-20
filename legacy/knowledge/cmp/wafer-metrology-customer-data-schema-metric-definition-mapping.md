<!-- V2-SECTION: R5-wafer | 근거: metrology, uniformity, wiwnu, calibration | 정본: ORG.md §7.3 -->
# Cal-1 — 고객 계측 데이터 스키마 소유 + WIWNU 정의 불일치 매핑 규칙

> 에이전트: wafer-metrology Cal-1 (캘리브레이션 단원, ORG.md §7.3) | 작성일: 2026-09-19
> [[uniformity-metrics-definitions-standards]] [[wafer-metrology-output-schema-site-flatness-standards]] [[wafer-metrology-thickness-methods]] [[inline-virtual-metrology-sampling-optimization]] [[wafer-surface-roughness-afm-scan-scale-dependence]] [[../data/wafer-coordinate-units-outlier-cleaning]] [[../data/cmp-measurement-ingest-schema-standardization]] [[wiwnu-pressure-velocity-wafer-scale]]

## 0. 목적·범위·형제 경계

ORG.md §7.3은 wafer-metrology에게 **"고객 계측 데이터(포인트 좌표·두께·조도) 스키마 소유 +
지표 정의 불일치(고객마다 다른 WIWNU 정의)를 매핑하는 규칙"**을 맡겼다. 이 노트는 그 산출물이다.
앞 단원(Lv1-2 지표 정의·Lv3-2 출력 스키마)은 **재서술하지 않고 인용만** 한다.

**형제 경계 (침범 금지, 인용만):**
- 스키마 **파일**(`data/schema/wafer_measurement.schema.json`)·`ingest.py` 구현은 **cmp-data-engineer** 소유
  ([[../data/cmp-measurement-ingest-schema-standardization]], [[../data/wafer-coordinate-units-outlier-cleaning]]).
  이 노트는 **개정 제안(§5)만** 표로 적고 스키마 파일을 직접 고치지 않는다 — 구현은 PROFILE.md 요청으로 넘긴다.
- 잔차 GP 보정은 **cmp-calibrator** 소관. 여기서는 "정본 정의로 정규화된 스칼라"까지만 책임진다.
- **고객·재직사 데이터 절대 미사용**(ORG.md §7.5). 이 노트의 모든 수치는 공개 표준·문헌·**합성** 프로파일이다.

이 단원이 푸는 실제 문제: 고객 A는 WIWNU를 "3σ/mean"으로, 고객 B는 "(max−min)/mean"으로, 고객 C는
"σ/mean"으로 보고한다. **같은 웨이퍼라도 정의가 다르면 숫자가 최대 3배 차이**(§4)가 난다. 게다가
포인트 맵(49 vs 81)이 다르면 range형 지표는 추가로 어긋난다(§4). 정의·포인트맵을 메타로 붙잡아
정본(uniformity.py default)으로 정규화하지 않으면 캘리브레이션이 "정의 차이"를 "팹 고유 편차"로 오학습한다.

## 1. 계측 장비별 원 데이터 형식 — 좌표계·에지 제외·포인트 수의 1차 근거

고객마다 다른 것은 정의만이 아니다. **원 데이터 형식**(좌표계·에지 제외·측정점 배치)이 먼저 다르다.
아래는 이를 규정하는 표준·특허·1차 문헌이다. 좌표·단위 정규화식 자체는
[[../data/wafer-coordinate-units-outlier-cleaning]]가 이미 확정했으므로 재유도하지 않고, **계측 소스별로
"무엇이 다르게 들어오는가"**를 스키마 관점에서 정리한다.

### 1.1 포인트 좌표계 — 극좌표(polar) vs 직교(Cartesian) vs 다이(die)

- **극좌표 49점 (중심1 + 링 8/16/24)**: US6922603B1 특허 명세 — "a typical 49-point array ... a center point,
  and three concentric rings" with 8, 16, 24 points(1차 확인, [[uniformity-metrics-definitions-standards]] §5 계승).
  광학 두께툴·4점탐침의 전형. Kumar 2019(§2.2)도 4점탐침 **49 site**를 쓴다.
- **직교 52점 대안**: Bibby & Harwood, "Cartesian coordinate maps for chemical mechanical planarization
  uniformity characterization," *Thin Solid Films* 308-309 (1997) 539-544,
  **DOI: 10.1016/S0040-6090(97)00435-5** (Crossref 실존 확인; 원문 PDF Cloudflare 차단으로 **초록만 확인=E5**).
  초록 요지: 49-site 극좌표 맵이 CMP 산업 표준처럼 쓰이나 엣지 부근 불균일도를 **오도(misrepresent)**할 수
  있어 52-site 직교 맵이 더 낫다 — 즉 **좌표계 선택 자체가 지표를 바꾼다**([[wafer-metrology-output-schema-site-flatness-standards]] §2 계승).
- **다이 인덱스(col,row)**: 프로버/전기툴. US7539552B2(AMD)식 NOTCH_DIRECTION 4값(Bottom/Right/Top/Left)과
  아핀 변환으로 물리좌표화([[../data/wafer-coordinate-units-outlier-cleaning]] §1.3, 인용).
- **측정선 배향**: Kumar 2019는 프로파일 측정을 "**노치에서 90° 방향 선**을 따라, 웨이퍼 중심을 지나게" 잡는다.
  즉 같은 49점이라도 **노치 기준각**이 다르면 azimuthal 귀속이 어긋난다(스칼라 지표는 불변,
  [[../data/wafer-coordinate-units-outlier-cleaning]] §4-1의 노치 오등록 논지와 동일 축).

### 1.2 측정점 수(5/9/49/81/121)의 표준 근거 — SEMI MF1618(=ASTM F1618)

- **SEMI MF1618 / ASTM F1618-02** "Practice for Determination of Uniformity of Thin Films on Silicon Wafers,"
  **DOI: 10.1520/f1618-02** (Crossref 실존; ASTM에서 2003년 SEMI로 이관. store-us.semi.org 유료·원문 미확보,
  **스코프·초록만 확인=E5**). 이 Practice가 바로 **"a set of site distribution patterns"**(측정 사이트 배치
  패턴 집합)과 **좌표 선정 규칙·통계 계산법**을 규정한다. 스코프 원문: *"the exact number of measurement sites
  is chosen based on the size of the wafer being used, the desired spatial resolution ... and whether maximal,
  or somewhat lesser information density is desired."* → **5/9/49/81 등 점 수는 웨이퍼 크기·요구 분해능에 따라
  고르되 패턴·좌표·통계는 이 Practice에 일관**되게 두라는 것. "49점=산업 표준"의 통념보다, MF1618은
  **"점 수는 가변, 절차는 고정"**을 규정한다(3편 연속 못 찾던 SEMI 측정점 근거를 이 표준에서 확보).
- Lee & Boning 1999(DOI 10.1109/iwstm.1999.773193)도 "9점"·"49점" 같은 관행 점수를 비교 대상으로 다룬다
  (초록·2차, [[uniformity-metrics-definitions-standards]] §2 인용).
- 9점: US6922603B1이 "mean value of multiple points (for example, nine points)"로 명시(웹검색 스니펫 확인).

### 1.3 에지 제외(EE 2/3 mm → 1.5/1 mm)와 사이트 크기 — NIST 1차

- **NIST Griesmann, Wang, Tricard, Dumas, Hall (2007)**, "Manufacture and Metrology of 300 mm Silicon Wafers
  with Ultra-Low Thickness Variation," *AIP Conf. Proc.*, **DOI: 10.1063/1.2799352** (Crossref 실존;
  **원문 PDF 전문 확보·fitz 판독 = E2급 1차**). 확인된 정량:
  - **에지 제외**: *"the economic pressure to increase the number of dies per wafer will compel the reduction
    of the edge exclusion from **3 mm to 1.5 mm**."* → EE는 고정 상수가 아니라 **줄어드는 추세**
    ([[../data/wafer-coordinate-units-outlier-cleaning]] §3.1의 EE 2–3 mm→1 mm 추세와 정합).
  - **사이트 평탄도 SFQR**: *"site total indicator range after subtraction of a best fit plane (called SFQR)
    over a **26 mm × 8 mm site**"* → SFQR 사이트 크기 1차 근거(ITRS 인용: 80 nm@2005 → 32 nm@2013 → 14 nm@2020).
    [[wafer-metrology-output-schema-site-flatness-standards]] §1.3이 SFQR을 "사이트별 최소자승 평면 range"로만
    정의했는데, **사이트 치수(26×8 mm)**를 이 NIST 문헌에서 확정.
  - 노광 사이트 25 mm × 25 mm에서 두께변동 10–15 nm, 전면 TTV ~40 nm 달성(MRF).

→ **스키마 함의**: 계측 소스는 (좌표계, 점 수, EE 폭, 사이트 크기, 노치 기준각)을 **전부 다르게** 넘긴다.
이 다섯은 지표값을 바꾸므로 **지표와 함께 반드시 메타로 저장**해야 한다(§5 개정 제안).

## 2. WIWNU 정의 변형 5종 — 각 정의가 실제로 쓰인 1차 문헌

[[uniformity-metrics-definitions-standards]] §2가 3σ/1σ/half-range 세 정의를 확정했다. Cal-1은 **고객
입력에서 실제로 마주치는 변형 전체**를 열거하고 각각에 1차 출처를 단다(재서술 아님, 출처 확장).

| # | 표기 | 정의식 | 실제로 쓰인 1차 문헌(근거등급) |
|---|---|---|---|
| D1 | **3σ/mean** (default, "the WIWNU") | $100\cdot 3\sigma/\bar t$ | US6922603B1 특허(원문 확인, E2) [[uniformity-metrics-definitions-standards]] |
| D2 | **1σ/mean** (=CV) | $100\cdot \sigma/\bar t$ | Kumar 2019 Eq.(2) 전문 확인(E2); Doko 2026 "1σ/average×100%" 49점(E5) |
| D3 | **half-range** | $100\cdot (t_{max}-t_{min})/(2\bar t)$ | Burwell 2023 Eq.(1) 명시(E5); Luo & Dornfeld형 [[uniformity-metrics-definitions-standards]] |
| D4 | **full-range** | $100\cdot (t_{max}-t_{min})/\bar t$ | (T_max−T_min)/T_ave형(웹검색 스니펫, E5); Muduli 2020 eq.17/18(E5) |
| D5 | **range/(max+min)** | $100\cdot (t_{max}-t_{min})/(t_{max}+t_{min})$ | Zhu 2022 Eq.(1) "U=(t_max−t_min)/(t_max+t_min)×100%" 명시(E5) |

출처 상세:
- **D2 (σ/mean) — Kumar 2019**(전문 확보, E2): Amit Kumar et al.(BRIDG), "Optimizing the Within Wafer
  Non-Uniformity ...," *Int. Symp. Microelectronics* 2019, **DOI: 10.4071/2380-4505-2019.1.000450**.
  본문 Eq.(2): *"WIWNU was calculated using (2), where σ and Avg are the standard deviation and average of
  the measurements ... = σ/Avg × 100 (%)."* 200 mm Cu/W, 4점탐침 49 site, KLA P-170 프로파일러.
  **패턴 웨이퍼에서는 dishing을 WIWNU 계산의 응답량으로 씀** — 정의식(σ/mean)은 같고 **응답량**만 바뀐다(§3 매핑 핵심).
- **D2 보강 — Doko 2026**(E5, 하이라이트만): *Microelectron. Eng.*, **DOI: 10.1016/j.mee.2026.112496** —
  300 mm 49점 매핑에서 "uniformity was evaluated as **1σ/average × 100%**", 두께 0.6%(1σ). σ/mean이 현행
  최신 실무에서도 default임을 확인.
- **D3 (half-range) — Burwell 2023**(E5, 하이라이트만): *Adv. Eng. Mater.*, **DOI: 10.1002/adem.202201901** —
  *"NU = (MAX − MIN)/(2 × MEAN) × 100%"*, 8" 웨이퍼 두께 매핑. Luo & Dornfeld 스니펫과 **동일 식을 독립 문헌에서 재확인**.
- **D5 (range/(max+min)) — Zhu 2022**(E5, 하이라이트만): *Appl. Sci.* 12(23):11878,
  **DOI: 10.3390/app122311878** — *"U = (t_max − t_min)/(t_max + t_min) × 100%"*. 광학 박막 균일도.
  D3과 **분모만 다르다**(2·mean vs max+min): 대칭분포면 max+min≈2·mean이라 근사 일치, 비대칭이면 갈림(§4 검증).
- **정의 병기 원칙의 1차 근거 — Lee & Boning 1999**(E5, 초록/키takeaway): DOI 10.1109/iwstm.1999.773193.
  academia.edu 키takeaway 확인 — 이 논문이 **%-Std-Post**(post 두께 σ/mean), **Std-AR / %-Std-AR**(amount
  removed의 σ / 정규화 σ) 등을 명명·비교하고, **"어떤 지표는 처리시간에 편향(biased), 어떤 지표는 개선에
  둔감 → 여러 지표 병기가 필요"**하다고 결론. **D1~D5는 σ/mean 계열이 응답량(post 두께 vs 제거량)에 따라
  또 갈린다**는 것이 이 논문의 핵심(§3에서 스키마화).

## 3. 정의 매핑 규칙 명세 — metric_definition 필드 → 정본 정규화

### 3.1 정본(canonical) = uniformity.py default

정본은 이미 코드로 확정돼 있다(`sim/metrics/uniformity.py` docstring, 인용): **WIWNU_3σ = 3σ/mean·100
(D1)이 default 보고값**, 1σ/half-range 병기, radial은 방위각평균 반경프로파일 σ/range. Cal-1의 매핑은 이
정본으로 수렴시키는 규칙이다. **평균내지 않는다**(EVIDENCE-RULES §3: 상반된 지수 평균 금지) — 정의는
결정론적 함수이므로 재계산한다.

### 3.2 두 입력 경로에 따른 매핑 분기

고객 입력은 두 형태로 온다. 매핑 규칙이 다르다:

1. **원 포인트가 있으면(coord+value 배열)**: `metric_definition`을 **무시하고 D1~D5를 전부 재계산**한다.
   모든 정의가 같은 점 집합의 결정론적 함수이므로 고객이 어떤 정의로 불렀든 정본(D1)으로 재산출 가능.
   → 이것이 원칙적 해법. 원 포인트를 요구하는 이유가 여기 있다(스키마 `points` 필수, §5).
2. **사전계산 스칼라만 있으면(WIWNU 숫자 하나)**: 원 점이 없으니 재계산 불가. 이때 `metric_definition`이
   **어떤 식으로 나온 숫자인지**를 알려줘야 (a) 올바로 해석하고 (b) σ-계열끼리는 정본으로 환산한다.
   - σ-계열 환산은 정확(무손실): D1 = 3·D2, D2 = D1/3.
   - range-계열(D3/D4/D5)↔σ-계열은 **분포 형상에 의존**해 무손실 환산 불가 → "환산 불가, 원 점 요청" 플래그.
     D3↔D4는 정확(D4 = 2·D3). D5는 max+min을 알아야 D3/D4와 이어짐.

### 3.3 응답량(measured_quantity) 축 — Lee & Boning의 교훈

σ/mean이라는 **식이 같아도** 무엇의 σ/mean인지가 갈린다(§2 Lee & Boning):
`post_thickness`(%-Std-Post) · `amount_removed`(%-Std-AR) · `dishing`(Kumar 패턴) · `removal_rate` · `roughness`.
같은 웨이퍼도 post-두께 균일도와 제거량 균일도가 다르다(선행 두께 프로파일이 실려 있으므로). 따라서
`metric_definition`만으로 부족하고 `measured_quantity`를 **함께** 받아야 한다. 조도(Ra/Rq)는 스캔크기 함수라
별도 축([[wafer-surface-roughness-afm-scan-scale-dependence]], `scan_size_um` 필수).

### 3.4 포인트맵 비교가능성 한계 — 매핑으로 못 지우는 것

§4에서 정량하듯 **range형(D3/D4/D5)은 포인트맵이 다르면 정의 매핑으로도 비교 불가**해질 수 있다.
규칙: range형 스칼라를 서로 다른 포인트맵의 고객끼리 비교할 때는 **비교가능성 경고**를 띄우고
σ-계열(D1/D2, 상대적으로 맵-강건, §4)로만 비교하거나 원 점 재계산을 요구한다.

## 4. Python 검증 — 정의 항등식·값 스프레드·49 vs 81 샘플링 편향

합성 **center-fast 2% 포물선** 반경 프로파일(실측 아님)에 D1~D5를 계산해 (a) 상호 환산 관계를 assert하고,
(b) 정의별 값이 얼마나 벌어지는지, (c) 49점 vs 81점에서 range형이 얼마나 어긋나는지 정량한다.

```python verify
import numpy as np

# ── 합성 프로파일: center-fast 2% 포물선 (얇은 중심~두꺼운 엣지). 실측 아님.
R, EE, A, T0 = 150.0, 3.0, 0.02, 500.0     # 300mm, EE 3mm, 2% 변동, 500nm 기준
Ru = R - EE                                 # 유효반경 147mm (NIST DOI:10.1063/1.2799352 EE 추세)
def thick(r):
    return T0*(1 - A*(1 - (r/R)**2))        # r=0:0.98·T0(최박), r=R:T0(최후)

def polar_plan(ring_counts, radii):
    xs, ys = [0.0], [0.0]                    # 중심점 1개
    for n, rad in zip(ring_counts, radii):
        for k in range(n):
            th = 2*np.pi*k/n
            xs.append(rad*np.cos(th)); ys.append(rad*np.sin(th))
    return np.hypot(np.array(xs), np.array(ys))

# 49점(US6922603B1: 중심1+8/16/24), 81점(중심1+8/12/16/20/24)
r49 = polar_plan([8,16,24],       [Ru/3, 2*Ru/3, Ru])
r81 = polar_plan([8,12,16,20,24], [Ru/5, 2*Ru/5, 3*Ru/5, 4*Ru/5, Ru])
assert len(r49) == 49 and len(r81) == 81

def defs(r):
    t = thick(r); m = t.mean(); s = t.std(ddof=0); rng = t.max()-t.min()
    return dict(
        D1_3sig  = 100*3*s/m,                # 3σ/mean
        D2_sig   = 100*s/m,                  # σ/mean = CV
        D3_half  = 100*rng/(2*m),            # half-range
        D4_full  = 100*rng/m,                # full-range
        D5_sum   = 100*rng/(t.max()+t.min()),# range/(max+min)
        mx=t.max(), mn=t.min(), mean=m)
d49 = defs(r49)

# (a) 상호 환산 항등식 — 정본 정규화 규칙(§3.2)의 산술 근거
assert abs(d49['D1_3sig'] - 3*d49['D2_sig']) < 1e-12          # 3σ/μ = 3×σ/μ (무손실)
assert abs(d49['D4_full'] - 2*d49['D3_half']) < 1e-12        # full = 2×half (무손실)
# D5는 대칭분포(max+min≈2·mean)면 D3에 근사, 아니면 갈림 — (max+min)/(2mean) 만큼 차이
sym_factor = (d49['mx']+d49['mn'])/(2*d49['mean'])
assert abs(d49['D5_sum'] - d49['D3_half']/sym_factor) < 1e-9  # D5 = D3/((max+min)/2mean)
assert abs(sym_factor - 1.0) < 0.02, sym_factor              # 2% 프로파일이라 거의 대칭(≈1)

# (b) 값 스프레드: 같은 49점 웨이퍼가 정의만으로 얼마나 다른 숫자를 내는가
spread = d49['D4_full']/d49['D2_sig']        # full-range 대 σ/mean 배율
assert spread > 2.5, spread                  # 정의 선택만으로 2.5배 이상 벌어짐(관측 2.78배)
assert abs(d49['D1_3sig']/d49['D2_sig'] - 3.0) < 1e-9  # 3σ vs 1σ는 정확히 3배

# (c) 샘플링 편향 1 — 매끈한 프로파일·동일 반경범위면 range형은 49≈81 (비교 가능)
c49, c81 = defs(r49)['D4_full'], defs(r81)['D4_full']
assert abs(c81-c49)/c49*100 < 0.5            # 깨끗한 조건: full-range 49vs81 차이 <0.5%(관측 0.19%)

# (c) 샘플링 편향 2 — 방위각 측정노이즈 하에서 range는 점 수와 함께 커진다(σ는 강건)
rng = np.random.default_rng(0); NW, sd = 4000, 1.0    # 1nm 측정노이즈, 4000 웨이퍼 MC
def mc_metrics(r):
    fulls, sigs = [], []
    for _ in range(NW):
        t = thick(r) + rng.normal(0, sd, len(r)); m = t.mean()
        fulls.append(100*(t.max()-t.min())/m); sigs.append(100*t.std(ddof=0)/m)
    return np.mean(fulls), np.mean(sigs)
f49, s49 = mc_metrics(r49); f81, s81 = mc_metrics(r81)
range_bias = 100*(f81-f49)/f49; sig_bias = 100*(s81-s49)/s49
assert range_bias > 3.0, range_bias          # 81점 full-range가 49점보다 유의하게 큼(관측 +4.6%)
assert abs(sig_bias) < range_bias            # σ/mean은 점 수에 상대적으로 강건(관측 -2.8%)

# (c) 샘플링 편향 3 — 지배 요인은 점 수가 아니라 최외곽 반경(EE/링 위치) 불일치
r49_short = polar_plan([8,16,24], [Ru/3, 2*Ru/3, 0.90*Ru])   # 최외곽 0.90·Ru
short = defs(r49_short)['D4_full']; full = defs(r81)['D4_full']
radius_bias = 100*(full-short)/short
assert radius_bias > 15.0, radius_bias       # 최외곽 반경차만으로 full-range +23% 어긋남(관측 +23.5%)
assert radius_bias > range_bias              # 반경 불일치 > 점 수 노이즈 효과 (비교불가의 지배원인)

print(f"[a] 3σ=3×σ, full=2×half 무손실; D5=D3/(대칭인자{sym_factor:.4f})")
print(f"[b] 같은 49점: σ/μ={d49['D2_sig']:.3f}% · 3σ/μ={d49['D1_3sig']:.3f}% · "
      f"full={d49['D4_full']:.3f}% → 정의만으로 {spread:.2f}배 스프레드")
print(f"[c1] 깨끗·동일반경 full-range 49vs81 차이 {abs(c81-c49)/c49*100:.2f}% (비교가능)")
print(f"[c2] 노이즈 1nm: full-range 81이 49보다 {range_bias:+.1f}%(range편향) vs σ/μ {sig_bias:+.1f}%(강건)")
print(f"[c3] 최외곽 0.90Ru vs Ru: full-range {radius_bias:+.1f}% — 비교불가의 지배원인은 반경범위")
```

## 5. `wafer_measurement.schema.json` 개정 제안 (cmp-data-engineer 인계 — 파일 직접수정 금지)

현행 스키마([[../data/cmp-measurement-ingest-schema-standardization]] 소관)는 좌표·단위·notch·EE를 잘
잡지만, **지표 정의·응답량·포인트맵·불확도** 필드가 없어 Cal-1 매핑을 못 한다. 아래는 **제안**이며 구현은
cmp-data-engineer가 판단한다(§3 근거).

| 필드(제안) | 위치 | 타입/enum | 필수성 | 근거 | 효과 |
|---|---|---|---|---|---|
| `metric_definition` | record | enum: `wiwnu_3sigma`/`wiwnu_1sigma`/`cv`/`halfrange`/`fullrange`/`range_over_sum`/`raw_points_only` | 사전계산 스칼라 있으면 필수 | §2 D1–D5, §3.2 | 스칼라를 정본(D1)으로 해석·환산 |
| `measured_quantity` | record | enum: `post_thickness`/`pre_thickness`/`amount_removed`/`removal_rate`/`dishing`/`roughness` | 필수 | §3.3 Lee&Boning, Kumar 2019 | %-Std-Post vs %-Std-AR vs dishing 구분 |
| `scalar_wiwnu` | record | number\|null | 원 점 없을 때만 | §3.2 경로2 | 사전계산 값 보존(환산 입력) |
| `n_sites` | record | int | 필수 | §1.2 MF1618 | range형 비교가능성 판정 입력 |
| `outermost_radius_mm` | record | number | range형 스칼라면 필수 | §4-c3 (+23.5%) | 최외곽 반경 불일치 경고의 핵심 키 |
| `site_plan_name` | record | string(예 `p49_us6922603`,`p52_bibby_cartesian`) | 권고 | §1.1, [[inline-virtual-metrology-sampling-optimization]] | 포인트맵 식별 |
| `notch_reference_angle_deg` | record | number | 권고 | §1.1 Kumar(노치+90°선) | azimuthal 귀속·측정선 배향 |
| `site_size_mm` | point/record | `[26,8]` 등 | SFQR류면 필수 | §1.3 NIST 26×8mm | 사이트 평탄도(SFQR) 정의 완결 |
| `scan_size_um` | point | number | 조도값이면 필수 | [[wafer-surface-roughness-afm-scan-scale-dependence]] | 조도는 스캔크기 함수 |
| `value_uncertainty` + `coverage_k` | point | number | 권고 | [[../data/cmp-measurement-ingest-schema-standardization]] §1(GUM) | 신호/잡음 판별(캘리브레이션 가중) |
| `stat_ddof` | record | enum 0/1 | 권고 | [[uniformity-metrics-definitions-standards]] §3 | 소표본 σ 모/표본 구분 |

**주의**: `points`(원 좌표+value)를 받으면 D1~D5 전부 재계산되므로 위 스칼라 필드는 **원 점이 없는 레거시
입력용 폴백**이다(§3.2 경로1 우선). 스키마 `required`에 `points`를 유지하되, `raw_points_only` 경로를 정본으로 권장.

## 6. 남은 미확보·미검증 (정직성 표기)

- Bibby & Harwood 1997(DOI 10.1016/S0040-6090(97)00435-5): Crossref 실존하나 원문 PDF Cloudflare 차단,
  **초록만(E5)** — 49 vs 52점 정량 오차는 인용 못 함([[wafer-metrology-output-schema-site-flatness-standards]] §2와 동일).
- SEMI MF1618/ASTM F1618-02(DOI 10.1520/f1618-02): 실존, **스코프·초록만(E5)**. 사이트 배치 패턴의 정확한
  좌표표·통계식 원문은 유료 미확보 — "점 수 가변·절차 고정" 원칙만 스코프에서 확인.
- Doko 2026·Burwell 2023·Zhu 2022(D2/D3/D5 정의식): 각 DOI 실존·정의식 원문 스니펫 확인했으나 **전문 통독은
  안 함(E5, 하이라이트만)**. 정의식(수식)만 인용, 공정 수치는 인용 안 함.
- Lee & Boning 1999(DOI 10.1109/iwstm.1999.773193): 본문 유료, **초록·키takeaway만(E5)**. %-Std-Post/Std-AR
  명명은 academia.edu 키takeaway 기반 — 정확한 정의식 원문은 미대조.
- US6866792(Cabot, σ(Δ)/ave(Δ) 49점 제거량형): 특허 PDF가 스캔 이미지라 fitz 텍스트 추출 실패, **웹검색
  스니펫으로 식만 확인(E5)** — 본문 미판독. D2(제거량 응답)의 실사용 예로만 언급, 표 인용 없음.
- **1차 전문 확보(E2급)**: Kumar 2019(σ/mean·49site·dishing), NIST Griesmann 2007(EE 3→1.5mm·SFQR 26×8mm) —
  이 둘은 원문(imapsource PDF / AIP PDF fitz)을 직접 읽었다. 이 노트에서 가장 확실한 1차 근거.
- §4 샘플링 편향 수치(+4.6%/+23.5% 등)는 **합성 프로파일에 대한 이 노트의 직접 계산**이지 문헌 재현이 아니다
  (정직성 표지). 방향성(range형이 점 수·반경에 민감)은 Bibby & Harwood 정성 주장과 일치.

## 7. 자기시험
→ [[../../agents/wafer-metrology/EXAMS.md]] Cal-1 문항 참조.
