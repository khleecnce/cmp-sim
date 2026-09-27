"""Can a PSD-WIDTH term exist in this corpus, and would it have one sign?

Motivation.  `median_crossing_probe --held-out` puts
`us20190127607a1_teos_ceriasilica_size_sweep` (18.9%) second on the shortlist
of datasets that must cross the 15% bar.  Its own header names the cause: the
TEOS rate is NON-MONOTONIC in D50 (875 -> 1828 -> 1311 -> 2223 A/min), and the
dip is the ONE abrasive with a broad, 4-peak size distribution (D99-D50 =
146.5 nm against 65-106 nm for the others).  The model reads `abrasive_d50_nm`
only, so a single power law cannot reproduce a reversal; the obvious physics is
that the WIDTH of the size distribution, not just its median, sets how many
particles are actually loaded.

That is a real mechanism (Luo-Dornfeld: only particles within the largest
`~delta` of the distribution are indented at all, so a broad PSD puts a smaller
FRACTION of the abrasive to work at the same D50).  Before deriving it, this
probe asks the two questions §21/§28 say to ask first, both of which are
answerable with no fit and no new constant:

  Q1 REACHABILITY -- can width vary while everything the model already reads
     (D50, loading, pH, P, V) stays fixed?  Count corpus rows that declare a
     D99, and count how many distinct EXPERIMENTS they come from.  A constant
     identifiable in only one experiment is interpolation of that experiment.

  Q2 SIGN -- inside the blocks where it IS reachable, does the residual point
     the same way?  A mechanical particle-count term cannot depend on which
     oxide was deposited, so if the two films in the SAME runs disagree in
     sign, no shared width constant is even the right direction (§14's test).

Nothing is fitted into any pack.  Run:
    python tools/psd_width_identifiability_probe.py
"""

from __future__ import annotations

import math
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import yaml

from cmp_sim.core.predictive_score import (  # noqa: E402
    _measured, _predict_with_gate, dataset_paths,
)


def _width_ratio(ov: Dict) -> Optional[float]:
    """(D99 - D50) / D50 -- the dimensionless spread of the distribution.

    Dimensionless because the size term already reads the scale (D50); the
    question here is exclusively about SHAPE, and a ratio cannot be a
    relabelled size exponent.
    """
    d50 = ov.get("abrasive_d50_nm") or ov.get("abrasive_size_nm")
    d99 = ov.get("abrasive_d99_nm")
    if d50 in (None, 0) or d99 in (None, 0):
        return None
    w = (float(d99) - float(d50)) / float(d50)
    return w if w > 0 else None


def rows_with_width() -> List[Tuple[str, Dict, Dict]]:
    """(dataset stem, doc, row) for every scored row declaring a D99."""
    out = []
    for path in dataset_paths():
        doc = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        for row in doc.get("conditions") or []:
            if _measured(row) is None:
                continue
            if _width_ratio(row.get("overrides") or {}) is None:
                continue
            out.append((path.stem, doc, row))
    return out


def _residual_slope(doc: Dict, rows: List[Dict]) -> Optional[Dict]:
    """Slope of ln(measured/predicted) against ln(width ratio).

    The scorer's one free multiplicative scale cancels out of a SLOPE, so this
    needs no calibration and no fit beyond the regression itself.
    """
    xs, ys, preds, meas = [], [], [], []
    for row in rows:
        pred, _gate, _declined = _predict_with_gate(doc, row)
        m = _measured(row)
        w = _width_ratio(row.get("overrides") or {})
        if pred is None or pred <= 0 or m is None or m <= 0 or w is None:
            return None
        xs.append(math.log(w))
        ys.append(math.log(m / pred))
        preds.append(pred)
        meas.append(m)
    n = len(xs)
    if n < 3:
        return None
    mx = sum(xs) / n
    my = sum(ys) / n
    sxx = sum((x - mx) ** 2 for x in xs)
    if sxx <= 0:
        return None
    slope = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sxx
    return {"n": n, "slope": slope, "width_span": max(xs) - min(xs)}


def report() -> Dict:
    found = rows_with_width()
    by_ds: Dict[str, List[Dict]] = {}
    docs: Dict[str, Dict] = {}
    for stem, doc, row in found:
        by_ds.setdefault(stem, []).append(row)
        docs[stem] = doc

    # An "experiment" is the source publication, not the file: the two oxide
    # files here are the SAME four polishing runs measured on two films, so
    # counting them as two independent sources would let one patent supply its
    # own replication (§33's publication-level holdout lesson).
    sources = {}
    for stem, doc in docs.items():
        key = (doc.get("doi") or str(doc.get("source") or ""))[:80]
        sources.setdefault(key, []).append(stem)

    blocks = {}
    for stem, rows in sorted(by_ds.items()):
        blocks[stem] = _residual_slope(docs[stem], rows)
    return {"blocks": blocks, "sources": sources, "rows": len(found)}


def main() -> None:
    rep = report()
    print("PSD-WIDTH IDENTIFIABILITY PROBE")
    print("=" * 66)
    print(f"rows declaring a D99 : {rep['rows']}")
    print(f"datasets             : {len(rep['blocks'])}")
    print(f"independent sources  : {len(rep['sources'])}")
    for key, stems in rep["sources"].items():
        print(f"  - {key[:60]:60s} {', '.join(stems)}")
    print()
    print("Q2  residual slope d ln(meas/pred) / d ln((D99-D50)/D50)")
    print("    (the scorer's free scale cancels out of a slope -- nothing fitted)")
    for stem, res in rep["blocks"].items():
        if res is None:
            print(f"  {stem:58s}  unscorable")
            continue
        print(f"  {stem:58s}  n={res['n']}  slope={res['slope']:+.3f}"
              f"  ln-span={res['width_span']:.2f}")
    slopes = [r["slope"] for r in rep["blocks"].values() if r]
    if len(slopes) >= 2:
        same = all(s > 0 for s in slopes) or all(s < 0 for s in slopes)
        print()
        print(f"  signs agree: {same}")
        if not same:
            print("  => no shared width constant is even the right DIRECTION")
            print("     (§14): the same four abrasives, the same polishing runs,")
            print("     two oxide films, opposite residual signs.")


if __name__ == "__main__":
    main()
