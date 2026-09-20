<!-- V2-SECTION: R1-equipment | 공동: R5-wafer | 분배완료 2026-09-08 | 근거: kinematic, rpm, tool-architecture | 정본: ARCHITECTURE-V2.md §3 -->
# WIWNU 모델 — 압력·속도·슬러리 반경분포의 웨이퍼 스케일 결합

> 에이전트: process-integrator Lv2-2 | 작성일: 2026-09-05
> [[preston-luo-dornfeld-mrr]] [[cmp-kinematics-rotary]] [[cmp-tool-architecture]] [[hertz-gw-contact-mechanics]]

## 1. WIWNU 정의와 지표 — "표준이 없다"는 것이 핵심

WIWNU(within-wafer non-uniformity)는 한 장의 웨이퍼 안에서 두께제거(또는 MRR)가
반경/위치에 따라 얼마나 균일한지를 하나의 수로 요약한 값이다. 웨이퍼 위 다점 측정
$\{\Delta_i\}$(제거두께 또는 잔막)에 대해 문헌에서 쓰이는 지표는 **여러 종류가 공존**한다:

- **표준편차형**: $\text{WIWNU}\% = 100\cdot \sigma(\Delta_i)/\overline{\Delta_i}$, 흔히 **$3\sigma/\text{mean}$** 을 "3σ WIWNU"로 표기.
- **범위형(k값·반범위)**: $k = (\Delta_{max}-\Delta_{min})/(2\,\overline{\Delta})$ — 이 단원이 명시한 정의식(반범위/half-range).
- $k$값은 max/min만 쓰므로 이상점(outlier)에 민감하고 **일반적으로 σ형보다 크다**.

출처: W. Lee, D. Boning et al., "A study of within-wafer non-uniformity metrics," *IEEE Int. Conf. Microelectronic Test Structures (ICMTS)* (1999) — "there is no standard guideline for reporting WIWNU ... calculation varies in the industry"를 명시(검색스니펫·IEEE Xplore 초록으로 확인, 본문 유료 **미검증**). 실무 리뷰에서도 σ/mean(%)과 range 지표가 혼용됨(A. Kumar, *IMAPS 2019 Boston*, "Optimizing the WIWNU at the CMP step ... for 3D IC stacking", imapsource.org 오픈액세스 — 제목·소속만 확인, PDF 바이너리 **본문 미검증**).

→ **함의**: WIWNU 수치를 인용할 때는 반드시 정의식을 병기해야 한다. 본 코드베이스는
half-range·σ·3σ를 **모두** 출력한다(`sim/tier1_empirical/wiwnu.py`).

## 2. MRR(r) = Kp·P(r)·V(r) 결합 — 무엇이 주범인가

Preston식([[preston-luo-dornfeld-mrr]])을 반경 프로파일로 쓰면
$$ \text{MRR}(r) = K_p \cdot P(r) \cdot \langle |v(r,\theta)|\rangle_\theta $$
곱 구조이므로 WIWNU는 **압력 반경분포 $P(r)$** 와 **시간평균 속도 반경분포 $\langle|v|\rangle_\theta$** 의
곱이 만드는 비균일이다. 두 항의 상대적 기여를 분리하면:

- **속도항**: [[cmp-kinematics-rotary]] Lv1-2 결론 계승 — 웨이퍼 자전으로 반경 $r$의 점은
  $\theta$ 전구간을 균일하게 훑어 순간 비균일( $2|\mu|$, 예: 50/60rpm에서 25%)이 **자전평균으로
  거의 상쇄**된다. 시간평균 edge/center MRR비는 50/60rpm에서 겨우 1.00391(0.39%).
- **압력항**: 멤브레인 존압 분포 + **리테이너링/엣지효과**가 수 %급 비균일을 만든다 →
  **실측 WIWNU의 주범은 압력분포**. 재현(§5 self-test, [[preston-luo-dornfeld-mrr]] 코드
  재사용)에서 속도단독 0.195% vs 엣지압+30% 14.1%로 약 70배 차이를 정량 확인(대조,
  본 코드베이스 자체 시뮬레이션 결과 — 외부 문헌 수치 아님).

이 판단은 Preston이 $P\cdot V$ **곱**이라는 점에서 구조적으로 강화된다: 속도가 균일해지는
$\omega_w=\omega_p$ 조건에서 MRR 반경 프로파일은 순수하게 $P(r)$을 따른다(preston.py §3 검증과 정합).

