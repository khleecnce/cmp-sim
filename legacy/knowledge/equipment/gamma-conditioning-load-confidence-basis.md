<!-- V2-SECTION: R4-disk | 공동: R1-equipment | 작성 2026-09-14 | 근거: gamma, conditioner, critical load, Rs, pcr-decay | 정본: ARCHITECTURE-V2.md §3 -->
# Γ(컨디셔닝 부하) confidence 하한 3사유 판정 — Rs 보정 폐형식 상계·τ 앵커 항등성·임계하중 제1원리

> `sim/factors.py::_f_gamma()`는 confidence를 `estimated`로 하한하고 그 사유를 3개 적어 두었다
> ([[disk-rpm-load-radius-pcr]] §6). 이 노트는 그 셋을 **하나씩** 판정한다. 목표는 "해소"가 아니라
> 판정이다 — 근거 없는 승격은 오염이다. 결과: (1) 해소, (2) 조건부 하한으로 전환, (3) **스코프 축소
> 영구 종결(3회차, §4.7)** — R·Y 직접값은 이 코퍼스로 못 낸다. 따라서 기준조건 등급은 그대로
> `estimated`다(칸 수 불변, 확정값이며 하한이 아니다).
> 관련: [[conditioner-disk-pad-cutting-model]] [[conditioner-grit-density-protrusion-cutrate]]
> [[cvd-diamond-disk-patterned-grit-array]] [[../cmp/scratch-physics-source-signatures]]
> [[../materials/hertz-gw-contact-mechanics]] [[conditioning-mechanism-asperity-regeneration]]

## 1. 출처

**직접 인용(원문 확보)**
1. Zheng, Zhao & Lu (2023), *Micromachines* 14(9) 1683, DOI: 10.3390/mi14091683 (PMC10536193, CC-BY).
   Table 1 실험조건: 패드 100 RPM·디스크 73 RPM·하중 4 lbf·디스크 유효직경 104.5 mm·평균 다이아몬드
   피치 430 µm·폭 150 µm·돌출 250 µm·스윕 반경 83~308 mm. `papers/PMC10536193.txt`.
2. McAllister et al. (2019), *Micromachines* 10(4) 258, DOI: 10.3390/mi10040258 (PMC6523751, CC-BY).
   본문: "the platen and conditioning disc rotated counter-clockwise at 87 and 60 RPM" — **같은 방향** 회전,
   Rs=0.69. 코퍼스 `data/corpus/fulltext/doi_10.3390_mi10040258.xml`.
3. Kwon et al. (2013), *Tribology International* 67, 272–277, DOI: 10.1016/j.triboint.2013.08.008.
   플래튼 73 rpm·컨디셔너 93 rpm(Rs=1.27), 그릿 밀도 40,000개·피치 410 µm(Table 1).
   `papers/kwon2013-scratch-formation-diamond-conditioners.pdf`.
4. Tsai et al. (2014), *Math. Probl. Eng.* 2014, 913812, DOI: 10.1155/2014/913812 (CC-BY). 실험실 장비:
   컨디셔너 10 rpm·패드 40 rpm(Rs=0.25, 회전 방향 미기재), ∅108 mm 디스크, CDD 그릿 25,000개,
   "less than 10% of diamond grits are engaged". `papers/tsai2014-mpe-radial-cluster-arranged-diamond-disk.pdf`.
5. Saka, Eusner & Chun (2008), *CIRP Annals* 57(1) 341–344, DOI: 10.1016/j.cirp.2008.03.098.
   식(1)–(3) Hertz+Tresca 항복개시(a_Y, δ_Y, P_Y=(π³/48)H³R²/E²), 본문 IC1000 물성 **E_p=0.5 GPa,
   H_p=0.05 GPa**(습식 Berkovich, 국소값 0.01~0.31 GPa 산포, Fig.9). `papers/saka2008-cirp-nanoscale-scratching.pdf`.
6. Pysher, Goers & Zabasajja (3M, 2010), MRS Proc. 1249-E02-04, DOI: 10.1557/proc-1249-e02-04.
   사후 검사로 작동 다이아몬드의 DOP≈15 µm 추정. `papers/3m_diamond_conditioner_design.pdf`.
7. 특허(코퍼스 전문): US8657652B2(Saint-Gobain, 종래 디스크 활성 그릿 25~30%), JP6666749B2(패드 90 rpm·
   드레서 80 rpm), US10822524B2(테이블 17·드레서 20 rpm), US20070011952A1(테이블·디스크 100 rpm 동방향).
8. Lai (2001) MIT 박사논문 — 회전 운동학 상대속도식([[../physics/cmp-kinematics-rotary]]에서 확립,
   [[disk-rpm-load-radius-pcr]] §3이 디스크-패드 쌍에 치환). Lawing (2004) NCCAVS CMPUG 슬라이드 —
   "Below a critical down-force, polish rate will drop … Above critical down-force rate saturates".

**미확보(정직 표기)** — 마모된 다이아몬드 그릿의 **팁 곡률반경** 실측을 찾기 위해 `find_open_access.py`로
질의한 후보 3편: "Aggressive Diamond Characterization and Wear Analysis during CMP"(ECS Trans., DOI:
10.1149/05201.0597ecst), "CMP Active Diamond Characterization and Conditioner Wear"(MRS Proc., DOI:
10.1557/proc-0991-c01-01), "Diamond Conditioner Microwear Effect on Pad Surface Height Distribution in W CMP"
(JJAP, DOI: 10.7567/jjap.50.05ec05). 초판(판정#22)에서는 셋 다 OA 사본 없음 → **1차 미확보**. Tabor 관계(H≈3Y, 소성개시
p_m≈1.1Y)와 원뿔 압입의 자기상사성은 교과서 지식(Johnson 1985 *Contact Mechanics*, Tabor 1951)으로
**2차 인용**이며 원문은 확보하지 않았다 — 단 §4 verify가 Saka(2008) 식(3)과 수치로 대조한다.

**1회차 재탐색(2026-09-14, §4.5)에서 원문을 확보했으나 값 A·B에 부적격으로 판정한 문헌** — 모두 `papers/`·`INDEX.json` 등록.
9. Philipossian et al. (2013), *ECS Trans.* 52(1) 597–603, DOI: 10.1149/05201.0597ecst — 후보 3편 중 1편 **확보**.
   3M A3700 디스크·CMC D100 패드 30 h; 폴리카보네이트 드래그 테스트의 furrow **단면적**(원 top-20 합 1,242/1,223 µm²
   (Orientation 1/7)가 15 h 후 45/48 % 감소)만 보고. 폭·깊이 프로파일도 팁 반경도 없어 R 역산 불가. `papers/philipossian2013-ecst-aggressive-diamond-wear-analysis.pdf`.
10. Meled et al. (2010), *J. Electrochem. Soc.* 157(3) H250–H255, DOI: 10.1149/1.3273077 — 24 h 마모시험(44.5 N,
    IC1000, iCue 600Y75/PL-7103, 25·50 °C) 전후 aggressive 다이아몬드 SEM(스케일바 50 µm). "microwear on the cutting
    edges" 정성 서술뿐, 팁 반경 수치 없음. `papers/meled2010-jes-diamond-disk-substrate-wear-microwear.pdf`.
11. Borucki et al. (2007), *Trans. Electr. Electron. Mater.* 8(1) 15–20, DOI: 10.4313/teem.2007.8.1.015 — 미확보 MRS
    C01-01의 자매 논문(KoreaScience OA, 스캔본). PTFE 코팅 디스크의 간섭계·COF·MRR 30 h 추이만, 팁 형상 수치 없음.
    `papers/borucki2007-teem-diamond-conditioner-wear-cu-cmp.pdf`.
12. Yamada et al. (2010), *J. Electrochem. Soc.* 157(6) H617–H623, DOI: 10.1149/1.3368700 — JJAP 2011 저자들의 W CMP
    논문. **에머리지로 인위 마모**시킨 다이아몬드 SEM(Fig. 8, "flat tops with rounded edges", 스케일바 없음). CMP
    실사용 마모가 아니고 수치도 없음. `papers/yamada2010-jes-pad-wear-response-w-cmp.pdf`.
13. Kim, Saka & Chun (2014), *ECS J. Solid State Sci. Technol.* 3(5) P169–P178, DOI: 10.1149/2.027405jss (CC-BY) —
    Table II IC1000 Berkovich 90 nm 압입: **H 290 ± 220 MPa, E 2.21 ± 1.59 GPa**, 실측 최대 H 915 MPa(n>100). 경도이지
    항복강도 직접값이 아니다(값 B 부적격, §4.5 감도 대용). `papers/kim2014-jss-pad-scratching-mechanical-tribological.pdf`.
