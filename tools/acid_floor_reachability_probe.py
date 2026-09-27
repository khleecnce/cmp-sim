"""Probe: can ``ph_acid_mechanical_floor`` reach any prediction at all?

This is a MEASUREMENT script, not production code. It touches no pack.

THE QUESTION
------------
``ph_acid_mechanical_floor`` is the rate below the pH optimum as a fraction of
the peak. Three packs carry it at ``confidence: low`` with the source line
``TODO(owner) - order-of-magnitude bound, not a measurement``, i.e. it is an
invented number that looks like physics in the pack file.

The previous run withdrew ``abrasive_conc_half_wt_pct`` by asking whether a
fitted constant was NECESSARY (does removing it push the model outside the
measured band) rather than whether it scored well. This probe asks the cheaper
question that comes BEFORE necessity, and needs no measurement at all:

    can this constant change ANY number the model can be asked for?

WHY IT CAN FAIL TO
------------------
``chemical_rate`` clamps the evaluated pH to the pack's ``ph_valid_range``
before the bell is evaluated (the far tail of a locally fitted Gaussian is an
artefact of the function, not of a measurement). ``ph_response`` selects the
acid-side floor only when ``pH < ph_peak``. Composing those two:

    the acid floor is reachable  <=>  ph_valid_range[0] < ph_peak

When a pack's optimum sits AT the lower edge of the range its constants were
measured over -- which is exactly what happens when the sweep's lowest point
is its highest rate -- no admissible query is ever below the peak, so the
acid-side floor is unreachable for every input, at every pressure and speed.
Such a constant is not merely unused on this corpus; it is structurally
incapable of acting, and no future dataset changes that without also changing
``ph_valid_range``.

WHAT IS MEASURED
----------------
Per pack carrying the key:

    reachable      structural: ph_valid_range[0] < ph_peak
    width          how many pH units of the admissible window are acid-side
    max_delta_pct  the largest rate change over a pH scan when the constant is
                   replaced by the alternative the engine would otherwise use
                   (the alkaline floor -- the documented default when the key
                   is absent), measured by running the SHIPPING solver

The second number is the one that matters: "structurally unreachable" is a
claim about code paths, and this repo's own history says a claim about code
paths must be confirmed on the shipping path before it is acted on.
"""
from __future__ import annotations

import os
import sys
from typing import Any, Dict, List, Optional

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE)

from cmp_sim.api import run_recipe            # noqa: E402
from cmp_sim.core.params import load_pack     # noqa: E402
from cmp_sim.core.predictive_score import PACK_FILM  # noqa: E402

KEY = "ph_acid_mechanical_floor"

#: pH values to scan. Deliberately wider than any pack's valid range, because
#: a clamped query is exactly the case being tested.
PH_SCAN = [1.0, 2.0, 2.5, 3.0, 4.0, 4.9, 5.5, 6.0, 7.0, 8.0, 9.0, 10.0, 10.5,
           11.0, 12.0, 13.0]


def _rate(pack: str, film: str, ph: float,
          override: Any = ...) -> Optional[float]:
    recipe: Dict[str, Any] = {
        "model": "auto",
        "wafer": {"film": film, "n_radial": 11},
        "slurry": {"pack": pack, "ph": ph},
        "tool": {"pressure_psi": 4.0, "rpm_platen": 60, "rpm_head": 60,
                 "time_s": 60.0},
    }
    if override is not ...:
        recipe["params"] = {KEY: override}
    try:
        value = run_recipe(recipe).get("removal_rate_A_per_min")
    except Exception:
        return None
    return None if not value else float(value)


def probe() -> List[dict]:
    rows: List[dict] = []
    for pack_name, film in PACK_FILM.items():
        try:
            pack = load_pack(pack_name)
        except Exception:
            continue
        param = pack.params.get(KEY)
        if param is None or param.value is None:
            continue
        peak = pack.params.get("ph_peak")
        peak = None if peak is None else peak.value
        rng = pack.params.get("ph_valid_range")
        rng = None if rng is None else rng.value
        alk = pack.params.get("ph_mechanical_floor")
        alk = None if alk is None else alk.value
        low = float(rng[0]) if isinstance(rng, (list, tuple)) else None
        acid_span = 0.0
        reachable = False
        if peak is not None and low is not None and low < float(peak):
            reachable = True
            acid_span = float(peak) - low

        # The alternative is what the engine uses when the key is ABSENT:
        # ph_acid_mechanical_floor defaults to ph_mechanical_floor.
        max_delta = 0.0
        worst_ph = None
        for ph in PH_SCAN:
            base = _rate(pack_name, film, ph)
            alt = _rate(pack_name, film, ph, alk)
            if base and alt:
                delta = abs(alt - base) / base * 100.0
                if delta > max_delta:
                    max_delta, worst_ph = delta, ph
        rows.append({
            "pack": pack_name, "value": param.value,
            "confidence": param.confidence, "peak": peak,
            "range": rng, "alkaline_floor": alk,
            "reachable": reachable, "acid_span_ph_units": round(acid_span, 2),
            "max_delta_pct": round(max_delta, 3), "worst_ph": worst_ph,
        })
    return rows


def main() -> int:
    print(f"{'pack':30s} {'val':>6s} {'conf':>11s} {'peak':>5s} "
          f"{'range':>12s} {'acid_span':>9s} {'reach':>5s} {'max_dRate%':>10s}")
    for r in probe():
        rng = (f"{r['range'][0]:g}-{r['range'][1]:g}"
               if isinstance(r["range"], (list, tuple)) else "none")
        print(f"{r['pack'][:30]:30s} {r['value']:6.3f} {str(r['confidence']):>11s} "
              f"{str(r['peak']):>5s} {rng:>12s} {r['acid_span_ph_units']:9.2f} "
              f"{str(r['reachable']):>5s} {r['max_delta_pct']:10.3f}")
    print()
    print("reachable=False means NO admissible pH is below the optimum, so the "
          "acid-side floor cannot enter any prediction: the clamp to "
          "ph_valid_range happens before ph_response picks a side.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
