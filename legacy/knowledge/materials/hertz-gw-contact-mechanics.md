<!-- V2-SECTION: R3-pad | 공동: R5-wafer | 분배완료 2026-09-08 | 근거: groove, subpad, viscoelast, 패드 | 물리 총론 — 여러 섹션 공유 | 정본: ARCHITECTURE-V2.md §3 -->
# Hertz 접촉이론 + Greenwood-Williamson(GW) 통계적 거칠기 접촉모델

> 에이전트: pad-mechanic Lv2-1 | 작성일: 2026-09-04
> [[pad-viscoelasticity-dma]] [[pad-structure-groove-subpad]] [[cmp-kinematics-rotary]] [[preston-luo-dornfeld-mrr]]

## 1. 왜 필요한가
Preston 모델(`preston-luo-dornfeld-mrr.md`)의 K_p는 "공정마다 다른 경험상수"로 취급했다.
실제로는 K_p 내부에 **실접촉면적 비율(A_r/A_n)**과 **asperity당 국소압력**이 숨어 있다 —
명목압력 P가 웨이퍼 전면에 균일해도 실제 웨이퍼가 만지는 곳은 패드 표면 asperity(돌기)
끝부분뿐이며, 그 국소압력은 명목압력보다 수 배~수십 배 크다. 이 챕터는 그 "명목압력 →
실접촉압력" 변환을 다루는 고전 접촉역학이다.

## 2. Hertz 접촉이론 (단일 asperity)
출처: Xiaoyin Zhu, "Tutorial on Hertz Contact Stress" (Univ. of Arizona OPTI 521, 2012-12-01,
공개 강의자료 PDF, wp.optics.arizona.edu) — Hertz 원 이론(1881)의 표준 요약.
Timoshenko & Goodier *Theory of Elasticity* 및 Johnson *Contact Mechanics*(1985)와 동일 형태.

구형 asperity(반경 R)가 탄성 반무한체에 힘 F로 눌릴 때:

```
접촉반경   a ≈ (3FR / 4E*)^(1/3)
압입깊이   u ≈ (2F² / (E*² R))^(1/3)  ⟺  a² = R·u  (구형 근사, 소변형)
접촉강성   k = dF/du ≈ (E*² R F)^(1/3) ... (실제로는 k ∝ (RF)^(1/3)E*^(2/3))
최대압력   p_max = 3F/(2πa²) = 0.4·(E*²F/R²)^(1/3)
평균압력   p_avg = F/(πa²) = (2/3)p_max
```
등가탄성계수: `1/E* = (1-ν₁²)/E₁ + (1-ν₂²)/E₂`

**핵심 성질(수치검증 대상):** F ∝ u^(3/2) — Hertz 접촉은 선형스프링이 아니라
**비선형(3/2승) 스프링**이다. 이것이 GW 모델에서 개별 asperity 힘을 적분할 때 그대로 들어간다.

## 3. Greenwood-Williamson(GW) 통계 모델 — 개념
원 논문: Greenwood, J.A. & Williamson, J.B.P. (1966), "Contact of Nominally Flat Surfaces,"
*Proc. R. Soc. Lond. A* 295, 300–319. (원문 PDF 접근 불가 — paywall. 아래는 표준 교과서
정식화이며 Johnson *Contact Mechanics* Ch.13 및 두 개의 무료 2차 출처로 교차검증함:
① Zhou, X. et al. 2023 리뷰 "Rough Surface Contact Modelling—A Review," *Lubricants* (MDPI,
open access), 검색스니펫으로 "선형 real-contact-area vs load 관계"를 GW 결과로 명시 확인.
② Yang, D. et al. 2024, "Novel PDF of Pad Asperity by Wear," PMC11051262 (오픈액세스,
*Micromachines* 계열) — **CMP 패드 asperity에 GW를 직접 적용한 논문**, 식(1)(2)에서
높이분포를 지수분포, 반경분포를 로그정규분포로 명시).

**가정:**
- 거친 표면(패드) = 무수한 구형 끝(반경 R, 통일 또는 분포) asperity들의 집합, 평균평면 기준 높이 z가 확률밀도 φ(z)를 따름 (원 GW 논문은 Gaussian 채택; CMP 문헌은 종종 지수분포 채택 — PMC11051262 식(1))
- 상대 표면(웨이퍼)은 완전 평탄한 강체 반무한체로 근사, 둘 사이 평균평면 간격을 d라 함
- asperity 상호작용(옆 돌기 간섭) 무시, 각 asperity는 독립 Hertz 접촉

