<!-- V2-SECTION: R2-slurry | 근거: psi, inhibitor_strength_k, langmuir, Lee2022, BTA, picolinic acid, identifiability | 정본: EVIDENCE-RULES.md 판정#24 -->
# ψ `inhibitor_strength_k` 두 칸(unverified) 판정 — w_fe_oxidizer 하이진 감사 + cu_h2o2_bta 산성계 스윕 1회차 탐색

> 대상: `knowledge/params/w_fe_oxidizer.yaml::inhibitor_strength_k`(2.117)·`inhibitor_ref_mM`(121.8)·
> `inhibitor_K_L_per_mol`(1108.0), `knowledge/params/cu_h2o2_bta.yaml::inhibitor_strength_k`(3.0)·
> `inhibitor_ref_mM`(1.0). `sim/factors.py::_f_psi`, `sim/chemistry.py::_inhibitor_term`.
> [[bta-inhibitor-langmuir-K-effective-cu-cmp-falsification]] (판정 #17, 선행 — cu팩 동형 사례)
> [[w-cmp-picolinic-acid-inhibitor-langmuir-dissolution-suppression]] (원 팩 도출 노트, §6 한계를
> 이 노트 §A.2에서 실측치로 갱신한다)
> [[../EVIDENCE-RULES]] §판정 기록 #24

## 0. 과제와 배경

`tools/completion.py check` 격자 40/50에서 가장 등급이 낮은 두 칸은 `ψ psi/cu_h2o2_bta`와
`ψ psi/w_fe_oxidizer`(둘 다 `unverified`)다. `_f_psi`가 등급을 `_worst_conf(inhibitor_mM,
_worst_conf(inhibitor_strength_k, inhibitor_ref_mM))`로 매겨(`sim/factors.py:1172-1174`),
두 팩 모두 `inhibitor_strength_k`가 병목이다.

- **과제 A**: w_fe_oxidizer의 `inhibitor_strength_k=2.117`은 Lee & Seo(2022, DOI:10.3390/app12031227)
  의 **대상계 직접 실측**(정지식각 90→11 A/min, 1.5 wt%) 역산값인데 등급이 최하다 — 판정#16(등급
  역전 하이진 결함)과 같은 구조인지, 판정#19(식별불가)형인지, 판정#20(함수형 반증)형인지 데이터로
  가른다.
- **과제 B**: 판정#17이 남긴 과제 — 산성(pH 3~5) H₂O₂+BTA 계에서 BTA 농도를 스윕한 Cu 제거율/정지
  식각 1차 문헌 탐색.

## A. w_fe_oxidizer `inhibitor_strength_k` 감사

### A.1 현재 유도 경로

`inhibitor_K_L_per_mol=1108.0`은 Lee & Seo(2022) Table 1의 Langmuir 상수 b=0.009 L/mg를
MW=123.11 g/mol로 몰단위 환산한 값(R²=0.994, 문헌 자체 피팅)이다. `inhibitor_strength_k=2.117`은
이 K를 고정하고, 1.5 wt% 앵커점(정지식각 90→11 A/min, 8.2배 감소)**하나**로 역산한 값이다
(원 노트 §5). 즉 K는 문헌 회귀상수(E2급), k는 **단일 앵커점 역산**(대상계 직접 실측이지만 1점)이다.

### A.2 새로 확보한 것 — Figure 4b 실측 3점 (원 노트의 "0.5wt% 정량값 없음" 기록을 정정한다)

원 노트 §6은 "0.5 wt%의 정지식각 정량값은 원문에 숫자로 없다(그래프만 제시)"고 적었다. 이번에
mdpi-res.com CDN 경유로 원문 PDF(`papers/lee2022-appsci-picolinic-acid-w-cmp-langmuir.pdf`, CC-BY,
DOI:10.3390/app12031227)를 확보해 확인한 결과, Figure 4b는 래스터(JPEG) 삽입 이미지라 벡터 좌표는
없지만 **막대 색(주황) 픽셀의 최상단 행을 축 눈금(0/140 A/10min 프레임 선)에 매핑**하면 4점을 전부
읽을 수 있다(§A.5 verify 블록에서 재현). 원문 y축 단위는 본문 서술("90 to 11 Å/min")과 달리
**A/10min**이다(그림 축 라벨 직접 확인) — 비율(ψ 배수) 계산에는 무관하다.

