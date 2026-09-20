# Cal-1 — 옥사이드 실데이터 스키마 + 보정 파라미터(Kp_oxide·선택비·디싱) 정의·식별가능성

> film-oxide Cal-1 (캘리브레이션 단원, ORG.md §7.3) | 작성일: 2026-09-19
> 선행(재서술 금지·인용만): [[film-oxide-kp-filmtype-scaling-teos-hdp-bpsg-psg]] (Lv3-2, 막질별 Kp 배율표 thermal=1 — 이 노트가 **보정할 대상**),
> [[../cmp/sti-cmp-ceria-high-selectivity-nitride-stop-dishing]] (Lv2-2, Lee 2002 디싱 폐형해·선택비 조건의존 — 디싱 계수의 물리 스켈레톤),
> [[film-oxide-teos-hdp-bpsg-sod-density-hardness]] (Lv1-1, 막종류 정의·도핑 화학),
> [[../cmp/ild-cmp-planarization-global-local-density]] (Lv2-1, blanket K가 패턴모델에 들어가는 자리),
> [[../cmp/preston-luo-dornfeld-mrr]] (K = Kp·P·V 정의),
> [[../cmp/wafer-metrology-customer-data-schema-metric-definition-mapping]] (형제 Cal-1 본보기 — 계측 스키마·WIWNU 정의 매핑은 여기서 완결, 재서술 금지),
> [[../params/oxide_silica.yaml]] · [[../params/sti_ceria.yaml]] (보정 대상 팩)

## 0. 목적·범위·형제 경계

ORG.md §7.3은 film-oxide에게 **"옥사이드 실데이터(막종류·MRR·WIWNU·디싱) 스키마 + 보정 파라미터
(Kp_oxide, 선택비) 정의"**를 맡겼다. 이 노트가 그 산출물이다. Lv3-2가 이미 **막질별 Kp 배율표**를
만들었으므로([[film-oxide-kp-filmtype-scaling-teos-hdp-bpsg-psg]] §5, thermal=1 기준 TEOS 1.35·BPSG 4.6),
이 단원은 그 표를 **재서술하지 않고**, 그 표가 **고객 데이터로 어떻게 보정되는가**와 **무엇이
데이터로 식별 가능한가**를 정의한다. 이것이 캘리브레이션 단원의 고유 문제다.

이 단원이 푸는 실제 문제: 소재사·팹이 옥사이드 MRR·WIWNU·디싱을 입력했을 때, **절대 Kp를 올리는
것과 막종류 배율을 올리는 것이 같은 MRR을 낸다** — 둘은 곱으로만 들어가므로(§2), 기준막 데이터가
없으면 분리되지 않는다(§4-A, 조건수 ∞·상관 −1.000). 이 식별가능성 조건을 명시하지 않으면
캘리브레이션이 "절대 Kp 편차"와 "막종류 편차"를 임의로 뒤섞어 오학습한다.

**형제 경계 (침범 금지, 인용만):**
- **나이트라이드·poly-Si 물성·억제 메커니즘**은 film-nitride·film-poly-si 소관. 이 노트는 선택비의
  **분자(oxide RR)** 축만 다루고, 분모(nitride/poly RR 절대값)는 인용만 한다.
- **세리아 입자 화학**(Ce³⁺·chemical tooth)은 slurry-abrasive·slurry-chemistry 소관 — 인용만.
- **GP/베이지안 잔차 피팅**은 cmp-calibrator 소관. 이 노트는 "무엇이 식별되고 무엇을 prior로
  고정하는가"까지만 정의하고, 잔차 학습 알고리즘은 넘긴다(ORG.md §7.3).
- **계측 좌표·WIWNU 정의 매핑·스키마 파일**은 wafer-metrology(정의)·cmp-data-engineer(파일) 소관.
  이 노트는 옥사이드 전용 필드의 **개정 제안(§5)만** 표로 적고 `wafer_measurement.schema.json`을 직접
  고치지 않는다 — 구현은 PROFILE.md 요청으로 넘긴다.
- **고객·재직사 데이터 절대 미사용**(ORG.md §7.5). 이 노트의 모든 수치는 공개 표준·문헌·**합성**이다.

