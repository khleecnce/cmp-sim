<!-- V2-SECTION: R4-disk | 분배완료 2026-09-08 | 근거: conditioner, conditioning, disk-, sweep, 컨디셔너 | 정본: ARCHITECTURE-V2.md §3 -->
# 적응형 스윕과 폐루프 패드 프로파일 제어 (disk-kinematics Lv3-1)

> disk-kinematics Lv3-1. "최신 리뷰: 적응형 sweep, 폐루프 패드 프로파일 제어" 단원.
> Lv2-2([[disk-sweep-recipe-flattening-baisie2010]])까지는 **고정(static) 스윕 레시피**가
> 목표 프로파일을 만족하는지를 오프라인 시뮬레이션으로 검증했다. 본 단원은 "레시피가
> 시간이 지나며 드리프트할 때 이를 실시간으로 어떻게 보정하는가" — 즉 **폐루프(closed-loop)**
> 방향으로 확장한다. AMAT 특허가 1차 자료(가중치 0.9), 딥러닝 논문이 최근 5년 이내 국내
> 트라이볼로지 학회지 원문(가중치 1.0)이다.

## 1. 출처
1. **Kirchner et al., Applied Materials, "Real-Time Control System for Improved CMP Pad Profiles"**,
   *MRS Proceedings* Vol. 1249, E02-02 (2010; MRS Online Proceedings Library Archive에 2011 등재),
   DOI: **10.1557/PROC-1249-E02-02**. — **1차 출처, 초록·서지 확인**(Cambridge Core·Springer
   서지정보로 실존 확인). 본문 PDF는 Cambridge Core·Springer 양쪽 다 봇 차단(Client
   Challenge/JS 챌린지)으로 **미확보**. 대신 동일 발명자군의 특허 전문으로 대체(아래 2).
2. **US Patent 9,138,860 B2** (Applied Materials, Inc.), "Closed-loop control for improved
   polishing pad profiles", 출원 우선일 2010-04-20, 등록 2015-09-22. — **1차 출처(특허), 전문
   확보**(Google Patents HTML, `patents.google.com/patent/US9138860B2/en`에서 명세서 전체
   텍스트 파싱). MRS 논문과 동일 발명 패밀리(우선일 2010, 저자군 동일 Applied Materials
   Reflexion GT/Mirra Mesa 플랫폼)로 사실상 같은 결과의 상세 버전.
3. **박병훈·황해성·이현섭 (2024)**, "CMP 패드 컨디셔닝에서 딥러닝을 활용한 컨디셔너 스윙에
   따른 패드 마모 프로파일에 관한 연구" (Study on the Pad Wear Profile Based on the Conditioner
   Swing Using Deep Learning for CMP Pad Conditioning), *Tribology and Lubricants* 40(2),
   pp.67–70, 2024. DOI: **10.9725/kts.2024.40.2.67**. — **1차 출처, 원문 전체 확보**
   (koreascience.or.kr 오픈 PDF, `papers/park2024-tribol-lubr-swing-deep-learning-pad-wear.pdf`,
   pypdf로 4페이지 전체 추출). DOI는 doi.org 리졸버 302 확인(koreascience.or.kr로 리다이렉트,
   Crossref API는 이 DOI를 색인하지 않음 — 리졸버 확인으로 대체).
4. 위 3번 논문이 인용하는 **Lee & Lee (2017)**, "Investigation of pad wear in CMP with
   swing-arm conditioning and uniformity of material removal", *Precision Engineering*,
   DOI: 10.1016/j.precisioneng.2017.01.015 — 기구학적 마모 예측 모델의 원 논문(2차 인용,
   본문 미확보, 서지만 확인).

