<!-- V2-SECTION: R5-wafer | 공동: R2-slurry | 근거: STI, nitride loss, erosion, overpolish window, nitride budget | 정본: ARCHITECTURE-V2.md §3 -->
# STI 나이트라이드 손실·침식(erosion)과 오버폴리시 윈도우 — 선택비를 "나이트라이드 예산"으로 번역 (Lee 2002 식 2.56)

> film-nitride Lv2-1 | 작성일: 2026-09-11
> 선행(부모·자기): [[../materials/film-nitride-selectivity-ceria-chemistry]] (Lv1-2 — 선택비 3단 위계·흡착 포화-스위치. 여기서는 그 선택비 s가 **나이트라이드가 얼마나 깎이는가**로 번역된다),
> [[../materials/film-nitride-lpcvd-pecvd-properties-cmp]] (Lv1-1 — 정지층 막질·나이트라이드 두께)
> 형제(디싱 관점, 중복 금지): [[sti-cmp-ceria-high-selectivity-nitride-stop-dishing]] (film-oxide Lv2-2 — 같은 Lee 2002 모델을 **트렌치 옥사이드 디싱 D_ss** 각도로 다룸. 이 노트는 **나이트라이드 침식 E(t)·손실 예산·오버폴리시 창** 각도로 상보한다),
> 관련: [[preston-luo-dornfeld-mrr]] (K = Kp·P·V), [[ild-cmp-planarization-global-local-density]] (Phase 1 유효밀도 모델), [[pattern-metrics-dishing-erosion-stepheight]] (침식·디싱 정의·기준면), [[pattern-dependent-dishing-erosion]] (removal-rate diagram 틀), [[npw-ptw-transfer-rules-quantitative]] (블랭킷→패턴 전이), [[../materials/hertz-gw-contact-mechanics]] (up 영역 국소압 증폭)

## 1. 왜 이 단원이 필요한가 — "정지"의 실체는 나이트라이드 손실 예산이다

Lv1-2까지의 결론은 "세리아+사이트차단 첨가제 = 선택비 100~290:1"이었다. 그러나 **블랭킷 선택비가 크다고 나이트라이드가
안 깎이는 게 아니다.** 나이트라이드 정지층이 드러난 뒤에도 오버폴리시가 계속되는 동안 활성영역 나이트라이드는 **침식
(erosion)** 으로 얇아진다. 이 나이트라이드 손실이 소자 신뢰성의 급소다 — Lee 2002는 "필드 옥사이드가 실리콘보다 낮게
파이면 활성영역 측벽이 노출돼 측벽·에지 기생전도, 게이트 산화막 고전계, 문턱전압 저하가 생긴다"고 명시한다(Lee 2002 p.31,
Nagai [25] 인용). 그래서 현업은 **나이트라이드 손실 예산(nitride loss budget, 예: 200 Å)** 을 정하고 그 안에 머무는 것을
정지의 실제 정의로 삼는다(Lee 2002 p.185, "A nitride loss budget of 200 A is used to determine points of potential device
failure").

형제 노트(film-oxide)는 같은 Lee 2002 모델을 **디싱 D_ss** 로 풀었다. 이 노트는 각을 바꿔 **나이트라이드 침식 E(t)** 를
정면으로 다루고, 선택비 s가 어떻게 **정상상태 나이트라이드 손실률 K_ss** 와 **허용 오버폴리시 창** 으로 번역되는가를
정량화한다. 핵심 명제는 Lee 2002 본문에 직접 있다:

> "The low blanket nitride removal rate of the high-selectivity slurry results in **improved erosion (but worse dishing)**
> relative to a conventional STI CMP process. This indicates that this process may **allow for a greater overpolish window
> given a particular nitride loss budget**." (Lee 2002 p.114, §3.6)

즉 **고선택비의 진짜 값어치는 디싱 감소가 아니라(디싱은 오히려 악화) 나이트라이드 손실 예산 대비 오버폴리시 창의 확대**다.

## 2. 출처 (6건, 1차 4건)

- **[L] Brian Lee, "Modeling of Chemical Mechanical Polishing for Shallow Trench Isolation," Ph.D. thesis, MIT EECS, May 2002
  (지도 D. Boning).** MIT DSpace hdl 1721.1/29907, 원문 PDF(`papers/lee2002-mit-thesis-sti-cmp-modeling.pdf`, 201쪽). 이 노트가
  **새로 판독한 페이지**: 침식·디싱 정의와 소자 실패 기전(p.31·32), 침식식 유도(§2.6 식 2.54-2.56, p.59-60), 나이트라이드 손실
  예산·오버폴리시 창 명제(p.114), 세리아 HSS 표 3.9·3.10(p.119-120)과 "고선택비 세리아도 통상 공정과 비슷한 침식/디싱" 결론
  (p.121), 나노토포그래피 기반 200 Å 예산 소자실패 맵(p.185·189). 학위논문(가중치 0.7).
- **[J] Joy M. Johnson, "Modeling of Advanced Integrated Circuit Planarization Processes: eCMP, STI CMP using Non-Conventional
  Slurries," S.M. thesis, MIT EECS, June 2009 (지도 D. Boning).** 원문 PDF(`papers/johnson2009-mit-thesis-ecmp-sti-nonconventional-slurry.pdf`,
  99쪽). Lee 2002 후속 Boning 그룹 연구. **새 1차 출처.** 2장 "Evolution of Pattern-Density Die-Level CMP Model for STI"의 **시간에 따라
  변하는 유효밀도(evolving pattern-density)** 개념(§2.2.2, p.47-51)과 STI 스택(나이트라이드 1190 Å, 트렌치 5500 Å, 오버버든 550 Å,
  p.54)·요구사항("high selectivity to stop on nitride, low erosion of the nitride, low dishing", p.18)을 인용. 학위논문(가중치 0.7).
