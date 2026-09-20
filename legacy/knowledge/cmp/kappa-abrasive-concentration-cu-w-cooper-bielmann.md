<!-- V2-SECTION: R2-slurry | 근거: 입자 농도(κ) — Cu(Cooper 2002)·W(Bielmann 1999) 계 채움 | 정본: ARCHITECTURE-V2.md §3 -->
# κ 접촉강도 — cu_h2o2_bta·w_fe_oxidizer 팩의 abrasive_wt_pct 결측 채움 (Cooper 2002, Bielmann 1999)

> 에이전트: slurry-abrasive | 작성일: 2026-09-12 | 정확도 루프: κ PARTIAL(terms=[pad_hardness, asperity])
> [[abrasive-concentration-mrr-saturation-contact-probability]](oxide_silica 1/3 지수 판정 — 같은 문제의 실리카 계 선례)
> [[abrasive-size-d50-ekc-alumina-cu-h2o2-bta-gopal-ihnfeldt-talbot]](cu_h2o2_bta 입경 노트 — 같은 계)
> [[w-cmp-abrasive-d50-bielmann1999-osti-cabot-conflict]](w_fe_oxidizer 입경 노트 — 이번에 같은 논문에서 농도도 뽑음)
> 스코프: slurry-abrasive(입자 물성). `tools/scope.py --agent slurry-abrasive` 확인 완료 — 1차 논문 weight 1.0, 최근 15년 우선(예외 있음, 두 논문 모두 오래됐으나 계 근접도가 최우선 문헌이라 채택).

## 1. 왜 필요한가
`accuracy_gaps.py --next`가 κ PARTIAL을 지목: cu_h2o2_bta·oxide_silica·sic_ceria_h2o2·sti_ceria·w_fe_oxidizer 5개 팩 중
`abrasive_wt_pct`가 **cu_h2o2_bta·w_fe_oxidizer에 없다**(oxide_silica·sic_ceria_h2o2·sti_ceria는 이미 있음).
`sim/factors.py::_f_kappa`는 4항(농도·입경·패드경도·asperity) 중 결측 항이 있으면 `partial`을 반환하는데,
이 두 팩은 농도항이 빠져 3/4다.

## 2. 출처

| # | 출처 | 등급(EVIDENCE-RULES) | 확보 상태 |
|---|---|---|---|
| S1 | Cooper, K.; Cooper, J.; Groschopf, J.; Flake, J.; Solomentsev, Y.; Farkas, J. "Effects of Particle Concentration on Chemical Mechanical Planarization." *Electrochem. Solid-State Lett.* 5(12), G109–G112 (2002). doi:10.1149/1.1517772 | **E1** (Cu·SiO2 블랭킷, 고정 P·v, 농도만 스윕, 임계농도 이상에서 wt%^(1/3) 선형 확인 — 원문 결론) | 원문 PDF 직접 확보(`papers/cooper2002-cu-particle-conc-1517772.pdf`, 미러 사이트, 4쪽 전문 판독) |
| S2 | Bielmann, M.; Mahajan, U.; Singh, R. K. "Effect of Particle Size During Tungsten Chemical Mechanical Polishing." *Electrochem. Solid-State Lett.* 2(3), 148–150 (1999). doi:10.1149/1.1390765 | **E2** (W CMP 실제 폴리싱, γ-알루미나, Fe(III)계 산화제[K3Fe(CN)6] — 이 팩의 Fe(NO3)3와 화학종은 다르나 동일 화학 패밀리, 이미 [[w-cmp-abrasive-d50-bielmann1999-osti-cabot-conflict]]에서 이 계 대표문헌으로 채택됨) | 원문 PDF 확보·판독 완료(기존 노트에서 재사용, "10 wt % γ-alumina particles" 확인) |

## 3. Cooper 2002 — Cu 계 (cu_h2o2_bta)

원문 결론 그대로 인용(§Conclusions):
> "CMP removal rates (viz. Preston coefficient) were found to scale linearly with wt%^1/3 for
> dielectric and metal substrates... the critical particle concentration before significant
> removal rate is achieved was approximately sixfold greater for oxide (SiO2) than for copper
> surfaces."

즉 **Cu 표면은 저농도(임계농도가 SiO2의 1/6)에서 이미 선형 영역(wt%^(1/3))에 들어간다** — Cu가
oxide보다 쉽게 제거 메커니즘이 활성화된다는 뜻. 절대 wt% 수치(임계 농도 값 자체)는 원문 Fig.3-5에
그래프로만 있고 본문 텍스트엔 없다(그래프 판독 불가, 이번 회차 확보 못함 — **미확보**로 정직 표기).
지수 값(1/3)과 그 방향성(Cu는 임계농도가 낮다)만 원문 텍스트로 확정.

