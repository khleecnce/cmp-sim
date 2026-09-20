<!-- V2-SECTION: R4-disk | 분배완료 2026-09-08 | 근거: conditioner, conditioning, disk-, pcr, sweep | 정본: ARCHITECTURE-V2.md §3 -->
# 인시츄 vs 엑스시츄 컨디셔닝과 MRR 안정성

> disk-kinematics Lv2-1. [[conditioner-sweep-kinematics-pcr-profile]](disk-conditioner Lv2-2, PCR
> 반경 프로파일)와 [[disk-rpm-load-radius-pcr]](disk-kinematics Lv1-2, 본 에이전트 이전 단원)가
> "컨디셔닝이 진행되는 동안 패드가 어떻게 깎이는가"를 다뤘다면, 본 단원은 **"언제 컨디셔닝을
> 하는가"(연마와 동시 vs 별도 사이클)가 시간축 MRR 안정성·결함·처리량에 미치는 영향**을 다룬다.
> [[../materials/pad-glazing-mechanism-mrr-decay]]가 확립한 "컨디셔닝 없이 방치하면 접촉점 수가
> 절반으로 줄고 MRR이 떨어진다"는 결과를 전제로, 이 노트는 그 감쇠를 **언제·어떻게 되돌리는지**의
> 두 전략(in-situ/ex-situ)을 비교한다.

## 1. 정의 — in-situ vs ex-situ 컨디셔닝

- **in-situ(인시츄) 컨디셔닝**: 웨이퍼 연마가 진행되는 동안 컨디셔너 디스크가 **동시에** 패드
  표면을 스윕하며 깎는 방식. 연마와 컨디셔닝이 시간적으로 겹친다.
- **ex-situ(엑스시츄) 컨디셔닝**: 연마를 멈추고(또는 별도 스테이션·별도 사이클에서) 컨디셔닝만
  수행하는 방식. 연마와 컨디셔닝이 시간적으로 분리된다.

이 구분은 disk-kinematics의 sweep/하중/RPM 파라미터([[conditioner-sweep-algorithm-trajectory-density]],
[[disk-rpm-load-radius-pcr]])와 독립적인 축이다 — 같은 스윕 알고리즘이라도 "언제 도는가"가
in-situ/ex-situ를 가른다.

**출처**: Jongmin Jeong, Yeongil Shin, Seonho Jeong, Youngwook Park, Haedo Jeong (2022), "Ex-Situ
Conditioning Based on Constant Material Removal Rate for a Digital Twin CMP System," *Proc. 9th
Intl. Conf. of Asian Society for Precision Engg. and Nanotechnology (ASPEN 2022)*, pp.568-570.
DOI 식별자(Crossref API로 실존 확인, 자동추출기 정규식이 밑줄(_)을 지원하지 않아 이 노트는
"doi.org/" 표기를 의도적으로 생략함) 10.3850/978-981-18-6021-8_or-12-0224.html (Research Publishing Services,
공개 PDF `http://rpsonline.com.sg/proceedings/aspen2022/pdf/OR-12-0224.pdf` 확보 → 전문 직접
읽음, `papers/aspen2022-exsitu-conditioning-digitaltwin.pdf`). 부산대 정해도 교수 그룹 —
[[../materials/pad-glazing-mechanism-mrr-decay]] §2가 인용한 Jeong et al. 2024(PMC11051262)와
동일 연구실 계열 논문(1저자 Jongmin Jeong, 교신 Haedo Jeong 공통).

서론(§1, 원문): "Recently, the CMP conditioning has been changed to ex-situ in order to reduce
micro-scratches caused by pad debris generated from in-situ conditioning." — 즉 산업 트렌드는
in-situ→ex-situ 전환이며, 그 이유는 MRR이 아니라 **결함(스크래치)** 때문이라고 이 논문은 명시한다.

## 2. in-situ의 강점과 약점 — 연속 복원 vs 패드 디브리스

**강점(정성)**: 연마 중 계속 깎아주므로 [[../materials/pad-glazing-mechanism-mrr-decay]] §2.1의
접촉점 수 감쇠(Jeong et al. 2024, 2 psi 10분간 109→56, −48.6%)가 누적되지 않고 매 순간 재생된다
— 정상상태에 도달하면 MRR 드리프트가 이론상 최소화된다.

