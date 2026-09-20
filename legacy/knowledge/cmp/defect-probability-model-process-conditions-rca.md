<!-- V2-SECTION: Lv3-2 | 작성 2026-09-18 | defect-scientist Lv3-2 -->
# 공정 조건 → 결함 발생 확률 모델 + 원인 역추적 규칙 (Lv3-2)

> 에이전트: defect-scientist Lv3-2 | 작성일: 2026-09-18
> 선행: [[scratch-physics-source-signatures]](R_est=a_c²/2δ_c 역추적, 발생원별 형상표 §9),
> [[ml-defect-classification-and-rca-methodology]](시그니처→원인 규칙표 R1–R6, Choi 2010 RCA),
> [[defect-density-yield-models-and-spatial-statistics]](Poisson/Murphy/Seeds/음이항 수율식, killer ratio θ,
> join-count 공간무작위성 검정), [[corrosion-pit-defect-morphology-density-inspection]](부식·피트 형상·밀도),
> [[lpc-scratch-density-tail-correlation]](Remsen 2006 LPC-스크래치 선형상관, 임계 0.68 µm),
> [[pattern-dependent-dishing-erosion]](디싱/에로전 유효밀도·step-height 모델, cmp-integrator 소유)
> ⚠ 이 노트는 **모델 명세**만 다룬다 — 코드 구현은 소프트웨어 부문 몫(PROFILE.md `## 구현 요청` 참조).
> 판단 기준은 일반 변수(입자 농도 C, 입경 d_p, 응집체 분율 φ_agg, 하중/압력 P, 상대속도 V,
> 패드 경도 H_pad, 웨이퍼(막) 경도 H_w)로 쓴다 — 물질명은 문헌 인용 맥락에서만 등장한다.

## 1. 결함 종류별 발생 메커니즘과 공정변수

### 1.1 스크래치(마이크로스크래치·채터링) — 접촉역학 지배
단일 대입자(응집체·패드 파편·탈락 그릿)가 패드 애스퍼리티에 물려 웨이퍼 막을 소성 압입·
플로잉(plowing)하는 사건이다(Chandra et al. 2008 §4; [[scratch-physics-source-signatures]] §2).
확률을 올리는 변수:
- **입도분포 상위 꼬리(φ_agg, d_p 상위 백분위)** — 평균 입경이 아니라 임계 직경을 넘는 개수가
  지배(Remsen et al. 2006, §2 아래). 응집은 확산제한응집(DLA)/반응제한응집(RLA) 커널로 진행되며
  초기 입자농도 N₀가 클수록(=농도 C 상승) 응집 속도 자체가 빨라진다(Chandra 2008 식(2),
  α = 8k_BT N₀/3η — 커널이 N₀에 선형).
- **하중/압력 P** — 패드-웨이퍼 실접촉면적비 A_f(P)를 늘려 "활성 입자 수"(트랩된 입자-애스퍼리티
  접촉 사건 수)를 늘린다(Chandra 2008 §6, A_f=0.008 예시). 접촉역학 상한식(Saka/Eusner, 선행
  노트 §3)은 P·패드조도와 무관하게 **최대 스크래치 크기**를 제한하지만, **빈도**는 P에 비례.
- **상대속도 V** — 단위시간당 패드-웨이퍼 상대이동거리(=패드 위 대입자가 웨이퍼를 훑는 총 길이)를
  늘려 접촉 "시행 횟수"를 늘린다. 디스크 그릿의 경우 헤드·플래튼 rpm이 웨이퍼를 가로지르는 호의
  개수·길이를 결정([[scratch-physics-source-signatures]] §8-D).
- **패드 경도(분포 꼬리) H_pad** — 평균 경도가 아니라 **최대 경도(hard spot)**가 무른 패드 파편도
  긁게 만드는 마찰계수 문턱을 낮춘다(같은 노트 §6, µ*=0.366).
- **웨이퍼(막) 경도 H_w** — 낮을수록(연질 막) 같은 입자·하중에서 스크래치가 깊어진다(Chandra 2008
  §7.2, 식(6)).

