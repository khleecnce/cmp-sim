<!-- V2-SECTION: R2-slurry | 근거: 세리아 입자 표면화학, chemical tooth, Ce 사이트 밀도, 패싯, 선택비 | 정본: ARCHITECTURE-V2.md §3 -->
# 세리아 "화학적 톱니(chemical tooth)"의 입자측 정량 — Ce 표면 사이트 밀도·패싯·크기가 만드는 톱니 개수와 옥사이드 선택비

> 에이전트: slurry-abrasive Lv3-1 | 작성일: 2026-09-13
> 선행: [[abrasive-hardness-hertz-indentation-removal-volume]](Lv2-1 — 입자 경도와 소성압입 제거체적; 이 노트는 그 모델이 세리아에서 왜 무너지는지를 다룬다)
> [[abrasive-concentration-mrr-saturation-contact-probability]](Lv2-2 — 활성 입자 수·점유확률; 이 노트의 §5 "필요 활성 입자 면밀도"가 그 모델을 쓴다)
> [[abrasive-manufacturing-colloidal-fumed-silica-ceria]](Lv1-1 — 소성/습식 세리아 제법)
> 형제(중복 회피·상호참조): [[ceria-slurry-ce-redox-selectivity]](slurry-chemist Lv3-1 — Ce³⁺/Ce⁴⁺ 산화환원·DFT 흡착에너지),
> [[../materials/oxide-ceria-additive-selectivity-review-2024]](film-oxide Lv3-1 — 첨가제 선택비 제어·저결함),
> [[../materials/film-nitride-selectivity-ceria-chemistry]](film-nitride — 나이트라이드 선택 흡착 포화),
> [[sti-cmp-ceria-high-selectivity-nitride-stop-dishing]](film-oxide Lv2-2 — Dandu 2009 RR의 공정통합 번역)
> 스코프: **입자(세리아) 표면 자체의 기하·사이트 밀도**. 첨가제 설계·pH 제형·Ce³⁺ 화학종 제어는 slurry-chemistry/film-oxide 소관이라
> 정량 수치를 새로 만들지 않고 형제 노트를 인용만 한다. 검색어 씨앗은 "ceria abrasive particle size distribution"·
> "abrasive hardness removal rate"의 변형(패싯·사이트 밀도)만 사용(`tools/scope.py --agent slurry-abrasive --check` 통과 확인).

## 0. 이 노트가 형제 노트와 다른 점 (중복 방지 선언, 먼저 읽을 것)

- [[ceria-slurry-ce-redox-selectivity]]는 **Ce³⁺가 왜 활성점인가**(산소공공·전하균형·DFT 흡착에너지)를 다뤘다.
- [[../materials/oxide-ceria-additive-selectivity-review-2024]]·[[../materials/film-nitride-selectivity-ceria-chemistry]]는
  **첨가제가 어떻게 선택비를 100:1 이상으로 올리는가**를 다뤘다.
- 이 노트는 그 어느 쪽도 다루지 않은 질문만 푼다: **톱니가 입자 표면에 몇 개 있고(면밀도), 그중 몇 개가 실제로
  물려서(접촉·슬라이딩), 그것으로 실측 MRR이 설명되는가.** 즉 화학이 아니라 **개수와 기하**다.
  구체적으로 (a) 형석 격자에서 패싯별 Ce 면밀도를 유도해 문헌 원자모사값과 대조하고, (b) 측정된 세리아 MRR을
  "필요 활성 입자 면밀도"로 역산해 접촉 모델과 모순이 없는지 보고, (c) 같은 4 psi에서 콜로이달 실리카와 **입자 1개당**
  효율을 비교해 순수 기계 모델(Luo-Dornfeld)이 놓치는 배수를 숫자로 박는다.

## 1. 왜 이 단원인가 — `ceria_tooth_gain`이 캘리브레이션 1순위인데 근거가 비어 있다

`sim/chemistry.py::_ceria_term`은 chemical tooth를 `1 + gain·(f_Ce3+/f_ref − 1)`의 **Ce³⁺ 분율 선형**으로 놓았고,
팩(`knowledge/params/sti_ceria.yaml`)의 `ceria_tooth_gain`은 `confidence: unverified`에 주석까지
"문헌에 폐형식 함수가 없다 — 이 값이 캘리브레이션 1순위 대상이다"라고 자인한다. 문제는 이 항이 **입자 축 변수를
하나도 보지 않는다**는 것이다: 같은 Ce³⁺ 분율이라도 입경이 3배면 단위질량당 톱니 수는 1/3이고, 입자 형상이
큐브(={100} 우세)냐 팔면체(={111} 우세)냐에 따라 Ce 면밀도와 수산기 피복률이 함께 바뀐다. 이 단원은 그
입자 축을 기하로 먼저 고정한다.

## 2. 출처 (단원 상한 6건 준수 — 1차 4건)

