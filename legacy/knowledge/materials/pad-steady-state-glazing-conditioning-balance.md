<!-- V2-SECTION: R3-pad | 공동: R4-disk | factor: stab -->
# 패드 정상상태 모델: 글레이징률 vs 컨디셔닝 재생률의 균형 → S(안정성) × Γ(드레서 마모)

> 부모: [[pad-glazing-mechanism-mrr-decay]] (Jeong 2024 무컨디셔닝 감쇠 1차 데이터),
> [[pad-wear-glazing-mrr-decay]] (Shi & Ring population balance — "정상상태 d가 존재한다").
> 형제: [[../equipment/conditioner-disk-pad-cutting-model]] §2(Cut Rate = Wear Rate 균형) · §3(PCR 지수감쇠 τ),
> [[../equipment/disk-insitu-exsitu-conditioning-mrr-stability]] §3(압력별 회복 컨디셔닝 시간 표),
> [[../equipment/conditioner-grit-wear-scratch-lifetime]] §2(그릿 마모 → 절삭율 저하),
> [[../equipment/conditioner-grit-density-protrusion-cutrate]], [[disk-design-pad-roughness-asperity-relation]] §5.
> 검증: `validation/raw/phm2016/README.md` (실장비 477 웨이퍼, 드레서 사용량 vs MRR ρ=−0.70 저속군).

## 0. 왜 이 노트가 필요한가 — 시간감쇠 문헌을 더 찾는 것이 아니라 물리를 바꾼다

`sim/factors.py::_f_stab`은 2026-09-14까지 **컨디셔닝이 없는** 1~10분 로그감쇠(Jeong 2024, 실리카/IC1000)만
담았다. EVIDENCE-RULES 판정#9는 비-실리카 계 시간감쇠 계수를 3회차 탐색 끝에 "코퍼스에 존재하지 않음"으로
종결했고, 이 노트는 **그 판정을 존중한다** — 재탐색하지 않는다.

대신 실제 공정의 물리를 바로 세운다. 양산 CMP는 in-situ(또는 주기적 ex-situ) 컨디셔닝으로 **글레이징을 매
순간 되돌린다**. 그러므로 MRR 안정성을 정하는 것은 "시간이 얼마나 지났나"가 아니라 **글레이징률 k_g와
절삭재생률 k_c·G의 균형점**이다. Ring/Lawing의 "Cut Rate = Wear Rate 균형"([[../equipment/conditioner-disk-pad-cutting-model]]
§2)과 Shi & Ring(2010)의 "유체 포함 시 d가 유한한 정상상태에 수렴"([[pad-wear-glazing-mrr-decay]] §2.2)이
같은 말을 하고 있었는데 엔진에는 없었다. 균형 모델은 **패드 재질(IC1000류)의 성질**이라 슬러리 팩 5개에 공통이며,
슬러리 의존성은 k_g 한 곳에만 갇힌다(§5에서 그 영향을 정량화한다).

## 1. 모델 — 패드 조도(활성 asperity 척도) R(t)의 1차 균형 방정식

R = 컨디셔닝 직후 패드의 "절삭 능력 지표"(Rpk 또는 접촉점 수 N — Jeong 2022 회귀식 MRR ∝ +186.9·Rpk,
Jeong 2024 Table 1 N(t))를 신품 컨디셔닝 상태 R_fresh=1로 정규화한 무차원량.

```
dR/dt = −k_g · R  +  k_c · G · (R_fresh − R)                      … (1)
  k_g  [1/min]  글레이징률: 웨이퍼-패드 마찰이 asperity를 소성변형·매몰시키는 속도 (슬러리·패드 의존)
  k_c  [1/min]  절삭재생률: 신품 디스크가 정격 하중·속도·duty 100%로 패드를 신품 조도로 되돌리는 속도 (패드·디스크 의존)
  G    [–]      컨디셔닝 강도 = (duty/100) · A(t_disk)             … (2)
  A    [–]      드레서 마모 배수 = exp(−t_disk/τ_aging), τ_aging=27.4 h (Γ이 이미 쓰는 pcr_decay와 같은 함수)
```

