<!-- V2-SECTION: R2-slurry | 공동: R5-wafer | 근거: tungsten, 3D NAND, word line, bulk, buff, two-stage, low-defect, EOE, fanging, erosion | 정본: ARCHITECTURE-V2.md §3 -->
# 3D NAND 워드라인 W CMP와 벌크·버프 2단계 슬러리 — 고 MRR 벌크제거 vs 저결함 버프 마무리 (film-w Lv3-1)

> 에이전트: film-w Lv3-1 | 작성일: 2026-09-14
> 선행(자기 단원, 상호링크):
> [[w-cmp-wo3-passivation-oxidizer-kaufman]] (Lv1-1 — WO₃ 형성-제거 순환·정적식각. 이 노트의 벌크 슬러리 산화제(Fe³⁺/H₂O₂)와 pH 하강 기전이 그 순환 위에 얹힌다),
> [[w-cmp-fenton-catalyst-abrasive-alumina-silica]] (Lv1-2 — Fe 촉매 Fenton·실리카/알루미나 선택. 벌크는 Fe(NO₃)₃+실리카, 여기선 재서술 없이 링크로 참조),
> [[w-cmp-plug-recess-coring-keyhole-overpolish-window]] (Lv2-1 — 산화막 버프 공정창·침식 vs 프로트루전. 이 노트의 "버프 단계"가 그 폐형 모델의 실물 슬러리에 해당),
> [[w-cmp-ti-tin-barrier-selectivity-recess-erosion]] (Lv2-2 — W:배리어:옥사이드 선택비 창. 벌크의 고선택비·버프의 저선택비가 그 "선택비는 극대화가 아니라 창" 결론의 2단계 구현),
> [[w-cmp-abrasive-agglomeration-scratch-multiplier-egan-kim2019]] (자매 slurry-abrasive — 입자 응집→스크래치 배수. 이 노트 §4의 "큰 입자가 W MRR을 올린다"는 관측이 그 노트의 입경-MRR 무관 결론과 어떻게 갈라지는지 §4·§8에서 대조),
> 부모 상속 [[surface-chemistry-cu-w-pourbaix-passivation]]
> 형제 영역 침범 금지: film-cu(Cu 화학)·slurry-abrasive(입자 합성·입경-MRR 지수 추출)는 W 막질 관점에서 링크로만 참조. 이미 다룬 WO₃/Fenton 메커니즘은 재서술 금지.
> 스코프: (a) 3D NAND 워드라인/스테어케이스 맥락에서 W CMP의 특수성 — 두꺼운 W 벌크 제거·고 MRR·throughput·EOE(fanging)·확장 오버폴리시, (b) 저결함 W 슬러리 설계 — 국소부식·침식 저감 인자(입자 종류/크기·표면개질·pH·침식억제제)의 정량 효과, (c) 벌크 vs 버프 2단계 슬러리의 MRR·선택비·결함 트레이드오프, (d) 문헌값 python verify.

## 0. 출처 (특허 1차 4건 — 벌크·버프 2단계 짝 + 저결함 화학 2건)

1. **[1차·특허, freepatentsonline 원문 WebFetch]** Cabot Microelectronics Corp., "Tungsten bulk polishing method with improved topography," **US20190211228A1** (공개 2019-07-11; 등록 패밀리 EP3738140B1·TWI772590B, 2022). 3D NAND 벌크 W 제거용 표면개질 콜로이달 실리카 슬러리. §1·§3의 벌크 제거율·선택비(Table 2)·패턴 침식/국소부식(Table 3)은 이 명세서 실시예. freepatentsonline `y2019/0211228.html`을 WebFetch로 판독(원 PDF 직독 아님 — §7 verify [A]에서 보고 선택비를 RR로부터 재계산해 전사 정확도를 자체 대조).
2. **[1차·특허, freepatentsonline 원문 WebFetch]** Cabot Microelectronics Corp., "Tungsten buff polishing compositions with improved topography," **US20190211227A1** (공개 2019-07-11; 등록 패밀리 JP7370984B2, 2023). 벌크 후 마무리(버프) 단계 슬러리. §2·§3의 버프 제거율/선택비(Table 3)·패턴 침식(Table 4)은 이 명세서 실시예. WebFetch 판독(§7 verify [B]에서 자체 대조).
3. **[1차·특허, 로컬 전문]** Versum Materials US LLC, "Tungsten chemical mechanical polishing for reduced oxide erosion," **EP3597711B1** (출원 2019-07-22, 등록 2024-07-08). 로컬 텍스트 `papers/ep3597711b1-versum-w-cmp-reduced-oxide-erosion.txt` 통독(청구항). pKa≥4 침식억제제로 W 연마 부산물의 pH 하강을 상쇄해 pH≥4 유지 → 조밀 W 구조 침식 저감. W:옥사이드 선택비 >10·>40.
4. **[1차·특허, 로컬 전문]** Versum Materials US LLC, "Tungsten chemical-mechanical polishing composition," **KR102732305B1** (Google Patents 로컬 전문 `data/corpus/fulltext/patent_KR102732305B1.txt`). 화합물(아미노실란/인-함유) 혼입 콜로이달 실리카. 두 레짐 명시: 저pH·<2wt% 실리카에서 W>2000 Å/min·W:TEOS>40:1(벌크), 고pH·<4wt%에서 TEOS>1000 Å/min·TEOS:W>1(비선택/역선택 버프형).