- **[D] P. R. Dandu Veera, S. Peddeti, S. V. Babu, "Selective CMP of Silicon Dioxide over Silicon Nitride for STI Using Ceria
  Slurries," *J. Electrochem. Soc.* 156(12) H936-H943 (2009). DOI: 10.1149/1.3230624.** 1차 논문, 원문 완독
  (`papers/dandu2009-jes-selective-sio2-sin-ceria-sti.pdf`). Fig.14의 "나이트라이드 30 s에 3 nm 후 정지"(자기정지 극한) 인용.
- **[M] J. C. Mariscal et al., "Tribological, Thermal and Kinetic Characterization of SiO₂ and Si₃N₄ Polishing for STI CMP on
  Blanket and Patterned Wafers," *ECS J. Solid State Sci. Technol.* 9, 044008 (2020). DOI: 10.1149/2162-8777/ab89bc.** 1차 논문,
  원문 완독(`papers/mariscal2020-jss-sio2-si3n4-sti-kinetic.pdf`). 패턴 클리어 시각의 다이내 퍼짐(저밀도 먼저 열림→오버폴리시).
- **[S] R. Srinivasan, P. V. R. Dandu, S. V. Babu, "Shallow Trench Isolation CMP: A Review," *ECS J. Solid State Sci. Technol.*
  4(11) P5029-P5039 (2015). DOI: 10.1149/2.0071511jss.** CC-BY 리뷰(가중치 0.6), 원문 완독. 정지층 <1 nm/min 기준·나이트라이드
  손실 관점. 리뷰가 인용하는 Merricks(자기정지)·Lim(입경)·Seo(밀도별 디싱)는 **2차 인용**.
- **[U] N. D. Urban (Ferro), "High Selectivity Ceria Slurry for Next Generation STI CMP," AVS CMP Users Group, 2016-04-07.**
  벤더 슬라이드(가중치 0.5, `papers/urban2016-cmpug-ferro-high-selectivity-ceria-sti.pdf`). slide 8 "narrow nitride = large
  nitride loss, low density = both" — **미검증**, 경향만.

## 3. 침식(E) vs 디싱(D) — 정의와 나이트라이드 손실이 나쁜 이유 (Lee 2002 p.31, Fig.1.11)

- **침식 E(t)** = 특정 지점의 나이트라이드 제거량 = (CMP 전 나이트라이드 두께) − (CMP 후 나이트라이드 두께). 양(+)이 제거.
  = **활성영역(up) 나이트라이드 손실.**
- **디싱 D(t)** = 트렌치 옥사이드 표면과 활성영역 나이트라이드 사이의 단차. 양(+)이면 트렌치 옥사이드가 나이트라이드보다 낮음.
  = **필드(down) 옥사이드 손실.** ([[pattern-metrics-dishing-erosion-stepheight]]의 정의와 동일 기준면.)