해와 초기조건 — 두 운전 체제를 문헌 프로토콜대로 구분한다:

```
R_ss   = k_c·G / (k_g + k_c·G)                                      … (3)  정상상태
R(t)   = R_ss + (R(0) − R_ss) · exp(−(k_g + k_c·G)·t)               … (4)  과도해, 시정수 1/(k_g+k_c G)
```
- **in-situ(G>0)**: 시정수 1/(k_g+k_c)=0.24 min ≪ 웨이퍼 연마시간이므로 직전 웨이퍼가 끝났을 때 패드는 이미
  R_ss 에 있다 → R(0)=R_ss, 식(4)의 과도항이 0. **S = R_ss(G)/R_ss(G_ref)** — 시간 무관, 균형비만의 함수.
- **ex-situ / 무컨디셔닝(G=0)**: 매 웨이퍼 전에 컨디셔닝해 R(0)=R_fresh=1 로 시작(Jeong 2024·2022 프로토콜).
  R(τ)=exp(−k_g τ), τ = t − t_ref (Jeong 2024 Table 1: 초기 1 min 은 접촉수 변화 없음 → t_ref=1 min 이
  기존 S 기준점이자 유도기). **S = exp(−k_g·(clamp(t,1,10) − 1))** — 기존 로그감쇠와 10 min 값이 정확히 같다.
- G→0⁺ 극한(R_ss→0)과 G=0 분기(R=1)는 불연속이지만 **다른 프로토콜**이다: 전자는 "몇 시간 동안 사실상 컨디셔닝
  없음", 후자는 "웨이퍼마다 ex-situ 재생". 코드는 duty=0 을 후자로 해석하고 notes 에 명시한다.

```
S = R_ss(G)/R_ss(G_ref)          (G>0)     기준 duty=100%·신품 디스크에서 정확히 1.0     … (5a)
S = exp(−k_g (t − t_ref))        (G=0)     t_ref=1 min 에서 정확히 1.0                    … (5b)
```

특수해 두 개가 기존 지식과 이어진다:
- **(5b)**: 기존 로그감쇠 회귀 rate = a + b·ln t (a=1.1478, b=−0.1109)의 10분 손실 22.25%를 지수형으로 옮기면
  k_g = −ln(1−0.2225)/9 = **0.02796 /min**. 10 min 값은 두 형식이 정확히 같고(§4 verify), 중간점 R²는
  지수형이 로그형보다 높다(정규화 pooled: exp 0.77 vs log 0.64) — 형식 교체로 잃는 것이 없다.
- **(5a)**: in-situ 100% duty·신품 디스크에서 R_ss=0.9932 — Entegris Case 3의 "Ra가 0.5 h 안에 평형, 이후
  17 h 정체"([[../equipment/conditioner-disk-pad-cutting-model]] §4)와 정합(시정수 0.24 min).

## 2. 파라미터 도출

