"""Deciding elastic vs plastic particle contact without a circular input.

The blocker
-----------
``contact_branch`` was ``unknown`` for every film, which left the sign of the
particle-size exponent in P3 undetermined — the simulator could not say whether
larger abrasive polishes faster or slower. The obvious fix, comparing a particle
contact stress against the film hardness, is circular: the Luo-Dornfeld
formulation *defines* the contact stress as the hardness.

The non-circular route
----------------------
Compare LOADS rather than stresses, using the pad hardness — a directly
measured quantity — as the cap on what a pad asperity can apply:

    P_Y   = (pi^3/48) * Hc^3/Ec^2 * R^2     yield load (Hertz + Tresca)
    P_max = pi * R^2 * Hp                   pad-limited load
    plastic when P_max > P_Y:
    Lambda = 48 * Hp * Ec^2 / (pi^2 * Hc^3) > 1

R cancels, so the branch is particle-size independent — matching Eusner's
measurement that scratch width and depth are independent of polishing pressure
and pad topography.

Sources, all read from the original PDFs rather than a summary:
* Eusner, Saka, Chun et al., JES 156(7) H528-H534 (2009): Eq. 3 for P_Y,
  Table I for moduli and hardnesses, Fig. 15 for the pad hardness distribution
  (36 measurements, mean 0.05 GPa, s.d. 0.06), Table IV for Hp,max = 0.31 GPa.
* Saka, Eusner & Chun, CIRP Annals 57, 341-344 (2008): same Eq. 3, and
  "Ra = 5 um, la = 100 um, Ep = 0.5 GPa and Hp = 0.05 GPa" for an IC1000.
"""
import math

import pytest

from cmp_sim.core.solver import simulate
from cmp_sim.core.state import Disk, Pad, Recipe, Slurry, Tool, Wafer

PI = math.pi


def lam(hardness_gpa, modulus_gpa, pad_hardness_gpa):
    """Lambda, computed here independently of the implementation."""
    hc = hardness_gpa * 1e9
    ec = modulus_gpa * 1e9
    hp = pad_hardness_gpa * 1e9
    return 48.0 * hp * ec ** 2 / (PI ** 2 * hc ** 3)


def _run(film, pack):
    return simulate(Recipe(
        model="auto", wafer=Wafer(film=film, n_radial=11),
        slurry=Slurry(pack=pack),
        pad=Pad(groove_width_mm=0.5, groove_pitch_mm=2.0, groove_depth_mm=0.75),
        disk=Disk(),
        tool=Tool(pressure_psi=3.0, rpm_platen=60, rpm_head=60, time_s=60)))


def _situation(film, pack):
    return _run(film, pack).extras.get("situation") or {}


# ── the algebra ──────────────────────────────────────────────────────
def test_the_criterion_reproduces_the_published_table():
    """Values computed from Eusner Table I (E, H) plus Fig. 15 / Table IV (Hp)."""
    assert lam(3.24, 128, 0.05) == pytest.approx(117, rel=0.02)
    assert lam(3.24, 128, 0.31) == pytest.approx(726, rel=0.02)
    assert lam(1.22, 128, 0.05) == pytest.approx(2194, rel=0.02)
    assert lam(15.0, 92, 0.05) == pytest.approx(0.61, rel=0.03)
    assert lam(8.0, 69.8, 0.05) == pytest.approx(2.31, rel=0.03)


def test_the_branch_does_not_depend_on_particle_size():
    """R cancels exactly. If a future edit reintroduces an R dependence the
    criterion stops being the size-independent statement it is derived as."""
    for r_nm in (10, 50, 200, 1000):
        r = r_nm * 1e-9
        p_yield = (PI ** 3 / 48.0) * (3.24e9) ** 3 / (128e9) ** 2 * r ** 2
        p_max = PI * r ** 2 * 0.05e9
        assert (p_max > p_yield) is True, f"branch flipped at R = {r_nm} nm"


def test_the_criterion_discriminates_rather_than_always_saying_plastic():
    """A rule that returns one answer for every input has decided nothing."""
    assert lam(1.22, 128, 0.05) > 3.0          # copper: firmly plastic
    assert lam(15.0, 92, 0.05) < 1.0           # silica at 15 GPa: elastic
    assert lam(15.6, 128, 0.05) == pytest.approx(1.05, rel=0.05)  # on the line


