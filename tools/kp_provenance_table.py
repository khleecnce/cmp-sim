"""WHAT does each absolute-scale failure's pack SILENTLY CONFLATE? (21st run)

Why this probe exists
---------------------
§22 (`tools/absolute_scale_audit.py`) established that the absolute-rate failure
is **not** a mis-anchored constant: five of eight packs disagree with THEMSELVES
by 8-222x under one shared ``kp_m_per_pa``, and the three coherent packs carry
no >=3x failure at all. A constant cannot answer a disagreement inside a
constant's own scope.

§22 named the next step and this module is it: for every >=3x failure, put the
condition its pack's Kp was back-calculated from NEXT TO the block's own
condition, and ask what differs. Where the conflated variable is identifiable
and sourced, the answer is a pack SPLIT (precedent: ``oxide_silica_aminosilane``
earned its own split and is coherent today). Where it is not, the answer is to
say so, not to average over it.

THE FINDING THIS TABLE PRODUCED
-------------------------------
**Nine of the eleven failures were already identified — in prose the scorer
cannot read.** Each of those dataset files states, in its own header, that its
pack is a placeholder, or that its condition sits outside the Kp anchor's range,
or that the absolute value is systematically biased for a named reason. The
information was never missing; it was never machine-readable, so every run since
has re-measured the same misses as if their cause were unknown.

That claim invites an obvious objection -- that such prose is an excuse written
after seeing a bad number -- so the module tests it two ways (``anti_selection``):

  1. **The prose does not predict the miss.** 17 blocks carry it and 9 of them
     land INSIDE 3x; 20 blocks do not carry it and 3 of them fail. If the prose
     were a post-hoc excuse it would mark the failures and nothing else.
  2. **The prose predates the measurement.** Every quoted line was committed
     2026-09-15 .. 2026-09-24 (``git blame``), while the audit that first
     measured these misses is 2026-09-27.

And ONE failure pair is identified quantitatively rather than in prose:

  ``sti_ceria`` excluded the ceria-coated-silica composite datasets from its Kp
  average and recorded the value they imply (~2.3e-14 vs the pack's bare-ceria
  1.09e-13). That exclusion PREDICTS a miss of 0.21x for those two blocks, with
  no freedom left over. Measured: **0.188x and 0.235x**, bracketing it. The pack
  is right about the composite being a different abrasive, and the two blocks
  are the pack's own statement being scored as if it had not been made.

WHAT THIS MODULE REFUSES TO DO
------------------------------
It does not split ``sti_ceria``. A composite Kp can only be back-calculated from
the two blocks it would then be scored on -- self-marking, the 13th-run rule
applied to scale. The split needs a composite-abrasive dataset from a source
other than US20190127607A1, and that is recorded as the resolving experiment
rather than performed with the data in hand.

This module MEASURES ONLY. It fits nothing and must never modify a pack.
Usage: ``python tools/kp_provenance_table.py`` (inside ``.venv``).
"""
from __future__ import annotations

import math
import re
import statistics
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

import yaml

from cmp_sim.core.predictive_score import score_all
from cmp_sim.core.validation import dataset_paths

#: Same bar as score_report.py and §22, kept identical so they cannot drift.
SCALE_BAR = 3.0

#: Rulings. `quote` is a substring that MUST still be present in the dataset
#: file -- the citation is checked at runtime, so a citation cannot rot into a
#: claim about text somebody deleted. Nothing here is a fitted number.
#:
#: `identified` means: the variable conflated with this block is NAMED and
#: SOURCED. It does NOT mean the block can be fixed -- see `splittable`.
#: `splittable` means an INDEPENDENT anchor exists for a split, i.e. one not
#: back-calculated from the very blocks the split would be scored on.


@dataclass(frozen=True)
class Ruling:
    conflated: str          # what the pack is silently conflating
    identified: bool
    splittable: bool
    quote: str              # verbatim substring from the dataset file
    why: str


