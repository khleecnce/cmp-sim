# FabSim 엔진

- tier1_empirical: Preston, Luo-Dornfeld 등 경험식 + 운동학
- tier2_physics: 접촉역학·유동·화학 물리모델
- tier3_surrogate: 스몰데이터 ML (GP/BNN)

규칙: 모든 모델은 문헌 재현값 테스트 동반.
실행: `source .venv/bin/activate` 후 각 모듈을 `python3 <파일>` 로 직접 실행하면 self-test가 돈다.

## 파라미터 팩 — 껍데기(코드)와 내용(물성)의 분리

**엔진은 물리 상수를 갖고 있지 않다.** 막질·슬러리·패드 물성은 전부
`knowledge/params/*.yaml`(파라미터 팩)이 소유하고, 엔진은 팩 이름을 받아 읽는다.

```bash
python -m sim.cli --list-packs                    # 어떤 조건들이 있나
python -m sim.cli --pack cu_h2o2_bta --time 60    # Cu CMP
python -m sim.cli --pack w_fe_oxidizer --time 60  # W CMP — 코드 동일
```

새 공정을 추가하는 방법은 **YAML 한 장을 쓰는 것**이지 파이썬을 고치는 게 아니다.
`w_fe_oxidizer.yaml`이 그 증거다 — sim/ 코드를 한 줄도 안 고치고 추가했다.

### 팩의 규약

```yaml
base: oxide_silica          # 상속 (base → oxide_silica → 이 팩)
description: "..."
params:
  kp_m_per_pa:
    value: 3.5e-13
    unit: m^2/N
    source: knowledge/cmp/...md   # 필수 — 근거 없는 숫자 금지
    confidence: estimated          # verified|literature|estimated|unverified
    note: "왜 이 값인지, 무엇이 불확실한지"
```

- **없는 값은 지어내지 않는다.** 팩에 없는 물성을 요구하면 `ParamMissing`으로
  즉시 죽는다. Cu 팩을 돌렸는데 산화막 Kp가 조용히 쓰이면 결과 전체가 거짓말이다.
- **쓰인 값의 신뢰도가 결과에 따라 나온다.** `confidence`가 verified가 아닌 값을
  쓰면 `WaferResult.notes`에 ⚠ 경고가, `provenance`에 출처가 실린다.
- **⚠ YAML 1.1 함정**: `1.0e11`처럼 지수부에 부호가 없으면 YAML이 **문자열**로
  파싱한다. `sim/params.py`의 `_coerce_number()`가 정규화하고
  `test_numeric_params_are_numbers_not_strings`가 회귀를 막는다. 이걸 놓치면
  `can't multiply sequence by non-int`라는 엉뚱한 자리에서 터진다(실제 발생).

### 레시피 vs 팩

`Recipe`는 **사람이 이번 런에 정하는 것**(압력·rpm·시간·존압력)만 담는다.
물성 필드를 `None`으로 두면 팩이 채우고, 명시하면 그 값이 팩을 덮어쓴다.

## 테스트 실행법

각 모듈의 self-test(위 방식)와는 별도로, `tests/`에 pytest 기반 회귀 테스트 하네스가
있다. 새 모듈을 추가할 때 기존 모듈들을 사람이 하나씩 재실행해 확인할 필요 없이,
아래 한 줄로 전체 회귀를 한 번에 확인할 수 있다.

```
cd ~/fab-sim && source .venv/bin/activate && python -m pytest tests/ -v
```

- `tests/test_<모듈명>.py`가 각 sim/ 모듈(kinematics, preston, process_time,
  viscoelastic_maxwell, gw_contact)에 대응한다. 각 파일은 해당 모듈의
  `if __name__ == "__main__":` self-test 블록이 확인하는 항목을 그대로 pytest
  assert로 재구현한 것이며, 모듈의 함수를 import해서 호출만 할 뿐 물리 로직을
  재정의하지 않는다.
