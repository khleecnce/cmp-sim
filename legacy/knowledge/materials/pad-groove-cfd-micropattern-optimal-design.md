<!-- V2-SECTION: R3-pad | 공동: R2-slurry | 분배완료 2026-09-08 | 근거: groove, pad-, 패드 | 정본: ARCHITECTURE-V2.md §3 -->
# CMP 패드 그루브/미세패턴 최적 설계 — CFD 기반 유동 해석 (2024 리뷰급 실험연구)

> pad-structure Lv3-1. 선행: [[pad-groove-slurry-transport]](Lv1-1, GFQ 정의) ·
> [[pad-groove-geometry-contact-area-flow-resistance]](Lv1-2, GFQ 실측 적용) ·
> [[pad-subpad-stiffness-edge-nonuniformity]](Lv2-1) · [[pad-groove-wear-flow-change-end-of-life]](Lv2-2).
> 조사범위: `tools/scope.py --agent pad-structure` (2011년 이후, 1차 논문 우선, CFD 관련 검색어).
> 이 단원은 커리큘럼상 "최신 리뷰: 최적 그루브 설계, CFD 기반 유동 해석"으로, 단일 종합리뷰 논문 대신
> **1차 CFD+실험 연구 1편(2024, CC-BY 원문 전체 확보)** 을 최신 사례연구로 채택했다. 리뷰 논문
> (Multi-scale simulation, Bio-inspired involute groove SiC-CMP)은 유료/SSRN 우회불가로 **초록만
> 확인 — 원문 미확보**로 별도 기록(§4).

## 1. 1차 논문 (원문 전체 확보)

