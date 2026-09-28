r"""Which READER grades a `scale-only` constant -- or does nobody? (60th run)

WHY THIS PROBE EXISTS
---------------------
`tools/quiet_constant_response_probe.py` (§57) sorted 35 quiet constants by
perturbing them through the shipping scorer, and its largest surviving class was
left as an open question: **14 constants are `scale-only`.** The predicted RATE
moves (up to 929 % here), and every block's `shape_mape` is EXACTLY unchanged.

That is not a corpus shortage and no amount of new data repairs it. It is a
property of the reader: the headline score fits one free multiplicative scale
per dataset (§34), so a constant that only rescales a block's predictions is
divided straight back out. `kp_m_per_pa` is the pure case -- it multiplies every
rate, so the published median can NEVER test it, however many blocks sweep P
and V.

§34 already established that shape and absolute scale are DIFFERENT failures
and must not be merged. It also established that `absolute_scale_audit` is the
**only** reader here that looks at the rate itself. So the question §57 left is
answerable and is not about the median at all:

    for each `scale-only` constant, does a reader exist that can see it move?

Three outcomes, and separating them IS the result:

  `scale-graded`   a held-out, absolute-scale-comparable block sits inside the
                   constant's reach AND its scale ratio moves under an
                   admissible perturbation. The constant is falsifiable -- by
                   `absolute_scale_audit`, not by the headline median. That
                   division of labour is a fact about this repository that was
                   written down nowhere before this probe.
  `ungraded`       the rate moves and no SCORED reader can see it: every block
                   in reach is either fitted on (`used_for_calibration`, §46) or
                   forbids absolute comparison (`_forbids_absolute_comparison`
                   -- its own source says the rates are not comparable). Such a
                   constant is unfalsifiable inside this repository while
                   looking, in every report, exactly like a graded one.
                   ⚠ For these the probe then asks the LAST reader (below),
                   because "no reader at all" and "only a 30x-wide envelope"
                   are different statements and only one of them is true here.
  `scale-inert`    a comparable block exists in reach but the scale ratio does
                   not move. Cannot happen for a purely multiplicative
                   constant and is reported as a probe/consistency failure
                   rather than a finding.

⚠ THIS IS NOT A PROPOSAL TO SCORE ON SCALE. §34 measured that the two failures
are independent and that re-anchoring trades one for the other. The deliverable
is a DECLARATION of jurisdiction, so that "the median cannot test this" stops
being invisible.

THE LAST READER (asked only of the `ungraded` set) -- AND IT IS ALREADY SPENT
-----------------------------------------------------------------------------
`core/sanity.py` annotates every run whose absolute rate leaves its film's
published envelope, and it needs no dataset at all -- so in principle it can see
a constant that no scored block grades. It is a much weaker reader by
construction: the envelopes are deliberately order-of-magnitude ("meant to catch
10x errors, not 30% ones"), so a constant reaching it is bounded, not measured.

MEASURED, it is weaker than that. For `si_substrate_alkaline.kp_m_per_pa` the
envelope "first complains at x1" -- the UNPERTURBED shipping prediction (8,830
A/min against a 100-3,000 envelope) is already outside, so every perturbation
looks identical to it and the reader carries ZERO information about the constant.
That raised a question nobody here had asked, because `check_rate` is a
per-run annotation that no probe reads across the corpus:
`tools/envelope_saturation_census.py` finds the envelope firing on **30 of 52**
scored blocks. The last reader is not a spare check waiting to be used; on most
of the corpus it is a warning that is always on.

So for the two ungraded constants the honest verdict is NO READER, by two
different mechanisms: one film (`dlc`) has no published envelope at all, and the
other's envelope is saturated.

INSTRUMENT CONTROL (§43 -- a probe with no control decays into "nothing moves")
------------------------------------------------------------------------------
`kp_m_per_pa` has an ANALYTIC answer, so the probe can be checked rather than
trusted: it multiplies every predicted rate by the same factor, and the scale
ratio is `median(measured/predicted)`, so perturbing it by `f` must move
`log10(scale)` by exactly `-log10(f)` on every comparable block. Five of the
fourteen are `kp_m_per_pa`; if any of them comes back off that value, the
probe -- not the pack -- is wrong. `control_residuals()` reports it.

PERTURBATION RULES (§43): both directions, small factors first, largest
admissible response kept, so a constant is called inert only when NO admissible
perturbation reaches it.

NOTHING IS WIRED. No pack and no dataset is modified; perturbations travel
through the documented `params:` owner-override path, in memory.

Run:  .venv/bin/python tools/scale_only_jurisdiction_probe.py
"""
from __future__ import annotations