## 1. 옥사이드 실데이터 레코드가 담아야 할 필드 — 각 필드를 "왜"로 근거

Lv3-2가 확정한 사실 하나가 필드 전체의 근거다: **막종류별 Kp는 (경도 항 + 도핑 화학 항)으로 갈리고,
그 배율이 슬러리 종류에까지 의존한다**([[film-oxide-kp-filmtype-scaling-teos-hdp-bpsg-psg]] §5·§6). 즉
레코드가 MRR 하나만 담으면 보정이 "그 팹 편차"와 "막종류 편차"를 구분하지 못한다. 아래 필드는 그
구분을 가능케 하는 최소 집합이며, **각 필드가 Kp 배율의 어느 변수에 대응하는지**를 근거로 단다.

| 필드 | 왜 필요한가 (Lv3-2 배율이 의존하는 변수) | 근거 |
|---|---|---|
| **film_type** (enum: thermal/PECVD_TEOS/O3_TEOS/HDP/BPSG/PSG/SOD/silane) | 배율 m_f의 **키**. thermal=1·TEOS 1.35·HDP 1.30·PSG 2.9·BPSG 4.6이 전부 이 키로 갈린다 | Lv3-2 §5 |
| **dopant_B_wt_pct·dopant_P_wt_pct** | 도핑막 배율은 경도가 아니라 **B·P wt%**의 함수(BPSG 1.4%B→3.0, 4.9%B→4.6; PSG 3.3%P→2.2, 5.6%P→2.9) — 도핑막이면 필수 | Liu 1995 Fig.2/3 (DOI: 10.1016/0040-6090(95)07088-5) |
| **anneal_reflow** (bool) | reflow는 도핑막을 경화(H↑)시켜 배율을 바꾼다(BPSG vs BPSG+reflow) | Wei 2010 §III.A (DOI: 10.1109/wmed.2010.5453755) |
| **initial_thickness_nm** | 제거량 = 초기−최종. MRR 역산의 분자 | Preston 정의 [[../cmp/preston-luo-dornfeld-mrr]] |
| **amount_removed_nm / mrr_nm_per_min** | Kp_ref 역산의 응답량. `measured_quantity` 축(post_thickness vs amount_removed)은 wafer-metrology 인용 | [[../cmp/wafer-metrology-customer-data-schema-metric-definition-mapping]] §3.3 |
| **pressure_kPa·velocity_m_per_s** | **Kp_ref = MRR/(P·V) 역산에 필수**. P·V가 없으면 절대 Kp가 아예 식별 안 됨(§2·§4) | Preston K=Kp·P·V |
| **wiwnu** (+ metric_definition·measured_quantity) | 반경 균일도. **정의 필드는 wafer-metrology 규칙 인용** — 여기서 재정의하지 않는다 | [[../cmp/wafer-metrology-customer-data-schema-metric-definition-mapping]] §2·§3 |
| **stop_layer** (enum: none/Si3N4/poly_Si) | 선택비 s의 **분모 종류**. STI(Si₃N₄)냐 poly-stop이냐로 s 정의가 갈린다 | Lv2-2 §3, Lv3-2 §9 |
| **selectivity_oxide_over_stop** | s의 응답값(블랭킷 또는 패턴). 옥사이드 막종류로 분자가 갈리면 s도 갈린다 | Lv3-2 §9 |
| **feature_width_um·pattern_density_rho** | 디싱 D_ss = d_max·ρ(s−1)/(1+ρ(s−1))의 **ρ**와, d_max를 정하는 구조물 폭. PTW 전용 | Lee 2002 식 2.32 (Lv2-2 §4.2) |
| **dishing_nm·erosion_nm·overpolish_time_s** | 디싱 계수(d_max,τ₂) 식별의 관측량. 시간축이 있어야 τ_nit 수렴이 보인다 | Lee 2002 식 2.54·2.56 (Lv2-2 §4.2) |
| **slurry_pack_id** (예 oxide_silica / sti_ceria) | 막질 배율표가 **슬러리별로 다르다** — 실리카 배율을 세리아에 이식 금지(§6). 어느 팩의 prior를 쓸지 결정 | Lv3-2 §6 (Mariscal 2020, DOI: 10.1149/2162-8777/ab89bc) |

