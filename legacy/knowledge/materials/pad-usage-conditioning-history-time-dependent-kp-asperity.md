<!-- V2-SECTION: R3-pad | 공동: R4-disk | 분배완료 2026-09-16 | 근거: pad-, 패드, asperity, conditioning | 정본: ARCHITECTURE-V2.md §3 -->
# 패드 사용시간·컨디셔닝 이력 → 시간 의존 Kp·asperity 모델 (pad-lifecycle Lv3-2)

> pad-lifecycle Lv3-2 | 작성일: 2026-09-16
> 선행(직접 인용·확장): [[pad-glazing-mechanism-mrr-decay]] [[pad-thickness-groove-depth-monitoring-replacement-economics]]
> [[pad-lifetime-prediction-insitu-sensing-review]] [[hertz-gw-contact-mechanics]]
> 형제(인용만, 수정 안 함): [[pad-steady-state-glazing-conditioning-balance]]
> [[pad-usage-hours-conditioning-mrr-decay-son-lee2021]] [[../equipment/conditioner-disk-pad-cutting-model]]
> [[../equipment/conditioner-asperity-population-balance]] [[../cmp/preston-luo-dornfeld-mrr]]

## 0. 이 단원이 기존 노트와 다른 점 (중복 회피 선언)

이 저장소에는 이미 시간축 노트가 넷 있다. 이 노트는 그 넷을 반복하지 않는다.

| 기존 노트 | 이미 확보한 것 | 이 노트가 **추가로** 하는 것 |
|---|---|---|
| [[pad-glazing-mechanism-mrr-decay]] (Jeong et al. 2024) | **분** 단위, 컨디셔닝 **없는** 단발 연마의 N(t)·μR(t)·MRR(t) | 같은 현상을 **시간** 단위, 컨디셔닝 **있는** 조건에서 측정한 1차 데이터 |
| [[pad-usage-hours-conditioning-mrr-decay-son-lee2021]] (Son & Lee 2021) | 16~20 h 축의 MRR 감소율(재인용, 원문 미확보) | **원문 PDF를 직접 읽은** 시간축 데이터 3건(§2·§4·§5) |
| [[pad-steady-state-glazing-conditioning-balance]] | k_g·k_c 균형 ODE와 그 정상해 | 그 ODE가 **가정하는 함수형(단일 지수)이 실측과 어긋나는 구간**을 실측으로 특정(§5) |
| [[../equipment/conditioner-disk-pad-cutting-model]] §3 | PCR 지수감쇠 τ=27.4 h(Entegris 사례, **2차 인용**) | 같은 양을 **1차 피어리뷰 실측**으로 대조 — 지수형이 어디까지 맞고 어디서 깨지는지(§5) |

핵심 질문 하나로 좁히면: **"패드가 늙는다"를 Kp(t)의 시간 함수로 쓸 수 있는가, 아니면
패드 상태변수의 함수로 써야 하는가.** 2026-09-13 EVIDENCE-RULES 판정#8은 `sim/factors.py::_f_stab`
에서 `pad_usage_hours`·`disk_usage_hours` 드라이버를 **제외**했다 — "시간 → MRR"의 이식 가능한
계수가 없었기 때문이다. 이 노트는 그 판정을 뒤집지 않는다. 대신 그 판정이 빠뜨린 **중간
상태변수**(asperity 높이분포의 감쇠길이 λ, 패드 Rq)를 1차 실측으로 확보해, 시간축을
`시간 → 패드상태 → Kp` 두 단계로 쪼갤 수 있는지를 검증한다.

## 1. 시계는 하나가 아니다 — 네 자릿수에 걸친 네 개의 시간축

| 시계 | 지배 기구 | 무릎(knee)/시정수 | 1차 출처 |
|---|---|---|---|
| 1~10 min | 컨디셔닝 없는 asperity 소성평탄화 | 3 min 피크 후 10 min에 −17% (2 psi) | Jeong et al. 2024, [[pad-glazing-mechanism-mrr-decay]] |
| 0.5~8.5 h | 브러시 컨디셔닝 하 패드 표면 평탄화(λ 감소) | 무릎 **2.1 h** | Sampurno et al. 2011 (§2) |
| 30~300 min | 브러시 컨디셔닝 하 패드 마모·기공 개방(Rq 증가) | 무릎 **90~133 min**(압력 의존) | Zhou et al. 2018 (§4) |
| 15~30 h | 컨디셔너 다이아몬드 마모·신생 | **15 h 이후 정체** | Wu et al. 2013 (§5) |
| 16~20 h | 그루브 소진(별개 실패모드) | 16~20 h | Son & Lee 2021, [[pad-thickness-groove-depth-monitoring-replacement-economics]] |

**공통 형태는 지수감쇠가 아니라 "정체 후 감소"(plateau-then-decline)다.** 이 노트의 §2·§4·§6
세 데이터셋이 각각 독립적으로 같은 형태를 지지하며, 로그·멱 감쇠는 셋 모두에서 열등하다.
분 단위에서 검증된 로그감쇠(Jeong 2024 → `_f_stab`)를 시간 단위로 외삽하면 안 되는 이유다.

## 2. 1차 출처 A — Sampurno et al. (2011): 패드 나이 → asperity 높이분포 감쇠길이 λ

**출처**: Yasa Sampurno, Adam Rice, Yun Zhuang, Ara Philipossian, "Correlation of Pad Topography,
Friction Force and Removal Rate during Tungsten Chemical Mechanical Planarization",
*ECS Transactions* 34(1), 621–626 (2011), doi.org/10.1149/1.3567648.
원문 PDF 확보·전문 직접 읽음 → `papers/sampurno2011-ecst-pad-abruptness-tungsten-cmp.pdf`.

### 2.1 왜 이 논문이 이 단원의 중심인가
저자들이 쓰는 **abruptness λ**는 "표면높이 PDF의 오른쪽 꼬리가 1/e로 떨어지는 거리"로 정의된다.
이것은 [[hertz-gw-contact-mechanics]] §4의 지수분포 GW 모델에서 φ(z)=β·exp(−βz)의
**1/β와 정확히 같은 양**이다. 즉 이 논문은 GW 모델의 입력 파라미터를 패드 나이의 함수로 직접
측정한 드문 1차 데이터다. 저자는 Ra를 명시적으로 배격한다 — "패드 골짜기(valley)는 웨이퍼와
접촉하지 않으므로 Ra는 CMP에서 적절한 지표가 아니다"(원문 §Results 서술).

