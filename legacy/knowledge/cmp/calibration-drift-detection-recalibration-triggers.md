# 캘리브레이션 드리프트 감지 — 소모품 로트·패드 교체·PM 후 재보정 트리거

> cmp-calibrator Lv3-1. [[uq-prediction-interval-coverage-extrapolation-warning]](예측구간·외삽 경고, 같은 잔차분해 틀을 공유),
> [[pad-wear-glazing-mrr-decay]](패드 마모의 물리 기전 — 여기서는 재서술하지 않고 트리거 신호로만 재사용),
> [[conditioner-sweep-kinematics-pcr-profile]](Γ 컨디셔닝 부하의 정의) 상호링크.
> scope.py --agent cmp-calibrator --queries 는 상위 커리큘럼(베이지안 캘리브레이션) 기준 검색어만
> 주어 Lv3-1(EWMA/CUSUM 관리도)에는 WebSearch로 별도 검색어를 구성했다.

## 문헌

1. **Hsu, M.-C. & Chang, Y.-J. (2026)**, "A Data-Driven EWMA-KNN Run-to-Run Controller for
   Drift-Dominant Processes with Application to Chemical Mechanical Planarization", *Processes*,
   14(17), 2714. DOI: 10.3390/pr14172714. (MDPI 오픈액세스, 전문 15쪽 fitz 판독 — 이하 "HC2026".
   근거등급 **E2**: CMP 시뮬레이션 실험 + 폐형식 BIBO 안정성 증명.)
2. **Son, J. & Lee, H. (2021)**, "Contact-Area-Changeable CMP Conditioning for Enhancing Pad
   Lifetime", *Applied Sciences*, 11(8), 3521. DOI: 10.3390/app11083521. (MDPI 오픈액세스, 전문
   15쪽 fitz 판독 — 이하 "SL2021". **E2**: 200mm SiO2 웨이퍼 실측 20시간 연속실험.)
3. **Polunchenko, A. S., Sokolov, G. & Tartakovsky, A. G. (2014)**, "Optimal Design and Analysis
   of the Exponentially Weighted Moving Average Chart for Exponential Data", *Sri Lankan Journal
   of Applied Statistics*, 15(2), 55–82. arXiv:1307.7126v3 전문 27쪽 fitz 판독 — 이하 "PST2014".
   **E2**: 적분방정식 폐형식 유도 + 수치 사례연구(Table 4.1/4.2). 이 논문이 **Lucas, J. M. &
   Saccucci, M. S. (1990)**, "Exponentially Weighted Moving Average Control Schemes: Properties
   and Enhancements", *Technometrics*, 32(1), 1–12, DOI: 10.1080/00401706.1990.10484583 를
   EWMA 관리도의 원조 ARL 문헌으로 인용하는 것을 참고문헌 목록에서 확인했다 — Lucas & Saccucci
   (1990) 원문 자체는 Technometrics 유료·미러 실패로 **미확보(2차 인용만)**, 이 노트의 수치 검증은
   전부 PST2014의 폐형식 식과 표를 직접 재현한 것이다.
4. **NIST/SEMATECH (연도 미상, 상시개정)**, *e-Handbook of Statistical Methods*, §6.3.2.4(EWMA)·
   §6.3.2.3(CUSUM). https://www.itl.nist.gov/div898/handbook/pmc/section3/pmc324.htm ,
   https://www.itl.nist.gov/div898/handbook/pmc/section3/pmc323.htm . 미국 정부 공개문서
   (저자 개인 논문이 아니므로 근거등급 표기 대상 아님) — 관리도 정의·설계식의 표준 출처로만 인용.

## 1. 드리프트의 물리적 원인축

CMP 캘리브레이션(series_scale 등으로 고정한 Kp 배율·형상)이 무효가 되는 원인은 성격이 다른
네 가지로 나뉜다. 이 노트는 "언제 재보정을 트리거할지"가 목적이므로 각 물리 기전 자체의 유도는
기존 노트로 넘기고, **재보정 신호로 쓸 수 있는 관측 가능한 궤적**만 정리한다.

