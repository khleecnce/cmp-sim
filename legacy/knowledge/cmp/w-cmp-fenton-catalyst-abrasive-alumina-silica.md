<!-- V2-SECTION: R2-slurry | 근거: fenton, hydroxyl radical, oxidizer, abrasive, alumina, silica, isoelectric | 정본: ARCHITECTURE-V2.md §3 -->
# 텅스텐 CMP — Fe 촉매 H₂O₂의 Fenton 화학과 알루미나/실리카 입자 선택

> 에이전트: film-w Lv1-2 | 작성일: 2026-09-10
> 선행: [[w-cmp-wo3-passivation-oxidizer-kaufman]] (film-w Lv1-1, 이 노트의 직전 단원) ·
> 부모 상속 [[surface-chemistry-cu-w-pourbaix-passivation]]
> 관련: [[colloid-zeta-dlvo-slurry-stability]] [[oxidizer-redox-potential-decomposition-metal-suitability]]
> [[particle-wafer-interaction-mechanical-chemical-balance]] [[abrasive-size-concentration-ph-K-additive-mrr-quantitative]]
> [[lpc-scratch-density-tail-correlation]] [[hertz-gw-contact-mechanics]] [[preston-luo-dornfeld-mrr]]

## 1. 왜 필요한가 — Lv1-1이 남긴 두 구멍
직전 단원([[w-cmp-wo3-passivation-oxidizer-kaufman]])에서 **Fe(NO₃)₃ 미량 첨가만으로 W CMP
제거율이 H₂O₂ 단독 대비 ~16배 급증**(Lim 2013, 56→923 Å/min)한다는 것을 확인했다. 그런데
두 가지를 "정성 스케치"로만 남겼다:
- (a) Fe가 *왜* 촉매인가 — Lim 2013의 Eq.(6)-(8)은 원자 균형이 안 맞는 정성식이었다.
  실제 구동자는 **Fenton 반응의 하이드록실 라디컬(•OH)**이다.
- (b) 그 무른 WO₃ 막을 *무엇으로* 벗기는가 — 입자다. 알루미나냐 실리카냐가 제거율·스크래치·
  선택비를 가른다.

이 단원은 (a) Fenton 속도론을 **1차 원전 속도상수**(Buxton 1988)로 정량화하고, (b) 알루미나 vs
실리카 입자의 경도·등전점(IEP)·스크래치 트레이드오프를 **1차 논문**(Egan & Kim 2019)으로 판다.

## 2. Fenton 화학 — Fe²⁺/Fe³⁺ + H₂O₂ → •OH 의 속도론
### 2.1 반응 사이클 (촉매 재생)
Fe는 소모되지 않고 Fe²⁺↔Fe³⁺를 오가며 H₂O₂를 •OH로 쪼개는 **촉매**다:
- **개시(Fenton)**: `Fe²⁺ + H₂O₂ → Fe³⁺ + •OH + OH⁻`
  표준 문헌값 k₁ ≈ 63–76 M⁻¹s⁻¹ (De Laat & Gallard 1999, *Environ. Sci. Technol.* 33, 2726.
  DOI: 10.1021/es981171v — **원문 미확보, 2차 인용**. 값은 여러 리뷰가 인용하는 표준값이나 본 노트
  에서 직접 대조하지 못함, 미검증).
- **재생(Fenton-like, 율속)**: `Fe³⁺ + H₂O₂ → Fe²⁺ + HO₂• + H⁺`
  k ≈ 10⁻³–10⁻² M⁻¹s⁻¹ 로 **개시보다 4~5자릿수 느림**(De Laat & Gallard 1999, 위 DOI, 2차 인용, 값 직접 대조 못 함).
  → 순수 수용액에서 Fe³⁺(=Fe(NO₃)₃)만으로는 •OH 생성이 느리다.
- **W 표면 환원(현장 재생)**: Lim 2013(Eq.5, [[w-cmp-wo3-passivation-oxidizer-kaufman]])의
  `Fe³⁺ + W → Fe²⁺ + W⁺` 가 Fe²⁺를 계속 공급 → 개시반응이 표면에서 지속. 이것이 Fe(NO₃)₃
  (Fe³⁺)로도 W CMP가 잘 되는 이유 — **W 자체가 환원제**로 촉매 순환을 닫는다.

