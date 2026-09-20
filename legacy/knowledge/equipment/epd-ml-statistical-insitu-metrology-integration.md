# ML·통계 기반 EPD와 인시츄 계측 통합 — 최근 10년 리뷰와 정량 성능

> tool-endpoint Lv3-1. 선행(필수 상호링크): [[epd-optical-motor-friction-eddy-current-comparison]] (Lv1-1, 세 원리),
> [[epd-signal-processing-filtering-overpolish]] (Lv1-2, 필터·오버폴리시·SPRT 계보),
> [[epd-trace-removal-remaining-thickness-inversion]] (Lv2-2, 시각→제거량 역산),
> [[epd-film-type-suitability-transparent-multilayer-limits]] (Lv2-1, 막질 한계). 관련: [[../cmp/preston-luo-dornfeld-mrr]].
>
> Lv1·Lv2가 이미 다룬 **세 EPD 원리·이동평균/PauTa 필터·간섭 카운팅·막질 한계**는 여기서
> 반복하지 않는다. 이 노트의 초점은 그 위에 올라가는 세 가지다: **(a)** 최근 10년의 ML/통계
> 기반 EPD(변화점 검출·분류/회귀·가상계측 VM)와 그 **정량 성능**, **(b)** 인시츄 계측의
> 다중센서 통합(장비사 특허를 1차 자료로), **(c)** 한계·실패 모드. 산출물은 말미의 **모델
> 후보 표**로, Lv3-2(EPD 신호→제거량 모델, wear_aware_endpoint 확장)의 설계 입력이다.

## 1. 통계 기반 EPD의 계보 — SPRT·웨이블릿에서 관리도(T²)로

Lv1-2 §2c는 Das, Ganesan, Sikder, Kumar(2005, IEEE TSM 18:440–447)의 **웨이블릿 분해 +
순차확률비검정(SPRT) + 이동블록(moving block)** 방법을 EPD의 통계/패턴 계열 원형으로
소개했다(원문 미확보, 초록만). 최근 10년 문헌은 이 골격을 그대로 이어받아 확장한다.

**BenZakour & Taleb(2012)** — Das의 방법을 AE(음향방출) 신호에 적용하고 두 판별통계를
비교한다[1]. 웨이블릿(db) 다중해상도 8단계 분해로 detail 계수를 얻고, 블록 길이 $n=256$의
이동블록마다 detail의 **분산(variance)**과 **변동계수(CV=std/mean)**에 각각 SPRT를 걸어
상한 초과 시점을 종점 개시로 판정한다[1]. 시뮬레이션 신호에서 **분산 SPRT는 231번째,
CV SPRT는 202번째** 수집점에서 대립가설 $H_1$을 수락했다 — 즉 **CV 기반이 분산 기반보다
약 29점(12.6%) 먼저** 종점을 잡았고, 저자는 CV가 더 신뢰·효율적이라 결론한다[1]. AE 진폭이
연마 진행에 따라 감소한다는 관찰이 핵심 근거다(평균이 줄면 CV의 분모가 줄어 신호가 증폭).

**BenZakour(2012, 후속)** — 같은 AE 신호에 **웨이블릿 + 차원축소(PCA) + Hotelling T² 관리도**를
결합한다[2]. 1024점 신호를 db4 6단계 분해해 근사계수 10개로 줄이고(1024→10), PCA로 다시
5개 주성분(분산 큰 순 v₁,v₄,v₃,v₂,v₁₀)만 남겨 T² 관리도를 만든다[2]. 공정 in-control 평균
$7\times10^{-6}$에서 종점 전이 시 $5\times10^{-6}$로 평균이 이동하며(−28.6%), 실험상 종점은
370–380초 구간에 있다[2]. **PCA-웨이블릿 T²는 378초에서 검출(구간 안, 정확)**한 반면, 웨이블릿
계수에 T²를 직접 건 경우는 320초, MDS-웨이블릿은 329초에서 검출 — 둘 다 370초보다 일러
**under-polish(과소연마) 오검출**이었다[2]. 즉 차원축소 방식이 검출 타이밍을 좌우하고, PCA가
가장 정확했다.

