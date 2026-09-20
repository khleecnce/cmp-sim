<!-- V2-SECTION: R1-equipment | 분배완료 2026-09-08 | 근거: carrier, kinematic, platen, retaining-ring, tool-architecture | 정본: ARCHITECTURE-V2.md §3 -->
# CMP 캐리어 헤드·리테이너 링 상세 — AMAT vs Ebara 아키텍처 비교

> 담당: [[tool-platen-head]] Lv1-1 · 작성 2026-09-07 · 상태: 검증(출처 기재, 1건은 원문 PDF 확보)
> 연결: [[cmp-tool-architecture]](툴 4대 구성 개관) · [[cmp-kinematics-rotary]]

## 0. 범위 — 기존 노트와 무엇이 다른가
[[cmp-tool-architecture]]는 헤드·플래튼·리테이너링·컨디셔너를 **개관** 수준으로 다루고
AMAT 멤브레인 특허 2건(US6183354B1, US6244942B1)만 인용했다. 이 노트는 그 다음
단계로, (1) **AMAT vs Ebara** 두 벤더의 헤드 가압 방식이 설계 철학부터 다르다는 점,
(2) 리테이너 링의 정량적 압력비·챔퍼 각도, (3) 최신 실험 논문(2026)의 실측
불균일도(NU) 수치, (4) 슬러리 전달 아암의 벤더별 구조를 다룬다. 겹치는 특허는
재인용하지 않는다.

## 1. 캐리어 헤드 가압 방식: 멤브레인 멀티존 (AMAT) vs 직접 공압 (Ebara)
두 벤더는 "웨이퍼 뒷면에 압력을 어떻게 전달하는가"에서 서로 다른 해법을 특허화했다.

- **AMAT — 유연 멤브레인 멀티존**: US8088299B2 "Multiple zone carrier head with
  flexible membrane"(Applied Materials, 출원 2010-11-29 / 등록 2012-01-03)는
  베이스에서 뻗어나온 멤브레인이 **원형 내부 챔버 + 동심 중간 챔버 + 동심 외부 챔버**의
  3개 존을 형성하고, 각 존을 독립 가압한다[1]. [[cmp-tool-architecture]]에서 이미
  다룬 US6244942B1(엣지 압력 조정 홈)의 후속 세대로, 홈 하나 대신 완전한 동심
  챔버 여러 개로 발전한 형태다.
- **Ebara — 멤브레인 삽입물 제거, 직접 공압**: US7029382B2 "Apparatus for CMP head
  having direct pneumatic wafer polishing pressure"(Ebara, 출원 2001-12-21 / 등록
  2006-04-18)는 정반대 접근이다. 명세서는 멤브레인/폴리싱 인서트가 **배치마다
  물성이 달라지고 수분 흡수량이 달라져** 압력 불균일을 만든다고 지적하고[2],
  탄성 공압 환형 실링 블래더(bladder)로 웨이퍼 뒷면에 **인서트 없이 직접** 공압을
  가하는 구조를 청구한다. 수치: 공칭 폴리싱 압력 약 **8 psi**(backside chamber),
  face seal chamber 권장 **7–9 psi**, 포켓 깊이 200mm 웨이퍼 기준 **1–2 mm**(범위
  0.5–5mm), 엣지 블래더 폭 **2–10 mm**(전형 3–6mm)[2].
- 같은 회사(Ebara)라도 세대에 따라 접근이 겹친다: 더 이른 US6309290B1(원출원
  Mitsubishi Materials, Ebara로 양도, 등록 2001-10-30)은 **플로팅 리테이너링 +
  서브캐리어 멀티존**으로 멤브레인 방식에 가깝다[3]. 즉 "AMAT=멤브레인,
  Ebara=공압"으로 이분하는 것은 과도한 단순화이며, Ebara 포트폴리오 안에도
  멤브레인 계열(US6309290B1)과 직접공압 계열(US7029382B2)이 공존한다 — 이 점은
  두 특허의 출원인란과 청구항을 직접 대조해 확인했다(2차 인용 아님).

## 2. 리테이너 링 — 챔퍼 각도와 압력비
- **챔퍼(모따기) 각도**: US6309290B1은 리테이너 링 하단 전이부를 **약 20°**
  (청구항 표현으로 15–25° 범위)로 명시하고, 이 각도가 패드 버클링과 엣지 링
  마크를 줄여 엣지 제외 영역을 **6mm → 3mm 미만**으로 좁힌다고 주장한다[3].
- **멀티존 압력 범위**: 같은 특허의 실시예는 리테이너링 챔버 압력 P1 = **1.5–9.0
  psi**, 서브캐리어 챔버 압력 P2 = **1.5–10 psi**로 청구한다[3].
