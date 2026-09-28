"""§48 — the two readers that answer "did the model predict this axis?" are BINARY.

``inert_axis_scan`` asks whether the predicted rate moves more than 0.5 %, and
``flat_prediction_census`` asks whether the shape score differs from the flat
baseline by more than 0.05 pp.  **Neither bar takes the measurement as an
argument**, so both are cleared by a prediction that moves a token amount
against a measurement that moves a great deal — and every reader in this
repository then grades that block as an ordinary prediction of the axis.

These tests pin:

1. The blindness as **arithmetic** on synthetic input, so no corpus change can
   retire the motivation (the same decision §45/§46/§47 took).
2. That the continuous statistic (``trend_share``) separates the cases both
   binary readers merge, and is invariant to the scorer's free scale.
3. That **no token-trend block is SILENT** — each one is either a run-declared
   substitution, a dataset-declared unmodelled quantity, or a named member of a
   deliberately shared constant.  A new one appearing with no explanation fails
   here, which is the exit condition.
4. That the honesty fix moved **no prediction**: median unchanged at 18.9 %.

Every quoted number is re-measured at run time.  Pinning literals is how §40
came to edit prose instead of code.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from cmp_sim.core.declined_axes import (  # noqa: E402
    SUBSTITUTED_AXIS, declined_axes, substituted_axes,
)
from cmp_sim.core.predictive_score import score_all  # noqa: E402
from tools.trend_share_census import (  # noqa: E402
    INERT_TOLERANCE, SAME, TOKEN_SHARE, census,
    proof_inert_bar_ignores_the_measurement,
    reader_flat_says_predicting, reader_inert_says_responsive,
    shape_and_flat, shared_constant_members, trend_share,
)


@pytest.fixture(scope="module")
def scores():
    return score_all()


@pytest.fixture(scope="module")
def result(scores):
    return census(scores)


# ── 1. the blindness is arithmetic ──────────────────────────────────────────

@pytest.mark.parametrize("measured_span", [2.0, 10.0, 80.0])
def test_both_binary_bars_clear_on_a_token_response(measured_span):
    """A response 1.2x the inert bar is called RESPONSIVE against any span.

    No corpus is involved: the bar is a statement about the predicted series
    alone, so the same prediction passes whether the measurement moved 2x or
    80x, while the share it explains falls like 1/ln(span).
    """
    p = proof_inert_bar_ignores_the_measurement(measured_span)
    assert p["responsive"] == 1.0, (
        "inert_axis_scan must call this responsive — if it does not, its "
        "tolerance changed and this proof needs re-deriving, not relaxing")
    assert p["predicting"] == 1.0, (
        "flat_prediction_census must call this a prediction")
    assert p["share"] < 0.05, (
        f"explained share {p['share']:.4f} should be negligible")


def test_the_share_falls_as_the_measured_span_grows_at_fixed_prediction():
    """The defect is monotone in the thing the binary bars ignore."""
    shares = [proof_inert_bar_ignores_the_measurement(s)["share"]
              for s in (2.0, 10.0, 80.0)]
    assert shares == sorted(shares, reverse=True), shares


def test_trend_share_is_invariant_to_the_scorers_free_scale():
    """The shape score gives one free multiplicative scale per block.

    A statistic used to judge that score must not be readable off the
    calibration, so it has to be invariant over decades of scale.
    """
    measured = [1.0, 2.0, 4.0, 8.0]
    predicted = [1.0, 1.2, 1.5, 1.8]
    base = trend_share(measured, predicted)
    assert base is not None
    for k in (1e-3, 1e-1, 1.0, 10.0, 1e3):
        got = trend_share(measured, [k * p for p in predicted])
        assert got is not None
        assert abs(got - base) < 1e-9, (k, got, base)


def test_a_token_and_a_full_prediction_are_INDISTINGUISHABLE_to_both_bars():
    """The two readers merge the cases the share separates — on one input set."""
    measured = [1.0, 2.0, 4.0, 8.0]
    token = [1.0, 1.005, 1.010, 1.015]
    full = [1.0, 2.0, 4.0, 8.0]
    for predicted in (token, full):
        assert reader_inert_says_responsive(predicted)
        assert reader_flat_says_predicting(measured, predicted)
    t = trend_share(measured, token)
    f = trend_share(measured, full)
    assert t is not None and f is not None
    assert t < TOKEN_SHARE < f, (t, f)


def test_this_module_reproduces_the_shipping_scorers_two_numbers(scores):
    """Guard against the local reimplementation drifting from the scorer.

    Without this, the proofs above could be demonstrating a defect in a
    statistic nothing actually uses.
    """
    import yaml
    from cmp_sim.core.predictive_score import _measured, _predict
    from tools.trend_share_census import _load

    checked = 0
    for s in scores:
        if s.shape_mape is None or s.flat_mape is None or s.gated:
            continue
        doc = _load(s.dataset)
        if not doc:
            continue
        rows = [r for r in (doc.get("conditions") or [])
                if _measured(r) is not None]
        preds = [_predict(doc, r) for r in rows]
        if any(p is None for p in preds) or len(rows) < 3:
            continue
        shape, flat = shape_and_flat([float(_measured(r)) for r in rows],
                                     [float(p) for p in preds])
        assert abs(shape - s.shape_mape) < 1e-6, s.dataset
        assert abs(flat - s.flat_mape) < 1e-6, s.dataset
        checked += 1
        if checked >= 5:
            break
    assert checked >= 3, (
        "fewer than three blocks could be cross-checked against the shipping "
        "scorer — this test has gone vacuous")
    assert yaml is not None


# ── 2. the corpus reading, re-measured ──────────────────────────────────────

def test_the_census_is_not_vacuous(result):
    """A classifier collapsed to one answer passes every corpus-level test."""
    blocks = result["blocks"]
    assert len(blocks) >= 30, len(blocks)
    kinds = {b.kind for b in blocks}
    assert "predicting" in kinds, kinds
    assert len([b for b in blocks if b.kind == "predicting"]) >= 10


def test_NO_token_trend_block_is_silent(result):
    """The exit condition: every token block must have a stated reason.

    A token-trend block with nothing said about it is the §36 failure one level
    out — the run made no real claim about the axis it is being scored on, and
    a reader cannot tell that from the score. If this fails, MEASURE the new
    block (``tools/trend_share_census.py``) and classify it; do not widen the
    bar and do not remove the block.
    """
    silent = result["token_silent"]
    assert not silent, (
        "token-trend blocks with no stated reason: "
        + ", ".join("%s (share %.3f, %.2fx measured vs %.3fx predicted)"
                    % (b.dataset, b.share or 0, b.meas_span, b.pred_span)
                    for b in silent))


def test_the_token_band_is_non_empty_so_the_check_cannot_pass_vacuously(result):
    """If nothing lands in the band, the test above proves nothing.

    Should the corpus ever legitimately have no token block, this failure is
    the signal to re-derive the motivation rather than to delete the guard.
    """
    assert result["token"], (
        "no block lands in the token band — test_NO_token_trend_block_is_"
        "silent would now pass vacuously")


def test_each_token_block_is_classified_by_a_reason_that_exists(result):
    """A classification must be backed by the artefact it names."""
    for b in result["token"]:
        if b.kind == "token-substituted":
            assert b.substituted, b.dataset
            assert set(b.substituted) <= set(b.axes), (b.dataset, b.substituted)
        elif b.kind == "token-declared":
            assert b.unmodelled, b.dataset
        elif b.kind == "token-shared":
            assert b.shared_note, b.dataset
        else:
            pytest.fail(f"{b.dataset}: unclassified kind {b.kind}")


def test_a_substituted_axis_is_NOT_a_declined_axis(result, scores):
    """The two statements are different and must not be conflated.

    ``DECLINES_AXIS`` means the rate does not move on that axis at all.
    ``SUBSTITUTED_AXIS`` means it moves, driven by a constant from another
    species. Merging them would either excuse a real miss or hide a real
    refusal.
    """
    by_name = {s.dataset: s for s in scores}
    subbed = [b for b in result["token"] if b.kind == "token-substituted"]
    assert subbed, "no substituted block — this test has gone vacuous"
    for b in subbed:
        s = by_name[b.dataset]
        assert not (set(b.substituted) & set(s.declined_axes_swept)), (
            f"{b.dataset}: {b.substituted} is declared BOTH substituted and "
            "declined; those are contradictory claims")
        assert b.pred_span > 1.0, (
            f"{b.dataset}: a substituted axis must still MOVE the rate, else "
            "it is a declined axis and should say so")


def test_the_substitution_marker_keeps_its_prose(result, scores):
    """The marker is an addition, never a replacement (the §36 design point)."""
    import yaml
    from cmp_sim.api import run_recipe
    from cmp_sim.core.predictive_score import _measured, _recipe_for
    from tools.trend_share_census import _load

    subbed = [b for b in result["token"] if b.kind == "token-substituted"]
    assert subbed
    doc = _load(subbed[0].dataset)
    assert doc
    rows = [r for r in (doc.get("conditions") or []) if _measured(r) is not None]
    warns = run_recipe(_recipe_for(doc, rows[0])).get("warnings") or []
    carrying = [w for w in warns if SUBSTITUTED_AXIS in str(w)]
    assert carrying, warns
    for w in carrying:
        tail = str(w).split("]", 1)[1].strip()
        assert len(tail) > 60, (
            "the marker replaced the prose; the human-readable reason with its "
            "citation is what stops a refusal becoming permanent by accident")
    assert yaml is not None


def test_the_shared_constant_group_is_derived_from_the_table(result):
    """Membership is read from the provenance list, not restated here.

    Adding a sweep to a material's row must reclassify with no test edit.
    """
    members = shared_constant_members()
    assert members, "the size-exponent table published no sweep members"
    shared = [b for b in result["token"] if b.kind == "token-shared"]
    for b in shared:
        assert b.dataset in members, b.dataset


def test_a_shared_constant_block_sits_INSIDE_its_published_spread(result):
    """`token-shared` is only honest if the table already admits the miss.

    If a block's own measured exponent lies outside the spread published for
    ITS OWN material group, the group does not cover it and the classification
    is an excuse rather than a statement.

    The comparison carries ``PUBLISHED_PRECISION`` because the table states its
    spread to two decimals: ``bouvet2002_ti``'s measured exponent is -0.454 and
    the published low end is -0.45, i.e. the same number at the precision the
    table quotes. Matching to 1e-9 instead would have failed on the rounding of
    the very value the block contributed -- a bar tighter than the data behind
    it (§34: a threshold nobody has stood near is untested).
    """
    import math as _math
    from cmp_sim.core.predictive_score import _measured
    from cmp_sim.slurry.abrasive_effects import SIZE_EXPONENT_BY_ABRASIVE
    from tools.trend_share_census import _load

    PUBLISHED_PRECISION = 0.005  # half of the table's last printed digit

    shared = [b for b in result["token"] if b.kind == "token-shared"]
    assert shared, "no shared-constant block — this test has gone vacuous"
    checked = 0
    for b in shared:
        # the group this block is actually a member of, read from the table
        group = next(
            (row for row in SIZE_EXPONENT_BY_ABRASIVE.values()
             if any(str(s).split(" ")[0].strip() == b.dataset
                    for s in row.get("sweeps", ()))),
            None)
        assert group is not None, (
            f"{b.dataset} was classified token-shared but is not a member of "
            "any group in SIZE_EXPONENT_BY_ABRASIVE")
        doc = _load(b.dataset)
        assert doc
        rows = [r for r in (doc.get("conditions") or [])
                if _measured(r) is not None]
        xs, ys = [], []
        for r in rows:
            d = (r.get("overrides") or {}).get("abrasive_d50_nm")
            if d is None:
                continue
            xs.append(_math.log(float(d)))
            ys.append(_math.log(float(_measured(r))))
        if len(xs) < 3:
            continue
        mx = sum(xs) / len(xs)
        my = sum(ys) / len(ys)
        den = sum((x - mx) ** 2 for x in xs)
        slope = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / den
        lo, hi = group["spread"]
        assert lo - PUBLISHED_PRECISION <= slope <= hi + PUBLISHED_PRECISION, (
            f"{b.dataset}: measured exponent {slope:+.3f} lies outside its own "
            f"group's published spread {lo:+.2f}..{hi:+.2f}, so calling it a "
            "shared-constant member is an excuse rather than a classification")
        checked += 1
    assert checked >= 1, (
        "no shared block carried a size sweep — the assertion above ran on "
        "nothing")


# ── 3. the honesty fix moved no prediction ──────────────────────────────────

def test_the_headline_median_is_unchanged(scores):
    """Zero movement is the CORRECT outcome for an instrument repair.

    Assert it, or the next session reads the zero as a failure and 'improves'
    it (§36, §44, §45, §46, §47 all took this decision).
    """
    errs = sorted(s.shape_mape for s in scores if s.shape_mape is not None)
    assert errs
    median = errs[len(errs) // 2]
    assert abs(median - 18.9) < 0.15, (
        f"upper median is {median:.1f}%, expected 18.9% — this session added "
        "no constant and changed no pack value, so a move means a prediction "
        "changed and the marker leaked into the physics")


def test_the_marker_changes_no_rate(scores):
    """A warning string must not be able to alter a prediction."""
    from cmp_sim.api import run_recipe
    from cmp_sim.core.predictive_score import _measured, _recipe_for
    from tools.trend_share_census import _load

    doc = _load("jani2025_cu_h2o2_acidic_chelator")
    assert doc
    rows = [r for r in (doc.get("conditions") or []) if _measured(r) is not None]
    result = run_recipe(_recipe_for(doc, rows[0]))
    rate = result.get("removal_rate_A_per_min")
    assert rate and rate > 0
    subs = substituted_axes(result.get("warnings") or [])
    assert subs, "the marker did not reach the result"
    assert not (subs & declined_axes(result.get("warnings") or [])), (
        "an axis cannot be both substituted and declined")


def test_the_bars_this_module_quotes_match_their_owners():
    """Imported, not restated, so a change upstream cannot silently invalidate
    the proof published about it."""
    from tools.flat_prediction_census import SAME as OWNER_SAME
    from tools.residual_census import INERT_TOLERANCE as OWNER_INERT
    assert SAME == OWNER_SAME
    assert INERT_TOLERANCE == OWNER_INERT
    assert 0.0 < TOKEN_SHARE < 0.5
    assert math.isfinite(TOKEN_SHARE)
