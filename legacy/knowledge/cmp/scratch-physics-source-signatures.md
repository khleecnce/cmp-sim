<!-- V2-SECTION: R2-slurry(연계) · R3-pad · R4-disk | 작성 2026-09-13 | defect-scientist Lv1-2 -->
# 스크래치 물리 — 발생원별(슬러리 대입자·패드 파편·디스크 그릿 탈락) 형상 특징과 역추적 규칙

> 에이전트: defect-scientist Lv1-2 | 작성일: 2026-09-13
> 선행: [[post-cmp-defect-classification-and-inspection]](결함 유형·검사장비 정의),
> [[../materials/hertz-gw-contact-mechanics]](Hertz 접촉·GW 거칠기 — 본 노트의 하한 하중식이
> 그 Hertz 해에서 직접 유도된다)
> 관련: [[delta-scratch-damage-d99-oversize-particle-model]], [[lpc-scratch-density-tail-correlation]],
> [[w-cmp-abrasive-agglomeration-scratch-multiplier-egan-kim2019]],
> [[../equipment/conditioner-grit-wear-scratch-lifetime]](같은 Kwon 2013 Tribol. Int. 논문을
> **디스크 수명** 관점에서 다룸 — 본 노트는 같은 논문에서 **디브리 크기·형상 신호**만 가져오고
> 패드 절삭율·수명 판정은 중복 서술하지 않는다), [[colloid-zeta-dlvo-slurry-stability]],
> [[defect-density-yield-models-and-spatial-statistics]](Lv2-2 — 여기 §7의 디스크 그릿 긴 호(곡률 0.24–0.50m)를 **결함맵 공간 signature→CMP 원인 귀속**으로 받는다)

## 1. 질문을 바꾼다 — "스크래치가 몇 개인가"가 아니라 "이 스크래치는 누가 냈는가"
Lv1-1에서 스크래치의 조작적 정의(길이 ≥ 50 µm, dark-field 계수)와 검사장비를 고정했다. 그러나
결함맵에 찍힌 점 하나에서 **원인 소모품(슬러리 / 패드 / 디스크)** 으로 되돌아가려면 개수가 아니라
**형상(width·depth·length·곡률·군집성)** 을 읽어야 한다. 이 노트의 주장은 하나다:

> **스크래치의 정규화 치수(a_c/R)는 발생원과 무관하게 0.1–0.5의 좁은 띠에 갇혀 있다.
> 따라서 발생원 판별은 폭/깊이 "비율"이 아니라 폭·깊이의 "절대값"과 궤적으로 해야 하며,
> 그 절대값에서 R_est = a_c²/(2δ_c) 로 발생원 입자 반경을 역산할 수 있다.**

이 명제는 Saka–Eusner–Chun의 상한해석(§2)에서 나오고, Eusner et al.(2009)의 실측 스크래치
32건으로 검증된다(§4, §8-B). 형상 유형 분포는 Kwon et al.(2013, Tribol. Lett.)이 발생원 3종을
의도적으로 투입해 실측한 값을 쓴다(§5~§7).

## 2. 단일입자 접촉역학 — 하한(항복)과 상한(완전소성)
**Saka, N., Eusner, T., Chun, J.-H. (2008). "Nano-scale scratching in chemical–mechanical
polishing." CIRP Annals 57(1), 341–344. DOI: 10.1016/j.cirp.2008.03.098**
(전문 확보: `papers/saka2008-cirp-nanoscale-scratching.pdf`, 4쪽 직접 판독)
**Eusner, T., Saka, N., Chun, J.-H., Armini, S., Moinpour, M., Fischer, P. (2009). "Controlling
Scratching in Cu Chemical Mechanical Planarization." J. Electrochem. Soc. 156(7), H528–H534.
DOI: 10.1149/1.3121964** (전문 확보: `papers/eusner2009-jes-controlling-scratching-cu-cmp.pdf`, 7쪽)

강체 구형 입자(반경 R)가 연질 박막(탄성계수 E_c, 경도 H_c)을 누를 때:

```
[하한 — 항복 개시, Hertz + Tresca]
  a_Y,c = (π/4)(H_c/E_c) R
  δ_Y,c = (π²/16)(H_c/E_c)² R
  P_Y,c = (π³/48)(H_c³/E_c²) R²

[상한 — 완전소성 소성긁기(plowing)]
  H_c  = P_UB / (½π a_c²)          (경도 정의, 투영접촉면적)
  a_c  = (2 P_UB / (π H_c))^(1/2)
  δ_c  = P_UB / (π R H_c)
  P_UB = π δ_c R H_c
  δ_c/R = ½ (a_c/R)²               (구 기하)   → **R_est = a_c²/(2 δ_c)**
```
(Saka et al. 2008 식(1)–(8); Eusner et al. 2009 식(1)–(8)에 동일 형태로 재수록)

마지막 줄이 이 노트의 **역추적 공식**이다. 폭(2a_c)과 깊이(δ_c)를 프로파일러/AFM으로 재면
그것을 낸 입자의 반경 R이 나온다. Eusner et al.(2009) Table II·III의 `R_exp` 열이 바로 이
공식으로 계산된 값이며(Eusner et al. 2009 Table II·III), §8-B에서 32건 전부를 재현한다(최대 오차 0.44 %).

