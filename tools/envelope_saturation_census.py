r"""Is the plausibility envelope a READER, or has it already saturated? (60th run)

WHY THIS PROBE EXISTS
---------------------
`tools/scale_only_jurisdiction_probe.py` asked which reader grades §57's 14
`scale-only` constants, and for the two with no scored reader it fell back to
`core/sanity.py` -- the film-level plausibility envelope, which needs no dataset
and so can see a constant nothing else grades. For `si_substrate_alkaline.
kp_m_per_pa` it reported that the envelope "first complains at **x1**": the
UNPERTURBED shipping prediction is already outside. A reader that is already
complaining carries no information about the constant, because every
perturbation looks the same to it.

So the fallback was worthless there, and the question became much bigger than
the constant that raised it: **on how much of the corpus is the last reader
already saturated?** Nothing had ever counted, because `check_rate` is an
annotation on a single run and no probe here reads it across the corpus.

Answer: on **30 of 48** scored blocks at least one row's predicted rate is
outside its film's envelope. The envelope is not a spare reader waiting to be
used; on most of the corpus it is a warning that is always on.

THE SPLIT THAT MAKES IT A FINDING RATHER THAN A COUNT
-----------------------------------------------------
An out-of-envelope PREDICTION means two entirely different things depending on
the MEASUREMENT at the same row, and the envelope cannot tell them apart:

  `envelope-too-narrow`  the measured rate is outside too. Then the source is
                         reporting rates the envelope does not admit, and the
                         warning is about the ENVELOPE, not the model. This is
                         the larger class and it is not a model defect at all --
                         e.g. the `us9200180b2` Cu series measures 86-542 A/min
                         against a 1,000-12,000 A/min envelope built from
                         production damascene recipes.
  `model-scale-failure`  the measured rate is INSIDE and the prediction is not.
                         This is what the envelope was built to catch, and here
                         it does: `gong2024` is outside on 25 of 25 rows (its
                         absolute scale is 0.07x, §34's worst).

⚠ NEITHER CLASS IS A REASON TO WIDEN AN ENVELOPE. Every bound in
`core/sanity.py` cites a measurement, and the module's own header records that
the `snag` entry was DELETED for citing nothing -- "a guard that cannot fire is
worse than no guard". Widening an envelope so a block stops warning would
recreate exactly that. The deliverable here is the count and the split, so that
no future session mistakes a saturated annotation for an independent check.

WHAT WOULD RESOLVE the `envelope-too-narrow` class: a per-film envelope derived
from the corpus's own MEASURED rates rather than from review prose. That is a
real option and is deliberately NOT taken here, because it would make the guard
circular -- it would then be unable to report that a corpus block is itself
unusual.

Run:  .venv/bin/python tools/envelope_saturation_census.py
"""
from __future__ import annotations

import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import yaml  # noqa: E402

from cmp_sim.core import predictive_score as PS  # noqa: E402
from cmp_sim.core.sanity import PLAUSIBLE_RATE_A_PER_MIN, check_rate  # noqa: E402
from cmp_sim.core.validation import dataset_paths  # noqa: E402


@dataclass
class BlockEnvelope:
    dataset: str
    film: str
    rows: int = 0
    #: predicted outside, measured outside too -> the envelope is too narrow here
    too_narrow: int = 0
    #: predicted outside, measured inside -> a model scale failure, correctly caught
    model_failure: int = 0
    worst_predicted: Optional[float] = None
    envelope: Optional[Tuple[float, float]] = None

    @property
    def has_envelope(self) -> bool:
        return self.envelope is not None

    @property
    def fires(self) -> bool:
        return (self.too_narrow + self.model_failure) > 0

    @property
    def klass(self) -> str:
        if not self.has_envelope:
            return "no-envelope"
        if not self.fires:
            return "silent"
        if self.model_failure and self.too_narrow:
            return "mixed"
        return "model-scale-failure" if self.model_failure else "envelope-too-narrow"


def collect() -> List[BlockEnvelope]:
    out: List[BlockEnvelope] = []
    for p in dataset_paths():
        path = Path(p)
        doc = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        film = str(doc.get("film") or "").lower()
        entry = PLAUSIBLE_RATE_A_PER_MIN.get(film)
        be = BlockEnvelope(dataset=path.stem, film=film or "(unset)",
                           envelope=None if entry is None else (entry[0], entry[1]))
        for row in (doc.get("conditions") or []):
            measured = PS._measured(row)
            if measured is None:
                continue
            try:
                predicted = PS._predict(doc, row)
            except Exception:  # noqa: BLE001
                continue
            if not predicted:
                continue
            be.rows += 1
            if entry is None:
                continue
            if not check_rate(film, float(predicted)):
                continue
            if be.worst_predicted is None or abs(
                    float(predicted)) > abs(be.worst_predicted):
                be.worst_predicted = float(predicted)
            if check_rate(film, float(measured)):
                be.too_narrow += 1
            else:
                be.model_failure += 1
        out.append(be)
    return out


def summary(blocks: Optional[List[BlockEnvelope]] = None) -> Dict[str, int]:
    bs = collect() if blocks is None else blocks
    counts: Dict[str, int] = {}
    for b in bs:
        counts[b.klass] = counts.get(b.klass, 0) + 1
    counts["blocks"] = len(bs)
    counts["firing"] = sum(1 for b in bs if b.fires)
    return counts


def report(blocks: Optional[List[BlockEnvelope]] = None) -> str:
    bs = collect() if blocks is None else blocks
    counts = summary(bs)
    lines = [
        "scored blocks : %d   envelope FIRES on : %d"
        % (counts["blocks"], counts["firing"]),
        "",
        "WHAT AN OUT-OF-ENVELOPE PREDICTION MEANS depends on the MEASUREMENT at",
        "the same row, and core/sanity.py cannot tell the two apart:",
        "  envelope-too-narrow   measured is outside too -> the warning is about",
        "                        the ENVELOPE, not the model. Not a defect.",
        "  model-scale-failure   measured is INSIDE -> exactly what the guard",
        "                        was built to catch.",
        "  mixed                 both kinds of row in one block.",
        "  no-envelope           no published bound for this film; core/sanity.py",
        "                        says so rather than inventing one.",
        "",
        "⚠ NOT a licence to widen an envelope: every bound cites a measurement,",
        "  and the deleted `snag` entry is this module's own precedent that a",
        "  guard which cannot fire is worse than no guard.",
        "",
    ]
    for k in ("model-scale-failure", "mixed", "envelope-too-narrow",
              "no-envelope", "silent"):
        group = sorted([b for b in bs if b.klass == k],
                       key=lambda b: -(b.model_failure + b.too_narrow))
        lines.append("%s -- %d" % (k, len(group)))
        if not group:
            lines.append("  none.")
        for b in group:
            env = ("%.0f-%.0f" % b.envelope) if b.envelope else "(none)"
            lines.append(
                "  %-52s %-8s rows=%-3d out: model=%-3d narrow=%-3d "
                "envelope=%-12s worst=%s"
                % (b.dataset, b.film, b.rows, b.model_failure, b.too_narrow,
                   env,
                   "-" if b.worst_predicted is None
                   else "%.0f" % b.worst_predicted))
        lines.append("")
    return "\n".join(lines)


if __name__ == "__main__":                                # pragma: no cover
    print(report())