### 2.2 실험조건 (원문 §Experimental, 직접 확인)
100 mm 트라이보미터, Politex REG E II **연질** 패드(Shore D < 15 계열), Duraclean 3020-SST
**브러시** 컨디셔닝(2 lbf 일정, 다이아몬드 디스크 아님), 슬러리 SS W2000 43.3 vol% + UPW 43.3 vol%
+ 30% H2O2 13.3 vol%, 43 mL/min, 압력 4 psi, 상대속도 1.1 m/s, W 블랭킷(CVD W 4500 Å / Ti 500 Å).
패드 숙성은 W 금속 디스크 30분 연마 + 2분 브러싱 사이클 반복, 각 시점에 패드 시편을 절취해
건조 후 1.5×1.5 mm 영역 간섭계 측정.

### 2.3 판독 데이터 (Fig.3/4, 500 dpi 렌더 후 눈금 판독)

| 패드 나이 [h] | 0 | 0.5 | 2.5 | 5.5 | 8.5 |
|---|---|---|---|---|---|
| λ (abruptness) [µm] | 45.6 | 45.9 | 45.0 | 39.8 | 34.6 |
| COF | 0.967 | 0.954 | 0.963 | 0.881 | 0.821 |
| MRR [Å/min] | 5370 | 5392 | 5362 | 5138 | 5180 |

본문 명시치: COF는 첫 2.5 h 동안 0.96에서 안정, 5.5 h에 0.87, 8.5 h에 0.82로 감소.
MRR은 첫 2.5 h 약 5,400 Å/min 안정, 5.5 h 이후 약 5,100 Å/min로 떨어지고 평탄해짐.
상대표준편차는 COF 1.5%, MRR 2.0%, λ **30%**(λ가 가장 노이지한 양임을 잊으면 안 된다).
저자 환산: 2분 연마 기준 이 패드의 수명은 **약 100장**(원문 서술).

### 2.4 함수형과 계수 — 정체 후 선형감소

```
λ(t) = λ0                      (t < t_k)
λ(t) = λ0 − s_λ · (t − t_k)    (t ≥ t_k)
λ0 = 45.75 µm,  t_k = 2.07 h,  s_λ = 1.73 µm/h      (R² = 0.9995)
```
같은 데이터에 t=0부터의 단일 지수 λ=λ0·exp(−t/τ)를 맞추면 τ=31.2 h, R²=0.937로 **열등하다**.
아래 verify가 두 적합을 실제로 실행해 R²를 비교한다.

재현 요약(한 줄): Sampurno et al. 2011(doi.org/10.1149/1.3567648) Fig.3/4 판독값으로
원문이 명시한 상관계수 R²=0.98(λ–COF)·0.77(λ–MRR)을 재현해 **판독 자체를 검증**하고,
λ(t)의 함수형이 단일 지수가 아니라 정체-후-감소임을 R² 비교로 판정한다.

```python verify
# Sampurno, Rice, Zhuang, Philipossian (2011) ECS Trans. 34(1) 621-626, doi.org/10.1149/1.3567648
# Fig.3/4 판독값(원 PDF를 500 dpi로 렌더해 눈금 판독, 불확도 lambda +-0.3 um, COF +-0.003, MRR +-10 A/min)
import numpy as np
t   = np.array([0.0, 0.5, 2.5, 5.5, 8.5])          # pad age [h]
lam = np.array([45.6, 45.9, 45.0, 39.8, 34.6])      # abruptness lambda [um]  (Fig.3)
cof = np.array([0.967, 0.954, 0.963, 0.881, 0.821]) # COF                     (Fig.4a)
mrr = np.array([5370., 5392., 5362., 5138., 5180.]) # removal rate [A/min]    (Fig.4b)

def r2_lin(x, y):
    p = np.polyfit(x, y, 1)
    yh = np.polyval(p, x)
    return 1.0 - np.sum((y - yh) ** 2) / np.sum((y - y.mean()) ** 2)

# (1) 판독 검증: 원문이 명시한 상관계수 R^2 = 0.98(lambda-COF), 0.77(lambda-MRR)을 재현하는가
r2_cof = r2_lin(lam, cof)
r2_mrr = r2_lin(lam, mrr)
print(f"lambda-COF R2 = {r2_cof:.3f} (문헌값 0.98), lambda-MRR R2 = {r2_mrr:.3f} (문헌값 0.77)")
assert abs(r2_cof - 0.98) < 0.02, f"lambda-COF 재현 실패 {r2_cof:.3f}"
assert abs(r2_mrr - 0.77) < 0.03, f"lambda-MRR 재현 실패 {r2_mrr:.3f}"

# (2) 본문 서술 수치와 판독값 대조: COF 첫 2.5h 평균 0.96, 5.5h 0.87, 8.5h 0.82
assert abs(cof[:3].mean() - 0.96) < 0.01, cof[:3].mean()
assert abs(cof[3] - 0.87) < 0.015 and abs(cof[4] - 0.82) < 0.01
# MRR 본문: 첫 2.5h 약 5,400 A/min, 5.5h 이후 약 5,100 A/min
assert abs(mrr[:3].mean() - 5400) < 50, mrr[:3].mean()
assert abs(mrr[3:].mean() - 5100) < 80, mrr[3:].mean()

# (3) 함수형 판정: "정체 후 감소"(hockey stick) vs t=0부터의 단일 지수
from scipy.optimize import curve_fit
def hockey(x, y0, xk, s):
    return np.where(x < xk, y0, y0 - s * (x - xk))
def expo(x, a, tau):
    return a * np.exp(-x / tau)
def r2(y, yh):
    return 1.0 - np.sum((y - yh) ** 2) / np.sum((y - y.mean()) ** 2)

ph, _ = curve_fit(hockey, t, lam, p0=[45.5, 2.5, 1.8], maxfev=20000)
pe, _ = curve_fit(expo,   t, lam, p0=[46.0, 30.0], maxfev=20000)
r2h, r2e = r2(lam, hockey(t, *ph)), r2(lam, expo(t, *pe))
print(f"lambda(t): hockey R2={r2h:.4f} (무릎 {ph[1]:.2f} h, 기울기 {ph[2]:.2f} um/h) vs 지수 R2={r2e:.4f} (tau={pe[1]:.1f} h)")
assert r2h > r2e, "지수형이 더 나으면 이 노트의 함수형 주장이 반증됨"
assert r2h > 0.99 and 1.5 < ph[1] < 3.0 and 1.5 < ph[2] < 2.0
```

