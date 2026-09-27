"""The pH-response self-grade has NO path to a held-out value (docs/limits.md §34).

§32 left eleven pH-response citations self-graded across three packs. §33
measured the size-exponent family and refused the repair on price. The
instruction for this family was to ask the cheaper question first: does
outcome (b) -- refit the constant on evidence excluding the scored block --
exist STRUCTURALLY at all?

Measured (``tools/ph_holdout_reachability_probe.py``): no. Donors exist, but
the pH optimum is not a property of film or of abrasive -- within-group spread
EXCEEDS between-group spread (ratio 0.41x against a 2x bar), and two published
ceria-on-oxide slurries optimise 3.8 pH units apart, on opposite sides of
neutral. A held-out optimum would be a transplant, so the repair is (a) by
structure and the §32 held-out median 19.5% stands.

Every number is re-measured here from the dataset rows. The peak grid is
coarsened for speed and a test asserts the verdict does not depend on that.
"""
from __future__ import annotations

import pytest

from tools.ph_holdout_reachability_probe import (
    IMPLICATED,
    PROPERTY_BAR,
    donors_available,
    fitted_optima,
    verdict,
)

#: Coarse grid: the verdict is about spreads of whole pH units, and
#: test_the_verdict_does_not_depend_on_the_grid pins that this choice is not
#: load-bearing.
STEP = 1.0


@pytest.fixture(scope="module")
def rows():
    r = fitted_optima(peak_step=STEP)
    assert len(r) >= 5, (
        "only %d pH sweeps could be re-fitted; below this every assertion "
        "here passes by default" % len(r))
    scored = {x["dataset"] for x in r} & IMPLICATED
    assert len(scored) == len(IMPLICATED), (
        "the probe no longer reaches all implicated pH blocks: missing %s"
        % sorted(IMPLICATED - scored))
    return r


def test_donors_exist_so_this_is_not_a_no_data_refusal(rows):
    """The refusal must not be confusable with "the corpus is too small".

    Every implicated block shares a film with another publication. If that
    stopped being true the refusal would have a different, weaker reason and
    the entry would need rewriting.
    """
    by_film = donors_available(rows, ("film",))
    assert by_film and all(v > 0 for v in by_film.values()), (
        "every implicated pH block was supposed to HAVE a donor publication; "
        "got %s. §34 refuses on the quality of the donor, not its absence"
        % by_film)


def test_no_grouping_makes_the_ph_optimum_a_property(rows):
    """between/within must clear the same 2x bar the material split cleared.

    A ratio below 1.0 means the grouping explains less than nothing. This is
    the assertion that makes outcome (b) unreachable; a grouping clearing the
    bar reopens the repair.
    """
    v = verdict(rows)
    clearing = [("+".join(g["keys"]), g["ratio"]) for g in v["groupings"]
                if g["is_property"]]
    assert not clearing, (
        "%s now clear the %.1fx property bar, so a held-out pH optimum may "
        "exist and §34's structural refusal must be re-measured"
        % (clearing, PROPERTY_BAR))
    finite = [g["ratio"] for g in v["groupings"] if g["ratio"] == g["ratio"]]
    assert finite, "no grouping produced a finite ratio; the probe is broken"
    assert max(finite) < 1.0, (
        "the best grouping now reaches %.2fx; below 1.0 was the finding "
        "(within-group spread exceeds between-group), and at/above 1.0 the "
        "reading changes even if the 2x bar is still unmet" % max(finite))


def test_the_named_ceria_pair_really_is_the_same_grouping(rows):
    """§34's headline example must be checkable, not rhetorical.

    dandu2009 and netzband2020 are both ceria on oxide and are quoted as
    disagreeing by 3.8 pH units across neutral. If they ever stop sharing the
    grouping, the example is wrong even if the ratio still fails.
    """
    pair = {r["dataset"]: r for r in rows
            if r["dataset"] in ("dandu2009_sio2_ceria_ph_sweep",
                                "netzband2020_thermal_oxide_ceria_ph")}
    assert len(pair) == 2, "the quoted ceria pair is no longer in the corpus"
    a, b = pair.values()
    assert a["film"] == b["film"] and a["abrasive"] == b["abrasive"], (
        "the quoted pair no longer shares film+abrasive (%s/%s vs %s/%s), so "
        "it is not an example of WITHIN-group disagreement"
        % (a["film"], a["abrasive"], b["film"], b["abrasive"]))
    gap = abs(a["peak"] - b["peak"])
    assert gap >= 2.0, (
        "the two ceria-on-oxide optima now agree to %.1f pH units; the "
        "within-group disagreement that drives §34 has shrunk and the entry "
        "must be re-measured" % gap)


def test_the_verdict_does_not_depend_on_the_grid(rows):
    """A speed choice must not be load-bearing.

    The coarse grid used by these tests and the fine grid the CLI prints must
    reach the SAME verdict. Digits may differ; the reading may not.
    """
    coarse = verdict(rows)
    fine = verdict(fitted_optima(peak_step=0.5))
    assert coarse["any_donor"] == fine["any_donor"]
    assert coarse["any_property"] == fine["any_property"], (
        "the property verdict flips between peak grids (%s coarse vs %s fine); "
        "the conclusion is an artefact of resolution"
        % (coarse["any_property"], fine["any_property"]))


def test_expiry_a_qualifying_grouping_reopens_the_repair(rows):
    """§34 is a structural refusal, so it must expire on structure.

    Two sweeps of the same abrasive-and-dispersant system from different
    publications agreeing to ~1 pH unit would create a grouping the optimum
    IS a property of. The cheapest detectable signature is the worst
    within-group span collapsing.
    """
    v = verdict(rows)
    assert v["worst_within_span"] > 2.0, (
        "the worst within-group pH disagreement has fallen to %.1f units; a "
        "grouping may now support a held-out optimum and outcome (b) must be "
        "priced with a leave-one-out as in tools/size_exponent_loo_probe.py"
        % v["worst_within_span"])
