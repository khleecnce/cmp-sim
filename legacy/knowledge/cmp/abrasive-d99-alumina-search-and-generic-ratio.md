<!-- V2-SECTION: R2-slurry | 작성 2026-09-09 | 정본: ARCHITECTURE-V2.md §3 -->
# 알루미나 계열 D99 재탐색 + 일반 슬러리 D50/D99 세대별 비율 (Δ 손상 유발도 팩터)

> 에이전트: slurry-abrasive Lv2-1 (선행: [[abrasive-d99-spec-cross-pack-comparison]])
> [[abrasive-d99-spec-cross-pack-comparison]] [[abrasive-d99-composite-particle-versum2019]]
> [[lpc-scratch-density-tail-correlation]]

## 1. 목표
직전 노트(abrasive-d99-spec-cross-pack-comparison)에서 세리아 계열 D99는 확보했으나
알루미나 계열(cu_h2o2_bta, w_fe_oxidizer 팩의 화학종)은 "미확보"로 남겼다. 이번 회차는
① 알루미나 제조사·특허 실시예에서 D99를 다시 탐색하고, ② 실패 시 대안으로 업계 일반
D50→D99 비율(제조 세대별)을 추가 확보해 `damage_exponent` 상한/하한 참고치를 보강한다.

## 2. 탐색 시도와 결과 (실패 기록 — 정직하게)

### 2.1 특허 탐색 (실패)
다음 특허를 원문 확인했으나 알루미나 D99(90/99th percentile)를 명시한 것은 없었다:
- US11117239B2 (Applied Materials 계열, colloidal/calcined alumina) — 평균 입경만 명시
  (colloidal 50~90nm, calcined 140nm), **D99/D90 percentile 데이터 없음**.
- US9566686B2 (Cabot, W CMP, colloidal silica 중심) — 평균 입경(mean particle size 75nm)만,
  알루미나 관련 percentile 없음.
- JP5204226B2 (아루미늄 산화물 입자·연마조성물, Ni-P 하드디스크 기판용) — **D90/D10 비율은
  명시**(≤3, 바람직 ≤2.0)하지만 D99 자체나 절대 nm 값은 실시예 표(Table 1, HTML 렌더링 깨짐으로
  본문 확보 실패)에만 있고 텍스트 추출로는 못 얻음 — **원문 표 미확보, 2차 파싱 실패**.
  scope.py 체크 결과 이 특허는 slurry-abrasive 조사범위 내(✓ 허용).

### 2.2 제조사 기술문서 탐색 (실패)
- Baikowski(SLA 알루미나 슬러리) 웹페이지 확인 — "tailor-made upon request" 소개 페이지만
  존재, PSD 스펙 수치 비공개(상업 페이지, 상세 스펙은 NDA 견적서로 추정).
- AluminaWorld(중국 알루미나 제조사) 기술 블로그 — **CMP 등급 콜로이달 알루미나 RFQ 스펙 템플릿**을
  공개: D50 50–80 nm, D90 120–180 nm, **D99 <200 nm**(일부 커스텀 등급 D99 <150nm 가능).
  ⚠ 이 출처는 학술지·특허가 아닌 **제조사 블로그(2차 상업 콘텐츠, 회사명 "AluminaWorld"·저자
  불명·개인 판단 신뢰도 중간)** — 품질게이트 규칙1(1차 출처 DOI/PMC/arXiv/특허 필수)을
  만족시키지 못한다. **참고치로만 기록하고 팩 파라미터에 대입하지 않는다.**

결론: 알루미나 계열은 이번 회차도 1차 출처(특허·논문) 기준 D99 미확보 유지.

## 3. 대안 확보 — 세대별 D50/D99 비율 (일반 슬러리, 알루미나 한정 아님)

Levitronix CMP Users Conference (2008-02-11) 발표자료, Silco Electronic Materials
(반도체 실리콘 전자소재 업체) "Handling and Filtration of CMP Slurries" — 산업 컨퍼런스
발표자료 원문 PDF 직접 확보(웹 아카이브 경유, onsemi.com 원본 호스팅 확인).
URL(원본, 현재 403): https://www.onsemi.com/site/pdf/handlingfiltrationandpolishing.pdf
URL(확보 경로, web.archive.org 스냅샷): http://web.archive.org/web/2020/https://www.onsemi.com/site/pdf/handlingfiltrationandpolishing.pdf