def test_comparing_pad_hardness_to_film_hardness_directly_is_the_wrong_test():
    """The trap: Hp = 0.05 GPa is a load over the particle CROSS-SECTION, not
    over the ~100x smaller particle/film contact area. The naive comparison
    calls copper elastic, which contradicts the measured scratches."""
    naive_says_elastic = 0.05 < 1.22
    assert naive_says_elastic, "premise of the trap no longer holds"
    assert lam(1.22, 128, 0.05) > 1.0, (
        "the load criterion should say plastic where the naive one says elastic")


# ── wired into the engine ────────────────────────────────────────────
def test_copper_is_now_decided_rather_than_unknown():
    situation = _situation("cu", "cu_h2o2_bta")
    assert situation["contact_branch"] == "plastic"
    assert situation["metrics"]["pad_limited_plasticity_lambda"] > 3.0


def test_oxide_is_reported_as_marginal_not_forced_to_a_side():
    """Oxide CMP genuinely runs near the scratching threshold: it is the one
    material in the source paper's Table IV with no measurable scratches."""
    situation = _situation("oxide", "oxide_silica")
    assert situation["contact_branch"] == "transition"
    marginal = [u for u in situation["undetermined"] if "marginal" in u]
    assert marginal, "a boundary case was reported without saying it is one"
    # The caveat must say the limit is physical, not clerical: no published
    # nanoindentation reaches the sub-nm depth an abrasive works at, and
    # Lambda goes as 1/H^3, so 2x in hardness is 8x here.
    assert "sub-nm" in marginal[0] or "1/hardness^3" in marginal[0], (
        "the caveat reads as if a tidier number would settle it")


def test_the_engine_agrees_with_the_independent_calculation():
    situation = _situation("cu", "cu_h2o2_bta")
    from cmp_sim.core.solver import resolve

    rr = resolve(Recipe(
        model="auto", wafer=Wafer(film="cu", n_radial=11),
        slurry=Slurry(pack="cu_h2o2_bta"),
        pad=Pad(groove_width_mm=0.5, groove_pitch_mm=2.0, groove_depth_mm=0.75),
        disk=Disk(),
        tool=Tool(pressure_psi=3.0, rpm_platen=60, rpm_head=60, time_s=60)))
    expected = lam(
        float(rr.p_or("film_surface_hardness_pa", None)
              or rr.p_or("film_bulk_hardness_pa", None)) / 1e9,
        float(rr.p_or("film_youngs_modulus_pa", None)) / 1e9,
        float(rr.p_or("pad_wet_nanohardness_pa", None)) / 1e9)
    assert situation["metrics"]["pad_limited_plasticity_lambda"] == pytest.approx(
        expected, rel=1e-3)


def test_the_note_records_the_inputs_it_used():
    """A branch with no visible inputs cannot be checked by a reviewer."""
    notes = " ".join(_run("cu", "cu_h2o2_bta").notes)
    assert "pad-limited load criterion" in notes
    assert "Particle size cancels" in notes


# ── what the branch does NOT unblock, and why ────────────────────────
def test_the_branch_alone_does_not_settle_the_size_exponent():
    """Deciding the branch was supposed to fix the sign of the particle-size
    exponent. It does not, and pretending otherwise would be the more
    comfortable lie.

    The exponent relations assume 0 <= 1 - alpha*chi <= 1. The plastic branch
    (alpha = 3/2) violates that whenever chi > 2/3, and copper's measured load
    sharing gives chi = 1.0, so alpha*chi = 1.5. Taken literally n_C = -0.5,
    i.e. "more abrasive removes less", which the model's own bound forbids.

    alpha and chi are not independently adjustable - chi comes from the
    measured area-pressure exponent - so the engine reports the branch and
    leaves the exponents on the inherited elastic values with confidence
    'unverified' rather than publishing a negative concentration exponent.
    """
    result = _run("cu", "cu_h2o2_bta")
    situation = result.extras.get("situation") or {}
    assert situation["contact_branch"] == "plastic"

    regime = result.extras.get("abrasive_regime") or {}
    assert regime["n_conc"] > 0, (
        f"n_C = {regime['n_conc']} implies more abrasive removes less")
    assert regime["confidence"] == "unverified", (
        "the exponents are presented as settled while alpha and chi conflict")


def test_the_conflict_between_alpha_and_chi_is_explained_not_hidden():
    notes = " ".join(_run("cu", "cu_h2o2_bta").notes)
    assert "breaks the structural bound" in notes
    assert "more abrasive removes less" in notes
    assert "concentration sweep" in notes, (
        "the note does not say what measurement would resolve it")


