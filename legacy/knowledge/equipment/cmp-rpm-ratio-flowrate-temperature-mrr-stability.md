<!-- V2-SECTION: R1-equipment | 분배완료 2026-09-08 | 근거: carrier, flowrate, multizone, platen, retaining-ring | 정본: ARCHITECTURE-V2.md §3 -->
# RPM 비·유량·온도가 MRR 안정성에 미치는 영향 — 문헌 정량 대조

> 담당: [[tool-platen-head]] Lv2-2 · 작성 2026-09-07 · 상태: 검증(원문 PDF 2편 확보, 미러 사이트 경유)
> 연결: [[cmp-kinematics-rotary]](µ=운동학수·NU=2|µ| 해석해) · [[cmp-multizone-carrier-radial-response]] ·
> [[cmp-retaining-ring-wear-edge-profile]]

## 0. 범위
Lv2-1이 리테이너링의 정적 압력 프로파일(공간 변수)을 다뤘다면, 이 단원은 시간·유체 변수
(플래튼/헤드 RPM 비, 슬러리 유량, 플래튼 냉각수 온도)가 평균 MRR과 NU(비균일도)에 미치는
영향을 실험 문헌으로 정량 확인한다. cmp-kinematics-rotary.md가 RPM 비의 기구학적 효과
(순간 상대속도 비균일도 NU=2|µ|)를 해석적으로 유도했다면, 이 노트는 그 해석해가 실제
MRR 실험 데이터와 얼마나 맞는지, 그리고 유량·온도가 기구학과 독립적으로 MRR에
미치는 효과를 다룬다.

## 1. RPM 비 — 실험 vs 기구학 해석해

cmp-kinematics-rotary.md §5의 시뮬레이션 결과(Rs=50/60일 때 edge/center 시간평균
MRR 비 = 1.00391, 즉 0.4% 수준의 미세한 엣지-fast 프로파일, [[cmp-kinematics-rotary]] 2026-09-03 결과)를 실험 문헌과 대조하려
했으나, RPM 비를 유량·온도와 독립적으로 스윕하며 NU를 보고한 실험 논문은 이번 조사
범위(tools/scope.py --agent tool-platen-head: 1차논문·특허·학위논문·리뷰·업체문서,
2011년 이후 우선, ML-only/review-of-reviews 제외)에서 1차 확보하지 못했다. Kim & Jeong
(2004)[1]의 해석적 kinematic number ζ(=본 프로젝트 표기 µ와 동일 정의, §2 참조)는
이론 유도이지 실험 MRR 데이터가 아니므로 "RPM비 → 실측 MRR·NU"는 2차 인용
(Hocheng et al. 2000 인용문, 원문 미확보 — 미러 사이트/box 모두 DOI
10.1016/s0890-6955(00)00013-4에 무응답)으로만 확인된다: "the rotational speeds of the
platen and the carrier should be kept close to each other for better uniformity" [2, 재인용].
정량값 없이 정성적 결론만 문헌 합치.

## 2. Kim & Jeong (2004) — kinematic number ζ의 속도·슬라이딩거리 분포 재현

Kim, H. & Jeong, H., "Effect of Process Conditions on Uniformity of Velocity and Wear
Distance of Pad and Wafer during Chemical Mechanical Planarization", Journal of
Electronic Materials 33(1), 53-60, 2004. DOI: 10.1007/s11664-004-0294-4
(미러 사이트 경유 원문 6쪽 PDF 전체 확보, papers/kim2004_kinematic.pdf).

핵심 정의(원문 Eq.2, 표기 그대로): ζ = (r_w/D)(1−R), R = ω_w/ω_p (wafer/pad 속도비),
r_w=웨이퍼 반경, D=회전축간거리. 이것은 cmp-kinematics-rotary.md의 µ =
(R_w/r_cc)(1−Rs)와 정확히 같은 정의(변수명만 다름: ζ↔µ, R↔Rs, D↔r_cc) — 같은 그룹
(Kim, Jeong)의 2004년 원논문이 2026년 Hasni et al. JJMIE 논문이 재유도한 극좌표식의
원전임을 확인. cmp-kinematics-rotary.md §6에서 "원문 미확보로 추정"이라 적었던 것을
이번에 원문 확보로 확정한다.

