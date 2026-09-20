<!-- V2-SECTION: R5-wafer | 공동: R2-slurry | 분배완료 2026-09-08 | 근거: metrology, roughness, wafer- | 정본: ARCHITECTURE-V2.md §3 -->
# 표면 조도(Ra·Rq·Rz)와 AFM 스캔 크기 의존성 — CMP 후 막질별 문헌값 범위

> 에이전트: wafer-metrology Lv2-1 | 작성일: 2026-09-06
> 선행: [[wafer-metrology-thickness-methods]] [[uniformity-metrics-definitions-standards]]

## 1. Ra·Rq·Rz 정의 — AFM이 실제로 무엇을 계산하는가

AFM은 탐침이 표면을 따라가며 얻은 높이맵 z(x,y)에서 통계 파라미터를 계산한다.
스캔 라인(또는 면적) 안에서 평균면을 0으로 맞춘 뒤:

- **Ra** (arithmetic mean roughness) = (1/N)·Σ|z_i| — 절대편차 평균. 이상점(스크래치·파티클)에
  둔감해 가장 널리 보고되지만 분포 형태 정보를 버린다.
- **Rq (RMS roughness)** = sqrt((1/N)·Σ z_i²) — 표준편차와 동일(평균면=0이므로). 큰 편차에
  제곱으로 가중되어 스크래치·핏에 더 민감하다.
- **Rz** = 상위 5피크 평균높이 − 하위 5밸리 평균깊이(ISO 4287) 또는 최대 피크-밸리(ASME식과
  ISO식이 다름 — 어느 표준인지 병기 필요, 두 표준의 정확한 수식 차이는 원문 대조를 **확인 못함**).

가우시안(정규분포) 높이분포를 가정하면 Rq/Ra = sqrt(π/2) ≈ 1.2533이 수학적으로 유도된다
(Ra = σ·sqrt(2/π), Rq = σ). 이 관계는 ISO 4287 정의식 자체에서 나오는 항등식이며 CMP 논문을
따로 뒤질 필요가 없다 — 다만 이 특정 유도를 명시적으로 실은 1차 문헌은 이번 세션에서
특정하지 못했다(교과서적으로 통용되는 관계, **미검증** 표기).

## 2. AFM 스캔 크기가 커지면 왜 Rq가 커지는가 — self-affine(자기유사) 프랙탈 이론

CMP 폴리싱면을 포함한 많은 공학 표면은 완전히 랜덤(백색잡음)하지 않고, 넓은 대역에서
**self-affine fractal** 성질을 보인다. 이 경우 측정창(스캔 크기) L에 대해 RMS 조도가
w(L) ∝ L^H (H = 조도 지수/Hurst 지수, 0<H<1)로 커지다가 상관길이 ξ 이상에서 포화된다.
즉 "Rq 값"은 재질 고유 상수가 아니라 **스캔 크기의 함수**이며, 서로 다른 스캔 크기로 잰
두 보고값을 조도 크기 명시 없이 비교하는 것은 무의미하다.

- 이 스케일 의존성을 표면공학에서 처음 정식화한 고전 논문은 Sayles & Thomas (1978,
  *Nature* 271, 431, DOI: 10.1038/271431a0)로, 다수의 실제 엔지니어링 표면에서 측정
  RMS 조도가 시료 길이가 늘어나도 뚜렷한 상한 없이 계속 증가한다는 "non-stationary random
  process" 결과를 보고했다. **원문 확보 실패**(Nature 유료·미러 사이트/.st/.ru 전부 이 세션
  환경에서 접속 차단됨) — 표면계측학에서 통용되는 2차 인용 요약으로만 인용한다.
- 정량 모델로는 Palasantzas (1993, *Phys. Rev. B* 48, 14472, DOI: 10.1103/physrevb.48.14472)의
  K-correlation 모델이 있다. 초록(OpenAlex/기관 리포지토리 확인, 원문 PDF는 미확보)은
  "self-affine fractal 표면의 height-height correlation function에 대한 이론식을 STM으로
  측정한 은(Ag)·금(Au) 박막의 상관·표면폭(surface-width) 데이터와 비교했다"고 명시한다.
  즉 correlation length ξ와 조도 지수 H 두 파라미터로 Rq(L)의 스캔 크기 의존 곡선 전체를
  기술하는 표준적 접근이다. 구체적 H·ξ 수치는 원문 미확보라 이 노트에서 인용하지 않는다.

