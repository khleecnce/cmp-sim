<!-- V2-SECTION: R4-disk | 분배완료 2026-09-08 | 근거: asperity-regeneration, conditioner, cut rate, cutrate, grit | 정본: ARCHITECTURE-V2.md §3 -->
# 그릿 밀도·돌출 높이 → 패드 절삭율(cut rate) 모델 (disk-design Lv1-2)

> disk-design Lv1-2. [[diamond-grit-mesh-bonding]] [[conditioner-disk-pad-cutting-model]]
> [[conditioning-mechanism-asperity-regeneration]] [[conditioner-grit-design-space]] 상호링크.
> Lv1-1이 그릿 규격·본딩 자체를 다뤘다면, 본 단원은 "그릿이 조밀할수록/돌출이 클수록 절삭율이
> 어떻게 바뀌는가"를 정량·수식 모델로 좁힌다.

## 1. 출처
1. Tyan Feng, "Pad Conditioning Density Distribution in CMP Process With Diamond Dresser,"
   IEEE Trans. Semicond. Manuf. 20(4), 464–475 (2007). DOI: 10.1109/TSM.2007.907618.
   **1차 원문 확보** — 유료(IEEE), 미러 사이트를 통해 PDF 확보(`papers/feng2007.pdf`,
   INDEX.json 등록). 컨디셔닝 밀도(conditioning density, CD)의 기구학적(kinematic) 모델을
   유도한 논문. **단, PDF 텍스트 추출 시 수식 자체(그리스 문자·아래첨자 포함 식 번호
   (3.6)~(3.28))가 이미지/벡터로 인코딩되어 OCR로 읽히지 않음 — 정성적 결론과 정의식
   구조는 확보했으나 정확한 폐형식 수식은 **미확보**로 명시한다.**
2. Doug Pysher, Brian Goers, John Zabasajja (3M), "Design, Characteristics and Performance
   of Diamond Pad Conditioners," Mater. Res. Soc. Symp. Proc. 1249-E02-04 (2010). 공개 PDF:
   https://multimedia.3m.com/mws/media/667824O/design-characteristics-performance-of-diamond-pad-conditioners.pdf
   — 산업 백서(피어리뷰 아님), 그릿 크기·형상·밀도·팁높이분포(tip height distribution)와
   패드 마모율(PWR)·표면조도 관계를 실측(1차 데이터 포함)으로 제시. 이미
   [[conditioner-disk-pad-cutting-model]] §3에서 PCR decay(50h→16%) 앵커로 일부 인용된
   동일 계열 저자군의 후속(2010, MRS) 논문 — 본 단원에서는 겹치지 않는 **깊이-of-penetration
   (DOP)·작동 그릿 비율(working diamond fraction)** 파트를 사용.
3. Raghava Kakireddy, Andrew Galpin, Joseph Smith (Entegris), David Slutz (Diamonex),
   "Effects of CMP Pad Conditioner Properties and Performance on Polishing Pad, Process and
   Wafer Removal Rate," ECS Meeting Abstracts MA2010-02 1479 (2010). DOI:
   10.1149/MA2010-02/21/1479. **1차 원문(초록, Unpaywall OA로 확보)** — 전체 학회 발표
   슬라이드는 별도 미확보이나 초록 자체가 IOPscience 게재본이라 1차 출처로 인정.
   diamond shape/size/density/protrusion이 pad cut rate·wafer removal rate에 "직접적
   영향(directly impacting)"을 미친다는 정성 결론과, protrusion variation이 클수록 cut
   rate·removal rate 하락 폭이 크다는 정성 결론.

## 2. Feng(2007) 기구학 모델 — 컨디셔닝 밀도(CD)의 정의와 구조
- **CD 정의(식 3.2)**: 반경 r에서 컨디셔닝 밀도 = "단위 면적당, 시간평균한 총 궤적
  선분 길이"(the time average of total segment length per unit area in the radial
  direction). 즉 그릿이 그 반경을 지나간 총 길이를 그 반경대 면적으로 나눈 값 — Preston
  방정식의 "마모가 CD에 비례한다"는 가정([3],[8] 인용, 논문 본문 서술)의 기반.
- **그릿 밀도(n_g)의 역할(식 3.10~3.15, 구조만 확인)**: 논문은 그릿 밀도 n_g = N /
  (2π(r_o²−r_i²))(디스크 환형 면적당 그릿 개수, r_o·r_i는 디스크 외·내경)를 정의하고,
  "unit conditioning density" C̄D = CD/n_g로 **밀도를 정규화해 분리**한다(식 3.15). 이는
  CD가 (그릿 밀도) × (기하학적 궤적 함수)로 **선형 분해**된다는 구조적 주장이며 — 그릿
  밀도가 2배가 되면 (다른 조건 동일 시) CD도 정확히 2배가 된다는 뜻. 정확한 C̄D(r) 폐형식
  수식 자체는 §1의 OCR 한계로 **미확보**, 구조(선형 분해)만 확인.
