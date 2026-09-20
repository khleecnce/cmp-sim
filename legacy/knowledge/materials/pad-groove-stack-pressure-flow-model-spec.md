<!-- V2-SECTION: R3-pad | 공동: R2-slurry | 분배완료 2026-09-08 | 근거: groove, pad-, subpad, 패드 | 정본: ARCHITECTURE-V2.md §3 -->
# 그루브·적층 파라미터 → 압력 분포·유동 통합 모델 명세 (구현 명세)

> pad-structure Lv3-2. 선행(재서술 금지, 인용만):
> [[pad-groove-slurry-transport]](Lv1-1 GFQ 정의) · [[pad-groove-geometry-contact-area-flow-resistance]](Lv1-2 GFQ 실측·수확체감) ·
> [[pad-subpad-stiffness-edge-nonuniformity]](Lv2-1 Lo&Lin 단일 등가층 R) · [[pad-groove-wear-flow-change-end-of-life]](Lv2-2 컨덕턴스·τ) ·
> [[pad-groove-cfd-micropattern-optimal-design]](Lv3-1 DCA/DICL) · [[hertz-gw-contact-mechanics]](GW 국소압) · [[cmp-multizone-carrier-radial-response]](존-반경 응답).
> **이 단원의 목적은 구현이 아니라 "구현 가능한 모델 명세 + 문헌값 재현"이다.** sim/ 은 건드리지 않는다(구현요청은 §7·PROFILE).
> 형제 경계: 패드 재료 물성(E_pad 유효압축률·GW 파라미터)은 pad-material, 마모 수명(컷레이트·EOL)은 pad-lifecycle 소관 — **인용만**.
> 조사범위: `tools/scope.py --agent pad-structure`. 핵심 1차 문헌 일부는 2011년 이전(Choi&Dornfeld 2004, Xin, Byrne 2011)이나,
> 원문/리프린트를 직접 확보했고 이 단원의 정량 앵커라 Lv2-1과 같은 예외 사유로 사용(§8에 근거등급 표기).

## 0. 이 노트가 새로 하는 일 (Lv1~Lv3-1과 겹치지 않는 부분)

Lv2-1은 패드를 **단일 등가층**(E0·T0)으로 다뤄 엣지 응력비 R의 단조 경향만 재현했고(§4에서 "서브패드 2층 명시 모델 1차 미확보"로
남김), Lv1-2/Lv2-2는 그루브 폭·깊이의 유동(GFQ·τ·컨덕턴스)을 다뤘다. 이 단원은 그 조각들을 **구현 가능한 하나의 명세**로 묶고,
Lv2-1이 비워둔 **2층 적층(E1,t1/E2,t2) → 반경 압력** 자리를 1차 문헌으로 채운다:
(a) 2층 강성 적층 → 엣지 피크비(FEA 문헌 3계열) + 엣지롤오프 폭(준해석 BOEF 모델),
(b) 그루브 기하 → 접촉면적비·land 압력 증배 P/(1−GFQ)·유동 컨덕턴스를 **한 파라미터 세트**로,
(c) 그루브 유형(동심원/방사/나선)별 체류시간·MRR 상대비(1차 실측 3편),
(d) 기존 sim/tier2 함수와의 중복·충돌 점검.

## 1. (a) 2층 적층 강성 → 웨이퍼 반경 방향 압력 분포

### 1.1 세 영역 구조와 엣지 피크비 — FEA 문헌 3계열

웨이퍼-패드 접촉압력은 반경 방향으로 **평탄(interior) / 전이(약간 저압) / 엣지 급증(abrupt)** 세 영역으로 나뉘고, 엣지 급증이
과잉연마(edge roll-off)의 근원이다(Xin, "Modeling of Pad-Wafer Contact Pressure Distribution in CMP", Sensor Products
리프린트, **DOI 없음·리프린트 원문 확인**; Baker 1996 소프트층=탄성스프링 모델을 FEA로 재현). Xin 원문 결론:
**"엣지 압력 피크의 진폭과 비균일 영역의 폭이 둘 다 패드 경도가 낮아질수록 커진다"**(정성, 그림만).

