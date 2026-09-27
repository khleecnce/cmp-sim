"""List the vetoed runs and their measured branch (30th run bookkeeping)."""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__))))

import yaml

from plastic_branch_exponent_probe import dataset_branches
from cmp_sim.api import run_recipe
from cmp_sim.core.predictive_score import _recipe_for
from cmp_sim.core.validation import dataset_paths

branches = dataset_branches()
vetoed = []
for path in dataset_paths():
    doc = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    conds = doc.get("conditions") or []
    if not conds:
        continue
    try:
        result = run_recipe(_recipe_for(doc, conds[0]))
    except Exception:
        continue
    regime = result.get("abrasive_regime") or {}
    if regime.get("branch_outside_scope"):
        vetoed.append((path.stem, branches.get(path.stem)))

print(f"vetoed runs: {len(vetoed)}")
for name, branch in sorted(vetoed, key=lambda r: str(r[1])):
    print(f"  {str(branch):12s} {name}")