| 피콜린산 (wt%) | 정지식각 (A/10min, 픽셀 재추출) | 잔여율 (None 대비) |
|---|---|---|
| None (0)  | ≈89.5 | 1.000 |
| **0.5**   | **≈55.7** | **≈0.622** |
| 1.5       | ≈12.1 | ≈0.135 |
| 5.0       | ≈11.0 | ≈0.123 |

None≈90·1.5wt%≈11~12는 원문 텍스트("90 to 11 Å/min")와 정합한다(§A.5 assert). **0.5 wt%가
≈56 A/10min이라는 것은 원문에 실제로 존재하는 정량값**이며, 원 노트가 "그래프만 있고 숫자는 없다"고
적은 것은 벡터 텍스트 추출(`fitz.get_text()`)로는 래스터 이미지 속 수치를 못 읽어서 생긴 누락이었다
— 픽셀 판독으로 해소된다.

### A.3 핵심 결과 — k가 아니라 함수형 전체가 반증된다 (판정#17보다 강한 형태)

현행 경로(K=1108 고정, 1.5wt% 앵커로 k 역산 → k≈2.02~2.12)는 0.5wt%에서 잔여율 0.14 안팎을
예측하는데 실측은 0.622다 — **약 78% 과소예측**(모델이 실제보다 훨씬 강하게 억제된다고 예측).

판정#17(BTA)은 "k를 고정하고 K를 바꾸면 두 점을 꽤 정확히 재현한다 → 약한 고리는 K"였다. 여기서는
그 구조를 뒤집어 검사했다: **K를 0으로 보내는 극한(이 Langmuir+exp(−kθ) 함수형이 낼 수 있는 이론적
최선)에서도** Lee & Seo(2022, DOI:10.3390/app12031227) Figure 4b 재추출값 기준 0.5wt% 예측은 0.51로
실측 0.622에 17.5% 못 미친다(§A.5 verify). K를 1108(문헌값)로 올릴수록 격차는 –17.5%→–78%로
**단조 악화**한다. 즉:

- k만 스윕해서는(K=1108 고정) 1.5wt% 앵커를 지키는 한 0.5wt%를 못 맞춘다(k를 낮추면 1.5wt%
  앵커 자체가 깨진다) — **k는 약한 고리가 아니다**(판정#17과 동형 결론).
- **K까지 자유롭게 풀어도**(전 구간 스윕) 이론적 최선(K→0)조차 실측에 17.5% 못 미친다 — 이는
  판정#17의 BTA 사례(K를 낮추면 2점을 거의 정확히 재현)보다 **강한 반증**이다: BTA는 "K가
  틀렸다"로 설명됐지만, W/피콜린산은 "(K, k) 어떤 조합도 안 된다" — **Langmuir(n=1) 등온식과
  단일 지수감쇠 exp(−kθ)의 조합 자체가 이 3점(None/0.5/1.5wt%)을 구조적으로 못 담는다.**

### A.4 판정

**1) 하이진 결함(등급만 잘못 낮음)이 아니다.** 그러려면 "k를 어떤 값으로 바꿔도 안 된다 + K는
문제가 아니다"가 필요한데, 실제로는 K를 포함한 전체 파라미터 공간에서도 실패한다 — 오히려 더 강한
반증이다. `inhibitor_strength_k`를 literature로 승격할 근거가 없다. **unverified 유지.**

**2) 식별불가(판정#19형)도 아니다.** 판정#19는 "관측이 동일 잔차로 여러 (n, C_peak) 해를 허용"하는
축퇴였다. 여기는 반대로 **어떤 (K,k) 조합도 관측을 허용하지 않는다** — 축퇴가 아니라 과결정
반증(overdetermined falsification)이다. 밀도 불확실성(ρ=0.995~1.15)이 θ(0.5wt%)에 주는 영향도
0.978~0.981로 무시 가능해(§A.5) 식별불가의 원인이 아님을 확인했다.

**3) 함수형 반증(판정#20형)에 해당한다 — 단 교체하지 않는다.** 판정#20은 대체 폐형식(Langmuir
부동태 피복 억제항)을 문헌에서 확보해 교체했다. 이번에는 임계피복률 문턱이나 Frumkin 등온식 같은
대체 폐형식을 이 코퍼스에서 확보하지 못했다 — COMPLETION.md가 금지하는 "문헌 근거 없는 항 추가"에
해당하므로 **코드를 바꾸지 않는다.** 한계로만 기록한다(YAML 주석에 반영 완료).

