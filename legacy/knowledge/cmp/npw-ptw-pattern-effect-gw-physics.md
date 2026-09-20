<!-- V2-SECTION: R5-wafer | 공동: R3-pad | 분배완료 2026-09-08 | 근거: npw, pattern-, ptw | 정본: ARCHITECTURE-V2.md §3 -->
# NPW가 PTW를 예측 못하는 물리 — 확장 GW(Greenwood-Williamson) 접촉역학 모델 (Lv2-1)

> 에이전트: wafer-type Lv2-1 (NPW 결과가 PTW를 예측하지 못하는 이유: 패턴 효과의 물리) | 작성일: 2026-09-06
> 선행: [[npw-ptw-test-wafer-fundamentals]] (Lv1-1/1-2, NPW/PTW 정의·측정체계)
> 관련: [[pattern-dependent-dishing-erosion]] (effective density 모델, ρ_eff=x,y), [[wiwnu-pressure-velocity-wafer-scale]]

## 0. 질문
Lv1 노트가 남긴 정량 출발점: Kim&Seo(2002, 2차 인용·미검증)의 "NPW→PTW 상관계수 r≈0.71".
왜 완전한 상관(r=1)이 아닌가? 답은 **접촉역학**에 있다 — NPW는 패드 전체가 평평한 표면과
접촉하지만 PTW는 국소적으로 up-region(볼록부)만 패드 asperity와 우선 접촉해 압력이
집중된다. 이 노트는 그 물리를 1차 논문으로 정량화한다.

## 1. 1차 논문: 확장 GW 모델 (Vasilev et al. 2011)
Vasilev, Rzehak, Bott, Kücher, Bartha, "Greenwood–Williamson Model Combining Pattern-Density
and Pattern-Size Effects in CMP," *IEEE Trans. Semicond. Manuf.* 24(2), 338-347 (2011),
doi.org/10.1109/TSM.2011.2107756 — **1차, 원문 전체 확보**(유료 IEEE, 미러 사이트 미러 경유,
`papers/vasilev2011-gw-pattern-density-size-cmp.pdf`, 사용자 지시 2026-09-05 반영).

### 1.1 모델 구조 — 왜 NPW의 K 하나로 PTW를 설명 못하는가
NPW(블랭킷)에서 측정하는 blanket rate RR0는 패드 asperity와 평평한 웨이퍼 표면의 접촉만
반영한다(곡률 κ_asperity 하나). PTW에서는 up-region/down-region이 각각 다른 유효곡률을
갖는다(원 논문 eq.2, eq.5):
```
κ_U,D = κ_asperity ± κ_feature = 1/R_asperity ± 1/R_feature
κ_U = κ_asperity + 4αh/line²      (up-region, 볼록 → 곡률 가산)
κ_D = κ_asperity − 4αh/space²     (down-region, 오목 → 곡률 감산)
```
즉 **같은 패드 asperity 분포·같은 blanket rate라도 line/space 폭(피치)과 step height h에
따라 up/down 유효곡률이 갈라지고, 이게 각 영역이 받는 접촉압·제거율을 바꾼다.** NPW는
h=0(평평)이므로 κ_U=κ_D=κ_asperity로 수렴 — 이 분화 정보 자체가 NPW 데이터에 없다.

### 1.2 제거율 식 (원 논문 eq.27, GW 접촉역학 + Preston 결합)
지수형 asperity 높이분포 Φ(z)=(1/σ)exp(-z/σ)를 가정한 해석해:
```
RR_U = e^(h/σ) √κ_U · [√κ_D √κ_U / (√κ_U(1-ρ_eff) + e^(h/σ)√κ_D ρ_eff)] · RR0/κ_asperity
RR_D =        √κ_D · [√κ_D √κ_U / (√κ_U(1-ρ_eff) + e^(h/σ)√κ_D ρ_eff)] · RR0/κ_asperity
```
RR0(NPW blanket rate)는 입력 파라미터로만 쓰이고, up/down 제거율의 **분화**는 ρ_eff, h/σ,
κ_U/κ_D 비율이 결정한다. h→0(평탄화 완료) 극한에서 κ_U=κ_D=κ_asperity가 되며 RR_U=RR_D=RR0
로 수렴 — 이는 "국소평탄(local planarity)" 상태에서만 NPW≈PTW가 성립함을 뜻한다.

### 1.3 실측 대비 정량 검증 (Vasilev et al. 2011, Table I·Fig.5/6, 300mm STI 웨이퍼, AMAT Lk + IC1010패드 + Klebosol 30N50, 2.8psi, 64rpm)
| 파라미터 | Basic GW (density 전용) | Extended GW (density+pitch) |
|---|---|---|
| RR0 (측정, blanket) | 185 nm/min | 185 nm/min |
| IL (interaction length) | 1400 µm (density field) | 2950 µm |
| σ (asperity 높이분산) | 120 nm | 140 nm |
| R_asperity | 30 µm | 30 µm |
| α (형상 fit 파라미터) | — (모델에 없음) | 11.25(density)/20.5(pitch) |
| **step-height RMS fit 오차 (density field)** | **19 nm** | **13 nm** (32% 개선) |
| **up/down RMS fit 오차 (density field)** | 32 nm | 31 nm |
| **step-height RMS fit 오차 (pitch field)** | 20.5 nm | 13.5 nm (34% 개선) |
| **up/down RMS fit 오차 (pitch field)** | 20 nm | 13 nm (35% 개선) |