- `tests/conftest.py`가 `sim/tier1_empirical`, `sim/tier2_physics`를 sys.path에
  추가한다 — preston.py가 내부에서 `from kinematics import ...`(동일 폴더 기준
  bare import)를 쓰는 등, 모듈들이 스크립트 직접 실행을 전제로 상호 import하기
  때문에 pytest에서도 동일한 경로 조건을 맞춰줘야 한다.
- 새 모듈을 추가하면 같은 패턴으로 `tests/test_<새모듈>.py`를 추가하면 된다.

## 구현 현황

### tier1_empirical/kinematics.py — 회전식 CMP 운동학 (2026-09-03)
근거 지식: `knowledge/physics/cmp-kinematics-rotary.md` (Lai, MIT PhD thesis 2001, Ch.2)

제공 API
- `relative_velocity(x, y, ω_w, ω_p, r_cc)` → 상대속도 성분·크기 (Lai Eq. 2.11)
- `relative_speed_polar(r̄, θ, …)` → 극좌표 등가식
- `kinematic_number(R_w, r_cc, rpm_w, rpm_p)` → µ = (R_w/r_cc)(1−Rs)
- `speed_stats(...)` → 면적가중 평균/최대/최소/CV/비균일도
- `preston_mrr_profile(...)` → 반경별 시간평균 Preston MRR

**self-test 결과 (2026-09-03 실행, 7/7 PASS)**
| 검증 | 결과 |
|---|---|
| Rs=1 → 웨이퍼 전면 상대속도 균일 (Lai Eq.2.12) | \|v\|=1.256637 m/s = ω_p·r_cc, std=0.00e+00 ✔ |
| 비균일도 = 2\|µ\| 해석해 (50/55/66/72 vs 60rpm) | 25.0000 / 12.5000 / 15.0000 / 30.0000 %, 오차<1e-12 ✔ |
| 직교식(Lai) ≡ 극좌표식(JJMIE 2026) | 최대차 2.22e-16 m/s ✔ |
| Rs=1 Preston 반경 프로파일 | 편차 0.00e+00 (완전 평탄) ✔ |
| Rs=50/60 프로파일 | edge/center = 1.00391 (엣지 fast) ✔ |

핵심 시사점: 운동학 기인 MRR 비균일도는 자전 시간평균으로 대부분 상쇄된다
(순간 25% → 시간평균 0.39%). → WIWNU 모델의 주 항은 **압력분포**여야 한다.

### tier1_empirical/preston.py — Preston 선형 MRR v0 (2026-09-04)
근거 지식: `knowledge/cmp/preston-luo-dornfeld-mrr.md`

제공 API
- `local_mrr(x, y, ω_w, ω_p, r_cc, P, kp)` → 국소 순간 MRR [m/s] = Kp·P·|v|
- `mrr_profile(...)` → 반경별 시간평균 MRR (압력 반경분포 pressure_fn 확장 가능)
- `wafer_avg_mrr(...)` → 웨이퍼 전면 면적가중 평균 MRR (스루풋 추정용)
- `mrr_to_nm_per_min(...)` → 단위 변환

**self-test 결과 (2026-09-04 실행, 5/5 PASS)**
| 검증 | 결과 |
|---|---|
| P 2배 → MRR 2배 | ratio=2.000000000 ✔ |
| V 2배 → MRR 2배 | ratio=2.000000000 ✔ |
| 문헌 오더 대조 (SiO2 STI, P=20.7kPa, Kp=1e-13) | 모델 156.1 nm/min vs 문헌범위 50-1000+ nm/min(대표 254 nm/min) ✔ |
| Rs=1 반경 프로파일 (균일압력) | 편차 0.00e+00 (완전 평탄) ✔ |
| Rs=50/60 edge/center | 1.00391, kinematics.py와 교차검증 일치 ✔ |

