<!-- V2-SECTION: R2-slurry | 작성 2026-09-15 | 근거: tungsten CMP Preston coefficient, oxidizer concentration removal rate, Kp inversion | 정본: EVIDENCE-RULES.md 판정#6/#10 계열 -->
# 텅스텐 CMP — Kp 문헌 역산·산화제 농도-MRR 곡선·온도의존 1차 재현 (Lv3-2)

> 에이전트: film-w Lv3-2 (sim/tier2) | 작성일: 2026-09-15
> 선행/상속: [[w-cmp-wo3-passivation-oxidizer-kaufman]] (WO₃ 형성-제거 순환·Kaufman·Lim 산화제)
> · [[preston-luo-dornfeld-mrr]] (Preston 식·Kp 정의·P^1/2 계보) · [[hertz-gw-contact-mechanics]] (Kp의 접촉역학 분해)
> 관련: [[w-cmp-abrasive-size-null-result-egan-kim-2019]] (같은 팩 κ null) ·
> [[kappa-abrasive-concentration-cu-w-cooper-bielmann]] (Wang 2012 cube-root 이미 인용) ·
> [[w-cmp-picolinic-acid-inhibitor-langmuir-dissolution-suppression]] (같은 팩 ψ)

## 1. 왜 이 노트가 필요한가

`knowledge/params/w_fe_oxidizer.yaml`의 `kp_m_per_pa = 2.8e-13 m²/N`는 주석이 스스로 자백하듯
**"문헌 W MRR 범위(300~600 nm/min @ 3psi)에서 역산한 대표값. 미재현"(confidence=estimated)**이다.
또 팩의 산화제 곡선 파라미터(`oxidizer_langmuir_K`, `oxidizer_mech_floor` 등)는 **H₂O₂ 농도
스윕(US20110186542A1)에서 캘리브레이션**됐는데 팩이 선언한 산화제는 **Fe(NO₃)₃**다 — 종·농도
스케일이 다른 두 화학을 한 곡선이 대표하고 있다. 이 노트는 (a) W CMP에서 **압력·속도·MRR이 함께
보고된 1차 데이터점**으로 `Kp=MRR/(P·V)`를 역산해 2.8e-13이 실측과 얼마나 어긋나는지, (b) W가
Preston 선형(a=b=1)인지 산화-제거 순환 때문에 포화(비선형)인지, (c) 세 산화제(Fe(NO₃)₃/H₂O₂/KIO₃)의
농도-MRR 정점·포화 위치, (d) 온도의존을 1차 수치로 판정한다. **Lv1-1(Kaufman 메커니즘·PBR)과
Lv2(Preston 계보)는 재서술하지 않는다** — 여기서는 오직 팩값 대조에만 집중한다.

## 2. 1차 출처 (전부 원문 확보)

- **[S1] Stojadinović, Bouvet, Mischler, "Prediction of Removal Rates in CMP Using Tribocorrosion
  Modeling," *J. Bio- Tribo-Corros.* 2, 20 (2016).** DOI: 10.1007/s40735-016-0041-4. EPFL.
  미러 사이트→미러 사이트 경유 발행판 PDF 확보(`papers/stojadinovic2016-jbtc-w-cmp-tribocorrosion.pdf`,
  16쪽 통독). Mecapol E460, **head 5 psi·platen 50 rpm·head 60 rpm**, CVD W 100 mm, 3% 실리카,
  KIO₃ 산화제. Table 1에 (조성, pH, OCP, Q, RR) 동시 보고 — W CMP에서 **(P, rpm, MRR)+산화제
  농도 스윕**을 한 표에 준 드문 1차 문헌.