**① 패드 마모/교체(break-in 곡선).** 패드 asperity가 컨디셔닝 없이는 단조 평탄화(glazing)된다는
기전은 [[pad-wear-glazing-mrr-decay]](Shi & Ring 2010)가 이미 다뤘다. 이 노트에서 새로 쓰는 것은
**컨디셔닝을 계속해도 드리프트가 나는 경우**다. SL2021은 종래식(Case I, 디스크 전면 접촉) 컨디셔닝을
20시간까지 연속 수행하며 매 1~3시간마다 SiO2 웨이퍼 CMP(60초)로 MRR을 실측했다(§2.3, Table 4).
결과(§3.2, Fig. 15): Case I은 **12시간까지 MRR이 거의 일정(401→ 대략 유지)하다가 12시간 이후 급격히
꺾여 16시간 시점 221.0 nm/min까지 떨어짐 — 16시간 누적 기준 44.9% 감소**(401.3→221.0 nm/min).
WIWNU도 12시간까지 3% 이내였다가 16시간 시점 약 8.8%까지 급등(Fig. 16). 즉 **드리프트가 선형이
아니라 특정 누적 컨디셔닝 시간(이 실험에서 ≈12h)을 지나면서 변화점(change-point)을 갖는다** —
이 노트 §2가 다루는 변화점 검출 문제가 바로 이 형태의 신호를 겨냥한다. 대조군인 접촉면적 가변형
컨디셔닝(Case II)은 20시간 동안 MRR이 387.7→359.0 nm/min(7.4% 감소)로 완만해, "패드+컨디셔너
조합이 균일 마모를 유지하는 한 드리프트가 느리다"는 것도 같은 데이터로 확인된다.

**② 컨디셔너 디스크 마모.** SL2021 자체는 디스크 마모를 직접 정량화하지 않았고(디스크는 고정,
패드 쪽 마모 프로파일만 측정), FabSim 내부에서는 `sim/factors.py`가 디스크 마모를 Γ(컨디셔닝
부하)와 S(정상상태 패드 조도) 양쪽에 **같은 함수**(`conditioner_pcr_decay`, 시상수 τ=27.4h)로
반영한다고 문서화되어 있다([[conditioner-sweep-kinematics-pcr-profile]] 근거) — 이는 FabSim 내부
설계 문서이며 이 노트가 새로 확보한 1차 문헌은 아니다.

**③ 슬러리 로트 변동(입도분포·pH·산화제 역가).** 이 원인축은 정성적으로는 명백하다(로트마다
입도분포·pH·산화제 농도가 규격 안에서 흔들리면 Preston 배율이 흔들린다는 것은 CMP 슬러리
QC의 일반 상식이다) — 그러나 이번 조사에서 **정량적 1차 문헌은 확보하지 못했다**. WebSearch로
입도분포 QC 관련 자료(HORIBA 응용노트, 특허 등)는 찾았으나 로트 대 로트 변동폭을 수치로 보고한
학술 1차 문헌에는 도달하지 못했다. ⚠ **1차 출처 확보 실패** — 이 축은 트리거 규칙(§3)에서 "일반
변수"로만 다루고 구체 수치는 넣지 않는다.

**④ 툴 PM(캐리어 멤브레인·리테이너링 교체).** 마찬가지로 정성적으로는 소모품 교체 직후 압력
전달 특성(멤브레인 유연성, 리테이너링 마모에 따른 웨이퍼 에지 압력 프로파일)이 바뀐다는 것이
CMP 장비 유지보수의 표준 관행이지만, ⚠ **이번 조사에서 1차 정량 문헌은 확보하지 못했다.** 이
축은 FabSim의 Kp/S/Γ 스칼라 축이 아니라 압력 프로파일 p(r) 쪽(tool-platen-head 에이전트 소관)에
더 가깝다는 점도 §4에서 밝힌다.

HC2026은 ①을 R2R 제어 관점에서 다시 확인한다: CMP 공정을 `y_i = C + A·u_i + ω_i + δ·i`
(식 16, i=런 번호, δ=선형 드리프트 벡터)로 모델링하고, **패드를 50런마다 교체하며 그때마다
레시피와 KNN 오차-보정 데이터베이스를 초기값으로 리셋**하는 실험을 수행했다(§4.4). 5개 패드의
평균 제거율은 1696.15~1699.53 nm/min, 표준편차 22.91~28.79로 패드 교체 후에도 일관된 성능을
유지했고, 평균 제거율의 95% 신뢰구간은 [1696.16, 1699.61]로 좁았다(식 26). 이는 "패드 교체는
드리프트 파라미터(δ, 오차-보정 이력)를 무조건 리셋해야 하는 이벤트"라는 것을 실험으로 보여준다
— 통계적 변화점 검출이 아니라 **결정론적 트리거**(§3의 규칙 C)로 다뤄야 하는 이유다.

