"""docs/limits.md §47 — a per-pack coherence verdict can only represent ONE
CONSTANT OFFSET, so a scale that TRENDS along a condition is filed as
"the blocks disagree".

Every assertion here RE-MEASURES. Pinning today's counts (8 blocks, p_perm
0.009, 59x spread) would go stale the moment a dataset or a Kp lands, and a true
statement failing invites the next session to edit the number rather than
re-run the probe (the mistake limits §31 records).

The motivating defect is ARITHMETIC — a symmetry of the reduction — so the
first two tests prove it on synthetic input and cannot expire with the corpus.
"""
from __future__ import annotations

import math
import statistics

import pytest

from tools.scale_coherence_trend_probe import (
    MIN_BLOCKS, P_BAR, axis_trend, blocks, coherence_pair,
    cross_block_measured_exponent, report, verdicts,
    within_block_pressure_control,
)


# ── the blindness, proved without the corpus ────────────────────────────────
def test_the_coherence_pair_is_invariant_to_which_block_holds_which_scale():
    """Permute the assignment and (median, spread) are EXACTLY unchanged.

    That is the whole defect: the reduction's inputs are a multiset, so no
    condition can enter it. Proved on synthetic values so it cannot go stale.
    """
    scales = [0.06, 0.08, 0.31, 0.49, 1.09, 1.66, 3.24, 3.38]
    base = coherence_pair(scales)
    for shuffled in (list(reversed(scales)),
                     [scales[i] for i in (3, 0, 7, 1, 5, 2, 6, 4)]):
        assert coherence_pair(shuffled) == base


def test_a_perfect_trend_and_pure_scatter_reduce_identically():
    """Two packs, same scale VALUES, opposite structure, same verdict.

    One has log-scale falling monotonically with pressure; the other has the
    same values in an order uncorrelated with it. `coherence_pair` cannot
    separate them, while the trend statistic separates them decisively.
    """
    pressures = [1.0, 1.5, 2.0, 2.75, 4.0, 7.0]
    values = [3.4, 3.2, 1.7, 0.5, 0.31, 0.06]
    scrambled = [1.7, 0.06, 3.4, 3.2, 0.31, 0.5]
    assert sorted(values) == sorted(scrambled)
    assert coherence_pair(values) == coherence_pair(scrambled)

    xs = [math.log(p) for p in pressures]
    trend = axis_trend("pressure_psi", xs, [math.log10(v) for v in values])
    scatter = axis_trend("pressure_psi", xs,
                         [math.log10(v) for v in scrambled])
    assert trend is not None and scatter is not None
    assert trend.trending, trend
    assert not scatter.trending, scatter


def test_a_null_is_mandatory_because_the_populations_are_tiny():
    """A large |r| on MIN_BLOCKS points must not count on its own.

    With n = 4 the permutation null has only 4! = 24 orderings, so the smallest
    p-value ANY 4-point block can attain is 1/24 = 0.042 — reached solely by the
    single perfectly-ordered arrangement. A 4-block pack is therefore admitted
    as trending only in that one extreme case, and anything short of it (here
    |r| = 0.90, which reads as overwhelming to the eye) must not be: that is
    precisely the judgement a correlation-size bar would get wrong.
    """
    assert 1.0 / math.factorial(MIN_BLOCKS) < P_BAR < 2.0 / MIN_BLOCKS, (
        "the bar must be reachable by a perfect ordering at MIN_BLOCKS and "
        "still exclude near-misses; if MIN_BLOCKS or P_BAR moves, re-derive "
        "this rather than widening the assertion")
    xs = [math.log(v) for v in (1.0, 2.0, 3.0, 4.0)]
    strong = axis_trend("pressure_psi", xs, [-0.10, -0.40, -0.50, -0.90])
    assert strong is not None
    assert abs(strong.r) > 0.9, strong
    assert not strong.trending, (
        "|r| = %.2f on 4 points must NOT be called a trend: its own "
        "permutation null does not clear the bar" % strong.r)


# ── the corpus reading, re-measured ─────────────────────────────────────────
def test_the_probe_has_something_to_measure():
    """Non-vacuity: a probe whose population empties passes everything."""
    vs = verdicts()
    assert vs, "no pack has enough comparable blocks — the probe is vacuous"
    assert any(v.trends for v in vs), (
        "no pack shares a condition axis across its blocks; the trend "
        "question is unasked rather than answered")


