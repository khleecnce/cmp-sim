# 막질·공정별 EPD 적합성과 한계 — 투명막 간섭 모호성·다층/패턴 신호 희석

> tool-endpoint Lv2-1. 선행: [[epd-optical-motor-friction-eddy-current-comparison]] (Lv1-1, 세 원리
> 비교·반사율표·30–40nm 투명화), [[epd-signal-processing-filtering-overpolish]] (Lv1-2, 필터·오버폴리시).
> 이 노트는 그 원리들을 **어느 막질/공정에 쓰는가**와 **어디서 무너지는가**로 재배치한다.
> 신호처리(Lv1-2)는 반복하지 않고, 트레이스→제거량 역산은
> [[epd-trace-removal-remaining-thickness-inversion]] (Lv2-2)이 다룬다 — 특히 이 노트 §2의
> 간섭 주기 모호성은 Lv2-2 §2에서 "절대두께 모호 vs 상대 제거량 무모호"로 정밀화된다.
> 초점은 **적합성·한계**뿐. 관련: [[cmp-tool-endpoint-thermal-slurry-delivery]], [[../cmp/ild-cmp-planarization-global-local-density]],
> [[../cmp/sti-cmp-ceria-high-selectivity-nitride-stop-dishing]], [[../cmp/pattern-dependent-dishing-erosion]].

## 1. 막질/공정별 EPD 방식 지도

세 원리(Lv1-1)는 측정하는 물리량이 달라서 적용 막질이 갈린다. Lai(2001, MIT 박사논문
6장)는 광학 계열을 둘로 나눠 **간섭계(interferometry)는 투명 유전막에, 반사율
측정(reflectance)은 불투명 금속 표면(면적분율)에** 쓴다고 명시한다: "The interferometry
technique measures the film thickness based on the interference of light from the surface and
the underlying layers. This is suitable for measuring transparent films such as dielectric layers,
but not effective for opaque metal films. By contrast, the reflectance measurement is ideal for
detecting the surface topography and the metal area fraction on the surface."[1]

| 공정/막질 | 적합 EPD | 측정 물리량 | 부적합 EPD와 이유 |
|---|---|---|---|
| 금속 벌크 제거 (Cu, W) | 모터전류·와전류, 광학 **반사** | 마찰 전이 / 금속 실두께 / 반사강도 | 광학 **간섭** ✗ — 불투명막은 하층 간섭광 없음[1] |
| 유전체/ILD (SiO₂, TEOS, low-k) | 광학 **간섭** | 막 실두께(간섭 주기) | 와전류 ✗(도전체 없음), 모터전류 ✗(대비 작음)[1] |
| STI (oxide→nitride stop) | 광학 간섭 + 모터전류(마찰 전이) | 두께 / SiO₂↔Si₃N₄ 마찰 전이 | 와전류 ✗ (둘 다 비금속) — [[../cmp/sti-cmp-ceria-high-selectivity-nitride-stop-dishing]] |
| 금속 후 배리어 노출 (Cu→Ta/TaN) | 반사강도 급락 | 반사율 계면 대비 | 극박 배리어는 광학에 반투명(§3)[1] |

핵심은 **간섭 vs 반사가 같은 광학 모듈의 서로 다른 모드**라는 점이다(Lv1-1 §2에서
확인). 간섭은 투명막에서만 성립하고, 반사는 불투명 금속에서 계면 대비를 준다. 금속
전용인 와전류·모터전류는 유전막에 원리상 적용 불가다(Lv1-1 §3·§4).

## 2. 투명막(투명 유전체) 위 광학 간섭 EPD의 한계 — 주기적 모호성

투명막의 두께를 간섭으로 읽으면 신호가 **주기 함수**라 두께가 유일하게 결정되지 않는다.
IBM 특허 US4293224("Optical system and technique for unambiguous film thickness monitoring",
1981-10-06)는 이 모호성을 정량화한다[2]:

