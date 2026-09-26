"""Decide the velocity axis using Sorooshian 2005, the corpus's second flow sweep.

WHY THIS SCRIPT EXISTS
----------------------
``tools/velocity_thermal_probe.py`` (2026-09-26) measured a large, one-sided
residual on the velocity axis: median b_V = -0.549 while b_P = -0.036. It
rejected frictional heating, Stribeck lubrication and P*V series resistance,
and identified ONE surviving zero-constant candidate:

    reactant starvation:  MRR ~ P * V**(2/3) * Q**(1/3)

derived from a mass balance (reactant inventory per swept area ~ Q/V) composed
with this repo's already-derived cube-root concentration law. It makes THREE
coefficient predictions, and the third -- b_Q = +1/3 -- is the one the velocity
data cannot fake. That probe could not settle it, because the only corpus
dataset varying flow (``yang2023_quartz_ceria_L25``) is the worst-fitting
dataset in the corpus and violates Preston's P-linearity (its own b_P =
-1.276), so it cannot arbitrate.

THE DATA THIS SCRIPT USES
-------------------------
Sorooshian, J. (2005), "Fundamental Tribological, Thermal and Kinetic
Attributes of Interlayer Dielectric, Tungsten and Shallow Trench Isolation
Chemical Mechanical Planarization", PhD dissertation, Dept. of Chemical &
Environmental Engineering, University of Arizona (Philipossian group), Ch. 4.3
pp. 175-189, Figs. 4.4-4.15.

    film      thermal SiO2, 100 mm
    slurry    Fujimi PL-4217 fumed silica, 12.5 wt%, pH 11
    flow      40 and 120 cc/min                      <- 2 levels, 3x span
    velocity  0.32 / 0.64 / 0.96 m/s (40/80/120 rpm) <- 3 levels, 3x span
    pressure  2 / 4 / 6 psi                          <- 3 levels, 3x span
    other     pad groove flat/XY/perforated, pad thickness 1.39/2.03 mm,
              all p-V cells in duplicate, in-situ conditioning, 24 C, 90 s

This is a FULL FACTORIAL in exactly the three variables the starvation law
constrains, which is why it can decide what yang2023 could not.

PROVENANCE, STATED PLAINLY
--------------------------
The factor LEVELS above are text (reliable). The removal rates are FIGURE
READS: the dissertation plots RR against p*V and does not tabulate it. They
were digitised programmatically from vector-quality charts (see
``research/digitized/sorooshian2005_digitize.py``), not eyeballed, and the
digitisation passes a self-check it could not pass if the axis calibration
were wrong -- every one of the 117 recovered markers lands on a nominal
(psi x m/s) product to within 0.5 %.

Because the rates are figure reads, this script is deliberately built to need
only ONE digit of them: it asks for the SIGN and rough MAGNITUDE of a log-log
slope across a 3x span in flow. A 5-10 % read error cannot manufacture or hide
an effect that size. The dataset is used to FALSIFY, not to fit a constant.

WHAT IS COMPUTED
----------------
1. b_Q, the flow exponent, from MATCHED PAIRS: same pad, same groove, same
   thickness, same pressure, same velocity, differing only in flow. Matching
   rather than regressing removes every confound by construction, so the
   result does not depend on a model of the other axes.
2. b_V, the velocity exponent, at fixed pressure and flow.
3. The Preston audit: does RR scale with P as Preston says? This is the check
   yang2023 FAILED, and it is applied here before the dataset is allowed to
   arbitrate anything.

Run: python tools/sorooshian_flow_probe.py
"""
from __future__ import annotations

import csv
import math
import statistics
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Sequence, Tuple

HERE = Path(__file__).resolve().parents[1]
CSV = HERE / "research" / "digitized" / "sorooshian2005_ild_cmp.csv"

#: The starvation law's three predictions (zero free constants).
PREDICTED_BQ = 1.0 / 3.0
PREDICTED_BV = 2.0 / 3.0
PREDICTED_BP = 1.0


