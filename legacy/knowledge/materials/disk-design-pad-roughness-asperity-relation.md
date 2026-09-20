<!-- V2-SECTION: R4-disk | 공동: R3-pad | 분배완료 2026-09-08 | 근거: conditioning, disk-, disk-design, 디스크 | 정본: ARCHITECTURE-V2.md §3 -->
# 디스크 설계(그릿 크기·밀도·돌출) → 컨디셔닝된 패드 표면 조도·asperity 분포의 정량 관계

> disk-design Lv2-2 | 작성일: 2026-09-07
> 선행: [[pad-conditioning-wear-regeneration-balance]] [[pad-hardness-porosity-measurement-methods]]
> [[hertz-gw-contact-mechanics]] [[gw-nominal-vs-local-pressure]] [[pad-glazing-mechanism-mrr-decay]]
> 형제·부모: [[../equipment/conditioner-grit-wear-scratch-lifetime]] (Kwon 2013 원문 확보처)
> [[../equipment/conditioner-grit-density-protrusion-cutrate]] [[../equipment/conditioner-grit-design-space]]
> [[../equipment/conditioner-asperity-population-balance]] (Ring et al. 원문 확보처) [[../cmp/preston-luo-dornfeld-mrr]]
> 스코프: 디스크 **설계 파라미터**(그릿 크기·밀도·형상·돌출·CVD 팁)가 컨디셔닝된 패드의
> **표면 통계**(Ra·Rpk·높이분포 감쇠길이 λ·정점밀도·정점곡률·실접촉면적)에 미치는 관계만
> 다룬다. 컨디셔닝 **하중·스윕**은 disk-kinematics 영역이라 "같은 디스크에서 하중을 바꾸면
> 어떻게 되는가"는 그릿 효과를 분리하는 데 필요한 최소한만 인용한다.

## 1. 왜 이 단원이 필요한가 — 디스크 스펙이 GW 파라미터로 번역되지 않고 있다

