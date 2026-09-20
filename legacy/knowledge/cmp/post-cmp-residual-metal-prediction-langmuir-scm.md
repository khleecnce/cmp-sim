<!-- V2-SECTION: R2-slurry | 공동: R5-wafer | 분배완료 2026-09-09 | 근거: chemistry, colloid, zeta, chelation | 정본: ARCHITECTURE-V2.md §3 -->
# 슬러리 조성·세정 조건 → 잔류 금속 농도 예측 모델 골격 — 경쟁 Langmuir·표면착화(SCM)·킬레이트 분기 + 문헌값 대조

> 에이전트: surface-contamination Lv3-2 | 작성일: 2026-09-09
> 선행: [[post-cmp-adsorption-cleaning-chemistry]] [[low-level-metal-cobalt-ruthenium-cross-contamination]]
> [[post-cmp-metallic-contamination-sources]] [[metal-contamination-device-impact-irds-limits]]
> [[wafer-surface-metal-detection-txrf-vpdicpms-sims-xps]] [[colloid-zeta-dlvo-slurry-stability]]
> [[surface-chemistry-cu-w-pourbaix-passivation]]

## 1. 왜 필요한가 — Lv1~Lv3-1의 조각을 "입력→atoms/cm²" 한 줄 수식으로 잇는다
지금까지 노트는 (i) 발생원별 오염 오더(Lv1-1), (ii) 허용치 1~2×10¹⁰ atoms/cm²(Lv2-1, IRDS 2024 YE6), (iii) 킬레이트
조건부 상수 K′(pH)와 유리 이온 분율·산화물 표면전하 부호(Lv2-2 → `sim/tier2_physics/chelation_surface_charge.py`),
(iv) 수산화물 전이 pH*·갈바닉 방향(Lv3-1)을 따로 들고 있다. 이 단원은 그것을 **하나의 예측 체인**으로 묶는다:

```
[슬러리/세정액 총 금속농도 C_tot, pH, 킬레이트 C_L, 산화제, 막질, 접촉시간 t]
  → (A) 용액 종분화: 유리 이온 [M]_free = f_free(K′(pH), C_L)·C_tot,  pH ≥ pH*(수산화물)이면 "입자 분기"
  → (B) 표면 평형: 경쟁 Langmuir  σ_i = σ0·K_i[M_i]_free / (1 + K_H[H⁺] + Σ_j K_j[M_j]_free)      (Loewenstein 1999 Eq.22)
        또는 2-자리 SCM(≡SiOCu⁺ / (≡SiO)₂Cu, Sun 2007 Table 4.1) + Boltzmann 정전 보정
  → (C) 시간 인자: σ(t) = σ_eq·τ,  τ = 1 − exp(−√(4Dt/π)/L)                                     (Loewenstein 1998·1999 Eq.8·10)
  → (D) 세정 단계: 잔류 = σ_ads × (1 − η_clean),  η는 DIW 린스(불충분)/킬레이트 린스/DHF 표층 제거별 문헌값
  → 출력: 잔류 atoms/cm² ↔ IRDS 2024 YE6 2×10¹⁰ 비교
```
문헌 근거는 여섯 건이다. 1차 논문 4건(Loewenstein & Mertens 1998, Loewenstein·Charpin·Mertens 1999, Seo et al. 2001,
Martin et al. 1999)은 원문 PDF를 확보했고, 학위논문 1건(Sun 2007, Univ. of Arizona)은 DSpace 원문, 1건(Tsutano et al. 2025)은
초록만 확보해 **2차 인용**으로 표기한다.

## 2. (B) 표면 평형 ① — 경쟁 Langmuir 모델 (Loewenstein·Charpin·Mertens 1999, 1차)
- 출처: L. M. Loewenstein, F. Charpin, P. W. Mertens, "Competitive Adsorption of Metal Ions onto Hydrophilic Silicon Surfaces
  from Aqueous Solution", *J. Electrochem. Soc.* 146(2) 719–727 (1999), doi:10.1149/1.1391670 (원문 PDF
  `papers/loewenstein1999-jes-competitive-adsorption-metal-ions-si.pdf`).