엣지 피크비(σ_edge/σ_avg 또는 P_edge/P_center)의 **정량 앵커는 독립 FEA 3계열**이 준다:

| 출처 | 계열 | 엣지 피크비 | 조건 |
|---|---|---|---|
| Byrne et al. 2011 (DOI: 10.1177/09544054JEM2187) | 하중구성 1 / 2 | **1.732 / 2.391** | 200 mm, 패드 2.68 mm+서브패드 1.33 mm, 리테이너링·립실 포함, 압력필름 실측 검증 |
| Wang et al.(Byrne이 인용) | 캐리어필름 단독하중 | **4.47** | 하중 전량이 캐리어필름→웨이퍼로 전달(엣지 분담 없음) |
| Lo & Lin 2005 (DOI: 10.1016/j.jmatprotec.2005.01.010) | E0·T0 스윕 | **1.68–2.08** | 단일 등가층, R=σ_max/σ_c ([[pad-subpad-stiffness-edge-nonuniformity]] 재현) |

핵심 해석(재서술 아님, 세 계열 종합): 엣지 하중을 리테이너링·립실로 **분담**한 Byrne(1.73–2.39)이 전량 캐리어필름으로 미는
Wang(4.47)보다 피크비가 낮다 — 즉 피크비는 패드 강성뿐 아니라 **엣지 하중경로(리테이너링 유무)**에 크게 좌우된다. 이는
[[cmp-multizone-carrier-radial-response]]의 리테이너링 기능(가상접촉면 확장·패드 리바운드 억제)과 같은 물리다.

### 1.2 2층 적층의 명시 회귀 — Choi & Dornfeld 2004 (die-scale)

Lv2-1이 못 구한 **상/하 2층(경질 E_h·t_h / 연질 E_s·t_s) 명시 모델**을 die-scale에서 확보했다.
**출처(1차, OA 원문 전체 확보): Choi, Dornfeld, "Evaluation of the Effect of Pad Thickness and Stiffness on Pressure
Non-Uniformity at Die-Scale in ILD CMP", UC Berkeley LMAS eScholarship item 06k6x1vm (2004);
동일 저자·동년 게재본 MRS Symp. Proc. 816, K4.4 (DOI: 10.1557/proc-816-k4.4).** 2층 FEM에 2⁴ 완전요인 DOE를 걸어
WIDNU 지표 H/L(=최대접촉압/최소접촉압)의 코드화 회귀를 얻었다(원문 식 1):

    H/L = 6.526892 + 0.628464·E_h − 0.577953·E_s − 0.374445·T_h   (E_h,E_s,T_h ∈ {−1,+1} 코드값)

원문이 명시한 설계규칙 3가지: (1) 경질층이 뻣뻣할수록 WIDNU↑, (2) 경질층이 두꺼울수록 WIDNU↓, (3) 연질층이 뻣뻣할수록
WIDNU↓. 지배 드라이버 순위는 |경질강성 0.628| > |연질강성 0.578| > |경질두께 0.374|(§5 A1 재현).

**⚠ 스케일 구분(중요, 혼동 금지)**: Choi&Dornfeld의 H/L은 **die-scale(패턴 간) WIDNU**이고 위 §1.1의 피크비는
**wafer-scale(엣지) 비균일**이다. 그래서 "두께" 부호가 겉보기 반대다 — die-scale은 경질층 두께↑→H/L↓(원문 규칙 2),
wafer-scale은 총 패드 두께↑→엣지 피크↑(Xin·Lo&Lin T0↑→R↑). 두 스케일은 지배 물리(die는 국소 굽힘, wafer는 엣지
기하 불연속)가 달라 **하나의 부호로 통합하면 안 된다**(EVIDENCE-RULES §스코프 분리).

