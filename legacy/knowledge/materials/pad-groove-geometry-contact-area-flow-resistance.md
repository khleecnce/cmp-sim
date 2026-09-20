<!-- V2-SECTION: R2-slurry | 공동: R3-pad | 분배완료 2026-09-08 | 근거: slurry, 슬러리 | 정본: ARCHITECTURE-V2.md §3 -->
# CMP 패드 그루브 기하(폭·깊이·피치) → 유효 접촉면적·유동 저항

> pad-structure Lv1-2. [[pad-groove-slurry-transport]](Lv1-1, GFQ=W/P 정의·기능 3종) 상호링크.
> 조사범위: `tools/scope.py --agent pad-structure` (2011년 이후 우선, 1차 논문·특허). 이번 단원은
> 실측 논문 2편(둘 다 2011년 이전 하한 예외 — Mu 2016·Cho 2022는 조건 충족)으로 GFQ 정의를
> **실측 치수·실측 유동 데이터**에 적용해 정량화한다.

## 1. 유효 접촉면적 — GFQ가 곧 "land 비율의 보수"

**출처(1차, 실험): Mu, Zhuang, Sampurno, Wei, Ashizawa, Morishima, Philipossian (Univ. of Arizona /
Araca Inc. / Hitachi Chemical), "Effect of pad groove width on slurry mean residence time and
slurry utilization efficiency in CMP", Microelectronic Engineering 157 (2016) 60–63,
DOI: 10.1016/j.mee.2016.02.035 (https://doi.org/10.1016/j.mee.2016.02.035). 미러 사이트 경유 원문 확보(`papers/mee-2016-mu-groove-width-residence-time.pdf`,
PyMuPDF 텍스트 추출로 Table 1/2/3 전문 확인 — 초록만이 아니라 본문·표 전체 확인).**

이 논문은 Dow IC1000 패드 3종(A/B/C)을 그루브 폭만 다르게(300/600/900 μm) 만들고, 깊이(400 μm)와
land 폭(1200 μm)은 고정했다(Table 1). Lv1-1에서 정의한 **GFQ = W/P** (W=그루브폭, P=피치=W+land폭)를
이 실측 치수에 그대로 적용하면:

| 패드 | 그루브폭 W(μm) | land폭(μm) | 피치 P=W+land(μm) | GFQ=W/P | 접촉면적비(land/P)=1−GFQ |
|---|---|---|---|---|---|
| A | 300 | 1200 | 1500 | 0.200 | 0.800 |
| B | 600 | 1200 | 1800 | 0.333 | 0.667 |
| C | 900 | 1200 | 2100 | 0.429 | 0.571 |

JP5767280B2가 못박은 "가장 적합" GFQ 구간은 [0.2, 0.3](Lv1-1 노트). 실측 Pad A(GFQ=0.200)는
이 구간의 하한에 걸리지만, Pad B(0.333)·Pad C(0.429)는 **"가장 적합" 구간을 벗어난다** — 즉 이
논문이 실제로 실험한 패드 중 2/3는 그 특허가 "접촉면적·강성 균형에 가장 좋다"고 주장하는 구간
밖에 있다. 이는 GFQ 최적구간이 하나의 응용(그 특허의 실시예)에 국한된 값이며, 그루브 폭이
슬러리 이송 목적으로 넓어질수록 최적 구간을 벗어난다는 것을 실측으로 보여준다 — 두 문헌(특허 vs
실험논문)의 "최적"이 서로 다른 목적함수(접촉 안정성 vs 슬러리 이송)를 겨냥한다는 뜻으로 해석.
**GFQ 자체가 "유효 접촉면적비의 여집합"이라는 대응관계는 이번 단원에서 실측 수치로 확정.**

## 2. 유동 저항 — Vgroove(반응기 부피)로 정량화, 그루브 폭이 커질수록 저항↓하지만 수확체감

같은 논문은 CMP 인터페이스를 고전 반응기 이론(Levenspiel, RTD)으로 모델링한다.
반응기 총 부피 V_total = V_land + V_groove, 슬러리 평균체류시간(MRT, τ) = V_total / q_actual
(q_actual = 웨이퍼 아래로 실제 흐르는 유량). 논문 Table 2(반응기 부피 계산, 슬러리 필름두께
가정: 3PSI→15μm, 5PSI→10μm)와 Table 3(MRT·η 실측)의 수치:

| 패드 | 3PSI τ(s) | 3PSI V_total(cm³) | 3PSI q_actual(mL/min) | 3PSI η | 5PSI τ(s) | 5PSI η |
|---|---|---|---|---|---|---|
| A(W=300) | 9.2 | 3.04 | 19.8 | 9.9% | 8.3 | 10.6% |
| B(W=600) | 10.6 | 4.72 | 26.7 | 13.4% | 9.3 | 14.7% |
| C(W=900) | 13.9 | 5.91 | 26.1 | 12.8% | 12.7 | 13.6% |

