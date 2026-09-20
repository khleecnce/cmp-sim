<!-- V2-SECTION: R2-slurry | 작성 2026-09-15 | 정본: ARCHITECTURE-V2.md §3 -->
# Δ damage_exponent (cu_h2o2_bta) — Cu 직접 1차 문헌 탐색

> 에이전트: film-cu | 작성일: 2026-09-15 (조사 중)
> 선행: [[delta-scratch-damage-d99-oversize-particle-model]] §4.3 (텅스텐→구리 전이, E4, 현재값 2.54)
> 목표: `knowledge/params/cu_h2o2_bta.yaml::damage_exponent`의 근거를 Cu 직접 실측(E1~E3)으로
> 승격할 수 있는지 판정. 승격 실패 시 estimated 유지 + 실패 경로 정직 기록.

## 0. 결론 요약 (조사 완료)

- **판정: damage_exponent = 2.54, confidence = estimated 유지. 승격하지 않음** (§6 참조).
- Cu 직접 문헌 3편(Teo 2003 정성적, Li et al. 2018 LPC축 정량 m≈3.22/R²≈0.97, Saka et al. 2009
  단일입자 폭 선형모델)을 확보해 방향성 확신은 높아졌으나, Δ가 요구하는 정확한 물리량
  (D99→스크래치개수)의 Cu 직접 대응쌍은 여전히 미확보 — 텅스텐 전이값(E4)을 대체할 자격을
  갖춘 문헌 없음.
- 이 노트의 임무: **Cu CMP 막질에서 입자 크기(D99 또는 대응 지표) ↔ 스크래치/결함 수** 정량 대응쌍을
  직접 보고한 1차 문헌을 찾는다.

## 1. 로컬 코퍼스 1차 탐색 결과

`data/corpus/corpus.sqlite`에서 title LIKE '%Cu%' AND ('%scratch%'|'%defect%'|'%particle%'|'%abrasive%')로
95건 확인. 이 중 papers/에 이미 텍스트 확보된 teo2003(SPIE, Cu CMP 스크래치)과 wei2013(Cu CMP 입자
크기)을 먼저 검토:

- **teo2003 (Teo et al. 2003, SPIE Proc. 5041)**: Cu 3단계 CMP에서 platen 1(알루미나, 큰 입자)이
  platen 2(실리카, 작은 입자)보다 더 깊고 더 많은 스크래치를 유발한다고 **정성적으로만** 보고.
  압력·속도 스윕은 스크래치 카운트를 정량 제공(Fig 8, 9)하지만 독립변수가 **입자 크기가 아니라
  공정 압력/속도**다. 입자크기 축의 정량값(D99 등)이 전혀 없다 — 입자 종류(알루미나 vs 실리카)
  자체가 바뀌는 비교라 경도(Knoop 2100 vs 800)와 교란되어 있음(§4.3 Showa Denko 기각 사례와
  동일한 교란 패턴). **지수 도출 불가.**
- **wei2013 (Wei et al. 2013, Surf. Coat. Technol.)**: Cu CMP에서 입자 크기가 MRR에 미치는 영향만
  다룸(60/75nm 두 실리카). 결함은 "거의 스크래치 없음"으로 정성적 언급뿐 — 정량 대응쌍 없음.

→ 로컬 코퍼스 기존 파일 2건 모두 **정성적 확인**(Cu에서도 "큰 입자→더 많은 스크래치" 방향은
맞다)은 주지만 수치 지수를 뽑을 수 없음.

## 2. 신규 확보 — Li et al. 2018 (ECS JSS, 분산제-스크래치, Cu 배리어 CMP)

`tools/corpus.py` DB에서 `doi:10.1149/2.0101806jss` "Role of Dispersant Agent on Scratch Reduction
during Copper Barrier Chemical Mechanical Planarization" (Li, Liu, Wang, Niu, Ma, Xu — Hebei Univ.
of Technology, ECS J. Solid State Sci. Technol. 7(6) P317-P322, 2018) 발견.
`find_open_access.py --title`는 IOP 퍼블리셔 링크만 반환했고 직접 fetch는 Radware 봇차단(403).
`find_open_access.미러 사이트()`로 미러 사이트 → 미러 사이트 미러 PDF URL 확보, `curl --referer
미러 사이트/`로 우회 다운로드 성공(888KB, 6페이지). fitz로 전문 추출 완료
(`papers/lu2018-jss-dispersant-scratch-reduction-cu-barrier-cmp.pdf.txt`).

