<!-- V2-SECTION: R1-equipment | 근거: tool-log, calibration, zone-response, thermal | 정본: ORG.md §7.3 -->
# Cal-1 — 툴 로그(존압력·RPM·유량·온도 시계열) 파싱·정렬 규칙 + 존 응답 행렬 보정

> 에이전트: tool-platen-head Cal-1 (캘리브레이션 단원, ORG.md §7.3) | 작성일: 2026-09-19
> [[cmp-multizone-carrier-radial-response]] [[tool-settings-to-pressure-velocity-field-model-spec]]
> [[cmp-theta-platen-coolant-temperature-driver]] [[../physics/frictional-heating-temperature-arrhenius-coupling]]
> [[cmp-rpm-ratio-flowrate-temperature-mrr-stability]] [[../data/cmp-measurement-ingest-schema-standardization]]

## 0. 목적·범위·형제 경계

ORG.md §7.3은 tool-platen-head에게 **"툴 로그(존압력·RPM·유량·온도 시계열) 소유 + 존 응답
행렬 보정"**을 맡겼다. 이 노트는 그 산출물이다. 존압력→p(r) 응답행렬 M 자체(기하 순수함수)는
이미 [[tool-settings-to-pressure-velocity-field-model-spec]]에서 명세했다 — **재서술하지
않고 인용만** 한다. 이 단원이 새로 하는 일은 (1) 그 M을 **실제 시계열 로그로 보정**할 때
필요한 필드·정렬 규칙, (2) 담당 축 중 하나인 **온도 시계열**이 흘러들어가는 유일한 소비처
`_f_theta`(Θ)의 앵커 상수 `platen_hot_side_ref_c`(36.0 °C, estimated)를 1차 문헌으로
대조하는 것이다.

**형제 경계(침범 금지, 인용만):**
- Θ 열저항 네트워크·3분배 물리 모델 자체는 **tribologist 소관**
  ([[../physics/frictional-heating-temperature-arrhenius-coupling]] §8) — 이 노트는 그 결과를
  **다른 툴·다른 막질의 독립 문헌으로 교차검증**하는 데이터 출처 역할만 한다.
- `sim/factors.py::_f_theta`·`sim/tier2_physics/cmp_theta_steady_state_heat_balance.py`
  **직접 수정 금지**(software 소관). §7 구현요청으로만 제안한다.
- 통합 로그 스키마 **파일**은 cmp-data-engineer 소관 — 이 노트는 §5 표로 필드 요구만 제안한다.
- **고객·재직사 데이터 절대 미사용**(ORG.md §7.5). 이 노트의 정렬 규칙은 공개 문헌의 시간상수·
  범위값으로 설계했고, 검증은 합성 시계열로 한다.

## 1. 로그 필드의 1차 근거

| 필드 | 정의·범위 근거(1차) |
|---|---|
| `zone_pressure_psi[3+ring]` | Lee, Lee, Jeong(2026, JKSPE 43(5) 443-448, 원문 확보, [[cmp-multizone-carrier-radial-response]])의 3존+리테이너링 구성. 존별 독립 채널, Zone3(0-85mm)는 나머지와 블록대각 분리 |
| `rpm_platen`·`rpm_head` | Kim & Jeong(2004, DOI 10.1007/s11664-004-0294-4, 원문 확보, [[cmp-rpm-ratio-flowrate-temperature-mrr-stability]]) kinematic number ζ 정의가 두 회전축을 요구 |
| `sfr_ml_min`(슬러리 유량) | Yuh et al.(2015, DOI 10.1007/s40684-015-0041-8, 원문 확보) 600-1200 mL/min 스윕 실험 설계 |
| `platen_coolant_temp_c`(냉각수 설정온도) | Shin et al.(2025, *Materials* 18(19):4461, DOI 10.3390/ma18194461, PMC12525981, 오픈액세스 원문 확인) 보텍스튜브 1/2단 30→27.5→26.5 °C |
| `pad_interface_temp_c`(계면/패드온도 실측, IR) | Shin 2025 Fig.7a(IR 센서, 5 Hz 급 실시간); Rosales-Yeomans et al.(2006, *J. Electrochem. Soc.* 153(4) G272-G277, DOI 10.1149/1.2168392, 원문 확보 — 아래 §4) 5점 IR 카메라 5 Hz |

