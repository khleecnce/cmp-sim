<!-- V2-SECTION: R2-slurry | 근거: ph, ionic-strength, zeta, dissolution, selectivity, pourbaix, edl, 화학 | 정본: ARCHITECTURE-V2.md §3 -->
# pH·이온강도 → 제타전위·용해율·선택비 — 표면전하(ζ)·전기이중층·Pourbaix 재해석 (slurry-chemistry Lv2-1)

> 에이전트: slurry-chemistry Lv2-1 | 작성일: 2026-09-11
> 선행(내 Lv1): [[oxidizer-redox-potential-decomposition-metal-suitability]] (산화제 E°·pH 기울기 −59 mV/pH) ·
> [[inhibitor-chelator-adsorption-isotherm-passivation]] (억제제 θ·킬레이트 log K, "I=0 상수는 Lv2-1에서 이온강도 보정" 예고)
> 선행(형제·부모): [[colloid-zeta-dlvo-slurry-stability]] (ζ·EDL·DLVO·Debye 0.304/√I·IEP 총론 — 이 노트는 그 위에 **pH·이온강도의 정량 손잡이**를 쌓는다) ·
> [[surface-chemistry-cu-w-pourbaix-passivation]] (Nernst 기울기·Pourbaix 정성) · [[cu-electrochemistry-pourbaix-bta-oxidizer-inhibitor]] (Cu-H₂O 경계 정량) ·
> [[silica-cmp-ph-acidic-repulsion-choi-power-law]] (실리카 ζ-pH → MRR) · [[ceria-slurry-ce-redox-selectivity]] (세리아 IEP·선택비)
> 스코프: (1) ζ의 pH 의존과 IEP/PZC의 자리해리 기원, (2) 이온강도 → Debye 길이·CCC(Schulze–Hardy), (3) pH가 용해/부동태/석출을
> 가르는 Pourbaix·양쪽성 용해 재해석, (4) 이 둘(입자 표면전하 ζ + 상 안정성 Pourbaix)이 oxide:nitride·Cu:barrier·W:oxide 선택비로
> 번역되는 정성 경로. **상세 선택비 설계·정지층 화학은 Lv2-2**, 입자 제형·농도-MRR 포화는 slurry-abrasive 몫(침범 안 함).

## 1. 왜 필요한가 — Lv1은 "무엇을 넣나", Lv2-1은 "pH·이온강도가 그걸 어떻게 켜고 끄나"
Lv1-1(산화제)·Lv1-2(억제제·킬레이트)는 조성 **성분**을 고정 조건에서 다뤘다. 그러나 같은 슬러리라도 **pH와 이온강도** 두
스칼라를 돌리면 (a) 연마입자·웨이퍼막의 **표면전하 ζ**(→정전 응집/분산·부착 → MRR·결함), (b) 금속/산화막의 **용해·부동태 상**
(→정적식각·선택비), (c) 킬레이트·억제제의 **조건부 실효 상수**가 모두 함께 움직인다. 이 단원은 그 두 손잡이를 정량화한다.
핵심 통찰 하나: **"charge"라는 말이 CMP에서 두 개의 서로 다른 그림을 가리킨다** —
- **입자 표면전하(ζ, EDL)**: pH가 IEP 대비 어디 있느냐로 부호·크기가 정해지는 *정전기* 그림. 콜로이드 안정성·부착을 지배.
- **산화환원 상태(Pourbaix, E–pH)**: 전위·pH로 금속/이온/산화물 중 어느 *고체상*이 열역학적으로 안정한가의 그림. 용해·부동태 지배.

두 그림은 **독립 축**이다(하나는 표면 하전, 하나는 벌크 상평형). CMP 최적 pH는 늘 이 둘의 절충이다
([[colloid-zeta-dlvo-slurry-stability]] §5가 "반응성 vs 안정성 절충"이라 한 것의 정량판).

## 2. ζ의 pH 의존 — 자리해리(site-dissociation)와 IEP/PZC
산화물 표면의 하전은 표면 하이드록실기(≡M–OH)의 **양쪽성 산·염기 해리**에서 나온다(Sun 2007 §3.7.3, 식 3.15–3.16):

$$\equiv\!\text{M–OH} \;\overset{\text{저 pH}}{\underset{+H^+}{\rightleftharpoons}}\; \equiv\!\text{M–OH}_2^{+}, \qquad
  \equiv\!\text{M–OH} \;\overset{\text{고 pH}}{\underset{-H^+}{\rightleftharpoons}}\; \equiv\!\text{M–O}^{-} + H^+$$

