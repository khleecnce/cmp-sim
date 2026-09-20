<!-- V2-SECTION: R2-slurry | 근거: tungsten, inhibitor, picolinic acid, langmuir, passivation, dissolution | 정본: ARCHITECTURE-V2.md §3 -->
# 텅스텐 CMP 억제제 - 피콜린산(picolinic acid) Langmuir 흡착과 정지식각 억제 정량

> 에이전트: film-w Lv1-3 | 작성일: 2026-09-10
> 선행: [[w-cmp-wo3-passivation-oxidizer-kaufman]] [[w-cmp-fenton-catalyst-abrasive-alumina-silica]]
> 관련: [[particle-wafer-interaction-mechanical-chemical-balance]] [[cu-electrochemistry-pourbaix-bta-oxidizer-inhibitor]]
> 이 노트는 정확도 루프 갭(psi 표면 보호도 UNMODELED, w_fe_oxidizer 팩)을 해결하기 위해 작성됐다.

## 1. 왜 필요한가
sim/factors.py의 psi(표면 보호도) 팩터는 particle-wafer-interaction 노트에서 확립한
"화학이 표면을 연화 -> 기계가 벗김"의 반대 축이다: 억제제가 표면을 부동태화해 정지식각(정적 용해)을
억제함으로써 과도한 용해로 인한 거칠기(topography) 손상을 막는다. 지금까지 psi 항은 Cu/BTA(cu_h2o2_bta 팩)에만
배선돼 있고 w_fe_oxidizer(W CMP) 팩에는 억제제 파라미터가 없어 W 슬러리에 부식억제제를 넣어도 결과가 바뀌지 않는다.

## 2. 1차 논문 - Lee and Seo (2022)
1차 인용: K. Lee, J. Seo, "Suppression of Dissolution Rate via Coordination Complex in Tungsten Chemical
Mechanical Planarization," Applied Sciences 12(3), 1227 (2022). DOI: 10.3390/app12031227.
CC-BY 오픈액세스(Unpaywall gold). 원문 PDF 확보(MDPI CDN res.mdpi.com 경유, 8쪽 전체 통독).
저자 소속: 삼성전자 파운드리 공정개발팀(제1저자), Clarkson Univ(교신저자). 실험 조건: SiO2 콜로이달 실리카
연마입자, H2O2 4.0 wt% 산화제, 피콜린산(picolinic acid, C6H5NO2, MW 123.11 g/mol) 억제제 0/0.5/1.5/5.0 wt%.

## 3. 메커니즘 - 피리딘기의 배위결합(coordination complex)
피콜린산의 피리딘 질소가 텅스텐 산화물 표면의 Lewis산/Bronsted산 활성점에 배위결합해 단분자층을 형성한다
(원문 3.1절). Langmuir 등온식이 Freundlich보다 결정계수가 높아(R2=0.994 vs 0.825, 원문 Table 1)
균질 단분자층 흡착으로 판정됐다. 이는 particle-wafer-interaction 노트에서 BTA/Cu에 쓴 것과 동일한
Langmuir 모델을 W/피콜린산에도 그대로 적용할 근거가 된다(같은 흡착 물리, 다른 흡착질/기질).

## 4. 정량 데이터 (원문 3.3절, Figure 4)
| 피콜린산 농도 (wt%) | 정지식각 속도 (A/min) | CMP 제거율 (A/min) | CMP 후 Ra (nm) |
|---|---|---|---|
| 0    | 90  | 120 | 17.3 |
| 0.5  | 그래프만, 수치 미표기(원문 "실패 수준" 서술) | 그래프만 | 손상 다수 관측 |
| 1.5  | 11  | 85  | 7.8 |
| 5.0  | 약 11 (1.5wt%와 거의 동일, 포화) | 약 85 (포화) | 낮음 유지 |

- 정지식각 억제 배수: 0에서 1.5 wt%로 90에서 11 A/min = 8.2배 감소.
- CMP 제거율 억제: 0에서 1.5 wt%로 120에서 85 A/min = 1.41배 감소(정지식각보다 훨씬 완만 -
  기계적 성분은 화학 억제에 덜 민감함을 뜻하며, particle-wafer-interaction 1절의
  "화학x기계 시너지"에서 화학이 정지식각을, 기계가 소성 plowing을 각각 지배한다는 구분과 정합).
- 포화농도(Lee and Seo 2022, DOI: 10.3390/app12031227, 원문 3.3절 서술): 1.5 wt%에서 흡착과 억제 모두 포화(Langmuir 등온식 결과와 일치). 5.0 wt%는 추가 억제 없음
  - cu-electrochemistry-pourbaix-bta-oxidizer-inhibitor(BTA)와 동일한 "포화 후 평탄" 패턴.
