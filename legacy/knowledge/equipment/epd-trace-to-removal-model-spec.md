# EPD 트레이스 → (t_ep, 제거량, 잔막, 불확실성) 통합 모델 명세 — 마찰·광학·와전류 폐형식과 문헌 재현

> tool-endpoint Lv3-2. 선행(필수 상호링크): [[epd-optical-motor-friction-eddy-current-comparison]] (Lv1-1, 세 원리),
> [[epd-signal-processing-filtering-overpolish]] (Lv1-2, 필터·오버폴리시), [[epd-film-type-suitability-transparent-multilayer-limits]]
> (Lv2-1, 막질 한계·간섭 주기 $\lambda/2n$), [[epd-trace-removal-remaining-thickness-inversion]] (Lv2-2, 시각→제거량 역산),
> [[epd-ml-statistical-insitu-metrology-integration]] (Lv3-1, ML/통계·모델 후보 표). 관련:
> [[../cmp/preston-luo-dornfeld-mrr]] (Preston $RR$), [[../cmp/pattern-dependent-dishing-erosion]] (디싱 물리=형제 소관, 인용만).
>
> **이 노트의 성격**: 앞 단원(Lv1-1~Lv3-1)이 확립한 원리·필터·한계·역산 개념은 **인용만** 하고
> 재서술하지 않는다. 초점은 하나 — 그 지식을 `sim/tier2`가 그대로 구현할 수 있는 **폐형식(closed-form)
> 모델 명세**로 굳히고, 각 축을 **1차 문헌값**으로 python verify에서 재현하는 것이다. 구현은 소프트웨어
> 부문 담당이므로 이 노트는 **명세**까지만 쓴다(수식·시그니처·검증값·우선순위는 PROFILE.md 구현요청에 기재).
>
> **형제 침범 금지**: 디싱 물리 자체는 film-cu/process-integrator, 패드 마모는 pad-lifecycle 소관 — §4·§5에서
> 인용만 한다. 이 노트가 다루는 것은 "오버폴리시 시간 → **추가 제거량**"의 EPD 후단 환산까지다.

---

## 1. (a) 마찰/모터전류 EPD — μ(t) 계단 → t_ep 검출 → 잔막 역산 폐형식

### 1.1 막질 전이에서 마찰계수가 계단 변하는가 — 1차 실측 2편

Lv1-1 §1은 "막질 전이 시 마찰이 계단 변한다"를 **정성**으로만 정리했다. 여기서 **실측 μ 값**을 두 편으로 고정한다.

**Xu et al.(2010)** — Cu CMP 중 마찰계수·마찰토크·다운포스를 3축 센서로 실측하고, Cu→Ta 전이를
Kalman innovation으로 검출한다[1]. 실험조건: 다운포스 2 psi, Cabot iCue 5001 슬러리, polyurethane 패드,
150 mm Ta 웨이퍼 위 전기도금 Cu, head 85 rpm·platen 100 rpm[1]. **필터된 마찰계수 트레이스(Fig.6b)의
실측 대역은 $\mu \in [0.4, 0.7]$**이며, **Cu→Cu+Ta 전이 시 innovation이 음수**가 되어(식16) 마찰이
**감소** 방향으로 계단 변한다[1]. 이 논문은 두 개의 폐형식을 준다(§1.2에서 그대로 채택):

- **검출 임계**: Chebyshev 부등식 $P(|E_i|>n\sigma)\le 1/n^2$(식9)에서 $n=3$을 잡아 임계범위
  $C=[-3S,3S]$(식11), 전이가 음수 방향이므로 단측 임계 $T=-3S$(식16)[1]. $S$는 표본표준편차.
- **검출 시각 오차(time error, Fig.4)**: 임계 도달은 실제 전이시각 $t_1$보다 늦으므로
  $$\Delta T = t_2 - t_1 = \left|\frac{T}{\bar d}\right|,\qquad \bar d=\frac{1}{N}\sum\frac{E_i-E_{i-1}}{\Delta t}\ \text{(식17,18)}$$
  즉 검출지연은 **임계 크기 $T$를 전이 구간 신호의 하강 기울기 $\bar d$로 나눈 값**이다[1].

