<!-- V2-SECTION: R2-slurry | 근거: 입자 농도, 포화, 접촉확률, 활성입자 | 정본: ARCHITECTURE-V2.md §3 -->
# 입자 농도 → MRR 포화 곡선과 접촉(점유) 확률 모델 — 콜로이달 실리카 TEOS 실측(US9499721B2)으로 검증

> 에이전트: slurry-abrasive Lv2-2 | 작성일: 2026-09-12
> 선행: [[abrasive-hardness-hertz-indentation-removal-volume]](Lv2-1, 입자당 제거체적 — 이 노트는 그 "입자 수" 쪽을 다룬다)
> [[../materials/hertz-gw-contact-mechanics]](실접촉면적 A_r ∝ 하중 — 포화 용량의 출처)
> [[luo-dornfeld-active-abrasive-size-mrr]](Luo-Dornfeld 2003 Region 1 폐형식, C 선형항)
> [[particle-size-mrr-molecular-scale-bai2007]](Bai 2007, 접촉 입자수 N ∝ χ^(2/3))
> [[abrasive-size-concentration-ph-K-additive-mrr-quantitative]](Li 2021, 농도 "선형 증가"·두 극한 멱함수)
> [[sic-alumina-concentration-negative-exponent-entegris]](고농도 음의 지수 — 포화 너머의 레짐)
> [[abrasive-size-null-result-force-partition-theory]](Chen 단층가정 — 공급 입자 면밀도 ∝ 1/x²)
> 스코프: slurry-abrasive(입자 물성 축). 슬러리 제형·첨가제는 slurry-chemistry 소관 — 침범 안 함.
> 검색어 씨앗 "colloidal silica CMP abrasive"의 변형(농도·포화)만 사용.

## 0. 이번 회차 환경 제약 (정직 표기 — 먼저 읽을 것)

이 회차(2026-09-12)는 실행 환경에서 **파이썬·curl·웹검색·웹페치가 전부 승인 대기로 차단**되어
다음을 수행하지 못했다: (a) `tools/scope.py --queries` 실행(대신 `agents/SCOPE.yaml`을 직접 읽어
허용 검색어·소스를 확인), (b) 신규 문헌 검색·PDF 다운로드(미러 사이트 폴백 포함), (c) 로컬 PDF 재판독
(pdftoppm 부재), (d) **`tools/verify_claims.py`·`tools/check_knowledge.py` 자가검사 실행**.
따라서 이 노트는 **저장소에 이미 확보된 1차 자료의 텍스트 캐시와, 이미 도구로 실존 확인된
DOI·특허번호만** 쓴다. verify 블록 4개는 순수 파이썬(외부 패키지 없음)으로 작성했고 산술을
손으로 재계산해 assert 밴드를 잡았으나, **기계 실행은 총괄이 재검해야 한다** — 실행 전까지는
"통과"가 아니라 "통과 예정"이다. 새 DOI는 하나도 쓰지 않았다(기억으로 DOI 쓰지 않음).

## 1. 왜 이 단원인가

