# Poly:Oxide 선택비 설계와 게이트 CMP 공정 윈도우

> 에이전트: film-poly-si Lv2-1 | 작성일: 2026-09-11
> 선행: [[film-poly-si-alkaline-dissolution-ph-kinetics]] (Lv1-2 — OH⁻ 알칼리 용해 메커니즘·Seidel 활성화에너지),
> [[film-poly-si-doping-grain-cmp]] (Lv1-1 — 도핑·결정립이 poly MRR을 바꾸는 축)
> 관련: [[film-nitride-selectivity-ceria-chemistry]] (나이트라이드 선택비의 3단 위계 프레임 — 같은 구조를 poly:oxide에 적용),
> [[../cmp/sti-nitride-loss-erosion-overpolish-window]] (오버폴리시 창 개념의 원형),
> [[../cmp/silica-cmp-ph-acidic-repulsion-choi-power-law]] (실리카 표면 정전기·pH 의존)
> 후속: [[film-poly-si-high-selectivity-lowdefect-slurry]] (Lv3-1 — poly:nitride 축을 채우고, 선택비 계단이 poly 가속이 아니라 산화막 억제에서 나옴을 보인다)

## 1. 왜 필요한가 — 게이트 CMP에서 선택비는 "방향"이 두 가지다

Poly-Si가 관여하는 게이트 CMP에는 **선택비의 방향이 반대인 두 가지 공정**이 있다:

1. **NAND 플로팅 게이트/STI형(poly-stop-on-oxide)**: poly-Si를 산화막(트렌치 충전 oxide) 위까지
   완전히 깎아내되 산화막은 보존해야 한다 — **poly:oxide 선택비를 높게** 원한다(poly가 빨리
   깎여야 함).
2. **리플레이스먼트 메탈게이트(replacement gate, poly-open CMP)**: 더미 poly-Si 게이트가
   금속게이트로 치환되기 전까지 **구조적 정지층(etch stop)** 역할을 해야 하므로, 위에 덮인
   ILD 산화막은 빨리 깎이고 poly는 보존돼야 한다 — **oxide:poly 선택비를 높게** 원한다(정반대
   방향).

이 노트는 1차 문헌 2건(§2, §3, 모두 방향 ①)과 특허 1건(§4, 방향 ②)으로 두 방향의 선택비를
정량 대조하고, §5에서 선택비가 실제 공정 윈도우(오버폴리시 마진)로 어떻게 번역되는지, §6에서
Lv1-2의 Seidel 활성화에너지가 이 선택비의 화학적 뿌리를 얼마나(그리고 얼마나 못) 설명하는지를
다룬다.

## 2. 1차 출처 — Park et al. (2007): TMAH 농도가 poly:oxide 선택비를 지배한다

1차 논문: Park, K.-W., Kang, H.-G., Kanemoto, M., Park, J.-G., Paik, U. (2007), "Effects of the
Size and the Concentration of the Abrasive in a Colloidal Silica (SiO₂) Slurry with Added TMAH on
Removal Selectivity of Polysilicon and Oxide Films in Polysilicon Chemical Mechanical Polishing,"
*J. Korean Phys. Soc.* 51(1), 214–223, DOI: 10.3938/jkps.51.214 — https://doi.org/10.3938/jkps.51.214
— papers/park2007-jkps-tmah-abrasive-poly-oxide-selectivity.pdf, 원문 전체(10쪽) 확보·직접 인용.
대상 공정은 NAND 플래시 플로팅 게이트용 STI(§1 방향 ①): poly-Si가 산화막 위까지 완전히
제거돼야 한다.