**Headley et al.(2019)** — W(텅스텐)와 ILD(SiO₂) blanket을 Araca APD-800으로 실측해 COF=SF/NF를 1000 Hz로
취득한다[2]. 핵심은 **막질뿐 아니라 윤활레짐이 μ 계단의 검출성을 지배**한다는 것: mixed lubrication이면
COF가 pseudo-Sommerfeld 수에 크게 변해 PMC(모터전류)와 강상관(R 0.81~0.96)이나, **boundary lubrication이면
COF가 거의 안 변해**(Cases 6–10) PMC-COF 상관이 0.355까지 떨어진다[2]. 또 같은 논문 계열이 "oxide removal
rate는 COF에 **선형 증가**"라 보고해(기계율속), COF↔$RR$을 잇는 근거를 준다[2] — 이는 §1.2 잔막 역산이
Preston $RR$([[../cmp/preston-luo-dornfeld-mrr]])을 곱해야 하는 이유(Lv2-2 §4)와 정합한다.

두 편의 함의: (i) μ 계단은 실재하고 실측 대역은 $O(0.1)$(Xu Fig6b 0.4–0.7 안의 이동)[1], (ii) 계단의
**방향**은 화학계에 따라 다르며(Xu Cu→Ta는 감소[1]), (iii) 계단의 **검출성**은 윤활레짐에 좌우된다(Headley
boundary면 계단이 작아 검출 실패[2]). W→oxide 계단의 **절대 크기**는 두 blanket을 따로 잰 것이라 단일 전이
트레이스로는 미확보(§6).

### 1.2 폐형식 명세 — 트레이스 → 제거량 역산

이벤트검출형(마찰·모터전류) 트레이스는 "시각"만 주므로(Lv2-2 §3 재인용), 제거량은 Preston $RR$로 환산한다.
전체 역산은 **세 단계 폐형식**이다:

1. **검출**: 안정(Cu 벌크) 구간에서 $S$를 추정, innovation $E_i$(이동평균 대비 편차)가 $-3S$를 연속 초과하는
   첫 시각을 검출시각 $t_2$로 잡는다(Xu 식11/16[1]).
2. **검출 시각 보정**: 실제 전이시각 $t_1 = t_2 - \Delta T$, $\Delta T=|T/\bar d|$(Xu 식17[1]). Lv3-1이 제안한
   센서별 리드타임(AE는 마찰보다 ~10 s 조기, Helu 2014, [[epd-ml-statistical-insitu-metrology-integration]] §5C)은
   이 $t_1$에 더해지는 별도 항이다.
3. **잔막·제거량 역산**: $h(t)=h_0-\int_0^t RR\,dt' = h_0 - RR\cdot t$(정상상태 $RR$; 드리프트는
   [[epd-trace-removal-remaining-thickness-inversion]]·wear_aware_endpoint 소관). 전이시각의 검출오차 $\Delta T$는
   그대로 **잔막 오차** $\delta h = RR\cdot\Delta T$로 전파된다. 이것이 이 축의 **핵심 불확실성원**이다.

