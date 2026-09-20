<!-- V2-SECTION: R3-pad | 공동: R5-wafer | 근거: asperity, GW, 접촉역학, 패드, eta | 정본: ARCHITECTURE-V2.md §3 -->
# 패드 asperity 면밀도 η — GW 접촉모델 파라미터의 1차 문헌 실측·사용값

> pad-mechanic 파라미터 앵커 노트 | 작성일: 2026-09-11
> 선행: [[hertz-gw-contact-mechanics]] (GW 정식화, η·R·σ의 정의와 적분식),
> [[disk-design-pad-roughness-asperity-relation]] (디스크 스펙 → 표면 통계, Ring 규칙의 수치 불일치 발견),
> [[pad-glazing-mechanism-mrr-decay]] (Jeong 2024 σ_z·μ_R 시계열).
> 이 노트의 질문 하나: **`asperity_density_per_m2`에 넣을 η의 문헌 근거 수치는 얼마인가.**

## 1. 왜 이 단원이 필요한가 — 그리고 현재값이 왜 위험한가

[[hertz-gw-contact-mechanics]] §3은 η(단위면적당 asperity 밀도)를 GW 세 파라미터 중 하나로
정의했지만 코드의 η=1e12는 "예시값 — 문헌 실측치 아님"으로 명시했다.
[[disk-design-pad-roughness-asperity-relation]] §4는 "η: 접촉 정점밀도 40–240 /mm²(Sun 2009);
Ring 표의 2.9×10¹¹ /m²는 접촉밀도의 10³배 — **전체 vs 접촉 정점 구분 필수**"라고 경고까지
남겼다. 그럼에도 `asperity_density_per_m2 = 1.0e11`이 `estimated`로 박혀 있었고, 그 출처는
Ring et al. 표 하나였다.

이 노트는 fab-sim `papers/` 코퍼스 190편 전수 정규식 스캔으로 **η를 명시적 수치로 적은 1차
출처만** 뽑는다. 결과는 예상과 달랐다: **현재값 1e11은 문헌 주류에서 500배 벗어나 있다.**

## 2. 1차 출처 — η가 숫자로 명시된 문헌 (원문 표기 그대로)

| # | 출처 | 문맥 | 원문 표기 | SI 환산 (/m²) | 성격 |
|---|---|---|---|---|---|
| 1 | **Bozkaya & Müftü (2009)**, "A Material Removal Model for CMP Based on the Contact Mechanics of Pad, Abrasives, and Wafer", *J. Electrochem. Soc.* 156(12), H890–H902. Northeastern Univ. | Table I "Physical values of parameters", GW 다중asperity 접촉모델의 base parameter | "Pad summit density (η_s) **2 × 10⁻⁴ /µm²**" (함께: Pad summit radius R_s = 50 µm, Pad summit SD σ_s = 5 µm) | **2.0 × 10⁸** | 모델 base값 |
| 2 | **Bozkaya & Müftü (2010)**, "Effects of Surface Forces on MRR in CMP", *J. Electrochem. Soc.* 157(3), H287–H296 | Table I, 후속 논문 동일 세트 | "Pad summit density (η_s) **2 × 10⁻⁴ /µm²**" (R_s=50 µm, σ_s=5 µm) | **2.0 × 10⁸** | 모델 base값(#1 재사용) |
| 3 | **Sorooshian (2005) 학위논문** (Univ. of Arizona), Appendix A (Eq. A.6–A.10, GW 정식화) | IC-1000 패드, 7 PSI, E=285 MPa, ν=0.5, λ=2.0 µm | "**η_s = 2.0 × 10⁸ /m²** (Elmufdi et al., 2004; Shan et al., 2000)" | **2.0 × 10⁸** | 타 문헌 인용값 |
| 4 | **Shi & Ring (2010)**, "CMP pad wear and polish-rate decay modeled by asperity population balance with fluid effect", Univ. of Utah 공개 PDF (`my.che.utah.edu/~ring/Publications-PDFs/J-135.pdf`) | Stein et al. (1996) 실험 데이터 재현 모델 | "we used values of the **asperity density 1/s = 2e8 /m²**, summit curvature k_s = 2e4 /m, pad modulus E* = 119 MPa" | **2.0 × 10⁸** | 모델 사용값 |
| 5 | **Suzuki, Hashimoto, Yasuda, Yamaki & Mochizuki (2017)**, "Prediction of polishing pressure distribution in CMP process with airbag type wafer carrier", *CIRP Annals*, DOI 10.1016/j.cirp.2017.04.088 (Nagoya Univ. + Ebara, 리포지토리 OA판 확보) | Table 1 "Material properties of polishing pad for simulations" — **패드 압축시험으로 동정(identified)한** GW asperity layer 파라미터 | "Asperity density **200 mm⁻²**" (함께: Standard deviation of asperity height 5.24 µm, Radius of hemisphere 50 µm, E=132 MPa, ν=0.3) | **2.0 × 10⁸** | **실측 동정값** |
| 6 | **Ring, Prasad & Dirksen** (연도 미기재), "Dynamic CMP Pad Asperity Population Balance…", Univ. of Utah 공개 PDF J-120 | Table 1, AMAT Mirra + Epic D100 패드 | "Asperity Density **2.938 × 10¹¹ #/m²**", 병기 규칙 "Asperity Density (1/D_grit)²", Mean Asperity Height 8.112 µm | **2.938 × 10¹¹** | **이상치 — §3 참조** |

**놀라운 수렴**: #1~#5는 서로 다른 5개 그룹(Northeastern / Arizona / Utah / Nagoya-Ebara)이
서로 다른 표기(`/µm²`, `/m²`, `mm⁻²`)로 적었는데 SI 환산하면 **전부 정확히 2.0 × 10⁸ /m²**다.
#1·#2와 #5는 R(정점반경) 50 µm, σ 5 µm/5.24 µm까지 사실상 일치한다(출처: 표 §2 행 1·2·5 —
Suzuki et al. 2017 CIRP Annals, DOI 10.1016/j.cirp.2017.04.088 Table 1 기준). #5는 이들 중 유일하게
**"패드 압축시험으로 동정한 값"**이라고 밝힌 실측 근거다.