### 1.2 잔류 입자(residue) — 부착 에너지장벽 지배, 접촉역학과 무관
잔류입자는 "큰 입자가 세게 부딪혀 생기는" 사건이 아니라 **세정 단계에서 못 떼어낸 입자가 남는**
사건이다([[post-cmp-defect-classification-and-inspection]] — 잔류입자는 세정 스플릿에 반응하고
연마조건 스플릿에는 반응하지 않는다는 조작적 구분). 확률을 올리는 변수:
- 입자-표면 간 **DLVO 부착 에너지장벽**이 낮을수록(등전점 근접, 반대 표면전하) 부착 확률↑.
- 세정 단계의 **제거 유효 전단력**(브러시·메가소닉·린스 유량)이 낮을수록 제거 확률↓.
- **입경 d_p**가 작을수록 유체역학적 항력이 작아 제거가 더 어렵다(반대로 스크래치는 대입자가
  문제, 잔류입자는 오히려 미세입자가 문제가 될 수 있음 — 두 결함의 입경 의존 방향이 다르다).
- 억제제·계면활성제 농도가 표면을 소수성/친수성으로 바꿔 재부착을 유발할 수 있다(선행 부식 노트
  §4(A)의 "억제제 농도↑ → 입자 결함↑" 역설이 그 예 — 물질명은 참고 인용일 뿐, 일반화하면
  "부착 에너지장벽을 낮추는 부산물 흡착"이 원인).

### 1.3 부식·피트·딤플 — 반응속도 적분 지배, 접촉역학과 무관
전기화학 반응(국부 용해·갈바닉 부식)이 노출 시간 동안 누적된 결과다([[corrosion-pit-defect-morphology-density-inspection]]
§2–§4). 확률(개수)을 올리는 변수: 산화제 농도, 세정 pH(알칼리/산성), DIW 린스 시간, 보호막(자연
산화막) 손상 여부, 가압(패드-웨이퍼 접촉으로 보호막이 기계적으로 벗겨짐). 이 결함군은 **공간적으로
무작위가 아니라 국부적**(edge-ring 등, Choi 2022 재인용)이라는 점이 스크래치(궤적성 신호)와 다르다.

### 1.4 디싱·에로전 유래 결함 — 결정론적 문턱 초과, 확률이 아니라 배치(layout) 함수
디싱·에로전 자체는 [[pattern-dependent-dishing-erosion]]이 다루는 유효밀도/step-height
모델의 **결정론적 출력**이다(같은 패턴밀도·같은 오버폴리시 시간이면 같은 디싱량이 나온다 — 확률
과정이 아니다). 그러나 디싱·에로전이 "결함"으로 전환되는 지점은 확률적으로 다룰 수 있다:
- 디싱량이 **비아 콘택트 여유 마진**을 넘으면 오픈(open) 결함 — 문턱 초과 여부는 국소 패턴밀도의
  다이-투-다이 산포(오버폴리시 시간의 웨이퍼 내 불균일)에 좌우된다.
- 에로전이 **절연 유전체 최소 두께**를 넘으면 인접 금속선 간 누설/브리지 위험 — 배선 피치가
  좁을수록(=killer 임계가 작을수록, [[defect-density-yield-models-and-spatial-statistics]] §3의
  θ) 같은 에로전량도 결함으로 셀 확률이 커진다.
이 항목은 §2.4에서 "확률 모델이 아니라 문턱 모델"임을 명시하고, 확률화는 오버폴리시 시간의
다이간 산포 분포를 통해서만 도입한다.

## 2. 확률 모델 명세 — 포아송/극값 통계

### 2.1 스크래치 — 접촉 확률 × 꼬리분포의 곱 (핵심 모델)
**1차 문헌**: Chandra, A., Karra, P., Bastawros, A.F., Biswas, R., Sherman, P.J., Armini, S.,
Lucca, D.A. (2008). "Prediction of scratch generation in chemical mechanical planarization."
*CIRP Annals — Manufacturing Technology* 57(1), 559–562. DOI: 10.1016/j.cirp.2008.03.130.
(전문 확보: `papers/chandra2008-cirp-scratch-prediction-cmp.pdf`, sci-hub 미러 경유, 4쪽 직접 판독)

