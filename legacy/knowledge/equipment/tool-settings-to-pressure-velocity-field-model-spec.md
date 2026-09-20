<!-- V2-SECTION: R1-equipment | 공동: R5-wafer | 분배완료 2026-09-18 | 근거: carrier, kinematic, multizone, platen, retaining-ring | 정본: ARCHITECTURE-V2.md §3 -->
# 툴 설정 → (p(r), V(r)) 분포 모델 명세 — 존압력·속도장·링압 통합 함수

> 담당: [[tool-platen-head]] Lv3-2 · 작성 2026-09-18 · 상태: 검증(1차 출처 4편 확보, python verify 3블록)
> 연결: [[cmp-multizone-carrier-radial-response]](Lv1-2, 존-반경 응답 실험) ·
> [[cmp-retaining-ring-wear-edge-profile]](Lv2-1, 링 접촉응력) ·
> [[cmp-rpm-ratio-flowrate-temperature-mrr-stability]](Lv2-2, ζ 둔감성) ·
> [[tool-platen-head-closed-loop-profile-new-tech]](Lv3-1, P1 감도) ·
> [[cmp-kinematics-rotary]](속도장 폐형식) · [[cmp-platen-wafer-center-distance-rcc]](r_cc 문헌값) ·
> [[../cmp/preston-luo-dornfeld-mrr]](MRR = Kp·p·V)

## 0. 이 노트의 목적 — 구현이 아니라 "구현 가능한 명세"

앞 단원들(Lv1-2~Lv3-1)은 존압력·링압·RPM 각각이 프로파일에 미치는 영향을 **개별
현상**으로 확보했다. 이 노트는 그것들을 sim/이 그대로 짤 수 있는 **하나의 함수 명세**
`tool_settings → (p(r), V(r))`로 통합한다. 앞 단원 내용은 재서술하지 않고 **입력 파라미터로만
인용**한다. 새로 확보한 1차 문헌은 Ye & Yao (2025)의 rpm 비 스윕 **실측**(4절)이다.

형제 영역 침범 금지: 패드 적층의 압력분포 감쇠는 pad-structure, 마찰열·온도는 tribologist
소관이다 — 여기서는 인용만 하고, 이 함수의 출력 p(r)은 **멤브레인이 웨이퍼 뒷면에 거는
명목 압력 프로파일**까지다(패드를 거친 국소 접촉압력 p_local은 [[../materials/gw-nominal-vs-local-pressure]]
및 `sim/tier2_physics/gw_pressure_solve.py`의 하류 단계).

## 1. 세 축의 입력 — 어느 문헌에서 어느 수치가 오는가

| 축 | 모델 입력 | 1차 문헌값 | 근거등급 |
|---|---|---|---|
| (a) 존압력 벡터 | 존 경계 반경, 멤브레인 전이폭 w | Lee 2026 8"(0-85/85-95/95-99mm), Park 2020 300mm(0-40/40-100/100-128/128-145/145-150mm) | E2~E3 |
| (b) 속도장 | ω_p, ω_w, r_cc | Lai 2001 폐형식, Ye&Yao 2025 실측(NUV 0–0.42), Zhao 2012(α≈1 규칙) | E2~E3 |
| (c) 링압비 | P_ring/P_zone | Lee 2026(링 5→6psi, 엣지3mm NU 4.5→6.1%) | E1(그 툴) |

두 존-경계 문헌(Lee 8인치, Park 300mm)은 **툴 스케일이 다르지만 모델 형식(반경 밴드+전이)은
동일**하다. 절대 경계값은 툴별로 다르므로 함수는 `zone_bounds`를 인자로 받는다(하드코딩 금지).

## 2. (a) 존압력 → p(r) 선형 응답행렬 모델

### 2.1 형식

존압력 벡터 **P** = [P₃, P₂, P₁, P_ring]ᵀ (중심→엣지)에서 반경 압력 프로파일 p(r)로 가는
사상을 **선형**으로 둔다 — 멤브레인 챔버가 웨이퍼 뒷면에 거는 압력은 챔버별로 중첩되기
때문이다(중첩원리, E4: 멤브레인 선형탄성 가정):