- **왜 나이트라이드 손실이 문제인가**: (i) 나이트라이드는 후속 습식 스트립의 두께 마진이자 활성영역 높이 기준이라, 과도한
  침식은 활성영역 상단을 깎아 트랜지스터 채널 폭·소자 높이를 흐트린다. (ii) 침식이 밀도별로 다르면(§5) 다이내 활성영역 높이가
  들쭉날쭉해진다. (iii) 미래세대로 갈수록 나이트라이드 침식 예산이 줄어 나노토포그래피 민감도가 커진다(Lee 2002 p.189
  "As nitride erosion budgets in STI CMP decrease with future technology generations, the effect of nanotopography on nitride
  thinning will become more of a concern").
- 나이트라이드가 깎이는 경로는 Lv1-1/Lv1-2대로 **직접 연마가 아니라 가수분해된 서브옥사이드층의 기계 제거**(Si₃N₄+6H₂O→3SiO₂+4NH₃)
  이므로, 첨가제가 가수분해를 막으면 침식률 자체가 낮아진다. 즉 §4의 K_nit(블랭킷 나이트라이드율)이 화학으로 결정된다
  ([[../materials/film-nitride-selectivity-ceria-chemistry]] §4).

## 4. 나이트라이드 손실 = 침식식 E(t) (Lee 2002 §2.6, 식 2.54-2.56)

나이트라이드 노출 시각 t_n(터치다운, 식 2.50-2.53) 이후, 활성영역(up=nitride)·필드(down=trench oxide)가 함께 깎이는
2물질 단계다. Preston 가정 하 선택비 s = K_ox/K_nit, K_nit = K/s. 단차 H(=디싱)가 커지면 압력이 up으로 몰려 나이트라이드
제거율이 오른다([[../materials/hertz-gw-contact-mechanics]] 국소압 증폭). 침식식은 제거량 방정식에서 유도된다:

  **E(t) = K_ss·(t − t_n) + (h_n − D_ss)·(1−ρ)/(1+ρ(s−1))·(1 − exp(−(t − t_n)/τ_nit))**    (식 2.56)

  K_ss = K / (1 + ρ(s−1))    (정상상태 제거율 = 정상상태 나이트라이드 손실률, 식 2.33)
  D_ss = d_max·ρ(s−1)/(1+ρ(s−1)) = K·τ_nit·(s−1)/s    (정상상태 디싱, 식 2.32·2.49)
  τ_nit = τ₂/(1+(s−1)ρ)    (식 2.48), d_max = K·τ₂/(s·ρ) (식 2.47)

여기서 ρ = 나이트라이드(활성영역) 유효밀도, h_n = 노출 시각의 단차. 구조를 읽으면:

1. **E(t)는 시간에 대해 선형항 + 과도항**이다. 오래 오버폴리시하면 **점근 기울기가 정확히 K_ss**(선형 누적). 즉 **정상상태
   나이트라이드 손실률 = K_ss = K/(1+ρ(s−1))**. §7 [A]에서 제거량 방정식(식 2.34) 수치적분이 식 2.56을 재현하고 점근 기울기가
   K_ss임을 확인.
2. **과도항 부호는 음(−)** (h_n=0 기준): 노출 직후에는 디싱이 아직 안 쌓여 압력집중이 없어 침식이 선형보다 **느리게** 시작하고,
   τ_nit 시정수로 정상상태 손실률 K_ss에 수렴한다(§7 [A]: offset ≈ −30 Å).
3. **정상상태 손실률 K_ss = K/(1+ρ(s−1))는 블랭킷 나이트라이드율 K_nit = K/s보다 크다** — up 영역 압력 집중 때문. ρ=0.5·s=10이면
   K_ss = K/5.5 = 0.18K 로 블랭킷율 0.1K의 **1.8배**. 저밀도일수록 K_ss → K_nit/ρ 로 더 커진다(§5).
4. **핵심 트레이드오프(Lee 2002 §2.7.2 명시)**: "A higher selectivity **decreases the steady-state removal rate and increases
   the steady-state dishing**." s↑ → K_ss↓(나이트라이드 손실률 감소, 좋음) 이지만 동시에 D_ss↑(디싱 악화). 나이트라이드를 지키면
   트렌치가 파인다.

## 5. 나이트라이드 손실의 패턴밀도·피처크기 의존 — "좁은 나이트라이드가 가장 많이 잃는다"

- **밀도 의존**: K_ss = K/(1+ρ(s−1))는 저밀도(ρ 작음)에서 커진다. s가 크면 K_ss → K_nit/ρ 로, ρ=0.1이면 블랭킷율의 10배로
  나이트라이드가 깎인다. Lee 세리아 HSS 실측(표 3.9, 7 psi/30 rpm)에서 정상상태 나이트라이드 손실률은 **ρ=0.5/0.7/0.9 =
  1367/903/465 Å/min**, 노출 직후 초기율 K_n1 = **1902/903/465 Å/min**(§7 [C])로, **저밀도 활성영역이 몇 배 더 빨리 손실**된다.
  표 3.10의 지수 적합 K_ss = 4784·exp(−ρ/0.40) Å/min은 이 밀도 의존을 폐형으로 준다 — ρ=0.2면 2902 Å/min로 ρ=0.9(504)의
  **5.8배**. Urban 2016 slide 8 "narrow nitride = large nitride loss, low density = both"(벤더, 미검증)와 방향 일치.
- **표 3.9의 함의(핵심)**: 세리아는 **블랭킷 선택비가 100:1 이상**인데도(Lv1-2) 표 3.9의 패턴 손실률은 수백~천 Å/min이다.
  이는 **패턴 웨이퍼의 유효(Phase-2) 선택비가 블랭킷보다 훨씬 낮음**을 뜻한다(K_ss=K/(1+ρ(s−1))로 역산하면 s가 한 자릿수).
  Lee 2002 p.121은 이를 실측으로 확인한다: "the high-selectivity ceria slurry results in **similar erosion and dishing
  results as a conventional STI CMP process**." **블랭킷 선택비 ≠ 낮은 나이트라이드 손실.** ([[npw-ptw-transfer-rules-quantitative]]
  의 블랭킷→패턴 선택비 하락 경고와 정합.)
