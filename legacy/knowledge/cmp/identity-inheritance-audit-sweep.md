<!-- V2-SECTION: R2-slurry | 정체성 상속 전수감사 2026-09-18 -->
# 정체성 상속 전수감사 — 같은 결함이 네 번 반복된 뒤 기계에 넘긴 것

> 판정#60 (2026-09-18, Max워커). 판정#59 의 직접 후속.
> 산출물: `tools/audit_identity_inheritance.py`(신고 도구),
> `tests/test_identity_inheritance_audit.py`(계약 6건).
> **결론: 신고 18건 중 2건이 MRR 을 실제로 움직이는 살아 있는 결함**이고,
> 그 2건은 **판정#59 와 같은 팩의 같은 유형**이다(입경축).

## 1. 왜 도구를 만들었나

같은 유형의 결함이 네 번 나왔다. 전부 사람이 **우연히** 발견했다.

| 판정 | 내용 |
|---|---|
| #34 | sic 팩이 `sti_ceria` 의 IEP 정전창(산성용)을 상속해 자기 pH 계수를 가림 |
| #48 | sic 팩이 실리카 부모의 연마입자 농도를 상속 |
| #52 | 근거 문헌과 파라미터가 서로 다른 팩에 흩어짐 |
| #59 | `sic_alumina_kmno4` 가 `abrasive` 키 자체를 `'ceria'` 로 상속 — 알루미나 슬러리에 세리아 화학항이 켜져 있었다 |

네 번이면 개별 대응이 아니라 상시 감사의 문제다.

## 2. 설계 — 축(axis)이 핵심이고, 보수성이 의도다

상속받은 파라미터 K 에 대해 (1) K 가 어느 **재료축**에 속하는지 이름으로 분류하고
(2) 그 축의 재료가 **나**와 **K 를 실제로 선언한 조상**에서 다르면 신고한다.

축 없이 그냥 대조하면 무슨 일이 일어나는지 먼저 측정했다: **64건**이 나오고
그 안에 `pad_ra_m`(패드 표면거칠기)이 "연마입자가 다르다"는 이유로 섞인다.
패드 물성은 연마입자와 무관하다 — 그런 신고가 섞이면 도구를 아무도 안 본다.
축 분류를 넣으면 **18건**으로 줄고 전부 실제 재료축에 걸린 것만 남는다.

**축을 분류하지 못하는 키는 신고하지 않는다.** 이건 누락이 아니라 설계다 —
추측해서 신고하면 오탐이 나고, 오탐이 나면 도구가 죽는다. 대신 사각지대를
숨기지 않고 `--unclassified` 로 따로 낸다(테스트로 고정: 사각지대가 신고
목록에 섞이면 실패).

`AXIS_NONE`(재료가 달라도 상속이 정당하다고 **선언한** 키)에는 근거를 적었다:
`hamaker_j`(입자-매질-기판 3자 상수라 한 축에 귀속 불가)·`damage_exponent`
(재료 고유인지 공정 고유인지 미확정)·`dispersant_type`·`slurry_viscosity_pa_s`.
이 네 건은 **미검증**이다 — "괜찮다"가 아니라 "축을 정할 근거가 없다"는 뜻이다.

## 3. 결과 — 18건, 그중 살아 있는 것 2건

`PYTHONPATH=. .venv/bin/python tools/audit_identity_inheritance.py` 실측:

- `sic_alumina_kmno4` 16건 (연마입자 14 · 산화제 2)
- `sic_ceria_h2o2` 1건 · `sti_ceria` 1건 (둘 다 `abrasive_saturation_wt_pct` ← `oxide_silica`)

각 항목의 값을 1.5배 흔들어 MRR 변화를 측정해 **살아 있는 것과 죽은 것을 갈랐다**:

| 상태 | 건수 | 내용 |
|---|---|---|
| ★ MRR 영향 | **2** | `abrasive_size_nm`(Δ=0.455) · `abrasive_ref_size_nm`(Δ=0.313) |
| 무영향 | 15 | 세리아 계수(ce3_*·ceria_tooth_*)는 판정#59 가 이미 분기를 껐고, 산화제 계수는 판정#50 종 게이트가 껐고, 나머지는 소비처가 없다 |
| 비수치 | 1 | `oxidizer_langmuir_species`(문자열 — 게이트가 소비) |

즉 **판정#59 와 판정#50 이 이미 막아둔 것이 대부분이고, 뚫려 있는 축은 입경 하나**다.

## 4. 살아 있던 결함 — 입경축 (판정#60 발견 → **판정#62 해소**)

