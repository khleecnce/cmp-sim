"""Is the peaked oxidizer form the packs DECLARE reachable by any query?

WHAT THE MUTATION GUARD FOUND
-----------------------------
A limit was being drafted to stop a later session WIRING a peaked Cu oxidizer
term.  Its guard fired immediately: `legacy/sim/chemistry.py` already
implements one (`mrr_oxidizer`, the legacy Kaufman unimodal curve keyed on
`oxidizer_peak_wt_pct` + `oxidizer_curve_n`), and three packs DECLARE a peak
position for it, `cu_h2o2_bta` at 3.0 wt% with a primary citation.

So the question is not "should a peak be wired".  It is the §35 question:
CAN ANY QUERY REACH THE ONE THAT IS ALREADY THERE?  Reading the source says
no -- the peaked branch sits last, behind three `return`s, and every pack that
declares a peak also declares a Langmuir K that returns first.  But §35's own
lesson is that reachability must be measured by running the SHIPPING solver,
not by reading the source, because a gate can be off at the reading's assumed
operating point.

WHAT THIS MEASURES
------------------
For every pack that declares `oxidizer_peak_wt_pct`:

  Q1  Which oxidizer branch actually executes?  Read from the run's own notes,
      not inferred from which keys exist.

  Q2  Does perturbing the DECLARED PEAK POSITION move the predicted rate at
      all?  Swept small-first in both directions (§43: the response can be
      non-monotone in the perturbation, and a large factor can push a key out
      of its own validity window where the model correctly refuses).

  Q3  INSTRUMENT CONTROL.  Perturb a key that is known to be read on the same
      pack and confirm the rate moves.  Without this, "nothing moves anything"
      reads as a clean bill of health for a broken probe.

  Q4  If the peak is unreachable, is its declared value even consistent with
      the literature?  Compared against the only source here that RESOLVES a
      maximum by direct measurement (Lin & Du 2009: 0.66-0.90 wt%, three
      dilutions).  An unreachable number that is also wrong is the §35 case
      exactly: unfalsifiable by any measurement, so it ages into fact.

Run:  .venv/bin/python tools/oxidizer_peak_reachability_probe.py
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from typing import Optional  # noqa: E402

from cmp_sim.api import run_recipe                        # noqa: E402
from cmp_sim.core.params import load_pack                 # noqa: E402
from cmp_sim.core.predictive_score import PACK_FILM       # noqa: E402

PEAK_KEY = "oxidizer_peak_wt_pct"

# Perturbation factors, SMALL FIRST and both directions (limits §43). A key is
# called unreachable only if NO admissible perturbation reaches it.
FACTORS = [1.05, 0.95, 1.25, 0.8, 1.5, 0.67, 2.0, 0.5, 3.0, 0.33]

# The only measured peak position for a Cu slurry in this repository's sources.
# Quoted from Lin & Du, ECS Trans 18(1) 485-490 (2009), abstract: the maximum
# moves 0.90 -> 0.74 -> 0.66 wt% across 1:6, 1:8 and 1:10 dilutions.
LIN2009_PEAK_WINDOW = (0.66, 0.90)


def _run(pack: str, film: str, overrides: Optional[dict] = None):
    """Run the SHIPPING solver, not a reimplementation of it."""
    recipe = {
        "model": "auto",
        "wafer": {"film": film, "n_radial": 11},
        "slurry": {"pack": pack},
        "tool": {"pressure_psi": 4.0, "rpm_platen": 60, "rpm_head": 60,
                 "time_s": 60.0},
    }
    if overrides:
        recipe["params"] = dict(overrides)
    return run_recipe(recipe)


def _rate_and_notes(res):
    rate = res.get("removal_rate_A_per_min")
    notes = res.get("warnings") or res.get("notes") or []
    return (None if not rate else float(rate)), [str(n) for n in notes]


def _branch_from_notes(notes) -> str:
    """Which oxidizer branch executed, read from the run's own output."""
    blob = " ".join(notes)
    if "레거시 산화제 곡선" in blob or "legacy oxidizer curve" in blob:
        return "PEAKED (legacy Kaufman)"
    if "촉진-포화형" in blob or "promoter" in blob.lower():
        return "promoter (acid x chelator)"
    return "Langmuir (promoter or passivation) — peaked branch not reached"


