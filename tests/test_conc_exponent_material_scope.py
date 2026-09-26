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
    """Every group outside the band must be a SiC row, and must be named.

    If a dissenter ever appears on a film other than SiC, the "indentation-
    limited on hard films" reading in the module comment is wrong and must be
    rewritten rather than quietly widened.
    """
    g = global_law_scope()
    films = {str(r["film"]) for r in g["dissenters"]}
    assert films <= {"sic"}, (
        f"a non-SiC dissenter appeared ({films}); the module comment's regime "
        "explanation no longer covers the data")
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
    for must in ("C**(1/3)", "Li 2021", "1.6x", "+0.06"):
        assert must in DERIVED_CONC_EXPONENT_WHY, must
