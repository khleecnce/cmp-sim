<!-- V2-SECTION: R2-slurry | 정확도루프 구조결함 수정 sic_alumina_kmno4 2026-09-18 -->
# sic_alumina_kmno4 연마입자 정체성 상속 결함 — 세리아 행세를 하던 알루미나 팩

> 판정#59 (2026-09-18, Max워커). 결론: 팩 `abrasive` 키가 부모의 `ceria` 를 상속하고 있어
> 알루미나 슬러리에 세리아 화학항이 켜져 있었다. 자기선언 + `_f_chi` 2차 패스 재료 일치
> 검사로 수정. **완성 격자 60/60 → 59/60 (의도된 후퇴, §5 참조)**, MRR 농도축 비트 불변,
> 나머지 5팩 전부 불변.
> 선행: [[sic-alumina-kmno4-L25-heldout-diagnosis]] (§3 pH축 사인은 "세리아 전용이라 꺼짐"으로
> 오진; 이번 노트가 그 진단을 한 단계 더 좁힌다 — 실제 사인은 `abrasive` 키 자체가
> 부모의 `'ceria'` 를 상속하고 있었다는 것)

## 1. 결함

`sim.params.load_pack('sic_alumina_kmno4')` 확인 결과 `abrasive` 키가 **own=False**로
부모(`sic_ceria_h2o2`)의 `'ceria'` 를 그대로 물려받고 있었다. 팩 자체는
`abrasive_density_kg_m3`(α-Al2O3 3950 kg/m³)·description·근거 문헌(US20220315802A1,
Gong 2024) 전부 알루미나라고 말하는데, `_f_chi` 의 분기 판정 키만 세리아였다.

결과:
- `_ceria_term`(ceria chemical tooth)이 알루미나 슬러리에 켜져 있었다.
- pH 분기가 `ph_ceria_window`(세리아 IEP 창)로 들어가 `wafer_iep_ph` 부재로 skip.

## 2. 함정 — abrasive만 고치면 실리카 곡선이 대신 뒤집어쓴다

`abrasive: alumina` 만 선언하면 `is_ceria=False` 가 되어 세리아 분기는 꺼지지만,
기존 `_f_chi` 2차 패스(own 계수가 아무도 없을 때의 폴백)가 다음 우선순위 후보인
`ph_peak`(오이드_silica 소유, 정점 pH=11)로 떨어진다. 실측 확인: pH 2~6 대입 시
chi = 1.7066 / 0.3636 / 0.1519 / 0.1243 / 0.1995 — 실리카 산화막 정점 곡선을
산성 알루미나/KMnO4계에 그대로 씌운 오염값이다.



## 3. 수정 — 두 층

