"""인자 분해·민감도 — 무엇이 성능을 만들고, 무엇을 돌려야 바뀌는가.

사용자 지시(2026-09-06):
  "각 요소를 나눠서 적용한다고 생각해. 그래서 각각의 요소가 얼마나 performance기여에
   영향을 주는지, 변화시켰을때 어떻게 바뀔건지 예측해. 물리화학과 기타작용까지 다 포함해서"

소재 개발자가 실제로 묻는 두 가지 질문이 있고, 둘은 다르다:

  (A) 기여 분해 — "지금 이 MRR이 나온 데 각 요소가 얼마나 보탰나"
  (B) 민감도    — "무엇을 바꾸면 가장 크게 변하나" (다음 실험에서 돌릴 손잡이)

(A)는 현재 상태의 회계, (B)는 다음 행동의 근거다. 이 모듈은 둘 다 낸다.

## 왜 탄성도(elasticity)인가

    E_x = ∂ln(MRR) / ∂ln(x)   =  x가 1% 변할 때 MRR이 몇 % 변하는가

압력(psi)·농도(mM)·경도(Pa)는 단위가 전부 달라서 ∂MRR/∂x를 그대로 비교할 수 없다.
탄성도는 무차원이라 **모든 인자를 한 축에 올려놓고 비교**할 수 있다.

멱함수 관계에서 탄성도는 지수 그 자체다:
  - Preston MRR = Kp·P·V  →  E_P = 1.0, E_V = 1.0 (정확히)
  - plowing MRR ∝ H^-1.5  →  E_H = -1.5

**이것이 이 도구가 미검증 상태에서도 쓸모 있는 이유다.** 절대 상수(Kp, α)는
문헌 역산치라 못 믿지만, **지수는 물리 구조에서 나오므로 훨씬 강건하다.**
Kp가 2배 틀려도 "압력을 올리면 선형으로 늘어난다"는 관계는 유지된다.
→ 순위와 방향은 신뢰할 수 있고, 절대값은 아니다(POSITIONING.md §3와 같은 논리).

## 탄성도만으로는 부족하다 — 실무 레버리지

탄성도가 높아도 **실제로 못 바꾸는 인자는 쓸모가 없다.**
  - 압력 탄성도 1.0인데 공정 창이 2.5~3.5 psi(±17%)면 → 실질 변화폭 ±17%
  - Ce³⁺ 탄성도 0.5인데 0.05~0.40으로 8배 조절 가능 → 실질 변화폭 훨씬 큼

그래서 **leverage = 탄성도 × 실제 조절 가능 범위**를 함께 낸다. 이게 "다음 실험에서
무엇을 돌릴까"에 대한 진짜 답이다. 조절 범위는 팩의 `*_range` 또는 기본 가정에서 온다.

## 무엇을 다루나 (기타작용 포함)

  기계   : 압력, 회전수(속도), 패드 탄성률·asperity 밀도·곡률반경, 엣지 압력집중
  화학   : 산화제 농도, 억제제 농도, Ce³⁺ 분율, pH
  소모품 : 입자 크기, 패드 마모 이력
  기하   : 웨이퍼 반경, 회전축 거리(r_cc)

출력 지표도 MRR 하나가 아니다. **균일도(TTV·CV)에 대한 민감도를 따로 낸다** —
소재 개발자의 합격 기준은 제거율이 아니라 균일도인 경우가 많다.
같은 인자가 MRR은 올리면서 균일도는 망칠 수 있고, 그 상충이 곧 설계 문제다.

## 정직성 규약

- **이 민감도는 "모델의 성질"이지 "현실"이 아니다.** 모델이 틀렸으면 민감도도 틀린다.
  다만 지수는 구조에서 오므로 절대값보다 강건하다(위 참조).
- 팩에 없는 인자는 계산하지 않는다. 조용히 0으로 두지 않고 목록에서 뺀다.
- 수치미분은 중심차분 + 상대 스텝. 스텝 의존성을 검사해 불안정하면 표시한다.
- 상호작용(A의 효과가 B에 의존)은 별도로 계산하며, 이걸 안 보고 단일 인자만
  보면 오판할 수 있다는 걸 명시한다.
"""
from __future__ import annotations

import math
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Dict, List, Optional, Tuple

import numpy as np

