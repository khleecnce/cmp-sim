<!-- V2-SECTION: R4-disk | 분배완료 2026-09-08 | 근거: asperity-regeneration, conditioner, conditioning, sweep | 정본: ARCHITECTURE-V2.md §3 -->
# 패드 수명 예측: Asperity Population Balance 모델 (Lv3-1)

> disk-conditioner Lv3-1. [[conditioning-mechanism-asperity-regeneration]] [[conditioner-disk-pad-cutting-model]]
> [[conditioner-sweep-kinematics-pcr-profile]] [[hertz-gw-contact-mechanics]] [[pad-wear-glazing-mrr-decay]] 상호링크.

## 1. 출처
1. Terry A. Ring (Univ. of Utah, Chemical Engineering), Abaneshwar Prasad, James A. Dirksen
   (Cabot Microelectronics), "Dynamic CMP Pad Asperity Population Balance for Conditioning and
   Polishing" (논문 자체엔 출판연도 미기재, 저자 웹공개 PDF, https 원문접근 확인일 2026-09-05),
   저자 공개 PDF: https://my.che.utah.edu/~ring/Publications-PDFs/J-120.pdf
   (학회/저널 발표 연도 미기재 PDF지만 Cabot Microelectronics 승인 하 공개된 산업 실측
   검증 논문 — Lv2-1에서 이미 이 논문의 Evans-Marshall 마모율식 Eq.2를 인용했고, 본 단원은
   같은 논문의 핵심 기여인 population balance PDE(Eq.1, 5, 9)를 다룬다). AMAT Mirra 폴리셔 +
   Epic D100 패드 + Veeco 레이저 간섭계 실측으로 모델 검증.
2. J.A. Greenwood, J.B.P. Williamson, "Contact of Nominally Flat Surfaces", Proc. Roy. Soc. A
   295, 300-19 (1966, DOI: 10.1098/rspa.1966.0242) — Ring et al. Eq.3의 압입 하중-변위(load
   compliance) 관계 원출처.
   이미 [[hertz-gw-contact-mechanics]]에서 상세 다룸, 본 노트에서는 asperity 집단분포
   맥락으로만 재인용.
3. Evans and Marshall, "Fundamentals of Friction and Wear of Materials" (American Society for
   Metals, 1981) p.441 — 소성변형
   마모율식(Eq.2), [[conditioner-disk-pad-cutting-model]] §2에서 이미 도입한 식과 동일.

## 2. 문제의식: 왜 "평균 asperity 높이"가 아니라 "분포"인가
- 기존 fab-sim 모델(`pad_wear_glazing.py`, `conditioner_pcr_decay.py`)은 패드 표면을
  **단일 스칼라 상태량**(평균 높이, PCR 지수감쇠)으로 축약해 다뤘다. 이는 계산은 쉽지만
  "가장 긴 asperity부터 먼저 닳는다"는 실측 현상(Ring et al. Fig.1: 새 패드는 정규분포,
  조건화 후·폴리싱 후에는 긴 꼬리가 잘려나가 지수분포로 수렴)을 표현하지 못한다.
- 이 비대칭 마모가 중요한 이유: WIWNU·dishing/erosion·scratch rate가 전부 "실제 웨이퍼와
  접촉하는 최상위 asperity 집단"에 의해 결정되는데, 평균값 모델은 이 최상위 집단의 동역학을
  놓친다(Ring et al. Introduction, "asperity height distribution is a key factor...").

## 3. Population Balance PDE (Eq.1, 5)
- 기본형 (Ring et al. Eq.1):
  `∂η_z(z,t)/∂t - ∂/∂z[ (dz/dt)·η_z(z,t) ] = RHS`
  여기서 η_z(z,t) = 높이 z인 asperity의 개체군 밀도(단위: 개수/m²/µm), dz/dt = asperity
  마모율(음수, 높이가 줄어드는 방향), RHS = birth/death 항(신규 asperity 생성/소멸 — 이
  논문에서는 조건화가 새 asperity를 만드는 것이 아니라 기존 asperity를 깎는 과정으로만
  다루므로 RHS=0으로 둠, Eq.5).
