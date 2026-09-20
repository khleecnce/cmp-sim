<!-- V2-SECTION: R5-wafer | 근거: npw, ptw, calibration, transfer | 정본: ORG.md §7.3 -->
# Cal-1 — NPW/PTW 메타데이터 스키마 소유 + 두 유형 실데이터 정렬·비교 규칙 (§7.2 전이 규칙의 구현)

> 에이전트: wafer-type Cal-1 (캘리브레이션 단원, ORG.md §7.3) | 작성일: 2026-09-19
> [[npw-ptw-transfer-rules-quantitative]] [[npw-ptw-test-wafer-fundamentals]] [[product-wafer-proxy-metrics-virtual-metrology]] [[npw-ptw-pattern-effect-gw-physics]] [[pattern-dependent-dishing-erosion]] [[wiwnu-pressure-velocity-wafer-scale]] [[wafer-metrology-customer-data-schema-metric-definition-mapping]] [[../data/cmp-measurement-ingest-schema-standardization]] [[../data/wafer-coordinate-units-outlier-cleaning]]

## 0. 목적·범위·형제 경계

ORG.md §7.3은 wafer-type에게 **"NPW/PTW 메타데이터 스키마 소유 + 두 유형 실데이터를
정렬·비교하는 규칙(=§7.2 전이 규칙의 데이터 구현)"**을 맡겼다. 이 노트는 그 산출물이다.
앞 단원(Lv1 정의·Lv3-2 전이 규칙)은 **재서술하지 않고 인용만** 한다. 이 단원이 새로 하는 일은
전이 규칙(물리)을 **데이터 필드 요구**로 번역하고, 같은 레시피의 NPW 반경 프로파일과 PTW 다이 맵을
**공통 좌표**로 정렬할 때 어느 반경 구간이 원리적으로 비교 불가능한지를 정량하는 것이다.

**형제 경계 (침범 금지, 인용만):**
- 스키마 **파일**(`data/schema/wafer_measurement.schema.json`)·`ingest.py`·좌표/단위 정규화는
  **cmp-data-engineer** 소유([[../data/cmp-measurement-ingest-schema-standardization]],
  [[../data/wafer-coordinate-units-outlier-cleaning]]). 이 노트는 **개정 제안(§5)만** 표로 적고
  파일을 직접 고치지 않는다 — 구현은 PROFILE.md 요청으로 넘긴다.
- 계측 **지표 정의**(WIWNU 5종·SFQR·조도)는 **wafer-metrology** 소관
  ([[wafer-metrology-customer-data-schema-metric-definition-mapping]]). 이 노트는 그 정의를 입력으로만 쓴다.
- 잔차 GP 보정(NPW→PTW 전이 학습 그 자체)은 **cmp-calibrator** 소관. 여기서는 "전이가 성립하려면
  어떤 메타 필드가 있어야 하는가"까지만 책임진다.
- **고객·재직사 데이터 절대 미사용**(ORG.md §7.5). 이 노트의 모든 수치는 공개 표준·문헌·특허·**합성**
  격자다.

## 1. NPW/PTW 메타데이터 필드의 1차 근거

두 유형은 **무엇을 메타로 붙잡아야 하는가**부터 다르다. NPW는 "막을 무엇으로 얼마나 쌓았고 어디를
쟀나", PTW는 "어떤 마스크의 어떤 구조물을 다이 어디에서 쟀나"다. 아래는 각 필드의 1차 근거다.

### 1.1 NPW(블랭킷) 메타데이터 — 막·측정망 축