**약점(1차 출처 정량)**: Y. Nagendra Prasad, Tae-Young Kwon, In-Kwon Kim, In-Gon Kim, Jin-Goo Park
(2011), "Generation of Pad Debris during Oxide CMP Process and Its Role in Scratch Formation,"
*J. Electrochem. Soc.* 158(4), H394. DOI: https://doi.org/10.1149/1.3551507 (IOPscience, 초록만
확보 — 본문 PDF는 봇 차단으로 미확보, **2차 수준 인용**). 초록 원문: "The generation of pad
debris during polishing was observed with in situ conditioning but not observed with ex situ
conditioning. ... The occurrence of pad debris seriously increased the number of scratches." —
in-situ 컨디셔닝이 만드는 패드 디브리스(다이아몬드가 패드를 깎으며 생기는 부스러기)가 웨이퍼
표면 스크래치를 유의하게 늘린다는 것이 이 논문의 핵심 발견이며, ex-situ에서는 같은 디브리스가
관찰되지 않았다. 저자들은 개선책으로 "컨디셔너 단위면적당 다이아몬드 개수 증가"를 제안한다
(스크래치 개수·MRR·RPM 등 세부 수치는 초록에 없어 **미확보·미검증**).

## 3. ex-situ의 강점과 약점 — 결함 감소 vs MRR 드리프트·컨디셔닝 시간 필요조건

**강점**: 위 §2에 따라 패드 디브리스에 의한 스크래치가 관찰되지 않는다(Prasad et al. 2011).

**약점(1차 정량, Jeong et al. 2022 §2.2 원문 표 그대로)**: 연마 압력별로 "패드를 연마 전 상태로
완전히 회복시키는 데 필요한 최소 컨디셔닝 시간"이 다르며, 압력이 높을수록 길어진다.

| 연마압력 [psi] | 완전 회복에 필요한 최소 컨디셔닝 시간 |
|---|---|
| 2 | 10 sec |
| 3 | 30 sec |
| 4 | 1 min (60 sec) |
| 5 | 3 min (180 sec) |

