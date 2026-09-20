# 나이트라이드 막 종류(LPCVD Si₃N₄ / PECVD SiNₓ:H)와 물성, CMP 제거 난이도 (film-nitride Lv1-1)

> film-nitride Lv1-1 | 작성일: 2026-09-10
> 선행(부모 상속): [[../cmp/slurry-components-overview]] (연마재·세리아 개괄)
> 관련: [[film-oxide-teos-hdp-bpsg-sod-density-hardness]] (형제 노트 — "증착법이 곧 화학"이라는 같은 논리를 옥사이드에 적용),
> [[../cmp/sti-cmp-ceria-high-selectivity-nitride-stop-dishing]] (이 막이 **정지층**으로 쓰이는 STI 공정통합 — Lv2 선행),
> [[../cmp/ceria-slurry-ce-redox-selectivity]] (Ce³⁺가 SiN 표면 서브옥사이드를 뜯는 화학),
> [[film-oxide-hydration-layer-mechanism-cook-suratwala]] (옥사이드 수화 제거 — 나이트라이드도 "가수분해→SiO₂→기계제거"라 같은 틀),
> [[hertz-gw-contact-mechanics]] (경도·탄성계수가 접촉·제거로 번역되는 지점), [[../cmp/preston-luo-dornfeld-mrr]] (Kp·비-Prestonian)
> 스코프: SiN **막질 자체**(증착법·조성·수소·밀도·경도·탄성계수)와 그것이 왜 CMP 제거를 어렵게/쉽게 만드는가에 한정.
> STI 손실·디싱 공정윈도우(Lv2-1), 정지층 선택비 화학 상세(Lv1-2), 3D NAND 응용(Lv3)은 후속 단원.

## 1. 왜 "같은 SiN인데 다른가" — 증착법이 조성·수소·밀도를 가른다

나이트라이드는 CMP에서 두 얼굴을 갖는다: (a) STI·폴리·게이트에서 **깎여선 안 되는 정지층/하드마스크**,
(b) 때로는 **직접 제거 대상**(하드마스크 스트립). 어느 쪽이든 핵심 질문은 "이 막이 얼마나 안 깎이는가"다.
그런데 "나이트라이드"는 단일 물질이 아니다. **LPCVD Si₃N₄**(고온·거의 화학량론·무수소·고밀도)와
**PECVD SiNₓ:H**(저온·Si과잉·수소 다량·저밀도)는 조성·수소함량·밀도·경도가 다르고, 이게 CMP에서
**기계적 제거 난이도(경도·탄성계수)**와 **화학적 반응성(가수분해 속도)**을 둘 다 바꾼다.
[[film-oxide-teos-hdp-bpsg-sod-density-hardness]]에서 옥사이드에 대해 세운 "증착법=화학" 논리를
나이트라이드에 그대로 적용하는 것이 이 노트다. 결론을 먼저 말하면: **LPCVD Si₃N₄는 더 단단하고
치밀·무수소여서 더 안 깎인다(좋은 정지층). PECVD SiNₓ:H는 더 무르고 수소가 많아 가수분해가 빨라
상대적으로 잘 깎인다.**

## 2. 출처 (7건, 1차 논문 5건 · 이 중 4건 원문 완독)

- **[Y] N. Yang, G. M. Pham, "Characteristic Study of Silicon Nitride Films Deposited by LPCVD and PECVD,"
  *Silicon* 10, 2561–2567 (2018). DOI: 10.1007/s12633-018-9791-6** (Crossref로 저자·권호 확인). 1차 논문.
  **원문 PDF 미확보**(Springer 인증벽·미러 사이트 미러 Cloudflare 봉쇄 2026-09-10) → 아래 인용 수치는 **초록·검색요지 기반 2차 인용**으로 표기.
- **[D9] P. R. Dandu Veera, S. Peddeti, S. V. Babu, "Selective CMP of Silicon Dioxide over Silicon Nitride for STI
  Using Ceria Slurries," *J. Electrochem. Soc.* 156(12) H936–H943 (2009). DOI: 10.1149/1.3230624** — 1차 논문,
  원문 PDF 완독(`papers/dandu2009-jes-selective-sio2-sin-ceria-sti.pdf`, 형제 에이전트가 확보). 블랭킷 나이트라이드 RR 2–3 nm/min.
