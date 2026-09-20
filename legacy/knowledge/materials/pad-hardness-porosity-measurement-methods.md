<!-- V2-SECTION: R3-pad | 공동: R2-slurry | 분배완료 2026-09-08 | 근거: pad-, porosity, 기공, 패드 | 정본: ARCHITECTURE-V2.md §3 -->
# CMP 패드 경도·탄성률·기공률 — 측정법과 문헌값 범위 (Lv1-2)

> pad-material Lv1-2. [[pu-pad-chemistry-prepolymer-foam]](Lv1-1, 조성이 경도를 정하는 화학)와
> [[pad-structure-groove-subpad]](pad-mechanic Lv1-2, IC1000/IC1010 실측 Shore D 60·압축률 2.25%)를
> 잇는다. 이 단원의 질문: **경도·탄성률·기공률을 실제로 어떻게 재는가, 그리고 값들이 서로 어떻게 연결되는가.**

## 1. 상용 패드 스펙 — IC1000/IC1010 (Pureon/DuPont 공식 데이터시트)

**출처(1차, 제조사 데이터시트)**: Pureon GmbH, "IC1000 datasheet" (2024-04-09),
https://pureon.com/wp-content/uploads/2024/04/IC1000_datasheet_en_2024-04-09.pdf
(Pureon은 DuPont IC1000™/IC1010™의 공인 유통사 — 원 제조사 DuPont/Qnity의 스펙을 그대로 게재).

| 패드 | 기재 | 압축률 (%) | 경도 | 경도 시험법 | 두께 (mils) |
|---|---|---|---|---|---|
| IC1000™ | 우레탄 | 2.25 | 60 | Shore D | 50 |
| IC1010™ | 우레탄 | 2.25 | 60 | Shore D | 80 |

IC1000/IC1010은 **같은 경도(Shore D 60)** 이고 두께만 다르다 — pad-mechanic Lv1-2 노트가 이미 확인한
값과 정확히 일치([[pad-structure-groove-subpad]] §1). 즉 "하드 IC1000 / 소프트 IC1010" 구분은 경도가
아니라 **적층 구조(IC1010은 서브패드 없이 단독 사용 가능한 2배 두께)** 차이 — CURRICULUM에 적힌
"하드·소프트" 프레임은 이 스펙시트 기준으로는 **부정확**하다(하드니스는 동일). 이 구분은 §2에서
다른 문헌(Shore C 90 계열)과 대조할 때 다시 짚는다.

## 2. Shore 경도 스케일 문제 — D와 C를 같은 표에 놓으면 안 된다

Shore 경도는 압입자 형상이 다른 여러 스케일(A/C/D 등, ASTM D2240)이 있고, **같은 재료라도
스케일이 다르면 숫자가 비교 불가능**하다. 이 노트가 참조하는 두 문헌은 서로 다른 스케일을 쓴다:

- IC1000/IC1010: **Shore D 60** (§1, 상용 경질 패드 표준)
- Chen et al. 2024(§3, 실험실 발포 배합): **Shore C ~90**

두 값을 "60 vs 90"으로 직접 비교하는 것은 **미검증이며 오류에 가깝다** — Shore C와 Shore D는
환산표가 있지만 압입 깊이 기준이 달라 재질군(고무 vs 경질 플라스틱)에 따라 환산 오차가 크다.
ASTM D2240 자체는 유료 표준(1차 미확보, 미러 사이트 미러 응답 없음 — surface-contamination Lv1-2와
동일한 접속 문제, 2026-09-06 재확인)이라 환산식은 이 노트에 넣지 않는다. **결론: 서로 다른 Shore
스케일 값은 병기만 하고 직접 비교하지 않는다** — 이게 이 단원의 핵심 실무 교훈이다.

## 3. 기공률(porosity) 정의와 측정 — 밀도 기반 표준 공식

**출처(1차, 오픈액세스)**: Chen, J. et al., "Effect of Secondary Foaming on the Structural Properties
of Polyurethane Polishing Pad," *Materials* 2024, 17(11), 2759.
DOI: 10.3390/ma17112759, PMC11173749 (MDPI 오픈액세스, 전문 확보·직접 읽음).

기공률은 겉보기밀도와 매트릭스(비발포) 밀도의 비로 정의된다:

```
P = 1 − ρ/ρ₀        ... (식 1, Chen et al. 2024 eq.4)
```
- P: 기공률 (%)
- ρ: 시편의 겉보기밀도 (g/cm³), 질량/부피 직접 측정
- ρ₀: 발포 전 매트릭스(고체 PU) 밀도 — 이 논문은 **1200 kg/m³ = 1.2 g/cm³**를 기준값으로 사용

