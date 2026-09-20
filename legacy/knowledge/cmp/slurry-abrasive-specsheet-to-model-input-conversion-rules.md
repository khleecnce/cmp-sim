<!-- V2-SECTION: R2-slurry | Cal-1 2026-09-19 | 근거: 스펙시트 측정법·가중 변환·식별가능성 | 정본: ORG.md §7.3 -->
# Cal-1 — 슬러리 입자 스펙시트(입도·농도·제타) → 모델 입력 변환 규칙 + 공개 데이터 검증 (slurry-abrasive)

> 에이전트: slurry-abrasive Cal-1 (캘리브레이션 단원, ORG.md §7.3) | 작성일: 2026-09-19
> 선행(인용만, 재서술 금지):
> [[abrasive-parameters-to-kp-contribution-quantitative-model]](Lv3-2 — 입자 파라미터→Kp 항별 감사)
> [[abrasive-concentration-mrr-saturation-contact-probability]](Lv2-2 — 농도 포화·US9499721B2 E1)
> [[abrasive-particle-size-distribution-d99-tail]](D99 1차 특허·disc centrifuge Table1)
> [[abrasive-size-concentration-ph-K-additive-mrr-quantitative]](정점모델 Li 2021 Eq.3-4)
> [[../materials/abrasive-psd-large-particle-tail-d99]](SLS 강도가중 vs SMPS 개수 측정법 한계)
> [[../slurry/slurry-storage-transport-history-effective-psd-model]](slurry-colloid 소유 — wt%→vol% F_vol·DLS d⁶ 강도가중)
> [[preston-luo-dornfeld-mrr]](Kp lumped 상수) [[wafer-metrology-customer-data-schema-metric-definition-mapping]](형제 Cal-1 본보기)

## 0. 목적·범위·형제 경계

ORG.md §7.3은 slurry-abrasive에게 **"슬러리 스펙시트(입도·농도·제타) → 모델 입력 변환 규칙 정의 +
공개 데이터로 검증"**을 맡겼다. 이 노트가 그 산출물이다. 앞 단원(Lv2·Lv3)은 **재서술하지 않고 인용만** 한다.

이 단원이 푸는 실제 문제는 wafer-metrology Cal-1([[wafer-metrology-customer-data-schema-metric-definition-mapping]])이
푼 것과 같은 구조다 — **"같은 물리량이라도 소스마다 표기 규약이 달라 숫자가 갈린다."** 거기서는 WIWNU 정의가
갈렸고, 여기서는 **입도의 측정 가중(강도/질량/개수)이 갈린다**: Evonik TDS는 입경을 **Z-average(DLS 강도가중)**로,
Versum 특허는 D99를 **"99 wt.%"(질량가중, disc centrifuge)**로 적는다(§1). 같은 입자라도 이 둘은 다른 숫자다(§3).
가중을 통일하지 않고 팩(`abrasive_size_nm`)에 넣으면 캘리브레이션이 "측정 규약 차이"를 "그 슬러리 고유 편차"로 오학습한다.

**형제 경계 (침범 금지, 인용만):**
- **제형·pH·산화제**는 slurry-chemistry 소관. 제타의 **부호가 pH로 뒤집히는 화학**은 인용만 하고 새 정량 안 만든다.
- **저장·이송 이력·응집 상태량**은 slurry-colloid 소관([[../slurry/slurry-storage-transport-history-effective-psd-model]]).
  wt%→vol% 환산식(`F_vol`)·DLS 강도가중(I∝d⁶)은 그 노트가 이미 **이력 맥락에서** 세웠다 — 여기서는
  **스펙시트→팩 입력 변환**이라는 다른 목적으로 **인용**하고, 재유도하지 않는다.
- **스키마 파일**(`data/schema/*.json`)·`ingest.py`·`prior.py`는 **cmp-data-engineer** 소관
  ([[../data/cmp-measurement-ingest-schema-standardization]]). 이 노트는 **개정 제안(§6)만** 표로 적고 파일을 고치지 않는다.
