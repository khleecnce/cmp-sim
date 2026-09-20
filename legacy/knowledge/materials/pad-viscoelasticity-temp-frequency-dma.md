<!-- V2-SECTION: R1-equipment | 공동: R3-pad | 분배완료 2026-09-08 | 근거: 마찰, 온도 | 정본: ARCHITECTURE-V2.md §3 -->
# CMP 패드 점탄성 심화 — 온도·주파수 의존 E'·E''·tanδ와 CMP 조건 매핑 (Lv2-1)

> pad-material Lv2-1 | 작성일: 2026-09-07
> 선행: [[pad-viscoelasticity-dma]](E'/E''/tanδ 정의·Maxwell 모델), [[hertz-gw-contact-mechanics]](E*가
> 접촉강성·실접촉면적을 정하는 방식), [[pu-pad-chemistry-prepolymer-foam]](하드/소프트 세그먼트 조성),
> [[pad-hardness-porosity-measurement-methods]](IC1000/IC1010 Shore D 60 스펙). 형제 노트
> [[pad-structure-groove-subpad]], [[gw-nominal-vs-local-pressure]]와도 연결.
> 이 노트의 질문: **패드 E'는 온도·주파수에 따라 얼마나 변하고, 그 변화가 CMP 실온도·마찰 주파수
> 대역에서 접촉강성·MRR에 어떤 크기로 작용하는가.**

## 1. 문제 설정 — 왜 "상온 1 Hz E'" 하나로는 부족한가

[[pad-viscoelasticity-dma]]는 E'(저장), E''(손실), tanδ=E''/E'의 정의와 단일 Maxwell 요소의 주파수
거동을 다뤘다. 그런데 CMP 패드 PU는 **유리전이(Tg)가 CMP 공정 온도 바로 위**에 놓이는 재료가
많다(§3). Tg 근방에서는 E'가 수십 °C 구간에 걸쳐 1~2자릿수 떨어지고 tanδ가 피크를 이루므로,
공정 중 패드가 마찰열로 몇 °C만 더워져도 접촉강성이 크게 달라진다. 이 노트는 그 크기를
문헌값으로 고정하고, 시간-온도 중첩(TTS, WLF식)으로 "온도 변화 = 주파수 변화"라는 등가성을
정리한 뒤, [[hertz-gw-contact-mechanics]]의 E*→실접촉면적 관계에 연결한다.

## 2. 시간-온도 중첩(TTS)과 WLF 식

고분자의 완화시간 τ는 온도가 오르면 짧아진다. 온도 T에서 측정한 E'(ω)를 기준온도 T_r의 곡선에
겹치려면 주파수 축을 shift factor a_T만큼 옮긴다: E'(ω, T) = E'(ω·a_T, T_r) (밀도보정 b_T 생략).
Williams–Landel–Ferry는 Tg 이상 ~Tg+100 K 구간에서 a_T가 다음 경험식을 따른다고 보였다:

```
log10 a_T = −C1·(T − T_r) / (C2 + T − T_r)
```

**출처(1차)**: M. L. Williams, R. F. Landel, J. D. Ferry, "The Temperature Dependence of Relaxation
Mechanisms in Amorphous Polymers and Other Glass-forming Liquids," *J. Am. Chem. Soc.* 77(14),
3701–3707 (1955). https://doi.org/10.1021/ja01619a008 — Crossref로 제목·권·페이지 실존 확인. 원문 PDF는
유료(ACS)라 **초록만 확인**: T_r = Tg로 잡으면 "log a_T = 17.44(T−Tg)/(51.6+T−Tg)" 꼴의 **보편상수
C1 = 17.44, C2 = 51.6 K**가 다양한 고분자에 근사적으로 적용된다는 것이 초록의 핵심 주장이다.
**2차 출처**: Wikipedia "Williams–Landel–Ferry equation"(raw 위키텍스트 확인) — T_r = Tg일 때
C1≈17.44, C2≈51.6 K, T_r = Tg+50 K일 때 C1≈8.86, C2≈101.6 K, 그리고 "보편상수는 실제로는 보편적이지
않으니 관심 온도 구간에서 직접 피팅하라"는 경고.