14. Bastawros, Chandra & Gouda (2019), *ECS J. Solid State Sci. Technol.* 8(5) P3145–P3153, DOI: 10.1149/2.0201905jss —
    **건식** IC1000 벌크 E 200–500 MPa, "saturation stress of about 20 MPa"(다공 압축 플래토, 본문 서술·시험조건 미기재),
    치밀 PU 가정 E_pad 1.7 GPa. 항복강도 직접 실측이 아니다(값 B 부적격, §4.5 감도 대용).
    `papers/bastawros2019-jss-multiscale-pad-response.pdf`.

## 2. 사유(1) 디스크 자전비 Rs 보정 — μ에 대한 폐형식 상계

### 2.1 유도
[[disk-rpm-load-radius-pcr]] §3의 치환식에서 디스크 위 점 (r̄, θ)의 상대속도는
`|v|/(ω_p r_cc) = sqrt(1 + 2εcosθ + ε²)`, ε = r̄μ, μ = (R_disk/r_cc)(1−Rs), Rs = ω_disk/ω_pad.
Γ는 디스크 **전체**가 패드에 가하는 절삭일률(P·v의 면적 적분)이므로, 균일 압력·균일 그릿밀도 가정
아래 필요한 것은 **면적평균** ⟨|v|⟩다.

θ 평균은 완전타원적분으로 닫힌다: `(1/2π)∮ sqrt(1+2εcosθ+ε²) dθ = (2/π)(1+ε)·E(k)`, k² = 4ε/(1+ε)².
ε<1에서 급수 전개하면 `1 + ε²/4 + ε⁴/64 + O(ε⁶)` (sqrt(1+x)의 x=2εcosθ+ε² 전개 후 ⟨cos²θ⟩=1/2 사용:
1차 항 ε²/2, 2차 항 −(4ε²/2)/8 = −ε²/4, 합 ε²/4). 면적 가중 2r̄dr̄로 r̄∈[0,1] 적분하면

```
⟨|v|⟩_area / (ω_p r_cc) = 1 + μ²/8 + μ⁴/192 + O(μ⁶)       →  c = 1/8
```

⚠ [[disk-rpm-load-radius-pcr]] §6 verify의 "1.00044"는 `np.linspace(0,1,200)`로 **반경 균등**(면적 가중
아님) 샘플이었다 — 그 가중에서는 c=1/12(=0.000434)이고, 물리적으로 옳은 면적 가중은 c=1/8(0.000652)이다.
둘 다 0.1% 미만이라 그 노트의 결론은 바뀌지 않지만, 계수는 여기서 정정한다(**재현 대조**: μ=0.0722에서
면적평균 편차 0.0652 % vs 반경균등 0.0435 %, 아래 verify).

### 2.2 실제로 가능한 μ 범위 (문헌)
| 출처 | 패드/디스크 rpm | Rs | 1−Rs | 비고 |
|---|---|---|---|---|
| Zheng 2023 Table 1 | 100 / 73 | 0.73 | 0.27 | 디스크 R=52.25 mm, 스윕 r_cc 83~308 mm → R/r_cc ≤ 0.63 |
| McAllister 2019 | 87 / 60 | 0.69 | 0.31 | 둘 다 반시계(동방향) 명시 |
| Kwon 2013 | 73 / 93 | 1.27 | −0.27 | 방향 미기재 |
| JP6666749B2 | 90 / 80 | 0.89 | 0.11 | 특허 실시예 |
| US10822524B2 | 17 / 20 | 1.18 | −0.18 | ex-situ 150 N |
| US20070011952A1 | 100 / 100 | 1.00 | 0 | 동방향 명시 |
| Tsai 2014 (실험실) | 40 / 10 | 0.25 | 0.75 | 소형 랩 장비, r_cc 미기재 |

산업 장비 6건은 |1−Rs| ≤ 0.31, 실험실 1건까지 넓히면 ≤ 0.75. R_disk/r_cc는 Zheng의 스윕 내측 반환점
(83 mm)에서 최대 0.63이고, 스윕 구간 균등 체류 가정의 평균 ⟨(R/r_cc)²⟩ = 0.107(∫dr_cc/r_cc² 해석적분).
역회전(1−Rs>1)은 확보한 문헌 어디에도 없다 — **범위 밖은 이 판정의 보증 대상이 아니다**.

### 2.3 verify — 계수 c 해석 vs 수치, 문헌 범위 최대 편차
```python verify
import numpy as np
from scipy.special import ellipe

def theta_avg_numeric(eps, n=20000):
    th = np.linspace(0, 2*np.pi, n, endpoint=False)
    return np.sqrt(1 + 2*eps*np.cos(th) + eps**2).mean()

def theta_avg_closed(eps):
    return (2/np.pi) * (1+eps) * ellipe(4*eps/(1+eps)**2)

# (a) θ 평균 폐형식(완전타원적분) = 수치적분
for eps in (0.05, 0.1, 0.3, 0.5, 0.9):
    assert abs(theta_avg_numeric(eps) - theta_avg_closed(eps)) < 1e-6, eps

def disk_area_avg(mu, n=4000):
    r = (np.arange(n) + 0.5) / n                       # 면적 가중 2r dr (중점법)
    return float(np.sum(theta_avg_closed(r*mu) * 2*r) / n)

def disk_radial_uniform_avg(mu, n=4000):
    r = np.linspace(0, 1, n)                           # disk-rpm-load-radius-pcr §6의 가중(반경 균등)
    return float(np.mean(theta_avg_closed(r*mu)))

series = lambda mu: mu**2/8 + mu**4/192

# (b) 계수 c=1/8 (면적 가중), 1/12 (반경 균등) — μ≤0.5에서 급수와 수치 1e-4 이내
for mu in (0.0722, 0.195, 0.28, 0.47):
    dev = disk_area_avg(mu) - 1
    assert abs(dev - series(mu)) < 1e-4, (mu, dev, series(mu))
    assert abs((disk_radial_uniform_avg(mu) - 1) - mu**2/12) < 2e-4

# (c) Zheng 2023 Table 1 조건 재현: μ=0.0722 → 면적평균 편차 0.065 %, 반경균등 0.043 %(§6의 1.00044)
mu_z = 0.0722
assert abs(disk_area_avg(mu_z) - 1.000652) < 2e-5
assert abs(disk_radial_uniform_avg(mu_z) - 1.000435) < 2e-5

# (d) 문헌 범위: 산업 6건 |1-Rs|<=0.31, 실험실 포함 <=0.75; R_disk/r_cc 순간 최대 0.63(83 mm), 스윕평균 <(R/r_cc)^2>=0.107
R_disk, r_in, r_out = 52.25, 83.0, 308.0             # mm, Zheng 2023 Table 1
ratio_max = R_disk / r_in
ratio_sq_sweep = R_disk**2 * (1/r_in - 1/r_out) / (r_out - r_in)
assert abs(ratio_max - 0.630) < 1e-3 and abs(ratio_sq_sweep - 0.1068) < 1e-3

def worst(one_minus_rs):
    inst = disk_area_avg(ratio_max * one_minus_rs) - 1                  # 내측 반환점 순간값
    sweep = series(np.sqrt(ratio_sq_sweep) * one_minus_rs)              # 스윕 평균(μ²∝⟨(R/r_cc)²⟩)
    return inst, sweep

inst_ind, sweep_ind = worst(0.31)     # 산업 최악(McAllister 2019)
inst_lab, sweep_lab = worst(0.75)     # 실험실 포함 최악(Tsai 2014)
print(f"산업 |1-Rs|=0.31: 내측 순간 {inst_ind*100:.2f}%  스윕평균 {sweep_ind*100:.3f}%")
print(f"실험실 |1-Rs|=0.75: 내측 순간 {inst_lab*100:.2f}%  스윕평균 {sweep_lab*100:.2f}%")
assert inst_ind < 0.01 and sweep_ind < 0.002      # 산업: 순간값도 1% 미만, 스윕평균 0.2% 미만
assert sweep_lab < 0.01 and 0.02 < inst_lab < 0.03  # 실험실 극단: 스윕평균 1% 미만, 순간값은 2~3%

# (e) 디스크 rpm 고정(73)·플래튼 rpm 변화 시 Γ 비율 오차가 스윕평균 1%를 넘는 플래튼 rpm 경계
one_minus_rs_1pct = np.sqrt(0.01 * 8 / ratio_sq_sweep)     # μ²/8 = 1% 되는 |1-Rs|
lo = 73 / (1 + one_minus_rs_1pct); hi = 73 / (1 - one_minus_rs_1pct)
print(f"|1-Rs| 경계 {one_minus_rs_1pct:.3f} → 플래튼 {lo:.0f}~{hi:.0f} rpm 안에서 스윕평균 편차 <1%")
assert 0.85 < one_minus_rs_1pct < 0.88 and lo < 40 and hi > 500
print("PASS: c=1/8 확인, 문헌 범위 내 총량 편차 <1%")
```

