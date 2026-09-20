# 옥사이드 막질별 Preston 계수(Kp) 배율 — thermal:TEOS:HDP:SOD:O3-TEOS:PSG:BPSG 상대비와 절대 Kp 제안 (film-oxide Lv3-2)

> film-oxide Lv3-2 | 작성일: 2026-09-15
> 선행: [[film-oxide-teos-hdp-bpsg-sod-density-hardness]] (Lv1-1, Wei 2010 경도·8종 막 개괄 — 이 노트는 그 논문의 **MRR·경도 그래프 수치를 렌더 판독으로 확보**해 배율을 뽑는다),
> [[film-oxide-hydration-layer-mechanism-cook-suratwala]] (Lv1-2, Cook 수화층·화학 지배 메커니즘 — 도핑막 배율의 물리),
> [[oxide-ceria-additive-selectivity-review-2024]] (Lv3-1, 세리아 첨가제 선택비),
> [[../cmp/ild-cmp-planarization-global-local-density]] (Lv2-1, K=blanket rate가 밀도모델에 들어가는 자리),
> [[../cmp/sti-cmp-ceria-high-selectivity-nitride-stop-dishing]] (Lv2-2, 세리아 선택비 수치는 여기서 완결 — 재서술 금지),
> [[../cmp/preston-luo-dornfeld-mrr]] (K = Kp·P·V 정의), [[../params/oxide_silica.yaml]] (분화 대상: 단일 kp_m_per_pa=1.0e-13)

## 1. 왜 이 단원이 필요한가 — Lv1이 남긴 "미검증 배율"을 수치로 닫는다

`knowledge/params/oxide_silica.yaml` 은 옥사이드 CMP를 **단일** `kp_m_per_pa = 1.0e-13`(TEOS 기준, verified)으로 다룬다.
Lv1-1(§9)은 "같은 SiO₂라도 막질별 Kp가 갈린다"를 정성적으로만 보였고, 그 노트 §8은 Wei 2010의
경도·MRR **그래프 수치를 텍스트로 못 읽어 미검증으로 남겼다**. 이 단원은 그 그래프를 페이지 이미지로
렌더해 판독하고, 두 번째 1차 논문(Liu 1995, **thermal oxide 기준 정규화값**)으로 절대 앵커를 세워,
**막질별 Kp 배율 표(thermal=1)**를 만든다. Lv1의 밀도·경도 서술은 반복하지 않는다.

## 2. 출처 (1차 3편, 전부 원문 확보·완독)

- **[W] G. Wei, S. Varghese, K. Beaman, I. Vasilyeva, T. Mendiola, A. Carswell, D. Fillmore, S. Lu
  (Micron Technology), "A Comprehensive Study on Nanomechanical Properties of Various SiO₂-based
  Dielectric Films," *IEEE WMED* 2010.** DOI: 10.1109/wmed.2010.5453755 (Crossref 확인).
  원문 PDF `papers/wei2010-sio2-nanomechanical.pdf` 완독. 상용 콜로이달 실리카 슬러리, 300 mm,
  AMAT Reflexion LK, IC1010 2-platen, 3 psi, platen 47 rpm/carrier 63 rpm, 총 70 s.
  **이 노트에서 Fig.1(경도)·Fig.2(미도핑 5종 경도-MRR)를 8× 렌더 판독**해 수치화(§3).
- **[L] C.-W. Liu, B.-T. Dai, C.-F. Yeh (National Chiao Tung Univ.), "Chemical mechanical polishing
  of PSG and BPSG dielectric films: the effect of phosphorus and boron concentration," *Thin Solid
  Films* 270, 607-611 (1995).** DOI: 10.1016/0040-6090(95)07088-5 (Crossref 확인). 원문 PDF
  `papers/liu1995-psg-bpsg-cmp.pdf` 완독. Westech 372M, IC1000/Suba IV, **fumed silica/KOH(SC-1
  Rippey) 슬러리**, 7 psi, table 20 rpm/carrier 42 rpm. **모든 값이 wet thermal oxide 기준으로
  정규화**돼 있어(Fig.2·3) thermal=1 앵커를 직접 준다. Fig.2·3을 4× 렌더 판독(§4).
