<!-- V2-SECTION: R2-slurry | factor: psi -->
# ψ 표면 흡착 보호 — 산화막 계 3팩 배선 (sti_ceria · oxide_silica · sic_ceria_h2o2)

> R2-slurry / cmp-chemistry | 작성 2026-09-14 | 팩터: ψ (passivation → adsorption shield)
> 선행: [[psi-surface-adsorption-shield-oxide-ceria]] (Park 2003 Fig.3 회귀 — 이 노트가 그 결과를
> 팩·엔진에 배선한다), [[inhibitor-chelator-adsorption-isotherm-passivation]] (Langmuir θ),
> [[ceria-slurry-ce-redox-selectivity]] (STI 선택비의 세리아 쪽 기원),
> [[sti-cmp-ceria-high-selectivity-nitride-stop-dishing]].
> 이 노트의 질문: 팩터 ψ를 "금속 부동태"에서 **"표면 흡착 보호"**로 넓혔을 때, 산화막 계 세 팩
> 각각에 **문헌이 허락하는 만큼만** 농도축을 어떻게 배선하는가 — 그리고 문헌이 없는 곳을
> 어떻게 정직하게 남기는가.

---

## 1. 배선 전 상태와 목표

`_f_psi`는 억제제 항(`inhibitor_mM`, Cu/W 전용)이 없으면 분산제 종류 이산 룩업
(`dispersant_type`, Li 2021 PVA/PVP)으로만 폴백했다. 세 팩 모두 `dispersant_type: NONE`이라
값은 1.0이고 **농도축이 없어** 사용자가 첨가제를 얼마나 넣든 결과가 안 변했다.
COMPLETION.md "축별 완성 경로"가 확정한 방향: ψ = 표면 흡착 보호(adsorption shield).

목표는 셋이다 — ① 기준 조성에서 ψ ≡ 1.0(Kp 이중 계상 금지) ② 첨가제 농도 ↑ → ψ ↓ 단조
③ 금속 팩(cu_h2o2_bta·w_fe_oxidizer) 경로 불변.

## 2. 관계식 (세 팩 공통 형식)

```
θ(C)  = (K·C)^n / (1 + (K·C)^n)          협동(Hill) 흡착 피복률, n=1 → Langmuir
ψ(C)  = exp(−k · [θ(C) − θ(C_ref)])      기준농도 정규화, C=C_ref 에서 exp(0)=1.0 정확
```

왜 (1−θ)가 아니라 exp(−k·θ)인가 — `sim/chemistry.py::_inhibitor_term`이 2026-09-06 사고
(θ 0.97 포화로 2 mM/5 mM 구분 소실)에서 확립한 형식을 그대로 승계한다. 왜 단일자리 Langmuir가
아니라 Hill인가 — Park 2003 질화막 곡선의 S자 문턱(0.04→0.08 wt%에서 660→80 Å/min)을 n=1은
원리적으로 못 만든다(선행 노트 §4, 기각 근거).

팩 키: `shield_additive_wt_pct`(드라이버, LIMIT_ROLE=MODULATOR) · `shield_ref_wt_pct`(기준, 짝) ·
`shield_langmuir_K` · `shield_hill_n` · `shield_strength_k` · (STI 진단용) `shield_nitride_*`.
**K는 첨가제×막질 쌍의 고유 물성이므로 `has_own` 자기선언일 때만 항이 활성화된다** — 상속값이면
항을 만들지 않고 partial + 사유(AGENTS.md 상속 규칙).

## 3. sti_ceria — Park 2003 직접 적용 (modeled / estimated)

1차 출처: Park, J.-G., Kim et al. (2003) *Jpn. J. Appl. Phys.* 42(9A) 5420–5425,
doi:10.1143/jjap.42.5420 (PDF `papers/kim2003-jjap-surfactant-oxide-nitride-selectivity-ceria.pdf`).
세리아 1 wt% + 음이온 계면활성제 0/0.02/0.04/0.06/0.08/0.10/0.20/0.40/0.80 wt%, 산화막·질화막 RR.
회귀 결과(선행 노트 §5.4, 상대오차 가중 최소제곱):

| 막질 | K [1/wt%] | n | k | C₅₀ [wt%] | 재현 |
|---|---|---|---|---|---|
| SiO₂ | 1.2949 | 4.620 | 3.0 | 0.772 | 9점 최대 상대오차 6.6% |
| Si₃N₄ | 14.02 | 4.623 | 3.4 | 0.0713 | 문턱 이하 18% 이내, 원문(Park 2003, doi:10.1143/jjap.42.5420 §3.1) 임계농도 0.08 wt% 독립 일치 |

