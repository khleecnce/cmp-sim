# χ(산화제) — 산화제 0 wt% 극단에서 억제형 단일 레짐의 구조적 반증 (Ihnfeldt 2008)

작성: 2026-09-20 / 담당: slurry-chemist / 대상 팩: `cu_h2o2_bta`
관련: [[chi-cu-ph-oxidizer-interaction-miranda2004]] · [[pressure-oxidizer-interaction-series-model-falsification]]

## 1. 무엇을 물었나

C4 갭(`cu_h2o2_bta` 유의 평균 ρ 0.7175 < 0.85)을 새 held-out 확보로 진전시킬 수
있는지. 조건: n≥4, 조성 1축 이상 변화, 인쇄값(표), 이 팩 재료계(Cu + H₂O₂ + 착화제).

## 2. 확보한 1차 자료

- **Ihnfeldt, R. V. (2008)** "Copper Chemical Mechanical Polishing: The Effects of
  Slurry Chemistry on Copper Surface Nanohardness, Alumina Agglomeration, and
  Material Removal Rate", Ph.D. dissertation, UC San Diego.
  로컬 전문: `papers/ihnfeldt2008-ucsd-dissertation-cu-cmp-alumina-colloidal.pdf`
  (코퍼스 doc_id `local:f26fd2cd11ef`). **Table 6.2** = 6 조성 × 3 pH 실측 MRR 표.
- **Ihnfeldt, R. V. and Talbot, J. B. (2008)** "Modeling Copper CMP Material Removal
  Rates Using Copper Surface Nanohardness", *ECS Transactions* **13**(4) 43–49.
  doi:10.1149/1.2912977 — 이번 회차 신규 확보(sci-hub 미러 경유,
  `papers/ihnfeldt2008-jes-modeling-cu-cmp-nanohardness.pdf`, 7쪽). 학술지판으로
  **공정 조건을 독립 재확인**하는 데 썼다: 1 psi · platen/wafer 30 rpm · 150 mL/min ·
  2 min · Cu 1 µm/Ta 30 nm/100 mm Si · MRR 실험오차 ±14 nm/min.
- 교차 대조: **Miranda, Imonigie, Moll (2004)**, doi:10.1109/WMED.2004.1297359
  (pH 4/8 × H₂O₂ 1.5/3.5 % 2² 요인, 이미 등록된 held-out).

배제: 같은 Table 6.2 의 조성 f(EDTA 계) 3점은 이 팩에 EDTA 축이 없어 범위 밖,
조성 a(KNO₃ 단독) 3점은 화학이 전부 꺼진 조건. 등록 규칙은 **관측 불확도**
(±14 nm/min)만 사용하고 우리 예측을 참조하지 않는다(자기채점 회피).

## 3. 등록 결과 — 실측 (내가 실행한 출력)

`validation/datasets/ihnfeldt2008_cu_alumina_ph_oxidizer_chelator.yaml`, n=7:
ρ=**−0.1429**, τ=−0.0476, p=0.6435, MAPE 1153.7 %, 계통편향 0.404배.
비유의이므로 유의 평균 ρ(0.9566) 집계에는 들어가지 않는다 — C4 격자는 불변이다.
숫자를 좋게 만들지 못했다는 사실을 그대로 적는다.

조건별 관측/예측(nm/min):

| 조건 | 관측 | 예측 | obs/pred |
|---|---|---|---|
| b) H₂O₂ 0 %, pH 10.0 | 15 | 933.5 | 0.0161 |
| c) H₂O₂ 0.1 %, pH 8.3 | 287 | 1525.0 | 0.1882 |
| c) H₂O₂ 0.1 %, pH 10.0 | 350 | 865.9 | 0.4042 |
| d) H₂O₂ 2.0 %, pH 3.0 | 113 | 1327.1 | 0.0851 |
| d) H₂O₂ 2.0 %, pH 8.3 | 289 | 670.7 | 0.4309 |
| d) H₂O₂ 2.0 %, pH 10.0 | 166 | 380.9 | 0.4359 |
| e) H₂O₂ 0.1 % + BTA 0.84 mM, pH 10.8 | 242 | 333.9 | 0.7247 |

