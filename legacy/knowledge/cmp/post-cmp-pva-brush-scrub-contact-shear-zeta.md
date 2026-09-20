<!-- V2-SECTION: (분배 대상 아님, tool-post-clean 독자 학습) | 작성 2026-09-13 | tool-post-clean Lv1-2 -->
# PVA 브러시 스크럽 물리 — 접촉역학·전단 입자탈리·계면 제타전위

> 에이전트: tool-post-clean Lv1-2 | 작성일: 2026-09-13
> 선행: [[colloid-zeta-dlvo-slurry-stability]](제타전위·Debye 길이·DLVO 정의) [[post-cmp-tool-cleaning-contamination-types-sources]](Lv1-1, 브러시가
> 오염 저장소가 되는 경로) [[post-cmp-adsorption-cleaning-chemistry]](세정액 화학·산화물 IEP)

## 1. 왜 세 축(접촉·전단·전하)을 같이 봐야 하는가
[[post-cmp-tool-cleaning-contamination-types-sources]]는 브러시가 "먹었다 뱉는" 오염 저장소가 되는 현상을
다뤘다. 이 노트는 그 앞 단계 — **브러시가 애초에 어떻게 입자를 떼어내는가**(또는 반대로 어떻게 새 입자를
만들어내는가) — 를 물리적으로 뜯어본다. PVA(polyvinyl alcohol) 브러시는 다공성·연질 스펀지형 고분자이며,
웨이퍼와의 상호작용은 세 축으로 분해된다: (i) **접촉역학** — 연질 브러시가 압축되며 웨이퍼와 만드는 접촉
면적·압력 분포, (ii) **전단에 의한 입자 탈리** — 브러시-웨이퍼 상대운동이 만드는 유체역학적 힘과 브러시
자체의 기계적 접촉력이 입자 부착력을 넘어서는가, (iii) **계면 제타전위** — 브러시·웨이퍼·용액 세 상이 만드는
전기이중층이 입자 재부착(또는 브러시 자체의 마모산 입자 발생)을 촉진/억제하는가. 세 축을 분리해서 보지
않으면 "압력을 올리면 세정력이 좋아진다"는 단순 직관이 왜 특정 조건(H-종단 Si)에서는 오히려 입자를
발생시키는지 설명할 수 없다(§4).

## 2. 접촉역학 — 연질 다공성 브러시 vs 단단한 웨이퍼 표면
**G. M. Burdick, N. S. Berman, S. P. Beaudoin, "A Theoretical Evaluation of Hydrodynamic and Brush Contact
Effects on Particle Removal during Brush Scrubbing," *J. Electrochem. Soc.* 150(10), G658 (2003).
DOI: 10.1149/1.1605422 (전문 확보: `papers/burdick2003-jes-hydrodynamic-brush-contact-particle-removal.pdf`,
미러 사이트 경유).**

- 단일면(single-sided) 디스크형 브러시 스크러버를 모델화할 때, 브러시-웨이퍼 사이 유동은 두 평행판(브러시=
  균일 고체면 가정, no-slip) 사이 흐름으로 근사한다(Burdick 2003 "Flow profile" 절). 브러시-웨이퍼 이격거리
  $D$는 **입자 크기 오더**로 잡아야 유의미한 제거가 일어난다는 것이 저자들의 전제다(같은 저자들의 선행논문,
  *J. Electrochem. Soc.* 150, G140, 2003 인용).
- 브러시 운전조건(Table I, 상용 브러시 스크러버 대표값): 브러시 반경 $R_B=5.7$ cm, 오프셋거리 $r_{cc}=5.0$ cm,
  **웨이퍼 각속도 90 rpm, 브러시 각속도 200 rpm**, 총 세정시간 20 s, **브러시 하중압력 3 psi(≈20.7 kPa)**,
  브러시 핑거(nodule) 지름 0.6 cm, 브러시당 핑거 수 85개. 이 조건에서 정규화 브러시-웨이퍼 상대속도
  $\hat V_{rel}$는 브러시 반경위치 $\hat r=0$에서 시간에 무관한 상수, $\hat r=1$(브러시 최외곽)에서 최대가
  된다 — 즉 **같은 브러시 압력이라도 반경위치에 따라 전단 조건이 크게 다르다**(브러시 중심부는 거의 정지
  마찰, 최외곽은 최대 상대속도).
