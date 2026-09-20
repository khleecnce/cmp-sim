# cu_alkaline_benzenesulfonic — 연마입자 축(κ 입경/농도 지수, Δ D99·손상지수) 판정

> 판정#71, 2026-09-19. 완성격자 미충족 3칸(C1 Δ · C2 κ · C2 Γ) 전진 과제.
> 선행: [[abrasive-size-null-result-force-partition-theory]] [[delta-damage-model-synthesis]]
> [[delta-scratch-damage-d99-oversize-particle-model]] [[abrasive-particle-size-distribution-d99-tail]]
> [[abrasive-concentration-mrr-saturation-contact-probability]] [[gamma-conditioning-load-confidence-basis]]

## §1 팩 정체성

`cu_alkaline_benzenesulfonic`은 2026-09-19 `cu_h2o2_bta`에서 갈라 나온 신설 팩이다
(`knowledge/params/cu_alkaline_benzenesulfonic.yaml` 헤더 주석 참조). 정의 문헌은
US9200180B2(Air Products / 현 Versum·Merck) 1건이며, 이 팩의 알칼리 pH 항
(`cu_ph_alkaline_k`=0.3329)·산화제 부동태 항(`oxidizer_passivation_K`=0.8232)이
이미 이 특허 TABLE 4·TABLE 2에서 역산돼 있다. 이번 과제는 같은 특허에 인쇄된
**연마입자 실측 스펙**을 마저 배선하는 것이다.

부모(cu_h2o2_bta)와의 차이:

| | cu_h2o2_bta(부모) | cu_alkaline_benzenesulfonic(이 팩) |
|---|---|---|
| pH | 4 (산성) | 9 (알칼리) |
| 억제제 | BTA 1 mM | 없음 |
| 연마입자 | 알루미나(EKC, D50 100 nm) | 콜로이달 실리카(K-안정, D50 50-60 nm) |
| 착화제 | 글리신 1 wt% | 없음(벤젠술폰산이 Ta 착화제 겸 산화제) |
| 막 | Cu | Cu(동일) |

막(Cu)은 그대로이고 연마입자 재료와 슬러리 화학이 바뀌었다는 것이 이하 모든 판정의
축이다 — 이 구분(막 vs 재료 vs 화학)이 §3·§6에서 반복해서 등급을 가른다.

## §2 입경 1차 출처 (US9200180B2 원문)

로컬 사본 `papers/patents/US9200180B2.html`을 직접 열어 재확인(grep 결과를 그대로
받지 않고 원문 문맥을 직접 대조):

```
COMPONENTS 목록(명세서 실시예 도입부):
A) Benzenesulfonic acid: Aldrich Chemical Company
B) Hydrogen Peroxide: 30 wt% 용액, Air Products and Chemicals
C) Potassium Hydroxide: Aldrich Chemical Company
D) Potassium-stabilized colloidal silica: DuPont Air Products NanoMaterials L.L.C.
   "an approximately 30 weight % potassium-stabilized dispersion in water with a
    particle size of 50-60 nanometers as measured by Capillary Hydro-Dynamic Flow
    using a Matec Applied Sciences model number CHDF 2000 instrument."
```

**어느 실시예에 쓰였는가**: 이 COMPONENTS 목록은 "실시예 전체에 공통으로 쓰인
성분 사전"이다 — 성분 D) 하나만 있고, 실시예별로 다른 입경의 실리카를 쓴다는
서술이 어디에도 없다. 원문 전수 검색(`re.sub`로 태그 제거 후 grep) 결과
"ABRASIVES"·"abrasive"라는 절 표제 자체가 없고, "50-60 nanometer silica described
in the examples"(Detailed Description 결론부)라는 표현이 **모든 실시예가 이 실리카
하나를 쓴다**는 것을 재확인한다. 즉:

> **US9200180B2는 입경을 스윕하지 않는다.** 실시예 1~23 전체가 성분 D)
> 하나만 쓴다. 이것이 §3의 판정 (c)의 전제가 된다.

