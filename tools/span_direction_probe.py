"""A span RATIO is a magnitude, not an association: does the model move the
RIGHT WAY on each ladder?

`ladder_span_probe` reduces each single-axis block to

    span_ratio = (max/min of PREDICTED) / (max/min of MEASURED)

and this repository's reading of the residual-sign skew (docs/limits.md §36)
rests on the resulting population ("median 0.86x, 15 of 20 UNDER-spread").
That reduction is deliberately fit-free -- the scorer's one free multiplicative
scale cancels out of a ratio of ratios -- but it throws away the PAIRING
between a predicted value and the measured value taken at the same condition.
Both spans are computed over the same rows, so nothing is mis-selected; the
loss is elsewhere and is exactly §44's question asked about a reduction rather
than about an evaluation point:

    a block whose prediction excursion is the right SIZE but points the wrong
    WAY scores span_ratio ~ 1.00x, i.e. indistinguishable from perfect
    agreement.

That failure mode is reachable here, not hypothetical: the chemistry layer
carries peaked terms (the pH gaussian, the oxidiser Langmuir), so a query sweep
that straddles a declared optimum can move the prediction DOWN where the
measurement moves UP, over a similar number of decades.  A non-monotonic model
compared to a monotonic experiment is the one case a span magnitude cannot see.

So this probe re-reads every block `ladder_span_probe` reads and publishes,
next to the span ratio:

  * `r_log`  -- Pearson correlation of log(predicted) against log(measured)
     across the block's rows.  Logs because the scorer's error is
     multiplicative and its free scale is an additive offset in logs, so `r`
     is invariant to it exactly as the span ratio is.  This is a DIRECTION
     statistic, not a goodness-of-fit: it cannot be improved by scaling.
  * `extremes_pair` -- whether the prediction's argmax/argmin rows are the
     measurement's argmax/argmin rows.  When they are not, the two spans in
     `ladder_span_probe` are excursions between DIFFERENT pairs of conditions,
     which is the mechanism by which a direction error hides inside a
     magnitude that looks right.

The probe proposes nothing.  Per this repository's rule, a residual with a
known sign is a derivation target and fitting an offset to it destroys the
evidence (docs/limits.md §14).  Its output is a classification, and the
honest result may well be that no block dissents -- in which case the §36
reading stands on a measurement rather than on an assumption, which is the
point of running it.

Run: .venv/bin/python tools/span_direction_probe.py
"""

from __future__ import annotations

import math
import statistics
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from cmp_sim.core.predictive_score import (  # noqa: E402
    _measured, _predict, _varying_axes, score_all,
)

ROOTS = (Path("cmp_sim/data/validation/datasets"),
         Path("legacy/validation/datasets"))

#: Below this, a log-space correlation is called `anti` -- the prediction moves
#: against the measurement.  Exactly 0.0 is the bar because the claim being
#: tested is a SIGN claim; a magnitude bar would be a fitted threshold.
ANTI_BAR = 0.0


def _load(name: str):
    for root in ROOTS:
        p = root / (name + ".yaml")
        if p.exists():
            return yaml.safe_load(p.read_text(encoding="utf-8"))
    return None


def pearson(a, b):
    """Pearson r, or None when either series is constant (no direction)."""
    ma, mb = statistics.fmean(a), statistics.fmean(b)
    sa = math.sqrt(sum((x - ma) ** 2 for x in a))
    sb = math.sqrt(sum((x - mb) ** 2 for x in b))
    if sa == 0.0 or sb == 0.0:
        return None
    return sum((x - ma) * (y - mb) for x, y in zip(a, b)) / (sa * sb)


def block(name: str, declined_axes) -> dict | None:
    """Re-read one single-axis block exactly as `ladder_span_probe` does."""
    doc = _load(name)
    if not doc:
        return None
    rows = [r for r in (doc.get("conditions") or []) if _measured(r) is not None]
    axes = _varying_axes(rows)
    if len(axes) != 1 or len(rows) < 3:
        return None
    m, q = [], []
    for r in rows:
        v = _predict(doc, r)
        if v is None:
            return None
        m.append(_measured(r))
        q.append(v)
    if min(m) <= 0 or min(q) <= 0:
        return None
    lm = [math.log(x) for x in m]
    lq = [math.log(x) for x in q]
    imax = lambda s: max(range(len(s)), key=lambda i: s[i])  # noqa: E731
    imin = lambda s: min(range(len(s)), key=lambda i: s[i])  # noqa: E731
    return {
        "dataset": name,
        "axis": axes[0],
        "n": len(m),
        "span_ratio": (max(q) / min(q)) / (max(m) / min(m)),
        "r_log": pearson(lm, lq),
        "extremes_pair": imax(m) == imax(q) and imin(m) == imin(q),
        # A declined axis predicts a constant, so it has no direction at all;
        # counting it as agreement or as dissent would both be wrong.
        "declined": axes[0] in set(declined_axes),
    }


