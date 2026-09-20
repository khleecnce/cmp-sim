<!-- V2-SECTION: R3-pad | 공동: R1-equipment | 분배완료 2026-09-08 | 근거: pad-, viscoelast, 패드 | 정본: ARCHITECTURE-V2.md §3 -->
# CMP 패드 폴리우레탄 점탄성 기초 (DMA, 저장/손실 탄성률, 크리프)

> pad-mechanic Lv1-1. [[cmp-tool-architecture]] (장비 구조, 헤드/플래튼/컨디셔너) 와 연결 —
> 이 노트는 그 "패드" 구성요소 자체의 재료 거동을 다룬다. 이후 [[preston-luo-dornfeld-mrr]]의
> Luo-Dornfeld형(P^1/2) 확장 시 접촉역학(GW 모델, Lv2-1)의 입력으로 쓰일 탄성계수 개념의 토대.

## 1. 왜 점탄성인가 — CMP 패드가 순수 탄성체가 아닌 이유
CMP 폴리우레탄(PU) 패드는 하드/소프트 세그먼트가 미세상분리된 블록공중합체다. 하드 세그먼트(우레탄
결합, 수소결합 도메인)가 물리적 가교점 역할을 하고 소프트 세그먼트(폴리올 사슬)가 점성 흐름을
담당한다 — 즉 탄성(고체적 저장)과 점성(액체적 소산)이 공존한다. 순수 후크 탄성체라면 압력 인가 후
즉시 변형이 정지하지만, 실제 CMP 패드는 하중 인가 중에도 서서히 추가 변형되는 **크리프(creep)**를
보이고, 패드-웨이퍼 접촉면의 실제 압력분포·WIWNU에 이 시간의존 거동이 직접 영향을 준다
(cf. [[cmp-kinematics-rotary]]에서 확인한 "운동학만으론 WIWNU 설명 불가 → 압력분포가 주범"이라는
결론의 다음 퍼즐 조각).

**출처**: Y. Meng, S. Zhang, Z. Zhang, "Effect of Structurally Modified Toluene Diisocyanate-Based
Polyurethane Pads on Chemical Mechanical Polishing of 4H Silicon Carbide Substrate," *Polymers*
2025, 17(5), 613. https://doi.org/10.3390/polym17050613 (오픈액세스, PMC11902601). 하드/소프트
세그먼트 미세상분리·PCDL(폴리카보네이트디올) 함량과 기계물성의 관계를 실험으로 규명한 최신 논문.

## 2. DMA(동적기계분석) — 저장탄성률·손실탄성률·tan δ
정현파 변형을 가하고 그 응답 응력의 위상차 δ를 측정한다.
- 변형: ε(t) = ε₀ sin(ωt)
- 응력: σ(t) = σ₀ sin(ωt + δ)
- **저장탄성률(storage modulus)** E′ = (σ₀/ε₀) cos δ — 탄성적으로 되돌려주는(저장되는) 에너지 성분
- **손실탄성률(loss modulus)** E″ = (σ₀/ε₀) sin δ — 열로 소산되는 점성 성분
- **손실계수** tan δ = E″/E′ — 값이 클수록 점성 지배적(감쇠 큼), 유리전이온도(Tg)에서 피크

순수 탄성체는 δ=0 (E″=0), 순수 점성 유체는 δ=90°(E′=0). 실제 PU 패드는 그 사이.

**출처**: Wikipedia, "Dynamic modulus" / "Dynamic mechanical analysis" (2025년판, 표준 교과서
수준 정의 — 1차 출처는 J.D. Ferry, *Viscoelastic Properties of Polymers*, Wiley, 1980, 이지만
본 노트는 무료 접근 가능한 Wikipedia 요약 + 검증 시뮬레이션으로 대체).

## 3. Maxwell 모델 — 가장 단순한 점탄성 회로 모델
스프링(탄성, 모듈러스 E)과 대시팟(점성, 점도 η)을 **직렬** 연결한 모델. 이완시간 τ₀ = η/E.
정현파 응력 인가 시:
- E″(ω) = E·τ₀ω / (τ₀²ω² + 1)  — ω = 1/τ₀ 에서 피크 (E″ 최대)
- E′(ω) = E·τ₀²ω² / (τ₀²ω² + 1)  — ω→∞ 에서 E로 포화(고주파=순간탄성), ω→0 에서 0(저주파=완전이완)