_ROOT = Path(__file__).resolve().parent
if str(_ROOT.parent) not in sys.path:
    sys.path.insert(0, str(_ROOT.parent))

from sim.engine import Recipe, simulate  # noqa: E402
from sim.params import load_pack  # noqa: E402


# ── 인자 정의 ───────────────────────────────────────────────
@dataclass
class Factor:
    """조절 가능한 인자 하나."""
    key: str
    label: str
    domain: str          # mechanical | chemical | consumable | geometry
    where: str           # 'recipe' (Recipe 필드) | 'pack' (팩 파라미터)
    # 실무에서 조절 가능한 범위 (lo, hi). leverage 계산에 쓴다.
    practical_range: Optional[Tuple[float, float]] = None
    note: str = ""


FACTORS: List[Factor] = [
    # 기계 — 공정 조건
    Factor("pressure_psi", "다운포스", "mechanical", "recipe", (1.5, 5.0),
           "헤드 압력. 공정 창이 좁다"),
    Factor("rpm_wafer", "웨이퍼 회전수", "mechanical", "recipe", (30.0, 120.0)),
    Factor("rpm_platen", "플래튼 회전수", "mechanical", "recipe", (30.0, 120.0)),
    # 기계 — 패드 물성 (소모품 선택으로 바뀐다)
    # 스캔 범위는 문헌 관측 대역이다 — 근거:
    # knowledge/pad/pad-material-gw-effective-modulus-asperity-distribution.md §2
    # (Shi&Ring 2010 119 MPa ~ Sorooshian 2005 380 MPa, 독립 3그룹).
    # 2026-09-15 이전 범위 (3e8, 3e9)는 팩 기본값 1.316e8 을 포함하지도 않는
    # 근거 없는 대역이었다 — 스캔이 문헌 밖에서만 돌고 있었다.
    Factor("pad_E_star_pa", "패드 탄성률", "consumable", "pack", (1.19e8, 3.8e8),
           "패드 종류 선택으로 바뀐다"),
    Factor("pad_asperity_density_m2", "asperity 밀도", "consumable", "pack",
           (1e10, 1e12), "패드 구조·컨디셔닝 상태"),
    # R: Bozkaya&Muftu 2009 Table I 범위 25~100 um(base 50), Sorooshian 2005 2~50 um.
    Factor("pad_asperity_radius_m", "asperity 곡률반경", "consumable", "pack",
           (2e-5, 1e-4)),
    # 1/beta: 동일 분포족(지수) 1차값이 Sorooshian lambda=2.0 um 1건뿐이라 대역 근거가
    # 약하다 — 그 값을 중심으로 ±1 오더의 절반만 연다(근거 노트 §2 ⚠ 표기).
    Factor("pad_height_beta_inv_m", "패드 조도", "consumable", "pack",
           (1e-6, 5e-6), "컨디셔닝으로 조절"),
    # 화학
    Factor("oxidizer_wt_pct", "산화제 농도", "chemical", "pack", (0.5, 10.0),
           "Kaufman 단봉 — 정점 존재"),
    Factor("inhibitor_mM", "억제제 농도", "chemical", "pack", (0.1, 10.0),
           "BTA 등. 단조 억제"),
    Factor("ce3_fraction", "Ce³⁺ 분율", "chemical", "pack", (0.05, 0.40),
           "세리아 chemical tooth 활성점"),
    Factor("slurry_ph", "pH", "chemical", "pack", (2.0, 11.0),
           "표면 전하·용해도. ⚠연화 계수 있을 때만 반영"),
    # 소모품
    Factor("abrasive_size_nm", "입자 크기", "consumable", "pack", (20.0, 200.0),
           "⚠현재 엔진 미반영 — 아래 UNMODELED 참조"),
    # 기하
    Factor("center_offset_m", "회전축 거리 r_cc", "geometry", "recipe",
           (0.10, 0.30), "속도장 분포를 바꾼다"),
]