⚠ **근거 한계**: [1][2]는 *International Journal of Computer Applications* / *IJCSIT*(AIRCC)
게재물로, 피어리뷰 수준이 낮은 저널이며 본 노트는 원 PDF를 직접 열지 못하고 검색엔진이
추출한 본문 발췌(도입·방법·결과 문단)만 확인했다 — **E5**로 취급한다. 다만 **방법론 계보 자체는
Das et al.(2005, IEEE TSM) 확립 방법의 직접 후속**이라, 방법의 정당성은 상위 근거가 뒷받침한다.
아래 §5 Block A/B에서 이들이 보고한 정성 결론(CV가 분산보다 민감, 검출 임계가 타이밍을 결정)을
합성 트레이스로 재현해 크기 규모를 대조한다.

## 2. 가상계측(VM)과 ML 대리모델 — 실측 없는 두께/압력 예측

**가상계측(Virtual Metrology, VM)**은 웨이퍼를 직접 재지 않고 장비 센서(압력·모터·유량·온도
등)와 공정 이력으로부터 계측값(제거량·두께·균일도)을 회귀 예측하는 계열이다. EPD가 "언제
멈출까"라면 VM은 "지금 결과가 얼마일까"를 실시간 추정해 피드포워드 제어로 잇는다. Lv1-2가
다룬 필터·임계 알고리즘과 달리, VM은 **다변량 회귀/ML 모델**을 쓴다.

**Rothe et al.(2025)** — Chemnitz공대·Infineon·Fraunhofer ENAS 공동 연구로, **5-zone(5구역)
연마 헤드의 방사형 계면압력 프로파일**을 FEM(유한요소) 대신 예측하는 ML 대리모델을 제안한다[3].
방법은 **함수형 주성분분석(functional PCA)**으로 FEM이 생성한 압력 프로파일 데이터셋에서
저차원 기저(basis)를 뽑고, **커널 릿지 회귀(kernel ridge regression)**로 구역별 인가하중→fPCA
계수를 사상한다[3]. 저자는 대리모델이 "상세 FEM과 정확도가 맞먹으면서 밀리초(millisecond)급
예측과 어느 입력이 어느 프로파일 변화를 유발하는지의 해석성을 제공한다"고 보고한다[3]. 계면압력은
Preston 제거율($\dot h=K_pPV$, [[../cmp/preston-luo-dornfeld-mrr]])의 $P$ 항 자체이므로, 이
대리모델은 곧 구역별 제거율·최종 두께 프로파일의 실시간 예측기로 쓰일 수 있다.

⚠ 본 노트는 [3]의 초록·참고문헌·저자정보는 확인했으나 **전문(RMSE/MAE 구체값, 유지 PC 개수,
데이터셋 크기, FEM 대비 배속)은 확보하지 못했다** — 해당 정량치는 **미검증**이다. 초록이 명시한
정성 주장(fPCA 저차원 기저 + KRR, ms급, FEM 정확도 매칭)만 §5 Block D에서 합성 프로파일로
"저차원 기저의 재구성 오차가 실제로 작아지는가"의 규모를 재현한다(문헌 수치 재현이 아니라
방법 타당성의 규모 확인임을 명시).

한편 순수 통계/특징선택 기반 VM도 CMP에 적용된다 — Nabil et al.(2021, IEEE ASMC)은 CMP
공정 산업 데이터셋에 필터+래퍼 결합 **하이브리드 특징선택**을 써서 VM의 예측정확도를 높이고
DB 저장·연산시간을 줄인다고 보고한다[4]. ⚠ [4]는 초록만 확인(HAL 리포지토리 프리프린트가
봇차단, IEEE 유료) — 구체 RMSE는 **미검증**, VM에서 특징선택이 핵심 전처리라는 방향만 채택한다.

## 3. 인시츄 계측의 다중센서 통합 — 음향방출(AE)과 장비사 특허

Lv1-1 §4는 "실제 양산 툴은 단일 원리가 아니라 조합해 쓴다"며 US6966816B2(Applied Materials,
광학+와전류 동일플래튼 통합)를 들었다. 최근 10년에는 여기에 **음향방출(AE)**이 유력한 인시츄
센서로 합류했다.

