"""Can contact-area evolution or flash heating produce the measured P-V coupling?

WHY THIS SCRIPT EXISTS
----------------------
The 9th run closed the search for a velocity EXPONENT
(``tools/velocity_pressure_interaction_probe.py``): b_V in MRR ~ P * V**b_V is
not a constant, and it is not a single function b_V(P) either, because the sign
of db_V/dP inverts between consumable sets:

    Sorooshian 2005  thermal oxide / fumed silica  2/4/6 psi   +0.370 +0.687 +0.764   UP
    mariscal2020     PETEOS / ceria                2/3/4 psi   +1.105 +0.857 +0.625   DOWN
    us6918821b2      Cu / IC1000                   1.5/4 psi   -0.416        +0.863   UP, sign change
    Borucki 2023     Cu (published)                1/1.5/2 psi -0.810 -0.620 +0.330   UP, sign change

STATUS.md's NEXT then named two candidate mechanisms and required that their
SIGN be derived from parameters already in the repository and checked against
those four bodies BEFORE any pack is touched. That is what this script does.
Nothing is fitted; no pack is modified.

THE TWO CANDIDATES, AND WHAT EACH PREDICTS WITH ZERO NEW CONSTANTS
------------------------------------------------------------------
(A) Contact-area evolution (``cmp_sim/models/contact_gw.py``).
    The hope recorded in NEXT: "if A_r grows sub-linearly in P while the
    per-asperity sliding distance grows linearly in V, the effective velocity
    exponent acquires a P dependence with NO new constant."

    Two independent checks are run, because the hope has a structural problem
    and a quantitative one:

    A1 STRUCTURE. Removal proportional to real contact area times sliding
       speed is MRR = c * A_r(P) * V. Then

           d ln MRR / d ln V = 1   exactly, for every P,

       because A_r is a quasi-static elastic response to the NORMAL load and
       contains no V at all. Sub-linearity in A_r(P) moves the PRESSURE
       exponent; it cannot move the VELOCITY exponent. So the mechanism is
       structurally incapable of producing db_V/dP != 0, whatever its
       parameters. This is stated first because it is decisive on its own.

    A2 MAGNITUDE. Even granting a coupling, the sub-linearity has to exist.
       For exponential summit heights GW gives A_r strictly proportional to
       load while contact is confined to the distribution's tail, and it bends
       only as summits run out. So measure d ln A_r / d ln P on the ACTUAL
       reference pad of each body's pack, at that body's own pressures, and
       report the summit saturation alongside it.

(B) Pad-asperity flash heating.
    Contact temperature rises with frictional power, T = T0 + c * P * V
    (c > 0), and an Arrhenius chemical term gives

        MRR ~ P * V * exp(-Ea / (R * (T0 + c*P*V)))
        => b_V = 1 + (Ea/R) * c*P*V / (T0 + c*P*V)**2

    For any Ea > 0 and c > 0 the second term is strictly POSITIVE, so

        b_V > 1 ALWAYS,  and  db_V/dP > 0 while c*P*V < T0.

    That is a zero-constant sign prediction: no value of Ea or c is needed to
    test it. It is a different claim from the one the 8th run rejected (heating
    as a pure VELOCITY law, residual slope -0.549), so the earlier rejection is
    not reused here.

PRE-REGISTERED DECISION RULES (fixed before running)
----------------------------------------------------
A passes only if it produces |d ln A_r/d ln P - 1| >= 0.05 at some body's
    pressures. Below that there is no sub-linearity to donate even if the
    structural objection A1 were wrong.
B passes only if it can produce b_V < 1 somewhere, since two of the four
    bodies measure b_V below 1 at every pressure.
If both fail, the P-V interaction axis is CLOSED the way the pH axis is
    closed, and the closure must be priced: part C measures what the axis costs
    the corpus median, which is the number STATUS.md's completion criterion
    demands ("what sets the lower bound on the error").

(C) THE PRICE OF THE AXIS — an explicit in-sample UPPER bound.
    Give every dataset its own measured per-pressure velocity exponent as a
    post-hoc correction: multiply the prediction by (V / V_group)**(b_V - 1),
    where b_V is the raw log-log slope of MEASURED rate against speed within
    that (pressure, chemistry) group. The correction uses no model residual, but
    b_V still comes from the same rows being scored, so the result is an ORACLE:
    an upper bound on what any P-V law could buy, not an achievable score. It is
    reported as such, and it is the honest input to "is <= 10% reachable?".

Run: python tools/pv_interaction_closure.py
"""
from __future__ import annotations