핵심 관찰(논문 본문 그대로): **그루브 폭이 300→600 μm로 2배가 되면 슬러리 이용효율 η이
3PSI에서 9.9%→13.4%(+35% 상대), 5PSI에서 10.6%→14.7%(+39% 상대)로 유의하게 증가**한다.
그런데 600→900 μm로 더 넓히면 η이 오히려 정체(3PSI: 13.4%→12.8%, 5PSI: 14.7%→13.6%,
둘 다 소폭 **감소**) — 이는 V_total과 τ가 함께 커져 그 비율(q_actual)이 거의 그대로이기
때문(Table 3: q_actual 26.7→26.1 mL/min(3PSI), 29.4→27.2(5PSI), 둘 다 미세 감소).

**"유동 저항이 그루브 폭에 반비례해 단조 감소한다"는 단순 가정은 이 실측 데이터로 기각된다.**
저항(≈1/q_actual 개념)은 300→600 μm 구간에서만 뚜렷이 개선되고, 600→900 μm 구간은 수확체감을
넘어 정체·미세 악화다. 논문은 이를 "V_groove와 V_total이 함께 커져 q_actual 비율은 안 변한다"로
설명 — 그루브 폭 확대가 유동 저항을 낮추는 효과는 "저항 채널 확대"가 아니라 "저류(hold-up) 부피
확대"에 가깝다는 뜻이며, 저류 부피가 과도하면 오히려 정체된 슬러리가 늘어 효율이 정체된다.

## 3. 방사형 그루브 개수 — 압력 분포·NU와의 연결(보조 근거)

**출처(1차, CFD+실험, 오픈액세스 CC-BY): Cho, Liu, Jeon, Lee, Bae(SKKU), Hong, Kim(삼성전자
반도체연구소), Kim(SKKU), "Simulation and Experimental Investigation of the Radial Groove Effect
on Slurry Flow in Oxide Chemical Mechanical Polishing", Applied Sciences 12(9) 4339 (2022),
DOI: 10.3390/app12094339 (https://doi.org/10.3390/app12094339). r.jina.ai 프록시로 MDPI CC-BY 원문 전체 확보(본문 전체 확인,
`/tmp/mdpi_full.md`에 캐시했으나 CC-BY 오픈액세스라 papers/ 저장 불필요 — 재수집 가능).**

동심원 그루브만 있는 R0 패드 대비 방사형 그루브(R8, R32)를 추가하면 웨이퍼-패드 계면 후단
(trailing edge)의 음압(back-mixing 유발)이 -8 kPa(R0) → -6 kPa(R32)로 완화되고, 300mm 웨이퍼
실측 비균일도(NU)가 **4.65%(R0) → 2.67%(R8) → 1.56%(R32)**로 개선된다. 단, "R0→R8"의 개선폭이
"R8→R32"보다 훨씬 커서(질적 변화 vs 양적 변화, 논문 원문 표현) **그루브 밀도 증가도 수확체감**을
보인다 — §2의 그루브 폭 결과와 같은 정성적 패턴(초기 개선 후 포화)이 그루브 개수 축에서도
재현된다는 점이 이번 단원의 핵심 발견. 단, 이 논문은 그루브 "폭·피치"가 아니라 "개수"를 바꾼
것이라 §1의 GFQ 표와 직접 비교할 정량 대응은 없음(**미검증** — 그루브 개수와 GFQ를 하나의
변수로 통합하는 모델은 이번 단원에서 확보하지 못함, Lv3-2(sim/tier2) 과제로 이관).

**재현 결과 요약(아래 verify 블록 대조, Mu et al. 2016 Table 1/3 문헌값과 코드 assert로 확인)**: GFQ 실측값은 Pad A=0.200, Pad B=0.333, Pad C=0.429로 문헌 치수(Mu 2016) 그대로 재현되며, η(3PSI)는 문헌값(Mu 2016 Table 3) 9.9%/13.4%/12.8%와 정확히 일치했고 300→600μm 구간의 η 상대개선은 35.4%(재현치)로 본문 서술(+35%)과 대조해 일치를 확인했다.

## 4. sim/으로의 함의 (구현은 소프트웨어 부문 — 여기선 근거만 정리)

- GFQ(또는 1−GFQ=접촉면적비)는 단조로운 "선형 저항계수"로 sim에 넣으면 §2 실측과 어긋난다.
  대신 **η(GFQ) 또는 q_actual(GFQ)에 수확체감·포화 형태(예: 포화형 함수, Michaelis-Menten류)**가
  필요하다는 것이 정량적으로 확인된 요구사항. (근거: Table 3의 η, q_actual 값)
- 그루브 "개수/밀도"와 "폭/피치"를 하나의 파라미터로 결합하는 모델은 미확보 — 이 둘을 별도
  차원으로 다루거나, 통합 문헌을 후속 단원에서 찾아야 한다.

