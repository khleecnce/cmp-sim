<!-- V2-SECTION: R2-slurry | 근거: oxidizer, chi, chelator, glycine, regime | 정본: ARCHITECTURE-V2.md §3 -->
# χ `cu_h2o2_bta` `oxidizer_acid_chelator_K` — 글리신계 1차 근거 탐색 (C2 마지막 1칸)

> 작성일: 2026-09-16 | 대상: `knowledge/params/cu_h2o2_bta.yaml::oxidizer_acid_chelator_K`
> 선행: [[chi-cu-h2o2-regime-reversal-jani2025]](판정#38·#41 — 게이트 신설, 옥살산 데이터로
> `K=0.7935` 적합, 글리신 실측 없어 confidence=estimated 고정)
> 과제: 판정#41 §9.0이 확인한 갭 — Jani 2025 원문 안에는 글리신>0 조건의 H2O2 단독 스윕이
> 없다. **원문 밖**에서 글리신 존재·산성~중성 pH·H2O2 3수준 이상 Cu CMP MRR 데이터를 찾는다.

## 1. 탐색 경로 전수기록

| 시도 | 결과 |
|---|---|
| Crossref `query.bibliographic=Aksu Doyle chemical mechanical polishing copper glycine` | `10.1149/1.1474436` "The Role of Glycine in the Chemical Mechanical Planarization of Copper" (Aksu, Doyle, JES 149(6) G352, 2002) 확인 — 과제 유력후보와 일치 |
| Crossref `query.bibliographic=Hariharaputhiran Zhang Ramarajan Babu ... hydroxyl radical` | `10.1149/1.1393979` "Hydroxyl Radical Formation in H2O2-Amino Acid Mixtures and CMP of Copper" (Hariharaputhiran et al., JES 147(10) 3820, 2000) 확인 — 과제 유력후보와 일치 |
| `tools/find_open_access.py --title "..."` (두 건) | 둘 다 OA PDF 없음(DOI만 매칭) — sci-hub 폴백으로 진행 |
| sci-hub.se/.st/.wf/.ru 직접 curl | DNS 미해석 또는 접속 실패(`Could not resolve host` / `http_code=000`) — 전멸 |
| sci-hub.ren, sci.bban.top | 200 OK 이지만 실제 PDF 링크가 `sci.bban.top/pdf/...` 로 Cloudflare JS 챌린지("Just a moment...") — curl 로 통과 불가 |
| **sci-hub.kr** (`citation_pdf_url` 메타 파싱 → `sci-hub.red/storage/...` 직링크) | **성공.** 두 논문 모두 첫 페이지 저자·제목·DOI 대조 완료(Aksu, Serdar / Doyle, Fiona M.; Hariharaputhiran, M. / Zhang, J. / Ramarajan, S. / Keleher, J. J.) — 오염 없음(판정#32 경계사항 확인 완료) |
| Aksu & Doyle 2002 본문 전수검토 | **부적격.** Table I–IV는 전부 EOC(개회로전위)·RP(분극저항)·iOC(부식전류밀도) — 순수 전기화학 측정치뿐이고 실제 CMP 제거율(nm/min) 표가 없다. H2O2 농도 스윕 실험 자체가 없음(H2O2는 논의부에서 타 문헌 인용으로만 언급). 조건#1·#2 둘 다 불충족 |
| Aksu & Doyle 2002 본문 중 Hirabayashi 인용(ref 13·14) 발견 | 본문(p.G352 부근)이 "Hirabayashi et al.이 0.1 wt%(~0.13 M) 글리신, pH 6.7 용액에서 H2O2 소량 첨가 시 용해율 증가, 5 wt% 초과 시 감소"를 직접 서술 — 정확히 우리가 찾던 글리신+H2O2 스윕의 존재를 시사하는 단서 |
| ref 13 = US Pat. 5,575,885 (Hirabayashi et al., Toshiba) 확보 시도 | `patents.google.com` 503(차단) → `freepatentsonline.com/5575885.html` 200 OK(텍스트, 특허 발명자·출원인 일치 확인: Kabushiki Kaisha Toshiba) → 도면 원문은 `patentimages.storage.googleapis.com/pdfs/US5575885.pdf` 에서 27쪽 전체(도면 포함) 확보 |
| **US5,575,885 FIG.2 정독** | **적격.** 아미노아세트산(글리신) 0.1 wt% 고정, H2O2 만 스윕, "폴리싱 중 Cu막 에칭률(during polishing, nm/min)" 곡선 — 아래 §2·§3 |
| Crossref `query.bibliographic=Du Tamboli Desai Seal copper CMP glycine` | `10.1149/1.1648029` "Mechanism of Copper Removal during CMP in Acidic H2O2 Slurry" (Du, Tamboli, Desai, Seal, JES 151(4) G230, 2004) — 과제 유력후보와 일치. sci-hub.kr에서 확보, 첫 페이지 저자 일치 확인. **본문에 `glycine` 단어가 0회 등장** — 착화제 없는 순수 pH4 H2O2 슬러리 연구였다(조건#2 불충족, 부적격). 배경정보로만 기록(§6) |
| Crossref `query.bibliographic=Du Tamboli Desai Seal ... Cu sulfate glycine`(2차) | `10.1016/j.electacta.2004.05.008` "Effect of hydrogen peroxide on oxidation of copper in CMP slurries containing glycine and Cu ions" (Electrochimica Acta 2004) 확인 — 제목상 가장 유력한 후보였으나 **PDF 확보 실패**: Unpaywall landing(UCF STARS 리포지토리)은 메타데이터만("no-file"), IOPscience/sci-hub.kr·.ee·.ren·.ru 전부 차단(캡차 3회 연속 또는 Cloudflare/DDoS-Guard 챌린지) — ⚠ 미확보로 기록 |
| 기존 로컬 파일 `papers/aksu2003-electrochimica-bta-glycine-cu-cmp.pdf` 재검토 | 실제 저자는 Ein-Eli, Abelev, Starosvetsky(Electrochimica Acta 49, 1499, 2004) — 순수 전기화학(OCP, potentiodynamic sweep)이며 CMP 제거율 표 없음. **부적격**(조건#1). 다만 "글리신은 BTA와 달리 전기화학적 부동태 거동에 영향을 주지 않는다"는 서술은 방향성 보조증거로 기록(§6) |

## 2. 확보 문헌

1. **Hirabayashi, Kinoshita, Kaneko, Hayasaka, Higuchi, Mase, Oshima**, US Patent 5,575,885,
   "Copper-based metal polishing solution and method for manufacturing semiconductor device"
   (Kabushiki Kaisha Toshiba, 출원 1994-12-09, 등록 1996-11-19).
   전문 확보: `papers/hirabayashi1996-us5575885-cu-polishing-aminoacetic-acid.pdf`(도면 포함 27쪽).
2. Aksu, Doyle, "The Role of Glycine in the Chemical Mechanical Planarization of Copper",
   *J. Electrochem. Soc.* **149**(6) G352 (2002), doi:10.1149/1.1474436.
   `papers/aksudoyle2002-jes-role-glycine-cu-cmp.pdf` — **부적격**(전기화학뿐, H2O2 스윕 없음),
   Hirabayashi 특허로 가는 단서로만 사용.
3. Hariharaputhiran, Zhang, Ramarajan, Keleher, Li, Babu, "Hydroxyl Radical Formation in
   H2O2-Amino Acid Mixtures and Chemical Mechanical Polishing of Copper", *J. Electrochem. Soc.*
   **147**(10) 3820 (2000), doi:10.1149/1.1393979.
   `papers/hariharaputhiran2000-jes-hydroxyl-radical-amino-acid-cu-cmp.pdf` — 단일 H2O2 농도점
   (5 wt%)만 있어 스윕 조건 불충족이지만, 팩 기준 글리신 농도와 거의 일치하는 조성의 실측
   CMP 제거율 값이 있어 보조 앵커로 사용(§3).
4. Du, Tamboli, Desai, Seal, "Mechanism of Copper Removal during CMP in Acidic H2O2 Slurry",
   *J. Electrochem. Soc.* **151**(4) G230 (2004), doi:10.1149/1.1648029.
   `papers/du2004-jes-mechanism-cu-removal-acidic-h2o2-slurry.pdf` — 글리신(또는 임의 착화제)
   없는 조성이라 부적격, 배경정보로만 인용(§6).
5. Ein-Eli, Abelev, Starosvetsky, "Electrochemical aspects of copper CMP in peroxide based
   slurries containing BTA and glycine", *Electrochimica Acta* **49** 1499 (2004).
   `papers/aksu2003-electrochimica-bta-glycine-cu-cmp.pdf`(기존 보유) — 부적격, 보조증거만.

## 3. 데이터 표

### 3.1 주 데이터 — US5,575,885 FIG.2 (그래프 판독, 최후수단)

조건: 아미노아세트산(글리신) **0.1 wt% 고정**, H2O2 만 스윕, 물 용액(알칼리제 KOH **미첨가**
— 특허 청구항 7·명세서에 "pH 9–14로 조정하려면 알칼리제를 **추가로** 넣으라"고 명시되어
있어, KOH 무첨가 조건은 자연(비조정) pH다). 자연 pH는 명시 수치가 본문에 없으나,
Hariharaputhiran(2000)이 보고한 동종 조성(H2O2+글리신 수용액)의 자연 pH 범위 2.7–6.5(§3.2)와
정합적으로, **pH<7로 추정**한다(직접 측정치 아님 — §6 한계).

판독 방법: `read_method: figure`(그래프 판독). PDF를 10× 확대 렌더링 후 축 눈금 픽셀 좌표를
`scipy.ndimage`로 검출해 선형보정(x: 5→843px, 10→1422px ⇒ 115.8 px/wt%; y: 상단테두리
202px=100, 하단테두리 3777px=0 ⇒ 35.75 px/(nm/min)), 각 open-circle(폴리싱 중 에칭률,
우축) 중심을 로컬 크롭 내 dark-pixel 중심으로 계산했다. 코드는 §4 블록1에 포함.

| H2O2 (wt%) | Cu 폴리싱 중 에칭률 (nm/min, 우축 open circle) | 판독 픽셀(x,y) |
|---|---|---|
| 0.5 | 76.0 | (324.3, 1062.2) |
| 5.0 | 37.4 | (850.0, 2440.6) |
| 12.0 | 10.5 | (1678.3, 3402.2) |

**방향: 단조 감소.** H2O2가 늘수록 Cu 폴리싱 중 제거율이 줄어든다 — Jani 2025 옥살산계
(판정#41, 증가 방향)와 **정반대**다.

참고로 같은 그래프의 좌축(딥핑 중 정적 에칭률, filled circle)은 0→28(0.5wt%, 피크)→19
(1.5wt%)→0(5wt%)로 **비단조**(피크형)다. 이건 조건#1(정적 식각율 제외)에 해당해 주 데이터로
쓰지 않는다 — 우축(폴리싱 중, 실제 패드 마모 동반) 값만 채택했다.

### 3.2 보조 앵커 — Hariharaputhiran 2000 Table IV (doi:10.1149/1.1393979, 인쇄표, 단일 H2O2점)

| 조성 | 연마제 유무 | H2O2 | 글리신 | pH | Cu 폴리싱율 (nm/min) |
|---|---|---|---|---|---|
| Table IV 행3 (doi:10.1149/1.1393979) | with abrasive(3wt% 알루미나) | 5 wt% | 1 wt% (≈0.13 M — 팩 `chelator_M=0.1332`와 거의 일치) | natural(2.7–6.5 범위 내, 조성별로 가변) | **406 ± 44** |

H2O2 단독 스윕이 없어(같은 논문 Fig.9는 Cu(NO3)2 스윕, H2O2는 고정) 독립 데이터셋으로
쓸 수 없다. 다만 팩의 글리신 농도(1 wt%, 0.1332 M)와 사실상 동일한 조성이라, §4의 정성적
교차검증에만 쓴다.

## 4. K 재적합 — 구조적으로 불가능함을 확인

```python verify
import sys
sys.path.insert(0, ".")
from sim.tier2_physics.slurry_components import oxidizer_coverage_langmuir as theta
import numpy as np
from scipy.optimize import minimize_scalar

PHI = 0.15
def f(C, K, C0=0.5):
    t, t0 = theta(C, K), theta(C0, K)
    return PHI + (1 - PHI) * t / t0

# US5,575,885 FIG.2 — 글리신 0.1wt% 고정, H2O2 스윕 (그래프 판독, 판정 노트 §3.1)
OBS = {0.5: 76.0, 5.0: 37.4, 12.0: 10.5}
obs_ratio = {C: v / OBS[0.5] for C, v in OBS.items()}

# (a) 현행 K=0.7935 (판정#41, 옥살산 proxy 적합값)로 이 데이터를 재현하면?
K_STORED = 0.7935
pred_stored = {C: f(C, K_STORED) for C in OBS}
print("현행 K=0.7935 예측(0.5wt% 대비 배수):", {c: round(v, 3) for c, v in pred_stored.items()})
print("실측 배수:", {c: round(v, 3) for c, v in obs_ratio.items()})
# 실측은 감소(1.0 -> 0.49 -> 0.14)인데 현행 K는 증가를 예측 -> 부호 반대
assert pred_stored[5.0] > pred_stored[0.5], "현행 K는 구조적으로 증가를 예측한다(확인용)"
assert obs_ratio[5.0] < obs_ratio[0.5], "실측은 감소한다(확인용)"

# (b) 같은 함수형(phi=0.15 고정, K 1개 자유도)으로 독립 재적합하면?
def sse(logK):
    K = np.exp(logK)
    pred = {C: f(C, K) for C in OBS}
    return sum((pred[C] - obs_ratio[C]) ** 2 for C in OBS)

res = minimize_scalar(sse, bounds=(-20, 20), method="bounded")
K_best = float(np.exp(res.x))
print(f"최소자승 최적 K* = {K_best:.3e}, 잔여 SSE = {res.fun:.4f}")

# theta(C,K)=KC/(1+KC)는 C에 대해 항상 단조증가이므로 f(C)도 K값과 무관하게 항상
# 단조증가(K->0에서 선형증가, K->inf에서 평탄값1로 수렴) -- 감소를 표현할 K는 존재하지 않는다.
assert K_best > 1e6, f"최적 K*={K_best:.3e}가 포화영역(K->inf, 평탄예측)으로 발산 — 구조적 불가 확인"
assert res.fun > 0.5, f"평탄예측(f=1)조차 SSE={res.fun:.3f}로 큼 — '최적'조차 데이터를 설명 못함"
print("=> 촉진-포화형 함수형은 이 글리신 데이터의 '감소' 방향을 어떤 K로도 표현할 수 없다"
      " (구조적 반증, 판정#38과 동일 패턴이 이번엔 글리신 실측으로 재현됨)")

# (c) 기존 Jani 2025 재현(판정#41)은 이 판정과 무관하게 그대로 유지되는지 재확인
BASE_JANI = {3.0: 2282.0, 4.0: 2533.0, 6.0: 2578.0}
jani_ratio = {c: v / BASE_JANI[3.0] for c, v in BASE_JANI.items()}
def f_jani(C, K=K_STORED, C0=3.0):
    t, t0 = theta(C, K), theta(C0, K)
    return PHI + (1 - PHI) * t / t0
for c in (4.0, 6.0):
    err = abs(f_jani(c) - jani_ratio[c]) / jani_ratio[c]
    assert err < 0.05, f"판정#41 Jani 재현이 이 판정으로 깨졌다(회귀) c={c} err={err:.1%}"
print("=> 판정#41의 Jani 2025 옥살산계 재현(5% 이내)은 이 판정과 무관하게 그대로 유지된다"
      " — YAML/코드를 건드리지 않았으므로 당연한 결과지만, 명시적으로 재확인했다")
```

## 5. 판정

**승격 기각. YAML·코드 변경 없음.** `oxidizer_acid_chelator_K=0.7935`, confidence
`estimated` 그대로 유지한다.

이번 회차는 과제가 요구한 "글리신 존재 조건의 H2O2 스윕" 1차 데이터를 실제로 찾아냈다
(US5,575,885 FIG.2 — §3.1). 그런데 그 데이터는 판정#41이 옥살산 데이터로 세운 가정
("산성×착화제 → H2O2 증가 시 Cu 제거율 **증가**")과 **정반대 방향**(글리신 0.1wt% 고정 시
H2O2 증가 → 제거율 **감소**, 76→37→10.5 nm/min)을 보인다. §4의 수치실험이 확인하듯,
현재 게이트가 쓰는 촉진-포화형 함수형 `f(C) = phi + (1-phi)*theta(C)/theta(C_ref)`는
theta가 C에 대해 항상 단조증가이므로 **어떤 K를 넣어도 감소를 표현할 수 없다**(최적화가
K→∞, 즉 평탄 예측으로 발산하고 그 상태에서도 SSE가 크다). 이는 판정#29→#38에서 밝혀진
"K값이 틀렸다"는 종류의 오차가 아니라, "이 함수형 자체가 실제 글리신계의 부호를 못 담는다"는
**함수형 수준의 구조적 반증**이다.

과제 지시의 A/B/C 중 어느 것에도 깨끗이 들어맞지 않는다:
- **A는 아니다** — 데이터를 확보했지만 현행 K는 이 데이터를 전혀 재현하지 못한다(부호 반대).
- **B(재적합)를 문자 그대로 적용하지 않았다** — §4(b)가 보여주듯 이 함수형 안에서 "재적합"은
  수학적으로 무의미하다(최적해가 발산, 잔차가 여전히 큼). 이런 퇴화한 "최적 K"를 코드에 넣고
  confidence를 literature로 올리는 것은 "데이터가 모델을 지지한다"는 잘못된 인상을 준다 —
  오히려 정반대(모델을 반증한다)이므로, 억지로 B를 적용하지 않았다.
- **C(데이터 없음)도 아니다** — 데이터는 있다. 다만 그 데이터가 승격이 아니라 **판정#41이
  세운 게이트 전제 자체에 대한 반증**을 제공한다는 점에서 C보다 훨씬 무거운 발견이다.

그래서 판정#38(레짐 불일치 발견 → BIAS로 재분류 → §7 구현요청 → 판정#41에서 게이트 신설)과
**동일한 패턴**을 따른다: 이번 판정은 confidence를 estimated로 유지한 채, 다음 BIAS급
검토가 필요한 구체적 반증 근거를 남긴다. 단, 이번 과제 범위는 C2(confidence 승격) 한정이라
게이트 재설계(예: 착화제 종에 따라 촉진형/억제형을 다시 분기하는 것, 또는 촉진-포화형을
비단조 함수형으로 교체하는 것)는 **이번 판정의 범위 밖**이다 — 물리적 근거 없이 즉흥적으로
함수형을 바꾸지 않는다(금지 규칙). §7에 후속 작업으로 명시적으로 넘긴다.

### 5.1 후속 작업 요청 (구현하지 않음, 기록만)

- `oxidizer_acid_chelator_K` 게이트의 전제("산성×착화제 → 촉진")는 옥살산 데이터(Jani 2025)
  에서만 확인됐고, 글리신 실측(이번 판정)은 **반대** 방향이다. 착화제 종에 따라 산화제-제거율
  관계의 부호 자체가 갈릴 가능성이 높다 — 옥살산과 글리신을 같은 "산성×착화제" 레짐으로
  묶은 것 자체가 과도한 일반화였을 수 있다(판정#41 §9.5가 이미 옥살산 계수 +536.63 /
  글리신 계수 −440.91 부호반전을 경고했었다 — 이번 판정은 그 경고가 **실측으로 확인됨**을
  보여준다).
- 다음 BIAS급 판정에서 검토할 것: (i) `chelator_species` 값에 따라 촉진형/억제형을 다시
  분기하는 2차 게이트, 또는 (ii) 비단조(피크형) 함수형 도입 — 단, US5,575,885는 특허 문서라
  등급이 E2이고 n=3(그래프 판독)뿐이므로, 게이트를 다시 바꾸기 전에 동일 방향을 보이는
  독립 데이터셋이 하나 더 필요하다(예: 미확보한 Electrochimica Acta 2004 Du et al. 논문 —
  §1 참고, 아직 원문 미확보).

## 6. 한계

- **주 데이터(§3.1)는 특허 문서의 그래프 판독**이다 — 인쇄된 수치표가 아니라 10배 확대
  렌더링 후 픽셀 좌표를 선형보정해 읽은 값이라 ±5% 내외의 판독오차가 있을 수 있다(축
  눈금 교차검증은 했으나 원자료 표는 없다). 등급은 E2(특허 실시예/도면)로, Jani 2025의
  E2(학술지 인쇄표)보다 약간 낮다.
- **pH가 직접 측정되지 않았다** — KOH 미첨가라는 사실과 Hariharaputhiran(2000)의 동종
  조성 자연 pH 범위(2.7–6.5)로부터 pH<7을 추정했을 뿐, US5,575,885 FIG.2 실험 자체의
  pH 실측값은 본문에 없다.
- **글리신 농도가 팩과 다르다** — FIG.2는 0.1 wt%(≈0.0133 M), 팩은 1 wt%(0.1332 M)로
  10배 차이난다. Hariharaputhiran Table IV(§3.2, 1wt% 글리신 조성)는 팩과 농도가 거의
  일치하지만 H2O2 스윕이 아니라 단일점이라 방향성 확인에 못 쓴다 — "농도가 다른 스윕
  데이터"와 "농도가 같은 단일점 데이터"를 조합해도 재적합에 필요한 3점 스윕은 못 만든다.
- **n=3, 단일 특허 실시예** — 반복측정이나 오차범위 표기가 없다(Hariharaputhiran의
  "±"와 달리 특허 도면에는 오차막대가 없다).
- Du et al.(2004)의 무착화제 pH4 H2O2 슬러리도 "1% 근방에서 피크 후 감소"라는 **비단조**
  거동을 보고한다 — 착화제 유무와 무관하게 pH4 산성 H2O2계에서 "고농도 H2O2 → 감소"
  방향이 흔하다는 정황증거이지만, 착화제가 없어 조건#2 미충족이라 정식 증거로 채택하지
  않았다.
- Electrochimica Acta 2004(Du, Tamboli, Desai, Seal, "Effect of hydrogen peroxide on
  oxidation of copper in CMP slurries containing glycine and Cu ions") — 제목상 가장
  직접적으로 관련된 논문일 가능성이 높으나 **원문을 확보하지 못했다**(§1). 다음 회차에서
  재시도할 가치가 있다.
