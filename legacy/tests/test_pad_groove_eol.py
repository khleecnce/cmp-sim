"""pad_groove_eol.py 회귀 테스트 — _self_test()의 항목을 pytest화.

노트 knowledge/materials/pad-thickness-groove-depth-monitoring-replacement-economics.md
§5 (A)(B) verify 블록의 값만 재현한다(새 문헌 숫자 없음). §5 (D) 경제성 계산은
옮기지 않는다(PROFILE.md가 sim/에 넣지 말라고 명시).
"""
import pad_groove_eol as pg


def test_cumulative_wear_case_I():
    assert abs(pg.cumulative_wear_um(43.4, 16.0) - 694.4) < 0.5


def test_cumulative_wear_case_II():
    assert abs(pg.cumulative_wear_um(22.2, 20.0) - 444.0) < 0.5


def test_case_I_wear_matches_groove_depth_lower_bound():
    cum_I = pg.cumulative_wear_um(43.4, 16.0)
    groove_lo = 750.0
    assert 0.5 * groove_lo < cum_I < 1.3 * groove_lo


def test_case_II_groove_not_exhausted():
    cum_II = pg.cumulative_wear_um(22.2, 20.0)
    assert pg.groove_exhausted(cum_II, 750.0) is False


def test_groove_exhausted_boundary_crossed():
    assert pg.groove_exhausted(800.0, 750.0) is True


def test_groove_eol_hours_case_I():
    assert abs(pg.groove_eol_hours(43.4, 750.0) - 17.28) < 0.01


def test_replacement_time_glazing_earlier():
    groove_eol = pg.groove_eol_hours(43.4, 750.0)
    assert abs(pg.replacement_time_hours(15.0, groove_eol) - 15.0) < 1e-9


def test_replacement_time_groove_earlier():
    groove_eol = pg.groove_eol_hours(43.4, 750.0)
    assert abs(pg.replacement_time_hours(20.0, groove_eol) - groove_eol) < 1e-9


def test_replacement_time_near_coincident_failure_modes():
    """Son & Lee(2021) Case I처럼 glazing(~16h)과 groove_eol(17.28h)이 근접한 경우
    OR 조건이 놓치지 않고 더 이른 쪽(glazing)을 반환하는지 확인."""
    glazing_eol_caseI = 16.0
    groove_eol_caseI = pg.groove_eol_hours(43.4, 750.0)
    assert abs(groove_eol_caseI - glazing_eol_caseI) < 2.0
    rep = pg.replacement_time_hours(glazing_eol_caseI, groove_eol_caseI)
    assert abs(rep - glazing_eol_caseI) < 1e-9