핵심 시사점: Preston v0(균일압력 가정)에서는 구조적으로 WIWNU=0이 나온다 —
즉 실측 WIWNU를 설명하려면 다음 단계(Lv2-2)에서 반드시 압력 분포 항을 추가해야 함이
코드 레벨에서도 재확인됨. Luo-Dornfeld형(P^1/2) 확장은 접촉역학/입도분포 지식이
갖춰지는 Tier2로 유보.

### tier1_empirical/process_time.py — 공정시간(time) 적분 v0 (2026-09-04)
근거 지식: `knowledge/cmp/preston-luo-dornfeld-mrr.md` (preston.py와 동일 근거,
새 물리 가정 없이 시간축만 추가)

**범위**: 시간(time) 축만 다룬다. 유량(flow rate)은 슬러리 물질전달/화학 지식이
아직 없어(knowledge/에 근거 노트 없음) 이번 범위에서 명시적으로 제외 —
유량은 슬러리 화학 지식 축적 후 별도 구현.

제공 API
- `removed_thickness(rs, mrr, t_sec)` → 반경별 제거두께 [m] = mrr(r) × t
  (Preston MRR이 정상상태에서 일정하다는 가정 하의 단순 시간적분, 새 물리 없음)
- `endpoint_time(target_thickness_m, mrr_at_ref)` → 목표두께 도달까지 걸리는 시간 [s]
  (mrr_at_ref는 보통 `preston.wafer_avg_mrr`의 웨이퍼 평균 MRR — 어떤 MRR을
  기준으로 할지는 호출부가 결정)
- `wiwnu_percent(arr)` → (max-min)/mean × 100 (demo_app.py에 인라인이던 계산을
  재사용 가능한 함수로 승격, 로직 변경 없음)
- `preston.py`, `kinematics.py`는 수정 없이 import만 함

**self-test 결과 (2026-09-04 실행, 4/4 PASS)**
| 검증 | 결과 |
|---|---|
| removed_thickness가 t에 정확히 비례 (120s = 60s의 2배) | max\|ratio-2\|=0.00e+00 ✔ |
| MRR 2배 → endpoint_time 정확히 1/2 | ratio=0.500000000 ✔ |
| Rs=1(균일압력) → WIWNU ~ 0% | WIWNU=0.00e+00% ✔ |
| Rs=50/60 → WIWNU 오더 확인(하드코딩 assert 없이 출력만) | WIWNU=0.3905% (kinematics.py/preston.py의 edge/center 1.00391과 정합하는 0.4% 근방) ✔ |

demo_app.py 사이드바에 "목표 제거두께(nm)" 슬라이더가 추가되어, 웨이퍼 평균 MRR
기준 목표두께 도달 예상시간과 반경별 제거두께 프로파일을 함께 표시한다.

### demo_app.py — Streamlit 데모 UI v0 (2026-09-04)
`kinematics.py`, `preston.py`를 그대로 불러 쓰는 Streamlit 데모. 코드 수정 없음, import만.

제공 기능
- 사이드바 슬라이더: 웨이퍼 반경 R_w(mm), r_cc(mm), RPM(웨이퍼/패드), 압력 P(kPa), Kp(m^2/N)
- "존압력" 체크박스: 켜면 R_w를 3등분한 center/mid/edge 구간별 압력을 각각 슬라이더로 입력받아
  `pressure_fn`으로 `mrr_profile`에 전달 (꺼져있으면 균일압력 스칼라 사용)
- 메인 화면: 반경별 MRR 프로파일 플롯(nm/min), 웨이퍼 면적가중 평균 MRR(`wafer_avg_mrr`),
  kinematic number µ 및 운동학 비균일도 2|µ|%, 프로파일 기준 WIWNU(%)
- 상단 고정 안내문: "Tier1 경험식(Preston), 균일/존압력 가정, 문헌 재현 검증된 v0 모델 —
  실제 공정 예측 정밀도 보증 아님"

실행: `source .venv/bin/activate && streamlit run sim/demo_app.py`