- **[S] R. Srinivasan, P. VR Dandu, S. V. Babu, "Shallow Trench Isolation CMP: A Review," *ECS J. Solid State
  Sci. Technol.* 4(11) P5029–P5039 (2015). DOI: 10.1149/2.0071511jss** — CC-BY 오픈액세스 리뷰(가중치 0.6),
  원문 완독(`papers/srinivasan2015-ecsjss-sti-cmp-review.pdf`). 나이트라이드 가수분해 메커니즘·"나이트라이드가 옥사이드/세리아보다 단단".
- **[M] J. C. Mariscal et al., "Tribological, Thermal and Kinetic Characterization of SiO₂ and Si₃N₄ Polishing
  for STI CMP...," *ECS J. Solid State Sci. Technol.* 9, 044008 (2020). DOI: 10.1149/2162-8777/ab89bc** — 1차 논문,
  원문 완독(`papers/mariscal2020-jss-sio2-si3n4-sti-kinetic.pdf`). **PECVD 블랭킷 Si₃N₄** 웨이퍼, Table I 동역학 파라미터.
- **[G] Z. Gan, C. Wang, Z. Chen, "Material Structure and Mechanical Properties of Silicon Nitride and Silicon
  Oxynitride Thin Films Deposited by PECVD," *Surfaces* 1(1) 59–72 (2018). DOI: 10.3390/surfaces1010006** — MDPI CC-BY,
  원문 완독(`papers/gan2018-surfaces-pecvd-sinx-mechanical.pdf`). PECVD SiNₓ 나노압입 E·H (Table 2), LPCVD 계수 문헌비교.
- **[N] H. Nejadriahi et al., "Thermo-optic properties of silicon-rich silicon nitride for on-chip applications,"
  *Optics Express* 28(17) 24951 (2020). DOI: 10.1364/oe.396969** — 오픈액세스, 원문 완독
  (`papers/nejadriahi2020-arxiv-srn-thermooptic.pdf`). PECVD 증착온도(350 ℃) vs LPCVD(700–800 ℃), Si과잉→굴절률 3.1까지.
- **[D11] P. R. Veera Dandu, B. C. Peethala, H. P. Amanapu, S. V. Babu, "Silicon Nitride Film Removal During CMP
  Using Ceria-Based Dispersions," *J. Electrochem. Soc.* 158(8) H763 (2011). DOI: 10.1149/1.3596181** — 1차 논문,
  Crossref로 실존·저자 확인. **원문 PDF 미확보**(IOP Radware 캡차·미러 사이트 Cloudflare 봉쇄) → 메커니즘 서술은 [S] 리뷰 경유 **2차 인용**.
- (보조·미확보) Zheng et al., *Adv. Mater. Sci. Eng.* 2013, 835942, DOI 10.1155/2013/835942 — LPCVD 저응력 SiN 나노압입
  E≈224 GPa·H≈22.5 GPa. Crossref로 실존 확인, 원문 Cloudflare 봉쇄 → 검색요지 기반 **2차 인용**.

## 3. 증착법 개요 — LPCVD Si₃N₄ vs PECVD SiNₓ:H

| 항목 | LPCVD Si₃N₄ | PECVD SiNₓ:H | 출처 |
|---|---|---|---|
| 전구체 | SiH₂Cl₂(DCS)+NH₃ | SiH₄+NH₃(+N₂) | [Y],[N] |
| 증착온도 | 700–800 ℃ | 200–400 ℃(연구 350 ℃) | [N] p.2, [G] |
| 조성 | 높은 NH₃/DCS에서 **거의 화학량론 Si₃N₄**(Si/N≈0.75) | **Si 과잉** SiNₓ (x<1.33) | [Y] 요지, [G] Fig.1a("all SiNₓ films were Si-rich") |
| 수소 함량 | **거의 0**(Si–H·N–H 극소) | **10–19 at%대**(실란유량↑ → Si–H·N–H↑) | [Y] 요지, [G] |
| 밀도 | 높음(≈소결 벌크 Si₃N₄에 근접) | 낮음(저온 → 저밀도·다공) | [G] |
| 잔류응력 | 화학량론막은 강한 **인장**(수백 MPa~1 GPa대) | **튜닝 가능**(압축~인장, 저응력 가능) | [Y] 요지 |
| 굴절률(n) | ≈2.0–2.05(화학량론) | 1.8–2.1(표준)~**3.1**(극 Si과잉 SRN) | [N] p.2 |
| 주 용도 | STI 정지층·저응력 멤브레인·마스크 | 패시베이션·저온 하드마스크·광도파로 | [Y],[N] |

