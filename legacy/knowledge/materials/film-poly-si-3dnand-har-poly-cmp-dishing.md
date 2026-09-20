# 3D NAND 응용 — 고종횡비 구조 위 Poly-Si CMP와 디싱 (패턴밀도·선택비·첨가제 의존)

> 에이전트: film-poly-si Lv2-2 | 작성일: 2026-09-12
> 선행: [[film-poly-si-oxide-selectivity-gate-cmp-window]] (Lv2-1 — poly:oxide 선택비의 방향·크기, 오버폴리시 마진 번역식),
> [[film-poly-si-doping-grain-cmp]] (Lv1-1 §4 — 3D NAND에서 poly-Si는 워드라인이 아니라 채널/플러그 재료),
> [[film-poly-si-alkaline-dissolution-ph-kinetics]] (Lv1-2 — 알칼리 화학 용해가 트렌치 바닥 poly도 깎는 이유)
> 관련: [[../cmp/sti-cmp-ceria-high-selectivity-nitride-stop-dishing]] (Lee 2002 2물질 폐형 모델 — 이 노트가 poly/oxide 계로 전이하는 원형),
> [[../cmp/pattern-dependent-dishing-erosion]] (유효밀도·PL·step-height 소멸 두 레짐), [[../cmp/pattern-metrics-dishing-erosion-stepheight]] (dishing·step height 정의),
> [[../cmp/npw-ptw-pattern-effect-gw-physics]] (블랭킷이 패턴을 예측 못 하는 미시 물리), [[hertz-gw-contact-mechanics]] (up 영역 국소압 증폭),
> [[../cmp/preston-luo-dornfeld-mrr]] (K = Kp·P·V — 밀도모델의 블랭킷 항)
> 후속: [[film-poly-si-high-selectivity-lowdefect-slurry]] (Lv3-1 — 여기서 남긴 χ_down 억제인자가 Lagudu 2019의 비-Preston 문턱압력으로 실체화된다)

## 0. 출처 (5건 — 1차 원문 3건, 초록 1건, 형제 노트 경유 1건; 단원 상한 6건 준수)

1. **[특허·전문 확인]** US Patent 10,822,524 B2, "Aqueous compositions of low dishing silica particles for polysilicon
   polishing," Penta, N. K., Van Hanehem, M., Tettey, K. E., Yoshida, K., Yoshida, K. (Rohm and Haas Electronic Materials
   CMP Holdings), 출원 2017-12-14, 등록 2020-11-03 — https://patents.google.com/patent/US10822524B2/en
   (papers/patents/US10822524B2.html, 명세서 전문·표 A–H 직접 판독). 명세서가 **3D-NAND/플래시 메모리 poly CMP**를 대상
   공정으로 명시하고, 패턴밀도(PD) 30/50/70 % 구조에서 **단차(step height)의 시간 변화 = 디싱의 시계열**을 표로 준다.
   특허 수치는 청구범위 확보용이므로 "대표값"이 아니라 **범위·경향**으로만 쓴다(SCOPE.yaml patent 주의사항).
2. **[1차·원문 전체(JATS XML)]** Jia, J. et al. (2023), "Investigation of the Connection Schemes between Decks in 3D NAND
   Flash," *Micromachines* 14, 1779, DOI: 10.3390/mi14091779 — https://doi.org/10.3390/mi14091779
   (data/corpus/fulltext/doi_10.3390_mi14091779.xml). 고종횡비 채널홀 식각 한계 → 다중 덱(dual-deck) 구조 → 덱 사이
   **poly-plug를 CMP로 평탄화**하는 공정 사슬과, 그 CMP 공정 변동이 셀 전류 산포로 번역되는 실측을 준다.
3. **[1차·초록만]** Sorooshian, J., Borucki, L., Timon, R., Stein, D., Boning, D., Hetherington, D., Philipossian, A. (2004),
   "Estimating the Effective Pressure on Patterned Wafers during STI CMP," *Electrochem. Solid-State Lett.* 7(10) G204,
   DOI: 10.1149/1.1785933 — https://doi.org/10.1149/1.1785933 (.paper_txt_cache/essl2004-effective-pressure-patterned-sti__pdf.txt,
   IOP 페이지 초록만 확보·본문 유료). 패턴밀도 10/50/90 %에서 유효압력/인가압력 = 2.2/1.7/1.3.
4. **[학위논문·형제 노트 경유]** B. Lee, "Modeling of Chemical Mechanical Polishing for Shallow Trench Isolation," Ph.D. thesis,
   MIT EECS, 2002, http://hdl.handle.net/1721.1/29907 (papers/lee2002-mit-thesis-sti-cmp-modeling.pdf). 2물질 폐형
   디싱 모델(식 2.32·2.33·2.38·2.46–2.49)은 [[../cmp/sti-cmp-ceria-high-selectivity-nitride-stop-dishing]] §4가 원문에서
   판독·재현한 것을 그대로 가져온다(이 노트는 원문을 다시 읽지 않았다 — **STI(oxide/nitride)→poly/oxide 전이는 E4**).
