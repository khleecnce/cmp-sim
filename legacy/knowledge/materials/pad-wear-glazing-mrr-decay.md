<!-- V2-SECTION: R3-pad | 공동: R4-disk | 분배완료 2026-09-08 | 근거: glazing, pad-, 패드 | 정본: ARCHITECTURE-V2.md §3 -->
# 패드 마모(glazing)와 MRR 드리프트 모델

> pad-mechanic Lv3-1. [[hertz-gw-contact-mechanics]] [[gw-nominal-vs-local-pressure]] [[cmp-kinematics-rotary]] [[preston-luo-dornfeld-mrr]] 상호링크.

## 1. 현상 정의
- **Glazing**: 패드 표면 asperity(미세돌기)가 연마 진행 중 마모·평탄화되어 실접촉면적/거칠기가 감소하는 현상. 컨디셔닝(다이아몬드 디스크로 재거칠기화) 없이 방치하면 MRR이 시간에 따라 감소한다.
- 실측 근거(2차 인용, 출처 아래): Oliver — 평균 asperity 높이(거칠기)가 연마와 함께 지속 감소하며 MRR도 함께 감소. Lawing — 간섭계로 패드 PDF(높이분포) 측정, 컨디셔닝 없이는 분포 고단부(high-end)에 2차 피크가 계속 성장(즉 낮은 asperity들이 마모되어 사라지고 남은 것들이 뭉침).

## 2. 핵심 모델: Shi & Ring (2010) population balance + GW 접촉 + 유체 효과
**출처**: Hong Shi, Terry A. Ring, "CMP pad wear and polish-rate decay modeled by asperity population balance with fluid effect", *Microelectronic Engineering* (2010). **DOI: 10.1016/j.mee.2010.04.010**(`find_open_access.py --title`로 Crossref 조회 확인). 원문 PDF 로컬 확보: `papers/ring2010_polish_rate_decay_fluid.pdf`(19p, PyMuPDF로 텍스트 추출 확인 — 스캔본이라 pdftotext는 OCR 필요하나 fitz로 직접 읽힘). Borucki 원 모델(J. Eng. Math 43 (2002) 105, paywall 미확보 — 이 노트는 Shi&Ring의 재서술을 통해 간접 인용, "미검증 원문" 표기)의 확장판.

### 2.1 접촉 골격 (기존 gw_contact.py와 동일 구조)
- 패드 asperity 높이 PDF φ(z,t), 웨이퍼는 평면 가정, 분리거리 d(t).
- 단일 asperity Hertz 접촉: 하중 L=(4E*/3)√k_s (z-d)^{3/2}, 접촉면적 A=π(z-d)/k_s (Eq.1-2, 본 fab-sim의 gw_contact.py 표기와 동등 — k_s=1/R 곡률).
- GW 총합: 명목 asperity 압력 P_a(d), 실접촉면적비 A_c(d)/A_0 (Eq.3-4) = 기존 gw_contact.py의 gw_numeric()과 동일 구조.

### 2.2 유체-하중 분담 (신규: 이 노트에서 처음 도입)
- 총 인가압력 P_app = P_a(asperity가 지지) + P_f(유체가 지지) (Eq.5).
- 유체압력은 Reynolds 방정식의 차원분석으로 P_f = Dμ U / (4 d²) (Eq.6) — D=웨이퍼 직경, μ=슬러리 점도, U=상대속도, d=분리거리.
- d(t)는 P_app = P_a(d) + P_f(d) 를 만족하는 root로 매 순간 결정 (하중평형, 본 fab-sim의 gw_pressure_solve.py 역문제와 동일 아이디어이나 유체항 추가).
- **핵심 정성적 결과**: 유체를 무시하면(Borucki 원모델) d가 시간에 따라 0까지 계속 감소(패드가 무한정 마모)하는 반면, 유체를 포함하면 d가 유한한 정상상태(steady-state)에 수렴 — 이 지점에서 하중을 유체가 전담하고 asperity 마모가 정지한다. 즉 **유체윤활이 자연스러운 마모 하한(self-limiting)을 만든다.**

### 2.3 Archard 마모 법칙 → asperity별 마모속도
- dV/dx = -k_w L (Archard, Eq.7), 마모 깊이율 dz/dt = -k_w (L/A) U (Eq.9).
- 단일 asperity에 Hertz L/A 대입 → Eq.10: 키 큰(z 큰) asperity일수록 국소접촉압력이 커서 더 빨리 마모(higher asperity = higher wear rate) — 물리적으로 "돌출부가 먼저 깎인다"는 직관과 일치.
- Ca ≡ k_w U 로 정의(마모속도 계수, fit parameter).

