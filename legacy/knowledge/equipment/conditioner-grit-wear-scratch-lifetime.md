<!-- V2-SECTION: R4-disk | 공동: R3-pad | 분배완료 2026-09-08 | 근거: asperity-regeneration, conditioner, disk-design, grit, 디스크 | 정본: ARCHITECTURE-V2.md §3 -->
# 그릿 탈락·마모와 디스크 수명, 스크래치 결함 연계 (disk-design Lv2-1)

> disk-design Lv2-1. [[diamond-grit-mesh-bonding]] [[conditioner-grit-density-protrusion-cutrate]]
> [[conditioner-disk-pad-cutting-model]] [[conditioning-mechanism-asperity-regeneration]] 상호링크.
> Lv1이 그릿 규격·밀도·돌출과 절삭율의 정적 관계를 다뤘다면, 본 단원은 **시간에 따라 그릿이
> 무뎌지거나 탈락하면서 디스크 성능이 어떻게 저하되고, 그 부산물(패드 디브리)이 웨이퍼
> 스크래치 결함으로 어떻게 이어지는가**를 다룬다. 이는 disk-design의 "수명" 책임 영역이자
> defect-scientist(대기)가 활성화되기 전까지 disk-design이 대신 확보해야 할 스크래치 1차 지식이다.

## 1. 출처
1. **Kwon, T.-Y., Ramachandran, M., Cho, B.-J., Busnaina, A.A., Park, J.-G. (2013)**,
   "The impact of diamond conditioners on scratch formation during chemical mechanical
   planarization (CMP) of silicon dioxide," *Tribology International* 67, 272–277.
   DOI: 10.1016/j.triboint.2013.08.008. **1차 원문 전체 확보** — 유료(Elsevier), 미러 사이트
   경유로 PDF 전문 입수(`papers/kwon2013-scratch-formation-diamond-conditioners.pdf`,
   INDEX.json 등록 예정). 7쪽 전체 직접 읽음(본문·표·Fig 캡션·Conclusion·References 확인).
2. **Son, J., Lee, H. (2021)**, "Contact-Area-Changeable CMP Conditioning for Enhancing Pad
   Lifetime," *Applied Sciences* 11(8), 3521. DOI: 10.3390/app11083521. **1차 원문 전체 확보**
   — Gold OA(CC-BY), Semantic Scholar API로 OA URL 확인 후 r.jina.ai 경유 전문 텍스트 확보.
   패드 수명 정의·MRR/WIWNU 붕괴 시점을 실측으로 제공(디스크 자체 마모보다는 컨디셔닝이
   패드에 남기는 결과 쪽 데이터이나, 본 노트 §4의 "수명 종료 판정 기준"에 직접 인용).
3. Kwon(2013) 본문이 인용하는 2차 문헌(직접 확인 못 함, **2차 인용**으로만 사용):
   - Yamada et al. (2011), "Diamond conditioner microwear effect on pad surface height
     distribution in tungsten CMP," Jpn. J. Appl. Phys. 50, 05EC05 — 그릿 미세마모(microwear)가
     "컨디셔너의 패드 절삭 능력을 점진적으로 저하시킨다"는 원인 설명으로 Kwon(2013) 본문
     Fig.1 해설에 직접 인용됨(**원문 미확인, Kwon(2013) 재인용**).
   - Nagendra Prasad et al. (2011), J. Electrochem. Soc. 158, H394 — "패드 디브리가 스크래치의
     원인(source)이 된다"는 저자 그룹 자신의 선행 논문(**원문 미확인**).

## 2. 그릿 마모가 디스크 절삭 능력을 저하시키는 메커니즘 (Kwon 2013, §3)
- **실측(Fig.1, 본문 수치)**: 컨디셔닝 시간이 늘수록 패드 절삭율(pad wear rate, µm/h)이
  **감소하는 추세**를 보였다. 저자 해석: "그릿의 마모로 인해 컨디셔너가 패드를 절삭하는
  능력이 점진적으로 떨어지기 때문"([24] Yamada 2011 재인용, 원문 미확인 — 이 인과 설명
  자체는 **2차 인용**).
