# 디스크 절삭율 결합식의 N 이중계상 — `disk_cutrate_coupled` 반증

> disk-design / S12 엔진 등록 심사 중 발견. 근거 노트: [[disk-design-cutrate-asperity-regeneration-model]]
> (이 모듈의 출처 노트), [[disk-design-pad-roughness-asperity-relation]] (Rpk-N 관계의 다른 소비처).
> **결론: 이 모듈의 종합 결합식은 엔진에 등록하면 안 된다.**
> 두 "독립" 회귀 지수가 실은 같은 3점 데이터의 같은 관계를 두 번 표현한 것이라,
> 곱하면 그릿 개수 N이 이중으로 계상된다.

## 1. 모듈의 주장

`sim/tier2_physics/disk_cutrate_coupling.py` 의 `disk_cutrate_coupled()` 는 주석에서
밀도항과 Rpk항을 **"두 개의 독립된 문헌 회귀 지수"** 라 부르고 둘을 곱한다:

```
CR = CR_ref * (N/N_ref)^(-0.53) * (Rpk/Rpk_ref)^(0.85) * [활성항]
```

출처는 둘 다 Kwon et al. (2013), Tribology International 67, 272-277,
doi:10.1016/j.triboint.2013.08.008 — **같은 논문의 같은 3점 데이터셋**이다.

## 2. 반증 — 두 지수는 독립이 아니다

Kwon 2013의 3점은 모듈 자신의 docstring에 전부 적혀 있다:

| N [grits] | CR [µm/h] | Rpk [µm] |
|---|---|---|
| 17,000 | 37.0 | 3.75 |
| 40,000 | 23.0 | 2.25 |
| 60,000 | 19.0 | 1.70 |

Rpk는 **독립변수가 아니라 N의 함수다**. 같은 3점에서 Rpk ∝ N^(-0.62) 이고
(이 값은 `sim/tier2_physics/disk_gw_relative_scaling.py` 가 이미 Kwon 2013에서
`rpk_relative` 지수로 채택해 쓰고 있다 — 즉 저장소가 이미 이 의존성을 알고 있었다),
따라서 Rpk항은 N항을 다른 좌표로 쓴 것에 불과하다:

    CR ∝ Rpk^0.85 ∝ (N^-0.62)^0.85 = N^-0.527

직접 회귀한 CR ∝ N^-0.53 과 **0.6% 이내로 같은 값**이다. 두 관계는 같은 하나다.

## 3. 곱하면 생기는 오차

```python verify
import math

# Kwon et al. 2013, Tribology International 67, 272-277
# doi:10.1016/j.triboint.2013.08.008
# 3점 데이터는 sim/tier2_physics/disk_cutrate_coupling.py docstring에 인쇄된 값 그대로.
N   = [17e3, 40e3, 60e3]
CR  = [37.0, 23.0, 19.0]
RPK = [3.75, 2.25, 1.70]

def loglog_slope(x, y):
    lx = [math.log(v) for v in x]
    ly = [math.log(v) for v in y]
    n = len(x)
    mx = sum(lx) / n
    my = sum(ly) / n
    num = sum((a - mx) * (b - my) for a, b in zip(lx, ly))
    den = sum((a - mx) ** 2 for a in lx)
    return num / den

e_cr_n   = loglog_slope(N, CR)     # 모듈이 -0.53 이라 부르는 값
e_cr_rpk = loglog_slope(RPK, CR)   # 모듈이 +0.85 라 부르는 값
e_rpk_n  = loglog_slope(N, RPK)    # disk_gw_relative_scaling 이 -0.62 로 쓰는 값

# (1) 모듈이 인용한 지수들이 원 데이터에서 실제로 재현되는지
assert abs(e_cr_n   - (-0.53)) < 0.01, e_cr_n
assert abs(e_cr_rpk - ( 0.85)) < 0.01, e_cr_rpk
assert abs(e_rpk_n  - (-0.62)) < 0.01, e_rpk_n

# (2) 핵심: 연쇄(Rpk 경유)와 직접 회귀가 같은 관계인가
chained = e_cr_rpk * e_rpk_n
assert abs(chained - e_cr_n) < 0.01, (chained, e_cr_n)
# => -0.527 vs -0.533. 두 "독립" 지수는 같은 관계다.

# (3) 곱하면 N 지수가 대략 두 배가 된다 (이중계상)
double_counted = e_cr_n + chained
assert abs(double_counted / e_cr_n - 2.0) < 0.02, double_counted

# (4) 실제 예측 오차 크기 — N을 기준의 3.5배로 올렸을 때
n_ratio = 60e3 / 17e3
correct  = n_ratio ** e_cr_n           # 올바른 단일 적용
wrong    = n_ratio ** double_counted   # 두 항을 곱했을 때
assert abs(correct - 0.5108) < 1e-3, correct
assert abs(wrong   - 0.2614) < 1e-3, wrong
assert wrong < correct / 1.9, (wrong, correct)
# => 절삭율을 1.95배 과소예측한다.
print("OK: chained=%.4f direct=%.4f  correct=%.4f wrong=%.4f ratio=%.2f"
      % (chained, e_cr_n, correct, wrong, correct / wrong))
```

