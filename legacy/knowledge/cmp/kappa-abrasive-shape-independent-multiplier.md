---
title: κ 입자 형상(shape) 축 — held-out 밖 독립 배수 탐색 (판정#68 2회차, 판정#75 선례 적용)
status: 완료 — (B) 방향 재확인, 신규 정량 배수 확보했으나 배선 보류(판정#68 2회차)
---

# κ 입자 형상 축 — 독립 정량 근거 탐색

> 위임 작업 | 작성일: 2026-09-19
> 선행: 판정#68 [[kappa-abrasive-shape-axis-ruling]] (방향 확정 E3, 배선 보류 — 자기채점 회피),
> 판정#73 [[c4-cu-h2o2-bta-heldout-rho-diagnosis]] (C4 유일 원인 = 이 축, ρ 0.7175→구형-only 0.8208)
> 선례: 판정#75(옥살산 촉진축) — "자기채점이라 배선 못 한다"는 "다른 문헌을 찾아라"는 뜻,
> held-out 밖 1차 특허(US6309560B1)를 찾아 배선하고 ρ 부호를 뒤집은 전례.

## 0. 결론

판정#68이 "방향만 주고 배수를 안 준다"고 판단한 **ma15217525(Materials 2022, 세리아/유리
CMP)의 Figure 7b를 이번 회차가 픽셀 좌표 보정으로 직접 판독해 정량 배수를 뽑아냈다**(§2).
방향은 재확인(비구형>구형)됐고, **배수도 처음으로 확보**했다 — 그런데 그 배수가 **상수가
아니라 슬러리 농도에 따라 1.09~2.51배로 비단조 변화**한다는 것이 이번 회차의 핵심 신규
발견이다(§2). 이 비상수성과, 대상계 불일치(세리아/유리 vs Cu/H2O2/BTA-실리카), 그리고
**held-out 데이터셋 자신이 이미 형상 항 생성에 명시적으로 반대하는 `excluded_axes` 주석을
갖고 있다**는 사실(§3) 셋을 근거로 **배선하지 않는다** — (B) 판정, 판정#68의 2회차로
카운트한다. 코드·YAML 변경 없음.

## 1. 판정#68이 이미 실패한 경로 (반복 금지 확인용)

- Kim, Eungchul et al. 2021, Powder Technology 381, 451-458,
  DOI: 10.1016/j.powtec.2020.11.058 — OpenAlex/Unpaywall/S2 전부 closed, sci-hub 3미러 캡차.
  **이번 회차는 이 DOI를 재시도하지 않는다**(판정#68 §1이 같은 날 5경로 소진 확인, 중복 방지).

## 2. ma15217525(Materials 2022) 재확인 — 그래프 픽셀 판독으로 정량 배수 확보

판정#68은 이 논문의 로컬 JATS XML(`data/corpus/fulltext/doi_10.3390_ma15217525.xml`)만
보고 "MRR의 정밀 배수는 Figure 7b(그래프)에만 있고 본문에는 하한값(">500")과 한 점(555)만
있다"고 판단했다. **이번 회차가 XML을 재파싱해 그 판단을 재확인했다**(`<table-wrap>`은
XRD 표 1건뿐, `<fig>` 9개 중 MRR을 다루는 것은 Figure 7b 하나, 본문 `<p>` 전수 검색으로도
숫자 두 개(">500", "9 wt.%, 555 nm/min") 외에는 없음 — 판정#68의 판단이 맞다).

**그래서 그래프 자체를 판독했다.** MDPI CDN(`mdpi-res.com/d_attachment/materials/...`)에서
원문 PDF를 직접 확보(HTTP 200, 로컬 캐시: `papers/zheng2022-ma15217525-ceria-abrasive-shape-mrr.pdf`,
gold OA CC-BY이므로 재배포 문제 없음)하고, PyMuPDF로 Figure 7b(MRR vs 농도, F/S/N 세 계열)
영역만 고해상도(10배율) 래스터화한 뒤, **y축 눈금 라벨(700~100, 7개 텍스트 밴드) 픽셀
중심에 대한 선형회귀로 축을 보정**하고(x축은 플롯 테두리 자체가 0/10에 정확히 일치하는
Origin 기본 동작을 이용), **각 계열 색상(RGB 임계값)에 이진 부식(binary erosion)을 걸어
마커(원/삼각형/사각형)만 남기고 연결선을 제거**해 5개 데이터점의 픽셀 중심을 얻었다.

```python verify
import fitz
import numpy as np
from PIL import Image
from scipy import ndimage

doc = fitz.open("papers/zheng2022-ma15217525-ceria-abrasive-shape-mrr.pdf")
page = doc[7]  # 0-indexed, "8 of 11" — Figure 7 캡션이 있는 페이지
mat = fitz.Matrix(10, 10)
clip = fitz.Rect(355, 92, 545, 255)  # panel (b): MRR vs concentration
pix = page.get_pixmap(matrix=mat, clip=clip)
img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
arr = np.array(img).astype(int)
R, G, B = arr[:, :, 0], arr[:, :, 1], arr[:, :, 2]

# y축 보정: 눈금 라벨 텍스트(700..100)의 픽셀 행 중심에 선형회귀
black_mask = (R < 80) & (G < 80) & (B < 80)
band = black_mask[:, 100:205]
rowsum = band.sum(axis=1)
rows = np.where(rowsum > 5)[0]
groups, cur = [], [rows[0]]
for r in rows[1:]:
    if r - cur[-1] <= 8:
        cur.append(r)
    else:
        groups.append(cur)
        cur = [r]
groups.append(cur)
label_groups = [g for g in groups if len(g) > 15]
assert len(label_groups) == 7, len(label_groups)
y_centers = [(g[0] + g[-1]) / 2 for g in label_groups]
fit_y = np.polyfit([700, 600, 500, 400, 300, 200, 100], y_centers, 1)
def val_y(p): return (p - fit_y[1]) / fit_y[0]

# x축 보정: 플롯 테두리(스파인) 좌우 끝 = 농도 0/10 wt%
spine_col = (R < 60) & (G < 60) & (B < 60)
colsum = spine_col.sum(axis=0)
spine_cols = np.where(colsum > 1300)[0]
x0, x10 = spine_cols.min(), spine_cols.max()
def val_x(p): return (p - x0) / (x10 - x0) * 10.0

def find_blobs(mask, iters, min_size):
    m = ndimage.binary_erosion(mask, iterations=iters)
    lbl, n = ndimage.label(m, structure=np.ones((3, 3)))
    out = []
    for i in range(1, n + 1):
        ys, xs = np.where(lbl == i)
        if len(xs) >= min_size:
            out.append((xs.mean(), ys.mean()))
    return out

red_mask = (R > 150) & (G < 100) & (B < 100)    # S-abrasives(방추형)
blue_mask = (B > 150) & (R < 100) & (G < 100)   # N-abrasives(구형에 가까움)

red_blobs = sorted(find_blobs(red_mask, 8, 30), key=lambda b: b[0])
blue_blobs = sorted(find_blobs(blue_mask, 8, 30), key=lambda b: b[0])
assert len(red_blobs) == 6 and len(blue_blobs) == 6  # 데이터 5점 + 범례 마커 1점

def drop_legend(blobs):
    return [b for b in blobs if not (1140 < b[1] < 1340 and 1380 < b[0] < 1440)]
red_pts = drop_legend(red_blobs)
blue_pts = drop_legend(blue_blobs)
assert len(red_pts) == 5 and len(blue_pts) == 5

interior = np.zeros_like(black_mask)
interior[90:1400, 220:1850] = True
legend_excl = np.zeros_like(black_mask)
legend_excl[1100:1345, 1320:1857] = True
f_mask = black_mask & interior & ~legend_excl   # F-abrasives(박편형/각진)
black_pts = sorted(find_blobs(f_mask, 8, 30), key=lambda b: b[0])
assert len(black_pts) == 5

def to_vals(pts): return [(round(val_x(x), 1), round(val_y(y), 1)) for x, y in pts]
F, S, N = to_vals(black_pts), to_vals(red_pts), to_vals(blue_pts)

# 판독 검증: 본문이 인쇄한 유일한 숫자(N-abrasives, 9 wt.%, 555 nm/min)와 대조
n9 = [v for (c, v) in N if abs(c - 9.0) < 0.5][0]
assert abs(n9 - 555.0) / 555.0 < 0.02, n9   # 판독값 553.6 vs 인쇄값 555 → 오차 0.25%

ratios_FN = [round(f[1] / n[1], 3) for f, n in zip(F, N)]
ratios_SN = [round(s[1] / n[1], 3) for s, n in zip(S, N)]
assert ratios_FN == [2.178, 2.504, 1.518, 1.333, 1.088]
assert ratios_SN == [1.239, 1.314, 1.085, 0.939, 0.781]
assert all(r > 1.0 for r in ratios_FN)          # F(비구형)>N(구형) — 5농도 전부, 방향 재확인
assert max(ratios_FN) / min(ratios_FN) > 2.0    # 상수 배수가 아니다(2.3배 폭)
assert ratios_SN[0] > 1.0 and ratios_SN[-1] < 1.0  # S/N은 농도에 따라 방향까지 뒤집힌다

print("F(박편형/각진)/N(구형) 배수:", list(zip([c for c, _ in F], ratios_FN)))
print("S(방추형)/N(구형) 배수:      ", list(zip([c for c, _ in S], ratios_SN)))
```

**결과** (wt% → F/N배수, S/N배수):
1%→2.178·1.239, 3%→2.504·1.315, 5%→1.518·1.086, 7%→1.333·0.939, 9%→1.088·0.781.

**해석**:
1. **방향 재확인**: F(박편형/각진, 가장 비구형)는 5개 농도 전부에서 N(구형에 가까움)보다
   MRR이 높다 — 판정#68의 결론과 같은 방향, 이번엔 그래프 판독으로 정량 재확인.
2. **신규 발견 — 상수 배수가 아니다**(§2 verify 블록 `ratios_FN` 재현, Zheng et al. 2022
   Figure 7b 판독): F/N 배수는 2.18배(1wt%)→2.50배(3wt%)→1.52배(5wt%)→
   1.33배(7wt%)→1.09배(9wt%)로 **비단조(3wt%에서 정점) + 농도 증가에 따라 1로 수렴**한다.
   S(방추형, F보다 덜 각진)/N 배수는 더 극적이다 — 1~3wt%에서는 1.09~1.32배로 S가 높지만
   **7~9wt%에서는 0.78~0.94배로 역전**(S<N)된다. 즉 "비구형이 항상 더 빠르다"는 이 논문
   자신의 결론(본문 서술)은 **F(가장 각진 계열)에서만 전 구간 성립**하고, 형상이 F보다
   약한 S에서는 고농도에서 반대 방향까지 나온다 — 응집(agglomeration)에 의한 유효접촉면적
   감소(본문이 직접 지목한 메커니즘, §본문 인용 "particle accumulation... reducing the
   effective contact area")가 각진 정도가 약한 입자일수록 먼저 이긴다는 뜻으로 읽힌다.
3. **정밀도 검증**(Zheng et al. 2022 본문, §2 verify 블록 `n9` 재현): 판독 파이프라인이
   논문 본문이 인쇄한 유일한 숫자(N, 9wt%, 555 nm/min)를 553.6로 재현했다(오차 0.25%) —
   축 보정·마커 분리 방법의 정확도가 실제 인쇄값으로 교차검증됐다.

## 3. 배선하지 않는 이유 — (B) 판정

정량 배수를 확보했음에도(§2), 다음 세 가지가 겹쳐 **여전히 배선하지 않는다**:

1. **대상계 불일치**: ma15217525은 세리아 연마입자 + TFT-LCD 유리 기판(기계적 마모
   지배)이고, `cu_h2o2_bta`는 콜로이달 실리카/알루미나 + Cu 금속(화학-기계 복합)이다.
   판정#62 선례(입경 항의 타계 전이)와 같은 구조의 전이지만 **그 판정도 "미검증"이라고
   명시한 한계를 그대로 물려받는다** — 형상이 만드는 기계적 효과(압입 각·유효접촉면적)가
   화학종이 달라도 같은 크기로 전이된다는 근거는 없다.
2. **상수가 아니라 대상계의 운전점을 특정할 수 없다**: TW202115224A의 실제 슬러리
   농도는 0.0833 wt%(고정, 모든 18조건 동일)로, ma15217525이 스윕한 범위(1~9 wt%)보다
   훨씬 낮다. §2의 F/N 배수는 1→3wt%에서 오히려 **증가**(2.18→2.50)했다가 그 이후
   감소하는 비단조 곡선이라, 0.0833 wt%로 외삽할 때 "낮은 농도 극한이니 배수가 더
   크다"고 단정할 수도, "가장 가까운 1wt% 값(2.18배)을 쓴다"고 정당화할 수도 없다 —
   두 논리 모두 이 데이터 자체가 반증한다(1→3wt% 구간에서 이미 반대로 움직였다). 상수
   하나를 고르는 것은 이 절 자체가 보여준 비선형성을 무시하고 지어내는 것이다
   (과제 지시 §절대금지).
3. **held-out 데이터셋 자신이 이미 이 항의 생성에 반대하는 주석을 갖고 있다**:
   `validation/datasets/tw202115224a_cu_abrasive_size_pressure.yaml`의
   `excluded_axes.abrasive_shape`가 "50 nm 쌍(배합5/6)에서만 제조사(Nalco/Fuso)와
   **동시에** 형상이 바뀌므로 이 데이터 안에서는 두 축이 분리 불가능하다... 분리되기
   전에 항을 만들면 두 효과가 한 계수에 뭉쳐 그 데이터셋의 지문이 된다"고 명시한다.
   이번 배수는 held-out 밖(ma15217525)에서 왔으니 판정#68이 우려한 "자기채점"은 아니지만,
   **이 데이터셋에 형상 라벨을 구조화된 입력(override)으로 추가해 항을 활성화시키는 행위
   자체**는 이 excluded_axes 주석이 미리 금지해 둔 것과 같은 종류의 조작이다 — 다른
   문헌에서 값을 가져왔다는 사실이 이 confound를 없애주지는 않는다.

**세 가지 중 어느 하나만으로는 판정#68을 뒤집기에 부족하지만, 셋이 겹치면 "배선 가능한
독립 배수를 확보했다"고 보기 어렵다.** 방향은 재확인됐고(§2-1), 배수는 확보했으나
비상수·타계·데이터셋 자체 금지 셋이 겹쳐 배선 근거로 쓰기엔 약하다 — **(B) 판정,
판정#68의 2회차로 카운트한다.** 3회차 미도달이므로 종결하지 않는다.

## 4. 다음 회차 구체 경로

1. **ma15217525의 저농도 극한 재검증**: 이 논문의 후속 연구나 같은 저자군의 다른 논문이
   1wt% 미만(TW202115224A의 실제 운전점 0.0833wt%에 더 가까운) 구간을 스윕했다면 비단조성
   해소 가능. 검색은 이번 회차에 하지 않았다(과제 지시 §진행규칙 — 이미 한 축을 깊게
   판 상태에서 새 문헌 탐색을 추가하면 60턴 규칙을 넘길 위험).
2. **excluded_axes 해소 경로**: TW202115224A의 50nm 쌍(Nalco 구형/Fuso 누에고치형) 제조사
   물성표(IEP·D99/D50·비표면적)를 확보하면(판정#68 §5-1, 같은 excluded_axes 주석이 지정한
   해소 경로) 형상과 제조사를 분리할 수 있고, 그러면 이 데이터셋 자체의 confound가
   풀려 §3-③의 반대 근거가 사라진다.
3. **Kim et al. 2021(Powder Technology) 원문**: 판정#68·이 노트 모두 미확보. 저자
   소속(SKKU) 외 공동연구기관(SK Group) 산학 리포지토리 등 새 경로가 열리면 재시도.

## 5. 게이트 실행 기록

- `tools/verify_claims.py knowledge/cmp/kappa-abrasive-shape-independent-multiplier.md` → ✓
  (출처 2건 실존·코드 1블록 통과)
- `tools/check_knowledge.py knowledge/cmp/kappa-abrasive-shape-independent-multiplier.md` → ✓
- `pytest -q` → **1294 passed, 1 skipped**(기준과 동일, 회귀 0 — 코드 미변경)
- `tools/completion.py check` → **67/70 불변**(C4 `cu_h2o2_bta` 유의 평균 ρ 0.7175 < 0.85,
  그대로 실패 — 숫자로 숨기지 않는다). ⚠ `n_total`이 5→6으로 표시될 수 있는데, 이는 이
  판정과 무관하게 동시 작업 중인 다른 워커가 `cu_h2o2_bta`에 새 held-out 데이터셋을 추가한
  결과다(이 노트는 그 데이터셋을 만들지도, 참조하지도 않았다).
- `tools/qa_loop.py run --strict` → **PASS**, 유의 평균 ρ **0.9566**(기준과 동일, 불변 —
  코드 미변경이므로 예상된 결과)