| 키(base.yaml) | 값 | 도출 | 등급 |
|---|---|---|---|
| `stab_glaze_rate_per_min` k_g | 0.02796 /min | Jeong et al. 2024 (doi:10.3390/ma17081817) Fig.9 pooled 로그회귀 a=1.1478, b=−0.1109 → 10 min 손실 22.25% → k_g=−ln(0.7775)/9. 압력별 개별 적합은 2 psi 0.0223, 5 psi 0.0392 /min(±40% 밴드, 압력 지수는 2점이라 항으로 만들지 않음, §6) | literature (실리카/IC1000) |
| `stab_cond_recovery_rate_per_min` k_c | 4.08 /min | Jeong et al. 2022 ASPEN, ISBN 978-981-18-6021-8 paper OR-12-0224 (원문 PDF 확보, §6-2) §2.2: 3 psi·10 min 연마 후 **30 s** 컨디셔닝으로 완전 회복. ⚠ 이는 4점 압력 사다리(2/3/4/5 psi → 10/30/60/180 s) 중 3 psi 좌표이며 k_c는 상수가 아니다(§6-2). 회복 중(웨이퍼 없음) 식(1)은 dR/dt=k_c(1−R) → 잔여 결손 ε=exp(−k_c·0.5 min). ε는 Jeong 2024 Table 1의 컨디셔닝 복원 허용폭 **±13%**(N_cond/N_0 = 0.91~1.13, [[pad-glazing-mechanism-mrr-decay]] §4(A))로 두어 k_c=ln(1/0.13)/0.5 = 4.08 /min. 독립 하한: Jeong 2024 "1 min 컨디셔닝으로 N 0.51→1.0±0.13" → k_c ≥ ln(0.49/0.13)=1.33 /min — 4.08은 이 하한 위에 있다 | literature (IC1000, 디스크 0.7 psi·101 rpm·9 cpm) |
| `stab_glaze_rate_uncertainty_x` | 5.0 | Lawing 2004 ex-situ 감쇠: fumed −35% vs colloidal −7%(4.7배, [[pad-glazing-mechanism-mrr-decay]] §4(E)) — 슬러리를 바꿀 때 k_g가 벗어날 수 있는 폭의 문헌 상한(§5의 등급 판정에 쓴다) | literature |
| `stab_ref_time_s` | 60 s | Jeong 2024 Fig.9 첫 측정점(1 min) = 기존 S 기준 계약 그대로 | literature |
| (기준점 재사용) `cond_ref_duty_pct`=100, `cond_ref_disk_usage_hours`=0 | — | Γ의 기준 조건과 동일 물리 조건(in-situ·신품) — 별도 키를 만들면 두 팩터의 기준이 갈라진다 | literature |

## 3. 드레서 마모의 결합 — Γ과 S가 같은 A(t)를 본다

[[../equipment/conditioner-grit-wear-scratch-lifetime]] §2(Kwon 2013 Fig.1): 컨디셔닝 시간이 늘수록 패드
절삭율이 감소 — "그릿 마모로 절삭 능력이 점진적으로 저하". [[../equipment/conditioner-disk-pad-cutting-model]] §3:
PCR(t)=PCR_0·exp(−t/τ), 50 h→16%로 τ=27.4 h. Γ(장비축)은 이 A(t)를 절삭 **부하**로 곱하고, S(소모품축)는
같은 A(t)를 식(2)의 G에 넣어 **정상상태 조도**로 변환한다. 즉 드레서가 닳으면 Γ↓ 이고 그 결과로 R_ss↓ → S↓.
두 팩터가 한 함수(`sim/tier2_physics/conditioner_pcr_decay.pcr_decay`)를 공유하므로 이중 정의가 없다.

이 결합이 만드는 예측: 드레서 사용량 ↑ → S 단조감소. **MRR에 곱해지지 않는** S(MRR_COUPLED 밖)의 순위 예측이
실장비에서 맞는지가 §4 (C)의 검증이다.

## 4. 정량 재현 (python verify)

재현 요약(한 줄): (Jeong et al. 2024, doi.org/10.3390/ma17081817) 무컨디셔닝 10 min S = 0.7775 는 기존 로그감쇠
값 0.7775 와 1e−9 이내로 일치하고, k_c=4.08 /min 은 (Jeong et al. 2022) 3 psi 30 s 회복 표와 (Jeong 2024) ±13%
복원 허용폭에서 재현되며, PHM2016 실장비 477 웨이퍼에서 S 순위는 MRR 순위와 저속군 ρ=+0.696(드레서 원변수 −0.696의
부호 반전)로 대조된다.