**결론: `inhibitor_strength_k=2.117`은 unverified로 유지한다.** 격자 칸 수는 오르지 않는다(오히려
반증이 더 강해져 승격 여지가 줄었다).

### A.4-2 `inhibitor_ref_mM` / `inhibitor_K_L_per_mol` 부수 감사

과제 지시대로 `inhibitor_ref_mM`의 팩 간 등급 불일치(cu=verified, w_fe=estimated)를 감사했다.
두 노트 모두 "Kp가 이 조성(1.0mM BTA / 1.5wt% 피콜린산)의 문헌 MRR에서 역산됐기 때문에 반드시
일치시켜야 이중계상이 없다"는 근거를 댔다. 그런데 실제 `kp_m_per_pa`의 출처
[[surface-chemistry-cu-w-pourbaix-passivation]]를 확인하면:

- cu_h2o2_bta(같은 노트의 대표값 유도): "문헌 MRR 범위(400~800 nm/min @ 2~3psi)에서
  역산한 대표값" — BTA 농도 무관.
- w_fe_oxidizer([[surface-chemistry-cu-w-pourbaix-passivation]] 동일 노트): "문헌 W MRR 범위
  (300~600 nm/min @ 3psi)에서 역산한 대표값. 미재현." — 피콜린산 농도 무관.

**두 Kp 모두 억제제 특정 조성에서 역산된 값이 아니다** — "조성 일치" 근거 자체가 양쪽 다 성립하지
않는다. 기준점 선택(ref_mM=inhibitor_mM, 이중계상 방지)은 코드로 확인 가능한 항등식이라 여전히
옳지만, "이 특정 숫자가 Kp와 조성이 일치한다"는 근거는 없었다. 등급이 달라야 할 이유가 없으므로
**일치시킨다 — cu_h2o2_bta의 `inhibitor_ref_mM`을 verified→estimated로 하향**(w_fe_oxidizer 쪽을
근거 없이 승격시키는 대신, 근거가 실제로 약한 cu 쪽을 내렸다. YAML 반영 완료). 두 psi 셀 모두
이미 `inhibitor_strength_k=unverified`가 바닥이라 격자에는 영향 없음.

`inhibitor_K_L_per_mol`(1108.0, literature)은 유지한다 — 이 값 자체는 Lee & Seo(2022,
DOI:10.3390/app12031227) Table 1의 **흡착 등온 회귀상수**(TOC 용액-고갈법, 12h 평형)로서 반증되지
않았다. 반증된 것은 "이 K를 exp(−kθ) 잔여율 모델에 대입해 SER(3분 침지)을 예측하는 것"이지 K 값
자체가 아니다 — 등온 실험(같은 논문, 12h 평형)과 SER 실험(같은 논문, 3분 침지) 사이의 **시간축
불일치**(비평형 흡착 동역학) 가설이 실제 원인일 가능성이 있으나(미검증), 원문에 흡착 속도론
데이터가 없어 확인하지 못했다(§A.6 한계).

### A.5 검증 (코드 — Figure 4b 픽셀 재추출 + 파라미터 공간 전수 스윕)

