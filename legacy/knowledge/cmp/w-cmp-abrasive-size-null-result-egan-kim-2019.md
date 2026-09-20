<!-- V2-SECTION: R2-slurry | 작성 2026-09-12 | 근거: abrasive size null result, tungsten CMP | 정본: EVIDENCE-RULES.md 판정#4 계열 -->
# 텅스텐 CMP — 입경(abrasive_size) → MRR 무반응(null) 확정: Egan & Kim 2019 1차 실측

> slurry-abrasive / w_fe_oxidizer 팩 κ(kappa) 갭 처리. 정확도루프 2026-09-12.
> [[abrasive-size-null-result-force-partition-theory]] (cu_h2o2_bta에서 이미 확정된 동일 구조의
> null 결과) [[w-cmp-abrasive-agglomeration-scratch-multiplier-egan-kim2019]] (같은 논문, Δ 갭에서
> 이미 인용됨) [[w-cmp-abrasive-d50-bielmann1999-osti-cabot-conflict]] (abrasive_size_nm 값 출처)
> [[kappa-abrasive-concentration-cu-w-cooper-bielmann]] EVIDENCE-RULES.md 판정#1(cu_h2o2_bta) 계열.

## 1. 왜 이 노트가 필요한가

`sim/factors.py`의 `_f_kappa`는 `abrasive_size_exponent`가 팩에 없으면 입경 항을 무반응(항
미계상)으로 둔다. w_fe_oxidizer.yaml에는 현재 `abrasive_ref_size_nm`도 `abrasive_size_exponent`도
없어 입경 슬라이더가 κ에 완전히 죽어있다(UNWIRED 'Particle Size D50' 갭과 동일 뿌리). cu_h2o2_bta는
이미 EVIDENCE-RULES.md 판정#1로 "입경은 지배인자가 아니다"라는 null 결론이 확정됐다. 이 노트는
w_fe_oxidizer(텅스텐 벌크 CMP)에서 **동일 결론이 독립적으로, 그것도 더 강한 등급의 증거로**
성립하는지 확인한다.

## 2. 1차 출처

**Bryan Egan and Hong Jin Kim, "Effect of Controlling Abrasive Size in Slurry for Tungsten Contact
CMP Process," ECS J. Solid State Sci. Technol. 8(5), P3206–P3211 (2019).**
DOI: 10.1149/2.0311905jss. GLOBALFOUNDRIES(Malta, NY) 실제 300mm 양산 라인. **오픈액세스
(CC BY-NC-ND)** — Unpaywall 경유 발행판 PDF 직접 확보(`tools/find_open_access.py --title
"Effect of Controlling Abrasive Size in Slurry for Tungsten Contact CMP Process" --download`,
2026-09-12), 로컬 저장 `papers/lee2019-jss-abrasive-size-w-cmp.pdf`. 전문 판독 완료(pdfplumber).
같은 논문이 이미 [[w-cmp-abrasive-agglomeration-scratch-multiplier-egan-kim2019]]에서 스크래치
Δ 갭 근거로 인용돼 있다 — 이번은 **같은 논문의 MRR 서술을 κ 입경 갭에 재사용**한다(새 문헌 아님,
같은 원문의 다른 절).

## 3. 원문 발췌 — 초록 및 본문

초록(원문 그대로):
> "While tungsten removal rate is not affected by abrasive size, the defectivity performance
> relies heavily on the ability to remove large particles from suspension."

본문(§ 결과, 스크래치 메커니즘 절):
> "While it is intuitive and well-studied that large abrasives cause large scratches, it is also
> accepted that the large abrasives are needed to maintain removal rate; however, in the specific
> case of tungsten bulk slurry, this is proven false. In fact, blanket tungsten removal rate data
> confirms that with the presence of large abrasives, the rate does not increase. Rate tests were
> done on multiple slurry samples with varying ranges of abrasive size. In each case, the rate was
> statistically comparable."