**Helu, Chien, Dornfeld(2014, Procedia CIRP)** — AE로 모사 STI CMP의 종점을 검출한 결과,
**전통적 마찰력(friction force) 방식보다 약 10초 빨리** 종점을 잡아 **5%의 오버폴리시를
방지**했다고 보고한다[5]. 또한 FFT(고속푸리에변환) 기반의 "endpoint frequency method"를
제시해, 종점을 **사전(a priori) 예측**하고 산업계 관행인 "box method"(고정시간창)보다 정확하며,
FFT 스펙트럼이 인시츄 **결함검출(fault detection)** 정보까지 부수적으로 준다고 한다[5]. AE가
마찰보다 유리한 물리적 이유는 마이크로/나노스케일 재료제거 기구에 대한 **감도·SNR이 높기**
때문이다(Dornfeld 그룹의 AE 계측 계보)[5]. ⚠ [5]는 Procedia CIRP(피어리뷰, Dornfeld 그룹)
논문이나 본 노트는 **초록만** 확인했다(전문 미확보) — 10초·5% 수치는 초록에 명시된 값이며
FFT 방법 세부(주파수 대역·임계)는 **미확인(E5)**. §5 Block C에서 10초/5%의 자기일관성과
Preston 환산을 재현한다.

**US10478937B2(Applied Materials, 2019 등록)** — "Acoustic emission monitoring and endpoint for
CMP", 발명자 Tang·Ishikawa·Cherian·Oh·Osterheld, 우선일 2015-03-05[6]. 명세서가 서술하는
다중센서 인시츄 구성(특허=1차 자료, 가중 0.9):

- 플래튼에 **AE 센서**를 두고, 폴리싱 패드를 관통하는 **도파관(waveguide, 뾰족한 needle/blunt
  probe)**을 슬러리 그루브까지 넣어 기판 변형(deformation)에서 나오는 음향을 낮은 감쇠로 받는다[6].
- 프로세서가 신호에 **FFT를 걸어 주파수 스펙트럼**을 만들고, 특정 대역의 세기(또는 국소
  극값의 폭)가 임계를 넘으면 하부층 노출로 보아 종점을 트리거한다 — **ILD/STI 연마에는
  225–350 kHz 대역**을 감시한다고 명시한다[6]. AE 센서 동작대역은 **125–550 kHz**[6].
- **복수 AE 센서**의 신호 도착 시간차 $T$를 **상호상관(cross-correlation)으로 삼각측량**해
  음향 이벤트의 웨이퍼 상 반경위치를 계산하고, 모터 엔코더로 센서-웨이퍼 상대위치를 안다[6].
  즉 단일 종점 시각을 넘어 **반경별(2D) 이벤트 매핑**까지 노리는 다중센서 융합이다.
- 종점 정보를 후속 스테이션 제어로 **피드포워드**하거나 되먹임할 수 있다고 서술[6].

이 특허는 Lv1-1의 US6966816B2(광학+와전류)와 짝을 이뤄, 장비사가 **광학·와전류·마찰·AE**를
서로 다른 정보원(반사·실두께·계면전이·이벤트음향)으로 융합하려는 방향을 1차 자료로 확증한다 —
어느 단일 센서도 모든 막질·모든 실패모드를 못 덮기 때문이다(§4).

## 4. 한계·실패 모드 — ML/통계도 물리 한계는 못 넘는다

새 알고리즘·센서가 늘어도 EPD의 근본 실패모드는 Lv2-1·Lv1-2가 정리한 물리 제약에서 온다.
ML은 이를 완화할 뿐 제거하지 못한다.

- **다층·투명막(원리적 신호 부재)**: Lv2-1이 정리한 대로 반사 신호는 금속 30–40 nm 이하에서
  투명화하고, 와전류는 유전막에 원리상 불가하다([[epd-film-type-suitability-transparent-multilayer-limits]]).
  아무리 정교한 분류/회귀도 **신호 자체가 없는 막질**에서는 예측 근거가 없다 — VM/ML이
  대체 센서(AE·모터전류)로 넘어가야 하는 이유.
- **패턴밀도 의존**: Lv1-2 §4는 디싱/침식이 오버폴리시 시간뿐 아니라 패턴밀도(37.5%/75% 라인에서
  ~800/200 Å)·슬러리 선택성·컨디셔닝에 좌우됨을 확인했다([[epd-signal-processing-filtering-overpolish]]).
  마찰/모터전류 기반 EPD는 **막질 대비(마찰계수 차)가 작으면 실패**하고(Lv1-1 §4), 이 대비는
  패턴밀도에 따라 달라진다. VM 회귀모델은 학습 시 본 패턴밀도 분포 밖에서 외삽 오차가 커진다.