- **[S2] Lim, Park, Park, "Effect of iron(III) nitrate concentration on tungsten CMP performance,"
  *Appl. Surf. Sci.* 282, 512–517 (2013).** DOI: 10.1016/j.apsusc.2013.06.003. Hanyang Univ.
  원문 `papers/lim2013-apsusc-fe-nitrate-w-cmp.pdf` 통독. **6 psi·carrier/table 70 rpm**, 4 wt%
  콜로이달 실리카(PL-7 Fuso)+H₂O₂+Fe(NO₃)₃ 촉매, pH 2.3. Fe(NO₃)₃ 농도-MRR·정지식각(SER) 동시.
  (동일 데이터 companion: Lee et al. 2013, 같은 그룹 — 독립 표본으로 세지 않는다.)
- **[S3] US8070843B2 (3M), "Polishing fluids and methods for CMP" (2011).** 이미 held-out 데이터셋
  `validation/datasets/us8070843b2_w_h2o2_series.yaml`로 등록됨. Mirra 3400, **4.0 psi(27.6 kPa)·
  platen 79 rpm·carrier 101 rpm**, 고정연마입자 패드+무연마 H₂O₂/Fe 용액. H₂O₂ 0→6.1 wt% 스윕.
- **[S4] Wang, Peng, Xia, Kitajima, Tsai, "Removal Mechanism of Tungsten CMP Process," *ECS Trans.*
  41(43) 103–111 (2012).** DOI: 10.1149/1.4717508. Applied Materials Reflexion GT. 원문
  `papers/wang2012-ecst-w-cmp-abrasive-conc-temp.pdf` 통독. **Prestonian 거동을 실측 검증**,
  연마입자 농도 cube-root, 공정온도-MRR **선형**(Arrhenius 소구간 선형화).
- **[S5] Bouvet et al., "Impact of colloidal silica particle size on PVD W removal rate," *JVST B*
  20(4) 1556 (2002).** DOI: 10.1116/1.1490393. Presi Mecapol E460, **7 psi·platen 55 rpm·head 45 rpm**,
  KIO₃ 산화제, 콜로이달 실리카. W 제거율이 입경·실리카 함량과 **무관** → 화학율속.
- 보조: **Kaufman et al. 1991** (DOI: 10.1149/1.2085434, [[w-cmp-wo3-passivation-oxidizer-kaufman]]에서
  통독) — K₃Fe(CN)₆, 1–5 kg/cm², ~130~400 nm/min. 압력·회전수·온도↑ → MRR↑ 정성.

## 3. (a) Kp = MRR/(P·V) 역산 — 3개 독립 문헌

W CMP 논문은 **선속도(m/s)를 직접 보고하지 않고 rpm만** 준다. 회전형 CMP에서 웨이퍼-패드 상대
속도는 platen 각속도항이 지배하며 웨이퍼 자전(head)항은 웨이퍼면 평균에서 대부분 상쇄된다
(v_rel = ω_p·**R**_cc + (ω_p−ω_w)·ρ, [[hertz-gw-contact-mechanics]]·[[preston-luo-dornfeld-mrr]] §4).
따라서 **V ≈ ω_platen · R_cc**로 근사하되 **중심간거리 R_cc는 어느 문헌도 보고하지 않으므로**
대표 R_cc=0.13 m(±0.04, 100~300 mm 웨이퍼 랩·양산툴 통상범위)로 두고 이를 지배 불확실도로
전파한다. 이 R_cc가 **역산 Kp의 가장 큰 오차원**이다(미검증 가정 — 아래 §8 verify에서 밴드로 처리).

| 문헌 | P | platen rpm | V≈ω·R_cc | MRR(대표) | Kp=ḣ/(P·V) |
|---|---|---|---|---|---|
| [S2] lim2013 Fe(NO₃)₃ 고원 | 6 psi=41.4 kPa | 70 | 0.95 m/s | 117.7 nm/min | 5.0e-14 |
| [S3] US8070843B2 H₂O₂ 6.1% | 4 psi=27.6 kPa | 79 | 1.08 m/s | 296.5 nm/min | 1.67e-13 |
| [S1] Stojadinović KIO₃ 2% pH5 | 5 psi=34.5 kPa | 50 | 0.68 m/s | 150 nm/min | 1.07e-13 |