# 민감도가 0으로 나오는 인자들 — **0이 "영향 없음"을 뜻하지 않는다.**
# 왜 0인지 이유가 다르고, 그 구분을 흐리면 사용자가 "이 손잡이는 쓸모없다"고 오판한다.
#
# 유형 A: 물리가 아직 엔진에 연결 안 됨 (구현하면 살아난다)
# 유형 B: 팩에 필요한 계수가 없어 항이 꺼짐 (팩을 채우면 살아난다)
# 유형 C: 모델 구조상 상쇄됨 (구현으로 안 풀린다 — 아래 CANCELLED 참조)
UNMODELED_HINT = {
    "abrasive_size_nm": "[유형A] 입자 크기의 MRR 영향(Luo-Dornfeld 활성입자 수 ∝ 1/d³)이 "
                        "아직 엔진에 연결되지 않았다. slurry-chemist Lv2-2 노트에 물리는 있다.",
    "slurry_ph": "[유형B] pH→연화 계수(ph_softening_per_unit)가 팩에 없어 화학층이 pH를 "
                 "무시한다. 계수를 넣으면 살아나지만 그 값은 문헌 근거가 약하다.",
}

# 유형 C — GW alpha 역산이 패드 물성 효과를 정확히 상쇄한다.
#
# 현재 tier2.gw_physical_kp는 기준점에서 alpha_removal을 Kp에 맞춰 역산한다:
#     alpha = Kp·P_ref·V_ref / (n_contacts(P_ref) · V_ref)
# 그런데 n_contacts는 E*·η·R·조도에 의존하므로, 패드를 바꾸면 n도 바뀌지만
# alpha가 정확히 그 역수로 따라 움직여 MRR이 불변이 된다.
#
# 실측(2026-09-06): E*를 0.5/1/2 GPa로 바꾸면 n_contacts는 6357/3179/1589로
# 정확히 반비례하는데, alpha 역산 후 MRR은 셋 다 99.36 nm/min으로 동일했다.
#
# ⚠ 이건 버그가 아니라 **모델이 답할 수 없는 질문**이다. Kp를 한 점에서 맞추는 한
# 패드 물성의 절대 효과는 그 캘리브레이션에 흡수된다. 풀려면 서로 다른 패드의
# 실측 MRR이 최소 2점 있어야 alpha를 패드와 무관하게 고정할 수 있다.
# → 실데이터 캘리브레이션(M3)이 풀어야 할 문제이고, 그 전까지는 "모른다"고 말해야 한다.
CANCELLED_BY_CALIBRATION = {
    "pad_E_star_pa", "pad_asperity_density_m2",
    "pad_asperity_radius_m", "pad_height_beta_inv_m",
}


# ── 출력 지표 ───────────────────────────────────────────────
Metric = Callable[..., float]

METRICS: Dict[str, Tuple[Metric, str]] = {
    "mrr": (lambda r: float(np.mean(r.mrr_nm_per_min)), "평균 제거율 [nm/min]"),
    "ttv": (lambda r: float(r.metrics.ttv_nm), "TTV [nm] (낮을수록 좋음)"),
    "cv":  (lambda r: float(r.metrics.cv_pct), "CV [%] (낮을수록 좋음)"),
}


def _apply(recipe: Recipe, factor: Factor, value: float) -> Recipe:
    """인자 하나만 바꾼 새 Recipe. 팩 파라미터는 override로 주입한다."""
    import copy
    r = copy.deepcopy(recipe)
    if factor.where == "recipe" and hasattr(r, factor.key):
        setattr(r, factor.key, value)
    else:
        r.pack_overrides = dict(r.pack_overrides or {})
        r.pack_overrides[factor.key] = value
    return r


def _current_value(recipe: Recipe, factor: Factor) -> Optional[float]:
    """현재 조건에서 이 인자의 값. 없으면 None(계산 대상에서 제외)."""
    if factor.where == "recipe":
        v = getattr(recipe, factor.key, None)
        if v is not None:
            return float(v)
        # Recipe에 없으면 팩이 채운 값
    pk = load_pack(recipe.pack)
    ov = recipe.pack_overrides or {}
    if factor.key in ov:
        return float(ov[factor.key])
    if pk.has(factor.key):
        try:
            return float(pk.get(factor.key))
        except (TypeError, ValueError):
            return None
    return None