```python verify
import json, math
from pathlib import Path
import numpy as np
from scipy.stats import spearmanr

# ── (A) k_g: Jeong 2024 Fig.9 pooled 로그회귀(기존 _f_stab 계수)의 10 min 손실을 지수형으로 이식
a, b = 1.1478, -0.1109
S10_log = (a + b * math.log(10)) / a
k_g = -math.log(S10_log) / 9.0
print(f"k_g = {k_g:.5f} /min, 로그감쇠 10 min = {S10_log:.4f}")
assert abs(k_g - 0.0279599276) < 1e-9   # base.yaml stab_glaze_rate_per_min 과 동일 정밀도
# 지수형이 중간점에서도 로그형보다 못하지 않다 (정규화 pooled, 각 압력 t=1 min 기준)
t9 = np.array([1, 2, 3, 4, 5, 7, 10.]); m2 = np.array([1.00, .975, 1.03, .975, .935, .88, .835])
m5 = np.array([1.15, 1.25, 1.185, 1.035, 1.005, .94, .87]) / 1.15
T = np.r_[t9, t9]; Y = np.r_[m2, m5]
def r2(pred): return 1 - ((Y - pred) ** 2).sum() / ((Y - Y.mean()) ** 2).sum()
k, c = np.polyfit(T, np.log(Y), 1); bb, aa = np.polyfit(np.log(T), Y, 1)
R2_exp, R2_log = r2(np.exp(c + k * T)), r2(aa + bb * np.log(T))
print(f"R² exp={R2_exp:.3f} log={R2_log:.3f}")
assert R2_exp >= R2_log, "지수형이 로그형보다 나쁘면 형식 교체 근거가 없다"
# 압력별 개별 k_g (2점뿐이라 항으로 만들지 않음 — 밴드만 기록)
kg2 = -np.polyfit(t9, np.log(m2), 1)[0]; kg5 = -np.polyfit(t9, np.log(m5), 1)[0]
print(f"k_g(2 psi)={kg2:.4f}, k_g(5 psi)={kg5:.4f} /min  (pooled {k_g:.4f} 가 두 값 사이)")
assert kg2 < k_g < kg5

# ── (B) k_c: Jeong 2022 ASPEN Table 1 (3 psi → 30 s 완전 회복) + Jeong 2024 복원 허용폭 ±13%
t_cond_min = 30 / 60; eps = 0.13
k_c = math.log(1 / eps) / t_cond_min
print(f"k_c = {k_c:.3f} /min")
assert abs(k_c - 4.08) < 0.01
# 독립 하한: Jeong 2024 Table 1, 2 psi 10 min N=56/109=0.514 → 1 min 컨디셔닝 후 114/109 (±13%)
k_c_lb = math.log((1 - 56 / 109) / eps) / 1.0
assert k_c > k_c_lb, f"k_c={k_c:.2f} 가 Jeong 2024 하한 {k_c_lb:.2f} 아래"
# 회복 중 잔여 결손 재현: 10 min 글레이징(1−0.7775) → 30 s 후
deficit = (1 - S10_log) * math.exp(-k_c * t_cond_min)
assert deficit < 0.13 * (1 - S10_log) * 1.001

# ── (C) 정상상태 S와 두 특수해 (식 5a/5b)
def S_model(t_min, duty=100.0, t_disk_h=0.0, kg=k_g, kc=k_c, tau_h=27.4, t_ref=1.0):
    G = (duty / 100) * math.exp(-t_disk_h / tau_h)
    if G <= 0:                                  # ex-situ 프로토콜: 웨이퍼마다 R(0)=1
        return math.exp(-kg * (min(max(t_min, 1.0), 10.0) - t_ref))
    rss = lambda g: kc * g / (kg + kc * g)      # in-situ: 직전 웨이퍼에서 이미 정상상태
    return rss(G) / rss(1.0)
assert abs(S_model(1.0) - 1.0) < 1e-12                       # 기준 1.0
assert abs(S_model(10.0, duty=0.0) - S10_log) < 1e-9           # duty=0 → 기존 로그감쇠 10 min 값
assert S_model(10.0, duty=50) > S_model(10.0, duty=0)          # duty↑ → S↑
assert S_model(10.0, duty=100) > S_model(10.0, duty=50)
assert S_model(10.0, t_disk_h=50) < S_model(10.0, t_disk_h=0)  # 드레서 마모 → S↓
assert 1 / (k_g + k_c) < 0.3, "in-situ 시정수가 분 단위를 넘으면 '정상상태 출발' 가정이 약해진다"
print(f"S(10min): in-situ {S_model(10):.4f}, duty50 {S_model(10, 50):.4f}, "
      f"드레서50h {S_model(10, 100, 50):.4f}, 무컨디셔닝 {S_model(10, 0):.4f}")

# ── (D) PHM2016 실장비 순위 검증 — 스케일된 데이터라 순위만 (README §쓸 수 없는 것)
rows = json.load(open(Path.home() / "fab-sim/validation/raw/phm2016/joined.json"))
d = np.array([r["dresser"] for r in rows]); m = np.array([r["mrr"] for r in rows])
assert len(rows) >= 400
rho_raw_all = spearmanr(d, m)[0]; lo = m < 120; rho_raw_lo = spearmanr(d[lo], m[lo])[0]
print(f"원변수 드레서 vs MRR: 전체 ρ={rho_raw_all:+.3f}, 저속군 ρ={rho_raw_lo:+.3f} (README −0.489/−0.696)")
assert abs(rho_raw_lo - (-0.696)) < 0.01
# 스케일 미상 → 사용량을 시간으로 바꾸는 배율 s를 여러 값으로 흔들어도 순위가 불변인지 본다
for s in (0.02, 0.05, 0.1):
    S = np.array([S_model(10.0, 100.0, (x - d.min()) * s) for x in d])
    r_all, r_lo = spearmanr(S, m)[0], spearmanr(S[lo], m[lo])[0]
    assert np.all(np.diff(S[np.argsort(d)]) <= 1e-15)          # S는 드레서 사용량에 단조감소
    assert abs(r_lo - (-rho_raw_lo)) < 1e-9 and r_lo > 0.6, f"저속군 ρ={r_lo:.3f}"
    assert r_all > 0.45
print(f"S 순위 vs MRR 순위: 저속군 ρ=+{-rho_raw_lo:.3f}, 전체 ρ=+{-rho_raw_all:.3f} — 부호·크기 재현 (스케일 무관)")

# ── (E) 슬러리 의존 k_g 불확실성(Lawing 5배)이 컨디셔닝 정상상태 S에 미치는 영향
for duty, t_disk in ((100, 0), (50, 0), (100, 50), (25, 27.4)):
    dS = abs(S_model(10, duty, t_disk, kg=5 * k_g) - S_model(10, duty, t_disk))
    print(f"duty={duty} 드레서={t_disk}h: |ΔS| under 5×k_g = {dS:.4f}")
assert abs(S_model(10, 100, 0, kg=5 * k_g) - S_model(10, 100, 0)) < 1e-12   # 기준점: k_g 가 아예 안 들어온다
assert abs(S_model(10, 50, 0, kg=5 * k_g) - S_model(10, 50, 0)) < 0.03        # duty 50%: 3% 이내
assert abs(S_model(10, 100, 50, kg=5 * k_g) - S_model(10, 100, 50)) > 0.03    # 드레서 50 h: 3% 초과 → estimated
assert abs(S_model(10, 0, 0, kg=5 * k_g) - S_model(10, 0, 0)) > 0.3   # 무컨디셔닝에서는 지배적
print("PASS: (A)~(E)")
```

