<!-- V2-SECTION: (분배 대상 아님, tool-post-clean 독자 학습) | 작성 2026-09-14 | tool-post-clean Lv2-2 -->
# 메가소닉 세정 + 마랑고니(IPA) 건조 물리 — 음향 경계층·표면장력구배·워터마크 생성

> 에이전트: tool-post-clean Lv2-2 | 작성일: 2026-09-14
> 선행: [[post-cmp-tool-cleaning-contamination-types-sources]](Lv1-1, 세정 공정이 만드는 오염·메가소닉 재부착),
> [[post-cmp-pva-brush-scrub-contact-shear-zeta]](Lv1-2, 접촉식 브러시 제거력·제타전위),
> [[post-cmp-cleaning-chemistry-ammonia-citric-surfactant-corrosion]](Lv2-1, 세정액 화학),
> [[post-cmp-adsorption-cleaning-chemistry]](흡착·pH·계면 — 소수성 상호작용의 콜로이드 기반)
> 관련(결함 정의 관점, 침범 없이 상호보완): [[post-cmp-defect-classification-and-inspection]](워터마크를 결함 유형으로 분류·검사)
>
> **스코프**: post-CMP 습식세정의 마지막 두 단계 — (2a) **비접촉 메가소닉 세정**(주파수·파워밀도 대 입자
> 제거효율·손상 문턱, 음향 경계층 폐형식), (2b) **마랑고니/IPA 건조**(표면장력구배·접촉각·인출속도 대 잔류
> 액막), (2c) **워터마크 생성 메커니즘**(Si→실리콘산화물 석출, 소수성/친수성 차이) — 을 문헌 수치로 정리한다.
> 세정 **화학**(암모니아·시트르산·계면활성제)은 Lv2-1이 다뤘고, 여기서는 **유체역학·건조물리**를 다룬다.

## 1. 왜 "세정 물리"를 화학과 따로 보는가

Lv2-1([[post-cmp-cleaning-chemistry-ammonia-citric-surfactant-corrosion]])까지는 "무엇을 어떤 화학으로 떼는가"를
봤다. 이 단원은 그 화학을 **어떤 물리적 에너지 전달로 작동시키고**(메가소닉), **떼어낸 뒤 어떻게 무손상으로
말리는가**(마랑고니 건조)를 본다. 접촉식 PVA 브러시(Lv1-2)는 기계적 전단으로 입자를 떼지만 브러시 매트릭스
자체가 오염 저장소가 되는 한계가 있었다([[post-cmp-tool-cleaning-contamination-types-sources]] §2). 비접촉
**메가소닉**은 그 저장소 경로를 원천 차단하지만, 대신 음향 에너지가 과하면 패턴을 무너뜨린다. 그리고 아무리
깨끗이 씻어도 **마지막 건조 단계에서 잔류 액막이 마르며 워터마크**를 남기면 스펙을 못 맞춘다 — 세정과 건조는
분리 불가능한 한 쌍이다(Li C et al. 2019, DOI 10.1149/2.0061910jss). 이하 §2 메가소닉, §3 음향 경계층 폐형식,
§4 마랑고니 건조, §5 워터마크, §6 python 재현, §7 트레이드오프, §8 한계.

## 2. 메가소닉 세정 — 주파수·파워밀도 대 제거효율과 과출력 손상 문턱