import math
import statistics
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

import yaml

from cmp_sim.core.params import load_pack
from cmp_sim.core.predictive_score import _measured
from cmp_sim.core.validation import dataset_paths

from tools.velocity_pressure_interaction_probe import (  # reuse, do not re-derive
    MIN_VELOCITY_LEVELS,
    _condition_key,
    _geo,
    _slope,
    _speed,
)

HERE = Path(__file__).resolve().parents[1]

PSI_PA = 6894.757

#: Pre-registered bars. See the module docstring.
SUBLINEARITY_BAR = 0.05          # |dlnA_r/dlnP - 1| must reach this for (A)
ORACLE_GAIN_BAR_PP = 2.0         # percentage points; below this the axis is cheap

#: The four measured bodies, from tools/velocity_pressure_interaction_probe.py
#: and Borucki & Philipossian ECS JSS 12 (2023) 043003.
#: (label, pack used for the pad, [(psi, b_V), ...], representative speed m/s)
MEASURED_BODIES: List[Tuple[str, str, List[Tuple[float, float]], float]] = [
    ("Sorooshian 2005 thermal oxide / fumed silica", "oxide_silica",
     [(2.0, +0.370), (4.0, +0.687), (6.0, +0.764)], 0.554),
    ("mariscal2020 PETEOS / ceria", "sti_ceria",
     [(2.0, +1.105), (3.0, +0.857), (4.0, +0.625)], 1.15),
    ("us6918821b2 Cu / IC1000", "cu_h2o2_bta",
     [(1.5, -0.416), (4.0, +0.863)], 1.0),
    ("Borucki 2023 Cu (published)", "cu_h2o2_bta",
     [(1.0, -0.810), (1.5, -0.620), (2.0, +0.330)], 1.0),
]


# --------------------------------------------------------------------------
# (A) contact-area evolution
# --------------------------------------------------------------------------
@dataclass
class ContactSlope:
    pack: str
    psi: float
    dln_ar_dln_p: float
    saturation: float


class _PackOnly:
    """Minimal stand-in for ResolvedRecipe, exposing only ``p(key)``.

    ``pad.material.reference_pad_state`` needs nothing but the pack lookup, and
    building a full Recipe would drag in a wafer, a tool and a slurry that this
    measurement does not use -- inventing conditions in order to read a pad
    property is exactly the kind of silent assumption this probe must avoid.
    """

    def __init__(self, pack_name: str) -> None:
        self.pack = load_pack(pack_name)

    def p(self, key: str) -> Any:
        return self.pack.get(key)


def contact_area_exponents() -> List[ContactSlope]:
    """d ln A_r / d ln P on each body's own reference pad, at its own pressures.

    Uses the pack's reference pad state, i.e. the pad whose properties the
    pack's Kp was calibrated with, so the numbers are the ones the simulator
    actually runs on rather than a generic illustration.
    """
    out: List[ContactSlope] = []
    seen: set = set()
    for _label, pack_name, levels, _v in MEASURED_BODIES:
        for psi, _b in levels:
            if (pack_name, psi) in seen:
                continue
            seen.add((pack_name, psi))
            state = _reference_pad(pack_name)
            if state is None:
                continue
            p_pa = psi * PSI_PA
            # central difference in log space; +-5% is small enough that the
            # slope is local and large enough to stay clear of solver noise
            lo, hi = p_pa * 0.95, p_pa * 1.05
            try:
                a_lo = state.contact_state(lo)["A_r"]
                a_hi = state.contact_state(hi)["A_r"]
                sat = state.saturation(p_pa)
            except Exception:                              # noqa: BLE001
                continue
            slope = (math.log(a_hi) - math.log(a_lo)) / (math.log(hi) - math.log(lo))
            out.append(ContactSlope(pack_name, psi, slope, sat))
    return out


