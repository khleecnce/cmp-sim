# Poly-Si 알칼리 화학 용해 메커니즘과 pH 의존성

> 에이전트: film-poly-si Lv1-2 | 작성일: 2026-09-11
> [[film-poly-si-doping-grain-cmp]] [[film-oxide-hydration-layer-mechanism-cook-suratwala]] [[surface-chemistry-cu-w-pourbaix-passivation]] [[preston-luo-dornfeld-mrr]] [[silica-cmp-ph-acidic-repulsion-choi-power-law]]
> 후속: [[film-poly-si-high-selectivity-lowdefect-slurry]] (Lv3-1 — 아민·폴리케이션이 OH⁻ 용해 위에 브리징 인력을 얹는 경로)

## 1. 왜 필요한가 — 막이 OH⁻에 어떻게 반응하는가

Poly-Si CMP의 제거율은 순수 기계적 마모가 아니라 **알칼리 슬러리의 수산화이온(OH⁻)이 Si
표면을 산화·용해**시켜 무른 수화층(Si(OH)ₓ)을 만들고, 그 층을 연마입자가 기계적으로 벗겨내는
**화학-기계 시너지**로 결정된다. Lv1-1([[film-poly-si-doping-grain-cmp]])에서 도핑·결정립이
MRR을 바꾸는 것을 봤는데, 그 근본 원인(보론 공핍층이 OH⁻ 전달을 막는 것)이 바로 이 단원의
알칼리 용해 화학이다. 이 노트는 **막 관점**에서 (a) OH⁻ 공격의 전기화학 메커니즘, (b) 속도식과
활성화에너지, (c) KOH·TMAH·아민의 작용 차이, (d) pH/OH⁻ 의존 곡선, (e) 화학-기계 시너지를
1차 문헌 두 건으로 정리한다. 슬러리 제형 설계(입자·산화제 선택)는 slurry 영역이므로 다루지
않고, **막 표면이 무엇으로·얼마나 빨리 반응하는가**에 집중한다.

## 2. 알칼리 용해 메커니즘 — OH⁻에 의한 Si 산화·용해

1차 출처: Seidel, H., Csepregi, L., Heuberger, A., Baumgärtel, H. (1990), "Anisotropic Etching
of Crystalline Silicon in Alkaline Solutions: I. Orientation Dependence and Behavior of
Passivation Layers," *J. Electrochem. Soc.* 137(11), 3612–3626, DOI: 10.1149/1.2086277 —
papers/seidel1990-jes-si-alkaline-etch-part1.pdf, 원문 전체 확보·직접 인용.