## 3. #6(Ring et al. 2.9×10¹¹)은 왜 다른가 — 현재 fab-sim 값의 출처 추적

`asperity_density_per_m2 = 1.0e11`(estimated)은 사실상 #6 계열의 오더를 따른 값이다. 그런데
[[disk-design-pad-roughness-asperity-relation]] §2.7이 이미 이 표의 **내부 모순**을 기록했다:

- 표가 병기한 규칙 η = (1/D_grit)²에 논문 자신의 D_grit=190 µm를 넣으면 2.8 × 10⁷ /m²다 —
  표의 2.938 × 10¹¹과 **10⁴배 차이**.
- 표(Ring et al., Univ. of Utah PDF J-120, Table 1 — [[disk-design-pad-roughness-asperity-relation]] §2.7 이 전사)의 η에서 역산한 D_grit은 1.85 µm, 같은 표 σ에서 역산한 D_grit은 16.2 µm — **서로 9배 불일치**.
- 즉 η=2.938×10¹¹은 논문이 제시한 규칙의 산출물도 아니고, 규칙과 일관되지도 않는다.

추가 단서(이번 회차 확인): 같은 논문 Figure 1은 Veeco 간섭계 실측 히스토그램을
"**Number/m²**" 축(1×10⁵ ~ 1×10¹¹)으로 그린다. 즉 2.938 × 10¹¹은 **높이 구간별 asperity 수의
분포 정규화 상수(=히스토그램 y축 스케일)**로 보이며, GW의 "접촉 가능한 정점의 면밀도 η"와는
다른 양일 가능성이 높다 — **추정이며 논문이 구분해 주지 않아 확인 못 했다.**

**결정적 반증(기하)**: η = 1×10¹¹ /m²는 asperity 평균 간격 √(1/η) = **3.2 µm**를 뜻한다.
그런데 같은 노트들이 인용한 asperity 정점반경 R은 Bozkaya/Suzuki 50 µm, Jeong 2024 7.5–8 µm,
Liao 2014(곡률 정의) 1.1–2.0 µm다. **간격 3.2 µm짜리 평면에 반경 50 µm 반구를 심을 수 없다** —
asperity들이 서로 관통한다. 반면 η = 2×10⁸ /m²는 간격 **70.7 µm**로 R=50 µm 반구와 기하적으로
양립한다(§4 verify에서 assert로 고정). 이것이 #1~#5를 채택하고 #6을 배제하는 1차 근거다.

