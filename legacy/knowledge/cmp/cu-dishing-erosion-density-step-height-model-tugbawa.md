<!-- V2-SECTION: R5-wafer | 공동: R2-slurry | 분배완료 2026-09-09 | 근거: dishing, erosion, pattern-, 선폭, dmax | 정본: ARCHITECTURE-V2.md §3 -->
# Cu dishing·erosion 물리 — Hooke 압력분배·removal-rate diagram·dmax(선폭·스페이스)·밀도 의존 (film-cu Lv2-1)

> film-cu Lv2-1 | 작성일: 2026-09-09
> 선행: [[pattern-dependent-dishing-erosion]] (MRS99 밀도모델·정상상태 dishing 개념 — 그 노트는 "절대 dishing nm값 미검증,
> dmax·b는 합성값"을 한계로 남겼다. 이 노트는 그 빈칸을 채운다: Tugbawa 2002 학위논문의 **닫힌 해석해**와
> **추출 파라미터 실측표**로 dishing/erosion의 시간·밀도·선폭·스페이스 의존을 정량화한다)
> [[pattern-metrics-dishing-erosion-stepheight]] (dishing/erosion 기준면 정의 3종 — 이 노트는 Park 1998 정의를 따른다)
> [[cu-cmp-three-step-process-slurry-requirements]] (3단계 공정 — 여기서 각 단계의 r_cu·r_ox가 왜 다른지 §5)
> [[cu-electrochemistry-pourbaix-bta-oxidizer-inhibitor]] (정적식각 SER — 패드 비접촉 저지대의 제거를 담당, §6 구현요청)
> [[npw-ptw-pattern-effect-gw-physics]] (Vasilev 2011 확장 GW — 선폭 효과의 미시 근거·밀도-스텝하이트 모델의 한계 대조)
> [[hertz-gw-contact-mechanics]] [[preston-luo-dornfeld-mrr]] [[wiwnu-pressure-velocity-wafer-scale]]
> 스코프: (1) 오버폴리시 단계의 압력-dishing Hooke 관계와 removal-rate diagram, (2) dishing·erosion의 닫힌 시간해
> (D_ss, τ₃, Y₁, Y₂), (3) 패턴 의존성 — 밀도 Φ_cu는 erosion을, 선폭 w·스페이스 s는 d_max를 통해 dishing을 지배,
> (4) 엣지 라운딩 ψ(s)·ear 효과·과도 오버폴리시 등 모델 한계, (5) 문헌 파라미터로 verify.

## 0. 출처 (6건, 1차 원문 4건)
1. **[1차·원문 전체]** T. E. Tugbawa, "Chip-Scale Modeling of Pattern Dependencies in Copper Chemical Mechanical Polishing
   Processes," PhD thesis, MIT EECS, 2002. https://dspace.mit.edu/handle/1721.1/8083 (papers/tugbawa2002-thesis-mit-chip-scale-cu-cmp.pdf,
   232쪽, 텍스트 추출 + 수식 페이지는 fitz 렌더 후 판독). 이 노트의 수식 번호(eq 3.19–3.53)·표(Table 3.1/3.3/3.9/3.10)는 모두 이 논문.
2. **[1차·원문 전체]** T. Tugbawa, T. Park, D. Boning, L. Camilletti, M. Brongo, P. Lefevre, "Modeling of Pattern Dependencies in
   Multi-Step Copper Chemical Mechanical Polishing Processes," *CMP-MIC* 2001, Santa Clara. (papers/tugbawa2001-cmpmic-cu-model.pdf,
   boning.mit.edu 리프린트; 2단계 공정 dishing/erosion 시간 데이터 Fig 3–6). DOI 없음(학회).
3. **[1차·원문 전체]** T. Park, T. Tugbawa, J. Yoon, D. Boning, J. Chung, R. Muralidhar, S. Hymes, Y. Gotkis, S. Alamgir, R. Shinde,
   L. Kamilletti, "Pattern and Process Dependencies in Copper Damascene CMP Processes," *VMIC* 1998
   (papers/park1998-vmic-cu-damascene.pdf). 선폭·피치·밀도 실측 트렌드와 break point.
4. **[1차·원문 전체, 시뮬레이터 출력 주의]** Ruan Wenbiao, Chen Lan, Li Zhigang, Ye Tianchun, "Effects of pattern characteristics on
   copper CMP," *J. Semicond.* 30(4) 046001 (2009), doi.org/10.1088/1674-4926/30/4/046001 (Crossref 실존 확인, Wayback 경유 원문 PDF
   papers/ruan2009-jos-pattern-effects-cu-cmp.pdf). 밀도 0.7 이상 포화 — 단 본문이 "process model simulations"에서 얻은 결론이라
   밝히므로 **실측 아닌 모델 출력**으로 취급한다.
