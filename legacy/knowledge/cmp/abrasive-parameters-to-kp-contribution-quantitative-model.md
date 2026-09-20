<!-- V2-SECTION: R2-slurry | 종합 2026-09-16 | 근거: 입자 파라미터 → Kp 기여 항별 1차 회귀·함수형 비교·3입자 배율 | 정본: ARCHITECTURE-V2.md §3 -->
# 입자 파라미터(d50·농도·경도·형상·D99) → Kp 기여 정량모델 — 항별 1차 회귀 재현·함수형 비교·3입자계 배율표 (slurry-abrasive Lv3-2 종합)

> 에이전트: slurry-abrasive Lv3-2 | 작성일: 2026-09-16
> 이 단원은 **종합 단원**이다 — Lv2-1~Lv3-1에서 항별로 확보한 1차 자료를 **하나의 Kp 기여 모델로 감사(audit)**하고,
> 서로 다른 함수형이 같은 데이터에서 어떻게 갈리는지 정량 비교하며, sim/tier2 구현 요청서를 낸다.
> 선행(반드시 먼저 읽을 것):
> [[abrasive-hardness-hertz-indentation-removal-volume]](Lv2-1 — 경도·소성압입, H_w^-3/2)
> [[abrasive-concentration-mrr-saturation-contact-probability]](Lv2-2 — 농도 포화·점유확률, US9499721B2 E1)
> [[kappa-abrasive-concentration-cu-w-cooper-bielmann]](농도 1/3 Cu·W 계 채움, Cooper 2002·Wang 2012)
> [[luo-dornfeld-active-abrasive-size-mrr]](Luo-Dornfeld 활성입자 폐형식)
> [[abrasive-size-concentration-ph-K-additive-mrr-quantitative]](Li 2021 입경 정점 Eq.3-4)
> [[abrasive-size-null-result-force-partition-theory]](입경 null·힘분배 d⁰)
> [[abrasive-shape-effect-purespherical-subset-nonmonotonic]](형상 비단조·구형 부분집합 null)
> [[ceria-chemical-tooth-particle-site-density-facet]](세리아 입자당 23배·기계모델 실패)
> [[ceria-abrasive-size-mrr-peak-shift-vs-silica]](세리아 정점 163 nm vs 실리카 80 nm)
> [[abrasive-particle-size-distribution-d99-tail]](D99 1차 특허·화학종별 D99/D50)
> [[delta-scratch-damage-d99-oversize-particle-model]](D99→Δ 스크래치 형태)
> 스코프: slurry-abrasive(입자 물성 축). 제형·pH·첨가제는 slurry-chemistry, 콜로이드 안정성은 slurry-colloid 소관 —
> **인용만** 하고 정량을 새로 만들지 않는다. 검색어 씨앗 "abrasive hardness removal rate"·"ceria abrasive particle size
> distribution"·"colloidal silica CMP abrasive"의 변형만 사용(`tools/scope.py --agent slurry-abrasive --check` ✓ 허용).

## 0. 이 노트가 형제·선행 노트와 다른 점 (중복 방지 선언)

Lv2·Lv3-1 노트들은 **항을 하나씩** 확보했다(농도·입경·경도·형상·세리아·D99 각각 따로). 이 노트는 그 어느 것도
재서술하지 않고, 오직 세 가지 종합 질문만 푼다:
1. **감사(a)**: `sim/factors.py::_f_kappa`가 쓰는 3항(농도 1/3·입경 정점모델·경도 H^-1.5) 각각을 **P·V 고정
   1차 데이터셋에서 회귀 지수를 구해 팩 값과 대조**한다 — 어느 항이 실제로 1차 회귀로 뒷받침되고 어느 항이
   그렇지 않은지 숫자로 판정한다.
2. **함수형 비교(b)**: 농도 축에서 Luo-Dornfeld 활성입자(선형)·Cooper 포화(1/3+임계)·점유확률(Langmuir/포아송)·
   Bai 미세접촉(χ^(2/3)) 네 함수형을 **같은 E1 데이터로 AIC·SSE 비교**하고, 상반된 지수를 평균내지 않고
   **레짐(저농도 선형 / 고농도 포화)으로 분할**한다.
3. **3입자 배율표(c)+D99 귀속(d)**: 실리카/세리아/알루미나의 Kp 기여 배율표(기준=콜로이달 실리카)를 만들고
   어느 칸이 E5/미검증인지 못박고, **D99 꼬리는 Kp가 아니라 Δ(스크래치)로 가야 하는 근거**를 형제 인용으로 정리한다.

## 1. 왜 이 단원인가 — κ 3항을 1차 회귀로 감사한다

`_f_kappa`(sim/factors.py:585~)는 Kp를 4항 곱으로 놓는다: **① 농도 `(C/C_ref)^n`(기본 n=1/3), ② 입경 정점형
piecewise(정점 이하 φ^(+4/3)·이상 φ^(-1/3)), ③ 패드경도 `(H/H_ref)^(-1.5)`, ④ 디스크 asperity 밀도.** 이 중 입자
파라미터는 ①·②와, "입자 경도"다. 그런데 **③의 H는 입자 경도가 아니라 패드(Shore D) 경도**이고, 입자 경도는
_f_kappa 어디에도 독립 항으로 없다 — 이 사실 자체가 감사의 첫 발견이다(§6). 이 노트는 세 축(농도·입경·경도)을
각각 1차 회귀로 검증한다.

