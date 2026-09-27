"""Census: which pack constants can reach ANY prediction the model can be asked for?

This is a MEASUREMENT script, not production code. It modifies no pack.

WHY THIS EXISTS
---------------
The 26th run withdrew two invented constants (``ph_acid_mechanical_floor`` in
``cu_h2o2_bta`` and ``oxide_silica``) after showing they were STRUCTURALLY
UNREACHABLE: ``chemical_rate`` clamps the queried pH into ``ph_valid_range``
before ``ph_response`` picks the acid side, so a pack whose optimum sits at the
lower edge of its measured window can never evaluate the acid branch, at any
pressure, speed or composition. The constant looked like physics in the pack
file and was impossible to falsify.

That was found by reading one gate. The lesson recorded in STATUS was the
general one -- *ask reachability before necessity, because reachability is
decided by code structure alone, costs nothing to measure, and removes invented
numbers without touching the score* -- but it had only ever been applied to a
single key. This census applies it to EVERY numeric constant in EVERY pack.

An unreachable constant is worse than an unused one. An unused key is found by
grepping; an unreachable one is referenced by live code, reads as a sourced
physical quantity, participates in review, and yet cannot change any answer, so
no dataset can ever contradict it.

METHOD (measurement only -- nothing is fitted)
----------------------------------------------
For each pack:

1. Build an ADMISSIBLE QUERY GRID -- recipes the shipping API accepts, spanning
   the axes the engine actually gates on: pH across the pack's own
   ``ph_valid_range`` (endpoints and midpoint, since anything outside is
   clamped and therefore not a distinct query), oxidiser concentration
   including zero, abrasive size and concentration, pressure, platen speed,
   platen temperature, flow and polish time.
2. Record the baseline rate at every grid point with the SHIPPING solver
   (``cmp_sim.api.run_recipe``), exactly as a user would get it.
3. For every numeric constant in the pack, re-run the whole grid with that one
   constant perturbed, and take the largest relative rate change.

A constant whose largest change over the entire admissible grid is below
``DEAD_TOLERANCE`` cannot enter any prediction: it is dead code wearing a
citation.

WHAT THE RESULT DOES *NOT* MEAN
-------------------------------
Unreachable is not the same as unnecessary, and neither is a licence to delete.
Three outcomes are distinguished in the report and must be treated differently:

``dead``
    No admissible query moves the rate. Candidate for withdrawal -- but only
    after asking WHY: a documentation-only key (deliberately unwired, with the
    reason in its note) is honest and must stay; a key whose gate was added
    later (the acid-floor case) is an expired safeguard and should be
    withdrawn; a key awaiting a dataset is a declared gap.
``narrow``
    Reachable, but only on a small part of the grid. These are where a wrong
    value hides, because a corpus that does not sweep that corner scores the
    same either way.
``live``
    Moves predictions across the grid. Nothing to do.

KNOWN LIMITS OF THIS INSTRUMENT (read before quoting any count)
---------------------------------------------------------------
The ``dead`` count is an upper bound on deadness and is NOT a list of things
to delete. Two revisions of this tool already produced wrong counts for
instrument reasons, and both are recorded here because the number looks
authoritative either way:

1. Watching only ``removal_rate_A_per_min`` called 86/102 tungsten constants
   dead, including ``scratch_threshold_nm``, which is *supposed* to move only
   the defect index. Fixed by walking every numeric leaf of the response.
2. Never NAMING a pad or disk, never patterning the wafer and never setting
   zone pressures left whole subsystems switched off, so their constants could
   not move anything. Fixed by the ``rich`` grid.

What is still not perturbed, and therefore still over-reports deadness:

* the abrasive TAIL (``abrasive_d99_nm``) is held at each pack's reference, so
  ``damage_exponent`` sees a tail ratio of exactly 1.0 at every grid point and
  reports dead in all twelve packs. It is demonstrably live -- the defect
  behaviour tests vary D99 and see the exponent applied.
* pad and conditioner AGEING (usage hours, conditioning duty) are never
  advanced, so the whole ``stab_*`` / ``cond_*`` / ``pad_wear_*`` family cannot
  respond.
* reference constants (``*_ref_*``) are denominators of ratios whose numerator
  the grid holds fixed; perturbing the pair together is the only meaningful
  test and this tool perturbs one at a time.

So: a ``live`` verdict is trustworthy, and a ``dead`` verdict is a QUESTION --
"is this constant unreachable, or did the probe never switch on the thing it
drives?" -- which must be answered per constant before anything is withdrawn.

Usage: ``python tools/constant_reachability_census.py [--pack NAME] [--jobs N]``
"""
from __future__ import annotations

import argparse
import os
import sys
from concurrent.futures import ProcessPoolExecutor
from typing import Any, Dict, List, Optional, Tuple

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE)