- **잔차 GP 보정**은 **cmp-calibrator** 소관. 여기서는 "정본 가중으로 통일된 팩 입력 + 잔차를 어느 스펙 축에
  귀속할지의 식별가능성 조건(§5)"까지만 책임진다.
- **고객·재직사 데이터 절대 미사용**(ORG.md §7.5). 이 노트의 모든 수치는 공개 상용 TDS·특허 실시예·논문·합성이다.

## 1. 상용 슬러리 스펙시트가 실제로 적는 항목·단위·측정법 — 1차 조사

상용 CMP 슬러리의 입도·농도·제타가 **공개 문서에 어떻게 적히는지**를 1차 자료로 조사했다. 핵심은
"어떤 값이냐"가 아니라 **"어떤 측정 원리(가중)로 얻은 값이냐"**다 — 이것이 변환 규칙(§2)의 입력이다.

| # | 소스(유형) | 입도 표기 | 측정법·가중 | 농도 | pH | 제타 | 등급 |
|---|---|---|---|---|---|---|---|
| S1 | **Evonik IDISIL TDS**(상용 기술문서, 2025-08) | "Average Particle Size **Z avg in nm**" 50/70/90/125 | **DLS Z-average**(강도가중 큐물란트, 유체역학직경) | "Silica Content **wt.%**" 20 | "pH (20 °C)" ~10.2–10.5 | 없음 | E3 |
| S2 | **US9499721B2**(Cabot, 특허 실시예) | "average particle size **54 nm**"(Example 13) | **미기재** | 15 wt% 농축→0.5~3.0 wt% 희석 | 4.7(농축) | 부호만("cationic") | 입경 E3 / MRR표 E1 |
| S3 | **US20190127607A1**(Versum, 특허 명세) | **D50·D99**, "D99 = particle size that **99 wt.%** of composition" | **disc centrifuge**(preferred; imaging/DLS/HDF도 가능 명시) | — | — | — | E2 |
| S4 | **US10894906B2**(Versum, 실시예 Table1) | D50 152.3 / D75 189.8 / D99 287.5 | **disc centrifuge**(질량가중 침강) | — | — | — | E2 |
| S5 | **Seo 2021**(논문, 재인용 via slurry-colloid §4.1) | d_DLS 75±6 nm | DLS(유체역학직경) | — | pH 8.1 | ζ = −63±2 mV **@pH 8.1** | E1 |
| S6 | Kim 2010 / Yang 2010(재인용 via [[../materials/abrasive-psd-large-particle-tail-d99]]) | SLS(강도) vs SMPS(개수) | 측정법별 가중 편차 | — | — | — | E2/E3 |

**조사 결과 4가지 사실(재서술 아님 — 스펙시트 관점의 새 정리):**
1. **상용 TDS(S1)는 입경을 Z-average(강도가중 DLS)로만 준다.** 분포폭(σ_g)·측정 pH·제타는 비공개.
   Evonik은 형상도 "**Peanut**"(구형 아님)으로 명시 — Z-avg가 구형 등가 유체역학직경임을 뜻한다.
2. **특허(S3·S4)는 disc centrifuge(질량/부피가중)로 D50·D99를 준다.** S3은 D99를 **"99 wt.%"**로 정의해
   가중이 질량 기준임을 못박는다. 즉 **소스마다 가중이 강도(S1)↔질량(S3·S4)로 다르다.**
3. **제타는 상용 TDS·특허 실시예엔 대개 없고**, 논문(S5)만 **측정 pH를 명시**한다(ζ=−63 mV @pH 8.1).
   제타는 IEP 근처에서 부호까지 바뀌므로(팩 `abrasive_iep_ph`=2.5, oxide_silica.yaml) **pH 없는 제타값은 해석 불가**다.
4. **팩 `abrasive_size_nm`(oxide_silica=50 nm)은 측정 가중을 명시하지 않는다**(출처: 총론 노트). 이 공백이
   §4의 검증에서 "우연히 맞지만 규약은 불명"이라는 문제를 만든다.