- 실험: IMEC clean(H₂SO₄/O₃ → dHF → dHCl/O₃, 친수성 화학산화막) 150 mm Si(100)에 10종 금속(Ba·Ca·Co·Cr·Cu·Fe·K·Ni·Sr·Zn)
  질산 용액 14.4 mL 퍼들, pH 3–5.5, pM 5–8 (pM = −log[M⁺], 즉 10 µM~10 nM), 스핀 건조, VPD-DC TXRF(Atomika XSA 8010).
- 핵심식: 실라놀 자리 σ0가 유한하고 H⁺를 포함한 모든 양이온이 경쟁한다는 Langmuir 가정에서
  `σ_i = σ0·K_i[M_i]/(1 + K_H[H⁺] + Σ_j K_j[M_j])` (Eq.22). 산성 극한(K_H[H⁺] ≫ ΣK_j[M_j])에서는
  `σ_i ≈ σ0·K_i[M_i]/(K_H[H⁺])` (Eq.24)로 1998 논문의 이온교환식 σ ∝ [M]/[H⁺]와 일치한다.
- 파라미터(1차 문헌값): Cr³⁺ 단독 실험(pH 3, 20 °C, 2 min) 1/σ vs 1/[Cr³⁺] 직선 적합 절편 3.00×10⁻¹³ cm²/atom →
  **σ0 = 3×10¹² sites/cm²**, SiO₂ 표면 단위(≈8×10¹⁴/cm²)의 **0.4 %**만이 흡착자리. K_H ≈ 10³ L/mol("probably"), 이때
  **K_Cr ≈ 10⁶ L/mol** (논문 표현 그대로 오더값, 미검증 수준의 추정치임을 저자가 명시).
- 경험 지수(Table VI, log σ = Const + m′·pH + n′·pM): [M⁺]ⁿ′ 지수 n′ = 0.27(K)~0.73(Cr·Sr), 평균 0.54±0.11;
  [H⁺]ᵐ′ 지수 m′ = −0.07(K)~−0.56(Sr), 평균 −0.30±0.15. Cu는 m′ −0.26±0.08, n′ 0.38±0.07, Fe는 −0.16/0.69.
  분수 지수는 Langmuir 포화 구간(K[M]~1)의 자연스러운 결과(Eq.16·17: 저농도 지수 1, 고농도 0)다.
- 측정값 예(Table I, 10¹⁰ atoms/cm²): pH 3·pM 5·τ 0.953에서 Cu 58.5, Fe 460.8, Ca 90.5, K 83.7; pH 3·pM 8에서는 Cu 0.9~1.7,
  Fe 0.3~17.6, Ca 0.9; pH 5.5·pM 7·τ 0.092에서 Cu 61.3, Fe 10.1, Ca 108.4. 즉 **pH 3, 10 nM급 금속이면 Cu·Ca가
  ~10¹⁰ atoms/cm² 오더**로 IRDS 2×10¹⁰ 경계에 들어오고, pH 5.5 또는 µM급이면 10¹¹~10¹²으로 넘친다.
- Co는 의도적으로 넣지 않았는데 검출됐다(표준용액 오염) — 저자 스스로 "오염원 통제 안 됨"을 명시. Co 값은 참고만.

## 3. (B) 표면 평형 ② — pH·전하/반경 비례 (Loewenstein & Mertens 1998, 1차)
- 출처: L. M. Loewenstein, P. W. Mertens, "Adsorption of Metal Ions onto Hydrophilic Silicon Surfaces from Aqueous Solution:
  Effect of pH", *J. Electrochem. Soc.* 145(8) 2841–2847 (1998), doi:10.1149/1.1838723 (원문 PDF
  `papers/loewenstein1998-jes-metal-ion-adsorption-hydrophilic-si-ph.pdf`).
