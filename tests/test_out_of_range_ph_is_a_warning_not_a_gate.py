"""Out-of-range pH is a WARNING, not a gate — and the measurement says so.

Declaring `ph_valid_range` on every pH-active pack switched on out-of-range
warnings for fifteen datasets. The obvious next step looked like gating them:
`score_dataset` already has the declined machinery built for
`oxidizer_ph_window`, so refusing to score an unsupported extrapolation would be
a three-line change.

IT WOULD ALSO BE WRONG, and the corpus says so before any code is written.

Splitting the scored datasets by whether every row sits inside its pack's
declared pH range:

    fully in-range        n=19   median 18.9%   mean 19.8%
    fully out-of-range    n=11   median 19.4%   mean 20.8%

Mann-Whitney U = 101.0 against an expected 104.5 under the null, z = -0.15.
There is no detectable difference. Out-of-range prediction here is not degraded
prediction — it is prediction whose pH term happens to be evaluated on its
floor or its flank rather than near its optimum, which is a perfectly ordinary
thing for a bounded function to do.

And the out-of-range group contains some of the best results in the corpus:
bouvet2002_w 2.3%, ep3161098b1 7.1%, lai2001 8.7%, bouvet2002_oxide 11.2%,
us8142675b2 12.3%. Gating would throw those away and replace them with silence.

WHY THIS DIFFERS FROM THE OXIDISER GATE, which WAS justified: there, Miranda's
2x2 showed the oxidiser term's SIGN reversing across the pH branch — the model
was confidently wrong in a direction no refit could fix, and declining was the
only honest answer. Here the model is not wrong; it is merely less constrained.
A gate is for "this prediction would be wrong", not for "this prediction rests
on fewer measurements". The second case is what warnings and confidence fields
are for.

THE ONE REAL FAILURE MODE IS ALREADY HANDLED SEPARATELY: an acid-side floor of
zero, where the rate decays to 0.00 A/min. That is caught by its own warning
naming it a refusal (see test_ph_validity_range_is_declared.py) and does not
need a corpus-wide gate to express it.

So: the range is declared, the warning fires, the score stands. This test exists
so that the next person who sees fifteen warnings and reaches for the gate has
to first explain away z = -0.15.
"""
from __future__ import annotations

import statistics

import yaml

from cmp_sim.core.params import load_pack
from cmp_sim.core.predictive_score import score_dataset
from cmp_sim.core.validation import dataset_paths


def _declared_range(pack_name: str):
    if not pack_name:
        return None
    try:
        param = load_pack(pack_name).param("ph_valid_range")
    except Exception:
        return None
    return param.value if hasattr(param, "value") else param


def _split_by_range():
    """(in_range_errors, out_of_range_errors) over scorable datasets."""
    inside, outside = [], []
    for path in dataset_paths():
        doc = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        span = _declared_range(doc.get("pack") or "")
        if not span:
            continue
        phs = [(row.get("overrides") or {}).get("slurry_ph")
               for row in (doc.get("conditions") or [])]
        phs = [ph for ph in phs if ph is not None]
        if not phs:
            continue
        try:
            score = score_dataset(path)
        except Exception:
            continue
        if score.shape_mape is None:
            continue
        out_fraction = sum(1 for ph in phs
                           if not span[0] <= ph <= span[1]) / len(phs)
        if out_fraction == 0.0:
            inside.append((path.stem, score.shape_mape))
        elif out_fraction == 1.0:
            outside.append((path.stem, score.shape_mape))
    return inside, outside


def test_both_groups_are_large_enough_to_compare():
    inside, outside = _split_by_range()
    assert len(inside) >= 15, len(inside)
    assert len(outside) >= 8, len(outside)


def test_out_of_range_prediction_is_not_measurably_worse():
    """The measurement that makes a gate unjustified."""
    inside, outside = _split_by_range()
    in_errors = [e for _, e in inside]
    out_errors = [e for _, e in outside]

    in_median = statistics.median(in_errors)
    out_median = statistics.median(out_errors)

    assert out_median < in_median + 6.0, (
        f"out-of-range median {out_median:.1f}% vs in-range {in_median:.1f}%. "
        "If out-of-range prediction has become measurably worse, revisit the "
        "decision recorded here: a gate may now be justified.")


def test_the_rank_sum_shows_no_separation():
    """Mann-Whitney by hand: |z| should be small, not merely the medians close."""
    inside, outside = _split_by_range()
    in_errors = [e for _, e in inside]
    out_errors = [e for _, e in outside]

    n1, n2 = len(out_errors), len(in_errors)
    u = (sum(1 for a in out_errors for b in in_errors if a < b)
         + 0.5 * sum(1 for a in out_errors for b in in_errors if a == b))
    mu = n1 * n2 / 2
    sigma = (n1 * n2 * (n1 + n2 + 1) / 12) ** 0.5
    z = (u - mu) / sigma

    assert abs(z) < 1.5, (
        f"z={z:+.2f}: the two groups have separated. The no-gate decision was "
        "based on z=-0.15; re-derive it before trusting this test's conclusion.")


def test_the_out_of_range_group_contains_excellent_predictions():
    """Concretely what a gate would discard."""
    _inside, outside = _split_by_range()
    excellent = sorted(e for _, e in outside if e < 15.0)
    assert len(excellent) >= 4, (
        f"only {len(excellent)} out-of-range datasets under 15% error; the "
        "argument that gating discards good predictions rests on these")


def test_out_of_range_datasets_are_still_scored_not_declined():
    """The decision itself, asserted against the engine.

    Note `gated` counts gates of ANY kind, and some of these datasets carry an
    unrelated one (lai2001 declares an oxidiser-data gap). What must not happen
    is a gate whose REASON is the pH range, and a score being withheld.
    """
    _inside, outside = _split_by_range()
    for stem, error in outside:
        score = score_dataset(next(p for p in dataset_paths()
                                   if p.stem == stem))
        reason = (score.gated_reason or "").lower()
        assert "ph_valid_range" not in reason and "outside the range" not in reason, (
            f"{stem} is being declined for pH range; that gate was measured to "
            f"be unjustified (z=-0.15). Reason given: {score.gated_reason}")
        # and the score itself still stands
        assert score.shape_mape == error
