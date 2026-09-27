"""§39 — the completion bar is NOT bounded from below by input degeneracy.

The owner's standing rule (STATUS.md) allows the 10% completion bar to be
relaxed toward 15% only if a session first writes down *what creates the lower
bound on the error* — a mechanism, not a difficulty.  This suite pins the
answer measured by ``tools/input_degeneracy_floor_probe.py``, which is **no**:
the bound exists, it is exactly computable, and it does not bind where the
headline is decided.

Every number below is re-measured from the shipping solver and the dataset
files at test time.  Nothing is copied from docs/limits.md — a test that pins
a literal transcribed from prose goes stale silently and then invites someone
to edit the prose to match it (docs/limits.md §35's lesson).
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from cmp_sim.core.validation import dataset_paths
from tools.input_degeneracy_floor_probe import dataset_floor
from tools.median_crossing_probe import crossing_report

BAR = 15.0


def _floors():
    out = []
    for path in dataset_paths():
        f = dataset_floor(path)
        if f is not None:
            out.append(f)
    return out


@pytest.fixture(scope="module")
def floors():
    return _floors()


@pytest.fixture(scope="module")
def held_out_floors(floors):
    """The corpus the honest headline is quoted on (docs/limits.md §32-§35)."""
    from tools.calibration_flag_audit import collect, tainted_datasets

    tainted = set(tainted_datasets(collect()))
    return [f for f in floors if f.dataset not in tainted]


def test_the_probe_is_not_vacuous(floors):
    """A probe that collects nothing would 'pass' every assertion below."""
    assert len(floors) >= 30, (
        f"only {len(floors)} datasets produced a floor; the corpus is larger "
        "than that, so the probe is silently failing to run the solver")
    assert any(f.floor > 0.0 for f in floors), (
        "no dataset has two rows sharing a prediction — either the corpus "
        "changed radically or the grouping key is broken")


def test_the_floor_is_a_real_bound_where_it_binds(floors):
    """A tied group's floor must not exceed the model's actual score on it.

    The floor gives every tied group its OWN free constant, which is strictly
    more freedom than the scorer's single per-dataset scale.  So on any
    dataset the probe and the scorer both grade, floor <= shape must hold.
    If it does not, the probe is not computing a bound and its verdict is
    worthless.
    """
    from cmp_sim.core.predictive_score import score_all

    scores = {s.dataset: s for s in score_all()}
    checked = 0
    for f in floors:
        s = scores.get(f.dataset)
        if s is None or s.shape_mape is None:
            continue
        checked += 1
        assert f.floor <= s.shape_mape + 1e-6, (
            f"{f.dataset}: floor {f.floor:.2f}% exceeds the shape score "
            f"{s.shape_mape:.2f}%. The floor is supposed to be a LOWER bound "
            "computed with more freedom than the scorer has, so this means "
            "the two are not scoring the same rows.")
    assert checked >= 20, f"only {checked} datasets were comparable"


def test_a_flat_prediction_is_not_counted_as_a_bound(floors):
    """One group for a whole dataset is a declared refusal, not a limit.

    docs/limits.md §36: those blocks predict a constant because the pack
    states it has no constants for the axis swept, and each carries a
    machine-readable ``[DECLINES_AXIS: ...]`` marker.  Supplying the missing
    measurement makes the prediction vary and the floor disappears.  Counting
    such a block as an irreducible bound would let the model's own silence
    argue for relaxing the completion bar — the §37 failure in a new costume.
    """
    flat = [f for f in floors if f.floor > 0.0 and f.is_flat]
    assert flat, (
        "no flat-predicting block found; §36 recorded several, so either they "
        "were repaired (update this test with the measurement that did it) or "
        "the flatness detector is broken")
    real = [f for f in floors if f.floor > 0.0 and not f.is_flat]
    assert real, "every degenerate block is flat — then §39 has no subject"
    # The two populations must be genuinely different, or the distinction is
    # decorative.
    assert len(real) >= len(flat), (
        "the genuine-degeneracy population has shrunk below the declared-"
        "refusal one; re-measure before trusting the verdict")


def test_the_corpus_median_floor_is_zero(floors):
    """The median dataset has NO degeneracy, so no corpus-wide bound exists.

    This is the whole verdict.  The headline is the upper median of the
    per-dataset shape errors, so a bound on the headline would require the
    MEDIAN dataset to be floored.  It is not: over half the corpus has a floor
    of exactly zero, meaning a better model could in principle score them
    perfectly.
    """
    vals = sorted(f.floor for f in floors)
    median = vals[len(vals) // 2]
    assert median == pytest.approx(0.0, abs=1e-9), (
        f"the median dataset now has a floor of {median:.2f}%. That WOULD be "
        "a corpus-wide bound and it would justify relaxing the completion "
        "bar — but only after re-deriving it here, not by editing prose.")


def test_no_must_cross_dataset_is_floored_above_the_bar(floors):
    """The completion bar is a counting statistic (§26), so this is the test.

    The median meets the bar exactly when enough individual datasets cross it.
    Degeneracy could therefore block completion in only one way: if a dataset
    that MUST cross were floored above the bar.  None is.  When that changes,
    this test fails and the relaxation argument becomes admissible — with the
    blocking dataset named.
    """
    rep = crossing_report(BAR, held_out=True)
    must = rep["datasets_that_must_cross"]
    assert must >= 0
    floor_by = {f.dataset: f.floor for f in floors}
    shortlist = [t[0] for t in rep["nearest"]]
    assert shortlist, "no dataset is above the bar — the project is complete"
    blocked = [(n, floor_by.get(n, 0.0)) for n in shortlist[:max(must, 1) + 2]
               if floor_by.get(n, 0.0) > BAR]
    assert not blocked, (
        f"{blocked} must cross {BAR}% but cannot: their input-degeneracy "
        "floor is already above it. THIS is a valid reason to relax the "
        "completion bar; record the mechanism in docs/limits.md and quote "
        "these numbers.")


def test_every_genuine_bound_sits_below_the_completion_bar(held_out_floors):
    """The strongest form of the verdict, and it is measured, not argued.

    Not only is the median floor zero -- on the held-out corpus **no** genuine
    degeneracy bound reaches the 15% bar at all.  Every dataset is therefore
    reachable in principle: whatever keeps the remaining blocks above the bar
    is missing physics or missing data, never the input schema.

    Measured on the HELD-OUT corpus, because that is the number the project
    quotes (19.5%, §32-§35). On the published corpus `cn109609035b` carries a
    16.1% bound -- but it is one of the blocks the model was fitted to, so it
    is not part of the honest headline and cannot be evidence about it either
    way.

    Flat blocks are excluded deliberately (§36): their "floor" is a declared
    refusal that a measurement dissolves, so including them would let the
    model's own silence argue for relaxing the bar.
    """
    real = sorted((f for f in held_out_floors if not f.is_flat),
                  key=lambda f: -f.floor)
    assert real, "no genuine degeneracy in the held-out corpus"
    worst = real[0]
    assert worst.floor <= BAR, (
        f"{worst.dataset} now carries a genuine bound of {worst.floor:.1f}%, "
        f"above the {BAR}% bar, on {worst.tied_rows} tied rows. If it is also "
        "a must-cross dataset the completion bar is structurally unreachable "
        "-- record the mechanism in docs/limits.md §39 with these numbers "
        "rather than relaxing this test.")


def test_the_worst_bound_is_a_row_collapse_not_a_whole_block(floors):
    """"Irreducible" must never be claimed on a block the model cannot score.

    The first draft of §39 grouped every measured row and named `ihnfeldt2008`
    the corpus's largest bound at 67.2%.  That dataset is not scored at all:
    six of its seven rows are GATED outside the pack's oxidizer pH window, so
    they share a prediction by declared refusal and `predictive_score` already
    drops them.  Any dataset the probe reports must therefore also be one the
    scorer grades.
    """
    from cmp_sim.core.predictive_score import score_all

    scored = {s.dataset for s in score_all() if s.shape_mape is not None}
    reported = {f.dataset for f in floors if f.floor > 0.0}
    stray = sorted(reported - scored)
    assert not stray, (
        f"{stray} carry a floor but are not scored by predictive_score. A "
        "bound on a dataset the headline never sees says nothing about the "
        "completion bar, and reporting one overstates the case.")
