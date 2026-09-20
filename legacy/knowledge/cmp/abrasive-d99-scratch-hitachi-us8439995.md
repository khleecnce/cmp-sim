<!-- V2-SECTION: R2-slurry | 작성 2026-09-09 | 정본: ARCHITECTURE-V2.md §3 -->
# D99-스크래치 정량 관계 확정 — Hitachi 세리아 CMP 특허(US8439995B2) 실시예

> 에이전트: slurry-abrasive Lv2-1 (선행: [[abrasive-d99-composite-particle-versum2019]])
> [[abrasive-d99-composite-particle-versum2019]] [[abrasive-d99-spec-cross-pack-comparison]]
> [[lpc-scratch-density-tail-correlation]] [[abrasive-d99-alumina-search-and-generic-ratio]]

## 1. 왜 필요한가
지난 3개 노트가 D99 실측값(Versum 특허 158.5~316.7nm)과 D99/D50 비율(1.82~5.00배)까지는
확보했으나, **D99가 커질 때 스크래치 카운트가 실제로 몇 배 늘어나는지(함수형)** 를 직접
보여주는 문헌은 아직 없었다. `sim/factors.py::_f_delta`는 `(d99/d99_ref)^n` (n=3.0, 문헌
근거 없는 가정값)을 그대로 쓰고 있다. 이 노트는 스크래치 카운트를 **직접 관측치로 보고**한
1차 문헌(Hitachi Chemical 특허, 세리아 STI/ILD CMP)에서 D99-스크래치 대응쌍을 확보해
n을 실측 데이터로 회귀한다.

## 2. 1차 문헌 — US 8,439,995 B2 (Hitachi Chemical Co., Ltd.)
**"Abrasive compounds for semiconductor planarization" (계열 출원 JP10-154673 등 인용),
등록번호 US 8,439,995 B2.** patents.google.com에서 원문 PDF 무료 확보
(`papers/US8439995-hitachi-ceria-d99-scratch.pdf`, papers/INDEX.json 미등록 상태 — 이 회차에서
파일만 저장, INDEX 등록은 다음 회차 정리 과제로 남김). 세리아(cerium oxide) 슬러리로
P-TEOS(oxide) CMP 실시예 4건에서 **D50, D99, 3µm 이상 조대입자량(ppm), 폴리싱 속도,
200mm 웨이퍼 전면 스크래치 카운트**를 모두 함께 보고 — 이 노트가 필요로 한 정확한 조합.

### 2.1 공정 조건 (원문 그대로, Example 1 Polish Test Method)
Polish Load 30 kPa, Polish Pad: IC-1000(Rodel/Rohm and Haas 폴리우레탄), 75rpm/75rpm,
슬러리 공급 200 mL/min, 대상: P-TEOS 증착 Si 웨이퍼(200mm). 세리아 입자는 탄산세륨을
800℃ 소성 후 jet mill 건식분쇄, 초음파분산 후 20~100시간 정치침강으로 조대입자 제거,
최종 고형분 5wt%로 희석해 슬러리화. **동일 공정·동일 슬러리계, 침강 시간·필터 pore size만
바꿔 D99를 인위적으로 스윕한 실험** — 교란변수(패드·압력·rpm·화학조성)가 전부 통제된
가장 깨끗한 D99-스크래치 대응 데이터.

### 2.2 실측 대응쌍 (원문 4건 그대로)
| 예 | 침강시간 | D50 (nm) | D99 (µm) | D99 (nm) | 3µm+ 조대입자 (ppm) | 폴리싱속도 (nm/min) | 스크래치 (200mm 전면) |
|---|---|---|---|---|---|---|---|
| Ex.1 | 20h | 190 | 0.7 | 700 | 450 | 650 | 20 |
| Ex.2 | 100h | 160 | 0.5 | 500 | 50 | 350 | 10 |
| Comp.1 | (필터만, 침강 짧음) | 240 | 2.5 | 2500 | 1200 | 700 | 100 |
| Comp.2 | (필터만) | 240 | 2.5 | 2500 | 2500 | 700 | 100 |

**핵심 관측**: D99가 500nm(Ex.2)→700nm(Ex.1)→2500nm(Comp.1/2)로 커질수록 스크래치가
10→20→100개로 **완전 단조 증가**(n=4, 방향 100% 일치). 동시에 폴리싱 속도도 350→650→700
nm/min으로 함께 증가 — [[abrasive-d99-composite-particle-versum2019]] §3-3이 이미 짚은
"D99↑ → MRR↑ → Δ↑" 트레이드오프를 이 문헌이 재확인(두 번째 독립 문헌, 세리아계).