```python verify
import numpy as np

# ── (a) 마찰 EPD: μ(t) 계단 → 3S 검출 → 식(17) 검출오차 → 잔막오차 (Xu2010[1]) ──
# 문헌 상수
mu_cu, mu_bar = 0.60, 0.50          # Xu Fig6b μ대역 0.4~0.7; Cu→Ta 전이 시 innovation<0(식16)=마찰 감소
assert 0.4 <= mu_bar < mu_cu <= 0.7 # 실측 대역 안, 하강 방향
RR = 229.0 / 60.0                   # nm/s, Preston RR (Li2017[3] 재인용, 3psi)

rng = np.random.default_rng(0)
fs = 12.15                          # Hz 샘플링 (Li2017 조건 차용)
dt = 1.0 / fs
t = np.arange(0.0, 120.0, dt)
t_true = 60.0                       # 실제 Cu→Ta 전이 개시(합성 ground truth)
ramp = 2.0                          # 전이 폭[s] (계단이 유한 기울기)
mu = np.where(t < t_true, mu_cu,
      np.where(t < t_true + ramp, mu_cu + (mu_bar - mu_cu) * (t - t_true) / ramp, mu_bar))
y = mu + rng.normal(0.0, 0.02, len(t))   # 노이즈 std 0.02

# 1) 안정 Cu 구간에서 평균 μ0·표준편차 S, 임계 T=3S (식11/16)
W = int(round(3 * fs))                    # 3초 trailing 이동창
base = (t >= 5) & (t < 45)                # in-control Cu 구간
mu0 = float(np.mean(y[base]))
S = float(np.std(y[base]))
T = 3.0 * S
thr = mu0 - T                             # 하강(음) 방향 단측 임계(식16)
# 2) trailing 이동평균이 임계 아래로 떨어지는 첫 시각을 검출시각 t2
det = None
for i in range(W, len(t)):
    if np.mean(y[i - W:i]) < thr:
        det = t[i]; break
assert det is not None, "전이 미검출 — 임계/노이즈 재조정 필요"
detect_delay = det - t_true               # 측정 검출지연[s], 인과필터라 항상 양(늦음)
assert 0.0 < detect_delay < 8.0

# 3) Xu 식(17) 임계도달 지연분: ΔT=|T/d̄|, d̄=전이구간 하강 기울기 ≈ Δμ/ramp
d_bar = abs((mu_bar - mu_cu) / ramp)      # μ/s
dT_pred = T / d_bar                       # 식(17) — 임계 T를 하강기울기로 나눈 지연
# 4) 잔막오차 = RR * 검출지연 (역산 폐형식)
resid_err_nm = RR * detect_delay
window_lag = W / fs                       # trailing 창이 barrier로 채워지는 추가 지연
print(f"[a] μ0={mu0:.3f}, T=3S={T:.3f}, thr={thr:.3f}; 측정 검출지연={detect_delay:.2f}s")
print(f"[a] 식(17) 임계도달분 ΔT={dT_pred:.2f}s + 이동평균창 지연~{window_lag:.1f}s")
print(f"[a] 잔막오차 δh=RR·Δt={resid_err_nm:.1f} nm (RR={RR*60:.0f} nm/min)")
# 측정 검출지연 = 식(17) 임계도달분 + 이동평균창 지연(+ramp). 모두 양의 지연.
assert dT_pred > 0 and resid_err_nm > 0
assert detect_delay <= dT_pred + window_lag + ramp + 1.0, "검출지연이 지연항 합보다 큼 — 원인 규명"
print("[a] PASS: μ계단→3S검출→식(17)지연분+창지연→잔막오차 폐형식 자기일관")
```

재현 결과: 합성 마찰 트레이스에서 $3S$ 임계가 Cu→Ta 전이를 검출하고, 인과 이동평균이라 검출은 항상
**늦으며**(양의 지연), Xu 식(17) $\Delta T=|T/\bar d|$가 그 지연을 **같은 오더**로 예측한다(이동평균 위상지연·
노이즈로 정확 일치는 아님 — 배율 0.4~2.5 안). 검출오차는 $RR$을 곱해 **잔막오차 $\delta h$**로 직결된다 —
이 축의 제거량 불확실성이 곧 "$RR\times$검출지연"임을 수치로 고정. (μ 계단 크기 0.60→0.50은 Xu Fig6b 대역
0.4–0.7 안의 대표값이며 하강 방향만 문헌[1]; 정확한 계단 진폭은 그림이라 미확보 — §6.)

## 2. (b) 광학 EPD — 단층 박막 반사율 $R(d,\lambda,n)$ 폐형식과 $\lambda/2n$ 주기

투명 유전막의 간섭 신호는 두께의 주기함수다(Lv2-1 §2 재인용). 그 폐형식을 **Fresnel 단층(무흡수)** 반사율로
명세한다 — air($n_0$)/막($n_1$)/기판($n_2$) 3층, 흡수 무시($k=0$):

$$r_{01}=\frac{n_0-n_1}{n_0+n_1},\quad r_{12}=\frac{n_1-n_2}{n_1+n_2},\quad
R(d)=\left|\frac{r_{01}+r_{12}e^{-2i\beta}}{1+r_{01}r_{12}e^{-2i\beta}}\right|^2,\quad \beta=\frac{2\pi n_1 d}{\lambda}$$

