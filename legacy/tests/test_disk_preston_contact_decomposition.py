"""disk_preston_contact_decomposition.py 회귀 테스트.

노트 knowledge/materials/disk-design-pad-roughness-asperity-relation.md §2.3, §3.4(b)
verify 블록의 η_c/A_f 값·방향성만 재현한다(새 문헌 숫자 없음).
"""
import pytest

import disk_preston_contact_decomposition as dpc

# Sun 2009 §2.3 표: (eta_c_A, a_f_A, eta_c_B, a_f_B)
PAD_TABLE = {
    "D100-1": (237, 5.6e-4, 58, 0.55e-4),
    "D100-2": (110, 2.9e-4, 42, 0.8e-4),
    "IC1000": (88, 4.4e-4, 80, 1.1e-4),
}


def test_eta_over_af_d100_1_type_a():
    assert abs(dpc.eta_over_af(237, 5.6e-4) - 4.23e5) / 4.23e5 < 0.05


def test_eta_over_af_d100_1_type_b():
    assert abs(dpc.eta_over_af(58, 0.55e-4) - 1.05e6) / 1.05e6 < 0.05


def test_eta_over_af_d100_1_ba_ratio():
    r_a = dpc.eta_over_af(237, 5.6e-4)
    r_b = dpc.eta_over_af(58, 0.55e-4)
    assert abs((r_b / r_a) - 2.48) / 2.48 < 0.10


@pytest.mark.parametrize("pad", PAD_TABLE.keys())
def test_eta_over_af_ba_direction_all_pads(pad):
    eta_a, af_a, eta_b, af_b = PAD_TABLE[pad]
    r_a = dpc.eta_over_af(eta_a, af_a)
    r_b = dpc.eta_over_af(eta_b, af_b)
    assert r_b > r_a, f"{pad}: 공격적 디스크(B)의 η_c/A_f가 더 크지 않음"


def test_eta_over_af_raises_on_nonpositive_af():
    with pytest.raises(ValueError):
        dpc.eta_over_af(100, 0.0)
    with pytest.raises(ValueError):
        dpc.eta_over_af(100, -1e-4)


def test_preston_coefficient_contact_scaling_identity():
    kp0 = 3.7
    assert dpc.preston_coefficient_contact_scaling(1.0e5, 1.0e5, kp0) == pytest.approx(kp0)


def test_preston_coefficient_contact_scaling_proportional():
    kp0 = 2.0
    kp = dpc.preston_coefficient_contact_scaling(2.0e5, 1.0e5, kp0)
    assert kp == pytest.approx(kp0 * 2.0)


def test_fragment_contact_separation_positive_excess():
    assert dpc.fragment_contact_separation(5.6e-4, 4.0e-4) == pytest.approx(1.6e-4)


def test_fragment_contact_separation_negative_clamped_to_zero():
    assert dpc.fragment_contact_separation(2.0e-4, 5.6e-4) == 0.0


def test_fragment_contact_separation_raises_on_negative_input():
    with pytest.raises(ValueError):
        dpc.fragment_contact_separation(-1e-4, 1e-4)
    with pytest.raises(ValueError):
        dpc.fragment_contact_separation(1e-4, -1e-4)


def test_disk_preston_contact_scaling_d100_1_a_to_b():
    out = dpc.disk_preston_contact_scaling(
        eta_c=58, a_f=0.55e-4, eta_c_ref=237, a_f_ref=5.6e-4, kp0=1.0
    )
    assert set(out.keys()) == {"eta_af", "eta_af_ref", "scale_factor", "kp_scaled"}
    assert abs(out["scale_factor"] - 2.48) / 2.48 < 0.10
    assert abs(out["kp_scaled"] - 2.48) / 2.48 < 0.10
