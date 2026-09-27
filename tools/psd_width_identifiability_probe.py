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

    # STANDARD ERROR -- the number whose absence let §38 assert a "disagreement
    # in sign" between two slopes, one of which is not distinguishable from
    # zero.  A sign is only a claim if the slope carrying it is a measurement:
    # with n=4 there are 2 residual degrees of freedom, so the uncertainty is
    # large and has to be quoted alongside the point estimate.  Nothing is
    # fitted into any pack here; this is the ordinary OLS slope error.
    intercept = my - slope * mx
    resid = [y - (intercept + slope * x) for x, y in zip(xs, ys)]
    dof = n - 2
    stderr = None
    if dof > 0:
        s2 = sum(r * r for r in resid) / dof
        stderr = math.sqrt(s2 / sxx) if s2 > 0 else 0.0

    # Is the width axis CONFOUNDED with the size axis the model already reads?
    # A width slope measured while D50 moves with it is partly a relabelled
    # size exponent, which is the second thing that has to be true before a
    # width term means anything.
    ds = []
    for r in rows:
        ov = r.get("overrides") or {}
        d50 = ov.get("abrasive_d50_nm") or ov.get("abrasive_size_nm")
        if d50 in (None, 0):
            ds = []
            break
        ds.append(math.log(float(d50)))
    corr = None
    if len(ds) == n:
        md = sum(ds) / n
        sdd = sum((d - md) ** 2 for d in ds)
        if sdd > 0:
            corr = (sum((x - mx) * (d - md) for x, d in zip(xs, ds))
                    / math.sqrt(sxx * sdd))

    return {"n": n, "slope": slope, "stderr": stderr,
            "t": (slope / stderr) if stderr else None,
            "width_size_corr": corr,
            "width_span": max(xs) - min(xs)}


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
    return {"blocks": blocks, "sources": sources, "rows": len(found),
            "external": external_sign_sources()}


#: Sign evidence that lives OUTSIDE the scored corpus.
#:
#: §38 required "a second, independent applicant" before the width axis could
#: be discussed at all, and looked for it among scored datasets only.  That is
#: the wrong place: a publication can establish the SIGN of an axis while being
#: unscorable for a reason that has nothing to do with the axis.  Basim 2000 is
#: exactly that case -- it varies PSD width at fixed D50 more cleanly than
#: anything in the corpus, and it cannot be scored because it prints the same
#: six removal rates three times with mutually inconsistent absolute values.
#:
#: The file is parsed rather than hard-coded so that the claim and its evidence
#: cannot drift apart: if the research note is edited or deleted, this reports
#: what the note now says, not what it said when this was written.
_EXTERNAL = Path(__file__).resolve().parents[1] / "research" / "psd_width_sign_evidence.yaml"


def external_sign_sources() -> List[Dict]:
    """Independent sign evidence for the width axis, read from research/."""
    if not _EXTERNAL.exists():
        return []
    doc = yaml.safe_load(_EXTERNAL.read_text(encoding="utf-8")) or {}
    if doc.get("axis") != "psd_width" or not doc.get("independent_of_corpus"):
        return []
    return [{
        "source": str(doc.get("source") or "")[:100],
        "direction": doc.get("direction"),
        "magnitude": doc.get("magnitude"),
        "evidence_lines": len(doc.get("direction_evidence") or []),
        "path": str(_EXTERNAL),
    }]


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
    print("    +/- is the OLS standard error on n-2 dof: a SIGN is only a claim")
    print("    if the slope carrying it is distinguishable from zero.")
    for stem, res in rep["blocks"].items():
        if res is None:
            print(f"  {stem:58s}  unscorable")
            continue
        se = res.get("stderr")
        t = res.get("t")
        corr = res.get("width_size_corr")
        print(f"  {stem:50s}  n={res['n']}  slope={res['slope']:+.3f}"
              + (f" +/- {se:.3f}" if se is not None else "")
              + (f"  t={t:+.2f}" if t is not None else "")
              + (f"  corr(width,D50)={corr:+.3f}" if corr is not None else ""))
    slopes = [r["slope"] for r in rep["blocks"].values() if r]
    measured = [r for r in rep["blocks"].values()
                if r and r.get("t") is not None and abs(r["t"]) >= 2.0]
    if len(slopes) >= 2:
        same = all(s > 0 for s in slopes) or all(s < 0 for s in slopes)
        print()
        print(f"  point-estimate signs agree : {same}")
        print(f"  blocks measuring ANY slope : {len(measured)} of "
              f"{len([r for r in rep['blocks'].values() if r])}  (|t| >= 2)")
        if not same and not measured:
            print("  => the 'films disagree in SIGN' reading is NOT supported:")
            print("     no block here measures a width slope at all, so two")
            print("     point estimates of opposite sign are two draws from")
            print("     noise, not a contradiction. (limits.md §40)")

    ext = rep.get("external") or []
    print()
    print(f"independent sign evidence OUTSIDE the scored corpus : {len(ext)}")
    for e in ext:
        print(f"  - direction={e['direction']}  magnitude={e['magnitude']}"
              f"  ({e['evidence_lines']} cited readings)")
        print(f"    {e['source']}")
        print(f"    {e['path']}")
    if ext:
        print("  => §38's exit condition ('a second, independent applicant')")
        print("     has fired. The axis now has a KNOWN SIGN and still no")
        print("     magnitude -- a sign is not a constant.")


if __name__ == "__main__":
    main()