- **정성 결론 3가지(논문 §IV, 명시적 서술)**:
  1. 그릿 배치 패턴(균일 vs 구조화)이 CD 분포에 미치는 영향은 **미미함**(insignificant) —
     Example 4.1, 문헌 [6](Bubnick et al. 2001)과 일치한다고 저자가 명시.
  2. 패드 마모율(=CD)의 반경 분포를 평탄하게 하려면 **디스크반경/패드반경 비율을 작게**
     해야 한다 — Example 4.3 결론 2), 문헌 [8](Chen et al. 2000 J. Electrochem. Soc.)과
     일치한다고 명시. (본 노트 §4에서 독립 수치실험으로 이 정성 결론만 재현 시도)
  3. 디스크반경/패드반경 비율이 커질수록 마모율 피크가 패드 중심 쪽으로 이동함(Example
     4.3 결론 3).

## 3. 돌출 높이(protrusion height)·작동 그릿 비율 — 3M(2010) 실측
- 3M은 사후 분석(post-use examination)으로 실제 사용 중 그릿의 **깊이-of-penetration
  (DOP) ≈ 15 µm**를 결정(단일 앵커값, 실측 근거는 마모된 그릿의 절대 고도 측정 —
  본문에 정확한 측정법 세부는 없음, **부분 미검증**).
- 이 15 µm 기준고도에서 **접촉면적(작동 그릿이 실제로 패드에 닿는 비율로 해석)이
  기존 설계 대비 신설계에서 크게 증가**했다고 서술(Fig. 3a→3b) — 본문에 병기된 면적%
  수치는 그림 캡션 OCR상 (a) 4.46%/9.76%, (b) 90.2%/95.5%로 뒤섞여 표기되어 있어 **정확한
  대응관계(어느 % 쌍이 (a)/(b)인지) 확정 불가 — 미검증**. 다만 저자가 본문에 "significant
  increase in the number of working diamonds is observed at a 15 μm elevation"라고
  명시했으므로, **정성적으로 그릿 돌출 높이 분포를 개선(더 균일하게)하면 동일 기준고도에서
  작동 그릿 비율이 유의미하게(수배~수십 배 오더로 추정, 수치 자체는 미확정) 증가한다**는
  결론만 확정 인용한다.
- **결과 지표**: 개선 설계는 Cu 블랭킷 웨이퍼 결함(defect)에서 SP1 micro-defect
  67~75개(구설계) → 0~9개(신설계), macro-defect 3개(구) → 0개(신설계)로 감소(Table I,
  실측치). 이는 "돌출 높이 균일성 개선 → 결함 감소"의 직접 정량 증거이나, **cut rate
  자체는 신·구 설계가 "similar removal rates"라고만 서술되어 정량 수치는 없음 — 미검증**.

## 4. Feng 결론 #2(디스크/패드 반경비 작을수록 평탄) 독립 수치 재현 (Lv1-2 sanity check)
- Feng(2007)의 정확한 CD 폐형식 수식은 미확보이므로, **동일 결론을 낳는 독립적인
  기하학적 모델**을 직접 구성해 정성적으로 재현한다(수치 자체를 논문과 대조하는 것이
  아니라, "작은 반경비 → 평탄한 분포"라는 방향성만 재현 — 규칙 3에 따라 명시).
- 모델: 반경 R_pad인 원형 패드 중심으로부터 거리 x에 중심을 둔 반경 R_d인 원형
  컨디셔너 디스크가, 패드가 고속 회전하는 동안 반경 r인 원과 교차한다. 원-원 교차
  기하학에서 그 교차 현(chord) 길이는 `L(r,x) = 2r·sqrt(1-((x²+r²-R_d²)/(2xr))²)`
  (삼각형 부등식을 만족할 때만 유효, 즉 |x-R_d|≤r≤x+R_d). 디스크가 스윕 스트로크
  구간 x∈[x_min,x_max]를 균일하게 왕복하면, 반경 r에서의 누적 노출(∝CD)은
  `Exposure(r) = ∫ L(r,x) dx` (x에 대해 균일가중 적분)로 근사할 수 있다. 이는 Feng의
  궤적-누적 개념(식 3.1, 3.9)과 동일한 발상(그릿이 그 반경을 스치는 길이의 총합)이지만
  **Feng의 정확한 sinusoidal 스윕·회전 위상 적분과는 다른 단순화된 근사**임을 명시한다.

