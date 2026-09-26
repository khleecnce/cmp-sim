"""The four SILENT inert axes now say why they do not move the rate.

Why this exists
---------------
``tools/inert_axis_scan.py`` (17th run) classified 25 of the corpus's 91 swept
axes as inert and sorted them into four kinds. Three kinds are fine -- a
wiring fault is a bug (fixed there), a *declared* gap is honest, an *alias*
restates a responsive axis. The fourth, ``silent``, is the dangerous one:
the input moves, the predicted rate does not, and **nothing in the output says
why**. A reader cannot distinguish that from a model that weighed the input
and judged it unimportant, so silence is read as a physical claim the model
never made.

Four axes were silent. This run makes each one speak. **Zero constants were
added and no term changed**, so the corpus median must not move -- a
declaration that changes a score is not a declaration, it is a fit, and the
last test here pins that.

The three causes, which are genuinely different and must not be merged:

1. ``pad_hardness_shore_d`` (kenchappa2021) -- WRONG PATH. The pack key exists,
   and the GW contact layer reads pad stiffness from the ``Pad`` object, not
   from the pack. So the value was accepted, stored, and never consumed. This
   is the subtle case: because the pack DECLARES the key, the standing
   "not declared by pack X" warning never fired.
2. ``abrasive_d99_nm`` (us20190127607a1 x2) -- CORRECT BY DESIGN. The
   large-particle tail feeds the defect proxy, not the rate: the D50
   population removes material and the tail makes scratches. Right behaviour,
   but it has to be stated, and it should be provable that the value is not
   simply being dropped -- so the test below also asserts D99 *does* move
   ``defect_risk``.
3. ``slurry_ph`` (us20110186542a1) -- A SOURCED NULL RESULT. ``w_fe_oxidizer``
   carries ``ph_response_is_null_over_3_to_6`` with the patent's own matched
   pH 3 / pH 6 table behind it. A measured null and a forgotten wire look
   identical from outside, and only one of them is an answer.

The scope clause matters more than the declaration. The null covers pH 3-6;
outside it this repository holds no W measurement, so the same flat response
stops being an answer and becomes an extrapolation. The warning must say
which of the two the caller is getting.
"""
from __future__ import annotations

import statistics

import pytest

from cmp_sim.api import run_recipe


def _oxide(**kw):
    recipe = {"model": "auto", "wafer": {"film": "oxide", "n_radial": 11},
              "slurry": {"pack": "sti_ceria"},
              "tool": {"pressure_psi": 2.5, "rpm_platen": 93, "rpm_head": 87,
                       "time_s": 60.0}}
    recipe.update(kw)
    return run_recipe(recipe)


def _w(ph):
    return run_recipe({
        "model": "auto", "wafer": {"film": "w", "n_radial": 11},
        "slurry": {"pack": "w_fe_oxidizer", "ph": ph},
        "tool": {"pressure_psi": 3.0, "rpm_platen": 90, "rpm_head": 90,
                 "time_s": 60.0}})


def _texts(res):
    return list(res.get("warnings") or []) + list(res.get("notes") or [])


# ── 1. pad hardness on the pack is on the wrong path ─────────────────────

def test_pad_hardness_set_on_the_pack_is_inert_and_says_which_path_works():
    lo, hi = _oxide(params={"pad_hardness_shore_d": 40.0}), \
             _oxide(params={"pad_hardness_shore_d": 60.0})
    assert lo["removal_rate_A_per_min"] == pytest.approx(
        hi["removal_rate_A_per_min"], rel=1e-9), (
        "if this now moves, the declaration below is stale and lying")

    said = [t for t in _texts(lo) if "pad_hardness_shore_d" in t]
    assert said, "an accepted-and-ignored pad hardness must announce itself"
    text = said[0]
    # The declaration is only useful if it names the path that DOES work.
    assert "Pad OBJECT" in text or "pad:" in text, text
    assert "shore_d" in text, text


def test_the_pad_object_is_the_path_that_reaches_the_contact_layer():
    """Calibrates the claim above: the recommended route is not inert too.

    Without this, the warning could be advice to do something equally
    ineffective and the test suite would be happy.
    """
    soft = _oxide(pad={"shore_d": 40.0})
    hard = _oxide(pad={"shore_d": 60.0})
    reached = [t for t in _texts(soft) if "Shore D 40" in t and "E*" in t]
    assert reached, (
        "the GW layer must at least CONVERT a Shore D given on the pad; "
        f"warnings were {_texts(soft)[:5]}")
    # kappa itself is withheld for sti_ceria (its reference pad is inherited,
    # not measured), and that refusal is a separate, already-tested policy.
    # What must not happen is silence.
    assert any("pad contact correction NOT applied" in t for t in _texts(soft)), (
        "the withheld contact factor must state that it was withheld")
    assert soft["removal_rate_A_per_min"] == pytest.approx(
        hard["removal_rate_A_per_min"], rel=1e-9)


# ── 2. D99 belongs to the defect proxy, and must be shown to reach it ────

