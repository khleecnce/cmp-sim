# SiC CMP H2O2 산화제 기전 — 함수형 판정 (2026-09-15)

> 결론 먼저: **방향(단조 촉진)과 기전(산화-제거 연쇄)은 문헌으로 확정.** 기존 3경로 중
> "레거시 단봉(Kaufman)"은 **이 팩(무 Fe 촉매 세리아계)에는 적용 근거가 없고**,
> "Langmuir 촉진 포화형"은 **직접 관측으로 반증**됐다(아래 §3). 남는 후보(선형/근사선형)는
> 기존 3경로 어디에도 없고, 그 형상조차 문헌 데이터의 축퇴 때문에 계수를 못 박는다.
> **코드·YAML 모두 미변경.** 함수형 방향만 확정하고 계수는 미확보로 남긴다.

## 과제 정의

`sic_ceria_h2o2` 팩에 `oxidizer_*` 형상 파라미터가 전혀 없어(판정#33·#34, `oxidizer_ref_wt_pct`만
선언) `sim/chemistry.py::_oxidizer_term`이 항상 `None`을 반환한다 — H2O2 농도가 모델에
연결돼 있지 않다. sic2026(n=50, `used_for_calibration: true`)에서 계수를 역산하면
이중학습이므로 금지. 이 노트는 **sic2026을 쓰지 않고** 함수형을 문헌으로 확정한다.

## §1. 물리 조사 — SiC CMP에서 H2O2의 역할

### 1.1 산화-제거 연쇄(oxidation-then-removal) 확인
Nitta et al. 2011 (*Jpn. J. Appl. Phys.* 50, 046501, doi:10.1143/JJAP.50.046501,
`papers/jjap50-046501-sic-high-removal-rate.pdf`, 1차 전문 확보)이 **직접 XPS로 확인**:
4H-SiC(Si-face)를 H2O2 용액에 12h 담그면 Si 2p 결합에너지가 DI water 대조군의 101 eV
(SiC 결정)에서 103–104 eV(SiO2)로 이동한다(Fig. 2). 즉 **H2O2가 SiC 표면을 SiO2로
직접 산화시키고, 이 무른 산화층이 기계적으로 제거된다** — 과제 §A가 가정한 산화-제거
연쇄가 그대로 confirmed. 순수 콜로이달 실리카(산화제 없음)의 제거율은 12 nm/h인데
H2O2 5wt% 추가 시 62 nm/h(5.2배)로 뛴다(Fig. 1) — 산화제가 없으면 SiC는 거의
깎이지 않는다는 과제 §A의 전제와 일치.

### 1.2 알칼리 분해 — 확인, 단 "손실"이 아니라 "경로 그 자체"
같은 논문 본문: *"H2O2 has easily self-decomposing quality in alkaline side"*
(pH 10.0 조건, KOH로 조정) — 과제 §A가 우려한 알칼리 분해가 **실제로 보고돼 있다.**
다만 이 분해가 산화력을 낭비하는 부반응이 아니라, **분해 산물(·OH, ·OOH 라디칼)이
바로 SiC를 산화시키는 활성종**이다(반응식 2H2O2→2H2O+O2, H2O2+OH·→H2O+OOH·,
H2O2+OOH·→O2+H2O+OH·). 즉 "유효농도<투입농도"라는 우려는 방향이 반대다 — 분해가
**곧 반응 경로**이므로, 분해가 빠를수록(알칼리일수록) 오히려 반응성이 올라간다는 게
이 논문의 주장이다. Wei et al. 2026(§1.3)도 동일한 라디칼 화학(·OH)을 쓴다.

