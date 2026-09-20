# ψ 표면 보호도 빠진 드라이버 — SiC 계 3팩 조사 (cu_alkaline_benzenesulfonic → sic_ceria_h2o2 → sic_alumina_kmno4)

> 갭 랭커(score 50, PARTIAL) 위임 작업. 대상 3팩을 순서대로 실사했고, 실제로 쓸 수 있는
> 1차 문헌 인쇄 수치표는 **sic_alumina_kmno4**에서 나왔다 — 아래 §4가 본체다.
> §2·§3은 앞의 두 팩을 왜 버렸는지(재발견 금지 원칙에 따른 기록)를 남긴다.

## 0. 갭 랭커 출력이 실제 코드와 어긋나는 이유 (dedup 아티팩트)

`tools/accuracy_gaps.py`가 준 원문 설명은 "3 packs: cu_alkaline_benzenesulfonic,
sic_alumina_kmno4, sic_ceria_h2o2 — terms=['dispersant']"였다. `_dedupe_factors()`
(`tools/accuracy_gaps.py:245-258`)가 `(kind, factor)` 키로만 묶고 `what` 문구는
**먼저 처리된 팩 하나의 것**을 그대로 재사용한다 — 세 팩이 실제로 같은 `terms`를
가진다는 보장이 없다. 직접 `simulate()`를 돌려 팩별 실제 상태를 확인했다:

```python verify
# ground truth: 세 팩의 psi 팩터가 실제로 무엇을 계산하는지 직접 확인
# (sim/factors.py::_f_psi, 2026-09-19 판정#70의 owned_by_chi 분기 포함)
import subprocess, sys, json
code = '''
import sys
sys.path.insert(0, ".")
from sim.engine import Recipe, simulate
out = {}
for p in ["cu_alkaline_benzenesulfonic", "sic_alumina_kmno4", "sic_ceria_h2o2"]:
    r = simulate(Recipe(pack=p))
    f = r.factors["psi"]
    out[p] = {"status": f.status, "terms": sorted(f.terms.keys()),
              "drivers": sorted(f.drivers.keys())}
print(out)
'''
result = subprocess.run([".venv/bin/python", "-c", code], cwd=".",
                         capture_output=True, text=True, timeout=120)
assert result.returncode == 0, result.stderr[-2000:]
data = eval(result.stdout.strip())
# cu_alkaline_benzenesulfonic: 판정#70의 항등원 분기 — dispersant 항이 아니다
assert data["cu_alkaline_benzenesulfonic"]["terms"] == ["owned_by_chi"], data
assert data["cu_alkaline_benzenesulfonic"]["drivers"] == [], data
# sic_alumina_kmno4 · sic_ceria_h2o2: 둘 다 실제로 dispersant(NONE 상수 lookup)뿐
assert data["sic_alumina_kmno4"]["terms"] == ["dispersant"], data
assert data["sic_ceria_h2o2"]["terms"] == ["dispersant"], data
assert set(data["sic_alumina_kmno4"]["drivers"]) == {"shield_additive_wt_pct", "dispersant_type"}, data
print("확인: 갭 랭커의 'terms=[dispersant]' 문구는 cu_alkaline_benzenesulfonic에는 해당하지 않는다 — dedup이 보여준 대표값일 뿐.")
```

**결론**: `cu_alkaline_benzenesulfonic`은 이미 판정#70([[psi-cu-alkaline-h2o2-passivation]])이
심층 조사를 마쳤고 `sim/factors.py:1729`에 그 결론(χ가 같은 θ(C)를 전담하므로 ψ=1.0
항등원)이 코드로 구현돼 있다 — **이 팩은 재작업 대상이 아니다.** 갭 랭커의 `drivers=[]`
서술은(원 위임 프롬프트에 인용된 숫자) 정확히 이 팩과 일치하지만, `terms=['dispersant']`는
dedup이 고른 대표 팩(sic 둘 중 하나)의 것이다. 이 사실을 여기 기록하고 **다음 우선순위
(sic_ceria_h2o2)로 넘어간다.**