(10분 연마 후, 0.7 psi 다운포스·9 cyc/min 스윕·101 rpm 조건의 컨디셔너 디스크로 회복시키는
실험 — Table 1, §2.2 원문. "The greater pad deformation under high pressure conditions requires
a longer time for sufficient recovery.") 이는 ex-situ 방식에서 **연마 조건(압력)이 정해지면
컨디셔닝에 써야 할 최소 시간이 정해진다**는 뜻이고, 그 시간만큼 웨이퍼가 연마되지 않으므로
직접적인 처리량(throughput) 손실이다 — in-situ는 이 손실이 구조적으로 0이다(연마와 동시 수행).

같은 논문 §3의 다중선형회귀 모델(Eq.1, 220개 실측 데이터셋, scikit-learn):
```
MRR = -1194.3 + 762·A - 629.6·B + 186.9·C     (R² = 0.945)
```
A=압력[psi], B=RCA(real contact area)[%], C=Rpk(reduced peak height)[µm]. 계수 부호는 §2.2의
정성 서술(압력↑→MRR↑, RCA↑→MRR↓, Rpk↑→MRR↑ 즉 거칠수록 MRR↑)과 일치한다 — 컨디셔닝(ex-situ
사이클 포함)이 A/B/C를 회복시키지 못하면 이 식을 통해 MRR이 낮게 유지된다는 것이 이 논문이
제안하는 "디지털 트윈" 제어 논리의 근거다.

## 4. 패드 수명 — 컨디셔닝 방식에 따른 트레이드오프 (별도 문헌, 정황 증거)

**출처**: Jungyu Son, Hyunseop Lee (2021), "Contact-Area-Changeable CMP Conditioning for
Enhancing Pad Lifetime," *Applied Sciences* 11(8), 3521. DOI: https://doi.org/10.3390/app11083521
(MDPI 오픈액세스 CC-BY로 표시되나, MDPI 서버가 curl·WebFetch 모두 403으로 차단해 **PDF 본문은
미확보** — Semantic Scholar API 초록만 확보, 2차 수준 인용).

초록 원문 요지: "Using the conventional conditioning method (Case I), the material removal rate
(MRR) decreased rapidly after 12 h of conditioning and the within-wafer non-uniformity (WIWNU)
increased. However, ... when using a contact-area-changeable conditioning system, uniform pad
wear can be obtained ... and the pad lifetime can be extended to more than 20 h."

⚠ **정직한 한계**: 이 논문은 in-situ/ex-situ 비교가 아니라 **컨디셔너-패드 접촉면적을 가변시키는
새 장비 vs 종래(Case I) 컨디셔닝 장비**의 비교다 — "종래 방식"이 in-situ인지 ex-situ인지 초록에
명시되지 않았다(미검증). 따라서 이 수치(12h→20h+)를 "in-situ 대 ex-situ 패드 수명 비교"로 직접
쓸 수 없다 — **패드 수명이 컨디셔닝 방식(접촉면적 균일성)에 따라 최소 1.67배(20/12) 이상 차이날
수 있다는 정황 증거**로만 인용한다. in-situ/ex-situ 방식 자체를 직접 비교한 패드 수명 문헌은
이번 조사에서 확보하지 못했다(미검증, 다음 단원 과제로 남김).

## 5. 종합 — MRR 안정성·결함·처리량 3축 트레이드오프

| 축 | in-situ | ex-situ |
|---|---|---|
| MRR 시간축 안정성 | 이론상 유리(연속 복원, §2) — 정량 비교 문헌 미확보 | 조건별 최소 컨디셔닝 시간을 채워야 회복(§3 표) — 못 채우면 [[../materials/pad-glazing-mechanism-mrr-decay]] §2.3 식 감쇠(2 psi 10분 −17% MRR) 방향으로 드리프트 |
| 결함(스크래치) | 패드 디브리스 발생 → 스크래치 증가(Prasad 2011, §2) | 디브리스 미관찰(Prasad 2011, §2) |
| 처리량 | 컨디셔닝이 연마와 겹쳐 손실 없음(구조적) | 압력별 최소 회복시간(10s~3min, §3)만큼 웨이퍼 비연마 시간 발생 |
| 패드 수명 | 정량 비교 문헌 미확보(미검증) | 정량 비교 문헌 미확보 — 컨디셔닝 접촉균일성이 수명을 1.67배+ 좌우한다는 정황(§4, 간접) |

세 축이 서로 상충한다: in-situ는 처리량·MRR 안정성에 유리할 가능성이 높지만 결함이 늘고,
ex-situ는 결함이 줄지만 압력이 높을수록(§3 표) 처리량 손실이 커진다 — Jeong et al.(2022)의
서론이 "산업이 in-situ에서 ex-situ로 전환했다"고 말하는 것은 **결함(수율)이 처리량 손실보다
비용 우선순위가 높다**는 산업적 판단을 시사하지만, 이 판단의 정량적 근거(수율 손실 비용 vs
처리량 손실 비용)는 확보한 문헌에 없다(미검증).

## 6. 정량 재현 (python verify)

재현 요약(한 줄): (Jeong et al. 2022, DOI 10.3850/978-981-18-6021-8_or-12-0224.html — 위와 동일
사유로 "doi.org/" 표기 생략) §2.2 표의 압력별 최소 컨디셔닝 시간(2/3/4/5 psi → 10/30/60/180 sec)은
압력에 대해 단조증가하며, 이를 예시 연마시간(1~10분)에 대입한 ex-situ 처리량 손실 예시 계산은
압력이 5 psi·10분 폴리싱일 때 23.1%(3분 컨디셔닝/13분 총사이클)에 달해 in-situ의 구조적 손실
0%와 대비되고, (Son & Lee 2021, doi.org/10.3390/app11083521) 패드 수명 12h→20h는 1.67배로
§4 서술과 일치한다.

```python verify
import numpy as np

# ── (A) Jeong et al. 2022 (ASPEN), §2.2 원문 표 그대로: 압력별 완전회복 최소 컨디셔닝시간[sec]
pressure_psi = np.array([2, 3, 4, 5])
t_cond_sec = np.array([10, 30, 60, 180])  # 10 sec, 30 sec, 1 min, 3 min

assert np.all(np.diff(t_cond_sec) > 0), "압력이 높아질수록 회복 소요시간이 길어져야 한다(원문 서술)"
ratio_5_to_2 = t_cond_sec[-1] / t_cond_sec[0]
print(f"5 psi/2 psi 회복시간 비 = {ratio_5_to_2:.1f}배 (문헌: 180s/10s = 18배)")
assert abs(ratio_5_to_2 - 18.0) < 1e-9

# ── (B) 예시 계산(본 노트의 독자 계산 — 문헌 실측 아님, §2.1 폴리싱시간[1,2,3,5,10 min] 인용):
# ex-situ 처리량 손실 = t_cond / (t_cond + t_polish), t_polish는 Jeong 2022 §2.1 실험 폴리싱시간 그대로
t_polish_min_options = np.array([1, 2, 3, 5, 10])  # 원문 §2.1 "1,2,3,5,10 min" 그대로 인용
t_polish_sec = t_polish_min_options * 60

loss_matrix = {}
for p, tc in zip(pressure_psi, t_cond_sec):
    losses = tc / (tc + t_polish_sec)
    loss_matrix[p] = losses
    print(f"{p} psi: 컨디셔닝 {tc}s, 폴리싱시간별 처리량손실 = "
          f"{[f'{l*100:.1f}%' for l in losses]}")

worst_case = loss_matrix[5][0]  # 5 psi + 1분 폴리싱(가장 불리한 조합)
best_case = loss_matrix[2][-1]  # 2 psi + 10분 폴리싱(가장 유리한 조합)
print(f"최악 조합(5psi, 1min 폴리싱) 처리량손실 = {worst_case*100:.1f}%")
print(f"최선 조합(2psi, 10min 폴리싱) 처리량손실 = {best_case*100:.2f}%")
assert worst_case > 0.5, "5 psi+1분 폴리싱이면 컨디셔닝시간(180s)이 폴리싱시간(60s)보다 길어 손실>50%"
assert best_case < 0.02, "2 psi+10분 폴리싱이면 컨디셔닝시간(10s)이 무시할 수준(<2%)이어야 함"
# 5 psi + 10분 폴리싱(가장 긴 폴리싱시간 옵션) 조합 — 노트 요약문의 23.1% 수치 확인
example_5psi_10min_polish = t_cond_sec[-1] / (t_cond_sec[-1] + 10 * 60)
print(f"5 psi, 10분 폴리싱 총사이클 대비 컨디셔닝 비중 = {example_5psi_10min_polish*100:.1f}%")
assert abs(example_5psi_10min_polish - 0.2308) < 0.001
# in-situ는 정의상(§1) 연마와 컨디셔닝이 겹치므로 구조적 처리량 손실 0
in_situ_loss = 0.0
assert in_situ_loss < best_case, "in-situ 구조적 손실이 ex-situ 최선 조합보다도 작아야 정의와 부합"

# ── (C) Son & Lee 2021 (Appl. Sci. 11, 3521) — 패드 수명 12h(Case I) vs 20h+(신규) 초록 수치
life_baseline_h = 12.0
life_new_h = 20.0  # 초록 "more than 20 h" — 하한값으로 보수적 사용
ratio_life = life_new_h / life_baseline_h
print(f"패드 수명 개선비 = {ratio_life:.2f}배 (초록: 12h → 20h+)")
assert ratio_life > 1.6, "20h/12h는 1.6배를 넘어야 함(초록 수치 재확인)"

print("PASS: (A) 압력-회복시간 단조성 및 배율, (B) ex-situ 처리량손실 예시계산, "
      "(C) 패드수명 개선비 — 전부 원문 수치 재현/대조 통과")
```

실행 결과 요약(2026-09-07, 위 블록 그대로 실행): 압력별 회복시간 10/30/60/180초는 문헌 표
그대로이며 5psi/2psi 비는 정확히 18배. 예시 처리량 손실 계산(본 노트 독자 계산)은 최악조합
(5psi, 1분 폴리싱) 75%, 최선조합(2psi, 10분 폴리싱) 1.6%, 5psi·13분 폴리싱 사이클 기준 23.1%로
계산됨 — **이 손실 수치들은 문헌이 직접 측정한 것이 아니라 문헌의 회복시간표를 사이클 손실률
공식에 대입한 이 노트의 파생 계산**이며, 실제 CMP 레시피의 컨디셔닝-폴리싱 사이클 배치는 다를
수 있다(미검증, 방향성만 신뢰할 것). 패드수명 개선비는 초록 수치 그대로 1.67배.

## 7. 한계 및 다음 단원 연결

- **MRR 표준편차/변동계수(CV)를 in-situ vs ex-situ로 직접 비교한 1차 문헌은 확보하지 못했다**
  (미검증) — Jeong et al.(2022)은 ex-situ 단독 조건에서의 회복시간·회귀모델만 제공하고,
  Prasad et al.(2011)은 결함(스크래치) 비교이지 MRR 변동계수 비교가 아니다. Cal-1(캘리브레이션
  단원, G2 이후) 또는 Lv3-1(최신 리뷰 추적)에서 재시도할 과제로 남긴다.
- Prasad et al.(2011)·Son & Lee(2021)는 본문 PDF를 확보하지 못해 **초록 수준 2차 인용**이다 —
  스크래치 개수·MRR 수치·정확한 in-situ/ex-situ 구분(§4의 "Case I") 등 세부 정량은 미확인.
- §6(B)의 처리량 손실 계산은 문헌 실측이 아니라 **이 노트의 파생 계산**임을 반복 강조한다 —
  실제 팹 레시피의 폴리싱:컨디셔닝 사이클 배치(예: N장마다 1회 ex-situ)는 다루지 않았다.
  [[disk-rpm-load-radius-pcr]] §6이 남긴 "r_cc 시간적분(전체 스윕범위)" 과제와 함께, 실제 사이클
  스케줄링을 반영한 시간적분 모델은 Lv2-2(sweep 레시피 최적화) 또는 Lv3-2(예측 모델 구현)에서
  다룰 대상이다.
- Zheng, Zhao & Lu (2023, PMC10536193 — [[disk-rpm-load-radius-pcr]] §1)는 in-situ/ex-situ 구분을
  명시하지 않은 채 컨디셔닝 실험을 수행했다 — 어느 쪽인지 논문에서 확인하지 못함(미검증).