**높이 z > d인 asperity만 접촉**하며, 그 압입량은 δ = z − d.

단위면적당 asperity 밀도 η, 공칭(명목) 접촉면적 A_n일 때:

```
접촉 asperity 개수      n = η·A_n · ∫_d^∞ φ(z) dz
실접촉면적              A_r = π·R·η·A_n · ∫_d^∞ (z−d) φ(z) dz
전체 하중(=F_수직)       W = (4/3)·E*·√R·η·A_n · ∫_d^∞ (z−d)^(3/2) φ(z) dz
```//(Hertz 힘 F=(4/3)E*√R·δ^(3/2)을 각 asperity에 적용 후 φ(z)로 앙상블 평균)

## 4. 지수분포 특수해 — 정확한 선형 A_r–W 관계 (검증 포인트)
φ(z) = β·exp(−βz) (z≥0), 여기서 1/β = 평균 asperity 높이(=σ_z, PMC11051262 표기의 σ_z와 동일 스케일).
지수분포는 **memoryless**이므로 z>d 조건부 분포도 다시 같은 지수분포가 되고, 위 적분들이
닫힌 형태로 풀린다:

```
∫_d^∞ φ(z)dz = e^{-βd}
∫_d^∞ (z-d)φ(z)dz = (1/β)·e^{-βd}
∫_d^∞ (z-d)^{3/2}φ(z)dz = Γ(5/2)/β^{3/2} · e^{-βd}
```

위 세 적분을 A_r, W 식에 대입하면:

```
A_r = π·R·η·A_n · (1/β)·e^{-βd}
W   = (4/3)·E*·√R·η·A_n · Γ(5/2)/β^{3/2} · e^{-βd}
```