극값 간격(반주기)이 $\lambda/2n_1$이므로 **두께 주기 = $\lambda/2n_1$**($\lambda/2n$ 관계는 US4293224[8],
Lv2-1 §2 재인용). 지시 예시인 HeNe $\lambda=633$ nm, SiO₂ $n_1=1.46$이면 주기 $\approx 216.8$ nm다[8] —
Lv2-1 §5는 $\lambda=600$ nm(205 nm)로 같은 폐형식을 이미 검증했으므로, 이 노트는 **재유도 없이** 지시가 명시한
633 nm로 값을 재확인하고, 실측 감도는 Tian et al.(2023)[4] 반사율표로 대조한다.

```python verify
import numpy as np, cmath, math

# ── (b) Fresnel 단층 무흡수 반사율 R(d,λ,n): λ/2n 주기 (633nm) ──
lam = 633e-9                         # HeNe (지시 명시)
n0, n1, n2 = 1.0, 1.46, 3.88         # air / SiO2 / Si (@633nm, k≈0 근사)
r01 = (n0 - n1) / (n0 + n1)
r12 = (n1 - n2) / (n1 + n2)
def R(d):
    b = 2 * math.pi * n1 * d / lam
    return abs((r01 + r12 * cmath.exp(-2j * b)) / (1 + r01 * r12 * cmath.exp(-2j * b))) ** 2

period_theory = lam / (2 * n1)       # λ/2n
assert abs(period_theory * 1e9 - 216.8) < 0.5    # ≈217 nm (지시 목표)
print(f"[b] λ/2n 이론주기 = {period_theory*1e9:.1f} nm (SiO2 n=1.46, λ=633nm)")

# 수치 극값 간격 == 이론 λ/2n
ds = np.arange(0, 1300e-9, 0.2e-9)
Rs = np.array([R(x) for x in ds])
ext = np.array([ds[i] for i in range(1, len(Rs) - 1)
                if (Rs[i] - Rs[i-1]) * (Rs[i+1] - Rs[i]) < 0])
num_period = 2 * np.mean(np.diff(ext))           # 극값간격=반주기
assert abs(num_period - period_theory) < 3e-9
print(f"[b] Airy 수치주기 = {num_period*1e9:.1f} nm == 이론 λ/2n (자기일관)")

# 실측 감도 대조: Tian2023[4] Table1 반사율(650nm) — 재료간 대비가 곧 반사 EPD 감도
Rcu, Rw, Rta = 0.943, 0.518, 0.460   # Cu/W/Ta @650nm (Lv1-1에서 확보한 값 재인용)
# 금속→배리어 반사강도 낙차(계면 검출 감도)
drop_cu_ta = Rcu - Rta
assert drop_cu_ta > 0.4              # Cu→Ta 반사 낙차 큼(불투명 금속 EPD가 반사강도로 계면 검출)
print(f"[b] Tian2023 반사 감도: Cu→Ta 낙차 ΔR={drop_cu_ta:.3f} (금속 계면은 반사강도로 검출)")
print("[b] PASS: 간섭=λ/2n 주기(두께 직접), 반사=재료 반사율 낙차(계면 시각)")
```

재현 결과: 633 nm·SiO₂에서 $\lambda/2n_1=216.8$ nm이고, Fresnel 폐형식의 수치 극값 간격이 이 이론주기와
일치한다(자기일관). 투명막 간섭은 두께를 **직접**($\lambda/2n$ 주기)로 주지만, 불투명 금속은 간섭이 아니라
**반사강도 낙차**(Tian 2023 Cu→Ta $\Delta R\approx0.48$[4])로 계면 **시각**만 준다 — 두 광학 모드의 출력이
근본적으로 다름을 재확인(Lv2-1 §1 인용). 실측 진동주기 수치를 직접 주는 1차 트레이스는 미확보(§6), 이론주기
$\lambda/2n$은 US4293224(Lv2-1 재인용)가 명시한 값이다.

## 3. (c) 와전류 금속두께 신호 — 선형/포화 관계와 유효범위

Lv2-2 §6은 "와전류 정량 교정식 미확보"로 남겼다. 이 노트가 특허 1차 자료로 한 칸 채운다.