이 논문이 정확히 과제가 요구하는 형태 — **"접촉확률 × 응집체 꼬리분포"** — 를 준다.

**(a) 응집체 꼬리분포 (Smoluchowski DLA 커널)**
```
dN(M)/dt = ½ Σ a(M-K,K) N(M-K) N(K) − N(M) Σ a(M,K) N(K)     (식1)
a(M,K) ≈ 8 k_B T N₀ / (3η)   for M ≫ K (DLA 극한, 식2)
```
N₀=초기 입자농도(=C), η=슬러리 점도. 클러스터 부피→등가반경 X 환산은 프랙탈차원 d_f(1.86–2,
Lin et al. 1989/1990 실측 인용)를 쓴다: V ∝ X^{d_f} (구형 가정 X³이 아님).

**(b) 접촉 확률 — 패드 애스퍼리티 PDF + 스크래치 깊이의 결합분포**
```
∂f(z,t)/∂t = (4 C_a E* √ks / 3π) ∂/∂z[ √(z−δ(t)) f(z,t) ]         (식3, 애스퍼리티 높이 PDF 진화)
W(i,j) = (E*√ks / H) · √(z_i−δ(t)) · X(i,j)                        (식4, 스크래치 깊이)
H = 3π H_w / (2 E* √ks)                                             (식6, 무차원 경도 파라미터)
P(W ≤ w) = ∬ f_{Z'}(z) f_X(x) dz' dx   [적분역: x∈(0, w²/H²), z'∈(0, X_max)]   (식5)
```
E*=패드 유효탄성계수(모듈러스), ks=애스퍼리티 팁 곡률, H_w=웨이퍼(막) 경도, δ(t)=패드-웨이퍼
평균간극. **빈도(발생 확률) = P(W>w) × 활성 입자 수**, 활성 입자 수는 "패드-웨이퍼 실접촉면적비
A_f(P)"로 결정된다(식5 문단, A_f=0.008 예시값). 즉:

```
D(w) [ea/면적·시간]  =  N_active(P, V)  ×  [1 − F_combined(w; H_pad, H_w, V)]
                     =  (접촉 시행 수)   ×  (임계 깊이 w를 넘을 확률, 응집체 꼬리분포에서 옴)
```

시행 수가 크고 개별 시행의 "임계 초과" 확률이 작을 때 이 곱은 **포아송 근사의 정의 그 자체**
(λ = n·p, n→∞, p→0, np=const)다 — 과제가 요구한 "극값통계"가 바로 이 구조다.

**정성적 방향(논문 §7 그대로)**: 패드 모듈러스 E*↑(건조 패드) → H↓(식6, H∝1/E*) → W↑(식4) →
스크래치는 **더 적은 빈도로 더 깊게**. 웨이퍼 경도 H_w↓(연질 막) → H↓ → W↑(식4, H∝H_w이므로
H_w↓ → H↓ → W↑) → **더 깊고 더 잦은** 스크래치(§7.2, Cu가 산화막보다 깊은 스크래치+높은 제거율).

### 2.2 잔류 입자 — 부착 확률 모델 (스크래치와 다른 축)
```
D_residue ∝ C_deposit × [1 − η_removal(shear, t_rinse, ΔG_barrier(ζ))]
```
C_deposit = 표면에 도달한 입자 개수밀도(농도 C·접촉시간의 함수), η_removal = 제거효율(전단력·
린스시간 증가함수, DLVO 장벽 ΔG_barrier 감소함수). **스크래치 모델과 반대 방향의 d_p 의존성**을
가진다는 것이 유일하게 필요한 대조 — 스크래치는 d_p 상위 꼬리, 잔류입자는 하위(작은 입자가 항력이
약해 안 떨어짐)일 수 있어 **d_p 하나로 두 결함을 동시에 최소화하는 방향이 없을 수 있다**는 것이
공정 설계의 실질적 함의다. ⚠ 정량 폐형식(ΔG_barrier의 함수형)은 이번 회차에 1차 문헌으로
확보하지 못했다 — §5에 미검증 명시.

