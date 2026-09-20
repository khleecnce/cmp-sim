<!-- V2-SECTION: R4-disk | 근거: conditioner, disk-, pcr, sweep, population balance | 정본: ARCHITECTURE-V2.md §3 -->
# 스윕 레시피 → 반경별 PCR·패드 두께 프로파일 예측 모델 (disk-kinematics Lv3-2)

> disk-kinematics Lv3-2. "지금까지 배운 sweep 운동학(체류시간·궤적밀도)·하중/RPM 영향·
> insitu/exsitu 안정성·레시피 최적화·폐루프 제어를 통합해, sweep 레시피 파라미터를 입력받아
> 반경별 PCR 프로파일과 시간에 따른 패드 두께 프로파일을 예측하는 모델을 정의하라"는 단원.
> 본 노트는 **모델 정의 + 문헌 대조 코드**만 다룬다 — 실제 시뮬레이터 구현(`sim/`)은 담당하지
> 않으며, 필요한 I/O는 `agents/disk-kinematics/PROFILE.md`의 `## 구현 요청`에 등록했다
> (2026-09-13 최신 지시: "sim/tier2"라는 옛 커리큘럼 문구를 따르지 말 것).

## 1. 출처
1. **Zheng, Zhao & Lu (2023)**, "Prediction of Pad Wear Profile and Simulation of Its Influence on
   Wafer Polishing", *Micromachines* 14(9), 1683, DOI: 10.3390/mi14091683, PMC10536193
   (오픈액세스, Europe PMC JATS XML 전문 확보, `data/corpus/fulltext/doi_10.3390_mi14091683.xml`).
   Lv1-2·Lv2-2에서 이미 이 논문의 Eq.1-12(4중 회전 궤적, Preston형 PCR)를 인용했다. 본 노트는
   **이전 단원에서 다루지 않은 Table 2**(13-partition dwell-time 실측/최적화 세팅표)를 처음으로
   사용한다 — 원문 JATS XML의 `<table-wrap id="...t002">` 원소에서 직접 파싱, 텍스트 추출로
   깨지지 않은 실제 수치표.
2. **Baisie, Li & Zhang (2010)**, ASME MSEC2010-34264, DOI: 10.1115/MSEC2010-34264 —
   [[disk-sweep-recipe-flattening-baisie2010]](Lv2-2)에서 확립한 "체류시간 균일(UNIFORM)이
   최평탄" 원칙과 TTV/NU 계산법을 그대로 재사용, Zheng et al. 실측 dwell표에 교차적용한다.