**AFM 검증 조건(Eusner et al. 2009 실험 절)**: Hysitron TriboIndenter, 다이아몬드 팁 **곡률반경 800 nm**,
스크래치 길이 **10 µm**, 수직하중 **50–300 µN**, 긁기 속도 **0.33 µm/s**, 시편은 300 mm 블랭킷
웨이퍼에서 절단한 10 mm × 10 mm(막 두께 1 µm) — 전 하중 구간에서 실측점이 상한선 아래에
있었다(Eusner et al. 2009 Fig.10).
⚠ 원문 PDF의 텍스트 추출에서 그리스문자 µ가 m으로 깨져 나온다("50 to 300 mN", "10 mm long").
Fig.8/9 캡션의 `P = 277 µN`과 Hysitron 장비 정격, 그리고 §8-B에서 재현한 하중 스케일(µN)로
µ 판독이 옳음을 교차확인했다.

### 2.1 재료 물성(모든 계산의 상수 — Eusner et al. 2009 Table I)
| 재료 | 유전율 k | E (GPa) | H (GPa) |
|---|---|---|---|
| Al₂O₃ 연마입자 | — | 350 | 20 |
| SiO₂ (유전막·연마입자) | 3.90 | 92 | 15 |
| Cu 배선 | — | 128 | 1.22 |
| low-k A | 3.05 | 11 | 2.09 |
| low-k B | 2.50 | 8 | 1.37 |
| 패드(IC1000, 습윤) | — | 0.53 | **0.05 평균 / 0.01–0.31 국소 범위** |

패드 경도는 Berkovich 압입(압입깊이 90 nm) 36회 측정값의 분포이며, **평균 0.05 GPa·표준편차
0.06 GPa·최대 0.31 GPa**(Eusner et al. 2009 Fig.15). 이 "분포의 꼬리"가 §6의 핵심이다.

## 3. 상한 한계 — 스크래치가 아무리 커도 넘을 수 없는 선
패드가 입자를 절반까지 삼키면(a_p = R) 그 다음 압력 증분은 패드가 입자를 완전히 감싸는 데 쓰인다.
같은 하중이 패드와 박막에 동시에 걸린다는 조건에서:

```
  a_c/R = √(H_p/H_c) · (a_p/R)  ≤  √(H_p,max/H_c)      (Saka 2008 식(14)(15) / Eusner 2009 식(9)(10))
  δ_c/R ≤ H_p,max/H_c                                    (Eusner 2009 식(11))
```
중요한 성질 두 가지: (i) 이 한계는 **연마압력과 패드 토포그래피에 무관**하다 — 압력을 낮추거나
패드 조도를 바꿔도 최대 스크래치 크기는 줄지 않는다(Eusner et al. 2009 결론). (ii) 한계를 정하는
것은 **패드 경도의 최대값**이지 평균값이 아니다.

§8-A에서 Eusner et al.(2009) Table IV 전체(Cu·low-k A·low-k B × H_p 0.05/0.31 GPa)를 재현한다:
Cu에서 a_c/R ≤ 0.20(평균 패드) / 0.50(최경 패드), δ_c/R ≤ 0.04 / 0.25 — 문헌 표와 소수 둘째
자리까지 일치.

## 4. 발생원 ①: 슬러리 대입자·응집체 — "폭 100 nm·깊이 5 nm"
Eusner et al.(2009)는 Cu 블랭킷 웨이퍼 2장을 실리카 슬러리 DO2(공칭 반경 50 nm)·DO4(45 nm)로
60 s 연마한 뒤(IC1000 패드, 5 wt% 고형분, H₂O₂ 0.3 vol%, 글리신 1 wt%, BTA 0.018 wt%)
프로파일러로 스크래치 32건의 폭·깊이를 실측했다. 평균값:

| 슬러리 | a_c (nm) | δ_c (nm) | R_exp (nm) | 응집입자수 n | a_c/R_exp | P (µN) |
|---|---|---|---|---|---|---|
| DO2 (R₀ = 50 nm) | 50.7 ± 15.8 | 4.7 ± 2.1 | 305 ± 124 | 253 ± 308 | 0.182 | 5.4 |
| DO4 (R₀ = 45 nm) | 51.7 ± 17.0 | 3.9 ± 1.1 | 381 ± 229 | 976 ± 1483 | 0.160 | 5.6 |

읽어야 할 세 가지(전부 Eusner et al. 2009 Table II·III 값):
1. **역산된 R_exp(305·381 nm)가 공칭 입경(50·45 nm)의 6–8배다.** 즉 Cu를 긁은 것은 1차 입자가
   아니라 **응집체**다. 응집입자수 n은 무작위조밀충전 계수 0.74로 n = 0.74 (R_exp/R₀)³ 로
   계산돼 있고(§8-B에서 32건 재현, 최대오차 1.6 %), DO2 평균 253개·DO4 평균 976개다.
2. **절대치수가 작다** — 폭 2a_c ≈ 100 nm, 깊이 δ_c ≈ 4–5 nm. 45 nm 노드 배선 폭과 같은 오더의
   폭이지만 깊이는 Cu 막두께(≈1 µm)의 0.5 % 수준이다. 단독으로 killer가 되기 어렵고,
   **개수 통계**로 관리해야 하는 이유가 여기 있다([[lpc-scratch-density-tail-correlation]]).