```python verify
import math
import fitz
import numpy as np

# ── (1) Figure 4b 픽셀 재추출 (Lee & Seo 2022, doi:10.3390/app12031227) ──
PDF = "papers/lee2022-appsci-picolinic-acid-w-cmp-langmuir.pdf"
doc = fitz.open(PDF)
page = doc[5]  # 0-index page 5 = 원문 p.6, Figure 4
clip = fitz.Rect(300, 460.8, 492.1, 588.1)  # Figure 4(b) 패널만
mat = fitz.Matrix(10, 10)
pix = page.get_pixmap(clip=clip, matrix=mat)
arr = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, pix.n)
r, g, b = arr[:, :, 0].astype(int), arr[:, :, 1].astype(int), arr[:, :, 2].astype(int)
orange_mask = (r > 200) & (g > 100) & (g < 200) & (b < 100)
black_mask = (r < 60) & (g < 60) & (b < 60)
row_black = black_mask.sum(axis=1)
candidate_rows = np.where(row_black > row_black.max() * 0.9)[0]
row_top = candidate_rows[candidate_rows < pix.height * 0.3].mean()
row_bot = candidate_rows[candidate_rows > pix.height * 0.7].mean()

def to_val(row):
    return 140.0 * (row_bot - row) / (row_bot - row_top)

cols = np.where(orange_mask.any(axis=0))[0]
groups, cur = [], [cols[0]]
for c in cols[1:]:
    if c - cur[-1] <= 5:
        cur.append(c)
    else:
        groups.append(cur)
        cur = [c]
groups.append(cur)
assert len(groups) == 4, f"막대 4개(None/0.5/1.5/5wt%) 기대, {len(groups)}개 검출"

bar_vals = []
for c0, c1 in [(gr[0], gr[-1]) for gr in groups]:
    sub = orange_mask[:, c0:c1 + 1]
    top_row = np.where(sub.any(axis=1))[0].min()
    bar_vals.append(to_val(top_row))
none_v, v05, v15, v5 = bar_vals
print(f"Figure 4b 재추출값 (A/10min): None={none_v:.1f} 0.5wt%={v05:.1f} "
      f"1.5wt%={v15:.1f} 5wt%={v5:.1f}")
assert 85 < none_v < 95, none_v
assert 50 < v05 < 62, v05
assert 9 < v15 < 15, v15
# 원문 텍스트(3절): "dramatically decreased from 90 to 11 A/min" — 재추출값과 정합
assert abs(none_v - 90.0) < 6.0, none_v
assert abs(v15 - 11.0) < 3.5, v15

# ── (2) 잔여율(관측) ──
r05_obs = v05 / none_v
r15_obs = v15 / none_v
print(f"관측 잔여율: r(0.5wt%)={r05_obs:.4f}, r(1.5wt%)={r15_obs:.4f}")
assert 0.55 < r05_obs < 0.70
assert 0.10 < r15_obs < 0.18

# ── (3) Langmuir 피복률 + 1.5wt% 앵커로 k 역산 (팩 현재 경로, K=1108 L/mol 고정) ──
MW = 123.11  # g/mol, picolinic acid (PubChem CID 1018)
K_LIT = 1108.0  # L/mol, Table 1 b=0.009 L/mg * MW * 1000

def wt_to_molar(wt_pct, rho=1.0):
    return wt_pct * 10.0 * rho / MW

def theta(C, K):
    KC = K * C
    return KC / (1.0 + KC)

C05, C15 = wt_to_molar(0.5), wt_to_molar(1.5)
th05_lit, th15_lit = theta(C05, K_LIT), theta(C15, K_LIT)
assert abs(th05_lit - 0.9783) < 0.001
assert abs(th15_lit - 0.9926) < 0.001

k_anchor = -math.log(r15_obs) / th15_lit  # 1.5wt% 점만으로 역산 (팩 현재 값의 유도 경로)
assert abs(k_anchor - 2.117) < 0.15, f"k_anchor={k_anchor:.3f} (팩 값 2.117 기대)"

pred05_lit = math.exp(-k_anchor * th05_lit)
gap_lit_pct = (pred05_lit - r05_obs) / r05_obs * 100
print(f"k={k_anchor:.3f}(K={K_LIT:.0f} 고정) 예측 r(0.5wt%)={pred05_lit:.4f} "
      f"vs 관측 {r05_obs:.4f} -> {gap_lit_pct:.1f}%")
assert gap_lit_pct < -60, "현행 (K,k) 조합이 0.5wt%를 심하게 과잉 억제 예측해야 반증 성립"

# ── (4) k 스윕: K=1108 고정, k를 무엇으로 바꿔도 두 앵커를 동시에 못 맞춘다 ──
print("K=1108 고정, k 스윕:")
for k in (0.1, 0.3, 0.5, 1.0, 1.5, 2.0, k_anchor, 2.5, 3.0, 5.0, 10.0):
    p15 = math.exp(-k * th15_lit)
    p05 = math.exp(-k * th05_lit)
    dev15 = (p15 - r15_obs) / r15_obs * 100
    print(f"  k={k:6.3f} pred15={p15:.4f}(dev {dev15:+6.1f}%) pred05={p05:.4f}")

# ── (5) K까지 자유롭게 풀어도(K->0 극한) 해소되지 않음: 이론적 최선 하한 ──
# K -> 0 극한에서 theta ~ K*C (선형), theta05/theta15 -> C05/C15 = 1/3.
# k를 1.5wt% 앵커에 맞추면(k*theta15 = -ln(r15)), pred05 = r15 ** (C05/C15) 로 수렴한다.
floor_pred05 = r15_obs ** (C05 / C15)
gap_floor_pct = (floor_pred05 - r05_obs) / r05_obs * 100
print(f"K->0 이론적 하한: pred(0.5wt%)={floor_pred05:.4f} vs 관측 {r05_obs:.4f} "
      f"-> {gap_floor_pct:.1f}% (이 함수형이 낼 수 있는 최선의 근사)")
assert abs(C05 / C15 - 1.0 / 3.0) < 1e-9
assert gap_floor_pct < -10, (
    "K->0 이론적 최선의 경우에도 관측을 못 따라가야 '함수형 자체의 한계'가 성립한다")

gaps = []
for K in (0.001, 1, 10, 100, K_LIT, 5000):
    th15_K, th05_K = theta(C15, K), theta(C05, K)
    k_K = -math.log(r15_obs) / th15_K
    p05_K = math.exp(-k_K * th05_K)
    gaps.append((p05_K - r05_obs) / r05_obs * 100)
print(f"K 스윕 격차(%): {[f'{x:.1f}' for x in gaps]} — K가 커질수록(1108 포함) 더 벌어진다")
assert gaps[0] > gaps[-1], "K가 작을수록(0에 가까울수록) 격차가 가장 작아야(최선이어야) 한다"
assert all(gaps[i] >= gaps[i + 1] - 1e-6 for i in range(len(gaps) - 1)), gaps

# ── (6) 밀도 불확실성이 theta(0.5wt%)에 미치는 영향 — 무시 가능 수준 확인 ──
th05_band = [theta(wt_to_molar(0.5, rho), K_LIT)
             for rho in (0.995, 1.000, 1.005, 1.010, 1.05, 1.15)]
assert max(th05_band) - min(th05_band) < 0.01, "밀도밴드가 theta(0.5wt%)를 유의하게 흔들면 안 된다"
print(f"밀도밴드(0.995~1.15) theta(0.5wt%) 범위: {min(th05_band):.4f}~{max(th05_band):.4f} "
      "— 무시 가능(식별불가 원인 아님)")

print("PASS: w_fe_oxidizer inhibitor_strength_k — (K,k) 전체 파라미터 공간에서도 "
      "0.5wt% 실측을 재현 못함(함수형 구조적 한계). 승격 근거 없음, unverified 유지.")
```

