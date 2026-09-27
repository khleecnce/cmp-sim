"""Is the abrasive supply a MONOLAYER? Measure it instead of assuming it.

Why this exists
---------------
``legacy/sim/abrasive_mechanics.decide_supply`` is the third of the three
regime questions that set the concentration and size exponents:

    n_C = p * (1 - alpha*chi)
    n_d = -q * (1 - alpha*chi) + beta

``p`` and ``q`` come from the gap/particle-diameter ratio: a gap that admits
one layer of particles gives ``p = 1, q = 2``; a gap several particles deep
gives a smaller ``p`` because only a fraction of the particles present are in
contact at any instant.

The solver hands ``decide_supply`` ``pad_wafer_gap_m``, which **no pack
declares and no caller sets** — it is in ``KNOWN_NON_PACK_KEYS`` as a "solved
quantity". So the decision is never made: every run takes the ``None`` branch,
which returns the monolayer values with confidence ``estimated`` and this note:

    "공급 형태 미판정: 패드-웨이퍼 간극을 모른다. 단층으로 가정한다"
    ("supply form UNDECIDED: the pad-wafer gap is unknown. Assuming monolayer")

Meanwhile the SAME run already solves a fluid film thickness and a lambda ratio
from sourced lubrication physics (``cmp_sim/models/uniformity.py`` ->
``legacy`` Sommerfeld / elastohydrodynamic film). That quantity is printed in
every result under ``uniformity``. So the model states it does not know a
number it has just computed.

What this script does (MEASUREMENT ONLY — fits nothing, edits no pack)
----------------------------------------------------------------------
For the first row of every scored dataset it reports

  * the solved mean fluid film thickness ``h`` and lambda ratio,
  * the recipe's abrasive diameter ``d``,
  * the ratio ``h/d`` that ``decide_supply`` would branch on,
  * the lubrication regime the model classified.

Reading it
----------
``decide_supply`` switches at ``h/d = 1.5``. Two outcomes are possible and they
have OPPOSITE consequences, which is why this has to be measured before any
wiring is done:

  * ``h/d <= 1.5`` corpus-wide — the monolayer assumption is CORRECT, and the
    only defect is that it is graded ``estimated`` while announcing ignorance.
    Wiring the gap changes no exponent and no prediction; it converts an
    undetermined axis into a determined one. The honest action is then to fix
    the grade and the note, not the number.
  * ``h/d > 1.5`` on some runs — ``p`` is genuinely below 1 there, every
    concentration exponent derived on those runs is too steep, and the fix
    changes predictions.

CAUTION, stated before the numbers are read: the mean fluid film thickness is
NOT obviously the gap ``decide_supply`` means. Luo-Dornfeld's active particles
are the ones trapped between a pad ASPERITY and the wafer, where the local gap
is set by the asperity contact, not by the mean film over the whole wafer. In
boundary lubrication (lambda < 1) the two coincide, because the film is thinner
than the roughness and asperities carry the load. In full-film lubrication they
do not, and the mean film is the wrong quantity. So this probe is only
licensed to conclude anything where the model itself reports boundary or mixed
lubrication.

Usage: ``PYTHONPATH=. .venv/bin/python tools/supply_gap_probe.py``
"""
from __future__ import annotations

import statistics
from typing import Any, Dict, List, Optional, Tuple

import yaml

from cmp_sim.core.predictive_score import _recipe_for
from cmp_sim.core.validation import dataset_paths

#: decide_supply's own branch point (legacy/sim/abrasive_mechanics.py).
MONOLAYER_RATIO = 1.5


def _first_row_report(path) -> Optional[Dict[str, Any]]:
    doc = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    conditions = doc.get("conditions") or []
    if not conditions:
        return None
    from cmp_sim.api import run_recipe
    try:
        result = run_recipe(_recipe_for(doc, conditions[0]))
    except Exception as exc:                                 # pragma: no cover
        return {"dataset": path.stem, "error": str(exc)[:70]}
    # The solved film lives under `slurry_supply`, which is where the
    # lubrication layer publishes it; `uniformity` carries the radial spread.
    supply = result.get("slurry_supply") or {}
    prov = result.get("provenance") or {}
    d_nm = None
    for key in ("abrasive_d50_nm", "abrasive_size_nm"):
        entry = prov.get(key)
        value = entry.get("value") if isinstance(entry, dict) else entry
        if value:
            d_nm = float(value)
            break
    h_nm = supply.get("film_thickness_nm")
    return {
        "dataset": path.stem,
        "h_nm": h_nm,
        "d_nm": d_nm,
        "lambda": supply.get("lambda_ratio"),
        "regime": supply.get("lubrication_regime"),
        "ratio": (float(h_nm) / d_nm) if (h_nm and d_nm) else None,
    }


def collect() -> List[Dict[str, Any]]:
    out = []
    for path in dataset_paths():
        row = _first_row_report(path)
        if row is not None:
            out.append(row)
    return out


def report(rows: List[Dict[str, Any]]) -> str:
    lines = [f"{'dataset':46s} {'h (nm)':>10s} {'d (nm)':>8s} "
             f"{'h/d':>8s} {'lambda':>8s}  regime"]
    lines.append("-" * 104)
    ratios: List[float] = []
    multilayer: List[Tuple[str, float]] = []
    for r in sorted(rows, key=lambda x: -(x.get("ratio") or -1)):
        if r.get("error"):
            lines.append(f"{r['dataset'][:44]:46s} {'ERROR: ' + r['error']}")
            continue
        ratio = r.get("ratio")
        if ratio is not None:
            ratios.append(ratio)
            if ratio > MONOLAYER_RATIO:
                multilayer.append((r["dataset"], ratio))
        fmt = lambda v, n=2: ("—" if v is None else f"{float(v):.{n}f}")
        lines.append(f"{r['dataset'][:44]:46s} {fmt(r['h_nm']):>10s} "
                     f"{fmt(r['d_nm'], 1):>8s} {fmt(ratio):>8s} "
                     f"{fmt(r['lambda'], 3):>8s}  {r.get('regime') or '—'}")
    lines.append("")
    if ratios:
        lines.append(f"{len(ratios)} datasets with a solvable gap/diameter "
                     f"ratio; median h/d = {statistics.median(ratios):.3f}, "
                     f"range {min(ratios):.3f}..{max(ratios):.3f}")
        lines.append(f"decide_supply's monolayer branch point is h/d = "
                     f"{MONOLAYER_RATIO}")
        if multilayer:
            lines.append(f"MULTILAYER on {len(multilayer)}: "
                         + ", ".join(f"{n} ({v:.2f})" for n, v in multilayer[:8]))
            lines.append("=> p < 1 there; the monolayer assumption is NOT "
                         "corpus-wide and wiring the gap changes predictions.")
        else:
            lines.append("=> every solvable run is MONOLAYER by the model's own "
                         "solved film. The p=1,q=2 default is correct; the "
                         "defect is the 'undecided' grade, not the number.")
    return "\n".join(lines)


if __name__ == "__main__":
    print(report(collect()))
