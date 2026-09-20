<!-- V2-SECTION: R2-slurry | 근거: psi, inhibitor_strength_k, Frumkin, Langmuir, Temkin, Sips, 임계피복률, identifiability | 정본: EVIDENCE-RULES.md 판정#24 -->
# ψ 억제항 대체 폐형식 문헌조사 — Frumkin 등온식·임계피복률 문턱

> 대상: `sim/chemistry.py::_inhibitor_term`, `sim/factors.py::_f_psi`,
> `knowledge/params/w_fe_oxidizer.yaml::inhibitor_strength_k`,
> `knowledge/params/cu_h2o2_bta.yaml::inhibitor_strength_k`.
> [[psi-inhibitor-strength-k-grade-ruling]] (판정 #24 — 현행 Langmuir+exp(−kθ)가 W/피콜린산
> 0.5·1.5wt% 앵커를 (K,k) 전 공간에서도 재현 불가함을 증명. Fig.4b 픽셀재추출 4점 데이터 원천)
> [[bta-inhibitor-langmuir-K-effective-cu-cmp-falsification]] (판정 #17 — Cu/BTA 0.5·0.75wt%
> 플래토를 같은 구조가 재현 못 함. Len2000 4점 데이터 원천)
> [[inhibitor-chelator-adsorption-isotherm-passivation]] (§3.2 — Frumkin이 BTA-Cu에 실험적으로
> 더 잘 맞는다는 부식 문헌 인용, CMP 계는 아니었음. 이 노트가 그 갭을 좁힌다)
> [[../EVIDENCE-RULES]] §판정 기록 #24 후속

## 0. 과제와 결론 요약

판정#24·#17이 확인한 것: 현행 함수형 `θ=KC/(1+KC)`(Langmuir n=1) + 잔여율=exp(−kθ)는 파라미터를
어떻게 잡아도 "저농도 완만·고농도 급감 후 플래토"라는 관측 패턴을 구조적으로 못 담는다. 이 노트는
데이터 재피팅이 아니라 **문헌이 지지하는 대체 폐형식**을 찾고, 찾은 후보를 판정#24·#17의 앵커로
직접 검사한다.

**결론(먼저 밝힌다): Frumkin 등온식(θ/(1−θ)·exp(−2fθ)=KC, 협동흡착 파라미터 f)으로 교체하면
두 앵커 모두 극적으로 개선되고(§6), f≈2.0(임계 협동성 부근)에서 식별성도 뾰족하다(§5) — 그러나
**코드는 이번 회차에 교체하지 않는다.** 이유(§7): (a) CMP 계에서 Frumkin+BTA를 직접 쓴 유일한
논문(Krishnan et al. 2024, IBM)의 원문을 이번 세션 내 모든 경로로 확보하지 못해 그들의 f 값과
우리가 역산한 f≈2.0~2.2가 같은 근거로 나온 것인지 대조 불가, (b) 피콜린산-W 계에는 Frumkin
적용 선례 자체가 문헌에 없다(BTA-Cu 계에서만 선례 확인) — 즉 수학적 재현은 강력하지만 "이 f 값이
왜 물리적으로 맞는가"의 문헌 근거가 계별로 고르지 않다. 다음 회차 최우선 과제를 §7에 명시한다.

## 1. 후보 함수형 목록

| 후보 | 수식 | 자유도(vs 현행) | 상태 |
|---|---|---|---|
| **① Frumkin** | `θ/(1−θ)·exp(−2fθ)=KC`, 잔여율=exp(−kθ) | +1(f) | **§2·5·6 — 강력히 지지, 코드는 보류** |
| **② 임계피복률 문턱(percolation)** | θ<θ_c: 잔여율≈1, θ>θ_c: 급감(예: 시그모이드/스텝) | +1~2(θ_c, 급경사) | **§3 — 직접 CMP 문헌 미확보. §2에서 Frumkin(f>2)이 이 문턱을 수학적으로 내재함을 보임(같은 메커니즘일 가능성)** |
| ③ Temkin | `θ=(RT/a)·ln(K·C)` | +1(a), 로그형이라 θ→0/1 경계 미정의 | §4 — CMP 문헌 미확보, 저농도 발산 문제로 후순위 |
| ④ Sips/Langmuir–Freundlich | `θ=(KC)ⁿ/(1+(KC)ⁿ)` | +1(n) | §4 — CMP 문헌 미확보, 판정#19가 이미 이 구조(n,C_peak)의 축퇴를 경고 |

## 2. Frumkin 등온식 — CMP 적용 사례

### 2.1 직접 CMP 문헌(같은 계: Cu + BTA) — 원문 미확보, 초록만

