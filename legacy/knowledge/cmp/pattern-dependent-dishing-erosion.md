<!-- V2-SECTION: R5-wafer | 분배완료 2026-09-08 | 근거: dishing, erosion, pattern- | 정본: ARCHITECTURE-V2.md §3 -->
# 패턴 의존성 — dishing/erosion & 밀도효과 모델 (MIT effective-density / step-height)

> process-integrator Lv3-1 | 작성일: 2026-09-05
> 관련: [[wiwnu-pressure-velocity-wafer-scale]] (국소압 증폭이 여기서 die-level로 이어짐),
> [[preston-luo-dornfeld-mrr]] (blanket rate K=Kp·P·V가 밀도로 나뉨),
> [[hertz-gw-contact-mechanics]] (raised area만 접촉→국소압↑의 미시근거),
> [[cmp-tool-architecture]] (웨이퍼스케일 vs die스케일 비균일도 구분)

## 1. 왜 필요한가 — WIWNU 아래의 die-level 변동
[[wiwnu-pressure-velocity-wafer-scale]]까지는 웨이퍼를 반경 프로파일 P(r)·V(r)로만 봤다.
그러나 실제 칩 안에서는 **레이아웃 패턴(금속선 밀도·피치)** 때문에 같은 웨이퍼 위 die
안에서도 제거량이 위치마다 다르다. Boning 그룹은 이 die-level 변동이 웨이퍼스케일 변동에
**필적하거나 더 크다**고 지적한다 — ILD CMP 실측에서 within-die 5000–8500Å, across-wafer도
비슷한 스케일(Boning et al. 1999, Fig.9). 즉 공정 최적화는 wafer-level만큼 die-level을 봐야 한다.
핵심 물리는 [[hertz-gw-contact-mechanics]]와 같다: 패드는 **볼록한(raised) 영역만** 만지므로
국소압이 명목압의 1/ρ배(ρ=국소 패턴밀도)로 증폭되고, 이것이 밀도 의존 제거율을 낳는다.

핵심 출처(1차, 오픈액세스로 원문 확인):
- D. Boning, B. Lee, C. Oji, D. Ouma, T. Park, T. Smith, T. Tugbawa, "Pattern Dependent
  Modeling for CMP Optimization and Control," *MRS Spring Meeting, Symp. P*, San Francisco,
  Apr. 1999. https://boning.mit.edu/wp-content/uploads/2022/11/MRS99-reprint.pdf (PDF 원문 확인)
- T. Park, T. Tugbawa, J. Yoon, D. Boning, et al., "Pattern and Process Dependencies in Copper
  Damascene CMP Processes," *VMIC*, Santa Clara, Jun. 1998.
  https://boning.mit.edu/wp-content/uploads/2022/11/Pattern-and-Process-Dependencies-in-Copper-Damascene-Chemical-Mechanical-Polishing-Processes.pdf (PDF 원문 확인)
- (기초 정립) B. Stine, D. Ouma, R. Divecha, D. Boning et al., "Rapid Characterization and
  Modeling of Pattern-Dependent Variation in CMP," *IEEE Trans. Semicond. Manuf.* 11(1), 1998;
  D. Ouma, PhD thesis "Modeling of CMP for Dielectric Planarization," MIT EECS, 1999,
  https://dspace.mit.edu/handle/1721.1/9704 — **원문 미독, MRS99가 [1,2,4]로 인용한 것을 2차 인용**.
  Stine 논문의 실체는 doi.org/10.1109/66.661292 (B. Stine et al., "Rapid Characterization and
  Modeling of Pattern-Dependent Variation in Chemical-Mechanical Polishing," IEEE Trans.
  Semicond. Manuf. 11(1), 1998) — `tools/find_open_access.py --title`로 확인한 DOI. 초록만
  확인, 본문은 유료벽이라 **초록만 확인**(§2 PL 6–8mm 수치의 원문 대조는 여전히 미완).