핵심: `film_type`·`dopant_*`·`slurry_pack_id` 세 필드가 없으면 배율 축이 붕괴하고, `pressure`·`velocity`가
없으면 절대 Kp 축이 붕괴한다. 두 축이 다 살아 있어야 §2의 보정 파라미터가 식별된다.

## 2. 보정 파라미터 정의 — 무엇을 데이터로 피팅하고 무엇을 prior로 고정하는가

### 2.1 Kp_oxide 의 구조: 절대 스케일 × 막종류 배율

$$K_f = K_{p,\mathrm{ref}} \cdot m_f \cdot P \cdot V \qquad (m_{\text{thermal}}\equiv 1)$$

Kp_oxide를 **두 인자의 곱**으로 분해한다(Lv3-2 §5의 배율표를 그대로 인자화):
- **막종류 배율 $m_f$** — thermal=1 기준 상대비. Lv3-2에서 1차 실측 그래프 판독으로 확정(E3, 상대비는
  신뢰 산출물). **→ literature prior 로 고정한다.** 이유: 소량 고객 데이터로 배율을 재추정하면 절대
  스케일과 얽혀 식별되지 않는다(§4-A). 배율은 재료 물성(도핑 화학·수화 확산)이라 팹이 바뀌어도
  대체로 보존된다는 것이 Lv3-2의 논지다.
- **절대 스케일 $K_{p,\mathrm{ref}}$** (=thermal 또는 팩 앵커막의 절대 Kp) — 그 팹·그 슬러리 로트·그
  컨디셔닝 고유값. **→ 고객 데이터로 피팅한다.** 단 **식별 조건**(§2.4)이 붙는다.

이 분해는 ORG.md §7.1의 "물리 prior(배율) + 데이터 보정(절대 스케일)" 원리와, §7.3의 "막질별 Kp를
보정"을 코드가능한 형태로 옮긴 것이다. Lv3-2가 "절대 Kp 열 전체는 estimated"라 한 것과 정합한다 —
절대값은 데이터로 눌러야 할 자리이고, 배율만 문헌으로 고정한다.

### 2.2 선택비 — 옥사이드 관점의 분자 축만

$$s = \frac{\mathrm{MRR}_{\text{oxide}}}{\mathrm{MRR}_{\text{stop}}}, \qquad
\mathrm{MRR}_{\text{oxide}} = K_{p,\mathrm{ref}}\cdot m_f \cdot P\cdot V$$

Lv3-2 §9의 결론을 파라미터로: **선택비 변동은 분자(oxide 막종류)에서 온다.** 같은 세리아 슬러리라도
oxide가 HDP냐 PETEOS냐로 s가 갈린다(Lv3-2 §6). 따라서 s를 "슬러리 상수"로 고정하면 안 되고, 분자를
막종류 배율로 예측한 뒤 분모(stop RR)와 나눈다. **분모(nitride/poly 절대 RR·억제 메커니즘)는
film-nitride·film-poly-si 소관 — 인용만.** oxide:nitride 절대 선택비 수치(무첨가 4.4, 첨가제 175–290,
Mariscal 32–101)는 Lv2-2 §5에서 완결됐으므로 재서술하지 않고 §3 prior 표에만 중심값으로 옮긴다.

### 2.3 디싱 계수 — PTW 전용, Lee 2002 파라미터

디싱은 NPW(블랭킷)엔 존재하지 않는다(패턴이 없다). PTW에서 Lee 2002 폐형해의 3개 파라미터
(d_max, s, τ₂)로 정의된다(Lv2-2 §4.2, 재유도 금지):

$$D_{ss}(\rho) = d_{max}\cdot\frac{\rho(s-1)}{1+\rho(s-1)}, \qquad
\tau_{nit} = \frac{\tau_2}{1+(s-1)\rho}$$

여기서 s는 §2.2의 선택비, ρ는 유효 패턴밀도, d_max는 패드가 트렌치 옥사이드에 닿지 않게 되는 단차
(패드·기하 상수). 이것이 ORG.md §7.2의 "NPW→PTW 전이"에 정확히 대응한다 — 절대 Kp·배율은 NPW에서
식별하고, 디싱 계수는 PTW에서만 추가로 식별된다.