텍스트 정박점 대조(그림 판독과 독립): 0.8 wt%에서 산화막 잔여율 0.198 ↔ 원문 "one fifth" ✔;
무첨가 선택비 3850/800=4.81 ↔ 원문 4.8 ✔; 0.4 wt% 선택비 모델 125 ↔ 원문 ">70" ✔.

팩 반영: `shield_langmuir_K=1.2949, shield_hill_n=4.62, shield_strength_k=3.0,
shield_nitride_langmuir_K=14.02, shield_nitride_hill_n=4.62, shield_nitride_strength_k=3.4`,
기준 `shield_ref_wt_pct=0`(팩 kp는 Dandu 2009, doi:10.1149/1.3230624 의 무첨가 60 nm 세리아 조건에서 역산 — 조건 일치).
confidence **estimated**: 문헌 실측이지만 그림 판독 + (K,n,k) 묶음 비식별(산화막 k는 SSE
프로파일이 평평, 하한 k≥1.62만 확정). `literature`로 올리면 오염이다.

엔진 스윕(2026-09-14 실행): C=0/0.08/0.2/0.4/0.8/1.6 wt% → ψ = 1.000/0.9999/0.994/0.872/0.198/0.055
(엄격 단조 감소). 진단 선택비 S = 4.8·ψ_O/ψ_N: 0.08→40, 0.1→79, 0.2→139, 0.4→125, 0.8→28.

## 4. oxide_silica — 검증된 영 (modeled / literature, K=0)

두 독립 출처가 같은 결론을 낸다.

**(A) Penta, Amanapu, Peethala, Babu (2013)** *Appl. Surf. Sci.* 283, 986–992,
doi:10.1016/j.apsusc.2013.07.057 (PDF `papers/penta2013-apsusc-anionic-surfactants-sio2-si3n4-colloidal-silica.pdf`,
미러 사이트 경유, 원문 7쪽 확인). 10 wt% 콜로이달 실리카(50 nm), 음이온 계면활성제 4종
(SDS 0.25 wt% / DBSA·DP·SLS 0.15 wt%, CMC 부근), pH 2~10, 4 psi/75 rpm.
§4.5 원문: *"None of the surfactants studied adsorbs on an oxide surface and, hence, does not
suppress the oxide RR."* Fig.2: 산화막 RR은 무첨가 대비 유지 또는 pH 3~4에서 소폭 상승(대이온
효과). 반면 질화막 RR은 pH ≤4에서 ~1 nm/min으로 억제(정전기 흡착, IEP≈5 아래). — 즉 실리카
슬러리에서 음이온 계면활성제의 ψ는 **산화막에 대해 0, 질화막에 대해서만 존재**한다.

**(B) US10526508B2** (KC Tech, freepatentsonline 전문) Table 1·2: 콜로이달 실리카 1.5~3.5 wt% +
PEG 0/0.2/0.4/0.45/0.5/0.8/1.0/1.4 wt%(10 실시예, pH 3.5, 글루타르산 0.025~1.0 wt%) → 산화막 RR
30/30/30/50/50/50/40/50/50/50 Å/min. PEG 농도–산화막 RR Spearman ρ = **+0.45**(억제 방향 아님,
n=10에 동률 다수). 카탈로그(`knowledge/additives/catalog.yaml` peg)가 "PEG가 산화막 흡착 stopping"
이라 적은 것은 이 특허의 **주장**이고, 실시예 표는 농도 의존 억제를 보여주지 않는다 — 산화막
RR 30~50 Å/min은 pH 3.5 저농도 실리카의 정전 반발 바닥값이다.

판정: 음이온 계면활성제·PEG 클래스에 대해 **K_oxide = 0** → θ ≡ 0 → ψ ≡ 1.0을 항으로 계상
(`adsorption_shield: 1.0`, status=modeled). "모름"과 "효과 없음"을 코드 수준에서 구분한다.
confidence **literature**(원문 서술 + 특허 표, 수치 회귀 아님).

⚠ 반례 클래스 — 양이온 폴리머: US9758697B2 Table 1(세리아 0.2 wt% + picolinic acid, pH 4)
poly(vinylimidazolium) 0/2/4/8 ppm → TEOS 6242/116/98/112 Å/min. 2 ppm에서 이미 98% 억제, 그 위는
평평 → K를 식별할 수 없는 **스위치형**(k 하한 ln(6242/112)=4.0). PDADMAC 20 ppm에서 산화막·질화막
<1 nm/min(Penta 2011 Langmuir, doi:10.1021/la104257k)도 같은 모양. 이 클래스는 Hill 폐형식의 대상이
아니며 이번 배선에서 **미모델링**(notes 신고). 실리카 팩 기본 첨가제 클래스가 아니므로 격자에는
영향 없다.