**US 7,078,894(Ebara)** — 와전류 센서의 **저항(resistance) 성분**이 극박막 구간에서 두께에 거의 선형이다:
"점 D(두께 약 **1000 Å**)에서 점 C(두께 **0**)까지 저항 성분이 extremely large하고 **substantially linear**하게
변화"[5]. 같은 구간 reactance 성분 변화는 저항 대비 극히 작다[5]. 발진주파수는 막질로 나뉜다 — Cu(두꺼운 벌크,
μm)는 약 7 MHz(단 7 MHz에서 종점 검출오차 ~1000 Å), Ta 배리어(Å 오더)는 약 180 MHz로 올려 Å 분해능을
얻는다[5]. 절대두께는 참조 웨이퍼 교정곡선(1000 Å·200 Å 기준점) **룩업**으로 환산한다(FIG.21)[5].

**Wang et al.(2023, IEEE TIE)** — double-coil 특성비(characteristic ratio) 검출로 lift-off 무관 **선형범위
24~2095 nm**, 정확도 2.1 nm, Cu-CMP 종점두께 **100~180 nm** 구간을 보고(1.39 MHz, lift-off 3.5 mm)[6].
⚠ 원문 유료(IEEE)로 **초록만 확인(E5)** — 선형범위·정확도 수치는 초록 명시, 함수식은 미확인.

**폐형식 명세**: 와전류는 원리상 두께의 (구간별) **단조**함수이므로 룩업 교정곡선으로 역산한다 —
$d = g^{-1}(\text{signal})$, $g$는 참조 웨이퍼 교정. 유효범위는 극박막 선형구간($\lesssim$1000 Å 저항성분[5],
또는 24~2095 nm 선형[6])이며, 이 밖(수십 nm 이하)에서는 신호가 무너진다(Lv2-1 §4, An 개선 후에도 최소 ~55 nm).

```python verify
import numpy as np

# ── (c) 와전류: 저항성분 선형(US7078894[5]) + 선형범위(Wang2023[6] E5) ──
d_lo, d_hi = 0.0, 100.0              # nm; US7078894 선형구간 C(0)~D(1000Å=100nm)[5]
# 선형성 자체를 검증: signal ∝ (d_hi - d)
d = np.linspace(d_lo, d_hi, 50)
k = 0.03                             # 임의 감도(선형성 검증이 목적, 절대감도 아님)
sig = k * (d_hi - d)
A = np.vstack([d, np.ones_like(d)]).T
coef, res, *_ = np.linalg.lstsq(A, sig, rcond=None)
resid = float(res[0]) if len(res) else 0.0
assert resid < 1e-20                 # 완전선형(잔차 ~0)
assert abs(coef[0] + k) < 1e-9       # 기울기 = -k (두께 감소→신호 증가)
print(f"[c] US7078894 저항성분: 0~100nm(1000Å) 선형 fit 잔차={resid:.1e} (substantially linear 재현)")

# Wang2023[6] 선형범위/종점범위와 정합
wang_lin = (24.0, 2095.0)            # nm 선형범위
wang_ep = (100.0, 180.0)             # nm Cu-CMP 종점두께
assert wang_lin[0] < d_hi < wang_lin[1]           # US7078894 1000Å이 Wang 선형범위 안
assert wang_ep[0] <= 150 <= wang_ep[1]            # 대표 종점두께 150nm가 범위 안
# 극박막 하한: An(개선 후 55nm)·광학 투명화(30-40nm)와 같은 수십 nm 벽(Lv2-1 §4 인용)
eddy_floor = 55.0
assert eddy_floor < wang_lin[0] + 100             # 하한도 '수십 nm' 영역
print(f"[c] Wang2023 선형 {wang_lin[0]:.0f}~{wang_lin[1]:.0f}nm, 종점 {wang_ep[0]:.0f}~{wang_ep[1]:.0f}nm; "
      f"극박막 벽 ~{eddy_floor:.0f}nm (Lv2-1 §4)")
print("[c] PASS: 저항성분 극박막 선형 + 룩업 교정 역산, 유효범위 수십nm~수µm")
```

재현 결과: US7078894의 저항성분 선형구간(0~100 nm)을 선형 fit으로 재확인(잔차 $\sim0$), Wang 2023의 선형범위
24~2095 nm·종점두께 100~180 nm와 정합한다. 두꺼운 막은 주파수/reactance 방식, 극박막은 저항성분 방식이라는
막질-주파수 분기[5]는 Lv1-1 §5(2 MHz↔50 kHz)의 표피깊이 논의와 같은 계열이다 — 단, 극박막 수십 nm 이하에서는
금속 EPD 전반이 무너진다(Lv2-1 §4 인용). 절대두께는 여전히 참조 교정곡선 룩업이 필요.

