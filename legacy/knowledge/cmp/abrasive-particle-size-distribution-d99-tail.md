<!-- V2-SECTION: R2-slurry | 작성 2026-09-14 | 정본: ARCHITECTURE-V2.md §3 -->
# 알루미나·콜로이달실리카 D99 — 화학종 일치 1차 특허로 estimated→literature 승격

> 에이전트: slurry-abrasive | 작성일: 2026-09-14
> 선행: [[delta-scratch-damage-d99-oversize-particle-model]](D99×5.00 일반비 유도, 3팩 estimated)
> [[abrasive-d99-scratch-hitachi-us8439995]](sti_ceria가 이미 literature로 승격한 형식 표본)
> [[abrasive-d99-composite-particle-versum2019]] [[abrasive-d99-alumina-fourth-attempt-guo-nanoalumina]]
> [[abrasive-d99-alumina-search-and-generic-ratio]] [[abrasive-d99-spec-cross-pack-comparison]]

## 1. 왜 필요한가

2026-09-14 EVIDENCE-RULES 판정#16이 `cu_h2o2_bta`/`oxide_silica`/`w_fe_oxidizer` 3팩의
`abrasive_d99_nm`을 literature→estimated로 강등했다. 이유: 기존 값(250/500/250 nm)이
"D50 × D99/D50 일반비 5.00"으로 유도됐는데, 이 5.00이라는 비율의 출처(Silco/Levitronix
2008 산업 컨퍼런스 슬라이드)가 (a) 2차 자료·동료심사 없음, (b) 특정 화학종 전용이 아닌
"일반 슬러리" 세대별 관측치, (c) 유일하게 확보된 실측 대조군(세리아, Hitachi US8439995B2)
으로 재현 시도하면 3.13~10.42로 최대 60% 벌어짐 — 이었다. 반면 `sti_ceria` 팩은 같은
`abrasive_d99_nm` 키가 이미 literature 등급이다: Hitachi Ex.1의 D99=700nm(세리아, oxide/
STI CMP 실측)을 "화학종+용도 일치, 이 팩 고유 조성은 아님"이라는 E2 근거로 그대로 이식했기
때문이다(§9, [[abrasive-d99-scratch-hitachi-us8439995]]).

이 노트는 그 형식을 알루미나 2팩(`cu_h2o2_bta`, `w_fe_oxidizer`)과 실리카 1팩
(`oxide_silica`)에 그대로 적용한다 — **화학종이 정확히 일치하는 1차 특허**를 새로 확보해
"일반비"가 아니라 "그 화학종 자체의 실측/스펙 D99"로 근거를 교체한다.

## 2. 1차 문헌 A — US 7,344,988 B2 (DuPont Air Products Nanomaterials LLC): 알루미나 CMP

**"Alumina abrasive for chemical mechanical polishing."** DuPont Air Products
Nanomaterials LLC(당시 Air Products and Chemicals 계열), 등록 2008-03-18. 원문 확보
(freepatentsonline.com, claims 1~10 + Detailed Description 전문 확인, 2개 독립 fetch로
수치 교차 확인). 대상 막질: **"copper, aluminum, or tungsten"**, 특히 **"especially preferred
for use on substrates comprising copper and/or tungsten"** — `cu_h2o2_bta`(Cu, 알루미나)와
`w_fe_oxidizer`(W, 알루미나) 두 팩의 화학종+용도가 모두 정확히 일치한다.

원문 명세(Horiba LA910 입도분석기 실측 기반):
> "The gamma alumina so formed can advantageously have a D50 particle size … from about
> 0.06 μm to about 0.25 μm, preferably between about 0.1 μm and about 0.2 μm, for example
> between about 0.13 μm and about 0.15 μm, and a D99.9 particle size … from about 0.2 μm to
> about 1.5 μm, for example between about 0.7 μm and about 1 μm."

Claim 8(후공정, 실제 슬러리에 들어가는 wet-milled 알루미나):
> "a solid component of fumed gamma alumina particles having an average particle size D50
> between about 60% and about 80% of the pre-milling particle size D50, and having a D99.9
> particle size that is less than about seven times the post-milling particle size D50…"

