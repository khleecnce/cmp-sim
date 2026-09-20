"""recipe_conversion_factor.py 회귀 테스트.

knowledge/cmp/product-wafer-proxy-metrics-virtual-metrology.md §6 python verify
블록 (A)의 assert 값을 그대로 재현한다 (임의 임계값 없음, 새 숫자 없음):
US20060116785A1 표 2 변환계수 STI=1.12, IMD=1.41.
"""
import recipe_conversion_factor as rcf


# ---------------------------------------------------------------------------
# §6 (A) — US20060116785A1 식(1)·표 2 변환계수 재현
# ---------------------------------------------------------------------------

def test_conversion_factor_ild_to_sti_matches_patent_table2():
    """ILD->STI 변환계수 ~= 1.12 (US20060116785A1 표 2, 노트 assert 허용오차 0.01)."""
    cf = rcf.recipe_conversion_factor(rcf.RECIPE_TABLE["ILD"], rcf.RECIPE_TABLE["STI"])
    assert abs(cf - 1.12) < 0.01


def test_conversion_factor_ild_to_imd_matches_patent_table2():
    """ILD->IMD 변환계수 ~= 1.41 (US20060116785A1 표 2, 노트 assert 허용오차 0.01)."""
    cf = rcf.recipe_conversion_factor(rcf.RECIPE_TABLE["ILD"], rcf.RECIPE_TABLE["IMD"])
    assert abs(cf - 1.41) < 0.01


def test_conversion_factor_self_to_self_is_one():
    """같은 레시피끼리 비교하면 변환계수는 1.0 (F(x)/F(x))."""
    for name, recipe in rcf.RECIPE_TABLE.items():
        assert rcf.recipe_conversion_factor(recipe, recipe) == 1.0


def test_conversion_factor_within_patent_claim6_range():
    """청구항 6 보고 범위(0.5~2.0) 안에 표 1 레시피 조합이 든다 (US20060116785A1)."""
    cf_sti = rcf.recipe_conversion_factor(rcf.RECIPE_TABLE["ILD"], rcf.RECIPE_TABLE["STI"])
    cf_imd = rcf.recipe_conversion_factor(rcf.RECIPE_TABLE["ILD"], rcf.RECIPE_TABLE["IMD"])
    assert 0.5 <= cf_sti <= 2.0
    assert 0.5 <= cf_imd <= 2.0


def test_work_function_positive_for_recipe_table_entries():
    """표 1 레시피(ILD/STI/IMD) 입력에서 work_function은 항상 양수."""
    for recipe in rcf.RECIPE_TABLE.values():
        F = rcf.work_function(recipe["downforce_psi"], recipe["slurry_flow_ml_min"],
                               recipe["platen_rpm"])
        assert F > 0


def test_work_function_positive_over_reasonable_range():
    """다운포스 2~8 psi, 유량 50~300 ml/min, 회전 20~150 rpm 범위에서 work_function 양수."""
    for X in (2.0, 4.0, 8.0):
        for Y in (50.0, 150.0, 300.0):
            for Z in (20.0, 63.0, 150.0):
                assert rcf.work_function(X, Y, Z) > 0
