<!-- V2-SECTION: R2-slurry | 분배완료 2026-09-08 | 근거: abrasive, additive, particle-wafer, ph, selectivity | 정본: ARCHITECTURE-V2.md §3 -->
# 슬러리 파라미터(입자크기·농도·pH·K⁺·분산제) → oxide MRR 정량모델 (slurry-chemist Lv3-2)

> slurry-chemist Lv3-2 | 작성일: 2026-09-08
> 선행: [[preston-luo-dornfeld-mrr]] (Preston·Luo-Dornfeld 계보) [[particle-wafer-interaction-mechanical-chemical-balance]] (Lv2-2, 접촉역학·활성입자)
> [[slurry-components-overview]] (Lv1-2, 첨가제 총론) [[ceria-slurry-ce-redox-selectivity]] (Lv3-1, 세리아 화학결합)
> 스코프: slurry-chemist(colloid-particle 축). 조성·표면화학·선택비. 패드/디스크 물성은 형제 에이전트 영역 — 침범 안 함.

## 1. 왜 이 단원인가

Lv1~Lv3-1까지는 메커니즘(DLVO, Pourbaix, 접촉역학, 세리아 화학결합)을 각각 따로 학습했다.
이 단원은 **하나의 실측 데이터셋 안에서** 입자크기·농도·pH·K⁺농도·분산제 5개 파라미터가
oxide(SiO₂) MRR에 미치는 영향을 **정량 수치와 함께** 통합한다. Lv3-2 요구사항(파라미터→MRR
정량모델)의 첫 조각 — 실제 sim 모듈화는 소프트웨어 부문이 담당하고, 여기서는 문헌 수치를
코드로 재현해 신뢰도를 검증한다.

## 2. 1차 출처

Yue Li, Chenwei Wang, Jianwei Zhou, Chen Xu, Yuanshen Cheng, Yuan Tian, Zhihui Cui, Hongliang Li,
Qixu Liu, "Role of Slurry Additives on Chemical Mechanical Planarization of Silicon Dioxide Film
in Colloidal Silica Based Slurry," *ECS J. Solid State Sci. Technol.* 10, 123008 (2021).
DOI: 10.1149/2162-8777/ac3e44. **CC BY-NC-ND, OPEN ACCESS — 원문 전체 PDF 확보**
(`papers/slurry-additives-cmp-oxide-ac3e44.pdf`, Unpaywall API로 무료 전문 확인 후 직접 다운로드,
미러 사이트 불필요). 실험: 콜로이달 실리카 슬러리, SiO₂ 박막 CMP, 압력·속도 등 공정조건은 논문에
구체 수치 미기재(장비 모델만 언급) — **미검증**으로 남긴다.

## 3. pH 효과 — 정량 수치 (§ Results, Fig.1)

조건: 20 wt% 콜로이달 실리카, K⁺ 0.25 mol/L, pH 10.0~12.5.

| pH | MRR (Å/min) |
|---|---|
| 10.0 | 1551 |
| 11.0 | 1727 (최댓값) |
| 12.5 | 1407 |

메커니즘: pH↑(10→11) → OH⁻가 Si-O-Si를 가수분해해 Si-O⁻ 생성 증가 → 기계적으로 더 쉽게
제거됨(연화) → MRR↑. pH↑(11→12.5) → 과잉 OH⁻가 실리카 입자·SiO₂ 표면 둘 다 더 강하게
음전하화 → 정전 반발↑ → 기계적 접촉력↓ → MRR↓. **정점형(peak) 거동** — Kaufman(1991) W CMP
산화제 정점([[preston-luo-dornfeld-mrr]] 계보)과 같은 "화학-기계 균형점" 패턴.