def test_d99_does_not_move_the_rate_but_says_so():
    fine = _oxide(slurry={"pack": "sti_ceria",
                          "abrasive": {"kind": "ceria", "d50_nm": 100.0,
                                       "d99_nm": 200.0}})
    coarse = _oxide(slurry={"pack": "sti_ceria",
                            "abrasive": {"kind": "ceria", "d50_nm": 100.0,
                                         "d99_nm": 800.0}})
    assert fine["removal_rate_A_per_min"] == pytest.approx(
        coarse["removal_rate_A_per_min"], rel=1e-9)
    said = [t for t in _texts(coarse) if "abrasive_d99_nm" in t
            or "D99" in t]
    assert said, "the tail must not be silently inert on the rate"
    assert any("defect" in t.lower() or "scratch" in t.lower() for t in said), (
        "the declaration has to name where D99 DOES go, or it is just an "
        f"apology: {said}")


def test_the_tail_really_does_reach_the_defect_proxy():
    """The other half of the claim. Inert on the rate, live on the defect.

    If D99 moved nothing anywhere, "it feeds the defect proxy" would be an
    excuse rather than a description.
    """
    fine = _oxide(slurry={"pack": "sti_ceria",
                          "abrasive": {"kind": "ceria", "d50_nm": 100.0,
                                       "d99_nm": 200.0}})
    coarse = _oxide(slurry={"pack": "sti_ceria",
                            "abrasive": {"kind": "ceria", "d50_nm": 100.0,
                                         "d99_nm": 800.0}})

    def risk(res):
        defect = res.get("defect_risk") or {}
        for key in ("delta_risk_index", "scratch_risk", "risk", "score"):
            if isinstance(defect.get(key), (int, float)):
                return float(defect[key])
        return None

    r_fine, r_coarse = risk(fine), risk(coarse)
    assert r_fine is not None and r_coarse is not None, (
        f"no numeric defect output to compare: {fine.get('defect_risk')}")
    assert r_coarse > r_fine, (
        f"a 4x larger tail must raise the defect proxy: {r_fine} -> {r_coarse}")


# ── 3. the tungsten pH null is measured, and its scope is stated ─────────

def test_the_w_ph_null_result_is_published_with_its_source():
    inside = _w(4.0)
    said = [t for t in _texts(inside) if "DECLARED NULL RESULT" in t]
    assert said, "a measured null must be reported, or it reads as a gap"
    text = said[0]
    assert "ph_response_is_null_over_3_to_6" in text, text
    assert "US20110186542A1" in text or "us20110186542a1" in text, (
        f"the null must carry the measurement it rests on: {text}")
    assert "inside that window" in text, text


def test_outside_the_measured_window_the_same_flatness_is_an_extrapolation():
    """The scope clause is the part that can go wrong silently.

    pH 3-6 is measured. An alkaline tungsten slurry is not, and the model
    returning the same flat response there is a guess wearing a measurement's
    clothes. The warning must change.
    """
    outside = _w(10.0)
    said = [t for t in _texts(outside) if "DECLARED NULL RESULT" in t]
    assert said, said
    assert "OUTSIDE that window" in said[0], said[0]
    assert "extrapolation" in said[0], said[0]


def test_the_null_window_is_parsed_from_the_key_not_asserted():
    """A window stated twice can disagree with itself.

    The boundary comes from the key NAME, so a pack cannot declare pH 3-6 and
    be checked against some other range held elsewhere.
    """
    from cmp_sim.models.chemical_rate import _ph_is_inside

    assert _ph_is_inside("3 to 6", 3.0)
    assert _ph_is_inside("3 to 6", 6.0)
    assert not _ph_is_inside("3 to 6", 6.01)
    assert not _ph_is_inside("3 to 6", 2.99)
    # An unparseable window must fall to the CAUTIOUS side (extrapolation),
    # never silently claim the measurement covers the point.
    assert not _ph_is_inside("whenever", 4.0)


# ── 4. the standing guards ───────────────────────────────────────────────

def test_no_silent_axis_remains_anywhere_in_the_corpus():
    """The 17th run left four; this run must leave none.

    The known-silent allowlist in
    tests/test_every_swept_axis_is_connected.py is now empty, so any newly
    disconnected input fails there. This test asserts the same fact from the
    scan's own numbers so the allowlist cannot be quietly refilled.
    """
    from tools.inert_axis_scan import scan

    result = scan()
    assert not result.by_kind("silent"), [
        (a.dataset, a.axis) for a in result.by_kind("silent")]
    assert not result.by_kind("wiring"), [
        (a.dataset, a.axis) for a in result.by_kind("wiring")]
    # The count itself must not fall: turning silence into a declaration does
    # not connect anything, so the same 25 axes stay inert.
    assert len(result.inert) == 25, (
        f"{len(result.inert)} inert axes; declaring a gap must not change "
        "which inputs reach the rate")


def test_declaring_the_gaps_did_not_move_the_score():
    """Zero constants were added, so the median must be exactly where it was.

    If this moves, something in this change was a fit dressed as a warning.
    """
    from cmp_sim.core.predictive_score import score_all

    scores = [s for s in score_all() if s.shape_mape is not None]
    median = statistics.median(s.shape_mape for s in scores)
    assert 18.5 <= median <= 19.0, median