**정량 결과(원문 결론부·Fig.5(b)(d) 서술):** 실리카 abrasive(30/70 nm) 5.3 wt% 조건에서 TMAH
농도(0.06→0.52 wt%)를 올리면 poly:oxide 선택비는 **약 25:1로 시작해 45:1까지 오른 뒤 다시
33:1로 내려가는 비단조(피크형)** 곡선을 그린다(원문: "the selectivity decreased after a
slightly increase, approximately from 25 : 1 to 45 : 1 to 33 : 1"). 반대로 **산화막 제거율은
TMAH 농도와 무관하게 40–60 Å/min 구간에 고정**된다(원문 결론: "the oxide removal rate was
maintained at 40 to 60 Å/min"). 즉 선택비 변화는 거의 전부 **poly 제거율의 비단조 변화**에서
온다 — 산화막은 TMAH에 화학적으로 거의 반응하지 않고 순수 기계적 마모율에 가깝게 유지된다(§7
verify (A)).

**메커니즘(원문 §III):** OH⁻가 abrasive·poly 표면의 Si에 결합해 실라놀기를 만들고 이것이
Si–Si 백본드를 편극시켜 약화시킨다(Lv1-2 §2 Seidel 반응식 Si+4OH⁻→Si(OH)₄+4e⁻와 정합). 여기에
**제타전위 비대칭**이 더해진다: poly-Si 필름은 등전점(IEP) pH 5–6이고 pH 10 이상에서도 약한
음전하(< −5 mV)에 머무는 반면, 산화막·개질된 실리카 abrasive 입자는 pH 10 이상에서 강한
음전하(> −50 mV)로 벌어진다. 그 결과 **abrasive–poly는 정전 인력(상대적으로 반발이 적음) →
기계적 접촉 강화, abrasive–oxide는 정전 반발 강화 → 접촉 회피**가 일어나 선택비를 밀어올린다.
**접촉각 상관:** poly 표면 접촉각이 TMAH 0.12 wt%에서 최소(41°, 최대 친수성)를 찍은 뒤 0.52
wt%에서 51.5°로 다시 오르는데, 이 곡선이 poly 제거율 곡선의 **거울상**이다 — 친수성이
높을수록(접촉각↓) 슬러리·OH⁻ 전달이 쉬워져 제거율이 오른다는 논리로, [[film-poly-si-alkaline-dissolution-ph-kinetics]]
§5의 Bae(2022) 접촉각-제거율 상관(EDA 50.5°→14.55°, 제거율↑)과 **같은 방향의 현상**이다(다른
알칼리원·다른 막이지만 "친수성↑→제거율↑" 정성 규칙은 일치).

## 3. Hwang/Kang et al. (2008): 알칼리원 종류(NaOH/KOH/TMAH)별 선택비 정점 비교

1차 출처(초록만 확보): Hwang, H.-S., Kang, H.-G., Park, J.-H., Paik, U., Park, J.-G. (2008),
"Effect of Alkaline Agent with Organic Additive in Colloidal Silica Slurry on Polishing Rate
Selectivity of Polysilicon-to-SiO₂ in Polysilicon CMP," 213th ECS Meeting Abstract #692, *ECS
Meeting Abstracts* MA2008-01, 692, DOI: 10.1149/ma2008-01/17/692 —
https://doi.org/10.1149/ma2008-01/17/692 — papers/kim2008-iop-polysilicon-alkaline-slurry.pdf,
2쪽 확대초록(extended abstract) 확보·직접 인용. 전체 논문(ECS Transactions 버전, DOI:
10.1149/1.2912980)은 **미확보 — 초록 수준의 정량치만 이 노트에 반영, 표/그래프 원자료는
검증 못 함(미검증)**.

같은 저자군(Park/Paik 계열, Hanyang Univ.)이 알칼리원(NaOH·KOH·TMAH)을 바꿔가며 유기첨가제
(polyacrylamide, PAM) 존재 하 poly 제거율을 비교했다:

- **TMAH**: poly 제거율이 가장 빠르게 피크(**2613 Å/min**)에 도달한 뒤 완만히 감소.
- **NaOH**: 피크 이후 하락폭이 가장 커서 **1165 Å/min** 감소(가장 급격한 붕괴).
- **KOH**: 제거율이 계속 증가하다가 0.3 wt%에서 포화(피크-후-하락 패턴이 없음).

세 알칼리원이 같은 OH⁻ 공급원인데도 농도-제거율 곡선의 모양(TMAH는 뾰족한 피크, KOH는
포화형)이 다르다는 것은 [[film-poly-si-alkaline-dissolution-ph-kinetics]] §4가 다룬
"OH⁻ 농도(=pH)만으로는 제거율을 설명 못 한다"는 결론과 같은 방향이다 — 양이온 종(Na⁺/K⁺ vs
TMA⁺)의 흡착·표면 상호작용 차이가 순수 pH 효과 위에 추가로 작용한다. 실무적으로 **TMAH는
금속이온(Na/K) 오염이 없어 게이트 CMP처럼 금속오염에 민감한 공정에 선호**된다는 점도 Lv1-2
§4에서 이미 확인한 논리와 일치한다.

## 4. 반대 방향 — 리플레이스먼트 게이트 CMP: US10119048B1의 Oxide:Poly 선택비 설계

특허 1차 출처: US Patent 10,119,048 B1, "Low-abrasive CMP slurry compositions with tunable
selectivity" (2018) — patents.google.com/patent/US10119048B1, 명세서 전문(Table C/D, Table 2/3)
직접 확인. 대상 공정은 §1 방향 ②(replacement/poly-open gate): 더미 poly-Si 게이트를 **보존**하며
위의 TEOS(ILD) 산화막을 깎아 게이트를 노출시켜야 한다 — 목표가 §2·§3과 **정반대**다.

명세서가 명시하는 설계 목표: "oxide:polysilicon removal rate ratio of at least 3:1, for example,
from 3:1 to 25:1 or, preferably, from 8:1 to 20:1"(과도한 선택비는 poly 게이트 아래 실리콘
손상·오버폴리시 마진 확보 실패로 이어지므로 **상한도 명시**한다는 점이 §2·§3의 "높을수록
좋다"는 암묵적 전제와 다르다). 20.7 kPa 조건 Table 3 실측값(모두 명세서 원문 수치):

| 예시 | 첨가제 | TEOS RR (Å/min) | Poly-Si RR (Å/min) | Oxide:Poly 선택비 |
|---|---|---|---|---|
| Ex.16 (비교예) | 아민 알콕실레이트 없음 | 3867 | 1721 | **2.25:1** |
| Ex.18 | 아민 알콕실레이트 0.0050 pbw | 3765 | 33 | **114:1** (명세서 우선범위 상한 초과) |
| Ex.19 | 아민 알콕실레이트 0.0050 pbw(다른 슬러리 조합) | 2065 | 115 | **17.96:1** (명세서 우선범위 8–20:1 내부) |

무첨가(Ex.16) 선택비 2.25:1은 §2 JKPS의 무첨가형 선택비(25–45:1 오더)보다 훨씬 낮다 — **같은
poly-Si·SiO₂ 재료쌍이라도 슬러리 화학(첨가제·pH·abrasive) 설계에 따라 선택비의 방향과 크기가
모두 뒤집힐 수 있다**는 것이 이 절의 핵심(§7 verify (B)). 아민 알콕실레이트는 poly-Si **와**
나이트라이드 제거율을 동시에 억제하면서 TEOS는 거의 그대로 두는 방식으로 작동한다고 명시돼
있는데, 이는 [[film-nitride-selectivity-ceria-chemistry]] §4의 "사이트-특이적 흡착제가 특정
표면만 포화시켜 선택적으로 차단한다"는 흡착 포화 프레임과 정성적으로 같은 그림이다(다만 이
특허는 흡착등온선 데이터를 직접 제시하지 않으므로 그 프레임과의 정합은 **유추이지 특허 자체의
주장은 아님 — 미검증**).

## 5. 선택비 → 공정 윈도우(오버폴리시 마진) 번역 — 이 노트의 유도(문헌 아님)

선택비가 실제로 의미하는 것은 "웨이퍼 두께 불균일(WIWNU)을 흡수하기 위한 오버폴리시 동안
얼마나 정지층(oxide 또는 poly)이 깎여나가는가"이다. 문헌(§2–4)이 선택비 수치는 주지만 이
번역식 자체를 제시하지는 않으므로, 아래는 **이 노트의 정의식**이며 문헌 주장이 아니다(정직성
표기: **미검증/이 노트의 모델**).

목표막(예: poly) 두께의 WIWNU를 두께 최대/최소 편차로 정의하면, 최박판이 목표 두께에 도달한
시점부터 최후판이 도달할 때까지의 **초과 시간(오버폴리시 시간)** 동안 정지층(oxide)이
`오버폴리시 시간 × oxide RR`만큼 깎인다. 선택비 S = poly RR / oxide RR가 클수록, 같은
오버폴리시 시간에 대해 oxide RR = poly RR / S가 작아지므로 oxide 손실이 줄어든다(§7 verify
(D)에서 가상 예시로 수치 확인 — 실측 WIWNU·목표두께 문헌값은 이번 조사에서 확보하지 못해
예시 숫자만 사용).

## 6. Seidel(1990) 활성화에너지와 CMP 선택비의 자릿수 괴리 — 습식식각 ≠ CMP

[[film-poly-si-alkaline-dissolution-ph-kinetics]] §3이 인용한 Seidel(1990, DOI:
10.1149/1.2086277)의 활성화에너지는 Si ⟨100⟩ 0.59 eV, SiO₂ 0.85 eV다. 이 차이(0.26 eV)만으로
Arrhenius 비를 상온(295 K)에서 계산하면 **순수 습식식각 Si:SiO₂ 선택비는 오더 ~2.8×10⁴:1**로
예측된다(§7 verify (C)) — 이는 §2·§4에서 실측한 **CMP 선택비(25–114:1)보다 200배 이상 크다**.
이 괴리는 Lv1-2 §8이 이미 지적한 한계, 즉 **"Seidel은 정적 습식식각, CMP는 여기에 기계적
마모가 곱해지는 동적 과정"**이라는 구도로 설명된다 — 산화막은 화학적으로는 거의 안 깎이지만
연마입자의 기계적 마모가 화학적 식각보다 훨씬 빠르게 산화막을 벗겨내므로(§2에서 본 "산화막
제거율이 TMAH 농도와 무관하게 40–60 Å/min 고정"이 이 기계-지배 레짐의 증거), 화학이 부여하는
거대한 잠재 선택비가 CMP 실측에서는 크게 압축된다. **이 압축의 정량 메커니즘(마모 모델
계수)은 이번 조사에서 확보하지 못했다 — 정성적 방향만 확인, 압축률 자체는 확인하지 못했다.**

## 7. Python 재현 & 문헌 대조

**재현 요약(US10119048B1의 20.7 kPa, Seidel 295 K 조건 다수 대조)**: (i) Park 2007(DOI
10.3938/jkps.51.214)의 TMAH 농도별 선택비 25:1→45:1(피크)→33:1과
산화막 제거율 40–60 Å/min 고정을 재현·역산 대조, (ii) US10119048B1 Table 3 실측치로 무첨가
2.25:1 vs 첨가 17.96–114:1 선택비를 계산해 명세서 우선범위(8–20:1)와 대조, (iii) Seidel(1990,
DOI 10.1149/1.2086277) 활성화에너지로 예측한 습식식각 선택비(~2.8×10⁴:1)가 CMP 실측 최대치
(114:1)보다 200배 이상 크다는 자릿수 괴리를 계산, (iv) 선택비→오버폴리시 산화막손실 번역식을
가상 예시로 수치 확인(문헌값 아님, 이 노트의 모델) — 아래 4블록 모두 PASS.

```python verify
# ── (A) Park 2007 (DOI 10.3938/jkps.51.214): TMAH 농도별 poly:oxide 선택비 피크 & oxide RR 고정 ──
sel_low, sel_peak, sel_high = 25.0, 45.0, 33.0   # 원문 결론부 명시 수치 (5.3 wt% abrasive 기준)
assert sel_low < sel_peak and sel_peak > sel_high, "TMAH 농도에 대해 선택비가 피크형(비단조)이어야 함"
assert 20 <= sel_low <= 30 and 40 <= sel_peak <= 50 and 28 <= sel_high <= 38

oxide_rr_min, oxide_rr_max = 40.0, 60.0   # A/min, 원문: "maintained at 40 to 60 A/min"
poly_rr_at_peak_low = sel_peak * oxide_rr_min
poly_rr_at_peak_high = sel_peak * oxide_rr_max
print(f"Park 2007: 선택비 {sel_low:.0f}->{sel_peak:.0f}(피크)->{sel_high:.0f}:1, "
      f"oxide RR 40-60 A/min 고정 구간에서 역산한 피크시 poly RR 범위 "
      f"{poly_rr_at_peak_low:.0f}-{poly_rr_at_peak_high:.0f} A/min")
assert 1500 < poly_rr_at_peak_low < poly_rr_at_peak_high < 3000

contact_min, contact_high = 41.0, 51.5   # deg, TMAH 0.12 wt%에서 최소 -> 0.52 wt%에서 재상승 (Fig.8)
assert contact_min < contact_high
print(f"접촉각 {contact_min}->{contact_high} deg — poly 제거율 곡선의 거울상(친수성 최대점=제거율 근접 피크)")

# ── (B) US10119048B1 Table 3 (20.7 kPa): 무첨가 vs 아민알콕실레이트 첨가 선택비 ──
TEOS_16, poly_16 = 3867.0, 1721.0     # Ex.16, 비교예(첨가제 없음)
TEOS_18, poly_18 = 3765.0, 33.0       # Ex.18, 아민알콕실레이트 0.0050 pbw
TEOS_19, poly_19 = 2065.0, 115.0      # Ex.19, 아민알콕실레이트 0.0050 pbw(다른 실리카 조합)
sel_16, sel_18, sel_19 = TEOS_16/poly_16, TEOS_18/poly_18, TEOS_19/poly_19
print(f"US10119048B1: Ex16(무첨가) {sel_16:.2f}:1, Ex18 {sel_18:.1f}:1, Ex19 {sel_19:.1f}:1")
assert 2.0 < sel_16 < 2.5, "무첨가 선택비가 명세서 배경기술 수준(약 2:1 오더)과 맞아야 함"
assert sel_18 > 100, "고농도 첨가 예시가 명세서 우선범위 상한을 넘는 극값이어야 함"
claim_lo, claim_hi = 8.0, 20.0        # 명세서 "preferably from 8:1 to 20:1"
assert claim_lo <= sel_19 <= claim_hi, "Ex19 선택비가 명세서 우선범위(8-20:1) 안에 있어야 함"

# ── (C) Seidel(1990) 활성화에너지가 예측하는 순수 습식식각 선택비 vs CMP 실측 자릿수 괴리 ──
import numpy as np
kB = 8.617333e-5  # eV/K
Ea_Si, Ea_SiO2 = 0.59, 0.85   # eV, Seidel(1990) DOI 10.1149/1.2086277 (Lv1-2 §3에서 재사용)
T = 295.0
kT = kB * T
intrinsic_ratio = np.exp((Ea_SiO2 - Ea_Si) / kT)
print(f"Seidel 활성화에너지차가 예측하는 상온 습식식각 Si:SiO2 선택비 ~{intrinsic_ratio:.0f}:1")
assert intrinsic_ratio > 1000
cmp_sel_max = max(sel_peak, sel_18)   # 이 노트에서 확보한 CMP 실측 최대 선택비
assert cmp_sel_max < intrinsic_ratio / 10, "CMP 실측 선택비가 화학적 잠재 선택비보다 훨씬 압축돼야 함"
print(f"CMP 실측 최대선택비 {cmp_sel_max:.0f}:1 은 화학적 잠재치보다 {intrinsic_ratio/cmp_sel_max:.0f}배 작다"
      f" — 기계적 마모가 산화막 제거를 지배해 선택비를 압축한다는 정성 해석(압축률 자체는 확인 못 함)")

# ── (D) 선택비 -> 오버폴리시 산화막 손실 번역식 (가상 예시, 문헌값 아님 — 이 노트의 모델) ──
poly_target_A = 2000.0   # A, 가상 예시 목표 poly 두께
WIWNU = 0.10              # 10%, 가상 예시 두께 불균일도 (=(최대-최소)/평균)
poly_RR = 2000.0          # A/min, 가상 예시(오더만 참고 - Park 2007 피크 부근 값과 비슷한 크기로 설정)
S = sel_peak              # Park 2007 피크 선택비 45:1 재사용
oxide_RR = poly_RR / S
t_thin = poly_target_A * (1 - WIWNU/2) / poly_RR
t_thick = poly_target_A * (1 + WIWNU/2) / poly_RR
overpolish_time = t_thick - t_thin
oxide_loss = oxide_RR * overpolish_time
print(f"[가상 예시, 확인 못 함] poly WIWNU {WIWNU*100:.0f}%, 선택비 {S:.0f}:1 가정 시 "
      f"오버폴리시 {overpolish_time*60:.1f}s 동안 예상 oxide 손실 {oxide_loss:.2f} A")
assert oxide_loss < poly_target_A * WIWNU, "선택비가 유한하면 oxide 손실이 poly 불균일량보다 작아야 함(선택비 존재의의)"
```

## 8. 한계 / 미확인 사항

- **Hwang/Kang et al.(2008)은 확대초록만 확보**했다(ECS Transactions 전체 논문 DOI
  10.1149/1.2912980은 미확보). §3의 정량치(2613 Å/min, 1165 Å/min 하락폭)는 초록 수준
  서술이며, 그래프 원자료·오차범위는 검증하지 못했다 — **미검증**.
- **§4 특허의 "사이트-특이적 흡착으로 poly·나이트라이드만 억제"라는 해석**은 명세서 서술을
  [[film-nitride-selectivity-ceria-chemistry]]의 흡착 포화 프레임에 빗댄 **이 노트의 유추**이며,
  특허 자체가 흡착등온선 데이터로 이를 직접 증명하지는 않는다 — **미검증**.
- **§5의 오버폴리시-산화막손실 번역식은 이 노트가 만든 모델**이지 문헌에서 가져온 식이 아니다.
  §7 verify (D)의 목표두께(2000 Å)·WIWNU(10%)·poly RR(2000 Å/min)은 모두 **가상 예시**이며,
  실제 게이트 CMP 공정의 WIWNU 스펙·목표 두께는 이번 조사에서 1차 문헌으로 확보하지 못했다.
- **§6의 "선택비 압축률"은 정성적 해석에 그친다.** 화학적 잠재 선택비(~2.8×10⁴:1)와 CMP 실측
  (25–114:1) 사이 200배 이상의 괴리를 "기계적 마모 지배"로 설명했지만, 이를 정량 모델(예:
  Preston형 기계항 vs Seidel형 화학항의 가중합)로 분리 검증하지는 못했다 — [[../cmp/preston-luo-dornfeld-mrr]]의
  Kp 프레임과 연결할 후속 과제로 남긴다.
- **§4 Table의 선택비는 20.7 kPa 한 압력 조건만 인용**했다. 명세서는 6.9 kPa 데이터도 갖고
  있으나(예: Ex.18 6.9 kPa에서 선택비 ~87:1, Ex.19 ~70:1) 압력 의존성 자체를 이 노트에서
  정량 분석하지는 않았다 — 압력 의존 선택비 설계는 확인하지 못함·후속 과제.
## 9. 이 에이전트의 결론 (모델링 관점)

1. **poly:oxide 선택비는 "선택비 하나"가 아니라 방향과 화학 설계에 따라 자릿수와 부호가 모두
   바뀌는 손잡이다.** §2·§3(TMAH계, poly가 빠름, 25–45:1)과 §4(아민알콕실레이트계, oxide가
   빠름, 2.25→17–114:1)는 같은 poly-Si/SiO₂ 재료쌍에서 정반대 방향·다른 자릿수를 낸다 —
   [[film-nitride-selectivity-ceria-chemistry]] §1의 "선택비는 하나의 숫자가 아니라 위계"라는
   결론이 poly:oxide 계에도 그대로 적용된다.
2. **Tier2 구현 시 Kp_oxide/Kp_poly 비율을 슬러리 화학(알칼리 종류·첨가제 유무·방향)에 따라
   스위칭 가능한 파라미터로 둬야 한다** — 단일 상수로 고정하면 §2(25–45:1)와 §4(2.25:1 또는
   17–114:1)를 동시에 표현할 수 없다.
3. **화학적 잠재 선택비(Seidel Ea 기반, ~10⁴ 오더)와 CMP 실측 선택비(10¹–10² 오더) 사이의 압축**은
   기계적 마모항이 화학적 선택비를 깎아먹는 정도를 정량화해야 메울 수 있는 간극이다 — 이는
   poly-Si Kp·화학 용해율 파라미터 재현을 다루는 Lv3-2(커리큘럼 예정)의 핵심 과제로 넘긴다.

## 10. 자기시험
→ [[../../agents/film-poly-si/EXAMS.md]] Lv2-1 문항 참조.