def test_the_incumbent_incoherent_verdict_is_reproduced_here():
    """This probe must agree with `absolute_scale_audit` on the incumbent
    statistic, or it is auditing something else."""
    from tools.absolute_scale_audit import by_pack, collect

    mine = {v.pack: round(v.spread_log, 9) for v in verdicts()}
    theirs = {}
    for v in by_pack(collect()):
        if len(v.blocks) >= MIN_BLOCKS:
            theirs[v.pack] = round(max(v.log_scales) - min(v.log_scales), 9)
    shared = set(mine) & set(theirs)
    assert shared, "the two probes share no pack — one of them is mis-grouping"
    for pack in sorted(shared):
        assert mine[pack] == pytest.approx(theirs[pack], abs=1e-6), pack


def test_any_trending_pack_is_reported_and_not_wired():
    """A trend that survives the null is REPORTED, never fitted.

    A cross-block slope is a per-publication offset until a controlled reading
    confirms it; fitting it is the move limits §14 forbids. So the requirement
    is that the probe names it AND that the report states the control's answer.
    """
    text = report()
    trending = [(v, t) for v in verdicts() for t in v.trending_axes]
    if trending:
        for v, t in trending:
            assert v.pack in text and t.axis in text
        assert "CONFOUND CONTROL" in text
    else:
        assert "none in today's corpus" in text


def test_the_cross_block_trend_is_not_promoted_without_the_control():
    """The exit condition, stated as a measurement.

    §47's conclusion — the cross-block trend is a confound, not a law — rests
    on two things that are re-measured here rather than quoted:

      (a) the WITHIN-block pressure slopes straddle zero
          (`pressure_saturation_probe`), and
      (b) the cross-block MEASURED-rate exponent has the wrong SIGN for
          Preston, i.e. the trend is not about pressure at all.

    If either stops holding, this test fails and the next session must re-open
    the question with numbers instead of inheriting the verdict.
    """
    _, neg, tot = within_block_pressure_control()
    assert tot >= 3, "too few multi-pressure blocks to run the control"
    straddles = neg not in (0, tot)

    trending = [(v, t) for v in verdicts()
                for t in v.trending_axes if t.axis == "pressure_psi"]
    if not trending:
        pytest.skip("no pack's scale trends with pressure in today's corpus")

    bs = blocks()
    for v, _t in trending:
        b_meas = cross_block_measured_exponent(v.pack, "pressure_psi", bs)
        assert b_meas is not None
        assert straddles and b_meas < 1.0, (
            f"{v.pack}: the cross-block pressure trend now survives its "
            f"controls (within-block straddles zero: {straddles}; cross-block "
            f"measured exponent {b_meas:+.2f} vs Preston's +1). §47 was "
            "written on the opposite reading — re-measure and rewrite the "
            "entry rather than relaxing this assertion.")


def test_the_audit_no_longer_claims_incoherent_exonerates_kp():
    """The over-claim is removed from the incumbent probe itself.

    A correction that lives only in docs/limits.md leaves the wrong sentence
    where the next reader will find it.
    """
    from tools import absolute_scale_audit as audit

    doc = audit.PackVerdict.coherent.__doc__ or ""
    assert "Kp is not the problem" not in doc
    assert "no single constant fits" in doc
    assert "47" in doc, "the docstring must point at the limits entry"
    text = audit.report()
    assert "Kp is not the cause" not in text


def test_the_corpus_median_did_not_move():
    """An honesty fix that changes a prediction is a bug, not a fix.

    Nothing here touches a pack, a constant or a solver path, so the headline
    must be bit-identical to the published number. Asserted on the UPPER median
    (`sorted(e)[n//2]`), the convention the README and the bar use — it has no
    parity discontinuity.
    """
    from cmp_sim.core.predictive_score import score_all

    errs = sorted(s.shape_mape for s in score_all() if s.shape_mape is not None)
    upper = errs[len(errs) // 2]
    assert upper == pytest.approx(18.9, abs=0.1), (
        f"median shape is {upper:.1f}%, expected the published 18.9%. §47 is "
        "a reader correction: if it moved a prediction, find what it touched.")
    # and the statistic the probe reads is the SCALE, which is likewise untouched
    scales = [s.scale_ratio for s in score_all() if s.scale_ratio is not None]
    assert len(scales) >= 30
    assert statistics.median(scales) == pytest.approx(1.12, abs=0.05)
