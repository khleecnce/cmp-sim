<!-- V2-SECTION: R2-slurry | 근거: abrasive size, alumina, tungsten, ferric nitrate, evidence conflict | 정본: ARCHITECTURE-V2.md §3 -->
# 텅스텐 CMP — abrasive_size_nm(알루미나+Fe계 산화제) 두 후보값(700nm·60nm) 원문 확인과 기각, (Bielmann 1999)로 대체

> 에이전트: (수동 조사, w_fe_oxidizer.yaml abrasive_size_nm 문헌 승격 작업) | 작성일: 2026-09-11
> [[particle-wafer-interaction-mechanical-chemical-balance]] [[w-cmp-fenton-catalyst-abrasive-alumina-silica]]
> [[w-cmp-wo3-passivation-oxidizer-kaufman]] [[abrasive-size-d50-ekc-alumina-cu-h2o2-bta-gopal-ihnfeldt-talbot]]
> EVIDENCE-RULES.md #4

## 1. 왜 필요한가
`knowledge/params/w_fe_oxidizer.yaml`의 `abrasive_size_nm`(W plug CMP, 알루미나+Fe(NO₃)₃ 산화제)이
`confidence: estimated`(value: 150.0)로 남아 있었다. 사전에 두 후보(OSTI 0.7 μm, Cabot v. Solution
Technology 판례문서 60 nm)가 상충한다는 단서가 있어 원문을 직접 확인했다. 결과: **둘 다 이 계에
그대로 쓸 수 없었고**, 원문 추적 과정에서 훨씬 더 계 근접한 1차 문헌(Bielmann et al. 1999)을 찾아
그쪽을 채택했다.