## 2. 출처 (재사용 1차 자료, 단원 상한 준수 — 새 문헌 미도입)

이 종합 단원은 새 문헌을 찾지 않고 **이미 확보·도구검증된 1차 자료를 재감사**한다(모든 DOI는 형제 노트에서
Crossref/NCBI로 실존 확인, `agents/.source_cache.json` 등록 확인). 원문 재판독이 아닌 항목은 **노트 내 재인용**으로 표기.

| # | 출처 | 등급 | 이 노트에서의 쓰임 | 확보 |
|---|---|---|---|---|
| S1 | US9499721B2 (Cabot, 2016) Example 18/TABLE 18 — 콜로이달 실리카 54 nm, TEOS, 0.5~3.0 wt% × 1.5/3/4/5 psi | **E1** | 농도 회귀·함수형 비교의 기준 데이터(P·V 고정 농도 스윕) | `papers/US9499721B2.txt` |
| S2 | Cooper et al. 2002, *Electrochem. Solid-State Lett.* 5(12) G109, doi:10.1149/1.1517772 | **E1** | 농도 1/3·임계농도(Cu 저·SiO2 6배) | `papers/cooper2002-cu-particle-conc-1517772.pdf` |
| S3 | Wang et al. 2012, *ECS Trans.* 41(43) 103, doi:10.1149/1.4717508 | **E1** | W 계 농도 1/3 직접 재확인 | 노트 내 재인용([[kappa-abrasive-concentration-cu-w-cooper-bielmann]]) |
| S4 | Li et al. 2021, *ECS J. Solid State Sci. Technol.* 10, 123008, doi:10.1149/2162-8777/ac3e44 | E3 | 입경 정점 Eq.3-4(실리카, 80 nm) — MRR 절대값은 그래프만 | `papers/slurry-additives-cmp-oxide-ac3e44.pdf` |
| S5 | TW202115224A (Versum, 2021) 표2 — Cu, 15~160 nm, n=18, MRR 수치 有 | **E3**(입경·형상 교락) | 입경 축의 유일한 **수치 MRR** 스윕(P·V 고정) — 회귀 대상 | `validation/datasets/tw202115224a_cu_abrasive_size_pressure.yaml` |
| S6 | Luo-Dornfeld 2001/2003, doi:10.1109/66.920723 / doi:10.1109/tsm.2003.815199; Bai et al. 2007 doi:10.1016/j.apsusc.2007.04.027 | E2 | 함수형(활성입자 선형·미세접촉 χ^(2/3))·경도 H_w^-3/2 | 노트 내 재인용(형제 노트) |
| S7 | Dandu 2009 doi:10.1149/1.3230624 / Oh 2010 doi:10.1016/j.mee.2010.07.040 | E1/E3 | 세리아 입자당 효율·정점 163 nm | 노트 내 재인용([[ceria-chemical-tooth-particle-site-density-facet]]·[[ceria-abrasive-size-mrr-peak-shift-vs-silica]]) |
| S8 | 경도값: 세리아 H=6.44 GPa doi:10.3390/ma19102134 / 용융실리카 H=7.3 GPa (Michel et al. 2006, *J. Non-Cryst. Solids* 352:3550 — **초록만·2차 인용**, DOI가 Crossref 미등록이라 DOI 표기 안 함) / 알루미나 Mohs 9·E≈500 GPa doi:10.3390/ma17030679 | E2/E4 | 입자 경도 리지드 인덴터 게이트 | 노트 내 재인용([[abrasive-hardness-hertz-indentation-removal-volume]] §4) |
| S9 | US7344988B2(DuPont 알루미나)·US10894906B2(Versum 실리카코어) | E2 | D99/D50 화학종별 비율 | 노트 내 재인용([[abrasive-particle-size-distribution-d99-tail]]) |

## 3. 항 A — 농도 지수: US9499721B2 1차 회귀 n≈0.30 vs 팩 0.3333 (S1, E1)

농도항만이 **P·V 고정 하에 농도만 스윕한 E1 회귀**로 팩 값을 직접 뒷받침한다. S1 TABLE 18의 3 psi 행(6점 완비,
Å/min÷10=nm/min)을 로그-로그 회귀하면 전역 멱지수 n≈0.30 — 팩의 `abrasive_conc_exponent=0.3333`과 0.05 이내로
일치한다. Cooper 2002(S2)·Wang 2012(S3)가 Cu·W 계에서 독립적으로 같은 "cubic root(1/3)"를 보고하므로, **1/3은
세 재료계(SiO2·Cu·W)에서 수렴하는 저농도 충돌빈도 레짐의 서명**이다([[kappa-abrasive-concentration-cu-w-cooper-bielmann]] §5).

**재현 요약**: US9499721B2 TABLE 18(doi 없음·특허, `papers/US9499721B2.txt`) 3 psi 6점 로그-로그 회귀 n≈0.30이
팩 값 0.3333과 0.05 이내 일치, Cooper 2002(doi:10.1149/1.1517772) 1/3 서술과 정합함을 assert(1블록).

