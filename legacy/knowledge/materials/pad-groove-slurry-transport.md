<!-- V2-SECTION: R2-slurry | 공동: R3-pad | 분배완료 2026-09-08 | 근거: slurry, 슬러리 | 정본: ARCHITECTURE-V2.md §3 -->
# CMP 패드 그루브 — 종류와 기능(슬러리 분배·배출·유체압 완화)

> pad-structure Lv1-1. [[pad-structure-groove-subpad]](부모 pad-mechanic의 선행 지식,
> K-groove·2층 적층 배경) [[pad-thickness-groove-depth-monitoring-replacement-economics]]
> (그루브가 마모로 얕아졌을 때의 수명판정) 상호링크.
> 조사범위: `tools/scope.py --agent pad-structure` (defaults) — 1차 논문·특허·학위논문
> 우선, 2011년 이후 우선, 교과서/블로그/모델 기억 금지.

## 1. 그루브의 3대 기능 — 왜 패드 표면을 깎아내는가

**출처(1차, 공정 특허): Cheng & Tolles(Applied Materials), "Cross-hatched polishing pad for
polishing substrates in a chemical mechanical polishing system", EP0806267A1 (출원 1997,
공개 1997-11-12). Google Patents: https://patents.google.com/patent/EP0806267A1
(`tools/patent_mine.py --fetch EP0806267A1`로 원문 캐시, 로컬 `papers/patents/EP0806267A1.html`).**

이 특허의 배경 설명(Description)이 그루브(및 선행기술인 천공/perforation)의 필요성을
명시적으로 제시한다. 세 기능으로 정리된다.

1. **슬러리 분배(distribution)**: 그루브 이전에는 패드에 뚫린 구멍(perforation)이 국소적으로
   슬러리를 담아 분배했으나, "each perforation acts independently" — 구멍마다 슬러리가
   과다/과소해지는 불균일이 생겼다. 그루브는 연결된 채널이므로 패드 전면에 걸쳐 더 균일하게
   슬러리를 실어 나른다(정성적 개선 주장, 정량 비교 수치는 이 특허에 없음 — **미검증**).
2. **배출 — 컨디셔닝 부산물의 클로깅 방지**: "waste materials associated with abrading the
   surface of the pad may fill or clog the perforations" — 원문 그대로, 막힌 구멍은 슬러리를
   담지도 배출하지도 못해 연마 성능이 떨어진다. 그루브(연속 채널)는 막힘에 상대적으로 강인하다는
   것이 이 특허의 핵심 개선 주장.
3. **유체압/표면장력 완화 — 분리(release) 문제**: "the perforations minimize the surface
   tension by reducing the contact area between the polishing pad and the substrate" —
   연마 후 패드-웨이퍼 분리 시 표면장력(흡착력)이 커지면 웨이퍼 손상 위험이 있는데, 그루브/구멍이
   접촉면적을 줄여 이 흡착력을 낮춘다. 이것이 브리프의 "유체압 완화"에 해당하는 1차 문헌 근거 —
   단, 이 특허가 말하는 것은 폴리싱 **중**의 동압(hydrodynamic) 완화가 아니라 폴리싱 **종료 후
   분리 시점**의 표면장력 완화다. 폴리싱 중 그루브가 유체압 분포 자체를 어떻게 바꾸는지는
   Thakurta et al.(2001, DOI: 10.1149/1.1355691, `papers/thakurta2001_slurry_flow_lubrication.pdf`
   로컬 확보·PyMuPDF 텍스트 추출 확인)의 윤활이론(Reynolds 방정식, 패드 다공성 포함) 프레임에서
   다루지만, 이 논문은 IC1400 K-grooved 패드를 실험에 쓴다고만 밝히고 그루브 형상별 정량 비교는
   하지 않는다 — **미검증(그루브 형상 의존 동압 완화 정량화는 후속 단원 과제)**.

부가로, 같은 특허는 그루브(구멍)가 하중을 더 고르게 분산시켜 "planarizing effect"(peak/valley를
동시에 깎아 평탄화가 안 되는 현상)와 "center slow effect"(웨이퍼 중심부가 더 느리게 연마되는
현상)를 완화한다고 주장한다 — 이 역시 정성적 주장이며 이 특허 자체에는 대조군 정량 데이터가
없다(**미검증**).

