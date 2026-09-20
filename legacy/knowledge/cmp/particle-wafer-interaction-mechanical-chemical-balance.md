<!-- V2-SECTION: R2-slurry | 분배완료 2026-09-08 | 근거: chemistry, particle-wafer, passivation, pourbaix, slurry | 정본: ARCHITECTURE-V2.md §3 -->
# 입자-웨이퍼 상호작용 — 기계적 제거 vs 화학적 용해의 균형(passivation-abrasion 시너지)

> 에이전트: slurry-chemist Lv2-2 | 작성일: 2026-09-06
> [[surface-chemistry-cu-w-pourbaix-passivation]] [[slurry-components-overview]] [[../materials/hertz-gw-contact-mechanics]] [[preston-luo-dornfeld-mrr]]

## 1. 왜 필요한가 — CMP 제거의 본질은 "화학×기계"의 시너지
[[slurry-components-overview]]의 Kaufman 경쟁모델과 [[surface-chemistry-cu-w-pourbaix-passivation]]의
passivation 열역학은 "무른 막이 생긴다"까지를 다뤘다. 이 단원은 그 무른 막이 **연마입자 한 알에
의해 실제로 어떻게 벗겨지는가**를 접촉역학([[../materials/hertz-gw-contact-mechanics]])과 결합해
정량화한다. 핵심 명제 세 가지:
- **순수 화학(정지식각)만으로는 제거가 거의 없다**(자기제한적 부동태). — [[surface-chemistry-cu-w-pourbaix-passivation]]
- **순수 기계(경질 산화막)만으로도 제거가 비효율적이다**(입자 압입깊이가 Å~sub-nm 오더).
- 따라서 제거는 **화학이 표면을 연화(H↓) → 기계가 깊이 파고들어 제거(V↑)**의 곱, 즉 시너지다.
  이것이 Kaufman(1991)의 passivation→abrasion→재산화 순환이며, 정량적으로 "연화가 마모체적을
  거듭제곱으로 증폭"함을 §4에서 코드로 보인다.

## 2. 단일 연마입자 접촉역학 — 입자당 압입깊이·접촉응력
[[../materials/hertz-gw-contact-mechanics]]의 Hertz 식을 **슬러리 입자 스케일**에 적용한다. 콜로이달
실리카(반경 R≈50 nm, 즉 직경 ~100 nm; [[slurry-components-overview]] §2)가 힘 F로 웨이퍼(SiO₂ 막)를
누를 때:

```
접촉반경  a = (3FR / 4E*)^(1/3)
압입깊이  δ = a²/R              (Hertz 탄성, a²=Rδ)
최대접촉압 p_max = 0.4·(E*²F/R²)^(1/3),  p_avg = (2/3)p_max
1/E* = (1-ν₁²)/E₁ + (1-ν₂²)/E₂   (SiO₂: E=73 GPa, ν=0.17)
```

입자당 하중 F는 실제로는 명목압력 P를 실접촉 asperity에 갇힌 **활성입자**들이 나눠 받는 값으로,
CMP에서 수 nN~수백 nN 오더로 보고된다(활성입자 개념은 §5, Luo-Dornfeld 2001, doi:10.1109/66.920723).
§4 코드로 F=10–100 nN 범위에서 **접촉응력 0.7–1.5 GPa(GPa 오더), 압입깊이 0.09–0.43 nm(Å~sub-nm
오더)**를 재현한다 — 문헌이 서술하는 "CMP 접촉응력 GPa 오더, 압입 nm 이하"와 오더 일치. 압입이
Å 오더로 극히 얕다는 점이 곧 "화학적 연화 없이는 기계제거가 비효율적"임을 정량적으로 뒷받침한다.

## 3. 탄성/소성 전이 — 왜 "무른 막"이어야 하는가
p_max를 재료 경도 H와 비교하면 접촉 모드가 갈린다(소성지수 개념, [[../materials/hertz-gw-contact-mechanics]] §5):
- **경질 산화막·유전체**(SiO₂ H≈8–9 GPa, 나노압입 2차값): p_max≈1.2 GPa < H → **탄성 접촉**. 탄성
  접촉은 슬라이딩 후 완전 회복 → 이상적으로는 재료제거 0. 순수 기계로는 잘 안 깎이는 이유.
- **연질 금속·연화막**(Cu H≈1–2 GPa; 산화·수산화막·착물막은 더 무름): p_max ≳ H → **소성 접촉**.
  소성 영역에서 평균접촉압은 경도 H로 포화(p_mean≈H, GPa 오더)하고, 입자가 파고들며 영구 홈(plowing)을
  남겨 실제 제거가 일어난다. 화학의 역할은 표면을 이 소성 레짐으로 끌어내리는 것(H를 낮춤).

