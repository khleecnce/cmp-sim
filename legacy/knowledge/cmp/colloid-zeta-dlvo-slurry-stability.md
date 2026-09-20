<!-- V2-SECTION: R2-slurry | 분배완료 2026-09-08 | 근거: colloid, dlvo, ph, slurry, zeta | 정본: ARCHITECTURE-V2.md §3 -->
# 콜로이드 화학 기초 — 제타전위·전기이중층·DLVO 이론·CMP 슬러리 안정성

> 에이전트: slurry-chemist Lv1-1 | 작성일: 2026-09-05
> [[preston-luo-dornfeld-mrr]] [[../materials/hertz-gw-contact-mechanics]] [[../physics/cmp-kinematics-rotary]]

## 1. 왜 필요한가 — 슬러리 안정성이 CMP의 출발점
CMP 슬러리는 연마입자(세리아/실리카/알루미나, 수십~수백 nm)를 물에 분산시킨 콜로이드다.
[[preston-luo-dornfeld-mrr]]의 Preston 계수 $K_p$나 Luo-Dornfeld의 "활성입자" 개념은 모두
**입자가 낱개로 잘 분산되어 있다**는 암묵적 전제 위에 선다. 입자가 응집(agglomeration)하면
(a) 유효 입경이 커져 스크래치·결함이 급증하고 (b) 침강으로 슬러리 공급이 불안정해지며
(c) 유효 활성입자 수가 바뀌어 MRR이 드리프트한다. 따라서 "언제 분산되고 언제 응집하는가"를
지배하는 콜로이드 화학이 슬러리 설계의 1층이다. 핵심 조절변수는 **pH**(표면전하)와
**이온세기**(반발 도달거리) 두 개다.

## 2. 제타전위와 전기영동 이동도 (측정)
입자 표면은 물속에서 하전되고, 그 주위에 반대이온이 모여 **전기이중층(EDL)**을 이룬다.
표면에 단단히 붙어 함께 움직이는 이온층의 바깥 경계(전단면, slipping plane)에서의 전위가
**제타전위 $\zeta$**다 — 표면전위 $\psi_0$ 자체는 측정 불가이고, 실험적으로 접근 가능한 대리값이 $\zeta$다.

측정은 전기장 $E$ 하에서 입자 이동속도(전기영동 이동도 $\mu_E=v/E$)로부터 역산한다. **Henry 식**:
$$ \mu_E = \frac{2\,\varepsilon_0\varepsilon_r\,\zeta}{3\eta}\,f(\kappa a) $$
- $f(\kappa a)$: Henry 함수. 두 극한 —
  - **Smoluchowski** $f=1.5$: $\kappa a \gg 1$ (큰 입자·고이온세기, 수용액 통상. 입경 >0.2 µm, 염 >$10^{-3}$ M).
  - **Hückel** $f=1.0$: $\kappa a \ll 1$ (작은 입자·저유전 비수계).
- 출처: Malvern "Electrophoretic Light Scattering – Overview" (공개 PDF, macro.lsu.edu/HowTo/MALVERN) —
  "$f(\kappa a)$ ranges from 1 (Hückel) to 1.5 (Smoluchowski)" 명시 확인. 원 이론 D.C. Henry (1931).
- **안정성 경험칙**: $|\zeta|\gtrsim 30$ mV 이면 정전반발이 충분해 분산 안정, $|\zeta|<~15$ mV 이면 응집 경향
  (dispersion.com "Zeta Potential – A Short Tutorial", 정성 서술 확인; 정확한 임계는 계·입경 의존, **미검증**).
- **재현/대조**: 아래 코드에서 $\mu_E=-3\times10^{-8}\,\mathrm{m^2/Vs}$ → Smoluchowski $\zeta=-38.4$ mV,
  Hückel $\zeta=-57.6$ mV (비 정확히 1.5), 콜로이드 전형 범위와 일치.

## 3. 전기이중층 두께 — Debye 길이 $\kappa^{-1}$
반발의 **도달거리**를 정하는 특성길이. 대칭 $z{:}z$ 전해질에서
$$ \kappa^{-1} = \sqrt{\frac{\varepsilon_0\varepsilon_r k_BT}{2\,N_A e^2\,z^2\,I\cdot 10^3}}
   \;\;\xrightarrow[\text{물, 25°C, 1:1}]{}\;\; \kappa^{-1}\approx\frac{0.304}{\sqrt{I}}\ \text{nm} $$
($I$ = 이온세기 mol/L). 이온세기가 오르면 이중층이 **압축**되어 반발이 짧아진다 — 이것이 염
추가가 응집을 부르는 물리다.
- 출처: 표준식은 Israelachvili *Intermolecular and Surface Forces* 3rd ed.(2011) — 원서 미확보,
  **2차 인용**. 앵커 대조값: dispersion.com 튜토리얼 "$\kappa^{-1}\approx$ 1 nm @ 0.1 M, 10 nm @ 0.001 M".