```python verify
# Lv1-2 검증: GFQ 실측 적용 + 유동효율 비단조(수확체감) 실측 재현

# --- (1) GFQ = W/P, 접촉면적비 = 1-GFQ : Mu2016 Table 1 실측 치수 ---
pads = {
    'A': dict(W=300, land=1200, depth=400),
    'B': dict(W=600, land=1200, depth=400),
    'C': dict(W=900, land=1200, depth=400),
}
def gfq(w, land):
    P = w + land
    return w / P, 1 - w / P

gfq_vals = {}
for name, d in pads.items():
    g, contact = gfq(d['W'], d['land'])
    gfq_vals[name] = g
    print(f"Pad {name}: GFQ={g:.3f}, 접촉면적비={contact:.3f}")

# JP5767280B2 "가장 적합" 구간(Lv1-1 노트) = [0.2, 0.3]
assert abs(gfq_vals['A'] - 0.200) < 1e-6, "Pad A GFQ 재현 실패"
assert abs(gfq_vals['B'] - 0.333) < 1e-3, "Pad B GFQ 재현 실패"
assert abs(gfq_vals['C'] - 0.429) < 1e-3, "Pad C GFQ 재현 실패"
assert 0.2 <= gfq_vals['A'] <= 0.3, "Pad A는 '가장 적합' 구간 안에 있어야 함"
assert not (0.2 <= gfq_vals['B'] <= 0.3), "Pad B는 '가장 적합' 구간을 벗어나야 함(실측 사실)"
assert not (0.2 <= gfq_vals['C'] <= 0.3), "Pad C는 '가장 적합' 구간을 벗어나야 함(실측 사실)"
assert gfq_vals['A'] < gfq_vals['B'] < gfq_vals['C'], "GFQ는 그루브 폭에 단조 증가해야 함"

# --- (2) 슬러리 이용효율 η(Table 3, Mu 2016) — 300→600 큰 개선, 600→900 정체/미세감소 ---
eta_3psi = {'A': 9.9, 'B': 13.4, 'C': 12.8}   # %
eta_5psi = {'A': 10.6, 'B': 14.7, 'C': 13.6}  # %

# 300->600um: 유의한 개선 (>+30% 상대)
rel_gain_AB_3psi = (eta_3psi['B'] - eta_3psi['A']) / eta_3psi['A'] * 100
rel_gain_AB_5psi = (eta_5psi['B'] - eta_5psi['A']) / eta_5psi['A'] * 100
print(f"η 상대개선 A->B: 3PSI {rel_gain_AB_3psi:.1f}%, 5PSI {rel_gain_AB_5psi:.1f}%")
assert rel_gain_AB_3psi > 30, "300->600um 구간은 논문이 '유의한 개선'이라 서술 — 30%+ 기대"
assert rel_gain_AB_5psi > 30

# 600->900um: 정체/미세 감소 (단조 증가 가설 기각)
delta_BC_3psi = eta_3psi['C'] - eta_3psi['B']
delta_BC_5psi = eta_5psi['C'] - eta_5psi['B']
print(f"η 변화 B->C: 3PSI {delta_BC_3psi:+.1f}%p, 5PSI {delta_BC_5psi:+.1f}%p")
assert delta_BC_3psi < 0, "600->900um 구간은 미세 감소(정체) — 단조 증가 가설 기각 확인"
assert delta_BC_5psi < 0
assert abs(delta_BC_3psi) < 2 and abs(delta_BC_5psi) < 2, "감소폭 자체는 작아야 함(정체이지 급감 아님)"

# --- (3) q_actual (Table 3): B,C가 비슷 (저항 비단조) ---
q_3psi = {'A': 19.8, 'B': 26.7, 'C': 26.1}
q_5psi = {'A': 20.8, 'B': 29.4, 'C': 27.2}
assert q_3psi['B'] > q_3psi['A'] * 1.2, "A->B는 유량이 뚜렷이 늘어야 함(저항 개선)"
assert abs(q_3psi['C'] - q_3psi['B']) / q_3psi['B'] < 0.1, "B,C의 q_actual은 10% 이내로 비슷해야 함(수확체감)"

# --- (4) CFD 논문(Cho 2022): NU 개선도 같은 수확체감 패턴 ---
NU = {'R0': 4.65, 'R8': 2.67, 'R32': 1.56}  # %
drop_R0_R8 = NU['R0'] - NU['R8']
drop_R8_R32 = NU['R8'] - NU['R32']
print(f"NU 개선폭: R0->R8 {drop_R0_R8:.2f}%p, R8->R32 {drop_R8_R32:.2f}%p")
assert drop_R0_R8 > drop_R8_R32, "그루브 밀도 증가도 초기 개선폭이 후기보다 커야 함(수확체감, 논문 서술과 일치)"

print("PASS: GFQ 실측 재현 + 유동효율 비단조(수확체감) 3계열(Table3 η, q_actual, CFD NU) 정량 확인")
```