실행 결과(2026-09-14): k_g=0.02796 /min(2 psi 0.0223 < pooled < 5 psi 0.0392), R² exp 0.768 vs log 0.636;
k_c=4.08 /min(하한 1.33 위); S(10 min) in-situ 1.0000 / duty 50% 0.9932 / 드레서 50 h 0.9658 / 무컨디셔닝 0.7775;
PHM2016 저속군 ρ(S, MRR)=+0.696, 전체 +0.489 — 배율 0.02·0.05·0.1 전부 동일(순위는 배율 무관);
5×k_g에서 |ΔS| = 기준점 0 / duty 50% 0.025 / 드레서 50 h 0.113 / 무컨디셔닝 0.47.

## 5. 새로 도출한 지식

1. **컨디셔닝된 공정에서 S는 시간의 함수가 아니라 균형비 k_g/(k_c·G)의 함수다.** in-situ·신품 디스크에서
   R_ss=0.9932 — 글레이징이 정상상태 조도를 0.7%만 깎는다. 기존 "10분에 −22%"는 무컨디셔닝(G=0) 특수해였고,
   그것을 in-situ 팩에 적용하던 것이 물리적 오류였다. 이 노트로 in-situ 기본 팩의 S(10 min)은 0.7775→1.0000(정상상태)으로
   바뀐다 — 정직한 지표 이동이며 회귀가 아니다.