이는 [[surface-chemistry-cu-w-pourbaix-passivation]]의 WO₃/Cu(OH)₂·Cu₂O "무른 막" 및
[[../physics/tribology-friction-wear-stribeck]] Archard 마모(V∝1/H, H↓→마모↑)와 정확히 정합한다.

## 4. 화학-기계 시너지 정량 — 연화가 마모체적을 거듭제곱으로 증폭
소성(plowing) 접촉의 기하: F = H·π·a_p², a_p²=2Rδ_p ⟹ **δ_p = F/(2πR·H) ∝ 1/H**. 입자가 슬라이딩하며
파내는 홈 단면적 A_f ≈ (4/3)√(2R)·δ_p^(3/2) ∝ R^{1/2}·H^{-3/2}. 즉 화학적 연화로 H를 4배 낮추면
압입은 4배, **입자당 제거체적률은 4^{1.5}=8배** 증폭된다. 이것이 Kaufman(1991, doi:10.1149/1.2085434)
passivation-abrasion 순환의 정량적 심장부다. 아래 verify 블록으로 §2·§4 수치를 모두 대조한다.

**재현 요약**(단일 실리카 R=50nm, F=50nN): 접촉응력 1.22 GPa·압입깊이 0.271 nm을 문헌 GPa·sub-nm 오더와 대조 일치, 화학연화 H 4배↓ → 압입 4배·마모체적 8배 증폭을 §4 코드로 재현(1블록 PASS).

```python verify
import math
# ── (A) 단일 실리카 입자 Hertz 탄성 접촉 (반경 50nm, SiO2-SiO2) ──
R = 50e-9                      # 입자 반경 50 nm (직경 100nm, colloidal silica)
E1=E2=73e9; nu1=nu2=0.17      # SiO2 탄성계수/포아송비 (2차값)
Estar = 1/((1-nu1**2)/E1 + (1-nu2**2)/E2)
assert abs(Estar/1e9 - 37.6) < 0.5, Estar/1e9   # E* ≈ 37.6 GPa

res = {}
for F in (10e-9, 50e-9, 100e-9):              # 입자당 하중 10~100 nN
    a = (3*F*R/(4*Estar))**(1/3)
    delta = a**2/R
    pmax = 0.4*(Estar**2*F/R**2)**(1/3)
    res[F] = (a, delta, pmax)
    print(f"F={F*1e9:5.0f} nN | a={a*1e9:.2f} nm | delta={delta*1e9:.3f} nm | pmax={pmax/1e9:.2f} GPa")

# 접촉응력 GPa 오더 (문헌: CMP 단일입자 접촉응력 ~GPa)
assert all(0.5e9 < res[F][2] < 5e9 for F in res), "접촉응력 GPa 오더 아님"
# 압입깊이 Å~sub-nm 오더 (문헌: 압입 nm 이하)
assert all(0.05e-9 < res[F][1] < 1e-9 for F in res), "압입깊이 sub-nm 오더 아님"
# 대표값 F=50nN 정밀 대조
a,d,p = res[50e-9]
assert abs(p/1e9 - 1.22) < 0.05 and abs(d*1e9 - 0.271) < 0.01

# ── (B) 화학적 연화 → 소성 압입·마모체적 증폭 (F=50nN 고정) ──
F = 50e-9
def plastic(H):
    a_p = math.sqrt(F/(math.pi*H))     # F = H·π·a_p²
    d_p = a_p**2/(2*R)                 # δ_p = F/(2πR·H) ∝ 1/H
    A_f = (4/3)*math.sqrt(2*R)*d_p**1.5  # plowing 홈 단면 ∝ H^-1.5
    return d_p, A_f
d_hard, A_hard = plastic(2.0e9)   # 경질(맨 Cu) H=2 GPa
d_soft, A_soft = plastic(0.5e9)   # 연화막 H=0.5 GPa (4배 무름)
print(f"H=2.0GPa: δ_p={d_hard*1e9:.4f} nm | H=0.5GPa: δ_p={d_soft*1e9:.4f} nm")
print(f"연화(H 4배↓) → 압입 {d_soft/d_hard:.2f}배, 마모체적 {A_soft/A_hard:.2f}배")
assert abs(d_soft/d_hard - 4.0) < 0.01      # 압입 ∝ 1/H → 정확히 4배
assert abs(A_soft/A_hard - 8.0) < 0.05      # 체적 ∝ H^-1.5 → 4^1.5 = 8배

# ── (C) Luo-Dornfeld 단일입자 소성 제거체적의 하중 스케일: V₁ ∝ F^1.5 ──
def vol_per_slide(f, H=1e9):
    a_p=math.sqrt(f/(math.pi*H)); d_p=a_p**2/(2*R)
    return (4/3)*math.sqrt(2*R)*d_p**1.5
r = vol_per_slide(100e-9)/vol_per_slide(50e-9)
print(f"하중 2배 → 입자당 제거체적 {r:.3f}배 (F^1.5 예측 {2**1.5:.3f})")
assert abs(r - 2**1.5) < 0.02   # 소성 plowing → V₁ ∝ F^1.5
print("PASS: 접촉응력 GPa·압입 sub-nm·연화 8배 시너지·V₁∝F^1.5 재현")
```

