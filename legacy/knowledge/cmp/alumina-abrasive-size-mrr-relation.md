<!-- V2-SECTION: R2-slurry | 정확도루프 2026-09-18 | 정본: ARCHITECTURE-V2.md §3 -->
# 알루미나 연마입자 입경-MRR 관계 — sic_alumina_kmno4 입경축 정합 (Su et al. 2011, 6H-SiC)

> 판정#60 §5 후속. `sic_alumina_kmno4` 팩의 `abrasive_size_nm`(120)·`abrasive_ref_size_nm`·
> `abrasive_size_peak_nm`(163)·`abrasive_size_exp_below_peak`(+4/3)·`abrasive_size_exp_above_peak`
> (-1/3) 5키가 전부 부모 `sic_ceria_h2o2`(세리아, Oh et al. 2010 DOI 10.1016/j.mee.2010.07.040)
> 소유였다 — 알루미나 팩인데 정점·지수가 세리아 형상. 근거문헌 Gong 2024
> (doi:10.3390/ma17030679)는 500 nm **고정**이라 입경 스윕을 못 준다.
> [[ceria-abrasive-size-mrr-peak-shift-vs-silica]] [[sic-alumina-pack-abrasive-identity-inheritance-defect]]
> [[identity-inheritance-audit-sweep]]
>
> **2026-09-18 재작업**: 직전 회차가 (a) YAML 5키를 own 선언했다고 주장했으나 실제로는
> 커밋되지 않아 여전히 세리아 상속 상태였고 (b) Fig.2 판독값 중 2점(48, 62)을 "육안 판독"
> 했다고 적었으나 그 값이 y축 표시 눈금(50/55/60/65) 최소치 아래라 물리적으로 의심스러웠다.
> 이번 회차는 **PyMuPDF 벡터 드로잉 좌표를 기계로 판독**해 재검증했다(§2).

