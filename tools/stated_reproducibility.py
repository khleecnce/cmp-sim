"""Turn each source's STATED reproducibility into a floor comparable to our error.

`cmp_sim/data/validation/reproducibility.yaml` holds what every publication says
about its own run-to-run scatter, verbatim. This module converts those statements
into the one form the accuracy question needs — a percentage of the measured rate
— and refuses to convert the ones that cannot honestly be converted.

Why each `kind` is handled differently
--------------------------------------
* ``replicate_rsd``  already a percentage. Used as printed.
* ``absolute_uncertainty``  a constant +/- on a rate that varies across the
  dataset, so it is a DIFFERENT percentage on every row. Converted per row and
  averaged with the same weighting our MAPE uses, so the floor and the error are
  the same kind of average. Collapsing it to one percentage against the mean rate
  would understate the floor on the slow rows, which is exactly where it bites.
* ``derived_pure_error``  recovered from printed ANOVA summary statistics.
  See `_miranda_pure_error` for the algebra; it is checked arithmetically in
  tests/test_stated_reproducibility.py.
* ``spatial_only``  an SD across points on ONE wafer is within-wafer
  non-uniformity. A model predicting the wafer-average rate is NOT bounded by it,
  so it yields NO floor. Recorded to stop it being mistaken for one.
* ``replicated_scatter_withheld``  the floor exists and is non-zero, and the
  source does not print it. No floor. This is the honest answer, and it is
  deliberately not the same answer as ``none_stated``.
* ``transcription_floor``  a figure-reading error, not a measurement one. Yields
  a floor on what the TRANSCRIPTION can support, reported separately so the two
  are never pooled.
* ``none_stated``  nothing. Searched and silent.

Nothing here feeds a prediction or a score. Reporting only.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import yaml

from cmp_sim.core.predictive_score import score_all, score_dataset
from cmp_sim.core.validation import dataset_paths

REPRO_PATH = (Path(__file__).resolve().parents[1] / "cmp_sim" / "data"
              / "validation" / "reproducibility.yaml")

#: kinds that yield a measurement floor in percent
MEASUREMENT_KINDS = {"replicate_rsd", "absolute_uncertainty",
                     "derived_pure_error"}
#: kinds that exist but cannot be quantified from the source
UNQUANTIFIED_KINDS = {"replicated_scatter_withheld", "spatial_only",
                      "none_stated"}


def load_statements() -> Dict[str, Dict[str, Any]]:
    doc = yaml.safe_load(REPRO_PATH.read_text(encoding="utf-8")) or {}
    return doc.get("datasets") or {}


def _rates(stem: str) -> List[float]:
    path = next((p for p in dataset_paths() if p.stem == stem), None)
    if path is None:
        return []
    doc = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    out = []
    for row in doc.get("conditions") or []:
        rate = row.get("measured_mrr_nm_per_min") or row.get("mrr_nm_per_min")
        if rate:
            out.append(float(rate))
    return out


def _absolute_to_percent(stem: str, sigma_nm_per_min: float) -> Optional[float]:
    """A constant +/- becomes a per-row percentage; average it as MAPE does."""
    rates = _rates(stem)
    if not rates:
        return None
    return 100.0 * sum(sigma_nm_per_min / r for r in rates) / len(rates)


def _miranda_pure_error(stem: str, entry: Dict[str, Any]
                        ) -> Optional[Tuple[float, float]]:
    """Recover replicate scatter from a printed adjusted R^2. Returns (lo, hi) %.

    The source prints: a 2^2 full factorial with r=3 replicates (n=12 runs), the
    four CELL MEANS, and adjusted R^2 = 0.69. The replicate rates themselves are
    withheld. That is still enough, because a saturated 2^2 model (p=4) passes
    exactly through the four cell means, so the between-cell sum of squares is
    computable from the printed means alone:

        SS_between = r * sum_i (ybar_i - ybar)^2

    and with SS_total = SS_between + SS_error,

        1 - R2_adj = (SS_error/(n-p)) / (SS_total/(n-1))
        =>  SS_error = (n-p) * a * SS_between / ((n-1) - (n-p) * a),   a = 1-R2_adj

    The pure-error standard deviation is sqrt(SS_error/(n-p)), reported relative
    to the grand mean so it is comparable to a MAPE.

    Two assumptions are carried as a BAND rather than hidden:
      * p = 4 (saturated) vs p = 3 — the text rejects the H2O2 main effect
        (p-value 0.588), so the reported fit may have three parameters, in which
        case SS_error also contains lack of fit and the recovered scatter is an
        upper bound.
      * adjusted R^2 is printed to two decimals.
    Pooled constant variance is assumed, as ANOVA does; this is stated in the
    dataset note because the cell means span 12x.
    """
    rates = _rates(stem)
    r = int(entry.get("replicates") or 0)
    adj = entry.get("adjusted_r2")
    band = entry.get("model_params_band") or []
    if len(rates) != 4 or r < 2 or adj is None or not band:
        return None
    n = len(rates) * r
    grand = sum(rates) / len(rates)
    ss_between = r * sum((y - grand) ** 2 for y in rates)
    a = 1.0 - float(adj)
    out = []
    for p in band:
        dof = n - int(p)
        denom = (n - 1) - dof * a
        if denom <= 0:
            continue
        ss_error = dof * a * ss_between / denom
        sd = (ss_error / dof) ** 0.5
        out.append(100.0 * sd / grand)
    if not out:
        return None
    return (min(out), max(out))


def floor_percent(stem: str, entry: Dict[str, Any]
                  ) -> Tuple[Optional[float], Optional[float], str]:
    """(low, high) measurement floor in percent, plus a one-word basis."""
    kind = str(entry.get("kind"))
    if kind == "replicate_rsd":
        lo = entry.get("value_percent_min")
        hi = entry.get("value_percent_max")
        return (None if lo is None else float(lo),
                None if hi is None else float(hi), kind)
    if kind == "absolute_uncertainty":
        pct = _absolute_to_percent(stem, float(entry["value_nm_per_min"]))
        return pct, pct, kind
    if kind == "derived_pure_error":
        band = _miranda_pure_error(stem, entry)
        if band is None:
            return None, None, kind + "(unrecoverable)"
        return band[0], band[1], kind
    return None, None, kind


def report() -> str:
    statements = load_statements()
    scores = {s.dataset: s for s in score_all()}
    lines = ["dataset                                      shape%   floor%        kind",
             "-" * 96]
    quantified: List[Tuple[str, float, float]] = []
    for stem in sorted(statements):
        entry = statements[stem]
        lo, hi, kind = floor_percent(stem, entry)
        score = scores.get(stem)
        shape = ("--" if score is None or score.shape_mape is None
                 else f"{score.shape_mape:.1f}")
        floor = "--" if lo is None else (f"{lo:.1f}" if abs((hi or lo) - lo) < 0.05
                                         else f"{lo:.1f}-{hi:.1f}")
        lines.append(f"{stem[:44]:44s} {shape:>7s} {floor:>8s}   {kind}")
        if lo is not None and score is not None and score.shape_mape is not None:
            quantified.append((stem, score.shape_mape, hi or lo))

    lines.append("")
    lines.append(f"statements transcribed: {len(statements)} datasets "
                 f"({sum(1 for e in statements.values() if e.get('kind') in MEASUREMENT_KINDS)} "
                 f"quantifiable, "
                 f"{sum(1 for e in statements.values() if e.get('kind') in UNQUANTIFIED_KINDS)} "
                 "stated-but-unquantifiable or silent)")
    at = [q for q in quantified if q[1] <= q[2]]
    lines.append(f"at or below the source's OWN stated floor: {len(at)}/"
                 f"{len(quantified)} quantifiable"
                 + (": " + ", ".join(s for s, _, _ in at) if at else ""))
    above = [q for q in quantified if q[1] > q[2]]
    for stem, shape, floor in sorted(above, key=lambda q: -(q[1] / q[2])):
        lines.append(f"  ABOVE its floor by {shape / floor:.1f}x: {stem} "
                     f"({shape:.1f}% vs {floor:.1f}%)")
    return "\n".join(lines)


def summary() -> Dict[str, Any]:
    statements = load_statements()
    scores = {s.dataset: s for s in score_all()}
    out: Dict[str, Any] = {"datasets": {}}
    for stem, entry in statements.items():
        lo, hi, kind = floor_percent(stem, entry)
        score = scores.get(stem)
        out["datasets"][stem] = {
            "kind": kind,
            "floor_percent_low": None if lo is None else round(lo, 2),
            "floor_percent_high": None if hi is None else round(hi, 2),
            "shape_mape_percent": (None if score is None or score.shape_mape is None
                                   else round(score.shape_mape, 2)),
        }
    return out


def main(argv: List[str]) -> int:
    if len(argv) > 1 and argv[1] == "--json":
        print(json.dumps(summary(), indent=2))
    else:
        print(report())
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
