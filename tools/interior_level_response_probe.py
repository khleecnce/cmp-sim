"""Does an axis's response survive being measured only at its ENDPOINTS?

Why this exists
---------------
``tools/inert_axis_scan.py`` (STATUS §17/§18) and ``tools/residual_census.py``
decide whether a swept input reaches the rate by running the dataset's first
row **twice** -- at the axis minimum and at the axis maximum the paper ran --
and comparing the two predicted rates. Every admissibility filter downstream
reads that map (`Census.responsive_axes`, the `silent`/`declared` split, the
"0 silent inert axes" verdict), so the two-point comparison is the single
reader behind a large family of closure arguments here.

§43 established that **the perturbation is part of the instrument**: a probe
that pushes a key with one large one-sided factor can land on a symmetry point
of the very term it is testing, where a peaked response returns exactly its
reference value and the measured response is precisely 0.00 %. That section
fixed the probe whose displacement it controlled
(`declared_key_response_census`). It could not fix this one, because here the
two evaluation points are **not chosen by the probe at all** -- they are the
first and last level *the publication ran*. The cancellation therefore arrives
through the data's own design, and no change to a perturbation constant can
avoid it.

The failure is exact, not statistical. This repository models several peaked
responses -- the Gaussian pH term
``exp(-((pH - ph_peak)/w)**2) / exp(-((pH_ref - ph_peak)/w)**2)``, the
oxidiser Langmuir saturation, the IEP-referenced zeta terms. For any peaked
`f`, two levels placed symmetrically about the optimum give
`f(lo) == f(hi)` for **every** width: the endpoint comparison returns 0.00 %
while the interior of the same sweep moves the rate as much as the term is
capable of moving it. And the more levels a paper ran -- i.e. the better the
experiment -- the more of them the two-point reading throws away.

That makes three distinguishable states with byte-identical output from the
incumbent reader:

``inert``
    No level of the axis moves the rate. The axis genuinely does not reach
    the output.

``endpoint-blind``
    The endpoints agree and an interior level does not. The axis IS read; the
    incumbent probe reports it as inert or near-inert. This is the class §43
    predicts and the one this probe exists to find.

``understated``
    The endpoints disagree, but by less than the full range of the sweep does.
    The axis is classified correctly and its response is quoted too small.

Method (measurement only -- nothing is fitted, no pack is modified)
-------------------------------------------------------------------
For every scored dataset and every axis it varies at **three or more** levels,
take the dataset's own first row, rebuild it at *every* level the paper ran,
and run the shipping solver on each. Then compare:

* ``endpoint`` = ``100 * |r(max_level) - r(min_level)| / max(...)`` -- exactly
  the quantity ``inert_axis_scan`` computes, recomputed here so the comparison
  cannot drift from the thing being audited;
* ``full`` = ``100 * (max(r) - min(r)) / max(r)`` over all levels.

Two-level axes are counted and excluded: for them the two readings are the
same measurement, so they can neither confirm nor refute anything.

Instrument control (§43)
------------------------
A probe that reports "nothing is hidden" is worthless unless it can be shown
to be capable of seeing something. This one must recover, among the axes it
examined, at least one whose endpoint reading is itself responsive -- if it
cannot, the whole output is stamped and every verdict in it is to be
distrusted rather than quoted.

Usage: ``python tools/interior_level_response_probe.py`` (inside ``.venv``).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import yaml

from cmp_sim.core.predictive_score import _measured, _recipe_for, score_all
from cmp_sim.core.validation import dataset_paths
from tools.residual_census import INERT_TOLERANCE, _axis_value, _with_axis

#: Minimum number of levels for the question to be askable at all. With two
#: levels the endpoint reading IS the full reading.
MIN_LEVELS = 3


@dataclass
class AxisReading:
    dataset: str
    axis: str
    levels: int
    #: level -> predicted rate (A/min); None where the run could not be made
    rates: List[Tuple[float, Optional[float]]] = field(default_factory=list)
    endpoint_pct: Optional[float] = None
    full_pct: Optional[float] = None

    @property
    def kind(self) -> str:
        if self.endpoint_pct is None or self.full_pct is None:
            return "unrunnable"
        if self.full_pct < INERT_TOLERANCE:
            return "inert"
        if self.endpoint_pct < INERT_TOLERANCE:
            return "endpoint-blind"
        if self.full_pct > self.endpoint_pct + 1e-9:
            return "understated"
        return "agrees"

    @property
    def understatement(self) -> Optional[float]:
        """How many times larger the full reading is than the endpoint one."""
        if not self.endpoint_pct or self.full_pct is None:
            return None
        return self.full_pct / self.endpoint_pct

    @property
    def extreme_level(self) -> Optional[float]:
        """The level at which the rate is furthest from the endpoint pair."""
        runs = [(lvl, r) for lvl, r in self.rates if r is not None]
        if len(runs) < 3:
            return None
        ends = (runs[0][1], runs[-1][1])
        mid = sum(ends) / 2.0
        return max(runs[1:-1], key=lambda lr: abs(lr[1] - mid))[0]


@dataclass
class ProbeResult:
    readings: List[AxisReading] = field(default_factory=list)
    two_level_axes: int = 0
    #: True when the probe recovered at least one endpoint-responsive axis.
    control_passed: bool = False

    def by_kind(self, kind: str) -> List[AxisReading]:
        return [r for r in self.readings if r.kind == kind]


def _rate(doc: Dict[str, Any], row: Dict[str, Any]) -> Optional[float]:
    from cmp_sim.api import run_recipe
    try:
        result = run_recipe(_recipe_for(doc, row))
    except Exception:
        return None
    value = result.get("removal_rate_A_per_min")
    return None if value in (None, 0) else float(value)


def _span_pct(values: List[float]) -> Optional[float]:
    if len(values) < 2:
        return None
    hi, lo = max(values), min(values)
    return None if hi <= 0 else 100.0 * (hi - lo) / hi


def probe(scores=None, only=None) -> ProbeResult:
    """Measure every axis; ``only`` restricts to a set of dataset stems.

    The filter exists for the tests, which must re-measure the mechanism at run
    time rather than pin a literal, and cannot afford the whole corpus.
    """
    scores = scores if scores is not None else score_all()
    by_name = {s.dataset: s for s in scores if s.shape_mape is not None}
    out = ProbeResult()
    for path in dataset_paths():
        score = by_name.get(Path(path).stem)
        if score is None:
            continue
        if only is not None and score.dataset not in only:
            continue
        doc = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
        rows = [r for r in (doc.get("conditions") or [])
                if _measured(r) is not None]
        if not rows:
            continue
        for axis in score.axes:
            levels = sorted({float(v)
                             for v in (_axis_value(r, axis) for r in rows)
                             if isinstance(v, (int, float))})
            if len(levels) < 2:
                continue
            if len(levels) < MIN_LEVELS:
                out.two_level_axes += 1
                continue
            reading = AxisReading(dataset=score.dataset, axis=axis,
                                  levels=len(levels))
            for lvl in levels:
                reading.rates.append(
                    (lvl, _rate(doc, _with_axis(rows[0], axis, lvl))))
            runs = [r for _, r in reading.rates if r is not None]
            ends = [r for lvl, r in reading.rates
                    if lvl in (levels[0], levels[-1]) and r is not None]
            if len(runs) >= MIN_LEVELS and len(ends) == 2:
                reading.endpoint_pct = _span_pct(ends)
                reading.full_pct = _span_pct(runs)
            out.readings.append(reading)
    out.control_passed = any(
        r.endpoint_pct is not None and r.endpoint_pct >= INERT_TOLERANCE
        for r in out.readings)
    return out


def report(result: Optional[ProbeResult] = None) -> str:
    result = result if result is not None else probe()
    lines = [
        "INTERIOR LEVEL RESPONSE — does the two-point endpoint reading that "
        "`inert_axis_scan` and",
        "`residual_census` publish agree with running EVERY level the paper "
        f"ran? (inert bar {INERT_TOLERANCE}%)",
        "-" * 108,
    ]
    if not result.control_passed:
        lines += ["", "*** INSTRUMENT CONTROL FAILED — this probe recovered no "
                      "endpoint-responsive axis at all.", "*** Every verdict "
                      "below is to be distrusted, not quoted: the likelier "
                      "reading is that the", "*** harness is not reaching the "
                      "solver. (§43)", ""]
    for kind, blurb in (
        ("endpoint-blind", "THE FINDING — the endpoints agree and an INTERIOR "
                           "level does not. The axis is read; the incumbent "
                           "two-point probe calls it inert."),
        ("understated", "classified correctly, response quoted too small"),
        ("inert", "no level moves the rate — the incumbent reading is right"),
        ("agrees", "endpoints already span the whole response"),
        ("unrunnable", "the solver declined at least one level"),
    ):
        group = result.by_kind(kind)
        lines += ["", f"{kind}: {len(group)}  — {blurb}"]
        for r in sorted(group, key=lambda a: -(a.understatement or 0.0)):
            end = "n/a" if r.endpoint_pct is None else f"{r.endpoint_pct:6.2f}%"
            full = "n/a" if r.full_pct is None else f"{r.full_pct:6.2f}%"
            ratio = ("" if r.understatement is None
                     else f"  x{r.understatement:,.1f}")
            peak = ("" if r.extreme_level is None
                    else f"  worst interior level {r.extreme_level:g}")
            lines.append(f"    {r.dataset:<28} {r.axis:<26} "
                         f"{r.levels} levels  endpoint {end}  full {full}"
                         f"{ratio}{peak}")
    lines += ["", f"two-level axes excluded (the two readings are the same "
                  f"measurement): {result.two_level_axes}",
              f"axes examined at >= {MIN_LEVELS} levels: "
              f"{len(result.readings)}"]
    return "\n".join(lines)


if __name__ == "__main__":  # pragma: no cover
    print(report())
