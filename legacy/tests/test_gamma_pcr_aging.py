"""Γ(컨디셔닝 부하)에 컨디셔너 PCR 시간적 소진(aging) 통합 — 회귀 및 방향성 테스트.

conditioner_pcr_decay.py(sim/tier2_physics)는 여기서 1바이트도 수정하지 않는다 — import만.
"""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "sim" / "tier2_physics"))

from sim.engine import Recipe                     # noqa: E402
from sim.factors import compute_factors            # noqa: E402

import conditioner_pcr_decay as CPD                # noqa: E402


def _gamma(pack="oxide_silica", **overrides):
    return compute_factors(Recipe(pack=pack, pack_overrides=overrides).resolve())["gamma"]


def test_usage_hours_zero_means_no_aging():
    """cond_disk_usage_hours=0(신품)이면 aging 배수는 1.0 — Γ에 영향 없음."""
    g = _gamma(cond_disk_usage_hours=0.0)
    assert g.terms["aging(pcr_decay)"] == pytest.approx(1.0, abs=1e-9)


def test_usage_hours_50_reproduces_entegris_anchor():
    """cond_disk_usage_hours=50이면 Entegris 앵커(50h -> 16%)를 그대로 재현한다."""
    g = _gamma(cond_disk_usage_hours=50.0)
    assert g.terms["aging(pcr_decay)"] == pytest.approx(CPD.ENTEGRIS_ANCHOR_RATIO, abs=1e-9)
    # CPD.pcr_decay와 직접 비교(엔진이 같은 함수를 그대로 호출했는지 확인)
    expected = CPD.pcr_decay(50.0, 1.0, CPD.TAU_AGING_HOURS)
    assert g.terms["aging(pcr_decay)"] == pytest.approx(expected, abs=1e-9)


def test_missing_driver_keeps_legacy_behavior():
    """cond_disk_usage_hours를 팩에서 아예 안 주면(기존 5팩과 동일) aging=1.0 — 회귀 방지."""
    g_with = _gamma(cond_disk_usage_hours=0.0)
    g_without = compute_factors(Recipe(pack="oxide_silica").resolve())["gamma"]
    assert "aging(pcr_decay)" in g_with.terms
    assert g_without.value == pytest.approx(g_with.value, abs=1e-9)


@pytest.mark.parametrize("pack", ["oxide_silica"])
def test_gamma_monotonically_decreases_with_usage_hours(pack):
    """F/rpm/duty 고정 시, 디스크 사용시간이 늘수록 Γ는 단조감소해야 한다."""
    hours = [0.0, 10.0, 27.4, 50.0, 100.0]
    values = [_gamma(pack, cond_disk_usage_hours=h).value for h in hours]
    assert all(v is not None for v in values)
    assert all(values[i] > values[i + 1] for i in range(len(values) - 1)), values


def test_gamma_confidence_stays_estimated_not_upgraded():
    """aging 배수를 붙여도 confidence는 estimated 유지(오염 금지 — 근거 없는 승격 방지)."""
    g = _gamma(cond_disk_usage_hours=50.0)
    assert g.confidence == "estimated"