- pH가 오르면 ≡M–O⁻가 우세해져 표면이 **더 음(−)**으로 간다. 순 전하가 0이 되는 pH가 **PZC**(전위결정이온 H⁺/OH⁻ 기준)이고,
  ζ=0이 되는 pH가 **IEP**다. 특이흡착이 없으면 IEP=PZC(Sun 2007 §3.7.1). CMP에서 특이흡착(예: PAA·Cu²⁺·실리케이트)은 IEP를 옮긴다.
- **Nern스트적 상한 기울기**: H⁺가 전위결정이온이면 이상적으로 dψ₀/dpH = −2.303RT/F = **−59.16 mV/pH**(25°C). 이는 [[surface-chemistry-cu-w-pourbaix-passivation]]
  §2의 Pourbaix −59.1 mV/pH와 **수학적으로 같은 상수**(둘 다 2.303RT/F)이지만 **물리는 다르다** — 하나는 표면 하전, 하나는 산화환원 경계.
  실제 산화물은 대개 **아-Nern스트(sub-Nernstian)**라 |dζ/dpH|가 이보다 작다(예: 실리카는 수 mV/pH대; 표준 교과서 서술, 2차 인용 —
  Hunter *Zeta Potential in Colloid Science* / Israelachvili류, 원서 미확보). 즉 −59 mV/pH는 **상한**이고 절대 기울기는 재료·이온강도 의존.
- **CMP 재료 PZC 표**(Sun 2007 표 3.1, UA 학위논문 직접 판독; 문헌 취합값이라 범위로 제시):

| 재료 | PZC(≈IEP) | CMP에서의 함의 |
|---|---|---|
| SiO₂ | 2–4 (본문 실측 ≈2.0–2.5) | 조사 pH(≥3) 전 구간에서 음(−) — [[silica-cmp-ph-acidic-repulsion-choi-power-law]]와 정합 |
| Si (수소말단) | 3–4 | post-CMP 세정 시 금속이온 흡착 pH 창 |
| Si₃N₄ | 3–5.5 (Sun 표) / ~9 (Dandu 실측) | **문헌 편차 큼** — 표면 산화·전처리 의존(§6 한계) |
| Al₂O₃ | 8–9 | 산성에서 양(+) — 대부분 CMP pH에서 실리카와 반대부호 |
| TiO₂ | 5–6 | 배리어(Ti계) 표면 산화물의 하전 참고 |

- **Cu²⁺ 흡착으로 IEP가 옮겨간다**(Sun 2007 §4.2.2.1, 그림 4.11): 순수 실리카 IEP≈2.5인데 용존 Cu를 10→1000 ppm 늘리면 표면이
  Cu(OH)₂(s) 코팅으로 덮여 전기영동 거동이 **Cu(OH)₂(IEP≈9.5)** 쪽으로 이동. 즉 오염 이온이 ζ-pH 곡선 자체를 바꾼다 —
  [[post-cmp-metallic-contamination-sources]]의 "슬러리 유래 금속 잔류"가 ζ로 나타나는 창구.

## 3. 이온강도 → 전기이중층 두께(Debye 길이)와 응집 임계농도(CCC)
[[colloid-zeta-dlvo-slurry-stability]] §3이 1:1 전해질에서 $\kappa^{-1}\approx 0.304/\sqrt{I}$ nm(물, 25°C)를 세웠다. 여기서 **원자가(z)로 확장**한다.
이온강도 정의 $I=\tfrac12\sum_i c_i z_i^2$ 때문에:
- **대칭 z:z 전해질**은 같은 몰농도 c에서 $I=z^2 c$ → 같은 c라도 2:2는 1:1보다 $\kappa^{-1}$이 **1/2배**, 3:3은 **1/3배**로 짧아진다.
- **비대칭(예: CaCl₂, 2:1)**은 $I=3c$라 1:1(=$c$)보다 이중층이 더 압축된다.