- **[M] J. C. Mariscal et al. (Univ. Arizona), "Tribological, Thermal and Kinetic Characterization
  of SiO₂ and Si₃N₄ Polishing for STI CMP on Blanket and Patterned Wafers," *ECS J. Solid State
  Sci. Technol.* 9, 044008 (2020).** DOI: 10.1149/2162-8777/ab89bc (Crossref 확인). 원문 PDF
  `papers/mariscal2020-jss-sio2-si3n4-sti-kinetic.pdf` 완독. **콜로이달 세리아** 슬러리에서
  막질 의존(HDP vs PETEOS)을 준다 — §6(세리아 vs 실리카) 근거.

배경 링크(값 재사용 아님): Cook 1990(DOI: 10.1016/0022-3093(90)90200-6, 화학 지배),
Netzband & Dunn 2020(DOI: 10.1149/2162-8777/ab8393, 세리아 thermal oxide — [[../cmp/ceria-slurry-ce-redox-selectivity]]).

## 3. Wei 2010 그래프 판독 — 미도핑 5종의 경도·MRR (실리카 슬러리)

Lv1-1이 "그래프라 못 읽음"으로 남긴 Fig.2를 8× 렌더해 판독한 값(단위: 경도 GPa, MRR nm/s).
판독 오차는 눈금 1칸의 ±¼(경도 ±0.2 GPa, MRR ±0.02 nm/s)로 본다.

| 막질 | 경도 H (GPa) | MRR (nm/s) | MRR (nm/min) | TEOS 기준 MRR비 |
|---|---|---|---|---|
| HDP | 7.8 | 1.87 | 112.2 | 0.964 |
| PECVD TEOS | 7.8 | 1.94 | 116.4 | 1.000 |
| SOD | 7.8 | 1.92 | 115.2 | 0.990 |
| Silane oxide | 6.0 | 1.99 | 119.4 | 1.026 |
| O₃-TEOS (HARP) | 4.65 | 2.15 | 129.0 | 1.108 |

**도핑 3종(Fig.2에 미표시, 본문 텍스트값)**: BPSG+reflow 7.78 nm/s, BPSG 7.91 nm/s, PSG 6.77 nm/s
— 미도핑 5종(1.87~2.15 nm/s)의 **약 4배**. Wei 본문: "the magnitude of the increase of their CMP
removal rates is **not attributed to hardness decrease**" → 도핑막 Kp는 경도 항이 아니라 화학 항.

핵심: 미도핑 5종은 **경도-MRR 역상관**(H↓→MRR↑)이지만 그 크기는 약하다 — O₃-TEOS는 경도가
TEOS의 0.60배인데 MRR은 1.11배뿐이다. 순수 1/H 예측(1.68배)과 크게 어긋나며(§7-[A]에서 대조),
실효 지수는 MRR ∝ H^(−0.2) 수준이다. 즉 미도핑막 내부에서 막질이 Kp를 흔드는 폭은 ±10% 정도로 작다.

## 4. Liu 1995 그래프 판독 — thermal oxide 기준 정규화 (실리카 슬러리)

Liu 1995 Fig.2·3은 **wet thermal oxide로 정규화된 polish rate와 hardness**를 준다(4× 렌더 판독).

| 막질 (도핑) | thermal 기준 polish rate | thermal 기준 경도 |
|---|---|---|
| thermal oxide (기준) | 1.00 | 1.00 |
| USG (undoped PECVD, P=0) | 1.35 | 0.62 |
| PSG (3.3 wt% P) | 2.2 | 0.58 |
| PSG (5.6 wt% P) | 2.9 | 0.67 |
| BPSG1 (1.4 wt% B, 5.8 P) | 3.0 | 0.60 |
| BPSG2 (2.8 B, 4.6 P) | 3.5 | 0.63 |
| BPSG3 (4.0 B, 4.6 P) | 3.7 | 0.60 |
| BPSG4 (4.9 B, 3.8 P) | 4.6 | 0.63 |

