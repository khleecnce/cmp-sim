# 모델의 침묵과 모델의 예측을 구분하기 — cu_h2o2_bta/pH 가짜 CONFLICT 종결 (판정#94)

관련 노트: [[response-map-false-conflict-replicates-and-excluded-axes]] (판정#87),
[[c4-heldout-rank-ceiling-structural-bound]] (판정#91),
[[chi-cu-oxidizer-zero-point-ihnfeldt-falsification]] (판정#92),
[[cu-cmp-ph-mechanism]] (pH 항의 레짐 구조 원본)

## 1. 배경 — 최우선 갭이 또 도구 결함이었다

`tools/accuracy_gaps.py --next` 가 이 회차에 준 최우선 갭(score 120):

```
RESPONSE_CONFLICT  cu_h2o2_bta/pH: 모델 valley vs 문헌 peak
                   (n=3, ihnfeldt2008_cu_alumina_ph_oxidizer_chelator)
action: sim/factors.py의 해당 항을 그 구간에서 문헌 형상을 재현하도록 고쳐라.
        정점을 단조로 근사한 경우가 가장 흔하다.
```

action 문구를 따랐다면 `_ph_cu_acidic_term` 의 부호나 함수형을 고쳤을 것이다.
그런데 **모델은 그 문헌 점들에 대해 아무 예측도 하지 않는다.**

## 2. 실측 — 모델이 어디서 말하고 어디서 침묵하는가

`sim/factors.py::_ph_cu_acidic_term` 은 pH-MRR 을 레짐 좌표로 나눠 관측이 없는
칸에서 **항을 끄고 이유를 notes 에 적는다**(판정#34·#42 이래의 설계):

| 레짐 | 계수 | 상태 |
|---|---|---|
| 산성(pH≤6.25) × 억제제 有 | `cu_ph_acid_k`=0.1428 (US20080090500A1 T4, 12점 R²=0.954) | 예측함 |
| 알칼리 × 억제제 無 | `cu_ph_alkaline_k`=0.3329 (US9200180B2 T4, 5점 R²=0.997) | 팩이 선언하면 예측함 |
| 알칼리 × 억제제 有 | — | **관측 없음 → 항을 켜지 않음** |
| 산성 × 억제제 無 | — | **관측 없음 → 항을 켜지 않음** |

`cu_h2o2_bta` 의 기본 `inhibitor_mM`=1.0(BTA 1 mM)이므로 억제제 有 열만 해당한다.
즉 **pH > 6.25 전 구간이 침묵**이다. 엔진 실측(기본 조성, tier2.gw_physical_kp):

| pH | 평균 MRR (nm/min) | 모델의 말 |
|---|---|---|
| 3.0 | 577.3 | 예측 (상대 1.153) |
| 5.0 | 433.9 | 예측 (상대 0.867) |
| 7.0 | 500.5 | **침묵** (항 꺼짐 → pH 무관 상수) |
| 8.3 | 500.5 | **침묵** |
| 10.0 | 500.5 | **침묵** |
| 11.0 | 500.5 | **침묵** |

`tools/response_map.py` 는 숫자만 봤다. 감소 구간(3→6.25)과 상수 구간(6.25→11)이
이어지면 형상 분류기 `classify` 는 안쪽 최소점을 보고 **"valley"** 라 부른다.
그 인공 골짜기를 문헌 정점(Ihnfeldt 2008 pH 3/8.3/10 = 0.681/1.741/1.000 정규화)과
대조해 CONFLICT 가 찍혔다.

**문헌 3점 중 2점(8.3·10)이 모델이 침묵하는 구간에 있다.** 즉 이 비교는
"모델이 반대 방향을 가리킨다"가 아니라 "모델이 말하지 않은 것을 채점했다"이다.

## 3. 무엇이 문제인가 — 평평함의 두 가지 의미

이 코드베이스에서 MRR 이 어떤 축에 대해 평평한 경우는 세 가지고, 처방이 전부 다르다:

1. **미구현** — 엔진이 그 인자를 아예 안 쓴다 → `DEAD`. 처방: 항을 만들어라.
2. **검증된 영 결과** — 문헌이 "이 계에서 지배인자가 아니다"라고 말한다
   (예: `abrasive_size_exponent`=0, 판정#1) → `NULL_CONFIRMED`. 처방: 없음.
3. **선언된 레짐 공백** — 항은 있는데 그 구간의 계수 근거가 없어 **모델이 스스로
   예측을 포기**했다. 처방: 그 레짐의 1차 데이터를 확보하라. 코드는 멀쩡하다.

3번이 분류에 없었다. 그래서 3번이 1번(무반응)이나, 더 나쁘게는 이번처럼 이웃
구간과 이어져 **없는 형상**(valley)으로 읽혔다.

## 4. 수정 — 침묵을 구조화해 하류로 전달한다

### 4.1 `sim/factors.py` — `Factor.gated`

`Factor` 에 `gated: Dict[str, str]`(입력 키 → 포기 사유)를 추가하고,
`_ph_cu_acidic_term` 의 네 개 조기 반환(연마입자 게이트 + 3개 미관측 레짐)에서
사유를 채운다. `_f_chi` 가 그것을 `Factor` 에 실어 보낸다.

**notes 문자열을 정규식으로 긁지 않은 이유**: 문구가 바뀌면 탐지가 조용히 꺼지고,
그러면 도구는 다시 침묵을 예측으로 읽는다. 판정#89가 확인한 "감사기가 구분을
못 하면 매 회차를 같은 오진에 태운다"의 예방판이다.

항 선택은 `inspect.signature` 로 한다 — `try/except TypeError` 로 하면 항 **내부**의
TypeError 까지 삼켜 조용히 인자 없이 재실행한다.

### 4.2 `tools/response_map.py` — 침묵 점 제외 + 문헌 구간 재정렬

- `sweep()` 이 각 점의 `Factor.gated` 를 읽어 침묵 점을 곡선에서 빼고 `gated_x` 에 담는다.
- **문헌 점도 모델 유효 구간으로 자른다.** 모델 쪽만 줄이고 문헌을 그대로 두면
  구간이 다시 어긋난 비교가 된다 — 이번엔 형상이 아니라 범위에서. 이 도구의
  제1원칙("같은 구간에서 비교하라")의 범위판이다.
- 남은 문헌 점이 `MIN_LIT_N`(3) 미만이면 판정을 포기하고 새 판정 **`GATED`**(🚧)를 낸다.

### 4.3 `tools/accuracy_gaps.py` — score 80

`RESPONSE_GATED` 를 CONFLICT(120)·SPLIT(110)·DEAD(95)보다 **낮게** 둔다.
코드 수정 과제가 아니라 데이터 수집 과제이므로 물리 결함 위로 올리면 안 된다.

## 5. 결과 (직접 실행)

```
전 팩 응답지도  before: CONFLICT 1 · SPLIT 1 · AGREE 5 · GATED 없음
                after : CONFLICT 0 · SPLIT 1 · AGREE 5 · GATED 1
```

`cu_h2o2_bta/pH` 행: `❌ CONFLICT` → `🚧 GATED`, 모델 형상 `골` → `예측포기`.
**`sim/` 의 수치 계산은 한 줄도 바뀌지 않았다** — `Factor` 에 필드가 하나 늘었을 뿐
`value`·`terms`·`status`·`confidence` 모두 불변이고, 따라서 backtest·completion 도 불변이다.

## 6. 검증

```python verify
import sys; sys.path.insert(0, ".")
from sim.engine import Recipe, simulate
import sim.models  # noqa: F401
import numpy as np

MODEL = "tier2.gw_physical_kp"

def run(ph):
    r = simulate(Recipe(pack="cu_h2o2_bta", pack_overrides={"slurry_ph": ph}),
                 model=MODEL)
    return r, float(np.mean(r.mrr_nm_per_min))

# ── 1. 산성 가지는 예측한다 (문헌 계수 US20080090500A1 TABLE 4, k=0.1428)
r3, m3 = run(3.0)
r5, m5 = run(5.0)
assert "slurry_ph" not in r3.factors["chi"].gated
assert "slurry_ph" not in r5.factors["chi"].gated
# f(pH)=exp(-k(pH-4)) 이므로 3→5 비는 exp(-2k)
import math
assert abs((m5 / m3) - math.exp(-0.1428 * 2.0)) < 1e-6, (m5 / m3)

# ── 2. 알칼리 × 억제제 有 는 침묵이고, 그 사실이 구조로 남는다
for ph in (7.0, 8.3, 10.0, 11.0):
    r, _ = run(ph)
    assert "slurry_ph" in r.factors["chi"].gated, ph
    assert "관측이 없다" in r.factors["chi"].gated["slurry_ph"]

# ── 3. 침묵 구간의 MRR 은 서로 완전히 같다 = 예측이 아니라 상수
vals = [run(p)[1] for p in (7.0, 8.3, 10.0, 11.0)]
assert max(vals) - min(vals) < 1e-9, vals

# ── 4. 문헌 3점 중 2점이 침묵 구간에 있다 (이번 CONFLICT 의 원인)
LIT_PH = [3.0, 8.3, 10.0]           # Ihnfeldt 2008 Table 6.2, 조성 c/d
silent = [p for p in LIT_PH if "slurry_ph" in run(p)[0].factors["chi"].gated]
assert silent == [8.3, 10.0], silent
assert len(LIT_PH) - len(silent) < 3, "근거 구간에 3점이 안 남는다 → 판정 불가"

# ── 5. 응답지도가 침묵 점을 곡선에서 빼고 GATED 로 판정한다
#     (전 팩 build()는 느려서 여기선 해당 축만 — 전수 검사는
#      tests/test_response_gated_regime.py 가 한다)
import tools.response_map as rm
f = next(x for x in rm.FACTORS if x.key == "slurry_ph")
sw = rm.sweep("cu_h2o2_bta", f, (3.0, 10.0))     # 문헌 x 범위와 동일 구간
assert sw["gated_x"], "알칼리 구간이 빠져야 한다"
assert all(x <= 6.25 for x in sw["xs"]), sw["xs"]
# 문헌 점을 모델 유효 구간으로 자르면 3점 미만 → 판정 포기
kept = [x for x in LIT_PH if min(sw["xs"]) <= x <= max(sw["xs"])]
assert len(kept) < rm.MIN_LIT_N, kept
# 문헌이 어떤 형상이든 GATED (부호를 고치라는 처방이 나오지 않는다)
for lit in ("peak", "valley", "up", "down", "mixed"):
    assert rm.verdict_of("gated", lit) == "GATED"

# ── 6. 갭 랭커에서 GATED 는 CONFLICT(120) 보다 낮다
import re
src = open("tools/accuracy_gaps.py", encoding="utf-8").read()
sc = lambda kind: int(re.search(r'"kind": "%s", "pack": r\["pack"\], "score": (\d+)'
                                % kind, src).group(1))
assert sc("RESPONSE_GATED") == 80
assert sc("RESPONSE_GATED") < sc("RESPONSE_CONFLICT") == 120

print("OK")
```

## 6b. 정량 대조 — 산성 가지는 문헌 계수를 실제로 재현하는가

이번 판정은 "모델이 어디서 침묵하는가"를 고치는 작업이라 새 물리값을 도입하지
않는다. 그래도 **살아 있는 구간이 문헌을 재현하는지**는 같이 확인해야, 침묵
구간을 떼어낸 뒤 남은 예측을 믿을 수 있다.

US20080090500A1 TABLE 4 pooled 회귀값 k = 0.1428 /pH, 기준 pH 4.0 에 대한
상대 배수 f(pH) = exp(−k(pH−4)):

| pH | 문헌 계수로 계산한 f | 엔진 실측 MRR (nm/min) | MRR 비 (vs pH 4) |
|---|---|---|---|
| 3.0 | 1.15347 | 577.3 | 1.15347 |
| 4.0 | 1.00000 | 500.5 | 1.00000 |
| 5.0 | 0.86695 | 433.9 | 0.86695 |

정량 대조(US20080090500A1 TABLE 4, 비교 대상은 **배수**다 — 문헌은 절대 nm/min 을 주지 않는다): 문헌 계수 k=0.1428 /pH 가 규정하는 pH 5 배수 0.86695 를 엔진이 433.9 nm/min ÷ 500.5 nm/min = 0.86695 로 재현하고, pH 3 배수 1.15347 을 577.3 nm/min ÷ 500.5 nm/min = 1.15347 로 재현한다 — 상대 오차 < 1e-6 (§6 verify assert 1). 기준값 500.5 nm/min 자체는 이 대조의 대상이 아니라 팩 Kp 역산 결과이며, 그 절대 스케일의 한계는 판정#86이 따로 기록했다.
χ 의 pH 항이 다른 항과 곱셈 분리돼 있으므로 비가 정확히 f 로 떨어진다 —
이 일치는 "물리가 맞다"가 아니라 **"팩 계수가 코드에 제대로 전달된다"**는
전달 검증이다. 계수 자체의 한계(US20080090500A1 TABLE 4 기반 Tafel 독립 유도 시 b≈0.954 V/dec 로 전형값
0.06~0.12 의 약 10배)는 `sim/factors.py` docstring 이 이미 신고한 대로 남아 있다.

⚠ **미검증·추정 표기(이 노트가 확신하지 않는 것)**
- 골 위치 `VALLEY_PH`=6.25 는 **두 문헌값(6.0·6.5)의 중간으로 택한 구성값**이지
  측정값이 아니다. 레짐 경계가 6.25 라는 주장 자체는 **미검증**이며, 경계가
  ±0.25 움직이면 침묵 구간의 시작점도 같이 움직인다. 이번 판정의 결론
  (문헌 8.3·10 이 침묵 구간)은 경계가 6.0~6.5 어디든 바뀌지 않아 **강건**하다.
- 알칼리 × 억제제 有 레짐에서 pH-MRR 이 실제로 어떤 형상인지는 **확인 못 함**.
  Ihnfeldt 2008 은 그 조건(BTA 有)이 pH 10.8 **한 점**뿐이라 형상을 말할 수 없다.
  이 노트는 "모델이 모른다"만 주장하고 "실제로는 정점이다"는 주장하지 않는다.
- `cu_h2o2_bta` 의 다른 GATED 후보(산성 × 억제제 無)가 실무에서 얼마나 자주
  쓰이는 조건인지는 **추정조차 하지 않았다** — 조사 범위 밖.

## 7. 새로 도출한 지식

- **평평한 예측과 예측 없음은 다른 사건이고, 숫자만으로는 구분되지 않는다.**
  모델이 정직하게 "이 레짐은 모른다"고 신고할수록 그 침묵 구간이 넓어지고,
  침묵을 상수 예측으로 읽는 채점기는 **정직한 모델일수록 더 많은 가짜 결함을
  만든다.** 이것이 판정#87(`excluded_axes`)·판정#89(기록된 부채)와 같은 계열의
  세 번째 사례다 — 이번엔 데이터셋이 아니라 **모델 자신**이 신고한 한계였다.
- **모델 쪽만 구간을 줄이면 범위 불일치가 되살아난다.** 침묵 점을 빼는 순간
  문헌 점도 같은 구간으로 잘라야 한다. 안 그러면 형상 버그를 고치면서 범위
  버그를 새로 만든다.
- **갭의 점수는 처방의 종류를 반영해야 한다.** CONFLICT 는 "코드를 고쳐라",
  GATED 는 "데이터를 가져와라"다. 둘을 같은 점수로 두면 크론이 멀쩡한 항을 고친다.

## 8. 남은 과제 (이 노트가 닫지 않은 것)

`cu_h2o2_bta` 의 알칼리 × 억제제 有 레짐은 여전히 **비어 있다**. 채우려면:
같은 조성에서 **억제제 농도 2수준 × 골(pH≈6.25) 양쪽 pH 3점 이상**의 제거율
인쇄표가 필요하다. Ihnfeldt 2008 은 BTA 가 조성 e 한 점(pH 10.8)에만 있어
이 요건을 만족하지 못한다. 확보 전까지 이 칸은 GATED 로 남는 것이 정직하다 —
이웃 레짐 계수(산성 k=0.1428 또는 알칼리·무억제제 k=0.3329)를 빌려 오면
판정#34가 금지한 "빈 레짐에 이웃 계수 주입"이 되고, 두 효과가 한 계수에 뭉쳐
겉보기 성능만 좋아진 채 들키지 않는다.

## 9. 출처

- US20080090500A1 (PPG Industries Ohio; Hellring·Li·Auger, 우선일 2002-08-05) TABLE 4
  — 산성역 계수 `cu_ph_acid_k`=0.1428 의 1차 출처.
- US9200180B2 TABLE 4 (Ex.15~19) — 알칼리·무억제제 계수 0.3329 의 1차 출처.
- R. V. Ihnfeldt, Ph.D. dissertation, UC San Diego, 2008, Table 6.2 — 이번 CONFLICT
  의 문헌 측 근거. 학술지판 doi:10.1149/1.2912977 (ECS Trans. 13(4) 43-49, 2008).
  데이터셋 `validation/datasets/ihnfeldt2008_cu_alumina_ph_oxidizer_chelator.yaml`
  (판정#92에서 등록, n=7, ρ=−0.143 p=0.6435 비유의).
- Du & Desai 2003, DOI 10.1557/PROC-767-F6.6 — Cu pH-MRR V자 곡선의 골 pH 6.
- Ilie & Ipate 2017, DOI 10.3390/lubricants5020015 — 같은 골 pH 6.5.
  (`VALLEY_PH`=6.25 는 이 두 값의 중간.)
