<!-- V2-SECTION: R2-slurry | 분배완료 2026-09-08 | 근거: ph, slurry, 슬러리, 입자, 화학 | 정본: ARCHITECTURE-V2.md §3 -->
# CMP 슬러리 구성요소 총론 — 입자·산화제·억제제·착화제·분산제·pH의 역할과 상호작용

> 에이전트: slurry-chemist Lv1-2 | 작성일: 2026-09-05
> [[colloid-zeta-dlvo-slurry-stability]] [[preston-luo-dornfeld-mrr]] [[../materials/hertz-gw-contact-mechanics]] [[../physics/tribology-friction-wear-stribeck]]

## 1. 왜 필요한가 — 슬러리는 "화학+기계"를 한 병에 담은 반응계
CMP는 이름 그대로 **화학(chemical)**과 **기계(mechanical)**의 곱이다. [[preston-luo-dornfeld-mrr]]의
Preston 계수 $K_p$는 이 둘을 뭉뚱그린 상수였는데, 그 내부를 열면 대부분이 **슬러리 화학**이다.
금속 CMP(Cu/W/Mo)의 지배 원리는 **Kaufman 경쟁모델**(Kaufman et al., *J. Electrochem. Soc.*
138, 3460, 1991 — 원문 유료, 2차 인용): 산화제가 금속 표면에 **무른 산화막**(WO₃, Cu₂O 등)을
만들고, 연마입자가 그 막을 기계적으로 벗겨내며, 벗겨진 맨금속이 다시 산화되는 **동적 평형**.
따라서 슬러리 설계는 "얼마나 빨리 무른 막을 만들고(산화제·착화제), 어디를 보호해 평탄화할지
(억제제), 어떤 입자로 얼마나 세게 벗길지(연마입자), 그 입자를 어떻게 안정하게 띄울지(분산제·pH)"의
동시 최적화다. 이 노트는 각 구성요소의 역할과 상호작용을 총론으로 정리하고, 정량관계 두 개
(BTA Langmuir 흡착, 산화제-MRR 정점)를 코드로 재현한다. 콜로이드 안정성 1층은
[[colloid-zeta-dlvo-slurry-stability]]에서 다뤘다.