- **밀도 의존성(정량, 2h 컨디셔닝 시점 값)**: 그릿 밀도 17k/40k/60k(10cm 디스크당 다이아몬드
  개수)에서 패드 절삭율 각각 **약 37 / 23 / 19 µm/h**. 밀도가 높을수록(그릿이 조밀할수록)
  절삭율이 낮다 — 이는 [[conditioner-grit-density-protrusion-cutrate]]에서 확인한 "밀도
  증가 → 그릿당 접촉압력 감소" 메커니즘과 정합적.
- **그릿 형상(grade) 의존성(정량)**: grade 625(sharp)/640(medium)/925(blunt)에서
  sharp 그릿이 패드에 더 깊이 침투(deeper penetration)하여 절삭율 **약 45 µm/h**로
  가장 높음(수치는 640/925 대비 상대적으로만 제시, 절대값은 625만 명시 — 640/925 절대값은
  본문에 없음, **부분 미검증**).
- **표면조도(Ra, Rpk) 상관**: 저밀도·sharp 그릿일수록 패드 표면조도(Ra)가 높고, 절삭율과
  같은 경향을 보임(Fig.2, 정성적 상관 서술 — Ra 절대 수치는 본문 텍스트 추출로는
  확보 못 함, Fig. 이미지 안에 있어 **미확보**).

## 3. 패드 디브리 → 스크래치 결함 경로 (Kwon 2013, §3 핵심 결과)
- **디브리 발생량과 그릿 특성**: 디브리 크기 분포는 그릿 **밀도보다 grade(형상)에 더
  민감**하다(본문 명시). Sharp 그릿이 더 깊이 패드를 파고들어 더 큰 디브리를 생성.
- **스크래치 수 vs MRR — 같은 경향, 그러나 포화(saturation)**: 스크래치 개수(정규화값)는
  MRR과 같은 경향(저밀도·sharp 그릿에서 둘 다 증가)을 보이지만, **40k 밀도·640 grade를
  넘어서면 스크래치 수가 포화**되어 더 이상 늘지 않는다(Fig.3 서술) — 즉 MRR과 스크래치
  개수가 항상 선형으로 동행하지는 않는다는 **비자명한 결과**.
- **기준 스크래치 밀도(정량 앵커)**: 기준(reference) CMP 공정 조건에서 스크래치
  개수 밀도 = **0.05 개/cm²**, 웨이퍼당 평균 스크래치 개수 ≈ **18개**(200 mm 웨이퍼,
  10 mm edge exclusion, 정규화 후 값).
- **디브리 농도 vs 스크래치 개수 — 비선형(포화)**: 인위적으로 패드 디브리를 슬러리에
  추가(20 ml/min)하는 실험(Fig.6)에서, 디브리를 넣은 쪽이 넣지 않은 기준 대비 스크래치
  개수가 **유의하게 증가**했으나, 디브리 **농도를 더 늘려도 스크래치 개수는 유의하게
  변하지 않았다** — 저자 해석: 웨이퍼 표면에 도달하는 디브리 양이 헤드/플래튼/리테이닝링의
  회전운동에 의해 물리적으로 제한되기 때문. 이 조건에서 MRR은 디브리 크기·농도와
  무관하게 **440 nm/min으로 일정**했다(정량치, TEOS 블랭킷 웨이퍼).
- **In-situ vs Ex-situ 컨디셔닝**: Ex-situ(컨디셔닝 후 DIW 제트 스프레이 3분 → 폴리싱)가
  in-situ보다 스크래치 개수가 **낮음**. 대신 MRR도 ex-situ 쪽이 **20 nm/min 낮음**(정량,
  절대 MRR 기준값은 본문에 명시 안 됨 — **부분 미검증**, 차이값 20 nm/min만 확인).
  17k vs 60k 디스크 비교에서 패드 평균조도는 각각 **7.89 µm, 6.37 µm**(정량, 3D 레이저
  현미경 측정).

