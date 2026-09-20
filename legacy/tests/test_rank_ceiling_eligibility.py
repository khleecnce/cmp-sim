"""C4 적격 필터 + 도달가능성 산술 회귀 — 판정#93.

배경: `tools/rank_ceiling.py`(판정#91)는 held-out ρ의 구조적 상한을 낸다.
그런데 출력이 `tools/completion.py::heldout_by_pack`이 실제로 C4에 세는
데이터셋과 안 세는 것(범위밖·캘리브레이션·비유의)을 구분하지 않아서, 작업자가
yang2023(석영유리 — 팩 재료계 밖)처럼 **C4가 절대 안 세는** 데이터셋의 ρ를
올리려 물리를 건드릴 위험이 있었다. 이 파일은 그 구분과, C4 도달가능성
산술(`--c4-requirement`)을 고정한다.

⚠ 절대값을 고정한다(상대적 성질만 검사하지 않는다) — 이 프로젝트에는 "0보다
크다"류의 상대 검사만으로 통과한 21,600km 버그 전례가 있다.

⚠ 필터를 되돌리면 실제로 FAIL 하는지 수동으로 확인했다: `select_rows`에서
`if not include_ineligible: results = [...]` 줄을 주석 처리하고 이 파일을
돌리면 `test_default_output_excludes_*` 4건이 전부 FAIL한다(yang2023·
carbide2023·mo2026·gong2024가 표에 다시 나타난다) — 판정#93 커밋 메시지에도
이 사실을 적는다.

`backtest.run_all()`은 GW 접촉 모델을 실제로 적분해 데이터셋마다 수 초가
걸린다 — 이 파일 전체가 한 번만 돌리도록 module-scope fixture로 공유한다.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "validation"))

import backtest  # noqa: E402
import tools.completion as completion  # noqa: E402
from tools.rank_ceiling import (  # noqa: E402
    compute_all, compute_uncomputable, select_rows, c4_requirement,
    achievable_rhos, min_significant_rho, c4_eligible,
)


@pytest.fixture(scope="module")
def raw():
    return backtest.run_all()


@pytest.fixture(scope="module")
def all_results(raw):
    return compute_all(raw_results=raw)


@pytest.fixture(scope="module")
def uncomputable(raw):
    return compute_uncomputable(raw_results=raw)


@pytest.fixture(scope="module")
def default_rows(all_results):
    return select_rows(all_results)


def _find(results, dataset):
    for r in results:
        if r.dataset == dataset:
            return r
    raise AssertionError(f"{dataset} not found")


# ═══════════════ 호출자 실측 표의 4건 — 기본 출력에서 제외 + 사유 ═══════════════

def test_yang2023_excluded_default_reason_out_of_scope(all_results, default_rows):
    r = _find(all_results, "yang2023_quartz_ceria_L25")
    assert r.in_scope is False
    assert r.eligible is False
    assert r.exclusion_reason == "범위밖"
    assert r.dataset not in {x.dataset for x in default_rows}


def test_carbide2023_excluded_default_reason_out_of_scope(all_results, default_rows):
    r = _find(all_results, "carbide2023_slurry_composition_L9")
    assert r.in_scope is False
    assert r.eligible is False
    assert r.exclusion_reason == "범위밖"
    assert r.dataset not in {x.dataset for x in default_rows}


def test_mo2026_excluded_default_reason_out_of_scope(all_results, default_rows):
    r = _find(all_results, "mo2026_double_sided_L16")
    assert r.in_scope is False
    assert r.eligible is False
    assert r.exclusion_reason == "범위밖"
    assert r.dataset not in {x.dataset for x in default_rows}


def test_gong2024_excluded_default_reason_calibration(all_results, default_rows):
    r = _find(all_results, "gong2024_4hsic_alumina_kmno4_L25")
    assert r.in_scope is True                 # 범위는 안이다 — 캘리브레이션이라 빠지는 것
    assert r.used_for_calibration is True
    assert r.eligible is False
    assert r.exclusion_reason == "캘리브레이션"
    assert r.dataset not in {x.dataset for x in default_rows}


# ═══════════════ 필터 소스 동일성 — completion.heldout_by_pack과 반드시 같아야 함 ═══════════════

def test_c4_eligible_is_imported_not_reimplemented():
    """rank_ceiling이 자기 판정 함수를 새로 만들지 않고 completion.c4_eligible을
    그대로 쓰는지 — 객체 동일성으로 고정한다(판정#58: 조건을 베끼면 조용히
    갈라진다)."""
    assert c4_eligible is completion.c4_eligible


def test_eligible_flag_matches_heldout_by_pack_membership(all_results):
    """default_rows의 적격 판정이 heldout_by_pack()이 실제로 세는 집합과
    정확히 일치하는지 팩별로 대조한다."""
    ho = completion.heldout_by_pack()
    ds_pack = completion.dataset_pack_map()
    eligible_datasets = {r.dataset for r in all_results if r.eligible}
    for pack, info in ho.items():
        counted_in_pack = {d for d in eligible_datasets if ds_pack.get(d) == pack}
        assert len(counted_in_pack) == info["n_sig"], (
            f"{pack}: rank_ceiling 적격 {len(counted_in_pack)}건 != "
            f"heldout_by_pack n_sig {info['n_sig']}건")


def test_reverting_eligibility_filter_would_include_ineligible_rows(all_results):
    """필터를 껐을 때(=include_ineligible=True) 위 4건이 실제로 다시 나타나는지
    확인한다 — select_rows의 필터 인자가 실제로 뭔가를 걸러낸다는 것의 직접
    증거(상대적 성질만 보는 검사가 아니다)."""
    filtered = {r.dataset for r in select_rows(all_results)}
    # ⚠ 두 축은 독립이다. `carbide2023` 는 상한이 **정확히 1.0** 이라
    #   적격 필터를 꺼도 `show_all` 없이는 상한 필터에 걸려 안 나온다.
    #   (2026-09-20 호출자 정정: 원래 이 테스트는 include_ineligible 하나만 켜고
    #    네 건 전부를 기대해 FAIL 했다 — 도구가 아니라 기대값이 틀렸다.
    #    실측 확인: carbide2023 ρ_ceiling=+1.0000.)
    unfiltered = {r.dataset for r in select_rows(all_results,
                                                  include_ineligible=True,
                                                  show_all=True)}
    ineligible_only = {r.dataset for r in select_rows(all_results,
                                                       include_ineligible=True)}
    for ds in ("yang2023_quartz_ceria_L25", "carbide2023_slurry_composition_L9",
               "mo2026_double_sided_L16", "gong2024_4hsic_alumina_kmno4_L25"):
        assert ds not in filtered
        assert ds in unfiltered
    # 상한<1.0 인 셋은 적격 필터만 꺼도 나타나야 한다(상한 필터에 안 걸리므로).
    for ds in ("yang2023_quartz_ceria_L25", "mo2026_double_sided_L16",
               "gong2024_4hsic_alumina_kmno4_L25"):
        assert ds in ineligible_only
    # 상한==1.0 인 것은 안 나타나야 한다 — 두 축이 독립이라는 직접 증거.
    assert "carbide2023_slurry_composition_L9" not in ineligible_only


# ═══════════════ --all과 --include-ineligible은 독립 축 ═══════════════

def test_all_flag_and_include_ineligible_are_independent_axes(all_results):
    base = {r.dataset for r in select_rows(all_results)}
    only_all = {r.dataset for r in select_rows(all_results, show_all=True)}
    only_ineligible = {r.dataset for r in select_rows(all_results, include_ineligible=True)}
    both = {r.dataset for r in select_rows(all_results, show_all=True,
                                            include_ineligible=True)}
    # --all은 상한==1.0 인 적격 데이터셋을 추가한다(예: us9200180b2_cu_h2o2_series) —
    # 범위밖/캘리브레이션 데이터셋은 여전히 포함하지 않는다.
    assert "us9200180b2_cu_h2o2_series" in only_all
    assert "yang2023_quartz_ceria_L25" not in only_all
    # --include-ineligible은 범위밖 데이터셋을 상한<1.0 조건 안에서 추가한다.
    assert "us9200180b2_cu_benzenesulfonic_series" in only_ineligible
    assert base < both
    assert only_all <= both and only_ineligible <= both


def test_default_empty_pack_still_prints_breakdown_info(all_results, uncomputable):
    """cu_alkaline_benzenesulfonic 팩은 기본 필터(상한<1·적격)로는 0건이지만
    그렇다고 '남은 후보가 없다'는 뜻이 아니다 — 걸러진 내역이 항상 계산돼야
    한다(과잉 필터 방지 장치)."""
    pack = "cu_alkaline_benzenesulfonic"
    shown = select_rows(all_results, pack=pack)
    assert shown == []
    pool = [r for r in all_results if r.pack == pack]
    assert len(pool) > 0, "이 회귀의 전제(해당 팩 데이터셋 존재)가 깨졌다"
    reasons = {r.dataset: r.exclusion_reason for r in pool}
    assert reasons.get("us9200180b2_cu_benzenesulfonic_series") == "범위밖"
    assert reasons.get("us9200180b2_cu_ph_alkaline_sweep") == "캘리브레이션"
    # 적격인데 상한==1.0이라 기본 표에서 숨겨진 것도 있다 — '적격 후보 0건'이 아니다.
    hidden_at_ceiling_one = [r for r in pool if r.eligible and r.rho_ceiling >= 1.0 - 1e-9]
    assert len(hidden_at_ceiling_one) >= 1


# ═══════════════ 계산불가(n=2, ρ=nan) — 비유의와 다른 사유 ═══════════════

def test_n2_dataset_classified_as_uncomputable_not_nonsignificant(all_results, uncomputable):
    dataset = "us9200180b2_cu_abrasive_series"
    assert dataset not in {r.dataset for r in all_results}, (
        "n=2 데이터셋이 compute_all()에 들어갔다 — ρ=nan인데 행이 생기면 안 된다")
    entry = next((u for u in uncomputable if u["dataset"] == dataset), None)
    assert entry is not None
    assert entry["n"] == 2
    assert "계산불가" in entry["reason"]
    assert "비유의" not in entry["reason"]


# ═══════════════ C4 도달가능성 산술 (cu_h2o2_bta) — 절대값 고정 ═══════════════

def test_cu_h2o2_bta_current_state_matches_manual_tally(all_results):
    """호출자 실측 표(6건, 그중 유의 1건)와 대조한다."""
    ds_pack = completion.dataset_pack_map()
    # ⚠ 호출자 실측 표는 **held-out 후보**(범위 안 + 비캘리브레이션)만 센 것이다.
    #   `compute_all()` 은 팩의 모든 데이터셋을 돌려주므로 캘리브레이션용
    #   (us20080090500a1·jani2025_cu_h2o2_acidic_chelator)과 범위 밖
    #   (lee2021_cu_nicotinic_inhibitor)이 함께 들어온다.
    #   (2026-09-20 호출자 정정: 원래 이 테스트는 그 셋까지 같은 집합으로 기대해
    #    FAIL 했다 — 도구가 아니라 기대값의 범위가 틀렸다.)
    pack_rows = [r for r in all_results
                 if ds_pack.get(r.dataset) == "cu_h2o2_bta"
                 and r.in_scope and not r.used_for_calibration]
    by_name = {r.dataset: r for r in pack_rows}
    expected_rho = {
        "tw202115224a_cu_abrasive_size_pressure": (18, 0.7175, True),
        "us8501625b2_cu_h2o2_pressure_series": (6, 0.6571, False),
        "jani2025_cu_rsm_composition_heldout": (13, 0.3022, False),
        "hong2007_cu_ads_bta_polish_rate": (5, 0.4472, False),
        "miranda2004_cu_ph_h2o2_2x2": (4, 0.0000, False),
        "ihnfeldt2008_cu_alumina_ph_oxidizer_chelator": (7, -0.1429, False),
    }
    assert set(by_name) == set(expected_rho)
    for name, (n, rho, sig) in expected_rho.items():
        r = by_name[name]
        assert r.n == n
        assert r.actual_rho == pytest.approx(rho, abs=5e-4)
        assert r.significant == sig
    assert sum(1 for r in pack_rows if r.eligible) == 1


def test_c4_requirement_k1_absolute_arithmetic(all_results):
    """유의 held-out 1건(0.71745) + 새 1건 x, 평균>=0.85 이려면
    x >= 2*0.85-0.71745 = 0.98255. 절대값을 rel=1e-3으로 고정한다."""
    info = c4_requirement("cu_h2o2_bta")
    assert info["n_sig"] == 1
    assert info["current_mean"] == pytest.approx(0.71745, rel=1e-3)
    req1 = info["requirements"][1]["req_sum"]
    assert req1 == pytest.approx(0.98255, rel=1e-3)


def test_c4_requirement_k2_absolute_arithmetic(all_results):
    """새 2건 x1+x2, 평균>=0.85 이려면 합 >= 3*0.85-0.71745 = 1.83255."""
    info = c4_requirement("cu_h2o2_bta")
    req2 = info["requirements"][2]["req_sum"]
    assert req2 == pytest.approx(1.83255, rel=1e-3)
    assert info["requirements"][2]["req_mean_new"] == pytest.approx(0.916275, rel=1e-3)


def test_c4_requirement_flags_structurally_impossible_candidates(all_results):
    """hong2007·miranda2004는 구조적 상한(0.6708/0.0)이 k=1 요구치(0.98255)에
    턱없이 못 미치거나 상한 자체가 영원히 비유의라 '원리적으로 불가능'으로
    표시돼야 한다."""
    info = c4_requirement("cu_h2o2_bta")
    cands = {c["dataset"]: c for c in info["requirements"][1]["candidates"]}
    assert cands["hong2007_cu_ads_bta_polish_rate"]["possible_in_principle"] is False
    assert cands["miranda2004_cu_ph_h2o2_2x2"]["possible_in_principle"] is False
    # ceiling==1.0인 셋은 (완벽한 순위 일치를 요구하더라도) 원리적으로는 가능
    for name in ("us8501625b2_cu_h2o2_pressure_series",
                 "jani2025_cu_rsm_composition_heldout",
                 "ihnfeldt2008_cu_alumina_ph_oxidizer_chelator"):
        assert cands[name]["possible_in_principle"] is True


def test_n6_achievable_rhos_matches_worked_example():
    """호출자가 제시한 n=6 이산값 예시(1.000, 0.943, 0.886, 0.829)를 그대로
    확인한다."""
    top4 = achievable_rhos(6)[:4]
    assert top4 == pytest.approx([1.0, 0.942857143, 0.885714286, 0.828571429], abs=1e-6)


def test_min_significant_rho_n6_matches_exact_permutation_search():
    """n=6의 최소 유의 ρ는 이산 후보 중 처음으로 p<0.05를 만족하는 값이다."""
    r = min_significant_rho(6)
    assert r is not None
    assert r["exact"] is True
    assert r["min_rho"] == pytest.approx(0.828571429, abs=1e-6)
    assert r["p"] < 0.05
    # 바로 아래 값(0.885714286 다음의 0.771428571)은 비유의여야 한다(경계 확인).
    from tools.rank_ceiling import _exact_p_value
    p_below = _exact_p_value(0.771428571, 6)
    assert p_below >= 0.05


def test_min_significant_rho_matches_backtest_perm_p_value_exact():
    """자체 이산분포 계산이 `backtest.perm_p_value`(exact 분기)와 같은 값을
    내는지 n<=8에서 직접 대조한다 — 두 계산이 갈리면 안 된다."""
    from tools.rank_ceiling import _exact_p_value
    for n in (4, 5, 6, 7):
        for rho in achievable_rhos(n)[:3]:
            mine = _exact_p_value(rho, n)
            theirs = backtest.perm_p_value(rho, n)
            assert mine == pytest.approx(theirs, abs=1e-9), (n, rho, mine, theirs)