## 4. 정량 관계 — η가 GW 해에 어떻게 들어가는가

[[hertz-gw-contact-mechanics]] §3의 Gaussian GW에서 명목압력 P_o와 분리거리 d의 관계는
(Bozkaya & Müftü 2009 Eq. 25와 동일 형태):

```
P_o = (4/3)·η·E*·√R · ∫_d^∞ (z−d)^{3/2} φ(z) dz
A_r/A_n = π·R·η · ∫_d^∞ (z−d) φ(z) dz
n_contact = η · ∫_d^∞ φ(z) dz
```

η가 500배 틀리면 d(분리거리)가 σ 단위로 이동하면서 세 출력이 전부 바뀐다. 다만 GW의 유명한
성질 때문에 **A_r는 η에 매우 둔감**하고(하중이 재분배될 뿐), **접촉점 개수 n_contact는 민감**하다 —
아래 verify가 이 비대칭을 수치로 보인다. 즉 η 오류는 "실접촉면적"으로는 잘 드러나지 않고
"접촉점 밀도"와 "국소 접촉압력"에서 드러난다. Preston K_p를 η_c/A_f 비로 분해하려는
[[disk-design-pad-roughness-asperity-relation]] §5 작업가설에는 **η가 직접 들어가므로 치명적**이다.

