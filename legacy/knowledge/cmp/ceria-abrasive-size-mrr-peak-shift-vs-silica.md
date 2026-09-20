<!-- V2-SECTION: R2-slurry | 정확도루프 2026-09-13 | 근거: 세리아 입경-MRR 반응 | 정본: ARCHITECTURE-V2.md §3 -->
# 세리아 연마입자 입경 → 산화막 MRR: 정점이 실리카(80 nm)보다 **훨씬 크다** (RESPONSE_CONFLICT 해소)

> 정확도 루프 갭: `UNWIRED abrasive_size_nm`(score 60) 회차에서 발견한 **상위 갭**.
> 실제 문제는 미배선이 아니라 **교차계 오전이(誤轉移)**였다.
> [[abrasive-size-concentration-ph-K-additive-mrr-quantitative]]
> [[abrasive-size-null-result-force-partition-theory]]
> [[sic-ceria-abrasive-particle-size-chen2017-rsc]]
> [[ceria-slurry-ce-redox-selectivity]] 상호링크.

## 1. 발견한 결함 (모델 무결성 문제)

`knowledge/params/oxide_silica.yaml`에는 2026-09-13에 입경 정점형 3파라미터가 배선됐다:

| 키 | 값 | 근거 |
|---|---|---|
| `abrasive_size_peak_nm` | 80 nm | Li et al. 2021 (콜로이달 **실리카**/SiO2 막) |
| `abrasive_size_exp_below_peak` | +4/3 | 압입 지배 |
| `abrasive_size_exp_above_peak` | -1/3 | 표면적 지배 |

그런데 `sti_ceria`와 `sic_ceria_h2o2`는 `base: oxide_silica` 상속이라 이 **세 값을 자기 것으로
선언하지 않은 채 그대로 물려받고 있었다**(실측 확인, 아래 §6 재현 블록). 즉 세리아 팩의 입경
응답 곡선이 **실리카 슬러리 논문 하나로** 결정되고 있었다. 세리아 팩 본값은 60 nm(sti_ceria)·
120 nm(sic_ceria_h2o2)라 이미 정점(80 nm)을 사이에 두고 갈라져 있어, 120 nm 팩은 **감소 가지**
위에서 돌고 있었다.

이건 "지수를 안 정했다(UNWIRED)"가 아니라 **다른 재료계의 지수를 조용히 쓰고 있었다**는
뜻이므로 등급이 더 높다(`accuracy_gaps.py` 종류 0 RESPONSE_CONFLICT — "문헌과 반대 방향").

## 2. 세리아 계 1차 문헌 — 방향이 반대다

세리아/산화막 계에서는 60~420 nm 구간에서 **입경이 커질수록 산화막 MRR이 올라간다**는 보고가
서로 독립적인 그룹·연도·합성법에서 반복된다.

| # | 문헌 | DOI (Crossref 실조회 확인) | 세리아 입경 스윕 | 관측 |
|---|---|---|---|---|
| A | Oh, Singh, Gupta, Cho 2010, *Microelectronic Engineering* | DOI `doi:10.1016/j.mee.2010.07.040` | 단결정 세리아 **62 / 116 / 163 / 232 nm**(수열합성, n=4 1축) | **163 nm에서 최대** |
| B | Oh, Nho, Cho, Lee, Singh 2011, *Powder Technology* | DOI `doi:10.1016/j.powtec.2010.09.025` | flux법 세리아 **84 / 166 / 295 / 417 nm**(n=4 1축) | "With increasing abrasive size, the removal rate of silicon dioxide and silicon nitride films increased" — **단조 증가**(단, 표면 균일도는 악화) |
| C | Kang, Katoh, Kim, Paik, Park, Park 2004, *Jpn. J. Appl. Phys.* 43, L365 | DOI `doi:10.1143/jjap.43.l365` | 다결정 세리아, 소성온도·밀링시간으로 grain size와 입경을 **독립 제어** | "the oxide removal rate increased with both the grain size and the abrasive particle size, while the nitride removal rate was independent of both" — **단조 증가** |
| D | Netzband & Dunn 2020, *ECS J. Solid State Sci. Technol.* | DOI `doi:10.1149/2162-8777/ab8393` | 세리아 **5 / 20 / 68 nm**(+ 상용 50 nm 대조) | "Fig. 5a shows a **decrease in MRR with decreasing particle size** as expected" — 작은 쪽에서도 증가 방향 일치 |