이 정의는 기공 형상·크기 분포는 전혀 반영하지 않는 **부피 기반 총기공률**이다(SEM·수은압입법
(mercury intrusion porosimetry)은 기공 크기 분포까지 주지만, 이 논문은 밀도법만 씀 — 웹검색으로
확인한 수은압입법 표준 방법론은 원문 미확보, 2차 인용 수준, **미검증**).

## 4. 발포제 종류·투입량 → 밀도·기공률·경도·MRR (정량 데이터, Chen et al. 2024)

무발포(대조군) 대비 NaHCO₃/NH₄HCO₃ 무기 발포제를 프리폴리머(IPDI+PPG1000, DBTDL 촉매)에
첨가한 실험 결과:

| 조건 | 밀도 (g/cm³) | 기공률 (%) | 물흡수율 (부피%) |
|---|---|---|---|
| 무첨가 (대조군) | 0.262 | 78.1 | 3.47 |
| NaHCO₃ 3 wt% (최적) | 0.232 | 80.7 | 6.99 |
| NH₄HCO₃ 1 wt% (최적) | 0.196 | 83.7 | 14.17 |

경도: 두 발포제 계열 모두 **Shore C 약 90 부근에서 유지**(첨가량에 따라 소폭 변동, 논문은 정확한
숫자 표 대신 그림 인용이라 이 노트에선 "약 90"으로만 확정 — **미검증**: 세부 첨가량별 정확한
경도 수치는 그래프 판독 없이는 못 얻음).

## 5. 정량 재현 — MRR 두 계열의 "기저 MRR"이 서로 일치하는지 교차검산

논문 본문은 MRR을 "무첨가 대비 몇 % 증가"로만 서술하고 최댓값(nm/min)을 따로 준다. 두 독립
계열(NaHCO₃ 최적 3wt%, NH₄HCO₃ 최적 1wt%)이 **같은 무첨가 대조군**을 기준으로 삼았다면, 각각의
증가율로 역산한 "무첨가 기저 MRR"이 서로 일치해야 한다. 이게 저자가 숫자를 일관되게 보고했는지
확인하는 독립적 sanity check다.

```python verify
# 출처: Chen et al. 2024, Materials 17(11), 2759, DOI 10.3390/ma17112759, §3.5
# "최대 MRR NaHCO3=89.45 nm/min (3wt%), 무첨가 대비 +33.8%"
# "최대 MRR NH4HCO3=98.78 nm/min (1wt%), 무첨가 대비 +47.8%"
mrr_nahco3_max = 89.45   # nm/min, 3 wt%
pct_nahco3 = 33.8        # %
mrr_nh4hco3_max = 98.78  # nm/min, 1 wt%
pct_nh4hco3 = 47.8       # %

baseline_from_nahco3 = mrr_nahco3_max / (1 + pct_nahco3 / 100)
baseline_from_nh4hco3 = mrr_nh4hco3_max / (1 + pct_nh4hco3 / 100)

# 두 독립 계열에서 역산한 무첨가 기저 MRR이 서로 일치하는지 (같은 대조군을 썼다는 저자 주장 검증)
diff_pct = abs(baseline_from_nahco3 - baseline_from_nh4hco3) / baseline_from_nahco3 * 100
print(f"NaHCO3 계열 역산 기저 MRR: {baseline_from_nahco3:.2f} nm/min")
print(f"NH4HCO3 계열 역산 기저 MRR: {baseline_from_nh4hco3:.2f} nm/min")
print(f"두 역산값 차이: {diff_pct:.2f}%")

assert abs(baseline_from_nahco3 - 66.85) < 0.05, "NaHCO3 역산값이 66.85 nm/min에서 벗어남"
assert abs(baseline_from_nh4hco3 - 66.83) < 0.05, "NH4HCO3 역산값이 66.83 nm/min에서 벗어남"
assert diff_pct < 0.1, f"두 계열 역산 기저 MRR이 {diff_pct:.2f}% 차이 — 저자 보고 불일치 의심"
```

역산 결과(Chen et al. 2024, doi:10.3390/ma17112759 §3.5 수치 기반 python verify) 두 계열 모두
**기저 MRR ≈ 66.8 nm/min**로 0.03% 이내 일치 — 저자가 실제로 같은 대조군 데이터를 두 계열에
일관되게 사용했음을 확인(문헌 자체 내적 정합성 검증, 외부 문헌과의 대조는 아님). 이 절대값
(66.8 nm/min, doi:10.3390/ma17112759 역산)은 실험 조건(하중·속도·슬러리)이 논문 본문에 별도
기재되어 있으나 이 노트에서는 §6로 미룬다(1차 미확보 항목은 아니고 단순 범위 초과).

