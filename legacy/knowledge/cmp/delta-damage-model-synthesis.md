<!-- V2-SECTION: R2-slurry | 공동: R4-disk | factor: delta -->
# Δ(손상 유발도) 모델 종합 — D99 꼬리 × 응집 × 스크래치 치수 상한, 5팩 폐형식 정리

> 작성 2026-09-14 | 종합 대상(전부 기확보 노트, 새 탐색 없음):
> [[lpc-scratch-density-tail-correlation]](Remsen 2006 LPC–스크래치 선형, 임계 0.68 µm) ·
> [[abrasive-d99-scratch-hitachi-us8439995]](세리아 D99–스크래치 4점, n=1.44; §9 등급 판정) ·
> [[w-cmp-abrasive-agglomeration-scratch-multiplier-egan-kim2019]](텅스텐 응집 배수, n_temp/n_agit) ·
> [[abrasive-d99-alumina-search-and-generic-ratio]](Levitronix/Silco 2008 D99/D50 일반비) ·
> [[abrasive-d99-composite-particle-versum2019]] · [[abrasive-d99-spec-cross-pack-comparison]] ·
> [[abrasive-d99-alumina-fourth-attempt-guo-nanoalumina]] · [[colloid-zeta-dlvo-slurry-stability]] ·
> [[scratch-physics-source-signatures]](Saka 2008/Eusner 2009 단일입자 접촉역학 상한) ·
> [[../slurry/colloidal-destabilization-lpc-defect-mechanism]](Basim & Moudgil 2002 응집 ×2) ·
> [[delta-scratch-damage-d99-oversize-particle-model]](3팩 활성화, 일반비 유도 경로)

## 1. 목적 — 흩어진 근거를 한 식으로 닫는다