5. **[초록만]** J. M. Steigerwald, R. Zirpoli, S. P. Murarka, D. Price, R. J. Gutmann, "Pattern Geometry Effects in the Chemical-Mechanical
   Polishing of Inlaid Copper Structures," *J. Electrochem. Soc.* 141(10) 2842–2848 (1994), doi.org/10.1149/1.2059241 (Crossref 서지·OpenAlex
   초록 확인. 본문 유료 — 미러 사이트 .box/.red/.ru 2026-09-09 모두 캡차/차단, **초록만**).
6. **[1차·원문 전체]** A. Vasilev, R. Rzehak, S. Bott, P. Kücher, J. W. Bartha, "Greenwood–Williamson Model Combining Pattern-Density and
   Pattern-Size Effects in CMP," *IEEE Trans. Semicond. Manuf.* 24(2) 338–347 (2011), doi.org/10.1109/TSM.2011.2107756
   (papers/vasilev2011-gw-pattern-density-size-cmp.pdf). 밀도-스텝하이트 모델이 설명 못 하는 "순수 선폭 효과"의 대조군.

## 1. 물리 — 왜 Cu는 파이고 산화막은 얇아지는가 (Hooke 압력분배)
[[pattern-dependent-dishing-erosion]] §4가 정성적으로 적은 "removal-rate diagram"의 물리적 뿌리는 **패드를 국소 선형 스프링(Hooke)으로
보는 압력 분배**다. 오버폴리시 단계(intrinsic stage three)에서 트렌치 Cu(down-area), 스페이스 유전체(up-area)가 동시에 갈린다.
Cu가 dishing D_cu만큼 파이면 패드가 그만큼 덜 눌러 Cu 위 압력은 선형으로 줄고, 그 몫이 유전체로 옮겨간다 (Tugbawa 2002 eq 3.31–3.32,
Fig 3.9):

```
P_ox = P₁ + P₁ · (Φ_cu/(1−Φ_cu)) · (D_cu/d_max)        (up-area, 유전체)      eq 3.31
P_cu = P₁ · (1 − D_cu/d_max)                           (down-area, Cu)        eq 3.32
```
- Φ_cu: 평탄화길이 L₃로 가중평균한 **유효 레이아웃 Cu 밀도**(스테이지 1의 전기도금 밀도 ρ_cu와 구분). 1−Φ_cu가 유전체 밀도.
- **d_max(최대 dishing)**: "Cu 위 압력이 0이 되는 dishing" — 패드가 트렌치 안으로 얼마나 파고들 수 있는가를 나타내는 **패턴 의존 파라미터**
  (선폭 w·스페이스 s의 함수, §3). 유전체 제거율이 0이면 d_max = 정상상태 dishing(Tugbawa 2002 §3.4.2 정의).
- 면적가중 평균압은 항상 P₁로 보존된다: (1−Φ)·P_ox + Φ·P_cu = P₁ (아래 verify 1에서 대수적으로 확인).

Preston형(RR ∝ P)을 대입하면 removal-rate diagram(eq 3.33–3.34, Fig 3.10):
```
RR_ox = r_ox + r_ox · (Φ_cu/(1−Φ_cu)) · (D_cu/d_max)    (dishing↑ → 유전체 제거율↑, 기울기 ∝ Φ/(1−Φ))
RR_cu = r_cu · (1 − D_cu/d_max)                          (dishing↑ → Cu 제거율↓, d_max에서 0)
dD_cu/dt = RR_cu − RR_ox,     dE_ox/dt = RR_ox            eq 3.35–3.36
```
r_cu, r_ox는 **유효 블랭킷 제거율**(순간값). 두 직선이 만나는 D_ss가 정상상태 dishing이고, 그 뒤 erosion은 선형으로 계속 증가한다.
같은 틀이 배리어 클리어 단계(stage two)에도 쓰인다 — 유전체 자리에 배리어(r_b), dishing 자리에 pre-dishing d_cu (eq 3.19–3.30).

