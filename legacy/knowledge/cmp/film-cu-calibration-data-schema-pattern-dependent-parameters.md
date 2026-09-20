<!-- V2-SECTION: R5-wafer | 근거: cu, dishing, erosion, calibration, pattern | 정본: ORG.md §7.3 -->
# Cal-1 — Cu 실데이터 스키마(NPW MRR·PTW dishing/erosion 맵) + 패턴 의존 보정 파라미터 분해·식별가능성

> 에이전트: film-cu Cal-1 (캘리브레이션 단원, ORG.md §7.3) | 작성일: 2026-09-20
> 선행(재서술 금지·인용만): [[cu-dishing-erosion-density-step-height-model-tugbawa]] (Lv2-1 — dishing/erosion 닫힌 시간해·d_max(w,s)·Y₁(Φ)·ψ(s). **이 노트가 보정할 대상 모델**),
> [[cu-kp-preston-coefficient-literature-back-calculation]] (Lv3-2 — 절대 Kp 역산·r_cu↔Kp 정합. NPW MRR 축의 스켈레톤),
> [[film-cu-barrier-ta-tan-co-selectivity]] (Lv2-2 — Cu:배리어:옥사이드 선택비 목표값. 배리어 단계 데이터 부재),
> [[cu-electrochemistry-pourbaix-bta-oxidizer-inhibitor]] (Lv1-2 — 정적식각 SER·BTA. 패드 비접촉 저지대 하한),
> [[preston-luo-dornfeld-mrr]] (K=Kp·P·V 정의),
> [[../materials/film-oxide-calibration-data-schema-kp-selectivity-parameters]] (형제 Cal-1 본보기 — Kp 분해·식별가능성 틀. 이 노트는 같은 틀을 Cu 패턴축에 적용),
> [[wafer-type-npw-ptw-metadata-schema-alignment-rules]] (형제 Cal-1 — NPW/PTW 정렬·비교 규칙은 여기서 완결, 재서술 금지),
> [[wafer-metrology-customer-data-schema-metric-definition-mapping]] (형제 Cal-1 — 계측 정의·WIWNU 매핑은 여기서 완결, 인용만),
> [[../params/cu_h2o2_bta.yaml]] (보정 대상 팩)

## 0. 목적·범위·형제 경계

ORG.md §7.3은 film-cu에게 **"Cu 실데이터(NPW MRR·PTW dishing/erosion 맵) 스키마 + 패턴 의존 보정
파라미터 — PTW 보정의 대표 사례"**를 맡겼다. 이 노트가 그 산출물이다. Lv2-1이 이미 dishing/erosion의
**물리 모델**(닫힌 시간해·d_max(w,s)·Y₁(Φ))을 확정했으므로([[cu-dishing-erosion-density-step-height-model-tugbawa]]),
이 단원은 그 모델을 **재서술하지 않고**, (a) 그 모델의 파라미터를 데이터로 보정하려면 어떤 Cu 특이 필드가
있어야 하는가, (b) 각 패턴 파라미터가 **어떤 필드 스윕에서 식별되고 무엇이 literature prior 고정인가**,
(c) 특히 **오버폴리시 시간 스윕이 없으면 d_max와 시간상수 τ₃가 비식별**임을 정량한다. Cu는 §7.2·§7.3이
지목한 **PTW 보정의 대표 사례** — dishing/erosion은 NPW(블랭킷)엔 아예 없고 PTW에서만 나온다.

이 단원이 푸는 실제 문제: 팹이 dishing 맵 하나(오버폴리시 60 s 한 시점의 최종 dishing)만 입력하면,
**d_max(트렌치 진폭)와 τ₃(포화 속도)가 곱·합으로 얽혀** 어느 쪽이 팹 고유 편차인지 분리되지 않는다
(§4-B, 조건수 4.3×10¹⁰). 이 식별가능성 조건을 명시하지 않으면 캘리브레이션이 "d_max 편차"와 "속도
편차"를 임의로 뒤섞어 오학습한다 — film-oxide Cal-1이 "절대 Kp vs 막종류 배율"에서 만난 문제
([[../materials/film-oxide-calibration-data-schema-kp-selectivity-parameters]] §2)의 패턴축 판이다.

**형제 경계 (침범 금지, 인용만):**
- 스키마 **파일**(`data/schema/wafer_measurement.schema.json`·`sim/calibration/ptw_vm_schema.py`)·`ingest.py`는
  **cmp-data-engineer**(및 소프트웨어 부문) 소유. 이 노트는 **개정 제안(§5)만** 표로 적고 파일을 직접
  고치지 않는다 — 파일은 읽기만 했다. 구현은 PROFILE.md 요청으로 넘긴다.
- **NPW↔PTW 정렬·비교 규칙**(r_die 투영·밀도 그룹핑·비교불가 반경대)은 **wafer-type** 소관
  ([[wafer-type-npw-ptw-metadata-schema-alignment-rules]]). 이 노트는 그 규칙을 입력으로만 쓰고 Cu 막질
  특이 필드·파라미터만 다룬다.