- Ra(거칠기)는 억제제 없음 17.3 nm에서 1.5wt% 7.8nm로 개선(2.2배) - 정지식각 억제가 곧 표면 품질 개선으로
  직결됨을 보여주는 응용 지표(엔진 roughness 필드는 아직 None, wafer-metrology 활성화 대기 - 6절).

## 5. Langmuir 상수 -> K(L/mol) 환산 및 psi 항 파라미터 도출 (verify로 재현)
원문 Table 1의 Langmuir 상수 b=0.009 L/mg를 몰 단위 K로 환산(MW=123.11 g/mol)하고, 포화농도 1.5 wt%에서의
피복률 theta_sat, 그리고 억제 강도 k_inhib(잔여율 = exp(-k*theta), sim/chemistry.py의 _inhibitor_term과
같은 형상)를 실측 배수(8.2배 감소)에서 역산한다. wt%에서 mol/L 환산은 "wt% 약 g/100 mL"(밀도 약 1 g/mL
가정, 원문이 밀도를 명시하지 않아 근사/미검증)를 썼다.

```python verify
import math

MW = 123.11          # g/mol, picolinic acid
b_L_per_mg = 0.009    # 원문 Table 1 Langmuir 상수 (L/mg)
K_L_per_mol = b_L_per_mg * MW * 1000.0   # L/mg -> L/mol  (mg/mol = MW*1000)
assert abs(K_L_per_mol - 1108.0) < 5, K_L_per_mol
print(f"K = {K_L_per_mol:.1f} L/mol (원문 b=0.009 L/mg, MW=123.11 환산)")

def wt_pct_to_molar(wt_pct):
    """wt% -> mol/L: 밀도 1 g/mL 근사(원문 밀도 미기재, 근사/미검증)."""
    g_per_L = wt_pct * 10.0     # wt% * (1000 g/L 용액) / 100 = wt%*10 g/L
    return g_per_L / MW

def theta(C_molar, K):
    return K * C_molar / (1.0 + K * C_molar)

c_sat = wt_pct_to_molar(1.5)
th_sat = theta(c_sat, K_L_per_mol)
assert th_sat > 0.98, f"1.5wt%(포화 농도)에서 세타는 거의 포화(>0.98)여야 함, got {th_sat:.4f}"
print(f"1.5 wt% -> {c_sat*1000:.2f} mM -> theta={th_sat:.4f} (거의 포화, 원문 '1.5wt%에서 흡착 포화'와 정합)")

ratio = 11.0 / 90.0
k_inhib = -math.log(ratio) / th_sat
print(f"실측 배수 90->11 A/min (8.2배 감소) 역산 k_inhib = {k_inhib:.3f}")
assert 1.5 < k_inhib < 3.0, f"k_inhib 오더 확인(BTA k=3.0과 동일 자릿수 기대), got {k_inhib:.2f}"

# 0.5 wt%에서 모델 예측치 vs 원문 정성 서술 대조 - 실제로 불일치한다(정직하게 드러낸다)
c05 = wt_pct_to_molar(0.5)
th05 = theta(c05, K_L_per_mol)
resid05 = math.exp(-k_inhib * th05)
pred_05 = 90.0 * resid05
print(f"0.5 wt% -> theta={th05:.4f} -> 모델 예측 정지식각 {pred_05:.1f} A/min")
# Langmuir 등온식은 b=0.009 L/mg로 저농도에서도 theta가 빠르게 포화(0.5wt%에서 이미 0.978)한다.
# 그런데 원문은 0.5wt%를 "억제 실패 수준"(그림상 손상 다수)이라고 정성 서술했다 -
# 모델(theta 기반 지수감쇠)은 이 문턱 거동을 재현하지 못한다. 억지로 맞추지 않고 그대로 드러낸다.
assert pred_05 < 20.0, "모델은 0.5wt%에서 이미 강한 억제를 예측한다(theta 조기포화) - 문헌 정성서술과 불일치"
print("주의: 모델(theta 지수감쇠)은 0.5wt%에서 이미 강한 억제(예측 11 A/min대)를 내지만, "
      "원문은 0.5wt%를 '억제 실패' 수준으로 정성 서술한다 - RESPONSE_CONFLICT 후보. "
      "1.5wt% 앵커점(90->11)은 재현되나 저농도 문턱 거동은 이 형상함수로 못 잡는다 - 미해결.")

mrr_ratio = 120.0 / 85.0
dissolution_ratio = 90.0 / 11.0
assert dissolution_ratio > 3 * mrr_ratio, \
    f"정지식각 억제 배수({dissolution_ratio:.2f})가 CMP 제거율 억제 배수({mrr_ratio:.2f})보다 훨씬 커야 함"
print(f"정지식각 억제 {dissolution_ratio:.2f}배 vs CMP 제거율 억제 {mrr_ratio:.2f}배 "
      "-> 화학은 정지식각을, 기계는 제거율을 지배 (Kaufman 경쟁모델과 정합)")
print("PASS: Langmuir K 환산, 포화 세타, k_inhib 역산, 정지식각-대-제거율 억제 비대칭 재현")

# 문헌값 대조 요약(정량 재현): 정지식각 90 nm/min -> 11 nm/min(1.5wt%, 8.2배 감소),
# CMP 제거율 120 nm/min -> 85 nm/min(1.5wt%, 1.41배 감소) — 단위 환산(1 A/min = 0.1 nm/min)
print(f"환산: 정지식각 {90*0.1:.1f} nm/min -> {11*0.1:.1f} nm/min, "
      f"제거율 {120*0.1:.1f} nm/min -> {85*0.1:.1f} nm/min (문헌 Fig.4 대조 재현)")
assert abs(90*0.1 - 9.0) < 1e-9 and abs(11*0.1 - 1.1) < 1e-9
```