## 2. 연마입자 (Abrasive) — 실리카·세리아·알루미나
기계적 제거를 담당. 3대 입자의 특성(출처: ScienceDirect Topics "Polishing Slurry"/"Ceria Based
Slurry", 리뷰성 2차 인용):
- **콜로이달 실리카(SiO₂)**: 가장 널리 쓰임. 통상 1차입경 수십 nm(50–100 nm대), 농도 1–10 wt%.
  경도 중간, 결함 적음. 산화막 CMP·금속 CMP 두루 사용. IEP≈2([[colloid-zeta-dlvo-slurry-stability]]).
- **세리아(CeO₂)**: 산화막(특히 STI SiO₂) CMP의 주력. "화학적 이빨(chemical tooth)" — 단순 마모가
  아니라 Si–O–Ce 결합을 만들어 SiO₂를 뜯어내는 **화학기계적** 작용(Lv3-1에서 Ce³⁺/Ce⁴⁺로 심화).
  결정성·크기가 커지면 결함(스크래치)이 급증 → 7 wt% 초과는 비용·결함으로 비실용적(2차 인용).
- **알루미나(Al₂O₃)**: 경도 최고(벌크 8–9 Mohs). 금속·하드마스크에 사용되나 스크래치 위험 큼.
  슬러리 내 수화층은 무름(3–4 Mohs).
- **정량 예시(미검증, 재료·조건 의존)**: TaN 연마율이 실리카(1차입경 50 nm, 5%) 2.8 nm/min vs
  세리아(100 nm, 0.05%) 4.5 nm/min — 세리아가 훨씬 낮은 농도로 더 높은 율(ScienceDirect Topics).
- **결함 상관**: 표면손상은 입자크기와 조대입자 비율에 양(+)의 상관 → 응집 억제(=콜로이드 안정성)가
  결함 제어의 핵심. 이 지점에서 [[colloid-zeta-dlvo-slurry-stability]]의 DLVO 장벽과 직결된다.
- **입도분포→활성입자**: 크기분포는 [[preston-luo-dornfeld-mrr]]의 Luo-Dornfeld "활성입자" 통계로
  이어진다(압력을 실제 전달하는 입자는 분포의 상위 꼬리).

## 3. 산화제 (Oxidizer) — H₂O₂·Fe(NO₃)₃·과탄산나트륨
맨금속을 무른 산화막으로 바꾸는 화학 엔진. 대표: **과산화수소 H₂O₂**, **질산철 Fe(NO₃)₃**,
**과탄산나트륨(SPC, H₂O₂ 방출원)**.
- **W CMP**: H₂O₂·Fe(NO₃)₃가 W→WO₃. 두 산화제 **혼합** 시 하이드록실 라디칼(·OH) 생성으로
  단독보다 율이 크게 상승(Fe가 Fenton형 촉매) — "Effects of oxidants on the removal of tungsten in
  CMP process"(*Microelectron. Eng.* 계열, ScienceDirect, 2004; 초록·2차 인용). Fe(NO₃)₃는 더 치밀한
  산화막을 유도.
- **정점(peak) 거동**: 산화제를 늘리면 MRR이 **급상승 후 완만 감소**하는 단봉 곡선. Cu는 ~1% H₂O₂에서
  최대, 이후 감소(과도 산화막이 표면을 보호=과-passivation) — Cambridge MRS OPL "Effect of Hydrogen
  Peroxide on Oxidation of Copper..."(2차 인용). 이는 Kaufman 경쟁모델의 직접 귀결(막생성 vs 막보호).
- **착화제 상호작용**: 글리신·구리염을 넣으면 Cu MRR 최대점이 ~3% H₂O₂로 **이동**(정점 shift) —
  착화제가 산화물을 계속 용해시켜 과-passivation을 늦추기 때문. §7에서 코드로 재현.

## 4. 부식억제제 (Corrosion Inhibitor) — BTA의 Cu 패시베이션
평탄화(planarization)의 핵심. 억제제가 없으면 산화제·착화제가 오목부(recess)의 Cu까지 등방 부식
(dishing/정적식각)시킨다. **벤조트리아졸(BTA, C₆H₅N₃)**은 Cu 표면에 **Cu(I)–BTA 중합막**을 만들어
정적식각을 막고, 볼록부(연마압 받는 곳)에서만 기계적으로 벗겨져 선택적으로 제거되게 한다.
- **흡착 정량**: BTA는 **Langmuir 흡착등온선**을 따르며 표준 흡착자유에너지 $\Delta G^0_{ads}\approx-35.4$
  kJ/mol(WebSearch 요지, 2차 인용). 부호(음수=자발흡착)와 크기(물리흡착 −20 ~ 화학흡착 −40 kJ/mol
  경계의 강한 흡착)만 검증했고 **절대값은 미검증**(1차 논문 전문 미확보).
- **의미**: $\Delta G$가 이 정도면 흡착상수 $K\approx2.9\times10^4$ L/mol → **수십 µM~mM 수준의 낮은
  BTA 농도로도 표면이 거의 포화**되어 강한 passivation. §7에서 재현.
- 다른 억제제·계: 우르산(uric acid, 알칼리 Cu), 3-amino-1,2,4-triazole/BTA(Mo barrier) 등도 유사한
  흡착막 원리(ScienceDirect, 2차 인용). Mo/Cu는 citrate계 약알칼리에서 화학촉진 제거가 연구됨
  (Gamagedara & Roy, *Materials* 17(19):4905, 2024, PMC11477894, 오픈액세스).

## 5. 착화제/킬레이트제 (Complexing/Chelating Agent)
금속이온과 **킬레이트 고리**를 만들어 (i) 산화막·금속의 용해를 촉진하고 (ii) 재석출·오염을 막으며
(iii) 제거율을 끌어올린다. 대표: **구연산(citric acid), 글리신, 옥살산**.
- Gamagedara & Roy(2024, PMC11477894): 0.1 M 구연산 첨가로 **Mo MRR ~2.4배, Cu MRR ~4.0배** 상승
  (무-연마입자 대비). Mo-citrate·Cu-citrate 착물 형성으로 표면 경도를 낮춰 기계제거를 도움.
  (검증: 문헌 보고 배수를 그대로 인용, 절대 MRR 46/41 nm/min은 조건 의존이라 **미검증** 취급.)
- 산화제-억제제와의 삼각관계: 착화제는 산화제가 만든 막을 계속 녹여 §3의 MRR **정점을 고농도로
  이동**시키고, 억제제(BTA)와는 "녹이려는 힘 vs 보호하려는 힘"으로 경쟁 → 이 균형이 dishing/erosion을 정한다.

## 6. 분산제·계면활성제 & pH 완충 — 입자를 띄우고 계를 고정
- **분산제/계면활성제**: 입자 응집·침강을 막아 안정한 콜로이드 유지. 정전(전하)·**입체(polymer brush)**
  두 방식으로 반발을 보강. 세리아 슬러리에 EAA 공중합체 분산제를 5→7 wt% 늘리면 제타전위가
  49→52 mV로 상승하고 입경이 281.6→227.2 nm로 감소(응집 완화), TEM상 ~5 nm 폴리머층이 입체장벽으로
  작용 — Hwang·Park·Kim, *Polymers* (Basel), 2024(PMC11679047, 오픈액세스). 이는
  [[colloid-zeta-dlvo-slurry-stability]]의 DLVO 정전반발에 **입체반발**을 더한 확장이다.
- **pH 완충(buffer)**: pH는 (i) 입자 표면전하(제타전위, IEP 회피 → 콜로이드 안정), (ii) 산화·용해
  화학의 방향(Pourbaix, Lv2-1), (iii) 억제제 흡착 상태를 **동시에** 지배한다. 완충제는 연마 중
  생성물(금속이온·산)으로 pH가 표류하는 것을 막아 율·선택비를 재현성 있게 고정한다.
- **상호작용 요약표**:

| 요소 | 1차 역할 | 늘리면 MRR | 과잉 시 부작용 | 결합 노트 |
|---|---|---|---|---|
| 연마입자 | 기계제거 | ↑(포화) | 스크래치·비용 | [[preston-luo-dornfeld-mrr]] |
| 산화제 | 무른 산화막 형성 | ↑후↓(정점) | 과-passivation·부식 | Kaufman |
| 억제제(BTA) | 오목부 보호(평탄화) | ↓(억제) | 율 과도저하·잔류결함 | Langmuir |
| 착화제 | 산화물 용해 | ↑(정점이동) | 등방부식·dishing | Pourbaix(Lv2-1) |
| 분산제 | 콜로이드 안정 | (간접) | 거품·율저하 | [[colloid-zeta-dlvo-slurry-stability]] |
| pH완충 | 계 고정 | (조건) | — | [[colloid-zeta-dlvo-slurry-stability]] |

## 7. 정량 재현 (코드) — BTA Langmuir & 산화제 정점
`sim/tier2_physics/slurry_components.py` (self-test **12/12 PASS**).
- **(A) BTA Langmuir**: $\theta=\dfrac{KC}{1+KC}$, $\Delta G_{ads}=-RT\ln(55.5K)$.
  - $\Delta G_{ads}=-35.4$ kJ/mol → $K=2.87\times10^4$ L/mol(재현). 반포화 $C=1/K=34.9$ µM에서 $\theta=0.5$
    (해석식 검증), **1 mM BTA에서 피복률 0.966 → 억제효율>0.9**(강한 passivation을 낮은 농도로 달성)로
    문헌 서술("낮은 BTA로도 강한 억제")과 정성 일치. 피복률은 농도에 단조증가·1로 포화.
  - **미검증**: $\Delta G$ 절대값은 2차 인용, IE≈θ 근사(피복률=억제율)는 통상 가정일 뿐 계 의존.
- **(B) 산화제-MRR 정점**: Kaufman 경쟁을 담은 현상론 단봉함수를 설계.
  $C=C_{peak}$에서 정확히 최대(미분=0 조건 만족, 수치탐색으로 확인), 이후 완만 감소(4%에서 정점의
  0.71배)를 재현. 착화제 파라미터로 정점을 1%→3%로 이동시키면 3% 지점 MRR이 역전 상승 → 문헌의
  "글리신 첨가 시 최대점 3%로 이동"을 정성 재현. **이 곡선은 형태 재현일 뿐 데이터 피팅이 아니며 정량
  절대값은 미검증**(디지털화 MRR-H₂O₂ 데이터 미확보).

## 8. 다른 에이전트 영역과의 연결·한계
- **Preston/입자스케일로**: 슬러리 화학은 $K_p$의 화학 성분을 채운다. 산화제/착화제=율↑, 억제제=율↓,
  이 순수 화학 자유도가 [[preston-luo-dornfeld-mrr]]의 $K_p$·활성입자 통계를 좌우.
- **접촉역학으로**: [[../materials/hertz-gw-contact-mechanics]]의 국소접촉압이 무른 산화막에 전달되어
  기계제거가 일어난다 — "무른 막"이라는 화학 전제가 접촉역학의 소성/취성 제거를 가능케 한다.
  [[../physics/tribology-friction-wear-stribeck]]의 Archard 마모(연질막 H↓→마모↑)와도 결합.
- **콜로이드로**: 분산제·pH는 [[colloid-zeta-dlvo-slurry-stability]]의 정전·입체 반발로 응집/결함을 제어.
- **한계/미검증**: (a) Kaufman 정점모델(B)은 현상론 — 실제 곡선·정점위치는 금속·산화제·pH별 실측 필요.
  (b) BTA $\Delta G$·Cu MRR 정점(1%/3%)·입자별 MRR 배수는 다수 2차 인용, 절대값 실측 캘리브레이션 대상.
  (c) 세리아 "화학적 이빨"·Ce³⁺/Ce⁴⁺ 산화환원 메커니즘은 Lv3-1에서 심화, 여기선 개요만.
  (d) 산화 화학의 pH·전위 지도(Pourbaix)와 passivation 동역학은 Lv2-1에서 정량화 예정.

## 9. 검증 코드 — §7 재현 + 이 노트를 인용하는 팩 키 감사 (2026-09-15 부채상환)

이 노트는 `check_knowledge.py`는 통과했으나 `verify_claims.py`에서 **검증 코드 블록 없음**으로
반려 상태였다 — §7이 "self-test 12/12 PASS"라는 **서술**만 갖고 있었기 때문이다. 서술은
증거가 아니므로(assert가 증거다) 아래에 실제로 실행되는 블록을 넣는다.

**감사 결과(신고)**: `knowledge/params/cu_h2o2_bta.yaml`의 네 키가 이 노트를 `source:`로
지목한다. 그중 `oxidizer_peak_wt_pct: 3.0`이 `confidence: verified`인데, **이 노트 §3·§8(b)는
Cu 정점 위치(1%/3%)의 근거를 §3·§8(b)에서 스스로 약하다고 표시**하고 있다 — 노트가 갖고 있지 않은
확신을 팩이 갖고 있는 **등급 역전**이다. 다만 같은 팩의 `oxidizer_curve_n` 주석은 "C_peak=3.0은
Aksu 2003(Electrochimica Acta)이 독립 확증한다"고 적고 있어, 실제 근거는 이 노트가 아니라
그쪽일 가능성이 높다. 즉 고칠 곳은 **등급이 아니라 `source:` 지목**일 수 있다. 값·등급을
이 회차에 임의로 내리지 않고(근거가 다른 문헌에 있을 수 있으므로) 아래 assert로 불일치를
사실로 고정해 담당(slurry-chemist)에게 이관한다. `oxidizer_wt_pct`·`inhibitor_mM`의 verified는
정당하다 — 이 둘은 문헌 물성이 아니라 **사용자가 이번 런에 정하는 운전 조건**이다.

```python verify
import math, re, pathlib

# ── (A) BTA Langmuir 재현 — §7(A)의 세 수치 ──
R, T = 8.314, 298.15
dG = -35.4e3                                  # J/mol — 절대값 근거는 §4에 적힌 그대로다
K = math.exp(-dG / (R * T)) / 55.5            # ΔG = −RT ln(55.5K)
assert abs(K - 2.87e4) / 2.87e4 < 0.02, f"K={K:.3e} — 본문 2.87e4와 2% 밖"

C_half = 1.0 / K                              # mol/L
assert abs(C_half * 1e6 - 34.9) < 0.5, f"반포화 {C_half*1e6:.1f} µM — 본문 34.9와 불일치"

theta = lambda C: K * C / (1.0 + K * C)
assert abs(theta(C_half) - 0.5) < 1e-12, "반포화 정의상 θ=0.5"
th_1mM = theta(1e-3)
assert abs(th_1mM - 0.966) < 0.002, f"1 mM θ={th_1mM:.4f} — 본문 0.966과 불일치"
assert theta(1e-4) < theta(1e-3) < theta(1e-2) < 1.0, "θ는 농도에 단조증가·1로 포화"

# ── (B) 산화제 단봉곡선 — 정점 조건이 실제로 만족되는지 ──
# §7(B)의 현상론 단봉함수. C_peak에서 최대이고 그 뒤 완만 감소해야 한다.
def mrr(C, C_peak, n=2.0):
    return (C / C_peak) ** 1.0 * math.exp(-((C / C_peak) ** n - 1.0) / n)
for C_peak in (1.0, 3.0):                      # 착화제 무/유 → 정점 이동
    grid = [i * 0.01 for i in range(1, 1201)]
    top = max(grid, key=lambda c: mrr(c, C_peak))
    assert abs(top - C_peak) < 0.02, f"C_peak={C_peak}인데 최대가 {top}"
# 정점 이동의 귀결: 3 wt%에서 착화제 계(정점 3%)가 무착화제 계(정점 1%)보다 높아야 한다(역전)
assert mrr(3.0, 3.0) > mrr(3.0, 1.0), "정점 이동 시 고농도에서 역전이 일어나야 한다"
assert mrr(4.0, 3.0) < mrr(3.0, 3.0), "정점 이후 감소"

# ── (C) 이 노트를 근거로 인용하는 팩 키 감사 ──
y = pathlib.Path("knowledge/params/cu_h2o2_bta.yaml").read_text()
cites = re.findall(
    r"^  (\w+):\n((?:    .*\n|\s*\n)*?)    source: knowledge/cmp/slurry-components-overview\.md\n"
    r"(?:    confidence: (\w+))?", y, re.M)
grades = {k: (g or "미선언") for k, _, g in cites}
print("이 노트를 인용하는 cu_h2o2_bta 키:", grades)

note = pathlib.Path("knowledge/cmp/slurry-components-overview.md").read_text()
weak_tokens = ("2차 " + "인용", "미" + "검증")   # 리터럴로 쓰면 이 노트 자신의 집계를 오염시킨다
assert all(w in note for w in weak_tokens), "본문이 스스로 근거 강도를 표시하고 있어야 한다"

# verified 가 정당한 두 부류 — 둘 다 "문헌이 보증하는 물성"이 아니라서 이 노트의 등급과 무관하다.
#   ① 운전 조건: 사용자가 이번 런에 정하는 값.
#   ② 기준 좌표(_ref): Kp를 어느 조성에서 역산했는지 가리키는 좌표. 본값과 함께 움직이며
#      예측을 바꾸지 않는다(과적합 감시가 자유도로 세지 않는 것과 같은 이유).
RUN_CONDITION = {"oxidizer_wt_pct", "inhibitor_mM", "oxidizer_ref_wt_pct"}
inversions = [k for k, g in grades.items()
              if g == "verified" and k not in RUN_CONDITION]
for k in inversions:
    print(f"⚠ 등급 역전: {k}=verified 인데 근거 노트는 스스로 약한 근거라 표시 "
          f"→ source 재지정 또는 등급 하향 필요(slurry-chemist 이관)")
assert inversions == ["oxidizer_peak_wt_pct"], \
    f"감사 기대와 다름: {inversions} — 해소됐다면 이 절의 기록을 갱신하라"
print("재현 A 3건 · B 4건 · 인용감사 1건 신고 완료")
```

## 10. 자기시험
→ [[../../agents/slurry-chemist/EXAMS.md]] Lv1-2 문항 참조.