### 1.3 엣지롤오프 폭 — 준해석 BOEF 모델 (이 노트의 새 명세)

피크비는 문헌 앵커가 있으나 **폭(width)의 폐형식**은 문헌이 그림으로만 준다. 구현용으로 탄성기초(Winkler→Hetényi
beam-on-elastic-foundation) 준해석 모델을 명세한다. 2층 적층을 **직렬 스프링**으로 등가화한 기초강성(단위면적당):

    k_eff = 1 / (t1/E1 + t2/E2)   [Pa/m]     (E1,t1=상단패드, E2,t2=서브패드)

웨이퍼(두께 h_w 얇은 판, 굽힘강성 D_w=E_Si·h_w³/[12(1−ν²)])를 이 기초 위에 놓으면 엣지 교란이 감쇠하는 특성길이:

    λ = (4·D_w / k_eff)^(1/4)   [m]   ← 엣지롤오프 폭 스케일 (엣지 배제영역 ≈ λ~2λ)

물리적으로 검증되는 세 성질(§5 A3, 절대값이 아니라 **오더·방향**만 신뢰):
- **λ ≈ 6–9 mm 오더** — 실제 엣지 배제영역(수 mm)과 정합. 절대값은 E_pad 유효압축률(포아송·기공률 의존, **pad-material 소관**)이
  불확실해 **미검증(오더만)**.
- **연질 서브패드가 기초 컴플라이언스를 지배** — t2/E2 ≫ t1/E1(전형값에서 60배). 즉 웨이퍼-스케일 순응은 서브패드가, 국소
  asperity 접촉은 경질 상단패드가 맡는다([[hertz-gw-contact-mechanics]]와 역할 분리). Lv2-1이 단일 등가층으로 뭉갠 것을 여기서
  두 층으로 분해한 것이 이 단원의 실질 성과.
- **서브패드 뻣뻣↑ → k_eff↑ → λ↓ → 롤오프 폭 좁아짐** — Xin의 "경도↑→폭↓" 정성서술과 **같은 방향**(방향은 검증, 크기는 미검증).

## 2. (b) 그루브 기하 → 접촉면적·land 압력·컨덕턴스 통합 파라미터 세트 (모델 명세)

하나의 입력 세트에서 접촉·압력·유동을 모두 산출하는 명세:

| 구분 | 기호 | 정의 / 식 | 단위 | 유효범위 |
|---|---|---|---|---|
| 입력 | w | 그루브 폭 | µm | 250–1000 (Mu 2016) |
| 입력 | land | land(랜드) 폭 | µm | 500–2000 |
| 입력 | D | 그루브 깊이(현재) | µm/mm | 250–1250 초기 (Lv2-2) |
| 입력 | P_nom | 명목(공정) 압력 | kPa | 7–35 |
| 파생 | GFQ | w/(w+land) = 그루브 면적분율 | — | 0.15–0.40 실무구간 |
| 출력 | f_land | land 접촉분율 = 1 − GFQ | — | 0.60–0.85 |
| 출력 | **P_land** | **P_nom / (1 − GFQ)** (하중평형) | kPa | ×1.18–×1.67 |
| 출력 | V_groove | ∝ GFQ·A_wafer·D (Mu 2016 반응기) | cm³ | — |
| 출력 | G | 직사각채널 컨덕턴스 ∝ w·D³급(§Lv2-2) | 상대 | — |
| 출력 | τ | V_total/q_actual (Mu 2016) | s | — |