> ⚠ **2026-09-19 부채상환 갱신(학습총괄).** 이 절은 판정#60 시점(2026-09-18)의
> 기록이었고, 그 뒤 **판정#62(커밋 8e0532e)가 입경 5키를 알루미나 실측으로
> 자기선언해 결함을 해소**했다. 아래 표는 **당시 상태의 역사 기록**이고,
> 현재 상태는 §4.1 이다. 노트를 고치지 않고 두면 다음 회차가 이미 고친 결함을
> 살아 있다고 읽는다 — 그것이 이 갱신의 이유다.

판정#60 당시 상태(현재는 성립하지 않음):

```
sic_alumina_kmno4:   # ← 2026-09-18 시점, 전부 owner=sic_ceria_h2o2 (세리아 상속)
  abrasive_size_nm      = 120.0 nm
  abrasive_ref_size_nm  = 120.0 nm
  abrasive_size_peak_nm = 163.0 nm
  abrasive_size_exp_below_peak = 1.3333
  abrasive_size_exp_above_peak = -0.3333
```

이 다섯 값은 전부 **세리아 슬러리**(sic_ceria_h2o2)에서 온 것이었고, 이 팩의
연마입자는 알루미나다. 그리고 이 팩의 근거 문헌은 **다른 입경**을 적는다:

- Gong 2024 (doi:10.3390/ma17030679) Table 1 — 알루미나 **500 nm**
- 데이터셋 YAML 의 `scope_note` 가 이미 이 사실을 적어뒀다: "입경도 원문 500 nm
  인데 팩은 이를 자기선언하지 않는다(절대값에만 영향, 이 DOE 는 입경을 고정하므로
  순위에는 무영향)"

즉 **이미 알려져 있었으나 상속 경로가 보이지 않아 방치돼 있던 것**이다. 판정#60 의
감사가 그 경로를 명시했고, 판정#62 가 그것을 닫았다.

### 4.1 현재 상태 (2026-09-19 실측)

입경 5키가 전부 `owner=sic_alumina_kmno4`(자기선언)이고 `confidence=literature` 다:

| 키 | 현재 값 | owner | 판정#60 당시 |
|---|---|---|---|
| `abrasive_size_nm` | 500.0 nm | sic_alumina_kmno4 | 120.0 (세리아 상속) |
| `abrasive_ref_size_nm` | 500.0 nm | sic_alumina_kmno4 | 120.0 (세리아 상속) |
| `abrasive_size_peak_nm` | 2500.0 nm | sic_alumina_kmno4 | 163.0 (세리아 상속) |
| `abrasive_size_exp_below_peak` | 0.309289 | sic_alumina_kmno4 | 1.3333 (세리아 상속) |
| `abrasive_size_exp_above_peak` | -0.066470 | sic_alumina_kmno4 | -0.3333 (세리아 상속) |

본값과 기준점(`_ref`)이 **같은 편집에서 함께 500 nm 로** 옮겨졌으므로 기준 조건에서
입경 항은 여전히 정확히 1.0 이다(Kp 이중 계상 없음). 아래 verify 블록이 그것을
매번 확인한다.

**정량 재현 — 문헌값 대조**: 팩이 현재 쓰는 `abrasive_size_nm` = **500.0 nm** vs
Gong 2024 (doi:10.3390/ma17030679) Table 1 인쇄값 **500 nm** — **일치**(차이 0.0 nm,
0.00%). 판정#60 당시 값 120.0 nm 와 문헌값 500 nm 의 차이는 380.0 nm(4.17배,
+316.7%)였으므로, 판정#62 는 그 380.0 nm 의 괴리를 0.0 nm 로 닫은 것이다.
`abrasive_ref_size_nm` 도 같은 500.0 nm 이므로 기준 조건 입경 항 = (500.0/500.0)^n
= 1.000000 (n 무관, 오차 < 1e-12). 아래 verify 블록의 assert 가 이 세 수치
(500.0 nm · 동반 이동 · 배수 1.554869)를 매 실행마다 재계산해 고정한다.

입경축 응답(현재 곡선, 알루미나 형상):

| abrasive_size_nm | κ 전체 | MRR (nm/min) |
|---|---|---|
| 120 | 0.310725 | 1.424453 |
| 163 | 0.341597 | 1.565978 |
| 500 (팩 기본 = Gong 실측) | 0.483137 | 2.214838 |