- 브러시 압축(down force)이 커지면 접촉 지름이 커진다는 것은 별도 실측 논문(§4, Sato & Shimogaki 2011)에서
  **압축거리 0.4→1.2 mm일 때 브러시 핑거 접촉부 지름이 무압축 대비 1.2~1.6배 증가**했다고 정량 보고한다 —
  연질 다공성 PVA가 압축되며 접촉면적이 늘어나는 것을 직접 보여주는 수치다(하중이 커질수록 실접촉면적↑,
  이는 국소압력을 오히려 완화하는 방향).

## 3. 전단에 의한 입자 탈리 — 임계 입자 레이놀즈수 모델
같은 Burdick et al. (2003) 논문의 핵심 결과는 **입자가 언제 굴러서 떨어지는가**를 모멘트 균형으로 정의한
것이다. 부착력 $F_A$(반데르발스, van der Waals), 항력 $F_D$, 양력 $F_L$, 외부 회전모멘트 $M_D$ 사이의
롤링 제거 기준은
$$ M_D + F_D l_1 + F_L l_2 \ge F_A l_2 $$
이며, 이를 만족시키는 문턱 유동조건을 **임계 입자 레이놀즈수 $Re_{pc}$**로 정의한다($Re_p \ge Re_{pc}$이면
제거). 매끈한 구형 입자의 vdW 부착력(입자-표면 간 Lennard-Jones 분리거리 $h=0.4$ nm 가정)은
$$ F_A = \frac{A d}{12 h^2}\Big(1+\frac{2a^2}{hd}\Big) $$
로 주어진다($A$=Hamaker 상수, $d$=입자지름, $a$=접촉반경). 논문은 이 매끈-구 식이 아니라 표면조도를 반영한
Cooper(2000, Ph.D. thesis, Arizona State Univ.; 원문 미확보 — Burdick 2003의 재인용으로만 확인, 2차 인용)의
확률모델로 alumina(0.2 μm, 형상비 AR 0.2~5)-water-SiO₂/Cu 계의 부착력을 계산했다:
- alumina-water-**SiO₂**: 평균 부착력 **0.1~16 nN**(AR·매립비율 전 범위), Hamaker 상수 $1.3\times10^{-20}$ J.
- alumina-water-**Cu**: 평균 부착력 **1.5~165 nN**, Hamaker 상수 $6.2\times10^{-20}$ J(Cu가 더 커서 부착력도
  더 크다).
- 입자가 표면에 **50% 매립**되면 접촉반경이 27~77 nm(비매립)에서 105~283 nm(매립)로 급증해 $Re_{pc}$가
  1~2 자릿수 뛴다 — "한 번 파묻힌 입자는 유체역학만으로 못 뗀다"는 결론(저자들의 Table VI: 50% 매립 입자는
  브러시-입자 모멘텀 전달을 더해도 대부분 "Unattainable"로 표시됨).
- §6의 재현 코드는 매끈-구 식(Eq. 2, 위 식)을 AR=1·비매립 조건(Table IV: $a=45.2$ nm, $d=0.2$ μm)에 그대로
  대입해, **표면조도를 무시하면 부착력이 문헌의 러프니스-보정 상한(SiO₂ 16 nN, Cu 165 nN)을 크게 초과**함을
  확인한다 — 이는 오류가 아니라 "표면조도가 실접촉면적·유효 vdW 상호작용을 몇 자릿수 깎는다"는 잘 알려진
  결과의 정성적 재현이다(Cooper 모델 자체는 미확보이므로 절대 저감폭은 **미검증**).

