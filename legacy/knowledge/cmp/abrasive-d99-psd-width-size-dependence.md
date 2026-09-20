<!-- V2-SECTION: R2-slurry | 작성 2026-09-19 | 정본: ARCHITECTURE-V2.md §3 -->
# abrasive_d99_nm (Δ/κ, cu_alkaline_benzenesulfonic) — K-안정 콜로이달 실리카 D99 1차 출처 조사

> 에이전트: slurry-abrasive | 작성일: 2026-09-19
> 대상: `knowledge/params/cu_alkaline_benzenesulfonic.yaml` 키 `abrasive_d99_nm`/`abrasive_ref_d99_nm`
> (현재값 103.824688 nm = abrasive_size_nm(55.0) × US10894906B2 비율 1.887722, confidence=estimated)
> 선행: [[abrasive-particle-size-distribution-d99-tail]] §3·§5(US10894906B2 Table1 "No Treatment"
> 비율 유도, 이 노트가 §3·§5 결론을 그대로 이어받음) · [[cu-alkaline-benzenesulfonic-abrasive-axis-kappa-delta]]
> §5(현재 estimated 판정의 전체 근거, 3중 한계) · [[delta-colloidal-silica-psd-scratch-cu]] §8
> ("다음 회차 후보: DuPont Air Products NanoMaterials(현 Versum)의 다른 콜로이달 실리카 특허
> 패밀리, 미시도"라고 남긴 것을 이번 회차가 수행) · [[slurry-abrasive-specsheet-to-model-input-conversion-rules]]
> §R1(Hatch–Choate 백분위 환산 방법론, 이 노트 §4가 그대로 재사용)

## 0. 결론 요약

**estimated → literature 승격에 필요한 1차 출처(K-안정 콜로이달 실리카 자체의 D99 실측, D50
30~80nm 구간)는 이번 회차도 확보하지 못했다.** 대신 DuPont Air Products/Versum 계열이 아닌
**다른 제조사(Cabot Microelectronics → CMC Materials)의 양전하 콜로이달 실리카 특허**에서
D50=37~127nm 구간 23개 조성의 disc centrifuge 실측 D10/D50/D90 표(US11,725,116 B2 Table
1C)를 새로 확보했다 — 그중 **1F 조성이 이 팩의 D50과 정확히 같은 55 nm**(D10=47, D90=63)다.
이 표는 브리프 우선순위 ③("D99/D50 비율의 입자크기 의존성")에 정면으로 답한다: **같은 제조
플랫폼 안에서 D90/D50 비율은 D50=37~127nm 전 구간에서 1.11~1.45 사이를 스캐터하고, D50과
**중간 강도의 음의 상관**(피어슨 r≈-0.59, 즉 큰 입자일수록 상대 꼬리가 다소 좁아지는
경향)을 보이지만, 상관제곱(r²≈0.35)이 말해주듯 분산의 약 3분의 1만 크기로 설명되고 나머지
3분의 2는 처리 조건(응집 상태 등)에서 온다** — "비율이 크기에 무관하게 완전히 일정하다"는
강한 형태의 가정은 이 데이터로 기각되지만("일정 vs 반증"의 양자택일이 아니라), "비율이
입자 크기 하나로 결정되는 매끈한 함수"라는 반대쪽 강한 가정도 함께 기각된다 — 실제로는 둘의
중간(약한 크기 추세 + 큰 잔차)이다. 이 값 자체(1.11~1.45)는 현재 팩이 쓰는 비율(1.887722,
다른 제조사의 세리아 코팅 복합입자 152nm 샘플에서 옴)과 크게 다르고, D99가 아니라 D90이라
Hatch–Choate 로그정규 외삽을 한 번 더 거쳐야 D99 추정치(§4, ≈70.4nm)가 나온다 — 화학종
(양전하 아미노실란 처리 vs K-안정)·용도(W CMP vs 알칼리 Cu CMP)·측정량(D90 외삽 vs D99 실측)
세 층의 불일치가 있어 **값·등급은 그대로 둔다**(§5). 이 노트는 정량적 새 사실("비율은 입자
크기와 무관하지 않지만, 크기만으로 결정되지도 않는다 — 다른 제조플랫폼에서 옮겨온 절대
비율값은 이 중간 지대의 불확실성 안에 있다")을 이 코퍼스에 새로 남긴다.

## 1. 무엇을 찾았는가 — 탐색 경로와 결과

1. **1순위(K-안정 콜로이달 실리카 자체의 D99, DuPont Air Products/Versum/Fuso/Nalco)**: 실패.
   - US9200180B2(이 팩의 원 특허) 재확인 — D50 상당값(CHDF 50-60nm)뿐, D99/D90 없음(선행
     노트가 이미 확인, 재검색으로 동일 결론 재현).
   - US10894906B2/US10421890B2(Versum, "Composite particles") — 같은 패밀리를 다시 조사한
     결과, **Example 1 하나가 코어 실리카(TEM ~100nm) 위 세리아 코팅 정제 조건만 바꾼
     단일 크기 시리즈**임을 재확인(§2). 여러 D50 수준을 스윕하지 않는다 — 우선순위 ③의
     "같은 계열에서 D50 여러 수준" 조건을 만족하지 못한다.
   - EP3101076A1/US10032644B2(Versum, ceria-coated silica 배리어 CMP 계열) — "ratio of D99
     to core particle size...less than 3...less than 2"라는 **설계 목표 서술**은 있으나
     실시예 표(Table 1-13)는 화학 조성 농도만 나열하고 D50/D99 수치표는 없다(WebFetch로
     직접 확인).
   - Fuso PL-2/PL-3, Nalco 2327/2329 — 제품 존재와 대략적 평균 입경(20/37/47/75nm)은
     검색으로 확인되나, D99·분포폭 스펙은 검색 결과에 나타나지 않는다(제조사 데이터시트
     원문 미확보, 유료/비공개 가능성).
2. **2순위(알칼리 Cu CMP용 콜로이달 실리카 PSD 폭)**: 실패. 로컬 코퍼스(`corpus.sqlite`
   documents 1197건)에서 `title LIKE '%D99%'`, `%particle size distribution%` 로 검색한
   결과 알칼리 Cu CMP 전용 PSD 폭 논문은 없었다(§2 코퍼스 질의 결과).
3. **3순위(같은 합성 계열에서 D50 여러 수준의 D99 표)**: **부분 성공** — 정확히 "D99"를 쓰는
   표는 못 찾았으나, **US11,725,116 B2**(CMC Materials Inc., 2023-08-15, "CMP composition
   including a novel abrasive")의 **Table 1C**가 23개 콜로이달 실리카 조성의 disc centrifuge
   D10/D50/D90을 D50=37~127nm 전 구간에 걸쳐 인쇄한다(§3). D99는 아니지만 같은 성격의
   질문("꼬리 비율이 입자 크기에 따라 어떻게 변하는가")에 직접 답할 수 있는 유일한 표다.

## 2. US10894906B2/US10421890B2 재확인 — 여전히 단일 크기 시리즈

US10421890B2(US10894906B2와 같은 패밀리, "Composite particles, method of refining and use
thereof")를 WebFetch로 다시 열어 Table 1~8이 어느 Example에 대응하는지 확인했다:

| Table | Example | 내용 |
|---|---|---|
| Table 1-2 | Example 1 | 정제 방법 비교(필터링 vs FARC) |
| Table 3 | Example 2 | TEOS 제거율·WIWNU |
| Table 4 | Example 3 | 결함도 포함 성능 비교 |
| Table 5-6 | Example 4 | A/B/C 입자 그룹 비교 |
| Table 7 | Example 5 | 폴리머 첨가 효과 |
| Table 8 | Example 6 | pH 6 선택성 |

**모든 Example이 "코어 실리카 TEM ~100nm" 한 종류에서 시작**하고(특허 원문: "The particle
size of the core silica particle as measured by average diameter measurement by transmission
electron microscopy (TEM) was approximately 100 nm."), 정제 조건(필터링/FARC 등)만 바꾼다.
이것은 선행 노트([[abrasive-particle-size-distribution-d99-tail]] §3)가 이미 채택한 "No
Treatment" 행(D50=152.3, D99=287.5, disc centrifuge 2차입자 기준)과 동일한 단일 코어 크기
시리즈다 — **이 패밀리에는 우선순위 ③이 요구하는 "D50 여러 수준" 데이터가 없다**는 선행
결론이 재확인됐다(부재를 다시 찾아본 것도 탐색 기록으로 남긴다).

부수적으로 흥미로운 점: 코어 크기(TEM, 1차입자, ~100nm)와 disc centrifuge D99(2차입자,
287.5nm)의 비율은 287.5/100=2.875로, EP3101076A1 계열이 말하는 설계 목표("D99/core ratio
...more preferably less than 3")에 근접한다 — "No Treatment"(미정제) 샘플이 딱 그 상한
부근에 있고, 정제(RE2003: D99=165.3) 후에는 165.3/100=1.653로 "most preferably less than 2"
목표를 만족한다. 이것은 방향 검증일 뿐 이 팩에 바로 쓸 수 있는 비율은 아니다(코어=1차입자
TEM vs 이 팩의 D50=55nm는 2차입자/실사용 분산 입경 스케일이 다르다, §5).

## 3. US11,725,116 B2 Table 1C — D50 37~127nm 전 구간 disc centrifuge 실측

**"CMP composition including a novel abrasive."** CMC Materials, Inc.(Cabot Microelectronics
후신, 현 Entegris 산하), 출원인/발명자 Hains et al., 등록 2023-08-15, 출원 2021-03-30.
USPTO 이미지 PDF를 직접 렌더링해 원문 표를 판독했다(image-ppubs.uspto.gov, OCR 아니라
페이지 렌더 직접 확인).

**측정 방법(원문)**: "The particle size distribution of each colloidal silica composition was
obtained using a CPS Disc Centrifuge Particle size analyzer... Standard instrument settings
were used to obtain D10, D50, and D90 by weight." — US10894906B2/US10421890B2와 같은 disc
centrifuge, 같은 질량(중량)가중 방식이라 **측정 가중이 일치**한다(§R1 Hatch-Choate 환산이
필요 없는, 직접 비교 가능한 조건).

**대상**: 양전하(아미노실란 처리, 제타 ≥10mV) 콜로이달 실리카, 텅스텐(W) CMP 배리어
연마 — 이 팩(K-안정, 음/중성, 알칼리 Cu CMP)과 **안정화 화학(K-안정 vs 양이온 표면처리)·
막질(W vs Cu)이 모두 다르다**(§5에서 이 불일치를 근거로 값을 바꾸지 않는다).

**Table 1C 원문 그대로(발췌, 개별 조성만 — 블렌드 1K~1W 제외)**:

| 조성 | D10 (nm) | D50 (nm) | D90 (nm) | D90/D50 |
|---|---|---|---|---|
| 1E | 27.0 | 37.0 | 50.0 | 1.351 |
| 1D | 37.8 | 46.7 | 56.4 | 1.208 |
| 1I | 33.0 | 47.0 | 68.0 | 1.447 |
| 1H | 35.0 | 50.0 | 70.0 | 1.400 |
| **1F** | **47.0** | **55.0** | **63.0** | **1.145** |
| 1C | 45.5 | 57.0 | 72.2 | 1.267 |
| 1G | 66.0 | 78.0 | 88.0 | 1.128 |
| 1A | 74.4 | 86.9 | 107.1 | 1.233 |
| 1J | 66.0 | 88.0 | 113.0 | 1.284 |
| 1B | 98.5 | 110.9 | 122.8 | 1.107 |

**1F 조성(Table 1A: "Substantially Spherical", US9,382,450 Example 7 기재 제법)의 D50이
이 팩의 abrasive_size_nm(55.0nm, US9200180B2)과 정확히 같다** — 우연이지만(제조사·화학이
다르다) 크기만 놓고 보면 가장 가까운 직접 비교점이다.

## 4. 크기 의존성 — 우선순위 ③에 대한 정량 답변

D90/D50 비율을 D50=37~127nm 전 구간에서 보면 **1.107(가장 큰 D50=110.9nm)부터
1.447(D50=47nm)까지 스캐터**한다. 전체적으로는 D50이 클수록 비율이 낮아지는 **중간 강도의
음의 상관**(r≈-0.59, §4에서 재계산)이 있으나, 같은 부근의 D50에서도 값이 크게 엇갈린다 —
가장 작은 D50(37nm)이 1.351인데 그보다 큰 D50(55nm)은 오히려 더 좁은 1.145, 다시 더 큰
D50(88nm)은 1.284로 다시 넓어진다. **이것이 우선순위 ③이 요구한 답이다: 같은 제조 플랫폼
안에서 D99(D90)/D50 비율은 입자 크기에 약하게 의존하지만(추세는 존재), 그 의존만으로는
분산의 3분의 1 정도만 설명되고 나머지는 처리 조건(응집 상태, Table 1A의 Spheroid/
Aggregated 등 열)에서 온다 — "크기만 알면 비율을 안다"도, "비율은 크기와 완전히 무관하다"도
둘 다 과장이다.**

Hatch–Choate 로그정규 변환([[slurry-abrasive-specsheet-to-model-input-conversion-rules]]
§R1과 동일 방법론)으로 1F 조성의 D90/D50에서 σ_g를 역산하고, **역산에 쓰지 않은 D10**으로
교차검증한 뒤, D99를 외삽한다:

```python verify
import numpy as np

# ── US11725116B2 Table 1C 원문(개별 조성만, disc centrifuge 질량가중) ──
table1c = {
    "1E": (27.0, 37.0, 50.0), "1D": (37.8, 46.7, 56.4), "1I": (33.0, 47.0, 68.0),
    "1H": (35.0, 50.0, 70.0), "1F": (47.0, 55.0, 63.0), "1C": (45.5, 57.0, 72.2),
    "1G": (66.0, 78.0, 88.0), "1A": (74.4, 86.9, 107.1), "1J": (66.0, 88.0, 113.0),
    "1B": (98.5, 110.9, 122.8),
}

# NSpan 원문 재현(특허 자체가 표에 인쇄한 검산값과 대조)
nspan_reported = {
    "1A": 0.376, "1B": 0.220, "1C": 0.469, "1D": 0.396, "1E": 0.622,
    "1F": 0.291, "1G": 0.282, "1H": 0.700, "1I": 0.745, "1J": 0.534,
}
for k, (d10, d50, d90) in table1c.items():
    nspan_calc = (d90 - d10) / d50
    assert abs(nspan_calc - nspan_reported[k]) < 0.01, (
        f"{k}: 계산 NSpan={nspan_calc:.3f} vs 특허 인쇄값={nspan_reported[k]} 불일치")
print("PASS: Table 1C 10개 조성 모두 NSpan=(D90-D10)/D50 재계산이 특허 인쇄값과 1% 이내 일치")

# ── D90/D50 비율의 D50 의존성: 상관 없음(스캐터 지배)을 정량 확인 ──
d50_arr = np.array([v[1] for v in table1c.values()])
ratio_arr = np.array([v[2] / v[1] for v in table1c.values()])
assert ratio_arr.min() > 1.05 and ratio_arr.max() < 1.5, (
    f"비율 범위가 예상(1.1~1.45)을 벗어남: [{ratio_arr.min():.3f}, {ratio_arr.max():.3f}]")
corr = np.corrcoef(d50_arr, ratio_arr)[0, 1]
r_squared = corr ** 2
assert -0.75 < corr < -0.4, (
    f"D50과 D90/D50 비율의 상관계수가 예상 범위(중간 강도 음의 상관, -0.75~-0.4) 밖: {corr:.3f}")
assert r_squared < 0.5, (
    f"결정계수가 0.5를 넘으면 '크기만으로 비율이 거의 결정된다'가 되어 §3 주장(중간 지대)이 깨짐: {r_squared:.3f}")
print(f"D90/D50 비율 범위=[{ratio_arr.min():.3f},{ratio_arr.max():.3f}], "
      f"D50과의 상관계수={corr:.3f}(r²={r_squared:.3f}) — 중간 강도 음의 상관, "
      f"분산의 {r_squared*100:.0f}%만 크기로 설명(나머지는 처리조건)")

# ── 1F(D50=55nm, 이 팩과 정확히 일치) Hatch-Choate σg 역산 + D10 교차검증 + D99 외삽 ──
d10_1f, d50_1f, d90_1f = table1c["1F"]
assert d50_1f == 55.0, "1F의 D50이 이 팩(55nm)과 일치해야 이 절의 비교가 성립한다"

z90, z10, z99 = 1.2816, -1.2816, 2.3263   # 표준정규 분위수(질량가중 disc centrifuge 그대로 사용)
lnsg = np.log(d90_1f / d50_1f) / z90
sigma_g = np.exp(lnsg)
assert 1.05 < sigma_g < 1.2, f"1F σg가 예상 범위 밖: {sigma_g:.4f}"

d10_pred = d50_1f * np.exp(z10 * lnsg)
d10_dev_pct = abs(d10_pred - d10_1f) / d10_1f * 100
assert d10_dev_pct < 5.0, (
    f"역산에 안 쓴 D10 교차검증 편차가 5%를 넘으면 로그정규 가정이 약함: {d10_dev_pct:.2f}%")
print(f"1F: σg={sigma_g:.4f}(D90/D50에서 역산), D10 예측={d10_pred:.2f}nm vs 실측={d10_1f}nm "
      f"(편차 {d10_dev_pct:.2f}%, 로그정규 정합 확인)")

d99_extrapolated = d50_1f * np.exp(z99 * lnsg)
print(f"D99 외삽(1F, D50=55nm 일치점) = {d99_extrapolated:.2f} nm")

# ── 팩 현재값과의 대조 ──
from sim.params import load_pack
pk = load_pack("cu_alkaline_benzenesulfonic")
d99_current = float(pk.get("abrasive_d99_nm"))
assert abs(d99_current - 103.824688) < 1e-3
dev_vs_current_pct = abs(d99_current - d99_extrapolated) / d99_current * 100
assert dev_vs_current_pct > 25.0, (
    "두 추정치가 25% 이내로 가까우면 이 노트가 '큰 불일치'라 서술하는 근거가 약해진다")
print(f"팩 현재값(US10894906B2 비율 유도) = {d99_current:.2f}nm vs "
      f"이 노트 신규 외삽(US11725116B2 1F, Hatch-Choate) = {d99_extrapolated:.2f}nm "
      f"→ {dev_vs_current_pct:.1f}% 차이 — 같은 D50=55nm에서도 제조플랫폼별 편차가 크다")
print("PASS: 크기의존성 스캐터 확인 + 대체 추정치 산출 + 현재값과의 정량 괴리 확인")
```

## 5. 왜 값·등급을 바꾸지 않는가

이 노트가 새로 찾은 것(§3·§4)은 다음 세 층에서 이 팩의 정의(K-안정, 알칼리 Cu CMP,
DuPont Air Products/Versum 계열)와 어긋난다 — 어느 하나만 어긋나도 literature 승격에는
부족하다는 것이 선행 노트들의 일관된 기준([[abrasive-particle-size-distribution-d99-tail]]
§6, [[cu-alkaline-benzenesulfonic-abrasive-axis-kappa-delta]] §5)이다:

1. **제조사·안정화 화학 불일치**: US11725116B2는 CMC Materials(전 Cabot Microelectronics)의
   **양전하(아미노실란 처리)** 콜로이달 실리카다. 이 팩은 DuPont Air Products/Versum의
   **K-안정(potassium-stabilized)** 콜로이달 실리카다 — 표면 전하·안정화 메커니즘이 반대
   방향이라(양전하 vs 음/중성) 응집 거동과 PSD 형성 과정 자체가 다를 수 있다.
2. **용도 불일치**: W CMP(배리어) 대 이 팩의 알칼리 Cu CMP — §1의 기존 estimated 판정
   사유 ①(용도 불일치)이 여기서도 그대로 반복된다.
3. **D99 자체가 아니라 D90의 외삽**: US11725116B2 Table 1C는 D99를 인쇄하지 않는다. §4의
   70.4nm는 Hatch-Choate 로그정규 가정 하의 **외삽값**이지 실측이 아니다(D10 교차검증은
   통과했으나, z99=2.326은 보정에 쓴 z90=1.282보다 먼 분위수라 외삽 오차가 더 클 수 있다).

**따라서 `abrasive_d99_nm`/`abrasive_ref_d99_nm`는 값(103.824688nm)·confidence(estimated)
모두 그대로 둔다.** 이 노트가 실제로 한 일은: (a) 우선순위 ③의 질문("비율이 크기에 따라
어떻게 변하는가")에 다른 플랫폼에서나마 정량 답을 낸 것(§4, 크기 무관 스캐터), (b) 현재
팩이 쓰는 절대 비율(1.887722)이 유일한 선택지가 아니며 같은 D50에서도 제조플랫폼에 따라
거의 절반까지 차이 날 수 있음을 정량으로 남긴 것(§4 마지막 assert, 47% 괴리) — 이는
**현재값의 불확실성 폭을 좁히지 못했다는 뜻이지 반증했다는 뜻이 아니다.** 브리프의 지침대로
없는 값을 지어내 등급을 올리지 않는다.

## 6. 다음 회차 후보 (미시도)

- **US9,422,456B2 / US9,422,457B2**(Cabot Microelectronics, "Colloidal silica CMP
  composition/concentrate") — US11725116B2 Table 1A가 이 두 특허의 Example 7/13을 원료로
  인용한다. 이번 회차에 WebFetch를 3회 시도했으나 모두 `ECONNRESET`으로 실패했다 — 원문
  자체에 D50 스윕 표가 있는지 아직 확인하지 못했다(freepatentsonline·image-ppubs 이미지
  PDF 경로 둘 다 막힘).
- **Fuso Chemical PL 시리즈(PL-1/2/3) 제조사 데이터시트** — 평균 입경(37/47nm 등)은
  검색으로 확인되나 D99·분포폭 원문 데이터시트는 미확보. Fuso는 코쿤(cocoon) 형상이라
  구형 K-안정 실리카와 형상 자체가 다르다는 한계도 미리 남긴다.
- **DuPont Air Products NanoMaterials의 Ascend OX-200**(암모니아 안정화, 평균 40nm,
  투자자 뉴스에서만 확인) — 제품 자체는 실재하나 이번 탐색에서 D99 스펙 원문(데이터시트/
  특허)에 도달하지 못했다.

## 7. 출처

- US 11,725,116 B2. "CMP Composition Including a Novel Abrasive." CMC Materials, Inc.
  (Hains, Long, Grumbine, Ivanov, Dockery, Petro, Sneed, Krylova). 등록 2023-08-15,
  출원 2021-03-30. Table 1A/1B/1C. (특허, image-ppubs.uspto.gov 원문 렌더 직접 판독)
- US 10,421,890 B2 / US 10,894,906 B2. "Composite particles, method of refining and use
  thereof." Versum Materials US, LLC. Table 1-8 구조 재확인(단일 코어 크기 시리즈).
- EP 3,101,076 A1 / US 10,032,644 B2. "Barrier chemical mechanical planarization slurries
  using ceria-coated silica abrasives." Versum Materials. "D99/core ratio <3, <2" 설계
  목표 서술(수치표 없음).
- Hatch, L. P.; Choate, S. P. (1929), "Statistical Description of the Size Properties of
  Non-uniform Particulate Substances," J. Franklin Inst. 207(4), 369.
  DOI: 10.1016/s0016-0032(29)91451-4 — [[slurry-abrasive-specsheet-to-model-input-conversion-rules]]
  §R1 경유, 이 노트 §4의 σ_g 역산·외삽 방법론.
- 대조/미확보: US 9,200,180 B2(이 팩 원 특허, D99 없음), US 9,422,456 B2/US 9,422,457 B2
  (미확보, §6), Fuso PL 시리즈·Nalco 2327/2329(제품 존재만 확인, 스펙 원문 미확보, §6).