import math
import statistics
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import yaml  # noqa: E402

from cmp_sim.core import predictive_score as PS  # noqa: E402
from cmp_sim.core.sanity import PLAUSIBLE_RATE_A_PER_MIN, check_rate  # noqa: E402
from cmp_sim.core.validation import dataset_paths  # noqa: E402
from tools.quiet_constant_response_probe import (  # noqa: E402
    PERTURBATIONS,
    measure as quiet_measure,
)

#: Below this a block's absolute scale is unmoved, in DECADES of
#: log10(measured/predicted). `absolute_scale_audit` prints the ratio to two
#: decimals, so anything under this is invisible to the reader being tested.
SCALE_TOLERANCE_DECADES = 1e-3

#: The class §57 left open.
SOURCE_CLASS = "scale-only"

#: The analytic control: these constants multiply every predicted rate.
MULTIPLICATIVE_CONTROLS = ("kp_m_per_pa",)

#: Factors at which the envelope reader is asked whether it fires, ascending in
#: |log10 f| so the FIRST hit is the smallest error `core/sanity.py` can catch.
#: Deliberately reaches far beyond the §43 scoring ladder: the question here is
#: not "is this constant wired" (already answered) but "how wrong could it be
#: before anything at all complains", and the honest answer may be 10x.
ENVELOPE_FACTORS: Tuple[float, ...] = (
    1.05, 0.95, 1.25, 0.8, 1.6, 0.625, 2.0, 0.5, 3.0, 1 / 3.0,
    5.0, 0.2, 10.0, 0.1, 30.0, 1 / 30.0, 100.0, 0.01,
)


def _docs() -> Dict[str, Tuple[Path, dict]]:
    out: Dict[str, Tuple[Path, dict]] = {}
    for p in dataset_paths():
        path = Path(p)
        out[path.stem] = (path, yaml.safe_load(path.read_text(encoding="utf-8")) or {})
    return out


def _scale_comparable(doc: dict) -> bool:
    """Can `absolute_scale_audit` read this block at all?

    Two exclusions, and they are different claims. `used_for_calibration` is
    the §46 rule: a block the constant was fitted on cannot refute it, because
    moving the constant moves the answer key with the answer.
    `_forbids_absolute_comparison` is the dataset's OWN statement that its
    rates are not comparable in absolute terms -- a fact about the source, not
    about the model. Both make the block unusable as evidence; neither is a
    defect.
    """
    if doc.get("used_for_calibration"):
        return False
    return not PS._forbids_absolute_comparison(doc)


def _scale_ratio_with(doc: dict,
                      override: Optional[Dict[str, Any]]) -> Optional[float]:
    """median(measured/predicted) for one dataset under an override.

    Deliberately mirrors `predictive_score._scale_ratio`, which is what
    `absolute_scale_audit` reads, rather than inventing a second definition of
    absolute scale: the point of the probe is to answer whether THAT reader can
    see the constant, so it must be that reader's statistic.
    """
    work = dict(doc)
    if override:
        merged = dict(doc.get("pack_overrides") or {})
        merged.update(override)
        work["pack_overrides"] = merged
    rows = [r for r in (work.get("conditions") or []) if PS._measured(r) is not None]
    if len(rows) < 3:
        return None
    return PS._scale_ratio(work, rows)


@dataclass
class Jurisdiction:
    pack: str
    constant: str
    value: float
    reach: List[str]
    rate_pct: float
    #: held-out blocks in reach whose absolute scale is comparable
    comparable: List[str] = field(default_factory=list)
    #: blocks in reach excluded, with the reason
    excluded: Dict[str, str] = field(default_factory=dict)
    scale_decades: float = 0.0
    scale_perturbation: Optional[float] = None
    #: largest |scale ratio| reached, to show whether the 3x audit bar is crossed
    crosses_audit_bar: bool = False
    #: for the ungraded set only: the film, whether an envelope exists for it,
    #: and the smallest perturbation factor at which `check_rate` complains.
    film: Optional[str] = None
    envelope: Optional[Tuple[float, float]] = None
    envelope_fires_at: Optional[float] = None

    @property
    def klass(self) -> str:
        if not self.comparable:
            return "ungraded"
        if self.scale_decades < SCALE_TOLERANCE_DECADES:
            return "scale-inert"
        return "scale-graded"

    @property
    def is_control(self) -> bool:
        return self.constant in MULTIPLICATIVE_CONTROLS

    @property
    def last_reader(self) -> str:
        """What, if anything, bounds an `ungraded` constant."""
        if self.envelope is None:
            return ("NO READER AT ALL -- no published envelope for film "
                    "'%s' (core/sanity.py declines to invent one)" % self.film)
        if self.envelope_fires_at == 1.0:
            return ("NO READER -- the envelope %.0f-%.0f A/min is ALREADY "
                    "firing on the UNPERTURBED run, so every perturbation "
                    "looks identical to it (tools/envelope_saturation_census"
                    ".py: 30 of 52 blocks)"
                    % (self.envelope[0], self.envelope[1]))
        if self.envelope_fires_at is None:
            return ("envelope %.0f-%.0f A/min never fires up to x%g -- "
                     "unbounded within the probed range"
                     % (self.envelope[0], self.envelope[1],
                        max(ENVELOPE_FACTORS)))
        return ("envelope %.0f-%.0f A/min first complains at x%g "
                "(order-of-magnitude bound, not a measurement)"
                % (self.envelope[0], self.envelope[1], self.envelope_fires_at))


