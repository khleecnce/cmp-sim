"""Does the model OVER-SPREAD every ladder?

`ladder_end_residual_probe` found the worst row's POSITION is uniform (bottom
5 / middle 7 / top 6 of 18) but its SIGN is not: 15 of 18 are over-predictions
against a fair-coin expectation of 9.  Position-uniform plus sign-skewed rules
out a missing end-correction and points at a different structural statement:
under a single free scale, a right-skewed residual set is what you get when the
model's response spans MORE than the measurement does.  The fit then parks most
rows slightly under and one row far over.

So this probe asks the question directly, per block, with no fitting at all:

    span_ratio = (max/min of PREDICTED) / (max/min of MEASURED)

The free scale cancels out of a ratio of ratios, so this number is independent
of the calibration the shape score gives away for free.  > 1 means the model
responds more strongly to the swept axis than the experiment did; < 1 means
less.  A population centred on 1 would say the sign skew is an artefact; a
population sitting above 1 says every exponent-bearing term in the chain is
collectively too steep, which is one claim rather than eighteen.

IMPORTANT -- this probe deliberately does NOT propose a shared damping factor.
Fitting an offset to a residual reproduces that residual by construction and
destroys the evidence that a term is missing (limits.md §14).  Its output is a
direction and a magnitude for a derivation to aim at, plus the list of blocks
that DISSENT, which is where the physics actually is.

Run: .venv/bin/python tools/ladder_span_probe.py
"""

from __future__ import annotations

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


def _load(name: str):
    for root in ROOTS:
        p = root / (name + ".yaml")
        if p.exists():
            return yaml.safe_load(p.read_text(encoding="utf-8"))
    return None


def span_report(name: str):
    doc = _load(name)
    if not doc:
        return None
    rows = [r for r in (doc.get("conditions") or [])
            if _measured(r) is not None]
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
    meas_span = max(m) / min(m)
    pred_span = max(q) / min(q)
    return {
        "dataset": name,
        "axis": axes[0],
        "n": len(m),
        "meas_span": meas_span,
        "pred_span": pred_span,
        "ratio": pred_span / meas_span,
    }


def main() -> int:
    scored = [s for s in score_all() if s.shape_mape is not None]
    out = [b for b in (span_report(s.dataset) for s in scored) if b]
    out.sort(key=lambda b: -b["ratio"])

    print("single-axis blocks measured: %d\n" % len(out))
    print("%-46s %-20s %4s %9s %9s %7s"
          % ("dataset", "axis", "n", "meas span", "pred span", "ratio"))
    for b in out:
        print("%-46s %-20s %4d %8.2fx %8.2fx %6.2fx"
              % (b["dataset"][:46], b["axis"][:20], b["n"],
                 b["meas_span"], b["pred_span"], b["ratio"]))

    ratios = [b["ratio"] for b in out]
    over = sum(1 for r in ratios if r > 1.0)
    print()
    print("median span ratio : %.2fx" % statistics.median(ratios))
    print("over-spread (>1)  : %d of %d" % (over, len(ratios)))
    print("under-spread (<1) : %d of %d" % (len(ratios) - over, len(ratios)))
    print()
    print("DISSENTERS (ratio < 1 -- the model responds LESS than the data):")
    for b in out:
        if b["ratio"] < 1.0:
            print("  %-46s %-20s %.2fx"
                  % (b["dataset"][:46], b["axis"][:20], b["ratio"]))
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
