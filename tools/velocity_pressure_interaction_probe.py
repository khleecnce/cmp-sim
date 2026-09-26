"""Is the velocity exponent a CONSTANT, or does it depend on pressure?

WHY THIS SCRIPT EXISTS
----------------------
Three runs of work on the velocity axis have all assumed the object of the
search is a single number b_V such that MRR ~ P * V**b_V:

  * ``tools/velocity_thermal_probe.py`` (2026-09-26) measured a one-sided
    velocity residual (median d ln(meas/pred)/d ln V = -0.549) and rejected
    frictional heating, Stribeck lubrication and P*V series resistance.
  * ``tools/sorooshian_flow_probe.py`` (2026-09-26) measured b_V = +0.655 on a
    full factorial that PASSES the Preston audit, corroborating sub-linearity
    as an experimental fact -- but falsified its only zero-constant derivation
    (reactant starvation) on the flow leg, b_Q = -0.010 vs +1/3 required.

Before proposing a fourth functional form for b_V, establish the SHAPE of the
thing being explained. Borucki & Philipossian (ECS J. Solid State Sci. Technol.
12 (2023) 043003, DOI 10.1149/2162-8777/accaa6) report copper velocity
exponents that CHANGE SIGN with pressure -- -0.81 / -0.62 / +0.33 at
1 / 1.5 / 2 psi on one tool, one pad, one slurry. If that holds here, then NO
global velocity exponent, derived or fitted, can be right, and the missing
physics is the P-V INTERACTION rather than V alone.

WHAT IS MEASURED (and what is NOT)
----------------------------------
At FIXED pressure, Preston's P-linearity is a constant factor, so the raw
log-log slope of measured rate against speed IS the velocity exponent, with no
model in the loop and no fitted scale. That is deliberately the weakest,
least model-dependent estimator available: this probe must not be able to
inherit an artefact from the simulator it is auditing.

Two independent bodies of data:

1. Sorooshian 2005 (``research/digitized/sorooshian2005_ild_cmp.csv``):
   thermal oxide, 2/4/6 psi x 0.32/0.64/0.96 m/s x 40/120 cc/min x 3 grooves
   x 2 pad thicknesses. Each (groove, thickness, flow, pressure) cell gives one
   3-point velocity ladder, so exponents can be cut per pressure directly.
2. The corpus's own datasets: any (dataset, pressure) cell holding >= 3
   distinct platen speeds.

PRE-REGISTERED DECISION RULE (fixed before looking, as for the size and
concentration probes, whose material hypotheses this same rule falsified)
-------------------------------------------------------------------------
Call the exponent pressure-dependent only if

    spread ACROSS pressures >= 2.0 x spread WITHIN a pressure

where "across" is the population standard deviation of the per-pressure
medians and "within" is the RMS of the per-pressure standard deviations. The
2x bar is the same one used to reject the abrasive-material hypothesis for the
concentration exponent (measured 1.6x). A sign change among the per-pressure
medians is reported separately: it is a stronger, purely qualitative claim
that no positive global exponent can accommodate.

NOTHING IS FITTED HERE. The output is a shape verdict that either keeps the
"find one velocity exponent" line open or closes it.

Run: python tools/velocity_pressure_interaction_probe.py
"""
from __future__ import annotations

import csv
import math
import statistics
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

import yaml

from cmp_sim.core.predictive_score import _measured
from cmp_sim.core.validation import dataset_paths

HERE = Path(__file__).resolve().parents[1]
SOROOSHIAN_CSV = HERE / "research" / "digitized" / "sorooshian2005_ild_cmp.csv"

#: Below three distinct speeds, a log-log "slope" is a two-point line through
#: read noise and carries no information about curvature or sign robustness.
MIN_VELOCITY_LEVELS = 3

#: Pre-registered bar. Across-pressure spread must exceed within-pressure
#: spread by this factor before the exponent is called pressure-dependent.
INTERACTION_BAR = 2.0