두 가지가 여기서 확정된다:
1. **미도핑 PECVD 옥사이드(USG)조차 thermal의 1.35배**로 깎인다 — PECVD의 "more open structure"가
   thermal보다 무르고 수화가 쉽기 때문(Liu 본문 §3.2, Cook 인용). 이것이 thermal→PECVD 브릿지 계수다.
2. **경도는 도핑에 거의 무관**(0.58~0.67, thermal의 ~0.6배로 평탄)한데 polish rate는 1.35→4.6으로
   3.4배 벌어진다. Liu 본문: "for doped films, **no distinct relationship** can be drawn [between
   hardness and polish rate]." → 도핑막의 Kp는 경도가 아니라 **화학(수화 확산)**이 정한다. Liu는
   borosilicate glass의 물 확산속도가 vitreous silica보다 **한 자릿수 높다**는 것을 그 근거로 든다
   ([[film-oxide-hydration-layer-mechanism-cook-suratwala]] §4의 Cook fast/slow 확산과 정합).

## 5. 막질별 Kp 배율 제안 표 (thermal oxide = 1) — 이 단원의 산출물

두 실리카 논문을 합친다. **Liu가 thermal=1 절대 앵커**를 주고(USG·PSG·BPSG), **Wei가 미도핑막
내부 세분**(HDP/SOD/Silane/O₃-TEOS)을 준다. 다리는 "Wei의 TEOS ≈ Liu의 USG(둘 다 미도핑 PECVD
옥사이드)"라는 가정(E4, 교차논문·전구체 다름 — SiH₄/O₂ vs TEOS)이며, 이 다리 계수 1.35에만
E4가 붙고 미도핑막 상호비(Wei)와 도핑막비(Liu)는 각각 E3(1차 실측 그래프 판독)이다.

절대 Kp는 현행 `oxide_silica.yaml` 의 **TEOS kp=1.0e-13(verified)을 앵커**로, 상대비를 곱해 스케일한다
(스케일 계수 = 1.0e-13 / 1.35 = 0.74e-13 per unit).

| 막질 | 상대 Kp (thermal=1) | 절대 Kp 제안 (m²/N) | 근거 문헌 | 등급 | confidence 제안 |
|---|---|---|---|---|---|
| thermal oxide | 1.00 | 0.74e-13 | Liu 정규화 기준 | E3 | literature |
| **PECVD TEOS** | **1.35** | **1.0e-13 (=현행 앵커)** | Liu USG=1.35 ≈ Wei TEOS | E4(다리) | literature(값), estimated(다리) |
| HDP | 1.30 | 0.96e-13 | Wei HDP/TEOS=0.964 × 1.35 | E3 | literature |
| SOD | 1.34 | 0.99e-13 | Wei SOD/TEOS=0.990 | E3 | literature |
| Silane oxide | 1.38 | 1.03e-13 | Wei Silane/TEOS=1.026 | E3 | literature |
| O₃-TEOS (HARP) | 1.50 | 1.11e-13 | Wei O₃-TEOS/TEOS=1.108 | E3 | literature |
| PSG (3.3% P) | 2.2 | 1.63e-13 | Liu Fig.2 | E3 | literature |
| PSG (5.6% P) | 2.9 | 2.15e-13 | Liu Fig.2 | E3 | literature |
| BPSG (1.4% B) | 3.0 | 2.22e-13 | Liu Fig.3 | E3 | literature |
| BPSG (4.9% B) | 4.6 | 3.40e-13 | Liu Fig.3 | E3 | literature |

⚠ **절대 Kp 열 전체는 confidence=estimated로 제안한다** — 상대비는 각각 1차 실측이지만, 절대값은
(현행 TEOS 앵커) × (교차논문 다리 1.35) × (그래프 판독 상대비) 세 층의 곱이라 오차가 누적된다.
상대비 열이 이 단원의 신뢰할 수 있는 산출물이고, 절대 열은 "성장엔진이 팩을 나눌 때 쓸 초기값 제안"이다.
⚠ Liu와 Wei는 **슬러리가 다르다**(fumed silica/KOH 7 psi vs colloidal silica 3 psi). Kp는 슬러리에도
의존하므로 두 논문의 절대 MRR은 직접 못 섞는다 — 그래서 **각 논문 안의 비(ratio)만** 가져와 곱했다.
막질 배율이 슬러리에 무관하다는 가정 자체가 근사이며, §6에서 세리아는 이 배율이 다름을 보인다.

