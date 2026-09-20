"""레거시 산화제 형상 파라미터(oxidizer_peak_wt_pct·oxidizer_curve_n)가
현재 활성 팩에서 **완전히 비활성(dead)** 임을 잠근다.

배경 (2026-09-15 Max워커 실측):
`sim/chemistry.py::_oxidizer_term` 은 if-체인이다 —
  ① oxidizer_langmuir_K      (w_fe_oxidizer 보유)
  ② oxidizer_passivation_K   (cu_h2o2_bta 보유)
  ③ 레거시 Kaufman 단봉(oxidizer_peak_wt_pct + oxidizer_curve_n)
①·②가 먼저 return 하므로, 이 둘을 가진 팩에서 ③은 **도달 불가**하다.
그런데 두 팩 모두 여전히 peak/curve_n 을 YAML에 들고 있어, 마치 살아있는
파라미터처럼 보인다 — 실제로 백로그에 "정점 위 농도 실측 1점을 찾아
(n, C_peak) 축퇴를 깨라"는 항목이 남아 있었다. 그 탐색은 **결과가 나와도
모델 출력을 1비트도 바꾸지 못한다**(판정#19가 Langmuir로 대체했기 때문).

이 테스트는 그 사실을 기계로 고정해, 같은 탐색이 다시 배차되는 것을 막는다.
③ 경로 자체는 제거하지 않는다 — 다른 팩이 Langmuir 계수를 못 얻었을 때
쓰는 하위호환 경로로 살아 있다(sim/chemistry.py:110 독스트링).
"""
import warnings

import pytest

from sim.chemistry import _oxidizer_term
from sim.params import load_pack, Param

warnings.filterwarnings("ignore")

# 축퇴 노트(knowledge/cmp/chi-oxidizer-curve-exponent-identifiability.md)가
# "전부 잔차 0으로 관측을 재현한다"고 적은 (n, C_peak) 조합들 + 극단값.
SHAPES = [(6.0, 3.0), (22.1, 0.5), (41.1, 2.0), (83.0, 6.0), (1.0, 1.0)]
CONCS = (0.5, 1.0, 3.0, 5.0)


def _set(pk, key, val):
    pk.params[key] = Param(key=key, value=val, source="test-probe",
                           confidence="estimated")
    return pk


def _curve(pack_name, peak, n):
    out = []
    for c in CONCS:
        pk = load_pack(pack_name)
        _set(pk, "oxidizer_peak_wt_pct", peak)
        _set(pk, "oxidizer_curve_n", n)
        _set(pk, "oxidizer_wt_pct", c)
        out.append(_oxidizer_term(pk, []))
    return out


@pytest.mark.parametrize("pack_name,active_key", [
    ("w_fe_oxidizer", "oxidizer_langmuir_K"),
    ("cu_h2o2_bta", "oxidizer_passivation_K"),
])
def test_legacy_shape_params_are_inert(pack_name, active_key):
    """peak 를 1.0 → 83.0 (83배) 로 흔들어도 산화제 항이 비트 단위로 불변."""
    assert load_pack(pack_name).has(active_key), (
        f"{pack_name} 가 {active_key} 를 잃으면 레거시 경로가 되살아난다 — "
        "이 테스트의 전제가 깨진 것이므로 백로그 판정을 재검토하라"
    )
    baseline = _curve(pack_name, *SHAPES[0])
    assert all(v is not None for v in baseline)
    for peak, n in SHAPES[1:]:
        assert _curve(pack_name, peak, n) == baseline, (
            f"{pack_name}: (peak={peak}, n={n}) 에서 출력이 달라졌다 — "
            "레거시 형상 파라미터가 더 이상 dead 가 아니다"
        )


def test_legacy_path_still_works_for_packs_without_langmuir():
    """③ 경로를 지운 게 아님을 확인 — Langmuir 계수를 제거하면 되살아나고,
    그때는 peak 가 실제로 출력을 바꾼다(하위호환 보존)."""
    def curve_without_langmuir(peak):
        out = []
        for c in CONCS:
            pk = load_pack("w_fe_oxidizer")
            pk.params.pop("oxidizer_langmuir_K", None)
            _set(pk, "oxidizer_peak_wt_pct", peak)
            _set(pk, "oxidizer_curve_n", 2.0)
            _set(pk, "oxidizer_wt_pct", c)
            out.append(_oxidizer_term(pk, []))
        return out

    a, b = curve_without_langmuir(3.0), curve_without_langmuir(30.0)
    assert all(v is not None for v in a + b)
    assert a != b, "레거시 경로가 살아있다면 peak 변화가 출력을 바꿔야 한다"