#: Borucki & Philipossian, ECS JSS 12 (2023) 043003, DOI 10.1149/2162-8777/accaa6.
#: Copper, one tool / pad / slurry; the observation that motivates this probe.
BORUCKI_CU_EXPONENTS = {1.0: -0.81, 1.5: -0.62, 2.0: +0.33}


@dataclass
class Ladder:
    """One velocity ladder at a single pressure."""
    source: str
    psi: float
    n_levels: int
    v_min: float
    v_max: float
    exponent: float


@dataclass
class Verdict:
    label: str
    ladders: List[Ladder] = field(default_factory=list)

    def by_pressure(self) -> Dict[float, List[float]]:
        out: Dict[float, List[float]] = defaultdict(list)
        for lad in self.ladders:
            out[lad.psi].append(lad.exponent)
        return dict(sorted(out.items()))

    def medians(self) -> Dict[float, float]:
        return {p: statistics.median(e) for p, e in self.by_pressure().items()}

    def spreads(self) -> Tuple[Optional[float], Optional[float]]:
        """(across-pressure spread, within-pressure spread).

        Across = population stdev of the per-pressure medians. Within = RMS of
        the per-pressure population stdevs, using only pressures with >= 2
        ladders (a single ladder carries no information about within-spread and
        must not be allowed to deflate it towards zero, which would make any
        dataset look interaction-dominated).
        """
        groups = self.by_pressure()
        meds = list(self.medians().values())
        across = statistics.pstdev(meds) if len(meds) >= 2 else None
        withins = [statistics.pstdev(v) for v in groups.values() if len(v) >= 2]
        within = math.sqrt(sum(w * w for w in withins) / len(withins)) if withins else None
        return across, within

    def ratio(self) -> Optional[float]:
        across, within = self.spreads()
        if across is None or within is None or within == 0:
            return None
        return across / within

    def sign_change(self) -> bool:
        meds = list(self.medians().values())
        return any(a > 0 for a in meds) and any(a < 0 for a in meds)


def _slope(xs: Sequence[float], ys: Sequence[float]) -> Optional[float]:
    mx = statistics.fmean(xs)
    my = statistics.fmean(ys)
    den = sum((x - mx) ** 2 for x in xs)
    if den == 0:
        return None
    return sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / den


def _geo(values: Sequence[float]) -> float:
    return math.exp(statistics.fmean(math.log(v) for v in values))