**land 압력 증배 P_land = P_nom/(1−GFQ)의 유도·근거**: 그루브에는 하중이 실리지 않으므로 전체 하중은 land가 받는다 —
하중평형 P_nom·A_total = P_land·A_land, A_land=(1−GFQ)·A_total ⟹ P_land = P_nom/(1−GFQ). Mu 2016 3종에서 증배는
×1.25/×1.5/×1.75(GFQ 0.20/0.333/0.429). 이 방향은 1차 문헌이 직접 지지한다: Cho 2022(DOI: 10.3390/app12094339)는
"방사 그루브가 land 면적을 잠식하면 global 접촉비가 낮아지고 **국소 pad-abrasive-wafer 압력이 커져** 단일 입자 압입깊이가
늘어 MRR이 오른다"고 명시하고, Wang & Yang 2007(DOI: 10.1149/1.2716558)도 "grooved pad는 접촉면적이 작다"고 못박는다.

**⚠ P_land↛MRR 직결 금지(정직성)**: P_land는 **국소 접촉응력**(GW·3체마모의 입력)이지 Preston 면적평균 MRR을 곧바로 곱하는
값이 아니다. Wang & Yang 2007은 접촉면적 감소가 지배하면 **net MRR이 오히려 낮아진다**고 보고한다 — Lv1-2에서 정리한
"폭↑(이용효율경로, Mu) vs 폭↓(접촉면적경로, Wei 2011)"의 두 상반 인과와 같은 구조다. 따라서 명세는 P_land를 GW/3체마모
레이어의 **국소압 입력**으로만 넘기고, 면적평균 MRR은 Preston이 P_nom으로 계산하도록 분리한다(통합 부호 강제 금지).

컨덕턴스·V_groove·τ 축은 **이미 sim/tier2에 구현됨**(§4) — 이 명세는 재구현하지 않고 그 함수를 재사용한다(§5 B에서 컨덕턴스
D³급 급감 0.097을 기존 함수로 확인).

## 3. (c) 그루브 유형별 슬러리 체류시간·MRR 상대비 (1차 실측 3편)

동심원(concentric)을 기준으로 방사(radial)·나선(spiral)의 상대 성능을 1차 실측으로 비교한다(XY는 정량 실측표 미확보 —
Guo 2012 SDT는 그래프뿐, [[pad-groove-geometry-contact-area-flow-resistance]] §5 인용, 여기선 방향만):

| 유형 | 출처(1차 실측) | 슬러리 체류/공급 | MRR (동심원 대비) | 비고 |
|---|---|---|---|---|
| 동심원 | (기준) | — | 기준 | 산업 표준 K-groove 계열 |
| 방사 | Cho 2022 (DOI: 10.3390/app12094339) | SST 21.52→16.06 s (**−25.4%**) | ↑ (NU 4.65→1.56%) | oxide, R0 vs R32 |
| 방사 | Bae 2022 (DOI: 10.1016/j.mssp.2022.106968) | 신선분율 0.528→0.676 | Cu RR 4051→5047 Å/min (**+24.6%**) | Cu, CG vs RG32, 90 rpm |
| 나선 | Rosales-Yeomans 2008 (DOI: 10.1149/1.2963268) | (COF +28%) | Cu RR (**+24%**) | Cu, Log(−)Spiral(+) vs 동심원 |

**핵심 교차수렴(§5 C 재현)**: 서로 다른 두 "smart groove" 유형 — 방사(Bae +24.6%)와 최적 나선(Rosales +24%) — 이
동심원 대비 **거의 같은 ~24% 폭으로 MRR을 올린다**(독립 논문·다른 막질·다른 그룹). 기전도 일치한다: 둘 다 회전과
직교/역류억제 채널을 만들어 신선 슬러리 공급을 빠르게 하고(체류·SST↓) land 접촉을 안정화한다. 방사는 SST를 25% 줄이고
(Cho), 나선은 COF를 28% 올린다(Rosales) — 서로 다른 대리지표지만 같은 방향(공급 가속→MRR↑). 단, Cho 초록은 동심원
SST를 25.52 s로 표기하나 본문 Table 4 실측은 21.52 s라 **본문값 채택**(초록 오타로 판단, Irfan 2025도 21.52 사용).

