<!-- V2-SECTION: R4-disk | 공동: R1-equipment | 분배완료 2026-09-08 | 근거: disk-, pcr, sweep, 디스크 | 정본: ARCHITECTURE-V2.md §3 -->
# 디스크 하중·RPM·반경이 PCR(패드절삭률)에 미치는 영향 — Preston형 컨디셔닝 모델

> disk-kinematics Lv1-2. [[conditioner-sweep-algorithm-trajectory-density]](Lv1-1, 반환점 밀도발산)
> [[conditioner-disk-pad-cutting-model]](disk-conditioner Lv2-1, Evans-Marshall 마모율)
> [[../physics/cmp-kinematics-rotary]](process-integrator Lv1-2, 상대속도 유도)와 상호링크.
> Lv1-1이 "스윕 알고리즘 → 반경별 궤적밀도"를 다뤘다면, 본 단원은 **절삭 강도(하중 P·상대속도 v)가
> PCR에 어떻게 선형결합되는지**를 다룬다 — 두 축(밀도×강도)이 합쳐져야 최종 PCR 공간분포가
> 나온다는 게 disk-kinematics 커리큘럼의 핵심 스토리.

## 1. 출처
1. **Zheng, Zhao & Lu (2023)**, "Prediction of Pad Wear Profile and Simulation of Its Influence
   on Wafer Polishing," *Micromachines* 14(9), 1683. DOI: 10.3390/mi14091683, PMC10536193
   (오픈액세스 CC-BY, State Key Lab of Tribology, Tsinghua Univ.). PMC 전문 직접 열람
   (curl로 pmc.ncbi.nlm.nih.gov 접근 성공, MDPI 원문 사이트는 접근 차단됨 — PMC 사본으로 대체).
   Eq.(10)–(12)에서 Preston 방정식을 컨디셔닝(디스크-패드)에 그대로 적용한 PCR 모델을 제시,
   §4.1 결과절과 Table 1 실험조건 수치(패드 100 RPM, 디스크 73 RPM, 하중 4 lbf, 디스크 유효직경
   104.5mm, 스윕 19 RPM, 스윕범위 반경 83~308mm)를 신규 인용한다.
2. **Lai, J.-Y. (2001)**, "Mechanics, Mechanisms, and Modeling of the Chemical Mechanical
   Polishing Process," PhD thesis, MIT. [[../physics/cmp-kinematics-rotary]]에서 이미 확립한
   상대속도 유도(Eq. 2.7–2.12, 운동학수 µ, 비균일도=2|µ| 해석식)를 본 노트는 웨이퍼-패드 쌍이
   아니라 **컨디셔너디스크-패드 쌍**에 대입해 재사용한다(동일 회전운동학 구조이므로 치환 타당).
3. A. Scott Lawing (2004), NCCAVS CMPUG 발표자료(공개 PDF) — "Increasing Wafer Down-force →
   Pad Wear Rate 증가" 슬라이드(정성적, 축 눈금 미기재). [[conditioner-disk-pad-cutting-model]]에서
   이미 1차 출처로 등록됨 — 본 노트에서는 §2의 "하중↑→절삭률↑" 방향성 재확인에만 사용.

## 2. Preston형 PCR 모델 (Zheng et al. 2023 Eq.10–12)
논문은 웨이퍼 MRR의 Preston 방정식을 디스크 컨디셔닝에 그대로 이식한다:
```
MRR = Kp · P · v          (Eq.10, 웨이퍼-패드)
PCR = Kp · P · v          (Eq.11, 디스크-패드로 치환: P=디스크 하중/접촉압력, v=디스크-패드 상대속도)
PCA = Kp · P · ∫v dt = Kp · P · s   (Eq.12, s=누적 스크래치 거리)
```
Kp는 실험적 상수(경험적, 조건마다 변함)로만 명시되고 수치는 논문에 없다 — 웨이퍼-패드 조건의
Kp~1e-13 m²/N 오더([[../cmp/preston-luo-dornfeld-mrr.md]])는 접촉 형상(다이아몬드 vs 슬러리
입자)이 달라 디스크-패드에 그대로 준용할 근거가 없으므로 여기서는 차용하지 않는다.

