<!-- V2-SECTION: R3-pad | 분배완료 2026-09-08 | 근거: groove, subpad, 패드 | 정본: ARCHITECTURE-V2.md §3 -->
# GW 모델: 명목압력 → 분리거리(d) → 국소(실접촉) 압력분포

> pad-mechanic Lv2-2. 선행: [[hertz-gw-contact-mechanics]], [[pad-structure-groove-subpad]]. sim 구현: `sim/tier2_physics/gw_pressure_solve.py`.

## 1. 문제 설정
GW 모델(지수분포 asperity 높이)에서 명목압력 P(=W/A_n, 웨이퍼가 패드를 누르는 하중/명목접촉면적)가
주어지면, 힘 평형 W(d) = P·A_n 을 만족하는 분리거리 d를 구해야 실접촉면적 A_r(d), 접촉점수 n(d),
그리고 asperity 1개당 평균 실접촉압력 p_r = W/A_r 를 계산할 수 있다. `gw_contact.py`(Lv2-1)는
d를 입력으로 받는 순방향 계산만 했고, "P를 알 때 d는?"이라는 역문제가 이번 단원의 핵심이다.

W(d)는 d의 단조감소함수(d 커질수록 접촉 asperity 수↓)이므로 이분법/Brent법으로 유일해를 구할 수 있다.

## 2. 핵심 결과: 평균 실접촉압력은 명목압력과 무관한 상수
GW 1966 원논문의 가장 유명한 결론(2차 출처로 교차검증, §3 참조): asperity 높이분포가
지수분포(또는 그에 가까운 분포)일 때, **실접촉면적 A_r은 하중 W(=명목압력 P×A_n)에 정확히
선형 비례**한다 (Lv2-1에서 폐형식/수치적분으로 이미 확인, 오차 8.6e-6). 이는 즉시 다음을
함의한다:

  p_r_mean = W / A_r = 1 / (A_r/W) = 상수 (E*, R, beta에만 의존, P와 무관)

즉 명목압력을 올려도 개별 asperity가 받는 평균 압입 응력(=실접촉압력)은 거의 변하지 않고,
**대신 접촉하는 asperity의 개수(n_contacts)가 늘어나 총 하중을 감당한다.** 이것이 CMP에서
Preston 상수 Kp가 (좁은 압력범위에서) 압력에 무관한 상수로 잘 맞는 미시적 근거 중 하나로
해석될 수 있다 — Preston 식 MRR=Kp·P·V의 선형성은 "압력이 개별 입자 압입 강도를 선형으로
올려서"가 아니라 "압력이 활성 접촉점 개수를 선형으로 늘려서"라는 그림과 더 잘 맞는다
(Luo-Dornfeld 2001/2004 계열 문헌의 표준 해석, [[hertz-gw-contact-mechanics]] §5 예비 논의 확장).

⚠️ 주의: 이 결과는 순수 탄성 Hertz + 지수분포 가정 하에서만 엄밀하다. 실제 패드는 소성변형
영역일 가능성이 Lv2-1 EXAMS Q3에서 psi≈4.9로 시사됐고(미검증 H값 기반), 소성 지배 영역에서는
GW의 고전적 결과가 "실접촉압력 ≈ 재료 경도 H로 수렴(하중 무관)"이라는 형태로 바뀐다(Bowden &
Tabor 소성접촉 이론, 2차 출처: tribonet.org GW wiki 요약 — "실접촉면적은 대체로 재료 경도로
결정되는 압력 하에서 하중에 비례" 취지, 접근 제약으로 원문 미확보 상태라 취지만 인용, 미검증).
탄성/소성 어느 쪽이든 **"평균 실접촉압력이 명목압력과 거의 무관한 상수로 수렴한다"는 정성적
결론 자체는 두 극한에서 공통**이라는 점이 본 단원의 핵심 수확이다.

## 3. Yang et al. 2024 MRR 식과의 연결 (출처: PMC11051262, Micromachines/유사 오픈저널 2024,
"asperity height/radius wear + PDF 기반 수정 GW 모델")
이 논문은 CMP MRR을 다음과 같이 3개 접촉 상태(탄성 Fe·탄소성 Fep·완전소성 Fp)의 가중합으로
쓴다(원문 Eq.20, 표기 단순화):

  MRR(t) = Kp · V / A_norm · [ Fe(t)·ne(t)·Ae(t) + Fep(t)·nep(t)·Ap(t) + Fp(t)·np(t)·Ap(t) ]

여기서 n_x(t)는 각 접촉모드의 개수, A_x(t)는 asperity 반경 분포에서 온 접촉면적, F_x(t)는
접촉력 — 즉 **"압력 → 접촉점 개수 n(d)의 증가"가 MRR 증가의 1차 경로**라는 본 노트 §2의
결론과 정확히 같은 구조다. 이 논문은 추가로 asperity 높이·반경 분포 자체가 CMP 진행에 따라
마모로 변한다는 시간의존성을 넣지만(→ Lv3-1 패드 마모·glazing 단원의 선행지식), 이번 Lv2-2
sanity check에서는 시간축 없이 정적 GW 힘평형만 구현한다(스코프 제한, 명시).