문헌값 대조(정량, 출처 = Ihnfeldt 2008 학위논문 Table 6.2 · 학술지판 doi:10.1149/1.2912977): pH 10 · H₂O₂ 0.1 wt% 조건에서 관측 350 nm/min vs 모델 예측 865.9 nm/min (2.47배 과대), pH 10 · 0 wt% 에서 관측 15 nm/min vs 예측 933.5 nm/min (62.2배 과대). 재현 비교: 관측 증가비 23.33배 vs 모델 상한 1.00배 — 부호 자체가 반대다.

0 wt% 점을 빼면 n=6 ρ=+0.0857(p=0.4597) — 즉 **ρ 를 음수로 끌어내리는 것은
산화제 0 wt% 한 점**이고, 나머지 6점에서도 모델은 무작위 수준이다. 두 사실을
분리해 적는 이유: 전자는 함수형의 구조 결함이고 후자는 별개의 미분리 문제다.

## 4. 새로 도출한 지식 — 억제형 g(C)는 C→0 을 원리적으로 재현할 수 없다

현행 경로(`sim/chemistry.py::_oxidizer_term`, 판정#20 억제형):

    f(C) = φ + (1−φ)·(1−θ(C))/(1−θ(C_ref)),  θ(C)=K·C/(1+K·C)

θ가 C에 단조 증가하므로 (1−θ)는 단조 **감소**한다. 따라서 임의의 K>0, φ∈[0,1)에서

    f(0.1)/f(0) ≤ 1   (항등적으로)

이다. 그런데 관측은 pH 10 에서 H₂O₂ 0 → 0.1 wt% 로 15 → 350 nm/min, 즉
**23.33배 증가**다. 팩 실측값(K=0.8232, C_ref=3.0)으로 φ를 0→0.9 로 스윕하면
비는 0.9239 → 0.9788 로만 움직인다 — **φ로는 부호를 만들 수 없다**(판정#85의
"찾으면 정말 고쳐지는가를 먼저 물어라"와 같은 계열의 사전 반사실 검사).

함의: 이 팩의 산화제 항은 "산화제가 많을수록 부동태로 억제"라는 **단일 부호**를
가정하는데, 실제 계는 C=0 근처에서 **산화제가 없으면 Cu 가 깎이지 않는**
촉진 영역을 갖는다. 즉 g(C)는 단조 감소도 단조 증가도 아니고 **저농도 촉진 →
고농도 억제의 단봉형**이며, 그 정점 위치가 pH 에 따라 이동한다. Miranda 2004
(pH 4/8 2점)와 이 논문(pH 3/8.3/10 3수준)이 같은 결론을 독립적으로 가리킨다.

**그런데 이번 회차에 함수형을 바꾸지 않았다.** 이유 3가지:
1. 단봉형으로 되돌리면 레거시 Kaufman 경로의 (n, C_peak) **완전축퇴** 문제가
   되살아난다(판정#19, [[chi-oxidizer-curve-exponent-identifiability]]).
   3수준(0 / 0.1 / 2.0)으로 2 파라미터를 정하면 적합이 아니라 항등이다.
2. 정점 위치의 pH 의존을 넣으려면 파라미터가 하나 더 늘고, 그 근거가
   **held-out 자신**이 된다 — 배선 즉시 채점자 자격을 잃는다(판정#75 기준).
3. 판정#88이 이미 같은 팩에서 "상호작용 항을 만들기 전에 후보 함수형의 응답
   상한을 먼저 재라"를 확정했다. 이번 산출은 그 상한 검사를 **산화제 축의
   C→0 극단**에서 한 번 더 수행한 것이고, 대체 함수형의 독립 1차 근거는
   확보하지 못했다 — **미검증**으로 남긴다.

다음 회차가 써야 할 요건(구체): 같은 조성·같은 pH 에서 H₂O₂ 를 **0 포함 4수준
이상** 스윕한 인쇄표. 0 점이 없으면 φ·정점 어느 것도 식별되지 않는다.

## 5. 재현

```python verify
import sys
sys.path.insert(0, 'sim/tier2_physics')
import slurry_components as SC
import yaml

pk = yaml.safe_load(open('knowledge/params/cu_h2o2_bta.yaml'))['params']
K = float(pk['oxidizer_passivation_K']['value'])
C_ref = float(pk['oxidizer_ref_wt_pct']['value'])
assert abs(K - 0.8232) < 1e-6, K
assert abs(C_ref - 3.0) < 1e-9, C_ref

def f(C, phi):
    th = SC.oxidizer_coverage_langmuir(C, K)
    thr = SC.oxidizer_coverage_langmuir(C_ref, K)
    return phi + (1.0 - phi) * (1.0 - th) / (1.0 - thr)

# ① 억제형은 C 에 대해 단조 감소 — 어떤 φ 에서도 비가 1 을 넘지 못한다
for phi in (0.0, 0.05, 0.15, 0.30, 0.90):
    ratio = f(0.1, phi) / f(0.0, phi)
    assert ratio <= 1.0, (phi, ratio)
assert abs(f(0.1, 0.0) / f(0.0, 0.0) - 0.9239) < 2e-4
assert abs(f(0.1, 0.90) / f(0.0, 0.90) - 0.9788) < 2e-4

# ② 관측(Ihnfeldt 2008 Table 6.2, pH 10.0): 0 -> 0.1 wt% 에서 15 -> 350 nm/min
obs_ratio = 350.0 / 15.0
assert abs(obs_ratio - 23.333) < 1e-2
# 구조적 불가: 모델 상한(1.0)과 관측이 23배 이상 벌어진다
assert obs_ratio / 1.0 > 20.0

# ③ 두 점은 원문 측정 불확도(±14 nm/min)를 넘는다 — 잡음이 아니다
assert 15.0 > 14.0 and 350.0 > 14.0

# ④ 학술지판 원문에서 공정 조건 문구를 직접 확인 (전사 오류 방지)
sys.path.insert(0, 'tools')
from paper_text import paper_text
t = paper_text('ihnfeldt2008-jes-modeling-cu-cmp-nanohardness.pdf')
assert '1 psi down' in t
assert '30 rpm platen' in t
assert '150 ml/min' in t
assert 'The experimental error for MRR was' in t and '14 nm/min' in t

# ⑤ 데이터셋 백테스트 실측 재현 (등록 당시 값)
sys.path.insert(0, '.')
from pathlib import Path
from validation.backtest import run_dataset
r = run_dataset(Path('validation/datasets/ihnfeldt2008_cu_alumina_ph_oxidizer_chelator.yaml'))
assert r.n == 7, r.n
assert abs(r.spearman - (-0.142857)) < 1e-4, r.spearman
assert r.p_value > 0.05, r.p_value      # 비유의 — 유의 평균 ρ 집계에 안 들어간다
print('OK rho=%.4f p=%.4f n=%d' % (r.spearman, r.p_value, r.n))
```

## 6. 한계 (정직하게)

- 이 데이터셋의 절대값은 계통편향 0.404배로 **쓰면 안 된다**. 1.0 psi 는 이 팩 Kp
  역산 앵커(2~3 psi) 밖이고, 패드·장비도 다르다. 순위 전용이다.
- 조성 e 의 SDS(0.1 mM ≈ 28.8 ppm)는 이 팩에 계면활성제 축이 없어 미반영.
- 알루미나 응집체 크기(341~1930 nm, Table 6.1)는 override 하지 않았다 — 이 팩의
  `abrasive_size_exponent`=0(판정#1 null 결과)이라 넣어도 예측이 안 바뀌므로
  넣으면 "반영한 척"이 된다.
- 단봉형 g(C) 의 정점 위치·pH 의존성은 **미검증**이다. 이 노트는 현행 함수형의
  반증만 확정했고 대체 함수형을 제시하지 않았다.