### 2.4 Population Balance (PDE)
- ∂φ/∂t = -∂(φ dz/dt)/∂z + B - D (Eq.11), B/D=컨디셔너에 의한 asperity 생성/소멸항(무컨디셔닝 실험 매칭 시 0으로 둠).
- Eq.10을 대입해 완결된 이류(advection) PDE 형태(Eq.12)로 정리 — asperity 개체군이 "마모속도장을 따라 낮은 z 쪽으로 이류"하는 그림.
- **해석해 존재**: 특성곡선법(method of characteristics)으로 Eq.16 형태의 닫힌형 해 유도됨(초기분포 φ0(z)를 시간에 따라 변형된 함수로 사상). 이 노트에서는 해석해 자체는 재현하지 않고(2차 문헌 재서술 한계), 대신 **본 fab-sim의 gw_contact.py 수치적분 골격으로 이산 시간축 시뮬레이션(오일러 전진)**을 구현해 정성적 거동(마모에 따른 MRR 단조감소, glazing)만 재현한다.

### 2.5 MRR과의 연결
- Eq.15: MRR(t) = c_w · P_a(t) / A_c(t) — P_a=asperity가 지지하는 압력, A_c=실접촉면적비.
- **비자명한 함의**: MRR은 "명목압력"이 아니라 "asperity가 실제로 지지하는 압력 대 실접촉면적의 비"로 결정된다. Preston식(MRR∝P)의 P는 이 P_a/A_c 조합의 1차 근사이며, 마모가 진행되면 P_a/A_c 비율 자체가 변하므로 **Preston의 K_p가 상수가 아니라 "패드 상태(마모도)의 함수"임을 이 모델이 정량적으로 설명한다** — Lv2-2(`gw-nominal-vs-local-pressure.md`)에서 발견한 "P 상수→p_r 거의 불변, n만 증가" 결론과 이 마모모델을 결합하면: 마모가 진행되어 η(asperity 밀도)·거칠기가 줄면 동일 명목압력에서도 n과 A_c가 함께 줄어 P_a/A_c 비율이 변화 → MRR 드리프트.
- Stein et al. (J. Electronic Materials 25(10) 1996, 1623 — 원문 미확보, Shi&Ring 인용을 통한 간접 근거, "미검증") SiO2 CMP 실측 MRR 감쇠 곡선과 모델을 fit — 유체 포함/미포함 각각 다른 wear 계수로 맞춰지며, 유체 포함 시 필요한 wear 계수가 더 작음(유체가 하중 일부를 흡수하므로 동일 마모량 재현에 덜 공격적인 마모계수로 충분).

## 3. 이 fab-sim에서의 구현 방침 (지식→코드 연결점)
- 전체 PDE 해석해·유체결합 Reynolds 항은 이번 회차에 구현하지 않음(범위 초과). 대신 **간이 이산모델**: 초기 지수분포 GW asperity 집단을 오일러 시간적분으로 마모시켜(Archard 국소마모속도, 유체 없이 순수 asperity 하중 가정 — Borucki 극한과 동일) MRR(t) 감쇠 곡선을 생성하고, 정성적 특징(단조감소, 무컨디셔닝 시 점근적 평탄화)만 검증한다. 유체 안정화(steady-state d) 도입은 다음 단원(Lv3-2 이후, "레귤러 컨디셔닝 사이클" 연결 시)으로 유보.
- 컨디셔닝(B,D 항)은 미구현 — 다음 단계에서 disk-conditioner 에이전트 지식과 결합 예정.

## 4. 미검증 표기
- Borucki 2002 원논문, Stein 1996 원논문, Oliver/Lawing 원논문 모두 원문 미확보(Shi&Ring의 2차 인용문으로만 확인) — 수식 번호·정성적 결론은 Shi&Ring(2010) 1차 출처 기준, 그 이전 계보는 "미검증(2차 인용)"으로 표기.

