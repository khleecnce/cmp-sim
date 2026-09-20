<!-- V2-SECTION: (분배 대상 아님, tool-post-clean 독자 학습) | 작성 2026-09-15 | tool-post-clean Lv3-1 -->
# 나노입자(<50 nm) 제거의 물리 한계 — 부착력 vs 제거력의 입경 스케일링·임계 입경, 저결함 세정 최신 동향

> 에이전트: tool-post-clean Lv3-1 | 작성일: 2026-09-15
> 선행(반드시 먼저 읽기): [[post-cmp-pva-brush-scrub-contact-shear-zeta]](Lv1-2 — 브러시 전단 제거력·제타전위·Burdick 임계 Re_pc·매립),
> [[post-cmp-cleaning-chemistry-ammonia-citric-surfactant-corrosion]](Lv2-1 — 암모니아/시트르산/계면활성제/부식방지제 네 축),
> [[post-cmp-megasonic-marangoni-drying-watermark]](Lv2-2 — 메가소닉 음향 경계층 δ_s·마랑고니 건조·Ng2007 제거력 최초 인용)
> 관련(침범 없이 상호링크): [[post-cmp-defect-classification-and-inspection]](§5 IRDS killer=½피치·관리임계 ¼피치),
> [[defect-density-yield-models-and-spatial-statistics]](killer ratio θ·수율식), [[colloid-zeta-dlvo-slurry-stability]](Hamaker·vdW 정의)
>
> **스코프(이 단원만)**: post-CMP 세정에서 **나노입자 제거가 왜 입경이 작아질수록 근본적으로 어려워지는가**를,
> (a) **부착력(vdW)의 입경 스케일링 ∝ R** vs **제거력(유체항력 ∝ R², 접촉/음향 ∝ R²~R³)의 입경 스케일링**과
> 그 교차(임계 입경)로 정량화하고, (b) 최근 10년 저결함 세정 1차 문헌(Cu/Co 갈바닉 억제·세리아 잔류·계면활성제
> /킬레이트 PRE)을 정리하며, (c) advanced node·3D NAND의 허용 결함 크기(관리임계 ¼피치)와 현 세정 기술의 갭을
> 짚는다. Lv1-2가 다룬 Burdick 롤링 모델·Lv2-2가 다룬 δ_s·Ng2007 도입부는 **재서술하지 않고 심화·정량 재현**한다.

## 1. 왜 "입경 스케일링"이 나노입자 제거 한계의 본질인가
Lv1-2는 브러시 전단이 입자를 굴려 떼는 롤링 모멘트 균형을, Lv2-2는 메가소닉 음향 경계층 δ_s가 서브µm로 얇아져
작은 입자에 전단이 닿는다는 것을 봤다. 그러나 두 단원 모두 "제거력이 부착력을 이기는가"를 **특정 입경 한 점**에서만
따졌다. 이 단원의 새로운 질문은 **입경을 연속 변수로 놓았을 때 부착력과 제거력이 서로 다른 멱수로 스케일링하며,
그 격차가 나노 영역에서 벌어져 임계 입경 아래로는 어떤 유체역학적 힘으로도 뗄 수 없게 된다**는 것이다. 핵심 물리
하나로 압축하면: **부착력(vdW)은 입자 반경 R의 1승, 유체역학 제거력은 R의 2승(항력)~3승(양력·관성)으로 줄어든다.**
따라서 R이 작아지면 제거력이 부착력보다 **빠르게** 사라지고, 둘의 비 F_removal/F_adh ∝ R이 1 아래로 떨어지는
입경이 존재한다. 이것이 "왜 sub-50 nm 입자는 화학 없이 못 떼는가"의 정량적 답이며(§2–4), (c) advanced node가
요구하는 관리임계(¼피치 ≈ 수 nm)와 현 기술의 갭을 설명한다(§6).

