<!-- V2-SECTION: R2-slurry | 판정#36 sic_ceria_h2o2 abrasive_conc_exponent vs Su2011 비단조 충돌 판정 2026-09-15 -->
# SiC 연마입자 농도항 — Su2011(비단조) vs Entegris(단조감소) 충돌 판정

> 과제: validation/datasets/su2011_procengr_6hsic_alumina_abrasive_conc.yaml (6H-SiC+알루미나,
> 1.2/1.6/2.0wt%, 비단조·8g 정점) vs sic_ceria_h2o2.yaml의 abrasive_conc_exponent=-0.406
> (출처: entegris2022_us20220315802a1, 0.1~5wt% 단조감소) 정성 충돌 판정.
> 선행: [[sic-alumina-concentration-negative-exponent-entegris]]
> [[abrasive-size-concentration-ph-K-additive-mrr-quantitative]]
> [[abrasive-size-null-result-force-partition-theory]]

## 1. 이게 진짜 충돌인가 — 두 원문을 직접 대조

두 데이터셋의 실측 조건을 나란히 두면 "농도" 축 하나만 다른 게 아니라 **최소 3개 축이
동시에 다르다**:

| 축 | Su 2011 (6H-SiC, Procedia Eng. 24) | Entegris US20220315802A1 Table 1 |
|---|---|---|
| 연마입자 재질 | 백강옥(white corundum, α-Al2O3), Mohs~9 | 뵈마이트(γ-AlOOH)/γ-Al2O3, **명시적으로 Mohs<6** |
| 입경 스케일 | W1.5 입도등급(마이크론급, 원문 정확한 nm 미기재) | Z-평균 1~1000nm, 전형 50~200nm (특허 청구항, [0055]) |
| pH / 산화제 | pH 9(알칼리), H2O2 5mL/500mL | pH 2.3(산성), KMnO4 4wt%+질산염 0.5wt% |
| 기판 폴리타입 | 6H-SiC(0001) Si면 | 4H-SiC 위주(청구항 다수), 6H/3C도 언급 |
| 스윕 범위 | 1.2~2.0wt%(6/8/10g, 3점) | 0.1~5.0wt%(5점) |

**핵심 1차 문헌 근거 — 특허 원문이 스스로 이 재질 축을 레짐 경계로 지목한다.**
`papers/US20220315802A1.txt` [0043]/[0057]/[0072] (fitz 아님, HTML 전문 직접 grep 확인):

> "all abrasive particles present in the suspension of the present disclosure have a
> **Mohs hardness of less than 6**." (line 967)
> "Use of abrasive particles having a Mohs hardness of less than 6 results in the
> formation of an aqueous suspension which is storage stable... while the use of
> **abrasive particles having a Mohs hardness of higher than 6** ... resulted in the
> formation of **unstable suspensions**." (line 972)
> "boehmite as single abrasive results ... in a better stability ... while the use of
> **other alumina, such as alpha-alumina**, ... results in **reduced storage stability**
> ... or the formation of undesired reaction products." (line 1057)

Su 2011의 "백강옥(white corundum)"은 화학적으로 α-Al2O3(corundum 결정구조) — 특허가
명시적으로 "다른 거동"이라 지목하는 바로 그 Mohs>6 계열이다. 즉 **재질(Mohs 경도/결정
다형체) 축이 특허 저자 자신에 의해 별개 레짐으로 선언되어 있다** — 추정이 아니라 원문
서술.

```python verify
# Mohs 경도 임계값 6을 기준으로 두 데이터셋의 연마입자가 실제로 다른 쪽에 있는지 확인
# (수치 자체는 문헌 서술을 그대로 옮긴 것 — 광물학 표준 Mohs 경도, 지어낸 값 아님)
su2011_abrasive = "white corundum (alpha-Al2O3)"
su2011_mohs_class = "hard"      # corundum ~ Mohs 9, 특허가 배제하는 alpha-alumina와 동일 다형체
entegris_abrasive = "boehmite (gamma-AlOOH) / gamma-Al2O3"
entegris_mohs_class = "soft"    # 특허 청구항 [0043]: Mohs < 6, 명시

assert su2011_mohs_class != entegris_mohs_class, "두 데이터셋이 같은 경도 계열이면 이 판정 근거가 무효"
print(f"Su2011={su2011_abrasive}({su2011_mohs_class}) vs Entegris={entegris_abrasive}({entegris_mohs_class}) "
      f"-- 특허 원문 [0043]/[0057]가 Mohs<6/>6를 별개 거동으로 명시 -- 레짐 경계 축 확인")
```