| 필드 | 정의 근거(1차) |
|---|---|
| `film_stack`(막 종류) | Oji thesis 1999(LPCVD TEOS, MIT hdl 1721.1/80109, 원문 확인, [[npw-ptw-test-wafer-fundamentals]] §1 인용); Kim & Seo 2002 STI 블랭킷 = PECVD-TEOS+SiN(DOI: 10.1016/S0167-9317(01)00694-3, 원문 확인) |
| `deposition_method`·`initial_thickness_nm` | Kim & Seo 2002: PECVD-TEOS **16 000 Å** 블랭킷(원문 §2); Park 1999 CMP-MIC: 3000 Å oxide/1000 Å Si₃N₄/7000 Å TEOS/250 Å barrier/1000 Å PVD Cu seed/1.5 µm ECD Cu(원문 §II, 8″) |
| `wafer_lot` | Kim & Seo 2002: 상관 **85로트**·재현 **50로트**(원문 §3) — 로트가 회귀·드리프트의 최소 단위 |
| `site_plan_name`(측정 포인트 맵 ID) | US6922603B1: center+3 rings(8/16/24)=**49점** polar(특허 원문, [[npw-ptw-test-wafer-fundamentals]] §1); 점 수 가변·절차 고정은 SEMI MF1618/ASTM F1618-02(스코프만, E5, [[wafer-metrology-customer-data-schema-metric-definition-mapping]] §1.2 인용) |
| `edge_exclusion_mm` | SEMI M1 2–3 mm→1 mm 추세; NIST Griesmann 2007 EE **3→1.5 mm**(DOI: 10.1063/1.2799352, 원문 E2, [[wafer-metrology-customer-data-schema-metric-definition-mapping]] §1.3 인용); Kim & Seo는 7 mm |
| `npw_time_series`(제거량 vs 시간) | Tugbawa 2002: 블랭킷 rate는 시간의 비선형 함수 AR(t)=a₁t+a₂(e^{−t/τ}−1)(hdl 1721.1/8083 §3.6, 원문). **단일 60 s 평균이 아니라 여러 시점**이 있어야 순간 포화 rate a₁을 뽑는다(§3, [[npw-ptw-transfer-rules-quantitative]]) |

### 1.2 PTW(패턴) 메타데이터 — 마스크·구조물·다이 축

PTW의 핵심 새 1차 문헌은 **Park, Tugbawa, Boning, Chung(MIT), Hymes, Muralidhar, Wilks, Smekalin,
Bersuker(SEMATECH), "Electrical Characterization of Copper Chemical Mechanical Polishing,"
Proc. 1999 CMP-MIC Conf., Santa Clara, pp. 184–191**(저자 소속 리포지토리 boning.mit.edu 리프린트
PDF 전문 확인 = **E2급 1차**; DOI 없음, IEEE 참고문헌·US 특허 참고문헌 다수가 동일 서지로 교차확인).
이 논문이 PTW 시험마스크의 **구조물 종류·블록 크기·피치/밀도 정의**를 명세한다.

| 필드 | 정의 근거(1차) |
|---|---|
| `mask_id` | MIT **854/855 계열** 특성화 마스크(area/pitch/density/aspect submasks) — Boning et al. 1999 MRS99(원문, [[npw-ptw-test-wafer-fundamentals]] §2); Park 1999 CMP-MIC 전용 **전기 시험마스크**(원문 §III) |
| `structure_type`(측정 구조물 종류) | Park 1999: **density 구조**·**pitch 구조**·**modified Kelvin**(전기 두께 추출의 핵심)·**serpentine/comb**(최소피처 0.35 µm 수율)(원문 §III). Tugbawa 2002 dishing/erosion 구조([[npw-ptw-transfer-rules-quantitative]] §3) |
| `pitch_um`·`line_width_um`·`line_space_um` | Park 1999 정의: **pitch = line width + line space**, **metal density = line width / pitch = 면적비**(원문 §III). 최소피처 0.35 µm |
| `die_density_mean`·`local_density`·`pattern_density_map_ref` | 다이 평균 밀도와 국소(블록별) 밀도는 별개 축(Sorooshian 2005 유효압력비, [[product-wafer-proxy-metrics-virtual-metrology]] §4). 밀도 블록 크기 = 상호작용거리로 결정 |
| `block_size_mm`(구조물 블록) | Park 1999: **density 3×3 mm**·**pitch 2.5×3.0 mm** — 상호작용거리(oxide **3–5 mm**, Ouma CMP-MIC 1998)로 이웃 간섭을 디커플하도록 선정(원문 §III) |
| `die_size_mm`·`in_die_xy` | 표준 노광필드 **26×33 mm**(reticle limit, 최대 단일다이 858 mm², 반도체 산업 관행/ASML NXT·NXE, **E5 업계자료**); NIST Griesmann 2007 노광사이트 **25×25 mm**·SFQR **26×8 mm**(E2, 인용). 다이 내 구조물 위치(in_die_xy)는 US7539552B2식 (col,row)+아핀변환으로 물리좌표화([[../data/wafer-coordinate-units-outlier-cleaning]] §1.3) |
| `planarization_length_mm` | Ouma 1998 표 5.2 **2.90–4.50 mm**, 레시피·패드 의존·레이아웃 무관(hdl 1721.1/9704, [[npw-ptw-transfer-rules-quantitative]] §2). PTW 마스크에서만 추출 |