## 2. 닫힌 시간해 — D_ss, τ₃, 선형 erosion (Tugbawa 2002 eq 3.37–3.43)
1차 선형 ODE라 해석해가 있다. t₃ = t₁ + t₂(벌크 Cu 클리어 + 배리어 클리어 시각), d₂ = 배리어 클리어 순간의 dishing:
```
D_cu(t) = d₂·e^{−(t−t₃)/τ₃} + D_ss·(1 − e^{−(t−t₃)/τ₃})                                   eq 3.37
E_ox(t) = Y₁·(t−t₃) + Y₂·(D_ss − d₂)·(e^{−(t−t₃)/τ₃} − 1)                                  eq 3.38
D_ss = d_max·(r_cu − r_ox)·(1−Φ_cu) / [r_cu(1−Φ_cu) + r_ox·Φ_cu]                            eq 3.39
τ₃  = d_max·(1−Φ_cu) / [r_cu(1−Φ_cu) + r_ox·Φ_cu]                                           eq 3.40
Y₁  = r_cu·r_ox / [r_cu(1−Φ_cu) + r_ox·Φ_cu]      (정상상태 erosion 속도)                     eq 3.41
Y₂  = r_ox·Φ_cu / [r_cu(1−Φ_cu) + r_ox·Φ_cu]                                                eq 3.42
```
읽는 법:
- **dishing은 지수적으로 포화**, 시간상수 τ₃ = d_max/(정상상태 Cu 제거율 상당). r_cu ≫ r_ox인 1단계 슬러리에서는 D_ss ≈ d_max·(1−Φ)/(1−Φ+Φ·r_ox/r_cu) —
  즉 **d_max에 거의 도달**하고(고립선 Φ→0이면 정확히 d_max·(1−r_ox/r_cu)), 밀도가 높을수록 D_ss < d_max로 줄어든다.
- **erosion은 정상상태 뒤 선형** 기울기 Y₁. Y₁은 Φ_cu에 단조증가(분모 r_cu(1−Φ)가 줄어드니까): 밀한 어레이일수록 유전체가 빨리
  깎인다 — 이것이 "erosion ∝ 밀도"의 수식적 실체. 반면 **Y₁에는 w·s가 직접 안 들어간다** — 선폭·스페이스 효과는 d_max(τ₃·Y₂)와
  §3.3 ψ(s)를 통해서만 들어온다(논문 스스로 "line space effect is currently treated as a second order effect", §3.5).
- r_cu < r_ox인 2단계(배리어) 슬러리에서는 D_ss < 0: Cu가 up-area가 되고 1단계에서 생긴 dishing이 **회복**된다(Tugbawa 2001 Fig 5:
  80 % 밀도 dishing 250 Å → 150 s 후 60 Å 판독). 다만 erosion은 계속 쌓여 두 밀도의 erosion이 r_ox 기울기로 수렴한다(Fig 6).

## 3. 패턴 의존성 — 밀도·선폭·스페이스가 들어오는 자리
### 3.1 밀도 Φ_cu → erosion (지배), dishing(2차)
- Tugbawa 2002 Fig 3.13–3.14: 두 광폭 규칙 어레이 w/s = 1/1 µm(Φ≈50 %)와 9/1 µm(Φ≈90 %)의 erosion-시간 판독값(그림 눈금, ±50 Å):
  90 %는 92→110 s에 1750→2850 Å, 50 %는 330→540 Å (Tugbawa 2002 Fig 3.14 판독). 기울기 약 61 vs 12 Å/s — **5배 차이**.
  verify 1에서 Table 3.9 파라미터로 Y₁을 계산해 대조한다.
- Steigerwald et al. 1994 초록: "erosion은 밀도에 강하게 의존하고 선폭에는 무관; dishing은 선폭에 강하게 의존하고 밀도에는
  미미" (doi.org/10.1149/1.2059241, **초록만**). Tugbawa 모델에서 이 분리는 Y₁(Φ)와 d_max(w,s)의 분리로 나타난다.
- Park 1998 VMIC: 피치 250 µm 고정에서 erosion은 밀도 ~60 % break point 이후 급증, dishing은 60–70 %(스페이스 100–75 µm)에서
  최대 후 급감 — 스페이스 > ~100 µm면 유전체가 패드를 지지 못해 가속 폴리시 (Park et al. 1998 원문). 이 "지지 상실"은 Hooke 선형
  분배로는 표현되지 않는 **비선형 접촉 효과**다([[npw-ptw-pattern-effect-gw-physics]]).
- Ruan et al. 2009 (doi.org/10.1088/1674-4926/30/4/046001) Fig 10–11: 밀도 0.3→0.9에서 dishing 500→1000–1200 Å(0.8에서 최대),
  erosion 50→700–800 Å로 **0.7 이상 포화** — 단 Preston+밀도-스텝하이트+접촉역학 시뮬레이터 출력이며 실측(AFM) 대조 수치는 본문에 없음.
  Tugbawa의 Y₁(Φ)는 포화하지 않고 Φ→1에서 r_ox·r_cu/(r_ox)=r_cu로 발산하므로, 포화는 접촉역학 항(또는 §4.2 과도 오버폴리시 효과)에서
  나온다고 보는 게 합리적(**추정**).