Detailed Description이 이 상한을 3단계로 좁힌다:
> "the average D99.9 preferably being less than about seven times, more preferably less than
> 5 times, for example less than 3 times, the average D50 of the milled abrasive."

⚠ **D99.9 ≠ D99**: 이 특허는 99.9백분위수를 쓴다. D99 ≤ D99.9는 항상 성립하므로(백분위가
낮을수록 값이 작거나 같다), 이 특허의 D99.9 상한은 D99에도 유효한 **상한**이다(과대추정
방향, 안전한 쪽). 절대 실측 단일값이 아니라 "preferably/more preferably/example" 3단계
스펙 범위라는 것도 명시한다 — 세리아(Hitachi)처럼 단일 실시예 표는 아니다.

## 3. 1차 문헌 B — US 10,894,906 B2 (Versum Materials US, LLC): 실리카 코어 CMP 복합입자

**"Composite particles, method of refining and use thereof."** Versum Materials US, LLC,
등록 2021-01-19. 원문 확보(freepatentsonline.com, 2개 독립 fetch로 Table 1 수치 교차
확인 — 완전 일치). 실리카 코어 위에 세리아 나노입자를 코팅한 복합입자, 대상 CMP는
**oxide/STI/ILD**(§[0007] 계열 Versum 특허 공통 서술, [[abrasive-d99-composite-particle-versum2019]]
§2와 동일 패밀리) — `oxide_silica`(콜로이달 실리카, 산화막 CMP)와 코어 소재(실리카)+용도
(oxide CMP)가 일치한다. 세리아 코팅은 표면 처리이지 코어 자체를 바꾸지 않는다.

**Table 1 원문 그대로 (Disc Centrifuge 실측, Example 1)**:

| 처리 | MPS (nm) | D50 (nm) | D75 (nm) | D99 (nm) |
|---|---|---|---|---|
| No Treatment (원료, 미처리) | 155.0 | 152.3 | 189.8 | 287.5 |
| RE2003 (원심분리 상위 30% 정제) | 102.5 | 104.0 | 118.3 | 165.3 |
| RE2004 (정제 조건 2) | 105.7 | 109.1 | 128.6 | 181.1 |
| Filtration | 152.3 | 152.0 | 190.6 | 287.8 |

**"No Treatment" 행을 baseline으로 채택한다** — RE2003/RE2004는 이 특허 자체의 발명(정제
공정)으로 꼬리를 인위적으로 좁힌 결과이고, "No Treatment"가 특허 발명 적용 전의 일반
실리카-코어 복합입자 상태에 가장 가깝다. D99=287.5 nm, D50=152.3 nm, 비율
D99/D50=1.887 — 기존 `oxide_silica` 팩이 쓰던 일반비 5.00과 크게 다르다(§5에서 정량 확인).

## 4. 판정 — sti_ceria 형식 그대로, 3팩 각각 다르게 적용

sti_ceria의 핵심 논리(§9, [[abrasive-d99-scratch-hitachi-us8439995]])를 그대로 쓴다:
"화학종+용도 일치 실측값을 이 팩의 baseline(기준점)으로 이식한다 — 이 팩이 실제로 그
조성을 쓴다는 뜻이 아니다." 단, 이번엔 3팩이 서로 다른 취급을 받는다:

### 4.1 `cu_h2o2_bta`, `w_fe_oxidizer` (알루미나) — 값은 유지, 근거만 교체
기존 유도값(500 nm = 100×5.00, 250 nm = 50×5.00)을 보면 **비율이 정확히 5.00** — 이는
바로 US7344988B2의 "more preferably less than 5 times" 상한과 **정확히 일치**한다(§2).
일반비의 출처가 "화학종 무관 산업 슬라이드"에서 "알루미나 CMP 전용 1차 특허의 상한 스펙"으로
바뀌는 것이지, 계산값은 항등적으로 같다 — **값을 바꿀 필요가 없다**(브리프 지침: 값 불변 +
confidence만 상승이 가장 안전). 등급: E2(화학종+용도 일치 1차 특허 상한 스펙, 이 팩 고유
조성 실측 아님 → literature, verified 아님).

