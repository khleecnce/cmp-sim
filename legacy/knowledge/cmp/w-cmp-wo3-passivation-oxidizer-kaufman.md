<!-- V2-SECTION: R2-slurry | 근거: tungsten, oxidizer, WO3, passivation, 산화제 | 정본: ARCHITECTURE-V2.md §3 -->
# 텅스텐 CMP 메커니즘 — WO₃ passivation 막 형성-제거 순환과 산화제 종류별 차이

> 에이전트: film-w Lv1-1 | 작성일: 2026-09-10
> 선행: [[surface-chemistry-cu-w-pourbaix-passivation]] (부모 상속) · 관련 [[slurry-components-overview]] [[preston-luo-dornfeld-mrr]] [[cu-electrochemistry-pourbaix-bta-oxidizer-inhibitor]]

## 1. 왜 필요한가 — W CMP의 기본 원리
텅스텐은 DRAM·3D NAND의 via/plug·gate·word-line 재료다. W는 기계적으로 매우 단단한(경도가
높은) 금속이라 순수 기계연마만으로는 실용적 제거율이 안 나온다. 해법은 **화학적으로 무른
산화막(WO₃)을 표면에 만들고 그 막만 기계적으로 벗기는** 산화-제거 순환이다. 이 단원은 그
"WO₃ 막이 어떻게 형성·제거되고, 산화제 종류가 그 순환을 어떻게 바꾸는가"를 1차 논문으로 판다.

## 2. Kaufman 경쟁 모델 (1차 논문, 원문 확보)
1차 인용: F. B. Kaufman, D. B. Thompson, R. E. Broadie, M. A. Jaso, W. L. Guthrie, D. J. Pearson,
M. B. Small, "Chemical-Mechanical Polishing for Fabricating Patterned W Metal Features as Chip
Interconnects," *J. Electrochem. Soc.* 138(11), 3460–3465 (1991). DOI: 10.1149/1.2085434
(IBM Watson; W CMP의 원조 논문. 원문 PDF `papers/kaufman1991-w-cmp-mechanism.pdf` 확보·통독).

핵심 메커니즘 — **기계+화학 두 작용의 경쟁**(원문 Fig.2, Eq.[1][2]):
- 표면 WO₃ passivation 막이 있으면 W의 정적 화학용해(static etch)는 거의 멈춘다(자기제한적 부동태).
- 연마입자의 **기계적 작용**이 이 막을 벗겨 맨 W를 노출 → **화학적 작용**이 W를 용해(식각)하거나
  즉시 새 WO₃ 막으로 재부동태화. 이 형성-제거-재형성 순환이 반복되며 평탄화가 진행된다.
- 산화제(ferricyanide K₃Fe(CN)₆)는 W를 산화시키는 "전자 흡수원(electron sink)" 역할.
  용해 반응 [1]과 부동태 재형성 반응 [2]이 동시에 경쟁하며, 계면 국소 pH(완충제·약염기가 조절)가
  둘의 균형을 정한다.

원문 Eq.[1] W 용해 / Eq.[2] WO₃ 재형성 (§7 코드에서 원자·전하 균형 검증):
- [1] `W + 6Fe(CN)₆³⁻ + 4H₂O → WO₄²⁻ + 6Fe(CN)₆⁴⁻ + 8H⁺` (가용성 텅스텐산 이온으로 용해)
- [2] `W + 6Fe(CN)₆³⁻ + 3H₂O → WO₃ + 6Fe(CN)₆⁴⁻ + 6H⁺` (표면 WO₃ 재형성)
  ※ 원문 인쇄본(및 OCR)은 [2] 우변을 "8H⁺"로 표기하나, 이는 H·전하 균형상 **6H⁺가 맞고 8H⁺는
    오식으로 보인다**(§7에서 assert로 드러냄 — 문헌 표기를 맹신하지 않는다).

정량 관측값(원문 본문·Table I):
- W CMP 제거율 최대 ~400 nm/min, 대표 사례 130 nm/min (ferricyanide-phosphate + 알루미나/실리카).
- 정적 wet etch rate: pH 5.0(K-F) 8 nm/s, pH 6.5(K-F-En) 6 nm/s, pH 10.5(F-En) 43 nm/s.
  pH 10.5에서는 부동태가 깨져 압력·입자 없이도 큰 제거(=hydrodynamic wet etching) → 전역평탄화 실패.