→ **핵심 비대칭**: NPW 메타는 전부 **웨이퍼 스케일**(막·측정망), PTW 메타는 **다이·피처 스케일**(마스크·
구조물·밀도)이다. 두 유형을 한 스키마에 담으려면 **wafer_type 구분 키**가 record 최상위에 있어야
필드 필수성이 갈린다(§5).

## 2. 정렬 규칙 — 공통 좌표로의 투영

같은 레시피로 돈 NPW 반경 프로파일과 PTW 다이 맵을 비교하려면 **공통 좌표**가 필요하다. 규칙은 둘이다:

1. **웨이퍼 반경 r로의 투영(die-center radius r_die)**: PTW 각 다이의 중심을 웨이퍼 중심에서의 반경
   `r_die = hypot(x_die, y_die)`로 사상한다. NPW의 반경 프로파일(방위각평균)과 **같은 축**이 된다.
   Ouma 1998의 "die-position dependent blanket rate"가 정확히 이 사상을 요구한다(NPW의 다이 위치별 K를
   PTW 모델에 넣으려면 다이→반경 매핑이 있어야 한다, [[npw-ptw-transfer-rules-quantitative]] §2).
2. **다이 내 국소 밀도별 그룹핑**: 같은 반경대에 여러 다이가 방위각으로 흩어져 있고, 각 다이 안에는
   density/pitch 블록이 여러 개다. 따라서 PTW는 **한 반경에서 밀도별로 나뉜 여러 값**을 주는 반면
   NPW는 **한 반경에서 방위각평균 한 값**만 준다. 비교는 "같은 r_die 빈 안에서 밀도로 그룹핑한 PTW
   유효 MRR" 대 "그 반경의 NPW MRR"로 한다.

이 투영에는 **두 가지 원리적 한계**가 있고, §4에서 합성 격자로 정량한다:

- **(L1) 외곽 비교불가 구간**: 완전인쇄(full-printed) 다이의 중심은 유효반경 Ru까지 못 간다 —
  다이 반쪽(반대각 ≈ 21 mm)만큼 안쪽에서 멈춘다. NPW의 최외곽 링(147 mm)에는 대응하는 PTW 다이 중심이
  없다. 이 외곽 annulus는 **NPW만 존재**한다(부분 다이는 패턴이 잘려 밀도 정의가 깨지므로 계측 제외).
- **(L2) 반경 스미어**: 다이 하나가 차지하는 반경폭(≈2×반대각 = 42 mm)이 NPW 81점 링 간격(29.4 mm)보다
  **크다**. 그래서 한 다이를 하나의 NPW 세밀 링에 **깨끗이 귀속시킬 수 없다** — 조밀한 49점 링
  간격(49 mm)보다는 작아 조립 링에만 할당 가능하다. 즉 **NPW의 반경 분해능을 PTW가 못 따라간다**.

## 3. 비교 규칙 — NPW MRR 대 PTW 유효 MRR(밀도 보정), 그리고 필드 요구

[[npw-ptw-transfer-rules-quantitative]] §5의 전이 파라미터 표(무엇이 NPW에서 오고 무엇이 PTW에서만
나오는가)를 **데이터 필드 요구**로 번역한다. 규칙: **비교는 "NPW MRR(블랭킷)"과 "PTW 유효 MRR(=RR_up
= K/ρ_eff, 밀도 보정)"을 같은 반경 빈에서** 한다(RR_up = K/ρ_eff는 Boning et al. 1999,
[[pattern-dependent-dishing-erosion]] §2). 이 비교가 성립하려면 아래 필드가 있어야 한다.