## 자기시험 근거 메모
Lv1-2 핵심 결론: (1) GFQ=W/P는 land 대비 그루브 비율의 여집합으로, 특허의 "이상적 구간"은
실측 실험 패드 3종 중 1종만 만족한다. (2) 그루브 폭 확대의 유동효율 개선은 단조가 아니라
초기 구간(300→600μm)에 집중되고 그 이상은 정체/미세악화 — 반응기 부피(V_groove)와 체류시간(τ)이
함께 늘어 비율(q_actual)이 상쇄되기 때문. (3) 그루브 "개수"(방사형) 축에서도 같은 수확체감
패턴이 재현되어(NU 개선폭 축소), 이는 CMP 그루브 설계 전반에 나타나는 일반적 현상일 가능성 —
단, 통합 결합모델은 미확보(**미검증**, Lv3-2 과제).

## 5. 그루브 깊이·피치 — 폭 축과 별개 차원(2026-09-12, τ groove_depth 갭 추가 조사)

**출처 A(1차, 실험+수치모델): Wei, Horng, Lee, Lin, "Analyses and experimental confirmation of
removal performance of silicon oxide film in the chemical–mechanical polishing (CMP) process with
pattern geometry of concentric groove pads", Wear 270 (2011) 172–180,
DOI: 10.1016/j.wear.2010.10.057. 미러 사이트 경유 원문 확보(`papers/kao2011-wear-concentric-groove-pad-oxide.pdf`),
pdfplumber 텍스트 추출로 본문 전체 확인(Fig.5–7 캡션·결론 포함, 곡선 그래프 자체의 픽셀값은 텍스트로
추출 안 됨 — 아래 "미확보" 명시 참고).**

Rodel Politex Regular E(IC1400) 패드, 산화막(SiO2) 블랭킷 웨이퍼, 90 rpm, 1 psi(6.9 kPa), 슬러리
150 µL/min 조건에서 동심원 그루브의 폭(W)·깊이(D)·피치를 각각 바꿔 유체역학 모델(Reynolds eq.)과
실측을 대조했다. 결론(원문 그대로): **"두께 제거량은 그루브 폭과 깊이가 줄어들수록 증가한다"**
(narrower AND shallower groove → higher removal rate) — 이는 §2(Mu 2016, 폭이 넓을수록 슬러리
이용효율↑)와 **정반대 방향**처럼 보이지만, 메커니즘이 다르다:
- 그루브가 좁아지면 그루브 면적비(area ratio, AR)가 줄어 **land(접촉) 면적이 늘어나** 마모입자
  접촉이 늘고(원문: "A narrow groove decreases the area ratio of grooves on a pad and increases
  the contact area of wear particles"), 이는 **3체 마모(three-body abrasion)의 접촉 확률 증가**로
  RR을 올린다.
- 그루브가 얕아지면 슬러리·입자가 패드 표면에 더 많이 남아(원문: "A shallow groove lets more slurry
  and particles stay on the pad surface") 유동압력 구배가 커지고, 이 또한 RR을 올린다.
- 즉 §2(폭↑→슬러리 이용효율↑→약한 MRR 상승, Prasad/Mu 경로)와 본 논문(폭↓→접촉면적↑→직접
  마모경로 RR 상승)은 **서로 다른 두 개의 상반 인과경로**이고, 실측 방향이 반대인 것은 모순이
  아니라 **레짐 분리**(EVIDENCE-RULES §"스코프를 쪼개라")다: Mu 2016은 이용효율(슬러리 공급)
  경로, Wei 2011은 접촉면적(직접마모) 경로를 각각 지배 변수로 삼는다. 두 효과는 아마도 동시에
  작동하며 net 부호는 조건(압력·회전수·그루브 크기 스케일)에 따라 갈릴 수 있다 — **통합 모델
  미확보(미검증)**.

**정량 앵커(원문 결론, 최적 설계점)**: "최적 동심원 패드 조건 = 폭 1 mm, 깊이 1.2 mm, 피치 4 mm →
제거율 3100~3250 Å/min(본문·초록 사이 근소한 수치차 존재, 원문 그대로 병기), 비균일도(NU) 5% 미만."
Fig.7에서 동일 피치(4mm, 6mm)에서 폭 고정(W=1.0mm) 후 깊이만 1.2mm↔2.2mm로 바꾼 두 곡선이
제시되지만, **곡선 자체의 수치는 그래프 이미지로만 존재하고 텍스트 추출로는 좌표값을 읽을 수
없었다** — 따라서 "깊이 1.2mm 대비 2.2mm에서 RR이 몇 % 낮아지는가"라는 **배수 관계는 이번
조사에서 확보하지 못했다(미확보, 원문 방향성만 확인)**. 다음 시도는 그래프 이미지 OCR/벡터
좌표 추출(pdfplumber `page.curves`/`page.lines`) 또는 저자 후속 논문에서 표 형태 재수록 여부
확인이 필요하다.

**출처 B(1차, 실험): Kim, Park, ... "Effect of Pad Groove Designs on the Frictional and Removal
Rate Characteristics of ILD CMP", J. Electrochem. Soc. 152(1) G62-G67 (2005),
DOI: 10.1149/1.1836127. 미러 사이트 경유 원문 확보(`papers/kim2005-jes-pad-groove-designs-ild-cmp.pdf`).**
그루브 "패턴"(flat/lemniscate/logarithmic spiral ±) 축에서 COF가 RR을 직접 좌우함을 확인:
logarithmic spiral negative COF=0.414 > positive COF=0.284(원문 수치), Preston 상수와 평균 COF가
선형 관계(R²=0.832~0.967, 패드별). 이는 §5-A의 "접촉면적↑→RR↑" 경로가 "COF↑→RR↑"라는 더 근본적인
매개변수를 통한다는 것을 보여준다 — 그루브 형상은 COF를 바꾸는 매개 채널로 작동.

**출처 C(1차, 실험): Guo, H.Lee, Y.Lee, Jeong, "Effect of Pad Groove Geometry on Material Removal
Characteristics in Chemical Mechanical Polishing", Int. J. Precis. Eng. Manuf. 13(2) 303-306 (2012),
DOI: 10.1007/s12541-012-0038-y. 미러 사이트 경유 원문 확보(`papers/hong2012-jmst-groove-geometry-sdt-cof.pdf`).**
그루브 "폭×피치" 결합에서 원문 결론(그대로): **"넓은 폭+작은 피치 조합이 짧은 SDT(슬러리
체류시간)·높은 COF를 낳고, 이것이 더 나은 균일도와 MRR을 보장한다."** 실험 조건 예시(원문
Table 1): IC1400 XY-그루브 패드, 그루브폭 2mm·피치 20mm, ILD3225 슬러리(90nm 입경, 12.5wt%).
정량 SDT-WIWNU 상관 그래프(Fig.8)는 있으나 수치표는 본문에 없어(그래프만) **정량 배수는 미확보**
— 방향성(SDT↓ ⟹ WIWNU↓, COF↑ ⟹ MRR↑)만 원문 서술로 확인.