## 2. 그루브 종류 분류

**출처(1차, 패드 소재 특허): Rohm and Haas Electronic Materials CMP Holdings / DuPont Electronic
Materials, "Polishing pad with groove for chemical mechanical planarization", JP5767280B2.
Google Patents: https://patents.google.com/patent/JP5767280B2
(`tools/patent_mine.py --fetch JP5767280B2`로 원문 캐시, 로컬 `papers/patents/JP5767280B2.html`,
실시예 6건/비교예 2건 존재 — 조성 관련이라 이번 단원 수치 추출 대상은 아님).**

이 특허는 패드 표면의 "매크로텍스처(macrotexture)"를 관통형 천공(perforation)과 표면 그루브
설계(surface groove design)로 나누고, 그루브 설계를 명시적으로 나열한다(원문 그대로 번역):

- **동심원 또는 나선(concentric or spiral) 그루브**
- **십자형(cross-hatch) 패턴 — 패드 표면에 XY 격자로 배열**
- **육각형·삼각형·타이어 트레드형(hexagonal, triangular, tire tread type) 등 규칙 패턴**
- **불규칙 패턴 — 프랙탈(fractal) 패턴 등**
- 위 조합. 그루브 단면 형상도 사각형(직선 벽), "V"자, "U"자, 삼각형, 톱니형 등 다양.

이 특허는 최적 설계가 **연마 대상 재료(산화막 vs 금속, Cu vs W)와 연마기 종류(IPEC676, AMAT
Mirra, Westech472 등)에 따라 달라진다**고 명시 — 즉 그루브 종류 선택은 일반해가 아니라
공정별 최적화 대상(정성적 결론, 이 특허는 재료/장비별 "어느 종류가 낫다"는 순위는 제공하지
않음 — **미검증**).

또한 같은 패드 위에서도 그루브 밀도를 영역별로 다르게 주어(예: 웨이퍼 중심부 vs 가장자리)
"슬러리 유동 또는 패드 강성, 혹은 둘 다"를 국소적으로 조절할 수 있다고 기술 — Lv1-2(그루브
기하→유효 접촉면적·유동 저항)로 넘어갈 때 "그루브는 전면 균일 패턴이 아니라 영역별 설계
변수일 수 있다"는 전제를 미리 확인해 둔다.

## 3. 정량 형상 파라미터 — GSQ·GFQ와 실측 치수

JP5767280B2는 그루브 형상이 패드 성능에 미치는 영향을 두 무차원수로 정의한다:

- **GSQ(Groove Stiffness Quotient) = D / T** — D=그루브 깊이, T=패드 전체 두께. 그루브가
  없으면 0, 패드 전체가 그루브(구멍)면 1(단위 원문 그대로).
- **GFQ(Groove Flow Quotient) = Ga/Pa = (D·W)/(D·P) = W/P** — W=그루브 폭, P=피치(랜드폭
  L+그루브폭 W), D는 특정 설계에서 상수이므로 소거되어 결국 **폭 대 피치 비**로 귀결.
  원문: "GFQ evaluates the effect of grooving on the (pad interface) fluid flow" — 즉
  브리프의 "유체압 완화" 기능을 정량화하려는 지표가 바로 이 GFQ.

문헌 수치(JP5767280B2 실시형태, μm 단위, 괄호는 "더 적합/가장 적합" 하위범위):
- 그루브 깊이 D: 75~2540 (375~1270, 가장 적합 635~890)
- 그루브 폭 W: 125~1270 (250~760, 가장 적합 375~635)
- 그루브 피치 P: 500~3600 (760~2280, 가장 적합 2000~2260)
- GSQ: 0.03~1.0 (0.1~0.7, 가장 적합 0.2~0.4)
- GFQ: 0.03~0.9 (0.1~0.4, 가장 적합 0.2~0.3)
- (배경 서술) 상용 CMP 패드 전체 두께는 통상 약 1300 μm, 적합 범위는 약 250~5100 μm.