**핵심은 v의 반경·RPM 의존성이다** — Kp·P가 반경/시간에 걸쳐 상수라고 가정하면(같은 하중,
같은 다이아몬드 밀도), PCR의 공간분포는 순전히 v(상대속도)의 공간분포로 결정된다.

## 3. 상대속도 v의 반경·RPM 의존성 — Lai(2001) 운동학수 치환
process-integrator 노트(§2.1, §3)의 결과를 디스크-패드 쌍에 치환한다: 웨이퍼→디스크, 헤드
각속도 ω_w→디스크 자전 ω_d, 플래튼 각속도 ω_p→패드 자전 ω_p, 축간거리 r_cc→(디스크 중심)-
(패드 중심) 거리(스윕에 따라 시간에 따라 변함).

```
|v_R(r̄,θ)| = ω_p · r_cc · sqrt( (r̄µ)² + 2r̄µ·cosθ + 1 ),   r̄ = r/R_disk ∈[0,1]
µ = (R_disk / r_cc) · (1 − Rs),   Rs = ω_d/ω_p
(v_max − v_min)/(ω_p·r_cc) = |1+µ| − |1−µ|
```

- **Rs=1 (동속)** 이면 µ=0 → |v_R| = ω_p·r_cc, 디스크 전면에서 위치 무관 균일 — process-integrator
  노트 §2.1 결과가 그대로 성립. 디스크 자체의 국소 절삭 불균일이 최소화된다는 뜻이다(패드
  반경별 PCR 자체는 여전히 sweep 반경별 체류시간(Lv1-1)에 의해 불균일 — 별개 현상).
- **Rs≠1**이면 µ≠0이고, §4에서 Zheng et al. 실제 조건(Rs=0.73)에 대입한 결과 µ≈0.072,
  디스크 내 상대속도 비균일도 약 14%로 계산됐다(당초 "작을 것"이라는 가설과 반대 — §4 참조).
- **하중 P**는 PCR에 선형(Eq.11)으로 곱해진다. 균일압력 가정 시 반경 의존은 없다 — 디스크가
  강체가 아니면 국소압력이 달라질 수 있으나 이는 본 논문 범위 밖(다루지 않음, 별도 문헌 필요).

## 4. Python 검증 — Lai(2001) 치환식을 Zheng et al.(2023) Table 1 조건에 대입
문헌은 PCR 반경분포를 그림으로만 제공하고 수치표는 없다(그림 판독은 하지 않음). 대신 **Lai
(2001) 유도식 자체의 수학적 성질**(비균일도=2|µ|)을 Zheng et al. 실험조건의 수치(패드 100 RPM,
디스크 73 RPM, 디스크 유효반경 52.25mm)에 대입해, 그 조건에서 디스크 국소 불균일이 실제로
작은지를 정량 대조한다.