**Krishnan, M., Canaperi, D.F., Rangarajan, S.K. (2024).** "Molecular Interactions in Copper
Chemical Mechanical Planarization: A Phenomenological Study." *ECS J. Solid State Sci. Technol.*
13, 074001. DOI: 10.1149/2162-8777/ad5fe4. 저자 소속: IBM Research(당시). CC-BY(hybrid OA로
등록되어 있으나 원문 접근은 실패 — 아래 §8).

초록(OpenAlex·Semantic Scholar API로 확인, 독립 2경로 일치):

> "the molecular interactions occurring during Chemical Mechanical planarization of Copper in
> Ferric nitrate–Alumina–Benzotriazole system is investigated. This system is characterized by
> **sudden and dramatic transitions in removal rates** when experimental parameters such as
> downforce and concentrations of the slurry components (Benzotriazole, abrasive, oxidizer) are
> varied. ... A phenomenological model incorporating **Frumkin isotherm for the adsorption of
> Benzotriazole molecules** and Langmuir isotherm for the adsorption of surfactants/ions is
> proposed. ... The non-linear equations describing the sudden transitions are shown to exhibit a
> **cusp catastrophe** when the interaction parameter exceeds a certain value."

이 초록은 판정#17·#24가 재현 못 한 정확히 그 현상("sudden and dramatic transitions", 완만한
저농도 구간 뒤 급변)을 BTA-Cu 계에서 Frumkin 등온식 + 상호작용 파라미터로 설명한다. **원 계
(Cu+BTA, CMP)와 완전히 일치**하므로 확보됐다면 E1/E2급 근거가 됐을 것이다.

**⚠ 원문 미확보.** 시도한 경로(모두 실패, 2026-09-15):
- IOPscience 직접(`/article/.../pdf`): Radware Bot Manager 캡차(HTTP 200, HTML 캡차 페이지).
- 미러 사이트 미러 6종(se/st/ru/wf/box/red/cat): se·st는 연결 실패(exit 000), ru·wf·box는 altcha
  "로봇 확인" 챌린지, red는 502, cat은 501 — **전부 봇 검증 실패**(2024년 출판이라 애초에
  미러 색인 여부도 불확실).
- CORE API v3 검색(저자명+제목 키워드): 0건(관련 없는 論文만).
- IBM Research 공식 퍼블리케이션 페이지(`research.ibm.com/publications/molecular-interactions
  -in-copper-chemical-mechanical-planarization-a-phenomenological-study`, 메타데이터로 실존
  확인됨) — DOI 외부링크만 있고 **PDF 자체 호스팅은 없음**.
- Unpaywall/OpenAlex `best_oa_location`: `pdf_url=None`(리포지토리 사본 없음, hybrid OA는
  출판사 자체 페이지에서만 무료라는 뜻인데 그 페이지가 봇차단).

**결론: 이 논문의 존재·계·방법론(Frumkin+cusp catastrophe)은 2개 독립 API(OpenAlex,
Semantic Scholar)로 교차 확인했지만, 구체적 수식·f 값·검증 데이터는 확인 못 했다 — E5(2차
정보, 원문 미확보)로만 인용한다.** §5·6의 f≈2.0~2.2 역산은 **이 논문과 무관하게 이 노트가
독자적으로** 판정#17·#24의 원 데이터에서 재도출한 값이다 — "논문이 이 값을 썼다"고 주장하지
않는다.

### 2.2 계 전이 문헌(다른 계: Cu + BTA, 부식 전기화학) — 원문 확보·검증됨

[[inhibitor-chelator-adsorption-isotherm-passivation]] §3.2가 이미 인용한
**Antonijevic & Petrovic (2008)**, "Copper Corrosion Inhibitors. A Review," *Int. J.
Electrochem. Sci.* 3, 1–28. DOI: 10.1016/s1452-3981(23)15441-1 (오픈액세스, 전문 확보
`papers/antonijevic2008-ijes-copper-corrosion-inhibitors-review.pdf`, 이 세션에서 원문
"Frumkin" 키워드 재확인, §2.4 verify). 이 리뷰는 여러 Cu 부식억제제(FA/FB 계면활성제,
DTUr 등 우라실 유도체)에 **Frumkin 등온식이 Langmuir보다 잘 맞는다**는 원논문들을 정리한다
— 그러나 **CMP가 아니라 부식(염수 침지) 전기화학 셀**이고, 리뷰가 다루는 개별 분자(FA/FB,
DTUr)는 BTA·피콜린산이 아니다. **판정: E4(계 전이) — 같은 금속(Cu)의 흡착 거동에 Frumkin이
일반적으로 적용되는 선례는 있으나, BTA 자체의 f 값이나 CMP 조건으로의 이전은 이 리뷰만으로는
정당화되지 않는다.**

### 2.3 Frumkin 등온식의 수학적 성질 — 임계 협동성과 "급변"의 연결(자체 유도, 코드 검증)

