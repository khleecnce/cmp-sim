"""How much of a block's MEASURED trend does the prediction actually span?

Why this exists (the §43-§47 ladder, one rung further)
-----------------------------------------------------
The reader audit has asked: who chooses the perturbation (§43), who chooses the
evaluation points (§44), what does the reduction throw away (§45), what family
can it represent (§46), and can it represent anything but a constant (§47).
This module asks the same question of the two readers that answer *"did the
model predict this axis at all?"* -- and both of them are **binary**:

``tools/inert_axis_scan.py``
    ``response < INERT_TOLERANCE`` (0.5 %) => inert.  The bar is applied to the
    PREDICTED response alone; **the measured span is not an input to it.**

``tools/flat_prediction_census.py``
    ``|shape_mape - flat_mape| < 0.05`` pp => the prediction carries no trend.
    That equality is a bar on the SCORE, and the shape score's one free scale
    means any non-zero tilt moves it off the flat baseline a little.

Neither bar contains the measured span, so both can be cleared by a prediction
that moves a token amount against a measurement that moves a great deal.  That
is arithmetic, not a corpus property (see ``proof_*`` below and the enforcing
test): for ANY response above the inert bar there is a measured span large
enough to make the explained share arbitrarily small, and the block is then
reported by every reader here as an ordinary prediction.

The continuous statistic that *could* see this already exists -- the span ratio
in ``tools/ladder_span_probe.py`` -- but it was built for a different question
(is the model collectively too steep?), so it (a) looks only at blocks with
exactly ONE varying axis, which excludes every Taguchi array and every aliased
size sweep here, and (b) has no bar at all: it reports a population geometric
mean, in which a block explaining 10 % of its own trend is one more point below
1.0x rather than a named case.

What this module reports
------------------------
For each scored block, in log space so the shape score's free scale cancels:

    trend_share = ln(max/min PREDICTED) / ln(max/min MEASURED)

1.0 means the prediction spans exactly as much as the data do; 0.0 means it
says nothing about the trend it is being scored on.  Blocks are classified in
priority order so nothing is counted twice:

``declined``   the run declined a swept axis (§36) -- a refusal, not a defect.
``flat``       already reported by ``flat_prediction_census`` -- not new here.
``token``      share below ``TOKEN_SHARE`` while clearing BOTH binary bars.
               This is the band no reader in this repository could report.
``predicting`` everything else.

A ``token`` verdict is a QUESTION, not a bug.  A model is entitled to predict a
weak dependence where the measurement moved a lot -- but then it should say so,
and the repository's rule is that inert is acceptable while *silently* inert is
not.  So each token block is sub-classified by whether ANY reader here already
says something about it:

``token-declared``  the dataset's own ``excluded_axes:`` names an unmodelled
                    quantity the experiment varied.  The block's measured trend
                    belongs to that quantity while ``_varying_axes`` enumerated
                    a *different* one that drifted incidentally across the same
                    rows -- e.g. US9200180B2's benzenesulfonic-acid table, whose
                    pH moves 8.5-8.7 as a by-product.  The honest statement is
                    published but was not machine-readable from the score, which
                    is the §36 failure mode one level out.
``token-substituted``
                    the run says ``[SUBSTITUTED_AXIS: ...]``: a term IS applied
                    and the rate DOES move, but its constant was measured on a
                    different species or regime, so the response is not a test
                    of this system.  Between "declined" and "predicted", and
                    nothing here could express it before §48.
``token-shared``    the constant is deliberately SHARED across several
                    publications and this block is a named member of the group
                    it disagrees with, at the edge of the spread the table
                    already publishes.  Not a defect and not a substitution:
                    it is the price of having fewer constants, and the honest
                    report is the spread, not a per-block exponent.
``token-silent``    nothing in the repository says anything.  This is the band
                    that must not exist quietly.

This module MEASURES ONLY.  It fits nothing and modifies no pack.

Run: .venv/bin/python tools/trend_share_census.py
"""