2. **슬러리 의존성(비-실리카 갭)은 컨디셔닝 균형에서는 운전점에 따라 예측에 거의 안 들어온다.** S의 k_g
   탄성도는 d ln S/d ln k_g = k_g/(k_g+k_c G_ref) − k_g/(k_g+k_c G) 로, 기준점(G=G_ref)에서는 **정확히 0**(k_g가
   식에서 상쇄), duty 50%에서 Lawing 5배 밴드를 통째로 먹여도 |ΔS|=0.025(제품 오차 목표 3% 이내), 드레서 50 h에서는
   0.11, 무컨디셔닝에서는 0.47. → 등급 규칙(물질명 없음): **불확실 파라미터의 문헌 밴드를 관통시킨 |ΔS|를 이번
   런의 운전점에서 계산해 0.03 미만이면 그 파라미터는 약한 고리가 아니다.** `_f_stab`은 이 판정을 런타임에
   수행한다 — 비-실리카 팩이라도 컨디셔닝 균형 구간의 기준 근방에서는 k_c·A 등급(literature)을, 밴드가 3%를
   넘는 운전점·무컨디셔닝 구간에서는 판정#9대로 estimated를 낸다. 이는 등급 리터럴이 아니라 계산된 판정이다.
3. **드레서 마모는 S와 Γ에 같은 부호로 들어가며 실장비 순위를 재현한다.** 사용량 스케일이 숨겨져 있어도
   A(t)가 단조라 순위는 배율 무관 — PHM2016 저속군 ρ=+0.696은 스케일 가정 없이 얻은 값이다. 이것이 S×Γ
   경로의 유일한 실장비 검증이고, 조성 경로(κ·χ·ψ)는 이 데이터로 검증할 수 없다(README).
4. **ex-situ 회복시간 표(2/3/4/5 psi → 10/30/60/180 s)가 k_c의 압력 의존을 암시한다**: 같은 ε이면
   k_c ∝ 1/t_cond 로 18배 폭. 그러나 이는 k_c(디스크)가 아니라 **글레이징 깊이(k_g·P)가 압력에 따라 커진
   것**의 반영이다(Jeong 2022 원문: "greater pad deformation under high pressure requires longer time").
   k_c는 3 psi(기본 압력) 값으로 고정하고 압력 항은 k_g 쪽에 속한다 — 2점 데이터라 미도입(§6).

## 6. 문헌이 지지하지 않아 뺀 항·한계 (정직 기록)

- **k_g의 압력 지수**: 2 psi/5 psi 두 점(k ∝ P^0.62)뿐이고 Fig.9는 눈금 판독(±0.02). 항으로 넣지 않고
  ±40% 밴드로 기록. 압력은 Λ(장비축)의 드라이버라 S에 넣으면 축이 섞이는 문제도 있다.
- **Γ의 하중·속도 항을 G에 곱하지 않았다**: PCR ∝ F·v(Preston형)은 문헌이지만 k_c를 뽑은 조건(0.7 psi·101 rpm)이
  base 기준(4 lbf·55 rpm)과 다르고 그 환산 지수가 없다. G=duty×A만 쓴다 — 하중·속도 변화의 S 반응은 **미모델링**
  (Γ이 부하로만 담는다).
- **그릿 밀도·형상(Kwon 2013 17k/40k/60k → 37/23/19 µm/h)**: k_c의 디스크 설계 의존이 실측돼 있으나 팩에 그릿
  밀도 키가 없어 미연결. 키가 생기면 k_c ∝ PCR 비율로 붙일 수 있다(추정, 미검증).
- **Son & Lee 2021 수십시간 감쇠(2.81 vs 0.37 %/h)**: 컨디셔너 구조(swing-arm vs 분할형) 변수 부재 — 판정#8 유지.
- **PHM2016은 절대값 검증이 아니다**: 모든 컬럼이 은닉 배율로 스케일됨. 사용량→시간 배율은 미상이며 위 verify가
  세 배율에서 순위 불변임을 보인 것이지 배율을 확정한 것이 아니다.