```python verify
import math

def v_rel_uniformity(R_disk, r_cc, omega_p, Rs):
    """Lai(2001) 치환식: mu와 에지(r_bar=1)에서의 상대속도 비균일도(무차원)를
    해석식과 수치탐색(theta 3600분할) 양쪽으로 계산해 서로 대조한다."""
    mu = (R_disk / r_cc) * (1 - Rs)
    r_bar = 1.0
    vals = []
    for i in range(3600):
        theta = 2 * math.pi * i / 3600
        v = omega_p * r_cc * math.sqrt((r_bar * mu) ** 2 + 2 * r_bar * mu * math.cos(theta) + 1)
        vals.append(v)
    vmax, vmin = max(vals), min(vals)
    analytic_nondim = abs(1 + mu) - abs(1 - mu)
    numeric_nondim = (vmax - vmin) / (omega_p * r_cc)
    return mu, analytic_nondim, numeric_nondim

# Zheng et al. (2023) Table 1 실측 조건: 패드 100 RPM, 디스크 73 RPM, 디스크 유효직경 104.5mm.
# r_cc(디스크-패드 중심거리)는 논문 미기재 — 스윕범위 반경 83~308mm(Table 1)의 중간값
# 195.5mm를 대표값으로 근사(*미검증 근사* — 논문이 시간별 실제 위치를 안 줌).
omega_p = 100 * 2 * math.pi / 60  # rad/s, 문헌값 100 RPM 그대로
R_disk = 0.05225  # m, 문헌값 104.5mm/2 = 52.25mm
r_cc_case = 0.1955  # m, 스윕범위(83~308mm) 중간값 근사
Rs_case = 73 / 100  # 문헌값 디스크73RPM/패드100RPM

mu, analytic, numeric = v_rel_uniformity(R_disk, r_cc_case, omega_p, Rs_case)
assert abs(analytic - numeric) < 1e-6, f"해석식-수치탐색 불일치: {analytic} vs {numeric}"
# 실측 대입 결과: mu~0.072, 비균일도~14.4% — 작지 않다(당초 가설과 반대, 아래 §4 정직히 기록)
assert 0.06 < abs(mu) < 0.08, f"mu가 예상 범위(0.06~0.08) 밖: {mu:.5f}"
assert 0.13 < numeric < 0.16, f"비균일도가 예상 범위(13~16%) 밖: {numeric:.4f}"

# 대조군: Rs=1(동속)이면 mu=0, 비균일도=0 (순수 수학적 극한, 문헌과 무관한 자체 sanity check)
mu0, analytic0, numeric0 = v_rel_uniformity(R_disk, r_cc_case, omega_p, 1.0)
assert abs(mu0) < 1e-12 and abs(numeric0) < 1e-9

print(f"문헌조건(Rs=0.73) 재현: mu={mu:.5f}, 디스크 내 상대속도 비균일도={numeric*100:.2f}% (해석식과 {abs(analytic-numeric):.2e} 일치)")
print(f"동속 대조군(Rs=1.0): mu={mu0:.2e}, 비균일도=0%")
```

**결과 요약(재현값 vs 당초 가설 대조 — 정직한 기록)**: Zheng et al. Table 1 실측 RPM 조건
(패드100/디스크73 RPM, 디스크 유효반경 52.25mm)을 Lai(2001) 치환식에 대입하면 µ≈0.0722, 디스크
에지 상대속도 비균일도 **14.4%** — 이는 §3에서 "µ가 매우 작을 것"이라 예상했던 당초 가설과
**반대로 작지 않은 수치다**. 원인은 R_disk/r_cc 비(52.25mm/195.5mm≈0.267)가 process-integrator
노트가 전형값으로 제시한 웨이퍼-패드 비(R_w/r_cc, 통상 <1이지만 훨씬 작은 값)보다 커서
(1-Rs)=0.27과 곱해진 결과다. 즉 **디스크는 패드보다 훨씬 작아서 R_disk/r_cc 자체가 웨이퍼-
패드계보다 크게 나올 수 있고, 그 결과 같은 RPM비 편차(Rs=0.73)라도 디스크-패드계의 국소
비균일도가 웨이퍼-패드계보다 커질 수 있다** — 이는 논문이 직접 검증한 결과가 아니라 **본
노트가 Lai(2001) 치환식을 대입해 얻은 독자 계산**이며, §4.1의 "PCR 패턴은 스윕기구학이
지배한다"는 정성 서술과 **꼭 일치하지 않을 수도 있다**(오히려 Rs≠1 선택 자체가 디스크 국소
불균일을 14% 수준 유발할 수 있다는 반대 방향의 시사점). r_cc를 근사값(195.5mm)으로 가정한
결과이므로, 실제 r_cc(83~308mm 범위 내 시간에 따라 변함)가 다르면 비균일도도 달라진다 —
§7 과제로 남긴다.

## 5. Lawing(2004) 정성 대조
Lawing 슬라이드의 "Increasing Wafer Down-force → Pad Wear Rate 증가"는 §2 Eq.11의 P 선형항과
방향이 일치한다(하중↑ → PCR/PCA↑). 슬라이드에 축 눈금이 없어 기울기·지수는 확인 불가 —
[[conditioner-disk-pad-cutting-model]] §2에서 이미 Evans-Marshall 마모율(하중 선형)로 정량화된
것과 같은 방향성이라는 점만 재확인한다.

