<!-- V2-SECTION: R2-slurry | 근거: 구리 CMP 의 pH → MRR 관계(산성역), 산화제·억제제 공존계 -->
# 구리 CMP 의 pH 의존성은 **산화제 매개 + V자 곡선의 산성 가지**다 — pH 3–6 로그선형 k≈0.143/pH

> 에이전트: slurry-chemist | 작성일: 2026-09-15
> 선행: [[w-cmp-ph-acidic-oxidizer-mediated-stojadinovic]] (텅스텐 선례, 같은 형식)
>       [[cu-electrochemistry-pourbaix-bta-oxidizer-inhibitor]] (Cu-H₂O Pourbaix·BTA 막)
> 관련 팩: `knowledge/params/cu_h2o2_bta.yaml` (pH 4.0, H₂O₂ 3 wt%, BTA 1 mM)
> 관련 코드: `sim/factors.py` — Cu 계 pH 항 **현재 없음**(이 노트가 그 빈칸을 채운다)

---

## 0. 결론 요약 (먼저 읽어라)

| 항목 | 값 |
|---|---|
| 메커니즘 | **텅스텐과 다르다.** Cu 금속의 산화 반쪽반응(Cu → Cu²⁺ + 2e⁻)은 H⁺ 를 포함하지 않아 **pH 무관**(dE/dpH = 0). pH 는 (a) 산화제 H₂O₂ 의 환원 전위(dE/dpH = −59 mV), (b) **Cu²⁺ 용해성 / Cu₂O·CuO 부동태 상경계**, (c) BTA 막 안정성을 통해 간접적으로 들어온다 |
| 전체 곡선 형태 | **V 자(정점형이 아니라 골형)** — 산성에서 높고 pH 6~6.5 에서 최소, 알칼리에서 다시 증가 |
| 우리 팩 영역(pH 3–6, H₂O₂ + BTA) | 로그선형 감소, `f(pH) = exp(−k·(pH − 4.0))`, **k = 0.1428 /pH unit** |
| 재현오차 | 12 점 최대 **7.3 %**, pooled R² = 0.954 |
| 실측 표 | **확보** (US20080090500A1 TABLE 4, 5 × 4 = 20 점) |
| 게이트 | 연마입자 ≥ 2 wt%, 산화제 존재, pH 3–6. 이 밖은 **스코프 밖** |

---

## 1. 문제 — Cu 팩은 pH 를 3→11 로 바꿔도 화학 팩터가 1.000000 이다

`cu_h2o2_bta` 팩은 `slurry_ph: 4.0` 을 선언하지만 `sim/factors.py` 의 어떤 pH 항도
Cu 계에서 켜지지 않는다. 실리카 산화막의 `_ph_peak_term`(정점형)·세리아의
`_ph_ceria_electrostatic_term`(IEP 창)·텅스텐의 `_ph_w_acidic_term`(Nernst 지수형)
셋 다 메커니즘이 다르므로 그대로 빌려오면 부호나 극값 위치가 틀린다.

**특히 텅스텐 식을 그대로 이식하면 틀린다** — §2 가 그 이유다.

## 2. 메커니즘 — 왜 텅스텐 유도를 그대로 못 쓰는가

텅스텐은 산화 반쪽반응 자체에 H⁺ 가 들어간다:

```
W + 3H2O -> WO3 + 6H+ + 6e-,   E_rev = -0.119 - 0.059*pH
```

**구리는 다르다.** Cu 금속의 1차 산화는

```
Cu -> Cu2+ + 2e-,   E0 = +0.3419 V (CRC 전기화학표)
```

로 **H⁺ 를 포함하지 않는다 → dE/dpH = 0**. Pourbaix 도표에서 Cu²⁺/Cu 경계가
수평선인 것이 바로 이것이고, 이는 형제 노트
[[cu-electrochemistry-pourbaix-bta-oxidizer-inhibitor]] §2 가 CRC 표에서 직접 계산해
Tamilmani 2005 그림 4.1 판독값(0.22 V)과 ±0.03 V 로 대조 확인한 사실이다.

그러면 pH 는 어디로 들어오는가 — **세 경로가 있고, 그중 하나만 지수형이다**:

