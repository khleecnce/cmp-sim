<!-- V2-SECTION: R2-slurry | 공동: R5-wafer | 근거: cobalt, galvanic, corrosion, inhibitor, BTA, imidazole, Pourbaix, 부식 | 정본: ARCHITECTURE-V2.md §3 -->
# Co 배선 CMP — 막질(Co) 관점의 부식 민감성·갈바닉 커플·억제제 흡착 정량 (film-emerging Lv1-1)

> 에이전트: film-emerging Lv1-1 | 작성일: 2026-09-16
> 선행(반드시 먼저): [[../cmp/surface-chemistry-cu-w-pourbaix-passivation]] (부모 상속 — Nernst 기울기·Kaufman 경쟁모델·
> "자기제한적 부동태"라는 틀. 이 노트는 그 틀을 **부동태가 거의 없는 금속(Co)** 에 적용하면 무엇이 깨지는지를 다룬다),
> [[../slurry/cobalt-ruthenium-complexing-agent-oxidizer-free-chi-driver]] (형제 영역 — Co/Ru **착화제 조성 설계**.
> 조성은 그쪽 소관이라 침범하지 않고, 이 노트는 **막 표면에서 일어나는 부식·갈바닉·억제제 흡착 물리**만 다룬다)
> 관련: [[../cmp/low-level-metal-cobalt-ruthenium-cross-contamination]] (§3.1 CRC 표준전위표·§3.3 Co(OH)₂ 용해도 —
> 이 노트가 그 값을 **Pourbaix 부동태 창의 폭**이라는 다른 결론으로 쓴다),
> [[../cmp/cu-electrochemistry-pourbaix-bta-oxidizer-inhibitor]] (Cu-BTA 막 실체 — Co-BTA와의 대조군),
> [[../cmp/inhibitor-chelator-adsorption-isotherm-passivation]] (Langmuir/Frumkin 등온식·ΔG_ads 정의의 원 노트),
> [[../cmp/bta-inhibitor-langmuir-K-effective-cu-cmp-falsification]] (판정 #17 — 평형 θ를 CMP 정상상태 MRR에 직접
> 넣는 것이 Cu/BTA에서 반증됨. §6에서 **Co 계 독립 사례**로 교차확증한다),
> [[../cmp/stop-layer-chemistry-design-principles-oxide-nitride-cu-barrier-w-oxide]] (Class C 금속 배리어 설계 원칙),
> [[../cmp/oxidizer-redox-potential-decomposition-metal-suitability]] (E° 표의 원 출처·산화제 열역학),
> [[../cmp/preston-luo-dornfeld-mrr]] (기계항 — 억제제가 화학항만 죽인다는 §6의 논지가 여기에 걸린다)
>
> **스코프**: (1) Co 막이 왜 Cu/W보다 부식에 취약한가 — Pourbaix 부동태 창의 **폭**, (2) Co/Cu·Co/Ru 갈바닉 커플의
> 구동력 ΔE_corr와 갈바닉 전류밀도 i_g의 폐형식, (3) BTA·5-메틸BTA(TTA)·5-카르복시BTA·이미다졸계 억제제의 **Co 표면**
> Langmuir 흡착 정량(K_ads, ΔG°_ads, 부식전류 감소율). 슬러리 조성비·착화제 선정은 형제 노트 소관이라 제외.

## 1. 왜 이 단원이 첫 단원인가 — Co는 "무른 막을 만들어 벗기는" 게임이 성립하지 않는다

[[../cmp/surface-chemistry-cu-w-pourbaix-passivation]]의 결론은 "① 산화제가 무른 고체상을 만들고 ② 그 상이
**자기제한적 부동태**여야 하며 ③ 착화제가 적당히 재용해시킨다"였다. W의 WO₃, Cu의 Cu₂O/CuO는 이 ②를 만족한다.
**Co는 만족하지 않는다.** 아래 §2가 보이는 대로 Co의 열역학적 부동태 영역은 CMP가 쓰는 pH 창(8~10.5) 바깥에
있거나 폭이 0.7 pH 단위밖에 안 되어, "가만히 둬도 스스로 멈추는 산화막"이 사실상 없다. 그 결과 Co CMP에서
부동태는 **열역학이 아니라 억제제 분자의 흡착으로 인공 공급**되어야 하고, 이것이 Co CMP 문헌이 유독 억제제
(BTA 계열·이미다졸 계열)와 갈바닉 부식에만 집중하는 이유다.

## 2. 출처 (6건 — SCOPE `max_sources_per_unit=6` 준수, 1차 논문 5건 · 이 중 4건 원문 완독)

- **[H] L.-F. Huang, J. M. Rondinelli, "Reliable electrochemical phase diagrams of magnetic transition metals and
  related compounds from high-throughput ab initio calculations," *npj Materials Degradation* 3, 14 (2019).
  DOI: https://doi.org/10.1038/s41529-019-0088-z** — Nature CC-BY, 원문 완독
  (`papers/huang2019-npjmatdeg-pourbaix-magnetic-transition-metals.pdf`). Co–H₂O 계의 실험기반·DFT Pourbaix 도표.
  본문에서 Chivot et al. 2008(Corros. Sci. 50, 62, DOI 10.1016/j.corsci.2007.07.002 — **유료, 원문 미확보**)의
  실험 Pourbaix를 인용·재현하며 **CoO/Co(OH)₂ 상영역이 pH ∈ (10.3, 11.0)** 로 좁다고 명시.
- **[R25] K. U. Gamagedara, D. Roy, "Tribo-Electrochemical Considerations for Assessing Galvanic Corrosion
  Characteristics of Metals in Chemical Mechanical Planarization," *Electrochem* 6(2), 15 (2025).
  DOI: https://doi.org/10.3390/electrochem6020015** — MDPI CC-BY, 원문 완독
  (`papers/gamagedara2025-electrochem-cu-co-galvanic-tribo.pdf`). **Cu–Co 이금속 커플**을 대상으로 혼합전위이론
  폐형식(식 8–15)과 정지(hold)/연마(polish) 조건 PDP 실측(Table 2·3)을 함께 제공. 이 단원의 중심 문헌.
- **[R26] K. U. Gamagedara, D. Roy, "Mitigating Galvanic Corrosion of Molybdenum Diffusion Barriers in CMP of
  Copper Interconnects: A Case Study Using Imidazole in a Citrate Slurry of Neutral pH," *Electrochem* 7(1), 6 (2026).
  DOI: https://doi.org/10.3390/electrochem7010006** — MDPI CC-BY, 원문 확보
  (`papers/gamagedara2026-electrochem-mo-imidazole-galvanic.pdf`). **이미다졸**의 갈바닉 억제 사례. 단 막질이 Mo/Cu라
  Co로의 전이는 **E4(다른 막질 전이 → 방향만 채택, 크기 미채택)** 로 등급한다.
- **[C] J. Cheng, Y. Lv, F. Zhang, P. Han, Q. Miao, Z. Huang, "Understanding the adsorption mechanism of
  benzotriazole and its derivatives as effective corrosion inhibitors for cobalt in chemical mechanical polishing,"
  *Applied Surface Science* 682, 161684 (2025). DOI: https://doi.org/10.1016/j.apsusc.2024.161684** — green OA
  저자최종본 완독(`papers/cheng2024-apsusc-bta-derivatives-cobalt-cmp.pdf`, figshare 29924552). **Co 표면** BTA /
  5-메틸BTA(TTA) / 5-카르복시BTA(5CBTA)의 Langmuir 등온식·ΔG°_ads·η·EIS R_p·MRR/SER.
