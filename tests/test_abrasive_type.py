"""The abrasive TYPE must change the answer — and say what it cannot change.

The bug this file exists to prevent
-----------------------------------
``slurry.abrasive.kind`` used to be accepted, stored, used only to look up a
density for the viscosity estimate, and otherwise discarded. Running
``examples/oxide_baseline.yaml`` with silica, ceria, alumina, zirconia and
diamond returned a bit-identical 1601.0 A/min five times. The owner's whole
reason for asking for per-abrasive treatment is that the differences between
those particles are too large to pool, so returning one number for all five was
answering a question nobody asked.

Equally important is the other half: where no published same-recipe comparison
exists, the simulator must NOT invent a ratio (a hardness ranking is not a rate
ranking) and must NOT fall back to a derived exponent that belongs to a
different abrasive. It has to say the axis is unevaluated.
"""
from __future__ import annotations

import math

import pytest

from cmp_sim.core.solver import simulate
from cmp_sim.core.state import (Abrasive, Disk, Pad, Recipe, Slurry, Tool,
                                Wafer)


def _run(kind, film="oxide", pack="oxide_silica", conc=12.0, d50=70.0):
    return simulate(Recipe(
        model="full",
        wafer=Wafer(film=film, diameter_mm=300, initial_thickness_nm=1000,
                    n_radial=21),
        slurry=Slurry(pack=pack, ph=10.5,
                      abrasive=Abrasive(kind=kind, conc_wt_pct=conc, d50_nm=d50)),
        pad=Pad(shore_d=57.0, groove_width_mm=0.5, groove_pitch_mm=2.0,
                groove_depth_mm=0.75),
        disk=Disk(),
        tool=Tool(pressure_psi=3.0, rpm_platen=66.31, rpm_head=66.31,
                  flow_ml_min=200, time_s=60)))


def _abr(result):
    return result.extras.get("abrasive_type") or {}


# ── the bug itself ───────────────────────────────────────────────────
def test_swapping_the_abrasive_changes_the_rate():
    """The regression test for the identical-five-numbers bug."""
    rates = {k: _run(k).mean_rr_angstrom_per_min
             for k in ("silica", "ceria", "alumina", "zirconia")}
    assert len(set(round(v, 3) for v in rates.values())) > 1, (
        "every abrasive returned the same removal rate, so the abrasive type is "
        f"still being discarded: {rates}")
    # Ceria is the one pairing with a published ratio, and it is faster.
    assert rates["ceria"] > rates["silica"], rates


def test_ceria_uses_the_published_ratio_and_names_it():
    """The only licensed rescale in the table, applied with its citation."""
    r = _run("ceria")
    assert r.factors.get("abrasive_type") == pytest.approx(3.0)
    info = _abr(r)
    assert info["relative_rate"] == pytest.approx(3.0)
    assert "10.1149/1.2949085" in (info["relative_rate_source"] or ""), info
    assert info["ranking_only"] is False


def test_an_unanchored_abrasive_says_the_scale_is_not_its_own():
    """No published ratio -> no invented one, and the run says so.

    Alumina on oxide has no same-tool comparison against colloidal silica in
    this corpus. The rate must not be rescaled by a hardness ratio, and the
    result must declare itself a ranking rather than an anchored prediction.
    """
    r = _run("alumina")
    info = _abr(r)
    assert info["ranking_only"] is True
    assert info["relative_rate"] is None
    assert "abrasive_type" not in r.factors, (
        "a rate factor was applied for an abrasive with no published ratio")
    joined = " ".join(r.warnings)
    assert "not the abrasive this pack was calibrated with" in joined
    assert "hardness ranking" in joined, (
        "the result must say WHY it refused to substitute hardness, or the "
        "refusal reads as a missing feature")


def test_hardness_order_is_never_used_as_a_rate_order():
    """Harder abrasive != faster. Diamond must not out-predict ceria here.

    Diamond is ~5x harder than ceria and has no oxide rate ratio, so if any
    hardness-based fallback ever creeps in, diamond will overtake ceria on oxide
    and this test will catch it.
    """
    assert _run("diamond").mean_rr_angstrom_per_min < _run("ceria").mean_rr_angstrom_per_min


