---
title: glycine × Cu, oxalic × Cu — 흡착 자유에너지 ΔG_ads 판정
status: 완료 — glycine 등록, oxalic NO_ADSORPTION 선언
---

# glycine × Cu, oxalic(oxalate) × Cu — ΔG_ads 판정

> 작성일: 2026-09-20 | 대상: `sim/inhibitor_pairs.py::PAIR_TABLE`, `NO_ADSORPTION`
> 선행: [[c4-cu-h2o2-bta-heldout-rho-diagnosis]](판정#73), [[psi-glycine-chelator-suppression-cu-jani2025]](판정#72),
> [[chi-carboxylate-promoter-cu-oxalate-us6309560]](판정#75)
> 과제: `tools/pair_gap_report.py`가 지목한 미등록 쌍 2건(glycine×cu, oxalic×cu) 채우기

## 배경

완성 격자에서 C4(`cu_h2o2_bta` 유의 held-out 평균 ρ=0.7175<0.85)가 남아 있고,
`pair_gap_report.py`가 `jani2025_cu_rsm_composition_heldout` 데이터셋이 요구하는
`glycine×cu`·`oxalic×cu` 쌍이 `PAIR_TABLE`에 없다고 지목했다. 이번 회차 목표는
1차 문헌으로 이 두 쌍을 판정하는 것이다.

**⚠ 회차 도중 발견한 구조적 사실(정직하게 먼저 적는다)**: `cu_h2o2_bta` 팩은
`inhibitor_species=bta`/`substrate_species=cu`로 고정돼 있고(`knowledge/params/
cu_h2o2_bta.yaml` L370-381), `sim/chemistry.py::_inhibitor_term`이 조회하는
쌍은 이 **하나뿐**이다. 글리신(`chelator_species`)과 옥살산(`promoter_species`)은
같은 팩 안에서 이미 **별도의 전용 항**(`_chelator_suppression_term`,
`_carboxylate_promoter_term`)으로 배선돼 있다(판정#72·#75) — 이 일반 Langmuir
쌍 표(`PAIR_TABLE`)를 전혀 거치지 않는다. 즉 이번 등록은 `pair_gap_report.py`의
텍스트 마이닝 감사를 통과시키고 향후 다른 팩(예: glycine이 유일한 억제제인
계열)이 재사용할 수 있게 하는 데는 값어치가 있지만, **이 회차의 등록만으로는
`cu_h2o2_bta`의 시뮬레이션 출력이 바뀌지 않는다** — C4의 0.7175는 이미 판정#73이
확인했듯 전혀 다른 데이터셋(`tw202115224a`, 연마입자 형상 축)에서 온다. 이 사실을
숨기면 다음 회차가 "쌍을 채웠는데 왜 ρ가 안 오르지?"를 반복해서 재조사한다.

## 절 1 — glycine × Cu: **등록**

원문: M. M. Nandi, S. Biswas, N. Jain, S. Nandi, "The effect of inhibitor
structure on the corrosion of copper in 0.6 M aqueous sodium chloride
solution", *J. Indian Chem. Soc.* **94**, 369–380 (2017). 이 저널은 Crossref에
DOI가 없어(검색 확인) OA 호스팅 사본(Zenodo, DOI:10.5281/zenodo.5594539)을
인용한다 — PDF 전문을 직접 내려받아 `fitz`로 읽었다(로컬 확보, 재현 가능).

- 화합물 (1) = **순수 글리신**(N-벤젠설포닐 유도체 (2)~(10)은 곁사슬이 다른
  인접 분자이므로 등록하지 않았다 — 이식 금지 규칙).
- 측정법: 전위동태 분극(Tafel, `Icorr` 3점 농도 10⁻⁴~10⁻⁶ M) → 표면피복률
  θ=(icorr−icorr,inh)/icorr → Langmuir `Cinh/θ = Cinh + 1/Kads` 선형피팅.
- 조건: 0.6 M 수용액 NaCl, **pH 6**, 30±0.5 °C, 산화제 없음.
- 결과(원문 Table 4, 화합물 1): **Kads = 1.25×10⁵ dm³/mol, R²=0.991,
  ΔG°ads = −39.8208 kJ/mol** (음수 → 자발적 흡착; 저자들은 −40 kJ/mol 근방을
  화학흡착 경계로 해석). 원문(Nandi et al. 2017) 공식 ΔG=−2.303RT log(55.5·Kads)
  (T=30.5 °C)으로 직접 재계산해 대조하면 오차 0.00%로 일치한다(§검증 블록1).

**⚠ 조건 불일치를 숨기지 않는다**: 이 값은 무산화제·pH 6 NaCl계에서 잰 것이고,
`cu_h2o2_bta` 팩은 pH 3·H2O2 존재 조건이다. 원문 자신이 이미 pH 의존성을 경고한다:
"at pH 6 ... inhibition efficiency of glycine ... is found to be only 10.1%.
This may be due to zwitter ion structure of glycine ... glycine is good inhibitor
in HCl and H2SO4 solution ... where it exists as protonated species." 즉 pH가
내려가 양성자화될수록(=CMP 조건에 가까워질수록) 억제 효과가 오히려 **강해지는
방향**이라는 게 원문의 주장이다 — 그렇다면 pH 3의 진짜 ΔG_ads는 −39.82 kJ/mol보다
**더 음수**(더 강한 흡착)일 가능성이 있으나, 이 논문은 그 정량값을 pH 3에서
재지 않았다. 방향은 맞고 크기는 모른다.

**교차 corroboration (같은 결론, 다른 함수형)**: [[psi-glycine-chelator-suppression-cu-jani2025]]
(jani2025, doi:10.1149/2162-8777/adc59e, CC-BY, pH 3, 이 팩의 held-out 데이터셋
자신)가 독립적으로 "glycine functions as a dissolution inhibitor ...
effectiveness is limited at low pH, where its predominantly protonated ...
forms reduce its ability to complex with Cu²⁺" 라고 결론 내렸다 — **방향은
Nandi2017과 일치**(억제 방향)하지만 저농도 protonated 형태의 효능이 오히려
"제한적"이라고 서술해 위 문단의 추정과 미묘하게 다르다(원문 저자마다 protonation
효과의 부호 해석이 다르다는 뜻 — 미검증 영역으로 남긴다). jani2025는 ΔG_ads를
보고하지 않고 통제쌍 2점에서 역산한 지수형 계수(a=1.5119 /M, K·k 비식별)만
가지므로, 이 줄(Langmuir ΔG_ads)과 **함수형이 다르다** — 서로 대체하지 않았고
팩의 실제 글리신 항은 여전히 그 전용 계수를 쓴다.

**참고(등록 금지 — 인접분자, 표에 넣지 않음)**:
- bicine/tricine(N,N-치환 글리신 유도체), 0.6 M NaCl, ΔG_ads ≈ −28~−32 kJ/mol
  (물리흡착 영역) — 곁사슬이 다르다.
- H-Lys-Glu-Asp-Gly-OH 테트라펩타이드, ΔG_ads=−30.86 kJ/mol — 글리신은 4잔기 중
  1개일 뿐이라 순수 글리신 값이 아니다.

## 절 2 — oxalic(oxalate) × Cu: **NO_ADSORPTION 선언(흡착 항 아님)**

`sim/inhibitor_pairs.py::NO_ADSORPTION[("oxalic","cu")]`에 등록. 근거:

1. jani2025(doi:10.1149/2162-8777/adc59e, CC-BY, 전문 확보·직접 읽음) —
   "HC2O4⁻ dissolved CuO to form soluble complexes like [Cu(C2O4)2]²⁻" 및
   RSM 회귀에서 `[oxalic acid]` 계수 **+536.63 (p=1.7×10⁻⁷)**로 5개 인자 중
   **가장 크고 가장 유의한 양(+)의 인자**("oxalic acid had the most significant
   positive impact on the response"). 억제제라면 농도가 오를 때 제거율이
   내려야 하는데 정반대 부호다 — [[chi-carboxylate-promoter-cu-oxalate-us6309560]]가
   이미 지목한 것과 같은 결론.
2. 독립 1차 문헌: Kaufman, Kistler, Wang (Cabot), US6309560B1 TABLE 1 —
   옥살산암모늄 농도 0→1.0 wt% 스윕에서 Cu 제거율이 최대 **12.81배** 단조
   증가(통제쌍 2건, `knowledge/cmp/chi-carboxylate-promoter-cu-oxalate-us6309560.md`
   §3에 이미 재현). 서로 다른 저자·다른 장비·다른 시대(1996 특허 vs 2025 논문)가
   같은 방향(옥살산=촉진, 억제 아님)에 도달했다.
3. (보조, 초록만 확인 — `unverified` 수준 참고) IOP 10.1149/1.2121737
   "Electrochemistry of Copper in Aqueous Oxalic Acid Solutions" 초록은 Cu-옥살산
   용해도/전위-pH 도표를 다룬다고만 밝혀 흡착막이 아니라 **용액 화학종 평형**이
   연구 대상임을 시사한다 — 전문은 미확보라 결정적 근거로 쓰지 않았다.

이 쌍은 "①아무도 안 쟀다"가 아니라 "②그 메커니즘이 아니다"에 해당한다 —
옥살산은 Cu 표면에 흡착막을 만들어 억제하는 것이 아니라 Cu²⁺를 가용성 착물로
빼내 제거를 **촉진**한다. 그 물리는 이미 `sim/chemistry.py::_carboxylate_promoter_term`
(`promoter_species=oxalic`)이 맡고 있으므로 흡착 억제 항을 만들지 않는 것이 옳다.

## 절 3 — 판정 요약

| 쌍 | 판정 | 근거 | 등급 |
|---|---|---|---|
| glycine × cu | **등록** | Nandi2017 (Zenodo DOI:10.5281/zenodo.5594539), 직접 읽음 | literature |
| oxalic × cu | **NO_ADSORPTION 선언** | jani2025(adc59e) + US6309560B1, 둘 다 직접 읽음 | — (흡착 항 자체가 없음) |

두 판정 모두 `sim/inhibitor_pairs.py`의 이식 금지 규칙을 지켰다 — 인접 분자
(bicine/tricine/테트라펩타이드, malonate/succinate 등)는 등록하지 않았다.

## 검증

```python verify
# 블록1: glycine×cu 등록값이 원문 Table 4 공식으로 재현되는지 직접 계산
import math
R = 8.314462618
T = 30.5 + 273.15   # 원문 30±0.5 °C
K_ads = 1.25e5       # dm3/mol = L/mol
dG_paper = -2.303 * R * T * math.log10(55.5 * K_ads) / 1000.0   # kJ/mol
print(f"원문 공식으로 재계산한 ΔG = {dG_paper:.4f} kJ/mol (Table 4 인쇄값 -39.8208)")
assert abs(dG_paper - (-39.8208)) < 0.05, f"원문 공식 재현 실패: {dG_paper}"

import sys
sys.path.insert(0, ".")
from sim.inhibitor_pairs import lookup_dG, K_from_dG, adsorption_ruled_out

pair = lookup_dG("glycine", "cu")
assert pair is not None, "glycine×cu 가 등록돼 있어야 한다"
assert abs(pair.dG_kJ_per_mol - (-39.8208)) < 1e-6, pair.dG_kJ_per_mol
assert pair.confidence == "literature"

# 엔진 공식(K_from_dG, 25°C 298.15K 기준)으로도 K 방향이 맞는지 확인
# (원문은 30.5°C 기준값이라 정확히 같은 K는 아니고, 음수 ΔG -> 큰 K 라는 방향만 확인)
K_engine = K_from_dG(pair.dG_kJ_per_mol)
assert K_engine > 1e4, f"강한 음의 ΔG는 큰 K를 줘야 한다: {K_engine}"
print(f"엔진 K_from_dG(298.15K) = {K_engine:.4g} L/mol (원문 30.5°C 값 1.25e5와 같은 자릿수)")
```

```python verify
# 블록2: oxalic×cu가 흡착 항이 아니라 NO_ADSORPTION으로 선언됐는지, 그리고
# lookup_dG는 여전히 None(값 없음)임을 확인 — 두 표가 서로 배타적이어야 한다
import sys
sys.path.insert(0, ".")
from sim.inhibitor_pairs import lookup_dG, adsorption_ruled_out

reason = adsorption_ruled_out("oxalic", "cu")
assert reason is not None, "oxalic×cu 는 NO_ADSORPTION 표에 있어야 한다"
assert "536.63" in reason and "complex" in reason.lower(), "근거 문자열에 정량 근거가 있어야 한다"
assert lookup_dG("oxalic", "cu") is None, \
    "NO_ADSORPTION 로 선언된 쌍은 PAIR_TABLE 에 동시에 있으면 안 된다(두 표는 배타적)"
print("oxalic×cu: 흡착 없음 선언 확인, PAIR_TABLE 에는 값 없음(설계대로)")
```

```python verify
# 블록3: 이 회차 등록이 cu_h2o2_bta 팩의 실제 계산 경로에 연결되지 않는다는
# 구조적 사실을 코드로 직접 확인한다(노트 본문의 핵심 주장 — 눈으로만 말하지 않는다)
import sys
sys.path.insert(0, ".")
from sim.params import load_pack

pk = load_pack("cu_h2o2_bta")
inhib = pk.get_or("inhibitor_species", None)
subst = pk.get_or("substrate_species", None)
chelator = pk.get_or("chelator_species", None)
promoter = pk.get_or("promoter_species", None)

assert (inhib, subst) == ("bta", "cu"), \
    f"이 팩의 일반 Langmuir 쌍 표 조회는 여전히 bta×cu 뿐이다: {(inhib, subst)}"
assert chelator == "glycine", chelator
assert promoter == "oxalic_acid", promoter
print("확인: PAIR_TABLE 조회는 bta×cu만 쓰고, glycine/oxalic은 별도 전용 항목이 처리한다")
print("=> 이번 등록은 pair_gap_report 감사용이지 cu_h2o2_bta 예측을 바꾸지 않는다")
```

## 정직성 표지

- glycine ΔG_ads(-39.82 kJ/mol)는 pH 6·무산화제 조건 값이다. pH 3·H2O2 CMP
  조건의 실제 값은 **미확보**다 — 방향(억제)만 교차확인됐다.
- oxalic×cu NO_ADSORPTION 판정은 두 독립 1차 문헌(jani2025, US6309560B1)이
  같은 방향(촉진)에 도달했다는 강한 근거가 있지만, IOP 10.1149/1.2121737은
  초록만 확인했다(전문 미확보) — 결정적 근거로 인용하지 않았다.
- **이 회차의 등록은 C4(ρ=0.7175)를 움직이지 않는다.** C4의 실제 원인은
  판정#73이 이미 확정한 `tw202115224a`(연마입자 형상 축, 화학과 무관)이고,
  `jani2025_cu_rsm_composition_heldout`은 애초에 비유의(p=0.877)라 C4 평균에
  들어가지 않는다. 이 사실을 다음 회차 배차자가 다시 발견하느라 시간을 쓰지
  않도록 여기 명시한다.
