---
title: C4 cu_h2o2_bta 병목 진단 (판정#84) — jani2025 MAPE 11730% 원인
status: 완료 — 판정#84 (c) 구조적 한계, 코드·YAML 미변경
---

# C4 `cu_h2o2_bta` 병목 진단 — 판정#84

> Max워커 위임 | 작성일: 2026-09-20
> 관련: 판정#73 [[c4-cu-h2o2-bta-heldout-rho-diagnosis]] (같은 C4 병목, ρ 관점 —
> tw202115224a 형상축을 유일한 유의 held-out으로 확정, jani2025는 비유의라
> C4 숫자에 미반영이라고 결론). 이 노트는 판정#73이 다루지 않은 **jani2025의
> MAPE 11730%**(스케일 오차)를 판다.
> 판정#75(χ 카복실레이트/옥살산 촉진축 신설, 커밋 cff5ab7)가 이 데이터셋의
> ρ를 −0.349→+0.302 로 올렸다는 사실을 이어받아, "왜 순위는 좋아졌는데
> MAPE는 여전히 두 자릿수로 큰가"를 판다.

## §1 현황

`.venv/bin/python -c "from validation.backtest import run_dataset; ..."` 로
직접 재현(§8 verify가 이 값들을 코드로 다시 확인한다):
`jani2025_cu_rsm_composition_heldout`(doi:10.1149/2162-8777/adc59e, Jani et al.
2025) n=13 **ρ=0.3022 p=0.1584(순열)** **MAPE=11730.5%**
`scale_factor=0.010467`(= 예측이 평균 약 95.5배 과대).
p<0.05가 아니므로 C4 게이트(유의 held-out만 평균) 숫자 자체는 안 바뀐다
(판정#73 §2 그대로) — 이 진단은 **격자를 움직이지 않지만**, 지시문이 요구한
"MAPE 폭발 원인 규명"을 독립적으로 완결한다.

## §2 조사 — promoter(χ 카복실레이트/옥살산) 항 분리

`sim/chemistry.py::_carboxylate_promoter_term`을 13개 run에서 각각 떼어내
곱하기 전/후 pred를 비교했다(재현 스크립트는 §5 verify).

| | ρ | p(순열 아님, scipy 근사) | MAPE |
|---|---|---|---|
| 전체 모델(promoter 포함) | **+0.3022** | 0.316 | **11730.5%** |
| promoter 항 제거(나머지 그대로) | **−0.3462** | 0.247 | **848.2%** |

**promoter 항이 MAPE를 848%→11730%로 13.8배 증폭시키면서, 동시에 ρ를
−0.35→+0.30으로 뒤집는다.** 즉 이 항은 "순위는 맞는 방향으로 고치지만
절대 스케일을 크게 희생하는" 트레이드오프를 만든다 — 지시문이 예상한
정확히 그 패턴("순위는 대충 맞는데 스케일이 틀렸다")이다.

promoter 배수(`_carboxylate_promoter_term` 반환값)를 13개 run 전수 출력:

```
E9  oxalic0.08 → 20.40x    E22 oxalic0.02 → 8.11x
E10 oxalic0.02 → 8.11x     E23 oxalic0.05 → 14.81x
E12 oxalic0.05 → 14.81x    E24 oxalic0.05 → 14.81x
E13 oxalic0.05 → 14.81x    E25 oxalic0.02 → 8.11x
E21 oxalic0.05 → 14.81x    E26 oxalic0.08 → 20.40x
E29 oxalic0.08 → 20.40x    E34 oxalic0.03 → 10.54x
E35 oxalic0.06 → 16.76x
```

**13/13(전수) — 부분집합이 아니라 데이터셋 전체가 8.1~20.4배 배수를 맞는다.**
지시문이 예상한 "특정 부분집합에서만 폭발"이 아니라 **promoter_M>0인 모든
조건에서 균일하게 큰 배수가 걸리는 구조적 패턴**이다(Jani RSM 13조건 전부
oxalic0.02~0.08M을 쓰므로 promoter_M=0인 조건 자체가 없다 — §3에서
왜 이 배수가 이렇게 큰지 근본 원인을 판다).

## §3 배수가 큰 근본 원인 — `promoter_ref_M=0` 앵커 + 타계 전이 phi

`_carboxylate_promoter_term`의 함수형: `f(C) = g(C)/g(C_ref)`,
`g(x) = phi + (1-phi)*(x/C_anchor)^m`. 이 팩은 `promoter_ref_M=0.0`
(글리신-only 기준 조성엔 옥살산이 없으므로 Kp 이중계상 방지 목적, 그
자체로는 정당 — `knowledge/params/cu_h2o2_bta.yaml:565` note).
`x=0`이면 `(0/C_anchor)^m=0`이므로 **`g(0)=phi`** — 분모가 통째로
`phi=0.078058`(US6309560B1 통제쌍에서 나온 "기계 성분 바닥" 비율)이 된다.
즉 `f(C) = 1 + ((1-phi)/phi)*(C/C_anchor)^m`이고 `(1-phi)/phi = 11.81`
이라 **C가 0에서 조금만 벗어나도 배수가 즉시 8배 근방에서 시작**한다
(C=0.02M일 때 이미 8.11배).

이 phi=0.078058·m=0.7238·C_anchor=0.0403M **셋 다 US6309560B1**(patents.google.com/patent/US6309560B1)
(Cabot 특허, **알루미나** 연마입자·**옥살산암모늄**·**BTA 없음**·**wetting agent**
50/10ppm·자연 pH — cu_h2o2_bta 팩(콜로이달 실리카·옥살산·글리신 병존·pH 3
산성·BTA 있음)과 연마입자·산 종·pH·BTA 유무 4가지가 전부 다른 계)에서
**타계 전이(transfer)** 됐다 — 이는 `knowledge/params/cu_h2o2_bta.yaml`
`promoter_exponent_m`·`promoter_floor_phi` note 자신이 이미 "confidence=
estimated" 3개 사유로 명시한 사실이고(그 note는 Jani RSM과의 독립
교차확인이 0.02→0.08 배율에서 **19.2% 낮다**는 것도 이미 밝혔다), `sim/
chemistry.py:766` 런타임 note도 "크기는 순위 목적으로만"이라고 매 호출마다
경고한다. **이 진단이 새로 정량화한 것은**: 그 19.2% 오차는 "0.02M과
0.08M 사이의 비"만 비교한 것이라 **C=0 기준 절대 배수(8~20배)의 오차
크기는 검증된 적이 없었다**는 점이다 — EVIDENCE-RULES.md의 등급 체계로
읽으면 이 계수 조합은 **E4**("1차 유도지만 다른 막질/계에서 검증된 것을
전이 → 방향만 채택, 크기는 미채택")에 해당하는데, 실제 구현은 **크기까지
그대로 곱하고 있다** — 다만 이것은 판정#75가 이미 알고 승인한 트레이드오프다
(런타임 note에 "크기는 순위 목적으로만"이 박제돼 있다) — **새로운 결함이
아니라 이미 선언된 한계의 정량적 확인**이다.

## §4 promoter 제거 후에도 남는 MAPE 848% — 별도의 기존 원인

promoter를 떼어도 MAPE 848%가 남는다. 이건 이 진단이 만든 새 사실이 아니라
**같은 팩의 캘리브레이션 데이터셋 자신이 이미 신고한 baseline 편향**이다:
`validation/datasets/jani2025_cu_h2o2_acidic_chelator.yaml`(같은 논문
Expt 30/31/32, `used_for_calibration: true`)의 헤더 주석 —
"⚠ 절대값: 이 조건 엔진 예측 ~10284 nm/min vs 실측 2282 (4.5배 과대).
순위 전용이며 절대 MRR 주장에 쓰지 마라." **캘리브레이션 지점 자체에서도
이미 ~4.5배 과대**라고 팩이 스스로 밝혀 놓았다 — Kp가 역산된 기준 조성
(US20080090500A1, patents.google.com/patent/US20080090500A1,
별도 실험실·별도 툴)과 Jani의 벤치탑(CETR-CP-4, 2인치
디스크, 질량감량법)이 다른 장비·스케일이라 절대값 이전(移轉)에 원래
한계가 있다는 뜻이다. 즉 **promoter 이전에도 이미 알려진 baseline
scale 편향(~4.5~10배)이 있고, promoter가 그 위에 추가로 8~20배를 곱해
전체가 ~95배(scale_factor 역수) 과대로 복합**된다.

## §5 미전달 축 점검 (판정#41 패턴 여부)

지시문이 지목한 "데이터셋이 선언 안 해 팩 기본값으로 조용히 대체되는 필드"를
`jani2025_cu_rsm_composition_heldout.yaml`의 `overrides:` 13건 전수 확인:
`slurry_ph`·`abrasive_wt_pct`·`abrasive_ref_wt_pct`·`oxidizer_wt_pct`·
`inhibitor_mM`·`chelator_species`·`chelator_M`·`sfr_ml_min`·
`promoter_species`·`promoter_M` — **모두 조건마다 명시적으로 선언돼 있다.
이 held-out 데이터셋 자체에는 판정#41류(미선언→팩 기본값으로 조용히
대체) 결함이 없다.**

