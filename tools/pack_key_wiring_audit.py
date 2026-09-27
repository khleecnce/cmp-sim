"""Audit: does every pack key the solver ASKS FOR actually exist in a pack?

This is a MEASUREMENT script, not production code. It modifies nothing.

WHY THIS EXISTS
---------------
Three wiring bugs found in the 26th and 27th runs share one shape: a key name
the engine reads does not match the key name the packs declare, and NOTHING
FAILS. ``p_or(key, default)`` returns the default, the layer quietly takes its
"no data" branch, and the run still produces a plausible number.

* ``ph_acid_mechanical_floor`` -- reachable only through a branch a later
  clamp had made unreachable (26th run).
* ``scratch_threshold_nm`` -- declared by all twelve packs, shadowed by a
  hardcoded module constant that happened to hold the SAME value, so no
  prediction was wrong and no test could ever notice (27th run).
* ``pad_glazing_rate`` / ``pad_conditioning_rate`` -- asked for by the solver,
  declared by no pack under those names (the packs call them
  ``stab_glaze_rate_per_min`` / ``stab_cond_recovery_rate_per_min``), so the
  steady-state pad balance had NEVER executed (27th run).

All three would have been caught by the one cheap static question this script
asks. It needs no measurement, no corpus and no solver run: it is a name
comparison.

METHOD
------
1. Parse every ``p_or("...")`` / ``p("...")`` / ``pack.params.get("...")``
   literal out of the engine source with the ``ast`` module -- not a regex,
   because a regex cannot tell a key from a substring of a docstring.
2. Collect every key declared by any shipped pack (with a non-null value).
3. Report asked-for keys that NO pack declares.

READING THE RESULT
------------------
An orphan is not automatically a bug. Three legitimate reasons exist and are
distinguished by the reader, not by this tool:

``owner input``
    The key is supplied at call time by the user's recipe rather than by a
    pack (an override knob). Legitimate.
``declared gap``
    No pack has the data yet, and the engine's fallback branch is the honest
    "not measured" path. Legitimate, and usually paired with a warning.
``misspelling``
    The value EXISTS in the packs under another name. This is the bug class
    above, and the tell is that a near-miss name is present in the pack key
    list. The report prints the closest pack keys for exactly this reason.

Usage: ``python tools/pack_key_wiring_audit.py``
"""
from __future__ import annotations

import ast
import difflib
import os
import sys
from typing import Dict, List, Set, Tuple

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE)

from cmp_sim.core.params import load_pack           # noqa: E402
from cmp_sim.core.predictive_score import PACK_FILM  # noqa: E402

#: Call names whose FIRST string argument is a pack key.
_KEY_READERS = {"p_or", "p", "has", "param", "get_param"}

#: ``<something>.params.get("key")`` is the other spelling.
_PARAMS_GET = "get"


def _asked_keys(root: str) -> Dict[str, List[str]]:
    """Every pack key read by the engine, mapped to where it is read."""
    found: Dict[str, List[str]] = {}
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d != "__pycache__"]
        for name in filenames:
            if not name.endswith(".py"):
                continue
            path = os.path.join(dirpath, name)
            try:
                tree = ast.parse(open(path, encoding="utf-8").read())
            except SyntaxError:
                continue
            for node in ast.walk(tree):
                if not isinstance(node, ast.Call) or not node.args:
                    continue
                first = node.args[0]
                if not isinstance(first, ast.Constant) or \
                        not isinstance(first.value, str):
                    continue
                func = node.func
                hit = False
                if isinstance(func, ast.Attribute):
                    if func.attr in _KEY_READERS:
                        hit = True
                    elif func.attr == _PARAMS_GET and \
                            isinstance(func.value, ast.Attribute) and \
                            func.value.attr == "params":
                        hit = True
                elif isinstance(func, ast.Name) and func.id in _KEY_READERS:
                    hit = True
                if hit:
                    where = f"{os.path.relpath(path, HERE)}:{node.lineno}"
                    found.setdefault(first.value, []).append(where)
    return found


def _declared_keys() -> Tuple[Set[str], Set[str]]:
    """(keys any pack declares, keys any pack declares with a non-null value)."""
    all_keys: Set[str] = set()
    valued: Set[str] = set()
    for pack_name in PACK_FILM:
        try:
            pack = load_pack(pack_name)
        except Exception:
            continue
        for key, param in pack.params.items():
            all_keys.add(key)
            if getattr(param, "value", None) is not None:
                valued.add(key)
    return all_keys, valued


def main() -> int:
    asked = _asked_keys(os.path.join(HERE, "cmp_sim"))
    declared, valued = _declared_keys()

    orphans = {k: v for k, v in asked.items() if k not in declared}
    null_only = {k: v for k, v in asked.items()
                 if k in declared and k not in valued}

    print(f"engine reads {len(asked)} distinct pack keys; "
          f"packs declare {len(declared)} ({len(valued)} with a value)\n")

    print(f"── ORPHANS: read by the engine, declared by NO pack "
          f"({len(orphans)}) ──")
    print("   these are where a silent 'no data' branch may be hiding a "
          "misspelling\n")
    for key in sorted(orphans):
        near = difflib.get_close_matches(key, sorted(declared), n=3, cutoff=0.6)
        print(f"  {key}")
        print(f"      read at: {', '.join(orphans[key][:3])}")
        if near:
            print(f"      ⚠ packs declare similar: {', '.join(near)}")
    if not orphans:
        print("  (none)")

    print(f"\n── DECLARED BUT NULL EVERYWHERE ({len(null_only)}) ──")
    print("   the key exists, no pack has a value: an honest declared gap\n")
    for key in sorted(null_only):
        print(f"  {key}")
    if not null_only:
        print("  (none)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