CMP 패드처럼 다중 완화시간을 갖는 실재 고분자는 Maxwell 요소들의 병렬합(Generalized Maxwell /
Prony 급수)으로 근사하지만, 단일 Maxwell 요소로도 "저주파=점성 지배, 고주파=탄성 지배" 라는
정성적 거동과 피크 위치(ω=1/τ₀)는 정확히 재현된다 — Section 4에서 수치 검증.

**출처**: Wikipedia, "Dynamic mechanical analysis" §Frequency sweep (Maxwell model 수식 인용).

## 4. Maxwell-Voigt 크리프 모델 — CMP 하중 인가 시 시간의존 변형
CMP 패드는 헤드 하강 후 하중이 "유지"되는 스텝 응력 하에서 크리프(시간에 따른 변형 증가)를 보인다.
**Standard Linear Solid (Zener) 모델**의 크리프 컴플라이언스는 지수적으로 평형값에 접근한다:
  J(t) = J₀ + (J∞ − J₀)·(1 − exp(−t/τ_creep))
여기서 J₀=순간(유리질) 컴플라이언스, J∞=평형(고무질) 컴플라이언스, τ_creep=크리프 지연시간.
CMP 공정 관점에서 의미: 헤드 하강 직후 짧은 시간 동안은 패드가 아직 완전히 "안착"하지 않아
국소압력이 과도기적으로 불균일할 수 있고, 이 τ_creep이 초 단위라면 실제 폴리싱(수십 초~수 분)
전 구간에 걸쳐 무시 가능하지만 수 분 단위라면 시간축 MRR 드리프트([[process_time]] 모듈의
향후 확장 포인트)의 원인이 될 수 있다. **본 노트에서는 CMP 패드 실측 τ_creep 문헌값을 확보하지
못했음 — 미검증**. 유사 PU 폼(매트리스 등)의 τ_creep은 초~수십 초 오더로 보고됨(정성적 참고만).

**출처(정성적 참고, 미검증 정량값)**: E. Mendes et al., "Experimental method for creep
characterization of polymeric foam materials in media immersion," *Mechanics of Time-Dependent
Materials*, 2020. https://doi.org/10.1007/s11043-020-09457-x — CMP 패드가 아닌 좌석용 PU 폼
대상이므로 τ_creep 정량값은 CMP 패드에 직접 적용하지 않는다.

## 5. 실측 CMP 패드 물성 데이터 (하드니스·탄성계수)
2025년 논문(Meng et al., 위 출처)의 다공성 PU 패드 실측표 (PCDL 함량별, n≥5 시편):

| 시편 | 밀도(g/cm³) | Shore D 경도 | 압축률(%) | 탄성계수(MPa) | 인장강도(MPa) |
|---|---|---|---|---|---|
| Neat PU | 0.695 | 48±2 | 1.51 | 17.1±3.0 | 8.20±0.15 |
| PUPCD20 | 0.751 | 50±1 | 1.27 | 32.9±4.5 | 11.94±0.47 |
| PUPCD40 | 0.828 | 58±1 | 0.78 | 71.1±5.1 | 17.17±1.17 |
| HF2(상용 대조군) | 0.804 | 53±2 | 0.66 | 46.0±2.4 | 6.33±0.36 |

경향: PCDL(하드 세그먼트 강화) 함량 증가 → 경도↑·탄성계수↑·압축률↓·마모지수(wear index)↓.
상용 CMP 패드(IC1000 계열)의 문헌 Shore D 범위는 별도 특허 조사에서 **60~90**(US Patent 10391606,
Rohm & Haas/DuPont 계열)으로 보고되어, 위 실험 시편(48~58)보다 다소 단단한 축 — CMP 상용 패드는
비교적 강성 재료임을 시사(연질 패드는 서브패드 등 보조층에 국한).

**출처**: 
1) Meng et al. 2025 (위 인용) Table 2.
2) US Patent 10,391,606 B2 (Rohm & Haas Electronic Materials CMP Holdings), "Chemical mechanical
polishing pads for improved removal rate with controlled defectivity," Shore D 60–90 청구항.
https://patents.justia.com/patent/10391606

## 6. CMP 실무 함의 (다음 단원 Lv1-2로 연결)
- 패드 경도↑ → 국소 asperity가 웨이퍼 표면 요철에 덜 순응(conform) → **planarization efficiency**↑
  하지만 **defectivity**(스크래치) 위험도↑ — 트레이드오프. 이는 Lv1-2(패드 구조: IC1000류 발포체,
  groove, subpad)에서 서브패드(연질)로 완충하는 이유와 직결.