- **비-실리카 팩의 k_g**: 판정#9대로 코퍼스에 없다. 본 노트는 그 값을 찾지 않고, 그 값의 불확실성이 예측에 미치는
  영향을 정량화해 등급을 판정한다(§5-2). 무컨디셔닝(duty=0) 구간에서 비-실리카 팩의 S는 여전히 estimated다.
- ε=0.13(복원 허용폭)은 접촉점 수 기준이고 MRR 기준 허용폭은 별도 측정이 없다 — k_c의 자릿수(1.3~6 /min)만
  확실하고 4.08은 그 안의 한 점이다(추정 요소, 등급은 도출 문헌이 1차라 literature로 두되 note에 명시).

## 6-2. [2026-09-14 부채상환] 1차 출처 확보 + k_c는 상수가 아니다

이전 판은 k_c 근거를 이 프로시딩의 DOI(접두어 10‧3850 + ISBN + 논문ID 형태)로 적었는데 **Crossref 미등록(404)**이라
`verify_claims.py`가 출처 실존 위반으로 반려해 왔다. 접두어 자체는 등록돼 있으나(Research Publishing
Services) 개별 논문 DOI가 Crossref에 색인되지 않은 학회 프로시딩이다. 원문은 발행사 공개 PDF로 확보했다:

> Jeong, Jin, Jeong, Park, Jeong (2022), "Ex-Situ Conditioning Based on Constant Material Removal Rate
> for a Digital Twin CMP System", Proc. ASPEN 2022, pp.568–570, ISBN 978-981-18-6021-8, paper OR-12-0224.
> Pusan National University. 확보 경로: `https://rpsonline.com.sg/proceedings/aspen2022/pdf/OR-12-0224.pdf`
> (Referer 헤더 필요, 없으면 HTTP 406). 로컬 사본 `papers/jeong2022-aspen-exsitu-conditioning-constant-mrr.pdf`.
> **DOI는 인용 형식으로만 쓰고 실존 검증은 ISBN+논문ID로 한다** — 해석기가 DOI를 조회하면 영구히 404다.

원문 §2.2 대조 결과 **이전 판의 인용이 부정확**했다. 실제 서술은 Table 1이 아니라 Fig.3 본문이고,
30 s는 **3 psi 한 조건의 값**이며 원문은 네 압력 전부를 보고한다:

| 연마 압력 | 충분 회복에 필요한 컨디셔닝 시간 (원문 §2.2) |
|---|---|
| 2 psi | 10 s |
| 3 psi | 30 s ← 이전 판이 쓴 유일한 점 |
| 4 psi | 60 s |
| 5 psi | 180 s |

이 사다리를 이전 판과 **같은 변환**(잔여 결손 ε=0.13까지 1차 회복)으로 돌리면 k_c가 압력에 따라
12.24 → 0.68 /min 으로 **18배** 퍼진다. 글레이징 깊이 차이를 감안한 절대 해석(결손 d₀에서 0.13까지)으로도
7.3배다. 형상 상수 판정 기준은 "데이터셋별 최적값 퍼짐 2배 초과면 상수가 아니다"이므로 **k_c는 상수가 아니라
연마 압력(정확히는 직전 글레이징 깊이)의 함수**다. 이전 판의 k_c=4.08은 틀린 값이 아니라 **3 psi 좌표**다.

판정(EVIDENCE-RULES E1 동일계 통제실측): 사다리 4점이 단일 논문·단일 장비·단일 패드에서 나온 통제 실측이라
등급이 가장 높다. 다만 **이번 회차에 항을 만들지 않는다** — 회복 시간은 원문이 "충분한가"의 이산 판정으로만
주고(연속 회복 곡선이 아님) 네 점 모두 상한이지 등량점이 아니라, 멱함수를 적합하면 관측이 지지하지 않는
형상을 창작하게 된다. 현 모델은 in-situ 정상상태 R_ss만 쓰고 그 안에서 k_c는 비의 분자·분모에 함께 들어가
민감도가 낮으므로, **3 psi 좌표를 유지하되 압력 의존을 미모델링으로 신고**한다(아래 verify 블록이 이 상태를
고정한다). 해소 조건: 회복 곡선(시간 연속)을 보고한 문헌 1건. 담당 R3-pad, 구현 요청 대상.