- **[Y] H. Yan, X. Niu, F. Luo, M. Qu, J. Wang, N. Zhan, J. Liu, Y. Zou, "Surface Corrosion Inhibition Effect and
  Action Mechanism Analysis of 5-Methyl-Benzotriazole on Cobalt-Based Copper Film CMP for GLSI," *ECS J. Solid
  State Sci. Technol.* 12, 044007 (2023). DOI: https://doi.org/10.1149/2162-8777/accd99** — 본지는 IOP Cloudflare
  봉쇄로 미확보, **CC-BY 프리프린트 전문 완독**(`papers/yan2023-ecsjss-5mbta-cobalt-copper-cmp-preprint.pdf`,
  researchsquare.com/article/rs-1909550). 표 번호는 프리프린트 기준. **Cu와 Co를 같은 슬러리에서** SCE 기준으로
  측정한 E_corr/I_corr 쌍(Table 2·4)을 제공 — 갈바닉 방향 판정의 직접 근거.
- **[Z] W. Zhang, T. Wang, S. Yu, T. Han, L. Yang, "Investigation of the behavior of benzimidazole and its
  derivatives as corrosion inhibitors for cobalt in alkaline medium," *Int. J. Electrochem. Sci.* 18, 100360 (2023).
  DOI: https://doi.org/10.1016/j.ijoes.2023.100360** — Crossref로 실존·저자 확인. ScienceDirect·Elsevier API·exa
  전 경로 차단으로 **원문 미확보 → 초록만 확인(2차 인용, 등급 E5)**. 이미다졸계의 Co 적용 사례로만 인용하며
  수치는 §5에서 "단독 채택 금지"로 표기.

**제외 기록**(못 찾은 게 아니라 상한으로 뺀 것): 로컬 코퍼스(`data/corpus/corpus.sqlite`)에 Co CMP 억제제·갈바닉
1차 논문이 40건 이상 더 있다(1,2,4-트리아졸, 올레산칼륨, TT-LYK, 아스파르트산, 글루타치온, 프탈산 등). SCOPE의
`max_sources_per_unit=6` 때문에 본문 인용에서 제외했고, 후속 단원(Lv1-2·Lv3-1)에서 다룬다.

## 3. Co의 부식 민감성 — 부동태 창이 "좁다"가 아니라 "CMP pH 밖에 있다"

### 3.1 열역학 좌표
CRC Vanýsek 전기화학표(`papers/crc-vanysek-electrochemical-series.pdf`,
[[../cmp/low-level-metal-cobalt-ruthenium-cross-contamination]] §3.1 경유 재사용)의 표준환원전위:

| 반쪽반응 | E°/V (SHE, 25 °C) |
|---|---|
| Co²⁺ + 2e⁻ → Co | **−0.28** |
| Cu²⁺ + 2e⁻ → Cu | **+0.3419** |
| Ru²⁺ + 2e⁻ → Ru | **+0.455** |

→ ΔE°(Cu−Co) = **0.622 V**, ΔE°(Ru−Co) = **0.735 V**. **두 커플 모두 Co가 양극(용해 쪽)** 이고, Ru 커플이 Cu 커플보다
0.113 V 더 가혹하다. 즉 Cu 배선의 Co 라이너보다 **Ru 배리어와 접한 Co가 열역학적으로 더 위험**하다.

### 3.2 부동태 창의 폭 — 이것이 Co의 진짜 문제다
[H]의 Co Pourbaix 절(원문 §"Co Pourbaix diagrams")은 실험 열역학 데이터 기반 도표에서 **CoO(및 Co(OH)₂)의 상영역이
pH ∈ (10.3, 11.0)** 에 불과하다고 명시한다(Co 용존종 농도 10⁻⁶ mol/kg 기준). [H] 저자들은 이 폭이 실험 관측(pH ≳ 10에서
Co/CoO/Co(OH)₂ 샌드위치 형성)보다 **과소평가**라고 비판하며 DFT 도표에서는 더 넓다고 주장하지만, 어느 쪽을 택하든
결론의 방향은 같다: **Co CMP 슬러리가 실제로 쓰는 pH(문헌 3건: [R25] 8.5, [C] 8.0, [Y] 10.0)는 모두 이 부동태 창의
아래(산성 쪽)에 있다.** 그 영역에서 Co의 열역학적 안정종은 **가용성 Co²⁺**다.

이것을 Cu와 나란히 놓으면 대비가 선명하다 — MINTEQ v4(`papers/phreeqc-minteq.v4.dat`,
[[../cmp/low-level-metal-cobalt-ruthenium-cross-contamination]] §3.3에서 판독) 기준 수산화물 석출 시작 pH는
Co가 Cu보다 **2.21 pH 단위 높다**. Cu는 pH 7.3(10⁻⁶ M 기준)부터 고체 Cu(OH)₂/CuO로 덮이기 시작하는 반면 Co는
pH 9.5까지 이온으로 남는다. **"Cu CMP의 pH 창"을 그대로 Co에 쓰면 Cu는 부동태, Co는 알몸**이다.

```python verify
import math
# ---- 1차 데이터 ----
# CRC Vanysek "Electrochemical Series" (papers/crc-vanysek-electrochemical-series.pdf),
#   [[low-level-metal-cobalt-ruthenium-cross-contamination]] §3.1 표에서 재사용
E0 = {"Co": -0.28, "Cu": 0.3419, "Ru": 0.455}   # V vs SHE, 25 C
# Huang & Rondinelli 2019, npj Mater. Degrad. 3, 14, DOI: 10.1038/s41529-019-0088-z
#   원문 "Co Pourbaix diagrams" 절: 실험 기반 도표의 CoO/Co(OH)2 상영역 = pH (10.3, 11.0), [Co]=1e-6 mol/kg
CO_PASSIVE_pH = (10.3, 11.0)
# MINTEQ v4 (papers/phreeqc-minteq.v4.dat): Co(OH)2 + 2H+ = Co2+ + 2H2O logK 13.094 / Cu(OH)2 logK 8.674
logK_CoOH2, logK_CuOH2 = 13.094, 8.674
# 이 단원에서 실제로 확인한 Co CMP 슬러리 pH (문헌 3건)
SLURRY_pH = {"Gamagedara2025": 8.5, "Cheng2024": 8.0, "Yan2023": 10.0}

# (A) 갈바닉 구동력의 열역학 상한 — Co는 Cu/Ru 둘 다에 대해 양극
dE_CuCo = E0["Cu"] - E0["Co"]
dE_RuCo = E0["Ru"] - E0["Co"]
assert abs(dE_CuCo - 0.622) < 0.001, dE_CuCo
assert abs(dE_RuCo - 0.735) < 0.001, dE_RuCo
assert dE_RuCo > dE_CuCo, "Ru 커플이 Cu 커플보다 가혹해야 함"

# (B) Co2+/Co 경계를 1e-6 M로 Nernst 보정 (수평선: H+ 불참여 -> pH 무관)
k = 0.05916
E_CoCo2 = E0["Co"] + (k / 2) * math.log10(1e-6)
assert abs(E_CoCo2 - (-0.4575)) < 0.001, E_CoCo2

# (C) 부동태 창의 폭과 위치 — 이 노트의 핵심 주장
width = CO_PASSIVE_pH[1] - CO_PASSIVE_pH[0]
assert abs(width - 0.7) < 1e-9, width
for name, ph in SLURRY_pH.items():
    assert ph < CO_PASSIVE_pH[0], f"{name} pH {ph}가 부동태 창 안에 있음 — 주장 반증"

# (D) Co vs Cu 수산화물 석출 pH 차 (C = 1e-6 M): pH* = (logK - log C)/2
def ppt_pH(logK, C): return (logK - math.log10(C)) / 2
ph_Co, ph_Cu = ppt_pH(logK_CoOH2, 1e-6), ppt_pH(logK_CuOH2, 1e-6)
assert abs((ph_Co - ph_Cu) - 2.21) < 0.01, (ph_Co, ph_Cu)
assert ph_Cu < 8.0 < ph_Co, "pH 8에서 Cu는 석출·Co는 이온이어야 논지 성립"

print(f"문헌값 대조: ΔE°(Cu−Co)={dE_CuCo:.3f} V, ΔE°(Ru−Co)={dE_RuCo:.3f} V (Co가 양극)")
print(f"문헌값 대조: Co 부동태 창 폭 {width:.1f} pH 단위(10.3~11.0, Huang2019) — "
      f"슬러리 pH {sorted(SLURRY_pH.values())} 전부 창 밖(부식 영역)")
print(f"재현: 수산화물 석출 pH Cu {ph_Cu:.2f} vs Co {ph_Co:.2f} (차이 {ph_Co-ph_Cu:.2f} pH)")
```
문헌값과 대조한 재현 결과: ΔE°(Cu−Co)=0.622 V·ΔE°(Ru−Co)=0.735 V, Co 부동태 창 폭 0.7 pH 단위(10.3~11.0),
슬러리 pH 8.0/8.5/10.0 세 건 모두 창 아래 — assert 전부 통과. **한계**: [H]의 10.3~11.0은 [H] 본문이 인용한
Chivot 2008 실험 도표 값이고 Chivot 원문(유료)은 확인 못 했다 — [H] 경유 **2차 인용**이다. [H] 자신의 DFT 도표는
이 창이 더 넓다고 주장하므로, "창의 절대 경계"는 미검증이고 **"CMP pH가 창 아래에 있다"는 방향만 확정**이다.