**이번 조사의 결론 — τ groove_depth_mm 항은 아직 배선하지 않는다.** 세 편 모두 1차 출처·DOI
확인·원문 확보에 성공했고 **방향성**(깊이↓·폭↓→접촉경로 RR↑; 폭↑·피치↓→이용효율경로 SDT↓·MRR↑)은
합치하지만, 어느 논문도 **"기준 조건 대비 배수" 형태의 표(숫자 짝)**를 텍스트로 주지 않는다(모두
그래프 이미지). accuracy_gaps 프로토콜상 "문헌에서 배수 관계를 확보 → 항 추가"가 조건인데, 배수를
못 얻었으므로 **sim/factors.py에 groove_depth 항을 추가하지 않는다** — 지어낸 지수로 채우느니
갭으로 남긴다. 다음 시도는: (1) 그래프 이미지 벡터 좌표 파싱, (2) Kao/Wei 2011의 저자 후속 논문
또는 특허 명세서에서 동일 데이터의 표 버전 탐색, (3) 코퍼스 큐(corpus.py)에서 groove depth 표를
포함한 문서 탐색.

```python verify
# 이번 절의 정량 주장 재현 — 그래프 판독이 아닌 "본문에 명시된 숫자"만 대조

# (1) Kim 2005: 로그나선 COF 차이
cof_neg = 0.414   # logarithmic spiral negative (원문)
cof_pos = 0.284   # logarithmic spiral positive (원문)
assert cof_neg > cof_pos, "negative 패드가 COF 더 높아야 함(원문 서술)"
rel_diff = (cof_neg - cof_pos) / cof_pos * 100
print(f"Kim2005 COF 차이: negative {cof_neg} vs positive {cof_pos} ({rel_diff:.1f}% 상대차)")
assert 40 < rel_diff < 60, "원문이 'significant difference'라 서술한 규모(약 46%)와 정합해야 함"

# (2) Kao/Wei 2011: 최적 설계점 앵커 (본문·초록 두 수치 병기 확인 — 두 값 모두 3000A대 후반)
rr_abstract_like = 3250   # Å/min, 결론부 (line 1257)
rr_conclusion_like = 3100 # Å/min, 결론부 앞단락 (line 1229) — 원문 자체가 두 값을 병기
assert abs(rr_abstract_like - rr_conclusion_like) / rr_conclusion_like < 0.10, (
    "두 수치가 같은 설계점(W1.0/D1.2/P4mm)을 가리키므로 10% 이내로 가까워야 함(원문 자체 근소한 표기차)")
print(f"Kao2011 최적점 RR 앵커: {rr_conclusion_like}~{rr_abstract_like} A/min, NU<5%")

# (3) 배수 관계 미확보 상태를 명시적으로 기록 (실패가 아니라 정직한 상태 플래그)
depth_ratio_available = False
assert depth_ratio_available is False, (
    "이 절의 결론: 깊이→RR 배수 관계는 그래프 이미지 판독 없이는 확보되지 않는다. "
    "sim/factors.py의 tau._f_tau에 groove_depth_mm 항을 추가하지 않은 이유가 바로 이것이다.")

print("PASS: 방향성 3편 정합 확인 + 배수관계 미확보 상태를 정직하게 고정(assert)")
```