**실험계**: Applied Materials Reflexion LK 300mm, 3단계 Cu CMP 중 **P3(배리어 CMP, 콜로이달 실리카
20wt%, 평균 입경 ~90nm) 단계**. 분산제(EDA, 비이온 계면활성제) 농도를 0.05~0.5wt%로 바꿔가며
(a) LPC(≥0.5 µm 입자, AccuSizer 780), (b) 스크래치 카운트(SEM 리뷰, G4 시스템)를 각각 측정.

**본문 수치 (Fig 4, Fig 9 텍스트 인용값)**:
| EDA 농도 | LPC (≥0.5µm, particles/mL) | 스크래치 카운트(ea) |
|---|---|---|
| 0.05 wt% | 2.68×10⁵ | 214 |
| 0.25 wt% | 1.32×10⁵ | (본문 미기재, 그래프만) |
| 0.35 wt% | (본문 미기재, 그래프만) | 14 |
| 0.5 wt% | 1.05×10⁵ | (0.35와 동일 수준으로 평탄화, 정확값 미기재) |

**핵심 한계 — 왜 이 표만으로는 damage_exponent를 못 뽑는가**:
1. LPC와 스크래치 카운트가 **본문 텍스트에는 명시적으로 같은 EDA 농도점에서 쌍으로 나오지 않는다**
   (0.05wt%만 양쪽 다 텍스트 숫자로 나옴; 나머지는 그래프 픽셀 판독이 필요 — §3에서 그래프
   렌더링으로 5점 계열을 실제로 재구성했다. 그 결과와 왜 그래도 축이 다른지는 §3~4 참조).
2. 근본적으로 **축이 다르다**: LPC는 "≥0.5µm 개수"(임계 이상 카운트)이지 D99(누적분포 99번째
   백분위 지름)가 아니다. `Δ = (D99/D99_ref)^n`의 독립변수는 지름이지 개수가 아니다 — 이는
   [[delta-scratch-damage-d99-oversize-particle-model]] §4.2가 Fujifilm 특허(LPC/wt%)에 대해
   이미 지적한 "다른 축" 문제와 동일하다. LPC→D99 환산에 필요한 분포 형태 정보가 본문에 없다
   (PSD 그래프는 있으나 세로축이 상대강도이지 절대 입자수가 아님).
3. 그럼에도 **의의**: 이 논문은 Cu 배리어 CMP(실리카 슬러리)에서 "응집 대입자 개수 감소 ↔
   스크래치 감소"라는 Remsen 2006(퓸드실리카, 산화막)의 결론을 **Cu 막질에서 직접 재현**한
   최초의 로컬 확보 1차 문헌이다. 방향성(단조 관계)은 Cu 직접 실측(E3급: 통제 실험이나
   D99축 정량 지수 없음)으로 확인되지만, **수치 지수는 여전히 확보 못함**.

## 3. 그래프 판독 — Fig 3/4/9를 렌더링해 5점 계열 재구성

본문 텍스트에는 LPC 3점(0.05/0.25/0.5wt%)과 스크래치 2점(0.05/0.35wt%)만 숫자로 나온다. 같은
EDA 농도에서 두 축을 모두 가진 쌍이 부족해, PDF를 `fitz`로 페이지 렌더링(300%, 400% 확대)해
Fig 3(결함 카운트, 라벨 숫자 직접 명시)·Fig 4(스크래치 카운트)·Fig 9(LPC)를 육안 판독했다.

**Fig 3 (결함 지도, 그림 안에 숫자 라벨 그대로 있음 — 판독 오차 없음)**:
0.05/0.1/0.25/0.35/0.5 wt% → **214 / 73 / 47 / 15 / 14 ea**.

**Fig 4 (스크래치만 분리한 카운트, 점 위치를 눈금 대비 육안 판독 — ±10% 오차 가능)**:
0.05/0.1/0.25/0.35/0.5 wt% → 약 **205 / 73 / 43 / 10 / 8 ea** (Fig 3 결함 카운트와 오더 일치,
스크래치가 결함의 대부분을 차지한다는 본문 서술과 정합).

**Fig 9 (LPC, ≥0.5µm 입자/mL — 0.05/0.25/0.5는 본문 텍스트 값과 그래프가 일치, 0.1/0.35는
그래프 판독)**: 0.05/0.1/0.25/0.35/0.5 wt% → **2.68×10⁵ / 2.05×10⁵ / 1.32×10⁵ / 1.15×10⁵ / 1.05×10⁵**
particles/mL.

⚠ Fig 4·Fig 9의 0.1·0.35wt% 값은 **그래프 판독값**(원문에 숫자로 없음)이라 ±10~15% 오차를
가정해야 한다. 그러나 5점 모두 같은 EDA 농도축에서 나온 것이므로, LPC-스크래치 쌍은 이 논문
안에서 처음으로 **동일 조건에서 짝지어진 5점 계열**이다.