- 조건: 금속 5×10⁻⁸ mol/L(=50 nM, Cu 3.2 ppb), pH 3–5.6, t 1–1000 s, 20 °C. TXRF 수집효율 보정 Cu 20 %, 나머지 80 %.
- 결과: 평형 표면농도는 **pH 5.6→3에서 최대 78배 감소**(Discussion "pH Dependence"), [H⁺] 지수는 약 ½(a₁ 평균 0.51±0.08).
  시간의존은 Cr·Fe만(pH 4 이상에서 "켜짐"), 나머지는 1 s 안에 평형 — 확산 길이 L=√(4Dt/π)(D≈1600 µm²/s)가 1 s에 30 µm,
  1000 s에 1000 µm이므로 고갈층 두께 δ=σ/ρ가 L과 비슷한 pH 6·1 s 조건에서만 수송 제한이 나타난다(Table V).
- 물리: 수화 양이온으로 존재하는 금속은 pH 6 평형 표면농도가 **전하/반경 비 Q_r(Å⁻¹)에 비례**(Fig.5, Eq.13; pH 3에서는
  σ = 0.61·Q_r − 0.62, r² = 0.850). Al(Al₂O₃·3H₂O 침전), Fe³⁺(Fe(OH)₂⁺), Ni²⁺·Zn²⁺(수산화물), Cu(pH 5.6에서 Cu(OH)₂)는
  Pourbaix 상 이 비례에서 벗어난다 — Lv3-1의 pH* 분기와 같은 결론이다([[low-level-metal-cobalt-ruthenium-cross-contamination]] §3.3).
- 실무 결론(저자): 린스는 산성에서, 알칼리금속(K)은 pH 의존이 약해 **용액 농도 자체를 낮추는 수밖에 없다**. Marangoni 건조처럼
  액-표면 친화도를 낮추는 건조도 잔류를 낮춘다.

## 4. (B) 표면 평형 ③ — Cu/SiO₂ 2-자리 SCM과 슬러리 첨가제 효과 (Sun 2007 학위논문, 1차 데이터)
- 출처: Yuxia Sun, "Colloidal and Electrochemical Aspects of Copper-CMP", PhD dissertation, The University of Arizona, 2007
  (지도 S. Raghavan), hdl.handle.net/10150/194903 (DSpace 원문 `papers/sun2007-ua-thesis-colloidal-electrochemical-cu-cmp.pdf`).
- TEOS 웨이퍼 침지(I = 0.01 M, 3 min, DIW 1 min 린스, TXRF) 등온선(Fig.4.3 판독값, ±30 %): pH 6에서 5→80 ppm Cu에
  5×10¹⁰→7×10¹² atoms/cm², pH 4에서 2.5×10¹⁰→2×10¹¹. 콜로이드 실리카 등온선(Fig.4.12·본문): **pH 6 포화 ≈10¹³, pH 4 ≈10¹¹
  atoms/cm²**, 둘 다 Langmuir형. 흡착은 <0.5 min에 평형(Fig.4.4, 100 ppm, pH 6).
- pH edge(Fig.4.13, 1 ppm Cu, SiO₂ 2.728 g/L): pH ≤5에서 ≈5 %, pH 6.0에서 ≈50 %, pH ≥7.2에서 ≈100 % 흡착.
- SCM 파라미터(Table 4.1, FITEQL 적합): 자리밀도 **2 OH/nm²**, 비표면 416 m²/g, pKa1(≡SiOH ⇌ ≡SiO⁻+H⁺) **5.9**,
  pK1(≡SiOH + Cu²⁺ ⇌ ≡SiOCu⁺ + H⁺) **4.35**, pK2(2≡SiOH + Cu²⁺ ⇌ (≡SiO)₂Cu + 2H⁺) **8.22**. pH > 5.5에서는 이좌배위
  (≡SiO)₂Cu가 지배(Fig.4.16)라 DIW 린스로 잘 안 떨어진다(Fig.4.5: pH 6 흡착분은 10 min 오버플로 린스에도 부분 비가역).
- 첨가제 효과(모두 pH 6): 시트르산(CA) 100 ppm → 흡착 **약 2자릿수 감소**(Fig.4.6); H₂O₂ 5 % → 증가(Fig.4.8); BTA 1 mM → 증가
  (Fig.4.10); H₂O₂ 5 % + CA 100 ppm → **~10¹³ → ~10¹⁰ atoms/cm²**(Fig.4.9: 5~50 ppm Cu에서 ≤1×10¹⁰, 80~100 ppm에서 6×10¹⁰).
  이미 흡착된 Cu의 CA 린스: **4.32×10¹³ → 7.53×10¹⁰ atoms/cm²**(Fig.4.7, "~3 orders").