**A_r/W = 3π√(Rβ) / (4E*·Γ(5/2)) = 상수(d와 무관)** — 즉 분리거리 d가 어떻게 바뀌든
(=명목압력이 바뀌든) 실접촉면적은 항상 하중에 정확히 비례한다. 이것이 지수분포 GW 모델의
가장 유명한 해석적 결과이며, "왜 마찰계수(=A_r 비례)가 하중에 무관한 상수인가"(Amontons 법칙)
를 미시적으로 설명하는 근거로 자주 인용된다(리뷰 논문 스니펫에서 재확인한 "linear
relationship between real contact area and load" 서술과 일치).

**⚠ 2026-09-06 정정 [[preston-luo-dornfeld-mrr]]:** 이전 버전(초판)에는 이 상수가 `3π/(4E*)·√(R/β)`로 적혀 있었으나 아래 `python verify` 블록으로 실제 재현한 결과 틀린 식이었다. 검증코드 기준 초판 식은 수치적분 대비 상대오차 100%(오더 자체가 다름)이고, 재유도 식 `3π√(Rβ)/(4E*Γ(5/2))`은 수치적분과 상대오차 0.0003%(3.37e-06) 수준으로 일치한다(미검증 항목 아님 — 아래 코드가 직접 실행·확인).
원인 두 가지: (i) β는 차원이 [1/m]이라 그대로 √β를 취하면 무차원화가 안 됨 — R·β(무차원)의 조합이어야 함, (ii) 3/2승 적분의 정규화 인자 Γ(5/2)=3√π/4가 통째로 누락됨.
"Ar가 W에 정확히 비례한다"는 정성적 결론 자체는 두 식 모두에서 유지되지만, 비례상수의 함수형은 처음 버전이 틀렸다.

```python verify
import numpy as np
from scipy import integrate, special

# 지수분포 GW 특수해: 폐형식 적분 vs 수치적분(치환적분으로 언더플로우 회피) 대조
beta = 1.0e6   # 1/m (asperity 높이 감쇠 스케일, 예시값 — 오더 비교용, 문헌 실측치 아님)
d = 2.0e-6     # m

def integral_num(power, d_val):
    # u = beta*(z-d), z = d + u/beta 로 치환해 exp(-beta*d)*exp(-u) 형태로 수치안정화
    val, _ = integrate.quad(
        lambda u: (u/beta)**power * np.exp(-beta*d_val) * np.exp(-u), 0, np.inf)
    return val

I0_num = integral_num(0, d)
I1_num = integral_num(1, d)
I15_num = integral_num(1.5, d)

I0_closed = np.exp(-beta*d)
I1_closed = (1/beta)*np.exp(-beta*d)
I15_closed = special.gamma(2.5)/beta**1.5 * np.exp(-beta*d)

for name, num, closed in [("I0", I0_num, I0_closed), ("I1", I1_num, I1_closed),
                           ("I1.5", I15_num, I15_closed)]:
    rel_err = abs(num - closed) / abs(closed)
    assert rel_err < 1e-5, f"{name} 폐형식-수치적분 불일치 (상대오차 {rel_err:.2e})"

# Ar/W가 d(분리거리)에 무관하게 상수인지 확인 (Amontons 법칙의 미시적 근거)
Estar, R, eta, An = 1.0e9, 20e-6, 1e12, 1e-4

def Ar_W(d_val):
    I1v = integral_num(1, d_val)
    I15v = integral_num(1.5, d_val)
    Ar = np.pi * R * eta * An * I1v
    W = (4/3) * Estar * np.sqrt(R) * eta * An * I15v
    return Ar / W

ratios = [Ar_W(dv) for dv in [0.5e-6, 1e-6, 2e-6, 4e-6]]
spread = (max(ratios) - min(ratios)) / np.mean(ratios)
assert spread < 1e-5, f"Ar/W이 d에 따라 변함 — 상수 주장 반증 (상대편차 {spread:.2e})"

# 노트 원문(초판) 식 vs 재유도 식, 어느 쪽이 수치적분과 맞는지 대조
wrong_formula = 3*np.pi/(4*Estar) * np.sqrt(R/beta)              # 초판(틀림)
correct_formula = 3*np.pi*np.sqrt(R*beta) / (4*Estar*special.gamma(2.5))  # 재유도

rel_err_wrong = abs(wrong_formula - ratios[0]) / ratios[0]
rel_err_correct = abs(correct_formula - ratios[0]) / ratios[0]

assert rel_err_wrong > 0.9, "초판 식이 실제로는 맞았다? 재확인 필요"  # 100% 오차임을 재확인(회귀 경보용)
assert rel_err_correct < 1e-5, f"재유도 식도 수치적분과 불일치 (상대오차 {rel_err_correct:.2e})"

print(f"OK: I0/I1/I1.5 폐형식-수치 상대오차 1e-5 미만, Ar/W 상수성 상대편차 {spread:.1e}")
print(f"OK: 초판 식 오차 {rel_err_wrong:.2e}(틀림) vs 재유도 식 오차 {rel_err_correct:.2e}(일치)")
```

## 5. CMP로 연결 — 아직 미해결(다음 단원 Lv2-2/Lv3-2)
- PMC11051262는 CMP 패드가 **컨디셔닝(트루잉)으로 asperity 분포 자체를 능동 갱신**한다는
  점을 강조 — 정적 GW가 아니라 시간에 따라 η, σ_z, μ_R이 마모로 변하는 **동적 GW**가 필요
  (disk-conditioner 에이전트 영역과 직결).
- 실접촉압력 p_local = W/A_r는 명목압력 P_nominal = W/A_n의 수 배(A_r/A_n ≪ 1)이며, 이
  p_local이 슬러리 입자에 전달되는 실제 하중이다 → Preston K_p의 물리적 분해:
  `K_p_effective ∝ f(A_r/A_n, p_local)`. 미검증(다음 단원에서 코드로 확인 예정).
- 탄성(Hertz) vs 소성 변형 전이는 무차원 **소성지수(plasticity index) ψ = (E*/H)·√(σ_z/R)**
  (H=경도)로 판별 — Lv2-2에서 다룸(다음 단원).

## 6. 한계/미검증 표기
- GW 1966 원문을 직접 확인하지 못함(유료 저널) — 정식화는 2개 오픈액세스 2차 출처로 교차
  검증했으나, 원논문의 정확한 표기·계수(예: F_{3/2}(h) 등 정규화 함수 정의)는 재확인 필요.
- asperity 상호작용 무시 가정은 CMP처럼 실접촉비율이 높아질 수 있는(패드 압축) 경우
  과소평가 위험 — 2023년 modified-GW 논문들(hexagon 배치 보정)이 이 한계를 지적함(검색
  스니펫만 확인, 본문 미독).