## 1. sic_ceria_h2o2 — 무엇이 필요한가

이 팩은 `dispersant_type: "NONE"`(own, 2026-09-14 판정#15)과 `shield_additive_wt_pct: 0.0`
(own, `shield_langmuir_K` 미선언)을 선언한다. 즉 두 경로 다 **의도적으로 비활성** —
"NONE"은 실리카형 억제를 전이하지 않는다는 판정의 결과이고, shield 경로는 SiC+세리아
첨가제 농도-RR 문헌이 없어서 막아둔 상태다(yaml 자체 주석). 빠진 드라이버를 채우려면
SiC(또는 최소 세리아 계) 위에서 첨가제/계면활성제 **농도 vs 제거율(또는 흡착량)**을
인쇄 수치로 주는 1차 문헌이 필요하다.

### 1.1 시도한 경로와 실패 사유

- **yaml이 이미 지목한 후보** "Zhou 2015 6H-SiC Triton X-100 (doi:10.1016/j.apsusc.2015.10.158)"
  — 이 DOI를 `tools/find_open_access.py`로 재조회하면 **Chen, Ni, Xu, Li (2015),
  "Performance of colloidal silica and ceria based slurries on CMP of Si-face 6H-SiC
  substrates", Appl. Surf. Sci. 359, 664–668**로 나온다. 저자가 Zhou가 아니라 Chen이고
  제목에 Triton X-100이 없다 — **이 DOI 인용 자체가 기존 노트의 오류**로 보인다(이미
  `papers/chen2015-apsusc-6hsic-ceria-kmno4-ph.pdf`로 로컬 확보돼 있고 계면활성제 언급
  0건, 아래 §1.2 verify 참조). "Zhou 2015 Triton X-100"이라는 실제 논문이 존재하는지는
  **확인하지 못했다** — 제목을 바꿔 재검색해도 못 찾음. 정직하게 "미확인"으로 남긴다.
- MDPI `10.3390/cryst13060869`(Triton X-100 0.5wt% 언급, 비수계 고정입자패드 SiC 연마) —
  Unpaywall이 CC-BY OA를 확인했으나 **이 세션에서 mdpi.com·mdpi-res.com·researchgate.net·
  papers.ssrn.com 전부 HTTP 403(Akamai 엣지 차단)** — 네트워크 승인 차단 세션으로 판단,
  로컬 코퍼스에도 fulltext 없음(discovered만, `data/corpus/corpus.sqlite`). 게다가
  **비수계(nonaqueous) 고정입자패드**라 이 팩(수계 슬러리, 자유입자)과 메커니즘이 달라
  전이 근거도 약하다.
- SSRN `10.2139/ssrn.4376071` / tandfonline `10.1080/23311916.2023.2272354`
  (Zhang, Xie, Lu — 이온성 계면활성제 SDS/CTAB/TX-100, 세리아 슬러리, STI) — WebSearch
  스니펫으로 "0.5 wt% SDS에서 MRR 2.58 μm/hr 최대"라는 **단일 최적점**만 확인됨(전체
  스윕 표는 WebFetch 전부 403이라 못 봄). 단일점은 이미 지시받은 결격 사유("그래프
  전용은 결격")와 같은 급의 결격 — 풀 데이터를 봐도 SiO2/Si3N4(STI)라 이 팩(SiC)과
  막질이 다르다.

```python verify
# Chen 2015 (실제로 이 DOI가 가리키는 진짜 논문) 로컬 사본에 계면활성제/분산제 언급이
# 없음을 확인 — "Zhou 2015 Triton X-100" 인용이 이 DOI와는 무관함을 재확인
import re
txt = open("papers/chen2015-apsusc-6hsic-ceria-kmno4-ph.pdf.txt", encoding="utf-8",
           errors="ignore").read()
for kw in ["surfactant", "dispersant", "Triton", "TX-100"]:
    assert kw.lower() not in txt.lower(), f"'{kw}'가 실제로 있다 — 재확인 필요"
# "Zhou"는 참고문헌 목록의 다른 저자 이름으로 2회 등장한다(본문 제1저자가 아님) —
# "Zhou 2015 Triton X-100"이라는 별개 논문이 이 사본 안에 없다는 것만 확인한다.
assert txt.lower().count("zhou") <= 3, "Zhou 언급 횟수가 예상보다 많다 — 재확인 필요"
assert "Chen" in txt or "664" in txt  # 원문 저자/페이지 표기 확인(대략)
print("확인: 로컬 Chen 2015 사본에 계면활성제 언급 없음, 'Zhou'는 참고문헌 목록의 타 저자일 뿐 —"
      " 'Zhou 2015 Triton X-100' 인용은 이 DOI의 오귀속으로 보인다.")
```

> ⚠ 위 발견(DOI 오귀속 가능성)은 `knowledge/cmp/psi-adsorption-shield-oxide-systems.md`
> §6 또는 `sic_ceria_h2o2.yaml`의 `shield_additive_wt_pct` 주석을 고쳐야 할 사안이지만,
> 이 위임의 담당 파일 범위 밖이라 **여기 기록만 하고 그 파일들은 건드리지 않았다.**

### 1.2 결론

**sic_ceria_h2o2에 대해서는 1차 문헌을 확보하지 못했다.** 네트워크 승인 차단(WebFetch
전부 403) + 로컬 코퍼스 fulltext 부재 + 발견된 후보 논문들의 막질 불일치(STI)·단일점
결격·메커니즘 불일치(비수계)가 겹쳤다. 이 팩은 `status=partial, terms=['dispersant']`
(dispersant_type=NONE인 상수 lookup, 실질적으로 무효 driver)로 남는다 — **버그가
아니라 정직한 미해결**이다.

## 2. sic_alumina_kmno4 — 실사용 가능한 1차 문헌 확보

이 팩(부모 sic_ceria_h2o2에서 분리, 판정#49-B: 산성 KMnO4/알루미나 고속 레짐)은
이미 **Su et al. 2011**(Procedia Engineering 24, 441–446, doi:10.1016/j.proeng.2011.11.2673,
로컬 사본 `papers/proeng-2011-11-2673-alumina-6h-sic.pdf.txt`)을 abrasive_size_peak_nm·
abrasive_size_exp_below/above_peak의 출처로 own 선언하고 있다. 같은 논문 §3.4에
**분산제 함량 스윕이 인쇄 수치로 있는데 아직 팩에 배선되지 않았다** — 새 논문을 찾을
필요 없이, 이미 신뢰 중인 문헌의 미사용 절이다.

### 2.1 원문 데이터 (§3.4, 텍스트 직접 인용)

> "The four slurries are prepared with the different dispersant content, such as 4ml,
> 8ml, 14ml and 20ml in slurry 500ml respectively... When the dispersant content
> increases from 8ml to 14ml, the MRR increases from 57nm/h to 59.3nm/h slightly. When
> the dispersant content increases to 20ml, but the material removal rate reduces to
> 45nm/h."

조건 고정: 알루미나 10g(W1.5), 산화제 5ml, pH 9(알칼리로 조정), P=2psi, np=60rpm,
nw=65rpm, 500ml 슬러리. 분산제 화학종은 원문에 "a type dispersant"로만 나오고
구체 명칭은 없음(미확인 — 지어내지 않는다).

인쇄된 수치 3점:
| 분산제 함량 (mL/500mL) | MRR (nm/h) |
|---|---|
| 8  | 57.0 |
| 14 | 59.3 (정점) |
| 20 | 45.0 |

4mL 점은 본문에 "낮을 때는 증가" 정성 서술만 있고 숫자가 없다 — **지어내지 않고
누락으로 남긴다.**

### 2.2 물리적 해석 — 왜 ψ가 아니라 두 메커니즘이 섞여 있는가

저자 자신의 설명(§3.4): 낮은 농도에서 MRR 상승은 "분산도가 오르며 실제 마모에
관여하는 연마입자 개수가 늘어서"(**분산 품질 → 유효 연마입자 개수 → 기계적 작용**,
이것은 ψ의 정의(표면 흡착 보호)가 아니라 κ(연마입자 유효성) 영역이다). 20mL에서의
하락은 "이유는 추가 연구가 필요하다"(원문 그대로, 저자도 확정하지 못함) — 이 하락
구간만 **과잉 흡착이 연마입자·SiC 표면을 덮어 기계적 접촉을 줄인다**는 ψ의 정의에
부합할 수 있는 후보 메커니즘이다.

**따라서 이 데이터 전체를 ψ 하나의 단조 함수로 넣을 수 없다.** 상승 구간(4→14mL)은
ψ의 스코프 밖(κ 영역, 이 노트의 담당 파일 밖이라 별도 미모델링으로만 신고), 하락
구간(14→20mL)만 ψ 후보다.

### 2.3 함수형 — 정점 기준 단일 지수 감쇠 (2점 결정, 새 계수 최소화)

하락 구간 데이터는 정확히 2점(정점 14mL=59.3, 20mL=45.0)뿐이다. 이미 이 코드베이스가
같은 상황(2점 데이터)에서 쓴 전례가 있다 — `sim/chemistry.py::_chelator_suppression_term`
(글리신 2점, Hill/Langmuir 3파라미터 대신 **단일 지수 1파라미터**를 씀, "K가 식별되지
않는다"는 이유를 노트에 명시). 같은 논리를 그대로 적용한다:

```
f(C) = exp(-a · (C - C_peak))   for C ≥ C_peak
```

`C_peak`는 자유도가 아니라 **원문 데이터의 정점 위치**(14mL)이고, `a`는 남은 2점
(14, 20mL)에서 유일하게 정해진다(1파라미터·1자유도 — 축퇴 없음).

```python verify
import math

# Su et al. 2011 §3.4 원문 인쇄값 (doi:10.1016/j.proeng.2011.11.2673)
C_peak, MRR_peak = 14.0, 59.3   # mL/500mL, nm/h
C_hi, MRR_hi = 20.0, 45.0

a = -math.log(MRR_hi / MRR_peak) / (C_hi - C_peak)
assert abs(a - 0.045991) < 1e-4, a   # 1/mL

# 재현 (정의상 항등 — 2점으로 1파라미터를 풀었으므로 당연히 딱 맞는다)
pred = MRR_peak * math.exp(-a * (C_hi - C_peak))
assert abs(pred - MRR_hi) < 1e-6, pred

# 상승 구간(8->14mL)은 이 함수형으로 설명되지 않음을 명시적으로 확인 —
# 같은 a로 8mL을 외삽하면 원문(57.0)과 얼마나 어긋나는지
pred_8_wrong_direction = MRR_peak * math.exp(-a * (8.0 - C_peak))
obs_8 = 57.0
err = pred_8_wrong_direction / obs_8 - 1.0
# 부호(하락형 함수가 상승 구간에 맞을 리 없음)와 큰 오차를 직접 확인 — "적용 범위 아님"의 증거
assert pred_8_wrong_direction > obs_8, (pred_8_wrong_direction, obs_8)
assert err > 0.15, err
print(f"a={a:.6f} /mL, C_peak=14mL. 상승구간 외삽 오차 {err*100:.1f}% — "
      f"하락구간 전용 함수임을 확인(상승구간은 κ영역, 별도 미모델링).")
# 문헌값 대조 재현: a=0.045991/mL로 20mL 지점의 원문 MRR 45.0 nm/h(=Su 2011 §3.4 인쇄값)를 오차 1e-6 이내로 재현했다.
assert abs(pred / MRR_hi - 1.0) < 1e-6

# 단위 환산: mL/500mL 슬러리 -> vol% (문헌 원 단위 그대로 두되 참고용)
to_volpct = lambda ml: ml / 500.0 * 100.0
assert abs(to_volpct(14.0) - 2.8) < 1e-9
assert abs(to_volpct(20.0) - 4.0) < 1e-9
```

### 2.4 이 제안의 한계 (정직성 표기)

- **화학 레짐 불일치**: Su 2011은 **알칼리 pH 9**, 이 팩(sic_alumina_kmno4)은
  **산성 pH 2.3 KMnO4**(팩 자신의 헤더 주석이 "Su 2011은 다른 레짐이라 분리했다"고
  명시적으로 적어 둔 바로 그 논문이다 — `sic_alumina_kmno4.yaml` 상단 주석 참조).
  이 팩이 이미 abrasive_size 형상에 Su 2011을 쓰는 것과 **같은 수준의 절충**이지만,
  입경(기하) 전이보다 흡착 화학(분산제-표면 상호작용) 전이가 **pH·산화제에 훨씬
  민감**하다 — 이 절충은 abrasive_size 사례보다 근거가 약하다. **미검증으로 표기한다.**
- **폴리타입**: Su 2011은 6H-SiC, 이 팩은 4H-SiC. 표면 화학이 완전히 같다는 보장 없음
  (이미 abrasive_size_peak_nm 주석이 같은 한계를 인정한 전례를 따른다).
  이 팩은 4H와 6H를 혼용 표기하고 있다(header: "4H/6H-SiC CMP") — 폴리타입 구분
  자체가 이 팩 설계에서 느슨하다.
  - **화학종 미상**: 원문이 분산제 종류를 밝히지 않는다("a type dispersant"). 기존
  ψ의 `dispersant_type` 이산 룩업(PVA/PVP, Li 2021)과는 다른 축 — 새 화학종을
  기존 룩업에 끼워 넣으면 안 되고, **연속 농도축**(이미 있는 `shield_additive_wt_pct`
  패턴과 형식은 같지만 지배 방정식이 다름 — Hill/Langmuir 피복이 아니라 정점형
  지수 감쇠)으로 별도 취급해야 한다.
- **단위**: 원문이 mL/500mL(부피비)이지 wt%가 아니다. 밀도를 모르므로 wt% 환산은
  **하지 않는다**(지어낸 환산이 됨) — 새 파라미터는 mL 단위(또는 vol%, §2.3 환산)
  그대로 받아야 한다.
- **정점 위치(C_peak=14mL) 자체가 근사**다 — 원문은 8→14mL을 "slightly increases"라고만
  적어 진짜 정점이 14mL 정확히인지, 8~14mL 사이 어딘가인지 확정할 수 없다(4mL 값
  부재로 상승 구간 형상도 모른다). **C_peak은 관측된 최댓값 지점이지, 참 정점이라는
  보장은 없다.**
- **상승 구간(4→14mL)은 여전히 미모델링**이다 — 이 노트의 스코프(ψ)가 아니라 κ(연마입자
  유효 개수) 영역이라는 저자의 설명을 따랐지만, sic_alumina_kmno4의 κ 팩터에 이
  메커니즘이 배선돼 있는지는 **확인하지 않았다**(담당 파일 범위 밖).

### 2.5 왜 새 파라미터인가 — 유도 불가능성

`a`(0.04599 /mL)는 분산제-SiC(또는 분산제-알루미나 연마입자) 흡착의 열역학 상수가
아니라 **이 특정 CMP 장비·조건에서 관측된 경험적 감쇠율**이다. Langmuir K처럼 흡착
자유에너지에서 원리적으로 유도되는 양이 아니라(원문이 흡착등온을 측정하지 않음,
MRR만 측정), 기존 물성(abrasive_density 등)에서 계산할 수 없다 — 문헌 3점 회귀로만
얻어지는 값이므로 **새 상수 선언이 맞다**(기존 `chelator_suppression_a`와 동일 범주).

## 3. 배선 요청 (구현은 총괄이 한다 — 아래는 제안 diff)

**`knowledge/params/sic_alumina_kmno4.yaml`에 추가 제안** (own 선언, 부모의
`shield_additive_wt_pct=0.0`/`dispersant_type=NONE` 상속을 덮지 않고 **별도 키**로):

```yaml
  alumina_dispersant_content_ml:
    value: <운전 조건의 실제 분산제 투입량 — 이 팩의 기본 레시피에 현재 없음, 확인 필요>
    unit: "mL/500mL slurry"
    source: "Su et al. 2011, doi:10.1016/j.proeng.2011.11.2673 §3.4"
    confidence: unverified   # 화학종 미상 + 레짐 불일치(§2.4) 때문에 literature 등급 불가
  alumina_dispersant_peak_ml:
    value: 14.0
    unit: "mL/500mL slurry"
    source: "Su et al. 2011 §3.4 (관측 최댓값, 참 정점 아닐 수 있음)"
    confidence: unverified
  alumina_dispersant_falloff_a_per_ml:
    value: 0.045991
    unit: "1/mL"
    note: "C >= peak 구간에서만 적용. C < peak는 미모델링(κ 영역, 별도)."
    source: "Su et al. 2011 §3.4, 2점(14/20mL) 단일 지수 회귀 — §2.3 verify"
    confidence: unverified
```

**`sim/factors.py::_f_psi`에 세 번째 하위 경로 제안** (기존 ① 억제제 Langmuir,
② shield Hill 흡착, ③ dispersant 이산 룩업과 병렬, `_chelator_suppression_term`과
같은 단일지수 패턴을 따름):

```python
# ④ 정점형 단일 지수 감쇠 — 분산제 과잉 흡착(Su 2011 §3.4, 하락 구간 전용)
if pk.has("alumina_dispersant_content_ml") and pk.has("alumina_dispersant_peak_ml") \
        and pk.has("alumina_dispersant_falloff_a_per_ml"):
    C = float(pk.get("alumina_dispersant_content_ml"))
    C_pk = float(pk.get("alumina_dispersant_peak_ml"))
    a = float(pk.get("alumina_dispersant_falloff_a_per_ml"))
    if C >= C_pk:
        val = math.exp(-a * (C - C_pk))
        terms["dispersant_overcoat"] = val
        f.drivers["alumina_dispersant_content_ml"] = C
        confs.append(_pack_conf(pk, "alumina_dispersant_falloff_a_per_ml"))
        srcs.append("knowledge/cmp/psi-drivers-sic-alumina-kmno4.md §2.3")
    else:
        f.notes.append("⚠ 분산제 함량이 정점 미만 — 상승 구간은 ψ 미모델링(κ 영역), 항등 1.0")
```

이 제안을 넣으면 `C < C_pk`(정점 미만)에서는 여전히 `terms`가 비어 있을 수 있어
`status`가 `partial`로 남는다 — **거짓으로 `modeled`를 만들지 않는다.** `C >= C_pk`
운전점에서만 `modeled`(또는 다른 항과 함께 `partial`)로 승격된다.

⚠ **선결 조건**: 이 팩의 현재 기본 레시피(`params:` 블록)에 분산제 투입량이
파라미터로 없다 — `alumina_dispersant_content_ml`의 실제 운전값을 어디서 가져올지
(예: US20220315802A1 Table 1에 분산제 항목이 있는지) **확인하지 않았다**. 값이
없으면 이 항은 선언은 되어도 실제로 운전점에서 켜지지 않을 수 있다 — 총괄이 배선
전에 확인해야 한다.

## 4. 요약

| 팩 | 상태 | 결론 |
|---|---|---|
| cu_alkaline_benzenesulfonic | 이미 해소됨(판정#70) | 재작업 불필요 — [[psi-cu-alkaline-h2o2-passivation]] |
| sic_ceria_h2o2 | 미해결 | 1차 문헌 확보 실패(네트워크 차단 + 막질/메커니즘 불일치) — §1 |
| sic_alumina_kmno4 | **문헌 확보, 배선 제안 있음** | Su 2011 §3.4, 2점 지수 감쇠, 미검증 등급 — §2·§3 |

## 관련 노트

[[psi-cu-alkaline-h2o2-passivation]], [[chi-oxidizer-cu-h2o2-reparameterization]],
[[psi-adsorption-shield-oxide-systems]], [[alumina-abrasive-size-mrr-relation]],
[[psi-surface-adsorption-shield-oxide-ceria]]
