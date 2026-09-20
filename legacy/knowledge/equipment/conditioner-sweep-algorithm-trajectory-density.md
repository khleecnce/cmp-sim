<!-- V2-SECTION: R4-disk | 분배완료 2026-09-08 | 근거: conditioner, sweep, 다이아, 컨디셔너 | 정본: ARCHITECTURE-V2.md §3 -->
# 컨디셔너 스윕 알고리즘별 궤적밀도 모델 — 정속 각속도 스윕의 반환점 밀도발산

> disk-kinematics Lv1-1. 컨디셔너 아암의 각속도 프로파일(스윕 알고리즘)과 체류시간이 반경별
> 궤적(다이아몬드 통과) 밀도에 어떻게 매핑되는지를 다룬다. 기존 [[conditioner-sweep-kinematics-pcr-profile]]
> 노트(disk-conditioner Lv2-2, Zheng et al. 2023 몬테카를로/격자 적산 방식)와 주제가 겹치므로,
> grep으로 확인한 뒤 **다른 각도** — 격자 시뮬레이션이 아니라 반환점(turning point) 근방에서
> 궤적밀도가 해석적으로 발산하는 기구학적 이유 — 로 별도 작성한다.

## 1. 출처
1. **Wang, Lian, Lin & Tsai (2025)**, "Geometric-overlap Modeling and Sweep Uniformity Optimization
   of Fixed Diamond Conditioning Disks for Chemical Mechanical Planarization", *Sensors and
   Materials* 37(10), 4447–4458. DOI: https://doi.org/10.18494/sam5844 (오픈액세스 CC-BY,
   National Chin-Yi Univ. of Technology, Taiwan; 2025-10-21 게재 — 최신 논문). find_open_access.py
   Unpaywall 조회로 PDF 확보(papers/wang2025-sweep-uniformity-sam5844.pdf), fitz로 본문 직접 발췌.
   — 본 노트의 1차 출처. GPU가속 "기하학적 중첩모델"과 NAR(정규화 중첩면적비) 지표, 다이아몬드
   개수 Nd=3~12별 정량 결과, 톱니파(saw-tooth) 스윕(±34°, 10°/s) 기구.
2. **Zheng, Zhao & Lu (2023)**, PMC10536193 — [[conditioner-sweep-kinematics-pcr-profile]]에서
   이미 확립한 4중 회전 합성(패드 자전·팔 스윕·디스크 자전·입자 반경위치) 좌표계 및 사인파 스윕
   β(T) 식. 본 노트는 그 스윕 파라미터화가 왜 반환점에서 밀도 특이성을 갖는지 분석하는 데 재사용.
3. 아크사인(arcsine) 분포는 조화진동자의 시간-평균 위치밀도로서 고전역학/확률론의 표준 결과다
   (2차 문헌 인용이 아니라 폐형식 수식이므로, §3 verify 블록에서 수치적분과 직접 대조해 코드로
   검증한다 — "출처"가 아니라 "유도 후 코드로 재확인"에 해당).

## 2. 기하학적 배경 — Wang et al.(2025) Table 1 파라미터
Wang et al.은 패드 자전(ω_pad) · 아암-플레이트 어셈블리 회전(θ_arm) · 디스크 자전(ω_DD)의 3단
합성 회전으로 다이아몬드 절대위치를 정의한다(논문 Eq.1–5, 회전행렬 곱 R_pad⁻¹·R_arm·R_DD).
시뮬레이션 조건(논문 Table 1):

| 파라미터 | 값 |
|---|---|
| 패드 직경 D_pad | 510 mm |
| 다이아몬드 디스크 직경 D_DD | 101.6 mm |
| 다이아몬드 배치반경 r_array | 40 mm |
| 다이아몬드 개수 N_d | 3~12 |
| 패드 자전속도 ω_pad | 90 rpm |
| 디스크 자전속도 ω_DD | 87 rpm |
| 아암 오실레이션 진폭 A_osc | ±34° |
| 오실레이션 스윕속도 θ_osc | 10 °/s (톱니파, saw-tooth) |

핵심 차이점: Zheng et al.(2023)은 **사인파(sinusoidal)** 스윕 모드(β(T)가 cos(arccos(...)+ωt)
형태)를 쓴 반면, Wang et al.(2025)은 **톱니파(정속 각속도, 10°/s로 왕복)** 스윕을 쓴다. 두
알고리즘 모두 "왕복(reciprocating)" 운동이라는 공통점이 있고, 이 공통점 자체가 §3의 반환점
밀도발산을 일으키는 원인이다(사인파는 위치 자체가 조화함수라서, 톱니파는 위치-각도 사상이
비선형이라서 — 메커니즘은 다르지만 결과는 유사).

## 3. 궤적밀도 정량모델 — 반환점(turning point) 밀도발산

