<!-- V2-SECTION: R4-disk | 분배완료 2026-09-08 | 근거: asperity-regeneration, break-in, breakin, conditioning, 다이아 | 정본: ARCHITECTURE-V2.md §3 -->
# 패드 브레이크인(Break-In) 물리: 초기 asperity 변형과 MRR 상승 곡선

> pad-lifecycle Lv1-1. [[hertz-gw-contact-mechanics]] [[pad-wear-glazing-mrr-decay]]
> [[conditioning-mechanism-asperity-regeneration]] 상호링크.
> 이 노트는 pad-wear-glazing-mrr-decay.md(패드 수명 **말기**, MRR 단조 감소)와 대칭인
> 패드 수명 **초기** 현상(신품/신컨디셔닝 패드에서 MRR이 상승해 정상상태로 수렴)을 다룬다.

## 1. 현상 정의 — Break-In이란 무엇인가

CMP 패드를 새로 장착하거나 새 다이아몬드 디스크로 처음 컨디셔닝을 시작하면, 초기 수 분~수
시간 동안 MRR·마찰계수·패드 온도가 시간에 따라 변하다가 특정 시점 이후 안정적인 값(이른바
"fully warmed-up", FWU 상태)에 도달한다. 이 과도 구간을 break-in(브레이크인)이라 부른다.
정성적으로는 [[conditioning-mechanism-asperity-regeneration]]에서 다룬 "정상상태 = 패드
마모율과 컨디셔너 절삭률의 균형"이 아직 성립하지 않은, **균형에 도달하기 전 과도 상태**로
이해할 수 있다 — 신품 패드의 asperity 분포(성형 시 만들어진 것)가 컨디셔닝이 만드는 "고유
(intrinsic)" 정상상태 분포와 다르기 때문에, 초기 여러 번의 웨이퍼 연마·컨디셔닝 사이클
동안 그 차이가 줄어드는 과정이다.

## 2. 1차 출처 실측 데이터: Jeong et al. (2021)

**출처**: Kyeongwoo Jeong, Seonho Jeong, Somin Shin, Jinuk Choi, Haedo Jeong,
"Identification of the Break-In Mechanism by Asperity Deformation of CMP Pad",
*Journal of the Korean Society for Precision Engineering* 38(2), 87-95 (2021-02-01).
DOI: https://doi.org/10.7736/JKSPE.020.082 (오픈액세스, jkspe.or.kr에서 확인).
**정직성 표지**: PDF 원문 파일 자체는 다운로드하지 못했다 — 저널 웹페이지(jkspe.or.kr)에
게재된 결과 요약 텍스트에서 아래 수치를 확인했다. 실험 조건(슬러리 종류, 컨디셔너 스펙,
패드 재질 상세)과 그래프/표 원본은 **확인 못 했으므로** 아래는 "저자가 보고한 핵심 결과값"
수준으로만 인용하고, 방법론적 세부는 다루지 않는다.

이 논문은 웨이퍼 압력을 3수준(210, 280, 350 g/cm²)으로 바꿔가며 패드가 FWU 상태(MRR·마찰·
온도가 정상상태에 도달)에 이르는 시간과 그 전후 MRR을 실측했다:

| 웨이퍼 압력 | FWU 도달 시간 | FWU 이전 MRR | FWU 이후 MRR |
|---|---|---|---|
| 210 g/cm² | 133 min | ~170.8 nm | ~193.7 nm |
| 280 g/cm² | 118.6 min | ~181.6 nm | ~211.0 nm |
| 350 g/cm² | 52.8 min | (범위 내) | ~211.0 nm 근접 |

(주: 논문 웹페이지 요약은 MRR을 "170.8–181.6 nm(FWU 이전) / 193.7–211.0 nm(FWU 이후)"
범위로만 제시하고 압력별 1:1 대응표는 명시하지 않았다 — 위 표의 압력-MRR 짝짓기는 범위의
양끝을 배치한 것이며 **추정**이다. 정확한 압력별 MRR 대응은 원문 PDF 확보 후 확인 필요.)