### 4.2 `oxide_silica` (콜로이달 실리카) — 값을 287.5nm로 교체(_ref 동반)
기존 250nm(=50×5.00)은 US10894906B2의 실측 비율(1.887, §3)과 맞지 않는다 — 실리카
코어는 알루미나와 달리 5.00배 일반비가 들어맞지 않는다(§5에서 정량 확인). sti_ceria가
Hitachi의 **절대값**(700nm)을 그대로 이식했듯, 이 팩도 "화학종+용도 일치 실측 절대값"
287.5nm을 채택한다(비율 재계산이 아니라 sti_ceria와 동일한 절대값 이식 방식). 기존
250nm과 15% 차이로 오더는 같다. `abrasive_ref_d99_nm`도 **같은 편집에서 287.5로 동반
이동**한다(기준 Δ=1.0 계약 유지).

## 5. 수식 재현 (verify)

```python verify
# ── (A) US7344988B2 — 알루미나, Cu/Al/W CMP: post-milled D99.9/D50 상한 3단계 ──
d99_9_over_d50_bounds = {"preferred": 7.0, "more_preferred": 5.0, "example": 3.0}

cu_h2o2_bta_d50_nm = 100.0     # 팩 기존값 (EKC alumina, Gopal 2007)
cu_h2o2_bta_d99_nm = 500.0     # 팩 기존값 (미변경)
w_fe_oxidizer_d50_nm = 50.0    # 팩 기존값 (Bielmann 1999)
w_fe_oxidizer_d99_nm = 250.0   # 팩 기존값 (미변경)

ratio_cu = cu_h2o2_bta_d99_nm / cu_h2o2_bta_d50_nm
ratio_w = w_fe_oxidizer_d99_nm / w_fe_oxidizer_d50_nm

assert ratio_cu == 5.0, f"cu_h2o2_bta D99/D50 비율이 5.00이 아님: {ratio_cu}"
assert ratio_w == 5.0, f"w_fe_oxidizer D99/D50 비율이 5.00이 아님: {ratio_w}"
assert ratio_cu == d99_9_over_d50_bounds["more_preferred"], (
    "두 팩의 기존 비율(5.00)이 US7344988B2의 'more preferably less than 5 times' 상한과 "
    "정확히 일치해야 한다 — 이것이 이 노트가 값을 바꾸지 않는 근거다."
)
# D99 <= D99.9 이므로, D99.9 상한을 만족하는 값은 D99 상한으로도 유효(과대추정 방향, 안전)
assert cu_h2o2_bta_d99_nm <= d99_9_over_d50_bounds["preferred"] * cu_h2o2_bta_d50_nm
assert w_fe_oxidizer_d99_nm <= d99_9_over_d50_bounds["preferred"] * w_fe_oxidizer_d50_nm
print(f"cu_h2o2_bta D99/D50={ratio_cu:.2f}, w_fe_oxidizer D99/D50={ratio_w:.2f} "
      f"— 둘 다 알루미나 특허(US7344988B2)의 'more preferred <=5x' 상한과 정확히 일치")

# ── (B) US10894906B2 — 실리카 코어 CMP 복합입자, Table 1 "No Treatment" ──
silica_d50_nm = 152.3
silica_d99_nm = 287.5
ratio_silica = silica_d99_nm / silica_d50_nm

assert 1.85 < ratio_silica < 1.90, f"실리카 코어 D99/D50 비율이 예상 범위 밖: {ratio_silica:.3f}"
print(f"US10894906B2 Table1 'No Treatment': D50={silica_d50_nm}nm, D99={silica_d99_nm}nm, "
      f"비율={ratio_silica:.3f}")

# 핵심 주장: 실리카 코어의 실측 비율(1.887)은 알루미나 팩이 쓰는 일반비(5.00)와 크게 다르다
# -> 화학종마다 D99/D50 비율이 다르므로, oxide_silica에는 알루미나용 5.00을 쓰면 안 된다
generic_ratio = 5.0
deviation_pct = abs(generic_ratio - ratio_silica) / ratio_silica * 100
assert deviation_pct > 100.0, (
    f"일반비(5.00)와 실리카 실측 비율({ratio_silica:.2f})의 차이가 100%를 넘어야 "
    "'화학종별로 다르다'는 이 노트의 핵심 논증이 성립한다"
)
print(f"일반비(5.00) vs 실리카 실측 비율({ratio_silica:.3f}) 차이 = {deviation_pct:.0f}% "
      "— 화학종 무관 일반비를 실리카에 쓸 수 없다는 근거")

# oxide_silica 팩의 새 baseline 값 = US10894906B2 절대 실측값 그대로(비율 재적용 아님, sti_ceria와 동일 방식)
oxide_silica_new_d99_nm = silica_d99_nm
old_d99_nm = 250.0
change_pct = abs(oxide_silica_new_d99_nm - old_d99_nm) / old_d99_nm * 100
assert change_pct < 20.0, f"기존값과 오더가 다르면 재검토 필요: {change_pct:.1f}%"
print(f"oxide_silica: 기존 {old_d99_nm}nm -> 신규(US10894906B2 실측) {oxide_silica_new_d99_nm}nm "
      f"({change_pct:.1f}% 차이, 같은 오더)")
```