## 4. 갈바닉 커플 — ΔE_corr는 필요조건이지 충분조건이 아니다

### 4.1 폐형식 ([R25] 식 12–15, 혼합전위이론)
음극금속 C(=Cu), 양극금속 A(=Co)가 접촉하면 갈바닉 혼합전위 E_g에서 양극의 아노드 전류 = 음극의 캐소드 전류 = I_g:

```
갈바닉 구동전위   ΔE_corr = E_corr(C) − E_corr(A)                                   ([R25] 식 1)
갈바닉 전위       E_g = [β_c(C)·E_corr(A) + β_a(A)·E_corr(C)] / β_ca
                       + (β_a(A)β_c(C)/β_ca)·ln[ i_corr(C)·S_c / (i_corr(A)·S_a) ]  ([R25] 식 14)
갈바닉 전류밀도   i_g(A) = exp(ΔE_corr/β_ca) · [i_corr(C)·S_c/S_a]^(β_c/β_ca)
                           · [i_corr(A)]^(β_a/β_ca) ,   β_ca = β_c(C) + β_a(A)      ([R25] 식 15)
```
(β는 자연로그형 Tafel 계수 [V]; S_c·S_a는 음극·양극의 유효 노출면적.)

**[R25]가 식 15에서 강조하는 것**: ΔE_corr만 지수 안에 있고 나머지(i_corr, 면적비)는 거듭제곱이다 →
ΔE_corr가 지배인자가 되기 쉽고, 그래서 업계가 전통적으로 ΔE_corr 하나로 갈바닉을 평가해 왔다.
**그러나 §4.3이 보이듯 그 관행은 실측으로 깨진다.**

### 4.2 실측 — 억제제는 "양극(Co) 전위를 올려서" ΔE_corr를 줄인다
[R25] Table 2 (pH 8.5, 0.1 M KNO₃ + 1 wt% H₂O₂ + 3 wt% SiO₂ 기준 슬러리 I, 전위 단위 V vs SCE):

| 슬러리 | 조성 | E_corr(H;Cu) | E_corr(H;Co) | ΔE_corr(H) | ΔE_corr(P, 연마중) |
|---|---|---|---|---|---|
| I | Ref | 0.139 | −0.368 | **0.507** | 0.142 |
| II | Ref + 0.1 M 말론산(MA) | 0.035 | −0.366 | 0.401 | 0.047 |
| III | Ref + 1 mM BTA | 0.120 | −0.229 | 0.349 | 0.105 |
| IV | Ref + MA + BTA | 0.089 | 0.045 | **0.044** | 0.042 |