## 4. (d) 기존 sim/tier2 함수와의 중복·충돌 점검

| 축 | 필요 기능 | 기존 구현 | 상태 |
|---|---|---|---|
| 유동 컨덕턴스 | 직사각채널 Poiseuille G(D) | `pad_groove_wear_flow.rectangular_channel_conductance`, `conductance_ratio` | **있음**(Lv2-2) — 재사용 |
| 체류시간 | τ=V_total/q_actual | `pad_groove_wear_flow.residence_time_s`, `slurry_volumes_cm3` | **있음**(Lv2-2) — 재사용 |
| 마모 유동단계 | 초기/중기/말기 | `pad_groove_wear_flow.wear_stage`, `groove_wear_flow_state` | **있음**(Lv2-2) — 재사용 |
| GW 국소 접촉압 | asperity p_r=W/A_r | `gw_pressure_solve.local_contact_state` | **있음** — asperity 스케일(land 스케일 아님) |
| land 하중 증배 | P_land=P/(1−GFQ) | 없음 | **부재** → 구현요청 |
| 웨이퍼-스케일 엣지 | 피크비·롤오프폭 λ(2층) | 없음(Lv2-1은 단일층 R만) | **부재** → 구현요청 |
| 그루브 유형계수 | 동심원/방사/나선 상대 MRR·SST | 없음 | **부재** → 구현요청 |

충돌 없음(중복 재구현 위험만 존재): land 증배·엣지 모델은 기존 컨덕턴스/τ/GW 함수와 **직교**하며, 명세는 기존 함수를
호출해 쓰도록 설계한다. gw_pressure_solve의 국소압은 **asperity 스케일**이라 land 스케일 P_land와 다른 층위다(혼용 금지).

## 5. 정량 재현 (python verify — tools/verify_claims.py 가 실행)

재현 요약(§5 A): Choi&Dornfeld 2004 회귀로 die-scale H/L 4.946–8.108 재현 및 설계규칙 3부호 확인; wafer-scale 엣지
피크비 (Byrne et al. 2011) 1.732/2.391 < Wang 4.47, (Lo&Lin 2005) 밴드 1.68–2.08와 대조; BOEF λ 6.1–8.5 mm 오더(서브패드 지배·경도↑→폭↓ 방향).