### 2.3 부식·피트 — 시간 적분 모델 (접촉역학과 무관)
```
N_corrosion(t) ∝ ∫₀ᵗ k_rxn(oxidizer, pH) · A_exposed(t') dt'
```
k_rxn=반응속도상수(산화제 농도·pH의 함수, [[corrosion-pit-defect-morphology-density-inspection]]
§4가 정량값 보유), A_exposed=보호막이 벗겨져 노출된 면적(가압·연마로 기계적으로 증가). 포아송류
모델이 아니라 **결정론적 반응속도 적분**이며, 개수의 확률적 요소는 A_exposed의 다이간 산포에서만
들어온다. 스크래치·잔류입자와 달리 **시간(공정 지속시간)이 1차 변수**라는 것이 구조적 차이.

### 2.4 디싱·에로전 유래 결함 — 문턱 모델 (확률 아님)
```
P(defect | pattern) = P( dishing(ρ_eff, t_overpolish) > margin_via )
```
dishing(·)은 [[pattern-dependent-dishing-erosion]]의 결정론적 유효밀도 모델 출력이고, 확률은
오버폴리시 시간 t_overpolish의 웨이퍼 내(WIWNU) 산포 분포에서만 도입된다. **입력에 물질명이
필요 없다** — ρ_eff(패턴밀도)와 margin_via(레이아웃 설계 마진)만으로 정의된다.

## 3. 검증 — 문헌값 대조 코드

