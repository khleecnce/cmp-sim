# 옥사이드 CMP 메커니즘: 수화층 형성과 화학-기계 결합 모델 (film-oxide Lv1-2)

> film-oxide Lv1-2 | 작성일: 2026-09-08
> 선행: [[film-oxide-teos-hdp-bpsg-sod-density-hardness]] (Lv1-1)

## 1. 왜 이 단원이 필요한가

Lv1-1에서 Cook 1990을 2.1절까지만 읽고 수화층 두께 정량값 미확인으로 남겼다.
이 단원은 Cook 1990 3절(화학 반응 메커니즘 본문, p.157-161)을 완독하고, 여기서 나온
1990년 시점의 이론적 확산 모델이 2015년 SIMS 실측(Suratwala et al.)으로 실제 검증됐는지
교차확인한다.

## 2. 1차 출처

- Lee M. Cook (Galileo Electro-Optics Corp.), "Chemical Processes in Glass Polishing,"
  Journal of Non-Crystalline Solids, vol. 120, pp. 152-171, 1990.
  DOI: 10.1016/0022-3093(90)90200-6 (Crossref 확인). 미러 사이트 경유 원문 확보 (기존 보유,
  papers/cook1990-chemical-processes-glass-polishing.pdf), 이번엔 3절 전체(p.157-161,
  Water-silica reactions ~ Aqueous reactions with other glass constituents) 직접 읽음.
- T. Suratwala, R. Steele, L. Wong, M. Feit, P.E. Miller, R. Dylla-Spears, N. Shen,
  R. Desjardin (Lawrence Livermore National Laboratory), "Chemistry and Formation of the
  Beilby Layer During Polishing of Fused Silica Glass," Journal of the American Ceramic
  Society, 98(8), 2015, pp. 2371-2379.
  DOI: 10.1111/jace.13659 (Crossref API로 직접 조회 확인, 저자 연도 저널 일치).
  공개 저자원고본(LLNL-JRNL-666384)을 OSTI(미 에너지부 공개 리포지토리,
  osti.gov/servlets/purl/1234587)에서 원문 PDF로 무료 확보, 전체 24쪽 직접 읽음.
  Cook 1990의 이론 모델을 25년 뒤 SIMS로 실측 검증한 후속 논문 - 이 노트의 핵심 교차검증 축.

## 3. Cook 1990 - 수화층 형성 화학 반응식 (3.1절)

핵심 반응식(원문 eq.12-15, 그대로 인용):

- 실란올 산-염기 평형: Si-OH <-(K1)-> Si-OH2+ <-(K2)-> Si-O- (eq.12) - 왼쪽은 Bronsted 산,
  오른쪽은 Bronsted 염기. 실리카의 pK1 약 -2 (강산 쪽으로 치우침).
- 축합(network 형성): Si-O- + Si-OH -> Si-O-Si + OH- (eq.14) - 반응속도는 표면 Si-O-
  농도에 정비례.
- 가수분해(수화층 형성, eq.14의 역반응): Si-O-Si + H2O -> 2 Si-OH (eq.15) - 이것이
  수화층의 화학적 정의: siloxane 결합이 물과 반응해 실란올로 끊어지는 것.
- pH=9.8에서 두 종(Si-OH2+, Si-O-)이 등몰 농도 - 이 pH가 세리아 지르코니아 연마제의 최대
  연마속도 최대 평활도 pH와 일치한다고 원문이 서술(정성적 상관, 정량 근거는 별도 인용
  Izumitani 1,16 - 이 노트에서 원문 미확보, 2차 인용).

실란올 밀도(정량, 원문 3.1절):
- 완전 수화된 괴상(massive) 유리질 실리카: 4.6 OH/nm^2 (Cook이 인용한 문헌값, 원문 각주
  22,23 - 이 노트에서 원논문 미확보, 2차 인용)
- 실리카 겔(silica gel): 약 8 OH/nm^2
- pH=7에서 표면 Si-O- 분율은 전체 실란올의 9%
## 4. Cook 1990 - 물 확산계수와 두 가지 메커니즘 (3.1절, Fig.6)

원문이 Lanford 등(N-15 핵반응 분석, 90도C 물 노출)의 실측을 인용해 두 개의 서로 다른
확산 메커니즘을 구분:

