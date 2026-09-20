# 세리아+EAA 분산제 → oxide MRR: 방향이 실리카(PVA/PVP)와 **반대** (EVIDENCE-RULES #15)

> 대상: `knowledge/params/sti_ceria.yaml`, `knowledge/params/sic_ceria_h2o2.yaml`의
> `dispersant_type: "NONE"` (confidence=estimated). 구현: `sim/chemistry.py::_dispersant_protection_term`
> + `DISPERSANT_MRR_RELATIVE`, `sim/factors.py::_f_psi`.
> [[abrasive-size-concentration-ph-K-additive-mrr-quantitative]] §6 (실리카/Li 2021 PVA·PVP 실측)
> [[ceria-abrasive-size-mrr-peak-shift-vs-silica]] (이 팩의 입경-MRR 정점 163 nm, 이 노트 §4에서 교차검산)
> [[ceria-slurry-ce-redox-selectivity]] (같은 팩의 χ 항, Ce³⁺ 화학)
> [[../EVIDENCE-RULES]] §판정 기록 #15

## 1. 질문

세리아 계(STI/SiC oxide CMP)에서 분산제는 실리카 계(Li et al. 2021)처럼 oxide MRR을 **억제**하는가?
`sti_ceria.yaml`/`sic_ceria_h2o2.yaml`의 `dispersant_type: "NONE"` 주석이 스스로 자백한 갭이다 —
"세리아 슬러리는 실제로 EAA 공중합제 분산제를 쓰지만 정량 MRR 저해값이 문헌에 없다."

## 2. 1차 출처

- **[A]** Kim, J. et al. 2024. "The Stability Evaluation of Ceria Slurry Using Polymer Dispersants with
  Varying Contents for Chemical Mechanical Polishing Process." *Polymers* 16(24), 3593.
  DOI `10.3390/polym16243593`, PMC11679047, MDPI CC-BY. 전문 확보: OA(PMC), 로컬
  `papers/kim2024-polymers-eaa-dispersant-ceria-slurry-fulltext.txt`. PDF는 MDPI 봇차단으로 미확보 —
  PMC 렌더 전문 텍스트만 확보.
- **[B]** Wang, S. (Han et al.) 2024. "The Effect of Sodium Hexametaphosphate on the Dispersion and
  Polishing Performance of Lanthanum-doped Ceria." *Materials* 17(19), 4901.
  DOI `10.3390/ma17194901`, PMC11477672, MDPI CC-BY. 전문 확보: OA(PMC), 로컬
  `papers/wang2024-materials-shmp-laceria-dispersant-fulltext.txt`. PDF 동일 사유로 미확보.

## 3. [A] 정량 — 계 근접도가 매우 높다

세리아(CeO₂, 소성분말) + EAA(ethylene acrylic acid) 아연염 공중합체 분산제(D5/D6/D7 = 5/6/7 wt%) +
PETEOS 산화막(200 mm 웨이퍼, 9 psi, pH 7-8, AP-300, IC1010 패드) — 이 팩의 `dispersant_type` 항이
가리키는 바로 그 화학(EAA)·바로 그 막질(oxide) 조합이다. §3.4 Fig. 20(원문 §Results):

| 시료 | 분산제 함량 | oxide(PETEOS) RR (Å/min) | 불균일도 (%) | DLS 입경 (nm) | 제타전위 (mV) |
|---|---|---|---|---|---|
| 상용(대조) | — | 4706 | 6.82 | — | 49.2 |
| D5 | 5 wt% | **4224** | 9.95 | 281.6 ± 13.3 | 42.9 |
| D6 | 6 wt% | **4538** | 7.31 | 251.8 ± 17.1 | 45.3 |
| D7 | 7 wt% | **4712** | 5.48 | 227.2 ± 0.57 | 52.1 |

원문 §Results 그대로: "The preapred ceria slurry with according to contents of the polymer dispersant
increased to 4224 Å/min, 4538 Å/min, and 4712 Å/min" — **분산제 함량이 오를수록 oxide MRR이 오른다**
(D5→D7: +11.55%). 불균일도도 동시에 개선(9.95→5.48%). §Fig. 6: "the particle size measured at 281.6 nm,
251.8 nm, 227.2 nm for D5, D6, D7... as the polymer dispersant content increases, the particle size...
decreases." 제타전위도 42.9→52.1 mV로 동시에 오른다(§Fig. 11).

**부호 비교**: 실리카/Li 2021(§6, 이미 확보)에서는 분산제(PVA/PVP)가 무첨가 대비 MRR을 **저해**한다
(2700→2604 Å/min, −3.6%; 2700→2486 Å/min, −7.9%). [A]는 분산제 함량이 오를 때 MRR이 **촉진**된다
(+11.55%). **방향이 정반대다.**