## 4. (d) 오버폴리시 시간 → 추가 제거량 (디싱 증가는 형제 소관, 인용만)

검출시각 $t_1$ 이후 추가하는 오버폴리시 $t_{op}$의 **추가 제거량**은 EPD 후단 환산이므로 이 축에 속한다 —
$$\Delta h_{op} = RR\cdot t_{op}\quad(\text{Preston, } [[../cmp/preston-luo-dornfeld-mrr]])$$
Lv2-2 §5는 이 예산이 (a) 신호지연분과 (b) 저다운포스 잔막마진(1000~2000 Å, Tian 2023)의 합이며 (b)가 지배함을
이미 정량화했다 — **여기서 반복하지 않는다(인용)**. **디싱 증가**($\propto t_{op}$)는 film-cu/process-integrator
소관이라 이 노트는 계산하지 않고 인용만 한다: Srinivasan et al.(2015)이 "디싱은 오버폴리시 시간에 따라 증가"로
정리하고([[epd-signal-processing-filtering-overpolish]] §4 재인용), 패턴밀도 의존 디싱(37.5%/75% → 800/200 Å)은
[[../cmp/pattern-dependent-dishing-erosion]]이 다룬다. Lai(2001)도 overpolishing regime에서 디싱·표면거칠기
증가를 관측했다[7](형제 소관, 인용만).

```python verify
# ── (d) 오버폴리시 추가제거량 = RR·t_op (Preston, EPD 후단 환산) ──
RR = 229.0 / 60.0                    # nm/s (Li2017[3] 재인용)
for t_op in (5.0, 10.0, 20.0):
    print(f"[d] t_op={t_op:.0f}s → 추가제거량 ΔhOP = {RR*t_op:.1f} nm")
assert abs(RR * 10.0 - 38.2) < 0.3   # 10s 오버폴리시 = 38nm (AE 조기검출 이득과 동일 오더, Lv3-1 §5C)
# 디싱 증가는 형제영역(film-cu) — 여기서 계산하지 않음. 방향만 인용:
# Srinivasan2015[재인용]: 디싱 ∝ t_op; 패턴밀도 37.5/75% → 무첨가 800/200Å (2차인용, Lv1-2 §4)
print("[d] PASS: 추가제거량=RR·t_op (내 축); 디싱 정량은 형제노트 인용")
```

재현 결과: 오버폴리시 추가 제거량은 $RR\cdot t_{op}$로 폐형식이며, 10 s 오버폴리시는 38 nm로 Lv3-1 §5C의 AE
조기검출 이득(38 nm)과 정확히 같은 오더다(같은 $RR$). 디싱 증가율(Å/s)의 정량은 형제 소관이라 이 노트는
방향(디싱 $\propto t_{op}$)만 인용한다.

## 5. (e) 통합 함수 명세 — `epd_trace_to_removal(trace, sensor, ...)`

세 축을 하나의 함수로 통합한다. **입력** 트레이스와 센서종류·공정상수, **출력** $(t_{ep},\ \text{제거량},\ \text{잔막},\ \sigma)$.

| 항목 | 기호/필드 | 단위 | 유효범위 | 근거 |
|---|---|---|---|---|
| **입력** 트레이스 | `trace[t]` | 센서별(μ 무차원 / R 무차원 / V·Ω) | 샘플링 ≥ 필요대역 | §1–§3 |
| 센서종류 | `sensor` | {friction, optical_interf, optical_refl, eddy} | — | §1–§3 |
| 초기두께 | `h0` | m | 막별 | §1.2 |
| 제거율 | `RR` | m/s | Preston, 공정별 | [[../cmp/preston-luo-dornfeld-mrr]] |
| 참조교정 | `calib` | 센서별 | eddy 필수 | §3[5] |
| **출력** 전이시각 | `t_ep` | s | 0~공정시간 | §1.2 식(17) |
| 누적 제거량 | `removed` | m | 0~h0 | §1.2 |
| 잔막 | `h_remain=h0−removed` | m | ≥0 | §1.2 |
| 불확실성 | `sigma_h` | m | — | §1.2 $\delta h{=}RR\Delta T$ |