```python verify
import math
# Jeong 2022 ASPEN OR-12-0224 §2.2 — 원문에 인쇄된 네 점(압력 psi → 충분 회복 컨디셔닝 시간 s)
T_REQ_S = {2: 10.0, 3: 30.0, 4: 60.0, 5: 180.0}
EPS = 0.13                      # Jeong 2024 Table 1 복원 허용폭(접촉점 수 기준)
# 이전 판이 k_c=4.08을 뽑은 변환을 그대로 네 점에 적용한다
kc = {p: math.log(1 / EPS) / (t / 60.0) for p, t in T_REQ_S.items()}
assert abs(kc[3] - 4.08) < 0.01, f"3 psi 재현 실패: {kc[3]:.3f}"   # 기존 값은 3 psi 좌표
spread = max(kc.values()) / min(kc.values())
assert spread > 2.0, "퍼짐이 2배 이하면 상수로 둬도 된다"
assert 17.0 < spread < 19.0, f"퍼짐 {spread:.1f}배 — 기대 18배"
# 글레이징 깊이를 보정한 절대 해석으로도 상수가 아니다
KG = {2: 0.0223, 5: 0.0392}     # §2 압력별 k_g 적합 (/min)
kc_abs = {p: math.log((1 - math.exp(-KG[p] * 9.0)) / EPS) / (T_REQ_S[p] / 60.0) for p in KG}
assert kc_abs[2] / kc_abs[5] > 2.0, "깊이 보정 후에도 2배를 넘어야 '상수 아님' 결론이 선다"
# 단조성: 압력이 높을수록 회복이 느리다(원문 결론과 같은 방향)
assert all(kc[p] > kc[q] for p, q in zip([2, 3, 4], [3, 4, 5])), "압력-회복속도 단조 감소가 깨짐"
print(f"k_c(2..5 psi) = {[round(kc[p], 2) for p in (2,3,4,5)]} /min · 퍼짐 {spread:.1f}배")
print("→ k_c는 상수가 아니다. 3 psi 좌표만 채택하고 압력 의존은 미모델링으로 신고한다.")
```

## 7. 출처 요약

- Jeong, Shin, Jeong, Jeong, Jeong (2024), Materials 17(8) 1817, doi:10.3390/ma17081817 (PMC11051262) — Table 1, Fig.9.
- Jeong, Jin, Jeong, Park, Jeong (2022), "Ex-Situ Conditioning Based on Constant Material Removal Rate for a Digital Twin CMP System", Proc. ASPEN 2022 pp.568-570, ISBN 978-981-18-6021-8, paper OR-12-0224 — §2.2. ⚠ 이 프로시딩의 DOI는 Crossref 미등록(404)이므로 인용에 쓰지 말고 ISBN+논문ID로 식별하라. 1차 원문: papers/jeong2022-aspen-exsitu-conditioning-constant-mrr.pdf
- Lawing (2004), NCCAVS CMPUG, "Ex Situ Rate Decay" — fumed/colloidal 감쇠비.
- Kwon, Ramachandran, Cho, Busnaina, Park (2013), Tribology International 67, 272, doi:10.1016/j.triboint.2013.08.008 — Fig.1.
- Shi & Ring (2010), population balance with fluid load sharing — 정상상태 존재 (2차 서술, [[pad-wear-glazing-mrr-decay]]).
- Entegris Case Study (Planargem) 50 h→16% PCR 앵커 — 2차 인용, τ=27.4 h (Γ과 공유, 등급 하한 사유 그대로).
- PHM Society 2016 Data Challenge — `validation/raw/phm2016/README.md`, 미러 github.com/akangel0307/PHM-Data-Challenge.