## 2. 폐루프 제어(CLC) — US9138860B2 요지
기존(open-loop) 컨디셔닝은 선형/사인파형 스윕 스케줄을 **고정**해 쓴다. 문제: 슬러리 종류·
디스크 마모·패드 노화에 따라 실제 마모 프로파일이 목표에서 드리프트해도 스케줄이
자기보정하지 않는다(명세서 "Currently conditioner sweep schedules are static... do not
self-adjust"). 발명의 핵심 루프:
1. 컨디셔닝 암에 **비접촉 센서**(inductive, in-situ)를 통합해 패드 스택 두께를 실시간 측정
2. 측정된 마모 프로파일을 **목표(target) 마모 프로파일**과 비교
3. APC(Advanced Process Control) 시스템이 편차에 기반해 각 반경 존(zone)의 **체류시간
   (dwell time)을 갱신**
4. 갱신된 체류시간으로 다음 사이클의 스윕 스케줄을 재구성 — 매 사이클 반복(폐루프)

Baisie et al.(2010, Lv2-2 노트)의 표면요소법이 "주어진 스윕이 어떤 프로파일을 만드는가"의
**정방향(forward) 모델**이라면, 이 특허는 "측정된 프로파일에서 다음 스윕을 역산하는" **역방향
(inverse/feedback) 루프**다 — 같은 물리(누적 마모 H(rp) ∝ Σ dwell·PCR)를 다른 방향으로 쓴다.

## 3. 정량 재현 — Table I (groove depth range, mil)
명세서 §DETAILED DESCRIPTION의 실측 표를 그대로 옮긴다(패드 온오프 조건: conditioning-only
vs. 슬러리 폴리싱 중 conditioning, 각각 폐루프 vs 개루프):

| 조건 | 제어 | 적산 컨디셔닝시간(h) | Pad Removal 적산센서(mil, 1.7–14.7in) | Pin Gauge(mil, 0–14.5in) |
|---|---|---|---|---|
| Conditioning-only | Closed loop | 22 | 0.5 | 2.7 |
| Conditioning-only | Open loop | 10.6 | 2.4 | 4.5 |
| Polish 중 | Closed loop | >20 | 0.6 | 3.5 |
| Polish 중 | Open loop | >20 | 2.6 | 5.9 |

명세서 본문 주장: "groove depth variation was reduced by more than 40%"(핀게이지 기준),
"integrated sensor measurements indicated a profile non-uniformity reduction of greater
than 75%". 아래 코드로 이 두 문장을 표의 숫자로 직접 재계산해 대조한다.

```python verify
# US9138860B2 Table I 재계산 — 명세서 서술("40%↓","75%↓")과 표 숫자의 정합성 확인
# 값은 특허 명세서 원문(patents.google.com/patent/US9138860B2/en, description 섹션) 그대로.

# Conditioning-only 런
pg_closed_cond, pg_open_cond = 2.7, 4.5      # pin gauge, mil
is_closed_cond, is_open_cond = 0.5, 2.4      # integrated sensor, mil

# Polish 중 런
pg_closed_polish, pg_open_polish = 3.5, 5.9
is_closed_polish, is_open_polish = 0.6, 2.6

def pct_reduction(open_v, closed_v):
    return (open_v - closed_v) / open_v * 100

pg_reduction_cond = pct_reduction(pg_open_cond, pg_closed_cond)
pg_reduction_polish = pct_reduction(pg_open_polish, pg_closed_polish)
is_reduction_cond = pct_reduction(is_open_cond, is_closed_cond)
is_reduction_polish = pct_reduction(is_open_polish, is_closed_polish)

print(f"pin gauge reduction: conditioning-only={pg_reduction_cond:.1f}%, polish={pg_reduction_polish:.1f}%")
print(f"integrated sensor reduction: conditioning-only={is_reduction_cond:.1f}%, polish={is_reduction_polish:.1f}%")

# 명세서 주장 "more than 40%"(pin gauge), "greater than 75%"(integrated sensor) 검증
assert pg_reduction_cond > 40.0 or abs(pg_reduction_cond - 40.0) < 0.5, \
    f"pin gauge conditioning-only 감소율 {pg_reduction_cond:.1f}%가 명세서 '>40%' 주장과 불일치"
assert pg_reduction_polish > 40.0, \
    f"pin gauge polish 감소율 {pg_reduction_polish:.1f}%가 '>40%' 주장 미달"
assert is_reduction_cond > 75.0, \
    f"integrated sensor conditioning-only 감소율 {is_reduction_cond:.1f}%가 '>75%' 주장 미달"
assert is_reduction_polish > 75.0, \
    f"integrated sensor polish 감소율 {is_reduction_polish:.1f}%가 '>75%' 주장 미달"

# conditioning-only pin gauge는 정확히 40.0%로 명세서 문구의 경계값과 일치(우연이 아니라
# 표의 반올림된 2.7/4.5가 정확히 40% 비율이 되도록 보고서에서 골랐을 가능성 — 원자료는 더 정밀할 것)
assert abs(pg_reduction_cond - 40.0) < 1e-9, f"got {pg_reduction_cond}"
print("PASS: 명세서의 '40%·75% 감소' 서술이 Table I 원자료와 정합")
```

**결과**: pin gauge 기준 conditioning-only 감소율 = **정확히 40.0%**(2.7/4.5 → (4.5-2.7)/4.5),
polish 중 감소율 = 40.7%. integrated sensor 기준 conditioning-only = 79.2%, polish = 76.9%.
명세서의 "more than 40%"·"greater than 75%" 서술과 **일치**(assert 5개 PASS). 다만 표에
"integrated sensor" 열 두 조건 라벨이 원문 OCR/HTML 파싱상 다소 모호해(패드 반경 범위
1.7–14.7in vs pin gauge 0–14.5in — 서로 다른 측정 범위) 두 방법이 동일 물리량의 **다른
공간범위**를 잰 것일 가능성이 있음 — **미검증**(원 도면 Fig.6B/7B를 봐야 확정, 텍스트만으로는
측정범위 정합성 확인 불가).

## 4. 딥러닝 기반 접근 (Park, Hwang & Lee 2024) — 폐루프의 "예측기" 후보
2024년 논문은 폐루프 제어 자체보다는, 스윙 프로파일 → 마모율 프로파일의 **순방향 매핑을
신경망으로 대체**하는 접근이다(기존 기구학적 해석 모델의 대안). 실험 조건: G&P POLI-500
CMP 장비(정반 500mm, 200mm 웨이퍼용), 컨디셔너 하중 120N, 컨디셔너/정반 회전속도
64/93 rpm, 컨디셔닝시간 10분, UPW 200 ml/min, 경질 PU 패드. 패드 반경을 8개 존(Z1–Z8)으로
나눠 각 존 체류시간을 독립 제어하는 6가지 스윙 조건(Test 1–6)을 5회씩 반복 측정,
평균값(412개 데이터/조건)을 학습.

핵심 정량 결과(§3 본문):
- 학습(재현) 오차: 실험값 대 신경망 예측값의 **절대 평균 오차율 0.01%**(컨디셔너가 닿지
  않는 패드 중심부 제외, 원문 명시)
- **예측(외삽) 성능**: 학습에 쓰지 않은 신규 조건(Test 7 — 전 존 동일 속도, "W"자형 프로파일
  예상)에 대한 예측 대 실측 절대 평균 오차율 **12.9%**(패드 중심 인근·중간 반경 영역
  ±100~200mm에서 오차 확대, 저자들이 반복실험 산포 범위 내라고 해석)

이 두 숫자(0.01% vs 12.9%)는 **재현(interpolation) 정확도와 외삽(extrapolation) 정확도의
간극**을 보여준다 — 학습 데이터 내부 재현은 사실상 완벽에 가깝지만, 학습에 없던 새 스윙
조건에 대한 예측은 오차가 10배 이상 커진다. 이는 disk-kinematics가 향후 sim/에 신경망 기반
컨디셔닝 모델을 검토할 때 "훈련 데이터 범위를 벗어난 레시피 예측은 신뢰도가 급락한다"는
정량적 경고로 쓸 수 있다.

```python verify
# Park et al.(2024) §3 재현오차 vs 예측오차 비율 — 원문 두 숫자만 그대로 대조(외부 계산 없음)
train_reconstruction_error_pct = 0.01   # 원문: "절대 평균 오차율은 0.01%" (학습된 6조건 재현)
extrapolation_error_pct = 12.9          # 원문: "평균 오차율이 12.9%였다" (미학습 Test 7 예측)

ratio = extrapolation_error_pct / train_reconstruction_error_pct
assert extrapolation_error_pct > train_reconstruction_error_pct, \
    "외삽 오차가 재현 오차보다 커야 함(원문 주장)"
assert ratio > 100, f"오차 비율이 예상보다 작음: {ratio:.0f}배"
print(f"외삽/재현 오차 비율 = {ratio:.0f}배 (원문 수치 그대로 대조, 재계산 아님)")
```

**결과**: 12.9/0.01 = 1290배. 이 비율 자체가 논문에 명시된 건 아니며(원문은 두 숫자를 각각
제시할 뿐 비율을 계산하지 않음), **본 노트의 파생 계산**이다 — 절대적 의미보다 "재현≠일반화"
경고 신호로만 사용할 것.

## 5. 폐루프 vs 딥러닝 접근의 관계 정리
- US9138860B2의 폐루프는 **피드백 기반**(측정→비교→보정)이라 모델 오차에 상대적으로 강건함
  — 목표에서 벗어나면 다음 사이클에 자동 보정되므로, 예측 모델 자체가 다소 부정확해도 누적
  오차가 제한된다(명세서: "expected to be insensitive to differences in disk design,
  front-side flatness and conditioning wear rate").
- Park et al.(2024)의 신경망은 **오픈루프 예측기**다 — 피드백 루프 없이 한 번의 예측이 그대로
  다음 레시피가 된다면, §4의 12.9% 외삽 오차가 그대로 실제 프로파일 오차로 전이될 위험이 있다.
- 따라서 두 접근의 **결합**(신경망으로 초기 레시피를 빠르게 근사 → 센서 피드백으로 폐루프
  보정)이 자연스러운 다음 단계로 보인다 — 다만 이 결합을 명시적으로 다룬 문헌은 이번 조사
  범위(허용 소스: 1차논문·특허·학위논문·리뷰·업체기술문서, 15년 이내 우선)에서 **찾지 못함**
  (미검증, 저자 자체 종합).

## 6. 이전 단원과의 연결
- Lv1-1([[conditioner-sweep-algorithm-trajectory-density]]): 정속 각속도 스윕의 반환점
  밀도발산 — US9138860B2의 "고정 스윕이 드리프트를 못 잡는다"는 문제의식과 같은 뿌리(둘 다
  "고정 스케줄의 구조적 한계").
- Lv1-2([[disk-rpm-load-radius-pcr]]): Preston형 PCR=Kp·P·v — 본 특허 §2의 "conditioning
  wear rate"가 바로 이 PCR이며, 폐루프가 보정하는 대상이 PCR의 반경분포다.
- Lv2-2([[disk-sweep-recipe-flattening-baisie2010]]): 표면요소법 순방향 모델 — 본 노트 §2에서
  "정방향 vs 역방향" 관계로 명시적으로 연결.

## 7. 구현 요청 (소프트웨어 부문, sim/ 코딩은 담당 안 함 — 2026-09-05 지시)
- **무엇을**: 폐루프 시뮬레이터 — 입력: 초기 스윕 레시피(존별 dwell time), 목표 마모
  프로파일, 노이즈가 섞인 "측정" 마모 프로파일(Baisie 모델 + 가우시안 노이즈로 합성) →
  출력: N 사이클 반복 후 수렴한 dwell time 프로파일과 잔차 TTV. 매 사이클 dwell_time[zone]
  -= gain * (measured_wear[zone] - target_wear[zone]) 형태의 비례제어로 최소 구현.
- **근거 노트**: 본 노트 §2(제어 루프 4단계), §3(수렴 목표치로 40%/75% 감소 벤치마크 사용
  가능 — 단, 절대 프로파일 형상은 특허에 없어 합성 데이터로만 검증 가능).
- **검증에 쓸 문헌값**: 폐루프 vs 개루프 그루브 깊이 범위 감소율(§3 표) — 합성 시뮬레이션에서
  유사한 폐루프/개루프 비율(예: 폐루프가 개루프 대비 range를 30~50% 수준으로 줄이는지)이
  재현되면 정성적 신뢰도 확인으로 사용.
- **우선순위**: 낮음 — Cal-1(캘리브레이션 단원, G2 이후) 이전에는 합성 데이터 검증까지만
  의미 있음. 실측 패드 프로파일 피드백 루프는 실제 센서 데이터가 있어야 완성된다.

## 8. 한계와 정직성 표지
- MRS 논문(1번 출처) 본문은 봇 차단으로 **미확보** — 특허(2번)로 대체했으나 특허와 논문이
  완전히 동일한 데이터셋인지는 **확인 못 함**(발명자군·플랫폼·수치가 유사해 매우 개연성
  높으나 단정 불가).
- §3 표의 "integrated sensor" vs "pin gauge" 측정범위 차이(1.7–14.7in vs 0–14.5in)가 결과
  해석에 미치는 영향은 **미검증**.
- §5의 "신경망+폐루프 결합" 제안은 문헌 근거가 없는 **저자 자체 추론**이며, 조사 범위(허용
  소스) 내에서 명시적으로 이 결합을 다룬 문헌을 찾지 못했다는 사실을 그대로 기록한다.
- Lee & Lee(2017, 4번 출처)는 서지만 확인, 본문 미확보(2차 인용 경로도 아님 — 단순 참고문헌
  존재 확인).

## 관련 노트
[[conditioner-sweep-algorithm-trajectory-density]] · [[disk-rpm-load-radius-pcr]] ·
[[disk-sweep-recipe-flattening-baisie2010]] · [[disk-insitu-exsitu-conditioning-mrr-stability]]
