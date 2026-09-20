"""회귀 — 차원(D) 검사의 중위 무차원 규칙 과잉적용 (EVIDENCE-RULES 판정#96).

배경: `check_dimensions()` 가 `DIMLESS_SUFFIX` 전체를 **중위**로도 적용해
(`any(f"{s}_" in key ...)`), 이름에 `_ph_` 가 들어가지만 그 자신은 무차원이
아닌 키(`cu_ph_acid_k` 단위 1/pH, `sic_kmno4_ph_floor_hi_wt` 단위 wt%)까지
"무차원이어야 하는데 단위가 있다"로 신고했다 — 실측 8건 전부 오탐.
중위 적용의 본래 의도는 `promoter_exponent_m` 처럼 지수를 가리키는 한 글자가
뒤에 붙는 경우 하나였으므로, 중위 표지를 `DIMLESS_INFIX`(지수만)로 좁혔다.
knowledge/cmp/model-hygiene-dimension-infix-overreach.md 참조.
"""
import sys
import warnings
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
warnings.filterwarnings("ignore")

from tools.model_hygiene import (  # noqa: E402
    DIMLESS_SUFFIX, DIMLESS_INFIX, check_dimensions,
)


def _dim_titles():
    return [i.title for i in check_dimensions()]


def test_no_false_dimensionless_flags_for_ph_axis_params():
    """pH 축 파라미터는 이름에 _ph_ 가 있어도 그 자신은 무차원이 아니다.

    감쇠계수는 1/pH, 앵커 농도는 wt% 가 정당한 단위다 — 이것들이
    "무차원이어야 하는데" 로 신고되면 오탐이다.
    """
    offenders = [t for t in _dim_titles()
                 if "무차원이어야" in t
                 and any(k in t for k in ("cu_ph_acid_k", "cu_ph_alkaline_k",
                                          "w_ph_acid_k", "sic_kmno4_ph_acid_k",
                                          "sic_kmno4_ph_floor_hi_wt",
                                          "sic_kmno4_ph_floor_lo_wt"))]
    assert not offenders, (
        "pH 축 파라미터가 여전히 무차원 위반으로 오탐된다: %r" % offenders)


def test_infix_rule_is_narrower_than_suffix_rule():
    """중위 표지는 접미 표지의 진부분집합이어야 한다 — 되돌리면 FAIL.

    DIMLESS_INFIX 를 DIMLESS_SUFFIX 로 되돌리면 이 assert 가 깨진다.
    """
    assert set(DIMLESS_INFIX) < set(DIMLESS_SUFFIX)
    assert "_ph" not in DIMLESS_INFIX, (
        "_ph 를 중위 표지로 되돌리면 1/pH·wt% 선언이 다시 전부 오탐된다")


def test_exponent_infix_still_recognised():
    """수축이 본래 의도(지수 한 글자 접미)를 깨지 않았는지 — 사각지대 방지."""
    key = "promoter_exponent_m"
    recognised = key.endswith(DIMLESS_SUFFIX) or any(
        ("%s_" % s) in key for s in DIMLESS_INFIX)
    assert recognised, (
        "promoter_exponent_m 이 무차원으로 인정되지 않는다 — 중위 규칙을 "
        "너무 좁혔다(지수는 이름 어디에 있든 무차원이다)")


def test_narrowing_did_not_create_silent_passes():
    """면제를 잃은 키들이 '검사 안 함'으로 새지 않고 실제로 통과해야 한다.

    수축의 위험은 반대 방향 오류다 — 면제가 풀린 키가 진짜 차원 결함인데
    아무도 안 보는 것. 차원 검사 결과에 이 키들에 대한 **어떤** 신고도
    없다면, 그것은 단위 선언이 정당하거나 note 로 예외가 문서화됐기
    때문이어야 한다(둘 다 데이터 쪽 근거다).
    """
    titles = _dim_titles()
    for key in ("cu_ph_acid_k", "sic_kmno4_ph_floor_hi_wt"):
        assert not any(key in t and "단위가 없음" in t for t in titles), (
            "%s 가 '단위 없음'으로 샜다" % key)