## 6. Gibson-Ashby 발포 스케일링 법칙 — 기공률→탄성률의 이론적 연결 (2차 인용, 미검증)

재료과학에서 발포체 탄성률-상대밀도 관계는 통상 **Gibson-Ashby 모델**로 기술된다:

```
E*/Es ≈ C · (ρ*/ρs)^n
```
- E*: 발포체(다공성) 탄성률, Es: 매트릭스(비발포) 고체 탄성률
- ρ*/ρs: 상대밀도 (= 1 − 기공률)
- 개기공(open-cell) 발포체는 n≈2, 폐기공(closed-cell)은 n≈1~2 범위가 통상 보고됨

**출처**: L. J. Gibson & M. F. Ashby, *Cellular Solids: Structure and Properties*, Cambridge Univ.
Press — 이 노트에서는 **원문(단행본) 미확보**, 웹검색 스니펫(ScienceDirect Topics, Bohrium 요약
페이지)만 확인한 **2차 인용**. 지수 n과 상수 C의 정확한 값·유도는 원문 없이 이 노트에 넣지 않는다.
CMP 패드가 개기공인지 폐기공인지도 Chen et al.(2024)이 SEM에서 "open-pore structure가 발포제
증가에 따라 나타난다"고 서술한 것으로 보아 **혼합형에 가깝다** — 이 역시 미검증.

이 관계식을 §4의 실측 기공률(78~84%)·경도값(Shore C 90 부근)에 직접 대입해 탄성률을 계산하는
것은 **다음 단원(Lv2-1 점탄성 심화)**으로 미룬다 — Es(매트릭스 PU 탄성률)와 정확한 n을 원문
확보 없이 가정하면 계산값 자체가 지어낸 수치가 되기 때문이다(규칙 3: 모르면 모른다고 쓴다).

## 7. Lv1-1과의 접점 — 조성(NCO%)이 경도로, 경도가 기공 형성 여유도로 이어지는 경로

[[pu-pad-chemistry-prepolymer-foam]] §2가 정리한 것처럼 프리폴리머의 %NCO(경질세그먼트 밀도)가
경도 목표를 정한다. 이 단원(§4)이 보여준 것은 그 다음 단계 — **같은 프리폴리머 배합에서 발포제
종류·양을 바꾸면 경도는 거의 유지된 채(Shore C 90 부근 고정) 밀도·기공률만 크게 변한다**는
사실이다. 즉 경질세그먼트 화학이 "경도의 상한"을, 발포 공정이 "그 안에서 기공률·MRR"을 따로
조절하는 **직교(orthogonal)에 가까운 두 손잡이**로 작동한다는 그림 — 다만 이건 이 두 논문의
관찰을 조합한 이 노트의 해석이지 원 문헌이 명시한 결론은 아니므로 **추정**으로 표기한다.

## 8. Qi, Joyce, Boyce(2003) — 범용 탄성체 Shore→탄성률 정량 환산: 있다, 그러나 못 쓴다

**배경**: sim/factors.py `_f_kappa()`는 패드 경도 항(H^-1.5)의 confidence를 구조적으로
"estimated"에 고정해 왔다. 이유는 "Shore D는 경도의 대리지표이고, H^-1.5의 H는 압입경도
(GPa)인데 Shore D↔GPa 환산이 비선형이며 미검증"(코드 주석). 이 절은 그 환산식의 1차 문헌을
실제로 찾아 대입해 본 결과다 — **찾았지만, 세 가지 이유로 confidence 승격에는 쓸 수 없다.**

**출처(1차, 무료 전문 확보)**: Qi, H. J., Joyce, K., Boyce, M. C., "Durometer Hardness and the
Stress-Strain Behavior of Elastomeric Materials," *Rubber Chemistry and Technology*, 76(2),
419–435 (2003). DOI: 10.5254/1.3547752 (papers/qi-joyce-boyce2003-durometer-hardness.pdf로
전문 확보·직접 읽음 — MIT 기계공학과 저자들의 유한요소 압입 시뮬레이션 논문).

### 8.1 논문이 실제로 주는 두 모델

- **FEA(비선형, 저자들이 사실상 "정답"으로 취급)**: Gaussian(neo-Hookean) 재료 µ=30MPa
  (E₀=3µ=90MPa, eq.9a)를 유한요소로 압입 시뮬레이션하면 Shore D **62**가 나온다(원문 p.428,
  "the Shore hardness for this material is 62D").
