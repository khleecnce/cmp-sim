# FabSim 모델 근거 보고서 (MODEL-BASIS)

생성: 2026-09-15 15:38 · 커밋 기준 자동 생성 — 손으로 고치지 말고 코드/팩/노트를 고쳐라.

완성 판정: **미완** (49/50칸). 미충족 1건은 끝에.

## 요약 — 이 문서를 처음 읽는 사람에게

**이 시뮬레이터가 하는 일**: CMP(화학기계연마) 레시피 — 압력·웨이퍼/플래튼 회전수, 슬러리 조성(연마입자·산화제·억제제 등)과 pH, 패드/디스크 조건 — 을 입력하면, 웨이퍼 반경 위치별 제거율(MRR, nm/min)과 그로부터 계산되는 균일도 지표(WIWNU·TTV·CV 등), 그리고 손상·안정성 같은 진단값을 출력한다. 실측 레시피를 그대로 재현하는 것이 아니라, 문헌에 보고된 관계식·수치를 근거로 그 공정이 어떻게 반응할지 계산한다.

### 10개 팩터 — 각각 공정에서 무엇을 뜻하는가

| 기호 | 이름(한글) | 영어 전문용어 | 공정상 의미 | 축 |
|---|---|---|---|---|
| Λ | 기계 부하 강도 | Preston product P·V | P·V (Preston 곱, 단위면적 마찰일률). | 장비축(설비가 결정) |
| Π | 반경 하중 분포 | radial pressure profile | 존압력·리테이너링이 만드는 P(r) 형상. | 장비축(설비가 결정) |
| Θ | 열·유동 부하 | thermal-flow load | 마찰 발열과 슬러리 냉각/공급의 균형. | 장비축(설비가 결정) |
| Γ | 컨디셔닝 부하 | pad conditioning load | 디스크가 패드에 가하는 단위시간 절삭일 (Preston형). | 장비축(설비가 결정) |
| κ | 접촉 강도 | contact intensity | 활성 입자 수 × 입자당 압입 깊이. | 소모품축(슬러리·패드·디스크가 결정) |
| χ | 화학 반응성 | chemical reactivity | 표면 연화·산화가 만드는 MRR 배수. | 소모품축(슬러리·패드·디스크가 결정) |
| ψ | 표면 보호도 | surface passivation | 표면 흡착 보호(adsorption shield)가 만드는 제거 억제 배수 (≤1). | 소모품축(슬러리·패드·디스크가 결정) |
| τ | 슬러리 전달 | slurry delivery/replenishment | 접촉부에 도달하는 신선 슬러리 유효분율. | 소모품축(슬러리·패드·디스크가 결정) |
| Δ | 손상 유발도 | defect/scratch propensity | 스크래치·결함 발생 경향 (진단 전용, MRR에 곱하지 않는다). | 소모품축(슬러리·패드·디스크가 결정) |
| S | 시간 안정성 | steady-state pad stability | 글레이징률 vs 컨디셔닝 재생률의 균형이 정하는 정상상태 패드 조도. | 소모품축(슬러리·패드·디스크가 결정) |

### 5개 공정 — 각 팩이 어떤 실제 CMP 공정인가

| 팩(내부 식별자) | 공정 |
|---|---|
| `cu_h2o2_bta` | Cu CMP: H2O2 산화 + BTA 패시베이션, dishing 지배 공정 |
| `oxide_silica` | Oxide CMP: 실리카 슬러리, STI/ILD 평탄화 |
| `sic_ceria_h2o2` | 4H-SiC CMP: 세리아/H2O2 알칼리 슬러리, pH 항 실측 역산 |
| `sti_ceria` | STI CMP: 세리아 슬러리, oxide:nitride 고선택비 |
| `w_fe_oxidizer` | W plug CMP: Fe계 산화제 산성 슬러리, 알루미나 연마입자 |

### 현재 완성도

격자(10개 팩터 × 5개 공정 = 50칸) 중 **49/50칸** 충족. 남은 미충족은 **χ(화학 반응성)/`cu_h2o2_bta`(Cu CMP, H2O2 산화제) 1칸**뿐이며, Cu 표면에서 H2O2가 만드는 산화막 반응성의 정량 관계를 그 조성·pH 조건에서 보고한 1차 문헌을 아직 찾지 못해 confidence가 literature 등급에 못 미친다(estimated).

### '종결 판정'이란 무엇인가

아래 팩터별 표에서 confidence가 낮은데도 완성 판정에 포함된 칸이 있다. 이건 **"아직 안 했다"가 아니라 "확인했지만 없다"는 뜻이다.** 해당 수치를 뒷받침할 만한 1차 문헌(논문·특허)이 공개 문헌에 존재하지 않는다는 것을 서로 다른 시점에 3회에 걸쳐 재확인한 뒤, 그 결과를 `validation/C2-CLOSURES.yaml`에 판정 번호와 근거 노트로 등록해 **구조적 한계로 종결**한 것이다. 종결은 숫자나 등급을 바꾸지 않는다 — 다음에 새 문헌이 나오면 그때 재검토한다(각 칸의 재개 조건은 `reopen_if`에 있다). 지금 **9개 칸이 이 방식으로 종결**되어 있다.

## 0. 결합식

```
MRR(r) = Kp · P(r) · V(r) · κ · χ · ψ · τ        (기준 조건에서 κ=χ=ψ=τ=1)
Λ, Π 는 P·V 자체의 분해(장비축), Θ·Γ·Δ·S 는 출력·진단 축 — MRR에 곱하지 않는다.
```

Kp는 팩마다 문헌 한 점에서 역산한 값이라 절대값은 그 조성·조건에 묶인다. 팩터는 전부 **기준 대비 배수**이므로 Kp와 이중 계상되지 않는다(`tests/test_factors.py`가 기준 1.0 계약을 강제).


## Λ 기계 부하 강도 (`lambda`) — 축: equipment · 파트: tool · MRR 결합: 아니오(진단)

### 모델 정의 근거 (코드 docstring 그대로)

```
Λ 기계 부하 강도 = P·V (Preston 곱, 단위면적 마찰일률).

Preston MRR = Kp·P·V 에서 Kp를 뺀 나머지 전부. 장비가 웨이퍼에 가하는
기계적 부하를 단일 숫자로 압축한 것이다.

기준: 팩의 pressure_psi × (그 조건의 상대속도). 기준 조건에서 1.0.
```

### 팩별 상태

| 팩(공정) | status | confidence | 항(terms) | 드라이버 | 출처 |
|---|---|---|---|---|---|
| cu_h2o2_bta (Cu CMP: H2O2 산화 + BTA 패시베이션, dishing 지배 공정) | modeled | literature | P×1.000, V×1.000 | pressure_psi, rpm_platen, rpm_wafer, center_offset_m | cmp-kinematics-rotary.md; preston-luo-dornfeld-mrr.md |
| oxide_silica (Oxide CMP: 실리카 슬러리, STI/ILD 평탄화) | modeled | literature | P×1.000, V×1.000 | pressure_psi, rpm_platen, rpm_wafer, center_offset_m | cmp-kinematics-rotary.md; preston-luo-dornfeld-mrr.md |
| sic_ceria_h2o2 (4H-SiC CMP: 세리아/H2O2 알칼리 슬러리, pH 항 실측 역산) | modeled | literature | P×1.000, V×1.000 | pressure_psi, rpm_platen, rpm_wafer, center_offset_m | cmp-kinematics-rotary.md; preston-luo-dornfeld-mrr.md |
| sti_ceria (STI CMP: 세리아 슬러리, oxide:nitride 고선택비) | modeled | literature | P×1.000, V×1.000 | pressure_psi, rpm_platen, rpm_wafer, center_offset_m | cmp-kinematics-rotary.md; preston-luo-dornfeld-mrr.md |
| w_fe_oxidizer (W plug CMP: Fe계 산화제 산성 슬러리, 알루미나 연마입자) | modeled | literature | P×1.000, V×1.000 | pressure_psi, rpm_platen, rpm_wafer, center_offset_m | cmp-kinematics-rotary.md; preston-luo-dornfeld-mrr.md |

엔진이 스스로 보고하는 한계:

- P·V = 3.456 psi·m/s (기준 대비 1.000배)

근거 노트(verify 블록 보유): `knowledge/cmp/preston-luo-dornfeld-mrr.md`, `knowledge/physics/cmp-kinematics-rotary.md`


## Π 반경 하중 분포 (`pi`) — 축: equipment · 파트: tool · MRR 결합: 아니오(진단)

### 모델 정의 근거 (코드 docstring 그대로)

```
Π 반경 하중 분포 — 존압력·리테이너링이 만드는 P(r) 형상.

Λ이 '얼마나 세게'라면 Π는 '어디를 세게'다. TTV/WIWNU를 지배하는 축이고,
Λ과 직교해야 한다(전체를 키우면 Λ, 기울기를 바꾸면 Π).

정의: 정규화 P(r)/P̄ 의 엣지/센터 비. 균일하면 1.0.
```

### 팩별 상태

| 팩(공정) | status | confidence | 항(terms) | 드라이버 | 출처 |
|---|---|---|---|---|---|
| cu_h2o2_bta (Cu CMP: H2O2 산화 + BTA 패시베이션, dishing 지배 공정) | modeled | verified | uniform×1.000 | edge_pressure_amp | cmp-multizone-carrier-radial-response.md |
| oxide_silica (Oxide CMP: 실리카 슬러리, STI/ILD 평탄화) | modeled | verified | uniform×1.000 | edge_pressure_amp | cmp-multizone-carrier-radial-response.md |
| sic_ceria_h2o2 (4H-SiC CMP: 세리아/H2O2 알칼리 슬러리, pH 항 실측 역산) | modeled | verified | uniform×1.000 | edge_pressure_amp | cmp-multizone-carrier-radial-response.md |
| sti_ceria (STI CMP: 세리아 슬러리, oxide:nitride 고선택비) | modeled | verified | uniform×1.000 | edge_pressure_amp | cmp-multizone-carrier-radial-response.md |
| w_fe_oxidizer (W plug CMP: Fe계 산화제 산성 슬러리, 알루미나 연마입자) | modeled | verified | uniform×1.000 | edge_pressure_amp | cmp-multizone-carrier-radial-response.md |

엔진이 스스로 보고하는 한계:

- 균일 압력 — Π=1.0 (존압력·엣지집중 없음)

근거 노트(verify 블록 보유): `knowledge/equipment/cmp-multizone-carrier-radial-response.md`


## Θ 열·유동 부하 (`theta`) — 축: equipment · 파트: tool · MRR 결합: 아니오(진단)

### 모델 정의 근거 (코드 docstring 그대로)

```
Θ 열·유동 부하 — 마찰 발열과 슬러리 냉각/공급의 균형.

발열은 두 독립 채널의 곱이다: Λ(웨이퍼-패드 마찰, 기존)과 리테이닝 링 압력(링-패드 마찰,
Lee/Guo/Jeong 2012, doi:10.1007/s12541-012-0004-8, knowledge/physics/cmp-theta-retaining-
ring-pressure-heat-channel.md — Table 1 총마찰력 선형회귀 R²>0.99). 냉각은 세 독립 채널로
이루어진다: ①슬러리 유량(SFR, 대류 물질교환) ②플래튼 냉각수 온도(열전달 구동력 ΔT)
③플래튼 회전속도(회전 대류냉각, von Karman 회전원판 Nu∝Re^0.5 — Harmand et al. 2013,
doi:10.1016/j.ijthermalsci.2012.11.009, knowledge/physics/cmp-theta-rotation-convective-
cooling-driver.md). rpm_platen은 Λ의 발열(V=ω·r_cc, 선형)에도 쓰이지만 냉각 쪽에서는
제곱근으로 스케일링돼 순net 효과는 완화될 뿐 상쇄되지 않는다(같은 노트 §2).
Yuh 2015(doi:10.1007/s40684-015-0041-8)가 SFR·온도를 독립 실험축으로 스윕했다
(knowledge/equipment/cmp-theta-platen-coolant-temperature-driver.md §1).
온도는 Arrhenius로 화학속도를, 유량은 신선 슬러리 공급을 지배한다.

⚠ 회전 냉각 채널은 전체 냉각의 일부만 차지한다(2026-09-13 정정): White 2003 원문 열저항
네트워크(정상상태 검증판은 sim/tier2_physics/cmp_theta_steady_state_heat_balance.py,
frictional-heating-temperature-arrhenius-coupling.md §8.2/§8.4)에 따르면 냉각은
G_slurry(엔탈피 수송, 회전무관)+G_pad(전도, 회전무관)+G_air(회전 대류, √Ω)의 병렬합이고
Shin 2025 중앙 케이스 분해가 슬러리 74%/패드 19%/공기 7%임을 준다. 과거에는 cool_rotation
전체를 √Ω로 스케일해 이 7% 채널의 효과를 냉각 전체(100%)에 적용했다 — 회전 냉각 효과를
심하게 과대평가한 것이다(§8.4 "정정 후보"로 기록되어 있었음). 지금은 가중평균
(1-W_AIR_FRACTION)·1.0 + W_AIR_FRACTION·√Ω로 그 7%만 반영한다. W_AIR_FRACTION=0.07은
단일 케이스(Shin 2025 중앙값)에서 나온 근사치이고 범위는 6~8%다(§8.4 최소/최대 케이스) —
구조적 결측(§8.5: 웨이퍼/헤드 경로 미모델링, L_pad 유효길이, h_air CMP 실측, 완전 열교환
가정)이 전혀 닫히지 않았으므로 confidence는 여전히 estimated다.

⚠ 절대 온도가 아니라 **기준 대비 부하비**다. 실제 ΔT 예측은
knowledge/physics/frictional-heating-temperature-arrhenius-coupling.md 의
모델이 담당하고, 여기서는 팩터로 압축만 한다.
```

### 팩별 상태

| 팩(공정) | status | confidence | 항(terms) | 드라이버 | 출처 |
|---|---|---|---|---|---|
| cu_h2o2_bta (Cu CMP: H2O2 산화 + BTA 패시베이션, dishing 지배 공정) | modeled | literature | heat(Λ)×1.000, heat(ring)×1.000, cool(SFR)×1.000, cool(coolant_temp)×1.000, cool(rotation)×1.000 | sfr_ml_min, pressure_psi, rpm_platen, rpm_wafer, center_offset_m, platen_coolant_temp_c, retaining_ring_pressure_psi | frictional-heating-temperature-arrhenius; cmp-rpm-ratio-flowrate-temperature-mrr-s; cmp-theta-platen-coolant-temperature-dri; cmp-theta-rotation-convective-cooling-dr; cmp-theta-retaining-ring-pressure-heat-c |
| oxide_silica (Oxide CMP: 실리카 슬러리, STI/ILD 평탄화) | modeled | literature | heat(Λ)×1.000, heat(ring)×1.000, cool(SFR)×1.000, cool(coolant_temp)×1.000, cool(rotation)×1.000 | sfr_ml_min, pressure_psi, rpm_platen, rpm_wafer, center_offset_m, platen_coolant_temp_c, retaining_ring_pressure_psi | frictional-heating-temperature-arrhenius; cmp-rpm-ratio-flowrate-temperature-mrr-s; cmp-theta-platen-coolant-temperature-dri; cmp-theta-rotation-convective-cooling-dr; cmp-theta-retaining-ring-pressure-heat-c |
| sic_ceria_h2o2 (4H-SiC CMP: 세리아/H2O2 알칼리 슬러리, pH 항 실측 역산) | modeled | literature | heat(Λ)×1.000, heat(ring)×1.000, cool(SFR)×1.000, cool(coolant_temp)×1.000, cool(rotation)×1.000 | sfr_ml_min, pressure_psi, rpm_platen, rpm_wafer, center_offset_m, platen_coolant_temp_c, retaining_ring_pressure_psi | frictional-heating-temperature-arrhenius; cmp-rpm-ratio-flowrate-temperature-mrr-s; cmp-theta-platen-coolant-temperature-dri; cmp-theta-rotation-convective-cooling-dr; cmp-theta-retaining-ring-pressure-heat-c |
| sti_ceria (STI CMP: 세리아 슬러리, oxide:nitride 고선택비) | modeled | literature | heat(Λ)×1.000, heat(ring)×1.000, cool(SFR)×1.000, cool(coolant_temp)×1.000, cool(rotation)×1.000 | sfr_ml_min, pressure_psi, rpm_platen, rpm_wafer, center_offset_m, platen_coolant_temp_c, retaining_ring_pressure_psi | frictional-heating-temperature-arrhenius; cmp-rpm-ratio-flowrate-temperature-mrr-s; cmp-theta-platen-coolant-temperature-dri; cmp-theta-rotation-convective-cooling-dr; cmp-theta-retaining-ring-pressure-heat-c |
| w_fe_oxidizer (W plug CMP: Fe계 산화제 산성 슬러리, 알루미나 연마입자) | modeled | literature | heat(Λ)×1.000, heat(ring)×1.000, cool(SFR)×1.000, cool(coolant_temp)×1.000, cool(rotation)×1.000 | sfr_ml_min, pressure_psi, rpm_platen, rpm_wafer, center_offset_m, platen_coolant_temp_c, retaining_ring_pressure_psi | frictional-heating-temperature-arrhenius; cmp-rpm-ratio-flowrate-temperature-mrr-s; cmp-theta-platen-coolant-temperature-dri; cmp-theta-rotation-convective-cooling-dr; cmp-theta-retaining-ring-pressure-heat-c |