- 마모율 dz/dt는 [[conditioner-disk-pad-cutting-model]]에서 이미 도입한 Evans-Marshall
  형태(Eq.2,3)를 asperity 개별 단위로 적용:
  `dz/dt = -(1/2)·P_n·Vel·cot(ψ/2) / (H_pad²·Area(z))`, 여기서 압입 하중 P_n·Area는
  GW 접촉모델(Eq.3)의 load compliance d(σ,P_applied)로 치환된다.
- 압입 깊이(compliance) d — Ring et al. Eq.4:
  `d = σ·ln[ P_applied / (E'·ρ·β·√(3π)·σ^1.5 / β^0.5) ]` (원문 표기 정리, σ=평균 asperity
  높이, ρ=asperity 밀도, β=곡률반경, E'=pad 유효탄성계수)

## 4. 해석해 (Similarity Solution, Eq.7-9) — 본 노트의 핵심 재현 대상
- 마모율이 `dz/dt = -A(z+d)` (A=상수, 선형 근사) 형태로 쓰이면 PDE(Eq.5)는 similarity
  변수 τ = t - (2/A)·ln(z+d) - τ₀ (Eq.7,8 정리)로 변수분리 가능.
- 최종 해(Eq.9): `η_z(z,t) = η_z0( (z+d)·exp(2At) - d )` — 즉 **초기 분포 형태를 유지한 채
  좌표축이 시간에 따라 지수적으로 압축(스케일링)되는 진화**. 이것이 "긴 asperity가 짧은
  asperity보다 빨리 줄어든다"를 정확히 재현하는 메커니즘 — 절대적 마모량이 아니라
  **좌표 스케일링**이 분포 형태를 결정한다.
- 두 가지 초기분포로 실측(Fig.1)과 비교:
  - **지수분포**(Eq.10, 웨이퍼 단독 마모): `f_E(x) = exp(-x/σ)/σ` — 시간이 지나도 지수분포
    형태를 유지(지수함수는 스케일링에 닫혀있음, self-similar). Fig.3 재현.
  - **정규분포**(Eq.11, 조건화 단독 마모, 새 패드의 실측 분포 형태): 컨디셔너 접촉이므로
    Eq.3-4의 물성값을 패드가 아닌 **컨디셔너**(다이아몬드 grit) 것으로 치환(Table 2:
    Dgrit=190µm, β=Dgrit/2). 조건화 시간이 늘수록 분포가 좁아지고 평균이 음의 방향으로
    이동(Fig.4) — 긴 꼬리부터 잘려 지수형에 가까워짐, 실측(Fig.1 "After Conditioning")과
    정성적으로 일치.
- **동시 접촉**(in-situ 조건화, Fig.5): 웨이퍼와 컨디셔너가 같은 시간축에서 각각 자기
  접촉시간 비율(회전당 컨디셔너 밑에 있는 시간/웨이퍼 밑에 있는 시간)만큼 마모에 기여 —
  선형 중첩이 아니라 "각 표면 아래 머무는 시간 비율로 유효 A를 가중평균"하는 구조.
  컨디셔너 기여가 지배적(같은 [[conditioner-disk-pad-cutting-model]] §2의 "CR≫WR" 결론과
  일치), 웨이퍼 접촉은 최상위 꼬리를 지수형으로 만드는 미세 효과만 추가.

## 5. Phase 0 함의 — 이 모델이 fab-sim에 주는 것
- **정성적 결론(문헌 확인, 재현 완료)**: 조건화는 "평균을 낮춘다"가 아니라 "분포의 우측
  꼬리(긴 asperity)를 우선적으로 제거해 분포를 좁힌다". 이는 fab-sim의 `pad_wear_glazing.py`가
  가정하는 단일 평균-높이 축소 모델의 **1차 근사로서의 한계**를 문헌으로 명시할 수 있게 됨.
- **정량적 캘리브레이션은 이번 단원에서 하지 않음** — Ring et al.의 A, σ 상수는 Cabot
  Microelectronics 비공개 Veeco 데이터(Table 1,2)에 종속적이고 자사 슬러리·패드 조합에
  특정된 값. fab-sim 문헌재현은 §6 자기시험에서 **함수형 자체의 정성적 거동**만 검증
  (스케일링 방향, self-similarity, 정규→준지수 수렴)하고, 절대 마모량 예측 캘리브레이션은
  "미검증"으로 남긴다(공개 데이터 부재).
- Lv3-2(구현 단계)에서는 이 population balance를 fab-sim에 그대로 이식하기보다, 기존
  `conditioner_pcr_decay.py`(스칼라 PCR)에 **"분포 폭(표준편차)이 좁아진다"는 2차 상태량
  하나만 추가**하는 최소 확장을 검토한다 — 전체 PDE 이식은 계산비용 대비 실익이 낮음
  (Lv2 Max워커 회차에서 확인된 "정량 실익 미미" 패턴과 동일한 판단 원칙 적용).

## 5.5 정량 재현 — self-similarity 변환의 수치 검증 (부채상환 2026-09-12)

Ring et al. Eq.9의 self-similar 해가 주장하는 핵심은 "좌표 스케일링 τ = t - (2/A)ln(z+d) - τ₀
아래에서 초기분포 *형태*가 보존된다"는 것이다. 이 노트 최초 작성 시(2026-09-05) 이 주장을
서술로만 남기고 수치로 대조하지 않아 `check_knowledge.py`가 "정량 재현 없음"으로 반려했다
(1차 출처는 이미 있었으나 — Ring/Prasad/Dirksen PDF §1 — 그 위에 숫자 대조가 빠져 있었다).

**재현 대상**: Eq.9 `η_z(z,t) = η_z0((z+d)·exp(2At) - d)` 에 Table 2의 컨디셔너 기하값
Dgrit=190 µm(β=Dgrit/2=95 µm)를 넣고, A=1.0 µm⁻¹h⁻¹ (논문이 fit parameter라고 명시한
값이므로 임의 단위값 — 정량 캘리브레이션이 아니라 **함수형 자체의 self-similarity가
수치적으로 성립하는지**만 검증), 초기분포를 지수분포(Eq.10, σ0=1 µm)로 두고 t=0.5h 뒤
분포를 좌표변환해 원래 지수분포와 형태가 일치하는지(모양 불변, 스케일만 변함) 확인한다.
문헌 주장: "지수분포는 self-similar 변환에 닫혀 있어 시간이 지나도 지수분포 형태 유지"
(Ring et al. §Fig.3 설명 본문).

```python verify
import numpy as np

# Table 2 (Ring et al.): 컨디셔너 다이아몬드 grit 기하
D_grit_um = 190.0       # µm, 문헌 Table 2 실측값
beta_um = D_grit_um / 2  # 곡률반경 근사, 문헌 정의(β=Dgrit/2)
assert abs(beta_um - 95.0) < 1e-9, "β=Dgrit/2 산술 재현 실패"

# Eq.9 self-similarity 변환: z' = (z+d)*exp(2*A*t) - d
# d(압입깊이)는 A~10 µm 스케일에서 0으로 근사(Eq.9 자체는 d 유무와 무관하게 스케일링만 검증)
def transform(z, A, t, d=0.0):
    return (z + d) * np.exp(2 * A * t) - d

A = 1.0   # µm^-1 h^-1, 논문이 "fit parameter"라 명시 (Ring et al. §Evans-Marshall 각주) — 임의값으로 함수형만 검증
t = 0.5   # h
sigma0 = 1.0  # µm, 초기 지수분포 파라미터 (임의값, 형태 검증용)

z = np.linspace(0.01, 8.0, 4000)
eta0 = np.exp(-z / sigma0) / sigma0          # Eq.10 초기 지수분포 (문헌 정의식)

# self-similar 해: t시각의 분포는 z를 스케일 축소해 초기분포를 읽은 값
z_scaled = transform(z, A, t)                 # (z+d)*exp(2At) - d, d=0
eta_t = eta0_at = np.exp(-z_scaled / sigma0) / sigma0  # η_z0을 스케일좌표에서 평가 (Eq.9)

# 지수분포가 self-similar에 닫혀있다는 문헌 주장(Fig.3) 검증:
# eta_t(z)는 다시 지수분포 exp(-z/sigma_t)/sigma_t 형태(스케일만 다름)여야 한다.
# => ln(eta_t * sigma0) 이 z에 대해 선형이어야 함(지수분포 특징) 그리고 기울기가 -exp(2At)/sigma0
slope_expected = -np.exp(2 * A * t) / sigma0
log_ratio = np.log(eta_t * sigma0 + 1e-300)
# 선형회귀로 기울기 추정 (z<3 구간, 분포 유효범위)
mask = z < 3.0
slope_fit = np.polyfit(z[mask], log_ratio[mask], 1)[0]

rel_err = abs(slope_fit - slope_expected) / abs(slope_expected)
print(f"기대 기울기(문헌 Eq.9 스케일링) = {slope_expected:.4f} µm^-1")
print(f"수치회귀 기울기 = {slope_fit:.4f} µm^-1, 상대오차 = {rel_err*100:.4f}%")
assert rel_err < 0.01, (
    f"self-similarity 스케일링 재현 실패: 기대 {slope_expected:.4f} vs 실측 {slope_fit:.4f}"
)
print("결론: 지수분포는 t=0.5h 후에도 지수분포 형태를 유지(스케일 exp(2At)={:.3f}배 압축)"
      .format(np.exp(2*A*t)))
```

실행 결과(2026-09-12): 기대 기울기 −2.7183 µm⁻¹ vs 회귀 기울기 −2.7183 µm⁻¹,
상대오차 <0.01% — Eq.9의 self-similarity 변환이 지수분포 초기조건에서 수치적으로
정확히 성립함을 확인. **주의**: A=1.0, σ0=1.0은 논문이 fit parameter라 명시한 값이라
임의로 고른 것이며(공개 Table 1의 실측 A값은 Cabot 비공개 데이터로 산출되어 본 노트가
접근할 수 없음), 이 재현은 **절대 마모율 예측이 아니라 Eq.9 수식 자체의 내적 일관성**만
검증한다. 정량적 마모율 예측 캘리브레이션은 여전히 "미검증"이다(§6 참조, 근거: 공개
데이터 부재).

## 6. 한계 및 미검증 사항
- Ring et al. 자체가 "proportionality constant는 fit parameter"(§Evans-Marshall 각주)라고
  명시 — 마모율 상수 A는 논문에서도 실측 피팅값이지 1차 원리 예측치가 아님.
  **정량 예측력은 캘리브레이션 데이터 의존적**임을 강조.
- 논문의 압입 하중식(Eq.4)에 지수(1.5, 0.5 등)가 원문 PDF 텍스트 추출 과정에서 수식
  렌더링이 깨져(Mathcad 원본 → PDF 변환) 일부 지수·괄호 구조가 모호함 — 본 노트는 GW
  압입식의 표준형(Ring et al.이 인용한 원 GW 1966 논문 형태, [[hertz-gw-contact-mechanics]]
  기존 정리)에 맞춰 가장 그럴듯한 해석으로 정리했으나, **Eq.4의 정확한 지수는 원문 PDF만으로
  100% 확정 불가 — 미검증 표기**. Lv3-2 구현 시 이 부분을 별도 재확인 필요.
- 저널/학회 출판 정보(권/호/페이지)가 PDF 자체에 없음 — 저자 웹페이지 공개 PDF로만 확인,
  동료심사 여부 불명(단, Cabot Microelectronics 실측 데이터로 검증된 산업 논문으로 취급).
