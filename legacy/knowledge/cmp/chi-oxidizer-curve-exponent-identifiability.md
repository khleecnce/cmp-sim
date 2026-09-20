<!-- V2-SECTION: R2-slurry | 근거: oxidizer, 산화제, chi, 화학 | 정본: ARCHITECTURE-V2.md §3 -->
# χ 산화제 곡선 지수 `oxidizer_curve_n`은 현 데이터로 **식별 불가능하다** (구조적 판정)

> 작성일: 2026-09-14 | [Max워커] | 대상: `sim/chemistry.py::_oxidizer_term`,
> `sim/tier2_physics/slurry_components.py::mrr_oxidizer`
> 선행: [[w-cmp-wo3-passivation-oxidizer-kaufman]], [[cu-electrochemistry-pourbaix-bta-oxidizer-inhibitor]],
> [[oxidizer-redox-potential-decomposition-metal-suitability]]

## 1. 질문

`tools/blockers.py --cells` 기준 χ는 5팩 중 4칸이 C2(confidence<literature)에 걸려 있고,
금속 2팩의 병목은 산화제 곡선의 형상 파라미터다:

| 팩 | `oxidizer_curve_n` | `oxidizer_peak_wt_pct` | 비고 |
|---|---|---|---|
| cu_h2o2_bta | 2.0 (**unverified**) | 3.0 (verified) | n이 χ/cu 칸을 혼자 막는다 |
| w_fe_oxidizer | 3.0 (estimated) | 6.0 (estimated) | 둘 다 estimated |

질문: **n을 문헌·제1원리로 확정해 등급을 올릴 수 있는가?**

결론부터: **없다. 그리고 그 이유는 "문헌을 못 찾아서"가 아니라 모델 구조 자체가
현재 데이터로 n을 식별하지 못하기 때문이다.** 이것이 이 노트의 결과다 — 앞선 시도들이
"문헌 미확보"로 종결된 진짜 원인이 여기 있다.

## 2. 1차 출처 (papers/에 원문 확보)

1. Lim, Lee et al. (2013), "Investigating the catalytic effect of Fe(NO₃)₃ on the performance of
   tungsten CMP in H₂O₂-based acidic slurries", *Appl. Surf. Sci.* 282, 512.
   **DOI: 10.1016/j.apsusc.2013.06.005** — `papers/lim2013-apsusc-fe-nitrate-w-cmp.pdf` 전문 확보.
   Fig.1 실측(1.0 wt% H₂O₂, pH 2.3, 6 psi, 70 rpm): Fe(NO₃)₃ 무첨가 56 Å/min →
   0.01 wt% 923 Å/min → 0.05 wt% 1177 Å/min → 0.1 wt% 위(region II)는 완만 증가.
2. Aksu, Doyle (2003), "The electrochemical behavior of copper in Na₂SO₄ solutions containing
   peroxide, BTA and glycine", *Electrochimica Acta* —
   `papers/aksu2003-electrochimica-bta-glycine-cu-cmp.pdf` 전문 확보. 본문 명시:
   "peroxide concentration was in the region of **1–3%**. Further increase in H₂O₂ concentration
   resulted in reduction of dissolution" (>3%에서 Cu 부동태화).
   → **cu_h2o2_bta의 `oxidizer_peak_wt_pct`=3.0을 독립 확증**한다. 단 n은 주지 않는다.
3. Kaufman et al. (1991), W CMP 메커니즘 — `papers/kaufman1991-w-cmp-mechanism.pdf`.
   단봉(정점형) 구조의 원형 근거. 형상 지수의 정량값은 없다.
4. w_fe_oxidizer 팩의 현행 값 출처: `papers/US20110186542A1.txt` (실측 3점 0/1/3 wt%,
   상대비 0.14/0.63/1.00).

## 3. 모델 구조와 식별성 분석

현행 곡선(`mrr_oxidizer`):

    g(x) = (n+1)·x / (1 + n·x^((n+1)/n)),   x = C/C_peak      … g(1)=1 에서 정점

여기에 기계 하한 φ를 가산 결합하고 기준 농도로 상대화한 것이 χ의 산화제 항이다:

    f(C) = [φ + (1-φ)·g(C/C_peak)] / [φ + (1-φ)·g(C_ref/C_peak)]

**관측이 정점 아래(C < C_peak)에만 있으면 (n, C_peak)는 한 방향으로 완전히 축퇴한다.**
n을 키우면서 C_peak를 함께 키우면 정점 아래 구간의 곡선이 **잔차 0으로** 동일하게 재현된다.
즉 데이터는 두 파라미터의 조합(저농도 구간의 곡률) 하나만 고정하고, n 단독은 고정하지 못한다.

## 4. 정량 대조