## 5. 세 팩 한눈에

| 팩 | 활성 항 | status | confidence | 근거 |
|---|---|---|---|---|
| sti_ceria | adsorption_shield(Hill) + dispersant | modeled | estimated | Park 2003 회귀 |
| oxide_silica | adsorption_shield(K=0, 검증된 영) + dispersant | modeled | literature | Penta 2013 §4.5, US10526508B2 T2 |
| sic_ceria_h2o2 | dispersant 만 | **partial** | literature | 문헌 없음(§6) |
| cu_h2o2_bta / w_fe_oxidizer | inhibitor (불변) | modeled | unverified | 기존 |

## 6. sic_ceria_h2o2 — 문헌 없음 (partial)

코퍼스 DB 1510건(제목 nitride/selectiv/surfactant/polymer/silicon carbide 필터 + 본문 SiC×surfactant
스캔)과 웹 검색에서 **SiC 위 첨가제 농도–RR 스윕**을 찾지 못했다. 근접 후보:
- Zhou et al. 2015 *Appl. Surf. Sci.* doi:10.1016/j.apsusc.2015.10.158 — 6H-SiC, 실리카/세리아 +
  KMnO₄ + Triton X-100 0.5 wt% 단일 최적점(초록만; 원문 미확보, 스윕 표 유무 미검증).
- US20220315802A1 — SiC 알루미나/지르코니아 슬러리, 첨가제 1% 단일 비교(Table 5), 농도축 없음.
- MDPI mi13101752 SiC CMP 리뷰 — surfactant 언급 0건.
SiC는 Si–C 공유결합이라 SiO₂ 실란올 표면화학이 없고, 부모 K는 계면활성제×SiO₂ 쌍 상수라
전이 금지. 팩에는 드라이버(`shield_additive_wt_pct=0`)와 기준만 선언하고 K는 **미선언** →
`has_own` 게이트가 항을 만들지 않는다. 사용자가 이 값을 올려도 결과 불변이며 notes가 그 사실을
말한다. 원문 스윕 표가 확보되면 K 역산 → 자기선언 → 자동 활성화.

## 7. verify 블록

```python verify
"""ψ 산화막 계 배선 검증 — 문헌값 재현 + 설계계약(기준 1.0, 단조, 금속 불변)."""
import math

def theta(C, K, n):
    if C <= 0 or K <= 0: return 0.0
    x = (K*C)**n; return x/(1+x)
def psi(C, Cref, K, n, k):
    return math.exp(-k*(theta(C,K,n)-theta(Cref,K,n)))

# ── sti_ceria: Park 2003 정박점 (팩 값 그대로) ──
KO,nO,kO = 1.2949, 4.62, 3.0
KN,nN,kN = 14.02, 4.62, 3.4
assert abs(math.exp(-kO*theta(0.8,KO,nO)) - 0.20) < 0.01           # 0.8 wt% 산화막 = 1/5
assert abs(1/KN - 0.08) < 0.015                                     # 질화막 임계농도 ≈0.08 wt%
S04 = 4.8*psi(0.4,0,KO,nO,kO)/psi(0.4,0,KN,nN,kN)
assert S04 > 70, S04                                                # 0.4 wt% 선택비 >70
assert abs(KN/KO - 10.83) < 0.1                                     # K 비 = 선택비 창

# ── 기준조건 항등 1.0 & 엄격 단조 감소 (엔진 스윕 재현) ──
assert psi(0.0,0.0,KO,nO,kO) == 1.0
sweep = [psi(C,0.0,KO,nO,kO) for C in (0.0,0.08,0.2,0.4,0.8,1.6)]
assert all(a > b for a,b in zip(sweep, sweep[1:])), sweep
assert abs(sweep[3]-0.872) < 0.002 and abs(sweep[4]-0.198) < 0.002   # 0.4→0.872, 0.8→0.198

# ── oxide_silica: 검증된 영 — K=0 이면 어떤 농도에서도 정확히 1.0 ──
for C in (0.0, 0.5, 1.4, 10.0):
    assert psi(C, 0.0, 0.0, 1.0, 1.0) == 1.0
# US10526508B2 Table 1·2 PEG 농도 vs 산화막 RR — 억제 방향(음의 순위상관)이 아니다
C_peg = [0.5,0.4,0.4,0.45,0.5,0.2,0.0,0.8,1.0,1.4]; RR_ox = [30,30,30,50,50,50,40,50,50,50]
def rank(x):
    s=sorted(range(len(x)),key=lambda i:x[i]); r=[0]*len(x); i=0
    while i<len(x):
        j=i
        while j+1<len(x) and x[s[j+1]]==x[s[i]]: j+=1
        for q in range(i,j+1): r[s[q]]=(i+j)/2+1
        i=j+1
    return r
rc,rr = rank(C_peg),rank(RR_ox); m=len(rc); mc=sum(rc)/m; mr=sum(rr)/m
rho = sum((a-mc)*(b-mr) for a,b in zip(rc,rr))/math.sqrt(sum((a-mc)**2 for a in rc)*sum((b-mr)**2 for b in rr))
assert rho > 0, rho                                                  # ρ=+0.45
# 양이온 폴리머는 스위치형 (US9758697B2 Table 1): 2 ppm 에서 이미 98% 억제
assert 1 - 116/6242 > 0.98

print("PASS — Park 2003 정박점 3개, 기준 1.0, 단조, oxide K=0 검증된 영, PEG ρ=%.2f" % rho)
```

