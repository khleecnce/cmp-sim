"""A refusal the scorer cannot read is scored as a prediction.

The validation scorer's job is to compare the model's opinion against
measurement.  When a term is switched off for a cited reason, the model has no
opinion about that axis -- the rate is constant along it -- and the shape
score's one free scale then fits the constant to the measured mean, so the
block reproduces the `flat` baseline EXACTLY and still counts toward the
headline median.  That is a declared silence being graded as an answer.

The scorer recognised exactly one word, ``GATED``.  Four of the five flat
blocks used other words, two of them with full citations and an unblocking
experiment.  The fix is a machine-readable marker naming the AXIS declined
(`cmp_sim.core.declined_axes`), added alongside the existing prose.

These tests pin the property, not the instances:

* every flat-scoring block must DECLARE the axis it is flat on;
* the marker must name an axis the dataset actually sweeps, not merely exist;
* the human-readable reason must survive (a bare marker is worse than prose);
* and the median must NOT move, because nothing about the physics changed --
  an honesty fix that moved the score would be a selection.
"""

from __future__ import annotations

import pytest

from cmp_sim.core.declined_axes import declined_axes, declining_warnings
from cmp_sim.core.predictive_score import score_all
from tools.flat_prediction_census import SAME, census


@pytest.fixture(scope="module")
def scores():
    return score_all()


def test_the_corpus_still_contains_flat_scoring_blocks(scores):
    """Non-vacuity: these assertions are worthless if nothing is flat.

    If this fails because the count reached zero, every flat block now
    predicts its axis -- delete the guard rather than lowering it.
    """
    c = census(scores)
    assert len(c["flat"]) >= 3, (
        "fewer flat blocks than expected; the tests below would pass by "
        "examining nothing")


def test_no_flat_block_is_silent(scores):
    """Every block whose prediction carries no trend must SAY so."""
    c = census(scores)
    silent = [s.dataset for s in c["silent"]]
    assert not silent, (
        "these blocks score exactly the flat baseline -- the model made no "
        "prediction about the axis they sweep -- and no warning declares it, "
        "so a reader cannot tell a refusal from a result: " + ", ".join(silent))


def test_a_declaration_names_an_axis_the_dataset_actually_sweeps(scores):
    """Declaring some unrelated axis must not count as declaring this one.

    Without this, a warning naming a convenient axis would silence the check
    above while the block stayed exactly as undetectable as before.
    """
    c = census(scores)
    for s in c["declared"]:
        assert s.declined_axes_swept, s.dataset
        assert set(s.declined_axes_swept) <= set(s.axes), s.dataset


def test_the_declaration_keeps_its_prose_reason(scores):
    """A marker alone is a regression: the reason is the part that expires.

    Each declaring warning must carry substantially more than the marker, so
    a future edit cannot reduce a cited refusal to a machine token.
    """
    from cmp_sim.api import run_recipe
    from cmp_sim.core.predictive_score import _recipe_for, _measured
    from cmp_sim.core.validation import dataset_paths
    import yaml

    c = census(scores)
    wanted = {s.dataset for s in c["declared"]}
    seen = 0
    for path in dataset_paths():
        if path.stem not in wanted:
            continue
        doc = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        rows = [r for r in (doc.get("conditions") or [])
                if _measured(r) is not None]
        if not rows:
            continue
        warns = run_recipe(_recipe_for(doc, rows[0])).get("warnings") or []
        for w in declining_warnings(warns):
            body = w.split("]", 1)[1] if "]" in w else ""
            assert len(body.strip()) > 80, (
                f"{path.stem}: a declaration was reduced to a marker with no "
                f"readable reason: {w!r}")
            seen += 1
    assert seen, "no declaring warning was inspected"


def test_marking_a_refusal_does_not_move_the_headline(scores):
    """Zero median movement is the CORRECT outcome here -- assert it.

    Nothing about the physics changed: the same rates are predicted for the
    same rows. If this ever fails, a "labelling" change has altered a
    prediction and must be re-examined rather than re-baselined.
    """
    errs = sorted(s.shape_mape for s in scores if s.shape_mape is not None)
    assert abs(errs[len(errs) // 2] - 18.9) < 0.3, errs[len(errs) // 2]


def test_flat_means_flat_by_the_same_definition_the_census_uses(scores):
    """The census's `SAME` tolerance must actually select constant predictions.

    A tolerance loose enough to catch blocks that DO respond would make the
    honesty claim above vacuous in the other direction.
    """
    c = census(scores)
    for s in c["flat"]:
        assert abs(s.shape_mape - s.flat_mape) < SAME, s.dataset


def test_the_parser_requires_the_marker_and_not_merely_the_word(scores):
    """`declined_axes` must not fire on prose that happens to say GATED."""
    assert declined_axes(["oxidizer term GATED at pH 10 for good reasons"]) \
        == set()
    assert declined_axes(["[DECLINES_AXIS: slurry_ph] because ..."]) \
        == {"slurry_ph"}
    assert declined_axes(["[DECLINES_AXIS: a, b] x"]) == {"a", "b"}
    assert declined_axes(None) == set()
