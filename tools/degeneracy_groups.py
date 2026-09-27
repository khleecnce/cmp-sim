"""Print the tied-prediction groups of one dataset (diagnostic companion to
``input_degeneracy_floor_probe``).

"18 of 18 rows tied" can mean two very different things and the floor number
cannot distinguish them:

* many small groups -- the table lists genuine replicates or a swept axis the
  schema does not carry (an irreducible bound, and honest);
* ONE group of 18 -- the model is predicting a constant across the whole
  dataset, which is the flat-prediction failure ``tools/flat_prediction_census``
  exists to catch, not a floor at all.

Usage:  .venv/bin/python tools/degeneracy_groups.py <dataset-stem>
"""
from __future__ import annotations

import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import yaml

from cmp_sim.core.predictive_score import _measured, _predict_with_gate
from cmp_sim.core.validation import dataset_paths


def main(argv):
    if not argv:
        print(__doc__)
        return 2
    stem = argv[0]
    path = next((p for p in dataset_paths() if p.stem == stem), None)
    if path is None:
        print(f"no dataset named {stem}")
        return 1
    doc = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    rows = [r for r in (doc.get("conditions") or []) if _measured(r) is not None]
    groups = defaultdict(list)
    for row in rows:
        value, _g, _d = _predict_with_gate(doc, row)
        key = "None" if value is None else f"{value:.12e}"
        groups[key].append((row.get("label", "?"), _measured(row)))
    print(f"{stem}: {len(rows)} rows -> {len(groups)} distinct predictions")
    for key, members in sorted(groups.items(), key=lambda kv: -len(kv[1])):
        pred = float(key) if key != "None" else float("nan")
        print(f"\n  prediction {pred:>12.1f}   ({len(members)} rows)")
        for label, m in members:
            print(f"      measured {m:>10.1f}   {label}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