### 2.4 식별가능성 조건 요약 (이 단원의 핵심 산출)

| 파라미터 | 식별에 필요한 데이터 조합 | 없으면 |
|---|---|---|
| **절대 $K_{p,\mathrm{ref}}$** | **기준막(thermal 또는 팩 앵커막) 1종의 (MRR,P,V)** | 배율과 곱으로 얽혀 비식별(조건수 ∞, 상관 −1.000, §4-A/B) → 팩 앵커를 prior로 고정 |
| **막종류 배율 $m_f$** (재추정 시) | 같은 (P,V)에서 **기준막 + 대상막** 동시 측정 | 절대 스케일과 분리 불가 → 기본은 재추정 안 하고 문헌 prior 고정 |
| **선택비 $s$** | oxide·stop을 **같은 P·V**에서 측정 | P·V 불일치 시 Preston 미상쇄로 편향(§4-D, 배수 = P₁V₁/P₂V₂) |
| **디싱 (d_max, s)** | **밀도 ρ 2점 이상** + 오버폴리시 시간축(PTW) | ρ 1점이면 (d_max,s) 곡선 위 무한해 → 비식별(§4-D) |

## 3. 문헌 prior 값·범위 — 1차 문헌에서 중심·폭

prior의 **폭(로그정규 σ)** 규약은 `sim/calibration/prior.py` docstring을 인용한다: literature 등급은
"같은 재료계 문헌 간 $k^*=\mathrm{MRR}/(P\cdot\text{rpm})$ 정상 산포 ≈ 1.5배"를 1-시그마 로그폭으로
쓴다 → $\sigma_{\log}=\ln 1.5 \approx 0.405$. 절대 스케일·배율 모두 로그정규로 둔다(Kp는 양수·곱셈적).

| 파라미터 | prior 중심 | $\sigma_{\log}$ | 1차 근거(실존 확인) | 등급 |
|---|---|---|---|---|
| $m_{\text{TEOS}}$ | 1.35 | 0.405 | Liu 1995 USG≈TEOS 정규화 (DOI: 10.1016/0040-6090(95)07088-5) | E3 |
| $m_{\text{HDP}}$ | 1.30 | 0.405 | Wei 2010 HDP/TEOS=0.964×1.35 (DOI: 10.1109/wmed.2010.5453755) | E3 |
| $m_{\text{O3-TEOS}}$ | 1.50 | 0.405 | Wei 2010 O₃-TEOS/TEOS=1.108×1.35 | E3 |
| $m_{\text{PSG(5.6\%P)}}$ | 2.9 | 0.405 | Liu 1995 Fig.2 | E3 |
| $m_{\text{BPSG(4.9\%B)}}$ | 4.6 | 0.405 | Liu 1995 Fig.3 | E3 |
| $K_{p,\mathrm{ref}}$ (thermal, 실리카) | 0.74e-13 m²/N | ln(2)≈0.69 (절대값 estimated → 넓게) | Lv3-2 §5 (TEOS 앵커 1.0e-13 ÷ 1.35) | E4 |
| $s$ (세리아, 무첨가) | 4.4 | 큼(공정의존) | Dandu 2009 (DOI: 10.1149/1.3230624) | E2 |
| $s$ (세리아 + 억제제) | ~57 (√(32·101)) | 큼(0.3–1.0 dex) | Mariscal 2020 32–101 (DOI: 10.1149/2162-8777/ab89bc) | E2 |

**주의(Lv2-2 §5·Lv3-2 §5 인용):** 선택비 s는 상수가 아니라 P·V·패턴의 함수라 폭이 매우 넓다
(실리카 2.7–38, 세리아 32–101). prior 중심은 참고값일 뿐이고, s는 **특성화 마스크에서 추출하는
공정 파라미터**로 취급해야 한다(Lv2-2 §9-3). 절대 스케일 Kp_ref의 σ를 배율(0.405)보다 넓게(ln2) 둔
것은 Lv3-2가 절대 열을 estimated로 남긴 것과 정합한다.

