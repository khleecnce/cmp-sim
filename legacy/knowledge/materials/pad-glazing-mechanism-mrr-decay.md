<!-- V2-SECTION: R4-disk | 공동: R2-slurry | 분배완료 2026-09-08 | 근거: asperity-regeneration, breakin, conditioning | 정본: ARCHITECTURE-V2.md §3 -->
# 패드 Glazing 메커니즘: asperity 소성변형·슬러리 잔류물 축적·MRR 감소

> pad-lifecycle Lv2-1 | 작성일: 2026-09-07
> [[pad-wear-glazing-mrr-decay]] [[conditioning-mechanism-asperity-regeneration]]
> [[pad-conditioning-wear-regeneration-balance]] [[pad-breakin-asperity-mrr-runup]]
> [[hertz-gw-contact-mechanics]] [[gw-nominal-vs-local-pressure]] 상호링크.
> 부모 노트 [[pad-wear-glazing-mrr-decay]]는 glazing을 "asperity 마모·평탄화 → MRR 감소"로
> 정의하고 Shi&Ring(2010) population balance로 모델링했다. 이 노트는 그 정의를 **세 가지 물리
> 구성요소(소성변형·기공 막힘·잔류물 응착)로 분해**하고, 컨디셔닝 없이 방치했을 때
> asperity 밀도·반경·높이편차·MRR이 **얼마나** 변하는지 1차 출처 실측값으로 정량화한다.

## 1. Glazing의 물리적 정의 — 세 구성요소

문헌마다 glazing의 강조점이 다르다. 1차 확보한 출처별로 정리하면:

| 구성요소 | 서술 | 출처(확보 수준) |
|---|---|---|
| (a) asperity 끝의 마모·소성 평탄화 | 웨이퍼와의 상대회전 마찰로 키 큰 asperity가 먼저 깎이고(높이편차 σz 감소), 압축이 겹쳐 접촉 asperity의 **등가반경이 커진다** — "resulting in a smoother surface" | Jeong et al. 2024 §3.1 (전문 확보·직접 읽음) |
| (a') 높이분포의 truncation | 컨디셔닝 없이 다수 웨이퍼를 연마하면 asperity tip이 절단된 "wafer dominated" 표면 — 높이분포에 2차 피크 성장 | Lawing 2004 (공개 PDF 확보, [[conditioning-mechanism-asperity-regeneration]] §1과 동일 자료) |
| (b) 기공 막힘 | "Glazing occurs when the pores of the pad become clogged with abrasive particles from the slurry. This phenomenon prevents uniform transport of the slurry across the wafer." | Moon 1999 박사논문 p.42-43 (UC Berkeley, 공개 PDF 확보·직접 읽음) |
| (c) 잔류물/부산물 응착층 | "pad becomes flattened or glazed with particles clogging the pores ... forming a layer of slurry residue and wafer particles" / "surface undergoes plastic deformation so that the surface becomes smoother and the pores fill with the pad materials" | McGrath & Davis 2004 (**초록 스니펫 수준만 확인**, 본문 미확보 — 2차 인용) |

즉 glazing은 단일 현상이 아니라 **기계적 평탄화(a) + 슬러리 수송 차단(b) + 계면 오염층(c)**의
중첩이다. 이 노트에서 정량화할 수 있었던 것은 (a)뿐이다 — (b)(c)의 정량 실측(기공 폐색률,
잔류물 두께)은 확보한 1차 출처에 없다(**미검증, 정성 서술만**). 마찰계수 변화 수치도 이번
회차에 1차 출처를 확보하지 못했다(미검증).

Moon(1999)이 컨디셔닝 없는 MRR 감쇠의 근거로 든 Li(1995)·Stein(1996)은 원문 미확보(2차 인용).
Borucki(2002)의 polish-rate decay 수학모델은 doi.org/10.1023/A:1020305108358 로 DOI 실존만
확인(Semantic Scholar/Crossref), 본문은 미확보 — 부모 노트와 동일하게 Shi&Ring(2010) 재서술로
간접 인용한다.

## 2. 1차 출처 정량 데이터: Jeong et al. (2024) — 컨디셔닝 없는 10분 연마

**출처**: Seonho Jeong, Yeongil Shin, Jongmin Jeong, Seunghun Jeong, Haedo Jeong, "Novel
Probability Density Function of Pad Asperity by Wear Effect over Time in Chemical Mechanical
Planarization", *Materials* 17(8), 1817 (2024), doi.org/10.3390/ma17081817, PMC11051262
(MDPI 오픈액세스 CC-BY, Europe PMC에서 PDF 전문 확보 → `papers/jeong2024-pad-asperity-pdf-wear-materials.pdf`,
JATS 전문 XML도 확인. 본문·표·그림 직접 읽음).

> ⚠ 출처 표기 정정: [[hertz-gw-contact-mechanics]]와 [[gw-nominal-vs-local-pressure]]는 이 논문
> (PMC11051262)을 "Yang et al. 2024"로 인용했으나, JATS 메타데이터·PDF 1면 모두 저자는
> **Jeong, Shin, Jeong, Jeong, Jeong(부산대)**이다. 이 노트는 정확한 저자명으로 인용한다(다른
> 노트의 정정은 담당 에이전트 몫으로 남김).

실험조건(§4.1, 직접 확인): IC1000 패드, 콜로이달 실리카 슬러리 150 mL/min, 200 mm SiO2
블랭킷 웨이퍼, 압력 2/3/4/5 psi, 테이블 93 rpm·캐리어 87 rpm, **컨디셔닝 없이** 60 s 단위로
600 s까지 연마(POLI-500, GnP Technology). 패드 표면은 공초점현미경·micro-CT로 측정.

### 2.1 접촉점 개수 N(t) — Table 1 (원문 표 그대로)

| 압력 | Bef. | 1 min | 2 min | 3 min | 4 min | 5 min | 10 min | Cond. |
|---|---|---|---|---|---|---|---|---|
| 2 psi | 109 | 121 | 103 | 113 | 97 | 91 | 56 | 114 |
| 3 psi | 106 | 103 | 116 | 110 | 98 | 96 | 52 | 120 |
| 4 psi | 121 | 118 | 101 | 99 | 80 | 82 | 60 | 110 |
| 5 psi | 114 | 96 | 72 | 81 | 60 | 46 | — | 108 |

(N = 측정 시야 내 접촉체 개수, 절대 밀도 환산은 논문에 없음. "Cond."는 10분 연마 후 1분
컨디셔닝한 값 — Fig.4 범례 "1 min conditioning after 10 min"에서 확인.)

저자 서술(§3.1): "초기 CMP에서는 접촉수에 유의한 변화가 없다가, CMP가 길어질수록 접촉수가
급감하며 이때 CMP 효율이 크게 떨어진다." — 즉 glazing은 **지연 후 급진행**하는 비선형 과정이다.
**컨디셔닝 1분으로 접촉수가 연마 전 수준(±13%)으로 복원**된다 — 이것이 "컨디셔닝으로의
회복"의 직접 실측 근거다.

### 2.2 높이편차 σz(t)와 평균반경 μR(t) — Fig.3/4 + 경험식 Eq.3/4

- Fig.3(그래프 눈금 판독, ±0.05 µm): σz(0)=4.51 µm에서 5분 후 2 psi 3.88 / 3 psi 3.34 /
  4 psi 3.21 / 5 psi 3.25 µm. 압력이 높을수록 초반 감소가 급하다(5 psi는 1분 만에 3.43 µm).
- Fig.4 우측(눈금 판독, ±1 µm): μR(0)≈7.5–8 µm → 10분 후 2 psi ≈19 / 3 psi ≈24.7 /
  4 psi ≈30.5 / 5 psi ≈33.5 µm. **반경이 2.5–4.5배** 커진다 — 뾰족한 다수 접촉이 뭉툭한
  소수 접촉으로 바뀌는 것이 (a)의 정량적 실체다.
- Fig.4 좌측(4 psi): 연마 전 반경 히스토그램은 5–10 µm에 몰려 있고, 10분 후 40–70 µm로
  퍼지며, **10분 후 1분 컨디셔닝**하면 10–30 µm 범위로 되돌아온다(완전 복원은 아님, 눈금 판독).
- 경험식(원문 Eq.3, Eq.4, 계수는 본문 명시): σz,wear = σz(0) + exp(−1/τ1) + β1·exp(−t/τ2) − γ1,
  μR = (β2·p + γ2)·t + β3·exp(β4·p); σz(0)=4.512, τ1=158.01·e^(−1.195p), τ2=21.5, β1=1.411,
  γ1=2.405, β2=0.28, β3=5.45, β4=0.18, γ2=0.621. (단위는 본문에 명기되지 않음 — 아래 verify에서
  μR[µm], t[min], p[psi]로 두면 Fig.4 판독값과 맞는 것을 확인. **Eq.3은 인쇄된 형태 그대로는
  τ1 항에 t가 없어 t=0 값이 압력에 따라 달라지는 자기모순이 있다** — 조판 누락 추정, 아래
  verify에서 그 모순을 수치로 기록. 저자 의도 형태는 확정 못 함, 미검증.)

### 2.3 MRR(t) — Fig.9 (정규화, 2 psi 초기 MRR=1 기준, 눈금 판독 ±0.02)

| t (min) | 1 | 2 | 3 | 4 | 5 | 7 | 10 |
|---|---|---|---|---|---|---|---|
| Exp. 2 psi | 1.00 | 0.975 | 1.03 | 0.975 | 0.935 | 0.88 | 0.835 |
| Exp. 5 psi | 1.15 | 1.25 | 1.185 | 1.035 | 1.005 | 0.94 | 0.87 |

저자 서술(§4.2): 실제 CMP에서 MRR은 초기에 뚜렷이 감소하지 않고 "증가하거나 안정"하다가
일정 시간이 지나면 급감한다. 이유(§4.2, Fig.10): 초기에는 높이 감소로 asperity당 접촉력이
줄지만 **반경 증가가 접촉력 감소를 보상**하고(고압입 영역에서 반경 효과 큼), 계속되면
접촉수·압입깊이가 함께 급감해 보상이 사라진다. 높이 마모만 넣은 기존 모델(Ref. model)은
초기 상승을 재현 못 하고 단조감소만 예측한다.

**핵심 정량 관계(이 노트의 발견)**: 10분간 접촉점 수는 약 절반(2 psi: 109→56, −49%)으로
줄었는데 MRR은 −17%(2 psi)만 줄었다. MRR이 접촉수에 비례하지 않는 이유는 위의 반경 보상과,
하중이 일정하므로 남은 asperity에 하중이 재분배되기 때문이다 — [[hertz-gw-contact-mechanics]]
§4의 지수분포 GW 결과(A_r/W가 η와 d에 무관한 상수)에 따르면 η가 절반이 되어도 총 실접촉면적은
같고 **접촉당 면적이 2배**가 된다. 이는 Fig.4의 반경 증가와 정성적으로 정합한다(정량 대응은
미검증 — GW의 η는 표면 전체 밀도이고 Table 1의 N은 접촉 중인 개수라 정의가 다름).

## 3. 컨디셔닝 중단(ex situ) 후 MRR 감쇠의 산업 실측: Lawing (2004)

**출처**: A. Scott Lawing, "Pad Conditioning Effects in Chemical Mechanical Polishing", NCCAVS
CMPUG 2004-05-05 발표자료, https://nccavs-usergroups.avs.org/wp-content/uploads/CMPUG2004/CMPUG_05_2004_Lawing.pdf
(공개 PDF, 이번 회차에 재확보·12면/17면을 이미지로 렌더링해 판독). 같은 저자의 피어리뷰판
"Pad Conditioning and Pad Surface Characterization in Oxide CMP", *MRS Proc.* 732 (2002),
doi.org/10.1557/proc-732-i5.3 — DOI 실존 확인, 본문 미확보(Jeong 2024 ref.[26]은 2011로
표기하나 Crossref/Semantic Scholar는 2002 — 온라인 게재연도 차이로 추정).

12면 "Ex Situ Rate Decay" 그래프(산화막 폴리시율 Å/min vs 컨디셔닝 중단 후 시간, 눈금 판독
±30 Å/min):
- Fumed 실리카 슬러리 / 중간 공격성 컨디셔너: 1 min 2280 → 31 min 1480 Å/min (**−35%**)
- Fumed / 고공격성: 0 min 2550 → 31 min 1620 Å/min (−36%)
- Colloidal / 중간: 2 min 2950 → 20 min 2730 Å/min (**−7%**)
- Colloidal / 고: 2 min 3100 → 31 min 2870 Å/min (−7%)

저자 결론(원문 그대로): "Typical 'logarithmic' decay of rate after conditioning is suspended",
"Colloidal slurries induce less significant asperity wear and result in less significant rate
decay", "Conditioning sets initial rate but has little influence after conditioning is
suspended". 같은 슬라이드의 패드 높이분포(간섭계): Fumed-Medium은 0→3→15→31 min에 걸쳐
분포 고단부에 좁고 높은 2차 피크가 성장(=마모된 asperity 끝의 평탄면), Colloidal-Medium은
31 min에도 분포 형태가 거의 유지된다.

17면 "Polish Rate and Contact Area": 폴리시율은 모델 추정 접촉면적에 대해 **최대점**을 가진다 —
임계 접촉면적 이상에서는 rate ∝ 접촉면적(=인가압력), 이하에서는 절대 접촉면적이 rate를
제한한다(저자의 working model). Colloidal ex situ 데이터는 31 min간 3100→2870 Å/min로
거의 평탄(−7%). **Fumed vs colloidal의 5배 감쇠 차이**는 glazing이 순수 기계적 마모가 아니라
슬러리 입자 종류(응집 fumed 입자의 공격성)에 강하게 의존함을 뜻한다 — 구성요소 (b)(c)와
연결되나 메커니즘 분리는 이 자료로 불가(미검증).

## 4. 정량 재현 (python verify)

재현 요약(한 줄): (Jeong et al. 2024, doi.org/10.3390/ma17081817) Table 1 접촉점 수 109→56(2 psi, 10 min)은 −48.6% 감소로 문헌값과 대조해 재현되고, Eq.4 평균반경 19.6 µm(2 psi, 10 min)는 Fig.4 판독값 19 µm와 3% 이내로 일치하며, (Lawing 2004) fumed 31 min 감쇠 −35%는 colloidal −7%의 4.7배로 대조 확인된다.

```python verify
import numpy as np

# ── (A) Jeong et al. 2024, Materials 17, 1817, doi 10.3390/ma17081817 — Table 1 (원문 표 그대로)
t_tab = {2: [0, 1, 2, 3, 4, 5, 10], 3: [0, 1, 2, 3, 4, 5, 10],
         4: [0, 1, 2, 3, 4, 5, 10], 5: [0, 1, 2, 3, 4, 5]}
N_tab = {2: [109, 121, 103, 113, 97, 91, 56], 3: [106, 103, 116, 110, 98, 96, 52],
         4: [121, 118, 101, 99, 80, 82, 60], 5: [114, 96, 72, 81, 60, 46]}
N_cond = {2: 114, 3: 120, 4: 110, 5: 108}   # 10 min 연마 후 1 min 컨디셔닝

loss = {p: 1 - N_tab[p][-1] / N_tab[p][0] for p in N_tab}
print("접촉점 감소율(마지막 측정/초기):", {p: f"{v*100:.1f}%" for p, v in loss.items()})
assert abs(loss[2] - 0.486) < 0.005, "2 psi 10 min 감소율이 109→56(−48.6%)와 다름"
for p in (2, 3, 4):
    assert 0.45 < loss[p] < 0.55, f"{p} psi 10 min 접촉점 감소가 약 절반이 아님: {loss[p]:.2f}"
assert loss[5] > loss[2], "5 psi는 5 min만에 2 psi의 10 min보다 더 줄어야(압력 가속) 함"

# 지수감쇠 N=N0 exp(-t/tau) 최소자승 — 압력이 높을수록 tau가 짧은가
tau = {}
for p in N_tab:
    t = np.array(t_tab[p], float); y = np.log(np.array(N_tab[p], float))
    slope, _ = np.polyfit(t, y, 1)
    tau[p] = -1 / slope
print("지수감쇠 시정수 tau[min]:", {p: f"{v:.1f}" for p, v in tau.items()})
assert tau[5] < tau[2], "5 psi tau가 2 psi보다 길다 — '압력이 마모를 가속' 서술과 모순"
# 3 psi vs 4 psi는 단조가 아닐 수 있음(측정 산포) — 강제하지 않고 출력만 한다.

# 컨디셔닝 회복: 연마 전 대비 ±15% 이내로 복원되는가
rec = {p: N_cond[p] / N_tab[p][0] for p in N_tab}
print("컨디셔닝 후/연마 전 접촉점 비:", {p: f"{v:.2f}" for p, v in rec.items()})
assert all(0.85 < v < 1.15 for v in rec.values()), "1 min 컨디셔닝으로 접촉점 수가 초기 ±15%로 복원되지 않음"

# ── (B) Eq.4 평균반경 μR = (β2 p + γ2) t + β3 exp(β4 p)  vs Fig.4 우측 눈금 판독값(±1 µm)
b2, b3, b4, g2 = 0.28, 5.45, 0.18, 0.621
muR = lambda p, t: (b2 * p + g2) * t + b3 * np.exp(b4 * p)
fig4_read = {2: 19.0, 3: 24.7, 4: 30.5, 5: 33.5}   # µm at t=10 min, 그래프 판독
for p, obs in fig4_read.items():
    pred = muR(p, 10.0)
    err = abs(pred - obs) / obs
    print(f"Eq.4 μR({p} psi, 10 min) = {pred:.1f} µm vs 판독 {obs} µm (오차 {err*100:.1f}%)")
    assert err < 0.10, f"Eq.4가 Fig.4 판독값과 10% 이상 어긋남 (p={p})"
assert abs(muR(2, 10.0) - 19.6) < 0.1
ratio_R = muR(2, 10.0) / muR(2, 0.0)
print(f"2 psi 10 min 반경 증가 배율 = {ratio_R:.2f}배 (초기 {muR(2,0):.2f} µm)")
assert 2.0 < ratio_R < 3.0

# ── (C) Eq.3 인쇄 형태의 자기모순 기록: t=0에서 σz가 압력에 따라 달라짐
s0, tau2, b1, g1 = 4.512, 21.5, 1.411, 2.405
tau1 = lambda p: 158.01 * np.exp(-1.195 * p)
sig_eq3 = lambda p, t: s0 + np.exp(-1 / tau1(p)) + b1 * np.exp(-t / tau2) - g1
z0 = {p: sig_eq3(p, 0.0) for p in (2, 3, 4, 5)}
print("Eq.3(인쇄형) t=0 σz:", {p: f"{v:.2f}" for p, v in z0.items()}, "— Fig.3 실측은 전 압력 4.51 µm")
spread = max(z0.values()) - min(z0.values())
assert spread > 0.5, "인쇄형 Eq.3이 t=0에서 압력 무관이라면 이 노트의 '자기모순' 지적이 틀린 것"
print(f"  → t=0 값이 압력에 따라 {spread:.2f} µm 벌어짐: 인쇄된 Eq.3은 그대로 쓸 수 없다(조판 누락 추정, 미해결)")

# ── (D) Fig.9 정규화 MRR(눈금 판독 ±0.02) — 접촉점 감소(−49%)보다 MRR 감소가 훨씬 작은가
t9 = np.array([1, 2, 3, 4, 5, 7, 10], float)
mrr2 = np.array([1.00, 0.975, 1.03, 0.975, 0.935, 0.88, 0.835])
mrr5 = np.array([1.15, 1.25, 1.185, 1.035, 1.005, 0.94, 0.87])
drop2 = 1 - mrr2[-1] / mrr2[0]; drop5 = 1 - mrr5[-1] / mrr5.max()
print(f"Fig.9 MRR 감소: 2 psi 1→10 min −{drop2*100:.1f}%, 5 psi 최대→10 min −{drop5*100:.1f}%")
assert 0.12 < drop2 < 0.22 and 0.25 < drop5 < 0.35
assert drop2 < loss[2] * 0.5, "MRR 감소가 접촉점 감소의 절반 이상이면 '반경 보상' 서술을 재검토해야 함"
assert mrr5.argmax() == 1 and mrr2.argmax() == 2, "초기 MRR 상승(2 psi 3 min, 5 psi 2 min 피크)이 판독값에 없음"

# ── (E) Lawing 2004 (NCCAVS CMPUG) 12면 Ex Situ Rate Decay, 눈금 판독 ±30 Å/min
t_fm = np.array([1, 2, 3, 5, 7, 11, 15, 19, 23, 27, 31], float)
r_fm = np.array([2280, 2200, 1990, 1860, 1790, 1770, 1690, 1630, 1590, 1540, 1480], float)
t_cm = np.array([2, 5, 7, 9, 11, 13, 15, 17, 19, 20], float)
r_cm = np.array([2950, 2810, 2790, 2770, 2760, 2770, 2730, 2730, 2720, 2730], float)
t_fh = np.array([0, 1, 3, 5, 11, 15, 19, 23, 27, 31], float)
r_fh = np.array([2550, 2470, 2330, 2160, 1990, 1860, 1800, 1730, 1670, 1620], float)
t_ch = np.array([2, 4, 7, 10, 14, 18, 22, 26, 31], float)
r_ch = np.array([3100, 2990, 2950, 2950, 2950, 2940, 2920, 2890, 2870], float)

decay_fm = 1 - r_fm[-1] / r_fm[0]; decay_cm = 1 - r_cm[-1] / r_cm[0]
decay_fh = 1 - r_fh[-1] / r_fh[0]; decay_ch = 1 - r_ch[-1] / r_ch[0]
print(f"Lawing ex situ 감쇠: fumed-med −{decay_fm*100:.0f}%, fumed-high −{decay_fh*100:.0f}%, "
      f"colloidal-med −{decay_cm*100:.0f}%, colloidal-high −{decay_ch*100:.0f}%")
assert abs(decay_fm - 0.35) < 0.02 and abs(decay_cm - 0.075) < 0.02
assert decay_fm / decay_cm > 3.0, "fumed 감쇠가 colloidal의 3배 이상이어야 '슬러리 의존' 서술 성립"

# '로그 감쇠' 주장: rate = a − b·ln(t) 적합의 R²
def r2_log(t, r):
    x = np.log(t); b, a = np.polyfit(x, r, 1); pred = a + b * x
    return 1 - np.sum((r - pred) ** 2) / np.sum((r - r.mean()) ** 2), a, b
R2_fm, a_fm, b_fm = r2_log(t_fm, r_fm)
R2_fh, a_fh, b_fh = r2_log(t_fh[1:], r_fh[1:])   # t=0은 ln 불가 → 제외
print(f"log 적합 fumed-med: rate = {a_fm:.0f} {b_fm:+.0f}·ln t, R² = {R2_fm:.3f}; fumed-high R² = {R2_fh:.3f}")
assert R2_fm > 0.95 and R2_fh > 0.95, "'logarithmic decay' 서술이 판독 데이터로 재현되지 않음"
# 같은 데이터를 선형(rate = a − b t)으로 적합하면 R²가 더 낮아야 '로그형'이 선형보다 나은 서술
b_lin, a_lin = np.polyfit(t_fm, r_fm, 1); pred_lin = a_lin + b_lin * t_fm
R2_lin = 1 - np.sum((r_fm - pred_lin) ** 2) / np.sum((r_fm - r_fm.mean()) ** 2)
print(f"선형 적합 R² = {R2_lin:.3f} (로그 적합 {R2_fm:.3f}보다 {'낮음' if R2_lin < R2_fm else '높음!'})")
assert R2_lin < R2_fm, "선형이 로그보다 잘 맞으면 Lawing의 'logarithmic' 표현은 재검토 대상"
print("PASS: (A)~(E) 전부 문헌 상수 재현/대조 통과")
```

실행 결과 요약(2026-09-07, 위 블록 그대로 실행): 접촉점 감소 2/3/4 psi −48.6/−50.9/−50.4%,
5 psi(5 min) −59.6%; 지수감쇠 τ ≈ 2 psi 15 min → 5 psi 5–6 min; 컨디셔닝 후 복원비
0.91–1.13; Eq.4 μR 오차 0.3–6%; Fig.9 MRR −17%(2 psi)/−30%(5 psi 피크 대비); Lawing fumed
−35% vs colloidal −7%, 로그 적합 R² > 0.95이고 선형보다 높음. **정직한 한계**: (B)(D)(E)의
"관측값"은 그래프 눈금 판독이라 ±3–5% 판독오차를 내포하며, assert 문턱은 그 오차를 반영해
느슨하게 잡았다. 표 값(A)만이 원문 숫자 그대로다.

## 5. 부모·형제 노트와의 연결 — glazing을 population balance 언어로

- [[pad-wear-glazing-mrr-decay]] §2.5의 MRR = c_w·P_a/A_c(Shi&Ring Eq.15)와 [[gw-nominal-vs-local-pressure]]의
  "실접촉압력은 명목압력과 거의 무관" 결론을 합치면, glazing 중 MRR이 떨어지는 1차 경로는
  **P_a/A_c 자체의 변화가 아니라 접촉 개수 n(t)와 접촉당 기하(반경·압입깊이)의 변화**다 —
  Jeong 2024의 3-모드 MRR 식(Eq.20)이 정확히 그 항들을 시간의존으로 만든 것이다.
- [[pad-conditioning-wear-regeneration-balance]] §3의 "두 종류 정상상태" 중 (a) 컨디셔닝 균형에서
  B항(생성)이 하는 일이 Table 1 "Cond." 열의 복원(56→114)이다. Lawing의 "Cut Rate < Wear
  Rate = Severe glazing"은 이 복원이 접촉수 감쇠 속도(τ ≈ 5–15 min, 압력 의존)를 따라잡지
  못하는 상태로 번역된다.
- [[pad-breakin-asperity-mrr-runup]] §3의 "접촉면적↓·둘레↑ → MRR↑" 가설과 Jeong 2024 Fig.9의
  초기 MRR 상승(2 psi 3 min, 5 psi 2 min 피크)은 같은 현상의 두 관찰일 가능성이 있다 — 다만
  Jeong 2024는 이를 "반경 증가에 의한 접촉력 보상"으로 설명하므로 브레이크인 노트의
  "macro-asperity 분해" 가설과는 메커니즘 서술이 다르다(어느 쪽이 맞는지 미검증).
- [[conditioning-mechanism-asperity-regeneration]] §2의 "저공격성 컨디셔너일수록 접촉면적이
  커진다(11.3/7.7/2.2%)"는 Lawing 17면 "rate vs 접촉면적 최대점" 그림과 같은 자료다: glazing이
  진행되면 접촉면적은 **늘지만** rate는 준다 — "접촉면적이 크면 MRR이 크다"는 직관은 임계점
  이상에서 뒤집힌다.

## 6. 미검증·한계 표기 (정직성)

- 구성요소 (b) 기공 막힘, (c) 잔류물 응착의 **정량 실측은 이 노트에 없다** — Moon(1999)·McGrath &
  Davis(2004) 서술 인용뿐. McGrath & Davis는 검색 스니펫 수준(초록 접근 403), 2차 인용.
- 마찰계수 변화: 1차 출처 미확보, 미검증(다음 회차 과제).
- Jeong 2024 Eq.3(σz)은 인쇄 형태 그대로 자기모순 → 저자 의도 형태 미확정. Eq.4(μR)만 재현.
- Jeong 2024 Fig.3/4/9, Lawing 2004 12면/17면 수치는 **그래프 눈금 판독**(디지타이저 미사용).
- Lawing 2004는 산업 발표자료(피어리뷰 아님). 피어리뷰판 MRS 732(2002)는 DOI만 확인.
- Table 1의 N은 측정 시야 내 개수라 절대 asperity 밀도(η, /m²)로 환산 불가 — sim 연결 시
  비율(N/N0)만 사용해야 한다.
- Borucki(2002)·Li(1995)·Stein(1996) 원문 미확보(2차 인용).

## 7. 출처 요약 (한 줄 형식)
- Seonho Jeong, Yeongil Shin, Jongmin Jeong, Seunghun Jeong, Haedo Jeong (2024), "Novel Probability Density Function of Pad Asperity by Wear Effect over Time in Chemical Mechanical Planarization", *Materials* 17, 1817, doi.org/10.3390/ma17081817, PMC11051262 — OA 전문 확보·직접 읽음(1차).
- A. Scott Lawing (2004), "Pad Conditioning Effects in Chemical Mechanical Polishing", NCCAVS CMPUG 2004-05-05 공개 PDF — 확보·직접 판독(1차, 비피어리뷰). 피어리뷰판: Lawing (2002) *MRS Proc.* 732, doi.org/10.1557/proc-732-i5.3 — DOI 실존만 확인.
- Yongsik Moon (1999), "Mechanical Aspects of the Material Removal Mechanism in Chemical Mechanical Polishing (CMP)", Ph.D. dissertation, UC Berkeley (advisor D.A. Dornfeld), 공개 PDF https://cden.ucsd.edu/internal/Publications/Archive/SFR/Misc.papers/YongsikDissertation.pdf — 확보·직접 읽음(1차, 학위논문).
- J. McGrath, C. Davis (2004), "Polishing pad surface characterisation in chemical mechanical planarisation", *J. Mater. Process. Technol.* 153-154, 666-673, doi.org/10.1016/j.jmatprotec.2004.04.094 — DOI 실존 확인, 초록 스니펫만(2차).
- L. Borucki (2002), "Mathematical modeling of polish-rate decay in chemical-mechanical polishing", *J. Eng. Math.* 43, 105-114, doi.org/10.1023/A:1020305108358 — DOI 실존 확인, 본문 미확보.
- Hong Shi, Terry A. Ring (2010), *Microelectron. Eng.* 87, 2368, doi.org/10.1016/j.mee.2010.04.010 — [[pad-conditioning-wear-regeneration-balance]]에서 전문 확보 완료, 이 노트는 재인용.

## 8. 비-실리카 계 외삽 갭 — 1차 문헌 탐색 기록 (2026-09-13 [Max워커], 1회차)

`_f_stab()`은 confidence를 `literature if abrasive == "silica" else "estimated"`로 준다.
Jeong 2024 원 데이터가 콜로이달 실리카/IC1000 단일계이기 때문이다. 따라서 S(stab) 팩터의
C2 미충족 4칸(cu_h2o2_bta=알루미나, sic_ceria_h2o2·sti_ceria=세리아, w_fe_oxidizer=알루미나)은
**"다른 연마입자계에서 무-컨디셔닝 시간감쇠를 실측한 1차 문헌"** 하나로 동시에 해소된다
(`tools/blockers.py` 키별 1위: time_s 4칸).

이번 회차 탐색 결과 — **미확보**:

| 후보 | 상태 |
|---|---|
| Pad Surface Variation and its Effect on SiO₂ Removal Rate in Ceria-based CMP Slurry, **CSTIC 2023, doi:10.1109/cstic58779.2023.10219240** | 제목·DOI상 **정확히 필요한 세리아 계 문헌**. IEEE 유료. 미러 사이트 "논문을 찾을 수 없습니다", 미러 사이트/.ren Cloudflare Turnstile 캡차, 미러 사이트/.st DNS 불능 → 본문 미확보 |
| Effect of Pad Surface Roughness on SiO₂ Removal Rate in CMP with Ceria Slurry, JJAP 45, 733 (2006), doi:10.1143/jjap.45.733 | Unpaywall이 OA로 표시하나 IOP `/pdf`가 14 KB HTML(봇 차단) 반환 → 미확보 |
| Choi, Doyle, Dornfeld, *ECS JSSST* **6**, P187 (2017), doi:10.1149/2.0351704jss | **OA 전문 확보**(11 p). 그러나 내용은 BTA 보호막 제거효율(전기화학 전류밀도)이지 **시간감쇠가 아니다** — 이 갭에 무효 |
| Seo, *J. Mater. Res.* (2020), doi:10.1557/s43578-020-00060-x | 전문 확보(23 p, 리뷰). 2차 인용이라 C2 승격 근거로 불가 |

**판정(미종결, 1회차)**: 알루미나·세리아 계 시간감쇠는 지금 코퍼스로 확정할 수 없다.
근거 없이 실리카 계수(a=1.1478, b=−0.1109)를 4팩에 전이하는 것은 금지 — 같은 노트 §3이
**fumed vs colloidal 실리카만으로도 감쇠율이 5배 차이**남을 기록하고 있어, 연마입자 종류를
넘는 전이는 E4(타계 전이)로도 정당화되지 않는다. 현행 `estimated` 유지가 정직한 상태다.

EVIDENCE-RULES §3회차 규칙 적용 대상으로 등록한다 — **이 갭은 3회차까지만 보류 가능**하며,
그때까지 1차 문헌을 못 구하면 (a) CSTIC 2023을 다른 경로로 확보하거나 (b) "S팩터는
실리카 계에서만 literature, 그 외는 스코프 밖"으로 **스코프 축소 종결**한다.

### 8.1 2회차 탐색 기록 (2026-09-14 [Max워커], 2회차) — 전부 미확보

| # | 질의 | 결과 | 부적격 사유 |
|---|---|---|---|
| 1 | `find_open_access.py --title "ceria slurry polishing time material removal rate decay pad glazing"` | 1건: doi:10.1007/s13391-012-2144-5 "Effect of pad surface roughness on material removal rate in CMP using ultrafine colloidal ceria slurry" | 패드 거칠기 축이지 시간축 감쇠가 아니다 |
| 2 | Crossref `query.bibliographic="ceria slurry polishing time removal rate decrease without conditioning"` (8건) | 전부 농도·pH·계면활성제·패드거칠기 축 | 시간축 무-컨디셔닝 감쇠 데이터 없음 |
| 3 | Crossref `query.bibliographic="polishing time dependence removal rate alumina slurry CMP pad glazing"` (8건) | 컨디셔너 물성/온도/roll-CMP 축. 그 중 CSTIC 2023 세리아 논문(doi:10.1109/cstic58779.2023.10219240, "Pad Surface Variation and its Effect on SiO2 Removal Rate in Ceria-based CMP Slurry")가 판정#9의 원 최근접 후보로 재등장 | IEEE 유료 + 미러 사이트 4개 미러 전부 실패(se/st 응답 000, ru 302 리다이렉트, ren 200이나 "Verification — Please complete the check" 캡차 페이지) — 1회차와 동일하게 본문 미확보 |
| 4 | OpenAlex `search="ceria slurry polishing time removal rate decrease pad glazing"&filter=is_oa:true` (10건) | 스크래치·패드debris·컨디셔너 texture 축 | 시간축 감쇠 없음 |
| 5 | OpenAlex `search="pad wear polish rate decay asperity population balance"` (10건) | 최근접 doi:10.1016/j.mee.2010.04.010 "CMP pad wear and polish-rate decay modeled by asperity population balance with fluid effect"; 나머지 OA 항목은 무관; Jeong 2024(doi:10.3390/ma17081817, 이미 확보한 동일 실리카 계 데이터)가 재등장 | mee.2010.04.010은 OA=false(Elsevier 유료); Jeong 2024는 이미 확보한 동일 실리카 계 데이터라 새 정보 아님 |
| 6 | OpenAlex `search="copper CMP removal rate polishing time decay alumina slurry"&filter=is_oa:true` (12건) | 트리아졸 부동태화 속도론·tribo-전기화학 등 | 시간축 MRR 감쇠가 아니다 |

**결론(2회차 종결, 미확보)**: 알루미나·세리아 계의 무-컨디셔닝 시간축 MRR 감쇠 실측은 OA 범위에
존재하지 않는다. 유일한 계 근접 후보(CSTIC 2023, doi:10.1109/cstic58779.2023.10219240)는
유료+봇차단으로 2회 연속 실패했다. **3회차에도 미확보면 4회차 없이 종결** —
"S는 실리카 계에서만 literature"로 스코프 축소하고, `_f_stab`의 현행 `estimated` 하한을
영구 확정한다(코드 docstring에 사유 명시).