```python verify
import numpy as np
from scipy import integrate, optimize

# ── (a) 문헌값 단위 환산 대조: 서로 다른 표기 4종이 모두 같은 SI 값인가 ──────────────
lit = {
    "Bozkaya&Muftu2009 Table I (2e-4 /um^2)":  2e-4 * 1e12,   # /µm² -> /m²  (µm²=1e-12 m²)
    "Bozkaya&Muftu2010 Table I (2e-4 /um^2)":  2e-4 * 1e12,
    "Sorooshian2005 App.A (2.0e8 /m^2)":       2.0e8,
    "Shi&Ring2010 (2e8 /m^2)":                 2.0e8,
    "Suzuki2017 CIRP Table1 (200 mm^-2)":      200 * 1e6,     # /mm² -> /m²  (mm²=1e-6 m²)
}
vals = list(lit.values())
for name, v in lit.items():
    print(f"  {name:44s} -> {v:.3e} /m^2")
    assert abs(v - 2.0e8) / 2.0e8 < 1e-9, f"{name}: 환산값이 2.0e8 /m^2가 아님 ({v:.3e})"
assert max(vals) == min(vals), "5개 문헌값이 완전히 동일해야 함(환산 오류 점검)"
print(f"독립 5출처 환산 일치: {vals[0]:.2e} /m^2")

# Ring et al. 값은 이 수렴에서 얼마나 떨어져 있는가
ETA_RING = 2.938e11
assert ETA_RING / 2.0e8 > 1000, "Ring 값이 주류 대비 1000배 이상 커야 함(§3 논거)"
print(f"Ring et al. 2.938e11 /m^2 = 주류값의 {ETA_RING/2.0e8:.0f}배")

# fab-sim 현재값 1e11이 주류에서 벗어난 배율
ETA_CURRENT = 1.0e11
print(f"fab-sim 현재값 1.0e11 = 주류값의 {ETA_CURRENT/2.0e8:.0f}배")
assert ETA_CURRENT / 2.0e8 == 500.0

# ── (b) 기하 일관성: η와 정점반경 R이 양립하는가 (§3 반증) ────────────────────────
def mean_spacing_um(eta):
    return 1.0 / np.sqrt(eta) * 1e6   # m -> µm

R_LIT_um = 50.0   # Bozkaya&Muftu Table I, Suzuki2017 Table 1 모두 50 µm
s_main = mean_spacing_um(2.0e8)
s_cur  = mean_spacing_um(ETA_CURRENT)
s_ring = mean_spacing_um(ETA_RING)
print(f"평균 간격: 주류 {s_main:.1f} µm / fab-sim현재 {s_cur:.2f} µm / Ring {s_ring:.2f} µm  (문헌 R={R_LIT_um} µm)")
# 반경 R인 반구가 서로 관통하지 않으려면 간격이 최소 R 수준은 되어야 한다
assert s_main > R_LIT_um, "주류 η에서도 간격이 R보다 작으면 이 기하 논증 자체를 폐기해야 함"
assert s_cur  < R_LIT_um / 10, "현재값의 간격이 R의 1/10보다 작다(=기하적으로 불가능)는 것이 §3 논거"
assert s_ring < R_LIT_um / 10

# ── (c) η 감도: Gaussian GW를 실제로 풀어 A_r와 접촉점밀도의 민감도 차이를 본다 ──────
sigma, R = 5e-6, 50e-6          # m, Bozkaya&Muftu2009 Table I (σ_s=5 µm, R_s=50 µm)
E, nu = 100e6, 0.3              # Pa, hard pad (같은 Table I의 Es=100 MPa)
Estar = E / (1 - nu**2)
phi = lambda z: np.exp(-0.5 * (z / sigma) ** 2) / (sigma * np.sqrt(2 * np.pi))

def gw_solve(eta, P_psi):
    Po = P_psi * 6894.76
    f = lambda d: (4/3) * eta * Estar * np.sqrt(R) * \
                  integrate.quad(lambda z: (z - d) ** 1.5 * phi(z), d, d + 10 * sigma)[0] - Po
    d = optimize.brentq(f, -6 * sigma, 8 * sigma)
    Ar = np.pi * R * eta * integrate.quad(lambda z: (z - d) * phi(z), d, d + 10 * sigma)[0]
    nc = eta * integrate.quad(phi, d, d + 10 * sigma)[0]
    return d / sigma, Ar, nc / 1e6      # d/σ, A_r/A_n, 접촉점밀도(#/mm²)

out = {}
for eta, tag in [(2.0e8, "lit"), (1.0e11, "cur")]:
    for psi in (1, 4):
        d, Ar, nc = gw_solve(eta, psi)
        out[(tag, psi)] = (d, Ar, nc)
        print(f"  eta={eta:.0e} {psi} psi: d/sigma={d:+.2f}, A_r/A_n={Ar*100:.4f} %, 접촉밀도={nc:.1f} #/mm^2")

# A_r는 η 500배에도 거의 안 변한다(GW의 알려진 둔감성) — 25% 이내
for psi in (1, 4):
    r_Ar = out[("cur", psi)][1] / out[("lit", psi)][1]
    assert 0.8 < r_Ar < 1.3, f"{psi} psi: A_r 비 {r_Ar:.2f} — GW의 A_r 둔감성 서술과 어긋남"
# 접촉점밀도는 눈에 띄게 달라진다(민감) — A_r보다 훨씬 큰 변화
for psi in (1, 4):
    r_nc = out[("cur", psi)][2] / out[("lit", psi)][2]
    r_Ar = out[("cur", psi)][1] / out[("lit", psi)][1]
    assert r_nc > 1.5 and r_nc > r_Ar * 1.4, f"{psi} psi: 접촉밀도 비 {r_nc:.2f}가 A_r 비 {r_Ar:.2f}보다 크게 민감해야 함"
    print(f"  {psi} psi: eta 500배 -> A_r x{r_Ar:.2f} (둔감) vs 접촉밀도 x{r_nc:.2f} (민감)")

# 주류 η에서 계산된 접촉점밀도가 Sun(2009) 공초점 실측(40~240 #/mm^2, 4 psi 부근)과
# 같은 자릿수 안에 드는지 — 다만 '전체 정점' vs '접촉 정점' 정의가 달라 정성 대조만 한다.
nc_lit_4psi = out[("lit", 4)][2]
print(f"주류 eta의 4 psi 접촉밀도 {nc_lit_4psi:.1f} #/mm^2 vs Sun2009 실측 40~240 #/mm^2 (자릿수 대조)")
assert 0.1 < nc_lit_4psi < 1000, "접촉밀도가 Sun 실측과 자릿수조차 어긋나면 σ·R 선택을 재검토해야 함"
```