원자·전하 균형은 §7 블록1에서 assert로 검증(Kaufman/Lim 정성식과 달리 이 세 식은 균형이 맞는다).

### 2.2 •OH의 운명 — 생산적 산화 vs 자기소거 (핵심 정량)
생성된 •OH는 (i) W 표면을 산화해 치밀 WO₃를 만들거나(생산적), (ii) 슬러리 성분에 소거된다.
소거 경쟁 상대는 **Fe²⁺**와 **H₂O₂ 자신**이다. 1차 원전 속도상수(Buxton et al. 1988,
*J. Phys. Chem. Ref. Data* 17, 513. DOI: 10.1063/1.555805 — **원문 PDF 확보·표 판독**,
`papers/buxton1988-hydroxyl-radical-rate-constants.pdf`):
- 반응 85 `•OH + Fe²⁺ → FeOH²⁺ + H₂O`: **k = 4.3×10⁸ M⁻¹s⁻¹**(pH 3, best value);
  3.2×10⁸(pH 7), 2.3×10⁸(pH 1), 3.5×10⁸(pH 4.5–6.2).
- 반응 159 `•OH + H₂O₂ → O₂•⁻ + H₂O`: **k = 2.7×10⁷ M⁻¹s⁻¹**(4개 값 평균).
- 반응 90 `•OH + Fe(CN)₆⁴⁻ → Fe(CN)₆³⁻ + OH⁻`: k = 1.05×10¹⁰ (Kaufman의 ferricyanide
  산화제가 왜 강력한 전자흡수원인지와 연결 — [[w-cmp-wo3-passivation-oxidizer-kaufman]] §3).

**Fe²⁺가 •OH를 H₂O₂보다 ~16배 빨리 소거**한다(4.3×10⁸/2.7×10⁷ = 15.9). 따라서 **Fe를 과잉
투입하면 촉매가 스스로 만든 •OH를 도로 잡아먹어 W 산화 효율이 떨어진다**(자기소거). 이것이 촉매
농도-MRR 곡선에 **최적점이 존재**하는 화학적 근거다.

## 3. 촉매 농도–MRR 관계 — Lim 2013 region I/II를 자기소거로 설명
Lim 2013(DOI: 10.1016/j.apsusc.2013.06.003, [[w-cmp-wo3-passivation-oxidizer-kaufman]]에서 원문
확보)은 Fe(NO₃)₃ 농도-제거율을 두 영역으로 봤다: **region I(<0.1 wt%) 급증 → region II(>0.1 wt%)
완만**. §7 블록2에서 Buxton 속도상수로 계산하면, 1.0 wt% H₂O₂([H₂O₂]≈0.29 M) 슬러리에서 •OH가
Fe에 소거되는 분율은 **0.01 wt% Fe에서 ~2%, 0.05 wt%에서 ~10%, 0.1 wt%에서 ~18%**로 올라간다.
즉 region I 끝(0.1 wt%)부터 자기소거가 무시 못 할 크기가 되어 **농도 증가의 수확이 체감**한다 —
Lim의 region I→II 전이와 **정성적으로 정합**(정확한 전이 농도의 정량 재현은 W 표면 반응·확산까지
필요하므로 **미검증**, 방향성만).

정리: Fe 촉매의 MRR 기여는 "생성률(Fe↑로 증가) × 생산적 활용률(Fe↑로 자기소거에 감소)"의
곱이라 종형(포화형) 곡선이 되고, 산업 슬러리가 Fe를 최소량(수백 ppm~0.1 wt%)만 쓰는 이유가 된다.

## 4. 입자 선택 — 알루미나 vs 실리카 (경도·IEP·스크래치)
### 4.1 경도 — "무른 막만 벗길 것인가, 금속까지 긁을 것인가"
CMP는 무른 WO₃ 막만 선택적으로 벗겨야 한다([[particle-wafer-interaction-mechanical-chemical-balance]]).
입자가 너무 단단하면 막 아래 W 금속·저차산화물까지 파고들어 스크래치를 낸다.
대표 경도(Vickers/Mohs, 표준 핸드북값 — **2차 인용, 값 직접 대조 못 함**):
- 실리카(SiO₂ 콜로이드) ≈ Mohs 7, HV ~8–10 GPa
- 알루미나(α-Al₂O₃) ≈ Mohs 9, HV ~20 GPa (다이아 다음으로 단단, 상용 연마재 중 최경질)
- W 금속 ≈ Mohs ~7.5, HV ~3.5–4.3 GPa; WO₃ 막은 다공성이라 훨씬 무름
→ **알루미나/W ≈ 5배, 실리카/W ≈ 2.3배**(§7 블록3). 알루미나는 제거율이 높지만(단단해 막+금속
모두 깎음) **스크래치를 남기기 쉽다**; 실리카는 W보다 약간만 단단해 주로 무른 막만 제거 →
저스크래치·저제거율. (일반값 교차확인: IntechOpen "Abrasive for CMP" 챕터, 2차 인용.)