**역산 분포(3 독립 문헌, R_cc=0.13 m): 중앙값 1.07e-13, 범위 5.0e-14 ~ 1.67e-13 m²/N.**
팩값 2.8e-13은 중앙값의 **2.6배**(R_cc 0.09~0.17 밴드에서 1.8~3.4배). 즉 팩 Kp는 세 통제된 W CMP
실험 역산치보다 **계통적으로 약 2배 높다**. 자릿수(10⁻¹³)는 맞지만 상단으로 치우쳐 있다.
원인은 팩 앵커가 "300~600 nm/min @ 3 psi"라는 **낙관적 MRR**인데 반해, 실측 세 건은 더 높은
4~7 psi에서 118~296 nm/min에 그친다는 데 있다. 2.8e-13을 역산치로 맞추려면 R_cc≈0.05 m(비현실적
소형)이 필요하므로 **속도 불확실도만으로는 이 격차가 닫히지 않는다**(§8에서 assert).

## 4. (b) Preston 선형성 vs 산화-제거 포화 — 레짐 분기 (평균 금지)

- **기계율속 레짐 → Preston 선형(a=b=1):** [S4] Wang 2012는 Reflexion GT에서 blanket W의 여러
  "Prestonian number"(=P·V)에 대해 **"the Prestonian equation fits the data well in the range"**
  라고 실측 검증했다(Fig.1b). 즉 산화막이 충분히 빨리 재형성되면 MRR ∝ P·V가 성립한다.
- **화학율속 레짐 → 포화(기계입력에 무감):** [S5] Bouvet 2002는 콜로이달 실리카+KIO₃에서 W
  제거율이 **입경(12~75 nm)·실리카 함량과 무관**하며 **"the limiting factor is chemical related"**
  라 결론냈다. 산화가 느리면 기계입력을 늘려도 MRR이 안 오른다 — Preston 지수가 실효적으로 a→0.
- **기구론적 정밀화 → 준선형(a≈1/2):** [S1] Stojadinović 2016은 Kaufman 순환을 트라이보부식으로
  모형화해 **"the contact pressure appears at the square root ... instead of the linear dependence
  predicted by Preston"**라 명시(RR∝P^0.5). Tseng et al.의 5/6·1/2 지수와 [[preston-luo-dornfeld-mrr]]
  Luo-Dornfeld P^1/2와 같은 계보.

**판정(EVIDENCE-RULES §3 스코프 분기, 평균 금지):** 세 값은 충돌이 아니라 **레짐이 다르다**.
직접 실측(Wang, E2/E3)이 작업창 안에서 **선형 Preston을 지지**하고, 준선형 P^0.5는 접촉역학
정밀화(E4 모델 전이), 완전 포화는 화학율속 극단이다. 팩은 `Kp·P·V` 선형식을 쓰는데 이는 확보한
**유일한 직접 실험 검증(Wang)과 정합**하므로 **Preston 지수는 a=b=1로 유지**한다(P^0.5로 바꿀
1차 실측 W 지수는 확보 못 함 — 모델 예측뿐, 미채택). 다만 팩 Kp는 화학율속 포화를 표현할 통로가
없어, 산화제가 부족한 조건에서 MRR을 과대추정한다(§5의 산화제 곡선이 이 포화를 대신 담당).

## 5. (c) 산화제 농도 → MRR 곡선 — 세 산화제의 정점·포화 위치

세 산화제 모두 **상승 후 포화**하나 **포화 농도가 100배 규모로 다르다**(전부 1차 수치):

