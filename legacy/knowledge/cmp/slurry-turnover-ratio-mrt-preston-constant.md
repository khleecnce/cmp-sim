<!-- V2-SECTION: R2-slurry | 공동: R3-pad | 근거: slurry, 전달, MRT | 정본: ARCHITECTURE-V2.md §3 -->
# 슬러리 체류시간(MRT)·턴오버비(TR) → Preston 상수 — τ 팩터의 두 번째 채널

> 목적: τ(슬러리 전달) 팩터는 지금까지 **η(이용효율) 한 채널**만 갖고 있었고, 그 결합 지수(0.07)는
> 기공률 실험에서 역산해 그루브 축에 교차 대입한 값(E4)이라 τ 전체 등급이 `unverified`에 묶여 있었다.
> 이 노트는 **대상계(ILD oxide CMP, 콜로이달 실리카) 직접 실측으로 전달→MRR 결합을 정량화한 1차 문헌**을
> 확보해 두 번째 채널(TR)을 만들고, 기존 η 채널과 **부호가 반대**라는 사실을 정량으로 확인한다.
> 상호링크: [[pad-groove-geometry-contact-area-flow-resistance]](Mu 2016 Table 3 정본),
> [[pad-porosity-slurry-transport-mrr]](Prasad 2013 η 채널 지수 0.07의 출처).

## 1. 1차 출처

1. **Philipossian, A. / Mitchell, E., "Mean Residence Time and Removal Rate Studies in ILD CMP",
   J. Electrochem. Soc. 151(6) G402–G407 (2004), DOI: 10.1149/1.1731539.**
   원문 PDF 확보(`papers/philipossian2004-jes-mrt-removal-rate-ild.pdf`, 6p, 본문·Fig.10~12 서술 전문 확인).
2. **Philipossian, A. / Mitchell, E., "Slurry Utilization Efficiency Studies in Chemical Mechanical
   Planarization", Jpn. J. Appl. Phys. 42 (2003) 7259, DOI: 10.1143/JJAP.42.7259.**
   원문 확보(`papers/philipossian2003-jjap-slurry-utilization-efficiency.pdf`).
3. **Mu, Zhuang, Sampurno, Wei, Ashizawa, Morishima, Philipossian, Microelectronic Engineering 157
   (2016) 60–63, DOI: 10.1016/j.mee.2016.02.035.** (MRT·η 실측 6점 — 이미 확보)

## 2. TR(턴오버비)의 정의와 실측 결합

Philipossian 2004 Eq.1: **TR = MRT / t_polish** (무차원). 폴리시 시간이 짧을수록, 혹은 슬러리가
웨이퍼-패드 계면에 오래 머물수록(MRT↑) TR이 커진다. TR이 크다는 것은 "물→슬러리 치환 과도기가
폴리시 시간 안에서 차지하는 비중이 크다"는 뜻이고, 과도기 동안 계면 고형분 농도가 정상상태(20 wt%)에
못 미치므로 제거가 손해를 본다.

논문이 준 **정량 앵커(Conclusion 직전 단락, Fig.12 해석)**:

> "a 30 s polish operating at 6 psi and a relative pad-wafer velocity of 0.31 m/s has a turnover
> ratio of 1.13. The linear model predicts that during the 30 s polish, **370 Å** of oxide are
> polished. In the absence of TR effects, the amount removed would be **500 Å**. This is a **26%
> reduction** from the expected oxide removal."

즉 **Preston 상수의 TR 의존은 선형**(Fig.12: "Preston's constant decreases steadily with TR")이고,
기울기는 두 점(TR=0 → 배수 1.0, TR=1.13 → 배수 370/500=0.740)으로 닫힌 형태로 풀린다:

    f_TR(TR) = 1 − a·TR,   a = (1 − 370/500)/1.13 = 0.2301  [1/TR]

실험 오차: 논문 명시 "relative standard deviation is approximately 10% for both the abscissa and
the ordinate", 반실험 모델-실측 일치도는 "within 4%"(Fig.11). **a는 2점 유도이므로 곡률은 미검증**이며,
논문 실측 TR 범위(0.28~1.13, Fig.10~12)를 벗어난 외삽은 하지 않는다. TR > 1/a = 4.35에서 f_TR이
음수가 되는 것은 명백한 비물리이므로 코드에서 하한 클램프를 건다.

## 3. MRT를 레시피에서 어떻게 얻는가 — Mu 2016 실측 6점

Mu 2016 Table 3(동일 저자군·동일 RTD 기법):

| 그루브폭 W(μm) | MRT@3PSI(s) | MRT@5PSI(s) | η@3PSI | η@5PSI |
|---|---|---|---|---|
| 300 | 9.2 | 8.3 | 9.9% | 10.6% |
| 600 | 10.6 | 9.3 | 13.4% | 14.7% |
| 900 | 13.9 | 12.7 | 12.8% | 13.6% |