### 3.2 선폭 w·스페이스 s → d_max (dishing 지배)
Tugbawa 2002 §3.4.2: "선폭이 클수록 패드가 쉽게 파고들어 dishing↑, 단 증가율은 체감(sub-linear); 스페이스가 넓을수록 dishing↑,
역시 체감". 경험식 두 형태(어느 쪽이든 "good accuracy"):
```
eq 3.46:  d_max = B·(w/w₀)^α₂·(s/s₀)^β₂        (0 ≤ s < s_l)
                = B·(w/w₀)^α₂·(s_l/s₀)^β₂      (s ≥ s_l)      ← 스페이스 포화(dishing length scale s_l ≈ 100 µm)
eq 3.47:  d_max = B·(w/w₀)^α₂·ln(s/s_m)         (s ≥ s_m, s_m = 유효 최소 스페이스)
```
w₀ = s₀ = 1 µm, B[Å] ≥ 0, 0 < α₂, β₂ < 1. **추출값(Table 3.9/3.10, Mirra·EPC-5001 슬러리·4 psi·75 rpm·175 mL/min, MIT-SEMATECH 854 마스크)**:

| 실험세트 / 엣지라운딩 | r_cu 포화 a₁ (Å/s) | r_ox (Å/s) | L₃ (µm) | B (Å) | α₂ | β₂ | C | s_c (µm) | RMS (Å) |
|---|---|---|---|---|---|---|---|---|---|
| #1 Stacked pad, ψ 미포함 | 159 | 4.34 | 1309 | 294.2 | 0.303 | 0.292 | — | — | 107 |
| #1 Stacked pad, ψ 포함 | 159 | 2.22 | 1498 | 333.0 | 0.303 | 0.259 | 3.04 | 22.5 | 70 |
| #2 Solo pad, ψ 미포함 | 115 | 4.34 | 1385 | 337.0 | 0.174 | 0.240 | — | — | 74 |
| #2 Solo pad, ψ 포함 | 115 | 0.9 | 1529 | 372.4 | 0.188 | 0.185 | 7.4 | 15.4 | 46 |

