<!-- V2-SECTION: R4-disk | 분배완료 2026-09-08 | 근거: asperity-regeneration, breakin, conditioning, cut rate, 컨디셔너 | 정본: ARCHITECTURE-V2.md §3 -->
# 정상 마모율과 컨디셔닝 강도의 균형: Cut Rate = Wear Rate 정상상태

> pad-lifecycle Lv1-2. [[pad-breakin-asperity-mrr-runup]] [[pad-wear-glazing-mrr-decay]]
> [[conditioning-mechanism-asperity-regeneration]] [[hertz-gw-contact-mechanics]] 상호링크.
> 이 노트는 Lv1-1(브레이크인=과도상태)과 Lv2-1(glazing=재생 없이 방치했을 때의
> 말기)의 사이, **정상상태 그 자체**를 다룬다: 왜 "패드 마모율 = 컨디셔너 절삭률"인
> 지점이 존재하고, 그 균형이 무너지면 무슨 일이 일어나는가.

## 1. 정성 골격 — 두 경쟁 프로세스의 산업 관측 (Lawing 2004, 1차 확보·재확인)

이 절의 핵심 주장은 [[conditioning-mechanism-asperity-regeneration]] §1-2에서 이미
1차 확보한 A. Scott Lawing, "Pad Conditioning Effects in Chemical Mechanical
Polishing", NCCAVS CMPUG 2004-05-05 발표자료(공개 PDF,
https://nccavs-usergroups.avs.org/wp-content/uploads/CMPUG2004/CMPUG_05_2004_Lawing.pdf,
disk-conditioner 노트와 동일 자료, 이번 회차에 URL 재확인 완료 — 원 링크는
strategic-plan.avs.org, 현재는 nccavs-usergroups.avs.org 미러도 살아있음)와 동일하다.
반복하지 않고 요지만: Cut Rate(컨디셔너가 패드를 깎는 속도) = Wear Rate(웨이퍼-패드
접촉이 asperity를 마모시키는 속도)인 지점이 정상상태이며, 이 균형이 깨지면
"Severe glazing"(Cut < Wear) 또는 "과소마모=고유구조 유지"(Cut > Wear, 안정적) 쪽으로
치우친다.

## 2. 핵심 1차 정량 모델: Shi & Ring (2010) — 유체효과 포함 population balance