MRR 비(120 nm → 500 nm) = **1.554869배**. 판정#60 당시 세리아 곡선에서 잰
1.0353배와 다른 이유는 §5 가 경고한 바로 그것이다 — **곡선 자체가 바뀌었기
때문**이지 값 하나가 바뀌었기 때문이 아니다. 정점이 163 → 2500 nm 로 옮겨가
500 nm 가 below-peak 가지로 들어왔다.

## 5. 왜 판정#60 에서는 고치지 않았나 (그리고 그 판단이 옳았다)

판정#60 은 값을 500 nm 로 바꾸는 한 줄 수정을 **의도적으로 거부**했다:

`abrasive_size_peak_nm`(163)·`_exp_below_peak`(1.333)·`_exp_above_peak`(-0.333)이
전부 **세리아 계에서 나온 형상**이었다. 입경 값만 알루미나 것으로 바꾸면 **알루미나
입경을 세리아 입경-MRR 곡선에 대입**하게 된다 — 판정#59 §2 에서 실측으로 확인한
"실리카 곡선을 알루미나에 씌우는" 것과 **정확히 같은 함정**이다.

**그 판단이 사후에 정량으로 정당화됐다**: 판정#62 가 형상 3키까지 알루미나 실측으로
함께 옮기자 같은 입경 비의 MRR 영향이 1.0353배 → 1.554869배로 **15배 커졌다**.
즉 판정#60 이 값 하나만 고쳤다면 "3.5% 영향"이라는 잘못된 크기 판단이 노트에 남고,
그 위에서 우선순위가 정해졌을 것이다. **값과 형상은 같은 편집에서 함께 옮겨야 한다.**

판정#60 의 산출은 값 변경이 아니라 신고의 상시화였고(코드·YAML 0줄, MRR 비트 불변),
그 신고가 이틀 뒤 판정#62 의 입력이 됐다.

## 5.1 지금 살아 있는 상속 신고 (2026-09-19 재실행)

감사 신고는 18건 → **19건**이고, `sic_alumina_kmno4` 의 연마입자축 신고는 아래 13건이다.
입경 5키는 목록에서 **빠졌다**(자기선언됐으므로).

```
abrasive_d99_nm · abrasive_iep_ph · abrasive_ref_d99_nm ·
abrasive_saturation_wt_pct · ce3_fraction · ce3_fraction_ref ·
ceria_tooth_exponent · ceria_tooth_gain · oxide_nitride_selectivity ·
oxidizer_langmuir_K · oxidizer_langmuir_species · ph_mrr_at_peak_rel · ph_peak
```

이 중 세리아 계수(`ce3_*`·`ceria_tooth_*`)와 pH 정점(`ph_peak`·`ph_mrr_at_peak_rel`)은
판정#59·#61 이 **분기를 꺼서** MRR 에 도달하지 않고, 산화제 계수
(`oxidizer_langmuir_*`)는 판정#50 의 종(species) 게이트가 막는다 — 즉 죽은 신고다.
**미검증**: `abrasive_d99_nm`·`abrasive_iep_ph`·`abrasive_saturation_wt_pct` 3건이
현재 MRR 을 움직이는지는 이번 회차에 재측정하지 않았다(판정#60 당시에는 무영향이었으나
그 뒤 Δ 축 항이 신설됐으므로 그 결론이 여전히 유효한지 확인이 필요하다).

## 6. 미검증·확인 못 한 것

- **`AXIS_PREFIX` 분류표가 완전한지 검증하지 못했다.** 132개 키 중 축을 배정한 것은
  접두사 9종 + 개별 지정 11종이고, 나머지는 `--unclassified` 로 빠진다. 빠진 키에
  같은 유형의 결함이 있을 수 있다(사각지대).
- **`AXIS_NONE` 4건의 "축 없음" 판단은 근거가 없다** — 문헌으로 확인한 것이 아니라
  "한 축에 귀속시킬 근거를 못 찾았다"는 뜻이다(미검증).
- **`abrasive_saturation_wt_pct` ← `oxide_silica` 2건**(sic_ceria_h2o2·sti_ceria)은
  MRR 무영향이라 이번에 파고들지 않았다. 소비처가 생기면 판정 대상이다.
- **입경축 결함의 정확한 크기는 미확정**: 1.0353배는 **세리아 곡선을 그대로 쓴다는
  가정 하의** 값이다. 알루미나 곡선이 다르면 이 수치 자체가 무의미하다.

## 출처
- Gong J., Wang W., Liu W., Song Z., Materials 17(3) 679 (2024),
  doi:10.3390/ma17030679, Table 1 — 알루미나 500 nm.
