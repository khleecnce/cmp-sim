# 최신 리뷰: 저압 Cu CMP, 갈바닉 부식, 고종횡비 배선 (film-cu Lv3-1)

> film-cu Lv3-1 | 작성일: 2026-09-12
> 선행: [[cu-electrochemistry-pourbaix-bta-oxidizer-inhibitor]] (Lv1-2 — Cu 혼합전위·BTA 막. 이 노트 §3의 "부식전위 차 ΔE_corr"는 그 노트의 E_mix 개념을
> 두 금속에 확장한 것) [[film-cu-barrier-ta-tan-co-selectivity]] (Lv2-2 — Ta/TaN/Co 선택비. 그 노트 §4가 Co에서 지적한 "부식전위 매칭"을 이 노트는 Ru·Mo에서
> 정량 실측으로 확인한다) [[cu-dishing-erosion-density-step-height-model-tugbawa]] (Lv2-1 — 선택비 1:1이 왜 dishing/erosion 억제 조건인가)
> 관련: [[cu-cmp-three-step-process-slurry-requirements]] [[preston-luo-dornfeld-mrr]] [[hertz-gw-contact-mechanics]]
> [[low-level-metal-cobalt-ruthenium-cross-contamination]] [[inhibitor-chelator-adsorption-isotherm-passivation]]
> 스코프: (1) 왜 배선 스케일링(고종횡비·초박 배리어)이 Cu CMP 요구를 "저압 + 배리어:Cu 1:1 + 갈바닉 억제"로 바꾸는가, (2) 갈바닉 부식의 정량
> 물리 — ΔE_corr·면적비·마찰 재부동태 속도, (3) 억제 전략 3종(Cu 쪽 막 강화 / Ru 쪽 OCP 이동 / 화학 매칭)의 실측 수치, (4) 저압 CMP의 MRR 문제.
> 제외: Ta/TaN 화학 자체(Lv2-2), 도금(SCOPE 제외 키워드), 패드 구조 설계(pad 에이전트 영역 — Han 2012는 "저압 동기" 부분만 인용).

## 0. 출처 (6건: 1차 논문 3 + 리뷰 1 + 특허 1 + 학위논문 1, 전부 원문 전체 확보)

1. **[1차·원문 전체]** K. Lee, S. Sun, G. Lee, G. Yoon, D. Kim, J. Hwang, H. Jeong, T. Song, U. Paik, "Galvanic corrosion inhibition from aspect of
   bonding orbital theory in Cu/Ru barrier CMP," *Sci. Rep.* 11, 21214 (2021), doi.org/10.1038/s41598-021-00689-6 (PMC8551296, CC-BY;
   papers/PMC8551296.xml). §3·§4의 Cu/Ru E_corr·R_p·제거율 표(Table 1–3)는 전부 이 논문. 조건: 1.5 psi, 79/80 rpm, 100 mL/min, IC1010/Suba IV,
   콜로이드 실리카 5 wt%(70 nm) + H₂O₂ 3 wt% + KIO₄ 0.05 M + 구연산 0.1 M + Mn(NO₃)₂ 0.01 M, pH 10(KOH), 억제제 니코틴산 0–0.05 M.
2. **[1차·원문 전체]** K. U. Gamagedara, D. Roy, "Mechanisms of Chemically Promoted Material Removal Examined for Molybdenum and Copper CMP in
   Weakly Alkaline Citrate-Based Slurries," *Materials* 17(19), 4905 (2024), doi.org/10.3390/ma17194905 (data/corpus/fulltext/doi_10.3390_ma17194905.xml).
   §5의 저압(0.014 MPa) Cu/Mo 제거율·선택비 창은 이 논문.
3. **[리뷰·원문 전체]** S. Moon, S. Jeong, D. Kim, J. Kim, J. Oh, H. Lee, S. Han, H. Kim et al., "Materials Quest for Advanced Interconnect Metallization
   in Integrated Circuits," *Adv. Sci.* 10, 2207321 (2023), doi.org/10.1002/advs.202207321 (PMC10427378). §1의 배선 스케일링 수치(20 nm 트렌치·AR 2에서
   3 nm Ta/TaN 면적 >30 %, 10 nm 하프피치 선저항 3배)는 이 리뷰의 서술 — **리뷰이므로 원논문 미추적 수치는 "2차 인용"으로 표기**.
4. **[1차·원문 전체, 가설 논문]** G. Han, Y. Liu, X. Lu, J. Luo, "A flexible nanobrush pad for the chemical mechanical planarization of Cu/ultra-low-к
   materials," *Nanoscale Res. Lett.* 7, 603 (2012), doi.org/10.1186/1556-276X-7-603 (PMC3499454). §6의 저압 정의(정상 2–8 psi vs 저압 <1 psi·0.5 psi)와
   "저압에서는 CMP가 기계적으로 제한된다"는 논지·참고문헌만 인용. 실험 MRR 데이터는 없다(패드 설계 자체는 pad 에이전트 영역이라 제외).