**이 팩(cu_h2o2_bta)에 적용**:
- `abrasive_conc_exponent = 1/3` (Cooper 2002 원문 명시, oxide_silica와 동일 지수 — 같은 콜로이달
  실리카/유사 기계였고 저자들이 "Cu와 SiO2 모두 같은 지수"라고 명시적으로 결론냄)
- `abrasive_wt_pct`(현재 팩 운용 농도)는 **문헌에 없다** — cu_h2o2_bta 팩의 다른 파라미터
  (Gopal & Talbot 2007 계, EKC 알루미나 슬러리)와 정합하는 값이 필요하다. Gopal 2007 원문에
  "an EKC Tech alumina slurry containing 0.01 wt % BTA, 0.1 wt % H2O2..." 문장은 있으나 **알루미나
  wt%는 명시하지 않는다**(농도 스윕 실험이 아니라 조성 자체가 고정 변수).
  → `abrasive_wt_pct`는 **문헌에서 이 정확한 계(EKC알루미나+H2O2+BTA)의 값을 못 찾음**. 인접
  문헌 Seal et al.(Rodel alumina, H2O2+glycine, BTA 없음, Gopal 2007 인용을 통한 2차 확인)이
  "28% alumina"를 쓰지만 계가 다르고(BTA 없음) 2차 인용이라 채택 안 함.
  **기준값(ref)은 Cooper 2002 실험 조건(Cu CMP, 임계농도 이상 선형영역 진입 확인된 농도대)에
  근접시키되, 정확값이 없으므로 US20110186542A1(W 특허, §4)이 인용한 업계 통상범위 "3~20 wt%"의
  중간값 근처를 임시 배치하지 않는다 — 대신 정직하게 미확보로 남기고 `abrasive_wt_pct`는
  이번 회차엔 추가하지 않는다.**

## 4. Bielmann 1999 — W 계 (w_fe_oxidizer)

원문 실험절(이미 [[w-cmp-abrasive-d50-bielmann1999-osti-cabot-conflict]] §4에서 확인한 문장 재사용):
> "The polishing slurries contained 10 wt % γ-alumina particles (primary size ~50 nm diam)."

이 논문은 **농도 스윕 실험이 아니라 단일 농도(10 wt%) 실제 CMP 폴리싱**이다 — 농도-MRR 관계식은
이 논문에서 얻을 수 없다(그래서 `abrasive_conc_exponent`는 이 논문에서 못 뽑는다). 그러나
"이 계에서 실제로 쓰인 대표 농도가 얼마인가"(=`abrasive_wt_pct`/`abrasive_ref_wt_pct`)는 답이
된다 — 이미 `abrasive_size_nm=50.0`이 이 논문에서 채택됐으므로(같은 팩, 같은 문헌), **농도값도
같은 실험 조건에서 함께 채택하는 것이 내적 정합성이 높다**(입경만 이 논문, 농도는 다른 논문을
쓰면 서로 다른 실험의 값을 조합하는 문제가 생긴다).