def _reference_pad(pack_name: str):
    """PadContactState of ``pack_name``'s reference pad, or None if it has none."""
    from cmp_sim.pad import material as pad_material
    try:
        return pad_material.reference_pad_state(_PackOnly(pack_name))
    except Exception:                                      # noqa: BLE001
        return None


# --------------------------------------------------------------------------
# (B) flash heating cross term
# --------------------------------------------------------------------------
def flash_heating_bv(psi: float, v_m_s: float, ea_j_mol: float,
                     c_k_per_w: float, t0_k: float = 298.15) -> float:
    """b_V predicted by MRR ~ P*V*exp(-Ea/(R*(T0 + c*P*V))).

    Derivation (also in the module docstring):
        ln MRR = ln P + ln V - Ea/(R*(T0 + c*P*V))
        d/d ln V  =>  b_V = 1 + (Ea/R) * c*P*V / (T0 + c*P*V)**2
    The SIGN of the correction does not depend on Ea or c, only on their being
    positive, which is what makes this a zero-constant test.
    """
    r_gas = 8.314462618
    u = c_k_per_w * psi * PSI_PA * v_m_s        # temperature rise [K]
    return 1.0 + (ea_j_mol / r_gas) * u / (t0_k + u) ** 2


def flash_heating_is_capable_of_sub_linear() -> bool:
    """Can ANY positive (Ea, c) put b_V below 1? Scanned, not asserted.

    Spans six decades in the heating coefficient and 10-200 kJ/mol in Ea, i.e.
    every physically sensible CMP surface reaction.
    """
    for ea in (10e3, 40e3, 80e3, 200e3):
        for c in (1e-9, 1e-7, 1e-5, 1e-3, 1e-1):
            for psi, v in ((1.0, 0.3), (4.0, 1.0), (6.0, 2.0)):
                if flash_heating_bv(psi, v, ea, c) < 1.0:
                    return True
    return False


# --------------------------------------------------------------------------
# (C) the price of the axis
# --------------------------------------------------------------------------
def _run(doc: Dict[str, Any], row: Dict[str, Any]) -> Optional[float]:
    from cmp_sim.core.predictive_score import _predict
    return _predict(doc, row)


@dataclass
class OracleScore:
    dataset: str
    n_points: int
    baseline_pct: float
    oracle_pct: float

    @property
    def gain_pp(self) -> float:
        return self.baseline_pct - self.oracle_pct


def oracle_scores() -> List[OracleScore]:
    """Per-dataset shape error with and without each group's MEASURED b_V.

    The correction is applied only inside (pressure, chemistry) groups holding
    >= MIN_VELOCITY_LEVELS speeds, because a slope through two points is read
    noise. Rows outside such a group are scored unchanged, so a dataset that
    never sweeps speed appears with gain 0.0 rather than being dropped -- the
    corpus median must be computed over the SAME datasets in both columns, or
    the comparison silently changes its population.
    """
    out: List[OracleScore] = []
    for path in dataset_paths():
        doc = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
        rows = [r for r in (doc.get("conditions") or [])
                if _measured(r) is not None]
        if len(rows) < 2:
            continue

        # measured per-group velocity exponents
        groups: Dict[tuple, List[Tuple[float, float]]] = defaultdict(list)
        for row in rows:
            speed = _speed(row)
            if speed is None or not row.get("pressure_psi"):
                continue
            key = (float(row["pressure_psi"]), _condition_key(row, ()))
            groups[key].append((speed, float(_measured(row))))  # type: ignore[arg-type]

        exponent: Dict[tuple, Tuple[float, float]] = {}
        for key, pts in groups.items():
            merged: Dict[float, List[float]] = defaultdict(list)
            for v, r in pts:
                merged[v].append(r)
            levels = [(v, _geo(rs)) for v, rs in sorted(merged.items())]
            if len(levels) < MIN_VELOCITY_LEVELS:
                continue
            slope = _slope([math.log(v) for v, _ in levels],
                           [math.log(r) for _, r in levels])
            if slope is None:
                continue
            exponent[key] = (slope, _geo([v for v, _ in levels]))

        measured: List[float] = []
        base: List[float] = []
        oracle: List[float] = []
        ok = True
        for row in rows:
            value = _run(doc, row)
            if value is None:
                ok = False
                break
            measured.append(float(_measured(row)))          # type: ignore[arg-type]
            base.append(value)
            speed = _speed(row)
            key = ((float(row["pressure_psi"]), _condition_key(row, ()))
                   if speed is not None and row.get("pressure_psi") else None)
            if key in exponent and speed:
                b_v, v_ref = exponent[key]
                oracle.append(value * (speed / v_ref) ** (b_v - 1.0))
            else:
                oracle.append(value)
        if not ok or len(measured) < 2:
            continue
        out.append(OracleScore(
            dataset=Path(path).stem, n_points=len(measured),
            baseline_pct=_scaled_median_error(measured, base),
            oracle_pct=_scaled_median_error(measured, oracle)))
    return out