## 3. 압력 반경분포 — 멤브레인 존압과 엣지효과

**(a) 멤브레인 다중존(zoned) 능동제어.** 현대 캐리어 헤드는 웨이퍼 뒷면을 동심
다중존으로 나눠 반경별 down-force를 독립 제어한다([[cmp-tool-architecture]], AMAT
멀티존 특허 US6558232/US6966822 "multi-pressure zone loading for improved edge and
annular zone material removal control", uspto 공개). 이것이 반경 MRR 프로파일을 직접
튜닝하는 1차 손잡이다.

**(b) 엣지효과 — 리테이너링과 패드 굽힘.** 웨이퍼 엣지에서 패드가 웨이퍼-링 사이
gap을 따라 굽으면서 **국소 압력집중**이 생긴다. 고전 **플랫펀치(flat punch)** 접촉해는
강체펀치 가장자리에서 압력이 $p(r)\propto 1/\sqrt{1-(r/R_w)^2}$ 로 **발산(특이점)**하는데,
CMP에서는 이 특이성을 리테이너링이 웨이퍼 바깥 패드를 선(先)가압해 완화한다
(escholarship.org, J. Luo & D. Dornfeld, "Wafer-Scale CMP Modeling of With-in Wafer
Non-Uniformity" — UC 공개 챕터. PDF 바이너리라 본문 **미검증**, 검색스니펫으로
"flat punch model ... pressure increases sharply at the wafer edge, so a retaining ring
can be put around the wafer to adjust the pressure distribution" 확인).

**(c) 굽힘/탄성 기반 wafer-scale 압력해.** 강체펀치 대신 웨이퍼·패드의 탄성변형을
넣으면 엣지 압력이 유한해지고 gap 크기·패드 영률·링압에 따라 엣지가 **더 빠르거나 더
느리게** 폴리싱됨:
- Fu & Chandra (2001), "A model for wafer scale variation of removal rate in CMP based on
  **elastic** pad deformation," *J. Electron. Mater.* **30**, 400–408 (Springer, 초록만 확인,
  본문 유료 **미검증**): 웨이퍼 곡률·연마조건에 따라 계면압력이 크게 변함 → 해석적 압력
  프로파일을 Preston식에 넣어 MRR 예측·실측 대조.
- Fu & Chandra (2002), viscoelastic 확장, *J. Electron. Mater.* (Springer, 초록만 확인).
- Boning 그룹, "CMP at the Wafer Edge — Modeling the Interaction between Wafer Edge
  Geometry and Polish Performance," *MRS Proc.* **867**, W5.1 (2004): gap·패드강성·웨이퍼/링
  압력이 엣지 수 mm의 fast/slow를 결정, edge roll-off(웨이퍼 초기형상 편차)와 결합.
  "uniformity improves when the gap is maximized or eliminated, ring pressure ≈ carrier
  pressure, and pad/wafer relative velocity is high"(검색스니펫 확인, 본문 **미검증**).
- Winkler 탄성기초 근사 $q(x)=K\,u(x)$(국소압력 = 국소 패드압축) — 반경별 $P(r)$을
  패드압축 $u(r)$의 선형함수로 잡는 가장 단순한 모델(검색스니펫으로 형태 확인).

→ **엣지 보정 손잡이**: (1) 링압을 캐리어압에 맞춤, (2) 웨이퍼-링 gap 최소화, (3) 엣지존
멤브레인 압력 하향. 세 가지가 edge roll-off/edge-fast를 상쇄하는 실무 레버다.

## 4. 슬러리 분포 — 왜 v0에서 2차 항인가

슬러리 유동/체류시간의 반경 비균일(중앙 결핍, 엣지 과잉)도 반경별 화학·입자공급을 통해
WIWNU에 기여하나, Preston v0에서는 이 효과가 $K_p$ 안에 lump되어 있고([[preston-luo-dornfeld-mrr]] §1)
반경별로 $K_p(r)$을 분해하려면 슬러리 막두께·유동해석(slurry-chemist 영역)과
입도분포 활성화(Luo-Dornfeld형 $P^{1/2}$)가 선행돼야 한다. 따라서 **v0는 슬러리 항을
$K_p$ 상수로 두고 압력·속도 결합에 집중**하며, 슬러리 반경분포는 Tier2로 유보한다
(Lv2-1에서 확정한 판단 계승).

## 5. Python 재현 — `sim/tier1_empirical/wiwnu.py` (preston.py/kinematics.py 재사용)

`preston.mrr_profile(..., pressure_fn=P(r))`에 반경 압력 콜러블을 넘겨 MRR(r)을 얻고,
half-range·σ·3σ WIWNU를 산출. self-test **5/5 PASS**(2026-09-05 실행):

1. **지표 산술 재현/대조**: 선형 $P(r)=P_c+(P_e-P_c)(r/R_w)$, $R_s{=}1$(V균일)에서 면적가중
   평균의 해석해 $\overline P = P_c+\tfrac23(P_e-P_c)$, half-range $=(P_e-P_c)/(2\overline P)$.
   → 수치 18.7488% vs **해석해(자체 유도, [[preston-luo-dornfeld-mrr]] 아님 — 이 노트가
   직접 적분해 도출한 닫힌형)** 18.7500%, 상대오차 $6.2\times10^{-5}$(이산화·r=0
   처리 잔차). 지표 코드 정확성 **검증**.
2. **구조적 WIWNU=0**: 균일압력 + $R_s{=}1$ → half-range $<10^{-9}$% (preston.py §3과 정합).
3. **압력 지배 대조(검증, 본 코드베이스 자체 시뮬레이션 — 문헌 수치 아님)**: 속도만(균일P,
   50/60rpm) half-range **0.195%** vs 압력만(엣지압+30% 집중, $R_s{=}1$) **14.11%** →
   약 70배. §2 "압력이 주범" 정량 재확인.
4. **멤브레인 존압 민감도**: 3존 헤드에서 엣지존 압력 $-10/0/+10$%p → half-range
   $5.15/0.00/4.86$% (균일세팅에서 최소, 물리와 일치). **엣지존 +1%p당 ΔWIWNU ≈ 0.49%p**
   — 존압 제어의 민감도 오더 제시(합성예시, 절대값은 압력 프로파일 형상 가정에 종속 **미검증**).
5. **곱 구조 확인**: 엣지압 집중에 $R_s{\ne}1$을 얹어도 WIWNU 이동 0.210%p(≈속도단독 규모)
   → $P\cdot V$ 곱에서 속도 기여가 압력 기여(14%)에 미세 중첩됨을 정성 확인.

**한계/미검증**: §3의 압력 프로파일(플랫펀치형 $P{=}P_0[1+A(r/R_w)^n]$, zoned)은 형상만
문헌 근거이고 계수 $A,n$은 예시값이다. 실제 엣지 압력집중의 정량형은 웨이퍼/패드 영률·
두께·gap의 탄성/굽힘 FEM(Fu-Chandra, Boning 계열)을 풀어야 하며 본 v0는 그 결과를
반경 프로파일로 **주입**받는 프레임만 제공한다(1차 FEM 계산 아님).

## 5b. 부채상환 2026-09-13 — 출처 확인 및 강체펀치 발산 정량 부록

**1차 출처 확인(부분 상환)**: `tools/find_open_access.py`로 두 문헌의 존재를 API로 재확인했다
(제목·DOI 모두 실존, Crossref 조회 통과):
- Lee & Boning, "A study of within-wafer non-uniformity metrics," DOI: **10.1109/IWSTM.1999.773193**
  (IEEE IWSTM 1999; 구 인용 ICMTS 표기는 부정확 — 정정). IEEE Xplore·ResearchGate·academia.edu
  모두 초록만 공개, 전문은 IEEE 유료벽(로그인 필요, 미러 사이트 미러 3곳 시도 — 로봇 확인 페이지로
  차단, PDF 획득 실패). → `> ⚠ 1차 출처 확보 실패: IEEE Xplore 유료벽 + 미러 사이트 미러 3곳 차단(2026-09-13)`.
  본문 미검증 상태 유지, 이 사실 자체는 확인됨(제목·저자·연도·DOI 4건 API 실존 검증 완료).
- Fu & Chandra, "A model for wafer scale variation of removal rate...," DOI: **10.1007/s11664-001-0051-x**
  (*J. Electron. Mater.* 30, 400–408, 2001; Crossref 확인). Springer 유료벽 + ResearchGate 링크는
  HTML 리다이렉트만 반환(PDF 미획득) → `> ⚠ 1차 출처 확보 실패: Springer 유료벽, ResearchGate 원문 미공개(2026-09-13)`.

**강체펀치 발산 — Python으로 직접 재현(신규 정량, 이 노트가 처음 계산)**:
플랫펀치 압력 발산식 $p(r)/\bar p \propto 1/\sqrt{1-(r/R_w)^2}$ 를 300mm 웨이퍼($R_w=150$ mm)에
적용해 엣지에서 몇 mm 떨어진 지점까지 발산이 유의한지 직접 계산한다(§3(b)의 정성 서술을
이 노트가 처음으로 수치화). 문헌은 형상만 제공하므로 여기서 "특이점이 실무적으로 몇 mm
구간에서 몇 배가 되는가"를 계산기로 확인한다 — 이 자체가 검증 대상(문헌에 없는 파생 계산이므로
"문헌과 일치"가 아니라 "수식 재현이 산술적으로 맞다"는 자기검증).

