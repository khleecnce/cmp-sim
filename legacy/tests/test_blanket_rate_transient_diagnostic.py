"""blanket_rate_transfer.py 엔진 등록 회귀 — 블랭킷 Cu 순간속도 a1 대비 평균 rate 과소평가 진단.

근거: sim/tier2_physics/blanket_rate_transfer.py::blanket_rate_average(원본 무수정,
eq.3.52), knowledge/cmp/npw-ptw-transfer-rules-quantitative.md §3·§6 verify (B)
(Tugbawa 2002, MIT EECS PhD thesis, dspace.mit.edu/handle/1721.1/8083, 표 3.3).

이 모듈의 docstring이 적은 미등록 사유("Recipe에 시간축 스키마가 없다")는 **역방향**
fit_blanket_rate에만 해당한다 — 순방향 eq.3.52는 rr.time_s 하나만 있으면 계산되므로
그 경계 안에서만 등록한다. fit_blanket_rate는 호출 금지(ast로 기계 고정).

절대값을 못 박는다 — 상대적 성질만 보는 테스트는 과거 21,600km 오류를 통과시킨 전례가
있다(다른 diagnostic 테스트들의 공통 주석 참조). 표 3.3 실험 1(5 psi, 63 rpm)의
r_avg(60s)/a1 = 0.740557(±)을 직접 계산해 못 박는다.
"""
import ast
import inspect
import math

import numpy as np
import pytest

import sim.engine as E
from sim.engine import Recipe, simulate, _blanket_rate_transient_diagnostic
from sim.params import available_packs
import blanket_rate_transfer as BRT

_ALL_PACKS = [p for p in available_packs() if p != "base"]

# (Tugbawa 2002) 표 3.3, knowledge/cmp/npw-ptw-transfer-rules-quantitative.md §3/§6
_TABLE_3_3 = {
    1: (249.5, 3986.6, 16.4),
    2: (120.0, 924.0, 9.71),
    3: (159.0, 1176.0, 7.7),
    4: (239.6, 1424.0, 6.3),
}


def _r_avg(t, a1, a2, tau):
    AR = a1 * t + a2 * (math.exp(-t / tau) - 1)
    return AR / t


def _cu_packs():
    """film == 'cu' 인 팩을 **전부** 돌려준다.

    ⚠ 처음엔 첫 번째 하나만 골랐는데(`_cu_pack`), 2026-09-19 에 알칼리 Cu 계가
    별도 팩(cu_alkaline_benzenesulfonic)으로 분리되면서 Cu 팩이 둘이 됐다.
    그러자 "Cu 아닌 팩" 목록에 나머지 Cu 팩이 섞여 들어가 계약 테스트가 깨졌다.
    팩이 늘어날 때마다 깨지지 않도록 **개수를 가정하지 말고 전부 센다.**
    """
    out = []
    for pack in _ALL_PACKS:
        rr = Recipe(pack=pack, time_s=60).resolve()
        if rr.film == "cu":
            out.append(pack)
    assert out, "Cu 팩이 하나도 없다 — 테스트 전제 깨짐"
    return out


_CU_PACKS = _cu_packs()
_CU_PACK = _CU_PACKS[0]          # 단일 팩으로 충분한 케이스의 대표


def _git_diff_clean_or_skip(paths, label):
    """원본 tier2_physics 모듈이 0바이트도 수정되지 않았는지 워킹트리에서 검사한다."""
    import subprocess
    root = E.__file__.rsplit("/sim/", 1)[0]
    inside = subprocess.run(["git", "rev-parse", "--is-inside-work-tree"],
                            cwd=root, capture_output=True, text=True)
    if inside.returncode != 0 or inside.stdout.strip() != "true":
        pytest.skip("git 워킹트리가 아님(pre-push archive 등) — 원본 무수정 검사 스킵")
    result = subprocess.run(["git", "diff", "--quiet", "--"] + list(paths), cwd=root)
    assert result.returncode == 0, f"{label}에 diff가 있다 — 원본 무수정 위반"


def test_original_blanket_rate_transfer_module_unmodified():
    _git_diff_clean_or_skip(
        ["sim/tier2_physics/blanket_rate_transfer.py"], "blanket_rate_transfer.py")


def test_diagnostic_does_not_change_mrr():
    r = Recipe(pack=_CU_PACK, time_s=60)
    res_ref = simulate(r)

    orig = E._blanket_rate_transient_diagnostic
    E._blanket_rate_transient_diagnostic = lambda rr: {
        "blanket_transient_avg_to_inst_ratio_range": (0.0, 0.0),
        "blanket_transient_underestimate_pct_range": (999.0, 999.0),
        "blanket_transient_note": "test-probe",
    }
    try:
        res_forced = simulate(r)
    finally:
        E._blanket_rate_transient_diagnostic = orig

    assert np.array_equal(res_ref.mrr_nm_per_min, res_forced.mrr_nm_per_min)
    assert np.array_equal(res_ref.removed_nm, res_forced.removed_nm)
    assert res_forced.blanket_transient_underestimate_pct_range == (999.0, 999.0)


