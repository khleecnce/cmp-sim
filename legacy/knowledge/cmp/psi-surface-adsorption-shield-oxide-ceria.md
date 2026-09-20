<!-- V2-SECTION: R2-slurry | 공동: R1-chem | 작성 2026-09-11 | 근거: psi, 흡착, adsorption shield, surfactant, 아미노산, STI 선택비 | 정본: ARCHITECTURE-V2.md §2 (ψ) -->
# ψ 표면 흡착 보호 — 산화막/세리아 계의 첨가제 피복과 MRR 억제 (Lv2)

> cmp-chemistry Lv2 | 작성일: 2026-09-11
> 선행: [[inhibitor-chelator-adsorption-isotherm-passivation]](Langmuir θ의 정의와 ΔG_ads→K),
> [[w-cmp-picolinic-acid-inhibitor-langmuir-dissolution-suppression]](θ→잔여율 exp(−k·θ) 형식의 선례),
> [[sti-cmp-ceria-high-selectivity-nitride-stop-dishing]](STI 선택비가 왜 필요한가),
> [[ceria-slurry-ce-redox-selectivity]](세리아 chemical tooth = ψ가 억제하는 대상).
> 이 노트의 질문: 금속 부식억제제가 **없는** 산화막/세리아 계에서, 첨가제(계면활성제·아미노산·
> 폴리머) 흡착이 MRR을 억제하는 관계를 **문헌 실측에서 폐형식으로 뽑아낼 수 있는가** — 그리고
> Cu/W에서 쓰는 `잔여율 = exp(−k·θ)` 형식을 그대로 재사용할 수 있는가.

---

## 1. 왜 이 단원인가

ψ는 원래 **금속 부동태**(Cu의 BTA, W의 피콜린산)로 정의됐다. 그런데 `oxide_silica` /
`sic_ceria_h2o2` / `sti_ceria` 세 팩은 금속이 아니라 실리카·세리아 슬러리라 `inhibitor_mM`이
없다. COMPLETION.md가 확정한 방향은 팩터 정의를 **'표면 흡착 보호(passivation/adsorption
shield)'**로 넓히는 것이다.

현재 구현(`sim/chemistry.py::_dispersant_protection_term`)은 이 방향을 **이산 룩업 테이블**
(PVA/PVP/PAA/PAM 4종의 상대 MRR)로만 구현해 뒀다. 그래서 세 팩의 ψ는 `unmodeled`이 아니라
`modeled`지만 — **농도 축이 아예 없다.** 첨가제를 얼마나 넣느냐는 사용자가 실제로 돌리는
핵심 노브인데 그 통로가 닫혀 있다. 이 단원은 그 농도 축을 문헌에서 폐형식으로 확보한다.

> ⚠ 사실 정정: 작업 지시는 세 팩의 ψ가 `status=unmodeled`라고 했으나, 실측 결과는
> 세 팩 모두 `status=modeled, value=1.0`이다(§8 검증 로그). 미모델링인 것은 **팩터 전체가
> 아니라 농도 의존성**이다.

---

## 2. 1차 출처

### (A) 주 출처 — 농도 스윕 실측 (폐형식 유도의 근거)

**Park, J.-G. et al. (2003)**, "Surfactant Effect on Oxide-to-Nitride Removal Selectivity of
Nano-abrasive Ceria Slurry for Chemical Mechanical Polishing", *Jpn. J. Appl. Phys.* **42**(9A),
5420–5425. DOI: `10.1143/jjap.42.5420` (doi.org/10.1143/jjap.42.5420).
PDF 확보: `papers/kim2003-jjap-surfactant-oxide-nitride-selectivity-ceria.pdf` (미러 사이트 경유,
사용자 2026-09-05 지시에 따름). 본문 7쪽 전체 확인.

왜 이게 주 출처인가 — 이 노트가 필요로 하는 **정확히 그 데이터**를 갖고 있다:
- 세리아 슬러리(1 wt% 고형분) + **음이온 계면활성제 9수준 농도 스윕**
  (0, 0.02, 0.04, 0.06, 0.08, 0.10, 0.20, 0.40, 0.80 wt%) — §2 Experimental, 원문 p.5421.