### (A) 패드 모듈러스·막 경도의 스크래치 깊이 방향성 — Chandra(2008) 식(4)(6) 결합
```python verify
# Chandra et al. 2008, CIRP Annals 57(1) 559-562, DOI 10.1016/j.cirp.2008.03.130
# 식(4): W = (E*sqrt(ks)/H) * sqrt(z-delta) * X   /  식(6): H = 3*pi*Hw/(2*E*sqrt(ks))
# 두 식을 결합하면 W ∝ (E*)^2 * ks / Hw  (z,delta,X 고정 시). 절대 배율은 논문이 명시하지
# 않으므로(무차원 상수·ks 단위 등 OCR로 완전 복원 불가), **비율만** 검증한다 — 그러면
# E*, ks의 미지 상수·단위가 전부 소거돼 안전하다.
import math

def W_ratio(Estar_a, Hw_a, Estar_b, Hw_b, ks=1.0):
    # W ∝ E*^2 * ks / Hw  (같은 ks, 같은 z,delta,X 가정)
    Wa = Estar_a**2 * ks / Hw_a
    Wb = Estar_b**2 * ks / Hw_b
    return Wa / Wb

# --- 웨이퍼(막) 경도 축: Cu(0.8 GPa) vs 함수화 산화막(4 GPa, wet) vs 건조 산화막(7 GPa) ---
# 논문 §7.2 원문 수치(Table 없이 본문 서술): Hw_oxide_wet=4 GPa, Hw_oxide_dry=7 GPa, Hw_Cu=0.8 GPa
Hw = {"Cu": 0.8e9, "oxide_wet": 4.0e9, "oxide_dry": 7.0e9}
r_cu_vs_oxide_wet = W_ratio(1.0, Hw["Cu"], 1.0, Hw["oxide_wet"])   # E* 고정
print(f"같은 조건에서 W(Cu)/W(oxide,wet) 예측비 = {r_cu_vs_oxide_wet:.2f}배 (Hw 역비 그대로)")
assert r_cu_vs_oxide_wet > 1.0, "Cu(연질)가 산화막보다 깊은 스크래치를 내야 한다(논문 §7.2 정성 결론)"
assert abs(r_cu_vs_oxide_wet - (Hw["oxide_wet"]/Hw["Cu"])) < 1e-9  # W ∝ 1/Hw 이므로 비율은 Hw 역수와 정확히 같다

# --- 패드 모듈러스 축: wet 29 MPa vs partially-dry 100 MPa (논문 §7.1 원문 수치) ---
Estar = {"wet": 29e6, "dry": 100e6}
r_dry_vs_wet = W_ratio(Estar["dry"], 1.0, Estar["wet"], 1.0)      # Hw 고정, W ∝ E*^2
print(f"건조 패드/습윤 패드 예측 스크래치 깊이비 = {r_dry_vs_wet:.1f}배 (식(4)+(6) 결합으로 내가 유도, 논문은 방향만 서술)")
assert r_dry_vs_wet > 1.0, "건조(고모듈러스) 패드가 더 깊은 스크래치를 내야 한다(논문 §7.1: '모듈러스 증가 -> 깊이 증가')"
# 논문 본문은 정량 배율을 제시하지 않는다 -- 이 숫자는 식(4)(6) 결합에서 나온 유도값이며,
# 저자가 직접 보고한 값이 아니므로 '문헌 직접값'이 아니라 '문헌 수식의 재현'으로 표기한다.

# --- 참고: 오차 방향 그 자체(Fig.1 서술) -- 모델이 스스로 인정하는 한계 ---
# 논문 §6 원문: 실험 최대 스크래치 깊이 500nm@빈도2 인데 모델 예측은 "much lower".
# 저자 해석: 초기 입도분포 가정이 실제 슬러리의 극미량 대입자 오염을 놓쳤기 때문(응집 모델의 구조적 한계).
exp_max_depth_nm, exp_max_freq = 500.0, 2.0
exp_common_depth_nm, exp_common_freq = 250.0, 9.0   # 논문이 보고한 "정상적" 피크(오염 꼬리 제외)
model_df2_depth_nm, model_df2_freq = 250.0, 13.0    # 프랙탈차원 d_f=2 극한
model_df186_depth_nm, model_df186_freq = 350.0, 9.0 # 프랙탈차원 d_f=1.86 극한
diff_freq_pct = abs(model_df2_freq - exp_common_freq) / exp_common_freq * 100
diff_depth_pct = abs(model_df186_depth_nm - exp_common_depth_nm) / exp_common_depth_nm * 100
print(f"d_f=2: 깊이는 실험과 정확히 일치(250nm)하나 빈도는 {diff_freq_pct:.0f}% 과대(13 vs 9)")
print(f"d_f=1.86: 빈도는 정확히 일치(9)하나 깊이는 {diff_depth_pct:.0f}% 과대(350 vs 250nm)")
assert diff_freq_pct > 0 and diff_depth_pct > 0, "두 극한 모두 한쪽 축만 맞고 다른 축은 어긋난다(저자 스스로 인정한 한계, §6)"
# 원인 가설(저자 서술 그대로): 프랙탈차원을 사전에 모르면 깊이·빈도를 동시에 못 맞춘다 -- 사후에만 역산 가능,
# 예측 전략으로는 구조적 한계.
```