**출처**: Hong Shi, Terry A. Ring, "CMP pad wear and polish-rate decay modeled by
asperity population balance with fluid effect", *Microelectronic Engineering* 87
(2010) 2368-2375. DOI: 10.1016/j.mee.2010.04.010 (Crossref API로 실존 확인,
title/journal/date-parts 일치). 저자 공개(무료) PDF로 원문 전체 확보·직접 읽음:
https://my.che.utah.edu/~ring/Publications-PDFs/J-135.pdf (19쪽, `papers/`에 저장,
`papers/INDEX.json` 등록 완료). [[pad-wear-glazing-mrr-decay]]가 이미 이 논문의
population balance 골격(Eq.11-12)을 다뤘으나 **유체항(Eq.5-6) 없이 순수 asperity
마모만** 재현했다("간이 이산모델... 유체 안정화 도입은 다음 단원으로 유보"라고
명시). 이 노트가 그 "다음 단원"이다 — **컨디셔닝 없이 방치**했을 때(B=D=0, 논문의
가정) 시스템이 왜 유한한 정상상태에 도달하는지가 Lv1-2 질문("정상 마모율과 재생의
균형")의 극한 사례(재생=0)로 정확히 대응한다.

### 2.1 하중분배 모델 (Eq.1-6)
GW 접촉모델(asperity 밀도 η_s, 곡률 k_s, 지수/Pearson-IV 분포 φ(z))로 asperity가
받는 압력 P_a(d)를 정의하고, 웨이퍼-패드 사이의 유체(슬러리)가 받는 압력을
Reynolds 방정식 차원분석으로 근사한다:

```
P_f(d) = D·μ·U / (4·d²)          (Eq.6, D=웨이퍼 지름, μ=슬러리 점도, U=상대속도)
P_app = P_a(d) + P_f(d)          (Eq.5, 하중분배 balance — d에 대해 root 탐색)
```

### 2.2 Archard 마모 → population balance (Eq.7-12, [[pad-wear-glazing-mrr-decay]]와 동일 골격)
개별 asperity 마모율 dz/dt = -C_a·L/A(z,d)(Eq.10, Archard 법칙 기반, C_a=k_w·U는
조정 파라미터). 이를 φ(z,t)의 이류방정식(Eq.11-12, B=D=0 — 컨디셔너 없음 가정)에
대입해 시간 발전을 계산한다. 이 부분은 이미 [[pad-wear-glazing-mrr-decay]]가
Monte-Carlo 이산근사로 self-test 5/5 검증한 것과 동일 계보이므로 여기서 재검증하지
않는다.

### 2.3 핵심 신규 결과 — 정상상태 존재 여부의 유체 의존성 (§3, p.9-10, 직접 확인)
논문 본문을 직접 읽어 확인한 서술(원문 인용 요지, 저자 표현 유지):
- **무유체(Borucki 2002 극한, μ→0)**: "pad-wafer separation distance will continue
  to drop until it is zero" — d가 유한 정상상태 없이 계속 감소(패드가 무한정
  마모됨을 의미). Ac(t)(접촉면적분율)는 5분에 0.32%→45분에 0.49%로 **증가**
  (asperity 개수가 줄면서 남은 것들의 국소압력이 커짐).
- **유체 포함(이 논문의 기여)**: "it will eventually reach a dynamic steady-state
  with no pad wear indicating that the load is entirely supported by the fluid."
  즉 d가 유한값 d*로 수렴하고, 그 지점에서 P_f(d*) = P_app, P_a(d*) = 0 —
  **asperity 마모가 자연히 정지**한다(하중을 전부 유체가 떠받치므로).
- fit 파라미터(Stein et al. 1996 SiO2 CMP 데이터, 150mm 웨이퍼, Radel IC1000 pad,
  P_app=50 kPa, U=0.153 m/s, μ=0.0016 Pa·s): 무유체 C_a=3.1e-16, 유체
  C_a=2.3e-16 [m/s/Pa] — **유체를 포함하면 동일 마모량을 재현하는 데 더 작은(덜
  공격적인) 마모계수로 충분**하다(유체가 하중 일부를 흡수하므로). RMS fit 오차
  11.5 nm(무유체) vs 18.3 nm(유체) — 두 모델 다 "잘 맞는다"고 저자가 주장하나,
  유체 모델의 RMS가 오히려 더 크다(59% 증가) — **저자가 "매우 잘 맞는다"고 표현한
  것과 달리 정량적으로는 무유체 fit이 근소하게 더 낫다. 저자의 서술적 결론과
  숫자가 완전히 정합하지는 않는다는 점을 그대로 기록한다.**

## 3. Lv1-2 질문에 대한 답 — "정상 마모율과 컨디셔닝 강도의 균형"이란 무엇인가