⚠ 이 문서는 학술 논문이 아니라 **산업 컨퍼런스 발표자료(2차 자료, 동료심사 없음)**이며 슬라이드
자체에 "CONFIDENTIAL"이 인쇄돼 있으나 현재 공개 인터넷(제조사 자사 웹사이트)에 정식 게시돼 있어
접근 자체는 합법적 공개 자료로 취급한다(사용자 지시: 무료·공개 소스 전체 활용). **일반 슬러리 통계이며
특정 화학종(알루미나 등) 전용이 아니다** — Δ 팩터에 직접 대입 불가, 참고 상한/하한용.

Slide "CMP Slurry Filtration: Changing Process Needs" (p.11):

| 세대 | D50 | D99 (mean size로 표기됨, 원문 그대로) | D99/D50 비율 |
|---|---|---|---|
| Earlier | 0.20 µm | 1 µm | 5.00 |
| New | 0.07 µm | 0.3 µm | 4.29 |
| Typical Next Target | 0.04 µm | 0.2 µm | 5.00 |

세 세대 모두 D99/D50 비율이 **4.29~5.00배**로 수렴 — 필터링 기술이 발전해도(D50이 0.20→0.04µm로
5배 축소) 상대적 꼬리 두께(D99/D50)는 거의 일정하게 유지된다는 정성적 시사점(n=3, 통계적으로
약함 — 같은 발표자료의 목표치 3개뿐).

## 4. 종합 — Δ 팩터 설계에 주는 시사점

이전 노트(세리아 코팅 실리카, D99/D50=1.82~3.82)와 이번 자료(일반 슬러리 세대별, D99/D50=4.29~5.00)를
합치면, **공개 문헌에서 관측된 D99/D50 비율의 범위는 약 1.8~5.0배**로 확장된다. 이는:
- 알루미나 전용 값이 여전히 없으므로 cu_h2o2_bta/w_fe_oxidizer 팩에 값을 넣을 근거는 없음(유지).
- `_f_delta`의 `damage_exponent`(현재 기본값 3.0, 미검증)이 이 넓은 범위의 중간값 근처에 있다는
  점은 우연의 일치 이상의 근거가 못 된다 — **여전히 미검증으로 유지**해야 한다(오해 방지, 이전
  노트와 동일 결론 반복 확인).
- 향후 알루미나 D99 확보 실패가 계속되면, 다음 회차는 **AluminaWorld류 상업 블로그 스펙(D99<200nm,
  D50 50–80nm → 비율 2.5~4.0배 내외)을 "2차 인용, 미검증"으로 명시적으로 참고치에만 편입**하는
  것을 고려할 수 있으나, 이번 회차는 품질게이트 1차 출처 규칙을 지켜 편입하지 않는다.

## 5. Δ 팩터 구현 요청 갱신 (소프트웨어 부문, `agents/slurry-abrasive/PROFILE.md`)
- 무엇을: 여전히 no-op. 알루미나 계열 D99 1차 출처 미확보 지속.
- 참고치 갱신(팩 파라미터 대입 금지): D99/D50 비율 관측 범위 **1.82~5.00배**(세리아 코팅
  실리카 1.82~3.82배 + 일반 슬러리 세대별 4.29~5.00배, 알루미나 미포함).
- 우선순위: 중(3회 연속 알루미나 미확보 — 접근 전환 필요. 다음 시도는 JP5204226B2 Table 1의
  실제 수치 표를 patent_mine.py 등 구조화 파서로 재시도하거나, 텅스텐 CMP 논문 SI의 알루미나
  PSD 데이터를 찾는 방향으로 전환 권고).

## 6. 한계 (정직한 미검증 표기)
- ⚠ **미검증**: AluminaWorld 블로그 D50/D99 스펙(2.4절)은 1차 출처 아님, 참고만.
- ⚠ **미검증**: JP5204226B2 D90/D10≤3 조건은 확인했으나 D99 절대값은 원문 표 파싱 실패로 미확보.
- ⚠ **미검증**: Levitronix/Silco 자료의 D99/D50 비율 수렴(4.29~5.00)은 n=3(같은 발표자료 내
  3개 값)으로 통계적 근거가 약하다. 알루미나 미포함, 일반화 주의.