| 전이/비교 단계 | 필요한 메타 필드 | 결손 시 불가능해지는 것 | 근거 |
|---|---|---|---|
| 블랭킷 rate 순간화(60 s 평균→a₁) | NPW `npw_time_series`(≥2 시점) | 순간 포화 rate 미상 → NPW MRR이 **10–26 % 과소**, 유효 MRR 비교 편향 | Tugbawa 2002 표 3.3 |
| 다이 위치별 K 사상 | NPW `site_plan_name`+PTW `in_die_xy`/(col,row)→r_die | 반경 정렬 불가 → NPW의 반경 프로파일을 PTW에 못 실음 | Ouma 1998 |
| 레시피 변환 | NPW·PTW 공통 `recipe_id`(다운포스·속도·패드·슬러리) | NPW↔NPW 변환계수(0.5–2) 못 씀 → 다른 레시피 NPW를 baseline으로 못 씀 | US20060116785A1 |
| 드리프트·제품 오프셋 분해 | `wafer_lot`/`run_index`·PTW `product_id`+`mask_id` | BR(n)=BR(0)+BR_Device(D)+Δ(n) 분해 불가 → 로트 드리프트를 패턴 효과로 오학습 | Boning et al. 1999 eq.5 |
| 유효 MRR 밀도 보정 | PTW `local_density`(또는 `die_density_mean`) | RR_up=K/ρ 계산 불가 → PTW 값을 NPW와 **직접 비교 금지**(밀도 축 결손) | Boning 1999 |
| 유효압력비 α(ρ) 검사 | PTW `local_density` | α(ρ)=P_eff/P_applied 못 붙임(2.2/1.7/1.3, GW 상한 1/ρ) | Sorooshian 2005; Vasilev 2011 |
| PL 재사용 | PTW `mask_id`+`planarization_length_mm`+`recipe_id`+패드 | PL 레이아웃 간 이전 불가(레시피·패드 바뀌면 재추출) | Ouma 1998 표 5.2 |

**한 줄 규칙**: `local_density`가 없으면 PTW 유효 MRR을 **정의할 수 없으므로** NPW와의 비교를 금지하고
(§5 `is_npw_equivalent` 인용), `npw_time_series`가 없으면 비교를 허용하되 **10–26 % 편향 경고**를 붙인다.

## 4. Python 검증 — 정의식·다이 격자 정렬·필드 결손 편향

합성 다이 격자(300 mm, 다이 26×33 mm)로 (a) Park 1999 구조물 정의식, (b) r_die 투영 커버리지와 두 원리적
한계(L1·L2), (c) 필드 결손 시 전이 편향을 assert로 정량한다. **격자는 합성**이며 문헌 재현이 아니다(정직 표지).