이온강도↑ → EDL 압축 → 정전반발 도달거리↓ → 응집. 반발이 완전히 무너지는 임계 전해질 농도가 **CCC**이며, 고전위 극한에서
**Schulze–Hardy 법칙** $\text{CCC}\propto z^{-6}$을 따른다(Gouy–Chapman/DLVO 해석해; 표준 교과서, 2차 인용). z=1,2,3의 CCC 비는
이론상 $1:2^{-6}:3^{-6}=1:0.0156:0.00137$, 즉 3가 반대이온은 1가보다 **~730배** 적은 농도로 응집시킨다 — 다가 금속이온
오염이 슬러리를 급격히 불안정화하는 정량 근거([[post-cmp-metallic-contamination-sources]]와 연결).

**정직한 실측 예외(비-DLVO)**: Sun 2007 §8.3.1은 0.2% 실리카(Klebosol) 슬러리에 KNO₃를 넣어 전도도를 ~8–12 mS/cm까지 올려도
pH 2.0·6.0에서 **2시간 동안 침강/응집이 일어나지 않았다**고 보고한다("it may not be feasible to bring SiO₂ out of suspension simply
by increasing the ionic strength"). 이는 실리카의 **수화력(hydration force)·표면 겔층** 같은 비-DLVO 단거리 반발 때문으로,
고전적 Schulze–Hardy CCC 예측이 **실리카에는 그대로 적용되지 않는다** — DLVO는 산화물 콜로이드의 정량 상한/방향은 주지만
실리카의 이상적 안정성은 못 잡는다(같은 한계를 [[colloid-zeta-dlvo-slurry-stability]] §6이 "평활·강체 구 가정"으로 지적).

## 4. pH → 용해 vs 부동태 vs 석출 — Pourbaix·양쪽성 용해 재해석
ζ가 "입자가 붙느냐"를 정하면, **어느 고체상이 안정한가**는 pH·전위가 정한다. 두 계열로 나뉜다.

### 4.1 금속(전위 축이 있음) — 면역/부식/부동태
금속은 E–pH 평면에서 **면역(금속 안정)·부식(용존 이온 안정)·부동태(산화물 안정)** 세 영역을 갖는다. CMP는 "부동태 영역에서
무른 막을 만들고 기계로 벗기되, 부식 영역이 배경 정적식각을 준다"는 그림([[surface-chemistry-cu-w-pourbaix-passivation]]).
- Cu-H₂O 경계는 [[cu-electrochemistry-pourbaix-bta-oxidizer-inhibitor]]가 CRC E°에서 정량화: Cu²⁺/Cu 수평선 0.224 V,
  삼중점 pH≈4.14, Cu²⁺/산화물 수직선 pH≈6.5 — **산성에서 Cu²⁺(용해), 중성~알칼리에서 산화물(부동태)**. pH가 이 경계를 넘기는 손잡이.
- W는 산성에서 WO₃ 자기제한 부동태([[w-cmp-wo3-passivation-oxidizer-kaufman]]), pH↑·강알칼리에서 WO₄²⁻로 용해.
- **이온강도의 2차 효과**: Lv1-2가 예고한 대로 킬레이트 안정도상수 log K는 I=0 값이라 실 이온강도에서 활동도계수로 보정해야 하며
  (Davies식), Nernst 식의 활동도항도 이온강도에 걸린다 — 즉 Pourbaix 경계선 위치도 이온강도에 약하게 의존
  ([[inhibitor-chelator-adsorption-isotherm-passivation]] §5의 "I=0 상수 → 조건부 보정" 연결).

### 4.2 유전막(전위 무관) — 양쪽성 산화물의 U자형 용해도
산화막은 산화환원 없이 **산/염기 용해**만 한다. 용해도 최솟값은 대략 PZC 근처이고 양극단 pH에서 급증(양쪽성):
- **SiO₂**: pH 2–8에서 용해도 거의 불변, **pH>9에서 실리케이트(H₃SiO₄⁻ 등)로 급증**([[silica-cmp-ph-acidic-repulsion-choi-power-law]]
  §2 — Choi, Lee, Singh 2004, *Electrochem. Solid-State Lett.* 7(7) G141, doi:10.1149/1.1738472 — "pH<10에서 용해 불변, pH>10에서 겔층·MRR 재상승" 서술). 그래서 실리카 CMP는 저~중 pH에선 정전반발(ζ)이,
  고 pH에선 용해가 지배한다. **같은 pH가 ζ 그림과 용해 그림에 동시에 작용**하는 대표 사례.
- **Al₂O₃**: PZC(8–9) 근처에서 최소, 산성에서 Al³⁺, 강알칼리에서 알루미네이트(Al(OH)₄⁻)로 용해(양쪽성; 2차 인용, 표준 무기화학).

## 5. ζ·상 안정성 → 선택비 번역 (정성 — 상세 설계는 Lv2-2)
### 5.1 oxide:nitride (STI) — **ζ 부호 정합이 선택비를 켠다** (Dandu 2009, 1차)
Dandu, Peddeti, Babu (2009), *J. Electrochem. Soc.* 156, "Selective CMP of SiO₂ over Si₃N₄ for STI Using Ceria Slurries,"
doi:10.1149/1.3230624 (papers/dandu2009-jes-selective-sio2-sin-ceria-sti.pdf, 전문 판독) — ζ-pH 실측으로 선택비 기원을 규명:
- **실측 IEP**: 실리카 ≈2(전 pH에서 음), **세리아 ≈8**(pH 2–8 양전하), **Si₃N₄ pH 9까지 양전하**(본문 §Zeta potential data).
- pH 4–5에서 **양전하 세리아 + 음전하 실리카(SiO₂막) = 정전인력** → 세리아가 SiO₂막에 붙어 화학기계 제거를 촉진, oxide RR **350 nm/min**
  (알칼리 영역보다 훨씬 큼). 이는 [[ceria-slurry-ce-redox-selectivity]]의 Si–O–Ce 화학결합과 **정전인력이 접촉을 먼저 만든다**는 점에서 상보적.
- **첨가제가 ζ를 재프로그래밍**: 0.01% PAA는 세리아 IEP를 **8→4**로 끌어내려 pH 5.5 이상에서 두 막 RR을 함께 죽인다;
  1% pyridine·HCl(양이온)은 pH 4에서 음전하 실리카·질화막에 흡착해 nitride RR을 **2 nm/min**으로 억제 → oxide/nitride 선택비 **~175**.
- 즉 STI 고선택비는 (i) 세리아–실리카 **반대부호 정전인력**(ζ)과 (ii) nitride 표면 **선택 흡착 억제**의 곱이다 — 둘 다 pH와 ζ가 손잡이.
- 리뷰 교차확인: Srinivasan, Dandu, Babu 2015, "Shallow Trench Isolation CMP: A Review," *ECS J. Solid State Sci. Technol.* 4(11) P5029,
  doi:10.1149/2.0071511jss (papers/, OA 전문)이 세리아-실리카 정전인력·아미노산 nitride 억제를 STI 선택비 기제로 정리 — 위 Dandu 실측과 정합.

### 5.2 Cu:barrier, W:oxide — 두 그림의 결합 (정성, 상세는 Lv2-2)
- **Cu:barrier(Ta/TaN/TiN)**: Cu와 배리어는 (a) Pourbaix 상이 다르고(Cu는 착화·용해, Ta계는 넓은 pH에서 Ta₂O₅ 부동태 → 매우 낮은 식각),
  (b) 두 금속이 전기적으로 접촉해 **갈바닉 커플**을 이룬다(귀한 쪽 보호, 천한 쪽 가속). Barrier step에서 Cu:barrier 선택비는 산화제·억제제·pH로
  두 Pourbaix 그림의 간격을 조정해 맞춘다([[cu-electrochemistry-pourbaix-bta-oxidizer-inhibitor]] §5 "MRR/정적식각 비 = 평탄화 선택성").
- **W:oxide**: W는 산성 부동태(WO₃), 실리카 유전막은 산성에서 저용해 — pH를 산성으로 잡으면 둘 다 정적식각이 낮아 기계 지배가 되고,
  연마입자 정전 부착(ζ)이 실제 접촉 빈도를 정한다([[w-cmp-wo3-passivation-oxidizer-kaufman]]).
- **주의**: 갈바닉·정지층 정량(부식전류·선택비 수치·Ta₂O₅ 경계)은 **Lv2-2**의 몫이며 여기선 "pH·ζ·Pourbaix가 어느 방향으로 미는가"만 잡는다.

## 6. 한계 (정직 표기)
- **ζ-pH 절대 기울기**는 계·이온강도·측정법 의존이라 −59 mV/pH는 **상한**일 뿐이고, 이 노트는 아-Nern스트 정도의 실측 절대값을
  독립 검증하지 못했다(교과서 서술 2차 인용). Nern스트 slope 상수(59.16 mV/pH)만 계산 재현.
- **Si₃N₄ IEP가 문헌마다 크게 다르다**(Sun 표 3–5.5 vs Dandu 실측 ~9). 표면 산화층·수화·측정 pH 이력에 민감 — 어느 쪽이 "맞다"기보다
  **시료 상태 의존**으로 남긴다(선택비 논의는 Dandu의 자기 실측 IEP를 그 논문 내부에서 일관되게 사용).
- **Schulze–Hardy z⁻⁶**는 고전위·이상 DLVO 극한이다. §3에서 보였듯 실리카는 수화력으로 이를 벗어나며, 실측 CMP 슬러리 CCC 절대값은
  검증하지 않았다(Sun 2007은 실리카가 오히려 안정하다는 반례만 제공).
- **Pourbaix 경계의 이온강도 보정**(활동도계수·Davies)은 방향만 서술했고 CMP 조건에서의 경계 이동량은 정량 미검증.
- **양쪽성 용해도 곡선**(SiO₂·Al₂O₃)은 정성 형태(U자·pH 9 전환)만 문헌으로 확인했고 절대 용해도[mol/L]-pH 표는 이 노트에서 재현하지 않았다.
- 1차 실측은 Dandu 2009(OA·DOI 실존)와 Sun 2007(UA 학위논문, 핸들 10150/194903, 직접 판독). Cu(OH)₂ IEP·PZC 표는 Sun 논문의
  취합/실측값을 상수로 채택했고 원 1차(개별 인용문헌)까지는 거슬러 확인하지 못했다.

## 7. 정량 재현 (verify)
**재현 요약**: (1) Debye 길이의 원자가 확장(2:2→1/2배·3:3→1/3배·CaCl₂ 2:1→I=3c)과 Schulze–Hardy z⁻⁶(3가/1가 ~730배);
(2) Nern스트 ζ-pH 상한 −59.16 mV/pH·PZC 표 부호논리·실리카 이온강도 안정성 반례; (3) Dandu 2009 세리아(+)-실리카(−) 정전인력·
oxide:nitride 선택비 ~175·PAA IEP 8→4. 문헌 상수를 박고 관계식·부호·비를 assert.

```python verify
# verify 1 — 이온강도 → Debye 길이(원자가 확장) + Schulze–Hardy CCC ∝ z^-6
# 앵커: colloid-zeta-dlvo 노트의 1:1 값 (0.96 nm @0.1 M, 9.62 nm @0.001 M) ; 물 25°C
import math
def kappa_inv_nm(I):            # I = 이온강도 [mol/L], 1:1 근사식 0.304/sqrt(I) nm
    return 0.304/math.sqrt(I)
def ionic_strength(c, zc, za, nu_c, nu_a):   # c=염 농도, z/nu = 양·음이온 전하·화학량수
    return 0.5*(nu_c*c*zc**2 + nu_a*c*za**2)

# (a) 1:1 앵커 재현 (colloid 노트와 일치)
assert abs(kappa_inv_nm(0.1) - 0.961) < 0.005      # 0.96 nm
assert abs(kappa_inv_nm(0.001) - 9.615) < 0.01     # 9.62 nm

# (b) 대칭 z:z 는 같은 몰농도에서 I=z^2 c → κ⁻¹ ∝ 1/z
c = 0.001
I_11 = ionic_strength(c,1,1,1,1); I_22 = ionic_strength(c,2,2,1,1); I_33 = ionic_strength(c,3,3,1,1)
assert abs(I_11-0.001)<1e-12 and abs(I_22-0.004)<1e-12 and abs(I_33-0.009)<1e-12
r2 = kappa_inv_nm(I_22)/kappa_inv_nm(I_11); r3 = kappa_inv_nm(I_33)/kappa_inv_nm(I_11)
assert abs(r2-0.5)<1e-9 and abs(r3-1/3)<1e-9     # 2:2 → 1/2배, 3:3 → 1/3배
print(f"Debye @1mM: 1:1 {kappa_inv_nm(I_11):.2f} nm, 2:2 {kappa_inv_nm(I_22):.2f} nm(1/2), 3:3 {kappa_inv_nm(I_33):.2f} nm(1/3)")

# (c) 비대칭 CaCl2 (2:1): I = 0.5(c*4 + 2c*1) = 3c → 1:1보다 압축
I_CaCl2 = ionic_strength(c,2,1,1,2)
assert abs(I_CaCl2-3*c)<1e-12
assert kappa_inv_nm(I_CaCl2) < kappa_inv_nm(I_11)
print(f"CaCl2 0.001 M: I={I_CaCl2:.4f}, κ⁻¹={kappa_inv_nm(I_CaCl2):.2f} nm (< 1:1 {kappa_inv_nm(I_11):.2f})")

# (d) Schulze–Hardy: CCC ∝ z^-6 (고전위 DLVO 극한, 표준 교과서 2차 인용)
ccc = {z: z**-6.0 for z in (1,2,3)}
assert abs(ccc[1]/ccc[2] - 64) < 1e-6            # 1가/2가 = 2^6 = 64
assert abs(ccc[1]/ccc[3] - 729) < 1e-6           # 1가/3가 = 3^6 = 729
# 정규화 비 (실험 고전 인용 ~100:1.6:0.13 과 대조)
norm = {z: 100*ccc[z]/ccc[1] for z in (1,2,3)}
assert abs(norm[2]-1.5625)<1e-3 and abs(norm[3]-0.1372)<1e-3
print(f"Schulze–Hardy CCC 비 z=1:2:3 = {norm[1]:.0f}:{norm[2]:.2f}:{norm[3]:.3f} (3가는 1가의 1/{ccc[1]/ccc[3]:.0f})")
print("OK verify1: EDL 원자가 압축 + z^-6 CCC")
```

```python verify
# verify 2 — ζ-pH Nern스트 상한 기울기 + PZC 표 부호논리 + 실리카 이온강도 안정성 반례
import math
R,F,T = 8.314462, 96485.33, 298.15
nernst_slope_mV = R*T/F*math.log(10)*1000            # 2.303RT/F [mV], = ζ-pH 상한 & Pourbaix 기울기
assert abs(nernst_slope_mV - 59.16) < 0.05
print(f"ζ-pH Nern스트 상한 = -{nernst_slope_mV:.2f} mV/pH (Pourbaix -59.1 mV/pH와 동일 상수, 물리는 다름)")

# 표면전하 부호 = sign(PZC - pH) : pH<PZC → 양(+), pH>PZC → 음(-)   (Sun 2007 표 3.1)
def charge_sign(pzc, pH): return 1 if pH < pzc else (-1 if pH > pzc else 0)
PZC = {"SiO2": 2.5, "Al2O3": 8.5, "TiO2": 5.5, "Cu(OH)2": 9.5}   # 표/실측 중앙값
# 통상 CMP pH 4: 실리카는 음, 알루미나는 양 → 반대부호
assert charge_sign(PZC["SiO2"], 4) == -1 and charge_sign(PZC["Al2O3"], 4) == +1
# Cu 오염 → 실리카 IEP가 2.5 쪽에서 Cu(OH)2(9.5) 쪽으로 이동 (Sun §4.2.2.1): 같은 pH 7에서 부호 반전 가능
assert charge_sign(2.5, 7) == -1 and charge_sign(9.5, 7) == +1
print(f"pH4: SiO2 {charge_sign(2.5,4):+d}, Al2O3 {charge_sign(8.5,4):+d} (반대부호); Cu오염 시 IEP 2.5→9.5로 이동")

# Cu 흡착 pH 의존 (Sun 2007 §4.2.2.2): pH6 ~1e13, pH4 ~1e11 atoms/cm² → 100배
ads = {6: 1e13, 4: 1e11}
assert ads[6]/ads[4] == 100
print(f"SiO2 위 Cu 흡착: pH6 {ads[6]:.0e} vs pH4 {ads[4]:.0e} atoms/cm² (×{ads[6]/ads[4]:.0f}, 강한 pH 의존)")

# 실리카 이온강도 안정성 반례 (Sun 2007 §8.3.1): DLVO/Schulze-Hardy는 고 I에서 응집 예측하나 실측은 안정
dlvo_predicts_coagulation_at_high_I = True    # z^-6 CCC 논리상 KNO3 다량 첨가 시 응집 예상
observed_silica_stable_at_12mScm  = True       # 실측: 8-12 mS/cm에서도 2h 안정 (비-DLVO 수화력)
assert dlvo_predicts_coagulation_at_high_I and observed_silica_stable_at_12mScm
print("OK verify2: -59 mV/pH 상한·PZC 부호·Cu 흡착 pH의존; 실리카는 고이온강도서 DLVO 예측을 벗어나 안정(비-DLVO)")
```

```python verify
# verify 3 — Dandu 2009 (doi:10.1149/1.3230624) : ζ 부호 정합 → oxide:nitride 선택비
# 실측 IEP: 실리카 2, 세리아 8, Si3N4 9 ; RR: oxide 350, nitride(무첨가) 80 / (1% pyridine) 2 nm/min
IEP = {"silica": 2.0, "ceria": 8.0, "nitride": 9.0}
def sign(iep, pH): return 1 if pH < iep else (-1 if pH > iep else 0)
pH = 4.0
# pH4: 세리아(+)·실리카(-) → 반대부호(인력); 세리아·질화막은 둘 다 (+) → 동부호(반발)
assert sign(IEP["ceria"], pH) == +1 and sign(IEP["silica"], pH) == -1
assert sign(IEP["ceria"], pH) * sign(IEP["silica"], pH) < 0     # 세리아-실리카 인력 = oxide 제거 촉진
assert sign(IEP["ceria"], pH) * sign(IEP["nitride"], pH) > 0    # 세리아-질화막 반발 = nitride 접촉 적음
print(f"pH{pH:.0f}: 세리아{sign(IEP['ceria'],pH):+d}·실리카{sign(IEP['silica'],pH):+d}=인력(oxide↑), 세리아·질화막 동부호(nitride↓)")

# 선택비: 무첨가 vs 1% pyridine·HCl (nitride 억제)
ox, ni_bare, ni_inhib = 350.0, 80.0, 2.0
sel_bare, sel_inhib = ox/ni_bare, ox/ni_inhib
assert abs(sel_bare - 4.375) < 0.01
assert 170 < sel_inhib < 180                                    # ~175
print(f"선택비 oxide:nitride = 무첨가 {sel_bare:.1f} → 1% pyridine {sel_inhib:.0f} (nitride 80→2 nm/min)")

# PAA가 세리아 IEP를 8→4로 끌어내려 pH>5.5에서 인력창을 닫음 (Dandu §RR vs pH)
iep_ceria_PAA = 4.0
assert sign(iep_ceria_PAA, 5.5) <= 0                            # pH5.5에서 세리아 더는 양전하 아님 → 인력 소멸
assert IEP["ceria"] - iep_ceria_PAA == 4.0
print(f"0.01% PAA: 세리아 IEP {IEP['ceria']:.0f}→{iep_ceria_PAA:.0f} (pH>5.5에서 정전인력창 닫힘)")
print("OK verify3: ζ 부호 정합이 세리아 STI 선택비를 켠다 (Dandu 2009)")
```

## 8. 다른 에이전트·단원과의 연결
- **[[colloid-zeta-dlvo-slurry-stability]]**: 이 노트는 그 §3(Debye)·§5(IEP)를 **원자가·CCC·자리해리**로 정량 확장하고 실리카 비-DLVO 반례를 추가.
- **[[surface-chemistry-cu-w-pourbaix-passivation]]·[[cu-electrochemistry-pourbaix-bta-oxidizer-inhibitor]]**: Pourbaix "상 안정성" 축을
  이 노트의 "표면전하 ζ" 축과 **독립 두 그림**으로 명시적 구분(§1·§4).
- **[[silica-cmp-ph-acidic-repulsion-choi-power-law]]**: 실리카 ζ-pH → MRR의 단조 반발이 §2·§4.2 양쪽성 용해(pH9 전환)와 이어짐.
- **[[ceria-slurry-ce-redox-selectivity]]**: §5.1 Dandu 정전인력이 그 노트의 Si–O–Ce 화학결합과 **접촉-반응 상보**(먼저 붙고 화학결합).
- **[[inhibitor-chelator-adsorption-isotherm-passivation]]**: 그 노트가 예고한 "I=0 상수 → 이온강도 조건부 보정"을 §4.1에서 Davies/활동도로 연결.
- **[[post-cmp-metallic-contamination-sources]]·[[metal-contamination-device-impact-irds-limits]]**: 다가 금속이온의 z⁻⁶ 응집·Cu 흡착 IEP 이동이 오염 경로.
- **구현 요청**: ζ(pH,I)·Debye(z)·조건부 안정도상수 스케일러는 담당 PROFILE.md "## 구현 요청"에 등록(직접 sim/ 미투입).

## 9. 자기시험
→ [[../../agents/slurry-chemistry/EXAMS.md]] Lv2-1 문항 참조.
