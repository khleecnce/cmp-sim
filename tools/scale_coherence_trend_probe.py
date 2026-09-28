"""A per-pack coherence verdict can only represent ONE CONSTANT OFFSET — so a
scale that TRENDS along an axis is filed as "the blocks disagree".

WHY THIS PROBE EXISTS
---------------------
`docs/limits.md` §43-§46 walk one ladder of reader defects: who chooses the
perturbation (§43), who chooses the evaluation points (§44), what the reduction
throws away (§45), and what FUNCTION FAMILY the reduction can represent (§46).
This probe applies §46's question to the reduction behind the repository's whole
absolute-scale story.

`tools/absolute_scale_audit.py` reduces each pack to two numbers:

    median_log = median over its blocks of log10(measured/predicted)
    spread     = max(log10 scale) - min(log10 scale)

and calls the pack `coherent` when `spread < log10(3)`.  The published reading
(limits §22/§23, STATUS) is:

    "COHERENT   -> one mis-anchored Kp, the fix is one traceable constant"
    "INCOHERENT -> the blocks disagree, so Kp is NOT the cause"

The second half is the over-claim, and it is an over-claim about a FAMILY.
`median` and `spread` are both functions of the *multiset* of scale values, so
they are INVARIANT to which block holds which value.  Permute the assignment of
scale ratios to blocks and both numbers are unchanged to the last bit, while any
statistic of the pack's scale AGAINST a condition axis moves freely.  The
reduction therefore spans exactly the family

    scale(block) = const  + noise

and can express nothing about `scale(block) = A * P^b`.  A pack whose miss rises
or falls SYSTEMATICALLY with a condition is mapped to a large `spread`, i.e. to
"the blocks disagree" -- a conclusion that retires the Kp question with an answer
the statistic is structurally unable to have earned.  The blindness is arithmetic
(a symmetry of the reduction), so no corpus change retires it, exactly as in §45.

WHAT THIS PROBE MEASURES
------------------------
For every pack with at least MIN_BLOCKS comparable blocks, it regresses
`log10(scale_ratio)` on `log(median axis value)` for each condition axis the
pack's blocks differ in, and prices the slope against a PERMUTATION NULL (the
same 2000-shuffle control §46 used), because with 4-8 blocks a large |r| is
cheap.  A pack is `trending` on an axis when the permutation p-value is below
`P_BAR`.

THE CONFOUND CONTROL -- READ THIS BEFORE QUOTING ANY SLOPE
----------------------------------------------------------
A cross-BLOCK trend is not a law.  Blocks differ by publication, so pressure
covaries with pad, polisher, film variant, slurry vendor and rpm; a trend in the
cross-block direction can be carried by any of them.  The repository already has
the control that holds all of those FIXED: `tools/pressure_saturation_probe.py`
regresses `ln(measured/scaled prediction)` on `ln P` WITHIN each block.  This
probe re-runs it and prints both readings side by side.  When the within-block
slopes straddle zero while the cross-block slope is large, the honest conclusion
is that the cross-block trend is a confound -- and the finding is about the
READER, not about pressure.  Fitting the cross-block slope would be fitting a
per-publication offset under the name of a law (limits §14's forbidden move,
and §37's vetoed global steepening term).

This module MEASURES ONLY.  It fits nothing into any pack and must never
modify one.

Run: .venv/bin/python -m tools.scale_coherence_trend_probe
"""
from __future__ import annotations

import math
import random
import statistics
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Sequence, Tuple

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from cmp_sim.core.predictive_score import (  # noqa: E402
    dataset_paths, score_all,
)

#: A pack needs this many comparable blocks before a trend can be told from a
#: two-point slope.  4 is the smallest number that leaves 2 residual degrees of
#: freedom, which is also why the permutation null is mandatory rather than nice.
MIN_BLOCKS = 4

#: Permutation p-value below which a slope is called a trend.  It is a
#: SIGNIFICANCE bar against the reduction's own degrees of freedom, not a fitted
#: threshold on the slope's size: the claim being tested is "this reduction
#: cannot represent a trend", so what matters is whether a trend is present at
#: all, never how steep it is.
P_BAR = 0.05

#: Shuffles for the permutation null.  Same count as §46's curvature probe so
#: the two nulls are comparable.
N_PERM = 2000