보조(2차, 초록만): Y. Wang et al., "Synergetic Effect of Chemical Components in a Tungsten CMP Slurry and the Evolution of Tungsten Surface Species," *ECS J. Solid State Sci. Technol.* (2024), DOI: 10.1149/2162-8777/ad60fe — 50 ppm Fe³⁺+2wt% H₂O₂+75 ppm 옥살산 슬러리로 W 710 Å/min·거칠기 1 nm, 옥살산이 H₂O₂를 "래핑"해 안정화(MRR 손실 없이). **본문 미확보, 초록 수치만 인용(E5)**. Fenton 화학 자체는 [[w-cmp-fenton-catalyst-abrasive-alumina-silica]] 링크 참조.

## 1. 3D NAND 워드라인 맥락에서 W CMP의 특수성 (US20190211228A1 §배경, subtopic a)

3D NAND는 워드라인(WL)을 게이트-라스트(gate-last) 치환공정으로 만든다: 산화물/질화물 스택을 쌓고 슬릿을 뚫어 질화물을 제거한 뒤 그 공간을 CVD/ALD로 **텅스텐 충전**한다. WL 게이트 자체의 잉여 W는 대개 **플라즈마 에치백(etch-back)**으로 슬릿·측벽에서 제거된다(웹검색 2차 요약, 게이트-라스트 흐름 — **미검증**, CMP가 아니라 건식식각 영역). 따라서 **3D NAND에서 W CMP의 주무대는 WL 게이트 그 자체가 아니라** ① 스테어케이스 콘택·플러그·인터커넥트의 두꺼운 W 벌크, ② 상부 배열(above-array) 배선이다 — 이 노트의 벌크/버프 슬러리는 US20190211228A1 배경이 명시하듯 "3D NAND devices"와 "tungsten plug and interconnect structures"를 겨냥한다.

3D NAND가 W CMP에 부과하는 세 가지 압력(US20190211228A1·US20190211227A1 배경):
- **두꺼운 W·고 MRR·throughput**: "relatively large portions of tungsten"을 "high tungsten removal rate"로 걷어내야 한다. 벌크 W 제거율이 낮으면 공정시간(process time)이 길어져 throughput이 깨진다. 아래 §3의 벌크 슬러리가 W ~318 nm/min(=3180 Å/min급)을 노리는 이유.
- **EOE(edge-over-erosion, "fanging")와 국소부식**: 넓은 배열의 가장자리·고립 라인에서 국소적으로 과도하게 파이는 결함. 기존 음이온 실리카계는 "excessive edge-over erosion"으로 수율을 깎거나, 반대로 "low film removal rates"로 공정시간을 늘리는 상충에 갇혀 있었다. EOE의 기계적 성격은 [[w-cmp-plug-recess-coring-keyhole-overpolish-window]] §6(Vacassy)과 연결.
- **확장 오버폴리시(extended overpolishing) 내성**: 3D NAND의 큰 필드·두께 편차 때문에 국소적으로 오래 갈리는 구간이 생긴다 — 그동안 이미 노출된 옥사이드·조밀 구조가 침식되지 않아야 한다("improved performance with extended overpolishing").