## 4. 교란 — 입경이 동시에 움직인다 (EVIDENCE-RULES 판정#13과 동형)

[A]의 D5→D7 스윕은 분산제 함량 하나만 의도적으로 바꿨지만, 그 결과로 DLS 입경이 281.6→227.2 nm로
**동시에** 줄고, 제타전위·점도 거동도 같이 변한다(원문이 명시: "This is considered to be due to better
adsorption of the polymer dispersant onto the surface of ceria particle... which in turn decreases the
particle size."). 즉 분산제 함량 단독 효과가 아니라 **κ(입경) 축과 교란**돼 있다 — 이는 판정#13
(Hwang 2026, Ce³⁺%와 TEM 입경·BET 비표면적이 동시에 움직여 단독 귀속 불가)과 같은 구조다.

이 팩(`sti_ceria`)은 판정#10으로 세리아 입경-MRR 정점을 163 nm로 이미 확정해 `abrasive_size_peak_nm=163`,
`abrasive_size_exp_above_peak=-1/3`을 선언해 두었다. D5/D6/D7의 281.6/251.8/227.2 nm는 전부 163 nm
정점보다 **위**(감소 가지, exponent=−1/3: d가 커질수록 κ항이 줄어든다)에 있으므로, 이 팩 자신의
κ 모델로 "분산제 없이 입경만 281.6→227.2 nm로 줄었다면 κ항이 얼마나 변하는가"를 역산할 수 있다
(§6 코드 재현 — Kim 2024 §Fig.20 수치로 assert). 결과: κ항만으로 **+7.42%**가 설명되고, 관측된
+11.55%(Kim 2024) 중 나머지 **+3.85%**가 잔차다(§6 재현 코드가 이 두 수치를 직접 assert한다).

⚠ 이 잔차가 ψ(분산제 화학) 때문인지, 제타전위·점도 등 이 팩이 모델링하지 않는 다른 축 때문인지는
**이 데이터만으로는 가를 수 없다** — 정직하게 미확정으로 남긴다. 다만 잔차가 (a) 작고(+3.85%,
관측치의 1/3 미만) (b) 실리카의 억제 부호(음수)와 달리 **여전히 양(+)**이라는 점은, "세리아 EAA
분산제가 실리카처럼 MRR을 억제한다"는 가설과 직접 모순된다 — 즉 실리카형 억제 배수를 세리아 팩에
전이하지 않는 현재 선택(NONE=1.0)이 틀렸다는 증거가 전혀 없고, 오히려 반대 방향의 실측이 뒷받침한다.

## 5. [B]는 왜 정량 근거에서 빠지는가 — "못 찾았다"가 아니라 "범위/부적격"

[B](Wang/Han 2024, SHMP 분산제)는 같은 세리아 계열이지만 이 절의 정량 판정에는 쓸 수 없다:

1. **MRR을 전혀 보고하지 않는다.** 원문 전체를 검색해도 "material removal rate"의 수치가 없다 —
   보고 지표는 표면조도 Ra(0.914 nm[무첨가] → 0.806/0.642/0.515 nm[0.5 wt% SHMP, pH 6.69→6→11]),
   탁도(2715 NTU), 제타전위(−48.49/−51.99 mV), XPS 표면 Ce³⁺(31.01%→28.27%, §3.5)뿐이다.
2. **피연마재가 웨이퍼가 아니라 K9 광학유리다** — 반도체 oxide CMP와 막질이 다르다(원문:
   "polished K9 glass workpieces... using the NF-300 system").
3. **분산제 화학도 다르다**(SHMP=무기 인산염 vs [A]/이 팩 맥락의 EAA=유기 고분자).
4. 원문 결론이 직접 명시: XPS Ce³⁺가 SHMP로 오히려 **감소**(31.01→28.27%)했는데도 연마 성능(Ra)은
   개선됐다 — "the improvement of polishing performance by adding SHMP is mainly due to the enhancement
   of the mechanical rather than chemical effect." 즉 [B] 자신의 결론이 "이건 화학(ψ/χ) 경로가 아니라
   기계적 효과"라고 말하고 있어, ψ 배수의 근거로 쓰면 저자의 결론과 어긋난다.

그러므로 [B]는 **방향성 보조 증거**(분산제가 세리아 표면 Ce³⁺%를 낮추면서도 연마 성능은 개선될 수
있다는 사례 — [A]의 "화학 단독이 아니다"는 관찰과 정성적으로 정합)로만 인용하고, 정량 배수 산출에는
쓰지 않는다.

## 6. 정량 재현 (코드)

```python verify
mrr_d5 = 4224.0
mrr_d6 = 4538.0
mrr_d7 = 4712.0
mrr_commercial = 4706.0
unif_d5, unif_d6, unif_d7, unif_commercial = 9.95, 7.31, 5.48, 6.82
d5_size, d6_size, d7_size = 281.6, 251.8, 227.2  # nm, DLS, Table 1
zeta_d5, zeta_d6, zeta_d7 = 42.9, 45.3, 52.1      # mV

# (a) D5→D7 MRR 증가율 — 원문 §Fig.20 수치 그대로
mrr_ratio = mrr_d7 / mrr_d5
mrr_pct = (mrr_ratio - 1) * 100
assert 11.5 <= mrr_pct <= 11.7, f"D5->D7 MRR 증가율 {mrr_pct:.3f}% — 예상 11.5~11.7% 밖"

# (b) 부호 반대 확인: 실리카(Li 2021 §6, PVA/PVP)는 분산제로 MRR이 감소(음수),
#     세리아(Kim 2024, EAA)는 분산제 함량 증가로 MRR이 증가(양수) — 부호가 반대다.
silica_pva_pct = (2604.0 - 2700.0) / 2700.0 * 100   # -3.6%
silica_pvp_pct = (2486.0 - 2700.0) / 2700.0 * 100   # -7.9%
assert silica_pva_pct < 0 and silica_pvp_pct < 0, "실리카 분산제 방향이 음수여야 한다"
assert mrr_pct > 0, "세리아 EAA 분산제 방향이 양수여야 한다"
assert (mrr_pct > 0) != (silica_pva_pct > 0), "부호가 서로 달라야 한다(반대 방향 확인)"

# (c) 교란: 입경이 동시에 -19.3% 변했다(281.6 -> 227.2 nm)
size_change_pct = (d7_size - d5_size) / d5_size * 100
assert -19.4 <= size_change_pct <= -19.2, f"입경 변화율 {size_change_pct:.2f}% — 예상 -19.4~-19.2% 밖"

# 불균일도도 방향이 정합(입경 감소 = 응집 억제 = 균일도 개선): D5->D7 -44.9%
unif_change_pct = (unif_d7 - unif_d5) / unif_d5 * 100
assert unif_change_pct < 0, "불균일도는 개선(감소) 방향이어야 한다"

# (d) 이 팩(sti_ceria) 자신의 κ 입경-정점 모델(판정#10: peak=163nm, exp_above=-1/3)로
#     "분산제 없이 입경만 281.6->227.2nm로 줄었다면" κ항이 얼마나 변하는지 역산해
#     관측된 +11.55%와 겹치는 부분(교란)과 잔차를 분리한다.
peak_nm = 163.0
exp_above = -1.0 / 3.0
assert d5_size > peak_nm and d7_size > peak_nm, "두 입경 모두 정점(163nm) 위 감소가지여야 분기 일관"

def kappa_term(d_nm: float) -> float:
    return (d_nm / peak_nm) ** exp_above

kappa_ratio = kappa_term(d7_size) / kappa_term(d5_size)
kappa_pct = (kappa_ratio - 1) * 100
assert 7.0 <= kappa_pct <= 7.8, f"kappa 단독 예측 {kappa_pct:.3f}% — 예상 7.0~7.8% 밖"

residual_ratio = mrr_ratio / kappa_ratio
residual_pct = (residual_ratio - 1) * 100
assert 3.5 <= residual_pct <= 4.2, f"잔차 {residual_pct:.3f}% — 예상 3.5~4.2% 밖"
# 잔차가 여전히 양수 — "세리아 EAA 분산제가 oxide MRR을 억제한다"는 가설과 모순.
assert residual_pct > 0

print(f"D5->D7 MRR +{mrr_pct:.2f}% (관측), kappa단독 +{kappa_pct:.2f}%(입경 교란분), "
      f"잔차 +{residual_pct:.2f}%(ψ 또는 미모델링 축, 귀속 불가)")
print("OK: 세리아/EAA는 실리카/PVA·PVP와 부호 반대, 교란(입경) 존재, "
      "잔차도 억제 방향 아님 — NONE(배수 1.0) 유지가 문헌과 모순되지 않는다")
```

## 7. 판정 (EVIDENCE-RULES.md 절차)

충돌 구도(EVIDENCE-RULES.md 판정표 #15 표기 기준): **A**=Li et al. 2021 실리카/PVA·PVP 억제
(§6, 이미 확보) — 세리아 팩 입장에서는 **타계 전이(E4)**. **B**=이 노트 §3의 [A]=Kim 2024
세리아/EAA — 대상계(세리아+oxide) 직접 실측이지만 입경과 교란(**E3**). [B]=Wang 2024(SHMP)는
MRR 미보고+K9 유리로 **부적격**(등급 매길 후보 자체가 아님, §5).

- **등급 비교**: B(E3, 대상계 실측) vs A(E4, 타계 전이) — 서열상 **E3 > E4**이므로 1단계에서
  **B 채택**: 세리아 팩에 실리카 억제 배수를 전이하지 않는 것이 맞다.
- **값**: B도 교란(§4) 때문에 정량 ψ 배수를 단독 추출할 수 없다 — `dispersant_type="NONE"`
  (배수 1.0) **값 자체는 변경하지 않는다.**
- **confidence**: `estimated` → **`literature`로 승격**. 근거: 이 승격은 "NONE의 정량값이
  문헌에서 나왔다"는 뜻이 아니라 — **"실리카형 억제 배수를 적용하지 않는다는 이 팩의 결정이
  이제 1차 대상계 실측(E3)으로 뒷받침된다"**는 뜻이다. §6 코드 재현이 (i) 부호가 실리카와
  반대임을 assert하고 (ii) 이 팩 자신의 κ 모델로 교란을 정량 분리했을 때도 잔차가 억제
  방향(음수)이 아님을 assert한다 — EVIDENCE-RULES §4 "효과 없음(null)도 결론이다"와
  같은 구조(cf. 판정#1, #6, #7, #8: null/미이식 결론에 `confidence=literature` 부여 선례).
  `unverified`나 `estimated`로 남기면 "이 선택을 뒷받침하는 근거가 전혀 없다"는 뜻이 되어
  버리는데, 이제는 전혀 없지 않다 — 부호 반대의 1차 실측이 있다.

## 8. 미검증·한계 (정직 표기)

- [A]의 D5/D6/D7은 상용 대조군과 조성·이력이 다른 자체 합성 슬러리라, "분산제 함량"이 유일한
  변수라고 확신할 수 없다(원문도 안정성·pH·전도도가 동시에 변한다고 보고).
- κ 교란 분리(§4, §6-d)는 **이 팩 자신의 163 nm 정점 모델**(판정#10 — 정점 위치 자체가 2차 인용 E5
  근거, 미검증 한계가 그쪽 노트에 이미 기록됨)에 의존한다 — 순환 검증에 가깝다. "잔차 +3.85%"는
  정밀한 귀속값이 아니라 "교란을 걷어내도 억제 방향은 아니다"라는 **부호 판정**으로만 신뢰한다.
- [B]의 Ra 개선(0.914→0.515 nm)은 정성적으로 [A]의 "분산제가 응집을 줄여 연마질을 개선한다"는
  스토리와 정합하지만, MRR과 Ra는 다른 지표라 정량 교차확인은 아니다.
- `dispersant_ref_type`(기준 조성)은 이 팩에 여전히 미선언 — `pack.get_or("dispersant_ref_type",
  "NONE")` 폴백을 그대로 쓴다. Kp가 무분산제 기준 문헌(sti_ceria 자체는 Ce redox 문헌 기준)에서
  역산됐다고 보는 기존 가정과 상충 없음(값 자체가 NONE=1.0이라 이중계상 문제가 생기지 않는다).
- 이 노트는 PDF 원문이 아니라 PMC 렌더 전문 **텍스트**(fitz/HTML 추출본)를 근거로 한다 — 그림의
  픽셀 좌표 값(예: 제타전위 그래프의 정확한 오차막대)은 본문 수치 서술만 신뢰했고 그래프 자체는
  재판독하지 않았다.

## 9. 자기시험

1. Kim 2024 D5→D7에서 PETEOS oxide MRR은 어느 방향으로 움직이는가, 몇 %인가?
   → 상승, +11.55%(4224→4712 Å/min).
2. 이 방향이 실리카(Li 2021, PVA/PVP)와 같은가 다른가?
   → 다르다(반대). 실리카는 분산제가 MRR을 억제(음수), 세리아/EAA는 촉진(양수).
3. 이 팩의 κ 입경-정점 모델(163 nm, exp_above=−1/3)로 281.6→227.2 nm 변화만 넣으면 MRR항은
   몇 % 변하는가, 그리고 관측치와의 잔차는?
   → κ단독 +7.42%, 잔차 +3.85%(여전히 양수 — 억제 방향 아님).
4. Wang 2024(SHMP)가 이 절 정량 판정에서 빠진 이유 두 가지는?
   → (1) MRR을 보고하지 않음(Ra만 보고), (2) 피연마재가 K9 광학유리(웨이퍼 oxide가 아님).
5. `dispersant_type="NONE"`의 **값**이 바뀌었는가, **confidence**가 바뀌었는가?
   → 값은 불변(NONE, 배수 1.0). confidence만 estimated→literature로 승격 — "이 선택이
   틀렸다는 근거가 없고 오히려 반대 방향 실측이 뒷받침한다"는 판단에 대한 근거 승격이지,
   정량값 자체의 근거 승격이 아니다.