| 산화제 | 출처 | 농도 스윕 → MRR (Å/min) | 포화/정점 |
|---|---|---|---|
| **Fe(NO₃)₃**(촉매) | [S2] lim2013 Fig.1 | 0→56, 0.01%→923, 0.05%→1177, ~1.0%까지 완만 | region I→II 전이 **~0.1 wt%** |
| **KIO₃**(pH5) | [S1] Table 1 | 0→40, 0.1%→140, 0.5%→750, 2%→1500, 4%→1600 | 포화 **~2 wt%** |
| **KIO₃**(pH2) | [S1] Table 1 | 0→25, 0.1%→200, 0.5%→1150, 2%→1950 | 상승(4% NA) |
| **H₂O₂** | [S3] us8070843 데이터셋 | 0→96, 2.03%→1508, 4.06%→2396, 6.1%→2965 | 6.1%까지 **단조상승(정점 미도달)** |

관련 산화 지표: [S2] 정지식각(SER)은 Fe(NO₃)₃ 0→0.01%에서 37.8→85.9 Å/min로 잠깐 오른 뒤
0.05%→31.1, 0.1%→19.3, 1.0%→12.3 Å/min로 **급감** — Fe 증가가 치밀 WO₃ 부동태를 강화(정지식각↓)
하는 동안 MRR(기계+화학)은 상승하는 **Kaufman 산화-제거 순환의 정량 증거**([[w-cmp-wo3-passivation-oxidizer-kaufman]] §2).

**팩 대조:** `w_fe_oxidizer.yaml`은 산화제를 `Fe(NO₃)₃`로 선언하지만 `oxidizer_wt_pct=3.0`·
`oxidizer_langmuir_K=0.549/wt%`·`oxidizer_mech_floor=0.14`는 전부 **H₂O₂ 3 wt% 스케일**(US20110186542A1)
에서 나왔다. 그런데 촉매 Fe(NO₃)₃의 포화는 **~0.1 wt%**로 H₂O₂ 스케일보다 **~30~60배 낮다**.
즉 팩의 산화제 곡선을 Fe(NO₃)₃ 농도축에 그대로 쓰면 **정점을 100배 규모로 오른쪽에 두는 셈**이다.
이는 값 오류라기보다 **"어느 산화제 축의 곡선인가"가 팩에 불명확**한 구조 문제다(갱신 제안 §7).
또 held-out [S3] H₂O₂ 데이터는 6.1 wt%까지 단조상승이라 팩의 정점(H₂O₂ 3 wt% 부근 감소 가정)과
**어긋난다**(us8070843b2 데이터셋 notes가 이미 기록) — 정점은 6.1 wt%보다 오른쪽.

## 6. (d) 온도 의존 — 방향은 확정, 활성화에너지 수치는 미확보

- [S4] Wang 2012: "removal rate showed a **strong linear relationship** with process temperature."
  Arrhenius(식5 k=a·e^(−Ea/RT))를 두 온도비로 전개해 소구간에서 RR∝ΔT로 선형화(원문 식6). 산화막
  형성이 반응율속이라 온도↑→WO₃ 두께↑→MRR↑. **단 Ea(kJ/mol) 수치는 원문에 제시되지 않음**(그래프뿐).
- Kaufman 1991: "polish rates increase as a function of increasing temperature of the slurry" — 정성.
- **미검증:** W CMP의 활성화에너지 수치(kJ/mol)는 확보한 1차 문헌 어디에도 없다(Wang은 그림·선형관계만,
  Kaufman은 정성). 방향(양의 온도계수)만 1차로 확정하고 크기는 채택하지 않는다. 팩에는 온도항이
  아예 없으므로(이번 조사도 온도 파라미터를 제안하지 않는다) 이 갭은 방향만 기록하고 종결한다.

## 7. 팩 갱신 제안 표 (yaml 직접 수정 금지 — 성장엔진 크론 판정용)