Δ는 `sim/factors.py::_f_delta`가 계산하는 **진단 전용** 팩터다(`MRR_COUPLED` 밖, MRR에 곱하지
않는다 — Egan & Kim 2019 §3.4가 텅스텐 벌크 CMP에서 "대입자는 제거율을 올리지 않고 스크래치만
늘린다"고 실측했으므로 이 분리는 설계가 아니라 물리다). 지금까지 8편의 노트가 각각 (a) 함수형,
(b) 지수, (c) 응집 배수, (d) D99 절대값 유도, (e) 등급 판정을 따로 확보했다. 이 노트는 그것을
**하나의 관계식 + 팩별 파라미터 표 + 재현 코드**로 닫고, 종합 과정에서만 보이는 새 지식(§6)을
도출한다. 새 문헌은 찾지 않았다.

## 2. 관계식 — 문헌이 지지하는 항만

```
Δ = (D99 / D99_ref)^n  ×  (1 + a)          … 기준 조건(D99 = D99_ref, a = 0)에서 정확히 1.0
      └─ ① 꼬리 항          └─ ② 응집 항
진단 출력(배수가 아니라 절대 치수·위치, MRR/Δ 값에 영향 없음):
  ③ 임계 위치   D99 / d_c ,  d_c = 680 nm(Remsen 2006; Kwon 2023 700 nm; Eusner 2009 응집체 610~762 nm)
  ④ 치수 상한   2a_max = D99·√(H_p,max / H_film) ,  δ_max = (D99/2)·(H_p,max / H_film)   (Eusner 2009 식(10)(11))
```

| 항 | 문헌 | 채택 형태 | 왜 이 형태인가 |
|---|---|---|---|
| ① D99 거듭제곱 | Hitachi US8439995B2 4점(세리아) 로그-로그 회귀 n=1.44, R²=0.997; Egan & Kim 2019 텅스텐 배수 2점(n 1.73/3.73, 기하평균 2.54) | `(D99/D99_ref)^n`, n은 팩별 `damage_exponent` | 임계 초과 입자 **개수**축에서는 선형(Remsen Table V)이고, 대표 직경 D99 축으로 옮기면 꼬리 기울기를 타고 완만한 거듭제곱이 된다(§6-1이 이 변환을 정량화) |
| ② 응집 배수 | Basim & Moudgil 2002 Table 1 — NaCl 0.2 M(CCC 0.25 M 미달)에서 **평균 입경 불변**인데 Rmax 25→50 nm(×2) | `1 + aggregate_ratio`, a=1이 "그 논문의 불안정화 정도" | D99가 못 잡는 일시적(transient) 응집체 경로가 D99 항과 **독립**으로 존재함을 실측이 보였다. 단일점(n=1)이라 곱셈 계수 2.0의 일반화는 미검증 |
| ③ 임계 위치 | Remsen 2006(퓸드실리카, LPC 상관 Y절편=0인 최소 직경 0.68 µm), Kwon 2023(세리아 0.7 µm), Eusner 2009(Cu를 긁은 응집체 R_exp 305/381 nm → 2R 610/762 nm) | 배수가 아니라 **위치 진단**(D99가 임계 아래/근처/위) | 세 독립 출처·세 화학종이 0.6~0.8 µm에 수렴 — "스크래치로 셀 만큼 깊은" 사건의 문턱. 배수로 넣지 않는 이유: 임계 아래에서도 카운트가 0이 아니고(Remsen 절편은 회귀 절편일 뿐) 팩 5개 중 3개가 임계 아래라 계단 항은 기준 1.0 계약과 충돌한다 |
| ④ 치수 상한 | Saka 2008 식(14)(15) / Eusner 2009 식(9)~(11), Table IV; H_p,max = 0.31 GPa(IC1000 습윤 Berkovich 36회 최대) | 절대 치수 출력(nm) | 상한은 **연마압력·패드 토포그래피에 무관**하고 **패드 경도의 최대값**과 막 경도만으로 정해진다(Eusner 결론). 곱셈 항이 될 수 없는 이유: 한 팩 안에서 막 경도는 상수라 기준 대비 비가 항상 1.0 — 드라이버가 아니다 |

**넣지 않은 항과 이유**
- **입자/막 경도비 배수**: 문헌은 스크래치 *치수 상한*이 막 경도(H_film)와 패드 최대 경도로 정해진다고
  말할 뿐(④), 스크래치 *개수*가 입자 경도에 어떻게 비례하는지 정량 관계를 준 문헌이 종합 대상에 없다.
  게다가 실리카 입자(H≈7.3 GPa)는 SiO₂ 막(≈9~10 GPa)보다 오히려 무르다
  ([[abrasive-hardness-hertz-indentation-removal-volume]] §4) — "리지드 인덴터" 가정 자체가 실리카계에서
  깨지므로 경도비를 단조 배수로 넣으면 실리카 팩에서 틀린 방향을 가리킨다. → 배수 제외, ④의 상한만 출력.
- **제타전위·이온강도 → 응집도 유도**: DLVO 정성 형태(장벽 존재/소멸)는 [[colloid-zeta-dlvo-slurry-stability]]
  §4가 재현했으나, 팩 5개 어디에도 제타전위·이온강도 실측값이 없고(oxide_silica.yaml이 "지어내지 않음"으로
  명시) Basim & Moudgil의 장벽값(720→167 kT)도 상수-전하 근사 결과값만 있어 입력값을 재구성할 수 없다.
  → `aggregate_ratio`는 유도하지 않고 **선언 입력**으로 둔다(기본 미선언 = "이 경로 미조사", 0 = 무영향).
- **LPC 개수축**(Fujifilm US10907074 "LPC/wt% < 800,000 @0.2 µm"): 현재 팩이 개수 입력을 받지 않는다 —
  축 신설은 구현 과제로 이관(변경 없음).

## 3. 팩별 파라미터 표 — 값·유도 방법·등급

| 팩 | 연마입자/막 | D50 (nm) | `abrasive_d99_nm` = `abrasive_ref_d99_nm` | 도출 방법 | D99 등급 | `damage_exponent` | n 출처 | n 등급 | Δ 등급(최약) |
|---|---|---|---|---|---|---|---|---|---|
| sti_ceria | 세리아/SiO₂ | 60 | **700** | Hitachi US8439995B2 Ex.1 실측 이식(화학종·용도 일치, E2) | literature | 1.44 | Hitachi 4점 회귀 | literature | **literature** |
| sic_ceria_h2o2 | 세리아/SiC | 120 | **700** (sti_ceria 상속) | 상동 | literature | 1.44 | 상동 | literature | **literature** |
| oxide_silica | 콜로이달 실리카/SiO₂ | 50 | **250** | D50 × 일반비 5.00(Levitronix/Silco 2008) — **직접값 아님** | estimated | 1.44 | Hitachi(막질 일치·입자 불일치) | literature | estimated |
| cu_h2o2_bta | 알루미나/Cu | 100 | **500** | D50 × 5.00 — 직접값 아님. Showa Denko US6770218 "more preferably 0.5 µm" 상한과 경계 일치 | estimated | 2.54 | Egan & Kim 기하평균(W→Cu 전이) | estimated | estimated |
| w_fe_oxidizer | 알루미나/W | **50**(Bielmann 1999) | **250** ← 이번 정정(750에서) | D50 × 5.00 — 직접값 아님 | estimated | 2.54 | Egan & Kim(막질·공정 일치) | literature | estimated |

**이번 회차의 정정(w_fe_oxidizer)**: 팩의 `abrasive_size_nm`이 150 → 50 nm(Bielmann 1999 실측)로 승격된
뒤에도 D99는 옛 D50(150)×5.00 = 750 nm로 남아 있었다 — 유도값이 유도 입력과 어긋난 상태. 유도 절차대로
50×5.00 = **250 nm**로 재계산하고 `_ref`를 같은 편집에서 함께 옮긴다(기준 Δ=1.0 불변, 예측 형상 불변).
부수 효과: 750 nm는 Remsen 임계(680)를 넘는 유일한 팩이었는데 정정 후 5팩 전부 임계 아래로 들어간다 —
"이 팩만 꼬리가 임계 위"라는 이전 진단은 **옛 D50의 잔재**였다.

**등급을 올리지 않은 이유(정직 표기)**: [[abrasive-d99-scratch-hitachi-us8439995]] §9(EVIDENCE-RULES 판정#16)가
일반비 5.00을 유일한 실측 D99/D50 대응쌍(Hitachi 4점)에 대면 30~60% 괴리, 비교예는 반대 방향 2배 —
**재현되지 않는다**고 판정했다. 유도값을 `literature`로 올리려면 알루미나·실리카 자체의 D99/D50 실측이
필요하다(5회 탐색 실패). 이 노트는 그 판정을 뒤집을 새 근거를 갖고 있지 않으므로 estimated를 유지한다.
Δ 배수는 `D99/D99_ref` 비만 쓰므로, 사용자가 what-if D99를 **D50 배수로** 넣는 한 일반비 선택(4.29/5.00)에
불변이다(§5-C) — 그러나 절대 nm를 직접 넣으면 기준점 절대값이 결과에 들어가므로 등급을 부풀릴 수 없다.

## 4. 공통 파라미터(base.yaml, 진단 전용) — 이번에 추가

| 키 | 값 | 출처 | 등급 | 쓰임 |
|---|---|---|---|---|
| `scratch_threshold_nm` | 680 | Remsen et al. 2006 JES 153(5) G453, doi:10.1149/1.2184036 (LPC 상관 절편 0인 최소 직경, 실리카 등가); 교차: Kwon 2023 700 nm, Eusner 2009 응집체 610/762 nm | literature | ③ 임계 위치 진단 `D99/d_c` |
| `pad_asperity_hardness_max_pa` | 3.1e8 | Eusner et al. 2009 JES 156(7) H528, doi:10.1149/1.3121964 Fig.15 (IC1000 습윤 Berkovich 36회, 평균 0.05·최대 0.31 GPa) | literature | ④ 치수 상한 — 상한을 정하는 것은 평균이 아니라 **최대** 경도 |

둘 다 드라이버가 아니다(기준 대비 배수를 만들지 않음) — `_f_delta`의 `status` 판정(terms == drivers)에
들어가지 않고 notes로만 나간다. 미선언 팩에서는 진단 줄이 빠질 뿐 Δ 값은 같다.

## 5. 수식 재현 (verify) — 문헌값 재현 + 설계 계약

```python verify
import numpy as np
from math import erf, sqrt, exp, pi, log

# ── (A) US8439995B2 (Hitachi) 세리아 D99–스크래치 4점 → damage_exponent 재현 ──
d99 = np.array([500., 700., 2500., 2500.])     # Ex.2, Ex.1, Comp.1, Comp.2 [nm]
scr = np.array([10., 20., 100., 100.])         # 스크래치 카운트(원문 표)
ref = d99 == 500.0                             # 원 노트와 같은 원점통과(ref=Ex.2) 회귀
ld, ls = np.log(d99 / 500.0), np.log(scr / 10.0)
n_fit = float(np.sum(ld[~ref] * ls[~ref]) / np.sum(ld[~ref] ** 2))
pred = 10.0 * (d99 / 500.0) ** n_fit
r2 = 1 - np.sum((scr - pred) ** 2) / np.sum((scr - scr.mean()) ** 2)
print(f"(A) Hitachi 원점통과 로그-로그 회귀 n={n_fit:.3f}, R²={r2:.3f}  (문헌값 1.444 / 0.997)")
assert abs(n_fit - 1.444) < 0.005 and r2 > 0.99, "Hitachi n=1.444/R²=0.997 재현 실패"

# ── (B) Egan & Kim 2019 텅스텐 응집 배수 → n 역산, 기하평균 ──
n_temp = log(60.0) / log(3.0)            # 입경 3배 → 스크래치 60배 (Fig.7)
n_agit = log(1.0 / 0.15) / log(3.0)      # 입경 1/3 → 스크래치 85% 감소 (Fig.9)
n_geo = sqrt(n_temp * n_agit)
print(f"(B) Egan-Kim n_temp={n_temp:.2f}, n_agit={n_agit:.2f}, 기하평균={n_geo:.2f}  (팩값 2.54)")
assert abs(n_temp - 3.73) < 0.01 and abs(n_agit - 1.73) < 0.01 and abs(n_geo - 2.54) < 0.01

# ── (C) D99 없는 팩: Levitronix/Silco 2008 일반비 × 팩 D50 — 유도 재현 + 일반비 불변성 ──
GEN = 5.00   # Earlier 1.0/0.20 = 5.00, New 0.3/0.07 = 4.29, Next 0.2/0.04 = 5.00 → 중앙값 5.00
derived = {"cu_h2o2_bta": 100.0 * GEN, "oxide_silica": 50.0 * GEN, "w_fe_oxidizer": 50.0 * GEN}
assert derived == {"cu_h2o2_bta": 500.0, "oxide_silica": 250.0, "w_fe_oxidizer": 250.0}, derived
assert 150.0 * GEN == 750.0   # 정정 전 w_fe 값의 출처 — 옛 D50(150)의 잔재였음을 기록
for ratio in (4.29, 5.00):    # what-if를 D50 배수(50→80 nm)로 넣으면 Δ는 일반비 선택에 불변
    assert abs(((80.0 * ratio) / (50.0 * ratio)) ** 1.44 - 1.6 ** 1.44) < 1e-12
print("(C) 유도 D99 재현:", derived, "— what-if를 D50 배수로 넣으면 일반비 4.29/5.00 어느 쪽이든 Δ 불변")

# ── (D) 스크래치 임계 직경 수렴 — 독립 3출처·3화학종 ──
d_c = {"Remsen2006 퓸드실리카 LPC 절편": 680.0, "Kwon2023 세리아": 700.0,
       "Eusner2009 DO2 응집체 2R": 2 * 305.0, "Eusner2009 DO4 응집체 2R": 2 * 381.0}
assert all(600.0 <= v <= 800.0 for v in d_c.values()), d_c
print("(D) 임계/응집체 직경 0.6~0.8 µm 수렴:", d_c)

# ── (E) Eusner 2009 Table IV 상한 재현(6칸) + 팩별 최대 스크래치 치수 ──
H_p = {"mean": 0.05, "max": 0.31}; Hc = {"Cu": 1.22, "low-k A": 2.09, "low-k B": 1.37}   # GPa
tab = {("mean","Cu"):(0.20,0.04), ("max","Cu"):(0.50,0.25), ("mean","low-k A"):(0.15,0.02),
       ("max","low-k A"):(0.39,0.15), ("mean","low-k B"):(0.19,0.04), ("max","low-k B"):(0.48,0.23)}
for (hp, film), (a_r, d_r) in tab.items():
    assert abs(sqrt(H_p[hp]/Hc[film]) - a_r) < 0.011 and abs(H_p[hp]/Hc[film] - d_r) < 0.011, (hp, film)
print("(E) Eusner Table IV 재현: a_c/R=√(H_p/H_c), δ_c/R=H_p/H_c 6칸 소수 둘째 자리 일치")
packs = {"cu_h2o2_bta": (500., 1.2e9), "oxide_silica": (250., 9e9), "sti_ceria": (700., 9e9),
         "sic_ceria_h2o2": (700., 2.6e10), "w_fe_oxidizer": (250., 1.2e10)}
for p, (d, Hf) in packs.items():
    print(f"    {p}: 2a_max={d*sqrt(0.31e9/Hf):.0f} nm, δ_max={(d/2)*0.31e9/Hf:.1f} nm  (압력 무관 상한)")
assert 500 * sqrt(0.31 / 1.2) > 700 * sqrt(0.31 / 9), "Cu는 D99가 작아도 무른 막이라 상한이 세리아/SiO2보다 크다"

# ── (F) 새 지식: 상수 n은 로그정규 꼬리가 임계 d_c를 지나는 구간의 할선(secant)이다 ──
Phi = lambda z: 0.5 * (1 + erf(z / sqrt(2))); phi = lambda z: exp(-z * z / 2) / sqrt(2 * pi)
def n_local(d50, d99, dc=680.0):
    """d ln N(>d_c) / d ln D99 (D50 고정, 로그정규 σ = ln(D99/D50)/2.326)"""
    u = log(d99 / d50); s = u / 2.326; z = log(dc / d50) / s
    return phi(z) / (1 - Phi(z)) * z / u
nl = {d: n_local(d50, d) for d50, d in [(160, 500), (190, 700), (240, 2500)]}   # Hitachi (D50, D99)
print("(F) Hitachi 3점 위치의 국소 지수:", {k: round(v, 2) for k, v in nl.items()})
assert nl[500] > nl[700] > nl[2500], "D99가 d_c를 향해/넘어 갈수록 국소 지수는 단조 감소해야 한다"
lit = [1.44, 1.73, 2.54, 3.73]
assert min(nl.values()) < min(lit) and max(lit) < max(nl.values()), "문헌 n 4개가 국소지수 포락(0.7~8.4) 안에 있어야 한다"
sec = np.polyfit(np.log([500, 700, 2500]),
                 np.log([1 - Phi(log(680 / d50) / (log(d / d50) / 2.326)) for d50, d in [(160,500),(190,700),(240,2500)]]), 1)[0]
print(f"    로그정규-임계 모델의 할선 n={sec:.2f} vs 실측 회귀 1.44 — 형상(감소 방향)은 설명, 절대 지수는 1.8배 과대(미검증)")

# ── (G) Basim & Moudgil 2002 — 평균 입경 불변 응집 손상 ×2 (응집 항의 유일한 정량 근거) ──
assert 50.0 / 25.0 == 2.0 and 720 / 167 > 4
print("(G) NaCl 0.2 M: 평균 입경 0.2 µm 불변, Rmax 25→50 nm(×2), DLVO 장벽 720→167 kT — D99 항과 독립 경로")
```

재현 결과(위 블록 실행, 출처는 §8 — US8439995B2 / doi:10.1149/2.0311905jss / doi:10.1149/1.3121964):
(A) n=1.444, R²=0.997 문헌값 일치 · (B) 2.54 팩값 일치 · (C) 유도값 250/500/250 nm 재현, 750 nm는 옛 D50
잔재 확인 · (D) 임계 610~762 nm 수렴 · (E) Eusner 2009 Table IV 6칸 일치, 팩별 상한 Cu 2a_max 254 nm/
δ_max 65 nm, SiO₂(세리아 700 nm) 130/12 nm, SiO₂(실리카 250 nm) 46/4 nm, SiC 76/4 nm, W 40/3 nm ·
(F) 국소 지수 8.4 → 4.6 → 0.7 · (G) ×2.

## 6. 새로 도출한 지식

1. **damage_exponent n은 재료 상수가 아니라 "D99가 임계 d_c의 어느 쪽에 있는가"의 함수다.** 임계 초과
   개수 N(>d_c)를 로그정규 꼬리로 쓰면 국소 지수는 `n_loc = z·h(z)/ln(D99/D50)`(h = 정규 해저드,
   z = ln(d_c/D50)/σ)이고, Hitachi 3점 위치에서 8.4 → 4.6 → 0.7로 **단조 감소**한다. 문헌의 상수 n
   (1.44~3.73)은 이 곡선의 **할선**이다. 그래서 (a) 세리아 시리즈(D99 500~2500, 임계를 **가로지름**)는 완만한
   1.44가 나오고, (b) 텅스텐 응집 관측(D99가 임계 **아래에서 위로** 3배 점프)은 3.73처럼 가파른 값이 나온다 —
   두 문헌의 "불일치"는 화학종 차이가 아니라 **관측 창의 위치 차이**로 설명된다. 함의: 팩의 n은 그 팩의 D99가
   d_c 대비 어디 있는지와 함께 인용해야 하고(κ의 농도 지수가 "측정 창의 함수"인 것과 같은 구조), D99 what-if를
   임계를 가로질러 크게 흔들 때 상수 n은 임계 아래에서 과소·위에서 과대 예측한다.
   ⚠ 미검증: 로그정규 가정과 σ = ln(D99/D50)/2.326 환산은 형상 설명용이며, 할선 절대값(2.61)은 실측(1.44)보다
   1.8배 크다 — 절대 지수를 이 모델로 **대체하지 않는다**(팩값 유지).
2. **스크래치 치수 상한은 D99와 막 경도만으로 닫힌다(압력 무관).** 같은 D99 700 nm라도 SiO₂ 막(δ_max 12 nm)과
   SiC 막(4 nm)은 3배 차이고, Cu(1.2 GPa)는 D99 500 nm로도 δ_max 65 nm — 5팩 중 가장 깊다. **Δ 배수가 같아도
   손상의 절대 심각도는 막이 정한다** — 이것이 "입자/막 경도비를 배수로 넣지 않고 상한으로 출력"하는 이유이자,
   팩별로 Δ를 비교하면 안 되는 이유(Δ는 팩 내부 what-if 축).
3. **5팩 전부의 D99(250~700 nm)는 임계 680 nm 아래 또는 경계다.** w_fe 750 nm의 "임계 초과"는 옛 D50의
   잔재였다(정정). 임계 근처(세리아 700 nm)가 가장 민감한 위치이며, 그 팩에서 D99 what-if 감도가 가장 크다.
4. **유도값의 정합성 규칙**: `abrasive_d99_nm`을 D50×일반비로 유도한 팩은 `abrasive_size_nm`이 승격될 때
   D99·`_ref` 짝을 함께 재계산해야 한다 — 안 하면 유도값이 유도 입력과 어긋난 채 남는다(이번 w_fe 사례).

## 7. 한계·미검증

- ⚠ **미검증**: cu/oxide/w_fe 3팩 D99는 유도값(estimated) — 알루미나·실리카 자체 D99/D50 실측 없음(5회 탐색 실패).
- ⚠ **미검증**: 응집 계수 2.0은 실리카 학술계 단일점(n=1); 화학종 외삽 미검증. 제타전위·이온강도에서
  `aggregate_ratio`를 유도하는 경로는 팩에 입력값이 없어 열지 않았다.
- ⚠ **미검증**: cu_h2o2_bta n=2.54는 텅스텐→구리 화학종 전이(estimated) — Cu 막 D99–스크래치 대응쌍 미확보.
- ⚠ **미검증**: §6-1 로그정규 꼬리 모델은 형상 설명이며 절대 지수를 재현하지 못한다(1.8배 과대).
- ⚠ **미검증**: H_p,max=0.31 GPa는 IC1000 습윤 1종 패드 36회 측정의 최대값 — 다른 패드로의 이식은 추정.
- ⚠ **미검증**: 임계 d_c=680 nm는 실리카 등가 직경(Remsen)이며 세리아·알루미나에서는 밀도·형상 보정이 필요할 수
  있다 — Kwon 2023(세리아 0.7 µm)이 근접하므로 오더 수준에서만 공통값으로 쓴다.
- **범위 밖**: LPC 개수축(Fujifilm 800,000/wt%), 패드 파편·디스크 그릿 탈락 발생원(scratch-physics 노트 §5, §7)은
  Δ 입력에 없다 — Δ는 슬러리 대입자 발생원만 담는다.

## 8. 출처
- US 8,439,995 B2 (Hitachi Chemical) https://patents.google.com/patent/US8439995B2/en
- Egan & Kim (2019), ECS J. Solid State Sci. Technol. 8(5) P3206, doi:10.1149/2.0311905jss
- Remsen et al. (2006), J. Electrochem. Soc. 153(5) G453, doi:10.1149/1.2184036
- Eusner, Saka, Chun et al. (2009), J. Electrochem. Soc. 156(7) H528, doi:10.1149/1.3121964
- Saka, Eusner, Chun (2008), CIRP Annals 57(1) 341, doi:10.1016/j.cirp.2008.03.098
- Basim & Moudgil (2002), J. Colloid Interface Sci. 256(1) 137, doi:10.1006/jcis.2002.8352
- Bielmann et al. (1999), Electrochem. Solid-State Lett. 2(3) 148, doi:10.1149/1.1390765 (w_fe D50=50 nm)
- Silco Electronic Materials (2008), Levitronix CMP Users Conference slide p.11 (2차 자료, D99/D50 세대비)
- US 6,770,218 B2 (Showa Denko) https://www.freepatentsonline.com/6770218.html (알루미나 최대 입경 상한)
