<!-- V2-SECTION: R4-disk | 분배완료 2026-09-08 | 근거: break-in, conditioner, sweep, 디스크, 컨디셔너 | 정본: ARCHITECTURE-V2.md §3 -->
# 컨디셔너 디스크 상용 규격·레시피 축 (산업 1차 자료 보강)

> disk-conditioner 보강 노트 (2026-09-06). [[diamond-grit-mesh-bonding]]
> [[conditioner-grit-design-space]] [[conditioner-sweep-kinematics-pcr-profile]]
> [[conditioner-grit-wear-scratch-lifetime]] 상호링크.
>
> 목적: `knowledge/components/conditioner.yaml` 스키마를 세울 때, 기존 Lv1~Lv3 노트가
> 다루지 않은 **상용 디스크의 실제 규격 항목**(캐리어 치수·세그먼트·평탄도·edge exclusion·
> aggressiveness 등급값)과 **레시피 축**(컨디셔닝 duty, 스윕 리비전, break-in)을
> 산업 1차 자료로 확보하는 것. 스키마의 `origin: researched` 근거로 쓰인다.

## 1. 출처 (본 회차 새로 확보)

1. **3M, "3M™ Diamond Pad Conditioner E187", Technical Data, June 2014** (제조사 공개
   기술데이터시트, 자료번호 60-5002-0211-8).
   https://multimedia.3m.com/mws/media/974449O/3m-tm-diamond-pad-conditioner-e187.pdf
   — PDF 직접 파싱해 표 값 인용. 제품 데이터시트이므로 SCOPE의 "업체 기술문서(가중치 0.5)"
   등급. 특정 제품 1점의 값이므로 **일반 범위로 확대 해석 금지**.
2. **C. C. Garretson, S. T. Mear, J. P. Rudd, G. Prabhu, T. Osterheld, D. Flynn (Applied
   Materials) + B. Goers, V. Laraia, R. D. Lorentz, S. A. Swenson, T. W. Thornton (3M),
   "New Pad Conditioning Disk Design Delivers Excellent Process Performance While Increasing
   CMP Productivity", SEMICON West 2000, CMP Technology for ULSI Interconnection, © SEMI 2000.**
   https://multimedia.3m.com/mws/media/153316O/new-pad-conditioning-disk-design-delivers-pdf.pdf
   — PDF 직접 파싱. 학회 프로시딩(피어리뷰 아님), 60종 이상 디스크 설계 DOE + 70,000매
   연마 실측을 담은 1차 데이터.
3. **A. Zhang et al., "Methodology for pad conditioning sweep optimization for advanced
   nodes", Microelectronic Engineering (2019), DOI: 10.1016/j.mee.2019.111101.**
   유료. `tools/find_open_access.py`로 DOI만 확인, 전문은 미확보 — 본 노트는
   academia.edu 게재본에서 확보한 발췌 문단만 인용하며 **전문 미확보로 표기**.
4. **Y. Wang et al., "CMP Pad Conditioning Using the High-Pressure Micro-Jet Method",
   Micromachines 14(1), 200 (2023), DOI: 10.3390/mi14010200.** Gold OA(CC-BY),
   `find_open_access.py`로 OA 확인 후 본문 텍스트 확보.

## 2. 상용 디스크의 물리 규격 — 3M E187 TDS (출처 1, 표 직접 인용)

| 항목 | 값 |
|---|---|
| 캐리어 재질 | 304 스테인리스 |
| 캐리어 형태 | Ring (환형) |
| 캐리어 직경(공칭) | **260 mm / 360 mm** 두 종 |
| 연마재 | 니켈계 합금 + 패턴 배열 다이아몬드 |
| 작업면 형태 | **Segmented** (세그먼트 분할) |
| 다이아몬드 크기(공칭) | **181 µm** |
| 다이아몬드 등급 | Type 4, **semi-sharp** |
| 배열 패턴 | **Square array** (정사각 격자) |
| 디스크 평탄도 | **< 100 µm** |
| Aggressiveness Value (BL) | 260 mm: **70–90** / 360 mm: **55–75** |
| 기타 | 세그먼트마다 **Diamond Edge Exclusion Zone** 존재 |