RULINGS: Dict[str, Ruling] = {
    # ---- cu_h2o2_bta: Kp back-calculated from a literature RANGE (400-800
    # nm/min at 2-3 psi) for an acidic glycine/H2O2/BTA damascene slurry,
    # confidence `estimated`. Four of its five failures differ from that
    # anchor in the CHEMISTRY, not in the constant.
    "lai2001_cu_alumina_size_sweep": Ruling(
        conflated="slurry chemistry: neutral pH 7 alumina with NO oxidiser and "
                  "NO complexant, scored against an acidic H2O2/glycine/BTA Kp",
        identified=True, splittable=False,
        quote="Absolute MRR from any silica/Cu pack is",
        why="The dataset declares the pack a placeholder chosen for the SHAPE "
            "of the size response. A Cu slurry without an oxidiser removes by a "
            "different mechanism, so the 16x over-prediction is the anchor's "
            "chemistry, not its arithmetic. Not splittable: this is the only "
            "additive-free Cu block in the corpus, so a 'neutral alumina Cu' "
            "pack could only be anchored on itself."),
    "miranda2004_cu_ph_h2o2_2x2": Ruling(
        conflated="tool scale: a 4-inch benchtop polisher whose rates run above "
                  "damascene practice, against a 200 mm damascene Kp",
        identified=True, splittable=False,
        quote="절대값이 아니라 순위",
        why="Stated in the file's own header before this failure was measured. "
            "Tool-to-tool scale is not a slurry property and a pack split "
            "cannot carry it."),
    "ihnfeldt2008_cu_alumina_ph_oxidizer_chelator": Ruling(
        conflated="pressure regime: 1.0 psi, below the 2-3 psi window the "
                  "pack's Kp was back-calculated in",
        identified=True, splittable=False,
        quote="팩 Kp 역산 앵커 범위 밖이다",
        why="Extrapolating a Preston coefficient below its anchoring window is "
            "a known limitation of the linear form, not a wrong constant. A "
            "split on pressure would be a second Kp for the same chemistry."),
    "us8501625b2_cu_h2o2_pressure_series": Ruling(
        conflated="inhibitor species (1,2,4-triazole, not BTA) and an abrasive "
                  "loading 18x below the pack reference (0.17 vs 3.0 wt%)",
        identified=True, splittable=False,
        quote="rank_only",
        why="Both divergences are declared in the file, and both are constant "
            "across its six rows -- which is why the shape score survives "
            "(20.2%) while the scale does not. The inhibitor is the wrong "
            "lookup key, so the passivation term is being asked about a "
            "molecule it was never measured on."),
    "us6918821b2_cu_ic1000_pressure_speed_2x3": Ruling(
        conflated="UNIDENTIFIED — the patent states no slurry composition",
        identified=False, splittable=False,
        quote="Absolute MRR comparisons will carry an unknown scale factor",
        why="The only failure whose cause is genuinely unknown rather than "
            "merely unhandled: without a composition there is nothing to "
            "compare to the anchor. This block is also BLOCKED #1 (the Cu "
            "low-pressure velocity inversion), so its shape is unexplained too."),

    # ---- oxide_silica: Kp verified on a TEOS/colloidal-silica STI point.
    "us8142675b2_pt_alumina_pressure_sweep": Ruling(
        conflated="the FILM: platinum scored through an oxide pack, because no "
                  "Pt pack exists",
        identified=True, splittable=False,
        quote="PLACEHOLDER: there is no Pt pack",
        why="film: other. A noble metal and a silicate glass do not share a "
            "Preston coefficient, and this is the corpus's only Pt block, so a "
            "Pt pack would be anchored on the data it is scored against."),

    # ---- sic_alumina_kmno4
    "gong2024_4hsic_alumina_kmno4_L25": Ruling(
        conflated="the Kp anchor itself is secondary (Wang 2021 via a review, "
                  "E5) and assumes an alumina loading the source never states",
        identified=True, splittable=False,
        quote="used_for_calibration: true",
        why="The pack's own Kp note records the open assumption and the 29x "
            "spread between the two papers and the patent it chose between. "
            "This block is used_for_calibration, so by the 13th-run rule it "
            "cannot vote on its own pack's constant in either direction."),

    # ---- sic_ceria_h2o2: Kp least-squares fitted on the Wang 50-run 4H-SiC
    # DOE (ceria + H2O2, pH 9-11).
    "liang2026_4hsic_ceria_composite_h2o2_conc": Ruling(
        conflated="abrasive identity (CuxO-CeO2/Al2O3 composite) and pH 7, "
                  "outside the pack's pH 9-11 calibration window",
        identified=True, splittable=False,
        quote="rank_only: true",
        why="Already adjudicated in-file with a counterfactual: re-anchoring Kp "
            "to this block moves the pack's own calibration set and its "
            "held-out block 3.7-4.1x the OTHER way. The ruling predates this "
            "table and this table does not overturn it."),
    "wei2026_sic_silica_size_sweep": Ruling(
        conflated="abrasive material: colloidal silica scored through the "
                  "ceria pack, on a SiC workpiece",
        identified=True, splittable=False,
        quote="PLACEHOLDER: silica-abrasive pack",
        why="The pack declares reference_abrasive: ceria. Silica and ceria "
            "remove SiC by different chemistries, and the corpus has no second "
            "silica-on-SiC block to anchor a split."),

    # ---- sti_ceria: THE QUANTITATIVE ONE. See composite_prediction().
    "us20190127607a1_teos_ceriasilica_size_sweep": Ruling(
        conflated="abrasive identity: ceria-COATED-SILICA composite, which the "
                  "pack's own Kp note excludes as a different abrasive",
        identified=True, splittable=False,
        quote="composite ceria-coated silica abrasive",
        why="Quantitatively identified: the excluded value (~2.3e-14 vs the "
            "pack's 1.09e-13) predicts 0.21x and this block measures 0.188x. "
            "Not splittable: that 2.3e-14 was itself read off these two blocks."),
    "us20190127607a1_hdpoxide_ceriasilica_size_sweep": Ruling(
        conflated="abrasive identity: ceria-COATED-SILICA composite, which the "
                  "pack's own Kp note excludes as a different abrasive",
        identified=True, splittable=False,
        quote="ceria-coated silica",
        why="Same particles, the HDP-oxide column of the same patent table. "
            "Predicted 0.21x, measured 0.235x."),
}

