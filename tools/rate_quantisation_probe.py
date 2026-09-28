r"""What does the published median rest on -- the model, or `round(rate, 1)`? (59th run)

WHY THIS PROBE EXISTS
---------------------
`tools/quiet_constant_response_probe.py` set out to classify §56's 35
`untestable-no-sweep-in-reach` constants by perturbing each and watching the
SHIPPING scorer. The classification worked, and one row in it was arithmetically
impossible: `sic_ceria_h2o2.kp_m_per_pa` moved four blocks' `shape_mape` by up
to 1.3 pp.

`Kp` multiplies every predicted rate in a block by the same factor, and the
shape score fits one free multiplicative scale per block (`predictive_score`
line ~530), so that scale absorbs the factor EXACTLY and the shape MAPE must be
invariant. It is invariant everywhere else in the corpus -- `cu_h2o2_bta`'s ten
blocks return per-row ratios of 0.8000 to four decimals under a x0.8
perturbation. On `sic_ceria_h2o2` the same perturbation returns 0.8235 / 0.7895
/ 0.8049.

The cause is not in the physics. `StateResult.summary()` publishes

    "removal_rate_A_per_min": round(self.mean_rr_angstrom_per_min, 1)

-- a DISPLAY rounding, correct for a JSON result a human reads -- and
`predictive_score._predict_with_gate` reads that very field. So every predicted
rate entering the published median is quantised to 0.1 A/min. On a Cu block
predicting ~3000 A/min that is 3e-5 relative and invisible. 4H-SiC is
chemically inert and polishes at a few A/min: this pack's predictions are
3.4 / 3.8 / 4.1 A/min, where 0.1 A/min is up to **1.5% per row**, and the
quantisation error does not scale with Kp -- which is exactly why a purely
multiplicative constant appeared to change the shape of the trend.

WHAT IS MEASURED
----------------
Each scored block's `shape_mape` as published, against the same computation
reading the UNROUNDED rate (`removal_rate_nm_per_min` carries 3 decimals in
nm/min = 0.01 A/min, and `StateResult` carries full precision, so the probe
takes the float from the result object and never re-derives the physics).

The probe REPORTS. It does not change the scorer: the repair and its price are
separate decisions (§27), and a change to what the published median is computed
on must be priced before it is made.

Run:  .venv/bin/python tools/rate_quantisation_probe.py
"""
from __future__ import annotations

import statistics
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import yaml  # noqa: E402

from cmp_sim.core import predictive_score as PS  # noqa: E402
from cmp_sim.core.validation import dataset_paths  # noqa: E402

#: The display rounding under audit, as published by `StateResult.summary()`.
PUBLISHED_DECIMALS = 1

#: A block whose predicted rates sit near this magnitude has a quantisation
#: error of order 0.1 / rate per row. Printed so the reading is never quoted
#: without the quantity that produces it.
def _quantisation_pct(rates: List[float]) -> float:
    lo = min(abs(r) for r in rates if r)
    return 100.0 * (0.5 * 10 ** (-PUBLISHED_DECIMALS)) / lo


@dataclass
class BlockQuantisation:
    dataset: str
    pack: str
    n: int
    min_rate: float
    worst_row_pct: float
    shape_published: Optional[float] = None
    shape_unrounded: Optional[float] = None

    @property
    def delta_pp(self) -> Optional[float]:
        if self.shape_published is None or self.shape_unrounded is None:
            return None
        return self.shape_published - self.shape_unrounded


def _unrounded_rate(doc: Dict[str, Any], row: Dict[str, Any]) -> Optional[float]:
    """The model's rate at full precision, from the result OBJECT.

    Taken from `StateResult.mean_rr_angstrom_per_min` rather than from any
    summary field, so the probe cannot be measuring a second rounding.
    """
    from cmp_sim.api import recipe_from_dict, simulate

    try:
        result = simulate(recipe_from_dict(PS._recipe_for(doc, row)))
    except Exception:                                      # noqa: BLE001
        return None
    value = getattr(result, "mean_rr_angstrom_per_min", None)
    if value in (None, 0):
        return None
    return float(value)