5. **[특허·1차]** Cabot Microelectronics, "Compositions and methods for ruthenium and tantalum barrier CMP," KR101557514B1 (data/corpus/fulltext/
   patent_KR101557514B1.txt, 한/영 병기 전문). §4의 "암모니아 유도체가 Ru OCP를 100 mV 낮춰 Cu와 근접시킨다"는 실시예 2·6C 서술과 청구항.
   표 2·3의 개별 OCP 수치는 텍스트 추출에서 표가 비어 있어 **미확보** — "100 mV"라는 본문 요약치만 쓴다.
6. **[학위논문·원문 전체]** S. Tamilmani, *Electrochemical and chemical aspects of copper CMP: dissolution, corrosion, passivation, and waste treatment*,
   Univ. of Arizona PhD (2005), hdl.handle.net/10150/280774 (papers/tamilmani2005-ua-thesis-cu-cmp-dissolution-corrosion.pdf, Lv1-2에서 확보). §3의
   Cu/Ta 갈바닉 전류 직접 실측(Table 4.7/4.8, Fig 4.49/4.50)은 이 논문. 2005년이지만 SCOPE before_year 1990 이후이고, "마찰 중 갈바닉 전류 직접 측정"은
   이후 문헌(Lee 2021·Gamagedara 2024)이 채택한 tribo-electrochemical 방법의 원형이라 채택.

2차 인용(원문 미확보, DOI는 위 논문 참고문헌 목록에서 옮김): Pandija, Roy, Babu 2009 *Microelectron. Eng.* 86, 367 (저압 Cu CMP 평탄화 효율,
doi.org/10.1016/j.mee.2008.11.047 ); Peethala, Roy, Babu 2011 *ECS Solid-State Lett.* 14, H306 (Cu/Ru 갈바닉 — BTA + 아스코르브산,
doi.org/10.1149/1.3589308 ); Cheng, Pan, Wang, Lu 2018 *Corros. Sci.* 137, 184 (KIO₄ 중 Cu/Ru 미세갈바닉, doi.org/10.1016/j.corsci.2018.03.045 ).
Tai et al.의 Cu/W > Cu/WN > Cu/TaN > Cu/Ta 갈바닉 전류 서열(2–32 µA/cm²)은 Tamilmani 2005 §2.2.5.3의 2차 인용이며 화학·pH 불명.

## 1. 왜 스케일링이 Cu CMP 요구를 바꾸는가 — 고종횡비·초박 배리어

Moon et al.(2023) 리뷰의 핵심 수치: 트렌치 폭 20 nm·종횡비 2에서 3 nm Ta/TaN 이중층이 단면적의 >30 %를 차지하고, 이 다층 구조가 10 nm 하프피치
Cu 선저항을 3배 이상 올린다(리뷰 서술, 원논문 미추적 — 2차 인용). 배리어 두께는 "더 줄일 수 없는 지점"에 도달했고(Cu 확산 차단 실패), 그래서
(a) Ru 같은 단일 라이너로 Ta/TaN을 대체하거나 (b) 배리어리스 Ru·Mo 배선으로 가는 두 갈래가 생긴다. Lee et al.(2021) 서론도 같은 그림을 준다:
Ta/TaN은 170–250 Å이 필요했는데 Ru 배리어는 40–50 Å로 충분하고, Cu를 시드 없이 Ru 위에 직접 도금할 수 있다.

CMP 관점에서 이 전환이 뜻하는 것 세 가지(이 노트의 뼈대):

- **배리어:Cu 선택비 목표가 1:1로 바뀐다.** Lv2-2의 Ta 특허 목표(TaN:Cu ≥ 3–4:1)와 달리, Ru 배리어 구조에서는 "완전 평탄면"을 위해 Cu:Ru 1:1이
  요구된다(Lee 2021, 원문: "the Cu to Ru selectivity requirement to achieve a completely flat surface is 1:1"). Gamagedara & Roy(2024)도 Mo 배리어에서
  [Mo:Cu] 목표창을 1 ± 0.5로 잡는다 — 이유는 [[cu-dishing-erosion-density-step-height-model-tugbawa]]의 removal-rate diagram에서 배리어 클리어 단계의
  r_b ≈ r_cu이면 Cu와 배리어가 같은 속도로 내려가 pre-dishing이 생기지 않기 때문이다.
- **갈바닉 커플이 Cu/Ta에서 Cu/Ru·Cu/Co·Cu/Mo로 바뀐다.** Ru는 Cu보다 훨씬 귀한 금속이라 Cu가 양극(용해)이 된다 — Lee 2021 실측 ΔE_corr 0.49 V.
  Moon 2023 리뷰도 "Ru와 Cu의 큰 전위 차가 Cu의 심한 갈바닉 부식을 일으킨다"를 Ru 도입의 최대 장애(CMP)로 꼽는다.
