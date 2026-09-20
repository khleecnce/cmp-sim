"""disk_cutrate_coupling.py 회귀 테스트 — _self_test()의 항목을 pytest화.

노트 knowledge/materials/disk-design-cutrate-asperity-regeneration-model.md §2, §3, §5
verify 블록의 Kwon(2013)·Tsai(2014) 문헌값 재현만 다룬다(새 문헌 숫자 없음).
"""
import pytest

import disk_cutrate_coupling as dcc


def test_cutrate_density_scaling_reproduces_kwon_40e3():
    # Kwon et al. 2013: N=[17e3,40e3,60e3] -> CR=[37.0,23.0,19.0] µm/h(2h)
    # N_ref=17e3, CR_ref=37.0로 N=40e3 예측 (3점 회귀 지수 -0.53이라 완전일치는 아님).
    pred = dcc.cutrate_density_scaling(40e3, 17e3, 37.0)
    assert abs(pred - 23.0) / 23.0 < 0.20


def test_cutrate_rpk_scaling_reproduces_kwon_1_7():
    # Rpk=[3.75,2.25,1.7] -> CR=[37.0,23.0,19.0], Rpk_ref=3.75,CR_ref=37.0로 Rpk=1.7 예측.
    pred = dcc.cutrate_rpk_scaling(1.7, 3.75, 37.0)
    assert abs(pred - 19.0) / 19.0 < 0.20


def test_active_grit_residual_factor_reproduces_tsai_1_75():
    # Tsai et al. 2014: N_eff 비 1.12배(432->484 대리), PCR 비 1.96배(24.0->47.0 µm/h)
    residual = dcc.active_grit_residual_factor(1.12, 1.96)
    assert residual == pytest.approx(1.75, rel=0.02)


def test_disk_cutrate_coupled_missing_g_or_neff_ratio_not_applied():
    # Neff_ratio, g 중 하나라도 None이면 active_term_applied=False + 안내 note.
    # 노트 §5·§6이 g를 명시적으로 미확정이라 했으므로 engine에는 등록하지 않는 계약 테스트.
    out_no_g = dcc.disk_cutrate_coupled(40e3, 17e3, 1.7, 3.75, 37.0, Neff_ratio=1.12, g=None)
    out_no_neff = dcc.disk_cutrate_coupled(40e3, 17e3, 1.7, 3.75, 37.0, Neff_ratio=None, g=0.3)
    out_neither = dcc.disk_cutrate_coupled(40e3, 17e3, 1.7, 3.75, 37.0)

    for out in (out_no_g, out_no_neff, out_neither):
        assert out["active_term_applied"] is False
        assert out["active_term"] is None
        assert out["note"] == (
            "g(활성 비율 지수)는 노트가 미확정이라 캘리브레이션 없이는 적용 불가"
        )


def test_disk_cutrate_coupled_applies_active_term_when_both_given():
    out = dcc.disk_cutrate_coupled(40e3, 17e3, 1.7, 3.75, 37.0, Neff_ratio=1.12, g=0.3)
    assert out["active_term_applied"] is True
    assert out["active_term"] == pytest.approx(1.12 ** 0.3)
    assert out["note"] is None


def test_cutrate_density_scaling_monotonic_decreasing_in_N():
    cr_lo = dcc.cutrate_density_scaling(17e3, 17e3, 37.0)
    cr_hi = dcc.cutrate_density_scaling(60e3, 17e3, 37.0)
    assert cr_hi < cr_lo


def test_cutrate_rpk_scaling_monotonic_increasing_in_Rpk():
    cr_lo = dcc.cutrate_rpk_scaling(1.7, 3.75, 37.0)
    cr_hi = dcc.cutrate_rpk_scaling(3.75, 3.75, 37.0)
    assert cr_hi > cr_lo