## 2. 변환 규칙 명세 — 스펙시트 값 → 팩 입력

### R1. 입도: 측정 가중을 정본으로 통일 (Hatch–Choate median 변환)

로그정규 입도분포에서 **개수(number)·면적·부피/질량·강도(intensity)로 가중한 분포는 전부 같은 기하표준편차
$\sigma_g$를 갖는 로그정규이고, median만 이동**한다. 그 이동량이 Hatch–Choate 관계다
(Hatch & Choate 1929, *J. Franklin Inst.* 207, 369, **DOI: 10.1016/s0016-0032(29)91451-4**; 표준 통계 결과라 유도로 재현):

$$D_{\text{median},\,k} = D_g \cdot \exp\!\big(k\,\ln^2\sigma_g\big),\qquad
k=\begin{cases}0 & \text{개수(number)}\\ 2 & \text{면적}\\ 3 & \text{부피/질량(disc centrifuge·레이저회절)}\\ 6 & \text{강도(DLS, Rayleigh 극한 }I\propto D^6)\end{cases}$$

**규칙**: 팩 정본 가중을 하나 정하고(제안: **부피median** — 접촉·질량수지와 정합), 모든 소스를 그리로 환산한다.
- DLS Z-avg(S1)·강도median → 부피median: $\times\exp(-3\ln^2\sigma_g)$
- disc centrifuge 질량median(S3·S4)은 **이미 부피median**(환산 불필요, k=3=3)
- $\sigma_g$는 같은 소스의 **D99/D50** 또는 D90/D10에서 역산: $\ln\sigma_g=\ln(D99/D50)/z_{0.99}$, $z_{0.99}=2.326$.
- ⚠ **$\sigma_g$를 안 주는 소스(대부분의 상용 TDS)는 환산 불가** → 표기값을 그대로 쓰되 `size_basis` 플래그를
  남기고 잔차를 그 축에 못 준다(§5). 지어낸 $\sigma_g$로 환산하면 그게 오염이다.
- ⚠ **한계**: DLS Z-average는 엄밀히는 강도가중 **조화평균**(큐물란트)이지 강도median이 아니다. k=6은
  Rayleigh 극한($D\ll\lambda$)이고 50~150 nm 입자·λ=633 nm에서는 Mie 보정이 필요하다 — k=6 환산은 **상한 근사**다.

### R2. 농도: wt% → vol%(부피분율) — 입자·용액 밀도 필요

팩 농도항은 wt% 기준(`abrasive_wt_pct`)이나, 접촉확률 물리(점유확률
[[abrasive-concentration-mrr-saturation-contact-probability]] §4)의 자연 변수는 **부피분율**이다. 환산식은
slurry-colloid가 이미 세운 `F_vol`([[../slurry/slurry-storage-transport-history-effective-psd-model]] §6, **인용**):

$$\phi_{\text{vol}} = \frac{w/\rho_p}{w/\rho_p + (100-w)/\rho_s}\quad(\rho_p=\text{입자밀도},\ \rho_s\approx\rho_{\text{water}})$$

**규칙**: 팩 `abrasive_density_kg_m3`(oxide_silica=2200, 비정질 실리카)를 필수 입력으로 쓴다. 밀도가 다른
입자끼리(세리아 7216 vs 실리카 2200 kg/m³) wt%를 그대로 비교하면 부피분율이 3배 이상 어긋난다 — vol% 통일 필수.

### R3. 1차입경(BET/TEM) vs 응집체(DLS/disc centrifuge 유체역학·침강 직경)

DLS(S1·S5)·disc centrifuge(S3·S4)는 **유체역학·침강 직경**이라 수화층·약응집을 포함해 1차입경보다 크다.
BET 비표면적·TEM(S3의 core MPS "by TEM")은 **1차입경**이다. 팩 `abrasive_size_nm`이 1차인지 2차(응집체)인지
명시해야 한다 — 정점모델(Li 2021)이 어느 축의 크기를 가정했는지에 따라 입력 축이 갈린다.

## 3. Python 검증 — 변환 규칙 재현·문헌값 대조