- ζ(pH) (Fig.4.11 판독, 0 ppm Cu 실리카): IEP ≈2.5, pH 4 ≈ −5 mV, pH 6 ≈ −17 mV, pH 7 ≈ −27 mV, pH 8 ≈ −35 mV.
  Cu 10→1000 ppm이면 Cu(OH)₂(IEP ≈9.5) 피복으로 실리카 ζ가 양(+)으로 뒤집힌다 — 입자 분기의 실증.
- Cu(OH)₂ 용해도: pH > 7.5에서 1 ppm 미만도 침전(Fig.4.1; logK CuOH⁺ 7.69, Cu(OH)₂⁰ 13.68, Cu(OH)₃⁻ 26.85 — 논문 표기값).
  Lv3-1 §6(B)의 minteq 계산(100 ppm에서 pH* 5.74)과 농도 스케일링(1 ppm → +1.0)으로 6.7이 되어 "7.5" 와 0.8 차이 —
  사용한 상수 세트가 달라(minteq vs 논문 표) **원인 미상, 미검증**으로 둔다.

## 5. (D) 세정 단계와 슬러리 조성 — Seo 2001·Martin 1999·Tsutano 2025
### 5.1 KOH 슬러리 산화막 CMP 후 K·Ca 잔류와 DHF 표층 제거 (Seo et al. 2001, 1차)
- 출처: Y.-J. Seo, W.-S. Lee, S.-Y. Kim, J.-S. Park, E.-G. Chang, "Optimization of post-CMP cleaning process for elimination of CMP
  slurry-induced metallic contaminations", *J. Mater. Sci.: Mater. Electron.* 12, 411–415 (2001), doi:10.1023/A:1011242900843
  (원문 PDF `papers/seo2001-jmsme-post-cmp-cleaning-slurry-metallic-contamination.pdf`; 이전 노트의 "2차 요약" 표기를 이제 1차로 승격).
- 조건: 200 mm p-Si, PE-TEOS·O₃-BPSG·PE-BPSG·PSG, IPEC 472 + Rodel IC-1000 + **Cabot SS-12(KOH계) 슬러리**, 세정은
  Avanti 9000에서 **DIW만**, Rigaku TXRF 3700-LE(검출한계 ~10¹⁰ atoms/cm²).
- 결과(§3.1·Fig.1·2): as-dep K 2~3×10¹⁰, Ca(BPSG) 4~6×10¹⁰; CMP+DIW 후 **PE-TEOS K ≈10¹², Ca ≈10¹¹; O₃-BPSG K ≈3×10¹³,
  Ca ≈2×10¹²** — as-dep 대비 약 2자릿수 증가. **dHF로 3 nm 제거**하면 K·Ca가 as-dep 수준(≈2×10¹⁰)으로 복귀 → 슬러리 유래 K·Ca는
  표면 3 nm 이내에 있다. BPSG의 P가 K·Ca를 게터링해 더 심하고, PSG는 P 함량과 함께 K·Ca 잔류가 증가(Fig.6).
- 모델 함의: **완충제 양이온(K⁺)은 pH 의존이 약해(§3, m′ −0.07) 흡착 억제가 아니라 표층 에칭(DHF 3 nm)이 유일한 확실한 η**.
  잔류 = σ_ads×(1−η)에서 DIW 린스 η≈0(K·Ca가 그대로), DHF-3 nm η ≈ 1 − 2×10¹⁰/10¹² = 0.98(TEOS).

### 5.2 SC-1 세정액 자체가 오염원일 때 — 킬레이트 1 ppm의 효과 (Martin et al. 1999, 1차)
- 출처: A. R. Martin, M. Baeyens, W. Hub, P. W. Mertens, B. O. Kolbesen, "Alkaline cleaning of silicon wafers: additives for the
  prevention of metal contamination", *Microelectron. Eng.* 45, 197–208 (1999), doi:10.1016/S0167-9317(99)00150-1 (원문 PDF
  `papers/martin1999-mee-alkaline-cleaning-additives-metal-contamination.pdf`).