| 경로 | 내용 | pH 민감도 | 이 노트의 취급 |
|---|---|---|---|
| (a) 산화제 구동력 | H₂O₂ + 2H⁺ + 2e⁻ → 2H₂O, dE/dpH = **−59 mV** | 셀 전위 전체의 pH 기울기가 여기서만 나온다 | 지수형의 **물리적 근거** |
| (b) 상경계 | pH < 4.1(a=10⁻⁴)에서 Cu²⁺ 용해, 그 위에서 Cu₂O/CuO 부동태 | 계단형(경계에서 급변) | **V 자 골의 위치**를 결정 — 지수형으로 못 담음 |
| (c) BTA 막 | Cu(I)-BTA 안정영역 pH ≈ 2.7–9.8, pH > 9.8 에서 Cu₂O 가 밀어냄 | 구간형 | **적용 상한**의 근거 |

**즉 Cu 의 pH 항은 텅스텐처럼 "Nernst 를 직접 지수에 넣은 것"이 아니다.**
Nernst 는 (a) 를 통해 **부호와 대략적 크기의 정당화**만 주고, 실제 계수 k 는
실측 표에서 역산한 **경험 계수**다. §6 이 이 구별을 수치로 못박는다.

### 2.1 브이(V) 자 — 문헌이 일치하는 정성 사실

두 독립 1차 출처가 같은 형태를 보고한다(둘 다 **BTA 없음**, H₂O₂ 단독계):

- **Du & Desai (2003)**, MRS Proc. 767, F6.6, DOI **10.1557/PROC-767-F6.6** —
  초록 원문: *"In 5% H₂O₂, the Cu removal rate decreases with an increase in pH and
  reaches minimum at pH 6, and then increases under alkaline conditions."*
  (본문 PDF 미확보 — 초록의 정성 서술만 인용. **수치 없음**)
- **Ilie & Ipate (2017)**, *Lubricants* 5(2) 15, DOI **10.3390/lubricants5020015** —
  전문 PDF 확보(`mdpi-res.com` 직링크). 그림 1, 5.5 % H₂O₂ 구연산 완충계,
  Cu ≥ 85 % 선택층. 본문: *"Both the selective layer MRR and the ER decreased with
  the increasing pH and reach a minimum at pH 6.5, then the removal and etching
  rates start to increase with increasing pH."*
  그림 1 판독(4점, 왼축 MRR Å/min / 오른축 ER Å/min): pH 2 ≈ 1010 / 70,
  pH 4.1 ≈ 810 / 38, pH 6.5 ≈ 40 / 0, pH 8.5 ≈ 300 / 20.
  ⚠ **그림 판독이며 원문 표가 아니다**. 또 시편이 Cu 블랭킷 웨이퍼가 아니라
  마찰 선택전이층(OLC45 강 + CuSn12T 청동, Cu ≥ 85 %)이다 → **계수 유도에는 쓰지 않았다**.
  V 자의 존재와 골 위치(pH 6~6.5)를 **독립 확증**하는 용도로만 쓴다.

두 출처가 골 위치를 pH 6 과 6.5 로 각각 말하는 것은 조성 차이(5 % vs 5.5 % H₂O₂,
완충제 유무)로 설명 가능한 범위다 — **평균내지 않고 둘 다 기록한다**.
Pourbaix 로 읽으면 이 골은 Cu²⁺ 용해영역이 끝나고 CuO 부동태가 완성되는 지점이다
(형제 노트 §2.1: Cu²⁺/CuO 수직선 pH ≈ 5.65, a = 10⁻⁴).

---

## 3. 1차 출처