**검증 (2026-09-04)**: `streamlit run --server.headless true --server.port 8511`로 기동 후
`curl http://localhost:8511` → 200 OK, Streamlit 앱 HTML 정상 응답. `/_stcore/health` → `ok`
(임포트/런타임 예외 없이 스크립트 정상 실행 확인). 이후 프로세스 종료.

### tier2_physics/gw_contact.py — Hertz + Greenwood-Williamson 접촉모델 v0 (2026-09-04)
근거 지식: `knowledge/materials/hertz-gw-contact-mechanics.md`

제공 API
- `hertz_force(delta, E_star, R)` → 단일 asperity Hertz 힘 (F ∝ delta^1.5)
- `hertz_contact_area(delta, R)` → 단일 asperity 접촉면적
- `gw_numeric(d, beta, eta, A_n, E_star, R)` → 지수분포 GW 모델 수치적분(접촉개수·실접촉면적·하중)
- `gw_analytic_ratio(beta, E_star, R)` → A_r/W 폐형식(분리거리 d에 무관)
- `plasticity_index(E_star, H, sigma_z, R)` → 소성지수 psi (탄성/소성 판별 참고용, 미검증 임계값)

**self-test 결과 (2026-09-04 실행, 5/5 PASS)**
| 검증 | 결과 |
|---|---|
| Hertz F~delta^1.5 스케일링 (2배 압입) | 2.828427 = 2^1.5 (오차 <1e-9) ✔ |
| Hertz a²=R·delta 일관성 | 정확히 일치 ✔ |
| GW 지수분포 A_r/W 비율이 d(분리거리)와 무관 | d=0/0.2/0.5µm에서 max_dev=8.6e-6 ✔ |
| A_r vs W 선형회귀 기울기 = 폐형식 값 | slope=7.236e-9 vs analytic=7.236e-9 ✔ |
| 소성지수 psi 오더 확인 | psi≈4.9 (참고용, 정밀 임계값 미검증) ✔ |

핵심 시사점: 지수분포 가정 하에서 실접촉면적은 명목압력(분리거리 d)과 무관하게 항상 하중에
선형 비례한다 — Amontons 마찰법칙의 미시적 근거이자, Preston K_p 내부에 숨은 "명목압력→실접촉
압력" 변환의 기초. 아직 preston.py와 미연결(Lv2-2에서 K_p 물리적 분해 예정).

### tier2_physics/gw_pressure_solve.py — GW 힘평형 역문제(명목압력→분리거리) (2026-09-04)
근거 지식: `knowledge/materials/gw-nominal-vs-local-pressure.md`

제공 API
- `solve_separation(P_nominal, A_n, beta, eta, E_star, R, d_bracket=None)` → 명목압력을 만족하는 분리거리 d (Brent법)
- `local_contact_state(P_nominal, ...)` → d, 접촉점수 n, 실접촉면적 A_r, 하중 W, 평균 실접촉압력 p_r_mean 반환

**self-test 결과 (2026-09-04 실행, 5/5 PASS)**: 14→96kPa(6.9배) 압력변화에도 평균 실접촉압력
p_r=W/A_r이 <0.1%(2.16e-16) 편차로 사실상 불변, 접촉점수 n은 W에 거의 정확히 비례(1.78e-15).
아직 preston.py와 미연결.