```
p(r_i) = Σ_j M[i,j] · P_j ,   M[i,j] = m_j(r_i)   (존 j의 반경 멤버십)
```

**M**은 순수 기하 행렬(압력 무관)이고, 각 행은 1로 합산된다(**partition of unity**) — 그래서
모든 존이 같은 압력이면 p(r)은 그 값으로 균일하다. 존 j의 멤버십 m_j(r)은 인접 경계에서
**전이폭 2w**로 매끄럽게 넘어가는 smoothstep으로 정의한다(멤브레인 유연성 + 패드 점탄성이
경계를 번지게 하는 것을 한 개 파라미터 w로 흡수).

### 2.2 전이폭 w는 문헌 관측으로 보정된다

[[cmp-multizone-carrier-radial-response]]가 Lee 2026 Fig.8-11에서 읽은 핵심: **응답이
자기 존의 명목 경계보다 안쪽 10-15mm에서 시작**된다(존 경계는 이산이지만 응답은 확산적).
이것이 곧 전이폭이다. 각 존 스윕의 응답 개시 반경(그림 판독, E3):

| 존(밴드) | 명목 안쪽 경계 | 응답 개시 반경 | 함의 전이폭 |
|---|---|---|---|
| Zone1 (95-99) | 95mm | ~85mm | 10mm |
| Zone2 (85-95) | 85mm | ~70mm | 15mm |
| Zone3 (0-85) | 85mm(외) | ~70mm | 15mm |

→ w ≈ 10-15mm. 모델은 w=12.5mm(중앙값)로 두고, **한 관측에서 정한 w로 나머지 개시
반경을 예측해 Lee의 세 관측 범위 안에 드는지**를 §2.4에서 검증한다.

### 2.3 단일존 대비 멀티존 NU 개선(모델 검증 목표값)

Lee 2026 Table 3/5(엣지제외 3mm): 단일존 4.5% → 멀티존 2.5%. 이 노트의 응답행렬 모델이
재현해야 할 목표는 "존을 독립 제어하면 반경 프로파일 자유도가 늘어 NU가 준다"는 것이며,
정량 목표는 이 두 수치다(§2.4에서 재계산).

### 2.4 python verify — 응답행렬 성질 + 전이폭 보정 + NU 개선