즉 3D NAND의 W CMP 요구는 **"두껍고 빠르게, 그러나 넓은 배열의 토포그래피를 지키며"**로 요약되고, 단일 슬러리로는 이 둘(속도 vs 토포그래피)을 동시에 못 잡아 **벌크-버프 2단계**로 분업한다(§3).

## 2. 벌크 vs 버프 — 두 단계의 역할 분담 (subtopic c 개요)

| 항목 | 벌크(bulk) 슬러리 | 버프(buff) 슬러리 |
|---|---|---|
| 목표 | 두꺼운 W 대량·고속 제거 | 잔여 W 마무리 + 토포그래피 교정 |
| W 제거율 | **~318 nm/min**(고 MRR) | **~40–67 nm/min**(저 MRR) |
| W:옥사이드 선택비 | **~40–61:1**(고선택, 옥사이드 보존) | **~1.1–2.6:1**(거의 비선택) |
| 왜 그 선택비인가 | 벌크 중엔 옥사이드를 건드리면 안 됨 | 일부러 옥사이드도 깎아 프로트루전·침식 편평화 |
| 지배 결함 | throughput·초기 EOE | 최종 침식·array/isolated 라인 |

버프의 **저선택비(≈비선택)**가 핵심이다 — [[w-cmp-plug-recess-coring-keyhole-overpolish-window]] §4에서 Yu 2009가 "산화막 버프로 옥사이드를 L만큼 더 깎아 프로트루전·침식을 편평화한다"고 한 폐형 모델의 실물이 바로 이 버프 슬러리다. 벌크가 옥사이드를 지키며 W만 빠르게 없앤 뒤, 버프가 W·옥사이드를 비슷한 속도로 함께 깎아 표면을 고른다. Lv2-2([[w-cmp-ti-tin-barrier-selectivity-recess-erosion]])의 "선택비는 극대화가 아니라 창" 결론이 여기서 **단계별 분업**으로 구현된다: 벌크=고선택 창, 버프=저선택 창.

## 3. 저결함 벌크 W 슬러리 — 표면개질 실리카·입자크기·국소부식 (US20190211228A1, subtopic b)

벌크 슬러리 조성(US20190211228A1): **표면개질 콜로이달 실리카**(술포네이트/카복실레이트/포스포네이트기 공유결합, 입경 90–350 nm, ζ = −20~−70 mV @ pH~2) + **Fe(NO₃)₃**(0.005–0.1 wt%) + **말론산**(안정제) + pH 2–3. Fe³⁺/실리카 화학 자체는 [[w-cmp-fenton-catalyst-abrasive-alumina-silica]] 참조(재서술 없음).

**Table 2(블랭킷 필름) 정량**(비교예 1A=구형 음이온 실리카 68 nm 대비 발명예):
- W 제거율: 146.6 → 267.1(100 nm)/317.5(120 nm)/329.8(160 nm) nm/min — **발명예가 비교예의 ~2배**.
- W:TEOS 선택비: 29:1 → 40~61:1 — **선택비도 ~2배** 상승. (옥사이드 제거율은 5.0→4.9~7.3 nm/min로 거의 불변, W만 올림.)

**Table 3(패턴 웨이퍼) 정량** — 저결함의 핵심(1E, 120 nm vs 비교예 1A, 68 nm):
- 0.18×0.18 µm 조밀 라인 침식: 4 → 5 nm(거의 동일).
- **0.18 µm 고립 라인 국소부식: 5 → 1 nm(−80 %)**.
- **1 µm 고립 라인 침식: 11.1 → 4.8 nm(−57 %)**.

즉 **더 큰(120 nm) 표면개질 입자가 조밀부 침식은 그대로 두면서 고립 라인의 국소부식만 크게 줄인다** — EOE/fanging이 고립 피처에서 심하다는 §1과 정합. 국소부식 저감의 기전은 입자 자체보다 **음전하 표면개질(ζ 제어)에 의한 정전 안정성·균일 접촉**으로 US20190211228A1이 설명한다.