## 4. Python 검증 — 식별가능성 실험 (```python verify```, 실제 실행)

**재현 요약(한 줄)**: Preston MRR=Kp·P·V 합성데이터(thermal=1·TEOS 1.35·HDP 1.30 배율, Lv3-2 §5)로
(A) 기준막 없으면 절대 Kp와 배율이 곱으로 얽혀 정규행렬 조건수 ∞·구성적 shift 불변, 기준막 앵커를
넣으면 full-rank로 진값 복원, (B) 두 파라미터 사후 상관이 −1.000→약함, (C) 문헌 배율 prior σ_log=0.405·
TEOS 95%CI[0.61,2.99]·단조순서, (D) 선택비는 P·V 불일치 시 P₁V₁/P₂V₂ 배 편향·디싱은 ρ 1점 비식별/
2점 복원 — 아래 4블록 assert PASS.

```python verify
import numpy as np
# ═══ [A] 절대 Kp vs 막종류 배율 동시 식별 — 기준막(thermal) 앵커 유무 ═══
# 합성: Preston MRR = Kp_th·m_f·P·V·(1+노이즈). 관측 y = log(MRR/(P·V)) = logKp_th + log m_f.
rng = np.random.default_rng(0)
Kp_th = 0.74e-13                                  # thermal 절대 Kp (Lv3-2 §5 제안 앵커)
m = {"thermal":1.00, "TEOS":1.35, "HDP":1.30}     # thermal=1 기준 배율 (Lv3-2 §5)
P, V = 20.7e3, 0.8                                 # Pa, m/s (oxide_silica 팩 캘리브레이션점)
def synth(films, n_each=25, noise=0.02):
    rows=[]
    for f in films:
        for _ in range(n_each):
            mrr = Kp_th*m[f]*P*V*(1+rng.normal(0,noise))
            rows.append((f, np.log(mrr/(P*V))))
    return rows
def design(rows, params):        # params: δ를 추정할 막(thermal은 δ=0 고정)
    X=[[1.0]+[1.0 if f==p else 0.0 for p in params] for f,_ in rows]
    y=[yy for _,yy in rows]
    return np.array(X), np.array(y)

# A1 기준막 없음: TEOS,HDP만 → 절대Kp와 배율이 얽힘
X1,y1 = design(synth(["TEOS","HDP"]), ["TEOS","HDP"])   # 파라미터 [b0, δTEOS, δHDP]
cond1 = np.linalg.cond(X1.T@X1)
beta0 = np.array([np.log(Kp_th), np.log(m["TEOS"]), np.log(m["HDP"])])
c=0.7; beta_shift = beta0+np.array([c,-c,-c])           # 구성적 비식별: 절대 올리고 배율 내려 상쇄
r0 = y1-X1@beta0; rs = y1-X1@beta_shift
assert cond1 > 1e12                                     # 정규행렬 특이 (열 c0 = c_TEOS + c_HDP)
assert np.allclose(r0, rs)                              # 두 파라미터가 동일 예측 → 분리 불가

# A2 기준막(thermal) 앵커 포함 → full rank, 진값 복원
X2,y2 = design(synth(["thermal","TEOS","HDP"]), ["TEOS","HDP"])
beta_hat = np.linalg.lstsq(X2,y2,rcond=None)[0]
cond2 = np.linalg.cond(X2.T@X2)
assert cond2 < 1e3
assert abs(beta_hat[0]-np.log(Kp_th)) < 0.03
assert abs(np.exp(beta_hat[1])-1.35) < 0.06 and abs(np.exp(beta_hat[2])-1.30) < 0.06
print(f"[A] 기준막없음 cond={cond1:.1e}·shift잔차동일={np.allclose(r0,rs)}; "
      f"기준막있음 cond={cond2:.1f}·Kp_th복원 {np.exp(beta_hat[0])*1e13:.2f}e-13·"
      f"mTEOS {np.exp(beta_hat[1]):.2f}·mHDP {np.exp(beta_hat[2]):.2f}")

# ═══ [B] 조건수·상관계수로 식별불가를 정량 ═══
lam=1e-9                                                # 미세 ridge로 특이행렬 역행렬화
def corr01(X):
    Sig=np.linalg.inv(X.T@X+lam*np.eye(X.shape[1]))
    return Sig[0,1]/np.sqrt(Sig[0,0]*Sig[1,1])
r1=corr01(X1); r2=corr01(X2)
assert r1 < -0.999          # 절대Kp와 배율이 완전 음의 상관 = 하나 올리면 다른 하나 내려 상쇄
assert abs(r2) < 0.8        # 기준막 앵커가 상관을 깬다
print(f"[B] 상관 r(logKp,δTEOS): 기준막없음={r1:.4f} 기준막있음={r2:.4f}")
```