```python verify
# (a) 2층 적층 → 반경 압력: 피크비(FEA 3계열) + 엣지롤오프 폭(준해석 BOEF)
# A1. die-scale 2층 회귀 (Choi & Dornfeld 2004, eScholarship 06k6x1vm; DOI:10.1557/proc-816-k4.4)
b0,bEh,bEs,bTh = 6.526892, 0.628464, -0.577953, -0.374445   # 원문 식(1) 코드화 회귀
def HL(Eh,Es,Th): return b0 + bEh*Eh + bEs*Es + bTh*Th
assert bEh>0 and bEs<0 and bTh<0                 # 설계규칙: +경질강성 / -연질강성 / -경질두께
assert abs(bEh) > abs(bEs) > abs(bTh)            # 지배순위 경질강성>연질강성>경질두께
corners = [HL(a,b,c) for a in(-1,1) for b in(-1,1) for c in(-1,1)]
assert abs(max(corners)-8.107754)<1e-4 and abs(min(corners)-4.946030)<1e-4
assert HL(1,-1,-1)==max(corners) and HL(-1,1,1)==min(corners)

# A2. wafer-scale 엣지 피크비 (σ_edge/σ_avg): FEA 3계열
pr_byrne = [1.732, 2.391]      # Byrne 2011 JEM 두 하중구성 (DOI:10.1177/09544054JEM2187)
pr_wang  = 4.47                # Wang et al.(캐리어필름 단독하중), Byrne이 인용
lolin_R  = (1.6766, 2.0760)    # Lo & Lin 2005 R 범위 (DOI:10.1016/j.jmatprotec.2005.01.010, Lv2-1 재현)
assert all(p>1 for p in pr_byrne) and pr_wang>1                 # 엣지 피킹 존재
assert max(pr_byrne) < pr_wang                                  # 링/립실 분담 < 캐리어필름 단독
assert lolin_R[0] <= pr_byrne[0] <= lolin_R[1]                  # Byrne 1.732 ∈ Lo&Lin 밴드
assert pr_wang > 2*lolin_R[0]                                   # 4.47은 밴드 밖(하중경로 차이)

# A3. 엣지롤오프 폭 준해석 (BOEF, Hetényi): 2층 직렬스프링 기초 k_eff=1/(t1/E1+t2/E2)
E_si, h_w, nu_si = 150e9, 0.725e-3, 0.22
D_w = E_si*h_w**3/(12*(1-nu_si**2))               # 웨이퍼 굽힘강성 ~5 N·m
def lam_mm(E2, E1=300e6, t1=1.3e-3, t2=1.3e-3):
    k = 1/(t1/E1 + t2/E2)
    return (4*D_w/k)**0.25*1e3, k
lam_soft,k_soft  = lam_mm(5e6)
lam_stiff,k_stiff= lam_mm(20e6)
assert 2 < lam_soft < 20 and 2 < lam_stiff < 20                 # (i) mm 오더(엣지 배제영역 수 mm)
assert (1.3e-3/5e6) > 10*(1.3e-3/300e6)                        # (ii) 서브패드가 기초 컴플라이언스 지배
assert k_stiff > k_soft and lam_stiff < lam_soft               # (iii) 서브패드 뻣뻣↑→λ↓ (Xin 방향)
print(f"A: H/L {min(corners):.3f}-{max(corners):.3f}; 피크비 Byrne{pr_byrne}<Wang{pr_wang}; λ {lam_soft:.1f}>{lam_stiff:.1f} mm")
print("PASS (a)")
```

재현 요약(§5 B): land 압력 증배 P/(1−GFQ)=×1.25/1.5/1.75(Mu 2016 3종) 하중평형 정합, 컨덕턴스 d0.25/d0.75=0.097로
깊이비(0.333)보다 급감(D³급)을 기존 sim 함수로 재확인.

```python verify
# (b) 그루브 기하 통합 세트: 접촉면적비 + land 압력 증배 + 컨덕턴스(기존 함수 재사용)
import sys; sys.path.insert(0,'sim/tier2_physics')
import pad_groove_wear_flow as W
pads = {'A':(300,1200),'B':(600,1200),'C':(900,1200)}          # (w_um, land_um) Mu 2016
def gfq(w,land): return w/(w+land)
P_nom = 21.0                                                    # kPa 예시
exp = {'A':1.25,'B':1.5,'C':1.75}
for name,(w,land) in pads.items():
    g = gfq(w,land); mult = 1/(1-g)                            # P_land = P_nom/(1-GFQ)
    assert abs(mult-exp[name])<1e-2, f"{name} land 증배 {mult}"
    assert abs(P_nom*(1-g)*mult - P_nom) < 1e-9               # 하중평형 항등식
r = W.rectangular_channel_conductance(0.5,0.25)/W.rectangular_channel_conductance(0.5,0.75)
assert abs(r-0.0973)<0.01 and r < 0.25/0.75                   # 컨덕턴스 깊이비보다 급감(D^3급)
print(f"B: P_land 증배 {[exp[k] for k in 'ABC']}, 컨덕턴스비 {r:.4f}")
print("PASS (b)")
```

재현 요약(§5 C): 동심원 기준 방사 SST −25.4%(Cho et al. 2022, 21.52→16.06 s)·Cu RR +24.6%(Bae et al. 2022, 4051→5047 Å/min),
나선 RR +24%(Rosales-Yeomans et al. 2008) — 방사·나선 두 유형이 ~24%로 수렴.

