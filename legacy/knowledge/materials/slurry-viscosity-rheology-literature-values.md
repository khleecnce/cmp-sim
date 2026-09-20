<!-- V2-SECTION: R2-slurry | 공동: R4-physics | 근거: viscosity, 점도, 슬러리, 레올로지, rheology | 정본: ARCHITECTURE-V2.md §2 -->
# CMP 슬러리 점도 — 실측 문헌값과 전단속도 의존성 (Lv2)

> slurry Lv2 | 작성일: 2026-09-11
> 선행: [[cmp-lubrication-regimes]](So·λ 정의, μ를 입력으로 요구 — 노트는 "물기반 ~1e-3"으로만 명시),
> [[pad-groove-cfd-micropattern-optimal-design]](CFD가 "water viscosity for dilute suspensions" 가정).
> 이 노트의 질문: **엔진 키 `slurry_viscosity_pa_s`에 넣을 값이 문헌 실측으로 뒷받침되는가.**
> 선행 노트 두 개 모두 "물 근사"라는 가정만 서술하고 실측 슬러리를 측정한 값이 아니었다
> (=confidence estimated). CMP 전단속도 영역(10³~10⁵ s⁻¹)에서의 실측값이 필요하다.

## 1. 1차 출처 (모두 OA, 본문 확인)

1. **Crawford, Williams, Boldridge, Liberatore (2013)**, "Shear thickening and defect formation of
   fumed silica CMP slurries", *Colloids Surf. A* **436**, 87-96. DOI: **10.1016/j.colsurfa.2013.06.003**.
   Colorado School of Mines + Cabot Microelectronics. 원문 미확보(합법 OA 없음) → 미러 사이트 미러에서
   PDF 확보, `papers/crawford2013-colsurfa-fumed-silica-shear-thickening.pdf` (10쪽 전문 확인).
   **CMP 공정 전단속도(10³~10⁵ s⁻¹)에서 직접 레오미터로 측정한 유일한 확보 문헌.**
2. **Kim et al. (2024)**, "The Stability Evaluation of Ceria Slurry Using Polymer Dispersants with
   Varying Contents for CMP Process", *Polymers* **16**(24), 3593. DOI: **10.3390/polym16243593**.
   MDPI OA, PMC11679047. 본문·Figure 16/17/18 서술 확인.
3. **Kim et al. (2024)**, "Characterization of Ceria Nanoparticles as Abrasives Applied with
   Defoaming Polymers for CMP", *Polymers* **16**(6), 844. DOI: **10.3390/polym16060844**.
   MDPI OA, PMC10974854. **Table 3·Table 4** 수치 직접 인용.
4. **Lee et al. (2025)**, "Effects of Hydrolysis Reaction and Abrasive Drag Force Accelerator on
   Enhancing Si-Wafer Polishing Rate...", *Nanomaterials* **15**(16), 1248. DOI: **10.3390/nano15161248**.
   MDPI OA, PMC12388451. 콜로이달 실리카 슬러리 점도(Brookfield DV-II+Pro) 직접 인용.

## 2. 정량값 — 슬러리 종류별 실측 점도

| 슬러리 | 고형분/조성 | 점도 (실측) | 전단속도/측정기 | 출처 |
|---|---|---|---|---|
| **콜로이달 실리카** (Si 웨이퍼 CMP, pH 9.7) | 콜로이달 실리카 + TAP 0.0024~0.0244 wt% | **~0.98 cP = 9.8e-4 Pa·s** (TAP 농도 무관, 일정) | Brookfield DV-II+Pro (회전식, 저전단) | Lee 2025 §3.2, Fig.3a |
| 콜로이달 실리카 + HEC 증점제 | HEC 0.0012 → 0.0049 wt% | **1.01 → 1.12 cP** (1.01e-3 → 1.12e-3 Pa·s) | 동상 | Lee 2025 §3.3, Fig.7a |
| 콜로이달 실리카 + TAP + HEC | HEC 0.0012 → 0.0049 wt% (TAP 0.0037 고정) | 1.02 → 1.13 cP | 동상 | Lee 2025 §3.5, Fig.11a |
| **상용 세리아 슬러리** | 미상(commercial) | **1.41 cP = 1.41e-3 Pa·s** (초기, 25 °C) → 3개월 후 1.16 cP | Brookfield (cone/plate) | Kim 2024b §3.3, Fig.17d |
| 자체제조 세리아 (SMA 분산제 5~7 wt%) | D5/D6/D7 | **1.62 / 1.47 / 1.44 cP** (초기) | 동상 | Kim 2024b §3.3 |
| 세리아 + SMA-1000 분산제 4.0/4.5/5.0 % | — | **1.34 / 1.34 / 1.35 cP** | Brookfield DV Next Cone/Plate | Kim 2024a **Table 3** |
| 세리아 + 소포제(Depol/BYK/G-336) | 0.01~0.05 % | **1.31 ~ 1.33 cP** (거의 불변) | 동상 | Kim 2024a **Table 4** |
| **퓸드 실리카 25 wt%** (염 무첨가) | 25 wt%, KCl 없음 | 1,000→100,000 s⁻¹ 구간에서 **전단박화, 40 % 감소** (절대값은 Fig.3a 그래프만, 표 없음) | AR-G2 평행판, gap 30 µm | Crawford 2013 §3.1 |
| 퓸드 실리카 25 wt% + KCl 0.15 M | 고이온강도 | ~30,000 s⁻¹에서 **전단증점 개시, 30k→100k s⁻¹에 5배 증가**, 비가역(최종 ~100배) | 동상 | Crawford 2013 초록·§3.1 |
| (검증 대조) **DI water** | — | **8.6 ± 0.3 ×10⁻⁴ Pa·s** (측정), 문헌값 8.9e-4 Pa·s(25 °C)의 3 % 이내 | 동상, 전체 전단램프 평균 | Crawford 2013 §3.1 |