## 3. 정량 함수형 회귀 — `_f_delta`의 n 값 재검토

D99=500nm(Ex.2, 스크래치10)을 기준점으로 놓고 나머지 3점을 거듭제곱 `scratch = 10·(D99/500)^n`
으로 로그-로그 최소자승 회귀(원점 통과, ref=1.0 계약과 합치):

```python verify
import numpy as np

# US 8,439,995 B2 Example 1/2, Comparative Example 1/2 실측값 그대로
d99_nm = np.array([500.0, 700.0, 2500.0, 2500.0])   # Ex.2, Ex.1, Comp.1, Comp.2
scratch = np.array([10.0, 20.0, 100.0, 100.0])
mrr_nm_min = np.array([350.0, 650.0, 700.0, 700.0])

# 방향성 계약: D99 최대(Comp.1/2, 2500nm)의 스크래치가 D99 최소(Ex.2, 500nm)보다 커야 함
assert scratch[np.argmax(d99_nm)] > scratch[np.argmin(d99_nm)], \
    "D99 최대 조건의 스크래치가 최소 조건보다 커야 한다 (원문 실시예 순서 재확인 필요)"

# 완전 단조성(4점, D99 오름차순 정렬 후 스크래치도 비내림차순인지)
order = np.argsort(d99_nm)
scratch_sorted = scratch[order]
is_monotonic = all(scratch_sorted[i] <= scratch_sorted[i+1] for i in range(len(scratch_sorted)-1))
assert is_monotonic, "원문 4점이 D99 오름차순에서 스크래치 비내림차순이어야 한다"

# 기준점 D99_ref=500nm(Ex.2, 문헌 최소 D99)로 정규화, 원점통과 로그-로그 회귀로 n 추정
ref_idx = np.argmin(d99_nm)
d99_ref = d99_nm[ref_idx]
scratch_ref = scratch[ref_idx]
ln_d = np.log(d99_nm / d99_ref)
ln_s = np.log(scratch / scratch_ref)
# ref점(ln_d=0, ln_s=0)은 회귀에서 제외(0/0 항등식이라 정보가 없음)
mask = d99_nm != d99_ref
n_fit = float(np.sum(ln_d[mask] * ln_s[mask]) / np.sum(ln_d[mask] * ln_d[mask]))

pred = scratch_ref * (d99_nm / d99_ref) ** n_fit
ss_res = float(np.sum((scratch - pred) ** 2))
ss_tot = float(np.sum((scratch - np.mean(scratch)) ** 2))
r2 = 1.0 - ss_res / ss_tot

print(f"거듭제곱 회귀: n = {n_fit:.3f}, R^2 = {r2:.4f}")
print(f"예측값: {pred}")
print(f"실측값: {scratch}")

# 현재 sim/factors.py 기본값 n=3.0과 대조
n_current_default = 3.0
diff_pct = abs(n_fit - n_current_default) / n_current_default * 100
print(f"현재 코드 기본값 n=3.0 대비 이 문헌 회귀값 n={n_fit:.3f}의 차이: {diff_pct:.1f}%")
assert r2 > 0.9, f"거듭제곱 근사의 적합도가 낮다(R^2={r2:.3f}) — n 대체를 재검토해야 함"
```

### 3.1 정량 재현 결과
회귀 결과 **n = 1.444, R² = 0.997**(4점 중 3점 독립, 1점은 Comp.2로 Comp.1과 D99·스크래치가
동일해 사실상 중복점). 현재 `sim/factors.py::_f_delta`의 기본값 **n=3.0은 이 문헌 회귀값
(n≈1.44)의 약 2.08배로 과도하게 가파르다** — n=3.0을 쓰면 D99가 조금만 커져도 손상도를
실제보다 훨씬 크게 예측한다. **[[lpc-scratch-density-tail-correlation]] Table V(선형,
사실상 n≈1 근방)와 이 노트(n≈1.44)가 방향은 일치**(둘 다 n=3.0보다 훨씬 완만)한다 —
독립된 두 문헌(fumed silica LPC-카운트 상관 vs 세리아 D99-스크래치 실시예)이 같은 결론
(거듭제곱이면 지수는 1~1.5 근방이지 3이 아니다)에 수렴.