5. **[1차·원문 전체, Lv1-1 경유]** Lee, J., Yoon, D.-G., Sim, J.-M., Song, Y.-H. (2021), "Impact of Residual Stress on a
   Polysilicon Channel in Scaled 3D NAND Flash Memory," *Electronics* 10(21), 2632, DOI: 10.3390/electronics10212632 —
   3D NAND 채널 스택(macaroni oxide/poly-Si 채널/ONO)과 poly-Si가 최종 소자에 남는 구조 근거([[film-poly-si-doping-grain-cmp]] §4).

**범위 밖으로 뺀 것(찾았지만 제외)**: US7972962B2(GlobalFoundries, 하이브리드 oxide/poly CMP 평탄화)는 로직 게이트 높이
차 평탄화 특허로 3D NAND·디싱 데이터가 없어 제외. US10647887B2(W 버프)는 "3D NAND"를 응용 나열에만 언급해 제외.

## 1. 왜 필요한가 — 3D NAND에서 poly CMP가 놓이는 자리

3D NAND에서 poly-Si는 워드라인이 아니라 **수직 채널(macaroni channel)과 덱 사이를 잇는 poly-plug**다
([[film-poly-si-doping-grain-cmp]] §4, Lee et al. 2021). Jia et al. (2023)은 공정 사슬을 이렇게 요약한다: 적층 수가 늘수록
채널홀 식각 종횡비가 커져 "deep hole etching with a large aspect ratio is difficult to achieve"(채널 기울어짐, 바닥 셀
직경 축소) → 스택을 두 덱으로 나눠 식각 → **"the chemical–mechanical polishing (CMP) process used to flatten the structure
of the lower deck before depositing the upper deck"** → 그 CMP의 공정 변동이 poly-plug 구조 차이를 만든다. 즉 3D NAND의
poly CMP는 (i) 채널홀/플러그를 채운 poly 오버버든을 제거하고 (ii) 산화막(또는 나이트라이드) 정지층에서 멈추되 (iii)
**홀/플러그 안의 poly가 정지층 아래로 파이는 디싱**을 억제해야 한다. US10822524B2 배경기술도 같은 문제를 적는다:
"Conventional slurries do not provide effective stopping on the oxide or nitride stop film; further, the same slurries
cause a significant loss of polysilicon in the trench area or dishing." 그리고 선택비의 존재 이유를 **오버폴리시 마진**으로
못박는다: "to provide an overpolish margin to ensure all pattern densities are cleared of the polysilicon" — Lv2-1 §5의
번역식과 같은 논리다.

디싱이 소자에 무엇을 하는가는 Jia 2023이 실측한다: 같은 적층 수의 1덱 시료 대비 poly-plug로 연결한 2덱 시료에서
채널 포화전류 대표값이 **17 % 감소**하고 **전류 산포가 거의 2배**가 됐고, 원인을 "structure variation of the poly-plug
under process variation"(CMP 포함)의 차폐효과 차이로 귀속한다(원문 §3, Fig.5; TCAD로 교정). 디싱 자체를 nm로 측정한
논문은 아니므로 **디싱 깊이→전류의 정량 전달함수는 이 단원에서 확보하지 못했다**.

## 2. 1차 출처 — US10822524B2: 3D NAND poly CMP 패턴 웨이퍼의 디싱 시계열

