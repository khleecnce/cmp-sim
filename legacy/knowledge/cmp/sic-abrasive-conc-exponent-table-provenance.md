<!-- V2-SECTION: R2-slurry | 판정#37 sic_ceria_h2o2 abrasive_conc_exponent 출처절 재판정(Table1 vs Table9) 2026-09-15 -->
# `abrasive_conc_exponent`(-0.406) 출처 절 재판정 — Table 1(비교예) vs Table 9(발명공정)

> 과제: 판정#36(sic-abrasive-concentration-regime-ruling.md)의 부수 발견 — 현재 팩이 쓰는
> US20220315802A1 Table 1이 특허 원문에서 스스로 "Example 1 (**Comparative**)"라 부른다는
> 점을 확인하고, 같은 특허의 Table 9(발명 공정, S-I1 계열)가 동일 저농도 구간에서 부호가
> 반대(단조 증가)인지, 반대라면 팩이 잘못된 절을 쓰고 있는지 재판정한다.
> 선행: [[sic-alumina-concentration-negative-exponent-entegris]](2026-09-11) [[sic-abrasive-concentration-regime-ruling]](2026-09-15)
> 원문: `papers/US20220315802A1.txt` (HTML 전문 텍스트, fitz 아님). 출원일 2022-03-30
> (원문 메타 `DC.date content="2022-03-30"`), 출원인 Entegris/University of Florida Research
> Foundation.

## 1. 원문에서 뽑은 조건 대조 — Table 1 vs Table 9

### Table 1 (Example 1, Comparative) — [0204]/[0205]

원문: "This example demonstrates the concentration effect of alumina nanoparticles on
single crystal SiC polishing temperature and material removal rates. Polishing
temperature and removal rates were determined for each aqueous suspension containing
4 wt.-% of KMnO4 and 0.5 wt.-% of salts of nitric acid at pH 2.3" ([0204]).

| 항목 | 값 | 출처 |
|---|---|---|
| 연마입자 종류 | "alumina nanoparticles" (구체적 종·Mohs·입경 **미기재**) | [0204] |
| 농도 범위 | 0.1 / 0.2 / 0.5 / 1 / 5 wt% (n=5) | Table 1 본문 |
| MRR (μm/hr) | 5.8 / 5.2 / 4.5 / 3.1 / 1.2 (단조감소) | Table 1 본문 |
| pH | 2.3 (고정) | [0204] |
| 산화제 | KMnO4 4wt% + "salts of nitric acid" 0.5wt% (염 종류 **미특정**) | [0204] |
| 압력·속도·패드·툴 | **미기재** (Example 1-3 구간 전체에 압력/rpm/패드 언급 없음, grep 확인) | — |
| 기판 | "single crystal SiC" (4H/6H 미특정, 일반 서술[0193]에서만 "some embodiments"로 4H 언급) | [0204] |
| 서술 | "The increase in abrasive concentration shows decrease in temperature and at the same
  time it also decreases the silicon carbide removal rates." | [0205] |

### Table 9 (S-I1/S-C1~C9, 배치형 CMP) — [0243]/[0245], 조성은 Table 7([0235])

