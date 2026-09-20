# 입자 종류별 제조법과 물성 — 콜로이달/퓸드 실리카, 세리아 소성/습식

> 에이전트: slurry-abrasive Lv1-1 | 작성일: 2026-09-10
> [[slurry-components-overview]] [[colloid-zeta-dlvo-slurry-stability]]
> [[abrasive-d99-composite-particle-versum2019]] [[lpc-scratch-density-tail-correlation]]

## 1. 왜 필요한가
CURRICULUM.md Lv1-1은 "입자 종류별 제조법과 물성(콜로이달/퓸드 실리카, 세리아 소성/습식)"이다.
지금까지 Lv1-2·Lv2-1에서는 D50/D99·LPC 같은 **분포 수치**를 다뤘지만, 그 분포가 왜 제조법마다
다른 모양(narrow vs long-tail)이 되는지는 다루지 않았다. 이 노트는 제조 공정 자체(이온교환·
화염가수분해·소성·습식침전)가 입자 형상·분포·연마 성능에 미치는 방향성을 1차 문헌으로 확립한다.

## 2. 콜로이달 실리카 — 이온교환법(ion exchange)
**US 8,211,193 B2** (Fujifilm Planar Solutions, LLC — 원 출원 Applied Materials/Advanced
Technology Materials 계열, 등록일 2012-07-03), "Ultrapure colloidal silica for use in chemical
mechanical polishing applications". 원문 청구항·명세서 서술(웹 조회로 확보, PDF 미다운로드 —
freepatentsonline.com/8211193.html 원문 그대로):
1. 퓸드 실리카 또는 규산염을 알칼리금속수산화물 수용액에 용해 ("dissolving a fumed silica in
   an aqueous solvent containing an alkali metal hydroxide")
2. 이온교환으로 알칼리금속 대부분 제거 ("removing majority of the alkali metal via ion exchange")
3. 온도·농도·pH를 핵생성·입자성장이 시작되는 값으로 조정
4. 냉각하여 콜로이달 실리카 분산액 완성

실측 규격: **1차 입자 약 2~100 nm, 평균 입자크기(MPS) 약 10~200 nm**, Na 불순물 **1 ppm 미만**
(반도체급 요구 — Na 오염은 후공정 소자 결함 원인). 전통적으로는 천연 규사를 1200°C 미만에서
탄산나트륨과 융융해 물유리(water glass, Na2SiO3)를 만든 뒤 물에 녹이고 이온교환하는 경로가
가장 흔하다(Kim 2018, IntechOpen 리뷰 챕터, DOI: 10.5772/intechopen.75408, §"Silica abrasive").

## 3. 퓸드 실리카 — 화염가수분해(flame hydrolysis)
Kim 2018(상동)이 정리한 반응: 클로로실란(SiCl4)을 수소-산소 화염 중에서 기상 가수분해한다.
`SiCl4 + 2H2 + O2 → SiO2 + 4HCl` — 콜로이달 실리카의 액상(수계) 합성과 달리 **기상 고온
공정**이라는 점이 핵심 차이다. 이 차이가 형상을 가른다: Kim 2018은 콜로이달 실리카를
"spherical shape"로, 퓸드 실리카는 1차입자가 응집(aggregate)해 300 Å(=30 nm)보다 큰 이차구조를
이룬다고 서술한다("larger than 300 Å"). 같은 챕터는 정성적으로 "Colloidal silica abrasive
slurry has much lower removal rate than fumed silica abrasive"이면서 "it gives much lower
scratch defect performance by its spherical shape and small size"라고 대비한다 — 즉 **퓸드=
빠르지만 결함 많음, 콜로이달=느리지만 결함 적음**이라는 트레이드오프. 단 이 서술은 리뷰
챕터(가중치 0.6)의 정성적 요약이고, 두 슬러리를 같은 조건에서 비교한 정량 표는 이 챕터에
없다 — **미검증**: 제거율·결함 차이의 정량 배수(몇 배인지).

## 4. 세리아 — 소성(calcined) vs 습식(wet) 제조
Kim 2018 Table 1(서술 인용, 원표 접근 불가로 문장 형태로 재구성): 소성 세리아는 "raw ceria
material is oxidized followed by mechanical crushing to make them small particles"로 만들며
형상은 **facet shape(각진 면)·poor size distribution(분포 나쁨)**. 습식(콜로이달) 세리아는
"precipitation procedure in liquid state. Seed ceria nuclei in an aqueous cerium solution grows"로
만들며 형상은 **spherical shape·uniform size distribution**. 즉 top-down(분쇄, 각진 파편) vs
bottom-up(핵생성-성장, 구형)이라는 제조 경로 차이가 형상·분포 차이로 직결된다는 것이 두 개
독립 문헌([[abrasive-d99-composite-particle-versum2019]] Lv2-1 노트가 이미 확인한 LPC
13.28배 차이의 제조공정 가설, Kim 2018의 정성 서술)에서 방향이 일치한다.

**Cabot Microelectronics 특허 US 2015/0104939 A1**("Wet-Process Ceria Compositions for
Polishing Substrates, and Methods Related Thereto", 공개일 2015-04-16)도 같은 구분을 명문화:
"wet-process ceria refers to a ceria prepared by a precipitation, condensation-polymerization,
or similar process (as opposed to, for example, fumed or pyrogenic ceria)"이고 "wet-process
techniques can result in smaller particles by controlling the particle growth ... in contrast to
dry process techniques where a calcining process is typically used." 이 특허의 실시예는
**1차 입자 약 12 nm 이하, 2차 입자(응집체) 약 30 nm 이하**를 목표로 하나, 원문에 D50/D99
백분위수나 결정자 크기·경도 수치는 없다(자유특허조회 HTML 렌더 확인 — **미검증**: 결정자
크기·경도 정량값).

## 5. 습식 세리아 정량 사례 — Son et al. 2021 (초미세 세륨수산화물)
**Son, Y.-H. et al., "Super fine cerium hydroxide abrasives for SiO2 film chemical mechanical
planarization performing scratch free", Scientific Reports 11, 17736 (2021),
doi: 10.1038/s41598-021-97122-9** (PMC8421349, CC-BY, 전문 PDF 확보·fitz 텍스트 추출 대조).
이 논문은 §2·§4의 "습식 세리아" 계열 중에서도 초미세(super-fine) 변종을 다룬다.

### 5.1 합성 조건(Methods, 원문 그대로)
"0.052 mol of (NH4)2Ce(NO3)6"를 Ce4+ 전구체로, "0.170 mol of C3H4N2"(이미다졸)을 Ce4+ 용해도를
높이는 촉매로 DI수에 녹이고, NaOH로 pH를 적정해 종료(termination)한다 — **온도 25°C**로,
기존 습식세리아 합성(Ce4+와 Ce3+ 혼합, 60~80°C)보다 낮은 저온 공정. 촉매/전구체 몰비는
0.170/0.052 ≈ 3.27배(§7 verify 블록에서 재계산).

### 5.2 입자 크기·결정성
1차 입자(Ce(OH)4)는 "the average and standard deviation of their size were 2.06 and 0.15 nm"
— f.c.c. 다결정. 슬러리 내 2차입자(secondary abrasive, 실제 연마에 관여하는 응집 단위)는
합성 종료 pH·슬러리 pH에 따라 130~258 nm 범위로 변한다(§5.3).

### 5.3 2차입자 크기 ↔ 연마율의 역상관 (CMP 슬러리 pH 스윕, Fig.5 그대로)
슬러리 pH를 5.0→6.0으로 올리면 2차입자 크기는 **223 nm → 130 nm로 감소**하는 동시에
SiO2막 연마율은 **263 nm/min → 524 nm/min로 증가**한다(피크). pH를 6.0→6.25로 더 올리면
2차입자 크기는 **130 nm → 153 nm로 재증가**하고 연마율은 **524 nm/min → 437 nm/min로 감소**
— 두 구간 모두 "2차입자가 작을수록 연마율이 높다"는 역상관이 방향 일치로 재현된다(저자는
이를 유효 접촉면적 논거로 설명: 동일 고형분 0.3 wt%에서 2차입자가 작을수록 개수가 많아
총 접촉면적이 커진다). 이 초미세 습식세리아 슬러리(2차입자 ~130 nm)의 최대 연마율(524 nm/min)은
같은 논문이 인용한 통상적 facet-표면 습식세리아(1차입자 ~3 nm, 스크래치 억제를 위해 극소화한
비교군)의 연마율(~10 nm/min)보다 **약 50배 높다** — 저자 서술: "~ 50 times higher than that
(~ 10 nm/min) of the facet surface (~ 3 nm in size) wet ceria abrasive." 이 비교군은 스크래치를
줄이려고 크기를 극한까지 줄인 결과 연마율까지 희생된 사례이며, 초미세 Ce(OH)4는 비정질에
가까운 낮은 결정성·구형에 가까운 형상 덕분에 이 트레이드오프를 우회했다는 것이 저자의 핵심
주장(스크래치 없이 고연마율)이다.

## 6. 형상·경도와 정확도 갭(Δ 손상)의 연결
accuracy_gaps.py 1순위 갭(Δ 손상 유발도 미모델링, abrasive_d99_nm·scratch_threshold_nm 관련)에
비추어 보면, 이번 조사가 보탠 것은 **"D99·LPC 같은 분포 꼬리 수치 자체가 제조법에서 갈린다"**는
상류 인과 한 단계다: 소성(top-down 분쇄, facet)·퓸드(화염 응집)는 넓은 분포·각진 형상 →
[[lpc-scratch-density-tail-correlation]]가 다룬 스크래치-LPC 상관의 "입력"에 해당하고, 콜로이달·
저온습식(bottom-up, 구형)은 좁은 분포 → 스크래치 위험이 낮다는 방향이 이번 문헌들(정성, Kim
2018)과 정량 사례(Son 2021, 2차입자 크기 역상관)에서 함께 확인된다. 다만 **경도(HV/Mohs) 자체의
1차 문헌 수치는 이번 조사에서 확보하지 못했다** — Kim 2018 챕터는 알루미나>>텅스텐/구리라는
상대 서열만 서술하고 절대 경도값(GPa)은 제시하지 않는다. **미검증**: 실리카/세리아/알루미나
절대 경도값 — 압입 파괴인성과 함께 Lv2-1 잔여 과제(Hertz 압입)로 이월한다.

## 7. 정량 재현 (verify)

```python verify
# Son et al. 2021, Sci. Rep. 11, 17736, doi:10.1038/s41598-021-97122-9
# Fig.5 (CMP 슬러리 pH 스윕) 원문 수치 그대로

slurry_ph = [5.0, 6.0, 6.25]
secondary_size_nm = {5.0: 223, 6.0: 130, 6.25: 153}
polish_rate_nm_min = {5.0: 263, 6.0: 524, 6.25: 437}

# 1) pH 5.0->6.0: 2차입자 크기 감소 & 연마율 증가 (역상관, 저자 핵심 주장)
assert secondary_size_nm[6.0] < secondary_size_nm[5.0], "5.0->6.0 구간 2차입자 크기가 감소해야 한다"
assert polish_rate_nm_min[6.0] > polish_rate_nm_min[5.0], "5.0->6.0 구간 연마율이 증가해야 한다"

# 2) pH 6.0->6.25: 2차입자 크기 재증가 & 연마율 감소 (역상관, 피크 지난 구간)
assert secondary_size_nm[6.25] > secondary_size_nm[6.0], "6.0->6.25 구간 2차입자 크기가 재증가해야 한다"
assert polish_rate_nm_min[6.25] < polish_rate_nm_min[6.0], "6.0->6.25 구간 연마율이 감소해야 한다"

# 3) 최대 연마율은 pH 6.0에서 관찰(초미세 세리아 슬러리 피크)
peak_ph = max(polish_rate_nm_min, key=polish_rate_nm_min.get)
assert peak_ph == 6.0, "논문 Fig.5c 피크는 슬러리 pH 6.0에서 관찰됨"
print(f"피크 연마율 {polish_rate_nm_min[peak_ph]} nm/min @ pH {peak_ph}")

# 4) 초미세 습식세리아(2차입자~130nm) vs facet 습식세리아(1차입자~3nm, 연마율~10nm/min) 배수
facet_ceria_rate = 10  # nm/min, 저자가 비교군으로 인용한 값
ratio = polish_rate_nm_min[6.0] / facet_ceria_rate
assert 45 <= ratio <= 55, f"저자 서술 '~50배'와 대조 — 재계산 {ratio:.1f}배가 45~55 범위를 벗어남"
print(f"초미세 vs facet 습식세리아 연마율 비 = {ratio:.1f}배 (문헌값 ~50배와 대조)")

# 5) 합성 촉매/전구체 몰비 재계산 (Methods 원문 0.170 mol / 0.052 mol)
catalyst_mol = 0.170
precursor_mol = 0.052
molar_ratio = catalyst_mol / precursor_mol
assert 3.0 <= molar_ratio <= 3.5, f"원문 몰수 재계산 결과 {molar_ratio:.2f}가 예상 범위(3.0~3.5) 밖"
print(f"촉매/전구체 몰비 = {molar_ratio:.2f} (원문 0.170 mol / 0.052 mol)")
```

### 7.1 재현 결과 요약
위 verify 블록 실행 결과: pH 5.0→6.0 구간에서 2차입자 223→130 nm(감소)·연마율 263→524 nm/min
(증가)이 문헌값과 정확히 일치(원문 표 그대로 가져온 값이므로 표 내적 일관성 확인), pH
6.0→6.25 구간도 130→153 nm(증가)·524→437 nm/min(감소)로 역상관 방향이 재확인됐다. 초미세
세리아(524 nm/min)와 facet 세리아(10 nm/min) 배수는 재계산 52.4배로 저자 서술 "~50배"와
대조해 45~55배 범위 안에 들어 일치, 촉매/전구체 몰비 3.27배도 원문 몰수 그대로 재계산해
3.0~3.5 범위 안에서 일치했다.

## 8. 한계·후속 (정직한 미검증 표기)
- ⚠ **미검증**: 실리카·세리아·알루미나의 절대 경도(GPa/HV)와 압입 파괴인성 — 이번 조사(Kim
  2018 리뷰, Son 2021, Cabot 특허)에는 상대 서열 서술만 있고 1차 수치가 없다. Hertz 압입
  단원(Lv2-1 잔여)에서 별도 문헌 탐색 필요.
- ⚠ **미검증**: 퓸드 vs 콜로이달 실리카의 제거율·결함 차이 정량 배수 — Kim 2018은 방향만
  서술("much lower removal rate", "much lower scratch defect")하고 배수를 제시하지 않는다.
- ⚠ **미검증**: US 2015/0104939 A1의 소성 세리아 결정자 크기·경도 실시예 수치(원문에 D50/D99
  백분위수·경도값 자체가 없어 확보 불가 — 자유특허조회 렌더 재확인 완료).
- Son 2021의 "2차입자 크기 ↔ 연마율 역상관"은 **같은 화학종(초미세 Ce(OH)4) 내부의 pH 스윕**
  결과이며, 이를 콜로이달실리카/퓸드실리카/소성세리아 간 **교차 화학종 비교**로 일반화하지
  않는다(오귀속 방지 — [[abrasive-d99-composite-particle-versum2019]] §3와 같은 원칙).
- 스코프 준수: `tools/scope.py --agent slurry-abrasive --check` 기준 1차논문(weight 1.0)·
  특허(weight 1.0)·리뷰(weight 0.6) 혼합, focus(입자 자체 물성) 내 — 제형(첨가제 비율)은
  다루지 않음. 고용주의 사내 데이터·관행 없음.

## 9. 다음 단원
Lv2-1 잔여(입자 경도·형상과 Hertz 압입, 입자당 제거 체적)로 이어간다 — 이번 노트가 확보하지
못한 절대 경도값이 그 단원의 선행 과제.