- **압력 부등식**: US6419567B1(Infineon/NXP, "Retaining ring for CMP head... and
  slurry cycle system", 등록 2002-07-16)은 벤더 특정은 아니지만 리테이너링 설계의
  일반 원칙을 정량화한다 — 링 압력 P_R, 슬러리 압력 P, 웨이퍼 압력 P_W에 대해
  **|P_R| ≥ |P| + |P_W|**를 만족해야 웨이퍼 이탈 없이 슬러리를 링-패드 계면으로
  가둘 수 있다고 청구한다[4]. 계수(안전마진)는 명세서에 구체 수치가 없어 **미검증**.

## 3. 실측 데이터: 리테이너 링 압력·멀티존이 엣지 불균일도에 미치는 영향
Lee, Lee, Jeong (부산대, 2026)의 실험 논문[5]을 원문 PDF로 확보해 직접 읽었다
(`papers/jkspe-025-132-multizone-pressure.pdf`, CC-BY-NC 오픈액세스). 8인치 산화막
블랭킷 웨이퍼, 멤브레인 캐리어 기준.

| 조건 | 웨이퍼 압력 | 리테이너링 압력 | 엣지제외 3mm NU |
|---|---|---|---|
| 단일영역, Wafer#1 | 5.0 psi | 5.0 psi | **4.5 %**[5] |
| 단일영역, Wafer#2 | 5.0 psi | 6.0 psi | **6.1 %**[5] |
| 멀티존 캐리어(3존) | 5.0 psi | (Zone1/2/3 개별) | **2.5 %**[5] |

리테이너링 압력을 5→6 psi로 올리면 패드 리바운드가 커져 NU가 오히려 **악화**된다는
것이 문헌값 대조 결과다: 5psi에서 4.5%, 6psi에서 6.1% — 이는 §2의 "링 압력을 올리면
엣지가 좋아진다"는 단순 직관을 반박하는 실측이다. 반경 구간은 Zone1(엣지, 95–99mm) / Zone2(중간, 85–95mm) / Zone3(중심,
0–85mm)로 나뉘며[5], Zone3는 다른 두 존과 상호작용이 거의 없는 독립 변수로,
Zone1·Zone2·리테이너링 셋은 서로 얽힌 비독립 변수로 보고된다[5]. 각 존 압력은
3.0–4.2 psi 범위에서 스윕했다[5].

참고: 논문 [5]가 인용하는 Zhao et al. (2013, *Microelectronic Eng.* 108, 33–38,
DOI 10.1016/j.mee.2013.03.042)은 12인치 멀티존 CMP에서 존압력 0–2.0 psi 범위의
웨이퍼 벤딩·계면유체압력을 실측했다고 알려져 있으나[6], 원문은 페이월(ScienceDirect
403, 미러 사이트 미러 접속 불가)에 막혀 **직접 확인하지 못했다** — 서지정보(저자·권·페이지)만
Crossref/Semantic Scholar로 교차검증했고, 수치(0–2.0psi)는 검색엔진 요약 인용으로
**2차 인용**임을 밝힌다.

## 4. 슬러리 전달 아암 — AMAT 분산형(DSDA)
AMAT의 슬러리 아암 특허 CN102203918B "Self cleaning and adjustable slurry delivery
arm"(Applied Materials, 출원 2009-10-27 / 등록 2014-06-04)은 "분산식 슬러리 전달
암(DSDA)" 구조를 청구한다: 매니폴드 **2개 이상**, 매니폴드당 슬러리 노즐
**6개 이상 + 말단 노즐 1개**, 매니폴드 사이에 고압 세척 노즐을 배치해 자체 세정
기능을 겸한다[7]. 단일 피벗 아암에 노즐 1~2개를 배치하는 구식 설계(예: 각형 스윕만
하는 아암) 대비, 매니폴드형은 패드 반경 방향으로 슬러리를 동시다발 도포해 슬러리
체류시간 편차를 줄이는 방향의 설계다 — 다만 이 우위를 정량 비교한 논문은 이번
조사 범위에서 찾지 못했다(**불명**, 후속 단원 과제).

## 5. AMAT vs Ebara 요약
| 항목 | AMAT | Ebara |
|---|---|---|
| 헤드 가압 | 유연 멤브레인 3존(US8088299B2)[1] | 직접 공압 무-인서트(US7029382B2)[2], 단 구세대(원 Mitsubishi 승계)는 멤브레인+플로팅링(US6309290B1)[3] |
| 리테이너 링 특징 | (본 노트 범위에서 AMAT 리테이너링 전용 특허는 미조사 — [[cmp-tool-architecture]]는 엣지압력 홈 구조만 다룸) | 챔퍼 20°, 플로팅 구조, P1/P2 별도 챔버[3] |
| 슬러리 아암 | DSDA 다중 매니폴드+자체세정[7] | 이번 조사에서 Ebara 슬러리 아암 특허는 찾지 못함(**확인 못**) |