## 3. 막질별·슬러리별 문헌값 범위

- 확보한 정량 문헌값(2026년 논문, 1차 확인): SiC CMP에서 슬러리 화학(H₂O₂ 농도·pH)이 조도
  상한을 지배하며, 머신러닝 최적화 조건에서 실험 검증한 최종 표면조도가 **Ra ≤ 0.13 nm**로
  보고되었다(Wang et al. 2026, *Langmuir* 42(3):2851-2866, DOI: 10.1021/acs.langmuir.5c05695;
  Crossref 서지 확인 + OpenAlex 초록 확인, 본문 전체 미확보). 같은 연구에서 제거율(MRR)은
  기계적 파라미터가, 조도는 슬러리 화학이 각각 주로 결정한다고 구분했다.
- 커리큘럼이 요구한 SiO2/Cu/W 각각의 조도 대표값·범위는 이번 세션에서 1차 문헌 원문으로
  확정하지 못했다(검색 도구가 반환한 후보들이 CMP 조도가 아닌 다른 주제로 반복 오매칭됨).
  업계·문헌에서 통상 SiO2 CMP 후 RMS 조도가 서브나노미터대, Cu·W는 결정립 뽑힘(grain
  pull-out)·부식 특성 때문에 이보다 크다고 정성적으로 알려져 있으나, 이는 **추정**이며 이
  세션에서 DOI로 확인된 1차 수치가 아니다 — 다음 단원 재시도 항목으로 남긴다.
- 슬러리 입자 크기·패드 조도가 최종 표면 마무리(및 MRR)에 영향을 준다는 메커니즘 자체는
  Wang, Sherman, Chandra & Dornfeld (2005, CIRP Annals, DOI:
  10.1016/s0007-8506(07)60110-3, eScholarship OA 전문 확보·직접 읽음)가 다루지만, 이 논문은
  MRR 모델링이 중심이고 웨이퍼 최종 Ra/Rq 수치 자체는 보고하지 않는다(원문 확인 완료,
  조도 수치는 없음 — 인용 범위를 메커니즘 설명으로 한정).

## 4. 조도가 후속 리소·증착 공정에 미치는 영향

- **증착(step coverage/conformality)**: 거친 하지 위에 박막을 증착하면 하지의 요철이 후속
  막에 전파(telegraphing)되는 경향이 있다는 것은 박막 증착 공학의 오래된 일반 지식이며,
  진공증착의 step coverage를 다룬 초기 문헌 중 하나가 *Vacuum* 24(9):420 (1974, DOI:
  10.1016/0042-207x(74)92330-6)이다. 다만 이 문헌은 서지사항(제목·권호)만 확인했고 본문·
  저자명은 미확보라 구체적 수치 인용은 하지 않는다(**2차 인용** 수준으로만 취급).
- **리소(반사율·CD 제어)**: 거친 표면은 노광 시 산란광을 늘려 정재파(swing curve) 보정이나
  반사방지막 설계에 영향을 줄 수 있다는 것은 광학적으로 타당한 추론이지만, 이를 정량화한
  1차 문헌을 이번 세션에서 확보하지 못했다 — **미검증**, 다음 단원 재시도 대상으로 남긴다.
- 이 인과관계가 왜 중요한지는 [[uniformity-metrics-definitions-standards]]에서 다룬 "지표는
  측정 조건(edge exclusion 등)과 항상 함께 보고해야 한다"는 원칙과 같은 축이다 — 조도도
  스캔 크기를 명시하지 않으면 후속 공정 스펙 설정에 쓸 수 없는 반쪽 숫자가 된다.

## 5. Python 재현 — Ra/Rq 통계 관계 및 스캔 크기-Rq 스케일링