def test_none_when_film_not_cu():
    non_cu_packs = [p for p in _ALL_PACKS if p not in _CU_PACKS]
    assert non_cu_packs, "Cu 아닌 팩이 없다 — 테스트 전제 깨짐"
    for pack in non_cu_packs:
        rr = Recipe(pack=pack, time_s=60).resolve()
        assert rr.film != "cu"
        out = _blanket_rate_transient_diagnostic(rr)
        assert out["blanket_transient_avg_to_inst_ratio_range"] is None, pack
        assert out["blanket_transient_underestimate_pct_range"] is None, pack
        assert out["blanket_transient_note"] is not None, pack
        assert "Cu 계 아님" in out["blanket_transient_note"]


def test_none_when_time_s_not_positive():
    rr = Recipe(pack=_CU_PACK, time_s=0).resolve()
    out = _blanket_rate_transient_diagnostic(rr)
    assert out["blanket_transient_avg_to_inst_ratio_range"] is None
    assert out["blanket_transient_underestimate_pct_range"] is None
    assert out["blanket_transient_note"] is not None
    assert "<= 0" in out["blanket_transient_note"] or "<=0" in out["blanket_transient_note"]


def test_experiment1_r_avg_60s_over_a1_absolute_value():
    # 표 3.3 실험1(5psi, 63rpm) a1=249.5, a2=3986.6, tau=16.4 — 절대값을 못 박는다.
    a1, a2, tau = _TABLE_3_3[1]
    expected_ratio = _r_avg(60.0, a1, a2, tau) / a1
    assert expected_ratio == pytest.approx(0.7405568116145871, rel=1e-9)
    assert BRT.blanket_rate_average(60.0, a1, a2, tau) / a1 == pytest.approx(
        expected_ratio, rel=1e-12)

    rr = Recipe(pack=_CU_PACK, time_s=60).resolve()
    out = _blanket_rate_transient_diagnostic(rr)
    ratio_lo, ratio_hi = out["blanket_transient_avg_to_inst_ratio_range"]
    # 실험1이 4실험 중 가장 큰 과소평가(26%, 즉 가장 작은 ratio)를 낸다 — §6 verify (B) 정량표
    assert ratio_lo == pytest.approx(expected_ratio, rel=1e-9)
    pct_lo, pct_hi = out["blanket_transient_underestimate_pct_range"]
    assert pct_hi == pytest.approx((1.0 - expected_ratio) * 100.0, rel=1e-9)


def test_range_matches_all_four_experiments_min_max_not_averaged():
    rr = Recipe(pack=_CU_PACK, time_s=60).resolve()
    out = _blanket_rate_transient_diagnostic(rr)
    ratios = [_r_avg(60.0, a1, a2, tau) / a1 for a1, a2, tau in _TABLE_3_3.values()]
    ratio_lo, ratio_hi = out["blanket_transient_avg_to_inst_ratio_range"]
    assert ratio_lo == pytest.approx(min(ratios), rel=1e-9)
    assert ratio_hi == pytest.approx(max(ratios), rel=1e-9)
    # 대표값(평균)을 내지 않는다 — 4실험 개별 ratio 중 범위 밖의 값이 없어야 함
    assert all(ratio_lo - 1e-9 <= r <= ratio_hi + 1e-9 for r in ratios)


def test_note_always_mentions_operating_point_mismatch_when_computed():
    rr = Recipe(pack=_CU_PACK, time_s=60).resolve()
    out = _blanket_rate_transient_diagnostic(rr)
    assert out["blanket_transient_note"] is not None
    assert "오더 참고용" in out["blanket_transient_note"]
    assert "운전점" in out["blanket_transient_note"]


def test_note_never_empty_across_all_packs_and_time_values():
    for pack in _ALL_PACKS:
        for t in (0.0, 60.0):
            rr = Recipe(pack=pack, time_s=t).resolve()
            out = _blanket_rate_transient_diagnostic(rr)
            assert out["blanket_transient_note"], (pack, t)


def test_forbidden_fit_blanket_rate_never_called_in_engine():
    # fit_blanket_rate는 실측 (t, 제거량) 시계열이 Recipe/팩 어디에도 없어 호출 금지.
    tree = ast.parse(inspect.getsource(E))
    called = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            fn = node.func
            if isinstance(fn, ast.Name):
                called.add(fn.id)
            elif isinstance(fn, ast.Attribute):
                called.add(fn.attr)
    assert "fit_blanket_rate" not in called, (
        "engine.py가 fit_blanket_rate를 호출한다 — 실측 시계열 없이 역추정을 시도한다")


def test_all_packs_full_simulate_wires_the_field():
    for pack in _ALL_PACKS:
        res = simulate(Recipe(pack=pack, time_s=60))
        if pack in _CU_PACKS:
            assert res.blanket_transient_avg_to_inst_ratio_range is not None, pack
            assert res.blanket_transient_underestimate_pct_range is not None, pack
        else:
            assert res.blanket_transient_avg_to_inst_ratio_range is None, pack
            assert res.blanket_transient_underestimate_pct_range is None, pack
        assert res.blanket_transient_note is not None, pack