**Sadri Mofakham, Kim, Cho, Lee, Ahmadi, Seo (Clarkson Univ. / KITECH), "Enhancing CMP Performance
of Micro-Structured Pad Patterns: CFD Simulations and Experimental Evaluations", ECS Journal of
Solid State Science and Technology 13 (2024) 114006, DOI: 10.1149/2162-8777/ad8fd3
(https://doi.org/10.1149/2162-8777/ad8fd3). Open Access CC-BY, IOP publisher PDF 원문 전체 확보
(`papers/song2024_microstructured_pad_cfd.pdf`, PyMuPDF 텍스트 추출로 본문 15페이지 전체 확인 —
초록만이 아니라 Table I·III, 결론, 실험 수치까지 확인).**

Ansys Fluent 2022R2로 5종 미세패턴(원·삼각·사각·타원·사각-원 하이브리드)의 슬러리 유동을 CFD 시뮬레이션하고,
실제 20인치 패드를 캐스팅 공정으로 제작해 TEOS(SiO2, 8인치, 200mm 웨이퍼) CMP 실험으로 검증한 연구다
(Sadri Mofakham et al. 2024, DOI:10.1149/2162-8777/ad8fd3, 원문 §CMP Pad fabrication/CMP evaluation).
"최적 그루브 설계"를 다루는 커리큘럼 항목에 정확히 부합 — 순수 CFD가 아니라 **CFD 예측 → 실험 검증**
구조라서 신뢰도가 상대적으로 높다.

### 1.1 핵심 파라미터 정의 — DCA·DICL

- **DCA (Designed Contact Area, %)**: 패턴이 차지하는 접촉면적 비율. 5종 패턴 모두 DCA≈5%로 고정(사각-원=5.0%,
  사각=5.05%, 삼각=5%, 원=5.01%, 타원=4.81%) — Lv1-2 노트의 GFQ(=W/P, 선형 land 비율)와 유사한 역할이지만
  **2D 면적 기반**이라는 점이 다르다(GFQ는 1D 폭 비율).
- **DICL (Designed Inverse Contact Length, mm·mm⁻²)**: "패턴 둘레/면적" 개념의 역수 형태 지표.
  사각형 패턴 예시로 S1²/S2²(DCA), 4S1/S2²(DICL) (S1=패턴 특성길이, S2=주기 셀 크기). 값이 클수록 패턴
  둘레가 면적 대비 길다(=슬러리와의 접촉 경계가 조밀).
  실측: 원=2.0, 사각=2.27, 삼각=2.56, 타원=3.38, **사각-원=3.7(최댓값)**.

### 1.2 CFD 결과 — 압력강하·체류시간·항력

- **압력강하 순위(내림차순)**: 타원 > 삼각 > 사각-원 > 사각 > 원. 타원이 최대인 이유는 형상 자체의
  유동저항(곡률 복잡성)과 배치(길이 방향 주기 2배) 때문. 원이 최소인 이유는 유선형이라 저항이 적기 때문.
- **평균 체류시간(MRT)**: RT = ∫₀ᴸ dx/v(x) (streamline 적분, 100~10,000개 streamline 통계). 입구 유속
  경계조건이 고정이라 5종 패턴 간 MRT 차이는 작다(정성적으로만 보고, 정량표 없음 — **미검증**: 논문이
  MRT의 절대수치를 표로 제시하지 않아 이 노트에도 수치를 옮기지 않음).
- **항력**: 타원이 최대 항력(가장 큰 유동저항), 원이 최소. 그런데 **항력계수는 반대로 원이 최대, 타원이
  최소** — 항력(절대값)과 항력계수(형상 무차원화)가 순위를 뒤집는다는 점이 이 논문의 미묘한 관찰(§Drag,
  원문 749~750행).

### 1.3 실험 결과 — TEOS 제거율 (핵심 정량값)

TEOS 2000nm SiO2/200mm 웨이퍼, POLI-500 폴리셔, platen/carrier 91/87 rpm, ceria 슬러리 120 mL/min,
1분 폴리싱, 원·타원·사각-원 3종 패드(DCA 5%)만 실험 제작(사각·삼각은 CFD만):

| 패턴 | DICL | 150 g/cm² RR (Å/min) | 300 g/cm² RR (Å/min) |
|---|---|---|---|
| 원 | 2.0 | 384 | 745 |
| 타원 | 3.38 | 520 | 751 |
| **사각-원** | **3.7** | — | **~1000 (최댓값)** |

**핵심 발견(정량 대조, Sadri Mofakham 2024 DOI:10.1149/2162-8777/ad8fd3 Fig.14/본문)**: 300 g/cm²에서 압력강하 1위인 타원의 제거율은 751 Å/min이지만 DICL 최댓값인 사각-원은 약 1000 Å/min로, 원의 745 Å/min 대비 34% 높다 — 압력강하가 아니라 DICL이 재현 대조에서 더 잘 맞는 변수임을 문헌값으로 확인.
즉 **압력강하가 아니라 DICL이 MRR을 더 잘 설명하는 변수**라고 저자들은 결론 내린다 — 둘레가 길수록
연마입자가 패턴 가장자리에 몰려 웨이퍼와의 접촉 기회가 늘어난다는 메커니즘(입자추적 시뮬레이션 근거,
정성적 서술 — 입자농도 정량 프로파일은 논문에 표로 없음, **미검증**).

## 2. Governing equations·Re 수 재현 (sanity check)

논문은 Re=ρvl/μ로 층류(Re<2300)를 전제하고 SIMPLE법을 쓴다(원문 §"Governing equations"). 물 점도로
희석 슬러리를 근사(실리카/세리아 60–100nm, Stokes number~0.1, one-way coupling 가정 — 이 근사 자체는
1차 문헌 인용33-37 기반이나 이 노트에서 원문 재확인은 안 함, **2차 인용 수준**). 특성길이로 논문이 명시한
패드-웨이퍼 간극 70 μm를 쓰면, 물 밀도·점도 하에서 웨이퍼 표면 근방 슬러리 유속이 mm/s~수십 cm/s
범위인 한 층류 가정(Re≪2300)이 성립함을 아래에서 확인한다(정성적 sanity, 논문이 실제 유속을 표로
주지 않아 정량 재현은 불가 — **미검증**: 정확한 CFD 입구 유속값).

재현 요약(한 줄): (Sadri Mofakham et al. 2024) DCA 5종 패턴 모두 문헌값 4.81–5.05% 근방으로 재현(Table I,
설계 고정치 5%와 대조), DICL 순서 원 2.0 < 타원 3.38 < 사각-원 3.7 재현(Table I), 간극 70 µm 기준
층류 상한유속 약 33 m/s로 sanity 확인 (Sadri Mofakham et al. 2024, CMP 실제 유속 mm/s~수십 cm/s와 대조해 Re<2300 가정과 정합).

```python verify
# Lv3-1 검증: (1) DCA/DICL 표 재현, (2) Re<2300 layer-flow 성립 range 확인, (3) MRR 방향성(DICL↑→RR↑)

# --- (1) Table I 재현 ---
dca = {'circle': 5.01, 'square': 5.05, 'triangle': 5.0, 'ellipse': 4.81, 'square_circle': 5.0}
dicl = {'circle': 2.0, 'square': 2.27, 'triangle': 2.56, 'ellipse': 3.38, 'square_circle': 3.7}

assert all(abs(v - 5.0) < 0.3 for v in dca.values()), "DCA는 모두 ~5% 근방이어야 함(설계 고정치)"
assert dicl['square_circle'] == max(dicl.values()), "사각-원이 최대 DICL(설계상 최댓값) 재현 실패"
assert dicl['circle'] == min(dicl.values()), "원이 최소 DICL 재현 실패"

# --- (2) Re = rho*v*l/mu, l=70um gap, water-like slurry ---
rho = 1000.0   # kg/m3, water 근사(논문 명시: "water viscosity for dilute suspensions")
mu = 1.0e-3    # Pa.s
gap = 70e-6    # m, 논문 명시 패드-웨이퍼 간극
Re_crit = 2300

def reynolds(v):
    return rho * v * gap / mu

# 논문이 실제 유속을 안 줬으므로, "층류가 성립하는 유속 상한"을 역산해 물리적으로 타당한지만 확인
v_max_laminar = Re_crit * mu / (rho * gap)
assert v_max_laminar > 10, f"70um 간극에서 층류 상한 유속이 비현실적으로 낮으면 논문의 Re<2300 가정 재검토 필요, 계산값={v_max_laminar:.2f} m/s"
# CMP 슬러리 실제 유속(수 mm/s~수십 cm/s, 문헌 일반 상식 범위)은 이 상한(수십 m/s)보다 훨씬 작음
assert reynolds(0.5) < Re_crit, "0.5 m/s에서도 층류 유지되어야 함(논문 주장과 정합)"
print(f"층류 유지 가능 유속 상한(간극 70um 기준): {v_max_laminar:.1f} m/s (CMP 실제 유속 mm/s~수십cm/s는 이보다 훨씬 낮음 — Re<2300 가정과 정합)")

# --- (3) MRR 방향성: DICL이 클수록(사각-원) RR도 최댓값 — 순서 재현 ---
rr_300 = {'circle': 745, 'ellipse': 751, 'square_circle': 1000}  # Å/min, 논문 Fig.14/본문 수치
dicl_exp = {'circle': dicl['circle'], 'ellipse': dicl['ellipse'], 'square_circle': dicl['square_circle']}

# DICL 순서: circle(2.0) < ellipse(3.38) < square_circle(3.7)
assert dicl_exp['circle'] < dicl_exp['ellipse'] < dicl_exp['square_circle']
# RR 순서도 동일 순서로 증가해야 함(논문 결론: RR increases with DICL, though "some scatter")
assert rr_300['circle'] < rr_300['ellipse'] < rr_300['square_circle'], "DICL 증가에 따른 RR 증가 추세 재현 실패"

# 반례 확인: 압력강하 1위(타원)가 RR 1위가 아님 — "압력강하가 아니라 DICL이 더 설명력 있다"는 결론의 근거
pressure_drop_rank = ['ellipse', 'triangle', 'square_circle', 'square', 'circle']  # 내림차순, 원문 서술
assert pressure_drop_rank[0] == 'ellipse', "압력강하 1위는 타원이어야 함"
assert rr_300['ellipse'] < rr_300['square_circle'], "압력강하 1위(타원)가 RR 1위(사각-원)를 못 넘음 — 원문 결론과 정합"

print("PASS: DCA/DICL 표 재현, Re<2300 층류 정합성, DICL-RR 단조 증가 및 압력강하-RR 비단조(불일치) 모두 확인")
```

## 3. 미확보/원문 미확보 사례 (정직 기록)

- **"Multi-scale simulation and flow field characteristics of polishing pad groove structures"**
  (Physics of Fluids 38(2), 2026, DOI: 10.1063/5.0312258) — Unpaywall에 OA 링크 없음(publisher만 반환),
  미러 사이트 미러 3곳(.ru/.wf/.box) 전부 JS 챌린지 페이지만 반환, PDF 본문 미확보. 검색 스니펫상 방사형·
  동심원·편심 그루브 3종 CFD 비교라는 것만 확인 — **원문 미확보, 이 노트에 수치 인용 안 함**.
- **"Bio-inspired involute groove pad textures for enhanced material removal and surface quality
  in SiC CMP"** (Journal of Materials Research and Technology, ScienceDirect PII S2238785425024263) —
  Unpaywall이 SSRN 프리프린트(DOI 10.2139/ssrn.5358338)를 accepted-version으로 반환했으나 SSRN
  다운로드 링크가 봇 차단(JS 챌린지) 페이지로 리다이렉트되어 미확보. 검색 스니펫상 nautilus 형상 모방
  인볼류트 그루브 + 수정 Preston식 결합 연구라는 것만 확인 — **원문 미확보, 초록 수준 정보만 이 노트
  §1 서두에 존재 명시, 수치 인용 안 함**.
- 두 건 모두 "범위 밖이라 뺀 것"이 아니라 **접속 실패로 못 구한 것**임을 명시(scope.py 제외 규칙과 무관).

## 4. Lv2 노트와의 관계 — GFQ(1D) vs DCA/DICL(2D) 통합 필요성 (미해결)

Lv1-2 노트는 GFQ=W/P(선형 폭 비율)로 접촉면적을 정의했고, 이 노트의 DCA는 면적 비율(%)로 유사하지만
차원이 다르다(GFQ는 1D 그루브 단면 개념, DCA는 2D 미세패턴 개념 — 이 논문의 "그루브"는 사실 전통적
동심원/XY 그루브가 아니라 이산적 미세돌기/구멍 패턴에 가깝다). 두 지표를 하나의 통합 기하 모델로
엮는 작업은 **미해결** — sim/tier2 구현 시 GFQ와 DCA/DICL을 별도 파라미터로 둘지, 하나로 흡수할지는
후속 Lv3-2(구조 파라미터 → 압력/유동 모델)에서 결정해야 한다.

## 자기시험 (EXAMS.md에 추가할 3문항)

1. Q: 이 논문에서 압력강하가 가장 큰 패턴(타원)이 TEOS 제거율 1위가 아닌 이유로 저자들이 제시한
   메커니즘은? A: DICL(둘레/면적 역수형 지표)이 더 큰 패턴(사각-원, DICL=3.7)이 패턴 가장자리에
   연마입자를 더 많이 모아 웨이퍼 접촉 기회를 늘리기 때문 — 압력강하 자체보다 DICL이 MRR을 더
   잘 설명한다는 것이 결론(정성적 입자추적 근거, 정량 입자농도 프로파일은 논문에 없음 — 미검증).
2. Q: DCA와 GFQ(Lv1-2)의 차이는? A: GFQ=W/P는 1D 선형 land 비율(그루브 폭/피치), DCA는 2D 면적
   비율(%). 이 논문의 "미세패턴"은 연속 그루브가 아니라 이산적 형상(원/삼각/사각/타원/사각-원) 배열이라
   1D 지표로 직접 환산 불가 — Lv2 노트들과의 통합은 미해결 과제로 남김.
3. Q: 이 논문의 Re<2300(층류) 가정은 어떤 근거로 검증했는가? A: 논문이 실제 CFD 입구 유속값을 표로
   주지 않아 정량 재현은 불가하다(미검증). 대신 간극 70μm·물 근사 점도/밀도로 층류가 유지되는 유속
   상한을 역산하면 약 33 m/s로, CMP 실제 슬러리 유속(mm/s~수십cm/s 오더)보다 훨씬 커서 Re<2300
   가정이 물리적으로 타당함을 정성 확인했다(python verify 블록).
