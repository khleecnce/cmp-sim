"""sim/metrics/sampling_plan.py 검증 — 노트 `inline-virtual-metrology-sampling-optimization.md`
§3.1, §4 블록2(Table III CDS) 문헌값 재현. 스냅샷/임의값 금지."""
import pytest

from sim.metrics.sampling_plan import (
    material_at_risk,
    mssi_cds,
    mssi_min_balanced,
    static_sampling_plan,
    woi,
)


def test_material_at_risk():
    assert material_at_risk(5) == 5
    assert material_at_risk(1) == 1
    with pytest.raises(ValueError):
        material_at_risk(0)


def test_table_iii_cds_woi():
    # 노트 §4 블록2 Table III CDS 재현 데이터 그대로 (±0.1 %p는 노트가 이미 검증한 허용오차)
    V = 50
    t3_cds = {2: 50.0, 3: 34.0, 4: 26.1, 5: 20.0, 6: 18.2, 7: 16.3, 8: 14.3, 9: 12.2}
    for Vm, woi_lit in t3_cds.items():
        assert abs(woi(V, Vm) - woi_lit) <= 0.1, (Vm, woi(V, Vm), woi_lit)


def test_mssi_example_V50_Vm7():
    # 노트 §4 블록2 φ_PCA=5, k*=7 문맥의 V=50 예시
    assert mssi_min_balanced(50, 7) == 7
    assert mssi_cds(50, 7) == 43


def test_static_sampling_plan():
    plan = static_sampling_plan(20, 5)
    assert [i for i, measured in enumerate(plan) if measured] == [0, 5, 10, 15]
    assert sum(plan) == 4


def test_invalid_inputs_raise_value_error():
    with pytest.raises(ValueError):
        mssi_min_balanced(50, 51)  # Vm > V
    with pytest.raises(ValueError):
        mssi_cds(0, 0)  # V <= 0
    with pytest.raises(ValueError):
        static_sampling_plan(10, 0)  # sample_interval < 1