## 6. 세리아 vs 실리카 — 막질 의존이 다른가 (Mariscal 2020)

실리카 슬러리에서 HDP는 미도핑 대표 TEOS와 **거의 같다**(§3: HDP/TEOS MRR비 0.964, 경도도 동일 7.8).
그런데 **콜로이달 세리아** 슬러리에서는 다르다:

- Mariscal 2020 블랭킷 PETEOS RR = **2,528 Å/min**(측정값). 같은 논문 본문: "**HDP SiO₂ is known
  to polish at a much slower rate**" than PETEOS, 그 이유로 "the density of HDP SiO₂ could be
  different"을 든다. 패턴 웨이퍼 HDP는 COF가 0.21에서 시작(PETEOS 블랭킷 0.45의 절반)하고 **4.5분이
  지나야 제거가 시작**된다 → 세리아에서 HDP-PETEOS 격차가 실리카보다 훨씬 크다.
- ⚠ 단 Mariscal의 HDP는 **패턴 웨이퍼**, PETEOS는 **블랭킷**이라 순수 막질비가 아니다(패턴·비균일
  ±9%·낮은 입자농도가 섞임 — [[../cmp/sti-cmp-ceria-high-selectivity-nitride-stop-dishing]] §5.2).
  따라서 세리아의 HDP/PETEOS **정량 배수는 확보 못 함**(미검증), 방향(HDP≪PETEOS)만 E3.

**해석**: 세리아는 Si-O-Ce **화학결합(chemical tooth)**으로 실리카를 뜯으므로
([[../cmp/ceria-slurry-ce-redox-selectivity]]), 제거율이 막의 **경도**보다 **표면 화학·밀도(수화·
반응성)**에 더 민감할 개연성이 있다. HDP는 치밀(고밀도)해 세리아 화학 반응이 더 억제되는 반면,
실리카 슬러리의 순수 기계 제거에는 HDP의 높은 경도가 TEOS와 큰 차이를 안 낸다. 즉 **§5의 막질
배율표는 실리카 슬러리 전용이며, 세리아 팩(sti_ceria)에 그대로 이식하면 안 된다** — 세리아는 막질
민감도의 축(경도→밀도·화학)이 다르기 때문이다. 세리아 전용 막질 배수는 정량 데이터가 없어 이
단원에서 넣지 않는다(EVIDENCE-RULES §4: 근거 없는 전이 금지).

## 7. 밀도·경도로 배율이 설명되는가 — 정량 대조

(b) 과제: 막질 MRR비가 밀도비·경도비로 설명되는지. 결론을 먼저: **미도핑막은 경도로 약하게(H^−0.2),
도핑막은 경도로 전혀 설명 안 되고 화학(수화 확산)이 지배**한다. 밀도는 공개 정량값이 없어(Lv1-1에서도
미확보) 정성 대조만 가능하다 — Mariscal이 HDP의 느린 세리아 제거를 "density could be different"로
귀속한 것이 유일한 밀도-제거율 연결 서술이다(정성, E5). §8 verify가 아래를 실제 실행한다.

## 8. 검증 — 원문 수치 재현 (```python verify```, 실제 실행)

**재현 요약(한 줄)**: Wei 2010 TEOS 116.4 nm/min·O₃-TEOS 129.0 nm/min 렌더 판독값을 문헌값으로 재현하고
미도핑 5종 경도-MRR 음의 상관(r<0)·1/H 과대예측 확인, Liu 1995 thermal 기준 배율(USG 1.35배, PSG 2.9배,
BPSG 4.6배)로 절대 Kp 스케일, 도핑/미도핑 4배 격차를 Wei·Liu 양쪽에서 교차 확인, 세리아 PETEOS
252.8 nm/min(=2528 Å/min) 대비 HDP much-slower 방향 — 아래 4블록 assert PASS.