### (B) 스크래치 = "시행수 × 확률"의 선형 극한 — Remsen(2006) LPC 선형상관을 포아송 λ로 재해석
```python verify
# Remsen et al. 2006, JES 153(5) G453, DOI 10.1149/1.2184036 (Table V, S03+S05 병합 센서)
# 이미 [[lpc-scratch-density-tail-correlation]] §5에서 재현된 수치를 재사용한다.
# 주장: "시행수(LPC) x 확률(threshold 고정)" = 포아송(lambda = n*p, p 고정)이면 원점을 지나야
# 한다(트라이얼이 0이면 사건도 0). Table V의 절편이 정확히 0이 아니므로, 근사가 좋은 구간과
# 나쁜 구간을 x절편(스크래치=0이 되는 LPC)으로 직접 정량화한다.
slope = 2.99e-5       # counts / (particles/g_slurry)
intercept = -9.0       # counts (Y절편, 통계오차 -9±7 -- 0과 통계적으로 구분 안 됨)

x_intercept_lpc = -intercept / slope           # 스크래치=0이 되는 LPC (포아송 '트라이얼 문턱')
print(f"x절편(스크래치=0) LPC = {x_intercept_lpc:.2e} particles/g_slurry")

lpc_lo, lpc_hi = 7.0e5, 5.0e6                  # 실험 스윕 범위 근방 두 점(Table III에서 재구성)
frac_lo = x_intercept_lpc / lpc_lo
frac_hi = x_intercept_lpc / lpc_hi
print(f"x절편/LPC 비 -- 저농도({lpc_lo:.1e}): {frac_lo:.2f}, 고농도({lpc_hi:.1e}): {frac_hi:.3f}")
# 고농도에서는 절편이 무시할 만큼 작아(<15%) 원점통과 포아송 근사가 좋다
assert frac_hi < 0.15, "고농도에서도 절편이 크면 순수 포아송(np) 근사가 전 구간에서 부적절"
# 저농도에서는 절편이 신호와 같은 자릿수라 포아송 근사가 나쁘다 -- 정직하게 명시
assert frac_lo > 0.3, "저농도에서 절편이 무시할 만하면 '근사가 농도의존적으로 나빠진다'는 주장이 틀림"
print(f"결론: LPC ≫ {x_intercept_lpc:.1e}(문턱)일 때만 D(w)≈slope×C(순수 포아송, 원점통과)가 좋고, "
      f"문턱 근방(저농도)에서는 절편(측정 노이즈 바닥 또는 문턱이하 결함원)이 무시 못 할 크기다.")
```

### (C) 포아송 선형 근사의 파탄 지점 — Kwon(2013) 디브리 농도 포화, 나이브 선형 대비 26% 과대
```python verify
# Kwon et al. 2013, Tribology International 67, 272-277, DOI 10.1016/j.triboint.2013.08.008
# Fig.6 판독값([[scratch-physics-source-signatures]] §5): 정규화 스크래치 수(기준 1.0)
wtpct = [0.25, 0.375, 0.5, 1.0]
scratch_norm = [2.25, 2.4, 3.0, 2.5]

# 저농도 두 점(0.25, 0.375 wt%)으로 순진한 선형(포아송 np) 모델을 세우고 고농도(1.0 wt%)로 외삽
slope_naive = (scratch_norm[1] - scratch_norm[0]) / (wtpct[1] - wtpct[0])
intercept_naive = scratch_norm[0] - slope_naive * wtpct[0]
pred_at_1wt = slope_naive * wtpct[3] + intercept_naive
actual_at_1wt = scratch_norm[3]
diff_pct = (pred_at_1wt - actual_at_1wt) / actual_at_1wt * 100
print(f"나이브 선형(저농도 기울기) 외삽: wt%=1.0 예측 {pred_at_1wt:.2f} vs 실측 {actual_at_1wt:.2f} "
      f"-> {diff_pct:.0f}% 과대예측")
assert diff_pct > 20, "저농도 선형을 고농도로 외삽하면 실측보다 20% 이상 과대예측해야 한다(포화 증거)"
assert scratch_norm[3] < scratch_norm[2], "1.0 wt%에서 실제로는 0.5 wt%보다 낮아지는 포화(비단조) 관찰"
# 원인 가설(Kwon 2013 저자 서술 그대로): 웨이퍼면에 실제 전달되는 디브리 양이 헤드/플래튼/
# 리테이닝링 회전으로 제한된 실접촉면적(A_f)에 의해 상한이 있다 -- §2.1의 N_active(P)가
# 농도와 무관하게 포화하기 때문. 즉 D(w) = N_active x P_tail에서 N_active가 C의 함수가 아니라
# '접촉면적이 허용하는 만큼만' 포화하는 구조라는 뜻 -- 순수 포아송(np, n∝C 무한선형)의 실패 지점.
print("결론: LPC 축(B)에서는 선형(포아송)이 맞지만, 디브리 절대농도가 접촉면적 포화점을 넘으면(C) 깨진다.")
print("      -> D(w) 모델의 N_active(P,C)는 저농도에서 ∝C, 고농도에서 A_f(P) 상한으로 포화하는 함수여야 한다.")
```

