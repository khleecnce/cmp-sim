<!-- V2-SECTION: R4-disk | 분배완료 2026-09-08 | 근거: conditioner, pcr, sweep, 컨디셔너 | 정본: ARCHITECTURE-V2.md §3 -->
# 컨디셔너 스윕 운동학 — PCR(r) 반경 프로파일 예측 모델

> disk-conditioner Lv2-2. 컨디셔닝 압력·스윕·RPM 레시피가 패드 반경별 절삭률(PCR) 프로파일에
> 어떻게 매핑되는지, 그리고 그 프로파일이 패드 형상(균일도) 진화에 미치는 영향을 다룬다.

## 1. 출처
- **Zheng, Zhao & Lu (2023)**, "Prediction of Pad Wear Profile and Simulation of Its Influence on
  Wafer Polishing", *Micromachines* 14(9), 1683. 오픈액세스 PMC10536193
  (https://pmc.ncbi.nlm.nih.gov/articles/PMC10536193/). Tsinghua Univ. State Key Lab of Tribology.
  실측 검증 포함(Hwatsing Co. 12인치 산업용 CMP 플랫폼 Universal-300-Plus, 레이저 공초점현미경
  OLS5100). — 본 노트의 1차 출처, 수식·표·실험조건 전부 이 논문에서 직접 인용.
- (2차 배경) [[conditioner-disk-pad-cutting-model]] — Lv2-1에서 확립한 Preston형
  PCR=k·P·v 관계 및 Entegris(2013) PCR 지수감쇠 앵커. 이번 단원은 그 "v(속도)" 항을
  운동학적으로 어떻게 계산하는지 구체화한다.
- (2차 배경) [[pad-structure-groove-subpad]] — McAllister(2019) 실측 세팅에서 sweep range,
  disk RPM 등 파라미터가 이미 등장했음(교차확인).

## 2. 핵심 운동학 모델 (Zheng et al. Eq.1–9)

좌표계: 패드에 고정된 직교좌표(패드 자체는 회전하지 않는 것으로 간주, 팔(arm)이 반대 방향으로
회전한다고 취급 — 상대운동 등가).

**팔 중심(arm center) 위치** (T=경과시간(s), n_p=패드 RPM, α0=초기각):
```
α(T)  = α0 - (2·n_p/60)·π·T
x_ac(T) = R_p·cos(α(T)),  y_ac(T) = R_p·sin(α(T))
```

**디스크 중심(disk center) 위치** — 사인파(sinusoidal) 스윕 모드, β_s=시작각, β0=초기각,
β_max=스윕범위, n_a=스윕 속도(RPM):
```
β(T) = β_s - (1/2)·β_max·cos( arccos(2(β0-β_s)/β_max) + (2·n_a/60)·π·T ) + (1/2)·β_max
x_dc(T) = x_ac(T) + R_a·cos(α(T)+β(T)),  y_dc(T) = y_ac(T) + R_a·sin(α(T)+β(T))
```

**개별 다이아몬드 입자 위치** (n_d=디스크 자전 RPM, θ_i0=입자 초기각, R_i=입자의 디스크
중심으로부터 반경):
```
θ_i(T) = θ_i0 + (2·n_d/60)·π·T
x_i(T) = x_dc(T) + R_i·cos(α(T)+β(T)+θ_i(T)),  y_i(T) = ... sin(...)
```

즉 4중 회전 합성(패드 자전 + 팔 스윕 + 디스크 자전 + 개별 입자의 디스크 반경위치)으로
각 다이아몬드의 절대 궤적을 시간의 함수로 완전히 결정할 수 있다.

## 3. PCR(반경) 프로파일 도출 — Preston형 연결

Zheng et al.은 [[conditioner-disk-pad-cutting-model]]과 동일한 Preston형 관계를 사용:
```
MRR = k·P·v         (연마)
PCR = k·P·v         (컨디셔닝, k·P는 다르지만 형태 동일)
PCA = k·P·∫v dt = k·P·s     (s = 스크래치 거리, PCA = pad cut amount)
```
핵심 통찰: **컨디셔닝 하중 P는 (일반적으로) 전체 스윕 반경에 걸쳐 균일하게 인가**되지만,
**속도 v(그리고 누적 스크래치 거리 s)는 반경 위치에 따라 균일하지 않다** — 팔이 스윕 사이클
동안 각 반경 구간에 머무르는 시간(dwell time)이 다르고, 상대속도 자체도 위치·시간에 따라
변하기 때문이다. 따라서:
```
PCR(r) ∝ s(r) = Σ_i (모든 다이아몬드 i가 반경 구간 r을 지난 궤적 길이의 합)
```
이를 얻기 위해 논문은 MATLAB으로 전체 궤적을 시뮬레이션 후 격자(square unit)별로 스크래치
거리를 합산했다 — 본질적으로 **몬테카를로/그리드 적산 방식**이다.

## 4. 실측 검증 (Table 1, 논문 실험조건 — 발췌)
| 파라미터 | 값 |
|---|---|
| 패드 회전속도 n_p | 100 RPM |
| 디스크 자전속도 n_d | 73 RPM |
| 디스크 하중 | 4 lbf (≈17.8 N) |
| 스윕 모드 | Sinusoidal |
| 스윕 속도 n_a | 19 RPM |
| 스윕 범위 | 반경 83~308 mm |
| 총 컨디셔닝 시간 | 8시간 |
| 평균 다이아몬드 피치/폭/돌출량 | 430/150/250 µm |

레이저 공초점현미경(OLS5100, 반복정밀도 <2µm)으로 그루브 깊이 프로파일을 측정, 시뮬레이션
PCR과 비교 → **"실험 결과가 시뮬레이션과 좋은 근사를 보여 운동학 모델의 유효성을 검증"**
(논문 원문). 추가로 중요한 발견: **PCR 결과는 패드의 기존 표면 프로파일과 거의 무관** —
즉 이 운동학 모델은 "1차 근사로 패드 형상과 독립적인 절삭 속도장"을 준다(마모가 진행돼도
같은 PCR(r) 프로파일을 재사용해도 된다는 근거, 최소한 그루브 깊이 규모에서는).

## 5. 실무적 함의 — 균일 마모를 위한 레시피 설계
- 스윕 범위·모드(사인파 vs 선형)를 조정하면 dwell-time 분포가 바뀌어 PCR(r) 프로파일 형상을
  제어할 수 있다 — 이것이 "컨디셔닝 레시피(압력·스윕·RPM) → 패드 프로파일 진화"의 핵심 레버.
- 실무에서는 스윕을 여러 구간(partition)으로 나누고 각 구간의 dwell 비율을 다항식/스플라인으로
  피팅하는 방식(논문 Table 2, 부분 확인 — 페이월/본문 뒷부분 미확보, "몇 개 구간으로 나눠
  dwell time 비율을 정하고 스플라인 함수로 피팅한다" 정도만 확인, 구체적 수치표는 미확보로
  **미검증** 표기)을 쓴다.
- 리테이닝 링(RR) 존재가 웨이퍼 엣지 프로파일을 개선하고, 패드 불균일이 응력 집중을 일으켜
  다중존 압력제어를 어렵게 한다는 부가 결론(논문 정적모델 파트, Section 5)도 있으나 이는
  Lv3(패드 수명 예측·최적화) 범위로 이번 노트에서는 요약만 하고 심화는 다음 단원으로 유보.

## 6. fab-sim 구현 방향 (다음 트랙B)
Zheng et al. Eq.1–9를 그대로 코드화하여 시간축 T에 대해 각 다이아몬드 위치를 계산하고,
반경 구간별로 dwell-time(또는 스크래치 거리)을 히스토그램 적산하면 PCR(r) 상대 프로파일을
얻을 수 있다. 이는 순수 기구학(질량·힘 없이 좌표 미적분)이므로 지식(본 노트)만으로 바로
구현 가능 — Lv2-2 지식과 Lv3-2(결합모델 구현) 사이의 다리 역할. [[conditioner-pcr-decay]]의
시간축 노화 모델과는 독립적 차원(공간 r 방향)이며, 두 모델을 곱하면
`PCR(r,t) = PCR_shape(r) · decay(t)` 형태의 2차원 결합이 가능하다(다음 구현 후보,
process-integrator의 [[luo-dornfeld-integrated-cmp-framework]] 3-스케일 아키텍처와도 정합).

## 6b. 정량 재현 — Zheng et al. Table 1 하중·운동학 수치 대조

Table 1의 "디스크 하중 4 lbf ≈ 17.8 N" 및 4중 회전 궤적 좌표식(Eq.1-3, §2)을 코드로 재현해
문헌 수치·기하 제약과 직접 대조한다.

```python verify
import numpy as np

# --- (a) 하중 단위 환산: 4 lbf -> N, 논문 본문 "≈17.8 N" 표기와 대조 ---
LBF_TO_N = 4.4482216153
load_lbf = 4.0
load_N = load_lbf * LBF_TO_N
assert abs(load_N - 17.8) < 0.05, f"4 lbf={load_N:.3f} N, 문헌 표기 17.8 N과 불일치"

# --- (b) 팔 중심(arm center) 궤적: 반경 R_p로 고정된 원운동이어야 한다 (Eq.1 기하 제약) ---
R_p = 0.30  # m, 임의 테스트 반경(패드 반경 스케일)
n_p = 100.0  # RPM (Table 1 실측값)
alpha0 = 0.3  # rad, 임의 초기각
T = np.linspace(0, 60.0 / n_p, 50)  # 정확히 1회전 구간 샘플
alpha = alpha0 - (2 * n_p / 60.0) * np.pi * T
x_ac = R_p * np.cos(alpha)
y_ac = R_p * np.sin(alpha)
r_ac = np.sqrt(x_ac**2 + y_ac**2)
assert np.allclose(r_ac, R_p, atol=1e-9), "팔 중심 궤적이 반경 R_p로 고정돼야 한다(원운동 제약)"

# 1회전 후 각도가 정확히 2π만큼 회전했는지(회전속도 n_p=100 RPM 정의 재현)
period_s = 60.0 / n_p
alpha_start = alpha0 - (2 * n_p / 60.0) * np.pi * 0.0
alpha_end = alpha0 - (2 * n_p / 60.0) * np.pi * period_s
assert abs((alpha_start - alpha_end) - 2 * np.pi) < 1e-9, "n_p=100 RPM이면 60/100초에 정확히 1회전(2π)해야 한다"

# --- (c) 스윕 범위(83~308 mm) 기하 일관성: 범위 폭과 중간값 확인 ---
sweep_min_mm, sweep_max_mm = 83.0, 308.0
sweep_range_mm = sweep_max_mm - sweep_min_mm
assert abs(sweep_range_mm - 225.0) < 1e-9, "Table 1 스윕 범위 83~308mm의 폭은 225mm"

# --- (d) PCR=k·P·v Preston형 선형성 재현: P 또는 v를 2배로 하면 PCR도 정확히 2배 (형태 검증) ---
k = 1.0
P, v = 17.8, 0.5  # 임의 단위(형태 검증 목적, 절대 물리단위 아님)
pcr_base = k * P * v
pcr_double_P = k * (2 * P) * v
pcr_double_v = k * P * (2 * v)
assert abs(pcr_double_P - 2 * pcr_base) < 1e-9
assert abs(pcr_double_v - 2 * pcr_base) < 1e-9
print(f"OK: 4lbf={load_N:.2f}N(문헌 17.8N), 팔궤적 반경오차<1e-9, 스윕범위={sweep_range_mm}mm, PCR 선형성 확인")
```

결과: (a) 4 lbf 환산값 17.79 N ≈ 문헌 "17.8 N" 일치. (b)(c) Table 1 수치(RPM·스윕범위)는 좌표
기하 제약을 정확히 만족 — 이는 트리비얼한 검증(하중·회전 정의 자체를 코드화한 것)이라
**PCR(r) 절대 프로파일 자체는 여전히 미검증**이다(§7 참조, MATLAB 몬테카를로 적산 결과의
숫자표는 원문 확보 실패). 이 verify 블록은 "본 노트가 인용한 실험 파라미터가 내적으로
일관적임"만 보증한다.

## 7. 한계/미검증
- Table 2 이후(스윕 파티션·스플라인 피팅 구체 수치)는 페이지 뒷부분 접근 제한으로 본문 발췌
  실패 — **미검증**, 구현 시엔 사인파 모드(Eq.4, 전체 확보)만 재현한다.
- 4중 회전 합성 궤적 적산은 계산량이 커서(다이아몬드 수 × 시간 스텝) fab-sim 구현에서는
  대표 소수 다이아몬드 또는 해석적 근사(균등분포 가정)로 단순화할 가능성 — 실제 구현 시
  self-test에서 명시.

## 관련 노트
[[conditioner-disk-pad-cutting-model]] · [[conditioner-grit-design-space]] ·
[[conditioning-mechanism-asperity-regeneration]] · [[pad-structure-groove-subpad]] ·
[[luo-dornfeld-integrated-cmp-framework]]