### (A) w_fe_oxidizer — 3점 데이터는 n을 전혀 제약하지 않는다
US20110186542A1 실측 2개 구속조건(1 wt%→0.63, 3 wt%→1.00, φ=0.14)에 대해
n을 0.5~8로 바꿔가며 최적 C_peak를 재적합하면 **모든 n에서 잔차가 0**이다(§6 verify).
n=0.5→C_peak=22.1 / n=2→41.1 / n=6→83.0 wt%. 전부 관측을 동일하게 재현한다.

**정량 대조(문헌값 vs 모델):** US20110186542A1 실측 상대비를 기준으로,
n=0.5(C_peak=22.1 wt%)·n=2(41.1 wt%)·n=6(83.0 wt%) 세 해가 모두
1 wt%에서 63.00% / 3 wt%에서 100.00%를 재현한다 — 문헌값 63% / 100% 대비 오차 <0.01%.
즉 서로 12배 차이나는 n 값들이 **문헌값을 동일한 정밀도로 재현**한다.

또한 팩에 저장된 (n=3, C_peak=6.0)은 **잔차 최소해조차 아니다** — 1 wt% 예측 0.6373로
관측 0.63 대비 +1.16% 어긋난다(같은 n=3의 잔차 0 해는 C_peak=52.3). 기존 격자 적합이
거칠었던 탓이며, 이는 "값이 틀렸다"가 아니라 **애초에 정할 수 없는 값을 정한 척했다**는 뜻이다.

### (B) cu_h2o2_bta — 기준 운전점에서 n은 수학적으로 죽은 파라미터
이 팩은 C = C_ref = C_peak = 3.0 wt%다. 그러면 f(C)의 분자와 분모가 **항등적으로 같아**
n에 무관하게 정확히 1.000000000000이다(§6 verify). n은 what-if 스캔(농도를 바꿔볼 때)에서만
값에 영향을 준다. 영향 크기(§6 verify 블록이 실행해 확인하는 모델 자체 출력, 문헌값 아님):
C=1 wt%에서 n=1 vs n=6 예측차 35.5%, C=2 wt%에서 5.6%.
Aksu 2003 문헌값(정점 1~3% 구간, >3%에서 감소)과 대조하면 C_peak=3.0 wt%는 일치하나,
같은 문헌이 n에 대해서는 어떤 제약도 주지 않는다.

### (C) 축퇴를 깨는 데 필요한 데이터
정점 **위쪽** 측정점이 있어야 한다. C=6 wt%에서 n 구분폭 7.4%, 10 wt%에서 19.0%,
20 wt%에서 28.5%. 즉 **C_peak의 2배 이상 농도에서 측정 1점**이면 n이 식별된다.
현재 코퍼스에는 금속 CMP에서 정점 위 농도를 스윕한 MRR 실측이 없다(Aksu 2003은
용해거동만, Lim 2013은 촉매 농도축이라 H₂O₂ 축이 아니다).

## 5. 결론 및 판정

- **값 변경 없음.** cu `n`=2.0(unverified), w_fe `n`=3.0/`C_peak`=6.0(estimated) 유지.
- 등급도 올리지 않는다. **올릴 근거가 없는 것이 아니라, 올릴 대상 자체가 식별 불가능**하기 때문이다.
  식별 불가능한 파라미터에 literature 등급을 주는 것은 오염이다.
- 이것은 "3회차 미확보 순환"이 아니라 **구조적 종결**이다: 왜 확정할 수 없는지가
  수치로 증명됐고(§4), 무엇이 있으면 확정되는지도 명시됐다(§4C). 다음 회차가 같은 자리를
  다시 돌 이유가 없다.
- 후속 경로는 두 갈래이며 **문헌 탐색이 아니라 구현 과제**다:
  (a) 정점 위 농도 실측 1점 확보 시 n 즉시 식별 → 그때 등급 승격.
  (b) 재파라미터화 — 식별 가능한 조합 하나(저농도 곡률)만 노출하고 n·C_peak를 내부로 숨기면
      "미검증 파라미터 2개"가 "문헌값 1개"로 바뀐다. 모델 형태 변경이라 소프트웨어 부문 소관.

## 6. 검증