#: How each condition axis is read off a validation row.  A declared map, never
#: a pattern match over row keys: a pattern eventually reads a measured-rate
#: column and a probe that regresses on the ANSWER reports nonsense
#: confidently (limits §41).
AXES: Dict[str, Callable[[Dict[str, Any]], Any]] = {
    "pressure_psi": lambda r: r.get("pressure_psi"),
    "rpm_platen": lambda r: (r.get("rpm_platen")
                             or (r.get("overrides") or {}).get("rpm_platen")),
    "abrasive_wt_pct": lambda r: (r.get("overrides") or {}).get("abrasive_wt_pct"),
    "abrasive_size_nm": lambda r: ((r.get("overrides") or {}).get("abrasive_size_nm")
                                   or (r.get("overrides") or {}).get("abrasive_d50_nm")),
    "slurry_ph": lambda r: (r.get("overrides") or {}).get("slurry_ph"),
    "oxidizer_wt_pct": lambda r: (r.get("overrides") or {}).get("oxidizer_wt_pct"),
}


@dataclass
class Block:
    dataset: str
    pack: str
    film: str
    n: int
    scale: float
    #: median of each axis over the block's rows; missing axes are absent
    axis: Dict[str, float] = field(default_factory=dict)

    @property
    def log_scale(self) -> float:
        return math.log10(self.scale)


@dataclass
class AxisTrend:
    axis: str
    n: int
    slope: float
    r: float
    p_perm: float

    @property
    def trending(self) -> bool:
        return self.p_perm < P_BAR


@dataclass
class PackVerdict:
    pack: str
    blocks: List[Block]
    trends: List[AxisTrend]

    @property
    def median_log(self) -> float:
        return statistics.median(b.log_scale for b in self.blocks)

    @property
    def spread_log(self) -> float:
        return (max(b.log_scale for b in self.blocks)
                - min(b.log_scale for b in self.blocks))

    @property
    def incoherent(self) -> bool:
        """The incumbent verdict, recomputed here so the two cannot drift."""
        return self.spread_log >= math.log10(3.0)

    @property
    def trending_axes(self) -> List[AxisTrend]:
        return [t for t in self.trends if t.trending]


def pearson(x: Sequence[float], y: Sequence[float]) -> Optional[float]:
    n = len(x)
    mx, my = sum(x) / n, sum(y) / n
    sx = math.sqrt(sum((a - mx) ** 2 for a in x))
    sy = math.sqrt(sum((b - my) ** 2 for b in y))
    if sx == 0.0 or sy == 0.0:
        return None
    return sum((a - mx) * (b - my) for a, b in zip(x, y)) / (sx * sy)


def ols_slope(x: Sequence[float], y: Sequence[float]) -> Optional[float]:
    n = len(x)
    mx, my = sum(x) / n, sum(y) / n
    den = sum((a - mx) ** 2 for a in x)
    if den == 0.0:
        return None
    return sum((a - mx) * (b - my) for a, b in zip(x, y)) / den


def axis_trend(axis: str, xs: Sequence[float], ys: Sequence[float],
               seed: int = 20260928) -> Optional[AxisTrend]:
    """Slope of log10(scale) on log(axis), priced against a permutation null."""
    r = pearson(xs, ys)
    slope = ols_slope(xs, ys)
    if r is None or slope is None:
        return None
    rng = random.Random(seed)
    shuffled = list(ys)
    hits = 0
    for _ in range(N_PERM):
        rng.shuffle(shuffled)
        rr = pearson(xs, shuffled)
        if rr is not None and abs(rr) >= abs(r):
            hits += 1
    return AxisTrend(axis=axis, n=len(xs), slope=slope, r=r,
                     p_perm=hits / N_PERM)


def blocks() -> List[Block]:
    """Every block the absolute-scale audit can compare, with its axis medians.

    `scale_ratio is None` means the dataset's own notes FORBID absolute
    comparison (benchtop coupons, scaled units).  Those are not missing data and
    must not be filled in — they are excluded, exactly as the audit excludes
    them.
    """
    docs = {p.stem: (yaml.safe_load(p.read_text(encoding="utf-8")) or {})
            for p in dataset_paths()}
    out: List[Block] = []
    for s in score_all():
        if s.scale_ratio is None or s.scale_ratio <= 0:
            continue
        doc = docs.get(s.dataset) or {}
        pack = doc.get("pack")
        if not pack:
            continue
        rows = doc.get("conditions") or []
        axis: Dict[str, float] = {}
        for name, read in AXES.items():
            vals = []
            for row in rows:
                v = read(row)
                if v is None:
                    continue
                try:
                    v = float(v)
                except (TypeError, ValueError):
                    continue
                if v > 0:
                    vals.append(v)
            if vals:
                axis[name] = statistics.median(vals)
        out.append(Block(dataset=s.dataset, pack=pack, film=s.film or "?",
                         n=s.n, scale=float(s.scale_ratio), axis=axis))
    return out


