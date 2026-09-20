<!-- V2-SECTION: R2-slurry | 정확도루프 VALIDATION(held-out 확보) sic_alumina_kmno4 2026-09-16 -->
# 산성 KMnO4/알루미나 4H-SiC CMP — 독립 held-out DOE(L25) 확보와 진단

> slurry-chemist Lv3-2 확장 | 작성일: 2026-09-16
> 선행: [[sic-alumina-concentration-negative-exponent-entegris]] (같은 계 κ 농도항의 현행 출처)
> [[sic-h2o2-oxidizer-saturation-alkaline-ceria]] (부모 팩의 산화제 형상, 판정#50)
> [[sic-abrasive-concentration-regime-ruling]] (Mohs 6 레짐 경계, 판정#36)
> 스코프: slurry-chemist. 팩 `sic_alumina_kmno4`(판정#49-B 로 분리된 산성 KMnO4 레짐).

## 1. 왜 이 단원인가 — 이 팩의 유일한 데이터가 자기 출처였다

`tools/accuracy_gaps.py --next` 가 100점으로 지목한 갭은 SiC 계 held-out 부재였다.
`sic_alumina_kmno4` 가 가진 유일한 데이터셋 `entegris2022_us20220315802a1_sic_alumina_conc`
(n=5)는 **그 팩의 조성 기준점·pH 기준점·산화제 종·농도 기준점을 전부 거기서 가져온**
데이터다(파일의 `calibration_contact` 9항목이 그 사실을 스스로 신고하고 있다).
ρ=+1.000 이 나오지만 순환 보정이라 근거로 쓸 수 없다 — 판정#33이 이미 "통과의 근거는
약하다"고 기록해 둔 상태였다.

## 2. 확보한 1차 출처

**Gong J., Wang W., Liu W., Song Z., "Polishing Mechanism of CMP 4H-SiC Crystal
Substrate (0001) Si Surface Based on an Alumina (Al2O3) Abrasive", Materials 17(3)
679 (2024), DOI 10.3390/ma17030679** (MDPI, CC-BY 오픈액세스).

- 확보 경로: 로컬 코퍼스 전문 XML(JATS) `data/corpus/fulltext/doi_10.3390_ma17030679.xml`
  의 `<table-wrap>` Table 2 를 파싱. MDPI PDF 엔드포인트는 2026-09-16 봇 차단(413 B HTML
  반환)으로 직접 내려받지 못했고, 텍스트 전문을
  `papers/gong2024-ma17030679-4hsic-alumina-kmno4-L25.txt` 로 등록했다(INDEX.json 등록 완료).
- 재료계: 2인치 4H-SiC (0001) Si면, α-Al2O3 500 nm, 산화제 과망간산염(KMnO4),
  pH 는 HNO3/KOH 조정, Suba 800 패드, 4 psi, 헤드 100 rpm / 플래튼 90 rpm, 90 mL/min, 60 min.
  → `sic_alumina_kmno4` 팩(산성·KMnO4·알루미나)과 레짐 일치.
- 설계: **L25(5수준 3인자) 직교표** — pH 2~6 × KMnO4 1~5 wt% × Al2O3 1~5 wt%, n=25.
  각 수준이 5회 반복되고 세 인자가 균형 배치된다(주효과 교란 없음).
- `validation/datasets/gong2024_4hsic_alumina_kmno4_L25.yaml` 로 등록,
  `used_for_calibration: false`(어떤 팩 파라미터도 이 논문에서 뽑지 않았다).
  `qa_loop.py audit` 결과 **clean**(F1/F3 플래그 없음, 원문미확인 0/25).

## 3. 백테스트 결과 — 통과가 아니라 진단이다

실행: `.venv/bin/python validation/backtest.py`

```
gong2024_4hsic_alumina_kmno4_L25   n=25  ρ=-0.190  τ=-0.157  p=0.817  MAPE=28.5%
```

**비유의**다. 그런데 원인이 n 부족이 아니다(n=25 는 이 저장소에서 두 번째로 큰 DOE).
조건별 예측을 직접 찍어 보면 원인이 즉시 드러난다 — **예측값이 5개 값만 갖는다.**
(11.747 / 8.865 / 7.520 / 6.691 / 6.111 nm/min, 각각 Al2O3 1/2/3/4/5 wt%)

즉 pH 5수준과 KMnO4 5수준이 예측에 **전혀 반영되지 않는다**. 이유는 둘 다 알려진 구조다:

- **KMnO4 축**: 판정#50이 종 게이트(`_oxidizer_species_gate_ok`)를 세워 부모 팩의
  H2O2 Langmuir 곡선 상속을 차단했다 — 의도적으로 갭으로 남긴 자리다. 이 팩에는
  KMnO4 형상 파라미터가 없으므로 `_oxidizer_term` 이 배수 1.0 으로 고정된다.
- **pH 축**: `_ph_softening_term` 이 `abrasive == 'ceria'` 일 때만 켜진다
  (판정#33 §진단). 이 팩의 연마입자는 알루미나라 꺼진다.

정량 대조(같은 조건의 문헌값 vs `sim/engine.py` 예측, 단위 nm/min. 문헌값 출처는 모두
Gong et al. 2024, doi:10.3390/ma17030679 Table 2, 예측은 `validation/backtest.py` 실행값):
T2-01(pH2·KMnO4 1wt%·Al2O3 1wt%) 문헌값 8.69 대 예측 11.75(+35%),
T2-19(pH5·KMnO4 4wt%·Al2O3 4wt%) 문헌값 13.80 대 예측 6.69(−52%).
절대 편차는 MAPE 28.5 % 로 이 저장소 SiC 데이터셋 중 가장 작다
(entegris2022, 같은 출처 US20220315802A1 계열은 29배 과소예측) —
**그런데도 순위가 안 맞는다.** 계통 편향이 작다는 것과 인자 반응이 맞다는 것은 별개다.

원문 자신의 극차분석 R 값은 **산화제(0.1717) > pH(0.1104) > 연마입자(0.0978)** 순이다.
**우리 모델에서 죽어 있는 두 축이 실측상 1·2위 지배인자**이고, 살아 있는 유일한 축이
실측 3위(가장 약한 인자)다. ρ 가 0 근방으로 나오는 것은 모델이 "틀린 순위"를 주장해서가
아니라, 지배인자를 못 보는 상태에서 약한 인자만으로 순위를 매기기 때문이다.

## 4. 새로 도출한 지식 — 농도 지수의 계내 충돌(기록, 미종결)

같은 재료계(4H-SiC + 알루미나 + 산성 KMnO4)인데 농도-MRR 부호가 두 문헌에서 갈린다.

| 출처 | 농도 범위 | 로그-로그 지수 | 부호 |
|---|---|---|---|
| US20220315802A1 Table 1 (현행 `abrasive_conc_exponent` 출처, n=5) | 0.1~5 wt% | **−0.406** | 감소 |
| Gong 2024 Table 2 주변평균 (n=25, 수준당 5반복) | 1~5 wt% | **+0.036** | 거의 평탄(미세 증가) |

L25 다중회귀(3인자 동시)로도 확인: log(abr) 계수 **+0.0356**, 95% 부트스트랩 구간
**−0.037 ~ +0.142** — **0 을 포함한다**. 즉 Gong 데이터가 주장하는 것은
"증가한다"가 아니라 **"이 구간에서 농도는 지배인자가 아니다"** 이다(원문 극차분석에서도
연마입자가 3인자 중 최하위). 반면 현행 −0.406 은 1→5 wt% 에서 MRR 이 절반 이하로
떨어진다고 예측하는데, Gong 의 관측 구간 전체가 그 구간이다.

**이번 회차에서는 값·코드를 바꾸지 않았다.** 이유:
(a) 이 데이터를 지수 적합에 쓰는 순간 유일한 held-out 이 calibration 으로 바뀐다 —
    갭이 해소되는 게 아니라 이동한다.
(b) 두 관측 모두 E3(대상계 실측)이라 서열로 못 깨고, 계 근접도로도 못 깬다
    (둘 다 4H-SiC·알루미나·KMnO4·산성). 판정#37 과 같은 상황이다.
(c) Gong 은 압력 4 psi·유효 pH 2~6, Entegris 는 1 psi·pH 2.3 고정이라
    압력·다른 인자 교란이 남아 있다.
→ EVIDENCE-RULES 3회차 한도 안에서 다음 회차가 종결할 것. 후보 결론은
  "두 관측이 모두 맞되 지수의 크기가 다른 게 아니라 **농도가 이 계에서 약한 인자**라
  둘 다 |지수|가 작은 잡음 구간을 보고 있다"(§4 null 결론형) 이다 — 지금은 **미검증**.

## 5. 정량 재현

```python verify
import math

# Gong 2024 Materials 17(3) 679 Table 2 — L25 직교표 원 측정값 (μm/h)
rows = [(2,1,1,0.5212),(2,2,3,0.7665),(2,3,5,0.7972),(2,4,2,0.4906),(2,5,4,0.6439),
        (3,1,5,0.5519),(3,2,2,0.4599),(3,3,4,0.7052),(3,4,1,0.6439),(3,5,3,0.6439),
        (4,1,4,0.4906),(4,2,1,0.7052),(4,3,3,0.5212),(4,4,5,0.7052),(4,5,2,0.7358),
        (5,1,3,0.5212),(5,2,5,0.7052),(5,3,2,0.7052),(5,4,4,0.8278),(5,5,1,0.7972),
        (6,1,2,0.5825),(6,2,4,0.7358),(6,3,1,0.6745),(6,4,3,0.7665),(6,5,5,0.7052)]
assert len(rows) == 25

def marginal(idx):
    d = {}
    for r in rows:
        d.setdefault(r[idx], []).append(r[3])
    return {k: sum(v)/len(v) for k, v in sorted(d.items())}

# (1) 원문 Table 3 의 k 값을 우리가 표에서 재계산한 값과 대조한다.
#     ⚠ 허용오차 5e-4 인 이유: 논문은 K/k 를 **반올림 전** 원값으로 계산했는데
#     (본문 전개식에 0.79716·0.52122 처럼 Table 2 의 0.7972·0.5212 보다 자릿수가
#     많은 값이 등장한다), 우리는 Table 2 에 인쇄된 4자리 값만 쓴다. 차이는
#     그 반올림에서만 오고 최대 3.3e-4 다. 억지로 맞추지 않고 그대로 둔다.
#     논문 인쇄값: k_pH = 0.64386 / 0.60094 / 0.631596 / 0.711312 / 0.692916
lit_k_ph = [0.64386, 0.60094, 0.631596, 0.711312, 0.692916]
mine_ph = list(marginal(0).values())
for a, b in zip(lit_k_ph, mine_ph):
    assert abs(a - b) < 5e-4, (a, b)

#     인쇄값: k_ox = 0.533484 / 0.67452 / 0.680652 / 0.686784 / 0.70518
lit_k_ox = [0.533484, 0.67452, 0.680652, 0.686784, 0.70518]
for a, b in zip(lit_k_ox, marginal(1).values()):
    assert abs(a - b) < 5e-4, (a, b)

#     인쇄값: k_abr = 0.668388 / 0.594804 / 0.64386 / 0.680652 / 0.692916
lit_k_abr = [0.668388, 0.594804, 0.64386, 0.680652, 0.692916]
for a, b in zip(lit_k_abr, marginal(2).values()):
    assert abs(a - b) < 5e-4, (a, b)

# (2) 원문 극차 R: 산화제 0.171696 > pH 0.110376 > 연마입자 0.097812
def rng(idx):
    v = list(marginal(idx).values())
    return max(v) - min(v)
assert abs(rng(1) - 0.171696) < 5e-4
assert abs(rng(0) - 0.110376) < 5e-4
assert abs(rng(2) - 0.097812) < 5e-4
# 지배 순서: 산화제 > pH > 연마입자  ← 우리 모델에서 앞의 둘이 죽어 있다
assert rng(1) > rng(0) > rng(2)

# (3) §4 표의 농도 지수: 주변평균 로그-로그 기울기 +0.036 (부호가 −0.406 과 반대)
def loglog_slope(m):
    xs = [math.log(k) for k in m]
    ys = [math.log(v) for v in m.values()]
    xb = sum(xs)/len(xs); yb = sum(ys)/len(ys)
    return sum((x-xb)*(y-yb) for x, y in zip(xs, ys)) / sum((x-xb)**2 for x in xs)

s_abr = loglog_slope(marginal(2))
assert abs(s_abr - 0.0352) < 5e-3, s_abr
assert s_abr > 0 > -0.406           # 현행 팩 지수와 부호가 반대
# 다만 크기가 작다 — "증가한다"가 아니라 "약한 인자"라는 §4 결론의 근거
assert abs(s_abr) < 0.10

# (4) 산화제 축은 약하지 않다: 같은 방식의 기울기가 연마입자의 4배 이상
s_ox = loglog_slope(marginal(1))
assert abs(s_ox - 0.1626) < 5e-3, s_ox
assert s_ox > 4 * abs(s_abr)

# (5) 단위 변환 검산: 표의 μm/h → 데이터셋의 nm/min (×1000/60)
assert abs(0.5212 * 1000/60 - 8.6867) < 1e-3
assert abs(0.8278 * 1000/60 - 13.7967) < 1e-3
```

## 6. 다음 작업 (구현 요청 아님 — 정확도 루프 항목)

1. **KMnO4 산화제 형상 확보**: 이 L25 는 산화제 축이 5수준이라 형상 적합이 가능하다.
   다만 그렇게 쓰면 held-out 지위를 잃는다 → **다른 문헌의 KMnO4 스윕**을 찾아 형상을
   넣고, 이 데이터셋은 blind 검증용으로 보존하는 것이 옳은 순서다.
2. **pH 항의 연마입자 게이트**: `_ph_softening_term` 이 세리아 전용인 것은 세리아
   chemical-tooth 물리에서 온 제약인데, SiC 계의 pH 효과는 산화막 생성/용해라
   연마입자 종과 독립일 수 있다 — 문헌 확인 후 별도 판정 필요.
3. §4 농도 지수 충돌 종결(3회차 한도).

## 7. 한계 (정직 표기)

- 원문 본문은 최적 조합을 "pH=4" 라 쓰지만 같은 논문 Table 3 의 k 값은 pH=5 가 최대다
  (0.7113 vs 0.6316). **원문 내부 불일치**이며, 우리는 Table 2 원 측정값만 쓰므로
  데이터에는 영향이 없다. 원인은 확인 못 함 — 미검증.
- 절대 MRR 은 0.46~0.83 μm/h(7.7~13.8 nm/min) 좁은 구간(최대/최소 1.8배)에 몰려 있어
  순위 검정이 측정 노이즈에 민감하다. 반복 측정 산포는 원문에 없다 — 미보고.
- 팩은 입경 500 nm 를 자기선언하지 않는다(부모 세리아 값 상속). 이 DOE 는 입경을
  고정하므로 순위에는 무영향이나 절대값 비교에는 부적합하다.