from __future__ import annotations

import math
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from cmp_sim.core.predictive_score import (  # noqa: E402
    _measured, _predict, _varying_axes, score_all,
)
from cmp_sim.core.declined_axes import substituted_axes  # noqa: E402
from cmp_sim.slurry.abrasive_effects import (  # noqa: E402
    SIZE_EXPONENT_BY_ABRASIVE,
)


def shared_constant_members() -> Dict[str, str]:
    """Dataset name -> the shared-constant group it is a named member of.

    Read from the table at run time, never restated, so adding a sweep to a
    material's provenance list updates this classification with no edit here.
    """
    out: Dict[str, str] = {}
    for kind, row in SIZE_EXPONENT_BY_ABRASIVE.items():
        lo, hi = row["spread"]
        for sweep in row.get("sweeps", ()):
            name = str(sweep).split(" ")[0].strip()
            out[name] = ("abrasive_size_exponent is shared across k=%d sweeps "
                         "for %s (n=%+.2f, members span %+.2f..%+.2f)"
                         % (row["k"], kind, row["value"], lo, hi))
    return out

#: Shared with ``tools/inert_axis_scan.py`` / ``residual_census`` -- imported
#: rather than restated so a change there cannot silently invalidate the proof
#: this module publishes about that bar.
INERT_TOLERANCE = 0.5  # percent change in the predicted rate

#: ``flat_prediction_census.SAME``: below this the shape score and the flat
#: baseline are the same number to the precision either is quoted at.
SAME = 0.05  # percentage points

#: A block explaining less than this fraction of its own measured log-span is
#: reported by name.  0.20 is not a physics constant and nothing is fitted to
#: it: it is the point at which the prediction accounts for less than a fifth
#: of the trend it is scored on, i.e. where quoting the block as evidence about
#: that axis is no longer honest.  The report prints the whole distribution so
#: the reading does not depend on the cut (§34).
TOKEN_SHARE = 0.20

#: Below this the measurement itself barely moved, so the share is a ratio of
#: two small logs and is dominated by rounding in the published table.
MIN_MEASURED_SPAN = 1.05

ROOTS = (Path("cmp_sim/data/validation/datasets"),
         Path("legacy/validation/datasets"))


def _load(name: str) -> Optional[Dict[str, Any]]:
    for root in ROOTS:
        p = root / (name + ".yaml")
        if p.exists():
            return yaml.safe_load(p.read_text(encoding="utf-8"))
    return None


# ── the two incumbent readers, as predicates over (measured, predicted) ──────
# Written against the lists rather than against the corpus so the blindness can
# be demonstrated on synthetic input, which no corpus change can retire.

def _mape(pairs: Sequence[Tuple[float, float]]) -> float:
    return 100.0 * sum(abs(p - m) / m for m, p in pairs) / len(pairs)


def shape_and_flat(measured: Sequence[float],
                   predicted: Sequence[float]) -> Tuple[float, float]:
    """The scorer's two numbers: one free scale, and predict-the-mean.

    This reproduces ``predictive_score.score_dataset``; a test asserts it
    agrees with the shipping scorer on a real block, so the two cannot drift.
    """
    scale = (sum(m * p for m, p in zip(measured, predicted))
             / sum(p * p for p in predicted))
    shape = _mape([(m, scale * p) for m, p in zip(measured, predicted)])
    mean = sum(measured) / len(measured)
    flat = _mape([(m, mean) for m in measured])
    return shape, flat


def reader_inert_says_responsive(predicted: Sequence[float]) -> bool:
    """``inert_axis_scan``'s verdict: does the rate move more than 0.5 %?

    Note what is NOT an argument: the measurement.
    """
    lo, hi = min(predicted), max(predicted)
    if lo <= 0:
        return False
    return 100.0 * (hi - lo) / lo >= INERT_TOLERANCE