- 조건: Gigabit급(금속 <0.1 w-ppb) SC-1 1/4/20(70 °C)·1/3/80(50 °C), 10 min 침지, 의도적 **1 w-ppb** Ca·Fe·Ni·Cu·Zn 스파이크,
  킬레이트 1 ppm(cTRAMP, Dequest 2060s, EDTA) 첨가, VPD-DSE-TXRF.
- Fig.5 판독값(1 ppb 스파이크, atoms/cm²): SC-1만 → Fe ≈1.2×10¹², Zn ≈3×10¹¹, Ca ≈5×10¹⁰, Ni ≈1×10¹⁰, Cu ≈2×10⁹;
  +1 ppm cTRAMP → Fe 검출한계(≈3×10¹⁰) 이하, Zn ≈8×10⁹, Cu ≈1×10⁹; +1 ppm EDTA → Fe ≈6×10¹¹(효과 미미, 10 ppm 필요);
  +Dequest → Fe ≈3×10¹¹이지만 **Cu는 ≈2×10¹⁰으로 오히려 증가**. SPV Fe 벌크 농도는 킬레이트로 10¹⁰~10¹¹ atoms/cm³.
- 모델 함의: 알칼리(pH 9.5~11)에서는 Fe³⁺가 이온이 아니라 수산화물 입자로 침전·부착하므로 §2의 이온 Langmuir가 아니라
  "입자 분기"이며, 킬레이트는 **침전 자체를 막는 f_free 인자**로 들어간다. ppb 용액 → 10¹² 표면은 §2의 pM 8(10 nM ≈ 0.6 ppb Fe)
  → 10¹⁰~10¹¹(pH 3)보다 1~2자릿수 크다 — pH 10의 침전 경로가 산성 이온흡착보다 훨씬 효율적이라는 뜻.

### 5.3 초순수 pg/L 금속의 흡착 비율 (Tsutano et al. 2025, 2차 인용 — 초록만)
- 출처: K. Tsutano, T. Mawaki, Y. Shirai, R. Kuroda, "Contamination Behavior of Bare Silicon Wafer Surface During Single-Wafer
  Process Using Deionized Water Containing Ultra-Trace Metal Impurities", *ECS J. Solid State Sci. Technol.* (2025),
  doi:10.1149/2162-8777/add809 — 유료·IOP 봇차단·미러 사이트 미보유로 **초록만 확인(2차 인용)**.
- 초록: pg/L급 Al·Ti·Mn·Co·Cu·Sr·Pb 함유 DIW 매엽 린스에서 **Cu 흡착비 2.6~3.3 %**로 최대, 농도·린스시간에 무관하고 **공급 유량에
  의존**(유량↑ → 경계층 얇아져 흡착확률↓). Al·Ti는 친수화 진행에 따라 거동이 급변. 원문 수치·정의(흡착비 분모)는 미검증.
- 모델 함의: 초저농도 극한(K[M] ≪ 1)에서는 §2 Eq.16 σ ∝ [M]이지만, 실제로는 수송(경계층)이 지배해 τ(t)가 아니라
  **유량 항**이 필요하다 — (C) 시간 인자의 한계(§7).