### 3.1 Hatch–Choate median 변환 재현 (R1)

**재현 요약**: 로그정규 number 표본(D_g=100, σ_g=1.30)에서 D^k 가중 median이 해석식 $D_g\exp(k\ln^2\sigma_g)$와
1% 이내 일치(k=0/2/3/6)하고, 강도median/부피median = 부피median/개수median = 1.229(σ_g=1.30)임을 assert(1블록).

```python verify
import numpy as np
rng = np.random.default_rng(0)
# 로그정규 number 분포: number median D_g, 기하표준편차 sigma_g
Dg, sg = 100.0, 1.30                       # nm, 전형 콜로이달 실리카 폭
lnsg = np.log(sg); N = 2_000_000
x = np.exp(rng.normal(np.log(Dg), lnsg, N))   # number-weighted 표본

def wmedian(vals, w):
    o = np.argsort(vals); v = vals[o]; cw = np.cumsum(w[o]); cw = cw/cw[-1]
    return v[np.searchsorted(cw, 0.5)]

# Hatch-Choate: D^k 가중 분포의 median = Dg·exp(k·ln²σg)
for k, name in [(0,"number"),(2,"surface"),(3,"volume/mass"),(6,"intensity(Rayleigh)")]:
    mc = wmedian(x, x**k); ana = Dg*np.exp(k*lnsg**2); rel = abs(mc-ana)/ana
    print(f"k={k} {name:<20}: MC {mc:.2f} vs 해석 {ana:.2f} nm (편차 {rel*100:.2f}%)")
    assert rel < 0.01, f"k={k} Hatch-Choate median 불일치 {rel:.3f}"
r_iv = np.exp((6-3)*lnsg**2); r_vn = np.exp(3*lnsg**2)
print(f"강도median/부피median={r_iv:.3f}, 부피median/개수median={r_vn:.3f} (σg={sg})")
assert abs(r_iv-1.229) < 0.01 and abs(r_vn-1.229) < 0.01
print("OK: 가중이 다르면 같은 물리 입자도 median이 달라진다 — Hatch-Choate로만 통일 가능")
```

### 3.2 disc centrifuge 실측(S4)이 로그정규와 정합 → σ_g 유도·부피→개수 환산 (R1)

**재현 요약**: US10894906B2 Table1 "No Treatment"(disc centrifuge) D99/D50=1.887에서 부피가중 σ_g=1.314를
역산하고, **역산에 쓰지 않은 D75**를 로그정규로 예측하면 실측(189.8 nm)과 3.6% 이내로 정합 → 이 σ_g로
disc centrifuge D50(부피median 152.3)을 개수median 121.8 nm(−20%)로 환산함을 assert(1블록).

```python verify
import numpy as np
from scipy.stats import norm
# US10894906B2 (Versum) Table1 "No Treatment" — disc centrifuge(질량/부피 가중), [[abrasive-particle-size-distribution-d99-tail]] §3
D50, D75, D99 = 152.3, 189.8, 287.5        # nm
z99, z75 = norm.ppf(0.99), norm.ppf(0.75)
lnsg = np.log(D99/D50)/z99; sg = np.exp(lnsg)
print(f"disc centrifuge D99/D50={D99/D50:.3f} → 부피가중 σg={sg:.4f}")
assert 1.28 < sg < 1.35, sg
D75_pred = D50*np.exp(z75*lnsg); rel = abs(D75_pred-D75)/D75   # 독립 백분위 교차검증
print(f"D75 예측 {D75_pred:.1f} vs 실측 {D75} nm → 편차 {rel*100:.1f}% (역산에 안 쓴 점)")
assert rel < 0.05, f"로그정규 3점 정합 실패 {rel:.3f}"
Dn = D50*np.exp(-3*lnsg**2)                 # 부피(k=3) → 개수(k=0) median
print(f"disc centrifuge D50(부피) {D50} → 개수median {Dn:.1f} nm ({(Dn/D50-1)*100:+.0f}%)")
assert Dn < D50 and abs(Dn-121.8) < 1.5
print("OK: 특허 실측이 로그정규를 지지 → Hatch-Choate 환산이 실데이터에서 성립")
```

