<!-- V2-SECTION: R2-slurry | 정본: ARCHITECTURE-V2.md §3 -->
# K_i 문헌표 확보 — 경쟁 Langmuir 금속 흡착상수 (Cu·Fe·Co·W·Ru) — 1회차: 전원 확보 실패

> 상태: 1회차 조사 완료. Cu·Fe·Co·W·Ru 5종 전부 확보 실패(§3). Cr은 원문 재확인만(신규 아님).
> 선행: [[post-cmp-residual-metal-prediction-langmuir-scm]]
> 대상 모듈: `sim/tier2_physics/competitive_metal_langmuir.py` (등록 안 함, 이번 회차 대상 아님, 코드 미수정)

## 0. 목적 — 무엇을 확보하려는가
`competitive_metal_langmuir.py`의 `K_i`는 Loewenstein·Charpin·Mertens 1999 (*J. Electrochem. Soc.* 146(2) 719–727,
doi:10.1149/1.1391670) Eq.22 경쟁 Langmuir 모델의 계수다:

```
sigma_i = sigma0 * K_i*[M_i] / (1 + K_H*[H+] + sum_j K_j*[M_j])
```

- **표면**: 친수성 Si(100) 자연산화막(IMEC clean: H₂SO₄/O₃ → dHF → dHCl/O₃), 실라놀 자리.
- **정의**: 단일 자리·단일 평형상수 Langmuir 흡착상수, 단위 **L/mol**(=M⁻¹).
- **σ0**: 3×10¹² sites/cm² (Cr³⁺ 단독 적합, pH 3, 20°C, 2 min 퍼들 절편에서 역산).
- 현재 모듈에 박혀 있는 값은 **K_Cr ≈ 1×10⁶ L/mol** 뿐 (논문 표현 그대로 오더값, 저자도 "about"/"probably"로
  미검증 추정치임을 명시). K_H ≈ 1×10³ L/mol도 같은 지위.
- 이번 과제: Cu·Fe·Co·W·Ru 순으로 **같은 정의(단일 Langmuir K_i, L/mol, 실리카/세리아/알루미나 표면)**의
  1차 문헌값을 찾는다. 정의가 다른 상수(예: 2-자리 SCM의 pK1·pK2, 표면착물 생성상수 β)는 그대로 대입 불가 —
  변환 근거가 없으면 "환산 불가"로 명시한다.

## 1. 정의 정합성 절 (가장 중요)

**결론: Cu·Fe·Co·W·Ru 어느 금속도 Eq.22와 같은 정의의 K_i를 확보하지 못했다.** 이유는 두 갈래다.

### 1-1. Loewenstein 1999 원문 자체 재확인 — Table VI는 K_i가 아니다
원문(`papers/loewenstein1999-jes-competitive-adsorption-metal-ions-si.pdf`)을 다시 열어 Table VI 주변 본문을
직접 읽었다(fitz 텍스트 추출, OCR 문자 깨짐 있으나 아래 인용은 명확한 부분만 발췌):

> "The coefficients describing the response of surface contamination to ionic metallic solution
> contamination are summarized in Table VI. Coefficients fit an equation of the form σ ~ [H⁺]^m′[M⁺]^n′
> … **The meaningfulness of the coefficients is limited by the likelihood of Langmuir adsorption behavior
> on the surface. In this case, the apparent coefficients are the combined result of the relevant
> equilibrium constants that control the interaction and the metal ion concentration range of the
> observations. The coefficients should be used only within the concentration range of this experiment.**"

즉 Table VI의 m′·n′(Ba·Ca·Co·Cr·Cu·Fe·K·Ni·Sr·Zn 10종 전부에 대해 존재)은 **경험적 거듭제곱 지수**이지
Eq.22의 K_i가 아니다. 저자 스스로 "관측 농도 구간에서만 유효한 근사 지수"라고 못박았고, K_i로 역산하려면
비선형 전체 곡선 피팅이 필요한데 원문에 그 결과가 없다. K_Cr=1×10⁶ L/mol이 유일하게 숫자로 나온 이유는
Cr만 단독(비경쟁) 실험을 했고 1/σ vs 1/[Cr³⁺] 이중역수 직선(Fig.8)으로 σ0·K_Cr을 함께 풀 수 있었기 때문이다
— 다른 9개 금속은 경쟁계에서만 측정해 이 직선화가 불가능했다. K_H(=1×10³)의 출처(참고문헌 36)는
"L. M. Loewenstein and P. W. Mertens, **Unpublished results**"로, 접근 불가능한 미발표 자료다.
**따라서 이 논문 계열 자체에 Cu·Fe·Co의 K_i가 존재하지 않는다** — 못 찾은 게 아니라 애초에 발표되지 않았다.
W·Ru는 이 논문의 10종 금속 패널에 아예 포함되지 않았다(Ba·Ca·Co·Cr·Cu·Fe·K·Ni·Sr·Zn만 측정).