3. **꼬리에 괴물이 있다** — DO4 1번 스크래치는 a_c = 292.3 nm, δ_c = 7.0 nm → R_exp = 6103 nm,
   n ≈ 1.85 × 10⁶개, 하중 163.7 µN. 즉 6 µm급 하드 응집체 한 개가 평균 대비 폭 6배·하중 30배의
   스크래치를 냈다. LPC 관리 임계(실리카 등가 0.68 µm 초과, Remsen et al. 2006)가
   왜 "평균"이 아니라 "꼬리"를 보는지가 이 한 줄로 설명된다.

**건조 응집체(dried particle)의 크기**: Kwon et al.(2013, Tribol. Lett.)은 신선 슬러리(퓸드실리카
120 nm, 13.5 wt%, KOH계 pH ≈ 11.4)를 30 °C에서 12 h 건조·분쇄해 만든 건조입자의 평균 크기를
**2.5 µm**(1차 입자의 약 21배)로 측정하고, 이를 2 wt%로 투입했다.

## 5. 발생원 ②: 패드 파편(pad debris) — "35 µm짜리 무른 덩어리"
**Kwon, T.-Y., Ramachandran, M., Cho, B.-J., Busnaina, A.A., Park, J.-G. (2013). "The impact of
diamond conditioners on scratch formation during chemical mechanical planarization (CMP) of
silicon dioxide." Tribology International 67, 272–277. DOI: 10.1016/j.triboint.2013.08.008**
(전문 확보: `papers/kwon2013-scratch-formation-diamond-conditioners.pdf`)

- **크기(Fig.5 범례 실측값)**: 컨디셔너 그릿 밀도별 평균 디브리 크기 **34.61 µm(17 k) /
  32.78 µm(40 k) / 32.01 µm(60 k)**, 그릿 형상(grade)별 **41.17 µm(sharp 625) /
  32.78 µm(medium 640) / 31.56 µm(blunt 925)**. 분포 자체는 약 5 µm~300 µm에 걸친다.
  → **디브리 크기는 그릿 밀도(±4 %)보다 그릿 형상(±30 %)에 민감하다**. 날카로운 그릿이 패드에
  깊이 박혀 큰 조각을 뜯기 때문(Kwon et al. 2013).
- **양(정량 앵커)**: 컨디셔닝 중 진공 포집한 디브리 현탁액 1 mL를 50 °C·24 h 건조했을 때
  건조중량 **0.025 g**(Kwon et al. 2013).
- **효과(Fig.6 판독)**: 디브리를 0.25 wt%로 20 mL/min 주입하면 정규화 스크래치 수가 기준 1.0 →
  **2.25**로 뛰지만, 농도를 0.375 / 0.5 / 1 wt%로 올려도 **2.4 / 3.0 / 2.5**로 오차막대 안에서
  포화한다. 저자 해석: 웨이퍼면에 실제로 전달되는 디브리 양이 헤드·플래튼·리테이닝링 회전으로
  제한되기 때문. MRR은 디브리 크기·농도와 무관하게 **440 nm/min**으로 일정했다.
  (막대·오차막대는 Fig.6 그림 판독 — 축 눈금 0.5 간격, 판독오차 ±0.1로 본다.)

**그런데 패드 파편은 웨이퍼보다 무르다.** 폴리우레탄 디브리의 경도는 패드 경도 그 자체
(0.01–0.31 GPa)이고 Cu는 1.22 GPa다. 무른 것이 굳은 것을 어떻게 긁는가 — 이것이 §6이다.

## 6. 무른 파편이 긁는 조건 — 마찰계수가 경도 부족을 대신한다
**Saka, N., Eusner, T., Chun, J.-H. (2010). "Scratching by pad asperities in chemical–mechanical
polishing." CIRP Annals 59(1), 329–332. DOI: 10.1016/j.cirp.2010.03.113**
(전문 확보: `papers/saka2010-cirp-pad-asperity-scratching.pdf`, 4쪽 직접 판독)

패드 애스퍼리티(=포집되지 않은 파편과 같은 재료)가 완전소성으로 눌릴 때, 박막이 항복(=긁힘)할
조건은 마찰계수 µ의 함수다(FEA, Mises, ν = 0.33):

