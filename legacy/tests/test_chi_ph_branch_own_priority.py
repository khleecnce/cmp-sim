"""χ pH 항 선택 — has_own 우선 규칙 회귀 테스트 (EVIDENCE-RULES.md 판정#34).

sim/factors.py::_f_chi 의 pH 항 선택은 "팩이 어떤 pH 메커니즘의 고유 계수를
직접 선언(has_own)했다면, 상속만 받은 다른 메커니즘보다 우선한다"는 원칙을
따른다. 여기서 고정하는 것:
  (a) 5팩 각각이 타는 분기를 고정한다.
  (b) sic_ceria_h2o2는 ph_softening 분기를 탄다 (자기 이름으로 직접 역산한
      계수 ph_softening_per_unit이, 상속만 받은 sti_ceria의 abrasive_iep_ph
      보다 우선해야 한다).
  (c) 나머지 4팩(cu_h2o2_bta·oxide_silica·sti_ceria·w_fe_oxidizer)은 이 원칙
      도입 전과 분기가 완전히 동일해야 한다(회귀 방지).
  (d) sic_ceria_h2o2에서 pH를 9→11로 바꾸면 χ가 실제로 바뀐다 — 수정 전에는
      세리아 IEP 정전 창이 pH 9~11 구간에서 완전 포화해 안 바뀌었다.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sim.engine import Recipe          # noqa: E402
from sim.factors import _f_chi         # noqa: E402


def _chi_terms(pack, **overrides):
    rr = Recipe(pack=pack, pack_overrides=overrides).resolve()
    return _f_chi(rr)


def test_branch_selection_fixed_across_five_packs():
    expected = {
        "cu_h2o2_bta": set(),                        # oxidizer만 활성, pH 항은 전무
        "oxide_silica": {"ph_peak"},
        "sti_ceria": {"ph_ceria_window"},
        "w_fe_oxidizer": {"ph_w_acidic"},
        "sic_ceria_h2o2": {"ph_softening"},
    }
    ph_branch_names = {"ph_ceria_window", "ph_w_acidic", "ph_peak", "ph_softening"}
    for pack, want in expected.items():
        f = _chi_terms(pack)
        got = set(f.terms.keys()) & ph_branch_names
        assert got == want, f"{pack}: pH 분기 {got} != {want}"


def test_sic_takes_ph_softening_not_inherited_ceria_window():
    f = _chi_terms("sic_ceria_h2o2")
    assert "ph_softening" in f.terms
    assert "ph_ceria_window" not in f.terms


def test_other_four_packs_branch_unchanged():
    """세리아·산성W·실리카 3팩은 각자 own 메커니즘을 그대로 유지한다."""
    sti = _chi_terms("sti_ceria")
    assert "ph_ceria_window" in sti.terms

    w = _chi_terms("w_fe_oxidizer")
    assert "ph_w_acidic" in w.terms

    silica = _chi_terms("oxide_silica")
    assert "ph_peak" in silica.terms

    cu = _chi_terms("cu_h2o2_bta")
    ph_branch_names = {"ph_ceria_window", "ph_w_acidic", "ph_peak", "ph_softening"}
    assert not (set(cu.terms.keys()) & ph_branch_names)


def test_sic_ph_sensitivity_restored_in_alkaline_range():
    """수정 전: 세리아 IEP 창이 pH 9~11에서 포화해 χ가 전혀 안 바뀌었다.
    수정 후: sic 고유 ph_softening 항이 살아나 pH 9→11 에서 χ가 실제로 바뀐다."""
    chi_9 = _chi_terms("sic_ceria_h2o2", slurry_ph=9.0).value
    chi_11 = _chi_terms("sic_ceria_h2o2", slurry_ph=11.0).value
    assert chi_9 is not None and chi_11 is not None
    assert abs(chi_11 - chi_9) > 0.05 * abs(chi_9)