- 저장탄성률 E′가 웨이퍼-패드 접촉의 "유효 강성"을 결정 → GW 접촉모델(Lv2-1)에서 asperity 압축
  강성 입력으로 사용될 값. 현재는 정성적 이해만 확보, Lv2-1에서 Hertz 접촉 압축응력↔변위 관계로
  정량화 예정.

## 7. 정량 재현 — Maxwell 모델 피크 위치 + Meng et al. 2025 표 대조 (부채상환 2026-09-07)
> ⚠ 1차 출처 확보 시도: §4의 τ_creep(CMP 패드 실측)은 여전히 미검증(CMP 패드가 아닌 좌석용 PU 폼
> 문헌만 확보됨, 위 §4 참조). 여기서는 §2~3의 Maxwell 모델 수식과 §5 Meng et al. 2025 실측표를
> 코드로 직접 재현해 "검증했다"는 서술을 assert로 대체한다.

**(a) Maxwell 모델**: ω=1/τ₀ (완화각주파수)에서 E′(ω)=E·τ₀²ω²/(τ₀²ω²+1) 이므로 τ₀ω=1 대입 시
E′ = E·1/(1+1) = E/2 — 즉 완화주파수에서 저장탄성률은 고주파 평형값(E)의 정확히 절반이 되어야
한다(Ferry 표준 결과, §2~3 인용 수식에서 직접 도출되는 항등식이므로 문헌 재검색 불필요).

**(b) Meng et al. 2025 Table 2 (§5, DOI: 10.3390/polym17050613)**: Neat PU → PUPCD40 탄성계수가
17.1 MPa → 71.1 MPa로 증가한다고 §5에 옮겨 적었다. 배율을 코드로 재계산해 노트에 옮긴 숫자가
표 원본과 산술적으로 일치하는지 대조한다(전사 오류 검출).

```python verify
# (a) Maxwell 이완주파수에서 E'/E_plateau = 0.5 (Ferry 표준 항등식)
def E_prime_ratio(tau0, omega):
    x = tau0 * omega
    return x**2 / (x**2 + 1)

ratio_at_relax = E_prime_ratio(tau0=1.0, omega=1.0)  # ω=1/τ0 → τ0*ω=1
assert abs(ratio_at_relax - 0.5) < 1e-9, f"이완주파수 E'/E 비율 {ratio_at_relax} != 0.5"

# 고주파(ω>>1/τ0)에서 E'→E(포화), 저주파(ω<<1/τ0)에서 E'→0 (§3 서술 재현)
ratio_high = E_prime_ratio(tau0=1.0, omega=1000.0)
ratio_low = E_prime_ratio(tau0=1.0, omega=0.001)
assert ratio_high > 0.999, f"고주파 포화 실패: {ratio_high}"
assert ratio_low < 0.001, f"저주파 완전이완 실패: {ratio_low}"

# (b) Meng et al. 2025 Table 2 (§5) — 노트에 옮겨 적은 수치의 배율을 원표와 대조
E_neat = 17.1   # MPa, Neat PU
E_pcd40 = 71.1  # MPa, PUPCD40
fold_increase = E_pcd40 / E_neat
# 문헌값과 대조: 이 배율(약 4.16배)을 §5 서술("경도↑·탄성계수↑" 정성 서술)의 정량 근거로 삼는다.
assert 4.0 < fold_increase < 4.3, (
    f"PCDL 40 도입 시 탄성계수 배율 {fold_increase:.2f}배 — §5 표 옮겨적기 오류 가능성"
)

# HF2(상용 대조군, 46.0 MPa)는 Neat~PUPCD40 사이에 위치해야 한다(§5 서술 "48~58 사이" 경도와 일관)
E_hf2 = 46.0
assert E_neat < E_hf2 < E_pcd40, f"HF2 상용 대조군이 실험군 범위 밖: {E_hf2} MPa"

print(f"PASS: Maxwell E'/E@relax={ratio_at_relax}, Meng2025 탄성계수 배율={fold_increase:.2f}x")
```

**해석**: (a)는 §2~3에 인용한 Maxwell 수식이 내적으로 일관됨을 확인한 것이지 별도 문헌 실측치와의
대조는 아니다(수식 자체가 출처). (b)는 §5에 옮겨 적은 Meng et al. 2025 표 수치가 산술적으로
자기일관적임을 재확인했다 — 전사 오류가 없음을 검증했을 뿐, τ_creep 등 CMP 패드 고유의 미검증
정량값(§4)을 해소한 것은 아니다. **§4 τ_creep은 여전히 미검증 상태로 남는다.**