## 3. λ → Kp 결합: GW가 주는 세 후보 지수 중 실측이 고르는 것

[[hertz-gw-contact-mechanics]] §4의 폐형식(지수분포 GW, 하중 W·asperity 반경 R 고정)에서
β=1/λ를 대입하면

```
A_r / W  ∝ √(R·β) = √(R/λ)      →  A_r     ∝ λ^(−1/2)
p_local = W / A_r               →  p_local ∝ λ^(+1/2)
```

즉 패드가 매끈해질수록(λ↓) **실접촉면적은 늘고 국소압력은 떨어진다**. MRR이 무엇에
비례하느냐에 따라 λ 지수가 갈린다 — 세 후보:

| 가정 | MRR ∝ | λ 지수 |
|---|---|---|
| 실접촉면적 지배 | A_r | **−0.5** |
| asperity 스케일 Preston (MRR ∝ A_r·p_local = W, 총하중 보존) | 상수 | **0.0** |
| 국소압력 지배 | p_local | **+0.5** |

Sampurno 데이터의 실측 탄성은 **MRR ∝ λ^0.159**, **COF ∝ λ^0.582**이다. MRR 쪽은 세 후보 중
"총하중 보존"(지수 0)에 가장 가깝다 — λ가 24% 줄어드는 동안 MRR은 3.5%밖에 안 줄었다.
이것이 [[pad-glazing-mechanism-mrr-decay]] §2에서 "접촉점이 절반이 돼도 MRR은 −17%뿐"이라고
관측된 것과 **같은 물리의 시간 단위 판본**이다: 하중이 일정한 한, asperity 통계가 바뀌어도
총 제거량은 1차적으로 보존된다.

반면 COF는 λ에 **양의 탄성(+0.58)**을 보이는데, 전단강도 일정의 경계윤활 GW 모델은
COF ∝ A_r/W ∝ λ^(−1/2)를 예측하므로 **부호부터 반대다**. 즉 패드 나이에 따른 COF 감소는
접촉면적으로 설명되지 않는다 — 평탄화된 패드 위에서 슬러리 막이 두꺼워지는 윤활영역
전이(Philipossian 그룹이 Sommerfeld 수로 다루는 축)가 필요하다. **이 노트는 그 전이를 정량화하지
않았다 — 미검증**이며, 본 데이터만으로는 구별할 수 없다(설명 후보 제시에 그친다).

```python verify
# GW(지수분포) 예측 지수 vs Sampurno 2011 실측 탄성(elasticity) — 세 후보 중 어느 쪽인가
# 근거 식: knowledge/materials/hertz-gw-contact-mechanics.md §4
#   A_r/W = 3*pi*sqrt(R*beta)/(4*E*Gamma(5/2)),  beta = 1/lambda
#   => 하중 W·반경 R 고정에서  A_r ~ lambda^(-1/2),  p_local = W/A_r ~ lambda^(+1/2)
import numpy as np
from scipy import special

lam = np.array([45.6, 45.9, 45.0, 39.8, 34.6])
cof = np.array([0.967, 0.954, 0.963, 0.881, 0.821])
mrr = np.array([5370., 5392., 5362., 5138., 5180.])

# GW 폐형식이 정말 A_r ~ lambda^(-1/2)를 주는지 수치로 재확인(부호 실수 방지)
Estar, R = 1.0e9, 20e-6
def Ar_over_W(lmbda):
    beta = 1.0 / lmbda
    return 3 * np.pi * np.sqrt(R * beta) / (4 * Estar * special.gamma(2.5))
lams_m = np.array([30e-6, 45e-6])
slope_Ar = np.polyfit(np.log(lams_m), np.log([Ar_over_W(x) for x in lams_m]), 1)[0]
assert abs(slope_Ar + 0.5) < 1e-9, f"GW A_r 지수가 -1/2가 아님: {slope_Ar}"

# 실측 탄성 (log-log 기울기)
e_mrr = np.polyfit(np.log(lam), np.log(mrr), 1)[0]
e_cof = np.polyfit(np.log(lam), np.log(cof), 1)[0]
print(f"실측 탄성: MRR ~ lambda^{e_mrr:.3f}, COF ~ lambda^{e_cof:.3f}")

# 후보 지수 3종 (평균내지 않고 하나를 고른다 — EVIDENCE-RULES)
cand = {"A_r 비례(접촉면적 지배)": -0.5,
        "총하중 보존(asperity 스케일 Preston)": 0.0,
        "p_local 비례(국소압력 지배)": +0.5}
pick = min(cand.items(), key=lambda kv: abs(kv[1] - e_mrr))
print(f"MRR 탄성에 가장 가까운 후보: {pick[0]} (예측 지수 {pick[1]:+.1f})")
assert pick[1] == 0.0, "MRR 탄성이 '총하중 보존' 이외 후보에 더 가까우면 §3 해석을 고쳐야 한다"
assert abs(e_mrr) < 0.25, e_mrr

# COF: 경계윤활 + 전단강도 일정 가정이면 COF ~ A_r/W ~ lambda^(-1/2) — 부호가 실측과 반대여야 한다
assert e_cof > 0, "COF 탄성 부호가 양이 아니면 아래 서술이 틀림"
assert e_cof * (-0.5) < 0, "COF 실측 탄성과 경계윤활 GW 예측(-0.5)의 부호가 같다면 반증 서술을 철회해야 함"
print(f"COF: 경계윤활 GW 예측 -0.50 vs 실측 {e_cof:+.3f} — 부호 자체가 반대(면적 지배로 설명 불가)")
```