def verdicts(bs: Optional[List[Block]] = None) -> List[PackVerdict]:
    bs = bs if bs is not None else blocks()
    by: Dict[str, List[Block]] = {}
    for b in bs:
        by.setdefault(b.pack, []).append(b)
    out: List[PackVerdict] = []
    for pack, group in sorted(by.items()):
        if len(group) < MIN_BLOCKS:
            continue
        trends: List[AxisTrend] = []
        for axis in AXES:
            pts = [(math.log(b.axis[axis]), b.log_scale)
                   for b in group if b.axis.get(axis)]
            if len(pts) < MIN_BLOCKS:
                continue
            t = axis_trend(axis, [p[0] for p in pts], [p[1] for p in pts])
            if t is not None:
                trends.append(t)
        out.append(PackVerdict(pack=pack, blocks=group, trends=trends))
    return out


def cross_block_measured_exponent(pack: str, axis: str,
                                  bs: Optional[List[Block]] = None
                                  ) -> Optional[float]:
    """d ln(median MEASURED rate) / d ln(axis) ACROSS a pack's blocks.

    This reads the DATA alone -- no prediction, no scale -- so it cannot inherit
    an artefact of the model being audited.  Its use is to say what the
    cross-block direction physically claims: if the measured rate falls with
    pressure between publications while every controlled sweep inside a
    publication rises, the cross-block slope is a statement about which
    experiments got published, not about the axis.
    """
    docs = {p.stem: (yaml.safe_load(p.read_text(encoding="utf-8")) or {})
            for p in dataset_paths()}
    from cmp_sim.core.predictive_score import _measured

    xs: List[float] = []
    ys: List[float] = []
    for b in (bs if bs is not None else blocks()):
        if b.pack != pack or not b.axis.get(axis):
            continue
        rows = (docs.get(b.dataset) or {}).get("conditions") or []
        rates = [float(m) for m in (_measured(r) for r in rows) if m]
        if not rates:
            continue
        xs.append(math.log(b.axis[axis]))
        ys.append(math.log(statistics.median(rates)))
    if len(xs) < MIN_BLOCKS:
        return None
    return ols_slope(xs, ys)


def within_block_pressure_control() -> Tuple[float, int, int]:
    """The confound control: (median slope, n negative, n total) WITHIN blocks.

    Re-measured from `tools/pressure_saturation_probe.py`, never pinned: if the
    within-block reading ever stops straddling zero, this probe's conclusion
    must change with it rather than quote a stale number.
    """
    from tools.pressure_saturation_probe import trends as p_trends

    rows = p_trends()
    slopes = [t.slope for t in rows]
    return (statistics.median(slopes), sum(1 for s in slopes if s < 0),
            len(slopes))


# ── the arithmetic proof, exposed so the test can run it on synthetic input ──
def coherence_pair(scales: Sequence[float]) -> Tuple[float, float]:
    """(median_log, spread_log) — the incumbent reduction, as a pure function.

    It takes only the MULTISET of scale values.  There is no argument through
    which a condition could enter, which is the blindness stated as a type
    signature rather than as a measurement.
    """
    ls = [math.log10(s) for s in scales]
    return statistics.median(ls), max(ls) - min(ls)