```python verify
import numpy as np, math

# ═══ (A) 메타 필드의 1차 근거 — Park 1999 CMP-MIC 시험구조물 정의식(문헌값 대조) ═══
# Park, Tugbawa, Boning et al., "Electrical Characterization of Cu CMP," 1999 CMP-MIC pp.184-191(원문).
lw, ls = 0.35, 0.35           # µm, 최소피처 line/space (Park 1999 §III)
pitch = lw + ls               # 정의: pitch = line width + line space
density = lw / pitch          # 정의: metal density = lw/pitch = 면적비
assert abs(pitch - 0.70) < 1e-12
assert abs(density - 0.5) < 1e-12          # 최소피처 serpentine/comb = 50% 밀도
den_block, pit_block = (3.0, 3.0), (2.5, 3.0)      # mm, Park 1999 §III 블록크기
interaction_oxide = (3.0, 5.0)                     # mm, oxide 상호작용거리 (Ouma CMP-MIC 1998)
assert den_block[0] >= interaction_oxide[0]        # 밀도블록 ≥ 상호작용거리 하한 → 이웃 디커플
DW, DH = 26.0, 33.0                                 # mm, 표준 노광필드(reticle limit)
assert abs(DW*DH - 858.0) < 1.0                     # 최대 단일다이 858 mm²

# ═══ (B) 정렬 규칙 — 합성 다이 격자 → r_die 투영, NPW 반경빈 커버리지 ═══
R, EE = 150.0, 3.0; Ru = R - EE                     # 300mm, EE 3mm → 유효반경 147mm
hw, hh = DW/2, DH/2
half_diag = math.hypot(hw, hh)                      # 다이 중심→최원corner = 21.01mm
xs, ys = [], []                                     # 중심 다이를 원점에 둔 격자
for i in range(-8, 9):
    for j in range(-6, 7):
        x, y = i*DW, j*DH
        if math.hypot(abs(x)+hw, abs(y)+hh) <= Ru:  # 완전인쇄(full-printed): 최원 corner ≤ Ru
            xs.append(x); ys.append(y)
xs, ys = np.array(xs), np.array(ys)
rdie = np.hypot(xs, ys)                             # 다이 중심 반경으로 투영
assert 55 <= len(xs) <= 60                          # 완전인쇄 다이 57개
assert rdie.min() < 1e-9                            # 중심 다이 존재 → 내측 반경 커버 OK

# (L1) 외곽 비교불가 구간: 완전다이 중심 최대반경이 유효반경보다 안쪽
rmax = rdie.max()
assert rmax/Ru < 0.90, rmax/Ru                      # 130/147 = 0.884
area_gap = (Ru**2 - rmax**2)/Ru**2
assert area_gap > 0.20, area_gap                    # 외곽 21.8% 면적: NPW만, PTW 다이중심 없음
assert np.sum(rdie > 135.0) == 0                    # 135mm 밖 다이중심 0 (부분다이 제외)

# NPW 반경 링 (49점: center+8/16/24, 81점: center+8/12/16/20/24)
r49 = np.array([Ru/3, 2*Ru/3, Ru])
r81 = np.array([Ru/5, 2*Ru/5, 3*Ru/5, 4*Ru/5, Ru])
n49_out = int(np.sum(r49 > rmax)); n81_out = int(np.sum(r81 > rmax))
assert n49_out == 1 and n81_out == 1                # 최외곽 링(147mm)만 다이중심 밖 → PTW로 비교불가

# (L2) 반경 스미어: 다이 하나가 차지하는 반경폭 vs 링 간격
die_span = 2*half_diag                              # 42.0mm
assert die_span > Ru/5                              # 42 > 29.4: 81점 링간격보다 큼 → 세밀 링 귀속 모호
assert die_span < Ru/3                              # 42 < 49: 49점 링간격보다 작음 → 조밀 링만 할당가능

# 밀도 그룹핑 가능성: 중간 반경대에 다이 여러 개(방위각 분산) → 국소밀도별 그룹핑 가능
mid = np.sum((rdie >= 90) & (rdie <= 110))
assert mid >= 3
bins = np.arange(0, 150+1, 25)
cnt, _ = np.histogram(rdie, bins=bins)              # 반경빈 다이수: 면적×격자로 증가하다 외곽서 급감

# ═══ (C) 비교 규칙 — 필드 결손 시 전이 편향(Lv3-2 전이표의 데이터화) ═══
# (C1) npw_time_series 없이 단일 60s 평균 MRR만 → 순간 포화 rate a1 과소평가
a1, a2, tau = 249.5, 3986.6, 16.4                   # Tugbawa 2002 표3.3 실험1 (Å/s, Å, s)
r_avg60 = a1 + (a2/60.0)*(math.exp(-60.0/tau) - 1)  # eq.3.52 평균 rate
deficit = 1 - r_avg60/a1
assert 0.24 <= deficit <= 0.27, deficit             # 60s 평균이 a1보다 26% 낮음 → 시계열 필드 필수
# (C2) local_density 없이 PTW 유효 MRR(RR_up=K/ρ, Boning 1999) 계산 불가
K = 200.0                                           # 임의 blanket rate (합성)
assert abs((K/0.5)/K - 2.0) < 1e-9                  # ρ=0.5 up-area는 블랭킷의 2배 → 밀도 필드 결손=비교불가
for rho in (0.2, 0.5, 0.8):
    assert abs((K/rho) - K*(1/rho)) < 1e-9

print("Cal-1 정렬·비교 규칙 검증 통과 (합성 격자, 문헌값 대조)")
print(f"[A] pitch={pitch}µm density={density} 블록 den{den_block}/pit{pit_block}mm 다이{DW:.0f}×{DH:.0f}={DW*DH:.0f}mm²")
print(f"[B] 완전다이 {len(xs)}개, r_die 0~{rmax:.0f}mm(={rmax/Ru:.3f}Ru), 외곽 {area_gap*100:.1f}% 비교불가, "
      f"다이스팬 {die_span:.0f}mm > 81링간격 {Ru/5:.0f}mm(세밀링 모호), < 49링간격 {Ru/3:.0f}mm")
print(f"[B] 반경빈(25mm) 다이수 {list(map(int,cnt))} — 외곽빈 급감")
print(f"[C] npw_time_series 결손: 60s평균 {deficit*100:.0f}% 과소 / local_density 결손: 유효MRR 정의불가")
```