Frumkin 등온식 `KC = θ/(1−θ)·exp(−2fθ)`는 흡착분자 간 측면 상호작용을 f로 담는다(f>0=협동/
인력). **f>2(2f>4)에서 C(θ)가 비단조가 되어(dC/dθ가 구간에서 음수) θ가 좁은 농도 구간에서
"뛰어오르는"(jump/catastrophe) 거동**을 보인다 — 이는 Frumkin 등온식 자체의 수학적 성질로
(Bragg-Williams 평균장 격자기체 모델과 동형, 임계점 f=2) 특정 논문을 인용할 필요 없이 §5
verify에서 직접 재현했다. 이것이 §2.1 초록의 "cusp catastrophe" 서술과 정성적으로 일치하는
독립 확인이다 — **단, 이 절은 계산상의 사실 확인이지 "그러므로 BTA-CMP의 f가 실제로 2 이상"
이라는 물리적 주장은 아니다.** 그 주장은 §5·6의 데이터 재현에서 별도로 검사한다.

이 성질은 후보②(임계피복률 문턱)와 후보①(Frumkin)이 **서로 다른 함수형이 아니라 같은 현상의
매끄러운 버전/이산 버전일 수 있음**을 시사한다 — f>2인 Frumkin은 사실상 연속적인 "문턱"이다.

### 2.4 원문 텍스트 확인(코드) — §2.2 Antonijevic 2008, §3.1 Dai 2024

```python verify
import fitz

# ── Antonijevic & Petrovic 2008 — "Frumkin"이 실제로 본문에 등장하는가 ──
doc = fitz.open("papers/antonijevic2008-ijes-copper-corrosion-inhibitors-review.pdf")
text = "".join(p.get_text() for p in doc)
assert text.lower().count("frumkin") >= 2, "Frumkin 언급이 본문에 최소 2회 이상 있어야 한다"
assert "DTUr" in text or "dithiouracil" in text.lower(), "Frumkin으로 맞는 억제제(DTUr) 서술 확인"
print(f"Antonijevic 2008: 'Frumkin' {text.lower().count('frumkin')}회 등장 — 원문 확인.")

# ── Dai et al. 2024 — Table 2 (Rp, eta_E) 수치가 본문에 그대로 있는가 ──
doc2 = fitz.open("papers/dai2024-researchsquare-triazole-threshold-cu-cmp.pdf")
text2 = "".join(p.get_text() for p in doc2)
assert "15 mM TAZ provides the best corrosion" in text2 or "15 mM TAZ" in text2
assert "85.34" in text2, "15mM 억제효율 85.34%가 본문 표에 있어야 한다"
assert "81.57" in text2, "20mM 억제효율 81.57%가 본문 표에 있어야 한다"
assert "agglomeration" in text2, "응집(agglomeration)에 의한 막 붕괴 서술 확인"
print("Dai 2024: Table 2 수치(85.34%, 81.57%) + agglomeration 서술 본문 확인 완료.")
```

## 3. 임계 피복률 문턱 모델 — 직접 CMP 문헌

### 3.1 확보한 것 — TAZ/Cu 알칼리 CMP 슬러리 문턱 효과(비단조형, 판정#24가 필요로 하는 형태와 다름)

**Dai, L., Yan, Z., Zhang, D., Li, C., Shi, C., Gao, L., Xin, Z. (2024).** "Corrosion inhibition
threshold effect of 1,2,4-triazole in alkaline chemical mechanical polishing of copper:
Investigations using synchrotron radiation microinfrared." *Research Square* preprint (CC-BY,
2024-10-04). DOI: 10.21203/rs.3.rs-5011272/v1. 전문 확보
`papers/dai2024-researchsquare-triazole-threshold-cu-cmp.pdf`(Research Square landing page →
`assets-eu.researchsquare.com` 직접 PDF, green OA).

계: 알칼리 Cu CMP 슬러리(2wt% 글리신+0.5wt% H₂O₂, pH 9, KOH/HNO₃ 조정) + 1,2,4-트리아졸(TAZ,
BTA와 같은 아졸 계열이나 벤젠 고리가 없는 5원환) 0/5/10/15/20 mM, 3전극 전기화학 셀(EIS)로
분극저항 Rp 측정 → 억제효율 ηE(%) 산출(§2.4 verify로 원문 표 재추출):

| TAZ (mM) | Rp (Ω·cm²) | ηE (%) |
|---|---|---|
| 0(blank) | 51.45 | — |
| 5  | 180.84 | 71.55 |
| 10 | 279.40 | 81.58 |
| **15** | **350.90** | **85.34**(최댓값) |
| 20 | (Rp 표에서 산출) | 81.57 |

원문 결론: "15 mM TAZ provides the best corrosion inhibition ... The integrity of the surface
film decreases significantly at concentrations above the threshold level. This is mainly due to
the **agglomeration of Cu-TAZ complexes**."