### 2.4 판정 — **해소(총량 스칼라에 한해)**
- Γ의 v항 오차는 `[1+dev(μ_now)]/[1+dev(μ_ref)] − 1`이므로 위 최대 편차가 곧 상계다. 확보한 문헌 범위
  전체(|1−Rs| ≤ 0.75, R_disk/r_cc ≤ 0.63)에서 **스윕평균 편차 < 1%**, 산업 조건에서는 < 0.2%다.
  이는 rpm_platen 자체의 표기 해상도(1 rpm/55 rpm ≈ 1.8%)보다 작다.
- 따라서 **Rs 드라이버 부재는 스칼라 총량 Γ의 등급을 제한하는 결측이 아니다.** 단 이 판정은
  **반경별 분포**에 대한 주장이 아니다 — 디스크 에지의 peak-to-peak 14.4%([[disk-rpm-load-radius-pcr]] §4)는
  여전히 존재하며 [[conditioner-sweep-kinematics-pcr-profile]]·[[disk-kinematics-sweep-pcr-prediction-model]]
  (분포 모듈)의 몫으로 남는다. 역회전 레시피(1−Rs>1)가 나타나면 이 상계는 재계산해야 한다.

## 3. 사유(2) PCR 시간감쇠 앵커(τ) — 기준조건에서 항등적으로 무관