## 2. 감지 통계 — EWMA/CUSUM 관리도와 ARL–오경보 트레이드오프

### 2.1 정의

NIST/SEMATECH 핸드북 §6.3.2.4의 EWMA 통계량: `EWMA_t = λ·Y_t + (1-λ)·EWMA_{t-1}`, 관리한계는
점근분산 `σ²_EWMA = (λ/(2-λ))·σ²`을 써서 `UCL/LCL = EWMA_0 ± L·σ·sqrt(λ/(2-λ))`. λ가 작을수록
과거 이력을 길게 누적해(느린 반응, 작은 지속적 이동에 민감) λ가 클수록 최근 관측에 가깝다
(λ=1이면 Shewhart 관리도와 동일 — 이는 HC2026 §2.1(식 2)의 R2R EWMA 추정기와 정확히 같은
재귀식이다: HC2026은 이 통계량을 관리도가 아니라 보정량 계산에 쓴다는 점만 다르다). §6.3.2.3의
CUSUM은 `S_hi(i) = max(0, S_hi(i-1) + x_i - μ0 - k)`, `S_lo(i) = max(0, S_lo(i-1) + μ0 - k - x_i)`
로 누적하고 `h`를 넘으면 이상 판정한다. 설계 지침(§6.3.2.3): 탐지하려는 이동폭 δ의 절반을 k로,
h는 대략 4~5σ로 잡는다.

### 2.2 ARL과 오경보율의 트레이드오프 — PST2014 폐형식 재현

관리도 설계의 핵심 트레이드오프는 "재현율(탐지 지연 ARL₁, delay)"과 "오경보율(허위경보 간 평균
런길이 ARL₀ = γ)"이 같은 손잡이(λ, 관리한계)로 동시에 움직인다는 것이다. PST2014는 지수분포
사전/사후 평균모형(사전 평균 1, 사후 평균 1+θ)에서 한쪽 EWMA 관리도의 ARL·SADD(최악조건 평균
탐지지연)·STADD(정상상태 평균 탐지지연)를 폐형식으로 유도했다(식 3.8, 3.10, Fredholm 적분방정식의
급수해). Table 4.1(θ=0.5, 헤드스타트 z=0)은 오경보 ARL(γ)을 100/1000/10000으로 고정했을 때
최적 (λ, A)가 각각 (0.275, 2.07)/(0.096, 1.79)/(0.049, 1.67)임을 보고한다 — **γ가 커질수록(오경보를
줄일수록) 최적 λ가 작아져야 하고, 그 대가로 SADD(탐지지연)가 17.7→46.5→85.5로 커진다**(같은
표). 이것이 이 절이 다루는 트레이드오프의 수치 그 자체다.

```python verify
# verify(1): PST2014 식(3.8)의 EWMA-지수 관리도 ARL 폐형식을 직접 구현해
# Table 4.1(θ=0.5, z=0)의 (λ, A, γ) 세 쌍을 재현한다. 오경보 ARL이 문헌 설계값과
# 1% 이내로 일치해야 "그 λ,A 조합이 정말 그 오경보율을 낸다"는 주장이 선다.
import math

def arl_ewma_exp(lam, A, z=0.0, nmax=300):
    """PST2014 식(3.8): ARL(z) = 1 + (1/lam) * sum_n (A^n-(az)^n)/n * [n-1]_a! / (n-1)!"""
    alpha = 1.0 - lam
    az = alpha * z
    total = 0.0
    log_qfact = 0.0  # log([n-1]_alpha!) 누적
    for n in range(1, nmax + 1):
        if n >= 2:
            j = n - 1
            qb = (1 - alpha**j) / (1 - alpha)
            log_qfact += math.log(qb)
        log_fact = math.lgamma(n)  # log((n-1)!)
        term = (A**n - az**n) / n * math.exp(log_qfact - log_fact)
        total += term
    return 1.0 + total / lam

# Table 4.1(a) z=0 행, θ=0.5 (ARL은 θ와 무관 — 무변화 상태의 통계량이므로)
cases = [(0.275, 2.07, 100), (0.096, 1.79, 1000), (0.049, 1.67, 10000)]
for lam, A, gamma in cases:
    est = arl_ewma_exp(lam, A, z=0.0)
    rel_err_pct = 100 * (est - gamma) / gamma
    assert abs(rel_err_pct) < 1.5, f"λ={lam}: 문헌 설계 ARL {gamma}와 {rel_err_pct:.2f}% 차이"
    print(f"λ={lam}, A={A}: closed-form ARL={est:.1f} (문헌 목표 γ={gamma}, "
          f"오차 {rel_err_pct:+.2f}%)")
```

