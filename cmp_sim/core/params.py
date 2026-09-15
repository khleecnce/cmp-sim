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

import copy
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

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


#: Parsed YAML keyed by (path, mtime_ns, size). Only the PARSED TEXT is cached,
#: never a ParamPack object: packs are mutated in place by owner overrides and
#: by fitted factors, so handing out a shared instance would let one run's
#: override leak into the next. Re-building the pack from cached raw data is
#: ~90% cheaper than re-parsing 224 KB of YAML and carries no such risk.
#:
#: The mtime and size are part of the key so editing a pack takes effect
#: immediately - a stale cache during a parameter-tuning session would be a
#: silent wrong answer, which is the worst kind.
_RAW_CACHE: Dict[Tuple[str, int, int], Dict[str, Any]] = {}


def _load_yaml(path: Path) -> Dict[str, Any]:
    """Parse a YAML file, reusing the result while the file is unchanged."""
    try:
        st = path.stat()
        key = (str(path), st.st_mtime_ns, st.st_size)
    except OSError:                                   # pragma: no cover
        return yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    hit = _RAW_CACHE.get(key)
    if hit is None:
        hit = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        _RAW_CACHE[key] = hit
    # Deep-copied on the way out: callers build packs from this and must not be
    # able to mutate the cached tree.
    return copy.deepcopy(hit)


def clear_cache() -> None:
    """Drop the parsed-YAML cache (tests that write packs on the fly)."""
    _RAW_CACHE.clear()


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
    raw: Dict[str, Any] = _load_yaml(path)

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
