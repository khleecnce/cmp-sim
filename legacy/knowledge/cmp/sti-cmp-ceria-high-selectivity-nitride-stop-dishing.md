<!-- V2-SECTION: R5-wafer | 공동: R2-slurry | 근거: STI, ceria, selectivity, nitride stop, dishing, erosion | 정본: ARCHITECTURE-V2.md §3 -->
# STI CMP — 세리아 고선택비 슬러리, 나이트라이드 정지, 트렌치 옥사이드 디싱 (Lee 2002 2단계 모델)

> film-oxide Lv2-2 | 작성일: 2026-09-09
> 선행: [[ild-cmp-planarization-global-local-density]] (Lv2-1, PL·유효밀도·식 2.1 기본모델 — 이 노트의 Phase 1이 그대로 상속),
> [[../materials/film-oxide-hydration-layer-mechanism-cook-suratwala]] (Lv1-2, 옥사이드 제거 메커니즘),
> [[../materials/film-oxide-teos-hdp-bpsg-sod-density-hardness]] (Lv1-1, HDP 트렌치 필 막질)
> 관련: [[ceria-slurry-ce-redox-selectivity]] (slurry-chemist Lv3-1 — Ce³⁺ 활성점·Si–O–Ce 화학결합·첨가제 선택비 화학. 본 노트는 그 화학이 **패턴 웨이퍼의 디싱·침식으로 어떻게 번역되는가**를 다룬다),
> [[pattern-dependent-dishing-erosion]] (형제 노트 — Cu damascene removal-rate diagram; STI는 같은 틀의 "nitride up / oxide down" 판),
> [[pattern-metrics-dishing-erosion-stepheight]] (dishing·erosion 정의·기준면), [[npw-ptw-transfer-rules-quantitative]] (Kim & Seo 2002 STI 블랭킷↔패턴 상관),
> [[preston-luo-dornfeld-mrr]] (K = Kp·P·V), [[../materials/hertz-gw-contact-mechanics]] (up 영역 국소압 증폭)

## 1. 왜 이 단원이 필요한가

STI(shallow trench isolation)는 Si 트렌치를 HDP 옥사이드로 채운 뒤 **활성영역 위 Si₃N₄ 정지층에서 멈춰야 하는**
2물질 CMP다. 요구사항은 세 가지가 서로 당긴다 — (i) 오버버든 옥사이드는 빨리(스루풋), (ii) 나이트라이드는
거의 깎이지 않아야(정지층 보전, 리뷰는 <1 nm/min 을 기준으로 제시 — Srinivasan et al. 2015), (iii) 트렌치
옥사이드는 파이면(디싱) 안 된다. 세리아 슬러리는 (i)(ii)를 화학으로 해결하지만, **높은 선택비가 자동으로 낮은
디싱을 뜻하지는 않는다** — 선택비가 클수록 정상상태 디싱 D_ss는 오히려 커진다(§4 식 2.49). 이 단원은 그 역설을
Lee 2002 MIT 학위논문의 폐형 모델로 정량화하고, 세리아 고선택비(HSS) 슬러리의 블랭킷 수치(Dandu 2009, Mariscal 2020,
Urban 2016)를 그 모델 파라미터(s, K)로 번역한다.

## 2. 출처 (6건, 1차 3건)

- **[L] Brian Lee, "Modeling of Chemical Mechanical Polishing for Shallow Trench Isolation," Ph.D. thesis, MIT EECS,
  May 2002 (지도 D. Boning).** MIT DSpace handle http://hdl.handle.net/1721.1/29907 — **원문 PDF 확보**
  (`papers/lee2002-mit-thesis-sti-cmp-modeling.pdf`, 201쪽, 텍스트층 있으나 수식은 깨져 p.55-59·69·75·118·120을 페이지 이미지로
  판독). 2장(STI 2단계 모델·식 2.7-2.56·표 2.1-2.4), 3.7절(세리아 HSS 사례연구·표 3.9-3.10) 완독. 학위논문(가중치 0.7).
- **[D] P. R. Dandu Veera, S. Peddeti, S. V. Babu, "Selective CMP of Silicon Dioxide over Silicon Nitride for STI Using Ceria
  Slurries," *J. Electrochem. Soc.* 156(12) H936-H943 (2009), https://doi.org/10.1149/1.3230624** — 1차 논문, 원문 PDF
  (`papers/dandu2009-jes-selective-sio2-sin-ceria-sti.pdf`) 완독. Crossref로 저자·권호 확인.
- **[M] J. C. Mariscal, J. McAllister, Y. Sampurno, J. Sierra Suarez, M. O'Neill, H. Zhou, M. Grief, D. Slutz, A. Philipossian,
  "Tribological, Thermal and Kinetic Characterization of SiO₂ and Si₃N₄ Polishing for STI CMP on Blanket and Patterned Wafers,"
  *ECS J. Solid State Sci. Technol.* 9, 044008 (2020), https://doi.org/10.1149/2162-8777/ab89bc** — 1차 논문, 원문 PDF
  (`papers/mariscal2020-jss-sio2-si3n4-sti-kinetic.pdf`) 완독. 콜로이달 세리아 상용 슬러리 + MIT 864 STI 패턴 웨이퍼.
- **[S] R. Srinivasan, P. V. R. Dandu, S. V. Babu, "Shallow Trench Isolation CMP: A Review," *ECS J. Solid State Sci. Technol.*
  4(11) P5029-P5039 (2015), https://doi.org/10.1149/2.0071511jss** — CC-BY 리뷰(가중치 0.6), 원문 PDF
  (`papers/srinivasan2015-ecsjss-sti-cmp-review.pdf`). 표 I(고선택비 슬러리 24종)·나이트라이드 억제 메커니즘·패턴 STI 절.
  이 리뷰를 통해 인용하는 Seo(PAA+PEG 디싱)·Lim(입경)·Merricks(오버폴리시)·Manivannan(글루탐산) 결과는 **2차 인용**.
- **[U] N. D. Urban (Ferro Corp.), "High Selectivity Ceria Slurry for Next Generation STI CMP Processes," AVS CMP Users Group
  Meeting, 2016-04-07** — 업체 학회 발표자료(가중치 0.5), PDF 확보(`papers/urban2016-cmpug-ferro-high-selectivity-ceria-sti.pdf`).
  세대별 슬러리 표(HDP RR·나이트라이드 RR·세리아 wt%)와 아민 SiN 패시베이션 모델.
- **[H] S. Hwang, T. Lyu, W. Kim, "Poly(acrylic acid)-Containing Ceria Slurries for STI CMP: Colloidal Stability, Planarization
  Efficiency, and Selectivity," *Polymers* 18, 1899 (2026), https://doi.org/10.3390/polym18151899** — 1차 논문(CC-BY), 원문 PDF
  (`papers/hwang2026-polymers-paa-ceria-sti-slurry.pdf`). 억제제 없이 PAA 분산제만 넣은 세리아의 **낮은** 선택비 대조군.