def survey() -> list[dict]:
    out = []
    for s in score_all():
        if s.shape_mape is None:
            continue
        b = block(s.dataset, s.declined_axes_swept)
        if b:
            # Carried so the "this reader finds nothing the repository was not
            # already flagging" claim is CHECKED rather than asserted: a block
            # that fails to beat predicting its own measured mean is already
            # published as a failure by score_report.
            b["beats_flat"] = s.beats_flat
            out.append(b)
    out.sort(key=lambda b: (b["r_log"] if b["r_log"] is not None else 9.0))
    return out


def classify(b: dict) -> str:
    if b["declined"]:
        return "declined"
    if b["r_log"] is None:
        return "no-direction"
    if b["r_log"] < ANTI_BAR:
        return "anti"
    if not b["extremes_pair"]:
        return "non-monotonic"
    return "agrees"


def main() -> int:
    out = survey()
    print("single-axis blocks measured: %d\n" % len(out))
    print("%-40s %-18s %3s %8s %7s %6s  %s"
          % ("dataset", "axis", "n", "span", "r_log", "pair", "verdict"))
    for b in out:
        r = b["r_log"]
        print("%-40s %-18s %3d %7.2fx %7s %6s  %s"
              % (b["dataset"][:40], b["axis"][:18], b["n"], b["span_ratio"],
                 "n/a" if r is None else "%.2f" % r,
                 "yes" if b["extremes_pair"] else "NO", classify(b)))

    buckets: dict[str, list[dict]] = {}
    for b in out:
        buckets.setdefault(classify(b), []).append(b)
    print()
    for k in ("anti", "non-monotonic", "no-direction", "agrees", "declined"):
        print("  %-14s %d" % (k, len(buckets.get(k, []))))

    print()
    print("WHAT A NON-ZERO `anti` COUNT WOULD MEAN:")
    print("  span_ratio ~ 1.00x on such a block reads as perfect agreement in")
    print("  ladder_span_probe, so the §36 population reading would be built")
    print("  partly from blocks the model gets BACKWARDS.  The repair is in")
    print("  the physics of the peaked term, never in the span statistic.")
    print()
    print("WHAT A ZERO COUNT MEANS (do not skip this):")
    print("  it is a measurement of THIS corpus, not a proof that the span")
    print("  reduction is safe.  One sweep straddling a declared optimum in")
    print("  the opposite direction to its data reopens it, so the enforcing")
    print("  test re-measures rather than pinning today's counts.")
    print()
    print("IS ANY `anti` BLOCK NEW INFORMATION?")
    print("  A block that already fails `beats_predicting_the_mean` in")
    print("  score_report is published as a failure, so finding it here adds a")
    print("  MECHANISM, not a defect count. A block that BEATS the mean while")
    print("  pointing backwards would be new -- and unreported anywhere else.")
    for b in out:
        if classify(b) in ("anti", "non-monotonic"):
            print("  %-42s %-14s beats_mean=%s"
                  % (b["dataset"][:42], classify(b), b.get("beats_flat")))

    worst = [b for b in out if not b["declined"] and b["r_log"] is not None]
    if worst:
        rs = [b["r_log"] for b in worst]
        print()
        print("predicting blocks: %d   median r_log %.2f   min %.2f (%s)"
              % (len(rs), statistics.median(rs), min(rs),
                 min(worst, key=lambda b: b["r_log"])["dataset"]))

    # Does §37's verdict depend on the anti blocks? §37 concluded "no
    # detectable corpus-wide under-response" from a sign test over the
    # PREDICTING population. An anti block is not a weak prediction, it is a
    # prediction pointing the other way, so whether its span ratio lands above
    # or below 1 carries no information about response STRENGTH. Print the
    # sign test both ways rather than asserting which is right.
    print()
    print("DOES §37's SIGN TEST DEPEND ON THE ANTI BLOCKS?")
    for tag, grp in (("predicting (§37's population)", worst),
                     ("predicting minus anti       ",
                      [b for b in worst if b["r_log"] >= ANTI_BAR])):
        r = [b["span_ratio"] for b in grp]
        if not r:
            continue
        k = sum(1 for x in r if x < 1.0)
        gm = math.exp(statistics.fmean(math.log(x) for x in r))
        print("  %s n=%2d  geo-mean %.2fx  under %d/%d  p=%.3f"
              % (tag, len(r), gm, k, len(r), _sign_test_p(len(r), k)))
    return 0


def _sign_test_p(n: int, k: int) -> float:
    """Two-sided sign test, re-used from `ladder_span_probe` by import so the
    two probes cannot drift apart on the arithmetic §37's verdict rests on."""
    from tools.ladder_span_probe import sign_test_p
    return sign_test_p(n, k)


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
