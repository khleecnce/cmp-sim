"""Parameter-pack loader with a two-tier search path.

Reuses the inherited loader primitives (``legacy/sim/params.py``:
``Param``, ``ParamPack``, ``_parse_params``, ``ParamMissing``) instead of
re-deriving them. The only thing added here is the search path: CMP-Sim's own
packs (``cmp_sim/data/params``) take precedence, and anything not overridden
falls through to the inherited packs (``legacy/knowledge/params``).

Every parameter must carry value/unit/source/confidence. Missing constants
raise ``ParamMissing`` — a silent default is a hallucination.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

from cmp_sim.core.legacy_bridge import LEGACY_PACK_DIR, REPO_ROOT  # noqa: F401
from sim.params import Param, ParamMissing, ParamPack, _parse_params  # legacy primitives

OWN_PACK_DIR = REPO_ROOT / "cmp_sim" / "data" / "params"
SEARCH_PATH: List[Path] = [OWN_PACK_DIR, LEGACY_PACK_DIR]

__all__ = ["Param", "ParamPack", "ParamMissing", "load_pack", "available_packs",
           "pack_path", "SEARCH_PATH"]


def pack_path(name: str, after: Optional[Path] = None) -> Path:
    """Locate ``<name>.yaml``, own packs first.

    ``after`` skips search-path entries up to and including the directory the
    given file came from. That is what lets an own pack shadow an inherited one
    of the SAME name and still inherit from it (``base: <its own name>``):
    without it the loader would find itself and report an inheritance cycle.
    """
    dirs = list(SEARCH_PATH)
    if after is not None:
        try:
            dirs = dirs[dirs.index(Path(after)) + 1:]
        except ValueError:
            pass
    for d in dirs:
        p = d / f"{name}.yaml"
        if p.exists():
            return p
    where = [str(d) for d in dirs]
    raise FileNotFoundError(
        f"parameter pack '{name}' not found in {where}. "
        f"available: {available_packs()}"
    )


#: YAML files in the params directory that are databases, not parameter packs
_NON_PACK_FILES = {"additives", "abrasives"}


def available_packs() -> List[str]:
    """Parameter packs only — the additive/abrasive databases are not packs."""
    names = set()
    for d in SEARCH_PATH:
        if d.exists():
            names.update(p.stem for p in d.glob("*.yaml")
                         if p.stem not in _NON_PACK_FILES and not p.stem.startswith("_"))
    return sorted(names)


def load_pack(name: str, _seen: Optional[List[str]] = None,
              _after: Optional[Path] = None) -> ParamPack:
    """Load ``<name>.yaml`` with ``base:`` inheritance, own-dir first.

    A pack may declare ``base:`` with its own name to override an inherited
    pack of the same name; resolution then continues further down the search
    path rather than looping.
    """
    _seen = list(_seen or [])
    path = pack_path(name, after=_after)
    if (name, path) in [(n, p) for n, p in _seen]:
        chain = " -> ".join(n for n, _ in _seen + [(name, path)])
        raise ValueError(f"pack inheritance cycle: {chain}")
    raw: Dict[str, Any] = yaml.safe_load(path.read_text(encoding="utf-8")) or {}

    params: Dict[str, Param] = {}
    lineage: List[str] = []
    parent_name = raw.get("base")
    if parent_name:
        # Same name = shadowing: continue the search below this file's directory.
        after = path.parent if parent_name == name else None
        parent = load_pack(parent_name, _seen + [(name, path)], _after=after)
        params.update(parent.params)
        lineage = parent.lineage
    own = _parse_params(raw.get("params"))
    params.update(own)
    for key in own:
        params[key].owner = name
    return ParamPack(name=name, description=raw.get("description", ""),
                     params=params, lineage=lineage + [name])