## 4. 오늘 구현·검증 요약 (수치)
`gw_pressure_solve.py`: Lv2-1 `gw_numeric()`을 재사용해 W(d)=P·A_n을 Brent법으로 d에 대해
풀고, 3개 서로 다른 명목압력(14/48/96 kPa — Lai 2001 실험조건 오더 재사용, [[cmp-kinematics-rotary]]
와 동일 실험조건 재사용해 지식 간 일관성 확보)에서 실접촉압력 p_r=W/A_r을 계산한다. self-test에서
p_r가 P에 따라 (14→48→96 kPa, 6.9배 압력 변화 구간에서) 상대편차 <0.1% 이내로 거의 불변임을
확인 — §2의 이론적 결론을 수치로 재현한 것. 동시에 접촉점수 n(d)는 압력에 거의 선형 비례함을
함께 출력해 "압력이 개수를 늘린다"는 그림을 정량 확인한다.

```python verify
# 2026-09-08 학습총괄 부채상환 — sim/tier2_physics/gw_pressure_solve.py 실제 실행 재현
import sys, os
sys.path.insert(0, os.path.expanduser('~/fab-sim/sim/tier2_physics'))
from gw_pressure_solve import local_contact_state

beta = 1.0 / 0.3e-6
eta = 200000 / 1e-4
A_n = 1e-4
E_star = 1e9
R = 5e-6

pressures_pa = [14e3, 48e3, 96e3]   # Lai 2001 오더 재사용 (본문 §4)
results = {P: local_contact_state(P, A_n, beta, eta, E_star, R) for P in pressures_pa}

p_r_vals = [results[P]['p_r_mean'] for P in pressures_pa]
n_vals = [results[P]['n_contacts'] for P in pressures_pa]

# 주장 1: 압력이 6.86배(96/14) 변해도 평균 실접촉압력은 상수로 수렴한다.
rel_spread = (max(p_r_vals) - min(p_r_vals)) / (sum(p_r_vals) / 3)
assert rel_spread < 1e-6, f"p_r 상대편차 {rel_spread:.2e} — 상수 수렴 실패"
# 실측: 세 압력 모두 p_r_mean = 138,196,469.9 Pa (≈138.2 MPa)로 완전히 동일
# (부동소수 오차 수준 <1e-9) — 노트 본문의 "<0.1% 이내" 주장은 과소서술이었고
# 실제로는 이 파라미터 세트에서 상대편차가 사실상 0(수치오차 이하)이다.

# 주장 2: 접촉점수 n(d)는 압력에 거의 선형 비례한다.
ratio_P = pressures_pa[2] / pressures_pa[0]           # 96/14 = 6.857
ratio_n = n_vals[2] / n_vals[0]                        # 실측
assert abs(ratio_n - ratio_P) / ratio_P < 0.01, (
    f"선형비례 이탈 {ratio_n:.4f} vs 압력비 {ratio_P:.4f}")
# 실측: ratio_P=6.857, ratio_n=6.858 (오차 0.02%) — "압력이 접촉점 개수를
# 선형으로 늘린다"는 §2 결론이 GW 모델 자체의 수치해로 정량 재현됨.

print(f"p_r_mean(14/48/96kPa) = {p_r_vals} Pa (상대편차 {rel_spread:.2e})")
print(f"n_contacts(14/48/96kPa) = {n_vals}")
print(f"압력비 {ratio_P:.4f} vs 접촉점수비 {ratio_n:.4f}")
```

**재현 결과 (2026-09-08 실행):** p_r_mean = 138,196,469.9 Pa (138.2 MPa)로 14/48/96 kPa
전 구간에서 부동소수 오차 이내로 완전히 동일 — 원래 노트가 "<0.1% 이내"로 보수적으로
서술했던 것보다 훨씬 강하게(사실상 정확히) 상수 수렴을 확인. n_contacts는 2149.76 →
7370.61 → 14741.21로, 압력비 6.857배에 대해 접촉점수비 6.858배(오차 0.02%)로 거의
완전한 선형 비례. §2의 "압력 → 접촉점 개수 증가"라는 정성 결론이 코드 실행으로
정량 재현됨(단, 이는 GW 이론식의 자기재현이지 Greenwood & Williamson(1966) 원논문
수치와의 직접 대조는 아니다 — 원논문은 여전히 paywall 미확보, §5 참조).

## 5. 출처
- Yang, J. et al. (2024) "Prediction of Material Removal Rate in Chemical Mechanical Planarization
  Considering the Pad Asperity Distribution", 오픈액세스, PMC11051262
  (https://pmc.ncbi.nlm.nih.gov/articles/PMC11051262/) — Eq.20 MRR 3-모드 가중합, GW+PDF 시간의존
  마모 모델.
- Greenwood, J.A. & Williamson, J.B.P. (1966) Proc. R. Soc. A 295 — 원논문 paywall, 미확보.
  A_r∝W(하중무관 비율)은 본 지식노트 계보에서 [[hertz-gw-contact-mechanics]] Lv2-1 폐형식
  유도로 대체 검증(수치오차 8.6e-6) — 원논문 직접 인용 아님, 명시.
- tribonet.org GW wiki 요약(검색결과 스니펫 수준 확보, 페이지 본문 크롤링 실패 — "실접촉면적은
  하중에 비례하고 명목접촉면적과 무관"이라는 취지만 재확인용으로 인용, 미검증 수준).
- 소성접촉 하 실접촉압력→경도 수렴: Bowden & Tabor 고전 결과, 2차 출처 취지 인용만(원문 미확보,
  미검증).
- 압력조건(14/48/96 kPa)은 [[cmp-kinematics-rotary]]에서 이미 채택한 Lai(MIT, 2001) 실험범위와
  일관되게 오더만 재사용(96kPa은 Lai 상한 근방으로 임의 추가, 데이터 자체는 재사용 아님).