내부 무결성 검사: MRT = V_total/q_actual 이므로 q_actual = V_total/MRT 가 표의 q_actual과 맞아야 한다.
아래 verify 블록에서 6점 전부 재현했고 5/6점이 0.2% 이내, Pad C@3PSI만 −2.3%(표 반올림 추정)로
어긋난다. η = q_actual/200 mL/min 도 6점 전부 재현된다.

압력 의존: 3→5 PSI에서 MRT 비는 0.902/0.877/0.914(평균 0.898) — 슬러리 필름두께가 얇아져
반응기 부피가 줄기 때문(논문 설명). 이 2점 사이는 선형 보간하고 **밖은 끝값 고정**(외삽 금지).

## 4. ⚠ η 채널과 TR 채널은 독립이 아니다 — 곱하면 이중 계상이다 (이 노트의 핵심 발견)

Mu 2016의 정의를 그대로 풀면:

    η = q_actual / q_total,   q_actual = V_total / MRT
    ⟹  **η · MRT = V_total / q_total**

즉 η와 MRT는 같은 실측에서 나온 **하나의 양(반응기 저류 부피 V_total)의 두 얼굴**이다. 실측 6점에서
η·MRT를 계산하면 V_total/q_total(초 단위)과 전부 2% 이내로 일치한다(DOI:10.1016/j.mee.2016.02.035 Table 3 6점, 아래 verify, 최악 +1.83%).

그래서 기존 τ가 쓰던 η 항 `(η/η_ref)^0.07`과 이번에 만들 TR 항을 **곱으로 병치하면 그루브 폭의
효과를 두 번 세게 된다**. 두 항은 실제로 서로 반대 방향으로 움직인다 — 그루브 폭 300→600 μm(3 PSI,
30 s 폴리시)에서 η 항은 +2.15%, TR 항은 −1.15%. 부호가 갈리는 이유가 바로 V_total이 η의 분자이면서
MRT의 분자이기 때문이다. 서로 상쇄하는 것처럼 보이는 순증 +0.98%는 물리가 아니라 **같은 변수를
두 지표로 두 번 센 잔차**다.

**판정(EVIDENCE-RULES 근거 서열 적용) — TR 채널 채택, η 채널 제거:**

| | η 채널 | TR 채널 |
|---|---|---|
| 결합 지수의 출처 | Prasad 2013 **기공률** 실험에서 역산(0.07)해 **그루브 축에 교차 대입** | Philipossian 2004 **ILD oxide + 콜로이달 실리카** 직접 실측, TR→Preston 상수 2점 폐형식 |
| 등급 | **E4**(타계 전이 유도) | **E2**(대상계 폐형식 유도) |
| 대상계 일치 | 축이 다름(기공률→그루브) | 일치(ILD oxide CMP) |

E2 > E4이므로 **TR 채널을 채택하고 η 항은 τ에서 뺀다**. "상반된 두 지수를 평균내지 마라"는 규칙의
자매 규칙 — 서로 종속인 두 지표를 곱하지도 마라. 기공률(porosity) 항은 Prasad 2013이 **기공률 축에서
직접** 측정한 것이라 교차 대입이 아니며 τ에 그대로 남는다.

이 교체의 부수 효과: τ의 "가장 약한 고리"였던 교차대입 지수 0.07이 τ 값에서 사라지므로, τ의
confidence 하한이 `unverified`에 묶일 이유가 없어진다(§9 참조).

## 4-1. 방향 검증 — 독립 실측이 TR 방향을 지지한다 (η 방향은 정량 근거 없음)

η 항을 빼고 TR 항만 남기면 모델의 **그루브 폭 → MRR 방향이 뒤집힌다**(기존: 600 μm 정점,
교체 후: 폭이 넓을수록 MRR 감소). 이건 큰 변경이라 제3의 독립 문헌으로 방향을 확인했다.

**지지(TR 방향과 일치):** Kao, Y.-C. / Lu, C.-H., "Analyses and experimental confirmation of removal
performance of silicon oxide film in the chemical–mechanical polishing (CMP) process with pattern
geometry of concentric groove pads", Wear 271 (2011) 1181–1189, DOI: 10.1016/j.wear.2010.10.057
(원문 확보 `papers/kao2011-wear-concentric-groove-pad-oxide.pdf`). 본문:

> "The removed thickness of silicon oxide films increased with **decreasing** width and depth of
> grooves... They also indicated that the removal rate was **reduced by increasing the groove width**
> such that it finally approached the result of a non-grooved pad, which is the same as our findings."

