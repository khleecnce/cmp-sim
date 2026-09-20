<!-- V2-SECTION: R3-pad | 근거: pad-, 패드, Cal-1, 시간축 보정 | 정본: ARCHITECTURE-V2.md §3 -->
# Cal-1: 패드 이력 로그(사용시간·컨디셔닝 횟수) → 시간축 보정 파라미터

> pad-lifecycle Cal-1(캘리브레이션 단원, ORG.md §7.3). 작성일: 2026-09-19.
> 선행: [[pad-usage-conditioning-history-time-dependent-kp-asperity]](Lv3-2, 1차 데이터 3건 보유)
> [[pad-wear-glazing-mrr-decay]] [[../pad/pad-material-gw-effective-modulus-asperity-distribution]](pad-material §5, 대조 대상)

## 0. 과제 정의와 이번 회차가 실제로 한 일

과제는 `pad_wear_half_life_h = 48.0 h (confidence=estimated)`의 1차 출처를 찾아 대조하는 것이다.
**먼저 중복 확인**: `knowledge/pad/pad-material-gw-effective-modulus-asperity-distribution.md` §5
(pad-material 에이전트, 2026-09-15, EVIDENCE-RULES #40이 이미 판정 승인)가 이 정확한 파라미터를
이미 조사했고 "1차 출처 확보 실패 — estimated 유지 권고"로 끝났다. 그 판정을 뒤집을 새 문헌은
이번 회차에도 찾지 못했다(같은 `find_open_access.py` 검색어로 재확인, §1). 같은 실패를 반복
보고하는 대신, 이 노트는 **이미 pad-lifecycle이 확보한 1차 출처 3건**(Sampurno 2011, Zhou 2018,
Wu 2013 — 전부 Lv3-2에서 원문 PDF 직접 확인)에서 "반감기로 강제 재해석하면 얼마가 나오는가"를
새로 계산해(§2) 48h와 대조하는 **추가 증거**를 만든다. pad-material의 브래킷(Son&Lee 2차 인용,
4.9~29h)과 달리 이번 브래킷은 전부 1차 출처다.

## 1. 대조 대상 값 재확인

```
knowledge/params/base.yaml:128
  pad_wear_half_life_h: {value: 48.0, unit: h, confidence: estimated,
                          source: knowledge/materials/pad-wear-glazing-mrr-decay.md}
```
`pad-wear-glazing-mrr-decay.md`(pad-lifecycle 소유 노트) 본문을 재확인했으나 "48"이나 반감기
수치는 **어디에도 없다** — source 필드가 가리키는 노트에 그 값의 근거가 실제로 없다는 것도
이번 회차의 확인 사항이다(grep 결과, 아래 verify가 이 사실 자체를 코드로 확인한다). 또한
`grep -rn pad_wear_half_life_h sim/`가 **공집합**이다 — 이 키는 엔진 어디에도 아직 연결되지
않은 orphan 파라미터다(`knowledge/components/process.yaml` 528행 `status: not_wired`가 이미
그렇게 표기). 대조할 물리량의 정의(무엇의 반감기인가 — asperity 높이? MRR? Kp?)조차 소스 노트
안에 명시돼 있지 않다는 것이 근본 문제다.

```python verify
from pathlib import Path
note = Path("knowledge/materials/pad-wear-glazing-mrr-decay.md").read_text()
has_half_life_term = ("반감기" in note) or ("half-life" in note.lower()) or ("half life" in note.lower())
has_48h_value = "48.0" in note or "48 h" in note or "48h" in note
assert not has_half_life_term, "source 노트에 반감기 용어가 실제로 있다면 이 절의 주장을 고쳐야 함"
assert not has_48h_value, "source 노트에 48h 수치가 실제로 있다면 이 절의 주장을 고쳐야 함"
print("확인: source 필드가 가리키는 노트 본문에 반감기(half-life) 용어·48h 수치 모두 없음")
```

## 2. 1차 출처 3건에서 재계산한 "의사 반감기" 브래킷

세 데이터셋 모두 [[pad-usage-conditioning-history-time-dependent-kp-asperity]] §2/§4/§5가 이미
"정체-후-감소(plateau-then-decline)가 단일 지수보다 우월하다"고 확립한 상태다. 즉 **엄밀한
반감기(첫 감쇠 시상수)는 이 데이터들의 자연스러운 출력이 아니다** — pad-material §5의 결론과
같은 이유(1항)로 이 노트도 동의한다. 그럼에도 fab-sim의 `pad_wear_half_life_h`가 이미 단일
지수/스칼라를 전제하므로, "정체-후-감소 적합 곡선이 초기값의 절반에 도달하는 시각"을 **의사
반감기**로 강제 재해석해 세 독립 1차 출처에서 계산한다 — 이는 "정답"이 아니라 정직한 대조용
브래킷이다.

```python verify
# Sampurno 2011(doi:10.1149/1.3567648, 원문 확보)과 Zhou 2018(doi:10.1149/2.0011806jss, 원문 확보)
# 의 정체-후-감소 적합(Lv3-2 노트 §2.4·§4.2, R^2>0.98 및 함수형 비교로 이미 검증됨)을 그대로
# 재적합해 "적합곡선이 y0/2에 도달하는 시각"을 의사 반감기로 계산한다.
import numpy as np
from scipy.optimize import curve_fit

def hockey(x, y0, xk, s):
    return np.where(x < xk, y0, np.maximum(y0 - s * (x - xk), 0.0))

# --- Sampurno 2011: W CMP, 연질 Politex 패드, 브러시 컨디셔닝, lambda(t) [um], t [h] ---
t_s = np.array([0.0, 0.5, 2.5, 5.5, 8.5])
lam = np.array([45.6, 45.9, 45.0, 39.8, 34.6])
ph_s, _ = curve_fit(hockey, t_s, lam, p0=[45.5, 2.5, 1.8], maxfev=20000)
y0_s, xk_s, s_s = ph_s
half_life_sampurno_h = xk_s + (y0_s - y0_s / 2) / s_s
print(f"Sampurno lambda(t) 의사반감기: {half_life_sampurno_h:.2f} h (적합: y0={y0_s:.2f}um, xk={xk_s:.2f}h, s={s_s:.3f}um/h)")
assert 14.0 < half_life_sampurno_h < 17.0, half_life_sampurno_h

# --- Zhou 2018: 융착실리카, 경질 패드, 브러시 컨디셔닝, MRR(t) [nm/min], t [min] ---
t_z = np.array([30., 60., 90., 120., 150., 180., 210., 240., 270., 300.])
rr09  = np.array([36.8, 46.2, 43.3, 44.0, 45.6, 38.0, 27.0, 21.7, 23.2, 20.9])
rr126 = np.array([47.5, 54.8, 56.3, 54.3, 46.0, 30.3, 32.3, 29.4, 28.9, 20.8])
m = t_z >= 60
half_lives_zhou_h = {}
for name, y, p0 in (("0.9psi", rr09, [45, 150, 0.25]), ("1.26psi", rr126, [55, 120, 0.3])):
    ph, _ = curve_fit(hockey, t_z[m], y[m], p0=p0, maxfev=40000)
    y0, xk, s = ph
    t_half_min = xk + (y0 - y0 / 2) / s
    half_lives_zhou_h[name] = t_half_min / 60.0
    print(f"Zhou MRR(t) {name} 의사반감기: {t_half_min/60:.2f} h (적합: y0={y0:.1f}, xk={xk:.1f}min, s={s:.4f}/min)")
assert 4.0 < half_lives_zhou_h["0.9psi"] < 5.0
assert 4.0 < half_lives_zhou_h["1.26psi"] < 5.0

# --- Wu et al. 2013 (doi:10.1149/2.036301jss): 컨디셔너 다이아 furrow, tau_wear~=15h 오더 성분만 ---
# A(t) = A_inf + (1-A_inf)*exp(-t/tau_wear); 감쇠 성분 자체의 반감기는 tau_wear*ln2 (A_inf와 무관)
tau_wear_h = 15.0
half_life_wu_h = tau_wear_h * np.log(2)
print(f"Wu 2013 furrow 감쇠성분 반감기: {half_life_wu_h:.2f} h (tau_wear~15h 오더, 원문 §5.2)")
assert 9.0 < half_life_wu_h < 12.0

fab_sim_current_h = 48.0
bracket = [half_lives_zhou_h["1.26psi"], half_lives_zhou_h["0.9psi"], half_life_wu_h, half_life_sampurno_h]
print(f"1차 출처 3건 의사반감기 브래킷: {min(bracket):.1f}~{max(bracket):.1f} h vs fab-sim 현재값 {fab_sim_current_h} h")
assert max(bracket) < fab_sim_current_h / 3.0, \
    "세 1차 출처 모두 48h의 1/3 미만이어야 이 노트의 핵심 주장(현재값이 과대 가능성)이 성립"
```

## 3. 대조 결과 — 값이 다르다, 그리고 왜 다른지

세 1차 출처의 의사 반감기는 **4.2~15.3 h**에 모여 있고, fab-sim 현재값 **48 h는 그 상단(15.3h)의
3배 이상**이다. **대조**: 문헌 브래킷 상단 15.3 h는 현재값 48.0 h의 절반에도 못 미친다(15.3 h < 24.0 h). Son&Lee 2차 인용으로 만든 pad-material §5의 브래킷(4.9~187h, 넓고 느슨함)과
달리 이번 브래킷은 좁고(4.2~15.3h) 세 개 다 48h 아래에 몰려 있다는 점이 다르다. 다만 **이 값을
그대로 "정답"으로 대입하면 안 된다** — 세 출처 모두 **컨디셔닝이 계속 돌아가는 조건**에서
측정됐다(Sampurno: 브러시 2 lbf 상시, Zhou: 매 연마 후 브러시, Wu: 컨디셔너 자체의 마모).
`pad_wear_half_life_h`가 fab-sim에서 의도하는 물리량이 "컨디셔닝이 있는 정상가동 중의 드리프트"
인지 "무컨디셔닝 glazing"인지조차 소스 노트에 명시돼 있지 않다(§1) — 이는 대조를 방해하는
근본적 모호성이며, 이번 회차로 해소하지 못했다.

또한 세 값 자체도 서로 3.6배(4.2h vs 15.3h) 차이 나 하나로 수렴하지 않는다 — [[pad-usage-conditioning-history-time-dependent-kp-asperity]]
§7.2가 이미 확립한 "패드 종류·컨디셔닝 방식이 시정수를 한 자릿수 넘게 흔든다"는 결론과
정합적이다. **즉 이 불일치는 측정 오차가 아니라 물리적으로 실재하는 조건 의존성**이다.

## 4. Cal-1 결론 — 이력 로그를 위한 시간축 보정 파라미터 제안

과제가 요구하는 "시간축 보정 파라미터"를 단일 반감기 스칼라로 만드는 것은 §2·§3의 근거로
**권장하지 않는다**. 대신 Lv3-2 §7.1이 이미 이식 가능 등급으로 확보한 구조를 그대로 제안한다:

```
상태(t) = y0                         (t < t_k)
상태(t) = y0 − s · (t − t_k)         (t ≥ t_k, 하한 0 또는 A_inf에서 clamp)
```

이력 로그가 제공하는 두 변수(`pad_usage_hours` 누적, `conditioning_count`)는 **t_k와 s의
공동 인자**로 들어가야 한다 — Zhou 2018 §4.2가 압력이 t_k만 바꾸고 s는 거의 안 바꾼다는 것을
보였듯, 컨디셔닝 강도/빈도는 t_k(플래토 길이)를 늘리는 효과로 모델링하는 것이 물리적으로
타당하다(컨디셔닝이 자주 될수록 "새 패드 상태"가 오래 유지된다). 다만 §6(PHM 2016 실장비
477웨이퍼)에서 이미 확인됐듯 **패드 사용시간 자체는 실장비 MRR과 거의 무상관**(ρ=0.030)이고
드레서 이력이 5배 이상 우세하므로, 시간축 보정 파라미터의 1순위 입력은 `pad_usage_hours`가
아니라 **`disk_usage_hours`(컨디셔너 이력)**여야 한다는 것이 이 회차의 부가 결론이다. 이는
2026-09-13 EVIDENCE-RULES 판정#8이 `pad_usage_hours`를 `_f_stab`에서 제외한 것과 정합한다.

## 5. 미검증·한계 (정직 표기)

- §2의 세 "의사 반감기"는 **정의상 반감기가 아니다** — 정체-후-감소(선형 감소부) 곡선을 억지로
  지수 반감기 프레임에 투영한 값이며, §3에서 이미 그 한계를 명시했다. **참고 브래킷일 뿐 대입
  가능한 문헌값이 아니다.**
- `pad_wear_half_life_h`가 실제로 어떤 물리량(asperity 높이? MRR? Kp?)의 반감기를 의도하는지
  소스 노트에 정의돼 있지 않아, "정의 자체가 다른 값끼리 비교"했을 위험이 있다 — **미검증**.
- Wu 2013의 τ_wear≈15h는 원문이 명시한 정밀값이 아니라 Lv3-2 §5가 "오더"로만 확보한 값이다
  (원문은 furrow 데이터를 정밀 지수 피팅하지 않았다) — 이 노트의 half_life_wu_h=10.4h도 그
  불확실성을 그대로 물려받는다.
- 결론적으로 **`pad_wear_half_life_h`의 confidence를 literature로 승격할 근거는 이번 회차에도
  확보하지 못했다** — pad-material §5의 "estimated 유지" 권고에 **동의**하며 뒤집지 않는다.
  이 노트의 기여는 승격이 아니라 (i) 대조 브래킷을 1차 출처로 좁힌 것, (ii) 시간축 보정
  파라미터의 구조·1순위 입력에 대한 구체적 제안(§4)이다.

## 6. 출처

1. Y. Sampurno, A. Rice, Y. Zhuang, A. Philipossian, "Correlation of Pad Topography, Friction
   Force and Removal Rate during Tungsten Chemical Mechanical Planarization", *ECS Transactions*
   34(1), 621–626 (2011). DOI: 10.1149/1.3567648. 원문 PDF 확보(`papers/sampurno2011-ecst-pad-abruptness-tungsten-cmp.pdf`, pad-lifecycle Lv3-2에서 직접 읽음).
2. Y. Zhou et al., "Study on Pad Performance Deterioration in Chemical Mechanical Polishing (CMP)
   of Fused Silica", *ECS J. Solid State Sci. Technol.* 7(6), P295–P298 (2018).
   DOI: 10.1149/2.0011806jss. 원문 PDF 확보(`papers/zhou2018-jss-pad-performance-deterioration-fused-silica.pdf`).
3. C. Wu et al., "Aggressive Diamond Characterization and Wear Analysis during Chemical Mechanical
   Planarization", *ECS J. Solid State Sci. Technol.* 2(1), P36–P41 (2013). DOI: 10.1149/2.036301jss.
   원문 PDF 확보(`papers/wu2012-jss-aggressive-diamond-wear.pdf`).
4. `knowledge/pad/pad-material-gw-effective-modulus-asperity-distribution.md` §5 — 동일 파라미터
   1차 출처 확보 실패 판정(pad-material 에이전트, 2026-09-15, EVIDENCE-RULES #40 승인). 대조 대상.