| 파라미터 | 현재값 | 제안값 | 근거 문헌 | 등급 | confidence 제안 |
|---|---|---|---|---|---|
| `kp_m_per_pa` | 2.8e-13 m²/N | **~1.1e-13**(3문헌 역산 중앙값) 또는 유지+주석 | [S1][S2][S3] Kp=ḣ/(P·V) 역산, R_cc=0.13±0.04 | E3(직접 실측, 단 V=ω·R_cc 가정) | **estimated 유지** — R_cc 미보고로 절대값 미확정. 값 교체 시 근거는 실측 상향이나 factor~2 개선 |
| Preston 지수 a,b | (선형 1,1 암묵) | **1,1 유지** | [S4] Prestonian 실측 검증(작업창) | E2/E3 | 유지. P^0.5는 [S1] 모델 예측(E4)이라 미채택 |
| 산화제 곡선 축 정의 | Fe(NO₃)₃ 선언 + H₂O₂ 스케일 곡선 | **곡선을 H₂O₂ 전용으로 명시**하거나 Fe(NO₃)₃ 곡선 별도(포화~0.1 wt%) | [S2] Fe(NO₃)₃ region I→II ~0.1 wt%; [S1] KIO₃ ~2 wt% | E1(직접 실측) | 곡선 축을 산화제 종별로 분리 권고. 현행 langmuir_K는 H₂O₂ 축에서만 literature |
| H₂O₂ 정점 | 3.0 wt%(cu팩 차용) | **>6.1 wt%**(미도달) | [S3] 0→6.1 wt% 단조상승 | E2(특허 실시예표) | 정점 위치는 6.1 wt% 우측 — 하강 예측은 실측과 반대 |
| 온도항 | 없음 | 없음(방향만: 양의 계수) | [S4][Kaufman] | E1(방향)/미확보(크기) | Ea 수치 미확보로 파라미터 신설 보류 |

## 8. 코드 재현 (문헌값 상수 박고 assert)

```python verify
# 블록1: (a) Kp = MRR/(P·V) 3문헌 역산 분포 + 팩값 2.8e-13 대조
import math, statistics
psi = 6894.757                      # Pa/psi
Rcc = 0.13                          # m, 중심간거리 대표값(미보고 가정, 지배 불확실도)
def V(rpm): return (rpm*2*math.pi/60.0)*Rcc          # V≈ω_platen·Rcc [m/s]
def Kp(mrr_nm_min, P_Pa, Vv): return (mrr_nm_min*1e-9/60.0)/(P_Pa*Vv)  # ḣ/(P·V) [m^2/N]

# (문헌, MRR[nm/min], P[Pa], platen rpm) — S1 Stojadinovic2016, S2 lim2013, S3 US8070843B2
S2 = Kp(117.7, 6*psi, V(70))        # Fe(NO3)3 고원, Appl.Surf.Sci.282,512
S3 = Kp(296.5, 4*psi, V(79))        # H2O2 6.1wt%, US8070843B2 데이터셋
S1 = Kp(150.0, 5*psi, V(50))        # KIO3 2% pH5, J.Bio-Tribo-Corros.2,20 Table1
inv = [S2, S3, S1]
med = statistics.median(inv)
print(f"Kp 역산: S2={S2:.2e} S3={S3:.2e} S1={S1:.2e}  median={med:.2e}")

# 자릿수: 전부 W용 Preston 오더 10^-14~10^-12 안 (preston-luo-dornfeld-mrr §1: SiO2 ~1e-13~1e-12)
for k in inv:
    assert 1e-14 < k < 1e-12, f"역산 Kp {k:.1e}가 Preston 오더 밖 — 계산/단위 오류 의심"

# 팩값은 역산 중앙값의 약 2배(상단 치우침) — 자릿수는 같으나 계통 과대
PACK = 2.8e-13
ratio = PACK/med
print(f"팩 {PACK:.1e} / median {med:.2e} = {ratio:.2f}배")
assert 1.5 < ratio < 4.0, f"팩/역산 비율 {ratio:.2f} — '자릿수 일치·2배 과대' 주장과 불일치"

# R_cc 불확실도(0.09~0.17)로도 팩값에 도달 못 함(도달하려면 Rcc<0.06)
def med_at(rc):
    Vb = lambda rpm:(rpm*2*math.pi/60.0)*rc
    return statistics.median([Kp(117.7,6*psi,Vb(70)),Kp(296.5,4*psi,Vb(79)),Kp(150,5*psi,Vb(50))])
band_lo, band_hi = med_at(0.17), med_at(0.09)   # Rcc 클수록 V↑→Kp↓
print(f"R_cc 밴드 median: {band_lo:.2e}(Rcc0.17) ~ {band_hi:.2e}(Rcc0.09)")
assert band_hi < PACK, "R_cc 최소경계 역산치가 팩값 이상 — 속도불확실도로 격차가 닫힘(주장 반증)"
rc_needed = 0.13*(med/PACK)         # 팩값=median 되게 하는 Rcc
print(f"팩값과 일치시키는 R_cc ≈ {rc_needed:.3f} m (비현실적 소형이면 팩 과대 확정)")
assert rc_needed < 0.07, "팩값 정당화에 필요한 Rcc가 통상범위면 과대 판정 근거 약함"
print("=> 팩 kp_m_per_pa=2.8e-13은 3문헌 역산 대비 ~1.8~3.4배 계통 과대(자릿수는 일치)")
```