엔진이 스스로 보고하는 한계:

- ⚠ 발열/냉각을 1차 비례로 압축했다 — 실제 열저항·체류시간은 미반영. 절대 ΔT는 별도 열모델이 담당한다.

근거 노트(verify 블록 보유): `knowledge/equipment/cmp-rpm-ratio-flowrate-temperature-mrr-stability.md`, `knowledge/equipment/cmp-theta-platen-coolant-temperature-driver.md`, `knowledge/physics/cmp-theta-retaining-ring-pressure-heat-channel.md`, `knowledge/physics/cmp-theta-rotation-convective-cooling-driver.md`, `knowledge/physics/frictional-heating-temperature-arrhenius-coupling.md`


## Γ 컨디셔닝 부하 (`gamma`) — 축: equipment · 파트: tool · MRR 결합: 아니오(진단)

### 모델 정의 근거 (코드 docstring 그대로)

```
Γ 컨디셔닝 부하 — 디스크가 패드에 가하는 단위시간 절삭일 (Preston형).

Zheng et al.(2023) Eq.11: PCR = Kp·P·v_rel. v_rel(디스크-패드 상대속도)의
지배항은 disk-rpm-load-radius-pcr.md §4가 유도·검증한 **디스크 중심 속도
ω_p·r_cc**다 — 이 항은 디스크 자전비(Rs=ω_disk/ω_pad)와 무관하게 정확하고,
같은 문헌조건(Rs=0.73)에서 디스크 전체 평균 v/(ω_p·r_cc)는 1.0004(0.04%
편차)로 사실상 완전히 지배적이다(§7 verify). r_cc는 레시피가 아니라 스윕
기구 형상(같은 장비)이므로 F·v 비율에서 상쇄돼, v 항을 rpm_platen(같은
플래튼) 비율만으로 근사할 수 있다 — Λ이 이미 쓰는 것과 동일 근사(§7 참조).

**cond_sweep_cpm(스윕 왕복수 n_a)은 v_rel 식에 나타나지 않는다** — 반경별
궤적밀도·체류시간 분포(어디를 깎는가)를 결정하는 별개 축이다
(conditioner-sweep-algorithm-trajectory-density.md,
conditioner-sweep-kinematics-pcr-profile.md). Γ는 반경 무관 스칼라(총
절삭 부하)이므로 sweep_cpm을 곱하지 않는다 — 곱하면 서로 다른 물리량
(회전 상대속도 vs 왕복수)을 이중 계상하는 것이었다(2026-09-11 정정, 이전
버전은 force×sweep×duty로 sweep을 속도 대리항처럼 썼다).

confidence 하한 3사유 — 2026-09-14 판정(knowledge/equipment/
gamma-conditioning-load-confidence-basis.md, EVIDENCE-RULES 판정#22):
(1) **해소** — 디스크 내 상대속도의 Rs 보정은 총량 스칼라에 대해 폐형식
상계 ⟨|v|⟩/(ω_p r_cc) = 1 + μ²/8 + μ⁴/192 (면적 가중)로 묶이고, 확보한 문헌
범위(|1−Rs| ≤ 0.75, R_disk/r_cc ≤ 0.63) 전체에서 스윕평균 편차 <1%(산업 조건
<0.2%)다(노트 §2). 에지 peak-to-peak 14.4%(disk-rpm-load-radius-pcr.md §4)는
**반경별 분포**의 몫이지 Γ(스칼라)의 결측이 아니다. disk RPM 드라이버 부재는
등급을 제한하지 않는다.
(2) **조건부** — 컨디셔너 PCR 시간적 소진은 `cond_disk_usage_hours`가 있으면
sim/tier2_physics/conditioner_pcr_decay.py의 `pcr_decay()`(TAU_AGING_HOURS≈27.4h,
Entegris 2차인용 앵커 50h→16% 역산, 판정#14 미확보 종결)로 반영된다. 이 함수는
**비율** A = pcr_now/pcr_ref 만 쓰므로 t = t_ref 에서는 τ와 무관하게 A ≡ 1 —
5팩 기준조건(t=t_ref=0)의 Γ는 τ를 10배·1/10배로 바꿔도 불변임을 노트 §3 verify가
증명했다. 따라서 2차 인용 앵커는 |A−1| > GAMMA_AGING_CONF_TOL 일 때만 estimated
하한 사유가 되고, 그때 notes에 이유를 남긴다(판정#14를 뒤집는 것이 아니라
"그 앵커가 기준조건 등급을 제한하지 않는다"는 별개 사실).
(3) **스코프 축소 종결(3회차, 2026-09-15) — 재탐색 금지, 4회차 없음.** 임계하중
(critical downforce) 아래에서는 절삭이 안 일어난다는 비선형이 F 선형항에
미반영이다. 구형 팁 Hertz+Tabor로 유도한 P_c = π³R²(1.65Y)³/(6E*²)에 IC1000
물성(Saka 2008: E_p 0.5 GPa, H_p 0.05 GPa)을 넣으면, 중심 사례(R=15 µm 가정,
작동 그릿 10%)는 그릿당 하중이 P_c의 ~40배(임계 downforce ≈0.10 lbf)로 운전점
4 lbf에서 멀지만, 마모 팁 반경 R을 기하 상한(D/2=90 µm)으로 밀면 1.1배, 작동
그릿 18,000개까지 겹치면 0.28배로 **부호까지 뒤집힌다**. 임계 downforce
범위(0.02~14 lbf)가 운전점을 가로지르므로 하한 유지(노트 §4). 3회차에 걸쳐
(마모 그릿 팁 반경 R 실측, IC1000 항복강도 직접 실측 Y)를 겨냥한 문헌 탐색을
반복했으나(3회차에 Wei 2010 UA 학위논문을 처음 식별·확보했지만 furrow 단면적·
UTS 대용값뿐이라 부적격), 이 코퍼스에서 두 값의 1차 문헌은 나오지 않는다는
결론이 확정됐다 — **"임계하중 비선형은 실재하나 이 계에서 정량화할 1차 문헌이
없다"는 영구 확정**(노트 §4.7, EVIDENCE-RULES 판정#22-종결). ⚠ 임계 아래에서는
선형 F항이 과대추정이다.

**S(stab)와의 결합(2026-09-14)**: 같은 `aging(pcr_decay)` 배수 A(t_disk)가 S의 컨디셔닝 강도
G = duty/100·A 에도 들어간다(knowledge/materials/pad-steady-state-glazing-conditioning-balance.md
§3). Γ은 A를 절삭 **부하**로, S는 정상상태 **조도** R_ss=k_c G/(k_g+k_c G)로 변환한다 —
한 함수를 공유하므로 드레서 마모의 이중 정의가 없고, 드레서 사용량↑ → Γ↓·S↓ 가 같은 부호다.
PHM2016 실장비(드레서 사용량 vs MRR 저속군 ρ=−0.696)는 이 경로의 순위 검증이다(S 쪽 verify).

⚠ 여기는 **장비 설정**(하중·회전속도·duty)만 담는다. 디스크의 형상(그릿
밀도·돌출)은 소모품이므로 κ/τ 쪽으로 간다. 이 분리를 지켜야 "디스크를
바꿀까 컨디셔너 세팅을 바꿀까"에 답할 수 있다.
```

### 팩별 상태

| 팩(공정) | status | confidence | 항(terms) | 드라이버 | 출처 |
|---|---|---|---|---|---|
| cu_h2o2_bta (Cu CMP: H2O2 산화 + BTA 패시베이션, dishing 지배 공정) | modeled | estimated | force×1.000, velocity(rpm_platen)×1.000, duty×1.000, aging(pcr_decay)×1.000 | cond_downforce_lbf, rpm_platen, cond_duty_pct, cond_sweep_cpm(coverage_only,not_multiplied), cond_disk_usage_hours | conditioner-disk-pad-cutting-model.md; disk-rpm-load-radius-pcr.md; gamma-conditioning-load-confidence-basis |
| oxide_silica (Oxide CMP: 실리카 슬러리, STI/ILD 평탄화) | modeled | estimated | force×1.000, velocity(rpm_platen)×1.000, duty×1.000, aging(pcr_decay)×1.000 | cond_downforce_lbf, rpm_platen, cond_duty_pct, cond_sweep_cpm(coverage_only,not_multiplied), cond_disk_usage_hours | conditioner-disk-pad-cutting-model.md; disk-rpm-load-radius-pcr.md; gamma-conditioning-load-confidence-basis |
| sic_ceria_h2o2 (4H-SiC CMP: 세리아/H2O2 알칼리 슬러리, pH 항 실측 역산) | modeled | estimated | force×1.000, velocity(rpm_platen)×1.000, duty×1.000, aging(pcr_decay)×1.000 | cond_downforce_lbf, rpm_platen, cond_duty_pct, cond_sweep_cpm(coverage_only,not_multiplied), cond_disk_usage_hours | conditioner-disk-pad-cutting-model.md; disk-rpm-load-radius-pcr.md; gamma-conditioning-load-confidence-basis |
| sti_ceria (STI CMP: 세리아 슬러리, oxide:nitride 고선택비) | modeled | estimated | force×1.000, velocity(rpm_platen)×1.000, duty×1.000, aging(pcr_decay)×1.000 | cond_downforce_lbf, rpm_platen, cond_duty_pct, cond_sweep_cpm(coverage_only,not_multiplied), cond_disk_usage_hours | conditioner-disk-pad-cutting-model.md; disk-rpm-load-radius-pcr.md; gamma-conditioning-load-confidence-basis |
| w_fe_oxidizer (W plug CMP: Fe계 산화제 산성 슬러리, 알루미나 연마입자) | modeled | estimated | force×1.000, velocity(rpm_platen)×1.000, duty×1.000, aging(pcr_decay)×1.000 | cond_downforce_lbf, rpm_platen, cond_duty_pct, cond_sweep_cpm(coverage_only,not_multiplied), cond_disk_usage_hours | conditioner-disk-pad-cutting-model.md; disk-rpm-load-radius-pcr.md; gamma-conditioning-load-confidence-basis |

엔진이 스스로 보고하는 한계:

- velocity 항은 rpm_platen(패드 RPM)만 쓴다 — 디스크 자전비(Rs) 보정은 총량 스칼라에 대해 1+μ²/8+μ⁴/192(면적 가중 폐형식)로 묶이고 문헌 범위(|1−Rs|≤0.75, R_disk/r_cc≤0.63)에서 스윕평균 <1%라 등급 사유에서 제외(해소, gamma-conditioning-load-confidence-basis.md §2). 디스크 에지 peak-to-peak 14.4%는 반경별 분포 모듈의 몫이다(disk-rpm-load-radius-pcr.md §4).
- ⚠ cond_sweep_cpm은 Γ 크기에 곱하지 않는다 — 문헌(disk-rpm-load-radius-pcr.md, conditioner-sweep-algorithm-trajectory-density.md)에 따르면 스윕 왕복수는 v_rel 식에 없고 반경별 궤적밀도(공간분포)만 결정한다. 총 절삭 부하가 아니다.
- ⚠ force×velocity(rpm_platen)×duty 곱 형태는 절삭일률의 1차 근사다 — 임계하중(critical downforce) 아래에서는 절삭이 안 일어난다는 비선형이 미반영(estimated 확정 사유 — 스코프 축소 종결, 3회차 재탐색 완료·재탐색 금지). Hertz+Tabor 유도 P_c는 마모 팁 반경 R²에 걸리는데 R·IC1000 항복강도 직접값 모두 이 코퍼스에서 못 낸다고 확정돼 임계 downforce가 0.02~14 lbf 범위로 운전점 4 lbf를 가로지른다 — 임계 아래에서는 선형 F항이 과대추정이다(gamma-conditioning-load-confidence-basis.md §4, §4.7).

근거 노트(verify 블록 보유): `knowledge/equipment/conditioner-disk-pad-cutting-model.md`, `knowledge/equipment/disk-rpm-load-radius-pcr.md`, `knowledge/equipment/gamma-conditioning-load-confidence-basis.md`


## κ 접촉 강도 (`kappa`) — 축: consumable · 파트: slurry, pad, disk · MRR 결합: 예

### 모델 정의 근거 (코드 docstring 그대로)

```
κ 접촉 강도 = 활성 입자 수 × 입자당 압입 깊이.

**세 파트가 함께 결정하는 대표 팩터다.**
  - 슬러리: 입경 R, 함량 → 접촉 입자 수
  - 패드:   경도 H, 탄성률 → 입자당 하중과 압입
  - 디스크: asperity 밀도 → 실접촉 면적

물리: δ_p = F/(2πR·H) 이고 제거 단면 A_f ∝ δ_p^1.5 ⟹ **MRR ∝ H^-1.5**
(knowledge/cmp/particle-wafer-interaction-... §4, verify PASS).

⚠ 화학적 연화(χ)도 같은 H를 통해 들어간다. **두 번 세지 않도록** κ는
'기계적 경도'만, χ는 '화학이 만든 경도 변화분'만 담당한다.
```

### 팩별 상태

| 팩(공정) | status | confidence | 항(terms) | 드라이버 | 출처 |
|---|---|---|---|---|---|
| cu_h2o2_bta (Cu CMP: H2O2 산화 + BTA 패시베이션, dishing 지배 공정) | modeled | literature | conc×1.000, size×1.000, pad_hardness×1.000, asperity×1.000 | abrasive_wt_pct, abrasive_size_nm, pad_hardness_shore_d, asperity_density_per_m2 | abrasive-concentration-mrr-saturation-co; abrasive-size-concentration-ph-K-additiv; abrasive-size-null-result-force-partitio; pad-hardness-porosity-measurement-method; gw-contact.md |
| oxide_silica (Oxide CMP: 실리카 슬러리, STI/ILD 평탄화) | modeled | literature | conc×1.000, size×1.000, pad_hardness×1.000, asperity×1.000 | abrasive_wt_pct, abrasive_size_nm, pad_hardness_shore_d, asperity_density_per_m2 | abrasive-concentration-mrr-saturation-co; abrasive-size-concentration-ph-K-additiv; abrasive-size-concentration-ph-K-additiv; pad-hardness-porosity-measurement-method; gw-contact.md |
| sic_ceria_h2o2 (4H-SiC CMP: 세리아/H2O2 알칼리 슬러리, pH 항 실측 역산) | modeled | literature | conc×1.000, size×1.000, pad_hardness×1.000, asperity×1.000 | abrasive_wt_pct, abrasive_size_nm, pad_hardness_shore_d, asperity_density_per_m2 | abrasive-concentration-mrr-saturation-co; abrasive-size-concentration-ph-K-additiv; abrasive-size-concentration-ph-K-additiv; pad-hardness-porosity-measurement-method; gw-contact.md |
| sti_ceria (STI CMP: 세리아 슬러리, oxide:nitride 고선택비) | modeled | literature | conc×1.000, size×1.000, pad_hardness×1.000, asperity×1.000 | abrasive_wt_pct, abrasive_size_nm, pad_hardness_shore_d, asperity_density_per_m2 | abrasive-concentration-mrr-saturation-co; abrasive-size-concentration-ph-K-additiv; abrasive-size-concentration-ph-K-additiv; pad-hardness-porosity-measurement-method; gw-contact.md |
| w_fe_oxidizer (W plug CMP: Fe계 산화제 산성 슬러리, 알루미나 연마입자) | modeled | literature | conc×1.000, size×1.000, pad_hardness×1.000, asperity×1.000 | abrasive_wt_pct, abrasive_size_nm, pad_hardness_shore_d, asperity_density_per_m2 | abrasive-concentration-mrr-saturation-co; abrasive-size-concentration-ph-K-additiv; abrasive-size-null-result-force-partitio; pad-hardness-porosity-measurement-method; gw-contact.md |

