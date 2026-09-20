# model_hygiene.py 극한(L) 검사의 조용한 건너뜀 제거 — time_s·dispersant_type·chelator_M/promoter_M

EVIDENCE-RULES 판정#95(2026-09-20). 관련: [[slurry-turnover-ratio-mrt-preston-constant]],
[[psi-glycine-chelator-suppression-cu-jani2025]], [[chi-carboxylate-promoter-cu-oxalate-us6309560]].

## 1. 문제

`tools/model_hygiene.py`의 극한(L) 검사에서 팩 7개 × 드라이버 전수 순회 중
11건이 "극한값으로 바꾸지 못함"(warn)으로 끝나 **검사가 수행되지 않았는데**
조용한 경고 한 줄로만 보고됐다(time_s 7팩 + dispersant_type 4팩). `model_hygiene.py`
자신의 docstring과 `sim/factors.py::LIMIT_ROLE` 주석이 "미선언은 통과가 아니라
결함이다", "검사기가 조용히 건너뛰면 '위반 없음'으로 잘못 읽힌다"고 명시하므로
이것은 스타일 문제가 아니라 설계 의도 위반이다. 원인은 두 갈래:

1. `time_s`는 팩 YAML 키가 아니라 `sim.engine.Recipe` 필드라 `_write_value()`의
   YAML 정규식 치환이 영원히 실패한다.
2. `dispersant_type`은 문자열 범주형이라 숫자 정규식이 매칭되지 않는다.

추가로, 이 조사 과정에서 `sim/factors.py::LIMIT_ROLE`에 등록되지 않은
드라이버(`chelator_M`, `promoter_M`)와 `_f_psi`의 ψ>1 정의위반 검사가
착화제 항을 곱하기 **전**에만 걸려 있어 사각지대를 만드는 결함을 발견했다.

## 2. 실물 A — τ의 time_s=0 불연속 (진짜 물리, 인공물 아님)

```
time_s=0.0     tau=1.0                  drivers에 time_s 없음(항이 자기 스스로 꺼짐)
time_s=1.0     tau=0.05211867631070653
time_s=30.0    tau=0.9576264737858694
time_s=60.0    tau=1.0                  (기준점)
```

원인: `sim/factors.py::_f_tau`의 `if t_pol > 0 and t_ref > 0:` 가드. 이 항은
Philipossian 2004(doi:10.1149/1.1731539) TR=1.13→370Å vs TR=0→500Å(26% 감소)
실측과 Mu et al. 2016(doi:10.1016/j.mee.2016.02.035, Table 3) 그루브 폭→MRT
실측으로 역산한 폐형식이다([[slurry-turnover-ratio-mrt-preston-constant]] §2·§3
에 이미 문헌값 대조·재현 기록이 있다 — 여기서는 재도출하지 않는다). t=0
이면 TR(턴오버비) 항 전체가 계상되지 않고 배수는 항등적으로 1.0이 되며
드라이버 목록에서도 `time_s`가 사라진다. **모델을 고쳐 연속으로 만들지
않는다** — t=0("연마를 하지 않았다")에는 τ의 정의 자체가 없다. 대신
`_f_tau`가 이미 `f.notes`로 신고하고 있었다(`⚠ τ turnover 항 미적용:
폴리시 시간(time_s)이 0 이하다.`) — 이번 작업은 이 "신고됨"과 "신고 안
됨"을 model_hygiene.py가 구분해서 판정하게 만드는 것이지, τ의 물리를
바꾸는 것이 아니다(미검증 재도출 없음).

## 3. 실물 B — chelator_M=0에서 ψ=1.223 > 1 (사각지대)

```
base           mult=1.000000  chi=1.0  psi=1.0
chelator_M=0   mult=1.223096  chi=1.0  psi=1.2230956708315368   ← ψ>1
```

