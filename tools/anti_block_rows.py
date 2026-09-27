"""What the two `anti` blocks actually look like, row by row.

`span_direction_probe` classifies a block `anti` when log(predicted) correlates
NEGATIVELY with log(measured) across the rows of a single-axis sweep.  That is
a classification; before any of it can be called physics the rows have to be
printed, because two very different situations produce a negative correlation:

  * the model's peaked term places its optimum on the WRONG SIDE of the swept
    range, so the prediction descends where the measurement climbs.  That is a
    statement about a constant (the declared optimum) and it is falsifiable.
  * the measurement barely moves at all, so its ordering is noise and any
    prediction correlates with it arbitrarily.  A negative r on a flat
    measurement is not a model error; it is the absence of a measurement.

The second case is the one that would waste a session, and it is separated by
comparing the measured span against the publication's own stated reproducibility
where the dataset records one.  Nothing is fitted and nothing is proposed here.

Run: .venv/bin/python tools/anti_block_rows.py
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from cmp_sim.core.predictive_score import _measured, _predict  # noqa: E402
from tools.span_direction_probe import _load, classify, survey  # noqa: E402


def main() -> int:
    anti = [b for b in survey() if classify(b) == "anti"]
    if not anti:
        print("no `anti` block in this corpus -- nothing to print.")
        return 0
    for b in anti:
        doc = _load(b["dataset"])
        rows = [r for r in (doc.get("conditions") or [])
                if _measured(r) is not None]
        axis = b["axis"]
        print("=" * 78)
        print("%s   axis %s   r_log %.2f   span_ratio %.2fx"
              % (b["dataset"], axis, b["r_log"], b["span_ratio"]))
        print("  film %s   pack %s" % (doc.get("film"), doc.get("pack")))
        print("  %-12s %12s %12s %8s" % (axis, "measured", "predicted", "ratio"))
        ms, qs = [], []
        for r in rows:
            v = _predict(doc, r)
            m = _measured(r)
            lvl = (r.get("overrides") or {}).get(axis, r.get(axis))
            ms.append(m)
            qs.append(v)
            print("  %-12s %12.1f %12.1f %8.2fx"
                  % (lvl, m, v, (v / m) if m else float("nan")))
        print("  measured span %.2fx   predicted span %.2fx"
              % (max(ms) / min(ms), max(qs) / min(qs)))
        rep = doc.get("reproducibility_pct") or doc.get("stated_reproducibility_pct")
        print("  stated reproducibility: %s"
              % ("%s%%" % rep if rep is not None else "not stated in this file"))
        print("  -> measured span is %s the stated scatter"
              % ("NOT comparable to (unstated)" if rep is None
                 else "%.1fx" % ((max(ms) / min(ms) - 1.0) * 100.0 / float(rep))))
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
