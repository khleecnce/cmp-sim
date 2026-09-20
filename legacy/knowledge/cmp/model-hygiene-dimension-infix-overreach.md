# 차원(D) 검사의 중위 무차원 규칙 과잉적용 — pH 축 파라미터 8건 오탐

EVIDENCE-RULES 판정#96(2026-09-20). 관련: [[model-hygiene-limit-check-silent-skip-time-chelator]],
[[chi-cu-ph-oxidizer-interaction-miranda2004]], [[sic-kmno4-ph-floor-oxidizer-coupling-wang2021]].

## 1. 무엇을 물었나

판정#95에서 `tools/model_hygiene.py`의 극한(L) 검사를 고친 직후, 같은 도구의
차원(D) 검사가 매 회차 **8건**을 "무차원이어야 하는데 단위가 있다"로 신고하고
있었다. 이것이 실제 차원 결함인가, 아니면 검사기 규칙의 과잉적용인가.

## 2. 실측 — 신고된 8건 전부 오탐

```
cu_alkaline_benzenesulfonic:cu_ph_acid_k        단위 1/pH
cu_alkaline_benzenesulfonic:cu_ph_alkaline_k    단위 1/pH
cu_h2o2_bta:cu_ph_acid_k                        단위 1/pH
cu_h2o2_bta:cu_ph_alkaline_k                    단위 1/pH
sic_alumina_kmno4:sic_kmno4_ph_acid_k           단위 1/pH
sic_alumina_kmno4:sic_kmno4_ph_floor_hi_wt      단위 wt%
sic_alumina_kmno4:sic_kmno4_ph_floor_lo_wt      단위 wt%
w_fe_oxidizer:w_ph_acid_k                       단위 1/pH
```

원문 대조 결과 **여덟 개 모두 단위 선언이 정당하다**:

- `*_ph_acid_k`·`*_ph_alkaline_k`는 f(pH)=exp(−k·(pH−ph_ref))의 감쇠계수다.
  지수의 인자가 무차원이어야 하므로 k는 **1/pH**가 맞다. 팩 note가 이미
  "접미사 `_k`가 검사기에서 절대온도(K)를 뜻하지만 여기서는 감쇠 상수 k이고
  차원은 1/pH다. pH는 무차원 로그량이므로 온도로 환산하는 관계 자체가
  존재하지 않는다"고 적어두었다. 값 0.1428은 US20080090500A1(PPG Industries
  Ohio; Hellring/Li/Auger) TABLE 4의 실리카 2/3/4 wt% 세 계열 12점 pooled
  최소자승이고, 계열별 k = 0.1360 / 0.1496 / 0.1427로 **서로 4.8% 이내 수렴**한다.
- `w_ph_acid_k` = 0.1163 (1/pH)는 Stojadinović, Bouvet, Mischler (2016),
  "Prediction of Removal Rates in Chemical-Mechanical Polishing (CMP) Using
  Tribocorrosion Modeling", *J. Bio- Tribo-Corros.* **2**:8,
  doi:10.1007/s40735-016-0041-4 Table 1에서 pH만 5→2로 바꾼 3조건의 MRR 비
  1.429/1.533/1.300을 로그평균해 ΔpH=3으로 나눈 값이다(재현오차 −0.8/−7.6/+9.0 %).
  같은 팩 note도 "exp()의 지수는 무차원이어야 하므로 (pH−ph_ref)[pH]와 곱해질 때만
  소거된다 — K로 바꿔 환산하면 오히려 차원이 깨진다"고 명시한다.
- `sic_kmno4_ph_floor_{hi,lo}_wt`는 φ 농도 보간의 앵커 **농도**이고 단위는
  **wt%**가 맞다. hi 앵커 6.5 wt%는 Wang, Liu, Song, ECS J. Solid State Sci.
  Technol. 10 (2021) 074004, doi:10.1149/2162-8777/ac12de 초록 인쇄값이다
  (pH 2.00, KMnO₄ 6.5 wt%, Al₂O₃, 4H-SiC Si면).

## 3. 원인 — 접미 규칙을 중위로 확장할 때 범위를 넓게 잡았다

`check_dimensions()`의 판정식:

    key.endswith(DIMLESS_SUFFIX) or any(f"{s}_" in key for s in DIMLESS_SUFFIX)

두 번째 항이 **중위(infix)** 검사인데, 코드 주석이 밝힌 도입 의도는 하나뿐이다
— `promoter_exponent_m`처럼 지수를 가리키는 한 글자(m·n·k)가 뒤에 붙으면
접미 규칙이 그 글자를 단위로 읽어 '미터'로 오판하는 문제. 그런데 튜플
**전체**를 중위로 돌리는 바람에 `_ph`가 `cu_ph_acid_k`·`sic_kmno4_ph_floor_hi_wt`
처럼 **이름에 pH가 들어가지만 그 자신은 무차원이 아닌** 키까지 집어삼켰다.

## 4. 새로 도출한 판정 기준 (물질명 없는 구조 규칙)

중위 표지가 될 수 있는가를 가르는 질문:

> 그 표지가 **키가 가리키는 양 자체**를 무차원으로 만드는가,
> 아니면 **어떤 축에 대한 양**인지를 말할 뿐인가.

지수는 전자다 — `_exponent`가 이름 어디에 있든 그 양은 무차원이다.
`_ph`는 후자다 — pH 축의 감쇠계수는 1/pH이고, pH 축의 앵커 농도는 wt%다.
축 이름은 차원을 정하지 않는다. 따라서 중위 표지는 `DIMLESS_INFIX = ("_exponent",)`
로 좁히고, 접미 규칙은 그대로 둔다(접미에서는 `_ph`로 **끝나는** 키가 실제로
무차원 pH 값이라 정당하다).

