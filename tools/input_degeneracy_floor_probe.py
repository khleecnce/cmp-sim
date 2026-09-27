"""What is the LOWEST shape error this corpus can reach with the inputs the
model actually receives?  Measured, not argued.

Why this exists
---------------
STATUS.md carries a standing instruction from the owner: the completion bar may
be relaxed above 10% only if the session first writes down *what creates the
lower bound on the error* -- "what makes it hard" is not an answer, "this
quantity is provably unreachable" is.  Two candidate bounds have been offered
before and both were refuted:

* the measurement-reproducibility floor (docs/limits.md, 15th session): only a
  minority of the corpus publishes replicates, and where it does the scatter
  runs 1.5%-37%, so there is no corpus-wide noise floor;
* "the remaining datasets are just hard", which is not a bound at all.

This probe measures a third bound that needs no replicate data, no fitting and
no new constant, and that no functional form can evade:

    **input degeneracy** -- two measured rows that the model cannot tell apart.

The prediction is a deterministic function of the input vector the harness
builds.  When a dataset varies a quantity the recipe has no field for (the
abrasive VENDOR in tw202115224a; the particle SHAPE in the same table), two
rows arrive at the solver as the *same* input and therefore leave with the
*same* prediction -- while the published rates differ.  No change to the
physics can separate them, because the separating information never enters the
model.  The error contributed by such a group is irreducible *for this input
schema*, and it is computable exactly.

Method
------
For each scored dataset, predictions are taken from the shipping solver (same
path ``predictive_score`` scores with, so a gate or a declined axis is honoured
identically).  Rows are grouped by identical prediction.  Each group is then
given its OWN free multiplicative constant -- strictly MORE freedom than the
real scorer, which allows one scale for the whole dataset -- and that constant
is chosen to minimise the group's contribution to the MAPE.  The resulting
per-dataset MAPE is therefore a valid LOWER BOUND on the shape score of any
model, however derived, that reads only the inputs this harness supplies.

Because each group gets a free constant, a dataset with no degeneracy scores a
floor of exactly 0.0% -- the probe says nothing about it, which is the correct
answer: nothing in ITS structure stops a better model from fitting it.

The optimum constant is a weighted median.  ``sum |c - m_i| / m_i`` is
piecewise linear in ``c`` with breakpoints at the measured values, so the
minimum is attained AT one of them; evaluating all of them is exact and needs
no optimiser.

Usage
-----
    .venv/bin/python tools/input_degeneracy_floor_probe.py [--held-out]
"""
from __future__ import annotations

import sys
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Optional, Tuple

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import yaml

from cmp_sim.core.predictive_score import (
    _measured,
    _predict_with_gate,
    _varying_axes,
    score_all,
)
from cmp_sim.core.validation import dataset_paths


def _best_constant(measured: List[float]) -> float:
    """The constant minimising sum |c - m| / m over a tied group (exact).

    Piecewise linear in c with breakpoints at the measured values, so the
    minimiser is one of them.  Ties broken by the smaller value for
    determinism.
    """
    best, best_cost = None, None
    for cand in sorted(measured):
        cost = sum(abs(cand - m) / m for m in measured)
        if best_cost is None or cost < best_cost - 1e-15:
            best, best_cost = cand, cost
    return float(best)


def _key(value: float) -> float:
    """Group predictions that are equal to within float noise.

    Rounding to 12 significant figures: two rows built from the same input
    vector travel the same code path and agree bit-for-bit, so this only
    absorbs formatting noise, never physically distinct predictions.
    """
    if value == 0.0:
        return 0.0
    return float(f"{value:.12e}")


class DatasetFloor:
    def __init__(self, dataset: str, n: int, floor: float,
                 groups: List[List[float]], axes: List[str],
                 declined: List[str]) -> None:
        self.dataset = dataset
        self.n = n
        self.floor = floor
        #: measured values of every group holding more than one row
        self.tied_groups = [g for g in groups if len(g) > 1]
        self.n_groups = len(groups)
        self.axes = axes
        #: axes the run explicitly DECLINED to predict (core.declined_axes)
        self.declined = declined

    @property
    def tied_rows(self) -> int:
        return sum(len(g) for g in self.tied_groups)

    @property
    def is_flat(self) -> bool:
        """One group for the whole dataset = a constant prediction.

        This distinction decides whether the floor is a BOUND or merely a
        description of today's model.  A flat prediction is a *declared
        refusal* (docs/limits.md §36): the pack states it has no constants for
        the axis swept.  Supplying those constants makes the prediction vary
        and the "floor" evaporates.  Genuine degeneracy is the opposite -- the
        rows differ in a quantity the input schema has no field for, so no
        constant, however measured, can separate them.
        """
        return self.n_groups == 1


