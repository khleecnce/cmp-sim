"""ptw_vm_schema.py 회귀 테스트.

지식 근거: knowledge/cmp/product-wafer-proxy-metrics-virtual-metrology.md §5.3.
새 물리 모델·추정치는 도입하지 않는다 — 스키마 필드 유효성 검증만 확인한다.
"""
from sim.calibration.ptw_vm_schema import (
    PTWVMInput,
    validate_ptw_vm_input,
    is_npw_equivalent,
)


def test_basic_construction_with_required_fields_only():
    x = PTWVMInput(product_id="P1", layer="M3", die_density_mean=0.5)
    assert x.product_id == "P1"
    assert x.layer == "M3"
    assert x.die_density_mean == 0.5
    assert x.local_density is None
    assert x.prev_layer_topography is None
    assert x.e_test_R_ohm is None
    assert x.forced_measurement_flag is False
    assert x.mrr_lag is None
    assert x.consumable_usage_neighbors is None


def test_die_density_mean_out_of_range_warns():
    x_high = PTWVMInput(product_id="P1", layer="M3", die_density_mean=1.5)
    x_low = PTWVMInput(product_id="P1", layer="M3", die_density_mean=-0.1)
    assert any("die_density_mean" in w for w in validate_ptw_vm_input(x_high))
    assert any("die_density_mean" in w for w in validate_ptw_vm_input(x_low))


def test_die_density_mean_in_range_no_density_warning():
    x = PTWVMInput(product_id="P1", layer="M3", die_density_mean=0.5, local_density=0.4)
    assert not any("die_density_mean" in w for w in validate_ptw_vm_input(x))


def test_no_layout_or_timeseries_info_warns_npw_equivalent():
    x = PTWVMInput(
        product_id="P1", layer="M3", die_density_mean=0.5,
        forced_measurement_flag=False, mrr_lag=None, local_density=None,
    )
    warnings = validate_ptw_vm_input(x)
    assert any("NPW" in w for w in warnings)


def test_forced_measurement_flag_true_suppresses_npw_warning():
    x = PTWVMInput(
        product_id="P1", layer="M3", die_density_mean=0.5,
        forced_measurement_flag=True, mrr_lag=None, local_density=None,
    )
    warnings = validate_ptw_vm_input(x)
    assert not any("NPW" in w for w in warnings)


def test_mrr_lag_length_out_of_range_warns():
    x_empty = PTWVMInput(product_id="P1", layer="M3", die_density_mean=0.5, mrr_lag=[])
    x_too_long = PTWVMInput(
        product_id="P1", layer="M3", die_density_mean=0.5, mrr_lag=[1.0] * 12
    )
    assert any("mrr_lag" in w for w in validate_ptw_vm_input(x_empty))
    assert any("mrr_lag" in w for w in validate_ptw_vm_input(x_too_long))


def test_mrr_lag_length_in_range_no_warning():
    for n in (1, 5, 11):
        x = PTWVMInput(
            product_id="P1", layer="M3", die_density_mean=0.5, mrr_lag=[1.0] * n
        )
        assert not any("mrr_lag" in w for w in validate_ptw_vm_input(x))


def test_e_test_r_ohm_negative_warns():
    x = PTWVMInput(product_id="P1", layer="M3", die_density_mean=0.5, e_test_R_ohm=-5.0)
    assert any("e_test_R_ohm" in w for w in validate_ptw_vm_input(x))


def test_e_test_r_ohm_nonnegative_no_warning():
    x = PTWVMInput(product_id="P1", layer="M3", die_density_mean=0.5, e_test_R_ohm=42.0)
    assert not any("e_test_R_ohm" in w for w in validate_ptw_vm_input(x))


def test_is_npw_equivalent_true_when_both_layout_fields_absent():
    x = PTWVMInput(
        product_id="P1", layer="M3", die_density_mean=0.5,
        local_density=None, prev_layer_topography=None,
    )
    assert is_npw_equivalent(x) is True


def test_is_npw_equivalent_false_when_local_density_present():
    x = PTWVMInput(
        product_id="P1", layer="M3", die_density_mean=0.5,
        local_density=0.3, prev_layer_topography=None,
    )
    assert is_npw_equivalent(x) is False


def test_is_npw_equivalent_false_when_prev_layer_topography_present():
    x = PTWVMInput(
        product_id="P1", layer="M3", die_density_mean=0.5,
        local_density=None, prev_layer_topography={"step_height_nm": 12.0},
    )
    assert is_npw_equivalent(x) is False


def test_consumable_usage_neighbors_stored_and_retrieved():
    neighbors = {"pad_hours": 12.5, "conditioner_disk_count": 3.0}
    x = PTWVMInput(
        product_id="P1", layer="M3", die_density_mean=0.5,
        consumable_usage_neighbors=neighbors,
    )
    assert x.consumable_usage_neighbors == neighbors
    assert x.consumable_usage_neighbors["pad_hours"] == 12.5