- **드리프트(재학습 부담)**: 패드 마모·컨디셔너 열화·슬러리 배치 변화로 센서-계측 관계가
  시간에 따라 이동한다. §1의 BenZakour SPRT가 **블록마다 임계를 데이터 자체에서 갱신**하는
  것도, §2 VM이 특징선택으로 모델을 가볍게 하는 것도, 결국 이 드리프트에 대응하려는 설계다 —
  고정 임계/고정 모델은 드리프트에서 무너진다. 이는 Lv1-2 §1의 "윈도우 크기는 크다고 좋은
  게 아니다"와 같은 교훈의 연장이다.
- **검출 타이밍 트레이드오프**: §1의 BenZakour ijcsit가 보인 것처럼, 검출을 **민감하게** 하면
  (임계를 낮추면) 조기검출→under-polish(320초), **둔감하게** 하면 지연검출→over-polish가 된다.
  ML은 이 트레이드오프의 최적점을 자동화할 뿐, 트레이드오프 자체는 없앨 수 없다 —
  Lv2-2 §5의 오버폴리시 예산 논리([[epd-trace-removal-remaining-thickness-inversion]])와 동형.

## 5. 정량 재현

패키지 제약(pywt 부재)으로 웨이블릿은 이동블록 통계로 대체하되, 문헌이 보고한 **정성 결론과
크기 규모**를 numpy/scipy 합성 트레이스로 재현·대조한다. 각 블록은 문헌값을 상수로 박고 assert로 검사한다.

```python verify
import numpy as np

# ══ Block A: 변화점 검출 감도 — 분산 vs CV (BenZakour&Taleb 2012 재현[1]) ══
# 문헌: 분산 SPRT 231점, CV SPRT 202점에서 H1 수락 → CV가 먼저(29점, 12.6% 일찍)
lit_var_pt, lit_cv_pt = 231, 202
lit_ratio = lit_cv_pt / lit_var_pt
assert abs(lit_ratio - 0.874) < 0.005      # 문헌 두 검출점 비 재확인

# 합성 AE 트레이스: 연마 구간(높은 평균·낮은 분산) → 종점 전이(평균 감소 + 분산 증가)
rng = np.random.default_rng(0)
n = 400
transition = 250                            # 실제 물리 전이 인덱스
mean_pre, mean_post = 1.0, 0.6              # AE 진폭이 연마 진행에 따라 감소(문헌 관찰)
std_pre, std_post = 0.05, 0.12             # 종점 전이 시 신호 요동 증가
sig = np.empty(n)
sig[:transition] = rng.normal(mean_pre, std_pre, transition)
sig[transition:] = rng.normal(mean_post, std_post, n - transition)

# 이동블록 rolling 통계 + 초기블록 기반 상한(3σ류). CV는 평균 감소로 분모가 줄어 증폭됨.
W = 30
base = slice(0, 80)                          # in-control 초기 구간에서 임계 학습
var0 = np.var(sig[base]); cv0 = np.std(sig[base]) / np.mean(sig[base])
var_lim = var0 * 4.0                          # 분산 상한
cv_lim = cv0 * 2.0                            # CV 상한 (동일 배율 논리로 잡되 스케일만 다름)

def first_cross(metric_fn, lim):
    for i in range(W, n):
        blk = sig[i - W:i]
        if metric_fn(blk) > lim:
            return i
    return None

det_var = first_cross(lambda b: np.var(b), var_lim)
det_cv = first_cross(lambda b: np.std(b) / abs(np.mean(b)), cv_lim)
print(f"[A] 합성 검출: 분산={det_var}, CV={det_cv} (물리전이={transition})")
# 문헌 방향 재현: CV가 분산보다 먼저(작거나 같은 인덱스) 임계 초과
assert det_cv is not None and det_var is not None
assert det_cv <= det_var, "CV가 분산보다 늦음 — 문헌 방향(CV 우선) 반증"
syn_ratio = det_cv / det_var
print(f"[A] 검출점비 합성={syn_ratio:.3f} vs 문헌={lit_ratio:.3f} "
      f"(방향 일치; 정확한 값은 신호 파라미터 의존이라 크기 재현은 아님)")
```