- **재현/검증**: 정확식(위 좌변)이 근사식 $0.304/\sqrt I$와 상대오차 0.1%로 일치, 문헌 앵커값과도
  0.96 nm(@0.1 M)·9.62 nm(@0.001 M)로 대조 성공 (코드 12/12 PASS).

## 4. DLVO 이론 — 총상호작용에너지 $V_T = V_{vdW} + V_{edl}$
Derjaguin–Landau–Verwey–Overbeek 이론: 두 입자 사이 총 위치에너지를 인력·반발의 합으로 본다.
표면간 거리 $h$, 입자반경 $a$에 대해 (동일 구-구, Derjaguin 근사):
$$ V_{vdW}(h) = -\frac{A\,a}{12\,h}, \qquad
   V_{edl}(h) = 2\pi\,\varepsilon_0\varepsilon_r\,a\,\zeta^2\,\ln\!\big(1+e^{-\kappa h}\big) $$
- $A$ = **Hamaker 상수**(매질을 낀 물질 쌍 고유, 물속 산화물 통상 $\sim10^{-20}$ J 오더).
  van der Waals 인력은 $\zeta$·이온세기와 무관하게 늘 존재하는 배경 인력.
- $V_{edl}$은 $\zeta^2$에 비례(전하가 반발을 키움)하고 $e^{-\kappa h}$로 감쇠(도달거리 $\kappa^{-1}$).
- 출처: 일정전위 구-구 형태 $2\pi\varepsilon_0\varepsilon_r a\zeta^2\ln(1+e^{-\kappa h})$는
  arXiv:1009.6150 (Constant $\zeta$ phase diagram, 2010) 및 표준 교과서와 일치 확인.
- **곡선의 형태**(문헌 대조 대상): 근거리 **1차 최소**(강한 인력, 비가역 응집) → 중간 **에너지장벽**
  ($\kappa^{-1}$ 근처, 이게 높아야 분산 안정) → 원거리 얕은 **2차 최소**(약한 가역 응집/floc).
- **재현/검증** (실리카 $a{=}50$ nm, $\zeta{=}{-}40$ mV, $A{=}0.85\times10^{-20}$ J):
  - 이온세기 ↑ → 장벽 46.7→37.7→22.4 kT (1→10→100 mM) 단조 감소, 2차최소 +1.1→−0.33→−1.29 kT로 심화.
    문헌 서술 "이온세기 증가 시 장벽 낮아지고 2차최소 깊어짐"과 정성 일치.
  - **pH 효과**(IEP 근접): 같은 10 mM에서 $|\zeta|$만 40→20→10 mV로 낮추면 장벽 37.7→4.6→−0.2 kT로
    붕괴 → 응집. $V_{edl}\propto\zeta^2$의 직접 귀결.

## 5. CMP 슬러리(세리아/실리카/알루미나)의 pH·이온세기 의존 안정성
표면전하가 0이 되는 pH가 **등전점(IEP)**이며, 이 근처에서 $\zeta\to0$이라 장벽이 무너져 가장 불안정하다.
문헌 IEP(수정 없는 순수 입자, 대략값; **2차 인용/미검증 폭 있음**):
- **실리카** IEP ≈ 2 (그 위 pH에서 음전위) — ScienceDirect Topics "Silica-Based Slurry".
- **세리아(CeO₂)** IEP ≈ 6.5 — ScienceDirect Topics "Ceria Based Slurry". 실리케이트 이온 흡착 시 IEP가
  낮은 pH로 이동(세리아-실리카 상호작용, oxide CMP 화학흡착 모델과 직결).
- **알루미나(Al₂O₃)** IEP ≈ 8–9 (문헌 "IEP>5") — IOPscience "Effects of CMP Slurry Chemistry on the Zeta
  Potential of Alumina Abrasives", *J. Electrochem. Soc.* (2006, doi:10.1149/1.2198128, 초록만 확인).
- Hamaker 상수 예: 6H-SiC–물–실리카 $3.3\times10^{-20}$ J, 6H-SiC–물–세리아 $8.5\times10^{-20}$ J
  (ScienceDirect Topics 재인용, **2차 인용**). 실리카-물-실리카는 통상 $\sim0.85\times10^{-20}$ J 오더로 채택(본 재현값).
- **실무 함의**: 슬러리 pH는 (i) 연마 화학반응(산화/passivation, [[preston-luo-dornfeld-mrr]] 이후 Lv2-1에서)과
  (ii) 콜로이드 안정성을 **동시에** 지배하므로 최적 pH는 둘의 절충이다. IEP 근처는 반응성엔 유리해도
  응집·스크래치 위험이 커 통상 회피하고, 분산제(정전/입체 반발)로 $|\zeta|$나 입체장벽을 보강한다.

