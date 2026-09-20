"""particle_chemomechanical_synergy.py 회귀 테스트.

knowledge/cmp/particle-wafer-interaction-mechanical-chemical-balance.md §4의
python verify 블록 정량값을 그대로 재현한다 (임의 임계값 없음, change-detector 아님).
"""
import particle_chemomechanical_synergy as pcs

R = 50e-9  # m, 콜로이달 실리카 입자 반경 (직경 ~100nm)


def test_effective_modulus_sio2_sio2():
    """SiO2-SiO2 등가탄성계수 E* ~= 37.6 GPa (E=73GPa, nu=0.17)."""
    Estar = pcs.effective_modulus(73e9, 0.17, 73e9, 0.17)
    assert abs(Estar / 1e9 - 37.6) < 0.5


def test_hertz_contact_f50nn_precise():
    """F=50nN에서 p_max~=1.22GPa, delta~=0.271nm (노트 §4 대표값)."""
    Estar = pcs.effective_modulus(73e9, 0.17, 73e9, 0.17)
    a, delta, p_max = pcs.single_particle_elastic_contact(50e-9, R, Estar)
    assert abs(p_max / 1e9 - 1.22) < 0.05
    assert abs(delta * 1e9 - 0.271) < 0.01


def test_hertz_contact_order_of_magnitude():
    """F=10/50/100nN 전부 접촉응력 GPa 오더(0.5~5GPa), 압입 sub-nm 오더(0.05~1nm)."""
    Estar = pcs.effective_modulus(73e9, 0.17, 73e9, 0.17)
    for F in (10e-9, 50e-9, 100e-9):
        a, delta, p_max = pcs.single_particle_elastic_contact(F, R, Estar)
        assert 0.5e9 < p_max < 5e9
        assert 0.05e-9 < delta < 1e-9


def test_chemical_softening_amplifies_depth_and_volume():
    """H 4배↓(2.0GPa->0.5GPa) -> depth_ratio~=4.0(정확한 해석적 결과), volume_ratio~=8.0."""
    amp = pcs.chemomechanical_amplification(2.0e9, 0.5e9, 50e-9, R)
    assert abs(amp["depth_ratio"] - 4.0) < 0.01
    assert abs(amp["volume_ratio"] - 8.0) < 0.05


def test_load_doubling_scales_volume_by_2p5_power():
    """하중 2배(50nN->100nN) -> 단일입자 제거체적 2^1.5배 (소성 plowing V∝F^1.5)."""
    _, A1 = pcs.plastic_plowing(50e-9, R, 1e9)
    _, A2 = pcs.plastic_plowing(100e-9, R, 1e9)
    ratio = A2 / A1
    assert abs(ratio - 2 ** 1.5) < 0.02