```python verify
import numpy as np

# ══ Block B: PCA 차원축소 + T² 검출 타이밍 (BenZakour 2012 ijcsit 재현[2]) ══
# 문헌: 1024점→db4 6단계 근사 10계수→PCA 5성분; 평균 7e-6→5e-6(−28.6%);
#       종점구간 [370,380]s; PCA-웨이블릿 T²=378s(정확), 직접/MDS=320/329s(조기 under-polish)
mean_in, mean_ep = 7e-6, 5e-6
shift_pct = (mean_in - mean_ep) / mean_in * 100
assert abs(shift_pct - 28.57) < 0.1        # 평균 이동폭 재확인
lit_pca, lit_direct, lit_mds = 378, 320, 329
lit_window = (370, 380)
# 정확도 판정: PCA만 종점 구간 안, 나머지 둘은 구간보다 이르다(under-polish)
assert lit_window[0] <= lit_pca <= lit_window[1]
assert lit_direct < lit_window[0] and lit_mds < lit_window[0]

# (1) 차원축소 규모: 다변량 AE(상관된 여러 채널)에 PCA → 소수 성분이 분산 대부분 설명
rng = np.random.default_rng(1)
T, C = 1024, 10                              # 1024 타임스텝, 10 채널(≈근사계수 수)
t = np.linspace(0, 1, T)
latent = np.c_[np.sin(2*np.pi*t), t, t**2]  # 3개 잠재 신호가 실제 자유도
mix = rng.normal(size=(3, C))
X = latent @ mix + rng.normal(0, 0.01, (T, C))
Xc = X - X.mean(0)
_, S, _ = np.linalg.svd(Xc, full_matrices=False)
evr = (S**2) / (S**2).sum()
cum5 = evr[:5].sum()
print(f"[B] PCA 누적분산: 5성분={cum5*100:.2f}% (문헌: 10→5 성분 유지)")
assert cum5 > 0.99, "5성분으로 99% 미만 — 차원축소 규모 미달"

# (2) 검출 타이밍: 평균이동을 T²(정규화 편차²)로 잡되, 임계가 타이밍을 결정함을 재현
N = 400
ep_idx = int(0.94 * N)                       # 물리 종점 ~ 구간 후반(378/[370,380] 비율 모사)
y = np.empty(N)
y[:ep_idx] = rng.normal(mean_in, 0.3e-6, ep_idx)
y[ep_idx:] = rng.normal(mean_ep, 0.3e-6, N - ep_idx)
mu0, sd0 = y[:100].mean(), y[:100].std()
t2 = ((y - mu0) / sd0)**2                     # 단변량 T²
def detect(thr):
    run = 0
    for i in range(N):
        run = run + 1 if t2[i] > thr else 0
        if run >= 5:                          # 연속 5점 초과 시 종점
            return i
    return None
d_tight, d_loose = detect(4.0), detect(12.0)  # 낮은 임계=민감, 높은 임계=둔감
print(f"[B] 검출: 민감임계={d_tight}, 둔감임계={d_loose}, 물리종점={ep_idx}")
assert d_tight is not None and d_tight <= ep_idx + 8   # 민감 임계는 종점 근처/약간 조기
# 문헌의 378(정확) vs 320(조기) 차이 = 임계 민감도가 타이밍을 가른다는 것을 규모로 확인
assert (d_loose is None) or (d_loose >= d_tight)
print("[B] 임계 민감도가 검출 타이밍(정확 vs 조기 under-polish)을 좌우 — 문헌 정성결론 재현")
```