- US20220315802A1 (Entegris / University of Florida), Table 1.
- 선행 판정: EVIDENCE-RULES.md 판정#34·#48·#50·#52·#59.
- 선행 노트: [[sic-alumina-pack-abrasive-identity-inheritance-defect]]
  (knowledge/cmp/sic-alumina-pack-abrasive-identity-inheritance-defect.md)

```python verify
# 판정#60 — 감사 도구가 실제로 돌고, 축 분류가 오탐을 막고,
# 입경축 수치가 노트에 적힌 그대로인지 매번 재확인한다.
import numpy as np
import sim.engine as E
from sim import factors
from sim.params import load_pack
from tools.audit_identity_inheritance import audit, _axis_of, AXIS_NONE

res = audit()
ms = {(m["pack"], m["key"]): m for m in res["mismatches"]}

# 1) 판정#59 유형(세리아 계수를 알루미나 팩이 상속)이 실제로 신고된다
for k in ("ce3_fraction", "ceria_tooth_gain", "ceria_tooth_exponent"):
    m = ms[("sic_alumina_kmno4", k)]
    assert m["axis"] == "abrasive" and m["mine"] == "alumina" and m["theirs"] == "ceria", m

# 2) 판정#62 해소 확인 — 입경 2키는 **더 이상 신고되지 않는다**
#    (신고가 되살아나면 판정#62 가 되돌아간 것이므로 실패해야 한다)
for k in ("abrasive_size_nm", "abrasive_ref_size_nm"):
    assert ("sic_alumina_kmno4", k) not in ms, ("판정#62 회귀", k)

# 3) 오탐 없음 — 패드/장비 키는 신고되지 않는다
for (_p, k) in ms:
    assert k.split("_")[0] not in {"pad", "cond", "platen", "rpm", "sfr",
                                   "groove", "retaining", "cof"}, k

# 4) 축을 모르는 키는 추측하지 않는다
assert _axis_of("pad_ra_m") is None
assert _axis_of("kp_m_per_pa") is None
for k in AXIS_NONE:
    assert _axis_of(k) is None, k

# 5) §4.1 표 재현 — 입경 5키가 자기선언(판정#62)이고 값·곡선이 노트대로다
pk = load_pack("sic_alumina_kmno4")
for k in ("abrasive_size_nm", "abrasive_ref_size_nm", "abrasive_size_peak_nm",
          "abrasive_size_exp_below_peak", "abrasive_size_exp_above_peak"):
    assert pk.has_own(k), ("판정#62 회귀 — 상속 상태로 돌아갔다", k)
    assert pk.param(k).owner == "sic_alumina_kmno4", (k, pk.param(k).owner)
assert abs(float(pk.get("abrasive_size_nm")) - 500.0) < 1e-9
# 본값과 기준점이 함께 옮겨졌다 = 기준 조건에서 입경 항이 정확히 1.0
assert (float(pk.get("abrasive_size_nm"))
        == float(pk.get("abrasive_ref_size_nm"))), "_ref 동반 이동 깨짐"
assert abs(float(pk.get("abrasive_size_peak_nm")) - 2500.0) < 1e-9

def kappa(size):
    rr = E.Recipe(pack="sic_alumina_kmno4",
                  pack_overrides={"slurry_ph": 5, "oxidizer_wt_pct": 2,
                                  "abrasive_wt_pct": 3,
                                  "abrasive_size_nm": size}).resolve()
    return factors._f_kappa(rr).value

for size, want in ((120, 0.310725), (163, 0.341597), (500, 0.483137)):
    got = kappa(size)
    assert abs(got - want) < 1e-5, (size, got, want)

def mrr(size):
    return float(np.mean(E.simulate(E.Recipe(
        pack="sic_alumina_kmno4",
        pack_overrides={"slurry_ph": 5, "oxidizer_wt_pct": 2,
                        "abrasive_wt_pct": 3,
                        "abrasive_size_nm": size})).mrr_nm_per_min))

ratio = mrr(500) / mrr(120)
assert abs(ratio - 1.554869) < 1e-4, ratio
# 판정#60 당시 세리아 곡선에서는 1.0353배였다 — 곡선 교체의 영향이 15배다
assert ratio / 1.0353 > 1.4, ratio

# 6) 감사는 읽기 전용 — MRR 을 건드리지 않는다
before = mrr(120)
audit()
assert mrr(120) == before

print("판정#60 verify: 6/6 PASS (신고 %d건, 사각지대 %d건)"
      % (len(res["mismatches"]), len(res["unclassified"])))
```