두 상수쌍은 독립 데이터가 아니라 **기준온도 이동에 따른 재매개화**다. 기준온도를 ΔT만큼 올리면
C1' = C1·C2/(C2+ΔT), C2' = C2+ΔT가 되어야 한다. 아래 verify에서 17.44/51.6 → 8.86/101.6 재현을 확인한다.

### 2.1 Arrhenius 대안과 적용 한계
Tg **아래**(유리질) 또는 2차 전이(β 완화)에는 WLF가 아니라 Arrhenius형 log a_T = (E_a/2.303R)(1/T − 1/T_r)이
쓰인다. CMP 패드의 25~30 °C 구간은 §3 문헌의 Tg(43~56 °C)보다 낮으므로 **WLF를 그대로 적용하면
안 되는 온도대**다 — 이 노트는 WLF를 Tg 이상(≥ 45 °C) 구간 예시에만 쓴다.

**보편상수의 실제 한계 (1차, OA)**: N. Billon, C. E. Federico, G. Rival, J. L. Bouvard, A. Burr (2023, Crossref 저자순 확인), "Time–Temperature Superposition Principle in
Shearing Tests Compared to Tension Conditions for Polymers Close to Glass Transition," *Int. J. Mol.
Sci.* 24(4), 3944. https://doi.org/10.3390/ijms24043944 (PMC9962352, Europe PMC 전문 확인). Table 1:
T_r = 130 °C에서 PMMA(인장) C1 = 4.5~8.8, C2 = 52~68 K; PEI C1 = 10.2, C2 = 44 K; PEKK C1 = 21.7,
C2 = 91 K — 그리고 **같은 재료라도 인장과 전단에서 C1, C2가 다르다**(PMMA 80k: 인장 4.5/66.3 vs
전단 6.6/87.9). CMP 패드 E'를 TTS로 외삽하려면 CMP 하중 모드(압축)에서 피팅한 상수가 필요하며,
그런 CMP 패드 전용 WLF 상수는 이 조사에서 **확보하지 못했다(미검증)**.

## 3. 문헌 E'(T) 데이터 — CMP 패드 PU의 Tg는 공정온도 바로 위에 있다

### 3.1 Cabot(현 CMC Materials) 특허 Table 1B — 정량 표
**출처(1차, 특허)**: Cabot Microelectronics, "Polyurethane CMP pads having a high modulus ratio,"
US20170087688A1 (출원 2016-09-23, 공개 2017-03-30; 등록 US10562149). 전문은
freepatentsonline.com/y2017/0087688.html에서 확인(Google Patents·USPTO PDF는 이미지/차단).
DMA 조건: TA Q800, 인장 모드 multi-frequency controlled strain, **1 Hz**, 진폭 30 µm, 5 °C/min,
0→120 °C, 시편 6×30 mm. "DMA transition temp"는 tanδ 최대 온도.

| 패드 | Tg(DSC) °C | tanδ 피크 °C (1 Hz) | 신율 % | E'(25) MPa | E'(50) MPa | E'(80) MPa | Shore D |
|---|---|---|---|---|---|---|---|
| 1A (TPU, 발명) | 43.4 | 60.8 | 259 | 2127 | 215 | 5 | 77.2 |
| 1B | 44.0 | 60.3 | 292 | 1725 | 204 | 5 | 77.8 |
| 1C | 44.5 | 60.3 | 312 | 1413 | 276 | 5 | 76.4 |
| 1D | 43.6 | 59.9 | 194 | 1590 | 317 | 5 | 76.9 |
| 1E | 45.5 | 66.8 | 318 | 1474 | 441 | 8 | 80.1 |
| Control (Epic D100, 상용) | (미기재) | 56 | 350 | 1000 | 141 | 19 | 72 |

읽는 법:
- **25→50 °C 사이에 E'가 3~10배 떨어진다** — 상용 대조군 D100도 1000→141 MPa(7.1배). Tg(DSC)
  43~46 °C, tanδ 피크 56~67 °C가 이 구간에 걸쳐 있기 때문이다. 즉 "CMP 온도 30~60 °C"는 이들
  패드에서 정확히 **유리전이 구간**이다.