Shin(2025)·Rosales-Yeomans(2006) 모두 **온도를 시계열로 로깅**한다(단일 종점값이 아니다) —
그래서 이 축은 압력·RPM·유량과 마찬가지로 "시계열 파싱·정렬"의 대상이지 스칼라 상수가 아니다.
§4가 정확히 이 사실("상수로 박은 `platen_hot_side_ref_c`가 온당한가")을 검사한다.

## 2. 파싱·정렬 규칙 — 다중 채널·다중 샘플레이트

실제 툴 로그는 채널마다 샘플레이트가 다르다(압력·RPM은 통상 수십 Hz 제어루프, 유량은
초 단위, 온도는 IR 5 Hz~열화상 카메라 프레임레이트). 정렬 규칙 셋:

1. **공통 시간축 리샘플**: 가장 느린 채널(대개 유량 또는 SCADA 로그, ~1 Hz)로 다운샘플하거나,
   압력/RPM처럼 빠른 채널은 그 구간의 평균·표준편차를 함께 보존한다(순간값 하나만 남기면
   [[cmp-multizone-carrier-radial-response]]의 "순간 속도 vs 시간평균 슬라이딩거리"처럼 1차 대
   2차 민감도가 다른 물리량을 뭉갠다 — [[cmp-rpm-ratio-flowrate-temperature-mrr-stability]] Q2
   재인용).
2. **정상상태 창(steady-state window) 추출 규칙**: 캘리브레이션에 쓸 값(zone별 유효 압력, 정상상태
   온도 등)은 런 **시작 구간(과도상태)을 버리고 마지막 구간만** 평균한다. 버릴 길이는 열
   시정수로 정한다 — White et al.(2003, DOI 10.1149/1.1560642, 원문 확보,
   [[../physics/frictional-heating-temperature-arrhenius-coupling]] §8.4)의 시정수 τ=19-74 s와
   Shin(2025)의 90 s에서 92-99 % 정상상태 도달 관측을 근거로, **"런 길이가 90 s 이상이면 마지막
   3τ(최소 60 s, 데이터 없으면 마지막 1/3) 구간만 정상상태로 채택"**을 규칙으로 둔다. 짧은 런
   (<90 s)은 "정상상태 미도달"로 표시하고 캘리브레이션에서 제외한다(Shin 자신의 90 s 데이터도
   완전 평형이 아니라 92-99 %임을 §3에서 재확인).
3. **레시피 경계 정렬**: `recipe_id`·`run_index`로 런을 자르고, 존압력 스텝테스트(§3)는 스텝
   변경 시각을 로그의 setpoint 채널(실제 압력이 아니라 명령값)에서 찾아 그 이후 정상상태
   창까지를 "그 스텝의 응답 구간"으로 정의한다.

## 3. 존 응답 행렬 M의 실측 보정 — 스텝테스트 역산과 식별성 한계

[[tool-settings-to-pressure-velocity-field-model-spec]] §2의 M은 **기하(존 멤버십)로만
구성한 순수함수**이고 압력값에 의존하지 않는다(partition-of-unity, 행합=1). 실제 로그로
"보정"한다는 것은 M 자체(기하)가 아니라 **M이 만드는 p(r) 예측을 반경별 실측 제거율과
맞추는 것**이다 — Preston 국소선형(RR(r)=Kp·p(r)·V(r))을 가정하면 제거율 실측에서 p(r)을
역산할 수 있다. 절차:

1. 각 스텝(§2 규칙3)의 정상상태 구간에서 zone_pressure 벡터 P_i와 반경별 실측 RR(r_j)를 쌍으로
   모은다.
2. RR(r_j)/[Kp·V(r_j)]로 p(r_j)를 역산(Kp는 [[../slurry/...]] 등 형제 축에서 옴, 이 노트는
   압력 축만 담당).
3. p(r_j) ≈ Σ_i M[j,i]·P_i 를 최소자승으로 풀어 M을 **재추정**하고, 명세식 M(smoothstep,
   w=12.5 mm)과 비교한다.