def _scaled_median_error(measured: Sequence[float],
                         predicted: Sequence[float]) -> float:
    """Median |error| after one free multiplicative scale (the shape metric)."""
    den = sum(p * p for p in predicted)
    scale = (sum(m * p for m, p in zip(measured, predicted)) / den) if den else 1.0
    return statistics.median(abs(scale * p - m) / m * 100.0
                             for m, p in zip(measured, predicted) if m)


# --------------------------------------------------------------------------
# report
# --------------------------------------------------------------------------
def report() -> str:
    lines = ["P-V INTERACTION: CAN EITHER CANDIDATE MECHANISM PRODUCE IT?",
             "Measured target: db_V/dP inverts between consumable sets, and two "
             "bodies sit BELOW b_V = 1 at every pressure.",
             ""]

    # ---- (A) -------------------------------------------------------------
    lines.append("(A) CONTACT-AREA EVOLUTION (cmp_sim/models/contact_gw.py)")
    lines.append("  A1 structure: MRR = c * A_r(P) * V has d ln MRR/d ln V = 1 "
                 "for every P.")
    lines.append("     A_r is a quasi-static response to the NORMAL load and "
                 "contains no V,")
    lines.append("     so contact-area evolution moves the PRESSURE exponent, "
                 "never the velocity one.")
    slopes = contact_area_exponents()
    lines.append("  A2 magnitude: d ln A_r / d ln P on each pack's own "
                 "reference pad")
    worst = 0.0
    if not slopes:
        lines.append("     (no pack exposed a reference pad state - cannot "
                     "measure)")
    for s in slopes:
        dev = abs(s.dln_ar_dln_p - 1.0)
        worst = max(worst, dev)
        lines.append(f"     {s.pack:22s} {s.psi:>4.1f} psi  "
                     f"dlnA_r/dlnP = {s.dln_ar_dln_p:.4f}  "
                     f"(|dev| {dev:.4f})  summit saturation "
                     f"{100.0 * s.saturation:.2f}%")
    lines.append(f"     worst sub-linearity {worst:.4f} vs bar "
                 f"{SUBLINEARITY_BAR:.2f}  -> "
                 f"{'PASSES' if worst >= SUBLINEARITY_BAR else 'FAILS'}")
    distinct = {(round(s.dln_ar_dln_p, 6), round(s.saturation / s.psi, 9))
                for s in slopes}
    if slopes and len(distinct) == 1:
        lines.append("     HONESTY: every pack above resolves to the SAME "
                     "inherited base pad, so these")
        lines.append("     rows are ONE pad measured at several pressures, not "
                     "three independent pads.")
        lines.append("     The exact 1.0000 is not a coincidence either: it is "
                     "GW's analytic result for")
        lines.append("     exponential summit heights (A_r strictly "
                     "proportional to load, memoryless tail),")
        lines.append("     which holds until the summits run out. Saturation is "
                     "1-5% here, i.e. the model")
        lines.append("     is deep inside the linear regime, so the "
                     "sub-linearity the mechanism needs")
        lines.append("     does not exist AT THESE PRESSURES for ANY pad "
                     "described this way. A pad whose")
        lines.append("     measured summit heights were NOT exponential could "
                     "bend A_r(P) -- that is a")
        lines.append("     different, data-limited question, and A1 would still "
                     "rule out the b_V effect.")
    lines.append("")

    # ---- (B) -------------------------------------------------------------
    lines.append("(B) PAD-ASPERITY FLASH HEATING (Arrhenius on T = T0 + c*P*V)")
    lines.append("  b_V = 1 + (Ea/R) * c*P*V / (T0 + c*P*V)**2  > 1 for any "
                 "Ea > 0, c > 0")
    capable = flash_heating_is_capable_of_sub_linear()
    for ea, c in ((40e3, 1e-7), (80e3, 1e-6)):
        vals = ", ".join(f"{psi:g} psi: {flash_heating_bv(psi, 1.0, ea, c):+.3f}"
                         for psi in (1.0, 2.0, 4.0, 6.0))
        lines.append(f"     Ea={ea/1e3:.0f} kJ/mol, c={c:g} K/W: {vals}")
    lines.append(f"     can any (Ea>0, c>0) give b_V < 1? "
                 f"{'YES' if capable else 'NO'}  -> "
                 f"{'PASSES' if capable else 'FAILS'} "
                 "(two bodies measure b_V < 1 at every pressure)")
    lines.append("     NOTE: this is the CROSS-TERM claim. The 8th run rejected "
                 "heating as a pure")
    lines.append("     velocity law (residual slope -0.549); that rejection is "
                 "not reused here.")
    lines.append("")

    # ---- (C) -------------------------------------------------------------
    scores = oracle_scores()
    lines.append("(C) PRICE OF THE AXIS - in-sample ORACLE upper bound")
    lines.append("    Each (pressure, chemistry) group keeps its own MEASURED "
                 "b_V; one free scale per dataset.")
    movers = sorted((s for s in scores if abs(s.gain_pp) > 0.05),
                    key=lambda s: -s.gain_pp)
    for s in movers:
        lines.append(f"     {s.dataset:52s} n={s.n_points:<3d} "
                     f"{s.baseline_pct:6.2f}% -> {s.oracle_pct:6.2f}%  "
                     f"({s.gain_pp:+.2f} pp)")
    if scores:
        base_med = statistics.median(s.baseline_pct for s in scores)
        orc_med = statistics.median(s.oracle_pct for s in scores)
        total_pts = sum(s.n_points for s in scores)
        moved_pts = sum(s.n_points for s in movers)
        lines.append(f"     corpus median over the SAME {len(scores)} datasets: "
                     f"{base_med:.2f}% -> {orc_med:.2f}%  "
                     f"({base_med - orc_med:+.2f} pp)")
        lines.append(f"     datasets whose score moves at all: {len(movers)} "
                     f"of {len(scores)}")
        lines.append(f"     MEASURED POINTS the axis can reach: {moved_pts} of "
                     f"{total_pts} ({100.0 * moved_pts / total_pts:.1f}%)")
        lines.append("     ^ read this before the median. A median over 49 "
                     "datasets is set by whichever")
        lines.append("       dataset sits at rank 25, so improving 3 datasets "
                     "can move it by re-ranking")
        lines.append("       rather than by explaining anything. The point share "
                     "is the honest size of")
        lines.append("       the axis; the median shift is its most flattering "
                     "presentation.")
        lines.append(f"     bar: a gain below {ORACLE_GAIN_BAR_PP:.1f} pp means "
                     "the axis is not the lever")
        lines.append("     NOTE: these medians are NOT the official 18.9% -- "
                     "this function scores every")
        lines.append("     dataset the engine will predict, without the "
                     "scorer's gates and exclusions,")
        lines.append("     because both columns must cover the same population. "
                     "Only the DELTA is claimed.")
    lines.append("")

    lines.append("VERDICT")
    a_ok = worst >= SUBLINEARITY_BAR
    lines.append(f"  (A) contact-area evolution : "
                 f"{'passes' if a_ok else 'FAILS'} "
                 "(structurally cannot touch b_V; and no sub-linearity exists "
                 "to donate)")
    lines.append(f"  (B) flash-heating cross term: "
                 f"{'passes' if capable else 'FAILS'} "
                 "(predicts b_V > 1 everywhere; two bodies measure b_V < 1)")
    if not a_ok and not capable:
        lines.append("  => both named mechanisms are rejected with ZERO fitted "
                     "constants. The P-V")
        lines.append("     interaction axis is CLOSED the way the pH axis is "
                     "closed, and part (C)")
        lines.append("     is the price of that closure.")
    return "\n".join(lines)


if __name__ == "__main__":
    print(report())