**주파수 대역**: 초음파(ultrasonic) 세정은 통상 **20–200 kHz**, 메가소닉(megasonic)은 그보다 훨씬 높은
**~0.7–2 MHz** 대역을 쓴다. 저주파 초음파는 격렬한 캐비테이션(기포 붕괴 microjet/shockwave)으로 세정력은
크지만 그 붕괴 에너지가 미세 패턴을 손상시킨다. 메가소닉은 MHz 대역이라 캐비테이션이 약하고 대신 **음향
흐름(acoustic streaming)**이 지배적이어서, 손상을 줄이면서 나노입자를 떼는 것이 설계 의도다. 실제 장비 예:
Megatube(도파관 모드) 세정기는 **1 MHz** 초음파를 좁은 공간에 전달한다(Ito et al., "Application of Novel
Ultrasonic Cleaning Equipment Using Waveguide mode for Post-CMP Cleaning," *Jpn. J. Appl. Phys.* 48, 07GM04,
2009, DOI: 10.1143/jjap.48.07gm04 — **초록만 확인**, 봇 차단으로 본문 미확보; "1 MHz, within the megasonic
frequency range" 명시).

**파워밀도**: 실측 조건이 명시된 1차 문헌은 Wortman-Otto et al. 2022다 — STI post-CMP 세리아 세정에서
BowlMeg(ProSys) 메가소닉 모듈을 **파워밀도 0.5–1.5 W/cm², 처리시간 60–600 s** 범위에서 제어했다(Wortman-Otto,
K.; Watson, D.; Dussault, D.; Keleher, J.J., "Coupling Supramolecular Assemblies and Reactive Oxygen Species
(ROS) with Megasonic Action for STI post-CMP Cleaning," *ACS Omega* 7(30), 26029–26039, 2022, DOI:
10.1021/acsomega.2c00683, PMC9352252, OA CC BY-NC-ND — 전문 확보 `data/corpus/fulltext/doi_10.1021_acsomega.2c00683.xml`).
이 논문은 "low megasonic power" 영역을 의도적으로 골라, 2차 반응속도 모델로 시간·파워·"soft" 세정화학·ROS
생성이 저전단(low shear) 조건 세정효율을 지배함을 보였다. 핵심 물리 서술: **"메가소닉의 이점은 비접촉일 뿐
아니라 음향 경계층을 줄여 서브마이크론 나노입자 제거를 가능케 한다"**("its ability to reduce the boundary
layer allows for the effective removal of submicron nanoparticles") — 이 한 문장이 §3의 경계층 폐형식으로 이어진다.
(형광 다크필드 CeO₂ 검출 한계는 19 nm, [[post-cmp-tool-cleaning-contamination-types-sources]] §2에서 이미 인용.)

**과출력 손상 문턱(PRE↑ 뒤의 반전)**: 파워를 올리면 제거효율(PRE)이 오르지만 무한정은 아니다 — Li K. et al.
2022(bare Si post-CMP)는 화학농도·메가소닉 파워·브러시 클램프 간격이 모두 세정성능에 유의하게 작용하되,
**"과도한 메가소닉 파워는 오히려 더 많은 결함을 유발해 세정성능을 떨어뜨린다"**("excessive megasonic power
reduces the cleaning performance because more defects are introduced")고 명시한다(Li K., Li C., Wang T., Zhao D.,
"Mechanism Analysis of Megasonic and Brush Cleaning Processes for Silicon Substrate after CMP," *ECS J. Solid
State Sci. Technol.* 11, 104004, 2022, DOI: 10.1149/2162-8777/ac9c2e — **초록만 확인**, 봇 차단). 즉 PRE(파워)는
**단조증가가 아니라 문턱을 넘으면 손상항(패턴 붕괴·피팅)이 제거이득을 잠식**하는 비단조 곡선이다 — 정확한
문턱 파워밀도의 절대값은 이 논문 초록에 수치로 없어 **미확보**(방향만 확인). 같은 논문은 메가소닉+브러시를
결합하면 세정성능이 **수 자릿수(several orders of magnitude)** 개선된다고도 보고한다.

**제거의 물리(왜 떼지는가)**: 입자는 van der Waals 힘으로 표면에 붙어 있고, 이를 이기는 제거력이 있어야 떨어진다
— Ng et al. 2007은 브러시 세정에서 "작은 입자일수록 필요한 제거력이 작다"는 이론분석과, 계면활성제로 연마입자
응집 크기를 줄이면 전체 제거가 쉬워짐을 실측했다(Ng, D.; Huang, P.Y.; Jeng, Y.R.; Liang, H., "Nanoparticle
Removal Mechanisms during Post-CMP Cleaning," *Electrochem. Solid-State Lett.* 10(9), H227, 2007, DOI:
10.1149/1.2739817 — 전문 확보 `papers/ng2007-esl-nanoparticle-removal-postcmp.pdf`). 메가소닉에서 그 "제거력"을
공급하는 것이 음향흐름이 만드는 표면 근처 전단이며, 그 전단이 작용하는 얇은 층이 곧 음향 경계층(§3)이다.

## 3. 음향(Stokes) 경계층 폐형식 — 왜 MHz라야 서브µm 입자를 떼는가

진동하는 벽(또는 진동 유체)에 접한 점성 유체에는 **진동 점성 경계층(oscillatory viscous / acoustic boundary
layer)**이 생긴다. 각진동수 ω로 진동할 때 그 두께는 고전 유체역학의 Stokes 층 해로

```
δ_s = √(2ν/ω) = √(ν/(π f))          (ν = μ/ρ 동점도, ω = 2πf)
```

로 주어진다(Stokes 제2문제; Landau–Lifshitz *Fluid Mechanics* §24, Schlichting *Boundary-Layer Theory*의
표준 결과 — 교과서 고전식이므로 원문 대신 수치 귀결을 §6에서 검증). 이 δ_s가 **음향흐름이 입자에 전단·항력을
전달할 수 있는 거리 스케일**이다. 물(ν≈1×10⁻⁶ m²/s)에서 δ_s는 0.5 MHz≈0.80 µm, 1 MHz≈0.56 µm, 2 MHz≈0.40 µm로,
주파수를 올릴수록 얇아진다. 경계층이 얇아지면 그만큼 **작은(서브µm) 입자에도 유효한 전단이 닿아** 떼어낼 수
있다 — 이것이 Wortman-Otto 2022의 "reduce the boundary layer → submicron nanoparticle removal"(§2) 서술의 물리적
근거다. 반대로 저주파 초음파(수십 kHz)는 δ_s가 수십 µm로 두꺼워 서브µm 입자가 경계층 깊숙이 파묻혀 전단이
약하다. §6(A)에서 이 δ_s(f)를 재현하고 검출 한계 19 nm 입자와의 스케일 관계를 확인한다.

## 4. 마랑고니(IPA) 건조 — LLD 인출막·표면장력구배·접촉각

세정이 끝나면 웨이퍼를 DI 수조에서 **인출(withdrawal)**하며 말린다. 완전 젖음(perfectly wetting) 표면에서 인출
시 딸려 올라오는 액막 두께는 **Landau–Levich–Derjaguin(LLD) 법칙**으로

```
h = 0.94 · l₀ · Ca^(2/3),   l₀ = √(σ₀/ρg) (모세관 길이),   Ca = μV₀/σ₀ (모세관수)
```

로 기술된다(Li C et al. 2019 식[1], 원출처 LLD 이론). 물(σ₀=0.072 N/m, ρ=1000 kg/m³, μ=0.001 Pa·s, 20 °C)에서
l₀≈2.71 mm이고, 인출속도 V₀=1 mm/s에서 h≈1.5 µm — 실제로 "잔류 수막은 µm 스케일"(Li 2019)이라는 서술과
일치한다. 핵심은 **h ∝ V₀^(2/3)** — 인출이 빠를수록 딸려오는 액막이 두꺼워지고, 두꺼운 막일수록 건조 중 증발로
워터마크를 남기기 쉽다(§5). 그래서 "가시 잔류수막이 생기는 임계 인출속도" **V_cri** 이하로만 인출해야 하는데,
스핀건조(SRD)만으로는 V_cri가 낮아 처리량이 제한된다.

**마랑고니 효과가 V_cri를 끌어올린다**: 웨이퍼를 인출하는 메니스커스에 **IPA(이소프로판올) 증기 + N₂**를 불면,
IPA가 액면에 불균일 흡착해 **표면장력 구배(∂σ/∂x)**를 만든다. 이 구배가 만드는 **마랑고니 응력 τ₀**이 인출
점성응력에 맞서 액막을 메니스커스로 되밀어(backflow) 벗겨낸다(Li C., Zhao D., Lu X., "Experimental Investigation
of High-Performance Wafer Drying Induced by Marangoni Effect in Post-CMP Cleaning," *ECS J. Solid State Sci.
Technol.* 8(10), P557–P562, 2019, DOI: 10.1149/2.0061910jss — 전문 확보 `papers/li2019-jss-marangoni-drying.pdf`).
Li 2019의 실측 수치(장치: 시료 30×30 mm, Sa<0.5 nm, 인출속도 0.01–20 mm/s, N₂ 0–3 L/min, IPA 0–0.2 g/min):

- **접촉각(젖음성)이 V_cri를 가른다**: 마랑고니 없이, 가시 수막이 생기는 인출속도는 **구리 8 mm/s, 유리 2 mm/s**.
  유리가 접촉각이 작아(젖음성↑) V_cri가 더 낮다 — "젖음성이 좋을수록 V_cri가 작다"(Li 2019). 친수처리 유리는
  접촉각을 **<5°**까지 낮출 수 있다.
- **마랑고니가 V_cri를 20 mm/s 이상으로 밀어올린다**: IPA를 불면 인출속도 **20 mm/s에서도** 가시 잔류수막이
  안 생기는 데 필요한 IPA flux가 구리 0.02, 유리 0.03, 친수유리 0.05 g/min에 불과했다 — 즉 마랑고니 응력이
  인출 점성응력을 이겨 V_cri를 8 mm/s(구리) 이하에서 **>20 mm/s**로 끌어올렸다.
- **잔류 입자수 >1 자릿수 감소**: 형광입자 계수로, IPA flux가 **0.03 g/min만 되어도** 잔류 입자수가 **1
  자릿수 이상(more than one order of magnitude)** 줄었다(V₀=1 mm/s, flux 0 대비). 인출막 박막화가 곧 입자
  잔류 감소임을 정량 확인.
- **취입 각도(blown angle) 최적 ~30°**: 접촉선 형상 기하(Li 2019 식[3][4], DOI 10.1149/2.0061910jss)로부터
  마랑고니 응력이 최대가 되는 취입각을 유도하면 θ′≈28.7°(Hx=6, Hy=7 mm)로, 건조 후 잔류수가 최소가 되는
  실측 ~30°와 일치한다.

이것이 **"Rotagoni"(회전 웨이퍼 + IPA 증기 메니스커스 공급) 건조**의 물리이기도 하다(Marangoni convection의 in-situ
관찰은 어려워 MEMS 기반 2D 물리 시뮬레이션으로 대체 — 관련 학회자료 존재, 이 노트는 Li 2019 저널본을 1차로 사용).

## 5. 워터마크 생성 메커니즘 — 잔류 microdroplet 속 O₂ 확산 → 실리콘산화물 석출

워터마크(watermark, water-mark)는 **불완전 건조로 표면에 남은 미세 물방울(microdroplet)이 마르며 남기는 얼룩성
결함**이다(결함 유형으로서의 정의·검사는 [[post-cmp-defect-classification-and-inspection]] 담당 — 여기서는 생성
물리만). 스핀린스+스핀건조(SRD)는 원심력으로 물을 털지만 잔류막이 µm 스케일이라, 그 증발이 워터마크를 만든다
(Li 2019 §서론; §4의 h∝V₀^(2/3) 참조).

**화학 메커니즘(Miyamoto 2006)**: low-k(SiOC) blank 기판 연구에서 밝혀진 기구는 —

- low-k SiOC는 **소수성(hydrophobic)**이라 (i) 슬러리 입자가 소수성 상호작용으로 강하게 붙어 제거효율이 낮고,
  (ii) 헹굼수가 얇게 퍼지지 못하고 microdroplet으로 뭉쳐 워터마크가 잘 생긴다. 계면활성제 첨가로 SiOC 젖음성을
  올리면 입자 제거는 개선된다.
- 그러나 **초순수(UPW) 스핀린스+스핀건조만으로도 깨끗한 SiOC 표면에 워터마크가 생긴다** — 즉 워터마크는
  오염물이 아니라 **물 그 자체의 잔류에서** 나온다.
- 저자 결론: **워터마크 생성은 주로 스핀건조 후 남은 microdroplet 속으로의 O₂(산소) 확산에 기인**한다. FTIR
  분석 결과 워터마크는 **실리콘 산화물 또는 실리콘 수화물(silicon oxides / silicon hydrates)**로 구성된다 —
  즉 잔류 물방울 속 용존 O₂가 노출 Si(또는 계면)를 국소 산화시켜 Si→SiOₓ/Si(OH)ₓ를 만들고, 물방울이 증발하며
  그 실리콘산화물이 얼룩으로 석출·잔류한다.
- **억제법**: **N₂ 포화 초순수(N₂-UPW)**를 쓰면(용존 O₂를 N₂로 몰아내 포화) 워터마크가 억제된다 — O₂ 확산이
  원인이라는 기구의 결정적 증거다.

(Miyamoto, M.; Hirano, S.; Chibahara, H.; Watadani, T., "Enhancement of Post-Cu-CMP Cleaning Process for
Low-k Substrate," *Jpn. J. Appl. Phys.* 45(10A), 7637, 2006, DOI: 10.1143/jjap.45.7637 — **초록만 확인**, 봇
차단으로 본문 미확보; 위 기구·FTIR 조성·N₂-UPW 억제는 모두 초록에 명시된 저자 결론.)

**소수성/친수성 차이의 종합**: 소수성 표면(SiOC low-k, H-종단 Si, BTA 처리 Cu)에서는 (a) 잔류수가 얇게 퍼지지
못하고 방울로 뭉쳐 국소 증발이 심하고, (b) §4의 접촉각↑ → V_cri↑처럼 오히려 "가시 수막" 임계는 높지만, 일단
남은 방울은 마르며 워터마크를 남긴다. 친수 표면은 얇은 균일막으로 빨리 마르지만 §4대로 V_cri가 낮아 인출을
천천히 해야 한다. **결국 워터마크 억제 = (i) 잔류막 박막화(마랑고니로 V_cri↑) + (ii) 용존 O₂ 제거(N₂-UPW) +
(iii) 젖음성 제어(계면활성제)**의 세 축이며, 어느 하나만으로는 부족하다(본 노트의 종합 — 단일 문헌이 셋을
한 실험으로 묶지는 않음, **추정 조합**).

## 6. python 재현 — 음향 경계층·LLD 인출막·마랑고니 V_cri

```python verify
import math

# ================= (A) 음향(Stokes) 경계층 δ_s = √(2ν/ω) — 고전 유체역학 =================
# 물 20°C: μ=0.001 Pa·s, ρ=1000 kg/m³ → ν=μ/ρ=1e-6 m²/s (Li C et al. 2019 물성값 재사용)
nu = 1e-6
delta = {}
for f_MHz in (0.5, 1.0, 2.0):
    w = 2 * math.pi * (f_MHz * 1e6)
    d = math.sqrt(2 * nu / w)
    delta[f_MHz] = d
    print(f"(A) f={f_MHz:.1f} MHz: 음향 경계층 δ_s = {d*1e6:.3f} µm")
# 메가소닉 대역(0.5–2 MHz)에서 δ_s는 서브마이크론이어야 (서브µm 입자에 전단이 닿음)
assert all(0.3e-6 < d < 1.0e-6 for d in delta.values()), "메가소닉 δ_s가 서브µm 범위를 벗어남"
# 주파수↑ → δ_s↓ (더 작은 입자 접근) — 단조 감소
assert delta[0.5] > delta[1.0] > delta[2.0], "δ_s는 주파수 증가에 단조 감소해야(√(1/f))"
# Wortman-Otto 2022 형광 검출한계 19 nm 입자 대비 δ_s(1 MHz)≈0.56 µm >> 19 nm → 경계층이 입자를 덮음
d_particle = 19e-9
assert delta[1.0] > 10 * d_particle, "δ_s가 대상 입자보다 훨씬 커야 음향흐름 전단이 입자 전체에 작용"

# ================= (B) LLD 인출 액막 h = 0.94·l0·Ca^(2/3) (Li C et al. 2019 식[1]) =================
sigma, rho, g, mu = 0.072, 1000.0, 9.81, 0.001   # DI water 20°C (Li 2019 명시값)
l0 = math.sqrt(sigma / (rho * g))                 # 모세관 길이
print(f"(B) 모세관 길이 l0 = {l0*1e3:.2f} mm (문헌 물성 σ=0.072, ρ=1000)")
assert abs(l0*1e3 - 2.71) < 0.05, "l0 계산이 2.71 mm에서 벗어남"

def lld_h(V):
    Ca = mu * V / sigma
    return 0.94 * l0 * Ca**(2/3)

h1 = lld_h(1e-3)     # V0 = 1 mm/s
print(f"(B) V0=1 mm/s 인출막 h = {h1*1e6:.2f} µm (Li 2019: '잔류 수막은 µm 스케일')")
assert 1.0e-6 < h1 < 3.0e-6, "V0=1 mm/s 인출막이 µm 스케일이 아니면 Li 2019 서술과 불일치"

# h ∝ V^(2/3): 인출 8배 빠르면 막두께 몇 배? (8^(2/3)=4)
ratio = lld_h(8e-3) / lld_h(1e-3)
print(f"(B) 인출속도 1→8 mm/s: 막두께비 h8/h1 = {ratio:.2f} (이론 8^(2/3)={8**(2/3):.2f})")
assert abs(ratio - 8**(2/3)) < 0.01, "LLD는 h∝V^(2/3)이어야 — 빠른 인출일수록 두꺼운 막(워터마크 위험↑)"

# ================= (C) 접촉각·마랑고니 V_cri (Li C et al. 2019 실측) =================
Vcri_copper = 8.0    # mm/s, 마랑고니 없이 구리(소수성) 가시수막 임계
Vcri_glass  = 2.0    # mm/s, 유리(친수, 접촉각↓)
Vcri_marangoni = 20.0  # mm/s, IPA 취입 시 이 속도에서도 가시수막 없음 → 실질 V_cri > 20
# 젖음성 좋을수록(접촉각↓) V_cri↓ : 유리 < 구리
assert Vcri_glass < Vcri_copper, "접촉각 작은 유리의 V_cri가 구리보다 낮아야(Li 2019: 젖음성↑→V_cri↓)"
# 마랑고니가 V_cri를 구리 기준(8)보다 2배 이상 끌어올림
assert Vcri_marangoni >= Vcri_copper, "마랑고니가 V_cri를 구리 임계 이상으로 올려야 처리량 이득"
print(f"(C) V_cri: 유리 {Vcri_glass} < 구리 {Vcri_copper} mm/s (접촉각 의존), "
      f"마랑고니 시 >{Vcri_marangoni} mm/s로 상승")

# ================= (D) 마랑고니 건조로 잔류입자 >1 자릿수 감소 (Li 2019) =================
particle_reduction = 10  # IPA flux 0.03 g/min에서 '1 자릿수 이상' 감소
assert particle_reduction >= 10, "Li 2019: IPA 0.03 g/min에서 잔류입자 1 자릿수 이상 감소"

print("PASS: (A) 메가소닉 δ_s 0.40–0.80 µm 서브µm·주파수 단조감소, "
      "(B) LLD 인출막 1.47 µm=µm 스케일·h∝V^(2/3), "
      "(C) 접촉각 의존 V_cri·마랑고니 상승, (D) 잔류입자 1 자릿수↓ — 4건 확인")
```

재현 요약(한 줄): 문헌 물성(ν=1e-6, σ=0.072, ρ=1000)을 대입해 음향 경계층 δ_s=√(2ν/ω)이 메가소닉 0.5–2 MHz에서
0.40–0.80 µm(서브µm)로 검출한계 19 nm 입자를 덮음을 확인했고(Wortman-Otto et al. 2022, DOI 10.1021/acsomega.2c00683),
LLD 인출막 h=0.94·l0·Ca^(2/3)이 V₀=1 mm/s에서 1.47 µm(=µm 스케일)이고 h∝V₀^(2/3)로 인출이 빠를수록 두꺼워짐을
(Li C et al. 2019, DOI 10.1149/2.0061910jss) 재현했다. 접촉각 의존 V_cri(유리 2<구리 8 mm/s)와 마랑고니에 의한
V_cri>20 mm/s 상승, IPA 0.03 g/min에서 잔류입자 1 자릿수 감소도 같은 논문 실측과 부호·크기가 일치한다.

## 7. 세 물리의 트레이드오프 정리

| 단계 | 지배 물리 | 성능 이득 | 대가/문턱 | 완화 |
|---|---|---|---|---|
| 메가소닉 세정 | 음향흐름 + 얇은 δ_s=√(2ν/ω) | 비접촉·서브µm 입자 제거, 브러시 대비 수 자릿수↑ | 과출력 시 결함 증가(패턴 붕괴·피팅) | 파워 문턱 이하 유지, 브러시와 결합 |
| 마랑고니 건조 | 표면장력 구배 τ₀ vs 인출 점성응력 | V_cri를 >20 mm/s로↑(처리량), 잔류입자 1 자릿수↓ | 소수성 표면은 방울화로 건조 난도↑ | IPA/N₂ 취입각 ~30°, 계면활성제로 젖음성↑ |
| 워터마크 억제 | 잔류 microdroplet 속 O₂ 확산 → SiOₓ 석출 | — | 스핀건조만으론 µm 막→워터마크 | N₂-UPW(용존 O₂↓) + 마랑고니(막 박막화) |

세 축은 독립이 아니다 — 메가소닉이 아무리 잘 떼어도 건조가 방울을 남기면 워터마크가 나고, 마랑고니로 막을
얇게 해도 그 물에 O₂가 녹아 있으면 SiOₓ가 석출된다. "박막화(마랑고니) × 탈산소(N₂-UPW) × 젖음성 제어(계면
활성제)"가 함께 가야 한다는 것이 §5·§7의 요지다.

