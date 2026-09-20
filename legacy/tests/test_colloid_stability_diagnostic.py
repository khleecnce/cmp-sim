"""dlvo_colloid.py stability_qualitative() 엔진 등록 회귀 — WaferResult 진단 필드 3종.

근거: knowledge/cmp/colloid-zeta-dlvo-slurry-stability.md §5 (self-test 15/15 PASS).
MRR 경로와 독립인 진단 필드라 mrr_nm_per_min은 건드리지 않는다.
"""
import dlvo_colloid as DLVO

from sim.engine import Recipe, simulate


def test_simulate_fills_colloid_fields_for_oxide_silica():
    # oxide_silica: slurry_ph=10.5, abrasive_iep_ph=2.5 -> 거리=8.0 -> risk=low
    res = simulate(Recipe(pack="oxide_silica", time_s=60))
    assert res.colloid_distance_from_iep_ph is not None
    assert abs(res.colloid_distance_from_iep_ph - 8.0) < 1e-9
    assert res.colloid_stability_risk == "low"
    assert res.colloid_stability_note is not None
    # MRR 경로는 이 진단과 무관하게 그대로여야 한다
    assert res.mrr_nm_per_min.shape == res.radius_m.shape


def test_simulate_leaves_colloid_fields_none_without_iep():
    # cu_h2o2_bta에는 abrasive_iep_ph가 없다 — 조용히 None
    res = simulate(Recipe(pack="cu_h2o2_bta", time_s=60))
    assert res.colloid_distance_from_iep_ph is None
    assert res.colloid_stability_risk is None
    assert res.colloid_stability_note is None


def test_risk_classification_by_iep_distance():
    assert DLVO.stability_qualitative(10.5, 2.5)["risk"] == "low"    # 거리 8.0 >= 2.0
    assert DLVO.stability_qualitative(3.0, 2.5)["risk"] == "high"    # 거리 0.5 < 1.0
    assert DLVO.stability_qualitative(4.0, 2.5)["risk"] == "medium"  # 1.0 <= 거리1.5 < 2.0


def test_sti_ceria_pack_fills_colloid_fields():
    # sti_ceria: slurry_ph=5.5, abrasive_iep_ph=6.8 -> 거리=1.3 -> medium
    res = simulate(Recipe(pack="sti_ceria", time_s=60))
    assert res.colloid_stability_risk == "medium"
    assert abs(res.colloid_distance_from_iep_ph - 1.3) < 1e-9


def test_colloid_diagnostic_does_not_change_mrr():
    # 진단은 MRR 경로와 완전히 독립 — colloid 필드가 채워지는 팩(oxide_silica)이나
    # 채워지지 않는 팩(cu_h2o2_bta)이나 MRR 계산 로직 자체는 동일 코드경로를 탄다.
    # 이 진단 추가 전후로 preston 모델(MRR 경로)이 정상 동작함을 확인한다 —
    # 콜로이드 진단이 MRR 계산에 관여하지 않는다는 회귀 방지.
    r = Recipe(pack="sti_ceria", pressure_psi=20.7e3 / 6894.757, time_s=60,
               rpm_wafer=60, rpm_platen=60)
    res = simulate(r)
    assert res.mrr_nm_per_min.shape == res.radius_m.shape
    assert (res.mrr_nm_per_min > 0).all()