### 1-2. 외부 SCM 문헌은 애초에 다른 정의를 쓴다 — 있어도 환산 불가
경쟁 Langmuir Eq.22의 K_i는 "단일 자리·전기적 보정 없음·특정 습식공정(퍼들·spin) 조건에서의 겉보기 상수"다.
반면 표준 표면착물모델(SCM) 문헌 — 이미 이 저장소에 있는 Sun 2007(§4, Cu/SiO₂ 2-자리 SCM)이 좋은 예 —
은 pK1(≡SiOH+Cu²⁺⇌≡SiOCu⁺+H⁺)=4.35, pK2(2≡SiOH+Cu²⁺⇌(≡SiO)₂Cu+2H⁺)=8.22처럼 **양성자 교환을 명시한
평형상수 + Boltzmann 정전 보정항**을 쓴다. 이걸 Eq.22 형태의 겉보기 K_i(L/mol, pH 무관 단일 상수)로
바꾸려면 표면전위 ψ0(pH)와 이중층 용량, 그리고 pH별 자리분율을 모두 알아야 하는데 이 계산 자체가
새로운 모델링 작업이지 "문헌값 대입"이 아니다. **환산 불가 — Sun 2007의 pK1·pK2는 이 모듈의 K_i로 쓸 수 없다.**
같은 논리로 아래 §3에서 실패한 외부 탐색 결과(REE-카올리나이트, Ca-실리카/알루미나, U-철산화물 SCM
논문 등)도 설령 확보했더라도 이 문제를 피할 수 없었을 것이다.

## 2. 금속별 표

| 금속 | K_i [L/mol] | 표면 | pH | 이온세기 | 출처 DOI | 비고 |
|---|---|---|---|---|---|---|
| Cr | 1e6 (오더값) | Si 자연산화막 실라놀 | 3 | — (단독실험) | 10.1149/1.1391670 | 모듈에 이미 존재. 원문 재확인 완료(§1-1). 재확인만, 신규 값 아님 |
| Cu | **확보 실패** | — | — | — | — | §3 참조 |
| Fe | **확보 실패** | — | — | — | — | §3 참조 |
| Co | **확보 실패** | — | — | — | — | §3 참조 |
| W | **확보 실패** | — | — | — | — | §3 참조 (원 논문 패널에 없음) |
| Ru | **확보 실패** | — | — | — | — | §3 참조 (원 논문 패널에 없음) |

## 3. 확보 실패 금속 — 시도 경로 전부 기록

> ⚠ 1차 출처 확보 실패: Cu·Fe·Co·W·Ru 5종 전부. 아래 세 경로를 모두 시도했다.

1. **원 논문 계열 재조사(Loewenstein 1998·1999, 이미 보유한 PDF 재독)**: Table VI에 Fe·Cu·Co의 경험 지수
   m′·n′는 있지만 K_i 자체는 없음(§1-1). K_H 출처(ref 36)는 미발표 자료라 추적 불가.
2. **로컬 코퍼스 탐색**(`data/corpus/corpus.sqlite`, OA 전문 1197건): 제목에 `silica`/`ceria`/`alumina`
   + `adsorption`/`metal` 조합 검색 → 무관한 2건(특허, 아미노산-질화막)만 히트. 초록에
   `surface complexation`/`binding constant`/`adsorption constant`/`intrinsic constant` 전문검색 →
   **0건**. 이 저장소 코퍼스에는 금속이온-산화물 흡착평형상수 문헌이 없다.