## 6. python 재현 — (A) 경쟁 Langmuir 지수·자리밀도 (B) SCM 비정전 근사의 한계와 ζ 보정 (C) 킬레이트·세정 단계 배수
```python verify
import math, sys
sys.path.insert(0, ".")
from sim.tier2_physics.chelation_surface_charge import chelation_conditional_logK, free_metal_fraction
from sim.tier2_physics.metal_contamination_surface import boltzmann_surface_enrichment

# ===== (A) Loewenstein 1999 경쟁 Langmuir: σ = σ0·K_M[M]/(1 + K_H[H+] + K_M[M]) =====
sigma0 = 3.0e12      # sites/cm², 1/절편 3.00e-13 cm²/atom (Fig.8, Cr3+ 단독, pH 3)
K_H, K_Cr = 1e3, 1e6 # L/mol, 논문 "probably ~1e3" / "about 1e6" (오더값)
def sigma(K_M, C_M, pH): H = 10**-pH; return sigma0 * K_M*C_M / (1 + K_H*H + K_M*C_M)
n_model = math.log10(sigma(K_Cr, 1e-5, 3) / sigma(K_Cr, 1e-8, 3)) / 3        # [M] 지수 (pM 8→5, pH 3)
m_model = -math.log10(sigma(K_Cr, 1e-8, 5.5) / sigma(K_Cr, 1e-8, 3)) / 2.5   # pH 지수 (pH 3→5.5, pM 8)
n_lit, m_lit = 0.73, -0.39                                                    # Table VI Cr n', m'
assert abs(n_model - n_lit) < 0.05, f"Cr [M] 지수 모델 {n_model:.2f} vs 문헌 0.73"
assert abs(m_model - m_lit) > 0.2   # pH 지수는 재현 안 됨 — 9종 타금속 경쟁항·K_H 오더값 때문(불일치 명시)
frac_sites = sigma0 / 8e14
assert 0.003 < frac_sites < 0.005    # 논문 "0.4 %"
# 자리밀도 오더 대조: Sun 2007 pH 6 포화 ≈1e13 (실리카 입자) — 같은 자릿수(<2 %)
assert 1e13 / sigma0 < 4 and 1e13 / 8e14 < 0.02
# pH 3, 10 nM Cu(pM 8) 상황을 K_Cu=K_Cr로 가정한 오더 계산 vs Table I Cu 0.9~1.7e10 (pH 3, pM 8)
s_cu = sigma(K_Cr, 1e-8, 3)
assert 1e9 < s_cu < 1e11, f"{s_cu:.2e}"   # 1.5e10 → 측정 0.9~1.7e10과 같은 자릿수 (K_Cu 미지, 오더 검증만)
# 시간 인자 τ = 1 − exp(−√(4Dt/π)/L): D=1560 µm²/s, L=815 µm — Table I의 τ 수준 0.092/0.522/0.953을 역산한 t (논문에 t 원값 없음)
D, L = 1560.0, 815.0
tau = lambda t: 1 - math.exp(-math.sqrt(4*D*t/math.pi)/L)
t_inv = {tv: (-math.log(1-tv)*L)**2 * math.pi / (4*D) for tv in (0.092, 0.522, 0.953)}
assert tau(1) < tau(60) < tau(1000) < 1 and abs(tau(t_inv[0.522]) - 0.522) < 1e-6
print(f"(A) Cr [M]지수 모델 {n_model:.2f} (문헌 0.73 일치) / pH지수 모델 {m_model:.2f} (문헌 −0.39 불일치); 자리분율 {frac_sites*100:.2f}% ; "
      f"pH3·10nM σ≈{s_cu:.1e}/cm²; τ 역산 t = " + ", ".join(f"{k}:{v:.0f}s" for k, v in t_inv.items()))

# ===== (B) Sun 2007 SCM(Table 4.1)을 정전 보정 없이 풀면 흡착 edge를 재현하지 못한다 → 필요한 Boltzmann 인자를 ζ와 대조 =====
ST = 2 * 416e18 * 2.728 / 6.022e23        # 자리 mol/L: 2 OH/nm² × 416 m²/g × 2.728 g/L
Ka1, K1, K2 = 10**-5.9, 10**-4.35, 10**-8.22
def frac_ads(pH, boltz=1.0):
    H = 10**-pH; SiOH = ST / (1 + Ka1/H)
    r1 = K1*SiOH/H * boltz; r2 = K2*SiOH**2/H**2 * boltz
    return (r1 + r2) / (1 + r1 + r2)
f6, f7 = frac_ads(6.0), frac_ads(7.0)
assert f6 < 0.15 and f7 < 0.2            # 비정전 근사: pH 6 ≈8 %, pH 7 ≈15 % — 실측(Fig.4.13) 50 %/100 %에 크게 미달(불일치 명시)
# 실측 50 %(pH 6)를 맞추려면 필요한 배수 → 등가 표면전위 |ψ| (Cu2+, z=2, 25 °C)
need6 = (0.5/0.5) / (f6/(1-f6))
psi6 = 25.69 * math.log(need6) / 2
zeta6 = -17.0                             # mV, Fig.4.11 판독(0 ppm Cu, pH 6)
assert boltzmann_surface_enrichment(-psi6, 2, 298.15) > 10   # sim 함수로 같은 인자 재현(>10배)
assert 20 < psi6 < 45 and abs(psi6) > abs(zeta6)   # 필요 |ψ| ≈31 mV > |ζ| 17 mV: 방향·오더 정합, ψ0>|ζ|이므로 모순 아님(정밀 재현은 미검증)
print(f"(B) 비정전 SCM 흡착분율 pH6 {f6*100:.1f}% / pH7 {f7*100:.1f}% (실측 50/100 %, 불일치); 필요 Boltzmann {need6:.1f}배 ↔ |ψ|≈{psi6:.0f} mV vs ζ {zeta6:.0f} mV")

# ===== (C) 킬레이트 분기·세정 배수 =====
logKp = chelation_conditional_logK("Cit", "Cu2+", 6.0)          # 노트 Lv2-2 sim: minteq logK 7.57, α_H(pH 6)
C_CA = 100e-3 / 192.12                                          # 100 ppm 시트르산 = 5.2e-4 M
f_free = free_metal_fraction(logKp, C_CA)
assert f_free < 1e-2                                            # 유리 Cu2+ ≥2자릿수 감소 → Sun Fig.4.6 "약 2자릿수" 흡착 감소와 방향·오더 정합
orders_pred = -math.log10(f_free)
assert 1.5 < orders_pred < 5                                    # 선형(K[M]≪1) 가정 예측 ≈3.7자릿수 vs 관측 ≈2 — Langmuir 포화 구간이라 과대(불일치 명시)
ca_rinse = 4.32e13 / 7.53e10                                    # Fig.4.7
assert 2.5 < math.log10(ca_rinse) < 3.0                         # "~3 orders"
teos_K, bpsg_K, asdep_K, dhf3nm_K = 1e12, 3e13, 2.5e10, 2e10    # Seo 2001 §3.1·Fig.2
irds_ye6 = 2e10
assert 40 <= teos_K/irds_ye6 <= 60 and bpsg_K/irds_ye6 >= 1000 and dhf3nm_K <= irds_ye6
eta_dhf = 1 - dhf3nm_K/teos_K
assert eta_dhf > 0.97
# pH 의존 오더: Loewenstein 1998 "pH 5.6→3 최대 78배" vs Sun 2007 pH 6→4 100배(≈10¹³→10¹¹) — pH 단위당 자릿수
per_pH_L, per_pH_S = math.log10(78)/2.6, math.log10(100)/2
assert 0.5 < per_pH_S/per_pH_L < 2
print(f"(C) CA 100 ppm pH6: logK'={logKp:.2f}, f_free={f_free:.1e} ({orders_pred:.1f}자릿수 예측 vs 관측≈2); CA 린스 {ca_rinse:.0f}배; "
      f"Seo2001 TEOS K/IRDS {teos_K/irds_ye6:.0f}배, BPSG {bpsg_K/irds_ye6:.0f}배, DHF3nm η={eta_dhf:.3f}; pH당 자릿수 L98 {per_pH_L:.2f} vs S07 {per_pH_S:.2f}")
```

