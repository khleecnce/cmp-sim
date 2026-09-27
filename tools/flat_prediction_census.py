"""Which blocks does the model score WITHOUT predicting their axis at all?

`ladder_span_probe` found five single-axis blocks whose predicted span is
exactly 1.00x: the model returns the SAME rate for every row while the
experiment sweeps an axis.  Under the shape score's one free scale, a constant
prediction is fitted to the measured mean, so such a block scores exactly the
`flat` baseline the repository added to detect precisely this -- and then
counts toward the headline median as though physics had been tested.

That is the "input ignored" failure the repo distinguishes from "model says no
effect" (limits.md): the first is a wiring bug and the second is a result, and
they are indistinguishable from the score alone.  The difference is whether the
run SAYS so.  `lee2021` is honest -- its oxidizer term is GATED with a cited
reason -- while a block that is silently flat is asserting a default as a
finding.

This probe separates the two across the whole corpus and reports what the
median reads with the silent ones removed, so their contribution to the
headline is a measured number rather than an assumption.  It fits nothing.

Run: .venv/bin/python tools/flat_prediction_census.py
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from cmp_sim.core.predictive_score import score_all  # noqa: E402

# Below this the shape score and the flat baseline are the same number to the
# precision either is quoted at; the prediction carries no trend information.
SAME = 0.05  # percentage points


def census(scores=None):
    rows = [s for s in (scores or score_all())
            if s.shape_mape is not None and s.flat_mape is not None]
    flat = [s for s in rows if abs(s.shape_mape - s.flat_mape) < SAME]
    silent = [s for s in flat if not s.declined_axes_swept]
    declared = [s for s in flat if s.declined_axes_swept]
    errs = sorted(s.shape_mape for s in rows)
    kept = sorted(s.shape_mape for s in rows if s not in silent)
    return {
        "n": len(rows),
        "flat": flat,
        "silent": silent,
        "declared": declared,
        "median_all": errs[len(errs) // 2],
        "median_without_silent": kept[len(kept) // 2],
    }


def main() -> int:
    c = census()
    print("scored blocks                       : %d" % c["n"])
    print("prediction carries NO trend (==flat): %d" % len(c["flat"]))
    print("  of which DECLARED (gated, cited)  : %d" % len(c["declared"]))
    print("  of which SILENT (no stated reason): %d" % len(c["silent"]))
    print()
    for label, group in (("DECLARED", c["declared"]), ("SILENT", c["silent"])):
        if not group:
            continue
        print("%s" % label)
        for s in sorted(group, key=lambda s: -s.shape_mape):
            print("  %-46s %-24s shape %5.1f%% == flat %5.1f%%"
                  % (s.dataset[:46], ",".join(s.axes)[:24],
                     s.shape_mape, s.flat_mape))
        print()
    print("upper median, every scored block        : %.1f%%" % c["median_all"])
    print("upper median, silent-flat blocks removed: %.1f%%"
          % c["median_without_silent"])
    print()
    print("NOTE: the second number is NOT a better score and must never be")
    print("quoted as one -- removing blocks to lower a median is forbidden.")
    print("It measures how much of the headline rests on blocks where the")
    print("model made no prediction about the axis being swept.")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