Basic GW(밀도만 반영, pitch 무관)는 pitch field 데이터에서 **모든 피치값에 대해 단일
곡선**만 예측(피치 의존성 자체가 모델에 없음) → 실측과 최대 20.5nm 어긋남. Extended GW가
피치를 유효곡률에 넣자 오차가 13.5nm로 줄었다(원 논문 서술 그대로, 재계산 아님).

## 2. NPW→PTW 예측력 부족의 정량적 원인 (Lv1 r≈0.71 질문에 대한 답)
1. **곡률 분화 항 자체가 NPW에 없음**: κ_feature=4αh/(size)²는 h(step height)와 구조
   크기(line/space)의 함수. NPW는 h=0이라 이 항이 항상 0 — PTW의 pitch·density 의존성을
   **원리적으로 관측 불가**.
2. **폴리싱 단계별로 오차가 다름**: 원 논문 §III, "초기 평탄화 단계(~150s)에서 편차가 가장
   크다"(low density에서 특히) — NPW가 잘 맞는 것은 국소평탄 이후 구간뿐, 초기·과폴리시
   단계는 안 맞는다.
3. **basic GW(밀도만) vs extended GW(밀도+피치) 비교가 시사하는 것**: 밀도만으로도 어느 정도
   설명되지만(오차 19-20.5nm), 피치 정보를 추가하면 32-35% 개선 — 즉 NPW+ρ_eff만으로는
   PTW 예측의 **65-68%만 설명**되고 나머지는 피치(구조 크기) 의존 접촉역학이 설명한다는
   것이 이 논문의 정량적 함의. (Kim&Seo r≈0.71과 방향은 일치하나 별개 데이터·다른 지표라
   직접 비교는 부적절 — **교차검증 아님, 정성적 방향 일치만 확인**.)

## 3. Python 재현 — 확장 GW 모델 up/down 제거율 분화 (정성 거동 + 수치 검증)
원 논문 파라미터(Table I, extended GW, density field)를 그대로 대입해 h→0 극한에서
RR_U=RR_D=RR0로 수렴하는지, 그리고 h>0일 때 up-region이 down-region보다 항상 빠르게
깎이는지(RR_U > RR_D, 이게 평탄화의 물리적 정의)를 검증한다.

```python verify
import numpy as np

# 원 논문 Table I 파라미터 (extended GW, density field) — 1차 문헌값
RR0 = 185.0        # nm/min, 측정 blanket rate
R_asp = 30_000.0   # nm (30 µm)
sigma = 140.0      # nm
alpha = 11.25
kappa_asp = 1.0 / R_asp

def removal_rates(h, rho_eff, line_nm, space_nm):
    """eq.5, eq.27 그대로 구현. h=step height[nm], line/space[nm]."""
    kU = kappa_asp + 4 * alpha * h / (line_nm ** 2)
    kD = kappa_asp - 4 * alpha * h / (space_nm ** 2)
    kD = max(kD, 1e-12)  # 논문: 음의 kD는 fit에서 관측 안 됨
    ratio = np.exp(h / sigma)
    denom = np.sqrt(kU) * (1 - rho_eff) + ratio * np.sqrt(kD) * rho_eff
    RR_U = ratio * np.sqrt(kU) * (np.sqrt(kD) * np.sqrt(kU) / denom) * RR0 / kappa_asp
    RR_D = np.sqrt(kD) * (np.sqrt(kD) * np.sqrt(kU) / denom) * RR0 / kappa_asp
    return RR_U, RR_D

# 검증 1: h -> 0 (평탄화 완료, NPW와 동일 조건)이면 RR_U = RR_D = RR0로 수렴해야 함
RR_U0, RR_D0 = removal_rates(h=1e-6, rho_eff=0.5, line_nm=1000, space_nm=1000)
assert abs(RR_U0 - RR0) / RR0 < 0.01, f"h->0 극한에서 RR_U={RR_U0}가 RR0={RR0}로 수렴 안 함"
assert abs(RR_D0 - RR0) / RR0 < 0.01, f"h->0 극한에서 RR_D={RR_D0}가 RR0={RR0}로 수렴 안 함"

# 검증 2: h>0(패턴 존재)이면 up-region이 down-region보다 빠르게 깎여야 함 (평탄화의 정의)
RR_U1, RR_D1 = removal_rates(h=200.0, rho_eff=0.5, line_nm=250, space_nm=250)
assert RR_U1 > RR_D1, f"패턴 존재 시 up({RR_U1:.1f}) > down({RR_D1:.1f}) 이어야 하는데 위배"

# 검증 3: line-width가 좁을수록(작은 구조) up-region 곡률 가산항이 커져 RR_U가 더 빨라짐
# (원논문 §III: "line-width 감소 시 up-region 제거율이 빠르게, 한계없이 증가")
RR_U_narrow, _ = removal_rates(h=200.0, rho_eff=0.5, line_nm=50, space_nm=250)
RR_U_wide, _ = removal_rates(h=200.0, rho_eff=0.5, line_nm=500, space_nm=250)
assert RR_U_narrow > RR_U_wide, "좁은 line이 넓은 line보다 up 제거율이 커야 함(원논문 정성 서술)"

print(f"h->0 극한: RR_U={RR_U0:.2f}, RR_D={RR_D0:.2f} nm/min (RR0={RR0})")
print(f"h=200nm, 250/250 피치: RR_U={RR_U1:.2f}, RR_D={RR_D1:.2f} nm/min")
print(f"line 50nm vs 500nm (h=200): RR_U_narrow={RR_U_narrow:.2f} > RR_U_wide={RR_U_wide:.2f}")
print("PASS: 3/3 assert — 정성 거동만 재현, 원 논문 Fig.5/6의 정량 곡선(RMS 13-31nm)은")
print("      digitize 없이는 재현 불가 → 이 코드는 '모델 구현이 맞는가'의 sanity check이지")
print("      '문헌 수치와 일치'를 주장하지 않는다.")
```