- **저압이 강제된다.** ULK 유전체(저밀도·저강도)와 좁은 고종횡비 배선은 수 psi의 다운포스를 견디지 못한다 — Han 2012가 인용하는 ITRS 2011 문제의식.
  §6에서 다룬다.

```python verify
# Moon et al. 2023 (doi.org/10.1002/advs.202207321) 서술 재현: 20 nm 트렌치, 종횡비 2, 3 nm Ta/TaN → 배리어 단면적 >30 %
w_nm, AR, t_nm = 20.0, 2.0, 3.0
h_nm = w_nm * AR                       # 40 nm
A_tot = w_nm * h_nm                    # 800 nm^2
A_bar = 2 * t_nm * h_nm + t_nm * (w_nm - 2 * t_nm)   # 양 측벽 + 바닥 = 240 + 42 = 282 nm^2
frac = A_bar / A_tot                   # 0.3525
assert 0.30 < frac < 0.40, f"배리어 면적비 {frac:.3f} — 리뷰의 '>30 %'와 불일치"

# Lee et al. 2021 서론 수치: Ta/TaN 170-250 Å vs Ru 40-50 Å 이 같은 20 nm 트렌치에 들어가면?
t_tatan_nm = 17.0                      # 170 Å 하한
assert w_nm - 2 * t_tatan_nm < 0, "17 nm Ta/TaN 두 측벽이 20 nm 트렌치를 넘친다 — Cu가 들어갈 자리가 없음(스케일링 한계의 산술적 이유)"
t_ru_nm = 4.5                          # 40-50 Å 중간
A_ru = 2 * t_ru_nm * h_nm + t_ru_nm * (w_nm - 2 * t_ru_nm)   # 360 + 49.5 = 409.5
cu_frac_ru = 1 - A_ru / A_tot          # 0.488
assert 0.45 < cu_frac_ru < 0.52
print(f"Ta/TaN 3 nm 면적비 {frac:.3f} (>0.30 OK); Ru 4.5 nm일 때 Cu 점유율 {cu_frac_ru:.3f}; 17 nm Ta/TaN은 20 nm 트렌치에 못 들어감")
```

## 2. 갈바닉 부식의 물리 — 무엇이 크기를 정하는가

Tamilmani(2005) §2.2.5.3의 정식화: 두 금속이 전기적으로 연결되면 귀한 금속(음극)의 환원 분극곡선과 활성 금속(양극)의 산화 분극곡선 교점이 갈바닉
전위 E_gal·전류 I_gal을 준다. CMP에서 크기를 정하는 인자는 세 가지다.

1. **부식전위 차 ΔE_corr** — 구동력. Cu/Ru(Lee 2021, pH 10 KIO₄+H₂O₂): 0.49 V. Cu/Ta(Tamilmani 2005): 커플 전위 자체가 화학에 따라 0.02–0.5 V vs SHE
   범위에서 움직인다(Table 4.7). 같은 Cu라도 상대 금속·산화제에 따라 구동력이 한 자릿수 달라진다.
2. **면적비** — 벌크 Cu 제거 직후에는 배리어 면적 ≫ Cu 면적이지만, 오버폴리시로 유전체가 드러나면 Cu 면적 ≫ 배리어 면적이 되어 **작은 쪽(양극이면
   배리어, Cu/Ru면 Cu 배선)의 전류밀도가 급등**한다(Tamilmani 2005 §2.2.5.3 — 정성 서술, 면적비 수치는 없음). Cu/Ru 구조에서는 Cu가 양극이므로
   오버폴리시 단계에서 좁은 Cu 배선이 큰 Ru 면적의 음극 전류를 받는다 — 고종횡비·좁은 선폭일수록 불리하다(이 확장은 이 노트의 추론, **미검증**).
3. **마찰에 의한 재부동태 파괴** — 갈바닉 전류는 정지 상태가 아니라 **마찰 중**에 결정된다. Tamilmani(2005) Table 4.7: 0.5 M 하이드록실아민 pH 6에서
   Cu/Ta 갈바닉 전류밀도는 마찰 중 500 µA/cm², 마찰 없음 <2 µA/cm² — 250배 차이. 시료 회전을 222 → 90 rpm으로 낮추면(패드 접촉 주기 0.27 → 0.66 s)
   500 → ~180 µA/cm²로 떨어져 회전속도에 거의 비례(Fig 4.49). 즉 Ta의 산화막이 깎이는 빈도가 갈바닉 전류를 정한다.

이 세 인자를 Faraday 환산으로 CMP 제거율 단위에 놓으면 갈바닉 부식이 "얼마나" 문제인지가 보인다.