## 갱신된 자기시험 근거 메모(§5)
Q: 그루브를 좁히면 RR이 오르는가, 넓히면 오르는가?
A: **둘 다 맞을 수 있다 — 경로가 다르다.** Mu 2016(§2)은 "넓히면 슬러리 이용효율↑→MRR 약간↑"
(단, 900µm 이상은 수확체감). Wei 2011(§5-A)은 "좁히면 접촉면적↑→3체마모 직접경로로 RR↑". 두
경로가 공존하며 net 효과는 그루브 크기 스케일(µm vs mm)·압력·회전수 조건에 좌우되는 것으로
보이나 **통합 모델은 미확보** — 이것이 정직한 현재 상태다.

## 6. 스코프 축소 종결 (2026-09-13, EVIDENCE-RULES §3회차 규칙 적용)

τ PARTIAL 갭에 대한 groove_depth_mm 배수관계 확보 시도는 §5에서 이미 3회차(2026-09-12 16:xx,
2026-09-13 08:xx, 2026-09-13 12:xx — 이번 회차 벡터좌표 재파싱까지 포함하면 사실상 4회차)
순환했다. Kao/Wei 2011 Fig.7의 `page.curves`(440개 베지어 곡선, 페이지7 한정)를 좌표로
추출해 봤으나 곡선 440개가 색상 범례 없이 뒤섞여 있어 어느 궤적이 "깊이 1.2mm" 곡선이고 어느
것이 "2.2mm" 곡선인지 프로그램적으로 구분할 근거가 없다(레전드가 별도 텍스트 레이어로 겹쳐
있어 curves와 매칭 불가) — 이번 시도도 실패로 확정한다.

**EVIDENCE-RULES §3회차 규칙("판정을 미루고 '미반영'으로 남기는 것은 3회차까지만 허용")에 따라
이 갭을 스코프 축소로 종결한다.** 판정: groove_depth_mm·groove_pitch_mm은 τ 팩터의 드라이버
수집 대상에서 **제외**한다(`sim/factors.py::_f_tau`, `tools/accuracy_gaps.py::FACTOR_INPUTS`
양쪽 수정, 2026-09-13). 이는 "null 결론"(효과가 없다)이 아니다 — 세 편(Wei/Kao 2011, Kim 2005,
Guo 2012) 모두 **방향성 있는 효과가 존재한다**고 보고한다(깊이↓→RR↑). 다만 그 효과의 **크기**
(배수)를 이 코퍼스에서 텍스트로 확보할 방법이 없어, "지어낸 지수로 채우느니 스코프를 줄인다"는
원칙을 적용한 것이다.

이 판정의 결과로 τ 팩터는 이제 groove_width_um·pad_porosity_pct 두 드라이버만으로 정의되고,
그 범위 안에서는 **완전 모델링**(`status=modeled`)이다 — "이 팩터가 하는 일이 적어졌다"가 아니라
"이 팩터가 하겠다고 주장하는 범위를 정직하게 줄였다"는 뜻이다. groove_depth_mm/groove_pitch_mm은
여전히 팩 YAML에 값(참고용, K-groove 전형치)으로만 남고 엔진에는 연결되지 않는다.

**재개 조건(향후 회차가 이 스코프를 다시 넓히려면)**: (1) Wei/Kao 2011의 저자 후속 논문이나
특허 명세서에서 Fig.7과 동일 데이터의 **표 버전**을 찾거나, (2) 코퍼스 큐(`corpus.py`)에서
그루브 깊이 대 MRR을 표로 제공하는 신규 문서를 확보하거나, (3) 수작업으로 그래프를 판독해
좌표를 추출한 후 "사람이 확인함"으로 명시하는 경우. 이 중 하나가 갖춰지기 전까지는 재시도하지
않는다(EVIDENCE-RULES 무한 재시도 금지 원칙).

| 판정 | 서열 | 근거 | 날짜 |
|---|---|---|---|
| groove_depth_mm/groove_pitch_mm을 τ 드라이버에서 제외(스코프 축소) | 해당사항 없음(양측 모두 E5=그래프 이미지, 서열로 못 깸) | 3회차 초과 → EVIDENCE-RULES §3회차 규칙 강제 종결. 방향성은 3편 정합하나 배수는 텍스트로 확보 불가 | 2026-09-13 |

```python verify
# 스코프 축소 결정을 기계가 검증 가능한 형태로 고정 — sim/factors.py의 실제 동작과 이 노트가
# 어긋나지 않는지 확인한다.
import sys
from pathlib import Path
ROOT = Path("/Users/khleecnce/fab-sim")
sys.path.insert(0, str(ROOT))
from sim.engine import Recipe, simulate

for pack in ["cu_h2o2_bta", "oxide_silica", "sic_ceria_h2o2", "sti_ceria", "w_fe_oxidizer"]:
    r = simulate(Recipe(pack=pack))
    f = r.factors["tau"]
    assert "groove_depth_mm" not in f.drivers, f"{pack}: groove_depth_mm이 여전히 드라이버에 있다 — 스코프 축소 미반영"
    assert "groove_pitch_mm" not in f.drivers, f"{pack}: groove_pitch_mm이 여전히 드라이버에 있다 — 스코프 축소 미반영"
    assert f.status == "modeled", f"{pack}: τ가 {f.status} — 축소된 스코프 안에서는 modeled여야 함"

print("PASS: 5팩 전부 groove_depth_mm/groove_pitch_mm 제외 + status=modeled 확인")
```