@dataclass
class Sensitivity:
    factor: Factor
    metric: str
    base_value: float          # 인자의 현재 값
    base_metric: float         # 지표의 현재 값
    elasticity: float          # ∂ln(metric)/∂ln(x)
    leverage: float            # 탄성도 × 실무 조절 폭(log 범위) — 실제 영향력
    stable: bool               # 스텝 크기를 바꿔도 값이 유지되는가
    modeled: bool = True       # 엔진이 실제로 이 인자를 쓰는가
    curvature: float = 0.0     # 2차 도함수(로그공간) — 정점/골 판별용
    note: str = ""

    def at_optimum(self) -> bool:
        """1차가 0인데 2차가 음수 = 지금 정점에 앉아 있다.

        이걸 '미모델링'과 구분하지 못하면 치명적이다: 산화제를 정점 농도에서
        재면 탄성도가 0으로 나오는데, 그건 '영향 없음'이 아니라 '이미 최적'이다.
        정반대 의미인데 숫자는 똑같이 0.000이다(2026-09-06 실제 오진).
        """
        # 임계값 주의: 수치 중심차분의 잔차가 1e-5 수준이라 1e-6은 너무 엄격해서
        # 실제 정점(산화제 3.0wt%, 곡률 -0.53)을 놓쳤다(2026-09-06).
        return abs(self.elasticity) < 1e-3 and self.curvature < -0.05

    def direction(self) -> str:
        if self.at_optimum():
            return "★정점"
        if not self.modeled:
            if self.factor.key in CANCELLED_BY_CALIBRATION:
                return "상쇄됨"
            return "미모델링"
        if abs(self.elasticity) < 1e-6:
            return "무영향"
        return "↑ 증가" if self.elasticity > 0 else "↓ 감소"


def elasticity(recipe: Recipe, factor: Factor, metric: str = "mrr",
               rel_step: float = 0.05, model: str = "tier2.gw_physical_kp") -> Optional[Sensitivity]:
    """중심차분으로 로그-로그 기울기를 구한다.

    두 가지 스텝(rel_step, rel_step/2)으로 계산해 값이 안정적인지 확인한다.
    불안정하면(수치 잡음·불연속) stable=False로 표시 — 숫자를 믿지 말라는 신호.
    """
    fn, _ = METRICS[metric]
    x0 = _current_value(recipe, factor)
    if x0 is None or x0 <= 0:
        return None
    try:
        m0 = fn(simulate(recipe, model=model))
    except Exception:
        return None
    if m0 <= 0:
        return None

    def slope(step: float) -> Optional[float]:
        try:
            hi = fn(simulate(_apply(recipe, factor, x0 * (1 + step)), model=model))
            lo = fn(simulate(_apply(recipe, factor, x0 * (1 - step)), model=model))
        except Exception:
            return None
        if hi <= 0 or lo <= 0:
            return None
        return (math.log(hi) - math.log(lo)) / (math.log(1 + step) - math.log(1 - step))

    # 2차 도함수(로그공간) — 1차가 0일 때 정점인지 무영향인지 가른다
    curv = 0.0
    try:
        h = rel_step
        lp = fn(simulate(_apply(recipe, factor, x0 * (1 + h)), model=model))
        lm = fn(simulate(_apply(recipe, factor, x0 * (1 - h)), model=model))
        if lp > 0 and lm > 0:
            lh = math.log(1 + h)
            curv = (math.log(lp) - 2 * math.log(m0) + math.log(lm)) / (lh * lh)
    except Exception:
        curv = 0.0

    e1 = slope(rel_step)
    e2 = slope(rel_step / 2)
    if e1 is None:
        return None
    stable = e2 is not None and abs(e1 - e2) <= max(0.02, 0.05 * abs(e1))
    e = e1 if e2 is None else (e1 + e2) / 2

    # leverage: 실무 범위를 로그 폭으로 환산해 곱한다
    lev = 0.0
    if factor.practical_range:
        lo, hi = factor.practical_range
        if lo > 0 and hi > lo:
            lev = abs(e) * math.log(hi / lo)

    modeled = abs(e) > 1e-9
    note = factor.note
    if not modeled:
        if factor.key in CANCELLED_BY_CALIBRATION:
            note = ("[유형C] GW alpha 역산이 이 인자의 효과를 상쇄한다 — 모델 구조상 "
                    "답할 수 없는 질문이다. 서로 다른 패드의 실측 2점이 있어야 풀린다(M3).")
        elif factor.key in UNMODELED_HINT:
            note = UNMODELED_HINT[factor.key]
        else:
            note = "민감도 0 — 엔진이 이 인자를 쓰지 않는다. '영향 없음'이 아니다."
    sens = Sensitivity(factor, metric, x0, m0, e, lev, stable, modeled, curv, note)
    if sens.at_optimum():
        sens.modeled = True
        sens.note = ("★ 현재 값이 정점이라 1차 민감도가 0이다 — '영향 없음'이 아니라 "
                     "'이미 최적'이다. 어느 방향으로 움직여도 MRR이 떨어진다.")
    return sens


