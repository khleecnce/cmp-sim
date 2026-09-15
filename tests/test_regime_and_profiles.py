"""Situation detection and model profiles.

The design claim under test: the right model is chosen by the *situation*, not
by the film name. Different films in the same regime share a profile; one film
in different regimes does not.
"""
import pytest

from cmp_sim.core import profiles as pf
from cmp_sim.core import regime as rg
from cmp_sim.core.solver import simulate
from cmp_sim.core.state import (Abrasive, Disk, Pad, Recipe, Slurry, Tool, Wafer)


def _run(model="auto", film="oxide", pack="oxide_silica", pdens=None,
         psi=3.0, rpm=60.0, pad_hours=0.0, disk_hours=0.0, **slurry_kw):
    return simulate(Recipe(
        model=model,
        wafer=Wafer(film=film, n_radial=21, pattern_density=pdens),
        slurry=Slurry(pack=pack, **slurry_kw),
        pad=Pad(use_hours=pad_hours, groove_width_mm=0.5, groove_pitch_mm=2.0,
                groove_depth_mm=0.75),
        disk=Disk(hours_used=disk_hours),
        tool=Tool(pressure_psi=psi, rpm_platen=rpm, rpm_head=rpm, time_s=60)))


# ── material family beats hardness ───────────────────────────────────
def test_hardness_alone_cannot_separate_tungsten_from_oxide():
    """W (~4-7 GPa) and thermal oxide (~7-9 GPa) overlap in hardness but polish
    by different mechanisms, so the family has to decide the class."""
    assert rg.classify_film(6.0e9, "w") == "metal"
    assert rg.classify_film(8.0e9, "oxide") == "dielectric"


def test_soft_and_hard_metals_are_split_by_hardness_within_the_family():
    assert rg.classify_film(1.0e9, "cu") == "soft_metal"
    assert rg.classify_film(6.0e9, "w") == "metal"


def test_hard_semiconductors_are_classed_as_ceramic():
    assert rg.classify_film(28.0e9, "sic") == "hard_ceramic"
    assert rg.classify_film(11.0e9, "poly_si") == "semiconductor"


def test_unknown_material_is_reported_not_guessed():
    assert rg.classify_film(None, "unobtainium") == "unknown"


def test_pack_can_declare_the_family_explicitly():
    assert rg.classify_film(8.0e9, "whatever", pack_family="metal") == "metal"


# ── the other regime axes ────────────────────────────────────────────
def test_contact_branch_follows_the_stress_to_hardness_ratio():
    assert rg.classify_contact_branch(1.0e10, 5.0e9) == "plastic"
    assert rg.classify_contact_branch(1.0e9, 5.0e9) == "elastic"
    assert rg.classify_contact_branch(3.5e9, 5.0e9) == "transition"


def test_contact_branch_is_undetermined_without_the_softened_hardness():
    """Guessing it would silently decide the sign of the size exponent in P3."""
    assert rg.classify_contact_branch(1.0e10, None) == "unknown"


def test_lubrication_regimes_follow_lambda():
    assert rg.classify_lubrication(0.1) == "boundary"
    assert rg.classify_lubrication(2.0) == "mixed"
    assert rg.classify_lubrication(5.0) == "full_film"


def test_hard_ceramics_are_chemically_rate_limited():
    assert rg.classify_rate_limit("hard_ceramic", chemistry_active=False) == "chemical"
    assert rg.classify_rate_limit("soft_metal", chemistry_active=True) == "mixed"


# ── auto-selection ───────────────────────────────────────────────────
@pytest.mark.parametrize("film,pack,expected", [
    ("cu", "cu_h2o2_bta", "soft_metal_plastic"),
    ("w", "w_fe_oxidizer", "hard_metal_passivation"),
    ("oxide", "oxide_silica", "dielectric_blanket"),
    ("sic", "sic_ceria_h2o2", "chemically_limited"),
])
def test_auto_picks_the_profile_that_suits_the_situation(film, pack, expected):
    assert _run("auto", film=film, pack=pack).extras["profile"] == expected