**⚠ 이 문턱은 판정#24가 필요로 하는 형태와 메커니즘이 다르다.** 판정#24·#17이 재현하려는 패턴은
**단조** 형태다 — 저농도에서 억제 미미, 고농도에서 억제가 강해진 뒤 그 수준에서 **유지**(포화,
더 나빠지지도 좋아지지도 않음). Dai 2024의 문턱은 **비단조**다 — 15mM까지 억제효율이 오르다가
20mM에서 오히려 소폭 하락한다(85.34%→81.57%, Cu-TAZ 착물 응집으로 막 무결성이 깨짐). 이것은
"과잉 억제제가 오히려 보호막을 약화시키는" **최적농도형** 문턱이지, "일정 농도 이상은 전부
똑같이 강하게 막는다"는 **포화형** 문턱이 아니다 — 함수형으로 옮기면 전자는 위로 볼록한 피크
(∩)이고 후자는 계단/시그모이드(⌐)다. 이 논문은 **"CMP 인접 계(전기화학 모사 셀)에서 아졸계
억제제에 진짜 문턱현상이 존재한다"는 것을 확인**해 주지만, **그 문턱의 함수형을 그대로 판정#24
앵커 재현에 쓸 수는 없다**(§7 한계로 기록).

**등급**: 계 근접도는 높다(Cu, 알칬리 CMP 슬러리 조성 그대로, 아졸계 억제제, 전기화학 정량
실측) 하지만 실험이 CMP 폴리싱 자체가 아니라 **슬러리 조성을 모사한 정지 전기화학 셀**이라
기계적 벗김이 없다 — **E2**(대상계에 근접한 직접 실측이나, 정상상태 CMP가 아닌 평형 전기화학).

### 3.2 미확보