엔진이 스스로 보고하는 한계:

- ⚠ Shore D는 경도의 대리지표다. H^-1.5의 H는 압입경도(GPa)인데 Shore D↔GPa 환산이 비선형이라 순위는 맞아도 절대값은 캘리브레이션이 필요하다. Qi/Joyce/Boyce 2003(DOI:10.5254/1.3547752, 위 노트 §8)이 범용 탄성체용 Shore D→탄성률 해석해(eq.11)를 주지만 confidence는 못 올린다 — ①62D 앵커점에서 FEA 대비 49% 편향만 확인됐고 60D에서의 편향 크기는 모름, ②범용 가황고무 대상(폴리우레탄 미검증), ③애초에 그 논문의 E는 압입경도가 아니라 단축인장 탄성률이라 물리량 자체가 다르다.
- ⚠ asperity 밀도 지수 0.5는 GW 접촉에서 실접촉면적이 밀도의 제곱근에 가깝게 증가한다는 근사다 — 미검증.
- ⚠ 농도 지수 n=-0.406 — 표면적 극한(1/3)은 US9499721B2 E1 실측 전역회귀(n≈0.30)로 압입 극한(4/3)보다 우세하다고 판정됐다(같은 데이터가 국소 지수는 0.56→0.11로 붕괴 — 순수 거듭제곱은 고농도 포화를 못 담는다는 별개의 구조적 한계는 남아있음).
- ⚠ 농도 지수 n=0.333 — 표면적 극한(1/3)은 US9499721B2 E1 실측 전역회귀(n≈0.30)로 압입 극한(4/3)보다 우세하다고 판정됐다(같은 데이터가 국소 지수는 0.56→0.11로 붕괴 — 순수 거듭제곱은 고농도 포화를 못 담는다는 별개의 구조적 한계는 남아있음).
- ⚠ 입자 함량 20 wt%가 포화농도 7 wt%를 넘었다 — 실제로는 더 넣어도 MRR이 안 오른다(Luo-Dornfeld 포화영역). 현재 항은 계속 증가시키므로 이 구간 예측은 과대평가다.
- 농도 지수 n=+0.333 를 **이론에서 유도**했다 (등급 estimated). n_C = p(1−αχ) = 1·(1−0.667·1) = +0.333 · n_d = −q(1−αχ)+β = -0.000
- 농도 지수 n=-0.406 를 **이론에서 유도**했다 (등급 estimated). n_C = p(1−αχ) = 1·(1−0.667·1) = +0.333 · n_d = −q(1−αχ)+β = -0.000
- 입경 정점형 반영: peak=163nm 기준 d=120nm(지수 below=1.33333), d_ref=120nm. Li et al. 2021 Eq.3-4(압입 지배 φ^1.33, 표면적 지배 φ^-0.333)를 벡터좌표 재추출로 확정한 값 — 이 계(콜로이달 실리카/SiO2)에 한정, 정점 위치·지수의 타 화학종 일반화는 미검증.

근거 노트(verify 블록 보유): `knowledge/cmp/abrasive-concentration-mrr-saturation-contact-probability.md`, `knowledge/cmp/abrasive-size-concentration-ph-K-additive-mrr-quantitative.md`, `knowledge/cmp/abrasive-size-null-result-force-partition-theory.md`, `knowledge/materials/pad-hardness-porosity-measurement-methods.md`


## χ 화학 반응성 (`chi`) — 축: consumable · 파트: slurry · MRR 결합: 예

### 모델 정의 근거 (코드 docstring 그대로)

```
χ 화학 반응성 — 표면 연화·산화가 만드는 MRR 배수.

기존 sim/chemistry.py를 승계하되, pH는 **정점형 항으로 교체**한다
(단조 연화항은 pH 11 위를 과대평가한다 — `_ph_peak_term` docstring 참조).
억제 항은 여기가 아니라 ψ가 가져간다 — 방향이 반대이고, 사용자가
"함량 변화에 따른 성능 변화"를 볼 때 촉진과 억제를 분리해 봐야 한다.

pH 항 선택 원칙 — **has_own 우선** (EVIDENCE-RULES.md 판정#34,
validation/C4-SIC-PACK-DIAGNOSIS.md §2.3·§2.4에서 진단):
  "팩이 어떤 pH 메커니즘의 계수를 **직접 선언**(`has_own`)했다면, 상속만
  받은 다른 메커니즘보다 우선한다." 자기 재료계에서 역산한 계수가 남의
  재료계에서 물려받은 계수보다 그 재료를 잘 기술하기 때문이다. 아래
  `candidates`를 1차 패스에서 own 계수 기준으로 훑고, 아무도 own이
  아니면(=지금까지의 4팩이 전부 여기 해당) 2차 패스에서 기존 우선순위
  (세리아 IEP 창 → W 산성역 → 실리카 정점 → 연화 폴백)로 그대로
  떨어진다 — 그래서 기존 4팩의 분기 선택은 이 변경으로 바뀌지 않는다.
  (sic_ceria_h2o2는 세리아 IEP 창의 `abrasive_iep_ph`를 sti_ceria에서
  상속만 받았을 뿐 직접 선언한 적이 없는데, 이 분기가 최우선이라 자기
  이름으로 직접 역산해 선언한 `ph_softening_per_unit`이 가려지고 있었다.)
```

### 팩별 상태

| 팩(공정) | status | confidence | 항(terms) | 드라이버 | 출처 |
|---|---|---|---|---|---|
| cu_h2o2_bta (Cu CMP: H2O2 산화 + BTA 패시베이션, dishing 지배 공정) | modeled | estimated | oxidizer×1.000, ph_cu_acidic×1.000 | oxidizer_wt_pct, slurry_ph | ceria-slurry-ce-redox-selectivity.md; particle-wafer-interaction-mechanical-ch |
| oxide_silica (Oxide CMP: 실리카 슬러리, STI/ILD 평탄화) | partial | literature | ph_peak×1.000 | oxidizer_wt_pct, slurry_ph | ceria-slurry-ce-redox-selectivity.md; particle-wafer-interaction-mechanical-ch |
| sic_ceria_h2o2 (4H-SiC CMP: 세리아/H2O2 알칼리 슬러리, pH 항 실측 역산) | modeled | literature | ceria_tooth×1.000, ph_softening×1.000 | oxidizer_wt_pct, slurry_ph, ce3_fraction | ceria-slurry-ce-redox-selectivity.md; particle-wafer-interaction-mechanical-ch |
| sti_ceria (STI CMP: 세리아 슬러리, oxide:nitride 고선택비) | modeled | literature | ceria_tooth×1.000, ph_ceria_window×1.000 | oxidizer_wt_pct, slurry_ph, ce3_fraction | ceria-slurry-ce-redox-selectivity.md; particle-wafer-interaction-mechanical-ch |
| w_fe_oxidizer (W plug CMP: Fe계 산화제 산성 슬러리, 알루미나 연마입자) | modeled | literature | oxidizer×1.000, ph_w_acidic×1.000 | oxidizer_wt_pct, slurry_ph | ceria-slurry-ce-redox-selectivity.md; particle-wafer-interaction-mechanical-ch |

엔진이 스스로 보고하는 한계:

- Cu 산성역 pH: pH 4 (기준 4) → 상대 1.000. 산화제(H₂O₂) 환원 전위 경로 — dE/dpH=−59 mV, k=0.1428/pH (US20080090500A1 TABLE 4, 3계열 12점 pooled, R²=0.954, 산포 ±4.8%). ⚠ 함수형은 물리(Nernst+Tafel)이나 계수 크기는 경험값 — Tafel 독립 유도 시 b≈0.954 V/dec 로 전형값의 10배라 어긋난다.
- W 산성역 pH: pH 2.5 (기준 2.5) → 상대 1.000. 산화(WO₃) 구동력 경로 — Nernst dE/dpH=−59 mV, k=0.1163/pH (Stojadinović 2016 Table 1, 산화제 존재 3조건 로그평균). ⚠ 개별 조건 재현오차 −0.8~+9.0 %, k 산포 ±22 % — 지수형 가정은 미검증.
- pH 10.5 (정점 11, 기준 10.5) → 상대 1.000. 실측 3점(Li 2021 Fig.1) 기반 정점형(pH≳9.0), 산성(pH≤6)은 골 형태 로그이차(cn109609035b n=7, 반등 포함 피팅). ⚠ 염기 정점식은 3점을 지나는 최소 가정, 산성 골 로그이차는 n=7 피팅 — 둘 다 문헌 폐형식은 아니다. ⚠ 6~9 전환구간은 데이터 없어 로그-선형 보간(미검증 외삽).
- pH 연화: pH 10 → 유효경도비 1.000 (⚠ 선형 가정, 미검증)
- ⚠ R/R booster(glycine 등)가 팩에 없다 — 막질별 선택비를 만드는 주요 축인데 통로가 없다. 담당 R2-slurry.
- ⚠ 산화제 농도(oxidizer_wt_pct/oxidizer_ref_wt_pct)가 팩에 선언돼 있으나 형상 파라미터(oxidizer_langmuir_K/oxidizer_passivation_K/oxidizer_peak_wt_pct)가 하나도 없어 χ가 산화제 변화에 조용히 반응하지 않는다 — 이번 회차는 이 누락을 경고만 하고 모델링하지 않는다(값·status·confidence 불변, validation/C4-SIC-PACK-DIAGNOSIS.md §2.2).
- ⚠ 화학 항들을 독립으로 보고 곱했다 — pH-흡착, 산화제-세리아 산화환원 커플링은 미모델링.
- 산화제 기계 하한 φ=0.15 (기본값) — 이 팩에 관측이 없어 금속막 CMP 의 관측 대역(0.12~0.27, 4계 독립 수렴) 중앙값을 쓴다. φ 는 재료보다 기계 조건(연마재 경도·압력·속도)이 정하는 양이다. ⚠ 이 계의 직접 관측이 아니므로 절대값은 신뢰하지 말 것.

근거 노트(verify 블록 보유): `knowledge/cmp/ceria-slurry-ce-redox-selectivity.md`, `knowledge/cmp/particle-wafer-interaction-mechanical-chemical-balance.md`


## ψ 표면 보호도 (`psi`) — 축: consumable · 파트: slurry · MRR 결합: 예

### 모델 정의 근거 (코드 docstring 그대로)

```
ψ 표면 보호도 — 표면 흡착 보호(adsorption shield)가 만드는 제거 억제 배수 (≤1).

χ와 분리한 이유: 사용자가 배합을 조정할 때 "촉진을 올릴까 억제를 낮출까"는
서로 다른 결정이다. 하나의 화학 배수로 뭉치면 그 판단이 사라진다.
디싱/에로전은 이 항이 지배한다.

ψ 정의 (2026-09-14 확장, COMPLETION.md "축별 완성 경로"): "금속 부동태"가 아니라
**표면 흡착 보호** — 어떤 화학종이 (막 또는 입자) 표면에 흡착해 연마입자의 접근이나
표면 반응을 막는 모든 경로. 세 갈래를 같은 형식으로 다룬다:

① 금속계 부식억제제 (Cu-BTA, W-피콜린산): `inhibitor_mM` + Langmuir K →
   `chemistry._inhibitor_term` (기존 그대로, 이 함수의 앞 절반. 변경 없음).
② 산화막/세리아계 **첨가제 농도축** — 이번 확장의 본체.
   근거 노트: knowledge/cmp/psi-adsorption-shield-oxide-systems.md,
             knowledge/cmp/psi-surface-adsorption-shield-oxide-ceria.md
     θ(C) = (K·C)^n / (1 + (K·C)^n)             협동(Hill) 흡착 피복률; n=1이면 Langmuir
     ψ    = exp(−k·[θ(C) − θ(C_ref)])            기준농도 정규화 → C=C_ref에서 항등적 1.0
   파라미터(팩, 첨가제×막질 쌍 고유 → `has_own` 자기선언일 때만 활성):
     shield_additive_wt_pct (드라이버), shield_ref_wt_pct, shield_langmuir_K,
     shield_hill_n, shield_strength_k [+ shield_nitride_* 는 STI 선택비 진단용]
   문헌 역산:
     · sti_ceria — Park et al. 2003 JJAP 42, 5420 (doi:10.1143/jjap.42.5420) Fig.3
       세리아 1 wt% + 음이온 계면활성제 0~0.8 wt% 9점: SiO₂ K=1.295/wt%, n=4.62, k=3.0
       (0.8 wt%에서 산화막 RR 1/5 = 원문 텍스트 정박점 재현); Si₃N₄ K=14.02/wt%,
       n=4.62, k=3.4 (임계농도 C₅₀=0.071 wt% ≈ 원문 0.08 wt%). 두 K의 비 10.8배가
       선택비 창(0.08~0.4 wt%)의 기원 — S(C)/S(ref) = exp(−k_N·Δθ_N + k_O·Δθ_O).
     · oxide_silica — **검증된 영(null)**: Penta et al. 2013 Appl. Surf. Sci. 283, 986
       (doi:10.1016/j.apsusc.2013.07.057) "None of the surfactants studied adsorbs on an
       oxide surface and, hence, does not suppress the oxide RR" (SDS·DBSA·DP·SLS, 10 wt%
       콜로이달 실리카, pH 2~10); US10526508B2 Table 1·2 PEG 0~1.4 wt%에서 산화막 RR
       30~50 Å/min 무단조(Spearman ρ=+0.45). → K_oxide=0 ⇒ θ≡0 ⇒ ψ≡1.0 을 **항으로
       계상**한다(모름이 아니라 효과 없음). 양이온 폴리머(PDADMAC·poly(vinylimidazolium))는
       반대로 2 ppm에서 이미 98% 억제(US9758697B2 Table 1: 6242→116 Å/min)라 K를 식별할
       수 없는 스위치형 — 이 팩의 첨가제 클래스가 아니므로 미모델링을 notes로 신고.
     · sic_ceria_h2o2 — **문헌 없음**. SiC 위 첨가제 농도-RR 스윕이 코퍼스·검색 어디에도
       없다. 부모(sti_ceria)의 K는 첨가제×SiO₂ 쌍의 상수라 상속 사용 금지(`has_own`) →
       항을 만들지 않고 status=partial + 사유.
③ 분산제 종류 이산 룩업 (Li 2021 PVA/PVP): `chemistry._dispersant_protection_term`.
   ②와 곱한다(독립 가정 — 커플링 미모델링을 notes에 명시).

한계 (보고서 그대로): (a) 산화막 쪽 k는 (K,n,k) 묶음으로만 식별된다 — 셋을 따로
옮기지 마라(노트 §5.5). 등급 estimated. (b) K는 화학종·pH·연마입자마다 다르다 —
Dandu 2009 pyridine계에 Park K를 대입하면 4배 어긋난다(부호·순서만 일치). (c) 아미노산
(proline 등)은 Prasad & Ramanathan 2006이 흡착량–억제 상관을 반증했으므로 이 폐형식
대상이 아니다(America 2004 Table I 이산 룩업만). (d) 온도 의존 K(T) 없음.
```

### 팩별 상태

| 팩(공정) | status | confidence | 항(terms) | 드라이버 | 출처 |
|---|---|---|---|---|---|
| cu_h2o2_bta (Cu CMP: H2O2 산화 + BTA 패시베이션, dishing 지배 공정) | modeled | unverified | inhibitor×1.000 | inhibitor_mM | cu-electrochemistry-pourbaix-bta-oxidize; inhibitor-chelator-adsorption-isotherm-p |
| oxide_silica (Oxide CMP: 실리카 슬러리, STI/ILD 평탄화) | modeled | literature | adsorption_shield×1.000, dispersant×1.000 | shield_additive_wt_pct, dispersant_type | psi-adsorption-shield-oxide-systems.md; psi-surface-adsorption-shield-oxide-ceri; abrasive-size-concentration-ph-K-additiv |
| sic_ceria_h2o2 (4H-SiC CMP: 세리아/H2O2 알칼리 슬러리, pH 항 실측 역산) | partial | literature | dispersant×1.000 | shield_additive_wt_pct, dispersant_type | abrasive-size-concentration-ph-K-additiv |
| sti_ceria (STI CMP: 세리아 슬러리, oxide:nitride 고선택비) | modeled | estimated | adsorption_shield×1.000, dispersant×1.000 | shield_additive_wt_pct, dispersant_type | psi-adsorption-shield-oxide-systems.md; psi-surface-adsorption-shield-oxide-ceri; abrasive-size-concentration-ph-K-additiv |
| w_fe_oxidizer (W plug CMP: Fe계 산화제 산성 슬러리, 알루미나 연마입자) | modeled | unverified | inhibitor×1.000 | inhibitor_mM | cu-electrochemistry-pourbaix-bta-oxidize; inhibitor-chelator-adsorption-isotherm-p |