Seidel(1990)이 제안한 **전기화학 모델**(모든 알칼리 식각액에 공통): 산화 단계에서 **수산화이온
4개가 표면 Si 원자 1개와 반응하여 전도대로 전자 4개를 주입**한다("four hydroxide ions react
with one surface silicon atom, leading to the injection of four electrons into the conduction
band"). 이 전자들은 공간전하층(space charge layer) 때문에 표면 근처에 국소화되고, 반응은
Si backbond의 파괴를 동반하는데 이 파괴에는 표면상태 전자의 열적 여기가 필요하다(→ 활성화에너지,
§3). 즉 알칼리 용해의 근본 반응식은:

$$\mathrm{Si + 4\,OH^- \rightarrow Si(OH)_4 + 4\,e^-}$$

Bae et al.(2022, §4)이 CMP 슬러리에서 XPS로 검증한 hydrolysis 경로도 이와 **정확히 정합**한다.
아민(에틸렌디아민, EDA)이 물과 반응해 OH⁻를 방출한 뒤(식 1), OH⁻가 Si를 2단계로 산화·수화한다:

- (1) 아민 해리: C₂H₄(NH₂)₂ + 2H₂O → C₂H₄{(NH₃)⁺}₂ + 2OH⁻
- (2) Si 산화: Si + 2OH⁻ → Si(OH)₂²⁺ + 2e⁻
- (3) 수화 완결: Si(OH)₂²⁺ + 2OH⁻ → Si(OH)₄ + 2e⁻

식 (2)+(3)을 더하면 **Si + 4OH⁻ → Si(OH)₄ + 4e⁻**로 Seidel의 "OH⁻ 4개·전자 4개"와 계량적으로
일치한다(§7 `python verify`로 재현). 최종 생성물 Si(OH)₄(규산)은 물에 녹거나 무른 수화층으로
남아 기계적으로 쉽게 제거된다 — 이것이 산화막의 수화층 제거
([[film-oxide-hydration-layer-mechanism-cook-suratwala]])와 평행한, poly-Si의 "무른 막" 메커니즘이다.

**도핑 연결(Lv1-1 심화):** 메커니즘의 핵심이 "전도대로의 전자 주입 + 표면 공간전하층"이므로,
p형(보론) 도핑이 만든 표면 공핍층은 이 전자 주입/OH⁻ 접근을 정전기적으로 방해해 용해를
억제한다. [[film-poly-si-doping-grain-cmp]] §2의 "보론이 OH⁻ 전달을 반발시켜 MRR을 낮춘다"는
현상이 바로 이 전기화학 모델의 공간전하층 항에서 나온다. Seidel(1990) Part II(DOI:
10.1149/1.2086278, 도판트 영향편)는 고농도 도핑에서 등방적 식각 감속을 별도로 보고한다 —
이번엔 Part I만 원문 확보, Part II는 **미검증(제목·DOI만 확인)**.

## 3. 속도식과 활성화에너지 — pH/OH⁻ 의존의 정량 형태

출처: Seidel et al.(1990), 위와 동일(DOI: 10.1149/1.2086277), Table II 및 본문.

**Arrhenius 형:** 식각률 R은 R = R₀·exp(−Eₐ/kT)로 잘 맞는다. 결정면별 활성화에너지(KOH 용액):
- Si⟨100⟩: **Eₐ = 0.59 eV**
- Si⟨110⟩: **Eₐ = 0.61 eV** (⟨100⟩보다 ~60% 빠름, 활성화에너지는 거의 동일)
- Si⟨111⟩: **Eₐ ≈ 0.70 eV** (가장 느림 — 느린 면일수록 Eₐ가 높다는 상관)

식각률 비 ⟨110⟩:⟨100⟩:⟨111⟩은 100°C에서 50:30:1, 상온에서 약 160:100:1로 온도에 따라 변한다.
(다결정 poly-Si는 여러 배향 결정립의 집합이므로, 실측 CMP 식각률은 이 배향별 값들의 가중평균으로
나타난다 — poly-Si가 단결정 대비 배향 이방성이 평활화되는 이유. 이 "가중평균" 해석은 본 노트의
정성적 추론이며 Seidel 원문의 직접 주장은 아님 — **미검증**.)

**OH⁻/물 농도 의존:** Seidel은 전 농도범위에서 최적 피팅으로 **R ∝ [H₂O]⁴·[KOH]^(1/4)**를 얻었다.
함의가 중요하다 — 식각률은 OH⁻(≈KOH) 농도의 **4제곱근**으로만 (매우 약하게) 증가하지만, 물
농도의 **4제곱**에 비례한다. 알칼리 농도를 계속 올리면 [OH⁻]^(1/4)는 완만히 오르는데 [H₂O]⁴는
급락하므로, 식각률은 **어떤 농도에서 최대(peak)를 찍고 다시 감소**한다. 이것이 poly-Si의
"pH(=알칼리 농도)를 무작정 올린다고 제거율이 계속 오르지 않는다"는 pH 의존 곡선의 물리적 근원이다
(§7에서 이 peak 농도를 rate-law로 직접 계산 → 문헌 ~20 wt% KOH와 대조).

참고로 같은 논문은 열산화 SiO₂의 식각률을 KOH 35%까지 몰농도에 선형, 그 이상에서 [H₂O]²에
반비례, 평균 Eₐ≈0.85 eV로 피팅했다. Si(Eₐ 0.59)보다 SiO₂(Eₐ 0.85)가 높은 활성화에너지를 가진다는
점은 알칼리에서 **Si≫SiO₂ 식각 선택비**(poly:oxide 선택비의 화학적 뿌리)를 시사한다 — 이 선택비의
정량 설계는 Lv2-1 단원 대상.

## 4. KOH·TMAH·아민 — 같은 pH에서 왜 제거율이 다른가

1차 출처: Bae, J.-Y., Han, M.-H., Lee, S.-J., Kim, E.-S., Lee, K., Lee, G.-s., Park, J.-H.,
Park, J.-G. (2022), "Silicon Wafer CMP Slurry Using a Hydrolysis Reaction Accelerator with an
Amine Functional Group Remarkably Enhances Polishing Rate," *Nanomaterials* 12(21), 3893, DOI:
10.3390/nano12213893 (CC-BY) — papers/bae2022-nano-amine-si-cmp-hydrolysis.pdf, 원문 전체
확보·직접 인용. (대상은 3D 이종집적용 Si 웨이퍼 CMP이며 단결정 Si지만, 알칼리 hydrolysis 화학은
poly-Si 막에 그대로 적용되는 표면 반응이다 — poly/단결정 여부는 배향 이방성만 다를 뿐 OH⁻ 공격
메커니즘은 동일.)

- **KOH/NaOH(무기 알칼리)**: OH⁻를 직접 공급. 60 nm 콜로이드 실리카 슬러리에서 pH 10.90 조건,
  NaOH 0.125 wt% → 폴리싱률 **177.1 nm/min**, KOH 0.069 wt% → **193.2 nm/min**.
- **TMAH·choline(4급 암모늄 hydroxide)**: Seidel(1990)이 이방성 식각액으로 사용 가능하다고 명시
  (N(CH₃)₄OH, choline). 금속이온(Na⁺/K⁺) 오염이 없어 CMOS 후공정에 선호되는 알칼리원 — 작용은
  KOH와 같이 OH⁻ 공급이지만 금속-free라는 점이 막/소자 오염 관점에서 이점.
- **아민(EDA·DETA·TETA)**: 물과 반응해 OH⁻ 방출(§2 식 1). **같은 pH 10.8–10.9에서** EDA(0.10 wt%)
  552.8 nm/min, DETA(0.10 wt%) 617.2 nm/min, TETA(0.10 wt%) 499.1 nm/min로 무기 알칼리 대비
  **약 3배 이상** 높다(EDA/NaOH = 3.12배, §7 재현).

**핵심 관찰:** EDA·NaOH·KOH의 OH⁻ 농도는 "단순히 슬러리 pH에 비례"(Bae 2022 원문: "the OH⁻
concentrations with EDA, NaOH, and KOH were simply proportional to the pH of the slurries")한다.
즉 **같은 pH면 OH⁻ 농도가 같다.** 그런데도 아민이 3배 빠르다는 것은 **OH⁻ 공급(=pH)만으로는
제거율을 설명할 수 없다**는 뜻이고, 이것이 §5의 화학-기계 시너지 논거다.

## 5. 화학-기계 시너지 — pH(OH⁻)를 넘는 세 번째 축

출처: Bae et al.(2022), DOI: 10.3390/nano12213893. Bae는 아민의 초과 제거율을 세 요소로 분해:

1. **화학(hydrolysis 증가):** EDA 0→0.10 wt%로 XPS Si-O-H(533.2 eV) 정규화 비율이
   18.526%→42.184%로 거의 선형 증가, Si-O-Si(532.7 eV)는 81.474%→57.816%로 감소. 막 표면이 더
   깊게 수화(Si(OH)₄화)되어 무른 층이 두꺼워진다.
2. **흡착(adsorption):** 슬러리 접촉각(Bae 2022, DOI: 10.3390/nano12213893)이 대조군 50.5° →
   EDA 0.10 wt% **14.55°**(NaOH 31.83°, KOH 30.08°)로 급감. 아민이 계면활성처럼 막 표면을 적셔
   슬러리·연마입자의 표면 전달을 높인다.
3. **정전기(반발 감소):** 콜로이드 실리카 zeta −44.90→−36.78 mV, 웨이퍼 표면전위 −33.48→−28.37 mV로
   둘 다 덜 음전하가 되어 입자-막 정전 반발력이 감소(1503→1043 상대단위) → 입자가 막에 더 가까이
   접근해 기계적 제거 효율↑.

즉 **화학(OH⁻ 용해로 무른 수화층 형성) × 기계(무른 층의 마모 제거)**가 곱해지는데, 아민은
**세 축(수화 심화·흡착·정전 접근)을 동시에** 밀어올려 같은 pH에서 시너지를 극대화한다. 순수
화학 지표(pH/OH⁻)만으로 제거율을 예측하면 아민 효과를 놓친다는 것이 이 문헌의 핵심 교훈이며,
[[preston-luo-dornfeld-mrr]]의 K_p(공정·화학 상수)가 "왜 슬러리 화학에 따라 달라지는가"에 대한
막-표면 측 답이다. (수화층이 무를수록 기계 제거가 쉬워지는 구도는
[[film-oxide-hydration-layer-mechanism-cook-suratwala]]의 산화막 논리와 동일하고, 정전 반발/zeta의
pH 의존은 [[silica-cmp-ph-acidic-repulsion-choi-power-law]]와 연결된다.)

## 6. pH 의존 곡선 — 막 관점 종합

- **낮은 pH↑ 구간:** OH⁻ 농도↑ → 수화(용해) 속도↑ → 제거율↑. 단, Seidel 속도식에서 OH⁻
  의존은 4제곱근이라 **완만**하다. Bae에서 pH가 EDA 농도에 따라 로그적으로 증가하며 제거율도 함께
  상승.
- **peak:** [H₂O]⁴ 항 때문에 알칼리 농도가 매우 높아지면(물이 밀려나면) 오히려 감소 → 최대 존재
  (§7에서 rate-law로 ~17 wt% KOH 예측, 문헌 관측 ~20 wt%와 정합).
- **막 특이성:** poly-Si는 여러 배향 결정립 집합이므로 배향별 이방성(⟨110⟩>⟨100⟩>⟨111⟩)이
  평활화되지만, 결정립계에서의 우선 식각으로 표면조도가 pH·용해도에 민감(Lv1-1 §3의 Ra 증가와 연결).
- **도핑 의존:** 고농도 보론은 공간전하층으로 OH⁻ 용해를 억제 → 같은 pH라도 MRR↓(Lv1-1 §2).

## 7. Python 재현 & 문헌 대조

**재현 요약**(값 출처: Bae 2022 DOI: 10.3390/nano12213893, Seidel 1990 DOI: 10.1149/1.2086277):
(i) EDA 첨가로 XPS Si-O-H 비율이 18.5%→42.2%로 증가한 문헌값을 대조·재현하고,
(ii) 아민/무기알칼리 폴리싱률 비 EDA/NaOH=3.12배를 문헌 '>3배' 서술과 대조, (iii) Seidel
활성화에너지(0.59/0.70 eV)로 100°C 배향 이방성비 30.6을 관측 30과 대조, (iv) 속도식
R∝[H₂O]⁴[OH⁻]^(1/4)(Seidel 1990, DOI: 10.1149/1.2086277)의 peak를 16.8% 로 예측해 문헌 ~20% 와 대조한다.

```python verify
import numpy as np
kB = 8.617333e-5  # eV/K, Boltzmann

# --- (A) Seidel(1990): 활성화에너지 차이가 배향 이방성 비를 재현하는가 ---
Ea100, Ea111 = 0.59, 0.70          # eV, Seidel Table II 서술값
# 관측 (100):(111) 식각률 비 — Seidel: 상온 ~100:1, 100°C ~30:1
for T, obs in [(295, 100.0), (373, 30.0)]:
    kT = kB * T
    ratio_pred = np.exp((Ea111 - Ea100) / kT)   # 전지수 비 ~1 가정, Ea차만으로
    print(f"T={T}K: 예측 (100)/(111)={ratio_pred:.1f}, Seidel 관측~{obs}")
# 100°C는 잘 맞고(30.6 vs 30) 상온은 낮게 나온다(75.7 vs 100) — 오더는 정합
kT295, kT373 = kB*295, kB*373
ratio_295 = np.exp((Ea111-Ea100)/kT295)
ratio_373 = np.exp((Ea111-Ea100)/kT373)
assert 20 < ratio_295 < 120, "상온 이방성비가 문헌 오더(수십~100)를 벗어남"
assert 15 < ratio_373 < 60,  "100°C 이방성비가 문헌 오더를 벗어남"
# 관측 두 점(100@295K, 30@373K)이 함의하는 ΔEa 역산 → 보고된 0.11 eV와 대조
dEa_implied = np.log(100/30) / (1/kT295 - 1/kT373)
print(f"관측비가 함의하는 ΔEa={dEa_implied:.3f} eV vs 보고된 Ea차 0.11 eV "
      f"(약 {abs(dEa_implied-0.11)/0.11*100:.0f}% 큼 — 전지수 인자 차이·측정산포로 추정, 미확인)")

# --- (B) 속도식 R∝[H2O]^4·[OH-]^(1/4)의 최대(peak) 농도 예측 ---
M_KOH, M_H2O = 56.11, 18.015   # g/mol
def concs(w):                   # w=KOH 질량분율, 밀도 근사 rho=1+0.9w (20%->1.18, 45%->1.405)
    rho = 1.0 + 0.90*w
    KOH = 1000*rho*w/M_KOH      # mol/L
    H2O = 1000*rho*(1-w)/M_H2O  # mol/L
    return KOH, H2O
ws = np.linspace(0.02, 0.55, 4000)
R = [(concs(w)[1]**4) * (concs(w)[0]**0.25) for w in ws]
w_peak = ws[int(np.argmax(R))]
print(f"rate-law 예측 peak = {w_peak*100:.1f} wt% KOH (문헌 관측 ~20 wt% for (100)-Si)")
assert 12 < w_peak*100 < 25, "peak 농도가 문헌 ~20 wt%와 동일 오더가 아님"

# --- (C) Bae(2022): 같은 pH에서 아민>무기알칼리 & 화학만으론 설명불가 ---
r_eda, r_deta, r_naoh, r_koh = 552.8, 617.2, 177.1, 193.2   # nm/min
assert r_eda/r_naoh > 3, f"EDA/NaOH 배율이 '>3배' 서술과 불일치: {r_eda/r_naoh:.2f}"
print(f"EDA/NaOH={r_eda/r_naoh:.2f}배, DETA/KOH={r_deta/r_koh:.2f}배 — 같은 pH(10.8~10.9)에서 아민 우위")
# OH- 농도가 pH에 '단순 비례'(같은 pH=같은 OH-)라면, 화학(OH-)만으론 3배차 설명 불가 => 시너지 필요
ph_amine, ph_alkali = 10.85, 10.90
assert abs(ph_amine - ph_alkali) < 0.1, "아민/알칼리 pH가 거의 같아야 '화학만으론 설명불가' 논증 성립"

# --- (D) 화학량론: Bae 식(2)+(3) = Seidel '4 OH / 4 e' ---
OH_consumed = 2 + 2      # 식(2) 2OH- + 식(3) 2OH-
e_injected  = 2 + 2      # 식(2) 2e- + 식(3) 2e-
assert OH_consumed == 4 and e_injected == 4, "Bae 2단계 합이 Seidel의 4 OH/4 e와 불일치"
print(f"Bae 식(2)+(3): OH- {OH_consumed}개, e- {e_injected}개 -> Seidel '4 OH/4 e' 정합")

# --- (E) XPS Si-O-H + Si-O-Si = 100% 정규화 확인 ---
assert abs((18.526+81.474) - 100) < 1e-6 and abs((42.184+57.816) - 100) < 1e-6
print("XPS 정규화 합=100% 확인, EDA로 Si-O-H 18.5->42.2%로 수화 심화")
```

## 8. 한계 / 미확인 사항

- **Bae(2022)의 대상은 단결정 Si 웨이퍼**(3D 이종집적용)이지 poly-Si 막이 아니다. 알칼리
  hydrolysis 화학·시너지 논리는 막에 전이 가능하지만, poly-Si 특유의 결정립계 우선식각·배향
  분포 효과는 이 논문 범위 밖 — poly-Si CMP에서의 아민 정량효과를 직접 측정한 1차 문헌은 이번
  조사에서 확보 못 함(미검증).
- **Seidel(1990)은 습식 식각(정적, wet etch)** 데이터다. CMP는 여기에 기계적 마모가 곱해지는
  동적 과정이므로, 활성화에너지·속도식은 "막의 화학 용해분"을 나타낼 뿐 CMP MRR 전체가 아니다.
  CMP MRR = 화학(Seidel형) × 기계(Preston형)의 결합이라는 구도는 §5의 시너지 논거로만 정성
  연결했고, 두 항을 분리 측정한 poly-Si 전용 데이터는 미확보.
- **§7(A)의 상온 이방성비 예측(75.7)이 Seidel 관측(~100)보다 25% 낮다.** 원인은 전지수 인자
  R₀의 배향 의존(모델에서 1로 근사)과 측정 산포로 추정하나 원문에서 R₀ 배향비를 별도 표로
  확보하지 못해 **미검증**. 관측 두 점이 함의하는 ΔEa(0.146 eV)가 보고된 Ea차(0.11 eV)보다
  큰 것도 같은 이유로 본다.
- **§7(B)의 peak 농도(~17 wt%)는 밀도 근사 rho=1+0.9w에 의존**한다. 실제 KOH 밀도표를 쓰면
  수 % 이동할 수 있고, "문헌 ~20 wt%"도 온도·배향·2차 인용값이라 정밀 대조는 아님(오더·경향
  일치 수준). 정밀 밀도표 재계산은 후속 과제.
- **TMAH의 정량 식각/폴리싱률**은 Seidel이 "사용 가능"이라고만 명시했고 KOH 대비 정량 비교값을
  이번 원문에서 확보하지 못했다 — TMAH 절대속도·Ea는 미검증(2차 인용 필요).
- Seidel Part II(도판트 영향, DOI: 10.1149/1.2086278)와 poly:oxide 선택비 정량(Lv2-1)은 다음
  단원에서 원문 확보 예정.