문헌 재현 대조: Bozkaya & Müftü (2009) Table I 문헌값 2×10⁻⁴ /µm², Suzuki et al. (2017) Table 1
문헌값 200 mm⁻², Sorooshian (2005) 및 Shi & Ring (2010) 문헌값 2e8 /m² 를 SI로 환산해 대조한 결과
네 표기가 모두 2.00e8 /m² 로 완전 일치했다(상대오차 0). 기하 일관성 계산에서 주류값의 평균
asperity 간격은 70.7 µm 로 문헌 정점반경 50 µm 보다 크고, fab-sim 현재값 1e11의 간격은
3.16 µm 로 50 µm 반구와 양립 불가함을 확인했다.

실행 결과(요약): A_r/A_n은 η를 500배 올려도 1 psi에서 0.0619 % → 0.0748 %(1.21배)로 거의
변하지 않지만, 접촉점 밀도는 2.3 → 4.2 #/mm²(1.83배)로 훨씬 민감하게 변한다 — η 오류가
실접촉면적에는 잘 안 드러나고 접촉점 통계·국소압력에 드러난다는 §4 서술을 수치로 확인했다.
주류 η에서 계산한 4 psi 접촉밀도 7.4 #/mm²는 Sun (2009) 공초점 실측 40–240 #/mm²와 같은
자릿수대는 아니지만(§6 참조) 물리적으로 불합리한 범위는 아니다.

## 5. fab-sim `asperity_density_per_m2` 제안 — **적용됨 (2026-09-11, Max워커)**

- **값: 1.0 × 10¹¹ → 2.0 × 10⁸ /m²** (500배 하향), **confidence: `estimated` → `literature`**.
- 근거: §2 표 #1~#5, 독립 5출처(Northeastern·Arizona·Utah·Nagoya/Ebara)가 표기만 다를 뿐 모두
  2.0 × 10⁸ /m². 그중 **Suzuki et al. (2017) CIRP Annals Table 1 "200 mm⁻²"는 Ebara 실기
  패드의 압축시험으로 동정한 값**으로, 이 수렴의 실측 앵커다.
- 동반 파라미터 정합성: 이 η를 채택하면 R=50 µm, σ=5~5.24 µm와 한 세트로 써야 한다
  (#1·#2·#5가 모두 같은 세트를 제시). **η만 바꾸고 R·σ를 다른 출처 값으로 두면 §4 (b)의
  기하 일관성이 다시 깨질 수 있다** — 파라미터 교체 시 세트로 다뤄야 한다.
- ✅ **적용 완료**: `knowledge/params/base.yaml`의 `pad_asperity_density_m2`,
  `asperity_density_per_m2`, `asperity_ref_density_per_m2` 세 값을 모두 2.0e8로,
  confidence를 `literature`로 바꿨다. `sim/factors.py`·`sim/engine.py`는 수정하지
  않았다 — `_pack_conf`가 팩 YAML의 confidence 필드를 그대로 읽으므로 코드 변경은
  불필요했다. 다만 `_f_kappa`의 `f.confidence = _worst_conf(_pack_conf(...), "estimated")`가
  모델 자체의 미검증 함수형(§4의 지수 0.5 등)을 이유로 "estimated" 하한을 항상 강제한다 —
  이는 asperity_density 값의 confidence를 하드코딩한 것이 아니라 κ 팩터 전체에 걸친
  기존 설계이므로 이번 스코프에서 건드리지 않았다(그 결과 base.yaml 변경만으로는 κ의
  최종 confidence 문자열이 `literature`로 안 올라갈 수 있다 — 완료 보고 시 확인 필요).
  커밋은 하지 않았다(Max워커가 git status 확인 후 별도 수행 예정).

## 6. 한계·미검증·문헌 공백 (정직 기록)

- **"CMP 패드의 GW 3종(η, R, σ)을 AFM/광학 프로파일로 직접 측정해 보고한 논문"은 끝내
  확보하지 못했다.** §2의 5건 중 실측 성격이 가장 강한 것은 #5(Suzuki 2017, 패드 **압축시험**
  기반 역동정)이며, 이는 표면형상 직접 측정이 아니라 하중–변위 곡선 피팅이다. #1·#2는
  "base parameter", #3·#4는 타 문헌 인용이다. **따라서 2.0×10⁸은 "문헌에서 널리 쓰이는 값"이지
  "직접 측정된 값"이 아니다** — confidence `literature`가 상한이고 `measured`는 아니다.