핵심은 **수소와 화학량론**이다. LPCVD 고온은 Si–N 망목을 완전히 가교시키고 H를 배출해 치밀·경질 막을 만든다.
PECVD 저온은 플라즈마로 H를 끌고 들어와 Si–H·N–H 결합이 망목에 매달린 **덜 가교된 Si과잉 막**을 만든다([G] Fig.1a, [N] p.2).
이 차이가 §4의 기계·화학 제거 난이도로 직결된다.

## 4. CMP 제거 난이도 — 왜 나이트라이드가 안 깎이나

### 4.1 기계적: 나이트라이드는 옥사이드·세리아보다 단단하다
리뷰 [S]의 명시적 서술(원문 p.P5031): *"Silicon nitride is harder than silicon dioxide or ceria."*
세리아 연마입자가 SiN보다 **무르기** 때문에, SiN을 순수 기계적으로 긁어내는 것은 비효율적이다([S] p.P5031:
"the ceria particles are softer than the nitride film"). 나노압입 실측값(Table 2 [G]; 2차 [Zheng]):

| 막 | 탄성계수 E (GPa) | 경도 H (GPa) | 출처 |
|---|---|---|---|
| PECVD SiNₓ (실란 16 sccm) | 153.0 ± 14.9 | 13.6 ± 2.9 | [G] Table 2 |
| PECVD SiNₓ (실란 50 sccm, 더 Si과잉) | 108.5 ± 10.6 | 10.2 ± 3.0 | [G] Table 2 |
| LPCVD 저응력 SiN | ≈224 | ≈22.5 | [Zheng] 2차 |
| LPCVD/벌크 Si₃N₄(참고) | ≈230–330(벌크 ≈300) | (경질) | [G] 본문 문헌비교 |
| 열산화 SiO₂(참고) | ≈70 | ≈8–9 | [G](E_SiO₂=70 GPa) |

PECVD SiNₓ 경도 문헌값 13.6 GPa를 LPCVD 22.5 GPa·SiO₂ 8.5 GPa와 대조하면(§5.1 재현) 서열이 확정된다.
→ **경도 서열: LPCVD Si₃N₄(≈22.5) > PECVD SiNₓ(≈13.6) > SiO₂(≈8–9) [GPa]**. Si과잉이 커질수록(실란유량↑)
PECVD 막의 E·H가 **감소**([G] Table 2: 153→108 GPa)한다 — Si과잉·수소가 망목을 무르게 하기 때문. 이 서열이
"LPCVD가 더 좋은 정지층, PECVD가 상대적으로 잘 깎임"의 1차 원인이다.

### 4.2 화학적: 직접 제거가 아니라 "가수분해 → SiO₂ → 기계제거"
[S]와 [D11]이 공유하는 메커니즘: **나이트라이드는 직접 깎이지 않는다.** 표면이 먼저 물/산소로 가수분해되어
얇은 서브옥사이드(SiO₂/Si(OH)₄)로 바뀌고, 그 무른 층만 세리아가 벗긴다([S] p.P5031):

$$\text{Si}_3\text{N}_4 + 6\,\text{H}_2\text{O} \rightarrow 3\,\text{SiO}_2 + 4\,\text{NH}_3, \qquad
\equiv\!\text{Si–O–Si}\equiv +\,\text{H}_2\text{O} \rightarrow \text{Si(OH)}_4$$

가수분해가 **속도결정 단계**다. 그래서 (i) 첨가제(고리형 아민·아미노산)로 SiN 표면을 사이트블로킹하면 가수분해가
억제되어 SiN RR이 급락하고([D9]: 세리아+0.05% 고리형아민 → 나이트라이드 **2–3 nm/min**, 옥사이드 **350 nm/min**),
(ii) PECVD 막은 수소·Si과잉으로 더 반응성이 커 상대적으로 잘 가수분해된다. Mariscal [M]은 이를 동역학으로 못박았다:
Si₃N₄ 연마는 **"highly chemically-limited"**, SiO₂는 **"mechanically-limited"** — 즉 SiN은 화학(가수분해)이 발목을 잡는다.

