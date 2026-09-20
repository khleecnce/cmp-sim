"""Γ(컨디셔닝 부하) confidence 하한 3사유 판정 고정 — 값이 아니라 등급만 바뀌는 변경임을 못 박는다.

근거: knowledge/equipment/gamma-conditioning-load-confidence-basis.md, EVIDENCE-RULES 판정#22.
  (1) Rs 보정 — 해소(총량 스칼라 한정): 등급 사유에서 제외, notes에 폐형식 상계 명시.
  (2) τ 2차 인용 앵커 — 조건부: t=t_ref 에서는 A≡1이라 무관, |A−1|>GAMMA_AGING_CONF_TOL 일 때만 하한+note.
  (3) 임계하중 — 미해소: 무조건 estimated 하한 유지 → 기준조건 등급은 estimated 그대로.
conditioner_pcr_decay.py(sim/tier2_physics)는 여기서 1바이트도 수정하지 않는다 — import만.
"""
import math
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "sim" / "tier2_physics"))

from sim.engine import Recipe                     # noqa: E402
from sim.factors import GAMMA_AGING_CONF_TOL, compute_factors   # noqa: E402

import conditioner_pcr_decay as CPD                # noqa: E402

PACKS = ["oxide_silica", "cu_h2o2_bta", "w_fe_oxidizer", "sti_ceria", "sic_ceria_h2o2"]
TAU_NOTE_KEY = "판정#14"          # 사유(2) 조건부 note 식별자
CRIT_NOTE_KEY = "임계하중"         # 사유(3) 미해소 note 식별자


def _gamma(pack="oxide_silica", **overrides):
    return compute_factors(Recipe(pack=pack, pack_overrides=overrides).resolve())["gamma"]


# ── 기준조건(t = t_ref): 판정 결과와 일치 ─────────────────────────────────────

@pytest.mark.parametrize("pack", PACKS)
def test_reference_condition_confidence_is_estimated_because_of_reason_3(pack):
    """사유(3)이 미해소라 기준조건 등급은 estimated. 단 사유(2) note는 붙지 않는다(A≡1)."""
    g = _gamma(pack)
    assert g.terms["aging(pcr_decay)"] == pytest.approx(1.0, abs=1e-12)
    assert g.confidence == "estimated"
    assert any(CRIT_NOTE_KEY in n for n in g.notes)
    assert not any(TAU_NOTE_KEY in n for n in g.notes)
    assert "knowledge/equipment/gamma-conditioning-load-confidence-basis.md" in g.sources


def test_reference_condition_gamma_is_independent_of_tau():
    """t=t_ref 에서 τ를 10배·1/10배로 바꿔도 Γ 값·등급 모두 불변 — 사유(2) 항등성."""
    tau0 = CPD.TAU_AGING_HOURS
    try:
        out = {}
        for k in (1.0, 10.0, 0.1):
            CPD.TAU_AGING_HOURS = tau0 * k
            g = _gamma()
            out[k] = (g.value, g.confidence)
    finally:
        CPD.TAU_AGING_HOURS = tau0
    assert out[10.0][0] == pytest.approx(out[1.0][0], abs=1e-12)
    assert out[0.1][0] == pytest.approx(out[1.0][0], abs=1e-12)
    assert out[1.0][1] == out[10.0][1] == out[0.1][1] == "estimated"


def test_rs_correction_is_no_longer_a_grade_reason_but_edge_distribution_is_noted():
    """사유(1): notes가 폐형식 상계(해소)와 에지 14.4%(분포 몫)를 둘 다 말해야 한다."""
    g = _gamma()
    rs_notes = [n for n in g.notes if "μ²/8" in n]
    assert len(rs_notes) == 1
    assert "해소" in rs_notes[0] and "14.4%" in rs_notes[0]
    assert not rs_notes[0].startswith("⚠")          # 더 이상 경고(하한 사유)가 아니다