```python verify
import numpy as np

# ══ Block C: AE 조기검출 → 오버폴리시 (Helu et al. 2014 자기일관성 + 선행노트 연결[5]) ══
# 문헌: AE가 마찰보다 ~10초 빠름 → 5% 오버폴리시 방지
dt_early = 10.0          # s, AE가 마찰보다 앞선 검출 이득(문헌 명시)
overpolish_saved = 0.05  # 5% (문헌 명시)
# 자기일관성: overpolish% = Δt / t_polish  →  t_polish 역산
t_polish = dt_early / overpolish_saved
print(f"[C] 자기일관성: 10s가 5%면 총연마시간 t_polish={t_polish:.0f}s")
# 선행노트 Li2017의 EPD 주폴리싱 구간(20~220초, [[epd-optical-...]] §1)과 정합해야 함
assert 20 <= t_polish <= 260, "역산 t_polish가 문헌 EPD 구간(20~220s) 밖"

# Preston 환산: 선행노트 RR=229 nm/min(3psi)로 10초 조기검출의 제거량 이득
RR = 229.0 / 60.0        # nm/s (Lv1-2·Lv2-2 재사용)
gain_nm = RR * dt_early
print(f"[C] 10초 조기검출 = {gain_nm:.1f} nm 덜 깎음 (RR=229nm/min)")
# 선행노트 필터지연 초과제거(4.94s, 18.8nm, Lv1-2 §5)와 규모 비교
filt_delay_s, filt_over_nm = 4.94, 18.8
assert gain_nm > filt_over_nm       # AE 조기검출 이득이 필터지연분보다 큼
print(f"[C] AE 이득 {gain_nm:.1f}nm vs 필터지연분 {filt_over_nm}nm "
      f"(같은 오더; 센서 선택(AE)이 필터 튜닝만큼 오버폴리시에 영향)")
```

```python verify
import numpy as np

# ══ Block D: fPCA 대리모델 재구성 규모 (Rothe et al. 2025 방법 타당성 재현[3]) ══
# 문헌: 5-zone 방사형 압력 프로파일을 functional PCA 저차원 기저 + KRR로 예측(RMSE는 미확보)
# 여기서는 "5구역 하중의 프로파일이 저차원 기저로 낮은 오차 재구성되는가"의 규모만 확인
rng = np.random.default_rng(2)
Nr, Z = 64, 5                               # 방사좌표 64점, 5구역
r = np.linspace(0, 1, Nr)
# 각 구역은 반경상 겹치는 가우시안 기저압을 준다(5-zone 헤드의 물리 근사)
centers = np.linspace(0.1, 0.9, Z)
zone_basis = np.stack([np.exp(-((r - c)**2) / (2 * 0.12**2)) for c in centers])  # (Z,Nr)
M = 300                                      # FEM 프로파일 데이터셋 크기(합성)
loads = rng.uniform(0.5, 2.0, (M, Z))       # 구역별 인가하중
profiles = loads @ zone_basis               # (M,Nr) 압력 프로파일
profiles += rng.normal(0, 0.01, profiles.shape)  # 소량 수치잡음

Pc = profiles - profiles.mean(0)
U, S, Vt = np.linalg.svd(Pc, full_matrices=False)
evr = (S**2) / (S**2).sum()
k = 5                                        # 유지 fPCA 성분(구역 자유도 = 5)
cumk = evr[:k].sum()
recon = U[:, :k] @ np.diag(S[:k]) @ Vt[:k] + profiles.mean(0)
rmse = np.sqrt(np.mean((recon - profiles)**2))
rel = rmse / profiles.std()
print(f"[D] fPCA {k}성분 누적분산={cumk*100:.3f}%, 재구성 RMSE={rmse:.4f} (상대 {rel*100:.2f}%)")
# 5구역 하중이 5자유도이므로 5 fPCA 성분으로 분산 대부분 설명되어야 함(저차원 기저 타당성)
assert cumk > 0.999, "5성분으로 99.9% 미만 — 저차원 기저 가정 반증"
assert rel < 0.02, "재구성 상대오차 2% 초과 — 대리모델 정확도 규모 미달"
print("[D] 소수 fPCA 기저가 프로파일을 낮은 오차로 재구성 — Rothe2025 정성주장(FEM정확도 매칭) 규모 확인")
print("    (⚠ 문헌 RMSE 구체값은 전문 미확보로 재현 불가; 이 값은 합성 데이터 규모 확인일 뿐)")
```