```python verify
# Tamilmani 2005 (hdl 10150/280774) Table 4.7/4.8 + 본문 §4.4.3-4.4.4 재현 — Faraday 환산으로 갈바닉 전류를 Å/min에 놓는다
F = 96485.33          # C/mol
M_Ta, rho_Ta, n_Ta = 180.948, 16.65, 5      # g/mol, g/cm^3, Ta -> Ta(V)
def ta_rate_A_per_min(i_uA_cm2):
    cm_per_s = (i_uA_cm2 * 1e-6) * M_Ta / (n_Ta * F * rho_Ta)
    return cm_per_s * 1e8 * 60.0
r10 = ta_rate_A_per_min(10.0)                   # 논문 본문: "10 µA/cm² ≡ 1.3 Å/min"
assert abs(r10 - 1.3) / 1.3 < 0.06, f"Faraday 환산 {r10:.2f} Å/min vs 논문 1.3 Å/min"
# 비커플 Ta 부식전류 86 µA/cm²(pH 6 하이드록실아민) → 논문 "11 Å/min"
r_uncoupled = ta_rate_A_per_min(86.0)
assert abs(r_uncoupled - 11.0) / 11.0 < 0.08, f"{r_uncoupled:.1f} vs 11"
# 마찰 중 갈바닉 500 µA/cm² → 실제 Ta 폴리시율 150 Å/min의 몇 %인가
r_gal = ta_rate_A_per_min(500.0)                # 67.6 Å/min
frac_gal = r_gal / 150.0
assert 0.40 < frac_gal < 0.50, f"갈바닉 등가 {r_gal:.0f} Å/min = 폴리시율의 {frac_gal:.0%}"
# 과산화수소계(Table 4.7: 40-120 µA/cm²)는 3-11 % — 저자의 "slightly increase"는 이 계에서만 정량적으로 성립
lo, hi = ta_rate_A_per_min(40.0) / 150.0, ta_rate_A_per_min(120.0) / 150.0
assert lo < 0.05 and hi < 0.12
# 회전속도 비례성: 500 µA/cm² @222 rpm vs ~180 @90 rpm
ratio_i, ratio_rpm = 500.0 / 180.0, 222.0 / 90.0
assert abs(ratio_i - ratio_rpm) / ratio_rpm < 0.15, f"전류비 {ratio_i:.2f} vs rpm비 {ratio_rpm:.2f}"
# 마찰 정지 후 감쇠: 하이드록실아민은 10 s 내 <10 µA/cm², H2O2 pH 6/8은 ~10 µA/cm²에서 포화 → 90 s 이송 중 Ta 손실
loss_90s = ta_rate_A_per_min(10.0) * 1.5
assert loss_90s < 3.0, f"{loss_90s:.1f} Å"
print(f"10 µA/cm² = {r10:.2f} Å/min; 갈바닉 500 µA/cm² = {r_gal:.0f} Å/min = 폴리시율 {frac_gal:.0%}; "
      f"H2O2계 {lo:.0%}-{hi:.0%}; rpm 비례 편차 {abs(ratio_i-ratio_rpm)/ratio_rpm:.0%}; 이송 90 s Ta 손실 {loss_90s:.1f} Å")
```

**해석(정직하게)**: 하이드록실아민계에서는 갈바닉 등가 제거율 68 Å/min이 실제 폴리시율 150 Å/min의 45 %로 작지 않다 — 논문의 "slightly increase"
서술은 H₂O₂계(3–11 %)에서만 정량적으로 성립하고, 하이드록실아민계에서는 저자의 표현이 과소하다고 본다(이 판단은 이 노트의 계산이며, 저자는
"비커플 11 Å/min ≪ 실측 150 Å/min이니 기계 지배"라는 논리를 폈다 — 비교 대상이 다르다). 마찰 정지 후에는 어느 계든 이송 90 s 동안 Ta 손실이
2 Å 미만이라 "폴리셔→클리너 이송 중 갈바닉 손상 없음"은 두 계 모두에서 성립한다. 단 H₂O₂ pH 6–8은 10 µA/cm²에서 포화해 0으로 안 떨어지므로
세정 전 잔류 화학 제거가 필수라는 저자 결론은 유지된다. 이 실측은 Cu/Ta 커플이며 Cu/Ru로의 전이는 **미검증**(부호가 반대 — Cu/Ru에서는 Cu가 양극).

## 3. 억제 전략 ① Cu 쪽 막을 선택적으로 강화 — Lee et al. 2021 (Cu/Ru, pH 10)

Lee et al.(2021)은 억제제 설계를 결합 궤도론으로 설명한다: 피리딘 고리의 N은 σ-결합으로 어느 금속 산화물에도 붙지만, π-역결합은 d-궤도가 꽉 찬
Cu⁺(3d¹⁰, Cu₂O)에서만 강하고 Ru⁴⁺(4d⁴)에서는 약하다. 그래서 니코틴산(3-피리딘카르복실산)은 Cu 위에 치밀한 막, Ru 위에 성긴 막을 만든다. 근거:

- 접촉각: 니코틴산 첨가로 Cu 28.7° → 41.9°(+13.2°), Ru 58.4° → 62.1°(+3.7°).
- XPS: Cu 2p·O 1s의 Cu₂O 피크가 0.05 M에서 급감(막이 Cu₂O 위에 형성), CuO 피크는 변화 적음 → **Cu⁺(Cu₂O) 선택 흡착**. Ru 3d·O 1s는 무변화.
- 전기화학(Table 1, V vs Ag/AgCl 3 M KCl): 니코틴산 0 → 0.05 M에서 Cu E_corr −0.27 → +0.36 V(+0.63 V), Ru 0.22 → 0.45 V(+0.23 V) →
  **ΔE_corr 0.49 → 0.09 V**. EIS R_p(Table 2): Cu 5,704 → 49,897 Ω·cm²(η 88.6 %), Ru 69,518 → 78,549(η 11.5 %).
- CMP(Table 3, 1.5 psi): Cu 95.98 → 26.23 Å/30 s(−73 %), Ru 24.85 → 25.0 Å/30 s(불변) → **Cu/Ru 선택비 3.86 → 1.05**. Cu R_q도 감소.

핵심 메시지: **한 분자로 갈바닉 억제(ΔE↓)와 선택비 1:1을 동시에** 얻는다 — Cu 양극 반응을 막는 막이 곧 Cu 제거율을 낮추는 막이기 때문. 이는
[[cu-electrochemistry-pourbaix-bta-oxidizer-inhibitor]]에서 본 BTA-Cu(I) 고분자막과 같은 논리(Cu⁺ 선택)이며, pH 10에서 Cu₂O가 안정한 것도 그 노트의
Pourbaix 경계와 일치한다. 주의: I_corr는 억제제 첨가로 오히려 증가(Cu 0.22 → 0.47 mA/cm²)하는데 저자는 이를 논하지 않는다 — Tafel 외삽 I_corr와
EIS R_p가 반대 방향인 이유는 **불명**(이 노트에서 해결 못 함).

```python verify
# Lee et al. 2021 Sci Rep (doi.org/10.1038/s41598-021-00689-6, PMC8551296) Table 1-3 재현
Ecorr = {"0 M": (-0.27, 0.22), "0.03 M": (0.26, 0.41), "0.05 M": (0.36, 0.45)}   # (Cu, Ru) V vs Ag/AgCl
gap = {k: ru - cu for k, (cu, ru) in Ecorr.items()}
assert abs(gap["0 M"] - 0.49) < 1e-9 and abs(gap["0.05 M"] - 0.09) < 1e-9, gap   # 본문 "0.49 → 0.09 V"
assert abs((0.36 - (-0.27)) - 0.63) < 1e-9 and abs((0.45 - 0.22) - 0.23) < 1e-9  # 본문 Cu +0.63 V, Ru +0.23 V

Rp = {"Cu": (5704.2, 13830.0, 49897.0), "Ru": (69518.0, 74011.0, 78549.0)}       # Ω·cm², 0/0.03/0.05 M
eta_lit = {"Cu": (58.75, 88.57), "Ru": (6.07, 11.50)}
for m, (r0, r1, r2) in Rp.items():
    for r, e_lit in zip((r1, r2), eta_lit[m]):
        eta = (r - r0) / r * 100.0                     # 논문 정의 η = (Rp − Rp0)/Rp
        assert abs(eta - e_lit) < 0.02, (m, eta, e_lit)

RR = {"Cu": (95.98, 41.33, 26.23), "Ru": (24.85, 24.52, 25.0)}                    # Å/30 s
sel_lit = (3.86, 1.69, 1.05)
for cu, ru, s in zip(RR["Cu"], RR["Ru"], sel_lit):
    assert abs(cu / ru - s) < 0.01, (cu / ru, s)
cu_nm_min = RR["Cu"][0] * 2 / 10.0                    # 19.2 nm/min @1.5 psi
ru_nm_min = RR["Ru"][0] * 2 / 10.0                    # 4.97 nm/min
assert 19.0 < cu_nm_min < 19.4 and 4.9 < ru_nm_min < 5.1
cu_drop = 1 - RR["Cu"][2] / RR["Cu"][0]               # 0.727
assert 0.70 < cu_drop < 0.75
assert abs(RR["Ru"][2] / RR["Ru"][0] - 1) < 0.02       # Ru 불변
print(f"ΔEcorr {gap['0 M']:.2f}→{gap['0.05 M']:.2f} V; η_Cu {[(r - Rp['Cu'][0]) / r * 100 for r in Rp['Cu'][1:]]}; "
      f"Cu {cu_nm_min:.1f} nm/min, Ru {ru_nm_min:.2f} nm/min @1.5 psi; Cu −{cu_drop:.0%}, 선택비 {RR['Cu'][0]/RR['Ru'][0]:.2f}→{RR['Cu'][2]/RR['Ru'][2]:.2f}")
```