## 5. 수축의 반대 방향 위험을 함께 검사했다

규칙을 좁히면 면제를 잃은 키가 **진짜 결함인데 아무도 안 보는** 반대 오류가
생길 수 있다. 면제를 잃은 키 12개를 전수 확인한 결과, 전부 (a) 단위 선언이
정당해 일반 규칙을 그대로 통과하거나 (b) 팩 note에 근거가 적혀
`_exception_documented()`로 인정되는 경로였다 — 즉 **검사가 꺼진 것이 아니라
데이터 쪽 근거로 통과**한다. 다만 `sic_kmno4_ph_floor_hi_wt` 하나는 note 기반
예외 판정이 False인데도 신고가 없다 — 단위 `wt%`가 일반 규칙에서 정당하기
때문이며(농도 키에 농도 단위), 이는 의도된 통과다.

⚠ **미검증**: 이 판정은 현재 7개 팩에 존재하는 키 집합에 대한 전수 확인이다.
앞으로 추가될 키가 같은 함정(축 이름이 중위에 들어가는 유차원 양)을 만들지
않는다는 보장은 없다 — 그래서 규칙 자체를 테스트로 고정했다(§6).

## 6. 회귀 고정

`tests/test_model_hygiene_dimension_infix.py` 4건. 핵심은 "되돌리면 실제로
FAIL 하는가"를 실행으로 확인한 것이다 — `DIMLESS_INFIX = DIMLESS_SUFFIX`로
되돌리자 2건(`test_no_false_dimensionless_flags_for_ph_axis_params`,
`test_infix_rule_is_narrower_than_suffix_rule`)이 실제로 FAIL 했고, 복원 후
다시 통과했다. 상대적 성질만 검사해 오답을 통과시킨 전례(판정 ㉑의 21,600 km
해)를 피하려고, 규칙 집합의 **포함 관계**(`DIMLESS_INFIX ⊊ DIMLESS_SUFFIX`)와
원래 의도(`promoter_exponent_m`이 여전히 인정되는가) 양쪽을 같이 못 박았다.

## 7. 결과

차원(D) 신고 **8건 → 0건**, `model_hygiene` 전체 **17건 → 9건**.
`sim/`·`knowledge/params/*.yaml` **0 변경** — 값이 틀린 게 아니라 검사기가
틀렸으므로 고칠 곳은 검사기뿐이다. MRR 비트 불변.

```python verify
import sys
sys.path.insert(0, "/Users/khleecnce/fab-sim")
import warnings
warnings.filterwarnings("ignore")

from tools.model_hygiene import DIMLESS_SUFFIX, DIMLESS_INFIX, check_dimensions

# 중위 표지는 접미 표지의 진부분집합 — 되돌리면 이 assert 가 깨진다
assert set(DIMLESS_INFIX) < set(DIMLESS_SUFFIX)
assert "_ph" not in DIMLESS_INFIX

# 본래 의도(지수 한 글자 접미)는 유지
key = "promoter_exponent_m"
assert key.endswith(DIMLESS_SUFFIX) or any(
    ("%s_" % s) in key for s in DIMLESS_INFIX)

# pH 축 파라미터 6종이 더는 무차원 위반으로 오탐되지 않는다
titles = [i.title for i in check_dimensions()]
for k in ("cu_ph_acid_k", "cu_ph_alkaline_k", "w_ph_acid_k",
          "sic_kmno4_ph_acid_k", "sic_kmno4_ph_floor_hi_wt",
          "sic_kmno4_ph_floor_lo_wt"):
    assert not any(k in t and "무차원이어야" in t for t in titles), k

# 문헌값 대조: cu_ph_acid_k = 0.1428 (1/pH) 는 US20080090500A1 TABLE 4 의
# 계열별 k 0.1360 / 0.1496 / 0.1427 의 pooled 적합이다 — 세 계열이 서로
# 4.8% 이내로 수렴하고, pooled 값이 그 범위 안에 있어야 한다.
series = [0.1360, 0.1496, 0.1427]
pooled = 0.1428
assert min(series) <= pooled <= max(series), pooled
spread = (max(series) - min(series)) / min(series)
assert abs(spread - 0.1) < 0.01, spread   # 10.0% 폭
assert abs(pooled - series[2]) / series[2] < 0.001   # 중앙 계열과 0.1% 이내

# 문헌값 대조 2: w_ph_acid_k = 0.1163 (1/pH) 는 Stojadinovic 2016 Table 1 의
# pH 5->2 MRR 비 3개를 로그평균해 dpH=3 으로 나눈 값이다 — 원문 수치에서
# 그대로 재계산되는지 확인한다(노트가 기록한 재현오차 -0.8/-7.6/+9.0 % 포함).
import math
ratios = [1.429, 1.533, 1.300]
d_ph = 3.0
k_recomputed = sum(math.log(r) for r in ratios) / len(ratios) / d_ph
assert abs(k_recomputed - 0.1163) < 5e-4, k_recomputed
# 조건별 개별 k 산포 (팩 note: 0.0875~0.1426)
ks = [math.log(r) / d_ph for r in ratios]
assert abs(min(ks) - 0.0875) < 5e-4, ks
assert abs(max(ks) - 0.1426) < 5e-4, ks

print("OK")
```
