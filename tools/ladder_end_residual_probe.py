"""Is the worst row of a block systematically its LOWEST point on a ladder?

Two of the three cheapest median crossers are each carried by one row, both at
the low end of their swept axis and both OVER-predicted (+57.7% at 1 wt%,
+95.4% at 1 psi).  Two blocks is an anecdote.  This asks the whole corpus the
structural question instead: for every block that sweeps a single axis, where
does the largest residual sit -- at the bottom of the ladder, the top, or
nowhere in particular -- and with which sign?

Why it matters: a MAPE spread evenly over rows is a wrong law (needs a new
term everywhere), while a MAPE concentrated at one END of every ladder is a
missing CURVATURE with a KNOWN SIGN, which is a derivation target.  A null
result here is equally useful: it closes the "one universal low-end
correction" search before any physics is written, the same way the centred
scale-miss census closed the "one universal factor" search.

Fits nothing, changes no pack.  Run: .venv/bin/python tools/ladder_end_residual_probe.py
"""

from __future__ import annotations

import sys
from collections import Counter
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from cmp_sim.core.predictive_score import (  # noqa: E402
    _measured, _predict, _varying_axes, score_all,
)

ROOTS = (Path("cmp_sim/data/validation/datasets"),
         Path("legacy/validation/datasets"))


def _load(name: str):
    for root in ROOTS:
        p = root / (name + ".yaml")
        if p.exists():
            return yaml.safe_load(p.read_text(encoding="utf-8"))
    return None


def _axis_value(row, axis):
    ov = row.get("overrides") or {}
    if axis in ov:
        return ov[axis]
    return row.get(axis)


def block_report(name: str):
    """Residual position of the worst row on a single-axis block, or None."""
    doc = _load(name)
    if not doc:
        return None
    rows = [r for r in (doc.get("conditions") or [])
            if _measured(r) is not None]
    axes = _varying_axes(rows)
    # A multi-axis block has no "bottom of the ladder" -- the question is not
    # even well posed there, so it is excluded rather than answered badly.
    if len(axes) != 1 or len(rows) < 3:
        return None
    axis = axes[0]
    m, q, xs = [], [], []
    for r in rows:
        v = _predict(doc, r)
        x = _axis_value(r, axis)
        if v is None or not isinstance(x, (int, float)):
            return None
        m.append(_measured(r))
        q.append(v)
        xs.append(float(x))
    scale = sum(a * b for a, b in zip(m, q)) / sum(b * b for b in q)
    res = [100.0 * (scale * b - a) / a for a, b in zip(m, q)]
    worst = max(range(len(res)), key=lambda i: abs(res[i]))
    order = sorted(range(len(xs)), key=lambda i: xs[i])
    rank = order.index(worst)  # 0 = lowest point on the axis
    where = ("bottom" if rank == 0 else
             "top" if rank == len(xs) - 1 else "middle")
    return {
        "dataset": name,
        "axis": axis,
        "n": len(m),
        "mape": sum(abs(x) for x in res) / len(res),
        "worst_residual": res[worst],
        "where": where,
        "sign": "over" if res[worst] > 0 else "under",
    }


def main() -> int:
    scored = [s for s in score_all() if s.shape_mape is not None]
    out = [b for b in (block_report(s.dataset) for s in scored) if b]
    out.sort(key=lambda b: -b["mape"])

    print("single-axis blocks with a scorable shape: %d of %d scored\n"
          % (len(out), len(scored)))
    print("%-46s %-20s %4s %6s %8s %7s %6s"
          % ("dataset", "axis", "n", "MAPE", "worst", "where", "sign"))
    for b in out:
        print("%-46s %-20s %4d %5.1f%% %+7.1f%% %7s %6s"
              % (b["dataset"][:46], b["axis"][:20], b["n"], b["mape"],
                 b["worst_residual"], b["where"], b["sign"]))

    pos = Counter(b["where"] for b in out)
    sign = Counter(b["sign"] for b in out)
    n = len(out)
    print()
    print("WHERE the worst row sits (uniform expectation for n rows is")
    print("  bottom = top = 1/n each; 'middle' collects the rest)")
    for k in ("bottom", "middle", "top"):
        print("  %-7s %2d  (%.0f%%)" % (k, pos[k], 100.0 * pos[k] / n))
    print("SIGN of that worst residual")
    for k in ("over", "under"):
        print("  %-7s %2d  (%.0f%%)" % (k, sign[k], 100.0 * sign[k] / n))

    bottom_over = sum(1 for b in out
                      if b["where"] == "bottom" and b["sign"] == "over")
    print()
    print("bottom AND over-predicted : %d of %d (%.0f%%)"
          % (bottom_over, n, 100.0 * bottom_over / n))
    # Expected share under the null "worst row is uniform, sign is a coin":
    exp = sum(1.0 / b["n"] for b in out) / 2.0
    print("expected under a uniform-position / fair-sign null : %.1f" % exp)
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