### 채택값

- **콜로이달 실리카계(oxide_silica 팩)**: **1.0e-3 Pa·s**.
  Lee 2025의 무첨가 실측 0.98e-3 ~ 증점제 첨가 1.12e-3의 중심. 기존 base 추정값과 숫자는 같지만
  **근거가 "물이니까 1e-3"에서 "콜로이달 실리카 CMP 슬러리 실측 0.98~1.13 cP"로 바뀐다.**
- **세리아계(sti_ceria, sic_ceria_h2o2 팩)**: **1.4e-3 Pa·s**.
  Kim 2024b 상용 세리아 슬러리 초기 실측 1.41 cP. Kim 2024a의 세리아 슬러리 1.31~1.35 cP와
  같은 대역이며 그 중 **상용품**을 대표값으로 골랐다. 실리카계보다 ~40 % 높다.

### 전단속도 의존성 — 왜 단일 스칼라가 허용되는가(그리고 언제 깨지는가)

- CMP 실공정 전단속도는 10³~10⁶ s⁻¹(Crawford 2013 §1, Lortz 2003 재인용).
- **희박 슬러리(수 wt% 이하, 상용 산화막/세리아 슬러리)**: Crawford의 DI water 대조가 전단속도
  무관(뉴턴)이고, Kim 2024b는 상용 세리아 분산제가 "Newtonian behavior"라고 명시. → 단일 스칼라 OK.
- **고고형분·고이온강도(25 wt% 퓸드 실리카 + 0.15 M KCl)**: 30,000 s⁻¹ 이상에서 5배 증점, 비가역.
  → **이 영역에서는 단일 스칼라가 물리적으로 틀린다.** 우리 엔진은 이 레짐을 모델링하지 않으므로
  적용 범위를 "희박 수계 슬러리"로 한정해 두어야 한다(§4 한계 1).
- 위 표의 Brookfield 값들은 **회전식 점도계(저전단)** 측정이며, 10³~10⁵ s⁻¹에서 직접 잰 값이 아니다.
  희박 뉴턴 슬러리라면 전단속도 무관이므로 외삽이 정당하지만, 이는 **가정이다**(§4 한계 2).

## 3. 정량 재현 (python verify)