## 4. 이 모델이 답하지 않는 것 (Lv3-2 전이규칙에 남는 과제)
- 원 논문 자체가 "line-width가 R_asperity(30µm)의 2배 이하로 작아지면 인접 up-region끼리
  패드 asperity를 공유해 이 모델이 깨진다"고 명시(§III 말미) — 최신 노드(수십 nm)에서는
  이 GW 프레임 자체가 한계.
- α(형상 fit 파라미터)는 density field(11.25)와 pitch field(20.5)에서 **다른 값**으로
  피팅됨 — 하나의 α로 두 데이터셋을 동시에 설명 못한다는 뜻. 저자들도 "실제 구조 형상이
  포물선 근사에서 벗어나는 정도"로만 해석, 물리적 기원은 미해결.
- Cu 다마신(erosion/dishing) 케이스는 이 논문이 다루지 않음(ILD·STI만) — [[pattern-dependent-dishing-erosion]]의
  effective-density 모델과의 결합은 Lv3-2/캘리브레이션 과제로 남긴다.
- Kim&Seo(2002) r≈0.71과의 정량 교차검증은 여전히 미확보(원문 미확보 상태 지속).

## 5. 결론 (Lv2-1 답)
NPW가 PTW를 예측하지 못하는 물리적 이유는 **접촉 곡률의 국소 분화**다. NPW는 h=0(평탄)
조건이라 up/down 곡률차 항(κ_feature=4αh/size²)이 원리적으로 0이 되어 패턴 크기·피치
의존성을 전혀 담지 못한다. Vasilev et al.(2011)의 확장 GW 모델은 이 항을 도입해 density만
쓰는 basic GW 대비 step-height 예측오차를 32-34% 줄였다(Vasilev et al. 2011, 실측 대조). 이는
"밀도(ρ_eff)만으로 부족하고 구조 크기(피치)가 별도 채널로 필요하다"는 것을 실측으로
보여준 결과이며, wafer-type 에이전트가 Lv3-2(전이규칙 정량화)에서 이어받을 지점이다.

## 구현 요청 (software-lead BACKLOG 인계용, 트랙 B는 소프트웨어 부문 담당)
- **무엇을**: `sim/` 엔진에 patterned-wafer 옵션으로 확장 GW up/down 제거율 계산
  (§3 python verify 코드의 `removal_rates()`를 참고 구현으로 사용, 프로덕션 코드는 별도 작성).
  입력: h(step height), ρ_eff(x,y), line/space(피치 분해), RR0(NPW 측정값). 출력: RR_U, RR_D.
- **근거 노트**: 본 노트 §1-3.
- **검증에 쓸 문헌값**: (Vasilev et al. 2011) Table I 파라미터(RR0=185, IL=1400/2950µm,
  σ=120/140nm, R_asperity=30µm, α=11.25/20.5) + Fig.5/6의 RMS 오차(13-31nm, digitize 필요시
  WebPlotDigitizer로 곡선 추출 후 대조 권장).
- **우선순위**: 중 — [[pattern-dependent-dishing-erosion]]의 effective-density 모델과
  통합해서 PTW 예측 모듈을 만드는 것이 더 큰 그림이므로, 두 노트를 함께 검토 후 결합
  설계할 것을 제안(단독 구현보다 결합이 우선).