### 3.1 팩: `abrasive: alumina` 자기선언
`knowledge/params/sic_alumina_kmno4.yaml`. 새 문헌값을 만들지 않았다 — 같은 파일이
이미 `abrasive_density_kg_m3`(α-Al2O3 3950 kg/m³, CRC)로 알루미나를 선언하고 있었고,
출처 두 건(US20220315802A1 Table 1, Gong 2024 doi:10.3390/ma17030679 Table 1 "Al2O3
500 nm")이 모두 알루미나라고 인쇄돼 있다. 즉 **누락된 선언을 채운 것**이지 새 주장이
아니다.

### 3.2 `_f_chi` 2차 패스: 소유 조상의 연마입자 검사
팩 이름 하드코딩 없이(판정#34 원칙) 일반 규칙으로 구현했다:

> pH 메커니즘의 고유 계수를 팩이 **직접 선언하지 않고 상속만** 받았고, 그 계수를
> **소유한 조상 팩의 `abrasive`가 이 팩의 `abrasive`와 다르면**, 그 분기를 쓰지 않는다.

own 계수는 이 검사를 구조적으로 항상 통과한다(자기 재료가 자기 계수를 쓴 것이므로
불일치가 성립할 수 없다). 후보가 전부 막히면 pH 항 없이 `terms`에서 빠지고 `notes`에
**어느 키가 어느 팩(어느 재료)에서 왔는지** 남는다 — 조용히 끄지 않는다.

## 4. 수정 후 실측 (Max워커 직접 실행)

`_f_chi(sic_alumina_kmno4)` 기준조건:

```
value = None      terms = {}
notes:
  ⚠ χ 미모델링: 산화제·pH·세리아 파라미터가 팩에 없다.
  ⚠ pH 분기 'ph_peak'의 고유 계수 'ph_peak'는 oxide_silica 팩(연마입자=silica)이
     소유한 상속값인데 이 팩의 연마입자는 alumina다 — 재료가 달라 쓰지 않는다(판정#59).
  ⚠ pH 분기 'ph_softening'의 고유 계수 'ph_softening_per_unit'는 sic_ceria_h2o2 팩
     (연마입자=ceria)이 소유한 상속값인데 이 팩의 연마입자는 alumina다 — 쓰지 않는다.
  ⚠ pH 항 미모델링: 후보 전부 재료 불일치로 막힘 — 고유 pH 계수 확보까지 갭.
  ⚠ oxidizer_langmuir_K 는 H2O2 로 적합됐는데 이 팩의 산화제는 KMnO4 다(판정#56 종결).
```

MRR 스윕(nm/min, pH5·KMnO4 2wt%·Al2O3 3wt% 기준점):

| 축 | 수정 전 | 수정 후 |
|---|---|---|
| pH 2/3/4/5/6 | 16.7858 전부 | 8.1098 전부 |
| KMnO4 1~5 wt% | 16.7858 전부 | 8.1098 전부 |
| Al2O3 1/2/3/4/5 wt% (축 출처: US20220315802A1 Table 1) | 12.6684 / 9.5610 / 8.1098 / 7.2158 / 6.5908 | **동일(비트 일치)** |

**연마입자 농도축은 비트 단위로 불변**이다. 절대 스케일이 16.79→8.11로 내려간 것은
`ceria_tooth` 항이 기준점 밖(Ce³⁺ 분율 상속값)에서 1.0이 아니었기 때문이고, 이는
**애초에 알루미나 슬러리에 켜져 있으면 안 되는 항**이었다. `kp_m_per_pa`는 손대지
않았다 — 되맞추는 것은 회귀식화다(COMPLETION.md 작업 우선순위).

5팩(cu_h2o2_bta·oxide_silica·sic_ceria_h2o2·sti_ceria·w_fe_oxidizer)의 `_f_chi`
분기 선택과 값은 **전부 불변**임을 직접 확인했다:

```
cu_h2o2_bta    chi=1  {'oxidizer': 1.0, 'ph_cu_acidic': 1.0}
oxide_silica   chi=1  {'ph_peak': 1.0}
sic_ceria_h2o2 chi=1  {'oxidizer': 1.0, 'ceria_tooth': 1.0, 'ph_softening': 1.0}
sti_ceria      chi=1  {'ceria_tooth': 1.0, 'ph_ceria_window': 1.0}
w_fe_oxidizer  chi=1  {'oxidizer': 1.0, 'ph_w_acidic': 1.0}
```

## 5. ⚠ 완성 격자 60/60 → 59/60 — 의도된 후퇴다

`tools/completion.py check` 가 **C1 χ/sic_alumina_kmno4: status=unmodeled** 를 새로
신고한다. 이것은 C7(무퇴보)에 걸리는 변화이므로 숨기지 않고 여기에 기록한다.

**되돌리지 않는 이유**: 이전의 `modeled` 는 이 팩이 **남의 재료(세리아) 화학항을
켜고 있었기 때문에** 성립한 등급이었다. 즉 그 칸은 "모델링돼 있었다"가 아니라
**"틀린 것이 모델링돼 있었다"** 이다. 되돌리면 격자 숫자는 복구되지만 알루미나
슬러리가 Ce³⁺ 분율에 반응하는 출력을 계속 내보낸다 — COMPLETION.md 가 금지하는
오염이다("문헌이 없는 것을 지어내 채우는 것은 완성이 아니라 오염이다").

정확히 말하면 격자가 내려간 게 아니라 **격자가 그동안 1칸 과대계상돼 있었고 이제
실제 상태를 가리킨다.** 이 칸을 다시 올리는 유일한 정당한 경로는 **산성 알루미나/
KMnO4 계의 pH 또는 산화제 형상 1차 문헌 확보**다(산화제축은 판정#56으로 3회차
종결됐으므로 실질 경로는 pH축 하나).

## 6. held-out 결과 — 갭의 이유가 바뀌었다

`gong2024_4hsic_alumina_kmno4_L25`(n=25, 3축 DOE)에서 pH·산화제 2축 무반응은
**여전하다**. 그러나 이유가 달라졌고, 그것이 이번 작업의 성과다:

- 수정 전: "세리아 IEP 창 분기가 `wafer_iep_ph` 부재로 skip" — **틀린 이유**.
  (이 팩엔 세리아가 없으므로 `wafer_iep_ph` 를 채워도 옳은 곡선이 나오지 않는다.
   그 노트대로 후속 크론이 `wafer_iep_ph` 를 넣었다면 알루미나 계에 세리아 정전
   창을 씌우는 오염이 발생했을 것이다 — 이번 수정이 그 함정을 제거했다.)
- 수정 후: "알루미나계 pH 계수 미확보" — **맞는 이유**. 다음 회차가 찾아야 할
  문헌이 무엇인지가 정확해졌다.

`qa_loop run --strict` PASS, 유의 데이터셋 9/27, 유의 평균 ρ = 0.9566 (직전 0.9512).
ρ 상승은 이 작업이 아니라 같은 루프에서 `us9200180b2_cu_abrasive_series` 가
비유의→유의로 전환된 결과다(다른 크론 소관, 여기 귀속하지 않는다).

## 7. 남은 갭 (지어내지 않고 남긴다)

1. **산성 알루미나/KMnO4 SiC 계의 pH 의존 1차 문헌** — 확보되면 이 팩이 고유
   pH 계수를 자기선언하고 χ 칸이 정당하게 복구된다. Gong 2024 Table 3 의 극차분석
   k 값(pH R=0.1104)이 출발점이나, 그 논문 자체가 본문("최적 pH=4")과 Table 3
   (pH=5 최대)에서 **서로 다른 값을 말한다**(데이터셋 YAML 주석에 기록됨) — 그대로
   계수로 쓸 수 없다.
2. **KMnO4 산화제 형상** — 판정#56 으로 영구 종결. 재탐색 금지.
3. **다른 팩에도 같은 유형의 정체성 상속 결함이 있는가** — 이번엔 `abrasive` 키만
   봤다. `film`·`oxidizer` 등 다른 정체성 키에 대해 own/상속 전수 감사를 하면
   같은 계열 결함이 더 나올 수 있다(미수행).

## 출처

- US20220315802A1 (Entegris / University of Florida), Table 1 — SiC CMP, α-alumina
  나노입자 0.1~5 wt%, 4 wt% KMnO4 + 0.5 wt% 질산염, pH 2.3.
- Gong J., Wang W., Liu W., Song Z., "Polishing Mechanism of CMP 4H-SiC Crystal
  Substrate (0001) Si Surface Based on an Alumina (Al2O3) Abrasive", Materials
  17(3) 679 (2024), doi:10.3390/ma17030679 (MDPI CC-BY), Table 1·Table 2.
- CRC Handbook of Chemistry and Physics — α-Al2O3 밀도 3.95 g/cm³.
- 선행 진단: knowledge/cmp/sic-alumina-kmno4-L25-heldout-diagnosis.md
- 선례 판정: EVIDENCE-RULES.md 판정#34(has_own 우선)·#48(부모 농도 상속)·
  #50/#56(KMnO4 종 게이트·종결)·#52(근거와 파라미터 팩 분리)

```python verify
# 판정#59 — 수정이 실제로 적용돼 있고, 5팩이 불변인지 기계로 확인한다.
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2])
                if "__file__" in dir() else ".")
from sim.params import load_pack
import sim.engine as E
from sim import factors

pk = load_pack("sic_alumina_kmno4")
# 1) 연마입자 정체성이 자기선언돼 있다
assert pk.has_own("abrasive"), "abrasive 가 여전히 상속 상태다"
assert str(pk.get("abrasive")) == "alumina", pk.get("abrasive")

# 2) 이 팩에서 세리아 화학항이 사라졌다
rr = E.Recipe(pack="sic_alumina_kmno4", pressure_psi=4.0, rpm_platen=90,
              rpm_wafer=100, time_s=3600).resolve()
chi = factors._f_chi(rr)
assert "ceria_tooth" not in chi.terms, chi.terms
# 3) 실리카 정점 곡선으로 조용히 떨어지지도 않는다
assert "ph_peak" not in chi.terms, chi.terms
# 4) 막힌 이유가 notes 에 남는다 / 남의 재료 곡선이 켜지지 않는다
#    ⚠ 2026-09-19 갱신 2회: (a) 판정#61 이 SiC×산성 KMnO4 전용 pH 항을 신설하며
#    판정#59 문구를 담던 폴백 note 가 교체됐고, (b) 같은 날 χ 회차가 Gong 2024 로
#    KMnO4 Langmuir K 를 **자기선언**해 산화제 항이 정당하게 켜졌다.
#    고정할 계약은 문구 리터럴도 "산화제 무반응"도 아니다 — 둘 다 당시의 증상일
#    뿐이었다. 계약은 **남의 재료/종의 곡선이 켜지지 않는다** 이므로 그렇게 쓴다.
assert chi.notes, "막힌 이유가 하나도 신고되지 않았다"
# 산화제 항이 서 있다면 그 K 는 반드시 이 팩의 자기선언이어야 한다(부모 H2O2 금지)
if "oxidizer" in chi.terms:
    assert pk.has_own("oxidizer_langmuir_K"), "부모(H2O2)의 K 를 물려받아 켜졌다"
    assert str(pk.get("oxidizer_langmuir_species")) == str(pk.get("oxidizer")), (
        pk.get("oxidizer_langmuir_species"), pk.get("oxidizer"))
else:
    assert any("oxidizer_langmuir_K" in n for n in chi.notes), chi.notes
# 이 팩 전용 pH 항(판정#61)이 세리아/실리카 것이 아닌 자기 것으로 서 있다
assert "ph_sic_kmno4_acidic" in chi.terms, chi.terms

# 5) 나머지 5팩의 분기 선택은 불변
EXPECTED = {
    "cu_h2o2_bta":    {"oxidizer", "ph_cu_acidic"},
    "oxide_silica":   {"ph_peak"},
    "sic_ceria_h2o2": {"oxidizer", "ceria_tooth", "ph_softening"},
    "sti_ceria":      {"ceria_tooth", "ph_ceria_window"},
    "w_fe_oxidizer":  {"oxidizer", "ph_w_acidic"},
}
for p, exp in EXPECTED.items():
    r = E.Recipe(pack=p, pressure_psi=4.0, rpm_platen=90,
                 rpm_wafer=100, time_s=3600).resolve()
    c = factors._f_chi(r)
    assert set(c.terms) == exp, (p, set(c.terms), exp)
    assert abs(float(c.value) - 1.0) < 1e-12, (p, c.value)

print("판정#59 verify: 5/5 PASS")
```

## 8. 문헌 정량 대조 — 이 수정이 데이터 방향과 맞는가

이 작업은 새 계수를 도입하지 않았으므로 "문헌값 재현"이 성립하는 대상은 **연마입자
농도축 하나**다. 그 축이 수정 전후 비트 불변이므로, 대조는 수정이 그 축의 문헌 일치를
훼손하지 않았음을 보이는 형태가 된다.

Gong 2024 L25(n=25)의 수준별 실측 평균(각 수준 n=5, 원문 μm/h → nm/min 환산값을
데이터셋 YAML 에서 직접 집계 — 아래 verify 블록이 매번 재계산한다):

| Al2O3 wt% | 실측 평균 (nm/min) | 모델 (nm/min, 다른 축 기준점 고정) |
|---|---|---|
| 1 | 11.1400 | 7.2635 |
| 2 | 9.9133 | 5.4819 |
| 3 | 10.7310 | 4.6498 |
| 4 | 11.3443 | 4.1372 |
| 5 | 11.5490 | 3.7789 |

> ⚠ **2026-09-19 부채상환 갱신(학습총괄).** 모델 열은 판정#61(Chen 2020 SiC×KMnO4
> 산성 pH 항)·판정#62(입경 5키 알루미나 자기선언)·2026-09-19 χ 산화제축 배선
> (Gong 2024 에서 `oxidizer_langmuir_K`=2.28 역산) **이후** 값으로 재측정했다.
> 이전 판(12.6684 → 6.5908)은 그 세 변경 이전 수치였고, 노트를 고치지 않아
> verify 블록이 반려 상태였다. **방향 결론은 바뀌지 않았다** — 절대 스케일만
> 내려갔고 감소율은 -47.97% 로 소수점까지 동일하다. 이유는 위 세 변경이 전부
> **농도축이 아닌 다른 축**(pH·입경·산화제)을 건드렸기 때문이다. 농도 지수
> `-0.406` 은 한 번도 바뀌지 않았고, 감소율은 그 지수만의 함수다 — 아래 verify
> 의 assert 가 그 불변성을 고정한다.

모델은 `abrasive_conc_exponent = -0.406`(US20220315802A1 Table 1, n=5 로그-로그 회귀)로
1→5 wt% 에서 **7.2635 → 3.7789 nm/min 단조 감소**(-47.97%)하는데, Gong 2024 실측 주효과는
**11.1400 → 11.5490 nm/min**(+3.67%, 2 wt% 에서 9.91 로 한 번 내려갔다 올라오는 비단조)로
사실상 평탄하다. 즉 두 문헌이 농도축에서 **방향이 어긋난다**(모델 -47.97% vs 실측 +3.67%).
이것은 이번 수정이 만든 문제가 아니라 **이전부터 있던 미해소 갭**이며, pH·산화제 축이
갭인 상태에서 농도축만으로 held-out 을 돌리면 ρ 가 끌려 내려가는 직접 원인이다.

참고로 **당시** 죽어 있던 두 축의 실측 주효과는 pH 10.73→11.55 nm/min(pH 2→5, 최저는 pH 3 의
10.02), KMnO4 8.89→11.75 nm/min(1→5 wt%, 단조 증가)로, **산화제축이 가장 큰 변화폭
(2.86 nm/min)** 을 보인다 — 원문(doi:10.3390/ma17030679 Table 3) 극차분석 순위(산화제 > pH > 연마입자)와 일치한다.
모델이 이 축에 전혀 반응하지 않는다는 사실의 비용이 얼마인지가 이 숫자였다.

> ✅ **그 두 축은 그 뒤 배선됐다**(2026-09-19 기준): pH 축은 판정#61(Chen 2020,
> `_ph_sic_kmno4_acidic_term`), 산화제 축은 2026-09-19 χ 회차(Gong 2024 Table 2 의
> KMnO4 주효과 5점에서 `oxidizer_langmuir_K`=2.28 역산, 종 게이트를 자기선언으로 통과).
> **그 대가로 이 데이터셋은 held-out 자격을 잃었다** — 같은 표가 계수의 출처가 됐으므로
> `used_for_calibration: false → true` 로 뒤집었다(자기 답안지 채점 방지, QA F4).
> 따라서 이 팩의 독립 검증은 현재 **0건**이고, 그것이 다음 회차의 문헌 발주 대상이다.
> 남아 있는 갭은 여전히 **농도축의 방향 불일치** 하나다(아래 §8 결론 불변).