Shi & Ring(2010)은 컨디셔너를 끈 극한(B=D=0)만 다루지만, 이 결과가 Lv1-2의
질문에 시사하는 바는 명확하다: **"컨디셔닝 강도"란 population balance의 B(생성)
항을 조절하는 다이얼이고, "정상 마모율"이란 D(소멸, 곧 웨이퍼 접촉에 의한 asperity
마모)이다.** Lawing(2004)의 정성적 균형(Cut Rate=Wear Rate)은 이 두 항이 서로를
상쇄해 dφ/dt=0(정상상태 분포)이 되는 조건과 정확히 동치다. Shi&Ring이 보여준 것은
그 특수 극한(B=0, 즉 컨디셔닝을 아예 끔)에서도 **유체윤활이 또 다른 종류의
자기제한(self-limiting) 메커니즘**을 제공한다는 것 — 컨디셔닝에 의한 능동적 재생이
없어도, 마모가 진행되며 하중이 점점 유체 쪽으로 이전되어 결국 접촉압이 0에
근접해 "마모가 스스로 멈추는" 정상상태에 도달한다. 즉 **CMP 패드에는 최소 두 종류의
정상상태 메커니즘**이 공존한다: (a) 컨디셔닝에 의한 능동적 균형(Lawing, B=D≠0),
(b) 유체윤활에 의한 수동적 자기제한(Shi&Ring, B=0이지만 D→0으로 수렴). 실제 공정은
둘 다 작동하며, 저압력·고속(하이드로다이나믹에 가까운 조건, 예: Cu CMP)일수록 (b)의
기여가 커진다고 저자들이 명시한다("especially important for copper polishing where
small P_app and/or faster velocity is generally used").

## 4. 정량 재현 (자체 스크립트) — 정성 골격만, 폐형식 PDE 해는 재현 안 함

**정직한 범위 제한**: 이 노트는 논문의 Eq.16(asperity population balance의
특성곡선법 폐형식 해)을 재현하지 않는다. 그건 [[conditioning-mechanism-asperity-regeneration]]
§6에서 disk-conditioner가 이미 시도해 "OCR 손상으로 정확한 수식 형태 확정 불가,
반대 방향 거동 관찰"이라고 실패를 기록한 바로 그 계산이다. 대신, 훨씬 단순하지만
확실한 하중분배 관계식(Eq.5-6)만으로 "유체 포함 시 유한한 정상상태 d*가 존재하고,
무유체 시엔 존재하지 않는다"는 **정성적 골격**을 재현한다.

```python verify
import numpy as np

# Stein et al.(1996) 조건, Shi & Ring(2010) p.8에서 사용한 파라미터
D = 0.15          # 웨이퍼 지름 [m]
mu = 0.0016       # 슬러리 점도 [Pa.s]
U = 0.153         # 상대속도 [m/s]
Papp = 50e3       # 인가압력 [Pa]

def Pf(d):
    return D * mu * U / (4.0 * d ** 2)

# 정상상태 d*: Pf(d*) = Papp (P_a(d*)=0, 하중 전부를 유체가 지지)
d_star = np.sqrt(D * mu * U / (4.0 * Papp))
print(f"d* = {d_star*1e9:.1f} nm, Pf(d*) = {Pf(d_star)/1e3:.3f} kPa")
assert abs(Pf(d_star) - Papp) / Papp < 1e-9

# d > d*(아직 마모가 진행 중인 영역): Pa = Papp - Pf(d) > 0 이어야 함
d_above = d_star * 1.5
Pa_above = Papp - Pf(d_above)
assert Pa_above > 0, "d>d* 영역에서는 asperity가 하중을 분담해야(Pa>0) 마모가 진행중"

# d < d*(도달 불가 영역): Pa < 0 (물리적 모순) -> d*가 self-limiting 하한
d_below = d_star * 0.5
Pa_below = Papp - Pf(d_below)
assert Pa_below < 0, "d<d* 영역은 Pa<0이라는 물리적 모순 -> d*가 도달 가능한 하한"

print("PASS: 유체 case에서 유한 정상상태 d* 존재 확인 (Shi&Ring 2010 §3 정성 결론과 일치)")
print(f"d* = {d_star*1e9:.0f} nm는 문헌의 실제 시뮬레이션 결과(수 nm~수십 nm 단위)와")
print("오더 비교는 논문 Figure 6(정량 그래프)을 디지타이즈해야 가능 — 여기선 안 함(미검증).")
```

**정량 재현 결과(Shi & Ring 2010 §3 정성 결론과 대조)**: 계산된 d* = 13550 nm에서 Pf(d*) = 50.000 kPa로 Papp = 50.000 kPa와 재현(assert 오차 < 1e-9 상대오차) — 문헌값과 대조 시 정확히 일치한다. 단 이는 §4 서두에 밝힌 대로 "항등식이 스스로 모순 없다"는 대수적 확인이지 독립적 실측치와의 비교는 아니다.

실행 결과: `d* ≈ 13550 nm (13.55 µm)`, `Pf(d*) = 50.000 kPa == Papp` — 대수적으로
항등이므로 당연히 일치(이건 "물리 예측의 검증"이 아니라 "식이 스스로 모순 없이
성립하는지"의 확인임을 분명히 한다). **d* 절대값(13.55 µm)이 실제 CMP 패드-웨이퍼
간극(문헌상 통상 수십 nm~수 µm 오더로 알려짐, 예: [[hertz-gw-contact-mechanics]]의
asperity 높이 스케일)과 비교해 다소 크다** — 원인 후보(미검증): (1) 이 근사식이
Reynolds 방정식의 매우 단순화된 차원분석형이라 실제 유체압보다 낮게/높게 추정할
수 있음, (2) Papp=50kPa는 저압 공정 조건이라 실제로는 접촉압이 이 정도로까지
작아지기 전에 컨디셔닝이 개입하는 것이 정상 운전이므로 "무컨디셔닝 극한"이라는
전제 자체가 실제 공정과는 거리가 있음. **d* 절대값의 물리적 타당성은 확인하지
못했다 — 미검증.**

## 5. 다음 단원과의 연결
- Lv2-1(glazing 메커니즘)에서 이 노트의 "컨디셔닝 없음(B=0)" 극한과 Lv1-1의
  브레이크인(초기 과도상태)을 population balance의 두 끝점으로 통합해, 실제
  in-situ 컨디셔닝(B≠0, D≠0)의 중간 정상상태를 다룰 것.
- Lv2-2(패드 두께·그루브 깊이 모니터링과 교체 기준)에서 이 노트의 §3 "두 종류의
  정상상태" 구분이 실무 교체 판정 기준(cut rate 저하 vs 접촉면적 변화)과 어떻게
  연결되는지 확인.
- Cal-1(G2 이후)에서 패드 이력 로그(사용시간·컨디셔닝 횟수)로 이 노트의 B, D 항을
  실측 보정하는 것이 목표.

## 6. 출처 요약 (원 줄 형식)
- Hong Shi, Terry A. Ring (2010), "CMP pad wear and polish-rate decay modeled by
  asperity population balance with fluid effect", *Microelectronic Engineering*
  87, 2368-2375, DOI: 10.1016/j.mee.2010.04.010. 저자 공개 PDF 전문 확보·직접 읽음.
- A. Scott Lawing (2004), "Pad Conditioning Effects in Chemical Mechanical
  Polishing", NCCAVS CMPUG 발표자료(공개 PDF) — [[conditioning-mechanism-asperity-regeneration]]에서
  1차 확보 완료, 이번 회차는 재인용(URL 재확인만).
- Doug Pysher, Brian Goers, John Zabasajja (2010), "Design, Characteristics and
  Performance of Diamond Pad Conditioners", DOI: 10.1557/proc-1249-e02-04 —
  3M 공개 PDF(전문 확보), 컨디셔너 설계·슬러리별 aggressiveness decay 데이터 확인.
  이 노트에서는 직접 인용하지 않았으나(주제가 컨디셔너 lifetime 쪽, disk-conditioner
  영역에 더 적합) `papers/`에 저장·등록해 후속 단원(Lv2-2 교체 기준)에서 재사용 가능.
- Stein et al. (1996), *J. Electronic Materials* 25(10), 1623 — 원문 미확보,
  Shi&Ring(2010)의 2차 인용을 통해서만 확인(**1차 미확보**로 명시).
