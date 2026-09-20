"""disk_gw_relative_scaling.py 회귀 테스트 — _self_test()의 항목을 pytest화.

노트 knowledge/materials/disk-design-pad-roughness-asperity-relation.md §3.1-§3.3
verify 블록의 멱법칙 지수·정량값만 재현한다(새 문헌 숫자 없음).
"""
import disk_gw_relative_scaling as dgw


def test_ra_relative_direction_and_kwon_ratio():
    ra_rel = dgw.ra_relative(40e3, 17e3)
    kwon_ratio = 8.05 / 6.8
    assert ra_rel > 1.0
    assert abs(ra_rel - kwon_ratio) / kwon_ratio < 0.15


def test_rpk_relative_direction_and_kwon_ratio():
    rpk_rel = dgw.rpk_relative(40e3, 60e3)
    kwon_rpk_ratio = 1.7 / 2.25
    assert rpk_rel < 1.0
    assert abs(rpk_rel - kwon_rpk_ratio) / kwon_rpk_ratio < 0.20


def test_surface_finish_relative_vs_3m_ratio():
    sf_rel = dgw.surface_finish_relative(45, 180)
    sf_3m_ratio_lo = 4.1 / 1.7
    sf_3m_ratio_hi = 4.2 / 1.7
    assert min(sf_3m_ratio_lo, sf_3m_ratio_hi) * 0.7 < sf_rel < max(sf_3m_ratio_lo, sf_3m_ratio_hi) * 1.3


def test_surface_finish_relative_leveled_multiplier():
    sf_leveled_vs_plain = dgw.surface_finish_relative(150, 150, leveled_target=True, leveled_ref=False)
    assert abs(sf_leveled_vs_plain - 0.57) < 1e-9


def test_lambda_relative_high_load_vs_sun_ratio():
    # Sun 2009 Fig.7.4: 8lb 조건에서 100-grit λ=6.7 µm vs 325-grit λ=4.3 µm(같은 하중 비교;
    # 3.3은 325-grit 3.6lb 값이라 다른 하중과 섞으면 안 됨)
    lam_rel_hi = dgw.lambda_relative(325, 100, high_load=True)
    sun_ratio = 6.7 / 4.3
    assert abs(lam_rel_hi - sun_ratio) / sun_ratio < 0.20


def test_lambda_relative_low_load_no_grit_effect():
    lam_rel_lo = dgw.lambda_relative(325, 100, high_load=False)
    assert abs(lam_rel_lo - 1.0) < 1e-9


def test_disk_gw_relative_scaling_composite_dict():
    ref = {"D_grit": 325, "N_grit": 40e3, "grade": "640", "leveled": False}
    target = {"D_grit": 100, "N_grit": 40e3, "grade": "640", "leveled": False}
    out = dgw.disk_gw_relative_scaling(ref, target, high_load=True)
    assert set(out.keys()) == {"lambda_rel", "Ra_rel", "Rpk_rel", "surface_finish_rel"}
    assert abs(out["lambda_rel"] - dgw.lambda_relative(325, 100, high_load=True)) < 1e-9
    assert abs(out["Ra_rel"] - 1.0) < 1e-9


def test_disk_gw_relative_scaling_grade_ignored():
    """grade는 문자열 태그일 뿐 수치 스케일링에 쓰지 않는다 — grade만 다른 두 target이
    동일한 배율을 내야 한다(Kwon 2013 §2.1 grade 효과 정량 미확보)."""
    ref = {"D_grit": 100, "N_grit": 40e3, "leveled": False}
    target_a = {"D_grit": 100, "N_grit": 60e3, "grade": "625", "leveled": False}
    target_b = {"D_grit": 100, "N_grit": 60e3, "grade": "925", "leveled": False}
    out_a = dgw.disk_gw_relative_scaling(ref, target_a, high_load=True)
    out_b = dgw.disk_gw_relative_scaling(ref, target_b, high_load=True)
    assert out_a == out_b