추가로 저자들은 FWU 상태에서: (1) 패드 표면 거칠기(surface roughness)가 압력 조건 전반에서
감소했고, (2) asperity의 탄성계수·경도가 FWU 상태에서 부분-웜업 상태 대비 감소했으며(마찰열에
의한 국소 연화로 해석), (3) **실접촉면적은 감소하지만 접촉 둘레(perimeter)는 증가**해 결과적으로
슬러리 연마입자가 관여하는 유효 계면이 늘어난다고 보고했다 — 이 (3)번 관찰이 이 논문의 핵심
주장("접촉면적↓이지만 MRR↑"이라는, 단순 GW 실접촉면적 비례 가정과 어긋나 보이는 결과를 설명)
이다.

## 3. 정성적 해석 — 왜 접촉면적이 줄어도 MRR이 오르는가 (2차 인용 수준, 미검증)

[[hertz-gw-contact-mechanics]]의 지수분포 GW 결과(§4)는 "실접촉면적이 하중에 비례"라는
정적 관계였다. Jeong et al.(2021)의 관찰은 이와 모순되지 않는다 — GW 결과는 **동일 asperity
분포 φ(z)** 내에서 하중만 바꿀 때의 관계이고, break-in은 φ(z) 자체가 시간에 따라 변하는
경우이기 때문이다. 정성적 가설(이 노트에서 처음 시도하는 종합, **미검증**): 신품 패드의
molded(성형) 표면은 소수의 크고 뭉툭한 macro-asperity로 이루어져 있어 초기 실접촉면적은
크지만 접촉 둘레(및 asperity 개수)는 적다. 브레이크인이 진행되며 이 macro-asperity가
마찰열·기계적 하중으로 국소 연화·변형(paper의 탄성계수 감소 관찰과 일치)되어 다수의 작은
asperity로 "쪼개지듯" 재구성되면, 총 접촉면적은 줄어도 접촉 둘레와 asperity 개수(=슬러리
입자가 끼어드는 미세 계면 수)가 늘어 MRR이 오히려 상승할 수 있다. 이 가설은 논문 원문을
읽지 못한 상태의 추정이며, [[pad-wear-glazing-mrr-decay]]의 population balance 틀(Shi & Ring
2010)과 결합해 정식화하는 것이 다음 레벨(Lv1-2 또는 Lv2-1)의 과제로 남는다.

## 4. 정량 탐색: FWU 도달 시간과 압력의 관계 (자체 회귀, 미검증 가설)

문헌값(Jeong et al. 2021)을 대조해보면 FWU 도달 시간이 압력 증가에 따라 감소한다:
210 g/cm²에서 133 min, 280 g/cm²에서 118.6 min, 350 g/cm²에서 52.8 min. 이것이 "브레이크인
완료에 필요한 총 마찰일(frictional work)이 압력·속도에 무관하게 일정하다"는 가설(러닝인
문헌의 고전적 직관과 유사한 형태, 예: Blau, "On the nature of running-in", *Tribology
International* 38(11), 1007-1012 (2005) — **이 논문도 원문 미확보, 표준적으로 인용되는
개념만 차용**)과 부합하는지, 거듭제곱 관계 t_FWU ∝ P^n으로 회귀해 대조한다. 아래
python verify 블록에서 실제로 재현한 결과(Jeong et al. 2021 문헌값 대비) n≈-1.74이며,
예측값과 문헌값의 상대오차는 12~24%로 — **정확한 물리법칙 재현이 아니라 오더만 맞춘
정성적 일치**에 그친다(미검증 가설, 3개 데이터점만으로 2개 파라미터를 적합했으므로
과적합 위험이 크고, 온도 의존 점탄성 연화 등 압력 외 변수가 섞였을 가능성이 높다).

## 5. 다음 단원과의 연결

- Lv1-2(정상 마모율=컨디셔닝 재생 균형)에서 이 브레이크인 과도상태가 정상상태로 수렴하는
  구체적 메커니즘(§3의 가설)을 GW population balance로 정식화할 것.