- 스키마 함의: 실무자가 디스크를 고를 때 실제로 지정하는 축은 (a) 캐리어 직경, (b) 링/원판/
  세그먼트 형태, (c) 그릿 공칭 크기, (d) 등급(sharp/semi-sharp/blocky), (e) 배열 패턴,
  (f) 전면 평탄도, (g) edge exclusion, (h) aggressiveness 등급값이다. 이 8축은 모두
  **제품 카탈로그에 실존하는 지정 항목**이므로 스키마에 필드로 둔다.
- **미검증**: Aggressiveness Value(BL)의 무차원 정의식은 이 TDS에도 없다 —
  [[conditioner-grit-design-space]] §7의 동일 미해결 항목이 그대로 남아 있다.
  같은 그릿 사양에서 직경이 커질수록 값이 낮게 표기된다는 사실(70–90 vs 55–75)만 확인.

## 3. 디스크 설계 DOE에서 실제로 돌린 변수 (출처 2, 본문 Table 1 + 서술)

- **핵심 4변수**: Diamond Size / Shape / Density / **Exposure(돌출)**.
- **기타 고려 변수**: Disk front-side flatness, macro-scale topography 유무(plateau·valley
  구조 — 저자 서술상 "실효 그릿 밀도를 낮추는" 수단), diamond edge exclusion zone 크기.
- **실측 범위(본문 명시)**: 그릿 크기 **100–425 µm**, 천연·합성 다이아몬드 양쪽,
  **다이아몬드 노출(exposure) 0에 가까운 값 ~ 약 60%**. 60종 이상 설계, 70,000매 이상 연마.
- 스키마 함의: 돌출을 "µm"가 아니라 **입경 대비 % (exposure)** 로 지정하는 관행이
  존재한다 — [[diamond-grit-mesh-bonding]]의 JP4508514B2가 말한 "입경의 5~30%(종래) /
  30~150%(발명)"와 같은 표기 체계. 스키마에는 두 표기를 모두 필드로 둔다.

## 4. 컨디셔닝 레시피 축과 결과 지표 (출처 2)

- **컨디셔닝 duty**: 총 연마시간 110초 중 **75%** 동안 컨디셔닝 수행(in-situ). 즉
  "컨디셔닝 시간 비율(duty)"은 레시피에서 직접 지정하는 독립 축이다.
- **패드 마모율 실측**: 플래튼1 **0.87 mil/hr**, 플래튼2 **0.88 mil/hr**. 연장 런 전체에서
  총 패드 마모 **약 23 mils**, 그럼에도 패드 프로파일은 평탄 유지.
- **수명 실측**: 패드당 약 **1,150매**(패드세트당 2,350매, 범위 1,600–3,000). 디스크는
  두 번째 연장 런까지 **디스크당 60시간 이상 컨디셔닝, 5,300매 이상** 처리.
- **결과 지표**: 열산화막 제거율 평균 3,345 Å/min, WIWNU 2.2%(5 mm EE) / 3.8%(3 mm EE),
  결함 adder 평균 23개.
- **break-in**: 본문에 "**No disk break-in was conducted prior to this extended run**"이라고
  명시되어 있고, 별도로 CoO 개선 레버 목록에 "**reducing disk break-in time**"이 등장한다.
  → **break-in은 실무에서 존재하는 절차이나 신설계에서는 생략 가능한 축**이라는 것이
  1차 자료로 확인된다. 다만 **표준 break-in 시간·하중·매수의 정량값은 이 문헌에 없음 — 미검증**.