[[hertz-gw-contact-mechanics]]는 패드 표면을 GW 통계(정점 밀도 η, 높이분포 스케일 σ 또는
지수분포의 1/β, 정점 반경 R)로 기술하고 [[gw-nominal-vs-local-pressure]]는 그 파라미터로
명목압력→실접촉압력을 풀었다. 그런데 이 세 파라미터가 **어디서 오는지**는 두 노트 모두
"예시값" 또는 "문헌 실측치 아님"으로 남겨 두었다. [[pad-conditioning-wear-regeneration-balance]]가
보인 것처럼 정상상태 패드 표면은 "컨디셔너가 만드는 고유구조(intrinsic structure)"와
"웨이퍼 마모"의 균형이고, 그 고유구조를 결정하는 것이 바로 디스크 설계다(Lawing 2004:
"Size, shape and density of diamonds on conditioner surface drive cutting characteristics and
intrinsic surface structure"). 이 노트의 질문: **그릿 크기·밀도·형상을 바꾸면 Ra·λ·η·R이
얼마나 변하는가, 그리고 그것이 실접촉면적·MRR로 어떻게 이어지는가.**

### 1.1 이 노트에서 쓰는 표면 지표 정의 (출처별로 지표가 달라 혼동 주의)

| 지표 | 정의 | 어느 출처가 쓰는가 |
|---|---|---|
| Ra | 산술평균 조도(프로파일 편차 절대값 평균) | Kwon et al. 2013 (3D 레이저현미경 Keyence VK-9700) |
| Rpk | bearing-ratio 곡선의 reduced peak height — 최상부 봉우리 영역 높이 | Kwon et al. 2013 (MRR과 상관이 강하다고 저자 명시) |
| "Surface finish" (µm) | 3M 사내 표준시험으로 기준 패드에 남긴 표면 마무리값 — 산출식·기준패드 종류 본문 미기재 | Pysher et al. 2010 (3M) |
| λ (surface abruptness, µm) | 표면 높이 PDF 우측 꼬리를 지수분포 exp(−z/λ)로 볼 때의 감쇠길이. 클수록 키 큰 asperity가 많음(덜 abrupt) | Sun 2009 학위논문 / Sun et al. 2010, Liao 2014, Borucki 이론 |
| η_c (contacting summit density, #/mm²) | 사파이어창 공초점 접촉이미지에서 센 접촉점 수/면적 | Sun 2009, McAllister 2018/2019 |
| A_f (contact area fraction) | 접촉 이미지의 흑색(접촉) 면적 비율 | Sun 2009, Lawing 2004(추정법 상이), McAllister 2018 |
| κ_s (mean summit curvature) | 정점 최고점의 곡률(=1/R) 평균, 상위 25% 정점만 사용(McAllister) | Liao 2014 (µm⁻¹), McAllister 2018 (1/µm² 표기 — Gaussian 곡률로 추정, 단위 표기 원문 그대로) |
| GW η, σ(=1/β), R | [[hertz-gw-contact-mechanics]] §3 정의 | Ring et al. (연도 미기재), Jeong et al. 2024 |

λ와 GW의 지수분포 스케일 1/β는 같은 물리량이다(둘 다 "높이 PDF 꼬리의 e-폴딩 길이").
Ra·Rpk는 프로파일 전체 통계라 λ와 1:1 대응이 없다 — **서로 다른 출처의 조도값을 한 축에
놓고 비교하지 않는다**([[pad-hardness-porosity-measurement-methods]] §2가 Shore C/D에 대해
내린 것과 같은 규칙).

## 2. 1차 출처 데이터 — 디스크 파라미터별 패드 표면 통계

### 2.1 그릿 밀도·형상(grade) → Ra·Rpk: Kwon et al. (2013), Tribology International 67, 272–277

출처: T.-Y. Kwon, M. Ramachandran, B.-J. Cho, A. A. Busnaina, J.-G. Park, "The impact of diamond
conditioners on scratch formation during chemical mechanical planarization (CMP) of silicon
dioxide", *Tribology International* 67, 272–277 (2013), doi.org/10.1016/j.triboint.2013.08.008
(서지는 Crossref로 재확인; 원문 전체 `papers/kwon2013-scratch-formation-diamond-conditioners.pdf`,
[[../equipment/conditioner-grit-wear-scratch-lifetime]]에서 Lv2-1에 확보). 조건: PU 패드, DIW 컨디셔닝 2 h, 6 psi, 플래튼/컨디셔너 93/100 rpm,
스윕 84 rpm(원문 표기). 디스크: 그릿 밀도 17k/40k/60k(개/디스크, grade 640 고정) 및
grade 625(sharp)/640(medium)/925(blunt)(밀도 40k 고정).

Fig. 2 막대그래프를 눈금 판독(±0.15 µm Ra, ±0.1 µm Rpk)한 값과 본문 명시 수치:

| 디스크 | Ra (µm, Fig.2a 판독) | Rpk (µm, Fig.2b 판독) | 본문 명시 Ra | 패드 절삭율 2 h (µm/h, 본문) |
|---|---|---|---|---|
| 17k / 640 | 8.05 | 3.75 | 7.89 µm (Fig.7 문맥) | 37 |
| 40k / 640 (기준) | 6.8 | 2.25 | — | 23 |
| 60k / 640 | 5.95 | 1.7 | 6.37 µm (Fig.7 문맥) | 19 |
| 40k / 625 sharp | 7.0 | 2.75 | — | ≈45 |
| 40k / 925 blunt | 5.85 | 1.8 | — | (본문 미기재) |

저자 결론(원문 §3, §4): "surface roughness increased with decreased of grade and decreased
with diamond density, which matches well with the pad wear rate" — 즉 **Ra·Rpk는 절삭율과
같은 방향**으로 움직인다(저밀도·sharp → 그릿당 접촉압 상승 → 깊은 침투 → 거친 표면).
본문 7.89/6.37 µm와 Fig.2 판독 8.05/5.95 µm는 2~7% 차이 — 같은 실험의 다른 측정 세트로
추정(Fig.7 스크래치 논의용 재측정), 원문이 구분해 주지 않아 **추정**.

### 2.2 그릿 크기 → 표면 마무리(surface finish): Pysher, Goers, Zabasajja (2010), 3M

출처: D. Pysher, B. Goers, J. Zabasajja, "Design, Characteristics and Performance of Diamond
Pad Conditioners", MRS Proc. 1249, E02-04 (2010), doi.org/10.1557/proc-1249-e02-04 — 3M 공개
PDF 전문 `papers/3m_diamond_conditioner_design.pdf`([[pad-conditioning-wear-regeneration-balance]]
§6에서 등록). Figure 1 "Surface finish and aggressiveness map"은 다이아 크기·형상별 디스크
수십 개를 (aggressiveness number, surface finish µm) 평면에 찍은 유일한 공개 **크기-조도
지도**다. 300 dpi 렌더링 후 군집 중심을 판독(±0.15 µm):

| 다이아 크기·형상 | 점 개수 | surface finish (µm) 범위 | 군집 중심 | aggressiveness 범위 |
|---|---|---|---|---|
| 45 µm (sharp, Region C) | 6 | 1.55–1.8 | 1.7 | 1–2 |
| 53 µm | 5 | 1.7–2.15 | 1.95 | 4–8 |
| 90 µm | 2 | 2.45–2.5 | 2.5 | 10, 14 |
| 150 µm **leveled**(팁 높이 정렬) | 7 | 1.85–2.15 | 2.0 | 1–8 |
| 125 µm sharp (Region A) | ~10 | 3.1–4.2 | 3.5 | 12–22 |
| 250 µm semi-sharp (Region A, 1세대) | ~9 | 3.0–5.4 | 4.1 | 13–22 |
| 180 µm semi-sharp | 7 | 2.8–5.4 | 4.2 | 17–22 |
| 180 µm sharp (Region B) | 15 | 3.5–4.85 | 4.1 | 26–36 |

두 가지 비자명한 관찰: (i) 45→125 µm 구간에서 surface finish는 크기와 함께 단조 증가하지만
125→250 µm에서는 **포화**(3.5→4.1, 형상 차이 안에 묻힘). (ii) **150 µm "leveled"** 디스크는
같은 크기의 일반 디스크(추정 3.5~4 µm)보다 훨씬 고운 2.0 µm — 팁 높이를 정렬하면 그릿
크기를 줄이지 않고도 조도를 낮출 수 있다는, 돌출 균일성의 직접 증거(Lv1-2 노트의 3M
DOP≈15 µm 논의와 같은 논문). 저자 본문: "In general, a finer pad finish can be obtained by
using a conditioner with smaller diamond sizes. However, there are practical limits to reducing
diamond size... We have also developed fine-finish conditioners by improving the diamond tip
height distribution." — 단, "surface finish"의 측정 정의·기준 패드가 본문에 없어 **절대값은
3M 내부 척도로만 유효**(다른 출처 Ra와 직접 비교 불가).

### 2.3 그릿 크기(100 vs 325 grit) → 높이분포 감쇠길이 λ: Sun (2009) / Sun et al. (2010)

출처(1차): Ting Sun, *Pad-Wafer and Brush-Wafer Contact Characterization in Planarization and
Post-Planarization Processes*, PhD dissertation, Univ. of Arizona (2009),
http://hdl.handle.net/10150/194898 (공개, 전문 확보 `papers/sun2009-dissertation-ua-pad-wafer-contact.pdf`).
Ch. 7.1이 T. Sun, L. Borucki, Y. Zhuang, A. Philipossian, "Investigating the effect of diamond
size and conditioning force on chemical mechanical planarization pad topography",
*Microelectron. Eng.* 87, 553–559 (2010), doi.org/10.1016/j.mee.2009.08.007 (Crossref 실존
확인, Elsevier 유료 — Unpaywall/OpenAlex/S2 전부 closed, **저널판 미확보**)의 학위논문판이다.

조건: Rohm & Haas IC1000 plain 패드, Mitsubishi Materials(MMC) TRD 디자인 100 mm 디스크
**100-grit vs 325-grit**(같은 배치 디자인, 그릿 크기만 다름), 하중 3.6 / 8.0 lb, DIW
220 mL/min. λ는 Veeco NT9800 백색광 간섭계(2×2 mm 높이 PDF 우측 꼬리) 및 Araca ILD-100
증분하중 시험(압력비 e배당 변위) 두 방법으로 독립 추출, 패드 반대편 2표본.

Figure 7.4 판독(±0.3 µm):

| 조건 | ILD 표본1 | ILD 표본2 | 간섭계 표본1 | 간섭계 표본2 | 평균 |
|---|---|---|---|---|---|
| 325-grit, 3.6 lb | 3.2 | 3.2 | 3.5 | 3.3 | 3.3 |
| 325-grit, 8.0 lb | 4.8 | 4.0 | 4.3 | 4.0 | 4.3 |
| 100-grit, 3.6 lb | 3.8 | 3.9 | 3.2 | 3.2 | 3.5 |
| 100-grit, 8.0 lb | 8.0 | 7.4 | 5.5 | 5.8 | 6.7 |

저자 서술(p.288–289): 하중 증가에 따른 λ 증가는 "about 20% for 325 grit, while it increases
by 60% for 100 grit"; 같은 하중에서 그릿 크기 효과는 "both sizes give similar λ at the low
load, while 100 grit diamonds give 30% higher value than the 325 grit at the higher load".
해석: **저하중에서는 그릿 크기와 무관하게 다이아 최상단 모서리만 패드를 깎아 λ가 같고,
하중이 커져 다이아의 더 넓은 부분이 관여할 때 비로소 크기 차이가 λ로 나타난다.** 즉
그릿 크기의 조도 효과는 하중과 **교호작용**한다 — 단독 스케일링 법칙이 없다.
§3.3 verify에서 판독값으로 저자 백분율을 재계산해 대조한다.

같은 학위논문 Ch. 7.2(Type A 디스크 vs "약 3배 cut rate"의 Type B 디스크, 7.0 lbf, 4 psi
사파이어창 공초점 측정, Fig. 7.14/7.15 판독):

| 패드 | 디스크 | A_f (접촉면적분율) | η_c (#/mm²) |
|---|---|---|---|
| CMC EPIC D100-1 | A (덜 공격적) | 5.6e-4 | 237 |
| D100-1 | B (≈3× cut rate) | 0.55e-4 | 58 |
| D100-2 | A | 2.9e-4 | 110 |
| D100-2 | B | 0.8e-4 | 42 |
| IC1000 k-groove | A | 4.4e-4 | 88 |
| IC1000 k-groove | B | 1.1e-4 | 80 |

저자 결론(p.306–308): 공격적 디스크는 접촉면적도 접촉점 수도 **줄이지만** MRR은 높다 —
η_c/A_f 비(접촉당 평균 면적의 역수, 저자 Eq. 7.14에서 평균 실접촉압력에 비례)가 커지기
때문. Type A/B의 그릿 스펙은 본문에 없다(**디스크 설계값 미기재**, "aggressiveness"로만
구분).

### 2.4 그릿 크기·형상·개수가 극단적으로 다른 두 디스크: McAllister et al. (2018, 2019)

출처: J. McAllister, C. Stuffle, Y. Sampurno, D. Hetherington, J. Sierra Suarez, L. Borucki,
A. Philipossian, "Effect of Conditioner Type and Downforce, and Pad Surface Micro-Texture on
SiO2 CMP Performance", *Micromachines* 10(4), 258 (2019), doi.org/10.3390/mi10040258,
PMC6523751 (CC-BY, Europe PMC에서 PDF·JATS XML 전문 확보). 디스크 스펙(§2 원문):
- **ABT S3410845N**: "tens of thousands" Type 3½(sharp 쪽) 다이아, 평균 크기 **173 µm**,
  기판 위 돌출 **52 µm**, 도넛형 외곽 배치.
- **EHWA CVD 1.3K**: 45×45 µm² 정사각 팁 **1,300개** 균일 가공, 높이 50 µm, 전면 CVD
  다이아 코팅(blocky).
IC1000 K-groove + Suba IV, 브레이크인 30 min 후 마이크로텍스처(Table 1, 원문은 상대값만):

| 디스크 | 하중 | 평균 정점높이 | 평균 정점곡률 | 접촉면적 % | 접촉밀도 |
|---|---|---|---|---|---|
| ABT | X | X | X | 4X | 2.2X |
| ABT | 3X | X | X | 3X | 1.6X |
| EHWA | 3X | 1.3X | 2.4X | X | X |

즉 큰 sharp 다이아 수만 개(ABT)는 CVD 소형 팁 1,300개(EHWA) 대비 **접촉면적 3~4배,
접촉밀도 1.6~2.2배**, 반면 EHWA는 정점이 1.3배 높고 곡률 2.4배(더 뾰족). 저자 해석: ABT의
큰·날카로운·많은 다이아가 절삭 효율을 높여 **패드 파편(fragments)과 붕괴된 기공벽**을 많이
만들고, 이 조각들이 접촉면적·밀도 통계를 부풀린다(Fig.1 접촉이미지의 흑점). 같은
저자들의 2018년 ECS JSS 논문 두 편(doi.org/10.1149/2.0261811jss 디스크 종류·하중 편,
doi.org/10.1149/2.0271805jss 하중·브레이크인 편)이 절대값을 주는데, IOP 사이트는 봇 차단으로
PDF를 못 받았고 후자만 Univ. of Arizona 리포지토리(http://hdl.handle.net/10150/628667)
저자 최종원고로 확보했다(`papers/mcallister2018-jss-downforce-breakin-microtexture.pdf`).
그 Table I(EHWA CVD 디스크, 60 min 브레이크인, IC1000 K-groove):

| 하중 (lbf) | 평균 정점높이 (µm) | 평균 정점곡률 (원문 단위 1/µm²) | 접촉밀도 (#/mm²) | 접촉면적 (%) |
|---|---|---|---|---|
| 6 | 21 | 407 | 82 | 0.022 |
| 10 | 20.5 | 323 | 143 | 0.052 |

⚠ 이 논문 초록은 "contact area and contact density **decreased** with conditioning downforce"
라고 쓰여 있으나 Table I과 본문("higher conditioning downforces results in larger contact
areas")은 **증가**를 보인다 — 초록과 표가 상충. 하중 효과는 형제 영역이라 이 노트는
판정하지 않고 모순만 기록한다. 절대값 오더(접촉밀도 ~10²/mm², 접촉면적 ~10⁻²%)는 Sun
(2009)의 4 psi 값(10¹~10² /mm², 10⁻²~10⁻¹ %)과 같은 자릿수다.

### 2.5 디스크 종류 → λ와 정점곡률 동시 측정: Liao (2014)

출처: Xiaoyan Liao, PhD dissertation, Univ. of Arizona (2014), http://hdl.handle.net/10150/323377
(공개, 전문 확보 `papers/liao2014-dissertation-ua-consumables.pdf`). Ch.4(=Liao et al., ECS
Solid-State Lett. 14, H201 (2011)): IC1010 M-groove, 26.7 N, **3M A2810 vs MMC 100-grit TRD**
→ λ = 3.84 vs 3.64 µm(거의 같음), Cu MRR 3,415 vs 2,457 Å/min. Ch.7(IC1000 K-groove, STI):
λ = 3.18 vs 2.92 µm(9% 차), **정점곡률 κ_s = 0.51 vs 0.89 µm⁻¹**(MMC가 1.7배 뾰족) →
등가 정점반경 R = 1/κ_s ≈ 1.96 vs 1.12 µm. 블랭킷 MRR은 3,167±26 vs 3,315±103 Å/min으로
같지만 MMC 디스크의 dishing·erosion이 10% 패턴밀도에서 약 3배. 저자 결론: **λ(높이 통계)가
같아도 R(정점 형상)이 다를 수 있고, 그 R이 패턴 성능을 가른다** — GW 파라미터 중 η·σ만으로는
부족하고 R을 독립 측정해야 한다는 근거. 3M A2810의 그릿 크기 스펙은 본문에 없음(미기재).

### 2.6 공격성 → 실접촉면적·높이분포 형태: Lawing (2004)

출처: A. S. Lawing, "Pad Conditioning Effects in CMP", NCCAVS CMPUG 2004-05-05 공개 PDF
(`papers/lawing2004-cmpug-pad-conditioning-effects.pdf`, 이번 회차 재확보·슬라이드 8–10 판독).
피어리뷰판 doi.org/10.1557/proc-732-i5.3 (Lawing 2002, 본문 미확보). 슬라이드 10: 공격성
low/medium/high 컨디셔너 → 정상상태 **접촉면적 11.3 / 7.7 / 2.2 %**, asperity 종횡비
(diameter/height) 분포가 공격성이 낮을수록 넓고(10–60), 높을수록 좁고 낮음(0–15, 즉 뾰족).
슬라이드 9: **솔리드(무기공) 패드의 고유 높이분포는 거의 Gaussian**이며 폭이 공격성에
따라 커진다(High가 ±20 µm 스케일, Low는 ±5 µm 스케일 — 그래프 눈금 판독, 수치 라벨 없음).
기공 패드는 필러가 조도를 지배하고 컨디셔닝은 "추가 조도 주파수"를 얹는다. 접촉면적
절대값(2~11 %)이 Sun·McAllister의 공초점 값(0.01~0.06 %)과 **두 자릿수 차이**인 것은
측정법(Lawing은 높이 PDF 기반 추정, 공초점은 광학 직접접촉)과 하중 정의 차이 때문으로
추정 — **절대값 상호 비교 불가, 같은 출처 안의 비율만 사용**.

### 2.7 GW 파라미터를 디스크 스펙에서 직접 뽑는 유일한 명시적 규칙: Ring, Prasad, Dirksen

출처: T. A. Ring, A. Prasad, J. A. Dirksen, "Dynamic CMP Pad Asperity Population Balance for
Conditioning and Polishing", 저자 공개 PDF https://my.che.utah.edu/~ring/Publications-PDFs/J-120.pdf
(연도 미기재, [[../equipment/conditioner-asperity-population-balance]]가 원문 확보, 이번
회차 재다운로드 `papers/ring-prasad-dirksen-asperity-population-balance-J120.pdf`). Table 1–2:

| 항목 | 규칙(표에 병기) | 표의 수치 |
|---|---|---|
| asperity 밀도 η | (1/D_grit)² | 2.938×10¹¹ #/m² |
| 평균 asperity 높이 σ | D_grit/2 | 8.112 µm |
| asperity 곡률반경 β | D_grit (Table 2) / 8.112 µm (Table 1) | — |
| 그릿 지름 D_grit | Saesol S-80 디스크 | 190 µm |

"Mean asperity height and asperity radius of curvature were extracted from the conditioner grit
size" — 즉 **η ∝ 1/D_grit², σ ∝ D_grit** 이라는 매핑을 논문이 명시한다. 그러나 D_grit=190 µm를
대입하면 (1/D)²=2.8×10⁷ /m², D/2=95 µm로 표의 수치(2.9×10¹¹, 8.112 µm)와 각각 4자릿수·12배
어긋난다(§3.4 verify). 8.112 µm는 본문에서 "새 패드 Veeco 분포가 평균 0, **표준편차 8.112 µm**의
정규분포"라고 실측값으로 재등장하므로, 표의 σ·η는 규칙의 산출물이 아니라 실측 피팅값을
규칙 옆에 병기한 것으로 추정한다. 규칙 자체는 물리적으로 그럴듯하지만(그릿 하나가 자기
크기 스케일의 고랑을 하나 남긴다는 그림) **이 논문 안에서 수치로 검증되지 않았다.**

### 2.8 컨디셔닝된 패드의 GW 실측값 참고 (디스크 스펙 미기재)

Jeong et al. (2024), doi.org/10.3390/ma17081817, PMC11051262 —
[[pad-glazing-mechanism-mrr-decay]] §2에서 판독한 컨디셔닝 직후 IC1000 값: σ_z(0)=4.51 µm,
μ_R(0)≈7.5–8 µm, 시야 내 접촉점 N≈110(1분 컨디셔닝 후 108–120). 사용 디스크 스펙은 논문에
없다. 이 값들은 §2.3의 λ(3–7 µm)·§2.7의 σ(8.1 µm)와 같은 자릿수(µm)이고, R은 Liao의
1–2 µm(정점 곡률 정의)보다 4~7배 크다 — **R은 정의(최고점 곡률 vs 등가원 반경)에 따라
수 배 달라지므로 출처를 섞으면 안 된다.**

## 3. 정량 재현 (python verify)

### 3.1 그릿 밀도 → Ra·Rpk 멱법칙 회귀 (Kwon 2013 Fig.2 판독값)

```python verify
# Kwon et al. 2013, Tribol. Int. 67, 272 (doi:10.1016/j.triboint.2013.08.008) Fig.2 판독값
# 밀도 시리즈(grade 640 고정): 17k / 40k / 60k 그릿
import numpy as np
dens = np.array([17e3, 40e3, 60e3])          # 그릿 개수/디스크
Ra   = np.array([8.05, 6.8, 5.95])           # µm, Fig.2a 눈금 판독 ±0.15
Rpk  = np.array([3.75, 2.25, 1.7])           # µm, Fig.2b 눈금 판독 ±0.1
Ra_text_17k, Ra_text_60k = 7.89, 6.37       # µm, 본문 명시(Fig.7 문맥)

# log-log 선형회귀: Ra ∝ N^a, Rpk ∝ N^b
a, _ = np.polyfit(np.log(dens), np.log(Ra), 1)
b, _ = np.polyfit(np.log(dens), np.log(Rpk), 1)
print(f"Ra ∝ N^{a:.2f}, Rpk ∝ N^{b:.2f}")
assert a < 0 and b < 0, "밀도↑ → 조도↓ 방향이 저자 결론(§3)과 달라짐"
assert b < a, "Rpk(봉우리 지표)가 Ra보다 밀도에 더 민감해야 함(판독값 기준) — 아니면 판독 재확인"
assert -0.35 < a < -0.15, f"Ra 지수 {a:.2f}가 판독 오차 범위(±0.15µm)로 설명되는 구간 밖"

# 본문 명시값(7.89/6.37)과 Fig.2 판독값(8.05/5.95)의 17k/60k 비율 대조
ratio_fig = Ra[0] / Ra[2]
ratio_txt = Ra_text_17k / Ra_text_60k
print(f"17k/60k Ra 비율: Fig.2 판독 {ratio_fig:.3f} vs 본문 {ratio_txt:.3f}")
# 두 값은 일치하지 않는다(판독 1.353 vs 본문 1.239, 약 9% 차이). 원인: 본문값은 Fig.7 논의용
# 별도 측정으로 추정 — 숨기지 않고 허용폭 15%로 '같은 실험군'인지만 확인한다.
assert abs(ratio_fig - ratio_txt) / ratio_txt < 0.15, "Fig.2 판독과 본문 수치가 다른 실험군 수준으로 다름"
print("OK: 밀도 3점 멱법칙 방향·지수 확인, 본문/그림 비율 9% 차이 기록")
```

실행 결과: Ra ∝ N^−0.23, Rpk ∝ N^−0.62 (N = 그릿 개수, 3점 판독 기반). 즉 그릿 수를 3.5배
늘리면 Ra는 25%, Rpk는 54% 감소 — 봉우리 지표(Rpk)가 평균조도(Ra)보다 밀도에 2.7배 민감하다.
Kwon 본문의 17k/60k Ra 비 1.24와 Fig.2 판독 비 1.35는 9% 차이로 완전 일치가 아님을 기록한다
(Kwon et al. 2013). 3점 회귀라 지수의 신뢰구간은 넓다(**지수 절대값은 참고용**).

### 3.2 그릿 크기 → 표면 마무리 멱법칙 (3M Fig.1 군집 중심)

```python verify
# Pysher, Goers, Zabasajja 2010, MRS Proc. 1249-E02-04 (doi:10.1557/proc-1249-e02-04) Figure 1
# 군집 중심 판독(±0.15 µm). 'leveled' 150 µm는 팁 정렬 설계라 크기 회귀에서 제외.
import numpy as np
D  = np.array([45, 53, 90, 125, 180, 180, 250], float)      # µm 다이아 크기
SF = np.array([1.7, 1.95, 2.5, 3.5, 4.2, 4.1, 4.1])          # µm surface finish 군집 중심
SF_leveled_150 = 2.0                                          # µm, 150 µm leveled 디스크

n, logC = np.polyfit(np.log(D), np.log(SF), 1)
pred = np.exp(logC) * D**n
r2 = 1 - np.sum((SF - pred)**2) / np.sum((SF - SF.mean())**2)
print(f"surface finish ∝ D^{n:.2f}, R²={r2:.3f}")
assert 0.4 < n < 0.8, f"크기 지수 {n:.2f}가 판독으로 예상한 0.4~0.8 밖"
assert r2 > 0.85, "멱법칙 설명력이 낮음 — 형상(sharp/semi-sharp) 교란이 크기 효과를 압도"

# 포화 확인: 125→250 µm 구간 증가율이 45→125 µm 구간보다 작다
g_small = np.log(3.5/1.7) / np.log(125/45)
g_large = np.log(4.1/3.5) / np.log(250/125)
print(f"국소 지수: 45→125µm {g_small:.2f}, 125→250µm {g_large:.2f}")
assert g_large < 0.5 * g_small, "대형 그릿 구간의 조도 포화가 관찰되지 않음"

# leveled 설계: 같은 크기의 멱법칙 예측 대비 얼마나 고운가
pred_150 = np.exp(logC) * 150**n
print(f"150 µm 멱법칙 예측 {pred_150:.2f} µm vs leveled 실측 {SF_leveled_150} µm")
assert SF_leveled_150 < 0.65 * pred_150, "팁 정렬(leveled) 효과가 예측 대비 35% 이상 개선이 아님"
print("OK: 크기 멱법칙·포화·leveled 효과 3건 확인")
```

실행 결과: surface finish ∝ D^0.57 (R² ≈ 0.91), 45→125 µm 구간 국소 지수 0.71, 125→250 µm
구간 0.23으로 대형 그릿에서 포화. 150 µm leveled 디스크는 멱법칙 예측(3.5 µm)의 57%인
2.0 µm — 같은 멱법칙에서 2.0 µm에 해당하는 일반 디스크 크기는 약 55 µm이므로, **돌출 높이
정렬이 그릿 크기를 150→55 µm로 줄인 것과 맞먹는 조도 개선**을 준다(Pysher et al. 2010,
군집 중심 판독 기반이라 지수 ±0.1은 판독 오차).

### 3.3 그릿 크기 × 하중 → λ: 판독값으로 저자 백분율 재계산 (Sun 2009 Fig. 7.4)

```python verify
# Sun 2009 dissertation (hdl.handle.net/10150/194898) Fig.7.4 판독값(µm, ±0.3)
# = Sun et al. 2010 Microelectron. Eng. 87, 553 (doi:10.1016/j.mee.2009.08.007) 학위논문판
import numpy as np
lam = {  # (grit, lb): [ILD s1, ILD s2, Interf s1, Interf s2]
    (325, 3.6): [3.2, 3.2, 3.5, 3.3],
    (325, 8.0): [4.8, 4.0, 4.3, 4.0],
    (100, 3.6): [3.8, 3.9, 3.2, 3.2],
    (100, 8.0): [8.0, 7.4, 5.5, 5.8],
}
mean = {k: np.mean(v) for k, v in lam.items()}
intf = {k: np.mean(v[2:]) for k, v in lam.items()}   # 간섭계만
# 저자 서술: 하중 효과 +20%(325), +60%(100); 8 lb에서 100 vs 325 = +30%; 3.6 lb에서는 '유사'
author = {"load325": 0.20, "load100": 0.60, "grit_hi": 0.30}
calc_all = {"load325": mean[(325,8.0)]/mean[(325,3.6)]-1,
            "load100": mean[(100,8.0)]/mean[(100,3.6)]-1,
            "grit_hi": mean[(100,8.0)]/mean[(325,8.0)]-1}
calc_int = {"load325": intf[(325,8.0)]/intf[(325,3.6)]-1,
            "load100": intf[(100,8.0)]/intf[(100,3.6)]-1,
            "grit_hi": intf[(100,8.0)]/intf[(325,8.0)]-1}
for k in author:
    print(f"{k}: 저자 {author[k]*100:.0f}% | 4값 평균 {calc_all[k]*100:.0f}% | 간섭계만 {calc_int[k]*100:.0f}%")
# 방향은 모두 저자와 일치해야 한다
assert all(v > 0 for v in calc_all.values())
assert calc_all["load100"] > calc_all["load325"], "coarse grit에서 하중 효과가 더 커야 함"
grit_lo = mean[(100,3.6)]/mean[(325,3.6)]-1
print(f"3.6 lb에서 100 vs 325 grit: {grit_lo*100:.0f}% (저자: '유사')")
assert abs(grit_lo) < 0.15, "저하중에서 그릿 크기 효과가 '유사'하다는 저자 서술과 불일치"
# 크기: 4값 평균은 저자 백분율과 맞지 않는다(30/89/56% vs 20/60/30%) — 간섭계만 쓰면 근접(22/77/36%).
# 저자가 어느 방법 기준으로 백분율을 냈는지 본문에 없음 → 간섭계 기준으로 추정하되 20%p 허용
for k in author:
    assert abs(calc_int[k] - author[k]) < 0.20, f"{k}: 간섭계 판독으로도 저자 백분율과 20%p 이상 차이"
print("OK: 방향 3건 + 저하중 무차이 재현, 백분율 절대값은 방법 의존(간섭계 기준 근접) 기록")
```

실행 결과: 하중 효과는 325-grit +30%, 100-grit +89%(4값 평균) / +22%, +77%(간섭계만); 8 lb에서
100 vs 325 grit +56% / +36%; 3.6 lb에서는 +7%로 "유사". 저자 서술 백분율(20/60/30%)과는 간섭계
판독만으로 근접하고 ILD 포함 평균으로는 안 맞는다 — **저자가 어느 방법을 기준으로
백분율을 냈는지 불명**, 판독 오차(±0.3 µm, 저λ에서 ±10%)도 겹친다(Sun 2009). 정성 결론
(coarse grit일수록 하중에 민감, 저하중에서는 크기 무관)은 4가지 조합 모두에서 재현된다.

### 3.4 GW 지수분포로 "공격적 디스크 → 접촉면적 감소"를 얼마나 설명하는가 + Ring 규칙 검산

```python verify
# (a) hertz-gw-contact-mechanics §4: 지수분포 GW에서 A_r/W = 3π√(Rβ)/(4E*Γ(5/2)), β=1/λ
#     → 하중·E*·R 고정 시 A_r ∝ λ^(-1/2). Sun 2009 Ch.7.1의 λ 극단비로 예측 vs Ch.7.2 실측.
import numpy as np
lam_min, lam_max = 3.3, 6.7          # µm, Sun Fig.7.4 평균 최소/최대 (325g 3.6lb / 100g 8lb)
gw_ratio = (lam_max / lam_min) ** -0.5   # 덜 공격적 대비 공격적 표면의 A_r 비 예측(R 고정)
Af_ratio_sun = {"D100-1": 0.55e-4/5.6e-4, "D100-2": 0.8e-4/2.9e-4, "IC1000": 1.1e-4/4.4e-4}  # Type B/A
Af_ratio_lawing = 2.2/11.3            # high/low aggressiveness (Lawing 2004, 추정법 상이)
print(f"GW(λ만, R고정) 예측 A_r 비 = {gw_ratio:.2f}")
for k, v in Af_ratio_sun.items():
    print(f"  Sun 실측 B/A {k}: {v:.2f}")
print(f"  Lawing high/low: {Af_ratio_lawing:.2f}")
# 실측 감소폭이 GW-λ 예측보다 훨씬 크다 — 예측이 실측을 설명하지 못함을 assert로 고정
assert all(v < 0.5 * gw_ratio for v in Af_ratio_sun.values()), "GW λ 효과만으로 설명될 정도로 감소폭이 작다면 §4 해석을 바꿔야 함"
assert Af_ratio_lawing < 0.5 * gw_ratio
# 필요한 R 변화: A_r ∝ √R 이므로 실측 비를 맞추려면 R_B/R_A = (실측비/GW비)^2
R_needed = {k: (v / gw_ratio) ** 2 for k, v in Af_ratio_sun.items()}
print("λ 효과 제외 후 실측을 맞추는 데 필요한 R_B/R_A:", {k: round(v, 3) for k, v in R_needed.items()})
assert all(v < 0.2 for v in R_needed.values()), "정점반경이 1/5 이하로 줄어야 설명 가능 — 물리적으로 큰 요구"

# (b) η_c/A_f 비 (Sun Eq.7.14 평균 실접촉압력 ∝) : 공격적 디스크가 더 커야 한다(저자 결론)
eta = {"D100-1": (237, 58), "D100-2": (110, 42), "IC1000": (88, 80)}
Af  = {"D100-1": (5.6e-4, 0.55e-4), "D100-2": (2.9e-4, 0.8e-4), "IC1000": (4.4e-4, 1.1e-4)}
for k in eta:
    rA = eta[k][0]/Af[k][0]; rB = eta[k][1]/Af[k][1]
    print(f"  {k}: η_c/A_f  A={rA:.2e}  B={rB:.2e}  (B/A={rB/rA:.1f}배)")
    assert rB > rA, f"{k}: 공격적 디스크의 η_c/A_f가 더 크지 않음 — 저자 결론과 불일치"
# 단순 GW 평균 실접촉압력 p/A_f (4 psi): 자릿수만 확인
p_nom = 4 * 6894.76
p_real_A = p_nom / 5.6e-4; p_real_B = p_nom / 0.55e-4
print(f"  D100-1 p/A_f: A {p_real_A/1e6:.0f} MPa, B {p_real_B/1e6:.0f} MPa")
assert 10e6 < p_real_A < 100e6 and p_real_B > 100e6

# (c) Ring et al. Table 1 규칙 검산: η=(1/Dgrit)², σ=Dgrit/2 vs 표의 수치
D = 190e-6
eta_rule, eta_tab = (1/D)**2, 2.938e11
sig_rule, sig_tab = D/2, 8.112e-6
print(f"  η 규칙 {eta_rule:.2e} vs 표 {eta_tab:.2e} (×{eta_tab/eta_rule:.0f}); σ 규칙 {sig_rule*1e6:.0f} µm vs 표 {sig_tab*1e6:.3f} µm (×{sig_rule/sig_tab:.1f})")
assert eta_tab / eta_rule > 1e3 and sig_rule / sig_tab > 5, "Ring 표의 수치가 규칙과 맞는다면 §2.7 서술을 정정해야 함"
D_from_eta = 1/np.sqrt(eta_tab); D_from_sig = 2*sig_tab
print(f"  역산 Dgrit: η에서 {D_from_eta*1e6:.2f} µm, σ에서 {D_from_sig*1e6:.2f} µm")
assert abs(D_from_eta - D_from_sig) / D_from_sig > 0.5, "단일 Dgrit으로 두 값이 동시에 설명되면 규칙이 일관된 것"
print("OK: GW-λ 단독 설명 실패(정량), η_c/A_f 방향 3/3, Ring 규칙-수치 불일치 확인")
```

실행 결과: λ 최대/최소 비 2.0에서 지수분포 GW(R 고정)가 예측하는 실접촉면적 비는 0.70인데,
Sun (2009)의 Type B/A 실측 비는 0.10 / 0.28 / 0.25, Lawing (2004)의 high/low 비는 0.19 —
**GW의 λ 효과만으로는 감소폭의 1/3~1/7밖에 설명하지 못한다.** λ 효과를 제외하고 남는 몫을
정점반경으로 메우려면 R이 1/50~1/6로 줄어야 한다. 이는 (i) 공격적 디스크가 정점을 훨씬
뾰족하게 만든다(Liao 2014의 κ_s 1.7배 = R 0.57배로는 부족), (ii) 덜 공격적 디스크의
접촉면적에 "완전히 지지되지 않은 패드 파편·붕괴 기공벽"의 큰 flat 접촉이 섞여 있다
(McAllister 2019, Liao 2014 Ch.4의 해석), (iii) 소성 접촉 — 세 요인이 겹친 결과로
해석한다(정량 분리는 미검증). p/A_f로 계산한 명목상 평균 실접촉압력은 4 psi에서 49 MPa
(Type A) / 500 MPa (Type B)로 PU 항복강도 오더를 넘어 **탄성 GW 가정 자체가 공격적 표면에서
깨진다**는 신호다([[gw-nominal-vs-local-pressure]] §2의 소성 전이 경고와 정합). η_c/A_f
비는 세 패드 모두 Type B가 1.4~3.6배 커서 저자 결론과 방향 일치. Ring et al. 표의 η·σ는
D_grit=190 µm 규칙값과 10⁴배·12배 어긋나고, η와 σ에서 역산한 D_grit(1.85 µm vs 16.2 µm)도
서로 맞지 않아 규칙은 이 논문에서 수치 검증되지 않았음을 확인한다.

## 4. 종합 — 디스크 설계 파라미터 ↔ 패드 표면 통계 ↔ GW 파라미터 매핑표

| 디스크 파라미터 ↑ | Ra / Rpk | λ (σ, 1/β) | η (정점밀도) | R (정점반경) | A_f (실접촉면적) | 근거·신뢰도 |
|---|---|---|---|---|---|---|
| 그릿 밀도(개수) | ↓ (Ra∝N^−0.23, Rpk∝N^−0.62) | (미측정) | ↑ 추정 | (미측정) | (미측정) | Kwon 2013 §3.1, 3점 회귀 |
| 그릿 크기 | ↑ (finish∝D^0.57, 125 µm 이상 포화) | ↑ 단 고하중에서만(+36~56%), 저하중 무차이 | — | — | — | Pysher 2010 §3.2, Sun 2009 §3.3 |
| 형상 sharp→blunt | Ra 7.0→5.85, Rpk 2.75→1.8 µm | — | — | — | — | Kwon 2013 (grade 625→925) |
| 돌출 높이 정렬(leveled) | ↓ 크게(예측 대비 −43%) | — | — | — | — | Pysher 2010 §3.2 |
| 공격성(총합 cut rate) | ↑ | ↑ | **↓** (η_c 기준 0.25~0.9배) | ↓ 추정 | **↓** (0.1~0.28배) | Sun 2009 §3.4, Lawing 2004 |
| 큰 sharp 다이아 다수(ABT) vs CVD 소형 팁(EHWA) | — | 정점높이 0.77배 | 접촉밀도 1.6~2.2배 | 곡률 0.42배(둔함) | 3~4배 | McAllister 2019, 파편 효과 포함 |

읽는 법: "공격성↑ → η_c·A_f↓"와 "ABT(더 공격적) → 접촉밀도·면적↑"는 **상충처럼 보이지만**,
McAllister는 패드 파편이 접촉 통계를 부풀린다고 명시했고 Sun은 파편 논의 없이 정상 정점만
센 것으로 보인다 — 즉 **접촉 이미지 기반 η_c·A_f는 파편 오염 여부에 따라 부호까지 바뀔 수
있는 지표**다. GW 파라미터로 쓰려면 파편을 제외한 "지지된 정점"만 세야 한다(현재 어느
출처도 그 분리 수치를 주지 않음 — 문헌 공백).

**GW 파라미터 초기값 제안(이 노트의 종합, 시뮬레이터 캘리브레이션 출발점)**:
- σ(=λ=1/β): IC1000 계열, 100–325 grit 통상 하중에서 **3–7 µm**(Sun 2009), 컨디셔닝 직후
  σ_z 4.5 µm(Jeong 2024), 새 패드 8.1 µm(Ring et al.). 그릿 크기 3.25배(325→100 grit)에
  고하중 λ 1.4~1.6배 → 작업가설 λ ∝ D^0.3~0.4(고하중), D^0(저하중).
- η: 접촉 정점밀도 40–240 /mm² (4 psi, 공초점, Sun 2009); 전체 정점밀도는 이보다 크며
  Ring 표의 2.9×10¹¹ /m²(=2.9×10⁵ /mm²)는 접촉밀도의 10³배 — 전체 vs 접촉 정점 구분 필수.
- R: 최고점 곡률 정의로 1.1–2.0 µm(Liao 2014), 등가원 정의로 7.5–8 µm(Jeong 2024).
- 디스크 스펙 → 이 값들로의 **닫힌 수식은 문헌에 없다**(Ring 규칙은 수치 미검증, Borucki
  2004 이론은 원문 미확보). 시뮬레이터는 (D_grit, 밀도, 형상, leveled 여부)를 §3의 멱법칙
  지수로 상대 스케일링하고 절대값은 캘리브레이션하는 구조가 현실적이다.

## 5. Preston 계수·MRR과의 연결

[[../cmp/preston-luo-dornfeld-mrr]]의 K_p 안에는 A_r/A_n과 국소압력이 숨어 있다
([[hertz-gw-contact-mechanics]] §1). 이 노트의 데이터가 그 분해에 주는 제약:
1. **조도↑ → MRR↑** (Kwon 2013: 17k·625에서 Ra·Rpk·MRR 모두 최대; 3M: "finer texture giving
   higher [W] rates"라는 반대 방향 문헌도 인용 — 재료·슬러리 의존). Kwon은 Rpk가 MRR과 가장
   강한 상관이라고 명시.
2. **A_f↓ 인데 MRR↑** (Sun 2009 Type B): Preston의 "MRR ∝ P"를 "MRR ∝ (접촉점 수)×(접촉당
   제거)"로 읽으면, 공격적 디스크는 접촉점 수를 줄이고 접촉당 압력(∝ η_c/A_f)을 올려 MRR을
   높인다 — [[gw-nominal-vs-local-pressure]] §2의 "압력은 접촉점 개수를 늘린다"는 그림에
   "디스크는 접촉당 압력을 바꾼다"는 두 번째 축이 추가된다. K_p ∝ f(η_c/A_f)가 작업가설.
3. **A_f↑ 인데 COF↓, MRR↑** (McAllister 2019 ABT): 파편 접촉은 윤활되어 COF엔 기여하지
   않고 MRR엔 기여 — Preston 계수를 "고체 미끄럼 접촉"과 "윤활 미끄럼 접촉" 두 항으로
   나눠야 한다는 저자 주장(Borucki et al. 2009, doi.org/10.1143/jjap.48.115502 —
   IOP 봇차단으로 **원문 미확보**, McAllister 2019 §3의 재서술만 확인).
4. Borucki, Witelski, Please (2004), "A theory of pad conditioning for chemical-mechanical
   polishing", *J. Eng. Math.* 50, 1–24, doi.org/10.1023/b:engi.0000042116.09084.00 — 그릿의
   절삭 기하에서 λ를 유도하는 유일한 해석 이론으로 Sun 2009가 인용. Springer 유료, Unpaywall·
   S2 closed, **원문 미확보** → λ의 디스크 스펙 의존 수식은 이 노트에 넣지 않는다.

## 6. 한계·미확보·문헌 공백 (정직 기록)

- **1차 저널판 미확보**: Sun et al. 2010 MEE(학위논문판으로 대체, 동일 데이터·저자),
  McAllister 2018 ECS JSS 디스크 종류 편(doi.org/10.1149/2.0261811jss, 2019 PMC 논문의
  상대값 Table 1로 대체), Borucki 2004·2009, Yang et al. 2010 IJMT "Effects of diamond size
  of CMP conditioner on wafer removal rates and defects for solid (non-porous) CMP pad"
  (doi.org/10.1016/j.ijmachtools.2010.06.007, closed), Li, Chen, Shiu 2021 "Analysis on Pad
  Surface Roughness of Diamond Conditioning Process for CMP" ECS JSS 10, 044009
  (doi.org/10.1149/2162-8777/abf47e, OA이나 IOP 봇차단으로 미확보 — 제목상 이 단원의 가장
  직접적 후속 자료, Lv3-1 이월). 미러 사이트 미러는 응답 없음(2026-09-07 재확인).
- **그래프 판독 의존**: Kwon Fig.2, 3M Fig.1, Sun Fig.7.4/7.14/7.15, Lawing 슬라이드 9는 모두
  수치 라벨 없는 그래프를 눈금 판독한 값이다. 오차 표기(±0.15~0.3 µm)를 넘는 결론은 내지
  않았고 §3 assert의 허용폭도 그에 맞췄다.
- **지표 혼재**: Ra(Kwon)·surface finish(3M)·λ(Sun/Liao)는 정의가 달라 절대값 교차 비교를
  하지 않았다. 3M "surface finish"의 정의는 미기재.
- **그릿 밀도 → λ·η·R** 직접 실측은 확보 못 함(Kwon은 Ra·Rpk만). **돌출 높이 → 표면 통계**는
  3M leveled 1점뿐. 디스크 스펙 → GW 3파라미터의 닫힌 매핑식은 어느 1차 출처에도 없다.
- **접촉 통계의 파편 오염**: §4에서 지적한 대로 η_c·A_f가 파편 포함 여부로 부호가 바뀔 수
  있으나 분리 수치는 어느 출처도 없음.
- 1차 출처 표기·수치 내부 불일치 3건을 그대로 기록: Kwon 본문 vs Fig.2(9%), McAllister 2018
  초록 vs Table I(방향 반대), Ring 규칙 vs 표(10⁴배).

## 7. 구현 요청

→ [[../../agents/disk-design/PROFILE]] "## 구현 요청" 절에 기재: (1) 디스크 스펙 → GW
파라미터 상대 스케일링 함수(§3.1/3.2 지수, §4 초기값), (2) 접촉 통계 기반 K_p 분해 훅
(η_c/A_f). 이 노트는 sim/에 직접 코드를 넣지 않는다.

## 8. 출처 (한 줄 형식)

- T.-Y. Kwon et al. (2013), Tribology International 67, 272–277, doi.org/10.1016/j.triboint.2013.08.008 — 원문 전체(Lv2-1 확보).
- D. Pysher, B. Goers, J. Zabasajja (2010), "Design, Characteristics and Performance of Diamond Pad Conditioners", MRS Proc. 1249, doi.org/10.1557/proc-1249-e02-04 — 3M 공개 PDF 전문.
- T. Sun (2009), PhD dissertation, Univ. of Arizona, http://hdl.handle.net/10150/194898 — 공개 전문; Ch.7.1 = T. Sun, L. Borucki, Y. Zhuang, A. Philipossian (2010), Microelectron. Eng. 87, 553–559, doi.org/10.1016/j.mee.2009.08.007 (유료, 미확보).
- J. McAllister et al. (2019), Micromachines 10(4), 258, doi.org/10.3390/mi10040258, PMC6523751 — CC-BY 전문.
- J. McAllister et al. (2018), ECS J. Solid State Sci. Technol. 7(5), P274, doi.org/10.1149/2.0271805jss — UA 리포지토리 저자원고 전문 http://hdl.handle.net/10150/628667; 자매 논문 doi.org/10.1149/2.0261811jss 미확보.
- X. Liao (2014), PhD dissertation, Univ. of Arizona, http://hdl.handle.net/10150/323377 — 공개 전문 (Ch.4 = ECS Solid-State Lett. 14, H201, 2011).
- A. S. Lawing (2004), NCCAVS CMPUG 발표자료(공개 PDF); 피어리뷰판 doi.org/10.1557/proc-732-i5.3 (2002, 미확보).
- T. A. Ring, A. Prasad, J. A. Dirksen (연도 미기재), 저자 공개 PDF https://my.che.utah.edu/~ring/Publications-PDFs/J-120.pdf.
- S. Jeong et al. (2024), Materials 17(8), 1817, doi.org/10.3390/ma17081817, PMC11051262 — [[pad-glazing-mechanism-mrr-decay]] 경유.
- J. A. Greenwood, J. B. P. Williamson (1966), Proc. R. Soc. A 295, 300, doi.org/10.1098/rspa.1966.0242 — 원문 미확보, [[hertz-gw-contact-mechanics]] 경유.
- L. Borucki, T. Witelski, C. Please (2004), J. Eng. Math. 50, 1–24, doi.org/10.1023/b:engi.0000042116.09084.00 — 미확보(이론 참조만).