- **tanδ 피크(1 Hz DMA)가 DSC Tg보다 16~21 °C 높다**(1A~1E). DMA 전이는 주파수 의존이므로 1 Hz
  측정이 정적 열분석(DSC)보다 높게 나오는 것은 TTS와 방향이 맞는다(원인 배분 — 주파수 효과 대
  측정법 정의 차이 — 은 이 특허로는 분리 못함, 추정).
- 특허 초록의 청구 "E'(25)/E'(80) ≥ 50" 은 대조군 D100(1000/19 = 52.6)도 만족한다. 대조군을 실제로
  배제하는 조건은 부가 청구인 **E'(25) ≥ 1200 MPa 그리고 E'(80) ≤ 15 MPa**(D100: 1000, 19 → 둘 다
  탈락)이다 — 아래 verify에서 확인. (Google Patents 스니펫엔 "≥30" 문구도 보이나 원문 대조 못함,
  미검증.)

### 3.2 Kim et al. 2006 — 열경화 PU 패드 E'(T) (2차 인용)
Kim, Seo, Lee, "Temperature effects of pad conditioning process on oxide CMP: Polishing pad, slurry
characteristics, and surface reactions," *Microelectron. Eng.* 83, 362–370 (2006).
https://doi.org/10.1016/j.mee.2005.10.004 — Crossref 실존 확인, **원문·초록 미확보(유료, OA/미러 없음)**.
아래 수치는 OA 리뷰 문단을 통한 **2차 인용**: Kim et al.의 PU 패드 E'는 **20 °C 약 35 MPa → 90 °C
약 10 MPa**, 70 °C까지 거의 선형 감소 후 포화.
**2차 출처(1차 OA)**: "Process Temperature Control for Low Dishing in CMP," *Materials* 18(19), 4461
(2025). https://doi.org/10.3390/ma18194461 (PMC12525981, Europe PMC 전문 확인, 서론 ref.[11] 문단).

같은 "PU CMP 패드"인데 Cabot TPU(25 °C 1000~2100 MPa, 25→80 °C 비 50~425)와 Kim 2006(20 °C 35 MPa,
20→90 °C 비 3.5)은 **E' 절대값이 30~60배, 온도비가 1~2자릿수 다르다**. 측정 모드(인장 vs 압축/전단),
발포체 vs 고형체, 열경화 IC1000류 vs 열가소성 TPU 차이가 후보이나 Kim 원문을 못 봐 **원인 미상**
— 이 노트에서 "PU 패드 E'는 X MPa"라고 단일값으로 쓸 수 없는 이유다.

### 3.3 IC1000 관련 DMA 문헌 — 초록/스니펫만 확보
- H. Lu, Y. Obeng, K. Richardson, "Applicability of dynamic mechanical analysis for CMP polyurethane
  pad studies," *Mater. Charact.* 49(2), 177–186 (2002). https://doi.org/10.1016/s1044-5803(03)00004-4
  — UCF STARS 리포지토리 landing(초록)만 확인, PDF 없음. 초록: IC1000/Suba IV 적층 패드의 tanδ 곡선에
  **다중 전이**(각 층 성분에 대응)가 나타나고, 적층 유효 E'는 개별 층 탄성과 상관; 사용 후 물성
  변화는 화학적 개질보다 **in situ 기계적 개질**이 지배. 정량값 없음.
- L. Charns, M. Sugiyama, A. Philipossian, "Mechanical properties of chemical mechanical polishing
  pads containing water-soluble particles," *Thin Solid Films* 485(1–2), 188–193 (2005).
  https://doi.org/10.1016/j.tsf.2005.03.023 — 검색 스니펫만: WSP 함유 패드는 Tg가 "표준 CMP 운전온도
  20~40 °C" 안에 있고, IC-1000은 E' 감소 기울기가 완만해 가교밀도가 더 높다고 서술. **1차 미확보**.

즉 IC1000 자체의 E'(T)·tanδ(T) 숫자표는 이 조사에서 **확보 못함(미검증)**. Lv1-2 스펙(Shore D 60,
[[pad-hardness-porosity-measurement-methods]] §1)만 확정값이다.