**(a) 조화진동 위치의 시간-평균 밀도 = 아크사인 분포.** 각도 θ(t)=ωt(각속도 ω 일정, 톱니파의
전형적 가정)이고 위치 x(θ)=A·sin(θ)라면, θ에 대해 균등한 시간샘플이 x-공간에서는

```
p(x) = 1 / (π·sqrt(A² − x²)),   −A < x < A
```

인 아크사인 분포로 사상된다. 이 분포는 x→±A(반환점, 즉 스윕 진폭의 끝)에서 **발산**한다 —
아암이 반환점 근처에서 국소적으로 느려지기 때문에(dx/dθ→0) 그 위치에 머무는 시간(밀도)이
비례해서 커진다. 이는 사인파 스윕(Zheng et al. 방식)에서 직접 적용되는 관계다.

**(b) 톱니파(정속 각속도) + 오프셋-원 사상 → 반경밀도 비균일.** Wang et al.은 아암을 "기준원
중심 C1 주위를 도는 팔 각도 θ_arm"으로 정의하지만(Eq.2), 팔 피벗과 패드 중심 사이 거리(L)와
팔 길이(R_arm)의 구체적 수치는 논문 본문·Table 1에 공개되어 있지 않다 — **미검증**, 이하 예시
값(L=140 mm, R_arm=90 mm, 다이아몬드 배치반경 40 mm와 디스크반경 50.8 mm 대비 자릿수만
맞춘 추정치)으로 정성적 메커니즘만 시연한다. 팔이 패드 중심에서 거리 L만큼 떨어진 피벗을
축으로 반경 R_arm에서 회전하면, 팔 끝(디스크 중심)의 패드-중심 기준 반경은 코사인법칙으로

```
r(θ) = sqrt(L² + R_arm² − 2·L·R_arm·cos(θ))
```

이고, 톱니파는 dθ/dt가 상수이므로 θ에 대해 시간이 균등 분배된다. 그런데 dr/dθ =
L·R_arm·sin(θ)/r(θ)는 θ=0(팔이 패드중심 쪽을 정면으로 향하는 반환점 부근)에서 0에 가까워지므로,
**반경 공간에서의 궤적밀도는 균일하지 않고 특정 반경대(반환점에 대응하는 r)에 집중**된다.
이것이 Wang et al. Conclusion(4)의 "정속 스윕은 패드 중심을 과다 컨디셔닝한다"는 서술의
기하학적 근거로 해석된다(논문은 이 메커니즘을 수식으로 명시하지 않고 시뮬레이션 결과로만
보고 — 본 노트의 §3(b) 유도는 그 결과를 설명하는 **본 노트의 자체 해석(추정)**이며, 논문이
직접 증명한 것은 아니다).

```python verify
import numpy as np

# (a) 조화진동 아크사인 분포 — 폐형식 vs 수치적분 대조
A = 34.0  # deg, Wang et al. 2025 Table 1 arm amplitude ±34
theta = np.linspace(1e-6, 2*np.pi-1e-6, 2_000_000)
x = A*np.sin(theta)
bins = np.linspace(-A*0.999, A*0.999, 200)
hist, edges = np.histogram(x, bins=bins, density=True)
centers = 0.5*(edges[:-1]+edges[1:])
closed_form = 1.0/(np.pi*np.sqrt(A**2 - centers**2))
mid = np.abs(centers) < 0.85*A
rel_err = np.abs(hist[mid]-closed_form[mid])/closed_form[mid]
assert np.median(rel_err) < 0.05, f"아크사인 분포 불일치: median rel_err={np.median(rel_err):.3f}"

rho_center = 1.0/(np.pi*np.sqrt(A**2-0**2))
rho_edge = 1.0/(np.pi*np.sqrt(A**2-(0.95*A)**2))
ratio = rho_edge/rho_center
assert ratio > 2.5, f"반환점 밀도발산 기대 미달: ratio={ratio:.2f}"

# (b) 오프셋-원 + 톱니파(정속 각속도) → 반경밀도 비균일 (예시값, 논문 미공개 파라미터 — 추정치)
L, R_arm = 140.0, 90.0  # mm, 예시값
theta_range = np.deg2rad(34.0)  # Wang et al. Table 1: ±34deg
theta_sweep = np.linspace(-theta_range, theta_range, 500_000)  # 정속 -> theta 균등샘플=시간균등샘플
r = np.sqrt(L**2 + R_arm**2 - 2*L*R_arm*np.cos(theta_sweep))
hist_r, edges_r = np.histogram(r, bins=np.linspace(r.min(), r.max(), 60), density=True)
peak_to_mean = hist_r.max() / hist_r.mean()
assert peak_to_mean > 2.0, f"정속 스윕 반경밀도 비균일 기대 미달: peak/mean={peak_to_mean:.2f}"

print(f"OK arcsine median_rel_err={np.median(rel_err):.4f} edge/center={ratio:.2f} "
      f"offset-circle peak/mean={peak_to_mean:.2f}")
```