수계산 대조 (Lee et al. 2021 Table 1–3): ΔE_corr 0.49 → 0.09 V, η_Cu 58.75/88.57 %, η_Ru 6.07/11.50 %, 선택비 3.86/1.69/1.05 — 논문 표기와 0.01 이내 일치.
Cu 19.2 nm/min·Ru 4.97 nm/min(1.5 psi) 환산은 이 노트의 계산. **주의: 이 세션은 python 실행 승인이 없어 위 블록을 기계로 돌리지 못했다** — 총괄이
`tools/verify_claims.py`로 실행해 확인해야 하며, 그 전까지 "수계산 통과"로만 표기한다.

## 4. 억제 전략 ② Ru 쪽 전위를 끌어내림 — Cabot KR101557514B1

Lee 2021이 Cu 전위를 올려 간격을 좁혔다면, Cabot 특허는 반대편(Ru)을 움직인다. 명세서(실시예 2): pH 9.5, 콜로이드 실리카 4 wt%, 과붕산나트륨
1 wt%(산화제) + BTA + 암모늄 아세테이트 0–x wt%(조성 2A–2D)에서 회전전극(500 rpm)으로 마모 중/무마모 OCP를 측정. 결과 서술: 암모니아 유도체는
Cu OCP에는 영향이 없고 **Ru OCP를 100 mV 낮춰** Cu와 근접시킨다(조성 2A vs 2D). 실시예 6C: 사붕산염 + H₂O₂ 조합에 암모니아를 넣어도 Ru OCP가 100 mV
넘게 내려간다. 청구항은 암모니아 유도체를 암모늄염·하이드록실아민·메틸아민군으로, pH 7–12, 산화제 과붕산염(또는 붕산염원 + H₂O₂)으로 특정한다.
특허 본문은 목표를 "Ru–Cu OCP 차를 0.3 V, 0.2 V, 0.1 V 또는 0.05 V 이하로"라고 범위로 나열한다(특허 관행상 범위이므로 대표값 아님).

(Lee et al. 2021)과 대조하면 두 전략은 상보적이다: Lee는 ΔE 0.49 → 0.09 V(−0.40 V, Cu 쪽 +0.63 V·Ru 쪽 +0.23 V), Cabot(KR101557514B1)은 Ru 쪽 −0.10 V. 두 문헌의 전해질·pH·
산화제가 달라(KIO₄+H₂O₂ pH 10 vs 과붕산염 pH 9.5) 절대 전위는 비교할 수 없고 **방향과 자릿수만** 비교 가능하다. Cabot 표 2·3의 개별 OCP 값은 텍스트
추출에서 표가 비어 **미확보**이며, "100 mV"는 본문 요약치다. 특허가 하이드록실아민을 암모니아 유도체(Ru OCP 저하제)로 청구한다는 점은 Tamilmani 2005가
하이드록실아민을 Cu 산화제로 쓴 것과 대비된다 — 같은 화학종이 Cu에서는 산화제, Ru에서는 OCP 조절제로 작동한다(두 출처의 역할 차이 지적일 뿐,
메커니즘 동일성은 **미검증**).

## 5. 억제 전략 ③ 화학으로 선택비·부식을 동시에 맞춤 — Gamagedara & Roy 2024 (Cu/Mo, 저압 0.014 MPa)

Mo는 Cu 배리어 후보(리뷰 §1)이고, Gamagedara & Roy(2024)는 약알칼리(pH 8) 시트르산 슬러리에서 Cu/Mo를 **0.014 MPa(≈2.0 psi)**로 연마하며
tribo-electrochemical 측정(폴리시 P / 정지 H 순환 중 OCP·EIS·Tafel)을 했다. 주요 결과:

- 슬러리 [0.1 M KNO₃ + 20 mM 과탄산나트륨(SPC, H₂O₂ 공급원) + 0.1 M 구연산 + 3 wt% 실리카]에서 Mo 46 nm/min, Cu 41 nm/min, 저자 표기 [Mo:Cu] 0.89.
  목표창은 1 ± 0.5 — "블랭킷으로 정한 선택비는 패턴 웨이퍼에서 압력 비균일 때문에 크게 변하므로 창을 넓게 둔다"는 이유가 명시된다.
- 구연산 슬러리에서 실리카 0 → 3 wt%로 Cu MRR 4.0배, Mo 2.4배 — 구연산 없는 슬러리에서는 Cu 2.7배. 즉 **연마재가 늘면 화학이 정한 선택비가 바뀐다**
  (Mo와 Cu의 기계 감도가 다름). 이는 [[particle-wafer-interaction-mechanical-chemical-balance]]의 화학-기계 시너지가 금속마다 다르다는 뜻.
- 메커니즘: 구연산 없는 계에서 Mo는 MoO₃·2H₂O가 제거 대상, 구연산이 있으면 Mo-구연산염(pH 2–11 안정)으로 용해가 촉진; Cu는 (CuCit₂H₋₂)⁴⁻로
  산화막이 부분 용해되어 **저압 마찰에서도 깎이는 연한 층**이 된다. 이것이 저압 CMP에서 "화학이 기계 부족을 보상"하는 구체 경로다(§6).