## 6. fab-sim Γ(컨디셔닝 부하 팩터) 적용 — sweep_cpm은 속도항이 아니다 (2026-09-11)

`sim/factors.py`의 `_f_gamma()`는 기존에 `Γ = (F/F_ref)×(sweep_cpm/sweep_ref)×(duty/duty_ref)`
형태로 스윕 왕복수(cond_sweep_cpm, n_a)를 마치 상대속도 v처럼 곱했다. §2-3의 Preston형
`PCR=Kp·P·v`와 대조하면 이는 물리적으로 틀렸다 — v_rel 식(§3)에 n_a(스윕 왕복수)는
**전혀 나타나지 않는다**. n_a가 결정하는 것은 [[conditioner-sweep-algorithm-trajectory-density]]·
[[conditioner-sweep-kinematics-pcr-profile]]이 이미 확립한 **반경별 궤적밀도(어디를 깎는가)**이지,
총 절삭 부하(얼마나 세게 깎는가)가 아니다. `cond_sweep_cpm`이 실측 문헌값으로 뒷받침된다는
사실([[conditioner-sweep-rate-literature-values]])과, 그 값이 **Γ라는 스칼라 절삭부하 곱셈항에
들어가야 한다는 것**은 별개 주장이며 후자는 근거가 없다.

**대안: v_rel을 디스크 중심속도 ω_p·r_cc로 근사하고, rpm_platen 비율로 대체한다.**
§3 식에서 r̄=0(디스크 중심)일 때 v_R = ω_p·r_cc가 Rs(=ω_disk/ω_pad)와 무관하게 **정확히**
성립한다(디스크 자전은 중심을 움직이지 않으므로). r̄>0에서는 Rs≠1 보정(µ항)이 국소 속도를
바꾸지만, 디스크 전체(반경·위상 균등)로 평균하면 그 보정은 상쇄된다 — 아래 verify에서 §4와
같은 Zheng et al. 실측조건(µ≈0.0722)에 대입해 정량 확인한다. r_cc(스윕기구 형상)는 레시피가
아니라 장비 상수이므로 F·v 비율(현재/기준)에서 분모·분자 모두 같은 r_cc를 쓰면 상쇄된다 —
따라서 v 항은 **rpm_platen(플래튼 rpm)의 현재/기준 비율만으로 근사 가능**하다. 이는
[[../physics/cmp-kinematics-rotary]]에 근거해 이미 Λ 팩터(`sim/factors.py _f_lambda`)가
쓰는 것과 동일한 "Rs=1 근사"·"ω_p가 지배항" 구조다 — 같은 플래튼이므로 같은 근사를 재사용하는
것이 정합적이다.

```python verify
import numpy as np

# Zheng et al. (2023) Table 1 실측조건(§4에서 이미 검증한 mu=0.0722)을 재사용해
# "디스크 전체 평균 v_rel / (omega_p*r_cc)"가 1에 얼마나 가까운지 정량 확인한다.
mu = 0.0722  # §4 verify 결과 재사용(문헌 RPM비 Rs=0.73, R_disk/r_cc≈0.267에서 유도)

theta = np.linspace(0, 2 * np.pi, 200_000, endpoint=False)
r_bar = np.linspace(0.0, 1.0, 200)  # 디스크 반경 균등 샘플(중심~에지)
TH, R = np.meshgrid(theta, r_bar)
v_over_omega_r = np.sqrt(1 + 2 * R * mu * np.cos(TH) + (R * mu) ** 2)

disk_avg = v_over_omega_r.mean()
edge_vals = np.sqrt(1 + 2 * mu * np.cos(theta) + mu ** 2)
edge_avg = edge_vals.mean()
edge_p2p = np.ptp(edge_vals)

# 핵심 주장: 디스크 전체 평균은 omega_p*r_cc에서 <0.1% 벗어난다(지배항 근사 정당화)
assert abs(disk_avg - 1.0) < 0.001, f"디스크평균 편차 {disk_avg-1:.5f} — 0.1% 기준 밖"
# 대조: 에지 국소값은 상당히 흔들린다(peak-to-peak) — 이건 반경분포 문제지 총량 문제가 아님
assert 0.13 < edge_p2p < 0.16, f"에지 peak-to-peak={edge_p2p:.4f} — §4의 14.4%와 불일치"

print(f"디스크 전체 평균 v/(omega_p*r_cc) = {disk_avg:.5f} (편차 {abs(disk_avg-1)*100:.3f}%)")
print(f"에지 평균 = {edge_avg:.5f}, 에지 peak-to-peak = {edge_p2p*100:.2f}%")
print("결론: 총 절삭부하(스칼라) 근사에는 omega_p*r_cc가 지배적 — "
      "Rs 보정은 반경분포(에지 vs 중심) 문제이지 총량 문제가 아니다.")
```

