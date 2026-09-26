"""Is the oxidiser order +1/2, as a radical chain would require?

WHY THIS SCRIPT EXISTS
----------------------
``tools/axis_error_census.py`` (12th run) showed the improvable error is
DISTRIBUTED: on four of six axes a single shared exponent buys almost nothing
because the per-dataset exponents disagree in sign. Exactly one axis survived
the tightening from oracle to law -- ``oxidizer_wt_pct``, shared exponent
**+0.48**, mean shape 32.5 % -> 23.0 %, every per-dataset exponent positive.

+0.48 is suspiciously close to a number that can be DERIVED rather than fitted.
If the oxidant feeds a steady-state population of chain carriers (OH-, HO2-
radicals from Fenton-type decomposition of H2O2 on Cu or on the W/Fe(II)
couple), and those carriers are destroyed by radical-radical recombination,
then at steady state

    initiation   = k_i * [ox]                  (one radical pair per oxidant)
    termination  = k_t * [R]**2                (bimolecular)
    => [R] = sqrt(k_i/k_t) * [ox]**(1/2)

and a surface reaction first order in the carrier inherits the HALF order:

    MRR_chem  ~  [ox]**(1/2).

That is a prediction with ZERO free constants, so it is falsifiable. The
alternative with the same initiation but FIRST-order termination (radicals
quenched at the surface or by a scavenger) gives [R] ~ [ox], i.e. order +1. The
two mechanisms are therefore distinguished by the ORDER ITSELF, and -- more
sharply -- by how the order CHANGES with concentration: bimolecular termination
takes over as radical density rises, so a system crossing from surface
quenching to recombination shows the order FALLING from ~1 towards ~1/2 as
[ox] increases.

STATUS.md pre-registered three tests before this script was written:

  1. ORDER TEST. Fit the order per dataset on the measured data. It must be
     indistinguishable from +1/2 in EACH dataset, not merely on average.
  2. TERMINATION TEST. Inside one wide sweep, compare the order at low vs high
     [ox]. Bimolecular termination predicts the order falls.
  3. SIGN GUARD. Du 2004 measures Cu polishing FASTER with no oxidiser at all,
     so any half-order term must sit on top of the existing additive mechanical
     floor and must not become a purely multiplicative factor (which would send
     the rate to zero at [ox] = 0).

The order is measured from the MEASURED RATES, not from the residual against
the current model. A residual exponent is contaminated by whatever oxidiser
term the pack already applies; the mechanism makes a claim about the rate
itself. Datasets flagged ``used_for_calibration`` are reported but EXCLUDED
from the verdict, because the pack's existing oxidiser constant was fitted on
them.

This module MEASURES ONLY. It fits nothing into any pack.
Usage: ``python tools/oxidizer_order_probe.py`` (inside ``.venv``).
"""
from __future__ import annotations

import math
import statistics
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

import yaml

from cmp_sim.core.predictive_score import _measured
from cmp_sim.core.validation import dataset_paths

#: The derived half order. Not tunable: it follows from bimolecular termination.
HALF_ORDER = 0.5
#: First-order alternative (surface quenching / scavenger-limited chain).
FIRST_ORDER = 1.0

#: Axis keys that carry an oxidant loading.
OX_KEYS = ("oxidizer_wt_pct", "h2o2_vol_pct")

#: Inputs that must be EQUAL across rows for the rows to form a clean oxidiser
#: block. Anything else varying makes the fitted order a mixture of axes.
HOLD_KEYS = ("pressure_psi", "rpm_platen", "rpm_wafer")


@dataclass
class Block:
    """One clean oxidiser sweep: same everything except the oxidant."""
    dataset: str
    film: str
    calibrated_on: bool
    x: List[float] = field(default_factory=list)
    y: List[float] = field(default_factory=list)
    order: Optional[float] = None
    stderr: Optional[float] = None

    @property
    def n(self) -> int:
        return len(self.x)

    def consistent_with(self, target: float) -> Optional[bool]:
        """Is the measured order within 2 standard errors of `target`?"""
        if self.order is None or self.stderr is None:
            return None
        return abs(self.order - target) <= 2.0 * self.stderr


def _ox_value(row: Dict[str, Any]) -> Optional[float]:
    over = row.get("overrides") or {}
    for key in OX_KEYS:
        value = over.get(key)
        if isinstance(value, (int, float)):
            return float(value)
    return None


def _hold_signature(row: Dict[str, Any]) -> Tuple:
    """Everything that must be fixed within a block.

    Includes every override EXCEPT the oxidant itself, so a row that also
    changes pH or abrasive loading lands in a different block instead of
    silently widening the fit.
    """
    over = row.get("overrides") or {}
    others = tuple(sorted((k, v) for k, v in over.items() if k not in OX_KEYS))
    return tuple(row.get(k) for k in HOLD_KEYS) + others