## 4. 브러시-웨이퍼-용액 계면의 제타전위 — 재부착 방지와 "브러시발 입자 생성"의 양날
**N. Sato, Y. Shimogaki, "Particle Generation on Hydrogen-Terminated Si Surface by Brush Scrubbing of
Polyvinyl Alcohol," *J. Electrochem. Soc.* 158(11), D651 (2011). DOI: 10.1149/2.041111jes (전문 확보:
`papers/sato2011-jes-particle-generation-h-terminated-si-pva-brush.pdf`, 미러 사이트 경유).**

- 이 논문은 [[colloid-zeta-dlvo-slurry-stability]]가 슬러리 입자-입자 상호작용에 쓴 것과 같은 제타전위 개념을,
  **브러시-웨이퍼라는 서로 다른 두 고체 표면 사이**에 적용한다 — 콜로이드 안정성(§3~5 참고)이 아니라
  "브러시 자체가 마모돼 입자를 만드는가"를 설명하는 데 쓴다는 점이 새롭다.
- 실측 제타전위(DIW, pH 7.0): **PVA 브러시 재질 −24.8 mV**, **H-종단 Si(DHF 처리 후) +12.5 mV**, **화학
  산화막(APM/HPM 처리 후) −11.3 mV**. 브러시/웨이퍼 회전속도는 각각 100 rpm/60 rpm(OnTrak DSS200 이중면
  스크러버), 압축거리 0.4~1.2 mm, 세정시간 50 s.
- 관찰: **H-종단 Si**(브러시와 부호가 반대, 인력 조건) 위에서 압축거리가 커질수록 브러시 회전토크가
  뚜렷하게 증가하고, 라만분광으로 확인된 비정질탄소(CH₂ 신축 2900 cm⁻¹, D밴드 1330 cm⁻¹·G밴드 1600 cm⁻¹)
  입자가 다량 생성됐다. 반면 **화학 산화막**(브러시와 같은 부호, 반발 조건) 위에서는 압축거리를 올려도 토크
  증가가 미미했고 입자 발생도 거의 없었다. 저자들은 이를 "브러시-웨이퍼 계면의 제타전위 부호"로 설명한다 —
  반대부호(인력)이면 브러시 표면과 웨이퍼가 정전기적으로 더 강하게 끌려 붙어 마찰이 커지고, 그 마찰이 PVA
  자체를 깎아 비정질탄소 입자를 만든다는 기구다(정성 서술, 저자도 정량 힘 계산은 제시하지 않음).
- §6의 재현 코드는 이 관찰을 **부호 규칙(같은 부호=반발, 반대부호=인력)** 으로 정식화해 세 표면쌍의
  인력/반발을 예측하고, Sato 2011이 보고한 토크·입자수 패턴(H-종단 Si=인력=마찰·입자 급증, 산화막=반발=
  거의 무영향)과 부호가 일치함을 확인한다. 추가로 [[colloid-zeta-dlvo-slurry-stability]]에서 이미 검증된
  Debye 길이 함수를 재사용해, DIW(순수 이온세기 ~$10^{-7}$ M 가정, 브러시 세정액 첨가제가 있으면 이온세기가
  올라가 차폐길이가 짧아진다는 점은 **미검증/추정**)의 정전차폐 길이가 Burdick 2003의 접촉 스케일(수십~수백
  nm)보다 훨씬 커서, 이 스케일에서는 정전 상호작용이 거의 차폐되지 않는 쿨롱 영역에 가깝다는 것도 확인한다.
- **재부착 방지 관점**(콜로이드 노트와의 접점): [[colloid-zeta-dlvo-slurry-stability]] §5는 슬러리 pH를
  올려 산화물 표면을 모두 음전하로 만들면 입자-웨이퍼 정전반발이 생겨 재부착이 억제된다고 정리했다. 이
  노트의 관찰은 그 원리의 "브러시-웨이퍼" 버전이다 — 세정액 pH·이온세기를 브러시 재질과 웨이퍼 표면이
  **같은 부호**가 되도록 맞추면 재부착뿐 아니라 브러시 마모발 입자 생성 자체도 줄어들 개연성이 있다(Sato
  2011은 이 함의를 명시하지 않았고, 본 노트의 추론이다 — **미검증**).