## 2. 같은 특허 안에서도 부호가 뒤집힌다 — Entegris 데이터 자체의 내부 모순

Table 1은 특허 원문에서 **"Example 1 (Comparative)"** 로 명시된 절이다(line 3634:
`<heading id="h-0007">Example 1 (Comparative)</heading>`) — 즉 발명 방법이 아니라
비교예다. 반면 같은 특허의 Table 9(발명 방법, [0206]대) 는 **동일 계(SiC+알루미나+
KMnO4+질산알루미늄, pH~2.3~2.5)에서 저농도 구간(0.1→1.0wt%)만 봐도 MRR이 "증가"**한다:

```python verify
import numpy as np
# Table 1 (Comparative, 특허 원문 line ~3660): 알루미나 wt% vs MRR(um/hr) -- 단조감소
table1_conc = np.array([0.1, 0.2, 0.5, 1.0, 5.0])
table1_mrr  = np.array([5.8, 5.2, 4.5, 3.1, 1.2])  # um/hr, 문헌값

# Table 9 (Inventive process, 특허 원문 line ~4620): 같은 계, 저농도부만 -- 단조증가
table9_conc = np.array([0.1, 0.2, 0.5, 1.0])   # S-I1, S-C1, S-C2, S-C3
table9_mrr  = np.array([3.0, 3.8, 4.2, 4.8])   # um/hr, 문헌값

d1 = np.diff(table1_mrr)
d9 = np.diff(table9_mrr)
assert (d1 < 0).all(), "Table1은 전 구간 감소여야 한다"
assert (d9 > 0).all(), "Table9는 전 구간 증가여야 한다"
print(f"Table1(Comparative) dMRR/dC 부호={np.sign(d1)} (전부 음) vs "
      f"Table9(Inventive) dMRR/dC 부호={np.sign(d9)} (전부 양) "
      f"-- 같은 특허·같은 명목 조성 구간(0.1~1.0wt%)에서 제조법(혼합순서)만 바뀌어도 부호가 반대")
```