**⚠ 입자크기-W MRR 주의(형제 영역 경계)**: Table 2에서 입경↑(68→160 nm)에 W RR↑는 표면적 관측이지만, 비교예 1A는 표면개질이 다른 **선행 음이온 실리카**이고 발명예는 술포네이트/포스포네이트 개질+ζ가 함께 바뀌므로 **입경 단독 스윕이 아니다(교란)**. 따라서 이 관측은 [[w-cmp-abrasive-agglomeration-scratch-multiplier-egan-kim2019]]·EVIDENCE-RULES 판정#6("W MRR은 알루미나 입경과 무관")을 **뒤집지 않으며**, 입경-MRR 지수 추출은 slurry-abrasive 영역이라 여기서 하지 않는다(방향성만 기록, 크기 미채택). **미검증**: 표면개질·ζ·입경이 얽힌 다중교란.

## 4. 저결함 버프 W 슬러리 — 비선택 마무리로 토포그래피 편평화 (US20190211227A1, subtopic b·c)

버프 슬러리 조성(US20190211227A1): 표면개질 실리카(90–350 nm, ζ −5~−35 mV @ pH 3, 1.5–3.5 wt%) + **Fe(NO₃)₃ 9수화물**(0.001–0.05 wt%) + 말론산 + **글리신**(부식억제제 0.1–0.5 wt%) + **H₂O₂**(0.3–0.5 wt%) + pH 2.2–3.5. 벌크와 달리 **글리신·H₂O₂를 명시** — 글리신이 W 킬레이트·부식억제로 마무리 단계의 국소부식을 잡는다.

**Table 3(블랭킷, 207 hPa)**:
- W 제거율 39.2~67.2 nm/min — **벌크(~318)의 1/5~1/8**(저 MRR 마무리).
- W:TEOS 선택비 1.09~2.56:1 — **거의 비선택**(벌크 ~50:1과 대비). 발명예 1G는 1.09:1로 W와 옥사이드를 거의 같은 속도로 깎는다.

**Table 4(패턴, 침식 nm)** — 버프의 토포그래피 교정력(비교예 1A vs 발명예):
- 0.18×0.18 µm 배열 침식: **15.4 → 0.9 nm(−94 %)**.
- 1×1 µm 고립 라인 침식: **24.6 → 7.4 nm(−70 %)**.
- 필드 옥사이드 손실: 17.4 → 13.5~20.6 nm(비슷하거나 소폭 증감 — 비선택이라 필드도 깎임).

**해석**: 버프는 **일부러 비선택**으로 옥사이드·프로트루전을 함께 깎아 배열/고립 라인의 침식을 편평화한다. 필드 손실은 감수하되(비선택의 대가), 국소 결함(array 침식 −94 %)을 지운다. 이는 [[w-cmp-plug-recess-coring-keyhole-overpolish-window]] §4 Yu 2009의 "버프량으로 프로트루전을 없애되 침식과 상충"을 실측 슬러리로 확인 — 벌크가 남긴 토포그래피를 버프가 비선택 제거로 흡수하는 2단계 설계.

## 5. 저결함의 pH 손잡이 — W 부산물 산성화 상쇄 (EP3597711B1, KR102732305B1, subtopic b)

EP3597711B1은 저결함의 **세 번째 손잡이 = pH 완충**을 준다. W가 연마되며 텅스텐산(tungstic acid) 계열 부산물이 슬러리 pH를 **떨어뜨리고**, 낮아진 pH에서 조밀 W 구조의 침식이 심해진다. 대책은 **pKa≥4 침식억제제**(폴리아크릴산·시트르산·피콜린산·EDTA 등)를 ≥0.01 wt% 넣어, W 분말 투입 1시간 후에도 **pH≥4(바람직 ≥5)를 유지**하는 것이다(청구항 1·4). 이 조건에서 W:옥사이드 선택비 >10, TEOS/HDP 상대로 >40을 유지한다(청구항 9·10). 즉 저결함 W 슬러리 설계는 **입자(§3·4) × 산화제/억제제 화학 × pH 완충**의 3축이며, pH는 "산화제 세기"와 독립적으로 침식을 제어하는 축이다.

KR102732305B1은 같은 화학계가 **pH·실리카 농도만으로 벌크↔버프 두 레짐을 오간다**는 것을 명시한다: 저 pH(<4)·<2 wt% 실리카에서 W>2000 Å/min·W:TEOS>40:1(벌크형 고선택), 산성이되 다른 조건에서 TEOS>1000 Å/min·TEOS:W>1(버프형 역선택). 벌크와 버프가 완전히 다른 슬러리가 아니라 **같은 화학계의 pH/고형분 조율로 갈리는 두 동작점**일 수 있음을 보여준다(단, 실제 양산은 별도 최적화 조성을 쓴다 — §3·4의 Cabot 조성이 그 예).