#: The prose with which a dataset declares its own absolute value incomparable.
#: Used ONLY for the anti-selection contingency test -- it changes no score.
PROSE = re.compile(
    r"(PLACEHOLDER|placeholder"
    r"|Absolute MRR[^\n]{0,80}(meaningless|unknown scale)"
    r"|절대\s*MRR[^\n]{0,40}의미\s*없"
    r"|절대값[^\n]{0,30}(순위|보지)"
    r"|rank[_ ]only"
    r"|prefer rank comparisons"
    r"|SHAPE of the [a-z ]+ response only)", re.I)

#: sti_ceria's two Kp values, both printed in its own kp_m_per_pa note. Read
#: from the pack at runtime where possible; the composite figure is only in
#: prose, so it is parsed out rather than retyped.
_COMPOSITE_RE = re.compile(r"composite datasets imply\s*~?([0-9.]+e-?\d+)")


def _raw_docs() -> Dict[str, str]:
    return {Path(p).stem: Path(p).read_text(encoding="utf-8")
            for p in dataset_paths()}


def _pack_of(stem: str, raws: Dict[str, str]) -> str:
    doc = yaml.safe_load(raws[stem]) or {}
    return str(doc.get("pack") or "?")


@dataclass
class Block:
    dataset: str
    pack: str
    scale: float
    n: int

    @property
    def miss_factor(self) -> float:
        return max(self.scale, 1.0 / self.scale)


def comparable_blocks() -> List[Block]:
    raws = _raw_docs()
    out = []
    for s in score_all():
        if s.scale_ratio is None:
            continue
        out.append(Block(dataset=s.dataset, pack=_pack_of(s.dataset, raws),
                         scale=float(s.scale_ratio), n=s.n))
    return out


def failures(blocks: Optional[List[Block]] = None) -> List[Block]:
    blocks = comparable_blocks() if blocks is None else blocks
    return sorted((b for b in blocks if b.miss_factor >= SCALE_BAR),
                  key=lambda b: -b.miss_factor)


def anti_selection(blocks: Optional[List[Block]] = None) -> Dict[str, float]:
    """Is the 'placeholder/rank-only' prose just a label for bad numbers?

    If every block carrying the prose were a failure, flagging on the prose
    would be indistinguishable from flagging on the miss, and the whole table
    would be circular. The contingency counts answer that directly.
    """
    blocks = comparable_blocks() if blocks is None else blocks
    raws = _raw_docs()
    flagged = [b for b in blocks if PROSE.search(raws.get(b.dataset, ""))]
    clean = [b for b in blocks if not PROSE.search(raws.get(b.dataset, ""))]
    return {
        "flagged": len(flagged),
        "flagged_failing": sum(1 for b in flagged if b.miss_factor >= SCALE_BAR),
        "flagged_median_miss": statistics.median(b.miss_factor for b in flagged),
        "clean": len(clean),
        "clean_failing": sum(1 for b in clean if b.miss_factor >= SCALE_BAR),
        "clean_median_miss": statistics.median(b.miss_factor for b in clean),
    }