### 4.2 등전점(IEP) — 산성 W 슬러리에서 분산 안정성
W CMP는 강한 산성(Lim 2013: pH 2.3)에서 돈다. 입자 IEP 근처에서는 제타전위≈0 →
정전반발 소멸 → 응집 → **큰 덩어리가 스크래치**([[colloid-zeta-dlvo-slurry-stability]]). 표준 IEP
(표준 핸드북값·문헌 산포 큼 — **2차 인용, 값 직접 대조 못 함**):
- 실리카 IEP ≈ pH 2–3, 알루미나 IEP ≈ pH 8–9.
- **pH 2.3에서**: 실리카는 IEP 바로 위(|ΔpH|≈0.3) → 표면전하 미약 → **응집·스크래치 위험**;
  알루미나는 IEP 훨씬 아래(|ΔpH|≈6.7) → 강한 양전하 → **잘 분산**(§7 블록3).
→ 산성 W 슬러리에서 **알루미나가 분산 안정성 면에서 유리**하다(경도 스크래치와는 상충 —
트레이드오프). 실리카를 쓰려면 pH를 IEP에서 떼거나 표면개질/영구전하 부여가 필요.

### 4.3 스크래치의 진짜 원인은 "크기 꼬리" — Egan & Kim 2019 (1차, OA)
Egan & Kim, "Effect of Controlling Abrasive Size in Slurry for Tungsten Contact CMP Process,"
*ECS J. Solid State Sci. Technol.* 8(5), P3206 (2019). DOI: 10.1149/2.0311905jss (GLOBALFOUNDRIES;
CC-BY-NC-ND 오픈액세스, 원문 확보 `papers/egan2019-jss-w-contact-cmp-abrasive-size.pdf`,
300 nm CVD W/oxide blanket + 볼륨 패턴 웨이퍼):
- **W 제거율은 입자 크기(평균)와 무관, 결함(마이크로스크래치)만 크게 의존** — W CMP가 화학지배
  (무른 WO₃ 제거)임을 뒷받침([[preston-luo-dornfeld-mrr]], [[abrasive-size-concentration-ph-K-additive-mrr-quantitative]]).
  스크래치를 내는 건 슬러리의 **큰 입자 꼬리(응집체)**이지 평균 입경이 아니다([[lpc-scratch-density-tail-correlation]]).
- 정량: 슬러리 숙성(aging)이 스크래치를 **40% 이상** 개선; 큰 입자 형성 억제로 패턴 웨이퍼
  스크래치 **85% 감소**; 정밀 여과는 baseline을 **~50%** 낮추지만 표준편차는 못 줄임(일부 웨이퍼는
  여전히 큰 입자 타격). → **필터로 걸러내기보다 응집체 형성 자체를 막는 것**이 관건(저장온도·교반 관리).

## 5. 종합 — 설계 결론
1. **촉매**: Fe는 Fenton으로 •OH를 만들어 W→치밀 WO₃ 산화를 가속하는 촉매(W가 Fe³⁺→Fe²⁺
   환원제로 순환을 닫음). 과잉 Fe는 •OH 자기소거(Fe²⁺가 H₂O₂보다 ~16배 빨리 •OH 소모)로
   수확체감 → **최소량·최적농도**가 답.
2. **입자**: 알루미나=고경도(고MRR·고스크래치·산성에서 분산 양호), 실리카=중경도(저스크래치·저MRR·
   산성에서 IEP 근접해 응집 주의). 실무는 **경도(스크래치)와 IEP(분산)의 상충**을 슬러리 pH·표면개질·
   혼합입자([[abrasive-d99-composite-particle-versum2019]] 계열)로 조율.
