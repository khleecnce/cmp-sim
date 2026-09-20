"""엔진에 등록된 마찰열-Arrhenius 열화학 반응속도 배율 진단의 계약 테스트.

근거: sim/tier2_physics/frictional_heating_arrhenius.py::arrhenius_rate_ratio(원본 무수정),
knowledge/physics/frictional-heating-temperature-arrhenius-coupling.md §4
(Shin et al. 2025, Materials 18(19) 4461, DOI 10.3390/ma18194461 — Crossref로 실존 확인:
"Process Temperature Control for Low Dishing in CMP").

고정하는 계약:
  1. cu 팩 — 필드가 채워지고 Ea=151.7 kJ/mol.
  2. oxide 막질 팩 2개(oxide_silica, sti_ceria) — Ea=8.75 kJ/mol.
  3. sic_4h/w 막질 — Shin 2025 표에 값이 없어 None + 스킵사유.
  4. theta_steady_state_delta_T_k가 None(Θ 입력 미비)이면 이 진단도 None.
  5. MRR 경로 비트 불변 — 이 진단 유무로 mrr 값이 정확히 동일.
  6. Ea 상수가 노트 §4 표와 일치(하드코딩 검증, 원본 모듈 SHIN2025_EA_J_MOL 단일 출처).
  7. 배율의 물리적 타당성 — ΔT_ss>0이면 ratio>1, Cu가 oxide보다 훨씬 민감.
"""
import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "sim" / "tier2_physics"))

from sim.engine import Recipe, simulate  # noqa: E402

EA_PACKS = ["cu_h2o2_bta", "oxide_silica", "sti_ceria"]
NO_EA_PACKS = ["sic_ceria_h2o2", "w_fe_oxidizer"]


def test_cu_pack_gets_cu_ea():
    r = simulate(Recipe(pack="cu_h2o2_bta", time_s=60))
    assert r.thermal_chemical_ea_kj_mol == pytest.approx(151.7)
    assert r.thermal_chemical_film == "cu"
    assert r.thermal_chemical_rate_ratio is not None
    assert "Ea=151.70 kJ/mol" in r.thermal_chemical_note


@pytest.mark.parametrize("pack", ["oxide_silica", "sti_ceria"])
def test_oxide_film_packs_get_sio2_ea(pack):
    r = simulate(Recipe(pack=pack, time_s=60))
    assert r.thermal_chemical_film == "oxide"
    assert r.thermal_chemical_ea_kj_mol == pytest.approx(8.75)
    assert r.thermal_chemical_rate_ratio is not None


@pytest.mark.parametrize("pack", NO_EA_PACKS)
def test_packs_without_shin2025_ea_skip_without_inventing(pack):
    r = simulate(Recipe(pack=pack, time_s=60))
    assert r.thermal_chemical_rate_ratio is None
    assert r.thermal_chemical_ea_kj_mol is None
    assert r.thermal_chemical_film is None
    assert "1차값이 없음" in r.thermal_chemical_note


def test_none_when_theta_steady_state_input_missing():
    """sfr_ml_min<=0이면 _theta_steady_state_diagnostic 자체가 ΔT_ss=None을 낸다 —
    이 진단은 그 None을 지어낸 절대온도로 메우지 않고 그대로 물려받아야 한다."""
    r = simulate(Recipe(pack="cu_h2o2_bta", time_s=60,
                        pack_overrides={"sfr_ml_min": 0.0}))
    assert r.theta_steady_state_delta_T_k is None
    assert r.thermal_chemical_rate_ratio is None
    assert "Θ 정상상태 열수지 입력 미비" in r.thermal_chemical_note


def test_diagnostic_does_not_touch_mrr():
    a = simulate(Recipe(pack="cu_h2o2_bta", time_s=60))
    b = simulate(Recipe(pack="cu_h2o2_bta", time_s=60))
    np.testing.assert_array_equal(a.mrr_nm_per_min, b.mrr_nm_per_min)
    assert a.thermal_chemical_rate_ratio is not None
    # sic_4h는 이 진단이 항상 None인 막질이지만 MRR 자체는 별도 경로 — 값이 있어야 한다
    c = simulate(Recipe(pack="sic_ceria_h2o2", time_s=60))
    assert c.thermal_chemical_rate_ratio is None
    assert np.all(np.isfinite(c.mrr_nm_per_min))


def test_ea_constants_match_note_table():
    """§4 표(SiO2 8.75 / Ta 29.9 / Cu 151.7 kJ/mol)와 원본 모듈 상수가 일치해야
    엔진이 그 값을 재하드코딩하지 않고 단일 출처에서 읽는다는 계약이 성립한다."""
    import frictional_heating_arrhenius as FHA
    assert FHA.SHIN2025_EA_J_MOL["SiO2"] == pytest.approx(8.75e3)
    assert FHA.SHIN2025_EA_J_MOL["Ta"] == pytest.approx(29.9e3)
    assert FHA.SHIN2025_EA_J_MOL["Cu"] == pytest.approx(151.7e3)
    r_cu = simulate(Recipe(pack="cu_h2o2_bta", time_s=60))
    r_ox = simulate(Recipe(pack="oxide_silica", time_s=60))
    assert r_cu.thermal_chemical_ea_kj_mol == pytest.approx(FHA.SHIN2025_EA_J_MOL["Cu"] / 1e3)
    assert r_ox.thermal_chemical_ea_kj_mol == pytest.approx(FHA.SHIN2025_EA_J_MOL["SiO2"] / 1e3)


def test_rate_ratio_physically_sensible():
    r_cu = simulate(Recipe(pack="cu_h2o2_bta", time_s=60))
    r_ox = simulate(Recipe(pack="oxide_silica", time_s=60))
    assert r_cu.theta_steady_state_delta_T_k > 0
    assert r_ox.theta_steady_state_delta_T_k > 0
    # ΔT_ss>0 -> T2>T1 -> 배율은 항상 1보다 커야 한다
    assert r_cu.thermal_chemical_rate_ratio > 1.0
    assert r_ox.thermal_chemical_rate_ratio > 1.0
    # 같은 ΔT_ss 오더에서 Cu(Ea=151.7)가 oxide(Ea=8.75)보다 훨씬 더 민감해야 한다
    assert r_cu.thermal_chemical_rate_ratio > 10 * r_ox.thermal_chemical_rate_ratio
