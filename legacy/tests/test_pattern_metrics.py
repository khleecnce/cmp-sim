"""sim/metrics/pattern_metrics.py 회귀 테스트.

앵커는 knowledge/cmp/pattern-metrics-dishing-erosion-stepheight.md §6의 python verify 블록
(ITRS 2007 Table INTC2a, Taylor Hobson ISO 5436-1형 스텝하이트, SunEdison/Corning ROA 규약,
Pan 1999 vs ITRS-2007 dishing 비율)에서 검증된 수치를 그대로 회귀 앵커로 쓴다. 노트의 코드를
그대로 옮기지 않고 sim/metrics/pattern_metrics.py의 재사용 가능한 함수 시그니처로 재현한다.
"""
import numpy as np
import pytest

from sim.metrics.pattern_metrics import (
    step_height_iso5436,
    dishing_erosion_from_profile,
    roa,
    itrs_allowance,
    residual_metal_fraction,
    remaining_thickness,
)


# ---------------------------------------------------------------------------
# (A) ITRS 2007 Table INTC2a — erosion 허용치 = 10%×배선높이 (노트 §6 (A))
# ---------------------------------------------------------------------------

M1_PITCH_NM = [136, 118, 104, 90, 80, 72, 64, 56, 50]
M1_AR = [1.7, 1.8, 1.8, 1.8, 1.8, 1.8, 1.9, 1.9, 1.9]
ITRS_EROSION_NM = [12, 11, 9, 8, 7, 6, 6, 5, 5]


def test_itrs_allowance_matches_2007_erosion_table_within_half_nm():
    for pitch, ar, expected in zip(M1_PITCH_NM, M1_AR, ITRS_EROSION_NM):
        calc = itrs_allowance(pitch, ar)
        assert abs(calc - expected) <= 0.5, (pitch, ar, calc, expected)


# ---------------------------------------------------------------------------
# (C) ISO 5436-1형 최소제곱 스텝하이트 — 합성 50 nm 스텝 회수 (노트 §6 (C))
# ---------------------------------------------------------------------------

def test_step_height_iso5436_recovers_synthetic_50nm_step():
    rng = np.random.default_rng(1)
    x = np.linspace(0, 200.0, 2001)
    h_true = 50.0
    delta = np.where((x > 70) & (x < 130), -1.0, 1.0)
    z = 1.0 * x + 5.0 + (h_true / 2) * delta + rng.normal(0, 0.3, x.size)

    result = step_height_iso5436(x, z, delta, exclude_transition_width=5.0)
    assert abs(result.step_height_nm - h_true) < 1.0
    assert abs(result.slope - 1.0) < 0.05


def test_step_height_iso5436_curvature_removal_cuts_error_from_taylor_hobson_10pct():
    # Taylor Hobson: 2 µm 기판 곡률 위 9 µm step — 곡률 미제거 시 "약 10%" 자릿수 오차 (노트 §6 (C'))
    xs = np.linspace(0, 10.0, 4001)  # mm
    sag_nm = 2.0e3 * (1 - (2 * (xs - 5) / 10) ** 2)
    step_region = (xs > 4) & (xs < 6)
    h_true = 9.0e3  # nm
    z = sag_nm + h_true * step_region
    delta = np.where(step_region, 1.0, -1.0)

    naive = step_height_iso5436(xs, z, delta, remove_curvature=False)
    err_naive = abs(naive.step_height_nm - h_true) / h_true
    assert 0.03 < err_naive < 0.30

    corrected = step_height_iso5436(xs, z, delta, remove_curvature=True)
    err_corrected = abs(corrected.step_height_nm - h_true) / h_true
    assert err_corrected < 0.01
    assert err_corrected < err_naive / 5


# ---------------------------------------------------------------------------
# (D) ROA — 규약 의존성, 같은 프로파일에서 두 규약이 크게 다름 (노트 §1.5, §6(D))
# ---------------------------------------------------------------------------