## 4. E'(T) 변화가 CMP 성능에 주는 영향 — Khanna 2019

**출처(1차, OA CC-BY-NC-ND)**: A. J. Khanna et al., "Impact of Pad Material Properties on CMP
Performance for Sub-10 nm Technologies," *ECS J. Solid State Sci. Technol.* 8(5), P3063–P3068 (2019; Crossref 기준 — Materials 2025 참조목록은 –P3070로 표기).
https://doi.org/10.1149/2.0121905jss (IOPscience HTML 전문 확인; PDF는 봇 차단으로 미저장).

- 실험 패드 1·3(설계 동일, E'(T)만 다름)과 업계 표준 참조 패드 2. **E'25/E'90 비**: 패드1 = 188,
  패드2 ≈ 4, 패드3 = 21 (Fig.5; "E'30/E'90도 정수 단위로 유사").
- 산화막 제거율을 **연속 90 s 폴리시(R90s×1)** 대 **15 s×6회(R15s×6)** 로 비교: 패드1 R90/R15 ≈ 2
  ("∼2x"), 패드2 ≈ 1, 패드3 ≈ 1.45(본문 그림 판독 요약치). 패드1은 90 s 내내 패드 온도가 계속 오르고,
  패드2는 온도·마찰이 ~45 s에 포화(시작 ~25 °C, 종단 온도 수치 미기재).
- 결론: 폴리시가 길어지면 온도↑ → E'↓ → MRR↑·평탄화효율(PE)↓. **E'의 온도 민감도(비율)가 클수록
  MRR 시간 드리프트가 크다.** 비율을 줄이면 공정시간 의존성을 억제할 수 있다.

메커니즘 연결([[hertz-gw-contact-mechanics]] §4 지수분포 GW 결과 A_r/W = 상수/E*): 명목하중이 같을 때
**실접촉면적 A_r ∝ 1/E***. E'가 25→50 °C에 7배 떨어지면(D100, §3.1) 모델상 A_r은 7배까지 커질 수
있다 — 이는 GW 모델이 **함의**하는 값이지 측정값이 아니다(추정). Preston K_p 안에 숨은 A_r/A_n이
온도의 함수가 된다는 뜻이며, 이것이 Khanna의 "E'비 ↑ → MRR 드리프트 ↑"의 물리적 경로다.
Hertz 단일 asperity 강성 k ∝ E*^(2/3)([[hertz-gw-contact-mechanics]] §2)도 같은 방향.
[[gw-nominal-vs-local-pressure]]가 "P 상수 → 국소압력 p_r 거의 불변, 접촉 개수 n만 변화"라 정리한
결과와 합치면, 온도 상승은 p_r보다 **n·A_r**을 키우는 쪽으로 작용한다(추정).

리바운드: tanδ가 큰 전이 구간에서는 압축 후 회복이 느려(손실 큼) asperity가 다음 접촉 전까지
완전히 되돌아오지 못한다 — 순환 하중에서 실접촉면적이 누적 증가한다는 2024년 보고가 있으나
(ResearchGate 초록 스니펫 "Effect of Viscoelastic Characteristics on the Real Contact Area of
Polishing Pad Surface", 출판지·DOI 미확인) 정량값은 **확보 못함**. Lv1-1 부모노트의 크리프 τ 미검증
항목과 동일 계열의 공백이다.

## 5. CMP 하중 주파수 대역 — 추정
CMP 패드가 받는 주기 하중은 두 스케일이다(모두 **이 노트의 추정치**, 문헌 직접 측정값 아님):
- 거시: 웨이퍼/플래튼 회전. Cabot 특허 레시피 플래튼 93 rpm·70 rpm → 1.55 Hz·1.17 Hz. DMA 표준
  1 Hz와 같은 자릿수 → §3.1 표의 E'(T)는 **거시 하중 주파수에는 그대로 적용 가능**.
- 미시: asperity 하나가 웨이퍼를 스치는 시간. 상대속도 ≈1.26 m/s([[cmp-kinematics-rotary]]
  Rs=1 해석해), asperity 반경 30 µm(Vasilev et al. 2011, https://doi.org/10.1109/TSM.2011.2107756,
  papers/vasilev2011-gw-pattern-density-size-cmp.pdf GW 파라미터표) → 접촉폭 ~2R = 60 µm 기준
  f ≈ v/2R ≈ 2×10⁴ Hz. 1 Hz DMA보다 **4자릿수 높다**.
TTS로 환산하면 "고주파 = 저온"이므로, asperity 스케일에서 패드는 1 Hz DMA가 보여주는 것보다
**더 유리질(더 단단하고 tanδ 낮음)**로 응답할 가능성이 있다. 이 환산의 정량화(CMP PU의 WLF 상수)가
없으므로 방향만 기록한다(미검증).

## 6. 정량 재현 — 문헌값 상수 박고 코드로 대조

```python verify
# ── (1) WLF 보편상수의 기준온도 재매개화: Tr=Tg (17.44, 51.6 K) → Tr=Tg+50 K 는 (8.86, 101.6 K)여야 한다
#     출처: Williams-Landel-Ferry 1955, JACS 77, 3701 (doi:10.1021/ja01619a008) 초록; Wikipedia WLF 문서
C1_Tg, C2_Tg = 17.44, 51.6          # Tr = Tg
C1_lit50, C2_lit50 = 8.86, 101.6    # Tr = Tg + 50 K (문헌 제시값)
dT = 50.0
C1_calc = C1_Tg * C2_Tg / (C2_Tg + dT)
C2_calc = C2_Tg + dT
assert abs(C1_calc - C1_lit50) < 0.01, f"C1 재매개화 불일치: {C1_calc:.3f} vs {C1_lit50}"
assert abs(C2_calc - C2_lit50) < 1e-9, f"C2 재매개화 불일치: {C2_calc} vs {C2_lit50}"

def log_aT(T, Tr, C1, C2):
    return -C1 * (T - Tr) / (C2 + (T - Tr))

# 두 매개화가 임의 온도에서 같은 상대 shift를 주는지 (항등식 수치 확인)
Tg = 0.0
for T in (Tg + 60, Tg + 80, Tg + 100):
    lhs = log_aT(T, Tg, C1_Tg, C2_Tg) - log_aT(Tg + 50, Tg, C1_Tg, C2_Tg)
    rhs = log_aT(T, Tg + 50, C1_calc, C2_calc)
    assert abs(lhs - rhs) < 1e-9, f"shift 항등식 실패 T=Tg+{T}: {lhs} vs {rhs}"

# CMP 예시(추정, 보편상수 — CMP PU 전용 상수 아님): Cabot 1D Tg(DSC)=43.6°C, 폴리시 온도 60°C
Tg_1D = 43.6
la = log_aT(60.0, Tg_1D, C1_Tg, C2_Tg)
assert -4.3 < la < -4.1, f"log aT(60°C, Tg=43.6°C) = {la:.3f} — 기대 -4.2 부근"
print(f"(1) WLF: C1'={C1_calc:.3f} (문헌 8.86), C2'={C2_calc} K (문헌 101.6 K); "
      f"60°C vs Tg: log aT={la:.2f} → 완화 {10**(-la):.0f}배 가속(보편상수 가정)")

# ── (2) Cabot US20170087688A1 Table 1B — E'(25)/E'(80) 비 및 청구 조건 대조
pads = {  # Tg_DSC, tanδ피크, 신율%, E25, E50, E80, ShoreD
    "1A": (43.4, 60.8, 259, 2127, 215, 5, 77.2),
    "1B": (44.0, 60.3, 292, 1725, 204, 5, 77.8),
    "1C": (44.5, 60.3, 312, 1413, 276, 5, 76.4),
    "1D": (43.6, 59.9, 194, 1590, 317, 5, 76.9),
    "1E": (45.5, 66.8, 318, 1474, 441, 8, 80.1),
}
ctrl = (None, 56, 350, 1000, 141, 19, 72)   # Epic D100, Tg(DSC) 미기재
ratio_ctrl = ctrl[3] / ctrl[5]
assert abs(ratio_ctrl - 52.6) < 0.1, f"D100 E'25/E'80 = {ratio_ctrl:.1f}"
assert ratio_ctrl >= 50, "대조군도 '비 ≥50' 조건을 만족해야 함(초록 조건만으론 대조군 미배제)"
assert not (ctrl[3] >= 1200 and ctrl[5] <= 15), "대조군은 E'25≥1200 & E'80≤15 부가조건에서 탈락해야 함"
for name, (tg, tand, el, e25, e50, e80, sd) in pads.items():
    r = e25 / e80
    assert r >= 50 and e25 >= 1200 and e80 <= 15, f"{name} 청구조건 불충족: r={r:.0f}, E25={e25}, E80={e80}"
    assert 3.0 <= e25 / e50 <= 10.5, f"{name} 25→50°C E' 감소배수 {e25/e50:.1f} — 3~10배 범위 밖"
    gap = tand - tg
    assert 15.0 <= gap <= 22.0, f"{name} tanδ피크-Tg(DSC) = {gap:.1f}°C — 16~21°C 범위 밖"
drop_ctrl = ctrl[3] / ctrl[4]
assert abs(drop_ctrl - 7.09) < 0.02, f"D100 25→50°C 감소배수 {drop_ctrl:.2f}"
print(f"(2) Cabot: D100 E'25/E'80={ratio_ctrl:.1f}(≥50이나 부가조건 탈락), 25→50°C 감소 {drop_ctrl:.1f}배; "
      f"발명패드 비 {min(p[3]/p[5] for p in pads.values()):.0f}~{max(p[3]/p[5] for p in pads.values()):.0f}")

# ── (3) Khanna 2019 (doi:10.1149/2.0121905jss): E'25/E'90 비가 클수록 R90s/R15s(MRR 드리프트)가 큰가 — 순서 일치 검사
e_ratio  = {"pad1": 188, "pad2": 4, "pad3": 21}
rr_ratio = {"pad1": 2.0, "pad2": 1.0, "pad3": 1.45}   # 본문 "∼2x", "∼1", 그림 판독 1.45
order_e  = sorted(e_ratio,  key=e_ratio.get)
order_rr = sorted(rr_ratio, key=rr_ratio.get)
assert order_e == order_rr == ["pad2", "pad3", "pad1"], f"순서 불일치: E' {order_e} vs RR {order_rr}"

# ── (4) Kim 2006 (2차 인용, Materials 2025 doi:10.3390/ma18194461 서론): 35 MPa@20°C → 10 MPa@90°C
kim_ratio = 35.0 / 10.0
assert abs(kim_ratio - 3.5) < 1e-9
assert ratio_ctrl / kim_ratio > 10, "Cabot D100(25→80°C)과 Kim(20→90°C) 온도비가 10배 이상 다름 — 원인 미상으로 기록"
print(f"(3) Khanna 순서 일치 {order_e}; (4) Kim 2006 E' 비 {kim_ratio}, Cabot D100 비 {ratio_ctrl:.1f} → "
      f"{ratio_ctrl/kim_ratio:.0f}배 차이(패드 종류/측정모드 차이 추정, 원문 미확보)")

# ── (5) 주파수 대역 추정(문헌 측정값 아님): 플래튼 rpm→Hz, asperity 통과 주파수 v/2R
for rpm, hz in ((93, 1.55), (70, 1.17)):
    assert abs(rpm / 60 - hz) < 0.01
v, R = 1.256637, 30e-6            # m/s (cmp-kinematics-rotary Rs=1), m (Vasilev 2011 GW 표)
f_asp = v / (2 * R)
assert 1.5e4 < f_asp < 2.5e4, f"asperity 통과 주파수 {f_asp:.0f} Hz — 2e4 Hz 오더 기대"
print(f"(5) 거시 1.2~1.6 Hz, 미시 {f_asp:.0f} Hz ≈ 1 Hz DMA 대비 {f_asp:.0e}배 (추정)")
```

재현 결과 요약(문헌값 대조):
- WLF 재매개화: 계산 C1' = 8.857 vs 문헌값 8.86 (0.03% 차이), C2' = 101.6 K 정확 일치 → 두 "보편상수
  쌍"은 하나의 식의 두 표기임을 확인. 60 °C에서 Tg(43.6 °C) 대비 log a_T ≈ −4.2(완화 ~1.6×10⁴배 가속)
  는 보편상수 가정치라 CMP PU 실측과의 대조는 **미검증**.
- Cabot Table 1B: D100의 E'25/E'80 = 52.6(≥ 50) 재현 — 초록의 비율 조건만으로는 대조군이 배제되지
  않고, E'(25) ≥ 1200 MPa·E'(80) ≤ 15 MPa 부가조건에서 탈락함을 확인. 발명패드 5종 모두 25→50 °C
  E' 3~10배 감소, tanδ 피크가 DSC Tg보다 16~21 °C 높음(1 Hz).
- Khanna 2019: E'비 순서(4 < 21 < 188)와 MRR 드리프트 순서(1.0 < 1.45 < 2.0) 일치(3점 순위 검사 —
  통계적 유의성은 없음, 방향성 확인 수준).
- Kim 2006 대 Cabot D100: 온도비 3.5 vs 52.6 — **불일치(15배)**. 문헌 두 편이 다른 재료·측정을 보고한
  것으로 보이나 Kim 원문 미확보로 원인 미상. 일치하는 척 맞추지 않는다.

## 7. 결론 — pad-material 관점 정리
1. CMP 패드 TPU/PU의 Tg(DSC 43~56 °C, tanδ 피크 56~67 °C @1 Hz)는 CMP 공정온도 대역 위에 걸쳐 있고,
   **25→50 °C에 E'가 3~10배** 떨어진다(Cabot 특허 6종). 상온 데이터시트 값 하나로 접촉강성을 고정하면
   폴리시 중 온도 상승분을 놓친다.
2. E'의 온도 민감도(E'저온/E'고온 비)는 **MRR의 시간 드리프트와 PE 저하의 직접 원인**(Khanna 2019).
   물리 경로는 GW의 A_r ∝ 1/E*: 온도↑ → E'↓ → 실접촉면적↑ → K_p 유효값↑.
3. 온도 효과는 TTS로 주파수 효과와 맞바꿀 수 있지만, CMP 패드 전용 WLF 상수와 asperity 스케일
   (~10⁴ Hz) 주파수의 실측은 없다. 이 두 공백이 다음 정량화의 병목이다.
4. 실제 공정온도: Materials 2025의 Cu CMP는 비제어 시 30 → 36 °C 이상으로 상승, 제어 시 30 °C 유지;
   Khanna는 25 °C 시작·90 s까지 상승. "30~60 °C"의 상단 60 °C는 이번 조사 문헌에선 직접 확인 못함(미검증).

## 미검증 목록
- CMP 패드(IC1000/IC1010) 자체의 E'(T)·tanδ(T) 수치표 — Lu 2002·Charns 2005는 초록/스니펫만
- CMP PU 전용 WLF(C1, C2) 또는 Arrhenius E_a — 보편상수(17.44/51.6)는 대용, 압축 모드 피팅 없음
- Kim 2006 E'(35→10 MPa)의 측정 모드·패드 종류 — 원문 미확보, Cabot 값과 15배 불일치 원인 미상
- Cabot 특허 "≥30" 비율 문구(Google Patents 스니펫) — 원문 대조 못함
- 온도↑ → A_r 7배(GW 함의)는 모델 추정, 실측 대조 없음; 순환하중 리바운드 지연의 정량값 없음
- asperity 통과 주파수 ~2×10⁴ Hz는 v/2R 추정, 실측 없음
- Lv1-2에서 미룬 Gibson–Ashby(E*/Es vs 상대밀도) 원문 확보 — 이번 단원 범위(온도·주파수) 밖으로
  남김, 여전히 미확보

## 다음 단원
Lv2-2 기공 구조와 슬러리 보유·이송: 기공률-MRR 관계. 이번 노트의 E'(T)와 [[pad-hardness-porosity-measurement-methods]] §6
Gibson–Ashby를 결합해 "기공률·온도 → 유효 E*"를 만드는 것은 Lv3-2(GW 유효 강성 정량모델)로 이월.
