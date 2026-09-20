<!-- V2-SECTION: R4-disk | 분배완료 2026-09-08 | 근거: asperity-regeneration, diamond, disk-design, grit, 다이아 | 정본: ARCHITECTURE-V2.md §3 -->
# 다이아몬드 그릿 규격(메시·형상·품질)과 본딩 기술(브레이징 vs 전착) 비교

> disk-design Lv1-1. [[conditioner-grit-design-space]] [[conditioning-mechanism-asperity-regeneration]]
> [[conditioner-disk-pad-cutting-model]] 상호링크. 부모 노트인 conditioner-grit-design-space가 이미
> "설계공간(finish×aggressiveness)"과 CVD 본딩(Entegris Planargem)을 다뤘으므로, 본 노트는 겹치지
> 않는 두 영역 — (1) 메시/입경 규격 자체의 정량 정의, (2) 브레이징·전착 두 본딩 방식의 공정 파라미터·
> 성능 정량 비교 — 에 집중한다.

## 1. 출처
1. Chien-Min Sung, "Brazed diamond tools and methods for making the same," US Patent
   8104464B2 (priority 1997-04-04, granted 2012-01-31).
   https://patents.google.com/patent/US8104464B2/en — 브레이징 본딩의 1차 출처(특허 명세서
   실시예에 조성·온도·치수 수치 다수 포함).
2. Asahi Diamond Industrial Co., Ltd., "CMP conditioner and method of manufacturing the
   same," Japanese Patent JP4508514B2. https://patents.google.com/patent/JP4508514B2/en
   — 전착(electroplating) 본딩의 1차 출처. CMP 컨디셔너 전용 특허라 실시예에 패드 제거율
   실측 데이터(n=20)까지 포함되어 있어 disk-design 지식베이스에 가장 직접적인 1차 출처.
3. 교차 확인용(본문 미인용, Lv2 보강용으로 존재만 확인): Y. Zhang et al., "Promoting the
   bonding strength and abrasion resistance of brazed diamond using Cu–Sn–Ti composite
   alloys reinforced with tungsten carbide," Diamond and Related Materials (2021),
   DOI: 10.1016/j.diamond.2021.108239 — find_open_access.py 조회로 실존 확인(Crossref
   등재), 본문 수치는 아직 미검토(미검증, Lv2에서 브레이징 계면 결합강도 정량화 시 사용 예정).

## 2. 그릿 메시 규격 → 물리적 입경 변환
- US8104464B2 실시예 서술: "coarse-sized powders, i.e. greater than 400 U.S. mesh or 34
  microns, are preferred" — 특허가 직접 **400 mesh ≈ 34 µm**로 명시.
- 업계 통용 체눈 규격표(ASTM E11 계열, 다수 연마재 카탈로그에 반복 등장하는 공칭값)에서는
  400 mesh 공칭 눈금이 약 **38 µm**로 알려져 있다. 특허값(34 µm)과 통용표값(38 µm) 사이
  약 **10.5%** 차이 — §5 코드에서 재현·대조. 원인은 "체눈 규격(눈금 자체 치수)"과 "그 체를
  실제로 통과하는 입자의 등가 지름(체 대각선 통과 가능한 최대 크기는 눈금보다 클 수 있음)"의
  정의 차이로 추정되나, 특허 본문은 이를 설명하지 않아 **미검증**으로 남긴다.
- 실시예에 쓰인 입도 표기: 40/50 mesh, 30/40 mesh (예: De Beers SDA-85+, SDA-100+, General
  Electric MBS-960). "40/50"과 같은 두 숫자 표기는 업계에서 "40 mesh 체는 통과하고 50 mesh
  체에는 걸러지는 입도 구간"을 뜻하는 관용 표기이나, 이 특허 자체가 그 정의를 명문화하지는
  않는다(정의는 업계 상식으로 통용 — **미검증**, 특허 문언으로 확인된 것은 숫자 표기 자체뿐).
- JP4508514B2 실시예는 mesh 대신 **평균 입경을 µm로 직접 지정**한다: 실시예1 180 µm, 실시예2
  280 µm. CMP 컨디셔너 전용 특허가 소잉(saw)용 브레이징 특허보다 더 좁은 입도 분포·직접적인
  µm 표기를 선호하는 경향(정성적 관찰, 두 특허 각 1건씩 비교한 것이므로 일반화는 **미검증**).