def measure(limit: Optional[int] = None) -> List[Jurisdiction]:
    docs = _docs()
    quiet = [q for q in quiet_measure() if q.klass == SOURCE_CLASS]
    if limit is not None:
        quiet = quiet[:limit]

    out: List[Jurisdiction] = []
    for q in quiet:
        j = Jurisdiction(pack=q.pack, constant=q.constant, value=q.value,
                         reach=list(q.reach), rate_pct=q.rate_pct)
        base: Dict[str, float] = {}
        for stem in q.blocks:
            _path, doc = docs[stem]
            if doc.get("used_for_calibration"):
                j.excluded[stem] = "used_for_calibration"
                continue
            if PS._forbids_absolute_comparison(doc):
                j.excluded[stem] = "source forbids absolute comparison"
                continue
            ratio = _scale_ratio_with(doc, None)
            if ratio is None or ratio <= 0:
                j.excluded[stem] = "no absolute scale ratio"
                continue
            base[stem] = ratio
            j.comparable.append(stem)
        j.comparable.sort()

        for factor in PERTURBATIONS:
            override = {q.constant: q.value * factor}
            for stem, b in base.items():
                _path, doc = docs[stem]
                p = _scale_ratio_with(doc, override)
                if p is None or p <= 0:
                    continue
                d = abs(math.log10(p) - math.log10(b))
                if d > j.scale_decades:
                    j.scale_decades = d
                    j.scale_perturbation = factor
                if max(p, 1.0 / p) >= 3.0 and max(b, 1.0 / b) < 3.0:
                    j.crosses_audit_bar = True

        if not j.comparable:
            _measure_envelope(j, q.blocks, docs)
        out.append(j)
    return out


def _predicted_rates(doc: dict,
                     override: Optional[Dict[str, Any]]) -> List[float]:
    work = dict(doc)
    if override:
        merged = dict(doc.get("pack_overrides") or {})
        merged.update(override)
        work["pack_overrides"] = merged
    rates: List[float] = []
    for row in (work.get("conditions") or []):
        if PS._measured(row) is None:
            continue
        try:
            value = PS._predict(work, row)
        except Exception:  # noqa: BLE001
            continue
        if value:
            rates.append(float(value))
    return rates


def _measure_envelope(j: Jurisdiction, blocks: List[str],
                      docs: Dict[str, Tuple[Path, dict]]) -> None:
    """The LAST reader: at what perturbation does `core/sanity.py` complain?

    Asked only where no scored block grades the constant. Deliberately uses the
    dataset's OWN conditions (a real operating point this repository holds a
    measurement for) rather than an invented recipe, so the answer is about this
    corpus and not about a condition nobody published. A film with no envelope
    entry gets `envelope = None`, which `last_reader` reports as no reader at
    all -- the honest outcome, and the one a blank line would hide.
    """
    for stem in blocks:
        _path, doc = docs[stem]
        film = str(doc.get("film") or "").lower()
        if not film:
            continue
        j.film = film
        entry = PLAUSIBLE_RATE_A_PER_MIN.get(film)
        if entry is None:
            j.envelope = None
            return
        j.envelope = (entry[0], entry[1])
        base = _predicted_rates(doc, None)
        if not base:
            continue
        # Ascending in |log10 f|, so the first hit is the SMALLEST error the
        # envelope can catch. A base run already outside its envelope would
        # make every factor "fire"; guard against reporting that as a reader.
        if any(check_rate(film, r) for r in base):
            j.envelope_fires_at = 1.0
            return
        for factor in sorted(ENVELOPE_FACTORS, key=lambda f: abs(math.log10(f))):
            rates = _predicted_rates(doc, {j.constant: j.value * factor})
            if any(check_rate(film, r) for r in rates):
                j.envelope_fires_at = factor
                return
        return