### 1.3 Fenton(-like) 촉매가 있으면 단봉형이 나온다 — 그러나 이 팩엔 촉매가 없다
Wei et al. 2026 (*Crystals* 16(3) 179, doi:10.3390/cryst16030179, CC-BY,
`papers/wei2026-cryst16030179-4hsic-fenton-cmp.pdf`, 1차 전문 확보) — 4H-SiC **C-face**
+ 콜로이달 실리카 + H2O2 + **Fe3O4 촉매**(헤테로 Fenton), pH=9. §3.3: Fe3O4 0.03wt%
고정, H2O2를 스윕하면 MRR이 **5wt%에서 정점(701 nm/h)을 찍고 감소**한다(0/2.5/5/7.5/10 wt%
스윕, Fig.6). 기전(Eq.2–5): Fe(II)+2H2O2→Fe(III)+·OH+HO2·+H2O 로 ·OH가 빠르게 대량
생성되면, 과잉 H2O2·과잉 ·OH가 자기소모 반응(2·OH→H2O2, ·OH+H2O2→H2O+·OOH)을
일으켜 유효 ·OH가 오히려 줄어든다 — **이것이 기존 코드의 "레거시 Kaufman 단봉" 경로가
전제하는 바로 그 경쟁 기전**이다.

⚠ **그러나 `sic_ceria_h2o2`는 세리아 연마재이고 Fe3O4(또는 다른 Fe 화합물) 촉매가
없다.** 단봉이 나타나려면 ·OH 생성 속도가 충분히 빨라 "과잉 구간"에 도달해야 하는데,
그 속도를 만드는 것이 Fe3O4라는 강한 이종 Fenton 촉매다. 세리아 자체도 H2O2를
분해하는 산화환원 사이클(Ce4+→Ce3+→Ce4+, "catalase-mimetic",
[[ceria-slurry-ce-redox-selectivity]] §2)을 갖지만, 이건 **세리아
입자 표면 자신의 활성점 비율(Ce3+ fraction)을 바꾸는 국소 반응**이지 Fe-Fenton처럼
용액 전체에 ·OH를 대량 방출하는 반응이 아니다 — 세기가 다른 별개의 촉매 경로다.
Wei2026의 정점 위치(5wt%)를 **촉매가 없는 이 팩에 그대로 전이하는 것은 근거가
없다**(교란변수: 촉매 유무 자체가 다르다).

### 1.4 무촉매(또는 약촉매)계는 같은 농도범위에서 단봉을 보이지 않는다
Nitta 2011은 **Fe계 촉매가 없는** 콜로이달 실리카+H2O2, pH 10.0 알칼리 조건에서
H2O2를 0→1.47 mol/L(≈0→5.0 wt%, 계산은 §2)까지 스윕했다(Fig. 3). **정점이나 감소
구간이 관측되지 않는다** — 전 구간 단조 증가. 이는 "촉매가 약하면(또는 없으면) 반응
율속 단계가 ·OH 과잉-자기소모가 아니라 여전히 ·OH 생성 자체"라는 §A의 가설과 정확히
들어맞는다: 촉매가 없어 ·OH 생성이 느리면, 시험한 농도범위 내내 "더 넣을수록 더
깎인다"는 촉진 방향만 보이고 과잉 구간에 도달하지 못한다.

**1차 결론 (기전·방향)**: `sic_ceria_h2o2`(세리아, Fe 없음)는 Nitta형(촉진, 무촉매)에
가깝다 — Wei형(단봉, 강촉매) 조건이 아니다. 방향은 **촉진(농도↑→MRR↑)**, 함수형
후보는 기존 3경로 중 **`oxidizer_langmuir_K`(촉진 포화형)**이 유일하게 방향이 맞는다.
다음 절에서 그 정확한 형상(포화 곡률)을 실측으로 검사한다.

### 1.5 Pourbaix/전기화학 — 근거 없음(확인)
```
$ grep -rn "pourbaix" sim/
```
`sim/tier2_physics/cu_pourbaix.py`, `pourbaix_nernst_slope.py`만 존재 — **SiC 전용
Pourbaix 모듈은 없다.** Cu/W Pourbaix 노트도 SiC 표면종(SiO2/CO2 생성)에는 적용되지
않는 별개 화학(Si-C 공유결합 세라믹 vs 금속 산화)이라 이번 판정에 전기화학적 근거를
추가하지 못했다 — 미확보로 기록한다.

## §2. 정량 추출 — Nitta 2011 Fig.3을 벡터 좌표로 직접 판독