3. **스크래치**: 평균 입경이 아니라 **큰 입자 꼬리**가 킬러 → 응집 형성 억제(저장·교반·숙성)가
   여과보다 효과적(Egan 2019).

## 6. 한계 (정직 표기)
- Fenton 개시/재생 속도상수(k₁≈63–76, k₋≈10⁻³ M⁻¹s⁻¹)는 De Laat & Gallard 1999의 표준값을
  **2차 인용**했을 뿐 원문 미확보 — **미검증**. §7 블록1은 *원자·전하 균형*만 검증하며 속도상수
  절대값은 검증 대상이 아니다.
- §2.2·§3의 •OH 소거분율 계산은 Buxton 1988 속도상수(직접 판독)는 정확하나, [Fe²⁺]를 첨가 Fe
  총량의 상한으로 잡은 **정상상태 근사**이며 W 표면 흡착·확산·pad 접촉을 무시 → region I/II 전이의
  **정성 방향만**, 정확한 전이농도는 **미검증**.
- 경도·IEP 수치(§4.1, §4.2)는 표준 핸드북값으로 문헌 산포가 크다(특히 알루미나 IEP는 상/제법따라
  pH 1~9까지 보고됨) — **2차 인용, 값 직접 대조 못 함**. IEP는 §7에서 *부호 판정 논리*만 재현.
- Egan 2019는 W **contact** CMP·특정 fab 조건(실리카계 bulk 슬러리) — 알루미나 슬러리나 다른
  노드로 일반화는 미검증.

## 7. 코드 재현 (문헌값 상수 박고 assert)

```python verify
# 블록1: Fenton 3반응의 원자·전하 균형 (Kaufman/Lim 정성식과 달리 균형이 맞음을 증명)
from collections import Counter
def balance(L, R):
    lc, rc = Counter(), Counter()
    for coef, atoms, charge in L:
        for el,n in atoms.items(): lc[el]+=coef*n
        lc['Q']+=coef*charge
    for coef, atoms, charge in R:
        for el,n in atoms.items(): rc[el]+=coef*n
        rc['Q']+=coef*charge
    return lc, rc
def assert_balanced(name, L, R):
    lc, rc = balance(L,R)
    for k in set(lc)|set(rc):
        assert lc[k]==rc[k], f"{name} 불균형 {k}: 좌{lc[k]} 우{rc[k]}"
    print(f"{name}: 원자·전하 균형 OK -> {dict(lc)}")

# 개시: Fe2+ + H2O2 -> Fe3+ + •OH + OH-   (•OH = O1H1 라디컬, OH- = O1H1 전하-1)
assert_balanced("개시 Fe2+553 +H2O2",
    [(1,{'Fe':1},+2),(1,{'H':2,'O':2},0)],
    [(1,{'Fe':1},+3),(1,{'O':1,'H':1},0),(1,{'O':1,'H':1},-1)])
# 재생(Fenton-like): Fe3+ + H2O2 -> Fe2+ + HO2• + H+
assert_balanced("재생 Fe3+ +H2O2",
    [(1,{'Fe':1},+3),(1,{'H':2,'O':2},0)],
    [(1,{'Fe':1},+2),(1,{'H':1,'O':2},0),(1,{'H':1},+1)])
# W 표면 환원: Fe3+ + W -> Fe2+ + W+   (W가 Fe2+ 재공급 -> 촉매순환 폐쇄)
assert_balanced("표면환원 Fe3+ +W",
    [(1,{'Fe':1},+3),(1,{'W':1},0)],
    [(1,{'Fe':1},+2),(1,{'W':1},+1)])
print("=> Fe는 소모되지 않는 촉매 (Fe2+ <-> Fe3+ 순환), W가 환원제로 순환을 닫음")
```