## 4. 원인 역추적 규칙 — 관측 시그니처 → 후보 원인 → 구분 실험

| # | 관측 시그니처(입력) | 판단 기준 | 후보 원인 | 구분 실험(출력 확정) |
|---|---|---|---|---|
| R1 | 짧은 선형 결함(길이 <8 µm, 폭 0.3–0.6 µm), 산발 분포 | R_est=a_c²/2δ_c < 0.6 µm ([[scratch-physics-source-signatures]] §9) | 슬러리 응집체(대입자 꼬리) | LPC(임계 0.68 µm 등가 이상) 재측정 → 상관; 필터 공극 축소 후 재현성 확인 |
| R2 | 긴 선형 결함(길이 >8 µm) 또는 웨이퍼맵 곡률반경 0.24–0.50 m의 호 | 곡률반경이 웨이퍼 반경(0.15 m)보다 훨씬 큼 | 디스크 그릿 탈락 | 컨디셔너 사용시간 vs 결함수 상관, 그릿 탈락 육안/현미경 검사, 디스크 교체 후 재현성 |
| R3 | group chatter(다중 파단) 스크래치, 형상분포에서 group chatter 비율↑ | 기준 대비 group chatter 28%→69%대 (Kwon 2013) | 패드 파편(무른 덩어리, 마찰계수 매개) | 패드 경도 산포(Berkovich 다점 압입) 측정, 컨디셔닝 방식(ex-situ/DIW젯) 변경 후 재현성 |
| R4 | 등방 concave/convex 결함, 하부 금속 산화물 조성, edge/패턴 편중 | DNN/DWN 비 ≈1, EDS 조성=기판 산화물 | 부식·피트 | EDS/XPS 조성 확인, 가압·DIW 린스시간 스윕 후 개수 상관(증가하면 부식 확정) |
| R5 | convex, 이질조성(슬러리 성분과 일치), 세정 스플릿에만 반응 | 연마 레시피 불변인데 세정만 바꿔 개수 변화 | 잔류 입자 | 세정 유량/브러시압 스윕, ζ전위 측정(부착장벽 추정), 조성 EDS로 슬러리 성분 확인 |
| R6 | 국소 다이 클러스터(웨이퍼 랜덤 아님), 특정 배선 밀도 영역 편중 | join-count SRT로 H0(공간독립) 기각([[defect-density-yield-models-and-spatial-statistics]] §6-C) + 패턴밀도맵과 공간 상관 | 디싱/에로전 유래 오픈·브리지 | ρ_eff(국소 패턴밀도) 대 결함좌표 중첩; 오버폴리시 시간 스윕으로 문턱초과 여부 재현 |
| R7 | 웨이퍼 전역에 걸친 균일 저밀도 산발, 형상분포는 기준과 동일(broken chatter 지배) | 형상만으로 구분 불가 — 개수만 변함 | 건조 응집체(슬러리 노화) | LPC 경시변화(슬러리 배치 연령) 추적, 슬러리 필터 교체 전후 대조 |

**절차**: ① ADC(자동분류)로 유형 분리([[ml-defect-classification-and-rca-methodology]] §6) →
② 위 표로 1차 후보 좁힘 → ③ 공간통계(SRT)로 무작위/국부 판정 → ④ commonality analysis로
공정 단계 귀속(슬러리 로트/필터 수명/컨디셔너 시간/툴) → ⑤ 구분 실험으로 최종 확정. **형상
단독 판정 금지**(조성·궤적·통계 검증 없이 라벨 확정하지 말 것 — Lv3-1 §9 규칙 계승).

## 5. 한계·미검증
- ⚠ **미검증**: §2.1 식(4)(6)의 절대 배율(모듈러스 100 MPa 대 29 MPa에서 정확히 몇 배 깊어지는가)은
  논문이 정량 제시하지 않아 §3(A)에서 **내가 두 식을 결합해 유도한 값**이다. 방향(단조 증가)은
  검증됐으나 절대 배율은 저자 확인 없이는 문헌값으로 인용하면 안 된다.