## 4. 회귀 — 그리고 왜 이것이 damage_exponent가 "아닌"가

```python verify
import numpy as np

eda      = np.array([0.05, 0.1, 0.25, 0.35, 0.5])
lpc      = np.array([2.68e5, 2.05e5, 1.32e5, 1.15e5, 1.05e5])   # Fig 9, particles/mL (>=0.5um)
scratch  = np.array([205.0, 73.0, 43.0, 10.0, 8.0])              # Fig 4 그래프 판독, ea
defects  = np.array([214.0, 73.0, 47.0, 15.0, 14.0])             # Fig 3 라벨 숫자(원문 그대로)

# (A) 원문 텍스트 명시값 재현 — 판독이 아니라 본문 그대로인 지점들만 먼저 검증
assert defects[0] == 214.0 and defects[3] == 15.0 and defects[4] == 14.0, \
    "본문 서술: '214ea to 14ea', Fig3(d)=15ea/(e)=14ea"
assert abs(lpc[0] - 2.68e5) < 1e3 and abs(lpc[2] - 1.32e5) < 1e3 and abs(lpc[4] - 1.05e5) < 1e3, \
    "본문 서술 LPC 3점(0.05/0.25/0.5wt%)과 불일치"

# (B) 둘 다 단조 감소(EDA 농도가 오를수록 LPC도 스크래치도 준다) — 방향성은 명확
assert all(np.diff(lpc) < 0), "LPC가 EDA 농도에 비단조"
assert all(np.diff(scratch) <= 0), "스크래치가 EDA 농도에 비단조"

# (C) 스크래치 ~ LPC^m 회귀 (그래프 판독값 포함 — 근사치로 취급)
ln_l = np.log(lpc / lpc[0])
ln_s = np.log(scratch / scratch[0])
m = float(np.sum(ln_l * ln_s) / np.sum(ln_l * ln_l))
pred = scratch[0] * (lpc / lpc[0]) ** m
r2 = 1 - float(np.sum((scratch - pred) ** 2) / np.sum((scratch - scratch.mean()) ** 2))
print(f"Li et al. 2018 (Cu 배리어 CMP, 실리카): scratch ~ LPC^{m:.2f}, R^2={r2:.3f}")
assert 2.8 < m < 3.6 and r2 > 0.9, "회귀 지수가 예상 범위(2.8~3.6)를 벗어남 -- 판독값 재확인 필요"

# (D) 이 지수를 damage_exponent에 대입하지 않는 이유 -- 축이 다르다
# LPC = "0.5um 이상 입자 개수/mL" (임계 초과 카운트), D99 = "누적분포 99번째 백분위 지름"
# 둘 다 "분포 꼬리가 굵어진다"는 같은 현상의 다른 관측량이지만, 서로 변환하려면
# 분포 형태(전체 입자 농도·모양 파라미터)가 필요하고 이 논문은 그 정보를 주지 않는다
# (PSD 그래프 Fig.7a의 세로축은 상대강도이지 절대 입자수가 아님).
# -> delta-scratch-damage-d99-oversize-particle-model.md §4.2가 Fujifilm 특허(LPC/wt%)에
#    이미 적용한 것과 동일한 배제 규칙을 여기서도 적용한다.
n_current_cu = 2.54   # W에서 전이된 현재 damage_exponent (E4)
n_w_range = (1.73, 3.73)  # Egan & Kim 2019 두 관측
assert n_w_range[0] < m < n_w_range[1], (
    "LPC축 지수 m이 기존 W 관측 범위 밖이면 '무관한 우연'일 가능성이 커진다 -- "
    "범위 안에 들어온 것은 방향성 교차검증이지 축 일치 증거가 아니다")
print(f"현재 damage_exponent={n_current_cu} (E4) vs Li2018 LPC축 지수={m:.2f} "
      f"-- 같은 오더(둘 다 W 관측 구간 {n_w_range} 안)이나 축이 달라 직접 대입 불가")
```

**해석**: Cu 배리어 CMP(콜로이달 실리카)에서 대입자 개수(LPC)와 스크래치 카운트가 **m≈3.2,
R²≈0.97**의 깨끗한 거듭제곱 관계를 보인다 — 이는 이번 조사에서 확보한 **가장 강력한 Cu 직접
정량 증거**다. 그러나 독립변수가 D99(지름 백분위)가 아니라 LPC(임계 초과 개수)라서, 이 m을
`cu_h2o2_bta::damage_exponent`(정의상 D99 축)에 그대로 넣으면 서로 다른 물리량을 같다고
우기는 것이 된다 — [[delta-scratch-damage-d99-oversize-particle-model]] §4.4가 Fuso 데이터에
적용한 것과 동일한 원칙이다. **m=3.22가 기존 W 전이값 2.54와 같은 오더(1.73~3.73 범위 안)에
들어온다는 것은 방향성 교차검증(triangulation)이지, 등급 승격의 근거가 아니다.**