**결과 해석(정직하게)**: (A) 경쟁 Langmuir에 논문 오더값(σ0 3×10¹², K_H 10³, K_Cr 10⁶)을 넣으면 Cr의 **[M] 지수 0.74가 문헌
Table VI 0.73과 0.01 이내로 재현**되지만, pH 지수는 −0.12로 문헌 −0.39와 3배 어긋난다 — 9종 타금속 경쟁항과 K_H가 오더값이기
때문이며 **불일치를 assert로 명시**했다. 자리밀도 0.4 %(3×10¹²)와 Sun의 pH 6 포화 10¹³는 같은 자릿수라 "표면 자리의 1 % 안팎"이
막질 무관 상수 후보다. (B) Sun의 SCM 상수를 정전 보정 없이 풀면 pH 6 흡착 8 %, pH 7 15 %로 실측 50/100 %를 크게 못 맞춘다.
50 %를 맞추는 데 필요한 Boltzmann 인자 ≈11배는 |ψ| ≈31 mV에 해당하고 Fig.4.11의 ζ(pH 6) −17 mV보다 크지만 ψ0 > |ζ|이므로
방향·오더는 정합한다 — 즉 **Lv1-1의 boltzmann_surface_enrichment가 SCM 체인의 필수 항**임을 수치로 확인했으나 정밀 재현은
미검증이다. (C) 시트르산 100 ppm(pH 6)의 유리 Cu²⁺ 분율 1.9×10⁻⁴는 관측 "2자릿수 감소"와 방향이 맞지만 선형 예측(3.7자릿수)은
과대 — Langmuir 포화 구간이라는 (A)의 결론과 일관된다. Seo 2001은 DIW-only 세정이 IRDS YE6 대비 TEOS 50배·BPSG 1500배로
넘치고 DHF 3 nm(η ≈0.98)만이 스펙 안으로 들여보낸다는 것을 보여준다.

