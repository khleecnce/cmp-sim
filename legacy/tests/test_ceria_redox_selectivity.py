"""ceria_redox_selectivity.py 회귀 테스트.

knowledge/cmp/ceria-slurry-ce-redox-selectivity.md §7 python verify 블록의 assert 값을
그대로 재현한다 (임의 임계값 없음, 새 숫자 없음): (A)~(E).
"""
import pytest

import ceria_redox_selectivity as crs


# ---------------------------------------------------------------------------
# §7 (A) — 산소공공 x <-> Ce3+ 분율 전하균형
# ---------------------------------------------------------------------------

def test_ce3_fraction_reproduces_known_values():
    """ce3_fraction(0.10)~=0.20, ce3_fraction(0.05)~=0.10 (노트 assert)."""
    assert abs(crs.ce3_fraction(0.10) - 0.20) < 1e-12
    assert abs(crs.ce3_fraction(0.05) - 0.10) < 1e-12


def test_ce3_fraction_charge_neutrality_self_consistent():
    """전하중립 자기일관: 4(1-f) + 3f == 2(2-x) (노트 assert, x=0.02,0.10,0.25)."""
    for x in (0.02, 0.10, 0.25):
        f = crs.ce3_fraction(x)
        assert abs(4 * (1 - f) + 3 * f - 2 * (2 - x)) < 1e-12


# ---------------------------------------------------------------------------
# §7 (B) — Si-O-Ce 화학흡착 (Brugnoli 2023, doi:10.1021/acs.langmuir.3c00304)
# ---------------------------------------------------------------------------

def test_chemisorption_energy_kj_mol_matches_brugnoli_2023():
    """-1.15 eV~=-111 kJ/mol, -2.67 eV~=-257.6 kJ/mol (노트 assert)."""
    E111 = crs.chemisorption_energy_kj_mol(-1.15)
    E100 = crs.chemisorption_energy_kj_mol(-2.67)
    assert abs(E111 - (-110.96)) < 0.5
    assert abs(E100 - (-257.61)) < 0.5


def test_both_surfaces_are_chemisorption():
    """(111)·(100) 모두 물리흡착(-20~-40) 경계보다 강함 -> is_chemisorption()=True (노트 assert)."""
    E111 = crs.chemisorption_energy_kj_mol(-1.15)
    E100 = crs.chemisorption_energy_kj_mol(-2.67)
    assert E111 < -50 and E100 < -50
    assert crs.is_chemisorption(E111) is True
    assert crs.is_chemisorption(E100) is True


def test_100_over_111_bond_strength_ratio_2p32():
    """(100)/(111) 결합강도비 2.32배 (노트 assert)."""
    assert abs((-2.67) / (-1.15) - 2.32) < 0.02


# ---------------------------------------------------------------------------
# §7 (C) — IEP 차이 -> 세리아(+)·실리카(-) 정전인력
# ---------------------------------------------------------------------------

def test_electrostatic_attraction_ph_4_to_6():
    """pH 4,5,6에서 세리아(IEP=6.8)·실리카(IEP=2.5) 반대부호 -> 인력(-1) (노트 assert)."""
    for pH in (4, 5, 6):
        assert crs.electrostatic_attraction(6.8, 2.5, pH) < 0


def test_electrostatic_no_repulsion_above_ceria_iep():
    """pH=8.0 (세리아 IEP 6.8보다 높음) -> 둘 다 음전하 -> 곱은 +1(반발 아님, 노트 assert)."""
    assert crs.electrostatic_attraction(6.8, 2.5, 8.0) > 0


# ---------------------------------------------------------------------------
# §7 (D) — oxide:nitride 선택비 (Hwang & Kim 2024, doi:10.3390/polym16060844)
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("name,oxide_mrr,nitride_mrr,reported", [
    ("Base", 3493, 60, 59),
    ("Depol", 4650, 75, 62),
    ("BYK", 5558, 83, 67),
    ("G-336", 5417, 68, 80),
])
def test_oxide_nitride_selectivity_matches_hwang_kim_2024(name, oxide_mrr, nitride_mrr, reported):
    calc = crs.oxide_nitride_selectivity(oxide_mrr, nitride_mrr)
    assert abs(round(calc) - reported) <= 1, f"{name}: 계산 {calc:.1f} vs 보고 {reported}"
    assert calc > 40


# ---------------------------------------------------------------------------
# §7 (E) — Netzband & Dunn 2020 (doi:10.1149/2162-8777/ab8393)
# ---------------------------------------------------------------------------

def test_h2o2_boost_selectivity_1_to_3():
    """H2O2 0.5wt%로 선택비 1:1 -> 3:1 (노트 assert)."""
    assert crs.h2o2_boost_selectivity(1.0, 3.0) == 3.0