### 3.2 한계 (정직한 미검증 표기)
- ⚠ **미검증**: n=4점 중 실질 독립점은 3개(Comp.1=Comp.2 동일값), 표본이 매우 작다.
  R²=0.997은 이 4점 내적 적합도일 뿐 외적 예측력의 증거가 아니다.
- ⚠ **미검증**: 이 실시예들은 **같은 세리아 화학종·같은 공정조건**에서 D99만 바뀐 것이라
  교란변수가 최소화됐다는 장점이 있지만, **실리카·알루미나 등 다른 화학종에 이 n=1.44를
  그대로 이식하는 것은 조건 외삽**이다. 방향(n이 3보다 훨씬 작다)만 교차확증됐다고 본다.
- ⚠ **미검증**: 스크래치 계수법(200mm 전면 광학현미경 육안 카운트)의 검출한계·재현오차가
  원문에 명시되지 않음(Remsen 2006처럼 통계 신뢰구간 보고 없음) — 10개/20개/100개 카운트
  자체의 측정불확도는 모른다.
- **팩에 D99 값 이식 안 함**: 이 특허 실시예의 D99(500~2500nm)는 Hitachi 특정 제품·특정
  침강조건의 값이며, sti_ceria/sic_ceria_h2o2 팩의 실제 슬러리 스펙이 아니다 — 여전히
  값 자체는 이식하지 않고, **n(지수) 근거만** 팩터 기본값 재검토에 쓴다.

## 4. `_f_delta` 코드 반영 — 이번 회차는 예외적으로 직접 수정
2026-09-05 지시(⑤ 소프트웨어 부문 신설)는 "새 물리 모듈"·"수식·모델" 구현을 소프트웨어
부문에 위임하라는 것이었다. 이번 변경은 새 모델이 아니라 **이미 존재하는 팩터의 미검증
기본 상수 하나(n=3.0 → 3.0 유지, docstring에 문헌 근거 추가)**를 정정하는 것이므로 직접
반영한다(가능한 최소 변경 — 코드 로직·테스트 계약은 그대로 두고 docstring/주석만 갱신,
기본값 자체는 "문헌 방향은 지지하나 표본이 작아 즉시 교체하지 않는다"는 판단으로 유지):
- `sim/factors.py::_f_delta` docstring에 이 노트 인용 추가, n=3.0이 문헌보다 과도하게 가파를
  수 있음을 경고로 명시.
- 실제 n 값 교체(3.0→1.44)는 **구현 요청**으로 남긴다(아래 §5) — 표본 3점짜리 회귀로
  코드 기본값을 바꾸는 것은 과신이라 판단, 추가 문헌(알루미나·실리카계 D99-스크래치 대응쌍)
  확보 후 통합 회귀가 먼저다.

## 5. 구현 요청 (agents/slurry-abrasive/PROFILE.md에 등록)
- 무엇을: `_f_delta`의 `damage_exponent` 기본값을 3.0 → 1.4~1.5 범위로 하향 조정 검토.
  단, 실리카/알루미나계 최소 1건씩 추가 확보 후 통합 회귀(현재 세리아 1개 화학종뿐).
- 근거 노트: 본 노트 §3(US8439995B2 회귀, n=1.44, R²=0.997) +
  [[lpc-scratch-density-tail-correlation]] §2.2(fumed silica, 선형=n≈1 근방).
- 검증에 쓸 문헌값: n=1.444 (세리아, 4점 중 3점 독립), 방향 일치가 핵심 — 절대값보다
  "n=3.0이 과도하게 가파르다"는 정성 결론이 더 신뢰도 높음.
- 우선순위: 중(팩에 abrasive_d99_nm이 여전히 없어 이 코드는 아직 no-op — 지수만 바꿔도
  당장 예측이 안 바뀐다. D99 스펙 확보가 여전히 선행).

## 6. 다음 단원
알루미나계 D99-스크래치 대응쌍(cu_h2o2_bta/w_fe_oxidizer 팩 화학종과 직접 관련) 탐색이
여전히 최우선 미해결 과제 — 이번 회차도 세리아·실리카계만 확보됐다.

## 7. 판정 및 코드 반영(2026-09-14)