## 4. 1차 출처 B — Zhou et al. (2018): 압력이 바꾸는 것은 기울기가 아니라 무릎 시각

**출처**: Yan Zhou, Haimei Luo, Guoshun Pan, Chunli Zou, Guihai Luo, Gaopan Chen, Chengxi Kang,
"Study on Pad Performance Deterioration in Chemical Mechanical Polishing (CMP) of Fused Silica",
*ECS J. Solid State Sci. Technol.* 7(6), P295–P298 (2018), doi.org/10.1149/2.0011806jss.
원문 PDF 확보·전문 직접 읽음 → `papers/zhou2018-jss-pad-performance-deterioration-fused-silica.pdf`.

조건(원문 §Experimental): 4인치 융착실리카, 폴리우레탄 패드, 콜로이달 실리카 8 wt% pH 2.0,
70 mL/min, 웨이퍼 50 rpm·정반 150 rpm, 압력 0.9 psi 또는 1.26 psi, **매 연마 후 플라스틱
브러시 컨디셔닝**. 패드 Rq는 20개 지점 평균.

### 4.1 판독 데이터 (Fig.1/Fig.8, 400 dpi 렌더 판독)

| 사용시간 [min] | 30 | 60 | 90 | 120 | 150 | 180 | 210 | 240 | 270 | 300 |
|---|---|---|---|---|---|---|---|---|---|---|
| MRR 0.9 psi [nm/min] | 36.8 | 46.2 | 43.3 | 44.0 | 45.6 | 38.0 | 27.0 | 21.7 | 23.2 | 20.9 |
| MRR 1.26 psi [nm/min] | 47.5 | 54.8 | 56.3 | 54.3 | 46.0 | 30.3 | 32.3 | 29.4 | 28.9 | 20.8 |
| 패드 Rq 0.9 psi [µm] | 0.68 | 0.70 | 0.74 | 0.755 | 0.775 | 0.79 | 0.80 | 0.875 | 0.915 | 0.94 |
| 패드 Rq 1.26 psi [µm] | 0.685 | 0.73 | 0.765 | 0.825 | 0.89 | 0.93 | 1.015 | 1.035 | 1.065 | 1.115 |

신품 패드 Rq는 0.474 µm(본문 명시) — 즉 **첫 30분에 0.47→0.68 µm로 급등하는 브레이크인**이
따로 있고([[pad-breakin-asperity-mrr-runup]]과 같은 구간), 그 뒤가 이 노트가 다루는 구간이다.

### 4.2 세 가지 정량 결론
1. **MRR은 정체 후 무너진다**: 60~150 min 정체 44.8 nm/min → 240 min 이후 21.9 nm/min(−51%).
   1.26 psi도 같은 형태로 −52%. 정체-후-감소 적합이 단일 지수보다 두 압력 모두에서 우월하다.
2. **무릎 이후의 감소 기울기는 압력에 거의 무관하다**: 0.165 vs 0.168 nm/min per min(차이 1.7%).
   압력이 바꾸는 것은 **무릎 시각**이다(적합치 133 min → 90 min, 본문 서술 150 min → 120 min).
3. **무릎 시각의 압력 지수**: 본문 서술치로 −0.66, 적합치로 −1.17. 두 추정이 **−1을 사이에 둔다** —
   "무릎까지의 누적 마찰일이 일정"(t_knee ∝ 1/p)이라는 가설과 모순되지 않지만, **압력 2점의
   기울기이므로 지수 자체는 미검증**이다. 어느 한쪽을 골라 상수로 박으면 안 된다.

**Sampurno(λ↓, 평탄화)와 Zhou(Rq↑, 거칠어짐)는 겉보기에 반대**지만 모순이 아니다. Zhou의 Rq는
골짜기를 포함한 전체 거칠기이고(기공이 열려 큰 기공층이 드러나면 Rq는 올라간다), Sampurno의 λ는
**접촉하는 꼬리만** 보는 양이다. Sampurno가 Ra를 배격한 이유가 바로 이것이다. 두 논문 모두
"패드 표면이 원래 상태에서 멀어지면 MRR이 꺾인다"는 같은 이야기를 서로 다른 지표로 말한다.

