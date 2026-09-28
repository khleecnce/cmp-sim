"""WHERE does the ABSOLUTE scale fail, and is it one cause or nine? (20th run)

Why this probe exists
---------------------
The axis programme is closed: six swept axes (§14), the oxidiser order (§15),
the <=10 % ceiling (§16), every inert axis (§19/§20) and now Ce3+ (§21). Every
one of those was measured against the SHAPE score -- MAPE after one free
multiplicative scale.

That free scale is the point. It is what makes shape a fair test of a trend,
and it is also what makes the corpus median **structurally blind** to being
wrong about the rate itself. `score_report.py` currently reports **nine blocks
whose absolute rate is off by more than 3x**, in BOTH directions (0.07x to
12.7x), and not one of those failures can move the median by a single point.

For a process simulator that is the more serious failure of the two: "the trend
is right but the rate is 10x out" is not usable by a fab, and reporting only
"median shape 18.9 %" hides it.

THE PRE-REGISTERED QUESTIONS (recorded in STATUS.md before this ran)
--------------------------------------------------------------------
S1  HOW BIG IS THE POPULATION, and is it symmetric in log space?
    A scatter centred on 1.0x with heavy tails is a per-pack calibration
    problem. A population systematically on one side is a missing factor
    common to the corpus.

S2  DOES THE MISS TRACK THE PACK, OR THE DATASET?
    If every block sharing a pack misses by the same factor, the pack's Kp is
    simply mis-anchored and the fix is one traceable constant per pack. If
    blocks sharing a pack disagree, the Kp is fine and something in the
    condition mapping is wrong.
    This is the whole diagnostic: it separates "one number is wrong" from
    "the model is wrong", and the two have completely different prices.

S3  IS THE FAILURE INHERITED FROM Kp'S OWN PROVENANCE?
    Each pack's `kp_m_per_pa` was back-calculated from ONE measurement. A block
    measured far from that anchoring condition (different film variant, pad,
    polisher) should miss by more. The probe reports each pack's Kp confidence
    alongside the misses so the correlation is visible rather than assumed.

S4  WOULD RE-ANCHORING BE A FIT?
    Yes, wherever the re-anchoring set is the block being scored. Any block
    that is `used_for_calibration`, or is the sole evidence for its pack's Kp,
    cannot be used to justify moving that Kp -- the 13th-run rule applied to
    scale instead of to shape. Reported, never silently used.

This module MEASURES ONLY. It fits nothing into any pack and must never modify
one. Usage: ``python tools/absolute_scale_audit.py`` (inside ``.venv``).
"""
from __future__ import annotations

import math
import statistics
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

from cmp_sim.core.predictive_score import score_all

#: A block missing the absolute rate by more than this factor, either way, is
#: reported as a scale failure. 3x is the threshold score_report.py already
#: uses, kept identical so the two numbers can never drift apart.
SCALE_BAR = 3.0


@dataclass
class ScaleMiss:
    dataset: str
    film: str
    pack: str
    n: int
    shape: Optional[float]
    scale: float                      # median measured/predicted
    used_for_calibration: bool
    kp_confidence: Optional[str] = None

    @property
    def log_scale(self) -> float:
        return math.log10(self.scale)

    @property
    def can_justify_reanchoring(self) -> bool:
        """S4: a block the pack was calibrated on cannot re-anchor that pack."""
        return not self.used_for_calibration


@dataclass
class PackVerdict:
    pack: str
    blocks: List[ScaleMiss] = field(default_factory=list)

    @property
    def log_scales(self) -> List[float]:
        return [b.log_scale for b in self.blocks]

    @property
    def coherent(self) -> Optional[bool]:
        """True when every block under this pack misses the SAME way.

        Coherent -> one mis-anchored constant, fixable and traceable.
        Incoherent -> **no single constant fits these blocks.** It does NOT
        establish that Kp is innocent, and this docstring used to say that it
        did: `median` and `spread` are functions of the MULTISET of scale
        values, so permuting which block holds which value leaves both exactly
        unchanged. The reduction therefore spans `scale = const + noise` and
        cannot tell scatter from a systematic trend along a condition
        (docs/limits.md §47, `tools/scale_coherence_trend_probe.py`). On
        `cu_h2o2_bta` the scale trends with pressure at p_perm = 0.009 while
        being reported here only as a 59x spread.
        Needs at least two blocks to mean anything.
        """
        if len(self.blocks) < 2:
            return None
        spread = max(self.log_scales) - min(self.log_scales)
        return spread < math.log10(SCALE_BAR)

    @property
    def median_log(self) -> float:
        return statistics.median(self.log_scales)