```python verify
# (c) 그루브 유형별 체류시간·MRR 상대비 (1차 실측 3편)
sst_R0, sst_R32 = 21.52, 16.06                                 # s, Cho 2022 Table 4 (DOI:10.3390/app12094339)
d_sst = (sst_R0-sst_R32)/sst_R0*100
assert sst_R32 < sst_R0 and 24 < d_sst < 27                    # 방사 SST ~25% 단축
f_CG, f_RG32 = 0.52754, 0.67606                                # 신선 슬러리 분율, Bae 2022 (DOI:10.1016/j.mssp.2022.106968)
rr_CG, rr_RG32 = 4051.3, 5047.2                                # Å/min
d_rr_bae = (rr_RG32-rr_CG)/rr_CG*100
assert f_RG32 > f_CG and 23 < d_rr_bae < 26                    # 방사 Cu RR +24.6%
d_rr_spiral, d_cof_spiral = 24.0, 28.0                         # %, Rosales-Yeomans 2008 (DOI:10.1149/1.2963268)
assert 20 < d_rr_spiral < 30 and d_cof_spiral > d_rr_spiral
assert abs(d_rr_bae - d_rr_spiral) < 3                         # 방사·나선 ~24% 교차수렴
print(f"C: 방사 SST-{d_sst:.0f}% RR+{d_rr_bae:.0f}%, 나선 RR+{d_rr_spiral:.0f}%")
print("PASS (c)")
```

재현 요약(§5 D): 기존 sim/tier2에 컨덕턴스·체류·마모단계·GW국소압은 있고, land 증배·엣지 피크비/롤오프폭·유형계수는
부재임을 import로 확인(중복 재구현 방지).

```python verify
# (d) 기존 sim/tier2 중복·충돌 점검
import sys; sys.path.insert(0,'sim/tier2_physics')
import pad_groove_wear_flow as W, gw_pressure_solve as G
have = set(dir(W)) | set(dir(G))
for f in ['rectangular_channel_conductance','conductance_ratio','residence_time_s',
          'slurry_volumes_cm3','wear_stage','groove_wear_flow_state','local_contact_state']:
    assert f in have, f"{f} 없음 — 재사용 대상이 사라졌다"
for absent in ['land_pressure','edge_rolloff','peak_ratio','radial_pressure','groove_type_factor']:
    assert absent not in have, f"{absent} 이미 존재 — 중복 구현"
print("PASS (d): 컨덕턴스/체류/GW국소압 존재; land증배·엣지피크비·유형계수 부재(구현요청)")
```

## 6. 미검증·한계 (정직성)

- BOEF λ의 **절대값**(6–9 mm)은 E_pad 유효압축률(포아송·기공률 의존, **pad-material 소관**)이 불확실해 **미검증(오더·방향만)**.
- 엣지 피크비 절대값은 FEA 설정(리테이너링·립실·하중경로)에 강하게 의존 — 세 계열이 1.7–4.5로 벌어짐. 하나의 상수로
  박지 말고 **하중경로를 명시한 함수**로 이식할 것(§7).
- Choi&Dornfeld 회귀는 die-scale·시뮬레이션(실험검증 없음)·코드화 단위라 절대 H/L은 그 DOE 설정 종속 — **부호·순위만** 이식.
- Xin 리프린트는 **DOI 없음**(업체 리프린트), 그림만 — 폭·경도 방향에만 사용, 수치 인용 없음.
- Bae 2022는 초록·핵심 수치 확인(본문 미확보); Rosales-Yeomans 2008 +24%/+28%은 초록 수치. 둘 다 1차 실측이나 본문
  전표는 미확보 — **크기는 단일 앵커**임을 명시.
- XY 그루브의 유형별 정량 실측표는 미확보(그래프뿐, Guo 2012) — §3 표에서 제외, 방향만.