def _loglog_slope(x: Sequence[float],
                  y: Sequence[float]) -> Tuple[float, Optional[float]]:
    """Slope of ln y vs ln x, with its standard error.

    The standard error is what makes test 1 an honest comparison: an order of
    0.7 measured on three noisy points does NOT refute +1/2, and saying so
    requires the scatter, not the point estimate.
    """
    lx = [math.log(v) for v in x]
    ly = [math.log(v) for v in y]
    n = len(lx)
    mx, my = sum(lx) / n, sum(ly) / n
    sxx = sum((v - mx) ** 2 for v in lx)
    if sxx <= 0:
        return 0.0, None
    slope = sum((v - mx) * (w - my) for v, w in zip(lx, ly)) / sxx
    if n <= 2:
        return slope, None            # zero residual degrees of freedom
    intercept = my - slope * mx
    resid = [w - (intercept + slope * v) for v, w in zip(lx, ly)]
    s2 = sum(r * r for r in resid) / (n - 2)
    return slope, math.sqrt(s2 / sxx)


def blocks(min_levels: int = 3) -> List[Block]:
    out: List[Block] = []
    for path in dataset_paths():
        doc = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
        rows = [r for r in (doc.get("conditions") or []) if _measured(r) is not None]
        groups: Dict[Tuple, List[Dict[str, Any]]] = {}
        for row in rows:
            if _ox_value(row) is None:
                continue
            groups.setdefault(_hold_signature(row), []).append(row)
        for _sig, group in groups.items():
            pairs = [(_ox_value(r), float(_measured(r))) for r in group]
            # Zero oxidant is a MEASURED condition but has no logarithm. It is
            # the subject of test 3, not of the order fit.
            pairs = [(x, y) for x, y in pairs if x and x > 0 and y > 0]
            if len({x for x, _ in pairs}) < min_levels:
                continue
            pairs.sort()
            blk = Block(dataset=Path(path).stem,
                        film=str(doc.get("film") or "?"),
                        calibrated_on=bool(doc.get("used_for_calibration")),
                        x=[x for x, _ in pairs], y=[y for _, y in pairs])
            blk.order, blk.stderr = _loglog_slope(blk.x, blk.y)
            out.append(blk)
    return out


