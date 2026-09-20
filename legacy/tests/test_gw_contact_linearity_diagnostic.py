"""gw_preston_link.py 엔진 등록 회귀 — WaferResult 진단 필드 3종(GW 접촉역학 선형성/Kp 물리분해).

근거: sim/tier2_physics/gw_preston_link.py (self-test 4/4 PASS),
knowledge/materials/gw-nominal-vs-local-pressure.md, knowledge/materials/hertz-gw-contact-mechanics.md.
MRR 경로와 독립인 진단 필드라 mrr_nm_per_min은 건드리지 않는다.
"""
import numpy as np

import sim.engine as E
from sim.engine import Recipe, simulate, _gw_contact_linearity_diagnostic

_PACKS = ["cu_h2o2_bta", "oxide_silica", "sic_ceria_h2o2", "sti_ceria", "w_fe_oxidizer"]


def test_none_without_gw_pad_params():
    # base.yaml에 있는 pad_E_star_pa를 이 팩 인스턴스에서만 지워 "GW 패드 파라미터 없는 팩"을 재현
    rr = Recipe(pack="oxide_silica", time_s=60).resolve()
    del rr.pack.params["pad_E_star_pa"]
    out = _gw_contact_linearity_diagnostic(rr)
    assert out["gw_contact_linearity_max_dev"] is None
    assert out["gw_kp_physical_to_lit_ratio"] is None
    assert out["gw_contact_note"] is None


def test_simulate_fills_gw_fields_for_all_five_packs():
    # pad_E_star_pa 등 5개 GW 패드 파라미터는 base.yaml에만 있고(팩별 오버라이드 없음),
    # kp_m_per_pa가 있는 5개 팩 전부가 이를 상속하므로 전부 채워져야 한다.
    for pack in _PACKS:
        res = simulate(Recipe(pack=pack, time_s=60))
        assert res.gw_contact_linearity_max_dev is not None, pack
        assert res.gw_kp_physical_to_lit_ratio is not None, pack
        assert res.gw_contact_note is not None, pack
        assert res.gw_contact_linearity_max_dev >= 0.0


def test_gw_kp_physical_to_lit_ratio_is_near_identity():
    # Kp_physical은 이 레시피의 P_center에서 역산된 alpha_removal로부터 나오므로
    # (calibrate_alpha_removal이 바로 그 지점의 Preston-direct MRR과 일치하도록 정의됨),
    # n_contacts(P)가 거의 완전히 선형(잔차~1e-12 오더)인 한 이 비율은 1.0에 극도로
    # 가까워야 한다 — 이건 항등식에 가까운 결과이지 별도의 물리 예측이 아니다(문서화 목적 assert).
    res = simulate(Recipe(pack="sti_ceria", time_s=60))
    assert abs(res.gw_kp_physical_to_lit_ratio - 1.0) < 0.05


def test_gw_diagnostic_does_not_change_mrr():
    # 이 진단을 계산하든 안 하든(no-op으로 대체하든) mrr_nm_per_min은 동일해야 한다 —
    # MRR 경로와 완전히 독립적인 진단이라는 계약.
    r = Recipe(pack="sti_ceria", time_s=60)
    res_with = simulate(r)

    orig = E._gw_contact_linearity_diagnostic
    E._gw_contact_linearity_diagnostic = lambda rr: {
        "gw_contact_linearity_max_dev": None,
        "gw_kp_physical_to_lit_ratio": None,
        "gw_contact_note": None,
    }
    try:
        res_without = simulate(r)
    finally:
        E._gw_contact_linearity_diagnostic = orig

    assert np.allclose(res_with.mrr_nm_per_min, res_without.mrr_nm_per_min)
    assert res_without.gw_contact_linearity_max_dev is None


def test_zone_pressures_and_uniform_pressure_both_work():
    # zone_pressures_psi가 있는 레시피(존압력 프로파일)와 없는 레시피(0.5x/1x/1.5x P_center
    # 3점 합성) 둘 다 조용히 계산돼야 한다.
    res_uniform = simulate(Recipe(pack="sti_ceria", time_s=60))
    res_zoned = simulate(Recipe(pack="sti_ceria", time_s=60,
                                zone_pressures_psi=[2.0, 3.0, 4.0]))
    assert res_uniform.gw_contact_linearity_max_dev is not None
    assert res_zoned.gw_contact_linearity_max_dev is not None
    assert res_uniform.gw_contact_note != res_zoned.gw_contact_note