### 2.1 시편·공정(명세서 [0063])
Ebara EPO222, 테이블/캐리어 93/87 rpm, 다운포스 207 hPa(3 psi), 슬러리 200 mL/min, VP5000 패드 + SP2310 서브패드,
ex-situ 컨디셔닝. 패턴 웨이퍼(PolySi MIT864, poly/SiO₂/Si): 다이 25구획, PD 0–100 %(10 % 간격)와 피치 1 µm–1 mm.
**poly 두께 ~6000 Å, 초기 단차 ~1800–2000 Å.** 정의: PD = 트렌치가 아닌 면적 비율(= 정지층 up 영역 분율),
SH = (oxide+poly) 두께(비트렌치) − (oxide+poly) 두께(트렌치). 따라서 **정지층 노출 후 SH가 다시 커지는 것이 곧
트렌치 poly 디싱**이다(명세서 [0065]: "step height initially decreases as the surface is planarized and then increases
once the underlying stop layer is exposed and removal of polysilicon continues in the trench").

### 2.2 표 A — 블랭킷 제거율·선택비(실리카 1.5 wt%, pH 10–10.5, 알콕실화 디아민 3.75 ppm)
| 예 | 염기(적정제) | poly RR (Å/min) | TEOS RR (Å/min) | poly:TEOS |
|---|---|---|---|---|
| 1-1* (비교, 디아민 0) | NH₄OH | 4000 | 42 | 97 |
| 1-2 | NH₄OH | 4278 | 62 | 69 |
| 1-3 | 에탄올아민 | 5182 | 18 | 290 |
| 1-4 | 디에탄올아민 | 3388 | 5 | 686 |
| 1-5 | 디부틸아민 | 3825 | 2 | 1832 |
| 1-6 | TEAH | 3049 | 2 | 1601 |
| 1-7 | TBAH | 1755 | 2 | 1150 |

명세서 목표 선택비는 "at least 40:1, for example, from 50:1 to 200:1 or, preferably, from 50:1 to 100:1" — **상한을 둔다**는
점이 핵심이다(§3에서 이유가 나온다). §7 (A)에서 poly/TEOS 재계산이 표기 선택비와 5 % 이내(TEOS RR이 "2 Å/min"로
반올림된 1-5/1-6/1-7은 반올림이 오차를 지배, 1-7은 24 % 차이)임을 확인했다.

### 2.3 표 B·C·D — PD 30/50/70 % 구조의 단차(SH, Å) 시계열 (HTML 셀 정렬을 이 노트가 파싱 — 결측 셀은 공란)
| PD | 예 | t=0 | 18–25 s | 36–40 s | 50–54 s | 60 s | 72–80 s | 100 s |
|---|---|---|---|---|---|---|---|---|
| 30 % | 1-1* | 1841 | 681 (18) | 280 (36) | 833 (54) | — | 1007 (72) | — |
| 30 % | 1-2 | 1908 | 493 (25) | 505 (40) | 524 (50) | 557 | 640 (75) | — |
| 30 % | 1-3 | 1852 | 497 (20) | 462 (36) | 977 (50) | 1008 | — | — |
| 30 % | 1-5 | 1841 | 1628 (20) | 1526 (40) | — | 296 | 494 (80) | 1760 |
| 50 % | 1-1* | 1825 | 654 (18) | 247 (36) | 734 (54) | — | 878 (72) | — |
| 50 % | 1-2 | 1895 | 465 (25) | 374 (40) | 510 (50) | 539 | 594 (75) | — |
| 50 % | 1-3 | 1835 | 504 (20) | 483 (36) | 854 (50) | 883 | — | — |
| 50 % | 1-5 | 1853 | 1617 (20) | 1627 (40) | — | 272 | 839 (80) | 1871 |
| 70 % | 1-1* | 1835 | 740 (18) | 299 (36) | 526 (54) | — | 612 (72) | — |
| 70 % | 1-2 | 1891 | 572 (25) | 373 (40) | 382 (50) | 400 | 438 (75) | — |
| 70 % | 1-3 | 1829 | 534 (20) | 220 (36) | 475 (50) | 493 | — | — |
| 70 % | 1-5 | 1842 | 1672 (20) | 782 (40) | — | 365 | 422 (80) | 1366 |

읽어낼 수 있는 사실(§7 (B)에서 assert):
- **비교예 1-1*(디아민 없음)**: SH가 36 s에 최소(280/247/299 Å)를 찍고 72 s에 1007/878/612 Å로 **재성장** — 정지층 노출
  후 트렌치 poly가 계속 깎이는 디싱. 재성장량 727/631/313 Å은 **PD 30 > 50 > 70 %로 단조 감소** — 트렌치(down) 면적이
  넓을수록 디싱이 크다. 54→72 s에도 아직 상승 중(9.7 Å/s)이라 정상상태 값이 아니다.
- **발명예 1-2(디아민 3.75 ppm + NH₄OH)**: 최소 후 재성장이 147/220/65 Å에 그치고 최종 SH 640/594/438 Å — 모든 PD에서
  비교예보다 작다. 명세서 결론 "lowest step height at the end of polishing … reduced polysilicon dishing"과 일치.
- **1-5(디부틸아민, 선택비 1832)**: 100 s에 SH가 1760/1871/1366 Å로 **초기 단차의 74–101 %까지 복귀** — 선택비가
  가장 높은 슬러리가 디싱 제어를 가장 크게 잃는다(명세서: "non-preferred base leads to reduced dishing control").
  같은 계열 1-3(에탄올아민, 290:1)도 50 s 이후 977–1008 Å로 재성장.

### 2.4 표 E–H — 첨가제 농도·고형분·암모니아
- 디아민 3.75→7.5→15→37.5 ppm(표 E): poly RR 5034→4754→4305→1990 Å/min, 선택비 72→71→69→38로 단조 감소. 같은 계열의
  50 % PD 최종 SH(표 F, 75 s)는 478→385→250 Å로 **감소** — 명세서 [0071] "increasing alkoxylated diamine concentration up
  to at least 15 ppm decreases final step height". 즉 첨가제는 선택비를 조금 깎으면서 디싱을 크게 줄인다.
- 고형분 0.75→15 wt%(표 G): TEOS RR 14→1206 Å/min으로 폭증, 선택비 215→4로 붕괴 — 저고형분(≤1.5 wt%) 설계의 이유.
- 암모니아 감소(표 H 서술): pH↓ → poly RR↓, 선택비↑.

## 3. 디싱 물리 — Lee 2002 STI 2물질 모델의 poly/oxide 전이(E4)와 패턴밀도 의존

[[../cmp/sti-cmp-ceria-high-selectivity-nitride-stop-dishing]] §4가 원문에서 재현한 Lee 2002 Phase 2 모델은 "빠른 down 재료
(트렌치)와 느린 up 재료(정지층)"만 가정하므로 STI(oxide down/nitride up)와 **poly-on-oxide(poly down/oxide up)는 구조가
같다**. 기호를 옮기면 K = 블랭킷 poly RR, s = poly:oxide 선택비, ρ = PD(정지층 up 분율), d_max = 패드가 트렌치 poly에
닿지 않게 되는 단차:

```
D_ss = d_max·ρ(s−1)/(1+ρ(s−1))          (식 2.32)   정상상태 디싱
K_ss = K/(1+ρ(s−1))                      (식 2.33)   정상상태 정지층 침식률
τ_nit = τ₂/(1+(s−1)ρ),  d_max = Kτ₂/(sρ) (식 2.46–2.49; d_max ∝ 1/ρ 가정)
```

이 전이에서 검증 가능한 예측 두 가지를 US10822524B2 표 B–D의 PD 스윕으로 대조했다(§7 (B)):
1. **d_max ∝ 1/ρ 변형**(Lee 2002 자신의 가정, 식 2.46): D_ss ∝ (s−1)/(1+ρ(s−1)) → ρ↑이면 D_ss↓. s = 97(1-1*)로
   D_ss(0.3)/D_ss(0.7) = 2.29, 실측 재성장 비 727/313 = 2.32 — **1.5 % 이내 일치**. 그러나 D_ss(0.3)/D_ss(0.5) = 1.64 vs
   실측 1.15 — **약 30 % 불일치**(실측이 정상상태가 아니고 n = 3인 점이 원인 후보, 확정 못 함).
2. **d_max 고정 변형**: D_ss/d_max = ρ(s−1)/(1+ρ(s−1))이 s = 97에서 0.966/0.980/0.985로 PD에 거의 무관(오히려 미증) —
   실측의 2.3배 감소를 전혀 예측 못 하므로 **poly/oxide 계에서는 기각**.
   → EVIDENCE-RULES 판정 #5: E4(전이 모델 두 변형) vs E3(특허 PD 스윕, n = 3, 시료 단위) → d_max ∝ 1/ρ 채택, **잠정**.

**선택비의 역설이 poly에도 그대로 나타난다.** 식 2.32는 s↑ → D_ss↑(s→∞에서 d_max)라 말한다. 표 A/B–D에서 선택비
1832의 1-5가 초기 단차까지 되파이고, 97의 1-1*보다 69의 1-2가 덜 파인다 — 방향은 모델과 같다. 그러나 **크기는 모델이
설명하지 못한다**(§7 (D)): ρ = 0.5, d_max 고정에서 D_ss/d_max는 s = 69/97/1832에 대해 0.971/0.980/0.999로 1 % 남짓
차이인데, 실측 최종 SH는 1-2가 1-1*보다 32 % 작다. 즉 알콕실화 디아민의 디싱 억제는 "선택비를 낮춰서"가 아니라
**정지층 노출 후 트렌치 poly의 제거율 자체를 Preston 항 밖에서 억제**(흡착 차단)하는 효과로 봐야 한다 — 명세서 [0034]
"alkoxylated diamines reduce dishing without significantly reducing polysilicon removal rates"가 이 해석과 부합한다.
흡착 등온선 데이터는 특허에 없으므로 메커니즘은 **추정**이다.

## 4. 유효압력과 평탄화 시정수 — 1/ρ 가정 vs Sorooshian 2004 실측

Lee 2002 Phase 1A(비압축 패드)는 up 영역 압력을 P/ρ로 보고 단차가 K/ρ로 **선형** 소멸한다고 한다 — t_c = ρ·h₀/K.
표 A의 K = 4000 Å/min, h₀ ≈ 1840 Å를 넣으면 t_c는 PD 30 %에서 8.3 s, 70 %에서 19.3 s인데, 실측 SH는 36 s에도 초기의
15–16 %가 남아 있다(§7 (C)). 대신 0→18→36 s의 감쇠는 **지수형**이다: 두 구간에서 추정한 시정수가 PD 30/50/70 %에서
18.1·20.3 / 17.5·18.5 / 19.8·19.9 s로 구간 간 12 % 이내로 맞고, **PD 간 편차도 10 %**에 불과하다 — Lee 2002 Phase 1B
(τ_ox = ρ·h_c/K, h_c ∝ 1/ρ로 밀도 무관)와 방향이 같다. 선형 모델은 연속 감소량 비가 1이어야 하지만 실측은 0.35–0.40이다.

Sorooshian et al. (2004, 초록)의 STI 실측 유효압력비 2.2/1.7/1.3(밀도 10/50/90 %)은 1/ρ = 10/2/1.11보다 저밀도에서
4.5배 작고 고밀도에서는 오히려 크다(§7 (C)). 즉 **패드는 1/ρ만큼 압력을 up 영역에 몰아주지 않는다** — 이것이 선형(Phase
1A) 예측보다 단차가 느리게, 지수형으로 사라지는 이유의 유력 후보다. 단 Sorooshian은 STI 산화막 데이터이고 본문을 못 봤으므로
poly 계에는 **방향만** 전이한다(E5).

## 5. 디바이스 결과 — Jia 2023: 덱 간 poly-plug CMP 변동이 전류 산포로

Jia et al. (2023)의 두 연결 방식 중 poly-plug 방식은 "the deposition of gate stack and channel polysilicon between the upper
and lower decks divides into two steps"이며, 하부 덱 평탄화 CMP 뒤 plug 구조가 공정 변동을 탄다. 실측: 1덱 대비 2덱
poly-plug 시료의 채널 포화전류 대표값 17 % 감소, 산포 ≈2배(원문 §3). 저자 처방은 plug N형 도핑으로 차폐효과를 완화하는
것이지 CMP 개선이 아니다 — 그러나 우리 관점에서는 §2.3의 디싱 재성장(수백 Å)이 plug 높이·접촉면 변동의 직접 후보이며,
"디싱 nm → plug 저항 → Ion" 전달함수는 **이 단원에서 확보하지 못했다**(Cal-1 실데이터 과제로 이관).

## 6. 고종횡비(HAR) 구조 특이점 — 확인한 것과 못 한 것

- 확인: HAR 채널홀 식각 한계가 다중 덱 구조와 덱 간 poly CMP를 **만드는 원인**이라는 공정 논리(Jia 2023 §1·§2).
- 확인: 3D NAND poly CMP의 요구조건(정지층 정지·오버폴리시 마진·트렌치 poly 디싱 억제)과 PD 30–70 % 패턴에서의
  디싱 시계열(US10822524B2).
- **확인 못 함**: 채널홀 자체(직경 ~100 nm급, 깊이 µm급) 안의 poly 리세스/디싱을 측정한 1차 문헌. 특허 시편은 피치
  1 µm–1 mm의 평면 트렌치이고 단차 ~2000 Å이므로, **홀 종횡비가 디싱에 미치는 효과는 이 노트에서 미검증**이다. 홀 직경이
  패드 asperity 접촉 스케일보다 훨씬 작으면 d_max(패드가 down에 닿지 않는 단차)가 사실상 무한대가 되어 디싱이 "패드
  비접촉 + 순수 화학 용해" 레짐([[film-poly-si-alkaline-dissolution-ph-kinetics]] §2의 OH⁻ 용해)으로 넘어간다는 것은
  [[../cmp/npw-ptw-pattern-effect-gw-physics]]의 GW 논리에서 나오는 **추정**이며, 이번 문헌으로는 확인하지 못했다.

## 7. Python 재현 & 문헌 대조

**재현 요약**: US10822524B2 표 A/E/G 선택비 재계산 5 % 이내, 표 B–D 비교예 디싱 재성장이 PD 30/50/70 %에서 단조 감소하고 Lee 2002 식 2.32(d_max ∝ 1/ρ) 비율 2.29 vs 실측 2.32배 대조(30/50 %는 30 % 불일치), 단차 감쇠 시정수 18–20 s 지수형, Sorooshian 2004(DOI 10.1149/1.1785933) 유효압력비 대조 — 아래 4블록.

```python verify
# ── (A) US10822524B2 표 A·E·G: poly/TEOS 재계산 vs 표기 선택비, 첨가제·고형분 경향 ──
tabA = {"1-1*": (4000, 42, 97), "1-2": (4278, 62, 69), "1-3": (5182, 18, 290), "1-4": (3388, 5, 686),
        "1-5": (3825, 2, 1832), "1-6": (3049, 2, 1601), "1-7": (1755, 2, 1150)}          # poly RR, TEOS RR (Å/min), 선택비
tabE = {"2-1": (3.75, 5034, 70, 72), "2-2": (7.5, 4754, 67, 71), "2-3": (15, 4305, 62, 69), "2-4": (37.5, 1990, 52, 38)}  # ppm, RR, RR, sel
tabG = {"3-1": (0.75, 3090, 14, 215), "3-2": (1.5, 4893, 58, 84), "3-3": (3.0, 7147, 165, 43),
        "3-4": (7.5, 7575, 533, 14), "3-5": (15.0, 4272, 1206, 4)}                        # wt%, RR, RR, sel
rounding_limited = []
for ex, (poly, teos, sel) in tabA.items():
    calc = poly / teos
    if teos >= 5:
        assert abs(calc - sel) / sel <= 0.05 or round(calc) == sel, (ex, calc, sel)
    else:                                   # TEOS RR '2 Å/min'은 반올림값 — 선택비 오차를 반올림이 지배
        rounding_limited.append((ex, calc, sel))
        assert abs(calc - sel) / sel <= 0.30, (ex, calc, sel)
assert any(abs(c - s) / s > 0.05 for _, c, s in rounding_limited)   # 1-7: 877 vs 1150 (24 %) — 숨기지 않음
for ex, (ppm, poly, teos, sel) in tabE.items():
    assert abs(poly / teos - sel) / sel <= 0.05 or round(poly / teos) == sel, (ex, poly / teos, sel)
for ex, (solid, poly, teos, sel) in tabG.items():
    assert abs(poly / teos - sel) / sel <= 0.05 or round(poly / teos) == sel, (ex, poly / teos, sel)
selE = [v[3] for v in tabE.values()]; rrE = [v[1] for v in tabE.values()]
assert all(a >= b for a, b in zip(selE, selE[1:])), selE          # 디아민↑ → 선택비 단조 비증가
assert all(a > b for a, b in zip(rrE, rrE[1:])), rrE              # 디아민↑ → poly RR 단조 감소
selG = [v[3] for v in tabG.values()]; teosG = [v[2] for v in tabG.values()]
assert all(a > b for a, b in zip(selG, selG[1:])) and all(a < b for a, b in zip(teosG, teosG[1:]))
print(f"(A) 표 A 선택비 재계산 OK(반올림 지배 {len(rounding_limited)}건), 표 E 선택비 {selE}, 표 G 선택비 {selG}")
```

```python verify
# ── (B) US10822524B2 표 B·C·D: PD별 단차(SH, Å) 시계열 → 디싱 재성장 → Lee 2002 식 2.32 전이(E4) 대조 ──
SH = {
 30: {"1-1*": [(0, 1841), (18, 681), (36, 280), (54, 833), (72, 1007)],
      "1-2":  [(0, 1908), (25, 493), (40, 505), (50, 524), (60, 557), (75, 640)],
      "1-3":  [(0, 1852), (20, 497), (36, 462), (50, 977), (60, 1008)],
      "1-5":  [(0, 1841), (20, 1628), (40, 1526), (60, 296), (80, 494), (100, 1760)]},
 50: {"1-1*": [(0, 1825), (18, 654), (36, 247), (54, 734), (72, 878)],
      "1-2":  [(0, 1895), (25, 465), (40, 374), (50, 510), (60, 539), (75, 594)],
      "1-3":  [(0, 1835), (20, 504), (36, 483), (50, 854), (60, 883)],
      "1-5":  [(0, 1853), (20, 1617), (40, 1627), (60, 272), (80, 839), (100, 1871)]},
 70: {"1-1*": [(0, 1835), (18, 740), (36, 299), (54, 526), (72, 612)],
      "1-2":  [(0, 1891), (25, 572), (40, 373), (50, 382), (60, 400), (75, 438)],
      "1-3":  [(0, 1829), (20, 534), (36, 220), (50, 475), (60, 493)],
      "1-5":  [(0, 1842), (20, 1672), (40, 782), (60, 365), (80, 422), (100, 1366)]}}
def stats(series):
    t_min, sh_min = min(series, key=lambda p: p[1])
    t_end, sh_end = series[-1]
    return sh_min, sh_end, sh_end - sh_min
regrow = {pd: {ex: stats(s)[2] for ex, s in d.items()} for pd, d in SH.items()}
final = {pd: {ex: stats(s)[1] for ex, s in d.items()} for pd, d in SH.items()}
# (a) 비교예 1-1*: 정지층 노출 후 디싱 재성장이 PD 30 > 50 > 70 %로 단조 감소
r11 = [regrow[pd]["1-1*"] for pd in (30, 50, 70)]
assert r11 == [727, 631, 313], r11
assert r11[0] > r11[1] > r11[2]
# (b) 발명예 1-2: 모든 PD에서 재성장·최종 SH가 비교예보다 작음 (명세서 [0065] 결론)
for pd in (30, 50, 70):
    assert regrow[pd]["1-2"] < regrow[pd]["1-1*"] and final[pd]["1-2"] < final[pd]["1-1*"], pd
# (c) 1-5 (dibutylamine, 선택비 1832): 100 s에 초기 단차의 70 % 이상으로 복귀 — 디싱 제어 상실
for pd in (30, 50, 70):
    sh0 = SH[pd]["1-5"][0][1]
    assert final[pd]["1-5"] / sh0 > 0.7, (pd, final[pd]["1-5"] / sh0)
# (d) Lee 2002 식 2.32 전이(E4): d_max ∝ 1/ρ 변형 vs d_max 고정 변형 — PD 스윕으로 판정
s = 97.0                                                   # 1-1* 블랭킷 선택비 (표 A)
def dss_inv(rho): return (s - 1) / (1 + rho * (s - 1))     # d_max ∝ 1/ρ  (식 2.46 가정)
def dss_fix(rho): return rho * (s - 1) / (1 + rho * (s - 1))   # d_max 고정
model_37, obs_37 = dss_inv(0.3) / dss_inv(0.7), r11[0] / r11[2]
model_35, obs_35 = dss_inv(0.3) / dss_inv(0.5), r11[0] / r11[1]
err_37 = abs(obs_37 - model_37) / model_37
err_35 = abs(obs_35 - model_35) / model_35
assert err_37 < 0.05, err_37                # 30/70 % 비율: 모델 2.29 vs 실측 2.32
assert err_35 > 0.2, err_35                 # 30/50 % 비율: 모델 1.64 vs 실측 1.15 — 약 30 % 불일치, 숨기지 않음
fix_37 = dss_fix(0.3) / dss_fix(0.7)
assert fix_37 < 1.05 and obs_37 > 2.0, (fix_37, obs_37)   # d_max 고정 변형은 PD 의존을 예측 못 함 → 기각
# (e) 1-1* 30 %는 54→72 s에도 상승 중 — 정상상태 미도달 (비교는 재성장량 기준임을 명시)
slope = (1007 - 833) / (72 - 54)
assert slope > 5, slope
print(f"(B) 재성장 1-1* {r11} Å; 모델/실측 비 30/70 %: {model_37:.2f}/{obs_37:.2f} (오차 {err_37*100:.1f} %), "
      f"30/50 %: {model_35:.2f}/{obs_35:.2f} (오차 {err_35*100:.0f} %); d_max 고정 비 {fix_37:.3f} 기각; 상승률 {slope:.1f} Å/s")
```

```python verify
# ── (C) 단차 소멸: Lee 2002 Phase 1A 선형(t_c=ρh0/K) vs 실측 지수 감쇠; Sorooshian 2004 유효압력 vs 1/ρ ──
import math
K = 4000.0                     # Å/min, 1-1* 블랭킷 poly RR (표 A)
SH11 = {0.3: [(0, 1841), (18, 681), (36, 280)], 0.5: [(0, 1825), (18, 654), (36, 247)],
        0.7: [(0, 1835), (18, 740), (36, 299)]}
taus, tcs = {}, {}
for rho, ser in SH11.items():
    h0 = ser[0][1]
    tcs[rho] = rho * h0 / K * 60.0                     # s, 비압축 패드 선형 소멸 시각
    assert ser[2][1] > 0.1 * h0, (rho, ser[2][1] / h0)   # t_c(8–19 s) 지난 36 s에도 단차 15 % 이상 잔존
    r1, r2 = ser[1][1] / ser[0][1], ser[2][1] / ser[1][1]
    tau1, tau2 = 18 / math.log(1 / r1), 18 / math.log(1 / r2)
    assert abs(tau1 - tau2) / tau1 < 0.2, (rho, tau1, tau2)          # 두 구간 시정수 일치 → 지수형
    lin_ratio = (ser[1][1] - ser[2][1]) / (ser[0][1] - ser[1][1])
    assert lin_ratio < 0.6, (rho, lin_ratio)                          # 선형이면 ≈1
    taus[rho] = (tau1 + tau2) / 2
vals = list(taus.values())
spread = (max(vals) - min(vals)) / (sum(vals) / len(vals))
assert spread < 0.2, spread                                           # τ가 PD에 거의 무관 (Phase 1B τ_ox 밀도무관 가정과 방향 일치)
assert 15 < min(vals) and max(vals) < 22, vals
assert tcs[0.3] < 10 and tcs[0.7] < 20, tcs
# Sorooshian et al. 2004 (DOI 10.1149/1.1785933, 초록): P_eff/P_applied = 2.2/1.7/1.3 @ 밀도 10/50/90 %
soro = {0.1: 2.2, 0.5: 1.7, 0.9: 1.3}
ratio = {rho: (1 / rho) / v for rho, v in soro.items()}
assert ratio[0.1] > 3.0 and ratio[0.9] < 1.0 and 1.0 < ratio[0.5] < 1.3, ratio
print(f"(C) t_c 선형예측 {tcs[0.3]:.1f}/{tcs[0.5]:.1f}/{tcs[0.7]:.1f} s vs 실측 지수 τ {vals[0]:.1f}/{vals[1]:.1f}/{vals[2]:.1f} s "
      f"(PD 편차 {spread*100:.0f} %); (1/ρ)/P_eff비 = {ratio[0.1]:.2f}/{ratio[0.5]:.2f}/{ratio[0.9]:.2f}")
```

```python verify
# ── (D) 선택비 s → D_ss/d_max (Lee 2002 식 2.32, d_max 고정, ρ=0.5): 방향은 맞지만 첨가제 효과 크기는 설명 못 함 ──
rho = 0.5
def dss_norm(s): return rho * (s - 1) / (1 + rho * (s - 1))
d_12, d_11, d_15 = dss_norm(69), dss_norm(97), dss_norm(1832)      # 1-2 / 1-1* / 1-5 블랭킷 선택비
assert d_12 < d_11 < d_15 < 1.0, (d_12, d_11, d_15)               # s↑ → D_ss↑ → d_max 포화
model_gap = 1 - d_12 / d_11                                        # 모델: 1-2가 1-1*보다 이만큼 덜 파임
obs_gap = 1 - 594 / 878                                            # 표 C 50 % PD 최종 SH (75 s vs 72 s)
assert model_gap < 0.02 and obs_gap > 0.3, (model_gap, obs_gap)    # 모델 <1 % vs 실측 32 % → 선택비만으로는 설명 불가
print(f"(D) D_ss/d_max s=69/97/1832: {d_12:.3f}/{d_11:.3f}/{d_15:.3f}; 모델 차 {model_gap*100:.1f} % vs 실측 차 {obs_gap*100:.0f} %")
```

## 8. 한계 / 미확인 사항

- **HAR 채널홀 내부 디싱의 1차 데이터가 없다.** §6 참조. 이 노트의 정량은 전부 피치 µm–mm급 평면 트렌치(US10822524B2)에서
  나왔고, 홀 종횡비→디싱 함수는 확인하지 못했다.
- **Lee 2002 모델 전이는 E4** (Lee 2002; STI oxide/nitride에서 검증된 폐형해를 poly/oxide로 옮김). PD 스윕 대조는 30/70 %만 맞고
  30/50 %는 30 % 어긋나며, 실측이 정상상태가 아니라 재성장량으로 대조한 것이다. d_max, τ₂ 등 poly 계 파라미터를 추출한
  것이 아니라 **비율만** 대조했다.
- **특허 표 B–D의 셀 정렬은 HTML 파싱 결과**다. 결측 셀 배치가 어긋났을 가능성을 배제 못 하나, 명세서 서술(1-2 최저 최종
  단차, 1-1* 디싱, 1-5 제어 상실)과 파싱 결과가 일관됨을 확인했다.
- **Sorooshian 2004는 초록만**(E5). 본문의 제거율 모델·오차범위를 못 봤다.
- **Jia 2023의 17 % / 2배**는 CMP만의 효과가 아니라 poly-plug 연결 방식 전체(정렬·2차 식각 포함)의 효과다. 디싱 깊이와의
  정량 연결은 **미검증**.
- **디아민 흡착 차단 메커니즘**(§3 말미)은 명세서 서술과 데이터의 정합에서 나온 **추정**이며 흡착등온선·XPS 증거는 없다.

## 9. 이 에이전트의 결론 (모델링 관점)

1. **poly 디싱은 PD가 낮을수록(트렌치 넓을수록) 크고, 정지층 노출 뒤 시간에 따라 재성장한다.** Tier2 패턴 모델은
   Lee 2002 2물질 폐형해를 poly/oxide 기호로 재사용하되 **d_max ∝ 1/ρ 변형**을 쓴다(판정 #5, 잠정).
2. **선택비는 디싱을 줄이지 않는다** — Lv2-1 §5의 "선택비↑ → 오버폴리시 마진↑"와 이 노트의 "선택비↑ → D_ss→d_max"는
   같은 손잡이의 두 얼굴이다. 명세서가 선택비 상한(50–100:1 선호)을 두는 이유가 이것이다. Kp_poly/Kp_oxide 한 파라미터로는
   1-2(69:1, 저디싱)와 1-5(1832:1, 고디싱)를 동시에 못 그리므로, **트렌치(down) poly의 제거율을 별도로 억제하는 화학 인자**
   (첨가제 흡착 차단, 단위: 무차원 0–1)가 필요하다.
3. **단차 소멸은 선형이 아니라 지수형(τ ≈ 18–20 s, PD 무관)**이다. Phase 1A(1/ρ 압력)보다 Phase 1B(τ 밀도무관)가 데이터에
   맞고, Sorooshian의 "유효압력은 1/ρ보다 훨씬 완만" 실측과 방향이 같다.
4. 3D NAND에서 이 디싱은 덱 간 poly-plug 변동(전류 17 %↓, 산포 2배)의 후보 원인이지만 전달함수는 Cal-1 실데이터에서 잡아야
   한다.

## 10. 자기시험
→ [[../../agents/film-poly-si/EXAMS.md]] Lv2-2 문항 참조.