- 저자 표기의 내부 불일치: 46/41 = 1.12인데 [Mo:Cu] = 0.89로 적혀 있다 — 41/46 = 0.89이므로 저자가 선택비를 Cu/Mo로 정의했거나 표기가 뒤집힌 것.
  어느 쪽인지 **불명**, 노트는 두 값을 그대로 둔다(아래 verify에서 41/46 = 0.89만 확인).

```python verify
# Gamagedara & Roy 2024 Materials (doi.org/10.3390/ma17194905) 저압 조건·선택비 재현 + Han 2012 (doi.org/10.1186/1556-276X-7-603) 저압 정의
psi_kPa = 6.894757
p_gam_psi = 14.0 / psi_kPa                     # 0.014 MPa = 14 kPa → 2.03 psi
assert 1.95 < p_gam_psi < 2.10, p_gam_psi
p_lee_kPa = 1.5 * psi_kPa                      # Lee 2021 1.5 psi → 10.3 kPa
assert 10.0 < p_lee_kPa < 10.6
# Han 2012: 정상 다운포스 2-8 psi, 저압 <1 psi 또는 0.5 psi → 두 실험은 "정상 하한(2 psi)"과 "그 아래(1.5 psi)"에 해당
assert p_gam_psi >= 2.0 * 0.98 and 1.5 < 2.0
# Preston 선형이면 2 psi → 0.5 psi에서 MRR 1/4: 저압 CMP의 MRR 문제(Han 2012 §Background)의 산술
assert (0.5 / 2.0) == 0.25
# 선택비 표기 검사
mo, cu = 46.0, 41.0
assert abs(cu / mo - 0.89) < 0.005, cu / mo             # 저자 표기 0.89는 Cu/Mo와 일치
assert abs(mo / cu - 0.89) > 0.2                         # Mo/Cu(1.12)로는 불일치 — 정의 불명으로 기록
assert 0.5 <= cu / mo <= 1.5 and 0.5 <= mo / cu <= 1.5   # 어느 정의든 목표창 1 ± 0.5 안
# 연마재 효과 역산: 3 wt% 실리카에서 Cu 4.0배 → 무연마 Cu MRR
cu_free = cu / 4.0                                       # 10.25 nm/min (구연산계, 순수 화학+패드 마찰)
mo_free = mo / 2.4                                       # 19.2 nm/min
assert 10.0 < cu_free < 10.5 and 19.0 < mo_free < 19.4
print(f"Gamagedara 0.014 MPa = {p_gam_psi:.2f} psi; Lee 1.5 psi = {p_lee_kPa:.1f} kPa; Cu/Mo {cu/mo:.3f}; 무연마 Cu {cu_free:.1f}, Mo {mo_free:.1f} nm/min")
```

수계산 대조 (Gamagedara & Roy 2024; Han et al. 2012): 0.014 MPa = 2.03 psi, 1.5 psi = 10.3 kPa, 41/46 = 0.891(저자 표기 0.89와 일치), 무연마 Cu 10.25 nm/min·
Mo 19.2 nm/min(역산). 마찬가지로 기계 실행은 총괄 몫(python 미승인 세션).

## 6. 저압 Cu CMP — 왜 어렵고, 무엇이 답인가

Han et al.(2012)의 문제 정의: 정상 다운포스 2–8 psi에서 잘 되던 Cu CMP를 ULK 손상 때문에 **<1 psi, 나아가 0.5 psi**로 내려야 하는데, 기존 슬러리·패드로는
MRR이 떨어진다. 그들은 Paul의 모델 계열(2차 인용, doi.org/10.1149/1.1372222 )을 들어 "저압에서 CMP는 기계적으로 제한된다"고 정리하고, 처방을
연마재-웨이퍼 접촉 빈도·접촉 면적을 압력과 무관하게 늘리는 패드 구조(나노브러시)에서 찾는다 — 이 논문 자체는 가설 논문이라 MRR 실측이 없고, 패드 설계는
pad 에이전트 영역이므로 여기서는 동기만 취한다. [[hertz-gw-contact-mechanics]]의 GW 모델로 말하면 저압은 실접촉면적 A_r ∝ W가 그대로 줄어드는
것이고, [[preston-luo-dornfeld-mrr]]의 Preston 선형이면 2 → 0.5 psi에서 MRR은 1/4이다(verify 4).

이 노트의 다른 출처들이 보여주는 답은 **화학으로 보상**이다:
- Gamagedara & Roy 2024: 0.014 MPa(2 psi)에서 구연산이 Cu 산화막을 (CuCit₂H₋₂)⁴⁻로 부분 용해시켜 "저압 마찰로 깎이는 연한 층"을 만든다 — 무연마재
  Cu MRR ≈ 10 nm/min(역산)이 화학 기여의 하한, 실리카 3 wt%로 41 nm/min.