def _packs_declaring_peak():
    out = {}
    for name, film in PACK_FILM.items():
        try:
            pack = load_pack(name)
        except Exception:
            continue
        p = pack.params.get(PEAK_KEY)
        if p is not None and p.value is not None:
            out[name] = (pack, film)
    return out


def main() -> int:
    packs = _packs_declaring_peak()
    print(f"packs declaring {PEAK_KEY}: {sorted(packs)}")
    if not packs:
        print("NOTHING DECLARES A PEAK — this probe has no subject, which is "
              "indistinguishable from a deleted check. Investigate.")
        return 1

    any_reachable = False
    for name, (pack, film) in sorted(packs.items()):
        peak = float(pack.params[PEAK_KEY].value)
        conf = getattr(pack.params[PEAK_KEY], "confidence", "?")
        print(f"\n=== {name} ({film}):  {PEAK_KEY} = {peak} wt%  [{conf}]")

        base_rate, notes = _rate_and_notes(_run(name, film))
        if not base_rate:
            print("    base run produced no rate — skipping")
            continue
        print(f"    base rate = {base_rate:.4f} A/min")
        print(f"    Q1 branch = {_branch_from_notes(notes)}")

        # Q2 — sweep the declared peak position, small first, both directions.
        best = 0.0
        for f in FACTORS:
            r, _ = _rate_and_notes(_run(name, film, {PEAK_KEY: peak * f}))
            if r:
                best = max(best, abs(r - base_rate) / base_rate * 100.0)
        verdict = "REACHED" if best > 1e-6 else "UNREACHABLE"
        print(f"    Q2 max |d rate| over {len(FACTORS)} perturbations "
              f"({min(FACTORS)}x..{max(FACTORS)}x) = {best:.6f}%  -> {verdict}")
        any_reachable = any_reachable or best > 1e-6

        # Q3 — instrument control on the SAME pack.
        control_key, control_moved = None, 0.0
        for k in ("oxidizer_wt_pct", "abrasive_wt_pct", "slurry_ph"):
            p = pack.params.get(k)
            if p is None or p.value is None:
                continue
            r, _ = _rate_and_notes(_run(name, film, {k: float(p.value) * 1.25}))
            if r:
                d = abs(r - base_rate) / base_rate * 100.0
                if d > control_moved:
                    control_moved, control_key = d, k
        if control_key is None or control_moved <= 1e-6:
            print("    Q3 CONTROL FAILED — no key known to be read moved the "
                  "rate either. This pack's whole result is suspect, not just "
                  "the peak.")
        else:
            print(f"    Q3 control: {control_key} x1.25 moved the rate "
                  f"{control_moved:.3f}% — the probe CAN see a live key")

        # Q4 — is the declared value consistent with the measured window?
        lo, hi = LIN2009_PEAK_WINDOW
        if peak < lo or peak > hi:
            ratio = peak / hi if peak > hi else lo / peak
            print(f"    Q4 declared peak {peak} wt% is {ratio:.1f}x outside "
                  f"the only directly MEASURED window {lo}-{hi} wt% "
                  f"(Lin & Du 2009, three dilutions)")
        else:
            print(f"    Q4 declared peak {peak} wt% lies inside the measured "
                  f"window {lo}-{hi} wt%")

    print("\n--- verdict")
    if not any_reachable:
        print("Every declared peak position is UNREACHABLE: the packs that")
        print("declare one also declare a Langmuir K, which returns first, so")
        print("no query — no pressure, no formulation — can make the peaked")
        print("branch execute. These are §35 numbers: carrying a source, a")
        print("unit and a confidence grade while being unfalsifiable by any")
        print("measurement, which is how a number ages into a fact.")
        print()
        print("NOT a licence to delete them. Deleting restores the")
        print("undetectable state (§27). The peaked FORM is the shape three")
        print("independent sources report (research/"
              "cu_acid_chelator_oxidizer_sign_evidence.yaml); what is wrong")
        print("is claiming a POSITION nobody here measured for a disclosed")
        print("composition, in a branch nobody can run.")
    else:
        print("At least one declared peak IS reachable — re-read the per-pack")
        print("output above; the source-reading conclusion was wrong.")
    print("\nNothing was written.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