def test_roa_requires_explicit_convention():
    r = np.linspace(100, 150, 501)
    t = np.zeros_like(r)
    with pytest.raises(TypeError):
        roa(r, t)  # convention 인자 없이 호출 불가
    with pytest.raises(ValueError):
        roa(r, t, "made_up_convention")


def test_roa_conventions_diverge_over_30pct_on_same_rolloff_profile():
    # 300 mm 웨이퍼(R=150mm), 엣지 3mm 이내에 국한된 롤오프 — 근거리(Corning)/원거리(SunEdison)
    # 규약이 같은 프로파일에서 크게 다른 값을 준다(노트가 보인 "규약 없는 ROA는 비교 불가"의 재현).
    r = np.linspace(100, 150, 5001)
    onset, width, amplitude = 147.0, 3.0, 1000.0
    t = np.where(r > onset, -amplitude * ((r - onset) / width) ** 2, 0.0)

    roa_sun = roa(r, t, "sunedison_300mm")
    roa_cor = roa(r, t, "edge_3_6mm")

    assert roa_sun < 0 and roa_cor < 0  # 둘 다 롤오프 부호(음수)
    reldiff = abs(roa_sun - roa_cor) / max(abs(roa_sun), abs(roa_cor))
    assert reldiff > 0.30


# ---------------------------------------------------------------------------
# (E) dishing_erosion_from_profile — Pan 1999 100 µm dishing vs ITRS-2007 요구 (노트 §6 (E))
# ---------------------------------------------------------------------------

def test_dishing_erosion_synthetic_100um_trench_vs_itrs2007():
    itrs2007_dishing_100um_nm = 24.0  # ITRS 2007 INTC2a "100 µm wide feature" 2007년 열
    pan_dishing_100um_nm = 50.0       # Pan 1999: "approx. 500 Å dishing over a 100 µm trench"

    x = np.linspace(0, 300.0, 3001)  # µm: field(0-100) - 100µm trench(100-200) - field(200-300)
    field_mask = (x < 100) | (x > 200)
    line_mask = (x >= 100) & (x <= 200)
    z = np.where(line_mask, -pan_dishing_100um_nm, 0.0)

    result = dishing_erosion_from_profile(
        x, z, field_mask, line_mask, array_mask=line_mask, stage="post_clear_dishing"
    )

    assert abs(result.dishing_nm - pan_dishing_100um_nm) < 1e-9
    assert result.reference == "field_oxide"
    assert result.stage == "post_clear_dishing"

    ratio = result.dishing_nm / itrs2007_dishing_100um_nm
    assert 1.5 < ratio < 3.0  # 노트 §6(E): 1999년 공정 실측이 2007년 요구치의 1.5~3배


def test_dishing_erosion_field_loss_switches_reference_to_as_deposited():
    x = np.linspace(0, 300.0, 301)
    field_mask = (x < 100) | (x > 200)
    line_mask = (x >= 100) & (x <= 200)
    z = np.where(line_mask, -10.0, 0.0)

    result = dishing_erosion_from_profile(
        x, z, field_mask, line_mask, array_mask=line_mask, field_loss_nm=5.0
    )
    assert result.reference == "as_deposited"
    assert abs(result.total_loss_nm - (result.dishing_nm + result.erosion_nm + 5.0)) < 1e-9


# ---------------------------------------------------------------------------
# (5) residual — 결함량(이산) vs 잔여 막두께(연속), 노트 §1.4
# ---------------------------------------------------------------------------

def test_residual_metal_fraction_is_defect_incidence_not_continuous():
    clean = np.zeros(100)
    assert residual_metal_fraction(clean) == 0.0

    with_residue = np.zeros(100)
    with_residue[:3] = 1.0
    assert residual_metal_fraction(with_residue) == pytest.approx(0.03)


def test_remaining_thickness_is_continuous_subtraction():
    assert remaining_thickness(500.0, 50.0) == 450.0
    assert remaining_thickness(500.0, 0.0) == 500.0