- **피처크기 의존**: Lee 2002 §3.7(p.115, Lee [79] 인용)은 "실리카 슬러리는 평탄화율이 **피처 밀도**에 의존, 세리아는 **피처
  크기·단차 높이**에 의존"이라 한다. 세리아의 down-area 입자 포획(Jouty/Kwon [77][80], 2차)이 큰 피처에서 다르게 작동하기
  때문. 따라서 세리아 STI의 나이트라이드 손실은 단순 밀도만이 아니라 피처크기의 함수다 — 서브µm 좁은 활성영역이 취약.
- **시간에 따라 변하는 유효밀도(Johnson 2009 §2.2.2)**: 증착 프로파일이 수직이 아니라 경사(bias)라, 폴리시로 단차가 줄면
  **국소 옥사이드 유효밀도가 오른다**(70-100 µm 피처: ρ 0.487→0.5, 작은 피처는 더 크게 변함, Johnson 2009 p.48 Fig.2-14).
  나이트라이드 노출 시각 t_n과 그 뒤 손실률이 이 진화하는 밀도에 좌우되므로, **정적 ρ 가정은 좁은 피처의 손실을 틀리게
  예측한다**(Johnson 2009은 이 진화밀도 모델로 RMS 오차 4% 감소).
- **다이내 손실 비균일**: 나이트라이드 터치다운 t_n이 다이 전체에서 ~40 s 퍼진다(저밀도가 먼저 열림; [[sti-cmp-ceria-high-selectivity-nitride-stop-dishing]]
  §3, Mariscal 2020 패턴 클리어 5→6 min). 전체 클리어까지 폴리시하면 **먼저 열린 저밀도 영역은 이미 40 s+ 오버폴리시** 상태라
  손실이 몰린다 — Lee 2002 p.185의 200 Å 예산 소자실패 맵이 나노토포그래피 "high spot"(먼저 접촉)과 강하게 상관하는 이유.

## 6. 선택비 → 나이트라이드 손실 예산 → 오버폴리시 창 (이 노트의 결론)

정상상태 뒤 나이트라이드 침식은 K_ss로 선형 누적된다. 손실 예산 E_max(예: 200 Å, Lee 2002 p.185)에 대해 허용 오버폴리시 시간
Δt_op는 식 2.56을 E=E_max로 풀어 얻는다(과도항 포함):

  E_max = K_ss·Δt_op + (h_n − D_ss)·(1−ρ)/(1+ρ(s−1))·(1 − exp(−Δt_op/τ_nit))