def _pack_kp_confidence(pack_name: str) -> Optional[str]:
    from cmp_sim.core.params import load_pack
    try:
        pack = load_pack(pack_name)
    except Exception:  # noqa: BLE001
        return None
    param = pack.params.get("kp_m_per_pa")
    return None if param is None else str(getattr(param, "confidence", "?"))


def collect() -> List[ScaleMiss]:
    """Every scored block that has a comparable absolute scale."""
    from cmp_sim.core.validation import dataset_paths
    docs = {}
    for path in dataset_paths():
        doc = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
        docs[Path(path).stem] = doc
    out = []
    for score in score_all():
        if score.scale_ratio is None:
            continue
        doc = docs.get(score.dataset, {})
        pack = str(doc.get("pack") or "?")
        out.append(ScaleMiss(
            dataset=score.dataset, film=score.film, pack=pack, n=score.n,
            shape=score.shape_mape, scale=float(score.scale_ratio),
            used_for_calibration=bool(doc.get("used_for_calibration")),
            kp_confidence=_pack_kp_confidence(pack),
        ))
    return out


def failures(blocks: List[ScaleMiss]) -> List[ScaleMiss]:
    bar = math.log10(SCALE_BAR)
    return [b for b in blocks if abs(b.log_scale) >= bar]


def by_pack(blocks: List[ScaleMiss]) -> List[PackVerdict]:
    groups: Dict[str, PackVerdict] = defaultdict(lambda: PackVerdict(pack=""))
    for b in blocks:
        verdict = groups[b.pack]
        verdict.pack = b.pack
        verdict.blocks.append(b)
    return sorted(groups.values(), key=lambda v: v.pack)


def symmetry(blocks: List[ScaleMiss]) -> Dict[str, Any]:
    """S1: is the miss population centred, and which way does it lean?"""
    logs = [b.log_scale for b in blocks]
    over = [b for b in blocks if b.scale > 1.0]    # model UNDER-predicts
    return {
        "n": len(blocks),
        "median_log10": statistics.median(logs),
        "median_factor": 10 ** statistics.median(logs),
        "under_predicting": len(over),
        "over_predicting": len(blocks) - len(over),
        "worst_under": max(blocks, key=lambda b: b.scale).dataset,
        "worst_over": min(blocks, key=lambda b: b.scale).dataset,
    }


def report() -> str:
    blocks = collect()
    bad = failures(blocks)
    lines = ["S1  comparable blocks: %d, of which %d miss the absolute rate by "
             ">=%.0fx" % (len(blocks), len(bad), SCALE_BAR)]
    sym = symmetry(blocks)
    lines.append("    population median %.2fx (log10 %+0.3f); "
                 "%d under-predict, %d over-predict"
                 % (sym["median_factor"], sym["median_log10"],
                    sym["under_predicting"], sym["over_predicting"]))
    lines.append("    worst under-prediction %s, worst over-prediction %s"
                 % (sym["worst_under"], sym["worst_over"]))

    lines.append("")
    lines.append("S2/S3  the failures, grouped by the pack that supplies Kp")
    for verdict in by_pack(bad):
        lines.append("    %-26s %d block(s)  median %.2fx  %s"
                     % (verdict.pack, len(verdict.blocks),
                        10 ** verdict.median_log,
                        "COHERENT (one mis-anchored Kp)"
                        if verdict.coherent
                        else ("INCOHERENT (no single constant fits these "
                              "blocks; this statistic cannot tell scatter "
                              "from a trend - limits 47)"
                              if verdict.coherent is False
                              else "single block, coherence untestable")))
        for b in verdict.blocks:
            lines.append("        %-50s %s  n=%2d  %6.2fx  shape %s  "
                         "Kp confidence %s%s"
                         % (b.dataset, b.film, b.n, b.scale,
                            "--" if b.shape is None else "%.1f%%" % b.shape,
                            b.kp_confidence,
                            "  [used_for_calibration]"
                            if b.used_for_calibration else ""))

    lines.append("")
    lines.append("S2  coherence across ALL comparable blocks, not just the "
                 "failures (a pack can be coherent and still wrong)")
    for verdict in by_pack(blocks):
        if len(verdict.blocks) < 2:
            continue
        spread = max(verdict.log_scales) - min(verdict.log_scales)
        lines.append("    %-26s %d blocks  median %.2fx  spread %.1fx  %s"
                     % (verdict.pack, len(verdict.blocks),
                        10 ** verdict.median_log, 10 ** spread,
                        "coherent" if verdict.coherent else "INCOHERENT"))

    lines.append("")
    unusable = [b for b in bad if not b.can_justify_reanchoring]
    lines.append("S4  of the %d failures, %d cannot justify re-anchoring their "
                 "own pack (used_for_calibration): %s"
                 % (len(bad), len(unusable),
                    ", ".join(b.dataset for b in unusable) or "none"))
    return "\n".join(lines)


if __name__ == "__main__":
    print(report())