다만 조사 중 **같은 논문의 다른 데이터셋**(`jani2025_cu_h2o2_acidic_
chelator.yaml`, used_for_calibration:true, §4)에서 이 패턴을 하나
발견했다: 이 조건들은 원문상 글리신 0M(무착화제)인데 `overrides`에
`chelator_M`을 선언하지 않아 팩 기본값(`chelator_M=0.1332`)으로 조용히
대체된다. **다만 수치 영향은 없다** — 직접 계산 확인: `chelator_M`과
`chelator_ref_M`이 똑같이 팩 기본값(0.1332)으로 대체되므로
`_chelator_suppression_term`의 `f(C)=f(C_ref)`가 되어 배수가 항등적으로
1.0이 된다(§5 verify에서 재확인). 즉 "선언 누락"은 사실이지만 "조용히
잘못된 값으로 샌다"(판정#41의 실제 피해 패턴)는 아니다 — 우연히 상쇄된다.
이 데이터셋은 `used_for_calibration: true`라 C4 집계에도 안 들어간다.
**값·코드를 바꾸지 않는다** — 선언을 채워 넣으면(chelator_M: 0.0) 이
데이터셋에 이미 적합된 `oxidizer_acid_chelator_K=0.7935`(판정#41)가 암묵
전제한 "이 축은 1.0"이라는 가정이 깨져 재적합이 필요해지고, 그건 이번
과제(C4 MAPE 진단) 범위를 벗어난다 — 별도 후속 과제로 남긴다.

## §6 판정 — **(c) 구조적 한계, 코드·YAML 미변경**

**jani2025의 MAPE 11730%는 두 개의 이미 알려진(판정#75, 그리고 캘리브레이션
데이터셋 자신의 헤더 경고) 배수 편향이 곱으로 겹친 결과다**: ① promoter
항(χ 옥살산 축, 타계 전이 E4 등급, phi/m/anchor가 US6309560B1 알루미나계
값)이 promoter_ref_M=0 앵커에서 8~20배를 곱하고(§2·§3, 판정#75가 이미
"크기는 순위용"으로 승인한 트레이드오프), ② 그 위에 팩 Kp 자체의 이미 알려진
~4.5~10배 baseline 과대(§4, 캘리브레이션 데이터셋 헤더에 이미 기록됨)가
겹쳐 전체 ~95배 과대(scale_factor 역수)가 된다. **새로운 결함이 아니다** —
promoter 항의 confidence=estimated·"크기는 순위 목적으로만" 경고, baseline
편향의 "절대 MRR 주장에 쓰지 마라" 경고 둘 다 **이미 코드/데이터에 박혀
있었다.** 이 진단이 추가한 것은 두 편향의 **정량적 분해**(§2 표, 848%↔11730%,
13.8배 증폭 기여)와 **13/13 전수 검증**(부분집합이 아니라 구조적임을 확인),
그리고 §5의 미전달 축 전수 점검(결함 없음, 수치 영향 없는 별도 데이터셋
1건만 기록)이다.

**ρ를 올리려고 값을 자유 적합하지 않는다** — 두 앵커(promoter phi/m/anchor,
baseline Kp)를 이 held-out으로 재적합하면 자기채점이 되므로(지시문 절대
금지), 그리고 promoter 축은 이미 §3에서 밝혔듯 EVIDENCE-RULES E4 등급이라
크기 채택 자체가 정책상 "방향만"이어야 한다 — 이미 그렇게 운용되고 있다
(런타임 note로 매번 경고). **격자 숫자는 움직이지 않는다. C4는 예상대로
실패 상태를 유지한다.**

## §7 다음 회차 구체 경로 (참고, 이번 회차 미실행)

1. **promoter 축 절대 배수 재검증**: Cu+콜로이달실리카+옥살산+글리신 계에서
   C=0(옥살산 없음) vs 옥살산 존재 조건을 **직접 대조한 통제쌍**을 가진
   1차 문헌을 확보하면(현재 Jani RSM은 옥살산이 0.02~0.08M 범위에만
   있고 정확히 0인 점이 없어 대조 불가 — §1) phi/m/anchor를 대상계
   고유값으로 교체할 수 있다(E4→E1/E2 승격 경로).
2. **baseline Kp 스케일**: `jani2025_cu_h2o2_acidic_chelator.yaml`이 이미
   지목한 ~4.5배 편향(CETR-CP-4 벤치탑 vs Kp 역산 원조성 툴)의 원인이
   압력/rpm 환산인지 순수 장비 차이인지 분리 조사(이번 회차 범위 밖).
3. §5에서 찾은 `jani2025_cu_h2o2_acidic_chelator.yaml`의 `chelator_M`
   미선언을 채우고 `oxidizer_acid_chelator_K`를 재적합하는 별도 과제
   (수치 영향 없음을 이미 확인했으므로 우선순위 낮음).

## 정직성 표지

- promoter 배수의 "13/13 전수"라는 발견은 이 데이터셋(jani2025 RSM)에
  국한된다 — 다른 팩·다른 데이터셋에서 promoter 축이 어떻게 도는지는
  이번 회차에 재확인하지 않았다.
- §4의 baseline ~4.5배 편향은 이 진단이 새로 측정한 게 아니라 기존
  데이터셋 헤더 주석을 인용한 것이다 — 재현은 이미 그 데이터셋이 하고
  있으므로 이번 verify에서 별도로 재확인하지 않았다.
- EVIDENCE-RULES E4 "크기 미채택" 원칙과 현재 구현("크기까지 곱함, 단
  경고 문구로 상쇄")이 문자 그대로는 어긋난다고 지적했으나, 이것이
  "고쳐야 할 결함"인지 "실용적으로 승인된 예외"인지는 판단하지 않고
  §6에서 후자로 정리했다 — 이 판단에 이견이 있을 수 있음을 남긴다.

## §8 verify

아래 코드가 §1·§2·§3의 핵심 수치를 재현한다: `run_dataset`으로 ρ=0.3022,
MAPE=11730.5%, p=0.1584를 다시 계산해 대조하고, promoter 항을 나눠 제거한
MAPE=848.2%·ρ=−0.3462를 재현한다. promoter 배수 8.11~20.40배(추정값,
US6309560B1 타계 전이 — §3)가 13/13 전수에 걸리는지도 이 블록이 직접
확인한다. §5의 `chelator_M` 미선언 항목은 confidence=estimated인
`chelator_suppression_a`가 실제로 항등 배수 1.0을 내는지까지 재현한다 —
확인 못 한 부분(§7 정직성 표지)은 여기서 재현하지 않고 그대로 미검증으로
남겼다.

```python verify
import sys, yaml
from pathlib import Path
sys.path.insert(0, ".")
from sim.engine import simulate
import sim.models  # noqa: F401
from validation.backtest import _recipe_from, run_dataset
from sim.chemistry import _carboxylate_promoter_term, _chelator_suppression_term
from scipy.stats import spearmanr
import numpy as np

raw = yaml.safe_load(
    Path("validation/datasets/jani2025_cu_rsm_composition_heldout.yaml").read_text())
pack = raw["pack"]
conds = raw["conditions"]

# §1: 공식 backtest 경로로 재현한 보고 수치
result = run_dataset(Path("validation/datasets/jani2025_cu_rsm_composition_heldout.yaml"))
assert result.n == 13
assert abs(result.spearman - 0.3022) < 0.001
assert abs(result.mape_pct - 11730.5) < 1.0
assert abs(result.p_value - 0.1584) < 0.001
assert result.p_value > 0.05          # 비유의 — C4 평균에 안 들어감(판정#73 §2)

# §2~§3: promoter 항 분리
obs, pred, pred_noprom, promF = [], [], [], []
for c in conds:
    rec = _recipe_from(c, pack)
    res = simulate(rec, model="tier2.gw_physical_kp")
    p = float(res.mrr_nm_per_min.mean()) if hasattr(res.mrr_nm_per_min, "mean") \
        else float(res.mrr_nm_per_min)
    rr = rec.resolve()
    f = _carboxylate_promoter_term(rr.pack, [])
    obs.append(c["mrr_nm_per_min"]); pred.append(p)
    promF.append(f); pred_noprom.append(p / f)

def mape(p, o):
    return float(np.mean([abs(a - b) / b for a, b in zip(p, o)]) * 100.0)

rho_np, p_np = spearmanr(pred_noprom, obs)
mape_full = mape(pred, obs)
mape_np = mape(pred_noprom, obs)

assert abs(rho_np - (-0.3462)) < 0.01
assert 700 < mape_np < 1000
assert mape_full / mape_np > 13.0      # promoter 항이 MAPE를 13배 이상 증폭

# 13/13 전수 — 부분집합이 아니다
assert len(promF) == 13
assert all(f > 1.0 for f in promF)
assert min(promF) > 8.0 and max(promF) < 21.0

# §5: chelator_M 미선언 캘리브레이션 데이터셋 — 수치 영향 없음(항등 1.0) 재확인
calib = yaml.safe_load(
    Path("validation/datasets/jani2025_cu_h2o2_acidic_chelator.yaml").read_text())
c0 = calib["conditions"][0]
assert "chelator_M" not in c0["overrides"]     # 미선언 사실 확인
rec0 = _recipe_from(c0, calib["pack"])
rr0 = rec0.resolve()
v_chel = _chelator_suppression_term(rr0.pack, [])
assert v_chel is not None
assert abs(v_chel - 1.0) < 1e-9   # C == ref(둘 다 팩 기본값) → 항등 1.0, 수치 왜곡 없음

print("전체 rho=%.4f MAPE=%.1f%% / promoter제거 rho=%.4f MAPE=%.1f%% (증폭 %.1f배)" %
      (result.spearman, mape_full, rho_np, mape_np, mape_full / mape_np))
print("promoter 배수 범위: %.2fx ~ %.2fx (n=%d, 전수)" % (min(promF), max(promF), len(promF)))
```