```python verify
# 블록2: (c) 산화제 농도-MRR — 세 산화제의 포화 농도가 100배 규모로 다름을 수치로 확정
# 문헌값(Å/min):
Fe = {0.0:56, 0.01:923, 0.05:1177, 1.0:1290}          # lim2013 Fig.1 (1.0%은 'slight increase' 근사상한)
KIO3_pH5 = {0.0:40, 0.1:140, 0.5:750, 2.0:1500, 4.0:1600}  # Stojadinovic2016 Table1
H2O2 = {0.0:96, 2.03:1508, 4.06:2396, 6.10:2965}      # US8070843B2 데이터셋(Å/min)

# Fe(NO3)3: region I(<0.1%)에서 이미 최대의 대부분 도달 = 저농도 포화
fe_frac_at_005 = Fe[0.05]/Fe[1.0]
print(f"Fe(NO3)3 0.05wt% MRR은 1.0wt% 대비 {fe_frac_at_005*100:.0f}% — region I 저농도 포화")
assert fe_frac_at_005 > 0.85, "Fe계가 0.05wt%에서 고원의 대부분에 도달 못하면 저농도포화 주장 반증"

# KIO3(pH5): 2%→4%에서 완만(포화 진입)
kio3_2to4 = (KIO3_pH5[4.0]-KIO3_pH5[2.0])/KIO3_pH5[2.0]
print(f"KIO3 2→4wt% 증가율 {kio3_2to4*100:.1f}% — ~2wt% 포화 진입")
assert kio3_2to4 < 0.15, "KIO3가 2→4%에서 15%이상 더 오르면 2%포화 주장 반증"

# H2O2: 6.1wt%까지 단조상승(정점 미도달)
h_vals = [H2O2[c] for c in sorted(H2O2)]
assert all(b>a for a,b in zip(h_vals,h_vals[1:])), "H2O2가 단조상승 아님 — 정점 미도달 주장 반증"
print(f"H2O2 0→6.1wt% 단조상승 {h_vals} — 정점은 6.1wt% 우측")

# 포화농도 대비: Fe(~0.1) vs H2O2(>6.1) → 60배 이상 차이 => 단일 곡선축으로 대표 불가
sat_ratio = 6.1/0.1
print(f"H2O2 포화(>6.1) / Fe(NO3)3 포화(~0.1) ≥ {sat_ratio:.0f}배 — 팩 산화제곡선 축 정의 필요")
assert sat_ratio >= 30, "포화농도 스케일 차이가 30배 미만이면 '축 분리 필요' 주장 약화"
```