```python verify
import numpy as np
# ═══ [C] 문헌 prior 중심·로그정규 σ (prior.py literature 규약) ═══
center={"thermal":1.00,"TEOS":1.35,"HDP":1.30,"O3-TEOS":1.50,"PSG_5.6":2.9,"BPSG_4.9":4.6}  # Lv3-2 §5
sig_log=np.log(1.5)                              # prior.py: 문헌간 k* 산포 ~1.5배 = 1σ 로그폭
assert abs(sig_log-0.405) < 0.005
lo=center["TEOS"]*np.exp(-1.96*sig_log); hi=center["TEOS"]*np.exp(1.96*sig_log)
assert abs(lo-0.61)<0.02 and abs(hi-2.99)<0.03   # TEOS 배율 95% prior 구간
# 배율 단조성 — 도핑막 > 미도핑막 > thermal (Lv3-2 물리: 도핑 화학 지배)
assert center["BPSG_4.9"]>center["PSG_5.6"]>center["O3-TEOS"]>center["TEOS"]>center["thermal"]
# 선택비 prior 로그중심: Dandu 무첨가 4.4, Mariscal 32-101 (Lv2-2 §5, 재서술 아님·중심만)
assert abs(350/80-4.375)<1e-9
sel_center=np.sqrt(32*101); assert 56<sel_center<57
# 절대 스케일은 배율보다 넓게 (Lv3-2: 절대 열 estimated)
sig_abs=np.log(2.0); assert sig_abs>sig_log
print(f"[C] σ_log(배율)={sig_log:.3f}·TEOS 95%CI[{lo:.2f},{hi:.2f}]; "
      f"선택비 로그중심 {sel_center:.1f}(32-101); σ_abs {sig_abs:.3f}>σ_log")
```

```python verify
import numpy as np
from scipy.optimize import fsolve
# ═══ [D] 선택비·디싱 파라미터 식별조건 ═══
# (D1) 선택비: oxide·stop을 다른 P·V로 재면 Preston 상쇄 안 돼 편향 (같은 P·V 매칭 필수)
s_true=175.0                                     # Dandu 피리딘 (350/2)
Kox,Kni=350.0,2.0
P1,V1,P2,V2=20.7e3,0.8,13.8e3,0.6
s_matched=Kox/Kni
s_mis=Kox/(Kni*(P2*V2)/(P1*V1))                  # nitride를 낮은 P·V에서 재면 RR 과소→s 과대
assert abs(s_matched-s_true)<1e-6
assert abs(s_mis/s_matched-(P1*V1)/(P2*V2))<1e-6 and s_mis>s_true
# (D2) 디싱: Lee D_ss(ρ)=d_max·ρ(s-1)/(1+ρ(s-1)); 미지 (d_max,s)
def Dss(rho,dmax,s): return dmax*rho*(s-1)/(1+rho*(s-1))
dmax_t,s_t=400.0,10.0                            # Lv2-2 §8[A] 재현치
r_a,r_b=0.3,0.7
Da,Db=Dss(r_a,dmax_t,s_t),Dss(r_b,dmax_t,s_t)
sol=fsolve(lambda x:[Dss(r_a,*x)-Da, Dss(r_b,*x)-Db],[300,5])   # ρ 2점 → 유일 복원
assert abs(sol[0]-400)<1 and abs(sol[1]-10)<0.1
s_alt=fsolve(lambda s:Dss(r_a,600,s)-Da,3)[0]    # ρ 1점: d_max=600에서 다른 s가 같은 D_ss
assert abs(Dss(r_a,600,s_alt)-Da)<1e-6 and abs(s_alt-s_t)>1   # 비식별: 무한해
print(f"[D1] 선택비 매칭 s={s_matched:.0f}·불일치 s={s_mis:.0f}(편향 {s_mis/s_matched:.2f}배=P1V1/P2V2)")
print(f"[D2] 디싱 ρ2점 복원 d_max={sol[0]:.0f}·s={sol[1]:.2f}; ρ1점 다른해(d_max=600,s={s_alt:.2f}) 동일 D_ss={Da:.1f}")
```