실행 결과: `PASS — Park 2003 정박점 3개, 기준 1.0, 단조, oxide K=0 검증된 영, PEG ρ=0.45`
(엔진 재현: `compute_factors(sti_ceria, shield_additive_wt_pct=0.4).psi = 0.8719`,
`0.8 → 0.1975`, 문헌값 0.20 대조 1% 이내).

## 8. 새로 도출한 지식

1. **선택비는 "질화막 억제"가 아니라 두 흡착상수의 비다.** 같은 계면활성제가 두 막질에 같은
   협동성(n≈4.62)으로 붙되 K가 10.8배 다르다. 그 결과 선택비 S(C)는 단조가 아니라 **정점형**
   (C≈0.2 wt%에서 S≈139, 0.4에서 125, 0.8에서 28)이다 — 질화막이 먼저 정지하고 산화막이 뒤늦게
   따라 떨어지는 창이 곧 STI 공정 창이다. 농도를 "많이"가 아니라 **두 C₅₀ 사이**에 둬야 한다.
2. **같은 첨가제 클래스라도 연마입자가 바뀌면 ψ의 대상 막이 바뀐다.** 세리아 슬러리에서는 음이온
   계면활성제가 산화막에도 흡착해(K_O=1.3/wt%) 고농도에서 산화막까지 억제하지만, 실리카 슬러리에서는
   산화막에 전혀 흡착하지 않는다(Penta 2013). 세리아 표면의 양전하(pH<IEP 6.8)가 음이온 계면활성제를
   입자 쪽에 끌어 입자-막 사이 층을 만드는 반면, 실리카는 음전하라 그 층이 생기지 않는다는 해석이
   일관되나 **추정**(Park·Penta 어느 쪽도 이 대비를 직접 실험하지 않았다).
3. **흡착 억제제는 두 클래스로 갈린다 — Hill형(연속)과 스위치형(불연속).** 음이온 계면활성제는
   0.02~0.8 wt%에 걸쳐 S자 곡선을 그리지만, 양이온 폴리머는 2 ppm(2×10⁻⁴ wt%)에서 이미 98% 억제
   후 평평하다. 후자는 농도축 모델의 대상이 아니라 on/off 룩업이다. 이 구분 기준(스윕에서 첫 점이
   이미 포화인가)은 물질명 없이 적용된다.
4. **"검증된 영"은 격자를 채우는 정당한 방법이다.** oxide_silica ψ는 문헌이 "효과 없음"을 명시했으므로
   K=0 항을 계상해 modeled/literature가 된다. 이것은 unmodeled를 1.0으로 숨기는 것과 다르다 —
   notes가 출처와 함께 "효과 없음"을 말하고, 양이온 폴리머라는 예외 클래스를 미모델링으로 신고한다.

## 9. 한계 · 미검증

- sti_ceria (K,n,k)는 묶음 식별(선행 노트 §5.5) — estimated 유지. Park의 계면활성제 상품명·분자량
  불명(원문 미기재)이라 다른 음이온 계면활성제로의 전이는 미검증.
- oxide_silica K=0의 관측 창: 계면활성제 ≤0.25 wt%(Penta), PEG ≤1.4 wt%(특허). 그 밖 고농도(점도
  상승 경로)는 미검증.
- sic_ceria_h2o2: 문헌 없음 — partial. Zhou 2015 원문 미확보(2차 인용).
- 농도축과 분산제 종류 항의 곱은 독립 가정(같은 자리 경쟁 커플링 미모델링).
- 온도 의존 K(T) 없음(Park 상온 단일).