### A.6 한계 (정직 표기)

- 픽셀 판독은 래스터(JPEG) 이미지 기반이라 Netzband 2020(벡터 rect) 판독보다 정밀도가 낮다 —
  본문 텍스트 수치(90, 11)와 3~6% 이내로 정합하는 것으로 신뢰도를 대신 확인했다(§A.5 assert).
- 0.5wt% 실측(≈56)이 3회 반복 평균인지 단일값인지 원문 Figure 4 캡션에 명시가 없다(오차막대는
  그림에 있으나 본문에 수치로 재기재되지 않음) — 정밀도는 그림 판독 수준.
- K 등온상수 자체(1108 L/mol, TOC 12h 평형 흡착)와 SER 측정(3분 침지) 사이의 시간축 불일치
  가설(§A.4-2)은 원문에 흡착 속도론 데이터가 없어 검증하지 못했다 — 추정으로만 기록.
- 대체 폐형식(Frumkin 등온식, 임계피복률 문턱)은 이번 회차에 문헌으로 확보하지 못해 코드에
  반영하지 않았다 — 다음 과제로 남긴다.

## B. cu_h2o2_bta 산성계 BTA 농도 스윕 — 1회차 탐색

### B.1 필요 조건과 탐색 경로

필요한 것: 산성(pH 3~5) H₂O₂ 기반 Cu CMP 슬러리에서 BTA 농도만 스윕한 Cu 제거율/정지식각률 실측
(n≥3). 판정#17이 확보한 Len et al. 2000(DOI:10.1557/proc-613-e7.4.1)은 **알칼리(NH₄OH)+알루미나**
계라 부적격이었다(§7, 계 불일치로 미채택).

### B.2 시도한 경로와 결과

