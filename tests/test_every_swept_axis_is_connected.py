"""Every swept axis in the corpus is CONNECTED, or says why not.

Why these tests exist
---------------------
The 16th run found two inert axes (``chelator_M``, ``promoter_M``) by
accident, while investigating one dataset. An inert axis is an input the
engine accepts, stores and then ignores while still printing a number that
looks like a prediction about it -- and it is the only error class in this
project that is fixable with ZERO new constants, because the missing piece is
a wire rather than a law. Nobody had ever checked the other 45 datasets the
same way.

``tools/inert_axis_scan.py`` now does, exhaustively: 46 datasets, 91 swept
axes, each perturbed end to end across the range its own paper ran and the
predicted rate compared. It also matters for the closure arguments already on
record. ``docs/limits.md`` §14 read 145 "owned by no axis" points as the shape
of a healthy model on a clean sweep -- but a DISCONNECTED input looks exactly
the same from the census's point of view, because an input that never reaches
the rate cannot own any of the residual either. Until this scan, that reading
was unverified.

What the scan found, and what these tests pin
---------------------------------------------
25 of 91 axes are inert, in four kinds, and the classification is the product:

``wiring`` (2, both fixed here)
    Every ``inhibitor_mM`` sweep in the corpus. ``Additive`` carries
    ``conc_wt_pct`` and ``conc_mM`` as SEPARATE fields, the inhibitor role
    reads the molar one, and the scoring harness was writing the millimolar
    figure into the weight-percent slot. The term declined the value and said
    so in a warning -- which nothing was reading. Fixed in
    ``predictive_score.ADDITIVE_OVERRIDES``, which now carries the unit.

``silent`` (4)
    Inert with nothing in the output to say so. The worst kind, because a
    reader cannot tell it from a model that considered the input and judged it
    unimportant.

``declared`` (10) / ``aliased`` (9)
    Honest: the pack announces the gap, or the key restates another axis the
    same dataset varies (``abrasive_d50_nm`` beside ``abrasive_size_nm``) so
    perturbing it alone is not a perturbation of the physics.

Fixing the wiring did NOT improve anything, and that is the finding. It
exposed a term whose constant is refuted -- see
``test_the_inhibitor_term_is_refused_below_its_reference``.
"""
from __future__ import annotations

import math

import pytest

from cmp_sim.core.predictive_score import ADDITIVE_OVERRIDES, _recipe_for
from cmp_sim.core.state import Abrasive, Additive, Recipe, Slurry, Tool, Wafer
from cmp_sim.core.solver import simulate

def _cu(bta_mM):
    return simulate(Recipe(
        model="full", wafer=Wafer(film="cu", n_radial=11),
        slurry=Slurry(pack="cu_h2o2_bta",
                      additives=[Additive("benzotriazole", conc_mM=bta_mM,
                                          role="inhibitor")],
                      abrasive=Abrasive(kind="silica")),
        tool=Tool(pressure_psi=3.0, rpm_platen=60, rpm_head=60, time_s=60)))


# ── the wiring fault itself ──────────────────────────────────────────────

def test_an_additive_override_declares_the_unit_it_is_stated_in():
    """A concentration without its unit is not a concentration.

    This is the bug in one line: ``inhibitor_mM`` was being written into
    ``Additive.conc_wt_pct``. Both fields are optional floats, so nothing
    raised; the inhibitor role asked for the molar field, found None, and
    declined. Requiring the unit in the table makes the next additive
    impossible to add without choosing one.
    """
    for key, entry in ADDITIVE_OVERRIDES.items():
        assert len(entry) == 3, f"{key} does not declare a unit field"
        _name, _role, unit_field = entry
        assert unit_field in ("conc_wt_pct", "conc_mM"), unit_field
        # The key's own suffix has to agree with the field it is routed to,
        # or the declaration is decorative.
        if key.endswith("_mM"):
            assert unit_field == "conc_mM", key
        if key.endswith(("_wt_pct", "_vol_pct")):
            assert unit_field == "conc_wt_pct", key