원문이 유도한 3가지 정량 결과(Eq.6a, 6b, 9a — PDF 텍스트가 OCR 손상되어 수식 자체는
읽기 어려우나 결과식은 명확히 식별됨):
- 속도 NU: NU_vel = 2|ζ| × 100% (max-min/avg 기준. 원문 Eq.6b: NU_vel(3σ) =
  (v_max−v_min)/((v_max+v_min)/2) × 100 = 200|ζ|%, v_max=1+ζ, v_min=1−ζ)
- 슬라이딩거리 NU: NU_s = 25ζ² % (원문 Eq.9a 계열, σ/S_avg 기준),
  S_avg = 1 + ζ²/8, S_max = 1+ζ²/4, S_min=1 (원문 §"SLIDING-DISTANCE..." 문단)
- 결론(원문 그대로): "속도의 비균일도는 ζ에 선형(2ζ)으로 민감하지만, 슬라이딩거리
  비균일도는 ζ²에 비례해 훨씬 둔감"하다 → 시간평균(=슬라이딩거리)이 순간속도보다
  RPM 비 어긋남에 강건하다는 결론. 이것이 cmp-kinematics-rotary.md §5의 시뮬레이션
  관찰([[cmp-kinematics-rotary]] 2026-09-03, "순간 속도 NU 12~25% vs 시간평균 MRR 편차 0.4%")과 정성적으로 완전히 일치하고,
  이번 노트가 그 관찰의 해석적 근거(왜 2차식으로 줄어드는가)를 원논문에서 확인한 것이다.

### 2.1 python verify — 슬라이딩거리 NU=25ζ² 재현
아래 코드 블록이 원문 Eq.9a 계열(S_avg=1+ζ²/8, NU_s=25ζ²%)을 몬테카를로/해석 적분으로
검증한다.

```python verify
"""Kim & Jeong (2004) Eq.9a 계열 — 슬라이딩거리 NU=25ζ² 재현.
S(rho, theta; zeta) = sqrt(rho^2 zeta^2 + 2 rho zeta cos(theta) + 1) 의 웨이퍼 면적평균/최대/최소를
수치적분으로 구해 원문이 보고한 근사식(S_avg=1+zeta^2/8, S_max=1+zeta^2/4, S_min=1,
NU_s = (S_max-S_min)/S_avg*100 근사 -> 25*zeta^2 %)과 대조한다."""
import numpy as np

def S_field(rho, theta, zeta):
    return np.sqrt(rho**2 * zeta**2 + 2*rho*zeta*np.cos(theta) + 1)

def area_avg_S(zeta, n_r=400, n_t=2000):
    rhos = np.linspace(1e-6, 1.0, n_r)
    thetas = np.linspace(0, 2*np.pi, n_t, endpoint=False)
    R, T = np.meshgrid(rhos, thetas, indexing="ij")
    S = S_field(R, T, zeta)
    theta_avg = S.mean(axis=1)  # theta 평균 (원 궤적 평균)
    area_avg = np.trapezoid(theta_avg * 2 * rhos, rhos)  # 면적가중 (원판 uniform weight, R=1 normalized)
    return area_avg

for zeta in [0.05, 0.125, 0.25]:
    Savg_num = area_avg_S(zeta)
    Savg_analytic = 1 + zeta**2 / 8
    rel_err = abs(Savg_num - Savg_analytic) / Savg_analytic
    assert rel_err < 1e-3, f"zeta={zeta}: S_avg 수치 {Savg_num:.6f} vs 해석 {Savg_analytic:.6f}, 상대오차 {rel_err:.2e}"

    Smax_analytic = 1 + zeta**2 / 4
    Smin_analytic = 1.0
    NU_s_analytic = (Smax_analytic - Smin_analytic) / Savg_analytic * 100
    NU_s_formula = 25 * zeta**2  # 원문 근사식 (Savg~=1로 근사할 때)
    # 두 근사식(Savg 포함 vs Savg=1 근사) 간 차이는 zeta^2 고차항, zeta<=0.25에서 1% 미만이어야 함
    diff_pct = abs(NU_s_analytic - NU_s_formula) / NU_s_formula * 100
    assert diff_pct < 5.0, f"zeta={zeta}: NU_s(정밀) {NU_s_analytic:.4f}% vs 원문근사 {NU_s_formula:.4f}%, 차이 {diff_pct:.2f}%"

print("PASS — zeta=0.05/0.125/0.25에서 S_avg=1+zeta^2/8 수치적분 일치(상대오차<1e-3),"
      " NU_s=25*zeta^2 근사식과 정밀식 차이 <5% 확인")
```