- **s↑ → K_ss↓ → Δt_op↑.** §7 [B]: K=2000 Å/min·ρ=0.5·예산 200 Å에서 s=10이면 창 **37.8 s**, s=100이면 **304 s** — **8.0배**
  확대(과도항 포함). 과도항을 무시한 순수 K_ss 비는 9.18배(형제 노트 §6-4 값). 과도항이 s=10 쪽 창을 상대적으로 더 늘려
  실제 배율이 조금 작다 — **형제 노트의 단순 추정을 과도항까지 넣어 정밀화**한 결과.
- **이것이 고선택비의 진짜 값어치**다(Lee 2002 p.114). 디싱은 s와 함께 악화되므로(§4-4), 고선택비는 "덜 파이는" 슬러리가
  아니라 "**나이트라이드 예산을 덜 쓰며 더 오래 오버폴리시할 수 있는**" 슬러리다. 다이내 t_n 퍼짐(40 s)을 흡수하려면 이 창이
  넓어야 하므로, 선택비의 실용 목적은 **클리어 비균일 흡수**다.
- **대안: 자기정지(self-stopping) 슬러리**. 예산을 늘리는 또 다른 길은 K_ss를 낮추는 게 아니라 **침식을 아예 포화시키는** 것.
  Dandu 2009 Fig.14는 세리아+피리딘에서 나이트라이드가 **첫 30 s에 자연산화층 3 nm만 깎이고 200 s까지 추가 손실 0**(실효
  <1 nm/min, §7 [D])임을 보인다 — 침식 E가 ~30 Å에서 포화하므로 **오버폴리시 시간과 무관하게 예산 안**. Nojo(2차, Lee 2002
  p.115 Fig.3.15)의 임계압력형 세리아(≈70 kPa 이하 RR≈0)도 같은 사상이며, Merricks(2차, Srinivasan 2015)의 아미노산 슬러리는
  노출 후 ~6 s면 옥사이드·나이트라이드 모두 1:1로 멈춰 오버폴리시 무해. **이상적 STI 슬러리는 "고선택비"가 아니라 "노출 후
  자기정지"** — Lee의 선형 K_ss 누적 모델과 달리 침식이 상한을 갖는다(§7 [D] 대조).

## 7. 검증 — 침식식·오버폴리시 창 재현 (```python verify```, 실제 실행)

**재현 요약(한 줄)**: Lee 2002 식 2.56 침식식이 제거량 방정식(식 2.34) 수치적분과 일치(점근 기울기 = K_ss = 364 Å/min,
과도 offset −30 Å), 나이트라이드 손실 예산 200 Å의 오버폴리시 창이 s=10→100에서 37.8 s→304 s(8.0배)로 넓어지고, 세리아 HSS
손실률 K_ss=4784·exp(−ρ/0.40)이 표 3.9(1367/903/465 Å/min)를 ±9% 재현하며 저밀도서 K_ss→K_nit/ρ, 자기정지(Dandu Fig.14)는
침식이 30 Å에서 포화해 창이 사실상 무한임을 대조 (Lee 2002 hdl 1721.1/29907; Dandu 2009 DOI 10.1149/1.3230624) — 아래 4블록 PASS.

