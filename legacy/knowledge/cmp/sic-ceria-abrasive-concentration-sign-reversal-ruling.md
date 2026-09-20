# SiC 팩의 연마입자 농도 지수 — 부호 역전 판정 (판정#52)

작성: 2026-09-16 · 담당: 정확도루프(성장엔진) · 대상 팩: `sic_ceria_h2o2`, `sic_alumina_kmno4`

## 1. 무엇이 문제였나

`knowledge/params/sic_ceria_h2o2.yaml` 의 `abrasive_conc_exponent` 는 **-0.406**
(농도↑ → MRR↓)이었다. 그 값의 근거는 Entegris/U.Florida 특허
**US20220315802A1 Table 1**(산성 pH 2.3 · KMnO4 4 wt% · 알루미나 나노입자
0.1~5 wt%, n=5)의 로그-로그 회귀다.

그런데 **그 데이터셋은 2026-09-16 판정#49-B 로 이미 이 팩을 떠나
`sic_alumina_kmno4` 팩으로 옮겨져 있었다**(절대 MRR 이 130배 갈려 레짐 분리).
근거는 자식 팩으로 가고 지수만 부모에 남은 **고아 파라미터** 상태였다.

## 2. 이 팩의 계에서 실제로 관측되는 방향

`sic_ceria_h2o2` 의 계는 **4H-SiC + H2O2 + 세리아 함유 연마입자 + 알칼리~중성**이다.
그 계에서 조성-MRR 이 인쇄된 1차 문헌 네 건은 **모두 비음(非負)** 방향이다.

| # | 문헌 | 계 | 농도 구간 | 관측 | 등급 |
|---|------|-----|-----------|------|------|
| 1 | Wang et al., figshare:31056549 (ACS SI Table S3) | 4H-SiC, CeO2/H2O2, pH 9~11 | 2/4/6 wt% | 매칭쌍 17개 로그-로그 기울기 중앙값 **+0.227** | E1(교란 통제 실측) |
| 2 | Liang et al., Nano Research 2026, doi:10.26599/NR.2026.94909100 §2.3 | 4H-SiC, CuxO-CeO2/Al2O3 + H2O2 8 wt%, pH 7 | 1/5/9 wt% | 228.54 → 538.45 → 621.47 nm/h **단조 증가**(OLS +0.472) | E3(실측, 촉매 교란) |
| 3 | Wei et al. 2026, doi:10.3390/cryst16030179 §3.2 | 4H-SiC C면, 콜로이달 실리카 110 nm + H2O2 5 wt% + Fe3O4, pH 9 | 2→8 wt% | 단조 증가, 8 wt% 최대 701 nm/h (>8 wt% 는 점도·응집으로 감쇠) | E3 |
| 4 | Gong et al. 2024, doi:10.3390/ma17030679 Table 2 (L25) | 4H-SiC, 알루미나/KMnO4, pH 2~6 | 1~5 wt% | +0.036 (95% CI -0.037~+0.142) | E3(타계, 참고) |

#1 은 **산화제·pH·압력·rpm 이 전부 같고 CeO2 농도만 다른 쌍**만 골라낸 것이라
이 표에서 교란이 가장 잘 통제돼 있다. 그래서 채택값은 #1 의 +0.227 이다.

#2 는 이번 회차에 새로 확보한 **held-out**(`validation/datasets/liang2026_4hsic_ceria_composite_h2o2_conc.yaml`)
이므로 적합에 쓰지 않았다 — 방향 확인 전용이다.

## 3. 이론 유도와의 정합

`sim/regime_adapter.py` 의 3인자 분해(χ·α·공급형태)가 이 팩에서 주는 값은

    n_C = p(1 - αχ) = 1 × (1 - 0.667 × 1.00) = +0.333   (표면적 지배 극한)

이다. 채택값 +0.227 은 **부호가 같고 자릿수도 같다**. 실측이 이론보다 다소 낮은
것은 고농도 포화(순수 거듭제곱이 구조적으로 표현 못 하는 영역) 때문으로 읽힌다.
이전 값 -0.406 은 이론 유도와 **부호부터 반대**였고, 어댑터는 "팩 선언값이
literature 등급이라 이론값을 이긴다"는 이유로 그 음수를 계속 채택하고 있었다.

## 4. 판정 (EVIDENCE-RULES)