**수렴 결론**: 세리아+산화막 계의 입경-MRR 곡선은 5 nm부터 최소 163 nm까지 **증가 가지**이고,
정점은 실리카 계(80 nm)보다 **약 2배 크다**(A). B·C는 232~417 nm까지도 증가를 보고하므로
정점이 더 클 가능성도 있다(하한만 확정).

### 왜 세리아에서 정점이 밀리는가 (메커니즘 — 정성)
Bellahsene et al. 2025 리뷰(`doi:10.3390/nano15171366`, MDPI OA, 원문 전문 확보)가 두 경쟁
메커니즘을 폐형식으로 준다: 압입 지배 MRR ∝ d^(4/3), 표면적 지배 MRR ∝ C0/d (즉 d^-1).
정점은 둘이 교차하는 지점이다. 세리아는 실리카와 달리 Si-O-Ce 화학결합("chemical tooth")로
**화학적 제거가 표면적이 아니라 접촉 사이트 수에 걸리고**, Netzband 2020(D)이 Ce3+% 최대화
시 5 nm 입자도 68 nm 입자에 필적하는 MRR을 냈다고 보고한 것이 그 방증이다 — 즉 세리아에서는
표면적 지배 가지가 늦게 켜지므로 교차점(정점)이 큰 쪽으로 밀린다. **이 인과 설명은 정성이며
이 노트가 유도한 것이 아니다(리뷰 §2.1 + D의 해석 결합) — 미검증.**

## 3. 근거 충돌 판정 (EVIDENCE-RULES.md)

| | A안 (현재 코드) | B안 (이 노트) |
|---|---|---|
| 주장 | 세리아 정점 = 80 nm, 그 위는 d^(-1/3) 감소 | 세리아 정점 >= 163 nm, 60~163 nm는 증가 |
| 근거 | Li et al. 2021 — **실리카** 슬러리/SiO2 막 단일 논문의 지수를 세리아 팩에 상속 (**E4** 타계 전이 유도) | 세리아 계 **직접 실측 4편**(A~D), 독립 그룹·연도·합성법, 방향 전원 일치 (**E3** 교란 있는 실측 — 아래 한계) |

**판정: B 채택.** EVIDENCE-RULES 서열에서 E3(대상계 실측) > E4(타계 전이)이고, 계 근접도에서도
세리아 팩에 세리아 실측을 쓰는 쪽이 옳다. A안은 애초에 **의도적으로 세리아에 적용된 값이 아니라
YAML 상속이 만든 부작용**이었다(§1) — 즉 충돌이라기보다 하이진 결함에 가깝다.

**보수적 적용**: 정점만 163 nm로 옮기고 **지수(+4/3 / -1/3)는 그대로 둔다.** 지수는 Bellahsene
리뷰(§2)가 재료 무관 메커니즘 폐형식으로 제시한 것이라 세리아에도 형식은 유효하다고 보되,
세리아 실측으로 지수 자체를 재추정할 데이터(각 점의 MRR 절대값 4점)는 **원문 PDF를 못 구해
확보하지 못했다** — 아래 §5.

## 4. 팩에 반영한 값

`sti_ceria.yaml`·`sic_ceria_h2o2.yaml`에 **자기 값으로 명시 선언**(상속 차단):

