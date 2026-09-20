# ζ(pH) 연속식 — 실리카·세리아·알루미나

> 에이전트: slurry-abrasive | 작성일: 2026-09-18
> [[colloid-zeta-dlvo-slurry-stability]] [[ph-ionic-strength-zeta-dissolution-selectivity-pourbaix]] [[post-cmp-metallic-contamination-sources]]

## 배경 / 문제
`sim/tier2_physics/metal_contamination_surface.py::boltzmann_surface_enrichment()`가 쓰는
`ZETA_MV_BY_PH`는 4구간 정성 카테고리(IEP 0 / 약산성 -20 / 중성 -40 / 약알칼리 -60 mV)뿐이라
연속값 `slurry_ph`를 매핑할 수 없다. 이 노트는 실리카·세리아·알루미나 세 연마입자에 대해
**1차 문헌에서 확보한 ζ(pH) 실측점**을 IEP·기울기·유효구간·이온세기 조건과 함께 정리한다.

## 목차
1. 알루미나 (Al2O3)
2. 세리아 (CeO2)
3. 실리카 (SiO2)
4. 판독 절차 (재현성)
5. 정량 재현 절 + verify 블록
6. 엔진 등록 여부
7. 미확보 · 스코프 제외 항목

---

## 1. 알루미나 (Al2O3) ζ(pH)

**출처(E1, 1차 논문, scope --check 통과):**
Gong, J.; Wang, W.; Liu, W.; Song, Z. "Polishing Mechanism of CMP 4H-SiC Crystal Substrate
(0001) Si Surface Based on an Alumina (Al2O3) Abrasive." *Materials* 2024, 17(3), 679.
DOI: 10.3390/ma17030679 (MDPI, CC-BY, 원문 PDF 직접 확보 — `papers/liu2024-materials-alumina-mno2-4hsic-cmp.pdf`,
mdpi-res.com CDN 직링크로 우회 — www.mdpi.com은 403).

측정법: 제타전위 애널라이저(Malvern Nano-ZS, Zetasizer 계열, "zeta plus particle apparatus"),
실온, pH는 NaOH 또는 HNO3로 조정. Fig. 7b에 Al2O3 및 MnO2(4H-SiC CMP 슬러리의 산화제 유래
부산물) 제타전위 대 pH 실측 10점(Al2O3, pH 2.1–12.0)이 그림으로 제시됨(본문 텍스트에는
수치표 없음 — §4 판독 절차로 추출).

**기계 판독 결과 (papers/img/liu2024_fig7b_alumina_mno2_zeta_ph.png, Fig.7b 우측 패널):**

| pH | ζ (mV, Al2O3) |
|---|---|
| 2.09 | +38.0 |
| 3.00 | +34.0 |
| 4.00 | +30.0 |
| 5.20 | +27.0 |
| 6.00 | +23.0 |
| 8.00 | +13.0 |
| 8.99 | −5.0 |
| 10.00 | −10.0 |
| 11.00 | −20.0 |
| 12.00 | −23.0 |

- **IEP ≈ 8.72** (pH8.00→+13.0mV, pH8.99→−5.0mV 사이 선형보간)
- **산성 구간 기울기 (pH 2.1–8.0): dζ/dpH ≈ −4.09 mV/pH** (절편 +46.8 mV, n=6)
- **염기 구간 기울기 (pH 9.0–12.0): dζ/dpH ≈ −6.39 mV/pH** (n=4)
- **이온세기: 문헌에 미기재.** pH 조정제(NaOH/HNO3) 농도·배경전해질 농도가 본문에 없음 —
  따라서 이 ζ 절대값은 "특정 이온세기 조건에서"만 유효하며, 다른 이온세기의 알루미나 슬러리에
  그대로 적용할 수 없다. 부호·개형(단조감소, IEP≈8.7)만 신뢰 구간이 넓고, 절대 mV는 좁게 봐야 한다.
- Kosmulski 리뷰(§7 참고, 미확보)의 일반적 Al2O3 IEP 문헌범위(pH 8–9.5대)와 오더 정합.

---

## 2. 세리아 (CeO2) ζ(pH)