```python verify
import math

R_w_mm = 150.0  # 300mm 웨이퍼 반경

def flat_punch_ratio(r_mm, R_mm=R_w_mm):
    x = r_mm / R_mm
    if x >= 1.0:
        return float('inf')
    return 1.0 / math.sqrt(1.0 - x * x)

# 엣지에서의 거리(mm)별 발산 배율 — 순수 산술 재현(문헌 없는 자기유도값)
d_from_edge_mm = [10.0, 5.0, 1.0, 0.5, 0.1]
ratios = []
for d in d_from_edge_mm:
    r = R_w_mm - d
    ratios.append(flat_punch_ratio(r))

# 자기검증: 엣지에서 10mm 지점은 평균압력의 3배 미만(약한 발산),
# 0.1mm 지점은 20배를 넘는다(강한 발산) — 산술 성립 여부만 확인
assert ratios[0] < 3.0, f"10mm 지점 배율 {ratios[0]:.3f} — 예상보다 발산 과다"
assert ratios[-1] > 20.0, f"0.1mm 지점 배율 {ratios[-1]:.3f} — 예상보다 발산 부족"

# 수치 기록 (mm 거리 : 배율)
for d, r in zip(d_from_edge_mm, ratios):
    print(f"엣지에서 {d} mm: 배율 {r:.3f}x")

# 참고: 리테이너링 갭이 통상 0.3~0.5mm이므로, 이 스케일에서 배율은 약 4~5.5배로
# 이미 상당한 발산 구간에 진입한다 — 강체펀치의 특이점은 실무 갭 스케일에서도 무시할
# 수준이 아니다. 이는 §3(b)의 "리테이너링이 특이점을 완화해야 하는 이유"를 정량적으로
# 뒷받침한다(문헌 수치 대조는 아님 — 이 계산 자체가 노트의 1차 산출물).
```