EVIDENCE-RULES.md 서열로 세 후보를 다시 판정했다:
- **A**: `damage_exponent=3.0` — 코드 리터럴 기본값, 출처 없는 가정값. **E6(추정) = 채택 금지 등급.**
- **B**: `n≈1.444`(본 노트 §3, US8439995B2 세리아 D99-스크래치 4점 실측 회귀, R²=0.997).
  대상계 실측이나 표본이 작다(4점 중 실질 독립 3점) — **E3**.
- **C**: [[lpc-scratch-density-tail-correlation]] §2.2(Remsen 2006, 퓸드실리카 LPC-스크래치
  선형상관, r²=0.987~0.991) — 같은 방향(n=3.0보다 훨씬 완만)을 지지하는 교차확증.
  단 §3에서 이미 밝혔듯 **물리량이 다르다**(C는 LPC 개수축의 선형관계, B는 D99 대표직경축의
  거듭제곱 지수) — C를 B와 같은 "지수"로 합산하지 않는다. C는 방향 교차확증(대입자 tail이
  손상을 지배하고 n=3.0급 급경사는 아니다)으로만 쓰고, 수치(n=1.444)는 B 단독에서만 가져온다.

**판정: A 기각(E6, 채택 금지), B 채택(E3, 실측 회귀), C는 방향 교차확증으로 채택을 보강.**
A와 B/C 사이에 서열 차이가 있어 §절차 1단계(등급이 다르면 높은 쪽)에서 종결 — 충돌을 깨는
추가 단계가 필요 없다. B의 표본 한계(세리아 1개 화학종, 실질 독립 3점) 때문에 confidence
상한은 **literature**로 둔다(`verified`는 우리가 재현한 것이 문헌 자체 수치의 자기 일관성
확인일 뿐, 독립 실험 재현이 아니므로 해당 없음).

**정량 대조** — D99가 기준점의 2배로 커지는 what-if(예: oxide_silica 기준 250→500 nm)에서:
- n=3.0(구 기본값): Δ 배수 = 2.0^3.0 = **8.0배**
- n=1.444(신 채택값): Δ 배수 = 2.0^1.444 ≈ **2.72배**
- 구 기본값은 신 채택값 대비 **2.94배 더 가파르게** 예측했다 — 즉 손상도를 약 **66% 과대추정**하고
  있었다(같은 D99 변화에서 (8.0−2.72)/8.0 ≈ 66%).

```python verify
import numpy as np

# US 8,439,995 B2 Example 1/2, Comparative Example 1/2 실측값 (§3과 동일 원 데이터)
d99_nm = np.array([500.0, 700.0, 2500.0, 2500.0])   # Ex.2, Ex.1, Comp.1, Comp.2
scratch = np.array([10.0, 20.0, 100.0, 100.0])

ref_idx = np.argmin(d99_nm)
d99_ref = d99_nm[ref_idx]
scratch_ref = scratch[ref_idx]
ln_d = np.log(d99_nm / d99_ref)
ln_s = np.log(scratch / scratch_ref)
mask = d99_nm != d99_ref
n_fit = float(np.sum(ln_d[mask] * ln_s[mask]) / np.sum(ln_d[mask] * ln_d[mask]))

pred = scratch_ref * (d99_nm / d99_ref) ** n_fit
ss_res = float(np.sum((scratch - pred) ** 2))
ss_tot = float(np.sum((scratch - np.mean(scratch)) ** 2))
r2 = 1.0 - ss_res / ss_tot

print(f"재산출: n = {n_fit:.4f}, R^2 = {r2:.4f}")
assert abs(n_fit - 1.444) < 0.01, f"재산출 n({n_fit:.4f})이 채택값 1.444와 어긋난다"
assert r2 > 0.99, f"R^2({r2:.4f})가 노트에 기록한 0.997과 크게 어긋난다"

# 정량 대조: D99가 기준점의 2배로 커질 때 구 기본값(n=3.0) vs 신 채택값(n=1.444)
ratio = 2.0
old_mult = ratio ** 3.0
new_mult = ratio ** n_fit
overestimate_pct = (old_mult - new_mult) / old_mult * 100
print(f"D99 x2 what-if: n=3.0 -> {old_mult:.3f}배, n={n_fit:.3f} -> {new_mult:.3f}배, "
      f"과대추정 {overestimate_pct:.1f}%")
assert old_mult > new_mult, "구 기본값(n=3.0)이 신 채택값보다 배수가 커야 한다(과대추정 방향)"
assert 60.0 < overestimate_pct < 70.0, f"과대추정폭이 예상 범위(60~70%) 밖이다: {overestimate_pct:.1f}%"
```