### 3.3 wt% → vol% 환산 (R2) — 입자밀도 필수성

**재현 요약**([[../slurry/slurry-storage-transport-history-effective-psd-model]] §6 F_vol 인용): 30 wt% 실리카(ρ=2.2)→16.30 vol%(문헌 대조)·20 wt%→10.20 vol% 재현, 밀도를 석영(2.65)으로 잘못 쓰면 vol%가 15%+ 어긋나 팩 `abrasive_density_kg_m3` 필수임을 assert(1블록).

```python verify
# wt%→vol% (slurry-colloid F_vol 인용: ../slurry/slurry-storage-transport-history-effective-psd-model §6)
RHO_SIO2, RHO_SOL = 2.20, 1.00             # g/cm^3 (비정질 실리카; 희박 수용액≈물)
def vol_pct(wt, rho_p=RHO_SIO2, rho_s=RHO_SOL):
    return 100.0*(wt/rho_p)/((wt/rho_p)+(100.0-wt)/rho_s)
v30 = vol_pct(30.0)
print(f"30 wt% 실리카(ρ=2.2) → {v30:.2f} vol%")
assert abs(v30-16.30) < 0.1, v30           # 문헌 대조: 30 wt% → ~16.3 vol%
v20a, v20q = vol_pct(20.0, 2.20), vol_pct(20.0, 2.65)
assert abs(v20a-10.20) < 0.1
err = (v20a-v20q)/v20a
print(f"20 wt% → {v20a:.2f} vol%(비정질2.2) vs {v20q:.2f} vol%(석영2.65 오사용) → 편차 {err*100:.0f}%")
assert err > 0.14, "밀도 2.2↔2.65 혼동만으로 vol%가 14%+ 어긋남(팩 abrasive_density 필수)"
print("OK: wt%→vol%는 입자밀도가 필수 입력 — 밀도 미기재 스펙시트는 vol% 환산 불가")
```

## 4. 공개 데이터 검증 (브리프 (c)) — 스펙 표기를 변환 규칙에 통과시켜 팩 값과 대조

팩 `oxide_silica.abrasive_size_nm=50`을 공개 스펙(S1 Evonik KE50 Z-avg 50, S2 US9499721B2 54)과 대조한다.

**재현 요약**: 표기 그대로면 Evonik Z-avg 50≡팩 50(0%)·US9499721B2 54는 +8%지만, 팩이 `size_basis`를
명시하지 않아 §3.2의 실리카 σ_g=1.31로 강도(k=6)→개수/부피 환산 시 Z-avg 50 nm이 부피median 40 nm·개수median
32 nm으로 벌어져 **측정 basis 미명시만으로 최대 35% 잠재 편차**가 정점모델 입력에 실림을 assert(1블록).

```python verify
import numpy as np
pack_size = 50.0                            # oxide_silica.yaml abrasive_size_nm (size_basis 미기재)
evonik = 50.0                               # S1 Evonik IDISIL TDS: "Z avg" 50 nm (강도가중 DLS)
us9499721 = 54.0                            # S2 US9499721B2 Ex.13: "average particle size 54 nm"(측정법 미기재)
# (i) 표기 그대로의 팩 대조
assert abs(evonik-pack_size)/pack_size < 0.01
diff_us = abs(us9499721-pack_size)/pack_size
print(f"표기 그대로: Evonik Z-avg 50 vs 팩 50 = 0%, US9499721B2 54 vs 팩 50 = {diff_us*100:.0f}%")
assert 0.05 < diff_us < 0.10
# (ii) basis 미명시의 대가 — Z-avg(강도 k≈6)를 부피/개수로 환산하면 크게 벌어진다
sg = 1.31; lnsg = np.log(sg)                # §3.2에서 유도한 실리카 부피 σg
d_vol = evonik*np.exp(-3*lnsg**2)           # 강도(6)→부피(3)
d_num = evonik*np.exp(-6*lnsg**2)           # 강도(6)→개수(0)
print(f"Z-avg 50 nm → 부피median {d_vol:.1f} nm, 개수median {d_num:.1f} nm")
worst = (evonik-d_num)/evonik
assert worst > 0.15
print(f"측정 basis 미명시 → 정점모델 입력에 최대 {worst*100:.0f}% 잠재 편차 "
      f"(우연히 팩 50과 맞지만 규약이 불명 — size_basis 필드 부재가 원인)")
```