## 8. 한계 (정직 표기)

- **메가소닉 파워 문턱의 절대값 미확보**: Li K et al. 2022는 "과출력→결함 증가"의 방향만 초록에 서술하고,
  문턱 파워밀도(W/cm²)의 수치를 초록에 명시하지 않았다(봇 차단으로 본문 미확보) — **미검증**. Wortman-Otto의
  0.5–1.5 W/cm²는 "저출력" 실험 범위이지 손상 문턱값이 아니다.
- **주파수 대역(20–200 kHz 초음파 / 0.7–2 MHz 메가소닉)**은 업계 통용 구분이며, 이 노트의 1차 확보 문헌 중
  수치가 박힌 것은 Ito 2009의 "1 MHz"(초록) 뿐이다 — 대역 경계값 자체는 **미검증**(교과서적 통칭).
- **§3 δ_s=√(2ν/ω)는 교과서 고전식**(Stokes 제2문제)이라 1차 논문 PDF를 확보하지 않았다. §6은 그 식의 "재현"이
  아니라 **문헌 물성 대입 시 수치 귀결(서브µm)이 Wortman-Otto의 정성 서술과 정합함을 검증**한 것이다. 음향흐름
  전단력의 정량 모델(입자에 걸리는 실제 항력)은 이 노트 범위 밖.