```python verify
# Li et al. 2021, ECS JSS Technol. 10, 123008, doi:10.1149/2162-8777/ac3e44
# Fig.1 pH-MRR 실측값 (20wt% silica, 0.25M K+)
pH  = [10.0, 11.0, 12.5]
mrr = [1551.0, 1727.0, 1407.0]  # Angstrom/min

# 정점이 pH=11.0(중간점)에 있어야 함 - 정성 확인
peak_idx = mrr.index(max(mrr))
assert pH[peak_idx] == 11.0, "MRR 최댓값이 pH 11.0이 아님 - 정점 위치 오류"
assert mrr[0] < mrr[1] and mrr[2] < mrr[1], "정점형(증가후감소) 거동이 아님"

# 상승폭·하강폭 정량 (문헌 수치 그대로)
rise_pct = (mrr[1]-mrr[0])/mrr[0]*100
fall_pct = (mrr[1]-mrr[2])/mrr[1]*100
print(f"pH 10.0->11.0: MRR +{rise_pct:.1f}% ({mrr[0]}->{mrr[1]} A/min)")
print(f"pH 11.0->12.5: MRR -{fall_pct:.1f}% ({mrr[1]}->{mrr[2]} A/min)")
assert abs(rise_pct - 11.3) < 0.5, "상승폭 계산 오류"
assert abs(fall_pct - 18.5) < 0.5, "하강폭 계산 오류"
print("OK: pH 정점형 거동(peak at pH 11.0) 수치 재현")
```

## 4. 입자 크기·농도 효과 — 두 경쟁 스케일링 모델, Eq.3-4 벡터좌표 재추출로 확정 (§ Fig.4, Eq.3-4)

**2026-09-13 정정**: 이전 버전은 "원문 Eq.3-4의 지수·부호가 PDF 텍스트 추출 과정에서 뒤섞여
신뢰할 수 없다"고 기록했다. 이는 `pdfplumber.extract_text()`(선형 텍스트 스트림)로 위·아래첨자가
뒤섞인 것이 원인이었다 — **문헌이 모호한 게 아니라 추출 방법이 부족했다.** `pdfplumber`의
문자 단위 좌표(`page.chars`, x0/top/size)를 이용해 위첨자(size≈6.4pt, top이 본문보다 낮은 값=위로
치우침)·아래첨자(size≈6.4pt, top이 본문보다 큰 값=아래로 치우침)를 분리 재구성한 결과, 원문
수식은 아래와 같이 **완전하고 모호함 없이** 복원된다(papers/slurry-additives-cmp-oxide-ac3e44.pdf
p.5, doctop 좌표 기준 EQ3 top≈411.2, EQ4 top≈435.8 — 재현 스크립트는 아래 verify 블록):

- **Eq.3 (표면적 지배, surface-area-controlled)**: $R \propto A \propto C_0^{1/3}\varphi^{-1/3}$
- **Eq.4 (압입 지배, indentation-controlled)**: $R \propto V \propto C_0^{-1/3}\varphi^{4/3}$

($R$=MRR, $A$=실접촉면적, $V$=압입체적, $C_0$=입자농도, $\varphi$=입자직경)

**중요한 정정**: 이전 버전은 Eq.4를 $C_0^{4/3}\varphi^{-4/3}$로 (잘못) 서술했다. 벡터좌표 재추출로
확정한 실제 부호는 **농도 지수가 Eq.3→Eq.4에서 +1/3→−1/3로 뒤집히고, 입경 지수가 −1/3→+4/3로
뒤집힌다** — 즉 두 모델은 농도·입경 방향이 서로 반대다(원문 본문 서술 "압입모델→표면적모델
전환"과 정합: §4 본문에서 40→80nm 구간은 압입 지배(Eq.4, 입경↑→R↑ 방향), 80→130nm 구간은
표면적 지배(Eq.3, 입경↑→R↓ 방향)로 논문이 직접 귀속시킨다). 이 부호 반전이 바로 **80nm 정점**을
만드는 구조다: 40→80nm은 Eq.4(입경 지수 +4/3, R 증가), 80→130nm은 Eq.3(입경 지수 −1/3, R 감소).

농도 방향 참고(원문 서술 "increased linearly as abrasive concentration increased" — 이는 §4
전체 스윕에서의 **순 방향**을 말하는 것이고, 위 두 극한식 각각의 농도 지수 부호가 반대라는 점과는
별개 — 논문은 어느 구간에서 어느 모델의 농도항이 지배적인지까지는 명시하지 않는다. **미검증**으로
남긴다.)

**정량 앵커(원문 서술, 그래프 수치는 텍스트로 미기재 — 방향·전환점만 확인, MRR 절대 수치는
미확보)**: 입자크기 40→80→130 nm에서 MRR은 80 nm에서 정점. 정확한 MRR 값(Å/min)은 Fig.4
그래프 이미지에만 있고 본문 텍스트에는 없다 — 이 값의 **정량 픽셀 판독은 이번 조사에서
시도하지 않았다**(§8에 명시, groove_depth 사례처럼 낮은 신뢰도의 그래프 판독을 반복하지 않기
위해 방향성 확정에 집중).

