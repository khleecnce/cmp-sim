<!-- V2-SECTION: R1-equipment | 공동: R4-disk | 분배완료 2026-09-08 | 근거: carrier, kinematic, platen, retaining ring, tool-architecture | 정본: ARCHITECTURE-V2.md §3 -->
# CMP 장비 구조 — 헤드/플래튼/리테이너링/컨디셔너

> 담당: [[process-integrator]] Lv1-1 · 작성 2026-09-03 · 상태: 검증(출처 기재)
> 연결: [[cmp-kinematics-rotary]] · [[cmp-wiwnu-basics]]

## 1. 주요 구성 (rotary polisher)
회전식 CMP 장비의 최소 구성 요소는 넷이다.

| 요소 | 역할 | 전형값 |
|---|---|---|
| **플래튼(platen) + 패드** | 회전 원판 위에 폴리싱 패드 부착. 웨이퍼 대비 훨씬 큼 | 실험용 300mm 알루미늄 플래튼[1]; 양산은 웨이퍼 지름의 2~3배 |
| **캐리어 헤드(carrier head)** | 웨이퍼를 **면을 아래로** 잡고 하중을 가하며 자전 | 짐벌(gimbal) 기구로 플래튼과 평행 정렬[1] |
| **리테이너 링(retaining ring)** | 웨이퍼 이탈 방지 + **엣지 압력 보정** | 헤드와 독립 가압 |
| **컨디셔너(diamond disk)** | 패드 표면 재생(글레이징 제거·asperity 회복) | in-situ 또는 ex-situ[2] |

슬러리는 패드 위에 적하되어 회전으로 계면에 끌려 들어간다. 웨이퍼와 패드는
**보통 같은 방향으로** 회전한다[2] — 이 사실이 [[cmp-kinematics-rotary]]에서
"동속이면 상대속도 균일"이 성립하는 전제다(부호가 같아야 ω_w-ω_p=0이 의미를 가짐).

## 2. 캐리어 헤드: 플렉시블 멤브레인과 존별 압력제어
초기 헤드는 웨이퍼 뒷면에 backing film을 대고 강체로 눌렀으나, 현대 헤드는
**가압 챔버를 만드는 유연 멤브레인(flexible membrane)** 을 쓴다.

- US6183354B1 (Applied Materials, "Carrier head with a flexible membrane for a CMP system"):
  housing / base / loading mechanism / gimbal mechanism / substrate backing assembly로 구성.
  멤브레인이 base 아래로 뻗어 **챔버**를 형성하고, 그 하면이 웨이퍼 장착면이 된다[3].
- US6244942B1 (AMAT, "Carrier head with a flexible membrane and **adjustable edge pressure**"):
  retaining ring 또는 spacer ring에 돌기(projection)/홈(indentation)을 두어
  **멤브레인 가장자리 압력을 중앙과 다르게** 만든다[4].
  → "존별 압력제어"의 초기 형태. 이후 세대는 동심 챔버를 여러 개(멀티존) 두어
  반경별 down-force를 독립 조절한다.

멀티존 멤브레인의 의의: 리뷰[2]는 **WIWNU에 가장 지배적인 인자가 멤브레인 가압의
균일도**이며, 고성능 멀티존 멤브레인 구조 개발이 슬러리 사용량 절감·수율 향상의
핵심 연구방향이라고 정리한다. (WIWNU가 나쁘면 최악 지점을 맞추느라 폴리싱
시간이 늘고 → 웨이퍼당 슬러리 소모가 비례 증가[2].)

## 3. 리테이너 링 — 왜 엣지가 문제인가
웨이퍼 엣지에서는 패드가 압축 상태로 진입/이탈하며 응력이 불연속이 되어
제거율이 튀거나 죽는다(edge roll-off / edge fast). 리테이너 링은 웨이퍼 바로 바깥에서
패드를 **미리 눌러** 이 불연속을 완화한다. 문헌은 링이 "기계적으로 웨이퍼를 잡을 뿐
아니라 **엣지 영역의 폴리싱 압력을 보정(calibrate)** 한다"고 명시한다[5].
링과 패드의 **접촉각(contact angle)** 이 엣지 MRR 프로파일과 WIWNU를 좌우한다는
연구도 있다[6]. → Phase 1 엣지 모델링 시 링 압력·접촉각을 파라미터로 둘 것.
(정량 관계식은 아직 **미검증** — 원문 미확보, 초록 수준만 확인.)

## 4. 대표 공정 조건 (문헌 실측 범위)
Lai(MIT, 2001)의 Cu blanket CMP 실험 조건[1]:

| 항목 | 값 |
|---|---|
| 웨이퍼 | 100mm Si / TiN 20nm / PVD Cu 1µm |
| 수직하중 / 압력 | 108, 379 N / **14, 48 kPa** |
| 회전수 | 5 – 420 rpm |
| 상대속도 | 0.05 – 3.91 m/s (전형 0.8 m/s) |
| 슬러리 | α-Al2O3, pH 7, 점도 0.03 Pa·s, 2–3 vol% |
| 유량 | 150 – 250 mL/min |
| 패드 | Rodel IC1400 (IC1000 top), 폴리우레탄, 57 shore D, 밀도 750 kg/m³, 기공 20–60µm, K-groove 250µm폭×375µm깊이×1.5mm피치 |

→ 시뮬레이터 기본 파라미터 세트의 출발점으로 이 값을 채택한다.

## 5. 패드 수명 (컨디셔닝 연결)
`T_life = C · G / PCR²`  (G=그루브 깊이, PCR=pad cut rate, C=그루브 사용한계 비율 0≤C≤1)[2].
낮은 PCR·깊은 그루브가 수명을 늘리지만, 실제 수명을 결정하는 건 부적절한 컨디셔닝에 의한
**프로파일 조기 열화**다[2]. → [[disk-conditioner]] 에이전트 Lv1 소재.

## 6. 정량 재현 — §4 압력값 (Lai 2001 Ch.2)
Lai 논문[1]은 하중(N)과 압력(kPa)을 함께 보고한다. 100mm 웨이퍼 전면적을
접촉면적으로 가정하고 P=F/A로 역산하면 문헌 표의 압력값과 일치하는지 확인할 수 있다.

```python verify
import math

# 문헌값 (papers/mit_lai_ch2.pdf, Ch.2 실험조건 표 — 하중 N, 압력 kPa 두 열)
wafer_diameter_mm = 100.0
loads_N = [108.0, 379.0]
lit_pressures_kPa = [14.0, 48.0]

radius_m = (wafer_diameter_mm / 1000.0) / 2.0
area_m2 = math.pi * radius_m ** 2  # 100mm 웨이퍼 전면적 가정

for F, P_lit in zip(loads_N, lit_pressures_kPa):
    P_calc_kPa = (F / area_m2) / 1000.0
    err_pct = abs(P_calc_kPa - P_lit) / P_lit * 100
    print(f"F={F}N -> P_calc={P_calc_kPa:.2f}kPa vs 문헌 {P_lit}kPa (오차 {err_pct:.1f}%)")
    # 웨이퍼 전면적 가정 하 5% 이내 재현 — 문헌이 유효접촉면적을 그대로 썼다는 뜻
    assert err_pct < 5.0, f"압력 재현 실패: {err_pct:.1f}% 오차"

print("PASS: 100mm 웨이퍼 전면적 가정으로 하중->압력 환산이 문헌값과 5% 이내 일치")
```

두 지점 모두 재현되므로, Lai가 압력을 "웨이퍼 전체 투영면적 기준 공칭압력"으로
정의했음을 역산으로 확인했다(원문에 면적 계산식이 명시되지 않아 이 역산이
유일한 검증 경로였다). §5의 `T_life = C·G/PCR²` 식은 원문에 대입 예시 수치가
없어 **미검증**으로 남긴다 — 구성 요소(C, G, PCR)의 개별 문헌값을 아직 확보하지
못했다.

## 출처
1. J.-Y. Lai, *Mechanics, Mechanisms, and Modeling of the CMP Process*, PhD thesis, MIT, Ch.2, 2001. https://web.mit.edu/cmp/publications/thesis/jiunyulai/ch2.pdf (papers/mit_lai_ch2.pdf)
2. H. Lee et al., "Approaches to Sustainability in Chemical Mechanical Polishing (CMP): A Review", *Int. J. Precis. Eng. Manuf.-Green Tech.*, 2021. https://pmc.ncbi.nlm.nih.gov/articles/PMC8617369/
3. US 6,183,354 B1, "Carrier head with a flexible membrane for a chemical mechanical polishing system", Applied Materials. https://patents.google.com/patent/US6183354B1/en
4. US 6,244,942 B1, "Carrier head with a flexible membrane and adjustable edge pressure", Applied Materials. https://patents.google.com/patent/US6244942B1/en
5. "Prediction of polishing pressure distribution in CMP process with airbag type wafer carrier", *CIRP Annals*, 2017. https://www.sciencedirect.com/science/article/abs/pii/S0007850617300884 — **전문 확보**(저자최종본, 나고야대 리포지토리 OA): `papers/prediction-of-polishing-pressure-distribution-in-cmp-process.pdf`
6. "Effect of contact angle between retaining ring and polishing pad on material removal uniformity in CMP process", *Int. J. Precis. Eng. Manuf.*, 2013. https://link.springer.com/article/10.1007/s12541-013-0204-x (초록만 확인 — 정량값 미검증)