- **디스크 평탄도 → 패드 마모 균일도 → WIWNU 드리프트**의 인과가 본문에 명시:
  "Disk flatness irregularities can result in non-uniform pad wear, which in turn affects
  relative removal rates on the wafer... especially true at the edge of the wafer."
  → 스키마의 `flatness_um` 필드가 왜 결과(WIWNU)와 연결되는지의 근거.

## 5. 스윕 프로파일 최적화 (출처 3, 전문 미확보 — 발췌만)

- 시뮬레이터가 Preston 식 + 경험식(패드 그루브 기하, **컨디셔너 짐벌(gimbal) 동작**,
  **비균일 컨디셔너 디스크 프로파일**)으로 패드 두께 프로파일을 예측하고, 0.001 s 시간
  스텝으로 컨디셔닝 사이클을 적산한다는 서술.
- 방법론의 물리적 골자(발췌 인용): "changes in the **contact area** across the pad radius,
  different **linear velocities** and **residence time**" — 즉 반경별 (접촉면적 × 속도 ×
  체류시간)이 스윕 최적화의 3요소. [[conditioner-sweep-kinematics-pcr-profile]] §3의
  dwell-time 논리와 동일한 구조를 산업 툴 쪽에서 독립 확인.
- 각 접촉 존의 공칭 면적이 패드 중심→엣지에서 **약 40,000 ~ 250,000 mm²** 범위이며,
  속도 구배로 보상해 접촉 횟수를 반경 방향으로 균일하게 맞춘다는 서술.
- **결론(발췌)**: 패드 중간반경의 **doming**이 center-fast 제거로 이어지고, 스윕 프로파일
  리비전(rev no.3)으로 패드 두께 프로파일을 평탄화하면 산화막 제거 프로파일이 평탄·안정해진다.
- **미검증**: 스윕 리비전의 구체적 존별 dwell 비율·수치표는 전문 미확보로 확인 못 함.
  "스윕 프로파일이 존별 dwell 비율의 집합으로 지정된다"는 구조만 확인.

## 6. 다이아몬드 디스크가 유일한 컨디셔닝 수단은 아니다 (출처 4)

- 고압 마이크로제트(HPMJ) 컨디셔닝이 다이아몬드 디스크의 대안으로 실증됨. 3종 패드
  (폴리우레탄/댐핑클로스/부직포)에서 MRR 변동폭이 HPMJ 2.73–3.75 / 1.38–1.99 /
  2.36–4.32 µm/h vs 다이아몬드 디스크 (…)–4.14 / 1.02–2.09 / 1.78–5.88 µm/h.
- 다이아몬드 컨디셔닝은 10시간 시점에 MRR이 **51.2% 감소**(댐핑클로스 패드), HPMJ 쪽이
  변동이 작고 SEM상 패드 기공 막힘이 적었다.
- 스키마 함의: `method` 필드에 `diamond_disk` 외 `hpmj`(고압수제트) 옵션을 둘 근거.
  **단 이 실험은 SiC 웨이퍼·비-IC 패드 대상이라 IC용 CMP로의 일반화는 미검증.**

## 6b. 정량 재현 — 출처 간 교차대조 (2026-09-11 학습총괄 부채상환)

출처 1(3M E187 TDS)의 단일 제품값과 출처 2(SEMICON West 2000 DOE)의 실측 범위가
**서로 독립으로 확보된 1차 자료**이므로, E187이 DOE가 실제로 시험한 범위 안에
드는지를 교차대조한다. 또한 출처 2가 명시한 패드 마모율(mil/hr)과 총 마모(mils)가
같은 자릿수 오더로 정합하는지 단위환산으로 확인한다.