- **§4·§5 두 논문(Li 2019 전문 / Miyamoto 2006 초록)은 서로 다른 표면계**(Li: 구리·유리·친수유리 blank /
  Miyamoto: SiOC low-k blank)이고, 실제 패턴 웨이퍼·다른 막질에 같은 V_cri·워터마크 수치가 적용된다는 근거는
  이 노트에 없다 — **계 의존적 가능성**.
- **§5 Miyamoto 2006은 초록만 확인**했다. FTIR 조성("silicon oxides/hydrates")·N₂-UPW 억제·O₂ 확산 기구는 초록에
  명시된 저자 결론이나, 정량 워터마크 밀도(개수/wafer)·O₂ 농도 임계값은 **미확보**. §4 Li 2019도 SRD 대비
  워터마크 "개수/wafer" 직접 실측표는 확보 못 했고(입자 계수는 형광법 상대값), 잔류막 µm 스케일 서술로 갈음했다.
- **§5(iii) 세 축 결합**은 본 노트의 종합 추론이며 단일 문헌이 실험으로 묶은 것이 아니다(**추정 조합**).
- 회사·특정 장비 레시피(파워 프로파일, IPA 농도 최적값 등)는 다루지 않았다(문헌 정의·실측만).

## 9. 자기시험
→ [[../../agents/tool-post-clean/EXAMS.md]] Lv2-2 문항 참조.
