"""chelation_surface_charge.py 회귀 테스트.

knowledge/cmp/post-cmp-adsorption-cleaning-chemistry.md §6 python verify 블록의 assert 값을
그대로 재현한다 (임의 임계값 없음, 새 숫자 없음): (A) Davies 보정, (B) K'(pH), (C) IEP/DHF pH.
"""
import chelation_surface_charge as csc


# ---------------------------------------------------------------------------
# §6 (A) — Davies 이온세기 보정
# ---------------------------------------------------------------------------

def test_davies_correction_matches_literature():
    """Davies 보정 Fe-EDTA~=25.13, Cu-EDTA~=18.79 (문헌 25.1/18.75와 0.3 log 이내)."""
    zL_edta = csc.LIGAND_CHARGE["EDTA"]
    pred_fe = csc.logK_at_I(*csc.EDTA_LOGK_I0["Fe3+"], zL_edta)
    pred_cu = csc.logK_at_I(*csc.EDTA_LOGK_I0["Cu2+"], zL_edta)
    assert abs(pred_fe - 25.13) < 0.05
    assert abs(pred_cu - 18.79) < 0.05
    assert abs(pred_fe - csc.EDTA_LOGK_LIT_I01["Fe3+"]) < 0.3
    assert abs(pred_cu - csc.EDTA_LOGK_LIT_I01["Cu2+"]) < 0.3


def test_selectivity_order_fe_cu_ca():
    """선택성 순서 Fe3+ > Cu2+ > Ca2+ (EDTA·Cit, pH11 조건부 상수에서도 유지)."""
    for ligand in ("EDTA", "Cit"):
        kfe = csc.chelation_conditional_logK(ligand, "Fe3+", 11.0)
        kcu = csc.chelation_conditional_logK(ligand, "Cu2+", 11.0)
        kca = csc.chelation_conditional_logK(ligand, "Ca2+", 11.0)
        assert kfe > kcu > kca


# ---------------------------------------------------------------------------
# §6 (B) — 조건부 안정도상수 K'(pH)
# ---------------------------------------------------------------------------

def test_conditional_logK_monotonic_in_pH():
    """pH 3 < 7 < 11 에서 K'(pH) 단조증가 (전 리간드x금속 조합)."""
    for ligand in ("EDTA", "Cit"):
        for metal in ("Fe3+", "Cu2+", "Ca2+"):
            k3 = csc.chelation_conditional_logK(ligand, metal, 3.0)
            k7 = csc.chelation_conditional_logK(ligand, metal, 7.0)
            k11 = csc.chelation_conditional_logK(ligand, metal, 11.0)
            assert k3 < k7 < k11


def test_citrate_ph3_ca_uncomplexed_fe_complexed():
    """pH3 시트르산-Ca logK'<0 (착화 불가), pH3 시트르산-Fe3+ logK'>0."""
    kca = csc.chelation_conditional_logK("Cit", "Ca2+", 3.0)
    kfe = csc.chelation_conditional_logK("Cit", "Fe3+", 3.0)
    assert kca < 0
    assert kfe > 0


def test_free_cu_fraction_suppressed_at_ph11_50mM():
    """pH11, 50mM 킬레이트에서 유리 Cu2+ 분율 < 1e-5 (EDTA/Cit 둘 다)."""
    for ligand in ("EDTA", "Cit"):
        k_prime = csc.chelation_conditional_logK(ligand, "Cu2+", 11.0)
        frac = csc.free_metal_fraction(k_prime, 0.050)
        assert frac < 1e-5


# ---------------------------------------------------------------------------
# §6 (C) — DHF pH, IEP·표면전하 부호
# ---------------------------------------------------------------------------

def test_dhf_ph_in_expected_range():
    """DHF 0.5wt% pH ~= 1.5~2.5 범위 (HF pKa=3.17 기준)."""
    pH_dhf = csc.hf_solution_pH(0.5)
    assert 1.5 < pH_dhf < 2.5


def test_all_oxides_positive_at_dhf_pH():
    """pH_dhf에서 SiO2/CeO2/Al2O3 전부 '+'."""
    pH_dhf = csc.hf_solution_pH(0.5)
    for oxide in csc.IEP:
        assert csc.oxide_surface_charge_sign(oxide, pH_dhf) == "+"


def test_all_oxides_negative_at_ph11():
    """pH 11에서 세 산화물 전부 '-'."""
    for oxide in csc.IEP:
        assert csc.oxide_surface_charge_sign(oxide, 11.0) == "-"


def test_ceo2_positive_sio2_negative_at_ph5():
    """pH 5에서 CeO2 '+' / SiO2 '-' (이부호)."""
    assert csc.oxide_surface_charge_sign("CeO2", 5.0) == "+"
    assert csc.oxide_surface_charge_sign("SiO2", 5.0) == "-"


def test_ceo2_iep_within_ederer2025_measured_range():
    """CeO2 IEP 6.8이 Ederer 2025 실측범위 5.21~9.40 안."""
    lo, hi = csc.CEO2_IEP_LIT_RANGE
    assert lo <= csc.IEP["CeO2"] <= hi
