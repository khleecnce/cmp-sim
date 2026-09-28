r"""Has anyone ever PRICED the fitted size exponent against the derived one? (58th run)

WHY THIS PROBE EXISTS
---------------------
`docs/limits.md` §55 withdrew a fitted concentration exponent and let the
engine's own three-factor decomposition supply `n_C = p(1-alpha*chi)` instead.
It scored 0 blocks worse and 3 better -- a constant DELETED while the fit
improved -- and the generalisation it recorded was:

    ask of every pack constant whether the engine already DERIVES the same
    quantity and the pack is merely overriding it.

`abrasive_size_exponent` is the immediate second instance, and structurally the
same one: `models/luo_dornfeld.mechanical_factor` computes
`n_d = -q(1-alpha*chi)+beta` from the resolved contact regime and then, if the
pack declares `measured_size_exponent`, throws it away.  Six packs declare one.
Nobody has ever measured what the derivation would have said.

WHAT THIS PROBE IS NOT ASKING
-----------------------------
NOT "should the size term be a richer function family?".  §54 already measured
that and closed it: the non-monotone blocks' in-sample family floor (6.86%) is
BETTER than the monotone ones' (8.19%), so the monotone power law is not where
the size error lives.  The only open question is WHICH NUMBER goes in the
exponent -- a pack's fit, or the engine's derivation.

METHOD (nothing is wired; no pack is modified)
----------------------------------------------
For every scored dataset, run the SHIPPING solver twice:

  shipping    exactly as it runs today
  derived     with `abrasive_size_exponent` overridden to None through the
              ordinary `params` path, so `mechanical_factor` falls back to
              `regime.n_size`

and report shape MAPE AND absolute scale for both -- both, always, because
shape alone has bought this repository a 13x-wrong rate for a better trend
number before.

Blocks that do not vary particle size are reported too, and separately: the
exponent still acts on them through `(d/d_ref)^n` whenever the formulation's
diameter differs from the pack reference, so "unchanged" there is a fact about
the reference condition, not about the exponent.

The verdict rule is the one §55 pinned, and it is deliberately asymmetric: a
derived value is adopted BECAUSE it is derived, and only if it is not worse.
"0 blocks worse" is not a licence to scan exponents -- if the derivation is
worse, the fit stays and the disagreement is recorded.

Run:  .venv/bin/python tools/size_exponent_derivation_price.py
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import statistics  # noqa: E402
from typing import Any, Dict, List, Optional, Tuple  # noqa: E402

import yaml  # noqa: E402

from cmp_sim.core import predictive_score as ps  # noqa: E402
from cmp_sim.core.params import load_pack  # noqa: E402
from cmp_sim.core.validation import dataset_paths  # noqa: E402

KEY = "abrasive_size_exponent"

#: Row-level keys naming the particle diameter.
SIZE_ALIASES = ("abrasive_size_nm", "abrasive_d50_nm", "abrasive_d99_nm")


def _shape_and_scale(doc: Dict[str, Any], rows: List[Dict[str, Any]],
                     override: Any, set_override: bool
                     ) -> Optional[Tuple[float, float]]:
    """(shape MAPE %, median measured/predicted) with one free scale.

    The scale is fitted exactly as `predictive_score.score_dataset` fits it,
    so this probe and the headline cannot drift apart.
    """
    measured: List[float] = []
    predicted: List[float] = []
    for row in rows:
        r = dict(row)
        if set_override:
            ov = dict(r.get("overrides") or {})
            ov[KEY] = override
            r["overrides"] = ov
        value = ps._predict(doc, r)
        m = ps._measured(row)
        if not value or m is None:
            return None
        measured.append(m)
        predicted.append(value)
    if len(measured) < 3:
        return None
    scale = (sum(m * p for m, p in zip(measured, predicted))
             / sum(p * p for p in predicted))
    shape = (100.0 * sum(abs(scale * p - m) / m
                         for m, p in zip(measured, predicted)) / len(measured))
    ratios = sorted(m / p for m, p in zip(measured, predicted))
    return shape, ratios[len(ratios) // 2]


def _varies_size(rows: List[Dict[str, Any]]) -> bool:
    for key in SIZE_ALIASES:
        if len({(r.get("overrides") or {}).get(key) for r in rows}) > 1:
            return True
    return False


def measure() -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    for path in dataset_paths():
        try:
            doc = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        except Exception:                                # noqa: BLE001
            continue
        pack_name = str(doc.get("pack") or "")
        if not pack_name:
            continue
        try:
            pack = load_pack(pack_name)
        except Exception:                                # noqa: BLE001
            continue
        param = pack.params.get(KEY)
        declared = None if param is None else getattr(param, "value", None)
        if declared is None:
            continue                                     # already derived
        rows = [r for r in (doc.get("conditions") or [])
                if ps._measured(r) is not None]
        if len(rows) < 3:
            continue
        before = _shape_and_scale(doc, rows, None, False)
        after = _shape_and_scale(doc, rows, None, True)
        if before is None or after is None:
            continue
        out.append({
            "dataset": path.stem,
            "pack": pack_name,
            "owner": getattr(param, "owner", None),
            "declared": float(declared),
            "held_out": not bool(doc.get("used_for_calibration")),
            "varies_size": _varies_size(rows),
            "shape_before": before[0], "scale_before": before[1],
            "shape_after": after[0], "scale_after": after[1],
        })
    return out


def report(rows: Optional[List[Dict[str, Any]]] = None) -> str:
    rows = measure() if rows is None else rows
    lines = ["blocks predicted by a pack DECLARING %s : %d" % (KEY, len(rows)),
             "",
             "  %-46s %-22s %7s   %8s -> %-8s  %7s -> %-7s"
             % ("dataset", "pack", "n_pack", "shape", "shape", "scale", "scale")]
    for r in sorted(rows, key=lambda r: r["shape_after"] - r["shape_before"]):
        mark = ""
        d = r["shape_after"] - r["shape_before"]
        if d < -0.05:
            mark = "  BETTER"
        elif d > 0.05:
            mark = "  WORSE"
        lines.append("  %-46s %-22s %+7.3f   %7.2f%% -> %-7.2f%% %7.3f -> %-7.3f%s%s"
                     % (r["dataset"][:46], r["pack"][:22], r["declared"],
                        r["shape_before"], r["shape_after"],
                        r["scale_before"], r["scale_after"],
                        "" if r["varies_size"] else "  [size fixed]", mark))

    better = [r for r in rows if r["shape_after"] < r["shape_before"] - 0.05]
    worse = [r for r in rows if r["shape_after"] > r["shape_before"] + 0.05]
    lines += ["", "  better with the DERIVED exponent : %d" % len(better),
              "  worse  with the DERIVED exponent : %d" % len(worse),
              "  unchanged                        : %d"
              % (len(rows) - len(better) - len(worse))]
    if rows:
        lines.append("  median shape  shipping %.2f%%  derived %.2f%%"
                     % (statistics.median([r["shape_before"] for r in rows]),
                        statistics.median([r["shape_after"] for r in rows])))
    lines += ["",
              "VERDICT RULE (§55, deliberately asymmetric): a derived value is",
              "  adopted BECAUSE it is derived and only if it is not worse. If",
              "  the derivation is worse, the fit stays and the disagreement is",
              "  recorded -- 'not worse' is never a licence to scan exponents."]
    return "\n".join(lines)


if __name__ == "__main__":                                # pragma: no cover
    print(report())