def control_residuals(results: List[Jurisdiction]) -> List[Tuple[str, float]]:
    """How far each multiplicative control is from its ANALYTIC response.

    `kp_m_per_pa` scales every predicted rate, so the largest admissible
    perturbation must move log10(scale) by exactly log10 of that factor. The
    probe keeps the LARGEST response, which is therefore the largest |log10 f|
    over the admissible set. A non-zero residual means the probe (or the
    override path) is not doing what this docstring says.
    """
    expected = max(abs(math.log10(f)) for f in PERTURBATIONS)
    out = []
    for r in results:
        if not r.is_control or not r.comparable:
            continue
        out.append((f"{r.pack}.{r.constant}", r.scale_decades - expected))
    return out


def report(results: Optional[List[Jurisdiction]] = None) -> str:
    rs = measure() if results is None else results
    by: Dict[str, List[Jurisdiction]] = {}
    for r in rs:
        by.setdefault(r.klass, []).append(r)

    lines = [
        "scale-only constants examined (§57's open class) : %d" % len(rs),
        "",
        "THE QUESTION",
        "  A `scale-only` constant moves the predicted RATE and leaves every",
        "  block's shape_mape EXACTLY unchanged, because the headline score",
        "  fits one free multiplicative scale per dataset (§34). So the median",
        "  can never test it. Which reader can?",
        "",
        "  scale-graded  a held-out, absolute-scale-comparable block in reach",
        "                moves -> falsifiable by absolute_scale_audit.",
        "  ungraded      the rate moves and NO reader sees it: every block in",
        "                reach is fitted on, or its own source forbids",
        "                absolute comparison.",
        "  scale-inert   comparable block exists, scale does not move --",
        "                impossible for a multiplicative constant; a probe",
        "                failure, not a finding.",
        "",
        "perturbations (§43, both directions, small first): %s" %
        ", ".join("x%g" % f for f in PERTURBATIONS),
        "",
    ]
    for k in ("ungraded", "scale-inert", "scale-graded"):
        group = sorted(by.get(k, []), key=lambda r: (-r.scale_decades, -r.rate_pct))
        lines.append("%s -- %d" % (k, len(group)))
        if not group:
            lines.append("  none.")
        for r in group:
            lines.append(
                "  %-28s.%-30s rate %8.3f%%  scale %6.3f dec (x%-5s) "
                "comparable=%d%s"
                % (r.pack, r.constant, r.rate_pct, r.scale_decades,
                   ("%g" % r.scale_perturbation) if r.scale_perturbation else "-",
                   len(r.comparable),
                   "  CROSSES 3x BAR" if r.crosses_audit_bar else ""))
            if r.klass == "ungraded" and r.excluded:
                for stem, why in sorted(r.excluded.items()):
                    lines.append("        excluded %-52s %s" % (stem, why))
            if r.klass == "ungraded":
                lines.append("        last reader: %s" % r.last_reader)
        lines.append("")

    ctl = control_residuals(rs)
    lines.append("INSTRUMENT CONTROL -- kp_m_per_pa is analytically "
                 "multiplicative, so its response must equal log10 of the")
    lines.append("largest admissible perturbation (%.4f decades) on every "
                 "comparable block." % max(abs(math.log10(f))
                                           for f in PERTURBATIONS))
    if not ctl:
        lines.append("  ⚠ NO CONTROL RECOVERED -- treat the whole table as "
                     "unverified.")
    for name, residual in sorted(ctl):
        lines.append("  %-44s residual %+0.2e %s"
                     % (name, residual,
                        "OK" if abs(residual) < 1e-9 else "⚠ PROBE SUSPECT"))

    graded = by.get("scale-graded", [])
    ungraded = by.get("ungraded", [])
    lines.append("")
    lines.append("VERDICT  %d of %d scale-only constants have a reader "
                 "(absolute_scale_audit); %d have none."
                 % (len(graded), len(rs), len(ungraded)))
    if graded:
        lines.append("         median scale response of the graded set: "
                     "%.3f decades" %
                     statistics.median([r.scale_decades for r in graded]))
    return "\n".join(lines)


if __name__ == "__main__":                                # pragma: no cover
    print(report())
