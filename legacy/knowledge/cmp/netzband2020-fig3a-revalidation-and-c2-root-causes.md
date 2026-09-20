# Netzband & Dunn 2020 Fig.3a 벡터 재판독 + C2 잔여 18칸 근본원인 분해

> 대상: `validation/datasets/netzband2020_thermal_oxide_ceria_ph.yaml`(판독 감사),
> `sim/chemistry.py::_ceria_term`의 `ceria_mechanical_floor` 기본값,
> COMPLETION.md C2 미충족 18칸.
> [[ceria-slurry-ce-redox-selectivity]] [[chi-oxidizer-curve-exponent-identifiability]]
> [[bta-inhibitor-langmuir-K-effective-cu-cmp-falsification]]

## 1. 1차 출처

- **[A]** C. M. Netzband, K. Dunn, "Controlling the Cerium Oxidation State During Silicon
  Oxide CMP to Improve Material Removal Rate and Roughness", *ECS J. Solid State Sci.
  Technol.* **9**, 044001 (2020). **DOI: 10.1149/2162-8777/ab8393** (CC BY 4.0 오픈액세스).
  전문 확보: `papers/netzband2020-jss-ceria-oxidation-state-oxide-cmp.pdf` (5쪽).
- **[B]** C. M. Netzband, K. Dunn, "Investigation into the Effect of CMP Slurry Chemicals on
  Ceria Abrasive Oxidation State using XPS", *ECS J. Solid State Sci. Technol.* **8**(10),
  P629 (2019). **DOI: 10.1149/2.0311910jss**. **미확보(원문)** — Unpaywall이 OA(cc-by-nc-nd)로
  보고하나 IOP가 PDF 요청에 HTML 안내페이지(14 KB)를 돌려주고, 미러 사이트 미러는 altcha 봇검사에
  막혔다. [A]의 Fig.2a가 이 논문에서 adapted 된 Ce3+%-H2O2 곡선이므로, Ce3+% **절대값**은
  이번 회차에도 확보하지 못했다.

## 2. 무엇을 새로 했나 - Fig.3a 벡터 기하 독립 재판독

기존 데이터셋은 "막대 상단 y좌표와 y축 눈금을 선형사상"했다고만 적혀 있었다. 이번에 **PDF
벡터 객체(rect)에서 축 눈금과 막대를 직접 추출**해 독립적으로 재판독했다. 판독 절차:

- p.4(0-index 3)의 y축 눈금 rect: x 구간 [94.2, 97.2] 에 13개, y = 559.15 ... 713.21 pt
  (긴눈금 7개 + 짧은눈금 6개 교대). 최하단 713.21 = 0, 최상단 559.15 = 30 nm/min
  -> 축척 **5.1353 pt per (nm/min)**, 등간격.
- 초록 막대(non_stroking_color = (0, 0.502, 0)) 5개의 top 좌표에서 높이 환산.

결과(왼쪽부터: 상용 슬러리, pH 4, pH 6, pH 8, pH 10):

| 막대 | 높이 (pt) | 재판독 (nm/min) | 데이터셋 기존값 | 차이 |
|---|---|---|---|---|
| 상용   | 20.81  | **4.05**  | 4.11 (주석) | -1.5% |
| pH 4   | 101.63 | **19.79** | 19.8 | -0.05% |
| pH 6   | 57.94  | **11.28** | 11.3 | -0.18% |
| pH 8   | 102.60 | **19.98** | 20.0 | -0.10% |
| pH 10  | 109.16 | **21.26** | 21.3 | -0.19% |

**판정: 기존 데이터셋 4점은 모두 0.2% 이내로 재현된다(Netzband & Dunn 2020, doi:10.1149/2162-8777/ab8393 Fig.3a 벡터 재판독; §2 verify 블록에서 assert).** 서로 다른 판독 경로(수동 좌표
읽기 vs 벡터 rect 추출)가 같은 값을 주므로 판독 오류가 아니다. 상용 슬러리만 1.5% 차이인데,
이는 원 주석의 4.11이 반올림 경로가 달랐던 것으로 보이며 데이터셋 `conditions`에는 상용
슬러리가 들어 있지 않아 백테스트에 영향이 없다.