**결과 해석(정직하게)**
- [A][B]는 **합성데이터에 대한 이 노트의 직접 계산**이지 문헌 재현이 아니다(정직성 표지). 배율·앵커
  Kp 값만 Lv3-2 문헌 판독값이다. 조건수 ∞는 정규행렬이 수학적으로 특이하기 때문이고, 실측 노이즈가
  있어도 rank는 회복되지 않는다 — 기준막 데이터라는 **구조적 정보**가 있어야만 분리된다.
- [C]는 prior.py의 σ_log 규약(literature=ln1.5)을 옥사이드 배율에 적용한 것이다. σ_log 자체는 이
  프로젝트의 운영 규약이지 옥사이드 전용 문헌값이 아니다(prior.py docstring이 "미검증 운영 규약"으로
  명시) — **미검증 규약을 그대로 계승**하고 옥사이드 중심값만 Lv3-2 문헌에서 가져왔다.
- [D1]의 P·V 불일치 편향은 Preston 선형성의 직접 귀결이다. [D2]의 디싱 비식별은 Lee 식의 (d_max,s)
  2미지·1방정식 구조에서 온다 — ρ 2점이 있어야 식별된다는 Lv2-2 §4.2 논지의 정량 확인이다.

## 5. `wafer_measurement.schema.json` 옥사이드 전용 필드 개정 제안 (cmp-data-engineer 인계 — 파일 직접수정 금지)

현행 스키마([[../cmp/wafer-metrology-customer-data-schema-metric-definition-mapping]] §5가 계측·정의
필드를 제안)는 좌표·단위·WIWNU 정의를 잡지만 **막종류·증착조건·선택비·디싱** 축이 없어 옥사이드
Kp 보정을 못 한다. 아래는 **제안**이며 구현은 cmp-data-engineer가 판단한다(§1·§2 근거).

| 필드(제안) | 위치 | 타입/enum | 필수성 | 근거 | 효과 |
|---|---|---|---|---|---|
| `film_type` | record | enum: thermal/PECVD_TEOS/O3_TEOS/HDP/BPSG/PSG/SOD/silane | 필수 | §1, Lv3-2 §5 | 배율 m_f 키 — 없으면 배율 축 붕괴 |
| `dopant_B_wt_pct`·`dopant_P_wt_pct` | record | number\|null | 도핑막이면 필수 | §1, Liu 1995 | 도핑막 배율 = B·P wt% 함수 |
| `anneal_reflow` | record | bool | 권고 | §1, Wei 2010 | reflow 경화로 배율 변화 |
| `initial_thickness_nm` | record | number | 필수 | §1 | 제거량 분자 |
| `pressure_kPa`·`velocity_m_per_s` | record | number | **필수** | §2.4 | Kp_ref=MRR/(P·V) 식별 — 없으면 절대 Kp 비식별 |
| `slurry_pack_id` | record | string(oxide_silica/sti_ceria) | 필수 | §6, Lv3-2 §6 | 실리카/세리아 배율표 분기 |
| `stop_layer` | record | enum: none/Si3N4/poly_Si | STI·poly면 필수 | §2.2 | 선택비 분모 종류 |
| `selectivity_oxide_over_stop` | record | number\|null | 선택비 보고 시 | §2.2 | s 응답값(분자=막종류 의존) |
| `feature_width_um`·`pattern_density_rho` | record/die | number | 디싱 보고 시 필수 | §2.3, Lee 2002 | d_max·ρ — 디싱 계수 식별 입력 |
| `dishing_nm`·`erosion_nm`·`overpolish_time_s` | point/record | number\|null | PTW 디싱 시 | §2.3·§2.4 | (d_max,τ₂) 식별 — ρ 2점+시간축 요구 |
| `is_reference_film` | record | bool | 권고 | §2.4 [A] | thermal 앵커 표식 — 절대 Kp 식별 게이트 |

