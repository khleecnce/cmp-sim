r"""What holds a `no sweep in reach` constant in place -- nothing, or the SCORER? (59th run)

WHY THIS PROBE EXISTS
---------------------
`tools/departed_evidence_census.py` (§56) sorted every live pack constant by
whether anything in the scored corpus could still contradict it, and its
largest class was not the headline finding: **35 constants classified
`untestable-no-sweep-in-reach`**. Their evidence is at home -- the datasets
they cite are still predicted by their own pack -- but no scored, held-out
block inside their reach varies the axis they govern, so a wrong value is not
reported by anything.

§56 said that is a QUESTION, not a bug list, and left the question open. This
probe answers it, and the answer is not one answer: the census decided
"testable" from an AXIS MAPPING (`CONSTANT_AXES`, a name-fragment table), which
is a proxy for the thing that matters. The thing that matters is measurable:

    perturb the constant and re-score the held-out blocks in reach through the
    SHIPPING scorer. Does the published number move?

Three outcomes, and separating them IS the result:

  `rate-inert`       no admissible perturbation moves the predicted RATE on any
                     block in reach. The constant is unreachable, which is the
                     §53/§17 class (a cited, graded constant that reaches
                     nothing), NOT §56's. Nothing can refute it because nothing
                     consumes it.
  `scale-only`       the rate moves, but every block's `shape_mape` is
                     unchanged. This is the sharpest class, and it is a
                     property of the SCORER, not of the corpus: the shape score
                     fits one free multiplicative scale per dataset (§34), so a
                     constant that only rescales a block's predictions is
                     divided straight back out. `kp_m_per_pa` is the pure case
                     -- it multiplies every rate -- and the headline median can
                     NEVER test it, however many blocks sweep P and V.
  `shape-testable`   the rate AND the shape score move. The census's axis
                     mapping was too strict for this constant: something in
                     reach does grade it. This is a census false negative and
                     is reported as such.

PERTURBATION RULES (§43 -- the perturbation is part of the instrument)
----------------------------------------------------------------------
Both directions, small factors FIRST, and the largest response over the whole
admissible set is kept, so a constant is called inert only when NO admissible
perturbation reaches it. A large one-sided factor cannot distinguish "no wire"
from "pushed outside the term's own validity window", where the model correctly
refuses and warns.

NOTHING IS WIRED. No pack and no dataset is modified; every perturbation is
applied through the documented `params:` owner-override path, in memory.

Run:  .venv/bin/python tools/quiet_constant_response_probe.py
"""
from __future__ import annotations

import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import yaml  # noqa: E402

from cmp_sim.core import predictive_score as PS  # noqa: E402
from cmp_sim.core.validation import dataset_paths  # noqa: E402
from tools.departed_evidence_census import collect as census_collect  # noqa: E402

#: §43: both directions, small first. The loop keeps the LARGEST response, so
#: a large factor that pushes a term outside its declared validity window
#: cannot make a live constant look inert.
PERTURBATIONS: Tuple[float, ...] = (1.05, 0.95, 1.25, 0.80, 1.60, 0.625)

#: Below this a predicted rate is unmoved. Chosen an order of magnitude above
#: float noise on a rate of order 1e3 A/min.
RATE_TOLERANCE_PCT = 0.05

#: Below this a block's shape MAPE is unmoved. Same bar the flat-prediction
#: census uses for "the scorer cannot tell these apart" (§36).
SHAPE_TOLERANCE_PP = 0.05

#: The class this probe exists to measure.
QUIET_CLASS = "untestable-no-sweep-in-reach"


def _docs() -> Dict[str, Tuple[Path, dict]]:
    out: Dict[str, Tuple[Path, dict]] = {}
    for p in dataset_paths():
        path = Path(p)
        out[path.stem] = (path, yaml.safe_load(path.read_text(encoding="utf-8")) or {})
    return out


def _held_out_blocks_in_reach(reach: List[str],
                              docs: Dict[str, Tuple[Path, dict]]) -> List[str]:
    """Scored, held-out datasets whose pack is inside the constant's reach.

    Held-out, because a block the constant was FITTED on cannot refute it
    (§46): moving the constant moves the answer key with the answer.
    """
    out = []
    for stem, (_path, doc) in docs.items():
        if str(doc.get("pack") or "") not in reach:
            continue
        if doc.get("used_for_calibration"):
            continue
        out.append(stem)
    return sorted(out)