## 7. 한계 (정직 표기)
- **K_i 표**가 없다. Loewenstein 1999는 Cr만 단독 실험이고 K_H·K_Cr도 오더값이다. Cu·Fe·K·Ca의 K_i는 미확보 — 모델 골격은
  "K_i를 회귀할 스키마"까지이며, 실제 슬러리 로트별 K_i는 Cal-1(고객 TXRF 데이터)에서 맞춰야 한다.
- 문헌은 모두 **친수성 화학산화막·TEOS·콜로이드 실리카** 위 흡착이다. Cu/W/Co 금속 표면, low-k, 질화막 위 잔류(Lv3-1)는 이 골격의
  σ0·K가 다르며 미검증. 막질별 σ0는 Loewenstein이 "표면 준비법에 의존"이라고만 밝혔다.
- SCM 정전 보정은 (B)에서 필요 배수만 역산했고, 확산이중층·이온세기 의존을 갖춘 정식 풀이(FITEQL/PHREEQC)는 하지 않았다.
- Sun 2007의 Cu(OH)₂ 침전 pH(1 ppm에서 7.5)와 Lv3-1 minteq 계산(6.7) 사이 0.8 차이는 원인 미상.
- Tsutano 2025는 초록만(2차 인용). 흡착비 정의·유량 의존 수식은 원문 미확인이라 (C) 시간 인자에 유량 항을 넣지 못했다.
- Seo 2001·Martin 1999의 막대그래프 수치는 **그림 판독(±30 %)**이며 본문에 숫자로 적힌 값(10¹², 3×10¹³, 3 nm, 1 ppb, 1 ppm)만
  정확하다. Sun 2007 등온선 판독값도 같다.
- 세정 단계 η는 문헌 조건(DIW 10 min, CA 100 ppm, DHF 3 nm)의 점값이며 브러시·메가소닉·유량 의존은 없다(Lv3-1 §4 재오염 경로 미포함).

## 8. 구현 요청 후보(→ PROFILE.md)
- `competitive_langmuir_surface(metals: dict[str,(K_i, C_i)], pH, sigma0=3e12, K_H=1e3)` — §2 Eq.22 그대로. 검증값: §6(A)
  (Cr 지수 0.73±0.05, 자리분율 0.4 %, pH 3·10 nM → ~1.5×10¹⁰).
- `residual_after_clean(sigma_ads, step)` — step ∈ {DIW, CA_rinse, DHF_3nm}, η 테이블 §5·§6(C).
- 체인 조립 시 입력 순서: `free_metal_fraction` (Lv2-2) → `hydroxide_transition_pH` (Lv3-1 요청) 분기 → Langmuir/SCM →
  `boltzmann_surface_enrichment` (Lv1-1) → η.

## 9. 자기시험
→ [[../../agents/surface-contamination/EXAMS.md]] Lv3-2 문항 참조.