```python verify
# Zhou et al. (2018) ECS J. Solid State Sci. Technol. 7(6) P295, doi.org/10.1149/2.0011806jss
# Fig.1/Fig.8 판독값(400 dpi 렌더 판독, MRR +-0.5 nm/min, Rq +-0.01 um)
import numpy as np
from scipy.optimize import curve_fit

t     = np.array([30., 60., 90., 120., 150., 180., 210., 240., 270., 300.])   # 패드 사용시간 [min]
rr09  = np.array([36.8, 46.2, 43.3, 44.0, 45.6, 38.0, 27.0, 21.7, 23.2, 20.9]) # 0.9 psi  [nm/min]
rr126 = np.array([47.5, 54.8, 56.3, 54.3, 46.0, 30.3, 32.3, 29.4, 28.9, 20.8]) # 1.26 psi [nm/min]
rq09  = np.array([0.68, 0.70, 0.74, 0.755, 0.775, 0.79, 0.80, 0.875, 0.915, 0.94])   # 패드 Rq [um]
rq126 = np.array([0.685, 0.73, 0.765, 0.825, 0.89, 0.93, 1.015, 1.035, 1.065, 1.115])

# (1) 본문 서술 대조: 60~150 min 정체구간 MRR 약 45 nm/min, 240 min 이후 약 20 nm/min (0.9 psi)
plateau09 = rr09[(t >= 60) & (t <= 150)].mean()
tail09    = rr09[t >= 240].mean()
print(f"0.9 psi: 정체 {plateau09:.1f} nm/min (본문 '약 45'), 말기 {tail09:.1f} nm/min (본문 '약 20')")
assert abs(plateau09 - 45.0) < 2.0, plateau09
assert abs(tail09 - 20.0) < 3.0, tail09

# (2) 함수형: 정체-후-감소 vs t=0부터의 단일 지수 (60 min 이후, 브레이크인 제외)
def hockey(x, y0, xk, s):
    return np.where(x < xk, y0, np.maximum(y0 - s * (x - xk), 0.0))
def expo(x, a, tau):
    return a * np.exp(-x / tau)
def r2(y, yh):
    return 1.0 - np.sum((y - yh) ** 2) / np.sum((y - y.mean()) ** 2)

m = t >= 60
out = {}
for name, y, p0 in (("0.9psi", rr09, [45, 150, 0.25]), ("1.26psi", rr126, [55, 120, 0.3])):
    ph, _ = curve_fit(hockey, t[m], y[m], p0=p0, maxfev=40000)
    pe, _ = curve_fit(expo,   t[m], y[m], p0=[70, 300], maxfev=40000)
    out[name] = (ph, r2(y[m], hockey(t[m], *ph)), r2(y[m], expo(t[m], *pe)))
    print(f"{name}: hockey R2={out[name][1]:.3f} (무릎 {ph[1]:.0f} min, 감소 {ph[2]:.3f} nm/min per min) "
          f"vs 지수 R2={out[name][2]:.3f}")
    assert out[name][1] > out[name][2], f"{name}에서 지수형이 더 나음 — 함수형 주장 반증"

# (3) 압력이 바꾸는 것은 '감소 기울기'가 아니라 '무릎 시각'이다
s09, s126 = out["0.9psi"][0][2], out["1.26psi"][0][2]
k09, k126 = out["0.9psi"][0][1], out["1.26psi"][0][1]
print(f"무릎 후 기울기: {s09:.3f} vs {s126:.3f} nm/min^2 (차이 {abs(s126-s09)/s09*100:.1f}%), "
      f"무릎 시각: {k09:.0f} -> {k126:.0f} min")
assert abs(s126 - s09) / s09 < 0.10, "기울기가 10% 넘게 다르면 '기울기 불변' 주장 철회"
assert k126 < k09 * 0.9, "무릎이 앞당겨지지 않으면 압력 주장 철회"

# (4) 무릎 시각의 압력 지수: 본문 명시치(150->120 min)와 적합치(위) 두 추정
n_text = np.log(120 / 150) / np.log(1.26 / 0.9)
n_fit  = np.log(k126 / k09) / np.log(1.26 / 0.9)
print(f"무릎시각 압력지수 n: 본문치 {n_text:.2f}, 적합치 {n_fit:.2f} (누적일 일정 가설이면 -1)")
assert -1.3 < n_fit < -0.5 and -1.0 < n_text < -0.5
assert min(n_text, n_fit) < -1.0 < max(n_text, n_fit), \
    "두 추정이 -1을 사이에 두지 않으면 '누적일 일정 가설과 정합' 서술을 약화해야 함"

# (5) 무릎 시점의 패드 Rq: 본문은 0.9 psi에서 약 0.8 um, 1.26 psi에서 약 0.9 um이라 명시
rq_at_150 = rq09[t == 150][0]
rq_at_120 = rq126[t == 120][0]
print(f"무릎 시점 판독 Rq: 0.9psi@150min {rq_at_150:.3f} um (본문 '약 0.8'), "
      f"1.26psi@120min {rq_at_120:.3f} um (본문 '약 0.9')")
assert abs(rq_at_150 - 0.8) < 0.05, rq_at_150
# 1.26 psi는 본문 서술(0.9)과 판독(0.825)이 8% 어긋난다 — 숨기지 않고 기록
gap = abs(rq_at_120 - 0.9) / 0.9
print(f"  -> 1.26 psi 무릎 Rq: 본문 서술과 판독이 {gap*100:.0f}% 불일치(원인 미상, §8에 기록)")
assert gap < 0.12
```

## 5. 1차 출처 C — Wu et al. (2013): 컨디셔너 디스크 공격성은 지수감쇠가 아니라 2단계

**출처**: Changhong Wu, Yun Zhuang, Xiaoyan Liao, Yubo Jiao, Yasa Adi Sampurno, Siannie Theng,
Fred Sun, Ananth Naman, Ara Philipossian, "Aggressive Diamond Characterization and Wear Analysis
during Chemical Mechanical Planarization", *ECS J. Solid State Sci. Technol.* 2(1), P36–P41 (2013;
online 2012-12-05), doi.org/10.1149/2.036301jss. 원문 PDF 확보·전문 직접 읽음
→ `papers/wu2012-jss-aggressive-diamond-wear.pdf`. 동일 데이터의 학위논문판(Ch.6, 그림·표 동일)
→ `papers/wu2015-ua-thesis-slurry-temperature-aggressive-diamonds-cmp.pdf`
(Changhong Wu, Univ. of Arizona PhD thesis, 2015, repository.arizona.edu, DSpace API로 확보).

조건: 3M A3700 디스크 + CMC D100 동심그루브 패드, Araca APD-800, 300 mm Si 블랭킷,
컨디셔닝 하중 13.3 N·디스크 95 rpm·분당 10회 스윕, 연마 10.3 kPa·2.2 m/s, DI water 300 mL/min,
**총 30시간**. 공격성 지표는 폴리카보네이트 시편 위 dragging test로 만든 **furrow 단면적**.

### 5.1 실측 (원문 Fig.4/6/7/10, 본문 명시치)
- 원래 top-20 공격 다이아의 furrow 면적: 1242 µm²(방향1)·1223 µm²(방향7) → **15 h에 −45%/−48%**
  (초록 헤드라인 −47%), 15→30 h는 유의한 변화 없음.
- 그 사이 **신생(newly "born") 공격 다이아가 7개씩 등장**. 15 h 시점 새 top-20의 면적은
  1088/899 µm²로 원래 top-20보다 12%/27%(평균 20%) 낮다.
- 활성 다이아 **전체** furrow 면적: 15 h에 −10%/−22%, 15→30 h "거의 불변".
- 상위 20개가 전체 절삭의 **81%**를 담당(15 h 후 49~54%로 분산). 반복 dragging의 표준편차는
  평균의 15% 이내.

### 5.2 현행 지수모델(τ=27.4 h)과의 대조 — 어디까지 맞고 어디서 깨지는가
`sim/tier2_physics/conditioner_pcr_decay.py`는 A(t)=exp(−t/27.4 h)를 쓴다. 그 τ는 Entegris 사례
"50 h에 PCR 16%"를 역산한 값이고 원 출처(Palmgren 2004)는 미확보 **2차 인용**이다
([[../equipment/conditioner-disk-pad-cutting-model]] §3, §6이 이미 그렇게 명시).