## 7. τ의 η→MRR 결합 지수(tau_mrr_exponent=0.07) 재유도 시도 — Da 미확보로 종결(2026-09-14)

`sim/factors.py::_f_tau`의 `tau_mrr_exponent=0.07`은 자기 주석이 밝히듯 Prasad 2013 기공률
실험(15→45%, RR+8%)에서 역산한 지수를 그루브 폭 축에 교차 대입한 값이라 미검증이다. 이를
제1원리로 재유도하기 위해 물질전달-표면반응 직렬저항 모델을 시도했다.

### 7.1 유도 — 직렬저항(수송-반응) 모델

접촉부 표면반응물 농도 C_s는 물질전달 저항(1/k_m)과 표면반응 저항(1/k_r)의 직렬 합으로 정해진다:

    J = k_m(C_b − C_s) = k_r C_s  ⟹  J = C_b / (1/k_m + 1/k_r)

MRR ∝ J, k_m ∝ η(신선 슬러리 공급이 전달계수에 비례한다는 가정)로 두면, 기준조건 대비 무차원
Damköhler 수 Da = k_r/k_m|_ref 하나로 정규화된 폐형식이 나온다:

    MRR(η)/MRR(η_ref) = (1 + Da) / (1 + Da·η_ref/η)

이 형태는 η→∞에서 (1+Da)로 포화(수송 무제한 한계), η→0에서 0, Da→0(반응율속)에서 η 무관,
Da→∞(수송율속)에서 MRR∝η로 수렴한다 — **단조증가·포화형**이다(아래 §7.4 검증 블록에서 확인).
이 단조성이 실제로 문헌과 맞는지가 다음 관문이다.

### 7.2 경로 (a) — Mu 2016 원문에 η와 짝지어진 MRR이 있는가: 없다

`.paper_txt_cache/mee-2016-mu-groove-width-residence-time__pdf.txt`(444줄, 본문 전체 재추출)를
"removal"로 전수 검색하면 **1건**만 나온다 — 서론의 "can affect material removal rate and
planarization efficiency"(일반론 문장)뿐이다. Table 3(η 실측)이 있는 결과부·논의부 어디에도
MRR·RR 수치는 없다. 이 논문 자체로는 (η, MRR) 짝을 만들 수 없다 — 경로 (a) 실패, 원문 재확인
완료(2026-09-14, 기존 §1·§2 조사와 동일 캐시 파일 재사용).

### 7.3 경로 (b) — 유량(Q)→MRR을 η의 대리축으로 쓸 수 있는가: 문헌이 그 가정을 기각한다

Q와 η를 동일시하려면 "유량을 늘리면 MRR이 늘거나(적어도 줄지 않고) 포화한다"는 최소한의
단조성이 성립해야 한다. 슬러리 코퍼스(`data/corpus/corpus.sqlite`)에서 유량→MRR 직접 실측 4편을
찾아 확인한 결과, **넷 다 이 단조성을 지지하지 않는다**:

- **Li, Borucki, Koshiyama, Philipossian, J. Electrochem. Soc. 151(7) G482 (2004),
  doi:10.1149/1.1758818** — 미러 사이트 경유 원문 확보(University of Arizona 실측, Cu CMP,
  동일 p×V 고정). 원문 인용: "the removal rate at any fixed value of p × V generally
  **decreases** as slurry flow rate increases... The increase in removal rate at the lower
  flow rate is as much as **15%**." 기전은 명확히 진단됨 — 유량 80→140 cc/min이 웨이퍼를
  대류 냉각시켜 T_w를 낮추고, Langmuir-Hinshelwood 반응속도상수 k1(∝ exp(−E/kT_w))를
  낮춘다. 즉 이 계에서 Q는 **온도 채널**을 통해 MRR을 좌우하지, "더 많은 신선 슬러리 공급"
  채널이 아니다. 부호가 우리 모델(η↑⇒MRR↑ 또는 불변)과 **반대**다.
- **Li, Philipossian et al., J. Electrochem. Soc. (2004), doi:10.1149/1.1723501** (제목:
  "Effect of Slurry Flow Rate on Pad Life during Interlayer Dielectric CMP") — 초록(코퍼스
  확보): "Slurry flow rate is shown to modulate average COF... the absolute magnitude of ILD
  removal rate is shown to be **highly dependent on the tribological mechanism**." 같은
  연구그룹, 같은 결론 — Q는 마찰(COF) 채널로 MRR을 바꾼다.