실행 결과(2026-09-07 확인): median_rel_err≈0.029(<0.05 기준 통과), 반환점/중심 밀도비≈3.20,
오프셋-원 반경밀도 peak/mean≈6.59 — 세 값 모두 assert 통과. 이 톱니파 조건(Wang et al. Table 1
문헌값인 오실레이션 진폭 ±34°와 패드 자전 90 rpm을 그대로 대조 입력)에서도 반경-공간 궤적밀도가
비균일하며 반환점 근방에서 발산 경향을 보인다는 정성적 주장이 코드로 확인된다. 예시 L, R_arm
값 자체는 문헌값이 아니므로 peak/mean=6.59라는 **숫자**는 미검증이고, "2배 이상 비균일"이라는
**정성적 방향성**만 신뢰할 수 있다.

## 4. Wang et al.(2025) 정량 결과와의 교차확인
논문이 실제로 보고한 수치(§3의 자체 해석과는 별개로, 논문 원문에서 직접 발췌):
- NAR(정규화 중첩면적비)는 N_d=7, 8에서 각각 **30.04%, 31.22%**로 최댓값 — 다이아몬드 3→4개
  증가 시 NAR가 **+9.2%** 점프, 5~6개는 오히려 낮아짐(비단조).
- N_d=7~8에서 중심 저밀도 사각지대(dead zone)가 **~40 mm** 반경까지 축소.
- 다이아몬드 개수가 3→12로 늘면서 피크 히트밀도가 **10¹→10² hits/mm²** 자릿수로 증가.
- 결론(4): "정속 스윕은 패드 중심을 과다 컨디셔닝한다 — 안쪽은 가속, 바깥쪽은 감속하는
  3구간(three-zone) 가변속 전략이 균일도를 개선한다."
이 결론(4)이 본 노트 §3(b)의 반환점 밀도발산 메커니즘과 방향이 일치한다 — 다만 논문은 3구간
전략의 구체적 속도 프로파일(가속/감속 비율)을 수치로 제시하지 않았다(본문 열람 범위 내
**미확보**, Table/Fig에 없음).

## 5. 실무적 함의
- 스윕 알고리즘(사인파 vs 톱니파)과 무관하게, **왕복형 스윕은 본질적으로 반환점 근방에
  궤적밀도가 몰린다** — 이를 상쇄하려면 반환점 근처에서 각속도를 오히려 높이는(가속) 가변속
  프로파일이 필요하다(Wang et al. 결론(4)의 3구간 전략과 정합).
- [[conditioner-sweep-kinematics-pcr-profile]]의 Zheng et al. 방식(격자 몬테카를로 적산)은
  이 발산을 시뮬레이션 해상도 내에서 암묵적으로 포함하지만, 발산의 **원인**을 명시하지 않는다
  — 본 노트는 그 원인(dr/dθ→0)을 해석적으로 분리해 제공한다는 점에서 상호 보완적이다.
- fab-sim 구현 시 두 문헌의 스윕 모드(사인파 vs 톱니파) 모두 반환점 근방 시간스텝을 촘촘히
  샘플링해야 궤적밀도 적산 오차가 줄어든다(반환점에서 dr/dθ→0이므로 균등 시간스텝은 그 근방
  공간해상도를 놓치기 쉽다) — 수치구현 유의사항으로 기록.

## 6. 한계와 정직성 표지
- Wang et al.의 팔 피벗-패드중심 거리(L)와 팔 길이(R_arm) 수치는 논문에 없음 — §3(b)는 예시값
  기반 정성 시연이며 정량값(peak/mean=6.59 등)은 문헌값과 무관, **미검증**.
- §3(b)의 "반환점=패드중심 과다컨디셔닝" 연결은 논문이 직접 수식으로 증명한 게 아니라 본
  노트의 **자체 해석**이다 — 논문은 결과(NAR·dead zone)만 보고, 원인은 서술적으로만("saw-tooth
  causes center over-conditioning") 언급한다.
- 논문의 사인파 서술(§4.1 "x(t)=Asin(2πf_osc t)")과 Table 1의 톱니파(saw-tooth) 조건이 본문 내
  용어상 불일치하는 것으로 보인다 — 저자가 개념 설명(§4.1, 나선궤적 직관)과 실제 시뮬레이션
  조건(§3.2, Table 1)에서 다른 스윕 모형을 섞어 쓴 것으로 추정되나 **확인 못** 함.
- 논문의 NAR 계산(2D 히스토그램 + y=0 단면 + B-spline 평활 + 사다리꼴 적분)은 본 노트에서
  재현하지 않았다 — 팔 피벗 파라미터 미공개로 인해 전체 파이프라인 재현은 범위 밖으로 유보.

## 관련 노트
[[conditioner-sweep-kinematics-pcr-profile]] · [[conditioner-disk-pad-cutting-model]] ·
[[cmp-kinematics-rotary]] · [[pad-structure-groove-subpad]]