엔진이 스스로 보고하는 한계:

- STI 선택비 진단: 질화막 배수 1.000 → oxide:nitride 선택비 1.00배(기준 대비). Park 2003 계(무첨가 S₀=4.8)라면 S≈4.8. 질화막 임계농도 C₅₀=0.071 wt%. (진단 출력 — 엔진 MRR에는 산화막 배수만 곱한다)
- ψ 정의 확장: 표면 흡착 보호(passivation/adsorption shield) — 이 팩은 금속 부동태가 아니라 첨가제/분산제 흡착 경로
- ψ 흡착 보호(농도축): C=0 wt% (기준 0) → θ=0.000 (기준 θ=0.000), Hill K=1.2949/wt% n=4.62 k=3 → 배수 1.000 (Park 2003 doi:10.1143/jjap.42.5420 Fig.3 역산)
- ψ 흡착 보호(농도축): 검증된 영 — 이 팩의 첨가제 클래스는 대상 막에 흡착하지 않아(K=0) 농도와 무관하게 배수 1.000. '모름'이 아니라 '효과 없음'(Penta 2013 doi:10.1016/j.apsusc.2013.07.057; US10526508B2 Table 2). 양이온 폴리머는 다른 클래스(스위치형 억제) — 미모델링.
- ⚠ surfactant가 미연결 — 계면활성제도 피복을 통해 억제에 기여하는데 통로가 없다.
- ⚠ ψ 흡착 보호 농도축 비활성: shield_langmuir_K 가 이 팩의 자기선언이 아니다(상속). 흡착상수는 첨가제×막질 쌍 고유 물성이라 부모 값을 쓰지 않는다 — 이 막질에서 첨가제 농도-RR 스윕 문헌이 확보되면 자기선언으로 활성화된다. 그때까지 첨가제 농도는 결과에 영향을 주지 않는다(partial).
- ⚠ 첨가제 농도축 부재 사유: 이 막질·첨가제 쌍의 농도-RR 문헌 없음 (knowledge/cmp/psi-adsorption-shield-oxide-systems.md §6).
- ⚠ 흡착 보호 항(농도축·분산제 종류)을 독립으로 보고 곱했다 — 같은 표면 자리를 두 종이 경쟁하는 커플링은 미모델링.

근거 노트(verify 블록 보유): `knowledge/cmp/abrasive-size-concentration-ph-K-additive-mrr-quantitative.md`, `knowledge/cmp/cu-electrochemistry-pourbaix-bta-oxidizer-inhibitor.md`, `knowledge/cmp/inhibitor-chelator-adsorption-isotherm-passivation.md`, `knowledge/cmp/psi-adsorption-shield-oxide-systems.md`, `knowledge/cmp/psi-surface-adsorption-shield-oxide-ceria.md`


## τ 슬러리 전달 (`tau`) — 축: consumable · 파트: slurry, pad, disk · MRR 결합: 예

### 모델 정의 근거 (코드 docstring 그대로)

```
τ 슬러리 전달 — 접촉부에 도달하는 신선 슬러리 유효분율.

⚠⚠ 이 팩터의 가장 중요한 사실: **"슬러리를 더 많이 나르면 MRR이 비례해서
오른다"는 직관은 실측으로 기각됐다.**

근거 ①  Prasad 2013 (doi:10.1557/jmr.2013.173, III.D.3, Mirra 툴 TEOS):
  동일 수지경도·유사 기공크기에서 기공률 %P만 15%→45%로 30%p 올렸는데
  평균 RR 증가는 **단 8%**("nominal increase", 원문 표현). 저자 스스로
  "기공=슬러리 저장소이므로 비례 증가"를 기대했다가 빗나갔다고 적었다.

근거 ②  Mu et al. 2016 (doi:10.1016/j.mee.2016.02.035, Table 3):
  그루브 폭 → 슬러리 이용효율 η (3 PSI 기준)
      300 µm → η 9.9%
      600 µm → η 13.4%   (+35% 상대)
      900 µm → η 12.8%   (정체·미세 감소)
  **단조가 아니다.** 600 µm 부근에서 꺾인다. 넓힐수록 좋다는 가정은
  틀렸다 — V_groove와 V_total이 함께 커져 q_actual 비율이 안 변하기 때문이다
  (저류 부피가 과하면 정체 슬러리가 늘어난다).

그래서 이 구현은 두 가지를 지킨다:
  1. η는 **실측 3점 보간**으로 낸다(단조 멱함수 금지 — 정체 구간을 놓친다).
  2. η→MRR 결합은 **매우 약하게** 들어간다. 지수는 Prasad 데이터에서 역산:
     보유용량 3배(15→45%)에 RR 1.08배 ⟹ n = ln(1.08)/ln(3) ≈ 0.07.
     ⚠ 이건 기공률 실험에서 뽑아 그루브 축에 적용한 **교차 대입**이라
     미검증이다. 순위(전달이 나아지면 조금 낫다)만 신뢰하고 크기는
     캘리브레이션 대상이다.

τ가 진짜로 지배하는 것은 평균 MRR이 아니라 **반경 프로파일**이다.
Prasad III.D.2: 기공 2 µm 패드는 중심이 슬러리 기아로 처지고 엣지가 올라
엣지-중심 RR 차이가 200 nm/min을 넘었다. 그 프로파일 결합은 아직 미구현이며
이 사실을 notes에 싣는다.
```

### 팩별 상태

| 팩(공정) | status | confidence | 항(terms) | 드라이버 | 출처 |
|---|---|---|---|---|---|
| cu_h2o2_bta (Cu CMP: H2O2 산화 + BTA 패시베이션, dishing 지배 공정) | modeled | literature | turnover×1.000, porosity×1.000 | groove_width_um, pad_porosity_pct, time_s | slurry-turnover-ratio-mrt-preston-consta; pad-porosity-slurry-transport-mrr.md §5 |
| oxide_silica (Oxide CMP: 실리카 슬러리, STI/ILD 평탄화) | modeled | literature | turnover×1.000, porosity×1.000 | groove_width_um, pad_porosity_pct, time_s | slurry-turnover-ratio-mrt-preston-consta; pad-porosity-slurry-transport-mrr.md §5 |
| sic_ceria_h2o2 (4H-SiC CMP: 세리아/H2O2 알칼리 슬러리, pH 항 실측 역산) | modeled | literature | turnover×1.000, porosity×1.000 | groove_width_um, pad_porosity_pct, time_s | slurry-turnover-ratio-mrt-preston-consta; pad-porosity-slurry-transport-mrr.md §5 |
| sti_ceria (STI CMP: 세리아 슬러리, oxide:nitride 고선택비) | modeled | literature | turnover×1.000, porosity×1.000 | groove_width_um, pad_porosity_pct, time_s | slurry-turnover-ratio-mrt-preston-consta; pad-porosity-slurry-transport-mrr.md §5 |
| w_fe_oxidizer (W plug CMP: Fe계 산화제 산성 슬러리, 알루미나 연마입자) | modeled | literature | turnover×1.000, porosity×1.000 | groove_width_um, pad_porosity_pct, time_s | slurry-turnover-ratio-mrt-preston-consta; pad-porosity-slurry-transport-mrr.md §5 |

엔진이 스스로 보고하는 한계:

- ⚠ MRT의 압력 의존(Mu 2016 실측, 3→5 PSI에서 MRT 약 0.90배)은 τ에 배선하지 않았다 — Preston 압력 선형성 계약을 지키기 위한 의도적 스코프 축소다. 배제한 크기는 30 s·2 PSI 스윙에서 약 1.1%.
- ⚠ τ 등급=literature: 결합 형식이 전부 대상계 실측 폐형식(E2)으로 교체됐다 — TR 항은 ILD oxide 실측(Philipossian 2004), 기공률 항은 기공률 축 직접 실측(Prasad 2013). 종속이던 η 항은 제거했다(이중 계상, 노트 §4). verified가 아닌 이유는 TR 기울기 a=0.2301이 2점 유도라 곡률이 미검증이기 때문이다.
- ⚠ τ가 실제로 지배하는 것은 평균 MRR이 아니라 **반경 프로파일**이다. 기공 2 µm 패드에서 중심이 슬러리 기아로 처지고 엣지-중심 RR 차이가 200 nm/min을 넘었다(Prasad 2013 III.D.2). 이 프로파일 결합은 미구현 — 담당 R3-pad × R2-slurry.
- 그루브 폭 600 µm(3 PSI 기준) → 슬러리 MRT=10.6 s, 폴리시 60 s에서 턴오버비 TR=0.177 → Preston 배수 0.959 (기준 0.959). ⚠ 폴리시 시간이 짧을수록 물→슬러리 치환 과도기 비중이 커져 평균 MRR이 떨어진다(Philipossian 2004 doi:10.1149/1.1731539).
- 기공률 30% (기준 30%). ⚠ 실측상 기공률 15→45%(3배)에도 RR은 8%만 올랐다 — 비례 가정은 기각됐다(Prasad 2013). 기공 외 이송(그루브·간극)을 기공률 등가 360% 로 두어 두 실측점을 정확히 재현한다. 기공 경로 기여는 7.7% 뿐이다.

근거 노트(verify 블록 보유): `knowledge/cmp/slurry-turnover-ratio-mrt-preston-constant.md`, `knowledge/materials/pad-porosity-slurry-transport-mrr.md`


## Δ 손상 유발도 (`delta`) — 축: consumable · 파트: slurry, pad, disk · MRR 결합: 아니오(진단)

### 모델 정의 근거 (코드 docstring 그대로)

```
Δ 손상 유발도 — 스크래치·결함 발생 경향 (진단 전용, MRR에 곱하지 않는다).

종합 노트: knowledge/cmp/delta-damage-model-synthesis.md (2026-09-14, 기확보 노트 8편 종합).

관계식
    Δ = (D99 / D99_ref)^n × (1 + a)         기준 조건(D99 = D99_ref, a = 0)에서 정확히 1.0
    ① 꼬리 항  — 스크래치는 평균 입경이 아니라 **대입자 꼬리(D99)** 가 만든다. 임계 초과
       입자 개수축에서는 선형(Remsen 2006 Table V, doi:10.1149/1.2184036)이고, 대표 직경
       D99 축으로 옮기면 완만한 거듭제곱이 된다. n = 팩의 `damage_exponent`:
       세리아 1.44(Hitachi US8439995B2 4점 로그-로그 회귀, R²=0.997, literature) /
       텅스텐 2.54(Egan & Kim 2019 doi:10.1149/2.0311905jss 배수 2점 기하평균, literature) /
       구리 2.54(텅스텐→구리 전이, estimated) / 실리카 1.44(세리아→실리카 입자 전이, literature).
    ② 응집 항  — Basim & Moudgil 2002(doi:10.1006/jcis.2002.8352) Table 1: NaCl 0.2 M(CCC
       미달)에서 **평균 입경 불변**인데 AFM Rmax 25→50 nm(×2). D99가 못 잡는 일시적 응집
       경로가 D99 항과 독립으로 존재한다 → `1 + aggregate_ratio`, a=1이 그 논문의 불안정화
       정도. 단일점(n=1) 기반이라 계수 2.0의 화학종 외삽은 미검증. 팩에 선언될 때만 항으로
       계상(미선언 = 이 경로 미조사, 0 = 무영향).
진단 출력(배수 아님, notes로만 — status/confidence/value에 영향 없음)
    ③ 임계 위치  D99 / d_c, d_c = `scratch_threshold_nm`(680 nm, Remsen 2006; Kwon 2023 700 nm;
       Eusner 2009 응집체 610/762 nm 수렴). 계단 항으로 넣지 않는 이유: 임계 아래에서도
       카운트가 0이 아니고 5팩 다수가 임계 아래라 기준 1.0 계약과 충돌한다.
    ④ 치수 상한  2a_max = D99·√(H_p,max/H_film), δ_max = (D99/2)·(H_p,max/H_film)
       (Saka 2008 doi:10.1016/j.cirp.2008.03.098 식(14)(15) / Eusner 2009 doi:10.1149/1.3121964
       식(10)(11), Table IV 6칸 재현). 압력·패드 토포그래피에 무관하고 패드 **최대** 경도
       `pad_asperity_hardness_max_pa`(0.31 GPa)와 막 경도 `film_bulk_hardness_pa`가 정한다.
       한 팩 안에서 막 경도는 상수라 기준 대비 비가 항상 1 — 드라이버가 될 수 없다.
넣지 않은 항
    · 입자/막 경도비 배수 — 개수와 입자 경도의 정량 관계를 준 문헌이 없고, 실리카 입자(7.3 GPa)는
      SiO₂ 막(≈9~10 GPa)보다 무르므로 단조 배수는 실리카 팩에서 틀린 방향을 가리킨다.
    · 제타전위·이온강도 → 응집도 유도 — 팩에 실측 입력이 없어(oxide_silica.yaml "지어내지 않음")
      aggregate_ratio는 선언 입력으로만 둔다.
    · LPC 개수축(Fujifilm US10907074 800,000/wt% @0.2 µm) — 입력 축 미신설.
D99 없는 팩(cu_h2o2_bta·oxide_silica·w_fe_oxidizer)의 D99는 **D50 × D99/D50 일반비 5.00**
(Levitronix/Silco 2008, 2차 자료) 유도값이며 직접 측정값이 아니다 → estimated(EVIDENCE-RULES
판정#16: 일반비가 Hitachi 실측 대응쌍에서 30~60% 괴리로 재현되지 않음). what-if를 D50 배수로
넣으면 Δ는 일반비 선택에 불변이다.
한계
    · 절대 스크래치 개수는 예측하지 않는다(문헌 slope가 계마다 자릿수 차이). 팩 간 Δ 비교 금지 —
      같은 Δ라도 손상의 절대 심각도는 ④가 보이듯 막 경도가 정한다(Cu δ_max 65 nm vs W 3 nm).
    · n은 재료 상수가 아니라 "D99가 d_c의 어느 쪽에 있는가"의 함수다(종합 노트 §6-1: 로그정규
      꼬리의 국소 지수가 Hitachi 3점에서 8.4→4.6→0.7로 단조 감소, 문헌 상수 n은 그 할선). D99를
      임계를 가로질러 크게 흔들면 상수 n은 임계 아래 과소·위 과대 예측한다.
    · 2026-09-13 스코프 축소: abrasive_size_nm(평균 입경)은 드라이버가 아니다 — 평균 입경(50~150 nm)은
      임계(680 nm)보다 훨씬 작아 그 자체로는 무의미(Remsen 2006 §2.2).
```

### 팩별 상태

| 팩(공정) | status | confidence | 항(terms) | 드라이버 | 출처 |
|---|---|---|---|---|---|
| cu_h2o2_bta (Cu CMP: H2O2 산화 + BTA 패시베이션, dishing 지배 공정) | modeled | estimated | d99×1.000 | abrasive_d99_nm | abrasive-d99-scratch-hitachi-us8439995.m; lpc-scratch-density-tail-correlation.md; colloidal-destabilization-lpc-defect-mec; delta-damage-model-synthesis.md |
| oxide_silica (Oxide CMP: 실리카 슬러리, STI/ILD 평탄화) | modeled | literature | d99×1.000 | abrasive_d99_nm | abrasive-d99-scratch-hitachi-us8439995.m; lpc-scratch-density-tail-correlation.md; colloidal-destabilization-lpc-defect-mec; delta-damage-model-synthesis.md |
| sic_ceria_h2o2 (4H-SiC CMP: 세리아/H2O2 알칼리 슬러리, pH 항 실측 역산) | modeled | literature | d99×1.000 | abrasive_d99_nm | abrasive-d99-scratch-hitachi-us8439995.m; lpc-scratch-density-tail-correlation.md; colloidal-destabilization-lpc-defect-mec; delta-damage-model-synthesis.md |
| sti_ceria (STI CMP: 세리아 슬러리, oxide:nitride 고선택비) | modeled | literature | d99×1.000 | abrasive_d99_nm | abrasive-d99-scratch-hitachi-us8439995.m; lpc-scratch-density-tail-correlation.md; colloidal-destabilization-lpc-defect-mec; delta-damage-model-synthesis.md |
| w_fe_oxidizer (W plug CMP: Fe계 산화제 산성 슬러리, 알루미나 연마입자) | modeled | literature | d99×1.000 | abrasive_d99_nm | abrasive-d99-scratch-hitachi-us8439995.m; lpc-scratch-density-tail-correlation.md; colloidal-destabilization-lpc-defect-mec; delta-damage-model-synthesis.md |

