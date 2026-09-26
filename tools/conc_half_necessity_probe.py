"""Probe: is ``abrasive_conc_half_wt_pct`` still DOING anything?

This is a MEASUREMENT script, not production code. It touches no pack.

WHY THIS QUESTION EXISTS
------------------------
Every pack that carries ``abrasive_conc_half_wt_pct`` justifies it the SAME
way in its own note: without the constant the model's log-log concentration
slope was about +1.0 while the measurements show +0.15..+0.53, so a saturating
(Langmuir / site-occupancy) form was introduced to bend it down.

That justification was written while ``models/luo_dornfeld.mechanical_factor``
applied the active-particle COUNT ratio N(C)/N(C_ref) directly on the
saturating branch — i.e. MRR ~ N^1, which asserts chi = 0 (no load sharing)
against the chi = 1.0 the same call resolves. The 2026-09-27 load-sharing fix
restores MRR ~ N^(1 - alpha*chi) on BOTH branches, which also lowers the
POWER-LAW branch's slope to n_C = p*(1 - alpha*chi).

So the constant's stated job may already be done by the corrected exponent.
A fitted constant whose justification has been withdrawn is a liability: it
still absorbs residual, but no longer for the reason anyone can state.

WHAT IS MEASURED (no fitting, no new constants)
-----------------------------------------------
For every iso-condition loading series in the corpus (>= 3 distinct wt% with
every other process axis held), the MODEL is run at each condition twice — with
the pack's C_half and with it forced to null — and a power law is fitted to the
MODEL's own predictions. The MEASURED slope of the same series is fitted the
same way. Three numbers per series:

    m_data          the measurement's slope
    m_with_chalf    the model's slope, constant present
    m_without       the model's slope, constant absent

The constant is NECESSARY on a series only if removing it pushes the model
OUTSIDE the measured band that it was inside with the constant. If the model
is already inside the band without it, the constant is doing nothing that can
be defended from the note it carries.

Slopes are scale-free, so the unknown per-dataset Kp scale drops out — the same
shape-only rule used everywhere else in this repo.

CAVEAT recorded up front: a local power law fitted across a saturation knee is
a CHORD slope, not a limiting exponent. That biases both model slopes the same
way (both are fitted on the same wt% points), so the comparison between them is
fair even though neither is a limiting exponent.
"""
from __future__ import annotations

import glob
import os
import sys
from typing import Any, Dict, List, Optional

import yaml

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE)

from size_derived_probe import _mrr, fit_power  # noqa: E402
from conc_derived_probe import GROUP_AXES, _conc  # noqa: E402

from cmp_sim.core import predictive_score as ps  # noqa: E402

DATASET_DIR = os.path.join(HERE, "cmp_sim", "data", "validation", "datasets")


def _groups_with_rows() -> List[dict]:
    """Iso-condition loading series, keeping the RAW rows so they can be re-run."""
    out: List[dict] = []
    for path in sorted(glob.glob(os.path.join(DATASET_DIR, "*.yaml"))):
        name = os.path.basename(path)[:-5]
        if name.startswith("_"):
            continue
        doc = yaml.safe_load(open(path)) or {}
        groups: Dict[tuple, List[dict]] = {}
        for cond in doc.get("conditions", []):
            c = _conc(cond)
            rate = _mrr(cond)
            if c is None or rate is None or c <= 0 or rate <= 0:
                continue
            ov = cond.get("overrides", {}) or {}
            merged = {**cond, **ov}
            key = tuple(merged.get(k) for k in GROUP_AXES)
            groups.setdefault(key, []).append(cond)
        for _key, rows in groups.items():
            if len({_conc(r) for r in rows}) < 3:
                continue
            out.append({"dataset": name, "doc": doc, "pack": doc.get("pack"),
                        "rows": rows})
    return out


def _model_slope(doc: Dict[str, Any], rows: List[dict],
                 kill_chalf: bool) -> Optional[float]:
    """Fit a power law to the MODEL's predictions across the series."""
    pts = []
    for row in rows:
        c = _conc(row)
        r = dict(row)
        if kill_chalf:
            # The override path the solver already honours, so this measures
            # the SHIPPING code path rather than a special branch.
            ov = dict(r.get("overrides") or {})
            ov["abrasive_conc_half_wt_pct"] = None
            r["overrides"] = ov
        try:
            pred = ps._predict(doc, r)
        except Exception:
            return None
        if not pred or pred <= 0 or c is None:
            return None
        pts.append((c, pred))
    if len({c for c, _ in pts} ) < 3:
        return None
    m, _r2 = fit_power(sorted(pts))
    return m


def main() -> int:
    from cmp_sim.core.params import load_pack

    print(f"{'dataset':45s} {'pack':22s} {'m_data':>7s} {'r2':>5s} "
          f"{'m_with':>7s} {'m_without':>9s}  verdict")
    verdicts: Dict[str, int] = {}
    for g in _groups_with_rows():
        pack_name = g["pack"]
        try:
            chalf = load_pack(pack_name).get_or("abrasive_conc_half_wt_pct", None)
        except Exception:
            chalf = None
        if chalf is None:
            continue                     # the constant is not in play here
        data_pts = sorted((_conc(r), _mrr(r)) for r in g["rows"])
        m_data, r2 = fit_power(data_pts)
        m_with = _model_slope(g["doc"], g["rows"], kill_chalf=False)
        m_without = _model_slope(g["doc"], g["rows"], kill_chalf=True)
        if m_with is None or m_without is None:
            continue
        # "Inside the band" = within the measurement's own fit quality. A
        # tolerance of 0.25 in the exponent is the same window the sibling
        # probe (conc_derived_probe.global_law_scope) uses for +1/3.
        inside_with = abs(m_with - m_data) <= 0.25
        inside_without = abs(m_without - m_data) <= 0.25
        if inside_with and not inside_without:
            v = "NEEDED"
        elif inside_without and not inside_with:
            v = "HARMFUL"
        elif inside_without and inside_with:
            v = "redundant"
        else:
            v = "both-miss"
        verdicts[v] = verdicts.get(v, 0) + 1
        print(f"{g['dataset'][:45]:45s} {str(pack_name)[:22]:22s} "
              f"{m_data:+7.3f} {r2:5.2f} {m_with:+7.3f} {m_without:+9.3f}  {v}")
    print()
    print("verdicts:", verdicts)
    print("NEEDED = removing the constant pushes the model out of the measured "
          "band; that is the only verdict that justifies keeping a fitted value.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