## 1. 목표
알루미나 연마입자 계의 입경 단독 스윕(3점 이상) 1차 문헌을 확보해 정점 위치 + 정점 양쪽 지수를
**알루미나 자신의 실측**으로 재선언한다(세리아 곡선을 그대로 두는 것이 판정#60이 금지한 함정).
우선순위 ①알루미나+SiC(4H/6H) ②알루미나+경질세라믹/사파이어 ③알루미나+산화막/금속.

## 2. 확보한 1차 문헌 — 우선순위 ①(알루미나+SiC) 정확 일치

**SU Jianxiu, DU Jiaxia, LIU Haina, LIU Xinglong (2011).** "Research on Material Removal Rate
of CMP 6H-SiC Crystal Substrate (0001) Si Surface Based on Abrasive Alumina (Al2O3)."
*Procedia Engineering* **24**, 441–446. DOI: `10.1016/j.proeng.2011.11.2673`.
(Elsevier Procedia, 원문 자체가 gold OA·CC-BY-NC-ND. 로컬 `papers/proeng-2011-11-2673-alumina-6h-sic.pdf`.)

- 웨이퍼: **6H-SiC (0001) Si면** — 이 팩(4H-SiC)과 폴리타입만 다르고 막질·연마입자(알루미나)가
  정확히 일치. 화학은 알칼리(pH 9, alkali 조정 + oxidant) — 이 팩(산성 KMnO4)과 오염 경로는
  다르나, 입경 항은 **입자 자체의 기하(압입 반경)**이지 산화제 화학이 아니다(같은 가정을
  `sic_ceria_h2o2` 팩의 Chen 2017 입경값 이식 때도 이미 썼다 — 상단 note 참조).
- §3.2 "The influence of abrasive size on the MRR": 4점 1축 스윕, 연마입자 W1/W1.5/W2.5/W3.5
  (원문 그래프 x축이 "Abrasive Size(um)"으로 W-호칭수를 그대로 μm 값 1.0/1.5/2.5/3.5로 표기 —
  중국 GB 미분(微粉) 연마재 호칭이지만 이 논문은 숫자를 μm 절대값으로 직접 쓴다).
  고정 조건: 연마입자 10 g/500 mL, 분산제 2 mL, 산화제 5 mL, pH 9(알칼리 조정),
  P=2 psi, n_w=65 rpm, n_p=60 rpm.

### 2.1 Fig.2 마커 좌표 기계판독 (육안 아님)

Fig.2는 PDF 페이지 3(0-idx 2)의 벡터 드로잉(`page.get_drawings()`)이다(래스터 이미지 아님 —
`page.get_images()`가 0건). 판독 절차:

1. `page.get_text("words")`로 x축 눈금 라벨(1.0~4.0, 7개)·y축 눈금 라벨(50/55/60/65, 4개)의
   PDF 좌표를 뽑는다(Fig.1과 Fig.2가 같은 페이지에 나란히 있어 x좌표 구간(270~420)·y좌표
   구간으로 Fig.2 쪽만 필터링).
2. 각 축에 대해 (픽셀좌표, 데이터값) 쌍을 최소자승 선형회귀해 `픽셀→데이터` 보정식을 얻는다.
3. `page.get_drawings()`에서 `type=='f'`(채워진 도형)이고 Fig.2 플롯박스 안(x: 275.5~404.5,
   y: 123.9~220.1)에 있는 3pt 미만 크기의 작은 사각형만 필터링 — 정확히 **4개**가 검출된다
   (마커가 아닌 다른 드로잉과 겹치지 않음).
4. 4개 마커 중심좌표에 보정식을 적용해 (입경 μm, MRR nm/h)로 변환한다.

결과 (x=1.0/1.5/2.5/3.5 μm 순, 소수 첫째자리 반올림):

| 입경 (μm = nm×1000) | 기계판독 MRR (nm/h) | 채택값 | 근거 |
|---|---|---|---|
| 1.0 (W1) | 47.90 | **47.9** | 원문 텍스트 미언급 구간 — 기계판독값 채택 |
| 1.5 (W1.5) | 50.91 | **51.0** | 원문 텍스트 명시값(Su et al. 2011 §3.2) 채택, 기계판독과 오차 0.09 |
| 2.5 (W2.5) | 62.92 | **63.3** | 원문 텍스트 명시값(Su et al. 2011 §3.2, 정점) 채택, 기계판독과 오차 0.38 |
| 3.5 (W3.5) | 61.91 | **61.9** | 원문 텍스트 미언급 구간 — 기계판독값 채택 |

**보정 검증**: 원문 텍스트가 직접 인쇄한 두 값(W1.5=51nm/h, W2.5=63.3nm/h — "The MRR increases
from the 51nm/h to 63.3nm/h when the abrasive size increases from the W1.5 to W2.5")과 기계판독
보정값의 오차가 각각 0.09·0.38 nm/h로 **±1.5 nm/h 이내** — 보정식이 타당하다(§6 verify 블록에서
PDF를 직접 열어 재현).

**"48/62가 y축 최소눈금(50) 아래라 축 밖" 문제의 해소**: Fig.2 플롯박스의 실제 y축 선(좌측 세로
드로잉)은 y=123.98pt(65 눈금 근방)부터 y=220.10pt까지 뻗어 있는데, "50" 눈금 라벨은 y=199.33pt다
— 즉 박스 바닥이 50 눈금보다 **더 아래**(≈46 nm/h 상당)까지 있다. W1(47.9)은 이 여백 안에 있어
플롯박스를 벗어나지 않는다. "축 밖이라 물리적으로 불가능"이라는 직전 회차의 우려는 틀렸다 —
다만 직전 회차의 48/62라는 **숫자 자체**는 육안 어림값이었고 기계판독값(47.9/61.9)과 우연히
비슷했을 뿐, 재현 가능한 근거가 없었다는 점에서 결함이었다(§5).

  원문 해석(저자 자신의 설명, §3.2 그대로): 입경이 커질수록 표면과의 기계적 상호작용(압입)이
  커져 MRR이 증가하지만, 슬러리 내 연마입자 **질량이 고정**돼 있어 입경이 커질수록 입자 **개수**가
  줄어 W3.5에서는 더 늘지 않는다 — 이 팩이 이미 갖고 있는 압입 지배/표면적(개수) 지배 두 메커니즘
  경쟁 구조(Bellahsene 2025 폐형식)와 정성적으로 **동일한 설명**이다.

## 3. 정점·지수 도출

정점: **2.5 μm = 2500 nm**에서 관측 최대(63.3 nm/h), 3.5 μm에서 소폭(-2.2%) 하락 — 세리아
정점(163 nm)보다 **약 15배** 크다. 이는 이상하지 않다: 이 논문의 알루미나는 CMP용 콜로이달
나노 슬러리가 아니라 **미분(micropowder) 등급 백색강옥(white corundum) 연마재**(원문 결론부
"the white corundum abrasive can be used in the CMP of SiC crystal substrate")이고, 이 팩의
기준 입경(Gong 2024 Table 1, 500 nm)도 이미 콜로이달 알루미나치고는 큰 편이라 같은 굵은 입자 계열의
연장선에 있다고 본다(500 nm은 정점 2500 nm보다 작아 **압입 지배 가지**에 위치).

로그-로그 회귀(below-peak, 1.0/1.5/2.5 μm 3점: 47.9/51.0/63.3 nm/h, 최소자승):
```
slope = 0.3092888377
```
정점-3.5 μm 2점 기울기(above-peak, 63.3→61.9 nm/h, 데이터가 2점뿐이라 회귀 아님 — 직선 기울기 그대로):
```
slope = -0.0664695242
```

## 4. 5키 값 (own 선언)

| 키 | 구값(세리아 상속) | 신값 | 근거 |
|---|---|---|---|
| `abrasive_size_nm` | 120.0 | **500.0** | Gong 2024 Table 1(이미 `abrasive:` 키가 인용 중이던 문헌, 알루미나 500 nm 고정) |
| `abrasive_ref_size_nm` | 120.0 | **500.0** | 관례상 `abrasive_size_nm`과 항상 일치(κ 항 자기정규화 기준점 — `sim/factors.py` L680-722 참조, `d==d_ref`면 항=1.0으로 Kp 앵커에 영향 없음) |
| `abrasive_size_peak_nm` | 163.0 | **2500.0** | Su et al. 2011 §3.2 Fig.2, W2.5=63.3 nm/h 최대점(기계판독, §2.1) |
| `abrasive_size_exp_below_peak` | +1.3333 | **+0.3092888377** | Su et al. 2011 §3.2, 1.0/1.5/2.5 μm 3점(기계판독+원문 인쇄값 혼합, §2.1) 로그-로그 회귀 |
| `abrasive_size_exp_above_peak` | -0.3333 | **-0.0664695242** | Su et al. 2011 §3.2, 2.5→3.5 μm 2점(기계판독+원문 인쇄값) 기울기(n=2, 약한 근거) |

기준조건(500 nm)이 정점(2500 nm) 아래이므로 below-peak 지수가 발동 — 즉 **이 팩의 기준조건에서
입경을 늘리면 MRR이 완만하게 증가**하는 쪽으로 바뀐다(세리아 상속 시절에는 기준조건이 정점 위
감소 가지에 있었다 — 판정#60이 지적한 "반대 가지" 문제가 이번 교체로 해소된다는 것도 §6 verify로
확인).

## 5. 한계 (정직 기록)

- ⚠ **화학 불일치**: Su 2011은 알칼리(pH 9, 미상 산화제) 계이고 이 팩은 산성 KMnO4다. 입경 항이
  화학과 독립이라는 가정은 이 세션이 새로 만든 것이 아니라 `sic_ceria_h2o2`가 Chen 2017(KMnO4)
  입경값을 H2O2 팩에 이식할 때 이미 쓴 선례를 따른 것 — 그러나 **미검증 가정**인 것은 동일하다.
- ⚠ **폴리타입 불일치**: 6H-SiC(Su 2011) vs 4H-SiC(이 팩). 팩 설명 자체가 "4H/6H-SiC CMP"로
  둘을 같이 다뤄 온 전례가 있다.
- ⚠ **above-peak 지수는 n=2**(2.5, 3.5 μm 두 점뿐)라 회귀가 아니라 직선 기울기다. 하락폭 자체가
  -2.2%로 작아 측정 잡음과 구분하기 어렵다 — 부호(음수)만 신뢰하고 크기는 약한 근거로 취급.
- ⚠ **below-peak 지수도 n=3**이고 구간별 국소 기울기가 0.09(1.0→1.5)~0.48(1.5→2.5)로 편차가
  크다(그래프 판독 오차 + 실제 비선형성 혼재) — 전역 회귀값(0.309)을 대표값으로 쓴다.
- ✅ **그래프 마커 판독 (갱신)**: 직전 회차는 "Fig.2를 6배 확대 렌더링해 육안 판독"이라 적었으나
  그 결과값(48, 62)이 재현 불가능한 어림값이었다. 이번 회차는 PyMuPDF `get_drawings()`로 마커의
  정확한 벡터 좌표를, `get_text("words")`로 축 눈금 라벨 좌표를 뽑아 **선형보정식으로 기계
  변환**했다(§2.1). 보정식은 원문(Su et al. 2011 §3.2)이 텍스트로 직접 인쇄한 두 값(51,
  63.3)과 대조해 ±0.4 nm/h 이내로 검증됐고, §6 verify 블록이 PDF를 직접 열어 이 판독을
  재현한다 — 더 이상 육안 판독이 아니다.
- ⚠ **입경 스케일 외삽**: 이 팩의 기준 입경(Gong et al. 2024 Table 1, 500 nm)은 Su et al. 2011
  §3.2 Fig.2의 스윕 구간(1.0~3.5 μm = 1000~3500 nm)보다 작다(500 nm < 1000 nm, 구간 하한의
  절반) — 정점 위치·지수를 500 nm까지 **외삽**한 것이며, 외삽 구간에서 곡선 형상(below-peak
  지수 0.309)이 그대로 유지된다는 실측 근거는 없다.
- 우선순위 ②(사파이어) 문헌 후보 `doi:10.1007/s40684-015-0020-0`(Springer, 알루미나+사파이어
  고압 CMP)를 로컬 코퍼스에서 찾았으나 전문 미확보(페이월, 이번 회차는 ①이 확보되어 추가 확보를
  시도하지 않았다) — 2회차 필요 시 교차검증 후보로 남긴다.

## 6. 재현 (verify)

```python verify
import math
import fitz
import yaml
from pathlib import Path

# (1) Fig.2 마커 좌표를 PDF에서 직접 기계판독 (육안 아님, §2.1 그대로 재현)
doc = fitz.open("papers/proeng-2011-11-2673-alumina-6h-sic.pdf")
page = doc[2]  # 0-idx 페이지 3, Fig.2 소재
words = page.get_text("words")

xticks = {"1.0": 1.0, "1.5": 1.5, "2.0": 2.0, "2.5": 2.5, "3.0": 3.0, "3.5": 3.5, "4.0": 4.0}
xpts, ypts = [], []
for w in words:
    x0, y0, x1, y1, text = w[0], w[1], w[2], w[3], w[4]
    t = text.strip()
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    if t in xticks and 270 < cx < 420 and 215 < cy < 235:
        xpts.append((cx, xticks[t]))
    if t in ("50", "55", "60", "65") and 260 < cx < 280 and 100 < cy < 210:
        ypts.append((cy, float(t)))
assert len(xpts) == 7 and len(ypts) == 4, f"Fig.2 축 눈금 라벨 개수 불일치: x={len(xpts)} y={len(ypts)}"

def linreg(pts):
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    mx, my = sum(xs) / len(xs), sum(ys) / len(ys)
    sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    sxx = sum((x - mx) ** 2 for x in xs)
    slope = sxy / sxx
    return slope, my - slope * mx

xs_slope, xs_int = linreg(xpts)
ys_slope, ys_int = linreg(ypts)

drawings = page.get_drawings()
markers = []
for d in drawings:
    if d.get("type") != "f":
        continue
    r = d["rect"]
    if 275.5 < r.x0 < 404.5 and 123.9 < r.y0 < 220.1 and (r.x1 - r.x0) < 3 and (r.y1 - r.y0) < 3:
        markers.append(((r.x0 + r.x1) / 2, (r.y0 + r.y1) / 2))
assert len(markers) == 4, f"Fig.2 필 마커 4개를 못 찾았다: {len(markers)}개 검출"

pts = sorted((xs_slope * px + xs_int, ys_slope * py + ys_int) for px, py in markers)
d_um_readout = [p[0] for p in pts]
mrr_readout = [p[1] for p in pts]

for expected_d in (1.0, 1.5, 2.5, 3.5):
    got = min(d_um_readout, key=lambda x: abs(x - expected_d))
    assert abs(got - expected_d) < 0.02, f"x축 판독 {got:.4f}가 {expected_d}에서 벗어났다"

d15_mrr = mrr_readout[d_um_readout.index(min(d_um_readout, key=lambda x: abs(x - 1.5)))]
d25_mrr = mrr_readout[d_um_readout.index(min(d_um_readout, key=lambda x: abs(x - 2.5)))]
assert abs(d15_mrr - 51.0) < 1.5, f"W1.5 보정값 {d15_mrr:.2f}가 원문 인쇄값 51과 ±1.5 밖"
assert abs(d25_mrr - 63.3) < 1.5, f"W2.5 보정값 {d25_mrr:.2f}가 원문 인쇄값 63.3과 ±1.5 밖"

# (2) 채택값(원문 인쇄값 우선 + 기계판독 나머지 2점) 재현
d_um = [1.0, 1.5, 2.5, 3.5]
mrr = [47.9, 51.0, 63.3, 61.9]

peak_idx = mrr.index(max(mrr))
assert d_um[peak_idx] == 2.5, "정점이 2.5um(W2.5)이 아니다"
assert mrr[peak_idx] == 63.3, "정점 MRR이 원문 텍스트값(63.3 nm/h)과 다르다"
assert mrr[1] == 51.0 and mrr[2] == 63.3
assert mrr[2] > mrr[1], "W1.5->W2.5 증가 방향이 원문과 다르다"
assert mrr[3] < mrr[2], "W2.5->W3.5 하락(정체) 방향이 원문 정성 서술과 다르다"

# (3) below-peak 로그-로그 회귀 (1.0/1.5/2.5 um, 최소자승)
xs = [math.log(v) for v in d_um[:3]]
ys = [math.log(v) for v in mrr[:3]]
mx, my = sum(xs) / len(xs), sum(ys) / len(ys)
sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
sxx = sum((x - mx) ** 2 for x in xs)
slope_below = sxy / sxx
assert abs(slope_below - 0.3092888377) < 1e-6, f"below-peak 회귀 재현 실패: {slope_below}"

# (4) above-peak 2점 기울기 (2.5 -> 3.5 um)
slope_above = math.log(mrr[3] / mrr[2]) / math.log(d_um[3] / d_um[2])
assert abs(slope_above - (-0.0664695242)) < 1e-6, f"above-peak 기울기 재현 실패: {slope_above}"
assert slope_below > 0 > slope_above, "두 지수 부호가 정점형 곡선의 필요조건을 만족하지 않는다"

# (5) 팩 반영값이 이 노트의 계산값과 정확히 일치하는지, 그리고 own(자기선언)인지 확인
from sim.params import load_pack

pk = load_pack("sic_alumina_kmno4")
for key, expected in (
    ("abrasive_size_nm", 500.0),
    ("abrasive_ref_size_nm", 500.0),
    ("abrasive_size_peak_nm", 2500.0),
    ("abrasive_size_exp_below_peak", slope_below),
    ("abrasive_size_exp_above_peak", slope_above),
):
    assert pk.has_own(key), f"{key} 가 own 선언이 아니다 — 세리아 상속이 남아있다"
    got = float(pk.get(key))
    assert abs(got - expected) < 1e-6, f"{key}: 팩값 {got} != 노트 계산값 {expected}"

# (6) 기준조건(500nm)이 정점(2500nm) 아래 -> below-peak 가지가 기준조건에서 발동
assert 500.0 < 2500.0, "기준 입경이 정점 아래(압입 지배 가지)에 있어야 한다"

# (7) 세리아 상속 시절과 방향이 바뀌었음을 확인 -- 판정#60이 지적한 "반대 가지" 해소.
# 근거문헌(Gong 2024)의 실제 알루미나 입경은 500nm다 -- 이 값이 세리아 상속 곡선의
# 정점(163nm)을 이미 지나 감소가지에 있었는데(identity-inheritance-audit-sweep.md
# L82-98), 알루미나 자신의 실측 정점(2500nm)에서는 500nm이 아직 증가가지에 있다.
def piecewise(d, peak, e_below, e_above):
    if d <= peak:
        return d ** e_below
    return (peak ** e_below) * (d / peak) ** e_above

old_peak_val = piecewise(163.0, 163.0, 4.0 / 3.0, -1.0 / 3.0)
old_at_500 = piecewise(500.0, 163.0, 4.0 / 3.0, -1.0 / 3.0)
assert old_at_500 < old_peak_val, (
    "구값(세리아)에서는 실제 재료 입경(Gong 2024, 500nm)이 정점(163nm)을 이미 지나 "
    "감소가지에 있었어야 한다(재확인)")

new_peak_val = piecewise(2500.0, 2500.0, slope_below, slope_above)
new_at_500 = piecewise(500.0, 2500.0, slope_below, slope_above)
assert new_at_500 < new_peak_val, (
    "신값(알루미나)에서는 실제 재료 입경(500nm)이 정점(2500nm) 전, 증가가지에 있어야 한다")
new_1000 = piecewise(1000.0, 2500.0, slope_below, slope_above)
assert new_1000 > new_at_500, "신값(알루미나)에서는 500->1000nm 확대가 증가가지여야 한다"

print("PASS: Fig.2 마커 기계판독(PDF 직접 재현) + 4점 재현 + 5키 own 선언 + 기준조건 가지 방향 확인")
print(f"기계판독 4점: {[(round(d,3), round(m,2)) for d, m in pts]}")
print(f"below-peak slope = {slope_below:.7f}, above-peak slope = {slope_above:.7f}")
```

## 7. 출처 요약
- SU Jianxiu, DU Jiaxia, LIU Haina, LIU Xinglong (2011). "Research on Material Removal Rate of CMP
  6H-SiC Crystal Substrate (0001) Si Surface Based on Abrasive Alumina (Al2O3)." *Procedia
  Engineering* 24, 441–446. DOI: 10.1016/j.proeng.2011.11.2673. (Gold OA, Elsevier Procedia,
  CC-BY-NC-ND. 로컬 PDF `papers/proeng-2011-11-2673-alumina-6h-sic.pdf`, fitz 전문 텍스트 추출 +
  Fig.2 벡터 드로잉 좌표 기계판독, §2.1·§6.)
- Gong et al. 2024, DOI 10.3390/ma17030679 Table 1 (알루미나 500 nm — 이미 팩의 `abrasive` 키가
  인용 중이던 문헌, 이번 회차에 `abrasive_size_nm`으로도 승격).