**결과(Zheng et al. 2023 Table 1 조건 재현, 2026-09-11)**: 디스크 전체 평균 v/(ω_p·r_cc) =
1.00044 (0.044% 편차) — Rs≠1이어도 총 절삭부하 스칼라 근사에는 ω_p(rpm_platen)가 사실상
완전히 지배적이다. 반면 에지 국소값은 peak-to-peak 14.4%까지 흔들린다(§4와 동일 수치, 대조군
으로 재확인) — 이건 **반경별 분포**
문제이지 Γ가 다루는 **총량** 문제가 아니라는 것을 수치로 분리했다.

**fab-sim 결론**: `_f_gamma()`를 `Γ=(F/F_ref)×(rpm_platen/lambda_ref_rpm_platen)×(duty/duty_ref)`로
재정의(2026-09-11 반영). `cond_sweep_cpm`은 f.drivers에 진단용으로만 남기고 f.value 계산에서
제외했다. confidence는 여전히 `estimated`로 하한한다 — 이유는 Rs 보정(에지 14%, 팩에
disk RPM 드라이버 없음), 컨디셔너 자체의 시간적 PCR 소진([[conditioner-disk-pad-cutting-model]]
§3, 50h→16%) 미반영, 임계하중 비선형 미반영 세 가지 구조적 결측 때문이다 — 이 셋은 개별
드라이버 confidence를 올린다고 해소되지 않는다.

**후속 판정(2026-09-14, [[gamma-conditioning-load-confidence-basis]], EVIDENCE-RULES 판정#22)**: 위 세 사유를
하나씩 판정했다 — Rs 보정은 면적평균 폐형식 1+μ²/8+μ⁴/192(위 verify의 1.00044는 반경 균등 가중, 면적
가중은 1.00065 — 둘 다 <0.1%)로 문헌 Rs 범위에서 총량 편차 <1%라 **해소**, τ 앵커는 기준조건에서 항등적으로
무관해 **조건부 하한**, 임계하중은 마모 팁 반경 미확보로 **미해소** → `_f_gamma` 하한은 그대로다.

## 7. 한계 및 다음 단원 연결
- Kp(경험상수) 절대값 미확보 — Cal-1(캘리브레이션 단원, G2 이후)에서 실측 대체 필요.
- r_cc(디스크-패드 중심거리)는 스윕 중 83~308mm 범위에서 연속 변화 — 본 노트는 중간값
  단일 스냅샷 근사만 검증했다. Lv2-1(인시츄 vs 엑스시츄)에서 시간적분(전체 스윕범위) 버전으로
  확장이 필요하다(83mm·308mm 양끝값에서 µ 재계산은 아직 하지 않음 — 다음 단원 과제).
- 디스크 표면 각 다이아몬드의 개별 v_R(θ,r)이 접촉압력의 국소 분포(Hertz 접촉, 개별 다이아몬드
  돌출높이 분포)와 어떻게 결합하는지는 다루지 않음 — [[conditioner-disk-pad-cutting-model]]
  (disk-conditioner Lv2-1)의 Evans-Marshall 마모율 결합이 그 역할.