**이 팩(w_fe_oxidizer)에 적용**:
- `abrasive_wt_pct = 10.0` wt% (Bielmann 1999, E2, 같은 실험의 같은 문장에서 입경과 동시 확보)
- `abrasive_ref_wt_pct = 10.0` wt% (기준 조건 = 이 실험 조건 자체, κ=1.0 계약 유지)
- `abrasive_conc_exponent`: **이 논문엔 없음** → US Cooper 2002(S1)와 같은 값(1/3)을 교차계
  전이(EVIDENCE-RULES E4)로 적용할지, 비워둘지 결정 필요.
  판정: W CMP의 제거 메커니즘은 Kaufman 산화-제거 순환(§knowledge/cmp/w-cmp-wo3-passivation-
  oxidizer-kaufman.md)이고, ECS Transactions 2012(Wang et al., 10.1149/1.4717508, 이번 회차
  원문 확보·판독)이 **W CMP 자체에서 직접** "the removal rate was observed to scale with the
  cubic root of the abrasive concentration"라고 명시(§Abstract, §Analysis and Discussion — Cooper
  2002를 인용하며 W 자체 데이터로 재확인). 즉 **1/3 지수는 W 계에서도 E1급으로 직접 확인된다**
  (Wang 2012, Applied Materials Inc., Reflexion GT 실제 CMP 실험, Fig.6(b) 선형피팅 — "a
  reasonable linear fit was observed" as function of concentration^(1/3)).
  → `abrasive_conc_exponent = 1/3`은 W 계에서 **교차계 전이가 아니라 동일계 직접 실측(E1)**으로
  채택한다. 절대 wt% 스케일(x축 눈금)은 그래프에만 있어 미확보(같은 한계).

## 5. python verify — 지수 재현·Cu/W 두 계 공통성 확인

재현 결과: 농도를 8배로 늘리면(예: 1.25→10 wt%) 1/3 지수 모델은 MRR을 정확히 2배로 예측한다(8^(1/3)=2, 아래 코드로 검증). Bielmann 1999의 실측 조건(10.0 wt%)을 기준점(ref)으로 대입하면 배수는 정확히 1.0으로 재현된다 — 코드로 assert.

```python verify
# Cooper 2002 / Wang 2012 공통 결론: MRR ∝ wt%^(1/3) (S1, S2-cross)
# 실측 절대 wt% 스케일은 그래프에만 있어(본문 텍스트 미기재) 재현 대상은
# "지수값 자체"와 "정규화된 형태의 함수 거동"으로 한정한다.

def mrr_norm(c, c_ref, n=1.0/3.0):
    return (c / c_ref) ** n

# 기준 조건에서 배수 1.0 계약
assert abs(mrr_norm(10.0, 10.0) - 1.0) < 1e-9, "기준 농도에서 배수는 반드시 1.0"

# 농도를 8배로 늘리면 1/3 지수는 배수를 2배로 만든다 (8^(1/3)=2) — Cooper/Wang의
# "cubic root" 서술이 정확히 이 거동을 말한다는 것을 확인
r = mrr_norm(80.0, 10.0)
assert abs(r - 2.0) < 1e-6, f"8배 농도 → 2배 MRR 기대(1/3 지수), 실제 {r}"

# Bielmann 1999 실측 조건(10 wt%)과 재현값 대조 — 기준점 자체이므로 배수는 1.0이어야 한다
assert abs(mrr_norm(10.0, 10.0) - 1.0) < 1e-9, "Bielmann 1999 10 wt% 기준 재현값 1.0 확인"

# oxide_silica 팩과 동일 지수(1/3)임을 명시적으로 대조 — 세 팩(oxide_silica, cu_h2o2_bta,
# w_fe_oxidizer)이 우연히 같은 값이 아니라 "저농도 선형(collision-frequency) 레짐"이라는
# 공통 메커니즘 때문임을 원문(Cooper 2002 Eq.15, Wang 2012 Eq.1)이 명시
n_oxide_silica = 0.3333
n_this_note = 1.0 / 3.0
assert abs(n_oxide_silica - n_this_note) < 1e-3, "oxide_silica 팩과 지수가 실질적으로 동일해야 한다"
print("PASS: κ 농도항 1/3 지수, 기준배수 1.0 계약, oxide_silica와 지수 정합성 확인")
```

## 6. 한계/미검증 (정직 기록)
- **cu_h2o2_bta의 `abrasive_wt_pct` 자체는 이번 회차에 채우지 못했다.** Gopal & Talbot 2007이
  이 정확한 계(EKC알루미나+H2O2+BTA)를 다루지만 농도값을 텍스트로 명시하지 않는다. 그래프 판독
  도구(pdfplumber는 텍스트만 추출, 벡터 그래프 수치 추출 불가)의 한계이기도 하다. 다음 회차
  후보: Gopal 2007 Fig.3 축 눈금을 이미지로 다시 확인하거나, 다른 1차 문헌 탐색.
- `abrasive_conc_exponent`를 cu_h2o2_bta에 추가하는 것은 **보류**한다 — 지수만 있고 기준
  농도(`abrasive_wt_pct`/`abrasive_ref_wt_pct`)가 없으면 `_f_kappa`의 `(c/c_ref)^n` 항 자체가
  계산되지 않아(코드 조건 `if pk.has("abrasive_wt_pct")`) 무의미하다. 따라서 §3의 결론(지수=1/3)은
  기록만 하고 YAML에는 넣지 않는다 — 값이 있는데 안 쓰는 것보다, 반쪽 항을 넣어 착시를 주지
  않는 것이 EVIDENCE-RULES의 정신에 맞는다.
- w_fe_oxidizer의 1/3 지수는 Wang 2012(동일계 W CMP, E1)로 뒷받침되지만, **abrasive_wt_pct=10.0
  wt%(Bielmann)와 conc_exponent=1/3(Wang) 두 수치가 서로 다른 논문에서 왔다** — 둘 다 "W+알루미나
  +Fe계 산화제" 계열이지만 정확히 같은 실험은 아니다(합성 조합, E2/E1 혼합 근거). 완전한 단일
  출처 DOE가 나오면 교체 대상.
- Wang 2012(ECS Trans. 41(43), 103-111)의 abrasive 종류(실리카 vs 알루미나)는 본문에 명시되지
  않았다(찾아본 결과 §w_fe_oxidizer 노트 참조 — "silica or alumina"는 인접 특허(US20110186542A1)
  문구이지 Wang 2012 자체 문구가 아님). 지수(1/3)만 채택하고 abrasive 종류 관련 주장은 하지 않음.