# ── exponents are scoped to the abrasive, not the film ───────────────
def test_the_packs_exponents_are_withdrawn_not_reused_on_a_swap():
    """Silica's -0.05 must not be applied to a ceria or alumina run.

    Updated 2026-09-27: the SIZE exponent no longer withdraws for an abrasive
    that HAS measured sweeps of its own — it is now re-attributed to the
    material (``abrasive_effects.SIZE_EXPONENT_BY_ABRASIVE``), because the
    corpus shows the exponent transfers across films within one material
    (bouvet2002's silica near zero on Ti/W/oxide in the same runs) but never
    across materials (between-material stdev 0.51 vs within 0.16).

    Updated again 2026-09-28: the CONCENTRATION exponent no longer withdraws
    either, but for the OPPOSITE reason — the material hypothesis was tested on
    it (``tools/conc_derived_probe.py``) and FAILED (between/within only 1.6x,
    below the 2x bar set in advance), while the DERIVED surface-area law
    MRR ~ C**(1/3) lands on the corpus median (+0.33 over 16 sweeps, 13/16
    within 0.25) with no fitted constant. So it is supplied as a LAW, reported
    under ``derived`` rather than ``material_scoped`` so the two provenances can
    never be confused. Superseded reasoning, kept because it was the right call
    until the check was run: "no equivalent cross-film check exists for the
    concentration keys, so borrowing them would be an untested assumption."
    ``abrasive_conc_half_wt_pct`` still withdraws — it is a wt% with units, not
    an exponent, and the law above says nothing about it.
    """
    info = _abr(_run("alumina"))
    assert set(info["withdrawn"]) == {"abrasive_conc_half_wt_pct"}, info
    assert "abrasive_size_exponent" not in info["withdrawn"], info
    why = " ".join(info["withdrawn"].values())
    assert "split by ABRASIVE" in why and "colloidal_silica" in why
    # and the size exponent that replaced it is alumina's own, with its k
    assert info["overrides"]["abrasive_size_exponent"] == pytest.approx(0.28)
    assert "k=2" in info["material_scoped"]["abrasive_size_exponent"]
    # the concentration exponent is the DERIVED 1/3, declared as derived and
    # NOT as a material-scoped borrow
    assert info["overrides"]["abrasive_conc_exponent"] == pytest.approx(1 / 3)
    assert "abrasive_conc_exponent" in info["derived"]
    assert "abrasive_conc_exponent" not in info["material_scoped"], info


def test_the_derived_conc_exponent_is_abrasive_independent():
    """A LAW must give the same value for every abrasive; a borrow need not.

    This is the distinguishing test between the two provenance kinds now in
    play. ``SIZE_EXPONENT_BY_ABRASIVE`` is a re-attributed measurement and so
    MUST differ by material; ``DERIVED_CONC_EXPONENT`` is geometry and so must
    NOT. If a later change ever quietly makes the concentration value material-
    dependent, it has stopped being derived and this fails.
    """
    from cmp_sim.slurry.abrasive_effects import DERIVED_CONC_EXPONENT

    seen = {}
    for kind in ("alumina", "ceria", "zirconia", "diamond"):
        info = _abr(_run(kind))
        if "abrasive_conc_exponent" in info["overrides"]:
            seen[kind] = info["overrides"]["abrasive_conc_exponent"]
    assert seen, "no abrasive received the derived concentration exponent"
    assert len(set(seen.values())) == 1, seen
    assert next(iter(seen.values())) == pytest.approx(DERIVED_CONC_EXPONENT), seen
    # and the derivation, not just the number, must travel with it
    why = _abr(_run("ceria"))["derived"]["abrasive_conc_exponent"]
    assert "C**(1/3)" in why and "1.6x" in why, why