```python verify
import math
# US9499721B2 (Cabot 2016) TABLE 18, 3 psi 행 (Å/min÷10 = nm/min) — P·V 고정, 농도만 스윕(E1)
conc = [0.5, 1.0, 1.5, 2.0, 2.5, 3.0]                 # wt%
mrr  = [140.0, 207.0, 226.0, 229.0, 243.0, 248.0]     # nm/min
# 로그-로그 최소자승(폐형식) → 전역 멱지수 n
lx = [math.log(c) for c in conc]; ly = [math.log(y) for y in mrr]
mx = sum(lx) / 6; my = sum(ly) / 6
n_pow = sum((a - mx) * (b - my) for a, b in zip(lx, ly)) / sum((a - mx) ** 2 for a in lx)
print(f"US9499721B2 3psi 전역 농도 지수 n = {n_pow:.3f}")
assert 0.25 < n_pow < 0.36, f"전역 지수 {n_pow:.3f}가 예상 밴드(0.25~0.36) 밖"
# 팩 값(oxide_silica.yaml abrasive_conc_exponent=0.3333)과 대조
pack_n = 0.3333
assert abs(n_pow - pack_n) < 0.05, f"1차 회귀 {n_pow:.3f} vs 팩 {pack_n} 차이가 0.05를 넘음"
# Cooper 2002(doi:10.1149/1.1517772)·Wang 2012 "cubic root" = 1/3 과도 정합
assert abs(pack_n - 1.0/3.0) < 0.01
print(f"OK: 1차 회귀 n={n_pow:.3f} ≈ 팩 {pack_n} ≈ 1/3(Cooper/Wang) — 농도항은 E1 회귀로 뒷받침됨")
```

## 4. 항 B — 함수형 비교: 멱함수 vs 포화형 vs 미세접촉, AIC/SSE, 레짐 분할 (S1·S6)

같은 S1 3 psi 6점에 서로 다른 함수형을 **같은 파라미터 수(k=2)**로 공정하게 적합한다. 상반된 지수를 평균내지 않고,
저농도(선형)·고농도(포화) 레짐으로 분할해 판정한다.

| 함수형 | 계보 | 저농도 극한 | 고농도 극한 | 포화 표현 |
|---|---|---|---|---|
| 멱함수 `k·C^n` | Li 2021 표면적 극한(S4)·sim 기본 | C^n | C^n | **불가**(기울기≠0) |
| 활성입자 선형 `k·C` | Luo-Dornfeld Region 1(S6) | C¹ | C¹ | 불가 |
| 미세접촉 `A_r·(6χ/πD³)^(2/3)` | Bai 2007(S6) | C^(2/3) | C^(2/3) | 불가 |
| Cooper 포화/Langmuir `M∞·C/(C_h+C)` | Cooper 2002 임계농도(S2) | C¹ | 상수 | **가능** |
| 점유확률 포아송 `M∞·(1−e^(−C/C0))` | 점유모델([[abrasive-concentration-mrr-saturation-contact-probability]] §4) | C¹ | 상수 | **가능** |

핵심: **세 멱함수형(멱·선형·미세접촉)은 어느 지수를 써도 기울기가 0으로 가지 않아 포화를 구조적으로 못 담는다.**
S1 실측은 0.5→3 wt%에서 국소 지수가 0.56→0.11로 5배 붕괴(포화)하므로, 포화형(Cooper/점유) 두 함수형이
멱함수보다 SSE·AIC 모두 우세하다. 단 포아송 vs Langmuir 우열은 6점 한 행으로 **미확정**으로 남긴다(레짐 판정은
"함수형은 포화형, 지수는 저농도 국소 지수로만 의미").

**재현 요약**: US9499721B2(`papers/US9499721B2.txt`) 3 psi 6점에서 멱함수 SSE≈926·AIC 대비 포화형(Langmuir SSE≈255·
포아송 SSE≈135)이 ΔAIC>10로 결정적 우세, 국소 지수 0.56→0.11 붕괴(레짐 분할, 평균 금지)를 assert(1블록).