즉 그릿 개수를 3.5배로 바꾸는 what-if 에서 결합식은 절삭율을 **1.95배 과소예측**한다.
N과 Rpk를 사용자가 **서로 독립인 것처럼** 입력할 수 있는 API라 이 오차는 조용히 발생한다.

## 4. 판정

**`disk_cutrate_coupled` / `cutrate_rpk_scaling` 를 엔진에 등록하지 않는다.**

- 두 항 중 하나만 써야 한다. 어느 쪽이든 같은 관계를 표현하므로 **더 직접적인 축**
  (설계자가 실제로 고르는 값 = 그릿 개수 N)을 쓰는 `cutrate_density_scaling` 만이 유효하다.
- Rpk는 N의 **결과**이지 독립 설계입력이 아니다. Rpk를 따로 측정한 경우에만
  (즉 N을 모르고 Rpk만 아는 경우) `cutrate_rpk_scaling` 을 **단독으로** 쓸 수 있다.
- 활성 그릿 항은 모듈 자신이 지수 g를 "미확정, 캘리브레이션 파라미터"라 선언해
  애초에 적용 불가다.

> ⚠ 이 판정은 Kwon 2013 원문을 확보하지 못한 채 **모듈 docstring에 인쇄된 3점**만으로
> 내렸다. 원문에 N과 Rpk를 독립적으로 변화시킨 (예: 같은 N에서 dressing 조건으로 Rpk만
> 바꾼) 추가 실험군이 있다면 결합식이 정당해질 여지가 있다. 그 경우 이 노트를 재판정하라.
> 다만 현재 저장소에 있는 근거만으로는 두 축이 완전히 공선(collinear)이다.


## 6. 정량 재현 대조표 (단위 포함)

모듈 docstring이 인용한 지수와, 같은 3점에서 이 노트가 직접 회귀한 값의 대조:

| 항목 | 모듈/저장소가 쓰는 값 | 이 노트 재회귀 | 차이 |
|---|---|---|---|
| CR ∝ N^a (a) | −0.53 (`cutrate_density_scaling`) | −0.532681 | 0.5 % |
| CR ∝ Rpk^b (b) | +0.85 (`cutrate_rpk_scaling`) | +0.853207 | 0.4 % |
| Rpk ∝ N^c (c) | −0.62 (`disk_gw_relative_scaling.rpk_relative`) | −0.622619 | 0.4 % |
| b·c (연쇄) | — | −0.531223 | a 대비 **0.27 %** |

절삭율 절대값 대조 (N: 17,000 → 60,000 grits, CR_ref = 37.0 µm/h 기준):

| 방식 | 예측 CR 배율 | 예측 CR [µm/h] | 실측 [µm/h] | 오차 |
|---|---|---|---|---|
| 단일 적용 (올바름) | 0.510798 | 18.90 | 19.0 | −0.5 % |
| 두 항 곱 (이중계상) | 0.261395 | 9.67 | 19.0 | **−49.1 %** |

즉 이중계상은 Kwon 2013 자신의 3번째 데이터점을 **49 % 과소예측**한다 —
모듈의 결합식은 그것을 유도한 원 데이터조차 재현하지 못한다.

## 7. 미검증·한계 (정직성 표지)

- **Kwon et al. 2013 원문 미확보 (1차 출처 미확인).** 이 노트의 3점 수치는
  `sim/tier2_physics/disk_cutrate_coupling.py` 와 `disk_gw_relative_scaling.py` 의
  docstring에 **인쇄된 2차 전사값**이다. 전사 자체가 틀렸을 가능성은 배제하지 못했다
  (다만 두 모듈이 서로 독립적으로 같은 3점을 적어두었고 지수도 일치한다).
- **원문에 N·Rpk 독립 변화 실험군이 있는지 확인 못 함 (미검증).** §4의 재판정 조건이
  바로 이것이다. 현재 근거만으로는 두 축이 완전 공선이라고 판단했다.
- **Tsai et al. 2014의 활성 그릿 잔차 1.75배는 이 노트가 검증하지 않았다** — 활성항은
  지수 g가 미확정이라 애초에 적용 불가라서 판정 대상에서 제외했다(추정 영역).
- **여기서 제안한 "N만 쓴다"가 물리적으로 옳다는 독립 근거는 없다.** 두 축이 공선일 때
  더 직접적인 설계 입력을 고른다는 것은 모델링 관례이지 이 논문이 검증한 사실이 아니다.

## 5. 부수 확인 — 기존 코드에는 영향 없음

`disk_cutrate_coupled` 의 소비처를 grep으로 전수 확인한 결과 `sim/` 에는 없고
모듈 자신의 `_self_test()` 뿐이다. 즉 **이 결함은 아직 어떤 출력에도 반영되지 않았다** —
등록을 막은 것으로 충분하며 기존 값은 하나도 바뀌지 않는다.
