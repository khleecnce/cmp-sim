"""Is the LOAD-SHARING axis (chi) decided, and does its value reach the rate?

Why this exists
---------------
``legacy/sim/abrasive_mechanics.decide_chi`` is the FIRST of the three regime
questions behind the Luo-Dornfeld exponent decomposition::

    n_C = p * (1 - alpha*chi)
    n_d = -q * (1 - alpha*chi) + beta

The 28th run closed the third question (supply: p, q) from the lubrication
regime, at zero constants, and STATUS.md named chi as "the only remaining
undecided axis" because every scored run reports
``abrasive_regime.confidence == 'unverified'``.

``decide_chi`` takes one input: ``m``, the pressure exponent of the REAL
contact area, ``A_r ~ P^m``. ``solver._abrasive_hook`` obtains it by numerically
differentiating the GW contact layer between ``P/2`` and ``2P``; if that raises,
``m`` becomes ``None`` and ``decide_chi`` falls back to ``chi = 1.0`` graded
``unverified``.

**Nobody has ever measured how often that fallback fires** — which is the same
omission that hid the supply axis for the whole life of the corpus. This probe
measures it, and then measures the two things that decide whether the axis is
worth any further work:

1. **Is it decided?** For every scored dataset's first row, recompute ``m``
   exactly as the solver does and record success/failure.
2. **What value does it take?** If the GW derivative always returns the same
   number, chi is not an axis at all — it is a constant with a derivation.
3. **Does chi REACH the rate?** Perturb chi (0.5 and 0.0 against the resolved
   value), re-run the shipping solver, and record the rate change. An axis
   that cannot move the prediction cannot be responsible for any part of the
   corpus error, no matter how undetermined its grade looks.

Question 3 is the one that matters and it is asked LAST on purpose: the same
mistake was made twice in this repo (lambda = V/p, summit saturation = P) of
adopting a diagnostic that turned out to be the operating point in disguise.
An exponent that is analytically pinned to 1.0000 by the GW summit
distribution is a fourth instance of that trap: it would grade the axis
"decided from data" while carrying no information from any measurement.

MEASUREMENT ONLY. This script fits nothing and edits no pack.

Usage: ``PYTHONPATH=. .venv/bin/python tools/chi_reachability_probe.py``
"""
from __future__ import annotations

import statistics
from typing import Any, Dict, List, Optional

import numpy as np
import yaml

from cmp_sim.core.predictive_score import _recipe_for
from cmp_sim.core.validation import dataset_paths

#: chi values forced in the perturbation test. 1.0 is full load sharing
#: (the fallback), 0.0 is asperity-carried load: the widest possible swing.
CHI_PROBES = (0.5, 0.0)


def _area_exponent(rr) -> Optional[float]:
    """Recompute m exactly as ``solver._abrasive_hook`` does."""
    from cmp_sim.pad.material import pad_state
    try:
        state, _n, _w = pad_state(rr.recipe.pad, rr)
        p_lo, p_hi = 0.5 * rr.pressure_pa, 2.0 * rr.pressure_pa
        a_lo = state.real_area_fraction(p_lo)
        a_hi = state.real_area_fraction(p_hi)
        return float(np.log(a_hi / a_lo) / np.log(p_hi / p_lo))
    except Exception as exc:                                  # pragma: no cover
        return None