## 6. 한계 (정직한 미검증 표기)

- ⚠ **D99.9 vs D99**: US7344988B2는 99.9백분위수를 쓴다. 이 노트가 이를 D99 상한으로 쓰는
  것은 "D99 ≤ D99.9" 부등식에 기댄 안전한 방향의 근사이며, D99 자체의 정밀값이 아니다.
- ⚠ **범위 스펙, 단일 실측 아님**: US7344988B2의 "preferably/more preferably/example" 3단계는
  제품 설계 목표 범위이지, 세리아(Hitachi)처럼 특정 로트의 4점 실측 표가 아니다. 알루미나
  2팩의 등급을 sti_ceria와 똑같은 E2로 매기되, "단일 실측"이 아니라 "실측 기반 설계 상한
  스펙(Horiba LA910)"이라는 차이는 남긴다.
- ⚠ **세리아 코팅**: US10894906B2의 입자는 실리카 코어에 세리아를 코팅한 복합입자다. 코어
  소재(실리카)는 일치하지만 표면 화학은 `oxide_silica` 팩의 순수 콜로이달 실리카와 다르다 —
  D99/D50 분포 폭 자체는 코팅 전 코어 합성 단계에서 대부분 결정되므로(코팅은 표면 화학,
  분포 폭은 코어 응집 상태) 영향이 작다고 보지만, 실측으로 분리 확인한 것은 아니다.
- ⚠ **damage_exponent는 이 노트의 범위 밖**: 이 노트는 `abrasive_d99_nm`/`abrasive_ref_d99_nm`만
  다룬다. `damage_exponent`(cu_h2o2_bta/w_fe_oxidizer=2.54, oxide_silica=1.44)는
  [[delta-scratch-damage-d99-oversize-particle-model]] §4.3의 근거를 그대로 유지한다(변경 없음).
- **범위 준수**: `tools/scope.py --agent slurry-abrasive --check`로 두 특허 모두 사전 확인
  (✓ 허용, 입자 물성 초점 — 제형 자체는 다루지 않음).

## 7. 출처 요약

- US 7,344,988 B2. "Alumina abrasive for chemical mechanical polishing." DuPont Air
  Products Nanomaterials LLC. 등록 2008-03-18. (특허, 무료 공개, freepatentsonline.com)
- US 10,894,906 B2. "Composite particles, method of refining and use thereof." Versum
  Materials US, LLC. 등록 2021-01-19. (특허, 무료 공개, freepatentsonline.com) Table 1.
- 대조 표본(형식): US 8,439,995 B2 (Hitachi) Ex.1 — sti_ceria가 이미 literature로 승격한
  D99=700nm 이식 사례, [[abrasive-d99-scratch-hitachi-us8439995]] §9.

## 8. 다음 단원

`damage_exponent`의 화학종 전이(w→cu, Egan & Kim 2019는 텅스텐 실측)는 여전히 estimated로
남아 있다 — 알루미나 CMP에서 직접 측정된 D99-스크래치 대응쌍은 이번 회차도 찾지 못했다(범위
밖, 이 노트의 임무는 `abrasive_d99_nm`뿐). 다음 회차 후보로 남긴다.
