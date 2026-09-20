<!-- V2-SECTION: R2-slurry | 근거: active particle density, load per particle, GW contact, Luo-Dornfeld | 정본: ARCHITECTURE-V2.md §3 -->
# `active_particle_density_per_m2` 입자당 하중 4~6자릿수 갭 재판정

> 작성일: 2026-09-16 | 대상: `knowledge/params/base.yaml::active_particle_density_per_m2`,
> `sim/engine.py::_particle_contact_diagnostic` (커밋 c60365d)
> 선행: [[pad-gw-parameter-literature-adoption-derived-recompute|../pad/pad-gw-parameter-literature-adoption-derived-recompute]],
> [[particle-wafer-interaction-mechanical-chemical-balance]]

## 0. 발견된 문제
`_particle_contact_diagnostic`이 F = P_nominal/η (η=`active_particle_density_per_m2`=4.434e6 /m²)로
입자당 하중을 계산하면 5팩 전부 F≈4.67 mN이 나오고, 소성 압입깊이 δ_p가 입자반경 R보다 수십~수백
배 커져(예: cu 팩 δ_p=12374 nm vs R=50 nm) plowing 근사(δ≪R)가 깨진다. 문헌은 입자당 하중을
수 nN~수백 nN 오더로 본다 — 4~6자릿수 괴리.

## 1. Q1 — F=P/η 유도 자체는 틀리지 않았다

`knowledge/pad/pad-gw-parameter-literature-adoption-derived-recompute.md` §3의 python verify 블록과
`sim/tier2_physics/gw_contact.py::gw_numeric`을 직접 열어 확인:

```
n_contacts = eta_input * A_n * n_frac        # GW 접촉 자리 수 (전체, 개수)
active_particle_density_per_m2 = n_contacts / A_n = eta_input * n_frac   # "자리 수 / 명목면적"
```

즉 `active_particle_density_per_m2`(η)는 **처음부터 명목면적 A_n으로 나눈 값**이다(재적분 노트
§3 `solve()`가 `n/A_n`을 반환해 YAML 값과 1% 이내로 맞춘 것으로 직접 확인). 따라서

```
F = W_total/n_contacts = (P_nominal·A_n)/(η·A_n) = P_nominal/η
```

는 η의 정의와 정합적이다 — `real_contact_area_ratio`(1.393e-3, A_r/A_n)를 분모·분자 어디에도
추가로 곱하거나 나눌 이유가 없다. `real_contact_area_ratio`는 base.yaml 자신의 note가 밝히듯
"명목압력을 입자가 실제로 받는 **응력**으로 환산"하는 별개 용도(p_real=P_nominal/real_contact_area_ratio)이고,
이 진단이 계산하는 것은 응력이 아니라 **입자당 하중**이므로 관여하지 않는다.

**결론: engine.py의 F 유도는 η의 정의(GW 접촉 자리 수/명목면적)와 완전히 일치한다. Q1은 "내 유도가
틀렸다"가 아니라 "유도는 맞다"로 종결.** 갭의 원인은 유도식이 아니라 §2의 가정 자체다.

## 2. Q2 — η의 물리적 의미와 문헌 대조

### 2.1 η가 실제로 세는 것
`gw_numeric()`의 입력은 **패드 물성**(E*, R=pad_asperity_radius_m, 1/β=pad_height_beta_inv_m)과
**패드 돌기(asperity) 밀도** eta_input(=2.0e8 /m², GW 재적분에서 고정값)뿐이다. 슬러리 입자 크기나
농도는 이 적분에 전혀 들어가지 않는다. 즉 η=4.434e6 /m²는 "3 psi에서 **패드 돌기**가 웨이퍼와
접촉하는 자리의 밀도"이지 "슬러리 입자가 몇 개 있는가"가 아니다. base.yaml note가 스스로 "자리
하나에 입자 하나가 들어간다는 **단층 가정**"이라 명시한 것이 바로 이 간극이다 — 패드 돌기 간격
(eta_input=2e8/m² → 간격 ~71 µm, R=50 µm)과 슬러리 입자 간격(입경 50~120 nm)은 단위가 3자릿수
다른 별개의 길이스케일이다.