| 메커니즘 | 확산계수 D | 물리적 해석 |
|---|---|---|
| 빠른(fast) | 1e-15 cm^2/s (90도C) | 분자상 물(H2O)이 유리 구조 속으로 빠르게 확산 |
| 느린(slow) | 6e-18 cm^2/s (90도C) | Si-O-Si 결합이 서서히 끊어져 말단 실란올(SiOH) 형성 |

상온(ambient) 스케일에서는 D 약 1e-19 cm^2/s, 90도C에서는 D 약 1e-18 cm^2/s (원문 실측값).
활성화에너지는 550도C 이상에서 약 80 kJ/mol, 그 이하 온도에서 약 40 kJ/mol로 두 구간에서
다르다(Wakabayashi 및 Tomozawa 데이터, 2차 인용).
## 5. Cook 1990 - 확산 깊이 계산과 실측 폴리싱층 두께의 일치 (3.1절, Fig.8, Appendix 1)

Cook은 Fick 확산 근사식 depth ~ (2Dt)^(1/2)를 이용해, 실리카 입자가 표면을 지나가는
접촉 시간(dwell time) 동안의 물 침투 깊이를 계산했다(Appendix 1, 원문에 세부 파라미터
미기재 - 표면온도 200도C, 연마속도 5 cm/s 가정만 본문에 명시).

결과: 계산된 확산 깊이 = 0.5~12 nm (입자 지름 압력에 따라 변화, Fig.8).
원문 인용: The calculated diffusion depths are in excellent agreement with measurements
showing polishing layer thicknesses to be 1-20 nm in thickness.
정량 재현 요약(Cook 1990 원문 명시값 기준): 계산값 0.5-12 nm 대 실측 문헌값 1-20 nm는
1-12 nm 구간에서 겹쳐 원문이 주장한 일치가 수치로 확인된다(8절 코드 검증 (A) 참고,
미검증 아님 - 두 수치 모두 Cook 1990 원문 직접 인용).

즉 Cook의 1990년 시점 결론은 이론 계산(0.5~12nm)과 당대 실측(1~20nm)이 오더 수준에서
일치한다는 것 - 단, 실측의 출처는 Cook 자신의 후속 연구(Cook 등, 원문 각주 29,
BK7 표면 depth profile)이며 이 노트에서 원문 미확보(2차 인용).
## 6. Suratwala 2015 - 25년 뒤 SIMS로 직접 검증 (Cook 모델과의 교차확인)

Suratwala 2015는 Cook 1990이 이론으로만 제시했던 수화층에 물이 실제로 침투한다는
가설을 SIMS(Secondary Ion Mass Spectroscopy)로 직접 측정해 최초로 실험 확인했다.
원문 인용: To the authors best knowledge, this is the first experimental confirmation of
H2O penetration into glass surface during polishing, confirming previous hypothesized
hydration processes during polishing.
핵심 실측 결과:
- H(수소, H2O 유래로 해석) 표면농도: 1~3e20 atoms/cm^3 (즉 10,000~30,000 ppm)
- Bulk 실리카 Si 농도: 2e22 atoms/cm^3 (균일)
- Bielby층 두께: Ce(세리아) 침투 깊이로 정의(SIMS 노이즈 플로어 약 1e16 atoms/cm^3 기준)
  하여 약 50 nm - Cook의 이론 예측 범위(0.5~12nm 확산깊이, 1~20nm 실측 폴리싱층)보다
  한 자릿수 정도 두껍다. 단, Suratwala는 Ce 침투를 확산이 아닌 화학 반응성 메커니즘으로
  설명하므로 Cook의 순수 확산 모델과 직접 비교 대상이 아닐 수 있다 - 미검증(두 메커니즘이
  정의하는 층 두께가 물리적으로 동일한 대상인지 확인 못 함).
- K(칼륨, KOH pH조절제 유래) 침투 깊이: 500~900 nm - Ce보다 훨씬 깊고, 제거속도
  증가시 침투 감소(2단계 확산 모델로 설명, Fick 제2법칙 기반).
- Ce 침투 깊이: 20~100 nm - 제거속도 증가시 침투도 증가(확산이 아니라 계면
  마찰열에 의한 온도상승으로 인한 Ce-O-Ce/Si-O-Si 가수분해 반응비 증가로 설명, 활성화에너지
  E=10 kcal/mol 최적합).

