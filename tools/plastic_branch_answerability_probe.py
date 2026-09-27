"""Is the alpha-chi veto ANSWERABLE on this corpus?

The 29th run found that 33 of 49 runs discard a MEASURED contact branch because
alpha*chi > 1 breaks the structural bound. Before the 30th run re-reads the
derivation, ask the cheap question: does the corpus contain a concentration
sweep on a film whose branch is plastic or transition? That is the one
observation that could say whether n_C there is really near zero.
"""
import collections

import yaml

from cmp_sim.api import run_recipe
from cmp_sim.core.predictive_score import _recipe_for
from cmp_sim.core.validation import dataset_paths

rows = []
for path in dataset_paths():
    doc = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    conds = doc.get("conditions") or []
    if not conds:
        continue
    try:
        result = run_recipe(_recipe_for(doc, conds[0]))
    except Exception:
        continue
    sit = result.get("situation") or {}
    branch = sit.get("contact_branch")
    # Which axes does this dataset actually sweep?
    #
    # The swept values live under `overrides`, NOT at the condition's top
    # level -- the first cut of this probe read only the top level and
    # reported ZERO plastic-branch loading sweeps, i.e. "the veto is
    # unanswerable", which was an artefact of the reader. Top-level keys
    # (pressure_psi, rpm_*) are merged in too, because they are swept there.
    levels = collections.defaultdict(set)
    for c in conds:
        flat = dict(c or {})
        flat.update((c or {}).get("overrides") or {})
        for k, v in flat.items():
            if isinstance(v, (int, float)) and not isinstance(v, bool):
                levels[k].add(v)
    conc_keys = [k for k in levels
                 if "abrasive" in k and ("wt" in k or "conc" in k)
                 and len(levels[k]) >= 3]
    rows.append((path.stem, branch, conc_keys,
                 {k: sorted(levels[k]) for k in conc_keys}))

by_branch = collections.Counter(r[1] for r in rows)
print("branch counts:", dict(by_branch))
print()
print("datasets with a >=3-level abrasive loading sweep, by branch:")
for name, branch, keys, lv in sorted(rows, key=lambda r: str(r[1])):
    if keys:
        print(f"  {branch or '—':12s} {name[:46]:48s} {keys} {lv}")
print()
hits = [r for r in rows if r[2] and r[1] in ("plastic", "transition")]
print(f"=> {len(hits)} plastic/transition datasets carry a >=3-level loading sweep")
if not hits:
    print("   The veto is UNANSWERABLE on this corpus: no concentration sweep "
          "exists on a film whose contact branch is plastic.")