```python verify
import numpy as np
# ── [A] Wei 2010 (DOI 10.1109/wmed.2010.5453755) Fig.2 미도핑 5종 렌더 판독값 ──
films = ["HDP","TEOS","SOD","Silane","O3-TEOS"]
H  = np.array([7.8, 7.8, 7.8, 6.0, 4.65])   # GPa, Fig.2 검은 사각형
RR = np.array([1.87,1.94,1.92,1.99,2.15])   # nm/s, Fig.2 흰 삼각형
# 경도-MRR 역상관(방향): 상관계수 음수
r = np.corrcoef(H, RR)[0,1]
assert r < -0.7, f"경도-MRR 역상관이 약함 r={r:.3f}"
# TEOS 기준 MRR비
RR_min = RR*60.0                              # nm/s → nm/min
assert abs(RR_min[1]-116.4)<0.1 and abs(RR_min[4]-129.0)<0.1   # TEOS 116.4, O3-TEOS 129.0 nm/min
teos = RR[1]
ratio = RR/teos
assert abs(ratio[0]-0.964)<0.005 and abs(ratio[4]-1.108)<0.01   # HDP 0.964, O3-TEOS 1.108
# 1/H(단순 반비례) 모델은 O3-TEOS를 과대예측: 예측 1.68배 vs 실측 1.11배
pred_1overH = H[1]/H[4]                       # = MRR_O3/MRR_TEOS if MRR∝1/H
assert abs(pred_1overH-1.677)<0.01
assert pred_1overH/ratio[4] > 1.5             # 1/H가 실측보다 1.5배 이상 과대
# 실효 멱지수 n: MRR ∝ H^(-n) (O3-TEOS vs TEOS 2점)
n = -np.log(ratio[4])/np.log(H[4]/H[1])
assert 0.15 < n < 0.25, f"실효 지수 n={n:.3f} — 미도핑막 경도 의존은 약함(≈0.2)"
print(f"[A] 경도-MRR r={r:.3f}(음의 상관), 1/H 예측 {pred_1overH:.2f}배 vs 실측 {ratio[4]:.3f}배, MRR∝H^-{n:.2f}")
```

```python verify
# ── [B] Liu 1995 (DOI 10.1016/0040-6090(95)07088-5) Fig.2/3 thermal 기준 배율 ──
# 렌더 판독값(thermal oxide=1)
rel = {"thermal":1.00, "USG":1.35, "PSG_3.3":2.2, "PSG_5.6":2.9,
       "BPSG_1.4":3.0, "BPSG_2.8":3.5, "BPSG_4.0":3.7, "BPSG_4.9":4.6}
hard = {"USG":0.62, "PSG_5.6":0.67, "BPSG_1.4":0.60, "BPSG_4.9":0.63}  # thermal 기준 경도
# (1) 경도는 도핑 무관하게 평탄(0.58~0.67), polish rate는 3배 이상 벌어짐 → 경도로 설명 불가
h = list(hard.values())
assert max(h)-min(h) < 0.10                       # 경도 산포 <0.10 (평탄)
pr_doped = [rel["PSG_5.6"], rel["BPSG_4.9"]]
assert min(pr_doped)/rel["USG"] > 2.0             # 도핑막 polish rate는 USG의 2배 이상
# (2) 절대 Kp 스케일: 현행 TEOS kp=1.0e-13(verified), TEOS≈USG=1.35 다리
kp_teos = 1.0e-13
scale = kp_teos / 1.35                             # per unit (thermal=1)
kp = {k: v*scale for k,v in rel.items()}
assert abs(kp["thermal"]-0.74e-13) < 0.01e-13
assert abs(kp["PSG_5.6"]-2.15e-13) < 0.02e-13
assert abs(kp["BPSG_4.9"]-3.40e-13) < 0.02e-13
# thermal < PECVD 미도핑 < 도핑 순서 불변
assert kp["thermal"] < kp["USG"] < kp["PSG_3.3"] < kp["BPSG_4.9"]
print(f"[B] 경도산포 {max(h)-min(h):.2f}(평탄), 도핑/USG={min(pr_doped)/rel['USG']:.2f}배; "
      f"절대 Kp thermal={kp['thermal']*1e13:.2f} PSG={kp['PSG_5.6']*1e13:.2f} BPSG={kp['BPSG_4.9']*1e13:.2f} (×1e-13)")
```

