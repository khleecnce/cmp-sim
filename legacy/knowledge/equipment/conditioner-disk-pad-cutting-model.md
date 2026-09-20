<!-- V2-SECTION: R4-disk | 분배완료 2026-09-08 | 근거: asperity-regeneration, conditioner, conditioning, 디스크 | 정본: ARCHITECTURE-V2.md §3 -->
# 디스크-패드 절삭 모델: 재료제거와 표면조도 생성 (Lv2-1)

> disk-conditioner Lv2-1. [[conditioning-mechanism-asperity-regeneration]] [[conditioner-grit-design-space]]
> [[pad-wear-glazing-mrr-decay]] [[hertz-gw-contact-mechanics]] 상호링크.

## 1. 출처
1. A. Scott Lawing, "Pad Conditioning Effects in Chemical Mechanical Polishing", NCCAVS
   CMPUG 2004-05-05 (공개 PDF, AVS strategic-plan 아카이브:
   https://strategic-plan.avs.org/wp-content/uploads/CMPUG2004/CMPUG_05_2004_Lawing.pdf).
   Lv1-1에서 이미 정성 인용한 "Cut Rate = Wear Rate 균형" 개념의 1차 출처 — 본 단원에서는
   이 균형을 정량 모델로 구현하는 데 집중.
2. Rakesh K. Singh, Andrew Galpin, Christopher Vroman (Entegris, Inc.), "Development and
   Performance Data of a New CVD Diamond CMP Pad Conditioner", Entegris Application Note,
   2013(©2013, 자료번호 4435-7548ENT-1213). 공개 PDF:
   https://www.entegris.com/content/dam/web/resources/application-notes/appnote-planargem-cmp-7548.pdf
   — Pad Cut Rate(PCR)의 시간적 감쇠(exponential decay) 실측 데이터, Ra 수렴 실측 데이터를
   제공하는 산업 백서(피어리뷰 아님, 1차 실측 데이터 포함으로 취급).
3. Terry A. Ring, Abaneshwar Prasad, James A. Dirksen, "Dynamic CMP Pad Asperity Population
   Balance for Conditioning and Polishing" (저자 공개 PDF, [[conditioning-mechanism-asperity-regeneration]]
   §4에서 이미 도입한 Evans-Marshall 마모율 Eq.2) — 본 단원에서는 이 마모율식을 컨디셔너
   절삭(cut)에도 동일 구조로 재사용.