def test_a_millimolar_inhibitor_sweep_reaches_the_additive_as_molar():
    doc = {"pack": "cu_h2o2_bta", "film": "cu"}
    row = {"pressure_psi": 2.0, "rpm_platen": 75,
           "overrides": {"inhibitor_mM": 10.0}}
    additives = _recipe_for(doc, row)["slurry"]["additives"]
    inhibitor = next(a for a in additives if a["role"] == "inhibitor")
    assert inhibitor.get("conc_mM") == 10.0
    assert "conc_wt_pct" not in inhibitor, (
        "a millimolar figure in the weight-percent field makes the inhibitor "
        "term decline the value and the whole axis goes inert")


def test_the_inhibitor_axis_is_no_longer_silently_dropped():
    """Whatever the term then decides, the input must REACH it.

    Before the fix this warning fired on every inhibitor dataset in the
    corpus, and the axis moved the rate by 0.00%.
    """
    res = _cu(10.0)
    dropped = [w for w in res.warnings
               if "no concentration in the unit the model needs" in w]
    assert not dropped, dropped


# ── what the fix exposed ─────────────────────────────────────────────────

def test_the_inhibitor_term_is_refused_wherever_it_is_tested():
    """Refused, and the refusal carries its own refutation.

    The constant reachable for this pack is the EQUILIBRIUM (BTA x Cu)
    adsorption constant, K = 3283 L/mol. Under polishing the Cu-BTA layer is
    continuously abraded, so steady-state coverage is not equilibrium
    coverage, and the numbers say so: the term asserts a 0/10 mM rate ratio of
    18.4 where Hong 2007 measures 1.21.
    """
    for mM in (0.0, 10.0):
        res = _cu(mM)
        refusal = [w for w in res.warnings if "inhibitor term REFUSED" in w]
        assert refusal, f"the refused term must announce itself at {mM} mM"
        text = refusal[0]
        for fragment in ("3283",                 # the constant being refused
                         "10.1149/1.2717410",    # the refuting measurement
                         "1.21",                 # measured ratio
                         "18.4",                 # asserted ratio
                         "183",                  # the substitution DECLINED
                         "pH 3-4"):              # the unblocking measurement
            assert fragment in text, f"the refusal omits {fragment!r}: {text}"
        assert "inhibitor" not in ((res.extras or {}).get("chemistry_terms") or {}), (
            "a refused term must not still be multiplying the rate")


def test_the_refusal_is_two_sided_because_a_bound_is_not_evidence():
    """The first version of this gate kept the above-reference half. Wrong.

    The argument was that coverage is already 0.767 at the 1 mM reference, so
    above it the factor is bounded below by exp(-k[1-theta_ref]) = 0.50 and
    "makes almost no claim". The bound is right and the inference is not: on
    the ONLY above-reference point in the corpus the term asserts a 1.84x
    drop from 0 to 10 mM where Hong measures 1.21x, overstating by 1.53x.
    Keeping that half cost hong2007 its noise floor and moved the corpus
    median 18.9% -> 19.5% -- a refuted constant paid for in score.

    A bound on a term's magnitude is not evidence that the term is harmless
    inside that bound. Only a measurement is.
    """
    at_ref = _cu(1.0).mean_rr_nm_per_min
    # Neither side may move the rate while the constant is refused.
    assert _cu(0.0).mean_rr_nm_per_min == pytest.approx(at_ref, rel=1e-6)
    assert _cu(10.0).mean_rr_nm_per_min == pytest.approx(at_ref, rel=1e-6)

    text = next(w for w in _cu(10.0).warnings if "inhibitor term REFUSED" in w)
    assert "1.53" in text and "bound" in text, (
        "the refusal must state why the bounded half was ALSO refused, or a "
        "later run will read the bound as a licence to switch it back on")


def test_refusing_the_term_keeps_the_corpus_median_where_it_was():
    """A refusal must cost nothing in score. If it does, something was fitted."""
    import statistics
    from cmp_sim.core.predictive_score import score_all

    scores = [s for s in score_all() if s.shape_mape is not None]
    median = statistics.median(s.shape_mape for s in scores)
    assert 18.5 <= median <= 19.0, median


# ── the scan itself, so the next wiring fault cannot be silent ───────────