| # | 출처 | 등급 | 확보 |
|---|---|---|---|
| **S1** | **US20080090500A1** (PPG Industries Ohio; S. Hellring, Y. Li, R. Auger), "Process for reducing dishing and erosion during chemical mechanical planarization", 우선일 2002-08-05, 공개 2008-04-17. **TABLE 4** | **E2** (pH 만 바꾼 1축 DOE, 4 pH × 5 연마입자농도 완전교차) | 전문 HTML `papers/patents/US20080090500A1.html` |
| S2 | **US9200180B2** (Air Products / 현 Versum·Merck), TABLE 4 Examples 15–19 | E3 (**BTA 없음**, 벤젠술폰산계, 알칼리역 — 교차확인 전용) | `papers/US9200180B2.txt` |
| S3 | Du, T.; Desai, V. (2003), MRS Proc. 767, F6.6, DOI 10.1557/PROC-767-F6.6 | E3 (초록만, 수치 없음) | 초록 |
| S4 | Ilie, F.; Ipate, G. (2017), *Lubricants* 5(2) 15, DOI 10.3390/lubricants5020015, 그림 1 | E3 (그림 판독 + 대리 시편) | 전문 PDF `papers/ilie2017-lubricants-cu-selective-layer-ph-mrr.pdf` |
| S5 | Ihnfeldt, R. (2008), Ph.D. dissertation, UC San Diego, Table 6.1/6.2 | E3 (pH·조성 동시 변동, 교란) | `papers/ihnfeldt2008-ucsd-dissertation-cu-cmp-alumina-colloidal.pdf` |
| S6 | CRC *Electrochemical Series* (Vanýsek), 형제 노트 §2 경유 | E1 (표준전위표) | `papers/crc-vanysek-electrochemical-series.pdf` |

**S1 이 이 노트의 근거다.** 왜 E2 인가: 같은 실험군에서 **글리신 1 wt% · BTA 1 mM ·
H₂O₂ 3 wt% · 장비(Struers LabPol-V) · 하중 30 N · 회전 60/60 rpm · 유량 60 mL/min ·
연마시간 1 min 을 전부 고정한 채**, H₂SO₄/KOH 로 **pH 만** 3/4/5/6 으로 바꿨다.
게다가 연마입자 농도 0/1/2/3/4 wt% 로 **완전교차**했으므로 pH 효과가 기계항과
분리된다. 이것은 우리 팩 조성(pH 4.0, H₂O₂ 3 wt%, BTA)과 **산화제 농도·억제제 종류·
pH 기준점이 모두 일치**하는 대응계다 — 텅스텐 노트가 대리계(KIO₃ vs Fe(NO₃)₃)였던
것과 대비해 오히려 정합성이 좋다.

---

## 4. 원문 수치 (S1 TABLE 4, 인용 — 판독 아님)

Copper Removal Rate (Å/min). 글리신 1 wt%, BTA 1 mM, H₂O₂ 3 wt%.

| 실리카 (wt %) | pH 3 | pH 4 | pH 5 | pH 6 |
|---|---|---|---|---|
| **0** | **259** | **106** | **176** | **151** |
| 1 | 434 | 488 | 412 | 342 |
| 2 | 597 | 537 | 483 | 393 |
| 3 | 705 | 617 | 528 | 451 |
| 4 | 801 | 644 | 565 | 520 |

부수 사실(같은 특허 TABLE 1–3, 실리카 스윕): 실리카 0 wt% 에서 Cu RR 은
207 / 68 / 94 nm/min 로 실리카 존재 시(400~626 nm/min)보다 크게 낮다 —
**기계 작용이 없으면 이 계의 제거는 대부분 사라진다**.

---

## 5. 새로 도출한 지식 — 계수 유도

### 5.1 게이트 근거: **연마입자가 없으면 pH 곡선이 무너진다**

0 wt% 행(259 / 106 / 176 / 151)은 **단조도 아니고 V 자도 아니다** — pH 4 에서
오히려 최소를 찍고 pH 5 에서 되올라간다. 텅스텐 노트에서 "산화제가 없으면 부호가
반대"였던 것과 같은 성격의 **게이트 신호**다. 1 wt% 행도 R² = 0.594 로 로그선형에서
벗어난다(pH 3 < pH 4). 따라서 이 항은 **연마입자 ≥ 2 wt% 에서만** 적용한다.

물리적으로도 정합한다: pH 는 **부동태막의 성질**을 바꾸는데, 그 막을 벗길 기계력이
없으면 pH 효과가 MRR 로 번역되지 않는다(형제 노트 §5 의 MRR/정적식각 비 11.5 와 같은 구조).

### 5.2 계수 — 실리카 2/3/4 wt% 세 계열의 pooled 로그선형 적합

세 계열의 개별 k 는 0.1360 / 0.1496 / 0.1427 (R² = 0.968 / 0.999 / 0.956),
평균 대비 산포 **±4.8 %** — 텅스텐(±22 %)보다 훨씬 좁다. 각 계열을 **자기 pH 4 값으로
정규화**하고 12 점을 한 번에 적합하면