```python verify
# [A] Lee 2002 침식식 E(t) (식 2.56) = 제거량 방정식(식 2.34) 수치적분 재현; 점근 기울기 = K_ss (hdl 1721.1/29907)
import math
K = 2000.0/60.0                                   # Å/s (§2.12 예시값)
s, tau2, rho = 10.0, 60.0, 0.5
dmax  = K*tau2/(s*rho)                             # 식 2.47 -> 400 Å
tau_n = tau2/(1+(s-1)*rho)                         # 식 2.48 -> 10.91 s
Dss   = K*tau_n*(s-1)/s                            # 식 2.49 -> 327 Å
Kss   = K/(1+rho*(s-1))                            # 식 2.33 (정상상태 나이트라이드 손실률)
hn = 0.0                                           # 노출 시각 단차(기준: 평탄 노출)
H   = lambda dt: (hn-Dss)*math.exp(-dt/tau_n)+Dss                     # 식 2.54 디싱
RRa = lambda h: (K/s)*(1/dmax)*((1-rho)/rho)*h + K/s                  # 식 2.34 활성영역(nitride) 제거율
Ecl = lambda dt: Kss*dt + (hn-Dss)*(1-rho)/(1+rho*(s-1))*(1-math.exp(-dt/tau_n))  # 식 2.56
# 제거량 방정식 수치적분: E(t)=∫ RRa(H) dt  (노출 t_n부터)
E, ddt, E20 = 0.0, 0.001, None
for i in range(int(60/ddt)):
    t = i*ddt; E += ddt*RRa(H(t))
    if abs(t-20.0) < ddt/2: E20 = E
assert abs(Ecl(0.0)) < 1e-9                        # 노출 시각 침식 0
assert abs(E20 - Ecl(20.0)) < 0.02*Ecl(20.0)       # 수치적분 = 폐형 (식 2.56 유도 검증)
slope = (Ecl(600)-Ecl(500))/100                    # 완전 감쇠 구간 점근 기울기
assert abs(slope - Kss) < 1e-6                      # 점근 기울기 = K_ss (선형 누적)
assert Ecl(20.0) < Kss*20.0                         # 과도항 음(-): 초기 침식 < 선형 (압력집중 전)
assert abs(Kss*60 - 363.6) < 0.5                    # K_ss = 364 Å/min = 블랭킷율(K/s=200)의 1.8배
print(f"[A] E(20s)={E20:.1f}Å(폐형 {Ecl(20.0):.1f}); 점근기울기={slope*60:.0f} Å/min=K_ss; 과도offset={Ecl(1e4)-Kss*1e4:.1f}Å")
```

```python verify
# [B] 나이트라이드 손실 예산 -> 오버폴리시 창 (식 2.56을 E=E_max로 해); s=10 vs 100 (예산 200 Å, ρ=0.5)
import math
K, tau2, rho = 2000.0/60.0, 60.0, 0.5
def window(s_, budget=200.0):
    Kss_ = K/(1+rho*(s_-1)); tn_ = tau2/(1+(s_-1)*rho); Dss_ = K*tn_*(s_-1)/s_
    coef = (0.0-Dss_)*(1-rho)/(1+rho*(s_-1))
    dt = budget/Kss_                                          # 과도항 무시 초기 추정
    for _ in range(200):                                     # Newton (과도항 포함 정확해)
        f  = Kss_*dt + coef*(1-math.exp(-dt/tn_)) - budget
        fp = Kss_ + coef*math.exp(-dt/tn_)/tn_
        dt -= f/fp
    return dt
w10, w100 = window(10.0), window(100.0)
assert abs(w10-37.8) < 1.0 and abs(w100-304) < 3            # 창: 37.8 s -> 304 s
assert 7.5 < w100/w10 < 8.5                                  # 과도항 포함 ~8.0배
pure_ratio = (K/(1+rho*(10-1)))/(K/(1+rho*(100-1)))          # 순수 K_ss 비 (과도항 무시)
assert abs(pure_ratio - 9.18) < 0.1                          # 형제 노트 §6-4 단순추정(9.2배)
print(f"[B] 예산 200Å 오버폴리시 창: s=10 {w10:.1f}s, s=100 {w100:.0f}s -> {w100/w10:.1f}배 (순수 K_ss비 {pure_ratio:.1f}배; 과도항이 s=10 창을 늘려 실제 배율↓)")
```

```python verify
# [C] 나이트라이드 손실률의 밀도 의존 (Lee 2002 표 3.9 세리아 HSS 실측 + 표 3.10 지수 적합, p.119-120)
import math
Kss_fit = lambda r: 4784*math.exp(-r/0.40)                  # 식 3.48, Å/min (정상상태 손실률)
Kn1_fit = lambda r: 11573*math.exp(-r/0.28)                 # 식 3.49, Å/min (노출 직후 초기 손실률)
tab39 = {0.5:(1367,1902), 0.7:(903,903), 0.9:(465,465)}     # ρ: (K_ss, K_n1) 실측 Å/min
for r,(kss_m,kn1_m) in tab39.items():
    assert abs(Kss_fit(r)-kss_m)/kss_m < 0.09               # 적합 ±9% (원문 "reasonable fit")
    assert abs(Kn1_fit(r)-kn1_m)/kn1_m < 0.09
assert Kss_fit(0.2)/Kss_fit(0.9) > 5                         # 저밀도 손실률 5배 이상 (좁은 나이트라이드가 취약)
# 큰 s 극한: K_ss = K/(1+ρ(s-1)) -> K_nit/ρ (블랭킷율/밀도)
K = 2000.0
Kss_lim = lambda r,s_: K/(1+r*(s_-1)); Knit = K/100
assert abs(Kss_lim(0.1,100) - Knit/0.1)/(Knit/0.1) < 0.11   # ρ=0.1서 K_ss ≈ K_nit/ρ = 블랭킷율의 10배
# 블랭킷 선택비 100+인데 패턴 K_ss 수백~천 Å/min -> 유효 패턴 선택비는 한 자릿수 (Lee p.121)
s_eff = (K/1367 - 1)/rho_ + 1 if (rho_:=0.5) else None       # K_ss=1367, K=2000 역산
assert 1 < s_eff < 5                                          # 블랭킷 100+ vs 패턴 유효 ~3 (통상공정 수준)
print(f"[C] 세리아 HSS 나이트라이드 손실률 K_ss(ρ=.2/.5/.9)={Kss_fit(0.2):.0f}/{Kss_fit(0.5):.0f}/{Kss_fit(0.9):.0f} Å/min; 패턴 유효선택비 s_eff≈{s_eff:.1f}(블랭킷 100+와 괴리)")
```