```python verify
import numpy as np

def exposure_profile(R_pad, R_d, x_min, x_max, n_r=200, n_x=400):
    """반경비 R_d/R_pad에 따른 방사방향 노출(CD 근사) 분포와 변동계수(CV)."""
    r = np.linspace(0.02 * R_pad, R_pad, n_r)
    xs = np.linspace(x_min, x_max, n_x)
    exposure = np.zeros(n_r)
    for x in xs:
        valid = (r > abs(x - R_d)) & (r < x + R_d) & (x > 0)
        num = (x**2 + r[valid]**2 - R_d**2)
        den = 2 * x * r[valid]
        cos_half = np.clip(num / den, -1, 1)
        L = 2 * r[valid] * np.sqrt(np.clip(1 - cos_half**2, 0, None))
        exposure[valid] += L
    exposure /= n_x
    return r, exposure

R_pad = 150.0  # mm, 임의 단위(무차원 비율만 의미 있음)

# Case A: 큰 디스크 (R_d/R_pad = 0.5, Feng의 "ratio가 큰" 경우에 대응)
r_big, exp_big = exposure_profile(R_pad, R_d=75.0, x_min=75.0, x_max=150.0)
# Case B: 작은 디스크 (R_d/R_pad = 0.10, Feng의 "ratio가 작은" 경우에 대응)
r_small, exp_small = exposure_profile(R_pad, R_d=15.0, x_min=15.0, x_max=150.0)

def cv(profile):
    mask = profile > 0
    p = profile[mask]
    return p.std() / p.mean()

cv_big = cv(exp_big)
cv_small = cv(exp_small)

print(f"CV(R_d/R_pad=0.50) = {cv_big:.4f}")
print(f"CV(R_d/R_pad=0.10) = {cv_small:.4f}")

# Feng(2007) Example 4.3 결론 #2: 디스크/패드 반경비가 작을수록 CD(=노출) 분포가 평탄해짐
# → 반경비가 작은 Case B의 변동계수(CV)가 Case A보다 작아야 한다.
assert cv_small < cv_big, (
    f"기대와 반대: 반경비가 작을 때(CV={cv_small:.4f})가 클 때(CV={cv_big:.4f})보다 "
    "평탄하지 않음 — Feng(2007) 결론 #2와 불일치, 모델 재검토 필요"
)
print("PASS: 반경비가 작을수록(0.10 < 0.50) 노출 분포가 더 평탄함(CV 낮음) "
      "— Feng(2007) 정성 결론 #2와 방향 일치 (수치 자체는 독립 근사 모델, 논문 수치와 직접 대조 아님)")
```

**재현 결과(방향성 확인)**: 위 코드 실행 시 `CV(R_d/R_pad=0.50)` ≈ 0.7~0.9대,
`CV(R_d/R_pad=0.10)` ≈ 0.1~0.2대로, 작은 반경비 쪽이 명확히 더 평탄(CV 낮음) —
Feng(2007) Example 4.3의 정성 결론(#2, "ratio 작을수록 CD 평탄")과 방향이 일치한다.
**단, 이 모델은 Feng의 정확한 스윕 기구학(사인파 스윕·회전 위상)을 재현한 것이 아니라
원-원 교차 기하학만으로 구성한 독립 근사이므로, 수치 자체(CV 절대값)를 논문과 대조하는
것은 아니다** — 규칙에 따라 방향성 재현으로만 표기.

## 5. 종합 — disk-design Lv1-2 시뮬레이터 설계 함의
- 그릿 밀도(n_g)는 Feng의 구조 분해(§2)에 따르면 CD(따라서 절삭율)에 **선형(비례)**으로
  기여한다고 논문이 주장하나, 정확한 폐형식 수식은 미확보 — sim/ 구현 시 "밀도 2배 →
  절삭율 2배" 가정은 **1차 근거(구조는 확인, 계수는 미확인)**로 표기해야 한다.
- 돌출 높이 분포의 균일성(3M §3)은 절삭율의 평균값보다는 **결함(defect) 발생과 작동
  그릿 비율의 변동성**에 더 직접적인 영향을 준다 — 단순 평균 cut rate 모델에는 반영이
  안 되고, 별도의 "working fraction" 또는 "protrusion variance" 항으로 확장이 필요함을
  시사(정성적 함의, Lv2-1의 그릿 탈락·수명 단원과 연결).
- 디스크/패드 반경비는 반경방향 마모 균일성(WIWNU)에 직접 영향을 준다는 것이 Feng의
  핵심 결론이며 §4에서 방향성 재현 확인 — 이는 [[../../knowledge/cmp/wafer-surface-metal-detection-txrf-vpdicpms-sims-xps]]나
  wafer-metrology의 radial TTV 지표와 직결되는 상위 원인 변수(디스크 설계 파라미터)임.

## 6. 미검증/한계 사항 (정직 표기)
- Feng(2007)의 정확한 CD 폐형식 수식(식 3.6, 3.9, 3.19, 3.23, 3.28)은 PDF의 수식 렌더링이
  OCR로 깨져 **구조(선형 분해, 정성 결론)만 확보, 정확한 계수·함수형은 미확보**.
- 3M Fig. 3의 접촉면적 % 수치는 OCR 순서가 뒤섞여 (a)/(b) 대응이 불명확 — **미검증**.
- 3M "improved conditioner provided similar removal rates"는 정성 서술이며 정량 removal
  rate 수치 자체는 논문에 없음(비교 결과는 결함 수만 정량) — **미검증**.
- ECS abstract(Kakireddy et al. 2010)는 초록만 확보, 본 발표의 그림·수치 데이터는
  **본문 미확보(2차 인용 아님, 초록 자체가 1차지만 상세 데이터 없음)**.
- §4의 수치실험은 독립 근사 모델로, Feng의 정확한 스윕 기구학과 다르다 — 방향성만
  재현했고 수치를 논문과 직접 대조하지 않았다는 점을 다시 명시한다.
