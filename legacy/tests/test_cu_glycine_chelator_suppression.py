"""판정#72 — ψ 글리신(착화제) 억제축 회귀 테스트.

근거 노트: knowledge/cmp/psi-glycine-chelator-suppression-cu-jani2025.md
출처: Jani et al. 2025, doi:10.1149/2162-8777/adc59e (Table I x Table II)

이 파일이 지키는 계약 네 가지:
  1. 기준 조건에서 배수가 정확히 1.0 (이중 계상 방지)
  2. 착화제 종이 다르면 항이 꺼진다 (옥살산 +536.63 vs 글리신 -440.91, 판정#45)
  3. 농도를 올리면 억제 강화, 내리면 완화 (단조·방향)
  4. 통제쌍 실측 배수를 5% 안에서 재현
"""
import copy

import pytest

from sim.chemistry import _chelator_suppression_term
from sim.params import Param, load_pack

PACK = "cu_h2o2_bta"
# Jani 2025 Table I x II, 연마입자 존재 & 글리신만 변하는 통제쌍 (복제쌍 평균)
OBS_RATIO = {0.13: 1329.0 / 1544.5, 0.26: 452.0 / 694.0}


def _tweak(pk, **kw):
    q = copy.deepcopy(pk)
    for k, v in kw.items():
        q.params[k] = Param(key=k, value=v, confidence="unverified")
    return q


@pytest.fixture(scope="module")
def pk():
    return load_pack(PACK)


def test_unity_at_reference(pk):
    """기준 조성(글리신 1 wt% = 0.1332 M)에서 배수는 항등적으로 1.0."""
    v = _chelator_suppression_term(pk, [])
    assert v is not None, "이 팩에서 글리신 억제 항이 활성이어야 한다"
    assert abs(v - 1.0) < 1e-12


def test_species_gate_blocks_transfer(pk):
    """옥살산으로 선언하면 글리신 적합값을 전이하지 않는다(부호가 반대)."""
    notes = []
    assert _chelator_suppression_term(_tweak(pk, chelator_species="oxalic_acid"),
                                      notes) is None
    assert any("부호가 반대" in n or "전이하지 않는다" in n for n in notes)


def test_missing_concentration_is_skipped(pk):
    """농도가 없으면 지어내지 않고 항을 건너뛴다."""
    q = copy.deepcopy(pk)
    q.params.pop("chelator_M", None)
    notes = []
    assert _chelator_suppression_term(q, notes) is None
    assert any("chelator_M" in n for n in notes)


def test_monotonic_direction(pk):
    """농도 ↑ → 억제 강화(<1), 농도 ↓ → 완화(>1)."""
    zero = _chelator_suppression_term(_tweak(pk, chelator_M=0.0), [])
    hi = _chelator_suppression_term(_tweak(pk, chelator_M=0.26), [])
    assert hi < 1.0 < zero
    vals = [_chelator_suppression_term(_tweak(pk, chelator_M=c), [])
            for c in (0.0, 0.05, 0.13, 0.26)]
    assert vals == sorted(vals, reverse=True), "농도에 대해 단조 감소여야 한다"


@pytest.mark.parametrize("C", sorted(OBS_RATIO))
def test_reproduces_controlled_pairs(pk, C):
    """0 M 기준으로 정규화한 예측이 실측 배수를 5% 안에서 재현."""
    zero = _chelator_suppression_term(_tweak(pk, chelator_M=0.0), [])
    pred = _chelator_suppression_term(_tweak(pk, chelator_M=C), []) / zero
    obs = OBS_RATIO[C]
    assert abs(pred - obs) / obs < 0.05, f"C={C}: 예측 {pred:.4f} vs 실측 {obs:.4f}"


def test_psi_factor_includes_chelator_term():
    """팩터 레벨 배선 확인 — ψ.terms 에 항이 실려 있고 driver 가 노출된다."""
    from sim.engine import Recipe
    from sim.factors import compute_factors

    fs = compute_factors(Recipe(pack=PACK).resolve())
    psi = fs["psi"]
    assert "chelator_suppression" in psi.terms
    assert abs(psi.terms["chelator_suppression"] - 1.0) < 1e-12
    assert "chelator_M" in psi.drivers