**여기서 계수를 바꾸지 않는다.** 판정#36·#37 이 이미 같은 축을 두 차례 판정했고
(Mohs 6 문턱 레짐 분리 / 관측범위가 실사용점을 포함하는가), Gong 2024 는 알루미나
500 nm 고정·pH 와 산화제가 **동시에 변하는** L25 직교표라 농도 주효과가 다른 두 축의
교란을 포함한다 — 단독 스윕이 아니다. `-0.406` 의 출처(Entegris Table 1)는 pH·산화제
고정 단독 스윕이므로 **교란 통제 측면에서 상위**다(EVIDENCE-RULES: 등급이 같으면
교란통제로 깬다). 방향 충돌은 **기록만 하고 값은 유지**한다.

- 이 대조의 한계는 **미검증**이다: 위 "실측 평균"은 Table 2 의 25행을 수준별로 묶어
  산술평균한 값이고, 원문이 그 평균을 인쇄한 것이 아니다. 원문 Table 3 의 극차분석
  k 값이 정본이며, 그 표는 본문 서술(최적 pH=4)과 자체 불일치(k 최대는 pH=5)를
  갖는다 — 데이터셋 YAML 주석에 이미 기록된 사안이다.
- 모델 열의 **절대 스케일은 실측과 비교할 수 없다**(Kp 가 Wang 2021 조건에서
  역산됐고 그 Kp 자체가 원문 미확보 2차 인용이다 — 팩 yaml 이 자백하고 있다).
  위 표는 **기울기 방향 대조용**이다.