```python verify
# verify — PDF 벡터 드로잉에서 Fig.3의 H2O2 곡선 마커 좌표를 직접 추출한다(눈대중 아님).
# 좌표계: x축 그리드 0/0.5/1.0/1.5/2.0 mol/L가 x=117.818/151.020/184.144/217.347/250.473 pt,
#         y축 그리드 0..160 nm/h(20 간격)가 y=190.036..68.423 pt (get_drawings()로 직접 확인).
import fitz
doc = fitz.open("papers/jjap50-046501-sic-high-removal-rate.pdf")
page = doc[3]
diamonds = []
for d in page.get_drawings():
    r = d["rect"]
    # 채워진(fill) 작은 다이아몬드만 — 범례 아이콘(x:125~181,y:78~104)은 제외
    if d["type"] == "f" and r.x1 - r.x0 < 6 and r.y1 - r.y0 < 6 and r.x1 < 260 and r.y0 > 110:
        cx, cy = (r.x0 + r.x1) / 2, (r.y0 + r.y1) / 2
        conc = (cx - 117.818) * 0.5 / 33.202       # mol/L
        rate = (190.036 - cy) * 20 / 15.2           # nm/h
        diamonds.append((round(conc, 3), round(rate, 1)))
diamonds.sort()
assert diamonds == [(0.0, 12.0), (0.35, 21.0), (0.879, 42.0), (1.468, 63.0)]
print("Nitta 2011 Fig.3 H2O2 곡선 (mol/L, nm/h):", diamonds)
```
벡터좌표 재현값 63.0 nm/h은 (Nitta et al. 2011) 텍스트 본문의 정성적 서술("0 mol/L
무산화제 12 nm/h", "1.44 mol/L에서 58~63 nm/h")과 일치한다 — 좌표 판독이 본문 숫자를
정확히 재현했다는 문헌값 대조. mol/L→wt% 환산(H2O2 M=34.01 g/mol, 묽은 수용액 밀도≈1 g/mL 가정,
wt%≈mol/L×3.40): 0/0.35/0.879/1.468 mol/L ≈ **0 / 1.19 / 2.99 / 5.00 wt%** —
sic2026 DOE의 스윕범위(2/4/6 wt%)와 거의 겹친다(계수를 sic2026에서 뽑지는 않지만,
같은 물리적 창을 보고 있다는 교차확인은 된다).

## §3. 함수형 검사 — 기존 `oxidizer_langmuir_K`(촉진 포화형)가 이 데이터에 맞는가

`_oxidizer_term`의 촉진 경로: `f(C) = φ + (1-φ)·θ(C)/θ(C_ref)`, `θ(C)=KC/(1+KC)`,
K>0(촉진), θ는 **오목(포화)** 함수다. C=0 지점과 C=C_ref 지점을 관측으로 고정(anchor)
하면 자유 파라미터는 K 하나 — 나머지 중간 관측 2점(0.35, 0.879 mol/L)이 그 K를
과결정으로 검사한다.

```python verify
# verify — K를 중간 두 점 각각에서 독립적으로 역산하면 둘 다 물리적으로 불가능한
# 음수가 나온다(촉진형은 K>0 이어야 함) → 촉진-포화 함수형 자체가 반증된다.
C = [0.0, 0.350, 0.879, 1.468]           # mol/L
rate = [12.0, 21.0, 42.0, 63.0]          # nm/h
Cref = C[-1]
floor = rate[0] / rate[-1]                # C=0 앵커로 φ 고정 = 0.1905
f_obs = [r / rate[-1] for r in rate]      # C=Cref 앵커로 정규화(f(Cref)=1)

def solve_K(Ci, ri):
    r_target = (ri - floor) / (1 - floor)
    # theta(C)/theta(Cref) = r_target 을 K에 대해 풀면:
    # K = (C - r_target*Cref) / (Cref*C*(r_target-1))
    return (Ci - r_target * Cref) / (Cref * Ci * (r_target - 1))

K_035 = solve_K(C[1], f_obs[1])
K_088 = solve_K(C[2], f_obs[2])
assert K_035 < 0 and K_088 < 0                 # 둘 다 물리적으로 불가능(K>0 이어야 촉진형)
assert abs(K_035 - K_088) > 5 * min(abs(K_035), abs(K_088))  # 서로도 정합 안 함(7배 차이)
print(f"K(0.35mol/L 앵커)={K_035:.4f}  K(0.879mol/L 앵커)={K_088:.4f}  — 둘 다 음수, 불일치")
```
```python verify
# verify — SSE 스캔으로도 교차확인: K를 0에서 키울수록(포화를 강하게 걸수록) 적합이
# 단조로 나빠진다. 즉 최적점이 "포화 없음"(K→0) 경계에 붙어 있다 — 내부해가 아니다.
import numpy as np
from scipy.optimize import minimize
C = np.array([0.0, 0.350, 0.879, 1.468]); rate = np.array([12.0, 21.0, 42.0, 63.0])
Cref = C[-1]; f_obs = rate / rate[-1]

def sse_for_K(K):
    theta = lambda c: K*c/(1+K*c) if K > 0 else c   # K→0 극한은 선형(로피탈)
    thc, thref = theta(C), theta(Cref)
    def floor_sse(floor):
        pred = floor + (1-floor)*(thc/thref)
        return np.sum((pred-f_obs)**2)
    return minimize(lambda f: floor_sse(f[0]), x0=[0.15], bounds=[(0,1)]).fun

Ks = [0.0, 0.05, 0.2, 0.5, 1.0, 2.0, 5.0]
sses = [sse_for_K(K) for K in Ks]
assert sses == sorted(sses)   # K가 커질수록 SSE가 단조 증가(=포화를 걸수록 나빠짐)
print("K:", Ks); print("SSE:", [round(s,5) for s in sses])
```
**결론**: 촉진-Langmuir(포화)의 곡률 자체가 이 실측과 반대 방향이다 — 데이터는
오목(포화)이 아니라 **거의 선형이거나 약한 볼록(가속)** 형태다(과잉 H2O2가 반응
가능한 라디칼 수를 늘리는 2단계 충돌 확률 논거, Nitta 논문 §3.1 "reaction probability
of radicals to SiC depends on oxidant concentration"과 정성적으로 부합).

```python verify
# verify — 대안으로 멱함수 f(C)=floor+(1-floor)*(C/Cref)^n 을 자유적합하면 n≈1.10(거의 선형)
# 이지만, 4점 벡터판독 노이즈 안에서 n=1.0(순수 선형)과 통계적으로 구분되지 않는다.
import numpy as np
from scipy.optimize import minimize
C = np.array([0.0, 0.350, 0.879, 1.468]); rate = np.array([12.0, 21.0, 42.0, 63.0])
Cref = C[-1]; f_obs = rate / rate[-1]

def sse_power(p):
    floor, n = p
    if not (0 <= floor <= 1) or n <= 0:
        return 1e9
    pred = floor + (1-floor)*(C/Cref)**n
    return np.sum((pred-f_obs)**2)

res = minimize(sse_power, x0=[0.15, 1.0], method="Nelder-Mead")
floor_fit, n_fit = res.x
assert 0.9 < n_fit < 1.3        # 선형(n=1) 근방 — 뚜렷한 초선형/포화 곡률 없음
print(f"멱함수 적합: floor={floor_fit:.3f} n={n_fit:.3f} SSE={res.fun:.6f}")
```

## §4. 식별성 판정 — `sim/unknown_router.py::identifiability` 실행

```python verify
# verify
import sys
sys.path.insert(0, "sim")
from unknown_router import identifiability
ok, why = identifiability(n_unknowns=1, n_independent_observations=2)
assert ok is True
print(ok, why)
```
`identifiability()`는 **개수만으로는** "식별 가능"(관측 2 > 미지수 1)이라고 답한다.
그러나 §3의 실측 적합은 그 식별 가능한 K가 **모델 형태 자체와 모순되는 부호**(음수)로
나오고, 두 관측이 서로 다른 K를 요구한다(7배 차이) — **개수상 식별 가능한 것과
모델이 옳은 것은 다르다.** 이건 "관측이 부족해서 못 정한다"(판정#19형 축퇴)가
아니라 "모델 형태 자체가 이 데이터를 설명 못 한다"(판정#24A형 반증)에 더 가깝다.
남는 대안(선형/약볼록 멱함수)은 기존 3경로 어디에도 없고, 그 지수(n=1.0~1.3)조차
4점·타재료(실리카)·디지타이즈 노이즈 안에서 축퇴돼 있다 — R7(구조적 제거: 이 항을
모델에서 뺀다)로 귀결된다.

## §5. 결론 — 함수형은 방향만 확정, 코드·YAML 미변경

| 질문 | 답 |
|---|---|
| 산화-제거 연쇄가 맞는가? | **그렇다.** Nitta 2011 XPS가 SiC→SiO2 전환을 직접 확인(§1.1) |
| 알칼리에서 H2O2가 분해되는가? | **그렇다**(Nitta 2011 본문 명시, §1.2). 단 분해 산물(·OH/·OOH)이 곧 산화 활성종이라 "손실"이 아니라 "경로"다 |
| 어느 함수형인가(촉진/억제/단봉)? | **방향은 촉진**(농도↑→MRR↑, 두 독립 무촉매/약촉매계 문헌이 정성적으로 일치: Nitta 2011 무촉매, sic2026 DOE 자체 순위 rho=+0.221도 방향은 동일 — 단, sic2026은 확인용일 뿐 계수 출처 아님). 단봉은 **강한 Fe 촉매(Wei2026)가 있을 때만** 관측되며 이 팩엔 Fe가 없어 전이 근거 없음 |
| 기존 3경로 중 맞는 게 있는가? | **없다.** 촉진-Langmuir(포화, 오목)는 §3에서 직접 반증(K가 음수로만 풀림, 두 앵커점이 불일치). 단봉·억제형은 방향부터 다름 |
| 계수를 넣을 수 있는가? | **아니다.** 대안 형태(선형/약볼록 멱함수)의 지수조차 4점 디지타이즈 데이터(타재료·타촉매계, E3~E4급 교차전이)로 축퇴 — `identifiability()`는 개수상 통과하지만 모델적합 자체가 불안정(§4) |
| 코드를 고쳤는가? | **아니다.** `sim/chemistry.py::_oxidizer_term`, `knowledge/params/sic_ceria_h2o2.yaml` 전부 미변경. 기존 판정#34의 구조적 경고 note(§4.5, oxidizer_wt_pct 선언 시 형상 파라미터 부재 감지)가 이미 이 상태를 정직하게 신고하고 있어 그대로 유지 |
| sic2026 ρ는? | 코드 미변경이므로 **판정#34 종료 시점 값(ρ=0.393, p=0.002)에서 불변.** 이 회차에서 올리거나 내리려 하지 않았다 — null 결과(함수형 미확정)를 그대로 기록한다 |

## §6. 남은 갭 (다음 회차 후보)
- ⚠ **미검증 항목 명시**: (1) 세리아 촉매 세기가 Fe3O4보다 약해 이 팩의 관측범위에서
  단봉 문턱에 도달하지 않는다는 판단은 정량 속도상수 대조가 아니라 **정성적 추정**이다
  (미검증). (2) 함수형 지수(선형 n=1 vs 약볼록 n≈1.1)도 미검증 — §3·§4가 보인 것은
  "촉진-포화형은 아니다"라는 반증이지 "정확히 이 형태다"라는 확정이 아니다.
- 세리아 자체의 H2O2 분해(catalase-mimetic) 속도상수가 Fe3O4 대비 얼마나 느린지
  정량 문헌이 있으면 "왜 이 계에서 단봉이 안 나오는가"를 정성이 아니라 정량으로
  뒷받침할 수 있다 — 이번 회차엔 미확보.
- 세리아+H2O2(Fe 없음)+SiC 계에서 H2O2를 3점 이상 스윕한 **동일 계 내부** 데이터가
  나오면(Nitta처럼 다른 연마재가 아니라) 이 노트의 §3 검사를 다시 돌려 진짜 K(또는
  대안 지수)를 역산할 수 있다.
- `abrasive_size_nm`(세리아, 120nm) 문헌이 이미 실리카와 교차전이를 쓰고 있으므로
  (§sic_ceria_h2o2.yaml 주석), 여기서도 실리카(Nitta)→세리아 교차전이가 아주 근거
  없는 것은 아니다 — 다만 이번엔 **곡률(포화 vs 선형)을 가르는 정밀한 판정**이라
  1차 근사(방향)보다 훨씬 엄격한 기준이 필요했고, 그 기준을 통과하지 못했다.
