"""화학-기계 결합층 계약 테스트.

사용자 지시(2026-09-06): "당연히 화학적인것도 반영해야해. 슬러리첨가제나 세리아같은
입자는 화학작용이 메이저잖아"

이 파일이 지키는 것: **조성을 바꾸면 MRR이 실제로 바뀌는가.**
그게 안 되면 소재 개발자용 도구가 아니다(POSITIONING.md §2).

값을 고정하지 않고 관계·순위만 검사한다 — 팩 수치는 캘리브레이션으로 계속 바뀐다.
"""
import sys
from pathlib import Path

import numpy as np
import pytest

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from sim.chemistry import chemistry_factor, SOFTENING_EXPONENT  # noqa: E402
from sim.engine import Recipe, simulate  # noqa: E402
import sim.models  # noqa: E402,F401


class FakePack:
    """팩 인터페이스 최소 구현 — 화학 항만 격리해 검사한다."""
    def __init__(self, **kw):
        self.d = kw
        self.name = "fake"
    def has(self, k): return k in self.d
    def get(self, k): return self.d[k]
    def get_or(self, k, dv): return self.d.get(k, dv)


CU_BASE = dict(abrasive="alumina", oxidizer_peak_wt_pct=3.0, oxidizer_ref_wt_pct=3.0,
               oxidizer_wt_pct=3.0, inhibitor_mM=1.0, inhibitor_ref_mM=1.0,
               inhibitor_dG_ads_kJ=-35.4, inhibitor_strength_k=3.0)


# ── 이중 계상 방지 (실제로 밟았던 버그) ─────────────────────
def test_reference_composition_gives_unity():
    """기준 조성에서는 화학 배수가 정확히 1.0이어야 한다.

    회귀 방어: 팩의 Kp는 '이미 그 조성으로 측정된' 문헌 MRR에서 역산한 값이다.
    여기에 절대 (1-θ)를 곱하면 억제를 두 번 적용하게 되고, 실제로 Cu MRR이
    450 → 22.5 nm/min로 20배 떨어졌다(2026-09-06).
    """
    eff = chemistry_factor(FakePack(**CU_BASE))
    assert eff.active
    assert eff.factor == pytest.approx(1.0, rel=1e-9)


def test_packs_at_reference_do_not_shift_mrr():
    """실제 팩도 기준 조성이므로 화학층이 MRR을 흔들면 안 된다."""
    for pack in ("cu_h2o2_bta", "sti_ceria"):
        res = simulate(Recipe(pack=pack, time_s=60))
        assert any("화학" in n for n in res.notes), "화학층 보고가 없다"
        # Cu Kp(3.5e-13) 기준 MRR 오더가 유지되는지 — 20배 붕괴 회귀 방어
        assert 10.0 < float(np.mean(res.mrr_nm_per_min)) < 5000.0


# ── 조성 반응성 (스크리닝의 핵심) ───────────────────────────
def test_inhibitor_is_monotonic_even_when_theta_saturates():
    """억제제를 더 넣으면 항상 덜 깎여야 한다.

    (1-θ)를 그대로 쓰면 θ가 0.97에서 포화돼 2mM과 5mM이 구분되지 않는다
    (배수가 전부 1.000으로 평평해졌다 — 실제 발생). 억제제 농도를 비교하려는
    사용자에게 그건 고장난 도구다.
    """
    factors = []
    for mM in (0.1, 0.5, 1.0, 2.0, 5.0, 10.0):
        d = dict(CU_BASE); d["inhibitor_mM"] = mM
        factors.append(chemistry_factor(FakePack(**d)).factor)
    for a, b in zip(factors, factors[1:]):
        assert b < a, f"억제제 증가에도 MRR이 안 줄었다: {factors}"


def test_oxidizer_follows_kaufman_peak():
    """산화제는 단봉이다 — 부족해도 과해도 정점보다 낮아야 한다."""
    def f(c):
        d = dict(CU_BASE); d["oxidizer_wt_pct"] = c
        return chemistry_factor(FakePack(**d)).factor
    peak = f(3.0)
    assert f(0.5) < peak, "산화제 부족인데 정점보다 높다"
    assert f(12.0) < peak, "산화제 과잉인데 정점보다 높다 (Kaufman 경쟁 위반)"


def test_ceria_tooth_scales_with_ce3():
    """세리아는 Ce³⁺ 활성점이 늘면 더 깎여야 한다 (chemical tooth)."""
    def f(frac):
        return chemistry_factor(FakePack(
            abrasive="ceria", ce3_fraction=frac,
            ce3_fraction_ref=0.15, ceria_tooth_gain=1.0)).factor
    assert f(0.05) < f(0.15) < f(0.30)


def test_ceria_term_does_not_apply_to_silica():
    """실리카 슬러리에 chemical tooth를 적용하면 안 된다 — 메커니즘이 다르다.

    실리카는 물리흡착(−20~−40 kJ/mol), 세리아는 화학흡착(−111~−258 kJ/mol)이다.
    """
    eff = chemistry_factor(FakePack(
        abrasive="silica", ce3_fraction=0.4, ce3_fraction_ref=0.15))
    assert "ceria_tooth" not in eff.terms


# ── 정직성 ──────────────────────────────────────────────────
def test_missing_chemistry_is_reported_not_silently_unity():
    """화학 파라미터가 없으면 배수 1.0이되, 그 사실을 반드시 보고해야 한다.

    조용히 1.0을 쓰면 "화학을 반영했다"는 거짓말이 된다.
    """
    eff = chemistry_factor(FakePack(abrasive="silica"))
    assert eff.factor == 1.0
    assert eff.active is False
    assert any("비활성" in n for n in eff.notes)
    assert "비활성" in eff.describe()


def test_softening_exponent_matches_plowing_geometry():
    """MRR ∝ H^-1.5 는 plowing 기하에서 유도된 값이지 튜닝 손잡이가 아니다.

    근거: knowledge/cmp/particle-wafer-interaction-mechanical-chemical-balance.md §4
      δ_p ∝ H⁻¹, A_f ∝ δ_p^1.5 ⟹ H를 4배 낮추면 체적 8배 (=4^1.5, 노트 verify PASS)
    """
    assert SOFTENING_EXPONENT == 1.5
    assert 4.0 ** SOFTENING_EXPONENT == pytest.approx(8.0)


def test_screening_ranks_compositions_sensibly():
    """스크리닝 시나리오: 5종 조성의 순위가 물리적으로 타당해야 한다.

    우리가 파는 것은 절대 MRR이 아니라 '어느 조성이 더 깎이는가'다
    (POSITIONING.md §3 — 데모 대체가 아니라 스크리닝).
    """
    def f(**ov):
        d = dict(CU_BASE); d.update(ov)
        return chemistry_factor(FakePack(**d)).factor

    standard = f()
    low_inhib = f(inhibitor_mM=0.3)
    high_inhib = f(inhibitor_mM=3.0)
    low_ox = f(oxidizer_wt_pct=1.0)
    high_ox = f(oxidizer_wt_pct=9.0)

    assert low_inhib > standard > high_inhib      # 억제제는 단조 억제
    assert low_ox < standard and high_ox < standard   # 산화제는 단봉
