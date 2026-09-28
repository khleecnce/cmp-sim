r"""Can a pack constant still be REFUTED by anything the model predicts? (58th run)

WHY THIS PROBE EXISTS
---------------------
`docs/limits.md` §55 found a fitted constant whose evidence had LEFT: the
dataset it was fitted on was re-assigned to another pack (ruling #49-B), the
citation still resolved, the grade still read `literature`, the value still
acted -- and nothing broke.  The generalisation recorded there is

    *a constant's evidence can leave without the constant noticing.*

§55 repaired ONE instance.  This probe asks the class question, and it asks it
in the direction no reader here has: **for every live pack constant, is there
still anything in the scored corpus that could contradict it?**

`tools/calibration_flag_audit.py` reads the same citations and asks the
OPPOSITE question -- "is this citation self-grading?" -- and it deliberately
EXCUSES a cross-pack citation as ordinary evidence reuse (its `own_pack`
filter; §46 got that false positive first and the excuse is correct there).
That excuse is exactly the blind spot here: a citation the audit waves through
as harmless reuse may be the constant's ONLY evidence, in which case the
constant has become unfalsifiable inside its own reach.

WHAT IS MEASURED (nothing is wired; no pack and no dataset is modified)
-----------------------------------------------------------------------
For every constant a pack OWNS, with a live numeric value:

  reach      the set of packs whose EFFECTIVE parameter of that name is this
             very object (`param.owner == pack`).  Computed by loading every
             pack, so inheritance and shadowing are accounted for exactly
             rather than guessed from `base:` chains.
  cited      dataset stems named by the constant's `source:` field.  `note:`
             is read but reported separately: §46 established that a note may
             cite the dataset that REFUTED a constant, and counting that as
             provenance reports honesty as circularity.
  home /     a cited dataset whose CURRENT `pack:` is inside the reach, versus
  departed   one that has moved outside it.
  testable   scored, held-out datasets inside the reach that sweep an axis
             this constant governs -- i.e. rows whose prediction the constant
             actually moves and whose measurement could disagree with it.

A constant with `testable == 0` cannot be contradicted by this corpus.  That
is not automatically a defect -- it is a QUESTION, and the probe says so in
its own output.  Three innocent reasons exist and are separated here:

  * the constant is a REFERENCE value (`*_ref_*`, `reference_*`): it defines
    the normalisation point, so it is 1.0 by construction and has no residual
    to be wrong about;
  * its axis is genuinely absent from the corpus (nothing to sweep);
  * it is deliberately cross-system, and its note SAYS so.

Only the fourth case -- a value claimed as measured in THIS system, whose
evidence now lives under another pack, with nothing left in reach to test it
-- is the §55 class.

Run:  .venv/bin/python tools/departed_evidence_census.py
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from dataclasses import dataclass, field  # noqa: E402
from typing import Any, Dict, List, Optional, Set  # noqa: E402

import yaml  # noqa: E402

from cmp_sim.core.params import available_packs, load_pack  # noqa: E402
from cmp_sim.core.predictive_score import score_all  # noqa: E402
from cmp_sim.core.validation import dataset_paths  # noqa: E402
from tools.calibration_flag_audit import CONSTANT_AXES  # noqa: E402

#: Phrases by which a constant's own note DECLARES that it is knowingly
#: transferred from another chemistry. A constant that says so is not the §55
#: class however far its evidence has moved: it never claimed to have been
#: measured in the system it acts on, so "no block in reach can refute it" is
#: the state it was written in rather than a decay. The probe must read this,
#: because the alternative is condemning a correctly-declared transfer -- the
#: §46 false positive recurring one level up.
CROSS_SYSTEM_PHRASES = (
    "cross-system", "cross system", "transfers across", "another chemistry",
    "not a calibrated value for this slurry", "separate pack",
    "borrow", "placeholder", "substituted",
)

#: Name fragments marking a constant that DEFINES the reference condition.
#: Every factor is exactly 1.0 there by the repository's central contract, so
#: such a value carries no residual and cannot be refuted by a rate. Excluding
#: them is not charity: scoring them would be scoring the normalisation.
REFERENCE_FRAGMENTS = ("reference_", "_ref_", "_ref", "ref_")


def _axes_for(constant: str) -> Set[str]:
    out: Set[str] = set()
    for frag, axes in CONSTANT_AXES.items():
        if frag in constant:
            out |= axes
    return out


def _is_reference(constant: str) -> bool:
    return any(f in constant for f in REFERENCE_FRAGMENTS)


@dataclass
class Finding:
    pack: str
    constant: str
    value: Any
    reach: List[str]
    cited_source: List[str] = field(default_factory=list)
    cited_note_only: List[str] = field(default_factory=list)
    home: List[str] = field(default_factory=list)
    departed: List[str] = field(default_factory=list)
    testable: List[str] = field(default_factory=list)
    axes: Set[str] = field(default_factory=set)
    declares_cross_system: bool = False

    @property
    def unfalsifiable(self) -> bool:
        return not self.testable

    @property
    def klass(self) -> str:
        if _is_reference(self.constant):
            return "reference-condition"
        if not self.axes:
            return "no-axis-mapping"
        if self.testable:
            return "testable"
        if self.departed and not self.home:
            return ("declared-cross-system" if self.declares_cross_system
                    else "DEPARTED-AND-UNTESTABLE")
        return "untestable-no-sweep-in-reach"


def _dataset_docs() -> Dict[str, dict]:
    return {Path(p).stem: (yaml.safe_load(Path(p).read_text(encoding="utf-8")) or {})
            for p in dataset_paths()}


def _reach_table() -> Dict[str, Dict[str, List[str]]]:
    """key -> owning pack -> packs whose EFFECTIVE param is that owner's."""
    table: Dict[str, Dict[str, List[str]]] = {}
    for pack_name in sorted(available_packs()):
        try:
            pack = load_pack(pack_name)
        except Exception:                                # noqa: BLE001
            continue
        for key, param in pack.params.items():
            owner = getattr(param, "owner", None)
            if owner is None:
                continue
            table.setdefault(key, {}).setdefault(owner, []).append(pack_name)
    return table