from cmp_sim.api import run_recipe            # noqa: E402
from cmp_sim.core.params import load_pack     # noqa: E402
from cmp_sim.core.predictive_score import PACK_FILM  # noqa: E402

#: Largest relative rate change (%) that still counts as "no effect". Shared
#: with residual_census/inert_axis_scan so the three tools agree on what a
#: non-response is; well above float noise, far below any physical effect.
DEAD_TOLERANCE = 0.5

#: A constant that moves the rate on this fraction of grid points or fewer is
#: reachable but NARROW: a wrong value there is invisible to most of the corpus.
NARROW_FRACTION = 0.20

#: Multiplier applied to a constant to test whether it matters. 1.5 is large
#: enough that any term with a sane functional form responds, and small enough
#: that it stays inside the same physical regime. Zero-valued constants are
#: perturbed additively instead, because scaling zero tests nothing.
PERTURB_FACTOR = 1.5
ZERO_PERTURB = 0.1


def _grid(pack_name: str, film: str) -> List[Dict[str, Any]]:
    """Admissible recipes spanning every axis the engine gates on."""
    pack = load_pack(pack_name)

    def pv(key: str, default: Any = None) -> Any:
        p = pack.params.get(key)
        return default if p is None or p.value is None else p.value

    rng = pv("ph_valid_range")
    if isinstance(rng, (list, tuple)) and len(rng) == 2:
        lo, hi = float(rng[0]), float(rng[1])
        # Only pH values INSIDE the declared window are distinct queries:
        # chemical_rate clamps anything outside, so a pH-1 probe and a pH-lo
        # probe are literally the same evaluation.
        phs = [lo, (lo + hi) / 2.0, hi]
    else:
        phs = [4.0, 7.0, 10.0]
    peak = pv("ph_peak")
    if peak is not None and float(peak) not in phs:
        phs.append(float(peak))

    ox_ref = pv("oxidizer_ref_wt_pct") or pv("oxidizer_peak_wt_pct") or 2.0
    size_ref = pv("abrasive_ref_size_nm") or pv("abrasive_size_peak_nm") or 100.0
    conc_ref = pv("abrasive_ref_wt_pct") or 5.0

    base: Dict[str, Any] = {
        "model": "auto",
        "wafer": {"film": film, "n_radial": 11},
        "slurry": {"pack": pack_name},
        "tool": {"pressure_psi": 4.0, "rpm_platen": 60.0, "rpm_head": 57.0,
                 "time_s": 60.0, "flow_ml_min": 200.0},
    }

    # A grid that never NAMES a pad or a disk, never patterns the wafer and
    # never sets zone pressures leaves whole subsystems unexercised, and every
    # constant in them is then reported dead by an instrument that never
    # switched them on. The first version of this census did exactly that and
    # called 1015 of 1201 constants dead -- a number produced by the probe, not
    # by the model. The rich variant below turns those subsystems on.
    rich: Dict[str, Any] = {
        "model": "auto",
        "wafer": {"film": film, "n_radial": 21, "pattern_density": 0.5,
                  "pitch_um": 100.0, "initial_thickness_nm": 1000.0},
        "slurry": {"pack": pack_name},
        "pad": {"name": "IC1010", "groove_width_mm": 0.5,
                "groove_pitch_mm": 2.0, "groove_depth_mm": 0.75},
        "disk": {},
        "tool": {"pressure_psi": 4.0, "rpm_platen": 60.0, "rpm_head": 57.0,
                 "time_s": 120.0, "flow_ml_min": 200.0,
                 "zone_pressures_psi": [3.0, 4.0, 5.0],
                 "zone_edges_norm": [0.0, 0.4, 0.8, 1.0],
                 "retaining_ring_psi": 5.0, "center_offset_m": 0.15,
                 "platen_temp_c": 40.0},
    }

    def variant(_from: Optional[Dict[str, Any]] = None, **over) -> Dict[str, Any]:
        import copy
        r = copy.deepcopy(_from if _from is not None else base)
        slurry = r["slurry"]
        tool = r["tool"]
        if "ph" in over:
            slurry["ph"] = over["ph"]
        if "ox" in over:
            slurry["additives"] = [{"name": over.get("ox_name", "hydrogen peroxide"),
                                    "conc_wt_pct": over["ox"],
                                    "role": "oxidizer"}]
        if "size" in over or "conc" in over:
            slurry["abrasive"] = {}
            if "size" in over:
                slurry["abrasive"]["d50_nm"] = over["size"]
            if "conc" in over:
                slurry["abrasive"]["conc_wt_pct"] = over["conc"]
        for k in ("pressure_psi", "rpm_platen", "platen_temp_c", "flow_ml_min",
                  "time_s"):
            if k in over:
                tool[k] = over[k]
        return r

    grid: List[Dict[str, Any]] = [base, rich]
    grid += [variant(ph=p) for p in phs]
    grid += [variant(ox=c) for c in (0.0, float(ox_ref) * 0.5, float(ox_ref),
                                     float(ox_ref) * 2.0)]
    grid += [variant(size=float(size_ref) * f) for f in (0.4, 2.5)]
    grid += [variant(conc=float(conc_ref) * f) for f in (0.3, 3.0)]
    grid += [variant(pressure_psi=p) for p in (1.0, 8.0)]
    grid += [variant(rpm_platen=v) for v in (20.0, 120.0)]
    grid += [variant(platen_temp_c=t) for t in (20.0, 60.0)]
    grid += [variant(flow_ml_min=f) for f in (50.0, 400.0)]
    grid += [variant(time_s=t) for t in (15.0, 180.0)]
    # The same sweeps again with pad, disk, pattern and zones switched ON.
    # Several subsystems (pad wear, conditioning, pattern, zone pressure) only
    # evaluate when their inputs were actually named, so a constant can be
    # reachable ONLY on this branch.
    grid += [variant(rich, ph=phs[0]), variant(rich, ph=phs[-1]),
             variant(rich, pressure_psi=1.0), variant(rich, pressure_psi=8.0),
             variant(rich, rpm_platen=120.0), variant(rich, time_s=600.0),
             variant(rich, flow_ml_min=50.0), variant(rich, platen_temp_c=60.0),
             variant(rich, size=float(size_ref) * 2.5),
             variant(rich, conc=float(conc_ref) * 3.0),
             variant(rich, ox=0.0), variant(rich, ox=float(ox_ref) * 2.0)]
    # The most informative points are combinations: a gate can be open on one
    # axis only while another axis is off its default.
    grid += [variant(ph=phs[0], ox=float(ox_ref), pressure_psi=8.0),
             variant(ph=phs[-1], ox=0.0, pressure_psi=1.0),
             variant(ph=phs[len(phs) // 2], platen_temp_c=60.0,
                     rpm_platen=120.0)]
    return grid


#: Every numeric OUTPUT the shipping API reports, not just the rate.
#:
#: The first version of this census watched ``removal_rate_A_per_min`` alone
#: and pronounced 86 of 102 tungsten constants dead. That verdict was an
#: artefact of the instrument: ``scratch_threshold_nm`` is supposed to leave
#: the rate untouched -- it feeds the defect proxy -- and a probe that cannot
#: see the defect index cannot tell "does nothing" from "does something I am
#: not looking at". A reachability claim is only as wide as the outputs it
#: watches, so the response is a VECTOR over everything the user is shown.
#: The former hand-written list of watched outputs, kept only as documentation
#: of what the first version could see. ``_numeric_leaves`` now walks the whole
#: response, so nothing is watched by name any more.
_OUTPUT_PATHS: Tuple[Tuple[str, ...], ...] = (
    ("removal_rate_A_per_min",),
    ("wiwnu_percent",),
    ("uniformity", "sigma_pct"),
    ("uniformity", "edge_center"),
    ("defect_risk", "delta_risk_index"),
    ("defect_risk", "d99_over_scratch_threshold"),
    ("defect_risk", "max_scratch_width_nm"),
    ("defect_risk", "max_scratch_depth_nm"),
    ("slurry_supply", "supply_number"),
    ("slurry_supply", "lambda_ratio"),
    ("slurry_supply", "film_thickness_nm"),
    ("pad_life", "rr_drift_pct"),
    ("pad_life", "asperity_ratio"),
    ("pattern", "dishing_nm"),
    ("pattern", "erosion_nm"),
    ("pattern", "step_height_nm"),
)


#: Output keys that are NOT a model response and must never count as one.
#: Echoes of the input (the tool settings the caller passed in) would make
#: every constant look alive the moment the rich grid changed a tool setting.
_IGNORED_LEAF_KEYS = frozenset({
    "flow_ml_min", "pressure_psi", "rpm_platen", "rpm_head", "time_s",
    "platen_temp_c", "n_radial", "diameter_mm", "pattern_density", "pitch_um",
})


def _numeric_leaves(node: Any, path: str = "",
                    out: Optional[Dict[str, float]] = None) -> Dict[str, float]:
    """Every numeric leaf in the API's JSON output, keyed by dotted path.

    Walking the WHOLE response rather than a hand-written list of paths is the
    point: a hand-written list is exactly the instrument that pronounced 1015
    constants dead, because it could not see the outputs they drive. A key it
    has never heard of is the case that matters.
    """
    if out is None:
        out = {}
    if isinstance(node, bool):
        return out
    if isinstance(node, (int, float)):
        out[path] = float(node)
    elif isinstance(node, dict):
        for k, v in node.items():
            if k in _IGNORED_LEAF_KEYS:
                continue
            _numeric_leaves(v, f"{path}.{k}" if path else str(k), out)
    elif isinstance(node, list):
        for i, v in enumerate(node):
            _numeric_leaves(v, f"{path}[{i}]", out)
    return out


def _response(recipe: Dict[str, Any],
              override: Optional[Dict[str, Any]] = None
              ) -> Optional[Dict[str, float]]:
    """Every numeric output the API reports, keyed by dotted path."""
    import copy
    r = copy.deepcopy(recipe)
    if override:
        r.setdefault("params", {}).update(override)
    try:
        out = run_recipe(r)
    except Exception:
        return None
    # `provenance` restates the pack's own parameter values, so perturbing a
    # constant always changes it — that is the input echoing back, not a
    # prediction responding, and counting it would mark everything live.
    out = {k: v for k, v in out.items() if k != "provenance"}
    got = _numeric_leaves(out)
    return got or None


def _max_relative_change(base: Dict[str, float],
                         alt: Dict[str, float]) -> float:
    """Largest relative change (%) over the shared outputs.

    A denominator of zero is not a division error but a real transition -- an
    output going from exactly 0 to non-zero is the strongest possible response
    -- so it is reported as a full-scale change rather than skipped.
    """
    worst = 0.0
    for key, b in base.items():
        a = alt.get(key)
        if a is None:
            continue
        if abs(b) < 1e-12:
            worst = max(worst, 0.0 if abs(a) < 1e-12 else 100.0)
        else:
            worst = max(worst, abs(a - b) / abs(b) * 100.0)
    return worst


def _perturbed(value: float) -> float:
    return ZERO_PERTURB if abs(value) < 1e-12 else value * PERTURB_FACTOR


def _scan_pack(pack_name: str) -> List[dict]:
    film = PACK_FILM[pack_name]
    pack = load_pack(pack_name)
    grid = _grid(pack_name, film)
    baseline = [_response(g) for g in grid]
    live_points = [i for i, b in enumerate(baseline) if b]
    rows: List[dict] = []
    for key, param in pack.params.items():
        value = param.value
        if not isinstance(value, (int, float)) or isinstance(value, bool):
            continue
        alt = _perturbed(float(value))
        deltas: List[float] = []
        for i in live_points:
            ref = baseline[i]
            got = _response(grid[i], {key: alt})
            if got is None or not ref:
                continue
            deltas.append(_max_relative_change(ref, got))
        if not deltas:
            continue
        moved = sum(1 for d in deltas if d > DEAD_TOLERANCE)
        max_d = max(deltas)
        if max_d <= DEAD_TOLERANCE:
            verdict = "dead"
        elif moved <= max(1, int(NARROW_FRACTION * len(deltas))):
            verdict = "narrow"
        else:
            verdict = "live"
        rows.append({
            "pack": pack_name, "key": key, "value": value,
            "confidence": str(param.confidence),
            "source": str(getattr(param, "source", ""))[:70],
            "max_delta_pct": round(max_d, 4),
            "points_moved": moved, "points": len(deltas),
            "verdict": verdict,
        })
    return rows


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pack", action="append", default=None)
    ap.add_argument("--jobs", type=int, default=max(1, (os.cpu_count() or 2) - 1))
    ap.add_argument("--show", default="dead,narrow",
                    help="comma-separated verdicts to print in full")
    args = ap.parse_args()

    packs = args.pack or sorted(PACK_FILM)
    rows: List[dict] = []
    if args.jobs > 1 and len(packs) > 1:
        with ProcessPoolExecutor(max_workers=args.jobs) as pool:
            for got in pool.map(_scan_pack, packs):
                rows.extend(got)
    else:
        for p in packs:
            rows.extend(_scan_pack(p))

    show = {s.strip() for s in args.show.split(",") if s.strip()}
    counts: Dict[str, int] = {}
    for r in rows:
        counts[r["verdict"]] = counts.get(r["verdict"], 0) + 1
    print(f"{'pack':28s} {'key':38s} {'value':>10s} {'conf':>11s} "
          f"{'maxd%':>9s} {'moved':>7s} verdict")
    for r in sorted(rows, key=lambda r: (r["verdict"], r["pack"], r["key"])):
        if r["verdict"] not in show:
            continue
        print(f"{r['pack'][:28]:28s} {r['key'][:38]:38s} "
              f"{r['value']:10.4g} {r['confidence'][:11]:>11s} "
              f"{r['max_delta_pct']:9.3f} "
              f"{r['points_moved']:3d}/{r['points']:<3d} {r['verdict']}")
    print()
    print("counts:", ", ".join(f"{k}={v}" for k, v in sorted(counts.items())),
          f"(total {len(rows)} numeric constants over {len(packs)} packs)")
    print(f"dead = no admissible query moves the rate by >{DEAD_TOLERANCE}%; "
          "see module docstring before withdrawing any of them.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