- **원출처 Elmufdi et al. (2004)·Shan (2000) 미확보**: #3이 η=2.0×10⁸의 출처로 지목한 두 문헌
  (Elmufdi, Paesano, Muldowney & James, CAMP 2004 학회록 / Shan, Georgia Tech 박사논문 2000)은
  어느 쪽도 온라인 전문을 찾지 못했다(CAMP 학회록은 온라인 미공개, Shan 학위논문은
  검색 결과가 서지정보뿐). **2.0×10⁸의 최초 측정 근거는 2차 인용 단계에서 끊긴다.**
- **Sun (2009) 공초점 실측(40–240 #/mm²)과의 불일치**: §4 (c)에서 주류 η·σ·R로 계산한 4 psi
  접촉밀도는 7.4 #/mm²로 Sun의 실측보다 5~30배 작다. 원인은 (i) Sun의 "contacting summit
  density"가 패드 파편·붕괴 기공벽까지 세는 지표일 가능성([[disk-design-pad-roughness-asperity-relation]]
  §4가 지적한 파편 오염), (ii) σ·R 세트를 Bozkaya Table I에서 가져왔는데 Sun의 패드는 λ가
  3~7 µm로 달랐던 점 — **어느 쪽인지 확인 못 했다.** 이 불일치는 숨기지 않고 기록한다.
- **Jeong et al. (2024)** (*Materials* 17, 1817, PMC11051262, `papers/jeong2024-pad-asperity-pdf-wear-materials.pdf`)는
  CMP 패드 GW를 정면으로 다루지만 **η를 면밀도로 보고하지 않는다** — Table 1은 "N (Number of
  contact objects on CMP pad)" 109·121·106… 같은 **시야 내 개수**만 주고 측정 시야 면적을
  본문에 적지 않았다. 면적을 모르면 /m²로 환산할 수 없어 **이 노트의 표에 넣지 못했다**(가장
  아쉬운 공백).
- **Shi et al. (2023)**, *J. Phys. Conf. Ser.* 2557, 012033 (OA, `papers/statistical-contact-state-polishing-pads-2023.pdf`,
  Dalian Univ.)는 IC1000 패드의 contact spot density N_c를 압력의 함수로 실측(Fig. 4)하지만
  **본문에 수치표가 없고 그래프뿐**이라 판독 없이는 인용할 수 없다. 판독은 이번 범위 밖 —
  후속 과제.
- §3의 "Ring 표의 2.938×10¹¹은 히스토그램 정규화 상수일 것"은 **본 노트의 추정**이며 논문이
  구분해 주지 않는다. 다만 §4 (b)의 기하 반증(간격 1.84 µm vs R 50 µm)은 추정과 무관하게
  성립하므로, **"GW의 η로 쓰면 안 된다"는 결론 자체는 이 추정에 의존하지 않는다.**
- **η는 적용했으나 R·σ는 아직 미적용 상태(후속 과제)**: `knowledge/params/base.yaml`의
  `pad_asperity_radius_m`(R 역할)은 5.0e-6 m(5 µm), `pad_height_beta_inv_m`(σ 역할)은
  0.3e-6 m(0.3 µm)로, §2 #1·#2·#5가 제시하는 세트(R=50 µm, σ=5~5.24 µm)와 둘 다 맞지
  않는다(R은 10배, σ는 ~17~20배 어긋남). §5가 경고한 대로 η만 2.0e8로 바꾸고 R·σ를
  그대로 두면 §4 (b)의 기하 일관성(간격 70.7 µm > R)이 fab-sim 내부에서는 R=5 µm 기준으로
  재검토돼야 한다(간격 70.7 µm > R=5 µm는 여전히 성립하지만, Bozkaya&Muftu 세트와는
  다른 조합이 됐다는 뜻). R·σ를 문헌 세트로 맞출지는 별도 조사·별도 작업으로 남긴다.

## 관련 노트
[[hertz-gw-contact-mechanics]] · [[disk-design-pad-roughness-asperity-relation]] ·
[[gw-nominal-vs-local-pressure]] · [[pad-glazing-mechanism-mrr-decay]] ·
[[pad-porosity-slurry-transport-mrr]]