```
f(pH) = exp(-k * (pH - pH_ref)),   k = 0.1428 /pH unit,   pH_ref = 4.0
```

pooled R² = **0.9537**, 12 점 최대 재현오차 **7.26 %** (S1 US20080090500A1 TABLE 4 12점 역산, §6 verify 블록에서 재현).

| pH | f(pH) |
|---|---|
| 3.0 | 1.1535 |
| 3.5 | 1.0740 |
| **4.0** | **1.0000** (팩 기준점, 이중계상 방지 계약) |
| 5.0 | 0.8669 |
| 6.0 | 0.7516 |

**왜 지수형인가**: (a) 셀 전위의 pH 기울기가 산화제 쪽 Nernst 항에서 선형으로 나오고,
(b) 전기화학 속도가 전위에 지수적으로 반응하는 것이 표준(Tafel)이기 때문이다 —
텅스텐 노트와 같은 논리. **다만 §6 이 보이듯 이 계에서 Tafel 로 k 를 독립 유도하면
숫자가 맞지 않는다** → 등급은 **literature(E2), verified 아님**.

### 5.3 알칼리 가지는 **같은 식이 아니다** (분기점 = 게이트 조건)

S2(US9200180B2 TABLE 4, Ex.15–19; 10 wt% K-안정 실리카, H₂O₂ 1 wt%,
벤젠술폰산 1 wt%, **BTA 없음**, 2.0 psi):

| pH | 6.2 | 7.1 | 8.7 | 9.4 | 9.9 |
|---|---|---|---|---|---|
| Cu RR (Å/min) | 732 | 577 | 334 | 263 | 214 |

이 5 점도 로그선형이지만(R² = 0.9971) **k = 0.3329 /pH — 산성 가지의 2.33 배**다.
같은 지수형에 같은 k 를 쓰면 pH 10 에서 배수가 2.3 배 틀린다.

**문헌이 갈라지는 지점을 평균내지 않는다.** 갈라짐의 원인은 두 가지가 겹쳐 있다:

1. **BTA 유무.** S1 은 BTA 1 mM, S2 는 BTA 없음. BTA 가 없으면 pH 상승에 따른
   부동태화가 막에 직접 나타나고(특허 본문: *"removal rates of copper decreased due to
   increased passivation of copper at high pH"*), 억제제가 이미 표면을 덮고 있으면
   그 추가 부동태의 한계효과가 작아진다 — 기울기가 완만해지는 방향.
2. **pH 구간.** S1 은 3–6(V 자의 산성 가지), S2 는 6.2–9.9(골을 지나 알칼리로 진입).
   S3/S4 의 V 자에 따르면 pH 6.5 부근에서 **부호가 뒤집혀야** 하는데 S2 는 계속 감소한다
   → S2 조성(벤젠술폰산, BTA 없음)에서는 V 자 회복이 pH 10 위로 밀려 있거나 없다.

**두 축이 얽혀 있어 어느 쪽이 주된 원인인지 이 데이터로는 분리할 수 없다.**
그래서 이 노트는 산성 가지 하나만 모델링하고, pH > 6 은 **스코프 밖**으로 둔다.

---

## 6. 정직: Tafel 로 k 를 독립 유도하면 맞지 않는다

지수형의 물리적 정당화를 끝까지 밀어보면:
k = 0.1428 /pH → 0.0620 decade/pH → 산화제 Nernst 기울기 59.16 mV/pH 로 나누면
1.048 decade/V → **Tafel 기울기 b ≈ 0.954 V/decade**.

전형적 전하이동 지배 Tafel 기울기는 0.06–0.12 V/decade 다 — **약 10 배 어긋난다.**
해석: 이 계의 율속은 순수 전하이동이 아니라 **부동태막 두께·기계적 제거·확산이 섞인
혼합 지배**이고, 그래서 k 는 Nernst 에서 유도되는 값이 아니라 **실측에서 역산한
경험 계수**다. 텅스텐 노트는 이 검산을 하지 않았지만(2점 할선이라 불가능했다),
Cu 는 4점 × 3계열이라 할 수 있었고 **결과는 "유도 실패"다. 이것을 숨기지 않는다.**

→ 함수형의 **선택**은 물리(단조·양수·배수형)에서 오지만, **계수의 크기는 순수 실측**이다.

---

## 7. 정량 재현 (verify)

```python verify
import math

# ---------------------------------------------------------------
# S1: US20080090500A1 (PPG Industries Ohio; Hellring, Li, Auger),
#     "Process for reducing dishing and erosion during CMP", TABLE 4.
#     glycine 1 wt%, BTA 1 mM, H2O2 3 wt%, pH adjusted with H2SO4/KOH,
#     Cu puck, 1 min, 60 mL/min, 30 N (~9.8 psi). RR in A/min.
# ---------------------------------------------------------------
T4 = {
    0: {3: 259, 4: 106, 5: 176, 6: 151},   # no abrasive
    1: {3: 434, 4: 488, 5: 412, 6: 342},
    2: {3: 597, 4: 537, 5: 483, 6: 393},
    3: {3: 705, 4: 617, 5: 528, 6: 451},
    4: {3: 801, 4: 644, 5: 565, 6: 520},
}

# (1) GATE: 연마입자가 없으면 pH 계열이 단조가 아니다 -> 이 항을 적용하면 안 된다
row0 = T4[0]
assert not all(row0[p] > row0[p + 1] for p in (3, 4, 5))
assert row0[4] < row0[5] < row0[3]          # 106 < 176 < 259 : pH4 에서 골, 감쇠가 아님
print("gate ok: abrasive-free row 259/106/176/151 is non-monotonic")

# (2) 계열별 로그선형 k
def fit(d):
    ph = sorted(d); y = [math.log(d[p]) for p in ph]; n = len(ph)
    mx, my = sum(ph) / n, sum(y) / n
    sl = sum((a - mx) * (b - my) for a, b in zip(ph, y)) / sum((a - mx) ** 2 for a in ph)
    inter = my - sl * mx
    ssr = sum((b - (inter + sl * a)) ** 2 for a, b in zip(ph, y))
    sst = sum((b - my) ** 2 for b in y)
    return -sl, 1 - ssr / sst

ks = {s: fit(T4[s]) for s in (1, 2, 3, 4)}
for s, (k, r2) in ks.items():
    print("  silica %d wt%%: k=%.4f  R2=%.4f" % (s, k, r2))
assert abs(ks[1][0] - 0.0884) < 5e-4 and ks[1][1] < 0.70      # 1 wt% 는 이탈점 (R2 0.59)
for s in (2, 3, 4):
    assert ks[s][1] > 0.95

# (3) 실리카 2/3/4 wt% pooled 적합 (각 계열을 자기 pH4 값으로 정규화)
pairs = [(p, math.log(T4[s][p] / T4[s][4])) for s in (2, 3, 4) for p in sorted(T4[s])]
n = len(pairs)
mx = sum(p for p, _ in pairs) / n
my = sum(v for _, v in pairs) / n
sl = sum((p - mx) * (v - my) for p, v in pairs) / sum((p - mx) ** 2 for p, _ in pairs)
inter = my - sl * mx
K = -sl
ssr = sum((v - (inter + sl * p)) ** 2 for p, v in pairs)
sst = sum((v - my) ** 2 for _, v in pairs)
R2 = 1 - ssr / sst
print("pooled k = %.5f /pH, R2 = %.4f" % (K, R2))
assert abs(K - 0.14277) < 5e-5, K
assert R2 > 0.95
assert abs(inter + sl * 4.0) < 0.02        # 적합선이 pH 4 에서 ln(1)=0 을 지난다

# (4) f(pH)=exp(-k*(pH-4)) 의 재현오차
f = lambda ph, k=K, ref=4.0: math.exp(-k * (ph - ref))
errs = []
for s in (2, 3, 4):
    for p in sorted(T4[s]):
        obs = T4[s][p] / T4[s][4]
        errs.append(100 * (f(p) - obs) / obs)
print("max |err| over 12 points = %.2f%%" % max(abs(e) for e in errs))
assert max(abs(e) for e in errs) < 7.5
assert abs(f(4.0) - 1.0) < 1e-12           # 팩 기준점에서 배수 정확히 1.0 (이중계상 방지)
assert f(3.0) > 1.0 > f(6.0)               # 산성일수록 빠르다
assert abs(f(3.0) - 1.1535) < 1e-3
assert abs(f(6.0) - 0.7516) < 1e-3

kk = [ks[s][0] for s in (2, 3, 4)]
kbar = sum(kk) / 3
spread = max(abs(x - kbar) for x in kk) / kbar
print("individual k = %s, mean %.4f, spread +-%.1f%%" % (["%.4f" % x for x in kk], kbar, 100 * spread))
assert spread < 0.06                        # 텅스텐(+-22%) 대비 훨씬 좁다 -> pooling 정당화

# ---------------------------------------------------------------
# S2 교차확인: US9200180B2 TABLE 4 Ex.15-19 (10% K-silica, 1% H2O2,
#     1% benzenesulfonic acid, BTA 없음, 2.0 psi) -- 부호 같고 2.3배 가파르다
# ---------------------------------------------------------------
ph2 = [6.2, 7.1, 8.7, 9.4, 9.9]
rr2 = [732, 577, 334, 263, 214]
k2, r22 = fit(dict(zip(ph2, rr2)))
print("US9200180B2: k=%.4f R2=%.4f  (k2/k1 = %.2f)" % (k2, r22, k2 / K))
assert abs(k2 - 0.33289) < 5e-5 and r22 > 0.99
assert k2 / K > 2.0                         # BTA 없는 알칼리 가지는 별도 레짐

# ---------------------------------------------------------------
# Nernst 교차검증: Cu 금속 반쪽반응은 pH 무관. 기울기는 전부 산화제에서 온다.
# 그리고 Tafel 로 k 를 독립 유도하면 10배 어긋난다 (숨기지 않는다).
# ---------------------------------------------------------------
kN = 0.05916
E_Cu = 0.3419                     # Cu2+ + 2e- = Cu, CRC (H+ 없음 -> dE/dpH = 0)
dEdpH_cell = -kN - 0.0            # H2O2 + 2H+ + 2e- = 2H2O 만 pH 를 탄다
assert abs(dEdpH_cell + 0.05916) < 1e-9
dec_per_pH = K / math.log(10)
b = 1.0 / (dec_per_pH / kN)
print("implied Tafel slope b = %.3f V/decade (전형 전하이동 0.06-0.12)" % b)
assert b > 0.5, "b 가 이상값의 ~10배 -> 지수형은 경험식이지 유도식이 아니다"
print("OK k=%.4f  f(3)=%.4f f(4)=%.4f f(6)=%.4f" % (K, f(3), f(4), f(6)))
```

기대 출력:
```
gate ok: abrasive-free row 259/106/176/151 is non-monotonic
  silica 1 wt%: k=0.0884  R2=0.5944
  silica 2 wt%: k=0.1360  R2=0.9684
  silica 3 wt%: k=0.1496  R2=0.9985
  silica 4 wt%: k=0.1427  R2=0.9564
pooled k = 0.14277 /pH, R2 = 0.9537
max |err| over 12 points = 7.26%
individual k = ['0.1360', '0.1496', '0.1427'], mean 0.1428, spread +-4.8%
US9200180B2: k=0.3329 R2=0.9971  (k2/k1 = 2.33)
implied Tafel slope b = 0.954 V/decade (전형 전하이동 0.06-0.12)
OK k=0.1428  f(3)=1.1535 f(4)=1.0000 f(6)=0.7516
```

---

## 8. 적용 경계 — 어디서 이 식이 깨지는가

| 경계 | 근거 | 조치 |
|---|---|---|
| **pH > 6** | S3/S4 의 V 자 골(pH 6~6.5)에서 **부호가 뒤집힌다**. S2 는 같은 구간에서 계속 감소하지만 k 가 2.33 배 — 조성마다 다르다 | **스코프 밖.** 범위 밖 경고만, 외삽 금지 |
| **pH < 3** | S1 의 최저 관측점이 pH 3. Cu²⁺/Cu/Cu₂O 삼중점이 pH 4.14(a = 10⁻⁴)이므로 pH 3 은 이미 완전 용해영역 | 외삽 금지 |
| **연마입자 < 2 wt%** | S1 0 wt% 행은 비단조(259/106/176/151), 1 wt% 행은 R² = 0.594 | **항을 켜지 마라** |
| **산화제 없음** | S1 전 계열이 H₂O₂ 3 wt% 고정 — 산화제 0 대응쌍이 표에 **없다** | **미확인.** 텅스텐에서 부호가 뒤집혔던 전례가 있으므로 기본값은 "적용 안 함" |
| **BTA 없음** | S2(BTA 없음)의 k 가 2.33 배. BTA 유무와 pH 구간이 얽혀 분리 불가(§5.3) | 별도 레짐, 이 k 를 쓰지 마라 |
| **착화제 종류** | S1 은 글리신 1 wt%. 구연산·옥살산·EDTA 계는 착화 상수가 달라 Cu²⁺ 용해도 곡선이 이동한다 | 미확인 |
| **절대 MRR** | S1 은 Cu 퍽 · 30 N(≈9.8 psi) · Struers 탁상 연마기. 우리 팩(2~3 psi 웨이퍼)과 장비가 다르다 | 이 항은 **배수만** 가져온다 |

---

## 9. 한계 (숨기지 않는다)

1. **Tafel 독립 유도 실패** (§6). 함수형 선택은 물리, 계수 크기는 순수 실측이다.
   텅스텐 노트보다 이 점에서 근거가 **약하다** — 그쪽은 2점이라 검산 자체를 못 했을 뿐이다.
2. **S1 은 특허다.** 동료심사 논문이 아니고 오차막대·반복수가 없다. 다만 5 × 4 완전교차
   설계와 세 계열의 k 산포 ±4.8 % 가 내적 일관성을 보증한다.
3. **V 자의 알칼리 가지를 모델링하지 않았다.** S3 는 수치 없는 초록뿐이고, S4 는
   그림 판독 + Cu 85 % 대리 시편이다. **알칼리 가지의 계수는 표 미확보 = 미검증**이며,
   이 노트의 알칼리 구간 서술은 전부 **2차 인용**(초록·그림 판독)으로 원문 수치를
   **확인 못 했다**.
4. **골(minimum) 위치가 문헌마다 다르다** (pH 6 vs 6.5). 평균내지 않고 둘 다 남긴다.
   코드에 경계를 넣지 않고 pH > 6 범위 밖 경고로만 처리한다(텅스텐 노트와 같은 관례).
5. **S5(Ihnfeldt 2008 Table 6.2)를 계수 유도에 쓰지 않았다.** 이 표는 같은 pH 변경에
   응집크기·경도·식각률이 동시에 바뀌어(예: 글리신 + 0.1 % H₂O₂ 계열이 pH 3.0 → 8.3 →
   10.0 에서 8 → 287 → 350 nm/min 로 **증가**) 교란이 심하다. 부호조차 조성마다 뒤집힌다
   (2.0 % H₂O₂ 계열은 113 → 289 → 166 으로 정점형) — **이것 자체가 §5.3 게이트의
   독립 방증**이지만 계수를 뽑을 수 있는 통제된 1축 DOE 가 아니다.
6. **산화제 0 대응쌍이 없다.** 텅스텐에서 가장 결정적이었던 게이트 근거(비 0.625)에
   해당하는 Cu 데이터를 확보하지 못했다. 그래서 "산화제 없음" 은 미확인으로 남긴다.
7. **k 와 억제제 항의 교호작용 미모델링.** §5.3 이 BTA 유무가 k 를 2.3 배 바꿀 수
   있음을 시사하지만, 이 코드베이스의 어떤 문헌도 BTA 농도 × pH 교차 표를 주지 않는다
   (형제 노트 [[chi-cu-h2o2-independent-refit-us9200180b2]] §6 의 같은 한계).

---

## 10. 구현 제안 (이 노트는 코드를 고치지 않았다)

```yaml
# knowledge/params/cu_h2o2_bta.yaml 에 추가 제안
  cu_ph_acid_k:
    value: 0.1428
    unit: "1/pH"
    confidence: literature      # verified 아님 — §6 Tafel 유도 실패
    source: knowledge/cmp/cu-cmp-ph-mechanism.md
  ph_ref:
    value: 4.0
    unit: pH
```

`sim/factors.py::_ph_cu_acidic_term` — `cu_ph_acid_k` + `ph_ref` + `slurry_ph` 가
**모두 선언되고**, 산화제가 존재하며, 연마입자 농도 ≥ 2 wt% 일 때만 켠다.
pH 가 [3, 6] 밖이면 노트에 경고를 남기고 **클램프하지 말고 그대로 계산하되**
결과를 신뢰 불가로 표시한다(텅스텐 항과 같은 관례).