| # | 출처 | 등급(EVIDENCE-RULES) | 확보 상태 |
|---|---|---|---|
| S1 | Brugnoli, Miyatani, Akaji, Urata, Pedone (2023), "New Atomistic Insights on the Chemical Mechanical Polishing of Silica Glass with Ceria Nanoparticles", *Langmuir* 39(15) 5527. DOI: 10.1021/acs.langmuir.3c00304, PMC10116594 (CC-BY) | **E2**(반응성 MD 유도·수치) | 전문 XML 확보·완독 `papers/brugnoli2023-langmuir-ceria-silica-cmp-atomistic.xml`, INDEX 등록 |
| S2 | Dandu Veera, Peddeti, Babu (2009), "Selective CMP of Silicon Dioxide over Silicon Nitride for STI Using Ceria Slurries", *J. Electrochem. Soc.* 156(12) H936. DOI: 10.1149/1.3230624 | **E1**(200 mm 블랭킷 실측, 입자·pH·농도 축 스윕) | 전문 PDF `papers/dandu2009-jes-selective-sio2-sin-ceria-sti.pdf` 완독(fitz 텍스트 대조) |
| S3 | **US9499721B2**(Cabot Microelectronics, 2016) Example 18 / TABLE 18 — 콜로이달 실리카 54 nm, TEOS, 0.5~3.0 wt% × 1.5/3/4/5 psi | **E1**(한 변수 스윕 실측표) | `papers/US9499721B2.txt`, 데이터셋 `validation/datasets/us9499721b2_teos_colloidal_silica_pressure_conc.yaml` |
| S4 | Chakarova et al. (2025), "FTIR Detection of Ce³⁺ Sites on Shape-Controlled Ceria Nanoparticles Using Adsorbed ¹⁵N₂ as a Probe Molecule", *Molecules* 30(15) 3100. DOI: 10.3390/molecules30153100, PMC12348644 (CC-BY) | **E4**(촉매 조건: 773 K 환원·100 K 흡착 — CMP 조건 아님. 패싯 서열·XPS Ce³⁺ 수준만 사용) | 전문 XML `papers/chakarova2025-molecules-ce3-sites-shape-controlled-ceria.xml` |
| S5 | Bellahsene, Sene, Félix, Larionova, Ferrari, Guari (2025), "A Comprehensive Review of the Nano-Abrasives Key Parameters Influencing the Performance in CMP", *Nanomaterials* 15(17) 1366. DOI: 10.3390/nano15171366, PMC12430078 (CC-BY) | **E3 리뷰**(수치는 원논문 미추적 — **2차 인용**으로만) | 전문 XML `papers/bellahsene2025-nanomaterials-nanoabrasive-parameters-review.xml` |
| S6 | 세리아·실리카 경도값 — 기존 노트 [[abrasive-hardness-hertz-indentation-removal-volume]] §4 표(세리아 H=6.44±0.72 GPa, DOI: 10.3390/ma19102134 / 용융실리카 H=7.3 GPa, DOI: 10.1016/j.jnoncrysol.2006.02.113 초록 수준) | E2/E4 (세리아는 벌크 펠릿·핵연료 대체재 시료, 실리카는 원문 미접근) | 노트 내 재인용(**2차 인용**) |

찾았으나 쓰지 못한 것(정직 기록): Ma, Xu, Luo, Lin, Pu (2022), "Enhancing the Polishing Efficiency of CeO₂ Abrasives
on the SiO₂ Substrates by Improving the Ce³⁺ Concentration on Their Surface", *ACS Appl. Electron. Mater.* 5, 526.
DOI: 10.1021/acsaelm.2c01553 — Crossref 실존 확인. Unpaywall은 SSRN 프리프린트(10.2139/ssrn.4026139)만 반환했고
SSRN은 403, 미러 사이트 미러 3종(.ren/.box/.red)은 Cloudflare Turnstile·502로 전부 실패(2026-09-13 실측).
**원문 미확보 → 이 노트는 이 논문의 수치를 쓰지 않는다**(S5가 2차 인용한 도핑 효과만 §8의 반례로 인용).

## 3. 톱니의 기하 — 형석 격자가 정하는 패싯별 Ce 면밀도

CeO₂는 형석(fluorite, Fm3̄m) 구조이고 Ce 부격자는 격자상수 a의 FCC다(S1이 모사한 구조, XRD JCPDS 34-0394와
동일 상). 톱니 개수의 상한은 화학이 아니라 **이 격자가 표면에 내놓는 Ce 개수**로 먼저 정해진다:

```
(111) 면:  σ_Ce = 4/(√3·a²)      (100) 면:  σ_Ce = 2/a²      →  σ(111)/σ(100) = 2/√3 = 1.1547
```

a = 5.411 Å을 넣으면 (111) 7.89 nm⁻², (100) 6.83 nm⁻² — S1이 원자모사에서 보고한 **"Ce atom density is 7.9 and
6.8 Ce per nm² at the ceria (111) and (100) surfaces"와 소수점 첫째 자리까지 일치**한다. 같은 격자에서 밀도(7.216 g/cm³)도
나오며, 이는 §6의 입자 개수 환산에 쓰인다.

그런데 **톱니 개수가 곧 반응성은 아니다.** S1은 같은 논문에서 세 가지를 함께 보고한다:
- (111)은 Ce가 더 조밀한데도 **수산기 피복은 절반**이다: 중성 pH에서 (111)의 Os–H + Ce–OH 합계 5.24 nm⁻²
  (표면 산소 자리의 33%)인 반면 (100)은 10.1 nm⁻²(자리의 90%).
