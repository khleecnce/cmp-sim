<!-- V2-SECTION: R5-wafer | 공동: R3-pad | 근거: ILD, planarization length, pattern density, 평탄화 | 정본: ARCHITECTURE-V2.md §3 -->
# ILD CMP 평탄화 — 글로벌/로컬 평탄도와 Stine/Ouma 밀도기반 모델 (planarization length)

> film-oxide Lv2-1 | 작성일: 2026-09-09
> 선행: [[../materials/film-oxide-hydration-layer-mechanism-cook-suratwala]] (Lv1-2, 옥사이드 제거 메커니즘),
> [[../materials/film-oxide-teos-hdp-bpsg-sod-density-hardness]] (Lv1-1)
> 관련: [[pattern-dependent-dishing-erosion]] (형제 노트 — 같은 MIT 모델을 process-integrator 관점에서 정리, 본 노트는 옥사이드 ILD 원문 기준으로 심화),
> [[npw-ptw-pattern-effect-gw-physics]] (NPW blanket rate K가 PTW를 못 맞추는 접촉역학),
> [[preston-luo-dornfeld-mrr]] (K = Kp·P·V의 출처), [[../materials/hertz-gw-contact-mechanics]] (asperity 접촉),
> [[../materials/pad-subpad-stiffness-edge-nonuniformity]] (서브패드 강성이 PL을 지배 — §6),
> [[wiwnu-pressure-velocity-wafer-scale]] (웨이퍼 스케일 변동과의 중첩)

## 1. 왜 이 단원이 필요한가

Lv1에서 옥사이드가 "어떻게" 깎이는지(수화층 + 기계 제거)를 봤다. 이 단원은 다층 배선의
ILD(inter-layer dielectric, 층간 절연막) 위에서 CMP가 **무엇을** 평탄화하는지 — 즉 국소(local)
단차는 없애지만 전역(global) 단차를 새로 만든다는 역설 — 를 1차 문헌(Ouma 박사논문 원문)으로
정량화한다. 핵심 파라미터는 **planarization length(평탄화 길이, PL)** 하나다.

## 2. 1차 출처

- **Dennis Okumu Ouma, "Modeling of Chemical Mechanical Polishing for Dielectric Planarization,"
  Ph.D. thesis, MIT EECS, 1999 (copyright 1998; 지도교수 D. Boning, J. Chung).**
  MIT DSpace handle http://hdl.handle.net/1721.1/9704 — **원문 PDF 확보**
  (`papers/ouma1999-mit-thesis-cmp-dielectric-planarization.pdf`, 229쪽 스캔본, 텍스트층 없음.
  DSpace REST API로 저자·연도·제목 메타데이터 확인). 1.4절(p.28-32), 5장 전체(p.111-155),
  7.1-7.2절(p.177-189)을 페이지 이미지로 직접 읽음. 이하 "논문 p.xx"는 이 논문 인쇄 쪽수.
- D. O. Ouma, D. S. Boning, J. E. Chung, W. G. Easter, V. Saxena, S. Misra, A. Crevasse,
  "Characterization and Modeling of Oxide Chemical Mechanical Polishing Using Planarization
  Length and Pattern Density Concepts," *IEEE Trans. Semicond. Manuf.* 15(2), 232-244 (2002).
  DOI: 10.1109/66.999598 — Crossref로 권·호·쪽수 확인. **본문은 유료(IEEE), 미확보** —
  박사논문 5장의 저널판이므로 본 노트는 논문 원문을 정본으로 삼는다.
- B. Stine, D. Ouma, R. Divecha, D. Boning, J. Chung, D. Hetherington, C. R. Harwood,
  O. S. Nakagawa, S.-Y. Oh, "Rapid Characterization and Modeling of Pattern-Dependent Variation
  in Chemical-Mechanical Polishing," *IEEE Trans. Semicond. Manuf.* 11(1), 129-140 (1998).
  DOI: 10.1109/66.661292 — Crossref 확인, **본문 미확보(2차 인용)**. 기본모델(§3)은 Ouma 논문이
  "Stine et al. [31]이 제안"이라 명시한 것을 Ouma 원문 식 5.1-5.3으로 읽었다.