def reader_flat_says_predicting(measured: Sequence[float],
                               predicted: Sequence[float]) -> bool:
    """``flat_prediction_census``'s verdict: is the score off the flat one?"""
    shape, flat = shape_and_flat(measured, predicted)
    return abs(shape - flat) >= SAME


def trend_share(measured: Sequence[float],
                predicted: Sequence[float]) -> Optional[float]:
    """Fraction of the measured LOG-span that the prediction spans.

    Log space, and a ratio of ratios, so the shape score's single free
    multiplicative scale cancels exactly and no fit is needed.
    """
    if min(measured) <= 0 or min(predicted) <= 0:
        return None
    m_span = max(measured) / min(measured)
    if m_span < MIN_MEASURED_SPAN:
        return None
    return math.log(max(predicted) / min(predicted)) / math.log(m_span)


# ── the arithmetic proofs, exported so the test cannot paraphrase them ───────

def proof_inert_bar_ignores_the_measurement(measured_span: float
                                           ) -> Dict[str, float]:
    """A response just past the inert bar, against any measured span.

    The bar is a statement about the predicted series alone, so pick a
    prediction that moves 1.2x the tolerance and a measurement that moves
    ``measured_span``: the reader says "responsive" for every span, while the
    explained share falls like 1/ln(span).  No corpus is involved.
    """
    step = 1.0 + 1.2 * INERT_TOLERANCE / 100.0
    predicted = [1.0, math.sqrt(step), step]
    measured = [1.0, math.sqrt(measured_span), measured_span]
    return {
        "responsive": float(reader_inert_says_responsive(predicted)),
        "predicting": float(reader_flat_says_predicting(measured, predicted)),
        "share": trend_share(measured, predicted) or 0.0,
    }


def _substituted_swept(doc: Dict[str, Any], row: Dict[str, Any]) -> set:
    """Axes the RUN declares it predicts with a foreign constant.

    Read from the shipping solver's own warnings rather than from source, so a
    term reached through the inherited dispatchers is seen too.
    """
    from cmp_sim.api import run_recipe
    from cmp_sim.core.predictive_score import _recipe_for
    try:
        result = run_recipe(_recipe_for(doc, row))
    except Exception:
        return set()
    return substituted_axes(result.get("warnings") or [])


@dataclass
class Block:
    dataset: str
    axes: List[str] = field(default_factory=list)
    n: int = 0
    meas_span: float = 1.0
    pred_span: float = 1.0
    share: Optional[float] = None
    shape: float = 0.0
    flat: float = 0.0
    declined: List[str] = field(default_factory=list)
    unmodelled: List[str] = field(default_factory=list)
    substituted: List[str] = field(default_factory=list)
    shared_note: Optional[str] = None
    kind: str = "predicting"


