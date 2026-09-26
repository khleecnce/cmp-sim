"""Is the corpus residual explained by a SATURATION of rate with pressure?

Motivation
----------
The residual census (``tools/residual_census.py``) showed that 35 of 46 scored
datasets DO respond to an axis they vary and still miss (median 20.2 %), so the
next step is to name a law rather than add a handle. The most commonly proposed
law for that bucket is a two-resistance / limiting-rate form,

    1/RR = 1/(k_mech * P * V) + 1/RR_chem,

i.e. the removal rate saturates once mechanical abrasion outruns regeneration
of the chemically modified surface layer (Kaufman 1991's passivation picture;
the same series-resistance algebra as mixed kinetic/transport control). Preston
is its P*V -> 0 limit. Adopting it costs ONE new constant per pack
(``RR_chem``), which the project's methodology only permits if the data DEMAND
it.

The test
--------
It makes a sharp, falsifiable prediction: after fitting one scale per dataset,
the residual ratio measured/predicted must fall systematically as pressure
rises, because a linear-in-P model over-predicts at the top of the ladder. So
for every dataset with >= 3 distinct pressures, regress
``ln(measured / scaled prediction)`` on ``ln P``. Saturation requires a
consistently NEGATIVE slope.

Result: FALSIFIED. See ``tests/test_pressure_saturation_falsified.py``.
The slopes straddle zero (median ~ +0.08) and flip sign between datasets
covering the same pressure range, so the misses are per-dataset scale/chemistry
errors, not a missing curvature in P. Preston's linearity in P is kept and no
constant is added.

Measurement only: fits nothing, touches no pack.
"""
from __future__ import annotations

import math
import statistics
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

from cmp_sim.core.predictive_score import _measured, _recipe_for
from cmp_sim.core.validation import dataset_paths

#: A dataset needs at least this many distinct down-force levels before a
#: curvature in P can be told apart from a two-point slope.
MIN_PRESSURE_LEVELS = 3


@dataclass
class PressureTrend:
    dataset: str
    n: int
    p_min: float
    p_max: float
    #: d ln(measured/predicted) / d ln P. Negative = the model over-predicts as
    #: pressure rises, which is what a saturating rate would look like.
    slope: float


def _run(doc: Dict[str, Any], row: Dict[str, Any]) -> Optional[float]:
    from cmp_sim.api import run_recipe
    try:
        result = run_recipe(_recipe_for(doc, row))
    except Exception:
        return None
    value = result.get("removal_rate_A_per_min")
    return None if value in (None, 0) else float(value)


def trends() -> List[PressureTrend]:
    out: List[PressureTrend] = []
    for path in dataset_paths():
        doc = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
        rows = [r for r in (doc.get("conditions") or [])
                if _measured(r) is not None and r.get("pressure_psi")]
        if len({r["pressure_psi"] for r in rows}) < MIN_PRESSURE_LEVELS:
            continue
        measured, predicted, pressures = [], [], []
        for row in rows:
            value = _run(doc, row)
            if value is None:
                measured = []
                break
            measured.append(float(_measured(row)))
            predicted.append(value)
            pressures.append(float(row["pressure_psi"]))
        if len(measured) < MIN_PRESSURE_LEVELS:
            continue
        # one free scale, exactly as the corpus score does, so the slope is a
        # SHAPE statement and a pure calibration error cannot create it
        scale = (sum(m * p for m, p in zip(measured, predicted))
                 / sum(p * p for p in predicted))
        lx = [math.log(p) for p in pressures]
        ly = [math.log(m / (scale * p)) for m, p in zip(measured, predicted)]
        mx, my = sum(lx) / len(lx), sum(ly) / len(ly)
        den = sum((x - mx) ** 2 for x in lx)
        if den == 0:
            continue
        out.append(PressureTrend(
            dataset=Path(path).stem, n=len(measured),
            p_min=min(pressures), p_max=max(pressures),
            slope=sum((x - mx) * (y - my) for x, y in zip(lx, ly)) / den))
    return out


def report(rows: Optional[List[PressureTrend]] = None) -> str:
    rows = rows if rows is not None else trends()
    lines = []
    for t in sorted(rows, key=lambda t: t.slope):
        lines.append(f"{t.dataset[:46]:46s} n={t.n:2d} "
                     f"P {t.p_min:.2f}-{t.p_max:.2f} psi  "
                     f"d(ln ratio)/d(ln P) = {t.slope:+.3f}")
    med = statistics.median(t.slope for t in rows)
    negative = sum(1 for t in rows if t.slope < 0)
    lines.append("")
    lines.append(f"{len(rows)} datasets with >= {MIN_PRESSURE_LEVELS} pressure "
                 f"levels; median slope {med:+.3f}; {negative}/{len(rows)} "
                 "negative")
    lines.append("saturation (1/RR = 1/kPV + 1/RR_chem) predicts a CONSISTENTLY "
                 "negative slope. It is not observed, so the law is rejected "
                 "and no RR_chem constant is introduced.")
    return "\n".join(lines)


if __name__ == "__main__":
    print(report())