def _shape(measured: List[float], predicted: List[float]) -> Optional[float]:
    denom = sum(p * p for p in predicted)
    if denom <= 0 or len(predicted) < 3:
        return None
    scale = sum(m * p for m, p in zip(measured, predicted)) / denom
    return PS._mape([(m, scale * p) for m, p in zip(measured, predicted)])


def measure() -> List[BlockQuantisation]:
    out: List[BlockQuantisation] = []
    for path in dataset_paths():
        p = Path(path)
        doc = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
        rows = [r for r in (doc.get("conditions") or [])
                if PS._measured(r) is not None]
        if len(rows) < 3:
            continue
        axes = PS._varying_axes(rows)
        gate_matters = any(a in axes for a in ("oxidizer_wt_pct", "h2o2_vol_pct"))

        measured: List[float] = []
        pub: List[float] = []
        raw: List[float] = []
        ok = True
        for row in rows:
            value, gate, _ = PS._predict_with_gate(doc, row)
            exact = _unrounded_rate(doc, row)
            if value is None or exact is None:
                ok = False
                break
            if gate and gate_matters:
                continue
            m = PS._measured(row)
            if m is None:
                continue
            measured.append(float(m))
            pub.append(float(value))
            raw.append(exact)
        if not ok or len(raw) < 3:
            continue
        block = BlockQuantisation(
            dataset=p.stem, pack=str(doc.get("pack") or "?"), n=len(raw),
            min_rate=min(raw), worst_row_pct=_quantisation_pct(raw),
            shape_published=_shape(measured, pub),
            shape_unrounded=_shape(measured, raw))
        out.append(block)
    return out


def medians(blocks: List[BlockQuantisation]) -> Tuple[Optional[float], Optional[float]]:
    """Upper medians (`sorted(e)[n//2]`, the headline convention, §35)."""
    pub = sorted(b.shape_published for b in blocks if b.shape_published is not None)
    raw = sorted(b.shape_unrounded for b in blocks if b.shape_unrounded is not None)
    return (pub[len(pub) // 2] if pub else None,
            raw[len(raw) // 2] if raw else None)


def report(blocks: Optional[List[BlockQuantisation]] = None) -> str:
    bs = measure() if blocks is None else blocks
    pub_med, raw_med = medians(bs)
    lines = [
        "blocks compared                     : %d" % len(bs),
        "published median (upper, shape)     : %s" %
        ("%.2f%%" % pub_med if pub_med is not None else "--"),
        "same, reading the UNROUNDED rate    : %s" %
        ("%.2f%%" % raw_med if raw_med is not None else "--"),
        "",
        "The published median is computed on `round(rate, %d)` -- a DISPLAY"
        % PUBLISHED_DECIMALS,
        "rounding in `StateResult.summary()`. Its relative size is set by the",
        "MAGNITUDE of the predicted rate, so it is invisible on Cu (~3000 A/min)",
        "and material on 4H-SiC (a few A/min). It does not scale with Kp, which",
        "is how a purely multiplicative constant came to move a shape score.",
        "",
        "%-52s %-22s %5s %9s %8s %8s %8s"
        % ("dataset", "pack", "n", "min A/min", "quant%", "pub", "exact"),
        "-" * 122,
    ]
    for b in sorted(bs, key=lambda b: -(b.worst_row_pct or 0)):
        d = b.delta_pp
        lines.append(
            "%-52s %-22s %5d %9.2f %8.3f %8s %8s%s"
            % (b.dataset[:52], b.pack[:22], b.n, b.min_rate, b.worst_row_pct,
               "%.3f" % b.shape_published if b.shape_published is not None else "--",
               "%.3f" % b.shape_unrounded if b.shape_unrounded is not None else "--",
               ("  <- %+.3f pp" % d) if d is not None and abs(d) >= 0.01 else ""))
    return "\n".join(lines)


if __name__ == "__main__":                                # pragma: no cover
    print(report())