## 5. 브러시 파라미터 정리 — 회전속도·압력·접촉시간
| 파라미터 | Burdick 2003 (Table I) | Sato 2011 (실험조건) |
|---|---|---|
| 브러시 각속도 | 200 rpm | 100 rpm |
| 웨이퍼 각속도 | 90 rpm | 60 rpm |
| 하중/압력 | 3 psi(≈20.7 kPa) | 압축거리 0.4~1.2 mm(압력 환산치 미기재) |
| 접촉시간 | 총 20 s | 50 s |
| 브러시 구조 | 핑거(nodule) 지름 0.6 cm, 85개/브러시 | 압축 시 접촉지름 1.2~1.6배 증가 |
두 논문이 쓴 상용 스크러버 조건(브러시:웨이퍼 각속도비 ≈2.2~1.7)은 오더가 비슷하지만 정확히 일치하지
않는다 — 장비 세대·용도(STI vs ILD vs Si 베어웨이퍼)에 따라 최적 조합이 다르며, 이 노트에서 "표준값"으로
단정할 수 있는 단일조건은 **확인하지 못했다**(미검증).

## 6. python 재현 — Debye 차폐길이 재사용, 제타전위 부호 규칙, vdW 부착력 상한 확인
```python verify
import math

EPS0 = 8.8541878128e-12
KB = 1.380649e-23
NA = 6.02214076e23
QE = 1.602176634e-19
EPSR_WATER = 78.5


def debye_length_nm(I_molar, T=298.15, epsr=EPSR_WATER, z=1):
    """[[colloid-zeta-dlvo-slurry-stability]]에서 12/12 PASS로 이미 검증된 함수를 그대로 재사용."""
    kappa2 = (2.0 * (z * QE) ** 2 * I_molar * 1000.0 * NA) / (EPS0 * epsr * KB * T)
    return 1.0 / math.sqrt(kappa2) * 1e9


# ---- (A) DIW(pH 7, 자체이온화 I~1e-7 M)의 정전차폐 길이 vs Burdick 2003 접촉 스케일 ----
I_DIW = 1.0e-7
kappa_inv_nm = debye_length_nm(I_DIW)
particle_scale_nm = 283.0  # Table IV, 50% 매립 alumina 입자의 최대 접촉반경(aembedded)
print(f"DIW(pH7) Debye 길이 = {kappa_inv_nm:.0f} nm (참고: 순수 DIW 가정, 첨가제 있으면 더 짧아짐 — 추정)")
assert kappa_inv_nm > 3 * particle_scale_nm, (
    "DIW의 정전차폐 길이가 브러시-입자 접촉 스케일(수백 nm)보다 3배 이상 커야 "
    "'거의 무차폐 쿨롱 영역' 근사가 성립한다")

# ---- (B) Sato et al. 2011 (DOI: 10.1149/2.041111jes) 실측 제타전위 부호 -> 인력/반발 예측 ----
zeta_mV = {'PVA': -24.8, 'H_Si': 12.5, 'oxide': -11.3}  # DIW, pH 7.0 실측값


def interaction(a, b):
    return 'attraction' if zeta_mV[a] * zeta_mV[b] < 0 else 'repulsion'


assert interaction('PVA', 'H_Si') == 'attraction', \
    "PVA(-24.8 mV)-H종단Si(+12.5 mV)는 반대부호이므로 정전인력이어야 함"
assert interaction('PVA', 'oxide') == 'repulsion', \
    "PVA(-24.8 mV)-화학산화막(-11.3 mV)은 동일부호이므로 정전반발이어야 함"
print("부호 예측: PVA-H종단Si=인력, PVA-산화막=반발"
      " -> Sato 2011 관찰(H종단Si에서만 토크 급증+비정질탄소 입자 검출)과 방향 일치")

# ---- (C) Burdick et al. 2003 (DOI: 10.1149/1.1605422) Eq.2 매끈-구 vdW 상한 vs Cooper 러프니스-보정치 ----
def vdw_force_N(A_J, d_m, a_m, h_m=0.4e-9):
    return (A_J * d_m / (12 * h_m ** 2)) * (1 + 2 * a_m ** 2 / (h_m * d_m))


d = 0.2e-6     # AR(lambda)=1, alumina 입자 지름 (Table IV)
a = 45.2e-9    # AR=1, 0% 매립 접촉반경 (Table IV)
FA_SiO2 = vdw_force_N(1.3e-20, d, a)   # Hamaker: alumina-water-SiO2
FA_Cu = vdw_force_N(6.2e-20, d, a)     # Hamaker: alumina-water-Cu

print(f"매끈-구 vdW 상한 (AR=1, 0% 매립): SiO2={FA_SiO2*1e9:.1f} nN, Cu={FA_Cu*1e9:.1f} nN")
assert FA_SiO2 > 16e-9, "매끈-구 모형은 Cooper 러프니스-보정 SiO2 상한(16 nN)보다 커야 함"
assert FA_Cu > 165e-9, "매끈-구 모형은 Cooper 러프니스-보정 Cu 상한(165 nN)보다 커야 함"
assert FA_Cu > FA_SiO2, "Hamaker 상수가 큰 Cu 쪽 vdW 힘이 SiO2보다 커야 함(논문의 정성 결론과 일치)"
print("PASS: (A) 차폐길이 스케일분리, (B) 제타전위 부호=관찰된 마찰/입자생성 패턴, "
      "(C) 매끈-구 상한이 러프니스-보정 상한을 초과(방향 일치) 모두 확인")
```
재현 요약(한 줄): 매끈-구 vdW 상한(SiO₂ {계산값}nN, Cu {계산값}nN)이 Burdick 2003의 러프니스-보정 부착력
범위(SiO₂ 16 nN, Cu 165 nN 상한)를 각각 초과하고 Cu>SiO₂ 순서가 유지됨을 확인했다(Burdick et al., 2003,
DOI: 10.1149/1.1605422). 제타전위 부호 규칙은 Sato et al.(2011, DOI: 10.1149/2.041111jes)이 실측한
PVA(−24.8 mV)/H종단Si(+12.5 mV)/산화막(−11.3 mV) 세 값에 대해 관찰된 마찰·입자생성 패턴과 방향이 일치했다.