```python verify
# verify(2): 위 폐형식이 아니라 실제 EWMA 관리도를 몬테카를로로 시뮬레이션해도
# 같은 (λ, A)에서 같은 오경보 ARL이 나오는지 독립 재현 — 공식 유도 오류를 배제한다.
import numpy as np

def mc_arl(lam, A, z0=0.0, n_reps=60000, seed=0):
    rng = np.random.default_rng(seed)
    Z = np.full(n_reps, z0)
    alive = np.ones(n_reps, dtype=bool)
    t = np.zeros(n_reps, dtype=np.int64)
    for _ in range(20000):
        if not alive.any():
            break
        X = rng.exponential(1.0, size=alive.sum())  # 무변화 상태: 사전평균 1
        Z[alive] = (1 - lam) * Z[alive] + lam * X
        t[alive] += 1
        newly_out = np.zeros(n_reps, dtype=bool)
        newly_out[alive] = Z[alive] >= A
        alive &= ~newly_out
    return t.mean()

for lam, A, gamma in [(0.275, 2.07, 100), (0.096, 1.79, 1000)]:
    est = mc_arl(lam, A, n_reps=60000)
    rel_err_pct = 100 * (est - gamma) / gamma
    assert abs(rel_err_pct) < 3.0, f"λ={lam}: MC ARL {est:.0f} vs 문헌 목표 {gamma} 차이 과다"
    print(f"λ={lam}, A={A}: MC ARL={est:.1f} (문헌 목표 γ={gamma}, 오차 {rel_err_pct:+.2f}%)")
```

두 검증 모두 (PST2014, Table 4.1) 설계값과 1~3% 이내로 일치한다(몬테카를로는 표본오차가 더 크므로
허용폭을 넓혔다). **핵심 결론**: 오경보 ARL을 10배 늘리려면(100→1000) λ를 0.275→0.096로 약 3배 줄여야
하고, 그 결과 탐지지연(SADD)은 17.7→46.5로 약 2.6배 늘어난다(Table 4.1) — CMP 드리프트 관리도
설계에서 "민감하게 할수록 오경보가 늘고, 오경보를 줄이면 반응이 느려진다"는 진술이 막연한
정성적 설명이 아니라 이 폐형식 하나로 정량화된다는 것이 이 절의 요지다. 다만 PST2014의 모형은
지수분포 평균이동 시나리오이고 CMP 잔차가 정확히 지수분포를 따른다는 근거는 없다 — **트레이드오프의
방향(λ↓ ⇒ ARL₀↑, 지연↑)은 EWMA 일반론(NIST 핸드북 정성적 서술과 일치)이지만, 표의 절대 숫자를
CMP 잔차(정규분포에 가까운 것이 보통)에 그대로 이식하는 것은 미검증이다.**

## 3. 재보정 트리거 규칙

판단 기준에는 특정 슬러리·막질 이름을 넣지 않고, 일반 변수(잔차 표준화값·누적 폴리시 시간·
디스크 누적 사용량)만 쓴다.