def test_the_structural_bound_is_what_it_claims_to_be():
    """0 <= 1 - alpha*chi <= 1, checked directly."""
    for alpha, chi, ok in [(2 / 3, 1.0, True), (1.5, 1.0, False),
                           (1.5, 0.5, True), (1.5, 2 / 3, True)]:
        within = 0.0 <= 1.0 - alpha * chi <= 1.0
        assert within is ok, f"alpha={alpha}, chi={chi}"


# ── the circular-value trap in the hardness source ───────────────────
def test_the_copper_surface_hardness_is_the_independent_column():
    """Ihnfeldt's dissertation reports TWO hardness columns for the same
    surfaces. H (nanoindentation, ~1-3 GPa here) is a direct measurement.
    H_N (>12 GPa) is BACK-SOLVED from Luo-Dornfeld to reproduce the measured
    removal rate, so using it to decide the contact branch would be circular in
    exactly the way this whole criterion exists to avoid.
    """
    from cmp_sim.core.params import load_pack

    param = load_pack("cu_h2o2_bta").param("film_surface_hardness_pa")
    gpa = float(param.value) / 1e9
    assert 1.0 < gpa < 6.0, (
        f"{gpa:.2f} GPa is outside the measured nanoindentation band and sits "
        "in the back-solved H_N range")
    assert "H_N" in (param.note or ""), (
        "the note does not warn about the circular H_N column in the same table")


def test_no_pack_carries_a_back_solved_hardness():
    """A film surface hardness above ~12 GPa on a metal would be the H_N
    signature. Ceramics legitimately sit there, so only metals are checked."""
    from cmp_sim.core.params import available_packs, load_pack

    metals = {"cu_h2o2_bta", "w_fe_oxidizer", "snag_solder"}
    for name in available_packs():
        if name not in metals:
            continue
        try:
            pack = load_pack(name)
        except Exception:
            continue
        value = pack.get_or("film_surface_hardness_pa", None)
        if value:
            assert float(value) / 1e9 < 12.0, (
                f"{name} declares a {float(value)/1e9:.1f} GPa metal surface "
                "hardness, which is the back-solved H_N range")


def test_the_particle_contact_stress_that_does_exist_is_not_luo_dornfeld_derived():
    """Some packs do carry a contact stress. It is only usable if it came from
    somewhere other than 'stress = hardness'."""
    from cmp_sim.core.params import load_pack

    param = load_pack("oxide_silica").param("particle_contact_stress_pa")
    source = ((param.source or "") + (param.note or "")).lower()
    assert "cook" in source and "hertz" in source, (
        "the oxide contact stress no longer cites an independent Hertzian "
        f"derivation: {source[:120]}")
    hardness = float(load_pack("oxide_silica").get_or("film_bulk_hardness_pa", 0))
    assert float(param.value) != hardness, (
        "contact stress equals the hardness, which is the circular assumption")


# ── the inheritance trap this exposed ────────────────────────────────
def test_sic_does_not_inherit_the_silica_modulus():
    """SiC's lineage is SiC -> sti_ceria -> oxide_silica, so adding SiO2's
    E = 92 GPa to the silica packs propagated it to SiC, whose real modulus is
    ~450. Lambda goes as E^2, so the inherited value made SiC look elastic on a
    number that was never about SiC. The same route once carried the oxide Kp
    into this pack and over-predicted SiC by 128x.
    """
    from cmp_sim.core.params import load_pack

    pack = load_pack("sic_ceria_h2o2")
    assert pack.get_or("film_youngs_modulus_pa", None) is None, (
        "SiC is again inheriting a modulus from the silica packs")


def test_sic_reports_the_branch_as_undetermined_and_says_why():
    situation = _situation("sic", "sic_ceria_h2o2")
    assert situation["contact_branch"] == "unknown"
    assert "pad_limited_plasticity_lambda" not in situation["metrics"]


def test_a_blocked_parameter_is_still_a_documented_parameter():
    """Declaring it null with a reason is the honest record; deleting it would
    look like an oversight and invite someone to re-add the inherited value."""
    from cmp_sim.core.params import load_pack

    param = load_pack("sic_ceria_h2o2").param("film_youngs_modulus_pa")
    assert param.value is None
    assert "TODO(owner)" in (param.note or "")
    assert "450" in (param.note or ""), (
        "the note does not say what the right order of magnitude is")