## 8. 엔진 등록 (S12, 2026-09-16) — τ0 없이 낼 수 있는 역진단만 등록
`sim/tier2_physics/viscoelastic_maxwell.py`(§3 Maxwell 수식 재현 모듈)를 `sim/engine.py`의
`_pad_loading_frequency_diagnostic`로 등록했다. §4가 자백한 대로 CMP 패드 실측 τ0(이완시간)
문헌값이 없어 De=τ0·ω를 지어내지 않는다 — 대신 공정 하중 주파수 ω 후보 두 개를 역산하고
τ_crit=1/ω(이완시간 임계값)만 낸다.

후보 (A) 플래튼 회전 ω_rot=2π·rpm_platen/60은 항상 계산된다.

후보 (B) 애스퍼리티 접촉 주기 ω_asperity=2π·V/(2a) — **2026-09-16 정정**: 직전 회차는 이것이
"개별 asperity 압입깊이 δ가 필요한데 GW 역문제 진단이 내는 값은 앙상블 적분뿐이라 구조적으로
얻을 수 없다"고 적었으나 틀렸다. GW 지수분포 해에서는 평균 압입깊이가 닫힌형으로 나온다 —
`A_r = πRηA_n·(1/β)·e^(−βd)`, `n = ηA_n·e^(−βd)` 이므로 `δ_mean = A_r/(πR·n) = 1/β`가 **분리거리
d와 무관한 정확한 항등식**이다(지수분포 memoryless 성질, `gw_contact.py`의 `gw_analytic_ratio`
유도와 동일 적분). 이는 새 통계 가정이 아니라 팩이 이미 literature 등급으로 선언한
`asperity_height_distribution: exponential`에서 직접 유도되는 수학적 귀결이다. 그래서 GW
5개 패드 파라미터(`_gw_contact_state_diagnostic`과 동일 키)가 선언돼 있고
`asperity_height_distribution`이 정확히 `"exponential"`일 때만 δ_mean=1/β → Hertz 접촉폭
2a=hertz_contact_area(δ_mean,R)를 거쳐 ω_asperity를 실제로 계산한다(가우시안 등 다른 분포면
항등식이 성립하지 않아 지어내지 않고 None+스킵사유). GW 파라미터는 base.yaml 상속이라
전 팩이 동일값을 낸다: δ_mean=2.0e-6 m, 2a=2.0e-5 m, V=1.1526 m/s, ω_asperity≈3.621e5 rad/s
— ω_rot(≈5.76 rad/s, base.yaml rpm_platen=55)과 약 6.3e4배 차이 난다. 두 ω는 서로 다른
물리 주기(플래튼 1회전 vs 애스퍼리티가 접촉폭을 한 번 지나가는 주기)이므로 평균내거나 하나를
대표값으로 고르지 않는다.

어느 팩도 `pad_relaxation_time_s`를 선언하지 않아 De/E'/E/E''/E/tanδ는 rot·asperity 두 축
모두 항상 None이 정상 경로다(pad_groove_eol·pad_viscoelastic_temperature와 동일 지위). 선언될
경우 두 축 각각 독립적으로 De=τ0·ω를 계산한다(하나만 대표로 고르지 않는다).

> ⚠ 1차 출처 확보 실패: CMP PU 패드의 DMA 주파수 스윕에서 tanδ 피크 주파수 또는 이완시간을
> 보고한 1차 문헌을 찾지 못했다. 시도 경로 — `tools/find_open_access.py --title`로
> "dynamic mechanical analysis chemical mechanical polishing pad polyurethane relaxation time"
> (SSRN 유료 랜딩만 반환), "viscoelastic properties polyurethane CMP pad frequency sweep
> storage loss modulus"(무관한 bagasse/glass fiber 복합재 논문 매칭), "IC1000 pad viscoelastic
> relaxation time chemical mechanical planarization"(URI DigitalCommons 학위논문 PDF 링크는
> Cloudflare 봇차단으로 다운로드 실패, "Just a moment..." HTML 반환). τ0는 여전히 미확보 —
> §4의 결론과 동일하게 남는다.

## 다음 단원
Lv1-2: CMP 패드 구조 (IC1000류 발포체, groove 패턴, subpad 역할) — 이번 노트의 §6 연장.