# ── t ≠ t_ref: 사유(2) 조건부 하한이 실제로 걸린다 ───────────────────────────

def test_disk_usage_20h_triggers_conditional_tau_floor_with_note():
    g = _gamma(cond_disk_usage_hours=20.0)
    a = g.terms["aging(pcr_decay)"]
    assert a == pytest.approx(math.exp(-20.0 / CPD.TAU_AGING_HOURS), abs=1e-12)
    assert abs(a - 1.0) > GAMMA_AGING_CONF_TOL
    assert g.confidence == "estimated"
    tau_notes = [n for n in g.notes if TAU_NOTE_KEY in n]
    assert len(tau_notes) == 1 and "27.4" in tau_notes[0] and "조건부" in tau_notes[0]


def test_tolerance_boundary_of_conditional_floor():
    """|A−1| 이 톨러런스 안이면 사유(2) note 없음, 밖이면 있음 — 문턱이 실제로 작동하는지."""
    tau = CPD.TAU_AGING_HOURS
    t_inside = -tau * math.log(1.0 - GAMMA_AGING_CONF_TOL * 0.5)   # A = 1 − 0.5·tol
    t_outside = -tau * math.log(1.0 - GAMMA_AGING_CONF_TOL * 2.0)  # A = 1 − 2·tol
    g_in = _gamma(cond_disk_usage_hours=t_inside)
    g_out = _gamma(cond_disk_usage_hours=t_outside)
    assert not any(TAU_NOTE_KEY in n for n in g_in.notes)
    assert any(TAU_NOTE_KEY in n for n in g_out.notes)
    assert g_in.confidence == g_out.confidence == "estimated"      # 사유(3) 때문에 둘 다 estimated


def test_equal_nonzero_usage_and_reference_is_identity():
    """t = t_ref = 20h 도 비율이라 A≡1 → 사유(2) note 없음."""
    g = _gamma(cond_disk_usage_hours=20.0, cond_ref_disk_usage_hours=20.0)
    assert g.terms["aging(pcr_decay)"] == pytest.approx(1.0, abs=1e-12)
    assert not any(TAU_NOTE_KEY in n for n in g.notes)


# ── Γ 값은 이번 변경으로 바뀌지 않는다 ──────────────────────────────────────

@pytest.mark.parametrize("pack", PACKS)
def test_gamma_value_unchanged_reference(pack):
    assert _gamma(pack).value == pytest.approx(1.0, abs=1e-12)


@pytest.mark.parametrize("hours,expected", [
    (0.0, 1.0),
    (20.0, math.exp(-20.0 / CPD.TAU_AGING_HOURS)),
    (50.0, CPD.ENTEGRIS_ANCHOR_RATIO),                 # 앵커 재현(0.16), 기존 test_gamma_pcr_aging와 동일
])
def test_gamma_value_unchanged_with_usage_hours(hours, expected):
    g = _gamma(cond_disk_usage_hours=hours)
    assert g.value == pytest.approx(expected, abs=1e-9)


def test_gamma_value_follows_closed_form_for_driver_changes():
    """값 계약: Γ = (F/F_ref)(ω/ω_ref)(duty/duty_ref)·A — 등급 로직이 값에 손대지 않았는지."""
    g = _gamma(cond_downforce_lbf=6.0, cond_duty_pct=50.0, rpm_platen=110.0, cond_disk_usage_hours=10.0)
    rr = Recipe(pack="oxide_silica").resolve()
    f_ref = float(rr.pack.get_or("cond_ref_downforce_lbf", 4.0))
    w_ref = float(rr.pack.get_or("lambda_ref_rpm_platen", rr.rpm_platen))
    d_ref = float(rr.pack.get_or("cond_ref_duty_pct", 100.0))
    expected = (6.0 / f_ref) * (110.0 / w_ref) * (50.0 / d_ref) * math.exp(-10.0 / CPD.TAU_AGING_HOURS)
    assert g.value == pytest.approx(expected, rel=1e-12)