- 15 h 예측 0.578 — **원래 top-20의 실측 0.535와 재현성(15%) 이내로 일치**한다.
- 30 h 예측 0.335 — **디스크 전체 실측 0.84와 2.5배 차이**. 지수모델이 크게 과소예측한다.

**판정(EVIDENCE-RULES: 1차 피어리뷰 > 업체 2차 인용)**: 단일 지수는 "이미 일하고 있던 다이아가
닳는 속도"로는 타당하지만, **디스크 전체의 절삭능은 신생 다이아가 보충해 0~30 h 구간에서 거의
평평하다**. 두 지수를 평균내지 않는다. 물리적으로 맞는 최소 수정은 하한(floor)을 둔 형태다:

```
A(t) = A_inf + (1 − A_inf)·exp(−t/τ_wear)
τ_wear ≈ 15 h 오더(원래 공격다이아 마모 시정수), A_inf ≈ 0.78~0.90 (30 h 시점 실측 0.84)
```
단, Wu의 실험은 **30 h까지**다. Entegris 사례의 "50 h에 16%"는 그 바깥 구간이며 지표도 다르다
(furrow 단면적 vs 패드 절삭율 PCR). **두 데이터는 직접 비교 불가**이므로 이 노트는 τ=27.4 h를
**교체하지 않는다** — 0~30 h 구간에 대해 "지수형은 이 구간의 디스크 전체 공격성을 설명하지
못한다"는 반증만 기록한다. 50 h 스케일의 1차 실측은 **미확보**.

```python verify
# Wu, Zhuang, Liao, Jiao, Sampurno, Theng, Sun, Naman, Philipossian (2013; online 2012)
#   ECS J. Solid State Sci. Technol. 2(1) P36-P41, doi.org/10.1149/2.036301jss
#   동일 데이터의 학위논문판: Wu, C. (2015) Univ. of Arizona PhD thesis, Ch.6 (repository.arizona.edu)
import math

# 원문 Fig.4/6/7/10 및 본문 명시치 (furrow surface area, um^2)
orig_top20 = {"O1": 1242.0, "O7": 1223.0}     # 연마 전 (Fig.4)
new_top20  = {"O1": 1088.0, "O7": 899.0}      # 15h 후 새 top-20 (Fig.7)
drop_orig_15h = {"O1": 0.45, "O7": 0.48}      # 본문: 원래 top-20 면적 45%/48% 감소
drop_total_15h = {"O1": 0.10, "O7": 0.22}     # 본문: 전체 활성 다이아 면적 10%/22% 감소
share_before, share_after_15h = 0.81, {"O1": 0.49, "O7": 0.54}
sigma_repeat = 0.15                            # 본문: 반복 dragging 표준편차 <= 평균의 15%

# (1) 본문 자기일관성: 새 top-20이 원래 top-20보다 '평균 20% 낮다'
lower = {k: 1 - new_top20[k] / orig_top20[k] for k in orig_top20}
print(f"새 top-20 감소: O1 {lower['O1']*100:.1f}% (본문 12%), O7 {lower['O7']*100:.1f}% (본문 27%), "
      f"평균 {sum(lower.values())/2*100:.1f}% (본문 '20%')")
assert abs(lower["O1"] - 0.12) < 0.01 and abs(lower["O7"] - 0.27) < 0.01
assert abs(sum(lower.values()) / 2 - 0.20) < 0.01

# (2) 헤드라인 47%는 두 방향 평균인가
mean_drop = sum(drop_orig_15h.values()) / 2
assert abs(mean_drop - 0.465) < 0.01, mean_drop     # 초록의 "47%"와 반올림 수준 일치
assert mean_drop > sigma_repeat, "측정 재현성(15%)보다 작으면 유의하다고 말할 수 없다"

# (3) 현행 sim/tier2_physics/conditioner_pcr_decay.py 의 단일 지수 tau=27.4 h 와 대조
#     (tau 출처: Entegris 사례 '50h에 PCR 16%' 역산 — 2차 인용,
#      knowledge/equipment/conditioner-disk-pad-cutting-model.md §3)
TAU_H = 27.4
pred_15 = math.exp(-15.0 / TAU_H)
pred_30 = math.exp(-30.0 / TAU_H)
meas_total_15 = 1 - sum(drop_total_15h.values()) / 2          # 디스크 전체 절삭능 (15h)
meas_total_30 = meas_total_15                                 # 본문: 15->30h "거의 불변"
meas_orig_15 = 1 - mean_drop                                  # 원래 top-20만 (15h)
print(f"tau=27.4h 지수 예측 A(15h)={pred_15:.3f}, A(30h)={pred_30:.3f}")
print(f"실측 원래 top-20 A(15h)={meas_orig_15:.3f}  /  디스크 전체 A(15h)={meas_total_15:.3f}, A(30h)={meas_total_30:.3f}")

# 지수모델은 '마모된 원래 공격다이아'는 맞히지만(15% 재현성 이내)
assert abs(pred_15 - meas_orig_15) / meas_orig_15 < sigma_repeat, \
    "지수모델이 원래 top-20 15h 값도 못 맞히면 §5 서술을 고쳐야 함"
# 디스크 전체(신생 다이아 포함)는 30h에서 2배 이상 과소예측한다
ratio_30 = meas_total_30 / pred_30
print(f"30h 디스크 전체: 실측/지수예측 = {ratio_30:.2f}배 (지수모델 과소예측)")
assert ratio_30 > 2.0, "2배 미만이면 '지수모델 기각' 주장을 약화해야 한다"

# (4) 공격 다이아 집중도: 상위 20개가 전체 절삭의 대부분을 한다 -> '유효 그릿 수'는 20 오더
assert share_before == 0.81 and min(share_after_15h.values()) >= 0.49
print(f"상위 20개 점유율 {share_before*100:.0f}% -> 15h 후 {min(share_after_15h.values())*100:.0f}~"
      f"{max(share_after_15h.values())*100:.0f}% (신생 다이아로 분산)")
```

