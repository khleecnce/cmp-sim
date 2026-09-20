"""sim/calibration/normalize.py 회귀 테스트.

문헌 근거: knowledge/data/wafer-coordinate-units-outlier-cleaning.md §1-3, §5(verify 블록).
검증 문헌값은 그 노트 §5의 assert들을 그대로 승격한 것이다.
"""
import math

import numpy as np
import pytest

from sim.calibration.normalize import (
    NOTCH_ANGLES_RAD,
    apply_edge_exclusion,
    flag_outliers,
    to_canonical_coords,
    to_canonical_units,
)
from sim.metrics.uniformity import compute_metrics_points


# ---- 1. psi -> kPa (NIST SP811 정의값) -------------------------------------------------

def test_psi_to_kpa_nist_definition():
    out = to_canonical_units(1.0, "psi")
    assert out.canonical_unit == "kPa"
    assert abs(out.value - 6.894757) < 1e-6
    out3 = to_canonical_units(3.0, "psi")
    assert abs(float(out3.value) - 20.684271) < 1e-3


# ---- 2. Å/s -> nm/min ------------------------------------------------------------------

def test_angstrom_per_s_to_nm_per_min():
    out = to_canonical_units(1.0, "angstrom_per_s")
    assert out.canonical_unit == "nm_per_min"
    assert abs(float(out.value) - 6.0) < 1e-12


def test_angstrom_to_nm():
    out = to_canonical_units(1.0, "angstrom")
    assert out.canonical_unit == "nm"
    assert abs(float(out.value) - 0.1) < 1e-15


def test_rpm_to_m_per_s():
    # r=0.15 m (300mm 엣지), N=100 rpm -> v=2*pi*r*N/60 ~= 1.5708 m/s (노트 §5.1)
    out = to_canonical_units(100.0, "rpm", radius_m=0.15)
    assert out.canonical_unit == "m_per_s"
    assert abs(float(out.value) - 1.5708) < 1e-3
    v_expect = 2 * math.pi * 0.15 * (100 / 60)
    assert abs(float(out.value) - v_expect) < 1e-9


def test_rpm_requires_radius():
    with pytest.raises(ValueError):
        to_canonical_units(100.0, "rpm")


def test_unsupported_unit_rejected():
    with pytest.raises(ValueError):
        to_canonical_units(1.0, "furlong_per_fortnight")


# ---- 3. MAD 이상치 상수/판정 (Leys et al. 2013) -----------------------------------------

def test_mad_constant_and_detection_leys2013():
    rng = np.random.default_rng(0)
    base = rng.normal(500, 3, 48)
    x = np.append(base, 560.0)  # 이상치 1개

    flags = flag_outliers(x, method="mad")  # default k=2.5
    assert flags.k == 2.5
    assert flags.is_outlier[-1] == True  # noqa: E712 — 이상치 검출됨
    assert flags.reason[-1] is not None
    # 정상점은 대부분 플래그되지 않아야 함
    assert flags.is_outlier[:-1].sum() <= 2

    med = np.median(x)
    mad = 1.4826 * np.median(np.abs(x - med))
    mean, sd = x.mean(), x.std(ddof=0)
    z_mad = abs(560 - med) / mad
    z_sigma = abs(560 - mean) / sd
    assert z_mad > z_sigma  # MAD가 sigma보다 이상치에 강건(마스킹 안 됨)
    assert z_mad > 2.5


def test_mad_default_not_sigma():
    # 노트 §3.2: sigma 기반은 default가 아니어야 함
    flags = flag_outliers([1, 2, 3, 4, 100])
    assert flags.method == "mad"


def test_iqr_outliers():
    x = np.array([10.0, 11.0, 12.0, 13.0, 14.0, 100.0])
    flags = flag_outliers(x, method="iqr")  # default k=1.5
    assert flags.k == 1.5
    assert flags.is_outlier[-1] == True  # noqa: E712
    assert not flags.is_outlier[:-1].any()


def test_outliers_are_flagged_not_deleted():
    x = np.array([1.0, 2.0, 3.0, 1000.0])
    flags = flag_outliers(x, method="mad")
    assert len(flags.values) == len(x)
    assert np.array_equal(flags.values, x)  # 원값 그대로 보존


# ---- 4. 엣지 제외(EE) 면적 비율 (SEMI M1 FQA) --------------------------------------------

def test_edge_exclusion_300mm_3mm_ratio():
    # 300mm 웨이퍼, 균일 분포 반경으로 몬테카를로 근사 -> 1-((150-3)/150)^2 ~= 3.96%
    rng = np.random.default_rng(1)
    n = 2_000_000
    r2 = rng.uniform(0, 150.0 ** 2, n)
    r = np.sqrt(r2)  # 면적 균일 샘플링
    flags = apply_edge_exclusion(r, ee_mm=3.0, D_mm=300.0)
    frac = flags.excluded.mean()
    expected = 1 - ((150 - 3) / 150) ** 2
    assert abs(expected - 0.0396) < 0.001
    assert abs(frac - expected) < 0.001


def test_edge_exclusion_missing_vs_excluded_distinct():
    r = np.array([10.0, 140.0, 148.0, np.nan, 149.9])
    flags = apply_edge_exclusion(r, ee_mm=3.0, D_mm=300.0)
    # index 3: NaN -> missing=True, excluded=False
    assert flags.missing[3] == True  # noqa: E712
    assert flags.excluded[3] == False  # noqa: E712
    # index 4: r=149.9 > 147 (FQA 경계) -> excluded=True, missing=False
    assert flags.excluded[4] == True  # noqa: E712
    assert flags.missing[4] == False  # noqa: E712
    # index 0: 안쪽 -> 둘 다 False
    assert not flags.missing[0] and not flags.excluded[0]
    # missing과 excluded는 동시에 True일 수 없음 (서로 다른 사유, 노트 §3.1)
    assert not np.any(flags.missing & flags.excluded)