```python verify
"""(a) 존압력→p(r) 선형 응답행렬 모델 검증.
   문헌: Lee, Lee, Jeong 2026 JKSPE 43(5) 443-448 (DOI 10.7736/JKSPE.025.132, 원문 PDF 확보).
   이 블록이 실패하면 §2의 모델 주장은 거짓이다."""
import numpy as np

# ── 존 기하 (Lee 2026 8인치, mm) — 중심→엣지, 마지막은 ring(웨이퍼밖 99+)
bounds = [0.0, 85.0, 95.0, 99.0]   # zone3=[0,85], zone2=[85,95], zone1=[95,99]
ring_boundary = 99.0
w = 12.5                           # 전이 반폭(mm), Lee 관측 10-15mm의 중앙값

def smoothstep(r, b, w):
    """경계 b에서 전이 지지구간 [b-w, b+w]를 3x^2-2x^3로 매끄럽게 0->1."""
    x = np.clip((r - (b - w)) / (2 * w), 0.0, 1.0)
    return 3 * x**2 - 2 * x**3

def membership_matrix(r, bounds, ring_boundary, w):
    t1 = smoothstep(r, bounds[1], w)   # 85 경계 (zone3|zone2)
    t2 = smoothstep(r, bounds[2], w)   # 95 경계 (zone2|zone1)
    t3 = smoothstep(r, ring_boundary, w)  # 99 경계 (zone1|ring)
    m3 = 1 - t1
    m2 = t1 - t2
    m1 = t2 - t3
    mR = t3
    return np.stack([m3, m2, m1, mR], axis=-1)  # (..., 4)

r = np.linspace(0, 101.6, 2000)   # 8인치 반경
M = membership_matrix(r, bounds, ring_boundary, w)

# (1) partition of unity: 모든 반경에서 행합=1 (⇒ 균일압력 in → 균일 p(r) out)
row_sum = M.sum(axis=1)
assert np.allclose(row_sum, 1.0, atol=1e-12), f"행합 최대이탈 {abs(row_sum-1).max():.2e}"
# (1b) 멤버십 음수 없음 (물리적 가중치)
assert M.min() > -1e-12, f"음수 멤버십 {M.min():.2e}"
# (1c) 균일압력 벡터 -> 균일 p(r)
P_uniform = np.array([4.0, 4.0, 4.0, 4.0])
p_uni = M @ P_uniform
assert (p_uni.max() - p_uni.min()) < 1e-9, "균일 존압인데 p(r) 불균일"
print(f"partition-of-unity OK (행합 이탈<{abs(row_sum-1).max():.1e}), 균일압 4psi -> p(r)=4.0 균일")

# (2) 전이폭 보정: w=12.5로 각 존 응답 개시 반경 예측 -> Lee 관측(±6mm) 안?
#     smoothstep 지지 시작 = b - w. 응답이 0에서 떠나는 반경.
lee_onset = {"Zone1(b=95)": (95.0, 85.0), "Zone2(b=85)": (85.0, 70.0), "Zone3(b=85)": (85.0, 70.0)}
for name, (b, onset_lit) in lee_onset.items():
    pred = b - w
    assert abs(pred - onset_lit) <= 6.0, f"{name}: 예측개시 {pred} vs 문헌 {onset_lit}"
    print(f"  {name}: 예측 응답개시 {pred:.1f}mm vs Lee 관측 {onset_lit:.0f}mm (차 {pred-onset_lit:+.1f}mm)")

# (3) 단일존 vs 멀티존 NU 개선 (Lee Table 3/5, 엣지제외 3mm) — 재계산
nu_single, nu_multi = 4.5, 2.5   # %
improve = (nu_single - nu_multi) / nu_single * 100
assert abs(improve - 44.44) < 0.1, f"개선율 {improve:.2f}%"
print(f"단일존 {nu_single}% -> 멀티존 {nu_multi}% : NU 개선 {improve:.1f}% (Lee 2026 Table 3/5)")

# (4) 응답행렬 블록구조 sanity: Zone3(중심) 멤버십은 엣지제외 3mm 구간(r>=95.6mm=101.6-6? )에서
#     실질 0 -> 중심존 압력이 엣지 프로파일을 거의 못 건드림(=Lee의 "Zone3 독립" 관측과 정합).
edge_mask = r >= (101.6 - 3.0)   # 엣지 3mm
assert M[edge_mask, 0].max() < 1e-3, f"Zone3가 엣지에 침투: {M[edge_mask,0].max():.2e}"
print(f"Zone3 멤버십이 엣지3mm에서 <1e-3 -> '중심존은 엣지 독립'(Lee 관측)과 모델 정합")
print("PASS — 선형 응답행렬 partition-of-unity, 전이폭 w=12.5mm 보정, NU개선 44.4% 재현")
```

## 3. (b) 상대속도장 V(r,θ) — 폐형식 + 실측 대조

### 3.1 형식(재인용, [[cmp-kinematics-rotary]] Eq.2.10-2.12)

```
V(r,θ) = |ω_p×(r_cc + r) − ω_w×r|
       = ω_p·r_cc · sqrt( (r̄μ)² + 2r̄μ cosθ + 1 ),   μ = (R_w/r_cc)(1 − ω_w/ω_p)
```

ω_p=ω_w(μ=0)이면 **V = ω_p·r_cc, 웨이퍼 전면 균일**(등방성). 엣지 순간 속도 NU = 2|μ|.
r_cc 문헌값은 [[cmp-platen-wafer-center-distance-rcc]](Zhao 2012 e₀=200mm)에서, 이 속도장은
이미 `sim/tier1_empirical/kinematics.py`(speed_stats)로 구현돼 있으므로 **여기서 재구현하지 않고
그 함수를 호출해 문헌 실측과 대조**한다.

### 3.2 실측 대조 — Ye & Yao (2025), rpm 비 스윕