```
  H_p/H_c ≥ 0.45                                             (µ ≤ 0.1, 식(6))
  H_p/H_c ≥ (1/3)(0.405 + 0.755µ + 7.763µ²)^(−1/2)           (µ ≥ 0.1, 식(7))
```
⚠ **지수 부호 정정**: 원문 PDF 추출본의 식(7)은 지수가 `+1/2`로 보인다. 그 형태는 (i) µ가 커질수록
긁기 문턱이 **높아지는** 물리적 역설을 낳고, (ii) 본문 서술("even softer asperities can … scratch
… if the friction coefficient is high")·Fig.6의 우하향 곡선·식(6)의 0.45와 모두 모순된다.
`−1/2`로 읽으면 µ = 0.1에서 0.446이 되어 식(6)의 **0.45와 정확히 이어진다**. §8-C에서 두 부호를
모두 계산해 실험 결과와 대조했고, `−1/2`만 실험을 재현한다. (이 정정은 본 노트의 판단이다.)

**저자 자신의 마찰 실험(IC1000 패드/Cu 박막, 왕복 슬라이딩, 하중 0.2 kg = 평균압력 11.1 kPa
(1.6 psi), 속도 5.5 mm/s)**:

| 윤활 | µ (평균) | µ (표준편차) | SEM 관찰 스크래치 |
|---|---|---|---|
| 건식 | 0.55 | 0.02 | 넓고 깊음 |
| 물 | 0.43 | 0.02 | 중간 |
| SDS 0.01 M | 0.19 | 0.01 | 극히 미세 |

§8-C 재현 결과: 최경 패드 재료(H_p = 0.31 GPa, H_p/H_Cu = 0.254)에 대해 문턱은
µ = 0.19 → 0.366(긁힘 없음), µ = 0.43 → 0.227(긁힘), µ = 0.55 → 0.187(긁힘)으로,
**SEM 관찰 3건과 모두 일치**한다. 임계 마찰계수는 **µ\* = 0.366**이고, 저자 권고는 안전여유를 둔
**µ < 0.2**이다(Saka et al. 2010 결론 3).

**가장 중요한 파생 결과(본 노트 계산)**: 같은 식에 패드의 *평균* 경도 0.05 GPa를 넣으면 필요한
마찰계수가 **µ ≈ 2.9**로 물리적으로 불가능하다. 즉 **패드·파편이 내는 스크래치는 패드 경도
분포의 상단 꼬리(≈0.31 GPa, 평균의 6배)가 만든다.** 관리 대상은 패드의 평균 경도가 아니라
**경도 산포**다(Eusner et al. 2009 결론의 "hard spots"와 같은 결론에 독립적으로 도달).

## 7. 발생원 ③: 컨디셔너 디스크 그릿 탈락 — "웨이퍼를 가로지르는 호"
**US 6,884,155 B2 (Kinik Co., 발명 Chien-Min Sung 외, 출원 2002-03-27, 등록 2005-04-26),
"Diamond grid CMP pad dresser"** (전문 확보: `papers/us6884155b2-kinik-diamond-grid-cmp-pad-dresser.txt`,
freepatentsonline 경유). 특허 배경기술이 기전을 명시한다 — *"abrasive particles may dislodge from
the substrate of the disk and become caught in the CMP pad fibers. This leads to scratching and
ruin of the work piece being polished."* 탈락 원인 두 가지도 명시돼 있다:
(i) 전기도금 니켈은 화학결합 없이 **기계적 힘만으로** 그릿을 잡고 있어 마찰에 쉽게 빠지고,
슬러리의 화학공격이 이를 가속한다. (ii) 브레이징은 화학결합이지만 **슬러리 산이 브레이즈–입자
결합을 빠르게 약화**시킨다. 추가로 브레이즈 표면의 뾰족한 돌기가 떨어져 나온 **브레이즈 플레이크
자체가 마이크로스크래치**를 만든다고 적고 있다.
수치 규격(같은 특허 청구항·명세): 그릿 크기 **100–350 µm**(청구항 12), 크기 산포 **≤ 50 µm**
(청구항 13), 오버레이 두께 **0.1–50 µm**(청구항 31), 브레이즈면 위 그릿 돌출 **10–90 %**.

**Pysher, D., Goers, B., Zabasajja, J. (2010). "Design, Characteristics and Performance of Diamond
Pad Conditioners." Mater. Res. Soc. Symp. Proc. 1249, 1249-E02-04. DOI: 10.1557/proc-1249-e02-04**
(전문 확보: `papers/3m_diamond_conditioner_design.pdf`) — 사용 후 디스크를 해체 계측해 얻은
**작동 그릿의 패드 침투깊이(DOP) ≈ 15 µm**, 상용 디스크 그릿 크기대 45–250 µm, 그리고 미세결함
개선 실험(200 mm Cu 블랭킷, AMAT Mirra Mesa, SP1): 컨디셔닝 없음 88·129 micro / 54·57 macro,
기존 디자인 75·67 / 3·3, 개선 디자인 **9·0 / 0·0**. 즉 **디스크 표면 요철 자체가 macro 결함의
지배 인자**였다(3M 2010 Table I).

**형상 신호(1차 실측)**: Kwon et al.(2013, Tribol. Lett.)은 **250 µm 다이아몬드 한 알을
폴리우레탄 패드에 고정**하고 산화막을 연마해, 헤드·플래튼 회전 때문에 **웨이퍼를 가로지르는 크고
반원형인(semicircular) 스크래치**가 생기고 광학현미경에서 **다이아몬드 다면체 면이 만든 줄무늬
(stripe) 다중선**이 보인다고 보고했다(Fig.8 웨이퍼 스캔맵·Fig.9). §8-D에서 이 "호"의 기하를
운동학으로 계산한다 — 헤드·플래튼 등속이면 패드 고정 입자의 궤적은 **중심거리와 같은 반지름의
정확한 원**이고, 67/73 rpm에서는 웨이퍼 내부 구간의 **곡률반경이 0.24–0.50 m**로 웨이퍼 반경
0.15 m보다 훨씬 크다. 그래서 칩 스케일에서는 직선, 웨이퍼 맵에서는 완만한 호로 보인다.

## 8. 검증 — 문헌값 대조 코드
### (A) Saka(2008) 패드 항복압력 + Eusner(2009) Table IV 상한치수
```python verify
import math
# --- Saka et al. 2008 식(13): 패드 애스퍼리티 탄성→소성 전이압력
# 문헌 제시 물성(IC1000): Ra=5 µm, la=100 µm, Ep=0.5 GPa, Hp=0.05 GPa → p_Y,a = 0.83 kPa (0.12 psi)
Ra, la, Ep, Hp = 5e-6, 100e-6, 0.5e9, 0.05e9
pY = math.pi**3/48 * Ra**2 * Hp**3 / (la**2 * Ep**2)
print("p_Y,a = %.1f Pa = %.3f kPa = %.3f psi (문헌 0.83 kPa / 0.12 psi)" % (pY, pY/1e3, pY/6894.757))
assert abs(pY/1e3 - 0.83)/0.83 < 0.05, "패드 항복압력 문헌값 불일치"
assert abs(pY/6894.757 - 0.12) < 0.005
# CMP 실공정압 13.8~34.5 kPa(2~5 psi)는 전이압력의 몇 배인가 → 애스퍼리티는 항상 완전소성
assert 17 < 13800/pY < 18 and 42 < 34500/pY < 43
print("CMP 압력/전이압력 = %.0f~%.0f배 → 애스퍼리티 완전소성 가정 정당" % (13800/pY, 34500/pY))

# --- Eusner et al. 2009 Table IV: (a_c/R)max = sqrt(Hp/Hc), (δc/R)max = Hp/Hc
Hc = {"Cu": 1.22, "A": 2.09, "B": 1.37}          # GPa, Table I
lit = {  # (Hp=0.05: a/R, δ/R), (Hp=0.31: a/R, δ/R)  ← Table IV 인쇄값
    "Cu": ((0.20, 0.04), (0.50, 0.25)),
    "A":  ((0.15, 0.02), (0.39, 0.15)),
    "B":  ((0.19, 0.04), (0.48, 0.23)),
}
for m, ((a5, d5), (a31, d31)) in lit.items():
    for Hp_, (aL, dL) in ((0.05, (a5, d5)), (0.31, (a31, d31))):
        a = math.sqrt(Hp_/Hc[m]); d = Hp_/Hc[m]
        assert abs(a - aL) <= 0.005 and abs(d - dL) <= 0.005, (m, Hp_, a, d)
        print("%-3s Hp=%.2f GPa → a/R=%.3f(문헌 %.2f)  δ/R=%.3f(문헌 %.2f)" % (m, Hp_, a, aL, d, dL))
print("Table IV 6쌍 전부 소수 둘째자리 일치")
```

### (B) Eusner(2009) 실측 스크래치 32건 — 역추적 공식·응집수·하중 재현
```python verify
import math, statistics
HCu = 1.22e9            # Pa, Eusner 2009 Table I
# Table II (DO2, 공칭 R0=50 nm) / Table III (DO4, R0=45 nm): (a_c nm, δ_c nm, R_exp nm, n, a/R, P µN)
DO2 = [(45.5,2.4,431,474,0.106,4.0),(49.0,3.5,343,239,0.143,4.6),(29.0,2.0,210,55,0.138,1.6),
       (58.0,7.0,240,82,0.242,6.4),(43.0,6.0,154,22,0.279,3.5),(98.5,8.3,584,1179,0.169,18.6),
       (48.8,4.6,259,103,0.188,4.6),(69.2,6.9,347,247,0.199,9.2),(43.3,3.8,247,89,0.175,3.6),
       (50.1,7.1,177,33,0.283,4.8),(54.7,7.2,208,53,0.263,5.7),(34.1,3.7,157,23,0.217,2.2),
       (50.5,3.2,398,373,0.127,4.9),(49.0,2.5,480,655,0.102,4.6),(50.5,3.4,375,312,0.135,4.9),
       (38.5,2.8,265,110,0.145,2.8)]
DO4 = [(292.3,7.0,6103,1845969,0.048,163.7),(153.9,5.1,2322,101667,0.066,45.4),(32.8,5.2,103,9,0.318,2.1),
       (32.7,2.9,184,51,0.178,2.0),(35.9,2.7,239,111,0.150,2.5),(46.6,4.4,247,122,0.189,4.2),
       (53.5,3.9,367,401,0.146,5.5),(36.7,2.8,241,114,0.152,2.6),(44.5,4.5,220,86,0.202,3.8),
       (64.5,2.7,770,3707,0.084,8.0),(90.0,5.0,810,4316,0.111,15.5),(59.0,6.0,290,198,0.203,6.7),
       (67.5,4.3,530,1209,0.127,8.7),(70.9,3.6,698,2762,0.102,9.6),(50.5,3.4,375,428,0.135,4.9),
       (38.5,2.8,265,151,0.145,2.8)]
eR, eN, eP, aspect, ratios = [], [], [], [], []
for rows, R0 in ((DO2, 50.0), (DO4, 45.0)):
    for a, d, R, n, ratio, P in rows:
        R_est = a*a/(2*d)                          # 역추적 공식 R = a²/2δ
        n_est = 0.74*(R_est/R0)**3                 # 무작위조밀충전 0.74
        P_est = math.pi*(d*1e-9)*(R_est*1e-9)*HCu*1e6   # 식(8), µN
        eR.append(abs(R_est-R)/R); eN.append(abs(n_est-n)/n); eP.append(abs(P_est-P)/P)
        aspect.append(2*a/d); ratios.append(a/R)
print("R_exp 재현 최대오차 %.2f %% / n 최대오차 %.1f %% / P 최대오차 %.1f %%"
      % (100*max(eR), 100*max(eN), 100*max(eP)))
assert max(eR) < 0.01 and max(eN) < 0.02 and max(eP) < 0.03
# 응집수에 충전율 0.74가 실제로 들어있는가 (없으면 640개가 되어야 함)
assert abs(0.74*(431/50)**3 - 474) < 1 and abs((431/50)**3 - 640.5) < 1
# 평균값 대조 (Table II/III 하단 Av. 행)
print("DO2 a_c 평균 %.1f nm(문헌 50.7) / δ 평균 %.1f nm(문헌 4.7)"
      % (statistics.mean(r[0] for r in DO2), statistics.mean(r[1] for r in DO2)))
assert abs(statistics.mean(r[0] for r in DO2) - 50.7) < 0.2
assert abs(statistics.mean(r[1] for r in DO2) - 4.7) < 0.1
# 정규화 폭은 좁은 띠에 갇혀 있다 / 종횡비는 넓게 퍼진다 → 판별은 절대값으로
print("a_c/R 범위 %.3f~%.3f (상한 0.50) | 폭/깊이 범위 %.0f~%.0f, 중앙값 %.0f"
      % (min(ratios), max(ratios), min(aspect), max(aspect), statistics.median(aspect)))
assert max(ratios) <= 0.50 and 12 < min(aspect) < 14 and 80 < max(aspect) < 85
```

### (C) Saka(2010) 마찰 기준 — 지수 부호 정정과 실험 3건 대조
```python verify
import math
HCu, Hp_max, Hp_avg = 1.22, 0.31, 0.05            # GPa, Eusner 2009 Table I / Fig.15
thr      = lambda mu: (1/3)*(0.405 + 0.755*mu + 7.763*mu**2)**-0.5   # 정정(−1/2)
thr_bad  = lambda mu: (1/3)*(0.405 + 0.755*mu + 7.763*mu**2)**+0.5   # 원문 추출형(+1/2)
# 1) µ=0.1에서 식(6)의 0.45와 이어지는가 — 정정형만 이어진다
print("정정형 thr(0.1)=%.4f, 원문형 thr(0.1)=%.4f (식(6) 문헌값 0.45)" % (thr(0.1), thr_bad(0.1)))
assert abs(thr(0.1) - 0.45) < 0.005
assert abs(thr_bad(0.1) - 0.45) > 0.2
# 2) 저자 마찰실험 3건(dry 0.55 / water 0.43 / SDS 0.19)의 긁힘 여부 재현
obs = {0.55: True, 0.43: True, 0.19: False}       # SEM 관찰(Fig.7): 넓고깊음/중간/극미세
r = Hp_max/HCu
for mu, scratched in obs.items():
    pred = r >= thr(mu)
    print("µ=%.2f: 문턱 %.3f vs H_p,max/H_Cu=%.3f → 예측 %s / 관찰 %s"
          % (mu, thr(mu), r, "긁힘" if pred else "없음", "긁힘" if scratched else "없음"))
    assert pred == scratched, "정정형이 실험과 불일치"
    assert (r >= thr_bad(mu)) != scratched or mu == 0.19   # 원문형은 0.43·0.55를 틀린다
# 3) 임계 마찰계수 µ* (H_p,max 기준) 및 저자 권고 µ<0.2와의 여유
A, B, C = 7.763, 0.755, 0.405 - (1/(3*r))**2
mus = (-B + math.sqrt(B*B - 4*A*C))/(2*A)
print("µ* = %.3f (저자 권고 µ<0.2 → 안전여유 %.0f%%)" % (mus, 100*(1-0.2/mus)))
assert abs(mus - 0.366) < 0.005
# 4) 평균 경도 애스퍼리티는 현실적 마찰로는 절대 Cu를 긁지 못한다
ra = Hp_avg/HCu
C2 = 0.405 - (1/(3*ra))**2
mu_avg = (-B + math.sqrt(B*B - 4*A*C2))/(2*A)
print("평균 패드경도(0.05 GPa)로 Cu를 긁으려면 µ = %.1f 필요 → 물리적으로 불가" % mu_avg)
assert mu_avg > 2.5
```

### (D) 발생원별 예측 치수·하중·궤적
```python verify
import math, numpy as np
HCu, Hp_max = 1.22e9, 0.31e9
def upper(R):                      # 상한 폭·깊이 (Cu, 최경 패드재)
    return 2*math.sqrt(Hp_max/HCu)*R, (Hp_max/HCu)*R
for name, R in (("슬러리 응집체 R=305 nm", 305e-9), ("패드 파편 R=17.5 µm", 17.5e-6),
                ("탈락 그릿 R=125 µm", 125e-6)):
    w, d = upper(R)
    print("%-22s 최대 폭 %8.3g m, 최대 깊이 %8.3g m" % (name, w, d))
w1, _ = upper(305e-9); w3, d3 = upper(125e-6)
assert abs(w1 - 3.07e-7) < 1e-8                     # 응집체: 폭 0.31 µm
assert w3/w1 > 400 and d3 > 30e-6                   # 그릿: 400배 이상 큰 폭, 깊이 30 µm 초과
# 탈락 그릿 1개가 Cu 박막(1 µm)을 관통시키는 데 필요한 하중 = π δ R H  (식(8))
for R in (50e-6, 125e-6, 175e-6):
    P = math.pi*1e-6*R*HCu
    print("R=%3.0f µm: 깊이 1 µm 절삭 하중 %.3f N, 반폭 %.1f µm" % (R*1e6, P, 1e6*math.sqrt(2*R*1e-6)))
F_wafer = 3*6894.757*math.pi*0.15**2                # 300 mm, 3 psi
P50, P175 = math.pi*1e-6*50e-6*HCu, math.pi*1e-6*175e-6*HCu
print("웨이퍼 총하중 %.0f N → 그릿 1개 몫은 %.3f~%.3f %%" % (F_wafer, 100*P50/F_wafer, 100*P175/F_wafer))
assert 1450 < F_wafer < 1470 and 100*P175/F_wafer < 0.05
# 패드에 박힌 입자의 웨이퍼면 궤적 (회전식 CMP 운동학)
rot = lambda th: np.array([[math.cos(th), -math.sin(th)], [math.sin(th), math.cos(th)]])
c = np.array([0.20, 0.0]); p = np.array([0.25, 0.0])   # 중심거리 0.20 m, 입자 위치(모델 가정)
def trace(wh_rpm, wp_rpm, T, N):
    wh, wp = wh_rpm*2*math.pi/60, wp_rpm*2*math.pi/60
    t = np.linspace(0, T, N)
    return t, np.stack([rot(-wh*ti) @ (rot(wp*ti) @ p - c) for ti in t])
t, q = trace(73, 73, 60/73, 2000)                      # 등속: 정확한 원
dev = np.abs(np.linalg.norm(q - p, axis=1) - np.linalg.norm(c))
print("등속(73/73 rpm): |궤적−입자점| = %.3f m 일정 (중심거리 %.3f m), 편차 %.1e m"
      % (np.linalg.norm(q[0]-p), np.linalg.norm(c), dev.max()))
assert dev.max() < 1e-12
t, q = trace(67, 73, 3.0, 30000)                       # 실제 조건(Kwon 2013: 헤드 67 / 플래튼 73 rpm)
r = np.linalg.norm(q, axis=1); inside = r <= 0.15
dq = np.gradient(q, t, axis=0); ddq = np.gradient(dq, t, axis=0)
Rc = np.linalg.norm(dq, axis=1)**3/np.abs(dq[:,0]*ddq[:,1]-dq[:,1]*ddq[:,0])
seg = np.linalg.norm(np.diff(q, axis=0), axis=1)
print("67/73 rpm: 웨이퍼 내부 곡률반경 %.2f~%.2f m (웨이퍼 반경 0.15 m), 3 s 동안 웨이퍼 위 궤적 %.2f m"
      % (Rc[inside].min(), Rc[inside].max(), seg[inside[:-1]].sum()))
assert Rc[inside].min() > 0.15 and seg[inside[:-1]].sum() > 0.5
```

## 9. 발생원 판별 규칙 (Lv3-2 역추적 규칙의 1차 초안)
| 관측 신호 | 슬러리 대입자·응집체 | 패드 파편 | 디스크 그릿 탈락 |
|---|---|---|---|
| 역산 반경 R_est = a_c²/2δ_c | **0.1–0.6 µm**(꼬리 6 µm) | 5–300 µm(평균 32–41 µm) | 50–175 µm(그릿 100–350 µm) |
| 실측/예측 폭 2a_c | 100 nm 내외(실측 평균 101 nm) | ~10 µm 급(예측) | 20–130 µm 급(예측) |
| 실측/예측 깊이 δ_c | 4–5 nm(실측) | ~4 µm(예측 상한) | 1 µm 이상, 상한 32 µm(예측) |
| 형상 유형 분포(산화막) | broken chatter 75.5 %, group 24.5 %, line 0 % | **group chatter 69 %**, broken 23 %, line 7.5 % | 대형 반원형 호 + 다중 stripe |
| 스크래치 수(≥2 µm, 기준 1.0) | **2.13 ± 0.79** | 1.39 ± 0.33 | (단일 입자로도 웨이퍼 관통 손상) |
| 궤적 | 짧고 산발 | 짧고 군집 | 곡률반경 0.24–0.50 m의 긴 호 |
| 1차 대응 | 슬러리 필터·LPC 꼬리 관리 | 컨디셔닝 방식(ex-situ·DIW 제트), 패드 경도 산포 | 디스크 본딩·검사, 디스크 교체 |

형상 유형 분포 행은 Kwon et al.(2013, Tribol. Lett.) Fig.3·Fig.7 막대 판독값이다
(기준 웨이퍼: broken chatter 67 %, group chatter 28 %, line 5 %). 핵심은 **패드 파편이 들어오면
group chatter 비율이 28 % → 69 %로 2.5배가 된다**는 것 — 저자 해석은 "크고 불규칙한 디브리는
웨이퍼와 접촉점이 여러 개라 다중 파괴를 일으킨다"이다. 반대로 건조 응집체는 기준 상태와 형상
분포가 거의 같아(broken chatter 지배) **형상으로는 구분되지 않고 개수로 구분된다** — 실리카
연마입자와 물성(경도)이 비슷하기 때문(Kwon et al. 2013).

계수 기준도 논문마다 다르다는 점을 명시해 둔다: Kwon(2013, Tribol. Lett.)의 정규화 스크래치 수는
**길이 ≥ 2 µm** 기준(Fig.6 범례)이고, Remsen et al.(2006)의 스크래치 계수는 **길이 ≥ 50 µm**
기준이다([[post-cmp-defect-classification-and-inspection]] §1.1). **두 문헌의 스크래치 밀도를
직접 비교하면 안 된다.**

## 10. 한계·미검증
- ⚠ 미검증: §9 표의 "패드 파편·탈락 그릿" 폭·깊이 열은 상한식(§3)에 크기를 대입한 **모델 예측**이다.
  해당 크기대의 스크래치 단면을 실측한 1차 문헌을 확보하지 못했다(Eusner 2009의 실측은 응집체
  영역뿐). 실제로는 막 두께에서 잘리거나 취성파괴로 전이해 상한보다 작을 수 있다.
- ⚠ 미검증: 상한식은 입자를 **구형·강체**로 본다. 다이아몬드 그릿은 다면체이고(Kwon 2013 Fig.9의
  stripe가 그 증거), 모서리 접촉은 같은 하중에서 더 깊게 파고든다. 다면체 보정계수는 확인 못 했다.
- ⚠ 미검증: chatter mark(스틱–슬립) 자체의 주기·진폭을 예측하는 정량모델은 확보하지 못했다.
  Kwon(2013)도 "the reason for the formation of chatter marks is still unknown"이라고 적었고,
  스틱–슬립설은 그 논문이 2차 인용한 가설이다.
- ⚠ 미검증(2차 인용): Kwon(2013, Tribol. Int.)이 인용한 Prasad et al.(2011) JES 158, H394
  "패드 디브리가 스크래치의 원인"은 원문을 확인하지 못했다.
- ⚠ 미검증: §8-D 궤적 계산의 중심거리 0.20 m·입자 위치 0.25 m는 **모델 가정값**이며 특정 장비의
  실측 치수가 아니다. 곡률반경 결론(웨이퍼 반경보다 크다)은 이 값에 대해서만 검증됐다.
- 저온·저압(ECMP 등) 조건, low-k 다공성 막의 취성파괴 모드는 이 노트의 소성긁기 틀 밖이다.
  Saka et al.(2010)도 "비구형 애스퍼리티 기하는 명시적으로 다루지 않았다"고 적었다.

## 11. 출처
1. **Saka, N., Eusner, T., Chun, J.-H. (2008)**, "Nano-scale scratching in chemical–mechanical
   polishing," *CIRP Annals — Manufacturing Technology* 57(1), 341–344.
   DOI: 10.1016/j.cirp.2008.03.098 — 1차, 전문 확보(미러 사이트 경유).
2. **Eusner, T., Saka, N., Chun, J.-H., Armini, S., Moinpour, M., Fischer, P. (2009)**,
   "Controlling Scratching in Cu Chemical Mechanical Planarization," *J. Electrochem. Soc.*
   156(7), H528–H534. DOI: 10.1149/1.3121964 — 1차, 전문 확보. 스크래치 32건 실측 원자료.
3. **Saka, N., Eusner, T., Chun, J.-H. (2010)**, "Scratching by pad asperities in
   chemical–mechanical polishing," *CIRP Annals* 59(1), 329–332. DOI: 10.1016/j.cirp.2010.03.113
   — 1차, 전문 확보. 마찰-경도 긁기 기준.
4. **Kwon, T.-Y., Cho, B.-J., Ramachandran, M., Busnaina, A.A., Park, J.-G. (2013)**,
   "Investigation of Source-Based Scratch Formation During Oxide Chemical Mechanical
   Planarization," *Tribology Letters* 50, 169–175. DOI: 10.1007/s11249-012-0098-2
   — 1차, 전문 확보. 발생원 3종 투입 실험·형상 분류.
5. **Kwon, T.-Y., Ramachandran, M., Cho, B.-J., Busnaina, A.A., Park, J.-G. (2013)**,
   "The impact of diamond conditioners on scratch formation during CMP of silicon dioxide,"
   *Tribology International* 67, 272–277. DOI: 10.1016/j.triboint.2013.08.008 — 1차, 전문 확보.
   패드 디브리 크기 분포·농도 효과.
6. **US 6,884,155 B2**, "Diamond grid CMP pad dresser," Kinik Co.(Chien-Min Sung 외),
   등록 2005-04-26 — 1차(특허). 그릿 탈락 기전·규격.
7. **Pysher, D., Goers, B., Zabasajja, J. (2010)**, "Design, Characteristics and Performance of
   Diamond Pad Conditioners," *MRS Symp. Proc.* 1249, 1249-E02-04.
   DOI: 10.1557/proc-1249-e02-04 — 업체 기술문서(MRS 수록). DOP·결함 실측.
8. Remsen, E.E. et al. (2006), *J. Electrochem. Soc.* 153(5), G453. DOI: 10.1149/1.2184036
   — 본 노트에서는 LPC 임계(0.68 µm)와 계수 기준만 인용. 상세는
   [[post-cmp-defect-classification-and-inspection]], [[lpc-scratch-density-tail-correlation]].