- **두께 변화 $\lambda/2n$가 사인 신호의 완전한 1주기**에 해당한다("A thickness change of
  $\lambda/2n$ ... corresponds to a complete cycle of the sinusoidal signal")[2].
- 따라서 단일 파장(monochromatic) 신호는 **초기 두께 불확정을 $\lambda/2n$ 이내로만**
  해소한다. 특허 예시: 통상 광학재료 $n\approx1.5$, 편의상 $\lambda\le1\,\mu$m이면 초기
  막두께를 **약 0.3 µm 이내로 이미 알고 있어야** 반사차수(order) 모호성을 피한다[2].
- 두 번째 파장을 추가하면 비모호 범위가 늘어난다. 두 파장의 $\lambda/2n$가 0.15, 0.25 µm
  이면 결합 신호의 반복주기가 **긴 쪽 단독의 3배**(=0.75 µm)로 확장된다[2].

즉 투명막 간섭 EPD는 "지금 두께가 $d$인지 $d\pm\lambda/2n$인지"를 신호만으로는 구분
못 한다 — **초기 두께를 알거나 다파장/광대역으로 차수를 풀어야** 절대두께가 나온다. 이는
불투명 금속의 반사강도 급락(계면 하나만 잡으면 됨)과 근본적으로 다른 제약이다. 실제
유전막(SiO₂, $n\approx1.46$, $\lambda=600$ nm)에서 1 fringe는 약 205 nm 두께에 해당한다
(§5에서 재현, $\lambda/2n$ 관계는 US4293224[2]) — 즉 205 nm 미만 잔막은 한 주기도 못
채워 간섭만으로 카운트할 수 없다.

## 3. 다층/패턴 웨이퍼 — 면적분율 신호 희석과 국소 불균일

패턴 웨이퍼의 반사 신호는 스캔 스팟 안 여러 재질의 **면적분율 가중 평균**이다. Lai(2001)는
입사광 파장이 패턴 요철보다 크면 표면이 정반사(specular)에 가까워져 "reflectance ...
will essentially indicate the Cu area fraction only"라 하고, 종점 시점 복합표면 반사율을
식(6.10)으로 준다[1]:

$$R = A_f\,R_{Cu} + (1-A_f)\,R_{Oxide}$$

여기서 $A_f$는 Cu 배선 면적분율, $R_{Cu}/R_{Oxide}$는 각각 Cu·TEOS의 정반사 반사율이다[1].
이 선형식이 곧 **신호 희석**의 원인이다: 어떤 국소 피처(면적분율 $f$)가 Cu→oxide로 전이
하면 스팟 평균 반사율 변화는 $\Delta R = f\,(R_{Cu}-R_{Oxide})$뿐이라, $f$가 작은 저밀도
영역의 클리어링은 신호가 노이즈에 묻힌다(§5 재현: $f=0.1$은 $f=0.5$의 1/5 신호).

같은 실험에서 **국소 불균일(clearing 시점 분산)**도 직접 관측된다. Cu MRR이 패턴
기하에 강하게 의존해("The MRR of Cu strongly depends on the pattern geometry ... nonuniform
pattern layout usually causes nonuniform polishing across the die area")[1], Cu 면적분율이
높은 서브다이(예 $A_f=0.5$)가 먼저 연마되어 약 2분 후 Ta 배리어가 노출되고, 이때
반사율이 약 0.8로 떨어졌다가 산화막 노출(약 3분)에서 약 0.5로 더 떨어졌다[1]. 즉 **한
웨이퍼 안에서 clearing 시점이 서브다이마다 어긋나** 종점이 "선"이 아니라 "구간"으로
번진다 — 저밀도 영역이 아직 안 뚫렸는데 고밀도 영역은 이미 오버폴리시·디싱에 들어간다
([[../cmp/pattern-dependent-dishing-erosion]]와 직접 연결).

**다층 스택 혼선**도 있다. Cu가 걷힌 뒤 극박 Ta 배리어는 두꺼울 때보다 빛에 반투명해져
("an ultra-thin Ta barrier, which is more transparent to the light than the thick layer, may
still remain on the surface and may not be detected by the optical sensor")[1] — 광학 센서가
배리어 잔막을 놓치므로 실무는 종점 검출 후 짧은 오버폴리시를 더한다(Lv1-2 §4의
오버폴리시 논리와 동일 귀결, 단 여기서는 원인이 신호지연이 아니라 **박막 반투명화**).

## 4. 각 방식의 물리적 검출 한계 (문헌 수치)

- **광학 반사(금속):** 금속막이 **30–40 nm 이하**로 얇아지면 관통깊이 한계로 반투명해져
  반사 기반 신호가 무너진다(Tian et al. 2023[3], Lv1-1 §2에서 확보).
- **광학 간섭(유전막):** 잔막이 fringe 주기($\lambda/2n\approx$205 nm @ SiO₂·600nm)보다
  얇으면 1주기를 못 채워 차수 모호성이 지배(§2, US4293224[2]).
- **와전류(금속 실두께):** 얇아질수록 "the signal does not form accurately, and thus the
  measurement of thickness is limited"[4]. An et al.(NCCAVS, Sungkyunkwan Univ.)의 기본
  시스템은 측정범위가 **약 3000 Å(=300 nm) 하한**으로 짧았고, 신호처리(이동평균+칼만)
  ·전압증폭 최적화 후 측정범위를 **7000 Å ~ 550 Å(=55 nm)**로 확장, 분해능을 약 18–20배
  개선했다(EPD 윈도우 1.5 mm 기준)[4]. 즉 개선 전에는 수백 nm, 개선 후에도 **최소 ~55 nm**
  — 광학 반사 투명화(30–40 nm)와 같은 "수십 nm" 영역에서 금속 EPD 전반이 한계에 부딪힌다.
- **모터전류(마찰 전이):** 두께 자체를 못 재고 계면 대비가 작으면 실패(Lv1-1 §1·§4).

## 5. 정량 재현 — 간섭 주기·박막 반사율·희석·검출한계

```python verify
import math, cmath
from fractions import Fraction

# ── Block A: 간섭 주기 λ/2n 와 order 모호성 (US4293224[2]) ──
n_opt, lam = 1.5, 1.0e-6
period_uncert = lam/(2*n_opt)                 # 단파장 비모호 범위
assert abs(period_uncert*1e6 - 0.333) < 0.02  # 특허 "약 0.3µm"
print(f"[A] n=1.5,λ=1µm: λ/2n={period_uncert*1e6:.3f}µm (특허 '약 0.3µm')")

p1, p2 = 0.15, 0.25   # µm, 특허 두 파장 예시
f1, f2 = Fraction(p1).limit_denominator(1000), Fraction(p2).limit_denominator(1000)
lcm_num = f1.numerator*f2.numerator // math.gcd(f1.numerator, f2.numerator)
joint = lcm_num / math.gcd(f1.denominator, f2.denominator)   # 두 주기의 LCM
assert abs(joint-0.75) < 1e-9 and abs(joint/p2 - 3.0) < 1e-9  # 긴쪽의 3배
print(f"[A] 두 파장 λ/2n={p1},{p2}µm → 결합 비모호범위={joint:.2f}µm = {joint/p2:.0f}×(긴쪽 {p2}µm)")

n_sio2, lam2 = 1.46, 600e-9                    # 실제 SiO2 유전막
fringe = lam2/(2*n_sio2)
assert 200 < fringe*1e9 < 210                  # 내 계산값(문헌 상수 n,λ로부터)
print(f"[A] SiO2 n=1.46,λ=600nm: fringe 주기={fringe*1e9:.1f} nm/주기")

# ── Block B: 박막 간섭 반사율(Airy) — 주기 재현 + 얇은 잔막 모호성 ──
n0, n1, n2 = 1.0, 1.46, 3.88                   # air/SiO2/Si(@600nm, k≈0 근사)
r01 = (n0-n1)/(n0+n1); r12 = (n1-n2)/(n1+n2)
def R_film(d):
    beta = 2*math.pi*n1*d/lam2                  # 편도 위상
    return abs((r01 + r12*cmath.exp(-2j*beta))/(1 + r01*r12*cmath.exp(-2j*beta)))**2
ds = [i*1e-9 for i in range(0, 600)]; Rs = [R_film(d) for d in ds]
ext = [ds[i] for i in range(1, len(Rs)-1) if (Rs[i]-Rs[i-1])*(Rs[i+1]-Rs[i]) < 0]
period = 2*sum(ext[i+1]-ext[i] for i in range(len(ext)-1))/(len(ext)-1)  # 극값간격=반주기
assert abs(period - fringe) < 15e-9            # Airy 수치 주기 == λ/2n 이론
print(f"[B] Airy R(d) 수치주기={period*1e9:.1f}nm vs 이론 λ/2n={fringe*1e9:.1f}nm")
resid = 200e-9                                  # 잔막 < fringe 주기 → 1주기 미만
assert resid/fringe < 1.0
print(f"[B] 잔막 {resid*1e9:.0f}nm = {resid/fringe:.2f}주기(<1) → 간섭 단독 카운트 불가")

# ── Block C: 패턴밀도 신호 희석 (Lai 2001 eq 6.10[1]) ──
Rcu = 0.943   # Tian 2023 Table1 @650nm[3]
Rox = 0.05    # 유전막 대표 반사율(오더용 예시) — *미검증*
dR = lambda f: f*(Rcu - Rox)                    # 국소 클리어링 신호 = f·(Rcu-Rox)
assert abs(dR(0.1)/dR(0.5) - 0.2) < 1e-9        # 선형 → 저밀도(0.1)는 0.5의 1/5
assert abs((0.5*Rcu+0.5*Rox) - (Rcu+Rox)/2) < 1e-9   # eq6.10 대칭 sanity
print(f"[C] ΔR(f=0.5)={dR(0.5):.3f}, ΔR(f=0.1)={dR(0.1):.3f}, 비={dR(0.1)/dR(0.5):.2f} (5배 희석)")

# ── Block D: 검출 한계 비교 (An NCCAVS[4] vs Tian[3]) ──
eddy_base_min, eddy_opt_min = 3000e-10, 550e-10   # 300nm, 55nm
assert eddy_base_min*1e9 == 300 and abs(eddy_opt_min*1e9 - 55) < 1e-9
assert 30 <= eddy_opt_min*1e9 <= 100              # 개선 와전류 최소도 수십 nm 영역
print(f"[D] 와전류 baseline최소={eddy_base_min*1e9:.0f}nm, 개선최소={eddy_opt_min*1e9:.0f}nm; "
      f"광학 반사 투명화 30-40nm — 금속 EPD 공통 한계 '수십 nm'")
print("ALL PASS")
```

재현 결과: (A) 단파장 비모호 범위 $\lambda/2n=0.333\,\mu$m이 특허의 "약 0.3 µm"와 일치,
두 파장 0.15/0.25 µm 결합범위 0.75 µm=긴쪽의 3배로 특허값 정확히 재현. SiO₂ fringe
주기는 **205.5 nm/주기**(문헌 상수 $n=1.46,\lambda=600$nm로부터 계산한 값). (B) Airy
공식으로 뽑은 $R(d)$의 수치 주기 205.5 nm가 이론 $\lambda/2n$(US4293224[2])과 일치 —
간섭식이 자기 일관됨을 확인했고, 200 nm 잔막은 0.97주기로 1주기 미만이라 간섭 단독으로는 못 센다.
(C) 종점 반사율 변화가 면적분율에 선형($\Delta R\propto f$)이라 $f=0.1$ 저밀도 영역은
$f=0.5$의 1/5 신호 — 이것이 패턴밀도 희석의 정량적 근거다($R_{Oxide}=0.05$는 예시값이라
절대 $\Delta R$은 미검증, 비율만 유효). (D) 와전류 개선 최소두께 55 nm가 광학 반사
투명화 30–40 nm와 같은 수십 nm 영역 — 금속 EPD 전반이 이 영역에서 한계.

## 6. 확인 못 한 것

- **US4293224의 회로/신호 구현 세부**(검출기·복조 방식): 특허 요지의 $\lambda/2n$·
  다파장 논리만 확보. 본 노트는 그 정량 관계만 인용했고 하드웨어 구현은 **미확인**.
- **Rox(유전막 실제 반사율)**: §5 Block C에서 0.05는 오더용 예시값이라 **미검증** —
  희석의 *비율*(선형성)만 검증되고 절대 $\Delta R$ 수치는 재료·파장별 실측 필요.
- **Si의 흡수(k)**: §5 Block B는 $\lambda=600$nm에서 Si의 $k\approx0$로 근사(실제 $k$는
  작지만 0은 아님). 주기(=$\lambda/2n_1$)는 $k$에 무관하나 fringe **진폭/대비**는 영향을
  받는다 — 진폭은 이 노트가 다루지 않았다(주기·모호성만이 초점).
- **An et al. NCCAVS의 정확한 게재연도/권호**: 확장초록(user-group)이라 DOI 없음. 측정
  범위(550–7000 Å)·EPD 윈도우(1.5 mm) 수치는 본문 직접 확인, 서지 완전성은 **미확인**.
- **STI/다층 간섭 EPD의 1차 실측 트레이스**: "Device pattern impact on optical endpoint
  detection by interferometry for STI CMP"(IEEE, 2017) 등은 유료·초록만 노출되어 **인용하지
  않았다**(2차 인용 방지). 패턴 영향은 Lai(2001) 실측으로 대체.

## 출처

1. Jiun-Yu Lai, "Mechanics, Mechanisms, and Modeling of the Chemical Mechanical Polishing
   Process", MIT Ph.D. thesis, Dept. of Mechanical Engineering (2001), Ch.6 "In Situ Sensing
   and Endpoint Detection in Copper CMP". dspace.mit.edu/handle/1721.1/8860 (오픈, 본문 확인:
   `papers/lai2001-mit-thesis-ch6-cu-cmp-endpoint.pdf`, §6.1/§6.2.1 eq(6.10)/§6.4 직접 확인).
   학위논문(가중 0.7).
2. US 4,293,224, "Optical system and technique for unambiguous film thickness monitoring",
   IBM Corp., 등록 1981-10-06. https://patents.google.com/patent/US4293224 (본문 확인:
   FreePatentsOnline 미러 https://www.freepatentsonline.com/4293224.html — λ/2n 주기·
   다파장 비모호범위 문단 직접 확인). 특허(가중 0.9).
3. F. Tian, T. Wang, X. Lu, J. Guo, "Endpoint Detection Based on Optical Method in Chemical
   Mechanical Polishing", *Micromachines* 14(11):2053 (2023), doi:10.3390/mi14112053,
   PMC10673209 (오픈액세스, `papers/pmc10673209-optical-epd.xml`; Cu 반사율 0.943@650nm,
   금속 30–40nm 투명화 — Lv1-1에서 확보한 값 재사용). 1차 논문(가중 1.0).
4. H. An, E. Kim, S. Oh, T. Kim, "Development of Eddy Current Sensor for End-point Detection in
   sub-Micron scale during Cu CMP", NCCAVS user-group 확장초록(Sungkyunkwan Univ.).
   https://nccavs-usergroups.avs.org/wp-content/uploads/2023/01/P10-HAn.pdf (본문 확인:
   `papers/an-nccavs-eddy-current-epd-submicron-cu.pdf`; 측정범위 3000Å→550–7000Å, EPD
   윈도우 1.5mm). 학회 발표자료(가중 0.5).
</content>
</invoke>