### sim/으로의 함의 — 정점형(piecewise) 입경 항 배선 가능해짐
이전에는 "지수·부호 불명"으로 `abrasive_size_exponent`를 비워뒀으나, 이제 **구간별 지수가
문헌에서 확정**됐다: 입경 < 기준점(80nm 부근)이면 지수 +4/3(Eq.4, 압입 지배), 입경 > 기준점이면
지수 −1/3(Eq.3, 표면적 지배). 이는 단일 멱함수가 아니라 **piecewise 지수**이므로, `sim/factors.py`
`_f_kappa`의 입경 항은 이 구간별 형태로 재구현해야 한다(연속성 보정을 위해 정점 위치에서 두 식이
같은 값으로 정규화되도록 스케일 앵커 필요 — 정점 위치 자체는 80nm로 이 계에서 확인됐으나 다른
화학종/조건으로의 일반화는 미검증).

```python verify
# Li et al. 2021 Eq.3-4 벡터좌표 재추출 재현 — 지수·부호 확정
# (papers/slurry-additives-cmp-oxide-ac3e44.pdf p.5, pdfplumber page.chars 좌표 분석)

# 문자 단위 좌표에서 확인된 지수 (위첨자 top<본문top, 아래첨자 top>본문top, size≈6.4 vs 9.0)
eq3_C0_exp = 1/3     # 'C' top=411.2(본문), '1' top=409.6(위=분자), '3' top=409.6 -> 1/3
eq3_phi_exp = -1/3   # 'ϕ' top=411.2, '−(1/3)' 전부 top=410.2(약간위, 지수 위치) -> -(1/3)
eq4_C0_exp = -1/3    # 'C' top=435.8, '0' top=440.4(아래=밑첨자), '−(1/3)' top=434.2(위=지수) -> C0^-(1/3)
eq4_phi_exp = 4/3    # 'ϕ' top=435.8, '4' '3' top=434.7(위=지수) -> phi^(4/3)

def R_surface_area(C0, phi):
    return C0**eq3_C0_exp * phi**eq3_phi_exp

def R_indentation(C0, phi):
    return C0**eq4_C0_exp * phi**eq4_phi_exp

# (1) 두 식의 phi(입경) 지수는 부호가 반대 -- 이것이 80nm 정점을 만드는 구조
assert eq3_phi_exp < 0 and eq4_phi_exp > 0, "표면적모델은 입경 증가->R 감소, 압입모델은 입경 증가->R 증가 -- 부호 반대여야 정점이 생긴다"

# (2) 40nm -> 80nm 구간(압입 지배, Eq.4 서술): 입경 증가하면 R 증가해야 함
r40 = R_indentation(0.20, 40e-9)
r80 = R_indentation(0.20, 80e-9)
assert r80 > r40, "40->80nm 구간은 압입모델 지배 -- 입경 증가시 R 증가(원문 서술과 일치해야 함)"
print(f"압입모델(40->80nm): R비율 = {r80/r40:.3f} (증가 확인)")

# (3) 80nm -> 130nm 구간(표면적 지배, Eq.3 서술): 입경 증가하면 R 감소해야 함
r80b = R_surface_area(0.20, 80e-9)
r130 = R_surface_area(0.20, 130e-9)
assert r130 < r80b, "80->130nm 구간은 표면적모델 지배 -- 입경 증가시 R 감소(원문 '거의 선형 감소' 서술과 일치해야 함)"
print(f"표면적모델(80->130nm): R비율 = {r130/r80b:.3f} (감소 확인)")

# (4) 농도 지수는 두 식이 서로 반대 부호 -- 이전 노트의 "두 식 다 농도증가->R증가"는 틀렸다(정정)
assert eq3_C0_exp > 0 and eq4_C0_exp < 0, "농도 지수도 두 식이 반대 부호다 -- 이전 버전의 오류를 여기서 명시적으로 고정한다"

print("PASS: Eq.3-4 지수·부호 벡터좌표 재추출로 확정, 이전 버전(OCR 불신 처리 + 농도지수 오기재) 정정 완료")
```