원문 서술과의 대조(자기검증): [A] 본문은 "both low and high pH resulted in removal rates
~20 nm min-1, about 4 times that of the commercial slurry"라 쓴다. 재판독값으로
19.79/4.05 = **4.89배**, 21.26/4.05 = **5.25배** - 본문의 "about 4 times"보다 크다.
저자가 어림한 것으로 **추정**되며(~20 및 ~4 모두 어림값), 판독값 자체는 "low·high pH 둘 다
~20, pH 6은 낮다"는 서술을 정확히 재현한다.

## 3. 새로 도출한 지식 - `ceria_mechanical_floor`의 독립 확증

`sim/chemistry.py::_ceria_term`은 기계 경로 바닥값을 `1/5.5 = 0.1818`로 둔다. 근거는
[A] 본문의 "polished **5.5 times faster** than the commercial slurry"(Fig.1a, H2O2 0.5 wt%
조건) 한 줄뿐이었다 - 즉 **단일 서술문에 매달린 값**이었다.

이번 Fig.3a 재판독은 **다른 그림·다른 실험축(pH 스윕)** 에서 같은 비율을 준다:
최고 MRR(pH 10) / 상용 = 21.26/4.05 = **5.25배** -> floor = 1/5.25 = **0.1905**.

현행 기본값 0.1818은 이 독립 추정치와 **4.6% 차이**로 일치한다. 두 값 모두 같은 논문·같은
상용 대조군이므로 완전 독립은 아니지만(E2: 동일 계, 다른 실험축), 서술문 1건에서 그림
2건으로 근거가 늘었다.

```python verify
# Fig.3a 벡터 재판독 - 축 눈금 기하에서 직접 환산
Y0_PT, Y30_PT = 713.21, 559.15      # y축 최하단(0)·최상단(30 nm/min) 눈금 rect 좌표
SCALE = (Y0_PT - Y30_PT) / 30.0     # pt per (nm/min)
assert abs(SCALE - 5.1353) < 1e-3, SCALE

bar_h_pt = {"commercial": 20.81, "pH4": 101.63, "pH6": 57.94, "pH8": 102.60, "pH10": 109.16}
mrr = {k: v / SCALE for k, v in bar_h_pt.items()}

# (1) 기존 데이터셋 값(validation/datasets/netzband2020_thermal_oxide_ceria_ph.yaml)과 대조
DATASET = {"pH4": 19.8, "pH6": 11.3, "pH8": 20.0, "pH10": 21.3}
for k, lit in DATASET.items():
    assert abs(mrr[k] - lit) / lit < 0.005, (k, mrr[k], lit)   # 0.5% 이내

# (2) 원문 서술 재현: pH 4·8·10 은 ~20 nm/min, pH 6 은 확연히 낮다
for k in ("pH4", "pH8", "pH10"):
    assert 19.0 < mrr[k] < 22.0, (k, mrr[k])
assert mrr["pH6"] < 0.62 * mrr["pH10"], mrr["pH6"]

# (3) ceria_mechanical_floor 독립 추정 - 최고/상용 비율의 역수
floor_fig3a = mrr["commercial"] / mrr["pH10"]
assert abs(floor_fig3a - 0.1905) < 0.002, floor_fig3a
FLOOR_CODE = 1.0 / 5.5              # sim/chemistry.py 현행 기본값 (Fig.1a 서술 "5.5 times")
assert abs(floor_fig3a - FLOOR_CODE) / FLOOR_CODE < 0.06, (floor_fig3a, FLOOR_CODE)
```

## 4. Fig.1a 는 왜 못 읽었나 (정직한 미확보 기록)

같은 방법을 p.3(0-index 2)의 Fig.1a(H2O2 농도 스윕)에 적용하면 막대 5개의 높이는
23.26 / 63.86 / 127.46 / 113.18 / 40.70 pt 로 깨끗하게 나온다. 그러나:

- **x축 라벨(H2O2 wt%)이 텍스트 레이어에 없다.** 이 페이지에서 top<258 인 char 는 캡션 54자뿐이다.
- **y축 최대값을 확정할 수 없다.** Fig.3a 축척(5.1353 pt/(nm/min))을 그대로 적용하면 최좌측
  막대가 4.53 nm/min 인데, Fig.3a 의 상용 막대는 4.05 다. 두 그림이 같은 축척이라면 같은
  대조군이 12% 어긋나므로(Netzband & Dunn 2020, doi:10.1149/2162-8777/ab8393 Fig.1a·Fig.3a 벡터 좌표 비교, 판독값 4.53 vs 4.05 nm/min — 미검증), 축 최대값이 다르거나 최좌측 막대가 상용이 아니다 - 구분 근거가 없다.

따라서 **Fig.1a 로부터 Ce3+%-MRR 관계(= `ceria_tooth_gain` 의 실측 근거)를 뽑는 것은 이번에도
불가능**하다. 이는 "안 찾아봐서"가 아니라 벡터 판독이 가능한 범위를 다 쓴 결과다. 필요한 것은
[B](2019 XPS 논문)의 Ce3+% 절대값이고, 그 원문이 §1의 이유로 막혀 있다. (미검증)

## 5. C2 잔여 18칸의 근본원인 분해

`tools/completion.py check` 가 남긴 C2 18칸을 개별 파라미터로 역추적하면, **서로 다른 18개
문제가 아니라 4개의 근본원인**이다. 팩 수 x 팩터 수로 곱해져 18칸으로 보일 뿐이다.

| # | 근본원인 | 막힌 칸 | 성격 | 해소 조건 |
|---|---|---|---|---|
| R1 | Γ: PCR 시간감쇠 앵커(50h->16%)가 Entegris 백서의 **2차 인용**, + `cond_disk_rpm` 드라이버 부재 | Γ x5 (estimated) | 원문 미확보 + 구조적 결측 | Palmgren 2004 원문 확보 **또는** 독립 PCR 감쇠 실측 문헌 |
| R2 | χ: `oxidizer_curve_n`·`ceria_tooth_gain` 이 **기준 운전점에서 항등적으로 1.0** - 현 데이터로 식별 불가 (EVIDENCE-RULES 판정 #19) | χ x4 | **식별성** 문제 (탐색 부족 아님) | 조성을 흔든 DOE 데이터셋(n>=4, 농도 1축) 확보 |
| R3 | ψ: `inhibitor_strength_k` 의 K_eq->정상상태 대입 경로가 **이미 정량 반증**됨 (판정 #17), 대체 K_eff 는 계 불일치(E3, 알칼리/알루미나) | ψ x2 | 모델 형태 결함 | 산성 H2O2+BTA 계의 BTA 농도 스윕 실측 |
| R4 | Δ·S: 표본 부족 외삽 - Δ 는 세리아 1화학종 실질 3점, S 는 실리카/IC1000 단일계 | Δ x3, S x4 | 도메인 외삽 | 다른 연마입자계의 시간드리프트·스크래치 스윕 |

**함의:** C2 를 "18번 검색하면 끝나는 일"로 보면 안 된다. R2·R3 은 문헌을 더 찾아도 안 열리고
**데이터셋(조성 스윕)이 있어야** 열린다. 즉 남은 C2 의 실질 경로는 VALIDATION 갭 해소와 같다.
R1·R4 만이 순수한 문헌 탐색 과제다.

## 6. 미검증·한계

- [B] 원문 미확보 -> Ce3+% 절대값 **미검증**(§4).
- Fig.1a 의 y축 최대값 확정 불가(§4) - 이 그림에서는 어떤 정량값도 인용하지 않았다. (미검증)
- §3 의 5.25배는 [A] 내부의 두 그림 비교이므로 완전 독립 확증이 아니다(E2). 다른 저자의
  세리아-상용 대조 실측이 나오면 그때 literature 승격을 재검토한다.
- 본문의 "about 4 times" 와 재판독 4.89~5.25배의 불일치는 저자 어림으로 해석한 것이며,
  저자에게 확인한 바 없다(추정).