엔진이 스스로 보고하는 한계:

- Δ 진단③ D99/d_c = 0.37 — 꼬리가 스크래치 임계 680 nm(Remsen 2006, Kwon 2023·Eusner 2009 교차) 아래. 배수에는 안 들어간다(위치 진단).
- Δ 진단③ D99/d_c = 0.42 — 꼬리가 스크래치 임계 680 nm(Remsen 2006, Kwon 2023·Eusner 2009 교차) 아래. 배수에는 안 들어간다(위치 진단).
- Δ 진단③ D99/d_c = 0.74 — 꼬리가 스크래치 임계 680 nm(Remsen 2006, Kwon 2023·Eusner 2009 교차) 아래. 배수에는 안 들어간다(위치 진단).
- Δ 진단③ D99/d_c = 1.03 — 꼬리가 스크래치 임계 680 nm(Remsen 2006, Kwon 2023·Eusner 2009 교차) 근처(가장 민감한 위치). 배수에는 안 들어간다(위치 진단).
- Δ 진단④ 스크래치 치수 상한(압력 무관): 폭 2a_max≈130 nm, 깊이 δ_max≈12.1 nm — Eusner 2009 식(10)(11), H_p,max=0.31 GPa, H_film=9.0 GPa. Δ 배수가 같아도 절대 심각도는 막 경도가 정한다.
- Δ 진단④ 스크래치 치수 상한(압력 무관): 폭 2a_max≈254 nm, 깊이 δ_max≈64.6 nm — Eusner 2009 식(10)(11), H_p,max=0.31 GPa, H_film=1.2 GPa. Δ 배수가 같아도 절대 심각도는 막 경도가 정한다.
- Δ 진단④ 스크래치 치수 상한(압력 무관): 폭 2a_max≈40 nm, 깊이 δ_max≈3.2 nm — Eusner 2009 식(10)(11), H_p,max=0.31 GPa, H_film=12.0 GPa. Δ 배수가 같아도 절대 심각도는 막 경도가 정한다.
- Δ 진단④ 스크래치 치수 상한(압력 무관): 폭 2a_max≈53 nm, 깊이 δ_max≈5.0 nm — Eusner 2009 식(10)(11), H_p,max=0.31 GPa, H_film=9.0 GPa. Δ 배수가 같아도 절대 심각도는 막 경도가 정한다.

근거 노트(verify 블록 보유): `knowledge/cmp/abrasive-d99-scratch-hitachi-us8439995.md`, `knowledge/cmp/delta-damage-model-synthesis.md`, `knowledge/cmp/lpc-scratch-density-tail-correlation.md`, `knowledge/slurry/colloidal-destabilization-lpc-defect-mechanism.md`


## S 시간 안정성 (`stab`) — 축: consumable · 파트: slurry, pad, disk · MRR 결합: 아니오(진단)

### 모델 정의 근거 (코드 docstring 그대로)

```
S 안정성 — 글레이징률 vs 컨디셔닝 재생률의 균형이 정하는 정상상태 패드 조도.

모델 (knowledge/materials/pad-steady-state-glazing-conditioning-balance.md §1):
    dR/dt = −k_g·R + k_c·G·(1 − R),   G = (duty/100)·A(t_disk),  A = exp(−t_disk/τ_aging)
    R_ss  = k_c·G / (k_g + k_c·G)
    S     = R_ss(G) / R_ss(G_ref)                       (G > 0, in-situ 균형; 시간 무관)
    S     = exp(−k_g·(clamp(t,1,10 min) − 1 min))       (G = 0, 무컨디셔닝 — Jeong 2024 특수해)
기준 조건(cond_ref_duty_pct=100, cond_ref_disk_usage_hours=0)에서 정확히 1.0.

파라미터 (base.yaml, 팩 5개 공통 — 패드 재질 성질):
  k_g = 0.02796 /min  Jeong et al. 2024 (doi:10.3390/ma17081817) Fig.9 pooled 로그회귀
                      (a=1.1478, b=−0.1109)의 10 min 손실 22.25%를 지수형으로 이식. 10 min 값은
                      기존 로그감쇠와 동일(회귀 테스트), 중간점 R²는 exp 0.77 > log 0.64.
  k_c = 4.08 /min     Jeong et al. 2022 ASPEN (doi:10.3850/978-981-18-6021-8_or-12-0224) Table 1
                      3 psi → 30 s 완전 회복 + Jeong 2024 복원 허용폭 ±13% → ln(1/0.13)/0.5.
  A(t_disk)           Γ과 같은 함수(sim/tier2_physics/conditioner_pcr_decay.pcr_decay, τ=27.4 h)
                      — 드레서 마모가 Γ(절삭 부하)와 S(정상상태 조도)에 한 번씩, 같은 부호로 들어간다.

검증 (같은 노트 §4 verify):
  · duty=0, t=10 min → 0.7775 = 기존 로그감쇠 값(1e−9 이내).
  · PHM2016 실장비 477 웨이퍼(validation/raw/phm2016): S 순위 vs MRR 순위 저속군 ρ=+0.696
    (원변수 드레서 사용량 −0.696의 부호 반전), 사용량→시간 배율 0.02/0.05/0.1 전부 동일 —
    데이터가 은닉 배율로 스케일돼 있어 **순위만** 검증(절대값 금지, README).

등급 판정(리터럴 하한이 아니라 계산): 비-실리카 팩의 k_g는 코퍼스에 없다(EVIDENCE-RULES
판정#9 종결 — 재탐색 금지). 그 불확실성이 이번 런에 실제로 미치는 폭을 잰다: k_g를
stab_glaze_rate_uncertainty_x(=5, Lawing 2004 fumed/colloidal)배로 바꿔 S를 재계산해
|ΔS| < 0.03(제품 오차 목표)이면 k_g는 약한 고리가 아니므로 k_c·A·duty 등급(literature)을 따르고,
넘으면 estimated. 기준점(G=G_ref)에서는 k_g가 식에서 상쇄돼 ΔS=0 — 실리카가 아니어도
in-situ 기준 운전점의 S는 문헌 등급이다. 무컨디셔닝(duty=0) 구간은 판정#9대로 실리카만 literature.

한계(문헌이 지지하지 않아 뺀 항, 노트 §6):
  · k_g 압력 지수(2 psi 0.0223 / 5 psi 0.0392 — 2점) 미도입, ±40% 밴드로만 기록. 압력은 Λ의 축.
  · G에 컨디셔너 하중·속도(F·v) 미포함 — k_c 도출 조건(0.7 psi·101 rpm)→기준(4 lbf·55 rpm) 환산
    지수 없음. 하중·속도의 S 반응은 미모델링(Γ이 부하로만 담는다).
  · 그릿 밀도·형상 → k_c(Kwon 2013 37/23/19 µm/h)는 팩에 그릿 키가 없어 미연결.
  · 수십시간 패드 수명(Son & Lee 2021)은 컨디셔너 구조 변수 부재로 판정#8 유지.
  · ε=0.13은 접촉수 기준 — k_c 자릿수(1.3~6 /min)만 확실, 4.08은 그 안의 한 점.
```

### 팩별 상태

| 팩(공정) | status | confidence | 항(terms) | 드라이버 | 출처 |
|---|---|---|---|---|---|
| cu_h2o2_bta (Cu CMP: H2O2 산화 + BTA 패시베이션, dishing 지배 공정) | modeled | literature | steady_state×1.000, R_ss(G)×0.993, R_ss(G_ref)×0.993, conditioning_strength_G×1.000, dresser_wear_A×1.000, k_g_band_dS×0.000 | time_s, cond_duty_pct, cond_disk_usage_hours | pad-steady-state-glazing-conditioning-ba; pad-glazing-mechanism-mrr-decay.md; disk-insitu-exsitu-conditioning-mrr-stab; conditioner-disk-pad-cutting-model.md; ma17081817 (PMC11051262) Fig.9; 978-981-18-6021-8_or-12-0224 Table 1 |
| oxide_silica (Oxide CMP: 실리카 슬러리, STI/ILD 평탄화) | modeled | literature | steady_state×1.000, R_ss(G)×0.993, R_ss(G_ref)×0.993, conditioning_strength_G×1.000, dresser_wear_A×1.000, k_g_band_dS×0.000 | time_s, cond_duty_pct, cond_disk_usage_hours | pad-steady-state-glazing-conditioning-ba; pad-glazing-mechanism-mrr-decay.md; disk-insitu-exsitu-conditioning-mrr-stab; conditioner-disk-pad-cutting-model.md; ma17081817 (PMC11051262) Fig.9; 978-981-18-6021-8_or-12-0224 Table 1 |
| sic_ceria_h2o2 (4H-SiC CMP: 세리아/H2O2 알칼리 슬러리, pH 항 실측 역산) | modeled | literature | steady_state×1.000, R_ss(G)×0.993, R_ss(G_ref)×0.993, conditioning_strength_G×1.000, dresser_wear_A×1.000, k_g_band_dS×0.000 | time_s, cond_duty_pct, cond_disk_usage_hours | pad-steady-state-glazing-conditioning-ba; pad-glazing-mechanism-mrr-decay.md; disk-insitu-exsitu-conditioning-mrr-stab; conditioner-disk-pad-cutting-model.md; ma17081817 (PMC11051262) Fig.9; 978-981-18-6021-8_or-12-0224 Table 1 |
| sti_ceria (STI CMP: 세리아 슬러리, oxide:nitride 고선택비) | modeled | literature | steady_state×1.000, R_ss(G)×0.993, R_ss(G_ref)×0.993, conditioning_strength_G×1.000, dresser_wear_A×1.000, k_g_band_dS×0.000 | time_s, cond_duty_pct, cond_disk_usage_hours | pad-steady-state-glazing-conditioning-ba; pad-glazing-mechanism-mrr-decay.md; disk-insitu-exsitu-conditioning-mrr-stab; conditioner-disk-pad-cutting-model.md; ma17081817 (PMC11051262) Fig.9; 978-981-18-6021-8_or-12-0224 Table 1 |
| w_fe_oxidizer (W plug CMP: Fe계 산화제 산성 슬러리, 알루미나 연마입자) | modeled | literature | steady_state×1.000, R_ss(G)×0.993, R_ss(G_ref)×0.993, conditioning_strength_G×1.000, dresser_wear_A×1.000, k_g_band_dS×0.000 | time_s, cond_duty_pct, cond_disk_usage_hours | pad-steady-state-glazing-conditioning-ba; pad-glazing-mechanism-mrr-decay.md; disk-insitu-exsitu-conditioning-mrr-stab; conditioner-disk-pad-cutting-model.md; ma17081817 (PMC11051262) Fig.9; 978-981-18-6021-8_or-12-0224 Table 1 |

엔진이 스스로 보고하는 한계:

- in-situ 균형: 시정수 1/(k_g+k_c·G)=0.24 min ≪ 연마시간이라 정상상태 — S는 time_s에 무관하고 duty·드레서 마모만 본다.
- ⚠ 미모델링: 컨디셔너 하중·속도의 S 반응(k_c 환산 지수 없음), 그릿 밀도→k_c, 수십시간 패드 수명(컨디셔너 구조 변수 부재, 판정#8). 균형 노트 §6.

근거 노트(verify 블록 보유): `knowledge/equipment/conditioner-disk-pad-cutting-model.md`, `knowledge/equipment/disk-insitu-exsitu-conditioning-mrr-stability.md`, `knowledge/materials/pad-glazing-mechanism-mrr-decay.md`, `knowledge/materials/pad-steady-state-glazing-conditioning-balance.md`


## 파라미터 도출 근거 (팩 YAML의 source/note/confidence 그대로)


### 팩 `cu_h2o2_bta` — Cu CMP: H2O2 산화 + BTA 패시베이션, dishing 지배 공정

| 키 | 값 | 단위 | confidence | 출처 | 도출 방법(note) |
|---|---|---|---|---|---|
| film | cu |  | verified |  |  |
| abrasive | alumina |  | literature | knowledge/cmp/slurry-components-overview.md |  |
| kp_m_per_pa | 3.5e-13 | m^2/N | estimated | knowledge/cmp/surface-chemistry-cu-w-pourbaix-passivation.md | ⚠ Cu는 산화막보다 MRR이 크다(연질 금속 + 화학적 산화층 제거). 이 값은 문헌 MRR 범위(400~800 nm/min @ 2~3psi)에서 역산한 대표값이며 우리가 재현 검증하지 않았다. 실데이터 캘리브레이션(M3) 전까지 절대값을 신뢰하지 마라. |
| slurry_ph | 4.0 | pH | literature | knowledge/cmp/surface-chemistry-cu-w-pourbaix-passivation.md | 산성 — Pourbaix상 Cu 용해/부동태 경계 제어 |
| oxidizer | H2O2 |  | literature | knowledge/cmp/slurry-components-overview.md |  |
| oxidizer_wt_pct | 3.0 | wt% | verified | knowledge/cmp/slurry-components-overview.md | 이번 런의 H2O2 농도. 이 값을 바꾸면 화학층이 MRR을 바꾼다 |
| oxidizer_ref_wt_pct | 3.0 | wt% | verified | knowledge/cmp/slurry-components-overview.md | 기준 농도 — 화학 배수가 1.0이 되는 지점. Kp가 이 조성의 문헌 MRR에서 역산됐으므로 반드시 명시해야 한다. 없으면 로더가 '현재 농도'로 폴백해 항상 자기 자신과 비교하게 되고 배수가 영원히 1.0이 된다(2026-09-06 실제 발생: 산화제 민감도가 '미모델링'으로 오진됐 |
| oxidizer_peak_wt_pct | 3.0 | wt% | verified | knowledge/cmp/slurry-components-overview.md | Kaufman 경쟁모델의 MRR 정점 농도. 착화제 유무로 1%→3% 이동이 확인됨. 화학층은 이 정점 대비 손실을 계산한다(정점에서 배수 1.0). |
| oxidizer_curve_n | 2.0 | - | unverified | knowledge/cmp/slurry-components-overview.md | 단봉 곡선의 정점 이후 감소 완만도. 현상론 형상 파라미터, 미검증. [식별성 판정 2026-09-14, EVIDENCE-RULES 판정#19] unverified 유지 — 근거를 못 찾아서가 아니라 현 데이터로 식별 불가능하기 때문이다. 이 팩은 C = oxidizer_ref_wt_p |
| oxidizer_passivation_K | 0.8232 | 1/wt% | estimated | knowledge/cmp/chi-oxidizer-cu-h2o2-reparameterization.md | Langmuir 부동태 피복 상수. theta(C)=K*C/(1+K*C) 이고 산화제 항은 f(C) = phi + (1-phi)*(1-theta(C))/(1-theta(C_ref)) 로, 산화제가 많을수록 Cu 표면 부동태막이 활성 사이트를 덮어 제거율이 낮아지는 방향이다. [EVIDE |
| inhibitor | BTA |  | literature | knowledge/cmp/slurry-components-overview.md |  |
| inhibitor_mM | 1.0 | mM | verified | knowledge/cmp/slurry-components-overview.md | BTA 농도. Langmuir θ=0.97 → 표면 97% 피복 = 제거 억제 |
| inhibitor_dG_ads_kJ | -35.4 | kJ/mol | estimated | knowledge/cmp/bta-inhibitor-langmuir-K-effective-cu-cmp-fals | BTA 흡착 자유에너지. K=2.9e4 L/mol로 환산되며 노트 verify 블록 PASS. 물리흡착(-20~-40 kJ/mol) 영역 — 세리아 화학흡착(-111~-258)과 대비된다. [등급 판정 2026-09-14, EVIDENCE-RULES 판정#17] verified→esti |
| inhibitor_ref_mM | 1.0 | mM | estimated | knowledge/cmp/slurry-components-overview.md | 기준 농도. 여기서 화학 배수가 정확히 1.0이 되어 Kp가 그대로 쓰인다(이중계상 방지). [등급 판정 2026-09-14, EVIDENCE-RULES 판정#24] verified→estimated 하향. 사유: 이 노트는 원래 "Kp가 이 조성(1.0mM BTA)의 문헌 MRR에서  |
| inhibitor_strength_k | 3.0 | - | unverified | knowledge/cmp/bta-inhibitor-langmuir-K-effective-cu-cmp-fals | ⚠ 억제 강도 형상 파라미터. 잔여율 = exp(-k·θ). (1-θ)를 쓰면 θ가 0.97에서 포화돼 2mM과 5mM이 구분되지 않는다(실제 발생). 실제 억제는 피복률뿐 아니라 막 치밀도·재생속도에도 달려 고농도에서도 계속 세진다. **문헌 폐형식 없음 — 캘리브레이션 1순위.**  |
| abrasive_size_nm | 100.0 | nm | literature | knowledge/cmp/abrasive-size-d50-ekc-alumina-cu-h2o2-bta-gopa | Cu+알루미나+H2O2+BTA를 정확히 동시에 다루는 1차 문헌(Gopal & Talbot 2007, JES 154(6) H507, doi:10.1149/1.2718474 — 원문 PDF 직접 확보·판독)에서 EKC Technology 알루미나 공칭 입경 100 nm(Ihnfeldt & |
| abrasive_size_exponent | 0.0 | - | literature | knowledge/cmp/abrasive-size-null-result-force-partition-theo | **검증된 영(null) 결과 — "모름"이 아니라 "효과 없음"이다.** EVIDENCE-RULES.md 판정 #1 (2026-09-11)로 확정. 5회차 순환하던 RESPONSE_DEAD를 종결한다. 충돌: Bai 2007(Appl.Surf.Sci. 253, 8489) 폐형식 유도는 |
| abrasive_d99_nm | 500.0 | nm | literature | knowledge/cmp/abrasive-particle-size-distribution-d99-tail.m | abrasive_size_nm(100 nm) × D99/D50 비율 5.00. 옛 근거(Silco/Levitronix 2008 산업 컨퍼런스 슬라이드, 화학종 무관 일반비)는 세리아 실측(Hitachi)으로 재현 안 됨이 확인돼 2026-09-14 EVIDENCE-RULES 판정#16으 |
| abrasive_ref_d99_nm | 500.0 | nm | literature | knowledge/cmp/abrasive-particle-size-distribution-d99-tail.m | 기준 조건(Δ=1.0)의 기준점 — abrasive_d99_nm과 동일값으로 이중 계상 방지. [2026-09-14 재승격] abrasive_d99_nm과 동일 사유로 confidence를 literature로 맞춘다(knowledge/cmp/abrasive-particle-size-d |
| damage_exponent | 2.54 | - | estimated | knowledge/cmp/delta-scratch-damage-d99-oversize-particle-mod | Egan & Kim 2019(ECS JSS 8(5) P3206, GLOBALFOUNDRIES 300mm 양산) 두 관측 n_temp=3.73 / n_agit=1.73의 기하평균(로그축 중앙). ⚠ 원 관측은 **텅스텐** 벌크 CMP다 — Cu로의 전이는 연마입자·촉매 계열 유사성(Sh |
| dishing_sensitivity | 1.0 | - | unverified | knowledge/cmp/pattern-dependent-dishing-erosion.md | ⚠ 미연결. dishing 정량에는 금속:산화막 MRR 비가 필요한데 아직 두 팩을 동시에 로드하는 다막질 모델이 없다(film-cu 에이전트 대기). |
| film_bulk_hardness_pa | 1200000000.0 | Pa | literature | Nanoindentation of electroplated Cu films — 결정립 크기에 따라 1.0~1 | 전해도금 구리막의 나노압입 경도. 산화막보다 한 자릿수 무르다 — 같은 접촉응력에서도 소성 쪽으로 더 가깝다는 뜻이다. ⚠ 이것은 **벌크** 경도이지 CMP 가 실제로 깎는 화학 변질층의 경도가 아니다. 변질층 경도의 절대값은 공개 문헌에 없다(_knowledge_audit/mecha |
| cu_ph_acid_k | 0.1428 | 1/pH | literature | knowledge/cmp/cu-cmp-ph-mechanism.md | Cu 산성역 pH 항의 감쇠 계수. f(pH) = exp(-k*(pH - ph_ref)). US20080090500A1 (PPG Industries Ohio; Hellring/Li/Auger, 우선일 2002-08-05) TABLE 4 에서 실리카 2/3/4 wt% 세 계열을 각자 pH |
| ph_ref | 4.0 | pH | literature | knowledge/cmp/cu-cmp-ph-mechanism.md | cu_ph_acid_k 의 기준점. 이 팩의 운전 pH 와 같게 두어 기준 조건에서 pH 항 배수가 정확히 1.0 이 되도록 한다(Kp 이중 계상 방지). WARN 본값(slurry_ph)을 옮기면 이 기준점도 함께 검토해야 한다. |
| abrasive_wt_pct | 3.0 | wt% | literature | knowledge/cmp/cu-cmp-ph-mechanism.md | US20080090500A1 TABLE 4 실험군의 실리카 농도 중앙값. 그 표는 글리신 1 wt% / BTA 1 mM / H2O2 3 wt% 를 고정하고 실리카를 0/1/2/3/4 wt% 로, pH 를 3/4/5/6 으로 완전교차한 DOE 다. WARN 이 팩에는 원래 농도 선언이 없 |
| abrasive_ref_wt_pct | 3.0 | wt% | literature | knowledge/cmp/cu-cmp-ph-mechanism.md | 농도 항의 기준점. 본값과 같게 두어 기준 조건에서 배수가 정확히 1.0 이 되도록 한다(Kp 이중 계상 방지). WARN 본값을 옮기면 이 기준점도 함께 검토해야 한다. |
| abrasive_ref_size_nm | 100.0 | nm | literature | knowledge/cmp/cu-cmp-ph-mechanism.md | 입경 항의 기준점. 이 팩의 abrasive_size_nm(100 nm)과 같게 두어 기준 조건에서 배수가 정확히 1.0 이 되도록 한다. WARN 기준점이 없어서 입경 항이 침묵했다 — 50/100/200 nm 에서 예측 MRR 이 완전히 동일했다(500.4519). 상대항 (d/d_ |
| inhibitor_species | bta |  | verified | 팩 정의 자체 (이 팩은 BTA 계 구리 슬러리다) | 이 키는 수치가 아니라 **조회 키**다. 다른 억제제를 쓰려면 이 값을 바꿔야 하고, 그러면 엔진이 그 쌍의 ΔG 를 요구한다 - 조용히 BTA 값을 재사용하지 않는다. 그것이 5,700배 오차의 원인이었다. |
| substrate_species | cu |  | verified | 팩 정의 자체 | 기질을 명시해야 하는 이유는 같은 억제제라도 기질이 바뀌면 ΔG 가 바뀌기 때문이다. 순금속과 합금도 다른 쌍이다(BTA/Cu-Ni = -22.093). |

### 팩 `oxide_silica` — Oxide CMP: 실리카 슬러리, STI/ILD 평탄화

| 키 | 값 | 단위 | confidence | 출처 | 도출 방법(note) |
|---|---|---|---|---|---|
| film | oxide |  | verified |  |  |
| abrasive | silica |  | literature | knowledge/cmp/slurry-components-overview.md |  |
| kp_m_per_pa | 1e-13 | m^2/N | verified | knowledge/cmp/preston-luo-dornfeld-mrr.md | STI 문헌 캘리브레이션점: P=20.7kPa, V=0.8m/s → MRR≈254.05 nm/min. sim/tier1_empirical/preston.py 가 이 값으로 5/5 PASS. |
| slurry_ph | 10.5 | pH | literature | knowledge/cmp/colloid-zeta-dlvo-slurry-stability.md | 실리카 슬러리 염기성 — 표면 실라놀 이온화로 제거 촉진 |
| abrasive_size_nm | 50.0 | nm | literature | knowledge/cmp/particle-wafer-interaction-mechanical-chemical |  |
| abrasive_iep_ph | 2.5 | pH | verified | knowledge/cmp/ceria-slurry-ce-redox-selectivity.md | 실리카 등전점 — pH 10.5에서 강한 음전하 → 정전 안정 |
| hamaker_j | 8.5e-21 | J | literature | knowledge/cmp/colloid-zeta-dlvo-slurry-stability.md §5 | 실리카-물-실리카 Hamaker 상수. 노트 §5: "실리카-물-실리카는 통상 ~0.85×10^-20 J 오더로 채택(본 재현값)" — sim/tier2_physics/dlvo_colloid.py self-test가 이 값으로 DLVO V_T(h) 정성 형태(장벽 존재/소멸)를 재현한다 |
| abrasive_wt_pct | 20.0 | wt% | literature | knowledge/cmp/abrasive-size-concentration-ph-K-additive-mrr- | Li et al. 2021 pH 실험 조건(20 wt% 콜로이달 실리카, K+ 0.25 mol/L). 통상 범위는 1~10 wt%(총론)이나 이 논문 계는 20~30 wt%로 높다. |
| abrasive_ref_wt_pct | 20.0 | wt% | literature | knowledge/cmp/abrasive-size-concentration-ph-K-additive-mrr- | κ 농도항 기준점 — 위와 같은 조건 |
| abrasive_conc_exponent | 0.3333 | - | literature | knowledge/cmp/abrasive-concentration-mrr-saturation-contact- | R ∝ C0^(1/3) 표면적 지배 극한. Li 2021 자체는 1/3(표면적)과 4/3(압입) 두 극한을 제시만 하고 어느 쪽인지 확정하지 않았으나(E5), 같은 화학계(TEOS/콜로이달실리카)의 US9499721B2 E1 직접 실측(TABLE 18, 0.5~3.0wt% 4압력)을 3 |
| abrasive_saturation_wt_pct | 7.0 | wt% | literature | knowledge/materials/pad-3dprinted-nonporous-lowdefect-review | Luo-Dornfeld 포화영역 — 퓸드 실리카 12 wt% 계에서 7 wt% 이상 RR 불변 확인. 이 위로는 농도항이 과대평가된다(factors.py가 경고를 띄운다). |
| abrasive_ref_size_nm | 50.0 | nm | literature | knowledge/cmp/particle-wafer-interaction-mechanical-chemical | κ 입경항 기준점 — abrasive_size_nm과 같은 값 |
| abrasive_size_peak_nm | 80.0 | nm | literature | knowledge/cmp/abrasive-size-concentration-ph-K-additive-mrr- | Li et al. 2021 Fig.4 실측 MRR 정점 위치(40/80/130nm 스윕 중 80nm 최대) |
| abrasive_size_exp_below_peak | 1.3333333333 | dimensionless | literature | knowledge/cmp/abrasive-size-concentration-ph-K-additive-mrr- | 정점 이하(40→80nm) 구간 지수 = Eq.4(압입 지배) φ 지수 4/3. 2026-09-13 pdfplumber 벡터좌표 재추출로 확정(이전 버전은 지수·부호 OCR 혼선으로 미배선 상태였음). |
| abrasive_size_exp_above_peak | -0.3333333333 | dimensionless | literature | knowledge/cmp/abrasive-size-concentration-ph-K-additive-mrr- | 정점 이상(80→130nm) 구간 지수 = Eq.3(표면적 지배) φ 지수 -1/3. 2026-09-13 pdfplumber 벡터좌표 재추출로 확정. |
| ph_peak | 11.0 | pH | verified | knowledge/cmp/abrasive-size-concentration-ph-K-additive-mrr- | MRR 최대 pH (20 wt% 실리카, K+ 0.25 M, SiO2 막). 정점형 거동 |
| ph_ref | 10.5 | pH | literature | knowledge/cmp/colloid-zeta-dlvo-slurry-stability.md | χ pH항 기준점 — 이 팩의 slurry_ph와 같은 값 |
| ph_mrr_at_peak_rel | 1.113 | - | verified | knowledge/cmp/abrasive-size-concentration-ph-K-additive-mrr- | pH 10.0 대비 pH 11.0의 MRR 비 (1727/1551 = 1.113, +11.3%). 노트 verify 블록이 이 값을 assert한다. |
| abrasive_d99_nm | 287.5 | nm | literature | knowledge/cmp/abrasive-particle-size-distribution-d99-tail.m | [2026-09-14 재승격, estimated→literature] US10894906B2(Versum Materials US, LLC, "Composite particles, method of refining and use thereof") Table 1 "No Treatment"  |
| abrasive_ref_d99_nm | 287.5 | nm | literature | knowledge/cmp/abrasive-particle-size-distribution-d99-tail.m | 기준 조건(Δ=1.0)의 기준점 — abrasive_d99_nm과 동일값으로 이중 계상 방지. [2026-09-14 재승격] abrasive_d99_nm 250→287.5 값 교체와 같은 편집에서 동반 이동 (knowledge/cmp/abrasive-particle-size-distri |
| damage_exponent | 1.44 | - | literature | knowledge/cmp/delta-scratch-damage-d99-oversize-particle-mod | US8439995B2(Hitachi 세리아) 4점 로그-로그 회귀 n=1.444, R²=0.997. 막질 일치 (산화막 CMP)이나 연마입자 불일치(세리아 vs 콜로이달 실리카) — 조건 외삽. 교차확증: Remsen 2006(퓸드실리카·산화막) Table V가 선형(n≈1)을 지지해  |
| slurry_viscosity_pa_s | 0.001 | Pa·s | literature | knowledge/materials/slurry-viscosity-rheology-literature-val | 콜로이달 실리카 CMP 슬러리 **실측** 점도. Lee et al. 2025 (Nanomaterials 15(16) 1248, DOI 10.3390/nano15161248, OA) Brookfield DV-II+Pro: 첨가제 무관 기본 슬러리 ~0.98 cP (§3.2 Fig.3a) |
| pad_ra_m | 5e-06 | m | estimated | knowledge/physics/cmp-lubrication-regimes.md §5 | 패드 raised 영역 평균거칠기 — 노트는 "~5µm 전형"으로만 명시 |
| dispersant_type | NONE | - | literature | knowledge/cmp/abrasive-size-concentration-ph-K-additive-mrr- | Li et al. 2021 §6의 기준 MRR(2700 Å/min, 무첨가)과 이 팩의 기준 조성을 일치시킨다 — 팩 기본값에서 ψ=1.0이 되어 이중 계상을 피한다. PVA(-3.6%), PVP(-7.9%)는 같은 논문 실측값이며 레시피 오버라이드로 스캔한다. |
| shield_additive_wt_pct | 0.0 | wt% | literature | knowledge/cmp/psi-adsorption-shield-oxide-systems.md §4 | 이 팩의 첨가제(음이온 계면활성제·PEG 클래스) 농도. 기본값 0 = 무첨가 — kp_m_per_pa 역산 조건(무첨가 Preston 캘리브레이션점)과 일치. 사용자가 올려도 아래 K=0 이라 산화막 MRR 은 변하지 않는다(문헌이 그렇게 말한다). |
| shield_ref_wt_pct | 0.0 | wt% | literature | knowledge/cmp/psi-adsorption-shield-oxide-systems.md §4 | 기준 농도 = kp 역산 조성(무첨가). shield_additive_wt_pct 와 짝으로 옮길 것. |
| shield_langmuir_K | 0.0 | 1/wt% | literature | knowledge/cmp/psi-adsorption-shield-oxide-systems.md §4 | **검증된 영.** Penta, Amanapu, Peethala, Babu 2013 Appl. Surf. Sci. 283, 986–992 (doi:10.1016/j.apsusc.2013.07.057) §4.5 원문: "None of the surfactants studied adsorb |
| shield_hill_n | 1.0 | - | literature | knowledge/cmp/psi-adsorption-shield-oxide-systems.md §4 | K=0 이라 무효(θ≡0). Langmuir 형식 유지용 형상 파라미터. |
| shield_strength_k | 1.0 | - | literature | knowledge/cmp/psi-adsorption-shield-oxide-systems.md §4 | K=0 이라 무효(exp(0)=1). 형식 유지용. |
| film_bulk_hardness_pa | 9e+09 | Pa | literature | Nanoindentation of thermal/TEOS SiO2 films — 표준 보고 범위 8~10 G | 열산화막·TEOS 산화막의 나노압입 경도. 3 psi 조건의 실접촉 압력(약 36 MPa)보다 두 자릿수 크므로 탄성 접촉 레짐을 가리킨다. ⚠ 이것은 **벌크** 경도이지 CMP 가 실제로 깎는 화학 변질층의 경도가 아니다. 변질층 경도의 절대값은 공개 문헌에 없다(_knowledge |
| oxidizer_wt_pct | 0.0 | wt% | literature | knowledge/cmp/cu-cmp-ph-mechanism.md | 이 팩의 기준 조성에는 산화제가 없다(산화막 CMP 는 기계·화학 마모가 지배하고 산화제를 쓰지 않는 것이 표준이다). WARN 값을 0 으로 **명시**하는 것과 키가 아예 없는 것은 다르다. 키가 없으면 검증 데이터가 산화제를 흔들어도 모델이 반응하지 못하고 (0/3/6 wt% 에서 |
| oxidizer_ref_wt_pct | 0.0 | wt% | literature | knowledge/cmp/cu-cmp-ph-mechanism.md | 산화제 항의 기준점. 본값과 같게 둔다. WARN 기준이 0 이면 상대비 C/C_ref 가 정의되지 않는다 — 산화제 항은 이 경우 '해당 없음'으로 비활성화되어야 하며, 억지로 나누면 발산한다. 산화제를 쓰는 계로 이 팩을 확장하려면 두 값을 함께 옮겨야 한다. |

### 팩 `sic_ceria_h2o2` — 4H-SiC CMP: 세리아/H2O2 알칼리 슬러리, pH 항 실측 역산

| 키 | 값 | 단위 | confidence | 출처 | 도출 방법(note) |
|---|---|---|---|---|---|
| film | sic_4h |  | measured | Wang et al. ACS SI Table S3 — 4H-SiC 웨이퍼 |  |
| abrasive | ceria |  | measured | Wang et al. ACS SI Table S3 — CeO2 연마입자 |  |
| slurry_ph | 10.0 |  | measured | Wang et al. ACS SI Table S3 — DOE 중심 수준 (pH 9/10/11) |  |
| ph_softening_ref | 10.0 |  | measured | Wang et al. ACS SI Table S3 — DOE 중심값을 기준으로 잡는다 |  |
| ph_softening_per_unit | 0.2787 |  | measured | Wang et al. ACS SI Table S3 50조건 역산 (pH만 다른 9조/12쌍, 배수 1.633 |  |
| abrasive_ref_wt_pct | 4.0 | wt% | measured | Wang et al. ACS SI Table S3 — DOE 중심 수준 (CeO2 2/4/6 wt%) |  |
| abrasive_conc_exponent | -0.406 | - | literature | knowledge/cmp/sic-alumina-concentration-negative-exponent-en | base(oxide_silica)의 +1/3(표면적지배, Li2021 콜로이달실리카 1~30wt%)을 오버라이드. SiC+알루미나 직접 실측(US20220315802A1 Table 1, n=5, 0.1~5wt%)에서 로그-로그 회귀로 지수 -0.406(음수, 압입지배 레짐) 확인 — E |
| oxidizer_ref_wt_pct | 4.0 | vol% | measured | Wang et al. ACS SI Table S3 — DOE 중심 수준 (H2O2 2/4/6 vol%) | ⚠ 키 이름은 wt_pct 인데 원문 단위는 **vol%** 다(Wang DOE: H2O2 2/4/6 vol%). H2O2 30% 수용액 기준 vol%↔wt% 는 밀도차로 약 1.1배 어긋나므로 엄밀히 같지 않다. χ 항이 **기준 대비 비(c/c_ref)** 로만 쓰므로 같은 단위끼리 |
| abrasive_size_nm | 120.0 | nm | literature | knowledge/cmp/sic-ceria-abrasive-particle-size-chen2017-rsc. | SiC+세리아 1차 문헌 실측값으로 승격(기존 base sti_ceria 상속값 80nm는 세리아가 아니라 같은 원문의 실리카 dmean을 잘못 전용한 값으로 보임 — 노트 §3). Chen et al. 2017 (RSC Adv. 7, 16938–16952, DOI 10.1039/C6R |
| dispersant_type | NONE | - | literature | knowledge/cmp/ceria-dispersant-eaa-oxide-mrr-direction-vs-si | oxide_silica 팩(→sti_ceria 경유)에서 상속된 경로였다. Li et al. 2021은 실리카 슬러리 실측이라 세리아 화학계로의 전이는 교차계 외삽(EVIDENCE-RULES E4)이고, 값 자체는 여전히 전이하지 않는다(아래 참조). 2026-09-14 EVIDENCE |
| shield_additive_wt_pct | 0.0 | wt% | literature | knowledge/cmp/psi-adsorption-shield-oxide-systems.md §6 | SiC 팩의 첨가제 농도. ⚠ 흡착상수(shield_langmuir_K) 미선언 → 이 값을 바꿔도 결과가 변하지 않는다(partial, notes 에 신고). 검색 흔적: Zhou 2015 6H-SiC Triton X-100 (doi:10.1016/j.apsusc.2015.10.158 |
| shield_ref_wt_pct | 0.0 | wt% | literature | knowledge/cmp/psi-adsorption-shield-oxide-systems.md §6 | 기준 농도(무첨가 DOE, Wang et al. ACS SI Table S3). 활성화 시 그대로 사용. |
| slurry_viscosity_pa_s | 0.0014 | Pa·s | literature | knowledge/materials/slurry-viscosity-rheology-literature-val | 세리아 슬러리 실제 점도(sti_ceria와 동일 근거: Kim 2024 DOI 10.3390/polym16243593 §3.3 Fig.17d 상용 세리아 1.41 cP, 25°C). ⚠ H2O2 추가 세리아 슬러리의 점도를 **직접 재는 문헌은 미확보**다. H2O2는 저농도 수용액이 |
| abrasive_ref_size_nm | 120.0 | nm | literature | 이 팩의 abrasive_size_nm 과 같은 출처 — 기준점은 독립 측정값이 아니라 '어느 조건에서 Kp | κ 입경항 기준점 — 이 팩의 abrasive_size_nm(120 nm)과 일치시킨다. 키가 없어 실리카 부모의 50 nm 를 상속하고 있었다 (2026-09-13 model_hygiene 극한검사가 검출). |
| abrasive_wt_pct | 4.0 | wt% | measured | Wang et al. ACS SI Table S3 — DOE 중심 수준 (CeO2 2/4/6 wt%) | 이 팩의 근거 DOE(Wang et al. ACS SI Table S3) 중심 수준. 이전에는 키가 없어 실리카 부모의 20 wt% 를 상속했는데, 그 값은 DOE 범위(2/4/6 wt%) 밖이고 이 재료계의 근거가 아니다 — 기준점 4.0 과 5배 어긋나 기준조건에서 κ 농도항이 0. |
| wafer_iep_ph | 4.9 | pH | literature | knowledge/cmp/sic-isoelectric-point-singh2006-jnr.md | SiC 표면 등전점(1차 문헌 실측, 분산제 무첨가 조건, PCD·입도·점도 3중 정합). base(sti_ceria)에서 상속되던 실리카 산화막 IEP(2.5)는 SiC 표면이 아니라 다른 막질(oxide_silica) 것이므로 이 팩 전용값을 명시적으로 선언한다(sim/factors |
| film_bulk_hardness_pa | 26000000000.0 | Pa | literature | Nanoindentation of 4H-SiC single crystal — 보고 범위 24~28 GPa | 4H-SiC 단결정의 나노압입 경도. 이 저장소에서 가장 단단한 막질이고, 그래서 같은 압력에서도 탄성 쪽에 깊이 머문다. ⚠ 이것은 **벌크** 경도이지 CMP 가 실제로 깎는 화학 변질층의 경도가 아니다. 변질층 경도의 절대값은 공개 문헌에 없다(_knowledge_audit/mec |
| abrasive_size_peak_nm | 163.0 | nm | literature | knowledge/cmp/ceria-abrasive-size-mrr-peak-shift-vs-silica.m | 세리아 입경-MRR 정점. 근거·한계·등급은 sti_ceria.yaml 의 동일 키와 같다 (Oh et al. 2010 MEE DOI 10.1016/j.mee.2010.07.040, 62/116/163/232 nm 중 163 nm 최대 — 1차 전문 미확보, Wang et al. 202 |
| abrasive_size_exp_below_peak | 1.3333333333 | dimensionless | literature | knowledge/cmp/ceria-abrasive-size-mrr-peak-shift-vs-silica.m | 압입 지배 d^(4/3). Bellahsene et al. 2025 (DOI 10.3390/nano15171366, MDPI OA, 전문 확보) §2.1 Eq.(1) 메커니즘 폐형식. 상속을 끊고 명시 재선언 (값은 부모와 동일하나 판단 주체를 이 팩으로 옮긴다). ⚠ 세리아·SiC 계 |
| abrasive_size_exp_above_peak | -0.3333333333 | dimensionless | literature | knowledge/cmp/ceria-abrasive-size-mrr-peak-shift-vs-silica.m | 표면적 지배 d^(-1/3). 근거·한계는 abrasive_size_exp_below_peak 와 동일. ⚠ 이 팩의 본값 120 nm 는 정점 163 nm 아래이므로 이 지수는 현재 기준조건에서 발동하지 않는다(120 nm < 163 nm → below 가지). 입경 슬라이더를 163 |
| ph_ref | 10.0 | pH | literature | 이 팩의 slurry_ph 와 같은 출처 — 기준점은 독립 측정값이 아니라 "어느 조건에서 Kp 를 역산했는 |  |
| oxidizer_wt_pct | 3.0 | wt% | literature | knowledge/cmp/cu-cmp-ph-mechanism.md | 이 팩의 기준 조성 산화제 농도. oxidizer_ref_wt_pct 와 짝을 이룬다. WARN 기준점(ref)은 있는데 본값이 없어서 산화제 항이 침묵했다 — 0/3/6 wt% 에서 예측 MRR 이 완전히 동일했다(314.5698). override 로만 주입되는 축은 팩이 본값을 모 |

### 팩 `sti_ceria` — STI CMP: 세리아 슬러리, oxide:nitride 고선택비

| 키 | 값 | 단위 | confidence | 출처 | 도출 방법(note) |
|---|---|---|---|---|---|
| abrasive | ceria |  | verified | knowledge/cmp/ceria-slurry-ce-redox-selectivity.md |  |
| kp_m_per_pa | 2.2e-13 | m^2/N | estimated | knowledge/cmp/ceria-slurry-ce-redox-selectivity.md | ⚠ 세리아는 화학결합(Si-O-Ce) 기반이라 실리카보다 산화막 MRR이 높다. Netzband 2020에서 H2O2 첨가 시 Ce3+ 증가로 MRR 5.5배 변화가 보고됐는데, 그건 조성 의존이라 단일 상수로 뭉뚱그린 이 값은 대표값일 뿐이다. 미재현. |
| slurry_ph | 5.5 | pH | verified | knowledge/cmp/ceria-slurry-ce-redox-selectivity.md | 세리아 IEP 6.8 부근 아래 — 약양전하로 실리카 표면(음전하) 정전인력 |
| abrasive_iep_ph | 6.8 | pH | verified | knowledge/cmp/ceria-slurry-ce-redox-selectivity.md |  |
| ph_ref | 5.5 | pH | verified | knowledge/cmp/ceria-slurry-ce-redox-selectivity.md §4 | 세리아 정전 창(2.5~6.8) 안의 기준점 — slurry_ph와 같은 값 |
| wafer_iep_ph | 2.5 | pH | literature | knowledge/cmp/ceria-slurry-ce-redox-selectivity.md §4 | 실리카 산화막 표면 IEP. 정전 창의 하단. 2차 인용 범위(2~3) |
| abrasive_size_nm | 60.0 | nm | literature | knowledge/cmp/sti-cmp-ceria-high-selectivity-nitride-stop-di | Dandu Veera, Peddeti, Babu 2009 (J. Electrochem. Soc. 156(12) H936-H943, doi:10.1149/1.3230624) — Rhodia Inc. 세리아 슬러리, 원문 명시 "mean diameter d_mean = 60 nm" (무첨가 |
| abrasive_d99_nm | 700.0 | nm | literature | knowledge/cmp/abrasive-d99-scratch-hitachi-us8439995.md §2.2 | Hitachi US8439995B2 Example 1 D99(문헌 실측) — 화학종(세리아, STI/ILD 산화막 CMP) 일치를 근거로 기준점(baseline)에 이식. 팩의 실제 조성값 아님, what-if 스캔용 기준. [등급 판정 2026-09-14, EVIDENCE-RULES  |
| abrasive_ref_d99_nm | 700.0 | nm | literature | knowledge/cmp/abrasive-d99-scratch-hitachi-us8439995.md §2.2 | 기준 조건(Δ=1.0)의 기준점 — abrasive_d99_nm과 동일값으로 이중계상 방지. [2026-09-14] abrasive_d99_nm과 동일 사유로 confidence를 literature로 맞춘다(EVIDENCE-RULES 판정#16). |
| damage_exponent | 1.44 | - | literature | knowledge/cmp/abrasive-d99-scratch-hitachi-us8439995.md §3 | US8439995B2 4점 실측 로그-로그 회귀값(n=1.44, R²=0.997) — sim/factors.py 기본값(3.0, 문헌 근거 없는 가정값)보다 약 2배 완만. 세리아 화학종 한정(텅스텐/알루미나는 별도 검토 필요, egan-kim2019 n_temp=3.73· n_agit |
| oxide_nitride_selectivity | 60.0 | - | literature | knowledge/cmp/ceria-slurry-ce-redox-selectivity.md | Hwang 2024 실측 선택비 59~80 범위의 하단. 아미노산/계면활성제 첨가로 제어된다. ⚠ 엔진은 아직 이 값을 쓰지 않는다 — nitride 정지층 모델(film-nitride) 미구현. |
| ce3_fraction | 0.15 | - | literature | knowledge/cmp/ceria-slurry-ce-redox-selectivity.md | 표면 Ce3+ 분율. 산소공공 x에 대해 전하균형 f=2x (노트 verify PASS). H2O2 0.5wt% 첨가 시 최대가 되며, 이때 oxide MRR이 상용 대비 5.5배로 보고됐다(Netzband & Dunn 2020). 이 값을 올리면 화학층이 MRR을 올린다. |
| ce3_fraction_ref | 0.15 | - | estimated | knowledge/cmp/ceria-slurry-ce-redox-selectivity.md | 기준 조건(배수 1.0이 되는 지점). 여기서 Kp가 캘리브레이션돼 있다고 본다 |
| ceria_tooth_gain | 1.0 | - | literature | knowledge/cmp/ceria-tooth-ce3-mrr-exponent-netzband-pair.md  | Ce3+ 분율 → MRR 배수의 진폭(기준 조건에서 화학 경로가 차지하는 몫의 배율). [2026-09-14 EVIDENCE-RULES 판정#23] 이전 주석은 이 값을 "캘리브레이션 1순위"로 지목했으나, 그 방향이 애초에 막다른 길임이 증명됐다: 선형 형태에서는 gain을 어떻게 잡 |
| ceria_tooth_exponent | 1.65 | - | literature | knowledge/cmp/ceria-tooth-ce3-mrr-exponent-netzband-pair.md  | Ce3+ 활성점 분율에 대한 MRR 멱지수 p. f(theta) = floor + a*(theta/theta_ref)^p. Netzband & Dunn 2019(ECS JSS 8 P629, XPS) Fig.4+Table I의 theta 와 2020(ECS JSS 9 044001) 본문의 |
| dispersant_type | NONE | - | literature | knowledge/cmp/ceria-dispersant-eaa-oxide-mrr-direction-vs-si | oxide_silica 팩에서 상속된 경로였다. Li et al. 2021은 실리카 슬러리 실측이라 세리아(STI/SiC) 화학계로의 전이는 교차계 외삽(EVIDENCE-RULES E4)이고, 값 자체는 여전히 전이하지 않는다(아래 참조). 2026-09-14 EVIDENCE-RULES |
| shield_additive_wt_pct | 0.0 | wt% | literature | knowledge/cmp/psi-adsorption-shield-oxide-systems.md §3 | 음이온 계면활성제 농도. 기본값 0 = 무첨가 — 이 팩의 kp·abrasive_size(Dandu 2009 무첨가 60 nm 세리아)와 조건 일치. 관측 창 0~0.8 wt%(Park 2003). 0.08 wt% 이상에서 질화막이 정지(임계농도), 0.4 wt%부터 산화막도 떨어지기  |
| shield_ref_wt_pct | 0.0 | wt% | literature | knowledge/cmp/psi-adsorption-shield-oxide-systems.md §3 | 기준 농도 = kp 역산 조성(무첨가). shield_additive_wt_pct 와 짝으로 옮길 것. |
| shield_langmuir_K | 1.2949 | 1/wt% | estimated | knowledge/cmp/psi-surface-adsorption-shield-oxide-ceria.md § | 산화막(SiO₂) 협동 흡착 역-임계농도(C₅₀=0.772 wt%). Park, Katoh, Lee, Jeon, Paik 2003 JJAP 42(9A) 5420 (DOI: 10.1143/JJAP.42.5420) Fig.3(a) 9점 상대오차 가중 회귀(최대 오차 6.6%); 텍스트 정박 |
| shield_hill_n | 4.62 | - | estimated | knowledge/cmp/psi-surface-adsorption-shield-oxide-ceria.md § | Hill 협동성 지수(hemimicelle 문턱). Park 2003 Fig.3 회귀. ⚠ [2026-09-15 반증 시도] 이 값은 산화막 단독 데이터로는 식별되지 않는다 — 산화막 SSE 프로파일이 n=4~20 구간에서 15% 이내로 평평하다(비식별). 실제로 n≈4.6에 진짜 최소 |
| shield_strength_k | 3.0 | - | estimated | knowledge/cmp/psi-surface-adsorption-shield-oxide-ceria.md § | 피복→잔여율 지수감쇠 강도(exp(−k·θ)). 하한 k≥1.62(0.8 wt% 잔여율 1/5 제약). 3.0 선택 근거: θ_max=0.54 로 포화 구간을 피해 고농도 구분이 살아 있다(노트 §5.5). [2026-09-15 독립 재현] 산화막 SSE 프로파일이 평평하다는 비식별 자 |
| shield_nitride_langmuir_K | 14.02 | 1/wt% | estimated | knowledge/cmp/psi-surface-adsorption-shield-oxide-ceria.md § | 질화막(Si₃N₄) 협동 흡착 역-임계농도 C₅₀=0.0713 wt% — 원문 본문 임계농도 0.08 wt% 와 독립 일치(회귀는 Fig.3(b) 마커만 사용). 산화막 K 의 10.8배 = 선택비 창의 기원. 진단 출력 전용(엔진 MRR 에는 산화막 배수만 곱한다). |
| shield_nitride_hill_n | 4.62 | - | estimated | knowledge/cmp/psi-surface-adsorption-shield-oxide-ceria.md § |  |
| shield_nitride_strength_k | 3.4 | - | estimated | knowledge/cmp/psi-surface-adsorption-shield-oxide-ceria.md § | 질화막 쪽 k 는 SSE 곡률이 있어 식별된다(k=2 SSE 26.2 / 3.4 → 0.46 / 6 → 1.70). |
| slurry_viscosity_pa_s | 0.0014 | Pa·s | literature | knowledge/materials/slurry-viscosity-rheology-literature-val | 세리아 CMP 슬러리 **실제** 점도. Kim et al. 2024 (Polymers 16(24) 3593, DOI 10.3390/polym16243593) §3.3 Fig.17d: 상용 세리아 슬러리 초기 실제 **1.41 cP** (25°C, Brookfield cone/plate |
| abrasive_ref_size_nm | 60.0 | nm | literature | 이 팩의 abrasive_size_nm 과 같은 출처 — 기준점은 독립 측정값이 아니라 '어느 조건에서 Kp | κ 입경항 기준점 — 이 팩의 abrasive_size_nm(60 nm)과 일치시킨다. 키가 없어 실리카 부모의 50 nm 를 상속해 기준조건 κ=1.275 였다 (2026-09-13 model_hygiene 극한검사가 검출). 값이 아니라 기준점만 옮기므로 예측 형상은 불변이고 배수만 |
| abrasive_size_peak_nm | 163.0 | nm | literature | knowledge/cmp/ceria-abrasive-size-mrr-peak-shift-vs-silica.m | 세리아 산화막 CMP 입경-MRR 정점. Oh, Singh, Gupta, Cho 2010 (Microelectronic Engineering, DOI 10.1016/j.mee.2010.07.040) — 수열합성 단결정 세리아 62/116/163/232 nm 4점 1축 스윕에서 163 n |
| abrasive_size_exp_below_peak | 1.3333333333 | dimensionless | literature | knowledge/cmp/ceria-abrasive-size-mrr-peak-shift-vs-silica.m | 정점 이하 구간 지수 = 압입 지배 d^(4/3). 값 자체는 부모(oxide_silica)와 같지만 **상속이 아니라 이 계에 대한 판단으로 재선언**한다 — 재료 특이 키를 상속시키면 부모가 바뀔 때 세리아 팩이 조용히 끌려간다(같은 결함이 wafer_iep_ph 에서도 발생했다). |
| abrasive_size_exp_above_peak | -0.3333333333 | dimensionless | literature | knowledge/cmp/ceria-abrasive-size-mrr-peak-shift-vs-silica.m | 정점 이상 구간 지수. 근거·한계는 abrasive_size_exp_below_peak 와 동일 (Bellahsene 2025 §2.1 표면적 지배 가지). 세리아 재추정 없음 — 미검증. |

### 팩 `w_fe_oxidizer` — W plug CMP: Fe계 산화제 산성 슬러리, 알루미나 연마입자

| 키 | 값 | 단위 | confidence | 출처 | 도출 방법(note) |
|---|---|---|---|---|---|
| film | w |  | verified |  |  |
| abrasive | alumina |  | literature | knowledge/cmp/slurry-components-overview.md |  |
| kp_m_per_pa | 2.8e-13 | m^2/N | estimated | knowledge/cmp/surface-chemistry-cu-w-pourbaix-passivation.md | ⚠ 문헌 W MRR 범위(300~600 nm/min @ 3psi)에서 역산한 대표값. 미재현. W는 Fe(III)/H2O2 산화 후 기계적 제거라 산화막과 메커니즘이 다르다. |
| slurry_ph | 2.5 | pH | literature | knowledge/cmp/surface-chemistry-cu-w-pourbaix-passivation.md | 강산성 — Pourbaix상 W 산화물 용해 억제하며 부동태막 유지 |
| ph_ref | 2.5 | pH | literature | knowledge/cmp/w-cmp-ph-acidic-oxidizer-mediated-stojadinovic | 이 팩의 기준 pH. 기준조건에서 pH 항이 정확히 1.0 이 되도록 slurry_ph 와 같다. |
| w_ph_acid_k | 0.1163 | 1/pH | literature | knowledge/cmp/w-cmp-ph-acidic-oxidizer-mediated-stojadinovic | f(pH)=exp(-k*(pH-ph_ref)). Stojadinovic 2016 Table 1 (3% 실리카 12nm, KIO3 4수준 고정, HCl 로 pH 만 5->2) 의 산화제 존재 3조건 MRR 비 1.429/1.533/1.300 을 로그평균해 dpH=3 으로 나눈 값. 재현오 |
| oxidizer | Fe(NO3)3 |  | literature | knowledge/cmp/slurry-components-overview.md |  |
| oxidizer_wt_pct | 3.0 | wt% | literature | papers/US20110186542A1.txt | 이번 런의 H2O2 농도. Fe(III) 활성제와 공존하는 W 슬러리의 통상 상한 구간. |
| oxidizer_ref_wt_pct | 3.0 | wt% | literature | papers/US20110186542A1.txt | 기준 농도 — 화학 배수 1.0. 실시예 표의 최고 농도(3 wt%)를 기준으로 상대화했다. |
| oxidizer_peak_wt_pct | 6.0 | wt% | estimated | papers/US20110186542A1.txt | ⚠ 실측 3점(0/1/3 wt%)이 단조 증가라 정점을 직접 못 봤다. Kaufman 단봉을 0→1→3의 상대비(0.14/0.63/1.0)에 격자 적합해 얻은 값(n=3, log-err 0.012). 3 wt% 위는 외삽. (비활성 — Langmuir 경로로 대체됨, 판정#19) |
| oxidizer_curve_n | 3.0 | - | estimated | papers/US20110186542A1.txt | 위와 같은 적합에서. 현상론 형상 파라미터. [식별성 판정 2026-09-14, EVIDENCE-RULES 판정#19] 등급 불변(estimated 유지) — 단 이 값은 잔차 최소해가 아니며, 애초에 식별 가능한 값이 아니다. 정점(C_peak) 아래 관측만 있으면 (n, C_peak |
| oxidizer_langmuir_K | 0.54955 | 1/wt% | literature | papers/US20110186542A1.txt | 판정#19(chi-oxidizer-curve-exponent-identifiability.md)로 (n, C_peak) 형상이 정점 아래 관측만으로는 완전축퇴(식별 불가)임이 확인됨에 따라, 식별 가능한 1파라미터 Langmuir 표면피복 θ(C)=K·C/(1+K·C)로 대체한다. 폐형 |
| oxidizer_mech_floor | 0.14 | - | literature | papers/US20110186542A1.txt | H2O2 0 wt%에서 남는 순수 기계 연마 분율(3 wt% 대비). 15조건 전부에서 0.117~0.189, 평균 0.142. Kaufman 단봉은 C=0에서 0이라 이 바닥이 없으면 산화제 0 예측이 0이 된다. |
| abrasive_size_nm | 50.0 | nm | literature | knowledge/cmp/w-cmp-abrasive-d50-bielmann1999-osti-cabot-con | Bielmann et al. 1999(ECS Solid-State Lett. 2(3) 148, DOI:10.1149/1.1390765) 실측 W CMP 폴리싱 슬러리의 γ-알루미나 1차입자경("primary size ~50 nm diam"). 원래 후보였던 OSTI 0.7μm(질산철 문 |
| abrasive_ref_size_nm | 50.0 | nm | literature | knowledge/cmp/w-cmp-abrasive-d50-bielmann1999-osti-cabot-con | κ 입경항 기준점 — abrasive_size_nm과 같은 값(cu_h2o2_bta의 abrasive_ref_size_nm 패턴과 동일). |
| abrasive_size_exponent | 0.0 | - | literature | knowledge/cmp/w-cmp-abrasive-size-null-result-egan-kim-2019. | **검증된 영(null) 결과** — cu_h2o2_bta와 독립적인 두 번째 계에서 확정. Egan & Kim 2019(ECS JSSTechnol. 8(5) P3206, DOI:10.1149/2.0311905jss, GLOBALFOUNDRIES W contact CMP 실제 양산 데이 |
| abrasive_wt_pct | 10.0 | wt% | literature | knowledge/cmp/kappa-abrasive-concentration-cu-w-cooper-bielm | Bielmann et al. 1999(같은 논문·같은 문장, 위 abrasive_size_nm과 동일 출처) — "The polishing slurries contained 10 wt % γ-alumina particles". 입경과 농도를 같은 실험·같은 문장에서 동시 확보해 내적 정 |
| abrasive_ref_wt_pct | 10.0 | wt% | literature | knowledge/cmp/kappa-abrasive-concentration-cu-w-cooper-bielm | κ 농도항 기준점 — 이 실험 조건 자체(Bielmann 1999)를 기준으로 잡아 κ=1.0 계약 유지 |
| abrasive_conc_exponent | 0.3333 | - | literature | knowledge/cmp/kappa-abrasive-concentration-cu-w-cooper-bielm | Wang et al. 2012(ECS Trans. 41(43) 103-111, DOI:10.1149/1.4717508, Applied Materials Reflexion GT 실제 W CMP 실험)이 W 계에서 **직접** "the removal rate was observed to s |
| abrasive_d99_nm | 250.0 | nm | literature | knowledge/cmp/abrasive-particle-size-distribution-d99-tail.m | abrasive_size_nm(50 nm, Bielmann 1999 실측) × D99/D50 비율 5.00 = 250 nm. 옛 근거(Silco/Levitronix 2008 일반비, 세리아 실측으로 재현 안 됨)로 2026-09-14 EVIDENCE-RULES 판정#16이 estimat |
| abrasive_ref_d99_nm | 250.0 | nm | literature | knowledge/cmp/abrasive-particle-size-distribution-d99-tail.m | 기준 조건(Δ=1.0)의 기준점 — abrasive_d99_nm과 동일값으로 이중 계상 방지. [2026-09-14 재승격] abrasive_d99_nm과 동일 사유로 confidence를 literature로 맞춘다(knowledge/cmp/abrasive-particle-size-d |
| damage_exponent | 2.54 | - | literature | knowledge/cmp/delta-scratch-damage-d99-oversize-particle-mod | Egan & Kim 2019(ECS JSS 8(5) P3206) 두 관측의 기하평균 √(3.73×1.73). 막질·공정 완전 일치(텅스텐 벌크 CMP, 300mm 양산 라인 defect inspection 실측). ⚠ 각 관측이 n=1 단일 대응쌍이고 저자 서술이 반올림("sixty t |
| inhibitor | picolinic_acid |  | literature | knowledge/cmp/w-cmp-picolinic-acid-inhibitor-langmuir-dissol |  |
| inhibitor_mM | 121.8 | mM | literature | knowledge/cmp/w-cmp-picolinic-acid-inhibitor-langmuir-dissol | 1.5 wt% 피콜린산(포화 농도, 밀도 1 g/mL 근사)에 해당하는 몰농도. 원문 Lee & Seo(2022) 3.3절에서 정지식각 90->11 A/min(8.2배 감소), CMP 제거율 120->85 A/min(1.41배 감소)의 실측 포인트. [등급 판정 2026-09-14, E |
| inhibitor_K_L_per_mol | 1108.0 | L/mol | literature | knowledge/cmp/w-cmp-picolinic-acid-inhibitor-langmuir-dissol | 원문 Table 1 Langmuir 상수 b=0.009 L/mg를 MW=123.11 g/mol로 몰단위 환산. 노트 verify 블록 PASS(K=1108 L/mol). |
| inhibitor_ref_mM | 121.8 | mM | estimated | knowledge/cmp/w-cmp-picolinic-acid-inhibitor-langmuir-dissol | 기준 농도 = inhibitor_mM과 동일(1.5 wt% 포화점) — 이중계상 방지를 위한 정의. [등급 판정 2026-09-14, EVIDENCE-RULES 판정#24] estimated 유지. 원래 이 노트가 "kp_m_per_pa가 이 농도 근처에서 역산됐다"고 적었으나, kp_ |
| inhibitor_strength_k | 2.117 | - | unverified | knowledge/cmp/psi-inhibitor-strength-k-grade-ruling.md | 정지식각 90->11 A/min(8.2배 감소, 1.5wt% 앵커) 역산값. Cu/BTA의 k=3.0(cu_h2o2_bta.yaml)과 다른 화학종 전용 값. [등급 판정 2026-09-14, EVIDENCE-RULES 판정#24] unverified 유지(승격하지 않음). 사유: 원문 |
| film_bulk_hardness_pa | 12000000000.0 | Pa | literature | Nanoindentation of CVD W films — 보고 범위 10~14 GPa | CVD 텅스텐막의 나노압입 경도. ⚠ 이것은 **벌크** 경도이지 CMP 가 실제로 깎는 화학 변질층의 경도가 아니다. 변질층 경도의 절대값은 공개 문헌에 없다(_knowledge_audit/mechanics.md 의 최대 병목). 다만 변질층은 벌크보다 무르므로 H_surface ≤  |

## 검증 (특허·논문 held-out)

| 팩(공정) | 데이터셋 | 유의 | 유의 평균 ρ |
|---|---|---|---|
| cu_h2o2_bta (Cu CMP: H2O2 산화 + BTA 패시베이션, dishing 지배 공정) | 6 | 2 | 0.8587 |
| oxide_silica (Oxide CMP: 실리카 슬러리, STI/ILD 평탄화) | 7 | 2 | 0.996 |
| sic_ceria_h2o2 (4H-SiC CMP: 세리아/H2O2 알칼리 슬러리, pH 항 실측 역산) | 3 | 1 | 1.0 |
| sti_ceria (STI CMP: 세리아 슬러리, oxide:nitride 고선택비) | 5 | 2 | 0.95 |
| w_fe_oxidizer (W plug CMP: Fe계 산화제 산성 슬러리, 알루미나 연마입자) | 2 | 1 | 1.0 |

## 미충족 항목

- C2 χ chi/cu_h2o2_bta(Cu CMP: H2O2 산화 + BTA 패시베이션, dishing 지배 공정): confidence=estimated → **[전진가능]** 판정#20 (상세: `validation/C2-RESIDUAL-CLASSIFICATION.md`)