## 6. 다른 에이전트 영역과의 연결·한계
- **Preston/활성입자로 연결**: 응집은 유효 입경분포를 바꿔 [[preston-luo-dornfeld-mrr]]의 Luo-Dornfeld
  활성입자 통계를 교란 → $K_p$ 드리프트. DLVO 안정성은 그 모델들의 전제조건이다.
- **접촉역학과의 대비**: [[../materials/hertz-gw-contact-mechanics]]가 패드-웨이퍼 asperity 접촉의
  van der Waals·소성변형을 다루듯, 여기선 입자-입자/입자-웨이퍼의 van der Waals·정전 상호작용을 다룬다.
  둘 다 최종적으로 입자에 전달되는 국소하중([[../physics/cmp-kinematics-rotary]]의 속도장과 곱해져 MRR)을 좌우.
- **한계/미검증**: (a) DLVO는 평활·강체 구 가정 — 실제 세리아는 각진 다면체·표면 거칠기·화학흡착이 있어
  정량 예측엔 확장(입체반발·비-DLVO 수화력) 필요. (b) 인용 IEP·Hamaker 값은 다수가 2차 인용이라 절대값은
  재료·전처리별 실측 캘리브레이션 대상. (c) 본 재현은 **정성 형태(장벽 존재/소멸)** 대조까지이며 특정 슬러리의
  절대 응집속도(CCC)는 검증하지 않았다.

## 7. 재현 코드
`sim/tier2_physics/dlvo_colloid.py` — Debye 길이(정확식 vs 0.304/√I vs 문헌앵커),
Henry식(Smoluchowski/Hückel), DLVO $V_T(h)$ 장벽·2차최소(이온세기·pH 스캔). **15/15 PASS**
(`.venv/bin/python sim/tier2_physics/dlvo_colloid.py`로 직접 재실행 확인, 2026-09-13).

```python verify
import math

EPS0 = 8.8541878128e-12
KB = 1.380649e-23
NA = 6.02214076e23
QE = 1.602176634e-19
EPSR_WATER = 78.5


def debye_length_nm(I_molar, T=298.15, epsr=EPSR_WATER, z=1):
    kappa2 = (2.0 * (z * QE) ** 2 * I_molar * 1000.0 * NA) / (EPS0 * epsr * KB * T)
    return 1.0 / math.sqrt(kappa2) * 1e9


def debye_length_approx_nm(I_molar):
    return 0.304 / math.sqrt(I_molar)


# §3: 정확식 vs 근사식(0.304/sqrt(I)) 상대오차, 문헌 앵커(dispersion.com ~1nm@0.1M, ~10nm@0.001M)
for I, anchor in [(0.1, 1.0), (0.001, 10.0)]:
    exact = debye_length_nm(I)
    approx = debye_length_approx_nm(I)
    rel_err = abs(exact - approx) / approx
    assert rel_err < 0.02, f"정확식/근사식 상대오차 2% 이내여야 함: I={I} rel_err={rel_err:.4f}"
    assert abs(exact - anchor) / anchor < 0.2, f"문헌 앵커값과 20% 이내 정합 필요: I={I} exact={exact:.2f} anchor={anchor}"

# §2: Henry 식 역산 — Smoluchowski(f=1.5) vs Huckel(f=1.0), 비율 정확히 1.5
def henry_zeta(mu_E, f_ka, eta=8.9e-4, epsr=EPSR_WATER):
    return 3.0 * eta * mu_E / (2.0 * EPS0 * epsr * f_ka)

mu_E = -3.0e-8
zeta_smol = henry_zeta(mu_E, 1.5)
zeta_huckel = henry_zeta(mu_E, 1.0)
ratio = zeta_huckel / zeta_smol
assert abs(ratio - 1.5) < 1e-9, f"Huckel/Smoluchowski 비는 정확히 1.5여야 함(같은 mu_E, f만 다름): {ratio}"
zeta_smol_mV = zeta_smol * 1000
assert -40 < zeta_smol_mV < -37, f"Smoluchowski zeta ~ -38.4 mV 기대: {zeta_smol_mV:.1f}"

print(f"Debye 길이: 0.1M exact={debye_length_nm(0.1):.2f}nm, 0.001M exact={debye_length_nm(0.001):.2f}nm (문헌 앵커와 20% 이내)")
print(f"Henry: zeta_Smoluchowski={zeta_smol_mV:.1f} mV, 비율(Huckel/Smol)={ratio:.2f}")
print("PASS: Debye 길이 근사식/문헌앵커 정합, Henry식 Smoluchowski/Huckel 비율 1.5 확인")
```

## 8. 자기시험
→ [[../../agents/slurry-chemist/EXAMS.md]] Lv1-1 문항 참조.