### 2.2 독립 문헌값 — Luo & Dornfeld 활성입자(active abrasive) 모델
과제가 지목한 Luo & Dornfeld 2001(IEEE Trans. Semicond. Manuf. 14(2) 112-133,
DOI: 10.1109/66.920723)의 원문은 이번에도 유료로 직접 확보하지 못했다(`~/software/BACKLOG.md`
기록과 동일). 그러나 로컬 코퍼스에 **동일 저자(Jianfeng Luo)가 같은 모델을 참고문헌 [1]=바로 이
2001년 논문으로 직접 인용하며 확장한 후속 프리프린트**가 이미 존재한다:

> `papers/luo-dornfeld-material-removal-regions-part1.pdf` — J. Luo, "Material Removal Regions in
> Chemical Mechanical Polishing: Coupling Effects of Slurry Chemicals, Abrasive Size Distribution
> and Wafer-Pad Contact Area, Part 1" (NSF/UC SMART 후원, references [1]=Luo&Dornfeld 2001
> doi:10.1109/66.920723, [2]=동일 저자 2001 제출본). fitz로 직접 렌더해 원문 확인(**E2** — 동일
> 계열 저자가 폐형식을 직접 유도, 2001년 원 논문의 확장판).

이 논문 p.15의 **포화(saturation) 영역** 유도(원문 그대로):
```
A'' = 활성입자 수 × 단일 입자의 눌린 자국 투영면적
포화 시: N = A' / (0.25π·x_avg-a²)        # A'=접촉영역이 활성입자로 "완전히 채워진" 상태
```
즉 포화 상태에서 활성입자 면밀도는 **입자 자신의 투영 단면적으로 그 영역을 빈틈없이 채운 값**
N/A' = 1/(0.25π·d²) = 4/(π·d²) (d=입자 직경)이다. 이것은 "패드 돌기 접촉 자리 수"와 무관하게
**입자 자체의 기하학적 최대 충전밀도**로 정의된 별개의 양이다.