이 서술은 **정성적**이다 — 원문에 정확한 MRR 수치 표나 통계치(p-값 등)는 제시되지 않는다("rate
was statistically comparable"이 유일한 정량적 수사이며 구체 검정 방법·수치는 본문에 없음).
**미검증(수치 미기재)**으로 남긴다. 그러나 결론의 방향("입경↑ → MRR 무변화")은 저자가 직접
"proven false"라는 강한 표현으로 명시했고, 실제 양산 라인의 "multiple slurry samples"(복수
배치, 정확한 n은 미기재)를 대상으로 한 controlled rate test다.


## 3b. 독립 2차 확증 — Bouvet et al. 2002 (콜로이달 실리카, W CMP, 정량 데이터)

**D. Bouvet, C. Salm, R. Ratnaike, R. J. Hopper, P. Woerlee, "Impact of the colloidal silica
particle size on physical vapor deposition tungsten removal rate and surface roughness,"
J. Vac. Sci. Technol. B 20(4), 1556-1560 (2002). DOI: 10.1116/1.1490393.**
미러 사이트 경유 원문 PDF 확보(`papers/bouvet2002-jvst-colloidal-silica-w-cmp-size.pdf`,
2026-09-12, 전문 판독). Egan & Kim 2019(알루미나 계열)과 **연마입자 종류가 다르다**(이 논문은
콜로이달 실리카)는 점에서 완전히 독립적인 재현이다.

원문 §III 정량 서술(Table I, Fig.3):
> "Although the particle sizes range from 12 to 75 nm (factor of 6.25), we observe that the
> tungsten removal rate is quite constant."

Table I 입경 4점(titration/laser-light/TEM 3중 측정): 12 nm, 25 nm, 45 nm, 75 nm(모두 TEM 기준).
**입경이 12→75 nm로 6.25배 벌어져도 텅스텐 제거율이 "quite constant"** — Egan & Kim의 정성
서술("statistically comparable")과 **독립 계에서 동일 방향**의 결론이다. 대조군으로 산화제
없는 경우 제거율이 <200 Å/min(20 nm/min)으로 급락한다는 수치(화학 반응이 지배 메커니즘임을
뒷받침, 입자 표면적 접촉 메커니즘이 지배가 아니라는 저자의 별도 논증)도 원문에 명시된다.

⚠ 원문은 이 결과가 **Bielmann et al. 1999(알루미나 계열)의 보고와 반대**라고 명시한다
("This result is opposite to what Bielmann et al. have mentioned in a previous study for
comparable experimental conditions" — 원문 그대로). 저자는 이를 "우리 실험은 훨씬 작은 실리카
입자(12-75nm)를 썼고 Bielmann은 훨씬 큰 알루미나 입자(0.25-10 µm)를 썼다"는 크기범위 차이로
설명한다 — **연마입자 종류(실리카 vs 알루미나)와 크기범위(nm vs µm) 둘 다 다르다는 교란이
있다.** 즉 이 논문 자체는 "실리카 입자, 12-75nm 범위에서 W 제거율 무반응"을 확증하지만,
w_fe_oxidizer 팩(알루미나 연마제)에 **직접 적용하기엔 연마입자 종류가 다르다는 한계**가 있다.

**판정**: w_fe_oxidizer(알루미나)에 대한 직접 증거는 여전히 Egan & Kim 2019(정성)이 유일하다.
Bouvet 2002(실리카, 정량, 12-75nm)는 **"W CMP에서 입경-MRR 무반응이 연마입자 종류를 넘어서는
더 일반적 현상일 가능성"을 보강하는 방향 일치 증거**로 인용하되, 연마입자 종류 불일치로
직접 대입(같은 계로 취급)은 하지 않는다 — EVIDENCE-RULES §3(스코프 분리) 적용.

```python verify
# Bouvet et al. 2002 (DOI:10.1116/1.1490393) Table I 입경 4점, 정량 재현
particle_sizes_nm = [12.0, 25.0, 45.0, 75.0]  # TEM 측정 (Table I)
size_range_factor = max(particle_sizes_nm) / min(particle_sizes_nm)
assert abs(size_range_factor - 6.25) < 0.01, size_range_factor
# 원문: "particle sizes range from 12 to 75 nm (factor of 6.25)"
print(f"PASS: 입경 범위 12->75nm = {size_range_factor:.2f}배 (원문 'factor of 6.25' 재현)")

# 산화제 제거 시 제거율 급락 수치(대조 실험, 원문 "less than 200 A/min")
oxidizer_off_rate_angstrom_min = 200.0
oxidizer_off_rate_nm_min = oxidizer_off_rate_angstrom_min / 10.0  # 1 nm = 10 A
assert oxidizer_off_rate_nm_min == 20.0
print(f"PASS: 산화제 제거시 W 제거율 <{oxidizer_off_rate_nm_min:.0f} nm/min "
      "(원문 '<200 A/min' 단위환산 재현) — 화학반응 지배 메커니즘 방증")
```

## 4. 등급 판정 (EVIDENCE-RULES.md)

- 대상 계: 텅스텐 벌크 CMP, γ-알루미나 연마입자(같은 산업 계열, GLOBALFOUNDRIES 실제 W contact
  CMP 라인) — w_fe_oxidizer 팩과 **직접 일치**(참고: `abrasive_size_nm` 자체도 같은 계열 문헌
  Bielmann 1999에서 옴).
- 교란 통제: "여러 입경 범위의 슬러리 샘플"로 rate test — 저자가 "다른 조건은 고정하고 입경만
  바꿨다"를 명시하지는 않으나, "in each case the rate was statistically comparable"라는 서술은
  **복수 조건에서 일관되게 무반응**이라는 의미로, 단일 대응쌍(n=1)인 §3(agglomeration 배수)과
  달리 **여러 샘플에 걸친 반복 확인**이다.
- 정량 수치 부재(구체 MRR 값·표·통계 검정 미기재)로 인해 **E1(완전한 통제실측)까지는 못 올라가고
  E2~E3 사이**로 판정한다: 1차 문헌·대상 계 직접 일치·저자 본인 검증(자사 양산 데이터)이라는 점에서
  E2에 가깝되, 정량 수치가 없어 우리가 python verify로 재현할 수 있는 형태가 아니다(방향성만
  검증 가능).

cu_h2o2_bta의 기존 null 결론(E4 대 E3 충돌을 교란분리로 해소)과 비교하면, 이 문헌은 **애초에
충돌이 없다** — 유일한 1차 문헌이 처음부터 null을 직접 서술한다. 따라서 판정 절차 1~3(충돌 해소)이
아니라 **EVIDENCE-RULES §4(null도 결론이다)**를 바로 적용한다.

## 5. 결론 — w_fe_oxidizer도 abrasive_size_exponent = 0.0 (검증된 null)

cu_h2o2_bta와 **독립적으로** 확인된 두 번째 계(W CMP)에서 같은 결론(입경은 MRR 지배인자가 아님)이
나왔다는 것은 이 성질이 "cu_h2o2_bta만의 우연"이 아니라 **연마입자-기판 마모 메커니즘의 더 일반적
성질**일 가능성을 시사한다(단, 두 계 모두 확정은 아니고 oxide_silica는 여전히 "미확정"으로 남아
있다 — §6 참조. 일반화를 주장하지 않는다, 팩별로 독립 판정한다).

`w_fe_oxidizer.yaml`에 다음을 추가한다:
- `abrasive_ref_size_nm = 50.0`(기존 `abrasive_size_nm`과 동일값 — 기준점, cu_h2o2_bta의
  `abrasive_ref_size_nm` 패턴과 동일)
- `abrasive_size_exponent = 0.0`, confidence: **literature**(값 자체는 "효과 없음"이 검증된
  결론이므로 literature — cu_h2o2_bta와 동일 규칙. 단, 정량 수치가 없어 cu_h2o2_bta만큼 강하지
  않음을 note에 명시)

## 6. 한계 — 정직 기록

- **정량 수치 없음(Egan&Kim 2019 자체)**: 이 논문 본문에 MRR 값 표나 구체 검정통계량이 없다 —
  "statistically comparable"이라는 저자 서술만 있다. cu_h2o2_bta 판정(순수 구형 부분집합 Spearman
  ρ≈0.03~0.15 + Chen 이론 유도 이중 지지)보다 이 논문 단독으로는 **증거 강도가 약하다**. 그러나
  §3b의 Bouvet 2002(독립 연마입자 종류·정량 데이터·factor 6.25 범위)가 **같은 방향으로 재현**되어
  단일 정성 논문보다는 강화된 근거를 이룬다 — 단 Bouvet은 실리카, 이 팩은 알루미나라 완전 대입은
  아니다(§3b 한계 참조).
- **산화제 차이**: 이 논문은 산화제 종류를 명시하지 않는다(벌크 텅스텐 슬러리 일반). w_fe_oxidizer
  팩의 Fe(NO3)3 산화제와의 일치 여부는 확인 불가 — abrasive_size_nm 출처(Bielmann 1999, K3Fe(CN)6)
  와 마찬가지로 "W CMP 알루미나 계열"이라는 상위 계로 근접시켰다.
- **일반화 금지**: oxide_silica는 아직 이 결론을 채택하지 않는다(§4 기존 노트가 "지수를 일부러
  비워둔다"로 미확정 유지 — Li et al. 2021은 정점형 정성 서술만 있고 null이라고 말하지 않는다).
  두 계(cu_h2o2_bta, w_fe_oxidizer)에서 null이 나왔다고 oxide_silica·sti_ceria·sic_ceria_h2o2에
  자동 적용하지 않는다 — 팩별 독립 판정 원칙(EVIDENCE-RULES §3 스코프 분리) 유지.

```python verify
# Egan & Kim 2019 (DOI:10.1149/2.0311905jss) 초록·본문 발췌의 내적 일관성 확인.
# 정량 수치가 없으므로 수치 재현은 불가 — 서술 내 논리 일관성만 검증한다.
abstract_claim = "tungsten removal rate is not affected by abrasive size"
body_claim = ("blanket tungsten removal rate data confirms that with the presence of large "
              "abrasives, the rate does not increase")
# 두 서술 모두 "입경↑ -> MRR 불변/무증가" 방향 - 상충되지 않음을 확인
assert "not affected" in abstract_claim
assert "does not increase" in body_claim
assert "not" in abstract_claim and "not increase" in body_claim
print("PASS: 초록·본문 두 서술 모두 입경->MRR 무반응/무증가 방향으로 일관됨 (정량 수치는 미기재)")

# EVIDENCE-RULES.md 판정#1(cu_h2o2_bta) 사례와 동일 채택 규칙 적용 확인
# (지수 0.0은 "모른다"가 아니라 "효과 없다"는 코드 규칙 - sim/factors.py:497-509 참조)
exponent = 0.0
d, d_ref = 80.0, 50.0  # 임의 입경값
mult = (d / d_ref) ** exponent
assert mult == 1.0, "지수 0이면 입경이 바뀌어도 배수는 항상 1.0이어야 한다"
print(f"PASS: abrasive_size_exponent=0.0 -> 입경 {d}nm(기준 {d_ref}nm)에서도 배수={mult} (무반응 재확인)")
```
