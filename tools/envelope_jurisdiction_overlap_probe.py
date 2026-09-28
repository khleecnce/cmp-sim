"""Does the envelope's `model-scale-failure` class SAY anything absolute_scale_audit
does not already say?

§58 delivered a split of the plausibility envelope's 30 firing blocks, and
STATUS's 61st-run item treats `model-scale-failure` + `mixed` (19 blocks) as a
new population to hunt a shared condition axis in.  Before hunting, ask the
cheaper question the ladder demands: **is this a new reader, or the absolute
scale audit wearing a different name?**

Both readers look at absolute rate.  If the classification is recoverable from
`|log10 scale_ratio|` alone, then §34 already owns these blocks and the only
NEW jurisdiction is the blocks `absolute_scale_audit` structurally cannot see --
those whose dataset notes forbid absolute comparison (`scale_ratio is None`),
where the envelope is the ONLY absolute reader in the repository.

This module MEASURES ONLY.
Run: .venv/bin/python tools/envelope_jurisdiction_overlap_probe.py
"""
from __future__ import annotations

import math
import statistics
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools.envelope_saturation_census import collect  # noqa: E402
from cmp_sim.core.predictive_score import score_all  # noqa: E402

#: The classes §58 calls a model defect.
FAILING = ("model-scale-failure", "mixed")

#: `absolute_scale_audit.SCALE_BAR`, re-imported rather than repeated so the two
#: numbers cannot drift apart.
from tools.absolute_scale_audit import SCALE_BAR  # noqa: E402


@dataclass
class Row:
    dataset: str
    film: str
    klass: str
    log_scale: Optional[float]     # None -> absolute comparison forbidden

    @property
    def failing(self) -> bool:
        return self.klass in FAILING

    @property
    def seen_by_scale_audit(self) -> bool:
        return self.log_scale is not None


def rows() -> List[Row]:
    sc = {s.dataset: s for s in score_all()}
    out: List[Row] = []
    for b in collect():
        s = sc.get(b.dataset)
        ls = None
        if s is not None and s.scale_ratio is not None and s.scale_ratio > 0:
            ls = math.log10(float(s.scale_ratio))
        out.append(Row(dataset=b.dataset, film=b.film, klass=b.klass,
                       log_scale=ls))
    return out


def separation(rs: Optional[List[Row]] = None) -> Dict[str, float]:
    """How well does |log10 scale| alone reproduce the failing/not split?"""
    rs = rows() if rs is None else rs
    comparable = [r for r in rs if r.seen_by_scale_audit]
    fail = [abs(float(r.log_scale or 0.0)) for r in comparable if r.failing]
    rest = [abs(float(r.log_scale or 0.0)) for r in comparable if not r.failing]
    # Mann-Whitney style rank statistic: P(a failing block misses by more).
    wins = sum(1 for a in fail for b in rest if a > b)
    ties = sum(1 for a in fail for b in rest if a == b)
    auc = (wins + 0.5 * ties) / (len(fail) * len(rest)) if fail and rest else float("nan")
    return {
        "n_failing": len(fail),
        "n_rest": len(rest),
        "median_failing": statistics.median(fail) if fail else float("nan"),
        "median_rest": statistics.median(rest) if rest else float("nan"),
        "auc": auc,
    }


def disagreements(rs: Optional[List[Row]] = None) -> Dict[str, List[Row]]:
    """Where the repository's TWO absolute readers return opposite verdicts.

    `absolute_scale_audit` reduces a block to ONE number -- the MEDIAN of
    measured/predicted over its rows -- and flags it at `SCALE_BAR`.  The
    envelope reads every ROW.  A median is a reduction, so §45's question
    applies to it: a block whose rows straddle the envelope can pass the scale
    audit at 1.09x while individual predictions are outside a published
    plausibility bound.  That is not the same claim, and neither reader
    reports the other's.

      `hidden-by-median`   envelope fires, scale audit passes it
      `forbidden`          envelope fires, the scale audit structurally cannot
                           see the block (its dataset forbids absolute
                           comparison), so the envelope is the ONLY reader
      `scale-only`         scale audit flags it, the envelope never fires
    """
    rs = rows() if rs is None else rs
    bar = math.log10(SCALE_BAR)
    out: Dict[str, List[Row]] = {"hidden-by-median": [], "forbidden": [],
                                 "scale-only": []}
    for r in rs:
        if r.failing and not r.seen_by_scale_audit:
            out["forbidden"].append(r)
        elif r.failing and abs(float(r.log_scale or 0.0)) < bar:
            out["hidden-by-median"].append(r)
        elif (not r.failing) and r.seen_by_scale_audit \
                and abs(float(r.log_scale or 0.0)) >= bar:
            out["scale-only"].append(r)
    return out