def split_order(blk: Block) -> Optional[Tuple[float, float]]:
    """(order over the lower half of the sweep, order over the upper half).

    Test 2. Bimolecular termination predicts the SECOND number is smaller: as
    radical density rises, recombination outcompetes first-order loss and the
    apparent order falls towards 1/2. Needs >= 3 levels in each half.
    """
    levels = sorted(set(blk.x))
    if len(levels) < 6:
        return None
    mid = levels[len(levels) // 2]
    lo = [(x, y) for x, y in zip(blk.x, blk.y) if x <= mid]
    hi = [(x, y) for x, y in zip(blk.x, blk.y) if x >= mid]
    if len({x for x, _ in lo}) < 3 or len({x for x, _ in hi}) < 3:
        return None
    return (_loglog_slope([x for x, _ in lo], [y for _, y in lo])[0],
            _loglog_slope([x for x, _ in hi], [y for _, y in hi])[0])


def zero_oxidant_rows() -> List[Tuple[str, float, float]]:
    """(dataset, rate at [ox]=0, max rate in that block) — test 3's evidence.

    A purely multiplicative half-order term predicts ZERO rate at zero
    oxidant. Every row here is a counter-example, and the existing additive
    mechanical floor is what keeps them predictable.
    """
    out = []
    for path in dataset_paths():
        doc = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
        rows = [r for r in (doc.get("conditions") or []) if _measured(r) is not None]
        zeros = [float(_measured(r)) for r in rows if _ox_value(r) == 0.0]
        others = [float(_measured(r)) for r in rows
                  if (_ox_value(r) or 0.0) > 0.0]
        if zeros and others:
            out.append((Path(path).stem, max(zeros), max(others)))
    return out


def verdict(bs: Optional[List[Block]] = None) -> Dict[str, Any]:
    bs = bs if bs is not None else blocks()
    judged = [b for b in bs if not b.calibrated_on and b.stderr is not None]
    half = [b for b in judged if b.consistent_with(HALF_ORDER)]
    first = [b for b in judged if b.consistent_with(FIRST_ORDER)]
    neither = [b for b in judged
               if not b.consistent_with(HALF_ORDER)
               and not b.consistent_with(FIRST_ORDER)]
    return {
        "blocks": len(bs),
        "judged": len(judged),
        "consistent_with_half": [b.dataset for b in half],
        "consistent_with_first": [b.dataset for b in first],
        "consistent_with_neither": [b.dataset for b in neither],
        "orders": [(b.dataset, b.order, b.stderr) for b in judged],
        # The pre-registered pass condition for test 1: EVERY judged block.
        "half_order_survives": bool(judged) and len(half) == len(judged),
    }


def predicted_order(blk: Block) -> Optional[float]:
    """The order the CURRENT model predicts over the same block.

    This closes the gap between this probe and ``axis_error_census``: the
    census fitted its exponent to measured/PREDICTED, so a uniformly positive
    residual exponent is equally consistent with (a) a missing +1/2 mechanism
    and (b) a pack whose oxidiser term is too STEEP and too NEGATIVE. Measuring
    the predicted order separates them, and the distinction decides whether the
    +0.48 is physics or a correction to an existing fitted curve.
    """
    from cmp_sim.api import run_recipe
    from cmp_sim.core.predictive_score import _recipe_for
    path = next((p for p in dataset_paths() if Path(p).stem == blk.dataset), None)
    if path is None:
        return None
    doc = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
    rows = [r for r in (doc.get("conditions") or []) if _measured(r) is not None]
    wanted = set(blk.x)
    picked: Dict[float, Dict[str, Any]] = {}
    for row in rows:
        value = _ox_value(row)
        if value in wanted and value not in picked:
            picked[float(value)] = row
    if len(picked) < 3:
        return None
    xs, ys = [], []
    for value, row in sorted(picked.items()):
        try:
            rate = run_recipe(_recipe_for(doc, row)).get("removal_rate_A_per_min")
        except Exception:
            return None
        if not rate:
            return None
        xs.append(value)
        ys.append(float(rate))
    return _loglog_slope(xs, ys)[0]


def census_gain_audit() -> List[Dict[str, Any]]:
    """Audit WHICH datasets carry the census's oxidiser gain, and whether they can.

    This is the step that decides the axis. ``axis_error_census`` reported a
    shared exponent of +0.48 worth 9.5 pp on ``oxidizer_wt_pct``, but a gain is
    only evidence if the datasets producing it are (a) not ones the pack's
    oxidiser constant was fitted on -- otherwise it is self-scoring -- and
    (b) not sweeping the oxidant in lockstep with another input, because a free
    exponent on the oxidant would then be silently paid for by the OTHER axis.
    Condition (b) bites hardest when the co-varying axis is INERT in the model,
    since the residual then contains that axis' whole effect with nowhere else
    to go.

    Returns one record per dataset that contributed a positive oxidiser gain.
    """
    from tools.axis_error_census import price, _axis_value, INERT_TOLERANCE
    from tools.residual_census import census as bucket_census

    buckets = {c.dataset: c for c in bucket_census()}
    out: List[Dict[str, Any]] = []
    for dp in price():
        for p in dp.prices:
            if p.axis not in OX_KEYS or p.gain_pp is None or p.gain_pp <= 0:
                continue
            path = next((q for q in dataset_paths() if Path(q).stem == dp.dataset), None)
            if path is None:
                continue
            doc = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
            rows = [r for r in (doc.get("conditions") or [])
                    if _measured(r) is not None]
            ox = [_ox_value(r) for r in rows]
            if any(v is None for v in ox):
                continue
            ox = [float(v) for v in ox]  # type: ignore[arg-type]
            confounds = []
            rec = buckets.get(dp.dataset)
            other_axes = [a for a in (rec.response if rec else {}) if a not in OX_KEYS]
            for axis in other_axes:
                values = [_axis_value(r, axis) for r in rows]
                if any(not isinstance(v, (int, float)) for v in values):
                    continue
                if len(set(values)) < 2:
                    continue
                n = len(values)
                mx = sum(ox) / n
                my = sum(values) / n
                num = sum((a - mx) * (b - my) for a, b in zip(ox, values))
                den = math.sqrt(sum((a - mx) ** 2 for a in ox)
                                * sum((b - my) ** 2 for b in values))
                if den <= 0:
                    continue
                r = num / den
                response = (rec.response.get(axis) if rec else None)
                inert = response is not None and response < INERT_TOLERANCE
                if abs(r) >= 0.4:
                    confounds.append({"axis": axis, "r": r, "inert_in_model": inert})
            out.append({
                "dataset": dp.dataset, "n": dp.n,
                "exponent": p.exponent, "gain_pp": p.gain_pp,
                "used_for_calibration": bool(doc.get("used_for_calibration")),
                "confounds": confounds,
                "admissible": (not doc.get("used_for_calibration")
                               and not any(c["inert_in_model"] for c in confounds)),
            })
    return out


def report() -> str:
    bs = blocks()
    lines = [f"{'dataset':44s} {'film':6s} {'n':>2s} {'[ox] range':>18s} "
             f"{'order':>7s} {'+/-':>6s}  verdict",
             "-" * 120]
    for b in sorted(bs, key=lambda b: (b.calibrated_on, b.dataset)):
        se = "  n/a" if b.stderr is None else f"{b.stderr:6.2f}"
        tags = []
        if b.calibrated_on:
            tags.append("EXCLUDED: pack fitted on it")
        else:
            if b.consistent_with(HALF_ORDER):
                tags.append("~ +1/2")
            if b.consistent_with(FIRST_ORDER):
                tags.append("~ +1")
            if not tags:
                tags.append("NEITHER")
        rng = f"{min(b.x):g}-{max(b.x):g}"
        lines.append(f"{b.dataset[:44]:44s} {b.film[:6]:6s} {b.n:2d} "
                     f"{rng:>18s} {b.order:7.2f} {se}  {', '.join(tags)}")

    v = verdict(bs)
    lines += ["", f"{v['blocks']} clean oxidiser blocks, {v['judged']} judged "
                  f"(calibration-contaminated ones excluded)",
              "", "TEST 1 (order == +1/2 in EVERY judged block, pre-registered):"]
    lines.append(f"  consistent with +1/2 : {len(v['consistent_with_half'])} "
                 f"{v['consistent_with_half']}")
    lines.append(f"  consistent with +1   : {len(v['consistent_with_first'])} "
                 f"{v['consistent_with_first']}")
    lines.append(f"  consistent with neither: {len(v['consistent_with_neither'])} "
                 f"{v['consistent_with_neither']}")
    lines.append(f"  => half order survives test 1: {v['half_order_survives']}")

    lines += ["", "TEST 2 (order FALLS as [ox] rises, if termination is bimolecular):"]
    any_split = False
    for b in bs:
        sp = split_order(b)
        if sp is None:
            continue
        any_split = True
        lo, hi = sp
        lines.append(f"  {b.dataset[:44]:44s} low {lo:+.2f} -> high {hi:+.2f}  "
                     f"{'FALLS (consistent)' if hi < lo else 'RISES (contradicts)'}")
    if not any_split:
        lines.append("  no dataset has 3+ oxidant levels in BOTH halves of its "
                     "own sweep: the termination order is UNTESTABLE on this "
                     "corpus, so it cannot be claimed either way")

    lines += ["", "PREDICTED vs MEASURED order (what the census's +0.48 really was):"]
    for b in bs:
        if b.calibrated_on:
            continue
        pred = predicted_order(b)
        if pred is None:
            continue
        lines.append(f"  {b.dataset[:44]:44s} model {pred:+.2f}  measured "
                     f"{b.order:+.2f}  residual would need {b.order - pred:+.2f}")

    lines += ["", "GAIN AUDIT (is the census's +9.5 pp admissible evidence at all?):"]
    audit = census_gain_audit()
    for rec in sorted(audit, key=lambda r: -r["gain_pp"]):
        why = []
        if rec["used_for_calibration"]:
            why.append("pack's oxidiser constant was FITTED on it")
        for c in rec["confounds"]:
            why.append(f"{c['axis']} co-varies r={c['r']:+.2f}"
                       + (" and is INERT in the model" if c["inert_in_model"] else ""))
        verdict_txt = "ADMISSIBLE" if rec["admissible"] else "INADMISSIBLE: " + "; ".join(why)
        lines.append(f"  {rec['dataset'][:44]:44s} n={rec['n']:3d} b="
                     f"{rec['exponent']:+.2f} gain {rec['gain_pp']:+5.1f} pp  {verdict_txt}")
    admissible_gain = sum(r["gain_pp"] for r in audit if r["admissible"])
    lines.append(f"  => admissible oxidiser gain across the corpus: "
                 f"{admissible_gain:.1f} pp of dataset-level shape")

    lines += ["", "TEST 3 (zero-oxidant rows forbid a purely multiplicative term):"]
    zeros = zero_oxidant_rows()
    if not zeros:
        lines.append("  no zero-oxidant rows in the corpus")
    for name, at_zero, best in zeros:
        lines.append(f"  {name[:44]:44s} rate at [ox]=0 is {at_zero:.1f} "
                     f"({100.0 * at_zero / best:.0f}% of the block's maximum) "
                     "-> a multiplicative term would predict 0")
    return "\n".join(lines)


if __name__ == "__main__":
    print(report())