```python verify
import sys, math, pathlib
ROOT = pathlib.Path(__file__).resolve().parents[2] if "__file__" in dir() else pathlib.Path(".")
sys.path.insert(0, str(ROOT / "sim" / "tier2_physics"))
from slurry_components import mrr_oxidizer as g

def term(C, C_ref, C_peak, n, phi):
    """chi 의 산화제 항 — sim/chemistry.py::_oxidizer_term 과 동일 형태."""
    cur = phi + (1 - phi) * g(C, C_peak, 1.0, n)
    ref = phi + (1 - phi) * g(C_ref, C_peak, 1.0, n)
    return cur / ref

# ── (B) cu_h2o2_bta: C = C_ref = C_peak = 3.0 이면 n 은 결과에 전혀 영향이 없다 ──
for n in (0.5, 1.0, 2.0, 3.0, 5.0, 10.0, 50.0):
    v = term(3.0, 3.0, 3.0, n, 0.15)
    assert abs(v - 1.0) < 1e-12, f"기준 운전점에서 1.0이 아님: n={n}, v={v}"
# 그러나 what-if 스캔에서는 살아난다 — '죽었다'고 잘라 말하면 그것도 거짓이다
lo = term(1.0, 3.0, 3.0, 1.0, 0.15)
hi = term(1.0, 3.0, 3.0, 6.0, 0.15)
spread = (hi - lo) / lo * 100
assert 30.0 < spread < 40.0, f"C=1wt% 에서 n 민감도가 예상(35.5%)과 다름: {spread:.1f}%"

# ── (A) w_fe_oxidizer: US20110186542A1 실측 2구속(1wt%->0.63, 3wt%->1.00) ──
# 모든 n 에 대해 잔차 0 인 C_peak 가 존재한다 = n 은 식별되지 않는다.
PHI_W = 0.14
OBS = {1.0: 0.63, 3.0: 1.00}          # 문헌 상대비 (0 wt% = phi = 0.14)
ridge = {}
for n in (0.5, 1.0, 2.0, 3.0, 4.0, 6.0, 8.0):
    best = None
    for i in range(1, 20000):
        Cp = 3.001 + i * 0.005
        e = sum((math.log(term(C, 3.0, Cp, n, PHI_W)) - math.log(v)) ** 2
                for C, v in OBS.items())
        if best is None or e < best[1]:
            best = (Cp, e)
    Cp, e = best
    ridge[n] = Cp
    # 핵심 주장: 잔차가 수치오차 수준(0)까지 내려간다
    assert e < 1e-8, f"n={n} 에서 잔차가 0 이 아님({e:.2e}) — 축퇴 주장 반증"
    assert abs(term(1.0, 3.0, Cp, n, PHI_W) - 0.63) < 1e-4, f"n={n} 1wt% 재현 실패"
# 축퇴 방향: n 이 커지면 C_peak 도 단조 증가
ns = sorted(ridge)
assert all(ridge[ns[i]] < ridge[ns[i + 1]] for i in range(len(ns) - 1)), \
    f"축퇴 릿지가 단조가 아님: {ridge}"
assert ridge[0.5] < 30.0 < ridge[2.0] < 60.0 < ridge[6.0], f"릿지 위치 예상 밖: {ridge}"

# ── 팩 저장값 (n=3, C_peak=6.0) 은 잔차 최소해가 아니다 (+1.16% 어긋남) ──
stored = term(1.0, 3.0, 6.0, 3.0, PHI_W)
err_pct = (stored - 0.63) / 0.63 * 100
assert 1.0 < err_pct < 1.4, f"팩 저장값 오차가 문서 서술(+1.16%)과 다름: {err_pct:+.2f}%"

# ── (C) 축퇴를 깨려면 정점 위 측정이 필요하다: 구분폭이 농도와 함께 커진다 ──
def spread_at(C):
    vs = [term(C, 3.0, ridge[n], n, PHI_W) for n in (0.5, 2.0, 6.0)]
    return (max(vs) - min(vs)) / min(vs) * 100
s6, s10, s20 = spread_at(6.0), spread_at(10.0), spread_at(20.0)
assert s6 < s10 < s20, f"고농도로 갈수록 구분이 쉬워져야 함: {s6:.1f} {s10:.1f} {s20:.1f}"
assert s6 < 10.0 and s20 > 25.0, f"구분폭 크기가 문서 서술과 다름: {s6:.1f}% / {s20:.1f}%"
print(f"OK — 축퇴 확인. 릿지={ {k: round(v,1) for k,v in ridge.items()} }, "
      f"구분폭 6/10/20wt% = {s6:.1f}/{s10:.1f}/{s20:.1f}%")
```

## 7. 한계·미검증

- **미검증**: `oxidizer_mech_floor` φ(cu 0.15 기본값, w_fe 0.14 실측)가 이 분석의 입력이다.
  φ가 틀리면 릿지 위치가 이동한다. 단 **축퇴의 존재 자체는 φ와 무관**하다(정점 아래
  관측만으로는 두 파라미터를 못 가르는 것은 함수형의 성질이다).
- **미검증**: Lim 2013의 축은 촉매 Fe(NO₃)₃ 농도이지 H₂O₂ 농도가 아니다. 이 노트는
  Lim을 "정점형 구조와 region I/II 꺾임의 실재" 확증으로만 쓰고, n의 수치 근거로는 쓰지 않았다.
  (촉매축을 산화제축에 대입하는 것은 EVIDENCE-RULES E4 전이이며 크기 채택 불가.)
- **1차 미확보**: 금속 CMP에서 C_peak의 2배 이상 산화제 농도를 스윕한 MRR 실측.
  Aksu 2003은 용해속도(SER 계열)만 보고하며 MRR이 아니다.
- 세리아 2팩(sic/sti)의 χ 병목(`ceria_tooth_gain`)은 EVIDENCE-RULES 판정#13에서
  2026-09-14 이미 미확보 종결 — 이 노트의 범위 밖이다.
