"""metal_contamination_surface.py 회귀 테스트.

두 지식노트의 python verify 블록 assert 값을 그대로 재현한다 (임의 임계값 없음, 새 숫자 없음):
  knowledge/cmp/post-cmp-metallic-contamination-sources.md §6 (A)(B)(C)
  knowledge/cmp/metal-contamination-device-impact-irds-limits.md §7 (A)(B)
"""
import math

import pytest

import metal_contamination_surface as mcs


# ---------------------------------------------------------------------------
# sources.md §6(A) — Si(100) 단분자층 밀도와 허용치 비율
# ---------------------------------------------------------------------------

def test_si100_monolayer_density_order():
    """N_ML = 2/a² (a=5.431 Å) ≈ 6.78e14 atoms/cm² — 노트 assert 6.5e14 < N_ML < 7.0e14."""
    N_ML = mcs.monolayer_density_si100()
    assert 6.5e14 < N_ML < 7.0e14
    assert N_ML == pytest.approx(2.0 / (5.431e-8) ** 2)


def test_tolerance_fraction_of_monolayer_order():
    """허용치 1e10 / N_ML ≈ 1.5e-5 ML — 노트 assert 1e-6 < frac < 1e-4."""
    N_ML = mcs.monolayer_density_si100()
    frac = mcs.fraction_of_monolayer(1e10, N_ML)
    assert 1e-6 < frac < 1e-4


# ---------------------------------------------------------------------------
# sources.md §6(B) — 슬러리 유래 Fe(출처 불명·미검증, 2차요약 오귀속 — Seo 2001 본문에 Fe값 없음, 2026-09-09 정정) vs 허용치
# ---------------------------------------------------------------------------

def test_fe_asdep_and_cleaned_vs_tolerance():
    """세정 전 Fe 1.5e12/1e10 > 50배, 세정 후 1e11/1e10 > 1배 (노트 §6(B) assert)."""
    assert mcs.precmp_to_spec_ratio(mcs.SEO2001["fe_asdep_atoms_cm2"]) > 50
    assert mcs.precmp_to_spec_ratio(mcs.SEO2001["fe_clean_atoms_cm2"]) > 1


# ---------------------------------------------------------------------------
# sources.md §6(C) — Cu²⁺ Boltzmann 표면과잉의 pH 방향
# ---------------------------------------------------------------------------

def test_thermal_voltage_reference_25p69_mV():
    """kT/e @298.15 K = 25.69 mV (노트 §6(C) 상수)."""
    assert mcs.thermal_voltage_mV() == pytest.approx(25.69, abs=1e-9)
    assert mcs.thermal_voltage_mV(298.15) == pytest.approx(25.69, abs=1e-9)


def test_boltzmann_enrichment_unity_at_iep():
    """ζ=0(IEP, pH~2) → 정전구동력 없음 → 배율 1 (노트 assert |x-1|<1e-9)."""
    assert abs(mcs.boltzmann_surface_enrichment(0.0) - 1.0) < 1e-9


def test_boltzmann_enrichment_monotonic_with_ph():
    """ζ 0 → -20 → -40 → -60 mV (pH↑) 순으로 Cu²⁺ 농축 단조증가 (노트 assert)."""
    vals = [mcs.boltzmann_surface_enrichment(z) for z in mcs.ZETA_MV_BY_PH.values()]
    assert all(vals[i] < vals[i + 1] for i in range(len(vals) - 1))


def test_boltzmann_enrichment_neutral_ph_over_20x():
    """중성(ζ=-40 mV), z=+2 → exp(80/25.69) ≈ 22배 > 20 (노트 assert)."""
    e = mcs.boltzmann_surface_enrichment(-40.0)
    assert e > 20
    assert e == pytest.approx(math.exp(-2 * (-40.0) / 25.69))


# ---------------------------------------------------------------------------
# irds-limits.md §7(A) — Wang et al. 2024 (doi:10.3390/electronics13122391)
# ---------------------------------------------------------------------------

def test_wang2024_pmos_fe_early_failure_ratio():
    """PMOS Fe 오염 조기파괴 8/71 = 0.1127 (노트 assert |x-0.1127|<0.001)."""
    fr = mcs.goi_early_failure_ratio(8, 71)
    assert abs(fr - 0.1127) < 0.001
    assert fr == mcs.goi_early_failure_ratio(mcs.WANG2024["n_fail_pmos_fe"],
                                             mcs.WANG2024["n_total"])


def test_wang2024_nmos_negligible_and_pmos_early_below_half_spec():
    """노트 §7(A) 나머지 assert: NMOS ΔV_bd <1%, PMOS 조기파괴 V_bd(1.5V) < 스펙(4.14V)/2."""
    w = mcs.WANG2024
    nmos_delta_pct = abs(w["vbd_nmos_fe_v"] - w["vbd_ref_v"]) / w["vbd_ref_v"] * 100
    assert nmos_delta_pct < 1.0
    assert w["vbd_pmos_fe_early_v"] < w["vbd_spec_v"] * 0.5


# ---------------------------------------------------------------------------
# irds-limits.md §7(B) — ITRS 2.0 각주[14] FEP 스펙 1E10 vs 세정전 W-CMP Fe
# ---------------------------------------------------------------------------

def test_itrs_fep_spec_default_is_1e10():
    """스펙 기본값 = ITRS 2.0 각주[14] 1E10 atoms/cm² = Lv1-1 잠정치 1e10 (노트 assert ==)."""
    assert mcs.ITRS_FEP_SPEC_ATOMS_CM2 == 1e10
    assert mcs.precmp_to_spec_ratio(1e10) == pytest.approx(1.0)


def test_precmp_w_cmp_fe_to_itrs_spec_100_to_200x():
    """세정전 W-CMP Fe 1e12~2e12 / 1e10 → 100~200배 (노트 assert 90~110·190~210)."""
    r_lo = mcs.precmp_to_spec_ratio(1e12)
    r_hi = mcs.precmp_to_spec_ratio(2e12)
    assert 90 <= r_lo <= 110
    assert 190 <= r_hi <= 210


# ---------------------------------------------------------------------------
# 입력 가드 (문헌값 아님 — 순수함수 계약)
# ---------------------------------------------------------------------------

def test_input_guards_raise():
    with pytest.raises(ValueError):
        mcs.monolayer_density_si100(0.0)
    with pytest.raises(ValueError):
        mcs.fraction_of_monolayer(1e10, 0.0)
    with pytest.raises(ValueError):
        mcs.thermal_voltage_mV(0.0)
    with pytest.raises(ValueError):
        mcs.goi_early_failure_ratio(8, 0)
    with pytest.raises(ValueError):
        mcs.goi_early_failure_ratio(72, 71)
    with pytest.raises(ValueError):
        mcs.precmp_to_spec_ratio(1e12, 0.0)