- XPS/Auger: 연마된 W 표면에 **5–6 Å WO₃ + 그 아래 3–10 Å의 저차 산화물**(WO₃↔bulk W 전이층).
- W는 산성 pH<4에서 WO₃로 부동태화되나, 산화제+약염기 착화로 부동태 영역이 pH 6.5까지 확장.

## 3. 산화제 종류별 차이 (1차 논문, 원문 확보)
1차 인용: J.-H. Lim, J.-H. Park, J.-G. Park, "Effect of iron(III) nitrate concentration on tungsten
chemical-mechanical-planarization performance," *Appl. Surf. Sci.* 282, 512–517 (2013).
DOI: 10.1016/j.apsusc.2013.06.003 (Hanyang Univ.; 원문 `papers/lim2013-apsusc-fe-nitrate-w-cmp.pdf`
확보·통독. 조건: 1.0 wt% H₂O₂, pH 2.3, 6 psi, carrier/table 70 rpm, IC1000/SubaIV 패드).

산화제 계열별 WO₃ 형성 경로:
- **H₂O₂ 단독**: WO₃가 잘 안 생기고 다공성 저차 산화물 경로. 원문 Eq.(1)-(3):
  `W + 2H₂O₂ → WO₂ + 2H₂O` → `2WO₂ + 6H₂O₂ → H₂W₂O₁₁ + 5H₂O` → `3H₂W₂O₁₁ + 7H₂O → 2H₂W₃O₁₂ + 8H₂O₂`.
  치밀한 WO₃ 부동태막을 못 만들어 **제거율이 낮다: Fe 없이 56 Å/min = 5.6 nm/min** (Lim 2013, Fig.1).
- **Fe(NO₃)₃ 촉매 + H₂O₂ (Fenton형)**: Fe³⁺가 전자 셔틀·H₂O₂ 분해 촉매로 작용해 치밀 WO₃를 빠르게
  형성. 원문 Eq.(4)-(8): `Fe(NO₃)₃→Fe³⁺+NO₃⁻`, `Fe³⁺+W→Fe²⁺+W⁺`, `Fe²⁺+H₂O₂→Fe³⁺+H₂O+O₂↑`,
  `W+O₂→WO₂`, `WO₂+O₂→WO₃(aq)+H₂O`. (Eq.6-8은 원문의 **정성 스케치라 원자 균형이 안 맞음** — §7에서 확인.)
- **정량 촉매 효과**(Lim 2013, Fig.1): 0.01 wt% Fe(NO₃)₃ 첨가만으로 923 Å/min(=92.3 nm/min),
  0.05 wt%에서 1177 Å/min(=117.7 nm/min). H₂O₂ 단독 대비 **약 16배** 급증(region I, <0.1 wt%).
  0.1 wt% 초과(region II)에서는 완만 — 과잉 Fe³⁺가 이미 W 표면에 충분히 공급되어 율속이 바뀜.
- **ferricyanide K₃Fe(CN)₆**(Kaufman 1991): 자체가 강한 산화제라 촉매 없이 WO₄²⁻ 용해+WO₃ 재형성을
  직접 구동. **KIO₃**도 유사 산화제로 언급됨(Lim 2013 서론, 2차 인용 수준).

보조 인용(초록만 확인, 2차 인용): D. Tamboli, S. Seal, V. Desai, "XPS and Electrochemical Studies
on Tungsten-Oxidizer Interaction in Chemical Mechanical Polishing," *MRS Symp. Proc.* 566, 89–95
(1999), DOI: 10.1557/proc-566-89 — "텅스텐 산화물의 용해가 CMP에서 비기계적 W 제거의 주경로"라고
결론(UCF 리포지토리 stars.library.ucf.edu, 전문 미공개 → 초록 수준만 채택, **본문 미검증**).