def test_a_withdrawn_axis_is_unevaluated_rather_than_silently_derived():
    """The trap: null was not neutral.

    A null ``abrasive_size_exponent`` used to select the DERIVED -0.84, whose
    sign was wrong for 8 of 10 measured sweeps. An abrasive with NO measured
    sweep anywhere must still report the composition axis as not applied rather
    than quietly filling it from the derivation. ``diamond`` is that case —
    ``alumina`` used to be, before its two sweeps were re-attributed to the
    material (see the test above).

    Updated 2026-09-28: ``chi_abrasive`` is now PRESENT for diamond, because the
    concentration axis is supplied by a derived law that needs no diamond sweep
    (DERIVED_CONC_EXPONENT). The SIZE axis is still withdrawn, and that is what
    this test now checks — per-axis rather than all-or-nothing. This is the real
    hole the change exposed: the old guard fired only when NO override existed,
    so once the conc law always supplied one, a withdrawn size exponent fell
    through as a null and luo_dornfeld read that null as "use the derived -0.84".
    A diamond run's rate moved 6.8x over a 10x size step before the per-axis
    neutralisation in ``solver._abrasive_hook`` was added.
    """
    r = _run("diamond")
    assert "chi_abrasive" in r.factors, (
        "the derived concentration law applies to any abrasive, so the factor "
        "must exist even when the size axis is withdrawn")
    joined = " ".join(r.warnings)
    assert "particle-SIZE axis was NOT applied" in joined, joined
    assert "wrong sign on 8 of 10" in joined, joined
    # the sister test below proves the withdrawal is real, not just announced


def test_size_has_no_effect_once_the_axis_is_withdrawn():
    """And it must be inert, not half-applied — for an unmeasured abrasive."""
    small = _run("diamond", d50=30.0).mean_rr_angstrom_per_min
    large = _run("diamond", d50=300.0).mean_rr_angstrom_per_min
    assert small == pytest.approx(large), (
        "the size axis was withdrawn, so it must not move the rate at all")


def test_a_measured_abrasive_carries_its_own_size_exponent_across_films():
    """The re-attribution, stated as behaviour rather than as a table.

    Swapping the oxide/silica pack's abrasive for alumina or ceria must move
    the rate with THAT material's measured exponent, not with silica's -0.13
    and not with a single shared constant. Ceria's +1.00 (son2021, r2 0.98) is
    ~3.6x steeper in log-slope than alumina's +0.28, so a 4x size step must
    separate them by much more than measurement noise.
    """
    def slope(kind):
        lo = _run(kind, d50=30.0).mean_rr_angstrom_per_min
        hi = _run(kind, d50=120.0).mean_rr_angstrom_per_min
        return math.log(hi / lo) / math.log(4.0)

    n_alumina, n_ceria = slope("alumina"), slope("ceria")
    assert n_alumina == pytest.approx(0.28, abs=0.03), n_alumina
    assert n_ceria == pytest.approx(1.00, abs=0.05), n_ceria
    assert n_ceria > 3 * n_alumina


def test_the_material_table_never_hides_how_thin_its_support_is():
    """A k=1 value must not read as well-supported.

    Ceria's +1.00 rests on ONE sweep. The provenance string must say so, and
    the table must carry k and the spread for every material so a future reader
    cannot mistake a single regression for a consensus.
    """
    from cmp_sim.slurry import abrasive_effects as ae

    for kind, row in ae.SIZE_EXPONENT_BY_ABRASIVE.items():
        assert row["k"] == len(row["sweeps"]), kind
        lo, hi = row["spread"]
        assert lo <= row["value"] <= hi, kind
        _, why = ae.material_size_exponent(kind)
        assert f"k={row['k']}" in why
        assert "NOT derived" in why, "the note must not claim this is physics"
    assert ae.material_size_exponent("zirconia") == (None, None), (
        "an abrasive with no measured sweep must return no exponent, not a "
        "derived fallback")


def test_the_matching_abrasive_still_responds_to_size_and_loading():
    """Withdrawal must not break the calibrated case it does not apply to."""
    small = _run("silica", d50=30.0).mean_rr_angstrom_per_min
    large = _run("silica", d50=300.0).mean_rr_angstrom_per_min
    assert small != pytest.approx(large), (
        "silica through the silica pack must keep its measured size response")
    lean = _run("silica", conc=1.0).mean_rr_angstrom_per_min
    rich = _run("silica", conc=20.0).mean_rr_angstrom_per_min
    assert rich > lean