- **문헌 없음이 아니라 "탐색했으나 1차 출처 미확보"** — 갭 랭커 `--skip` 대상 아님.

## 7. 출처 요약
- US 11,117,239 B2. "Chemical mechanical polishing composition and method." (특허, 무료 공개)
- US 9,566,686 B2. "Composition for tungsten CMP." Cabot Microelectronics Corp. (특허, 무료 공개)
- JP 5,204,226 B2 / WO2009151120A1. "Aluminum oxide particles and polishing composition containing
  the same." (특허, 무료 공개, patents.google.com)
- Silco Electronic Materials (2008-02-11). "Handling and Filtration of CMP Slurries." Levitronix
  CMP Users Conference 발표자료. (산업 컨퍼런스 슬라이드, 2차 자료, onsemi.com 자사 호스팅 확인)
- AluminaWorld Technical Team (2026-08-31). "High-Purity Alumina for Semiconductor CMP Slurry."
  (제조사 블로그, 상업 콘텐츠, 1차 출처 아님 — 참고만)

## 8. 정량 재현 확인 (문헌값과 코드 재현 대조)

Levitronix/Silco(2008) 슬라이드 원문값과 아래 코드 재현을 직접 대조한다: earlier 세대
D50=0.20 µm/D99=1.0 µm → 비율 5.00배(문헌 원문 그대로), new 세대 D50=0.07 µm/D99=0.3 µm →
비율 4.29배(문헌 원문 그대로), next target D50=0.04 µm/D99=0.2 µm → 비율 5.00배(문헌 원문
그대로) — 세 값 모두 계산 재현이 원문 표기와 일치(반올림 오차 내). 구체 대조:
재현 D99 = 1.0 µm / 0.3 µm / 0.2 µm 가 각각 문헌값 1.0 µm / 0.3 µm / 0.2 µm 와 일치.
⚠ 이는 같은 슬라이드의 두 숫자를 나눈 것이므로 일치가 당연하다 — 확인된 것은 전사
정확성이고 모델 정확도는 **미검증**이다(출처: Levitronix/Silco 2008 슬라이드 p.11).

```python verify
# Levitronix/Silco 2008 슬라이드 p.11 — D50/D99 세대별 값 (마이크론)
generations = {
    "earlier": (0.20, 1.0),
    "new": (0.07, 0.3),
    "next_target": (0.04, 0.2),
}

ratios = {k: d99 / d50 for k, (d50, d99) in generations.items()}
for k, r in ratios.items():
    print(f"{k}: D99/D50 = {r:.2f}")

assert 4.9 < ratios["earlier"] < 5.1, f"earlier 비율 이상: {ratios['earlier']}"
assert 4.2 < ratios["new"] < 4.4, f"new 비율 이상: {ratios['new']}"
assert 4.9 < ratios["next_target"] < 5.1, f"next_target 비율 이상: {ratios['next_target']}"

# 이전 노트(세리아 코팅 실리카) 범위와 병합 시 전체 관측 범위
prior_min, prior_max = 1.82, 3.82  # abrasive-d99-spec-cross-pack-comparison.md §2.2
this_min, this_max = min(ratios.values()), max(ratios.values())
combined_min = min(prior_min, this_min)
combined_max = max(prior_max, this_max)

assert combined_min == prior_min, "이전 노트의 최소값이 여전히 전체 최소가 되어야 한다"
assert combined_max == this_max, "이번 노트의 최대값이 전체 최대를 갱신해야 한다"
print(f"D99/D50 비율 통합 관측 범위: {combined_min:.2f}~{combined_max:.2f}배 (알루미나 미포함)")

# damage_exponent 기본값(3.0)이 이 범위 안에 있는지만 확인 (근거로 승격하지 않음 — 다른 변수)
damage_exponent_default = 3.0
assert combined_min < damage_exponent_default < combined_max, \
    "기본값이 관측 범위 밖 — 최소한의 정합성도 없다는 뜻이므로 재검토 필요"
print(f"damage_exponent 기본값({damage_exponent_default})은 통합 관측 범위 안에 있으나, "
      f"D99/D99_ref 지수와 D99/D50 절대비는 다른 물리량이므로 직접 근거로 쓰지 않는다.")
```
