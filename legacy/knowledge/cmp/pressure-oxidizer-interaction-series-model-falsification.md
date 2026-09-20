<!-- V2-SECTION: R2-slurry | 근거: 압력, 산화제, 교호작용, 비Preston, Cu | 정본: ARCHITECTURE-V2.md §3 -->
# Cu CMP — 압력×산화제 교호작용: 관측 압력비 4.32배가 **직렬(Langmuir-Hinshelwood)형을 구조적으로 반증한다** (판정#88)

> 작성일: 2026-09-20 | 대상: `tools/response_map.py` SPLIT 판정(`cu_h2o2_bta`/산화제 농도),
> `sim/chemistry.py::_oxidizer_term`, `sim/factors.py`(압력 경로)
> 데이터셋: `validation/datasets/us8501625b2_cu_h2o2_pressure_series.yaml` (n=6, held-out)
> 선행: [[chi-cu-ph-oxidizer-interaction-miranda2004]](판정#77 — pH가 산화제 부호를 뒤집는다),
> [[chi-cu-h2o2-regime-reversal-jani2025]](판정#41·#45·#47 — 착화제 종 분기),
> [[c4-cu-h2o2-bta-heldout-diagnosis]](판정#84)
> 과제: 갭 랭커 최상위 `RESPONSE_SPLIT`(score 110) — "문헌이 조건별로 방향이 갈린다(n=6), 모델은 단조↓ 단일 레짐".

## 1. 무엇을 물었나

판정#87이 이 축을 CONFLICT에서 SPLIT으로 재분류하면서 처방을 바꿨다: **부호를 뒤집지 말고
층을 가르는 조건을 찾아 팩을 분리하거나 상호작용 항을 유도하라.** 이번 회차의 질문은
하나다 — **US8501625B2의 2 psi/1 psi 두 층을 가르는 것이 무엇이고, 그것을 현행
곱셈분리 구조(`MRR = Kp·P·V · κ · χ · ψ · …`) 안에 담을 수 있는가.**

## 2. 1차 출처

- **US8501625B2** (Hitachi Chemical), "Polishing liquid for metal film and polishing method",
  등록 2013. TABLE 1(배합 A·F·G 조성)·TABLE 3(BTW 연마속도 2 psi/1 psi)·TABLE 5(A/F/G 재수록).
  전문: FreePatentsOnline HTML(`_patents/raw/8501625.json` 캐시). 조성은 H₂O₂ wt%만
  15→9.0→3.0으로 변하고 중합체·억제제(1,2,4-트리아졸 0.08 wt%)·킬레이트제·연마입자 동일,
  공정조건 공통(Rodel IC1000, platen 93 rpm, head 87 rpm, 200 mL/min, 블랭킷 Cu).
- **Ed Paul, "A Model of Chemical Mechanical Polishing", J. Electrochem. Soc. 148(6) G355-G358 (2001),
  doi:10.1149/1.1372222** — 원문 PDF 신규 확보(`papers/paul2001-model-of-cmp.pdf`, 4쪽).
  Eq. 16/17 및 Table I이 "화학 생성 ⇄ 기계 제거"의 정상상태 해를 폐형식으로 준다.
  `kD=0`(용해 무시, 본문이 "dissolution is often negligible under CMP conditions"라 명시)일 때
  Eq. 18은 `R = b₁[C]/([C]+b₂)`이고 **b₁ ∝ k_oM·P·v, b₂ ∝ (k₁ᵣ + k_oM·P·v·c_P·θ_A)/k₁f**
  (Table I) — 즉 P가 분자·분모에 **동시에** 들어가는 직렬 형태다. 두 단계 Langmuir-Hinshelwood
  모형(`1/MRR = 1/k_chem + 1/(k_mech·P·V)`)은 이 식의 같은 구조를 다른 표기로 쓴 것이다.

## 3. 관측 — 압력비가 산화제 농도에 의존한다

| H₂O₂ [wt%] | 2 psi [nm/min] | 1 psi [nm/min] | 압력비 | 유효 Preston 지수 n = log₂(비) |
|---|---|---|---|---|
| 15.0 | 630 | 330 | 1.909 | 0.933 |
| 9.0  | 720 | 390 | 1.846 | 0.885 |
| 3.0  | 820 | 190 | **4.316** | **2.110** |

- 곱셈분리형 `R = f(P)·g(C)`이면 압력비는 C에 **무관**해야 한다(정의상 g(C)가 약분된다).
  관측 압력비는 최대/최소 **2.338배** 차이 → 현행 엔진 구조로는 이 표를 원리적으로 재현 못 한다.
- 우리 엔진 실측(이번 회차 직접 실행): 세 농도 전부 예측 압력비 **2.000**(Preston 선형).
  2 psi 층만 보면 ρ=**+1.000**(모델 단조↓와 관측 단조↓ 일치), 1 psi 층은 ρ=**−0.500**.
  전체 6점 ρ=+0.657(p=0.087, 비유의). **즉 모델이 틀린 것은 산화제 항의 부호가 아니라
  압력·산화제를 독립으로 곱한 구조다** — 판정#87의 SPLIT 재분류가 옳았음을 정량 확인.

## 4. 새로 도출한 지식 — 직렬형은 압력비 2를 넘을 수 없다

Paul 2001 Eq.18(kD=0)에서 압력을 2배로 올릴 때의 비를 해석적으로 보면,
`R(P) = k·P·[C]/([C] + c₀ + κ·P)` 이므로

    R(2P)/R(P) = 2([C]+c₀+κP) / ([C]+c₀+2κP) < 2   (모든 [C], c₀, κ > 0)

직렬저항형 `1/R = 1/R_chem + 1/(R_mech·P)`도 같은 상한을 갖는다. **두 표준 모형 모두
압력 2배에 대해 항상 2배 미만(수확체감)을 예측한다.** 관측된 4.316배는 이 상한의 **2.16배**이므로
US8501625B2의 저산화제(3 wt%)·저압(1 psi) 조건은 **직렬 화학-기계 모형 자체를 반증한다**.
고농도 두 층(1.909·1.846)은 상한 안에 있으므로, 이 계는 **산화제 농도에 따라 서로 다른
모형이 지배하는 두 레짐**이다 — 하나의 함수형으로 덮는 것이 애초에 불가능하다.

임계압 가설(`R ∝ (P − P₀)`)로 같은 표를 읽으면 `P₀ = (r−2)/(r−1)`:

| H₂O₂ [wt%] | P₀ [psi] |
|---|---|
| 15.0 | −0.100 |
| 9.0  | −0.182 |
| 3.0  | **+0.698** |

산화제가 충분하면 P₀≤0(Preston 이상 영역, 임계압 없음)이고, 산화제가 고갈되면
P₀이 양수로 올라와 1 psi가 **임계압 바로 위**에 놓인다. 이는 특허 원문 해설
("산화제가 지나치게 적어 반응층이 얇고, 저압에서 속도가 낮다")과 방향이 일치한다.

## 5. 왜 배선하지 않았나 (조치: 코드·YAML 0 변경)

1. **자기채점.** P₀의 유일한 수치 근거가 이 held-out 6점 자신이다. 이 데이터셋으로 P₀를
   역산해 배선하면 그 순간 이 데이터셋은 채점자 자격을 잃는다(판정#75가 세운 기준:
   "자기채점이라 배선 못 한다는 것은 다른 문헌을 찾아라라는 뜻").
2. **자유도.** 3개 농도에 각각 P₀ 하나씩이면 3점에 3미지수 — 적합이 아니라 항등이다.
   임계압의 농도 의존성 `P₀(C)`를 유도하려면 최소 농도 3수준 × 압력 3수준 이상이 필요하다.
3. **반증한 것과 대체할 것은 다르다.** 이번 회차가 한 일은 "직렬형으로는 안 된다"의 증명이지
   "무엇이면 된다"의 증명이 아니다. 대체 함수형(임계압·압력의존 반응층 두께)의 독립 1차 근거는
   이번 탐색에서 확보하지 못했다 — **미검증**으로 남긴다.
4. 6점 적합을 강행한 반사실도 실행했다(4파라미터 직렬형 Nelder-Mead): MAPE 20.6%이지만
   **1 psi 층의 형상을 재현하지 못했다**(예측 290/331/351 단조↑ vs 관측 190/390/330 정점).
   지표가 좋아 보여도 형상이 틀리면 배선 근거가 아니다.

## 6. 한계·미검증

- P₀ 값 셋은 **이 특허 한 건에서만** 나왔다 — 독립 확인 0건. 미검증.
- 이 데이터셋은 억제제가 BTA가 아니라 1,2,4-트리아졸이고 연마입자가 0.17 wt%(팩 기준 3.0)이라
  절대값에 계통 편향이 있다(데이터셋 notes에 이미 신고됨, 순위 전용 취급).
- Paul 2001 Eq.16의 완전형(kD≠0)은 용해항이 압력 무관이라 압력비를 **더 낮춘다** —
  상한 2는 완전형에서도 유지된다(§7 verify).
- 압력×산화제 교호작용의 **독립 1차 근거**로는 Miranda 2004(판정#77, pH×H₂O₂ p=0.0207)가
  이미 있으나 그것은 pH 축이고 압력은 4 psi 고정이다 — 이 축의 대체 문헌은 못 찾았다.

## 7. 검증 코드

```python verify
import numpy as np

# ── US8501625B2 TABLE 3/5 인쇄값 (nm/min) — 1차 출처, 전사 그대로 ──
obs = {(2.0, 15.0): 630.0, (1.0, 15.0): 330.0,
       (2.0,  9.0): 720.0, (1.0,  9.0): 390.0,
       (2.0,  3.0): 820.0, (1.0,  3.0): 190.0}

# ① 압력비가 농도에 의존한다 = 곱셈분리형 R=f(P)g(C) 반증
ratios = {c: obs[(2.0, c)] / obs[(1.0, c)] for c in (15.0, 9.0, 3.0)}
assert abs(ratios[15.0] - 1.909090909) < 1e-6, ratios[15.0]
assert abs(ratios[9.0]  - 1.846153846) < 1e-6, ratios[9.0]
assert abs(ratios[3.0]  - 4.315789474) < 1e-6, ratios[3.0]
spread = max(ratios.values()) / min(ratios.values())
assert abs(spread - 2.3378) < 1e-3, spread          # 노트 §3의 2.338배

# ② 유효 Preston 지수 n = log2(압력비)
n_eff = {c: float(np.log2(r)) for c, r in ratios.items()}
assert abs(n_eff[15.0] - 0.9329) < 1e-3
assert abs(n_eff[9.0]  - 0.8845) < 1e-3
assert abs(n_eff[3.0]  - 2.1096) < 1e-3            # 초선형 — Preston(n=1) 위반

# ③ Paul 2001 (doi:10.1149/1.1372222) Eq.18 + Table I, kD=0:
#    R(P) = k P [C] / ([C] + c0 + kappa P)  →  압력 2배 비는 항상 < 2
def paul_ratio(C, c0, kappa, k=1.0, P=1.0):
    R = lambda p: k * p * C / (C + c0 + kappa * p)
    return R(2 * P) / R(P)
for C in (0.5, 3.0, 9.0, 15.0, 50.0):
    for c0 in (0.1, 1.0, 5.0, 20.0):
        for kappa in (0.01, 0.5, 3.0, 20.0):
            assert paul_ratio(C, c0, kappa) < 2.0

# ③-b 용해항(kD≠0, 압력 무관)을 더하면 비는 더 낮아진다
def paul_ratio_with_diss(C, c0, kappa, kd, k=1.0, P=1.0):
    R = lambda p: kd * C / (C + c0) + k * p * C / (C + c0 + kappa * p)
    return R(2 * P) / R(P)
for kd in (0.1, 1.0, 10.0):
    assert paul_ratio_with_diss(9.0, 5.0, 3.0, kd) < paul_ratio(9.0, 5.0, 3.0)

# ③-c 두 단계 Langmuir-Hinshelwood 1/R = 1/Rc + 1/(Rm*P) 도 같은 상한
def lh_ratio(Rc, Rm, P=1.0):
    R = lambda p: 1.0 / (1.0 / Rc + 1.0 / (Rm * p))
    return R(2 * P) / R(P)
for Rc in (10.0, 100.0, 1e4):
    for Rm in (10.0, 100.0, 1e4):
        assert lh_ratio(Rc, Rm) < 2.0

# ④ 관측 4.316 > 2 → 직렬형 두 계열 모두 구조적으로 재현 불가
assert ratios[3.0] > 2.0
assert ratios[3.0] / 2.0 > 2.0                      # 상한의 2.16배

# ⑤ 임계압 가설 R ∝ (P - P0):  ratio = (2-P0)/(1-P0) → P0 = (r-2)/(r-1)
P0 = {c: (r - 2.0) / (r - 1.0) for c, r in ratios.items()}
assert abs(P0[15.0] - (-0.1000)) < 1e-3, P0[15.0]
assert abs(P0[9.0]  - (-0.1818)) < 1e-3, P0[9.0]
assert abs(P0[3.0]  - (+0.6984)) < 1e-3, P0[3.0]
# 산화제가 줄수록 임계압이 커진다(반응층 고갈 방향) — 단조
assert P0[9.0] < P0[15.0] < P0[3.0] or P0[9.0] < P0[15.0] and P0[15.0] < P0[3.0]
assert P0[3.0] > 0.0 > P0[15.0]                     # 저농도만 임계압 양수

# ⑥ 2 psi 층만 보면 모델(단조↓)과 관측(단조↓)이 일치한다 — 부호를 뒤집으면 이 층이 깨진다
hi = [obs[(2.0, c)] for c in (15.0, 9.0, 3.0)]      # C 내림차순
assert hi == sorted(hi), hi                          # 630 < 720 < 820 (C↓일수록 빠름)
lo = [obs[(1.0, c)] for c in (15.0, 9.0, 3.0)]
assert not (lo == sorted(lo)), lo                    # 1 psi 층은 단조가 아니다(정점)
```

### 게이트 실행 결과 (이번 회차 직접 실행)
- 엔진 실측 예측 압력비 = **2.000**(세 농도 전부) vs 관측 1.909/1.846/4.316
- 층별 ρ: 2 psi **+1.000**, 1 psi **−0.500**, 전체 6점 +0.657(p=0.087, 비유의)
- 4파라미터 직렬형 강제적합: MAPE 20.6%, 그러나 1 psi 층 형상 재현 실패(§5-4)

### §7-b 반사실: 4파라미터 직렬형 강제적합 (지표는 통과, 형상은 실패)

```python verify
import numpy as np
# 6점에 대해 1/R = 1/(a·C^p) + 1/(b·P·C^-q) 를 로그공간 최소자승으로 적합한 결과
# (격자탐색 + Nelder-Mead, 이번 회차 실행). 아래는 그 해를 고정해 재현·검사한다.
a, p, b, q = 7467.0, 98.8856, 255.1, -0.1180
data = [(2.0, 15.0, 630.0), (1.0, 15.0, 330.0),
        (2.0,  9.0, 720.0), (1.0,  9.0, 390.0),
        (2.0,  3.0, 820.0), (1.0,  3.0, 190.0)]
P = np.array([d[0] for d in data]); C = np.array([d[1] for d in data])
R = np.array([d[2] for d in data])
r_chem = a * C**p
r_mech = b * P * C**(-q)
pred = r_chem * r_mech / (r_chem + r_mech)

mape = float(np.mean(np.abs(pred - R) / R)) * 100
assert 20.0 < mape < 21.0, mape                     # 노트 §5-4의 "MAPE 20.6%"

# 형상 검사: 1 psi 층은 관측이 정점(190/390/330, C=3/9/15)인데 적합은 단조↑
lo_pred = [float(pred[i]) for i in (5, 3, 1)]       # C = 3, 9, 15 (1 psi)
assert lo_pred == sorted(lo_pred), lo_pred          # 단조↑ = 정점 재현 실패
lo_obs = [190.0, 390.0, 330.0]
assert lo_obs != sorted(lo_obs)                     # 관측은 정점
# 즉 MAPE가 20%대여도 층 형상을 못 맞히므로 배선 근거가 아니다
assert abs(lo_pred[0] - 290.4) < 1.0, lo_pred[0]    # 관측 190 대비 +53%
```

## 8. 대조에 쓴 관련 1차 출처

- P. A. Miranda, J. A. Imonigie, A. J. Moll (2004), "Interaction Effects of Slurry Chemistry
  on Chemical Mechanical Planarization of Electroplated Copper", IEEE WMED,
  **doi:10.1109/WMED.2004.1297359** — pH×H₂O₂ 교호작용 p=0.0207(원문 ANOVA). 이 노트의
  압력×산화제 교호작용과 **같은 계열의 다른 축**이며, 압력은 4 psi 고정이라 본 축의
  독립 근거로는 쓸 수 없다(§6).
- J. Luo, D. A. Dornfeld (2004), "Review of CMP Modeling", in *Integrated Modeling of
  Chemical Mechanical Planarization for Sub-Micron IC Fabrication*, Springer,
  **doi:10.1007/978-3-662-07928-7_2** — Preston 식이 입자/다이/웨이퍼 스케일을 잇는
  인터페이스라는 구조. 본 노트가 반증한 것은 그 인터페이스 자체가 아니라 **P와 화학항을
  독립으로 곱하는 사용법**이다.
- 저장소 내 선행 판정: `EVIDENCE-RULES.md` 판정#77(pH 스위치), #87(이 축의 CONFLICT→SPLIT
  재분류), 데이터셋 `validation/datasets/us8501625b2_cu_h2o2_pressure_series.yaml`
  (자체 notes가 이미 "압력×산화제 상호작용을 표현하지 못해 G(1psi)에서 큰 오차가 예상된다"고 신고).