포화형(단조) 임계피복률/percolation 문턱을 CMP 억제제 폴리싱 실측(제거율 vs 농도)으로 직접
보고한 논문은 이번 회차에 찾지 못했다. Crossref 질의("critical coverage threshold inhibitor
adsorption chemical mechanical polishing" 등 3건, 각 10건 검토) 결과 Dai 2024가 유일한 "threshold"
직접 매치였다. §2.3의 Frumkin(f>2) 수학적 문턱이 현재로서는 가장 유력한 대체 경로다.

## 4. Temkin / Langmuir–Freundlich(Sips) — 미확보, 후순위 사유

Crossref 질의("Temkin isotherm inhibitor CMP copper tungsten", "Sips isotherm Langmuir-Freundlich
inhibitor CMP") 각 10건 검토 — CMP 억제제에 적용한 사례 0건(흡착 일반 문헌만 다수, 폐수처리·
염료흡착 등 무관 계). 두 후보 모두 자유도가 +1(Temkin의 a, Sips의 n)인데, **판정#19가 이미
같은 구조(오옥사이드 항의 (n, C_peak))에서 축퇴를 경고**했다 — CMP 문헌 근거 없이 자유도만
늘리는 것은 과제 규칙(§자유 파라미터가 늘어나는 함수형은 식별성 검사를 통과해야만 후보) 위반
소지가 커 이번 회차에는 식별성 검사조차 하지 않았다(대체할 CMP 문헌이 없어 물리적 근거 부재가
먼저 걸림). 다음 회차에 Temkin/Sips CMP 적용 사례가 확보되면 판정#19·#20 방식으로 재검사한다.

## 5. 식별성 검사(Frumkin, 코드)

3점(W/피콜린산: None/0.5/1.5/5.0wt%, 자유도 3개 K,k,f — 정확히 결정됨)과 4점(Cu/BTA:
0.1/0.25/0.5/0.75wt%, 자유도 3개 — 과결정)에서 **f를 그리드로 고정하고 (K,k)만 최소자승으로
풀어 SSE(f)의 형태를 본다.** 판정#19(축퇴, 리지형)·#20(뾰족한 단일최소)과 같은 방식.

```python verify
import math
import numpy as np
from scipy.optimize import brentq, least_squares

MW_PIC, MW_BTA = 123.11, 119.12

def wt_to_mM(wt, MW, rho=1.0):
    return wt / 100.0 * rho * 1000.0 / MW * 1000.0

def theta_frumkin(C_list, K, f):
    """Frumkin theta(C): K*C = theta/(1-theta)*exp(-2f*theta), continuation from theta~0."""
    thetas, th_guess = [], 1e-6
    for C in C_list:
        KC = K * C
        def g(th):
            return th / (1 - th) * math.exp(-2 * f * th) - KC
        ths = np.linspace(1e-9, 1 - 1e-9, 4000)
        vals = ths / (1 - ths) * np.exp(-2 * f * ths) - KC
        roots = [brentq(g, ths[i], ths[i + 1])
                 for i in range(len(ths) - 1) if vals[i] * vals[i + 1] < 0]
        th = th_guess if not roots else min(roots, key=lambda r: abs(r - th_guess))
        thetas.append(th)
        th_guess = th
    return np.array(thetas)

def model_ratios(wts, K, k, f, MW):
    Cs = [wt_to_mM(w, MW) * 1e-3 for w in wts]
    return np.exp(-k * theta_frumkin(Cs, K, f))

# ── (1) f=2 임계 협동성에서 C(theta)가 비단조가 됨을 직접 확인 (수학적 성질, §2.3) ──
f_test = 3.0
th = np.linspace(1e-4, 1 - 1e-4, 4000)
C_over_K = th / (1 - th) * np.exp(-2 * f_test * th)
assert np.any(np.diff(C_over_K) < 0), "f=3에서 C(theta) 비단조(jump) 구간이 있어야 한다"
f_sub = 1.5
C_over_K_sub = th / (1 - th) * np.exp(-2 * f_sub * th)
assert np.all(np.diff(C_over_K_sub) > 0), "f=1.5(<2)에서는 C(theta)가 단조여야 한다(임계점 f=2)"

# ── (2) W/피콜린산 3점(판정#24 Fig.4b 재추출값) — f를 스윕, (K,k) 최소자승 ──
wts_pic = [0.5, 1.5, 5.0]
r_obs_pic = np.array([0.6223, 0.1352, 0.1229])  # 55.7/89.5, 12.1/89.5, 11.0/89.5

def best_sse_given_f(f, wts, r_obs, MW):
    def resid(x):
        K, k = x
        if K <= 0 or k <= 0:
            return np.full(len(wts), 1e3)
        return model_ratios(wts, K, k, f, MW) - r_obs
    best = None
    for K0 in (0.01, 0.1, 1, 10, 100, 1000):
        for k0 in (0.5, 1, 2, 5, 10):
            sol = least_squares(resid, x0=[K0, k0], bounds=([1e-9, 1e-9], [1e9, 200]))
            sse = float(np.sum(sol.fun ** 2))
            if best is None or sse < best[0]:
                best = (sse, sol.x)
    return best

sse_f0, _ = best_sse_given_f(0.0, wts_pic, r_obs_pic, MW_PIC)
sse_f20, x_f20 = best_sse_given_f(2.0, wts_pic, r_obs_pic, MW_PIC)
sse_f25, _ = best_sse_given_f(2.5, wts_pic, r_obs_pic, MW_PIC)
print(f"W/피콜린산 SSE: f=0(Langmuir)={sse_f0:.4f}  f=2.0={sse_f20:.2e}  f=2.5={sse_f25:.2e}")
assert sse_f0 > 1e-2, "f=0(Langmuir)은 3점을 못 맞춰야 판정#24와 정합"
assert sse_f20 < 1e-6, "f=2.0 근처에서 사실상 정확히 재현돼야 한다"
assert sse_f0 / sse_f20 > 1e4, "f=0->f=2.0 개선이 4자릿수 이상이어야 '뾰족한' 최소로 볼 수 있다"
assert sse_f25 > sse_f20 * 10, "f=2.0에서 벗어나면(f=2.5) SSE가 다시 빠르게 악화돼야 축퇴가 아니다"

# ── (3) 무작위 재시작으로 (K,k,f) 유일해 확인 (식별성) ──
def resid3(params):
    K, k, f = params
    if K <= 0 or k <= 0:
        return np.full(3, 1e3)
    return model_ratios(wts_pic, K, k, f, MW_PIC) - r_obs_pic

rng = np.random.default_rng(0)
sols = []
for _ in range(40):
    K0, k0, f0 = 10 ** rng.uniform(-3, 4), 10 ** rng.uniform(-1, 1.7), rng.uniform(-3, 6)
    sol = least_squares(resid3, x0=[K0, k0, f0],
                         bounds=([1e-8, 1e-8, -10], [1e8, 100, 15]), xtol=1e-14, ftol=1e-14)
    if np.sum(sol.fun ** 2) < 1e-8:
        sols.append(tuple(np.round(sol.x, 2)))
uniq = set(sols)
print(f"무작위 재시작 40회 중 수렴 {len(sols)}건, 서로 다른 해 {len(uniq)}개: {uniq}")
assert len(sols) >= 20, "재시작의 절반 이상은 수렴해야 그리드가 유효하다"
assert len(uniq) == 1, "수렴한 해가 전부 같은 (K,k,f)여야 식별 가능(축퇴 아님)"

print("PASS: Frumkin은 f≈2 근방에서 뾰족한 단일 최소를 가진다 — 판정#19형 축퇴가 아니다.")
```

## 6. 앵커 재현 검사(Frumkin vs 현행 Langmuir, 코드)

```python verify
import math
import numpy as np
from scipy.optimize import brentq, fsolve, least_squares

MW_PIC, MW_BTA = 123.11, 119.12

def wt_to_mM(wt, MW, rho=1.0):
    return wt / 100.0 * rho * 1000.0 / MW * 1000.0

def theta_frumkin(C_list, K, f):
    thetas, th_guess = [], 1e-6
    for C in C_list:
        KC = K * C
        def g(th):
            return th / (1 - th) * math.exp(-2 * f * th) - KC
        ths = np.linspace(1e-9, 1 - 1e-9, 4000)
        vals = ths / (1 - ths) * np.exp(-2 * f * ths) - KC
        roots = [brentq(g, ths[i], ths[i + 1])
                 for i in range(len(ths) - 1) if vals[i] * vals[i + 1] < 0]
        th = th_guess if not roots else min(roots, key=lambda r: abs(r - th_guess))
        thetas.append(th)
        th_guess = th
    return np.array(thetas)

def model_ratios(wts, K, k, f, MW):
    Cs = [wt_to_mM(w, MW) * 1e-3 for w in wts]
    return np.exp(-k * theta_frumkin(Cs, K, f))

# ── (A) 판정#24 앵커: W/피콜린산 0.5·1.5wt% (+5.0wt% 교차점) ──
wts_pic = [0.5, 1.5, 5.0]
r_obs_pic = np.array([0.6223, 0.1352, 0.1229])

def resid_pic(params):
    K, k, f = params
    if K <= 0 or k <= 0:
        return np.full(3, 1e3)
    return model_ratios(wts_pic, K, k, f, MW_PIC) - r_obs_pic

sol = least_squares(resid_pic, x0=[3.0, 2.0, 2.0],
                     bounds=([1e-8, 1e-8, -5], [1e6, 50, 10]), xtol=1e-14, ftol=1e-14)
K_pic, k_pic, f_pic = sol.x
pred_pic = model_ratios(wts_pic, K_pic, k_pic, f_pic, MW_PIC)
print(f"W/피콜린산 Frumkin 재현: K={K_pic:.3f} k={k_pic:.3f} f={f_pic:.3f} "
      f"pred={np.round(pred_pic,4)} obs={r_obs_pic}")
assert np.allclose(pred_pic, r_obs_pic, atol=0.002), "3점 모두 0.2%p 이내로 재현돼야 한다"
assert 1.8 < f_pic < 2.3, f"f={f_pic:.3f} — 임계 협동성(f=2) 부근이어야 '판정#24가 필요로 한' 급변이 나온다"

# 판정#24가 이미 증명한 Langmuir(K->0 극한 이론적 최선)의 하한과 대조
r15_obs, r05_obs = r_obs_pic[1], r_obs_pic[0]
C05, C15 = wt_to_mM(0.5, MW_PIC), wt_to_mM(1.5, MW_PIC)
floor_pred05 = r15_obs ** (C05 / C15)  # 판정#24 §A.5 (5)와 동일 유도
gap_floor_pct = (floor_pred05 - r05_obs) / r05_obs * 100
print(f"Langmuir 이론적 최선(K->0): pred(0.5wt%)={floor_pred05:.4f} vs 관측 {r05_obs:.4f} "
      f"-> {gap_floor_pct:.1f}% (판정#24가 이미 확립한 하한)")
assert gap_floor_pct < -15, "Langmuir 최선의 경우도 15%p 이상 못 미쳐야 판정#24와 정합"

# ── (B) 판정#17 앵커: Cu/BTA 0.1/0.25/0.5/0.75wt% 플래토(Len2000) ──
wts_bta = [0.1, 0.25, 0.5, 0.75]
r_obs_bta = np.array([65.0, 42.0, 42.0, 42.0]) / 400.0

# B1: 전 4점 자유 피팅(자기 계에서 (K,k,f) 재추정) — 최선의 경우
def resid_bta(params):
    K, k, f = params
    if K <= 0 or k <= 0:
        return np.full(4, 1e3)
    return model_ratios(wts_bta, K, k, f, MW_BTA) - r_obs_bta

best = None
rng = np.random.default_rng(2)
for _ in range(60):
    K0, k0, f0 = 10 ** rng.uniform(-2, 5), 10 ** rng.uniform(-1, 1.7), rng.uniform(-2, 8)
    s = least_squares(resid_bta, x0=[K0, k0, f0],
                       bounds=([1e-8, 1e-8, -10], [1e10, 100, 20]), xtol=1e-14, ftol=1e-14)
    sse = float(np.sum(s.fun ** 2))
    if best is None or sse < best[0]:
        best = (sse, s.x)
K_bta, k_bta, f_bta = best[1]
pred_bta = model_ratios(wts_bta, K_bta, k_bta, f_bta, MW_BTA) * 400.0
print(f"Cu/BTA Frumkin 자기계 재현: K={K_bta:.2f} k={k_bta:.3f} f={f_bta:.3f} "
      f"pred(nm/min)={np.round(pred_bta,1)} obs=[65,42,42,42]")
assert max(abs(pred_bta - np.array([65, 42, 42, 42]))) < 3.0, "자기계 피팅은 3nm/min 이내"

# B2: f를 W/피콜린산에서 독립적으로 역산한 f=2.0으로 "이전"(re-fit 아님) — 더 정직한 교차검증
f_transfer = 2.0
C01, C025 = wt_to_mM(0.1, MW_BTA) * 1e-3, wt_to_mM(0.25, MW_BTA) * 1e-3
r01, r025 = 65.0 / 400.0, 42.0 / 400.0

def eqs(x):
    K, k = x
    th1, th2 = theta_frumkin([C01, C025], K, f_transfer)
    return [math.exp(-k * th1) - r01, math.exp(-k * th2) - r025]

(K_t, k_t), info, ier, msg = fsolve(eqs, [200, 2.5], full_output=True)
assert ier == 1, f"2점(0.1/0.25wt%) 정확 피팅 실패: {msg}"
C05b, C075b = wt_to_mM(0.5, MW_BTA) * 1e-3, wt_to_mM(0.75, MW_BTA) * 1e-3
th05, th075 = theta_frumkin([C05b, C075b], K_t, f_transfer)
pred05, pred075 = 400 * math.exp(-k_t * th05), 400 * math.exp(-k_t * th075)
dev05_pct = (pred05 - 42.0) / 42.0 * 100
dev075_pct = (pred075 - 42.0) / 42.0 * 100
print(f"f=2.0 이전(피콜린산 유래, BTA로 재피팅 안함): 0.1·0.25wt%에만 (K,k) 정확피팅 -> "
      f"0.5wt% 예측={pred05:.1f}nm/min({dev05_pct:+.1f}%), 0.75wt%={pred075:.1f}nm/min({dev075_pct:+.1f}%)")
# 판정#17이 이미 확립한 현행(Langmuir, k=3 고정) 0.5wt% 예측 28.14 (편차 -33.0%) 대비 개선폭
assert abs(dev05_pct) < 15, "이전된 f=2.0으로도 0.5wt% 편차가 15%p 이내여야 '개선'이라 부를 수 있다"
assert abs(dev05_pct) < 33.0, "적어도 판정#17의 Langmuir(k=3 고정, 편차 -33%)보다는 나아야 한다"

print("PASS: Frumkin(f≈2)이 두 앵커 모두에서 현행 Langmuir+exp(-kθ)보다 구조적으로 우월 — "
      "단 f의 '물리적 정당성'은 계마다 문헌 근거 수준이 다르다(§7).")
```

## 7. 채택/보류 판정

**보류(코드 미교체) — 그러나 다음 회차 최우선 후보로 명시 채택.**

| 근거 | 등급 | 판정에 준 무게 |
|---|---|---|
| §5·6 코드 검증: Frumkin(f≈2.0~2.2)이 판정#24·#17 앵커를 극적으로 개선 재현, 식별성도 뾰족 | **E1**(이 코드베이스 자체 실행, 원 데이터는 이미 E2급으로 확립됨) | 함수형이 "맞을 수 있다"는 강한 정황 |
| §2.1 Krishnan et al. 2024(IBM): CMP·Cu·BTA 동일계에서 Frumkin+cusp catastrophe 모델 존재 | **E5**(초록만, 원문 미확보) | 방향은 지지하나 수치 대조 불가 |
| §2.2 Antonijevic&Petrovic 2008: Cu 부식에서 Frumkin 일반 선례 | **E4**(계 전이 — 부식, BTA 아닌 분자) | BTA 자체·CMP 조건으로는 미검증 |
| 피콜린산-W 계 Frumkin 선례 | **없음** | §6의 f=2.0 "이전"은 순수 수학적 교차검증이지 문헌 근거가 아님 |

**판정 이유**: EVIDENCE-RULES 서열상 코드에 반영하려면 최소 E2급(폐형식 유도 + 같은 막질/화학계
검증)이 필요하다. 지금 손에 있는 것은 **E1(우리 코드가 우리 데이터를 잘 재현한다는 사실)**과
**E5(맞는 논문이 존재한다는 초록)**의 조합인데, 이 둘을 합쳐도 "저자가 실제로 쓴 f 값과 물리적
근거가 우리가 역산한 f≈2.0~2.2와 같다"는 것은 확인되지 않는다 — **데이터 재현이 아무리
인상적이어도, 원문 대조 없이 코드에 넣으면 "그럴듯한 회귀식"과 구별이 안 된다**(과제 규칙
정확히 그 문구). 판정#20(oxidizer_passivation_K)이 코드를 바꿨을 때는 대상계 E2 문헌(특허
실시예 인쇄표) 실측값에 **직접** 맞춘 것이었다 — 이번엔 그 자리에 올 문헌(Krishnan 2024)의
숫자를 못 봤다.