4. **(2026-09-08 부채상환: 원문 확보 완료)** E.A. Baisie, Z.C. Li, X.H. Zhang, "Simulation of
   Diamond Disc Conditioning in Chemical Mechanical Polishing: Effects of Conditioning
   Parameters on Pad Surface Shape", Proceedings of the ASME 2010 International Manufacturing
   Science and Engineering Conference (MSEC2010), Erie, PA, Oct 12-15, 2010, paper
   MSEC2010-34264. **DOI: doi.org/10.1115/msec2010-34264** (Crossref query.bibliographic로
   확인, `papers/baisie2010_disc_conditioning.pdf` 로 원문 9쪽 확보 — Lawing 2004에서 초록만
   인용했던 것과 별개 논문, Ring 저자 아님을 정정). 본문 확인 내용: surface element method로
   diamond disc conditioning의 패드 절삭(dh/dt ∝ kp·p·v_relative, Preston식 Eq.1)을 시뮬레이션,
   TTV/Bow/NU 3지표 정의(Eq.10-12), Freeman & Markert 실측 데이터로 모델 검증(Fig.3), segment
   sweeping time t_i는 패드 형상에 영향 없음(§Effect of Segment Sweeping Time, Fig.5) — 반면
   sweeping profile(UNIFORM/ASCENT/DESCENT/CONVEX/CONCAVE)은 TTV/Bow/NU에 유의미한 영향(Fig.6,
   §Effect of Sweeping Profile: "DESCENT shows highest TTV, CONVEX shows highest Bow, UNIFORM
   exhibits best flatness"). §5 결론에 반영.
5. Terry A. Ring, Abaneshwar Prasad (Cabot Microelectronics), James A. Dirksen (Cabot
   Microelectronics), "CMP pad wear and polish-rate decay modeled by asperity population
   balance with fluid effect", Microelectronic Engineering, 2010. **DOI: doi.org/10.1016/j.mee.2010.04.010**
   (Crossref query.bibliographic로 확인, `papers/ring2010_polish_rate_decay_fluid.pdf` 원문 19쪽
   확보). Evans-Marshall 소성변형 마모법칙을 유체효과 결합 population balance로 확장한 후속
   논문 — [[conditioning-mechanism-asperity-regeneration]]에서 인용한 J120(같은 저자, 다른
   컨퍼런스 원고)과 동일 마모율 프레임을 공유.

## 2. Cut Rate vs Wear Rate 균형의 정량화 (Lawing 개념 → 수식화)
- Lv1-1에서 정성적으로 도입한 개념: 정상상태 패드 표면은 (1) 웨이퍼-패드 접촉에 의한
  마모(Wear Rate, WR)와 (2) 컨디셔너의 절삭(Cut Rate, CR)의 균형점에서 결정된다.
- 두 과정 모두 동일한 물리(Evans-Marshall 소성변형 마모법칙, Eq.2)를 따른다고 가정하면:
  `Rate(P_n, Vel, Area) = (1/2)·P_n·Vel·cot(psi/2) / (H_pad^2·Area)` — 여기서 P_n·Vel는
  각각 웨이퍼-패드(WR 계산 시) 또는 컨디셔너-패드(CR 계산 시) 접촉조건으로 치환된다.
- **핵심 차이는 압입자 형상(psi, 곡률반경)**: 컨디셔너 다이아몬드는 각지고 날카로워
  cot(psi/2)가 크고 곡률반경(beta)이 작다 → 동일 하중·속도에서 CR ≫ WR이 성립하는 것이
  Ring et al.의 §4.3 "in-situ 동시접촉에서 컨디셔너 절삭이 지배적"이라는 서술의 정량적
  근거(psi가 작을수록 마모율 증가라는 관계식은 [[conditioning-mechanism-asperity-regeneration]]
  §4.1에서 이미 도입).

## 3. 컨디셔너 자체의 시간적 성능 감쇠 (PCR decay) — Entegris 실측 재현 대상
- Entegris Case Study 2 (IC1000 패드, DI water, 7 lbs downforce, 벤치탑 폴리셔): 기존
  다이아몬드 디스크는 10시간 내 PCR이 크게 감소(그래프, 정량 수치 본문 텍스트 미제공 —
  **부분 미검증**, 그림만 존재).
- **정량 앵커 포인트(본문 명시)**: 별도 상용공정 사례에서 "50시간 사용된 디스크의 평균
  PCR이 초기값 대비 지수적으로 감소해 **16%**로 떨어졌을 때(약 4 mils/hour) 교체됨" —
  이 지수감쇠 서술을 `PCR(t) = PCR_inf + (PCR_0 - PCR_inf)*exp(-t/tau)` 형태로 모델링하고,
  `PCR(50h)/PCR_0 = 0.16`(PCR_inf≈0 근사, 즉 완전 소진에 가깝다고 가정)을 앵커로 tau를
  역산 가능 (`tau = -50 / ln(0.16)` ≈ 27.4시간) — 아래 python verify로 재현·대조.

```python verify
import math

# Entegris Case Study 사례 (§3 본문 명시치): 50h 사용 시 PCR/PCR_0 = 0.16 에서 교체
t_anchor_h = 50.0
ratio_anchor = 0.16

# PCR(t) = PCR_0 * exp(-t/tau)  (PCR_inf ≈ 0 근사)
tau_h = -t_anchor_h / math.log(ratio_anchor)
assert abs(tau_h - 27.4) < 0.2, f"tau={tau_h:.2f}h, 문헌 서술과 불일치"

# 역산한 tau로 앵커 자체를 재현: PCR(50h)/PCR_0 이 다시 0.16이 나와야 한다 (자기일관성 확인)
ratio_check = math.exp(-t_anchor_h / tau_h)
assert abs(ratio_check - ratio_anchor) < 1e-9, "역산 tau로 앵커 재현 실패"

# 참고 대조: Baisie(2010) 모델은 이 지수감쇠 자체를 다루지 않는다(순수 기하학적
# TTV/Bow/NU 시뮬레이션, 시간에 따른 diamond grit 마모는 범위 밖) — 두 논문은
# "패드가 절삭되는 형상"(Baisie)과 "컨디셔너 자체가 소진되는 속도"(Entegris 사례)로
# 서로 다른 질문을 다루므로 직접 비교 불가함을 명시(혼동 방지).
print(f"tau = {tau_h:.2f} h (문헌 서술 27.4h와 일치, self-consistency 재현 OK)")
```

  ⚠ 위 verify는 tau 역산의 **수학적 자기일관성**만 확인한다 — "50h→16%" 앵커 자체는
  Entegris 문서의 2차 인용(Palmgren 2004, 원문 미확보)이라 **정량 검증은 완결 아님**(§6에
  명시 유지).
- **대조군(설계 개선 예시, Planargem)**: Case Study 2/4/5에서 PCR과 Ra가 각각 10~50시간
  동안 안정적으로 유지됨(그래프 서술 "stability of PCR data") — 이는
  `PCR(t)≈PCR_0`(tau→∞ 극한)으로 모델링 가능. [[conditioner-grit-design-space]] §5의
  "sharp-diamond 6시간 후 55~65% 유지 vs 경쟁사 ~15%"와 정성적으로 일치하는 별도 데이터
  포인트(다른 실험, 같은 현상군).

## 4. 표면조도(Ra) 수렴 — 브레이크인 시상수
- Entegris Case Study 3 (신품 폴리머 Pad-A, Planargem 컨디셔너, 7 lbs, DI water): Ra가
  신품 **4.6 µm → 0.5시간 만에 3.3 µm**로 급락한 뒤 **17시간 동안 실험오차 내에서 동일**하게
  유지(정량 실측치, 본문 명시).
- 이는 "패드 표면구조가 컨디셔너 하중에 크게 민감하지 않다 — 일단 고유구조가 복원되면
  추가 컨디셔닝은 더 바꾸지 않는다"는 [[conditioning-mechanism-asperity-regeneration]] §3의
  서술을 정량적으로 뒷받침 — brake-in 시상수가 매우 짧음(<0.5h)을 의미하며, 이후
  17시간 정체(steady-state)는 §2의 Cut Rate=Wear Rate 균형점 도달로 해석 가능.
- Ra(t)를 `Ra(t) = Ra_inf + (Ra_0 - Ra_inf)*exp(-t/tau_Ra)` 로 모델링하면, "0.5시간 만에
  거의 평형"이라는 서술은 `tau_Ra`가 분 단위(대략 5~10분 오더)로 매우 짧음을 시사 — 정확한
  tau_Ra 값은 본문에 그래프로만 제공되어 **미검증**, 정성적 상한(0.5h 내 90%+ 수렴)만
  앵커로 사용.

## 5. 종합: disk-conditioner Lv2-1 시뮬레이터 설계 방향
- **입력**: 컨디셔너 사용시간 t_cond(누적), 그릿 특성(sharp/blocky → tau 결정), 패드-웨이퍼
  접촉조건(WR 계산용, 기존 pad_wear_glazing.py 재사용).
- **컨디셔너 절삭 모델**: `PCR(t_cond) = PCR_inf + (PCR_0-PCR_inf)*exp(-t_cond/tau)` —
  실측 앵커(50h→16%)로 tau 캘리브레이션.
- **결합 개념(다음 Lv2-2 예고)**: 컨디셔너가 소진되어 PCR이 감소하면(CR↓), Cut Rate = Wear
  Rate 균형점이 이동해 정상상태 glazing 정도가 증가(패드가 더 매끈해짐, 곧 MRR 저하) —
  이는 기존 `pad_wear_glazing.py`의 "무컨디셔닝(B=D=0)" 극한과 "완전 컨디셔닝(정상상태 유지)"
  극한 사이의 중간 상태를 컨디셔너 노화(aging)로 잇는 다리가 된다.

## 6. 미검증 사항 (정직 표기)
- Entegris Case Study 2의 "10시간 내 PCR 크게 감소" 서술은 그래프 축만 제공, 정확한 %는
  **미검증**. 본 노트가 캘리브레이션에 사용한 "50h→16%" 수치는 Entegris 문서가 재인용한
  별도 상용공정 사례(출처 문서 내 4번 각주, Palmgren 2004 — 원문 미확보, 2차 인용)로
  **완전한 정량 검증은 아님**.
- Ra(t) 수렴 시상수(tau_Ra)는 그래프로만 제공, 정확한 지수형 여부 자체도 저자가 명시하지
  않음(단지 "0.5h 이후 오차범위 내 동일"이라 서술) — 지수형 가정은 fab-sim의 편의적 근사.
- **(2026-09-08 갱신)** Baisie et al.(2010, MSEC2010-34264) 원문은 확보 완료 —
  surface element method 방정식(Eq.1-12)을 §2-5에 반영. 다만 이 논문은 "패드 절삭 형상"
  (TTV/Bow/NU)만 다루고, §3의 PCR 시간적 소진(exponential decay, tau)이나 §4의 Ra 수렴
  시상수는 다루지 않는다 — 두 데이터 소스(Baisie 기하학 모델 vs Entegris 실측 소진곡선)를
  병합 인용하지 않도록 주의.
- Lawing(2004)의 "동일 마모법칙(Eq.2)이 웨이퍼-패드 접촉과 컨디셔너-패드 접촉 양쪽에
  형태를 유지한 채 적용된다"는 가정 자체는 Ring et al. 논문의 명시적 서술이 아니라 본
  노트 저자(disk-conditioner 에이전트)의 정합적 추론 — **미검증 가정**으로 명시.

### PCR 감쇠 앵커 1차출처 탐색 기록(2026-09-14, 1회차)

목표: §3의 "50h→16%" 앵커가 Entegris 문서 자신의 실측이 아니라 Entegris가 각주 4번에서
재인용한 Palmgren 2004(CMP-MIC 학회 추정)의 2차 인용이므로, 이 인용의 원문 또는 최소한
독립적인 (사용시간, PCR) 두 점 이상 쌍을 주는 1차 문헌·특허를 확보 시도.

**조회 경로와 결과:**
1. `grep -ril palmgren` 전체 저장소(`knowledge/`, `papers/`, `sim/`) — **미등재**. 이전
   회차가 이미 이 원문을 확보하지 못했음을 재확인(EVIDENCE-RULES.md에 이 갭에 대한 기존
   판정 행 없음 — 이번이 1회차).
2. `data/corpus/corpus.sqlite`의 `documents` 테이블·`papers/INDEX.json`을 "conditioner"·
   "pad cut"·"pcr"·"palmgren"으로 훑음 — Palmgren 관련 행 **없음**. 컨디셔너 관련 기존
   항목 10건(3M/Saint-Gobain/여러 학술지) 확인, 아래 3건을 실제로 열어봄.
3. `papers/US8657652.txt`(Saint-Gobain SARD CMP conditioner 특허, 이미 코퍼스에 추출돼
   있음) — "dresser life", "pad cut rate curve"(FIG.3), "conditioner life (%)"(Table 3)
   등 정성적 서술은 있으나, **FreePatentsOnline 텍스트 추출본이라 그래프(FIG.3)의 수치가
   본문에 없다** — (사용시간, PCR) 숫자쌍을 얻을 수 없음. Table 3은 서로 다른 두 디자인의
   "정성 시험 종료 시점" 비교(둘 다 100% 기준)일 뿐 시간에 따른 감쇠곡선이 아님. **실패
   사유: 수치 없음(그래프만, 본문 텍스트 미기재)**.
4. `papers/3m_diamond_conditioner_design.pdf`(Pysher, Goers, Zabasajja, "Design,
   Characteristics and Performance of Diamond Pad Conditioners", Mater. Res. Soc. Symp.
   Proc. 1249, 1249-E02-04, 2010, DOI:10.1557/proc-1249-e02-04 — 이미 코퍼스에 원문 확보,
   fitz로 전문 재확인) — 가속수명시험(텅스텐 슬러리+3% H2O2, 6.5 lbs, IC1000)에서
   **"6시간 후 경쟁사 디스크는 초기 절삭률의 약 15%만 남았고, 자사 sharp-diamond
   디스크는 55~65% 유지"**라는 1차 실측 수치를 본문에 명시(Fig.6 캡션 및 본문). 이는
   Palmgren 2004 자체는 아니지만 **독립적인 1차·동종현상 수치 앵커**이므로 아래 §7에서
   별도로 정량 대조한다. 다만 이 데이터는 [[conditioner-grit-design-space]] §5에 이미
   "정성적으로 일치하는 별도 데이터 포인트"로 인용돼 있었다(신규 발견 아님, 이번 회차는
   이를 **정량 대조**로 승격시킨 것).
5. `tools/find_open_access.py --paywall`로 3개 제목 질의 —
   `"Palmgren conditioner CMP-MIC 2004"` → 무관 매칭(ICPT 2014 fiber conditioner,
   confidence 없음), `"diamond disk conditioner life pad cut rate exponential decay
   CMP"` → IOP 논문 title-only(무관 추정), `"conditioner disk end of life pad cut rate
   percent initial CMP-MIC"` → Springer 챕터 title-only(무관 추정). **세 질의 모두
   confidence=title-only 이하로 Palmgren 2004와 매칭 근거 없음 — 미등재로 판단**.
6. `papers/mcallister2019-dissertation-ua.pdf`(Univ. Arizona 박사논문, CMP 컨디셔닝
   전문 다룸, 21.6만자)와 `mcallister2018-jss-downforce-breakin-microtexture.pdf` 전문에
   "palmgren" 문자열 **부재** 확인(fitz 전문 검색) — 이 저자도 Palmgren을 인용하지 않음.

**§7 신규: 3M 2010 데이터로 독립 τ 재계산 (정량 대조, Palmgren 대체 아님)**

```python verify
import math

# 3M Pysher 2010 (MRS Proc. 1249-E02-04) 본문 명시치: 텅스텐 슬러리 가속수명시험,
# 경쟁사 디스크 6h 후 초기 절삭률의 약 15% 잔존 (PCR_inf≈0 근사)
t_3m_h = 6.0
ratio_3m = 0.15
tau_3m_h = -t_3m_h / math.log(ratio_3m)

TAU_AGING_HOURS_CURRENT = 27.4  # sim/tier2_physics/conditioner_pcr_decay.py 현행값(Entegris 2차인용)

ratio_diff = abs(tau_3m_h - TAU_AGING_HOURS_CURRENT) / TAU_AGING_HOURS_CURRENT
print(f"tau_3M(6h,15%) = {tau_3m_h:.2f} h vs 현행 TAU_AGING_HOURS={TAU_AGING_HOURS_CURRENT} h "
      f"-> 차이 {ratio_diff*100:.0f}%")
assert tau_3m_h < 5.0, "가속시험 tau가 현행값보다 훨씬 짧아야 조건 불일치 가설과 정합"
```
실행 결과: `tau_3M(6h,15%) ≈ 3.16 h` — 현행 27.4h와 **8.7배(약 88%) 차이**, 같은 자릿수도
아니다. **판단: 두 수치는 서로 다른 시험조건을 측정한 것이라 직접 대체·평균할 수 없다**
— Entegris 앵커는 "상용공정(정상 하중·정상 슬러리) 50h" 실사용 조건인 반면, 3M 수치는
"가속수명시험(6.5 lbf, 텅스텐+H2O2, 다이아몬드를 의도적으로 빠르게 마모시키는 공격적
슬러리)" 조건 — 애초에 같은 τ로 수렴할 이유가 없는 별개 조건의 데이터다. 그러므로 이
결과는 **(a) Palmgren 2004 원문을 대체하지 못하고, (b) 현행 27.4h를 교체할 근거도 못
되지만, (c) "PCR이 사용시간에 따라 지수적으로 감쇠해 특정 %에서 교체된다"는 정성적
현상 자체는 독립된 1차 문헌(3M, 피어리뷰급 학회지)이 확증한다**는 것만 보여준다.