### 3.1 사실
5팩 전부 `cond_disk_usage_hours = 0.0`, `cond_ref_disk_usage_hours = 0.0`이고 `_f_gamma`는
`A = pcr_decay(t,1,τ)/pcr_decay(t_ref,1,τ) = exp(−(t−t_ref)/τ)` **비율**만 쓴다. t = t_ref이면 τ가 무엇이든
A ≡ 1. 즉 2차 인용 앵커(TAU_AGING_HOURS≈27.4 h, EVIDENCE-RULES 판정#14)는 **기준조건 Γ에 영향을 줄 수
없다**. 반대로 t ≠ t_ref이면 A = exp(−Δt/τ)라 τ가 결과를 지배한다(20 h에서 τ 10배 → A 0.48→0.93).

### 3.2 verify — τ를 10배·1/10배로 바꿔도 기준조건 Γ 불변, 20 h에서는 변함
```python verify
import sys
sys.path.insert(0, ".")
from sim.engine import Recipe
from sim.factors import compute_factors
import conditioner_pcr_decay as CPD      # sim/tier2_physics (engine이 path에 넣음)

def gamma(pack, **ov):
    return compute_factors(Recipe(pack=pack, pack_overrides=ov).resolve())["gamma"]

tau0 = CPD.TAU_AGING_HOURS
assert abs(tau0 - 27.28) < 0.01, tau0          # 판정#14의 27.4 h (반올림), 정확값 27.284
try:
    for pack in ("oxide_silica", "cu_h2o2_bta", "w_fe_oxidizer", "sti_ceria", "sic_ceria_h2o2"):
        vals = {}
        for k in (1.0, 10.0, 0.1):
            CPD.TAU_AGING_HOURS = tau0 * k
            vals[k] = gamma(pack).value                       # 기준조건 t=t_ref=0
        assert abs(vals[10.0] - vals[1.0]) < 1e-12 and abs(vals[0.1] - vals[1.0]) < 1e-12, (pack, vals)
        assert abs(vals[1.0] - 1.0) < 1e-12                   # 기준조건 Γ=1.0 계약
    # t = t_ref ≠ 0 도 항등 (비율이라서)
    CPD.TAU_AGING_HOURS = tau0
    g_a = gamma("oxide_silica", cond_disk_usage_hours=20.0, cond_ref_disk_usage_hours=20.0).value
    CPD.TAU_AGING_HOURS = tau0 * 10
    g_b = gamma("oxide_silica", cond_disk_usage_hours=20.0, cond_ref_disk_usage_hours=20.0).value
    assert abs(g_a - g_b) < 1e-12 and abs(g_a - 1.0) < 1e-12
    # 반면 t=20 h, t_ref=0 이면 τ가 지배
    CPD.TAU_AGING_HOURS = tau0
    a1 = gamma("oxide_silica", cond_disk_usage_hours=20.0).terms["aging(pcr_decay)"]
    CPD.TAU_AGING_HOURS = tau0 * 10
    a10 = gamma("oxide_silica", cond_disk_usage_hours=20.0).terms["aging(pcr_decay)"]
finally:
    CPD.TAU_AGING_HOURS = tau0
import math
assert abs(a1 - math.exp(-20/tau0)) < 1e-9 and abs(a10 - math.exp(-20/(10*tau0))) < 1e-9
assert abs(a1 - 0.4804) < 1e-3 and abs(a10 - 0.9294) < 1e-3
print(f"기준조건: τ×10, ×0.1에서 Γ 동일(5팩). 20 h: A(τ)={a1:.4f}, A(10τ)={a10:.4f} — τ가 지배")
```

### 3.3 판정 — **조건부 하한으로 전환**
앵커의 2차 인용성(판정#14, 뒤집지 않음)은 사실이지만 그것이 등급을 제한하는 것은 **A가 1에서 벗어나는
조건에서만**이다. `_f_gamma`는 |A−1| > 0.01일 때만 이 사유로 `estimated` 하한을 걸고 notes에 이유를
남기도록 바꿨다(`GAMMA_AGING_CONF_TOL`). 기준조건에서는 이 사유가 등급을 건드리지 않는다.
이것은 부풀리기가 아니라 하한을 **실제로 필요한 곳에만** 거는 것이며, t≠t_ref에서는 지금과 같이
estimated다. (다만 §4의 사유(3)이 남아 기준조건 등급은 결과적으로 estimated 그대로다.)

## 4. 사유(3) 임계하중 — 제1원리 유도와 운전점 대조

### 4.1 유도 (구형 팁 Hertz 접촉의 소성 개시 하중)
반경 R의 강체 구(다이아몬드, E≈1000 GPa ≫ 패드)가 탄성 반무한체(E*)를 누를 때 Hertz:
`a = (3PR/4E*)^{1/3}`, `p_max = 3P/(2πa²) = (6PE*²/(π³R²))^{1/3}`, `p_m = (2/3)p_max`.
Tabor: 소성 개시는 평균접촉압력 `p_m ≈ 1.1Y`(Tresca, ν≈0.3에서 p_max≈1.6Y와 등가) → `p_max = 1.65Y`.
대입해 P에 대해 풀면

```
P_c = π³ R² (1.65·Y)³ / (6 E*²)  ≈ 23.2 · R² Y³ / E*²          (Y = 항복강도, E* ≈ E_p/(1−ν_p²))
δ_c = a_c²/R = (1.65π/2)² (Y/E*)² R                            (개시 시 탄성 압입깊이)
```
Saka et al. (2008) 식(3) `P_Y = (π³/48)·H³R²/E²`은 같은 구조에서 개시 기준을 `p_max = H/2`로 둔 것이다.
Tabor H≈3Y를 넣으면 본 유도의 기준은 `p_max = 0.55H`이므로 두 식의 비는 (0.55/0.5)³ = 1.331 —
아래 verify가 이 비를 재현한다(**대조 일치**). 보수적(P_c가 큰) 쪽인 본 유도를 판정에 쓴다.

**뾰족한 원뿔·각뿔에는 임계하중이 없다.** 이상적 원뿔은 길이 척도가 없어(자기상사) 접촉반경 a ∝ δ,
하중 P ∝ E*·a²·cot(반각)이고 평균압력 `p_m = P/(πa²) ∝ E*·cot(반각)`은 **하중과 무관**하다. 따라서
p_m > 1.1Y 여부는 각도·재료로만 정해져 모든 하중에서 소성이거나 모든 하중에서 탄성이다 — "어느 하중
아래에서 절삭이 멈춘다"는 문턱은 **팁이 마모로 둥글어진 그릿에서만** 생긴다(둥근 팁의 곡률반경 R이
길이 척도를 공급). 그래서 P_c의 크기는 전적으로 R에 달려 있고, R이 (3)의 결정 변수다.

### 4.2 문헌값 확보 현황
| 항목 | 값 | 출처 | 상태 |
|---|---|---|---|
| (a) 패드 탄성률 E_p | 0.5 GPa | Saka 2008 본문(IC1000, 습식) | 확보 |
| (a) 패드 경도 H_p | 0.05 GPa (국소 0.01~0.31) | Saka 2008 본문·Fig.9 | 확보 |
| (a) 항복강도 Y | H/3 ≈ 16.7 MPa | Tabor 관계(2차 인용) | 환산 — **직접 실측 2회차까지 미확보**(§4.5·§4.6) |
| (a) 대용 H·E (감도용) | H 290 MPa·E 2.21 GPa(건식? 미기재, Berkovich 90 nm) / Y_sat≈20 MPa·E 0.2~0.5 GPa(건식 압축) | Kim 2014 Table II / Bastawros 2019 본문(§1 13·14) — Kim2013 MIT 학위논문·Gouda2004 ISU 학위논문 원문(§4.6)으로 재확인, 같은 데이터 계열 | 확보, 단 Y 직접값 아님 |
| (a) 대안 E | 1.0 GPa / 0.117 GPa | base.yaml `pad_E_star_pa`(estimated) / [[../materials/pad-hardness-porosity-measurement-methods]] §8 Qi eq(11)(사용 불가 판정) | 감도용 |
| (b) 마모 그릿 팁 반경 R | **미확보** | 후보 3편 중 ECS Trans.만 확보(단면적뿐), MRS·JJAP 미확보; 추가 4편도 수치 없음(§1 9~12, §4.5); 2회차 CORE 검색 5편도 전부 패드 애스퍼리티뿐(§4.6) | 2회차 재탐색 후에도 미확보 |
| (b) 기하 상한 | D/2 = 90 µm (E187 181 µm 그릿), Ring Table 2 β=D/2=95 µm | [[conditioner-disk-spec-recipe-industrial]] §2, [[conditioner-asperity-population-balance]] §5 | 상한만 |
| (b) 참고 | DOP≈15 µm | Pysher 2010 | 깊이이지 반경 아님 |
| (c) 그릿 총수 N_total | π(52.25 mm)²/(430 µm)² = 46,386 | Zheng 2023 Table 1(정방격자 가정) | 계산 |
| (c) 대안 N_total | 25,000 / 40,000 / 17k~60k | Tsai 2014 / Kwon 2013 / Kwon 2013 | 확보 |
| (c) 작동 비율 f_active | <10% / 25~30% / >75%(신설계 청구항) | Tsai 2014 / US8657652B2 Fig.6 / US8657652B2 청구항 1 | 확보 |

### 4.3 verify — P_c, 그릿당 하중, 임계 downforce, 감도분석
```python verify
import math
LBF = 4.4482216152605                       # N, 정의값
F_pack = 4.0 * LBF                          # cond_downforce_lbf=4.0 (5팩 공통, Zheng 2023 Table 1 조건)

# (a) Saka 2008 IC1000 물성 (본문 그대로)
E_p, H_p = 0.5e9, 0.05e9
Y = H_p / 3.0                               # Tabor H≈3Y (2차 인용)
E_star = E_p                                # ν_p=0 → E* 하한 → P_c 상한(보수적)

def P_c(R, Y=Y, E=E_star):                  # §4.1 유도식
    return math.pi**3 * R**2 * (1.65*Y)**3 / (6*E**2)
def P_saka(R, H=H_p, E=E_star):             # Saka 2008 식(3)
    return math.pi**3/48 * H**3 * R**2 / E**2
def delta_c(R, Y=Y, E=E_star):
    return (1.65*math.pi/2)**2 * (Y/E)**2 * R

# 유도식 vs Saka 식(3): 개시 기준 차이(0.55H vs 0.5H)만큼 1.331배 — 대조 일치
assert abs(P_c(50e-6)/P_saka(50e-6) - 1.331) < 0.002
# 기준 대입: R=90 µm → P_c 3.48 mN, R=15 µm → 0.097 mN (R² 스케일)
assert abs(P_c(90e-6)*1e3 - 3.482) < 0.01 and abs(P_c(15e-6)*1e3 - 0.0967) < 0.001
assert abs(P_c(90e-6)/P_c(15e-6) - 36.0) < 0.01

# (c) 그릿 수: Zheng 2023 Table 1 피치 430 µm·유효직경 104.5 mm → 46,386개 (정방격자)
N_total = math.pi * (52.25e-3)**2 / (430e-6)**2
assert abs(N_total - 46386) < 1
f_active = {"tsai_lt10pct": 0.10, "us8657652_conv": 0.30}
per_grit = {k: F_pack / (N_total * f) for k, f in f_active.items()}     # N
assert abs(per_grit["tsai_lt10pct"]*1e3 - 3.835) < 0.01
assert abs(per_grit["us8657652_conv"]*1e3 - 1.278) < 0.01

# 중심 사례(가정 R=15 µm, f=10%): 하중/P_c ≈ 40배, 임계 downforce 0.10 lbf
ratio_central = per_grit["tsai_lt10pct"] / P_c(15e-6)
Fc_central_lbf = N_total * 0.10 * P_c(15e-6) / LBF
print(f"중심 사례 R=15µm,f=10%: 그릿당 {per_grit['tsai_lt10pct']*1e3:.2f} mN vs P_c {P_c(15e-6)*1e3:.3f} mN "
      f"→ {ratio_central:.0f}배, 임계 downforce {Fc_central_lbf:.3f} lbf")
assert 39 < ratio_central < 41 and 0.09 < Fc_central_lbf < 0.11

# 감도분석: 각 입력을 P_c가 커지는(보수적) 쪽으로 밀었을 때 결론(오더 차이)이 유지되는가
flips = {}
# (b) R → 기하 상한 D/2 = 90 µm (팁 반경 문헌 미확보)
flips["R=90um"] = per_grit["tsai_lt10pct"] / P_c(90e-6)              # 1.10배
# (c) N_active → 60k×30% = 18,000 (Kwon 2013 최대밀도 × US8657652B2 종래 상한), R=90 µm
flips["R=90um,N=18000"] = (F_pack/18000) / P_c(90e-6)                  # 0.28배
# (a) E → 0.117 GPa (Qi 2003 eq11 추정, 사용불가 판정이지만 감도용), R=20 µm
flips["E=0.117GPa,R=20um"] = per_grit["tsai_lt10pct"] / P_c(20e-6, E=0.117e9)   # 1.2배
# (a) H 국소 상한 0.31 GPa (Saka Fig.9), R=15 µm
flips["H=0.31GPa,R=15um"] = per_grit["tsai_lt10pct"] / P_c(15e-6, Y=0.31e9/3)   # 0.17배
for k, v in flips.items():
    print(f"  보수적 밀기 {k}: 하중/P_c = {v:.2f}배")
assert all(v < 10 for v in flips.values()), "보수적 밀기에서도 오더 차이가 남으면 해소 가능 — 그렇지 않다"
assert flips["R=90um,N=18000"] < 1 and flips["H=0.31GPa,R=15um"] < 1   # 부호까지 뒤집힘(운전점이 임계 아래)

# 임계 downforce의 범위: (R, N_active) 조합에 따라 0.02~14 lbf — 운전점 4 lbf를 가로지른다
Fc = {(R, N): N * P_c(R) / LBF for R in (15e-6, 90e-6) for N in (850, 4640, 18000)}
assert min(Fc.values()) < 0.02 and max(Fc.values()) > 14
assert min(Fc.values()) < 4.0 < max(Fc.values())
print("임계 downforce 범위(lbf):", {f"R={R*1e6:.0f}um,N={N}": round(v, 3) for (R, N), v in Fc.items()})

# 보조: 개시 시 탄성 압입깊이 δ_c ≤ 0.67 µm(R=90 µm) ≪ 3M DOP 15 µm → 작동 그릿은 개시를 훨씬 넘어 있다
assert delta_c(90e-6)*1e6 < 0.7 and 15.0 / (delta_c(90e-6)*1e6) > 20
print("PASS: 임계하중 판정 — 입력 불확실성이 결론을 뒤집는다(미해소)")
```

### 4.4 판정 — **미해소(하한 유지)**
- 중심 사례(R=15 µm 가정, 작동 10%)만 보면 그릿당 하중이 P_c의 약 40배, 임계 downforce ≈ 0.10 lbf로
  운전점(4 lbf)에서 멀다. 그러나 이 결론은 **팁 반경 R의 가정에 R²로 걸려 있고**, R의 1차 문헌값이 없다.
- 보수적 밀기 4건 중 어느 하나만으로도 오더 차이가 사라지고(1.1배, 1.2배), 두 건은 부호까지 뒤집혀
  운전점이 임계 **아래**가 된다(0.28배, 0.17배). 임계 downforce의 범위(0.02~14 lbf)가 4 lbf를 가로지른다.
- 판정 규칙대로 **하한 유지**. 부족한 것은 구체적으로 (b) 마모 그릿 팁 곡률반경의 실측(§1 후보 3편 중
  1편이라도 원문 확보), 그리고 (a) IC1000류의 항복강도 자체(경도→Y 환산이 아닌 직접값)다. 이 둘이
  확보돼 R ≤ 30 µm·Y/E* ≥ 0.03이 확인되면 P_c ≤ 0.4 mN으로 하중 하한(1 mN)보다 작아져 재판정할 수 있다.
- 보조 관찰(판정 근거 아님): 3M DOP 15 µm(Pysher 2010)는 개시 압입깊이 δ_c(≤0.67 µm)의 20배 이상이므로
  **작동 중인** 그릿은 소성 영역 깊숙이 있다 — 그러나 3M의 하중이 미기재라 F_c를 구속하지 못한다.
- 별개 비선형(주의): Lawing (2004)의 "critical down-force"는 연마율(MRR)이 컨디셔너 하중에 **포화**하는
  상단 무릎이지 절삭 개시 문턱이 아니다([[conditioning-mechanism-asperity-regeneration]] §3). Γ(부하 스칼라)의
  정의 밖이며, Γ를 소비하는 S 쪽 과제로 남긴다.

### 4.5 1회차 재탐색(2026-09-14) — 값 A·B 모두 미확보, 하한 유지
과제: §4.4의 해제 조건 두 값(A: 마모 그릿 팁 곡률반경 R ≤ 30 µm 실측, B: IC1000급 항복강도 직접 실측 Y/E* ≥ 0.03)의
1차 문헌 확보. 결과 **(다) 둘 다 미확보** — 코드·격자 불변. 아래는 다음 회차가 반복하지 않도록 남기는 질의 이력이다.

**저장소 내부(1순위)** — `knowledge/`·`_knowledge_audit/`·`papers/INDEX.json` 전수 grep(항복/yield strength, 팁 반경/tip radius/
radius of curvature/worn/blunt) + 로컬 코퍼스 `data/corpus/corpus.sqlite` 전문 1,510건 정규식 스캔 + 로컬 PDF 24편 fitz 스캔.
팁 반경은 전부 **패드 애스퍼리티**(β=D_grit/2 규칙, Kim 2014 Ra 23.9 µm) 또는 AFM 프로브 얘기였고, 항복강도는 전부
Saka 2008 경도의 Tabor 환산(본 노트와 동일) 또는 일반 서술이었다. 새 값 0건.

**값 A(마모 팁 반경) 외부 탐색** — 확보 6편·미확보 3편, 전부 부적격:
- 확보(§1 9~12): ECS Trans. 2013(furrow 단면적만), Meled 2010 JES(SEM 정성, 50 µm 스케일에서 절삭날 microwear가
  식별될 뿐 반경 판독 불가), Borucki 2007 TEEM(간섭계 코팅 마모만), Yamada 2010 JES(에머리지 인위 마모·스케일바 없음).
  추가로 Tan & Cheng 2007 *Wear* 262 693(DOI: 10.1016/j.wear.2006.08.001, 무게감량·부식만), Tsai & Chen 2010 IJAMT 55 253
  (DOI: 10.1007/s00170-010-3055-y, 신품 형상 3종 비교·"sharp edges rounded off" 2차 서술만), Sun 2010 MEE 87 553(DOI:
  10.1016/j.mee.2009.08.007, 패드 애스퍼리티 곡률만)도 원문 확인 후 부적격.
- 미확보: MRS Proc. 991 C01-01(미러 사이트 404, 미러 사이트/.st 무응답), JJAP 50 05EC05·JJAP 47 6282(IOP `/pdf`·landing 모두
  Radware validate.perfdrive.com 리다이렉트; 미러 사이트은 200을 주지만 **전혀 다른 논문**(J. Phys. E 1968, J. Phys. A 2000)을
  내줌 — 1쪽 제목 확인으로 폐기), Sung 2021 *Handbook of Industrial Diamonds* ch.8(bban 404), Oh 2018 ECS MA(초록만).
- 질의 문자열: Crossref `query.bibliographic` "diamond conditioner wear tip radius CMP pad"(10건)·"worn diamond grit tip radius pad
  conditioner"(10)·"diamond disk conditioner wear SEM tip rounding CMP"(10)·"diamond grit tip radius wear conditioner SEM measurement
  pad conditioning lifetime"(10)·"conditioner diamond wear flat area attrition CMP pad cut rate decay"(10)·"Borucki diamond conditioner
  active diamonds wear characterization"(10); OpenAlex `search`+`is_oa:true` 4질의(174/3/4/1건)·`fulltext.search` "diamond conditioner"
  "tip radius"(3건: CBN 연삭·Cu CMP 학위논문·GaTech 학위논문, 전부 AFM/연삭 맥락)·"pad conditioner" diamond "radius of curvature"
  worn(3건, 패드 애스퍼리티)·"conditioner" diamond "wear flat"(1건, 무관)·"dresser" diamond "tip radius"(1건, 리뷰). 결론: **CMP 실사용
  마모 그릿의 팁 곡률반경 수치는 OA·미러 접근 범위에 존재하지 않는다.** 남은 길은 MRS C01-01·JJAP 2편의 **다른 경로**(UA 리포지토리
  Wei 2010 학위논문 — API가 이번 세션엔 403, Hitachi 저자 기관 리포지토리)뿐이다.

**값 B(IC1000 항복강도 직접값) 외부 탐색** — 확보 9편·미확보 5편, 직접 실측 0건:
- 확보: Kim 2014 JSS(경도, §1 13), Bastawros 2019 JSS(다공 플래토 20 MPa 서술, §1 14), Kim/Saka/Chun 2013 ECS Trans. 50(39) 35
  (DOI: 10.1149/05039.0035ecst, 같은 Berkovich 데이터), He 2017 JSS 6 P178(DOI: 10.1149/2.0321704jss, 압축 E 29±4 MPa·ν 0.17,
  항복 없음), Bajaj 1994 MRS 337 637(DOI: 10.1557/proc-337-637, 전단탄성률·밀도만), Tregub 2002 MRS 732 I5.4(DOI:
  10.1557/proc-732-i5.4, DMA만), Wang 1997 JES 144 1121(DOI: 10.1149/1.1837542, FEM 입력 탄성률만), Ronay 2004 JES 151 G847
  (DOI: 10.1149/1.1812738, 2차 수직력), Yeruva 2009 JES(DOI: 10.1149/1.3186032, 접촉면적), Bozkaya 2009 JES 156 H890
  (DOI: 10.1149/1.3231691, 모델 입력 E만), Kim 2014 Procedia CIRP 14 42(DOI: 10.1016/j.procir.2014.03.014, E/H=7.6 가정).
- 미확보(리포지토리 봇차단): Bozkaya 2009 Northeastern 학위논문(DOI: 10.17760/d10019194, 403/418 — OpenAlex 전문검색에
  "IC1000"+"stress-strain curve"+"uniaxial" 히트, **다음 회차 1순위**), USF 2005 학위논문(403), Doddabasanagouda ISU 학위논문
  (DOI: 10.31274/rtd-20201023-76, Bastawros 2019의 원 데이터, ISU DR 403), Ponte 2015 URI 학위논문(DOI:
  10.23860/thesis-ponte-david-2015, bepress 403), Huy 2023 JJAP(DOI: 10.35848/1347-4065/acd42a, IOP 차단·HAL Anubis·bban 404;
  전문검색에 "IC1000"+"stress-strain curve"+"tensile test"+"yield" 히트), Lu 2002 Mater. Charact. 49 177(DOI:
  10.1016/s1044-5803(03)00004-4, DMA, bban 404).
- 질의 문자열: Crossref "polyurethane CMP pad yield strength tensile test IC1000"·"mechanical properties polishing pad IC1000 stress
  strain compression yield"·"strain rate dependent mechanical behavior polyurethane CMP pad"·"uniaxial tensile properties chemical
  mechanical polishing pad polyurethane yield"·"CMP pad mechanical characterization tensile compression modulus yield stress wet dry
  soaking"·"nanoindentation polishing pad polyurethane yield stress elastic modulus CMP"(각 10건); OpenAlex `fulltext.search`
  "IC1000" "yield strength"(7)·"IC1000" "yield stress"(4)·"IC1000" tensile "elongation"(2)·"IC1000" "uniaxial"(4)·"IC1000"
  "stress-strain curve"(2)·"polishing pad" polyurethane "tensile test" "yield"(9)·"CMP pad" "stress-strain" tensile polyurethane yield(2).

**대용값으로 본 감도(판정 근거 보강, 채택 아님)** — 확보한 두 경도·플래토 대용값을 Y로 쓰면 P_c는 기준(Y 16.7 MPa·E 0.5 GPa)보다
**커진다**(아래 verify: Kim 2014 ×10.0, Bastawros 2019 ×1.7~×10.8). 즉 B의 후보 수치들은 하한 해제 쪽이 아니라 **유지 쪽**을
가리킨다. 중심 사례(R=15 µm, f=10 %)의 하중/P_c 40배가 3.7~23배로 줄고, R=30 µm이면 1배 이하로 떨어져 부호가 뒤집힌다.

```python verify
import math
LBF = 4.4482216152605; F_pack = 4.0*LBF; N_total = math.pi*(52.25e-3)**2/(430e-6)**2
per_grit = F_pack/(N_total*0.10)                     # §4.3 중심 사례 그릿당 하중 3.835 mN
def P_c(R, Y, E): return math.pi**3*R**2*(1.65*Y)**3/(6*E**2)
base = P_c(15e-6, 0.05e9/3, 0.5e9)
# Kim 2014 Table II: H 290 MPa → Y=H/3, E 2.21 GPa (Berkovich 90 nm, 경도 대용)
kim = P_c(15e-6, 290e6/3, 2.21e9)
# Bastawros 2019: saturation stress 20 MPa, 벌크 E 200~500 MPa (건식 압축 플래토 대용)
bas_lo, bas_hi = P_c(15e-6, 20e6, 0.5e9), P_c(15e-6, 20e6, 0.2e9)
print(f"P_c 배율 — Kim 2014: {kim/base:.1f}x, Bastawros 2019: {bas_lo/base:.1f}x~{bas_hi/base:.1f}x")
assert abs(kim/base - 10.0) < 0.1 and abs(bas_lo/base - 1.73) < 0.02 and abs(bas_hi/base - 10.8) < 0.1
r15 = [per_grit/P for P in (kim, bas_lo, bas_hi)]
print("R=15 µm 하중/P_c:", [round(x, 1) for x in r15])
assert min(r15) > 3.6 and max(r15) < 24
r30 = [per_grit/P_c(30e-6, Y, E) for (Y, E) in ((290e6/3, 2.21e9), (20e6, 0.2e9))]
assert all(x < 1.05 for x in r30), r30                # R=30 µm에서 부호 반전 — 하한 유지
print("PASS: B 대용값은 P_c를 키워 하한 유지 쪽 — 판정 불변")
```

**판정: 미해소 유지(변경 없음).** EVIDENCE-RULES 판정#22 행에 1회차 기록. 3회차 규칙: 2회차는 위 "다음 회차 1순위"(Bozkaya 학위논문·
Wei 2010 UA 학위논문·Huy 2023) 경로만 시도하고, 그래도 없으면 "R·Y 직접값은 이 코퍼스로 못 낸다"로 스코프 축소 종결한다.

