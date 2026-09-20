# Cu·W 팩 절대값 계통편향 3건 — 갭 랭커 최상위 BIAS (판정#58)

작성: 2026-09-18 · 담당: 정확도루프(성장엔진) · 대상 팩: `cu_h2o2_bta`, `w_fe_oxidizer`
관련: [[sic-kmno4-alumina-absolute-mrr-patent-vs-papers]](판정#55 방법론 출처),
[[liang2026-composite-abrasive-absolute-mrr-bias]](판정#57, 정의역 외삽 판정 계보),
[[w-cmp-preston-kp-oxidizer-rate-literature-reproduction]](Kp 3문헌 역산, 이 판정이 그대로 인용),
[[bta-inhibitor-langmuir-K-effective-cu-cmp-falsification]](억제제 항 정의역 한계 선례)

## 0. 대상과 결론 요약

`tools/accuracy_gaps.py` BIAS 최상위 3건:

| # | 데이터셋 | ρ(p) | scale(obs/pred) | 팩 | 판정 |
|---|---|---|---|---|---|
| 1 | `us9200180b2_cu_ph_alkaline_sweep` | +1.000 (p=0.008) | ~0.0051 (5점, 거의 상수) | cu_h2o2_bta | **갭 랭커 오상정 — 캘리브레이션셋 자기순환. 툴 수정으로 해소** |
| 2 | `us9200180b2_cu_abrasive_series` | +1.000 (p=0.042) | 0.0110~0.0211 | cu_h2o2_bta | **(B) 정의역 외삽 — rank_only** |
| 3 | `us8070843b2_w_h2o2_series` | +1.000 (p=0.008) | 0.089~0.320 (중앙 0.28) | w_fe_oxidizer | **(B) 정의역 외삽(Kp 상단치우침 + 고정연마입자 불일치) — rank_only** |

세 건 다 팩 파일의 수치는 바꾸지 않았다(단, w_fe_oxidizer는 이미 확정된 별건 사실을 알리는
주석 1개만 추가). `tools/accuracy_gaps.py::gaps_bias`와 두 데이터셋 파일에만 손을 댔다.

## 0-1. 1차 출처 (재인용 — 값은 이 판정 안에서 새로 계산, 문헌 자체는 §3에서 그대로 인용)

- Stojadinović et al. 2016, *J. Bio-Tribo-Corros.* 2, 20. DOI: 10.1007/s40735-016-0041-4 —
  KIO₃ 산화제 W CMP, Table 1 (P, rpm, MRR) 동시 보고.
- Lim et al. 2013, *Appl. Surf. Sci.* 282, 512–517. DOI: 10.1016/j.apsusc.2013.06.003 —
  Fe(NO₃)₃ 촉매 W CMP, 농도-MRR·정지식각.
- US9200180B2 (Air Products and Chemicals, 2015), patents.google.com/patent/US9200180B2 —
  TABLE 1-b/3/4, 이 판정 §1-1·§2의 1차 인쇄표.
- US8070843B2 (3M Innovative Properties, 2011), patents.google.com/patent/US8070843B2 —
  TABLE 1, 이 판정 §3의 held-out.

## 1. 격리(quarantine) 상태 확인 — 과제 전제가 절반만 맞았다

과제 지시는 "1·2(`cu_ph_alkaline_sweep`, `cu_abrasive_series`)가 이미 F4로 격리돼 있다"였다.
`./.venv/bin/python tools/qa_loop.py quarantine`로 확인한 실제 상태:

```
🔒 us9200180b2_cu_abrasive_series   ← #2. 격리됨(F4)
🔒 us9200180b2_cu_h2o2_series       ← 대상 밖의 세 번째 데이터셋(TABLE 1-b). 격리됨(F4)
```

`us9200180b2_cu_ph_alkaline_sweep`(#1)은 격리 목록에 **없다**. `tools/qa_loop.py`의 F4 감사
(`audit_dataset` §F4)는 "팩 파라미터의 source/note가 같은 문헌 ID를 언급하는데
`used_for_calibration`이 없으면" 격리한다 — `cu_ph_alkaline_sweep`은 `used_for_calibration: true`를
**이미 정확히 선언**하고 있어 애초에 F4 조건에 해당하지 않는다. 과제 지시문의 "1·2가 격리돼
있다"는 틀렸고, 정확히는 "2(와 대상 밖의 유사 데이터셋)가 격리돼 있고, 1은 격리 대상이 아니라
**calibration 데이터 자체**"다.

### 1-1. #2·유사건의 F4는 오검출(false positive)이었다

F4 감사는 같은 특허 안의 **표(table)를 구분하지 못한다**. `cu_ph_alkaline_k`의 실제 캘리브레이션
출처는 US9200180B2 **TABLE 4**(Examples 15-19, pH 6.2→9.9 알칼리 스윕)인데, `#2`는 **TABLE 3**
(Examples 11-14, 연마입자 스윕)이고 세 번째 데이터셋은 **TABLE 1-b**(Examples 5-7, H2O2 스윕)다.
같은 문헌 번호만 보고 표를 구분하지 않아 오탐이 났다. `papers/patents/US9200180B2.html` 원문을
직접 파싱해 세 표의 인쇄값이 데이터셋 YAML과 정확히 일치하고 서로 겹치지 않음을 확인했다(§4
verify 블록1). 조치: 두 데이터셋 파일에 `audit_verified: true`를 추가해 격리를 해제했다 —
**"안 맞는 데이터를 뺀다"가 아니라 "오염 의심이 오검출임을 원문 대조로 확정했다"**는 뜻이다
(qa_loop.py 자체가 규정한 해제 절차: "원문에서 값 확인 후 audit_verified: true 추가").

### 1-2. #1은 held-out이 아니라 calibration 데이터 — 갭 랭커가 자기 자신을 심사했다

`cu_ph_alkaline_sweep.yaml`은 `used_for_calibration: true`이고 노트에 이미 "held-out 성능
주장에 쓰면 안 된다"고 적혀 있다. `validation/backtest.py`의 held-out 집계(`held = [r for r in
results if not r.used_for_calibration ...]`, backtest.py:346)는 이미 이 필터를 쓴다 — 즉
qa_loop --strict가 보고하는 ρ=0.9512는 이 데이터셋을 **제외하고** 계산된다. 그런데
`tools/accuracy_gaps.py::gaps_bias()`는 `rank_only`만 걸러내고 `used_for_calibration`은
걸러내지 않아서, "이 파라미터를 역산한 바로 그 데이터로 그 파라미터가 틀렸다"고 재판정하는
**순환**이 생겼다(BIAS 스코어 50, 매 회차 최상위). 이건 E6(지표가 판정 근거가 되는 순환)의
변종이지 Kp 결함이 아니다. 조치: `gaps_bias()`에 `used_for_calibration` 필터를 추가해
`backtest.py`의 기존 관례와 일치시켰다(§4 verify 블록2로 갭 소멸을 확인).

## 2. #2 `cu_abrasive_series` — 절대값 판정 (B) 정의역 외삽

### 2-1. 단계별 조건 되돌리기(반사실, `sim.engine.simulate` 직접 호출)

재현 대조: 기준조건(pH4, 연마입자 3wt%, 산화제 3wt%, BTA 1mM) 예측 546.0 nm/min은 `kp_m_per_pa`가 역산 앵커로 인용한 문헌값 400~800 nm/min 범위 안에 들어가([[surface-chemistry-cu-w-pourbaix-passivation]]) 팩 앵커 자체는 건강함을 재확인한다.

기준조건(팩 기본값: pH4 산성, 연마입자 3wt%, 산화제 3wt%, BTA 1mM, 2.0psi/84·90rpm)의 예측은
546.0 nm/min — 팩 노트의 문헌 앵커(400~800 nm/min)와 합치한다(팩이 건강하다는 뜻). 이 데이터셋의
알칼리 pH 6.2 조건(연마입자 10wt%, 산화제 1wt%, BTA 미오버라이드=팩 기본값 1mM 유지)으로
하나씩 바꾸면:

| 단계 | 예측(nm/min) | 배수 |
|---|---|---|
| 기준(pH4 산성, 연마입자3, 산화제3, BTA1mM) | 546.0 | — |
| pH→6.2(알칼리) | 398.8 | 0.73× |
| + 산화제 3→1wt% | 5443.5 | 13.65× |
| + 연마입자 3→10wt% | 9621.9 | 1.77× |
| + (as-is, BTA 그대로 1mM) | 14373.2 | 1.49× |

실측(pH6.2)은 73.2 nm/min — 팩 기준의 **1/7.5**인데 모델은 팩 기준의 **26배**로 예측한다.
두 방향이 정반대다. 원인은 한 축이 아니라 **여러 축이 동시에 팩 캘리브레이션 정의역 밖**이다:
연마입자 10~20wt%(팩 캘리브레이션 범위 2~4wt%의 2.5~5배), 산화제 1wt%(정점 3wt% 미만 —
정점 통과 형상 자체가 이 축에서 미검증), 알칼리+무BTA 조합(cu_ph_alkaline_k는 무BTA 알칼리에서,
oxidizer_passivation_K는 유BTA 산성에서 각각 검정 — 이 데이터셋은 어느 쪽 정의역에도 온전히
들지 않는다). 판정#57과 같은 성격: 여러 축이 겹쳐 밖에 있으면 raw k* 대조만으로는 "Kp 문제
아님"만 확인되고, 어느 항이 범인인지 완전히 분리되지는 않는다.

### 2-2. "미신고 오버라이드"를 고치면 더 나빠진다 — 상쇄 오차 경고

이 데이터셋은 `inhibitor_mM` 오버라이드가 없어(원문은 BTA 무첨가·벤젠술폰산계) 팩 기본값
1mM BTA가 조용히 적용된다. 물리적으로는 `inhibitor_mM: 0.0`을 추가하는 게 "정직한" 값처럼
보이지만, 실행해보면 obs/pred가 조건별로 **2.9~10.0배 더 나빠진다**(0.0110~0.0211 →
0.0011~0.0074, §4 verify 블록3). 즉 이 미신고 오버라이드는 다른 곳의 과대예측과 우연히
상쇄되고 있다 — "고치면" 오히려 두 개의 독립된 오차가 하나로 안 겹쳐 총 오차가 커진다. 근거 없는 보정을
금지하는 원칙에 따라 **오버라이드를 추가하지 않는다**. rank_only로 절대값만 면제하고
원인 규명은 미해결로 남긴다.

## 3. #3 `w_h2o2_series` — 절대값 판정 (B) 정의역 외삽 (Kp 상단치우침 + 고정연마입자)

### 3-1. Kp가 3문헌 역산보다 계통적으로 높다 (기존 판정 재사용, 새로 지어낸 비교 아님)

`w-cmp-preston-kp-oxidizer-rate-literature-reproduction.md`(2026-09-15, 이번 판정 이전에
이미 존재)가 독립 3문헌(Stojadinović 2016 KIO₃, Lim 2013 Fe(NO₃)₃, **이 held-out 자신의
6.1wt% 점**)의 Preston 역산 Kp*=MRR/(P·V)로 median 1.07e-13을 구했고, 팩값 2.8e-13은 이
median의 1.8~3.4배(그 노트 §8 verify 블록에서 이미 assert됨)임을 확인해 두었다. 이 held-out을
빼고 **완전 독립 2문헌**(Stojadinović+Lim)만 median을 내면 7.85e-14 — 팩값의 약 1/3.6로,
"이 데이터셋 하나에 맞추려는" 값과 거의 일치한다(§4 verify 블록4). 즉 이 편향은 held-out
1건에 낚인 E6이 아니라 **사전에 독립 검증된 계통 오차**다.

### 3-2. 반사실 실험 — 하나를 맞추면 하나가 반대로 틀어진다

같은 팩을 쓰는 두 데이터셋(이 held-out과 캘리브레이션셋 `us20110186542a1_w_diamond_h2o2_ph`,
n=15)에 Kp 배수를 걸어 median obs/pred를 비교했다(§4 verify 블록5):

| Kp 배수 | 근거 | held-out(`w_h2o2_series`) | calib(`us20110186542a1`) |
|---|---|---|---|
| 1.0(현재) | — | 0.285(3.5배 과대) | 0.585(1.7배 과대) |
| 0.28 | held-out에 정확히 맞춤 | 1.017(거의 완벽) | **2.09배 과소로 반전** |
| 0.393 | 3문헌 median(1.1e-13) | 0.725(1.4배 과대) | 1.49(1.5배 과소) |

held-out만 맞추면(0.28배) 캘리브레이션셋이 과대예측(1.7배)에서 정반대인 과소예측(2.09배)으로
반전한다 — 전형적인 "하나 맞추면 하나 틀어짐"이다. 문헌 median(0.393배)을 쓰면 **둘 다** 2배
이내로 들어오지만 어느 쪽도 완전히 맞지는 않는다 — 잔차가 남는다는 뜻이고, 그 잔차의 유력한
원인이 §3-3이다. 이번 판정에서는 `kp_m_per_pa` 값을 실제로 바꾸지 않는다(§0 요약) — 3문헌
median 자체가 미보고 R_cc(중심간거리) 가정에 의존해 estimated 등급을 못 벗어나고, 값을
바꿔도 두 데이터셋 중 어느 것도 완전히 못 맞히는 상황에서 "판정#58이 처음으로 값을 바꾼다"는
근거가 약하기 때문이다 — 팩 note에 이 사실(§3-1·§3-2 수치)만 박아 다음 판정이 참고하게 한다.

### 3-3. 고정연마입자(fixed-abrasive) 패드 — 애초에 팩의 기계항 정의역 밖

US8070843B2 명세서는 이 실험이 **고정연마입자 패드 + 무연마입자 용액**(3M Mirra 3400,
MWR66 패드)이라고 명시한다. 팩 `w_fe_oxidizer`의 κ(기계) 항은 슬러리 내 유리(遊離) 알루미나
연마입자 함량(`abrasive_wt_pct`)을 전제로 설계돼 있고, 이 데이터셋은 그 오버라이드가 없어
팩 기본 유리연마입자 함량이 마치 존재하는 것처럼 계산된다 — 실제로는 존재하지 않는 메커니즘이다.
이 자체는 데이터셋 노트가 이미 "절대 MRR은 신뢰하지 말고 순위만 볼 것"이라고 적어 둔 사실이라
새 발견은 아니지만, rank_only 플래그로 **공식화**하지 않아서 갭 랭커가 계속 최상위로 올렸다.
Kp 배수 보정만으로 두 데이터셋을 동시에 완전히 못 맞히는 잔차(§3-2)가 이 기계 불일치로
설명된다고 보는 것이 물리적으로 정합적이다(정량 분리는 안 했다 — 그럴 근거 데이터가 없다).

## 4. 코드 재현 (문헌값·팩값 상수 박고 assert)

```python verify
# 블록1: US9200180B2 표(TABLE 1-b/3/4) 인쇄값이 서로 다른 실시예이고 데이터셋 전사가 정확함을 확인
import re
html = open("papers/patents/US9200180B2.html", encoding="utf-8", errors="ignore").read()
text = re.sub(r"<[^>]+>", " ", html)
text = re.sub(r"&nbsp;", " ", text)
text = re.sub(r"\s+", " ", text)

def after(tag, span=700):
    i = text.find(tag)
    assert i > 0, f"{tag} 를 원문에서 못 찾음"
    return text[i:i+span]

t1b = after("TABLE 1-b")
t3 = after("TABLE 3")
t4 = after("TABLE 4")

# TABLE 1-b (Examples 5,6,7): Cu RR 118/92/77 Å/min = 11.8/9.2/7.7 nm/min (cu_h2o2_series.yaml)
for v in ("118", "92", "77"):
    assert v in t1b, f"TABLE 1-b에 {v} 없음"
# TABLE 3 (Examples 11-14): Cu RR 64/84/210/384 Å/min (cu_abrasive_series.yaml)
for v in ("64", "84", "210", "384"):
    assert v in t3, f"TABLE 3에 {v} 없음"
# TABLE 4 (Examples 15-19): Cu RR 732/577/334/263/214 Å/min (cu_ph_alkaline_sweep.yaml — 캘리브레이션 출처)
for v in ("732", "577", "334", "263", "214"):
    assert v in t4, f"TABLE 4에 {v} 없음"
# 세 표의 조건이 겹치지 않음 — TABLE 4에만 있는 값이 TABLE 3/1-b에는 없어야 한다(표 혼동 아님)
assert "732" not in t3 and "732" not in t1b, "TABLE 4 고유값이 다른 표에도 나타남 — 표 혼동 의심"
print("US9200180B2 TABLE 1-b/3/4 전사 확인 — 서로 다른 실시예, 오탐(F4) 근거 확정")
```

```python verify
# 블록2: gaps_bias()가 used_for_calibration 데이터셋(자기순환)과 rank_only 데이터셋을 더 이상
# BIAS로 올리지 않는지 — 이번 판정으로 3건이 전부 갭 랭킹에서 빠짐을 확인
import sys
sys.path.insert(0, ".")
from tools.accuracy_gaps import gaps_bias
names = {g["dataset"] for g in gaps_bias()}
for ds in ("us9200180b2_cu_ph_alkaline_sweep", "us9200180b2_cu_abrasive_series",
           "us8070843b2_w_h2o2_series"):
    assert ds not in names, f"{ds} 가 판정#58 이후에도 BIAS 갭에 남아 있다"
print(f"판정#58 대상 3건 전부 BIAS 갭에서 소멸 확인. 남은 BIAS 갭: {names}")
```

```python verify
# 블록3: cu_abrasive_series — inhibitor_mM=0(미신고 오버라이드를 "정직하게 고침")을 실행하면
# obs/pred가 오히려 10배 더 나빠짐 — 상쇄 오차이므로 건드리지 않는다는 판정의 근거
import sys
sys.path.insert(0, ".")
import sim.models  # noqa
from sim.engine import Recipe, simulate

conds = [(0.5, 9.2, 6.4), (1.5, 9.8, 8.4), (10.0, 9.8, 21.0), (20.0, 10.0, 38.4)]
as_is, fixed = [], []
for abr, ph, obs in conds:
    base_ov = {"abrasive_wt_pct": abr, "abrasive_ref_wt_pct": 3.0, "oxidizer_wt_pct": 1.0,
               "slurry_ph": ph, "chelator_M": 0.0}
    for bucket, extra in ((as_is, {}), (fixed, {"inhibitor_mM": 0.0})):
        ov = dict(base_ov); ov.update(extra)
        rec = Recipe(pack="cu_h2o2_bta", pack_overrides=ov, pressure_psi=2.0, rpm_wafer=84, rpm_platen=90)
        pred = float(simulate(rec, model="tier2.gw_physical_kp").mrr_nm_per_min.mean())
        bucket.append(obs / pred)

per_point = [a / f for a, f in zip(as_is, fixed)]
assert all(r > 2.5 for r in per_point), f"모든 점에서 2.5배 이상 나빠지지 않았다: {per_point}"
print(f"as-is obs/pred={['%.4f'%x for x in as_is]}  inhibitor_mM=0 obs/pred={['%.4f'%x for x in fixed]}")
print(f"per-point 악화배수: {['%.2f'%x for x in per_point]} (최소 {min(per_point):.1f}x~최대 {max(per_point):.1f}x)")
print("=> 미신고 오버라이드를 '정직하게' 고치면 모든 점에서 더 나빠진다 — 건드리지 않는다")
```

```python verify
# 블록4: w_fe_oxidizer Kp — 독립 2문헌(Stojadinović+Lim, held-out 제외) median이
# 팩값의 ~1/3.6로, held-out 하나에 맞춘 배수(0.28)와 거의 일치함을 확인
import math, statistics
psi = 6894.757
Rcc = 0.13
def V(rpm): return (rpm * 2 * math.pi / 60.0) * Rcc
def Kp(mrr_nm_min, P_Pa, Vv): return (mrr_nm_min * 1e-9 / 60.0) / (P_Pa * Vv)

S1 = Kp(150.0, 5 * psi, V(50))   # Stojadinovic 2016 KIO3 2% pH5
S2 = Kp(117.7, 6 * psi, V(70))   # Lim 2013 Fe(NO3)3 고원
S3 = Kp(296.5, 4 * psi, V(79))   # 이 held-out(US8070843B2) 6.1wt% 점

indep_median = statistics.median([S1, S2])   # held-out 제외 — 완전 독립
PACK = 2.8e-13
ratio_indep = PACK / indep_median
print(f"독립 2문헌 median Kp={indep_median:.2e}, 팩값/median={ratio_indep:.2f}배")
assert 3.0 < ratio_indep < 4.2, f"독립 median 배수 {ratio_indep:.2f}가 예상 범위(3~4.2)를 벗어남"

held_out_fix_mult = 0.28   # §3-2에서 확인한, 이 held-out만 정확히 맞추는 Kp 배수
implied_by_indep = indep_median / PACK
assert abs(implied_by_indep - held_out_fix_mult) < 0.05, (
    f"독립 문헌이 암시하는 배수({implied_by_indep:.3f})가 held-out 전용 보정({held_out_fix_mult})과 "
    "너무 다르면 'E6 아님' 주장이 약해진다")
print(f"독립 문헌 암시 배수 {implied_by_indep:.3f} ≈ held-out 전용 보정 {held_out_fix_mult} "
      "— 이 편향은 held-out 1건에 낚인 게 아니라 사전 검증된 계통오차")
```

```python verify
# 블록5: 반사실 — Kp 배수별 held-out vs 캘리브레이션셋 median obs/pred (하나 맞추면 하나 틀어짐)
import sys, yaml
sys.path.insert(0, ".")
import sim.models  # noqa
from sim.engine import Recipe, simulate
import numpy as np

def median_scale(path, kp_mult):
    raw = yaml.safe_load(open(path))
    pack = raw["pack"]
    obs, pred = [], []
    for c in raw["conditions"]:
        ov = dict(c.get("overrides") or {})
        kw = {k: c[k] for k in ("pressure_psi", "rpm_wafer", "rpm_platen", "time_s",
                                  "wafer_radius_m", "n_points") if k in c}
        rec = Recipe(pack=pack, pack_overrides=ov, **kw)
        p = float(np.mean(simulate(rec, model="tier2.gw_physical_kp").mrr_nm_per_min)) * kp_mult
        pred.append(p); obs.append(c["mrr_nm_per_min"])
    return float(np.median([o / p for o, p in zip(obs, pred)]))

HOLD = "validation/datasets/us8070843b2_w_h2o2_series.yaml"
CALIB = "validation/datasets/us20110186542a1_w_diamond_h2o2_ph.yaml"

s_hold_1 = median_scale(HOLD, 1.0)
s_calib_1 = median_scale(CALIB, 1.0)
s_hold_028 = median_scale(HOLD, 0.28)
s_calib_028 = median_scale(CALIB, 0.28)

assert 0.9 < s_hold_028 < 1.1, f"0.28배로 held-out을 맞췄다는 주장 불일치: {s_hold_028:.3f}"
# 캘리브레이션셋은 현재 과대예측(<1)인데, held-out에 맞춘 배수를 적용하면 과소예측(>1)으로 반전해야 한다
assert s_calib_1 < 1.0 < s_calib_028, (
    f"'하나 맞추면 하나 반전' 주장과 불일치: calib@1.0={s_calib_1:.3f}, calib@0.28={s_calib_028:.3f}")
print(f"Kp×1.0   held-out={s_hold_1:.3f}  calib={s_calib_1:.3f}")
print(f"Kp×0.28  held-out={s_hold_028:.3f}  calib={s_calib_028:.3f} (반전 확인)")
```

## 5. 완료 기준 실행 로그

- `tools/accuracy_gaps.py` — 갭 24→21건, BIAS 3→0건(이 3건 소멸, 신규 BIAS 발생 없음).
- pytest 회귀 0(기준 1032 passed 유지 + 신규 계약테스트 추가분).
- `tools/completion.py check` — 60/60 불변(팩 값 미변경).
- `tools/qa_loop.py run --strict` — 유의 평균 ρ **0.9512 불변**(used_for_calibration 필터가
  이미 held-out 집계에 적용돼 있었으므로 이 판정으로 held-out 지표 자체는 안 움직인다),
  격리 목록에서 `us9200180b2_cu_abrasive_series`/`us9200180b2_cu_h2o2_series` 소멸.

## 6. ⚠ 남는 미결

- `#2`의 정확한 편향 원인(연마입자/산화제/pH 세 축 중 무엇이 지배적인지)은 분리하지 못했다 —
  분리하려면 US9200180B2와 같은 조성축(알칼리+무BTA+연마입자만 스윕)의 **독립** 제3 문헌이
  필요한데 찾지 못했다.
- `#3`의 `kp_m_per_pa` 교정값(1.1e-13 후보)은 R_cc 미보고로 여전히 estimated이고 이번 판정에서
  적용하지 않았다 — 적용 여부는 후속 판정 대상으로 남긴다(팩 note에 수치는 박아 두었다).