# ── the reference declaration itself ─────────────────────────────────
def test_the_reference_abrasive_factor_is_exactly_one():
    """The project's central rule: a factor is 1.0 at the pack's reference.

    The pack's Kp already contains its own abrasive, so naming that abrasive
    must not rescale anything — otherwise the same physics is counted twice.
    """
    named = _run("silica")
    info = _abr(named)
    assert info["matches_reference"] is True
    assert "abrasive_type" not in named.factors
    # And leaving it unstated must give the identical answer, since the pack's
    # reference abrasive is what it was calibrated with either way.
    unstated = _run(None)
    assert named.mean_rr_angstrom_per_min == pytest.approx(
        unstated.mean_rr_angstrom_per_min)


def test_every_pack_declares_which_abrasive_it_was_calibrated_with():
    """Without it, an abrasive swap cannot be detected at all.

    A pack may declare ``null`` — SnAg does, because it has no Kp and therefore
    no calibration whose abrasive could be named — but it must declare the key,
    with a note saying why it is null.
    """
    from cmp_sim.core.params import available_packs, load_pack

    missing = []
    for name in available_packs():
        try:
            pack = load_pack(name)
        except Exception:
            continue
        if "kp_m_per_pa" not in pack.params:
            continue                      # base/infrastructure packs
        param = pack.params.get("reference_abrasive")
        if param is None:
            missing.append(name)
            continue
        if param.value is None:
            assert "TODO" in (param.note or ""), (
                f"pack '{name}' declares reference_abrasive: null with no "
                "TODO(owner) note saying why")
    assert not missing, (
        f"these packs cannot detect an abrasive swap: {missing}")


def test_a_declared_reference_abrasive_resolves_in_the_database():
    """A reference naming an abrasive the database does not know is a typo."""
    from cmp_sim.core.params import available_packs, load_pack
    from cmp_sim.slurry.abrasive_effects import canonical_kind

    bad = {}
    for name in available_packs():
        try:
            pack = load_pack(name)
        except Exception:
            continue
        param = pack.params.get("reference_abrasive")
        if param is None or param.value is None:
            continue
        if canonical_kind(str(param.value)) is None:
            bad[name] = param.value
    assert not bad, f"reference_abrasive not in the abrasive database: {bad}"


def test_an_unknown_abrasive_is_reported_not_treated_as_the_reference():
    r = _run("unobtainium")
    info = _abr(r)
    assert info["ranking_only"] is True
    assert any("is not in the abrasive database" in w for w in r.warnings)


def test_aliases_resolve_to_the_same_abrasive():
    """`ceo2` and `ceria` must not be two different slurries."""
    a = _run("ceria").mean_rr_angstrom_per_min
    b = _run("ceo2").mean_rr_angstrom_per_min
    assert a == pytest.approx(b)


def test_colloidal_and_fumed_silica_are_not_the_same_entry():
    """Different PSD and aggregate structure; the DB keeps them apart."""
    from cmp_sim.slurry.abrasive_effects import canonical_kind

    assert canonical_kind("colloidal_silica") == "colloidal_silica"
    assert canonical_kind("fumed_silica") == "fumed_silica"
    assert canonical_kind("silica") == "colloidal_silica"


# ── the ratio table's own discipline ────────────────────────────────
def test_a_ratio_measured_against_another_reference_is_refused_not_chained():
    """Chaining two ratios from two tools multiplies their errors.

    The W table holds a silica/alumina entry. Asking for silica on the OXIDE
    pack (reference colloidal_silica) must not pick it up, and asking on a pack
    whose reference does not match a declared ratio must refuse rather than
    rescale.
    """
    from cmp_sim.slurry import abrasive_effects as ae

    # ceria/colloidal_silica exists on oxide...
    hit = ae._relative_rate("oxide", "ceria", "colloidal_silica")
    assert hit[0] == pytest.approx(3.0)
    # ...but the same entry must not be served for a different reference.
    miss = ae._relative_rate("oxide", "ceria", "alumina")
    assert miss[0] is None
    assert "chaining ratios" in (miss[2] or "")


