<!-- V2-SECTION: R1-equipment | 공동: R5-wafer | 분배완료 2026-09-08 | 근거: carrier, platen, retaining-ring | 정본: ARCHITECTURE-V2.md §3 -->
# 리테이너링 압력·마모와 엣지 프로파일 — FEA 접촉응력과 특허 구조 비교

> 담당: [[tool-platen-head]] Lv2-1 · 작성 2026-09-07 · 상태: 검증(1차 출처 2건, python verify)
> 연결: [[cmp-carrier-head-retaining-ring-vendors]](Lv1-1) ·
> [[cmp-multizone-carrier-radial-response]](Lv1-2, 존압력 스윕 실험) ·
> [[cmp-tool-architecture]]

## 0. 범위

Lv1-2가 "존 압력을 바꾸면 반경별 제거율이 어떻게 반응하는가"(경험적·실험적)를
다뤘다면, 이 단원은 리테이너링 자체의 역학 — 왜 링이 있으면 엣지 프로파일이
개선되는가(FEA 접촉응력 관점)와, 링 설계를 바꿔 엣지 제거율을 능동적으로
조절하는 특허 구조(공학적 관점) 둘을 다룬다. `tools/scope.py --agent
tool-platen-head`가 준 검색어("tool platen head CMP patent after:2011") 범위
안에서 조사했다.

## 1. 리테이너링이 없으면 엣지에서 무슨 일이 일어나는가 — FEA 정적 모델[1]

Zheng, Zhao, Lu(2023)[1]는 12인치(300mm) 플랫폼의 패드-웨이퍼 접촉을 정적
FEA로 모델링했다. 핵심 파라미터(원문 Table 3):

| 파라미터 | 값 |
|---|---|
| 서브패드 탄성계수 | 3.9 MPa (Poisson 0.4) |
| 웨이퍼 두께 / 탄성계수 | 775 μm / 193 GPa (Poisson 0.3) |
| 리테이너링 재질 | Polyphenylene Sulfide (PPS) |
| 리테이너링 탄성계수 | 210 GPa (Poisson 0.3) — **미검증**: 원문 표기가 PPS(통상 3-4 GPa 폴리머)와
  金屬(steel~210GPa) 값이 혼재되어 보임. 저자 표에 링과 지지 스테인리스 스틸 링이
  결합된 구조로 명시("stuck to a stainless steel ring")되어 있어, 210GPa은 폴리머
  단독이 아니라 결합체의 등가값일 가능성 — 원문에서 명확한 재확인 못함.
| Downforce P1/P2 | 4.3 psi / 3.5 psi |

원문의 정성적 결론(원문 인용, 저자 국문 초록 아님 — 이 노트가 영문 원문을 한국어로
번역): "리테이너링이 있는 경우와 없는 경우의 접촉응력을 비교한 결과, 링이 없을 때
웨이퍼 가장자리 영역의 평균(mainstream) 응력이 먼저 감소했다가 급격히 위로
휘어 오르며(warps upwards), 이는 응력 집중을 유발한다. 링이 있으면 이 효과가
완화되어 웨이퍼 엣지 오버폴리싱(edge over-polishing) 문제를 줄인다."[1] §4.2.

정량값(원문 Figure 18 설명 텍스트, 수치표 아님 — **비율만 확인, 절대 응력값 MPa는
원문 그래프에서만 확인 가능해 이 노트는 텍스트 서술 비율만 인용**):
- 중심 영역 일부 노드의 접촉응력: mainstream(평균) 대비 약 **2배**
- 엣지 영역 일부 노드: 링 있음(Fig 17a) 조건에서 mainstream 대비 약 **3배**,
  링 없음(Fig 17b) 조건에서 약 **4배**

즉 이 논문이 정량적으로 보여주는 것은 "리테이너링을 제거하면 엣지 응력 집중이
mainstream 대비 3배→4배로 악화된다"는 **상대 비율**이지, 절대 psi/MPa 압력값이
아니다. Preston 방정식(MRR ∝ 응력×상대속도)에 따르면 이 응력 집중이 그대로
국소 제거율 급증(=엣지 오버폴리싱)으로 이어진다는 것이 원문의 논리 연결이다[1]§4.2.

## 2. 리테이너링 설계로 엣지 제거율을 능동 조절 — US7121927B2[2]