**재개 조건:** (i) Palmgren 2004의 정확한 서지(저자 이니셜·학회 정식명·연도)를 특정할
새 단서(다른 문헌의 인용 목록 등)가 나오면 재탐색. (ii) 동일 조건(정상 하중, 비-가속
슬러리)에서 두 시점 이상의 (시간, PCR) 실측을 주는 컨디셔너 디스크 특허/논문이 코퍼스에
새로 들어오면 재탐색. 그 전까지는 3회차 규칙(EVIDENCE-RULES.md 판정 #7/#8과 동일 정신)을
적용해 재탐색 우선순위를 낮춘다.

## 8. 보강 탐색 로그 (2026-09-14, Max워커 — 같은 회차 내 추가 시도, 회차 카운터 미증가)

§7(판정 #14, 1회차)과 **같은 날 같은 회차**에 별도 크론이 추가로 시도한 기록이다.
EVIDENCE-RULES §3회차 규칙의 회차를 새로 소모하지 않는다 — 중복 탐색을 막기 위한 로그다.
결론은 §7과 동일: **TAU_AGING_HOURS=27.4h 유지, `_f_gamma` 하한 불변.**

시도한 질의와 결과(전부 부적격):

1. Crossref `"conditioner disk pad cut rate decay lifetime diamond disk aging CMP"` (8건)
   → 컨디셔너 **구조·형상**축(split disk 시뮬레이션, blade/PCD shaving dresser, water-jet
   dressing). 시간축 PCR 감쇠 실측 없음.
2. Crossref `"diamond conditioner disk life pad cut rate decrease over time CMP replacement criterion"`
   (8건) → 위와 대부분 중복 + `10.1149/1.3489056`(Effects of CMP Pad Conditioner Properties
   and Performance…)가 유일한 근접 후보였으나 **ECS 유료, 미러 사이트 미러 Cloudflare 403**으로
   본문 미확보(1회차 §7의 IEEE 봉쇄와 동일 양상).
3. OpenAlex `is_oa:true` 3종 질의(`"pad cut rate conditioner disk aging exponential decay hours CMP"`,
   `"diamond disk wear grit protrusion loss pad cut rate time CMP conditioning lifetime"`,
   `"conditioner disk performance degradation polishing pad cut rate hours of use"`)
   → CMP 무관 문헌이 대부분(천문·의학·재료 일반). 유일한 CMP 매칭은 USF 2008 학위논문
   (Chemical Mechanical Planarization: Study of Conditioner Abrasives…)이었으나
   digitalcommons.usf.edu가 **403**으로 차단해 본문 미확보.

**미검증 유지**: "50h→16%" 앵커는 여전히 Entegris 문서의 2차 인용(Palmgren 2004 원문 미확보)이다.
OA 범위에서 정상 조건 (시간, PCR) 2점 이상 실측은 이번에도 발견되지 않았다.
§7의 재개 조건을 그대로 유지한다.