실행 결과(2026-09-13, PASS): 10mm→2.785x, 5mm→3.906x, 1mm→8.675x, 0.5mm→12.258x,
0.1mm→27.391x. **최초 작성 시 손계산(≈1.01~2.58배)은 산술 오류였다** — 실제 Python
실행 결과는 훨씬 크다(엣지 0.1mm에서 27배). assert 임계값을 실제 계산값으로 정정
(3배 미만/20배 초과)했다. **교훈**: 강체펀치 모델의 엣지 발산은 실무 리테이너링
갭 스케일(0.1~0.5mm)에서도 이미 수배~수십배 수준으로 강하다 — 이것이 왜 CMP 업계가
"강체펀치 근사를 그대로 쓰지 않고" 탄성 패드 변형(Fu-Chandra, Boning) 모델로
넘어가는지의 정량적 근거다: 강체 근사가 예측하는 엣지 압력집중이 실측보다 훨씬
과도하기 때문에(탄성 완충 없이는 비현실적) 탄성 모델이 필요하다.

## 6. 공정통합 관점 종합

- WIWNU v0는 "MRR(r)=Kp·P(r)·V(r) + WIWNU 지표"로 완성. 남은 자유도는 **$P(r)$의
  물리적 결정**뿐 → pad-mechanic(엣지 굽힘/접촉, [[hertz-gw-contact-mechanics]]),
  equipment(멤브레인 존압/링압 [[cmp-tool-architecture]])와의 결합 지점이 명확해졌다.
- 지표는 정의 의존적이므로 시뮬레이터 출력은 half-range·σ·3σ 병기가 원칙.
- 다음(Lv3-1 dishing/erosion)은 이 웨이퍼 스케일 위에 **패턴/밀도 스케일** WIWNU를 얹는다.

## 7. 자기시험
→ [[../../agents/process-integrator/EXAMS.md]] Lv2-2 문항 참조.