- [[pad-wear-glazing-mrr-decay]]의 population balance 틀(초기분포 φ0(z) → 시간에 따라 이류)을
  "재생 방향"(macro-asperity 분해)으로 확장하면 이 노트의 §3 가설을 정량 모델로 만들 수 있다.
- 원문 PDF 확보(추후 기관 접근 또는 미러 사이트 재시도)로 §2의 압력-MRR 1:1 대응과 §4의 회귀를
  검증할 필요.

```python verify
import numpy as np

# Jeong et al. (2021) 문헌값: 웨이퍼 압력(g/cm^2) vs FWU 도달 시간(min)
P = np.array([210.0, 280.0, 350.0])       # g/cm^2
t_fwu = np.array([133.0, 118.6, 52.8])    # min

# 가설: t_FWU = A * P^n (총 마찰일 일정 가설의 거듭제곱 형태)
logP, logt = np.log(P), np.log(t_fwu)
n, logA = np.polyfit(logP, logt, 1)
A = np.exp(logA)
pred = A * P ** n

rel_err = np.abs(pred - t_fwu) / t_fwu
print(f"거듭제곱 회귀: n={n:.3f}, A={A:.3e}")
print(f"문헌값(min): {t_fwu}")
print(f"예측값(min): {np.round(pred, 1)}")
print(f"상대오차: {np.round(rel_err * 100, 1)}% (문헌과 최대 {rel_err.max()*100:.1f}% 차이)")

# 오더 수준 검증만 주장한다 — 30% 이내면 "정성적 일치"로 채택, 그 이상이면 가설 기각
assert rel_err.max() < 0.30, (
    f"거듭제곱 가설이 오더 수준에서도 안 맞음 (최대 상대오차 {rel_err.max()*100:.1f}%)")

# FWU 전후 MRR 상승폭이 물리적으로 타당한 범위(양수, 50% 미만)인지 대조
mrr_before = np.array([170.8, 181.6])   # nm, 문헌값 범위
mrr_after = np.array([193.7, 211.0])    # nm, 문헌값 범위
rise_frac = (mrr_after[:, None] - mrr_before[None, :]) / mrr_before[None, :]
assert np.all(rise_frac > 0), "MRR이 FWU 이후 하락 — 브레이크인 정의와 모순"
assert np.all(rise_frac < 0.50), (
    f"MRR 상승률이 비정상적으로 큼(50% 초과): {rise_frac.flatten()*100}%")
print(f"MRR 상승률 범위: {rise_frac.min()*100:.1f}% ~ {rise_frac.max()*100:.1f}% "
      f"(문헌값 170.8-181.6nm -> 193.7-211.0nm과 대조, 모두 물리적으로 타당한 범위)")
```

## 6. 한계 및 정직한 표지

- Jeong et al.(2021) **원문 PDF 미확보** — 저널 웹페이지 요약만으로 수치를 인용했다.
  압력-MRR 1:1 대응, 실험 반복수, 오차범위(에러바)는 확인 못 했다.
- Blau(2005) running-in 리뷰는 **원문 미확보**, "고전적으로 러닝인이 지수적/거듭제곱적 과도
  거동으로 논의된다"는 통념 수준에서만 인용했다 — 이 논문이 실제로 CMP 패드 브레이크인을
  다루는지는 확인하지 않았다(제목만 매칭, 2차 인용 수준).
- §3의 "macro-asperity 분해" 가설은 이 노트에서 처음 제안하는 **추정**이며, 어떤 문헌에서도
  직접 검증되지 않았다. 실접촉면적 감소+둘레 증가라는 관찰 자체(Jeong et al. 보고)와
  모순되지 않는다는 것만 확인했을 뿐, 메커니즘의 증거는 없다.
- §4의 거듭제곱 회귀는 3점 데이터의 2-파라미터 적합이라 통계적 유의성이 낮다 — 오더 수준의
  정성적 참고로만 취급해야 한다.
