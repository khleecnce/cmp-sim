"""Probe: is the passivation breakthrough pressure P0 a PER-FILM constant?

Context (STATUS.md NEXT, 2026-09-25)
------------------------------------
`tools/pv_regime_probe.py` established two things and left one open.

  * Fitting RR ~ k*P^a*V^b on matched-condition rows only (group by every
    override except P and V) collapses the exponent scatter -- most of the
    "regime split" was a confound with composition axes.
  * The residual super-linearity still correlates with LOW absolute pressure
    (rho(a, Pmean) = -0.696 under that control), which is the signature the
    breakthrough form predicts.

        RR = Kp * max(P - P0, 0) * V          (P0 >= 0)
        a_local = d ln RR / d ln P = P / (P - P0)   -> >1 near P0, ->1 far above

    ONE GLOBAL P0 bought only 0.3 points (25.3% -> 25.0%) and was not adopted.

Why per-FILM is the right next cut, physically
----------------------------------------------
P0 is not a property of the tool; it is the stress at which the asperity
contact breaks through the passivating layer the CHEMISTRY grows on that film
(Cu-BTA complex, WO3, hydrated silica gel). A breakthrough stress scales with
that layer's own hardness/thickness, so it can be shared WITHIN a film and must
not be shared ACROSS films. One global P0 averages layers with very different
yield stresses, which is why it bought almost nothing.

What makes this a law rather than interpolation
-----------------------------------------------
One constant per film is only meaningful if that film has several INDEPENDENT
matched-condition pressure datasets. In this corpus, after the matched-condition
control: oxide has the most, Cu next, W one. A constant fitted across 4 datasets
and then tested on a 5th it never saw is a law; a constant fitted on 1 dataset
is interpolation. So this script scores LEAVE-ONE-DATASET-OUT: P0 is fitted on
the other datasets of the same film, then applied unseen to the held-out one,
with the multiplicative scale still free per dataset (no two tools share a Kp).

Adopt ONLY if the held-out error beats Preston (P0 = 0) out of sample.
This script changes no model constant; it prints numbers.
"""
from __future__ import annotations

import statistics
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from cmp_sim.core.validation import dataset_paths  # noqa: E402
from tools.pv_regime_probe import (  # noqa: E402
    preston_err,
    pv_rows,
    threshold_err,
)

P0_GRID = [i * 0.05 for i in range(0, 61)]   # 0 .. 3.00 psi


def collect():
    """{film: [(stem, rows), ...]} for matched-condition pressure datasets."""
    by_film: dict[str, list] = {}
    for path in dataset_paths():
        doc = yaml.safe_load(path.read_text()) or {}
        rows = pv_rows(doc)
        if len(rows) < 3:
            continue
        if len({r[0] for r in rows}) < 2:      # needs a pressure axis
            continue
        by_film.setdefault(doc.get("film") or "?", []).append((path.stem, rows))
    return by_film


def fit_p0(sets):
    """Shared P0 minimising the mean scale-free MAPE over `sets`."""
    best = None
    for p0 in P0_GRID:
        errs = [threshold_err(rows, p0) for _, rows in sets]
        if any(e is None for e in errs):
            continue
        m = statistics.fmean(errs)
        if best is None or m < best[0]:
            best = (m, p0)
    return best


def main():
    by_film = collect()
    print("matched-condition pressure datasets per film:")
    for film, sets in sorted(by_film.items()):
        print(f"  {film:10s} {len(sets)}  " + ", ".join(s for s, _ in sets))

    for film, sets in sorted(by_film.items()):
        if len(sets) < 3:
            print(f"\n{film}: {len(sets)} dataset(s) -- too few for a "
                  f"leave-one-out test of one shared constant; skipped.")
            continue
        print(f"\n=== {film} ===")
        insample = fit_p0(sets)
        print(f"  in-sample shared P0 = {insample[1]:.2f} psi "
              f"(mean MAPE {insample[0]:.1f}%)")
        prest, held = [], []
        for i, (stem, rows) in enumerate(sets):
            rest = [s for j, s in enumerate(sets) if j != i]
            fit = fit_p0(rest)
            if fit is None:
                continue
            p0 = fit[1]
            e_p0 = threshold_err(rows, p0)
            e_pr = preston_err(rows)
            if e_p0 is None or e_pr is None:
                continue
            prest.append(e_pr)
            held.append(e_p0)
            flag = "BETTER" if e_p0 < e_pr else ""
            print(f"    hold out {stem[:40]:40s} P0(rest)={p0:4.2f}  "
                  f"preston {e_pr:6.1f}%  ->  {e_p0:6.1f}%  {flag}")
        if prest:
            print(f"  OUT OF SAMPLE mean: preston {statistics.fmean(prest):.1f}%"
                  f"  ->  P0-form {statistics.fmean(held):.1f}%")
            print(f"  median:             preston {statistics.median(prest):.1f}%"
                  f"  ->  P0-form {statistics.median(held):.1f}%")


if __name__ == "__main__":
    main()