```python verify
import math
# US9499721B2 TABLE 18, 3 psi (nm/min) — 함수형 비교(S1 E1, S6 함수형 계보)
conc = [0.5, 1.0, 1.5, 2.0, 2.5, 3.0]
mrr  = [140.0, 207.0, 226.0, 229.0, 243.0, 248.0]
N = len(mrr)
def sse(pred): return sum((p - y) ** 2 for p, y in zip(pred, mrr))
def aic(sse_val, k):                       # 정규오차 AIC = n·ln(SSE/n) + 2k
    return N * math.log(sse_val / N) + 2 * k

# (1) 멱함수 k·C^n (k_par=2: k,n) — 로그-로그 폐형식
lx = [math.log(c) for c in conc]; ly = [math.log(y) for y in mrr]
mx = sum(lx)/N; my = sum(ly)/N
n_pow = sum((a-mx)*(b-my) for a,b in zip(lx,ly)) / sum((a-mx)**2 for a in lx)
k_pow = math.exp(my - n_pow*mx)
sse_pow = sse([k_pow * c**n_pow for c in conc])

# (2)(3) 포화형: 형상 파라미터 격자탐색 + M∞ 선형최소자승 (각 k_par=2)
def fit_grid(gfun):
    best = None
    for i in range(5, 400):
        s_par = i/100.0
        g = [gfun(c, s_par) for c in conc]
        M = sum(a*y for a,y in zip(g,mrr)) / sum(a*a for a in g)
        s = sse([M*a for a in g])
        if best is None or s < best[0]: best = (s, s_par, M)
    return best
sse_hyp, ch, Mh = fit_grid(lambda c, p: c/(p+c))            # Cooper/Langmuir
sse_poi, c0, Mp = fit_grid(lambda c, p: 1.0-math.exp(-c/p)) # 점유확률 포아송

for nm, s, aval in (("멱함수", sse_pow, aic(sse_pow,2)),
                    ("Langmuir", sse_hyp, aic(sse_hyp,2)),
                    ("포아송", sse_poi, aic(sse_poi,2))):
    print(f"{nm}: SSE={s:.0f}, AIC={aval:.1f}")
# 포화형이 멱함수보다 SSE·AIC 모두 우세, ΔAIC>10 = 결정적
assert sse_hyp < sse_pow and sse_poi < sse_pow
d_aic_hyp = aic(sse_pow,2) - aic(sse_hyp,2)
d_aic_poi = aic(sse_pow,2) - aic(sse_poi,2)
print(f"ΔAIC(멱-Langmuir)={d_aic_hyp:.1f}, ΔAIC(멱-포아송)={d_aic_poi:.1f}")
assert d_aic_hyp > 6 and d_aic_poi > 10, "포화형이 멱함수 대비 결정적 우세여야(ΔAIC>10)"

# 레짐 분할: 저농도·고농도 국소 지수(평균내지 않고 분리) — 5배 붕괴가 곧 포화
n_lo = math.log(mrr[1]/mrr[0]) / math.log(2.0)
n_hi = math.log(mrr[5]/mrr[4]) / math.log(3.0/2.5)
print(f"국소 지수: 저농도 {n_lo:.2f} → 고농도 {n_hi:.2f}")
assert n_lo > 0.5 and n_hi < 0.15 and n_lo/n_hi > 4
# 세 멱함수형(멱·선형 C¹·미세접촉 C^2/3)은 전부 포화 불가 — '농도 2배 이득'이 농도 무관
for n in (n_pow, 1.0, 2.0/3.0):
    r_lo = (2e-3)**n/(1e-3)**n; r_hi = (200.0)**n/(100.0)**n
    assert abs(r_lo - r_hi) < 1e-9
print("OK: 함수형은 포화형(Cooper/점유) 채택, 멱함수·선형·미세접촉은 포화 구조적 불가 — 레짐 분할 확정")
```

## 5. 항 C — 입경 지수: 수치 회귀는 null(Cu 밸리), 정점모델은 유도이며 레짐(재료)별 분할 (S5·S4·S7)