def dataset_floor(path: Path) -> Optional[DatasetFloor]:
    """Floor computed on EXACTLY the rows the scorer grades.

    This alignment is load-bearing, not tidiness.  The first draft grouped
    every measured row and reported `ihnfeldt2008` as the corpus's largest
    "irreducible" bound at 67.2% -- but that dataset is not scored at all:
    six of its seven rows are GATED (the pack's oxidizer constants stop at
    pH 6.25 and the response sign flips across the Cu Pourbaix boundary), so
    they collapse to one prediction by *declared refusal*, and the scorer
    already excludes them.  Counting a gate as a bound would let the model's
    own silence argue for relaxing the completion bar -- docs/limits.md §36
    and §37, which also record that gates fire per ROW, not per block.
    """
    doc = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    rows = [r for r in (doc.get("conditions") or []) if _measured(r) is not None]
    if len(rows) < 3:
        return None
    axes = _varying_axes(rows)
    # Mirrors predictive_score.score_dataset: a gate only removes rows when
    # the gated axis is one this dataset actually varies.
    gate_matters = any(a in axes for a in ("oxidizer_wt_pct", "h2o2_vol_pct"))
    groups: Dict[float, List[float]] = defaultdict(list)
    all_declined: set = set()
    used = 0
    for row in rows:
        value, gate, declined = _predict_with_gate(doc, row)
        all_declined |= set(declined or ())
        if value is None:
            return None
        if gate and gate_matters:
            continue
        used += 1
        groups[_key(value)].append(float(_measured(row)))
    if used < 3:
        return None
    grouped = list(groups.values())
    total = 0.0
    for measured in grouped:
        c = _best_constant(measured)
        total += sum(abs(c - m) / m for m in measured)
    floor = 100.0 * total / used
    return DatasetFloor(path.stem, used, floor, grouped, axes,
                        sorted(all_declined & set(axes)))


def _tainted_names() -> set:
    """Datasets the calibration audit found the model was FITTED to.

    Held-out scoring removes exactly these (STATUS §32-§35): a dataset that
    donated a constant cannot grade the model that carries it.
    """
    from tools.calibration_flag_audit import collect, tainted_datasets

    return set(tainted_datasets(collect()))


def main(argv: List[str]) -> int:
    held_out = "--held-out" in argv
    drop = _tainted_names() if held_out else set()

    scores = {s.dataset: s for s in score_all()}
    results: List[Tuple[DatasetFloor, Optional[float]]] = []
    for path in dataset_paths():
        if path.stem in drop:
            continue
        f = dataset_floor(path)
        if f is None:
            continue
        s = scores.get(f.dataset)
        results.append((f, None if s is None else s.shape_mape))

    print("INPUT-DEGENERACY FLOOR PROBE"
          + ("  (HELD OUT)" if held_out else ""))
    print("=" * 74)
    print("floor = the lowest shape MAPE any model reading ONLY the inputs this")
    print("        harness supplies can reach on that dataset.  Each tied group")
    print("        is given its own free constant, so this is a bound, not a fit.")
    print()

    binding = [(f, s) for f, s in results if f.floor > 0.0]
    binding.sort(key=lambda t: -t[0].floor)
    if not binding:
        print("no dataset has two rows with identical predictions.")
    else:
        print(f"{'dataset':<50}{'n':>3}{'grp':>5}{'tied':>6}"
              f"{'floor':>8}{'shape':>8}  kind")
        for f, s in binding:
            shown = "  --  " if s is None else f"{s:6.1f}%"
            kind = ("FLAT (declared refusal, not a bound)" if f.is_flat
                    else "degenerate input")
            print(f"{f.dataset:<50}{f.n:>3}{f.n_groups:>5}{f.tied_rows:>6}"
                  f"{f.floor:>7.1f}%{shown:>8}  {kind}")
        print()
        print("degenerate datasets            : "
              f"{len(binding)} of {len(results)} scored")
        real = [t for t in binding if not t[0].is_flat]
        print("  of which a genuine BOUND      : "
              f"{len(real)}   (the rest predict a constant -- their floor is a")
        print("                                 description of a declared "
              "refusal, and it")
        print("                                 evaporates the moment the pack "
              "gains constants)")
        worst = binding[0]
        print("largest floor                  : "
              f"{worst[0].floor:.1f}%  ({worst[0].dataset}"
              + (", FLAT" if worst[0].is_flat else "") + ")")
        if real:
            print("largest genuine bound          : "
                  f"{real[0][0].floor:.1f}%  ({real[0][0].dataset})")

    floors = sorted(f.floor for f, _ in results)
    attainable = None
    if floors:
        n = len(floors)
        attainable = floors[n // 2]
        print("median floor across the corpus : "
              f"{attainable:.1f}%   (upper median, n={n})")
        print()
        print("=> the ATTAINABLE median -- what a model that scored every")
        print("   dataset at its own floor would report -- is that number.")
        print("   A corpus-wide floor argument therefore CANNOT be made from")
        print("   degeneracy: the median dataset has none.  The bound is PER")
        print("   DATASET and binds only where the experiment swept an axis")
        print("   the input schema does not carry.")

    # The completion bar is a COUNTING statistic (STATUS §26): it is met when
    # enough datasets individually cross it. So the question degeneracy can
    # actually answer is not "is the median floored" but "is any dataset that
    # MUST cross the bar floored above it" -- if one is, completion is
    # impossible for a reason no physics can fix.
    try:
        from tools.median_crossing_probe import crossing_report
    except Exception:
        return 0
    rep = crossing_report(15.0, held_out=held_out)
    shortlist = [t[0] for t in rep.get("nearest", [])]
    floor_by = {f.dataset: f.floor for f, _ in results}
    must = rep.get("datasets_that_must_cross")
    print()
    print(f"completion bar 15.0% needs {must} more dataset(s) to cross"
          + ("  (held out)" if held_out else ""))
    blocked = []
    for name in shortlist[: (must or 0) + 3]:
        fl = floor_by.get(name, 0.0)
        flag = "  <-- FLOORED ABOVE THE BAR" if fl > 15.0 else ""
        print(f"    {name:<58} floor {fl:5.1f}%{flag}")
        if fl > 15.0:
            blocked.append(name)
    if blocked:
        print("=> completion is structurally blocked by input degeneracy on: "
              + ", ".join(blocked))
    else:
        print("=> NO must-cross dataset is floored above the bar: degeneracy")
        print("   does not justify relaxing the completion bar.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