같은 단락(Detailed Description)에 일반 서술도 있다("median weight average
particle size ... 7 nm to about 400 nm, preferably 20~200 nm") — 이건 청구범위
수준의 포괄 서술(마쿠쉬형)이지 실시예 실측치가 아니므로 채택하지 않는다(SCOPE.yaml
"청구범위 나열값 금지"). 실측치는 성분 D)의 CHDF 50-60 nm 하나뿐이다.

이 팩의 `kp_m_per_pa`·`cu_ph_alkaline_k`가 역산된 TABLE 4 Examples 15-19도 이
성분 D) 실리카 10 wt%를 쓴다(팩 yaml 기존 주석에 이미 명시) — 즉 입경 값과 Kp
역산 조건이 동일 실시예군이라 이중 계상 문제가 없다.

```python verify
import re
html = open("papers/patents/US9200180B2.html", encoding="utf-8", errors="ignore").read()
text = re.sub(r"<[^>]+>", " ", html)
text = re.sub(r"\s+", " ", text)

# 원문 인용구가 실제로 이 사본에 존재하는지 직접 확인(grep 결과를 재신뢰하지 않는다)
quote = ("an approximately 30 weight % potassium-stabilized dispersion in water "
         "with a particle size of 50-60 nanometers as measured by Capillary "
         "Hydro-Dynamic Flow using a Matec Applied Sciences model number CHDF "
         "2000 instrument")
assert quote in text, "US9200180B2 로컬 사본에서 CHDF 입경 인용구를 찾지 못함"

# 이 특허가 입경을 스윕하지 않는다는 주장의 근거: COMPONENTS 목록에 연마입자가
# 성분 D) 하나뿐임(다른 알파벳 성분 A/B/C는 벤젠술폰산/H2O2/KOH로 비연마입자)
comp_d_idx = text.find("Potassium-stabilized colloidal silica")
assert comp_d_idx > 0
# 그 앞 1000자 안에 다른 연마입자 성분(alumina, ceria, ...)이 나오지 않아야 한다
window = text[max(0, comp_d_idx - 1000):comp_d_idx]
for other_abrasive in ("alumina", "ceria", "fumed silica"):
    assert other_abrasive not in window.lower(), (
        f"COMPONENTS 목록에 다른 연마입자({other_abrasive})가 함께 등장 — "
        "입경 스윕 주장이 무효화됨")
print("PASS: US9200180B2 로컬 사본이 CHDF 50-60nm 인용구를 포함하고, "
      "COMPONENTS 목록에 연마입자가 콜로이달 실리카 하나뿐임을 확인")
```

## §3 입경 지수(abrasive_size_exponent) 판정

브리프가 제시한 세 갈래 중 어느 것인지:

- **(b) oxide_silica의 Li 2021 정점형 3파라미터 — 기각.** oxide_silica.yaml 자신이
  "⚠ oxide_silica에 전용 금지"를 명시하고 있고(cu_h2o2_bta.yaml의 동일 주석 참조),
  그 근거(Li 2021)는 SiO₂ 막(경질, 탄성 접촉)에서 나온 결과라 Cu 막(연질, 소성
  접촉)에 적용하면 §4 유도의 전제(소성압입)가 깨진다. 채택 안 함.
- **(c) US9200180B2 자체 입경 스윕 확인 — §2가 이미 답했다: 스윕이 없다.**
  이 특허 하나로는 입경 지수를 직접 회귀할 수 없다.