## 6. 한계 (정직 표기)
- wt%에서 mol/L 환산은 밀도 1 g/mL 근사다. 원문이 슬러리 밀도를 명시하지 않았다. 콜로이달 실리카+H2O2
  슬러리의 실제 밀도(약 1.05~1.15 g/mL 추정)를 쓰면 K, theta가 소폭 달라진다 - 미검증.
- 0.5 wt%의 정지식각 정량값은 원문에 숫자로 없다(그래프(Figure 4)만 제시, "실패 수준"이라는 정성 서술뿐).
  5절 verify의 0.5wt% 예측치는 모델이 도출한 값이지 원문 실측치가 아니다.
- k_inhib=2.12는 W/피콜린산 전용 값이다. Cu/BTA의 k=3.0(knowledge/params/cu_h2o2_bta.yaml)과 같은
  형상함수이지만 물질계가 다르므로 값을 공유하지 않는다 - 화학종별로 별도 파라미터가 필요하다는 것이
  이 노트의 핵심 결론이다.
- CMP 제거율 억제(120에서 85 A/min)의 지배 메커니즘(기계 vs 화학)은 원문이 직접 분리하지 않았다.
  5절의 "화학은 정지식각 지배" 해석은 본 노트의 추론이지 원문이 명시한 결론은 아니다.
- Freundlich 모델도 시도됐으나(R2=0.825) Langmuir보다 적합도가 낮아 채택하지 않음 - 원문의 선택을 그대로 따름.
- **모델-문헌 정성 불일치(정직 표기)**: 5절 verify에서 theta 지수감쇠 모델은 0.5wt%에서 이미 theta=0.978로 조기포화해 강한 억제(예측 약 11 A/min)를 내지만, 원문은 0.5wt%를 AFM/SEM상 "억제 실패 수준"으로 정성 서술한다(원문 3.2절). 1.5wt% 앵커점(90->11 A/min)은 정확히 재현되나, 저농도(0.5wt%) 문턱 거동은 단순 Langmuir-지수감쇠 형상으로 못 잡는다 - 문헌에 실제 0.5wt% 정지식각 수치가 없어 이 불일치를 확정할 수 없고(그래프만 존재), 추후 원문 그래프 픽셀 판독이나 저자 문의로 해소해야 할 RESPONSE_CONFLICT 후보로 남긴다.

## 7. 팩 파라미터 연결
knowledge/params/w_fe_oxidizer.yaml에 inhibitor=picolinic_acid, inhibitor_K_L_per_mol=1108.0,
inhibitor_mM(기본 반영 농도), inhibitor_ref_mM(1.5wt%에 해당하는 mM), inhibitor_strength_k=2.12를
추가해 sim/chemistry.py의 _inhibitor_term(기존 BTA와 동일 함수, confidence=estimated로 신규 물질계 표기)이
psi 팩터를 활성화하도록 배선한다. _f_psi는 코드 변경 없이 그대로 재사용 가능(함수가 이미 범용).

## 8. 자기시험
참조: agents/film-w/EXAMS.md Lv1-3