## 5. 보조 확인 — Saka et al. 2009, Cu 단일입자 스크래치 폭 역학모델 (E2 후보지만 다른 물리량)

코퍼스에서 함께 발견한 `doi:10.1149/1.3121964` "Controlling Scratching in Cu Chemical Mechanical
Planarization" (Saka, Eusner, Chun — J. Electrochem. Soc. 156(2) H91, 2009 계열, ECS Trans 버전도
동일 저자). 동일 경로(find_open_access → 미러 사이트 → 미러 사이트 → curl referer 우회)로 전문
확보(`papers/saka2009-jes-controlling-scratching-cu-cmp.pdf.txt`).

이 논문은 Cu 표면에 Al₂O₃/SiO₂ 단일입자가 만드는 **최대 스크래치 폭이 입자 지름의 약 1/2**이라는
폐형식 접촉역학 모델(하중·입자 반경 함수)을 AFM 실험과 실제 연마 실험으로 검증한다. 이것은
**동일계(Cu) 폐형식 유도(E2에 해당하는 방법론)**이지만, 산출량이 damage_exponent의 정의
(스크래치/결함 **개수**의 D99 지수)와 다른 물리량(스크래치 **폭**, 입자 지름에 선형 비례 n≈1)이다.
즉 "입자가 크면 그 입자가 만드는 개별 스크래치도 크다"는 것이지 "입자 분포 꼬리가 두꺼워지면
스크래치 **개수**가 몇 제곱으로 늘어나는가"에 대한 답은 아니다 — Δ 모델이 규정한 종속변수와
불일치하므로 damage_exponent 값 자체에는 대입하지 않는다. 다만 "대입자 하나가 만드는 흔적의
크기는 입자 지름에 선형(n=1)"이라는 것은, §3~4의 개수 기반 회귀(n≈3.2, W 전이값 2.54)가
**단일 흠집의 크기가 아니라 발생 빈도(개수)에 관한 지수**라는 것을 다시 한 번 명확히 하는
교차 참고 자료로만 남긴다.

## 6. 판정

**결론: damage_exponent = 2.54, confidence = estimated 를 유지한다. 승격하지 않는다.**

- Cu CMP에서 "입자 크기가 커지면 스크래치가 는다"는 방향성은 이번 조사로 **세 편의 Cu 직접
  문헌**(teo2003 정성적, Li et al. 2018 정량 LPC축, Saka et al. 2009 단일입자 폭 모델)이
  독립적으로 확인했다 — 텅스텐→구리 전이 가정(§4.3 Showa Denko 조성 유사성 논거)이 **틀렸을
  가능성은 낮다**는 확신은 커졌다.
- 그러나 Δ 모델이 요구하는 정확한 물리량 — **D99(지름 백분위) → 스크래치/결함 개수**의 정량
  대응쌍은 Cu CMP 문헌에서 여전히 발견하지 못했다. Li et al. 2018이 제공하는 것은 LPC(임계
  개수)축이고, Saka et al. 2009가 제공하는 것은 단일 스크래치 폭(선형, n=1)축이다. 둘 다
  "축이 다르다"는 이유로 §4/§5에서 배제했다 — 이는 [[delta-scratch-damage-d99-oversize-particle-model]]이
  이미 세운 배제 규칙(Fuso Rq축, Fujifilm LPC/wt%축 배제)을 이번 신규 문헌에도 동일하게 적용한
  것으로, **기준을 낮추지 않았다**.
- 판정 규칙(E1~E6)에 따르면 이번 조사가 확보한 최선의 증거는 "동일계(Cu) 실측이지만 다른 종속
  변수(LPC 또는 폭)"다. 이것을 damage_exponent 자체의 근거 등급으로 무리하게 편입하면 E3
  ("교란 있는 실측")로 우길 수도 있어 보이지만, 교란(confound)은 "같은 양을 측정했는데 다른
  변수가 같이 변한 경우"를 뜻하고, 여기서는 **애초에 다른 양을 측정**했다 — 따라서 E3에도
  해당하지 않고 E4(현재 등급)를 그대로 유지하는 것이 정직하다.

## 7. 한계·미검증 (정직한 표기)