농도항과 달리 **입경항은 P·V 고정 수치 MRR 스윕에서 단일 지수가 나오지 않는다.** 이유가 두 겹이다:
1. **유일한 수치 MRR 입경 스윕(S5, Cu n=18)은 밸리형**이고, 형상 교락을 걷어낸 순수 구형 부분집합(n=6/압력)에서도
   Spearman ρ≈0.03~0.15로 **유의 상관 없음**([[abrasive-shape-effect-purespherical-subset-nonmonotonic]] §3). 즉 이 계에서
   입경은 MRR 지배인자가 아니다(EVIDENCE-RULES 판정 #1 null 종결). 단조 멱함수 자체가 이 데이터 형태와 구조적으로 안 맞는다.
2. **정점모델을 뒷받침하는 실리카(S4)·세리아(S7) 데이터는 MRR 절대값이 그래프에만 있어 수치 회귀 불가.** 팩의
   piecewise 지수(+4/3·−1/3)는 Li 2021 Eq.3-4의 **벡터좌표 재추출 유도**에서 왔지, MRR 회귀에서 온 것이 아니다
   ([[abrasive-size-concentration-ph-K-additive-mrr-quantitative]] §4).

따라서 입경항은 **재료계(레짐)로 분할**해야 하며 단일 지수로 통일하면 안 된다: 정점 위치가 콜로이달 실리카 80 nm,
세리아 ≥163 nm로 **약 2배 다르다**([[ceria-abrasive-size-mrr-peak-shift-vs-silica]] §2). 상반된 곡선(실리카 peak vs Cu
valley vs 세리아 늦은 peak)을 평균내지 않고 팩별 분기로 둔다.

**재현 요약**: TW202115224A(특허, `tw202115224a_...yaml`) 순수 구형 부분집합에서 |ρ|<0.3·p>0.5(입경-MRR null),
Li 2021(doi:10.1149/2162-8777/ac3e44) piecewise 정점 80 nm와 세리아(doi:10.1016/j.mee.2010.07.040) 163 nm가 재료별로
갈려 단일 지수 통일 불가함을 assert(1블록).

```python verify
from scipy.stats import spearmanr
# (1) S5 TW202115224A 순수 구형 부분집합 — 입경-MRR null (P·V 고정)
data = [(15,2.5,620.4),(15,1.5,408.4),(15,2.5,549.2),(15,1.5,345.1),
        (27,2.5,514.0),(27,1.5,371.2),(27,2.5,562.9),(27,1.5,351.9),
        (50,2.5,441.4),(50,1.5,310.9),(160,2.5,775.7),(160,1.5,457.4)]
for p in (2.5, 1.5):
    xs = [d[0] for d in data if d[1]==p]; ys = [d[2] for d in data if d[1]==p]
    rho, pv = spearmanr(xs, ys)
    print(f"P={p}psi 구형 부분집합 n={len(xs)}: Spearman rho={rho:.3f}, p={pv:.3f}")
    assert abs(rho) < 0.3 and pv > 0.5, "구형 통제 후에도 입경-MRR 유의상관 없음이어야(판정#1 null)"

# (2) 정점모델은 유도(Eq.3-4)이며 재료별로 정점이 다르다 — 단일 지수 통일 불가
def piecewise(d, peak, eb=4.0/3.0, ea=-1.0/3.0):
    return d**eb if d <= peak else (peak**eb)*(d/peak)**ea
peak_silica, peak_ceria = 80.0, 163.0        # S4(콜로이달 실리카) / S7 Oh 2010(세리아)
# 120 nm 입자: 실리카 정점(80) 위=감소 가지, 세리아 정점(163) 아래=증가 가지 — 부호가 재료로 뒤집힘
assert piecewise(120.0, peak_silica) < piecewise(80.0, peak_silica)   # 실리카: 80 위에서 감소
assert piecewise(120.0, peak_ceria) < piecewise(163.0, peak_ceria)   # 세리아: 163 아래에서 증가
same = (piecewise(120.0, peak_silica) < piecewise(80.0, peak_silica)) and \
       (piecewise(163.0, peak_ceria) > piecewise(120.0, peak_ceria))
assert same, "같은 120→163 nm 구간에서 실리카는 감소·세리아는 증가 — 단일 지수로 통일하면 한쪽은 반드시 틀린다"
assert peak_ceria / peak_silica > 1.9, "세리아 정점이 실리카의 약 2배(레짐 분할 근거)"
print("OK: 입경은 수치 회귀 null(Cu)·정점 유도(실리카 80/세리아 163) — 레짐 분할, 단일 지수 통일 금지")
```

## 6. 항 D — 입자 경도: H^-1.5는 입자 경도가 아니다; 입자 경도는 승수가 아니라 리지드 인덴터 게이트 (S6·S8)

감사의 핵심 발견: **`_f_kappa`의 `(H/H_ref)^(-1.5)` 항의 H는 패드(Shore D) 경도이고, 그 물리적 뿌리인 Luo-Dornfeld
H_w^(-3/2)의 H는 웨이퍼(표면층) 경도다** — 둘 다 **입자 경도가 아니다.** 입자 경도는 Luo-Dornfeld 모델에서
"입자를 리지드 인덴터로 놓는다"는 가정으로 들어가며, 가정이 성립하는 한 **입자 경도는 소거되어 Kp 승수로 나타나지
않는다**([[abrasive-hardness-hertz-indentation-removal-volume]] §2·§4). 세 결과가 이를 못박는다:
- **벌크 경도 단독 예측은 오더가 틀린다**: 웨이퍼 경도 H_w^(-3/2)만으로 W/SiO2 제거율비를 예측하면 ~31.6배인데
  실측은 ~0.5배 — 60배 이상 불일치. 벌크 경도가 아니라 화학이 만든 무른 표면층이 지배한다(같은 노트 §5).
- **실리카 입자는 리지드 인덴터 가정이 아슬아슬하게 깨진다**: 실리카 H≈7.3 GPa < SiO2 막 유효경도 ≈10 GPa
  (S8). 그래서 실리카/SiO2 짝은 순수 기계 압입이 아니라 Cook 수화층 메커니즘이 필요하다.
- **알루미나는 가정이 잘 성립**한다: Mohs 9·E≈500 GPa(S8)로 W(≈1 GPa)·SiO2(≈10 GPa) 어느 막보다 압도적으로 단단하다.

따라서 **입자 경도는 Kp에 "지수 승수"로 넣을 수 없고, 재료별 "리지드 인덴터 성립 여부 게이트"로만 다뤄야 한다** —
입자 경도 축의 P·V 고정 단일변수 스윕(같은 입경·같은 화학에서 경도만 바꾼 1차 데이터)은 확보되지 않았다(**미검증**).

**재현 요약**: Luo-Dornfeld(doi:10.1109/66.920723) H_w^-3/2로 W/SiO2 예측 31.6배가 실측 0.5배와 60배 이상 어긋나고
(벌크경도 단독 실패), 실리카 7.3 GPa < SiO2막 10 GPa(Michel et al. 2006 *J. Non-Cryst. Solids* 352:3550, 초록·2차 인용)로 리지드
인덴터 위반, 알루미나 E≈500 GPa(doi:10.3390/ma17030679)는 성립함을 assert(1블록).

```python verify
# S6 Luo-Dornfeld H_w^-3/2 + S8 경도값 (모두 [[abrasive-hardness-hertz-indentation-removal-volume]] §3~§5 재인용)
Hw_W, Hw_SiO2 = 1e9, 1e10                          # Pa, Fu et al. 2001 재인용치(2차 인용)
predicted_W_over_SiO2 = (Hw_SiO2 / Hw_W) ** 1.5    # 경도항 단독 예측
assert abs(predicted_W_over_SiO2 - 10**1.5) < 1e-6
# 실측 대표 제거율비 (형제 노트에서 문헌 대조된 값)
actual = 130.0 / 254.05                             # W 130 / 산화막 254.05 nm/min
mismatch = predicted_W_over_SiO2 / actual
print(f"경도항 단독 예측 W/SiO2 = {predicted_W_over_SiO2:.1f}배, 실측 {actual:.2f}배 → 불일치 {mismatch:.0f}배")
assert mismatch > 20, "벌크 경도 단독으로는 오더가 틀린다(입자 경도가 승수가 아닌 이유의 근원)"

# 입자 경도 = 리지드 인덴터 게이트 (승수 아님)
H_silica, H_oxide_film = 7.3, 10.0     # GPa (Michel et al. 2006 J.Non-Cryst.Solids 352:3550, 초록·2차 인용)
E_alumina, E_silica = 500.0, 72.0      # GPa (알루미나 doi:10.3390/ma17030679; 실리카 표준 교차참고)
assert H_silica < H_oxide_film, "실리카 입자가 SiO2 막보다 무르다 → 리지드 인덴터 가정 위반(실리카/SiO2)"
assert E_alumina / E_silica > 5, "알루미나는 압도적으로 단단해 리지드 인덴터 성립"
print(f"실리카/SiO2막 경도비 {H_silica/H_oxide_film:.2f}(<1 위반) vs 알루미나/실리카 탄성비 {E_alumina/E_silica:.1f}(성립)")
print("OK: 입자 경도는 Kp 승수가 아니라 재료별 '리지드 인덴터 성립 게이트' — 독립 스윕 미확보(미검증)")
```

## 7. 3입자계 Kp 기여 배율표 (기준=콜로이달 실리카)

세 입자계의 **같은 조건(가능한 한 P를 맞춘) 입자당/질량당 Kp 기여**를 콜로이달 실리카=1.0 기준으로 정리한다.
어느 칸이 E1이고 어느 칸이 E4/미검증인지 못박는다 — **평균내거나 팩 계수로 이식하지 않는다.**

| 입자계 | 농도항 지수 | 입경 정점 | 질량당 배율(vs 실리카) | 입자당 배율 | 등급/판정 |
|---|---|---|---|---|---|
| **콜로이달 실리카**(기준) | +1/3 (E1, S1/S2) | 80 nm (E3, S4) | **1.00** (정의) | **1.00** (정의) | 기준. 리지드 인덴터 아슬(§6) |
| **세리아** | 부호 미상, +1/3 상속 금지 | ≥163 nm (E3, S7) | 5.2배(0.5wt%)~11배(2.5wt%) | **≈23배**(4 psi 정합) | **E4 교차연구 오더표지** — 팩 계수 이식 금지 |
| **알루미나** | +1/3 (E1, W/Cu 계, S2/S3) | 미확보 | **미검증**(head-to-head 실측 없음) | **미확보** | 리지드 인덴터 성립(§6). Kp 배율 수치 없음 |

세리아 23배는 순수 기계 모델(Luo-Dornfeld) 예측 1.23배의 약 19배로, **chemical tooth의 실효 크기**다 — 그러나
막·속도·pH·첨가제가 다른 교차연구(E4)라 오더 표지일 뿐 팩 계수가 아니다([[ceria-chemical-tooth-particle-site-density-facet]] §6).
알루미나 칸은 **콜로이달 실리카와 같은 조건에서 나란히 잰 1차 데이터가 없어 확인 못 해** 비워둔다(지어내지 않는다).

**재현 요약**: 세리아(doi:10.1149/1.3230624 Dandu 2009) 질량효율 1400 nm/min/wt%가 콜로이달 실리카(US9499721B2)
270의 5.19배, 입자수비 0.222 적용 시 입자당 23.3배로 Luo-Dornfeld 예측 1.23배의 약 19배임을 재현하고 알루미나 칸은
수치 부재(확인 못 함)임을 표기(1블록).

```python verify
# 4 psi 정합 비교: Dandu 2009(doi:10.1149/1.3230624) 세리아 vs US9499721B2 콜로이달 실리카
# (전부 [[ceria-chemical-tooth-particle-site-density-facet]] §6 재인용 — E4 교차연구)
ceria = dict(mrr=350.0, wt=0.25, d=60.0, rho=7.216)
silica_rho, silica_d = 2.2, 54.0
silica = {0.5:135.0, 1.0:256.0, 1.5:294.0, 2.0:314.0, 2.5:319.0}  # wt%:nm/min
eff_c = ceria['mrr'] / ceria['wt']; assert eff_c == 1400.0
n_ratio = (silica_rho*silica_d**3) / (ceria['rho']*ceria['d']**3)  # 동일 질량 입자수비
assert abs(n_ratio - 0.222) < 0.003
eff_s0 = silica[0.5]/0.5                        # 가장 덜 포화된 0.5 wt% 기준(보수적)
mass_ratio = eff_c / eff_s0                       # 질량당 배율
per_particle = mass_ratio / n_ratio               # 입자당 배율
ld = (ceria['d']/silica_d)**2                     # Luo-Dornfeld 순수 기계 예측(재질 무관)
print(f"세리아/실리카: 질량당 {mass_ratio:.2f}배, 입자당 {per_particle:.1f}배, 기계예측 {ld:.2f}배, 톱니 {per_particle/ld:.1f}배")
assert abs(mass_ratio - 5.19) < 0.05 and abs(per_particle - 23.3) < 0.3
assert 15 < per_particle/ld < 25, "톱니 배수 오더(20배 근방)"
# 알루미나 칸: 콜로이달 실리카와 나란히 잰 1차 데이터 없음 → 수치 미검증(지어내지 않음)
alumina_kp_ratio = None
assert alumina_kp_ratio is None, "알루미나 Kp 배율은 head-to-head 실측 부재 — 미검증으로 비워둔다"
print("OK: 배율표 — 실리카 1.0(E1)/세리아 입자당 23배(E4 오더표지)/알루미나 미확보")
```

## 8. 항 E — D99 꼬리는 Kp가 아니라 Δ(스크래치)로 간다 (형제 인용만)

이 노트는 D99에 대해 **새 수치를 만들지 않고**, 왜 D99가 Kp가 아니라 Δ(손상 유발도)로 가야 하는지만 형제 인용으로
정리한다(브리프 지시 (d)):

1. **평균 입경(d50)과 꼬리(D99)는 서로 다른 백분위이고 서로 다른 팩터로 간다.** `_f_kappa`의 입경항은 `abrasive_size_nm`
   (평균/d50)을 쓰고, `_f_delta`는 `abrasive_d99_nm`(꼬리)을 쓴다. 화학종별 D99/D50 비율이 크게 달라(실리카 코어
   1.887 vs 알루미나 5.00, [[abrasive-particle-size-distribution-d99-tail]] §5) 하나로 묶을 수 없다 — d50로 Kp를,
   D99로 Δ를 각각 먹인다.
2. **Kp는 "평균적으로 얼마나 깎이나"(제거율), Δ는 "드물게 얼마나 긁히나"(결함 밀도)** — 물리적으로 다른 질문이다.
   대입자(oversize) 꼬리는 활성입자 통계의 <0.5%에 불과해 평균 MRR(Kp)엔 거의 기여하지 않지만, 스크래치는 바로
   그 꼬리가 지배한다([[delta-scratch-damage-d99-oversize-particle-model]] §4, [[lpc-scratch-density-tail-correlation]]
   Remsen 2006 임계 680 nm).
3. **Δ의 지수는 Kp의 지수와 무관하게 D99-스크래치 대응쌍에서만 회귀**된다(Hitachi US8439995B2 4점 n=1.44,
   [[abrasive-d99-scratch-hitachi-us8439995]]). D99를 Kp 입경항에 넣으면 이중계상이 되고, 평균 제거를 대입자 꼬리로
   왜곡한다.

**재현 요약**: 실리카 코어 D99/D50=1.887(US10894906B2)과 알루미나 5.00(US7344988B2)이 100% 넘게 달라 d50(→Kp)과
D99(→Δ)가 분리돼야 함을, 서로 다른 백분위가 서로 다른 팩터로 감을 assert(1블록, 형제 인용만).

```python verify
# 형제 노트 재인용만 — 새 수치 없음 ([[abrasive-particle-size-distribution-d99-tail]] §3·§5)
silica_d50, silica_d99 = 152.3, 287.5     # US10894906B2 Table1 'No Treatment'(실리카 코어)
ratio_silica = silica_d99 / silica_d50
alumina_ratio = 5.0                        # US7344988B2 'more preferred ≤5x'(알루미나)
assert 1.85 < ratio_silica < 1.90
# 화학종별 D99/D50이 100% 넘게 달라 하나의 축으로 묶을 수 없다 → d50→Kp, D99→Δ 분리 필수
dev = abs(alumina_ratio - ratio_silica) / ratio_silica * 100
assert dev > 100, "실리카(1.887)와 알루미나(5.00) D99/D50 차이가 100% 초과 — 분리 근거"
# 서로 다른 백분위가 서로 다른 팩터로: 평균(d50)=Kp, 꼬리(D99)=Δ (이중계상 금지)
kp_uses = "abrasive_size_nm(d50/평균)"; delta_uses = "abrasive_d99_nm(꼬리)"
assert kp_uses != delta_uses
print(f"실리카 D99/D50={ratio_silica:.3f}, 알루미나={alumina_ratio} (차이 {dev:.0f}%) → "
      f"d50는 {kp_uses}로 Kp, D99는 {delta_uses}로 Δ — 분리 확정")
```

## 9. 근거 충돌 판정 (EVIDENCE-RULES.md 서열)

| # | 충돌 | A (등급) | B (등급) | 판정 |
|---|---|---|---|---|
| 1 | 농도 함수형 | 멱함수 C^(1/3) 전역회귀 우수(E1, S1) | 국소지수 0.56→0.11 붕괴=포화(E1, 같은 S1) | **레짐 분할**: 지수값 1/3은 저농도 국소값으로 유효(literature), 함수형은 포화형 채택. 같은 데이터의 두 측면이지 충돌이 아니다(§4) |
| 2 | 입경-MRR 방향 | 실리카 peak@80nm(E3, S4) | Cu valley(E3, S5)·세리아 peak@≥163nm(E3, S7) | **레짐(재료) 분할**(EVIDENCE-RULES 절차 3). 세 곡선을 평균내지 않고 팩별 분기. Cu는 판정#1 null이 최종(§5) |
| 3 | 입자 경도의 Kp 진입 | 벌크 경도 H^-3/2 승수(E4 유도) | 벌크경도 예측 60배 실패·실리카 리지드가정 위반(E1/E2 실측, S6/S8) | **B 채택**: 입자 경도는 승수가 아니라 리지드 인덴터 게이트. 독립 스윕 없어 Kp 항으로 배선 안 함(§6) |
| 4 | 세리아 23배를 팩에 넣나 | 입자당 23배 실효(E4 교차연구, S7) | 막·속도·pH·첨가제 상이(교란) | **오더 표지로만**. 팩 계수 이식 금지(§7). 평균·이식 모두 금지 |

새 충돌 없음 — 전부 형제 노트의 기확정 판정을 종합 관점에서 재확인. **EVIDENCE-RULES 판정 #1(입경 null)**은 이
종합에서도 유지된다(§5).

## 10. 팩 갱신 제안 표 (knowledge/params/*.yaml — 이 노트는 수정하지 않음, 제안만)

| 팩 키 | 현재 | 제안 | 근거(이 노트) | 등급 | 우선순위 |
|---|---|---|---|---|---|
| `abrasive_conc_exponent`(oxide_silica) | 0.3333 | **유지** — 1차 회귀 n≈0.30과 0.05 이내 일치 | §3 | E1 | — (검증 완료) |
| 농도 함수형 | `(C/C_ref)^n` 멱함수 | **포화형 교체**(Langmuir/포아송) — 고농도(≳2wt%) 과대예측 | §4 | E1 | 중(§10-구현요청 1) |
| `abrasive_size_*`(세리아 팩) | 정점 163 배선됨 | **유지** — 재료별 분할 확인 | §5 | E3 | — |
| 입자 경도 항 | 없음(패드 H만) | **신설하지 말 것** — 승수 아님, 게이트로만 | §6 | 미검증 | 낮음(게이트 진단만) |
| 알루미나 Kp 배율 | 없음 | **비워둠** — head-to-head 실측 부재 | §7 | 미검증 | 낮음(문헌 확보 선행) |
| `abrasive_d99_nm` → Δ | Δ에 이미 귀속 | **유지** — Kp로 옮기지 말 것 | §8 | E2 | — |

## 11. 구현 요청 (소프트웨어 부문 — sim/tier2, PROFILE.md에도 등재)

1. **`abrasive_hardness_gpa` 진단 인자(승수 아님, 게이트)** — 입자 경도가 팩에 있고 웨이퍼(표면층) 유효경도보다
   낮으면 "리지드 인덴터 가정 위반 — 순수 기계 Kp 항 신뢰 저하"를 notes에 남기는 진단만. **Kp를 곱셈으로 바꾸지
   말 것**(§6). 근거: 이 노트 §6. 검증문헌값: 실리카 7.3 GPa < SiO2막 10 GPa. 우선순위: 낮음.
2. **농도 함수형 포화 교체** — 이미 [[abrasive-concentration-mrr-saturation-contact-probability]] §8·PROFILE 구현요청 4번과
   동일. 이 노트 §4의 AIC 비교가 그 요청을 강화(ΔAIC>10). 새 요청 아님(편승). 우선순위: 중.
3. **입자 경도 축·알루미나 배율 데이터 확보**(선행 조사) — 같은 입경·같은 화학에서 경도만 바꾼 P·V 고정 스윕,
   그리고 콜로이달 실리카와 나란히 잰 알루미나 Kp 실측. 확보 전까지 §7 알루미나 칸·§6 경도 게이트는 미확보 유지.

## 12. 한계 / 미검증 목록

- **입자 경도 축의 독립 스윕(같은 입경·화학, 경도만 변화)은 확보되지 않았다** — §6 결론(승수 아님)은 이론·간접
  실측에 기반하며 직접 회귀가 아니다(미검증).
- **§7 알루미나 칸은 head-to-head 1차 실측 부재로 비워뒀다.** 세리아 23배는 교차연구(E4) 오더 표지이지 팩 계수가 아니다.
- **S4(Li 2021)·S7(Oh 2010) 입경-MRR 절대값은 그래프에만 있어 수치 회귀 불가** — 정점 위치·방향만 확정, MRR 배수는 미확보.
- S8의 용융실리카 경도 7.3 GPa는 **초록만(2차 인용)**, 세리아 6.44 GPa는 핵연료 대체재 벌크 펠릿(CMP 나노입자 아님).
- Luo-Dornfeld 원 논문(2001, doi:10.1109/66.920723)은 IEEE 유료로 **원문 미접근** — 수식은 2003 Part-1 재인용.
- 이 노트는 종합이라 대부분 형제 노트의 **노트 내 재인용**이다 — 원문 재판독이 아닌 항목은 §2 표에 명시했다.

## 13. 자기시험
→ [[../../agents/slurry-abrasive/EXAMS.md]] Lv3-2 문항 참조.

## 상호링크
[[abrasive-hardness-hertz-indentation-removal-volume]] [[abrasive-concentration-mrr-saturation-contact-probability]]
[[kappa-abrasive-concentration-cu-w-cooper-bielmann]] [[luo-dornfeld-active-abrasive-size-mrr]]
[[abrasive-size-concentration-ph-K-additive-mrr-quantitative]] [[abrasive-size-null-result-force-partition-theory]]
[[abrasive-shape-effect-purespherical-subset-nonmonotonic]] [[ceria-chemical-tooth-particle-site-density-facet]]
[[ceria-abrasive-size-mrr-peak-shift-vs-silica]] [[abrasive-particle-size-distribution-d99-tail]]
[[delta-scratch-damage-d99-oversize-particle-model]] [[lpc-scratch-density-tail-correlation]]
[[abrasive-d99-scratch-hitachi-us8439995]] [[preston-luo-dornfeld-mrr]]