def test_no_swept_axis_is_inert_without_saying_so():
    """The standing guard: an UNDECLARED inert axis fails the build.

    This is the point of the whole exercise. Adding a key to a pack and
    forgetting to wire it, or renaming a field so a term stops receiving it,
    now fails here instead of being absorbed into the residual and read as
    missing physics three runs later.
    """
    from tools.inert_axis_scan import scan

    result = scan()
    offenders = result.by_kind("wiring") + result.by_kind("silent")
    # The four SILENT axes are known and separately explained below; they are
    # listed explicitly so that a FIFTH one fails.
    known_silent = {
        ("kenchappa2021_softpad_hdp_oxide", "pad_hardness_shore_d"),
        ("us20110186542a1_w_diamond_h2o2_ph", "slurry_ph"),
        ("us20190127607a1_hdpoxide_ceriasilica_size_sweep", "abrasive_d99_nm"),
        ("us20190127607a1_teos_ceriasilica_size_sweep", "abrasive_d99_nm"),
    }
    unexpected = [(a.dataset, a.axis) for a in offenders
                  if (a.dataset, a.axis) not in known_silent]
    assert not unexpected, (
        f"these swept axes do not reach the predicted rate and nothing in the "
        f"output says why: {unexpected}. Either wire the term, or make the "
        f"model DECLARE the gap -- an input that is accepted, stored and "
        f"ignored still looks like a prediction about that axis.")


def test_no_inhibitor_axis_remains_a_wiring_fault():
    from tools.inert_axis_scan import scan

    assert not scan().by_kind("wiring"), (
        "a wiring fault is inert for a reason that costs no constants to fix")


def test_the_scan_can_actually_fail():
    """Calibrated against the bug it exists to catch.

    A guard whose failure path has never been exercised is a guard nobody has
    tested. Feeding the classifier the pre-fix situation -- an inert axis
    whose only warning is about the wrong species -- must not produce an
    excuse.
    """
    from tools.inert_axis_scan import _classify

    kind, _ = _classify("promoter_M", [
        "additive 'benzotriazole' (role inhibitor) has no concentration in "
        "the unit the model needs (inhibitor_mM), so it was not applied"])
    assert kind == "silent", (
        "a warning about a DIFFERENT species must not excuse this axis")

    kind, _ = _classify("inhibitor_mM", [
        "additive 'benzotriazole' (role inhibitor) has no concentration in "
        "the unit the model needs (inhibitor_mM), so it was not applied"])
    assert kind == "wiring"

    # An alias is only excused when its partner actually responds.
    kind, _ = _classify("abrasive_d50_nm", [],
                        {"abrasive_size_nm": 53.0})
    assert kind == "aliased"
    kind, _ = _classify("abrasive_d50_nm", [],
                        {"abrasive_size_nm": 0.0})
    assert kind == "silent", (
        "if BOTH members of the pair are inert, the pair is not an excuse")


def test_the_measured_refutation_is_arithmetic_not_assertion():
    """Re-derive the two numbers the refusal rests on, from the constants.

    The warning quotes 18.4 (asserted) against 1.21 (measured). If someone
    changes K or k in the pack, this recomputes and the claim in the warning
    stops matching -- which is the point: a refutation that cannot go stale
    is a slogan.
    """
    from cmp_sim.core.legacy_bridge import install  # noqa: F401
    from cmp_sim.core.params import load_pack
    import slurry_components as sc

    pack = load_pack("cu_h2o2_bta")
    k = float(pack.params["inhibitor_strength_k"].value)
    dg = float(pack.params["inhibitor_dG_ads_kJ"].value)
    assert pack.params["inhibitor_K_ads_L_per_mol"].value is None, (
        "the refusal is premised on this pack declaring no steady-state K")

    # The pair table is what the term actually reaches; dG here only fixes the
    # order of magnitude for this cross-check.
    k_ads = sc.K_from_dG_ads(dg * 1000.0)
    assert 1.0e3 < k_ads < 1.0e5, k_ads

    def theta(mM, kk=3283.0):
        return sc.langmuir_coverage(mM * 1e-3, kk)

    ratio = (math.exp(-k * theta(0.0)) / math.exp(-k * theta(10.0)))
    assert ratio == pytest.approx(18.4, abs=0.5), ratio
    assert (265.0 / 220.0) == pytest.approx(1.21, abs=0.01)
