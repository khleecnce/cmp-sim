<!-- V2-SECTION: R2-slurry | 공동: R3-pad | 분배완료 2026-09-08 | 근거: additive, chemistry, slurry | 정본: ARCHITECTURE-V2.md §3 -->
# 최신 패드 소재 리뷰 — 3D 프린팅 패드·무발포(솔리드) 패드·저결함 패드 소재 (Lv3-1)

> pad-material Lv3-1 | 작성일: 2026-09-08
> 선행: [[pad-porosity-slurry-transport-mrr]](%P·기공 크기 vs MRR — 기존 발포 패드의 한계),
> [[pad-viscoelasticity-temp-frequency-dma]](E'(T)·Khanna 2019 — 3D 프린팅 패드의 E'30/E'90 설계축),
> [[pu-pad-chemistry-prepolymer-foam]](발포 공정이 기공 산포를 만드는 이유), [[hertz-gw-contact-mechanics]](A_r∝1/E*),
> [[disk-design-pad-roughness-asperity-relation]](Yang 2010 솔리드 패드 논문이 이월된 자리),
> [[gw-nominal-vs-local-pressure]](접촉면적↑ → 국소압력↓ → 스크래치↓ 경로).
> 이 노트의 질문: 발포 PU 패드의 '기공 산포·경도-결함 트레이드오프'를 깨려는 세 가지 소재 접근
> — (a) 적층제조(3D 프린팅)로 기공·소재를 위치 제어, (b) 기공을 없애고 레이저 마이크로홀로 대체,
> (c) 소프트(저모듈러스)·균일 asperity로 저결함 — 이 각각 1차 데이터로 무엇을 얼마나 보였는가.

## 1. 왜 별도 단원인가 — 발포 패드의 구조적 한계

Lv2-2([[pad-porosity-slurry-transport-mrr]])에서 확인한 두 사실이 출발점이다. (1) %P를 30%p 올려도
MRR은 8%만 오른다(Prasad 2013) — 기공률은 강한 조절 손잡이가 아니다. (2) 기공 크기 → 결함 부호가
재료계마다 뒤바뀐다(Prasad vs Yim). 두 결과의 공통 원인은 **발포(중공 미소구·가스 프로싱)로 만든
기공은 크기·위치·연결성이 통계적으로만 제어된다**는 점이다([[pu-pad-chemistry-prepolymer-foam]]).
그래서 2010년대 이후 패드 개발은 "기공 산포 자체를 없애거나(무발포), 기공 위치를 결정론적으로
놓는(3D 프린팅)" 쪽으로 갔다. 이 단원은 그 두 흐름과, 그 위에 얹힌 "하드 패드 평탄화 + 소프트 패드
저결함"을 동시에 노리는 소재 설계를 1차 논문·특허로 정리한다.

## 2. 1차 출처 (papers/에 확보, INDEX.json 등록; scope.py --check 전부 허용)

1. **Kenchappa, Popuri, Chockkalingam, Jawali, Jayanath, Redfield, Bajaj (2021)**, "Soft Chemical
   Mechanical Polishing Pad for Oxide CMP Applications", *ECS J. Solid State Sci. Technol.* 10, 014008.
   DOI: 10.1149/2162-8777/abdc40. Clarkson Univ.·Applied Materials. OA(CC BY-NC-ND) — Semantic Scholar
   PDF 미러에서 11쪽 전문 확보(papers/kenchappa2021-soft-pad-oxide-cmp-jss.pdf), 본문 전체 확인.
   *3D 프린팅 패드*: 본문은 "novel method of pad manufacturing … precise material placement and
   consistent pore construction"이라고만 쓰고 참고문헌 34–36·39(Bajaj·Ganapathiappan 등, "Polishing
   pads produced by an additive manufacturing process" 계열 AMAT 특허)를 달았다. 즉 실험 패드가
   적층제조품이라는 것은 **참고문헌 연결로 확인**, 본문 명시는 아님(저자가 proprietary로 세부 비공개).
2. **Yang, Choi, Hwang, Lee, Kim (2010)**, "Effects of diamond size of CMP conditioner on wafer removal
   rates and defects for solid (non-porous) CMP pad with micro-holes", *Int. J. Mach. Tools Manuf.* 50,
   860–868. DOI: 10.1016/j.ijmachtools.2010.06.007. 성균관대·삼성전자 메모리·Saint-Gobain. Elsevier
   유료 → 미러 사이트(미러 사이트 경유 미러 사이트) 9쪽 전문 확보(papers/yang2010-ijmt-solid-pad-
   microholes-conditioner.pdf). [[disk-design-pad-roughness-asperity-relation]] §6에서 "Lv3-1 이월"로
   남겨둔 바로 그 논문이다. 삼성 양산 라인 데이터이지만 **공개 논문**이므로 사용(회사 데이터 아님).
3. **Khanna et al. (2019)**, "Impact of Pad Material Properties on CMP Performance for Sub-10nm
   Technologies", *ECS JSS* 8(5), P3063. DOI: 10.1149/2.0121905jss. Applied Materials 3D 프린팅 패드의
   E'25/E'90 설계 논문 — 수치는 [[pad-viscoelasticity-temp-frequency-dma]] §4·verify(3)에 이미
   재현되어 있어 여기서는 인용만 한다(중복 재현 안 함).
4. **US 10,875,145 B2** (Applied Materials, "Polishing pads produced by an additive manufacturing
   process", 우선일 2014-10-17, 등록 2020-12-29). freepatentsonline 전문 열람(요지·수치 발췌).
5. **WO 2015/120430 A1** (Harvard College, "3D-printed polishing pad for chemical-mechanical
   planarization (CMP)", 출원 2015-02-10, 우선일 2014-02-10). freepatentsonline 전문 열람. 압출
   필라멘트 직교 적층 마이크로래티스(direct ink writing 계열) — 발명자 명단은 열람 페이지에 미표시.
6. **Morsada, Gunasekaran, Visaveliya, Shipp (2025)**, "Innovations in Polyurethane Pads Used in CMP:
   A Perspective and Future Directions", *ECS JSS* 14, 054009. DOI: 10.1149/2162-8777/add808.
   Clarkson Univ. 리뷰. **초록만 확인**(Unpaywall closed, IOP 봇차단, 미러 사이트 3미러 모두 "없음").
   리뷰 본문 수치는 이 노트에 하나도 넣지 않았다.

(허용 소스 6건 상한 준수: 1차 논문 3, 특허 2, 리뷰 1. 그 밖에 ICPT 2015 "Planarization improvement
using non-porous polishing pad in ILD CMP"(IEEE 7411988)는 Crossref에 DOI가 없어 인용에서 제외.)

## 3. 무발포(솔리드) 패드 — Yang 2010, 200 mm TEOS STI 양산 라인

### 3.1 소재 스펙 (Yang 2010 §2 Pad; fitz 추출에서 ± 기호가 숫자로 깨져 원문 대조 후 복원)

| 항목 | 다공성 IC-1010 (Dow) | 솔리드 SURE2000 (SKC) |
|---|---|---|
| 기공 | 20–60 vol%, 30–80 µm | 없음. 레이저 마이크로홀 φ165 µm, 깊이 520 µm, 홀 간격 80 µm |
| 그루브 | 있음 | 폭 210 µm, 깊이 600 µm (레이저) |
| 경도(Shore D) | 57 ± 5 | 67 ± 2 |
| 영률 | 87 ± 10 MPa | 90 ± 15 MPa |
| 밀도 | 0.72 ± 0.2 g/cm³ | 1.145 ± 0.1 g/cm³ (기공 없음) |
| 패드 컷레이트(같은 컨디셔너, 4.5 lbf, 1 h) | 4 µm/h | 1.9 µm/h |

핵심 관찰: **벌크 영률은 두 패드가 거의 같다(87 vs 90 MPa)**. 즉 솔리드 패드의 차이는 매트릭스
강성이 아니라 "기공이 없어서 접촉면적 배분이 다르다"는 데서 온다. 밀도비로 IC-1010의 %P를 역산하면
≈37%(§7 verify (1); 매트릭스 밀도를 솔리드 패드 밀도로 가정한 추정치이며 원문은 "20–60%"만 제시).

### 3.2 폴리싱 결과 (Yang 2010 §3.1, Fig. 4–7, 180 µm 다이아몬드 컨디셔너 동일)

- 블랭킷 TEOS RR: 솔리드 2951 Å/min vs 다공성 3656 Å/min → 솔리드가 약 20% 낮음. 양산 STI 패턴 웨이퍼
  1개월 모니터링에서는 약 10% 낮음(로트별 총제거량/총폴리시시간).
- 접촉면적비(3 psi, 유리판 광학측정, ImageJ): 다공성 0.7% vs 솔리드 **7.5%** — 10배 이상.
  저자 해석: 접촉면적↑ → 입자 1개당 하중↓ → Luo-Dornfeld 방향으로 RR↓(§3.1, 1차 논문 서술).
  [[gw-nominal-vs-local-pressure]]의 "P 고정 시 n·A_r이 변한다"와 같은 축.
- 스크래치: 솔리드 패드가 뚜렷이 낮음(Fig. 6, 1개월 로트 평균). 기전 두 가지(저자 가설, 미검증):
  (i) 접촉면적↑ → 국소 피크압력↓ → 갇힌 입자의 압입 깊이↓, (ii) 마이크로홀이 응집 실리카(EDX로
  확인, Fig. 7)를 가둬 재스크래치 방지.
- 결론적 트레이드오프: "결함은 좋으나 RR −10%는 양산에서 수용 불가" → 저자는 **패드가 아니라
  컨디셔너 다이아몬드 크기**를 바꿔 해결했다(§3.3). 이것이 무발포 패드의 실무적 핵심이다: 기공이
  없으면 asperity 텍스처는 오로지 컨디셔닝으로만 만들어지므로 컨디셔너가 곧 "기공 설계 변수"가 된다.

### 3.3 컨디셔너 다이아몬드 크기로 솔리드 패드 RR 회복 (Yang 2010 §3.2, Fig. 8–13)

| 다이아몬드 | RR (Å/min) | 접촉면적 | Ra (µm) | 스크래치/로트 | 양산 폴리시 시간 |
|---|---|---|---|---|---|
| 180 µm (Supplier-A) | 2973 | 7.5% | 2.31 | 5.36 | 127 s |
| 70 µm (SGA-A) | 3587 | 5.2% | 1.34 | 1.69 | 116 s |

- 70 µm로 줄이면 RR +20%(2973→3587), 접촉면적 7.5→5.2%, Ra 2.31→1.34 µm, 스크래치 −68%,
  양산 폴리시 시간 −9%(≈"약 10%") — **RR 손실을 회복하면서 결함은 더 줄었다**.
- 저자의 정량 설명: Luo-Dornfeld 포화영역(12 wt% 퓸드 실리카, 7 wt% 이상에서 RR 불변 확인)에서
  RR ∝ (활성입자 접촉면적)^(1/2) [Yang Eq. (1)]. (7.5/5.2)^0.5 = 1.201 ↔ RR비 3587/2973 = 1.207.
  원문은 이 값을 "1.206"이라 적었는데 §7 verify (2)에서 보듯 **1.206은 RR비이고 면적비 제곱근은
  1.201**이다 — 두 값이 0.5% 안에서 맞으므로 결론은 유지되지만 원문 숫자 라벨은 뒤바뀌어 있다.
- 원문 초록의 "increased from 2973 to 2587 Å/min"은 본문·결론(3587)과 어긋나는 **초록 오타**다.
  §7 verify (2)에 assert로 기록.
- 마이크로홀 가장자리: 180 µm는 버(burr)로 홀이 덮여 잔류물 포집 실패, 70 µm는 홀 가장자리가
  깨끗(Fig. 14, SEM). 접촉각 105°→63°(180 µm, 30 h)로 글레이징 진행 vs 70 µm는 안정(Fig. 16).
  디싱도 70 µm가 개선(Fig. 17, 수치 미기재 → 미검증).
- Ra↓ → RR↑라는 부호는 [[disk-design-pad-roughness-asperity-relation]]의 "거칠수록 RR↑" 통념과
  반대다. 차이는 솔리드 패드에서 180 µm 다이아몬드가 만드는 "크고 불규칙한 asperity"가 접촉면적을
  과잉 키우는 데 있다 — 다공성 패드 결과를 솔리드 패드에 외삽하면 부호를 틀린다.

## 4. 3D 프린팅(적층제조) 패드 — 특허가 말하는 설계 자유도

### 4.1 Applied Materials US 10,875,145 (2014 우선)

- 청구 요지: 2종 이상 소재(관능성 폴리머·올리고머·반응성 희석제·경화제)를 **순차 적층·경화**해
  층별로 조성을 달리한 패드. 제1 폴리머의 **E'30/E'90 > 약 6**(DMA 1 Hz, 5 °C/min), KEL은 40 °C·
  1 또는 1.6 Hz 측정 — 즉 "온도에 따른 E' 하락비"를 설계 파라미터로 명시했다. 이것이 Khanna 2019에서
  E'25/E'90 = 188 / 21 / 4 세 패드로 MRR 드리프트를 실측한 배경이다([[pad-viscoelasticity-temp-
  frequency-dma]] §4). 절대 E' 값·기공 크기·경도·RR 수치는 특허 본문에 없음(열람 확인).
- 소재 관점 함의: 발포 없이 광경화 수지의 조성으로 강성을 잡으므로, "%P를 올리면 E'가 같이 떨어지는"
  Lv2-2의 상쇄 구조(Gibson-Ashby 결합)를 **기공과 강성의 분리**로 풀 수 있다. 다만 이는 특허의 설계
  주장이며, 분리 효과의 정량 실증은 Kenchappa 2021(§5)의 "동일 밀도·기공에서 경도만 60D→40D"가 유일.

### 4.2 Harvard WO 2015/120430 (2014 우선) — 필라멘트 마이크로래티스

- 압출 필라멘트(직경 50–500 µm, 예시 225 µm)를 층마다 직교로 쌓은 마이크로래티스, 필라멘트 중심
  간격 10–2000 µm(예시 400 µm), 층 수 2–50(예시 6층), **공극 20–80 vol%**, 매트릭스는 에폭시·PU·
  폴리에스터·폴리이미드·PDMS, 필러 ≤200 nm(≤100 nm). 잉크의 저장 탄성률 G' ≥ 10⁴~10⁵ Pa, 항복응력
  ≥100 Pa(프린팅 가능 조건).
- 예시 기하로 층내 공극률을 계산하면 1 − 225/400 = 43.75%로 청구 범위 20–80% 안(§7 verify (3)).
  이 계산은 필라멘트를 직사각 단면으로 근사한 상한이며 원형 단면·층간 겹침을 넣으면 달라진다(추정).
- 특허가 내세우는 이점은 컨디셔닝이 아니라 **두께 전체를 관통하는 상호연결 유로**로 슬러리 흐름을
  사전 설계한다는 것 — Lv2-2의 "기공=슬러리 저장소" 가설을 결정론적 채널로 대체한 형태. 폴리싱
  실측 데이터는 열람 범위에 없음(미검증).

## 5. 저결함 소프트 패드의 실증 — Kenchappa 2021 (AMAT 적층제조 패드, 세리아 STI)

### 5.1 패드 스펙 (Kenchappa Table I·II)

| 패드 | 그루브 | 밀도 (g/cc) | 기공률/크기 | Shore D | 컨디셔너 | 패드 마모율 (mil/h) |
|---|---|---|---|---|---|---|
| 상용 (DuPont k-groove, 하드) | 동심 | 0.95 | 낮음/작음 | 58–60 | 다이아몬드(3M) | 10–15 |
| Pad-1 (하드, 실험) | 동심 | 0.9 | 낮음/작음 | 60 | CVD 디스크 | 3 |
| Pad-2 (소프트, 실험) | 나선 | 0.9 | 낮음/작음 | 40 | CVD 디스크 | 5–6 |

밀도·기공률·기공 크기는 세 패드가 "comparable", 명목 접촉면적 >50%(원문). **Pad-1과 Pad-2는 제법이
같고 소재 조성만 다르다** — 경도 60D vs 40D를 기공 변수와 독립으로 바꾼 유일한 공개 대조 실험.
(조건: POLI-500, 2.5/3.5 psi, 87/93 rpm, 슬러리 ~100 mL/min, 60 s, AGC 세리아, 200 mm HDP 산화막.)

### 5.2 결과 (Kenchappa Fig. 4–12)

- 블랭킷 산화막 RR: 상용 ~1700, Pad-1 ~1200, **Pad-2 ~3250 Å/min** — 소프트 패드가 하드 상용 패드의
  1.9배(원문 "twice", §7 verify (4)). 하드 실험 패드 Pad-1은 상용의 0.71배.
- 패드 온도 상승: 상용 ~18 °C > Pad-1·Pad-2(수치 미기재). CoF는 RR과 같은 순서로 증가.
- STI 패턴(0.5 µm 트렌치, 단차 ~700 nm): 액티브 산화막 완전 제거까지 상용 ~180 s vs Pad-2 ~105 s.
  엔드포인트 후 트렌치 산화막 손실 Pad-2 0–~250 Å vs 상용 ~750 Å(10% PD)·~500 Å(40% PD). 500 µm
  피처 디싱은 Pad-2와 상용이 동등(소프트 패드의 대피처 한계는 남음).
- asperity 높이 분포 폭(3D 컨포칼, Fig. 11b): Pad-1 ~130 µm, 상용 ~30 µm, **Pad-2 ~8 µm**. 저자는
  좁은 분포 → 균일 압력분포 → 높은 평탄화효율로 설명. [[disk-design-pad-roughness-asperity-relation]]
  §5의 GW 산포 σ와 같은 양이며, σ가 4~16배 작다는 것은 접촉 개수 n이 훨씬 균일하다는 뜻.
- 결함: 제목이 "low-defect"를 함의하지만 **결함 카운트 데이터는 이 논문에 없다**. 소프트 패드가 결함이
  낮다는 근거는 서론의 2차 인용(Yeh et al., "softer pads reduce scratches")뿐 — 이 노트에서는
  "소프트=저결함"을 Kenchappa의 실측으로 쓰지 않는다(미검증). 실측 결함 데이터가 있는 것은 §3의
  Yang 2010(솔리드 패드)뿐이다.

### 5.3 왜 소프트 패드가 RR도 높은가 — 접촉역학으로 읽기

GW(지수분포)에서 A_r/W ∝ 1/E*([[hertz-gw-contact-mechanics]] §4)이므로 40D 소재는 60D보다 실접촉면적이
크다. 세리아 STI는 Ce–O–Si 결합 형성이 율속이라(Kenchappa 서술) 접촉면적↑가 곧 RR↑로 연결된다.
반면 Yang 2010의 퓸드 실리카 TEOS에서는 접촉면적↑가 RR↓였다(§3.2). **같은 "접촉면적 증가"가 슬러리
화학에 따라 RR 부호를 바꾼다** — Lv2-2에서 "기공 크기→결함 부호가 재료계 의존"이라 남긴 것과 동일한
교훈이고, sim/에 소재 경도→MRR을 단일 부호로 넣으면 안 되는 두 번째 근거다.

## 6. 종합 — 세 접근의 위치와 sim/에의 함의

| 접근 | 1차 근거 | 무엇을 분리했나 | 실측 이득 | 남은 트레이드오프 |
|---|---|---|---|---|
| 무발포+마이크로홀 | Yang 2010 | 기공 산포 제거, 잔류물 포집 | 스크래치↓, 컷레이트 절반 | RR −10~20% → 컨디셔너로 회복 |
| 적층제조(광경화) | US10875145, Khanna 2019, Kenchappa 2021 | 기공·강성·E'(T) 독립 제어 | RR 1.9배, PE↑, 마모율 1/2~1/4 | 결함 실측 미공개, 대피처 디싱 동등 |
| 필라멘트 래티스 | WO2015120430 | 관통 유로 설계 | (실측 없음) | 폴리싱 데이터 부재 |

1. 소재 경도(E*)→MRR 부호는 슬러리 화학에 종속(세리아 +, 실리카 −). 단일 부호 금지.
2. 무발포 패드에서는 컨디셔너 다이아몬드 크기가 접촉면적(5.2~7.5%)을 직접 정하고 RR ∝ A^(1/2)
   관계(Yang Eq. 1)가 0.5% 안에서 맞는다 — [[disk-design-pad-roughness-asperity-relation]]의 다공성
   패드 결과와 부호가 반대이므로 패드 유형 플래그가 필요하다.
3. 적층제조 패드의 asperity 높이 산포(~8 µm)는 상용 발포 패드(~30 µm)의 1/4 — GW σ 입력을 패드
   유형별로 달리 잡아야 한다. 절대 σ 환산(높이 분포 폭≠σ)은 미검증.
4. 고용주의 사내 데이터 없음. Yang(삼성 양산), Kenchappa(AMAT), 특허(AMAT·Harvard) 전부 공개 자료.

## 7. 정량 재현 (python verify)

```python verify
# (1) Yang 2010 (doi:10.1016/j.ijmachtools.2010.06.007) 밀도로 IC-1010 %P 역산 — Lv2-2 %P 정의 재사용
def pct_porosity(rho_f, rho_s):
    return (1 - rho_f / rho_s) * 100
rho_porous, rho_solid = 0.72, 1.145   # g/cm3, Yang §2 (±0.2, ±0.1)
pP = pct_porosity(rho_porous, rho_solid)
assert 20 <= pP <= 60, pP              # 원문 "approximately 20–60% porosity" 범위 안
print(f"(1) IC-1010 %P 역산 = {pP:.1f}% (원문 범위 20–60% 안; 매트릭스밀도=솔리드패드 가정)")

# (2) Yang 2010 Eq.(1): 포화영역 RR ∝ (접촉면적)^0.5 — 70 vs 180 um 다이아몬드
A70, A180 = 5.2, 7.5                   # % 접촉면적
RR70, RR180 = 3587, 2973               # Å/min
ratio_area_sqrt = (A180 / A70) ** 0.5
ratio_rr = RR70 / RR180
assert abs(ratio_area_sqrt - ratio_rr) / ratio_rr < 0.01, (ratio_area_sqrt, ratio_rr)
# 원문 표기 "1.206"은 면적비 제곱근(1.201)이 아니라 RR비(1.207)에 해당 — 라벨 오류 기록
assert abs(ratio_rr - 1.206) < 0.002 and abs(ratio_area_sqrt - 1.206) > 0.004
# 초록 오타: "2973 to 2587" — 본문·결론은 3587. 2587이면 RR이 감소(-13%)해 본문 "+20%"와 모순
assert 2587 / 2973 < 1 and abs(RR70 / RR180 - 1.20) < 0.01
# 블랭킷 솔리드 vs 다공성 -20%, 스크래치 -68%, 폴리시 시간 -9%
assert abs(2951 / 3656 - 0.80) < 0.01
assert abs(1 - 1.69 / 5.36 - 0.68) < 0.01
assert abs(1 - 116 / 127 - 0.087) < 0.005
print(f"(2) Yang: sqrt(A180/A70)={ratio_area_sqrt:.3f} vs RR70/RR180={ratio_rr:.3f} (0.5% 일치); "
      f"솔리드/다공성 블랭킷 {2951/3656:.2f}, 스크래치 -{(1-1.69/5.36)*100:.0f}%, 시간 -{(1-116/127)*100:.1f}%")

# (3) Harvard WO2015120430 예시 기하 → 층내 공극률 (직사각 단면 근사 상한)
d_fil, pitch = 225.0, 400.0            # um
void_in_plane = 1 - d_fil / pitch
assert 0.20 <= void_in_plane <= 0.80   # 청구 범위 20–80 vol%
print(f"(3) 래티스 층내 공극률 = {void_in_plane*100:.2f}% (청구 20–80% 안)")

# (4) Kenchappa 2021 (doi:10.1149/2162-8777/abdc40) RR 비 — 원문 "twice"
RR_comm, RR_p1, RR_p2 = 1700, 1200, 3250   # Å/min
assert 1.8 <= RR_p2 / RR_comm <= 2.0 and abs(RR_p1 / RR_comm - 0.71) < 0.01
# 패드 마모율: 실험 패드 3, 5–6 mil/h < 상용 10–15 mil/h
assert max(3, 6) < 10
# asperity 높이 분포 폭: Pad-2 8 um이 상용 30 um의 1/4 이하, Pad-1 130 um의 1/16
assert 30 / 8 >= 3.5 and 130 / 8 >= 16
# 엔드포인트 후 트렌치 손실: Pad-2 최대 250 Å < 상용 500·750 Å
assert 250 < 500 < 750
# STI 액티브 클리어 시간: 105 s vs 180 s → 42% 단축
assert abs(1 - 105 / 180 - 0.417) < 0.005
print(f"(4) Kenchappa: Pad-2/상용 RR {RR_p2/RR_comm:.2f}x, Pad-1/상용 {RR_p1/RR_comm:.2f}x, "
      f"클리어 시간 -{(1-105/180)*100:.0f}%, asperity 폭 비 상용/Pad-2 = {30/8:.1f}")
```

## 8. 미검증·미확보 항목 (정직 기록)

- Morsada 2025 리뷰(DOI 10.1149/2162-8777/add808): 초록만. 3D 프린팅·무발포·저결함에 대한 리뷰 본문
  서술은 확보 못함 → 이 노트의 어떤 수치도 리뷰에서 오지 않았다.
- Yang 2010 스크래치·RR 절대값은 삼성 양산 레시피(Table 1: 93/87 rpm, 5.2 psi, 150 mL/min) 기준이며
  결함 검출은 0.5% HF 120 s 확대 후 KLA AIT-II — 다른 장비·검출 조건과 절대 비교 불가. 디싱 개선은
  프로파일 그림만(수치 미기재, 미검증).
- Yang §3.1 기전(접촉면적↑→압입깊이↓, 마이크로홀 포집)은 저자 가설. 접촉면적 7.5%/0.7%는 3 psi
  유리판 측정이며 실제 폴리시 압력·슬러리 존재 하 값이 아니다(추정).
- Kenchappa 2021: 결함 카운트 없음. 패드 소재·제법 비공개(proprietary). "3D 프린팅 패드"임은 참고문헌
  34–36·39의 AMAT 적층제조 특허로 연결한 추정이며 본문에 "additive"라는 단어는 없다.
- US10875145: E'30/E'90 > 6 외 절대 물성·RR·결함 수치 없음. WO2015120430: 폴리싱 실측 없음, 발명자
  명단 미확인(freepatentsonline 열람 페이지 한계).
- 3D 프린팅 패드의 GW σ 절대값, 컨디셔너 종속성(CVD 디스크 필요 여부), 패드 수명 비용은 공개 1차
  데이터를 찾지 못했다(Semantic Scholar API가 429를 반환해 해당 검색 경로는 중단).
- Khanna 2019 E' 비·MRR 드리프트는 [[pad-viscoelasticity-temp-frequency-dma]]에서 이미 재현되어
  이 노트는 재검증하지 않았다.