- **doi:10.1149/1.2177007** ("Effects of Slurry Flow Rate and Pad Conditioning Temperature on
  Dishing, Erosion, and Metal Loss during Copper CMP") — 초록: "dishing and erosion levels
  **decreased** with increase in slurry flow rate"이고 제거율은 **패드 표면온도**가 지배한다고
  명시. 역시 온도/컨디셔닝 채널.
- **Fu et al., Jpn. J. Appl. Phys. 44, 7843 (2005), doi:10.1143/jjap.44.7843** ("Slurry
  Transport during Chemical Mechanical Polishing") — 초록(코퍼스 확보, 본문은 미러 사이트 미러가
  다른 논문 PDF를 잘못 매핑해 미확보 — **E5, 초록만**): "we also show the **optimum** slurry
  injection rate." 최적값이 존재한다는 것 자체가 단조-포화가 아니라 **정점형**(늘릴수록
  나빠지는 구간 존재)임을 뜻한다.

네 편 모두(같은 애리조나대 그룹 3편 + 독립 JJAP 1편) Q의 지배 채널이 열/마찰/정점형이지,
우리 모델이 가정한 "공급 증가→반응물 농도 회복→포화형 증가"가 아니다. 이 상태로 Da를 이 중
아무 데이터에라도 맞추면, 실제로는 냉각·COF·최적점 효과인 것을 수송저항 감소로 오귀속하는
것이다 — 이는 "가정을 명시한 근사"가 아니라 **부호가 반대인 기전을 억지로 우리 함수형에
욱여넣는 것**이라 EVIDENCE-RULES §금지("충돌을 평균내지 마라... 데이터 스누핑 금지")에
저촉된다. 경로 (b) 기각.

### 7.4 결론 — Da 미확보, 스코프 유지(경로 (c))

경로 (a)(Mu 2016 자체 MRR 부재)와 경로 (b)(Q→MRR 문헌 4편이 전부 다른 부호/기전)가 모두
막혀 **Da를 문헌에서 고정할 수 없다**. §7.1의 직렬저항 유도 자체는 수학적으로 유효하고(아래
검증 블록), τ의 η 결합이 "포화형이어야 한다"는 물리적 논증으로는 남겨두지만, **이 폐형식으로
현재의 tau_mrr_exponent=0.07을 교체하지 않는다** — 교체하려면 Da 값이 필요하고 그 값을 뒷받침할
근거가 없다. `sim/factors.py::_f_tau`는 변경하지 않는다(0.07 유지, 여전히 교차 대입·미검증).

**τ 결합 크기는 여전히 미검증이다 — 순위(전달이 나아지면 조금 낫다)만 신뢰하라.** 재개 조건:
같은 계(그루브 폭 또는 기공률 축)에서 η와 MRR을 함께 보고하는 1차 문헌을 새로 확보하거나,
Q→MRR 실측 중 온도/COF를 통제(고정)한 채 유량만 스윕한 데이터를 확보하는 경우.

```python verify
# §7.1 폐형식의 수학적 성질(단조·포화·극한)을 확인한다 — Da를 문헌에서 못 구했다는 사실과는
# 별개로, 유도 자체가 옳게 서술됐는지를 검증한다.
def mrr_ratio(eta, eta_ref, Da):
    return (1 + Da) / (1 + Da * eta_ref / eta)

eta_ref = 0.10
# 단조증가: eta가 커질수록 비율도 커진다
vals = [mrr_ratio(eta, eta_ref, Da=2.0) for eta in [0.05, 0.10, 0.20, 0.50, 5.0]]
assert all(b > a for a, b in zip(vals, vals[1:])), f"단조증가가 아니다: {vals}"

# 포화: eta -> 무한대에서 (1+Da)로 수렴
assert abs(mrr_ratio(1e6, eta_ref, Da=2.0) - 3.0) < 1e-3

# Da=0(반응율속)이면 eta 무관 — 비율 항상 1
assert abs(mrr_ratio(0.5, eta_ref, Da=0.0) - 1.0) < 1e-9

# eta=eta_ref면 항상 정확히 1 (기준점 재현)
for Da in [0.1, 1.0, 10.0]:
    assert abs(mrr_ratio(eta_ref, eta_ref, Da) - 1.0) < 1e-9

print("PASS: 직렬저항 폐형식은 단조·포화·기준점 재현 성질을 만족한다(수학 자체는 유효, Da 값만 미확보)")
```

| 판정 | 서열 | 근거 | 날짜 |
|---|---|---|---|
| tau_mrr_exponent Da 재유도 — 경로(a)(b) 모두 실패, 0.07 유지 | 경로(b) 후보 4편 전부 **E3/E5**(같은 계 아님 또는 초록만) — 서열로 채택할 근거 자체가 없음(방향이 반대라 "약해도 채택"조차 불가) | Mu 2016 원문에 MRR 부재(재확인) + Q→MRR 문헌 4편이 전부 온도/COF/정점 채널로 진단되어 있어 "Q≡η, 단조포화" 가정과 부호가 반대. 데이터 스누핑 금지 원칙상 기각 | 2026-09-14 |

