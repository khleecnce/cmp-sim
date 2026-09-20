"""galvanic_hydroxide_ph.py 회귀 테스트.

knowledge/cmp/low-level-metal-cobalt-ruthenium-cross-contamination.md §3.1·§3.3·
§6 verify (A)(B) 검증값을 그대로 재현한다.
"""
import math

import pytest

import galvanic_hydroxide_ph as ghp


def test_galvanic_pair_direction_cu_co():
    """Cu-Co 쌍: Co가 양극, ΔE0 ~= 0.6219 V (0.3419-(-0.28), 노트 §6(A))."""
    result = ghp.galvanic_pair_direction("Cu", "Co")
    assert result["anode"] == "Co"
    assert result["cathode"] == "Cu"
    assert result["delta_E0_V"] == pytest.approx(0.6219, abs=1e-2)


def test_galvanic_pair_direction_ru_cu():
    """Ru-Cu 쌍: Cu가 양극, ΔE0 ~= 0.1131 V (0.455-0.3419, 노트 §6(A))."""
    result = ghp.galvanic_pair_direction("Ru", "Cu")
    assert result["anode"] == "Cu"
    assert result["cathode"] == "Ru"
    assert result["delta_E0_V"] == pytest.approx(0.1131, abs=1e-2)


def test_galvanic_pair_direction_unknown_metal_raises():
    with pytest.raises((KeyError, ValueError)):
        ghp.galvanic_pair_direction("Cu", "Unobtainium")


def test_galvanic_pair_direction_custom_table_overrides_default():
    custom = {"A": 0.0, "B": 1.0}
    result = ghp.galvanic_pair_direction("A", "B", E0_table=custom)
    assert result["anode"] == "A"
    assert result["delta_E0_V"] == pytest.approx(1.0, abs=1e-9)


def test_hydroxide_transition_pH_cu_100ppm():
    """Cu 100 ppm -> 1.574e-3 mol/L -> pH* ~= 5.74 (노트 §6(B)); Bisht 2022 관찰 ~=6 (±0.5)."""
    C_mol_L = 100.0 * 1e-3 / 63.55  # 100 mg/L / 63.55 g/mol
    assert C_mol_L == pytest.approx(1.574e-3, abs=1e-6)
    pH_star = ghp.hydroxide_transition_pH("Cu", C_mol_L)
    assert pH_star == pytest.approx(5.74, abs=1e-2)
    assert abs(pH_star - 6.0) < 0.5  # Bisht et al. 2022 관찰 "≈6"과 대조


def test_hydroxide_transition_pH_co_100ppm():
    """Co 100 ppm -> 1.697e-3 mol/L -> pH* ~= 7.93 (노트 §6(B))."""
    C_mol_L = 100.0 * 1e-3 / 58.93  # 100 mg/L / 58.93 g/mol
    assert C_mol_L == pytest.approx(1.697e-3, abs=1e-6)
    pH_star = ghp.hydroxide_transition_pH("Co", C_mol_L)
    assert pH_star == pytest.approx(7.93, abs=1e-2)


def test_hydroxide_transition_pH_co_vs_cu_gap():
    """Co가 Cu보다 100 ppm 기준 pH* 약 2.19 높다(노트 §3.3: "Co가 Cu보다 2.0~2.5 높다")."""
    C_cu = 100.0 * 1e-3 / 63.55
    C_co = 100.0 * 1e-3 / 58.93
    pH_cu = ghp.hydroxide_transition_pH("Cu", C_cu)
    pH_co = ghp.hydroxide_transition_pH("Co", C_co)
    assert (pH_co - pH_cu) == pytest.approx(2.19, abs=1e-2)
    assert 2.0 < (pH_co - pH_cu) < 2.5


def test_hydroxide_transition_pH_unknown_metal_raises():
    with pytest.raises(ValueError):
        ghp.hydroxide_transition_pH("Unobtainium", 1e-3)