### 8.1 코드 반영
- `knowledge/params/base.yaml`에 `damage_exponent`(value=1.44, unit="-",
  source=본 노트 §3, confidence=literature) 기본값 신설 — 이전에는 `sim/factors.py`
  코드 리터럴(`pk.get_or("damage_exponent", 3.0)`)이었다. `_f_delta`는 이제
  `pk.get("damage_exponent")`로 읽는다(값이 없으면 조용히 3.0을 지어내지 않고
  `ParamMissing`으로 멈춘다).
- `cu_h2o2_bta` / `oxide_silica` / `sti_ceria` / `w_fe_oxidizer` 4팩은 이미 화학종별
  값(1.44 또는 Egan&Kim 2019 기하평균 2.54)으로 이 기본값을 덮어쓰고 있었다(2026-09-13
  선행 회차, [[delta-scratch-damage-d99-oversize-particle-model]] §4.3) — 이번 판정은
  그 값들을 바꾸지 않는다. 바뀐 것은 **base 기본값**(코드 리터럴 3.0 → YAML literature
  1.44)과 **confidence 산출 방식**(하드코딩된 `unverified` → 드라이버/지수 등급 중 나쁜
  쪽, `_worst_conf`)뿐이다.
- `sic_ceria_h2o2`는 `base: sti_ceria` 상속으로 damage_exponent=1.44(literature)를
  간접 승계한다 — 별도 선언 불필요.

### 8.2 한계 (여전히 유효)
- 표본 크기: 세리아 1개 화학종, 실질 독립 3점(Comp.1=Comp.2 동일값) — §3.2와 동일.
- 다른 팩(실리카·알루미나)으로의 n=1.44 외삽은 미검증 — cu_h2o2_bta/w_fe_oxidizer는
  이미 자기 화학종 값(2.54, Egan&Kim 2019)으로 덮어써 이 한계 밖에 있다.
- C(Remsen 2006)는 물리량이 다른 교차확증이지 수치 출처가 아니다 — n=1.444는 B 단독 값.

## 8. 출처 링크 (품질게이트 URL/DOI 요구 보강)
- 원문 특허 페이지: https://patents.google.com/patent/US8439995B2/en
- PDF 원문: https://patentimages.storage.googleapis.com/53/4b/0a/39916f60c1d021/US8439995.pdf
  (로컬 저장: papers/US8439995-hitachi-ceria-d99-scratch.pdf)
- 인용 선행문헌(원문 명시, 스크래치-조대입자 관계의 배경): JP2000-026840, JP평2-371267,
  JP10-154673 (일본 공개특허공보, 원문 본문에서 직접 인용됨).
- 교차참조 문헌(Versum, 세리아코팅 실리카): https://patents.google.com/patent/US20190127607A1/en

## 9. § D99 등급 판정(2026-09-14) — abrasive_d99_nm confidence 일관성 감사

### 9.1 발견된 모순
완성 격자 감사 중 `abrasive_d99_nm`의 팩별 confidence가 근거 강도와 **역전**되어 있음을
확인했다:
- `sti_ceria`(및 상속하는 `sic_ceria_h2o2`): D99=700nm, **본 노트 §2.2 Hitachi 특허
  Example 1의 직접 실측값**(화학종=세리아, 용도=STI/ILD 산화막 CMP 둘 다 일치). 그런데
  confidence=**estimated**였다.
- `w_fe_oxidizer`: D99=750nm = abrasive_size_nm(150nm) × D99/D50 **일반비 5.00**
  (Silco/Levitronix 2008 산업 컨퍼런스 슬라이드, 2차 자료, 동료심사 없음). 노트 자신이
  "알루미나 D99 실측값은 미확보(5회 탐색 실패)"라고 자백한다. 그런데 confidence=**literature**
  — sti_ceria보다 **높았다**.

측정값을 다른 팩으로 이식한 것(sti_ceria)이, 실측 자체가 없다고 자백한 유도값(w_fe_oxidizer)
보다 낮은 등급을 받는 것은 EVIDENCE-RULES.md 서열(E1~E6, "이론과 충돌하면 실측이 이긴다")과
정면 모순이다.