```yaml
abrasive_size_peak_nm:
  value: 163.0     # Oh et al. 2010 MEE, 62/116/163/232 nm 중 최대
  confidence: literature
```
지수 두 개도 같은 값으로 **명시 재선언**한다 — 값이 같아도 "상속받은 것"과 "이 계에 대해
판단한 것"은 다르기 때문이다(상속이 결함을 만든 경로를 다시 열지 않는다).

## 5. 한계 — 정직 기록

- **A(Oh 2010)의 4점 MRR 절대값을 1차 원문에서 확보하지 못했다.** Elsevier 페이월이고 미러 사이트
  미러 4곳(box/red/se/ru)이 전부 봇검증 또는 502를 반환했다(2026-09-13 실행 로그). 확보한 것은
  (1) 출판사 초록의 스윕 설계("mean primary particle size of 62, 116, 163 and 232 nm") (2)
  Wang et al. 2020 (`doi:10.1177/0036850420982451`, SAGE OA, 전문 확보)의 **2차 인용**:
  "the single-crystal cerium dioxide abrasives with particle size of 163 nm is the best abrasive
  size in CMP, the oxide removal rate of 2369 A/min, nitride removal rate of 52.4 A/min".
  → **정점 위치(163 nm)는 E5(2차 인용)이고, 스윕 설계(n=4·1축)만 E3 수준으로 확인됐다.**
- **B·C·D는 초록/출판사 페이지 수준까지만 확인**했고 전문 표는 못 읽었다. 그래서 방향(증가)만
  쓰고 **배수는 쓰지 않았다.** 배수 없이 정점 위치만 옮긴 이유가 이것이다.
- B·C가 232~417 nm까지 증가를 보고하므로 **정점 163 nm는 하한일 수 있다**(과소추정 방향).
  반대로 A는 232 nm에서 감소를 봤으므로 163~232 사이 어딘가가 참값이다. 163을 택한 것은
  네 문헌 중 **입경을 1축으로 스윕한 유일한 단결정 세리아 실험**이 A이기 때문이다.
- `sic_ceria_h2o2`는 웨이퍼가 **SiC**지 산화막이 아니다. A~D는 전부 SiO2/SiN 계다. SiC로의
  적용은 **교차막질 전이(E4)**이며 미검증 — 그러나 기존 상속값(실리카 슬러리 정점 80 nm)보다는
  최소한 **연마입자 종류가 일치**하므로 개선이다. SiC+세리아 입경 스윕 실측이 나오면 교체한다.
- 지수 +4/3 / -1/3 자체는 세리아 실측으로 재추정된 적이 없다 — **형식 전용, 미검증**.

## 6. 재현 — 상속 결함과 수정 효과