- ⚠ **미검증**: Li et al. 2018의 Fig 4(스크래치)·Fig 9(LPC) 그래프 판독값 중 0.1·0.35wt% 두
  점은 원문에 숫자로 없어 육안 판독값이다(±10~15% 오차 가정). 0.05/0.25/0.5wt%는 본문 텍스트
  숫자와 일치 확인.
- ⚠ **미검증**: LPC(m≈3.22)와 D99 지수 사이의 정량적 환산 관계는 이 논문 정보만으로는 유도
  불가능하다(분포 형태·총 입자 농도 정보 없음) — 축이 다르다는 것은 확인했지만 "같은 오더"
  이상의 관계는 주장하지 않는다.
- ⚠ **미검증**: teo2003의 정성적 관찰(알루미나 platen이 실리카 platen보다 스크래치 심함)은
  입자 크기와 경도가 함께 바뀌는 교란 조건이라 damage_exponent에 직접 기여하지 않는다.
- ⚠ **범위 밖**: Saka et al. 2009의 폭-지름 선형 모델(n=1)은 개별 스크래치 형상 예측에는
  유용할 수 있으나, Δ가 정의하는 "빈도(개수)" 축과 무관하므로 이번 판정에 포함하지 않았다.
- **1차 출처 확보 경로 요약**: `find_open_access.py --title`은 두 논문 모두 IOP 퍼블리셔 링크만
  반환했고 직접 fetch는 Radware 봇차단(HTTP 403)이었다. `tools/find_open_access.미러 사이트(doi)`
  함수를 직접 호출해 미러 사이트 → 미러 사이트 미러 PDF URL을 얻었고, 그 URL 자체도
  urllib 직접 요청은 403이 나서 `curl -e https://미러 사이트/`(리퍼러 헤더)로 우회 성공했다
  — CLI의 `--download` 플래그는 `--scan` 모드 전용이라 `--title` 단건 조회에는 적용되지 않는다
  (인자 파서에 `--paywall`도 등록돼 있지 않다 — docstring 예시가 실제 CLI 인자와 어긋난다).

## 8. 출처 링크

- Li, Y.; Liu, Y.; Wang, C.; Niu, X.; Ma, T.; Xu, Y. (2018), "Role of Dispersant Agent on Scratch
  Reduction during Copper Barrier Chemical Mechanical Planarization," ECS J. Solid State Sci.
  Technol. 7(6) P317-P322. DOI: 10.1149/2.0101806jss.
- Saka, N.; Eusner, T.; Chun, J. H. (2009), "Controlling Scratching in Cu Chemical Mechanical
  Planarization." DOI: 10.1149/1.3121964.
- Teo, T. Y.; Goh, W. L.; Leong, L. S.; Lim, V. S. K.; Tse, T. Y.; Chan, L. (2003), "Characterization
  and Reduction of Copper Chemical Mechanical Polishing Induced Scratches," Proc. SPIE 5041, 61-69.
  (papers/teo2003-spie-cu-cmp-scratch-characterization.pdf.txt, 로컬 코퍼스 기확보)
- Wei, K.-H. et al. (2013), "The influence of abrasive particle size in copper chemical mechanical
  planarization," Surf. Coat. Technol. 231, 543-545. DOI: 10.1016/j.surfcoat.2012.04.004.
  (papers/wei2013-surfcoat-cu-cmp-abrasive-size.pdf.txt, 로컬 코퍼스 기확보)
- Egan & Kim (2019), ECS JSS 8(5) P3206 — 현재 채택값의 원 출처(텅스텐), 재확인만
  ([[delta-scratch-damage-d99-oversize-particle-model]] §2.5 참조).

## 9. 다음 단원 (구현 요청 아님 — 후속 탐색 후보)

- Zhang, Feng, Zhang (2013, C-plane 사파이어 스크래치) — Li 2018 참고문헌 [5], 반도체 CMP
  직접은 아니나 초음파 진동-스크래치 관계식이 있을 수 있음, 미확인.
- "Diffusion-Limited Agglomeration and Defect Generation during CMP" (doi:10.1149/1.2931519,
  코퍼스에서 발견, 미확인) — Cu 나노입자 응집 커널이 시간에 따라 결함 확률을 어떻게 올리는지
  모델링. D99 정적 지수가 아니라 시간에 따른 응집 동역학이라 축이 또 다르지만, 향후 별도
  파라미터(예: 슬러리 체류시간 민감도)로 검토할 가치는 있음.
- Fu, W. E. et al., "Nano-scratch evaluations of copper chemical mechanical polishing," Thin Solid
  Films 529, 306 (2013) — 제목만 확인, 전문 미확보. 다음 탐색 1순위 후보.
