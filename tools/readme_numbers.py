"""Print every number the README claims, recomputed from the scorer.

tests/test_readme_numbers_are_computed.py asserts the README against these;
this script exists so a session can regenerate them without re-deriving the
test's internals.
"""
from __future__ import annotations

import collections
import statistics as st

from cmp_sim.core.predictive_score import score_all


def main() -> None:
    scores = [s for s in score_all() if s.shape_mape is not None]

    by_axis = collections.defaultdict(list)
    for s in scores:
        for axis in s.axes:
            by_axis[axis].append(s.shape_mape)
    print("AXIS TABLE")
    for axis, values in sorted(by_axis.items(), key=lambda kv: st.median(kv[1])):
        print(f"  {axis:24s} {len(values):3d} {st.median(values):5.1f}%")

    shape = sorted(s.shape_mape for s in scores)
    loo = sorted(s.loo_mape for s in scores if s.loo_mape is not None)
    print("\nHEADLINE")
    print(f"  median shape {st.median(shape):.1f}%  median LOO {st.median(loo):.1f}%")
    print(f"  {len(scores)} datasets, {sum(s.n for s in scores)} points")
    print(f"  beats predict-the-mean: {sum(1 for s in scores if s.beats_flat)}")

    scaled = [s for s in scores if s.scale_ratio is not None]
    off = [s for s in scaled if not s.scale_is_calibrated]
    print("\nSCALE")
    print(f"  comparable {len(scaled)}, off >3x {len(off)}, within 3x {len(scaled) - len(off)}")
    for s in sorted(off, key=lambda s: -max(s.scale_ratio, 1 / s.scale_ratio)):
        print(f"    {s.dataset:50s} {s.scale_ratio:8.2f}x  shape {s.shape_mape:5.1f}%")


if __name__ == "__main__":
    main()