- X. Xie, T. Park, B. Lee, T. Tugbawa, H. Cai, D. Boning, "Re-examining the Physical Basis of
  Pattern Density and Step Height CMP Models," *MRS Spring Meeting Symp. F* (2003).
  https://mtlsites.mit.edu/researchgroups/Metrology/PAPERS/Xie_Boning_MRS03v3p7.pdf — 원문
  PDF 확보(`papers/xie2003-mrs-planarization-length-physical-basis.pdf`). DOI 미확인(학회록).
- D. Boning et al., "Pattern Dependent Modeling for CMP Optimization and Control," MRS 1999 —
  형제 노트 [[pattern-dependent-dishing-erosion]]가 이미 원문 확인(`papers/boning1999-mrs-pattern-dependent.pdf`).

## 3. 로컬 vs 글로벌 평탄화 — 정의 (논문 1.4절, p.28-31)

Ouma 논문 Fig.1.7/1.8의 정의를 그대로 옮긴다.
- **local step height(국소 단차)**: 인접한 높은 곳(금속선 위 산화막, "up area")과 낮은 곳(선 사이,
  "down area") 사이 높이차. CMP는 이것을 거의 0으로 만든다 — down area 폭이 PL보다 훨씬 작으면
  패드가 그 안으로 못 들어가므로 down area는 거의 안 깎이고 up area만 깎인다("This is why CMP
  achieves good local planarity", p.30).
- **global step height(전역 단차)**: 초기 패턴밀도가 다른 두 영역(ρ1 낮음, ρ2 높음)이 서로 다른 속도로
  깎여 국소 평탄화가 끝난 뒤에도 남는 높이차. Fig.1.7: t=T1에 저밀도 영역 국소평탄, t=T2에
  고밀도 영역 국소평탄 — 그 사이 생긴 두께차가 영구히 남는다. **"CMP removes local steps but
  generates global steps"** (p.28).
- **TIR(total indicated range)**: die 안 최고점-최저점 차 = 글로벌 단차의 실측 지표. 논문은 "국소
  단차 제거능력은 주요 평가항목이 아니고, TIR이 진짜 문제"라 못박는다(p.31). 다만 TIR은 극단 밀도
  위치를 알아야 하므로 레이아웃마다 다르고, **PL이 더 포괄적인 특성화 파라미터**다(p.31).
- **planarization length(1차 정의)**: 계단형 밀도 경계에서 국소 평탄화가 완료되기까지의 전이영역
  길이(Fig.1.8, p.30). 패드 탄성과 공정조건의 함수.
- 웨이퍼 스케일 변동은 이 die 내 패턴변동 위에 **중첩**되며(Fig.1.9), "패턴의존 변동이 웨이퍼레벨
  변동보다 통상 훨씬 크다"(p.31) → [[wiwnu-pressure-velocity-wafer-scale]]와 곱해서 다뤄야 한다.

## 4. Stine/Ouma 밀도기반 기본모델 (논문 5.1절, p.113-115)

Preston 식 dz/dt = -Kp·P·V 를 blanket rate K와 유효밀도 ρ(x,y,z)로 다시 쓴다(식 5.1):

```
dz/dt = -K / ρ(x,y,z)
ρ(x,y,z) = ρ0(x,y)   (z > z0 - z1, 국소 단차가 남아 있는 동안)
         = 1         (z < z0 - z1, 국소 평탄화 이후 → blanket rate로 폴리싱)     (식 5.2)
```
z0 = 초기 산화막 두께(up area), z1 = 초기 국소 단차. 폐형해(식 5.3):

```
z(t) = z0 - K·t/ρ0(x,y)                 t < ρ0·z1/K   (단차 잔존, 두께 ∝ 1/ρ_eff)
     = z0 - z1 - K·t + ρ0(x,y)·z1       t > ρ0·z1/K   (선형 레짐, 기울기 -K)
```
가정: ① 국소 단차가 없어질 때까지 down area는 안 깎임(패드 비압축성). ② ρ0는 막두께에 무관
(프로파일을 직선으로 근사 — "실험적으로 대부분의 막에서 정당화", p.114). ③ 측면 증착 효과는 금속선
폭에 **bias B**를 더해 반영 — 컨포멀 막은 B>0, HDP-CVD 산화막은 B<0 (p.113-114).
④ 큰 down area(필드)는 밀도 ≈ 0으로 취급해 즉시 국소평탄, 이후 선형 레짐으로 처리(p.114).

선형 레짐에서 **최종 두께는 ρ0에 선형(기울기 z1)** — 이것이 특성화 마스크로 PL을 뽑는 근거이며
(식 5.18 = 식 7.7), 두 극단 밀도 사이 두께차가 곧 TIR이다(§7).

## 5. Planarization length의 물리 — 유효밀도 가중함수 (논문 5.2-5.3절)

### 5.1 유효밀도 = 레이아웃 ⊗ 가중함수 (식 5.4)
`d(x,y) = l(x,y) ⊗ w(x,y)` — 국소 레이아웃 밀도 l을 패드 임펄스응답 w로 컨볼루션. w를 데이터에서
역산(식 5.5-5.6, 주파수영역 나눗셈)하는 방식은 데이터량 부족·L(k)=0 문제로 실패(p.118) → 대신
**패드 탄성변형 물리에서 w의 모양을 정하고 길이만 캘리브레이션**하는 전략을 택했다(p.121).

- 정사각 창(Stine 원안): 창 크기 = PL. 물리적으로 부정확(경계가 급격, 방향성 없음, p.117).
- **타원(elliptic) 가중함수(Ouma)**: 반경 a 원형 영역에 하중 q가 걸린 탄성 반무한체의 변형 프로파일
  (식 5.11 r<a, 식 5.12 r>a — 완전 타원적분). 핵심 성질: **변형의 모양은 재료상수(E, ν)에 무관하고
  하중 면적 a에만 의존**(p.125) → 재료·하중은 크기만 정하므로, 모양은 고정하고 길이 L=2a만
  데이터로 맞추면 된다.
- 최대 변형 w_max = 2(1-ν²)qa/E (식 5.13), 가장자리 변형 w(a) = 4(1-ν²)qa/(πE) (식 5.14).
  **PL의 공식 정의: 상대 가중치가 피크의 2/π로 떨어지는 폭 L**(Fig.5.11, p.130-131).
- 수치 예(p.126): IC1000 패드 E=2.9×10⁷ Pa, ν≈1/3, 반경 2 mm 원형 하중, 국소압 7 psi →
  최대 처짐 "약 6 µm". §9에서 재현.
- 압력분포(식 5.15): q = P/(2πa√(a²-r²)) — 중앙은 평탄, 가장자리 특이점 → 패턴 모서리가 먼저
  깎여 둥글어짐(p.126-127). 패드 asperity 크기가 ~50 µm 오더라 그보다 작은 피처는 단독으로 압력을
  못 받고, **인접 피처들의 중첩(superposition)** 으로 패드 표면이 국소 평탄해진다(Fig.5.9, p.127-128).
  → 이것이 [[../materials/hertz-gw-contact-mechanics]]·[[npw-ptw-pattern-effect-gw-physics]]의
  asperity 스케일과 PL(mm 스케일)이 분리되는 이유.
- 계산은 FFT 3단계(레이아웃 셀밀도 → 컨볼루션 → 유효밀도)로 하며, 어떤 가중함수든 같은 시간에
  가능(p.151, 5.6절).

### 5.2 가중함수별 캘리브레이션 오차 (논문 표 5.3, p.155)
| 필터 | RMS 오차 (Å) | 최적 창/길이 (mm) |
|---|---|---|
| Square | 91 | 5.25 |
| Cylindrical | 100 | 5.85 |
| Gaussian | 56 | 10.5 |
| **Elliptic** | **42** | 7.35 |

꼬리가 긴 필터(Gaussian, Elliptic)가 계단형 밀도 경계의 두께 천이를 더 잘 따른다(Fig.5.27, p.154).
단, "특성 길이의 정의가 필터마다 다르다(정사각=변, 원통=지름, 가우시안=1차 모멘트)"고 저자가
경고(p.154) — **필터가 다르면 PL 숫자를 직접 비교하지 말 것.**

## 6. PL 캘리브레이션 절차와 실측값 (논문 5.4-5.5절, 7.2절)

**절차(Fig.5.19, p.143)**: PL 초기값 → 유효밀도 계산 → 식 5.3으로 두께 예측 → 실측과 SSE → PL 갱신
반복. 데이터 조건: 계단형 밀도 마스크(4 mm×4 mm 블록), 블록당 ≥3점(5점 이상은 이득 미미), **up
area만 측정**(글로벌 평탄도가 목적), 중심 die 1개면 충분, 폴리시 시간은 "50% 밀도 구조가 국소
평탄화되는 시점"(50%는 blanket의 2배 속도)으로 설정(p.144-145).

**표 5.2 (p.146) — 공정조건별 PL, elliptic 필터:**
| 공정 | 다운포스 (psi) | 테이블 속도 (rpm) | PL (mm) |
|---|---|---|---|
| A (L,L) | 4.8 | 32 | 3.75 |
| B (L,H) | 4.8 | 68 | 4.50 |
| C (H,L) | 7.2 | 32 | 3.60 |
| D (H,H) | 7.2 | 68 | 2.90 |

저자 해석: "낮은 다운포스·높은 테이블 속도가 가장 긴 PL"(p.146) — 단 D(고압·고속)가 최단인 점은
이 한 줄 해석과 맞지 않고 논문도 설명하지 않는다(**원인 미상**, 7.2.5절은 "1차 인자는 다운포스,
속도는 2차"라고만 함, p.187).

**모델 검증 (Ouma 1999, 5.4.5절 p.146-148)**: Mask1로 뽑은 PL 3.75 mm를 Mask2에 적용. 폴리시 105/158/316 s
중 두 번째 시점 RMS < 150 Å, 최종 시점 RMS 270 Å(10% 저밀도 블록에서 악화). 초기 2 µm 막에서
1.5 µm 제거 후 모델 붕괴 — "실용 범위 밖"으로 처리, 원인은 미해결(패드가 이미 평탄화된 저지대에
압력을 덜 주는 효과 누적으로 추정, p.147). down area는 필터 길이 3.90 mm에서 잘 맞음(Fig.5.23).

**다른 추출법(5.5절)**: slope법 — 창 크기를 바꿔가며 두께 vs 밀도 회귀 기울기가 z1과 같아지는
창을 PL로 취함(Fig.5.24: PAD A 3 mm, PAD B 9.5 mm). regression법 — R² 최대 창(예 3.6 mm, Fig.5.24
두 번째). 둘 다 정사각 창에서만 편리.

**패드/속도 효과(7.2절, p.181-189)**: 통상 폴리시 PL 3 mm vs 고속·서브패드 없음 9.5 mm(Fig.7.5,
정사각 창 slope법). 저자는 이 ~3배를 속도가 아니라 **서브패드 부재(더 단단한 패드)** 탓으로 돌린다
— 표 7.2: 표준 적층패드 6.35 → 6.58 mm(속도 효과 +4%)인데 서브패드 제거 시 9.50 mm(속도 무관).
"PL은 서브패드의 강한 함수이며 패드 마모에는 둔감"(p.149) → [[../materials/pad-subpad-stiffness-edge-nonuniformity]]
와 직결. Xie 2003(MRS)은 contact-wear 시뮬레이션으로 **PL ∝ E(패드 영률) 선형, blanket rate에는
무관**을 확인(Fig.8) — 숫자는 논문에 없어 경향만 인용.

**글로벌 평탄도 개선 실측(Fig.7.4, p.185)**: 밀도 마스크 두께 range 5690 Å(통상) → 1824 Å(고속·
서브패드 없음), area 마스크 4419 → 1957 Å. PL 3배 → TIR 약 1/3 — §7 관계식과 방향 일치.

## 7. PL ↔ TIR 관계와 최적 증착량 (논문 7.1절, p.178-181)

```
Δρ = ρ_max - ρ_min            (die 내 유효밀도 범위, PL이 길수록 작아짐)        (7.1)
TIR = Δρ · z1                 (식 5.3 선형 레짐의 두 극단 밀도 차에서 유도)       (7.2)
t_lp = ρ_max · z1 / K         (최고밀도 영역 국소평탄화 시간; 이후 더 깎아도 TIR 불변) (7.3)
H0 = H_ILD + z1·(1 + Δρ)      (최소 잔류두께 H_ILD 보장에 필요한 초기 증착량)     (7.4)
t_opt = (ρ_max + 0.1)·z1 / K  (단차 10% 추가 오버폴리시 권고)                     (7.5)
H_opt = H_ILD + z1(1+Δρ) + H_error  (H_error = 웨이퍼 스케일 blanket 변동분)      (7.6)
```
Fig.7.1(p.179): 밀도 마스크, z1 = 7500 Å, PL = 4 mm → Δρ = 80% → TIR = 6000 Å. 각주(p.181):
실무 z1 ≈ 0.7 µm, H_ILD ≈ 0.8 µm, 초기 막 1.6-2.0 µm. **의미**: 증착량과 폴리시 시간은 PL 하나로
설계할 수 있고, 밀도 범위 Δρ를 줄이는 것(dummy fill)이 증착량·슬러리 소모를 줄이는 직접 레버.

## 8. 과제 문구 "step height ∝ exp(-x/PL)"에 대한 정직한 정정

Ouma/Stine 밀도 모델에는 **지수함수형 단차 감쇠가 없다.** ① 시간축: 국소 단차는 비압축성 가정
아래 **선형**으로 줄어 t = ρ0·z1/K에 소멸(식 5.3). 지수감쇠 h(t) ∝ exp(-t/τ)는 압축성 패드 모델
(Burke/Tseng)과 MRS99 통합모델에 속하며 형제 노트 [[pattern-dependent-dishing-erosion]] §3에 정리돼
있다. ② 공간축: 밀도 경계에서 두께 천이는 exp가 아니라 **타원 가중함수(완전 타원적분)의 컨볼루션**
이고, 그 폭이 PL이다. Gaussian 근사(σ)가 종종 쓰이며(논문 식 5.9, Xie 2003도 Gaussian 사용)
이때 exp(-x²/2σ²) 형태가 된다 — 1차 지수 exp(-x/PL)는 어느 원문에도 없다(**출처 불명**, 채택 안 함).

## 9. 검증 — 원문 수치 재현 (```python verify```, 실제 실행)

재현 요약(한 줄): 논문 Fig.7.1의 TIR = 0.8 × 7500 Å = 6000 Å, 식 5.13 IC1000 최대처짐 약 6 µm, 식 5.14
가장자리비 2/π, 표 7.2/Fig.7.5의 PL 비 9.5/3 ≈ 3.2배("about three times")를 코드로 대조한다 (Ouma 1999,
hdl.handle.net/1721.1/9704; 저널판 doi.org/10.1109/66.999598).

```python verify
# ── Ouma 1999 MIT thesis (hdl.handle.net/1721.1/9704) 원문 수치 재현 ──
import numpy as np

# [A] 식 5.3 폐형해 — 두 레짐 경계에서 연속인지, 선형 레짐에서 두께가 ρ0에 선형(기울기 z1)인지
z0, z1, K = 20000.0, 7500.0, 3000.0     # Å, Å, Å/min (z1=7500Å은 Fig.7.1 값; z0,K는 예시)
def z_ouma(t, rho0):
    tc = rho0 * z1 / K
    return np.where(t < tc, z0 - K * t / rho0, z0 - z1 - K * t + rho0 * z1)
for rho0 in (0.1, 0.5, 0.9):
    tc = rho0 * z1 / K
    left, right = z_ouma(tc - 1e-9, rho0), z_ouma(tc + 1e-9, rho0)
    assert abs(left - right) < 1e-3, f"식5.3 경계 불연속 rho0={rho0}: {left} vs {right}"
t_lin = 0.9 * z1 / K + 0.5                       # 모든 밀도가 선형 레짐에 든 시각 (식 7.3 이후)
rhos = np.linspace(0.1, 0.9, 9)
zs = z_ouma(t_lin, rhos)
slope = np.polyfit(rhos, zs, 1)[0]
assert abs(slope - z1) / z1 < 1e-9, f"선형 레짐 기울기 {slope} != z1 {z1} (식 5.18/7.7)"

# [B] 식 7.2 TIR = Δρ·z1 — Fig.7.1: PL=4mm 밀도마스크 Δρ=80%, z1=7500Å → TIR 6000Å (논문 p.179)
d_rho, TIR_lit = 0.80, 6000.0
TIR = d_rho * z1
assert abs(TIR - TIR_lit) < 1e-6, f"TIR 재현 실패: {TIR} vs 문헌 {TIR_lit}"
# 같은 값이 식 5.3 두 극단 밀도 차에서도 나와야 한다(유도 확인)
TIR_from_53 = z_ouma(t_lin, 0.9) - z_ouma(t_lin, 0.1)
assert abs(TIR_from_53 - TIR) < 1e-6
# 식 7.4 증착량: 각주 z1≈0.7µm, H_ILD≈0.8µm, "초기 막 1.6-2.0µm" 범위에 드는지 (Δρ=0.8 가정)
H0 = 0.8 + 0.7 * (1 + 0.8)                       # µm
assert 1.6 <= H0 <= 2.2, f"H0={H0:.2f}µm — 각주 범위(1.6-2.0µm)와 크게 다름"
print(f"[A/B] TIR={TIR:.0f}Å (문헌 6000Å), H0={H0:.2f}µm (각주 1.6-2.0µm)")

# [C] 타원 가중함수 — 식 5.11(r<a), 5.12(r>a)을 θ-적분으로 직접 계산해 식 5.13/5.14와 대조
E_pad, nu, a = 2.9e7, 1.0 / 3, 2.0e-3            # Pa, -, m  (IC1000 예, 논문 p.126)
q = 7.0 * 6894.757                               # 7 psi → Pa
th = np.linspace(0, np.pi / 2, 200001)
pref = 4 * (1 - nu**2) * q / (np.pi * E_pad)
def w_in(r):                                     # 식 5.11
    return pref * a * np.trapz(np.sqrt(1 - (r / a)**2 * np.sin(th)**2), th)
def w_out(r):                                    # 식 5.12
    k2 = (a / r)**2
    E_int = np.trapz(np.sqrt(1 - k2 * np.sin(th)**2), th)
    K_int = np.trapz(1 / np.sqrt(1 - k2 * np.sin(th)**2), th)
    return pref * r * (E_int - (1 - k2) * K_int)
w_max = w_in(0.0)
w_max_513 = 2 * (1 - nu**2) * q * a / E_pad      # 식 5.13
w_edge = w_in(a * (1 - 1e-9))
w_edge_514 = 4 * (1 - nu**2) * q * a / (np.pi * E_pad)  # 식 5.14
assert abs(w_max - w_max_513) / w_max_513 < 1e-6, "식 5.11(r=0) ≠ 식 5.13"
assert abs(w_edge - w_edge_514) / w_edge_514 < 1e-4, "식 5.11(r=a) ≠ 식 5.14"
assert abs(w_edge / w_max - 2 / np.pi) < 1e-4, "가장자리/최대 비가 2/π가 아님 (PL 정의 근거)"
# r>a 식과 r=a에서 연속(적분 특이점 때문에 r=1.001a로 근사)
w_out_near = w_out(a * 1.001)
assert abs(w_out_near - w_edge_514) / w_edge_514 < 0.02, "식 5.12가 r→a+에서 식 5.14와 불연속"
# 문헌: "maximum deflection is about 6 µm" (p.126)
assert abs(w_max * 1e6 - 6.0) / 6.0 < 0.05, f"w_max={w_max*1e6:.2f}µm — 문헌 '약 6µm'와 5% 이상 차이"
# 모양 불변성: E를 10배 바꿔도 정규화 프로파일은 동일 (p.125 주장)
prof1 = np.array([w_out(r) for r in a * np.array([1.5, 2, 4, 8])]) / w_max
E_pad2 = E_pad * 10; pref = 4 * (1 - nu**2) * q / (np.pi * E_pad2)
prof2 = np.array([w_out(r) for r in a * np.array([1.5, 2, 4, 8])]) / w_in(0.0)
assert np.allclose(prof1, prof2, rtol=1e-9), "변형 모양이 E에 의존 — 논문 p.125 주장과 불일치"
print(f"[C] w_max={w_max*1e6:.2f}µm (문헌 약 6µm), w(a)/w_max={w_edge/w_max:.4f} (2/π={2/np.pi:.4f}), "
      f"꼬리 w(4a)/w_max={prof1[2]:.3f}")

# [D] PL 실측값의 내부 정합 — 표 5.2, 표 7.2, Fig.7.5 (논문 p.146, p.186-189)
PL_tab52 = {"A(L,L)": 3.75, "B(L,H)": 4.50, "C(H,L)": 3.60, "D(H,H)": 2.90}   # mm
assert max(PL_tab52, key=PL_tab52.get) == "B(L,H)", "표 5.2: 저압·고속이 최장이어야(p.146 서술)"
assert PL_tab52["C(H,L)"] < PL_tab52["A(L,L)"], "표 5.2: 같은 속도에서 고압이 더 짧아야(7.2.5절)"
PL_conv, PL_hs_nosub = 3.0, 9.5                  # Fig.7.5 slope법(정사각 창)
ratio = PL_hs_nosub / PL_conv
assert 2.8 <= ratio <= 3.4, f"PL 비 {ratio:.2f} — 논문 'about three times'(p.188)와 불일치"
PL_stacked = (6.35, 6.58); PL_nosub = (9.50, 9.50)   # 표 7.2 (저속, 고속)
speed_eff = PL_stacked[1] / PL_stacked[0] - 1
subpad_eff = PL_nosub[0] / PL_stacked[0] - 1
assert speed_eff < 0.05 and subpad_eff > 0.4, "표 7.2: 속도 효과는 미미, 서브패드 효과가 지배여야"
print(f"[D] PL비 고속/통상={ratio:.2f}배, 속도효과 +{speed_eff*100:.1f}%, 서브패드제거 +{subpad_eff*100:.0f}%")

# [E] 합성 데모 — Fig.7.1 성질: PL이 길수록 die 내 Δρ가 단조 감소 (밀도 마스크 대신 합성 1D 레이아웃)
x = np.arange(0, 24.0, 0.05)                     # mm
layout = np.select([x < 8, x < 12, x < 16, x < 20], [0.05, 0.10, 0.90, 0.50], default=0.05)
def gauss_eff(PL):                               # 논문 식 5.9 가우시안 근사(σ=PL/2), 정규화
    sig = PL / 2
    k = np.exp(-((x - x.mean())**2) / (2 * sig**2)); k /= k.sum()
    return np.convolve(layout, k, mode="same")
d_rhos = [np.ptp(gauss_eff(PL)) for PL in (1, 2, 4, 8, 12)]
assert all(np.diff(d_rhos) < 0), f"Δρ가 PL에 단조감소하지 않음: {d_rhos}"
assert d_rhos[0] > 0.7 and d_rhos[-1] < 0.5, "PL 1mm면 거의 원 레이아웃, 12mm면 크게 평활돼야"
print(f"[E] Δρ(PL=1,2,4,8,12mm) = {[round(v,2) for v in d_rhos]} — 단조감소 확인")
print("OK: Ouma 1999 식 5.3/5.11-5.14/7.2, 표 5.2/7.2 재현 통과")
```

**결과 해석(정직하게)**
- [B] TIR 6000 Å과 [C] 최대처짐 ≈ 6 µm는 논문값과 일치. [C]의 2/π 비율은 해석식(5.13/5.14)의
  적분 재현이므로 "일치"는 수학적 동일성 확인이지 실험 검증이 아니다.
- [D]는 논문 실측 표의 **내부 정합**(서술과 표가 맞는지)만 확인한다. PL 절대값 3-9.5 mm는 재현 대상이
  아니라 입력값이다 — 우리 툴·패드에서의 PL은 특성화 마스크 실측 없이는 **미검증**.
- [E]는 논문 밀도 마스크 레이아웃 파일이 없어 합성 레이아웃으로 **성질만** 재현했다. Fig.7.1의
  Δρ(PL) 곡선 절대값(PL 4 mm → 80%)은 그 마스크 고유값이라 대조 불가.
- 표 5.2의 D(고압·고속) 최단 PL은 논문 서술과 부분 상충 — 원인 미상으로 남긴다.

## 10. 옥사이드 전문가 관점 결론

1. **ILD CMP의 산출물은 "국소 평탄 + 글로벌 비평탄"이다.** 글로벌 비평탄(TIR)은 Δρ·z1로 결정되고,
   Δρ는 레이아웃과 PL의 함수다. 공정이 바꿀 수 있는 것은 PL(패드 강성·다운포스), 설계가 바꿀 수
   있는 것은 Δρ(dummy fill).
2. **PL은 서브패드 강성이 지배**한다(표 7.2, Xie 2003 PL ∝ E). 패드 마모·컨디셔닝에는 둔감(p.149)
   — 따라서 PL은 패드 수명 모니터가 아니라 **소모품 세트 특성값**으로 관리하는 게 맞다.
3. K(blanket rate)는 [[preston-luo-dornfeld-mrr]]·Lv1-2 수화층 모델에서 오고, 밀도모델은 그 K를
   1/ρ_eff로 나눌 뿐이다. 옥사이드 막종(TEOS/HDP)은 K뿐 아니라 **bias B의 부호**(HDP는 음)로
   모델에 들어간다 — Lv1-1 막질 노트와 결합점.
4. 모델 한계(원문이 명시): 1.5 µm 이상 과다 제거 시 붕괴, down area 폴리싱 무시(압축성 패드 전이는
   [[pattern-dependent-dishing-erosion]] §3의 통합모델로 보완), 필터 종류에 따라 PL 숫자 비교 불가.

## 11. 구현 요청 → agents/film-oxide/PROFILE.md "## 구현 요청" 참조
(elliptic 가중커널 식 5.11-5.12 + 식 5.3 폐형해 + TIR/증착량 설계식 7.1-7.6. 현재
`sim/tier1_empirical/pattern_density.py`는 가우시안 커널만 있음.)

## 12. 자기시험
→ [[../../agents/film-oxide/EXAMS.md]] Lv2-1 문항 참조.