## 3. 그릿 형상·등급(grade)과 농도(concentration)
- US8104464B2: "abrasive particles of any shape, including euhedral, or naturally shaped
  particles" — 형상 스펙트럼을 자형(euhedral, 팔면체 등 결정형 그대로) ~ 파쇄형(naturally
  shaped, 불규칙 파쇄)까지 넓게 인정. 상업 등급명 De Beers **SDA**(Saw Diamond Abrasive,
  톱날/소잉 특화 — 상대적으로 인성이 높은 블록형 결정) vs GE **MBS**(Metal Bond Synthetic,
  금속본드 전용 등급)가 실시예에 병기되어, "본딩 방식에 맞춰 최적화된 grit grade가 실재한다"는
  정성적 근거는 확보. 다만 SDA/MBS의 정량적 인성지수(toughness index, TI)나 파쇄강도(kgf 등)
  자체는 특허에 없음(**미검증**).
- 다이아몬드 농도(concentration) 실측 표기: "diamond concentration of 20 (5% of total
  value)" — 업계 표준 정의(Concentration 100 = 4.4 carat/cm³ ≈ 부피비 25%)를 적용하면
  Concentration 20 → 20/100 × 25% = **5 vol%**로 특허 문언과 정확히 일치. 이는 특허 자체가
  이미 괄호로 명시한 값과 업계 표준 공식이 서로 어긋나지 않음을 재확인하는 수준의 대조이며
  (특허가 독립적으로 두 표기를 병기했으므로 완전한 외부검증은 아님), §5에서 계산으로 재현한다.

## 4. 본딩 기술 비교 — 브레이징(active-metal brazing) vs 전착(electroplating)

### 4.1 브레이징
- 대표 합금: NICROBRAZ LM (Ni–Cr–B–Si–Fe: Cr 7 wt%, B 3.1 wt%, Si 4.5 wt%, Fe 3.0 wt%,
  C ≤ 0.06 wt%, 잔부 Ni). 특허 본문 내에서도 액상선(liquidus) 온도가 실시예별로 **970–
  1000°C**와 **1010–1013°C** 두 가지로 다르게 기재되어 있음 — 같은 상품명 합금인데 특허 내
  자체 불일치, 원인 불명(**미검증**).
- 공정 온도: 액상선보다 약 50°C 높게, 전체 공정은 다이아몬드 흑연화를 막기 위해 **1,100°C
  미만** 유지. 진공(~10⁻⁵ torr) 또는 불활성(Ar, N₂)/환원(H₂) 분위기.
- 브레이즈 포일 두께 0.001″(~25.4 µm)~0.002″(~50.8 µm), 실시예 중 하나는 **100 mm 지름/
  50 mm 중심홀**의 환형(annular) 디스크 형태 — 실제 CMP 컨디셔너 디스크(200 mm 웨이퍼 공정
  표준 디스크는 대략 이 치수대)와 정합하는 기하 형태.
- 결합 메커니즘은 그릿-합금 계면의 화학반응(탄화물 형성 등)에 의한 야금학적 결합으로 서술되며,
  기계적 파지(전착의 매트릭스 감싸기)보다 결합력이 강하다고 주장되나 정량 수치(전단강도 등)는
  이 특허에 없음(Lv2에서 §1의 DOI 10.1016/j.diamond.2021.108239로 보강 예정, **미검증**).

### 4.2 전착
- Ni 설파메이트(sulfamate) 도금욕, 전류밀도 1~2 A/dm², 10~21시간.
- 도금 두께 실측 3점: 실시예1 1 A/dm²·21h → 250 µm, 비교예(종래설계) 1 A/dm²·10h → 125 µm,
  실시예2 2 A/dm²·21h → 500 µm. 패러데이 법칙(도금속도 ∝ 전류밀도)과의 정합성을 §5에서
  코드로 재현·대조.
- 종래기술(특허가 인용하는 선행문헌 JP10-15819호 서술): 그릿 탈락 방지를 위해 깊이 매립하면
  돌출량이 입경의 **5~30%**로 제한되어 슬러리 배출이 나빠짐.
- 본 발명(JP4508514B2): 도금층에 볼록 돌기를 만들어 돌기마다 그릿 1개씩 배치 — 돌기 평평부
  기준 그릿 팁까지 평균 높이가 입경의 **0.3~1.5배(30~150%)**로, 매립 깊이(탈락 방지)와
  돌출량(연삭력)을 동시에 확보한다고 주장.
- 성능 비교(패드 제거율, 표본 n=20): 실시예1 **156±8.6 µm/h**, 실시예2 **170±9.0 µm/h**,
  비교예(종래) **130±18.0 µm/h**. 발명 설계가 평균 제거율은 20~30% 높고, 변동계수(CV=
  표준편차/평균)는 종래 13.8%에서 발명 5.3~5.5%로 약 2.5배 개선(JP4508514B2 실시예/비교예
  대조, §5에서 계산 재현).