재현 결과 요약: **[A]** 합성 트레이스에서 CV 기반 검출이 분산 기반보다 먼저 임계를 초과해
BenZakour의 방향(202<231)을 재현한다 — 평균이 감소하는 신호에서 CV의 분모 축소가 민감도를
높인다는 메커니즘이 원인(정확한 값 231/202는 신호 파라미터 의존이라 크기까지 재현한 것은 아님).
**[B]** 상관된 다변량 신호는 5 주성분으로 99% 넘는 분산을 담아(문헌 10→5 축소 규모와 정합),
평균 −28.6% 이동을 T²로 검출하되 **임계 민감도가 검출 타이밍(정확 378초 vs 조기 320초
under-polish)을 가른다**는 정성결론을 재현. **[C]** "10초/5%"는 총연마시간 200초에서 자기일관적이고
(선행노트 EPD 구간 20~220초와 정합), Preston RR로 환산하면 약 38 nm의 조기검출 이득 —
필터지연 초과제거(18.8 nm)와 같은 오더라 **센서 선택(AE)이 필터 튜닝만큼 오버폴리시를 좌우**함을
보인다. **[D]** 5구역 하중 프로파일은 5개 fPCA 성분으로 99.9% 넘게(상대 RMSE <2%) 재구성되어
Rothe의 "저차원 기저로 FEM 정확도 매칭" 주장의 규모가 타당함을 확인(단 문헌 RMSE 구체값은
전문 미확보로 미검증 — 위 값은 합성 규모 확인).

## 6. 모델 후보 표 — Lv3-2(EPD 신호→제거량, wear_aware_endpoint 확장) 설계 입력

| 입력 신호 | 알고리즘/모델 | 출력 | 문헌 보고 성능 | 적용 조건·한계 | 근거[등급] |
|---|---|---|---|---|---|
| AE detail(웨이블릿) 분산·CV | 이동블록 SPRT (var vs CV) | 종점 개시 시각 | CV가 분산보다 29점(12.6%) 조기검출 (202 vs 231) | 평균이 감소하는 신호에 유리; AE 센서 필요 | [1] E5 |
| AE 웨이블릿 근사계수(1024→10) | PCA 차원축소 + Hotelling T² | 종점 시각 | PCA-웨이블릿 378s(정확), 직접/MDS 320/329s(조기 under-polish) | 임계가 타이밍 좌우; 평균이동 −28.6% 검출 | [2] E5 |
| AE(FFT 스펙트럼) | endpoint frequency method(FFT) | 종점(사전예측)+결함 | 마찰 대비 ~10s 조기, 5% 오버폴리시 방지; box법보다 정확 | STI 모사; 마찰계수 대비 필요 | [5] E5(초록) |
| AE 다센서(도파관, 125–550kHz) | FFT 임계 + 상호상관 삼각측량 | 종점 + 반경별 이벤트맵 | ILD/STI 225–350kHz 대역 감시 | 장비 통합 필요; 특허 구현 | [6] 특허0.9 |
| 구역별 인가하중(5-zone) | fPCA + 커널릿지회귀 | 방사형 계면압력 프로파일 | ms급 예측, FEM 정확도 매칭(RMSE 미확보) | FEM 학습데이터 필요; 학습범위 밖 외삽 위험 | [3] 초록·미확보 |
| 장비센서 다변량(압력·모터·유량 등) | 하이브리드 특징선택 + ML 회귀 | 제거량/두께(VM) | 정확도↑·연산/저장↓(RMSE 미확보) | 학습 패턴밀도 분포 내에서만; 드리프트 재학습 | [4] 초록 |

**Lv3-2 설계 함의**: (i) EPD 신호→제거량은 Lv2-2 §4의 `removed = RR·(t_detect + t_overpolish)`
골격을 유지하되, **AE 조기검출 이득(§5 C)을 t_detect 보정항**으로 넣을 수 있다(센서별 검출지연이
다름). (ii) VM/fPCA 대리모델(§2·§5 D)은 Preston의 $P$ 항을 **구역별로** 실시간 공급해
wear_aware_endpoint를 균일도-인식으로 확장하는 경로다. (iii) 검출 임계는 고정하지 말고
드리프트 대응으로 **블록마다 갱신**(§1 SPRT 방식)해야 하며, 임계 민감도가 under/over-polish를
가르는 튜닝 파라미터임을 §5 B가 규모로 보였다. 구체 구현 요청은 PROFILE.md에 기재.

## 7. 확인 못 한 것 (미확보·미확인 명시)