**다음 회차 1순위**: Krishnan et al. 2024(DOI:10.1149/2162-8777/ad5fe4) 원문 확보 — IOP
기관구독·저자(IBM Research, 현재 소속 변경 가능성 있음) 직접 요청·ResearchGate 개인 업로드
확인. 확보되면 (a) 그들의 f 값·K 값과 §5·6의 재도출값을 직접 대조, (b) BTA뿐 아니라 산화제·
연마입자 항의 상호작용까지 이 모델이 다루는지 확인, (c) 대조 결과가 일치하면 E2로 승격해
`sim/chemistry.py`에 `inhibitor_isotherm='frumkin'` 옵션을 **판정#20 선례대로 하위호환 추가**
(레거시 Langmuir 경로는 삭제하지 않음) 하는 것을 그 회차의 목표로 삼는다.

## 8. 미확보·한계 (정직 표기)

- **Krishnan et al. 2024 원문**: 이번 세션의 모든 접근 경로(IOP 직접, 미러 사이트 6미러, CORE,
  IBM 공식 페이지)가 실패했다. 세션마다 미러 사이트 미러 가용성이 바뀐다는 것은 기존 메모리
  기록과도 일치한다 — 다음 세션에서 재시도할 가치가 있다.
- **f≈2.0~2.2가 "임계 협동성"과 거의 정확히 겹치는 것**은 흥미롭지만, 이것이 물리적으로
  의미 있는 우연(실제로 Cu-BTA·W-피콜린산 흡착이 임계점 근방에서 작동)인지, 아니면 "관측된
  급격한 전이를 맞추려면 수학적으로 f가 그 근방일 수밖에 없다"는 동어반복(3파라미터로 3점을
  맞추면 늘 존재하는 해)인지 이 노트만으로는 구분할 수 없다. §5의 4점 과결정 피팅(Cu/BTA,
  자유도보다 데이터가 많음)이 그나마 후자 우려를 누그러뜨리지만 완전히 배제하지 않는다.
