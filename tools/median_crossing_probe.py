"""How many datasets must cross the completion bar, and WHICH are nearest?

The completion bar (`tests/test_definition_of_done.py`) is the UPPER median of
the per-dataset shape errors: `sorted(errors)[n//2]`.  That statistic is a
COUNTING statistic, not an averaging one: it is <= B exactly when at least
`n//2 + 1` datasets score <= B.  So the remaining distance to the bar is not
"3.2 percentage points spread over the corpus" -- it is an integer number of
datasets that must cross a threshold, and everything else may stay exactly
where it is.

This probe reports that integer and the ordered shortlist of nearest crossers,
so a session spends its effort on a block that can actually move the headline
instead of on the worst-scoring block (which cannot: improving a dataset that
is already above the median, but not below the bar, moves the median by zero).

It fits nothing and changes no pack.  Run:  python tools/median_crossing_probe.py
"""

from __future__ import annotations

import sys

from cmp_sim.core.predictive_score import score_all


def crossing_report(bar: float = 15.0, scores=None):
    rows = [r for r in (scores or score_all()) if r.shape_mape is not None]
    errs = sorted(r.shape_mape for r in rows)
    n = len(errs)
    median_idx = n // 2
    median = errs[median_idx]
    under = sum(1 for e in errs if e <= bar)
    # upper median <= bar  <=>  errs[n//2] <= bar  <=>  at least n//2+1 under bar
    needed = max(0, (median_idx + 1) - under)
    nearest = sorted(
        (r for r in rows if r.shape_mape > bar), key=lambda r: r.shape_mape
    )
    # A dataset whose OWN replicate scatter is already at or above the bar
    # cannot honestly be driven under it: below its own noise the remaining
    # "error" is the measurement, and fitting it is fitting noise (limit 17).
    def _floor(r):
        rep = getattr(r, "replicate_scatter", None)
        return None if rep is None else round(rep, 1)

    return {
        "n": n,
        "median": median,
        "bar": bar,
        "under_bar": under,
        "required_under_bar": median_idx + 1,
        "datasets_that_must_cross": needed,
        "nearest": [(r.dataset, r.shape_mape, _floor(r)) for r in nearest[:8]],
        "headroom_of_the_binding_dataset": (
            None if not nearest else round(nearest[0].shape_mape - bar, 2)),
    }


def main() -> int:
    bar = float(sys.argv[1]) if len(sys.argv) > 1 else 15.0
    rep = crossing_report(bar)
    print(f"corpus            : {rep['n']} scored datasets")
    print(f"median (upper)    : {rep['median']:.1f}%")
    print(f"completion bar    : {rep['bar']:.1f}%")
    print(f"already <= bar    : {rep['under_bar']}")
    print(f"needed <= bar     : {rep['required_under_bar']}")
    print(f"MUST CROSS        : {rep['datasets_that_must_cross']} dataset(s)")
    print()
    print("nearest datasets above the bar (cheapest crossers first):")
    for name, err, floor in rep["nearest"]:
        note = "" if floor is None else f"   (own replicate scatter {floor}%)"
        print(f"  {err:6.1f}%  {name}{note}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