## 6. 실장비 교차검증 — PHM 2016 477 웨이퍼: 패드 나이 축과 드레서 나이 축은 대등하지 않다

`validation/raw/phm2016/joined.json`은 웨이퍼마다 `pad_usage`와 `dresser` 두 이력 컬럼을 함께
갖는다. [[pad-steady-state-glazing-conditioning-balance]] §4(D)는 드레서 축만 썼다. 두 축을
같은 웨이퍼 집합에서 비교하면:

- 저속군(n=433): **드레서 사용량 vs MRR ρ = −0.696**, **패드 사용량 vs MRR ρ = +0.030**.
- 두 축은 서로 거의 독립(ρ = −0.076)이므로 교란이 아니라 진짜 차이다.
- 함수형 비교(드레서 축): 정체-후-감소 R²=0.531 > 선형 0.515 ≈ 지수 0.514 ≫ 로그 0.335 ≈ 멱 0.309.

**결론 두 가지.** (i) 이 양산 장비에서 시간의존 Kp를 지배하는 것은 **패드 나이가 아니라
컨디셔닝 이력**이다 — 판정#8이 `pad_usage_hours`를 제외한 것은 이 데이터와도 정합한다.
(ii) 함수형은 다시 **정체-후-감소**가 최선이지만 선형·지수와의 차이가 0.02 미만이라
**구분력이 약하다**(과적합 경계). 반면 로그·멱형은 0.19 이상 열등해 **명확히 배제**된다 —
Jeong 2024의 분 단위 로그감쇠를 시간축으로 외삽하면 안 된다는 §1 결론의 실장비 판본이다.
⚠ 모든 컬럼이 은닉 배율로 스케일돼 있어 **절대값·무릎의 물리 단위는 알 수 없다**(형태·순위만 사용).

```python verify
# 실장비 교차검증 — PHM Society 2016 Data Challenge (CMP tool health), 조건+MRR 연결 477 웨이퍼
# 로컬: validation/raw/phm2016/joined.json (validation/fetch_phm2016.py 로 재생성)
# ⚠ 모든 컬럼이 은닉 배율로 스케일됨 -> 절대값·단위 사용 금지, '형태와 순위'만 쓴다.
import json
from pathlib import Path
import numpy as np
from scipy.stats import spearmanr
from scipy.optimize import curve_fit

rows = json.load(open(Path.home() / "fab-sim/validation/raw/phm2016/joined.json"))
pad = np.array([r["pad_usage"] for r in rows])
drs = np.array([r["dresser"] for r in rows])
mrr = np.array([r["mrr"] for r in rows])
assert len(rows) == 477

lo = mrr < 120            # 저속 레시피군 (기존 노트 §4(D)와 동일 분할)
assert lo.sum() == 433
rho_drs = spearmanr(drs[lo], mrr[lo]).correlation
rho_pad = spearmanr(pad[lo], mrr[lo]).correlation
print(f"저속군(n={lo.sum()}): 드레서 사용량 vs MRR rho={rho_drs:.3f} / 패드 사용량 vs MRR rho={rho_pad:.3f}")
# 기존 README 기록값 -0.696 재현
assert abs(rho_drs - (-0.696)) < 0.01, rho_drs
# 같은 웨이퍼 집합에서 '패드 나이' 축은 사실상 무상관 — 두 이력축은 대등하지 않다
assert abs(rho_pad) < 0.10, rho_pad
assert abs(rho_drs) > 5 * abs(rho_pad), "드레서 축 우세가 5배 미만이면 §6 결론 약화"

# 두 축이 서로 교란하고 있지는 않은가(독립성 확인)
rho_cross = spearmanr(pad, drs).correlation
print(f"패드 사용량 vs 드레서 사용량 rho={rho_cross:.3f} (거의 독립)")
assert abs(rho_cross) < 0.15

# 함수형 비교: 정체-후-감소 / 선형 / 지수 / 멱 / 로그
x, y = drs[lo], mrr[lo]
o = np.argsort(x); x, y = x[o], y[o]
def r2(y, yh):
    return 1.0 - np.sum((y - yh) ** 2) / np.sum((y - y.mean()) ** 2)
def hockey(x, y0, xk, s):
    return np.where(x < xk, y0, y0 - s * (x - xk))
fits = {}
ph, _ = curve_fit(hockey, x, y, p0=[78, 300, 0.03], maxfev=40000)
fits["정체후감소"] = r2(y, hockey(x, *ph))
fits["선형"] = r2(y, np.polyval(np.polyfit(x, y, 1), x))
pe, _ = curve_fit(lambda x, a, tau: a * np.exp(-x / tau), x, y, p0=[85, 900], maxfev=40000)
fits["지수"] = r2(y, pe[0] * np.exp(-x / pe[1]))
pp, _ = curve_fit(lambda x, a, b: a * x ** (-b), x, y, p0=[100, 0.06], maxfev=40000)
fits["멱"] = r2(y, pp[0] * x ** (-pp[1]))
pl, _ = curve_fit(lambda x, a, b: a + b * np.log(x), x, y, p0=[95, -4], maxfev=40000)
fits["로그"] = r2(y, pl[0] + pl[1] * np.log(x))
for k, v in sorted(fits.items(), key=lambda kv: -kv[1]):
    print(f"  {k:6s} R2={v:.3f}")
best = max(fits, key=fits.get)
assert best == "정체후감소", f"최적 함수형이 {best} — §6 결론 수정 필요"
# 다만 상위 3종의 차이는 작다(과적합 경계) — 정직하게 assert 로 남긴다
assert fits["정체후감소"] - fits["선형"] < 0.05, "차이가 크면 아래 '구분력 약함' 서술을 고칠 것"
# 로그·멱형은 분명히 열등하다 (Jeong 2024 분 단위 로그감쇠를 시간축에 그대로 외삽하면 안 된다)
assert fits["로그"] < fits["정체후감소"] - 0.15 and fits["멱"] < fits["정체후감소"] - 0.15
print(f"무릎 추정 {ph[1]:.0f} (스케일 단위), 무릎 전 MRR {ph[0]:.1f}, 이후 기울기 {ph[2]:.4f}/단위")
```