- **선형탄성 해석해(1차 근사, Sneddon 1965 원뿔 압입자 해, θ=15°, ν=0.5)** — eq.(11):

  ```
  H_D = 100 − 20·(−78.188 + √(6113.36 + 781.88·E)) / E      [E: MPa]
  ```

- 저자들이 직접 명시한 결론(원문 p.430): "선형탄성 해석해는 주어진 경도에 대해 FEA보다 더 큰
  탄성률을 예측하며, **그 격차는 경도가 커질수록 증가한다**."

```python verify
# 출처: Qi, Joyce, Boyce (2003), Rubber Chem. Technol. 76(2), 419-435,
# DOI: 10.5254/1.3547752, eq.(11) 및 p.428(FEA 앵커: mu=30MPa -> E0=90MPa -> Shore D 62)
import math

def H_D_eq11(E_mpa: float) -> float:
    return 100 - 20 * (-78.188 + math.sqrt(6113.36 + 781.88 * E_mpa)) / E_mpa

def E_from_H_D_eq11(H_D_target: float, lo=0.001, hi=1e6, tol=1e-9) -> float:
    # H_D_eq11은 E에 대해 단조증가이므로 이분법으로 역산
    f = lambda E: H_D_eq11(E) - H_D_target
    a, b = lo, hi
    fa = f(a)
    for _ in range(200):
        m = (a + b) / 2
        fm = f(m)
        if abs(fm) < tol or (b - a) < tol:
            return m
        if (fa < 0) == (fm < 0):
            a, fa = m, fm
        else:
            b = m
    return (a + b) / 2

# (1) eq(11)에 FEA 앵커의 E=90MPa를 넣으면 FEA가 실제로 관측한 62D와 다른 값이 나와야 한다
#     (선형탄성 해석해가 FEA와 다르다는 저자 주장의 직접 재현)
h_d_at_90mpa = H_D_eq11(90.0)
print(f"eq(11)에 E=90MPa 대입 -> H_D={h_d_at_90mpa:.2f} (FEA 실측은 62D)")
assert abs(h_d_at_90mpa - 55.92) < 0.05, "eq(11) E=90MPa 재현값이 논문과 어긋남"
assert h_d_at_90mpa < 62.0, "저자 주장(해석해가 FEA보다 더 큰 E를 요구)과 모순 — 같은 E에서 해석해 예측 경도가 FEA보다 낮아야 함"

# (2) 반대로 FEA가 준 62D에서 eq(11)이 요구하는 E를 역산하면 90MPa보다 커야 한다(같은 방향의 편향)
e_at_62d = E_from_H_D_eq11(62.0)
ratio = e_at_62d / 90.0
print(f"eq(11) 역산 E at H_D=62 = {e_at_62d:.2f} MPa (FEA 실측 E0=90MPa), 배율={ratio:.3f}")
assert abs(e_at_62d - 134.28) < 0.1, "eq(11) 역산값이 재현되지 않음"
assert ratio > 1.0, "해석해가 FEA보다 더 큰 E를 예측해야 한다는 저자 주장과 불일치"

# (3) IC1000/IC1010 실제 스펙(Shore D 60, 본 노트 §1)에 eq(11)을 그대로 적용한 값
e_at_60d = E_from_H_D_eq11(60.0)
print(f"eq(11)로 IC1000/1010(Shore D 60) 추정 E = {e_at_60d:.2f} MPa = {e_at_60d/1000:.4f} GPa")
assert abs(e_at_60d - 117.28) < 0.1, "IC1000 Shore D 60 환산값이 재현되지 않음"
```