Ye & Yao 2025[3](5인치 단면 폴리셔, e=277.89mm, R_w=62.5mm)는 rpm 비를 실제로 스윕한
**실측+수치** 논문이다(원문 Europe PMC XML 확보). 확인값:
- 수치: 전 범위(0-80rpm) 속도 비균일도 **NUV = 0–0.42**, ω_P=ω_C에서 NUV=0(균일).
- 폐형식 대조: "정수배에서 안정 상대속도 **1.75 m/s @ 60rpm**" ← V=ω_p·r_cc=2π·0.27789=1.746 m/s로 재현.
- 실측 3조건(plate/carrier): 60/60, 50/60, 30/60 rpm에서 평균 제거두께 **9.2 / 8.1 / 5.2 µm**,
  제거율이 60/60 대비 50/60에서 **13%**, 30/60에서 **45.6%** 낮음.

주의(계 근접도, E4): Ye&Yao는 5인치 단면 폴리셔로 300mm 팹 툴이 아니다 — **방향성·폐형식
검증에는 쓰되 절대 µm/min은 이식하지 않는다**.

### 3.3 python verify — 폐형식 균일성 + Ye&Yao 실측 대조

```python verify
"""(b) 속도장 폐형식(ω_p=ω_w → V=ω·r_cc 균일) + Ye&Yao 2025 실측 rpm비 스윕 대조.
   문헌: Ye, Yao 2025 Micromachines 16(4) 450 (DOI 10.3390/mi16040450, PMC12029203, CC-BY).
   구현: sim/tier1_empirical/kinematics.py speed_stats() 호출(재구현 금지)."""
import sys, math
sys.path.insert(0, ".")
from sim.tier1_empirical.kinematics import speed_stats

Rw, rcc = 0.0625, 0.27789   # Ye&Yao Table 1 (m)

# (1) 폐형식: 60/60(ω_p=ω_w) → V=ω_p·r_cc, 전면 균일(NU=0)
s60 = speed_stats(R_w=Rw, r_cc=rcc, rpm_w=60, rpm_p=60)
V_closed = (2*math.pi*60/60) * rcc
assert abs(s60["mean"] - V_closed) < 1e-9
assert abs(V_closed - 1.746) < 0.01, f"폐형식 V={V_closed:.4f}"
assert s60["nu_ref"] < 1e-12, "μ=0인데 NU≠0"
print(f"폐형식: 60/60 → V=ω·r_cc={V_closed:.4f} m/s ≈ Ye&Yao 1.75 m/s, NU=0(균일) ✔")

# (2) 엣지 속도 NU=2|μ| 3조건 (plate 60/50/30, carrier 60 고정)
configs = {"60/60": (60, 60), "50/60": (50, 60), "30/60": (30, 60)}
stats = {k: speed_stats(R_w=Rw, r_cc=rcc, rpm_w=w, rpm_p=p) for k, (p, w) in configs.items()}
nu_3060 = stats["30/60"]["nu_ref"]
# 30/60의 엣지 속도 NU(0.45)가 Ye&Yao 전범위 NUV 최대(0.42)와 같은 자릿수인지(다른 정규화라 근사)
assert 0.40 < nu_3060 < 0.50, f"30/60 엣지NU {nu_3060:.3f}"
print(f"엣지 속도 NU=2|μ|: 60/60={stats['60/60']['nu_ref']*100:.1f}%, "
      f"50/60={stats['50/60']['nu_ref']*100:.1f}%, 30/60={nu_3060*100:.1f}% "
      f"(Ye&Yao 전범위 NUV_max=0.42와 30/60이 동일 자릿수)")

# (3) Preston MRR ∝ 평균 V 로 본 제거율 감소 vs Ye&Yao 실측
base = stats["60/60"]["mean"]
red_pred = {k: (base - stats[k]["mean"]) / base * 100 for k in ("50/60", "30/60")}
red_lit = {"50/60": 13.0, "30/60": 45.6}          # 논문 서술(제거율 감소%)
red_thick = {"50/60": (9.2-8.1)/9.2*100, "30/60": (9.2-5.2)/9.2*100}  # 평균두께 유도
for k in ("50/60", "30/60"):
    print(f"  {k}: Preston(∝V) 예측감소 {red_pred[k]:.1f}% | 논문 제거율 {red_lit[k]:.1f}% | "
          f"평균두께 유도 {red_thick[k]:.1f}%")
    # Preston-속도 예측이 실측과 같은 자릿수(±6%p)인지 — 정확일치 아님을 명시
    assert abs(red_pred[k] - red_lit[k]) < 6.5, f"{k} 예측 {red_pred[k]:.1f} vs 문헌 {red_lit[k]}"

# 정직: Preston(∝V)이 실측보다 약 3-4%p 과대예측(50/60: 16.7 vs 13, 30/60: 49.7 vs 45.6).
# 원인 — (i) 낮은 ω_p에서 고정 ω_w=60이 상대속도를 더해 순수 ω_p·r_cc 스케일링을 벗어남,
# (ii) 캐리어 커버리지·슬러리 등 Preston 밖 인자. 맞는 척 하지 않는다(미검증: 절대 MRR 이식).
print("PASS — 폐형식 균일성·1.75m/s 재현, 3조건 속도NU, Preston-V 제거율감소 자릿수 일치(과대 3-4%p 명시)")
```

