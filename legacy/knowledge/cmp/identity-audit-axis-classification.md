# 정체성 감사 축 분류 — 사각지대 4키 판정 (판정#63)

> 판정#60 §6 후속. `tools/audit_identity_inheritance.py` 는 상속 파라미터를 **재료축**
> (연마입자·막질·산화제·억제제·착화제)으로 분류하고, 그 축의 재료가 나와 **그 키를 실제로
> 선언한 조상**에서 다르면 신고한다. 축을 모르는 키는 **추측해 신고하지 않고**
> `--unclassified` 로 따로 낸다(오탐 1건이 도구 전체 신뢰를 깎기 때문).
> 이번 회차 착수 시점의 사각지대는 4키였다: `pad_ra_m`·`ph_peak`·`ph_mrr_at_peak_rel`·
> `ph_softening_per_unit`.
> [[identity-inheritance-audit-sweep]] [[alumina-abrasive-size-mrr-relation]]

## 1. 결론 요약

| 키 | 판정 | 축 | 근거 유형 |
|---|---|---|---|
| `ph_peak` | 분류 | **abrasive**(연마입자) | 판정#59 ③의 **실측 확인된 오염 경로** + 출처 문헌이 실리카 전용 |
| `ph_mrr_at_peak_rel` | 분류 | **abrasive** | `ph_peak` 와 **같은 문헌·같은 곡선**의 정점 높이 |
| `ph_softening_per_unit` | 분류 | **film**(막질) | 팩 note 자신이 "SiC 표면 화학에서 나왔다"고 근거를 댐 |
| `pad_ra_m` | `AXIS_NONE` | — | 소비처가 윤활 진단뿐, 5개 정체성 키 중 무엇도 계산에 안 들어감 |

사각지대 **4건 → 0건**. 신고 **13건 → 19건**(신규 6건은 전부 `ph_peak`·`ph_mrr_at_peak_rel`
축 배정으로 드러난 것). 이 도구는 **읽기 전용 감사**라 MRR·완성 격자·held-out ρ 는 불변이다.

## 2. `ph_peak` / `ph_mrr_at_peak_rel` — 연마입자축

**출처 문헌**: Li et al. 2021, *ECS J. Solid State Sci. Technol.* **10**, 123008,
doi:10.1149/2162-8777/ac3e44 (CC BY-NC-ND, 원문 PDF 확보).
`knowledge/params/oxide_silica.yaml` 이 두 키의 소유자이고, 두 값(`ph_peak`=11.0,
`ph_mrr_at_peak_rel`=1.113 = 1727/1551) 모두 그 논문의 **20 wt% 콜로이달 실리카** 조건에서
나왔다(근거 노트: `knowledge/cmp/abrasive-size-concentration-ph-K-additive-mrr-quantitative.md` §3).

**축이 연마입자인 이유는 추론이 아니라 실측이다.** `EVIDENCE-RULES.md` 판정#59 ③이 이미
기록해 둔 것:

> `abrasive: alumina` 만 선언하면 폴백이 `ph_peak`(oxide_silica 소유, 정점 pH=11 실리카 전용)로
> 떨어져 chi=1.7066/0.3636/0.1519/0.1243/0.1995(pH 2~6)라는 **실리카 곡선을 산성 알루미나계에
> 씌운 오염값**이 나온다(실측 확인).