def unique_jurisdiction(rs: Optional[List[Row]] = None) -> List[Row]:
    """Failing blocks NO absolute-scale reader can see.

    `scale_ratio is None` is not missing data: the dataset's own notes forbid
    absolute comparison (benchtop coupons, scaled units).  `absolute_scale_audit`
    correctly drops them, so for these blocks the envelope is the repository's
    only reader of absolute rate.
    """
    rs = rows() if rs is None else rs
    return [r for r in rs if r.failing and not r.seen_by_scale_audit]


def report() -> str:
    rs = rows()
    sep = separation(rs)
    fails = [r for r in rs if r.failing]
    out: List[str] = []
    out.append("blocks: %d   envelope-failing (%s): %d"
               % (len(rs), "+".join(FAILING), len(fails)))
    out.append("")
    out.append("Q1  IS THE CLASS RECOVERABLE FROM |log10 scale| ALONE?")
    out.append("    (if yes, absolute_scale_audit already owns these blocks)")
    out.append("      failing  n=%d  median |log10 scale| = %.3f  (%.2fx)"
               % (sep["n_failing"], sep["median_failing"],
                  10 ** sep["median_failing"]))
    out.append("      rest     n=%d  median |log10 scale| = %.3f  (%.2fx)"
               % (sep["n_rest"], sep["median_rest"], 10 ** sep["median_rest"]))
    out.append("      rank AUC = %.3f   (0.5 = no information, 1.0 = the two"
               % sep["auc"])
    out.append("                 readers agree perfectly)")
    out.append("")
    out.append("Q2  IS THE FAILING POPULATION ONE-SIDED?")
    signed = [float(r.log_scale or 0.0) for r in fails if r.seen_by_scale_audit]
    under = sum(1 for v in signed if v > 0)
    out.append("      median SIGNED log10 scale = %+.3f  (%.2fx);  %d under- vs"
               % (statistics.median(signed), 10 ** statistics.median(signed),
                  under))
    out.append("      %d over-predicting.  A centred population cannot be"
               % (len(signed) - under))
    out.append("      repaired by any factor missing from every pack (§34).")
    out.append("")
    out.append("Q3  WHERE DO THE TWO ABSOLUTE READERS DISAGREE?")
    out.append("    absolute_scale_audit reduces a block to the MEDIAN of")
    out.append("    measured/predicted; the envelope reads every ROW.  A median")
    out.append("    is a reduction, so §45's question applies to it too.")
    dis = disagreements(rs)
    for k in ("hidden-by-median", "forbidden", "scale-only"):
        out.append("      %-18s %d" % (k, len(dis[k])))
        for r in sorted(dis[k], key=lambda r: r.dataset):
            ls = r.log_scale
            out.append("        %-52s %-7s %s"
                       % (r.dataset, r.film,
                          "(absolute comparison forbidden)" if ls is None
                          else "%+.2f (%.2fx)  klass=%s" % (ls, 10 ** ls,
                                                            r.klass)))
    total = sum(len(v) for v in dis.values())
    out.append("")
    out.append("VERDICT")
    out.append("  The two readers disagree on %d of %d blocks (AUC %.2f), so"
               % (total, len(rs), sep["auc"]))
    out.append("  neither is a re-reading of the other and NEITHER reports the")
    out.append("  other's finding.  The deliverable is the DECLARED division of")
    out.append("  labour, not a change to either reader:")
    out.append("    * `hidden-by-median` (%d): the scale audit's own reduction"
               % len(dis["hidden-by-median"]))
    out.append("      collapses straddling rows, so a block passes at ~1.1x")
    out.append("      while individual predictions leave a published bound.")
    out.append("    * `forbidden` (%d): the envelope is the ONLY absolute reader"
               % len(dis["forbidden"]))
    out.append("      this repository has for these blocks.")
    out.append("    * `scale-only` (%d): flagged by scale, never by the"
               % len(dis["scale-only"]))
    out.append("      envelope -- inside the bound and still 3x+ wrong.")
    out.append("")
    out.append("  ⚠ This does NOT justify hunting a shared condition axis across")
    out.append("  `model-scale-failure` as one population (STATUS 61-1): the")
    out.append("  signed misses are centred (%+.3f, %d under vs %d over), which"
               % (statistics.median(signed), under, len(signed) - under))
    out.append("  §34 already showed closes the 'one universal correction'")
    out.append("  search before it starts.")
    out.append("")
    out.append("⚠ NOT a licence to widen an envelope or to drop a block; the")
    out.append("  bar used above is absolute_scale_audit's own SCALE_BAR = %.1fx."
               % SCALE_BAR)
    return "\n".join(out)


if __name__ == "__main__":                                # pragma: no cover
    print(report())