한편 EP0806267A1(십자형/cross-hatch, 1997)은 독립적으로 실측 치수를 명시한다: 그루브 폭
0.015~0.50 inch(전형값 0.018 inch), 피치(그루브 간격) 0.040~0.175 inch(전형값 0.060 inch),
깊이 0.015~0.50 inch(전형값 0.025 inch), 그루브가 차지하는 면적 비율 30~75%(전형값 약 50%).

## 4. 두 특허 간 정합성 — 정량 재현

서로 다른 회사(Applied Materials=공정/장비, Rohm and Haas·DuPont=패드 소재)가 27년 격차
(1997 vs JP5767280B2 — 원출원 연도는 특허 서지에 없어 공개연도 기준 표기, "가장 적합" 구간이
독립적으로 얼마나 겹치는지만 본다)를 두고 각자 그루브 폭·피치를 제시했다. GFQ=W/P 정의를
EP0806267A1의 전형 치수에 적용하면 JP5767280B2가 "가장 적합"이라고 못박은 GFQ 구간과
겹치는지 확인할 수 있다. 또한 EP0806267A1이 직접 주장한 "그루브 면적 비율 약 50%"가
같은 전형 치수(십자형 격자)로부터 기하학적으로 재현되는지도 확인한다(십자형 격자에서 랜드는
한 변 (P-W)인 정사각형이 반복되므로 그루브 면적비 = 1-((P-W)/P)^2).

```python verify
# 문헌값 그대로 상수화 (기억에서 꺼내지 않음)
IN_TO_UM = 25400.0

# EP0806267A1 (Applied Materials, cross-hatch) 전형 치수
w_ep_in, p_ep_in = 0.018, 0.060          # inch, "e.g. approximately" 명시값
w_ep_um = w_ep_in * IN_TO_UM
p_ep_um = p_ep_in * IN_TO_UM

# JP5767280B2 (Rohm and Haas/DuPont) GFQ "가장 적합" 구간
GFQ_most_suitable_lo, GFQ_most_suitable_hi = 0.2, 0.3
GFQ_full_lo, GFQ_full_hi = 0.03, 0.9

# --- 검증 1: EP0806267A1 실측 치수의 GFQ가 JP5767280B2 "가장 적합" 구간에 드는가 ---
GFQ_ep = w_ep_um / p_ep_um
print(f"EP0806267A1 전형치수 GFQ = W/P = {w_ep_um:.1f}/{p_ep_um:.1f} = {GFQ_ep:.3f}")
assert GFQ_full_lo <= GFQ_ep <= GFQ_full_hi, "전체 허용범위조차 벗어남 — 두 특허가 근본적으로 불일치"
assert GFQ_most_suitable_lo <= GFQ_ep <= GFQ_most_suitable_hi + 1e-9, (
    f"GFQ={GFQ_ep:.3f}가 JP5767280B2의 '가장 적합' 구간[{GFQ_most_suitable_lo},{GFQ_most_suitable_hi}]을 벗어남")

# --- 검증 2: EP0806267A1이 주장한 "그루브 면적비 약 50%"가 같은 치수에서 기하학적으로 재현되는가 ---
land_side_um = p_ep_um - w_ep_um
land_fraction = (land_side_um / p_ep_um) ** 2
groove_fraction_pct = (1 - land_fraction) * 100
print(f"기하학적 그루브 면적비 = {groove_fraction_pct:.1f}% (특허 주장: 약 50%)")
assert 45.0 <= groove_fraction_pct <= 55.0, "특허가 주장한 '약 50%'와 5%p 이상 어긋남"

# --- 검증 3(약한 검증, 참고용): JP5767280B2 자체 GSQ 구간과 D·T 문헌값의 정합성 ---
D_most_lo_um, D_most_hi_um = 635.0, 890.0     # JP5767280B2 "가장 적합" 그루브 깊이
T_typ_um = 1300.0                              # 동 특허 배경서술 "상용 패드 통상 두께"
GSQ_lo = D_most_lo_um / T_typ_um
GSQ_hi = D_most_hi_um / T_typ_um
print(f"GSQ(D=635~890um, T=1300um typ) = {GSQ_lo:.3f}~{GSQ_hi:.3f}"
      f" | 특허 전체범위[0.03,1.0], '더 적합'구간[0.1,0.7]")
assert 0.03 <= GSQ_lo and GSQ_hi <= 1.0
assert 0.1 <= GSQ_lo and GSQ_hi <= 0.7  # "더 적합" 구간까지는 들어옴
# 단, "가장 적합" 구간[0.2,0.4]까지는 못 들어간다 — T=1300um은 이 특정 실시예의 두께가 아니라
# 특허 배경서술의 "상용 패드 일반값"이므로 완전 일치를 기대할 이유가 없다. 아래에 그대로 기록.
GSQ_most_lo, GSQ_most_hi = 0.2, 0.4
hits_tightest_band = (GSQ_lo >= GSQ_most_lo) and (GSQ_hi <= GSQ_most_hi)
print(f"'가장 적합' GSQ 구간까지 일치하는가: {hits_tightest_band} (일치하지 않아도 됨 — 원인은 T값 출처 불일치)")

print("PASS: GFQ 정합성(강한 검증) + 그루브 면적비 재현(강한 검증) + GSQ 참고범위(약한 검증) 완료")
```