미확보(유료·미러 사이트 전멸 2026-09-09): Lee/Hwang/Kim/Jeong 2007 MEE https://doi.org/10.1016/j.mee.2006.12.004 (STI 슬러리 종류별
패턴 특성), Hwee et al. 2001 J. Electron. Mater. https://doi.org/10.1007/s11664-001-0161-5 (통합 스킴별 디싱·침식), Chang 2005 MEE
https://doi.org/10.1016/j.mee.2005.07.002 (STI 디싱 모델) — Crossref 실존만 확인, 본문 미독이라 수치 인용 안 함.

## 3. STI 구조와 "정지"의 의미 (Lee 2002 1.8절·2.10.1절, Mariscal 2020 Fig.2)

- 표준 스택(Lee 2002 실험 웨이퍼): 패드 옥사이드 100 Å, 나이트라이드 1500 Å, 트렌치 깊이 5000 Å → **초기 단차 z1 = 6600 Å**,
  오버버든 증착 9000 Å(§2.12 시뮬레이션 입력, Lee 2002 p.65·p.75). Mariscal 2020 웨이퍼: Si 트렌치 2850 Å + 열산화 → 트렌치
  4650 Å, HDP 6000 Å 증착 → 오버필 1350 Å·단차 4650 Å (Mariscal et al. 2020 Fig.2 서술).
- **정지(nitride stop)**는 "나이트라이드가 드러나는 순간 제거가 0이 된다"는 뜻이 아니다. 나이트라이드 노출 시각(nitride
  touch-down time t_n, Lee 2002 식 2.50-2.53)은 **유효밀도에 따라 다이 안에서 40 s 정도 퍼지고**(§2.12.2 예시: 80 s 시작 →
  120 s 완료, Lee 2002 p.75), 그 뒤 오버폴리시 동안 나이트라이드 침식(erosion)과 트렌치 옥사이드 디싱이 동시에 진행된다.
  즉 "정지"의 실체는 **오버폴리시 창(window) 동안 침식·디싱이 예산 안에 머무는 것**이고, 그 창의 크기를 선택비 s가 정한다.
- 나이트라이드가 깎이는 경로: Si₃N₄ 표면이 물에 가수분해되어 SiO₂/Si(OH)₄로 바뀐 층만 기계 제거된다(Si₃N₄ + 6H₂O → 3SiO₂ + 4NH₃,
  Srinivasan et al. 2015 "Silicon nitride removal mechanism" 절, Hu et al. 인용). 따라서 **가수분해를 막는 흡착제**(아미노산·
  환형 아민·PAA)가 곧 나이트라이드 억제제이며, 세리아 입자는 Si₃N₄보다 무르므로 산화층이 없으면 깎지 못한다(같은 절).

## 4. Lee 2002 폐형 STI 모델 — Phase 1(옥사이드 오버버든) + Phase 2(나이트라이드 오버폴리시)

### 4.1 Phase 1 — 단일물질, [[ild-cmp-planarization-global-local-density]]의 상속
- 파라미터 3개: 옥사이드 PL_ox, 블랭킷 K, 옥사이드 시정수 τ_ox (Lee 2002 §2.7.1). 패드가 up만 만지는 Phase 1A(RR_u = K/ρ,
  RR_d = 0, H = z1 − Kt/ρ)와 접촉높이 h_c 이후 up/down 제거율이 지수적으로 수렴하는 Phase 1B(H = h_c·exp(−(t−t_c)/τ_ox),
  τ_ox = ρ·h_c/K — 식 2.12·2.20). h_c ∝ 1/ρ 가정으로 τ_ox를 밀도 무관 상수로 둔다(식 2.20 아래 서술, Smith·Grillaert 인용).
- 표 2.3(10개 공정, IPEC 472, IC1400 적층 vs IC1000 solo): PL_ox 적층 2.3-4.1 mm, solo 5.3-7.5 mm, K 880-7048 Å/min, τ_ox 4-80 s,
  RMSE ≤ 609 Å (Lee 2002 p.68). 단단한 패드가 긴 PL — Lv2-1 표 7.2와 같은 결론.

### 4.2 Phase 2 — 2물질 removal-rate diagram (Lee 2002 §2.5.2, Fig.2.11)
나이트라이드가 드러난 뒤 활성영역(nitride, up)과 트렌치 옥사이드(field, down)가 함께 깎인다. Preston 가정 하에 선택비
s = K_ox/K_nit = Kp_ox/Kp_nit (식 2.29), K_ox = K, K_nit = K/s (식 2.30-2.31). 단차 H(=디싱)가 커지면 압력이 up(nitride)으로 몰려
nitride RR↑·oxide RR↓ — 선형 근사:

  RR_a = (K/s)(1/d_max)((1−ρ_nit)/ρ_nit)·H + K/s      (식 2.34, 활성영역)
  RR_f = −(K/d_max)·H + K                              (식 2.35, 트렌치 옥사이드)

d_max = 패드가 트렌치 옥사이드에 닿지 않게 되는 단차(최대 디싱). 두 제거율이 같아지는 점이 **정상상태**:

  D_ss = d_max·ρ_nit(s−1) / (ρ_nit(s−1)+1)      (식 2.32)
  K_ss = K / (ρ_nit(s−1)+1)                      (식 2.33)
  τ_nit = (d_max/K)·sρ_nit/(1+ρ_nit(s−1))         (식 2.38)
  D(t) = H(t) = (h_n − D_ss)·exp(−(t−t_n)/τ_nit) + D_ss      (식 2.41·2.54)
  E(t) = K_ss(t−t_n) + (h_n − D_ss)(1−ρ_nit)/(1+ρ_nit(s−1)) · (1−exp(−(t−t_n)/τ_nit))    (식 2.56, 침식)

d_max ∝ 1/ρ_nit 가정으로 "순수 나이트라이드 시정수" τ₂ = sρ_nit·d_max/K (식 2.46)를 정의하면 d_max = Kτ₂/(sρ_nit),
τ_nit = τ₂/(1+(s−1)ρ_nit), **D_ss = K·τ_nit·(s−1)/s** (식 2.47-2.49). Phase 2 파라미터도 3개: PL_nit, s, τ₂.

**핵심 함의(원문 §2.7.2 서술 + 식 2.33·2.49에서 직접 읽힘)**
1. **선택비 s↑ → D_ss↑, K_ss↓ (d_max 고정 비교).** d_max는 패드·기하가 정하는 양이라 슬러리를 바꿔도 대략 고정인데, 식 2.32의
   D_ss = d_max·ρ(s−1)/(1+ρ(s−1))는 s에 단조증가하고 s→∞에서 d_max(패드가 트렌치를 못 만질 때까지 파인다)로 간다; K_ss → K/(ρs) ≈ K_nit/ρ.
   (τ₂ = sρ·d_max/K는 s에 비례하는 유도량이므로 "τ₂ 고정" 비교는 무의미 — §8 [B]는 d_max 고정으로 확인.)
   즉 고선택비 슬러리는 나이트라이드를 지키는 대신 **트렌치 옥사이드가 d_max까지 파이는 것을 허용**한다. 이것이 리뷰가
   "세리아 HSS는 필드 옥사이드 디싱이 심하다"고 쓰는 물리적 이유다(Srinivasan et al. 2015 서론; 2차 인용 Merricks: PAA 슬러리는
   30 s 오버폴리시 동안 옥사이드 손실 지속).
