"""문헌에 없는 값을 만났을 때 무엇을 할 것인가 — 탈출 경로 판정.

왜 이 모듈이 필요한가
────────────────────
"문헌 미확보 → BLOCKED"로 적고 멈추면 절차가 거기서 끝난다. 그런데 우리가
만드는 것은 **어떤 슬러리든 넣으면 모델식이 나오는 절차**다. 절차가
"문헌에 없으면 못 합니다"로 끝나면 그것은 미완성이다.

실제로 물리 모델링에서 미지량을 다루는 길은 여럿이고, 대부분은 그 값을
**알아내지 않고도** 결론을 내는 길이다. 아래 8개로 정리한다.

탈출 경로
─────────
R1 소거      모델을 다시 써서 미지량이 **비 또는 도함수로만** 나타나게 한다.
             절대값이 약분된다. 가장 강력하다 — 값을 영영 몰라도 된다.
             판정: X를 10배 바꿔도 출력(순위)이 그대로인가?

R2 부등식    절대값은 모르지만 한쪽 경계는 안다. 한쪽 방향 결론만 낸다.
             "모르니 벌크값으로 대체"와 다르다 — 부등식이 허용하는 만큼만 말한다.

R3 과결정    미지수보다 **독립 관측**이 많으면 그것은 피팅이 아니라 측정이다.
             ⚠ 경계가 중요: 독립 관측 ≤ 미지수면 피팅이고, 그 순간 시뮬레이터가
             아니라 회귀식이 된다. 상관계수가 높은 두 미지수는 독립이 아니다.

R4 제1원리   계산으로 얻는다(전자구조·분자동역학). 문헌이 없어도 가능하지만 비싸다.

R5 차원닫음  차원해석으로 다른 알려진 양에서 유일하게 결정된다.

R6 대응관계  검증된 상관식으로 대체한다. ⚠ 그 상관식 자체에 문헌 근거가 필요하다.

R7 구조적제거 위 전부 불가면 그 항을 **모델에서 뺀다**.
             미지수를 자유 파라미터로 남기는 것이 최악이다 — 조용히 피팅
             손잡이가 되고, 겉보기 성능은 오히려 좋아져 들키지 않는다.

R8 측정명세  "이 값을 이렇게 재 오시오"를 절차가 명시한다.
             이것은 실패가 아니라 **정직한 사양**이다. 새 슬러리 하나를 넣기
             위해 어떤 측정 두 개가 필요한지 말해 주는 것은 제품 기능이다.

판정 순서
────────
R1 → R2 → R3 → R5 → R6 → R4 → R8 → R7
(싼 것부터. R1이 되면 그 값은 영영 필요 없다.)

⚠ 이 모듈에는 물질명이 없다. 미지량의 **역할**만 본다.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional, Sequence, Tuple

__all__ = [
    "Route", "Verdict", "cancellation_test", "route_unknown", "ROUTES",
]


ROUTES: Dict[str, str] = {
    "R1": "소거 — 비/도함수로 다시 써서 절대값을 약분",
    "R2": "부등식 — 한쪽 경계만으로 한쪽 방향 결론",
    "R3": "과결정 식별 — 독립 관측 > 미지수면 측정",
    "R4": "제1원리 계산",
    "R5": "차원 닫음",
    "R6": "검증된 대응관계로 대체",
    "R7": "구조적 제거 — 모델에서 항을 뺀다",
    "R8": "측정 명세 — 무엇을 어떻게 재면 되는지 출력",
}


@dataclass
class Verdict:
    """한 미지량에 대한 판정."""
    name: str
    route: str
    reason: str
    evidence: Dict[str, object] = field(default_factory=dict)
    action: str = ""

    def __repr__(self) -> str:
        return f"Verdict({self.name} → {self.route}: {self.reason})"


# ──────────────────────────────────────────────────────────────
# R1 판정 — 미지량이 실제로 약분되는가를 **수치로** 확인한다
# ──────────────────────────────────────────────────────────────

def cancellation_test(
    predict: Callable[[float], Sequence[float]],
    probe_values: Sequence[float],
    tol: float = 1e-9,
) -> Tuple[bool, Dict[str, object]]:
    """미지량을 크게 흔들어도 **순위**가 그대로인가.

    왜 순위인가: 우리가 약속한 완료 조건이 "경향성이 실제 데이터와 동일"이다.
    절대값이 아니라 순위가 목표라면, 순위를 바꾸지 않는 미지량은
    **알 필요가 없다**. 이것이 가장 값싼 해결이다.

    predict(x) : 미지량을 x로 놓았을 때의 예측값 벡터
    probe_values : 흔들어 볼 값들 (자릿수를 넘나들게 준다)

    반환: (약분되는가, 근거)
    """
    ranks: List[Tuple[float, Tuple[int, ...]]] = []
    raw: List[Tuple[float, List[float]]] = []
    for x in probe_values:
        try:
            y = [float(v) for v in predict(x)]
        except Exception as e:  # noqa: BLE001
            return False, {"error": f"{type(e).__name__}: {e}", "at": x}
        if any(math.isnan(v) for v in y):
            return False, {"error": "예측에 NaN", "at": x}
        order = tuple(sorted(range(len(y)), key=lambda i: y[i]))
        ranks.append((x, order))
        raw.append((x, y))

    base = ranks[0][1]
    same = all(r == base for _, r in ranks)

    # 절대값도 함께 본다 — 순위는 같아도 절대값이 흔들리면 R1은 '순위 한정'
    spread = 0.0
    if len(raw) > 1:
        first = raw[0][1]
        for _, y in raw[1:]:
            for a, b in zip(first, y):
                if a > 0 and b > 0:
                    spread = max(spread, abs(math.log(b / a)))

    # ⚠ 가장 위험한 오판: "약분된다"와 "애초에 쓰이지 않는다"의 혼동.
    #   미지량을 4자릿수 흔들었는데 출력이 **비트 단위로 동일**하면
    #   그것은 소거가 아니라 그 값이 계산 경로에 들어가지도 않았다는 뜻이다.
    #   전자는 해결이지만 후자는 **모델 결함**이다 — 물성을 선언해 놓고
    #   쓰지 않으니 그 물리가 통째로 빠져 있다.
    #   이 둘을 구분하지 못하면 검사기가 거짓 안심을 준다.
    untouched = (spread == 0.0 and len(raw) > 1
                 and all(y == raw[0][1] for _, y in raw[1:]))

    if untouched:
        return False, {
            "순위불변": same,
            "탐침값": list(probe_values),
            "절대값 로그편차": 0.0,
            "미사용": True,
            "판정": ("❌ 소거가 아니라 **미사용** — 값을 자릿수로 흔들어도 출력이 "
                     "완전히 동일하다. 이 물성은 계산 경로에 들어가지 않는다. "
                     "R1로 넘기지 말고 '해당 물리가 모델에 없음'으로 다뤄라."),
        }

    return same, {
        "순위불변": same,
        "탐침값": list(probe_values),
        "절대값 로그편차": round(spread, 6),
        "미사용": False,
        "판정": ("순위에 영향 없음 — 이 값은 몰라도 된다(소거)" if same
                 else "순위를 바꾼다 — 소거 불가"),
    }


# ──────────────────────────────────────────────────────────────
# R3 판정 — 피팅과 측정의 경계
# ──────────────────────────────────────────────────────────────

def identifiability(
    n_unknowns: int,
    n_independent_observations: int,
    max_pairwise_corr: Optional[float] = None,
    corr_limit: float = 0.9,
) -> Tuple[bool, str]:
    """이 미지수들을 데이터로 **식별**할 수 있는가(피팅이 아니라).

    두 조건을 모두 넘어야 한다:
      (1) 독립 관측 수 > 미지수 수   — 과결정이어야 측정이다
      (2) 미지수끼리 강하게 상관되지 않을 것 — 상관되면 개수가 있어도
          방향을 가를 수 없다(동등해가 무한히 생긴다)
    """
    if n_independent_observations <= n_unknowns:
        return False, (f"관측 {n_independent_observations} ≤ 미지수 {n_unknowns} "
                       "— 과결정이 아니다. 맞추면 피팅이다.")
    if max_pairwise_corr is not None and max_pairwise_corr >= corr_limit:
        return False, (f"미지수 상관 {max_pairwise_corr:.3f} ≥ {corr_limit} "
                       "— 개수가 충분해도 방향을 가를 수 없다(동등해).")
    return True, (f"관측 {n_independent_observations} > 미지수 {n_unknowns}, "
                  "상관 허용 범위 — 식별 가능(측정)")


# ──────────────────────────────────────────────────────────────
# 통합 판정
# ──────────────────────────────────────────────────────────────

def route_unknown(
    name: str,
    *,
    cancels: Optional[bool] = None,
    bound_known: Optional[str] = None,
    n_unknowns: int = 1,
    n_observations: int = 0,
    max_corr: Optional[float] = None,
    correspondence: Optional[str] = None,
    measurable_by: Optional[str] = None,
    used_by_terms: int = 1,
) -> Verdict:
    """미지량 하나를 경로에 배정한다.

    싼 순서로 시도하고, 처음 성립하는 경로에서 멈춘다.
    """
    if cancels:
        return Verdict(name, "R1", "순위 출력에서 약분된다",
                       {"확인": "수치 탐침"},
                       "값을 확보할 필요 없음 — 모델식을 비/도함수 형태로 유지하라")

    if bound_known:
        return Verdict(name, "R2", f"경계를 안다: {bound_known}",
                       {"bound": bound_known},
                       "부등식이 허용하는 방향의 결론만 낸다 — 경계값을 본값처럼 쓰지 말 것")

    ok, why = identifiability(n_unknowns, n_observations, max_corr)
    if ok:
        return Verdict(name, "R3", why,
                       {"미지수": n_unknowns, "관측": n_observations,
                        "상관": max_corr},
                       "독립 관측으로 역산한다 — 이것은 측정이며 근거 등급 measured")

    if correspondence:
        return Verdict(name, "R6", f"검증된 대응관계 사용: {correspondence}",
                       {"relation": correspondence},
                       "대응식 자체의 출처를 파라미터 근거로 기록하라")

    if measurable_by:
        return Verdict(name, "R8", f"측정으로 얻는다: {measurable_by}",
                       {"method": measurable_by},
                       "절차의 출력으로 '이 측정이 필요하다'를 명시한다 — 실패가 아니다")

    return Verdict(
        name, "R7",
        f"어떤 경로도 성립하지 않음 (사용 항 {used_by_terms}개)",
        {"used_by_terms": used_by_terms, "식별성": why},
        "이 항을 모델에서 뺀다. 자유 파라미터로 남기면 조용한 피팅 손잡이가 된다.")