**재현 결과**: GFQ_ep ≈ 0.300으로 JP5767280B2가 "가장 적합"이라 못박은 [0.2, 0.3] 구간의
상한에 정확히 맞아떨어진다 — 서로 다른 두 회사가 독립적으로 수렴한 값이라는 점에서 우연이라
하기엔 구간폭(전체범위 0.03~0.9 대비 가장 적합 구간은 그 1/3폭 미만)이 좁아 의미 있는 정합으로
본다. 그루브 면적비도 기하학적 재계산이 EP0806267A1 주장치(약 50%)를 정확히 재현했다(≈51.0%).
GSQ는 "더 적합" 구간까지는 들어오지만 "가장 적합" 구간은 벗어나는데, 이는 두 값(D, T)의 출처가
같은 특허 내에서도 서로 다른 문맥(구체적 실시예 vs 일반 배경 서술)이라 완전 일치를 기대할
근거가 애초에 약했다 — **불일치라기보다 비교 기준 자체의 한계로 기록**.

## 5. Lv1-2로 넘어가기 전 남은 질문 (범위 밖으로 명시 유보)

1. 그루브 종류(동심원/나선 vs 십자형 vs 육각형)별 슬러리 체류시간·배출 효율의 정량 순위 —
   이번 조사 범위(1차 특허 2건)에서는 "종류가 다양하다"와 "선택은 공정 의존적이다"까지만
   확인, 순위 비교 데이터는 확보 못함(**미검증**, Lv1-2 또는 Lv3-1 CFD 리뷰 후보).
2. Kim et al.(2020), *Wear*, DOI: 10.1016/j.mee.2020.111437 — circular vs circular+radial
   그루브의 CFD 비교 연구가 존재한다는 사실은 부모 노트([[pad-structure-groove-subpad]])에서
   이미 확인했으나 본문은 유료(OA 미확보, `find_open_access.py --title`로도 무료 사본 없음
   확인) — **2차 인용 이상으로 승격 못함**.
3. 폴리싱 **중**(분리 시점이 아니라) 그루브 형상이 국소 유체압 분포에 미치는 정량 효과는
   Thakurta(2001)의 윤활이론 프레임은 확보했으나 그루브 형상 파라미터(GSQ/GFQ)와 직접 연결한
   문헌은 이번 조사에서 찾지 못함 — Lv1-2(그루브 기하→유효 접촉면적·유동 저항)의 핵심 과제로 이관.

## 미검증 목록
- 슬러리 분배/배출 기능에 대한 EP0806267A1의 정성적 개선 주장 — 대조군 정량 데이터 없음.
- 그루브 종류별(동심원/나선/십자형/육각형) 성능 순위 — 확보한 1차 문헌 범위 밖.
- Kim et al.(2020) CFD 비교 결과 본문 수치 — 페이월, 초록만 확인(2차 인용 상태 유지).
- GSQ "가장 적합" 구간과 T=1300μm(배경 서술값) 사이의 완전한 일치 — 출처 문맥 불일치로 확인 불가.