Applied Materials 계열 특허 US7121927B2(원출원 2004, division of 10/930,076)는
Lv1-1에서 다룬 "표준 리테이너링은 항상 엣지 저제거율을 준다"는 문제를 링의
**기계적 구조**로 해결하려 한다.

핵심 청구 구조:
- 표준 200mm 웨이퍼용 리테이너링: 슬러리 채널 12개, 각 채널이 각도지게(회전
  방향으로) 배치됨
- 개선형: 채널마다 번갈아 "리세스"(패드와 접촉하지 않는 오목부)를 둬서, 접촉이
  실제로 일어나는 세그먼트("탭")의 총 길이가 **웨이퍼 둘레의 약 11.5%**로 줄어듦
  (6개 세그먼트, 200mm 웨이퍼 기준)[2]
- 결과: 표준링은 "항상 낮은 엣지 제거율"을 주지만, 개선형은 내부튜브압력(ITP)을
  조절하면 엣지 제거율을 중심보다 **높게도, 같게도, 낮게도** 만들 수 있다 —
  즉 접촉 면적을 줄여 링-패드 상호작용이 웨이퍼 엣지 프로파일에 미치는 영향
  자체를 조절 가능한 변수로 바꾼 것[2].

이 특허는 정량적 압력-제거율 곡선(그래프 도면 FIG.4~5)을 언급하지만 특허 텍스트
자체에는 수치가 표로 정리되어 있지 않다(도면 판독 필요, 이 노트에서는 확보 못함
— **미검증**).

## 3. 1절-2절 종합 — 왜 "링이 있으면 좋다"가 전부가 아닌가

1절(FEA)은 "링이 있으면 없을 때보다 낫다"(정성적으로 확실)를 보여주고, 2절
(특허)은 "표준형 링도 사실 최적이 아니다 — 접촉 구조를 바꾸면 엣지 제거율을
목표대로 튜닝 가능하다"는 것을 보여준다. 두 문헌을 합치면 리테이너링의 역할은
"엣지를 보호하는 수동 부품"이 아니라 "접촉 면적·압력을 통해 엣지 제거율을
조절하는 능동 설계 변수"로 재정의된다 — 이는 Lv1-2에서 관찰한 "5→6psi 승압시
NU가 오히려 악화(4.5%→6.1%)"[3] 현상과 정합적이다: 표준형 링에서는 압력을
올려도 접촉 구조 자체가 최적이 아니므로 패드 리바운드 효과가 이긴다.

## 4. python verify — 특허 접촉 세그먼트 비율, FEA 응력 배율 재현

```python verify
import math

# --- US7121927B2: 200mm 웨이퍼, 6개 세그먼트, 전체 접촉길이 = 둘레의 11.5% ---
wafer_d_mm = 200.0
circumference = math.pi * wafer_d_mm
contact_fraction = 0.115  # 특허 명시값[2]
contact_length_mm = circumference * contact_fraction

assert abs(contact_fraction - 0.115) < 1e-9
# 세그먼트 6개라면 세그먼트 하나당 평균 호 길이(원문은 세그먼트 개별 길이를
# 명시하지 않음 — 이 계산은 노트의 유도치이지 원문 수치가 아님, 균등 분배 가정)
n_segments = 6
avg_segment_arc_mm = contact_length_mm / n_segments
print(f"200mm 웨이퍼 둘레: {circumference:.1f}mm, 접촉 세그먼트 총길이: "
      f"{contact_length_mm:.1f}mm ({contact_fraction*100:.1f}%), "
      f"세그먼트당 평균(균등가정) {avg_segment_arc_mm:.1f}mm")

# --- Zheng, Zhao, Lu (2023): 응력 집중 배율 (mainstream 대비) ---
mainstream_ratio = 1.0
center_ratio = 2.0     # 중심 일부 노드
edge_with_rr_ratio = 3.0    # 링 있음
edge_without_rr_ratio = 4.0  # 링 없음

# 링 제거로 인한 엣지 응력 집중 악화율
degradation = (edge_without_rr_ratio - edge_with_rr_ratio) / edge_with_rr_ratio * 100
assert abs(degradation - 100/3) < 1e-6
print(f"리테이너링 제거 시 엣지 응력집중 배율: {edge_with_rr_ratio:.0f}배 -> "
      f"{edge_without_rr_ratio:.0f}배 ({degradation:.1f}% 악화)")

# Preston 관계: MRR ∝ P x v. 응력배율이 곧 국소압력 배율이라면(v 고정 가정,
# 이 노트의 단순화 — 원문은 v도 반경에 따라 변한다고 명시하나 이 근사에서는 무시)
# 국소 제거율도 같은 배율로 악화된다는 정성적 결론만 유효. 절대 nm/min 계산은
# Kp 값이 없어 불가 — 미검증으로 남긴다.
print("주의: 이 배율은 상대 응력비이며 절대 압력(psi/MPa)이나 절대 제거율")
print("(nm/min) 계산에는 쓸 수 없다 — 원문 그래프에 절대값이 있으나 이 노트는")
print("텍스트 서술 배율만 확보했다(미검증: 절대 응력 MPa 값).")
```