def census(scores=None) -> Dict[str, Any]:
    shared = shared_constant_members()
    blocks: List[Block] = []
    for s in (scores or score_all()):
        if s.shape_mape is None or s.flat_mape is None:
            continue
        doc = _load(s.dataset)
        if not doc:
            continue
        rows = [r for r in (doc.get("conditions") or [])
                if _measured(r) is not None]
        axes = _varying_axes(rows)
        if len(rows) < 3 or not axes:
            continue
        measured: List[float] = []
        predicted: List[float] = []
        for row in rows:
            v = _predict(doc, row)
            if v is None:
                break
            measured.append(float(_measured(row)))
            predicted.append(float(v))
        if len(predicted) != len(rows) or min(measured) <= 0 or min(predicted) <= 0:
            continue
        # The run's own substitution declarations, intersected with what this
        # dataset actually sweeps -- the same question `declined_axes_swept`
        # asks, so a substitution on an axis held constant is not counted.
        subs = sorted(_substituted_swept(doc, rows[0]) & set(axes))
        b = Block(dataset=s.dataset, axes=list(axes), n=len(rows),
                  meas_span=max(measured) / min(measured),
                  pred_span=max(predicted) / min(predicted),
                  share=trend_share(measured, predicted),
                  shape=float(s.shape_mape), flat=float(s.flat_mape),
                  declined=list(s.declined_axes_swept),
                  unmodelled=list(s.unmodelled_quantities),
                  substituted=subs,
                  shared_note=shared.get(s.dataset))
        # Priority order, so no block is counted under two headings.
        if b.declined:
            b.kind = "declined"
        elif abs(b.shape - b.flat) < SAME:
            b.kind = "flat"
        elif b.share is None:
            b.kind = "span-too-small"
        elif b.share < TOKEN_SHARE:
            if b.substituted:
                b.kind = "token-substituted"
            elif b.unmodelled:
                b.kind = "token-declared"
            elif b.shared_note:
                b.kind = "token-shared"
            else:
                b.kind = "token-silent"
        blocks.append(b)

    errs = sorted(b.shape for b in blocks)
    token = [b for b in blocks if b.kind.startswith("token")]
    kept = sorted(b.shape for b in blocks if not b.kind.startswith("token"))
    return {
        "blocks": blocks,
        "token": token,
        "token_silent": [b for b in blocks if b.kind == "token-silent"],
        "token_declared": [b for b in blocks if b.kind == "token-declared"],
        "token_substituted": [b for b in blocks
                              if b.kind == "token-substituted"],
        "token_shared": [b for b in blocks if b.kind == "token-shared"],
        "median_all": errs[len(errs) // 2] if errs else None,
        "median_without_token": kept[len(kept) // 2] if kept else None,
    }


def main() -> int:
    c = census()
    blocks = sorted(c["blocks"], key=lambda b: (b.share is None, b.share or 0))
    print("%-44s %-22s %3s %8s %8s %6s %6s %6s  %s"
          % ("dataset", "axes", "n", "meas", "pred", "share", "shape",
             "flat", "kind"))
    for b in blocks:
        print("%-44s %-22s %3d %7.2fx %7.3fx %6s %6.1f %6.1f  %s"
              % (b.dataset[:44], ",".join(b.axes)[:22], b.n, b.meas_span,
                 b.pred_span,
                 "   n/a" if b.share is None else "%.3f" % b.share,
                 b.shape, b.flat, b.kind))
    print()
    for kind in ("declined", "flat", "span-too-small", "token-substituted",
                 "token-declared", "token-shared", "token-silent",
                 "predicting"):
        n = sum(1 for b in blocks if b.kind == kind)
        print("  %-15s %d" % (kind, n))
    print()

    print("PROOF the two incumbent bars cannot see this band (no corpus):")
    for span in (2.0, 10.0, 80.0):
        p = proof_inert_bar_ignores_the_measurement(span)
        print("  measured span %5.1fx  responsive=%d  predicting=%d  "
              "explained share %.4f"
              % (span, p["responsive"], p["predicting"], p["share"]))
    print()

    if c["token"]:
        print("TOKEN-TREND blocks -- these clear BOTH binary bars while")
        print("spanning less than %.0f%% of their own measured trend:"
              % (100 * TOKEN_SHARE))
        for b in sorted(c["token"], key=lambda b: b.share or 0):
            print("  %-44s %-22s share %.3f  (%.3fx predicted vs %.2fx measured)"
                  % (b.dataset[:44], ",".join(b.axes)[:22], b.share or 0,
                     b.pred_span, b.meas_span))
            print("      %s: %s"
                  % (b.kind,
                     ", ".join(b.substituted) if b.substituted
                     else ", ".join(b.unmodelled) if b.unmodelled
                     else b.shared_note if b.shared_note
                     else "NOTHING in this repository says why"))
        print()

    print("upper median, every block here          : %.1f%%" % c["median_all"])
    print("upper median, token-trend blocks removed: %.1f%%"
          % c["median_without_token"])
    print()
    print("NOTE: the second number is NOT a better score and must never be")
    print("quoted as one -- removing blocks to move a median is forbidden.")
    print("It measures how much of the headline rests on blocks whose")
    print("prediction spans almost none of the trend it is scored against.")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