def report() -> str:
    bs = blocks()
    vs = verdicts(bs)
    lines: List[str] = []
    lines.append("comparable blocks: %d across %d packs; %d packs have >= %d "
                 "blocks" % (len(bs), len({b.pack for b in bs}), len(vs),
                             MIN_BLOCKS))
    lines.append("")
    lines.append("THE BLINDNESS, AS ARITHMETIC (no corpus needed):")
    lines.append("  median_log and spread_log are functions of the MULTISET of")
    lines.append("  scale values, so permuting which block holds which value")
    lines.append("  leaves both EXACTLY unchanged while every trend statistic")
    lines.append("  moves.  The reduction spans {scale = const + noise} only.")
    lines.append("")
    for v in sorted(vs, key=lambda v: -len(v.blocks)):
        lines.append("%-28s %d blocks  median %.2fx  spread %.1fx  %s"
                     % (v.pack, len(v.blocks), 10 ** v.median_log,
                        10 ** v.spread_log,
                        "INCOHERENT" if v.incoherent else "coherent"))
        for t in sorted(v.trends, key=lambda t: t.p_perm):
            lines.append("      %-18s n=%d  slope %+.2f  r %+.2f  "
                         "p_perm %.3f%s"
                         % (t.axis, t.n, t.slope, t.r, t.p_perm,
                            "   <-- TRENDS" if t.trending else ""))
        if not v.trends:
            lines.append("      (no axis is shared by %d of its blocks)"
                         % MIN_BLOCKS)

    trending = [(v, t) for v in vs for t in v.trending_axes]
    lines.append("")
    lines.append("PACKS WHOSE 'INCOHERENT' HIDES A TREND (the finding):")
    if not trending:
        lines.append("  none in today's corpus.  That is a measurement of THIS")
        lines.append("  corpus, not a proof the reduction is safe -- the")
        lines.append("  enforcing test re-measures rather than pinning counts.")
    for v, t in sorted(trending, key=lambda vt: vt[1].p_perm):
        lines.append("  %-26s %-16s slope %+.2f  p_perm %.3f  incumbent: %s"
                     % (v.pack, t.axis, t.slope, t.p_perm,
                        "INCOHERENT" if v.incoherent else "coherent"))

    med, neg, tot = within_block_pressure_control()
    lines.append("")
    lines.append("CONFOUND CONTROL -- the same axis read WITHIN blocks, where")
    lines.append("pad/polisher/film/vendor are held fixed by construction:")
    lines.append("  pressure_saturation_probe: median d(ln ratio)/d(ln P) = "
                 "%+.3f, %d/%d negative" % (med, neg, tot))
    straddles = neg not in (0, tot)
    lines.append("  => the within-block slopes %s zero"
                 % ("STRADDLE" if straddles else "do NOT straddle"))

    lines.append("")
    lines.append("WHAT THE CROSS-BLOCK DIRECTION CLAIMS ABOUT THE DATA ALONE")
    lines.append("(no model, no scale -- so it cannot inherit an artefact of")
    lines.append("the simulator under audit):")
    for v, t in sorted(trending, key=lambda vt: vt[1].p_perm):
        b_meas = cross_block_measured_exponent(v.pack, t.axis, bs)
        if b_meas is None:
            continue
        lines.append("  %-26s %-16s d ln(MEASURED rate)/d ln(axis) = %+.2f"
                     % (v.pack, t.axis, b_meas))
        if t.axis == "pressure_psi" and b_meas < 0:
            lines.append("      Preston requires +1.  A NEGATIVE cross-block")
            lines.append("      exponent is therefore not a property of")
            lines.append("      pressure: harder-pressed publications simply")
            lines.append("      polished slower systems.  Any 'correction'")
            lines.append("      fitted to it encodes publication selection.")
    lines.append("")
    lines.append("VERDICT:")
    if trending and straddles:
        lines.append("  The cross-block trend is NOT a law about its axis: the")
        lines.append("  controlled reading finds no such dependence inside a")
        lines.append("  block, so the trend is carried by whatever ELSE changes")
        lines.append("  between publications.  Nothing is wired; no constant is")
        lines.append("  introduced; the corpus median must not move.")
        lines.append("  What changes is the READING: 'INCOHERENT' may no longer")
        lines.append("  be quoted as 'therefore Kp is not the cause'.  It means")
        lines.append("  'no single constant fits these blocks', and this")
        lines.append("  reduction cannot tell scatter from a trend.")
    elif trending:
        lines.append("  A trend survives BOTH readings.  That is a derivation")
        lines.append("  target, not a fit: price a zero-constant form before")
        lines.append("  wiring anything (limits §28/§40).")
    else:
        lines.append("  No pack's scale trends above its own permutation null")
        lines.append("  today.  The reduction's blindness stands as arithmetic")
        lines.append("  regardless; it is simply unexercised by this corpus.")
    lines.append("")
    lines.append("WHAT WOULD MAKE THE CROSS-BLOCK SLOPE QUOTABLE AS PHYSICS:")
    lines.append("  two blocks of the SAME pack differing in one condition and")
    lines.append("  nothing else (same pad, polisher, film variant and vendor),")
    lines.append("  i.e. a between-publication replicate.  The corpus has none.")
    return "\n".join(lines)


if __name__ == "__main__":
    print(report())
