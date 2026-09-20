# Δ/cu_alkaline_benzenesulfonic `abrasive_d99_nm` — K-안정 콜로이달 실리카 D99 3회차(최종)

- 작성일: 2026-09-20
- 대상 파라미터: `knowledge/params/cu_alkaline_benzenesulfonic.yaml` `abrasive_d99_nm`(=`abrasive_ref_d99_nm`) 103.824688 nm, confidence=estimated
- 선행: 1회차 판정#71([[cu-alkaline-benzenesulfonic-abrasive-axis-kappa-delta]]), 2회차 2026-09-19([[abrasive-d99-psd-width-size-dependence]]), 비율 원출처 [[abrasive-particle-size-distribution-d99-tail]] §3 §5
- 규칙: EVIDENCE-RULES.md §금지 "3회차까지만 보류 허용" — 이 회차로 종결한다(4회차 없음).

## 0. 결론 요약

**(B) 미확보 → 값·등급 불변으로 영구 종결(판정#79).** `abrasive_d99_nm` = 103.824688 nm,
confidence = estimated 그대로 둔다. 다만 이번 회차는 앞 두 회차와 다른 **두 가지 실질 성과**가 있다:

1. **대상계 그 자체의 연마입자(Syton® OX-K)를 다루는 1차 특허를 처음 확보했다** —
   US6979252B1(DuPont Air Products NanoMaterials, 현 Versum; 발명자 Siddiqui 외;
   `papers/US6979252B1-dupont-syton-oxk-low-defectivity.txt`). 이 특허의 Example 1 /
   Examples 33-34 조성 서술은 US9200180B2 COMPONENTS D) 와 **문장 단위로 동일**하다
   ("30 weight percent (potassium-stabilized) dispersion in water with a particle size of
   50-60 nanometers as measured by Capillary Hydro-Dynamic Flow using ... CHDF 2000").
   즉 이 팩의 연마입자는 상품명 Syton® OX-K 로 특정된다 — 2회차까지는 모르던 사실이다.
2. **그런데 그 특허조차 D99 를 인쇄하지 않는다.** 꼬리를 개수축(>1 µm particles/mL)으로만
   보고한다. 그리고 §2.2 의 환산 계산이 보여주듯 그 개수축은 D99 로 **환산 불가능하다** —
   자릿수가 8.6배 떨어져 있어 99 퍼센타일 근처 정보를 전혀 담지 않는다.

따라서 미확보의 성격이 바뀌었다: "아직 못 찾았다"가 아니라 **"이 산업이 꼬리를 D99 로
보고하지 않는다"** 는 구조적 부재다. 4회차를 돌려도 같은 벽에 닿는다.

**⚠ 그리고 이 칸은 애초에 예측에 영향이 없다** — §3 의 실행 검증대로 `_f_delta` 는
`abrasive_d99_nm` 을 **`abrasive_ref_d99_nm` 과의 비로만** 소비하고, 이 팩은 둘을 같은 값으로
동반 선언했다. 어떤 배율로 동시에 흔들어도 Δ = 1.0 이다. 절대값 정밀도는 이 팩에서
**what-if 감도(사용자가 D99 만 흔들었을 때의 기울기)에만** 영향을 주고 기준 예측에는 0 이다.

## 1. 시도한 경로 전부 (성공/실패 모두)

### 1-1. 로컬 코퍼스 전수 재탐색 (네트워크보다 먼저) — **미확보**

대상: `papers/patents/*.html` 471건, `papers/` PDF 364건(fitz 텍스트 추출, 8건은 손상 파일로
열리지 않음)·txt 15건·xml 6건, `data/corpus/corpus.sqlite` fulltext_path 보유 1,574건.
검색어: `D99`, `99th percentile`, `oversize`, `>0.5 µm`, `LPC|large particle count`,
`potassium-stabilized|K-stabilized`, `CHDF|capillary hydrodynamic`. 동시출현만으로 판단하지
않고 상위 후보는 전부 태그 제거 후 본문 문맥을 직접 열어 실측표 유무를 확인했다(판정#78 교훈).

| 검색어 | 텍스트 실히트 | 직접 열어본 후보 | 결과 |
|---|---|---|---|
| `potassium-stabilized` | 2건 — US20110165777A1(DuPont Air Products, χ 판정#20 출처), US9200180B2(이 팩 원 특허) | 둘 다 | 둘 다 "0.5 µm 필터 여과 후에도 가용성 폴리실리케이트 잔존" 서술과 CHDF D50 상당값뿐. **D99·D90·LPC 수치표 없음**(1회차 결론 재현) |
| `CHDF` | 2건 — US9200180B2, ucf-thesis-si-passivation-2018.pdf | 둘 다 | 전자는 위와 동일, 후자는 Si 부동태화 학위논문(무관) |
| `D99` (HTML 특허 21건) | Cu 관련 8건: KR102444548B1·KR101557514B1·CN106244021B·CN1131125C·CN1158373C·US8070843B2·CN103339218A·CN1305547C | 전부 | 태그 제거 후 본문에 D99가 실제로 남는 것은 CN106244021B·JP6581198B2(Versum 세리아코팅 실리카 패밀리, "초음파 후 D50/D75/D99 변화 <10%"라는 Markush 상투구)뿐. 나머지는 HTML 속성/ID 문자열 오탐. **실측 D99 표 0건** |
| `D99` (PDF·sqlite) | us20190127607a1-versum-ceria-coated-silica-d99.pdf(33), US8439995(8) 외 20여 건 | 상위 4건 | Versum 세리아코팅 실리카(2회차 §2와 같은 단일 코어 시리즈, oxide 용도)·Hitachi 세리아(Δ 지수 출처)뿐. 나머지 `d 99`는 페이지 번호·연도 등 오탐 |
| `LPC` (PDF) | lin2006(Remsen, Cabot fumed silica, oxide)·lu2018-jss(Cu 배리어 콜로이달 실리카)·granstrom2015(Fujimi)·khanna2018/2019·wood2019·entegris 앱노트 2건 | lu2018·granstrom2015·lin2006 | **lu2018(DOI: 10.1149/2.0101806jss)**: 콜로이달 실리카 20 wt%, 평균 90 nm, Cu 배리어 슬러리(FA/O II 착화제, Tianjin), SPOS LPC(≥0.5 µm) 1.05~4.0×10⁵ particles/mL vs EDA 분산제 농도(Fig. 9) — **D99 아님**, 분산제 축 실험이라 기준 슬러리 꼬리값으로 못 쓰고, 실리카 안정화 화학 미기재. granstrom2015는 Fujimi PSD-shift 방법론(값 없음). lin2006은 fumed silica·oxide(기존 lpc 노트 출처) |
| `LPC` (HTML 특허) | US20070254964A1/US8211193B2(Fujifilm Planar Solutions "Ultrapure colloidal silica"), EP2995662B1(Fujifilm, Co CMP) | 셋 다 | 전자: LPC 데이터는 FIGS. 3-4 그래프 전용, 본문 수치 없음. EP2995662B1은 선행기술 인용으로 "US 2004/0159050 A1: 여과 후 0.5 µm 초과 입자 <150,000개/30 µL"만 재인용 |
| `oversize` | basim2000(oxide, 첨가 대입자 실험)·US8815396B2·US6620215B2 등 5건 | 상위 3건 | 의도적 대입자 첨가 실험 또는 Markush 문구, 제조 PSD 꼬리 아님 |
| `99th percentile` | HTML 34건 | 영문 9건 전부 | 전부 "99 wt% 물", "99% 표면 피복" 등 **오탐**. EP1485440B1/US20090029553A1의 "99%가 평균의 30% 이내"는 Markush 설계 문구 |

부수 발견: `papers/evonik-idisil-cmp-colloidal-silica-datasheet.pdf`(Evonik IDISIL KE 50/70/90/125,
2025-08)는 **K-안정 콜로이달 실리카 제조사 데이터시트 원문**이다(pH ~10.3, "trace metals other
than potassium", peanut 형상). 그러나 인쇄 스펙은 Z-avg 50/70/90/125 nm·SiO₂ 20 wt%·금속 <300 ppb
뿐 — **D99·LPC 꼬리 스펙 없음.** 즉 제조사 공개 데이터시트 수준에서는 꼬리 스펙을 인쇄하지 않는
관행이 확인된다(§1-2의 네트워크 탐색 결과와 합쳐 판단).

**결론(1-1)**: 로컬 코퍼스에는 K-안정 콜로이달 실리카(어느 제조사든)의 D99 실측값이 0건이다.
Cu CMP 콜로이달 실리카 꼬리 실측으로 가장 가까운 것은 lu2018의 LPC 개수(≥0.5 µm)이며, 이는
`_f_delta`가 소비하는 D99 축이 아니다(docstring "LPC 개수축 — 입력 축 미신설").

### 1-2. K-안정 콜로이달 실리카 제조사 특허·데이터시트 꼬리 스펙 — **부분 확보(개수축), D99 미확보**

로컬 코퍼스가 0건이었으므로 네트워크로 나갔다(Exa 웹검색 → Google Patents 전문 추출).

**핵심 확보: US6979252B1** — "Low defectivity product slurry for CMP and associated
production method", DuPont Air Products NanoMaterials L.L.C.(현 Versum Materials US LLC),
출원 US11/030,503, 우선일 2004-08-10, 공개 2005-12-27. 전문을
`papers/US6979252B1-dupont-syton-oxk-low-defectivity.txt` 에 저장하고 `papers/INDEX.json`
에 등록했다.

**왜 이것이 이 팩에 대해 대상계 문헌인가 (E1 후보였던 이유)**

| | US9200180B2 COMPONENTS D) (이 팩의 연마입자) | US6979252B1 Example 1 / Examples 33-34 |
|---|---|---|
| 고형분 | 30 wt% dispersion in water | 30 weight percent dispersion in water |
| 안정화 | potassium-stabilized | potassium-stabilized (Ex.33-34), Syton® OX-K (Ex.1-32) |
| 입경 | 50-60 nm | 50-60 nanometers |
| 측정법 | Capillary Hydro-Dynamic Flow, CHDF 2000 (Matec) | Capillary Hydro-Dynamic Flow, CHDF 2000 (Matec) |
| 출원인 | (Air Products) | DuPont Air Products NanoMaterials |

네 항목이 전부 일치하고 문장 표현까지 같다. 같은 회사의 같은 상품(Syton® OX-K)이다.
2회차에서 "K-안정 콜로이달 실리카 자체의 실측을 못 찾았다"고 한 바로 그 대상이다.

**그러나 인쇄된 꼬리 지표는 D99 가 아니라 개수축이다** (전문 §Examples, TABLE 1·TABLE 5):

| 슬러리 | post-polish defects >0.13 µm (정규화) | post-HF dip defects (정규화) | **oversize particles/mL > 1 µm** |
|---|---|---|---|
| Ex.1 Syton® OX-K 원액(대조) | 1.00 | 1.00 | **50,354** |
| Ex.2 원심분리 | 0.14 | 0.50 | **350,561** |
| Ex.3 계면활성제만 | 0.90 | 0.48 | **62,542** |
| Ex.4 원심분리 + 계면활성제 | 0.07 | 0.017 | **384,556** |

(TABLE 5, Westfalia SA20 대형 원심분리: Ex.33 정규화 oversize 4.4 vs Ex.34 대조 1.0,
결함은 0.03/0.008 로 감소.)

**부수 발견 — 이 특허의 결론이 Δ 모델의 전제와 충돌한다.** 위 표에서 oversize 개수와
결함 수의 Spearman ρ = **-1.00**(n=4) 으로 **완전한 역상관**이다. 특허 본문이 이를 명시적으로
결론화한다: "defectivity introduced during oxide CMP is not correlated with nor related to
the number of oversize particles but rather relates to the level of soluble polymeric
silicates". 즉 이 계에서 결함을 만든 것은 대입자 꼬리가 아니라 **가용성 폴리실리케이트 겔**
이었다. 원심분리가 겔을 제거하면서 동시에 1 µm 초과 개수는 7배 늘렸는데 결함은 1/14 로
줄었다.

⚠ 단, **이것을 Δ 의 반증으로 채택하지 않는다**: (a) 이 특허의 대상은 PETEOS(산화막) CMP 이고
이 팩은 알칼리 Cu CMP 다, (b) "1 µm 초과 개수"는 §2.2 대로 D99 축과 자릿수가 다른 별개
관측량이다, (c) `_f_delta` docstring 이 근거로 삼는 Remsen 2006 의 선형 개수 관계는
**의도적으로 첨가한** 대입자에 대한 것이고 여기는 제조 공정 부산물이다.
**기록만 하고 Δ 함수형은 건드리지 않는다** — 노트 §4 에 후속 갱으로 남긴다.

**그 외 시도한 네트워크 경로(전부 D99 미확보)**

| 경로 | 결과 |
|---|---|
| Google Patents 직접 curl (US6979252B1) | HTTP 503 봇차단 → Exa 전문추출로 우회 성공 |
| freepatentsonline.com / patft.uspto.gov | 연결 실패(000) |
| Evonik IDISIL KE 데이터시트(로컬 확보본) | Z-avg 50/70/90/125 nm·금속 <300 ppb 만, **꼬리 스펙 인쇄 안 함** |
| Fujifilm US20070254964A1 / US8211193B2 (ultrapure colloidal silica) | LPC 가 FIGS.3-4 그래프 전용, 본문 수치 없음 |
| EP2995662B1 | 선행기술 재인용("0.5 µm 초과 <150,000개/30 µL")뿐 — 2차 인용 |
| lu2018 (doi:10.1149/2.0101806jss) | Cu 배리어 콜로이달 실리카 SPOS LPC(≥0.5 µm) 1.05~4.0×10⁵/mL — 분산제 축 실험, 안정화 화학 미기재, D99 아님 |

**소결**: 제조사·특허·데이터시트 세 층위 전부에서 콜로이달 실리카의 꼬리는 **개수축(LPC,
oversize count)으로 보고되고 백분위(D99)로는 보고되지 않는다.** 1·2회차의 "못 찾았다"는
탐색 부족이 아니라 이 산업의 보고 관행이다.

### 1-3. `_f_delta` 소스 직접 판독 — 절대값이 필요한가, 비만 필요한가 — **비만 필요**

`sim/factors.py:2019-2110` 을 직접 읽었다. 관계식은

    Δ = (D99 / D99_ref)^n × (1 + a)

이고, 코드(2085-2093행)는 `abrasive_d99_nm` 과 `abrasive_ref_d99_nm` 을 읽어 **비만** 만든다.
절대값이 들어가는 곳은 **한 군데도 없다** — 임계 위치(D99/d_c)와 치수 상한(2a_max, δ_max)은
같은 docstring 이 "진단 출력(배수 아님, notes 로만 — status/confidence/value 에 영향 없음)"
이라고 명시한다.

이 팩은 `abrasive_d99_nm` = `abrasive_ref_d99_nm` = 103.824688 로 **동반 선언**돼 있다
(동반 이동 규칙, kp 이중계상 방지). 따라서 기준 조건 Δ 는 **어떤 절대값을 넣어도 정확히 1.0**
이다 — §3 verify 블록이 0.5·0.678·2.0배로 실행 확인한다.

**그래서 절대값 부재가 등급을 막는 진짜 이유인가?** 두 개를 갈라야 한다:

- **기준 예측**: 영향 0. 절대값이 틀려도 이 팩의 MRR·Δ 출력은 비트 단위로 같다.
- **what-if 감도**: 영향 있음. 사용자가 UI 에서 D99 **만** 흔들면(ref 고정) 기울기가
  n=2.54 거듭제곱으로 나오는데, 그 출발점이 103.8 nm 냐 70.4 nm 냐에 따라 같은
  "절대 D99 = 200 nm" 입력이 다른 배수를 준다.

confidence 는 후자를 보증하는 등급이므로 **estimated 유지가 맞다** — 절대값이 예측에
안 쓰인다는 이유로 등급을 올리는 것은 "안 쓰이니까 맞다"는 비논리다. 다만 이 사실은
**이 칸의 실무적 심각도를 낮춘다**: 지금까지 3회차 동안 이 칸을 최우선 병목(`blockers.py`
1위)으로 다뤄 왔는데, 실제로는 기준 예측에 영향 0 인 축이었다. 이 관측을 §4 에 기록한다.

## 2. 판정

### 2.1 결론: **(B) 미확보 → 영구 종결(판정#79)**

값 103.824688 nm, confidence=estimated **불변**. `knowledge/params/cu_alkaline_benzenesulfonic.yaml`
과 `sim/` 은 한 줄도 바꾸지 않는다. `validation/C2-CLOSURES.yaml` 에
`delta / cu_alkaline_benzenesulfonic` 종결을 등록한다.

**종결 근거 서열(EVIDENCE-RULES)**
- 확보한 것: US6979252B1 TABLE 1 개수축 실측 4점 — 대상계 연마입자 자체(Syton® OX-K)의
  1차 통제실측이므로 근거등급 자체는 **E1** 이다.
- 그러나 **관측량이 다르다**. D99 는 백분위(분포의 99% 지점 직경)이고 LPC 는 절대 개수다.
  §2.2 가 보이듯 환산 불가능하다. E1 이라도 **다른 물리량을 재는 E1 은 이 칸을 못 채운다**.
- 3회차 소진(판정#71 → 2026-09-19 2회차 → 본 회차). EVIDENCE-RULES 서두 규칙에 따라
  4회차 없이 종결한다.

### 2.2 왜 개수축 → D99 환산이 불가능한가 (정량)

Syton® OX-K 원액: 30 wt% 실리카, ρ=2.20 g/cm³ → 부피분율 0.16304.
D50 = 55 nm 구형 가정 시 입자 1개 부피 = π/6·(55e-7 cm)³ → 개수농도 **1.872×10¹⁵ /mL**.

TABLE 1 의 >1 µm 개수 50,354/mL 이 전체에서 차지하는 **개수 분율**은

    50,354 / 1.872e15 = 2.69×10⁻¹¹

즉 1 µm 초과 입자는 상위 **99.999999997 퍼센타일**에 해당한다. D99(상위 1%, 분율 10⁻²)
와는 **약 8.6 자릿수** 떨어져 있다. 로그정규 꼬리에서 8.6 자릿수 아래의 개수 하나로
99 퍼센타일 직경을 복원하려면 분포 형상(σ_g)을 따로 알아야 하는데, 그 σ_g 가 바로
지금 구하려는 미지수다 — **순환이다.**

(같은 이유로 2회차의 CMC Materials D90→D99 Hatch-Choate 외삽도 채택되지 않았었다.
그쪽은 자릿수가 1개 차이라 원리적으로는 가능했고 3중 불일치 때문에 기각됐다 —
이번 건은 **원리적으로 불가능**하다는 점에서 다르다.)

### 2.3 재오픈 조건

- K-안정(또는 임의 제조사) 순수 콜로이달 실리카의 **백분위 PSD 표**(D50 과 D90/D95/D99 를
  같은 표에 인쇄한 것)가 나오면 즉시 재오픈.
- 또는 `_f_delta` 에 **LPC 개수축 입력이 신설**되면(현재 docstring 이 "입력 축 미신설"로
  명시) 이 특허의 4점이 그 축의 1차 실측으로 바로 쓰인다 — 그때는 D99 축 자체가
  우회된다. 이쪽이 더 유망한 경로다(§4).

## 3. verify

```python verify
# ─────────────────────────────────────────────────────────────────
# (1) 현재값 재현: 팩 D50 55.0 nm × US10894906B2 Table 1 "No Treatment" D99/D50
ratio = 287.5 / 152.3
d99 = 55.0 * ratio
assert abs(ratio - 1.887722) < 1e-6, ratio
assert abs(d99 - 103.824688) < 1e-6, d99

# (2) 2회차 대체후보(CMC US11725116B2 1F, Hatch-Choate D99≈70.4nm)와의 괴리 — 미채택 사유
alt = 70.4
gap = (d99 - alt) / alt
assert 0.44 < gap < 0.50, gap          # 약 47%

# (3) §2.2 환산 불가능성 — >1µm 개수가 D99 와 몇 자릿수 떨어져 있는가
import math
w, rho_s, rho_w = 0.30, 2.20, 1.00     # US6979252B1 Ex.1: 30 wt% 수분산
vol_frac = (w/rho_s) / ((w/rho_s) + ((1-w)/rho_w))
assert abs(vol_frac - 0.163043) < 1e-5, vol_frac
d_cm = 55e-7                            # D50 55 nm
n_per_ml = vol_frac / (math.pi/6 * d_cm**3)
assert 1.8e15 < n_per_ml < 1.9e15, n_per_ml
tail_frac = 50354 / n_per_ml            # TABLE 1 Ex.1 대조군 실측
assert tail_frac < 1e-10, tail_frac
orders = math.log10(0.01 / tail_frac)   # D99 는 분율 1e-2
assert orders > 8.0, orders             # 8.6 자릿수 — 환산 불가

# (4) US6979252B1 TABLE 1: oversize 개수 vs 결함 수가 역상관(특허 자신의 결론)
from scipy import stats
oversize = [50354, 350561, 62542, 384556]      # Ex.1/2/3/4, particles/mL >1µm
defects  = [1.00,  0.14,   0.90,  0.07]        # post-polish >0.13µm, 정규화
rho, _ = stats.spearmanr(oversize, defects)
assert rho == -1.0, rho                        # 완전 역상관

# (5) _f_delta 는 D99 를 비로만 소비 — 절대값은 기준 예측에 영향 0
from sim.engine import Recipe
from sim.factors import compute_factors
rr = Recipe(pack="cu_alkaline_benzenesulfonic").resolve()
f = compute_factors(rr)["delta"]
assert f.status == "modeled", f.status
assert f.confidence == "estimated", f.confidence   # 이 회차에서 승격하지 않았다
assert abs(f.value - 1.0) < 1e-12, f.value
n = float(rr.pack.get("damage_exponent"))
d0 = float(rr.pack.get("abrasive_d99_nm"))
dr = float(rr.pack.get("abrasive_ref_d99_nm"))
assert abs(d0 - dr) < 1e-9, (d0, dr)               # 동반 선언
for scale in (0.5, 0.678, 1.0, 2.0):               # 동반 스케일 → 항상 1.0
    assert abs(((d0*scale)/(dr*scale))**n - 1.0) < 1e-12, scale
```

## 4. 출처

1. **US6979252B1** — Siddiqui, Castillo, Kapoor, Keefover, Richards; DuPont Air Products
   NanoMaterials LLC (현 Versum Materials US LLC), "Low defectivity product slurry for CMP
   and associated production method", 2005-12-27. 전문 로컬:
   `papers/US6979252B1-dupont-syton-oxk-low-defectivity.txt` (INDEX 등록). **E1**,
   단 관측량 불일치(개수축 ≠ 백분위) — §2.1.
2. **US9200180B2** — Air Products, COMPONENTS D). 로컬 `papers/patents/US9200180B2.html`.
   이 팩의 연마입자 스펙 원출처(CHDF 50-60 nm). D99 미인쇄(1회차 확인, 이번 재확인).
3. **US10894906B2** — Versum Materials, Table 1 "No Treatment" D99/D50 = 287.5/152.3.
   현재값의 비율 출처(1회차, 세리아코팅 복합입자 코어 → 용도 불일치로 estimated).
4. **US11725116B2** — CMC Materials, Table 1C. 2회차 대체후보(D50=55nm 조성 1F,
   D90=63nm → Hatch-Choate D99≈70.4nm). 3중 불일치로 미채택.
5. Lu et al. 2018, *J. Solid State Sci. Technol.*, **doi:10.1149/2.0101806jss** —
   Cu 배리어 콜로이달 실리카 SPOS LPC(≥0.5 µm). 관측량 불일치.
6. Remsen et al. 2006, **doi:10.1149/1.2184036** — `_f_delta` 꼬리 항의 원 근거
   (임계 초과 개수 선형). 첨가 대입자 실험이라 제조 부산물 꼬리와 다름(§1-2 (c)).
7. Basim & Moudgil 2002, **doi:10.1006/jcis.2002.8352** — Δ 응집 항 근거(이 회차 미변경).

> ⚠ **1차 출처 확보 실패 범위 명시**: K-안정 콜로이달 실리카의 **D99 백분위 실측값**은
> 로컬 코퍼스(특허 471 + 논문 1,574) 전수 + 네트워크 6경로에서 **끝내 확보하지 못했다.**
> 확보한 것은 같은 물질의 **개수축 꼬리 실측**이며, §2.2 대로 D99 로 환산 불가능하다.

## 5. 다음 작업자에게 남기는 갱

1. **(유망) `_f_delta` 에 LPC 개수축 입력 신설** — docstring 이 이미 "LPC 개수축 …
   입력 축 미신설"이라고 자백하고 있고, 이번에 확보한 US6979252B1 TABLE 1 4점 +
   기존 Fujifilm US10907074(800,000/wt% @0.2 µm) + lu2018(1.05~4.0×10⁵/mL @0.5 µm)로
   **세 계의 1차 실측**이 모인다. D99 백분위를 못 구하는 것이 구조적이라면 축을 바꾸는
   것이 정답일 수 있다. ⚠ 단 축 신설은 함수형 변경이므로 사용자 승인 사항 — 제안만 남긴다.
2. **(주의) 대입자 꼬리 ↔ 결함 인과의 반례가 나왔다** — US6979252B1 은 같은 슬러리에서
   oversize 개수를 7배 늘리면서 결함을 1/14 로 줄였고(ρ=-1.00), 원인을 가용성
   폴리실리케이트로 귀속한다. Δ 의 전제("스크래치는 꼬리가 만든다")가 **산화막 CMP 의
   일부 레짐에서 성립하지 않는다**는 1차 증거다. 반증으로 채택하지 않은 이유는 §1-2 (a)(b)(c).
   Δ 함수형 재검토 시 이 문헌을 반드시 대조할 것.
3. **(관측) 이 칸은 기준 예측에 영향 0 이었다** — §1-3. `blockers.py` 가 "승격 시 오르는
   칸 수"로만 순위를 매겨 3회차 동안 최우선 병목으로 잡혀 있었으나, 실제 예측 영향은
   what-if 감도에만 있다. blockers 순위에 **예측 영향도 축을 병기**하는 개선을 제안한다.