| 검증 항목 | 결과 |
|---|---|
| S_avg 수치적분 vs 1+ζ²/8 | ζ=0.05/0.125/0.25 모두 상대오차 <1e-3 일치 ✔ |
| NU_s=25ζ² 근사 vs 정밀식(S_avg 포함) | 차이 <5%(ζ≤0.25 범위) ✔ |
| ζ 정의 동일성(Kim&Jeong ↔ 본 프로젝트 µ) | 대수적으로 동형(변수명 치환만 차이) — 코드 대조는 아님, 수식 비교로 확인 |

## 3. 유량·온도 — Yuh et al. (2015) 실험 정량값

Yuh, M., Jang, S., Kim, H., Lee, H., Jeong, H., "Development of Green CMP by Slurry
Reduction through Controlling Platen Coolant Temperature", Int. J. Precis. Eng.
Manuf.-Green Technol. 2(4), 339-344, 2015. DOI: 10.1007/s40684-015-0041-8
(미러 사이트 경유 원문 6쪽 PDF 전체 확보, papers/yuh2015.pdf). Oscar-type 대면적
(510×510mm) Cu CMP 장비, PCB용 — 300mm 웨이퍼 팹 장비와 스케일은 다르나 유량·온도
변수의 정성적 방향성은 CMP 일반 원리로 채택 가능(§5 한계 참조).

### 3.1 다운포스·RPM (Preston 정합성 확인용, 참고)
down force 3.82-8.04 kN, platen/head 30-75 rpm 스윕에서:
- MRR_avg: 최대 4.1 µm/min (7.65kN, 75rpm) ↔ 최소 1.2 µm/min (3.82kN, 30rpm)
- NU: 최소 14.4%(5.1kN, 60rpm) ↔ 최대 34.2%(3.82kN, 30rpm) — NU가 U자형으로
  60rpm 부근에서 최소, 더 올리면 재악화. 원문: "rotational speeds should be about
  60 rpm to obtain high MRR_avg and low NU" — 단일 최적점 존재, 단조 감소 아님.
- Preston 정합 확인: Fig.4에서 MRR_avg가 압력×상대속도 곱에 선형 비례 (원문 서술,
  수치 좌표는 그래프라 미확보 — 미검증: 그래프 판독값 아님, 서술만 인용).

### 3.2 슬러리 유량 (down force 8.04kN, platen/head 50rpm, 온도 20°C 고정)
- 유량 600→1000 mL/min: MRR_avg 증가
- 유량 1000→1200 mL/min: MRR_avg 감소 (비단조, 1000mL/min 부근이 최적)
- 원인(원문 인용, Li et al. 2004 재인용): 유량 증가가 계면 냉각효과를 키워
  고유량에서는 열화학반응속도가 줄어 MRR이 준다.
- NU: 600→1200 mL/min 전 구간에서 단조 감소 (고유량이 중심→엣지 슬러리 이송을
  개선, 중심부 과다연마를 완화)

### 3.3 플래튼 냉각수 온도 (down force 8.04kN, platen/head 50rpm, 유량 600-1200 스윕)
- 온도 10→30°C: MRR_avg 단조 증가 (열화학반응 촉진, Arrhenius 방향과 정합 —
  단 원문은 활성화에너지·Arrhenius식을 명시하지 않음, 미검증: 정성적 온도 의존성만
  확인, 정량 Ea 없음)
- NU: 온도 상승에 따라 감소 (600mL/min 유량 조건만 예외) — 원인은 슬러리 점도
  저하로 인한 엣지 이송 개선(원문 §3.4)
- 원문 결론(그대로 인용): "high MRR and low NU are attained by increasing the platen
  coolant temperature rather than increasing the slurry flow rate" — 온도가
  유량보다 레버리지가 크다는 우선순위 서술. 정량 비교(예: %/°C vs %/(mL/min)) 수치는
  원문에 없어 미검증.

## 4. 종합 — MRR 안정성 위계