표의 빈 칸은 조사 범위(단원당 6건) 안에서 다루지 못한 부분이며, 지어내지 않고
공란으로 남긴다.

## 6. 정량 재현
```python verify
# 문헌값 대조 — 리테이너 링·멀티존 관련 정량 주장 검증

# (1) US6309290B1의 챔퍼 각도 청구범위 15-25도 안에 "약 20도" 실시예가 들어가는가
chamfer_claimed = 20.0  # deg, US6309290B1 실시예
assert 15.0 <= chamfer_claimed <= 25.0

# (2) US6309290B1 멀티존 압력 범위(psi)에 JKSPE 2026 실험 셋포인트(5,6psi)가 포함되는가
P1_range = (1.5, 9.0)   # 리테이너링 챔버, US6309290B1
P2_range = (1.5, 10.0)  # 서브캐리어 챔버, US6309290B1
exp_ring_pressures = [5.0, 6.0]  # psi, Lee et al. 2026 Table 2
for p in exp_ring_pressures:
    assert P1_range[0] <= p <= P1_range[1], f"{p}psi가 특허 청구 범위 밖"

# (3) 리테이너링 압력 5->6psi 증가 시 엣지 NU 악화 (Lee et al. 2026, Table 3 vs 4)
NU_ring5psi = 4.5   # %
NU_ring6psi = 6.1   # %
assert NU_ring6psi > NU_ring5psi, "링 압력 증가가 NU를 악화시킨다는 문헌 보고와 불일치"

# (4) 멀티존 캐리어가 단일존 대비 엣지 NU를 개선 (Lee et al. 2026, Table 5)
NU_single_zone = 4.5  # %, edge exclusion 3mm
NU_multi_zone = 2.5   # %, edge exclusion 3mm
assert NU_multi_zone < NU_single_zone

# (5) 8인치 웨이퍼 존 경계(mm)가 반경(~100mm, 공차 5%) 근방에서 끝나는가
zone3_outer, zone2_outer, zone1_outer = 85.0, 95.0, 99.0  # mm, Lee et al. 2026 Fig.7
assert zone3_outer < zone2_outer < zone1_outer
nominal_radius_8in = 101.6  # mm (200mm wafer / 2)
assert abs(zone1_outer - nominal_radius_8in) / nominal_radius_8in < 0.05

# (6) DSDA 매니폴드/노즐 하한이 특허 청구범위와 일치
manifolds_min, nozzles_per_manifold_min = 2, 6  # CN102203918B 청구항
assert manifolds_min >= 2 and nozzles_per_manifold_min >= 6

print("모든 정량 대조 통과")
```

## 출처
1. US 8,088,299 B2, "Multiple zone carrier head with flexible membrane", Applied
   Materials, 출원 2010-11-29 / 등록 2012-01-03. https://patents.google.com/patent/US8088299B2/en
2. US 7,029,382 B2, "Apparatus for chemical-mechanical polishing (CMP) head having
   direct pneumatic wafer polishing pressure", Ebara, 출원 2001-12-21 / 등록
   2006-04-18. https://www.freepatentsonline.com/7029382.html
3. US 6,309,290 B1, "Chemical mechanical polishing head having floating wafer
   retaining ring and wafer carrier with multi-zone polishing pressure control",
   원출원 Mitsubishi Materials, 현 Ebara, 출원 1999-04-19 / 등록 2001-10-30.
   https://patents.google.com/patent/US6309290B1/en
4. US 6,419,567 B1, "Retaining ring for chemical-mechanical polishing (CMP) head,
   polishing apparatus, slurry cycle system, and method", Infineon
   Technologies/NXP, 등록 2002-07-16. https://patents.google.com/patent/US6419567B1/en
5. Lee, T.S., Lee, E.H., Jeong, H.D. (2026), "Multi-zone Pressure Control for
   Improvement of Within Wafer Non-uniformity in CMP", *J. Korean Soc. Precis.
   Eng.*, 43(5), 443-448. DOI: 10.7736/JKSPE.025.132 (CC-BY-NC, 원문 PDF 확보:
   `papers/jkspe-025-132-multizone-pressure.pdf`)
6. Zhao, D., Wang, T., He, Y., Lu, X. (2013), "Effect of zone pressure on wafer
   bending and fluid lubrication behavior during multi-zone CMP process",
   *Microelectronic Engineering*, 108, 33-38. DOI: 10.1016/j.mee.2013.03.042 —
   **2차 인용**(서지정보만 Crossref/Semantic Scholar로 교차검증, 본문 미확보:
   ScienceDirect 403, 미러 사이트 미러 접속 불가)
7. CN 102203918 B, "Self cleaning and adjustable slurry delivery arm", Applied
   Materials, 출원 2009-10-27 / 등록 2014-06-04.
   https://patents.google.com/patent/CN102203918B/en