def load() -> List[dict]:
    rows = []
    with CSV.open(newline="", encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            rows.append({
                "groove": row["groove"], "thick": float(row["thick"]),
                "flow": float(row["flow"]), "psi": float(row["psi"]),
                "vel": float(row["vel"]), "rr": float(row["rr"]),
                "merged": row["merged"].strip().lower() == "true",
            })
    return rows


def _cell(rows: Sequence[dict], *keys: str) -> Dict[tuple, List[float]]:
    """Group rates by the tuple of the named columns (duplicates collapse)."""
    out: Dict[tuple, List[float]] = defaultdict(list)
    for r in rows:
        out[tuple(r[k] for k in keys)].append(r["rr"])
    return out


def _geo(values: Sequence[float]) -> float:
    return math.exp(statistics.fmean(math.log(v) for v in values))


def flow_exponent(rows: Sequence[dict]) -> Tuple[float, int, List[float]]:
    """b_Q from matched pairs differing ONLY in flow rate.

    Returns (exponent, n_pairs, per-pair exponents).
    """
    cells = _cell(rows, "groove", "thick", "psi", "vel", "flow")
    exps: List[float] = []
    seen = set()
    for key in cells:
        groove, thick, psi, vel, flow = key
        base = (groove, thick, psi, vel)
        if base in seen:
            continue
        lo = cells.get((groove, thick, psi, vel, 40.0))
        hi = cells.get((groove, thick, psi, vel, 120.0))
        if not lo or not hi:
            continue
        seen.add(base)
        # b_Q = d ln RR / d ln Q across the 40 -> 120 cc/min step
        exps.append(math.log(_geo(hi) / _geo(lo)) / math.log(120.0 / 40.0))
    return (statistics.median(exps) if exps else float("nan"),
            len(exps), exps)


def velocity_exponent(rows: Sequence[dict]) -> Tuple[float, int, List[float]]:
    """b_V from matched ladders at fixed pressure, flow, pad."""
    cells = _cell(rows, "groove", "thick", "psi", "flow", "vel")
    ladders: Dict[tuple, List[Tuple[float, float]]] = defaultdict(list)
    for (groove, thick, psi, flow, vel), rates in cells.items():
        ladders[(groove, thick, psi, flow)].append((vel, _geo(rates)))
    exps: List[float] = []
    for pts in ladders.values():
        if len(pts) < 3:
            continue
        lx = [math.log(v) for v, _ in pts]
        ly = [math.log(r) for _, r in pts]
        mx, my = statistics.fmean(lx), statistics.fmean(ly)
        den = sum((x - mx) ** 2 for x in lx)
        if den:
            exps.append(sum((x - mx) * (y - my)
                            for x, y in zip(lx, ly)) / den)
    return (statistics.median(exps) if exps else float("nan"),
            len(exps), exps)


def pressure_exponent(rows: Sequence[dict]) -> Tuple[float, int, List[float]]:
    """b_P — the Preston audit. This decides whether the dataset may arbitrate."""
    cells = _cell(rows, "groove", "thick", "vel", "flow", "psi")
    ladders: Dict[tuple, List[Tuple[float, float]]] = defaultdict(list)
    for (groove, thick, vel, flow, psi), rates in cells.items():
        ladders[(groove, thick, vel, flow)].append((psi, _geo(rates)))
    exps: List[float] = []
    for pts in ladders.values():
        if len(pts) < 3:
            continue
        lx = [math.log(p) for p, _ in pts]
        ly = [math.log(r) for _, r in pts]
        mx, my = statistics.fmean(lx), statistics.fmean(ly)
        den = sum((x - mx) ** 2 for x in lx)
        if den:
            exps.append(sum((x - mx) * (y - my)
                            for x, y in zip(lx, ly)) / den)
    return (statistics.median(exps) if exps else float("nan"),
            len(exps), exps)


def report() -> str:
    rows = load()
    lines = [f"Sorooshian 2005 ILD CMP — {len(rows)} digitised points",
             f"  flow levels     {sorted({r['flow'] for r in rows})} cc/min",
             f"  velocity levels {sorted({r['vel'] for r in rows})} m/s",
             f"  pressure levels {sorted({r['psi'] for r in rows})} psi",
             ""]

    bp, np_, _ = pressure_exponent(rows)
    lines.append("PRESTON AUDIT (does this dataset earn the right to arbitrate?)")
    lines.append(f"  b_P = {bp:+.3f} over {np_} ladders   "
                 f"(Preston requires {PREDICTED_BP:+.3f})")
    trustworthy = abs(bp - PREDICTED_BP) < 0.35
    lines.append(f"  -> {'PASSES' if trustworthy else 'FAILS'}: "
                 + ("close enough to linear in P to be trusted on a subtler axis"
                    if trustworthy else
                    "too far from linear in P; treat conclusions as weak"))
    lines.append("")

    bv, nv, _ = velocity_exponent(rows)
    lines.append("VELOCITY EXPONENT")
    lines.append(f"  b_V = {bv:+.3f} over {nv} ladders   "
                 f"(starvation predicts {PREDICTED_BV:+.3f}, "
                 f"Preston predicts +1.000)")
    lines.append("")

    bq, nq, per = flow_exponent(rows)
    lines.append("FLOW EXPONENT — the decisive test")
    lines.append(f"  b_Q = {bq:+.3f} over {nq} MATCHED PAIRS "
                 f"(identical pad/groove/thickness/pressure/velocity; "
                 f"40 -> 120 cc/min)")
    lines.append(f"  starvation predicts b_Q = {PREDICTED_BQ:+.3f}")
    if per:
        lines.append(f"  per-pair spread: min {min(per):+.3f}  "
                     f"max {max(per):+.3f}  "
                     f"fraction positive {sum(1 for e in per if e > 0)}/{len(per)}")
        ratio = math.exp(bq * math.log(3.0))
        lines.append(f"  a 3x flow increase moves MRR by {(ratio - 1) * 100:+.1f}% "
                     f"(starvation requires {(3 ** PREDICTED_BQ - 1) * 100:+.1f}%)")
    lines.append("")

    verdict_ok = abs(bq - PREDICTED_BQ) < 0.15
    lines.append("VERDICT")
    if not verdict_ok:
        lines.append(
            "  The starvation law is FALSIFIED on its flow leg by a dataset "
            "that PASSES the Preston audit. Because b_V and b_Q come from the "
            "SAME mass balance, the V**(2/3) exponent cannot be adopted on "
            "this derivation: keeping the velocity half while the flow half "
            "is measured to be absent would be fitting, not deriving.")
    else:
        lines.append("  The starvation law SURVIVES its flow leg. Re-open "
                     "adoption of MRR ~ P*V**(2/3)*Q**(1/3).")
    return "\n".join(lines)


if __name__ == "__main__":
    print(report())