## 2. Effective density(유효밀도)와 planarization length
밀도 모델의 심장은 **유효밀도** ρ_eff다. 국소 설계밀도 ρ_local(x,y)를 그대로 쓰지 않고,
패드가 하중을 주변으로 퍼뜨리는 범위(=탄성 굽힘 스케일)로 **가중평균**한다:

  ρ_eff(x,y) = ( w ⊛ ρ_local )(x,y)   — 가중필터 w와 2D 컨볼루션(또는 FFT)

- **planarization length (PL)** = 가중필터 w의 특성길이 = "얼마나 먼 이웃 지형이 이 지점의
  폴리싱에 영향을 주는가"의 거리. 초기(Stine)는 **정사각 균일창**, 이후(Ouma) **원형 대칭
  타원(elliptic) 가중**이 훨씬 잘 맞음을 발견 — 이 타원형은 국소하중 폭 L 아래 탄성체(패드)
  변형 프로파일 w(r)에서 물리적으로 유도된다(MRS99 eq.2, 탄성계수 E·포아송비 ν·하중 q의
  적분형). 여기 노트의 재현 코드는 이 elliptic 적분형 대신 **정규화 가우시안**으로 근사했다
  (핵심 성질만 재현, 정확한 elliptic 커널은 **미검증**).
