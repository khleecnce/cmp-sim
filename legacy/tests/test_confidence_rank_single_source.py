"""근거 등급 서열이 **모듈 두 곳에서 갈라지지 않음**을 잠그는 테스트.

2026-09-16 실제 사고: tools/completion.py 가 자기 CONF_RANK 표를 손으로 들고
있었고 거기에 "measured" 가 빠져 있었다. `.get(c, 0)` 이므로 예외가 나지 않고
**최상급에 가까운 실측 등급이 0점(=unverified 취급)** 으로 읽혔다.

증상이 조용했던 점이 핵심이다:
  · blockers.py 가 sic_ceria_h2o2 의 measured 키(Wang DOE 실측인 oxidizer_wt_pct·
    slurry_ph)를 "막는 키"로 지목했다
  · 다음 회차는 **이미 실측으로 확보된 값의 문헌을 다시 찾으러** 갔다
  · 진짜 약한 고리(oxidizer_langmuir_K, estimated, 부트스트랩 CI 0.32~2.70)는
    목록에 나오지도 않았다

그래서 사람의 주의로 막지 않고 기계로 막는다.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sim.factors import _CONF_ORDER, _worst_conf          # noqa: E402
from tools.completion import CONF_RANK, MIN_CONF          # noqa: E402


def test_every_factors_grade_has_a_rank():
    """factors.py 가 낼 수 있는 모든 등급은 랭크 표에 있어야 한다.

    빠진 등급은 `.get(c, 0)` 때문에 예외 없이 0점이 되어, 최상급 값이
    최하급으로 조용히 오판된다.
    """
    missing = [c for c in _CONF_ORDER if c not in CONF_RANK]
    assert not missing, (
        f"factors.py 의 등급 {missing} 가 completion.CONF_RANK 에 없다 — "
        "`.get(c, 0)` 이 이 등급을 unverified 로 취급한다"
    )


def test_rank_order_matches_factors_order():
    """랭크의 대소 관계가 factors.py 서열과 같은 방향이어야 한다."""
    ranks = [CONF_RANK[c] for c in _CONF_ORDER]
    assert ranks == sorted(ranks, reverse=True), (
        f"서열 불일치: {list(zip(_CONF_ORDER, ranks))} — "
        "factors.py 는 앞이 높은 순서인데 랭크가 그렇지 않다"
    )
    assert len(set(ranks)) == len(ranks), "등급 사이에 동점이 있으면 비교가 무의미하다"


def test_measured_passes_the_completion_gate():
    """실측(measured)은 완성 격자 최소 등급(literature)을 **통과해야** 한다.

    이 단정이 실패하면 팩이 실측값을 선언해도 칸이 오르지 않는다 —
    "문헌을 아무리 확보해도 진도가 안 오르는" 구조적 하한과 같은 병이다.
    """
    assert "measured" in _CONF_ORDER
    assert CONF_RANK["measured"] >= CONF_RANK[MIN_CONF], (
        "measured 가 격자 최소 등급에 미달한다 — 실측값이 미달로 취급된다"
    )
    # 서열상 measured 는 literature 보다 강해야 한다(실측 > 문헌인용)
    assert CONF_RANK["measured"] > CONF_RANK["literature"]


def test_worst_conf_and_rank_agree_on_which_is_weaker():
    """두 판정 경로(_worst_conf 와 CONF_RANK)가 같은 답을 내야 한다.

    _worst_conf 는 "가장 약한 고리"를 고르고, CONF_RANK 는 "게이트 통과"를
    판정한다. 둘이 다른 서열을 쓰면 팩터 등급과 진단이 어긋난다.
    """
    for a in _CONF_ORDER:
        for b in _CONF_ORDER:
            worst = _worst_conf(a, b)
            expect = a if CONF_RANK[a] <= CONF_RANK[b] else b
            assert worst == expect, (
                f"_worst_conf({a},{b}) = {worst} 인데 랭크로는 {expect} 가 약하다"
            )