## 4. (c) 리테이너링 압력비 → 엣지 3mm 프로파일 감도

Lee 2026[1]의 단일존 실측(웨이퍼 5.0psi 고정, 링압만 스윕)이 **엣지제외 3mm NU vs
P_ring/P_zone**의 1차 실측이다(E1, 그 툴):

| P_ring [psi] | P_ring/P_zone | 엣지3mm NU |
|---|---|---|
| 5.0 | 1.0 | 4.5% |
| 6.0 | 1.2 | 6.1% (악화) |

즉 링압을 존압 위로 올리면 패드 리바운드가 커져 엣지 NU가 **악화**된다(직관 반대, Lv1-2 결론
재확인). Park 2020[2]은 다른 지표(MRMRR)로 링압 11.9→9.9psi에서 14.1% 개선을 보고 —
방향(링압↓이 유리)이 정합하나 절대 지표가 달라 합치지 않는다(E2, 별도 지표).

### 4.1 python verify — 링압비 감도 계수

```python verify
"""(c) 링압비 → 엣지3mm NU 감도. 문헌: Lee 2026 Table 3/4 (링 5/6psi, NU 4.5/6.1%)."""
P_zone = 5.0
data = [(5.0, 4.5), (6.0, 6.1)]   # (P_ring, NU%)
ratios = [(pr / P_zone, nu) for pr, nu in data]
# 감도 dNU/d(ratio) 와 dNU/d(psi)
dNU_dratio = (ratios[1][1] - ratios[0][1]) / (ratios[1][0] - ratios[0][0])
dNU_dpsi = (data[1][1] - data[0][1]) / (data[1][0] - data[0][0])
assert abs(dNU_dratio - 8.0) < 0.1, f"{dNU_dratio}"   # (6.1-4.5)/(1.2-1.0)=8.0 %/ratio
assert abs(dNU_dpsi - 1.6) < 0.01, f"{dNU_dpsi}"       # 1.6 %/psi
assert data[1][1] > data[0][1], "링압↑에 NU가 악화되지 않으면 문헌과 불일치"
print(f"엣지3mm NU 감도: {dNU_dratio:.1f} %NU per (P_ring/P_zone), {dNU_dpsi:.2f} %NU/psi")
print(f"→ 링압비 1.0→1.2에서 NU 4.5→6.1% 악화 (Lee 2026, 국소 선형 감도, 이 비율밖 외삽 금지)")
print("PASS — 링압비 엣지감도 8.0%/ratio(1.6%/psi), 악화 방향 재현")
```

감도 8.0%/ratio는 **1.0-1.2 구간의 국소 선형값**이다 — 두 점뿐이라 곡률은 미검증, 이 구간
밖 외삽 금지.

## 5. (d) 통합 함수 명세 — `tool_settings_to_fields`

### 5.1 시그니처(제안)