```python verify
import numpy as np

# (A) Ra/Rq 비율: 가우시안 높이분포 이론값 sqrt(pi/2) 대조 — §1
rng = np.random.default_rng(42)
z = rng.normal(0, 1.0, 2_000_000)
z -= z.mean()
Ra = np.mean(np.abs(z))
Rq = np.sqrt(np.mean(z ** 2))
calc_ratio = Rq / Ra
lit_ratio = np.sqrt(np.pi / 2)  # ISO 4287 정의에서 유도되는 이론값 — 1차 문헌 특정 못함(2차 인용 수준)
assert abs(calc_ratio - lit_ratio) / lit_ratio < 0.01, f"차이 {calc_ratio} vs {lit_ratio}"
print(f"(A) 계산 Rq/Ra={calc_ratio:.4f}배 vs 이론값 {lit_ratio:.4f}배 (문헌값 대조, 가우시안 가정)")

# (B) self-affine 스케일링: PSD ~ q^-(2H+1)로 합성한 1D 프로파일에서
#     창 크기(스캔 길이) L을 늘릴수록 Rq(L) ∝ L^H로 커지는지 확인 — §2
#     H=0.75는 예시로 지정한 합성 파라미터이며 CMP 실측 문헌값이 아니다(확인 못함, 자기 재현 확인용)
N, H = 4096, 0.75
q = np.fft.rfftfreq(N)[1:]
amp = q ** (-(H + 0.5))
phase = rng.uniform(0, 2 * np.pi, len(q))
spec = np.zeros(N // 2 + 1, dtype=complex)
spec[1:] = amp * np.exp(1j * phase)
z2 = np.fft.irfft(spec, n=N)


def rq_at_window(window):
    n_win = N // window
    vals = [np.sqrt(np.mean((z2[i * window:(i + 1) * window]
                              - z2[i * window:(i + 1) * window].mean()) ** 2))
            for i in range(n_win)]
    return np.mean(vals)


windows = [32, 64, 128, 256, 512, 1024]
rqs = [rq_at_window(w) for w in windows]
assert rqs[-1] > rqs[0] * 2, "스캔 크기가 커져도 Rq가 커지지 않음 — 스케일 의존성 재현 실패"
slope, _ = np.polyfit(np.log(windows), np.log(rqs), 1)
calc_value = slope
lit_value = H
assert abs(calc_value - lit_value) / lit_value < 0.5, f"차이 {calc_value} vs {lit_value}"
print(f"(B) 복원 지수 {calc_value:.3f} vs 입력 H={lit_value:.2f} "
      f"— Rq(32)={rqs[0]:.3f} → Rq(1024)={rqs[-1]:.3f} (스캔크기 32배 시 Rq 증가, 자기유사 스케일링 자기검증)")
```

## 6. 정량 재현 요약

| 항목 | 계산값 | 대조 기준 | 상태 |
|---|---|---|---|
| Rq/Ra (가우시안) | ≈1.2533배 | 이론값 sqrt(π/2)=1.2533배 | 일치(<1% 오차), 1차 문헌 특정 못함 |
| Rq(L) 스케일링 지수 | 슬로프 회귀값 | 합성 입력 H=0.75 | 일치(<50% 오차) — **문헌 실측 H 대조 아님**, 이론식 자기재현 |
| Rq(1024)/Rq(32) | >2배 | 정성적 방향(스캔↑→Rq↑) | 재현됨 — Sayles&Thomas 1978 개념과 부호 일치(원문 미확보) |
| SiC CMP Ra | — | 문헌값 Ra ≤ 0.13 nm (Wang et al. 2026) | 인용만, 자체 재현 대상 아님(실험 프로세스 값) |

## 7. 남은 미확보·미검증 항목 (정직성 표기, 다음 재시도 대상)

- Sayles & Thomas (1978) 원문: 미러 사이트/.st/.ru 전부 이 환경에서 접속 차단(WebFetch 거부) —
  **원문 미확보**, 2차 인용 수준 서술만 사용.
  Palasantzas (1993) 원문 PDF: 초록만 확인, 본문(H·ξ 수치) **미확보**.
- SiO2/Cu/W 각 막질의 CMP 후 대표 Ra/Rq 범위: 도구 검색이 반복적으로 무관한 제목에 매칭되어
  1차 문헌으로 확정 못 함. 정성적 순서(SiO2가 가장 낮고 Cu/W가 결정립 구조 때문에 더 거칠다)는
  **추정**이며 다음 단원 또는 재검색 대상.
- 리소 공정에 대한 조도 영향의 정량 문헌: **미검증**, 확보 못 함.
- Rz의 ISO식 vs 최대 피크-밸리식 차이: 정의 자체는 확인했으나 두 표준 수식의 정확한
  비교표는 원문 대조 **미검증**.