2. **정상상태 침식률 K_ss = K/(1+ρ(s−1))는 K_nit = K/s보다 크다** — up 영역 압력 집중 때문. ρ=0.5, s=10이면 K_ss = K/5.5 = 0.18K
   (블랭킷 나이트라이드율 0.1K의 1.8배). 저밀도(ρ 작음)일수록 K_ss → K_nit/ρ 로 커져 "narrow nitride = large nitride loss"
   (Urban 2016 slide 8)가 된다.
3. **디싱 시정수 τ_nit는 밀도·선택비 의존**(τ₂/(1+(s−1)ρ)) — 고선택비·고밀도일수록 정상상태에 빨리 도달한다.
4. 식 2.36 인쇄본은 "dH/dt + (K/d_max)(…)H − K(1−s)/s = 0"인데, 이대로면 정상상태가 −D_ss가 되어 식 2.32·2.37과 모순이다.
   물리적으로 옳은 형태(dH/dt = RR_f − RR_a, H = 디싱)는 상수항이 +K(s−1)/s이어야 하며 §8 [A]에서 수치적분으로 확인했다
   — **원문 식 2.36 상수항 부호 오기(typo)로 판단, 미검증(저자 확인 못 함)**.

### 4.3 표 2.4 — 10개 공정의 Phase 2 추출값 (Lee 2002 p.69, 페이지 이미지 판독)
| 공정 | 패드 | P(psi)/V(rpm) | PL_nit(mm) | s | τ₂(s) | RMSE(Å) |
|---|---|---|---|---|---|---|
| A | IC1400 | 3/30 | 4.3 | 7.2 | 297 | 218 |
| B | IC1400 | 3/90 | 19.9 | 2.7 | 320 | 286 |
| C | IC1400 | 9/30 | 14.8 | 38 | 115 | 136 |
| D | IC1400 | 9/90 | 4.3 | 4.2 | 34 | 127 |
| E | IC1400 | 6/60 | 9.8 | 3.1 | 101 | 160 |
| F | IC1000 solo | 3/30 | 3.0 | 10.3 | 170 | 103 |
| G | IC1000 solo | 3/90 | 19.9 | 2.8 | 125 | 1006 |
| H | IC1000 solo | 9/30 | 5.9 | 8.9 | 58 | 206 |
| I | IC1000 solo | 9/90 | 13.4 | 4.4 | 40 | 101 |
| J | IC1000 solo | 6/60 | 11.2 | 8.6 | 66 | 133 |