## 5. 스키마 개정 제안 (파일 직접수정 금지 — cmp-data-engineer·소프트웨어 부문 인계)

현행 두 스키마는 Cal-1 정렬·비교에 필요한 필드가 부족하다. **핵심 결손은 NPW/PTW 구분 키 자체가 없다는
것**이다: `data/schema/wafer_measurement.schema.json`은 좌표·단위·notch·EE를 잘 잡지만 wafer_type 필드가
없고([[../data/cmp-measurement-ingest-schema-standardization]] 소관), `sim/calibration/ptw_vm_schema.py`의
`PTWVMInput`은 PTW VM 특징은 담지만 마스크·구조물·전이 필드가 없다. 아래는 **제안**이며 구현은 소관
에이전트가 판단한다(§1·§3 근거). 파일은 읽기만 했고 고치지 않았다.

### 5.1 `wafer_measurement.schema.json` (record 레벨)

| 필드(제안) | 타입/enum | 필수성 | 근거 | 효과 |
|---|---|---|---|---|
| `wafer_type` | enum `NPW`/`PTW` | **필수(구분 키)** | §1 비대칭 | 필드 필수성을 wafer_type별로 분기(allOf if/then) |
| `film_stack` | array of {material, method, thickness_nm} | 권고 | §1.1 Oji/Park 1999 | 막·증착·초기두께를 한 축으로 |
| `wafer_lot` | string | 권고 | §1.1 Kim&Seo 85/50로트 | 드리프트·회귀 최소단위 |
| `recipe_id` | string | 필수 | §3 레시피 변환 | NPW↔PTW 변환·PL 재사용 키 |
| `mask_id` | string | `wafer_type=PTW`면 필수 | §1.2 MIT 854/Park 1999 | 마스크 식별·PL 재사용 |
| `structure_type` | enum `density`/`pitch`/`kelvin`/`serpentine`/`comb`/`blanket` | PTW면 필수 | §1.2 Park 1999 §III | 측정 구조물 종류 구분(전기/물리) |
| `pitch_um`,`line_width_um`,`line_space_um` | number | PTW·구조물면 권고 | §1.2 Park 정의 | pitch=lw+ls, density=lw/pitch |
| `local_density`,`die_density_mean` | number [0,1] | PTW면 필수(유효 MRR용) | §3 RR_up=K/ρ | 밀도 보정·α(ρ) — 없으면 비교금지 |
| `block_size_mm` | [3,3]/[2.5,3] 등 | PTW면 권고 | §1.2 Park 3×3/2.5×3 | 상호작용거리 디커플 확인 |
| `die_size_mm` | [26,33] 등 | PTW면 권고 | §1.2 reticle limit | r_die 투영·외곽 커버 판정 |
| `planarization_length_mm` | number\|null | PTW·전이면 권고 | §3 Ouma 2.90–4.50 | PL 이전(레시피·패드 종속) |

`coord_kind=die`의 (col,row,pitch,col0,row0,x0,y0)는 이미 있으므로 r_die 투영은 현행 필드로 계산 가능
(파일 무수정, §4-B가 그 계산을 재현). 부족한 것은 **위 메타(밀도·구조물·마스크·전이)**뿐이다.

### 5.2 `PTWVMInput`(ptw_vm_schema.py) 추가 제안