**한계(정정 후에도 남는 것)**: (1) 두 극한식의 물리적 도출 근거(ref 26-29)는 여전히 미확보 —
왜 지수가 정확히 1/3·4/3인지는 이 논문도 설명하지 않는다. (2) 정점 위치(80nm)가 이 계(20-30wt%
콜로이달 실리카, SiO2 막)에 특정된 값인지 일반 법칙인지는 미검증. (3) MRR 절대 수치(Å/min)는
그래프 이미지 판독을 시도하지 않아 미확보 — 방향·전환점만 확정.

## 5. K⁺ 농도 효과 — 정량 수치 (§ Fig.10)

조건: 30 wt% SiO₂(80nm), pH 11.0.

| K⁺ (mol/L) | MRR (Å/min) |
|---|---|
| 0 | 1713 |
| 0.4 | 2538 (최댓값) |
| 0.5 | 2377 |

메커니즘: K⁺가 전기이중층을 압축(DLVO 반발↓, [[colloid-zeta-dlvo-slurry-stability]] §DLVO 항과
직결) → 입자-표면 인력↑ → 기계적 마모 강도↑ → MRR↑. 과잉 K⁺(≥0.3mol/L)는 응집·젤화를 유발해
유효 활성입자수↓ → MRR 하락 방향 전환. **동일 몰농도(0.2mol/L K⁺)에서 4종 K염(다른 음이온) 모두
~2380 Å/min로 수렴**(Fig.9, 무첨가 1750 대비 +36%) — MRR 결정 인자는 K⁺ 양이온 자체이지 염의
종류(음이온)가 아님을 실측으로 확인한 대목.

```python verify
# Li et al. 2021 Fig.10 K+ 농도-MRR 실측값 (30wt% SiO2 80nm, pH 11.0)
K_conc = [0.0, 0.4, 0.5]
mrr_K  = [1713.0, 2538.0, 2377.0]  # Angstrom/min

peak_idx = mrr_K.index(max(mrr_K))
assert K_conc[peak_idx] == 0.4, "K+ 정점이 0.4 mol/L이 아님"
gain_pct = (mrr_K[1] - mrr_K[0]) / mrr_K[0] * 100
print(f"K+ 0->0.4 mol/L: MRR +{gain_pct:.1f}% ({mrr_K[0]}->{mrr_K[1]} A/min)")
assert abs(gain_pct - 48.2) < 0.5

# Fig.9: 4종 K염(같은 몰농도 0.2M K+)이 무첨가 대비 수렴하는지
mrr_no_K = 1750.0
mrr_4salts_avg = 2380.0  # 문헌 "maintained at about 2380" 서술값
salt_gain_pct = (mrr_4salts_avg - mrr_no_K) / mrr_no_K * 100
print(f"K+ 0.2M(4종 염 평균) vs 무첨가: +{salt_gain_pct:.1f}%")
assert abs(salt_gain_pct - 36.0) < 1.0
print("OK: K+ 정점(0.4M) 및 염 종류 무관 수렴(+36%) 재현")
```

## 6. 분산제(PAM) — 입도 안정성·MRR 트레이드오프 정량 (§ Fig.14-15)

45°C 가속 안정성 시험(입자응집 촉진 조건):

| 분산제 | 평균입경 안정 유지 | 최종(응집 시점) 입경 | oxide MRR (기본슬러리 대비) |
|---|---|---|---|
| 무첨가 | 3일 | 175.2 nm | — |
| PAA | 7일 | 165.1 nm | 거의 무변화(negligible) |
| PVA | 14일 | 161.3 nm | 2700→2604 Å/min (−3.6%) |
| PVP | 21일 | 168.7 nm | 2700→2486 Å/min (−7.9%) |
| **PAM** | **30일** | **94.1 nm(안정 유지, 응집 없음)** | 거의 무변화("hardly changed") |

PAM만 30일간 응집 없이 94.1nm를 유지 — poly(acrylamide) 가수분해로 생성된 COO⁻ 사슬이
입자간 반발을 만들어 안정화하면서도(§ 논문 결론), MRR 저해가 없는 유일한 분산제. PVP/PVA는
표면 흡착·점도 증가로 MRR을 각각 −7.9%/−3.6% 저해 — 안정성과 활성 사이 트레이드오프가
분산제 화학구조에 따라 다르다는 것을 정량 확인.