### tier2_physics/pad_wear_glazing.py — 패드 마모(glazing) → MRR 시간 드리프트 v0 (2026-09-04)
근거 지식: `knowledge/materials/pad-wear-glazing-mrr-decay.md` (1차 출처: Shi & Ring, *Wear* 2010,
저자 공개 PDF https://my.che.utah.edu/~ring/Publications-PDFs/J-135.pdf)

gw_contact.py의 hertz_force/hertz_contact_area를 재사용, Shi&Ring의 Borucki 극한(유체 없음)을
Monte-Carlo asperity 집단(지수분포 표본)으로 이산 근사 — Archard 마모법칙(dz/dt ∝ sqrt(z-d))을
오일러 시간적분해 asperity 분포를 마모시키고 매 스텝 하중평형(d 재계산)·MRR을 기록한다.

제공 API
- `sample_heights(n, beta, rng)` → 지수분포 asperity 높이 표본
- `total_load_discrete/total_area_discrete(heights, d, ...)` → 이산 집단의 총 하중/실접촉면적
- `solve_separation_discrete(heights, W_target, ...)` → 이산 하중평형 분리거리 (gw_pressure_solve.py의 이산판)
- `wear_step_borucki(heights, d, C1, dt)` → 1스텝 Archard 마모 적분
- `simulate_pad_wear(...)` → 전체 시계열(t, MRR, p_r, mean_height, d) 시뮬레이션

**self-test 결과 (2026-09-04 실행, 5/5 PASS)**
| 검증 | 결과 |
|---|---|
| 무컨디셔닝 시 평균 asperity 높이 단조 비증가 | 2.9915e-07m → 2.9473e-07m (glazing) ✔ |
| MRR(t) 단조 감소 | 30스텝 2.66% 감쇠 ✔ |
| 감쇠 수확체감(초반>후반) | 초반1/3=1.24e-2, 후반1/3=1.18e-2 ✔ |
| 이산 t=0 vs 연속 gw_numeric() 교차검증 | rel_err=1.18% (Monte-Carlo 오차 범위) ✔ |
| 마모 시 p_r 변화(정적압력변화 시 불변과 대비) | 2.66% 변화 (Lv2-2 <0.1%와 대비) ✔ |

핵심 시사점: Preston의 K_p는 "패드 컨디셔닝 직후 상태"에서만 상수로 근사되며, 무컨디셔닝
구간에서는 패드 마모(=asperity 분포 변형)에 따라 시간의존적으로 변한다. 유체결합(Reynolds)·
컨디셔너 B/D항·preston.py 정식 연결은 Lv3-2 범위로 유보.

## sim/tier2_physics/gw_preston_link.py — GW 접촉모델 ↔ Preston Kp 정식 연결 (Lv3-2, pad-mechanic 최종단원)

근거 지식: `knowledge/materials/gw-nominal-vs-local-pressure.md` §2(n_contacts(P)의 P-선형성),
`sim/tier1_empirical/preston.py`(문헌 Kp=1e-13, STI MRR 254.05 nm/min 캘리브레이션 앵커).

Preston의 현상론적 MRR=Kp·P·V를 GW 미시모델로 재해석: MRR = alpha_removal · n_contacts(P) · V.
n_contacts(P)의 완전선형성(Lv2-2/이 모듈에서 재확인, 잔차 2.46e-13) 덕분에 이 대안식은 Preston의
P-선형성을 접촉점 개수 증가라는 물리적 그림으로 설명한다. alpha_removal(화학종속 lump 상수, GW로는
예측 불가 — slurry-chemist 영역)은 문헌 Kp를 앵커로 역산.

제공 API
- `n_contacts_at(P_pa)` → GW 접촉점수 (gw_pressure_solve.local_contact_state 래퍼)
- `linear_fit_slope(P_list, n_list)` → n(P) 최소자승 기울기(dn/dP)
- `mrr_gw_link(P, V, alpha_removal)` / `mrr_preston_direct(P, V, kp)` → 두 모델 각각의 MRR
- `calibrate_alpha_removal(P_ref, V_ref, kp_lit)` → 문헌 Kp에서 alpha_removal 역산

**self-test 결과 (2026-09-04 실행, 4/4 PASS)**
| 검증 | 결과 |
|---|---|
| n_contacts(P) 선형적합 잔차 | 2.458e-13 (사실상 완전선형) ✔ |
| 캘리브레이션점 GW-link == Preston-direct | 항등 확인 (99.36 vs 99.36 nm/min) ✔ |
| 캘리브레이션 MRR 문헌범위(50-1000 nm/min) 안 | 99.4 nm/min ✔ |
| 14/48/96kPa 외삽 GW-link vs Preston-direct 편차 | max_dev=4.6e-12 ✔ |

핵심 결론: alpha_removal 역산 시 Kp_physical(=alpha_removal·dn/dP)이 문헌 Kp=1e-13과 정확히
일치(항등식 검증, 독립예측 아님을 명시) — **Phase 0 "패드: GW 접촉모델" 항목 완전 완료**
(순방향 gw_contact → 역문제 gw_pressure_solve → 마모시계열 pad_wear_glazing → Preston 정식연결
gw_preston_link, 4개 모듈 체인). pad-mechanic 커리큘럼(CURRICULUM.md) 전 단원 이수 완료.

### tier1_empirical/wiwnu_pattern_combined.py — WIWNU(반경) × 패턴밀도(다이) 결합 브리지 (2026-09-05)

`wiwnu.py`(반경별 blanket MRR K(r))와 `pattern_density.py`(RR_up(x)=K/rho_eff(x), K는 종전엔
상수 가정)를 잇는 신규 파일 — 두 기존 모듈은 무수정(import만). K 자리에 K(r)을 대입해
RR(r,x) = K(r)/rho_eff(x) 2차원(반경×다이내부) 결합 제거율 맵을 만든다. r과 x는 분리가능
(separable)하다는 1차 근사이며 반경-패턴 교차항은 다루지 않는다(파일 상단 docstring 참조).

**self-test 결과 (2026-09-05 실행, 5/5 PASS)** — 극한 a) rho_eff≡1 → wiwnu.py 단독 K(r)과
bit-level 일치, 극한 b) p_uniform+Rs=1(K(r) 상수) → pattern_density.oxide_removed_up 기반
RR_up(x)와 일치, 결합효과 c) sigma_pct(CV)가 대수적 하한 max(반경단독, 패턴단독)을 만족
(분리가능 곱구조이므로 자명). half_range_pct(max-min 기반)는 이 하한이 대수적으로 보장되지
않는 지표라 assert 대상에서 제외하고 정보로만 기록 — 이번 합성 파라미터에서는 실측으로도
하한이 성립했음을 확인.