- Lee 2021: 1.5 psi에서 Cu 19 nm/min, Ru 5 nm/min(KIO₄+H₂O₂ pH 10). 억제제로 Cu를 Ru 수준(5 nm/min)까지 내려 1:1을 맞추는 방식 — 저압에서는
  "Cu를 빨리 깎기"가 아니라 "Ru를 Cu만큼 깎기"가 병목임을 보여준다.
- 2차 인용(원문 미확보): Pandija, Roy, Babu 2009는 저압에서 평탄화 효율을 높이는 슬러리를, Liu et al. 2011 *Thin Solid Films* 520, 400은 저압 Cu CMP의
  화학반응속도 모델을 보고한다(Han 2012 참고문헌 목록에서 확인, 수치 없음).

저압이 갈바닉 부식에 주는 효과는 이 노트 출처에서 직접 실측된 바 없다. Tamilmani 2005의 회전속도 비례성(§2 인자 3)을 유추하면 저압·저속은 재부동태
파괴 빈도를 줄여 갈바닉 전류를 낮출 것으로 기대되지만, 압력 스윕 데이터가 없어 **미검증**이다.

## 7. 근거 등급 판정(EVIDENCE-RULES 서열)과 이 단원의 결론

| 주장 | 근거 | 등급 |
|---|---|---|
| Cu/Ru ΔE_corr 0.49 V, 니코틴산 0.05 M로 0.09 V·선택비 1.05 | Lee 2021 실측(1.5 psi, n=3 CMP) | E1 |
| 갈바닉 전류는 마찰 중 250배 크고 회전속도에 비례 | Tamilmani 2005 직접 실측(Cu/Ta, 하이드록실아민·H₂O₂, pH 4/6/8) | E1(Cu/Ta) → Cu/Ru 전이는 E4 |
| 암모니아 유도체가 Ru OCP를 100 mV 낮춤 | Cabot 특허 실시예(표 수치 미확보) | E3(표 없음) |
| Mo:Cu 저압 선택비 창 1 ± 0.5, 46/41 nm/min | Gamagedara 2024 실측(2 psi) | E1(정의 불명 표기 1건) |
| 3 nm Ta/TaN이 20 nm 트렌치 단면 >30 %, 선저항 3배 | (Moon et al. 2023) 리뷰 서술 | E5(원논문 미추적, 2차 인용) — 기하 재현으로 산술만 확인(verify 1: 35.3 %) |
| 저압 <1 psi에서 MRR 기계 제한 | Han 2012 + Paul 모델(2차) | E5 |

충돌 판정 1건: Tamilmani 2005 저자의 "갈바닉은 Ta 제거율을 slightly 올릴 뿐" vs 이 노트 Faraday 환산(하이드록실아민계 45 %). 같은 데이터(E1)의 해석 차이이므로
서열로 가르지 않고 **레짐 분리**로 종결 — H₂O₂계(3–11 %)에서는 저자 서술 채택, 하이드록실아민계에서는 "무시 불가"로 기록. 평균내지 않음.

결론: 고종횡비·초박 배리어 시대의 Cu CMP는 (i) 배리어:Cu 1:1, (ii) ΔE_corr ≤ 0.1 V급 갈바닉 억제, (iii) ≤2 psi 저압을 동시에 요구하며, 세 요구를 한
화학(억제제/착화제)이 함께 푸는 것이 2021–2024 문헌의 공통 해법이다.

## 8. 한계·미확보·미검증

- Cu/Ru 갈바닉의 **마찰 중** 전류 실측은 없다(Lee 2021은 정지 Tafel/EIS만). Tamilmani의 250배·rpm 비례성이 Cu/Ru에서도 성립하는지 **미검증**.
- Cabot 특허 표 2·3(조성별 OCP 수치)·Gamagedara Fig 2의 전체 MRR 곡선 수치는 텍스트 추출 한계로 **미확보** — 본문 서술치만 사용.
- Moon 2023의 스케일링 수치는 리뷰의 2차 인용이며 원논문(선저항 3배의 출처)을 추적하지 못했다.
- Lee 2021의 I_corr 증가(0.22 → 0.47 mA/cm²)와 R_p 증가(η 88.6 %)가 상반되는 이유 **불명**.
- 저압(≤1 psi) Cu MRR 실측 데이터는 이 단원 출처에 없다(Han 2012는 가설 논문, Pandija 2009·Liu 2011은 원문 미확보). 이 세션은 네트워크 접근이 승인되지
  않아 신규 원문을 받지 못했고 로컬 코퍼스로만 구성했다 — Lv3-2에서 Pandija 2009·Liu 2011·Peethala 2011 원문 확보를 우선 과제로 남긴다.
- 구현 요청(PROFILE.md): 갈바닉 커플 모듈(ΔE_corr·면적비·마찰 재부동태 항)과 배리어 선택비 1:1 프로파일 — sim/은 이 노트에서 건드리지 않았다.