- 같은 스윕에서 **산화막과 질화막 RR을 모두** 측정(Fig. 3a, 3b). 즉 억제 곡선이 막질별로 둘.
- 저자가 메커니즘을 명시적으로 **흡착 보호막**으로 서술: *"A greater amount of adsorption onto
  the film surface raises the local viscosity near the film surface and the resulting layer then
  acts as a **passivation layer, preventing the abrasives from approaching the film surface**"*
  (원문 p.5423). — ψ의 정의(표면 흡착 보호)와 문자 그대로 같다.
- 결정적 교차검증: *"the oxide removal follows Preston's law but the nitride removal shows
  **non-Prestonian** behavior"* (Fig. 9, 원문 회귀식 `y=11.429x, R²=0.9716` vs
  `y=−0.0181x+35.992, R²=0.5053`). 질화막은 P·v에 무반응 = 피복막이 입자 접촉 자체를
  차단했다는 뜻. ψ가 **Preston 항과 곱해지는 별도 배수**여야 하는 이유가 여기 있다.

원문이 명시한 정박점(숫자를 읽는 게 아니라 텍스트로 확정된 값):
- 계면활성제 없을 때 산화막/질화막 선택비 = **4.8** (원문 p.5422 본문).
- 0.4 wt%에서 선택비 **> 70** (원문 p.5423 본문, Fig. 8 캡션 조건).
- 0.8 wt%에서 산화막 RR은 무첨가 대비 **1/5** (원문 §3.1: *"the oxide removal rate was one
  fifth of that at zero concentration"*).
- 질화막 RR이 포화되는 **임계농도 ≈ 0.08 wt%** (원문 §3.1 및 Fig. 3b의 화살표 라벨).

### (B) 보조 출처 — 억제제 종류별 선택비 (이산축, 농도축 아님)

**America, W.G. & Babu, S.V. (2004)**, "Slurry Additive Effects on the Suppression of Silicon
Nitride Removal during CMP", *Electrochem. Solid-State Lett.* **7**(12), G327–G330.
DOI: `10.1149/1.1817870`. PDF: `papers/america2004-ecs-slurry-additive-nitride-suppression.pdf`.
조건 고정(1 wt% 세리아 + **2 wt% 첨가제**, pH 9.6±0.1, 5 psi, 75 cm/s), 첨가제 10종 Table I:

| 첨가제 | 질화막 RR (nm/min) | 산화막 RR (nm/min) | 선택비 |
|---|---|---|---|
| Arginine | 1 | 23 | 23 |
| Lysine | 1 | 71 | 71 |
| **Proline** | **2** | **456** | **228** |
| N-methylglycine | 12 | 467 | 38.9 |
| Alanine | 18 | 455 | 30.3 |
| Glycine | 18 | 435 | 24.2 |
| Picolinic acid | 65 | 423 | 6.5 |
| N,N-dimethylglycine | 68 | 438 | 6.4 |
| 3-Aminobutyric acid | 72 | 442 | 6.1 |
| Isonicotinic acid | 71 | 441 | 6.2 |

이건 **단일 농도(2 wt%)의 이산 비교**다 — 농도 스윕이 아니다. 그래서 K·n을 뽑을 수 없고,
"어떤 첨가제가 얼마나 세냐"의 **상대 강도 룩업**으로만 쓸 수 있다.

### (C) 보조 출처 — 독립 교차검증

**Dandu, P.R.V., Penta, N.K., Babu, S.V. (2009)**, "Selective CMP of Silicon Dioxide over Silicon
Nitride for STI Using Ceria Slurries", *J. Electrochem. Soc.* **156**(12), H936–H943.
DOI: `10.1149/1.3230624`. PDF: `papers/dandu2009-jes-selective-sio2-sin-ceria-sti.pdf`.
pyridine HCl 농도 2점(원문 Results, Fig. 4·5): **0.05 wt% → 산화막 ~350 nm/min**(질화막 <2),
**1 wt% → 산화막 ~150 nm/min**(질화막 <2). 산화막이 저농도에서 온전하다가 고농도에서
떨어지는 **같은 부호·같은 모양**. §6에서 독립 검증으로 쓴다.

### (D) 반증 출처 — 반드시 함께 실어야 하는 것

**Nagendraprasad, Y. & Ramanathan, S. (2006)**, "Role of amino-acid adsorption on Silica and
Silicon Nitride surfaces during STI CMP", *J. Electrochem. Soc.* (IITM preprint 확보).
PDF: `papers/prasad2006-jes-aminoacid-adsorption-silica-nitride-sti.pdf` (저자 기관 OA 프리프린트).

TGA로 L-proline·L-arginine의 흡착량을 pH 9/10/11 × 농도 0~0.8 mol/L로 측정한 뒤 내린 결론
(원문 Abstract 그대로): *"The results suggest that the adsorption behavior **does not correlate
with the polishing behavior** of STI CMP and hence **it may not play a key role** in changing the
selectivity."* 근거: 실리카 위에서 proline과 arginine이 **비슷한 양** 흡착하는데 polishing
거동은 정반대(proline은 산화막 RR 유지, arginine은 산화막 RR도 억제).

**이 노트가 여기서 취하는 입장**: 아미노산 계(proline/arginine)는 "흡착량 → 억제율"의 단조
관계가 **문헌에서 반증됐다.** 그러므로 아미노산을 Langmuir θ로 모델링하면 안 된다. §5에서
유도하는 폐형식은 **Park 2003의 음이온 계면활성제 계에만** 적용하고, 아미노산 계는 (B)의
이산 룩업으로만 둔다. 이 구분은 타협이 아니라 문헌이 강제하는 것이다.

---

## 3. 메커니즘

두 갈래가 있고 **서로 다르게 다뤄야 한다.**

**(i) 계면활성제/폴리머 물리 피복 — 입자 접근 차단 (Park 2003)**
첨가제가 막 표면에 흡착 → 국소 점도 상승 + 입체 장벽 → 연마입자가 표면에 도달하지 못함.
Park의 근거는 소거법이다: 제타전위(Fig. 4)도 2차입경(Fig. 5)도 임계농도 0.08 wt%와
**일치하지 않았다**(원문 §3.1 말미). 즉 정전기나 응집이 아니라 **표면 근방 흡착층 자체**가
원인이다. 그리고 질화막의 non-Prestonian 거동(Fig. 9b, R²=0.51, 기울기 ≈0)이 이를 확증한다 —
압력·속도를 올려도 RR이 안 오르는 건 기계 에너지가 아니라 **접근 자체**가 막혔다는 뜻.
→ **이 갈래만 농도-연속 모델링 가능.**

**(ii) 아미노산 화학 특이흡착 — 가수분해 억제 (America 2004)**
proline이 Si₃N₄ 표면의 Si에 카복실 O 2개로 bidentate 결합하고 아미노 H가 격자 N과 수소결합
(America Fig. 3, 결합거리 2.2 Å / Si–O 1.68 Å). 이것이 Si₃N₄ + 6H₂O → 3SiO₂ + 4NH₃
가수분해를 막아 질화막 RR을 2 nm/min으로 떨군다. 구조 요건이 날카롭다 — 아미노기가 α위치에
있어야 하고(3-aminobutyric acid는 β위치라 효과 없음: 선택비 6.1), 아미노 H가 최소 1개
필요하다(N,N-dimethylglycine은 H가 없어 선택비 6.4).
→ **피복률의 연속함수가 아니라 분자구조의 이산 스위치.** (D)의 반증과도 일관된다.

---

## 4. 왜 단순 Langmuir로는 안 되는가 (먼저 기각한 것)

Cu/W가 쓰는 단일자리 Langmuir θ = KC/(1+KC)를 Park Fig. 3 데이터에 맞춰봤다
(9점, 상대오차 가중 최소제곱):

| 막질 | 최적 K | 최적 k | 가중 SSE |
|---|---|---|---|
| 산화막 | 0.10 /wt% | 19.65 | 0.357 |
| 질화막 | 13.5 /wt% | 4.00 | 1.357 |

**둘 다 기각.** 단일자리 Langmuir는 C가 0에서 커질 때 **즉시 볼록하게** 올라가는데, 실측
질화막은 0→0.04 wt%에서 거의 안 변하다가(800→660) 0.04→0.08에서 **절벽처럼** 떨어진다
(660→80). 이 S자 문턱은 단일자리 등온식이 원리적으로 못 만든다.

물리적으로도 예상된 결과다. 계면활성제는 표면에서 **협동적으로(hemimicelle)** 흡착한다 —
먼저 붙은 분자의 소수성 꼬리가 다음 분자를 끌어당겨 임계농도 부근에서 피복이 급격히 완성된다.
Park 본인이 이 지점을 **"critical concentration"**이라 명명했다(Fig. 3b 화살표).

---

## 5. 정량 관계식 유도

### 5.1 협동 흡착 등온식 (Hill / Sips 형)

협동 흡착의 표준 폐형식은 Hill 방정식이다 — 지수 n이 협동성(응집수)을 담는다:

```
θ(C) = (K·C)^n / (1 + (K·C)^n)
```

- n = 1이면 단일자리 Langmuir로 **정확히 환원**된다(형식의 상위 호환).
- K [1/wt%]: 역-임계농도. θ=0.5인 농도가 C₅₀ = 1/K.
- n > 1: 협동적(S자 문턱). Park 데이터가 요구하는 영역.

### 5.2 피복률 → 잔여 제거율

Cu/W 구현(`_inhibitor_term`)이 이미 확립한 형식을 그대로 승계한다:

```
잔여율 R(C)/R(0) = exp(−k · θ(C))
```

왜 (1−θ)가 아닌가 — `sim/chemistry.py:144-158`에 기록된 실제 사고 그대로다. θ가 0.97로
포화하면 그 위 농도가 전부 같은 값으로 뭉개져 **고농도 구간의 구분이 사라진다.** 지수감쇠는
θ가 포화한 뒤에도 k를 통해 단조성을 유지한다. 이 노트는 같은 형식을 재사용하므로 새 함수형을
발명하지 않는다.

### 5.3 기준 조건 정규화 (설계계약 ①)

절대 잔여율을 그대로 MRR에 곱하면 Kp가 이미 포함한 억제를 두 번 센다(2026-09-06 Cu 20배
붕괴 사고). 따라서 **반드시 기준농도 대비 비율**로 낸다:

```
ψ(C) = exp(−k·θ(C)) / exp(−k·θ(C_ref)) = exp(−k·[θ(C) − θ(C_ref)])
```

C = C_ref이면 지수가 0 → **ψ ≡ 1.0 항등적으로**. 부동소수점 오차도 없다(exp(0)=1.0 정확).

### 5.4 Park 2003 Fig. 3 회귀 결과

Fig. 3(a)(b)를 300 dpi로 렌더해 마커를 판독했다(축: 산화막 0–4000 Å/min 500 간격,
질화막 0–1000 Å/min 100 간격). 판독값은 원문이 텍스트로 명시한 4개 정박점과 교차확인했다 —
특히 C=0의 산화막 3850 / 질화막 800은 원문의 "선택비 4.8"을 재현한다(3850/800 = 4.81).

상대오차 가중 최소제곱(scipy `curve_fit`, sigma=y):

| 막질 | K [1/wt%] | n | k | C₅₀ [wt%] | 최대 상대오차 |
|---|---|---|---|---|---|
| **SiO₂ (산화막)** | 1.295 | 4.62 | 3.00 | 0.772 | **6.6%** |
| **Si₃N₄ (질화막)** | 14.02 | 4.62 | 3.40 | 0.0713 | 45%(꼬리), 17%(문턱 이하) |

**선택비의 기원이 여기서 폐형식으로 나온다.** 두 막질의 n은 사실상 같고(4.62 vs 4.62 —
같은 흡착 협동성) **K만 10.8배 다르다.** 즉 계면활성제는 질화막에 산화막보다 ~11배 낮은
농도에서 피복을 완성한다. 그 사이 농도창(0.08~0.4 wt%)이 선택비 창이다:

```
S(C) = S₀ · exp(−k_N·θ_N(C) + k_O·θ_O(C))
```

C₅₀,N = 0.071 wt%는 Park이 (Park 2003) 본문에서 명시한 임계농도 **0.08 wt%**와 독립적으로 일치한다
(회귀는 Fig. 3 마커만 썼고 본문 숫자를 넣지 않았다). 이게 이 유도의 가장 강한 자기검증이다.

### 5.5 k의 식별성 — 정직하게 밝혀야 할 한계

k와 K는 상관이 있다. k를 고정하고 (K,n)만 재적합한 프로파일:

| 고정 k | K | n | 가중 SSE | θ_max(0.8 wt%) |
|---|---|---|---|---|
| 1.63 | 2.01 | 11.17 | 0.01428 | 0.995 |
| **3.0** | **1.295** | **4.62** | **0.01343** | **0.541** |
| 10 | 0.807 | 3.75 | 0.01276 | — |
| 50 | 0.479 | 3.54 | 0.01253 | — |

산화막 쪽 SSE 프로파일은 **거의 평평하다**(0.0143→0.0125). 즉 이 9점만으로는 k를 결정할 수
없다 — 데이터가 결정하는 건 **곡선의 모양**이지 (k, K) 각각이 아니다. k의 절대 하한은
exp(−k·1) ≤ 760/3850 에서 **k ≥ 1.623**로 강제된다.

**k=3.0을 고른 근거**(자의적 선택이 아님을 밝힌다): θ_max = 0.54로 포화 구간에서 멀다.
§5.2가 피하려던 바로 그 문제 — θ→1에서 농도 구분이 죽는 현상 — 을 구조적으로 회피한다.
k=1.63을 고르면 θ_max=0.995로 정확히 그 함정에 빠진다. 질화막 쪽은 프로파일에 실제 곡률이
있어(k=2에서 SSE 26.2, k=3.4에서 0.46, k=6에서 1.70) **k=3.4가 식별된다.**

⚠ 결론: **(K, n, k)를 한 묶음으로만 써라.** k만 따로 바꾸거나 다른 계에서 K만 가져오면
곡선이 깨진다. confidence는 `literature`가 아니라 **`estimated`**가 정직하다 — 값의 출처는
문헌 실측이지만 그림 판독 + 비식별 파라미터가 섞였다.

---

## 6. 독립 교차검증 — Dandu 2009 (다른 연구실, 다른 첨가제)

Dandu 2009의 pyridine HCl 2점(0.05 wt% → 산화막 350 nm/min, 1 wt% → 150 nm/min)에
§5.4 산화막 파라미터를 **그대로** 대입하면:

- θ(0.05) = (1.295×0.05)^4.62/(1+…) ≈ 0.00013 → ψ ≈ 0.9996 (거의 무억제)
- θ(1.0) = (1.295)^4.62/(1+…) ≈ 0.762 → ψ ≈ 0.10

실측 비율은 150/350 = 0.43, 모델은 0.10. **정량적으로는 4배 어긋난다** — 당연하다.
다른 첨가제(양이온성 pyridine vs 음이온 계면활성제), 다른 pH(4~5 vs 6.6~8.4), 다른 세리아.
K는 화학종마다 다르므로 전이되지 않는다.

교차검증이 확인해 주는 것은 **부호와 순서**뿐이다: 저농도에서 산화막이 온전하고, 고농도에서
억제되며, 그 사이 문턱이 존재한다. 이 정성적 일치는 §5의 함수형이 Park 한 편의 우연이
아님을 뒷받침한다. **K·n·k를 Dandu 계에 옮겨 쓰면 안 된다.**

---

## 7. 각 팩에 무엇을 줄 수 있는가 (정직한 배분)

| 팩 | 연마입자 | Park 2003 전이 가능? | 판정 |
|---|---|---|---|
| `sti_ceria` | **세리아** | 같은 계 — 세리아 슬러리 + 계면활성제 + SiO₂/Si₃N₄ | ✅ **직접 적용** |
| `oxide_silica` | **실리카** | 연마입자가 다름(실리카 vs 세리아). 피복 대상은 SiO₂ 막으로 같으나 K는 미확인 | ⚠ **부분** — 함수형만, K는 캘리브레이션 |
| `sic_ceria_h2o2` | 세리아 | 피연마재가 **SiC** — Park에 SiC 데이터 없음. 계면활성제 농도 축도 원 DOE에 없음 | ❌ **근거 없음** |

**`sic_ceria_h2o2`에 값을 넣지 않는다.** SiC는 Si–C 공유결합 세라믹이라 SiO₂의 실란올
표면화학과 흡착 메커니즘이 다르고, 문헌이 없다. 여기서 숫자를 지어내면 시뮬레이터가 오염된다.
이 팩의 ψ는 현행 이산 분산제 경로로 남기고 농도축 부재를 notes로 신고한다.

---

## 8. verify 블록

```python verify
"""ψ 표면 흡착 보호 — Park 2003 JJAP 42, 5420 Fig.3 재현 검증.

이 블록이 지키는 것:
  ① Park Fig.3 9점 농도 스윕을 §5.4 파라미터로 재현 (산화막·질화막)
  ② 원문이 '텍스트로' 명시한 4개 정박점 재현 (그림 판독과 독립)
  ③ 기준조건 ψ ≡ 1.0 (설계계약 ①, 이중계상 방지)
  ④ θ 포화로 고농도 구분이 죽지 않음 (설계계약 ③)
  ⑤ n=1이면 단일자리 Langmuir로 환원 (형식 상위호환)
"""
import math

# ── §5.4 회귀 파라미터 (Park 2003 Fig.3, 상대오차 가중 최소제곱) ──
OXIDE   = dict(K=1.2949, n=4.620, k=3.000)   # SiO2  C50=0.772 wt%
NITRIDE = dict(K=14.021, n=4.623, k=3.400)   # Si3N4 C50=0.0713 wt%

def theta(C, K, n):
    """협동(Hill/Sips) 흡착 피복률. n=1이면 Langmuir로 환원."""
    if C <= 0:
        return 0.0
    x = (K * C) ** n
    return x / (1.0 + x)

def residual(C, K, n, k):
    """무첨가 대비 잔여 제거율 = exp(-k*theta)."""
    return math.exp(-k * theta(C, K, n))

def psi(C, C_ref, K, n, k):
    """ψ 배수 — 기준농도 정규화. C==C_ref에서 항등적으로 1.0."""
    return math.exp(-k * (theta(C, K, n) - theta(C_ref, K, n)))

# ── Park 2003 Fig.3 판독값 (wt%, Å/min) ──
C_SWEEP  = [0.00, 0.02, 0.04, 0.06, 0.08, 0.10, 0.20, 0.40, 0.80]
OX_MEAS  = [3850, 3800, 3730, 3680, 3660, 3650, 3590, 3380,  760]
NI_MEAS  = [ 800,  735,  660,  315,   80,   60,   50,   35,   20]

# ① 산화막 — 전 구간 상대오차 7% 이내
for C, meas in zip(C_SWEEP, OX_MEAS):
    pred = 3850.0 * residual(C, **OXIDE)
    assert abs(pred - meas) / meas < 0.07, f"oxide C={C}: {pred:.0f} vs {meas}"

# ① 질화막 — 문턱 구간(C<=0.08)은 18% 이내.
#    C>=0.10 꼬리는 모델이 27 Å/min에 바닥을 치고 실측은 60→20으로 표류한다.
#    이 꼬리는 이미 '완전 억제' 영역(무첨가 800의 8% 이하)이라 물리적으로
#    유의미한 주장은 '억제됐다'까지다 — 그 이상을 assert하면 과적합을 고정하는 셈이다.
for C, meas in zip(C_SWEEP, NI_MEAS):
    pred = 800.0 * residual(C, **NITRIDE)
    if C <= 0.08:
        assert abs(pred - meas) / meas < 0.18, f"nitride C={C}: {pred:.0f} vs {meas}"
    else:
        assert pred <= 0.08 * 800.0, f"nitride tail C={C}: pred {pred:.0f}"
        assert meas <= 0.08 * 800.0, f"nitride tail C={C}: meas {meas}"

# ② 원문 텍스트 정박점 — 그림 판독과 독립적인 검증
#    (a) 무첨가 선택비 4.8 (원문 p.5422)
assert abs(OX_MEAS[0] / NI_MEAS[0] - 4.8) < 0.05

#    (b) 0.8 wt%에서 산화막 RR = 무첨가의 1/5 (원문 §3.1)
assert abs(residual(0.80, **OXIDE) - 0.20) < 0.01, residual(0.80, **OXIDE)

#    (c) 0.4 wt%에서 선택비 > 70 (원문 p.5423)
sel_04 = (3850.0 * residual(0.40, **OXIDE)) / (800.0 * residual(0.40, **NITRIDE))
assert sel_04 > 70.0, sel_04

#    (d) 질화막 임계농도 ~0.08 wt% (Park 2003) — 회귀로 나온 C50이 본문값과 독립 일치.
#        (회귀는 Fig.3 마커만 사용했고 본문의 0.08을 입력하지 않았다.)
C50_N = 1.0 / NITRIDE["K"]
assert abs(C50_N - 0.08) < 0.015, C50_N

# ③ 설계계약 ① — 기준조건에서 정확히 1.0
for C_ref in (0.0, 0.08, 0.10, 0.40, 0.80):
    assert psi(C_ref, C_ref, **NITRIDE) == 1.0

# ④ 설계계약 ③ — 고농도에서 구분이 죽지 않는다 (엄격 단조 감소)
prev = 2.0
for C in [0.1, 0.2, 0.4, 0.8, 1.6, 3.2]:
    cur = psi(C, 0.10, **OXIDE)
    assert cur < prev, f"C={C} 구분 소실: {cur} !< {prev}"
    prev = cur
#    θ는 포화해도(θ→1) ψ는 계속 줄어드는가 — (1-θ) 형식이었다면 여기서 바닥에 붙는다
assert theta(3.2, **{k: OXIDE[k] for k in ("K", "n")}) > 0.99
assert psi(3.2, 0.10, **OXIDE) < psi(1.6, 0.10, **OXIDE)

# ⑤ n=1이면 단일자리 Langmuir로 정확히 환원 (형식 상위호환)
K_test, C_test = 5.0, 0.3
assert abs(theta(C_test, K_test, 1.0) - (K_test * C_test) / (1 + K_test * C_test)) < 1e-12

# ⑥ 선택비 폐형식 — K 비율 10.8배가 선택비 창을 만든다
assert abs(NITRIDE["K"] / OXIDE["K"] - 10.83) < 0.1
#    두 막질의 협동성 n은 사실상 같다 = 같은 흡착 기구
assert abs(NITRIDE["n"] - OXIDE["n"]) < 0.02

print("PASS — Park 2003 Fig.3 재현, 텍스트 정박점 4개 일치, 설계계약 ①③ 충족")
```

실행 결과: `PASS — Park 2003 Fig.3 재현, 텍스트 정박점 4개 일치, 설계계약 ①③ 충족`

**정량 재현 요약**: 산화막 재현 최대 상대오차 6.6%, 질화막(문턱 이하 구간) 재현 오차 18% 이내로
문헌값(Park 2003 Fig.3, 9점 스윕)과 대조했다. 독립 교차검증(Dandu 2009)은 부호·순서만
일치하고 절대값은 4배 어긋난다(수치 §6 참조) — 이 어긋남도 정직하게 기록한다.

---

## 9. 한계 / 미검증

1. **k는 식별되지 않는다**(산화막). §5.5 참조. (K, n, k)는 한 묶음으로만 쓸 것.
   confidence는 `estimated` — `literature`로 올리면 안 된다.
2. **그림 판독 의존.** Park 2003의 9점은 Fig. 3 마커를 300 dpi 렌더로 읽은 값이다. 원문에
   수치 표가 없다. 다만 텍스트 정박점 4개(선택비 4.8 / 1/5 / >70 / 0.08 wt%)가 모두
   독립적으로 맞아 판독 오류 가능성은 낮다.
3. **K는 화학종·pH별로 다르다.** §6이 실증했듯 다른 첨가제로 전이하면 4배 틀린다.
   Park의 "anionic surfactant"는 원문이 상품명·분자량을 밝히지 않았다 — 이것이 이 데이터의
   가장 큰 약점이다. 같은 음이온 계면활성제라도 사슬길이가 다르면 K가 바뀐다.
4. **아미노산 계는 이 폐형식을 쓰면 안 된다.** Prasad & Ramanathan 2006(§2-D)이 흡착량–억제
   상관을 명시적으로 반증했다. proline/arginine/glycine은 America 2004 Table I의 이산
   룩업으로만.
5. **SiC는 근거 없음.** `sic_ceria_h2o2`에 이 관계식을 적용할 문헌이 없다(§7).
6. **온도 의존성 미모델링.** K는 ΔG_ads를 통해 온도의 함수인데(선행노트
   [[inhibitor-chelator-adsorption-isotherm-passivation]]), Park은 상온 단일 온도만 측정했다.
   ΔG_ads가 없으므로 K(T)로 확장할 수 없다.
7. **협동성 n의 물리적 해석은 하지 않았다.** Hill n을 hemimicelle 응집수로 읽는 건 흔한
   관행이지만 Park이 그 주장을 하지 않았으므로 이 노트도 하지 않는다. n은 곡선 모양
   파라미터로만 취급한다.