Kao 2011은 W=0.7/1.0/1.2 mm 콘센트릭 그루브 실측+모델이고, 최적 조건을 W=1 mm에서 3100 Å/min으로
보고한다. Mu/Philipossian과 **다른 연구그룹·다른 장비·다른 기법**인데 같은 방향이다 (**E3**).

**반대(η 방향):** Hong 2012(IJPEM 13(2) 305, Brain Korea 21) "A wider groove with a small pitch has a
higher slurry-carrying capability... which also contributed to a higher COF and finally a higher MRR."
그러나 이 논문은 MRR-그루브폭 수치를 **그림(Fig.7)으로만** 제시하고 표·본문 숫자가 없어 배수를 낼 수
없다. 또 W=2 mm 급으로 Mu/Kao 범위(0.3~1.2 mm) 밖이다 (**E3이지만 정량 부적격**).

**판정:** 정량 대조가 가능한 두 독립 실측(Philipossian 2004 + Mu 2016 조합, Kao 2011)이 같은 방향으로
수렴하고, 반대 방향 주장은 정량값이 없다. TR 방향을 채택한다. ⚠ 다만 이 방향이 **모든 그루브 폭 범위에서
성립한다고 주장하지 않는다** — 확인된 구간은 0.3~1.2 mm다. 그보다 넓으면 Hong 2012의 레짐일 수 있다.

## 5. 새로 도출한 지식 — τ가 `time_s`에 의존한다

기존 엔진에서 `Recipe.time_s`는 총 제거량을 선형으로 스케일할 뿐 **MRR 자체에는 영향이 없었다**.
TR = MRT/t_polish 이므로 **폴리시 시간이 짧을수록 TR이 커져 순간 MRR(Preston 상수)이 떨어진다**는
것이 이 노트가 새로 만드는 배선이다. 기본 조건(W=600 μm, 3 PSI, MRT 10.6 s)에서 30 s 폴리시는
TR=0.353 → f_TR=0.919, 60 s는 TR=0.177 → f_TR=0.959. 즉 **폴리시 시간을 60 s→30 s로 반 토막 내면
평균 MRR이 약 4.2% 더 떨어진다** (총 제거량은 선형 반감에 더해 이만큼 추가 손실). 이 비선형은
지금까지 모델에 없었다.

⚠ 적용 범위: Philipossian 2004의 TR 효과는 **폴리시 전에 물이 계면에 있다가 슬러리로 치환되는
공정**에서 측정됐다(논문: 린스 스텝을 뺀 조건이 TR=0 데이터점). 슬러리가 이미 정상상태로 깔린 채
시작하는 공정에서는 이 손실이 없다. 그래서 코드는 **기준 조건 대비 배수**로만 쓰고(기준에서 정확히
1.0), 절대 손실률을 주장하지 않는다.

## 6. 미검증·한계

- a=0.2301의 **곡률**: 2점 유도라 선형 가정 자체는 논문 서술("decreases steadily", Fig.12)에 의존. **미검증**.
- MRT의 **유량·속도 의존**: Philipossian 2003/2004가 유량·상대속도 의존을 보고하지만(2배 유량 감소 →
  η 약 25% 증가), 그루브 폭과 결합된 MRT 표는 Mu 2016의 200 mL/min 고정 조건뿐이다. 유량 축은
  이번 단원에서 τ에 **넣지 않는다**(근거 부족) — **미검증**, 후속 과제.
- MRT 표는 IC1000 콘센트릭 그루브 200 mm 한정. 다른 패드 계열 전이는 **미검증**.
- η 채널 지수 0.07은 §4에서 **제거**한다(TR과 종속·등급 열위). η→MRR 직접 실측은 코퍼스에 여전히 없다.
- 기공률 항(Prasad 2013, `porosity_transport_floor_pct=360`)은 **남긴다** — 기공률 축에서 직접 측정한
  것이라 교차 대입이 아니고, TR/η와 종속 관계도 없다(다른 실험·다른 패드).

## 9. τ confidence 등급 재판정

기존 코드가 τ 등급을 `tau_exponent_confidence`(=`unverified`)로 하한한 이유는 docstring에 명시돼 있다:
"결합 지수(tau_mrr_exponent=0.07)가 기공률 실험에서 역산해 그루브 축에 교차 대입한 값이라 크기를
문헌이 보증하지 않는다". §4에서 그 지수를 제거하면 이 근거가 사라진다. 교체 후 τ의 구성 요소는:

| 항 | 값의 출처 | 등급 |
|---|---|---|
| turnover | Philipossian 2004 DOI:10.1149/1.1731539 ILD oxide 실측 2점 폐형식(a=0.2301) + Mu 2016 DOI:10.1016/j.mee.2016.02.035 MRT 실측 6점 | E2 |
| porosity | Prasad 2013 DOI:10.1557/jmr.2013.173 기공률 축 직접 실측 2점(15/45% → RR +8%) | E2 |
| 드라이버(groove_width_um·pad_porosity_pct) | 팩 선언, 기존 등급 | literature |

세 요소가 모두 **대상계 실측 또는 그 축의 직접 실측**이므로 τ 등급은 `literature`가 맞다.
`verified`로 올리지 않는 이유: a의 곡률이 2점 유도라 미검증이고(§6), MRT 표가 IC1000 200 mm 한정이다.

## 7. 재현 (verify)

```python verify
# Mu 2016 MEE Table 3 내부 무결성 + Philipossian 2004 TR 기울기 + 두 채널 상쇄
tab = {3: {300: (9.2, 3.04, 19.8, 0.099), 600: (10.6, 4.72, 26.7, 0.134),
           900: (13.9, 5.91, 26.1, 0.128)},
       5: {300: (8.3, 2.88, 20.8, 0.106), 600: (9.3, 4.56, 29.4, 0.147),
           900: (12.7, 5.75, 27.2, 0.136)}}
Q_TOTAL = 200.0  # mL/min, Mu 2016 고정
worst = 0.0
for P, d in tab.items():
    for w, (mrt, V, q_lit, eta_lit) in d.items():
        q_calc = V / mrt * 60.0                 # cm3/s -> mL/min
        err = abs(q_calc / q_lit - 1.0)
        worst = max(worst, err)
        assert abs(q_calc / Q_TOTAL - eta_lit) < 0.006, (P, w, q_calc / Q_TOTAL, eta_lit)
# 6점 중 최악은 Pad C@3PSI 2.3% (표 반올림) — 3% 이내면 표 자체가 자기정합
assert worst < 0.03, worst

# Philipossian 2004: TR=1.13에서 370A vs TR=0에서 500A → 26% 감소
a = (1.0 - 370.0 / 500.0) / 1.13
assert abs(a - 0.2301) < 0.0005, a
assert abs((1.0 - a * 1.13) - 0.740) < 1e-9      # 문헌 370/500 재현
assert abs((1.0 - 370.0 / 500.0) - 0.26) < 1e-9  # DOI:10.1149/1.1731539 본문 "26% reduction"

def f_TR(mrt, t):
    return 1.0 - a * (mrt / t)

# §4 종속성 — eta * MRT == V_total / q_total (6점 전부 2% 이내)
worst_dep = 0.0
for P, d in tab.items():
    for w, (mrt, V, q_lit, eta_lit) in d.items():
        lhs = eta_lit * mrt
        rhs = V / Q_TOTAL * 60.0
        worst_dep = max(worst_dep, abs(lhs / rhs - 1.0))
assert worst_dep < 0.02, worst_dep

# §4 두 채널 반대부호 — 그루브폭 300->600 um, 3 PSI, 30 s
eta_gain = (0.134 / 0.099) ** 0.07               # 제거 대상인 기존 tau 지수
tr_loss = f_TR(10.6, 30.0) / f_TR(9.2, 30.0)
assert eta_gain > 1.0 and tr_loss < 1.0, (eta_gain, tr_loss)
assert abs(eta_gain - 1.0215) < 0.001, eta_gain
assert abs(tr_loss - 0.98847) < 0.001, tr_loss

# §5 폴리시 시간 60->30 s (기준 W=600, 3 PSI, MRT 10.6 s)
drop = f_TR(10.6, 30.0) / f_TR(10.6, 60.0)
assert abs(drop - 0.95757) < 0.001, drop         # 추가 4.2% 손실
print("PASS worst_q_err=%.4f a=%.4f drop30s=%.4f" % (worst, a, drop))
```

## 8. 구현 요청 (소프트웨어 부문)

- **무엇을**: `sim/factors.py::_f_tau`에 `turnover` 항 추가. MRT(W, P)는 Mu 2016 6점 2-D 보간(폭 선형,
  압력 3~5 PSI 선형, 밖은 끝값 고정), `f_TR = (1 − a·MRT/t) / (1 − a·MRT_ref/t_ref)`, a=0.2301,
  하한 클램프 0.05. 기준 조건에서 정확히 1.0.
- **근거 노트**: 이 노트 §2·§3·§7.
- **검증 문헌값**(DOI:10.1149/1.1731539 본문 370/500 Å, DOI:10.1016/j.mee.2016.02.035 Table 3):
  TR=1.13 → 0.740; 60→30 s 배수 0.9576; 300→600 μm TR 채널 0.9885.
- **우선순위**: 높음 — `Recipe.time_s`가 MRR에 영향을 주지 않던 구조적 결측을 메운다.