### 4.6 2회차 재탐색(2026-09-14) — 값 A·B 모두 미확보(재확인), 하한 유지

과제: §4.5가 지정한 "다음 회차 1순위" 경로(Bozkaya 2009 Northeastern 학위논문·Wei 2010 UA 학위논문·
Gouda ISU 학위논문·Ponte 2015 URI 학위논문·Huy 2023 JJAP)를 1회차와 **다른 접근**(직접 PDF 엔드포인트,
OpenAlex `best_oa_location`/CORE API, Semantic Scholar Graph API, 미러 사이트 재시도)으로 시도했다.
결과: **1차 지정 5편은 전부 여전히 미확보**(리포지토리 봇차단은 그대로)였지만, CORE API 키워드 검색이
같은 저자군의 **다른 문헌 5편**을 원문으로 확보했다 — 그러나 **전부 값 A·B에 부적격**이었다.
값 A·B 모두 **다시 미확보**로 확정한다. 코드·격자 불변.

**직접 지정 경로 5편 — 전부 여전히 막힘(1회차와 동일 결과)**:
- Bozkaya 2009 Northeastern 학위논문(DOI: 10.17760/d10019194): OpenAlex `best_oa_location`이 직접 PDF
  URL(`repository.library.northeastern.edu/files/neu:1592/fulltext.pdf`)을 알려줬으나 UA 헤더를 붙인
  `curl -L`도 본문 10바이트 `Forbidden` — 1회차의 403/418과 동일 계열 차단, 경로만 바뀌었을 뿐 결과는 같다.