- ⚠ **미검증**: 프랙탈차원 d_f를 사전에 알 방법이 없어(저자 스스로 "사후 역산만 가능, 예측
  전략에는 못 씀"이라 명시) §2.1 모델은 **깊이와 빈도를 동시에 예측하지 못한다**(§3-A 재현).
  Lv3-2 모델 명세는 이 한계를 상속한다.
- ⚠ **미검증**: §2.2 잔류입자의 ΔG_barrier 정량 폐형식(DLVO 에너지장벽을 ζ전위·이온강도의 함수로
  쓰는 식)은 이번 회차에 1차 문헌으로 확보하지 못했다. 방향성(부착장벽↓→잔류입자↑)만 정성 서술.
- ⚠ **미검증**: §2.4 디싱/에로전 문턱모델의 margin_via(비아 콘택트 여유 마진) 절대값은
  레이아웃/설계룰 의존이라 공정문헌만으로는 못 정한다 — 확률화(오버폴리시 시간 산포)의 폐형식은
  제안만 하고 분포모수(예: 정규분포 σ)는 확보하지 못했다.
- ⚠ **범위 밖**: §3(C)의 "포화" 원인은 Kwon 저자의 정성 설명(리테이닝링 회전 제한)이며, A_f(P)
  포화의 정량 폐형식(예: A_f = A_f,max·(1-exp(-kC)))은 이번 문헌에서 직접 제시되지 않아 지어내지
  않았다 — 방향(포화 존재)만 확정, 함수형은 후속 과제.
- Chandra(2008)는 산화막(HDP oxide) 단일 시스템 실험으로 검증됐다 — 다른 화학종(금속 CMP,
  low-k)으로의 정량 이식은 §3(A)의 방향성 검증 범위 밖이다(저자도 §7이 "매개변수 연구"임을 명시).

## 6. 출처
1. **Chandra, A., Karra, P., Bastawros, A.F., Biswas, R., Sherman, P.J., Armini, S., Lucca, D.A.
   (2008)**, "Prediction of scratch generation in chemical mechanical planarization," *CIRP
   Annals — Manufacturing Technology* 57(1), 559–562. DOI: 10.1016/j.cirp.2008.03.130 — 1차,
   전문 확보(sci-hub 미러 경유, `papers/chandra2008-cirp-scratch-prediction-cmp.pdf`). 다중스케일
   접촉확률×응집체꼬리 모델의 원출처.
2. **Remsen, E.E., Anjur, S., Boldridge, D., Kamiti, M., Li, S., Johns, T., Dowell, C.,
   Kasthurirangan, J., Feeney, P. (2006)**, "Analysis of Large Particle Count in Fumed Silica
   Slurries and Its Correlation with Scratch Defects Generated by CMP," *J. Electrochem. Soc.*
   153(5), G453–G461. DOI: 10.1149/1.2184036 — 1차, 선행 노트에서 전문 확보·재인용
   ([[lpc-scratch-density-tail-correlation]]).
3. **Kwon, T.-Y., Ramachandran, M., Cho, B.-J., Busnaina, A.A., Park, J.-G. (2013)**, "The impact
   of diamond conditioners on scratch formation during CMP of silicon dioxide," *Tribology
   International* 67, 272–277. DOI: 10.1016/j.triboint.2013.08.008 — 1차, 선행 노트에서 전문
   확보·재인용([[scratch-physics-source-signatures]]).
4. 선행 노트 상호링크로 승계(2차 재인용 아님, 각 노트가 1차 출처를 직접 확보): 부식·피트 정량은
   [[corrosion-pit-defect-morphology-density-inspection]], killer ratio·공간통계는
   [[defect-density-yield-models-and-spatial-statistics]], ADC/RCA 방법론은
   [[ml-defect-classification-and-rca-methodology]], 스크래치 접촉역학 상한식은
   [[scratch-physics-source-signatures]], 디싱/에로전 결정론적 모델은
   [[pattern-dependent-dishing-erosion]](cmp-integrator 소유, 본 노트는 결함 문턱 해석만 추가).
