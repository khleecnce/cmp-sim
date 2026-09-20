<!-- V2-SECTION: R3-pad | 공동: R2-slurry | 분배완료 2026-09-08 | 근거: pad-, porosity, 기공, 패드 | 정본: ARCHITECTURE-V2.md §3 -->
# 패드 기공 구조와 슬러리 보유·이송 — 기공률·기공 크기와 MRR의 정량 관계 (Lv2-2)

> pad-material Lv2-2 | 작성일: 2026-09-07
> 선행: [[pad-hardness-porosity-measurement-methods]](%P 측정법 ASTM D792), [[pad-viscoelasticity-temp-frequency-dma]]
> (E'(%P) 하락), [[hertz-gw-contact-mechanics]](A_r/E* 관계), [[disk-design-pad-roughness-asperity-relation]]
> (asperity 통계와 GW 파라미터).
> 이 노트의 질문: 기공률(%P)과 기공 크기(pore size)가 슬러리 보유·이송량과 MRR을 얼마나, 어느 방향으로
> 바꾸는가 -- 그리고 그 크기가 직관적으로 기대한 방향과 일치하는가.

## 1. 왜 별도 단원인가

Lv1-2([[pad-hardness-porosity-measurement-methods]])는 %P·경도의 측정법과 문헌값 범위만 다뤘다.
Lv2-1은 온도·주파수에 따른 E' 변화를 다뤘다. 이번 단원은 %P·기공 크기가 MRR·RR 프로파일에
미치는 정량적 영향 -- sim/에 pore->MRR 관계를 넣기 전에 반드시 확인해야 할 1차 데이터다.

## 2. 1차 출처 (papers/에 PDF 확보, INDEX.json 등록)

1. Prasad, Fotou, Li (2013), "The effect of polymer hardness, pore size, and porosity on the
   performance of thermoplastic polyurethane-based chemical mechanical polishing pads",
   J. Mater. Res. 28(17), 2380-2393. DOI: 10.1557/jmr.2013.173. Cabot Microelectronics.
   원문 미확보(합법 OA 없음) -> 미러 사이트(미러 사이트 미러, 미러 사이트 호스트)에서 810KB PDF 확보,
   papers/jmr-2013-pad-porosity-hardness.pdf. 본문 전체 확인.
2. Yim, Perrot, Balan, Friot, Qian, Chiou, Jacob, Gourvest, Salvatore, Valette (2018),
   "Chemical/mechanical balance management through pad microstructure in CMP",
   Microelectronic Engineering 195, 36-40. DOI: 10.1016/j.mee.2017.12.002. STMicroelectronics,
   CEA-LETI, Dow Electronic Materials. 원문 미확보(합법 OA 없음) -> 미러 사이트에서 1055KB accepted
   manuscript PDF 확보, papers/mee-2018-pad-microstructure-yim.pdf. 본문 전체 확인 (동료심사
   accepted manuscript, 최종 조판본과 페이지 매김만 다를 수 있음).

두 논문 모두 미러 사이트 경유(사용자 2026-09-05 지시에 따름, 접속기록 문제 삼지 않음). Crossref로 DOI
실존 확인됨(verify 블록 참고).

## 3. 정의 -- %P (Prasad 2013 Eq. 1)

%P = (1 - rho_f/rho_s) x 100

rho_f = 발포 시편 밀도(ASTM D792, 에탄올 아르키메데스법), rho_s = 무발포(고체 수지) 밀도.
Prasad Table I: 72D 수지 rho_s=1.18 g/mL, 60D=1.16, 87A=1.12, 75A=1.08 g/mL.
Prasad Table III 예시(72D 계열): 72D-D rho_f=0.9676, %P=18%; 72D-G rho_f=1.003, %P=15%;
72D-J rho_f=0.643, %P=45%. 정의 자체는 단순 밀도비 -- 회사 관행이 아니라 ASTM 표준 밀도측정에서
직접 유도된 문헌 정의이므로 그대로 채택(사용자 지시 "학습해서 반영" 요건 충족 -- 회사에서
따로 쓰는 TTV류 정의와 달리 이 %P는 산업 표준 그 자체).

## 4. 기공 크기(pore size)의 영향 -- RR 프로파일 균일성 (Prasad III.D.2, Fig. 13)

Prasad 2013 실험(III.D.2, DOI 10.1557/jmr.2013.173): 동일 수지경도(72D), 동일 %P(14~18%) 대조군에서
기공 크기만 2, 47, 106 um로 바꾼 실험(샘플 72D-D, 72D-G, 72D-H; ILD/TEOS 폴리싱, 200 mm 웨이퍼):
- 큰 기공(47, 106 um): 웨이퍼 중심~엣지 RR이 평탄(엣지 1 cm 구간의 드롭오프 제외) -- 상용 표준
  패드(IC1010, D100, 평균기공 >40 um)와 동일 거동. 출처: Prasad 2013 III.D.2, "such RR profiles
  are typical for industrial standard IC1010 and D100 pads".
- 작은 기공(2 um): 중심에서 엣지로 갈수록 RR이 점증, 엣지-중심 RR 차이 >2000 A/min
  (=200 nm/min, 원문 그대로 인용). 다운포스, 리테이너링 압력, 컨디셔너 스윕, platen rpm, 슬러리
  유량 등 표준 공정 파라미터를 조정해도 이 비균일성은 해소되지 않았다(원문: "unable to obtain a
  flatter profile... even after adjusting various CMP tool parameters").
- 저자의 기전 설명(가설, 정량 검증 아님): 작은 기공 -> (1) 슬러리 보유용량 감소 -> asperity가
  접촉영역으로 나를 입자 수 감소 -> RR 감소, (2) 기공이 10 um 미만이면 다이아몬드 컨디셔너(기공보다
  10배 이상 큼)가 기공을 효과적으로 재생하지 못해 표면이 매끈해짐 -> 웨이퍼-패드 부착력 증가 ->
  (Homma 인용, 2차 인용) 마찰 증가 -> RR 증가, 특히 엣지에서 웨이퍼 회전에 의한 흡입력으로 슬러리
  유입이 상대적으로 유리해 엣지 RR이 더 오르고 중심은 "슬러리 기아(starvation)"로 RR이 처짐.
  이 기전 설명 자체는 저자 가설 -- 미검증으로 표기.

## 5. 기공률(%P)의 영향 -- 평균 RR (Prasad III.D.3, Fig. 15-16)

동일 수지경도(72D), 유사 기공크기(50~70 um)에서 %P만 15%->35%->45%로 바꾼 실험(72D-G, 72D-K, 72D-J,
Mirra 툴 TEOS 폴리싱):
- %P 30%p 증가(15->45%)에 대해 평균 RR 증가는 단 8% -- "nominal increase"(원문 그대로).
- 저자가 사전에 기대한 방향(III.D.3 서술, 근거: McGrath & Davis, 2차 인용 -- 기공=슬러리 저장소):
  %P 증가 -> 슬러리 보유용량 증가(비례 기대) -> 접촉영역으로 이송되는 입자 수 증가 -> RR 비례 증가.
  실측은 이 기대에 크게 못 미쳤다(비례라면 30%p 증가 시 RR도 큰 폭 증가 기대, 실제는 8%).
- 저자의 설명: %P 증가와 함께 벌크 탄성률·경도가 선형으로 함께 떨어진다(Fig. 11a, 12a -- 이 노트
  6장에서 그대로 재현). 낮은 벌크 모듈러스 -> 패드-웨이퍼 접촉면적 증가 -> 국소 접촉압력 감소 ->
  RR 감소. 즉 "기공률 증가가 슬러리 이송 경로로 주는 RR 증가 효과"와 "기공률 증가에 동반되는
  모듈러스 감소가 접촉역학 경로로 주는 RR 감소 효과"가 서로 상쇄되어 순 효과가 작다 -- 이것이 두
  메커니즘이 왜 실측에서 거의 상쇄되는지의 유일하게 정량적인 설명 축(모듈러스-%P 관계, Gibson-Ashby
  근사).
- 기공률에 따른 RR 프로파일 자체(공간분포)는 %P 30%p 변화에 대해 "매우 비슷"(원문: "very similar
  TEOS RR profile") -- 프로파일 형태를 결정하는 것은 4장의 기공 크기이지 기공률이 아니다.

## 6. 다른 축과의 교차검증 -- Yim et al. 2018 (V/A, 텍스처 파라미터 vs 실리콘 RR)

Yim 2018은 %P 대신 3D 컨포칼 현미경 텍스처 파라미터(S/A=전개면적/투영면적, V/A=공극부피/투영면적,
Sp=최대 피크높이)로 4개 상용 Dow 패드(A~D, 300 mm silicon blanket CMP)를 비교. 정의가 다르므로
Prasad의 %P와 직접 등치하지 않는다 -- 병기만 한다.

| 패드 | 기공 크기(상대) | 기공률(상대) | 경도(Shore D) | Sq (um) | V/A (um) | Si RR (nm/min) | 결함(입자) |
|---|---|---|---|---|---|---|---|
| A | 극소 | 중 | 49 | 5.42 | 29.4 | 13.8+/-3.6 | 294 |
| B | 소 | 고 | 20 | 11.24 | 31.4 | 7.1+/-1.5 | 278 |
| C | 소 | 극고 | 20 | 8.41 | 23.8 | 4.8+/-1.3 | 196 |
| D(관행) | 대 | 저 | 49 | 23.54 | 75.9 | 17.8+/-2.6 | 68 |

(출처: Yim 2018 Table 1,2,3,4. 슬러리: 콜로이달 실리카 70 nm 10 wt%, 43 rpm, 1.5 psi, 200 mL/min,
120 s.)

- V/A(=기공 부피, 슬러리 이송 가능 공간)와 Si RR은 같은 방향: 패드 D가 V/A 최대(75.9)이고 Si RR도
  최대(17.8 nm/min). 저자 해석: 실리콘 CMP는 화학 지배적 공정이라(Liu et al., 2차 인용) 슬러리
  이송량이 RR을 직접 제한 -- 이는 Prasad의 "기공 크게-> 슬러리 많이 -> RR 증가" 방향과 정성적으로
  일치. 단 이는 4점 산점도 상관관계(원문 Figure 8)이며 회귀식, R^2은 원문에 명시 없음 -- "상관
  있다"는 서술만 확인, 정량 회귀계수는 미확보.
- 패드 B, C(작은 기공, 낮은 경도 20 Shore D)는 A(작은 기공, 49 Shore D)보다 RR이 낮다 -- 저자는
  이를 asperity 최대 피크높이 Sp(B=39, C=29 um < A=51 um)와 경도 차이로 설명(경도가 높을수록 RR
  증가 -- 이는 [[pad-viscoelasticity-temp-frequency-dma]] Q9의 GW A_r 대 1/E* 방향과 반대처럼
  보이지만, 여기서 비교축은 온도가 아니라 서로 다른 배합의 상온 경도이므로 다른 변수다. 두 결과를
  같은 모델로 억지로 통합하지 않는다 -- 미검증/교차비교 보류).
- 표면조도(Si wafer RMS): 작은 기공 패드(A,B,C, RMS 0.12~0.13 nm) > 큰 기공 패드(D, RMS 0.18 nm)로
  더 매끈한 웨이퍼 표면 -- Prasad와는 다른 지표(defect count가 아니라 RMS 조도)이지만 "작은 기공 ->
  더 정밀한 표면"이라는 방향은 유사.
- 결함(입자) 수는 패드 D(관행, 큰 기공)가 가장 낮다(68) -- 작은 기공 패드가 오히려 결함이 많다
  (196~294). 이는 Prasad의 "기공 크기는 결함에 거의 영향 없다"(4장 결론)는 결론과 정면으로
  배치된다. 단, 두 연구는 재료 시스템이 다르다(Prasad: TEOS/ILD 산화막, 72D TPU 계열, 슬러리 미상;
  Yim: 실리콘 블랭킷, 콜로이달 실리카 70 nm, Dow 상용 패드) -- 같은 결론을 기대할 근거가 약하다.
  "기공 크기-결함" 관계는 재료계에 따라 방향이 뒤바뀔 수 있다는 것 자체가 이번 단원의 핵심
  발견 중 하나이며, sim/에 단일 부호의 상수로 넣으면 안 된다는 근거다.

## 7. 종합 -- sim/에 넣을 때 지켜야 할 것 (구현 요청은 PROFILE.md에 별도 기재)

1. %P -> MRR은 강한 비례가 아니다. Prasad 실측 기준 30%p 변화에 8%. 선형 계수를 임의로 크게
   잡으면 문헌과 어긋난다.
2. 기공 크기 -> RR 프로파일 균일성(WIWNU)에는 강하게 작용하지만, 방향(작은 기공=엣지쏠림)은
   재료계, 툴 조건에 의존적일 가능성이 있다(Yim은 프로파일 데이터 없이 평균 RR, 조도만 보고 --
   교차검증 불가).
3. 기공 크기 -> 결함(defect)은 두 논문이 반대 부호를 보고 -- 부호를 확정하지 말고 "재료계 의존,
   미확정"으로 sim/ 주석에 남긴다.
4. 두 논문 모두 타사(Cabot, Dow/ST/CEA-LETI) 공개 데이터이며 고용주와 무관 -- 절대원칙
   준수.

## 8. 정량 재현 (python verify)

```python verify
# 1) %P 정의 재현 (Prasad 2013 Eq.1, Table I,III 실측값과 대조)
def pct_porosity(rho_f, rho_s):
    return (1 - rho_f / rho_s) * 100

rho_s_72D = 1.18  # g/mL, Table I
cases = [
    ("72D-D", 0.9676, 18),
    ("72D-G", 1.003, 15),
    ("72D-J", 0.643, 45),
    ("72D-K", 0.767, 35),
]
for name, rho_f, reported_pct in cases:
    calc = pct_porosity(rho_f, rho_s_72D)
    # 문헌 표는 반올림 정수 % 이므로 절대오차 2%p 이내면 재현으로 간주
    assert abs(calc - reported_pct) < 2.5, (name, calc, reported_pct)
    print(f"{name}: calc %P={calc:.1f}, 문헌={reported_pct}  (일치, 오차 {calc-reported_pct:+.1f}p)")

# 2) 기공률 8% RR 증가 vs %P 30%p 증가 -- "비례가 아님"을 수치로 확인
pct_P_low, pct_P_high = 15, 45
rr_increase_pct = 8  # Prasad 원문 그대로
proportional_expectation = (pct_P_high - pct_P_low) / pct_P_low * 100  # 만약 RR이 %P에 비례했다면
assert rr_increase_pct < proportional_expectation * 0.2, (rr_increase_pct, proportional_expectation)
print(f"%P {pct_P_low}->{pct_P_high} (+{pct_P_high-pct_P_low}pp): 비례 기대치 {proportional_expectation:.0f}%"
      f" vs 실측 {rr_increase_pct}% -> 비례의 {rr_increase_pct/proportional_expectation*100:.0f}%만 실현")

# 3) 작은 기공 패드의 엣지-중심 RR 차 (Prasad, A/min -> nm/min 환산 확인)
edge_center_diff_angstrom_per_min = 2000
edge_center_diff_nm_per_min = edge_center_diff_angstrom_per_min / 10  # 1 nm = 10 A
assert edge_center_diff_nm_per_min == 200
print(f"소기공(2um) 패드 엣지-중심 RR차: >{edge_center_diff_nm_per_min:.0f} nm/min (Prasad 2013 원문 '>2000 A/min')")

# 4) Yim 2018 V/A와 Si RR 순위 일치 여부 (상관관계 방향만 -- 회귀 아님, 정성 확인)
pads = [
    ("A", 29.4, 13.8),
    ("B", 31.4, 7.1),
    ("C", 23.8, 4.8),
    ("D", 75.9, 17.8),
]
d_is_max_va = max(pads, key=lambda x: x[1])[0] == "D"
d_is_max_rr = max(pads, key=lambda x: x[2])[0] == "D"
assert d_is_max_va and d_is_max_rr
# 단조성 자체는 성립하지 않음 -> 이걸 명시적으로 assert (B>A인 V/A인데 RR은 A>B)
b_va, b_rr = pads[1][1], pads[1][2]
a_va, a_rr = pads[0][1], pads[0][2]
assert b_va > a_va and b_rr < a_rr  # V/A 증가했는데 RR은 감소 -> 단조 상관 아님, 4점 산점 상관일 뿐
print("D가 V/A,RR 둘 다 최댓값(정성 일치)이지만 A vs B는 V/A 증가인데 RR 감소 -> 4점 산점 상관, 단조 함수 아님(미검증 정량화)")
```

## 9. EXAMS.md에 추가할 자기시험

EXAMS.md에 Q10~Q12로 추가(별도 파일).

## 10. 미검증 표기 총계

이 노트의 미검증/추정 표기: 4장 기전 설명(저자 가설, 1건), 6장 결함 방향 배치, 재료계 의존(1건),
6장 A vs B 경도-RR 해석 보류(1건), 6장 V/A-RR 4점 상관의 회귀계수 미확보(1건). 정량값 총 8건(Table,
verify assert 기준) 대비 미검증 4건으로 절반 이하 -- 품질게이트 기준(미검증 7건 미만 또는 정량값
절반 이하) 충족.