## 6. 종합 — 이 에이전트의 결론 (W 공정통합 관점)

1. **3D NAND W CMP = 두껍고 빠르게, 넓은 배열 토포그래피를 지키며.** 단일 슬러리로 속도(고 MRR)와 토포그래피(저 EOE)를 동시에 못 잡아 **벌크→버프 2단계**로 분업한다.
2. **벌크 = 고 MRR·고선택(~318 nm/min, ~50:1).** 옥사이드를 지키며 W를 대량 제거. 저결함은 표면개질 실리카(ζ 제어)로 고립 라인 국소부식을 −80 % 줄인다(US20190211228A1).
3. **버프 = 저 MRR·비선택(~40–67 nm/min, ~1–2.6:1).** 일부러 옥사이드도 깎아 array 침식을 −94 %로 편평화(US20190211227A1) — Yu 2009 산화막 버프 모델의 실물.
4. **저결함 3축**: 입자(개질·ζ) × 산화제/억제제(Fe³⁺/H₂O₂/글리신) × pH 완충(pKa≥4, pH≥4 유지, EP3597711B1). pH는 부산물 산성화를 상쇄해 침식을 잡는 독립 축.
5. **선택비는 단계 의존**: 벌크는 극대화(창의 고선택 끝), 버프는 최소화(비선택). Lv2-2([[w-cmp-ti-tin-barrier-selectivity-recess-erosion]])의 "선택비 창"이 2단계 분업으로 실현됨.

## 7. 검증 — 문헌값 상수 박고 assert (```python verify```, verify_claims.py 실제 실행)

**재현 요약(한 줄)**: US20190211228A1(벌크) Table 2에서 발명예 W 제거율 267~330 nm/min이 비교예 146.6의 ~2배이고 W:TEOS 선택비 40~61:1이 보고값과 RR로부터 재계산해 ±1.5 이내로 일치하며 Table 3에서 120 nm 개질입자가 0.18 µm 고립 라인 국소부식을 5→1 nm(−80 %)·1 µm 라인을 11.1→4.8 nm(−57 %) 줄임을 재현; US20190211227A1(버프) Table 3에서 버프 W 제거율 39~67 nm/min이 벌크의 1/5~1/8이고 선택비 1.09~2.56:1이 거의 비선택이며 Table 4에서 배열 침식 15.4→0.9 nm(−94 %)·1 µm 라인 24.6→7.4 nm(−70 %) 편평화를 재현; EP3597711B1/KR102732305B1의 W:옥사이드 >40:1(벌크)과 TEOS:W>1(버프)로 두 레짐의 선택비 부호가 반대임을 대조 — 아래 3블록 PASS.