```python verify
# ── [C] 도핑/미도핑 4배 격차 — Wei·Liu 교차 확인 ──
# Wei(colloidal silica, nm/s): 도핑 3종 vs 미도핑 5종
wei_doped   = [7.78, 7.91, 6.77]        # BPSG+reflow, BPSG, PSG
wei_undoped = [1.87, 1.94, 1.92, 1.99, 2.15]
mean_ratio = (sum(wei_doped)/len(wei_doped)) / (sum(wei_undoped)/len(wei_undoped))
assert 3.5 < mean_ratio < 4.2, f"Wei 도핑/미도핑 비 {mean_ratio:.2f}"
# Liu(fumed silica/KOH, thermal 정규화): 도핑 PSG/BPSG vs 미도핑 USG
liu_doped   = [2.9, 4.6]                 # PSG_5.6, BPSG_4.9
liu_undoped = 1.35                       # USG
liu_ratio_hi = max(liu_doped)/liu_undoped
# 두 논문은 슬러리가 달라 절대비는 다르지만, "도핑막이 미도핑막보다 크게 빠르다"는 방향 일치
assert mean_ratio > 3.0 and liu_ratio_hi > 3.0   # 양쪽 다 3배 이상
# ⚠ 크기 차이(Wei 4배 vs Liu 3.4배)는 슬러리·도핑수준 차이 — 방향만 교차 확인, 평균 안 냄
print(f"[C] 도핑/미도핑: Wei={mean_ratio:.2f}배(colloidal), Liu 상한={liu_ratio_hi:.2f}배(fumed/KOH) — 방향 일치")
```

```python verify
# ── [D] 세리아 vs 실리카 막질 의존 (Mariscal 2020, DOI 10.1149/2162-8777/ab89bc) ──
# 실리카 슬러리: HDP ≈ TEOS (Wei)
silica_hdp_teos = 1.87/1.94
assert abs(silica_hdp_teos-0.964) < 0.005      # HDP는 TEOS의 96% — 거의 같음
# 세리아 슬러리: PETEOS 블랭킷 2528 Å/min, HDP "much slower"(정량 배수는 미확보)
peteos_ceria = 2528.0                            # Å/min, Mariscal 측정값
assert abs(peteos_ceria/10.0 - 252.8) < 0.1      # = 252.8 nm/min
# COF로 본 격차: HDP 패턴 시작 0.21 vs PETEOS 블랭킷 0.45 → 세리아에서 HDP-PETEOS 큰 격차
cof_hdp, cof_peteos = 0.21, 0.45
assert cof_hdp/cof_peteos < 0.5                  # 세리아 HDP COF는 PETEOS의 절반 이하
# 결론: 실리카는 HDP≈TEOS(0.96), 세리아는 HDP≪PETEOS → 막질 민감도의 축이 다름
assert silica_hdp_teos > 0.9 and cof_hdp/cof_peteos < 0.5
print(f"[D] 실리카 HDP/TEOS={silica_hdp_teos:.3f}(거의 같음) vs 세리아 HDP COF/PETEOS={cof_hdp/cof_peteos:.2f}(절반이하) "
      f"— 세리아 막질 의존은 실리카와 다름(경도→밀도/화학 축 전환), PETEOS={peteos_ceria:.0f} Å/min")
```

**결과 해석(정직하게)**
- [A]는 Wei Fig.2를 8× 렌더 판독한 값의 재현이다. 경도-MRR 역상관은 방향은 확실하나 크기는 약해
  (MRR∝H^−0.2), "경도가 곧 Kp"라는 단순 모델은 미도핑막에서도 부분적으로만 맞는다.
- [B]의 절대 Kp는 TEOS≈USG 다리(E4)에 의존한다 — SiH₄/O₂ 계 USG와 TEOS 전구체가 실제로 같은
  Kp인지는 직접 확인 못 했다(미검증). 상대비 열이 신뢰 산출물이고 절대 열은 제안값이다.