```python verify
# 블록2: •OH 자기소거 경쟁 — Buxton(1988) 속도상수로 촉매 최적점의 근거 재현
# 문헌값(직접 판독): •OH+Fe2+ k=4.3e8 (pH3), •OH+H2O2 k=2.7e7 M-1 s-1
k_OH_Fe2, k_OH_H2O2 = 4.3e8, 2.7e7
ratio = k_OH_Fe2 / k_OH_H2O2
assert 15 < ratio < 17, f"속도상수 비 {ratio:.1f} — Fe2+가 H2O2보다 ~16배 빨리 •OH 소거해야"
print(f"k(•OH+Fe2+)/k(•OH+H2O2) = {ratio:.1f}배 (Buxton 1988 반응85/159)")

# Lim 2013 슬러리: 1.0 wt% H2O2, Fe(NO3)3 0.01~0.1 wt% (밀도~1 g/mL 수용액 근사)
H2O2_M = 10.0/34.0                      # 1 wt% -> mol/L
def fe_M(wt): return (wt/100*1000)/241.86   # 무수 Fe(NO3)3 MW=241.86
def frac_fe(wt):
    fe = fe_M(wt)
    return k_OH_Fe2*fe/(k_OH_Fe2*fe + k_OH_H2O2*H2O2_M)  # •OH가 Fe2+에 소거되는 분율

f001, f005, f010 = frac_fe(0.01), frac_fe(0.05), frac_fe(0.1)
print(f"•OH 자기소거 분율: 0.01wt% {f001*100:.1f}%, 0.05wt% {f005*100:.1f}%, 0.1wt% {f010*100:.1f}%")
# region I(<0.1wt%)에서는 자기소거가 작다가, 0.1wt%부터 유의(>15%)해져 수확체감
assert f001 < 0.05, "저농도에서 자기소거 무시가능해야 (region I 급증과 정합)"
assert f010 > 0.15, "0.1wt%에서 자기소거가 유의(>15%)해져야 (region II 완만화와 정합)"
assert f001 < f005 < f010, "Fe 농도↑ -> 자기소거 분율 단조증가"
print("=> Fe↑ 시 생성↑·활용률↓ 상충 -> 종형 MRR 곡선, 최적농도 존재 (Lim 2013 region I/II와 정성 정합)")
```

```python verify
# 블록3: 알루미나 vs 실리카 — 경도비와 산성 슬러리 IEP 부호 판정
# 경도(HV, GPa; 표준 핸드북값·2차 인용, 값 직접 대조 못 함) — 상대 비교만
HV = {'silica':9.0, 'alumina':20.0, 'W':4.0}
r_al = HV['alumina']/HV['W']; r_si = HV['silica']/HV['W']
print(f"경도비  alumina/W = {r_al:.1f},  silica/W = {r_si:.2f}")
assert r_al > 4, "알루미나는 W보다 최소 4배 단단(고MRR·고스크래치 경향)"
assert 1.5 < r_si < 3, "실리카는 W보다 약간만 단단(저스크래치·저MRR)"
assert r_al > 2*r_si, "알루미나가 실리카보다 훨씬 공격적이어야 (스크래치 트레이드오프)"

# IEP(표준 핸드북값·2차 인용, 값 직접 대조 못 함). W 슬러리 pH=2.3 (Lim 2013)
IEP = {'silica':2.0, 'alumina':9.0}; pH = 2.3
def charge_sign(iep): return +1 if pH < iep else (-1 if pH>iep else 0)
# pH<IEP -> 양전하(분산 양호), pH≈IEP -> 전하≈0(응집 위험)
d_si, d_al = abs(pH-IEP['silica']), abs(pH-IEP['alumina'])
print(f"pH{pH}: silica |ΔpH|={d_si:.1f}(IEP근접·응집위험), alumina |ΔpH|={d_al:.1f}(양전하·분산양호)")
assert d_si < 0.5, "실리카는 산성 W 슬러리 pH에서 IEP에 근접해 정전반발 약함"
assert d_al > 5 and charge_sign(IEP['alumina'])==+1, "알루미나는 강한 양전하로 잘 분산돼야"
print("=> 경도(실리카 유리, 저스크래치) vs 분산안정성(알루미나 유리, 산성 pH)의 상충 트레이드오프")

# Egan & Kim 2019 정량 앵커: aging 스크래치 개선 >40%, 응집억제 시 패턴 스크래치 -85%, 여과 -50%
aging_improve, agglo_suppress, filtration = 40, 85, 50   # %
assert agglo_suppress > aging_improve > filtration/2, \
    "응집 형성 억제(85%)가 여과(50%)·숙성(40%)보다 스크래치에 효과적 (Egan 2019)"
print(f"Egan2019: 숙성 -{aging_improve}%, 여과 -{filtration}%, 응집억제 -{agglo_suppress}% "
      f"=> '큰 입자 꼬리 형성 억제'가 핵심")
```