# ---- 5. 좌표 변환: 가역성(원본 복원 가능) + 다이 아핀 행부호 반전 ------------------------------

def test_polar_to_canonical_cartesian_matches_definition():
    r = np.array([0.1, 0.05])
    theta = np.array([0.3, -1.2])
    out = to_canonical_coords((r, theta), notch_dir="Bottom", kind="polar")
    # Bottom 기준 방향은 회전 없음(phi=0) -> 그냥 x=r cos, y=r sin
    assert np.allclose(out.x_m, r * np.cos(theta))
    assert np.allclose(out.y_m, r * np.sin(theta))


def test_die_affine_row_sign_flip():
    # 노트 §5.2와 동일한 파라미터: 기준다이(5,5)->중심(0,0), 이미지행 6 -> 물리 -y
    coords = ([5, 5], [5, 6], 10.0, 10.0, 5, 5, 0.0, 0.0)
    out = to_canonical_coords(coords, notch_dir="Bottom", kind="die")
    assert out.x_m[0] == 0.0 and out.y_m[0] == 0.0
    assert out.y_m[1] == -10.0, out.y_m[1]  # 행 부호 반전 확인


def test_coords_reversible_via_metadata():
    """정준화는 원 좌표계·notch_dir을 메타로 보존해 원본 복원이 가능해야 한다(노트 §0)."""
    x0 = np.array([0.02, -0.03, 0.01])
    y0 = np.array([0.04, 0.01, -0.02])
    for notch_dir in ("Bottom", "Right", "Top", "Left"):
        out = to_canonical_coords((x0, y0), notch_dir=notch_dir, kind="cartesian")
        assert out.source_notch_dir == notch_dir
        assert out.source_kind == "cartesian"
        # 메타(notch_dir)로부터 정방향과 같은 회전각을 재계산해 역회전하면 원본이 복원되어야 함
        phi = -NOTCH_ANGLES_RAD[out.source_notch_dir]
        cos_p, sin_p = np.cos(-phi), np.sin(-phi)
        x_restored = out.x_m * cos_p - out.y_m * sin_p
        y_restored = out.x_m * sin_p + out.y_m * cos_p
        assert np.allclose(x_restored, x0, atol=1e-12)
        assert np.allclose(y_restored, y0, atol=1e-12)


# ---- 6. 노치 회전 불변성: TTV·WIWNU는 불변, 공간귀속은 달라짐 (uniformity.py 실호출) ----------

def test_notch_rotation_invariance_ttv_wiwnu_real_call():
    rng = np.random.default_rng(3)
    r = np.sqrt(rng.uniform(0, 0.15 ** 2, 200))
    th = rng.uniform(-np.pi, np.pi, 200)
    x = r * np.cos(th)
    y = r * np.sin(th)
    v = 500 + 40 * (r / 0.15) + 6 * np.cos(th)

    m_bottom = compute_metrics_points(x, y, v)

    for notch_dir in ("Right", "Top", "Left"):
        out = to_canonical_coords((x, y), notch_dir=notch_dir, kind="cartesian")
        m_rot = compute_metrics_points(out.x_m, out.y_m, v)
        assert abs(m_rot.ttv_nm - m_bottom.ttv_nm) < 1e-9
        assert abs(m_rot.wiwnu_3sigma_pct - m_bottom.wiwnu_3sigma_pct) < 1e-9
        # 그러나 실제 좌표 귀속은 달라져야 함(공간 분석은 오염됨, 노트 §4-1)
        assert not np.allclose(out.x_m, x) or not np.allclose(out.y_m, y)


# ---- 7. 단위 10배 -> CV(비율지표) 불변, TTV(절대지표)는 10배 (uniformity.py 실호출) -----------

def test_unit_10x_cv_invariant_ttv_scales():
    rng = np.random.default_rng(3)
    r = np.sqrt(rng.uniform(0, 0.15 ** 2, 200))
    th = rng.uniform(-np.pi, np.pi, 200)
    x = r * np.cos(th)
    y = r * np.sin(th)
    v_nm = 500 + 40 * (r / 0.15) + 6 * np.cos(th)

    m0 = compute_metrics_points(x, y, v_nm)

    # v를 Å로 착각(=10x 오류) — to_canonical_units로 Å->nm 변환하면 원래 nm값의 1/10이 되지만,
    # 여기서는 "단위 슬립" 자체의 영향(10x 오염)을 재현하기 위해 값을 10배로 둔다(노트 §5.5와 동일 실험).
    v_10x = v_nm * 10
    m1 = compute_metrics_points(x, y, v_10x)

    assert abs(m1.ttv_nm - 10 * m0.ttv_nm) < 1e-6
    assert abs(m1.cv_pct - m0.cv_pct) < 1e-9
    assert abs(m1.wiwnu_3sigma_pct - m0.wiwnu_3sigma_pct) < 1e-9

    # to_canonical_units로 Å->nm 변환한 값을 넣으면 원래 m0와 완전히 같아야 함(무손실 복원)
    v_from_angstrom = to_canonical_units(v_10x, "angstrom").value  # v_10x는 "Å로 잘못 읽은" nm값이라 가정
    assert np.allclose(v_from_angstrom, v_nm)
    m2 = compute_metrics_points(x, y, v_from_angstrom)
    assert abs(m2.ttv_nm - m0.ttv_nm) < 1e-9
    assert abs(m2.cv_pct - m0.cv_pct) < 1e-9