3. **Ring, Prasad & Dirksen** (Univ. of Utah / Cabot Microelectronics), "Dynamic CMP Pad Asperity
   Population Balance for Conditioning and Polishing", 저자 공개 PDF
   (https://my.che.utah.edu/~ring/Publications-PDFs/J-120.pdf) —
   [[conditioner-asperity-population-balance]](disk-conditioner Lv3-1)에서 이미 재현한 Eq.9
   self-similarity 해를 본 노트에서 **반경 의존형(A→A(r))**으로 확장한다.
4. **US Patent 9,138,860 B2** (Applied Materials) — [[disk-kinematics-closed-loop-adaptive-sweep]]
   (Lv3-1)에서 검증한 폐루프 dwell-time 보정 루프. 본 노트 §6에서 "다음 사이클 레시피 갱신"의
   구체적 대상이 바로 아래 §2의 {f_i} 벡터임을 명시한다.
5. **Jeong et al. (2022)**, ASPEN, DOI 10.3850/978-981-18-6021-8_or-12-0224.html —
   [[disk-insitu-exsitu-conditioning-mrr-stability]](Lv2-1)의 압력별 최소회복 조건화시간표.
   본 노트 §5에서 이 표를 "누적 조건화시간 T" 입력값 환산에 재사용한다.

## 2. 모델 정의 — 입력 → PCR(r) → 누적 패드 두께 H(r,T)

**입력**: 스윕 레시피는 반경 방향 N개 구간(partition)의 **체류시간 비율 벡터** {f_i}
(Σf_i=1, Zheng et al. §4.1 "divided into several partitions... percentage of the dwelling time...
fitted into a spline function"), 하중 P, 총 조건화시간 T, (필요시) 패드/디스크 RPM.

**1단계 — 반경별 PCR 형상함수** (Zheng et al. Eq.10-12, [[disk-rpm-load-radius-pcr]] Lv1-2에서
이미 확립한 "균일압력 하에서는 PCR(r) 형상이 전적으로 v(r)/dwell 형상으로 결정된다"는 결론
그대로 사용):
```
PCR_shape(r_i) ∝ f_i     (partition i가 반경 구간 r_i에 대응한다는 가정 — §8에서 미검증 표기)
PCR(r_i) = k · P · PCR_shape(r_i)
```

**2단계 — 누적 패드 두께 손실** (Zheng et al. Eq.12, PCA = k·P·∫v dt = k·P·s, 고정 레시피가
매 스윕 사이클 같은 dwell 패턴을 반복한다면 반경 구간 i에서의 누적 스크래치 거리는 총
조건화시간 T에 선형 비례):
```
H(r_i, T) = k · P · f_i · T
```
이 선형-시간 가정은 Zheng et al. §3의 실측 결과("PCR 결과는 패드의 기존 표면 프로파일과 거의
무관")로 정당화된다 — 즉 패드 표면이 마모되며 변해도 PCR(r) 형상 자체는 재사용 가능하다는
것이 논문의 핵심 실험적 발견이므로, H(r,T)를 시간에 대해 단순 적분(선형)해도 되는 근거가 된다.

**3단계 — asperity 분포의 반경별 미세구조 (population balance 결합)**: [[conditioner-asperity-
population-balance]]의 Ring et al. Eq.9 `η_z(z,t)=η_z0((z+d)exp(2At)-d)`는 원래 **0차원**(단일
접촉점, A는 위치 무관 상수) 모델이다. 본 노트는 [[conditioner-sweep-kinematics-pcr-profile]]
§6이 제안한 결합모델 `PCR(r,t)=PCR_shape(r)·decay(t)`의 population-balance 버전으로, 국소
마모율 상수를 반경의존형으로 일반화한다:
```
A(r_i) = A0 · f_i / f̄        (f̄ = mean(f_i), A0=Ring et al.의 평균조건 기준 fit parameter)
η_z(z, r_i, t) = η_z0( (z+d)·exp(2·A(r_i)·t) − d )
```
dwell 비율이 높은 반경(예: 반환점 근방)은 A(r)가 커서 asperity 분포가 더 빨리 좁아진다(=더
공격적으로 재생/글레이징 방지) — 이는 [[conditioner-sweep-algorithm-trajectory-density]]
(Lv1-1)의 "반환점 궤적밀도 발산" 결론을 population balance 언어로 재서술한 것이다.

## 3. 정량 재현 1 — Zheng et al. Table 2 실측 dwell표로 TTV/NU 계산, Baisie 원칙과 교차확인

Zheng et al. Table 2는 같은 12인치 플랫폼에서 실제 사용된 두 가지 13-partition dwell-time
세팅(Sinusoidal=기본 사인파 모드, Adjusted=평탄화 목적 보정 모드)을 %로 제공한다. 논문 본문은
"adjusted sweep mode is for an optimized pad wear profile"(§4.1)이라고만 서술하고 정량적
개선폭은 밝히지 않는다 — 아래 코드가 그 개선폭을 처음으로 정량화하고, [[disk-sweep-recipe-
flattening-baisie2010]]의 TTV/NU 계산법·"이상적 균일 dwell이 최평탄"이라는 원칙에 교차 대조한다.

```python verify
import numpy as np

# Zheng, Zhao & Lu (2023) Table 2 — 13-partition dwell-time 실측/최적화 세팅 (원문 표 그대로, %)
sinusoidal = np.array([17.89, 7.77, 6.24, 5.53, 5.15, 4.96, 4.90,
                        4.96, 5.15, 5.53, 6.24, 7.77, 17.89])
adjusted   = np.array([8.47, 7.24, 7.29, 7.33, 7.37, 7.42, 7.46,
                        7.50, 7.55, 7.59, 7.63, 7.72, 9.42])

assert abs(sinusoidal.sum() - 100.0) < 0.05, "dwell 비율 합은 100%에 근접해야 함(표 반올림 오차만)"
assert abs(adjusted.sum() - 100.0) < 0.05, "dwell 비율 합은 100%에 근접해야 함"

def ttv(f):
    return f.max() - f.min()

def nu(f):
    return f.std() / f.mean() * 100.0

ttv_sin, ttv_adj = ttv(sinusoidal), ttv(adjusted)
nu_sin, nu_adj = nu(sinusoidal), nu(adjusted)
ttv_reduction = (ttv_sin - ttv_adj) / ttv_sin * 100.0
nu_reduction = (nu_sin - nu_adj) / nu_sin * 100.0

print(f"TTV(pp): sinusoidal={ttv_sin:.2f}, adjusted={ttv_adj:.2f}, 개선율={ttv_reduction:.1f}%")
print(f"NU%: sinusoidal={nu_sin:.2f}, adjusted={nu_adj:.2f}, 개선율={nu_reduction:.1f}%")

# 논문 서술("adjusted가 optimized profile", §4.1)의 정량화 — 개선 방향과 크기 확인
assert ttv_adj < ttv_sin, "adjusted 모드가 TTV를 낮춰야 한다는 논문 서술과 불일치"
assert nu_reduction > 80.0, f"NU 개선율이 예상보다 작음: {nu_reduction:.1f}%"

# Baisie et al.(2010) 원칙 교차확인: 이상적 균일 dwell(100/13=7.69%)에 얼마나 가까운가
ideal = 100.0 / 13
dev_sin = np.max(np.abs(sinusoidal - ideal))
dev_adj = np.max(np.abs(adjusted - ideal))
print(f"이상균일 대비 최대편차(pp): sinusoidal={dev_sin:.2f}, adjusted={dev_adj:.2f}")
assert dev_adj < dev_sin, "adjusted가 Baisie UNIFORM 원칙에 더 근접해야 함"

# 그러나 adjusted도 완전한 균일(Baisie UNIFORM)에는 도달하지 못함을 확인 — 정직하게 기록
rel_dev_adj = dev_adj / ideal * 100.0
print(f"adjusted의 이상균일 대비 상대편차 = {rel_dev_adj:.1f}% (0%면 완전균일)")
assert rel_dev_adj > 5.0, "adjusted가 완전균일에 도달했다면 이 가정 재검토 필요"
```

**결과(2026-09-13 확인)**: TTV 12.99pp→2.18pp(83.2% 개선), NU 57.84%→7.56%(86.9% 개선) —
논문의 정성 서술을 정량적으로 뒷받침한다. 다만 adjusted 모드도 이상균일(7.69%) 대비 최대편차
1.73pp(상대 22.5%)가 남아 **완전한 UNIFORM에는 도달하지 못했다** — 특히 양끝 partition
(8.47%, 9.42%)이 중앙(7.3~7.6%)보다 여전히 높고 좌우 비대칭(8.47≠9.42)이다. 이는
[[conditioner-sweep-algorithm-trajectory-density]](Lv1-1)의 반환점 밀도발산이 스윕 가속만으로는
완전히 상쇄되지 않는다는(또는 저자들이 반환점 여유폭을 의도적으로 남겼다는) 정황과 부합하나,
논문이 이 잔여 비대칭의 원인을 직접 설명하지 않으므로 **저자 자체 해석**임을 밝힌다.

## 4. 정량 재현 2 — population balance 반경별 narrowing 시간 스케일 (구조적 일관성 검증)

§2의 결합모델(`A(r)=A0·f_i/f̄`)을 Zheng et al. Table 2의 sinusoidal dwell표에 대입해, 반환점
부근 partition(f 최대)과 중앙 partition(f 최소)에서 asperity 분포가 동일한 목표 압축배율에
도달하는 시간이 dwell 비율에 반비례함을 확인한다. **주의**: 이는 독립적인 실측 데이터와의
대조가 아니라, §2에서 정의한 결합모델 자체의 대수적 필연(Eq.9의 로그선형성)을 수치로 확인하는
**내적 일관성 검증**이다 — Ring et al.의 A0 절대값은 여전히 fit parameter로 미보정이다.

```python verify
import numpy as np

sinusoidal = np.array([17.89, 7.77, 6.24, 5.53, 5.15, 4.96, 4.90,
                        4.96, 5.15, 5.53, 6.24, 7.77, 17.89])
f_bar = sinusoidal.mean()

A0 = 1.0  # Ring et al.: 논문 자체가 "fit parameter"라 명시(각주) — 임의단위, 절대값 아님
A_local = A0 * sinusoidal / f_bar  # 정규화: 평균 dwell 비율에서 A=A0 (Ring et al.의 0차원 기준과 일치)

S_target = 2.0  # 임의 목표 압축배율(분포폭이 절반이 되는 시점)
t_star = np.log(S_target) / (2.0 * A_local)  # Eq.9로부터 역산한 목표 도달시간

edge_idx, mid_idx = 0, 6  # partition 1(반환점 부근, dwell 최대) vs partition 7(중앙, dwell 최소)
ratio_predicted = sinusoidal[mid_idx] / sinusoidal[edge_idx]  # A 비율의 역수 = t* 비율(대수적 필연)
ratio_actual = t_star[edge_idx] / t_star[mid_idx]

print(f"partition1(반환점) dwell={sinusoidal[edge_idx]}%, partition7(중앙) dwell={sinusoidal[mid_idx]}%")
print(f"예측 t*비율={ratio_predicted:.3f} vs 계산된 t*비율={ratio_actual:.3f}")

assert abs(ratio_predicted - ratio_actual) / ratio_actual < 1e-9, \
    "t* 비율은 정확히 dwell 비율의 역수여야 한다(Eq.9 로그선형성의 대수적 귀결)"
assert t_star[edge_idx] < t_star[mid_idx], \
    "반환점 부근(dwell 비율 최대)이 중앙보다 목표 압축배율에 더 빨리 도달해야 한다"

print(f"결론: 반환점 부근 asperity 분포 narrowing이 중앙 대비 {ratio_actual:.2f}배 빠르게 진행 "
      f"(모델 내적 일관성 확인, 절대 A0는 여전히 미보정)")
```

**결과**: t*(중앙)/t*(반환점) = 17.89/4.90 ≈ **3.65배** — 반환점 부근이 중앙보다 약 3.65배 빨리
목표 분포압축에 도달한다는 예측. 이는 Ring et al.의 population balance(§2 3단계)를 Zheng et
al.의 실측 dwell 형상에 결합했을 때 나오는 **본 노트의 독자적 합성 결과**이며, 두 논문 어느
쪽도 이 결합을 직접 다루지 않는다 — 저자 종합임을 명시한다.

## 5. 정량 재현 3 — in-situ/ex-situ 누적 조건화시간을 H(r,T)의 T로 환산

[[disk-insitu-exsitu-conditioning-mrr-stability]](Lv2-1)의 Jeong et al.(2022) 압력별 최소회복
조건화시간표(5 psi→180초)를 §2의 선형모델 `H(r_i,T)=k·P·f_i·T`의 **T 입력값**으로 직접 환산해,
동일 웨이퍼 수 처리 후 in-situ와 ex-situ가 모델상 얼마나 다른 누적 조건화 "도즈"를 받는지
정량화한다 — Lv2-1은 처리량 손실률(23.1%)만 계산했고, 본 노트가 다루는 "누적 H(r,T)" 관점의
비율은 이번에 처음 도출한다.

```python verify
polish_cycle_s = 600.0        # 10분 폴리싱 사이클 (Lv2-1 노트 예시조건)
recovery_time_5psi_s = 180.0  # Jeong et al.(2022) Table, 5psi 최소회복 조건화시간

N_wafers = 20

T_insitu_total = N_wafers * polish_cycle_s        # in-situ: 폴리싱 전체시간 동안 동시조건화
T_exsitu_total = N_wafers * recovery_time_5psi_s  # ex-situ: 회복버스트 시간만 조건화

ratio = T_insitu_total / T_exsitu_total
print(f"{N_wafers:.0f}장 처리 후 누적 조건화시간: in-situ={T_insitu_total:.0f}s, "
      f"ex-situ={T_exsitu_total:.0f}s, 비={ratio:.2f}배")

assert abs(ratio - polish_cycle_s / recovery_time_5psi_s) < 1e-9
assert ratio > 3.0, "in-situ 누적조건화시간이 ex-situ의 3배를 넘어야 한다(600/180=3.33)"

# H(r,T)=k*P*f_i*T가 T에 선형이므로, 동일 레시피(f_i 동일 가정) 하 누적 H 비율도 정확히 이 값
print(f"선형모델 하 예측 누적 H(r,T) 비율(in-situ/ex-situ) = {ratio:.2f}배 (같은 f_i 가정)")
```

**결과**: 비율 = 600/180 = **3.33배**. 동일 웨이퍼 수를 처리해도 in-situ 레시피는 §2 선형모델
기준 ex-situ보다 3.33배 많은 누적 조건화 "도즈"를 받는다 — [[disk-insitu-exsitu-conditioning-
mrr-stability]]가 이미 밝힌 "in-situ 처리량손실 구조적 0% vs ex-situ 23.1%"라는 결론과 같은
방향이지만 **다른 지표**(도즈 비율 vs 손실률)이다. 이 3.33배는 **본 노트의 파생 계산**이며,
실제 팹에서 폴리싱:회복 사이클 배치가 다르면 값이 달라진다(미검증, 방향성만 신뢰).

## 6. 폐루프 제어와의 연결 — {f_i}는 매 사이클 갱신되는 대상

[[disk-kinematics-closed-loop-adaptive-sweep]](Lv3-1)의 US9138860B2 폐루프는 "측정된 마모
프로파일과 목표의 편차에 기반해 dwell time을 갱신"한다고 서술한다(§2). 본 노트 §2의 표기로
정확히 옮기면:
```
f_i(cycle+1) = f_i(cycle) - gain · ( H_measured(r_i) - H_target(r_i) )   (정규화 후 Σf_i=1 재투영)
```
즉 Zheng et al.의 "Adjusted" 모드(§3)는 **한 번의 수동/오프라인 보정**이고, US9138860B2의
폐루프는 **매 사이클 반복되는 온라인 버전**이다 — §3에서 확인했듯 Adjusted 모드조차 이상균일에
완전히 도달하지 못했는데(잔여편차 22.5%), 폐루프 방식은 원리상 이 잔차를 사이클마다 줄여나갈
수 있다는 것이 두 접근의 핵심 차이다(단, 이 비교 자체를 두 문헌이 직접 하지는 않음 — 저자 종합).

## 7. 구현 요청 처리
실제 시뮬레이터 인터페이스는 `agents/disk-kinematics/PROFILE.md`의 `## 구현 요청` 섹션에
등록했다(입력: {f_i}, P, T, 반경-partition 매핑; 출력: PCR(r), H(r,T), 반경별 η_z(z,r,t)).
sim/ 코딩은 소프트웨어 부문이 담당한다(2026-09-13 지시).

## 8. 한계와 정직성 표지
- **partition↔반경 매핑 미확정**: Zheng et al. Table 2는 "13-partition"이 disk-center의 스윕
  경로 상 등간격 구간이라고만 서술하고, 이것이 **등반경(等半径)** 구간인지 **등각(β)** 구간인지
  명시하지 않는다. Table 1의 "sweep range: Radial 83~308mm" 표기로 미루어 등반경 구간으로
  가정했으나(§2), 등각 구간이라면 [[conditioner-sweep-algorithm-trajectory-density]]의
  코사인법칙 비선형 사상 때문에 PCR_shape(r) 형태가 달라진다 — **미검증, 확인 못 함**.
- **A0(Ring et al. fit parameter)는 여전히 미보정**: §4의 3.65배는 비율(구조)만 신뢰할 수 있고
  절대 시간 스케일은 예측할 수 없다([[conditioner-asperity-population-balance]] §6과 동일한
  한계).
- **선형시간모델 H∝T의 장기 타당성 미검증**: Zheng et al.의 "PCR이 표면형상과 무관" 실험은
  8시간 조건화 범위 내 결과이며, 그보다 훨씬 긴 시간(패드 자체가 심하게 마모돼 형상함수가
  변할 수 있는 영역)에서도 성립하는지는 원문이 다루지 않는다.
- **§4, §5의 결합(population balance × dwell 형상, in-situ/ex-situ × H(r,T))은 어느 문헌도
  직접 다루지 않은 본 노트의 저자 종합**이다 — 개별 구성요소(Ring et al. Eq.9, Zheng et al.
  Eq.10-12, Jeong et al. 회복시간표)는 각각 1차 출처가 있으나, 결합 자체의 실측 검증은 없다.
- k(Preston 상수)의 절대값은 어느 출처도 제공하지 않음 — 본 노트 전체가 **상대적 형상/비율
  예측**에 국한되며 절대 PCR·두께 수치 예측은 하지 않는다.

## 관련 노트
[[conditioner-sweep-kinematics-pcr-profile]] · [[disk-rpm-load-radius-pcr]] ·
[[conditioner-sweep-algorithm-trajectory-density]] · [[disk-sweep-recipe-flattening-baisie2010]] ·
[[disk-insitu-exsitu-conditioning-mrr-stability]] · [[disk-kinematics-closed-loop-adaptive-sweep]] ·
[[conditioner-asperity-population-balance]]