- [C]는 슬러리가 다른 두 논문의 **비만** 비교한 것이다. 절대비 크기(4 vs 3.4)는 평균 내지 않았다
  (EVIDENCE-RULES: 상반 아닌 방향 일치는 교차 확인으로만).
- [D]의 세리아 HDP는 패턴/블랭킷 교란이 섞여 정량 배수가 아니다. COF 비(0.47)는 tribology 대리
  지표일 뿐 제거율 배수가 아니다 — 방향 근거로만 쓴다.

## 9. (d) 옥사이드:정지층 선택비의 슬러리·막질 의존 — 옥사이드 관점만

선택비 = oxide RR / (nitride 또는 poly RR). 나이트라이드·폴리의 억제 메커니즘·절대값은 형제
에이전트(film-nitride·film-poly-si) 영역이며 세리아 선택비 수치는 이미
[[../cmp/sti-cmp-ceria-high-selectivity-nitride-stop-dishing]]에 완결돼 있어 **재서술하지 않는다.**
이 단원이 더하는 것은 **분자(oxide RR)가 막질로 갈리면 선택비도 갈린다**는 옥사이드 쪽 관점 하나다:

- **실리카 슬러리**: 도핑막(BPSG/PSG)은 미도핑 대비 oxide RR이 ~4배(§3,§8-C)이므로, nitride RR이
  같다면 oxide:nitride 선택비도 도핑막에서 ~4배 커진다. 단 실리카는 nitride도 상당히 깎아
  STI 정지에는 부적합(그래서 STI는 세리아를 쓴다).
- **세리아 슬러리**: 같은 슬러리라도 옥사이드 막질이 TEOS냐 HDP냐로 oxide RR이 갈린다(§6, HDP≪
  PETEOS). 세리아에서 nitride RR은 억제제로 <1 nm/min로 고정되므로(형제 노트), 선택비의 변동은
  대부분 **분모(nitride)가 아니라 분자(oxide 막질)에서 온다** — HDP 오버버든을 쓰는 실제 STI에서
  선택비가 블랭킷 PETEOS 측정치보다 낮게 나오는 이유의 일부다(Mariscal의 순진한 예측 2.4분 vs
  실측 6분과 정합, §6).
- **BPSG:정지층(SRO)** ≈ 3:1 (Liu 1995 §3.1, 실리카 슬러리, silicon-rich oxide 정지층) — 옥사이드
  대 옥사이드계 정지층 선택비의 1차 수치. nitride 정지와는 다른 계라 참고값(E3).

## 10. 옥사이드 전문가 관점 결론

1. **막질별 Kp 배율표(§5)는 실리카 슬러리 전용**이다. thermal=1 기준으로 미도핑막은 1.3~1.5(경도로
   약하게 갈림, ±10%), 도핑막은 2.2~4.6(화학=수화 확산이 지배). 이 배율은 상대비가 신뢰 산출물이고
   절대 Kp는 estimated 제안이다.
2. **도핑이 미도핑보다 큰 1차 분기**다 — Lv1-1 §9-1의 정성 결론을 Wei·Liu 두 논문의 배수(3.4~4배)로
   수치화했다. 경도가 아니라 borosilicate의 빠른 물 확산(Cook fast/slow, Lv1-2)이 원인.
3. **세리아는 배율표를 물려받으면 안 된다**(§6) — 막질 민감도의 축이 경도(실리카)에서 밀도·화학
   (세리아)으로 바뀐다. 세리아 전용 막질 배수는 정량 데이터 부재로 미제출(성장엔진에 넘김).
4. **선택비의 막질 의존은 분자(oxide RR)에서 온다**(§9) — sim이 STI 선택비를 막질(HDP 오버버든)로
   보정할 때 이 노트가 근거다.

## 11. 구현 요청 → agents/film-oxide/PROFILE.md "## 구현 요청" 참조
(oxide_silica 팩의 kp_m_per_pa를 oxide_type 룩업으로 분화: §5 상대비표. sti_ceria엔 적용 금지 §6.)

## 12. 자기시험
→ [[../../agents/film-oxide/EXAMS.md]] Lv3-2 문항 참조.