## 5. 입자 크기·농도 효과와 두 극단 레짐 — Luo-Dornfeld 활성입자 모델
- **활성입자(active abrasive)**: Luo & Dornfeld(2001, doi:10.1109/66.920723)와 후속 입도분포 논문
  (2003, doi:10.1109/tsm.2003.815199)은 슬러리 전 입자가 아니라 **패드-웨이퍼 간극을 메우고 하중을
  전달하는 큰 입자(분포의 상위 꼬리)만** 제거에 기여한다고 본다. 압력이 오르면 더 많은 입자가
  활성화되어, 웨이퍼-입자·입자-패드 양 계면 완전소성 가정 하에서 **MRR ∝ P^{1/2}·V** 형태를 얻는다
  ([[preston-luo-dornfeld-mrr]]의 Preston P¹ 대비 지수↓). §4(C)의 단일입자 V₁∝F^{1.5}가 이 모델의
  미시적 구성요소다. (원문 IEEE 유료 — DOI 실존확인, 활성입자수 폐형식 유도는 **초록·2차 인용만 확인**.)
- **농도 포화**: 입자농도↑ → 활성입자수↑ → MRR↑이나 곧 포화(간극당 수용 가능한 입자 한계) —
  [[slurry-components-overview]] §2의 "MRR ↑후 포화"와 정합.
- **두 극단 레짐**:
  (i) **순수 기계 지배**(경질막·저화학): §3 탄성접촉으로 제거 비효율, 스크래치·결함 위험.
  (ii) **화학용해 지배**(정지식각률 SER 큼): 등방부식으로 평탄화 상실·dishing. Kaufman(1991)이
  W CMP에서 정지식각을 억제(자기제한 WO₃)해야 패턴 W가 균일·무결함으로 남는다고 명시. Cu에서도
  "제어된 마모는 passivation과 기계마모의 **시너지**"이며 둘의 속도가 균형을 이룰 때 제거율이
  정점을 가진다(Wear 2013, doi:10.1016/j.wear.2013.08.001, 시너지 파라미터 ΔR_C-A; 원문 유료·초록 확인).
- **정량축(정지식각 vs CMP 비)**: 잘 설계된 슬러리에서 CMP 제거율은 정지식각률의 수 배~수십 배로,
  기계적 박리가 없으면 제거가 거의 멈춘다(W는 pH>6에서 정지용해≈0으로 접근, 검색스니펫 2차 확인;
  절대 배수는 슬러리·재료 의존 **미검증**).

## 6. 한계/미검증 (정직 표기)
- 입자당 하중 F(수 nN~수백 nN)는 활성입자 통계에서 나오는 값으로, 여기선 **오더만** 채택하고 절대값은
  실측 캘리브레이션 대상 — **미검증**.
- 경도 H(SiO₂ 8–9 GPa, Cu 1–2 GPa, 연화막 <1 GPa)는 나노압입 **2차 인용** 오더값. §4 시너지 배수(4배·8배)는
  H 비율에 대한 **상대적·해석적** 결과(δ∝1/H, V∝H^{-1.5})라 정확하지만, 실제 연화 정도는 슬러리별 미검증.
- Luo-Dornfeld MRR∝P^{1/2}·V의 지수는 원문(유료) 폐형식 유도를 직접 재현하지 못하고 **DOI 실존확인+2차
  인용**으로만 확인. §4는 그 미시 구성요소(단일입자 소성 plowing)만 독립 재현했다.
- plowing 홈 단면 A_f 근사(구형 압자, δ≪R)는 절삭효율 1(파낸 것 전부 제거) 가정 — 실제 ploughing vs
  cutting 구분은 [[preston-luo-dornfeld-mrr]] §3 "MRR 과대예측" 한계와 동일한 미해결 지점.

## 7. 자기시험
→ [[../../agents/slurry-chemist/EXAMS.md]] Lv2-2 문항 참조.