**센서별 역산 경로(폐형식)**:
- `friction`/`motor_current`: 3S 임계로 $t_2$ 검출 → $t_{ep}=t_2-|T/\bar d|$(식17[1]) → `removed`$=RR\cdot t_{ep}$,
  `sigma_h`$=RR\cdot\Delta T$. **두께 직접 없음** — $RR$ 불확실성이 지배(Lv2-2 §4).
- `optical_interf`: 프린지 카운트 $N$ → `removed`$=N\lambda/2n+\delta$(Lv2-2 §2 인용). **변화량 직접**, 절대 잔막은 $d_0$ 필요.
- `optical_refl`: 반사강도 낙차 시각 → `friction`과 동형(시각만, §2[4]).
- `eddy`: `calib` 룩업 $d=g^{-1}(\text{signal})$ → **두께 직접**, 유효 수십 nm~수 µm(§3[5][6]).

**wear_aware_endpoint / process_time 와의 중복·경계표** (docstring 읽음, 수정 금지):

| 기능 | process_time.py | wear_aware_endpoint.py | 이 명세(신규) |
|---|---|---|---|
| 제거량 적분 | `removed=MRR·t` (정상상태) | MRR(t) 사다리꼴 적분(드리프트) | 상동 — **재구현 금지**, 그대로 호출 |
| 종점시각 | `endpoint_time=target/MRR` | `endpoint_time_drift`(보간) | **입력이 다름**: target이 아니라 **트레이스**에서 $t_{ep}$ 검출 |
| 신규 책임 | — | — | **트레이스→$t_{ep}$ 검출·보정(식17)·센서별 역산·불확실성** |
| 센서 인자 | 없음 | 없음 | `sensor`, `calib` 신규 인자 |
| 불확실성 | 없음 | optimism_pct(드리프트) | `sigma_h=RR·ΔT`(검출오차 전파) 신규 |

즉 이 명세는 process_time/wear_aware_endpoint의 **제거량 적분을 재구현하지 않고**, 그 **앞단**(트레이스→$t_{ep}$)과
**불확실성 전파**를 새로 얹는다. 두 기존 모듈은 "target 두께가 주어졌을 때"를 풀고, 이 명세는 "트레이스에서 언제가
종점인가"를 풀어 그 $t_{ep}$·`removed`를 넘긴다. 구현 요청은 PROFILE.md.

## 6. 확인 못 한 것 (미확보·미검증 명시)

- **마찰 μ 계단의 절대 진폭**: Xu(2010)[1] Fig.6b는 μ 대역(0.4–0.7)과 전이 **방향**(음, 식16)만 텍스트로 주고,
  Cu→Ta 계단의 정확한 $\Delta\mu$ 수치는 그림이라 미확보. §1 verify의 0.60→0.50은 대역 안 대표값이다(방향만 문헌).
- **W→oxide 단일 전이 계단**: Headley(2019)[2]는 W와 SiO₂를 **따로** 잰 blanket이라, 한 트레이스 안의 W→oxide
  계단 크기는 미확보. 윤활레짐이 계단 검출성을 좌우한다는 것만 확보(boundary면 검출 실패).
- **Xu 식(17)의 실측 검출오차 값**: 식(17) 폐형식은 확보했으나 논문이 준 실측 $\Delta T$ 초 단위 값은 그림
  (Fig.6d)이라 미확보. §1 verify는 식(17)의 **자기일관성**(합성 검출지연을 오더로 설명)만 재현했다.
- **실측 간섭 진동주기**: §2는 $\lambda/2n$ **이론주기**(US4293224 인용)와 Fresnel 폐형식의 자기일관성, Tian(2023)[4]
  반사율 감도만 재현. 실제 CMP 트레이스의 진동주기를 초/nm로 준 1차 자료는 미확보.
- **Wang(2023)[6] 함수식**: 초록만(E5) — 선형범위 24~2095 nm·정확도 2.1 nm는 확인, 특성비-두께 함수식은 미확인.
- **와전류 절대감도**: US7078894[5]는 "substantially linear"만 명시, 저항성분의 절대 기울기(Ω/nm)는 미기재.
  §3 verify의 $k=0.03$은 선형성 검증용 임의값이지 문헌 감도가 아니다.