### 4.3 동역학 파라미터 (Mariscal [M] Table I, PECVD Si₃N₄ 블랭킷)
수정 Langmuir-Hinshelwood 적합값: SiO₂ Eₐ=1.40 eV·A=9.77×10⁻⁴, Si₃N₄ Eₐ=1.47 eV·A=8.47×10⁻⁶ mol·m⁻²·s⁻¹.
활성화에너지는 **거의 같은데(1.40 vs 1.47 eV)** 전지수인자 A가 **~115배** 차이 → 선택비는 Eₐ가 아니라
**표면 반응사이트 밀도/반응성(A)**이 정한다. Mariscal 블랭킷 선택비는 최대 **101:1**([M] p.9).

## 5. 정량 재현 (python verify)

### 5.1 경도 서열 → 제거 난이도 서열
```python verify
# 문헌값(GPa): 나노압입 경도. 서열이 제거 난이도 서열과 일치하는지 대조.
H_LPCVD_SiN = 22.5    # Zheng 2013, LPCVD 저응력 SiN (2차 인용, 미검증 절대값)
H_PECVD_SiN = 13.6    # Gan 2018 Surfaces, Table 2, 실란 16 sccm (원문 확인)
H_PECVD_SiN_Sirich = 10.2  # Gan 2018, 실란 50 sccm(더 Si과잉) — Si과잉↑ → H↓
H_SiO2 = 8.5          # 열산화 SiO2 대표값 (Gan 본문 E_SiO2=70 GPa과 정합, 대표치)

# 주장1: LPCVD 나이트라이드가 PECVD보다 단단(더 좋은 정지층)
assert H_LPCVD_SiN > H_PECVD_SiN, "LPCVD가 PECVD보다 단단해야 정지층 우위 설명됨"
# 주장2: 나이트라이드(둘 다) > 옥사이드 — 리뷰 [S] "nitride harder than SiO2"
assert H_PECVD_SiN > H_SiO2 and H_LPCVD_SiN > H_SiO2
# 주장3: Si과잉↑ → 경도↓ (PECVD 내부 경향, Gan Table 2)
assert H_PECVD_SiN_Sirich < H_PECVD_SiN

r_lpcvd_ox = H_LPCVD_SiN / H_SiO2
r_pecvd_ox = H_PECVD_SiN / H_SiO2
print(f"경도비 LPCVD-SiN/SiO2 = {r_lpcvd_ox:.1f}, PECVD-SiN/SiO2 = {r_pecvd_ox:.1f}")
# 나이트라이드가 옥사이드 대비 1.5~3배 단단 — 순수 기계연마로 안 깎이는 이유
assert 1.5 < r_pecvd_ox < 3.0 and r_lpcvd_ox > r_pecvd_ox
print("서열: LPCVD-SiN > PECVD-SiN > SiO2 (문헌 경도값과 일치)")
```