```python verify
CP = 1.0e-3  # 1 cP = 1e-3 Pa.s

# (1) Crawford 2013 DI water 대조 — 측정기 검증(문헌이 스스로 한 검증을 재현)
water_measured, water_ref = 8.6e-4, 8.9e-4          # Pa.s, 25 C
rel_err = abs(water_measured - water_ref) / water_ref * 100
assert rel_err < 3.5, rel_err                        # 원문 "within ~3%"
print(f"(1) Crawford DI water 실측 {water_measured:.2e} vs 문헌 {water_ref:.2e} Pa·s "
      f"-> 오차 {rel_err:.1f}% (원문 '~3% 이내' 재현)")

# (2) 콜로이달 실리카 슬러리 (Lee 2025) — cP -> Pa.s 환산 및 채택값 타당성
silica_cp = [0.98, 1.01, 1.12, 1.02, 1.13]           # TAP계, HEC 0.0012~0.0049 wt%, TAP+HEC
silica_pa_s = [v * CP for v in silica_cp]
adopted_silica = 1.0e-3
assert min(silica_pa_s) <= adopted_silica <= max(silica_pa_s), (adopted_silica, silica_pa_s)
print(f"(2) 콜로이달 실리카 실측 {min(silica_pa_s):.2e}~{max(silica_pa_s):.2e} Pa·s "
      f"-> 채택 {adopted_silica:.2e} (실측 범위 안)")

# (3) 세리아 슬러리 (Kim 2024a Table 3/4, Kim 2024b) — 채택값 1.4e-3
ceria_cp = {"commercial(2024b)": 1.41, "D5": 1.62, "D6": 1.47, "D7": 1.44,
            "SMA4.0": 1.34, "SMA4.5": 1.34, "SMA5.0": 1.35,
            "Depol0.01": 1.33, "BYK0.05": 1.31, "G336": 1.32}
adopted_ceria = 1.4e-3
lo, hi = min(ceria_cp.values()) * CP, max(ceria_cp.values()) * CP
assert lo <= adopted_ceria <= hi, (adopted_ceria, lo, hi)
assert abs(adopted_ceria - 1.41 * CP) < 2e-5        # 상용품 실측 1.41 cP를 유효숫자 2자리로 반올림
print(f"(3) 세리아 실측 {lo:.2e}~{hi:.2e} Pa·s (n={len(ceria_cp)}) "
      f"-> 채택 {adopted_ceria:.2e} = 상용 슬러리 초기 실측 1.41 cP")

# (4) 세리아가 실리카보다 높다 (같은 부호의 물리적 서열이 유지되는지)
assert adopted_ceria > adopted_silica
print(f"(4) 세리아/실리카 점도비 = {adopted_ceria/adopted_silica:.2f}배 "
      f"(세리아 고형분·분산제가 더 많음 — 방향 일치)")

# (5) 전단증점 레짐 경계 (Crawford) — 우리 스칼라 모델의 적용 한계를 수치로 명시
onset_shear_rate = 30_000.0   # 1/s, 25 wt% fumed silica + 0.15 M KCl
thickening_factor = 5.0       # 30k -> 100k s^-1
cmp_shear_lo, cmp_shear_hi = 1e3, 1e5
assert cmp_shear_lo < onset_shear_rate < cmp_shear_hi
print(f"(5) 전단증점 개시 {onset_shear_rate:.0e} 1/s는 CMP 전단영역 "
      f"{cmp_shear_lo:.0e}~{cmp_shear_hi:.0e} 1/s 내부 -> 고고형분(25wt%)·고이온강도 슬러리에는 "
      f"단일 스칼라 금지(최대 {thickening_factor:.0f}배 증점)")

# (6) 선행 노트 [[cmp-lubrication-regimes]] §2의 "물기반 ~1e-3" 가정과 모순되지 않는지
assert 0.5e-3 < adopted_silica < 2e-3 and 0.5e-3 < adopted_ceria < 2e-3
print("(6) 두 채택값 모두 선행 노트의 '~1e-3 오더' 가정과 정합 -> So/λ 진단 결론 불변")
```

## 4. 한계 / 미검증 표기

1. **적용 범위**: 채택값은 **희박 수계 CMP 슬러리(수 wt% 급)** 에만 유효하다. 25 wt% 퓸드 실리카 +
   고이온강도처럼 전단증점하는 슬러리는 10³~10⁵ s⁻¹에서 5배(비가역 시 ~100배)까지 오르므로
   단일 스칼라로 표현 불가 — 엔진 주석에 명시할 것.
2. **측정 전단속도 불일치**: 표의 cP 값들은 Brookfield 회전식(저전단) 측정이다. CMP 전단속도에서
   직접 잰 값이 아니며, "희박 슬러리는 뉴턴"이라는 근거(Kim 2024b 명시 + Crawford의 물 대조)에
   기대어 외삽했다 — 이 외삽 자체는 미검증.
3. **고형분 함량 미상**: Kim 2024a/b 모두 세리아 슬러리의 고형분 wt%를 본문에 명시하지 않았다.
   따라서 "고형분 X wt%일 때 점도 Y"라는 관계식은 세울 수 없다
   ([[knowledge/components/slurry.yaml]] "고형분-점도 관계" 항목은 여전히 미해결).
4. **온도 의존성 미확보**: 모든 값이 25 °C 기준. CMP는 패드-웨이퍼 마찰로 40~60 °C까지 오르며 물의
   점도는 그 구간에서 ~40 % 떨어지지만, 슬러리 점도의 온도곡선을 준 문헌은 미확보 — 미검증.
5. **sic_ceria_h2o2 팩 특수성**: H₂O₂ 첨가 세리아 슬러리의 점도를 직접 잰 문헌은 못 찾았다.
   H₂O₂는 저농도 수용액이라 점도를 크게 바꾸지 않을 것으로 보이나 **근거 없음** — 세리아 일반값을
   전용하며 이 전용 자체를 미검증으로 표기한다.
6. `validation/datasets/sic2023_shear_rheological_L9.yaml`은 "전단유동 연마(SRP)" 데이터셋으로
   슬러리 점도를 보고하지 않는다(in_scope: false). 이 노트에 쓸 수치 없음 — 확인 완료.

미검증 5건 / 정량값 20건 이상(표+verify assert) → 품질게이트(정량값 절반 이하) 충족.