## 7. 구현 요청 요약 (sim/ 담당 — 상세는 PROFILE.md)

1. `land_pressure_amplification(P_nom, GFQ) -> P_land = P_nom/(1-GFQ)` : GW/3체마모 레이어의 국소압 입력. **Preston 면적평균
   MRR과 곱하지 말 것**(§2 경고). 검증값 GFQ 0.20/0.333/0.429 → ×1.25/1.5/1.75.
2. `edge_pressure_profile(E1,t1,E2,t2,h_w; load_path)` : k_eff=1/(t1/E1+t2/E2), λ=(4 D_w/k_eff)^¼(롤오프폭 스케일),
   엣지 피크비는 하중경로 인자로 [1.7(링분담)–4.5(캐리어단독)]. 검증값 Byrne 1.732/2.391, Wang 4.47, Lo&Lin 1.68–2.08.
3. `groove_type_factor(type)` : 동심원=1 기준, 방사·나선 SST↓/MRR↑. 검증값 Cho SST −25%, Bae RR +24.6%, Rosales RR +24%.

## 8. 출처 요약 (근거등급 EVIDENCE-RULES)

- Byrne, Ahearne, Timoney (2011), Proc. IMechE B 226, "Development and validation of a 200 mm wafer-scale FEM of contact
  pressure distribution in CMP", DOI: 10.1177/09544054JEM2187 — 리프린트 발췌 확인(압력필름 실측검증 FEM), **E3**.
- Choi, Dornfeld (2004), UC Berkeley eScholarship 06k6x1vm; MRS Proc. 816 K4.4, DOI: 10.1557/proc-816-k4.4 — OA 원문 전체,
  2층 DOE 회귀(시뮬레이션), **E4**(계 근접·폐형식이나 실험검증 없음).
- Lo, Lin (2005), J. Mater. Process. Technol. 168, 250, DOI: 10.1016/j.jmatprotec.2005.01.010 — Lv2-1 확보 인용, **E2**.
- Xin, Y.-B., "Modeling of Pad-Wafer Contact Pressure Distribution in CMP", Sensor Products 리프린트(**DOI 없음**) — 방향만, **E5**.
- Cho et al. (2022), Appl. Sci. 12, 4339, DOI: 10.3390/app12094339 — CC-BY 본문 확인, **E2/E3**.
- Bae, Oh, Kim (2022), Mater. Sci. Semicond. Process. 151, DOI: 10.1016/j.mssp.2022.106968 — 초록·핵심수치, **E3**(본문 미확보).
- Rosales-Yeomans, DeNardis, Borucki, Philipossian (2008), J. Electrochem. Soc. 155, H797, DOI: 10.1149/1.2963268 — 초록수치, **E3**.
- Wang, Yang (2007), J. Electrochem. Soc., "Effects of Pad Grooves on CMP", DOI: 10.1149/1.2716558 — 초록(접촉면적↓ 방향), **E5**.

## 9. 자기시험 근거 메모
Q: 왜 die-scale H/L과 wafer-scale 피크비는 "두께" 부호가 반대인가? A: 지배 물리가 다르다 — die-scale은 경질층 국소 굽힘
(경질 두께↑→덜 휘어 H/L↓, Choi&Dornfeld), wafer-scale은 엣지 기하 불연속(총 두께↑→엣지 피크↑, Xin·Lo&Lin). 스케일이
다른 두 지표를 하나의 부호로 통합하면 안 된다.
Q: P_land=P/(1−GFQ)를 Preston에 곱하면 왜 틀리나? A: P_land는 land 국소 접촉응력(GW·3체마모 입력)이고, Preston 면적평균
MRR은 명목압 P로 계산한다. 접촉면적 감소가 지배하면 net MRR은 오히려 낮아진다(Wang&Yang 2007) — 국소압 상승과 면적평균
MRR을 혼동하면 안 된다.