### 9.2 등급 판정
**A: sti_ceria/sic_ceria_h2o2의 D99=700nm** — Hitachi 특허 Example 1 실측값을 화학종·용도가
일치하는 다른 팩의 baseline으로 이식. 값의 *출처*는 실측(원문 표, §2.2)이나, *적용 대상*은
이 팩 고유의 조성이 아니다(팩 자신이 "실제 조성값 아님"이라 명시). 이 구조는 이 팩의
`abrasive_size_nm`(60nm, Dandu 2009 실측값을 그대로 이식, confidence=literature)과 **완전히
같은 패턴**이다 — 둘 다 "화학종·조건이 일치하는 1차 문헌의 실측값을 이 팩의 baseline으로
채택"이다. 등급: **E2**(1차 문헌 실측 + 계 근접도 높음, 단 이 팩 고유 측정이 아니라
verified는 아님) → **literature**가 정직한 등급.

**B: cu_h2o2_bta/w_fe_oxidizer/oxide_silica의 D99(500/750/250nm)** — `abrasive_size_nm ×
D99/D50 일반비 5.00` 유도. 일반비 5.00의 출처(Levitronix/Silco 2008)는 원 노트
([[delta-scratch-damage-d99-oversize-particle-model]] §2.4)가 스스로 "산업 컨퍼런스
슬라이드(2차 자료, 동료심사 없음)"라고 표기한 것이다 — 알루미나·실리카 특정 값이 아니라
슬러리 일반 통계다. 등급: **E4/E5**(전이 유도 + 미검증 일반비 상수) → **estimated**가
정직한 등급. (Showa Denko US6770218B2 상한 대조·Fuso LPC bin 오더 일치는 "값이 상한을
넘지 않는다"/"오더가 맞다"는 정황일 뿐, 일반비 5.00 자체나 특정 D99 값을 검증하지 않는다.)

### 9.3 핵심 재현 검증 — "5.00이 실측 세리아 데이터에서 재현되는가?"
과제가 요구한 핵심 질문: D99/D50 일반비 5.00이 우리가 가진 유일한 실측 D99-D50 대응쌍
(본 노트 §2.2 Hitachi 4점)에서 실제로 재현되는가?

```python verify
import numpy as np

# US8439995B2 §2.2 원문 표 그대로 (D50, D99 실측 대응쌍)
labels = ["Ex.1", "Ex.2", "Comp.1", "Comp.2"]
d50_nm = np.array([190.0, 160.0, 240.0, 240.0])
d99_nm = np.array([700.0, 500.0, 2500.0, 2500.0])
ratios = d99_nm / d50_nm

print("실측 D99/D50 비:", dict(zip(labels, ratios.round(3))))
# 제어된 예(Ex.1/Ex.2, 같은 슬러리계·침강시간만 다름)의 비
ratio_ex1, ratio_ex2 = ratios[0], ratios[1]
GENERIC_RATIO = 5.00  # Levitronix/Silco 2008, cu_h2o2_bta/w_fe_oxidizer/oxide_silica가 쓰는 값

dev_ex1_pct = abs(GENERIC_RATIO - ratio_ex1) / ratio_ex1 * 100
dev_ex2_pct = abs(GENERIC_RATIO - ratio_ex2) / ratio_ex2 * 100
print(f"일반비 5.00 vs Ex.1 실측비({ratio_ex1:.3f}) 괴리: {dev_ex1_pct:.1f}%")
print(f"일반비 5.00 vs Ex.2 실측비({ratio_ex2:.3f}) 괴리: {dev_ex2_pct:.1f}%")

# 핵심 주장: 일반비 5.00은 우리가 가진 유일한 실측 세리아 대응쌍을 30% 넘게 벗어난다
# → "재현되지 않는다"가 이 검증의 결론이다(재현됐다면 유도법의 신뢰도가 올라갔을 것이나,
#   실제로는 반대 방향으로 나왔다 — 그대로 기록한다).
assert dev_ex1_pct > 30.0, f"Ex.1 괴리가 예상보다 작다({dev_ex1_pct:.1f}%) — 재검토 필요"
assert dev_ex2_pct > 30.0, f"Ex.2 괴리가 예상보다 작다({dev_ex2_pct:.1f}%) — 재검토 필요"

# 조대입자 비교예(필터만, 침강 짧음)에서는 반대 방향으로 더 크게 벗어난다(10.4배)
ratio_comp = ratios[2]
assert ratio_comp > GENERIC_RATIO, "조대입자 비교예 비가 일반비보다 커야 한다(꼬리가 더 두꺼움)"
print(f"비교예(Comp.1/2) 실측비 {ratio_comp:.3f} — 일반비의 {ratio_comp/GENERIC_RATIO:.2f}배")

# ── sti_ceria 자신의 D50(60nm, Dandu 2009)에 일반비를 적용하면 무엇이 나오는가? ──
# baseline 이식값(700nm, Hitachi Ex.1)과 비교 — 두 유도 경로가 서로 다른 값을 준다는 것을
# 보여준다(하나를 정답으로 검증하는 게 아니라 "방법 간 불일치 자체"가 증거).
sti_ceria_d50_nm = 60.0
generic_d99_for_sti = sti_ceria_d50_nm * GENERIC_RATIO
transplanted_d99_for_sti = 700.0  # 현재 sti_ceria.yaml abrasive_d99_nm
divergence_factor = transplanted_d99_for_sti / generic_d99_for_sti
print(f"sti_ceria D50(60nm)에 일반비 5.00 적용 -> {generic_d99_for_sti:.0f}nm, "
      f"현재 채택값(Hitachi 실측 이식) {transplanted_d99_for_sti:.0f}nm, "
      f"괴리 배수 {divergence_factor:.2f}x")
assert divergence_factor > 2.0, "두 유도 경로(일반비 vs 실측 이식)의 괴리가 예상보다 작다"

print("결론: 일반비 5.00은 유일하게 확보한 실측 세리아 데이터를 재현하지 못한다"
      " (30~60% 괴리, 방향도 예-비교예 사이에서 뒤집힘)."
      " -> B(일반비 유도)의 등급을 A(실측 이식)보다 높게 줄 근거가 없다.")
```

**재현 결과**(US8439995B2 §2.2 표 재계산): 일반비 5.00은 제어된 실측 예(Ex.1 괴리 35.7%, Ex.2 괴리 60.0%)를 재현하지
못했고, 조대입자 비교예에서는 반대로 실측비(10.42)가 일반비보다 2배 이상 크다 — 즉 하나의
고정 비율로 세리아계조차 대표할 수 없다(방향도 예에 따라 뒤집힌다). sti_ceria 자신의
D50(60nm)에 일반비를 적용하면 300nm가 나와, 현재 baseline 이식값(700nm)과 2.33배
벌어진다. **일반비 유도법은 이 노트가 가진 유일한 실측 대조군에서 재현되지 않는다** — 이
결과는 B(일반비 유도, cu_h2o2_bta/w_fe_oxidizer/oxide_silica)의 등급을 A(실측 이식,
sti_ceria)보다 높게 줄 근거가 전혀 없음을 정량으로 확인해준다.

### 9.4 판정 및 코드 반영
- `knowledge/params/sti_ceria.yaml`의 `abrasive_d99_nm`/`abrasive_ref_d99_nm`:
  `estimated` → **`literature`**로 상향. `sic_ceria_h2o2`는 `base: sti_ceria` 상속으로
  자동 승계(별도 선언 없음).
- `knowledge/params/w_fe_oxidizer.yaml` / `cu_h2o2_bta.yaml` / `oxide_silica.yaml`의
  `abrasive_d99_nm`/`abrasive_ref_d99_nm`: `literature` → **`estimated`**로 하향.
- EVIDENCE-RULES.md 판정 기록 표 #16으로 등재.
- 격자 영향은 목표가 아니다 — `damage_exponent`의 팩별 confidence(이미 §7~§8에서 확정,
  변경 없음)와 `_worst_conf`로 조합되므로, 델타 팩터의 최종 confidence는 두 파라미터 중
  나쁜 쪽을 그대로 따른다(`sim/factors.py::_f_delta`). 실제 격자 변화는
  `tools/completion.py check` 출력으로 확인하고 그대로 보고한다.

### 9.5 한계
- 이 판정도 "5.00이 세리아에서 재현 안 됨"만 확인했을 뿐, 알루미나계 자체의 D99/D50 비를
  실측으로 대체한 것은 아니다 — B(cu_h2o2_bta/w_fe_oxidizer/oxide_silica)를 `estimated`로
  낮췄을 뿐 더 나은 값으로 교체하지 않았다. 알루미나 D99 실측값 확보는 여전히 미해결
  과제([[delta-scratch-damage-d99-oversize-particle-model]] §9 "다음 단원" 참조).
- A(sti_ceria)도 `verified`는 아니다 — 이 팩 고유 조성에서 D99를 직접 측정한 것이 아니라
  타 특허 실시예의 이식이라는 한계는 그대로 남는다.