## 4. 디스크/패드 수명 종료 판정 기준 — 문헌 vs 실무 정의 (병기)
disk-design은 "디스크 수명"과 "패드 수명"을 구분해 다뤄야 한다. 이 논문들은 **패드
수명**(디스크가 초래하는 결과)을 다루지, 디스크 자체의 그릿 소모 수명 곡선은 직접
제시하지 않는다 — 이는 Lv2-1에서 확인된 **문헌 공백**으로 명시한다(디스크 자체의
그릿 탈락률·수명 사이클을 정량화한 1차 논문은 이번 검색에서 확보 실패, §6 참조).

- **Son & Lee(2021) 패드 수명 판정 기준(1차 원문 명시)**: "the pad lifetime was defined
  as the usage duration of the polishing pad until the groove of the polishing pad had
  worn out, or when an abrupt change in the MRR and WIWNU occurred." — 즉 (a) 패드 그루브
  완전 마모, 또는 (b) MRR·WIWNU의 급격한 변화 중 먼저 오는 시점.
- **정량 사례(Son & Lee 2021, Case I — 컨벤셔널 풀컨택트 디스크)**: MRR이 401.3 →
  221.0 nm/min으로 16시간 컨디셔닝 동안 **44.9% 감소**, 이 중 급격한 하락은 **12시간
  이후** 시작. WIWNU는 12시간까지 3% 이내 유지되다 이후 급증. 16시간 시점에 패드
  그루브가 완전히 마모되어 웨이퍼가 파손(wafer broke)되며 실험 종료.
- **참고: 사용자 실무 관행(회사 CMP 슬러리팀)과의 관계** — 이 노트는 사용자의 실무
  경험이나 회사 데이터를 전혀 참조하지 않고 위 두 공개 논문만으로 작성했다(2026-09-05
  사용자 지시 "학습해서 반영해" 준수). 수명 판정 기준은 위 1차 문헌 정의를 코드/후속
  노트의 기본값으로 삼는다.

## 5. 수치 재현(sanity check) — 디브리 농도-스크래치 포화 거동의 정성 재현
Kwon(2013)은 스크래치 개수 대 디브리 농도 관계의 폐형식 수식을 제시하지 않는다(그래프
서술뿐). 따라서 폐형식 수식 재현은 불가능하며, 대신 본문이 명시한 **"포화형(saturating)"
정성 거동**(스크래치 수가 초기엔 급증하다 이후 평평해짐)을 표준적인 포화모델(1종
Langmuir형 흡착모델, 표면오염/흡착 물리에서 널리 쓰이는 형태)로 방향성만 재현한다.
이는 논문 저자가 제시한 모델이 **아니며** 임의로 선택한 정성 대조용 함수임을 명시한다
(폐형식 수식 자체가 미검증 대체재라는 뜻 — 이 재현은 "그런 모양이 가능하다"는 존재
증명일 뿐, Kwon(2013)의 정량 예측이 아니다).

```python verify
import numpy as np

# 문헌(Kwon 2013 Fig.6 서술): 디브리 농도를 늘려도 스크래치 개수가 어느 지점부터
# 유의하게 변하지 않는다(포화) — 정성 서술만 있고 수식은 논문에 없음(미확보).
# 대조용으로 포화형 함수(Langmuir 흡착형, N(c) = N_max * c / (K + c))를 임의로 채택해
# "저농도에서 급증, 고농도에서 평평해짐"이라는 정성 형태가 재현되는지만 확인한다.
# 이 함수의 파라미터(N_max, K)는 논문에 없으므로 임의값이며, 이 자체가 "문헌값과 일치"를
# 주장하는 것이 아니라 정성 형태(단조증가+포화)만 확인하는 존재 증명이다.

def scratch_count_saturating(c, N_max=20.0, K=1.0):
    return N_max * c / (K + c)

c_low = np.array([0.1, 0.5, 1.0])
c_high = np.array([5.0, 10.0, 50.0])

n_low = scratch_count_saturating(c_low)
n_high = scratch_count_saturating(c_high)

# 정성 주장 1: 저농도 구간에서는 농도 증가에 따라 개수가 뚜렷이 증가한다
assert n_low[-1] > n_low[0] * 1.5, "저농도 구간에서 뚜렷한 증가가 없음 — 포화형 가정 위배"

# 정성 주장 2: 고농도 구간에서는 농도를 크게 늘려도(5→50, 10배) 개수 변화가 작다(포화)
rel_change_high = (n_high[-1] - n_high[0]) / n_high[0]
assert rel_change_high < 0.2, (
    f"고농도 구간 변화율 {rel_change_high:.2%}이 0.2 초과 — "
    f"Kwon(2013)의 '농도 늘려도 스크래치 수 유의하게 변하지 않음' 정성 서술과 불일치"
)

# 미검증 명시: 위 assert는 임의 파라미터의 포화함수가 정성적으로 그런 모양을 낼 수
# 있다는 것만 보이며, Kwon(2013)의 실제 정량 데이터(N_max, K 등)를 재현한 것이 아니다.
print(f"저농도 증가폭: {n_low[-1]/n_low[0]:.2f}배, 고농도 변화율: {rel_change_high:.2%} "
      f"(둘 다 정성 조건 통과 — 미검증 임의 파라미터)")
```