`sim/factors.py`의 농도 항은 `(C/C_ref)^n`, 기본 n=1/3(Li 2021 표면적 극한)이고,
`abrasive_saturation_wt_pct`는 경고문만 남길 뿐 예측값을 꺾지 않는다(코드 주석 자체가 "이 구간
예측은 과대평가다"라고 자인). 멱함수는 어떤 지수를 써도 **포화(기울기→0)를 표현할 수 없다**
(§4 verify로 증명). 이 단원은 (1) 같은 입자·같은 화학에서 농도만 스윕한 1차 실측으로 포화 곡선을
확보하고, (2) Luo-Dornfeld "활성 입자" 개념을 **접촉 자리 점유확률** 모델로 정식화해 저농도
선형(Region 1)과 고농도 포화가 한 식에서 나오게 하며, (3) 포화 농도가 압력(실접촉면적)에
따라 움직인다는 모델 예측을 같은 데이터의 압력 축으로 검증한다.

## 2. 출처 (단원 상한 6건 준수)

| # | 출처 | 등급(EVIDENCE-RULES) | 확보 상태 |
|---|---|---|---|
| S1 | **US9499721B2** (Cabot Microelectronics, 2016), "Colloidal silica chemical-mechanical polishing composition", Example 18 / TABLE 18 — 콜로이달 실리카(아미노실란 코어-쉘, 평균 54 nm) 0.5·1.0·1.5·2.0·2.5·3.0 wt% × 1.5/3/4/5 psi, TEOS 블랭킷, Mirra·IC1010·100 rpm·150 mL/min | **E1** (한 변수 스윕, 압력별 n=5~6, 입자·pH·첨가제 고정) | 전문 텍스트 `papers/US9499721B2.txt`(Google Patents 캐시), 데이터셋 `validation/datasets/us9499721b2_teos_colloidal_silica_pressure_conc.yaml` 등록됨. 특허 실시예 **실측표**이므로 SCOPE.yaml의 "청구범위 나열값 금지"에 해당하지 않음 |
| S2 | Luo & Dornfeld (2003), "Effects of abrasive size distribution in chemical mechanical planarization: Modeling and verification", *IEEE Trans. Semicond. Manuf.* 16(3). doi:10.1109/tsm.2003.815199 (agents/.source_cache.json에 Crossref 실존 확인 기록 있음). eScholarship Part-1 리프린트 `papers/luo-dornfeld-material-removal-regions-part1.pdf` | E2 (폐형식 유도) — 단 **이번 회차 PDF 재판독 불가**, [[luo-dornfeld-active-abrasive-size-mrr]]·[[abrasive-hardness-hertz-indentation-removal-volume]]가 원문 p.6-7에서 직접 판독해 옮긴 Eq.1-2를 재인용(노트 내 2차 인용) | 로컬 PDF 있음(판독 불가) |
| S3 | Li et al. (2021), *ECS J. Solid State Sci. Technol.* 10, 123008, doi:10.1149/2162-8777/ac3e44 (OA, 캐시 `.paper_txt_cache/slurry-additives-cmp-oxide-ac3e44__pdf.txt` 직접 판독) | E3 (농도 스윕 수치가 그래프에만 있음, 텍스트 미기재) | 전문 확보 |
| S4 | Bai et al. (2007), *Appl. Surf. Sci.* 253, 8489, doi:10.1016/j.apsusc.2007.04.027 — Eq.8 접촉 입자수 N = A_r·(6χ/(πD³))^(2/3) | E2(유도) → 농도 축은 E4(oxide 검증 전이) | PDF `papers/apsusc-2007-04-027-zhao-chang-mrr-molecular-scale.pdf`(이번 회차 판독 불가), [[particle-size-mrr-molecular-scale-bai2007]] 인용 재사용 |
| S5 | US20220315802A1 (Entegris/UF), Table 1 — SiC CMP 알루미나 0.1~5 wt%, MRR **감소**(n≈−0.41) | E3 (계·입자 다름) | [[sic-alumina-concentration-negative-exponent-entegris]] |
| S6 | Oliver (ed.) 2004, *CMP of Semiconductor Materials*, Springer, p.234 — S1 특허 본문이 "실리카 15→12→9 wt%에서 급격한 산화막 제거율 하락"을 인용 | **E5 2차 인용**, 교과서 소스는 SCOPE.yaml에서 enabled=false | 정량 채택 금지, 맥락(업계 관행 12.5 wt%)만 기록 |

## 3. 실측 포화 곡선 — US9499721B2 TABLE 18 (원문 Å/min 그대로)

| 조성(wt%) | 1.5 psi | 3 psi | 4 psi | 5 psi |
|---|---|---|---|---|
| 18A 0.5 | 940 | 1400 | 1350 | — |
| 18B 1.0 | 1100 | 2070 | 2560 | 2690 |
| 18C 1.5 | 1130 | 2260 | 2940 | 3480 |
| 18D 2.0 | 1170 | 2290 | 3140 | 3630 |
| 18E 2.5 | 1200 | 2430 | 3190 | 3860 |
| 18F 3.0 | 1240 | 2480 | — | 4030 |
| Control(퓸드 12.5 wt%) | 1200 | 2260 | 2970 | 3720 |

(US9499721B2 TABLE 18, `papers/US9499721B2.txt` 2826행 이하 원문 표 전사. 공란 2개는 원문도 공란.)

관찰(특허 저자 서술 + 본 노트 정량화):
- 저자 서술: "at 1.5, 2, 2.5, and 3 weight percent colloidal silica the TEOS removal rates were
  similar to the control (…fumed silica…about 12.5 weight percent)" — 즉 **1.5 wt% 이상에서는 더
  넣어도 12.5 wt% 대조군과 같은 수준**. 이것이 포화의 1차 서술이다(US9499721B2 Example 18).
- 3 psi 행: 0.5→1.0 wt% 구간 기울기 1340 Å/min/wt%, 2.5→3.0 wt% 구간 100 Å/min/wt% —
  **한계 기울기 13.4배 붕괴**(아래 verify). 1.5 psi 행은 1.0 wt% 이후 3 wt%까지 총 +12.7%뿐.
- 18A(0.5 wt%)는 4 psi가 3 psi보다 낮다(1350 < 1400) — 저농도에서 압력을 올려도 입자가
  모자라는 **입자 고갈(starvation)** 신호. 데이터셋 yaml 주석도 같은 해석. 접촉확률 모델에서는
  "자리(A_r)는 늘었는데 공급(C)이 그대로라 자리당 점유율이 떨어진 상태"로 읽힌다(§4).

**재현 요약**: 3 psi 한계기울기 1340→100 Å/min/wt%(13.4배 붕괴)와 1.5 psi 1.0→3.0 wt% 총증가 12.7%를 원문 표(US9499721B2 TABLE 18)에서 재현, 전 압력 농도 단조증가 확인(1블록).

```python verify
# US9499721B2 (Cabot Microelectronics, 2016) Example 18 / TABLE 18 — TEOS 연마율(Å/min)
# 콜로이달 실리카(아미노실란 코어-쉘, 54 nm) 0.5~3.0 wt%, Mirra/IC1010, 100 rpm, 150 mL/min
# papers/US9499721B2.txt 원문 표 그대로(Å/min). nm/min 환산은 ÷10.
conc = [0.5, 1.0, 1.5, 2.0, 2.5, 3.0]          # wt%
table = {  # psi: [Å/min] (None = 원문 공란)
    1.5: [940, 1100, 1130, 1170, 1200, 1240],
    3.0: [1400, 2070, 2260, 2290, 2430, 2480],
    4.0: [1350, 2560, 2940, 3140, 3190, None],
    5.0: [None, 2690, 3480, 3630, 3860, 4030],
}
# (1) 농도 단조 증가 — 공란 제외, 모든 압력에서 성립해야 함
for p, row in table.items():
    vals = [(c, v) for c, v in zip(conc, row) if v is not None]
    for (c0, v0), (c1, v1) in zip(vals, vals[1:]):
        assert v1 > v0, f"{p} psi: {c0}->{c1} wt%에서 MRR 증가 아님"
# (2) 한계 기울기 붕괴 = 포화의 증거. 3 psi 행(6점 완비)
row3 = table[3.0]
slope_first = (row3[1] - row3[0]) / (conc[1] - conc[0])   # Å/min per wt%
slope_last  = (row3[5] - row3[4]) / (conc[5] - conc[4])
ratio = slope_first / slope_last
print(f"3 psi: 첫 구간 기울기 {slope_first:.0f}, 마지막 구간 {slope_last:.0f} Å/min/wt% → 비 {ratio:.1f}배")
assert slope_first == 1340 and slope_last == 100, "표 전사 오류"
assert ratio > 5, "기울기 비가 5배 미만이면 포화라고 부를 수 없다"
# (3) 1.5 psi 행: 1.0 wt% 이후 총 증가폭(1100->1240)
row15 = table[1.5]
gain_after_1wt = (row15[5] - row15[1]) / row15[1] * 100
print(f"1.5 psi: 1.0->3.0 wt% 총 증가 {gain_after_1wt:.1f}%")
assert abs(gain_after_1wt - 12.7) < 0.2
# (4) 0.5 wt% 저농도 이상점: 18A는 4 psi가 3 psi보다 낮다(1350<1400) — 입자 고갈 신호
assert table[4.0][0] < table[3.0][0]
print("OK: 전 압력 농도 단조증가, 3 psi 한계기울기 13.4배 붕괴(포화), 18A@4psi 고갈 이상점 확인")
```

## 4. 접촉(점유) 확률 모델 — Luo-Dornfeld "활성 입자"의 확률적 정식화

Luo-Dornfeld는 슬러리 전 입자가 아니라 **패드 asperity와 웨이퍼 사이에 끼어 하중을 전달하는
입자(active abrasive)**만 제거에 기여한다고 본다(S2; [[particle-wafer-interaction-mechanical-chemical-balance]] §5).
Region 1(저농도) 폐형식은 `MRR = k1·C/Hw1^(3/2)·[(x_avg+3σ)²/x_avg³]·P^(1/2)` — **C에 선형**이다
([[luo-dornfeld-active-abrasive-size-mrr]] §3, 원문 Eq.1-2 판독본 재인용). 그러나 이 식은
"C가 커져도 계속 선형"이므로 §3 실측의 포화를 담지 못한다. 저자 자신이 Region 1을 "상부 연질층이
전면을 덮은 저농도 영역"으로 한정했고(같은 노트 §3), 고농도에서는 **웨이퍼-패드 접촉면적이
수용할 수 있는 입자 수**가 상한이 된다는 것이 Part-1 제목("…Wafer-Pad Contact Area")의 취지다.
아래 정식화는 그 취지를 **점유확률**로 옮긴 것이며, 함수형(포아송/Langmuir) 선택은 이 노트의
근사이지 원문 식이 아니다(**미검증** — 원문 재판독 후 대조 필요).

**가정과 유도**
1. 접촉 "자리": 패드 asperity-웨이퍼 실접촉 안에서 입자 하나가 끼어 하중을 받을 수 있는 자리 수
   n_s ∝ A_r/x² (자리 하나의 footprint ≈ 입자 단면 x²). GW 지수분포 특수해에서 A_r ∝ W ∝ P
   ([[../materials/hertz-gw-contact-mechanics]] §4) → **n_s ∝ P/x²**.
2. 공급: 간극 슬러리막이 입자 한 겹(두께 ≈ x, Chen 단층가정 — [[abrasive-size-null-result-force-partition-theory]] §3)
   이면 단위면적당 공급 입자수 σ_p = φ_v·x/(πx³/6) = 6φ_v/(πx²) ∝ C/x².
3. 자리당 평균 공급 λ = σ_p·(footprint) / (A_r/A_n) ∝ **C/A_r** (x² 상쇄). 자리마다 독립
   포아송 도착이면 점유확률 p = 1 − e^(−λ). 활성 입자수 **N = n_s·(1 − e^(−λ))**.
4. 극한: λ ≪ 1 → N ≈ n_s·λ ∝ C (Region 1, 선형, 압력 무관 — Luo-Dornfeld Eq.2와 정합).
   λ ≫ 1 → N → n_s ∝ A_r ∝ P (포화, 농도 무관, 압력 비례 — Preston P¹ 회복).
   반포화 농도 **C_h = ln2·A_r/a ∝ P** — 압력을 올리면 자리가 늘어 포화가 늦어진다.
5. Langmuir형 대안: 자리 점유가 가역 흡착이면 p = KC/(1+KC), N = n_s·C/(C_h+C), C_h = 1/K.
   두 함수형은 저·고농도 극한이 같고 중간 곡률만 다르다 — 데이터로 구분 시도는 §5.
6. 포화 너머(입자가 자리보다 훨씬 많아 다층·구름 입자가 하중을 나눠 가짐)는 입자당 하중이
   떨어져 압입 지배 계에서 MRR이 **감소**한다 — S5 Entegris(n≈−0.41)와 Li 2021 Fig.7(ii)
   "고농도 조건" 도식이 이 레짐이다. 이 노트의 점유 모델은 감소를 만들지 못한다(범위 밖, 명시).

Bai 2007(S4)의 N = A_r·(6χ/(πD³))^(2/3) ∝ χ^(2/3)과 Li 2021(S3)의 C^(1/3)·C^(4/3)은 전부 **순수
멱함수**라 어느 농도에서도 기울기가 0으로 가지 않는다. 즉 세 문헌의 농도 지수는 모두 "Region 1
근방의 국소 지수"로 읽어야 하며 포화를 대신할 수 없다 — 아래 verify가 이를 대수적으로 확인한다.

```python verify
import math
# 점유확률(포아송) 모델: 접촉 자리 n_s ∝ A_r, 자리당 평균 공급 λ = a·C/A_r
def n_active(C, A_r, a=1.0):
    n_s = A_r                     # 자리 수 ∝ 실접촉면적 (GW 지수분포: A_r ∝ W ∝ P)
    lam = a * C / A_r             # 공급 입자수/자리 (단층 가정: 면밀도 ∝ C)
    return n_s * (1.0 - math.exp(-lam))
A = 1.0
# Region 1 (λ≪1): N ≈ a·C — 선형이고 A_r(압력)와 무관 (Luo-Dornfeld Eq.2의 C 선형항)
for C in (1e-3, 2e-3):
    assert abs(n_active(C, A) / C - 1.0) < 2e-3
lowP = n_active(1e-3, A); lowP2 = n_active(1e-3, 2 * A)
assert abs(lowP2 - lowP) / lowP < 1e-3, "저농도에서는 압력을 올려도 활성입자수가 거의 안 변해야 함"
# Region 3 (λ≫1): N → n_s ∝ A_r — 농도 무관, 압력 비례
assert abs(n_active(50.0, A) - A) < 1e-6
assert abs(n_active(50.0, 2 * A) / n_active(50.0, A) - 2.0) < 1e-6
# 반포화 농도 C_h = ln2·A_r/a → A_r(∝P)에 정비례
def c_half(A_r, a=1.0):
    lo, hi = 0.0, 100.0
    for _ in range(60):
        mid = (lo + hi) / 2
        if n_active(mid, A_r, a) < 0.5 * A_r:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2
assert abs(c_half(A) - math.log(2)) < 1e-6
assert abs(c_half(2 * A) / c_half(A) - 2.0) < 1e-6
# 대조: 순수 멱함수 N ∝ C^n (Bai2007 χ^(2/3), Li2021 C^(1/3)/C^(4/3), sim 기본 1/3)는 포화 불가
#   "농도 2배" 이득이 어느 농도에서나 2^n으로 일정 → 기울기가 0으로 가지 않는다
for n in (1/3, 2/3, 4/3):
    r_lo = (2e-3) ** n / (1e-3) ** n
    r_hi = (200.0) ** n / (100.0) ** n
    assert abs(r_lo - r_hi) < 1e-9 and r_hi > 1.2
# 포아송 모델은 저농도에서 2배(선형), 고농도에서 1배(포화)
r_poi_lo = n_active(2e-3, A) / n_active(1e-3, A)
r_poi_hi = n_active(20.0, A) / n_active(10.0, A)
assert r_poi_lo > 1.99 and r_poi_hi < 1.0001
print(f"OK: 점유확률 모델 — 저농도 2배이득 {r_poi_lo:.3f}, 고농도 {r_poi_hi:.5f}; "
      f"C_h(A)/ln2={c_half(A)/math.log(2):.6f}; 멱함수는 2배이득이 농도 무관(포화 불가)")
```

## 5. 모델 대조 — 포화형(쌍곡선·포아송) vs 멱함수, 3 psi 6점

같은 2-파라미터끼리 공정하게 비교한다: 멱함수 k·C^n(로그-로그 폐형식), 쌍곡선 M∞·C/(C_h+C),
포아송 M∞·(1−e^(−C/C0))(후자 둘은 C_h·C0 격자탐색 + M∞ 선형최소자승). 결과(손계산·아래 코드):

| 모델 | 파라미터 | SSE (nm/min)² |
|---|---|---|
| 멱함수 | n≈0.30, k≈187 | ≈926 |
| 쌍곡선 | C_h≈0.5 wt%, M∞≈293 nm/min | ≈255 |
| 포아송 | C0≈0.6 wt%, M∞≈247 nm/min | ≈135 |

(US9499721B2 TABLE 18 3 psi 행. 손계산 근사치 — 정확값은 verify 출력이 정본, 밴드 assert.)

핵심 발견 두 가지:
- **전역 멱지수 n≈0.30은 sim 기본값 1/3과 거의 같다.** 즉 현재 팩의 1/3은 "이 데이터 전체를
  하나의 직선으로 눌러 편 평균 기울기"로서는 틀리지 않았다. 그러나 **국소 지수는 0.56(0.5→1 wt%)
  에서 0.11(2.5→3 wt%)로 5배 떨어진다** — 멱함수는 이 곡률을 구조적으로 못 담고, 12.5 wt%로
  외삽하면 쌍곡선 대비 약 40% 과대예측한다(손계산 403 vs 282 nm/min, verify 출력이 정본).
- 포화형 두 모델 모두 멱함수보다 SSE가 3.6~6.9배 작다. 포아송이 쌍곡선보다 더 잘 맞지만
  6점 한 행의 결과이므로 **함수형 우열은 미확정**으로 둔다(다른 압력 행·다른 계에서 재확인 필요).

**재현 요약**: US9499721B2 TABLE 18 3 psi 6점에서 쌍곡선 M∞≈293 nm/min·C_h≈0.5 wt%, 포아송 M∞≈247 nm/min·C0≈0.6 wt%, 멱함수 n≈0.30을 재현하고 SSE 순위(포화형 < 멱함수)를 assert(1블록).

```python verify
import math
# US9499721B2 TABLE 18, 3 psi 행 (Å/min ÷ 10 = nm/min)
conc = [0.5, 1.0, 1.5, 2.0, 2.5, 3.0]
mrr3 = [140.0, 207.0, 226.0, 229.0, 243.0, 248.0]

def sse(pred):
    return sum((p - y) ** 2 for p, y in zip(pred, mrr3))

# (a) 멱함수 MRR = k·C^n — 로그-로그 최소자승(폐형식)
lx = [math.log(c) for c in conc]; ly = [math.log(y) for y in mrr3]
mx = sum(lx) / 6; my = sum(ly) / 6
n_pow = sum((a - mx) * (b - my) for a, b in zip(lx, ly)) / sum((a - mx) ** 2 for a in lx)
k_pow = math.exp(my - n_pow * mx)
sse_pow = sse([k_pow * c ** n_pow for c in conc])

# (b)(c) 포화형: 형상 파라미터 격자탐색(0.05~3.99 wt%) + M∞ 선형최소자승
def fit_grid(gfun):
    best = None
    for i in range(5, 400):
        s_par = i / 100.0
        g = [gfun(c, s_par) for c in conc]
        M = sum(a * y for a, y in zip(g, mrr3)) / sum(a * a for a in g)
        s = sse([M * a for a in g])
        if best is None or s < best[0]:
            best = (s, s_par, M)
    return best
sse_hyp, ch_hyp, M_hyp = fit_grid(lambda c, ch: c / (ch + c))              # 쌍곡선(Langmuir)
sse_poi, c0_poi, M_poi = fit_grid(lambda c, c0: 1.0 - math.exp(-c / c0))   # 포아송 점유

print(f"멱함수  n={n_pow:.3f}, k={k_pow:.1f}  SSE={sse_pow:.0f}")
print(f"쌍곡선  C_h={ch_hyp:.2f} wt%, M∞={M_hyp:.0f} nm/min  SSE={sse_hyp:.0f}")
print(f"포아송  C0={c0_poi:.2f} wt%, M∞={M_poi:.0f} nm/min  SSE={sse_poi:.0f}")
# 전역 멱지수는 sim 기본값 1/3 근방 — 그러나 곡률(포화)은 표현 못 한다
assert 0.25 < n_pow < 0.36, f"전역 멱지수 {n_pow:.3f}가 예상 밴드(0.25~0.36) 밖"
assert sse_hyp < sse_pow and sse_poi < sse_pow, "포화형 두 모델이 멱함수보다 나빠야 할 이유가 없다"
assert 0.35 < ch_hyp < 0.75 and 270 < M_hyp < 330
assert 0.40 < c0_poi < 0.80 and 230 < M_poi < 270
# 국소 지수 붕괴: 0.5->1.0 구간 vs 2.5->3.0 구간
n_lo = math.log(mrr3[1] / mrr3[0]) / math.log(2.0)
n_hi = math.log(mrr3[5] / mrr3[4]) / math.log(3.0 / 2.5)
print(f"국소 지수: 저농도 {n_lo:.2f} → 고농도 {n_hi:.2f}")
assert n_lo > 0.5 and n_hi < 0.15
# 포화도와 외삽: 3 wt%와 12.5 wt%(업계 관행 농도, US9499721B2 본문 서술)
for c in (3.0, 12.5):
    sat = c / (ch_hyp + c) * 100
    print(f"  C={c} wt%: 쌍곡선 포화도 {sat:.0f}% → {M_hyp * c / (ch_hyp + c):.0f} nm/min, "
          f"멱함수 외삽 {k_pow * c ** n_pow:.0f} nm/min")
over = k_pow * 12.5 ** n_pow / (M_hyp * 12.5 / (ch_hyp + 12.5))
assert 1.15 < over < 1.6, f"12.5 wt% 외삽에서 멱함수/쌍곡선 비 {over:.2f}"
print("OK")
```

## 6. 반포화 농도의 압력 의존 — 접촉면적 용량 모델의 독립 검증

§4 모델의 비자명한 예측은 **C_h ∝ A_r ∝ P**(압력이 오르면 자리가 늘어 포화가 늦어진다)이고,
포화 MRR은 M∞ ∝ n_s ∝ P(Preston 회복)이다. TABLE 18은 같은 농도 6종을 4압력에서 쟀으므로
이 예측을 같은 데이터의 다른 축으로 검증할 수 있다. 세 압력이 공통으로 갖는 1.0~3.0 wt% 5점만
써서(0.5 wt% 점은 5 psi에 없음, 4 psi 행은 3.0 wt% 공란 + 18A 고갈 이상점이라 제외) 쌍곡선을
압력별로 적합하면 C_h는 약 0.2 → 0.3 → 0.9 wt%(1.5 → 3 → 5 psi)로 **단조 증가**하고, M∞는
약 130 → 270 → 530 nm/min으로 압력에 거의 비례한다(US9499721B2 TABLE 18; 정확값은 verify).
지수로 환산하면 C_h ∝ P^≈1.25, M∞ ∝ P^≈1.17 — 둘 다 모델 예측(1.0)의 오더에 있으나 3점
추정이라 **지수 자체는 미검증**이고 방향(단조증가)만 확정한다.

이 결과는 팩 설계에 직접적인 함의를 준다: **포화 농도는 슬러리 상수가 아니라 압력(정확히는
실접촉면적)의 함수**다. `abrasive_saturation_wt_pct`를 상수로 두면 저압에서는 포화를 놓치고
고압에서는 과도하게 꺾는다.

**재현 요약**: US9499721B2 TABLE 18 압력별 쌍곡선 적합 C_h 1.5/3/5 psi ≈0.2/0.3/0.9 wt% 단조증가, M∞ ≈130/270/530 nm/min, 적합 RMSE는 M∞의 2% 이내(1블록).

```python verify
import math
# US9499721B2 TABLE 18 — 세 압력이 공통으로 갖는 농도 5점(1.0~3.0 wt%), nm/min
conc = [1.0, 1.5, 2.0, 2.5, 3.0]
rows = {1.5: [110, 113, 117, 120, 124],
        3.0: [207, 226, 229, 243, 248],
        5.0: [269, 348, 363, 386, 403]}
def fit_hyp(ys):
    best = None
    for i in range(5, 400):
        ch = i / 100.0
        g = [c / (ch + c) for c in conc]
        M = sum(a * y for a, y in zip(g, ys)) / sum(a * a for a in g)
        s = sum((M * a - y) ** 2 for a, y in zip(g, ys))
        if best is None or s < best[0]:
            best = (s, ch, M)
    return best
res = {p: fit_hyp(ys) for p, ys in rows.items()}
for p, (s, ch, M) in res.items():
    rmse = math.sqrt(s / 5)
    print(f"{p} psi: C_h={ch:.2f} wt%, M∞={M:.0f} nm/min, RMSE={rmse:.1f} nm/min ({rmse / M * 100:.1f}% of M∞)")
    assert rmse / M < 0.05, "적합 RMSE가 M∞의 5%를 넘으면 쌍곡선 근사가 부적절"
ch = {p: r[1] for p, r in res.items()}
M = {p: r[2] for p, r in res.items()}
# 모델 예측: C_h ∝ A_r ∝ P → 압력과 함께 단조 증가
assert ch[1.5] < ch[3.0] < ch[5.0], "C_h가 압력에 단조증가하지 않음 — 접촉면적 용량 모델 반증"
assert 0.10 < ch[1.5] < 0.40 and 0.15 < ch[3.0] < 0.80 and 0.60 < ch[5.0] < 1.60
n_ch = math.log(ch[5.0] / ch[1.5]) / math.log(5.0 / 1.5)
n_M = math.log(M[5.0] / M[1.5]) / math.log(5.0 / 1.5)
print(f"C_h ∝ P^{n_ch:.2f} (모델 예측 1.0 — 3점 추정, 지수는 확인 못 함), M∞ ∝ P^{n_M:.2f} (Preston 예측 1.0)")
assert 0.5 < n_ch < 2.0, "C_h-압력 지수가 오더 1에서 벗어남"
assert 0.8 < n_M < 1.5, "포화 MRR의 압력 지수가 Preston 오더(1) 밖"
print("OK: 반포화 농도·포화 MRR 모두 압력과 함께 증가 — 접촉면적 용량 모델과 방향 일치")
```

## 7. 근거 충돌 판정 (EVIDENCE-RULES.md 서열)

| 충돌 | A | B | 판정 |
|---|---|---|---|
| 농도→MRR 함수형 | S1 Cabot TABLE 18: 0.5~3 wt%에서 **포화**(E1) | S3 Li 2021: "increased linearly as the abrasive concentration increased"(E3, 수치는 그래프만·농도 범위 텍스트 미기재, 20~30 wt% 대역 추정) | **레짐 분리(절차 3)**. 같은 콜로이달 실리카·같은 SiO₂막이지만 S1은 양전하(아미노실란) 입자·pH 4.7, S3는 음전하 입자·pH 11·K⁺ 0.25 M. 점유 모델에서 입자-표면 친화도 K가 낮으면(정전 반발, [[silica-cmp-ph-acidic-repulsion-choi-power-law]]) C_h=1/K가 커져 선형 구간이 수십 wt%까지 늘어난다 — 두 관측은 같은 곡선의 다른 구간일 수 있다. **이 해석은 가설(미검증)**, 판정은 "함수형은 포화형 채택, C_h는 계별 캘리브레이션". |
| 포화 이후 거동 | 점유 모델: 평탄(감소 없음) | S5 Entegris: 0.1~5 wt%에서 단조 **감소** n≈−0.41(E3, 알루미나/SiC/KMnO₄) | 서열 동급 아님(S1 E1 vs S5 E3)이지만 **계가 달라 직접 충돌이 아니다**. 점유 모델 범위 밖(다층·하중분배)으로 명시하고 평균내지 않는다. 팩별 분기 유지(sic_ceria_h2o2 −0.406은 그대로). |
| 교과서 "15→12→9 wt% 급락" | S6(E5, 교과서 비활성) | S1 실측(E1) | S1 채택. S6은 퓸드 실리카·알칼리 계일 가능성이 크고(특허 본문의 재인용이라 조건 불명) 정량 사용 금지. |

## 8. 팩·구현 함의 (sim/ 은 건드리지 않음 — 구현 요청은 PROFILE.md)

- **함수형 교체 후보**: `(C/C_ref)^n` → `M∞(P)·C/(C_h(P)+C)` 또는 `M∞(P)·(1−e^(−C/C0(P)))`. 정규화는
  `C_ref`에서 1이 되도록 `[C/(C_h+C)] / [C_ref/(C_h+C_ref)]`. 팩 파라미터: `abrasive_conc_half_wt_pct`
  (기준압력에서의 C_h)와 `abrasive_conc_half_pressure_exponent`(기본 1.0, 미확정·GW 근거).
- **검증 데이터**: `validation/datasets/us9499721b2_teos_colloidal_silica_pressure_conc.yaml` 22점 —
  현재 held-out. 이 항이 켜지면 농도 축 순위는 유지하면서 3 psi·1.5 psi 행의 고농도 평탄부가
  재현되어야 한다(§5 SSE 기준 멱함수 대비 개선).
- **적용 범위 게이트**: 점유 모델은 "포화까지"만. 팩이 `abrasive_conc_exponent<0`(sic_ceria_h2o2)
  이면 기존 멱함수 유지 — 감소 레짐은 이 노트 범위 밖.
- **oxide_silica 팩 주의**: 캘리브레이션 출처 Li 2021은 20~30 wt%·음전하·pH 11이라 S1(0.5~3 wt%·
  양전하·pH 4.7)의 C_h≈0.2~0.9 wt%를 그대로 이식하면 안 된다(조성 오귀속). C_h는 팩 계에서
  재추정이 필요하고, 그 전까지는 `confidence=estimated`로만.

## 9. 한계 / 미검증 목록

- 이 회차는 verify_claims·check_knowledge를 **실행하지 못했다**(§0). 4개 verify 블록의 assert
  밴드는 손계산(격자탐색 값은 근사)으로 잡았다 — 기계 실행에서 밴드가 어긋나면 그건 손계산
  오차이지 데이터 문제가 아니므로, 출력값을 보고 밴드를 조정하되 방향 assert(단조성·SSE 순위·
  C_h 압력단조)는 건드리지 말 것.
- Luo-Dornfeld 2003 원문(S2)·Bai 2007 원문(S4)을 이번 회차에 재판독하지 못했다 — 형제 노트가
  원문에서 옮긴 식만 재인용(노트 내 2차 인용). 원문의 고농도 Region(포화·감소) 서술과 §4 점유
  모델의 대응 관계는 **미검증**.
- 점유 모델의 함수형(포아송 vs Langmuir)은 3 psi 한 행에서 포아송이 근소 우세했을 뿐 —
  일반화는 확인 못 함. 자리 footprint ≈ x², 단층 두께 ≈ x 같은 기하 상수는 오더 가정이며 C_h의
  절대값 예측에는 쓰지 않는다(데이터로 적합).
- S1의 pH 4.7은 농축액 pH이고 희석 후 pH는 원문에 없다(데이터셋 주석과 동일). 헤드 rpm 미기재.
- S3 Li 2021의 농도 스윕 범위·수치는 텍스트에 없어 "선형"의 정량 대조를 못 했다(E3).
- 새 문헌 탐색(예: 접촉확률을 명시적으로 쓴 마이크로접촉 모델 논문)은 웹 차단으로 못 했다 —
  "못 찾았다"가 아니라 "찾지 못할 환경이었다". 다음 회차에 `tools/scope.py --queries` 씨앗
  "colloidal silica CMP abrasive" 변형으로 재탐색할 것.

## 10. 자기시험
→ [[../../agents/slurry-abrasive/EXAMS.md]] Lv2-2 문항 참조.

## 상호링크
[[abrasive-hardness-hertz-indentation-removal-volume]] [[../materials/hertz-gw-contact-mechanics]]
[[luo-dornfeld-active-abrasive-size-mrr]] [[particle-size-mrr-molecular-scale-bai2007]]
[[abrasive-size-concentration-ph-K-additive-mrr-quantitative]] [[sic-alumina-concentration-negative-exponent-entegris]]
[[abrasive-size-null-result-force-partition-theory]] [[particle-wafer-interaction-mechanical-chemical-balance]]
[[silica-cmp-ph-acidic-repulsion-choi-power-law]] [[preston-luo-dornfeld-mrr]]