def _row_report(path) -> Optional[Dict[str, Any]]:
    doc = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    conditions = doc.get("conditions") or []
    if not conditions:
        return None
    from cmp_sim.api import recipe_from_dict, run_recipe
    from cmp_sim.core.solver import resolve as resolve_recipe

    recipe = _recipe_for(doc, conditions[0])
    out: Dict[str, Any] = {"dataset": path.stem}
    try:
        result = run_recipe(recipe)
    except Exception as exc:                                  # pragma: no cover
        return {"dataset": path.stem, "error": str(exc)[:70]}
    regime = result.get("abrasive_regime") or {}
    out.update(
        chi=regime.get("chi"),
        alpha=regime.get("alpha"),
        n_conc=regime.get("n_conc"),
        confidence=regime.get("confidence"),
        rate=result.get("removal_rate_A_per_min"),
    )
    try:
        rr = resolve_recipe(recipe_from_dict(recipe))
        out["m"] = _area_exponent(rr)
    except Exception:                                         # pragma: no cover
        out["m"] = None

    # ── does chi reach the rate? ──────────────────────────────────────
    # Patch the regime resolver the solver calls, forcing chi while leaving
    # everything else (alpha, beta, p, q and their derived exponents) to be
    # recomputed from it, which is what a genuine change in load sharing means.
    import dataclasses
    from cmp_sim.models import luo_dornfeld as ld

    base_resolve = ld.resolve_regime
    moves: Dict[float, Optional[float]] = {}
    for chi_forced in CHI_PROBES:
        def patched(_chi=chi_forced, **kwargs):
            reg = base_resolve(**kwargs)
            n_conc = reg.p * (1.0 - reg.alpha * _chi)
            n_size = -reg.q * (1.0 - reg.alpha * _chi) + reg.beta
            return dataclasses.replace(reg, chi=_chi, n_conc=n_conc,
                                       n_size=n_size)
        ld.resolve_regime = patched
        try:
            forced = run_recipe(recipe).get("removal_rate_A_per_min")
        except Exception:                                     # pragma: no cover
            forced = None
        finally:
            ld.resolve_regime = base_resolve
        base_rate = out.get("rate")
        if forced and base_rate:
            moves[chi_forced] = abs(float(forced) / float(base_rate) - 1.0) * 100.0
        else:
            moves[chi_forced] = None
    out["moves"] = moves
    return out


def collect() -> List[Dict[str, Any]]:
    rows = []
    for path in dataset_paths():
        row = _row_report(path)
        if row is not None:
            rows.append(row)
    return rows


#: below this a forced chi swing is indistinguishable from float noise
INERT_PCT = 0.5


def report(rows: List[Dict[str, Any]]) -> str:
    lines = [f"{'dataset':44s} {'m':>8s} {'chi':>6s} {'alpha':>6s} "
             f"{'n_C':>7s} {'d%@0.5':>8s} {'d%@0.0':>8s}  confidence"]
    lines.append("-" * 104)
    ms: List[float] = []
    no_m = 0
    inert = 0
    live = 0
    for r in sorted(rows, key=lambda x: x["dataset"]):
        if r.get("error"):
            lines.append(f"{r['dataset'][:42]:44s} ERROR: {r['error']}")
            continue
        m = r.get("m")
        if m is None:
            no_m += 1
        else:
            ms.append(m)
        mv = r.get("moves") or {}
        biggest = max((v for v in mv.values() if v is not None), default=None)
        if biggest is not None:
            if biggest < INERT_PCT:
                inert += 1
            else:
                live += 1
        fmt = lambda v, n=3: ("—" if v is None else f"{float(v):.{n}f}")
        lines.append(
            f"{r['dataset'][:42]:44s} {fmt(m, 4):>8s} {fmt(r.get('chi'), 2):>6s} "
            f"{fmt(r.get('alpha'), 2):>6s} {fmt(r.get('n_conc')):>7s} "
            f"{fmt(mv.get(0.5), 2):>8s} {fmt(mv.get(0.0), 2):>8s}  "
            f"{r.get('confidence') or '—'}")
    lines.append("")
    if ms:
        lines.append(
            f"m solved on {len(ms)} runs, unsolved on {no_m}; "
            f"median {statistics.median(ms):.4f}, "
            f"range {min(ms):.4f}..{max(ms):.4f}, "
            f"spread {max(ms) - min(ms):.2e}")
        if max(ms) - min(ms) < 1e-6:
            lines.append(
                "=> m is CONSTANT across the corpus. chi is then not an axis "
                "that data can move: it is a fixed consequence of the GW "
                "summit height distribution, and grading it 'measured' would "
                "dress a structural constant as an observation.")
    lines.append(f"forced-chi response: {live} datasets move >= {INERT_PCT}%, "
                 f"{inert} are inert")
    if live == 0:
        lines.append(
            "=> chi does NOT reach the rate on any scored run. Whatever its "
            "grade, it cannot own any part of the corpus error, and deciding "
            "it would change the confidence string and nothing else.")
    return "\n".join(lines)


if __name__ == "__main__":
    print(report(collect()))