## 7. 종합 — 이식 가능한 것과 이식 불가능한 것

### 7.1 이식 가능(계수까지 확보)
1. **λ(t) 상태방정식** (Sampurno et al. 2011, 연질 패드·브러시 컨디셔닝·4 psi·1.1 m/s):
   λ0 = 45.75 µm, 무릎 t_k = 2.07 h, 무릎 후 기울기 1.73 µm/h, R² = 0.9995.
   λ는 지수분포 GW의 1/β와 같은 양이므로 [[hertz-gw-contact-mechanics]]의 폐형식에 **직접** 꽂힌다.
2. **λ → 관측량 탄성**: MRR ∝ λ^0.159, COF ∝ λ^0.582(같은 데이터 log-log 기울기).
   MRR 탄성이 0에 가깝다는 것 자체가 "하중 보존 때문에 Kp(t)는 asperity 통계 변화에 둔감하다"는
   정량 근거다 — **시간의존 Kp를 넣을 때 과대 효과를 경계해야 한다**.
3. **컨디셔너 공격성의 하한**: A(30 h) ≈ 0.84 (Wu et al. 2013, furrow 면적 기준, 0~30 h 구간).

### 7.2 이식 불가능(조건 불일치·근거 부족)
- **무릎 시각 t_k의 절대값**: 2.07 h(Politex 연질·W CMP), 90~133 min(폴리우레탄·융착실리카),
  16~20 h(하드 패드·다이아 디스크, [[pad-usage-hours-conditioning-mrr-decay-son-lee2021]]).
  **패드 종류·컨디셔닝 방식이 t_k를 한 자릿수 넘게 흔든다** — 상수로 박으면 안 된다.
- **무릎의 압력 지수**: −0.66(본문치)과 −1.17(적합치) 사이. 2점 기울기라 **미검증**.
- **λ의 절대 스케일**: Sampurno는 연질 Politex 패드다. IC1000급 하드 패드의 λ(t)는 이 노트가
  확보하지 못했다 — **미검증**.
- **τ=27.4 h 교체 근거 없음**: §5는 0~30 h 구간의 반증만 제공한다. 50 h 스케일 1차 실측 미확보.

### 7.3 형제 영역 경계
컨디셔너 디스크 자체의 그릿 설계·마모(§5의 furrow 데이터)는 disk-conditioner·disk-design
영역이다([[../equipment/conditioner-grit-wear-scratch-lifetime]],
[[disk-design-cutrate-asperity-regeneration-model]]). 이 노트는 그 결과를 **패드 쪽 Kp(t)의
입력으로 인용만** 하고 해당 노트를 수정하지 않는다.

## 8. 미검증·한계 (정직 표기)
- Sampurno 2011의 λ 상대표준편차는 **30%**다. 무릎 2.07 h는 5점 적합이고 λ 자체가 노이지하므로
  무릎 시각의 불확도는 최소 ±0.5 h 오더로 봐야 한다(논문에 오차막대 없음 — **미검증**).
- Zhou 2018의 1.26 psi 무릎 시점 패드 Rq: 본문 서술 "약 0.9 µm" vs 그림 판독 0.825 µm로
  **8% 불일치**. 원인 미상(저자가 150 min 시점 값을 가리켰을 가능성 — **확인 못 함**).
- §3의 COF 해석(윤활영역 전이)은 **후보 설명이지 검증된 기구가 아니다**. 이 노트의 데이터로는
  Sommerfeld 수를 계산할 수 없다(슬러리 점도·막두께 미측정) — **미검증**.
- §5의 지수모델 반증은 **furrow 단면적** 지표에 대한 것이다. PCR(패드 절삭율 µm/h)로 같은
  결론이 나오는지는 **확인 못 했다**(Wu 논문은 MRR·PCR을 측정하지 않았고, 저자 스스로
  "MRR은 측정하지 않았으나 15 h 후 감소했다가 안정될 것으로 **예상**한다"고만 썼다 — 2차 추론).
- §6의 PHM 데이터는 폐루프 제어가 걸린 **관측 데이터**다. 인과가 아니라 순위·형태만 쓴다.
  무릎의 물리 단위 환산 배율은 **미상**.
- Son & Lee 2021의 16~20 h 축은 여전히 **원문 미확보(재인용)** 상태다
  ([[pad-usage-hours-conditioning-mrr-decay-son-lee2021]] §6) — 이번 회차에도 해소하지 못했다.

## 9. 출처
1. Y. Sampurno, A. Rice, Y. Zhuang, A. Philipossian, "Correlation of Pad Topography, Friction
   Force and Removal Rate during Tungsten Chemical Mechanical Planarization", *ECS Transactions*
   34(1), 621–626 (2011). DOI: 10.1149/1.3567648. 전문 확보·직접 읽음.
2. Y. Zhou, H. Luo, G. Pan, C. Zou, G. Luo, G. Chen, C. Kang, "Study on Pad Performance
   Deterioration in Chemical Mechanical Polishing (CMP) of Fused Silica", *ECS J. Solid State
   Sci. Technol.* 7(6), P295–P298 (2018). DOI: 10.1149/2.0011806jss. 전문 확보·직접 읽음.
3. C. Wu, Y. Zhuang, X. Liao, Y. Jiao, Y. A. Sampurno, S. Theng, F. Sun, A. Naman,
   A. Philipossian, "Aggressive Diamond Characterization and Wear Analysis during Chemical
   Mechanical Planarization", *ECS J. Solid State Sci. Technol.* 2(1), P36–P41 (2013).
   DOI: 10.1149/2.036301jss. 전문 확보·직접 읽음.
4. C. Wu, "Control of Slurry Flow, Temperature and Aggressive Diamonds in Chemical Mechanical
   Planarization", PhD thesis, University of Arizona (2015), Ch.6. 전문 확보·직접 읽음
   (repository.arizona.edu DSpace REST API). 3번과 동일 데이터의 학위논문판.
5. PHM Society 2016 Data Challenge (CMP tool health tracking), 로컬 조인
   `validation/raw/phm2016/joined.json` — 실장비 관측 데이터, 은닉 배율 스케일.