- **§6 B2의 "f=2.0 이전"은 통계적으로 한 사례(n=1 계 쌍)뿐**이다 — 임계 협동성 f≈2가 여러
  CMP 억제제 계에서 보편적인지 확인하려면 최소 하나의 제3계(예: TTA/Cu, BTA/W)가 더 필요하다.
- Temkin·Sips는 CMP 억제제 적용 문헌을 이번 회차에 하나도 찾지 못했다 — §4에 기록하고 이번
  회차 식별성 검사 대상에서 제외했다(문헌 근거 부재가 식별성보다 먼저 걸리는 문제이므로).
- Dai et al. 2024(TAZ 문턱)는 CMP 인접(전기화학 모사 셀)이지 실제 폴리싱 실측이 아니다 —
  §3.1에서 이미 밝혔듯 메커니즘도 비단조(최적농도)라 이번 앵커 재현에 직접 쓰지 않았다.

## 자기시험

1. 이 노트가 "Frumkin으로 바꾸자"고 코드를 바꾸지 않은 이유는? → 데이터 재현(§6)과 식별성
   (§5)은 충분히 강하지만, "이 f 값이 물리적으로 맞다"는 근거가 CMP 계(Krishnan 2024)에서는
   원문 미확보(E5), 계 전이(Antonijevic 2008)에서는 BTA·CMP 어느 쪽도 정확히 일치하지 않는다
   (E4) — 과제 규칙이 요구하는 "문헌 근거"가 수치 수준까지는 없다.
2. §2.3의 "f=2 임계점" 주장은 어느 근거 등급인가? → E1이 아니라 **수학(코드로 직접 증명한
   등온식 자체의 성질)**이다 — 문헌 인용이 필요 없는 유형의 주장이라 등급표에 넣지 않았다.
3. Dai et al. 2024(TAZ 문턱)를 왜 앵커 재현에 안 썼는가? → 메커니즘이 다르다(비단조 최적농도
   vs 판정#24가 필요로 하는 단조 포화형) — 억지로 맞추면 §0이 경계한 "회귀식"이 된다.
4. 다음 회차가 실패해도(원문 계속 미확보) 이 노트의 가치는? → §5·6의 코드 검증은 원문과
   무관하게 유효하다 — "Frumkin이 두 앵커를 재현할 수 있다"는 사실 자체는 남는다. 남은 것은
   "그 f가 왜 그 값인지"의 물리적 근거뿐이다.