def _score_with(path: Path, doc: dict,
                override: Optional[Dict[str, Any]]) -> Tuple[Optional[float],
                                                             Optional[float]]:
    """(shape_mape, mean predicted rate) for one dataset under an override.

    Re-scores through the SHIPPING scorer rather than re-deriving it, so the
    number this probe reads is the number the README publishes. The override
    travels via `pack_overrides`, which `_recipe_for` funnels into `params:` --
    the documented owner-override path -- and which `setdefault` lets any row
    override win, so a perturbation can never silently replace a MEASURED
    value a dataset states for itself.
    """
    work = dict(doc)
    if override:
        merged = dict(doc.get("pack_overrides") or {})
        merged.update(override)
        work["pack_overrides"] = merged

    rows = [r for r in (work.get("conditions") or []) if PS._measured(r) is not None]
    if len(rows) < 3:
        return None, None
    measured: List[float] = []
    predicted: List[float] = []
    gate_matters = False
    axes = PS._varying_axes(rows)
    gate_matters = any(a in axes for a in ("oxidizer_wt_pct", "h2o2_vol_pct"))
    for row in rows:
        value, gate, _declined = PS._predict_with_gate(work, row)
        if value is None:
            return None, None
        if gate and gate_matters:
            continue
        m = PS._measured(row)
        if m is None:
            continue
        measured.append(float(m))
        predicted.append(value)
    if len(predicted) < 3:
        return None, None
    denom = sum(p * p for p in predicted)
    if denom <= 0:
        return None, None
    scale = sum(m * p for m, p in zip(measured, predicted)) / denom
    shape = PS._mape([(m, scale * p) for m, p in zip(measured, predicted)])
    return shape, sum(predicted) / len(predicted)


@dataclass
class QuietResponse:
    pack: str
    constant: str
    value: float
    reach: List[str]
    blocks: List[str] = field(default_factory=list)
    rate_pct: float = 0.0
    shape_pp: float = 0.0
    rate_perturbation: Optional[float] = None
    shape_perturbation: Optional[float] = None
    runnable_blocks: int = 0

    @property
    def klass(self) -> str:
        if self.runnable_blocks == 0:
            return "unrunnable"
        if self.rate_pct < RATE_TOLERANCE_PCT:
            return "rate-inert"
        if self.shape_pp < SHAPE_TOLERANCE_PP:
            return "scale-only"
        return "shape-testable"


def measure(limit: Optional[int] = None) -> List[QuietResponse]:
    docs = _docs()
    findings = [f for f in census_collect() if f.klass == QUIET_CLASS]
    if limit is not None:
        findings = findings[:limit]

    out: List[QuietResponse] = []
    for f in findings:
        blocks = _held_out_blocks_in_reach(f.reach, docs)
        res = QuietResponse(pack=f.pack, constant=f.constant, value=float(f.value),
                            reach=list(f.reach), blocks=blocks)
        base: Dict[str, Tuple[Optional[float], Optional[float]]] = {}
        for stem in blocks:
            path, doc = docs[stem]
            base[stem] = _score_with(path, doc, None)
        res.runnable_blocks = sum(1 for v in base.values() if v[0] is not None)
        if res.runnable_blocks == 0:
            out.append(res)
            continue

        for factor in PERTURBATIONS:
            override = {f.constant: res.value * factor}
            for stem in blocks:
                b_shape, b_rate = base[stem]
                if b_shape is None or not b_rate:
                    continue
                path, doc = docs[stem]
                p_shape, p_rate = _score_with(path, doc, override)
                if p_shape is None or p_rate is None:
                    continue
                d_rate = 100.0 * abs(p_rate - b_rate) / abs(b_rate)
                d_shape = abs(p_shape - b_shape)
                if d_rate > res.rate_pct:
                    res.rate_pct = d_rate
                    res.rate_perturbation = factor
                if d_shape > res.shape_pp:
                    res.shape_pp = d_shape
                    res.shape_perturbation = factor
        out.append(res)
    return out


def report(results: Optional[List[QuietResponse]] = None) -> str:
    rs = measure() if results is None else results
    by: Dict[str, List[QuietResponse]] = {}
    for r in rs:
        by.setdefault(r.klass, []).append(r)

    lines = [
        "quiet constants examined (%s) : %d" % (QUIET_CLASS, len(rs)),
        "",
        "WHAT THIS SEPARATES",
        "  rate-inert      nothing in reach consumes it -- the §53/§17 class,",
        "                  not §56's. Unfalsifiable because unreachable.",
        "  scale-only      the rate moves and the SHAPE SCORE does not. The",
        "                  scorer fits one free scale per block (§34), so a",
        "                  purely multiplicative constant is divided back out",
        "                  and the headline median can never test it.",
        "  shape-testable  the published number moves: the census's axis",
        "                  mapping was too strict here (a false negative).",
        "",
        "perturbations (§43, both directions, small first): %s" %
        ", ".join("x%g" % f for f in PERTURBATIONS),
        "",
    ]
    for k in ("shape-testable", "scale-only", "rate-inert", "unrunnable"):
        group = sorted(by.get(k, []), key=lambda r: (-r.shape_pp, -r.rate_pct))
        lines.append("%s -- %d" % (k, len(group)))
        if not group:
            lines.append("  none.")
        for r in group:
            lines.append(
                "  %-28s.%-30s rate %7.3f%% (x%-5s) shape %6.3f pp (x%-5s) "
                "blocks=%d"
                % (r.pack, r.constant, r.rate_pct,
                   ("%g" % r.rate_perturbation) if r.rate_perturbation else "-",
                   r.shape_pp,
                   ("%g" % r.shape_perturbation) if r.shape_perturbation else "-",
                   r.runnable_blocks))
        lines.append("")
    return "\n".join(lines)


if __name__ == "__main__":                                # pragma: no cover
    print(report())