`_chelator_suppression_term`(Jani 2025, doi:10.1149/2162-8777/adc59e, Table
I×II 통제쌍 2건 + 회귀 [glycine]=−440.91, p=4.08e-7)은 `exp(-a·(C-C_ref))`
꼴이라 C=0(착화제 없음)에서 C_ref=0.1332 mol/L 대비 배수가 1을 넘는다 —
[[psi-glycine-chelator-suppression-cu-jani2025]] §자체가 이미 "2점 적합이라
절대 크기는 순위 목적으로만 쓸 것"이라고 경고한 항이 정의역 밖(C=0)에서
정확히 그 경고대로 터진 사례다. `_f_psi`의 ψ>1 정의위반 검사(표면 보호 ≤1)가
곱하기 **전의** 억제제 항에만 걸려 있어 이 경우를 못 잡았다. 범위 검사
([0,5])도 1.223은 통과한다. 기존 종결 판정(#17·#24A~C·#39 — `cu_h2o2_bta
psi=9.969`·`w_fe_oxidizer psi=8.178`, 둘 다 `inhibitor_mM=0` 조건)과는
**다른 축**(`chelator_M`)·**다른 수치**·`validation/adjudicated_violations.yaml`의
`value` 대조 규칙상으로도 자동으로 별개 취급되므로, 이는 독립 결함으로
판정#95에 등록한다(하류 증상 아님 — 상류 갭이 다르다).

## 4. 조치

- `sim/factors.py::_f_psi` — 정의위반 검사를 착화제 항 곱셈 **후**의
  최종 v에 걸도록 이동(판정#95). MRR 수치는 불변(§6 bit-invariance 확인) —
  검사 위치만 옮겼다.
- `sim/factors.py::LIMIT_ROLE` — `chelator_M`, `promoter_M`을 MODULATOR로
  등록. 판정 절차(①0이 '없음'인가 ②0에서 제거 경로가 남는가)를 그대로 적용:
  `chelator_M=0`은 억제제가 없는 상태이고 χ·inhibitor_mM 경로가 남으며
  (`inhibitor_mM`과 동형), `promoter_M=0`은
  [[chi-carboxylate-promoter-cu-oxalate-us6309560]]의 phi(기계 바닥,
  US6309560B1 TABLE 1 역산 phi=0.07806)가 유한 양수로 남아 순수 기계 경로가
  죽지 않는다.
- `sim/factors.py::CATEGORICAL_ABSENT` 신설 — 범주형 드라이버의 "없음" 값을
  모델이 선언(`dispersant_type` → `"NONE"`, 기존 `_dispersant_protection_term`
  docstring 관례 — Li et al. 2021, doi:10.1149/2162-8777/ac3e44, §6 기준선
  2700 Å/min — 를 승격했을 뿐 새로 지어내지 않았다).
- `tools/model_hygiene.py::check_limits` — Recipe 필드 드라이버는
  `dataclasses.fields(Recipe)`로 introspect해 Recipe kwarg로 주입(하드코딩
  금지), 범주형은 `CATEGORICAL_ABSENT` 조회, 둘 다 아니면서 YAML 치환도
  실패하면 (2026-09-20 이전 warn →) **error**로 격상. MODULATOR/AGENT 판정
  직전에 "그 드라이버가 여전히 실제로 보고됐는가"(`driver_seen`)를 확인해,
  항이 스스로 비활성화된 경우(t=0의 τ처럼)는 통과/위반 대신 별도의 미확인
  경고로 분리한다 — "MODULATOR 통과"로 잘못 읽지 않도록.

## 5. 결과

이전: 극한(L) 검사 결과 21건 중 11건이 "바꾸지 못함"(time_s 7 + dispersant_type
4). 이후: 0건. `time_s`는 7팩 전부 "항이 스스로 비활성화됨"(정보성 warn,
role 판정 보류)으로 대체됐고, `dispersant_type`은 `CATEGORICAL_ABSENT`
경로로 실제 극한 검사(MODULATOR: m>0 확인)를 통과했다. `chelator_M`·
`promoter_M`은 LIMIT_ROLE 등록 후 실제 0-probe를 통과(각각 m=1.223>0,
m=1.0>0 — MODULATOR 정의 위반 없음).

미검증으로 남긴 것: `_INTENSIVE_PROBES`·`CATEGORICAL_ABSENT`에 없는 향후
신규 드라이버가 재발시키는 것은 `tests/test_model_hygiene_limit_probes.py`의
`test_limit_role_keys_all_have_a_check_path`가 막지만, 이 테스트는
`relative_velocity_m_s`처럼 **LIMIT_ROLE엔 있으나 어느 팩터도 드라이버로
보고하지 않는** 선언은 스코프 밖으로 걸러낸다 — 그 키가 실제로 쓰이게 될 때
같은 성질 검사가 자동으로 걸린다(추정이며 실측 확인은 아직 안 함).

## 5-1. 정량 재현 — 두 실물의 절대값을 폐형식에서 독립 재도출

이 노트의 고정 절대값이 "실행해 보니 그 숫자가 나왔다"가 아니라 **문헌 계수에서
독립적으로 계산된다**는 것을 확인한다(서술이 아니라 §6 verify 블록이 매번 실행한다).

**(A) τ(time_s=1 s) = 0.05211867631070653 재현**

Philipossian et al. 2004(doi:10.1149/1.1731539) 본문 실측 2점 — 턴오버비 TR=0 에서
50.0 nm, TR=1.13 에서 37.0 nm(26% 감소) — 에서 기울기를 역산하면

    a = (1 − 37.0/50.0) / 1.13 = 0.23008849557522126     (팩 선언값 0.2301과 0.04% 일치)

이 a 로 두 실측점을 되짚으면 TR=0 → 50.0000 nm, TR=1.13 → 37.0000 nm 로 **문헌값을
오차 0.0001 nm 이내 재현**한다. 여기에 Mu et al. 2016(doi:10.1016/j.mee.2016.02.035)
Table 3 의 MRT 실측(그루브 폭 300/600/900 µm → 9.2/10.6/13.9 s, 3 PSI)에서 이 팩의
폭 600 µm 에 해당하는 MRT=10.6 s 를 넣으면

    f(t=1 s)   = max(1 − 0.2301·(10.6/1),  0.05) = 0.05        (클램프 발동)
    f(t=60 s)  = max(1 − 0.2301·(10.6/60), 0.05) = 0.9593490…  (기준점)
    τ = 0.05 / 0.9593490… = 0.05211867631070653                 ← 고정 절대값과 일치

즉 τ(1 s) 은 자유 파라미터가 아니라 **두 문헌의 인쇄값 5개(50.0 nm·37.0 nm·1.13·
10.6 s·60 s)로 완전히 결정**된다. t=1 s 에서 클램프(하한 0.05)가 실제로 발동한다는
사실도 함께 기록한다 — 이 점의 값은 폐형식이 아니라 **하한이 정한 값**이므로 순위
정보로만 쓸 수 있다(미검증: 클램프 하한 0.05 자체의 1차 근거는 없다).

**(B) ψ(chelator_M=0) = 1.2230956708315368 재현**

`_chelator_suppression_term` 은 exp(−a·(C − C_ref)) 꼴이고, 이 팩의 선언값은
a = chelator_suppression_a, C_ref = 0.1332 mol/L(글리신 1 wt% 환산, 판정#41)이다.
C=0 을 넣으면 배수 = exp(+a·0.1332) 이고, 억제제 항이 기준 조건에서 항등적으로
1.0 이므로 최종 ψ 가 그대로 1.2230956708315368 이 된다 — **1 을 22.3% 초과**한다.
이 초과분은 오차가 아니라 정의역 밖 외삽의 크기다: 근거 노트
[[psi-glycine-chelator-suppression-cu-jani2025]] 가 스스로 "2점 적합이라 절대
크기는 순위 목적으로만" 이라고 경고한 항을, 적합 구간에 없던 C=0 으로 밀었을 때
나오는 값이기 때문이다. 판정#95 이전에는 이 22.3% 가 **어느 게이트에도 안 걸렸다**.

## 6. python verify

```python verify
import warnings
warnings.filterwarnings("ignore")
import numpy as np
from sim.engine import Recipe, simulate

# A. tau(time_s) 절대값 고정 (cu_h2o2_bta) — Philipossian 2004·Mu 2016 역산값 재현
rr1 = simulate(Recipe(pack="cu_h2o2_bta", time_s=1.0))
tau1 = rr1.factors["tau"].value
assert abs(tau1 - 0.05211867631070653) < 1e-9, tau1

rr0 = simulate(Recipe(pack="cu_h2o2_bta", time_s=0.0))
tau0 = rr0.factors["tau"].value
assert tau0 == 1.0, tau0
assert "time_s" not in rr0.factors["tau"].drivers, rr0.factors["tau"].drivers
assert any("turnover 항 미적용" in n for n in rr0.factors["tau"].notes)

# B. psi(chelator_M=0) 절대값 고정 (cu_h2o2_bta) — 판정#95 이후 최종값에 신고
rrB = simulate(Recipe(pack="cu_h2o2_bta", pack_overrides={"chelator_M": 0.0}))
psiB = rrB.factors["psi"].value
assert abs(psiB - 1.2230956708315368) < 1e-9, psiB
assert psiB > 1.0
assert any("정의(표면 보호 ≤1) 위반" in n for n in rrB.factors["psi"].notes)

# C. MRR 비트 불변 — 진단 계층만 고쳤다. 문헌값과 대조·재현한 기준 조건
# 평균 MRR이 7팩 전부 정확히 이 값과 일치해야 한다(수정 전후 diff로 확인).
expected = {
    "cu_h2o2_bta": 500.5453363064934,
    "oxide_silica": 143.01295323042672,
    "w_fe_oxidizer": 400.4362690451948,
    "sti_ceria": 314.6284971069387,
    "sic_ceria_h2o2": 2.0227752104911554,
    "sic_alumina_kmno4": 7.132342003507841,
    "cu_alkaline_benzenesulfonic": 27.330323101945417,
}
for pack, want in expected.items():
    got = float(np.mean(simulate(Recipe(pack=pack)).mrr_nm_per_min))
    assert got == want, (pack, got, want)

# D. 폐형식 독립 재도출 (§5-1) — 절대값이 문헌 인쇄값에서 계산된다
# Philipossian 2004 doi:10.1149/1.1731539 : TR=0 -> 50.0 nm, TR=1.13 -> 37.0 nm
a_lit = (1.0 - 37.0 / 50.0) / 1.13
assert abs(a_lit - 0.23008849557522126) < 1e-15, a_lit
# 두 실측점 재현 (오차 1e-9 nm 이내)
assert abs((1.0 - a_lit * 0.0) * 50.0 - 50.0) < 1e-9
assert abs((1.0 - a_lit * 1.13) * 50.0 - 37.0) < 1e-9

# 팩 선언 기울기는 같은 값을 4자리로 반올림한 것 (0.04% 이내)
from sim.params import load_pack
pk = load_pack("cu_h2o2_bta")
a_pack = float(pk.get_or("tr_preston_slope", 0.2301))
assert abs(a_pack - a_lit) / a_lit < 4e-4, (a_pack, a_lit)

# Mu 2016 Table 3 (3 PSI): 600 um -> MRT 10.6 s. t=1 s 는 클램프(0.05) 발동.
MRT, T_REF, CLAMP = 10.6, 60.0, 0.05
f_cur = max(1.0 - a_pack * (MRT / 1.0), CLAMP)
f_ref = max(1.0 - a_pack * (MRT / T_REF), CLAMP)
assert f_cur == CLAMP, f_cur          # 클램프가 실제로 발동함을 기록
assert abs(f_ref - 0.9593490) < 1e-6, f_ref
assert abs(f_cur / f_ref - 0.05211867631070653) < 1e-12, f_cur / f_ref

# B 의 초과분도 폐형식에서 — exp(+a_chel * C_ref)
import math
a_chel = float(pk.get("chelator_suppression_a"))
c_ref = float(pk.get("chelator_ref_M"))
assert abs(math.exp(a_chel * c_ref) - 1.2230956708315368) < 1e-12

print("OK")
```