즉 "이 키를 다른 연마입자 팩이 물려받으면 잘못된다"는 것이 **이미 한 번 실행으로 확인된**
사실이고, 그때 `sim/factors.py::_f_chi` 에 들어간 차단 규칙("고유 계수를 상속만 받았고 그 계수를
소유한 조상 팩의 `abrasive` 가 나와 다르면 그 분기를 쓰지 않는다")이 바로 **연마입자축 판정을
코드로 구현한 것**이다. 감사 도구가 같은 판정을 하지 않고 있던 것이 불일치였다.

`ph_mrr_at_peak_rel` 을 같은 축으로 두는 이유: 같은 논문·같은 pH 곡선의 **정점 높이**다.
정점 위치와 정점 높이가 서로 다른 축으로 갈라지면 그 자체가 결함이다.

> ⚠ **지금은 전부 비활성(dead)이다**: 신고된 3팩(`sic_alumina_kmno4`·`sic_ceria_h2o2`·
> `sti_ceria`)은 `_f_chi` 의 `has_own` 우선 규칙(판정#34)에 따라 **자기가 선언한 다른 pH 분기**를
> 먼저 고른다. 그래서 이 6건은 현재 MRR 에 영향이 없다. 그러나 그 own 키가 제거·리네임되면
> 즉시 판정#59 ③이 실측한 오염이 되살아난다 — **지금 조용한 것과 안전한 것은 다르다.**
> 회귀 테스트 `test_ph_peak_axis_is_abrasive_2026_09_18` 이 이 신고가 사라지지 않게 고정한다.

### 2.1 정량 대조 — 두 값이 실제로 그 문헌의 실리카 곡선에서 나왔는가

축 배정은 "이 숫자가 어느 재료의 실측인가"를 묻는 것이므로, 팩에 저장된 값이 원문 실리카
데이터에서 나온 것임을 숫자로 대조한다(근거 노트
`knowledge/cmp/abrasive-size-concentration-ph-K-additive-mrr-quantitative.md` §3, Li 2021 Fig.1:
20 wt% 콜로이달 실리카, K⁺ 0.25 mol/L).

| pH | 문헌 MRR (Å/min) |
|---|---|
| 10.0 | 1551 |
| 11.0 | **1727**(최댓값) |
| 12.5 | 1407 |

- `ph_peak` = **11.0 pH** ← 위 표의 최댓값 위치와 일치.
- `ph_mrr_at_peak_rel` = **1.113** ← 1727 / 1551 = 1.1135 (pH 10 대비 +11.3 %),
  팩 저장값과의 오차 **0.0005 미만**.

**정량 대조**(문헌값 vs 팩 저장값, 단위 포함):

- 정점 위치 — 문헌값 pH 11.0 에서 1727 Å/min(최댓값, Li 2021 doi:10.1149/2162-8777/ac3e44
  Fig.1) vs 팩 `ph_peak` = 11.0, **일치**.
- 정점 높이비 — 문헌값 1727 Å/min ÷ 1551 Å/min = 1.1135(**+11.35 %**, Li 2021
  doi:10.1149/2162-8777/ac3e44 Fig.1) vs 팩 `ph_mrr_at_peak_rel` = 1.113, 오차
  **0.045 %** 로 재현.
- 하강 가지 — 문헌값 1727 → 1407 Å/min(pH 11.0 → 12.5, Li 2021
  doi:10.1149/2162-8777/ac3e44 Fig.1)은 **-18.5 %**. 이 하강폭은 팩에 저장되지 않는다
  (χ 곡률 파라미터가 따로 형상을 만든다) — 대조 대상이 아님을 명시한다.
- 오염 크기 — 판정#59 ③(EVIDENCE-RULES.md 판정 기록표, 실행 확인)이 이 곡선을 산성
  알루미나계 pH 2~6 에 씌웠을 때 나온 χ 산포는 최대 1.7066 / 최소 0.1243 = **13.73 배**.
  축을 안 가르면 이만큼 틀린다.

두 값 모두 **실리카 연마입자 조건에서만** 측정됐다. 세리아·알루미나 계의 pH 곡선은 정점
위치 자체가 다르다는 것이 판정#59 ③에서 실측으로 확인됐다(그 팩 운전점 pH 2~6 구간에서
실리카 곡선을 씌우면 χ = 1.7066 / 0.3636 / 0.1519 / 0.1243 / 0.1995 라는 오염값이 나온다 —
**최대·최소 배수 13.7배**).

## 3. `ph_softening_per_unit` — 막질축

소유자 `knowledge/params/sic_ceria_h2o2.yaml` 의 헤더 주석이 스스로 축을 밝힌다(19-21행):

> ⚠ 이 값은 **SiC 표면 화학에서 나왔다**. Si 산화막의 pH 의존성은 다르다
> (실리카 등전점 pH~2, 세리아 ~7 → 정전기 상호작용이 반대로 움직인다). 다른 재료계로 옮기지 마라.

무엇을 깎느냐(SiC 표면의 가수분해·연화)가 계수를 정하지, 어느 연마입자·산화제로 깎느냐가
정하지 않는다 — 막질축이다.

**이 배정이 신고를 만들지 않는 것이 정확한 결과다.** 이 키를 상속하는 유일한 팩
`sic_alumina_kmno4` 의 `film` 은 소유 조상 `sic_ceria_h2o2` 와 똑같이 `sic_4h` 다. 즉
"재료가 달라도 정당한 상속"이 아니라 **애초에 이 축의 재료가 같다**(다른 것은 연마입자와
산화제다). 사각지대로 남겨 우연히 조용한 것과, 축을 배정하고 일치를 확인해 조용한 것은
전혀 다른 상태다.

> ⚠ 주의: 그 note 가 경고한 "다른 재료계로 옮기지 마라"는 **산화막 계(oxide)** 로의 전이를
> 가리킨 말이고, 이 감사가 묻는 축 일치와는 다른 층위다. 또한 산성 pH 2.3 운전점에
> 알칼리 pH 9~11 에서 역산한 계수를 외삽하는 위험(판정#57 이 지적한 정의역 외삽)은
> **이 감사의 범위 밖**이다 — 감사는 "재료가 같은가"만 묻지 "조건이 같은가"는 묻지 않는다.

## 4. `pad_ra_m` — `AXIS_NONE`(사각지대가 아니라 적극적 판정)

소비처를 `grep` 으로 전수 확인한 결과 `sim/equipment_outputs.py` 와 `sim/engine.py` 의
**윤활 진단**(Sommerfeld 수 / Stribeck 레짐)뿐이고, 거기서 `slurry_viscosity_pa_s` 와 함께
쓰인다. 5개 정체성 키(연마입자·막질·산화제·억제제·착화제) 중 **무엇도 이 계산에 들어가지
않는다** — 패드 표면거칠기는 패드 제조사·컨디셔닝의 함수이지 재료 정체성이 아니다.

판정#60 이 "축 없이 대조하면 `pad_ra_m` 이 '연마입자가 다르다'고 섞인다(오탐 64건)"를
도구 설계의 근거로 든 바로 그 키다. 그 서술을 코드로 확정했다.

## 5. 기존 `AXIS_NONE` 4건 재검토 — "근거 있음"과 "근거 못 찾음"을 갈랐다

기존 주석은 전부 단정형이라 **문헌 근거가 있는 것처럼 읽혔다**. 실제로는 성격이 다르다:

| 키 | 갱신 후 | 이유 |
|---|---|---|
| `slurry_viscosity_pa_s` | **근거 있는 AXIS_NONE** | 슬러리 **전체** 물성(다성분이 함께 정한다) — 단일 재료축 귀속이 범주 오류. `pad_ra_m` 과 같은 소비처·같은 이유 |
| `hamaker_j` | **미검증 — 귀속 근거 미확보** | 3자(입자-매질-기판) 상수라 원칙적으로도 단일축이 어렵고, 현재 `sim` 어디서도 팩 값을 읽지 않는 **고아 키**라 축을 배정해도 검증할 실행 경로가 없다 |
| `damage_exponent` | **미검증 — 귀속 근거 상충** | 팩 note 들이 **서로 다른 축**을 정당화 근거로 쓴다: `oxide_silica`·`w_fe_oxidizer` 는 막질 일치를 근거로 전이했는데 `cu_h2o2_bta` 는 막질이 다른데도(W→Cu) "연마입자·촉매 계열 유사성"을 근거로 같은 값을 전이했다. `base.yaml` 자신도 "재료 고유인지 공정 고유인지 미확정"이라 적는다 — **강제 배정하면 이 상충 중 하나는 반드시 틀린다** |
| `dispersant_type` | **미검증 — 귀속 근거 미확보** | '분산제는 입자 표면에 흡착한다'는 메커니즘상 연마입자축이 그럴듯하나, **흡착 선호도가 연마입자 화학종에 따라 갈린다는 것을 직접 보인 문헌을 확보하지 못했다**. PAA/PVA 류는 입자 특이성이 없을 수도 있다 — 그럴듯한 가설과 확인된 근거를 구분한다 |

## 5.1 왜 "연마입자가 바뀌면 곡선이 바뀐다"가 축 배정의 근거인가

이 감사가 묻는 것은 "값이 맞는가"가 아니라 **"이 숫자가 어느 재료의 실측인가"**다. 같은
저장소 안에 연마입자를 바꾸면 곡선 형상 자체가 달라진다는 실측이 세 건 쌓여 있다:

| 축 | 실리카 | 세리아 | 알루미나 |
|---|---|---|---|
| pH 정점(χ) | **11.0 pH**(Li 2021 doi:10.1149/2162-8777/ac3e44 Fig.1, 1727 Å/min) | — | 산성계, 실리카 곡선 대입 시 χ 산포 13.73 배 오염(EVIDENCE-RULES 판정#59 ③) |
| 입경 정점(κ) | 80 nm(조부모 상속값, 출처는 그 팩 note) | **163 nm**(Oh 2010 doi:10.1016/j.mee.2010.07.040) | **2500 nm**(Su 2011 doi:10.1016/j.proeng.2011.11.2673, 판정#62) |

입경축에서는 세리아 정점 163 nm(Oh 2010 doi:10.1016/j.mee.2010.07.040)와 알루미나 정점
2500 nm(Su 2011 doi:10.1016/j.proeng.2011.11.2673)가 **15.3 배** 차이 나고, 팩 기준값
500 nm 가 둘 사이에 놓여 **어느 곡선을 쓰느냐에 따라 증가 가지와 감소 가지가 뒤바뀐다** —
판정#62 가 바로 이 이유로 5키를 한 편집에서 함께 교체했다. pH 축도 같은 구조이므로
`ph_peak`·`ph_mrr_at_peak_rel` 을 연마입자축으로 두는 것이 일관된 처리다.

## 6. 재현 (verify)

```python verify
import sys
from pathlib import Path

sys.path.insert(0, str(Path.cwd()))

from sim.params import load_pack
from tools.audit_identity_inheritance import AXIS_NONE, _axis_of, audit

# (1) 이번 회차에 분류한 3키의 축
assert _axis_of("ph_peak") == "abrasive"
assert _axis_of("ph_mrr_at_peak_rel") == "abrasive"
assert _axis_of("ph_softening_per_unit") == "film"

# (2) pad_ra_m 은 축 없음 -- 그리고 그것이 '분류를 안 한 것'이 아니라
#     AXIS_NONE 에 근거와 함께 등재된 적극적 판정임을 확인한다.
assert _axis_of("pad_ra_m") is None
assert "pad_ra_m" in AXIS_NONE
assert "윤활" in AXIS_NONE["pad_ra_m"]

# (3) 기존 AXIS_NONE 3건은 '미검증'이 명시돼야 한다(근거 있는 것처럼 쓰지 않는다)
for k in ("hamaker_j", "damage_exponent", "dispersant_type"):
    assert "미검증" in AXIS_NONE[k], k
# slurry_viscosity_pa_s 는 근거가 있는 AXIS_NONE 이라 그 부정형이 명시된다
#   — 단순 부분문자열 검사는 부정문에도 걸리므로 부정형 문구 자체를 확인한다.
assert "미검증이 아니다" in AXIS_NONE["slurry_viscosity_pa_s"]

res = audit()

# (4) 사각지대가 비었다 -- 이번 회차의 목표
unclassified = {u["key"] for u in res["unclassified"]}
for k in ("pad_ra_m", "ph_peak", "ph_mrr_at_peak_rel", "ph_softening_per_unit"):
    assert k not in unclassified, k

got = {(m["pack"], m["key"]) for m in res["mismatches"]}

# (5) ph_peak 축 배정이 드러낸 신규 신고 6건 (3팩 x 2키)
expected_new = {
    (p, k)
    for p in ("sic_alumina_kmno4", "sic_ceria_h2o2", "sti_ceria")
    for k in ("ph_peak", "ph_mrr_at_peak_rel")
}
assert expected_new <= got, sorted(expected_new - got)

# (6) ph_softening_per_unit 은 신고되지 않는다 -- 축(film)이 실제로 일치하기 때문이다.
#     '분류를 안 해서 조용한 것'과 구분하려면 일치 자체를 확인해야 한다.
assert ("sic_alumina_kmno4", "ph_softening_per_unit") not in got
mine = load_pack("sic_alumina_kmno4").get_or("film", None)
theirs = load_pack("sic_ceria_h2o2").get_or("film", None)
assert mine == theirs == "sic_4h", (mine, theirs)

# (7) 오탐 없음 -- 패드/장비 키는 어떤 팩에서도 신고되지 않는다
for pack, key in got:
    assert key not in {"pad_ra_m", "slurry_viscosity_pa_s"}, (pack, key)

# (8) 정량 대조 -- 팩에 저장된 두 값이 Li 2021 Fig.1 실리카 곡선에서 나온 숫자인가.
#     축 배정의 근거가 "그 숫자가 어느 재료 실측인가"이므로 이것이 곧 근거 검증이다.
ox = load_pack("oxide_silica")
ph_lit = [10.0, 11.0, 12.5]
mrr_lit = [1551.0, 1727.0, 1407.0]          # Angstrom/min, Li 2021 Fig.1

peak_ph_lit = ph_lit[mrr_lit.index(max(mrr_lit))]
assert peak_ph_lit == 11.0
assert float(ox.get("ph_peak")) == peak_ph_lit, (
    "ph_peak(%s) != 문헌 정점 pH(%s)" % (ox.get("ph_peak"), peak_ph_lit))

rel_lit = mrr_lit[1] / mrr_lit[0]           # 1727 / 1551
assert abs(rel_lit - 1.1135) < 1e-3, rel_lit
assert abs(float(ox.get("ph_mrr_at_peak_rel")) - rel_lit) < 5e-4, (
    "ph_mrr_at_peak_rel(%s) != 1727/1551(%.4f)" % (ox.get("ph_mrr_at_peak_rel"), rel_lit))

# (9) 판정#59 ③ 이 실측한 오염 배수 -- 실리카 곡선을 산성 알루미나계에 씌웠을 때의
#     chi 산포. 축을 안 갈랐을 때 얼마나 틀리는지의 크기다.
chi_contaminated = [1.7066, 0.3636, 0.1519, 0.1243, 0.1995]   # pH 2~6
spread = max(chi_contaminated) / min(chi_contaminated)
assert abs(spread - 13.73) < 0.05, spread

print("PASS: 사각지대 4건 -> 0건, 신규 신고 %d건 확인, 오탐 0" % len(expected_new))
print("총 신고 %d건 / 미분류 %d건" % (len(got), len(unclassified)))
print("정량: ph_peak=%s pH (문헌 정점 %s), rel=%s (1727/1551=%.4f A/min 비)"
      % (ox.get("ph_peak"), peak_ph_lit, ox.get("ph_mrr_at_peak_rel"), rel_lit))
```

## 7. 출처
- Li, Zhang et al. 2021, *ECS J. Solid State Sci. Technol.* 10, 123008,
  DOI 10.1149/2162-8777/ac3e44 (CC BY-NC-ND, 원문 PDF 확보) — `ph_peak`·`ph_mrr_at_peak_rel`
  두 값의 1차 출처. 20 wt% 콜로이달 **실리카** 조건.
- `EVIDENCE-RULES.md` 판정#59 ③ — `ph_peak` 폴백이 산성 알루미나계에 실리카 곡선을 씌우는
  오염값을 낸다는 **실행 확인** 기록(저장소 내부 판정, 1차 출처 아님).
- `knowledge/params/sic_ceria_h2o2.yaml` 19-21행 — `ph_softening_per_unit` 이 SiC 표면
  화학에서 나왔다는 소유자 자신의 선언.
- Su Jianxiu et al. 2011, *Procedia Engineering* 24, 441-446,
  doi:10.1016/j.proeng.2011.11.2673 — 같은 팩(`sic_alumina_kmno4`)의 입경축을 판정#62 에서
  알루미나 자기 실측으로 되돌린 근거. 이번 판정의 `ph_peak` 와 **같은 종류의 결함**
  (연마입자가 다른데 남의 곡선을 물려받음)이 이미 한 축에서 실제로 교정된 선례다.
- Oh et al. 2010, *Microelectronic Engineering*, doi:10.1016/j.mee.2010.07.040 — 세리아 계
  입경-MRR 곡선. 연마입자 종류가 바뀌면 곡선 형상 자체가 달라진다는 것(실리카·세리아·
  알루미나가 서로 다른 정점을 가진다)의 근거 계보.