읽는 법 세 가지:
1. **BTA는 Co 쪽 아노드 억제제다**(I→III): Co의 E_corr이 −0.368 → −0.229 V로 **+139 mV** 올라가는 동안 Cu는
   0.139 → 0.120 V로 −19 mV밖에 안 움직인다. [R25] §2.3의 이론 예측("아노드 억제제는 θ_a를 낮춰 식 8을 통해
   그 금속의 E_corr을 올린다")과 부호·크기가 정합한다.
2. **연마(abrasion)가 ΔE_corr를 자체적으로 무너뜨린다**: 슬러리 I에서 정지 0.507 V → 연마중 0.142 V로 **−72%**.
   즉 **정지 조건 PDP로 잰 ΔE_corr는 실제 CMP 중 구동력을 3.6배 과대평가**한다. 이건 우리 모델링에 직접적이다 —
   문헌의 "정적 ΔE_corr" 수치를 그대로 CMP 시뮬레이터에 넣으면 갈바닉 결함을 과대예측한다.
3. **착화제+억제제 조합이 전위매칭을 완성**(IV): ΔE_corr 0.507 → 0.044 V(−91%). 이는
   [[../cmp/low-level-metal-cobalt-ruthenium-cross-contamination]] §3.2가 기록한 Seo 2019의 En 착화 ΔE_corr ≈40 mV
   (DOI: https://doi.org/10.1149/2.0011908jss)와 같은 자릿수로 수렴한다 — **서로 독립인 두 실험실·두 화학계**.

```python verify
# Gamagedara & Roy 2025, Electrochem 6(2) 15, DOI: 10.3390/electrochem6020015, Table 2
# 전위 단위 V vs SCE. H = stationary hold, P = dynamic polish
Ecorr = {   # slurry: (Cu_hold, Co_hold, Cu_polish, Co_polish)
    "I":   (0.139, -0.368, 0.175, 0.033),
    "II":  (0.035, -0.366, 0.161, 0.114),
    "III": (0.120, -0.229, 0.195, 0.090),
    "IV":  (0.089,  0.045, 0.186, 0.144),
}
dE_lit_H = {"I": 0.507, "II": 0.401, "III": 0.349, "IV": 0.044}   # 원문 표의 ΔEcorr(H) 열
dE_lit_P = {"I": 0.142, "II": 0.047, "III": 0.105, "IV": 0.042}   # 원문 표의 ΔEcorr(P) 열

# (A) ΔEcorr = Ecorr(Cu) - Ecorr(Co) 로 원문 표의 ΔEcorr 열을 그대로 재현하는가
for s, (cuH, coH, cuP, coP) in Ecorr.items():
    assert abs((cuH - coH) - dE_lit_H[s]) < 1e-3, (s, cuH - coH, dE_lit_H[s])
    assert abs((cuP - coP) - dE_lit_P[s]) < 1e-3, (s, cuP - coP, dE_lit_P[s])
    assert cuH > coH and cuP > coP, f"{s}: Cu가 음극·Co가 양극이어야 함"

# (B) BTA는 Co 쪽(양극) 억제제인가 — I -> III 에서 Co가 Cu보다 훨씬 크게 움직여야 한다
d_Co = (Ecorr["III"][1] - Ecorr["I"][1]) * 1000     # mV
d_Cu = (Ecorr["III"][0] - Ecorr["I"][0]) * 1000     # mV
assert abs(d_Co - 139.0) < 0.5 and abs(d_Cu - (-19.0)) < 0.5, (d_Co, d_Cu)
assert d_Co > 0 > d_Cu and abs(d_Co) > 5 * abs(d_Cu), "BTA가 아노드(Co) 선택 억제제라는 주장 반증"

# (C) 연마가 ΔEcorr를 얼마나 무너뜨리나 (정적 측정의 과대평가 배수)
ratio = dE_lit_H["I"] / dE_lit_P["I"]
assert 3.4 < ratio < 3.7, ratio
drop_pct = (1 - dE_lit_P["I"] / dE_lit_H["I"]) * 100
assert 70 < drop_pct < 75, drop_pct

# (D) 착화제+억제제 조합의 ΔEcorr 급감이 Seo 2019(En 착화, ~40 mV)와 같은 자릿수인가
seo2019_dE_mV = 40.0    # DOI: 10.1149/2.0011908jss, 노트 low-level-metal-... §3.2 경유
assert 0.5 < (dE_lit_H["IV"] * 1000) / seo2019_dE_mV < 2.0

print(f"문헌값 대조: ΔEcorr(H) 재현 {[round(Ecorr[s][0]-Ecorr[s][1],3) for s in Ecorr]} "
      f"= 원문 {list(dE_lit_H.values())}")
print(f"재현: BTA 첨가로 Co E_corr {d_Co:+.0f} mV vs Cu {d_Cu:+.0f} mV -> 아노드 선택 억제")
print(f"재현: 정지 ΔEcorr가 연마중보다 {ratio:.2f}배 큼(−{drop_pct:.0f}%) — 정적 PDP는 갈바닉을 과대평가")
print(f"재현: 슬러리 IV ΔEcorr {dE_lit_H['IV']*1000:.0f} mV ≈ Seo2019 En {seo2019_dE_mV:.0f} mV (독립 수렴)")
```
문헌값과 대조한 재현 결과: ΔE_corr(H) 4건 = 0.507/0.401/0.349/0.044 V로 원문 표와 소수 3자리까지 일치,
BTA 첨가 시 Co +139 mV·Cu −19 mV, 정적/연마중 비 3.57배(−72%), 슬러리 IV의 44 mV가 Seo 2019의 40 mV와
1.1배 이내 — assert 전부 통과.

### 4.3 ★ ΔE_corr만으로는 갈바닉 전류를 예측할 수 없다 (말론산 반례)
[R25] Table 3의 갈바닉 전류밀도 i_g(정지·순방향 1차 스캔, IR 보정 전, µA/cm²):

| 슬러리 | ΔE_corr(H) / V | i_g(H-F) / µA·cm⁻² |
|---|---|---|
| I (Ref) | 0.507 | 55.1 |
| II (+MA) | 0.401 | **62.2** ← ΔE_corr는 내려갔는데 i_g는 올라갔다 |
| III (+BTA) | 0.349 | 21.1 |
| IV (+MA+BTA) | 0.044 | 6.60 |

슬러리 I·III 두 점만으로 식 15의 지수항을 역산하면 β_ca ≈ 0.165 V가 나온다(다른 인자가 전부 불변이라는 가정 —
실제로는 i_corr·면적비 변화가 이 값에 흡수되므로 **유효 lumped 계수**다). 이 값으로 나머지 두 슬러리를 예측하면:
- 슬러리 IV: 예측 3.3 vs 실측 6.60 µA/cm² → **2.0배 과소예측**(같은 자릿수, 허용 범위)
- 슬러리 II: 예측 28.9 vs 실측 62.2 µA/cm² → **2.15배 과소예측이면서 방향이 반대** — MA는 ΔE_corr를 21% 낮추는데도
  i_g를 13% **올린다**.

**왜인가**: MA는 착화제라 Cu·Co 양쪽의 i_corr을 함께 올린다([R25] Fig. 6이 icorr 상승을 보이나 **수치표가 아니라
그래프뿐이라 정확한 i_corr 값은 판독 못 함 — 미검증**). 식 15에서 i_corr(C)·i_corr(A)는 거듭제곱으로 들어가므로,
ΔE_corr 감소의 지수 이득을 i_corr 상승의 거듭제곱 손실이 이긴 것이다. 
**모델링 함의**: 우리 시뮬레이터가 갈바닉 결함을 ΔE_corr 하나로 스칼라화하면 **착화제를 넣는 레시피에서 부호가
틀린다.** i_corr(양쪽 금속) 또는 i_g를 별도 입력으로 가져야 한다. (→ PROFILE 구현 요청)

```python verify
import math
# Gamagedara & Roy 2025, Electrochem 6(2) 15, DOI: 10.3390/electrochem6020015
#   Table 2 ΔEcorr(H) [V]  +  Table 3 ig(H-F) [µA/cm^2]  (정지·순방향 1차 스캔, IR 미보정)
dE  = {"I": 0.507, "II": 0.401, "III": 0.349, "IV": 0.044}
ig  = {"I": 55.1,  "II": 62.2,  "III": 21.1,  "IV": 6.60}

# (A) 반례 자체: MA(II)는 ΔEcorr를 낮췄는데 ig는 오히려 올렸다 -> "ΔEcorr만으로 갈바닉 판정" 반증
assert dE["II"] < dE["I"] and ig["II"] > ig["I"], "말론산 반례가 성립하지 않음"
dE_drop_pct = (1 - dE["II"] / dE["I"]) * 100
ig_rise_pct = (ig["II"] / ig["I"] - 1) * 100
assert 20 < dE_drop_pct < 22 and 12 < ig_rise_pct < 14, (dE_drop_pct, ig_rise_pct)

# (B) 식 15의 지수항만으로 I->III 을 설명한다고 가정하고 유효 β_ca 역산
#     ig = exp(ΔEcorr/β_ca) * (나머지 인자) ; 나머지 불변 가정
beta_ca = (dE["I"] - dE["III"]) / math.log(ig["I"] / ig["III"])
assert 0.16 < beta_ca < 0.17, beta_ca     # V (자연로그형). 10진 Tafel 합 ~379 mV/decade

def predict(s):  return ig["I"] * math.exp((dE[s] - dE["I"]) / beta_ca)

# (C) 순수 지수모델의 외삽 성능: IV는 2배 이내(같은 자릿수), II는 2배이면서 방향이 틀림
r_IV = ig["IV"] / predict("IV")
r_II = ig["II"] / predict("II")
assert 1.8 < r_IV < 2.3, r_IV
assert 2.0 < r_II < 2.4, r_II
# 방향 오류의 명시: 지수모델은 II가 I보다 ig가 작다고 예측하지만 실측은 반대
assert predict("II") < ig["I"] < ig["II"], "지수모델의 방향 오류를 재확인 못 함(회귀 경보)"

print(f"문헌값 대조: MA 첨가로 ΔEcorr −{dE_drop_pct:.0f}%인데 ig는 +{ig_rise_pct:.0f}% (반례 성립)")
print(f"재현: 유효 β_ca = {beta_ca:.3f} V; 지수모델 예측 IV {predict('IV'):.1f} vs 실측 {ig['IV']:.1f} "
      f"({r_IV:.1f}배 과소), II {predict('II'):.1f} vs 실측 {ig['II']:.1f} ({r_II:.2f}배 과소·방향 반대)")
```
문헌값과 대조한 재현 결과([R25] Gamagedara & Roy 2025, doi.org/10.3390/electrochem6020015 Table 2·3):
MA 첨가 시 ΔE_corr −21%인데 i_g는 +13%(반례 성립), 유효 β_ca=0.165 V,
지수모델이 슬러리 IV를 2.0배·슬러리 II를 2.15배 과소예측하며 II는 **부호까지 틀림** — assert 전부 통과.
**차이의 원인은 규명됨**(식 15의 i_corr 거듭제곱 항 누락)이나, i_corr 실측값이 [R25]에 그래프로만 있어
**정량 분해는 미검증**이다.

### 4.4 갈바닉 방향은 슬러리 화학으로 뒤집힌다 — 같은 슬러리 안의 Cu vs Co ([Y])
[Y] Table 2·4는 **동일 슬러리(0.5 wt% SiO₂ + 0.7 wt% H₂O₂ + 2.5 wt% 글리신 + JFCE, pH 10, SCE 기준)** 에서
Cu와 Co를 각각 측정했다:

| TTA / ppm | E_corr(Cu) / V | E_corr(Co) / V | ΔE_corr = Cu − Co / mV | I_corr(Co) / A·cm⁻² | Co 억제효율 η |
|---|---|---|---|---|---|
| 0 | 0.053 | 0.057 | **−4** | 1.065×10⁻³ | — |
| 400 | 0.058 | 0.091 | **−33** | 2.291×10⁻⁴ | 78.5 % |

표준전위는 Co가 Cu보다 622 mV 비(卑)하다고 말하는데, **실측 혼합전위에서는 Co가 Cu보다 4 mV 귀(貴)하고,
TTA를 넣으면 33 mV까지 더 귀해진다.** 이유는 2.5 wt%(=333 mM) 글리신이 Cu²⁺를 강하게 착화해 Cu의 혼합전위를
끌어내리는 동시에, TTA가 Co 표면에 Co-TTA 막을 만들어 Co의 아노드 반응을 죽이기 때문이다([Y] §3.3.3 XPS:
TTA 첨가 시 표면 금속 Co 비율 10.96% → 1.58%, Co₃O₄ 우세). 즉 **"Co는 항상 양극"은 열역학 명제이지 공정 명제가 아니다.**

**[[../EVIDENCE-RULES]] 서열에 따른 판정**: [R25](Cu 음극·Co 양극, ΔE_corr +507 mV)와 [Y](Co가 4 mV 귀함)는
표면적으로 충돌한다. 두 근거 모두 **E1(대상 계 직접 실측)** 이므로 등급으로 안 갈린다. §판정절차 ③(교란 통제)과
③'(스코프 분할)을 적용하면: [R25]는 착화제 없는 기준 슬러리(KNO₃)를 포함해 첨가제를 하나씩 켜는 통제 설계,
[Y]는 처음부터 고농도 글리신이 들어간 실제 레시피다. **평균내지 않는다 — 레짐이 다르다**:
> **착화제가 음극금속(Cu)을 선택적으로 착화하는 레짐에서는 갈바닉 부호가 뒤집힐 수 있다.**
[R25] 자신도 슬러리 II→IV에서 MA가 Cu의 E_corr을 104 mV 끌어내리는 것을 보이므로(0.139→0.035 V), 두 문헌은
**같은 메커니즘의 강도 차이**일 뿐 모순이 아니다.

```python verify
# Yan et al. 2023, ECS JSST 12, 044007, DOI: 10.1149/2162-8777/accd99 (프리프린트 Table 2·4)
#   동일 슬러리: 0.5 wt% SiO2 + 0.7 wt% H2O2 + 2.5 wt% glycine + JFCE, pH 10, 기준전극 SCE
Cu = {0: (0.053, 8.345e-4), 100: (0.056, 3.872e-4), 300: (0.057, 2.883e-4),
      400: (0.058, 2.763e-4), 500: (0.063, 2.309e-4)}      # ppm TTA -> (Ecorr V, Icorr A/cm2)
Co = {0: (0.057, 1.065e-3), 100: (0.066, 3.660e-4), 300: (0.062, 2.645e-4),
      400: (0.091, 2.291e-4), 500: (0.066, 2.714e-4)}
eta_Co_lit = {100: 65.6, 300: 75.2, 400: 78.5, 500: 74.5}   # 원문 Table 4 억제효율(%) 열

# (A) 원문 억제효율 열을 eta = 1 - Icorr/Icorr0 로 재현
for c, lit in eta_Co_lit.items():
    eta = (1 - Co[c][1] / Co[0][1]) * 100
    assert abs(eta - lit) < 0.1, (c, eta, lit)

# (B) 갈바닉 부호 역전: 표준전위는 Co가 622 mV 비(卑)한데 실측 혼합전위는 Co가 더 귀(貴)
dE0_CuCo_mV = (0.3419 - (-0.28)) * 1000       # CRC E°, +622 mV
dE_meas_0   = (Cu[0][0] - Co[0][0]) * 1000    # 측정 ΔEcorr (Cu - Co)
dE_meas_400 = (Cu[400][0] - Co[400][0]) * 1000
assert abs(dE_meas_0 - (-4.0)) < 0.5 and abs(dE_meas_400 - (-33.0)) < 0.5, (dE_meas_0, dE_meas_400)
assert dE0_CuCo_mV > 0 > dE_meas_0 > dE_meas_400, "부호 역전 주장 반증"
assert abs(dE_meas_0) < 0.01 * dE0_CuCo_mV, "실측 ΔEcorr가 표준전위차의 1% 미만이어야 함"

# (C) TTA는 Co와 Cu 둘 다 억제하되 Co 쪽이 더 강하다 (그래서 부호가 더 벌어진다)
eta_Cu_400 = (1 - Cu[400][1] / Cu[0][1]) * 100
eta_Co_400 = (1 - Co[400][1] / Co[0][1]) * 100
assert eta_Co_400 > eta_Cu_400, (eta_Co_400, eta_Cu_400)

print(f"문헌값 대조: Co 억제효율 재현 {[round((1-Co[c][1]/Co[0][1])*100,1) for c in eta_Co_lit]} "
      f"= 원문 {list(eta_Co_lit.values())} (%)")
print(f"재현: ΔE° = +{dE0_CuCo_mV:.0f} mV(Co 양극) 이지만 실측 ΔEcorr = {dE_meas_0:+.0f} mV(0 ppm) / "
      f"{dE_meas_400:+.0f} mV(400 ppm) — 부호 역전, 표준전위차의 {abs(dE_meas_0)/dE0_CuCo_mV*100:.1f}%")
print(f"재현: 400 ppm TTA 억제효율 Co {eta_Co_400:.1f}% > Cu {eta_Cu_400:.1f}%")
```
문헌값과 대조한 재현 결과: [Y] Table 4의 억제효율 열 65.6/75.2/78.5/74.5%를 I_corr에서 소수 첫째자리까지 재현,
측정 ΔE_corr = −4 mV(0 ppm)·−33 mV(400 ppm)로 표준전위차 622 mV의 0.6% 수준이며 **부호가 반대** — assert 전부 통과.

### 4.5 Co/Ru 커플 — 확보 못 한 것 (정직 표기)
이 단원의 목표 중 하나였던 **Co/Ru 커플의 실측 ΔE_corr**는 **확보하지 못했다**("못 찾았다"이지 "범위 밖"이 아니다).
확인한 사실만 적으면:
- 열역학 구동력은 §3.1대로 ΔE°(Ru−Co) = 0.735 V로 Cu 커플(0.622 V)보다 크다.
- 실측이 존재하는 것은 **Cu/Ru** 커플이다: Lee et al. 2021(Sci. Rep. 11, DOI: https://doi.org/10.1038/s41598-021-00689-6,
  PMC8551296) 0.05 M KIO₄+3% H₂O₂ pH 10에서 ΔE_oc 0.49 V → 니코틴산 첨가로 0.09 V
  ([[../cmp/low-level-metal-cobalt-ruthenium-cross-contamination]] §3.2에 기록됨, 이 노트가 재측정한 것 아님).
- Co와 Ru이 **같은 슬러리에서 동시에 측정된 1차 논문**은 이번 조사 범위(코퍼스 8960건 + 웹)에서 찾지 못했다.
따라서 Co/Ru 갈바닉의 **크기는 미검증**이며, §3.1의 ΔE° 0.735 V는 **열역학 상한이지 공정 예측값이 아니다**
(§4.4가 보인 대로 실측 ΔE_corr는 ΔE°의 1% 수준까지 떨어질 수 있다).

## 5. 억제제의 Co 표면 흡착 정량 — Langmuir K_ads·ΔG°_ads·부식전류 감소율

### 5.1 [C]의 Co 실측 (pH 8, 0.5 wt% H₂O₂ + 0.15 wt% 글리신, 3 wt% SiO₂)
억제효율 η = (I_corr,0 − I_corr)/I_corr,0 ([C] 식 11), 원문 Table 2:

| c / mM | 5CBTA η(%) | BTA η(%) | TTA η(%) |
|---|---|---|---|
| 3 | 54.12 | 53.88 | 68.18 |
| 6 | 68.34 | 69.65 | 87.62 |
| 9 | 73.11 | 73.22 | **91.71** |

기준 부식전류밀도 I_corr,0 = **334.25 µA/cm²**, 9 mM TTA에서 **27.70 µA/cm²**([C] 본문) → **12.1배 감소**.
Langmuir 등온식 c/θ = c + 1/K_ads ([C] 식 13)와 ΔG°_ads = −RT·ln(55.5·K_ads) ([C] 식 14)를 θ=η/100으로 풀면:

| 억제제 | K_ads / M⁻¹ (재현) | ΔG°_ads / kJ·mol⁻¹ (재현) | [C] 보고값 |
|---|---|---|---|
| 5CBTA | 474 | **−25.21** | −25.21 ✔ |
| BTA | 476 | **−25.23** | −25.23 ✔ |
| TTA | 622 | **−25.89** | −28.89 ✘ (3.00 kJ/mol 차이) |

세 값 모두 −20 ~ −40 kJ/mol 구간이므로 [C]의 해석대로 **물리흡착·화학흡착 공존**이다. 흡착세기 순서
TTA > BTA ≈ 5CBTA는 [C]의 DFT/MD 결론(메틸기가 벤젠고리 전자밀도를 올려 Co 표면 전하이동을 키움)과 일치한다.

**불일치 처리(정직)**: TTA의 ΔG°_ads가 [C] 본문 −28.89 kJ/mol과 우리 재현 −25.89 kJ/mol 사이에서 **3.00 kJ/mol
(10.4%)** 어긋난다. 같은 코드가 5CBTA·BTA는 소수 둘째자리까지 맞히므로 **방법이 아니라 그 한 값이 문제**이며,
차이가 정확히 3.00이고 앞자리 숫자만 다른 점(25.89 ↔ 28.89)에서 **원문 오탈자로 의심**하지만 저자에게 확인할 수
없으므로 **원인 미상·미검증**으로 남긴다. 순위(TTA가 가장 강함)는 어느 값을 써도 바뀌지 않는다.

```python verify
import numpy as np
# Cheng, Lv, Zhang, Han, Miao, Huang (2025), Appl. Surf. Sci. 682, 161684,
#   DOI: 10.1016/j.apsusc.2024.161684 — Table 2(억제효율), 본문(Icorr), 식 11·13·14
R, T = 8.314, 298.0            # 원문 식 14가 명시한 상수
C_SOLVENT = 55.5               # mol/L, 원문 식 14
conc_mM = np.array([3.0, 6.0, 9.0])
eta_pct = {"5CBTA": [54.12, 68.34, 73.11], "BTA": [53.88, 69.65, 73.22],
           "TTA":   [68.18, 87.62, 91.71]}
dG_lit = {"5CBTA": -25.21, "BTA": -25.23, "TTA": -28.89}    # 원문 본문 보고값
Icorr0, Icorr_TTA9 = 334.25, 27.70                          # µA/cm2, 원문 본문

def langmuir(c_mM, theta):
    """c/θ = c + 1/K_ads 를 최소자승으로 풀어 (K_ads[M^-1], ΔG°_ads[kJ/mol], 기울기) 반환"""
    y = c_mM / theta
    slope, intercept = np.polyfit(c_mM, y, 1)
    K_M = 1.0 / intercept * 1000.0          # mM^-1 -> M^-1
    return K_M, -R * T * np.log(C_SOLVENT * K_M) / 1000.0, slope

res = {}
for name, e in eta_pct.items():
    K, dG, slope = langmuir(conc_mM, np.array(e) / 100.0)
    res[name] = (K, dG, slope)
    assert 0.85 < slope < 1.15, f"{name}: Langmuir 기울기가 1에서 크게 벗어남 {slope:.3f}"

# (A) 5CBTA·BTA 는 원문 보고값을 0.02 kJ/mol 이내로 재현해야 한다 (방법 검증)
for name in ("5CBTA", "BTA"):
    assert abs(res[name][1] - dG_lit[name]) < 0.02, (name, res[name][1], dG_lit[name])

# (B) TTA 만 어긋난다 — 어긋나는 대로 assert 해서 회귀 경보로 남긴다
gap = abs(res["TTA"][1] - dG_lit["TTA"])
assert 2.9 < gap < 3.1, f"TTA 불일치 크기가 3.00 kJ/mol이 아님: {gap:.2f} (원문 재확인 필요)"
assert abs(res["TTA"][1] - (-25.89)) < 0.02, res["TTA"][1]

# (C) 흡착세기 순서 TTA > BTA ~ 5CBTA (보고값·재현값 어느 쪽으로 봐도 동일)
assert res["TTA"][0] > res["BTA"][0] > res["5CBTA"][0]
assert res["TTA"][1] < res["BTA"][1] < res["5CBTA"][1]     # 더 음수 = 더 강함

# (D) 모두 물리+화학 흡착 공존 구간(-40 ~ -20 kJ/mol) — 원문 해석의 근거
for name, (K, dG, _) in res.items():
    assert -40.0 < dG < -20.0, (name, dG)

# (E) 9 mM TTA 억제효율을 Icorr 원시값에서 재현
eta_TTA9 = (Icorr0 - Icorr_TTA9) / Icorr0 * 100
assert abs(eta_TTA9 - 91.71) < 0.01, eta_TTA9
assert 12.0 < Icorr0 / Icorr_TTA9 < 12.1

print("문헌값 대조: " + ", ".join(
    f"{n} K={res[n][0]:.0f} M^-1, ΔG={res[n][1]:.2f} kJ/mol (원문 {dG_lit[n]})" for n in res))
print(f"재현: 9 mM TTA η = {eta_TTA9:.2f}% (원문 91.71%), Icorr {Icorr0:.2f} -> {Icorr_TTA9:.2f} µA/cm2 "
      f"= {Icorr0/Icorr_TTA9:.1f}배 감소")
print(f"불일치(정직): TTA ΔG 재현 {res['TTA'][1]:.2f} vs 원문 {dG_lit['TTA']:.2f} kJ/mol — "
      f"{gap:.2f} kJ/mol 차, 원인 미상(오탈자 의심)")
```
문헌값과 대조한 재현 결과: 5CBTA −25.21·BTA −25.23 kJ/mol로 원문과 0.02 kJ/mol 이내 일치, 9 mM TTA η=91.71%와
I_corr 334.25→27.70 µA/cm²(12.1배 감소) 재현, TTA ΔG만 3.00 kJ/mol 불일치(원인 미상) — assert 전부 통과.

### 5.2 두 측정법(PDP vs EIS)이 같은 답을 주지 않는다
[C] Table 3의 EIS 분극저항 R_p(Ω·cm²)는 기준 33.80 → 9 mM TTA에서 1114.01로 **33.0배** 커진다. 그런데 같은 조건의
I_corr는 12.1배밖에 안 줄었다. Stern–Geary 관계(i_corr = B/R_p)에서 **B(Tafel 계수 조합)가 일정하다면 두 배수는
같아야 한다.** 2.7배 차이는 억제제가 **Tafel 기울기 자체를 바꾼다**는 뜻이다 — 즉 Co-BTA 막은 단순히 반응 면적을
가리는 기하학적 차단(geometric blocking)이 아니라 **반응 메커니즘(전하이동 계수)** 을 바꾼다.

**모델링 함의**: 억제제 항을 "유효 면적 (1−θ)"로만 넣으면 이 2.7배를 놓친다. 억제효율을 어느 측정법에서 뽑았는지
(PDP인지 EIS인지) 문헌마다 확인해야 하며, 두 값을 섞어 쓰면 안 된다.

```python verify
# Cheng 2025, Appl. Surf. Sci. 682, 161684, DOI: 10.1016/j.apsusc.2024.161684
#   Table 3 (EIS 피팅 Rp, Ω·cm2) + 본문 (PDP Icorr, µA/cm2), 동일 조건 pH 8 / 9 mM TTA
Rp_ref, Rp_TTA9 = 33.80, 1114.01
Icorr_ref, Icorr_TTA9 = 334.25, 27.70

fold_Rp    = Rp_TTA9 / Rp_ref            # EIS 기준 개선 배수
fold_Icorr = Icorr_ref / Icorr_TTA9      # PDP 기준 개선 배수
eta_Rp     = (1 - Rp_ref / Rp_TTA9) * 100
eta_Icorr  = (1 - Icorr_TTA9 / Icorr_ref) * 100

assert 32.9 < fold_Rp < 33.1, fold_Rp
assert 12.0 < fold_Icorr < 12.1, fold_Icorr
# Stern-Geary 에서 B 불변이면 두 배수가 같아야 한다 -> 실제로는 2.7배 어긋난다
mismatch = fold_Rp / fold_Icorr
assert 2.6 < mismatch < 2.8, mismatch
# 억제효율로 환산하면 차이는 5.3 %p 로 작아 보이지만(비선형), 배수로는 2.7배다
assert abs((eta_Rp - eta_Icorr) - 5.25) < 0.2, (eta_Rp, eta_Icorr)

print(f"문헌값 대조: EIS Rp {Rp_ref:.2f} -> {Rp_TTA9:.2f} Ω·cm2 ({fold_Rp:.1f}배) vs "
      f"PDP Icorr {Icorr_ref:.2f} -> {Icorr_TTA9:.2f} µA/cm2 ({fold_Icorr:.1f}배)")
print(f"재현: Stern-Geary B 불변 가정의 어긋남 = {mismatch:.2f}배 "
      f"(η로는 {eta_Rp:.1f}% vs {eta_Icorr:.1f}%, 차 {eta_Rp-eta_Icorr:.1f} %p) — B가 일정하지 않다")
```
문헌값과 대조한 재현 결과: EIS R_p 33.0배 개선 vs PDP I_corr 12.1배 개선 → Stern–Geary B 불변 가정이 2.7배
어긋남(억제효율로는 96.97% vs 91.71%, 5.3 %p 차) — assert 전부 통과. **원인은 Tafel 계수 변화로 추정**하나
[C]가 Tafel 기울기 표를 주지 않아 **직접 검증은 못 했다(미검증)**.

### 5.3 이미다졸 계열 (E4/E5 — 방향만 채택)
- **[R26]**(pH 중성 시트르산 슬러리, Mo/Cu 커플): 이미다졸 첨가가 갈바닉 전류를 뚜렷이 줄인다고 보고. 단
  **막질이 Mo이고 Co가 아니다** → [[../EVIDENCE-RULES]] 서열 **E4(다른 막질 전이)**, 방향만 채택하고 크기는
  이 노트에 반영하지 않는다. 같은 저자·같은 측정체계라 §4.1 폐형식의 이식성 근거로만 쓴다.
- **[Z]**(벤즈이미다졸·2-히드록시·2-아미노벤즈이미다졸, 알칼리 Co): 초록에 따르면 5 mM 이상에서 억제효율 >90%,
  10 mM이 최적(Co 제거율 100–300 Å/min 유지), Langmuir 등온식 추종, 효율 순서 2-아미노 > 2-히드록시 > 벤즈이미다졸.
  **원문 미확보 → 전부 2차 인용(E5), 단독 채택 금지.** 다만 "이미다졸 고리도 Co에서 Langmuir를 따른다"는 점은
  §5.1의 트리아졸 결과와 같은 방향이다.

## 6. Co 계에서도 "평형 θ ≠ 정상상태 MRR" — 판정 #17의 독립 교차확증

[[../cmp/bta-inhibitor-langmuir-K-effective-cu-cmp-falsification]](판정 #17)과
[[../cmp/psi-inhibitor-isotherm-functional-form-survey.md]](판정 #24)는 **Cu/BTA·W/피콜린산** 계에서 평형 Langmuir θ를
`잔여율 = exp(−k·θ)`로 MRR에 직접 넣는 구조가 관측을 못 담는다고 판정했다. [C]는 **Co라는 세 번째 막질**에서 같은
현상을 보여준다:

9 mM TTA에서 θ = 0.9171(부식전류의 91.7%가 죽었다)인데, **같은 조건의 Co MRR은 132.64 nm/min으로 살아 있다**
([C] 본문, Co 벌크 연마 요구사항 ≥100 nm/min을 충족). 정적식각률 SER은 0.79 nm/min까지 떨어졌다. 즉:
- **화학 경로(SER)는 θ를 거의 그대로 따라간다** — 부동태막이 정적 용해를 막는다.
- **기계 경로(MRR)는 θ에 거의 반응하지 않는다** — 패드·입자가 막을 계속 벗기므로 정상상태 피복률은 평형 θ보다
  훨씬 낮고, [[../cmp/preston-luo-dornfeld-mrr]]의 기계항이 그대로 살아남는다.
MRR/SER = 168배라는 이 격차가 Co CMP 레시피가 성립하는 이유 자체다(연마 중에만 깎이고 정지 중엔 안 깎임).

**정직 표기**: [C]는 MRR·SER을 **그림으로만** 주고 수치표가 없어 9 mM TTA 한 점(132.64 / 0.79 nm/min)만 본문에서
읽을 수 있었다. 기준(억제제 0 mM) MRR 값이 없어 **"MRR이 θ에 얼마나 둔감한가"의 기울기는 정량화 못 했다 —
비율 168배와 "MRR이 요구사항 이상으로 살아남는다"는 사실만 검증된다.**

```python verify
# Cheng 2025, Appl. Surf. Sci. 682, 161684, DOI: 10.1016/j.apsusc.2024.161684 (본문 §3.5)
#   9 mM TTA, pH 8, 3 wt% SiO2 + 0.5 wt% H2O2 + 0.15 wt% glycine
theta_9mM = 0.9171          # = η/100, Table 2
MRR_9mM   = 132.64          # nm/min
SER_9mM   = 0.79            # nm/min
MRR_REQ, SER_REQ = 100.0, 1.0   # 원문이 명시한 Co 벌크 연마 요구사항

# (A) 화학은 죽었는데 기계는 살아있다 — 평형 θ를 MRR에 직접 넣으면 안 되는 이유
assert theta_9mM > 0.9,  "피복률 주장 반증"
assert MRR_9mM >= MRR_REQ, "θ=0.92인데 MRR이 요구사항 미달이면 이 논지가 깨진다"
assert SER_9mM <  SER_REQ, SER_9mM
ratio = MRR_9mM / SER_9mM
assert 165 < ratio < 172, ratio

# (B) 만약 exp(-k*θ) 구조가 MRR에 그대로 성립한다면, θ=0.917에서 남을 수 있는 잔여율의 상한 검사.
#     판정 #17의 Cu/BTA 계에서 쓰인 강도 k=3 수준이면 MRR은 6.4%만 남아야 한다.
import math
k_cu_scale = 3.0            # [[bta-inhibitor-langmuir-K-effective-cu-cmp-falsification]] 계열의 k 오더
residual_pred = math.exp(-k_cu_scale * theta_9mM)
assert residual_pred < 0.07, residual_pred
# 실제로는 MRR이 요구사항(100 nm/min) 위에 남았다 -> 같은 구조를 Co에 쓰면 MRR을 크게 과소예측
assert MRR_9mM / MRR_REQ > 1.0

print(f"문헌값 대조: θ={theta_9mM:.3f}에서 MRR {MRR_9mM:.2f} nm/min(요구 ≥{MRR_REQ:.0f}) · "
      f"SER {SER_9mM:.2f} nm/min(요구 <{SER_REQ:.0f}) — MRR/SER = {ratio:.0f}배")
print(f"재현: exp(-kθ) (k~{k_cu_scale:.0f}) 구조라면 잔여율 {residual_pred*100:.1f}%만 남아야 하는데 "
      f"실측 MRR은 요구사항 위 — 판정 #17의 구조적 반증이 Co 계에서도 재현됨")
```
문헌값과 대조한 재현 결과: θ=0.917에서 MRR 132.64 nm/min(요구 ≥100 충족)·SER 0.79 nm/min(요구 <1 충족),
MRR/SER = 168배이며, `exp(−kθ)` 구조(k≈3)가 예측하는 잔여율 6.4%와 정면으로 어긋남 — assert 전부 통과.
**단, k≈3은 Cu 계 노트의 오더를 빌린 값이지 Co 계 피팅값이 아니다 → 이 대조는 "구조가 안 맞는다"는 방향만
말하고 정확한 배수는 미검증이다.**

## 7. 이 에이전트의 결론 (모델링 관점)

1. **Co의 부동태는 열역학이 아니라 억제제가 공급한다**. 파라미터 팩에 Co를 넣을 때 W/Cu처럼 "pH가 부동태 상을
   정한다"는 구조를 그대로 쓰면 안 된다 — Co CMP pH(8~10)는 Pourbaix 부식 영역이고, 부동태는 억제제 농도의
   함수다. → **Co 팩의 χ(화학) 항은 `inhibitor_conc` 없이는 정의되지 않는다.**
2. **갈바닉은 스칼라 ΔE_corr로 요약할 수 없다**(§4.3의 말론산 반례). 착화제를 켜는 순간 ΔE_corr와 i_g가 반대로
   움직인다. 최소한 (ΔE_corr, i_corr(음극), i_corr(양극), S_c/S_a) 4개 입력이 필요하다.
3. **정적 PDP 수치를 그대로 쓰면 갈바닉을 3.6배 과대예측한다**(§4.2). 문헌 ΔE_corr를 인용할 때 hold인지 polish인지
   반드시 확인하고, polish 값이 없으면 hold 값에 축소계수를 명시적으로 넣어야 한다.
4. **억제제 항은 화학 경로(SER)와 기계 경로(MRR)에 다르게 걸린다**(§6). Co에서 θ=0.92가 SER은 0.79 nm/min까지
   죽이지만 MRR은 132 nm/min으로 살린다. 판정 #17/#24의 결론이 세 번째 막질에서 재확인됐다.
5. **Co/Ru은 열역학적으로 Co/Cu보다 가혹한데(ΔE° 0.735 vs 0.622 V) 실측이 없다**(§4.5). Lv1-2(Ru·Mo CMP)에서
   최우선으로 채워야 할 빈칸이다.

## 8. 한계·미검증 (정직 표기)

- **Co Pourbaix 경계의 절대 좌표는 미검증**. §3.2의 pH (10.3, 11.0)은 [H] 본문이 Chivot 2008(유료, 미확보)을 인용한
  **2차 인용**이고, [H] 자신은 그 값이 과소평가라고 반박한다. 확정된 것은 **"CMP pH가 부동태 창 아래에 있다"는
  방향**뿐이다.
- **[R25]의 i_corr 절대값을 못 읽었다**(Fig. 6 그래프만, 수치표 없음). §4.3의 "MA가 i_corr을 올려서 i_g가 올라간다"는
  메커니즘 설명은 **정성적 근거만** 있고 정량 분해는 미검증이다. 역산한 β_ca = 0.165 V는 다른 인자를 전부 흡수한
  **lumped 유효값**이지 Tafel 계수 실측값이 아니다.
- **[C]의 TTA ΔG°_ads 3.00 kJ/mol 불일치는 원인 미상**(§5.1). 오탈자로 의심하지만 확인 못 했다.
- **[C]의 MRR/SER은 그림뿐**이라 억제제 농도-MRR 곡선을 얻지 못했다(§6). θ→MRR 감쇠의 **함수형은 미검증**.
- **§5.2의 Stern–Geary 2.7배 어긋남의 원인(Tafel 기울기 변화)은 추정**이다 — [C]가 β_a·β_c 표를 주지 않았다.
- **[Z](이미다졸계-Co)는 초록만 확인**했다(ScienceDirect·Elsevier API·exa 전 경로 차단). E5 단독 채택 금지.
- **[R26](이미다졸)은 막질이 Mo/Cu**라 Co로의 크기 전이는 하지 않았다(E4).
- 인용 6건 중 Co 실측은 [C]·[Y]·[R25] 3건이고 서로 슬러리 화학(글리신 농도 0.15 vs 2.5 wt%, pH 8 vs 8.5 vs 10)이
  달라 **절대 수치의 계간 비교는 성립하지 않는다** — 이 노트는 각 계 내부의 비·배수만 주장한다.

## 9. 자기시험
→ [[../../agents/film-emerging/EXAMS.md]] Lv1-1 문항 참조.
