"""Price the DECLARED Cu peak position against the corpus that would grade it.

WHY
---
`cu_h2o2_bta` declares `oxidizer_peak_wt_pct: 3.0` with `confidence:
literature`, and `oxidizer_peak_shape_K: 8.0` makes it ACT — the peaked branch
in `cmp_sim/models/chemical_rate.py` is reachable (measured: perturbing the
peak moves the rate 13.9%, while the same key is inert on the two other packs
that declare it).

The only source here that RESOLVES a Cu maximum by direct measurement puts it
at 0.66-0.90 wt% (Lin & Du 2009, three dilutions), 3.3x below what the pack
declares. The declared 3.0 wt% is read from a MODELLING paper's prose about a
third party's experiment.

Before touching anything, the §21 question: CAN THE CORPUS TELL THE
DIFFERENCE? Every scored H2O2 level in this regime is 3.0 wt% or above, past
both candidate peaks, where the response is on its falling limb either way.
This measures that rather than asserting it: each Cu block is re-scored with
the peak moved to each source's position, using the scorer's OWN recipe
builder and gate so the numbers cannot disagree with the published median.

Writes nothing.
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Dict, List, Optional

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import yaml  # noqa: E402

from cmp_sim.core.predictive_score import (  # noqa: E402
    _measured, _predict_with_gate, dataset_paths, score_all,
)

PACK = "cu_h2o2_bta"
KEY = "oxidizer_peak_wt_pct"

# Candidate positions. Nothing here is invented — each is a position some
# publication reports, with how it was obtained, because the provenance is
# the whole argument.
CANDIDATES = {
    3.0: "DECLARED — [GT07], a MODELLING paper, prose about Seal et al.'s "
         "alumina/glycine experiment ('2-3.6 wt%')",
    0.90: "Lin & Du 2009, 1:6 dilution — measured maximum",
    0.74: "Lin & Du 2009, 1:8 dilution — measured maximum",
    0.66: "Lin & Du 2009, 1:10 dilution — measured maximum",
}


def _upper_median(values: List[float]) -> Optional[float]:
    """The headline convention here: sorted(e)[n//2], NOT statistics.median."""
    s = sorted(values)
    return s[len(s) // 2] if s else None


def _best_scale(measured: List[float], predicted: List[float]) -> float:
    """The one free multiplicative scale the shape score allows per block."""
    num = sum(m * p for m, p in zip(measured, predicted))
    den = sum(p * p for p in predicted)
    return (num / den) if den else 1.0


def _score_block(doc: Dict, rows: List[Dict],
                 peak: Optional[float]) -> Optional[float]:
    """Shape MAPE for one block, optionally with the peak moved."""
    measured, predicted = [], []
    for row in rows:
        m = _measured(row)
        if m is None:
            continue
        d = dict(doc)
        if peak is not None:
            # Injected the way a dataset states its own formulation constant,
            # which is the scorer's documented owner-override path.
            d["pack_overrides"] = dict(doc.get("pack_overrides") or {})
            d["pack_overrides"][KEY] = peak
        p, gated, _declined = _predict_with_gate(d, row)
        if p is None or gated:
            return None
        measured.append(m)
        predicted.append(p)
    if len(measured) < 2:
        return None
    s = _best_scale(measured, predicted)
    return 100.0 * sum(abs(s * p - m) / m
                       for m, p in zip(measured, predicted)) / len(measured)


def _cu_blocks():
    out = []
    for path in dataset_paths():
        doc = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        if not isinstance(doc, dict) or not doc.get("in_scope"):
            continue
        if doc.get("pack") != PACK:
            continue
        rows = doc.get("conditions") or []
        # Only blocks that actually sweep the oxidizer can respond at all;
        # reporting the rest would pad the table with guaranteed zeros.
        levels = sorted({v for v in
                         ((r.get("overrides") or {}).get("oxidizer_wt_pct")
                          for r in rows) if v is not None})
        out.append((path.name, doc, rows, levels))
    return out


def main() -> int:
    blocks = _cu_blocks()
    if not blocks:
        print(f"no in-scope blocks use {PACK} — this probe has no subject, "
              "which is indistinguishable from a deleted check")
        return 1

    print(f"blocks scored under {PACK}: {len(blocks)}")
    print(f"{'block':52s} {'H2O2 levels':22s} " +
          "  ".join(f"{p:>6}" for p in CANDIDATES))
    print("-" * 110)

    any_moved = False
    for name, doc, rows, levels in sorted(blocks):
        cells = []
        base = None
        for peak in CANDIDATES:
            e = _score_block(doc, rows, peak)
            cells.append(e)
            if base is None:
                base = e
        lv = ",".join(f"{x:g}" for x in levels) if levels else "(none swept)"
        row = f"{name[:52]:52s} {lv[:22]:22s} "
        row += "  ".join("  --  " if c is None else f"{c:6.1f}" for c in cells)
        spread = [c for c in cells if c is not None]
        if spread and (max(spread) - min(spread)) > 0.05:
            any_moved = True
            row += f"   <- moves {max(spread) - min(spread):.1f} pp"
        print(row)

    # The headline, from the shipping scorer, so the base number cannot drift
    # from what the README publishes.
    errs = [s.shape_mape for s in score_all()
            if s.shape_mape is not None]
    print(f"\npublished upper median (unchanged by this probe): "
          f"{_upper_median(errs):.1f}% over {len(errs)} blocks")

    print()
    if not any_moved:
        print("VERDICT: moving the peak from 3.0 to 0.66 wt% — a 4.5x move,")
        print("across the entire range any source reports — changes NO block's")
        print("score. The corpus sits entirely past both candidate peaks, so")
        print("it cannot distinguish them. The declared position is therefore")
        print("UNFALSIFIABLE by the data that grade it: it has a source, a")
        print("unit and `confidence: literature`, and no measurement here can")
        print("contradict it. That is the §35 pattern.")
        print()
        print("NOT a licence to change it to 0.66. A number nothing can test")
        print("is not improved by swapping which untested number it is; and")
        print("Lin's slurry is a different (undisclosed) composition whose")
        print("peak moves 0.90 -> 0.66 under dilution alone. The honest act")
        print("is to record that the grade `literature` overstates what this")
        print("corpus can support, and to name the sweep that would settle it")
        print("(sub-1 wt% levels with a disclosed chelator AND inhibitor).")
    else:
        print("VERDICT: at least one block responds — the peak position IS")
        print("testable here. Read the table above before changing anything.")
    print("\nNothing was written.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