- 그럼에도 실리카 젤과의 계면에서 **Si–O–Ce 결합은 (111)에서 (100)의 약 2배**가 형성되고, (111)은 Si 하나당
  최대 3개의 Ce–O–Si 다리를, (100)은 1개만 허용한다(S1 §"(100) 표면" 논의).
- 반대로 **단위 결합당 반응성은 (100)이 더 높다**("the (100) ceria surface was intrinsically more reactive than (111)", S1 초록).

즉 패싯은 **톱니 밀도(=Ce/nm²)·톱니 물림수(=bridges/Si)·톱니 날카로움(=결합당 반응성)** 세 축을 서로 반대 방향으로
움직인다. 형상 제어(큐브 vs 팔면체 vs 로드)가 MRR에 단조 효과를 주지 못하는 이유의 기하학적 뿌리가 여기다
([[abrasive-shape-effect-purespherical-subset-nonmonotonic]]가 실측에서 본 "형상-MRR 비단조"와 같은 방향).
S4는 독립적으로 (111)이 환원(=Ce³⁺ 생성)이 가장 어려운 면임을 TPR로 보이고("oxygen vacancy formation energy is
highest for the (111) plane"), {100}·{110}이 먼저 환원된다고 보고한다 — **톱니 밀도가 가장 높은 면이 Ce³⁺는 가장
적게 만든다**는 상충. 단 S4는 촉매 조건(773 K 환원)이라 CMP 수용액 조건으로의 전이는 **미검증**.

**재현 요약**: 형석 격자(a=5.411 Å)에서 유도한 Ce 면밀도 7.89/6.83 nm⁻²가 S1 원자모사 보고값 7.9/6.8 nm⁻²와 일치,
(111) 수산기 5.24 nm⁻²가 "표면 산소 자리의 33%"라는 S1 서술과 2 O/Ce 기하로 정합, 밀도 7.22 g/cm³ 재현(1블록).

```python verify
import math
# 형석 CeO2: Ce 부격자 = FCC(격자상수 a). a=5.411 Å (JCPDS 34-0394 상, S1이 모사한 구조)
a = 5.411e-10                     # m
s111 = 4.0 / (math.sqrt(3) * a**2) / 1e18     # Ce per nm^2, FCC {111} 면밀도
s100 = 2.0 / (a**2) / 1e18                    # Ce per nm^2, FCC {100} 면밀도
print(f"Ce 면밀도: (111) {s111:.2f}/nm², (100) {s100:.2f}/nm², 비 {s111/s100:.4f}")
# 문헌값 대조 — Brugnoli 2023 (doi:10.1021/acs.langmuir.3c00304): "7.9 and 6.8 Ce per nm2"
assert abs(s111 - 7.9) < 0.05, f"(111) 면밀도 {s111} != 문헌 7.9"
assert abs(s100 - 6.8) < 0.05, f"(100) 면밀도 {s100} != 문헌 6.8"
assert abs(s111/s100 - 2/math.sqrt(3)) < 1e-12          # 비는 격자상수와 무관한 순수 기하
# (111) 수산기 총량 5.24 nm^-2 = "표면 산소 자리의 33%" — 화학량론 표면은 Ce당 O 2개
oh111, oh100 = 5.24, 10.1       # nm^-2, 중성 pH (Brugnoli 2023 §ceria/water 계면)
frac = oh111 / (2 * s111)
print(f"(111) OH 피복률 {frac*100:.1f}% (문헌 서술 33%)")
assert abs(frac - 0.33) < 0.02, "2 O/Ce 기하로 33% 서술이 재현되지 않음"
# (100)은 OH가 1.93배 많지만 Ce는 0.87배뿐 → Ce당 수산기는 2.2배
print(f"OH 밀도비 (100)/(111) = {oh100/oh111:.2f}, Ce당 수산기비 = {(oh100/s100)/(oh111/s111):.2f}")
assert 1.9 < oh100/oh111 < 2.0 and 2.1 < (oh100/s100)/(oh111/s111) < 2.3
# 같은 격자에서 밀도 — §6 입자 개수 환산에 쓰는 값(문헌 상수 7.22 g/cm3 대조)
NA = 6.02214076e23
rho = 4 * 172.115 / (NA * (a*100)**3)          # g/cm^3, 단위포당 CeO2 4개
print(f"CeO2 결정밀도 {rho:.3f} g/cm³ (문헌 상수 7.22)")
assert abs(rho - 7.22) < 0.02
print("OK: 패싯 Ce 면밀도·수산기 피복률·밀도 전부 격자 기하에서 재현")
```

## 4. 경도로는 세리아를 설명할 수 없다 — 순수 기계 모델의 정량적 실패

Luo-Dornfeld 소성압입 모델([[abrasive-hardness-hertz-indentation-removal-volume]] §2)은 입자를 **리지드 인덴터**로
놓고 제거율을 웨이퍼 경도 H_w의 −3/2승으로 쓴다. 이 모델에는 **입자 재질이 들어가지 않는다** — 같은 크기·같은
농도라면 세리아든 실리카든 같은 MRR을 예측한다(입자당 제거체적 ∝ x²만 다름). 그런데:

- 세리아 벌크 경도 H=6.44±0.72 GPa(S6)는 용융실리카 7.3 GPa보다 **낮고**, Luo가 인용한 SiO₂ 막 유효경도 ≈10 GPa
  보다는 **훨씬 낮다**. 리지드 인덴터 가정은 실리카/SiO₂ 짝에서 이미 아슬아슬했는데([[abrasive-hardness-hertz-indentation-removal-volume]] §4),
  세리아/SiO₂에서는 더 크게 깨진다.
- 그런데 실측은 정반대다: 세리아는 **더 적은 양으로 더 빨리 깎는다**(§6).

따라서 세리아의 제거를 설명하는 항은 경도가 아니라 **표면 화학결합의 개수**여야 한다. 이것이 chemical tooth를
"비유"가 아니라 **세는 대상**으로 다뤄야 하는 이유다.

**재현 요약**: 세리아 경도 6.44 GPa가 SiO₂ 막 10 GPa의 0.64배로 리지드 인덴터 조건(≫1) 위반, Luo-Dornfeld는
입자 재질항이 없어 세리아/실리카 입자당 제거비를 (60/54)²=1.23배로만 예측함을 확인(1블록).

```python verify
# 입자·막 경도 (knowledge/cmp/abrasive-hardness-hertz-indentation-removal-volume.md §3·§4 재인용)
H_ceria = 6.44      # GPa, doi:10.3390/ma19102134 상온 나노압입(벌크 펠릿 — CMP 나노입자 아님, 오더 참고)
H_silica_part = 7.3 # GPa, doi:10.1016/j.jnoncrysol.2006.02.113 용융실리카(초록 수준, 2차 인용)
H_oxide_film = 10.0 # GPa, Fu et al. 2001 재인용치(Luo 2002 본문)
for name, H in (("세리아", H_ceria), ("실리카", H_silica_part)):
    r = H / H_oxide_film
    print(f"{name} 입자/산화막 경도비 {r:.2f}")
    assert r < 1.0, f"{name}가 막보다 단단하면 이 절의 논지가 무너진다"
assert H_ceria < H_silica_part, "세리아가 실리카 입자보다도 무르다는 것이 이 절의 핵심"
# Luo-Dornfeld 입자당 제거율 ∝ x² (입자 재질 무관) — 세리아 60 nm vs 콜로이달 실리카 54 nm
ld_ratio = (60.0/54.0)**2
print(f"Luo-Dornfeld 예측 입자당 제거비(세리아/실리카) = {ld_ratio:.2f}")
assert abs(ld_ratio - 1.23) < 0.01
# 경도를 '입자 쪽'에 넣어 보정해도 방향은 더 나빠진다(무른 입자가 더 잘 깎을 이유가 없다)
assert (H_ceria/H_silica_part)**1.5 < 1.0
print("OK: 순수 기계 모델은 세리아 우위를 1.23배 이상으로 만들 수 없다 — §6 실측과 대조할 기준선")
```

## 5. 톱니 개수로 실측 MRR을 재구성 — "필요 활성 입자 면밀도" 역산

S2의 기준점: **60 nm 세리아 0.25 wt%, 첨가제 없음, pH 4~5.5, 4 psi, 75/75 rpm, IC1000 → 열산화막 350 nm/min**
(원문 Results 본문에 숫자로 명시, 그래프 판독 아님). 이 값을 톱니 개수로 설명할 수 있는지 본다.

가정(전부 명시):
1. 제거 단위는 SiO₄ 하나 = SiO₂ 분자부피 M/(ρN_A) = 45.4 Å³ (ρ=2.2 g/cm³).
2. 톱니 효율: **충돌 24회당 SiO₂ 1개**(Cook 1990 추정치를 S1이 인용 — 원문 미확보, **2차 인용**).
3. 표면 Si–O–Ce 결합 면밀도 σ_b = (Si당 0.1~0.2 결합) × (표면 Si ≈ 4.6 nm⁻²) ≈ 0.46~0.92 nm⁻² → 0.7 nm⁻² 채택(S1).
4. 접촉 폭 w = f_w·d, f_w = 0.05~0.3(오더 가정, **미검증**). 상대속도 V = 0.5~1.5 m/s(S2가 트랙 반경을 안 밝혀
   75 rpm에서 환산 불가 — 대역으로 둔다).

입자 하나가 초당 만드는 결합 사건 = σ_b·w·V, 제거는 그 1/24. 측정 MRR을 맞추려면 **단위면적당 활성 입자가 몇 개
필요한가**를 역산하고, 그것을 입자 단층 완전피복(1/d²)과 비교한다. 결과는 단층의 **0.06~1.06%** — 즉 톱니 모델은
"웨이퍼-패드 실접촉 면적률(통상 0.1~1% 오더, [[../materials/hertz-gw-contact-mechanics]]·[[abrasive-concentration-mrr-saturation-contact-probability]] §4)"과
같은 자릿수의 활성 입자만으로 350 nm/min을 만든다. **화학 톱니는 물리적으로 모자라지 않다**는 것이 이 절의 결론이고,
동시에 "모든 입자가 일하지 않는다"는 활성입자 개념과 정합한다.

**재현 요약**: 350 nm/min(Dandu 2009)을 SiO₂ 45.4 Å³ 단위·Cook 24회/개·σ_b 0.7 nm⁻²로 역산하면 필요 활성 입자는
0.16~2.94개/µm²로 입자 단층(278개/µm²)의 0.06~1.06%이며, 어떤 (f_w, V) 조합에서도 5% 미만임을 확인(1블록).

```python verify
NA = 6.02214076e23
# (1) 제거 단위: SiO2 분자부피 (비정질 ρ=2.2 g/cm³)
V_unit = 60.084 / (2.2 * NA) * 1e-6          # m³
print(f"SiO2 단위부피 {V_unit*1e30:.1f} Å³")
assert abs(V_unit*1e30 - 45.4) < 0.5
# (2) Dandu 2009 (doi:10.1149/1.3230624): 60 nm 세리아 0.25 wt%, 4 psi → 열산화막 350 nm/min
mrr = 350e-9 / 60.0                           # m/s
flux = mrr / V_unit                           # 제거되는 SiO2 개수 /(m²·s)
print(f"제거 플럭스 {flux:.2e} SiO2/(m²·s), Cook 24회/개 → 결합 사건 {flux*24:.2e}/(m²·s)")
assert 1.2e20 < flux < 1.35e20
# (3) 입자 1개의 톱니 사건률 = σ_b · (접촉폭 w) · V, 제거는 1/24
d = 60e-9
sigma_b = 0.7e18            # Si-O-Ce 결합 /m² (Si당 0.1~0.2 × 표면 Si 4.6/nm², Brugnoli 2023)
n_mono = 1.0 / d**2         # 입자 단층 완전피복 면밀도 /m²
fracs = []
for f_w in (0.05, 0.1, 0.3):
    for V in (0.5, 1.0, 1.5):
        per_particle = sigma_b * (f_w*d) * V / 24.0     # SiO2 /s per particle
        n_need = flux / per_particle                     # 필요 활성 입자 /m²
        fr = n_need / n_mono
        fracs.append(fr)
        print(f"  f_w={f_w}, V={V} m/s → 필요 {n_need/1e12:.2f}개/µm², 단층의 {fr*100:.3f}%")
        assert 5e-4 < fr < 0.05, "필요 활성 입자가 단층의 0.05~5% 밴드를 벗어남"
print(f"단층 완전피복 {n_mono/1e12:.0f}개/µm²; 필요 활성분율 {min(fracs)*100:.2f}~{max(fracs)*100:.2f}%")
assert abs(n_mono/1e12 - 278) < 1
assert min(fracs) < 0.001 and max(fracs) > 0.01          # 대역 폭 자체를 기록
print("OK: 톱니 모델은 실접촉 면적률과 같은 자릿수의 활성 입자만으로 350 nm/min을 설명한다")
```

## 6. 입자 1개당 효율 — 같은 4 psi에서 세리아 vs 콜로이달 실리카

두 1차 실측을 **압력을 맞춰(4 psi)** 놓고 비교한다.
- 세리아(S2): 60 nm, 0.25 wt%, 4 psi → 350 nm/min (열산화막)
- 콜로이달 실리카(S3 TABLE 18): 54 nm, 4 psi → 0.5 wt% 135 nm/min, 1.0 wt% 256, 1.5 wt% 294, 2.0 wt% 314, 2.5 wt% 319 (TEOS)

질량당 효율은 세리아 1400 nm/min/wt%, 실리카 270(0.5 wt%)~128(2.5 wt%) nm/min/wt% → **5.2~11배**. 실리카 쪽은
이미 포화 곡선 위에 있으므로([[abrasive-concentration-mrr-saturation-contact-probability]] §3) 가장 덜 포화된
0.5 wt% 점(5.2배)을 보수적 기준으로 삼는다. 여기서 **입자 개수**로 환산하면 이야기가 달라진다: 같은 질량에서
세리아는 밀도가 3.3배 크고 입경도 커서 입자 수가 **0.22배뿐**이다. 따라서 입자 1개당 효율은 **23배**(보수적 기준)
~49배(2.5 wt% 기준). §4에서 계산한 순수 기계 모델의 예측은 1.23배 — **한 자릿수가 아니라 20배 가까이 어긋난다.**
이 차이가 chemical tooth의 실효 크기다.

⚠ 교차연구 비교의 한계(**미검증** 항목): 막이 다르고(열산화막 vs TEOS), 상대속도가 다르며(Westech 75/75 rpm,
트랙 반경 미기재 vs Mirra 100 rpm), pH·첨가제 계가 다르다(pH 4~5.5 무첨가 vs 아미노실란 코어-쉘 pH 4.7).
EVIDENCE-RULES 기준 **E4(교차계 전이)**이므로 이 23배는 "오더 표지"이지 팩에 그대로 넣을 계수가 아니다.

**재현 요약**: 4 psi에서 세리아(Dandu 2009, doi:10.1149/1.3230624) 질량효율 1400 nm/min/wt%가 콜로이달 실리카(US9499721B2 TABLE 18) 270(0.5 wt%)의 5.19배,
입자수 환산 0.222배를 적용하면 입자당 23.3배로 Luo-Dornfeld 예측 1.23배의 19배임을 재현(1블록).

```python verify
import math
# 4 psi 실측 두 계 — Dandu 2009 (doi:10.1149/1.3230624) / US9499721B2 TABLE 18
ceria = dict(mrr=350.0, wt=0.25, d=60.0, rho=7.216)      # rho는 §3에서 격자로 재현한 값
silica_rho, silica_d = 2.2, 54.0                          # 비정질 실리카 밀도(문헌 상수, 콜로이달은 2.0~2.2 — 미검증 폭)
silica = {0.5: 135.0, 1.0: 256.0, 1.5: 294.0, 2.0: 314.0, 2.5: 319.0}   # wt% : nm/min
eff_c = ceria['mrr'] / ceria['wt']
assert eff_c == 1400.0
# 같은 질량에서의 입자 수 비 (∝ 1/(ρ d³))
n_ratio = (silica_rho * silica_d**3) / (ceria['rho'] * ceria['d']**3)
print(f"입자수비(세리아/실리카, 동일 질량) = {n_ratio:.3f}")
assert abs(n_ratio - 0.222) < 0.003
rows = []
for wt, m in sorted(silica.items()):
    eff_s = m / wt
    mass_ratio = eff_c / eff_s
    per_particle = mass_ratio / n_ratio
    rows.append((wt, eff_s, mass_ratio, per_particle))
    print(f"  실리카 {wt} wt%: 질량효율 {eff_s:.0f} nm/min/wt% → 세리아/실리카 질량비 {mass_ratio:.2f}, 입자당 {per_particle:.1f}배")
# 가장 덜 포화된 0.5 wt% 점을 보수적 기준으로 삼는다
wt0, eff0, mass0, part0 = rows[0]
assert wt0 == 0.5 and abs(mass0 - 5.19) < 0.05 and abs(part0 - 23.3) < 0.3
# 포화가 진행될수록 비는 커진다(=실리카가 손해) — 단조성 확인
assert all(rows[i][3] < rows[i+1][3] for i in range(len(rows)-1))
# 순수 기계 모델(§4)의 예측과의 격차
ld = (ceria['d']/silica_d)**2
print(f"기계 예측 {ld:.2f}배 vs 실측 입자당 {part0:.1f}배 → 톱니 배수 {part0/ld:.1f}")
assert 15 < part0/ld < 25, "톱니 배수가 예상 오더(20배 근방)를 벗어남"
print("OK: 압력 정합 비교에서 입자당 20배 안팎의 설명되지 않는 이득 = chemical tooth의 실효 크기")
```

## 7. 크기 축 — 표면 Ce 분율의 기하 상한과 XPS가 재는 것

톱니는 표면 Ce에만 있다. 지름 d 입자에서 **최외곽 Ce 층 하나**가 차지하는 분율은 껍질 모델로
f_surf = 1 − (1 − 2t/d)³, t = d_{111} = a/√3 = 0.312 nm다. 60 nm면 3.1%, 180 nm면 1.0%, 7 nm면 24.5%.
한편 XPS는 입자 전체가 아니라 **탈출 깊이(≈5 nm) 안**만 본다 — 그 안에서 최외곽 층이 차지하는 비중은 6.2%다.
S4가 소성 나노쉐이프(큐브·다면체·로드)에서 **XPS Ce³⁺ ≈ 5%**를 보고하고 그조차 "측정 중 환원 때문일 수 있다"고
단서를 단 것은, 이 기하 상한(6.2%)과 정합한다 — **Ce³⁺가 최외곽 한 층에 갇혀 있다면 XPS는 5~6%를 넘길 수 없다.**

이것이 팩에 주는 함의는 날카롭다. `sti_ceria.yaml`의 `ce3_fraction = 0.15`는 **정의가 명시돼 있지 않다**:
(a) "입자 전체 Ce 중 Ce³⁺ 비율"로 읽으면 60 nm 입자에서 기하 상한 3.1%를 5배 초과해 불가능하고,
(b) "XPS 탐침 깊이 내 비율"로 읽으면 최외곽 2.4층이 전부 환원돼야 하며,
(c) "표면 Ce 중 Ce³⁺ 비율"로 읽으면 완전히 정상값이다. **(c)로 읽어야 물리적으로 성립**하고, 그렇다면 `_ceria_term`의
분모 `ce3_fraction_ref`도 같은 정의여야 한다. 현재 주석에는 이 정의가 없다 — §9 구현 함의에 남긴다.

크기 스케일링도 방향이 갈린다: 단위질량당 입자수 ∝ 1/d³, 입자당 톱니 수 ∝ 접촉면적 ∝ d² → **단위질량당 제거 ∝ 1/d**.
S2의 두 점(60 nm 0.25 wt% → 1400 nm/min/wt%, 180 nm 1 wt% → 600)은 비 2.33배로, 1/d 예측(3.0배)보다 완만하다
(실효 지수 0.77). 두 점·다른 공급사(Rhodia 습식 vs Ferro 소성)·다른 형상이라 **지수는 미검증**, 방향(작은 입자가
질량당 유리)만 확정한다.

**재현 요약**: 껍질 모델 f=1−(1−2t/d)³로 60 nm에서 3.09%, XPS 5 nm 탐침 내 최외곽층 비중 6.25%를 계산해 Chakarova 2025(doi:10.3390/molecules30153100)와
XPS Ce³⁺ ≈5% 정합 확인, 단위질량 제거의 크기 지수는 두 점에서 0.77(예측 1.0)임을 확인(1블록).

```python verify
import math
a = 5.411e-10
t = a / math.sqrt(3) * 1e9          # nm, (111) Ce 층간거리 = 최외곽 한 층 두께로 채택
print(f"Ce 층 두께 t = {t:.3f} nm")
assert abs(t - 0.312) < 0.002
def f_surf(d_nm):                    # 입자 전체 Ce 중 최외곽 한 층의 분율
    return 1.0 - (1.0 - 2*t/d_nm)**3
for d_nm, expect in ((7.0, 24.5), (20.0, 9.1), (60.0, 3.1), (180.0, 1.0)):
    v = f_surf(d_nm) * 100
    print(f"  d={d_nm:6.1f} nm → 표면 Ce층 분율 {v:.2f}% (예상 {expect}%)")
    assert abs(v - expect) < 0.15
# XPS(탈출 깊이 ~5 nm) 안에서 최외곽 한 층이 차지하는 비중
xps_depth = 5.0
frac_probe = t / xps_depth * 100
print(f"XPS 탐침 내 최외곽층 비중 {frac_probe:.2f}% vs Chakarova 2025(doi:10.3390/molecules30153100) XPS Ce³⁺ ≈5%")
assert abs(frac_probe - 6.25) < 0.1
assert 5.0 < frac_probe < 8.0, "측정 Ce³⁺ 5%가 단일층 기하 상한 안에 들어와야 한다"
# 팩 ce3_fraction=0.15의 해석 — 전체 Ce 기준이면 60 nm에서 불가능
assert 0.15 > f_surf(60.0), "0.15가 '전체 Ce 대비'라면 60 nm 입자의 기하 상한을 넘는다(정의 오류)"
print(f"  → ce3_fraction=0.15는 '전체 Ce 대비' 상한 {f_surf(60.0)*100:.2f}%의 {0.15/f_surf(60.0):.1f}배 — '표면 Ce 대비'로 읽어야 성립")
# 크기 스케일링: 단위질량당 제거 ∝ 1/d 예측 vs Dandu 두 점
e60, e180 = 350.0/0.25, 600.0/1.0
n = math.log(e60/e180) / math.log(180.0/60.0)
print(f"질량효율 {e60:.0f} vs {e180:.0f} nm/min/wt% → 실효 지수 {n:.2f} (모델 1.0, 두 점·다른 공급사 — 미검증)")
assert abs(e60/e180 - 2.333) < 0.01 and 0.5 < n < 1.0
print("OK: 표면 Ce 기하 상한·XPS 정합·크기 방향 확인")
```

## 8. 근거 충돌 판정 (EVIDENCE-RULES.md 서열)

| 충돌 | A | B | 판정 |
|---|---|---|---|
| Ce³⁺가 많을수록 MRR이 오르는가 | `_ceria_term`의 선형 가정 + Netzband 2020(형제 노트, H₂O₂로 Ce³⁺% 최대 → oxide MRR 5.5배) | S5 2차 인용: Ln³⁺ 도핑으로 Ce³⁺를 늘렸을 때 SiO₂ RR 증가는 Sm 50.0%, Nd 29.6%, La 20.9%, **Yb 4.3%** — 그런데 **Yb가 Ce³⁺ 함량은 가장 높다** | **단조성 반증(부분)**. Ce³⁺ 개수는 필요조건이지 충분조건이 아니다 — S1의 패싯 결과(밀도·물림수·반응성이 서로 반대로 움직임)와 §3의 상충이 이유를 준다. 판정: `ceria_tooth_gain`의 **선형 외삽 금지**, 기준점 근방에서만 유효(국소 선형화)로 제한하고 상한을 둔다. S5는 리뷰라 수치는 2차 인용 — 원논문 추적 전까지 팩에 계수로 넣지 않는다 |
| 어느 패싯이 "좋은" 톱니인가 | S1: Si–O–Ce 결합은 (111)에서 2배, Ce 면밀도도 (111)이 1.15배 | S1 자신 + S4: 결합당 반응성은 (100)이 높고, Ce³⁺ 생성(환원)은 (111)이 가장 어렵다 | **분해(절차 2)**: "톱니 밀도"(=기하, (111) 우세)와 "톱니 활성"(=산화환원, {100}/{110} 우세)은 **다른 양**이다. 하나의 스칼라 형상계수로 합치지 않는다. S4는 촉매 조건이라 CMP 전이는 미검증 |
| 세리아 농도-MRR 거동 | S3 콜로이달 실리카: 농도 증가 → 포화(단조증가) | S2: 60 nm 세리아는 **0.25 > 0.5 > 1 wt%로 감소**(본문 서술), 180 nm는 1 wt%에서 최대(600 nm/min) | **계 분리**. 실리카의 "자리 점유 포화"([[abrasive-concentration-mrr-saturation-contact-probability]] §4)로는 감소가 안 나온다. 세리아는 입자가 늘면 입자당 하중이 떨어져 톱니가 물리지 못하는 레짐으로 먼저 들어가는 것으로 읽힌다([[sic-alumina-concentration-negative-exponent-entegris]]의 음의 지수와 같은 방향). **정량 수치는 그래프에만 있어 채택 안 함**(본문 서술의 순서만 사용) |

## 9. 팩·구현 함의 (sim/ 은 건드리지 않음 — 구현 요청은 PROFILE.md)

1. **`ce3_fraction`의 정의를 파라미터 주석에 못 박아야 한다** — "표면 Ce 중 Ce³⁺ 분율"(§7). 지금은 정의가 없어
   전체 Ce 대비로 읽으면 60 nm 입자에서 기하적으로 불가능한 값이다.
2. **`ceria_tooth_gain`은 상한을 둔 국소 선형화로 제한**(§8 Yb 반례). 기준점에서 ±1 오더 밖 외삽 금지 경고를 notes에 추가.
3. **`sti_ceria`가 `abrasive_wt_pct=20.0`(실리카 팩 base)을 그대로 상속하고 있다** — 이 팩의 `abrasive_size_nm=60`과
   `kp_m_per_pa`는 Dandu 2009의 **0.25 wt%** 조건에서 온 값이다. 80배 어긋난 기준 농도는 (a) 농도 what-if 축을
   무의미하게 만들고 (b) 세리아가 고농도에서 MRR이 **감소**한다는 S2 관측(§8)과 정면으로 어긋난다. 세리아 팩에는
   `abrasive_wt_pct: 0.25`·`abrasive_ref_wt_pct: 0.25`를 명시 오버라이드하고, 농도 지수는 실리카의 +1/3을
   그대로 쓰지 말 것(부호부터 다를 수 있음 — 별도 단원 필요).
4. **입자 축 톱니 인자의 형태**: 톱니 수 ∝ (표면 Ce 면밀도 σ_Ce) × (접촉면적) × (수산기 피복률). 형상 파라미터를
   넣는다면 스칼라 하나가 아니라 **밀도축·활성축 두 개**로 나눠야 한다(§8 분해 판정). 지금 근거로는 계수를 정할 수
   없으므로 **이번 회차 배선 없음**.

## 10. 한계 / 미검증 목록

- §5의 접촉 폭 f_w(0.05~0.3)·상대속도 V(0.5~1.5 m/s)는 **오더 가정**이다. S2가 트랙 반경을 안 밝혀 75 rpm에서
  상대속도를 못 구했다. 결론(활성분율 ≪ 단층)은 밴드 전체에서 유지되지만 절대값은 **미검증**.
- Cook(1990)의 "24회 충돌당 SiO₂ 1개"는 S1이 인용한 값이고 **원문 미확보(2차 인용)**. Cook 원논문은
  *J. Non-Cryst. Solids* 120, 152(1990)로 유료이며 형제 노트도 확보 실패했다.
- §6의 23배는 **교차연구(E4)** 비교다: 막(열산화막 vs TEOS)·속도·pH·첨가제가 다르다. 실리카 밀도 2.2 g/cm³는
  비정질 표준값으로, 콜로이달 실리카 실제값(2.0~2.2)에 따라 ±10% 흔들린다 — **미검증**.
- 세리아 경도 6.44 GPa는 **핵연료 대체재용 벌크 펠릿** 측정치다(S6 주석 그대로). CMP 나노입자의 경도는 아니다.
- S4는 촉매 조건(773 K H₂ 환원, 100 K ¹⁵N₂ 흡착)이다. 패싯별 환원 난이도 서열을 CMP 수용액·실온으로
  옮기는 것은 **미검증 전이**이며, 이 노트는 방향(서열)만 인용했다.
- S5의 도핑 수치(50.0/29.6/20.9/4.3%)는 **리뷰의 2차 인용**이다. 원논문을 추적하지 못했으므로 반례의 **존재**만
  쓰고 값은 팩에 넣지 않는다.
- Ma et al. 2022(doi:10.1021/acsaelm.2c01553)는 이 단원의 정중앙 주제(Ce³⁺ 농도 ↔ SiO₂ 연마효율)인데
  **원문 확보 실패**(§2). 다음 회차 최우선 확보 대상.
- 세리아 입자의 **실제 노출 패싯 비율**(상용 소성 세리아가 (111)을 얼마나 내놓는지)은 이번 회차에 정량 자료를
  못 찾았다 — "못 찾았다"이지 "없다"가 아니다. HRTEM 통계가 있는 논문이 필요하다.

## 11. 자기시험
→ [[../../agents/slurry-abrasive/EXAMS.md]] Lv3-1 문항 참조.

## 상호링크
[[abrasive-hardness-hertz-indentation-removal-volume]] [[abrasive-concentration-mrr-saturation-contact-probability]]
[[abrasive-manufacturing-colloidal-fumed-silica-ceria]] [[ceria-slurry-ce-redox-selectivity]]
[[../materials/oxide-ceria-additive-selectivity-review-2024]] [[../materials/film-nitride-selectivity-ceria-chemistry]]
[[sti-cmp-ceria-high-selectivity-nitride-stop-dishing]] [[abrasive-shape-effect-purespherical-subset-nonmonotonic]]
[[sic-alumina-concentration-negative-exponent-entegris]] [[../materials/hertz-gw-contact-mechanics]]
[[sic-ceria-abrasive-particle-size-chen2017-rsc]] [[psi-surface-adsorption-shield-oxide-ceria]]