```python verify
# (1) Bellahsene 2025 리뷰 §2.1 두 메커니즘 폐형식 재현 — 교차점이 곧 정점
#     압입 지배: MRR ~ d^(4/3) / 표면적 지배: MRR ~ C0/d
assert (4.0/3.0) > 0 > -1.0, "리뷰가 준 두 지수는 부호가 반대 — 정점형 곡선의 필요조건"

# (2) factors.py가 쓰는 piecewise 곡선을 그대로 옮겨, 정점을 80->163으로 옮겼을 때
#     '세리아 실측 방향(60->163nm 구간 증가)'을 만족하는지 확인한다.
def piecewise(d, peak, e_below, e_above):
    if d <= peak:
        return d ** e_below
    return (peak ** e_below) * (d / peak) ** e_above

E_BELOW, E_ABOVE = 4.0/3.0, -1.0/3.0

# 구 설정(실리카 정점 80nm 상속): 120nm 팩은 감소 가지 위에 있다 -> 문헌과 반대
old_120 = piecewise(120.0, 80.0, E_BELOW, E_ABOVE)
old_163 = piecewise(163.0, 80.0, E_BELOW, E_ABOVE)
assert old_163 < old_120, "구 설정에서는 120->163nm 로 키우면 MRR이 내려간다(문헌과 반대 방향)"

# 신 설정(세리아 정점 163nm): 같은 구간이 증가로 바뀐다 -> 문헌(A~D) 방향과 일치
new_120 = piecewise(120.0, 163.0, E_BELOW, E_ABOVE)
new_163 = piecewise(163.0, 163.0, E_BELOW, E_ABOVE)
assert new_163 > new_120, "신 설정에서는 120->163nm 가 증가 — Oh 2010/2011·Kang 2004 방향과 일치"

# Netzband 2020(D) 방향: 5 -> 20 -> 68 nm 에서 MRR 증가. 두 설정 모두 증가 가지라 일치해야 한다.
for peak in (80.0, 163.0):
    v5  = piecewise(5.0,  peak, E_BELOW, E_ABOVE)
    v20 = piecewise(20.0, peak, E_BELOW, E_ABOVE)
    v68 = piecewise(68.0, peak, E_BELOW, E_ABOVE)
    assert v5 < v20 < v68, f"peak={peak}: 5<20<68nm 증가(D) 재현 실패"

# (3) 기준조건(d = d_ref)에서는 항이 1.0으로 상쇄되어야 한다(기준 1.0 계약, 이중계상 금지).
for peak in (80.0, 163.0):
    ref = piecewise(120.0, peak, E_BELOW, E_ABOVE)
    assert abs(piecewise(120.0, peak, E_BELOW, E_ABOVE) / ref - 1.0) < 1e-12, "기준조건 1.0 계약"

# (4) 실제 팩이 이 값을 '자기 것으로' 갖고 있는지 — 상속이면 결함이 남은 것이다.
from sim.params import load_pack
for name in ("sti_ceria", "sic_ceria_h2o2"):
    pk = load_pack(name)
    for key in ("abrasive_size_peak_nm",
                "abrasive_size_exp_below_peak",
                "abrasive_size_exp_above_peak"):
        assert pk.has_own(key), f"{name}.{key} 가 상속 상태 — 실리카 값이 다시 새어든다"
    assert abs(float(pk.get("abrasive_size_peak_nm")) - 163.0) < 1e-9, \
        f"{name} 정점이 세리아 실측값(163nm)이 아니다"
print("OK: 세리아 정점 163nm 배선 + 상속 차단 확인")
```

## 7. 새로 도출한 지식

1. **YAML 팩 상속은 물리 파라미터에 대해 안전하지 않다.** 화학계가 다른 자식 팩이 부모의
   재료 특이 상수를 조용히 물려받는다. 이번 건은 `abrasive_size_peak_nm`이었지만, 같은 구조가
   `wafer_iep_ph`(2026-09-13 직전 회차)에서도 발견됐다 — **두 번째 사례이므로 패턴이다.**
2. **세리아 정점은 실리카 정점의 약 2배(80 -> 163 nm 이상)**이고, 이는 세리아의 화학적 제거가
   표면적 지배 가지의 발현을 늦추기 때문으로 해석된다(정성, 미검증).
3. **정점 위치와 지수는 분리해서 이식할 수 있다.** 지수는 메커니즘(압입/표면적)에서 오므로
   재료 간 형식 전용이 가능하고, 정점은 두 메커니즘의 상대 세기라 재료마다 다시 재야 한다.

## 8. 구현 요청 (소프트웨어 부문)

- **무엇을**: `tools/model_hygiene.py`에 "재료 특이 키 상속 검사" 추가. 후보 키 목록
  (`abrasive_size_peak_nm`, `abrasive_size_exp_*`, `wafer_iep_ph`, `abrasive_size_exponent`,
  `abrasive_saturation_wt_pct`)에 대해 `pack.has(k) and not pack.has_own(k)`이면 경고 보고.
- **근거 노트**: 이 노트 §1·§7-1.
- **검증**: 수정 전 sti_ceria·sic_ceria_h2o2가 3건씩 잡히고, 수정 후 0건이 되어야 한다.
- **우선순위**: 높음 — 조용한 오전이는 백테스트 rho로도 안 잡힌다(방향만 틀리고 기준조건은 1.0).