**판정**: 팩 값 50 nm은 Evonik Z-avg와 **우연히 일치**하나, 팩이 가중을 선언하지 않아 이 일치의 의미가 모호하다.
정점모델(Li 2021, 정점 80 nm)이 어느 가중의 크기를 가정했는지도 원문이 밝히지 않으므로(그래프 축만),
`abrasive_size_nm`에 `size_basis`를 붙이지 않는 한 이 축의 잔차를 신뢰 귀속할 수 없다(§5로 연결).

## 5. 잔차 정의 — 어느 스펙 축에 귀속하나 (식별가능성 조건)

변환 후 예측 MRR과 실측 MRR의 잔차 $r=\text{MRR}_{obs}/\text{MRR}_{pred}$를 입도·농도·제타 중 어디에
귀속할지의 **식별가능성**을 정리한다. Kp는 이 축들의 **곱**이다(`_f_kappa` 3항 곱,
[[abrasive-parameters-to-kp-contribution-quantitative-model]] §1): $K_p = K_{p0}\cdot\kappa_{size}(d)\cdot\kappa_{conc}(C)\cdot\chi_{pH}$.

### 5.1 식별가능성 조건 표

| 스펙 축 | 팩 입력 | Kp 진입 | 단일조건 식별 | 분리(귀속) 조건 | 근거 |
|---|---|---|---|---|---|
| 입도 d50 | `abrasive_size_nm`(+ `size_basis`) | 정점모델 κ (곱) | **불가** (농도와 곱) | 농도·화학 고정, **입경만 스윕**(≥2점) + basis 통일 | §4, [[abrasive-parameters-to-kp-contribution-quantitative-model]] §5 |
| 농도 | `abrasive_wt_pct`(→vol%) | 농도항 κ (곱) | **불가** | 입경·화학 고정, **농도만 스윕**(US9499721B2 22점 E1) | [[abrasive-concentration-mrr-saturation-contact-probability]] §5 |
| 제타/전하 | (팩엔 IEP·pH) | χ (pH항, slurry-chemistry) | **불가** + 측정 pH 미상 시 **귀속 불가** | pH 스윕 + 제타를 **측정 pH와 함께** | §1 S5(Seo pH 8.1) |
| D99 꼬리 | `abrasive_d99_nm` | Δ (진단, MRR 비관여) | MRR 잔차와 **무관** | 스크래치·LPC 데이터로만 | [[abrasive-particle-size-distribution-d99-tail]] |

### 5.2 Python 검증 — 단일조건 분리불가·스윕 필요성

**재현 요약**([[abrasive-parameters-to-kp-contribution-quantitative-model]] §1 곱셈구조): Kp=κ_size·κ_conc 곱 구조에서 잔차 1.20을 입도 단독(d≈57.4 nm) 또는 농도 단독(C≈1.73 wt%)이 각각 완벽히 설명해(둘 다 존재) 단일조건 식별이 불가능하고, 스펙 축 스윕이 있어야 귀속이 성립함을 assert(1블록).