```python verify
# [A] US20190211228A1 벌크 W 슬러리 — Table 2(블랭킷 RR·선택비)·Table 3(패턴 국소부식)
# 단위: nm/min. (size_nm, W_RR, TEOS_RR, ratio_reported)
bulk = {'1A':(68,146.6,5.0,29),'1B':(100,267.1,6.7,40),'1C':(120,317.5,7.3,43),
        '1D':(120,316.6,6.5,49),'1E':(120,297.0,4.9,61),'1F':(160,329.8,5.7,58),
        '1G':(174,329.2,5.9,56)}
# (1) 전사 정확도: 보고 선택비를 W/TEOS로 재계산해 ±1.5 이내 일치 (WebFetch 판독 자체 대조)
for k,(s,w,t,r) in bulk.items():
    assert abs(w/t - r) < 1.5, f"{k}: 재계산 {w/t:.1f} vs 보고 {r}"
# (2) 벌크 고 MRR: 발명예(개질) W RR이 비교예(1A, 68nm 선행 음이온)의 ~2배
inv = [bulk[k][1] for k in ('1C','1D','1E','1F','1G')]  # 120~174nm 발명예
mean_inv = sum(inv)/len(inv)
comp = bulk['1A'][1]
assert mean_inv/comp > 1.8, f"발명예/비교예 W RR 배수 {mean_inv/comp:.2f}"
# (3) 벌크 고선택: 발명예 선택비 40~61 vs 비교예 29
assert all(bulk[k][3] >= 40 for k in ('1B','1C','1D','1E','1F','1G'))
assert bulk['1A'][3] < 30
# (4) Table 3 국소부식(120nm 1E vs 68nm 1A): 조밀부는 비슷, 고립라인만 급감
iso_018 = (5, 1)   # 0.18um 고립: 1A -> 1E (nm)
iso_1um = (11.1, 4.8)
dense = (4, 5)     # 0.18x0.18 조밀: 1A -> 1E (거의 동일)
red_iso = (iso_018[0]-iso_018[1])/iso_018[0]
red_1um = (iso_1um[0]-iso_1um[1])/iso_1um[0]
assert red_iso > 0.75, f"고립 국소부식 감소 {red_iso:.0%}"   # -80%
assert 0.5 < red_1um < 0.65, f"1um 라인 감소 {red_1um:.0%}"   # -57%
assert abs(dense[1]-dense[0]) <= 1                              # 조밀부는 ±1nm
print(f"[A] 벌크(US20190211228A1): 발명예 W RR 평균 {mean_inv:.0f} nm/min = 비교예의 {mean_inv/comp:.2f}배, "
      f"선택비 40~61:1; 고립 국소부식 -{red_iso:.0%}, 1um -{red_1um:.0%}, 조밀부 불변")
```

```python verify
# [B] US20190211227A1 버프 W 슬러리 — Table 3(저MRR·비선택)·Table 4(침식 편평화) + 벌크 대조
buff = {'1A':(39.2,21.6,1.81),'1G':(45.2,41.5,1.09),'1J':(67.2,26.2,2.56)}  # (W,TEOS,ratio)
# (1) 전사 정확도: 보고 선택비 재계산 ±0.05
for k,(w,t,r) in buff.items():
    assert abs(w/t - r) < 0.05, f"{k}: {w/t:.2f} vs {r}"
# (2) 버프 저 MRR: W RR 39~67 nm/min << 벌크 대표 ~318
buff_W = [buff[k][0] for k in buff]
bulk_rep = 318.0   # [A]의 발명예 평균
assert max(buff_W) < 70 and bulk_rep/ (sum(buff_W)/len(buff_W)) > 5, "버프는 벌크의 1/5 이하 MRR"
# (3) 버프 비선택: 선택비 ~1~2.6 (벌크 ~50과 정반대)
assert all(buff[k][2] < 3 for k in buff)
sel_ratio = 50.0 / (sum(buff[k][2] for k in buff)/len(buff))  # 벌크선택비/버프선택비
assert sel_ratio > 20, f"벌크/버프 선택비 배수 {sel_ratio:.0f}"
# (4) Table 4 침식 편평화 (비교예 1A vs 발명예 1G)
array = (15.4, 0.9)   # 0.18x0.18 배열 침식 nm
iso   = (24.6, 7.4)   # 1x1 um 고립 라인
red_array = (array[0]-array[1])/array[0]
red_iso   = (iso[0]-iso[1])/iso[0]
assert red_array > 0.9, f"배열 침식 감소 {red_array:.0%}"   # -94%
assert red_iso   > 0.65, f"고립 침식 감소 {red_iso:.0%}"    # -70%
print(f"[B] 버프(US20190211227A1): W RR {min(buff_W):.0f}~{max(buff_W):.0f} nm/min(벌크의 1/{bulk_rep/(sum(buff_W)/len(buff_W)):.0f}), "
      f"선택비 1.09~2.56:1(벌크의 1/{sel_ratio:.0f}); 배열 침식 -{red_array:.0%}, 고립 -{red_iso:.0%}")
```