K와 Ce가 반대 경향을 보인다는 것이 이 논문의 핵심 발견 - 즉 수화층은 단일 메커니즘이
아니라, 종에 따라 Cook식 확산 지배 메커니즘과 계면온도 의존 화학반응 지배 메커니즘이
공존한다. Cook 1990이 제시한 것은 물(H2O) 자체의 거동이며, Suratwala 2015는
이를 실측으로 확인하는 동시에 불순물(K, Ce)에는 별도 메커니즘이 필요함을 보였다.
## 7. film-oxide 실무 함의 - Kp 분화와의 연결

Lv1-1에서 확인한 Kp는 화학 반응성에 의존한다는 정성적 결론에, 이 단원은 정량적 반응
경로를 붙인다:
1. 수화(가수분해, eq.15)로 siloxane망이 실란올로 끊어져 기계적으로 약해진 표면층이 형성.
2. 이 층의 두께(Cook: 0.5~20nm, Suratwala: Ce기준 50nm)가 Kp에 영향을 줄 후보 변수.
3. 도핑막(BPSG/PSG, Lv1-1 4절)이 미도핑막과 다른 Kp를 갖는 이유는, 도핑이 Si-O-Si 망목
   구조 자체(가교밀도)를 바꿔 3절의 반응식(eq.12-15)의 평형점(K1, K2)이 이동하기 때문일
   가능성이 있다 - 단 이는 이 노트의 추정이며, Wei 2010은 화학적 효과라고만 서술하고
   구체 메커니즘을 밝히지 않았다(Lv1-1 6절). 미검증(추정).
## 8. 정량 재현 (sanity check)

```python verify
cook_calc_depth_min_nm = 0.5
cook_calc_depth_max_nm = 12.0
cook_measured_depth_min_nm = 1.0
cook_measured_depth_max_nm = 20.0

overlap_min = max(cook_calc_depth_min_nm, cook_measured_depth_min_nm)
overlap_max = min(cook_calc_depth_max_nm, cook_measured_depth_max_nm)
assert overlap_min < overlap_max
print(f"Cook 1990: 계산 {cook_calc_depth_min_nm}-{cook_calc_depth_max_nm}nm vs "
      f"실측 {cook_measured_depth_min_nm}-{cook_measured_depth_max_nm}nm, "
      f"겹치는 구간 {overlap_min}-{overlap_max}nm - 원문 주장 확인")

h_surface_conc = 2e20
si_bulk_conc = 2e22
h_si_ratio = si_bulk_conc / h_surface_conc
assert 90 <= h_si_ratio <= 110
print(f"Suratwala 2015: Si:H = {h_si_ratio:.0f}:1")

d_fast = 1e-15
d_slow = 6e-18
order_diff = d_fast / d_slow
assert order_diff > 100
print(f"fast/slow 확산계수 비 = {order_diff:.0f}배")

suratwala_bielby_nm = 50.0
assert suratwala_bielby_nm > cook_calc_depth_max_nm
ratio_thicker = suratwala_bielby_nm / cook_calc_depth_max_nm
print(f"Suratwala Bielby층이 Cook 계산 최대값보다 {ratio_thicker:.1f}배 두꺼움")
```
## 9. 남은 미검증 항목 (다음 단원 또는 후속 조사 필요)

- Cook 1990 Appendix 1의 확산깊이 계산 세부 파라미터(입자별 접촉시간 압력 구간)는 OCR로
  본문 수식이 깨져(예: eq.13 nb 공식) 이 노트에 코드로 재현하지 않았다. 미검증(원문 수식
  OCR 손상, 재현 보류).
- Cook이 인용하는 실란올 밀도(4.6/nm^2, 8/nm^2) 원출처(Iler 1979 추정, 원문 각주 22)는
  이 노트에서 미확보 - 2차 인용.
- Suratwala의 K 침투 500-900nm과 Ce 침투 20-100nm의 정확한 개별 실험값(Table 1)은
  이 노트에서 표 전체를 옮기지 않았다 - 필요시 원문 재확인.
- 7절의 도핑이 K1/K2 평형을 이동시킨다는 명제는 이 노트의 추정이며 직접적 문헌 근거 없음.

## 10. 다음 단원

Lv2-1(ILD CMP: 다층 배선 평탄화)에서 이 수화층 메커니즘이 실제 다층 구조의 국소/전역
평탄화에 어떻게 연결되는지 다룬다.