| 필드(제안) | 타입 | 근거 | 효과 |
|---|---|---|---|
| `mask_id` | str | §1.2 | PL 재사용·마스크 식별 |
| `structure_type` | str(enum) | §1.2 Park 1999 | dishing/erosion 구조물 구분 |
| `pitch_um` | Optional[float] | §1.2 Park 정의 | density=lw/pitch 재계산 |
| `recipe_id` | str | §3 변환·전이 | NPW 짝·변환계수 키 |
| `npw_reference_id` | Optional[str] | §3 짝 실험(Tugbawa 표 5.7 B-7..11) | 전이 1단계 NPW 링크(없으면 순간화 불가 경고) |
| `planarization_length_mm` | Optional[float] | §3 Ouma | 레이아웃 간 이전 값 저장 |

기존 `local_density`·`die_density_mean`·`is_npw_equivalent()`(§5 인용)는 §3 "밀도 결손=비교금지"를 이미
판정한다 — 제안은 그 위에 **마스크·전이 링크 필드**를 얹어 §3 표의 나머지 행(레시피·PL·NPW 짝)을 검사
가능하게 만드는 것이다.

## 6. 미확보·미검증 (정직 표기)

- Park 1999 CMP-MIC(pp.184–191): 저자 리포지토리 PDF 전문 확인(E2급)이나 **DOI 없음**(학회 프로시딩) —
  실존은 IEEE 1309307 참고문헌·freepatentsonline 특허 참고문헌 다수의 동일 서지로 교차확인. 블록 크기·
  정의식은 본문 §III에서 직접 읽음.
- 다이 26×33 mm(reticle limit): SEMI 표준 원문이 아니라 **업계 관행/스캐너 벤더(ASML NXT·NXE) 자료 =
  E5**. §4의 격자는 이 크기를 **예시 입력**으로 쓴 합성 계산이지 특정 제품 레이아웃 재현이 아니다.
- §4-B의 커버리지 수치(57다이·0.884 Ru·21.8 %·42 mm 스팬)는 **이 노트의 직접 계산**이며 문헌 재현이 아니다
  (정직 표지). 다만 방향성(완전다이는 유효반경까지 못 감·부분다이 제외)은 계측 관행과 정합.
- 격자 배치(중심 다이를 원점에 둠)는 하나의 관례다 — 다이 코너를 원점에 두는 팹이면 r_die 분포가
  바뀐다(L1·L2 방향은 불변, 정확한 %는 배치 의존). **본 노트의 가정**으로 표기.
- §3 표의 전이 편향값(10–26 %·2×)은 [[npw-ptw-transfer-rules-quantitative]]가 이미 문헌으로 확정한 값의
  **재인용**이고 이 노트에서 새로 측정한 게 아니다.

## 7. 결론 (Cal-1 답)

1. **NPW 메타는 웨이퍼 스케일(막·증착·두께·로트·측정망), PTW 메타는 다이·피처 스케일(마스크·구조물·
   피치·밀도·다이좌표)**이다. 한 스키마에 담으려면 `wafer_type` 구분 키가 record 최상위에 있어야 필드
   필수성이 갈린다(§5). 새 1차 문헌 Park 1999 CMP-MIC가 PTW 구조물·블록·정의식을 준다.
2. **정렬은 다이 중심을 반경 r_die로 투영**해 NPW 반경 프로파일과 같은 축에 놓고, 같은 반경 빈 안에서
   **국소 밀도로 그룹핑**한다. 두 원리적 한계: (L1) 완전다이 중심은 유효반경의 0.884배까지만 가서
   외곽 21.8 % 면적이 NPW-only(비교불가), (L2) 다이 반경폭 42 mm가 NPW 81점 링 간격 29.4 mm보다 커서
   세밀 링 귀속이 모호(49점 조밀 링만 할당 가능).
3. **비교는 NPW MRR 대 PTW 유효 MRR(=K/ρ_eff)**로 하되, `local_density`가 없으면 유효 MRR을 정의할 수
   없어 비교를 금지하고, `npw_time_series`가 없으면 순간 포화 rate 미상으로 10–26 % 편향 경고를 붙인다.
   §3 표가 각 전이 단계의 필드 요구와 결손 시 불가능해지는 것을 정리한다.

## 8. 구현 요청
→ [[../../agents/wafer-type/PROFILE.md]] "## 구현 요청 (2026-09-19, wafer-type Cal-1)" 참조.

## 9. 자기시험
→ [[../../agents/wafer-type/EXAMS.md]] Cal-1 문항 참조.