```python verify
# Kp = Kp0·κ_size(d)·κ_conc(C) — 두 스펙축이 곱으로 들어간다 (정점모델·농도 1/3)
def k_size(d, peak=80.0):
    return (d/50.0)**(4.0/3.0) if d <= peak else (peak/50.0)**(4.0/3.0)*(d/peak)**(-1.0/3.0)
def k_conc(C, Cref=1.0): return (C/Cref)**(1.0/3.0)
resid = 1.20                                # 단일조건에서 관측된 MRR 잔차(관측/예측)
d_expl = 50.0*resid**(3.0/4.0)             # κ_size 비=resid 가 되는 d (입도 단독 설명)
C_expl = 1.0*resid**3                       # κ_conc 비=resid 가 되는 C (농도 단독 설명)
assert abs(k_size(d_expl)/k_size(50.0)-resid) < 1e-6
assert abs(k_conc(C_expl)/k_conc(1.0)-resid) < 1e-6
print(f"같은 잔차 {resid}: 입도 단독(d={d_expl:.1f}nm)도, 농도 단독(C={C_expl:.2f}wt%)도 완벽 설명 → 단일조건 식별 불가")
d1, d2 = 50.0, 65.0                          # 농도 고정·입경 2점이면 잔차비가 κ_size비를 따라야 귀속
sep = k_size(d2)/k_size(d1)
assert sep > 1.0
print(f"입경 스윕 50→65nm(농도고정) 잔차비 {sep:.3f} = 입도축 귀속의 검정량 — 스윕이 식별가능성의 전제")
```

**함의(파이프라인 연결)**: 이는 `sim/calibration/prior.py`·`fit_npw.py` 설계와 정합한다 — 잔차 GP는 반경 프로파일의
**계통 편차**만 학습하고 스펙 축에 귀속하지 않는다(그 축을 흔든 데이터가 없으면 귀속이 비식별). 스펙 축 귀속은
**그 축을 스윕한 데이터셋**(validation/datasets의 농도·입경 스윕)이 있을 때만 가능하다.

## 6. `data/schema/` 개정 제안 (cmp-data-engineer 인계 — 파일 직접수정 금지)

현행 `wafer_measurement.schema.json`은 **계측(두께/제거율) 레코드**용이라 슬러리 스펙 필드가 없다. 아래는
**새 슬러리 스펙 필드(또는 별도 `slurry_spec` 객체)** 제안이며 구현은 cmp-data-engineer가 판단한다(§1~§5 근거).

| 필드(제안) | 타입/enum | 필수성 | 근거 | 효과 |
|---|---|---|---|---|
| `abrasive_size_value` + `_unit`(nm) | number | 필수 | §1 S1·S2 | 입경 원값 |
| `abrasive_size_basis` | enum: `intensity_zaverage`/`intensity_median`/`volume_median`/`mass_median`/`number_median`/`primary_bet`/`primary_tem`/`hydrodynamic` | **필수** | §1(Z-avg vs disc centrifuge), §3·§4 | Hatch-Choate 환산의 k 결정 |
| `abrasive_size_method` | enum: `dls`/`laser_diffraction`/`disc_centrifuge`/`spos`/`bet`/`tem` | 권고 | §1 S3 | 측정 원리 추적 |
| `psd_sigma_g` **또는** (`d50`,`d99`) | number | 권고 | §2 R1, §3.2 | σ_g 없으면 환산 불가·플래그(§5) |
| `abrasive_conc_value` + `_unit` | enum: `wt_pct`/`vol_pct`/`g_per_L` | 필수 | §1 S1·S2 | 농도 원값 |
| `abrasive_density_kg_m3` | number | conc가 wt%면 **필수** | §2 R2, §3.3 | wt%→vol% 환산 입력 |
| `zeta_mv` | number\|null | 권고 | §1 S5 | 전하 |
| `zeta_ph` | number | zeta 있으면 **필수** | §1 S5(Seo pH 8.1), §5.1 | 측정 pH 없는 제타는 귀속 불가 |
| `zeta_ionic_strength_mM` | number\|null | 권고 | §1 S5 | 제타의 계 의존 |
| `slurry_ph` | number | 권고 | §1 S1·S2 | χ_pH 축(slurry-chemistry) |

**주의**: 이 제안은 [[wafer-metrology-customer-data-schema-metric-definition-mapping]] §5의 원칙과 같다 —
**측정 규약(가중·pH)을 값과 함께 메타로 저장**해야 캘리브레이션이 규약 차이를 팹 고유 편차로 오학습하지 않는다.

