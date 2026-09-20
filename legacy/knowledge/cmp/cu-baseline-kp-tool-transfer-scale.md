---
title: cu_h2o2_bta baseline Kp ~4.5배 과대 원인 분리 (판정#86)
status: 완료 — 판정#86 (c) A/B 둘 다 기각, 실제 원인은 이미 알려진 ψ 정의위반(판정#17·#24)
---

# `cu_h2o2_bta` baseline ~4.5배 과대 원인 분리 — 판정#86

> Max워커 위임 | 작성일: 2026-09-20
> 선행: [[c4-cu-h2o2-bta-heldout-diagnosis]](판정#84) §4·§7-2 — jani2025 held-out
> MAPE 11730%를 ①promoter(χ 옥살산, 판정#85가 별도 추적 중 — **이 노트는 건드리지
> 않는다**) × ②이 baseline ~4.5배의 곱으로 분해했고, §7-2가 "②가 압력/rpm 환산
> 문제(A)인지 순수 장비 차이(B)인지는 다음 회차"로 남겼다. 이 노트가 그 다음 회차다.
> 대상: `validation/datasets/jani2025_cu_h2o2_acidic_chelator.yaml`(Expt 30/31/32,
> `used_for_calibration: true`) 헤더가 스스로 신고한 "~10284 vs 2282 (4.5배 과대)".

## §0 출처

1. C. Jani et al. (2025), *ECS J. Solid State Sci. Technol.* 14(4) 044003,
   doi:10.1149/2162-8777/adc59e — `papers/jani2025-revisiting-roles-cu-cmp.html`.
2. T. E. Tugbawa (2002), MIT PhD thesis, hdl.handle.net/1721.1/8083 —
   Table 3.3 블랭킷 Cu 제거율 r_cu.
3. Zhao, Wang, He, Lu (2012), *IEEE Trans. Semicond. Manuf.* 25(3), 502–510,
   doi:10.1109/TSM.2012.2190432 — r_cc=200mm(300mm 툴) 근거.
4. Lai (2001) MIT PhD thesis Eq. 2.10–2.12 — `sim/tier1_empirical/kinematics.py`
   docstring 재인용, 동속(Rs=1) 균일속도 극한식.
5. US20080090500A1 (PPG Industries, 2008-04-17 공개), patents.google.com —
   `cu_ph_acid_k` 계열 근거(직접 사용 안 함, 대조용).

## §1 결론 먼저

**가설 A(P·V 단위/환산)도 가설 B(순수 장비 스케일)도 주 원인이 아니다.**
Preston 항(P·V·Kp)만 떼어 보면 오히려 **관측치를 2.8배 과소예측**한다(§3) — 방향이
반대라 "P·V가 부풀렸다"는 A 가설은 이 조건에서 성립할 수 없다. 실제 배수 4.51배는
전부 **ψ(표면 보호도) 인자**에서 나온다: 이 조건은 BTA 없음(`inhibitor_mM=0`)인데
팩의 `inhibitor_ref_mM=1.0`(BTA 1mM 기준)과 비교되면서 ψ=9.969가 곱해진다(§4).
**이 메커니즘은 새로 발견한 게 아니다** — `sim/factors.py::_f_psi`가 이미 런타임
경고로 "ψ>1은 정의(≤1) 위반, inhibitor_ref_mM이 범위 하단이 아니라 중간에 있다는
뜻"이라고 매 호출마다 신고하고 있고, 그 기준점의 estimated 등급 자체가 판정#17·#24가
이미 매긴 것이다. 이번 회차가 새로 한 일은 "그 이미 알려진 정의위반이 **이 정확한
held-out 조건의 4.5배 과대를 몇 배 중 몇 배까지 설명하는지**"를 처음으로 숫자로
분리한 것이다. **코드·YAML은 건드리지 않는다** — 고치려면 `inhibitor_ref_mM`을
문헌 그라운딩된 값으로 옮겨야 하는데, 그건 판정#17/#24와 같은 급의 별도 캘리브레이션
결정이라 이 판정 범위 밖이다(§6).

## §2 조건 대조표 — Jani(CETR-CP-4) vs 팩 Kp 역산 앵커

`kp_m_per_pa=3.5e-13`은 특정 논문 1편의 (P,V)에서 단일 역산된 값이 아니라(과제
지시문의 전제와 달리) "일반 문헌 MRR 범위 400~800 nm/min @ 2~3psi"라는 대표값이고
([[cu-kp-preston-coefficient-literature-back-calculation]] §1), 그 노트가 이후
다중 문헌(Guo 2004·wei2013·**Tugbawa 2002**·Li&Babu 2001)으로 교차검증한 결과
**Tugbawa(Mirra 생산용 툴, 4 psi·75 rpm)의 역산 Kp=3.67e-13이 팩값과 5% 이내로
가장 근접**했다(같은 노트 §6). 그 지점을 사실상의 "앵커"로 놓고 비교한다.

| | Jani 2025 (CETR-CP-4, Expt 30) | Tugbawa 2002 (Mirra, 앵커) |
|---|---|---|
| 압력 | 3.0 psi = 20684 Pa | 4.0 psi = 27579 Pa |
| rpm | wafer 90 / platen 90 (paper는 platen만 명시 — §5) | wafer 75 / platen 75 (Mirra 동속 가정) |
| r_cc(center_offset_m) | **미선언 → 팩 기본값 0.200 m**(SEMI 300mm 툴, Zhao 2012) | 0.200 m(같은 가정, 노트가 명시적으로 가정했다고 표기) |
| V = ω_p·r_cc | 1.885 m/s | 1.571 m/s |
| V 비율 | **1.885/1.571 = 1.20배** | — |
| 시료 | 2인치(5.08cm) Cu 디스크, 벤치탑 pin형 | 300mm 웨이퍼, 생산용 CMP |

**핵심 관찰**: `rpm_wafer=rpm_platen`(Rs=1)이면 `sim/tier1_empirical/kinematics.py`의
Lai(2001) 극한식에 의해 속도가 웨이퍼 전면에서 균일 `|v|=ω_p·r_cc`가 되고 **웨이퍼
반경(wafer_radius_m)은 소거된다** — 즉 2인치 디스크든 300mm 웨이퍼든 이 변속비에서는
r_cc만 V를 결정한다. **그런데 두 데이터셋 모두 CETR-CP-4의 실제 r_cc(플래튼 중심-시료
중심 거리)를 선언하지 않고 있다** — Jani도 Tugbawa도 똑같이 팩 기본값(0.200m, 300mm
production 툴용 Zhao 2012 수치)을 물려받는다. 이것은 판정#41류의 "미선언→조용히 팩
기본값 대체"이지만, **양쪽(캘리브레이션 앵커·held-out)에 동일하게 적용되므로 상쇄된다**
— V 비율은 90/75=1.20배뿐이다. **이 1.20배로는 4.51배를 설명할 수 없다.**

## §3 Preston(P·V) 항만 분리 — 설명되는가? **아니다, 오히려 반대 방향**

`GWPhysicalKpModel`은 기준점(면적평균 P,V)에서 alpha를 역산해 GW로 돌리므로, 단일
균일 조건(Rs=1이라 반경 전체 P,V 균일)에서는 `Kp·P·V`와 **수치적으로 동일**하다
(코드로 직접 확인, §7 블록1).

```
Kp·P·V = 3.5e-13 × 20684 Pa × 1.885 m/s = 818.8 nm/min  (화학 배수 곱하기 전)
관측값                                    = 2282.0 nm/min
비율                                      = 0.359배  ← P·V만으로는 2.8배 "과소"예측
```

**가설 A(P·V 환산이 4.5배를 만든다)는 이 시점에서 기각된다** — 방향이 반대다.
P·V·Kp 단독은 관측치보다 작다. 4.51배 과대는 이 이후 곱해지는 화학 인자에서 나온다.

## §4 실제 원인 — ψ(표면 보호도) 정의위반, 이미 알려진 결함(판정#17·#24)

`sim/engine.py::simulate`는 `mrr_m_s = mrr_m_s(P,V 경로) × fmult`이고 `fmult`는
`κ·χ·ψ`(τ는 이 조건 1.0)만 곱한다(Λ Π Θ 등은 진단 전용, MRR 비적용 — 코드 주석
"여기서 chemistry_factor()를 직접 곱하지 않는다" 근방). 이 조건에서 실측:

```
fmult = 12.5606  (χ=1.0000, κ=1.2599, ψ=9.9693, τ=1.0000)
예측 = 818.8 × 12.5606 = 10284.2 nm/min   ← §1 보고값과 일치
```

**ψ=9.9693이 지배한다.** `sim/factors.py::_f_psi`의 억제제 경로(`_inhibitor_term`)는
`inhibitor_mM`을 팩의 `inhibitor_ref_mM=1.0`(BTA 1mM) 대비 **상대값**으로 계산한다
— Kp가 이미 기준 슬러리에서 역산됐다는 전제로 이중계상을 막는 설계다. 이 조건은
Jani가 **BTA를 전혀 쓰지 않는다**(`inhibitor_mM: 0.0`, Table I 확인) — 기준(1mM)보다
**적은** 억제제이므로 상대 배수가 1을 넘는다. 코드는 이걸 조용히 통과시키지 않고
**매 호출마다** 이렇게 경고한다(§7 블록2로 재현):

> "⚠ ψ=9.969 > 1 — 정의(표면 보호 ≤1) 위반. 기준 농도보다 억제제가 적은 조건이라
> 상대값이 1을 넘었다. 이 팩의 inhibitor_ref_mM이 검증 조건 범위의 하단이 아니라
> 중간에 있다는 뜻이다. 기준점을 범위 하단(보통 0)으로 옮기거나, 억제 항을 ψ가
> 아니라 별도 팩터로 분리해야 한다."

그리고 그 함수 자신의 독스트링이 이미 다른 조건(억제제 0, 예측 9085 vs 실측 19.2)에서
같은 실패 패턴을 예시로 들고 있다 — **이 결함은 이번에 발견한 게 아니라 코드에 처음부터
박혀 있던 자기신고다.** `inhibitor_ref_mM=1.0`의 confidence가 `estimated`로 내려간
사유(판정#24, `psi-inhibitor-strength-k-grade-ruling.md §A.4`)도 정확히 이 문제의
뿌리를 이미 지목했다: "Kp가 1.0mM BTA 조성에서 역산됐다는 근거 자체가 성립하지 않는다."

**감도 확인**(반사실, 코드 변경 없이 계산만 — §7 블록3): ψ를 1.0으로 고정하면(즉
BTA 유무 축을 완전히 끄면) 예측은 818.8×1.2599×1.0=1031.6 nm/min, 관측(2282) 대비
0.452배(2.2배 **과소**). 즉 ψ를 끄면 방향이 다시 뒤집힌다 — "ψ가 없으면 딱 맞는다"도
아니다. **잔여 배수(약 2.2배)는 아직 원인이 갈리지 않은 채 남는다**(κ=1.26·abrasive
6wt%↔ref 3wt%·pH·시료 스케일 등 여러 항이 얽혀 있고, 이 노트가 그 전부를 분리하지는
못했다 — 정직성 표지 참조).

## §5 원문 대조 (과제 3번) — 전사 오류 없음

`papers/jani2025-revisiting-roles-cu-cmp.html` 직접 판독(fitz 아님, HTML 텍스트):
"Polishing was performed at **a pressure of 3.0 psi and a platen speed of 90 rpm**."
"2-inch copper disks", "flow rate of 150 ml min⁻¹", "polishing time was generally
**2 min**". Table II 값 재확인: Expt 30/31/32/33 = **2282/2533/2578/2326** nm/min —
데이터셋 YAML과 정확히 일치(전사 오류 없음). **주의**: 원문은 `rpm_wafer`(캐리어/헤드
회전수)를 전혀 보고하지 않는다 — "platen speed 90 rpm"만 명시. 데이터셋이
`rpm_wafer=90`을 채운 것은 **가정**(co-rotation, Rs=1)이며 원문이 확인해 주는 값이
아니다. 이 가정이 틀렸다면(예: 시료가 고정 pin이라 자전 없음) 엄밀히는 Rs≠1 식을
써야 하지만, Rs=1 극한이 이미 "웨이퍼 전면 균일 속도=ω_p·r_cc"로 wafer_radius_m을
소거하므로 순수 pin(자전 없음, 반경=0인 극한)과 결과가 **동일**하다 — 이 가정은
우연히 무해하다(§7 블록4 확인).

## §6 mass-loss→MRR 변환 확인 (과제 4번) — 개입 없음

`read_method: table`이므로 데이터셋은 논문이 **이미 계산해 인쇄한** "Cu RR"(nm/min)
칼럼을 그대로 옮긴다 — 우리 코드가 질량감량(Δm/(ρ·A·t))을 따로 계산하는 경로는 이
데이터셋에 없다(`ρ=8.96 g/cm³`·`A=20.27 cm²`는 논문 본문 서술일 뿐, 우리 backtest는
그 계산 결과값만 쓴다). **밀도 나눗셈 누락/중복 가설은 기각** — 애초에 우리 코드가
그 나눗셈을 하지 않는다.

## §7 판정 — 기존 EVIDENCE-RULES 등급으로 정리

- **가설 A(P·V 환산) 기각**: §3에서 방향이 반대(과소예측)임을 직접 계산 확인.
  §2의 r_cc 미선언은 실재하는 판정#41류 결함이지만 앵커·held-out 양쪽에 동일하게
  적용돼 상쇄되고(비율 1.20배), 4.51배 규모를 설명 못 한다.
- **가설 B(순수 장비 차이) 기각**: "장비가 다르다"는 사실이지만, 그 차이가 수치로
  드러나는 경로가 P·V가 아니라 **ψ 인자**임을 §4가 특정했다. "장비 차이"로 뭉뚱그리면
  이미 코드가 정확히 지목하고 있는 원인(inhibitor_ref_mM 기준점 위치)을 가린다.
- **실제 원인**: ψ(표면 보호도) 인자가 `inhibitor_ref_mM=1.0`(estimated, 판정#24가
  "이 값이 Kp와 조성 일치를 이룬다는 근거 없음"으로 이미 하향)을 기준점으로 삼아 계산
  되는데, BTA 없는 held-out 조건은 이 기준점보다 낮은 쪽이라 상대 배수가 1을 초과
  한다. 이 메커니즘과 그로 인한 위험은 `sim/factors.py::_f_psi`가 런타임 경고로 **이미
  스스로 신고하고 있다** — E-등급으로 말하면 이건 "새 결함"이 아니라 **이미 판정된
  estimated 한계의 정량적 사례 확인**이다(판정#84가 promoter 축에 대해 내린 것과
  같은 유형의 결론).
- **고치지 않는 이유**: `inhibitor_ref_mM`을 옮기려면(코드 자신이 제안한 "범위 하단
  0으로 이동" 또는 "별도 팩터 분리") 이 파라미터를 쓰는 **cu_h2o2_bta의 다른 모든
  캘리브레이션 지점**(US20080090500A1 TABLE 4 계열 등, BTA=1mM 고정)에 미치는 영향을
  전부 재확인해야 하는 독립 캘리브레이션 결정이다 — 이 held-out 하나에 맞춰 조용히
  옮기면 그 자체가 자기채점이 된다(지시문 금지 사항과 같은 성격의 위험). **판정#17·
  #24가 이미 이 파라미터를 estimated로 심사했고, 그 이상은 이번 판정 범위 밖이다.**
  Kp에 보정계수를 곱하지 않았고(금지 사항 준수), promoter(χ) 축도 건드리지 않았다.
- **격자 영향**: 없음. C4는 판정#73/#84 그대로 실패 상태 유지(코드·YAML 0변경이므로
  당연하다).

## 정직성 표지

- §4 말미의 "잔여 ~2.2배"는 이 노트가 분리하지 못했다 — κ(접촉강도, abrasive
  6wt%↔ref 3wt%)·pH 항·시료 스케일 등 여러 항이 남아 있고, 그중 무엇이 얼마나
  기여하는지는 **후속 판정(번호 미할당 — 원장에 없는 번호를 미리 인용하지 않는다)** 몫이다.
  **A/B 어느 쪽도 이 잔여를 설명한다고 주장하지 않는다.**
- §2의 "r_cc 미선언이 앵커·held-out 양쪽에 동일 적용돼 상쇄된다"는 주장은 **Tugbawa
  Mirra(300mm 생산 툴)에 r_cc=0.2m 가정이 원래도 타당했다는 것**과 **CETR-CP-4(2인치
  벤치탑)에도 우연히 비슷한 크기가 맞는다는 것**은 별개 주장이다 — 후자는 확인하지
  못했다(CETR-CP-4의 실제 플래튼-시료 축간거리는 어떤 1차 문헌에서도 찾지 못함, 웹
  접근 차단으로 제조사 스펙도 확인 못 함). 다만 이 불확실성이 있어도 §3의 핵심 결론
  (P·V가 과소예측 방향이라 A를 기각한다)은 r_cc 값 자체에 좌우되지 않는다 — r_cc를
  키워 V를 올려도 P·V·Kp가 4.5배 이상 커지려면 r_cc가 현재 가정보다 2.8배 이상
  커야 하는데, 그러면 앵커(Tugbawa)쪽 Kp 역산도 같이 뒤틀려 팩값 자체가 바뀐다 —
  이 경로는 탐색하지 않았다(범위 밖).
- §5의 "co-rotation 가정이 우연히 무해하다"는 Rs=1 극한(균일속도)에서만 성립한다 —
  원문이 실제로는 Rs≠1(예: 자전 없는 고정 pin, ω_w=0)이라면 kinematics 식이 달라져야
  하고, 그 경우 §2의 V 비교 자체가 무효가 된다. 이건 원문이 확인해 주지 않는 이상
  구조적으로 확인 불가능하다.

## §8 verify

```python verify
import sys, yaml
import numpy as np
sys.path.insert(0, ".")
from sim.engine import simulate, PSI_TO_PA
from sim.models import GWPhysicalKpModel
import sim.models  # noqa: F401
from validation.backtest import _recipe_from
from sim.tier1_empirical import kinematics as kin
from sim.factors import compute_factors, mrr_multiplier

calib = yaml.safe_load(
    open("validation/datasets/jani2025_cu_h2o2_acidic_chelator.yaml"))
pack = calib["pack"]
c0 = calib["conditions"][0]           # Expt 30, H2O2 3wt%
rec = _recipe_from(c0, pack)
rr = rec.resolve()

# ── 블록1: 기하·속도 — r_cc 미선언 → 팩 기본값 0.200m, wafer_radius는 Rs=1이라 무관
assert rr.center_offset_m == 0.200
assert rr.rpm_wafer == rr.rpm_platen == 90
V = kin.speed_stats(rr.wafer_radius_m, rr.center_offset_m,
                     rr.rpm_wafer, rr.rpm_platen)["mean"]
assert abs(V - 1.884955) < 1e-4
V_tugbawa = kin.rpm_to_rads(75) * 0.200
assert abs(V_tugbawa - 1.570796) < 1e-4
assert abs(V / V_tugbawa - 1.20) < 0.01     # 앵커 대비 속도비 1.20배뿐

# ── 블록2: Preston(P·V·Kp) 단독 — GW 모델이 이 균일조건에서 Kp·P·V와 수치일치
radius = np.linspace(0.0, rr.wafer_radius_m - rr.edge_exclusion_m, rr.n_points)
mrr_ms = GWPhysicalKpModel().mrr_radial(rr, radius)
preston_nm_min = float(np.mean(mrr_ms)) * 1e9 * 60.0
P_pa = rr.pressure_psi * PSI_TO_PA
kp_pv_nm_min = rr.kp_m_per_pa * P_pa * V * 1e9 * 60.0
assert abs(preston_nm_min - kp_pv_nm_min) / kp_pv_nm_min < 0.01
assert abs(preston_nm_min - 818.8) < 2.0
obs = c0["mrr_nm_per_min"]
assert obs == 2282.0
ratio_preston_only = preston_nm_min / obs
assert ratio_preston_only < 1.0                 # 가설 A 기각: 방향이 반대(과소)
assert abs(ratio_preston_only - 0.3588) < 0.005

# ── 블록3: 전체 예측(ψ 포함) = 보고된 4.51배 재현, ψ가 지배 인자
res = simulate(rec, model="tier2.gw_physical_kp")
pred_full = float(res.mrr_nm_per_min.mean()) if hasattr(res.mrr_nm_per_min, "mean") \
    else float(res.mrr_nm_per_min)
assert abs(pred_full - 10284.2) < 1.0
assert abs(pred_full / obs - 4.507) < 0.01

factors = compute_factors(rr)
fmult, fnotes = mrr_multiplier(factors)
assert abs(fmult - 12.5606) < 0.01
assert abs(factors["psi"].value - 9.9693) < 0.01
assert abs(factors["kappa"].value - 1.2599) < 0.01
assert abs(factors["chi"].value - 1.0) < 1e-6
assert any("정의" in n and "위반" in n for n in factors["psi"].notes), \
    "ψ>1 정의위반 런타임 경고가 사라졌다 — 코드가 바뀌었으면 이 노트를 재검토하라"

# ψ를 반사실로 1.0 고정 — 여전히 관측치와 안 맞음(방향이 다시 반대로 뒤집힘)
pred_no_psi = preston_nm_min * factors["kappa"].value * factors["chi"].value
assert abs(pred_no_psi - 1031.6) < 2.0
assert pred_no_psi / obs < 1.0                  # ψ 없이는 다시 과소예측(0.452배 근방)
assert abs(pred_no_psi / obs - 0.452) < 0.01

# ── 블록4: Rs=1(co-rotation) 가정이 순수 pin(ω_w=0, R_w→0 극한)과 속도가 같음
v_corot = kin.relative_velocity(0.05, 0.0, kin.rpm_to_rads(90), kin.rpm_to_rads(90),
                                 rr.center_offset_m)[2]
v_pin = kin.rpm_to_rads(90) * rr.center_offset_m   # 순수 pin: |v|=ω_p·r_cc, R_w 무관
assert abs(float(v_corot) - v_pin) < 1e-9

# ── 블록5: 원문 Table II 인쇄값(Expt 30~33) 데이터셋 전사 확인
import re
html = open("papers/jani2025-revisiting-roles-cu-cmp.html", encoding="utf-8",
            errors="ignore").read()
text = re.sub(r"<[^>]+>", " ", html)
text = re.sub(r"\s+", " ", text)
assert "3.0 psi and a platen speed of 90 rpm" in text
assert " 30 2282 " in text and " 31 2533 " in text and " 32 2578 " in text

print("Preston 단독 %.1f nm/min (%.3f배, 과소) | 전체 예측 %.1f nm/min (%.3f배, ψ=%.3f 지배)"
      % (preston_nm_min, ratio_preston_only, pred_full, pred_full / obs, factors["psi"].value))
```