원문 조성표(Table 7, [0235] "The final composition of all prepared Examples... is given
in Table 7"): KMnO4 4.0wt%(전 계열 공통), 알루미늄나이트레이트 0.50wt%(전 계열 공통),
알루미나입자(각주1: "**boehmite particles with a Z-average particle size of 100 nm**
(supplied by Sasol Performance Chemicals)"), 준비법 Method A(발명법, [0226]-[0230],
"alumina particles having a **Mohs hardness of 3 to 4**"[0227]) 전 계열 공통(S-C5만 예외
Method B). pH(23°C, 조제 직후) 3.6~4.8이나 "Prior to polishing, the pH of each
composition was reduced to **2.1** with nitric acid"([0237]).

| 항목 | 값(S-I1→S-C3, 0.1~1.0wt% 구간) | 출처 |
|---|---|---|
| 연마입자 종류 | boehmite(γ-AlOOH), Z-avg **100nm**, Mohs **3~4** (명시) | Table 7 각주1, [0227] |
| 농도·MRR (μm/hr) | 0.1→3 / 0.2→3.8 / 0.5→4.2 / 1.0→4.8 (**단조증가**) / 5.0→n.d.(불안정) | Table 9 본문 |
| pH | 조제직후 3.6~4.8 → 연마직전 2.1로 조정(전 계열 공통) | Table 7, [0237] |
| 산화제 | KMnO4 4.0wt% + 알루미늄나이트레이트 0.50wt% (염 종류 명시) | Table 7 |
| 압력·속도·패드·툴 | 배치형 CMP 툴, 웨이퍼 16장, 압력 수치는 **이 표에 없음**(별도 Table 10은 S-I1 단일농도의
  단일형 CMP 압력스윕 405~972 psi·in/sec — 농도스윕과 무관한 별개 실험) | [0237], Table 10 |
| 기판 | "4H-type round wafer, diameter 150 mm" (명시) | [0237] |
| 서술 | "Comparative aqueous suspensions S-C1 to S-C3 containing a higher amount of alumina
  particles than inventive aqueous suspension S-I1 result in **higher** material removal
  rates. However, the increase ... is associated with an undesirable significant increase
  in surface roughness" | [0245]/[0257] |
| 특기 | [0066]: 발명의 핵심 주장 자체가 "**less than 0.2 wt.-%**의 연마입자"가 낮은 표면조도의
  "surprising" 이점을 준다는 것 — 즉 Table 9의 S-I1은 **저농도 특화 지점**이고, S-C1~C3는
  "더 높지만 여전히 낮은"(0.2~1.0wt%) 비교점. 5wt%(S-C4)는 제조 단계에서 불안정(n.d.) |

### 두 표 모두 로그-로그 회귀로 지수 재현 — 문헌값과 대조

```python verify
import numpy as np

# Table 1 (Example 1, Comparative, [0204]) — 원문 수치 그대로
c1 = np.array([0.1, 0.2, 0.5, 1.0, 5.0])       # wt%
m1 = np.array([5.8, 5.2, 4.5, 3.1, 1.2])        # um/hr, [0204] Table 1 본문

# Table 9 (S-I1, S-C1, S-C2, S-C3, [0243]) — 5.0wt%(S-C4)는 n.d.(불안정)라 제외
c9 = np.array([0.1, 0.2, 0.5, 1.0])             # wt%
m9 = np.array([3.0, 3.8, 4.2, 4.8])             # um/hr, Table 9 본문

def loglog_slope(c, m):
    A = np.vstack([np.log(c), np.ones_like(c)]).T
    n, _ = np.linalg.lstsq(A, np.log(m), rcond=None)[0]
    return n

n1 = loglog_slope(c1, m1)
n9 = loglog_slope(c9, m9)
print(f"Table1 지수 n1 = {n1:.3f} (문헌값 대조: 기존 -0.406과 일치해야 함)")
print(f"Table9 지수 n9 = {n9:.3f} (부호 반대 확인)")

assert abs(n1 - (-0.406)) < 0.01, f"Table1 재현 실패: {n1:.3f} vs -0.406"
assert n9 > 0, f"Table9는 단조증가라 양수여야 하는데 {n9:.3f}"
assert 0.15 < n9 < 0.25, f"Table9 지수가 예상 범위(0.15~0.25) 밖: {n9:.3f}"

# 팩의 실사용점(c_ref=4.0wt%)이 각 표의 관측 범위 안에 있는지 대조 — 외삽 여부 확인
c_ref = 4.0
in_range_table1 = c1.min() <= c_ref <= c1.max()
in_range_table9 = c9.min() <= c_ref <= c9.max()
print(f"c_ref=4.0wt%가 Table1 범위[{c1.min()},{c1.max()}] 안? {in_range_table1}")
print(f"c_ref=4.0wt%가 Table9 유효범위[{c9.min()},{c9.max()}] 안? {in_range_table9}")
assert in_range_table1 and not in_range_table9, (
    "판정 근거(범위 포함 여부)가 원문 수치와 어긋난다")
print("OK: Table1은 c_ref=4.0wt%를 내삽 범위에 포함, Table9는 4배 외삽 필요")
```

재현 결과 문헌값과 대조: Table1 회귀 지수 -0.406(0.1wt%→5.0wt% 구간 MRR이 5.8um/hr에서
1.2um/hr로 감소), Table9 회귀 지수 +0.191(0.1wt%→1.0wt% 구간 MRR이 3.0um/hr에서
4.8um/hr로 증가)로 §1 코드블록 출력과 원문 수치가 일치함을 확인했다.

## 2. 팩(sic_ceria_h2o2.yaml) 조건과의 대조

| 축 | 팩(sic_ceria_h2o2) | Table 1 | Table 9(S-I1계열) |
|---|---|---|---|
| pH | **10.0**(알칼리, Wang DOE 9/10/11) | 2.3(산성) | 2.1(연마직전, 산성) |
| 산화제 | H2O2 2/4/6 **vol%** | KMnO4 4wt%+질산염0.5wt% | KMnO4 4wt%+Al나이트레이트0.5wt% |
| 연마입자 | **세리아**(CeO2) | 알루미나(종 미특정) | 보헤마이트(γ-AlOOH, Mohs3-4, 100nm) |
| **농도 스윕 범위** | 2 / 4 / 6 wt% (DOE, **ref=4.0wt%**) | **0.1~5.0 wt%** (n=5, 4wt%를 포함하는 구간) | **0.1~1.0 wt%**만 유효 (5.0은 n.d.), **4wt% 근방 데이터 전무** |
| 기판 | 4H-SiC | SiC(폴리타입 미특정, 일반서술상 4H 추정) | 4H-SiC(명시) |
| 압력/속도 | Wang DOE 절대값 있음 | 미기재 | 미기재(농도스윕 구간) |

**pH·산화제·연마입자 화학은 Table 1·Table 9 어느 쪽도 팩(알칼리·H2O2·세리아)과 맞지 않는다 —
두 표 모두 산성·KMnO4·알루미나계로 동일하게 멀다.** 이 축에서는 두 표가 **동등하게** 계가
다르므로(§배경 지시의 "물어야 할 것" 1번 항목상 우열 없음), 판정은 화학이 아니라 **농도
스윕 범위가 팩의 실제 사용점(c_ref=4.0wt%)을 포함하는가**로 갈린다 — 이것도 원문에 적힌
숫자(스윕 범위)를 그대로 비교하는 것이지 ρ가 아니다.

- Table 1의 스윕(0.1~5.0wt%)은 팩의 c_ref=4.0wt%를 **내삽 구간 안에 포함**한다(4.0은
  1.0과 5.0 사이).
- Table 9의 유효 스윕(0.1~1.0wt%, 5.0wt%는 n.d.로 제외)은 팩의 c_ref=4.0wt%보다
  **훨씬 낮은 구간에서 끝난다** — 4.0wt%는 Table 9 데이터 범위의 **4배 밖**, 완전
  외삽이다. 더구나 [0066]이 명시하듯 Table 9의 S-I1~S-C3 구간(<1.0wt%)은 발명 자체가
  "**극저농도**에서 표면조도 이득"을 주장하는 특수 구간이라서, 1.0wt%를 넘는 영역(팩이
  실제로 쓰는 2~6wt%)에서 이 단조증가 추세가 계속된다는 보장이 원문에 전혀 없다
  (오히려 Table 1은 같은 화학·재질(알루미나) 계에서 1→5wt% 구간이 **여전히 단조감소**임을
  보여준다 — 즉 저농도(<1wt%)의 증가 추세와 고농도(1~5wt%)의 감소 추세가 **같은 특허,
  같은 화학계 안에서도 공존**할 수 있다는 반증).

## 3. 판정: **(b) Table 1 유지 확정**

**근거 (ρ 무관, 조건 일치로만 판단):**
1. 팩의 실제 사용점(`abrasive_ref_wt_pct=4.0wt%`, Wang DOE 2~6wt%)은 Table 1의 관측
   구간(0.1~5.0wt%) 안에 있고, Table 9의 유효 관측 구간(0.1~1.0wt%)에는 없다 — Table 9로
   지수를 다시 뽑아도 그 지수를 4wt%에 적용하는 순간 **4배 외삽**이 되어 버린다.
2. 특허 자신도 Table 9의 단조증가 구간(<1.0wt%, 특히 <0.2wt%)을 "발명의 핵심 저농도
   특이점"으로 서술한다([0066]) — 이는 일반적인 농도-MRR 관계가 아니라 **좁은 농도창에서만
   성립하는 국소 현상**이라는 저자 자신의 주장이다. 반대로 Table 1은 5wt%까지 폭넓게
   스윕한 **일반 구간** 데이터다.
3. "Comparative"라는 라벨은 Table 1이 **준비법(Method A/B 구분 이전의 예비 스크리닝)과
   조성 세부사항(연마입자 Mohs·입경 미기재)이 후속 발명 공정만큼 통제되지 않았다"는
   뜻이지, 데이터 자체가 물리적으로 틀렸다는 뜻이 아니다 — 넓은 농도범위에서의 MRR 감소
   경향은 재질 축(백강옥 Mohs9 vs 보헤마이트 Mohs<6)을 가른 판정#36과 달리, 같은 특허
   본문([0043]/[0063])이 정의하는 "Mohs<6 알루미나" 계열 안에서 관측된 것으로 보인다
   (Example 1이 별도 재질을 썼다는 원문 서술 없음).
4. 두 표를 평균내지 않았고, ρ 방향을 보지 않았다 — 오직 **농도 스윕 범위가 팩의 c_ref를
   포함하는가**만으로 판단했다.

**남는 한계(솔직히 기록):** Table 1도 Mohs·입경이 미기재라 Table 9만큼 재질이 확실하지
않다. 또한 Table 9의 반전(<1wt% 구간 단조증가)이 왜 일어나는지 — Method A(발명적 첨가
순서)의 화학적 효과인지, 순수 저농도 극한의 다른 메커니즘인지 — 는 이 노트로 규명하지
못했다. 이는 **팩이 쓰는 4wt%대 구간에서는 무관한 질문**이므로 더 파고들지 않는다.

## 4. 결론 — 파라미터 변경 없음

`sic_ceria_h2o2.yaml`의 `abrasive_conc_exponent: -0.406` (source: US20220315802A1 Table 1,
n=5 로그-로그 회귀)는 **그대로 유지**한다. confidence(`literature`)도 변경하지 않는다
(근거가 더 강해진 것이 아니라, 대안(Table 9)을 검토했으나 팩의 사용 구간에 부적합함을
확인했을 뿐이므로 승격 사유 없음).

## 상호링크
[[sic-alumina-concentration-negative-exponent-entegris]] [[sic-abrasive-concentration-regime-ruling]]