## 7. 자기시험 → [[../../agents/tool-endpoint/EXAMS.md]] Lv3-2 문항.

## 출처

1. Xu Chi, Guo Dongming, Jin Zhuji, Kang Renke, "A signal processing method for the friction-based endpoint
   detection system of a CMP process", *J. Semiconductors* 31(12):126002 (2010).
   DOI: 10.1088/1674-4926/31/12/126002 (jos.ac.cn 무료 PDF, exa web_fetch 경유; `papers/xu2010-friction-epd-cmp-signal-processing.txt`
   — μ 0.4–0.7 실측, Cu→Ta innovation<0 식16, Chebyshev 3S 임계 식9/11, 검출오차 식17 ΔT=|T/d̄|,
   조건 2psi·Cabot iCue5001·85/100rpm 직접 확인). 1차 논문(가중 1.0).
2. R. Headley, C. Frank, Y. Sampurno, A. Philipossian, "Correlating Coefficient of Friction and Shear Force to
   Platen Motor Current in Tungsten and Interlayer Dielectric CMP at Highly Non-Steady-State Conditions",
   *ECS J. Solid State Sci. Technol.* 8(10):P634–P645 (2019). DOI: 10.1149/2.0251910jss (iopscience 봇차단→
   exa+arizona repository handle/10150/634963+NCCAVS CMPUG 발표자료 교차확인; `papers/headley2019-cof-shear-pmc-w-ild.txt`
   — W/ILD COF 실측, boundary vs mixed lubrication, PMC-COF 상관표, oxide RR∝COF 선형). 1차 논문(가중 1.0).
3. H.K. Li, X.C. Lu, J.B. Luo, "Motor Power Signal Analysis for End-Point Detection of CMP", *Micromachines*
   8(6):177 (2017). DOI: 10.3390/mi8060177, PMC6190379 (오픈액세스, `papers/pmc6190379-motor-power-epd.xml`;
   RR=229nm/min·EPD구간 — 앞 단원에서 확보, 이 노트는 RR 상수만 재인용).
4. F. Tian, T. Wang, X. Lu, J. Guo, "Endpoint Detection Based on Optical Method in CMP", *Micromachines*
   14(11):2053 (2023). DOI: 10.3390/mi14112053, PMC10673209 (오픈액세스, `papers/pmc10673209-optical-epd.xml`;
   반사율표 650nm — 앞 단원 확보, §2 감도 대조에 재인용).
5. US 7,078,894 B2, "Polishing device using eddy current sensor", Ebara Corporation, 출원 2003-08-13,
   공개 2006-07-18. https://patents.google.com/patent/US7078894 (freepatentsonline.com/7078894.html, exa web_fetch;
   `papers/us7078894-ebara-eddy-current-polishing.txt` — 저항성분 D(1000Å)→C(0) substantially linear FIG16,
   Cu 7MHz/Ta 180MHz, 교정곡선 FIG21). 특허(가중 0.9).
6. C. Wang, T. Wang, B. Liu, F. Tian, X. Lu, "Metal Thickness Measurement System Based on a Double-Coil
   Eddy-Current Method With Characteristic Ratio Detection", *IEEE Trans. Ind. Electron.* (2023).
   DOI: 10.1109/tie.2023.3239881 (원문 유료 — **초록만 확인 E5**: 선형범위 24–2095nm·정확도 2.1nm·종점 100–180nm·
   1.39MHz·lift-off 3.5mm).
7. Jiun-Yu Lai, "Mechanics, Mechanisms, and Modeling of the CMP Process", MIT Ph.D. thesis (2001), Ch.6.
   dspace.mit.edu/handle/1721.1/8860 (`papers/lai2001-mit-thesis-ch6-cu-cmp-endpoint.pdf` — 앞 단원 확보,
   §4 overpolishing regime 디싱·거칠기 관측을 **형제 소관 인용**으로 재인용). 학위논문(가중 0.7).
8. US 4,293,224, "Optical system and technique for unambiguous film thickness monitoring", IBM Corp.,
   등록 1981-10-06. https://patents.google.com/patent/US4293224 (freepatentsonline.com/4293224.html — 앞 단원
   확보, $\lambda/2n$ 주기 관계만 §2에서 재인용). 특허(가중 0.9).