### 2.3 오더 대조 (python verify로 고정)
`active_particle_density_per_m2`(η)는 **명목면적** 기준이므로, Luo의 N/A'(**접촉점유면적** 기준)과
비교하려면 같은 면적 기준으로 맞춰야 한다: η를 `real_contact_area_ratio`(A_r/A_n=1.393e-3)로 나눠
"현재 가정이 함의하는, 접촉영역 기준 활성입자 밀도"로 환산한다(A_r≈Luo의 A'로 취급 — 둘 다 "패드와
웨이퍼가 실제로 맞닿는 영역"이라는 동일 개념이라는 가정, §4 한계에 기록).

```python verify
import math

eta_nominal = 4.434e6                 # /m^2, YAML active_particle_density_per_m2 (A_n 기준)
real_contact_area_ratio = 1.393e-3    # A_r/A_n
eta_real = eta_nominal / real_contact_area_ratio   # "현재 가정"을 접촉영역 기준으로 환산

assert abs(eta_real - 3.183e9) / 3.183e9 < 1e-3, "현재 가정의 접촉영역-기준 밀도"

# 팩별 abrasive_size_nm (base.yaml/각 팩 yaml에서 직접 확인, §2 grep)
sizes_nm = {"oxide_silica": 50.0, "w_fe_oxidizer": 50.0, "sti_ceria": 60.0,
            "cu_h2o2_bta": 100.0, "sic_ceria_h2o2": 120.0}

gaps = {}
for pack, d_nm in sizes_nm.items():
    d = d_nm * 1e-9
    n_over_a = 4.0 / (math.pi * d ** 2)     # Luo 포화 활성입자 밀도, N/A' = 1/(pi/4 d^2)
    gaps[pack] = n_over_a / eta_real

# 문헌(Luo 포화 충전밀도)이 현재 가정보다 항상 크다 — 방향이 하나로 수렴
assert all(g > 1 for g in gaps.values()), "모든 팩에서 문헌값이 현재 가정보다 커야 한다"
# 자릿수: 4~5자릿수 갭 (오더로만 판정, 정밀값 아님 — §4 한계)
assert all(1e4 < g < 1e6 for g in gaps.values()), (
    f"갭이 4~5자릿수 범위를 벗어남: {gaps}")
for pack, g in sorted(gaps.items(), key=lambda kv: kv[1]):
    print(f"{pack}: gap={g:.3e}x (log10={math.log10(g):.2f})")
```

**실행 결과**: 5팩 전부 gap이 2.78e4~1.60e5배(log10 4.44~5.20) — **정확히 과제가 지목한 4~6자릿수
괴리와 오더가 맞는다.** 방향도 하나로 수렴한다: 현재 GW-단층 가정이 Luo의 입자 최대충전밀도보다
**항상, 큰 폭으로 작다.** 즉 η=4.434e6/m²는 슬러리 입자가 실제로 있을 수 있는 밀도에 비해
지나치게 낮은 대용값이다 — "패드 돌기 자리"와 "슬러리 입자"를 동일시한 단층 가정의 실패다.

## 3. Q3 — 판정

**서열 적용**: 현재 η는 GW 수치적분(패드 3키, 문헌값 literature 채택, 판정#40) 그 자체로는 정확하지만
"자리=입자" 등치는 **1차 근거가 없는 가정**(base.yaml 자신이 "단층 가정"이라 명명, 기존
confidence=estimated)이다(**E6 — 추정, 채택금지 등급인 가정**). Luo(2001)를 직접 인용·확장한
동일 저자 폐형식(**E2**)이 이 가정과 반대 방향(4~5자릿수 더 큰 밀도)을 가리킨다. E2가 E6을 이긴다
— 1단계에서 판정 종결.

**(C) 채택 — 단층 가정 자체가 부적절함을 명시하고 경고를 정확하게 고친다. 값은 교체하지 않는다.**

값을 안 바꾸는 이유:
1. `active_particle_density_per_m2`(η=4.434e6/m²) 자체는 "GW 접촉 자리 밀도"라는 **자기 정의** 안에서는
   여전히 유효한 재적분 결과다(판정#40이 GW 3키를 문헌값으로 교체하고 같은 코드로 재적분한 값 —
   그 계산 자체에는 결함이 없다).
2. Luo의 N/A'는 **포화(saturation) 레짐**(접촉영역이 입자로 빈틈없이 채워진 극한)의 **상한**이지,
   "3 psi 대표 운전점에서의 실제 활성입자 밀도"가 아니다 — 슬러리 농도·간극 분포에 따라 포화 미만일
   수 있다. 이 상한을 그대로 η의 **대체값**으로 박으면 반대 방향의 근거 없는 정밀도를 만든다
   (과제 지침이 금지하는 "값을 역산해 맞추는" 것과 같은 함정 — 이번엔 δ_p<R이 아니라 δ_p→0쪽으로
   과잉보정하는 대칭적 오류).
3. Luo의 식은 입자직경 d에 의존하므로 팩마다 다른 상수가 나온다(2.8e13~5.1e14/m², 팩별 abrasive_size_nm
   차이만으로 5.8배 편차) — `base.yaml`의 **팩 공통 단일 상수**라는 현재 구조 자체와 맞지 않는다.
   구조를 바꾸는 리팩터는 이번 과제 범위를 넘는다(§5 후속).
4. 소비처 전수 확인(`grep -rn active_particle_density_per_m2`) 결과 이 키를 쓰는 곳은
   `sim/engine.py::_particle_contact_diagnostic` 단 하나뿐이고, 그 출력은 MRR 계산 경로에 전혀
   들어가지 않는다(모듈 docstring·기존 테스트 `test_mrr_bit_invariant_regardless_of_particle_diagnostic_inputs`가
   이미 고정). 값을 바꾸든 안 바꾸든 qa_loop ρ에는 영향이 없다 — 이는 판정#40이 이미 기록한 사실과
   같다.

대신 다음을 고쳤다:
- `sim/engine.py::_particle_contact_diagnostic`의 δ_p≥R 경고 문구에 **Luo(2001) 문헌 근거로 4~5자릿수
  차이가 있다는 정량 사실**을 추가해, "confidence=estimated"라는 원론적 경고를 "동일 계열 저자의
  독립 폐형식과 4~5자릿수 어긋난다"는 구체적 반증으로 격상했다.
- `knowledge/params/base.yaml::active_particle_density_per_m2`의 note에도 같은 대조 결과와 출처를
  추가해, 이 값을 다른 용도로 재사용하려는 미래 회차가 같은 함정(자리=입자 등치)에 빠지지 않도록
  했다.
- confidence는 **estimated로 유지**한다(격상도 강등도 하지 않음 — 판정#40 원칙과 동일: 이미 단층
  가정이 미검증이라 명시돼 있었고, 이번 결과는 "미검증"을 "검증해보니 방향이 어긋남"으로 구체화한
  것이지 신뢰도를 올릴 근거가 아니다).

## 4. 한계 (정직 기록)
1. Luo & Dornfeld 2001 원문(DOI: 10.1109/66.920723)은 **여전히 미확보**다(유료, BACKLOG 기록과 동일
   결론). §2.2에서 쓴 것은 같은 저자가 그 논문을 [1]로 직접 인용하며 확장한 **후속 프리프린트**의
   폐형식이며, 2001년 원문과 계수가 100% 동일하다는 보장은 없다 — 다만 "활성입자=접촉영역을 자기
   투영면적으로 채우는 입자 수"라는 **정의 자체**는 두 논문이 같은 모델 계열([1-2]로 함께 인용됨)이라
   구조적으로 같다고 본다.
2. §2.3의 갭 계산은 `real_contact_area_ratio`(GW 적분의 A_r)와 Luo의 A'(활성입자가 채우는 접촉영역)를
   **같은 물리량으로 대응**시켰다 — 둘 다 "패드·웨이퍼가 실제로 맞닿는 영역"이라는 정성적 정의는
   같지만, 하나는 GW 돌기 탄성접촉 모델에서, 다른 하나는 Luo의 별도 접촉역학 모델에서 나온 값이라
   **정량적으로 같은 A_r을 가리킨다는 것은 미검증**이다. 이 대응이 깨지면 §2.3의 구체적 배율(2.8e4~
   1.6e5배)은 달라질 수 있지만, "패드 돌기 간격(µm) vs 입자 간격(nm~수백 nm)의 3자릿수 길이스케일
   차이"라는 §2.1의 정성적 결론(자릿수 규모)은 이 대응과 무관하게 성립한다.
3. Luo의 N/A'는 **포화 레짐 상한**이다 — 실제 3 psi 조건이 포화인지 미포화인지는 이 노트로 판별하지
   못한다. §3에서 값을 교체하지 않은 핵심 이유이기도 하다.
4. 입자직경으로 `abrasive_size_nm`(팩 평균/벤더값)을 그대로 썼다 — Luo 원문은 "활성입자 크기 ≈
   x_avg+3s"(평균보다 큰 상위꼬리)라고 명시하므로, 실제 x_avg-a를 쓰면 N/A'는 더 작아져 갭이 줄어들
   방향이다. 다만 §2.3에서 이미 문헌값이 현재값보다 압도적으로 크므로(4~5자릿수), 입경을 5배 크게
   잡아도(→ 밀도 25배 감소) 갭은 여전히 3자릿수 이상 남는다 — 결론(방향과 자릿수 규모)은 이 불확실성에
   robust하다.

## 5. 후속 (범위 밖)
`active_particle_density_per_m2`를 팩별 `abrasive_size_nm` 함수로 바꾸는 구조 변경(§3-③)과, Luo
포화식이 실제 미포화 레짐에서 어떤 배율로 스케일되는지(농도 의존)의 1차 데이터 확보는 이번 과제
범위를 넘는다 — 별도 과제로 남긴다.