```python verify
# §8 의 표가 데이터셋·모델에서 실제로 나오는 값인지 매번 재계산한다.
import collections, statistics, yaml
import sim.engine as E
import numpy as np

d = yaml.safe_load(open("validation/datasets/gong2024_4hsic_alumina_kmno4_L25.yaml"))
assert len(d["conditions"]) == 25, len(d["conditions"])

g = collections.defaultdict(list)
for c in d["conditions"]:
    g[c["overrides"]["abrasive_wt_pct"]].append(c["mrr_nm_per_min"])
meas = {k: statistics.mean(v) for k, v in g.items()}
for k, v in g.items():
    assert len(v) == 5, (k, len(v))          # L25 균형 배치
EXP = {1: 11.1400, 2: 9.9133, 3: 10.7310, 4: 11.3443, 5: 11.5490}
for k, v in EXP.items():
    assert abs(meas[k] - v) < 5e-4, (k, meas[k], v)

def model(ab):
    r = E.Recipe(pack="sic_alumina_kmno4", pressure_psi=4.0, rpm_platen=90,
                 rpm_wafer=100, time_s=3600,
                 pack_overrides={"slurry_ph": 5, "oxidizer_wt_pct": 2,
                                 "abrasive_wt_pct": ab, "abrasive_size_nm": 500})
    return float(np.mean(E.simulate(r).mrr_nm_per_min))

MOD = {1: 7.2635, 2: 5.4819, 3: 4.6498, 4: 4.1372, 5: 3.7789}
for k, v in MOD.items():
    assert abs(model(k) - v) < 5e-4, (k, model(k), v)

# 절대 스케일은 다른 축(pH·입경·산화제)이 배선될 때마다 움직인다 — 이 노트의
# 주장은 절대값이 아니라 **농도축 기울기**이므로 그것을 따로 고정한다.
# 감소율 -47.97% 는 abrasive_conc_exponent(-0.406) 하나의 함수이고,
# 다른 축 배선으로는 절대 변하지 않아야 한다(변했다면 축이 섞인 것이다).
_slope = (MOD[5] - MOD[1]) / MOD[1] * 100
assert abs(_slope - (-47.97)) < 0.02, ("농도축 기울기가 바뀌었다", _slope)

# 핵심 주장: 방향이 어긋난다 (모델 단조 감소 vs 실측 순증)
assert MOD[5] < MOD[1], "모델 농도축이 단조 감소가 아니다"
assert meas[5] > meas[1], "실측 농도축이 순증이 아니다"
d_mod = (MOD[5] - MOD[1]) / MOD[1] * 100
d_mea = (meas[5] - meas[1]) / meas[1] * 100
assert abs(d_mod - (-47.97)) < 0.02, d_mod
assert abs(d_mea - 3.67) < 0.02, d_mea

print("§8 정량 대조: 모델 %.1f%% vs 실측 %+.1f%% — 방향 불일치 확인" % (d_mod, d_mea))
```