## 7. 근거 충돌 판정 (EVIDENCE-RULES.md 서열)

| # | 충돌 | A (등급) | B (등급) | 판정 |
|---|---|---|---|---|
| 1 | 입경 D50의 "참값" | Evonik Z-avg 50(강도, S1 E3) | disc centrifuge D50(질량/부피, S3·S4 E2) | **레짐(가중) 분할**: 둘 다 맞되 가중이 다르다. 평균 금지 — Hatch-Choate로 정본(부피)에 통일(§2 R1) |
| 2 | k=6 강도 환산 정확도 | Rayleigh I∝d⁶(이론) | CMP 입자 50~150nm는 Mie 영역(D~λ/5) | **상한 근사로만**: k=6은 상한, 실 Mie 보정 미확보 → §2·§4에 미검증 표기 |
| 3 | 팩 size 50과 스펙 일치 | Evonik 50 = 팩 50(0%, S1) | 규약(basis) 불명(§4) | **일치는 우연**으로 판정: size_basis 부재로 신뢰 귀속 불가(§5). 값은 유지, 필드 신설 제안(§6) |

새 충돌 없음 — §1 A/B는 형제(slurry-colloid·측정법 노트)의 기확정을 스펙시트 관점에서 재확인.

## 8. 한계·미확보·미검증 (정직성)

- **k=6 강도가중 환산은 상한 근사**(§2·§7-2). Z-average는 강도가중 **조화평균**(큐물란트)이지 강도median이
  아니고, CMP 입자는 Rayleigh 극한을 벗어난다. 실 Mie 가중의 정확 k는 **미확보**.
- **σ_g는 disc centrifuge 소스(S4)에서만 유도**했다(§3.2). 상용 TDS(S1)는 σ_g를 비공개하므로 그 소스의
  Z-avg→부피 환산은 **불가**다 — §4의 편차 정량은 "S4의 σ_g를 S1에 대입했을 때의 예시"이지 S1의 실측 σ_g가 아니다.
- **팩 `abrasive_size_nm=50`의 측정 가중은 원문(총론)이 밝히지 않았다**(§4 판정). 정점모델(Li 2021)의 크기 축
  가중도 그래프 축만 있어 **미확인**.
- **US9499721B2 54 nm의 측정법은 특허 본문(Example 13)이 명시하지 않았다**(§1 S2). `papers/US9499721B2.txt`가
  현재 저장소에 부재해 Example 13 원문 재판독은 못 했다 — 54 nm은 데이터셋 yaml(§검증됨)과 형제 노트 재인용이며 **측정법 E3**.
- **Seo 2021·Kim 2010·Yang 2010은 slurry-colloid/형제 노트를 통한 재인용**(DOI는 도구로 실존 확인, 원문 재판독 아님).
- **Evonik TDS(S1)는 DOI 없는 상용 기술문서**(`papers/evonik-idisil-cmp-colloidal-silica-datasheet.pdf`) — 제조사
  실측이나 측정조건(σ_g·온도 외)·오차막대 미공개라 E3.
- 제타의 **화학(pH·IEP·부호)**은 slurry-chemistry 소관이라 정량을 새로 만들지 않았다 — 식별가능성 조건(§5)에서
  "측정 pH 필수"만 다뤘다.

## 9. 자기시험
→ [[../../agents/slurry-abrasive/EXAMS.md]] Cal-1 문항 참조.

## 상호링크
[[abrasive-parameters-to-kp-contribution-quantitative-model]] [[abrasive-concentration-mrr-saturation-contact-probability]]
[[abrasive-particle-size-distribution-d99-tail]] [[abrasive-size-concentration-ph-K-additive-mrr-quantitative]]
[[../materials/abrasive-psd-large-particle-tail-d99]] [[../slurry/slurry-storage-transport-history-effective-psd-model]]
[[preston-luo-dornfeld-mrr]] [[wafer-metrology-customer-data-schema-metric-definition-mapping]]
[[../data/cmp-measurement-ingest-schema-standardization]]