```python verify
# 대조 1: 3M E187 다이아몬드 공칭크기(181 µm, 출처1)가
#         AMAT/3M DOE 실측 그릿크기 범위(100–425 µm, 출처2 SEMICON West 2000)에 포함되는가
e187_diamond_um = 181
doe_range_um = (100, 425)
assert doe_range_um[0] <= e187_diamond_um <= doe_range_um[1], (
    f"E187 {e187_diamond_um}µm이 DOE 실측범위 {doe_range_um} 밖 — 두 1차 출처 불일치")

# 대조 2: Aggressiveness Value(AV)가 캐리어 직경이 클수록 낮다는 서술(§2)을
#         TDS 표의 두 구간값으로 정량 확인 — 문헌값 그대로 대조
av_260mm = (70, 90)
av_360mm = (55, 75)
assert av_260mm[0] > av_360mm[0] and av_260mm[1] > av_360mm[1], (
    "AV가 직경에 반비례한다는 서술과 표값이 불일치")

# 대조 3: 패드 마모율(mil/hr, 출처2 실측) → µm/hr 환산(1 mil = 25.4 µm, 정의값) —
#         스키마 필드 단위(µm)로 쓸 값의 자릿수 검산
plate1_mil_hr, plate2_mil_hr = 0.87, 0.88
plate1_um_hr = plate1_mil_hr * 25.4
plate2_um_hr = plate2_mil_hr * 25.4
# 문헌값(mil/hr)과 환산값(µm/hr)이 정의상 정확히 25.4배여야 함 — 계산기 오류 배제용 항등검산
assert abs(plate1_um_hr - 22.098) < 0.01 and abs(plate2_um_hr - 22.352) < 0.01, (
    f"단위환산 불일치: {plate1_um_hr:.3f}, {plate2_um_hr:.3f} µm/hr")
# 두 플래튼 마모율이 문헌 서술("거의 동일") 그대로 2% 이내 근접하는지 대조
rel_diff = abs(plate1_mil_hr - plate2_mil_hr) / plate1_mil_hr
assert rel_diff < 0.02, f"두 플래튼 마모율 차이 {rel_diff*100:.2f}% — 문헌 서술(거의 동일)과 불일치"

print(f"OK: E187 {e187_diamond_um}µm ⊂ DOE {doe_range_um}µm, "
      f"AV 직경반비례 확인, 마모율 {plate1_um_hr:.2f}/{plate2_um_hr:.2f} µm/hr (차이 {rel_diff*100:.2f}%)")
```
→ 재현 결과: 3건 모두 PASS(2026-09-11 실행). E187(181µm)은 DOE 범위 내, AV는 직경
반비례 서술과 정합, 두 플래튼 마모율 차이는 1.1%로 문헌의 "거의 동일" 서술과 대조 일치.
**단, 이 대조는 두 문헌이 서로를 인용하지 않은 독립 출처 간 정합성 확인이지, 제3의
검증기관 데이터와의 대조는 아니다 — 그 의미에서는 여전히 약한 검증이다(미검증 표기 유지).**

## 7. 미검증/한계 정리

- 3M E187 값은 **특정 제품 1점**의 카탈로그 값이다. 스키마의 `typical` 범위로 쓸 때는
  다른 제품군을 함께 확인해야 한다(현재 260/360 mm, 181 µm 두 점만 확보).
- Aggressiveness Value의 정의식은 세 번째 출처에서도 미확보(계속 미해결).
- break-in 절차의 정량 표준(시간/하중/DIW 여부/판정 기준)은 어느 출처에도 없다 —
  스키마에서 해당 필드는 전부 `confidence: unverified` + "⚠ 조사 필요"로 남긴다.
- 출처 3은 전문 미확보(유료). 인용한 문장은 academia.edu 게재본 발췌 텍스트이며,
  수치표(스윕 리비전 정의)는 확인하지 못했다.

## 관련 노트
[[diamond-grit-mesh-bonding]] · [[conditioner-grit-design-space]] ·
[[conditioner-grit-density-protrusion-cutrate]] · [[conditioner-sweep-kinematics-pcr-profile]] ·
[[conditioner-disk-pad-cutting-model]] · [[conditioner-grit-wear-scratch-lifetime]] ·
[[conditioning-mechanism-asperity-regeneration]]