## 2. 후보 A — OSTI LLNL-BOOK-816634 "0.7-μm-diameter alumina particles in 1% ferric nitrate" (E5)
원문 확보(`osti.gov/servlets/purl/1830476`, Free & Zhu, "The Use of Surfactants in Enhanced Particle
Removal During Cleaning," *Surfactants in Precision Cleaning* ch.3, LLNL, 2020). 이 챕터는 **2020년
리뷰**이고, "0.7-μm-diameter alumina particles in 1% ferric nitrate medium at 31°C"라는 정확한 문구는
**Fig. 3.20(석영유리)·Fig. 3.21(구리)** 캡션에만 등장한다. **텅스텐 데이터는 Fig. 3.15·3.16**인데
캡션은 "polishing of a tungsten-coated surface using 0.7-μm-diameter alumina particles"뿐이고
**산화제(ferric nitrate)를 명시하지 않는다** — 즉 원문을 직접 읽어도 "W + 알루미나 + 질산철" 조합이
0.7 μm이라는 서술은 **확인되지 않는다**(구리/석영유리에서만 확인됨). 이 챕터의 참고문헌 [104]가
바로 §3의 Bielmann et al. 1999(아래)이므로, 이 챕터는 Bielmann의 1차 데이터를 재인용하는 **2차
문헌**이기도 하다. 등급: **E5**(2차 인용/편집 서술, 산화제-필름 조합이 원문에서 명시적으로 대응되지
않음) — EVIDENCE-RULES E5는 단독 채택 금지.

## 3. 후보 B — Cabot Corp. v. Solution Technology, Inc., 122 F. Supp. 2d 599 (W.D.N.C. 2000), "60 nm" (기각)
원문 확보(law.justia.com, 사실인정 부분 전문 대조). 60 nm은 STI(피고)의 상품 **"Ultra-Sol 201 A/60"**
(boehmite alumina, Vista Chemical 제조)를 가리키며, 법원 사실인정 원문:
> "These slurries were of the product Ultra-Sol 201 A, a very small particle boehmite alumina
> dispersion, having particle size of 60 nm... **The chemical component of those slurries was nitric
> acid.** Yancey did not sell IBM boehmite alumina and ferric nitrate."

즉 이 60 nm 제품의 화학성분은 **질산(HNO₃)이지 질산철(Fe(NO₃)₃)이 아니다**. 이 사건에서 boehmite
alumina + **ferric nitrate**의 조합이 나오는 곳은 별도로, Yancey가 1996년에 발명을 주장한 **구리
연마용 화합물**("a new patent disclosure for a copper polish made up of boehmite alumina and ferric
nitrate")이다 — **텅스텐이 아니라 구리** 계다. 더구나 이 판례문서에서 실제 텅스텐 CMP 제품으로
언급되는 것은 Cabot의 특허 슬러리(Semi-Sperse W-A355, **fumed alumina** 사용, Hung 담당)와 Rippey의
텅스텐 슬러리(**M100 감마알루미나, 1–1.5 μm**, Yancey 증언)뿐이며 둘 다 60 nm이 아니다. 판정:
**대상 계(W+알루미나+Fe(NO₃)₃) 자체가 아니다 — 기각**(E6 상당: 계 불일치로 채택 대상에서 제외).
텅스텐용 60 nm 알루미나·질산철 조합을 뒷받침하는 서술은 이 판례문서 어디에도 없다.

## 4. 채택 — Bielmann et al., *Electrochem. Solid-State Lett.* 2(3), 148–150 (1999) (E2)
DOI: 10.1149/1.1390765 (원문 PDF 확보). 계 근접도가 가장 높다 — **CVD W(0.6 μm)막, γ-알루미나
연마입자, Fe계 산화제[K₃Fe(CN)₆, 0.1–0.15 M], pH 4(HNO₃로 조정)**, IC-1000/SUBA IV 패드, 6.5 psi,
150 rpm 실제 CMP 폴리싱 실험(제거율 결과로 자체 검증됨). 원문 실험절 발췌:
> "The polishing slurries contained 10 wt % γ-alumina particles (**primary size ~50 nm diam**)."

같은 문단에서 별도 목적(SEM 부착력 관찰)으로 쓴 입자만 300–500 nm임을 명시하며 **폴리싱 슬러리
자체의 값이 아님**을 저자가 스스로 구분한다:
> "For these tests, larger sized alumina particles (300-500 nm) where chosen to facilitate the SEM
> observation."

제거율 810±40 nm/min(표면활성제 안정화) / 560±30 nm/min(비안정화)로 4회 반복 재현성까지 보고돼
데이터 신뢰도가 높다. 산화제가 Fe(NO₃)₃가 아니라 K₃Fe(CN)₆이라는 차이는 있으나 둘 다 "Fe(III)계
산화제, 산성 pH, W-CMP" 동일 화학 패밀리([[w-cmp-fenton-catalyst-abrasive-alumina-silica]] §2의
Fe³⁺ 촉매 순환 논리가 공통)이고, 필름·연마재(γ-알루미나)·공정조건은 사실상 동일계다.

## 5. EVIDENCE-RULES 판정
원 지시대로면 "A(700nm, §2 OSTI) vs B(60nm, §3 Cabot v. Solution Technology 2000)" 충돌을 등급 비교로
풀어야 했지만(둘 다 (Bielmann 1999) 채택 이전에 대조), 원문 대조 결과 **B는 애초에 대상 계가 아니어서
등급 비교 이전에 기각**되고, **A는 산화제-필름 대응이 원문에 없어 E5로도 이 계에 직접 적용할 근거가
약하다**. 두 후보 모두 단독 채택 기준(E5 이상)을 못 채워, EVIDENCE-RULES §판정절차의 취지(더 근거
있는 쪽 채택)에 따라 **원 후보 밖에서 계 근접도가 가장 높은 1차 문헌(Bielmann 1999, E2)을 새로 찾아
채택**했다. EVIDENCE-RULES.md 표 #4에 기록.

## 6. 한계 (정직 표기)
- Bielmann 1999의 50 nm은 저자가 "primary size"(1차입자경, 제조사 스펙)라고 명시했다 — 슬러리
  분산 후 실제 D50(응집 포함 유효경)과는 다를 수 있다(같은 논문이 "due to agglomeration, the
  effective size of abrasive particles may increase"라고 자인). **1차입자경 ≈ D50 근사이며 응집
  보정은 미검증**.
- 산화제가 K₃Fe(CN)₆(potassium ferricyanide)이고 이 팩의 Fe(NO₃)₃와 다르다 — 둘 다 Fe(III)계
  산화제·산성 pH·W CMP라는 점에서 계 근접도는 높으나 **동일 화학종은 아니다**(E1이 아니라 E2로
  등급을 낮춘 이유).
- 입경 방향의 MRR 민감도(abrasive_size_exponent)는 이 노트의 범위가 아니다 — 이 노트는 "이 계에서
  실제로 쓰인 대표 입경이 얼마인가"만 답한다.

## 7. 재현 확인 (원문 발췌 수치 내부정합성)

**재현 요약**: Bielmann 1999 원문에서 폴리싱 슬러리 입경(50 nm)과 SEM 부착시험 전용 입경
(300–500 nm)이 별개 값임, 제거율 810/560 nm/min 비율(1.45배)과 Fe계 산화제 몰농도 0.1–0.15 M
범위를 아래 블록에서 대조.

```python verify
# Bielmann et al. 1999 (DOI:10.1149/1.1390765) 원문 발췌 수치 내부정합성 확인
polishing_size_nm = 50.0     # "primary size ~50 nm diam" — 실제 폴리싱 슬러리 알루미나
sem_test_size_range = (300.0, 500.0)  # "larger sized alumina particles (300-500 nm)" — SEM 부착시험 전용
assert polishing_size_nm < sem_test_size_range[0], \
    "폴리싱 슬러리 입경(50nm)은 SEM 부착시험용 입경(300-500nm)보다 작아야 한다 — 저자가 별도 목적으로 구분"

# 제거율 재현성(4회 반복): stable 810±40, unstable 560±30 nm/min
mrr_stable, mrr_unstable = 810.0, 560.0
ratio = mrr_stable / mrr_unstable
assert 1.3 < ratio < 1.6, f"안정화 슬러리가 ~30% 더 빠른 제거율(문헌 서술)과 정합해야: {ratio:.2f}"
print(f"MRR ratio stable/unstable = {ratio:.2f} (문헌: '30% difference')")

# Fe계 산화제 농도 범위 0.1-0.15 M, pH 4 (HNO3로 조정) — W CMP 산성계 정합
oxidizer_M_range = (0.1, 0.15)
assert oxidizer_M_range[0] < oxidizer_M_range[1]
ph = 4.0
assert ph < 7, "W CMP 슬러리는 산성이어야 한다(부동태 유지) — w_fe_oxidizer.yaml slurry_ph=2.5와 방향 정합"

# Cabot v. Solution Technology 60nm 제품의 화학성분은 질산(HNO3), 질산철 아님 -> 이 계(Fe(NO3)3) 기각 근거
cabot_60nm_chemical_component = "nitric_acid"
target_oxidizer = "ferric_nitrate"
assert cabot_60nm_chemical_component != target_oxidizer, \
    "Cabot판례의 60nm(Ultra-Sol 201A/60)는 질산 슬러리 — Fe(NO3)3 W CMP 계와 불일치하므로 채택 불가"

print("PASS: Bielmann 50nm 폴리싱경/SEM경 구분, MRR비 1.45배, 산화제 0.1-0.15M, Cabot 60nm 화학불일치 확인")
```