**주의**: `film_type=thermal`(또는 팩 앵커막)의 (MRR,P,V)가 데이터셋에 **하나라도 있어야** 절대 Kp가
식별된다(§4-A). 없으면 ingest 단계에서 "절대 Kp 비식별 — 팩 앵커 prior로 고정" 플래그를 띄우고
배율만 보정하도록 cmp-calibrator에 넘겨야 한다. `is_reference_film` 필드가 그 게이트다.

## 6. 남은 미확보·미검증 (정직성 표기)

- **막종류 배율의 슬러리 전이 가정은 근사**다: Lv3-2 §6이 이미 보였듯 실리카 배율(HDP≈TEOS)은
  세리아에 이식 금지(세리아는 HDP≪PETEOS). 세리아 전용 막질 배율은 **정량 데이터 부재로 미확보** —
  `sti_ceria` 팩 보정은 배율 prior 없이 절대 Kp만 데이터로 눌러야 한다(§3에 세리아 배율 행 없음).
- **σ_log 규약(ln1.5)은 미검증 운영 규약**이다(prior.py docstring 자백). 옥사이드 배율의 실제 문헌 간
  산포를 독립 측정하지 못했다 — Wei·Liu 두 논문의 슬러리가 달라(colloidal 3psi vs fumed/KOH 7psi)
  배율 σ를 교차 추정할 수 없었다(Lv3-2 §5 ⚠). 1.5배는 계승값이다.
- **절대 Kp_ref prior 중심(0.74e-13)은 E4**(교차논문 다리 TEOS≈USG). §4-A의 진값도 이 값을 썼으므로
  식별가능성 논증은 절대값 정확성과 무관하다(구조적 결론) — 하지만 prior 중심으로서는 estimated다.
- **선택비·디싱 파라미터의 실제 고객 식별은 미시연**이다. §4는 합성데이터로 식별가능성 **조건**만
  보였다. 실제 GP 잔차 학습·불확실성은 cmp-calibrator 소관이고 여기서 다루지 않는다.
- Lee 2002 학위논문(hdl 1721.1/29907)은 DOI가 아니라 handle — Crossref 조회 대상 아님(Lv2-2에서 원문
  PDF 확보·완독). 디싱 식(§2.3)은 그 노트에서 완결된 것을 인용만 한다.

## 7. 옥사이드 관점 결론

1. **Kp_oxide = 절대 스케일 × 막종류 배율**로 분해하고, 배율은 literature prior 고정·절대 스케일은
   고객 데이터로 피팅한다(§2.1). 이것이 Lv3-2 배율표를 캘리브레이션에 연결하는 방식이다.
2. **절대 Kp는 기준막(thermal) 데이터가 있어야 식별된다** — 없으면 배율과 곱으로 얽혀 조건수 ∞·상관
   −1.000(§4-A/B). 기준막이 없으면 팩 앵커를 prior로 고정하고 배율만 보정한다.
3. **선택비는 옥사이드 막종류(분자)로 갈리고 같은 P·V에서 재야 식별**된다(§2.2·§4-D1). 분모는 형제
   에이전트 소관.
4. **디싱 계수는 PTW·밀도 2점 이상에서만 식별**된다(§2.3·§4-D2) — NPW→PTW 전이(ORG §7.2)에 대응.
5. 스키마엔 `film_type`·`dopant_*`·`pressure`·`velocity`·`slurry_pack_id`·`is_reference_film`이 추가돼야
   보정 파라미터가 식별된다(§5).

## 8. 구현 요청 → agents/film-oxide/PROFILE.md "## 구현 요청" 참조
(Kp_oxide 분해 인자화 + 절대 Kp 식별 게이트(is_reference_film) + 디싱 계수 PTW 식별. §2·§4·§5.)

## 9. 자기시험
→ [[../../agents/film-oxide/EXAMS.md]] Cal-1 문항 참조.