### integration/spatiotemporal_removal.py — 시공간 결합 제거량 필드 조립 레이어 (2026-09-05)

process-integrator Lv3-2(커리큘럼 최종 단원, "통합 시뮬레이터 아키텍처 설계·조립")의
산출물. Luo & Dornfeld(2003) 리뷰의 핵심 통찰(Preston식이 입자/다이/웨이퍼 3-스케일을
잇는 "인터페이스")을 근거로, `wiwnu_pattern_combined.py`의 정상상태 RR(r,x) 맵에
`process_time.py`의 선형 시간적분 로직을 그대로 적용해 thickness(r,x,t) 시공간 필드를
만든다. 새 물리가정 없음 — 기존 두 모듈을 조립만 함(신규 sim/integration/ 서브패키지,
기존 5개 tier1/tier2 파일 무수정).

**self-test 결과 (2026-09-05 실행, 4/4 PASS)**
| 검증 | 결과 |
|---|---|
| thickness_field가 t에 정확히 비례(120s=2×60s) | max\|ratio-2\|=0.00e+00 ✔ |
| 극한 rho_eff≡1 → K(r)·t와 bit-level 일치 | max_abs_diff=0.00e+00 ✔ |
| endpoint_time 배선 == 직접 나눗셈 | direct=9.6108s, via=9.6108s ✔ |
| 다이-스케일 CV가 시간에 불변(RR·t 선형배율 상쇄) | CV(60s)=CV(120s)=6.6734% ✔ |