(실리카 계열 표준 슬러리 공정. Lee 2002 p.69-73) 관찰: 선택비 s가 2.7-38로 **공정조건에 따라 크게 변한다**(원문 "selectivity
also appears to change with process conditions") — 블랭킷 선택비를 상수로 믿으면 안 된다는 경고. PL_nit는 속도↑·압력↓에서 길다.
B·G의 PL 19.9 mm는 RMSE가 PL에 둔감해(Fig.2.20) 신뢰도 낮음, G는 웨이퍼 스케일 비균일 의심(원문 서술).

### 4.4 원문 §2.12 예시 시뮬레이션(K = 2000 Å/min, s = 10, τ₂ = 60 s, PL_ox 3 mm, PL_nit 2.3 mm, z1 6600 Å, 증착 9000 Å)
Fig.2.23(p.75, 이미지 판독): 트렌치 디싱 컬러바 약 400-1000 Å, 나이트라이드 침식 약 100-600 Å, **고밀도 영역이 최소·저밀도가
최대**(원문 서술). §8 [B]에서 같은 파라미터로 D_ss(ρ)를 계산하면 ρ = 0.1-0.9에서 947-198 Å로 컬러바와 오더가 맞는다(정확한
시각·h_n은 그림에서 못 읽어 **오더 일치만**).

## 5. 세리아 HSS 슬러리 — 블랭킷 수치와 억제 메커니즘

### 5.1 1차 실측 (Dandu Veera et al. 2009, JES; 4 psi, 75/75 rpm, IC1000, Westech 372)
- 60 nm Rhodia 세리아 0.25 wt%, 첨가제 없음, pH 4-5.5: **옥사이드 350 nm/min, 나이트라이드 80 nm/min** → 선택비 ≈ 4.4
  (Dandu Veera et al. 2009 Fig.3 서술). pH ≤3·≥6에서 둘 다 급감(pH 5.5 이상은 PAA 0.01 % 필요).
- 같은 슬러리 + **피리딘·HCl 0.05 wt%**: 나이트라이드 **2 nm/min**, 옥사이드 350 nm/min 유지 → 선택비 ≈ 175 (Fig.3·5·7;
  피페라진·이미다졸도 2-3 nm/min). 180 nm Ferro 소성 세리아 1 wt%에서는 옥사이드 580 nm/min(첨가제 1 → 0.05 %로 줄일 때
  350 → 580)에 나이트라이드 2 nm/min → 선택비 ≈ 290 (Dandu Veera et al. 2009 Fig.7 서술). §8 [D] 재현.
- **시간 추이(Fig.14)**: 나이트라이드는 처음 30 s에 약 3 nm(자연산화층 두께)만 깎이고 200 s까지 더 이상 제거 없음 — 흡착
  피리딘이 가수분해를 막아 "진짜 정지"에 가까운 거동. 옥사이드는 선형(일정 RR). 이것이 Lee 모델의 K_nit ≈ 0 극한.
- 메커니즘 근거: 피리딘·HCl은 옥사이드·나이트라이드 **둘 다에 흡착**하지만(TGA·접촉각 표 I-II), 0.25 % 세리아만으로
  30 s 폴리시하면 옥사이드 접촉각은 57→32°, 나이트라이드는 62→40°로 둘 다 벗겨진다 — 그럼에도 옥사이드 RR이 안 줄어드는 것은
  저농도(0.05 %)에서 옥사이드 표면 피복이 성기고, 나이트라이드 쪽 결합이 더 강하기 때문(Dandu Veera et al. 2009 결론). 세리아
  IEP는 8이고 피리딘 첨가로 7로 이동(Fig.8) — pH 4-5에서 세리아(+)·실리카(−) 정전인력은 [[ceria-slurry-ce-redox-selectivity]] §4와 정합.

### 5.2 상용 콜로이달 세리아 + MIT 864 패턴 웨이퍼 (Mariscal et al. 2020, JSS)
- 블랭킷 선택비는 **P·V에 따라 32:1 ~ 101:1**로 변하고(최대 101:1은 중간 조건 3 psi·1.25 m/s), 최저는 최저 속도(32-44:1),
  최고 속도는 75-91:1 (Mariscal et al. 2020 Fig.9 서술). 실리카 슬러리 대비값으로 4:1을 제시. Lee 표 2.4의 "s는 공정조건 함수"와
  같은 결론을 세리아에서 확인.
- 수정 Langmuir–Hinshelwood 적합: SiO₂는 k₁/k₂ = 6.3-142(기계 지배), Si₃N₄는 k₁/k₂ = 2.5e-5-9.9e-5(**극단적 화학 제한** —
  억제제가 화학단계를 막음), Ea 1.40/1.47 eV, RMSE 98/4 Å/min (Mariscal et al. 2020 표 I). COF는 SiO₂ 0.37-0.51, Si₃N₄는
  약 절반.
- **패턴 웨이퍼 엔드포인트**: HDP 6000 Å 오버버든이 4.5 min쯤 COF 최대(0.36, 블랭킷 SiO₂ 수준)를 지나 6 min에 0.26(블랭킷
  Si₃N₄ 수준)으로 떨어짐 → 저밀도 영역이 5 min에 먼저 열리고 전체 클리어에 1 min 더(Fig.16-17). 블랭킷 PETEOS 2528 Å/min으로
  나눈 순진한 예측 2.4 min보다 2.5배 길다(HDP가 느림 + ±9 % 센터패스트 비균일 + 패턴; Mariscal et al. 2020 서술) — [[npw-ptw-transfer-rules-quantitative]]의
  NPW→PTW 전이 경고와 동일. 제거량이 시간에 비례하지 않는(4-5·5-6 min 구간에 몰림) 이상은 낮은 입자농도 때문으로 설명(2차: Lim et al. 인용).

### 5.3 업체 데이터 (Urban 2016, Ferro; 학회 슬라이드 — 검증 불가, 경향만)
| 세대 | D_mean(nm) | 세리아 wt% | HDP RR(Å/min) | 나이트라이드 RR(Å/min) | 선택비(계산) |
|---|---|---|---|---|---|
| 1세대 | 145 | 4 | 2000 | <20 | >100 |
| 2세대 | 145 | 4 | 2700 | <20 | >135 |
| 3세대 | 130 | 3 | 3500 | <20 | >175 |
| SRS-2092 | 130 | 0.5 | 3400 (TEOS) | <20 | >170 |
| LDM SRS-2092 | 70 | 0.5 | 2800 | <20 | >140 |
| Colloidal | 30 | 0.5 | 2000 | <10 | >200 |
(Urban 2016 slides 12·18·23·24; "고객 보고 >500:1"은 slide 20, **미검증**) — 아민계 억제제로 SiN 패시베이션, Ce³⁺ 안정화
첨가제(pH 3-4 완충)로 옥사이드 가속, 세리아 4 → 0.5 wt%로 같은 율. 슬라이드 8의 명제 "wide trench = large dishing, narrow
nitride = large nitride loss, low density = both"는 §4.2 함의 1-2와 정확히 대응.

### 5.4 대조군 — 억제제 없는 PAA 분산 세리아 (Hwang, Lyu, Kim 2026, Polymers)
HNU15 세리아(1차입자 12.2 nm, Ce³⁺ 22.1 %) + PAA(Mw 21,300): HDP-SiO₂ **114.4 Å/min, Si₃N₄ 14.3 Å/min → 선택비 8.0**; 상용
HC10(Ce³⁺ 17.7 %): 57.5/12.3 → 4.7 (Hwang et al. 2026 Fig.13·§3.8). §8 [D] 재현. 나이트라이드 억제제가 없으면 세리아라도
선택비는 한 자릿수 — 리뷰 표 I의 "PAA만 pH 7 ~50"(Srinivasan et al. 2015 표 I 11행, 2차)과 차이가 크며 PAA 분자량·농도·pH(여기선
pH 9.1)·낮은 절대 RR(실험실 툴) 때문으로 보이나 **원인 미검증**. 교훈: "세리아 = 고선택비"가 아니라 "세리아 + 나이트라이드
흡착억제제 = 고선택비".

### 5.5 리뷰 표 I 요약(Srinivasan et al. 2015; 2차 인용, 값은 슬러리·조건 의존이라 정밀도 없음)
세리아 + 첨가제 계열 선택비: KHP+Zonyl 68-246(pH 6.5-7), 아미노프로필실란 54-233, L-프롤린 등 아미노산 42-306(pH 6-11),
글루탐산 >100(pH 5-7), 환형 아민 >100(pH 4-5; = [D]), PAA ~50, TEA ~60, 아스파르트산 ~100. 실리카 + 음이온 계면활성제
20-700(pH 2-4). 리뷰 자체가 "small changes in nitride rate → 선택비 급변, 정밀값으로 보지 말 것"이라 경고.

## 6. 디싱·침식과 선택비·오버폴리시·밀도 — 정리

1. **디싱은 오버폴리시 시간의 함수**: D(t)가 τ_nit로 D_ss에 수렴(식 2.54). 2차 인용(Lim et al., Srinivasan 리뷰): 10 µm 트렌치에서
   디싱은 오버폴리시 시간과 함께 증가, 입경(45/175/225 nm)이 클수록 약간 더 큼.
2. **첨가제로 디싱을 줄이는 길은 "옥사이드도 멈추게" 하는 것**: 2차 인용 Seo et al.(리뷰 §패턴 STI): 세리아 pH 5, 100 µm 라인,
   첨가제 없음(선택비 ~56) 디싱 800 Å(ρ 37.5 %)·200 Å(ρ 75 %) → PAA 0.8 wt% + PEG 0.3 wt%로 600·100 Å. 저밀도가 4배 큰
   것은 §4.2 함의 1(D_ss ∝ ρ(s−1)/(1+ρ(s−1))·d_max, d_max ∝ 1/ρ)과 방향 일치 — §8 [C]에서 비율 대조.
   Merricks(2차): 아미노산 슬러리는 나이트라이드 노출 후 ~6 s만 지나면 옥사이드·나이트라이드 모두 거의 멈춰(1:1) 오버폴리시
   무해, PAA 슬러리는 옥사이드가 계속 깎여 디싱·WIW 악화. 즉 **이상적 STI 슬러리는 "고선택비"가 아니라 "노출 후 자기정지
   (self-stopping)"**이다 — Nojo(2차, Lee 2002 Fig.3.15 재게재)의 임계압력형 세리아 슬러리(약 70 kPa 이하 RR≈0)와 같은 사상.
3. **Lee 2002 세리아 HSS 사례(§3.7, IC1400, 7 psi/30 rpm)**: 블랭킷 RR은 압력에 대해 거의 Preston(1 psi 450 → 9 psi 4700 Å/min,
   Fig.3.16 판독), 그러나 패턴 웨이퍼는 **28 s 활성화 지연**(t' = t − 28 s, 식 3.45) 뒤에야 제거 시작. 밀도구조별 추출값(표 3.9):
   D_ss 2021/1873/1532 Å(ρ 0.5/0.7/0.9), τ_nit ≈ 32 s 일정, K_ss 1367/903/465 Å/min; 지수 적합 D_ss = 2862·exp(−ρ/1.51),
   K_ss = 4784·exp(−ρ/0.40), K_n1 = 11573·exp(−ρ/0.28) (Lee 2002 표 3.10; §8 [C] ±8 % 재현), PL 1.6 mm(Phase 1)/4.7 mm(Phase 2) (Lee 2002 §3.7.9). ρ = 0.2·0.3은 침식이 심해
   Phase 2 데이터 없음. 결론(원문): "세리아 HSS는 통상 STI 공정과 비슷한 침식·디싱" — 고선택비가 디싱을 줄이지 않는다는 실측.
   표 3.9의 Phase 1 K1(ρ)은 식 3.46(A 9225, B 0.59)으로 재현되지 않음 — §8 [C]에 정직 기록.
4. **오버폴리시 창(내 유도, 미검증)**: 정상상태 뒤 침식은 K_ss로 선형이므로 나이트라이드 손실 예산 E_max에 대해 허용 오버폴리시
   ≈ (E_max − 과도항)/K_ss. K 2000 Å/min·ρ 0.5에서 s = 10이면 K_ss 364 Å/min, s = 100이면 40 Å/min — 예산 300 Å 기준 창이
   0.8 → 7.5 min으로 9배 넓어진다(§8 [B]). **고선택비의 진짜 가치는 디싱 감소가 아니라 침식 예산 대비 오버폴리시 창 확대**다.

## 7. 한계·불명확 (정직하게)
- (a) Lee 모델은 최소 피처 10 µm 마스크로 검증됨 — 선폭·피치 의존(Cu의 Tugbawa 확장)은 STI에서 미연구(원문 §2.13). 서브µm
  트렌치의 입자 포획(down-area particle trapping)·자기정지 슬러리는 모델 밖(§3.7 서두).
- (b) 표 2.4·3.9 값은 IPEC 472 + 특정 슬러리의 것 — 우리 툴에는 **입력값이 아니라 파라미터 형태만** 가져온다.
- (c) Dandu·Mariscal의 선택비는 블랭킷값. 패턴 웨이퍼 선택비는 더 낮다(2차: Merricks) — Lee 표 2.4가 실리카에서 보여준 조건
  의존과 합쳐 "s는 특성화 마스크에서 추출할 파라미터"로 취급.
- (d) Urban 2016은 벤더 슬라이드 — 수치는 경향 확인용, **미검증**. Hwang 2026과 리뷰 PAA 값의 6배 차이 원인 미검증.
- (e) 식 2.36 부호 오기 판단은 내 재유도·수치적분 근거이며 저자 정오표를 찾지 못했다(미검증).
- (f) 유료 3편(Lee 2007 MEE·Hwee 2001 JEM·Chang 2005 MEE)은 미러 사이트 전 미러 사망으로 본문 미확보.

## 8. 검증 — 원문 수식·수치 재현 (```python verify```, 실제 실행)

**재현 요약(한 줄)**: Lee 2002 식 2.32/2.33/2.38/2.47-2.49 자기일관 + ODE 수치적분이 D_ss 327 Å·τ_nit 10.9 s(K 2000 Å/min, s 10, τ₂ 60 s, ρ 0.5)로 수렴, 표 3.10 지수식이 표 3.9 D_ss·K_ss·K_n1을 ±8 % 재현, Dandu 2009 선택비 4.4/175/290·Hwang 2026 8.0/4.7 재현 (Lee 2002; Dandu Veera et al. 2009; Hwang et al. 2026) — 아래 verify 4블록 PASS.

```python verify
# [A] Lee 2002 (MIT thesis, hdl 1721.1/29907) Phase 2 STI model — 자기일관 + ODE 수치적분
import math
K, s, tau2, rho = 2000.0/60.0, 10.0, 60.0, 0.5      # Å/s, -, s, - (원문 §2.12 예시값)
dmax   = K*tau2/(s*rho)                              # 식 2.47
tau_n  = tau2/(1+(s-1)*rho)                          # 식 2.48
Dss_49 = K*tau_n*(s-1)/s                             # 식 2.49
Dss_32 = dmax*rho*(s-1)/(rho*(s-1)+1)                # 식 2.32
Kss_33 = K/(rho*(s-1)+1)                             # 식 2.33
tau_38 = (dmax/K)*s*rho/(1+rho*(s-1))                # 식 2.38
assert abs(Dss_49-Dss_32) < 1e-9 and abs(tau_n-tau_38) < 1e-9
RRa = lambda H: (K/s)*(1/dmax)*((1-rho)/rho)*H + K/s  # 식 2.34 (nitride, up)
RRf = lambda H: -(K/dmax)*H + K                       # 식 2.35 (trench oxide, down)
assert abs(RRa(Dss_32)-Kss_33) < 1e-9 and abs(RRf(Dss_32)-Kss_33) < 1e-9   # 정상상태: 두 RR = K_ss
# ODE: dH/dt = RR_f - RR_a  (H = 디싱). 인쇄본 식 2.36 상수항 부호(-K(1-s)/s)로는 -D_ss로 수렴 → 오기 판단
H, dt, hn = 0.0, 0.01, 0.0
for i in range(int(20*tau_n/dt)):
    H += dt*(RRf(H)-RRa(H))
    if i == int(tau_n/dt): H_at_tau = H
assert abs(H-Dss_32) < 1e-3*Dss_32                            # 정상상태 디싱으로 수렴
assert abs((Dss_32-H_at_tau)/(Dss_32-hn) - math.exp(-1)) < 0.01   # 시정수 = τ_nit (식 2.41)
H2 = 0.0
for i in range(int(20*tau_n/dt)):
    H2 += dt*( -(K/dmax)*((1+rho*(s-1))/(s*rho))*H2 + K*(1-s)/s )   # 인쇄본 식 2.36 그대로
assert abs(H2 + Dss_32) < 1e-3*Dss_32                         # → -D_ss : 부호 모순 확인
print(f"[A] d_max={dmax:.0f} Å, τ_nit={tau_n:.1f} s, D_ss={Dss_32:.0f} Å, K_ss={Kss_33*60:.0f} Å/min; ODE 수렴 OK, 식2.36 인쇄부호는 -D_ss")
```

```python verify
# [B] Lee 2002 §2.12 예시 파라미터로 밀도별 D_ss·K_ss·오버폴리시 창 (Fig.2.23 컬러바 400-1000 Å 오더 대조)
K, tau2 = 2000.0, 60.0    # Å/min, s
def dss(rho, s):  return (K/60)*tau2/(1+(s-1)*rho)*(s-1)/s
def kss(rho, s):  return K/(1+rho*(s-1))          # Å/min
vals = {r: dss(r, 10) for r in (0.1, 0.2, 0.5, 0.9)}
assert abs(vals[0.1]-947) < 2 and abs(vals[0.5]-327) < 2 and abs(vals[0.9]-198) < 2
assert vals[0.1] > vals[0.2] > vals[0.5] > vals[0.9]           # 저밀도가 큰 디싱 (Fig.2.23 서술)
assert 198 <= vals[0.5] <= 1000 and 400 <= vals[0.1] <= 1000    # 컬러바 오더
# 선택비↑ → D_ss↑, K_ss↓ (§4.2 함의 1) — d_max 고정(ρ=0.5, s=10, τ2=60 s에서 d_max = Kτ2/(sρ) = 400 Å) 비교
dmax0 = (K/60)*tau2/(10*0.5); assert abs(dmax0-400) < 1e-9
dss_fixed = lambda s, rho=0.5: dmax0*rho*(s-1)/(1+rho*(s-1))         # 식 2.32
assert abs(dss_fixed(10)-dss(0.5, 10)) < 1e-9                          # 두 표현 동일 (식 2.32 = 2.49)
assert dss_fixed(100) > dss_fixed(10) > dss_fixed(2) and abs(dss_fixed(100)-392) < 1
assert dss_fixed(1e6) > 0.999*dmax0                                     # s→∞ 에서 d_max
assert abs(kss(0.5, 10)-363.6) < 0.5 and abs(kss(0.5, 100)-39.6) < 0.5
assert kss(0.5, 10) > K/10                                        # K_ss > K_nit (압력 집중)
win10, win100 = 300/kss(0.5, 10), 300/kss(0.5, 100)              # 예산 300 Å 오버폴리시 창(min), 과도항 무시
assert abs(win100/win10 - 9.1) < 0.2
print(f"[B] D_ss(ρ=.1/.5/.9, s=10)={vals[0.1]:.0f}/{vals[0.5]:.0f}/{vals[0.9]:.0f} Å; K_ss s=10/100 = {kss(.5,10):.0f}/{kss(.5,100):.0f} Å/min; 창 {win10:.1f}→{win100:.1f} min")
```

```python verify
# [C] Lee 2002 표 3.9 (세리아 HSS 추출값) vs 표 3.10 지수 적합 D_ss=A·exp(-ρ/B); Seo(2차) 밀도별 디싱 비율 대조
import math
tab39 = {0.5: (2021, 1367, 1902), 0.7: (1873, 903, 903), 0.9: (1532, 465, 465)}   # ρ: (D_ss Å, K_ss, K_n1 Å/min)
fit = {"Dss": (2862, 1.51), "Kss": (4784, 0.40), "Kn1": (11573, 0.28)}
worst = 0
for rho, (d, k, kn) in tab39.items():
    for name, meas in zip(("Dss", "Kss", "Kn1"), (d, k, kn)):
        A, B = fit[name]; calc = A*math.exp(-rho/B)
        err = abs(calc-meas)/meas; worst = max(worst, err)
        assert err < 0.085, f"{name} ρ={rho}: {calc:.0f} vs {meas}"
assert worst > 0.07          # 최대 오차 ~8 % (K_ss ρ=0.7/0.9) — 원문이 "reasonable fit"이라 한 수준
# Phase 1 K1(ρ) = A·exp(-ρ/B), A=9225, B=0.59 (식 3.46)는 표 3.9 K1을 재현하지 못한다 → 정직 기록
K1 = {0.2: 13537, 0.3: 12131, 0.5: 7644, 0.7: 5783, 0.9: 4609}
calc02 = 9225*math.exp(-0.2/0.59)
assert abs(calc02-K1[0.2])/K1[0.2] > 0.5          # 6573 vs 13537: 51 % 차이, 원인 미상(상수 오기 가능)
# 표 3.9 자체는 ln K1 vs ρ 선형(지수형)으로 잘 맞는다: 두 끝점으로 얻은 A≈18.4e3, B≈0.65
B_fit = -0.7/math.log(K1[0.9]/K1[0.2]); A_fit = K1[0.2]*math.exp(0.2/B_fit)
for rho, v in K1.items():
    assert abs(A_fit*math.exp(-rho/B_fit)-v)/v < 0.12                    # 5점 모두 ±12 % (ρ=0.5가 최대)
# 세리아 HSS 블랭킷(Fig.3.16 판독): 거의 Preston — 1 psi 450, 5 psi 2550, 9 psi 4700 Å/min → 기울기 ≈ 530 Å/min/psi
slope = (4700-450)/8; assert 500 < slope < 560
# Seo et al.(리뷰 2차): 디싱 800 Å(ρ .375) vs 200 Å(ρ .75) — Lee 식 2.32에 d_max∝1/ρ 넣으면 D_ss ∝ (s-1)/(1+ρ(s-1)); s=56
r = (1+0.75*55)/(1+0.375*55)          # = D_ss(.375)/D_ss(.75) 모델 비율
assert 1.9 < r < 2.0 and 800/200 == 4.0   # 모델 1.96배 vs 실측 4배 — 방향 일치, 크기 2배 차이(선폭·h_n 효과 미포함, 미검증)
print(f"[C] 표3.10 적합 최대오차 {worst*100:.1f} %; K1 식3.46 불일치 {abs(calc02-K1[0.2])/K1[0.2]*100:.0f} %(재적합 A={A_fit:.0f},B={B_fit:.2f}); Seo 비율 모델 {r:.2f} vs 실측 4")
```

```python verify
# [D] 블랭킷 선택비 재현: Dandu Veera 2009 (doi:10.1149/1.3230624), Mariscal 2020 (doi:10.1149/2162-8777/ab89bc),
#     Hwang 2026 (doi:10.3390/polym18151899), Urban 2016 (벤더 슬라이드)
ox, ni = 350.0, 80.0                        # nm/min, 60 nm 세리아 0.25 %, 첨가제 없음, pH 4-5.5
assert abs(ox/ni - 4.375) < 1e-9
sel_pyr = 350.0/2.0; sel_180 = 580.0/2.0    # + 피리딘·HCl 0.05 %; 180 nm 세리아 1 %
assert sel_pyr == 175 and sel_180 == 290 and sel_pyr > 100      # 리뷰 표 I 15행 ">100"과 정합
assert sel_pyr/(ox/ni) == 40.0                                   # 첨가제 0.05 %로 선택비 40배
# Fig.14: 나이트라이드는 30 s에 3 nm(자연산화층)만 → 200 s까지 0 → 실효 K_nit ≈ 3 nm/200 s
assert 3/(200/60) < 1.0                                          # < 1 nm/min (리뷰 기준 충족)
# Mariscal 2020: 선택비 32-101, 실리카 4:1; 패턴 클리어 6 min vs 6000/2528 Å/min
assert 32 <= 44 <= 101 and 101/4 > 25
t_naive = 6000/2528; assert abs(t_naive-2.37) < 0.01 and 6/t_naive > 2.4
# Hwang 2026: 억제제 없는 PAA 세리아
assert abs(114.4/14.3 - 8.0) < 0.05 and abs(57.5/12.3 - 4.67) < 0.01
# Urban 2016 (미검증 벤더값): HDP 2000-3500, nitride <20 → 선택비 >100
for rr in (2000, 2700, 3500, 3400, 2800):
    assert rr/20 >= 100                                              # 1세대 2000/20 = 100 (경계)
assert 2000/10 == 200
print(f"[D] Dandu: 무첨가 {ox/ni:.1f} → 피리딘 {sel_pyr:.0f}/{sel_180:.0f}; Mariscal 32-101(실리카 4); Hwang {114.4/14.3:.1f}/{57.5/12.3:.1f}; Ferro >100-200")
```

**결과 해석(정직하게)**
- [B]의 "s↑ → D_ss↑"는 d_max 고정 가정에서만 성립한다. 원문 표 2.4처럼 τ₂를 추출 파라미터로 잡으면 s와 τ₂가 함께 움직여 겉보기 경향이 달라질 수 있다.
- [A]는 원문 식들의 **수학적 자기일관**과 부호 오기 확인이지 실험 검증이 아니다. D_ss·τ_nit 절댓값은 §2.12 예시 입력값의 함수.
- [B]의 컬러바 대조는 그림 판독(±100 Å)이고 시각·h_n을 모르므로 오더만. 오버폴리시 창 9배는 내 유도(과도항 무시).
- [C]의 표 3.10 적합은 원문 표를 재계산한 것(±8 %). 식 3.46의 K1 불일치는 원문 상수 오기 가능성이 크나 확인 못 함. Seo 비율은
  2차 인용값에 단순 모델을 대본 것 — 2배 차이는 선폭 100 µm·과도항 효과가 빠진 탓일 수 있음(미검증).
- [D]는 블랭킷 수치의 나눗셈 재현. 패턴 웨이퍼 선택비는 이보다 낮다(2차: Merricks).

## 9. 옥사이드 전문가 관점 결론

1. **STI CMP 모델 = Phase 1(ILD 밀도모델 그대로) + Phase 2(2물질 removal-rate diagram)**. Phase 2의 새 파라미터는 s·τ₂·PL_nit
   셋뿐이고, 디싱·침식·클리어 시각이 모두 폐형으로 나온다(Lee 2002 식 2.41-2.56). 이것이 sim/tier1 STI 모듈의 뼈대여야 한다.
2. **선택비는 디싱을 줄이지 않는다.** d_max 고정 시 D_ss = d_max·ρ(s−1)/(1+ρ(s−1))는 s에 단조증가, s→∞에서 d_max. 선택비의 가치는 K_ss ≈ K_nit/ρ를
   줄여 **침식 예산 대비 오버폴리시 창을 넓히는 것**이다(§6-4). 디싱을 줄이려면 옥사이드 쪽도 노출 후 자기정지하는 슬러리
   (아미노산 1:1 거동, 임계압력형)나 낮은 d_max(단단한 패드·짧은 PL_nit)가 필요.
3. **s는 상수가 아니다** — 실리카 표 2.4에서 2.7-38, 세리아 Mariscal에서 32-101(P·V 의존), 블랭킷→패턴에서 더 낮아짐. 캘리브레이션
   층(Cal-1)에서 s는 "슬러리 스펙"이 아니라 **특성화 마스크에서 추출하는 공정 파라미터**로 스키마에 넣어야 한다.
4. 세리아 HSS 고유 거동 두 가지는 Preston 밖: **활성화 지연(28 s)**과 **밀도 무관 K₂·h_c**(Lee §3.7) — Phase 1 방정식에 t' = t − t_off를
   넣고 K1(ρ)를 지수형으로 두는 "일반화 모델"(Lee 3장)이 필요. Mariscal의 "제거량이 시간에 비례하지 않음"도 같은 계열.
5. 나이트라이드 정지의 화학([[ceria-slurry-ce-redox-selectivity]] §5)은 여기서 **K_nit ≈ 0 + 노출 직후 3 nm 과도 제거**로 요약된다
   (Dandu Fig.14). 모델에서는 K_nit → 0이 K_ss → 0·D_ss → d_max로 이어지므로 d_max(=Kτ₂/(sρ))의 독립 추정이 세리아 STI 모델링의 급소.

## 10. 구현 요청 → agents/film-oxide/PROFILE.md "## 구현 요청" 참조
(Lee 2002 Phase 2 폐형해 식 2.32-2.56 + touch-down 시각 식 2.50-2.53 + 세리아 HSS 일반화(t_off, 지수형 D_ss/K_ss/K_n1) — 현재
`sim/tier1_empirical/pattern_density.py`에는 STI 2물질 단계가 없음.)

## 11. 자기시험
→ [[../../agents/film-oxide/EXAMS.md]] Lv2-2 문항 참조.

## 12. κ 농도항 — sti_ceria 팩의 실리카 상속 결함 정정 (2026-09-16, 판정#48)

### 12.1 무엇이 틀려 있었나
`knowledge/params/sti_ceria.yaml`은 `abrasive_wt_pct`·`abrasive_ref_wt_pct`·`abrasive_conc_exponent`
세 키를 선언하지 않아 부모 팩 `oxide_silica`에서 상속받고 있었다. 부모 값은 **콜로이달 실리카
20 wt% 고형분**(US9499721B2 TEOS 계) 기준인데, 세리아 STI 슬러리의 실사용 농도는 0.25~1 wt% 대다.
그래서 `κ`의 농도항이 기준조건에서 1.0이 아니라 `(0.25/20)^(1/3) = 0.232` 로 눌려 있었다 —
**4.31배 계통 과소** 이며, 이것이 백테스트가 4회차 연속 최상위 갭으로 지목한
`dandu2009_sio2_ceria_ph_sweep: 절대값 3.20배 계통편향`의 직접 원인이다.

판정#16(`abrasive_ref_size_nm`이 실리카 부모의 50 nm를 상속해 κ=1.275였던 건)과 **같은 유형**의
하이진 결함이다. 그때 입경 기준점만 고치고 농도 기준점은 남겨뒀다.

### 12.2 값을 어디서 가져왔나 (Dandu 2009 Figure 2a, 1차 원문 벡터좌표)
`papers/dandu2009-jes-selective-sio2-sin-ceria-sti.pdf` p.3의 Figure 2a는 **60 nm 세리아, pH 4**에서
입자 loading 0.25 / 0.50 / 1.0 wt%의 oxide·nitride RR을 준 막대그래프다. PyMuPDF `get_drawings()`로
막대 사각형의 상단 y좌표를 뽑아 축 눈금 라벨(0 nm/min ↔ y=236.4, 400 nm/min ↔ y=110.3)에
선형사상했다(눈대중 아님).

| loading (wt%) | 막대 상단 y | oxide RR (nm/min) |
|---|---|---|
| 0.25 | 125.4 | **352.1** |
| 0.50 | 169.8 | **211.3** |
| 1.00 | 175.2 | **194.1** |

본문 서술이 같은 방향을 독립적으로 뒷받침한다 — *"The oxide RR at pH 4 was higher with 0.25%
ceria particle loading, as shown in Fig. 2a, compared to 0.5 and 1%."*

### 12.3 이 계에서 농도 지수는 **음수**다 — 그리고 입경에 따라 부호가 갈린다
로그-로그 회귀 결과 **n = −0.4295**(최대잔차 15.3%). 부모의 +1/3(표면적 극한)과 부호가 반대다.

그런데 **같은 논문 Figure 2b(180 nm Ferro 소성 세리아)는 부호가 반대다**: 같은 방법으로 읽으면
390.0 / 505.0 / 627.8 / 495.0 nm/min(0.25/0.5/1/2 wt%)이고 0.25~1.0 구간 지수는 **+0.343**이다.
즉 농도 지수는 재료 상수가 아니라 **입자 크기·소성 이력에 따라 부호가 갈리는 양**이다.
이 팩의 입자는 Fig.2a의 60 nm이므로 EVIDENCE-RULES §서열(등급 동률 시 계 근접도)에 따라
Fig.2a를 채택했다. 입경 분기 파라미터 신설은 **제안만 하고 구현하지 않는다** — 데이터 2점으로
분기축을 만들면 과적합이다.

### 12.4 검증 — 판독·회귀·자기일관

```python verify
import math

# ── (A) Figure 2a 벡터좌표 → nm/min 선형사상 (축 눈금 0↔y=236.4, 400↔y=110.3) ──
def to_rr(y, y0=236.4, v0=0.0, y1=110.3, v1=400.0):
    return v0 + (y - y0) * (v1 - v0) / (y1 - y0)

BAR_TOP_2A = {0.25: 125.4, 0.50: 169.8, 1.00: 175.2}   # get_drawings() 실측 y
A = {c: to_rr(y) for c, y in BAR_TOP_2A.items()}
assert abs(A[0.25] - 352.1) < 0.5, A
assert abs(A[0.50] - 211.3) < 0.5, A
assert abs(A[1.00] - 194.1) < 0.5, A
# 본문 서술("0.25%가 0.5·1%보다 높다")과 판독이 일치하는가
assert A[0.25] > A[0.50] > A[1.00]

# ── (B) 자기검증: Fig.2a의 0.25%와 Fig.3(다른 그림)의 pH4 독립 판독값 대조 ──
FIG3_PH4 = 347.4      # validation/datasets/dandu2009_sio2_ceria_ph_sweep.yaml (기존 등록값)
dev = abs(A[0.25] - FIG3_PH4) / FIG3_PH4 * 100
assert dev < 2.0, f"독립 판독 불일치 {dev:.1f}%"

# ── (C) 로그-로그 회귀로 농도 지수 ──
def loglog_exponent(d):
    xs = [math.log(c) for c in d]; ys = [math.log(v) for v in d.values()]
    n = len(xs); mx = sum(xs)/n; my = sum(ys)/n
    num = sum((x-mx)*(y-my) for x, y in zip(xs, ys))
    den = sum((x-mx)**2 for x in xs)
    slope = num/den; a0 = my - slope*mx
    resid = [abs(math.exp(a0+slope*x)-v)/v*100 for x, v in zip(xs, d.values())]
    return slope, max(resid)

n_a, res_a = loglog_exponent(A)
assert abs(n_a - (-0.4295)) < 0.002, n_a          # 팩에 넣은 값 그대로
assert n_a < 0                                     # 음수 = 더 넣으면 덜 깎인다
assert res_a < 16.0, res_a                         # n=3 그래프 판독의 정직한 잔차

# ── (D) Figure 2b(180 nm 세리아)는 부호가 반대 — 일반화 금지 근거 ──
BAR_TOP_2B = {0.25: 337.2, 0.50: 316.5, 1.00: 294.4, 2.00: 318.3}
B = {c: to_rr(y, 407.4, 0.0, 281.4, 700.0) for c, y in BAR_TOP_2B.items()}
n_b, _ = loglog_exponent({c: v for c, v in B.items() if c <= 1.0})
assert n_b > 0, n_b                                # 60nm과 부호 반대
assert n_a * n_b < 0                               # 명시적으로 '갈린다'

# ── (E) 결함의 크기: 기준점 상속이 만들던 계통 과소 배수 ──
inherited_ref, inherited_n = 20.0, 1/3.0           # oxide_silica 부모값
term_before = (0.25 / inherited_ref) ** inherited_n
assert abs(term_before - 0.2321) < 0.001, term_before
assert abs(1.0/term_before - 4.308) < 0.01         # 4.31배 과소 — 관측 편향 3.20배와 같은 자릿수
# 고친 뒤 기준조건 배수는 항등적으로 1.0
assert (0.25/0.25) ** n_a == 1.0

print(f"(A) Fig2a 판독 {[round(v,1) for v in A.values()]} nm/min — 본문 서술과 순서 일치")
print(f"(B) 자기검증: Fig2a 0.25%={A[0.25]:.1f} vs Fig3 pH4={FIG3_PH4} → {dev:.1f}% 차")
print(f"(C) 농도 지수 n={n_a:+.4f} (최대잔차 {res_a:.1f}%)")
print(f"(D) Fig2b(180nm) n={n_b:+.4f} — 부호 반대, 입경 의존 확인")
print(f"(E) 상속 결함 크기 = {1.0/term_before:.2f}배 과소 (관측 편향 3.20배)")
```

### 12.5 효과와 한계 (실행 확인)
`validation/backtest.py` 실측: `dandu2009_sio2_ceria_ph_sweep` 계통편향 **3.20배 → 0.74배**
(±2배 경고창 안으로 복귀, 순위 ρ=+0.933 불변 — 농도가 전 조건 고정이라 순위는 원래 안 움직인다).
같은 팩의 `netzband2020_thermal_oxide_ceria_ph`도 0.749→0.500으로 이동했다(1 wt% 조건이라 농도항이
같이 바뀜) — **개선이라고 주장하지 않는다.** 그 데이터셋은 ρ=−0.800·p=0.958로 애초에 비유의라
스케일 논의의 대상이 아니다. `mariscal2020`·`kenchappa2021`은 농도 override가 없어 비트 단위 불변.

한계: (1) n=3 그래프 판독이라 잔차 15.3%가 남는다. (2) §12.3의 입경 부호 반전 때문에 이 지수는
**60 nm급 세리아에만** 적용된다 — 180 nm급으로 외삽하면 방향이 틀린다. (3) 이 파라미터는
`dandu2009` 데이터셋과 같은 논문에서 왔으므로 그 데이터셋 YAML에 `calibration_contact`로 신고했다
(qa_loop 감사에서 F4→C4로 전환 확인).
