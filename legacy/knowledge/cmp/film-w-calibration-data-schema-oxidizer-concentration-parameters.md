<!-- V2-SECTION: R2-slurry | 공동: R5-wafer | Cal-1 2026-09-20 | 근거: W 실데이터 스키마·산화제 농도의존 보정 파라미터·식별가능성 | 정본: ORG.md §7.3 -->
# Cal-1 — 텅스텐 실데이터 스키마 + 산화제 농도 의존 보정 파라미터(Kp_W·f_ox·g_pH) 정의·식별가능성 (film-w)

> 에이전트: film-w Cal-1 (캘리브레이션 단원, ORG.md §7.3) | 작성일: 2026-09-20
> 선행(재서술 금지·인용만):
> [[w-cmp-preston-kp-oxidizer-rate-literature-reproduction]] (Lv3-2 — Kp 역산 median 1.1e-13·팩 2.8e-13 2.6배 과대·산화제 포화농도 종별 100배·f_ox 곡선 축 불일치. **이 노트가 보정으로 흡수할 대상**),
> [[w-cmp-plug-recess-coring-keyhole-overpolish-window]] (Lv2-1 — 리세스·코어링·심/키홀·Yu 버프 모델. PTW W 특이 필드의 물리 스켈레톤),
> [[w-cmp-ti-tin-barrier-selectivity-recess-erosion]] (Lv2-2 — Ti/TiN 배리어·W:배리어 U자 선택비),
> [[w-cmp-fenton-catalyst-abrasive-alumina-silica]] (Lv1-2 — Fe 촉매 Fenton·입자), [[w-cmp-wo3-passivation-oxidizer-kaufman]] (Lv1-1 — WO₃ 순환·정적식각),
> [[chi-oxidizer-curve-exponent-identifiability]] (판정#19 — (n,C_peak) 정점아래 완전축퇴 → Langmuir 1파라미터 대체),
> [[preston-luo-dornfeld-mrr]] (K=Kp·P·V 정의),
> [[calibration-parameter-registry-identifiability-sequential-fitting]] (cmp-calibrator Cal-1 — **레지스트리 표 §1, 이 노트 산출은 거기 추가될 행**),
> [[cmp-calibration-schema-integration-validation-rules]] (cmp-data-engineer Cal-1 — 통합 스키마 49필드, **W 필드 제안은 이것과 충돌 없이**),
> [[../materials/film-oxide-calibration-data-schema-kp-selectivity-parameters]] (형제 Cal-1 본보기 — Kp 절대×배율 분해·식별가능성 형식),
> [[slurry-abrasive-specsheet-to-model-input-conversion-rules]] (형제 Cal-1 — 스펙시트→입력 변환·곱구조 잔차 귀속),
> [[../params/w_fe_oxidizer.yaml]] (보정 대상 팩)

## 0. 목적·범위·형제 경계

ORG.md §7.3은 film-w에게 **"W 실데이터(막질·MRR·선택비·결함) 스키마 + 보정 파라미터(막질별 Kp·화학 상수·선택비) 정의"**를
맡겼고, film-w의 캘리브레이션 단원 특기 축은 **산화제 농도 의존**이다. Lv3-2가 이미 세 사실을 세웠다
([[w-cmp-preston-kp-oxidizer-rate-literature-reproduction]]): (1) 팩 `kp_m_per_pa=2.8e-13`은 3문헌 역산 median 1.1e-13의
**~2.6배 과대**, (2) 팩 산화제 곡선(H₂O₂ 스케일)이 선언종 Fe(NO₃)₃의 포화농도(~0.1 wt%)와 **~100배 불일치**,
(3) W는 산화-제거 순환이라 산화제가 부족하면 MRR이 포화한다. 이 단원은 그 진단을 **재서술하지 않고**, 그것이
**고객 데이터로 어떻게 식별·보정되는가** — 무엇이 피팅 대상이고 무엇을 prior로 고정하며, 산화제 종류가 바뀌면
어느 파라미터가 재설정되는가 — 를 정의한다. 이것이 옥사이드 Cal-1(절대 Kp×막종류 배율)의 **W 산화제 판본**이다.

이 단원이 푸는 실제 문제: W MRR을 입력했을 때 **절대 Kp를 올리는 것과 산화제 곡선 최대값 f_max를 올리는 것이
같은 MRR을 낸다**(둘은 곱 `Kp_ref·f_ox`). 그리고 **산화제 종류를 명시하지 않으면** 캘리브레이터가 Fe(NO₃)₃ 데이터를
H₂O₂ 곡선(반포화 ~6 wt%)에 맞추려 Kp_ref를 왜곡한다. 이 두 식별가능성 조건을 명시하지 않으면 보정이
"절대 Kp 편차"·"산화제 편차"·"종류 혼동"을 임의로 뒤섞어 오학습한다.

**형제 경계 (침범 금지, 인용만):**
- **산화제 화학 자체**(Fenton 속도상수·전기화학 E°·억제제 흡착)는 slurry-chemistry 소관. 이 노트는 산화제 농도가
  Kp에 들어오는 **함수형과 식별조건**만 다루고 반응 메커니즘은 인용만 한다([[w-cmp-fenton-catalyst-abrasive-alumina-silica]]).
- **입자→Kp 기여·스펙시트 변환**은 slurry-abrasive 소관([[slurry-abrasive-specsheet-to-model-input-conversion-rules]]) — κ항은 인용만.
- **스키마 파일**(`data/schema/*.json`)·`ingest.py`·`prior.py`는 **cmp-data-engineer** 소관
  ([[cmp-calibration-schema-integration-validation-rules]]). §5는 **개정 제안(표)만** 적고 파일을 고치지 않는다.
- **잔차 GP 피팅·순차 위상·불확실성**은 cmp-calibrator 소관. 이 노트는 "무엇이 식별되고 무엇을 prior로 고정하는가"와
  레지스트리 추가 행까지만 정의한다([[calibration-parameter-registry-identifiability-sequential-fitting]]).
- **계측 정의**(WIWNU·측정점)는 wafer-metrology, **NPW/PTW 정렬·전이**는 wafer-type 소관 — 입력으로만.
- **고객·재직사 데이터 절대 미사용**(ORG.md §7.5). 모든 수치는 공개 표준·문헌·특허·**합성**이다.

## 1. W 전용 실데이터 필드 — 각 필드를 "왜"로 근거 (Cal-1 (a))

W CMP 레코드는 옥사이드와 세 지점에서 다르다: **(NPW) 증착 스택·핵생성층·배리어·시트저항 측정**, **(PTW) 플러그
직경·피치·리세스·코어링**, **(슬러리) 산화제 종류·농도·Fe 촉매·pH**. 아래 필드는 이 세 축을 데이터로 살리는 최소
집합이며, 각 필드가 어느 보정 변수에 대응하는지를 1차 근거로 단다. **새 1차 문헌 2편**(Choi 2022·Kun Xu 2016)과
Lv1~Lv3-2에서 이미 통독한 문헌의 **재인용**으로 구성한다(과제 (a): 새 문헌 ≥2편, 기존은 재인용).

### 1.1 NPW(블랭킷) — 증착 스택·핵생성·배리어·측정법

| 필드 | 왜 필요한가 (보정 변수 대응) | 근거 |
|---|---|---|
| **w_deposition** (enum: CVD_WF6_H2) | W는 WF₆/H₂ 기상 CVD로만 증착(전구체·부산물이 기체) — Kp의 막 물성 기준 | Kun Xu 2016 §Intro (DOI: 10.1149/2.0371606jss, 새 문헌) |
| **nucleation_precursor** (enum: SiH4/B2H6) | ALD 핵생성 전구체가 **grain 크기를 정한다**(SiH₄=소립·B₂H₆=대립) → 초기 저율 initiation 구간 길이·유효 Kp가 갈림 | Kun Xu 2016 (SiH₄ 소립/B₂H₆ 대립, 대립이 initiation 길어 동일시간 Ave.RR 낮음) |
| **film_stack[].role∈{polish/nucleation/barrier/stop}** | CVD W(polish)/ALD W(nucleation)/PVD overburden 다층. 배리어=TiN, stop=SiO₂ | Choi 2022 §2.1 (DOI: 10.1016/j.apsusc.2022.153767, 새 문헌); Kun Xu 2016 (contact sub-layer Ti/TiN) |
| **barrier_material**(enum: TiN/Ti/Ti_TiN)·**barrier_thickness_nm** | 배리어 클리어 단계 선택비·오버폴리시 시간의 대상. W:배리어 U자 페널티 입력 | Choi 2022 §2.1(BM=TiN); [[w-cmp-ti-tin-barrier-selectivity-recess-erosion]] Lv2-2 |
| **w_thickness_nm** (증착 초기두께) | 제거량=초기−최종. Ave.RR 역산 분자. CVD W 통상 2000–2200 Å | Kun Xu 2016 (blanket W 2000–2200 Å) |
| **sheet_resistance_ohm_sq** + **resistivity_ohm_m** + **thickness_method**(enum: four_point_probe/eddy_current) | **블랭킷 W MRR의 표준 측정 = 4탐침 시트저항 → 두께 환산**(t=ρ/Rs). ρ 가정을 명시해야 두께·MRR이 재현됨 | Lee&Seo 2022 §2(ρ_W≈5.6×10⁻⁸ Ω·m, t=ρ/R_s, 4탐침 CMT-SR5000, 재인용, DOI: 10.3390/app12031227); Kun Xu 2016(eddy current 실시간 두께·KLA-Tencor RS-100 4탐침 전후) |
| **pressure_kpa·velocity_m_per_s** | **Kp_ref=MRR/(P·V) 역산에 필수**. 없으면 절대 Kp 비식별(Lv3-2 §3) | [[preston-luo-dornfeld-mrr]] |

### 1.2 PTW(패턴) — 플러그·컨택 기하·리세스·코어링

| 필드 | 왜 필요한가 | 근거 |
|---|---|---|
| **plug_diameter_nm·plug_pitch_nm·local_density** | 컨택/플러그 스케일. 고립(저밀도) 플러그가 더 파임(리세스 밀도의존은 Cu 침식과 방향 반대) | [[w-cmp-plug-recess-coring-keyhole-overpolish-window]] Lv2-1 §5 |
| **recess_nm** + **recess_method**(enum: AFM/SEM_cross_section/profilometry) | 리세스 관측량. AFM/단면 SEM으로 잰다. 디싱+정적식각+심노출의 합 | Lv2-1 §1·§4 (Yu 2009 버프 모델, DOI: 10.1149/1.3009224 재인용) |
| **coring_depth_nm·seam_flag·keyhole_flag** | 심/키홀이 있으면 리세스가 코어링으로 폭주(자기제한 안 됨). 증착 이력 입력 | Lv2-1 §2·§3 (Kim 2005 DOI: 10.1016/j.microrel.2005.07.048; S.Xu 2020 DOI: 10.1016/j.mee.2020.111285, 재인용) |
| **overpolish_time_s** | 코어링≈SER×t_overpolish·배리어 클리어 시점. 통합 49필드에도 존재(공유) | Lv2-1 §3; [[cmp-calibration-schema-integration-validation-rules]] §3.3 |
| **selectivity_w_over_barrier·selectivity_w_over_oxide** | W:TiN·W:ILD 선택비. bulk=고선택·buff=비선택(반대 선택비) | Choi 2022 §2.2(bulk/buff opposite selectivity); Lv2-2 |

### 1.3 슬러리 — 산화제 종류·농도·Fe 촉매·pH·입자

| 필드 | 왜 필요한가 (보정 변수 대응) | 근거 |
|---|---|---|
| **oxidizer_type** (enum: H2O2/ferric_nitrate/KIO3/K3FeCN6/KMnO4) | **f_ox 곡선 축의 키**. 종류마다 반포화 농도가 100배 규모로 다름(§2·§4) — 없으면 곡선 축이 잠기지 않아 종류 혼동 오학습 | Lim 2013(Fe(NO₃)₃, DOI: 10.1016/j.apsusc.2013.06.003); Stojadinović 2016(KIO₃, DOI: 10.1007/s40735-016-0041-4); US8070843B2(H₂O₂); Kaufman 1991(K₃Fe(CN)₆, DOI: 10.1149/1.2085434) — 재인용 |
| **oxidizer_conc_wt_pct** | f_ox(C)의 C. 반포화 K/C_peak 식별의 스윕 축 | Lv3-2 §5 |
| **fe_catalyst_ppm** | Fenton 촉매(Fe³⁺). bulk 슬러리는 H₂O₂+Fe(NO₃)₃ 공존 — Fe가 슬러리 온도·W RR을 올림 | Choi 2022 §2.2(H₂O₂ oxidant + Fe(NO₃)₃ catalyst Fenton); [[w-cmp-fenton-catalyst-abrasive-alumina-silica]] Lv1-2 |
| **slurry_ph** | pH는 W를 직접 안 깎고 산화(WO₃ 생성) 구동력으로만 들어옴(g_pH) | [[w-cmp-wo3-passivation-oxidizer-kaufman]] Lv1-1; 팩 `w_ph_acid_k` note |
| **abrasive**(alumina/silica)·**abrasive_conc_wt_pct**·**abrasive_size_nm** | κ항(기계). W는 입경 무반응(null)·농도 cube-root | Egan&Kim 2019(DOI: 10.1149/2.0311905jss); Wang 2012(DOI: 10.1149/1.4717508) — 재인용 |

핵심: `oxidizer_type`·`oxidizer_conc_wt_pct`가 없으면 f_ox 축이 붕괴하고(종류 혼동), `pressure`·`velocity`가 없으면
절대 Kp_ref 축이 붕괴한다. 두 축이 다 살아야 §2 파라미터가 식별된다. `sheet_resistance`+`resistivity`가 없으면 NPW
MRR 자체가 재현 불가다(4탐침 두께 환산이 ρ 가정에 의존).

## 2. 보정 파라미터 분해 — Kp_W = Kp_ref × f_ox(C; K_ox, φ) × g_pH (Cal-1 (b))

### 2.1 분해 구조

$$\mathrm{MRR}_W = K_{p,\mathrm{ref}}\cdot f_{ox}(C;K_{ox},\varphi)\cdot g_{pH}(\mathrm{pH})\cdot P\cdot V,\qquad
f_{ox}(C)=\varphi+(1-\varphi)\frac{\theta(C)}{\theta(C_{ref})},\ \ \theta(C)=\frac{K_{ox}C}{1+K_{ox}C}$$

팩 `w_fe_oxidizer.yaml`이 실제로 쓰는 형태다(원문 확인): `oxidizer_langmuir_K`=$K_{ox}$, `oxidizer_mech_floor`=$\varphi$,
`oxidizer_ref_wt_pct`=$C_{ref}$. pH항은 `w_ph_acid_k`=$k_{pH}$로 $g_{pH}=\exp(-k_{pH}(\mathrm{pH}-\mathrm{pH}_{ref}))$.
(팩의 `oxidizer_curve_n`·`oxidizer_peak_wt_pct`는 Kaufman 단봉 형태로 **비활성** — 판정#19가 정점아래 관측만으로
$(n,C_{peak})$ 완전축퇴임을 확인해 Langmuir 1파라미터로 대체, [[chi-oxidizer-curve-exponent-identifiability]].)

### 2.2 무엇을 피팅하고 무엇을 prior로 고정하는가

| 파라미터 | 성격 | 처리 | 이유 |
|---|---|---|---|
| **$K_{p,\mathrm{ref}}$** (절대 스케일) | 그 팹·슬러리 로트·컨디셔닝 고유값 | **피팅** (기준 산화제·pH matched NPW) | 절대값은 데이터로 눌러야 할 자리. Lv3-2가 estimated로 남긴 열(팩 2.8e-13은 estimated) |
| **$K_{ox}$** (산화제 반포화, =$1/C_{half}$) | **산화제 종류마다 완전히 다른 값** | **피팅 (종별 재설정)** | Fe(NO₃)₃ 반포화 ~0.004 wt% vs H₂O₂ ~6 wt% = 100배 규모(§4-1). 종별 별도 곡선 |
| **$\varphi$** (기계 floor) | 산화제 0에서 남는 순수 기계 분율 | **prior 고정** | US20110186542A1 15조건 0.117~0.189, 평균 0.142(measured, 좁음, §4-3) |
| **곡선 함수형/$n$** (형상) | "상승 후 포화" 형태 | **prior 고정 (재추정 금지)** | 판정#19: 정점아래 관측만으로 $(n,C_{peak})$ 완전축퇴. Langmuir(1파라미터)로 형태 고정 |
| **$g_{pH}$·$k_{pH}$** | 산화 구동 pH 감쇠 | 피팅(스윕 있을 때)/기본 prior | Stojadinović KIO₃ 대리계 $k_{pH}$=0.1163/pH(E3, 3조건 산포±22%, 팩 note) |

**형태(형상)는 공통, 스케일(종별 $K_{ox}$)은 종별**이 핵심 규칙이다: 세 산화제(Fe(NO₃)₃·KIO₃·H₂O₂)가 모두
"상승→포화"라는 **같은 Langmuir 형태**를 공유하므로 $\varphi$·함수형은 종을 넘어 고정하되, **반포화 농도 $K_{ox}$는
종류마다 재피팅**한다. 이것이 옥사이드 Cal-1의 "배율은 literature 고정·절대는 피팅"과 대응하되, W는 **산화제 종별
스케일 재설정**이라는 축이 하나 더 붙는다.

### 2.3 Lv3-2 두 문제를 캘리브레이션이 어떻게 흡수하는가

- **팩 Kp 2.6배 과대 → $K_{p,\mathrm{ref}}$ 재피팅으로 흡수 가능.** 절대 스케일은 단일 스칼라 배율 $s$로 전 조건을
  동시에 이동한다(§4-3, $s$=median/pack≈0.39). 이것이 series_scale(내 Lv3-2·cmp-calibrator §5)이 하는 일 — 곱셈
  구조의 절대 인자는 lumped 스칼라로 흡수된다. 자릿수(10⁻¹³)는 맞으므로 재피팅이 안전하다.
- **산화제 스케일 100배 불일치 → 스칼라 재피팅만으로는 흡수 불가.** 팩이 Fe(NO₃)₃ 선언인데 곡선이 H₂O₂
  스케일($K_{ox}$≈0.16/wt%, 반포화 ~6 wt%)이면, Fe(NO₃)₃ 데이터(0.05 wt%에서 이미 포화)를 이 곡선에 넣으면
  $f_{ox}$가 저농도에서 거의 0을 예측한다 — 어떤 단일 $K_{p,\mathrm{ref}}$ 스칼라로도 **곡선 형태 자체가 어긋나** 맞출 수
  없다(§4-1 교차오차 69%). **스키마에 `oxidizer_type` 필드 + 종별 $K_{ox}$가 없이는 구조적으로 불가능**하다 —
  이것이 §5 스키마 개정의 핵심이자 Lv3-2 P1 구현요청의 캘리브레이션 근거다.

## 3. 문헌 prior 값·범위 (1차에서 중심·폭)

σ_log 규약은 cmp-calibrator `prior.py`를 계승한다(literature ln1.5≈0.405, measured 0.203, estimated 0.811 — 미검증 운영규약).

| 파라미터 | prior 중심 | σ_log | 1차 근거(실존 확인) | 등급 |
|---|---|---|---|---|
| $K_{p,\mathrm{ref}}$ (W, alumina) | 1.1e-13 m²/N | estimated 0.811 (넓게) | Lv3-2 §3 3문헌 역산 median(팩 2.8e-13은 2.6배 과대) | E3(실측, V=ω·R_cc 가정) |
| $K_{ox}$ (H₂O₂) | ~0.16/wt% (반포화 6.3 wt%) | measured 0.203 | US8070843B2 0→6.1 wt% 단조상승(§4-1) | E2(특허 실시예표) |
| $K_{ox}$ (Fe(NO₃)₃) | ~260/wt% (반포화 0.004 wt%) | measured 0.203 | Lim 2013 region I→II ~0.1 wt%(§4-1) | E1(직접 실측) |
| $K_{ox}$ (KIO₃) | ~0.5/wt% (반포화 ~2 wt%) | measured 0.203 | Stojadinović 2016 Table1 포화~2 wt% | E1(직접 실측) |
| $\varphi$ (기계 floor) | 0.142 | measured 0.203 | US20110186542A1 15조건 0.117~0.189 평균 | E1 |
| 곡선 함수형 | Langmuir(1파라미터) | literature 0.405(형태) | 판정#19 (n·C_peak 축퇴) | E2(식별성 판정) |
| $k_{pH}$ | 0.1163/pH | literature 0.405 | Stojadinović KIO₃ 대리계(±22%) | E3(대리계) |

**주의:** 산화제 반포화 $K_{ox}$는 종류마다 100배 규모로 다르므로 **중심값을 종을 넘어 이식 금지**(Fe 값을 H₂O₂에
쓰면 §4-1처럼 69% 오차). prior는 **oxidizer_type별 분기 테이블**로 둔다.

## 4. Python 검증 — 산화제 스윕 재현 + 식별가능성 (Cal-1 (c))

**재현 요약(한 줄)**: 팩 Langmuir $f_{ox}$로 (1) US8070843B2 H₂O₂ 스윕(0/2.03/4.06/6.1 wt%→96/1508/2396/2965 Å/min)과
Lim2013 Fe(NO₃)₃ 스윕(0/0.01/0.05 wt%→56/923/1177 Å/min)을 각각 종별 반포화농도로 재현(오차<3%)하되 H₂O₂ 곡선을
Fe에 쓰면 69% 오차(반포화 6.3 vs 0.004 wt%=1600배)임을 assert; (2) 순수 포화형 $K_{p,\mathrm{ref}}\!\cdot\!\theta(C)$
합성데이터에서 농도 스윕이 포화영역을 안 포함하면 $(K_{p,\mathrm{ref}},C_{half})$ 비식별(조건수>1e3·|r|>0.99),
포함하면 식별(조건수<1e2)임을 assert; (3) 4탐침 t=ρ/Rs 저항률 환산·floor φ=0.142 measured·Kp 스칼라 재피팅
2.6배 흡수·σ_log 규약을 대조 — numpy만, 3블록 PASS.

```python verify
import numpy as np
# ═══ (1) 산화제 농도-MRR 스윕 재현 — 종별 반포화농도(K_ox)가 필요함 ═══
# 팩 f_ox = φ + (1-φ)·θ(C)/θ(Cref), θ(C)=C/(C+Chalf)  (Langmuir; Chalf=1/K_ox)
def theta(C, Chalf): return C/(C+Chalf)
def fox(C, Chalf, phi, Cref): return phi + (1-phi)*theta(C,Chalf)/theta(Cref,Chalf)
def fit_Chalf(C, rel, phi, Cref):                       # 반포화농도만 격자탐색(1자유도)
    grid = np.logspace(-3, 2, 5000); errs=[np.sum((fox(C,Ch,phi,Cref)-rel)**2) for Ch in grid]
    return grid[int(np.argmin(errs))]
def maxpct(C, Ch, phi, Cref, rel):
    p = fox(C, Ch, phi, Cref); return float(np.max(np.abs(p-rel)/np.where(rel>0,rel,1))*100)

# H₂O₂ (US8070843B2, held-out; Å/min) — 0→6.1 wt% 단조상승
C_h = np.array([0.0,2.03,4.06,6.10]); M_h = np.array([96,1508,2396,2965.0]); rel_h = M_h/M_h[-1]
phi_h = rel_h[0]; Ch_h = fit_Chalf(C_h, rel_h, phi_h, C_h[-1]); err_h = maxpct(C_h,Ch_h,phi_h,C_h[-1],rel_h)
# Fe(NO₃)₃ (Lim 2013; Å/min) — region I→II ~0.1 wt%
C_f = np.array([0.0,0.01,0.05]); M_f = np.array([56,923,1177.0]); rel_f = M_f/M_f[-1]
phi_f = rel_f[0]; Ch_f = fit_Chalf(C_f, rel_f, phi_f, C_f[-1]); err_f = maxpct(C_f,Ch_f,phi_f,C_f[-1],rel_f)
print(f"H2O2 반포화 {Ch_h:.2f}wt%(err {err_h:.1f}%) / Fe(NO3)3 반포화 {Ch_f:.4f}wt%(err {err_f:.1f}%) → 비율 {Ch_h/Ch_f:.0f}배")
assert err_h < 3.0 and err_f < 3.0                      # 종별 K로는 각각 잘 재현
assert Ch_h/Ch_f > 100                                  # 반포화농도 100배 규모 차이

# 공통 K(H₂O₂ 곡선)를 Fe(NO₃)₃ 조건에 쓰면 스칼라 재조정으로도 못 맞춘다(형태 불일치)
err_cross = maxpct(C_f, Ch_h, phi_f, C_f[-1], rel_f)
print(f"H2O2 곡선을 Fe에 적용 → err {err_cross:.0f}% (oxidizer_type 없이는 종류 혼동)")
assert err_cross > 40                                   # 종 혼동 시 큰 편차 = 축 분리 필요
```

```python verify
import numpy as np
# ═══ (2) (Kp_ref, C_half) 식별가능성 — 포화영역 포함 여부 ═══
# 순수 포화형 MRR = A·θ(C), θ(C)=C/(C+Chalf), params=[logA, logChalf]
def g(C, A, Chalf): return A*C/(C+Chalf)
def cond_corr(Cpts, A, Chalf):
    p0 = np.array([np.log(A), np.log(Chalf)])
    logM = lambda p: np.log(g(Cpts, np.exp(p[0]), np.exp(p[1])))
    J = np.zeros((len(Cpts),2)); h=1e-6; f0=logM(p0)
    for k in range(2):
        pp=p0.copy(); pp[k]+=h; J[:,k]=(logM(pp)-f0)/h
    JTJ=J.T@J; cond=np.linalg.cond(JTJ)
    Sig=np.linalg.inv(JTJ+1e-15*np.eye(2)); r=Sig[0,1]/np.sqrt(Sig[0,0]*Sig[1,1])
    return cond, abs(r)
Chalf_t, A_t = 2.0, 3000.0                              # 반포화 2 wt%, 최대 MRR 3000 Å/min
condA, rA = cond_corr(Chalf_t*np.array([0.01,0.03,0.06]), A_t, Chalf_t)  # 전부 포화 훨 아래(선형가지)
condB, rB = cond_corr(Chalf_t*np.array([0.5,2.0,6.0]),  A_t, Chalf_t)   # 반포화~6배(포화 포함)
print(f"[포화아래] cond={condA:.2e} |r|={rA:.4f}  [포화포함] cond={condB:.2e} |r|={rB:.4f}")
# 포화아래: θ≈C/Chalf 선형 → A와 Chalf가 비 A/Chalf로만 → 비식별
assert condA > 1e3 and rA > 0.99
# 포화포함: 곡률이 A(plateau)와 Chalf(전이)를 분리 → 식별
assert condB < 1e2 and rB < 0.95
print("=> 포화영역(반포화의 ≥2배) 관측이 있어야 (Kp_ref, C_peak) 분리 — 없으면 상승가지 축퇴")
```

```python verify
import numpy as np
# ═══ (3) 부수 파라미터 — 4탐침 저항률 환산·floor·Kp 스칼라 흡수·σ_log ═══
# (i) 4탐침 t=ρ/Rs (Lee&Seo 2022 ρ_W=5.6e-8 Ω·m). 제거량 = ρ(1/Rs1 - 1/Rs2)
rho = 5.6e-8                                            # Ω·m (Lee&Seo 2022 §2)
Rs1, Rs2 = 0.50, 0.70                                   # Ω/sq (연마 전/후, 두께↓→Rs↑)
t1, t2 = rho/Rs1, rho/Rs2                               # m
removed_nm = (t1 - t2)*1e9
print(f"4탐침: t1={t1*1e9:.1f}nm t2={t2*1e9:.1f}nm 제거 {removed_nm:.1f}nm")
assert abs(t1*1e9 - 112.0) < 0.5 and removed_nm > 0     # ρ 가정 명시해야 두께·MRR 재현
# (ii) floor φ — US20110186542A1 15조건 범위·평균 (measured)
phi_obs = [0.117, 0.142, 0.189]                         # 최소·평균·최대 (팩 oxidizer_mech_floor note)
assert min(phi_obs) < 0.14 < max(phi_obs) and abs(np.mean([0.117,0.189])-0.153)<0.01
# (iii) Kp 스칼라 재피팅이 2.6배 과대를 흡수 — 단일 배율 s로 전 조건 동시 이동
pack_kp, med_kp = 2.8e-13, 1.1e-13
s = med_kp/pack_kp                                      # series_scale 스칼라 배율
assert 0.35 < s < 0.42 and abs(pack_kp*s - med_kp) < 1e-15   # 절대축은 스칼라로 흡수 가능
assert abs(pack_kp/med_kp - 2.545) < 0.02               # 팩이 ~2.6배 과대(Lv3-2)
# (iv) σ_log 규약 계승 (cmp-calibrator prior.py): estimated > literature > measured
LN15 = np.log(1.5); sig = {"measured":0.5*LN15, "literature":1.0*LN15, "estimated":2.0*LN15}
assert sig["estimated"] > sig["literature"] > sig["measured"]
assert abs(sig["literature"]-0.405)<0.003 and abs(sig["estimated"]-0.811)<0.003 and abs(sig["measured"]-0.203)<0.003
print(f"[3] floor 0.142(0.117~0.189)·Kp 스칼라 s={s:.3f}(2.6배 흡수)·σ_log est {sig['estimated']:.3f}>lit {sig['literature']:.3f}>meas {sig['measured']:.3f}")
```

**결과 해석(정직하게)**
- (1)은 US8070843B2·Lim2013 **실측 상대비의 재현**이다(문헌값 상수 박음). 반포화농도는 종별 격자적합(1자유도)이라
  실측 형태를 잘 따르나, 두 종의 반포화가 1600배 벌어지는 것은 **팩 곡선 축이 종류에 잠겨야 한다**는 구조적 결론이다.
  US8070843B2는 고정연마입자 패드라 절대 MRR은 rank_only(데이터셋 note)지만 **상대 곡선 형태**는 유효하다.
- (2)는 **합성데이터에 대한 직접 계산**이지 실측 재현이 아니다(정직 표지). 포화아래 축퇴는 Langmuir가 저농도에서
  선형화($\theta\approx C/C_{half}$)돼 A와 C_half가 비로만 들어오는 수학적 귀결이라 노이즈로 회복 안 된다 — 포화영역
  관측이라는 **구조적 정보**만이 분리를 준다. 이는 판정#19(정점아래 (n,C_peak) 축퇴)의 Langmuir 판본이다.
- (3-i)의 저항률 환산은 t=ρ/Rs 표준식으로 ρ 가정(Lee&Seo 5.6e-8)에 선형 의존한다 — ρ를 다르게 가정하면 두께·MRR이
  비례 이동하므로 `resistivity_ohm_m` 필드가 필수다. (3-iii)의 스칼라 흡수는 절대축만 해당하고, 산화제 축은
  (1)에서 보듯 스칼라로 못 옮긴다. σ_log는 계승한 운영규약이지 W 전용 문헌값이 아니다.

## 5. 스키마 개정 제안 — 통합 49필드에 없는 W 특이 필드 (cmp-data-engineer 인계 — 파일 무수정) (Cal-1 (d))

통합 스키마([[cmp-calibration-schema-integration-validation-rules]] §3)는 `film_stack`·`pressure_kpa`·`slurry_pack_id`·
`overpolish_time_s`·`local_density`·`structure_type`를 이미 가진다(재사용). 아래는 **W 특이 필드**로, 통합 스키마와
충돌 없이 추가(전부 optional=MINOR, §6 semver 규칙). 산화제 축이 최우선이다.

| 필드(제안) | 위치 | 타입/enum | 필수성 | 근거 | 통합스키마 관계 |
|---|---|---|---|---|---|
| **`oxidizer_type`** | slurry_spec | enum: H2O2/ferric_nitrate/KIO3/K3FeCN6/KMnO4 | **필수(W)** | §1.3·§2.3·§4-1 | 신설 — f_ox 곡선 축 잠금(종류 혼동 방지) |
| `oxidizer_conc_wt_pct` | slurry_spec | number(≥0) | 필수(W) | §1.3 | 신설 — f_ox(C)의 C |
| `fe_catalyst_ppm` | slurry_spec | number\|null | 권고 | §1.3(Choi 2022 Fenton) | 신설 — Fe(NO₃)₃ 촉매 |
| `nucleation_precursor` | film_stack[nucleation] | enum: SiH4/B2H6 | 권고 | §1.1(Kun Xu 2016) | film_stack layer 속성 확장 |
| `barrier_thickness_nm` | film_stack[barrier] | number | 배리어 클리어 보고 시 | §1.1(Choi 2022) | film_stack `role=barrier`에 두께 |
| `sheet_resistance_ohm_sq`+`resistivity_ohm_m`+`thickness_method` | record/point | number/enum(four_point_probe/eddy_current) | 블랭킷 MRR 시 필수 | §1.1(Lee&Seo·Kun Xu) | 신설 — 4탐침 두께 환산 provenance |
| `plug_diameter_nm`·`plug_pitch_nm` | record(PTW) | number | PTW·플러그면 필수 | §1.2 | film-oxide `line_width`와 별개(플러그=원형 컨택) |
| `recess_nm`+`recess_method`(AFM/SEM_cross_section) | point | number/enum | PTW 리세스 시 | §1.2(Lv2-1) | 신설 — 디싱과 구분되는 W 리세스 |
| `coring_depth_nm`·`seam_flag`·`keyhole_flag` | record/point | number/bool | 증착이력 있을 시 권고 | §1.2(Kim 2005·S.Xu 2020) | 신설 — 코어링 폭주 플래그 |
| `selectivity_w_over_barrier` | record | number\|null | 배리어 클리어 보고 시 | §1.2(Choi 2022 bulk/buff) | film-oxide `selectivity_oxide_over_stop`의 W 판본 |

**주의:** `oxidizer_type`이 없으면 캘리브레이터가 종류를 알 수 없어 f_ox 곡선을 잘못 적용한다(§4-1, 69% 오차) — 이 한
필드가 W 스키마의 가장 중요한 신설이다. `is_reference_oxidizer`(기준 산화제·pH 표식)를 두면 절대 $K_{p,\mathrm{ref}}$
식별 게이트가 된다(film-oxide `is_reference_film` 대응).

## 6. 근거 충돌 판정 (EVIDENCE-RULES.md 서열)

| # | 충돌 | A (등급) | B (등급) | 판정 |
|---|---|---|---|---|
| 1 | 산화제 반포화 K를 종을 넘어 공유 vs 종별 재설정 | 단일 곡선으로 단순화(파라미터↓) | Lim/Stojadinović/US8070843 실측 종별 포화 100배 차이 (E1/E2) | **B 채택(종별)** — 공통 K는 §4-1에서 69% 오차. `oxidizer_type` 분기 필수 |
| 2 | 곡선형 지수 n 데이터 재추정 vs prior 고정 | 자유 n 피팅(자유도↑) | 판정#19: 정점아래 (n,C_peak) 완전축퇴 (E2) | **B 채택(고정)** — Langmuir 1파라미터로 형태 고정, 스케일 K만 피팅 |
| 3 | 팩 Kp 2.8e-13 유지 vs 역산 1.1e-13 | 팩 estimated 대표값 | 3문헌 역산 median (E3, R_cc 가정) | **재피팅으로 흡수**(§4-3 스칼라 s) — 값 교체는 별도 판정, 캘리브레이션이 s로 흡수 |

상반된 지수를 평균낸 곳 없음 — #1·#2 모두 실측/식별성이 단순화를 이긴다.

## 7. 한계·미확보·미검증 (정직성 표기)

- **Kun Xu 2016은 IOP OA HTML 본문·초록 판독**(PDF 봇차단으로 papers/ 미저장, E2/E3). SiH₄/B₂H₆ 대립/소립·3단계 RR·
  Table I(W CMP onset 1995 0.35µm)은 초록·본문에서 직접 판독했으나 Fig.·Table II 정량은 미판독. DOI Crossref 실존 확인.
- **Choi 2022는 로컬 PDF 완독(E2)** 이나 리세스·부식은 대부분 **정성**(pit/recess 정량 nm 없음) — 필드 존재·스택 근거로만 썼다.
- **W 저항률 ρ=5.6×10⁻⁸ Ω·m는 Lee&Seo 2022 §2의 "estimated"** 값이다(원문 "estimated to 5.6×10⁻⁸"). 박막 두께의존
  저항률(scattering)은 미반영 — 단일 ρ 가정이라 절대 두께에 계통편차 가능(§4-3 정직표지).
- **산화제 반포화 $K_{ox}$ 중심값은 스윕 격자적합**(§4-1)이지 저자 보고값이 아니다 — Fe(NO₃)₃ ~0.004 wt%는 Lim의
  region 전이(~0.1 wt%)와 오더는 맞으나(반포화<전이완료) 정확값은 데이터·모델형 의존. KIO₃·H₂O₂도 같은 성격.
- **§4-2는 합성데이터 계산**(정직표지). 축퇴는 Langmuir 저농도 선형화의 수학적 귀결.
- **팩 Kp 2.6배·산화제 100배는 Lv3-2에서 확정된 것**을 인용해 흡수 방식만 정의했다 — 재측정 아님. R_cc 미보고로
  절대 Kp는 estimated 유지(Lv3-2 §7).
- **fe_catalyst_ppm의 W RR 함수형은 미확보**: Choi가 Fenton 촉매임을 밝혔고 Lv1-2가 종형(포화) 방향을 세웠으나
  ppm-MRR 정량 곡선은 이 노트에서 새로 만들지 않았다(slurry-chemistry 소관, 인용만).

## 8. 구현 요청
→ [[../../agents/film-w/PROFILE.md]] "## 구현 요청 (2026-09-20, Cal-1)" 참조 (oxidizer_type 종별 f_ox 축 + 절대 Kp
식별 게이트 + 4탐침 저항률 provenance + 리세스/코어링 PTW 필드, §2·§4·§5).

## 9. 자기시험
→ [[../../agents/film-w/EXAMS.md]] Cal-1 문항 참조.

## 10. 결론 (W 캘리브레이션 관점)

1. **Kp_W = 절대 Kp_ref × f_ox(C;K_ox,φ) × g_pH**로 분해하고, **Kp_ref·K_ox는 피팅·φ·곡선형은 prior 고정**(§2.2).
2. **산화제 반포화 K_ox는 종류마다 100배 규모로 재설정**(Fe(NO₃)₃~0.004 vs H₂O₂~6 wt%) — `oxidizer_type` 없이는
   종류 혼동으로 오학습(§4-1, 69% 오차).
3. **f_ox 곡선형은 공통 Langmuir·1파라미터**로 고정(판정#19 (n,C_peak) 축퇴) — 스케일만 종별 피팅(§2.2).
4. **(Kp_ref, C_peak)는 포화영역(반포화 ≥2배) 관측이 있어야 식별**(§4-2, 없으면 cond>1e3·|r|>0.99).
5. **팩 Kp 2.6배 과대는 Kp_ref 스칼라 재피팅으로 흡수 가능**하나, **산화제 스케일 100배 불일치는 `oxidizer_type`
   필드 없이는 스칼라로 흡수 불가**(§2.3·§4-1) — 이것이 §5 W 특이 스키마의 최우선 신설이다.

## 레지스트리 추가 행 (cmp-calibrator §1 형식 — 이 노트가 [[calibration-parameter-registry-identifiability-sequential-fitting]] §1 표에 더할 행)

| # | 파라미터 (기호) | 소유(형제) | Kp 진입 | prior 중심 출처(등급) | 등급→σ_log | 식별에 필요한 스윕 | 잔차 귀속 순서 |
|---|---|---|---|---|---|---|---|
| W1 | **절대 스케일 $K_{p,\mathrm{ref}}^{W}$** | film-w / 팩 앵커 | 곱(스칼라) | 3문헌 역산 median 1.1e-13 m²/N, 팩 2.8e-13 2.6배 과대 (E3) | estimated→0.811 | 기준 산화제·pH matched NPW at **matched P·V** | **1 (최우선, = series_scale `s`)** |
| W2 | **산화제 반포화 $K_{ox}$ (종별)** | film-w | 곱 (f_ox 스케일) | H₂O₂ 6.3 / Fe(NO₃)₃ 0.004 / KIO₃ 2 wt% (E1/E2) | measured→0.203 | 산화제 농도 ≥3점 **포화영역 포함**(반포화≥2배) + `oxidizer_type` | **2 (종별 재피팅)** |
| W3 | **기계 floor $\varphi$** | film-w | 곱 (f_ox 하한) | US20110186542A1 15조건 0.117~0.189 평균 0.142 (E1) | measured→0.203 | C=0 산화제 조건 포함 | **고정 (prior)** |
| W4 | **f_ox 곡선 함수형 (Langmuir/$n$)** | film-w | 곱 (f_ox 형상) | 판정#19 (n,C_peak) 정점아래 축퇴 → Langmuir (E2) | literature→0.405 (형태) | 정점 넘는 관측 필요(대개 부재) | **고정 (재추정 금지)** |
| W5 | **pH 산화구동 $g_{pH}$ ($k_{pH}$)** | film-w | 곱 | Stojadinović KIO₃ 대리계 0.1163/pH, ±22% (E3) | literature→0.405 | pH 스윕 ≥2점 + **측정 pH** 명시 | 3 (스윕 있을 때) |
| W6 | **W 리세스·코어링 $(recess, coring)$** | film-w | **PTW 전용**(진단) | Yu 2009 버프 폐형·Kim 2005 심/키홀 (E2) | — | 밀도·오버폴리시 시간 + `seam_flag` | 5 (PTW, fit_ptw) |

**잔차 귀속 순서 규칙(레지스트리 §1 계승):** W1 절대 스케일 먼저(series_scale) → **W2 산화제 종별 K는 포화 스윕이
있을 때만 귀속, 없으면 W1에 흡수하고 쪼개지 않음**(EVIDENCE-RULES §3 데이터 스누핑 금지) → W5 pH(측정 pH 있을 때)
→ 반경 δ(GP, fit_npw) → W6 PTW 리세스/코어링(fit_ptw, NPW 고정 후). W3·W4는 재추정 안 하고 prior 고정.

## 상호링크
[[w-cmp-preston-kp-oxidizer-rate-literature-reproduction]] [[w-cmp-plug-recess-coring-keyhole-overpolish-window]]
[[w-cmp-ti-tin-barrier-selectivity-recess-erosion]] [[w-cmp-fenton-catalyst-abrasive-alumina-silica]]
[[w-cmp-wo3-passivation-oxidizer-kaufman]] [[chi-oxidizer-curve-exponent-identifiability]]
[[calibration-parameter-registry-identifiability-sequential-fitting]] [[cmp-calibration-schema-integration-validation-rules]]
[[../materials/film-oxide-calibration-data-schema-kp-selectivity-parameters]] [[slurry-abrasive-specsheet-to-model-input-conversion-rules]]
[[preston-luo-dornfeld-mrr]]