```python verify
# [C] 두 레짐의 선택비 부호 대조 (EP3597711B1 / KR102732305B1) + 3D NAND throughput 정합
# EP3597711B1 청구항: W:oxide > 10, TEOS/HDP 상대로 > 40 (pH>=4 유지 조건)
sel_bulk_min = 40      # 벌크형 W:TEOS 하한 (EP3597711B1 청구항10, KR102732305B1 >40:1)
# KR102732305B1: 벌크 W>2000 A/min(=200 nm/min), 버프형 TEOS>1000 A/min & TEOS:W>1
W_bulk_Amin = 2000.0   # A/min
TEOS_buff_Amin = 1000.0
assert W_bulk_Amin/10 == 200.0            # 200 nm/min, 벌크 고 MRR 하한
# 벌크는 W:TEOS>1(W가 빠름), 버프형은 TEOS:W>1(옥사이드가 빠름) -> 부호 반대
regime_bulk = ('W', W_bulk_Amin, 'TEOS', W_bulk_Amin/sel_bulk_min)  # TEOS < 50 A/min
assert regime_bulk[1] > regime_bulk[3]     # 벌크: W > TEOS
regime_buff = ('TEOS', TEOS_buff_Amin, 'W', TEOS_buff_Amin*0.9)     # TEOS:W>1
assert regime_buff[1] > regime_buff[3]     # 버프: TEOS > W (역선택)
# 두 레짐의 "빠른 물질"이 서로 반대 (벌크=W, 버프=옥사이드)
assert regime_bulk[0] != regime_buff[0]
# 3D NAND throughput 정합: 벌크 200 nm/min이면 두꺼운 W 1 um 제거에 걸리는 시간
t_1um_s = (1000.0 / 200.0) * 60.0   # nm / (nm/min) -> min -> s
assert t_1um_s < 360               # 1 um W를 6분 이내 (고 throughput)
print(f"[C] 벌크 레짐 빠른물질={regime_bulk[0]}(W:TEOS>{sel_bulk_min}:1), "
      f"버프 레짐 빠른물질={regime_buff[0]}(TEOS:W>1) -> 선택비 부호 반대; "
      f"벌크 200nm/min로 1um W 제거 {t_1um_s:.0f}s")
```

## 8. 한계·불명확 (정직 선언)

- (a) **벌크/버프 실시예 수치(US20190211228A1·227A1)는 원 PDF 직독이 아니라 freepatentsonline HTML을 WebFetch로 판독**한 것이다. 전사 오류 위험은 §7 [A][B]에서 보고 선택비를 RR로 역산해 ±1.5(벌크)·±0.05(버프) 이내로 자체 대조해 낮췄으나, 표 외 조건(다운포스·패드·시간)의 정확한 값은 이 노트에서 완전 확인 못 함 — **일부 미검증**.
- (b) **3D NAND WL 게이트 W가 CMP가 아니라 에치백으로 제거된다**는 §1 서술은 웹검색 2차 요약(게이트-라스트 흐름)으로 1차 원문 미확보 — **미검증**. 이 노트의 벌크/버프 슬러리는 특허 배경상 3D NAND의 플러그·인터커넥트·스테어케이스 콘택 W CMP를 겨냥하며, WL 게이트 리세스 자체의 CMP 스펙(리세스 깊이 nm)은 특정 1차 수치를 확보하지 못했다 — **미확보**.
- (c) §3의 **입자크기↑→W MRR↑**(146→330 nm/min)는 표면개질·ζ·입경이 동시에 바뀐 **다중교란 관측**이라 입경 단독 효과가 아니다 — EVIDENCE-RULES 판정#6을 뒤집지 않으며 입경-MRR 지수는 추출하지 않음(slurry-abrasive 영역). **미검증**.
- (d) KR102732305B1의 "같은 화학계가 pH로 벌크↔버프를 오간다"는 명세서 서술이며, Cabot의 실제 양산 벌크(US...228)·버프(US...227) 조성이 동일 화학계인지는 **확인 못 함**(서로 다른 출원인·조성). §5는 "가능성"으로만 기록.
- (e) 보조 인용 Wang 2024(DOI 10.1149/2162-8777/ad60fe, 710 Å/min)는 **초록만 확보(E5)** — 본문 미검증, verify에 넣지 않음.
- (f) 침식/부식 절대 nm(예: array 15.4 nm)는 특정 패턴·패드·조건의 값으로 다른 노드 전이는 보장 안 됨 — **구조(부호·배수)만 일반화** 가능.

## 9. 구현 요청 → agents/film-w/PROFILE.md "## 구현 요청" 참조
(벌크·버프 2단계 MRR/선택비/침식 트레이드오프 모델 — 상세는 PROFILE.)

## 10. 자기시험
→ [[../../agents/film-w/EXAMS.md]] Lv3-1 문항 참조.