**식별성 한계(정직 표기)**: [[cmp-multizone-carrier-radial-response]] Q1이 이미 지적했듯
Zone3는 독립이지만 {Zone1, Zone2, Ring}은 결합 블록이다. 즉 이 세 압력을 **동시에** 바꾸는
스텝테스트로는 블록 내부의 개별 기여를 분리하지 못한다 — 스텝테스트 설계 규칙은 "블록 내
압력은 한 번에 하나씩만 바꾼다(one-factor-at-a-time)"여야 하며, 동시변경 로그만 있으면 M의
그 블록은 **재추정 불가**(명세값을 그대로 쓰되 "실측 미보정" 표시)로 처리한다. §6 python
verify에서 이 최소자승 절차와 식별성 조건(설계행렬의 랭크)을 합성 데이터로 확인한다.

## 4. `platen_hot_side_ref_c`(36.0 °C, estimated) 대조 — [[cmp-theta-platen-coolant-temperature-driver]] 1차 재검토

### 4.1 현재 값의 1차 출처 재확인
`knowledge/params/base.yaml`의 값(36.0 °C)과 노트
[[cmp-theta-platen-coolant-temperature-driver]]는 Shin et al.(2025, *Materials* 18(19):4461,
DOI 10.3390/ma18194461, PMC12525981, CC BY, 오픈액세스 전문 확인)의 **"미제어 90 s 후 패드
계면온도 ≈36 °C"** 단일 실측을 전 팩 공통 앵커로 쓴다. 이 값 자체는 실존하는 1차 출처의
정확한 인용이다(할루시네이션 아님) — 문제는 "그 특정 장비·막질의 단일값을 전 팩에 공통 적용"
하는 **일반화**가 정당한가이다. 브리프가 요구한 대로, **다른 장비·다른 막질**의 정상상태
계면온도 실측을 아래에서 3건 추가로 모은다(White는 기존 노트가 이미 확보한 것을 재인용,
나머지 둘은 이번 조사에서 신규 확보).

### 4.2 신규 확보 문헌 A — Rosales-Yeomans et al. 2006 (ILD/산화막, 100·200 mm 트라이보미터)
Rosales-Yeomans, Borucki, Doi, Lujan, Philipossian, "Implications of Wafer-Size Scale-up on
Frictional, Thermal, and Kinetic Attributes of Interlayer Dielectric CMP Process," *J.
Electrochem. Soc.* **153**(4) G272-G277 (2006), DOI: 10.1149/1.2168392. 미러 사이트(sci.bban.top)
경유로 원문 PDF 전문 확보(6쪽, papers 미등록 상태 — §6 verify에서 로컬 경로 명시).
- **막질**: 열산화 blanket SiO₂(ILD, Shin 2025의 배리어와 다른 막질). **툴**: 실험실
  트라이보미터(100 mm·200 mm 두 스케일, 산업 툴 축소판 — Shin의 POLI-500 생산 툴과 다른 장비).
- IR 비디오카메라(범위 −40~2000 °C, 정확도 ±2 °C, 분해능 0.1 °C, 5 Hz)로 웨이퍼 리딩엣지
  5점의 **패드 표면온도**를 실시간 측정(원문 §Experimental).