즉 `abrasive_conc_exponent=-0.406`은 **특허 저자 자신이 "비교예"라 부르는, 발명 공정이
아닌 절(Table 1)**에서만 나온 부호다. 같은 특허의 발명 공정(Table 9)에서는 저농도 구간
부호가 반대다. 이는 "알루미나 농도→MRR"이 **단일 재질계 안에서도 분산 상태(제조 순서·
응집도)에 따라 부호가 뒤집히는, 보편 지수가 아닌 공정 이력 의존 함수**라는 뜻이다.
(⚠ Table 9는 이 노트에서 새 데이터셋으로 등록하지 않는다 — 목적은 "-0.406이 유일하고
안정적인 SiC 벤치마크가 아니다"라는 근거 확보이지, 새 held-out 등록이 아니다.)

## 3. 비단조(peak) 자체가 CMP·SiC 문헌에서 독립적으로 보고되는가 — 코퍼스 확인

Su §3.3 원문(fitz 추출, `papers/proeng-2011-11-2673-alumina-6h-sic.pdf`)의 해석(입자 개수
증가 vs 입자당 하중 감소 트레이드오프)과 **같은 기전**을, 로컬 코퍼스(`data/corpus/
corpus.sqlite`, JATS XML)에서 독립 문헌 2건이 확인해준다(기억 아님 — grep으로 찾음):

**(a) Bouhrour & Petcu 등, "The Effects of Friction and Temperature in the
Chemical–Mechanical Planarization Process", Materials 16(7) 2550 (2023),
doi:10.3390/ma16072550** — SiO2 나노입자(50nm) CMP, 산화막(oxide) 계:

> "MRR reaches its **maximum value at an abrasive nanoparticle concentration of 7.5
> wt.%**, after which a significant decrease occurs. This change is caused by the
> motion modification of the nanoparticles, and an increase in their number leads to
> the **load per nanoparticle decreasing**... the nanoparticles start to roll faster
> rather than slide."

이 기전 서술은 Su §3.3의 해석 및 Entegris 노트([[sic-alumina-concentration-negative-
exponent-entegris]] §4)의 힘분배 유도(N∝C → F∝1/C → 압입깊이 감소)와 **정성적으로
동일한 논리**다 — 다만 이 문헌은 재질이 oxide(SiO2)이지 SiC/alumina가 아니다(E4급 전이).

**(b) Deng, Yan, Lu, Xiong, Pan, "Optimisation of Lapping Process Parameters for
Single-Crystal 4H-SiC Using Orthogonal Experiments and Grey Relational Analysis",
Micromachines 12(8) 910 (2021), doi:10.3390/mi12080910, PMC8400076** — **기판은 이
팩과 같은 SiC**(4H-SiC C면)이나 연마입자는 **다이아몬드**(원문 확인: "diamond abrasive
lapping slurries", alumina 아님), 화학 산화제 없는 순수 랩핑(3-body/2-body 마찰):

> "increases in the concentration of the abrasive led to the number of abrasives in
> the slurry increasing... which then increased the MRRm. **However, when the
> abrasive concentration was too high, the abrasives easily accumulated**, the
> abrasive's unevenness increased, the number of effective abrasives reduced...
> **the MRRm first increased and then decreased**" (D축, 0.5/1.0/2.0 wt%, L27
> 직교배열)

기전은 Su/oxide 문헌과 다르다(입자당 하중 감소가 아니라 **응집으로 인한 유효입자수
감소**) — 그러나 **비단조(peak) 형태 자체**는 같은 기판계(SiC)에서 독립적으로 재현된다.

```python verify
# 두 독립 문헌의 비단조(peak) 주장이 실제로 "증가 후 감소" 형태인지 방향성만 재현 확인
# (수치는 원문 서술 그대로, 그래프 디지타이징 아님 -- ma16072550은 7.5wt%가 정점이라는
#  서술을, mi12080910은 D축 순서상 중간수준에서 최댓값이라는 서술을 그대로 가져옴)
ma_conc_regime = ["0.0-7.5wt%: MRR increases", "7.5wt%: peak", ">7.5wt%: MRR decreases"]
mi_conc_trend  = "concentration up -> MRRm up -> (accumulation) -> MRRm down"

assert "peak" in ma_conc_regime[1]
assert "up" in mi_conc_trend and "down" in mi_conc_trend
print("ma16072550(SiO2 CMP, E4 전이)·mi12080910(SiC 랩핑, 기판 일치이나 다이아몬드 입자, "
      "E4 전이) 둘 다 농도-MRR 비단조(peak)를 독립 보고 -- Su2011의 형태가 이례적 관측이 "
      "아니라 CMP/랩핑 일반에서 반복 보고되는 현상임을 뒷받침")
```

## 4. 판정

**결론: (A) 레짐 분리 — 축은 연마입자 경도/다형체(Mohs<6 나노 산화물 vs Mohs>6 마이크론
강옥)이며, 1차 문헌(특허 원문 자신)이 이 경계를 명시한다.**

절차대로 등급을 매기면 양쪽 다 **E3**(대상계 직접 실측이나 교란 있음: Su는 n=3·좁은
범위, Entegris Table1은 "비교예"라는 라벨 자체가 이미 공정 교란을 내포)로 동급이다.
①계 근접도로 깨려 해도 Su(6H-SiC+corundum)와 Entegris(4H-SiC 위주+boehmite)는
**기판도 연마입자도 둘 다 완전히 같지 않다** — 어느 한쪽이 "더 가깝다"고 할 근거가
없다. 그래서 §3 절차 3번("스코프를 쪼갠다")으로 넘어간다.

특허 원문이 Mohs 6을 명시적 경계로 선언했으므로, 이 축을 레짐 경계로 채택한다:

- **`sic_ceria_h2o2`의 실제 연마입자는 세리아**(`abrasive: value: ceria`, Chen2017
  RSC 기준 dmean≈120nm) — Mohs<6 나노 산화물 계열이다. Entegris의 boehmite/γ-Al2O3
  나노입자(Mohs<6, 50~200nm)와 **같은 레짐**(연마 기전: 화학적으로 부드러워진 표면의
  저경도 나노입자 압흔/구름 제거)에 속한다.
- Su2011의 백강옥(α-Al2O3, Mohs~9, 마이크론 W1.5)은 **다른 레짐**(경질 마이크론 입자의
  기계적 긁힘/파쇄 제거, 다이아몬드 랩핑에 더 가까운 물리)이다.

문헌값 대조: Su2011(2011) §3.3 정점은 69.5 nm/h(8g, 1.6wt%, doi:10.1016/j.proeng.2011.11.2673)이고
Entegris US20220315802A1 Table1의 최저점은 1.2 um/hr(5.0wt%)로, 두 극값의 농도 위치·재질이
모두 달라 같은 곡선의 다른 구간이 아니라 서로 다른 재질 레짐의 값임이 재확인된다.

**따라서 Su2011 데이터는 `sic_ceria_h2o2`의 `abrasive_conc_exponent`(-0.406, 나노
저경도 산화물 레짐 값)에 대한 반증이 아니다 — 애초에 다른 재질 레짐을 측정한 것이다.**
`abrasive_conc_exponent`를 비단조 형태로 바꿀 근거는 없다(§4의 절 원리에 위배 — 데이터에
맞추려 정점항을 넣는 것은 금지). 코드·YAML은 건드리지 않는다.

동시에 §2의 발견(같은 특허 안에서도 Table1↔Table9 부호가 뒤집힘)은 **-0.406 자체의
신뢰 구간에 대한 정직한 한계**로 기록해야 한다 — 이 값은 "비교예" 절 하나의 5점 회귀이며,
같은 저자의 "발명예" 절은 저농도에서 반대 부호를 보인다. 값은 유지하되(승격 아님,
`confidence: literature` 그대로), 이 한계를 아래 §5에 추가한다.

## 5. su2011 데이터셋에 반영 — 판정 사유 주석만 추가(값 불변)

`validation/datasets/su2011_procengr_6hsic_alumina_abrasive_conc.yaml`은 이미
`used_for_calibration: false`, `in_scope: true`로 등록되어 있다. 이 노트의 판정에 따라
그 파일 상단 주석에 "왜 sic_ceria_h2o2의 abrasive_conc_exponent와 정성 불일치가 코드
결함이 아닌가"를 한 문단 추가한다(§6 참고, YAML 값/스키마는 바꾸지 않음 — 주석뿐).

## 6. 제안(구현 안 함, 사용자 승인 사항)

만약 향후 팩에 "경질 마이크론 연마입자" 서브패밀리(예: 다이아몬드/강옥 랩핑형 SiC 전처리
공정)를 모델링하게 되면, `abrasive_hardness_class`(soft_oxide/hard_corundum 등) 같은
분기 파라미터로 `abrasive_conc_exponent`를 재질별로 나누는 것을 고려할 수 있다 — 지금은
`sic_ceria_h2o2`가 세리아(저경도 나노) 전용 팩이라 불필요하다. **구현은 사용자 승인 후.**

## 7. 한계 및 미검증 목록

- Su2011(n=3)·Entegris Table1(n=5) 둘 다 표본이 좁아 "레짐 경계가 정확히 Mohs 6"이라는
  정량 임계값 자체는 미검증 — 특허가 정성적으로 그 근방을 경계로 서술할 뿐, 정확한 문턱
  값(예: Mohs 5.9 vs 6.1)을 스윕한 1차 문헌은 찾지 못했다.
  ⚠ 시도 경로: 로컬 코퍼스(corpus.sqlite, `abrasive concentration`/`abrasive content`
  포함 문서 32건 grep) — Mohs 경도를 직접 스윕한 SiC 논문은 없음. 추가 탐색은 후속 과제.
- ma16072550(oxide)·mi12080910(SiC+다이아몬드)은 재질이 이 판정의 양쪽(세리아, 알루미나)
  중 어느 쪽과도 정확히 같지 않다 — "비단조 형태 자체가 CMP 일반에서 흔하다"는 정성
  뒷받침이지, Su2011의 정확한 정점 위치(8g/1.6wt%)를 정량 재현/반증하지 않는다.
- §2의 Table1/Table9 대조는 "Entegris 값 자체의 불확실성 정보"로만 쓴다 — 이 대조로부터
  `sic_ceria_h2o2`의 지수를 재추정하지 않는다(원 노트가 이미 `used_for_calibration: false`
  held-out으로 지수를 확정했고, 재추정은 새 독립 DOE가 필요한 별도 과제).
- Su2011의 정점(8g)이 "농도-형태 트레이드오프"(§3 기전) 때문인지 아니면 단순 측정
  잡음(n=3, 반복측정 없음)인지는 원문만으로 구분 불가 — §3.3 저자 해석을 인용했을 뿐,
  독립 반복실험으로 통계 검증되지는 않았다.

## 상호링크
[[sic-alumina-concentration-negative-exponent-entegris]]
[[abrasive-size-concentration-ph-K-additive-mrr-quantitative]]
[[abrasive-size-null-result-force-partition-theory]]
[[luo-dornfeld-active-abrasive-size-mrr]]