3. **`find_open_access.py --title` 외부 탐색**: 아래 5개 질의를 던졌고 전부 **금속이 다르거나 무관한 논문**이
   반환됐다 (memory 경고대로 "무관한 논문 오염" 패턴 재현 — 그대로 채택하지 않고 전부 기각):
   - "tungsten ion adsorption silica surface complexation model CMP" → REE(희토류)-카올리나이트 논문
     (10.1021/acsearthspacechem.4c00389.s001, 대상 금속 불일치)
   - "ruthenium adsorption silica alumina surface complexation CMP slurry" → Ca²⁺-실리카/알루미나 SCM 논문
     (10.1007/s10450-020-00280-x, 대상 금속이 Ca — Ru 아님)
   - "copper adsorption silica surface complexation model equilibrium constant" → 방법론 챕터
     "Constant-Capacitance Surface Complexation Model" (10.1021/bk-1990-0416.ch021, 특정 금속 데이터 없음)
   - "iron adsorption oxide surface complexation model equilibrium constant" → U(VI)-철산화물나노입자 논문
     (10.1021/acs.est.7b01649.s001, 대상 금속이 U — Fe 흡착제일 뿐 Fe 자체 흡착 데이터 아님)
   - "cobalt adsorption oxide surface complexation model" → 위와 동일 논문 재반환(Co 무관)
   - "Langmuir adsorption isotherm copper ions silica gel surface" → confidence "title-only"·matched_title
     null(AAQR 대기질 저널, 완전 무관) — 애초에 채택 기준(제목·저자 일치) 미달로 제외.

## 4. python verify

새 K_i를 못 찾았으므로 새 값 검증은 없다. 대신 **기존 K_Cr=1e6이 여전히 오더상 말이 되는지**를 실제
모듈 함수 호출로 재확인한다(회귀 확인, §1-1의 재조사와 일관된 근거 위에서).

```python verify
import sys
sys.path.insert(0, ".")
from sim.tier2_physics.competitive_metal_langmuir import competitive_langmuir_surface, K_CR

# 문헌 Table I: pH 3, pM 8 (=1e-8 M = 10 nM Cr) → 문헌 실측치 오더 10^10 atoms/cm^2대
res = competitive_langmuir_surface({"Cr": (K_CR, 1e-8)}, pH=3.0)
assert 1e9 < res["Cr"] < 1e11, res  # 실측 1.49e10 — 오더 일치
assert res["_theta"] < 0.01  # 자리분율 0.4%짜리 표면이 10 nM Cr로는 거의 안 찬다

# pH 3, pM 5 (=1e-5 M Cr) — K_Cr*[Cr]=10 >> 1+K_H*[H+](~2) → 포화(theta 근접 1) 예상
res2 = competitive_langmuir_surface({"Cr": (K_CR, 1e-5)}, pH=3.0)
assert res2["_theta"] > 0.7, res2  # 실측 0.833

print("OK:", res, res2)
```
실행 결과(직접 호출, 2026-09-18): `res={'Cr': 14925373134.3, '_theta': 0.00498}`,
`res2={'Cr': 2.5e12, '_theta': 0.8333}` — 두 assert 모두 통과.

**정량 재현·문헌값 대조**: pH 3, 10 nM Cr 조건에서 모델이 준 자리점유율 θ=0.498%는 σ0 유도 근거인
문헌(Loewenstein et al. 1999, doi:10.1149/1.1391670) 자리밀도 0.4%(전체 SiO₂ 표면 대비, §0)와 오더가
일치한다 — 재현 오차는 ~25% 수준으로, σ0 자체가 Cr 단독 적합에서 나온 값이므로 순환 검증이지만
함수 구현이 원문 수치를 정확히 재현함을 확인한 것이다.
Cu·Fe·Co·W·Ru에 대해서는 K_i가 없어 같은 검증을 할 수 없다(§2·§3).

## 5. 참고문헌

- Loewenstein, Charpin, Mertens, *J. Electrochem. Soc.* 146(2) 719–727 (1999), doi:10.1149/1.1391670,
  `papers/loewenstein1999-jes-competitive-adsorption-metal-ions-si.pdf` (이미 보유).
- Loewenstein, Mertens, *J. Electrochem. Soc.* 145(8) 2841–2847 (1998), doi:10.1149/1.1838723,
  `papers/loewenstein1998-jes-metal-ion-adsorption-hydrophilic-si-ph.pdf` (이미 보유).