## 2. 부착력의 입경 스케일링 — vdW ∝ R (1차 유도 2편의 합치)
**F. Zhang, A. A. Busnaina, G. Ahmadi, "Particle Adhesion and Removal in Chemical Mechanical Polishing and
Post-CMP Cleaning," *J. Electrochem. Soc.* 146(7), 2665–2669 (1999). DOI: 10.1149/1.1391989** (전문 확보:
`papers/zhang2000-jes-particle-adhesion-removal-cmp-postclean.pdf`, 미러 사이트→미러 사이트; 파일명 2000은
초판 오타, 실제 1999). **50 µm 미만 입자에서는 van der Waals 힘이 지배**임을 명시(§"primary adhesion forces of
small particles, less than 50 µm in diam, van der Waals forces are predominant")하고, vdW 부착력을 (E2, 폐형식 유도)
$$ F_a = \frac{A R}{6 z_0^2}\Big(1 + \frac{a^2}{R z_0}\Big) \quad\text{(Zhang 1999 Eq.6)} $$
로 쓴다($A$=Hamaker 상수, $z_0$=분리거리, $R$=입자 반경, $a$=소성변형 접촉반경). 접촉항 $a^2/(Rz_0)$이 작을 때
**주항은 $F_a \approx AR/(6z_0^2) \propto R$** — 부착력은 입자 반경에 **1차 선형**이다. 같은 논문은 소성접촉을
Maugis–Pollock $F=\pi a^2 H$(Eq.7)로 닫아 접촉반경 $a$를 힘균형 $\pi a^2 H = F_a+F_P$(Eq.9)로 푼다 — 즉 입자가
연마압으로 파묻히면 $a$가 커지고 접촉항이 부활해 부착력이 급증한다(Lv1-2 Burdick의 "매립→제거불가"와 같은 물리).

**Ng et al. 2007**([[post-cmp-megasonic-marangoni-drying-watermark]]에서 이미 서지 인용, DOI: 10.1149/1.2739817,
전문 `papers/ng2007-esl-nanoparticle-removal-postcmp.pdf`)은 이상적 구형 부착의 vdW를 (E2)
$$ F = \frac{A R}{6 d^2},\quad A=0.37\text{ eV (SiO}_2/\text{H}_2\text{O/Si}),\ d=z_0=0.4\text{ nm} $$
로 쓰고, 세정 전 실리카 부착력을 **3.087×10⁻⁹ ~ 1.544×10⁻⁸ N**으로 보고한다. §7(A)에서 이 두 경계값을 그대로
재현하면 각각 **R=50 nm(입경 100 nm)와 R=250 nm(입경 500 nm)**에 정확히 대응함을 보인다 — 즉 Ng의 보고 범위는
입경 100–500 nm 창의 vdW 부착력이며, $F_a \propto R$ 선형이 두 논문에서 일관된다. (알루미나 부착력은 oxide 표면에서
실리카의 **약 12배**, Zhang 1999 Fig.5 — Hamaker 차이. Lv1-2 Burdick의 SiO₂ 16 nN·Cu 165 nN 러프니스-보정 상한과
같은 계열의 관측.)

## 3. 제거력의 입경 스케일링 — 유체 ∝ R², 접촉/음향 ∝ R²~R³
Zhang 1999은 세정 중 입자에 작용하는 제거력을 세 갈래로 분해한다(E2, 폐형식 유도):
- **유체 항력(drag)**: 벽 근처 선형 전단류의 구형 입자 항력을 O'Neill류로 $F_D \propto \mu R^2$ (Eq.14, 전단 Reynolds
  $Re^*$ 포함) — **반경의 2승**. 절대값은 **0.001–0.01 nN**으로 보고("The drag force … is very small
  (0.01–0.001 nN) compared to the particle adhesion force").
- **양력(lift)**: $F_L \propto (Re^*)^{3/2}$ (Eq.16), 경계층에서 항력보다 **더 작아 무시 가능**("the lift force is much
  smaller than the drag force and cannot affect particle removal"). 즉 **입자는 들려서가 아니라 굴러서(roll-off)** 떨어진다.
- **접촉(브러시/pad asperity) 제거력**: JKR 접촉부착 $F_A \propto W\,r$(Eq.17, $r$=접촉반경, $W$=부착일)과 그로 인한
  마찰 $F_F=fF_A$(Eq.18). 접촉반경 $r$이 입자 크기에 비례하므로 접촉 제거력도 대략 **면적 스케일 R²**. Zhang의
  롤링 제거 판정(Eq.22): $F_D + F_F \ge \tfrac{a}{1.4R}(F_a-F_A)$ — 접촉반경 $a \ll 1.4R$이라 입자는 슬라이딩보다
  **롤링으로 훨씬 쉽게** 떨어진다.

Ng 2007은 접촉 제거에 필요한 마찰력을 $F=\pi r^2(\sigma_s + \tan\phi_{pm})\ \propto R^2$(접촉면적 기반, Eq.10)로 쓰고
**"smaller particle size has lower friction force … a smaller abrasive particle requires less force to be mechanically
removed"**(Fig.4b)라 명시한다 — 제거에 **필요한** 힘도 작은 입자일수록 작지만, **공급 가능한** 제거력이 R²~R³로 더
빨리 사라지는 것이 문제의 핵심이다(§4). 문헌 개관(2차, E5)도 제거력이 "반경의 2승 또는 3승에 비례"한다고 정리한다.

## 4. 임계 입경 — 유체역학만으로는 나노입자를 뗄 수 없다 (핵심 결론)
$F_a \propto R$(§2)과 $F_D \propto R^2$(§3)를 나누면 **$F_D/F_a \propto R$** — 입자가 작을수록 유체 제거력 대 부착력의
비가 선형으로 작아진다. 둘이 같아지는 교차 반경
$$ R_{crit} = \frac{A}{6 z_0^2 \cdot (1.7009\cdot 6\pi\mu G)} $$
을 Zhang의 항력계수와 Ng의 Hamaker로 계산하면(§7(C)), 대표 벽전단률 $G\approx5000\text{ s}^{-1}$에서
**$R_{crit}\approx 385\ \mu m$**가 나온다 — 즉 **수백 µm보다 큰 입자만 유체항력으로 뗄 수 있고, 서브µm·나노 입자는
유체역학적으로 완전히 무력**이다. 이것이 Zhang의 결론("particles most likely roll off the surfaces by the drag force
**plus the contact forces** from the pad or brush asperities")의 정량적 실체다. 결과적으로:
1. **나노입자 제거는 반드시 접촉력(브러시 asperity)·음향 캐비테이션·화학적 부착력 저감에 의존**한다 — 순수 유체
   세척(rinse)은 나노 영역에서 원리적으로 불충분.
2. 그러나 접촉력은 입자를 **더 파묻는**(Ng Fig.4a, 페네트레이션↑) 양날 → Lv1-2 Burdick "매립→Unattainable"과 연결.
3. 메가소닉이 유일하게 비접촉으로 서브µm에 접근하는 이유는 δ_s(Lv2-2)를 얇혀 음향흐름 전단을 입자에 닿게 하기
   때문이나, 그 음향흐름 전단력 역시 유체 기반이라 절대 크기 한계가 있어 **화학(계면활성제·킬레이트로 F_a↓)과
   반드시 병행**해야 한다(Ng 2007의 "combined effort between a brush and surfactant" 결론과 합치).

## 5. 최근 10년 저결함 세정 — Cu/Co 갈바닉 억제·세리아 잔류·계면활성제 조합
Lv2-1이 세정액 4성분의 상호 견제를 다뤘다면, 이 절은 **advanced node(Co 라이너·세리아 슬러리) 특유의 최신 저결함
세정 1차 결과**를 본다.

**Cu/Co 계면 갈바닉 부식 억제 세정(1차 전문, E1)** — J. Seo, S. S. R. K. H. Vegi, S. V. Babu, *ECS J. Solid State
Sci. Technol.* 8(8), P379–P387 (2019), DOI: 10.1149/2.0011908jss (OA CC-BY, 전문
`papers/seo2019-jss-cuco-galvanic-postclean.pdf`). Co를 Cu 라이너로 쓰면 post-Cu-CMP 세정에서 (i) BTA/Cu-BTA/
Co-BTA 유기잔류와 실리카를 동시에 떼야 하고 (ii) Cu-Co 갈바닉쌍의 부식을 막아야 한다. 저자들의 해법:
- **50 mM 에틸렌디아민(En) pH 11 + 초음파**로 Cu·Co 위 잔류물을 거의 완전 제거 — Cu-En/Co-En 착물의 안정도
  상수가 Cu-BTA/Co-BTA보다 훨씬 커서 **리간드 교환으로 BTA 착물을 해리**시킨다(§2-1 시트르산 킬레이션과 같은
  원리의 더 강한 버전). 단 En 단독은 Cu/Co 갈바닉 구동력(Ecorr 차)을 **~40 mV**로만 낮춰 Icorr가 여전히 높다.
- **0.75 mM 시스테인(Cys) + 9.25 mM 요산(UA) + 50 mM En pH 11** 혼합이 유기잔류·실리카 제거와 동시에 Cu-Co
  **Ecorr 차를 ~5 mV**, 갈바닉 부식전류 **Igc ~0.7 µA/cm²**로 억제 — Cys는 음극(Cu)·UA는 양극(Co) 반응을 각각
  제어. §7(E)에서 이 값들을 재현한다.

**세리아 잔류·계면활성제/킬레이트 조합(초록·스니펫만, E5)**: 최신 세리아·Co 세정은 다성분 처방으로 고 PRE를
보고한다 — (i) sub-10 nm 미세 세리아 입자를 **gas-dissolved water(용존기체수)**로 떼는 시도(Choi, Lee, Liu et al.,
"Gas-dissolved water assisted post-CMP cleaning for removal of sub-10 nm fine ceria particles," *Appl. Surf. Sci.* 2026,
DOI: 10.1016/j.apsusc.2026.167590 — **제목만 확인, 초록·본문 미확보 E5**; sub-10 nm 세리아 제거가 **여전히 미해결
과제**임을 방증), (ii) Co 패턴 세정에서 시트르산이 Si–O–Co 결합을 끊고 양이온+비이온 계면활성제 조합으로 PRE
~94–99% 보고(Zhang et al., Co forward design, ACS AEM 2023, DOI: 10.1021/acsaelm.3c01315; 계면활성제 조합 citric
acid계 PRE 99.5% 보고 등 — **웹 검색 스니펫만, 원문 미확보 E5**), (iii) 비이온 계면활성제의 STI 세리아 제거 효과
(Zhao et al., *Mater. Sci. Semicond. Process.* 2024, DOI: 10.1016/j.mssp.2024.108279 — **제목만 확인 E5**). EDTA
pH 11이 SiO₂ 위 세리아를 Ce–O–Si 결합 파괴·Ce(III)-EDTA 착화로 뗀다는 기구도 반복 보고된다(웹 스니펫, E5).
→ 공통 구조: **킬레이트(금속-산소 결합 파괴) + 계면활성제(젖음·정전반발·재부착 방지) + 부식억제(갈바닉 제어)**의
삼중 처방이 저결함 세정의 최신 표준이며, Lv2-1 §6 트레이드오프 표의 advanced-node 확장이다.

## 6. Advanced node·3D NAND 요구와 현 기술 갭
[[post-cmp-defect-classification-and-inspection]] §5(E1, IRDS 2024 YE 주석[1] 원문 인용)와
[[defect-density-yield-models-and-spatial-statistics]] §3이 이미 정리한 killer 규칙을 이 단원의 제거 물리로 받는다:
- **killer 판정**: 입자·잔사는 크기가 **배선 피치의 ½ 초과 시 killer**, 전도성 입자는 그보다 작아도 브리지(killer).
  **관리임계 = ¼피치**. M1 피치 38–45 nm 세대에서 ½피치 ≈ 19–22.5 nm, 관리임계(¼피치) ≈ **3.5–10 nm**(선행 §5).
- **갭**: advanced node는 **관리임계 ~수 nm(¼피치)** 입자 제거를 요구하지만, §4의 스케일링($F_D/F_a \propto R$)상
  10 nm 입자(R=5 nm)는 250 nm 입자(R=125 nm) 대비 유체 제거력 대 부착력 비가 **약 25배 불리**(§7(F)). sub-10 nm
  세리아 제거가 2026년에도 신규 논문 주제(§5, E5)라는 사실이 이 물리적 갭을 방증한다.
- **3D NAND 함의**: 3D NAND는 수직적층·고종횡비로 CMP 패스 수가 많아 세정 누적 결함예산이 빡빡하나, 본 노트가
  확보한 1차 문헌에는 3D NAND **웨이퍼당 허용 결함 수**의 정량표가 없다 — IRDS YE의 killer 규칙(크기 기준)만
  E1로 인용하고, "패스당 결함 수/wafer"의 노드별 절대 스펙은 **미확보(E5, 정량 미주장)**로 남긴다.

## 7. python 재현 — 부착력·항력 스케일링, 임계 입경, 갈바닉, node 갭
```python verify
import math

# ===== (A) Ng 2007 vdW 부착력 F=AR/6z² 재현: 보고 범위 경계값 → 대응 입경 =====
A_NG = 0.37 * 1.602176634e-19   # 0.37 eV → J (SiO2/H2O/Si, Ng 2007)
z0 = 0.4e-9                      # 분리거리 (Ng 2007)
def F_vdw(R):
    return A_NG * R / (6 * z0**2)
Fa_50 = F_vdw(50e-9); Fa_250 = F_vdw(250e-9)
print(f"(A) R=50nm F_a={Fa_50:.3e} N, R=250nm F_a={Fa_250:.3e} N (Ng 보고: 3.087e-9~1.544e-8)")
assert abs(Fa_50 - 3.087e-9)/3.087e-9 < 0.01, "R=50nm 부착력이 Ng 하한 3.087e-9 N과 불일치"
assert abs(Fa_250 - 1.544e-8)/1.544e-8 < 0.01, "R=250nm 부착력이 Ng 상한 1.544e-8 N과 불일치"
# 부착력 ∝ R 선형: 반경 5배면 힘도 정확히 5배
assert abs(Fa_250/Fa_50 - 5.0) < 1e-9, "F_a는 R에 선형이어야(250/50=5배)"

# ===== (B) Zhang 1999 유체항력 F_D=1.7009·6πμG·R² : ∝R², 절대값 0.001~0.01 nN 오더 =====
mu = 1e-3            # 물 점도 Pa·s
G = 5000.0          # 벽 전단률 s⁻¹ (Zhang 미명시 → 0.001~0.01nN 재현하는 대표값으로 역산, 미검증 가정)
def F_drag(R):
    return 1.7009 * 6 * math.pi * mu * G * R**2   # O'Neill 벽근접 선형전단 항력
FD_50 = F_drag(50e-9); FD_250 = F_drag(250e-9)
print(f"(B) R=50nm F_D={FD_50:.3e} N, R=250nm F_D={FD_250:.3e} N (Zhang 보고: 0.001~0.01 nN)")
assert 1e-13 < FD_250 <= 1.1e-11, "R=250nm 항력이 Zhang 보고 상한(0.01 nN=1e-11 N) 오더를 벗어남"
# 항력 ∝ R²: 반경 5배면 힘은 25배
assert abs(FD_250/FD_50 - 25.0) < 1e-6, "F_D는 R²이어야(250/50의 제곱=25배)"
# 유체항력은 같은 입경의 부착력보다 2~4자릿수 작다 (Zhang: '유체 힘은 너무 작다')
assert FD_250 / Fa_250 < 1e-2, "유체항력이 부착력의 1% 미만이어야(유체 무력 결론)"

# ===== (C) 임계 입경 교차 F_D=F_a → R_crit : 나노 영역은 유체로 제거 불가 =====
R_crit = A_NG / (6 * z0**2 * 1.7009 * 6 * math.pi * mu * G)
print(f"(C) R_crit = {R_crit*1e6:.0f} µm (이보다 작은 입자는 유체항력<부착력 → 유체로 제거 불가)")
assert R_crit > 100e-6, "임계 반경이 100µm보다 커야 '서브µm·나노는 유체 무력' 결론 성립"
# 검산: R_crit에서 실제로 F_D≈F_a
assert abs(F_drag(R_crit)/F_vdw(R_crit) - 1.0) < 1e-6, "R_crit 정의(F_D=F_a) 자체 정합"

# ===== (D) 스케일링 격차: F_D/F_a ∝ R (작은 입자일수록 유체 제거 불리) =====
ratio_50  = F_drag(50e-9)  / F_vdw(50e-9)
ratio_250 = F_drag(250e-9) / F_vdw(250e-9)
print(f"(D) F_D/F_a: R=50nm {ratio_50:.2e}, R=250nm {ratio_250:.2e} — 5배 큰 입자가 5배 유리")
assert abs((ratio_250/ratio_50) - 5.0) < 1e-6, "F_D/F_a는 R에 선형이어야(∝R²/R=R)"
assert ratio_50 < ratio_250 < 1.0, "두 입경 모두 비<1(둘 다 유체로 못 뗌)이고 작을수록 더 불리"

# ===== (E) Seo 2019 Cu/Co 갈바닉 억제 수치 (전문 실측 E1) =====
Ecorr_En_only_mV = 40.0     # En 단독: Ecorr 차 ~40 mV (여전히 높음)
Ecorr_full_mV    = 5.0      # Cys+UA+En: Ecorr 차 ~5 mV
Igc_full_uAcm2   = 0.7      # 갈바닉 부식전류 ~0.7 µA/cm²
print(f"(E) Seo 2019: En단독 ΔEcorr {Ecorr_En_only_mV}mV → Cys+UA+En {Ecorr_full_mV}mV, Igc {Igc_full_uAcm2}µA/cm²")
assert Ecorr_full_mV < Ecorr_En_only_mV, "Cys+UA 첨가가 갈바닉 구동력(ΔEcorr)을 낮춰야 함"
assert Ecorr_En_only_mV / Ecorr_full_mV >= 8.0, "완성 처방이 En단독 대비 ΔEcorr을 8배 이상 낮춤(40→5)"
assert Igc_full_uAcm2 < 1.0, "완성 처방 갈바닉 전류가 1 µA/cm² 미만(허용 수준)"

# ===== (F) advanced node 갭: 관리임계 ¼피치(≈수 nm) 입자의 유체 제거 불리도 =====
# 선행 노트 §5(E1): M1 ½피치 19~22.5nm, 관리임계 ¼피치 ≈ 3.5~10nm
half_pitch_nm = 20.0
manage_thresh_nm = half_pitch_nm / 2   # ¼피치 = 관리임계 입자 지름(≈10 nm)
R_node = manage_thresh_nm/2 * 1e-9     # 반경 (지름 10nm → R=5nm)
R_ref  = 125e-9                        # 참조: 지름 250nm 입자
gap = (F_drag(R_ref)/F_vdw(R_ref)) / (F_drag(R_node)/F_vdw(R_node))
print(f"(F) ¼피치 관리임계 지름 {manage_thresh_nm:.0f}nm(R={R_node*1e9:.0f}nm) vs 250nm 입자: 유체 제거효율비 {gap:.0f}배 불리")
assert abs(gap - R_ref/R_node) < 1e-6, "격차는 반경비(F_D/F_a∝R)와 일치해야"
assert gap > 20, "node 관리임계 입자가 250nm 입자보다 20배 이상 유체 제거 불리(=화학·접촉력 필수)"

print("PASS: (A) Ng vdW 경계값=입경100/500nm 정확재현, (B) 항력∝R²·유체무력, "
      "(C) R_crit≈385µm, (D) F_D/F_a∝R, (E) Seo 갈바닉 40→5mV·Igc0.7, (F) node갭 25배 — 6건 확인")
```
재현 요약(한 줄): Ng 2007의 vdW 부착력 경계값(3.087e-9·1.544e-8 N)을 F=AR/6z²로 재현하니 각각 입경 100·500 nm에
정확히 대응($F_a\propto R$)했고, Zhang 1999의 유체항력 $F_D\propto R^2$(대표 G=5000/s에서 0.0004~0.01 nN)이 같은
입경 부착력의 1% 미만이라 임계 반경 $R_{crit}\approx385\,\mu m$—서브µm·나노는 유체역학적으로 제거 불가—를 얻었으며
(Zhang et al. 1999, DOI: 10.1149/1.1391989; Ng et al. 2007, DOI: 10.1149/1.2739817), $F_D/F_a\propto R$로 ¼피치
관리임계(지름 10 nm) 입자는 250 nm 입자 대비 유체 제거가 25배 불리함을, Seo 2019(DOI: 10.1149/2.0011908jss)의
Cu/Co 갈바닉 억제(ΔEcorr 40→5 mV, Igc 0.7 µA/cm²)와 함께 확인했다.

## 8. 모델 후보 표 — Lv3-2(세정 조건→잔류 결함 확률) 설계 입력
입경·재료·세정조건 → 부착력/제거력 스케일링 → PRE/문헌값. **근거등급 병기**. Lv3-2가 이 표를 잔류확률
$P_{res}=f(F_a/F_{removal})$의 드라이버로 받는다.

| 입경(지름) | 재료계 | 지배 부착력 | 유체 제거력 | 세정 수단 | PRE/문헌값 | 근거등급·출처 |
|---|---|---|---|---|---|---|
| 100–500 nm | SiO₂/oxide | vdW F_a=AR/6z₀²=3.09e-9~1.54e-8 N (∝R) | F_D∝R² ~0.001–0.01 nN (무력) | 브러시 접촉력+희석 NH₃ | DI만으론 실리카 제거, 알루미나는 NH₃ 필요(부착력 12배) | E2 Zhang1999/Ng2007 |
| <50 nm | SiO₂/세리아 | vdW ∝R (+매립 시 접촉항 급증) | F_D/F_a∝R → 나노에서 비≪1 | 메가소닉(δ_s 서브µm)+계면활성제 | 순수 유체 불가, 화학+음향 병행 필수(정성) | E2 스케일링 + E5 최신 |
| sub-10 nm | 세리아/oxide | vdW + Ce–O–Si 화학결합 | 사실상 0(유체 무력) | 용존기체수·킬레이트(EDTA/시트르산) | 2026년 신규 연구주제(정량 PRE 미확보) | E5 Choi2026 apsusc |
| ~수십–수백 nm | 실리카+BTA잔류 / Cu·Co | vdW + Cu/Co-BTA 착물 흡착 | F_D 무력 | 킬레이트(En 리간드교환)+Cys/UA+초음파 | 거의 완전제거; ΔEcorr 40→5mV, Igc 0.7µA/cm² | E1 Seo2019 |
| ~수십–수백 nm | 세리아/Co 패턴 | vdW + Si–O–Co 결합 | F_D 무력 | 시트르산(결합절단)+양이온/비이온 계면활성제 | PRE ~94–99.5% (조합 처방) | E5 웹스니펫/초록 |
| ¼피치 관리임계(≈3.5–10 nm) | node 요구 | — | 250nm 대비 25배 불리(§7F) | (현 기술 갭) | killer=½피치, 관리=¼피치 | E1 IRDS(선행 §5) |

## 9. 한계 (정직 표기)
- **벽 전단률 G는 Zhang 1999가 명시하지 않았다** — §7(B)(C)의 G=5000 s⁻¹은 Zhang 보고 항력(0.001–0.01 nN)을
  재현하도록 우리가 역산한 대표값(**미검증 가정**). $R_{crit}$는 $\propto 1/G$라 절대값(385 µm)은 G에 민감하다.
  주장하는 것은 "$R_{crit}$이 수백 µm 오더 → 서브µm·나노는 유체 무력"이라는 **방향·오더**이지 정확한 385 µm가 아니다.
- **Ng의 Hamaker A=0.37 eV(=5.93e-20 J)는 SiO₂/H₂O/Si**(Si 기판 포함)로, SiO₂/H₂O/SiO₂ 표준 Hamaker
  (≈0.46–1.6×10⁻²⁰ J)보다 크다 — §7은 Ng의 논문값을 그대로 써 그의 보고 부착력을 재현한 것이며, 다른 재료계로
  전이하려면 A를 바꿔야 한다(전이 시 절대값 **미검증**).
- **제거력 "∝R²~R³"의 3승(양력·관성·음향 캐비테이션)은 본 노트가 1차로 확보한 Zhang/Ng에서 R²(항력·접촉면적)
  까지만 폐형식으로 확인**했다. 3승 항의 1차 유도는 확보 문헌 범위 밖(웹 개관 E5) — §7은 R² 스케일링만 assert한다.
- **§5의 세리아·Co 계면활성제 PRE(94–99.5%)·sub-10 nm 세리아·EDTA 기구는 초록/제목/웹 스니펫만(E5)**. 원문
  (ScienceDirect·ACS·IOP 봇차단, 미러 사이트 미등재)을 확보 못 해 정량값은 인용 스니펫 수준이다. Seo 2019(Cu/Co)만
  전문 확보(E1)라 정량 assert에 넣었다.
- **§6의 "3D NAND 웨이퍼당 허용 결함 수" 노드별 절대 스펙은 미확보** — killer **크기** 규칙(¼피치)만 IRDS(E1,
  선행 노트 경유)로 인용하고, 결함 **개수** 예산은 정량 주장하지 않는다.
- Burdick 롤링 모델(Lv1-2)·δ_s(Lv2-2)와 본 노트 스케일링을 하나의 통합 제거확률식으로 엮는 것은 Lv3-2 과제이며,
  본 노트는 그 입력(§8 표)까지만 제공한다.
- 회사·특정 장비/레시피(브러시 벤더 처방, 메가소닉 파워 프로파일)는 다루지 않았다(문헌 정의·실측만).

## 10. 자기시험
→ [[../../agents/tool-post-clean/EXAMS.md]] Lv3-1 문항 참조.
</content>
</invoke>