(Tugbawa 2002 Table 3.9·3.10, 페이지 렌더 판독. r_cu는 eq 3.53 r(t)=a₁ − (a₂/τ_r)e^{−t/τ_r}의 포화값 a₁; #1: a₂=1176 Å, τ_r=7.7 s,
#2: a₂=2373 Å, τ_r=15.0 s. 오버폴리시 t≈100 s ≫ τ_r이라 r_cu ≈ a₁.)
- **Cu 평탄화길이 L₃ ≈ 1.3–1.5 mm** — MRS99/Park 1998이 말한 산화막 3–5 mm보다 짧지만, Park 1998의 "Cu 상호작용거리 50–100 µm"보다는
  훨씬 길다. 두 값은 정의가 다르다(L₃는 밀도 가중창, 50–100 µm는 어레이 가장자리 erosion 프로파일이 정상상태에 이르는 거리) —
  이 노트는 둘을 **다른 물리량**으로 병기하고 어느 쪽도 폐기하지 않는다.
- **선폭 지수 α₂ ≈ 0.17–0.30, 스페이스 지수 β₂ ≈ 0.19–0.29** — 둘 다 1보다 훨씬 작다: 선폭 10배에 dishing 1.5–2배. 이 체감이 왜
  생기는가는 Hooke 스프링 모델 밖의 질문이고, Vasilev 2011 확장 GW(트렌치 곡률 κ_D = κ_asp − 4αh/s²가 접촉압을 바꿈)가 답의 후보다.
- 고립선 실측(Tugbawa 2002 Fig 3.12, 엔드포인트 시각 dishing, 그림 판독 ±40 Å): w = 0.25/0.35/0.5/1/2/5/10 µm → 약 250/270/330/660/1000/1220/1400 Å.
  verify 3에서 멱법칙 지수를 판독값에서 뽑아 Table의 α₂와 대조한다.
- 서브마이크론 고립선도 판다(0.25 µm, 0.18 µm 고립선 dishing 관측, Fig 3.40) → d_max(0.25 µm) > 0. 반면 스테이지 1의 접촉높이 H_ex(0.25 µm) = 0.
  즉 d_max ≠ H_ex: "패드 압축만이 원인이라면 둘이 같아야 하는데 다르므로, d_max에는 슬러리·연마입자 효과가 섞여 있다"(Tugbawa 2002 §3.4.2).

### 3.3 스페이스 → erosion: 엣지 라운딩 ψ(s) (Tugbawa 2002 §3.5, eq 3.48–3.49)
밀도 모델은 스페이스 효과를 "2차"로만 담는데, 실측은 그렇지 않다. w = 20 µm 고정·s = 1→100 µm 가변 좁은 어레이(폭 ≈500 µm ≪ L₃, 밀도 효과
무시 가능)에서 114 s 오버폴리시 후 erosion이 s = 1 µm 2050 Å → 5 µm 1000 Å → 10 µm 480 Å → 20 µm 170 Å → 100 µm 60 Å (Tugbawa 2002 Fig 3.16 판독 ±50 Å).
원인: up-area 가장자리의 국소 압력 피크(스페이스가 좁을수록 두 피크가 겹쳐 델타형) → 모서리 라운딩 → 유효 스페이스 감소. 밀도 접근은
L₃ 창으로 평균하면서 이 피크를 지운다. 밀도-스텝하이트 틀 안의 임시방편:
```
r'_ox = ψ(s)·r_ox,    ψ(s) = C·e^{−s/s_c} + 1      (C ≥ 0, s_c = 엣지 라운딩 길이 ≈ 15–23 µm)
```
ψ를 넣지 않으면 부동(float) 추출된 r_ox가 **측정 블랭킷 유전체 속도(< 1 Å/s)의 6–10배**로 튀어 오른다(#1: 4.34 Å/s) — 모델이 스페이스 효과를
r_ox에 뭉뚱그려 흡수하기 때문. ψ 포함 시 r_ox는 2.22(#1)·0.9(#2) Å/s로 내려가고 RMS도 107→70, 74→46 Å로 준다(Table 3.9/3.10).
**이 "유효 r_ox 부풀림"은 Tugbawa 2001 데이터에서도 재현된다** — verify 2.

## 4. 모델 한계 (Tugbawa 2002 §3.9 — 구현 시 플래그 필수)
### 4.1 Ear(어레이 가장자리) 효과
더미필 없는 레이아웃에서 광폭 필드 옆 어레이 가장자리 Cu가 덜 파이거나 솟는다. 국소 배리어 양(넓은 필드 = 배리어 많음)과 관련 —
r_cu·r_b를 패턴 의존 함수로 만들어야 하지만 파라미터가 늘어 미해결. 고립선이 같은 폭 어레이선보다 더 파이는 것(Fig 3.40)도 같은 계열.
### 4.2 과도 오버폴리시
모델은 정상상태 뒤 erosion을 **선형**으로 예측하지만, w/s = 100/1 µm(Φ≈99 %) 어레이 실측은 107–116 s에서 기울기가 꺾여 모델이 과대예측
(Tugbawa 2002 Fig 3.41: 92→102 s 2200→2950 Å는 일치, 116 s 3500 Å 실측 vs 모델 약 4300 Å 판독). 원인: 어레이 전체가 필드보다 깊이 꺼지면
**장거리 높이차**가 어레이 위 유효압을 낮추는데(어레이-필드 사이의 2차 removal-rate diagram), 모델에는 이 항이 없다. 캘리브레이션 데이터에서
과도 오버폴리시 점을 빼라는 지침의 근거(§3.7.1 항목 5).
### 4.3 블랭킷 속도의 시간의존
Mirra에서 Cu 블랭킷 순간속도는 상수가 아니라 r(t) = a₁ − (a₂/τ_r)·e^{−t/τ_r}로 포화(eq 3.53; Table 3.3 실험 1–4: a₁ = 249.5/120.0/159.0/239.6 Å/s,
τ_r = 16.4/9.71/7.7/6.3 s). Park이 온도 상승(지수적 포화)과 연결 — [[frictional-heating-temperature-arrhenius-coupling]]과 맞닿는다.
< 25 Å/s인 유전체·배리어 속도는 상수로 취급. "일부 장비에서는 관측 안 됨"이라 장비 파라미터로 둔다.
### 4.4 배리어 단계 데이터 부재
배리어 200–250 Å이라 stage two를 분리 실험할 수 없다(§3.7.1 항목 4) → r_b, d₂는 stage three 피팅에서 간접 추정. [[../../agents/film-cu/CURRICULUM.md]] Lv2-2 과제.

## 5. 3단계 공정과의 연결 (Tugbawa 2001)
다단계 공정 = 각 스텝이 (r_cu, r_ox, d_max, Φ) 세트를 따로 갖는 단일스텝 모델의 연쇄. Tugbawa 2001 Fig 3–6 (IPEC 472, 80 %/33 % 밀도 구조):
- 1단계(r_cu = 135, r_ox = 1.5 Å/s 측정 블랭킷): dishing은 클리어 후 ~10 s 안에 포화(80 % ≈ 265 Å, 33 % ≈ 320 Å 모델선 판독) — **저밀도가 더 판다**
  (D_ss ∝ (1−Φ)/[(1−Φ)+Φ·r_ox/r_cu]: r_ox ≪ r_cu라 Φ 의존은 약하지만 방향은 저밀도↑). erosion은 선형: 80 % 약 32 Å/s, 33 % 약 15 Å/s (Fig 4 판독).
- 2단계(r_cu = 12, r_ox = 18 Å/s): dishing 회복(250→60 Å/150 s), erosion은 두 밀도가 같은 기울기(≈ r_ox)로 수렴.
- 시사점: [[cu-cmp-three-step-process-slurry-requirements]]의 "소프트랜딩·배리어 스텝은 선택비를 뒤집는다"는 서술의 정량적 형태가 D_ss의 부호다.

## 6. 시뮬레이터 연결 — 무엇을 어디에 (구현은 PROFILE.md 구현요청으로)
- 현행 `sim/tier1_empirical/pattern_density.py`의 `steady_state_dishing(RR_m, RR_ox, rho_m, dmax, b)`는 유전체 쪽 기울기를 자유 파라미터 b로 두는데,
  Tugbawa eq 3.33은 그 기울기를 **Φ/((1−Φ)·d_max)로 고정**한다(압력 보존에서 유도, 자유 파라미터 아님). b를 없애고 eq 3.39–3.42 닫힌 해로 바꾸는 것이 1순위.
- d_max(w, s)는 eq 3.46(B, α₂, β₂, s_l) 기본값 Table 3.9 ψ 포함 행. 엣지 라운딩 ψ(s)는 r_ox 승수. 과도 오버폴리시 플래그: E_ox > (예) 3000 Å 또는
  Φ_eff > 0.95면 "모델 과대예측 영역" 경고.
- 정적식각(SER)은 이 모델에 없다 — 패드 비접촉(D_cu ≥ d_max) 저지대는 RR_cu = 0이지만 실제로는 SER로 깎인다. [[cu-electrochemistry-pourbaix-bta-oxidizer-inhibitor]]의
  SER 26.4 nm/min(Lee H. 2023)을 RR_cu 하한으로 더하는 확장을 요청한다.

## 7. 검증 (verify_claims.py가 실제 실행)
재현 요약(한 줄): Table 3.9 ψ 포함 파라미터로 계산한 90 % 어레이 정상상태 erosion 속도 58.2 Å/s는 Fig 3.14 판독 기울기 61 Å/s와 5 % 내 일치, 50 % 어레이는 16.5 vs 11.7 Å/s로 41 % 과대(Tugbawa 2002).

### verify 1 — Hooke 분배 보존·정상상태식 내부정합·Fig 3.14 대조
```python verify
import numpy as np
# Tugbawa 2002 Table 3.9 (실험세트 #1, Mirra, EPC-5001, 4 psi, 75 rpm)
r_cu = 159.0            # Å/s  (a1, t >> tau_r=7.7 s)
r_ox_noER = 4.34        # Å/s  엣지라운딩 미포함 추출값
r_ox_ER, C, s_c = 2.22, 3.04, 22.5   # 엣지라운딩 포함 추출값

def Dss(dmax, rcu, rox, phi): return dmax*(rcu-rox)*(1-phi)/(rcu*(1-phi)+rox*phi)   # eq 3.39
def tau3(dmax, rcu, rox, phi): return dmax*(1-phi)/(rcu*(1-phi)+rox*phi)            # eq 3.40
def Y1(rcu, rox, phi): return rcu*rox/(rcu*(1-phi)+rox*phi)                          # eq 3.41
def psi(s): return C*np.exp(-s/s_c) + 1.0                                             # eq 3.49

# (a) 압력 보존: (1-Φ)P_ox + Φ P_cu = P1  (eq 3.31-3.32)
for phi in (0.1, 0.5, 0.9):
    for D_over_dmax in (0.0, 0.3, 1.0):
        P1 = 1.0
        P_ox = P1 + P1*(phi/(1-phi))*D_over_dmax
        P_cu = P1*(1-D_over_dmax)
        assert abs((1-phi)*P_ox + phi*P_cu - P1) < 1e-12
# (b) D_ss에서 RR_cu == RR_ox (eq 3.33-3.34 교점)
dmax = 333.0
for phi in (0.3, 0.5, 0.9):
    d = Dss(dmax, r_cu, r_ox_ER, phi)
    RR_cu = r_cu*(1-d/dmax); RR_ox = r_ox_ER + r_ox_ER*(phi/(1-phi))*(d/dmax)
    assert abs(RR_cu-RR_ox)/RR_ox < 1e-9
    assert abs(RR_ox - Y1(r_cu, r_ox_ER, phi)) < 1e-9          # 정상상태 erosion 속도 = Y1
# (c) 고립선(Φ→0): D_ss → dmax(1 - r_ox/r_cu)
assert abs(Dss(dmax, r_cu, r_ox_ER, 1e-9) - dmax*(1-r_ox_ER/r_cu)) < 1e-6
# (d) Y1은 Φ에 단조증가 (erosion ∝ 밀도)
phis = np.linspace(0.05, 0.95, 19)
assert np.all(np.diff([Y1(r_cu, r_ox_ER, p) for p in phis]) > 0)

# (e) Fig 3.14 판독 대조 (w/s = 9/1 µm Φ≈0.9, w/s = 1/1 µm Φ≈0.5; 92→110 s)
slope90 = (2850-1750)/(110-92); slope50 = (540-330)/(110-92)     # Å/s, 판독 ±50 Å → 기울기 ±4 Å/s
rox_eff = psi(1.0)*r_ox_ER                                         # s = 1 µm 스페이스 → ψ≈3.9
y90, y50 = Y1(r_cu, rox_eff, 0.9), Y1(r_cu, rox_eff, 0.5)
assert abs(y90-slope90)/slope90 < 0.10, (y90, slope90)             # 58.2 vs 61.1 Å/s
assert 0.25 < (y50-slope50)/slope50 < 0.55, (y50, slope50)         # 16.5 vs 11.7 Å/s — 41 % 과대, 원인: Φ_eff(L3=1.5 mm 창)≠명목 0.5 (추정)
# ψ 없이 r_ox_noER를 쓰면 90 % 어레이가 43 % 과소 → ψ가 필요한 이유
assert Y1(r_cu, r_ox_noER, 0.9) < 0.6*slope90
print(f"OK: Y1(90%)={y90:.1f} vs 판독 {slope90:.1f} Å/s; Y1(50%)={y50:.1f} vs {slope50:.1f}; tau3(Φ=.5)={tau3(dmax,r_cu,rox_eff,0.5):.2f} s")
```
결과: 90 % 어레이 5 % 이내 일치, 50 % 어레이 41 % 과대 — 어레이 중심의 Φ_eff는 L₃ ≈ 1.5 mm 창으로 이웃 필드가 섞여 명목 밀도와 다르므로
정확한 대조는 마스크 레이아웃이 필요(미검증). τ₃ ≈ 1 s 오더 → 클리어 직후 dishing이 즉시 포화한다는 서술과 정합.

### verify 2 — Tugbawa 2001 Fig 4 기울기에서 "유효 r_ox 부풀림" 역산
```python verify
# Tugbawa et al. 2001 CMP-MIC Fig 3-4 (IPEC 472, 1단계): 측정 블랭킷 r_cu = 135 Å/s, r_ox = 1.5 Å/s (그림 캡션)
r_cu, r_ox_meas = 135.0, 1.5
slope80 = (2150-380)/(148-92)      # Å/s  Fig 4 판독(±60 Å)  80 % 밀도
slope33 = (800-0)/(148-94)         # Å/s  33 % 밀도
def r_from_Y1(y, phi): return y*r_cu*(1-phi)/(r_cu-y*phi)   # eq 3.41을 r_ox에 대해 푼 것
r80, r33 = r_from_Y1(slope80, 0.80), r_from_Y1(slope33, 0.33)
# (a) 측정값 1.5 Å/s로는 두 기울기를 4배 이상 못 맞춘다
Y1 = lambda r, phi: r_cu*r/(r_cu*(1-phi)+r*phi)
assert Y1(r_ox_meas, 0.80) < slope80/4 and Y1(r_ox_meas, 0.33) < slope33/6
# (b) 역산한 유효 r_ox는 두 밀도에서 서로 30 % 안에 있고, 측정값의 5–7배 — 논문 서술 "6–10배"(Tugbawa 2002 §3.8.1)와 같은 오더
assert abs(r80-r33)/max(r80, r33) < 0.30, (r80, r33)          # 7.8 vs 10.3 Å/s
assert 5 <= r80/r_ox_meas <= 7 and 6 <= r33/r_ox_meas <= 7.5
# (c) 포화 dishing(모델선 판독 80 %: 265 Å, 33 %: 320 Å)에서 dmax 역산 → 두 구조의 dmax가 4 % 안에서 같다(같은 선폭·스페이스 계열로 추정)
def dmax_from(Dss, r, phi): return Dss*(r_cu*(1-phi)+r*phi)/((r_cu-r)*(1-phi))
d80, d33 = dmax_from(265, r80, 0.80), dmax_from(320, r33, 0.33)
assert abs(d80-d33)/d33 < 0.05, (d80, d33)                     # 346 vs 359 Å
# (d) τ3 = dmax(1-Φ)/[...] ≈ 2–3 s → 3τ ≈ 6–8 s 안에 포화: Fig 3에서 95→105 s 사이 포화와 정합
tau80 = d80*0.2/(r_cu*0.2+r80*0.8); tau33 = d33*0.67/(r_cu*0.67+r33*0.33)
assert 1.5 < tau80 < 3.5 and 1.5 < tau33 < 3.5
print(f"OK: r_ox,eff = {r80:.1f}/{r33:.1f} Å/s (측정 1.5의 {r80/1.5:.1f}/{r33/1.5:.1f}배), dmax≈{d80:.0f}/{d33:.0f} Å, tau3≈{tau80:.1f}/{tau33:.1f} s")
```
재현 요약(한 줄): Tugbawa 2001 Fig 4 기울기 32/15 Å/s에서 역산한 유효 r_ox 7.8/10.3 Å/s는 측정 블랭킷 1.5 Å/s의 5–7배로, 논문의 "6–10배" 서술과 대조해 같은 오더(Tugbawa et al. 2001).

### verify 3 — d_max(w, s) 경험식: 체감 멱법칙·스페이스 포화·Fig 3.12 판독 지수
```python verify
import numpy as np
# Tugbawa 2002 eq 3.46, Table 3.9(#1, ψ 포함) / Table 3.10(#2, ψ 포함)
sets = {"#1": dict(B=333.0, a2=0.303, b2=0.259), "#2": dict(B=372.4, a2=0.188, b2=0.185)}
s_l = 100.0   # µm, dishing length scale ("approximately 100 µm for conventional processes")
def dmax(w, s, B, a2, b2): return B*(w**a2)*(min(s, s_l)**b2)
for k, p in sets.items():
    w = np.array([0.25, 0.5, 1, 2, 5, 10, 50])
    d = np.array([dmax(x, 100, **p) for x in w])
    assert np.all(np.diff(d) > 0)                                   # 선폭 단조증가
    assert np.all(np.diff(d)/np.diff(w) > 0) and np.all(np.diff(np.diff(d)/np.diff(w)) < 0)   # 증가율 체감(오목)
    assert dmax(1, 200, **p) == dmax(1, 100, **p)                   # s ≥ s_l 포화
    r10 = dmax(10, 100, **p)/dmax(1, 100, **p)
    assert abs(r10 - 10**p["a2"]) < 1e-12
# Fig 3.12 고립선 엔드포인트 dishing 판독(±40 Å): 10 µm/1 µm 비 2.1 vs 모델 10^α2 = 2.0(#1)·1.5(#2)
w_m = np.array([0.25, 0.35, 0.5, 1, 2, 5, 10]); D_m = np.array([250, 270, 330, 660, 1000, 1220, 1400])
ratio_meas = D_m[-1]/D_m[3]
assert abs(ratio_meas - 10**0.303)/ratio_meas < 0.10     # #1 α2로 6 % 일치
assert abs(ratio_meas - 10**0.188)/ratio_meas > 0.20     # #2 α2로는 27 % 과소 — 공정이 다르면 α2가 다르다
alpha_fit = np.polyfit(np.log(w_m), np.log(D_m), 1)[0]
assert 0.45 < alpha_fit < 0.58, alpha_fit                 # 전 구간 멱법칙 지수 0.51 — Table α2(0.17–0.30)와 불일치, 원인 미상(Fig 3.12 공정·시각 미명시)
# 고립선 절대값: #1 파라미터 dmax(1 µm, s≥100) = 333·100^0.259 = 1097 Å vs 판독 660 Å → 40 % 과대 (다른 웨이퍼 세트, 미검증)
print(f"OK: ratio10/1 meas {ratio_meas:.2f} vs 10^0.303={10**0.303:.2f}; 전구간 지수 {alpha_fit:.2f}; dmax#1(1µm,iso)={dmax(1,100,**sets['#1']):.0f} Å")
```
재현 요약(한 줄): Fig 3.12 판독 dishing 비(10 µm/1 µm) 2.12는 Table 3.9 α₂ = 0.303의 10^α₂ = 2.01과 6 % 일치하나, 0.25–10 µm 전 구간 멱법칙 지수 0.51은 문헌 α₂ 0.17–0.30과 불일치(Tugbawa 2002) — 원인 미상.

## 8. 미검증·한계 목록 (정직 선언)
- Steigerwald 1994 본문 미확보(초록만) — "dishing은 밀도에 미미"라는 정량 근거(선폭·밀도 범위) 미확인.
- Ruan 2009 Fig 10–12는 시뮬레이터 출력. 밀도 0.7 포화의 실측 근거는 이 노트에서 확보 못 함.
- Fig 3.12·3.14·3.16, Tugbawa 2001 Fig 3–6의 수치는 모두 그림 눈금 판독(±40–60 Å). 원자료 없음.
- verify 1의 50 % 어레이 41 % 과대, verify 3의 지수 0.51 vs 0.17–0.30 불일치는 원인 미상으로 남긴다. Φ_eff 계산에는 854 마스크 레이아웃이 필요.
- 엣지 라운딩 ψ의 s_c ≈ 15–23 µm는 두 실험세트의 추출값이며 물리 유도가 아니다(경험식).
- Cu 상호작용거리 50–100 µm(Park 1998)와 L₃ ≈ 1.3–1.5 mm(Tugbawa 2002)의 관계는 이 노트에서 해소하지 못했다 — 정의 차이로 병기.

## 9. 자기시험
→ [[../../agents/film-cu/EXAMS.md]] Lv2-1 문항 참조.
