"""tools/blockers.py의 파라미터 병목 진단이 다단계 팩 상속을 올바르게 따라가는지 검증.

배경(2026-09-13 발견·수정): sic_ceria_h2o2 → sti_ceria → oxide_silica → base로
이어지는 다단계 상속 체인에서, 기존 `_pack_params()`는 자기 파일 + base.yaml만
봐서 중간 팩(sti_ceria/oxide_silica)에만 정의된 키(abrasive_wt_pct 등)를
못 찾고 confidence를 "unverified"로 오판했다. 이 오판은 blockers.py 출력에서
cond_sweep_cpm(5칸)·abrasive_wt_pct(2칸) 등 실재하지 않는 병목을 만들어
COMPLETION.md 작업 우선순위 판단을 오도할 뻔했다.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from tools.blockers import _pack_params  # noqa: E402
from sim.params import load_pack  # noqa: E402


def test_multilevel_inheritance_resolves_ancestor_only_keys():
    """sic_ceria_h2o2는 자기 YAML에 abrasive_wt_pct가 없고 sti_ceria(조부모뻘인
    oxide_silica)에서 상속한다 — _pack_params가 이 키를 찾아야 한다."""
    params = _pack_params("sic_ceria_h2o2")
    assert "abrasive_wt_pct" in params, (
        "다단계 상속(sic_ceria_h2o2 -> sti_ceria -> oxide_silica)을 못 따라가 "
        "조상 팩 전용 키를 놓쳤다"
    )
    # sim.params.load_pack이 실제로 계산하는 confidence와 일치해야 한다
    # (진단 도구가 엔진의 실제 판단과 다른 값을 보고하면 무의미하다).
    live_conf = load_pack("sic_ceria_h2o2").param("abrasive_wt_pct").confidence
    assert params["abrasive_wt_pct"].get("confidence") == live_conf


def test_multilevel_inheritance_sti_ceria_dispersant_type():
    """sti_ceria도 같은 체인(oxide_silica 경유)에서 dispersant_type을 상속한다."""
    params = _pack_params("sti_ceria")
    assert "dispersant_type" in params
    live_conf = load_pack("sti_ceria").param("dispersant_type").confidence
    assert params["dispersant_type"].get("confidence") == live_conf


def test_driver_key_with_diagnostic_suffix_is_normalized():
    """Γ(gamma)의 drivers 키 'cond_sweep_cpm(coverage_only,not_multiplied)'처럼
    진단용 꼬리표가 붙은 키도 실제 파라미터(cond_sweep_cpm)로 정규화되어
    confidence를 올바르게 조회해야 한다(가공 키 그대로 조회하면 항상
    unverified로 오판했다 — 2026-09-13 수정)."""
    from tools.blockers import analyze

    blockers, cells = analyze()
    # cond_sweep_cpm 자체는 base.yaml에서 confidence=literature이므로,
    # 정규화가 되면 더 이상 "cond_sweep_cpm(coverage_only,not_multiplied)"가
    # 병목(bad_params)에 나타나지 않아야 한다.
    for cell in cells:
        for bad in cell.get("bad_params", []):
            assert not bad.startswith("cond_sweep_cpm("), (
                f"cond_sweep_cpm 진단 꼬리표 키가 정규화 없이 병목으로 오판됨: {bad}"
            )