def collect() -> List[Finding]:
    docs = _dataset_docs()
    scored = {s.dataset: s for s in score_all()}
    stems = sorted(docs, key=len, reverse=True)
    reach_table = _reach_table()

    out: List[Finding] = []
    for pack_name in sorted(available_packs()):
        try:
            pack = load_pack(pack_name)
        except Exception:                                # noqa: BLE001
            continue
        for key, param in sorted(pack.params.items()):
            if getattr(param, "owner", pack_name) != pack_name:
                continue
            value = getattr(param, "value", None)
            if value is None or isinstance(value, bool) \
                    or not isinstance(value, (int, float)):
                continue                                  # withdrawn, or a flag
            source = str(getattr(param, "source", "") or "")
            note = str(getattr(param, "note", "") or "")
            reach = sorted(set(reach_table.get(key, {}).get(pack_name, [pack_name])))
            axes = _axes_for(key)

            cited_src, cited_note = [], []
            seen: Set[str] = set()
            for stem in stems:
                if stem in seen:
                    continue
                if re.search(re.escape(stem), source):
                    seen.add(stem)
                    cited_src.append(stem)
                elif re.search(re.escape(stem), note):
                    seen.add(stem)
                    cited_note.append(stem)

            home = [s for s in cited_src
                    if str(docs[s].get("pack") or "") in reach]
            departed = [s for s in cited_src
                        if str(docs[s].get("pack") or "") not in reach]

            testable = []
            for stem, doc in docs.items():
                if str(doc.get("pack") or "") not in reach:
                    continue
                if doc.get("used_for_calibration"):
                    continue                               # answer key, not a test
                sc = scored.get(stem)
                if sc is None or getattr(sc, "shape_mape", None) is None:
                    continue
                if axes & set(getattr(sc, "axes", []) or []):
                    testable.append(stem)

            out.append(Finding(pack=pack_name, constant=key, value=value,
                               reach=reach, cited_source=cited_src,
                               cited_note_only=cited_note, home=home,
                               departed=departed, testable=sorted(testable),
                               axes=axes,
                               declares_cross_system=any(
                                   p in note.lower()
                                   for p in CROSS_SYSTEM_PHRASES)))
    return out


def report(findings: Optional[List[Finding]] = None) -> str:
    fs = collect() if findings is None else findings
    by_class: Dict[str, List[Finding]] = {}
    for f in fs:
        by_class.setdefault(f.klass, []).append(f)

    lines = ["live numeric pack constants examined : %d" % len(fs)]
    for k in sorted(by_class):
        lines.append("  %-28s : %d" % (k, len(by_class[k])))

    lines += ["",
              "THIS IS A SHORTLIST OF QUESTIONS, NOT A BUG LIST.",
              "  A constant with no testable block in reach may be a correct",
              "  cross-system transfer whose note says so, or an axis this",
              "  corpus simply does not sweep. The probe cannot read intent;",
              "  it reports reach, evidence and testability and stops."]

    hot = by_class.get("DEPARTED-AND-UNTESTABLE", [])
    lines += ["", "DEPARTED-AND-UNTESTABLE -- the §55 class: every cited block "
                  "now sits outside", "  this constant's reach, nothing in "
                  "reach sweeps its axis, AND the note does",
              "  not declare the transfer"]
    if not hot:
        lines.append("  none.")
    docs = _dataset_docs()
    for f in sorted(hot, key=lambda f: (f.pack, f.constant)):
        lines.append("  %s.%s = %r" % (f.pack, f.constant, f.value))
        lines.append("      reach     : %s" % ", ".join(f.reach))
        lines.append("      departed  : %s" % ", ".join(
            "%s -> %s" % (s, docs[s].get("pack")) for s in f.departed))

    declared = by_class.get("declared-cross-system", [])
    lines += ["", "declared-cross-system -- evidence is outside the reach and "
                  "the note SAYS so;",
              "  untestable by construction, not by decay"]
    if not declared:
        lines.append("  none.")
    for f in sorted(declared, key=lambda f: (f.pack, f.constant)):
        lines.append("  %-28s.%-26s departed=%s"
                     % (f.pack, f.constant, ",".join(f.departed)))

    lines += ["", "DEPARTED but still testable -- the citation moved, the "
                  "constant can still be wrong"]
    moved = [f for f in fs if f.departed and f.testable]
    if not moved:
        lines.append("  none.")
    for f in sorted(moved, key=lambda f: (f.pack, f.constant)):
        lines.append("  %-28s.%-26s departed=%d  testable=%d"
                     % (f.pack, f.constant, len(f.departed), len(f.testable)))

    lines += ["", "untestable-no-sweep-in-reach -- home evidence exists, but "
                  "no scored held-out",
              "  block under this constant's reach varies its axis"]
    quiet = by_class.get("untestable-no-sweep-in-reach", [])
    for f in sorted(quiet, key=lambda f: (f.pack, f.constant)):
        lines.append("  %-28s.%-26s reach=%s"
                     % (f.pack, f.constant, ",".join(f.reach)))
    if not quiet:
        lines.append("  none.")
    return "\n".join(lines)


if __name__ == "__main__":                                # pragma: no cover
    print(report())