재현 결과(DOI: 10.5254/1.3547752, eq.11 python verify): eq(11)에 FEA 앵커(E=90MPa)를 넣으면
55.92D — FEA 실측 62D보다 **낮다**. 반대로 FEA가 준 62D를 eq(11)로 역산하면 134.28MPa — FEA
실측 90MPa보다 **49% 높다**. 두 재현 모두 저자 주장("해석해가 FEA보다 더 큰 E를 예측, 경도가
커질수록 격차 확대")과 방향이 일치한다.
IC1000/IC1010(Shore D 60, §1)에 eq(11)을 그대로 넣으면 E≈117.3 MPa(0.117 GPa)가 나온다.

### 8.2 그런데도 confidence를 못 올리는 세 가지 이유

**세 가지 이유** 모두 필요조건이라 하나만 걸려도 승격 불가다.

1. **경도가 오를수록 벌어지는 격차의 크기를 60D에서 모른다.** §8.1의 49% 과대추정은 **62D
   단일 앵커점**에서만 확인됐다. 원문은 "격차가 경도와 함께 커진다"는 방향만 보장하고 그 함수
   형태는 주지 않는다(Fig.12 자체가 y축 라벨이 "Error (%)"로 인쇄되어 있어 — Fig.13의 동일
   축("E₀ (MPa)")과 대조하면 원 저널의 인쇄 오류로 보이지만 확인 불가 — 곡선 값을 픽셀 판독해
   보정계수를 세분화하는 것은 이 노트에서 **하지 않는다**(규칙: 애매한 축을 지어내 읽지 않는다).
   따라서 60D에서 실제 배율이 1.49보다 큰지 작은지조차 모른다 — 62→60D 사이 외삽조차 못 한다.
2. **재질군이 다르다.** 원 논문은 범용 가황고무·엘라스토머(Gaussian/Arruda-Boyce 사슬 모델,
   ASTM D2240)를 다룬다. CMP 패드는 가교 폴리우레탄(경질/연질 세그먼트 공중합체, IC1000/1010은
   무발포 캐스트 — [[pu-pad-chemistry-prepolymer-foam]] §2)로 화학이 다르다. §2가 이미 지적한
   "Shore C를 Shore D와 비교하면 안 된다"는 함정과 같은 종류의 함정이다 — 이번엔 스케일이 아니라
   **재질 자체**가 다르다. 저자들은 폴리우레탄 CMP 패드에 자기 모델을 검증한 적이 없다.
3. **애초에 같은 물리량이 아니다.** eq(11)이 주는 E는 **단축인장 초기 탄성률**(uniaxial initial
   modulus, E₀=3µ, eq.9a)이다. `_f_kappa` 코드 주석이 말하는 "압입경도(GPa)"는 소성·항복 거동까지
   반영하는 별개의 양이다 — 탄성률과 압입경도는 상관되지만 동일하지 않다. 즉 eq(11)을 쓰더라도
   코드 주석이 전제한 "H=압입경도(GPa)"를 eq(11)의 출력(인장탄성률)으로 바로 채울 근거가 없다.

**결론**: 이 문헌은 `_f_kappa`의 confidence 하한이 가리키던 "Shore D↔GPa 환산이 비선형이며
미검증"이라는 서술에 **처음으로 정량적 형태**(eq.11, 그리고 FEA 대비 편향의 존재·방향·62D에서의
크기 49%)를 부여한다. 그러나 위 세 이유로 "미검증"을 "검증됨"으로 바꾸지 못한다 — 오히려
"Shore D→GPa는 물론, 애초에 그 GPa가 압입경도인지 인장탄성률인지부터 문헌마다 다른 양을 잰다"는
더 정밀한 미해결 문제를 드러냈다. sim/factors.py의 `_worst_conf(..., "estimated")`는 그대로
유지한다(EVIDENCE-RULES.md — 근거가 불충분하면 지어내지 않고 estimated로 남긴다).

## 자기 점검
- IC1000/IC1010의 경도 차이는? → 없음(둘 다 Shore D 60), 차이는 두께(50 vs 80 mils)뿐 (§1)
- Shore C 90과 Shore D 60을 직접 "더 무르다/단단하다"고 비교할 수 있는가? → 아니오, 스케일이
  달라 직접 비교 불가(§2, ASTM D2240 환산표 1차 미확보로 이 노트에 없음)
- Chen et al.(2024) 최적 발포제 조건에서 MRR 개선폭은? → NaHCO₃ 3wt%: 최대 89.45 nm/min
  (+33.8%), NH₄HCO₃ 1wt%: 최대 98.78 nm/min(+47.8%), 두 계열 역산 기저 MRR 66.8 nm/min로
  상호 일치(§5 python verify)
- Qi et al.(2003) eq(11)로 IC1000(Shore D 60)의 탄성률을 추정할 수 있는가? → 계산은 된다
  (E≈117.3 MPa, §8.1 python verify) 그러나 confidence는 못 올린다 — 62D 앵커점 밖 외삽 불가,
  범용 고무 대상(폴리우레탄 미검증), 그리고 탄성률≠압입경도라는 물리량 불일치 때문(§8.2)

## 다음 단원
Lv2-1(점탄성 심화: 온도·주파수 의존 저장/손실 탄성률)에서 §6의 Gibson-Ashby 관계를 원문
확보 후 완성하고, 매트릭스 PU 탄성률 Es의 1차 출처를 찾아 실제 탄성률 계산까지 진행한다.
§8이 드러낸 "탄성률 vs 압입경도" 구분 문제도 이 단원에서 Es를 구할 때 같이 정리해야 한다 —
같은 혼동이 반복되지 않도록.