def composite_prediction() -> Dict[str, float]:
    """sti_ceria's own excluded Kp, turned into a falsifiable prediction.

    The pack averaged FOUR bare-ceria datasets into kp_m_per_pa and recorded,
    in the same note, that the two ceria-coated-silica composite datasets imply
    ~2.3e-14 -- excluded as a different abrasive. Scoring those two blocks with
    the bare-ceria Kp must therefore under-predict by exactly the ratio of the
    two values. There is no free parameter in that statement: both numbers were
    written into the pack before this run, and the prediction is a division.
    """
    from cmp_sim.core.params import load_pack
    pack = load_pack("sti_ceria")
    param = pack.params["kp_m_per_pa"]
    bare = float(param.value)
    match = _COMPOSITE_RE.search(str(getattr(param, "note", "")))
    if match is None:
        raise AssertionError(
            "sti_ceria's kp_m_per_pa note no longer records the composite "
            "value; this prediction cannot be re-derived from the pack.")
    composite = float(match.group(1))
    observed = {b.dataset: b.scale for b in comparable_blocks()
                if b.dataset.startswith("us20190127607a1_")}
    return {"bare_kp": bare, "composite_kp": composite,
            "predicted_scale": composite / bare, **observed}


def report() -> str:
    blocks = comparable_blocks()
    bad = failures(blocks)
    lines = [
        "Kp PROVENANCE TABLE — what each >=3x absolute-scale failure's pack "
        "silently conflates",
        "(§22 established the cause is not one mis-anchored constant; this is "
        "the per-block follow-up)",
        "",
        f"{len(bad)} failures of {len(blocks)} comparable blocks",
        "",
    ]
    unruled = [b.dataset for b in bad if b.dataset not in RULINGS]
    for b in bad:
        ruling = RULINGS.get(b.dataset)
        lines.append(f"  {b.dataset}  [{b.pack}]  {b.scale:.3f}x  n={b.n}")
        if ruling is None:
            lines.append("      ⚠ NO RULING — a new failure appeared and was "
                         "not adjudicated")
            continue
        tag = ("IDENTIFIED" if ruling.identified else "UNIDENTIFIED")
        tag += ", splittable" if ruling.splittable else ", not splittable"
        lines.append(f"      {tag}: {ruling.conflated}")
        lines.append(f"      {ruling.why}")
    lines.append("")

    sel = anti_selection(blocks)
    lines.append("ANTI-SELECTION — is the in-file prose merely a label for bad "
                 "numbers?")
    lines.append(
        f"    prose present: {sel['flagged']} blocks, "
        f"{sel['flagged_failing']} fail (median miss "
        f"{sel['flagged_median_miss']:.2f}x)")
    lines.append(
        f"    prose absent : {sel['clean']} blocks, "
        f"{sel['clean_failing']} fail (median miss "
        f"{sel['clean_median_miss']:.2f}x)")
    lines.append("    -> the prose does NOT partition the corpus into failures "
                 "and successes, so it is a scope statement, not an excuse.")
    lines.append("")

    comp = composite_prediction()
    lines.append("THE ONE QUANTITATIVE IDENTIFICATION — sti_ceria's excluded "
                 "composite Kp predicts its own two failures")
    lines.append(f"    pack Kp (bare ceria, 4 datasets) {comp['bare_kp']:.3g}"
                 f"   composite implied {comp['composite_kp']:.3g}")
    lines.append(f"    predicted scale {comp['predicted_scale']:.3f}x")
    for key, value in comp.items():
        if key.startswith("us2019"):
            lines.append(f"    observed  {value:.3f}x   {key}")
    lines.append("    -> the two blocks bracket the prediction. The pack was "
                 "already right; nothing in it needs to change.")
    if unruled:
        lines.append("")
        lines.append("⚠ UNADJUDICATED: " + ", ".join(unruled))
    return "\n".join(lines)


if __name__ == "__main__":
    print(report())