**(1) `tools/find_open_access.py --title` 3질의**:
- "benzotriazole concentration copper CMP removal rate hydrogen peroxide acidic" →
  DOI: 10.1021/la7013557.s001 ("Mechanism of Electrochemical Reduction of H2O2 on Cu in Acidic
  Sulfate Solutions") — BTA 없음, 부적격.
- "BTA concentration dependence copper polishing rate static etch rate" →
  DOI: 10.1016/0168-583x(94)95457-7 (Lexan 식각) — 무관.
- "corrosion inhibitor concentration copper CMP slurry pH 4" →
  DOI: 10.1002/9780470180907.ch8 (Cu CMP용 억제제 총론 챕터, 특정 농도 스윕 데이터 아님) — 부적격.

**(2) Crossref bibliographic query 4건**(각 8~10건 검토, 총 34건): 무관 논문(H₂O₂ 농도 모니터링
센서, Cu 제거율-압력/속도 모델링, BTA 제거용 post-CMP 세정액 등) 다수. 유력 후보 5건 발견:

| DOI | 제목 | 판정 |
|---|---|---|
| 10.1557/proc-1157-e06-02 | Fundamental Mechanisms of Copper CMP – Passivation Kinetics of Copper in CMP Slurry Constituents | MRS Proc, Unpaywall `is_oa=False`, 미러 사이트 미러 3종(kr/wf/bban) 전부 봇차단 — **미확보** |
| 10.5006/1.3280782 | Adsorption of Benzotriazole on Copper Electrode Surfaces in Citric Acid Media | 산성(citric acid)! Unpaywall `is_oa=False`, 미러 사이트 동일 사유로 **미확보** |
| 10.1143/jjap.47.108 | Effect of Corrosion Inhibitor, Benzotriazole, in Cu Slurry on Cu Polishing (Kim, Kang, Kim, Park 2008) | 초록: "dynamic etching rate ... decreased when BTA was added to the slurry **at pH 2, 4, and 6**" — **가장 유력한 후보**(산성+BTA+제거율). IOP "bronze" OA로 표시되나 `/pdf` 요청은 구매 안내 페이지 반환, 미러 사이트 미러(se/st/ru/wf/bban) 전부 봇차단(altcha·Cloudflare) — **미확보** |
| 10.1149/1.3499217 | Copper CMP Modeling: Millisecond Scale Adsorption Kinetics of BTA in Glycine-Containing Solutions **at pH 4** | 흡착 속도론(chronoamperometry)이라 제거율 스윕은 아님 — IOP 페이월, **미확보(부차 후보)** |
| 10.1149/2.010310jes | Influence of Copper Ion Concentration on ... Protective Layer on Copper in an Acidic CMP Solution Containing BTA and Glycine | Cu 농도 스윕이지 BTA 농도 스윕이 아님 — IOP 페이월, **미확보(부차 후보)** |

**(3) 로컬 코퍼스 확인**(`grep -il benzotriazole papers/*.txt`, `data/corpus/corpus.sqlite` 32건
조회): `papers/aksu2003-electrochimica-bta-glycine-cu-cmp.pdf.txt`(Ein-Eli/Abelev/Starosvetsky
2004, DOI:10.1016/j.electacta.2003.11.010, 판정#20에 이미 등장한 그 논문) 확인 결과 pH4·Na₂SO₄
전해질에 BTA 0.001~0.1M을 쓰지만 **전기화학 전류밀도**(potentiodynamic/potentiostatic) 측정이지
CMP 제거율/정지식각이 아니고, 도판도 두 농도(0.001M vs 0.01M) 비교뿐이라 n≥3 스윕이 아니다 —
부적격. `data/corpus/corpus.sqlite` documents 테이블에서 title LIKE '%benzotriazole%'+'%copper%'
32건을 전수 확인, 위 표의 5건 외에는 post-CMP 세정(BTA 제거)·XPS/SIMS 메커니즘·pH 구조론 등으로
농도-제거율 정량 스윕은 없었다.

**(4) 미러 사이트 미러**: 미러 사이트/st(연결 실패, exit 000), 미러 사이트(→미러 사이트 리다이렉트,
altcha "로봇 확인" 차단), 미러 사이트(브라우저 체크 페이지), 미러 사이트(Cloudflare "Just a
moment..." 챌린지) — 이번 세션에서 시도한 4개 미러 전부 봇 검증에 막혔다(메모리 기록과 달리
이번 회차엔 통과 미러 없음 — 미러 가용성이 시점마다 바뀐다).

### B.3 판정

**⚠ 1차 출처 확보 실패.** 가장 유력한 후보 10.1143/jjap.47.108(Kim et al. 2008, JJAP)을 특정했다
— 초록이 "산성(pH 2/4/6) BTA 첨가 Cu 슬러리에서 동적 식각률 변화"를 직접 보고해 이 과제에 정확히
들어맞지만, IOP 페이월 + 미러 사이트 미러 전부 차단으로 본문(농도 스윕표 존재 여부, n, 정량값)을
확인하지 못했다. K와 k를 동시 식별할 자료를 확보하지 못했으므로 `cu_h2o2_bta.yaml`의
`inhibitor_strength_k`는 **unverified 그대로 둔다**(값도 불변). 다음 회차는 새 질의를 반복하지
말고 **10.1143/jjap.47.108 본문 확보(IOP 기관구독·저자 요청·ResearchGate)를 1순위**로 시도할 것 —
이번 회차에 이미 최적 후보를 찾았으므로 탐색 단계는 건너뛰어도 된다.

## 결론 요약

| 파라미터 | 이전 | 이후 | 근거 |
|---|---|---|---|
| `w_fe_oxidizer.inhibitor_strength_k` | unverified | **unverified(불변)** | (K,k) 전 공간 반증 — 승격 근거 없음, 오히려 반증이 강해짐 |
| `w_fe_oxidizer.inhibitor_K_L_per_mol` | literature | **literature(불변)** | 흡착 등온상수 자체는 반증 안 됨 — SER 모델 적용만 한계로 기록 |
| `w_fe_oxidizer.inhibitor_ref_mM` | estimated | **estimated(불변)** | cu 쪽을 내려 맞춤(아래) |
| `cu_h2o2_bta.inhibitor_ref_mM` | verified | **estimated(하향)** | "Kp가 이 조성에서 역산됐다"는 근거가 감사 결과 성립하지 않음(양쪽 다 조성 무관 대표값) |
| `cu_h2o2_bta.inhibitor_strength_k` | unverified | **unverified(불변)** | 산성계 BTA 스윕 1차 출처 미확보(§B.3) |

격자 칸 수(`tools/completion.py check`)는 **불변**이 예상된다 — 두 ψ 칸 모두 병목(`inhibitor_
strength_k`)이 그대로 unverified이기 때문이다. 실측 보고는 본문(대화) 쪽에서 실행 결과로 확인한다.

## 자기시험

1. 판정#17(BTA)과 이번 w_fe 감사의 핵심 차이는? → BTA는 "K를 낮추면 2점을 거의 정확히 재현"해
   약한 고리가 K로 특정됐다. w_fe는 K를 0으로 보내는 극한(이론적 최선)에서도 실측에 17.5% 못
   미쳐 **K를 포함한 전체 함수형이 반증**된다 — 더 강한 결론.
2. `inhibitor_strength_k=2.117`이 대상계 직접 실측(1.5wt% 앵커) 역산값인데도 승격하지 않는 이유는?
   → 그 앵커에 정확히 맞추는 k가 같은 논문의 다른 데이터점(0.5wt%)을 78% 어긋나게 예측한다 —
   단일 앵커 역산값이 데이터 전체와 불일치하는 게 확인된 이상 승격할 수 없다.
3. `inhibitor_ref_mM`을 왜 w_fe 쪽이 아니라 cu 쪽을 내려서 맞췄는가? → cu의 "verified" 등급이
   기댄 근거("Kp가 이 조성에서 역산됨")를 Kp의 실제 출처 노트에서 확인한 결과 성립하지 않았다 —
   근거 없이 강한 등급을 준 쪽을 맞추는 게 정직하다(반대로 약한 쪽을 근거 없이 올리는 것보다).
4. 산성계 BTA 스윕을 못 찾았는데 왜 "실패"로 끝내지 않고 특정 DOI를 지목했는가? → 탐색 자체는
   성공(10.1143/jjap.47.108이 정확히 필요조건에 부합하는 초록을 가짐), 접근만 실패했다 — 다음
   회차는 새 질의 없이 이 DOI의 본문 확보 경로만 시도하면 된다(탐색 중복 방지).