def rank_factors(recipe: Recipe, metric: str = "mrr",
                 model: str = "tier2.gw_physical_kp") -> List[Sensitivity]:
    """모든 인자의 민감도를 구해 leverage 순으로 정렬한다."""
    out = []
    for f in FACTORS:
        s = elasticity(recipe, f, metric=metric, model=model)
        if s is not None:
            out.append(s)
    return sorted(out, key=lambda s: -s.leverage)


# ── 기여 분해 ───────────────────────────────────────────────
@dataclass
class Contribution:
    label: str
    domain: str
    factor_x: float        # 이 요소가 기여한 배수 (기준 조건 대비)
    note: str = ""


def decompose(recipe: Recipe, reference: Optional[Recipe] = None,
              model: str = "tier2.gw_physical_kp") -> Tuple[List[Contribution], float, float]:
    """현재 조건의 MRR을 기준 조건 대비 요소별 배수로 분해한다.

    곱셈 모델이라 로그 공간에서 가법적이다:
        ln(MRR/MRR_ref) = Σ ln(각 요소 배수)

    한 인자씩 기준값→현재값으로 옮기며 배수를 잰다(one-at-a-time).
    ⚠ 상호작용이 있으면 배수들의 곱이 전체 비와 정확히 일치하지 않는다.
    그 잔차를 'interaction' 항으로 명시한다 — 숨기면 분해가 거짓말이 된다.
    """
    fn, _ = METRICS["mrr"]
    ref = reference or Recipe(pack=recipe.pack)      # 팩 기본 조건
    m_ref = fn(simulate(ref, model=model))
    m_cur = fn(simulate(recipe, model=model))

    contribs: List[Contribution] = []
    prod = 1.0
    for f in FACTORS:
        x_ref = _current_value(ref, f)
        x_cur = _current_value(recipe, f)
        if x_ref is None or x_cur is None or x_ref <= 0:
            continue
        if abs(x_cur - x_ref) / x_ref < 1e-9:
            continue                      # 안 바뀐 인자는 기여 없음
        m_one = fn(simulate(_apply(ref, f, x_cur), model=model))
        factor_x = m_one / m_ref if m_ref else float("nan")
        if abs(factor_x - 1.0) < 1e-9:
            continue
        contribs.append(Contribution(f.label, f.domain, factor_x, f.note))
        prod *= factor_x

    total = m_cur / m_ref if m_ref else float("nan")
    inter = total / prod if prod else float("nan")
    if abs(inter - 1.0) > 0.01:
        contribs.append(Contribution(
            "상호작용(잔차)", "interaction", inter,
            "인자들을 하나씩 바꾼 곱과 전체 변화의 차이. 1.0에서 멀수록 "
            "인자를 따로 보면 안 된다는 뜻이다."))
    return contribs, total, m_cur


def interaction(recipe: Recipe, fa: Factor, fb: Factor,
                rel_step: float = 0.1,
                model: str = "tier2.gw_physical_kp") -> Optional[float]:
    """두 인자의 상호작용 강도 — 로그공간 혼합 2차 미분.

    0에 가까우면 독립(따로 최적화해도 된다).
    0에서 멀면 A의 최적값이 B에 따라 달라진다 = DOE에서 교호작용 항이 필요하다.
    """
    fn, _ = METRICS["mrr"]
    xa, xb = _current_value(recipe, fa), _current_value(recipe, fb)
    if not xa or not xb or xa <= 0 or xb <= 0:
        return None
    h = rel_step

    def m(sa: float, sb: float) -> Optional[float]:
        r = _apply(recipe, fa, xa * (1 + sa))
        r = _apply(r, fb, xb * (1 + sb))
        try:
            v = fn(simulate(r, model=model))
        except Exception:
            return None
        return math.log(v) if v > 0 else None

    pp, pm, mp, mm = m(h, h), m(h, -h), m(-h, h), m(-h, -h)
    if pp is None or pm is None or mp is None or mm is None:
        return None
    return (pp - pm - mp + mm) / (4 * math.log(1 + h) * math.log(1 + h))