- Fig. 7(원문 그림, fitz 렌더 판독 — 판독 불확도 ±0.5 °C 명시): 압력×속도(pV, W/m²) 4,000~
  25,500 범위에서 **200 mm 트라이보미터 패드온도 26.5→32.9 °C, 100 mm 트라이보미터 25.5→29.1 °C**로
  **단조 증가**. 즉 **같은 장비·같은 막질·같은 슬러리에서도 pV 조건만으로 절대 계면온도가
  ~6.4-7.5 °C 스윙**한다(원문 결론: "높은 pV의 200mm 툴에서 더 높은 평균 패드 리딩엣지온도가
  더 높은 제거율과 상관").

### 4.3 신규 확보 문헌 B — Hocheng, Huang, Chen 1999 (온도 상승량, 국립칭화대)
Hocheng, Huang, Chen, "Kinematic Analysis and Measurement of Temperature Rise on a Pad in
Chemical Mechanical Planarization," *J. Electrochem. Soc.* **146**(11) 4236-4239 (1999),
DOI: 10.1149/1.1392620. 미러 사이트(sci.bban.top) 경유 원문 PDF 전문 확보(4쪽).
- 대만 국립칭화대/ERSO-IITRI 실험실 CMP 장비(막질 비특정, 열화상 카메라로 실측), White(2003)·
  Shin(2025)와 또 다른 3번째 장비.
- Fig. 7(원문, fitz 렌더 판독): 웨이퍼 카운트 10th/90th/170th에서 **정규화 반경 0.1-0.2 부근
  온도 상승 피크 ≈3.3-3.5 °C**(절대온도 아니라 **상승량**), 반경이 커질수록 감소, 패드
  마모(카운트 증가)에 따라 피크가 3.5→2.6 °C로 감소.
- 이 값은 White(ΔT_ss 9.1-16 °C)·Shin(ΔT≈15 K)보다 **4-5배 작다** — 저자가 보고한 공정조건이
  더 낮은 압력·속도(구체 pV 수치는 원문에 없음, 정성적으로 "장비마다 발열조건이 다르면 ΔT가
  자릿수 안에서도 크게 갈린다"는 근거로만 쓴다).

### 4.4 정량 종합 — "공통 근사"는 부분적으로만 정당하다
| 문헌 | 장비 | 막질 | 절대/상대 | 값(°C) |
|---|---|---|---|---|
| Shin 2025(현재 앵커) | POLI-500(생산 툴) | 배리어(Ta 슬러리) | 절대 T_ss | ≈35.5(baseline≈20.5, ΔT≈15) |
| White 2003 | 구형 8 in 생산 툴 | Cu | ΔT_ss(실측) | 9.1(예측 10.95-16.12) |
| Rosales-Yeomans 2006(신규) | 200 mm 트라이보미터 | SiO₂(ILD) | 절대(pV 스윕) | 26.5-32.9 |
| Rosales-Yeomans 2006(신규) | 100 mm 트라이보미터 | SiO₂(ILD) | 절대(pV 스윕) | 25.5-29.1 |
| Hocheng 1999(신규) | 대만 실험실 툴 | 비특정 | ΔT(상승량) | 2.6-3.5 |

**정직한 판정**: 4개 독립 문헌·5개 장비-막질 조합의 절대/상대 계면온도가 모두 **상온(≈20-25 °C)
+ 수~수십 °C 상승**이라는 **자릿수**에는 들어맞는다 — "36 °C가 물리적으로 터무니없다"는
반증은 없다. 그러나 **같은 장비·같은 막질(Rosales-Yeomans)** 안에서도 pV 조건만으로 ~6-7.5 °C
스윙하고, ΔT 자체는 장비에 따라 **2.6 °C~16 °C로 6배 가까이** 벌어진다(Hocheng vs White/Shin).
따라서 "전 팩 공통 근사"는 **자릿수 수준에서는 방어 가능**하지만 **±1 °C 수준의 정밀도는
없다** — 특정 장비(POLI-500)·특정 막질(배리어)·특정 압력(2 psi)의 단일값을 "막질 무관 상수"로
쓰는 것은 근거 이상으로 정밀해 보이는 착시다. **confidence는 `estimated`를 유지해야 하고,
`literature`로 승격할 근거는 없다** — 오히려 이 조사는 승격 기각(반증) 쪽이다.

### 4.5 결정적 반전 — 이 상수는 현재 MRR 예측에 전혀 영향을 주지 않는다
`sim/factors.py`를 직접 읽으면(§6 verify로 코드 자체를 assert), Θ(`_f_theta`)는
`MRR_COUPLED = {"chi","psi","kappa","tau"}`에 **포함되지 않는다** — Θ는 진단 전용 팩터이고
`platen_hot_side_ref_c`를 소비하는 유일한 코드는 이 Θ뿐이다. 즉 **이 상수의 값이나 confidence
등급을 무엇으로 바꾸든 오늘 시점의 어떤 MRR 예측치도 달라지지 않는다.** `tools/accuracy_gaps.py`의
CONFIDENCE 게이트는 팩 파라미터의 confidence만 보고 MRR 배선 여부를 보지 않으므로(원문 §5
`gaps_unmodeled_and_confidence`), 이 파라미터가 랭킹 상위에 뜨는 것은 **"근거가 약하다"는
경고로는 유효**하지만 **"고치면 정확도가 오른다"는 뜻은 아니다** — 두 사실을 혼동하면 안 된다.

## 5. 로그 스키마 개정 제안 (파일 직접수정 금지 — cmp-data-engineer 인계)

| 필드(제안) | 근거 | 효과 |
|---|---|---|
| `pad_interface_temp_c_timeseries`(≥5 Hz, 런 전체) | §4 Shin/Rosales-Yeomans 모두 시계열 실측 | `platen_hot_side_ref_c`를 상수 대신 **런별 실측 정상상태값**으로 대체 가능 |
| `zone_pressure_psi_timeseries[]`(존별, setpoint+실측 분리) | §2 규칙3 스텝 경계 탐지 | M 실측 보정(§3)의 입력 |
| `pv_condition_w_m2`(압력×속도, 파생) | §4.2 Rosales-Yeomans pV-온도 단조관계 | Θ를 상수 앵커 대신 **pV 함수**로 바꿀 근거 데이터 |

## 6. Python 검증

```python verify
import sys, math
sys.path.insert(0, ".")
import numpy as np

# ═══ (A) §4.5 코드사실 확인 — theta가 MRR_COUPLED 밖에 있는지 소스에서 직접 assert ═══
from sim.factors import MRR_COUPLED, _f_theta
assert "theta" not in MRR_COUPLED, MRR_COUPLED
assert MRR_COUPLED == {"chi", "psi", "kappa", "tau"}, MRR_COUPLED
print(f"[A] MRR_COUPLED={sorted(MRR_COUPLED)} — 'theta' 없음 확인 "
      f"(platen_hot_side_ref_c는 오늘 시점 어떤 MRR도 못 바꾼다)")

# ═══ (B) §4.2 Rosales-Yeomans 2006 pV 조건 재현 — 원문 P,V 조합이 Fig.7 x축 범위(4000-25500 W/m2) 안인지 ═══
P_kpa = [13.7, 20.7, 27.5]          # 원문 §Experimental 3수준
V_ms  = [0.31, 0.62, 0.93]          # 원문 §Experimental 3수준
pv_grid = sorted(p*1000*v for p in P_kpa for v in V_ms)
assert abs(pv_grid[0] - 4247.0) < 50, pv_grid[0]      # 최소조합 13.7kPa*0.31m/s
assert abs(pv_grid[-1] - 25575.0) < 50, pv_grid[-1]   # 최대조합 27.5kPa*0.93m/s
assert 4000 <= pv_grid[0] and pv_grid[-1] <= 25600    # Fig.7 x축(4,000-25,500) 범위 재현
print(f"[B] pV 격자 {pv_grid[0]:.0f}~{pv_grid[-1]:.0f} W/m^2 — Fig.7 x축(4000-25500) 재현")

# ═══ (C) §4.2 Fig.7 판독값(fitz 렌더 육안판독, ±0.5C 불확도 명시) — 단조성·스윙폭 ═══
temp_200mm_lo, temp_200mm_hi = 26.5, 32.9   # 200mm 트라이보미터, pV 최소/최대
temp_100mm_lo, temp_100mm_hi = 25.5, 29.1   # 100mm 트라이보미터, pV 최소/최대
swing_200 = temp_200mm_hi - temp_200mm_lo
swing_100 = temp_100mm_hi - temp_100mm_lo
assert 6.0 < swing_200 < 7.0, swing_200      # ~6.4C
assert 3.0 < swing_100 < 4.0, swing_100      # ~3.6C
assert temp_200mm_hi > temp_100mm_hi and temp_200mm_lo > temp_100mm_lo  # 200mm이 전체적으로 더 뜨거움(원문 결론)
print(f"[C] 같은 장비·같은 막질에서도 pV만으로 200mm {swing_200:.1f}C / 100mm {swing_100:.1f}C 스윙 "
      f"— '전 팩 공통 상수' 가정이 흡수 못하는 변동폭")

# ═══ (D) §4.3 Hocheng 1999 vs White 2003 vs Shin 2025 — DeltaT 자릿수 비교(장비간 최대 6배 차) ═══
dT_hocheng = 3.3     # Fig.7 원문 판독, 10th wafer 피크
dT_white   = 9.1     # White 2003 실측(Cu, frictional-heating 노트 §8.3 재인용)
dT_shin    = 15.0    # Shin 2025 실측 근사(frictional-heating 노트 §8.4 ΔT_meas≈15K)
ratio_max_min = dT_shin / dT_hocheng
assert 4.0 < ratio_max_min < 5.0, ratio_max_min    # ~4.5배
assert dT_hocheng < dT_white < dT_shin             # 세 장비가 자릿수는 같되 단조 증가하지 않음(장비종속)
print(f"[D] DeltaT 장비간 비교: Hocheng {dT_hocheng}C < White {dT_white}C < Shin {dT_shin}C "
      f"(최대/최소={ratio_max_min:.1f}배) — 자릿수(수~십수 C)는 공통, 절대값은 장비종속")

# ═══ (E) §4.5 실제 소비 코드(_f_theta 내부 cool_temp 식, sim/factors.py L350-359 그대로 이식)에
#          T_hot을 문헌값으로 바꿔 대입 — 얼마나 민감한가 ═══
def cool_temp(T_coolant, T_hot, T_ref):
    """sim/factors.py::_f_theta 의 cool_temp 계산부와 동일 로직(가드 포함)."""
    T_coolant_clip = min(T_coolant, T_hot - 0.5)
    driving_ref = T_hot - T_ref
    driving_now = T_hot - T_coolant_clip
    if driving_ref > 0:
        return driving_now / driving_ref
    return 1.0   # 실제 코드의 폴백값(냉각수온도항 무효화)

T_ref, T_coolant = 30.0, 26.5   # 팩 기본값(Shin 균형점) / Shin 2단 보텍스튜브 냉각값
ct_36 = cool_temp(T_coolant, 36.0, T_ref)     # 현재 팩 값(Shin, 배리어)
ct_33 = cool_temp(T_coolant, 32.9, T_ref)     # Rosales-Yeomans 200mm 산화막, pV 최대값
pct_diff = (ct_33 - ct_36) / ct_36 * 100
assert abs(ct_36 - 1.5833) < 1e-3, ct_36
assert ct_33 > ct_36            # T_hot이 낮을수록(같은 냉각수온도 대비) 구동력 비율이 커짐
assert 30 < pct_diff < 45, pct_diff
print(f"[E] cool_temp(T_hot=36, 배리어)={ct_36:.3f} vs cool_temp(T_hot=32.9, 산화막 pV상단)={ct_33:.3f} "
      f"({pct_diff:+.1f}%) — Θ가 MRR_COUPLED에 있었다면 이만큼 실제로 달랐을 폭")

# ═══ (F) 구조적 취약점 — Rosales-Yeomans 100mm 트라이보미터(25.5-29.1°C)처럼 T_hot이
#          팩 기준 T_ref(30°C)보다 낮은 막질/조건이면 가드가 조용히 냉각항을 무효화(1.0)한다 ═══
ct_low = cool_temp(T_coolant, 29.0, T_ref)    # Rosales-Yeomans 100mm 상단값(<T_ref)
assert ct_low == 1.0, ct_low     # driving_ref=29-30=-1<=0 -> 가드 발동, 실측 냉각효과가 통째로 사라짐
print(f"[F] T_hot=29°C(<T_ref=30°C, Rosales-Yeomans 100mm 산화막 상단)를 넣으면 "
      f"cool_temp={ct_low} — 가드가 냉각수온도 항 전체를 조용히 1.0으로 무효화한다 "
      f"(에러가 아니라 침묵 폴백이라 눈에 안 띈다). 저발열 막질/조건에 이 앵커를 그대로 "
      f"쓰면 이런 구조적 함정이 있다는 뜻 — 상수를 막질별로 분리하거나 최소한 이 폴백을 "
      f"경고로 승격할 것을 §7에서 제안한다.")

print("ALL PASS — Cal-1 로그 정렬 규칙 + platen_hot_side_ref_c 대조 검증 통과")
```

## 7. 구현 요청 (software 부문 BACKLOG용 — 직접 구현 금지)

- **무엇을**: (1) `data/schema/tool_log.schema.json`(신규, cmp-data-engineer 소관)에 §5 표의
  3필드 추가. (2) `sim/factors.py::_f_theta`의 `platen_hot_side_ref_c` 처리에 §4.4 결론(자릿수만
  방어됨) 반영 — 값 자체는 그대로 두되(대체할 더 나은 단일값 근거 없음), confidence 승격 보류를
  코드 주석에 명시. (3) **가드 취약점(§6 (F))**: `driving_ref = T_hot - T_ref <= 0`이면
  냉각수온도 항이 **조용히** 1.0으로 폴백한다 — 저발열 막질/조건(Rosales-Yeomans 100mm 산화막
  상단 29°C처럼 T_hot이 팩 기준 T_ref=30°C보다 낮은 경우)에서 이 상수를 그대로 재사용하면
  냉각효과가 침묵 속에 사라진다. `f.notes`에 이 폴백 발동 시 경고를 추가할 것을 제안(현재는
  무발동). (4) **우선순위 재고 제안**: `tools/accuracy_gaps.py`의 CONFIDENCE 랭킹이
  MRR_COUPLED 배선 여부를 반영하지 않아(§4.5) 진단전용 팩터의 estimated 파라미터가 실제
  영향력 있는 파라미터와 같은 점수로 상위 랭크된다 — score 계산에 "MRR_COUPLED 소속 팩터가
  소비하는가" 가중치 추가를 제안(구현은 총괄/software 판단).
- **근거 노트**: 본 노트 §4.4-4.5, [[../physics/frictional-heating-temperature-arrhenius-coupling]] §8.
- **검증 문헌값**: Rosales-Yeomans 200mm pV스윙 6.4°C(26.5→32.9)·100mm 3.6°C(25.5→29.1);
  Hocheng ΔT피크 3.3-3.5°C; MRR_COUPLED={chi,psi,kappa,tau}(theta 미포함, 코드 assert 확인);
  cool_temp(T_hot=36)=1.583 vs cool_temp(T_hot=32.9)=2.171(+37.1%) vs cool_temp(T_hot=29)=1.0(가드 폴백).
- **유효범위**: 이 판정은 현재(2026-09-19) 엔진 배선 기준 — Θ가 향후 MRR_COUPLED에 편입되면
  §4.5 결론(영향 없음)은 무효화된다. 그때는 §4.4의 pV 종속성(Rosales-Yeomans)을 반영해 상수 대신
  함수로 재설계할 것을 권고.

## 8. 결론 (Cal-1 + 정확도 갭 답)

1. **로그 파싱·정렬**: 다중 샘플레이트 채널은 공통시간축 리샘플 + 정상상태 창(마지막 3τ, τ는
   White 19-74s·Shin 90s 관측 근거) 추출 규칙으로 정렬한다. 존 응답 행렬 M은 기하 자체가 아니라
   "M이 만드는 p(r) 예측 대 반경별 실측 RR"을 최소자승으로 맞추는 방식으로 실측 보정하되,
   {Zone1,Zone2,Ring} 블록은 one-factor-at-a-time 스텝테스트 없이는 식별 불가하다.
2. **`platen_hot_side_ref_c`=36°C 대조**: 1차 출처(Shin 2025)는 실재하고 정확히 인용됐다.
   신규 확보한 독립 문헌 2건(Rosales-Yeomans 2006, 산화막/트라이보미터; Hocheng 1999, 비특정
   막질/대만 실험실 툴)과 기존 White 2003(Cu, 구형 툴)을 더해 총 4문헌·5개 장비-막질 조합을
   비교한 결과, **자릿수(상온+수~십수°C 상승)는 공통이나 절대값·상승폭은 장비·막질·압력속도
   조건에 따라 최대 6배 벌어진다** — "전 팩 공통 근사"는 등급 승격 근거가 아니라 **정량적
   반증**에 더 가깝다. confidence는 `estimated`를 유지해야 한다.
3. **더 중요한 발견**: 코드를 직접 assert한 결과 `theta`는 `MRR_COUPLED`에 없다 — 이 상수는
   오늘 시점 **어떤 MRR 예측도 바꾸지 않는 진단 전용 값**이다. `accuracy_gaps.py`가 이를
   상위 랭크한 것은 confidence 등급만 보고 배선 여부를 안 보기 때문이며, 이 사실 자체가
   §7 구현요청의 핵심 제안이다.