- **Rothe et al.(2025) 전문**[3]: RMSE/MAE, 유지 fPCA 성분 수, 데이터셋 크기, FEM 대비 배속의
  구체 수치 — 전문 미확보로 재현 불가. §5 Block D는 문헌 수치 재현이 아니라 방법 타당성의
  합성 규모 확인이다.
- **Nabil et al.(2021, ASMC) VM**[4]: 특징선택 후 예측정확도·연산시간 감소의 구체 수치 — HAL
  프리프린트 봇차단·IEEE 유료로 초록만, 미확보.
- **Helu et al.(2014) FFT 세부**[5]: endpoint frequency method의 감시 주파수 대역·임계·box법과의
  정량 비교표 — 전문 미확보, 10s/5%만 초록에서 확인(**E5**).
- **BenZakour [1][2] 원 PDF**: 저품질 저널 게재물로 검색엔진 본문 발췌만 확인(**E5**). 231/202,
  378/320/329s 등 검출점은 발췌에 명시됐으나 원 PDF·그림은 미확인. 방법 계보만 Das(2005)로 상위확증.
- **US10478937B2 실측 성능**[6]: 특허 명세서는 구성·방법을 기술하나 검출지연·정확도의 **실측
  수치는 특허 특성상 없음**(청구범위 중심).

## 출처

1. S. Ben Zakour, H. Taleb, "Using Discrete Wavelet analysis and Sequential test to detect the
   endpoint in CMP process", *Int. J. Computer Applications* 42(4) (2012), doi:10.5120/5746-7953.
   (저품질 저널, 원 PDF 미확보 — 검색엔진 본문 발췌로 방법·결과 확인, E5. 방법 계보는
   Das et al. 2005 IEEE TSM의 후속 — [[epd-signal-processing-filtering-overpolish]] §2c.)
2. S. Ben Zakour, "PCA - Wavelet Coefficients for T2 chart to Detect Endpoint in CMP process",
   *Int. J. Computer Science & Information Technology (IJCSIT)* 4(4) (2012), doi:10.5121/ijcsit.2012.4402.
   (저품질 저널, 원 PDF 미확보 — 본문 발췌로 확인, E5.)
3. T. Rothe, A. Lauff, A. Shaporin, P. Thieme, M.A. Sayyed, K. Gottfried, J. Schuster, J. Langer,
   L. Jäckel, M. Stoll, H. Kuhn, "Real-Time Interfacial Pressure Prediction in CMP Using Machine
   Learning Surrogates of Finite Element Simulations", *Int. J. Automation Technology* 19(5):879–889
   (2025), doi:10.20965/ijat.2025.p0879 (Fraunhofer publica 미러 doi:10.24406/publica-5596).
   (초록·참고문헌·저자 확인, 전문 미확보 — RMSE 등 정량치 미확보.)
4. R. Nabil et al., "A hybrid feature selection approach for virtual metrology: Application to CMP
   process", *IEEE Advanced Semiconductor Manufacturing Conf. (ASMC)* (2021),
   doi:10.1109/asmc51741.2021.9435673. (초록만 확인 — HAL 프리프린트 봇차단, IEEE 유료, 미확보.)
5. M. Helu, J. Chien, D. Dornfeld, "In-situ CMP Endpoint Detection Using Acoustic Emission",
   *Procedia CIRP* 14:454–459 (2014), doi:10.1016/j.procir.2014.03.025. (피어리뷰, Dornfeld 그룹;
   본 노트는 초록만 확인 — 10s/5% 수치는 초록 명시, FFT 세부는 미확인 E5.)
6. US 10,478,937 B2, "Acoustic emission monitoring and endpoint for chemical mechanical polishing",
   Applied Materials, Inc. (발명자 J. Tang, D.M. Ishikawa, B. Cherian, J. Oh, T.H. Osterheld),
   우선일 2015-03-05, 등록 2019-11-19. https://patents.google.com/patent/US10478937B2/en
   (명세서 본문 확인: 도파관·125–550kHz·STI 225–350kHz·FFT 임계·상호상관 삼각측량 문단.
   특허=1차 자료, 가중 0.9. Lv1-1의 US6966816B2와 짝 — [[epd-optical-motor-friction-eddy-current-comparison]] §3.)