지식노트 `knowledge/cmp/luo-dornfeld-integrated-cmp-framework.md`에서 확정한 설계
결정: GW 접촉모델(gw_preston_link.py)의 Kp 물리적 분해와의 연결은 이번 단원 스코프
밖(Kp가 함수형이 되려면 기존 상수-kp self-test들의 회귀 위험 있음) — Lv4로 명시적 유보.

### tier2_physics/conditioner_pcr_decay.py — 컨디셔너 PCR 노화(aging) 모델 (2026-09-05)

disk-conditioner Lv2-1(디스크-패드 절삭 모델) 산출물. 지식노트
`knowledge/equipment/conditioner-disk-pad-cutting-model.md` 근거: Entegris(2013) 백서의
실측 앵커("50시간 사용 디스크의 PCR이 초기값의 16%로 지수적 하락") — 이를
`PCR(t)=PCR0*exp(-t/tau)`로 캘리브레이션(tau≈27.28h). `pad_wear_glazing.py`를 무수정
재사용(import만)해, 컨디셔너가 노화될수록 재생력이 약해지는 결합 마모 ODE
(`simulate_conditioned_wear`)를 추가 구현. 재생항(sqrt(z0-z) 함수형)은 문헌에서 직접
가져온 식이 아니라 fab-sim의 최소 확장 가정 — self-test는 정성적 방향(순위)만 검증하고
정량값은 미보증으로 명시.

**self-test 결과 (5/5 PASS)**
| 검증 | 결과 |
|---|---|
| 캘리브레이션 tau로 앵커(50h→16%) 정확 재현 | PCR(50h)/PCR0=0.160000 ✔ |
| tau→inf 극한에서 PCR(t)=PCR0 상수(Planargem 안정성 극한) | PCR(1000h)/PCR0=1.0 ✔ |
| PCR(t) 단조 비증가 | PCR(0)=1.0→PCR(100h)=0.0256 ✔ |
| 노화 컨디셔너 하 평균 asperity 높이가 이상적 컨디셔너보다 더 많이 감소 | h_aging<h_ideal ✔ |
| 컨디셔닝 부재<노화<이상적 3단계 순위 | h_none<h_aging<h_ideal ✔ |

### tests/ — pytest 회귀 하네스
`source .venv/bin/activate && python -m pytest tests/ -v` — 신규 test_conditioner_pcr_decay.py
(6건) 포함 전체 **62개 PASS** (2026-09-05 기준).

### tier2_physics/slurry_film_lubrication.py — 슬러리 필름두께 스케일링 (2026-09-05)
근거 지식: `knowledge/physics/cmp-slurry-flow-lubrication-film-thickness.md`
(Thakurta et al. 2001, 3-D Reynolds 윤활방정식, 미러 사이트 경유 원문 확보)

전체 2-D 비선형 Reynolds PDE(뉴턴법 수치해)는 미이식 — 대신 z0 무차원 길이스케일(Eq.19)과
h_min의 파라미터 의존 방향(압력·속도·점도·다공성·압축성·곡률·웨이퍼자전) 8개 정성 부호를
최소 스케일링 함수로 재현.

**self-test 결과 (10/10 PASS)**
| 검증 | 결과 |
|---|---|
| z0 오더가 논문 h_min(36µm)과 같은 오더 | z0≈232µm ✔ |
| P_app↑→z0↓, 패드속도↑→z0↑ | 방향 일치 ✔ |
| h_min_scaling: P_app↑↓, U↑↑, μ↑↑ | 방향 모두 일치 ✔ |
| 패드 다공성·압축성↑ → h_min↓ | 방향 일치 ✔ |
| 웨이퍼 자전↑(패드 고정) → h_min↓ (반직관 방향) | 방향 일치 ✔ |
| 웨이퍼 곡률(d0) → h_min 내부 극댓값 존재(비단조) | imax=2/5(중간값) ✔ |

pytest 회귀: `tests/test_slurry_film_lubrication.py` 신규 7건, 전체 **90/90 PASS**.