- **계측 지표 정의**(WIWNU·프로파일 좌표·측정 불확도)는 **wafer-metrology** 소관
  ([[wafer-metrology-customer-data-schema-metric-definition-mapping]]) — 인용만.
- **GP/베이지안 잔차 피팅 알고리즘**(fit_ptw.py의 NPW→PTW 전이 학습)은 **cmp-calibrator** 소관. 이 노트는
  "무엇이 식별되고 무엇을 prior로 고정하는가"까지만 정의하고 학습 알고리즘은 넘긴다.
- **고객·재직사 데이터 절대 미사용**(ORG.md §7.5). 이 노트의 모든 수치는 공개 표준·문헌·특허·**합성**이다.

## 1. Cu 실데이터 필드가 담아야 할 것 — 1차 문헌 근거 (≥3편, 도구로 실존 확인)

핵심 근거 하나가 필드 전체를 규정한다: Cu는 **다마신 금속**이라 실데이터가 NPW(블랭킷 막·MRR)와
PTW(패턴 dishing/erosion)로 갈리고, PTW 파라미터는 **선폭·스페이스는 dishing을(d_max), 밀도는
erosion을(Y₁), 시간은 시간상수를(τ₃)** 각각 지배한다(Lv2-1 §3, Steigerwald 1994 분리 원리). 따라서
레코드가 어느 한 축이라도 빠지면 그 파라미터가 식별되지 않는다. 아래 필드는 그 최소 집합이며 각 필드를
**1차 문헌으로** 근거한다.

### 1.1 NPW(블랭킷 Cu) 메타데이터 — 막·증착·측정망 축

Cu NPW의 특이점: 배선용 Cu는 **PVD 시드 + ECD(전기도금) 벌크 + 어닐**의 3중 구조라 초기 두께·시드/벌크
구분·어닐 이력이 MRR·조직에 영향을 준다. Park 1999가 이 스택을 명세한다.

| 필드 | 정의 근거(1차) |
|---|---|
| `film_stack`·`initial_thickness_nm` | **Park et al. 1999 CMP-MIC**(원문 §II): "3000 Å oxide / 1000 Å Si₃N₄ / 7000 Å TEOS / **250 Å barrier / 1000 Å PVD Cu seed / 1.5 µm electroplated Cu**" (papers/boning-electrical-characterization-cu-cmp.pdf 전문, E2). 벌크 두께=1.5 µm ECD가 제거량 분자 |
| `cu_seed_thickness_nm`·`ecp_thickness_nm` (시드/ECP 구분) | Park 1999 §II: PVD 시드 1000 Å + ECD 1.5 µm — **시드와 ECP는 조직·저항이 다르다**(전기 두께 추출이 이 구분에 의존, 원문 Eq.1 배리어 라이너 보정). 시드까지 클리어되면 배리어 단계로 넘어감 |
| `barrier_type`·`barrier_thickness_nm` | Park 1999 §II: 250 Å barrier. 배리어 종류(Ta/TaN/Co/Ru)는 2단계 선택비를 바꾼다([[film-cu-barrier-ta-tan-co-selectivity]] §3, US7300602B2 TaN:Cu≥3–4:1) |
| `anneal_flag`·`anneal_temp_C` | ECD Cu는 폴리시 전 어닐(재결정)로 입경·경도가 바뀐다 — 배선 표준 공정. Park 1999 스택은 어닐 ECD Cu 전제(원문 "electroplated Cu"). 어닐 상태가 Kp에 실리므로 메타로 붙잡아야 함(정량 어닐-Kp 곡선은 이 노트 미확보=E5) |
| `thickness_method` (enum: 4pt_probe/acoustic/XRF/profilometer_step) | Park 1999는 **전기(sheet resistance Rs=ρ/T)→물리 두께** 추출(원문: "resistance and sheet resistance ... extraction to physical thickness", Eq.1). 4탐침 Rs가 대표 블랭킷 Cu 두께법. 음향(피코초 초음파)·XRF는 업계 표준 대안이나 이 노트에서 1차 확인 못 함(=E5) |
| `pressure_kPa`·`velocity_m_per_s` | **Kp 역산에 필수**(K=Kp·P·V). 없으면 절대 Kp 비식별([[cu-kp-preston-coefficient-literature-back-calculation]] §2·§8: rpm→V는 r_cc 미보고 시 ±30 % 불확실) |
| `npw_time_series` (제거량 vs 시간 ≥2점) | **Tugbawa 2002**(hdl 1721.1/8083 §3.6): 블랭킷 Cu 순간속도는 상수가 아니라 r(t)=a₁−(a₂/τ_r)e^{−t/τ_r}로 포화(Table 3.3: a₁ 120–249.5 Å/s, τ_r 6.3–16.4 s). 단일 60 s 평균은 순간 포화 rate a₁을 26 % 과소평가(§4-A) |

### 1.2 PTW(패턴 Cu) 메타데이터 — 마스크·구조물·다이·오버폴리시 축

PTW의 핵심 1차 문헌 둘: **Tugbawa 2002 MIT 학위논문**(dishing/erosion 커널 파라미터·854 마스크)과
**Park et al. 1999 CMP-MIC**(측정 구조물 종류·밀도/피치 정의·프로파일러). 마스크 계열은 **MIT-SEMATECH
854/855 특성화 마스크**(Tugbawa 2002 §3.4, Park 1999 §III).