## 4. 종합 — 왜 WO₃가 "좋은 무른 막"인가
① 산화제가 W(단단함)를 WO₃(무름·다공성)로 바꾸고 → ② 그 막이 자기제한적으로 성장을 멈춰 정적
부식 폭주를 억제하며 → ③ 입자가 그 막만 벗겨 다시 순환. 산화제 종류는 이 순환의 **WO₃ 형성 속도와
치밀도**를 정한다: H₂O₂ 단독(느림·다공성) < Fe 촉매 H₂O₂(빠름·치밀) ≈ ferricyanide(직접 산화).
WO₃가 무른 이유의 물리적 근거는 Pilling-Bedworth 비(§7)로 정량 확인 — W→WO₃ 산화 시 부피가
약 3.4배 팽창해 압축응력·다공성 막이 되며, 이것이 기계적으로 쉽게 벗겨지는 조건이다.

## 5. 한계 (정직 표기)
- Kaufman Eq.[2]의 우변 H⁺ 계수는 원문 인쇄본이 "8H⁺"로 되어 있으나 균형상 6H⁺ — 오식으로 판단
  (원저자 정정 여부는 미확인).
- Lim 2013 Eq.(6)-(8)은 원문이 제시한 **정성적 메커니즘 스케치**로, 원자·전하 균형이 맞지 않는다
  (§7에서 명시). 실제 Fenton 화학의 ·OH 라디컬 경로는 원문이 상세히 균형잡지 않았다 — **정성만 채택**.
- Tamboli 1999는 초록만 확보(전문 유료/미공개) — 정량값 인용 안 함, 정성 결론만.
- WO₃/W 밀도(§7 Pilling-Bedworth)는 표준 핸드북값이라 이 노트에서 1차 논문 대조는 못 했다 — **미검증(핸드북값)**.

## 6. 자기시험
→ EXAMS.md Lv1-1 참조.

## 7. 코드 재현 (문헌값 상수 박고 assert)

```python verify
# 블록1: Kaufman(1991) Eq.[1] W 용해 반응의 원자·전하 균형 검증 (질량·전하 보존 = 이론)
# W + 6 Fe(CN)6^3- + 4 H2O -> WO4^2- + 6 Fe(CN)6^4- + 8 H+
def balance(reactants, products):
    from collections import Counter
    L, R = Counter(), Counter()
    for coef, atoms, charge in reactants:
        for el, n in atoms.items(): L[el] += coef*n
        L['CHG'] += coef*charge
    for coef, atoms, charge in products:
        for el, n in atoms.items(): R[el] += coef*n
        R['CHG'] += coef*charge
    return L, R

# 원소를 {원소:개수}로. Fe(CN)6 = Fe1 C6 N6.
FeCN6 = {'Fe':1,'C':6,'N':6}
eq1_L = [(1,{'W':1},0), (6,FeCN6,-3), (4,{'H':2,'O':1},0)]
eq1_R = [(1,{'W':1,'O':4},-2), (6,FeCN6,-4), (8,{'H':1},+1)]
L,R = balance(eq1_L, eq1_R)
for k in set(L)|set(R):
    assert L[k]==R[k], f"Eq[1] 불균형 {k}: 좌{L[k]} 우{R[k]}"
print("Eq[1] W용해: 원자·전하 균형 OK ->", dict(L))

# 블록1b: 원문 인쇄 Eq.[2]는 '8H+'로 표기 -> 균형 안 맞음을 드러내고, 6H+가 맞음을 보인다.
eq2_L = [(1,{'W':1},0), (6,FeCN6,-3), (3,{'H':2,'O':1},0)]
eq2_R_orig = [(1,{'W':1,'O':3},0), (6,FeCN6,-4), (8,{'H':1},+1)]  # 원문 표기 8H+
L2,R2 = balance(eq2_L, eq2_R_orig)
mismatch = [k for k in set(L2)|set(R2) if L2[k]!=R2[k]]
assert mismatch, "원문 8H+가 균형이 맞으면 오식 가설이 틀림"
print(f"Eq[2] 원문 '8H+' 표기는 불균형 항목 {mismatch} (H: 좌{L2['H']} 우{R2['H']}, "
      f"전하: 좌{L2['CHG']} 우{R2['CHG']}) -> 오식")
eq2_R_fix = [(1,{'W':1,'O':3},0), (6,FeCN6,-4), (6,{'H':1},+1)]   # 정정 6H+
L3,R3 = balance(eq2_L, eq2_R_fix)
for k in set(L3)|set(R3):
    assert L3[k]==R3[k], f"정정 Eq[2] 불균형 {k}"
print("Eq[2] '6H+'로 정정 시 원자·전하 균형 OK")
```