- **(a) cu_h2o2_bta의 null 결과(n=0.0, 판정#1) 상속 — 조건부로 채택.**

판정#1의 null 결과는 두 독립 다리로 literature 등급을 받았다
([[abrasive-size-null-result-force-partition-theory]]):

1. **실측 다리**: TW202115224A(Versum Materials, 2021,
   patents.google.com/patent/TW202115224A, Cu, n=18) 순수 구형 부분집합
   (15/27/50/160 nm)에서
   Spearman ρ≈0.03~0.15(비유의). 이 데이터의 조성은
   `validation/datasets/tw202115224a_cu_abrasive_size_pressure.yaml` 원문 그대로
   **글리신 5.5 wt% + 알라닌 9.5 wt% + 1,2,4-트리아졸 416 ppm + H2O2 1 wt%,
   pH 7.2** — 부모 팩(cu_h2o2_bta)의 화학과 같은 계열(착화제+트리아졸계 억제제)
   이지 이 팩(벤젠술폰산·억제제 없음·pH 9)의 화학이 아니다.
2. **이론 다리**: Chen thesis(Iowa State PhD, 2000s, 원문
   https://dr.lib.iastate.edu/bitstreams/a946712d-5717-441d-87f7-61c66c27ca57/download)
   힘분배+단층+소성압입 결합 유도가
   정확히 MRR ∝ d⁰를 준다(N∝d⁻², A_f∝d²가 상쇄). 이 유도(원 노트 §4)를
   다시 읽어 확인한 결과 — **화학종(오염제거제·억제제·산화제·pH)이 수식 어디에도
   등장하지 않는다.** 입력은 막 경도(H, Cu 벌크경도로 대표되는 연질→소성 레짐)와
   입자 형상(구형, 반경 R=d/2)뿐이다.

이 팩은 막(Cu)·입자재료(콜로이달 실리카)·입자크기범위(50-60 nm ⊂ 15-160 nm)가
①②의 전제와 일치하지만, ①의 **화학**(글리신/알라닌/트리아졸)과는 다르다(벤젠술폰산
+H2O2+알칼리, 억제제 없음). 즉 화학무관인 다리(②)만 전이되고 화학특정인 다리(①)는
전이되지 않는다 — EVIDENCE-RULES.md E4 정의("1차 유도지만 다른 계에서 검증된 것을
전이 — 방향만 채택, 크기는 미채택")에 해당한다.

**판정: n=0.0 값은 그대로 상속하되(②가 예측하는 값 자체가 0이므로), confidence는
literature에서 estimated로 한 단계 낮춘다.** 부모의 literature 등급은 ①+② 결합에서
나왔고 이 팩은 ②만 갖고 있기 때문이다. n을 다른 값으로 바꿀 근거는 없다 — ①의
반증도, 다른 부호를 지지하는 화학특정 증거도 없다(Li 2021의 반대부호는 산화막/탄성
레짐 소관이지 이 팩의 소성 레짐 소관이 아니다).

```python verify
# Chen thesis 힘분배+단층+소성압입 유도가 화학종을 참조하지 않는다는 주장을,
# 원 노트의 수식 자체를 재실행해 재확인한다(막·입자 입력만으로 d^0이 나옴).
def mrr_relative(d, P_const=1.0):
    R = d / 2.0
    N = 1.0 / d**2
    F = P_const / N
    delta_p = F / R
    A_f = R**0.5 * delta_p**1.5
    return N * A_f

# 이 팩의 실제 입경(55nm, §2)과 부모 팩이 검증한 범위 양끝(15/160nm)에서 계산
d_this_pack, d_lo, d_hi = 55e-9, 15e-9, 160e-9
r_lo = mrr_relative(d_lo) / mrr_relative(d_this_pack)
r_hi = mrr_relative(d_hi) / mrr_relative(d_this_pack)
assert abs(r_lo - 1.0) < 1e-9 and abs(r_hi - 1.0) < 1e-9, (
    "힘분배+단층+소성압입 결합모델은 화학종 입력 없이 d^0 이어야 한다")
print(f"PASS: d=55nm(이 팩)/15nm/160nm 세 지점 모두 이론상 MRR 비=1.0 — "
      "화학종을 참조하지 않는 이 유도가 이 팩(55nm)에도 값 자체는 그대로 적용됨")
```

## §4 농도 지수(abrasive_conc_exponent) 전이 판정

코드 기본값 1/3의 출처는 US9499721B2(Cabot Microelectronics, 2016,
patents.google.com/patent/US9499721B2) TABLE 18 — **콜로이달
실리카** 0.5~3.0 wt% × 4압력, TEOS 블랭킷(oxide 막), 전역 로그-로그 회귀 n≈0.30
([[abrasive-concentration-mrr-saturation-contact-probability]] §5). 입자 화학종
(콜로이달 실리카)은 이 팩과 정확히 일치한다.

**literature로 승격하지 않고 estimated로 유지하는 이유**: 근거 노트 §5 자신이
일치 판정 기준을 "같은 화학계(TEOS/콜로이달실리카)"라는 **막질+입자 조합**으로
쓴다 — `oxide_silica`가 이 값을 literature로 받은 것도 막질이 TEOS/oxide로
일치했기 때문이지 입자만 일치해서가 아니다. 이 팩은 막질이 Cu다. US9499721B2의
TEOS/oxide 계와 다르다. 입자만 일치하고 막질이 다른 전이는, 같은 코퍼스가 이미
쓰는 판정 기준으로는 "다른 화학계로의 전이"이고, §6의 damage_exponent(W→Cu 막질
전이가 literature가 아니라 estimated로 낮아진 사례)와 동형이다 — **막질전이는
한 단계 낮춘다**는 원칙을 여기서도 그대로 적용한다.

부수적 한계: 이 팩의 `abrasive_wt_pct`=10 wt%는 US9499721B2 스윕 상한(3 wt%)보다
높다 — 같은 노트 §3,§5가 지적한 "국소 지수 0.56→0.11 붕괴"(고농도 포화를 순수
거듭제곱이 못 담는 구조적 한계) 구간에 이미 들어가 있다는 뜻이다. 지수값 판정과는
별개 문제이나 정직하게 남긴다.

```python verify
from sim.params import load_pack
pk = load_pack("cu_alkaline_benzenesulfonic")

# 1) 팩이 own으로 선언했는지(상속 침묵이 아님) 확인
assert pk.has_own("abrasive_conc_exponent")
assert pk.param("abrasive_conc_exponent").confidence == "estimated"
n = float(pk.get("abrasive_conc_exponent"))
assert abs(n - 1.0/3.0) < 1e-6, f"1/3에서 벗어남: {n}"

# 2) 이 팩의 농도(10wt%)가 US9499721B2 스윕 상한(3wt%)을 넘는다는 한계 서술의 수치 확인
c = float(pk.get("abrasive_wt_pct"))
assert c == 10.0 and c > 3.0, "US9499721B2 스윕 상한(3wt%) 초과 여부 확인 실패"
print(f"PASS: abrasive_conc_exponent={n:.4f}(own, estimated), "
      f"운전농도 {c}wt% > US9499721B2 스윕 상한 3wt% — 과대평가 구간 진입 확인")
```

## §5 D99 꼬리 판정

부모(cu_h2o2_bta)의 D99=500 nm(=100×5.00)는 US7344988B2(알루미나 CMP 전용
특허, D99.9<5×D50)에서 나왔다 — 이 팩은 알루미나가 아니라 콜로이달 실리카이므로
그 배수를 그대로 쓸 수 없다(재료 전이).

**화학종 무관 일반비(Levitronix/Silco 2008, 5.00)도 쓰지 않는다** —
[[abrasive-particle-size-distribution-d99-tail]] §5의 verify 블록이 이미
"일반비(5.00)와 실리카 실측 비율(1.887)의 차이가 100%를 넘는다"를 이 코퍼스
안에서 직접 assert로 증명해 뒀다. 실리카 팩에 알루미나용 일반비를 쓰는 것은
이 코드베이스 자신의 기존 결론과 정면으로 모순된다.

대신 같은 노트 §3의 **US10894906B2(Versum Materials, 실리카 코어 CMP 복합입자,
2021, patents.google.com/patent/US10894906B2)**
Table 1 "No Treatment" 실측 비율 D99/D50 = 287.5/152.3 = 1.887722을 이 팩의
`abrasive_size_nm`(55.0 nm)에 곱했다: 55.0 × 1.887722 = **103.8247 nm**.

이것이 (oxide_silica가 한 것과 같은) "절대값 이식"이 아니라 "비율 재적용"인
이유: oxide_silica는 화학종(실리카)**+용도(oxide/STI/ILD CMP)**가 소스와 완전히
일치해 sti_ceria와 동일한 절대값 이식 방식을 썼다. 이 팩은 용도가 다르다(Cu CMP,
Versum 소스는 oxide CMP) — 절대값을 그대로 옮길 근거가 없어 비율을 이 팩의 실제
D50에 곱하는 차선책을 썼다. 이 차선책은 "비율이 입자 크기(152 nm→55 nm, 약 2.8배
축소)에 걸쳐 불변"이라는 **검증되지 않은 추가 가정**을 얹는다.

confidence=estimated인 이유(literature이려면 아래가 전부 성립해야 했다):
1. 화학종 일치(콜로이달 실리카)이나 **용도 불일치**(oxide CMP 소스 vs 이 팩 Cu CMP).
2. 세리아 코팅 복합입자의 코어 실측 — K-안정 순수 콜로이달 실리카와 표면화학이 다름
   (원 노트도 이미 이 한계를 명시. PSD 폭이 코팅 전 코어 합성 단계에서 정해진다는
   것이 그 노트의 논거이나 분리 실측은 아니다).
3. 비율의 입자크기 불변성이 미검증(2.8배 스케일 차).

**미확보**: US9200180B2 자체는 D99/D90 등 분포폭 스펙을 인쇄하지 않는다(§2에서
확인 — CHDF 값 하나뿐). K-안정 콜로이달 실리카(DuPont Air Products/현 Versum)
자체의 D99 실측은 이번 탐색(1회차)에서 찾지 못했다 — §8에 남긴다.

```python verify
from sim.params import load_pack
pk = load_pack("cu_alkaline_benzenesulfonic")

silica_d50, silica_d99 = 152.3, 287.5   # US10894906B2 Table1 "No Treatment"
ratio = silica_d99 / silica_d50
assert 1.85 < ratio < 1.90, ratio

d50_this_pack = float(pk.get("abrasive_size_nm"))
assert d50_this_pack == 55.0
expected_d99 = d50_this_pack * ratio
d99_declared = float(pk.get("abrasive_d99_nm"))
assert abs(d99_declared - expected_d99) < 1e-6, (
    f"팩 선언값({d99_declared})이 비율 재계산값({expected_d99})과 불일치")

# 이중계상 방지 계약: D99와 ref가 같아 기준조건 배수가 정확히 1.0이어야 한다
d99_ref = float(pk.get("abrasive_ref_d99_nm"))
assert d99_ref == d99_declared
n_damage = float(pk.get("damage_exponent"))
assert (d99_declared / d99_ref) ** n_damage == 1.0

# 알루미나용 일반비(5.00)를 그대로 썼다면 나왔을 값과 얼마나 다른지 정직하게 남긴다
alt_generic = d50_this_pack * 5.00
deviation_pct = abs(alt_generic - d99_declared) / d99_declared * 100
assert deviation_pct > 100.0
print(f"PASS: D99={d99_declared:.3f}nm = D50(55nm) x 실리카비율({ratio:.3f}), "
      f"기준조건 배수=1.0(이중계상 방지), 알루미나 일반비 사용시({alt_generic:.1f}nm) "
      f"대비 {deviation_pct:.0f}% 차이 — 재료전이를 피한 근거")
```

## §6 damage_exponent 판정

부모(cu_h2o2_bta)와 **동일값(2.54)·동일 근거를 그대로 상속**한다.
[[delta-damage-model-synthesis]] §3 팩별 표의 "n 출처" 열을 다시 읽으면, 이
코퍼스가 damage_exponent 전이 등급을 갈라온 축은 **연마입자 화학종이 아니라
막질**이었다:

| 팩 | n 출처 | 등급 |
|---|---|---|
| sti_ceria / sic_ceria_h2o2 | Hitachi 4점 회귀(막질+화학종 일치) | literature |
| oxide_silica | Hitachi(**막질 일치·입자 불일치** — 세리아→실리카) | literature |
| cu_h2o2_bta / w_fe_oxidizer | Egan & Kim 2019(doi:10.1149/2.0311905jss, **W→Cu 또는 W 자신**) | estimated |

oxide_silica는 입자가 불일치(세리아 vs 실리카)해도 막질이 맞아 literature를
유지했다. 반대로 cu_h2o2_bta는 막질이 불일치(W→Cu)해서 estimated로 낮아졌다.
즉 이 축을 가르는 것은 막질이지 입자 재료가 아니다.

이 팩은 막=Cu로 부모와 완전히 동일하다 — 연마입자가 알루미나에서 실리카로
바뀐 것은 이 축의 판정 기준(막질)에 영향을 주지 않는다. 따라서 텅스텐→구리
전이라는 근거 구조가 한 글자도 바뀌지 않고, 값(2.54)과 등급(estimated)을 그대로
상속한다. 판정#27·#30·#31(cu_h2o2_bta damage_exponent 3회차 미확보 종결 —
"Cu 막의 D99-스크래치 1차 대응쌍이 공개 코퍼스에 없다")의 결론도 화학무관하게
이 팩에 그대로 적용된다(코퍼스 자체가 바뀌지 않았으므로 재조사해도 같은 결론이
나올 것이 확실하다) — 그러나 **이 사실만으로 이 팩의 Δ 셀 전체를 C2-CLOSURES에
등록하지는 않는다**(§8 참조: D99 쪽 약한 고리는 아직 3회차를 거치지 않았다).

```python verify
from sim.params import load_pack
pk_new = load_pack("cu_alkaline_benzenesulfonic")
pk_parent = load_pack("cu_h2o2_bta")

n_new = float(pk_new.get("damage_exponent"))
n_parent = float(pk_parent.get("damage_exponent"))
assert n_new == n_parent == 2.54
assert pk_new.param("damage_exponent").confidence == "estimated"
assert pk_new.param("damage_exponent").confidence == pk_parent.param("damage_exponent").confidence
print(f"PASS: damage_exponent={n_new} — 부모(cu_h2o2_bta)와 값·등급 모두 동일 상속 "
      "(막질=Cu 불변이 근거, 연마입자 변경은 이 축과 무관)")
```

## §7 Γ 종결 상속

`sim/factors.py::_f_gamma`를 실제로 읽었다(441~588행). 필요 입력은
`cond_downforce_lbf`·`cond_duty_pct`·`rpm_platen`뿐이고 이들은 **슬러리 화학과
무관한 장비/컨디셔너 설정**이다. confidence 하한은 코드가 무조건 거는 리터럴이다:

```python
f.confidence = _worst_conf(driver_conf, "estimated")   # 사유(3) 스코프 축소 종결(확정 하한)
```

이 줄은 어떤 팩이 들어오든 실행되는 **팩-독립 경로**다 — `pk.has(...)` 분기가
`cond_downforce_lbf`/`cond_duty_pct`의 유무만 볼 뿐 화학 파라미터(pH·억제제·
연마입자 종류)를 전혀 참조하지 않는다. 이미 `sic_alumina_kmno4`가 정확히 같은
논리로 판정#22를 상속 등록한 선례가 있다(`validation/C2-CLOSURES.yaml`).

이 팩도 코드 경로가 완전히 같으므로 동일하게 등록한다(§`validation/C2-CLOSURES.yaml`
"factor: gamma, pack: cu_alkaline_benzenesulfonic" 항목, judgments 판정#22·
판정#22-종결). 이것은 "조사 없이 칸을 채우는" 것이 아니라 — 코드를 직접 읽어
팩-독립 경로임을 확인한 뒤 내리는 **구조적 한계의 재선언**이다.

```python verify
import inspect
import sim.factors as F

src = inspect.getsource(F._f_gamma)
# 이 함수가 화학 관련 키(pH, 억제제, 연마입자)를 전혀 읽지 않는다는 것을 소스코드에서
# 직접 확인한다 — "필요 입력이 장비/컨디셔너뿐"이라는 §7 주장의 기계적 검증.
chemistry_keys = ["slurry_ph", "inhibitor", "abrasive_wt_pct", "abrasive_size_nm",
                  "oxidizer", "chelator"]
for k in chemistry_keys:
    assert k not in src, f"_f_gamma가 화학 키 '{k}'를 참조함 — 팩-독립 주장이 깨짐"
# 리터럴 하한이 실제로 존재하는지 확인
assert '_worst_conf(driver_conf, "estimated")' in src
print("PASS: _f_gamma는 화학 파라미터를 참조하지 않고, estimated 리터럴 하한이 "
      "팩-독립적으로 걸려 있음을 소스코드로 직접 확인")
```

## §8 한계와 미확보

- **κ는 literature로 승격하지 못했다.** 두 지수(입경·농도) 모두 estimated에
  머문다 — 입경은 이론 다리만 전이돼(화학특정 실측 다리 상실), 농도는 막질전이라
  이 코퍼스의 기존 등급 기준으로 한 단계 낮췄다. `_pack_conf`가 두 그룹의 최약값을
  취하므로 κ 전체 confidence는 estimated다. **completion.py의 C2 임계값
  (literature)을 넘지 못한다** — unverified(전혀 근거를 물을 대상이 없음)에서
  estimated(근거는 있으나 화학특정 검증이 없음)로 실질적으로 승격했지만, 자동
  게이트 통과에는 이르지 못했다. 이 격차를 억지로 메우려 지수를 다른 값으로
  바꾸지 않았다(브리프의 금지사항 그대로 지켰다).
- **Δ도 literature로 승격하지 못했다.** `abrasive_d99_nm`이 estimated(§5, 용도
  불일치+표면화학 불일치+크기외삽 3중 한계)이고 `damage_exponent`도 estimated
  (§6, 상속)라 Δ 전체가 estimated다. 브리프가 명시한 대로 Δ의 목표는 C1(모델링
  존재)뿐이었으므로 이것은 **허용된 결과**다. 다만 `abrasive_d99_nm`의 estimated
  등급은 damage_exponent와 달리 **아직 3회차 소진 절차를 거치지 않은 새 약한
  고리**이므로, C2-CLOSURES에 등록하지 않았다 — 등록하면 damage_exponent의
  기(旣)종결 판정(#27/#30/#31)에 무임승차해 아직 조사하지 않은 D99 쪽 갭을
  가리게 된다.
- **⚠ 1차 출처 확보 실패**: K-안정 콜로이달 실리카(DuPont Air Products/현 Versum)
  자체의 D99(또는 D90) 실측 스펙 — US9200180B2는 CHDF D50 상당값 하나만 인쇄한다
  (§2, §5). 시도한 경로: (1) 같은 로컬 특허 사본 전문 재검색("D99"·"D90"·
  "particle size distribution" 키워드) — 분포폭 스펙 없음. (2) US10894906B2
  (§5에서 비율만 채택) — 절대값 직접 전용은 용도 불일치로 기각. 다음 회차 후보:
  DuPont Air Products NanoMaterials(현 Versum)의 다른 콜로이달 실리카 특허 패밀리
  (예: US72380xx 계열, 미시도)에서 같은 제조사·같은 K-안정화 공정의 D99 실측을
  찾는 것.
- 입자 형상(구형)은 US9200180B2 원문이 명시하지 않고 "colloidal silica"라는
  업계 관행 표기에서 추정했다(§3) — 미검증.