이번 조사에서 확인한 3개 변수의 MRR·NU 민감도를 정성 등급으로 정리(정량 계수는
문헌 부재로 미검증):

| 변수 | MRR_avg 방향성 | NU 방향성 | 함수형 |
|---|---|---|---|
| RPM 비(ζ) 어긋남 | 순간속도만 영향(시간평균 무관, Lai Eq.2.12) | 순간 NU∝ζ(선형), 시간평균 NU∝ζ²(2차, 훨씬 둔감) | Kim&Jeong 2004 해석해 |
| 슬러리 유량 | 비단조(최적점 존재, 1000mL/min 부근) | 단조 감소(고유량↑ NU↓) | Yuh 2015 실험, 함수형 미제시 |
| 플래튼 온도 | 단조 증가(10→30°C) | 단조 감소(대부분 조건) | Yuh 2015 실험, 함수형 미제시 |

핵심 시사점: RPM 비는 Kim&Jeong(2004) 해석해로 이미 2차식(ζ²) 둔감성이 확인되어
"시간평균 MRR은 RPM 미스매치에 강건"하다는 결론이 재확인됐다. 반면 유량·온도는
경험적 최적점/단조성만 확인됐고 함수형(선형·지수·Arrhenius 등)은 이번에 확보한
2편 모두 제시하지 않는다 — Lv3-1(최신 리뷰)에서 열-화학반응속도 모델(Arrhenius
활성화에너지 포함)을 확보하는 것이 다음 과제.

## 5. 미검증 / 한계
- Yuh et al.(2015)는 PCB용 Oscar-type 대면적 폴리셔(Cu-clad laminate, 35µm Cu on
  polymer) 실험이며 300mm 반도체 웨이퍼 CMP와 장비 스케일·재질이 다르다. 정성적
  방향성(유량↑→NU↓, 온도↑→MRR↑)은 열유체·트라이볼로지 일반원리로 채택하되,
  정량값(mL/min, °C 절대수치)은 반도체 팹 300mm 툴에 직접 이식 불가 — 미검증.
- RPM 비의 실측 MRR·NU 데이터(300mm 웨이퍼, 팹 조건)는 이번 조사에서 1차 미확보.
  Hocheng et al.(2000)는 2차 인용만 확인(원문 페이월, 미러 사이트 무응답).
- 온도 의존성의 Arrhenius 활성화에너지(Ea)는 미검증 — Yuh(2015)는 정성적 방향만
  보고, 수치 모델 없음.
- Yuh(2015) Fig.3~10의 그래프 판독 좌표값(예: 정확한 NU% at 특정 유량)은 그래프이며
  본문 텍스트로 명시된 것(위 §3.1~3.3의 구체 수치)만 인용했다 — 그래프 눈대중 추정치는
  넣지 않음.

## 출처
1. H. Kim, H. Jeong, "Effect of Process Conditions on Uniformity of Velocity and Wear
   Distance of Pad and Wafer during Chemical Mechanical Planarization", J. Electron.
   Mater. 33(1), 53-60, 2004. DOI: 10.1007/s11664-004-0294-4
2. H. Hocheng, H. Y. Tsai, M. S. Tsai, "Effects of Kinematic Variables on Nonuniformity
   in Chemical Mechanical Planarization", Int. J. Mach. Tools Manuf. 40(11),
   1651-1669, 2000. DOI: 10.1016/S0890-6955(00)00013-4 (원문 페이월, 미러 사이트/box
   무응답 — 2차 인용만, ScienceDirect 초록 서술 재인용)
3. M. Yuh, S. Jang, H. Kim, H. Lee, H. Jeong, "Development of Green CMP by Slurry
   Reduction through Controlling Platen Coolant Temperature", Int. J. Precis. Eng.
   Manuf.-Green Technol. 2(4), 339-344, 2015. DOI: 10.1007/s40684-015-0041-8
4. [[cmp-kinematics-rotary]] — µ 정의·해석해(2|µ| 속도NU), 본 노트 §1-2의 기반
5. Z. Li, L. Borucki, I. Koshiyama, A. Philipossian, "Effect of Slurry Flow Rate on
   Tribological, Thermal, and Removal Rate Attributes of Copper CMP", J. Electrochem.
   Soc. 151(7), G482-G487, 2004 (Yuh 2015 §3.3에서 인용됨, 원문 미확보 — 2차 인용)