def test_the_same_film_gets_a_different_profile_when_patterned():
    """The situation changed, not the material."""
    blanket = _run("auto", film="oxide", pack="oxide_silica").extras["profile"]
    patterned = _run("auto", film="oxide", pack="oxide_silica",
                     pdens=0.4).extras["profile"]
    assert blanket != patterned
    assert "patterned" in patterned


def test_different_films_in_the_same_regime_share_a_profile():
    """SiC here; any hard, inert material lands in the same place."""
    assert _run("auto", film="sic", pack="sic_ceria_h2o2",
                psi=5.5).extras["profile"] == "chemically_limited"


# ── overlays ─────────────────────────────────────────────────────────
def test_pad_wear_is_an_overlay_not_a_competing_profile():
    """A worn Cu wafer should not have to choose between modelling copper and
    modelling pad wear."""
    r = _run("auto", film="cu", pack="cu_h2o2_bta", pad_hours=0.15, disk_hours=40)
    assert r.extras["profile"].startswith("soft_metal_plastic")
    assert "wear" in r.extras["profile"]
    assert "pad_life" in r.extras


def test_overlays_stack_with_pattern():
    r = _run("auto", film="oxide", pack="oxide_silica", pdens=0.4,
             pad_hours=0.15, disk_hours=30)
    assert "wear" in r.extras["profile"]


# ── mismatch is reported ─────────────────────────────────────────────
def test_choosing_a_mismatched_profile_warns_and_suggests_a_better_one():
    r = _run("dielectric_blanket", film="cu", pack="cu_h2o2_bta", pdens=0.5)
    joined = " ".join(r.warnings)
    assert "does not match the detected situation" in joined
    assert "Consider" in joined


def test_turning_chemistry_off_on_a_chemically_limited_system_warns():
    r = _run("preston_baseline", film="sic", pack="sic_ceria_h2o2", psi=5.5)
    assert any("chemically rate-limited" in w for w in r.warnings)


def test_a_patterned_wafer_without_the_pattern_layer_warns():
    r = _run("mechanical_screening", film="oxide", pack="oxide_silica", pdens=0.4)
    assert any("patterned but" in w for w in r.warnings)


def test_an_explicitly_named_profile_is_respected_not_silently_overridden():
    """The user asked for that physics; we warn rather than substitute."""
    r = _run("preston_baseline", film="cu", pack="cu_h2o2_bta")
    assert r.extras["profile"] == "preston_baseline"
    assert r.factors == {}


# ── backward compatibility ───────────────────────────────────────────
@pytest.mark.parametrize("legacy", ["preston", "gw_preston", "full"])
def test_the_original_model_names_still_work(legacy):
    r = _run(legacy, film="oxide", pack="oxide_silica")
    assert r.mean_rr_angstrom_per_min > 0
    assert r.extras["profile"]


def test_preston_alias_still_means_preston_only():
    assert _run("preston", film="oxide", pack="oxide_silica").factors == {}


def test_unknown_profile_is_rejected_with_the_available_list():
    with pytest.raises(ValueError) as exc:
        _run("not_a_profile")
    msg = str(exc.value)
    assert "not_a_profile" in msg
    for name in ("auto", "soft_metal_plastic", "chemically_limited"):
        assert name in msg


# ── the report ───────────────────────────────────────────────────────
def test_the_situation_is_reported_so_the_user_can_audit_the_choice():
    s = _run("auto", film="cu", pack="cu_h2o2_bta").extras["situation"]
    for axis in ("film_class", "rate_limit", "contact_branch", "lubrication",
                 "load_regime", "topography", "pad_state"):
        assert axis in s
    assert s["metrics"]


def test_undetermined_axes_are_declared_rather_than_defaulted():
    r = _run("auto", film="cu", pack="cu_h2o2_bta")
    assert any("undetermined" in w for w in r.warnings)
