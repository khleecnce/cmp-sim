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


def pack_path(name: str) -> Path:
    for d in SEARCH_PATH:
        p = d / f"{name}.yaml"
        if p.exists():
            return p
    raise FileNotFoundError(
        f"parameter pack '{name}' not found in {[str(d) for d in SEARCH_PATH]}. "
        f"available: {available_packs()}"
    )


def available_packs() -> List[str]:
    names = set()
    for d in SEARCH_PATH:
        if d.exists():
            names.update(p.stem for p in d.glob("*.yaml"))
    return sorted(names)


def load_pack(name: str, _seen: Optional[List[str]] = None) -> ParamPack:
    """Load ``<name>.yaml`` with ``base:`` inheritance, own-dir first."""
    _seen = list(_seen or [])
    if name in _seen:
        raise ValueError(f"pack inheritance cycle: {' -> '.join(_seen + [name])}")
    raw: Dict[str, Any] = yaml.safe_load(pack_path(name).read_text(encoding="utf-8")) or {}

    params: Dict[str, Param] = {}
    lineage: List[str] = []
    parent_name = raw.get("base")
    if parent_name:
        parent = load_pack(parent_name, _seen + [name])
        params.update(parent.params)
        lineage = parent.lineage
    own = _parse_params(raw.get("params"))
    params.update(own)
    for key in own:
        params[key].owner = name
    return ParamPack(name=name, description=raw.get("description", ""),
                     params=params, lineage=lineage + [name])