```python verify
# [D] 자기정지 슬러리는 오버폴리시 시간과 무관하게 예산 안 (Dandu 2009 Fig.14, DOI 10.1149/1.3230624) vs 선형 K_ss 누적
# 자기정지: 나이트라이드 30 s에 3 nm(자연산화층) 후 200 s까지 추가 제거 0
nitride_selfstop_rate = 3.0/(200/60)                        # nm/min 실효
assert nitride_selfstop_rate < 1.0                          # <1 nm/min (Srinivasan 2015 정지층 기준 충족)
E_selfstop_saturated = 30.0                                 # Å, 침식이 여기서 포화 (오버폴리시 무관)
budget = 200.0
assert E_selfstop_saturated < budget                        # 어떤 오버폴리시든 예산 안 -> 창 사실상 무한
# 대조: Lee 선형 K_ss(세리아 HSS ρ=0.5, 1367 Å/min)는 예산을 빠르게 소진
Kss_linear = 1367.0/60                                       # Å/s
t_budget_linear = budget/Kss_linear                         # s
assert t_budget_linear < 10                                  # 8.8 s만에 200 Å 소진 (자기정지와 대조)
print(f"[D] 자기정지 실효 {nitride_selfstop_rate:.2f} nm/min, 침식 {E_selfstop_saturated:.0f}Å서 포화<예산 {budget:.0f}Å -> 창 무한; 선형 K_ss=1367은 {t_budget_linear:.1f}s만에 예산 소진")
```

**결과 해석(정직하게)**
- [A]는 Lee 식 2.56이 제거량 방정식(식 2.34)의 적분과 수학적으로 일치함을 확인한 것(유도 검증)이지 실험 검증이 아니다.
  절댓값은 §2.12 예시 입력값(K·s·τ₂·ρ)의 함수이며 h_n=0은 "평탄 노출" 이상화다(실제 h_n은 Phase 1B 잔여 단차).
- [B]의 8.0배는 내 유도(예산 200 Å, 과도항 포함). 형제 노트의 9.2배는 과도항 무시 순수 K_ss 비다 — 둘 다 맞고, **과도항을
  넣으면 s=10 쪽 창이 상대적으로 커져 실제 배율이 8.0으로 내려간다**. 예산·ρ·h_n에 따라 값은 달라진다.
- [C]의 표 3.10 적합은 원문 표 3.9를 재계산(±9%). 손실률 절댓값은 7 psi/30 rpm·특정 세리아의 것으로 오더·경향만. s_eff 역산은
  K_ss 정의에 실측 K_ss를 대입한 것으로, 블랭킷 선택비(100+)와 패턴 유효선택비(~3)의 괴리를 드러낸다(Lee p.121 결론과 정합).
- [D]는 Fig.14의 정성 거동(3 nm 후 정지)을 수치화한 것으로 포화값 30 Å은 자연산화층 두께 근사(미검증 절댓값). 요점은 **선형
  누적(K_ss) 모델과 포화(자기정지) 모델의 구조 차이**이지 특정 수치가 아니다.

## 8. 한계·불명확 (정직하게)