# --------------------------------------------------------------------------
# Body 1: Sorooshian 2005, per-pressure ladders
# --------------------------------------------------------------------------
def sorooshian_ladders() -> List[Ladder]:
    cells: Dict[tuple, List[float]] = defaultdict(list)
    with SOROOSHIAN_CSV.open(newline="", encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            key = (row["groove"], float(row["thick"]), float(row["flow"]),
                   float(row["psi"]), float(row["vel"]))
            cells[key].append(float(row["rr"]))

    ladders: Dict[tuple, List[Tuple[float, float]]] = defaultdict(list)
    for (groove, thick, flow, psi, vel), rates in cells.items():
        ladders[(groove, thick, flow, psi)].append((vel, _geo(rates)))

    out: List[Ladder] = []
    for (groove, thick, flow, psi), pts in sorted(ladders.items()):
        if len(pts) < MIN_VELOCITY_LEVELS:
            continue
        slope = _slope([math.log(v) for v, _ in pts],
                       [math.log(r) for _, r in pts])
        if slope is None:
            continue
        out.append(Ladder(
            source=f"sorooshian/{groove}/{thick:g}mm/{flow:g}cc",
            psi=psi, n_levels=len(pts),
            v_min=min(v for v, _ in pts), v_max=max(v for v, _ in pts),
            exponent=slope))
    return out


# --------------------------------------------------------------------------
# Body 2: the corpus's own velocity ladders, cut per pressure
# --------------------------------------------------------------------------
def _speed(row: Dict[str, Any]) -> Optional[float]:
    """Platen rpm as the velocity proxy; a constant of proportionality does
    not affect a log slope (same choice as velocity_thermal_probe)."""
    value = row.get("rpm_platen")
    return None if value in (None, 0) else float(value)


#: Row fields that must NOT enter the grouping key.
#:
#:  * the kinematic and load fields ARE the ladder's axes;
#:  * ``rpm_wafer``/``rpm_head`` co-vary with platen speed in every corpus
#:    dataset (the head tracks the platen), so keeping them would make every
#:    row its own group and silently return zero ladders;
#:  * ``label`` is free text naming the row's own conditions, and the rest are
#:    the measurement and its provenance, not a condition.
_NOT_A_CONDITION = {
    "pressure_psi", "rpm_platen", "rpm_wafer", "rpm_head",
    "label", "read_method", "mrr_nm_per_min", "mrr_a_per_min",
    "removal_rate_nm_per_min", "source", "doi", "comment",
}


def _condition_key(row: Dict[str, Any], ignore: Sequence[str] = ()) -> tuple:
    """Everything that is NOT speed/pressure, so a ladder varies only speed.

    Without this, rows differing in chemistry (pH, oxidiser, abrasive) would be
    pooled into one "ladder" and the slope would measure chemistry, not speed.
    """
    skip = set(ignore) | _NOT_A_CONDITION
    return tuple(sorted((k, repr(v)) for k, v in row.items()
                        if k not in skip and not k.startswith("measured")
                        and not k.startswith("note")))


def corpus_ladders() -> List[Ladder]:
    out: List[Ladder] = []
    for path in dataset_paths():
        doc = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
        rows = [r for r in (doc.get("conditions") or [])
                if _measured(r) is not None and _speed(r)
                and r.get("pressure_psi")]
        if not rows:
            continue
        groups: Dict[tuple, List[Tuple[float, float]]] = defaultdict(list)
        for row in rows:
            key = (float(row["pressure_psi"]), _condition_key(row, ()))
            speed = _speed(row)
            assert speed is not None
            groups[key].append((speed, float(_measured(row))))  # type: ignore[arg-type]
        for (psi, _), pts in groups.items():
            # collapse duplicate speeds geometrically
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
            out.append(Ladder(
                source=Path(path).stem, psi=psi, n_levels=len(levels),
                v_min=levels[0][0], v_max=levels[-1][0], exponent=slope))
    return out


#: Corpus datasets that produce per-pressure velocity ladders, reviewed one by
#: one. A dataset may only be SCORED if its ladder holds every non-kinematic
#: factor fixed; otherwise the slope measures chemistry, not speed. The reasons
#: are recorded here rather than applied silently, and ``unreviewed_sources()``
#: makes a newly added dataset show up loudly instead of joining the average.
REVIEWED_CORPUS: Dict[str, Tuple[bool, str]] = {
    "mariscal2020_peteos_ceria_pressure_velocity_3x3": (
        True, "genuine 3x3 pressure x velocity factorial, one slurry"),
    "us6918821b2_cu_ic1000_pressure_speed_2x3": (
        True, "genuine 2x3 pressure x speed factorial, one slurry and pad"),
    "sic2023_shear_rheological_L9": (
        False,
        "L9 orthogonal array: abrasive size (0.5/1.0 um) and loading "
        "(3/6/9 wt%) change from row to row and are recorded only in the row "
        "LABEL, not in fields the grouping key can see, so its 'ladders' pool "
        "chemically different slurries (hence b_V = +6.76 at one pressure). "
        "Excluded as a design confound, not for its answer."),
}


def unreviewed_sources(ladders: Sequence[Ladder]) -> List[str]:
    return sorted({lad.source for lad in ladders
                   if lad.source not in REVIEWED_CORPUS})


def admissible_corpus(ladders: Sequence[Ladder]) -> Dict[str, List[Ladder]]:
    """Per-dataset ladders for the datasets whose design permits scoring.

    Grouping PER DATASET is essential: pooling one ladder from each of several
    datasets makes the across-pressure spread measure the difference between
    films, slurries and tools, which is how a first cut of this probe produced
    a spurious 22x.
    """
    out: Dict[str, List[Ladder]] = defaultdict(list)
    for lad in ladders:
        ok, _ = REVIEWED_CORPUS.get(lad.source, (False, "unreviewed"))
        if ok:
            out[lad.source].append(lad)
    return dict(sorted(out.items()))


def monotone_trend(v: Verdict) -> Optional[str]:
    """Is the per-pressure median monotone in pressure? ('up', 'down', None).

    Reported SEPARATELY from the pre-registered ratio rule and explicitly as a
    post-hoc statistic (it was added after seeing that Sorooshian's medians
    rise monotonically while its ratio sits at 0.99x). It is disclosed rather
    than substituted, because swapping in a statistic chosen after the fact is
    how a probe starts confirming what its author already believes.

    The ratio rule is structurally insensitive when a pressure holds MANY
    ladders: it compares the spread of MEDIANS against the spread of SINGLE
    ladders, and a median of ~10 ladders is roughly sqrt(10) times more precise
    than one ladder. The rule was calibrated on the size/concentration probes,
    where each group held a handful of sweeps.
    """
    meds = list(v.medians().values())
    if len(meds) < 3:
        return None
    ups = all(b > a for a, b in zip(meds, meds[1:]))
    downs = all(b < a for a, b in zip(meds, meds[1:]))
    return "up" if ups else "down" if downs else None


def median_stderr(v: Verdict) -> Dict[float, Optional[float]]:
    """Approximate standard error of each per-pressure median (1.253*s/sqrt(n)).

    The 1.253 factor is the asymptotic efficiency of the median relative to the
    mean for a normal sample; it is used only to say whether the per-pressure
    medians are separated by more than their own noise, never to fit anything.
    """
    out: Dict[float, Optional[float]] = {}
    for psi, exps in v.by_pressure().items():
        out[psi] = (1.253 * statistics.pstdev(exps) / math.sqrt(len(exps))
                    if len(exps) >= 3 else None)
    return out


def borucki_verdict() -> Verdict:
    """The published observation, scored by the SAME rule, for calibration.

    One ladder per pressure means the within-pressure spread is undefined, so
    the ratio rule cannot fire. That is the honest outcome: Borucki's numbers
    can only make the QUALITATIVE sign-change claim, and this makes that
    limitation visible instead of letting a literature quote outrank measured
    data.
    """
    v = Verdict("Borucki 2023 (Cu, published)")
    for psi, exp in BORUCKI_CU_EXPONENTS.items():
        v.ladders.append(Ladder(source="borucki2023", psi=psi, n_levels=3,
                                v_min=float("nan"), v_max=float("nan"),
                                exponent=exp))
    return v


def _describe(v: Verdict) -> List[str]:
    lines = [f"{v.label}: {len(v.ladders)} ladders, "
             f"{len(v.by_pressure())} pressure levels"]
    if not v.ladders:
        lines.append("  (no ladder met the >= 3 velocity level bar)")
        return lines
    errs = median_stderr(v)
    for psi, exps in v.by_pressure().items():
        spread = (f", stdev {statistics.pstdev(exps):+.3f}"
                  if len(exps) >= 2 else ", stdev n/a (1 ladder)")
        se = errs.get(psi)
        semsg = f", SE(median) {se:.3f}" if se is not None else ""
        lines.append(f"  {psi:>5.2f} psi  n={len(exps):<3d} "
                     f"median b_V = {statistics.median(exps):+.3f}{spread}{semsg}")
    across, within = v.spreads()
    lines.append(f"  across-pressure spread : "
                 f"{'n/a' if across is None else f'{across:.3f}'}")
    lines.append(f"  within-pressure spread : "
                 f"{'n/a' if within is None else f'{within:.3f}'}")
    ratio = v.ratio()
    lines.append(f"  ratio                  : "
                 f"{'n/a' if ratio is None else f'{ratio:.2f}x'}"
                 f"   (bar = {INTERACTION_BAR:.1f}x)")
    lines.append(f"  sign change across pressures: "
                 f"{'YES' if v.sign_change() else 'no'}")
    trend = monotone_trend(v)
    lines.append(f"  monotone in pressure (post-hoc): "
                 f"{trend or 'no'}")
    return lines


def bodies() -> List[Verdict]:
    """Every body of evidence, each SCORED SEPARATELY.

    Never pooled: each body is one film / slurry / tool, and the whole question
    is whether b_V moves with pressure WITHIN such a set.
    """
    out = [Verdict("Sorooshian 2005 (thermal oxide, 3 grooves x 2 thick x 2 flow)",
                   sorooshian_ladders())]
    corpus = corpus_ladders()
    for name, lads in admissible_corpus(corpus).items():
        ok_reason = REVIEWED_CORPUS[name][1]
        out.append(Verdict(f"{name} ({ok_reason})", lads))
    out.append(borucki_verdict())
    return out


def report() -> str:
    lines = ["VELOCITY EXPONENT x PRESSURE INTERACTION PROBE",
             "Question: is b_V in MRR ~ P * V**b_V one number, or does it move "
             "with P?",
             "Pre-registered bar: across/within spread >= "
             f"{INTERACTION_BAR:.1f}x, or a sign change, => pressure-dependent",
             ""]

    all_bodies = bodies()
    for body in all_bodies:
        lines += _describe(body) + [""]

    excluded = [(n, why) for n, (ok, why) in REVIEWED_CORPUS.items() if not ok]
    if excluded:
        lines.append("EXCLUDED CORPUS DATASETS (design, not answer)")
        for name, why in excluded:
            lines.append(f"  {name}: {why}")
        lines.append("")

    unreviewed = unreviewed_sources(corpus_ladders())
    if unreviewed:
        lines.append("UNREVIEWED corpus sources producing ladders — review "
                     "these before trusting any verdict:")
        for name in unreviewed:
            lines.append(f"  {name}")
        lines.append("")

    scorable = [b for b in all_bodies if b.ratio() is not None]
    fired = [b for b in scorable if b.ratio() >= INTERACTION_BAR]  # type: ignore[operator]
    signs = [b for b in all_bodies if b.sign_change() and len(b.ladders) >= 2]
    trends = [b for b in all_bodies if monotone_trend(b)]

    lines.append("VERDICT")
    lines.append(f"  bodies scorable by the ratio rule : {len(scorable)}")
    lines.append(f"  ratio rule fires in              : {len(fired)}")
    lines.append(f"  sign change within a body        : {len(signs)}")
    lines.append(f"  monotone medians (post-hoc)      : "
                 f"{', '.join(f'{b.label.split()[0]}:{monotone_trend(b)}' for b in trends) or 'none'}")
    lines.append("")
    if fired or signs:
        lines.append("  b_V IS pressure-dependent in at least one body: "
                     + ", ".join(sorted({b.label.split(' (')[0]
                                         for b in fired + signs})))
        lines.append("  => a single global velocity exponent, derived or "
                     "fitted, CANNOT be right. The missing physics is the P-V "
                     "INTERACTION, not V alone.")
    elif trends:
        lines.append("  The ratio rule does not fire anywhere, but the "
                     "per-pressure medians are MONOTONE in pressure where they "
                     "can be seen. Under-powered, not negative: report as "
                     "'suggestive, undecided' and do not adopt an exponent.")
    else:
        lines.append("  b_V is CONSTANT in pressure in every body that can be "
                     "scored. One number explains the ladders.")
    return "\n".join(lines)


if __name__ == "__main__":
    print(report())