- Ponte 2015 URI 학위논문(DOI: 10.23860/thesis-ponte-david-2015): Semantic Scholar가 직접 PDF 엔드포인트
  `digitalcommons.uri.edu/cgi/viewcontent.cgi?article=1678&context=theses`를 알려줬으나 Cloudflare
  managed-challenge(`Just a moment...`, altcha 유사)로 차단 — 1회차 미시도 URL이지만 결과는 동일 계열.
- Gouda(Doddabasanagouda) ISU 학위논문(DOI: 10.31274/rtd-20201023-76): OpenAlex가 알려준 직접 URL
  `lib.dr.iastate.edu/cgi/viewcontent.cgi?article=21401&context=rtd`도 403 Forbidden. 단, **CORE API
  검색이 같은 논문을 다른 미러로 확보**했다(아래 참조) — 값 B 기준으로는 부적격이지만 원문 확보 자체는 성공.
- Huy 2023 JJAP(DOI: 10.35848/1347-4065/acd42a, "Vickers hardness of polishing pads … microtomography
  model"): Semantic Scholar가 IOP 직접 PDF URL을 줬으나 `curl`은 여전히 Radware `validate.perfdrive.com`
  HTML(14 KB)을 반환 — 1회차와 동일 차단. CORE 키워드 검색(제목 그대로)도 0건.
- Wei 2010 University of Arizona 학위논문: DOI/저자 전체이름을 특정하지 못했다. OpenAlex `search`+
  `filter=type:dissertation`(diamond conditioner/CMP pad 키워드 2질의)에 이 논문이 나타나지 않음 —
  UA 리포지토리 자체 검색(`repository.arizona.edu/simple-search`)도 JS 렌더링이라 정적 HTML만으로는
  결과 목록을 못 읽음(빈 페이지, 827바이트). **식별조차 못 함 — 3회차 과제로 남긴다.**

**CORE API 검색으로 새로 확보한 5편 — 원문 확인, 전부 값 A·B 부적격**(papers/INDEX.json 등록):
1. Doddabasanagouda 2004 ISU MS 학위논문(위 Gouda 학위논문 그 자체, `core.ac.uk/download/595616917.pdf`
   로 확보 성공 — Bastawros 2019 JSS(§1 item14 "saturation stress ≈20 MPa" 서술)의 **원 논문**이지만,
   본문에는 "plateau stress"가 Gibson & Ashby 셀룰러 고체 이론의 일반 서술(§2.x, 교과서 인용)로만
   등장하고 IC1000 실측 수치가 없다. 탄성률 E_pad=1.7 GPa(dense polyurethane)만 보고 — **20 MPa라는
   수치의 1차 출처가 이 MS 논문이 아님**이 드러났다(Bastawros 2019가 인용한 원 데이터가 이 논문이라는
   §1 item14의 추정이 틀렸을 수 있다 — 별도 확인 필요, 이 노트의 범위 밖).
2. Baisie 2012 NC A&T PhD 학위논문("Modeling, Simulation, And Optimization Of Diamond Disc Pad
   Conditioning in CMP", DOI 없음, `core.ac.uk/download/322523806.pdf`) — 컨디셔닝 디스크 자체를
   모델링하는 논문이라 정조준이었으나, "diamond shape" 논의는 정성적(원형성·규칙성)이고 팁 곡률반경
   수치는 전혀 없다.
3. Kim(Sanha) 2013 MIT PhD 학위논문("Micro-Scale Scratching by Soft Pad Asperities in CMP",
   `core.ac.uk/download/19880193.pdf`, 255쪽) — Kim 2014 JSS(§1 item13)의 **원 논문**. 나노압입 경도
   데이터가 동일(Ha,max=915 MPa for IC1000, 290±220 MPa 평균)하고 더 상세하지만, 여전히 **경도**이지
   항복강도 직접값이 아니다. "radius of curvature"는 전부 **패드 애스퍼리티**(다이아몬드 컨디셔너로
   평탄화된 후의 패드 표면 형상) 얘기이고 다이아몬드 그릿 팁 반경이 아니다 — 1회차와 동일한 혼동 함정.
4. Roberts 2011 MIT BS 학위논문("Scratching by Pad Asperities in CMP", `core.ac.uk/download/4433256.pdf`)
   — Table 4에 8종 패드의 Young's modulus·hardness(GPa) 표가 있으나 IC1000 항복강도 직접값 없음.
   "radius of curvature"(Table 5)도 패드 애스퍼리티 곡률이다.
5. Ponte(David) 2015 자신의 후속 저널 논문("Energy Dissipation and Constitutive Modeling for a
   Mechanistic Description of Pad Scratching in CMP", DOI 10.1007/s10854-015-3949-4, URI Faculty
   Publications, `core.ac.uk/download/56700522.pdf`) — 차단된 학위논문 저자 본인의 저널판. IC1000
   압축·인장 **응력완화**(stress relaxation) 실험을 27.6~170 kPa 범위에서 수행했으나 이는 점탄성
   특성화이지 항복 시험이 아니다(가한 응력이 항복 근처에도 못 미친다 — Kim2014 Tabor 환산 Y≈97 MPa,
   Bastawros 대용 20 MPa보다도 170 kPa는 두 자릿수 작다). Von Mises 항복기준은 **웨이퍼**에만 적용되고
   패드는 선형탄성으로 가정한다(패드 항복강도 자체가 이 모델의 관심사가 아님). 값 B 부적격.

**추가 시도한 경로(부적격 확인)**:
- MRS Proc. 0991-C13-02(Bozkaya & Müftü 2007, "Contact Model for a Pad Asperity and a Wafer Surface
  …") — 미확보 C01-01의 자매 논문(같은 MRS 991권). OpenAlex `is_oa: false`, Semantic Scholar
  `openAccessPdf.status: CLOSED`, CORE 키워드 검색 0건, 미러 사이트(se/st/ru DNS 실패, bban 404) 전부 실패
  — MRS 학회 논문집은 미러 사이트 커버리지 밖(1회차 §4.5의 관찰과 일치).
- Crossref bibliographic "Wei conditioner disk diamond chemical mechanical planarization dissertation
  Arizona"(10건) → 전부 무관(비-CMP 분야).
- CORE `q="tip radius" diamond conditioner CMP pad wear worn`(10건 검토) → 다이아몬드 터닝 공구 마모
  (규소 가공, Wear지 2편), 컨디셔닝 밀도 분포·FEA·드레싱 특성 논문 다수지만 전부 팁 반경 수치 없음.
  같은 질의에서 **원 미확보 후보 MRS C01-01(DOI 10.1557/proc-0991-c01-01)이 다시 나타났으나 downloadUrl
  없음**(CORE도 원문 미보유 — 폐쇄) — 1회차 판정 재확인.
- CORE `q="radius of curvature" worn diamond grit conditioning disk pad CMP`(10건) → 위 Baisie 2012
  학위논문 외 전부 FEA·드레싱 모델링 논문, 팁 반경 수치 없음.
- OpenAlex `10.1016/j.mee.2015.09.006`("Method for accelerated diamond fracture characterization in
  CMP", Elsevier MEE) · `10.1109/tsm.2020.3029763`("A Novel Method to Quantify Conditioner-to-Conditioner
  Variation and Predict Conditioner Lifetime …", IEEE TSM) — 제목상 유망했으나 둘 다 `is_oa: false`.
  미러 사이트 3개 미러(box DNS 실패, red 502 Bad Gateway, bban 404) 전부 실패.

**결론**: 지정된 1차 5편은 전부 여전히 봇차단(1회차와 동일). CORE API가 열어준 새 경로 5편은 원문을
전부 확보했지만 **값 A(다이아몬드 그릿 팁 곡률반경)·값 B(항복강도 직접 실측)** 어느 쪽도 담고 있지
않다 — 이 저자군(MIT Kim/Saka/Chun 계열, URI Ponte/Bastawros 계열, ISU Doddabasanagouda 계열)의
축적된 문헌은 전부 **패드 애스퍼리티 형상**·**나노압입 경도**·**점탄성 완화**만 측정했고, "마모된
다이아몬드 그릿의 팁 반경"과 "IC1000의 직접 항복강도"라는 두 값은 **이 저자군 코퍼스 자체에 존재하지
않는 것으로 보인다**(1회차의 잠정 결론이 2회차 다른 접근으로도 재확인됨).

> ⚠ **2회차 1차 출처 확보 실패**: Bozkaya 2009 NEU(직접 PDF 403)·Ponte 2015 URI(Cloudflare 챌린지)·
> Gouda 2004 ISU(직접 PDF 403, CORE 미러로 원문은 확보했으나 부적격)·Huy 2023 JJAP(Radware 차단)·
> Wei 2010 UA(식별 실패) — 5편 전부 값 A·B 미제공. CORE API 신규 검색 5편(Baisie 2012·Kim 2013·
> Roberts 2011·Ponte 저널판·Gouda 본문)도 원문 확보 후 부적격 확인. MRS proc-0991-c13-02·mee.2015.09.006·
> tsm.2020.3029763 3편은 폐쇄/미러실패로 미확보. **3회차 규칙**: §절차(3회차까지 보류 허용, EVIDENCE-RULES
> §서두)에 따라 다음 회차가 마지막이다. 3회차 권고: (1) Wei 2010 UA 학위논문을 OpenAlex/ProQuest에서
> 정확한 제목·DOI로 먼저 **식별**(이번 회차는 식별조차 못 함), (2) 그래도 값 A·B 미확보면 "R·Y 직접값은
> 이 코퍼스로 못 낸다"로 **스코프 축소 종결**(판정#7·#8·#9-종결과 동일 유형) — `_f_gamma`의 사유(3)
> 하한을 "임계하중 비선형은 실재하나 이 계(diamond conditioner wear literature)에서 정량화할 1차 문헌이
> 없다"는 **영구 확정**으로 전환하고 격자는 estimated 그대로 둔다.

### 4.7 3회차 재탐색(2026-09-15) — **마지막 회차, 종결**

과제: (1) Wei 2010 UA 학위논문을 OpenAlex/UA 리포지토리/ProQuest/CORE/Semantic Scholar로 정확히 식별,
(2) 실패 시 값 A(마모 그릿 팁 반경)·값 B(IC1000 항복강도 직접값)를 겨냥한 신규 질의 최소 8건
(1·2회차 미시도 질의만), (3) 3회차 규칙에 따라 이번 회차에 종결.

**Wei 2010 UA 학위논문 — 이번 회차에 처음으로 식별·원문 확보 성공.** OpenAlex 저자 API로 University
of Arizona 소속 "Xiaomin Wei"(OpenAlex A5022255930)를 특정 — 2015년 논문
"Method for accelerated diamond fracture characterization in chemical mechanical planarization"
(§4.6에서 이미 폐쇄 확인된 그 doi:10.1016/j.mee.2015.09.006)의 공저자로 나타나 저자군이 일치함을
확인했다. 이 저자의 2010년 학위논문 W191125918 "Fundamental Characterization of Tribological,
Thermal, Fluid Dynamic and Wear Attributes of Consumables in Chemical Mechanical Planarization"
(Univ. of Arizona PhD, 지도교수 Philipossian 그룹, DOI 없음, UA Campus Repository handle
10150/195125)이 바로 2회차가 식별하지 못했던 "Wei 2010 UA"다. `repository.arizona.edu/handle/...`
랜딩 페이지는 이번 세션에도 DSpace 7 마이그레이션 안내 HTML만 반환했지만, DSpace 7 REST API
(`/server/api/core/items/{id}/bundles` → `bundles/{id}/bitstreams` → `bitstreams/{id}/content`)로
우회하자 원문 PDF(19 MB, 315쪽)를 확보했다(1·2회차가 시도한 landing-page/OAI 경로와 다른 API 경로).
papers/wei2010-ua-phd-thesis-tribological-thermal-wear-cmp-consumables.pdf로 저장.

원문을 전문 검색한 결과 **값 A·B 둘 다 부적격**임을 확인했다:
- 값 A(팁 반경): Ch.8 "Identifying and Positioning the Aggressive Diamonds"의 furrow 단면적 분석
  (Fig. 8.12)은 캡션에 "(Borucki et al. 2007)"로 명시돼 있어 **§4.5가 이미 확보·기각한 ECS Trans.
  2013(furrow 단면적만, E5)과 같은 원조 방법론·같은 인용 원본**임이 확인된다 — furrow 폭·깊이가
  분리 보고되지 않아(단면적만) 반경 역산이 여전히 불가능하다. Ch.9(diamond pullout/fracture,
  doi:10.1016/j.mee.2015.09.006 의 원 데이터)도 SEM은 탈락/파단 사진일 뿐 마모 팁 곡률 측정이 아니다.
- 값 B(항복강도): Table 8.1(Ch.8, p.250)이 "Ultimate Tensile Strength (MPa): Polycarbonate 66,
  Hard Polyurethane Pads 45–96"를 보고하지만 (i) **인장강도(UTS)이지 항복강도가 아니고**, (ii)
  "Hard Polyurethane Pads"는 "IC family by Dow Chemical or D100 family by Cabot Microelectronics"를
  묶은 범위값이라 IC1000 단독 수치가 아니며, (iii) 이 표 자체의 1차 출처가 본문에 인용되지 않는다
  (2차 인용 수준 미만). 값 B로 채택 불가.

**신규 발견 — Irene Li 2000 UCF PhD 학위논문, 대상계 정확히 일치했으나 미확보.**
"Chemical-mechanical wear mechanism in polyurethane polishing pad materials"(OpenAlex
W2804437860)는 초록부터 **IC1000/Suba IV 적층 패드**를 명시적으로 다뤄 이번 과제의 대상계와
정확히 일치하는 유일한 학위논문이다(Shore 경도·DMA·흡수시험은 언급되나 초록에 항복강도 언급 없음
— 본문 확인이 필요했다). OpenAlex는 `oa_status: green`, `stars.library.ucf.edu/rtd/1912`를
가리키지만 실제 랜딩 페이지는 "This document is currently not available"(임베고/비공개)를
반환한다. CORE API 검색도 같은 논문(core id 71373238)을 찾았으나 `downloadUrl`이 없다(CORE도
원문 미보유). ProQuest 공개 메타데이터·Semantic Scholar 경로는 API 429(요청과다)로 이번 회차엔
접근 불가. **미확보로 남긴다** — 4회차가 없으므로 재시도 대상에서 제외.

**신규 확보(부적격) — Hou et al. 2024, *Materials* 17(11) 2759(doi:10.3390/ma17112759, CC-BY).**
mdpi-res.com CDN 직링크(`d_attachment/materials/materials-17-02759/...`)로 원문 확보(landing
page는 403). NaHCO₃/NH₄HCO₃ 발포제를 첨가한 **자체 제작 발포 폴리우레탄 연마패드**의 압축강도
곡선(Fig. 7c/7d)을 보고하지만 (i) IC1000류 상용 패드가 아닌 임의 배합 시료이고, (ii) 수치가
본문 문장이 아니라 곡선 그림으로만 제시돼 페이지 인용 없이 추출할 수 없으며, (iii) "compressive
strength"라는 용어를 쓰되 항복점 정의가 본문에 없다 — 값 B 부적격. papers/hou2024-materials-
secondary-foaming-pu-polishing-pad.pdf로 저장(참고용, 값 B 근거로는 미채택).

**신규 질의 9건 (1·2회차 미시도, 전부 부적격/미확보)**:
1. OpenAlex `fulltext.search`="IC1000 yield point"(95건, 상위 8건 검토) → 경도·Von Mises·STI
   모델링 등 무관.
2. OpenAlex `fulltext.search`="polyurethane pad compressive yield strength microcellular"(49건)
   → 전부 신발 밑창·복합재 리뷰 등 CMP 무관 발포재 문헌.
3. OpenAlex `fulltext.search`="CMP pad material datasheet tensile yield Rohm Haas"(0건).
4. CORE `q`='"tip radius" "diamond conditioner" wear CMP' → 압입경도 리뷰 2편(무관)·다이아몬드
   터닝공구 마모(실리콘 가공, 계 상이)·Wei 2010 본인(위에서 이미 처리) 재등장, 신규 없음.
5. CORE `q`='IC1000 "yield strength" polyurethane pad' → Lu 2002 DMA(§4.6에서 이미 미확보 확인된
   그 논문, doi:10.1016/s1044-5803(03)00004-4) 재등장·나머지 무관 PU 발포재.
6. CORE `q`='polishing pad polyurethane "compressive yield"' → Zantye et al. 2004(MRS Proc. 816,
   K4.7, doi:10.1557/proc-816-k4.7, "Investigation of Mechanical Integrity … Novel Polyurethane
   Polishing Pad") 발견, OpenAlex `is_oa: false`·CORE 미보유로 **미확보**; Irene Li 2000·Hou 2024는
   위에서 별도 처리.
7. Semantic Scholar Graph API `paper/search`(worn diamond tip radius / diamond dresser wear flat
   radius) → 두 질의 모두 HTTP 429(rate limit), 이번 회차엔 API 키 없이 접근 불가.
8. CORE `q`="diamond disc conditioner used worn AFM tip radius CMP measurement" → 응답 파싱 실패
   (빈 본문), 재시도 없이 실패로 기록.
9. CORE `q`="CMP conditioner diamond apex radius characterization wear scanning electron
   microscopy" → 실리콘 다이아몬드터닝 공구마모·전자현미경 응용 리뷰 등, 팁 반경 수치 없음.

**결론(3회차·최종): 값 A·B 모두 미확보.** 처음으로 Wei 2010 UA를 식별·원문 확보했으나 §4.5가 이미
기각한 것과 **같은 furrow-단면적 방법론**(Borucki et al. 2007 원 데이터 재사용)과 **같은 종류의
UTS 대용값**만 담고 있어 판정을 바꾸지 못한다. 유일하게 대상계(IC1000/Suba IV)가 정확히 일치했던
신규 후보(Irene Li 2000)는 임베고로 접근 불가였고, 그 대체로 확보한 Hou 2024는 계 불일치(임의
발포배합)로 부적격이다. **3회차 규칙에 따라 이번 회차로 종결한다.**

> ⚠ **3회차 1차 출처 확보 실패(최종)**: Wei 2010 UA(원문 확보했으나 furrow-단면적·UTS 대용값만,
> 부적격)·Irene Li 2000 UCF(대상계 정확 일치했으나 임베고로 미확보)·Zantye 2004 MRS(폐쇄, 미확보)·
> Hou 2024 MDPI(원문 확보했으나 계 불일치로 부적격)·Semantic Scholar(rate limit) — **값 A(마모
> 그릿 팁 반경)·값 B(IC1000 항복강도 직접값) 어느 쪽도 3회차 누적 25편 이상의 확보/검토 문헌에서
> 나오지 않는다.**

**최종 판정 — 스코프 축소 영구 종결.** "R·Y 직접값은 이 코퍼스로 못 낸다." `_f_gamma` 사유(3)의
하한은 "미해소(재탐색 대상)"에서 **"스코프 축소 종결 — 후속 크론은 재탐색 금지, 4회차 없음"**으로
전환한다. Γ confidence 하한은 그대로 `estimated`이며, 이는 이제 **추가 조사로 해소될 하한이 아니라
확정된 값**이다(EVIDENCE-RULES §서두 3회차 규칙 — 판정#9-종결·#22의 동형). 코드·격자·Γ 값은 전부
불변.

## 5. 종합 — `_f_gamma` 반영
| 사유 | 판정 | 코드 반영 |
|---|---|---|
| (1) Rs 보정 | 해소(총량 스칼라 한정, 문헌 범위 내 스윕평균 <1%) | docstring "해소"로 갱신, notes 문구 수정 |
| (2) τ 앵커 | 조건부 — 기준조건 무관, \|A−1\|>0.01일 때만 하한 | `GAMMA_AGING_CONF_TOL`, 조건부 note |
| (3) 임계하중 | **스코프 축소 종결(3회차, §4.7)** — R·Y 직접값은 이 코퍼스로 못 낸다 | 무조건 `estimated` 하한 유지, 재탐색 금지 |

기준조건 Γ 등급: `estimated` **확정값**(하한이 아니다 — 3회차 규칙에 따른 영구 종결, §4.7). Γ **값**은
한 곳도 바뀌지 않는다(`tests/test_gamma_confidence_basis.py`가 5팩·t=0/20/50 h에서 고정). EVIDENCE-RULES 판정#22.

## 6. 미검증·한계
- (1)의 상계는 균일 압력·균일 그릿밀도 가정이다. 디스크 짐벌·에지 압력 집중은 미반영(분포 모듈 몫).
- 역회전(1−Rs>1) 레시피는 문헌에서 확인하지 못했다 — 나타나면 §2.3 (d)를 재계산.
- (3)의 R은 **1차 미확보로 영구 확정**(3회차까지, §4.5·§4.6·§4.7), Y는 H/3 환산(2차 인용), 패드는 평탄 반무한체 가정(애스퍼리티 위 접촉이면
  응력 집중으로 P_c가 더 작아지므로 이 가정은 보수적이다). 3M DOP는 기준면 정의라 "침투 깊이"로 읽는
  것은 해석이다.
- N_total의 정방격자 환산은 디스크 전면이 그릿으로 덮였다는 가정(edge exclusion 무시)이라 상한 쪽이다.
- **3회차로 종결(§4.7)** — Wei 2010 UA 학위논문을 이번 회차에 식별·원문 확보했으나 값 A·B 모두
  부적격이었고, 대상계가 정확히 일치하는 유일한 신규 후보(Irene Li 2000 UCF)는 임베고로 미확보였다.
  "R·Y 직접값은 이 코퍼스로 못 낸다"로 **스코프 축소 영구 종결** — 4회차 없음, 후속 크론은 재탐색 금지.