- (a) Lee 모델은 최소 피처 10 µm 마스크로 검증됨 — 서브µm 좁은 활성영역의 나이트라이드 손실(입자 down-area 포획·자기정지)은
  모델 밖(Lee 2002 §2.13·§3.7). §5의 피처크기 의존은 Lee [79](2차 인용)의 정성 서술에 근거.
- (b) 표 3.9의 손실률은 **패턴 웨이퍼에서 추출한 유효 파라미터**로, 블랭킷 선택비와 별개다. K_ss·K_n1 절댓값은 우리 툴에
  입력이 아니라 **파라미터 형태**로만 가져온다.
- (c) h_n(노출 시각 단차)을 이 노트는 0으로 두었다 — 실제로는 Phase 1B의 잔여 단차이고 밀도 의존이라, 오버폴리시 창
  절댓값은 h_n 추정에 민감하다(미검증).
- (d) Johnson 2009의 진화밀도 모델은 **옥사이드 단계** 개선(RMS −4%)을 보였고, 나이트라이드 손실(Phase 2)에 대한 정량 개선치는
  본문에서 명시 안 됨 — §5의 "정적 ρ가 좁은 피처 손실을 틀리게 예측"은 개념적 함의로 취급(부분 미검증).
- (e) Urban 2016 slide 8은 벤더 슬라이드 — 방향만, **미검증**.
- (f) 식 2.56의 과도항 부호(음)는 h_n=0 기준의 내 해석이며, h_n > D_ss이면 부호가 뒤집혀 침식이 선형보다 빠르게 시작할 수 있다
  (원문은 h_n 일반형만 제시).

## 9. 이 에이전트의 결론 (나이트라이드 손실 관점, 모델링)

1. **정지의 실체 = 나이트라이드 손실 예산.** 정지층 모델의 출력은 "나이트라이드율 0"이 아니라 **E(t) = 오버폴리시 시간의 함수**이고,
   소자 판정은 E < E_max(예: 200 Å, Lee p.185)로 한다. sim의 STI Phase 2는 D_ss(디싱)뿐 아니라 **E(t)·K_ss(손실률)를 함께 출력**해야 한다.
2. **선택비의 값어치는 디싱이 아니라 오버폴리시 창.** s↑ → K_ss↓ → Δt_op↑(§7 [B], 8배)이되 D_ss↑(§4-4). 즉 고선택비는 "덜 파는"
   게 아니라 "**나이트라이드 예산을 아끼며 클리어 비균일(40 s t_n 퍼짐)을 흡수**"하는 것. 이것이 [[../materials/film-nitride-selectivity-ceria-chemistry]]
   의 선택비 s가 공정통합에서 갖는 실제 의미다.
3. **블랭킷 선택비 ≠ 낮은 나이트라이드 손실.** 패턴 유효(Phase-2) 선택비는 블랭킷보다 훨씬 낮아(세리아 HSS: 블랭킷 100+ vs 패턴
   s_eff≈3, §7 [C]), 손실은 통상 공정 수준일 수 있다(Lee p.121). 캘리브레이션(Cal-1)에서 나이트라이드 손실 보정 파라미터는
   **블랭킷 스펙이 아니라 특성화 마스크에서 추출한 K_ss(ρ)·K_n1(ρ)** 여야 한다.
4. **저밀도·좁은 나이트라이드가 손실 급소.** K_ss → K_nit/ρ (저밀도서 블랭킷율의 여러 배). 손실 예산 판정은 **최저밀도 활성영역**
   에서 먼저 깨진다 — 다이내 t_n 퍼짐과 겹쳐 "먼저 열린 저밀도 영역"에 손실이 몰린다(§5).
5. **자기정지 슬러리는 선형 K_ss 모델을 깬다.** 침식이 포화(Dandu Fig.14, ~30 Å)하면 오버폴리시 창이 사실상 무한 — Lee의 K_ss
   선형 누적 대신 **포화형 침식항**이 필요(향후 구현요청). 이것이 "고선택비"보다 근본적인 나이트라이드 보호다.

## 10. 구현 요청 → agents/film-nitride/PROFILE.md "## 구현 요청" 참조
(Lee 2002 Phase 2 침식식 2.56 + K_ss(ρ)·K_n1(ρ) 밀도의존 + 나이트라이드 손실 예산 판정 E<E_max + 자기정지 포화항 — 상세는 PROFILE.)

## 11. 자기시험
→ [[../../agents/film-nitride/EXAMS.md]] Lv2-1 문항 참조.