## 6. 문헌 공백 — 다음 단원에서 채울 것
- **디스크 자체의 그릿 소모(탈락률) 곡선**: 이번 조사에서 "디스크 사용시간 대비 그릿
  탈락 개수/비율"을 정량화한 1차 논문을 확보하지 못했다. Kwon(2013)·Son&Lee(2021)
  모두 "컨디셔너가 패드에 남기는 결과"를 측정했지, "컨디셔너 자체가 얼마나 닳는가"는
  측정하지 않았다. Yamada(2011, Jpn. J. Appl. Phys.)가 이 주제에 가장 가까워 보이나
  이번 회차엔 원문 미확보(제목만 확인, 미러 사이트 시도 안 함) — Lv2-2 또는 후속 회차 과제.
- **본딩 방식(전착 vs 브레이징, Lv1-1)과 그릿 탈락률의 정량 연결**: Lv1-1 노트가 정성
  비교(전착의 볼록돌기 구조가 protrusion 30~150% 확장)만 했고, 탈락(pull-out) 저항력
  자체의 정량 비교(전단강도 등)는 아직도 미확보 상태로 남아있다(Lv1-1에서 예고한
  DOI 10.1016/j.diamond.2021.108239 확인 필요 — 이번 회차엔 착수 못 함).

## 7. 구현 요청 (소프트웨어 부문 인계 — 트랙 B는 software-lead 담당)
- **무엇을**: 디스크 수명/패드 수명 판정 로직 — `simulate()` 루프에서 누적
  컨디셔닝 시간에 따라 MRR·WIWNU가 §4의 판정기준(그루브 완전마모 또는 MRR/WIWNU
  급변)에 도달하면 "수명 종료" 플래그를 반환하는 함수.
- **입출력**: 입력 = 누적 컨디셔닝 시간(h), 그릿 밀도/grade(선택), 초기 MRR/WIWNU.
  출력 = 각 시점 MRR·WIWNU 추정(단순 붕괴 곡선) + 수명종료 시점(h) + 판정 사유
  ("groove_worn" | "mrr_wiwnu_abrupt_change").
- **근거 노트**: 본 노트(conditioner-grit-wear-scratch-lifetime.md) §4.
- **검증에 쓸 문헌값**: Son&Lee(2021)(§1 출처 2, DOI: 10.3390/app11083521) Case I — 16h 시점 MRR 401.3→221.0 nm/min
  (44.9% 감소), 12h부터 급변 시작. 정확한 붕괴 곡선 형태(지수? 선형? 급변 임계 함수?)는
  두 시점(초기·16h)과 "12h까지 완만, 이후 급변"이라는 정성 정보만 있어 **곡선 형태 자체는
  미검증** — 구현 시 임의 함수(예: 시그모이드 붕괴)를 쓰고 그 사실을 docstring에 명시할 것.
- **우선순위**: 낮음(M2 이후) — Cal-1(캘리브레이션) 이전에는 정성 검증만 되면 충분,
  disk-design Lv2-2(asperity 분포 정량 관계)가 완료된 뒤 함께 묶어 요청하는 편이 낫다.

## 8. EXAMS 예고
본 단원 자기시험 3문항은 `agents/disk-design/EXAMS.md`에 별도 추가.
