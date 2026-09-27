"""The abrasive-CONCENTRATION exponent is a DERIVED LAW, not a material property.

Pins BOTH halves of the 2026-09-28 result, because each half is load-bearing and
each is easy to lose:

  NEGATIVE: the material-scope hypothesis that licensed
  ``SIZE_EXPONENT_BY_ABRASIVE`` FAILS on the concentration axis. STATUS.md set
  the bar (between/within > 2x) BEFORE the measurement, and the answer is 1.6x.
  Re-attributing anyway "for symmetry with the size axis" is the mistake this
  test exists to block.

  POSITIVE: a single DERIVED exponent m = +1/3 (Li 2021 surface-area branch /
  Cook 1990 supply limit) lands on the corpus median. That is the opposite of
  the pH and size verdicts, where a single derived value was falsified — so the
  three results together are not a pattern of "derivations fail", and this test
  keeps the distinction auditable.

Both numbers are RE-DERIVED from the dataset files here rather than copied from
the probe's docstring, so editing a dataset cannot leave a stale claim behind.
"""
from __future__ import annotations

import os
import statistics
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))), "tools"))

from conc_derived_probe import (  # noqa: E402
    DERIVABLE_MAX, DERIVABLE_MIN, MIN_RATIO, conc_range_scope,
    global_law_scope, load_conc_groups, material_scope,
)

from cmp_sim.slurry.abrasive_effects import (  # noqa: E402
    DERIVED_CONC_EXPONENT, DERIVED_CONC_EXPONENT_WHY,
    SIZE_EXPONENT_BY_ABRASIVE,
)


def test_the_corpus_still_has_enough_conc_sweeps_to_decide_anything():
    groups = load_conc_groups()
    assert len(groups) >= 15, (
        f"only {len(groups)} concentration sweeps with >=3 levels; the "
        "verdicts below were measured on 18 and are not supported by fewer")
    for g in groups:
        assert len({c for c, _ in g["points"]}) >= 3


def test_concentration_is_NOT_a_material_property():
    """The size axis's licence does not extend here — measured, not assumed."""
    res = material_scope()
    assert res["ratio"] is not None, res
    assert res["ratio"] < MIN_RATIO, (
        f"between/within is now {res['ratio']:.1f}x, above the {MIN_RATIO}x bar. "
        "If this is real the concentration exponent COULD become a material "
        "table like the size one — but do not flip it on this test alone; "
        "re-run tools/conc_derived_probe.py and check which material moved")
    # the specific reason it fails: the well-sampled materials AGREE
    well = {k: statistics.fmean(v) for k, v in res["by_material"].items()
            if len(v) >= 3}
    assert len(well) >= 3, well
    assert max(well.values()) - min(well.values()) < 0.15, (
        f"the three well-sampled materials no longer agree: {well}")


def test_a_single_derived_third_covers_the_corpus():
    g = global_law_scope()
    assert g["median"] == pytest.approx(DERIVED_CONC_EXPONENT, abs=0.05), (
        f"corpus median {g['median']:+.3f} has moved away from the derived "
        f"{DERIVED_CONC_EXPONENT:+.3f}; the law no longer matches the data")
    assert g["n_within_0_25"] / g["n_strong"] >= 0.75, (
        f"only {g['n_within_0_25']}/{g['n_strong']} groups sit within 0.25 of "
        "+1/3; the single-law claim is weakening")
    assert DERIVABLE_MIN <= DERIVED_CONC_EXPONENT <= DERIVABLE_MAX


def test_the_dissenters_are_recorded_not_excluded():
    """Every dissenter must be NAMED, and its direction must be accounted for.

    This asserted "every dissenter is a SiC row", licensing the module
    comment's "indentation-limited on hard films" reading. That failed in
    2026-09 when a dilute colloidal-silica ladder on OXIDE (US9422456B2
    Example 1) dissented -- and the honest reading is that the old claim was
    over-general rather than that the new datum is an outlier.

    The SIGN is what separates the two explanations, so it is asserted rather
    than the film list. A supply/indentation dissenter is FLATTER than the
    derived +1/3 (removal starved relative to the area law). The oxide
    dissenter is STEEPER (+0.83), which is the load-sharing-onset direction of
    docs/limits.md §30: at 0.5 wt% the contact is not full, so adding particles
    buys more than the area law predicts. Two mechanisms, opposite signs, and
    the module comment must not claim one covers both.
    """
    g = global_law_scope()
    assert g["dissenters"], "no dissenters at all; the band claim is vacuous"
    for r in g["dissenters"]:
        film, m = str(r["film"]), float(r["m"])
        if film == "sic":
            continue
        assert m > DERIVED_CONC_EXPONENT, (
            f"a non-SiC dissenter on {film} is FLATTER than the derived "
            f"exponent (m={m:+.2f}); that is the supply-limited direction on "
            "a film the 'indentation on hard films' reading does not cover, "
            "so the module comment is now wrong in a way this test cannot "
            "excuse. Re-derive rather than widen the wording.")
    steep = [r for r in g["dissenters"]
             if str(r["film"]) != "sic" and float(r["m"]) > DERIVED_CONC_EXPONENT]
    if steep:
        why = DERIVED_CONC_EXPONENT_WHY
        assert "NOT all SiC" in why and "§30" in why, (
            "a steep non-SiC dissenter exists but DERIVED_CONC_EXPONENT_WHY "
            "still tells the all-SiC story; the provenance string must name "
            "the exception and where it is explained")
    assert "SiC" in DERIVED_CONC_EXPONENT_WHY


def test_langmuir_saturation_is_falsified_on_this_axis():
    """A saturating response predicts a clearly NEGATIVE slope-vs-wt% trend."""
    rng = conc_range_scope()
    assert rng["r"] is not None
    assert rng["r"] > -0.3, (
        f"corr(m, log mean wt%) is now {rng['r']:+.2f}; a strongly negative "
        "value would revive the saturation form and the derived pure power "
        "law would need the knee back")


def test_derived_and_material_scoped_provenance_stay_distinct():
    """A law is abrasive-independent; a re-attributed measurement is not.

    Guards the honesty boundary rather than a number: the size exponent must
    keep differing by material, and the concentration exponent must be a single
    value carrying its derivation.
    """
    values = {k: v["value"] for k, v in SIZE_EXPONENT_BY_ABRASIVE.items()}
    assert len(set(values.values())) == len(values), (
        f"the size table collapsed to shared values {values}; if that is real "
        "it is no longer a material property either")
    assert isinstance(DERIVED_CONC_EXPONENT, float)
    assert DERIVED_CONC_EXPONENT == pytest.approx(1.0 / 3.0)
    for must in ("C**(1/3)", "Li 2021", "1.6x"):
        assert must in DERIVED_CONC_EXPONENT_WHY, must
    # The saturation-falsification correlation is quoted in the provenance
    # string, so it is RE-MEASURED here rather than pinned as a literal. A
    # hard-coded "+0.06" went stale the moment a dataset was added, which made
    # a true statement fail a test and invited editing the string to match a
    # number nobody had recomputed.
    corr = conc_range_scope().get("r")
    assert corr is not None
    assert f"{corr:+.2f}" in DERIVED_CONC_EXPONENT_WHY, (
        f"the provenance string quotes a saturation correlation that is no "
        f"longer what the corpus measures ({corr:+.2f}); re-run "
        "tools/conc_derived_probe.py and update the claim")
    assert corr > -0.3, (
        f"the saturation correlation is now clearly negative ({corr:+.2f}), "
        "which is the Langmuir signature the provenance string declares "
        "falsified; the derived exponent's justification must be re-argued")