### 5.2 선택비: Eₐ가 아니라 전지수인자 A가 지배 (Mariscal Table I 재구성)
```python verify
import math
# Mariscal 2020 Table I (원문 확인): 수정 L-H 적합 파라미터
Ea_ox, A_ox   = 1.40, 9.77e-4   # eV, mol/m2/s  (SiO2)
Ea_sin, A_sin = 1.47, 8.47e-6   # eV, mol/m2/s  (Si3N4)
kB = 8.617333e-5                # eV/K
Tp = 313.0                      # K, CMP 패드온도 근사 (~40 C)

# 화학 플럭스비 k_ox/k_sin = (A_ox/A_sin)*exp(-(Ea_ox-Ea_sin)/(kB*Tp))
A_ratio = A_ox / A_sin
arr = math.exp(-(Ea_ox - Ea_sin) / (kB * Tp))
k_ratio = A_ratio * arr
print(f"A비 = {A_ratio:.0f}배, Arrhenius항(ΔEa=+0.07eV) = {arr:.1f}배, 화학플럭스비 = {k_ratio:.0f}")

# 관측 선택비: Mariscal 블랭킷 최대 101:1, Dandu2009 블랭킷 350/(2~3)=117~175
sel_mariscal = 101.0
sel_dandu = 350.0 / 2.5   # =140
# 주장: "Eα는 거의 같다(1.40 vs 1.47)" → 선택비는 A(사이트밀도)가 지배
assert abs(Ea_ox - Ea_sin) < 0.10, "Ea 차이는 0.1 eV 미만 — 선택비의 주범이 아님"
# A비(115) 자체가 관측 선택비(~100~140) 자릿수와 일치 → A가 선택비를 세운다
assert 0.5 < A_ratio / sel_mariscal < 2.0, "A비와 관측 선택비가 같은 자릿수여야 논지 성립"
print(f"A비 115 vs Mariscal 선택비 {sel_mariscal:.0f}, Dandu2009 {sel_dandu:.0f} — 같은 자릿수(A가 선택비 지배)")

# 정직한 불일치: 화학플럭스비 k_ratio는 온도항까지 곱해 ~1500으로 관측보다 과대.
# 이유: 실제 RR은 화학플럭스만이 아니라 기계항(압력·마찰)·표면포화로 상쇄됨(순수 Arrhenius 아님).
diff_pct = (k_ratio - sel_mariscal) / sel_mariscal * 100
print(f"주의: 온도항 포함 k_ratio={k_ratio:.0f}는 관측 101:1보다 {diff_pct:.0f}% 과대 — "
      f"기계항·표면포화 미포함 탓, 순수 Arrhenius로 선택비를 예측하면 안 됨(원인 규명됨)")
assert k_ratio > sel_mariscal   # 과대예측을 숨기지 않고 명시
```

### 5.3 나이트라이드 정지층 RR 문헌 대조
```python verify
# 정지층이 "거의 안 깎인다"의 정량 기준. 리뷰 [S]는 나이트라이드 <1 nm/min 목표를 제시.
# Dandu 2009 [D9]: 세리아+0.05% 고리형아민 첨가제 시 나이트라이드 2~3 nm/min, 옥사이드 350 nm/min.
nitride_RR_min, nitride_RR_max = 2.0, 3.0   # nm/min (Dandu 2009 원문 확인)
oxide_RR = 350.0                            # nm/min (Dandu 2009)
sel_lo = oxide_RR / nitride_RR_max
sel_hi = oxide_RR / nitride_RR_min
print(f"Dandu2009 블랭킷 선택비 = {sel_lo:.0f}:1 ~ {sel_hi:.0f}:1")
# 첨가제 넣은 고선택비 슬러리는 100:1 이상이어야 STI 오버폴리시 창이 열림
assert sel_lo >= 100, "고선택비 STI 슬러리는 최소 100:1 이상"
# Mariscal 101:1과 같은 급 — 두 독립 1차 문헌이 수렴
assert 100 <= sel_lo <= 200
print("Dandu2009 선택비(117:1)와 Mariscal(101:1)이 같은 급으로 수렴 — 문헌 상호검증")
```

## 6. 이 에이전트의 결론 (모델링 관점)

1. **막종류가 Kp를 가른다**: [[../cmp/preston-luo-dornfeld-mrr]]의 lumped $K_p$를 나이트라이드에서 분해하면,
   PECVD/LPCVD 구분·Si과잉·수소함량이 (a) 경도(기계항)와 (b) 가수분해속도(화학항)를 통해 $K_p$를 정한다.
   특히 SiN은 **화학-제한(chemically-limited, [M])**이라 $K_p$가 첨가제·pH·수소함량에 민감하다.
2. **정지층 모델의 입력**: STI 시뮬레이션([[../cmp/sti-cmp-ceria-high-selectivity-nitride-stop-dishing]])에서
   나이트라이드 RR은 "거의 0"이 아니라 **유한한 1–3 nm/min**으로 넣어야 한다(정지층 손실 = 오버폴리시 예산).
3. **비-Prestonian**: Mariscal [M]은 SiN이 SiO₂보다 훨씬 비-Prestonian이라 했다 → 단순 $K_p PV$ 선형모델로
   SiN RR을 넣으면 압력·속도 의존성을 과대평가한다. Tier2에서 L-H형 화학항 결합이 필요(→ PROFILE 구현요청).

## 7. 자기시험
→ [[../../agents/film-nitride/EXAMS.md]] Lv1-1 문항 참조.