```python verify
# 블록2: Lim(2013) 산화제 종류별 W CMP 제거율 — Fe(NO3)3 촉매 효과 정량 재현
# 문헌값(Appl. Surf. Sci. 282, 512, Fig.1; 1.0wt% H2O2, pH2.3, 6psi, 70rpm)
mrr_h2o2_only = 56.0    # A/min, Fe 없이 (H2O2 단독)
mrr_fe_001    = 923.0   # A/min, +0.01 wt% Fe(NO3)3
mrr_fe_005    = 1177.0  # A/min, +0.05 wt% Fe(NO3)3

# Angstrom/min -> nm/min
to_nm = lambda a: a/10.0
print(f"H2O2 단독 {to_nm(mrr_h2o2_only):.1f} nm/min, "
      f"+0.01%Fe {to_nm(mrr_fe_001):.1f} nm/min, +0.05%Fe {to_nm(mrr_fe_005):.1f} nm/min")

# 촉매 배수: Fe 미량 첨가로 10배 이상 급증해야 'Fenton 촉매 급증(region I)' 주장이 성립
ratio_001 = mrr_fe_001 / mrr_h2o2_only
assert ratio_001 > 10, f"촉매 배수 {ratio_001:.1f} — 문헌의 '급증' 서술과 불일치"
print(f"0.01wt% Fe 첨가 촉매 배수 = {ratio_001:.1f}배 (문헌: H2O2 단독은 치밀 WO3 못 만듦)")

# region I 내부 증가율 > region I->II 완만화: 0.01->0.05 구간은 아직 급증 구간
slope_I = (mrr_fe_005 - mrr_fe_001) / (0.05 - 0.01)  # A/min per wt%
assert slope_I > 0, "region I에서 농도 증가에 제거율이 늘어야 함"
print(f"region I 기울기 ~ {slope_I:.0f} (A/min)/wt% (0.01->0.05 구간)")
```

```python verify
# 블록3: WO3가 왜 무른 다공성 막인가 — Pilling-Bedworth 비(PBR)로 부피팽창 확인
# PBR = (M_ox * rho_M) / (n * M_M * rho_ox), n = 산화막 화학식당 금속원자 수
# 밀도/몰질량은 표준 핸드북값(미검증, 핸드북값) — 1차 논문 대조는 못 함.
M_W, rho_W = 183.84, 19.25     # g/mol, g/cm^3  (금속 텅스텐)
M_WO3, rho_WO3 = 231.84, 7.16  # g/mol, g/cm^3  (삼산화텅스텐)
n = 1                          # W -> WO3, 금속원자 1개

PBR = (M_WO3 * rho_W) / (n * M_W * rho_WO3)
print(f"W->WO3 Pilling-Bedworth 비 = {PBR:.2f}")
# PBR>2 이면 산화막이 큰 압축응력·다공성/크랙 경향 -> 기계적으로 쉽게 벗겨지는 '무른 막'
assert PBR > 2, f"PBR={PBR:.2f} — WO3가 팽창성 다공막이라는 근거가 약함"
# 부피 팽창 배수(몰부피 비)도 같은 결론
Vm_W  = M_W / rho_W
Vm_WO3 = M_WO3 / rho_WO3
assert abs(PBR - Vm_WO3/Vm_W) < 1e-6, "PBR과 몰부피비 정의 일치 확인"
print(f"몰부피: W {Vm_W:.2f} cm3/mol, WO3 {Vm_WO3:.2f} cm3/mol -> 부피 {PBR:.1f}배 팽창")
print("=> WO3는 부피팽창 다공막 => Kaufman/Lim의 '기계적으로 쉽게 제거되는 무른 막'과 정합")
```