실행 결과(2026-09-07 확인): 200mm 웨이퍼 둘레 628.3mm, 접촉 세그먼트 총길이
72.3mm(11.5%), 6분할 균등가정 시 세그먼트당 12.1mm(원문 미확인 유도치).
리테이너링 제거 시 엣지 응력집중 배율이 3배→4배로 33.3% 악화 — 이 배율 자체는
원문[1] 텍스트에 명시된 값이며, "33.3% 악화"는 이 노트가 계산한 유도치다.

## 5. 한계 및 다음 단원 연결

- **1차 미확보**: Touzov, Fujita, Doy(2001, IEEE ISSM, DOI 10.1109/ISSM.2001.962981)
  — "Novel retaining ring to reduce CMP edge exclusion"은 US7121927B2가 인용하는
  것으로 추정되는 원 연구이나, IEEE Xplore 페이월이고 미러 사이트 5개 미러가 이번
  조사에서도(Lv1-2와 동일 증상) 응답하지 않아 미확보. 특허 명세서(2절)로 대체.
- 1절 FEA 논문의 절대 응력값(MPa 단위 실제 그래프 수치)은 이 노트에서 확보하지
  못했다 — Figure 17/18의 도면 판독이 필요하나 텍스트 추출만으로는 불가능.
  **미검증**으로 남긴다.
- 리테이너링 탄성계수 210GPa(PPS 표기와 불일치 가능성)는 1절에서 지적한 대로
  **미검증** — 원문의 스테인리스 지지링 결합 여부를 재확인 필요.
- 다음 단원(Lv2-2, RPM비·유량·온도와 MRR 안정성)로 진행. 이 단원에서 확보한
  "링 구조가 엣지 제거율의 능동 조절 변수"라는 결론은 Lv3-2(툴 설정→압력·속도
  분포 모델)에서 Recipe의 리테이너링 압력 필드 설계 시 참고할 것.

## 구현 요청 후보 (직접 구현하지 않음 — software 부문 BACKLOG용, ORG.md §5 규칙)
- 무엇을: 없음(우선순위 낮음). 이 단원은 정성적 결론(응력비, 접촉면적비)만
  확보했고 절대 압력→제거율 전달함수가 없어 지금 구현하면 추측이 된다.
  Lv1-2와 동일한 결론 — Zhao 2013/Touzov 2001 원문 확보가 선행 과제.

## 출처
[1] Zheng, P., Zhao, D., Lu, X. (2023), "Prediction of Pad Wear Profile and
    Simulation of Its Influence on Wafer Polishing", Micromachines 14(9), 1683,
    DOI: 10.3390/mi14091683, PMC10536193. 원문 확보: MDPI 직접 다운로드 403(Access
    Denied/Akamai edgesuite) 및 PMC PDF PoW챌린지(curl 차단)로 실패, **Europe PMC
    REST API fullTextXML로 본문 확보**(papers/mi14091683-fulltext.xml, CC-BY).
[2] US7121927B2, "Retaining ring structure for edge control during chemical
    mechanical polishing" (division of US7029375), Applied Materials 계열,
    출원 2004(원출원 10/930,076). Google Patents 원문 확보(공개 특허 전문).
[3] [[cmp-multizone-carrier-radial-response]] §3 (Lee, Lee, Jeong 2026, JKSPE,
    단일존 5/6psi NU 4.5%/6.1%) — 3절 종합 논의에 재사용.