| 규칙 | 입력 | 판단 기준 | 출력 |
|---|---|---|---|
| **A. 통계적 변화점** | 회귀 잔차(실측/예측 MRR 비의 로그)의 EWMA 통계량 `Z_t` | `\|Z_t - Z_0\| > L·σ·sqrt(λ/(2-λ))`(§2.1 NIST식) 연속 위반, 또는 CUSUM `S_hi/S_lo > h` | `{trigger: "statistical", axis: "Kp", confidence: L 초과폭}` — 즉시 재보정이 아니라 **재보정 후보 플래그**(오경보 있음, §2.2) |
| **B. 누적 폴리시 시간 임계** | 마지막 컨디셔너/패드 교체 이후 누적 폴리시 시간 `t_cum` | `t_cum`이 그 패드·컨디셔너 조합의 실측 변화점(SL2021 방식으로 그 설비에서 사전 characterize한 값, 이 노트의 12h는 예시이지 보편 상수 아님)에 근접 | `{trigger: "scheduled", axis: "Γ,S", action: "conditioning 재특성화 예약"}` |
| **C. 소모품 로트/부품 교체 이벤트** | 패드 교체, 슬러리 로트 변경, 컨디셔너 디스크 교체, 캐리어 멤브레인/리테이너링 교체 로그 | 이벤트 발생 자체(통계 판정 불필요 — HC2026 §4.4가 이 방식이 유효함을 실증) | `{trigger: "deterministic_reset", axis: "Kp,S,Γ 전체", action: "잔차 이력·EWMA 상태 초기화 후 재보정 런 요구"}` |
| **D. 디스크 누적 사용량** | 컨디셔너 디스크 누적 드레싱 횟수/시간 | 제조 규격 수명 대비 비율이 임계(예: 80%) 초과 | `{trigger: "consumable_life", axis: "Γ", action: "S(정상상태 조도) 재적합 예약"}` |

규칙 A와 B/D의 차이: A는 "무엇이 드리프트를 일으켰는지 모르는 채로" 잔차만 보고 반응하는 사후
탐지(reactive)이고, B/D는 물리적 원인(§1)을 미리 알고 있어 통계 검정 없이 예방적으로(preventive)
트리거하는 것이다. C는 둘 다와 달리 확률적 판정이 아예 필요 없는 결정론적 리셋이다 — HC2026이
패드 교체마다 무조건 리셋했더니 5개 패드 모두 평균 1696~1700 nm/min, 95% CI [1696.16, 1699.61]로
일관됐다는 사실(§1 후반)이 "판정 없이 리셋해도 손해가 없다"는 근거다.

## 4. FabSim 축 매핑

FabSim은 장비축(Λ Π Θ Γ)과 소모품축(κ χ ψ τ Δ S)을 분리한다(`sim/factors.py` 문서화, 이 노트가
새로 확보한 문헌은 아니고 내부 설계 인용). 이 안에서:

- **Kp 계열 배율**(Preston 계수 보정, `sim/store.py`의 `calibration_factor()`): §1③ 슬러리 로트
  변동(입도·pH·산화제 역가)이 여기 해당한다 — `sim/chemistry.py` 주석대로 화학 효과가 Kp 하나에
  뭉뚱그려진 설계이므로, 로트가 바뀌어 화학 조성이 규격 내에서 이동하면 재보정 대상은 Kp다.
  규칙 A(잔차 EWMA/CUSUM)와 C(로트 교체 이벤트)가 이 축을 겨냥한다.
- **Γ 컨디셔닝**(컨디셔닝 부하, `conditioner_pcr_decay` 시상수 τ=27.4h): §1②(컨디셔너 디스크
  마모)가 직접 해당하고, §1①(패드 마모)도 컨디셔닝 재생률과 짝을 이루는 한 축이다. 규칙 B·D가
  이 축을 겨냥한다.
- **S 안정성**(글레이징률 대 컨디셔닝 재생률의 균형이 정하는 정상상태 패드 조도, `sim/factors.py`
  주석): §1①(패드 마모/교체)이 가장 직접적으로 해당한다 — SL2021의 "12시간 변화점" 패턴이 바로
  이 정상상태가 무너지는 순간이다. 규칙 A(SL2021류 실측 곡선에서 사전 characterize한 변화점을
  CUSUM/EWMA로 탐지)와 C(패드 교체 시 무조건 리셋)가 이 축을 겨냥한다.
- **매핑되지 않는 축**: §1④(캐리어 멤브레인·리테이너링 PM)은 Kp/S/Γ 스칼라 축이 아니라 압력
  분포 p(r)·V(r) 프로파일(tool-platen-head 에이전트 소관)에 더 가깝다. 이 노트의 규칙 C는 이
  이벤트에도 "재보정 런 요구"를 트리거하는 것으로 넣었지만, 어느 스칼라 축을 재적합할지는 Kp/S/Γ
  삼분류 밖의 문제로 남는다 — ⚠ 이 매핑은 미검증 제안이다.