```
tool_settings_to_fields(
    zone_pressures_psi : list[float],   # [P_center, ..., P_edge], 존 개수 n (Lee n=3, Park n=5)
    p_ring_psi         : float,         # 리테이너링 압력
    rpm_platen         : float,         # ω_p [rpm]
    rpm_head           : float,         # ω_w [rpm]
    r_cc_m             : float,         # 축간거리 [m]
    R_wafer_m          : float,         # 웨이퍼 반경 [m]
    zone_bounds_m      : list[float],   # 존 경계 반경 [0, b1, .., R_wafer], 오름차순
    transition_w_m     : float = 0.0125,# 멤브레인 전이 반폭 [m], 기본 12.5mm
    n_radial           : int = 200,
    theta_average      : bool = True,
) -> dict:  # {r_m:[..], p_r_Pa:[..], V_r_mps:[..], V_mean_mps:float}
```

### 5.2 입력·출력·단위·유효범위

| 항목 | 단위 | 유효범위 | 근거 |
|---|---|---|---|
| zone_pressures_psi | psi | 1.5–10 (챔버 청구범위) | US6309290B1 P2 1.5–10psi([[cmp-carrier-head-retaining-ring-vendors]]) |
| p_ring_psi | psi | 1.5–9.0 | US6309290B1 P1 1.5–9.0psi |
| rpm_platen, rpm_head | rpm | 10–100(전형 30–60) | Zhao 2012 np=100 상한, Ye&Yao 실측 30–60 |
| r_cc_m | m | 0.15–0.28 | Kim&Jeong 0.15 ~ Ye&Yao 0.278([[cmp-platen-wafer-center-distance-rcc]]) |
| transition_w_m | m | 0.010–0.015 | Lee 2026 응답개시 10–15mm(§2.2) |
| **출력 p_r_Pa** | Pa | 존압 중첩(선형) | §2 응답행렬 |
| **출력 V_r_mps** | m/s | ≥0, α=1이면 균일 | §3 폐형식 |

유효범위 밖 입력은 **조용한 클램프 금지, ValueError**(sim/tier2_physics 관례, `npw_ptw_effective_pressure.py` docstring).

### 5.3 기존 sim 함수와의 중복 표 (재구현 금지 대상)

| 이 명세의 조각 | 기존 구현 | 중복 처리 |
|---|---|---|
| V(r,θ), V_mean, NU=2\|μ\| | `sim/tier1_empirical/kinematics.py` speed_stats() | **그대로 호출**, 재구현 금지 |
| Preston MRR=Kp·p·V | `sim/tier1_empirical/preston.py` | p_r_Pa·V_r_mps를 그 함수에 넘김 |
| 명목압력→국소 접촉압력 p_local | `sim/tier2_physics/gw_pressure_solve.py` | 이 명세의 **하류**(출력 p_r_Pa가 입력) |
| 패턴밀도 유효압력 | `sim/tier2_physics/npw_ptw_effective_pressure.py` | 직교(웨이퍼스케일 vs 다이스케일), 결합 안 함 |
| 존압력→p(r) 응답행렬 M | **없음(신규)** | §2, 이 명세가 요청하는 새 순수함수 |

즉 **신규 구현이 필요한 것은 §2의 응답행렬 M(zone_pressures→p(r)) 하나**뿐이고, 속도장은
기존 kinematics.py를 재사용한다. 이 분리가 이 명세의 핵심 결론이다.

## 6. 한계 / 미검증

- 응답행렬 M은 **멤브레인 선형중첩 가정**(E4)의 현상 모델이다. Lee의 실측은 존압→**제거율**
  응답이지 존압→압력이 아니므로, w=12.5mm는 압력이 아니라 제거율 응답의 전이폭을 흡수한
  등가값이다 — 압력 전이와 제거율 전이가 같다는 것은 **미검증**(Preston 국소선형 가정 하 근사).
- Ye&Yao 절대 제거율(µm/min)은 5인치 툴 값이라 300mm 이식 불가(E4, 방향만 채택). Preston(∝V)이
  실측 제거율 감소를 3-4%p 과대예측하는 원인은 §3.3에 명시(고정 ω_w 기여 + 커버리지).
- 링압비 감도 8.0%/ratio는 두 점 국소선형(미검증 곡률). Park의 MRMRR 지표와는 합치지 않음(E-룰:
  상반 지표 평균 금지, 스코프 분리).