- 두 관측군(알칼리 세리아/H2O2 계 vs 산성 KMnO4/알루미나 계)은 **평균내지 않는다.**
  "둘 다 맞되 레짐이 다르다" 로 판정하고 **팩별로 분기**한다.
  - `sic_ceria_h2o2` → **+0.227** (literature)
  - `sic_alumina_kmno4` → **-0.406** (literature, 근거 특허와 같은 팩으로 이동)
- 레짐 경계의 근거는 특허 원문 자신이다: US20220315802A1 [0043]/[0057] 이
  Mohs<6(나노 산화물)과 alpha-alumina 계열을 별개 거동으로 명시한다(판정#36에서 확인).
- 과거 **판정#37**(Table 1 유지 재확정)은 "Entegris 데이터가 `sic_ceria_h2o2` 의
  것"이라는 전제 위에 있었고 판정#49-B 로 그 전제가 사라졌다 — 함께 종결한다.
- **미결정으로 남는 것**: +0.227 의 부트스트랩 95% CI 는 -0.136~+0.598 로 0 을
  포함한다. **부호만 판정됐고 크기는 미결정**이다. 그래서 등급은 measured 가
  아니라 literature 다.
- 마이크론급 백강옥 알루미나의 비단조(su2011, 판정#36)는 여전히 별개 레짐이다.

## 5. 정량 재현

```python verify
import math, statistics, itertools, random, yaml, pathlib

# ── (1) Wang DOE 매칭쌍 재분석: 채택값 +0.227 이 데이터에서 실제로 나오는가 ──
d = yaml.safe_load(open(pathlib.Path("validation/datasets/sic2026_ceria_h2o2_ph_DOE50.yaml")))
conds = d["conditions"]
assert len(conds) == 50, len(conds)

from collections import defaultdict
groups = defaultdict(list)
for c in conds:
    o = c["overrides"]
    key = (o["oxidizer_wt_pct"], o["slurry_ph"], c["pressure_psi"], c["rpm_platen"], c["rpm_wafer"])
    groups[key].append((o["abrasive_wt_pct"], c["mrr_nm_per_min"]))

slopes = []
for v in groups.values():
    for (a1, m1), (a2, m2) in itertools.combinations(sorted(v), 2):
        if a1 != a2:
            slopes.append(math.log(m2 / m1) / math.log(a2 / a1))

assert len(slopes) == 17, len(slopes)
med = statistics.median(slopes)
assert abs(med - 0.227) < 0.002, med          # 노트 §2 의 +0.227
assert med > 0, "이 계의 농도 지수는 양수다 — 부호 판정의 핵심"

random.seed(0)
bs = sorted(statistics.median(random.choices(slopes, k=len(slopes))) for _ in range(2000))
lo, hi = bs[50], bs[1950]
assert lo < 0 < hi, (lo, hi)                   # §4: CI 가 0 을 포함 = 크기 미결정
assert abs(lo - (-0.136)) < 0.02 and abs(hi - 0.598) < 0.02, (lo, hi)

# ── (2) Liang 2026 held-out: 방향이 단조 증가인가 (원문 인쇄값) ──
liang = [(1.0, 228.54), (5.0, 538.45), (9.0, 621.47)]   # wt%, nm/h  §2.3
assert all(liang[i][1] < liang[i + 1][1] for i in range(len(liang) - 1)), "단조 증가"
xs = [math.log(c) for c, _ in liang]; ys = [math.log(m) for _, m in liang]
mx, my = statistics.mean(xs), statistics.mean(ys)
ols = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sum((x - mx) ** 2 for x in xs)
assert abs(ols - 0.472) < 0.005, ols
assert ols > 0

# ── (3) 두 팩이 실제로 분기됐는가 (레짐 분리가 코드에 반영됐는지) ──
from sim.params import load_pack
ceria = load_pack("sic_ceria_h2o2")
alumina = load_pack("sic_alumina_kmno4")
n_ceria = float(ceria.get("abrasive_conc_exponent"))
n_alum = float(alumina.get("abrasive_conc_exponent"))
assert abs(n_ceria - 0.227) < 1e-9, n_ceria
assert abs(n_alum - (-0.406)) < 1e-9, n_alum
assert n_ceria * n_alum < 0, "부호가 갈려야 레짐 분리다"

# ── (4) 이론 유도값과 부호 일치 ──
from sim.regime_adapter import exponents_for
ex = exponents_for(ceria, 4.3511)
assert ex["regime"].p * (1 - ex["regime"].alpha * ex["regime"].chi) > 0
print("OK  Wang median=%.4f (CI %.3f~%.3f) · Liang OLS=%.4f · packs %+.3f / %+.3f"
      % (med, lo, hi, ols, n_ceria, n_alum))
```

## 5-1. 정량 대조 (문헌값 vs 재현값)

| 항목 | 문헌값(원문 인쇄) | 재현값(위 verify 실행) | 차이 |
|------|------------------|----------------------|------|
| Liang 2026 §2.3, 연마입자 1 wt% | 228.54 nm/h | 228.54 nm/h (데이터셋 전재) | 0 % |
| Liang 2026 §2.3, 5 wt% | 538.45 nm/h | 538.45 nm/h | 0 % |
| Liang 2026 §2.3, 9 wt% | 621.47 nm/h | 621.47 nm/h | 0 % |
| Wei 2026 §3.2 최대 MRR(8 wt%) | 701 nm/h | — (방향만 인용, 값 대조 안 함) | 미검증 |
| Wang DOE 매칭쌍 기울기 | (원문에 없음 — 우리가 계산) | **+0.2271** (n=17) | — |
| 이론 유도 n_C | +0.333 (3인자 분해) | +0.333 | 부호 일치, 크기 32 % 낮음 |
| su2011 MAPE(백테스트) | 실측 45.0/69.5/56.2 nm/h | 예측 오차 64.1 % → **13.0 %** | 51 %p 개선 |

⚠ **미검증으로 남기는 것**: Wei 2026 과 Gong 2024 의 값은 방향 확인용으로만
인용했고 우리 엔진으로 절대값을 재현하지 않았다. Liang 2026 의 pH(=7) 는
§2.3 문맥에서 **추정**한 것이지 Fig. 3(h)/3(i) 캡션에 명시된 값이 아니다
(순위 지표에는 영향 없음 — 4조건 전체에 같은 상수로 걸린다).
⚠ 채택값 +0.227 의 **크기는 미확정**이다(부트스트랩 CI 가 0 을 포함).

## 6. 백테스트 영향 (실행값)

`validation/backtest.py` 실행 결과, 값 교체 전후:

| 지표 | 전 | 후 |
|------|----|----|
| 유의 held-out 평균 ρ | +0.9442 (8개, 79조건) | **+0.957 (9개, 83조건)** |
| held-out 14개 전체 평균 ρ | +0.523 | **+0.723** |
| `liang2026_...`(신규 held-out, n=4) | ρ=-0.800 p=0.958 | **ρ=+1.000 p=0.042** |
| `entegris2022_...`(n=5, 자식 팩) | ρ=+1.000 p=0.008 | ρ=+1.000 p=0.008 (불변) |
| `su2011_...`(n=3) | ρ=-0.500 MAPE 64.1% | ρ=+0.500 MAPE **13.0%** |
| `sic2026_..._DOE50`(캘리브레이션, 참고) | ρ=+0.463 MAPE 45.2% | ρ=+0.688 MAPE 33.7% |

`gong2024_..._L25`(ρ=-0.190)는 **불변**이다 — 그 데이터셋은 `sic_alumina_kmno4`
팩이고 그 팩의 지수는 값이 바뀌지 않았다(부모에서 자식으로 자리만 옮겼다).
그 데이터셋의 비유의는 pH·KMnO4 두 축이 꺼져 있는 별개 갭이다(2026-09-16 앞 회차 노트).

## 7. 상호링크

- [[sic-alumina-concentration-negative-exponent-entegris]] — -0.406 의 원 회귀
- [[sic-abrasive-concentration-regime-ruling]] — 판정#36, 백강옥 레짐 분리
- [[sic-abrasive-conc-exponent-table-provenance]] — 판정#37(이 노트로 종결)
- [[sic-preston-coefficient-pack-own-declaration]] — 판정#49-B, 팩 분리
- [[abrasive-concentration-mrr-saturation-contact-probability]] — 1/3 vs 4/3 극한
- [[sic-alumina-kmno4-L25-heldout-diagnosis]] — Gong L25 held-out