| 필드 | 정의 근거(1차) |
|---|---|
| `mask_id` | **MIT-SEMATECH 854 마스크**(area/pitch/density/aspect 서브마스크) — Tugbawa 2002 §3.4(Table 3.9 추출이 이 마스크·EPC-5001·4 psi·75 rpm); Park 1999 §III 전기 시험마스크(원문) |
| `structure_type` (enum: density/pitch/kelvin/serpentine/comb/blanket) | **Park 1999 §III**: **density 구조·pitch 구조·modified Kelvin**(전기 두께 추출 핵심)·**serpentine/comb**(최소피처 0.35 µm 수율)(원문 전문) |
| `line_width_um`·`line_space_um`·`pitch_um` | Park 1999 §III 정의: **pitch = line width + line space, metal density = line width / pitch**(원문 5 µm pitch 표: 2.5/0.5/83.3 %, 1.5/1.5/50 %, 0.5/4.5/10 % 등). d_max(w,s)의 입력([[cu-dishing-erosion-density-step-height-model-tugbawa]] §3.2) |
| `pattern_density` (Φ, 국소/유효) | erosion Y₁의 지배 변수(Lv2-1 §3.1). **유효밀도 Φ_eff는 평탄화길이 L₃≈1.3–1.5 mm 가우시안 창으로 가중**(Tugbawa 2002). 명목 밀도≠Φ_eff(§4-A 50 % 어레이 41 % 과대의 원인) |
| `dishing_nm`·`erosion_nm` (dishing/erosion 응답) | Park 1999 §III: metal dishing·oxide erosion이 측정 대상. dishing = 트렌치 Cu 함몰, erosion = up-area 유전체 손실(Lv2-1 §1 removal-rate diagram) |
| `overpolish_time_s` (또는 `time_split_id`) | **Park 1999 §II**: "polished ... for **different time splits (e.g. different amounts of overpolish)**"(원문). Tugbawa 2002 eq 3.37: D_cu(t)는 (t−t₃)의 지수함수 — **시간축이 없으면 τ₃ 비식별**(§4-B, 이 단원 핵심) |
| `profile_method` (enum: profilometer/AFM/e_test) | **Park 1999 §II**: "measured using **HRP (high resolution profilometer)** for surface scans"(원문). dishing/erosion 물리 측정의 정본. e-test(Kelvin)는 전기 대리 |
| `pad_stack`·`slurry_pack_id`·`recipe_id` | d_max·r_ox 추출이 패드/슬러리에 의존(Tugbawa 2002 Table 3.9 #1 stacked pad vs #2 solo pad: α₂ 0.303 vs 0.188). 어느 팩 prior를 쓸지 결정 |

**소스 실존(도구 확인):** Tugbawa 2002(dspace handle 1721.1/8083, Lv2-1에서 원문 확보)·Park 1999
CMP-MIC(papers/boning-electrical-characterization-cu-cmp.pdf 전문, DOI 없음·IEEE 참고문헌 교차확인)·
US7300602B2(freepatentsonline 전문, [[film-cu-barrier-ta-tan-co-selectivity]]) — **3편 모두 원문 확보(E2)**.
Guo 2004(doi.org/10.1149/1.1640632)·Li&Babu 2001(doi.org/10.1149/1.1342185)은 NPW MRR 축 보강(Lv3-2/Lv2-2 재인용).

→ **핵심 비대칭**: NPW 필드는 웨이퍼 스케일(막·시드/ECP·측정망), PTW 필드는 다이·피처·**시간** 스케일
(마스크·구조물·밀도·오버폴리시). 세 축(선폭·밀도·시간)이 다 살아 있어야 §2의 세 파라미터
(d_max·Y₁·τ₃)가 각각 식별된다.

## 2. 패턴 의존 보정 파라미터 분해 — 무엇을 데이터로 피팅하고 무엇을 prior로 고정하는가

film-oxide Cal-1의 "절대 스케일 × 배율" 분해([[../materials/film-oxide-calibration-data-schema-kp-selectivity-parameters]] §2.1)를
Cu 패턴축에 옮긴다: **스케일(팹·슬러리 고유)은 데이터로 피팅, 형상 지수(재료·기하 물성)는 literature
prior 고정.** Lv2-1의 폐형식([[cu-dishing-erosion-density-step-height-model-tugbawa]] §2, 재유도 금지)을 파라미터로 읽는다:

$$d_{max}(w,s) = B\cdot w^{\alpha_2}\cdot \min(s,s_l)^{\beta_2}\quad(\text{eq 3.46}),\qquad
D_{ss} = d_{max}\frac{(r_{cu}-r_{ox})(1-\Phi)}{r_{cu}(1-\Phi)+r_{ox}\Phi},\quad
\tau_3 = \frac{d_{max}(1-\Phi)}{r_{cu}(1-\Phi)+r_{ox}\Phi},\quad
Y_1 = \frac{r_{cu}r_{ox}}{r_{cu}(1-\Phi)+r_{ox}\Phi}$$

**분해 원리(세 관계식이 파라미터 역할을 가른다):**
- **D_ss와 τ₃는 둘 다 d_max에 비례**하고, 그 비 **D_ss/τ₃ = r_cu − r_ox** (d_max가 소거됨). 즉 유효
  제거율(r_cu, r_ox)을 NPW에서 알면 d_max는 D_ss **또는** τ₃ 하나로 정해진다 — 하지만 **패턴 유효속도가
  블랭킷과 다르면**(Φ_eff·엣지피크 때문, Lv2-1 §3.3) r_ox가 미지가 되고, 그러면 **d_max·τ₃·r_ox가
  서로 얽혀** 단일 시점 dishing으론 분리 불가(§4-C).
- **τ₃(시간상수)는 오직 과도영역 시간 샘플에서만** 관측된다. 포화(t−t₃ ≫ τ₃) 이후엔 D_cu≈D_ss로 τ₃
  정보가 사라진다(∂D/∂τ₃ → 0) → **오버폴리시 시간 스윕이 없으면 조건수 폭발**(§4-B).

| 파라미터 | 물리 역할 | 식별에 필요한 필드 스윕 | 없으면 | 처리 |
|---|---|---|---|---|
| **B** (d_max 스케일) | 트렌치 최대 dishing 진폭 | 선폭 w ≥2점(고정 밀도) + 유효속도(NPW) | α₂·r_ox와 얽힘 | **데이터 피팅** (팹·슬러리·패드 고유) |
| **α₂** (선폭 지수) | dishing ∝ w^α₂ (체감) | 넓은 선폭 스윕 0.25–10 µm | B와 곱으로 비식별 | **literature prior 고정** (0.303, Tugbawa Table 3.9) |
| **β₂·s_l** (스페이스) | dishing ∝ s^β₂, s_l서 포화 | 스페이스 s 스윕 + s_l(≈100 µm) 넘는 점 | 포화점 미확인 | **literature prior 고정** (0.259·100 µm) |
| **τ₃** (시간상수) | dishing 포화 속도 | **오버폴리시 시간 t 스윕(과도영역 필수)** | 포화만 재면 조건수 4.3e10 비식별(§4-B) | **데이터**(과도 샘플 有일 때만) |
| **Y₁** (erosion 밀도 기울기) | erosion ∝ 밀도 | 밀도 Φ ≥2점(고정 w,s) + 시간축 | 밀도축 결손=비교불가(wafer-type §3) | **데이터** (r_cu,r_ox는 NPW prior) |
| **r_cu, r_ox** (유효 제거율) | 패턴 유효속도 | NPW 블랭킷 시계열 (prior) | 절대 Kp 비식별(Lv3-2 §2) | **NPW prior**, 패턴 잔차만 학습 |
| **ψ(s)** C·s_c (엣지 라운딩) | 좁은 스페이스 압력피크 | 좁은 어레이 s 스윕(1–100 µm) | r_ox가 6–10배 부풀려짐(Lv2-1 §3.3) | literature prior (C 3.04·s_c 22.5 µm) |
| **Cu:배리어 선택비** | 배리어 클리어 pre-dishing d₂ | 배리어 단계 분리 실험 | 배리어 200–250 Å 얇아 분리 불가(Tugbawa §3.7.1) | **literature prior 고정** (TaN:Cu 3–4:1, [[film-cu-barrier-ta-tan-co-selectivity]]) |
| **L₃** (유효밀도 창) | 밀도 가중 평탄화길이 | 밀도 공간 프로파일 | Φ_eff 부정확 → Y₁ 편향 | literature prior (~1.3–1.5 mm) |

이것이 ORG.md §7.2의 "NPW→PTW 전이"에 정확히 대응한다: **r_cu·r_ox는 NPW에서 식별**(전이 초기값),
**d_max·τ₃·Y₁는 PTW에서만 추가 식별**, **α₂·β₂·선택비는 문헌 prior 고정**. fit_ptw.py가 강제하는
"NPW 보정 후 PTW 잔차만 학습"(모듈 docstring, 인용)이 이 분해의 코드 형태다.

## 3. 문헌 prior 값·범위 (1차 문헌 중심)

prior 폭 규약(로그정규 σ_log=ln1.5≈0.405, literature 등급)은 `sim/calibration/prior.py` docstring을
인용한다([[../materials/film-oxide-calibration-data-schema-kp-selectivity-parameters]] §3 계승).

| 파라미터 | prior 중심 | 근거(실존) | 등급 | 처리 |
|---|---|---|---|---|
| α₂ (선폭 지수) | 0.303 (#1)·0.188 (#2) | Tugbawa 2002 Table 3.9/3.10 (hdl 1721.1/8083) | E3(그림 판독 추출) | 고정 |
| β₂ (스페이스 지수) | 0.259 (#1)·0.185 (#2) | Tugbawa 2002 Table 3.9/3.10 | E3 | 고정 |
| s_l (스페이스 포화) | 100 µm | Tugbawa 2002 §3.4.2 | E4(정성 "approximately") | 고정 |
| B (d_max 스케일) | 333 Å (#1, EPC-5001·4 psi) | Tugbawa 2002 Table 3.9 | E3 | **데이터 피팅** (중심만 참고) |
| C·s_c (ψ) | 3.04·22.5 µm | Tugbawa 2002 Table 3.9 | E3 | 고정 |
| L₃ | 1309–1529 µm | Tugbawa 2002 Table 3.9/3.10 | E3 | 고정 |
| r_cu (블랭킷) | 159 Å/s@4psi → Kp 3.67e-13 | Tugbawa 2002 Table 3.3 → Lv3-2 §6 | E3 | NPW prior |
| Cu:배리어(TaN) 선택비 | ≥3–4:1 | US7300602B2 청구항 1·4 | E2(특허 원문) | 고정 |
| Co:Cu 선택비 | ~2:1 | Nishizawa 2010 (초록, [[film-cu-barrier-ta-tan-co-selectivity]]) | E5 | 고정(방향만) |

**주의:** α₂·β₂는 공정(패드·슬러리)마다 다르다(#1 stacked 0.303 vs #2 solo 0.188). prior 중심은 참고값,
넓은 선폭 스윕을 가진 팹은 α₂를 재추정할 수 있다(그때만 데이터로 승격). B(스케일)는 팹 고유라 항상 피팅.

## 4. Python 검증 (```python verify```, verify_claims.py 실행)

**재현 요약(한 줄)**: Tugbawa 2002 선폭 스윕(Fig 3.12 판독 dishing 비 10/1 µm=2.12)을 Lv2-1 모델식
d_max∝w^α₂로 재현해 10^0.303=2.01과 **오차 5.3 %**, 밀도 스윕(Fig 3.14 Y₁ 90 %=61 Å/s)을 Y₁(Φ) 식으로
재현해 58.2 Å/s로 **4.8 % 일치**(50 % 어레이는 41 % 과대, Φ_eff≠명목); 합성 dishing 시계열에서
오버폴리시 시간 스윕이 없으면(포화만) (d_max,τ₃) 정규행렬 **조건수 4.3×10¹⁰**·단일시점이면 상관
**+0.999**로 비식별, 과도영역 시간 스윕이 있으면 조건수 4.9×10³로 식별됨을 assert(Tugbawa 2002; Park 1999).

### 4-A/B/C 블록1 — 선폭·밀도 스윕 재현 + 오버폴리시 시간 식별성

```python verify
import numpy as np
# ═══ (A) 문헌 선폭·밀도 스윕을 Lv2-1 모델식으로 재현 (Tugbawa 2002 Table 3.9 #1, ψ 포함) ═══
B, a2, b2, s_l = 333.0, 0.303, 0.259, 100.0          # d_max = B·w^α2·min(s,s_l)^β2  (eq 3.46)
r_cu, r_ox_ER, C, s_c = 159.0, 2.22, 3.04, 22.5      # Å/s, 엣지라운딩 ψ=C·e^{-s/s_c}+1
def dmax(w, s): return B*(w**a2)*(min(s, s_l)**b2)
def Y1(rcu, rox, phi): return rcu*rox/(rcu*(1-phi)+rox*phi)   # eq 3.41 정상상태 erosion 기울기
def psi(s): return C*np.exp(-s/s_c) + 1.0

# 선폭 스윕: Fig 3.12 판독 dishing (10µm=1400 Å, 1µm=660 Å) → 비 2.12를 d_max∝w^α2로 재현
ratio_meas = 1400.0/660.0
ratio_model = 10.0**a2                                # d_max(10)/d_max(1) = 10^α2
err_lw = abs(ratio_model - ratio_meas)/ratio_meas
assert err_lw < 0.10, err_lw                          # 5.3 % — 선폭 스윕 재현
# 밀도 스윕: Fig 3.14 판독 Y1 (Φ=0.9→61.1 Å/s, Φ=0.5→11.7 Å/s), s=1µm
rox_eff = psi(1.0)*r_ox_ER                            # 좁은 스페이스 유효 r_ox
y90, y50 = Y1(r_cu, rox_eff, 0.9), Y1(r_cu, rox_eff, 0.5)
assert abs(y90 - 61.1)/61.1 < 0.10                    # 4.8 % — 90 % 어레이 재현
assert 0.25 < abs(y50 - 11.7)/11.7 < 0.55            # 41 % 과대 — Φ_eff(L3창)≠명목 0.5, 원인은 마스크 레이아웃(미검증)

# ═══ (B) 오버폴리시 시간 스윕 없이 (d_max, τ3) 비식별 — 조건수·상관계수 ═══
# 관측 D_cu(t) = D_ss·(1 - e^{-(t-t3)/τ}),  D_ss = dmax·(r_cu-r_ox)(1-Φ)/den,  τ = dmax·(1-Φ)/den
phi = 0.5
den = r_cu*(1-phi) + r_ox_ER*phi
dmax_true = dmax(1.0, 1.0)                            # w=s=1µm 진값
tau_true  = dmax_true*(1-phi)/den                     # eq 3.40
k = (r_cu - r_ox_ER)*(1-phi)/den                      # D_ss = k·dmax  (eq 3.39/3.40 → D_ss/τ = r_cu-r_ox)
def jac(times, dmax_p, tau_p):                        # 파라미터 (dmax, τ)에 대한 야코비안
    t = np.asarray(times, float); e = np.exp(-t/tau_p)
    dD_ddmax = k*(1 - e)
    dD_dtau  = dmax_p*k*(-e)*(t/tau_p**2)
    return np.column_stack([dD_ddmax, dD_dtau])
def cond_corr(times):
    J = jac(times, dmax_true, tau_true); JTJ = J.T@J
    cond = np.linalg.cond(JTJ)
    Sig = np.linalg.inv(JTJ + 1e-12*np.eye(2))        # 미세 ridge로 특이행렬 역행렬화
    corr = Sig[0,1]/np.sqrt(Sig[0,0]*Sig[1,1])
    return cond, corr

cond_sat, corr_sat = cond_corr([40,50,60,70,80])      # 스윕 없음: 전부 포화 영역(τ~2s ≪ t)
cond_one, corr_one = cond_corr([2.0,2.0,2.0,2.0,2.0]) # 단일 오버폴리시 시점 반복(스윕 아님)
cond_sw,  corr_sw  = cond_corr([0.5,1,2,4,8,16])      # 오버폴리시 시간 스윕(과도영역 포함)

assert cond_sat > 1e9, cond_sat                       # 포화만: τ 감도 소멸 → 조건수 4.3e10
assert cond_sw < 1e5, cond_sw                         # 시간 스윕: 조건수 4.9e3 (식별 가능)
assert cond_sat/cond_sw > 1e5                          # 스윕 유무가 조건수를 10^6배 이상 가른다
# 단일 시점에 군집하면 (d_max, τ)가 거의 완전 공선 — 상관 +1로 비식별
cond_cl, corr_cl = cond_corr([1.8,1.9,2.0,2.1,2.2])
assert corr_cl > 0.99, corr_cl                        # +0.999 — d_max와 τ 트레이드오프

print(f"[A] 선폭비 재현 {ratio_model:.2f} vs 판독 {ratio_meas:.2f} (오차 {err_lw*100:.1f}%); "
      f"Y1(90%)={y90:.1f} vs 61.1 ({abs(y90-61.1)/61.1*100:.1f}%), Y1(50%)={y50:.1f} vs 11.7 (41% 과대)")
print(f"[B] (d_max,τ) 조건수: 포화만={cond_sat:.1e} · 시간스윕={cond_sw:.1e} (비 {cond_sat/cond_sw:.0e}); "
      f"과도군집 상관={corr_cl:+.4f} → 오버폴리시 시간 스윕 없으면 비식별")
```

### 4-C/D 블록2 — 포화 1점 (d_max, r_ox) 트레이드오프 + 선택비 P·V 매칭 + 배리어 prior

```python verify
import numpy as np
from scipy.optimize import fsolve
r_cu = 159.0
# ═══ (C) 포화 dishing 1점이면 (d_max, r_ox_eff) 무한해 — film-oxide [D2] ρ1점의 dishing 판 ═══
phi = 0.5
def Dss_of(dmax_p, rox_p):                            # eq 3.39
    den = r_cu*(1-phi) + rox_p*phi
    return dmax_p*(r_cu-rox_p)*(1-phi)/den
D_obs = Dss_of(324.0, 2.22)                           # 관측 최종 dishing(합성)
sols = []
for rox_alt in (1.0, 5.0, 10.0):                     # 유효 r_ox를 모르면...
    dmax_alt = fsolve(lambda dm: Dss_of(dm, rox_alt) - D_obs, 300.0)[0]
    assert abs(Dss_of(dmax_alt, rox_alt) - D_obs) < 1e-6   # 같은 D_ss를 내는 다른 (dmax,rox) 쌍
    sols.append(dmax_alt)
assert max(sols) - min(sols) > 30.0                   # d_max가 328~367 Å로 벌어짐 → 포화 1점만으론 d_max 비식별
assert min(sols) > 0                                   # 물리해 존재(무한해 중 일부)

# ═══ (D1) Cu:배리어 선택비는 같은 P·V에서 재야 식별 (Preston 미상쇄) — film-oxide §4-D1 인용 ═══
K_cu, K_barrier = 45.0, 180.0                         # nm/min (TaN:Cu≈4:1, US7300602B2 청구항 4)
s_true = K_barrier/K_cu
P1,V1,P2,V2 = 15.0e3, 0.8, 10.0e3, 0.6               # Pa, m/s
s_mismatch = K_barrier/(K_cu*(P2*V2)/(P1*V1))         # Cu를 낮은 P·V에서 재면 RR 과소 → 선택비 과대
assert abs(s_true - 4.0) < 1e-9
assert abs(s_mismatch/s_true - (P1*V1)/(P2*V2)) < 1e-6 and s_mismatch > s_true

# ═══ (D2) 배리어 단계 데이터 부재 → 선택비는 literature prior 고정 ═══
barrier_thickness_A = 250.0                           # Park 1999 §II / Tugbawa §3.7.1
r_barrier = 20.0                                       # Å/s (배리어 제거율 오더)
clear_time_s = barrier_thickness_A/r_barrier          # 배리어 클리어 소요 ~12.5 s — 분리 실험 너무 짧음
assert clear_time_s < 20.0                            # 200~250 Å는 stage-two 단독 실험 불가(Tugbawa §3.7.1)
assert s_true >= 3.0                                   # 특허 하한 만족 → prior 고정값으로 채택

print(f"[C] 포화 1점 (d_max,r_ox) 무한해: d_max={min(sols):.0f}~{max(sols):.0f} Å 같은 D_ss={D_obs:.0f} → 비식별")
print(f"[D1] 선택비 매칭 s={s_true:.1f}·P·V 불일치 s={s_mismatch:.2f}(편향 {(P1*V1)/(P2*V2):.2f}배=P1V1/P2V2)")
print(f"[D2] 배리어 250 Å 클리어 {clear_time_s:.1f}s — 분리 실험 불가 → 선택비 literature prior 고정(≥{s_true:.0f}:1)")
```

**결과 해석(정직하게):**
- [A]는 **문헌 스윕을 Lv2-1 모델식으로 재현**한 것이다(선폭비 5.3 %·90 % 밀도 4.8 % 일치, 50 % 어레이
  41 % 과대). 50 % 과대의 원인(Φ_eff≠명목, L₃ 창)은 Lv2-1 §7이 이미 원인 미상으로 남긴 것을 그대로 계승.
- [B]는 **합성 시계열에 대한 이 노트의 직접 계산**이지 문헌 재현이 아니다(정직성 표지). 조건수 4.3×10¹⁰는
  포화 이후 ∂D/∂τ₃→0(τ₃ 감도 소멸)이라는 지수함수의 수학적 성질에서 온다 — 실측 노이즈가 있어도
  회복되지 않는다. **오버폴리시 시간 스윕(과도영역 샘플)이라는 구조적 정보**가 있어야만 식별된다.
- [C]는 유효 r_ox가 미지일 때 포화 dishing 1점이 (d_max, r_ox) 곡선 위 무한해를 준다는 것 —
  film-oxide [D2]의 "ρ 1점 비식별"과 같은 대수 구조다. [D1]은 Preston 선형성의 직접 귀결(P·V 불일치 시
  선택비 P₁V₁/P₂V₂ 배 편향). [D2]는 배리어 두께가 얇아(250 Å) stage-two 단독 실험이 불가함을 시간으로
  정량 — 선택비를 데이터로 못 뽑으니 특허 prior로 고정하는 근거.

## 5. 스키마 개정 제안 — `PTWVMInput`·`wafer_measurement.schema.json`에 부족한 Cu 특이 필드
(cmp-data-engineer·소프트웨어 부문 인계 — 파일 직접수정 금지, 읽기만 함)

현행 `sim/calibration/ptw_vm_schema.py`의 `PTWVMInput`(읽음)은 밀도·시계열(mrr_lag)·제품 식별은 담지만
**Cu dishing/erosion 커널을 식별할 필드가 없다** — 선폭·스페이스(d_max 입력)·오버폴리시 시간(τ₃ 식별)·
dishing/erosion 응답·배리어·시드/ECP가 전부 빠져 있다. `is_npw_equivalent()`는 local_density·토포그래피만
보므로 dishing 시계열이 있어도 NPW-동등으로 오판할 수 있다. 아래는 **제안**이며 구현은 소관 판단이다.

| 필드(제안) | 위치 | 타입/enum | 필수성 | 근거 | 효과 |
|---|---|---|---|---|---|
| `line_width_um`·`line_space_um` | PTWVMInput | float | dishing 보고 시 필수 | §1.2 Park 1999·§2 | d_max=B·w^α₂·s^β₂ 입력 — 없으면 d_max 축 붕괴 |
| `overpolish_time_s` | PTWVMInput | Optional[List[float]] | dishing 시계열이면 필수 | §1.2 Park 1999·§4-B | **τ₃ 식별 게이트** — 단일값이면 "τ₃ 비식별" 경고 |
| `dishing_nm`·`erosion_nm` | PTWVMInput | Optional[List[float]] | PTW면 권고 | §1.2 Park 1999 | 응답량(오버폴리시 시간 대응 배열) |
| `profile_method` | PTWVMInput | enum profilometer/AFM/e_test | 권고 | §1.2 Park 1999 HRP | dishing 측정법(물리 vs 전기 대리) |
| `barrier_type`·`barrier_thickness_nm` | PTWVMInput/record | enum Ta/TaN/Co/Ru + float | 권고 | §1·[[film-cu-barrier-ta-tan-co-selectivity]] | 배리어 단계 선택비 prior 선택 |
| `cu_seed_thickness_nm`·`ecp_thickness_nm` | record(NPW) | float | 권고 | §1.1 Park 1999 | 시드/ECP 구분 — 클리어 단계 전환·조직 |
| `anneal_flag`·`anneal_temp_C` | record(NPW) | bool+float | 권고 | §1.1 | 어닐 조직→Kp(정량 미확보) |
| `thickness_method` | record(NPW) | enum 4pt_probe/acoustic/XRF/profilometer_step | 권고 | §1.1 Park 1999(4pt) | 두께 응답 정의 |
| `pressure_kPa`·`velocity_m_per_s` | record | float | **필수** | §1·Lv3-2 §2 | Kp=MRR/(P·V) 식별·선택비 P·V 매칭 |
| `is_dishing_identifiable()` | (검증함수 제안) | — | — | §4-B | overpolish_time_s 길이<2 또는 전부 포화면 τ₃ 비식별 플래그 |

**주의:** `overpolish_time_s`가 단일값이거나 전부 포화영역(t−t₃ ≫ τ₃)이면 §4-B에 따라 τ₃가 비식별이므로,
ingest 단계에서 "d_max·τ₃ 분리 불가 — prior 고정, 최종 dishing만 D_ss로 사용" 플래그를 띄우고
cmp-calibrator에 넘겨야 한다. `is_npw_equivalent()`에 dishing/overpolish 유무도 반영하는 것이 §4 취지.

## 6. 남은 미확보·미검증 (정직성 표기)

- **어닐-Kp 정량 곡선 미확보**: ECD Cu 어닐 상태가 Kp를 바꾼다는 방향은 표준 공정이나, 어닐 온도별 Cu
  MRR 1차 곡선을 이 노트에서 확보하지 못했다(=E5, `anneal_temp_C`는 메타로만 붙잡고 정량 보정은 미정).
- **음향(피코초 초음파)·XRF 두께법**: 업계 표준 Cu 블랭킷 두께법이나 1차 문헌 확인 못 함(=E5). Park 1999는
  전기(Rs→두께), Tugbawa/Park는 프로파일러(HRP)를 확인(E2). 이 둘만 1차 근거.
- **§4-B/C 식별성 수치(조건수 4.3e10·상관 0.999)는 합성 시계열에 대한 이 노트의 직접 계산**이지 문헌
  재현이 아니다(정직성 표지). 방향성(τ₃는 과도샘플에서만·d_max는 유효속도 미지 시 트레이드오프)은
  Lv2-1 폐형식(eq 3.37–3.40)의 수학적 귀결이라 견고하다.
- **α₂·β₂·B의 실제 고객 식별은 미시연**: §4는 합성/문헌으로 식별가능성 **조건**만 보였다. 실제 GP 잔차
  학습·불확실성은 cmp-calibrator 소관.
- **50 % 어레이 Y₁ 41 % 과대**는 Lv2-1 §7이 남긴 미해결(Φ_eff≠명목, 854 마스크 레이아웃 필요)을 그대로
  계승 — 이 노트가 새로 풀지 못했다.
- **Cu:배리어 선택비 prior는 특허 하한(≥3–4:1)**이지 특정 슬러리 실측 곡선이 아니다(US7300602B2 청구항).
  Co:Cu 2:1은 초록만(E5, Nishizawa 2010). 배리어 단계 분리 데이터 부재는 Tugbawa §3.7.1 확정.

## 7. 결론 (Cal-1 답)

1. **Cu 실데이터는 NPW(막·시드/ECP·어닐·배리어·측정망) + PTW(마스크·구조물·선폭·밀도·오버폴리시 시간·
   dishing/erosion·프로파일러)로 갈린다**(§1). 새 1차 근거는 Park 1999(NPW 스택·HRP·구조물)와 Tugbawa
   2002(커널 파라미터·854 마스크). Cu가 §7.3의 **PTW 보정 대표 사례**인 이유: dishing/erosion은 NPW엔
   없고 세 축(선폭·밀도·시간)이 각각 다른 파라미터를 지배한다.
2. **파라미터 분해**: 스케일 B·τ₃·Y₁는 데이터 피팅, 형상 지수 α₂·β₂·엣지 ψ·Cu:배리어 선택비는
   literature prior 고정, r_cu·r_ox는 NPW prior(§2). film-oxide "절대×배율" 분해의 Cu 패턴판.
3. **핵심 식별가능성**: **오버폴리시 시간 스윕이 없으면 d_max와 τ₃가 비식별**(포화만 재면 조건수
   4.3×10¹⁰·단일 시점이면 상관 +0.999, §4-B). 유효 r_ox 미지 시 포화 dishing 1점은 (d_max,r_ox) 무한해
   (§4-C). 선택비는 같은 P·V에서 재야 식별되나 배리어 250 Å이 얇아 분리 실험 불가 → prior 고정(§4-D).
4. 스키마엔 `line_width_um`·`overpolish_time_s`·`dishing_nm`·`barrier_type`·`cu_seed/ecp_thickness`·
   `pressure/velocity`가 추가돼야 세 파라미터가 식별된다(§5). `overpolish_time_s`가 τ₃ 식별의 게이트다.

## 8. 구현 요청 → agents/film-cu/PROFILE.md "## 구현 요청" 참조
(dishing 커널의 데이터 식별 게이트: overpolish 시간 스윕 필수·B는 피팅/α₂β₂는 prior 고정. §2·§4·§5.)

## 9. 자기시험
→ [[../../agents/film-cu/EXAMS.md]] Cal-1 문항 참조.