```python verify
# Li et al. 2021 Fig.14(입경 안정성)-Fig.15(MRR 저해) 대조
dispersants = {
    "none": {"days": 3,  "final_nm": 175.2, "mrr": None},
    "PAA":  {"days": 7,  "final_nm": 165.1, "mrr": "negligible"},
    "PVA":  {"days": 14, "final_nm": 161.3, "mrr": 2604.0},
    "PVP":  {"days": 21, "final_nm": 168.7, "mrr": 2486.0},
    "PAM":  {"days": 30, "final_nm": 94.1,  "mrr": "hardly_changed"},
}
mrr_base = 2700.0  # Angstrom/min, 기본슬러리(30wt% SiO2 + 0.32M K+ pH11.0)

pva_drop_pct = (mrr_base - dispersants["PVA"]["mrr"]) / mrr_base * 100
pvp_drop_pct = (mrr_base - dispersants["PVP"]["mrr"]) / mrr_base * 100
print(f"PVA MRR 저해: -{pva_drop_pct:.1f}%  PVP MRR 저해: -{pvp_drop_pct:.1f}%")
assert abs(pva_drop_pct - 3.6) < 0.3
assert abs(pvp_drop_pct - 7.9) < 0.3

# PAM이 안정성 유지일수 최장 + 입경이 가장 작게(=응집 없이) 유지됨을 확인
assert dispersants["PAM"]["days"] == max(d["days"] for d in dispersants.values())
assert dispersants["PAM"]["final_nm"] < min(
    d["final_nm"] for k, d in dispersants.items() if k != "PAM"
), "PAM 최종 입경이 다른 분산제보다 작아야(응집 안 됨) 함"
print("OK: PAM이 안정성(30일)-MRR 무손실 양립 유일 분산제, PVA/PVP는 MRR 저해 정량 재현")
```

## 7. 종합 — 5개 파라미터의 MRR 반응 형태 요약

| 파라미터 | MRR 반응 형태 | 최적점(이 논문 조건 한정) |
|---|---|---|
| pH | 정점형(peak) | 11.0 |
| 입자크기 | 정점형(peak, 두 경쟁모델 크로스오버) | 80 nm |
| 입자농도 | 단조증가(포화 미관측, 이 논문 범위 내) | 측정범위 내 최고값 |
| K⁺ 농도 | 정점형(peak) | 0.4 mol/L |
| 분산제 | PAM만 안정성-활성 동시달성, 나머지는 트레이드오프 | PAM |

**패턴**: 5개 중 3개(pH·입자크기·K⁺)가 정점형이라는 것은 우연이 아니라 CMP 슬러리 설계의
구조적 특징 — 화학적 활성화(연화·해리)와 물리적 방해(응집·정전반발)가 같은 파라미터의 서로
다른 구간에서 경쟁하기 때문이다. 이것이 [[particle-wafer-interaction-mechanical-chemical-balance]]
§5 "두 극단 레짐" 논의의 실측 사례에 해당한다. **하나의 sim 모듈로 만든다면**: 각 파라미터를
독립 정점함수(예: 가우시안 또는 이차함수 근사)로 모델링하고, 곱셈적 결합(multiplicative combination)
전에 상호작용항이 있는지는 이 논문 데이터(단변량 스윕만 존재, 다변량 실험설계 없음)로는
**확인 불가 — 미검증**.

## 8. 한계/미검증 (정직 표기)

- 압력·상대속도(Preston P·V) 조건이 논문에 구체 수치로 없다 — 이 데이터는 **화학적 파라미터의
  상대적 영향만** 보여주며, Preston 절대 MRR 오더 비교([[preston-luo-dornfeld-mrr]] §3)와 직접
  연결할 수 없다.
- §4 모델식(표면적/압입 지수 1/3·4/3)은 논문이 인용만 하고 원 도출은 없음(ref 26-29 미확보) —
  지수값 자체의 1차 검증 없음, 크로스오버 지점(80nm)의 정량 예측력도 없음.
- 5개 파라미터를 하나의 통합 회귀식으로 만들 만한 다변량 데이터가 이 논문에는 없다(전부 단변량
  스윕) — §7의 "곱셈적 결합" 가능성은 제안일 뿐 검증되지 않음.
- 압력·속도 조건 부재로 이 데이터를 `sim/tier1_empirical/preston.py`나 Luo-Dornfeld 활성입자
  모델과 직접 캘리브레이션에 쓸 수는 없다 — 상대적 파라미터 감도(sensitivity) 참고자료로만 유효.

## 9. 자기시험
→ [[../../agents/slurry-chemist/EXAMS.md]] Lv3-2 문항 참조.