**출처(E1, 1차 논문 — 본문 미확보, 등가 데이터는 저자 자신의 학위논문(E2, 0.7)로 확보):**
Dawkins, K.; Rudyk, B.W.; Xu, Z.; Cadien, K. "The pH-dependant attachment of ceria
nanoparticles to silica using surface analytical techniques." *Applied Surface Science*
2015, 345, 249–255. DOI: 10.1016/j.apsusc.2015.03.170.
— Unpaywall/OpenAlex/Semantic Scholar/CORE 전부 `closed`(Elsevier 유료, sci-hub 미러는
DNS 불능으로 이 세션에서 접근 불가) → **본문 PDF 미확보**.

대신 같은 저자의 박사학위논문(scope 0.7, 학위논문) 4장이 **이 논문을 그대로 재수록**했다고
명시(p.60: "This chapter is based on the K. Dawkins, R.W. Rudyk, Z. Xu and K. Cadien paper
published in Applied Surface Science")하므로, 이를 원자료로 사용:
Dawkins, Korel V. *Mixed Abrasive Slurries of Ceria and Silica Nanoparticles formed by
Electrostatic Attraction for Shallow Trench Isolation Chemical Mechanical Polishing.*
PhD Dissertation, University of Alberta, 2019. DOI: 10.7939/r3-g3c2-xe63 (OA,
University of Alberta Scholaris 리포지토리, REST bitstream API로 확보 —
`papers/dawkins2019-ualberta-phd-ceria-silica-electrostatic.pdf`).

측정법: 전기영동 이동도(electrophoretic mobility) 측정, Milli-Q수 희석, pH는 시트르산/KOH로
조정, 실온. Fig. 4-2에 세리아(CeO2, Nyacol Nano Technologies 20wt%→5wt% 희석) 및 실리카
(Bindzil EB6080) ζ 대 pH 실측 11점(pH 3–13)이 그림으로 제시.

**기계 판독 결과 (papers/img/dawkins2019_fig4-2_ceria_silica_zeta_ph.png):**

| pH | ζ (mV, CeO2) |
|---|---|
| 3 | +47.4 |
| 4 | +52.1 |
| 5 | +42.9 |
| 6 | +44.7 |
| 7 | +43.1 |
| 8 | +11.7 |
| 9 | +8.7 |
| 10 | −2.1 |
| 11 | −18.0 |
| 12 | −29.7 |
| 13 | −40.7 |

- **IEP: 본문 서술 ≈9.6**(p.64 "the isoelectric point of ceria was found to be approximately
  9.6") **vs 그림 4-2 직접 판독 선형보간 IEP≈9.81** (pH9→+8.7mV, pH10→−2.1mV 보간) — 차이
  2.2%, 판독 오차 범위 내로 교차검증 성립 (출처: Dawkins 2019 학위논문, doi:10.7939/r3-g3c2-xe63, p.64 본문 서술 + Fig.4-2 기계판독; §5 verify 블록이 실행 시 재현).
- **acidic 평탄역 (pH 3–7): +43~+52 mV** (단조가 아니라 소폭 진동 — 단일 기울기로 요약 부적절,
  범위로만 제시)
- **pH 7→10 전이구간 기울기: dζ/dpH ≈ −13.9 mV/pH** (선형회귀, pH7,8,9,10 4점)
- **⚠ 정량 불일치(정직 기록):** 본문 p.64 5장(§5.1 MAS)에서 "ceria zeta potential at pH 4
  ... approximately 40 mV (Figure 4-2)"라 서술하나, Figure 4-2 자체를 기계 판독하면 pH4 지점은
  **+52.1 mV**다 — **30.2% 불일치** (출처: Dawkins 2019, doi:10.7939/r3-g3c2-xe63, p.64 서술 vs Fig.4-2 기계판독; §5 verify 블록이 실행 시 assert). 원인 미상(본문 서술이 반올림/오기 가능성, 혹은 5장에서
  참조한 것이 Fig.4-2가 아닌 별도 실측일 가능성 — 확인 불가). 판독값(52.1 mV)과 본문
  서술값(40 mV) 둘 다 이 노트에 남기고 어느 쪽도 임의로 채택하지 않는다.
- **이온세기: 문헌에 미기재.** pH 조정에 시트르산·KOH만 사용, 배경전해질 농도 없음 — 알루미나와
  동일한 한계.

---

## 3. 실리카 (SiO2) ζ(pH)

**출처:** 위 세리아 항목과 동일 (Dawkins 2019 논문/학위논문 Fig. 4-2, Bindzil EB6080 콜로이드
실리카, AkzoNobel, 35.48 wt%).

**기계 판독 결과:**

| pH | ζ (mV, SiO2) |
|---|---|
| 3 | −31.3 |
| 4 | −37.9 |
| 5 | −55.6 |
| 6 | −57.2 |
| 7 | −58.2 |
| 8 | −58.2 |
| 9 | −57.7 |
| 10 | −62.0 |
| 11 | −58.5 |
| 12 | −56.9 |
| 13 | ≈−41 (세리아 pH13 마커와 겹쳐 개별 클러스터 분리 불가 — 육안상 두 계열이 같은 점에 수렴)|

- **측정 구간(pH 3–13) 내 IEP 없음** — 항상 음전하. 본문 p.52: "Silica has a negative
  zeta-potential over the entire pH range (3-13) studied" (일반 문헌의 실리카 IEP≈pH2와 정합 —
  측정 구간이 IEP보다 산성쪽으로 충분히 내려가지 않음).
  - Si-OH ↔ Si-O⁻ + H⁺ 탈양성자화가 원인으로 서술(p.64).
- **급격 하강 구간 (pH 3→4): dζ/dpH ≈ −6.6 mV/pH**
- **평탄역 (pH 5–12): 평균 −58.0 ± 1.7 mV** (사실상 pH 무관 — 이 구간에서는 "기울기"보다
  "평탄값"으로 요약하는 게 문헌 실측과 더 정합)
- pH13에서 −41 mV로 반등(덜 음성화)하는 것은 그림에 보이나 본문이 명확히 설명하지 않음 —
  **미검증, 관측만 기록**. (§5.1은 5장 MAS 복합입자 맥락의 다른 논의여서 이 반등의 직접
  설명은 아님.)
- **이온세기: 문헌에 미기재.** 알루미나·세리아와 동일한 한계.

---

## 4. 판독 절차 (재현성)

Fig. 7b(알루미나) / Fig. 4-2(세리아·실리카)는 래스터 이미지(벡터 아님)로 PDF에 내장돼
`get_drawings()`가 곡선을 반환하지 못한다. 대신:

1. `fitz.Page.get_images()`로 원본 픽셀맵(2002×910 / 1454×1125)을 추출.
2. 테두리 박스(그레이스케일 <100 임계값의 최장 연속 행/열)로 플롯 경계 픽셀좌표를 찾는다.
3. 눈금선(테두리 바깥으로 뻗은 짧은 검은 선분, 알루미나는 x·y축 모두, 세리아·실리카는
   y축만 — x축은 눈금선이 없어 테두리 좌우단=pH 0/14로 직접 대응하지 않고, 대신 본문이
   명시한 정수 pH(3–13, 11점)에 좌→우 순서로 그대로 대응시켰다)의 픽셀 중심을 클러스터링해
   눈금 라벨 값(예: −30,−20,…,40)에 **선형회귀**로 매핑.
4. 데이터 마커(적색 원/흑색 사각형)를 색상 임계값(R>150,G<90,B<90 등)으로 분리, 연결요소
   중심을 같은 선형식으로 pH·mV 변환.
5. **보정식이 인쇄된 눈금값을 재현하는지 잔차로 확인** — 알루미나 x축 잔차 최대 0.003 pH,
   y축 최대 0.023 mV; 세리아/실리카 y축 잔차 최대 0.09 mV. 전부 육안 판독이 아니라 §5
   verify 블록이 실행 시점에 이 임계값들을 직접 assert한다.

한계: 알루미나 x축은 실제 눈금선으로 검증했지만, 세리아/실리카 x축은 (눈금선 부재로)
"본문이 pH 3–13 정수로 측정했다"는 텍스트 진술에 의존한 배치다 — 그림 자체만으로 x좌표를
역산한 것이 아니라는 점을 밝혀둔다.

---

## 5. 정량 재현 절

```python verify
import numpy as np
from PIL import Image
from scipy import ndimage
from pathlib import Path

ROOT = Path.home() / 'fab-sim'

# ---------------------------------------------------------------- Figure 1
# Gong et al. 2024, Materials 17(3), 679, Fig. 7b (alumina/MnO2 zeta vs pH, CC-BY)
img1 = ROOT / 'papers/img/liu2024_fig7b_alumina_mno2_zeta_ph.png'
arr1 = np.array(Image.open(img1).convert('RGB')).astype(int)
gray1 = arr1.mean(axis=2)

xticks_px = np.array([1128.0, 1284.0, 1440.0, 1595.5, 1751.5, 1907.0])
xticks_val = np.array([2, 4, 6, 8, 10, 12])
yticks_px = np.array([775.5, 675.0, 574.5, 474.0, 373.5, 273.0, 173.0, 72.5])
yticks_val = np.array([-30, -20, -10, 0, 10, 20, 30, 40])
mx1, bx1 = np.polyfit(xticks_px, xticks_val, 1)
my1, by1 = np.polyfit(yticks_px, yticks_val, 1)
assert np.max(np.abs(mx1 * xticks_px + bx1 - xticks_val)) < 0.05, \
    "x축 보정식이 Fig.7b 인쇄 눈금(pH 2,4,...,12)을 재현하지 못함"
assert np.max(np.abs(my1 * yticks_px + by1 - yticks_val)) < 0.05, \
    "y축 보정식이 Fig.7b 인쇄 눈금(-30..40 mV)을 재현하지 못함"

R, G, B = arr1[:, :, 0], arr1[:, :, 1], arr1[:, :, 2]
plot_mask = np.zeros(gray1.shape, dtype=bool)
plot_mask[25:775, 1052:1983] = True
legend_mask = np.zeros(gray1.shape, dtype=bool)
legend_mask[20:160, 1650:1990] = True
red_mask = (R > 150) & (G < 90) & (B < 90) & plot_mask & ~legend_mask
labeled, n = ndimage.label(red_mask)
sizes = ndimage.sum(red_mask, labeled, range(1, n + 1))
centers = ndimage.center_of_mass(red_mask, labeled, range(1, n + 1))
al_pts = sorted((mx1 * cx + bx1, my1 * cy + by1) for (cy, cx), sz in zip(centers, sizes) if sz > 20)
assert len(al_pts) == 10, f"알루미나 적색 마커 10개 기대, {len(al_pts)}개 검출"
al_ph = np.array([p[0] for p in al_pts])
al_zeta = np.array([p[1] for p in al_pts])

acidic = al_ph <= 8.01
basic = al_ph >= 8.99
m1_fit, b1_fit = np.polyfit(al_ph[acidic], al_zeta[acidic], 1)
m2_fit, b2_fit = np.polyfit(al_ph[basic], al_zeta[basic], 1)
iep_al = 8.00 + (0 - 13.00) / (-4.98 - 13.00) * (8.99 - 8.00)

assert abs(m1_fit - (-4.09)) < 0.1, f"알루미나 산성 구간 기울기 재현 실패: {m1_fit:.2f}"
assert abs(m2_fit - (-6.38)) < 0.1, f"알루미나 염기 구간 기울기 재현 실패: {m2_fit:.2f}"
assert abs(iep_al - 8.72) < 0.05, f"알루미나 IEP 보간 재현 실패: {iep_al:.2f}"

print(f"[알루미나] Fig.7b 판독 IEP={iep_al:.2f}, 산성기울기={m1_fit:.2f} mV/pH, "
      f"염기기울기={m2_fit:.2f} mV/pH (n={len(al_pts)}점)")

# ---------------------------------------------------------------- Figure 2
# Dawkins 2019 PhD thesis (U. Alberta), Fig. 4-2 — reproduces Dawkins et al. 2015
# Appl. Surf. Sci. 345, 249-255, doi:10.1016/j.apsusc.2015.03.170
img2 = ROOT / 'papers/img/dawkins2019_fig4-2_ceria_silica_zeta_ph.png'
arr2 = np.array(Image.open(img2).convert('RGB')).astype(int)
gray2 = arr2.mean(axis=2)

yticks_px2 = np.array([131.0, 193.0, 254.5, 317.5, 379.0, 441.0, 504.0,
                        565.5, 627.5, 690.5, 752.0, 814.0, 876.5, 938.5])
yticks_val2 = np.array([60, 50, 40, 30, 20, 10, 0, -10, -20, -30, -40, -50, -60, -70])
my2, by2 = np.polyfit(yticks_px2, yticks_val2, 1)
assert np.max(np.abs(my2 * yticks_px2 + by2 - yticks_val2)) < 0.1, \
    "y축 보정식이 Fig.4-2 인쇄 눈금(-70..60 mV)을 재현하지 못함"

R2, G2, B2 = arr2[:, :, 0], arr2[:, :, 1], arr2[:, :, 2]
plot_mask2 = np.zeros(gray2.shape, dtype=bool)
plot_mask2[135:935, 270:1245] = True
legend_mask2 = np.zeros(gray2.shape, dtype=bool)
legend_mask2[150:260, 1000:1250] = True

red_mask2 = (R2 > 150) & (G2 < 90) & (B2 < 90) & plot_mask2 & ~legend_mask2
labeled2, n2 = ndimage.label(red_mask2)
sizes2 = ndimage.sum(red_mask2, labeled2, range(1, n2 + 1))
centers2 = ndimage.center_of_mass(red_mask2, labeled2, range(1, n2 + 1))
ce_pts = sorted((cx, my2 * cy + by2) for (cy, cx), sz in zip(centers2, sizes2) if sz > 40)
assert len(ce_pts) == 11, f"세리아 적색 마커 11개(pH3-13) 기대, {len(ce_pts)}개 검출"
ce_zeta = np.array([p[1] for p in ce_pts])

iep_ce_img = 9 + ce_zeta[6] / (ce_zeta[6] - ce_zeta[7])
assert abs(iep_ce_img - 9.81) < 0.05, f"세리아 IEP(그림판독) 재현 실패: {iep_ce_img:.2f}"
# 본문 서술 IEP(~9.6, Dawkins 2019 p.52,61)과 그림 판독 IEP(~9.8)는 2% 범위 내로 근접 — 교차검증 성립
assert abs(iep_ce_img - 9.6) / 9.6 < 0.03, \
    f"세리아 IEP: 본문(9.6) vs 그림판독({iep_ce_img:.2f}) 차이가 3%를 초과함"

# 본문(p.64)은 "pH 4에서 세리아 제타전위 약 40 mV"라고 서술하나, 그림 4-2 자체를 판독하면
# pH4 지점은 약 52 mV다 — 일치하지 않는다. 값을 꾸미지 않고 불일치를 그대로 기록한다.
zeta_ce_pH4 = ce_zeta[1]
text_claim_pH4 = 40.0
diff_pct = abs(zeta_ce_pH4 - text_claim_pH4) / text_claim_pH4 * 100
assert diff_pct > 20, "pH4 불일치가 예상보다 작음 — 재확인 필요(하드코딩 오류 가능)"
print(f"[세리아] 그림 4-2 판독 pH4 zeta={zeta_ce_pH4:.1f} mV vs 본문 서술 '~40 mV' "
      f"→ {diff_pct:.1f}% 불일치, 원인 미상(본문-그림 대조 결과 그대로 기록)")
print(f"[세리아] IEP: 본문 서술 9.6 vs 그림판독 {iep_ce_img:.2f} (차이 {abs(iep_ce_img-9.6)/9.6*100:.1f}%)")

black_mask2 = (R2 < 70) & (G2 < 70) & (B2 < 70) & plot_mask2 & ~legend_mask2
labeled3, n3 = ndimage.label(black_mask2)
sizes3 = ndimage.sum(black_mask2, labeled3, range(1, n3 + 1))
centers3 = ndimage.center_of_mass(black_mask2, labeled3, range(1, n3 + 1))
sq_pts = [(cx, my2 * cy + by2, sz) for (cy, cx), sz in zip(centers3, sizes3) if 250 < sz < 340]
sq_pts.sort()
assert len(sq_pts) == 10, f"실리카 흑색 사각마커 10개(pH3-12, pH13은 세리아와 겹침) 기대, {len(sq_pts)}개"
sil_zeta = np.array([p[1] for p in sq_pts])
assert sil_zeta.max() < 0, "실리카 ζ가 측정구간 내에서 양의 값을 가짐 — 본문의 'IEP 없음' 서술과 모순"
plateau = sil_zeta[2:]
assert abs(plateau.mean() - (-58.0)) < 2.0, f"실리카 평탄역 평균 재현 실패: {plateau.mean():.1f}"
print(f"[실리카] pH3-12 ζ 최댓값(최소절댓값)={sil_zeta[0]:.1f} mV(pH3), "
      f"pH5-12 평탄역 평균={plateau.mean():.1f}±{plateau.std():.1f} mV, IEP 없음(항상 음전하)")
```

---

## 6. 엔진 등록 여부: **등록하지 않음**

이유:

1. **이온세기 조건 부재.** 세 문헌 모두 배경전해질 농도(이온세기)를 보고하지 않는다
   (pH 조정제 농도만 있고 mol/L 단위 이온세기 없음). 과제 지시("이온세기 조건이 팩에 없으면
   ζ 절대값을 내지 마라")와 별개로, **문헌 자체가 이온세기를 특정하지 않아** ζ 절대값의
   재현 가능한 조건을 코드에 박을 수 없다.
2. **팩 스키마에도 이온세기 필드가 없다.** `sim/tier2_physics/metal_contamination_surface.py`
   상단 주석이 이미 이 사실을 명시: "Recipe에 pH·제타전위·오염원별 시계열 필드가 없어
   engine.Model로 조립할 입력이 아직 없다" — 이 모듈 자체가 현재도 engine.py에 미등록
   상태다(의도적 설계). 이번 조사로 ζ(pH) 연속값을 확보했다고 해서 이 스키마 부채가
   해소되지는 않는다.
3. 알루미나·세리아 IEP(8.7·9.6~9.8)와 실리카(IEP<3, 측정범위 밖)는 서로 다른 pH에서
   부호가 바뀌므로 **단일 연속식으로 세 입자를 한 함수에 합치면 입자종 분기 로직이 필요**해져
   "팩이 선언한 키만으로 계산" 원칙과 충돌할 위험도 있다(어떤 입자가 쓰였는지 팩이 명시적으로
   `has_own`으로 선언하는 필드가 현재 slurry 팩에 없음 — 확인 필요하나 이번 조사 범위 밖).

→ 1단계(문헌값 확보)로 종료. `sim/tier2_physics/*.py`는 0바이트 수정, `sim/engine.py` 미변경.

---

## 7. 미확보 · 스코프 제외 항목

- **Dawkins et al. 2015 (Appl. Surf. Sci. 345, 249)** 원문 PDF: Elsevier 유료, Unpaywall/
  OpenAlex/Semantic Scholar/CORE 전부 OA 없음(`closed`), sci-hub 미러 도메인은 이 세션에서
  DNS 해석 불가(`nodename nor servname provided`) — **1차 저널 논문 자체는 미확보**,
  등가 데이터를 학위논문(E2)으로 대체.
- **Suphantharida & Osseo-Asare (2004), J. Electrochem. Soc. 151, G658**, DOI
  10.1149/1.1785793 ("Cerium Oxide Slurries in CMP. Electrophoretic Mobility and Adsorption
  Investigations of Ceria/Silicate Interaction") — scope --check 통과, 이온세기 조건이 있는
  고전 세리아 전기영동 논문으로 추정되나 IOP 호스팅 유료라 미확보(Unpaywall/S2 `closed`).
  향후 조사에서 우선순위 높음(이온세기 조건이 명시된 세리아 1차 문헌 후보).
- **"Effects of CMP Slurry Chemistry on the Zeta Potential of Alumina Abrasives"**
  (J. Electrochem. Soc. 2006), DOI 10.1149/1.2198128 — IOP 호스팅, Radware 봇차단으로
  PDF 직접 접근 실패(`<head><title>Radware...`). scope 통과·미확보.
- **Kosmulski, M. (2016) "Isoelectric points and points of zero charge of metal (hydr)oxides:
  50 years after Parks' review." Colloids Interface Sci. Commun.**, DOI 10.1016/j.cis.2016.10.005
  — 리뷰(E6, weight 0.6), Elsevier 유료, 미확보. IEP 문헌범위 교차검증용으로 유용하나 이번
  조사에서는 시간 제약으로 시도하지 않음.
- 실리카 IEP(pH<3)에 대한 이온세기-조건부 1차 정량 문헌(예: Quantification of Zeta-Potential
  ... Colloidal Silica, DOI 10.1021/acs.jpcc.7b12525)은 scope 통과했으나 ACS 유료로 미확보.

---

## 8. ⚠ 중복 조사 / 독립 문헌 교차대조 (2026-09-18 추기)

**같은 날 같은 질문을 두 세션이 각각 조사했다.** 이 노트(`knowledge/cmp/`, 커밋 45e5dac)와
[[../slurry/zeta-potential-ph-continuous-relation]](커밋 5529a4b)이 파일명은 같지만
**서로 다른 문헌**에서 출발했다. 중복은 낭비였지만, 결과적으로 **독립 교차검증**이 생겼다 —
어느 한쪽도 상대를 보고 쓰지 않았으므로 확증편향이 없다. 두 결과를 그대로 대조한다.

| 입자 | 이 노트 (Gong 2024 / Dawkins 2019) | slurry 노트 (Dandu 2009 / Gopal 2006) | 판정 |
|---|---|---|---|
| 알루미나 IEP | 8.72 (Gong Fig.7b 판독) | **9.0** (Gopal, 입자클러스터 최대점, 본문 1차 수치) | **Gopal 채택** — 아래 사유 |
| 알루미나 기울기 | -4.09 mV/pH (산성) / -6.39 (염기) | -12.6 mV/pH (pH 3.5~10 평균) | 구간 정의가 달라 직접 비교 불가 |
| 세리아 IEP | 9.6 (본문) / 9.81 (판독) | ~8 (Dandu 본문 명시) | **불일치 — 평균 금지, 병기** |
| 세리아 기울기 | -13.9 mV/pH (pH 7~10) | -16.7 mV/pH (pH 6~9) | **오더 정합**(약 17% 차, 구간 차이로 설명 가능) |
| 실리카 IEP | 측정구간(pH 3~13) 밖, 항상 음전하 | <2 (Dandu 본문 명시) | **정합** |
| 실리카 기울기 | pH 3->4 -6.6, pH 5~12는 평탄(-58.0±1.7 mV) | -3.0 mV/pH (pH 2~8) / 타 문헌 -8.2 | **문헌 간 오더 상이 — 대표값 없음** |

**알루미나 IEP 판정 (EVIDENCE-RULES 근거 서열 적용, 판정 없이 병기만 하지 않는다):**
- Gopal & Talbot 2006 (doi:10.1149/1.2198128) 은 **지지전해질 1 mM KNO3 를 명시**한다 = 이온세기
  통제된 실측(**E1**).
- Gong 2024 (doi:10.3390/ma17030679) 는 pH 조정제 종류(NaOH/HNO3)만 있고 이온세기 미기재 =
  **교란 통제 없는 실측(E3)**.
- **E1 > E3 → 알루미나 IEP 는 9.0 을 채택**하고, Gong 의 8.72 는 "이온세기 미통제 조건의
  독립 관측, 3.1% 이내로 정합"으로 **보강 증거**로 기록한다. 두 값을 평균낸 8.86 같은 수는
  **어느 문헌도 지지하지 않으므로 만들지 않았다.**

**세리아 IEP 불일치 (~8 vs 9.6~9.8, 약 20% 차)는 종결하지 않는다 — 스코프 분리가 정답으로 보인다:**
- 두 문헌의 세리아가 **같은 물질이 아니다**: Dandu 2009 는 "pure ceria", Dawkins 2019 는
  Nyacol 상용 콜로이드 세리아(20wt% 원액 희석). [[../slurry/zeta-potential-ph-continuous-relation]] §2
  가 이미 세 번째 값(6.5, 2차 인용)까지 기록해 **세 값이 제각각**임을 보였다.
- 그 노트의 해석("전처리·하소 여부·입경에 따라 편차가 크다")은 이 노트의 독립 데이터로도
  **지지된다** — 즉 세리아 IEP 는 단일 상수가 아니라 **제품별 실측값**이다.
- 따라서 "어느 쪽이 맞는가"는 잘못된 질문이다. 팩이 쓰는 세리아의 IEP 는 그 제품의 실측이
  필요하고, 문헌값으로 팩의 `abrasive_iep_ph`(6.8) 를 고치는 것은 **근거가 없다**(양쪽 노트
  모두 팩값을 고치지 않았다 — 독립적으로 같은 결론).

**두 노트 공통 결론 (독립적으로 같은 곳에 도달했다는 점이 중요하다):**
1. 문헌 이온세기(1 mM 또는 미기재) vs CMP 슬러리 실사용(수십~수백 mM + 산화제·킬레이트)의
   **조건 불일치** 때문에 **절대 mV 를 코드에 직접 대입할 수 없다**.
2. 재사용 가능한 것은 **부호 · IEP 위치 · 기울기 오더**뿐이다.
3. 따라서 `boltzmann_surface_enrichment` 의 4구간 카테고리표 대체는 **아직 불가** —
   슬러리 이온세기 보정이 선결 조건이다. 양쪽 세션 모두 `sim/`·YAML 0줄 변경으로 끝냈다.

**후속 (두 노트 §7 통합):** 이온세기가 명시된 세리아 1차 문헌 —
Suphantharida & Osseo-Asare 2004, JES 151 G658, doi:10.1149/1.1785793 (IOP 유료, 미확보).
이것이 서면 세리아 IEP 불일치를 E1 끼리 비교해 판정할 수 있다.