## 7. 한계 (정직 표기)
- Cooper의 러프니스-보정 부착력 모델(원 Ph.D. thesis, 2000, Arizona State Univ.)은 원문을 확보하지 못했고
  Burdick 2003의 재인용 범위(0.1~16 nN, 1.5~165 nN)만 사용했다 — **2차 인용**이며, AR=1·0%매립 조건의
  "정확한" Cooper 모델 값(Fig. 6에서 도표로만 제시)은 그림 판독을 시도하지 않아 **미확보**다. 따라서 §6(C)는
  "매끈-구 상한이 러프니스-보정 상한보다 크다"는 방향성 확인이지, 정량적 저감비율 재현이 아니다.
  · 계산값: SiO₂ 70.5 nN, Cu 336.2 nN (본 노트 §6 코드 실행 결과, 2026-09-13 재실행 확인).
- Sato 2011의 "제타전위 부호가 마찰·입자생성을 좌우한다"는 서술은 저자 본인도 힘의 정량 계산 없이 정성적
  기구로만 제시했다 — 본 노트 §6(B)의 부호규칙은 저자 서술을 코드로 정식화한 것이지, 저자가 직접 제시한
  수식을 재현한 것이 아니다.
- §4 말미의 "세정액 pH를 브러시-웨이퍼 동일부호로 맞추면 브러시발 입자생성도 줄어들 것"이라는 추론은 본
  노트의 확장 해석이며 문헌에 직접 근거가 없다(**미검증**).
- §5 표의 두 논문 운전조건은 세대·용도가 다른 장비값을 나란히 놓은 것으로, 어느 쪽이 "표준"인지는
  **확인하지 못했다**.
- 고용주의 사내 데이터·특정 장비 벤더의 실제 레시피는 다루지 않았다(공개 문헌 정의만).

## 8. 자기시험
→ [[../../agents/tool-post-clean/EXAMS.md]] Lv1-2 문항 참조.