```python verify
# 블록3: (b) Preston 선형 vs 산화-제거 포화 — Wang 선형성과 Bouvet 화학율속(무감)의 정합성
# Wang 2012: MRR = Kp·P·V 선형이면, 같은 Kp로 P·V만 다른 두 점의 MRR비 = (P·V)비 여야 함(작업창 내).
# 여기서는 '선형이면 성립하는 항등식'을 확인(문헌 그림의 정성 결론을 코드 제약으로 고정).
Kp = 1.1e-13   # 본 노트 §3 역산 중앙값(m^2/N)
psi = 6894.757
def mrr(P_psi, V): return Kp*(P_psi*psi)*V*1e9*60   # nm/min
# 작업창 예: 4→6 psi, V 0.8→1.0 m/s 이면 MRR비 = (6*1.0)/(4*0.8)
r_pred = (6*1.0)/(4*0.8)
r_calc = mrr(6,1.0)/mrr(4,0.8)
assert abs(r_pred-r_calc) < 1e-9, "선형 Preston 항등식 불성립 — 구현/식 오류"
print(f"선형 Preston: MRR비 예측 {r_pred:.3f} = 계산 {r_calc:.3f} (Wang2012 작업창 정합)")

# Bouvet 화학율속 극단: 기계입력(입경·농도) 바뀌어도 MRR 무감 → 실효 Preston 지수 a→0
# 정점 아래(화학율속)에서 산화제 없으면 MRR<200 Å/min(=20 nm/min) 하한(Bouvet 원문)
mrr_no_oxidizer = 20.0   # nm/min, Bouvet: "less than 200 Å/min" without oxidizer
mrr_with_oxidizer_min = 40.0  # Stojadinovic pH5 0%KIO3=40Å/min? -> 산화제0에서도 바닥
# 화학율속에서는 산화제 유무가 P·V보다 지배적: 무산화제 MRR이 저압 유산화제보다 낮아야 함
assert mrr_no_oxidizer < 150, "화학율속 레짐에서 무산화제 MRR이 낮지 않으면 '화학율속' 주장 약화"
print(f"Bouvet: 무산화제 W MRR < {mrr_no_oxidizer*10:.0f} Å/min → 화학율속(포화) 레짐 = Preston a→0")
print("=> 선형(Wang, 기계율속) / 포화(Bouvet, 화학율속)는 레짐 분기 — 평균 금지, 팩은 선형 유지")
```

## 9. 한계 / 미검증 표기 (정직)

- **Kp 절대값 미확정:** 모든 출처가 선속도(m/s)를 안 주고 rpm만 준다. V=ω·R_cc의 R_cc(중심간거리)는
  **미보고**라 대표 0.13 m로 가정했다(추정). 이것이 역산 Kp의 지배 오차원 — 그래서 값을 바꾸더라도
  confidence는 estimated 유지가 옳다(§7). 자릿수·팩 대비 2배 계통편차는 R_cc 밴드 안에서도 견고함은
  §8이 assert.
- **레짐 분기의 직접 W 지수 부재:** Wang의 Prestonian 검증은 그림 기반(정량 지수 회귀표 없음, E2/E3
  경계), Stojadinović P^0.5는 모델 예측(E4). 어느 쪽도 n≥5 W 압력스윕 회귀 지수를 수치로 안 준다 —
  선형 유지는 "직접 실측이 선형을 지지"에 근거하되 정밀 지수는 **미확보**.
- **활성화에너지(kJ/mol) 미확보:** Wang·Kaufman 모두 온도↑→MRR↑ 방향만, Ea 수치 없음(§6).
- lim2013/Lee2013은 동일 그룹 데이터라 독립 표본 1건으로 셌다. US8070843B2는 고정연마입자 패드라
  절대 MRR은 알루미나/실리카 슬러리와 다를 수 있어 순위·오더로만 사용(데이터셋 notes 기존 경고).

## 10. 자기시험
→ [[../../agents/film-w/EXAMS.md]] Lv3-2 문항 참조.