## 9. 이 노트에서 확인하지 못한 것 (정직성 표지)

- **알루미나/KMnO4 산성계의 pH 의존 폐형식은 확보하지 못했다.** Gong 2024 의 극차분석
  k 값은 있으나 앞서 적은 본문-표 불일치 때문에 계수로 전용할 수 없다고 **판단**한
  것이며, 이 판단 자체가 1차 문헌의 지지를 받는 것은 아니다(미검증).
- **`abrasive` 외의 정체성 키(`film`·`oxidizer`·`pad_*`)에 같은 상속 결함이 있는지는
  확인하지 못했다.** 이번 감사 범위는 `abrasive` 하나다(§7-3).
- **수정 후 절대 MRR 8.11 nm/min 가 이 계의 참값에 더 가까운지는 미검증이다.**
  확인된 것은 "세리아 항이 부당하게 켜져 있었다"는 것뿐이고, 항을 뗀 결과가 우연히
  실측(Gong 평균 약 11 nm/min)에 더 가까워졌으나 이는 **근거가 아니라 관찰**이다 —
  `kp_m_per_pa` 가 별개 문헌(Wang 2021, 2차 인용)에서 역산된 값이라 두 숫자가
  같은 기준에 있지 않다. 이 우연한 근접을 모델 타당성의 증거로 쓰지 않는다.
- **Gong 2024 원문 PDF 는 로컬 코퍼스 전문 XML 로만 확인했다**(데이터셋 YAML 의
  read_method: table). 그림은 보지 않았다.