- **PL 전형값**: 산화막(ILD) CMP에서 **3–5 mm** (Park VMIC98 본문, 원문 인용 "on the order of
  3 mm to 5 mm for conventional oxide polish"). 별도 2차 검색스니펫은 Ouma가 조건별 6.2–7.8 mm를
  보고했다고 하나 원문 대조 못함 — **미검증(2차 인용)**. 오더(수 mm)만 신뢰.

**제거율(density model, MRS99 eq.1):**  RR_up(x,y) = K / ρ_eff(x,y)
- K = blanket(비패턴) 제거율. ρ_eff가 크면(밀한 곳) 국소압 분산 → 느림 → 두껍게 남음.
- 결과적으로 **최종 산화막 두께맵 ∝ ρ_eff 맵** (MRS99 본문). 이게 특성화 마스크로 PL을
  역추출하는 원리.

## 3. Step-height 소멸 두 레짐 + 통합모델
"국소 step height h"(볼록/오목 산화막 높이차)의 시간거동은 패드 압축성 가정에 따라 갈린다.
- **비압축성(incompressible) 패드 (Grillaert)**: 패드가 오목(down)영역에 안 닿음 → up만
  K/ρ로 깎임 → **step 이 선형 감소**, 시각 t_c = ρ·h0/K 에 소멸. (MRS99가 채택한 기본가정,
  이 가정만으로 raised/down 산화막 RMSE < 300Å 적합.)
- **압축성(compressible) 패드 (Burke, Tseng)**: step 축소율 ∝ 남은 step → **step 지수감쇠**
  h(t) = h_c·exp(−(t−t_c)/τ). 국소압차가 step과 함께 줄어 점점 덜 깎임.
- **통합모델 (Smith et al.)**: 큰 step 동안 비압축성 → 접촉높이 h1에서 압축성으로 전이. 접촉높이가
  유효밀도에 종속:  **h1 = a1 + a2·exp(−ρ/a3)** (MRS99 eq.4). 이 통합으로 down-area RMSE가
  273Å→98Å, 253Å→83Å로 감소(MRS99 Fig.6,8) — feedback 제어에 쓸 수준.

## 4. Cu dishing / oxide erosion — 정의·측정·overpolish
**정의(Park VMIC98 원문):**
- **Dishing** = "CMP 후 최종 oxide 면과 copper 라인 내 최저점 사이 수직거리" — Cu 라인이
  움푹 파인 깊이. (측정: 프로파일로미터/AFM 스캔에서 oxide 레벨 대비 Cu 함몰.)
- **Erosion** = "증착 시 oxide 두께와 CMP 후 oxide 두께의 차" — 라인 어레이 위 산화막이
  통째로 얇아진 양(보통 인접 비패턴 필드 대비).
- **총 Cu 두께손실 = 필드 oxide loss + 국소 oxide erosion + Cu dishing** — 셋 다 overpolish로 증가.

**overpolish 3단계(damascene, MRS99 Fig.12):** ①벌크 Cu 제거 ②배리어/라이너 제거(여기서 dishing
시작) ③over-polish(잔류 Cu/배리어 완전제거 위해 필수 → dishing·erosion 본격화). 클리어링을 위해
overpolish는 불가피하므로 dishing/erosion은 **원리적으로 0이 될 수 없다**.

**패턴 의존 실측 트렌드(Park VMIC98):**
- 50% 밀도에서 **총 정규화 Cu 손실 ∝ log(pitch)** (큰 피치 영역, 선형). 피치 클수록 dishing↑.
- **break point ≈ oxide 라인스페이스 100 µm**: 스페이스 > ~100µm면 oxide가 패드를 지지 못해
  가속 폴리싱 → erosion↑·dishing↓급감. 밀도 60–70%(스페이스 100–75µm)에서 dishing 최대 후 급락.
- **Cu의 interaction distance(=PL 상당) ≈ 50–100 µm**로 산화막(3–5 mm)보다 **수십 배 짧다**
  (Park VMIC98 원문). → Cu CMP는 국소성이 강해 die-level보다 feature-level 모델이 중요.

**overpolish 정상상태 dishing (removal-rate diagram, MRS99 Fig.13):** dishing이 깊어질수록 Cu 제거율은
선형 감소(d=dmax에서 패드 접촉소실→0), oxide 스페이스 제거율은 선형 증가. 둘이 같아지는
**정상상태 d_ss**가 그 구조에서 관측되는 **최대 dishing**(W CMP의 Elbel et al.과 동일 개념).
STI에서는 같은 틀이 oxide dishing·nitride erosion으로 나타난다(nitride 가속 erosion은 밀도효과만으론
설명 안 됨 — MRS99가 남긴 미해결 이슈).

## 5. Python 재현 (sim/tier1_empirical/pattern_density.py — self-test 9/9 PASS)
검증 항목(문헌 서술과 대조):
1. **유효밀도 필터 정규화**: 합=1 → 균일밀도 입력이면 동일 출력(편향 없음), max dev 1e-16.
2. **step 밀도 평활**: ρ_eff가 step 밀도(0.2↔0.8)를 PL 스케일로 매끄럽게, **overshoot 없음**
   (0.2–0.8 범위 유지). → "ρ_eff는 국소밀도의 PL-가중평균" 성질 확인.
3. **밀도 모델 불변량**: step 구간에서 (제거량 × ρ_eff) = K·t (spread 0) — 즉 **제거량 ∝ 1/ρ_eff**.
   밀한 곳 ρ=0.8은 1875Å, 성긴 곳 ρ=0.4는 3750Å 제거(2배) → "밀한 곳 덜 깎여 두껍게 남음" 정량.
4. **비압축성 step**: t_c = ρ·h0/K 에 정확히 소멸(선형 감소) 확인.
5. **압축성 step**: 합성 지수감쇠(1% 노이즈)에서 τ_true=0.8 → τ_fit=0.8012 (회수오차 <2%).
6. **접촉높이 h1 = a1+a2·exp(−ρ/a3)**: 밀도↑ → h1↓ → a1로 수렴, 단조 확인.
7. **정상상태 dishing**: d_ss=322.6Å에서 Cu rate=oxide rate(2516.1, 대입 일치) 확인.
   추가 sanity: **필드 oxide 제거율↓ → dishing↑**(322.6→503.6Å) — Cu가 느린 필드를 따라가느라
   더 깊이 파임. (실측 절대값 검증 아님, 모델 내부정합·부호방향만 확인 — 절대 dishing값 **미검증**.)

한계/미검증: (a) 정확한 elliptic 가중커널(MRS99 eq.2 적분형) 대신 가우시안 근사 — 오더/평활성만
재현. (b) K, PL, τ, a1..a3, dmax, b 등은 실측 특성화로 뽑는 값이라 여기 수치는 예시(합성). 절대
dishing/erosion nm값은 실험 캘리브레이션 없이는 **미검증**. (c) Stine 1998·Ouma 1999 원논문은
미독 — MRS99/VMIC98의 인용을 **2차 인용**한 부분(§2 PL 6–8mm 등)은 원문 대조 필요.

## 6. 공정통합 관점 결론
- **밀도효과 = die-level WIWNU의 물리**: [[wiwnu-pressure-velocity-wafer-scale]]의 P(r) 반경모델
  위에, die 안에서는 ρ_eff(x,y)가 국소압 1/ρ 증폭으로 제거율을 재분포시킨다. 두 스케일은 곱해진다.
- **Tier 배치**: 밀도 모델(RR=K/ρ_eff)은 파라미터가 (K, PL) 둘뿐이라 Tier1으로 즉시 구현가능.
  통합 step-height(τ, h1(ρ))·Cu removal-rate diagram(dmax, d_ss)은 Tier2로, 특성화 마스크 데이터가
  있어야 계수를 채운다.
- **레이아웃↔공정 결합점**: dummy fill(밀도 균일화)로 ρ_eff 편차를 줄이는 게 die-level 평탄화의
  1차 레버 — 밀도 모델이 바로 그 dummy fill 규칙의 근거다.

## 8. 검증 (sim 재현, 실제 실행)
아래 블록은 `tools/verify_claims.py`가 실제로 실행한다. §5의 self-test(T3·T4·T7)를
assert로 재확인 — 밀도-제거율 반비례 불변량, 비압축성 step 소멸시각, 정상상태 dishing 대입.

```python verify
import sys
sys.path.insert(0, "sim/tier1_empirical")
from pattern_density import (
    oxide_removed_up, step_height_incompressible, steady_state_dishing,
)
import numpy as np

# T3 재현: 밀도 모델 불변량 removed*rho_eff = K*t (step 구간)
K, h0, t = 3000.0, 6000.0, 0.5
rho_in = np.array([0.4, 0.6, 0.8])  # t_c=rho*h0/K=rho*2 > t=0.5 만족
removed = oxide_removed_up(t, K, rho_in, h0)
invariant = removed * rho_in
assert np.allclose(invariant, K * t, rtol=1e-9), f"불변량 불일치: {invariant} vs {K*t}"
assert np.all(np.diff(removed) < 0), "밀도 높을수록 덜 깎여야 한다(단조감소)"

# T4 재현: 비압축성 step은 t_c = rho*h0/K 에서 정확히 소멸
rho1 = 0.5
t_c = rho1 * h0 / K
h_at = step_height_incompressible(t_c, K, np.array([rho1]), h0)[0]
assert h_at <= 1e-6, f"t_c에서 step이 0으로 소멸해야 하는데 h={h_at}"

# T7 재현: 정상상태 dishing d_ss에서 Cu rate == oxide rate
RR_m, RR_ox, rho_m, dmax, b = 3000.0, 1000.0, 0.5, 2000.0, 0.0008
d_ss = steady_state_dishing(RR_m, RR_ox, rho_m, dmax, b)
r_cu = RR_m * (1 - d_ss / dmax)
r_ox = RR_ox / (1 - rho_m) * (1 + b * d_ss)
assert abs(r_cu - r_ox) / r_ox < 1e-6, f"d_ss에서 두 rate가 같아야: {r_cu} vs {r_ox}"

print(f"OK: invariant={invariant[0]:.1f} (K*t={K*t}), t_c={t_c:.3f}min, d_ss={d_ss:.1f}A")
```

한계: 이 검증은 **모델 내부정합**(수식이 자기 정의대로 동작하는지)만 확인한다.
K=3000 Å/min, PL=3mm 등은 실측 캘리브레이션 없는 예시값 — 절대 dishing/erosion nm값의
문헌 대조는 §5에 적었듯 여전히 **미검증**이다.

## 9. 자기시험
→ [[../../agents/process-integrator/EXAMS.md]] Lv3-1 문항 참조.