def test_every_filled_ratio_carries_a_source_and_a_reference():
    """A rate ratio without its reference abrasive is meaningless."""
    from cmp_sim.slurry.abrasive_effects import _db

    for film, row in (_db().get("relative_rate", {}) or {}).items():
        for kind, spec in (row or {}).items():
            assert "reference" in spec, f"{film}/{kind} has no reference abrasive"
            if spec.get("value") is not None:
                assert spec.get("source"), f"{film}/{kind} has a value but no source"
                assert spec.get("confidence") in {"literature", "vendor", "derived"}, spec
            else:
                assert "TODO" in (spec.get("note") or ""), (
                    f"{film}/{kind} is null without a TODO(owner) note")


# ---------------------------------------------------------------------------
# US5575885 Table 1 — a real matched comparison that is deliberately NOT applied
# ---------------------------------------------------------------------------
# Toshiba 1996, Cu slurry. One tool, one pad (SUBA800), one load (400 g/cm2),
# one chemistry (0.1 wt% aminoacetic acid + 13 wt% H2O2), ~9 wt% abrasive:
#
#     alumina 98.5 | colloidal silica 35.3 | ceria 31.1 | zirconia 22.1
#     no abrasive at all: 10.0        (all nm/min)
#
# It is the strongest four-abrasive matched table in the corpus, and it still
# cannot be used as a rate ratio, because the four abrasives are not
# size-matched: 30 / 740 / 1100 / 1300 nm. This simulator already models
# particle size as its own term, so a ratio carrying a hidden size penalty
# applies that penalty twice.
#
# That is not a theoretical objection. Applying 0.358 to a silica Cu recipe
# drove examples/cu_damascene.yaml to 677.9 A/min, under the published
# 1,000-12,000 A/min copper floor, and the engine's own plausibility gate
# caught it. These tests pin the decision so nobody "fixes" the nulls later
# without deconfounding the sizes first.

_US5575885 = {"alumina": 98.5, "colloidal_silica": 35.3,
              "ceria": 31.1, "zirconia": 22.1}


def _cu(kind):
    return _run(kind, film="cu", pack="cu_h2o2_bta", conc=9.0, d50=740.0)


def test_cu_ratios_are_recorded_but_not_applied():
    """The measurement is in the file, with its source — and stays null.

    A null here is a decision, not an omission, so it must carry both the
    number it declined to use and the reason.
    """
    from cmp_sim.slurry.abrasive_effects import _db

    spec_all = _db()["relative_rate"]["cu"]
    for kind in ("colloidal_silica", "ceria", "zirconia"):
        spec = spec_all[kind]
        assert spec["value"] is None, (
            f"{kind} was given a value; US5575885's abrasives span 30-1300 nm "
            "and the size term would be double-counted")
        assert "US5575885" in (spec.get("source") or ""), spec
        assert "NOT APPLIED" in spec["note"], spec


def test_cu_swaps_say_ranking_only():
    """With no usable ratio, a Cu abrasive swap must not claim an absolute rate."""
    for kind in ("colloidal_silica", "ceria", "zirconia"):
        at = _cu(kind).extras.get("abrasive_type") or {}
        assert at.get("ranking_only") is True, (kind, at)
        assert at.get("reference_kind") == "alumina", (kind, at)
        assert at.get("relative_rate") is None, (kind, at)


def test_cu_example_stays_inside_the_published_envelope():
    """The regression that caught the double-counting, kept as a test.

    examples/cu_damascene.yaml names silica explicitly, so it exercises the Cu
    swap path. 677.9 A/min was the broken value.
    """
    rate = _cu("colloidal_silica").mean_rr_angstrom_per_min
    assert rate > 1000.0, (
        f"{rate:.1f} A/min is below the published copper floor — a size-"
        "confounded ratio is being applied again")


def test_ceria_is_fast_on_oxide_and_not_on_cu():
    """The same particle must not carry one global 'strength' factor.

    Ceria is ~3x colloidal silica on oxide (Si-O-Ce bond formation) and ~0.88x
    on Cu, where that chemistry has nothing to grip. The oxide ratio is applied
    because its source is size-matched; the Cu one is not applied at all. A
    simulator storing one ceria factor would have to be wrong on one film.
    """
    oxide_ratio = (_run("ceria").mean_rr_angstrom_per_min
                   / _run("colloidal_silica").mean_rr_angstrom_per_min)
    assert oxide_ratio > 2.5, oxide_ratio
    assert (_cu("ceria").extras.get("abrasive_type") or {})["relative_rate"] is None
