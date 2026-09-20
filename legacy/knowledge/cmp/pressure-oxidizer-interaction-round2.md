<!-- V2-SECTION: R2-slurry | 근거: 압력, 산화제, 교호작용, C4 반사실, Cu | 정본: ARCHITECTURE-V2.md §3 -->
# Cu CMP — 압력×산화제 교호작용 2회차: C4 반사실 스윕 — "무엇이면 되는가"는 자기채점 경계 안에서만 존재한다 (판정#89)

> 작성일: 2026-09-20 | 선행: [[pressure-oxidizer-interaction-series-model-falsification]](판정#88 — 직렬형 함수형 계열 자체가 관측 압력비 4.316배로 구조적 반증됨)
> 과제: 1회차가 남긴 "무엇이면 되는가"(임계압 P₀(C) 또는 압력의존 반응층 두께)의 독립 1차 근거 탐색.
> **결론(최상위): 착수 전 반사실 스윕 결과 — C4는 이론적으로 도달 가능하나, 그 유일한 경로가
> 이 held-out 자신에 대한 거의 완전한 파라미터 포화(자기채점)를 요구한다. 독립 문헌이 공급할 수 있는
> 수준의 2~3파라미터 형태로는 구조적으로 미달이다. 이에 따라 본 회차는 무거운 문헌 탐색을
> 진행하지 않았다(과제 지시 §단계0의 게이트).**

## 1. C4 계산 경로 확인 (실측)

이번 회차가 재사용한 관측표는 **US8501625B2**(Hitachi Chemical, 판정#88·1회차가 확보한
`_patents/raw/8501625.json` 캐시) TABLE 3/5의 문헌값 그대로다 — H₂O₂ 15/9/3 wt%에서
2 psi MRR 630/720/820 nm/min, 1 psi MRR 330/390/190 nm/min(전사·대조는
[[pressure-oxidizer-interaction-series-model-falsification]] §3·§7이 이미 완료했고 이번 회차는
그 값을 그대로 스윕 입력으로만 재사용한다). 압력×산화제 폐형식의 다른 표준 후보인
Paul 2001(doi:10.1149/1.1372222, `papers/paul2001-model-of-cmp.pdf` 로컬 확보)의 Eq.18도
1회차가 이미 반증했으므로 이번 회차는 재검증하지 않는다.

`tools/completion.py::heldout_by_pack()`이 팩별 C4를 계산한다. `cu_h2o2_bta` 팩은 held-out YAML
8개 중 `in_scope=True`이고 `used_for_calibration=False`인 5개(`hong2007_cu_ads_bta_polish_rate`,
`jani2025_cu_rsm_composition_heldout`, `miranda2004_cu_ph_h2o2_2x2`, `tw202115224a_cu_abrasive_size_pressure`,
`us8501625b2_cu_h2o2_pressure_series`)가 후보이고, 이 중 **유의(순열검정 p<0.05)한 것만** 평균에
들어간다. 직접 실행 결과 — 현재 유의 데이터셋은 **`tw202115224a`(ρ=0.7175) 단 1건**이고
`us8501625b2`(1회차의 판정#88 대상, ρ=0.657)는 **p=0.087로 비유의**라 평균에 전혀 기여하지 않는다.
즉 판정#88이 반증한 층분리 자체가 C4 점수에는 **지금도 반영되지 않고 있다.**

```python verify
# tools/completion.py::heldout_by_pack() 실측치를 그대로 고정해 재현 검사한다.
# (2026-09-20, .venv/bin/python -c 로 직접 실행해 확인)
n_sig, mean_rho, rho_tw = 1, 0.7175, 0.7174500322602797
assert n_sig == 1
assert abs(round(rho_tw, 4) - mean_rho) < 1e-9
RHO_MIN = 0.85
assert mean_rho < RHO_MIN          # 현재 C4 미달 — 노트 상단 배경과 일치
```

## 2. 반사실 스윕 — us8501625b2가 유의해지면 C4가 되는가

n=6 순열검정(정확검정, 6!=720)에서 유의(p<0.05) 경계는 **ρ≥0.7714**이다(ρ=1.0 만이 아니다 —
이 지점은 처음 스윕에서 오독했다가 전체 순열분포를 다시 계산해 정정했다). 이 데이터셋이
유의해지면 팩 평균은 `(0.7175 + ρ_new)/2`가 되므로, C4(≥0.85) 도달에는 **ρ_new ≥ 0.9825**가
필요하다 — 사실상 **완전 순위 일치(ρ=1.0, 즉 6점 전부 순위 오차 0)**에 가까운 근처만 통과한다.

```python verify
import itertools

def spearman_rho(x, y):
    n = len(x)
    rx = sorted(range(n), key=lambda i: x[i])
    ry = sorted(range(n), key=lambda i: y[i])
    rank_x = [0]*n; rank_y = [0]*n
    for r, i in enumerate(rx): rank_x[i] = r
    for r, i in enumerate(ry): rank_y[i] = r
    d2 = sum((rank_x[i]-rank_y[i])**2 for i in range(n))
    return 1 - 6*d2/(n*(n**2-1))

def perm_p_value(rho, n):
    base = list(range(n))
    total = hit = 0
    for q in itertools.permutations(base):
        total += 1
        if spearman_rho(base, list(q)) >= rho - 1e-9:
            hit += 1
    return hit/total

# n=6 유의 경계 재계산 (판정#88 노트는 이 지점을 다루지 않았다 — 이번 회차 신규 확인)
base = list(range(6))
rhos = sorted(set(round(spearman_rho(base, list(q)), 6) for q in itertools.permutations(base)), reverse=True)
sig_rhos = [r for r in rhos if perm_p_value(r, 6) < 0.05]
assert min(sig_rhos) == 0.771429, sig_rhos   # 유의 경계 = 0.7714 (ρ=1.0 만이 아니다)

# 팩 평균이 0.85에 도달하려면 필요한 ρ_new
rho_tw = 0.7174500322602797
required = 2*0.85 - rho_tw
assert abs(required - 0.982550) < 1e-4      # ≥0.9825 필요 — 유의 경계(0.7714)보다 훨씬 엄격
# 유의 경계를 겨우 넘는 값(0.7714~0.9429)으로는 전혀 부족하다
for r in (0.771429, 0.828571, 0.885714, 0.942857):
    mean = (rho_tw + r) / 2
    assert mean < 0.85, (r, mean)
# ρ=1.0(6점 전부 순위 오차 0)만이 유일하게 충족
assert (rho_tw + 1.0) / 2 >= 0.85
```

## 3. 파라미터 수를 늘려가며 "실제로 도달 가능한 최대 ρ"를 쟀다

관측 6점의 순위(오름차순): (1psi,3%)<(1psi,15%)<(1psi,9%)<(2psi,15%)<(2psi,9%)<(2psi,3%).
곱셈분리형(`R=f(P)g(C)`)은 판정#88이 이미 반증했으므로(P가 다르면 C에 대한 순서가 뒤집힘),
비분리 함수형 계열에서 **자유파라미터 수를 2→5로 늘리며** 이 순위를 재현할 수 있는 최댓값을
쟀다(과제 지시 "P₀(C)를 어떤 형태로 주더라도"에 대응하는 실측). `R=P−(a+bC)`류는 순위가 `a`에
전혀 의존하지 않는다는 것을 먼저 대수적으로 확인했다(모든 6점에서 `a`가 공통으로 상쇄) — 즉
"2파라미터"라 불러도 순위결정에는 실질 자유도가 1(`b`)뿐이다. 이 대수적 사실 때문에 초기 스윕에서
쓴 확률적 Nelder-Mead 다중시작 탐색이 `min_gap=0`(순위 동률)인 축퇴해를 최적으로 오판하는 문제가
있어, 이번엔 **결정적 격자스캔**으로 다시 쟀다.

| 함수형(순위결정 실질자유도) | 성격 | 달성 ρ(격자스캔 전역값) | 유의(p<0.05)? | 새 팩평균 |
|---|---|---|---|---|
| `R=P−(a+bC)` (1) | 임계압 선형 | 0.8783(`b→0`, 사실상 C무의존) | 예 | 0.798 |
| `R=P−(a+bC+cC²)` (2) | 임계압 이차 | 0.8857 | 예 | 0.802 |
| `R=(k₀+k₁C)(P−(a+bC+cC²))` (5, 1 DOF) | 진폭+임계압 모두 자유 | **1.000** | 예 | **0.859** |

5파라미터(6점 데이터에 자유도 1만 남김)에서야 완전 순위 일치(ρ=1.0)에 도달했고, 그 아래
1~2 실질자유도 계열은 격자 전역에서도 팩 평균을 0.85 위로 올리지 못한다(0.798~0.802에서 정체).

```python verify
import numpy as np
from scipy.stats import spearmanr

data = [(2.0, 15.0, 630.0), (1.0, 15.0, 330.0), (2.0, 9.0, 720.0),
        (1.0, 9.0, 390.0), (2.0, 3.0, 820.0), (1.0, 3.0, 190.0)]
P = np.array([d[0] for d in data]); C = np.array([d[1] for d in data]); R = np.array([d[2] for d in data])
rho_tw = 0.7174500322602797

# ① 1 실질자유도: R = P - b*C (a는 모든 항에 공통 상쇄되어 순위 무관 — 대수적으로 자명)
best1 = max(spearmanr(P - b*C, R).correlation for b in np.linspace(-5, 5, 2001))
assert abs(best1 - 0.878310) < 1e-4, best1

# ② 2 실질자유도: R = P - (b*C + c*C^2)  (격자스캔, 전역값과 일치 확인된 해상도로 재현)
best2 = 0.0
for b in np.linspace(-2, 2, 101):
    for c in np.linspace(-0.2, 0.2, 101):
        rho = spearmanr(P - b*C - c*C**2, R).correlation
        if rho > best2:
            best2 = rho
assert abs(best2 - 0.885714) < 1e-4, best2

mean_1 = (rho_tw + best1) / 2
mean_2 = (rho_tw + best2) / 2
assert mean_1 < 0.85, mean_1
assert mean_2 < 0.85, mean_2

# ③ 5파라미터(1 DOF): 격자탐색으로 확보한 해를 상수로 고정해 재현 검사(과도한 탐색 대신 고정값 검증)
k0, k1, a, b, c = 975.842815, -51.3601481, 0.865345419, -0.0516260003, -0.00396341663
pred5 = (k0 + k1*C) * (P - (a + b*C + c*C**2))
rho5 = spearmanr(pred5, R).correlation
assert rho5 > 0.999, rho5                              # 완전 순위 일치
mean_5 = (rho_tw + rho5) / 2
assert mean_5 >= 0.85, mean_5
```

## 4. 왜 5파라미터 해가 "찾은 것"이 아니라 "자기채점"인가

5파라미터로 6점을 맞추면 자유도가 1(round1 §5-2가 이미 지적한 "3점에 3미지수는 항등"의 연장)이다.
독립 1차 문헌이 이런 형태(진폭과 임계압이 각각 산화제 농도의 이차함수)를 **다른 계에서 검증한 뒤
이 held-out에 그대로 대입**했을 가능성은 이번 탐색에서 찾지 못했다 — 그런 정밀도의 이차 교호작용
모형을 보고하는 Cu CMP 압력×산화제 교차설계 논문은 극히 드물 것으로 예상되고(과거 회차가 이미
Miranda 2004(doi:10.1109/WMED.2004.1297359)를 압력×산화제류 교호작용의 유일한 독립 근거로 확인,
[[pressure-oxidizer-interaction-series-model-falsification]] §6·§8), 이번 회차의 로컬 탐색도 동일 결론에
도달했다(§5). **5파라미터 해를 채택하는 것은 held-out 6점 자체를 역산해 배선하는 것과 실질적으로
같다** — 판정#75의 자기채점 금지 기준, 판정#85 2회차가 세운 "반사실 먼저" 원칙과 같은 계열이다.
J. Luo, D. A. Dornfeld(2004), doi:10.1007/978-3-662-07928-7_2 가 정리한 Preston 인터페이스
구조(입자↔다이↔웨이퍼 스케일을 잇는 승수형 연결)도 이 5파라미터 해처럼 **압력과 화학을
비분리로 다시 얽는 항**을 표준으로 요구하지 않는다 — 즉 표준 문헌 계열 자체가 이런 고자유도
교호작용 항을 기본으로 공급하지 않는다는 방증이다.
2~3파라미터(독립 문헌이 실제로 공급 가능한 복잡도)는 구조적으로 0.85에 못 미친다(§3 표).

## 5. 독립 1차 근거 탐색 — 제한적 시도, 신규 후보 0건

과제 지시대로 판정#83·#85·#88의 "부적격 확인" 목록(로컬 특허 코퍼스, Clarkson 그룹 4편,
sci-hub 대체 미러 등)은 재탐색하지 않았다. 이번 회차 신규로 확인한 것:

- **로컬 코퍼스**: `data/corpus/corpus.sqlite`(1719건 전문 확보) 제목 검색에서 "copper"+"pressure/psi"
  동시 히트 **0건**. `papers/*.txt`(전문 텍스트 추출본, 21개뿐 — 극히 일부만 텍스트화됨) 중
  "psi"∧"H2O2/hydrogen peroxide"∧"copper" 3중 동시 등장 파일 **0건**. `_patents/index.jsonl`(149건)
  제목에 copper 포함 14건이나 압력×산화제 교차표를 확인하려면 전문을 열어야 하고 이번 회차 예산으로는
  전수 확인하지 않았다 — **미검증**으로 남긴다.
- **Ihnfeldt 2008 (UCSD 박사논문, 로컬 전문 보관, `validation/datasets/ihnfeldt2008_cu_alumina_ph_oxidizer_chelator.yaml`
  이 이미 사용 중)**: Table 6.2가 pH×산화제×첨가제 조합이지만 **압력이 1.0 psi 고정**(장비 최대,
  §4.5.2)이라 압력 축이 없다 — 이 축의 후보에서 제외.
- 그 외 신규 검색(OpenAlex/find_open_access.py 호출)은 **§2·§3의 반사실 결과를 보고 수행하지
  않았다** — 과제 지시의 "(b)가 원리적으로 불가능하면 탐색 자체를 하지 마라" 게이트를 그대로 적용.
  다만 완전한 불가능은 아니고 "실현 가능한 복잡도로는 불가능"이라는 조건부 결론이라, 완전 탐색
  중단이 과도했을 가능성은 있다 — **추정**으로 표기.

## 6. 배선 요청 — 없음

이번 회차는 `sim/`·`validation/`에 대한 배선을 제안하지 않는다. 판정#88의 결론(직렬형 계열 반증,
코드 0변경)을 뒤집을 신규 근거가 없고, §2~§4의 정량 스윕은 오히려 "이 held-out으로 C4를 통과하려면
자기채점이 불가피하다"는 것을 확인했을 뿐이다. `EVIDENCE-RULES.md` 등록과 격자 갱신은 총괄이
직접 한다(과제 지시).

## 7. 한계·미검증

- §5의 로컬 코퍼스 검색은 제목/파일명 매칭과 21개뿐인 텍스트 추출본에 한정됐다 — 전문 PDF
  1719건 전수를 열어 확인하지는 않았다. **확인 못 함**.
- §3의 "5파라미터에서 ρ=1.0" 결과는 Nelder-Mead 다중 시작점 탐색으로 얻은 **하나의 해**이며
  전역 최적이라는 보장은 없다 — 다만 결론(2~3파라미터 부족, 5파라미터 충분)에는 영향 없다.
- 압력의존 반응층 두께 가설(과제 배경이 언급한 두 번째 후보)은 이번 회차에서 별도로 다루지
  않았다 — 임계압형과 수학적으로 동형(`R∝(P−P₀)`)이라 §2~§4 결과가 그대로 적용된다고 **추정**한다.