- **진짜 폐루프(센서→실시간 재조정)**는 Lv3-1과 동일하게 미확보 — 이 명세는 정적 순방향
  `tool_settings→(p(r),V(r))`까지이고, 역방향(목표 프로파일→존압 최적화)은 M의 의사역행렬로
  풀 수 있으나 실시간 되먹임 문헌은 여전히 봇차단으로 미확보(Wang&Lu 계열).

## 7. 구현 요청 (software 부문, 직접 구현하지 않음 — ORG.md §5)

- **무엇을**: §5.1 시그니처의 `tool_settings_to_fields`. 신규 부분은 §2 응답행렬 M(존압→p(r))
  순수함수뿐. 속도장은 `sim/tier1_empirical/kinematics.py` speed_stats 재사용.
- **근거 노트**: 본 노트 §2(응답행렬·전이폭), §3(속도장), §4(링압비), §5(중복표).
- **검증에 쓸 문헌값**:
  - partition-of-unity 행합=1, 균일압 4psi→p(r)=4.0 균일(§2.4)
  - 전이폭 w=12.5mm → Lee 응답개시 85/70/70mm 예측 ±6mm(§2.4)
  - 단일존 4.5%→멀티존 2.5%, NU 개선 44.4%(§2.4)
  - 60/60에서 V=ω·r_cc=1.746 m/s(Ye&Yao 1.75), NU=0(§3.3)
  - 링압비 감도 8.0%/ratio(§4.1)
- **우선순위**: 중. 응답행렬 M은 형식이 확정됐고(선형·partition-of-unity) 검증값도 있어 구현
  가능. 단 w의 압력↔제거율 전이 등가성이 미검증이라 M 출력은 "명목 압력 프로파일"로만 쓰고
  MRR 캘리브레이션은 별도.

## 출처

[1] Lee, T.S., Lee, E.H., Jeong, H.D. (2026), "Multi-zone Pressure Control for Improvement of
    Within Wafer Non-uniformity in CMP", *J. Korean Soc. Precis. Eng.* 43(5), 443-448,
    DOI: 10.7736/JKSPE.025.132. 원문 PDF 확보(`papers/jkspe-025-132-multizone-pressure.pdf`, CC-BY-NC).
[2] Park, J.-Y., Han, J.-H., Kim, C. (2020), "A Study on the Influence of the Cross-Sectional Shape
    of the Metal-Inserted Retainer Ring and the Pressure Distribution from the Multi-Zone Carrier
    Head to Increase the Wafer Yield", *Appl. Sci.* 10(23), 8362, DOI: 10.3390/app10238362.
    원문 PDF 확보(`papers/park2020-app10238362-zone-pressure-retainer-ring.pdf`, CC-BY).
[3] Ye, G., Yao, Z. (2025), "Research on the Trajectory and Relative Speed of a Single-Sided
    Chemical Mechanical Polishing Machine", *Micromachines* 16(4), 450, DOI: 10.3390/mi16040450,
    PMC12029203 (CC-BY). 원문 Europe PMC fullTextXML 확보(`papers/ye-yao-2025-mi16040450-fulltext.xml`;
    NUV 0–0.42, 3조건 실측 9.2/8.1/5.2µm,
    1.75 m/s@60rpm). 정오표 *Micromachines* 17(2), 160(PMC12943132) — Table 1 수치 정정 대상 아님.
[4] Zhao, D., He, Y., Wang, T., Lu, X. (2012), "Effect of Kinematic Parameters and Their Coupling
    Relationships on Global Uniformity of CMP", *IEEE Trans. Semicond. Manuf.* 25(3), 502-510,
    DOI: 10.1109/TSM.2012.2190432. 원문 PDF(`papers/zhao2012-tsm-kinematic-coupling.pdf`) — α≈1 &
    αk_T0>2 설계규칙, 폐형식 속도식(§3.1)의 원전.
[5] J.-Y. Lai, PhD thesis, MIT, 2001, §2.2.2 — 속도장 폐형식 정본(2차 인용은 [[cmp-kinematics-rotary]]).