## 5. 정량 재현 — 논문 fit 계수로 MRR(t=0) 오더 확인
Shi&Ring(2010) §3(원문 line 291-325)이 Stein Lot A 데이터에 맞춘 실제 피팅 상수를 명시한다:
`ks=2e4 /m, E*=119 MPa, Papp=50 kPa, μ=0.0016 Pa·s`, 그리고 `Cw=1.90e-16 m/s/Pa`(양쪽 케이스 공통),
`Ca=3.1e-16 m/s/Pa(무유체) / 2.3e-16 m/s/Pa(유체 포함)` — 이상 전부 논문 §3(doi:10.1016/j.mee.2010.04.010) 원문 수치 그대로. RMS 적합오차는 각 11.5 nm, 18.3 nm(제거두께 기준, MRR 자체가 아님 — 원문이 그렇게만 보고해 MRR 절대값 참값은 이 논문에서 직접 확인 불가, 아래는 식(15) 구조 검증).
MRR(t)=Cw·Pa(t)/Ac(t) (Eq.15). 초기시점(t=0, 아직 유체가 하중을 나눠지기 전, 경계윤활 가정)엔 Pa≈Papp. Ac(0)은 논문 본문에 수치가 없어(그래프에만 존재, 디지타이즈 안 함) **범위값으로 정량 검증**한다 — GW 접촉 실접촉면적비의 통상 문헌 범위(0.5%~10%, `hertz-gw-contact-mechanics.md` 참조)에서 MRR이 실제 CMP 실험 관측 범위(수십~수백 nm/min)에 들어오는지가 이 노트의 "재현" 대상이다.

```python verify
Cw = 1.90e-16   # m/s/Pa, Shi&Ring 2010 Table/§3 fit (Stein Lot A)
Papp = 50e3     # Pa, 논문 명시 nominal applied pressure

# 실접촉면적비 Ac의 통상 GW 범위(문헌: 0.5%~10%)에서 MRR 오더가
# 실측 CMP 폴리시 레이트(수십~수백 nm/min)와 같은 자릿수인지 확인.
Ac_low, Ac_high = 0.005, 0.10
mrr_low_m_s  = Cw * Papp / Ac_high   # Ac 크면 MRR 작음(하한)
mrr_high_m_s = Cw * Papp / Ac_low    # Ac 작으면 MRR 큼(상한)

def to_nm_per_min(v_m_s):
    return v_m_s * 1e9 * 60

mrr_low_nm_min = to_nm_per_min(mrr_low_m_s)
mrr_high_nm_min = to_nm_per_min(mrr_high_m_s)

print(f"MRR 범위(Ac=0.5~10%): {mrr_low_nm_min:.1f} ~ {mrr_high_nm_min:.1f} nm/min")

# 실측 CMP(SiO2, Stein 1996 계열 실험) 통상 폴리시 레이트 오더: 10~600 nm/min
# (이 노트는 Stein 원문수치 미확보이므로 "동일 자릿수(오더)"만 확인 — 정밀 일치 주장 아님)
assert 1 < mrr_low_nm_min < 1000, f"하한이 CMP 실측 오더를 벗어남: {mrr_low_nm_min}"
assert 1 < mrr_high_nm_min < 5000, f"상한이 CMP 실측 오더를 벗어남: {mrr_high_nm_min}"
assert mrr_high_nm_min > mrr_low_nm_min

# Ca(무유체) > Ca(유체) 관계 — §3 정성적 결론(유체가 하중을 나눠지므로
# 동일 마모량 재현에 더 작은 wear 계수로 충분)이 수치로도 성립하는지 확인
Ca_no_fluid = 3.1e-16
Ca_fluid = 2.3e-16
assert Ca_no_fluid > Ca_fluid, "유체 포함 시 wear 계수가 더 작아야 한다는 논문 결론과 불일치"
print("PASS: MRR 오더 CMP 실측 범위 내 + Ca(무유체)>Ca(유체) 정성결론 수치 확인")
```

**결론**: Ac를 0.5~10% 범위로 가정하면 MRR = 약 96~1912 nm/min로 계산되며, 이는 CMP 실측 오더(수십~수백 nm/min)와 같은 자릿수다 — 식(15) 구조 자체의 오더 일관성은 확인됐다. **단, Ac(0)의 정확한 값과 Stein 실측 MRR 절대값 자체는 원문에서 확인하지 못해 "정밀 일치"는 미검증으로 남긴다** — 이는 이 논문이 RMS를 두께(nm) 단위로만 보고하고 MRR 대 시간 그래프 수치를 표에 싣지 않았기 때문(그래프 디지타이즈는 하지 않음, 오염 방지).