## 5. 재현·검증 (python)

```python verify
# 1) 메시 ↔ 마이크론 변환: 특허값 vs 업계 통용 체눈 표(ASTM E11 계열 공칭값)
patent_400mesh_um = 34.0     # US8104464B2 본문
standard_400mesh_um = 38.0   # 업계 통용 참조표(비-API, 다수 연마재 카탈로그 공칭값)
diff_pct = abs(patent_400mesh_um - standard_400mesh_um) / standard_400mesh_um * 100
assert 5 < diff_pct < 15, f"400 mesh 환산 차이가 예상 범위(5~15%) 밖: {diff_pct:.1f}%"
print(f"400 mesh 환산 차이: {diff_pct:.1f}% (정의 차이 추정, 미검증)")

# 2) 다이아몬드 농도(concentration) 정의 재현
concentration_100_volpct = 25.0  # 업계 표준: Concentration 100 = 4.4 ct/cm^3 ~= 25 vol%
concentration = 20
vol_pct = concentration / 100 * concentration_100_volpct
assert abs(vol_pct - 5.0) < 0.01, f"Concentration 20 -> {vol_pct} vol%, 특허 명시값 5%와 불일치"

# 3) 전착 도금속도 — 패러데이 법칙(속도 ∝ 전류밀도) 재현
rate_ex1 = 250 / 21    # µm/h, 1 A/dm^2
rate_comp = 125 / 10   # µm/h, 1 A/dm^2 (비교예)
rate_ex2 = 500 / 21    # µm/h, 2 A/dm^2
assert abs(rate_ex1 - rate_comp) / rate_comp < 0.10, "동일 전류밀도 두 실시예의 도금속도가 10% 이상 차이"
assert abs(rate_ex2 - 2 * rate_ex1) / (2 * rate_ex1) < 0.05, "전류밀도 2배 시 도금속도 2배 기대치와 5% 이상 불일치"

# 4) 균일도(변동계수 CV) 비교 — 발명 vs 종래
cv_ex1 = 8.6 / 156
cv_ex2 = 9.0 / 170
cv_comp = 18.0 / 130
assert cv_comp > cv_ex1 and cv_comp > cv_ex2, "발명 실시예의 변동계수가 종래 대비 개선되지 않음"
print(f"CV: 실시예1={cv_ex1:.3f}, 실시예2={cv_ex2:.3f}, 비교예={cv_comp:.3f}")
```

## 6. Lv1-2·Lv2 연결점
- 전착 protrusion 데이터(입경의 0.3~1.5배)와 브레이징 concentration 데이터(20→5 vol%)는
  [[conditioner-grit-design-space]] §6이 예고한 "D_grit → GW 파라미터(η, β)" 매핑 체인의
  구체적 입력 후보다. 특히 protrusion ratio 상한(1.5배)·하한(0.3배)은 [[conditioning-
  mechanism-asperity-regeneration]]의 GW 접촉모델에서 asperity 높이 분포의 물리적 경계로
  쓸 수 있을 것으로 보인다(모델 결합은 아직 미시도, Lv1-2 과제).
- 브레이징(화학결합 파괴로 탈락)과 전착(Ni 매트릭스 소성변형/피로로 탈락)은 그릿 탈락
  메커니즘 자체가 다를 가능성이 있어, [[conditioner-disk-pad-cutting-model]]의 수명 모델이
  본딩 방식별로 다른 파라미터를 요구할 수 있다(**미검증**, 후속 조사 필요 — 특허 어디에도
  탈락 메커니즘의 정량 수명식은 없음).

## 7. 미검증 사항 정리 (정직 표기)
- NICROBRAZ LM 액상선 온도: 특허 내 970–1000°C vs 1010–1013°C 불일치, 원인 불명.
- 400 mesh ↔ µm 변환: 특허(34 µm) vs 업계 통용표(38 µm) 약 10.5% 차이, 정의 차이로 추정하나
  확정 못함.
- mesh 두 숫자 표기(예: 40/50)의 정확한 체 통과 정의는 이 두 특허 어디에도 명문화되어 있지
  않음(업계 상식으로 통용되는 정의를 차용).
- SDA/MBS 등급의 정량적 인성·강도 지수 미확보.
- 브레이징 계면 결합력의 정량치(전단강도 등, MPa 단위) 미확보 — DOI
  10.1016/j.diamond.2021.108239 논문 본문 검토로 Lv2에서 보강 예정.
