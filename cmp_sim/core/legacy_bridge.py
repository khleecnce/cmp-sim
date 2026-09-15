"""Bridge to the inherited `legacy/` package (FabSim, commit e385ed1).

RULE (project charter): legacy modules are verified-working. We import and wrap
them; we never re-derive or refactor them. This module is the ONLY place that
manipulates sys.path so the legacy bare-imports (`from kinematics import ...`)
keep working exactly as they do in their home repo (see legacy/sim ... conftest).
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
LEGACY_ROOT = REPO_ROOT / "legacy"
LEGACY_PACK_DIR = LEGACY_ROOT / "knowledge" / "params"
LEGACY_DATASETS = LEGACY_ROOT / "validation" / "datasets"

_TIER_DIRS = (
    LEGACY_ROOT,
    LEGACY_ROOT / "sim" / "tier1_empirical",
    LEGACY_ROOT / "sim" / "tier2_physics",
    LEGACY_ROOT / "sim" / "integration",
)


def install() -> None:
    """Make legacy modules importable. Idempotent."""
    for p in _TIER_DIRS:
        s = str(p)
        if s not in sys.path:
            sys.path.insert(0, s)


install()

# Re-exports: the legacy call surface this project is allowed to use.
from sim.params import ParamMissing, ParamPack, load_pack, available_packs  # noqa: E402
import preston as legacy_preston            # noqa: E402  legacy/sim/tier1_empirical/preston.py
import kinematics as legacy_kinematics      # noqa: E402
import wiwnu as legacy_wiwnu                # noqa: E402
import pattern_density as legacy_pattern    # noqa: E402
import process_time as legacy_process_time  # noqa: E402

__all__ = [
    "REPO_ROOT", "LEGACY_ROOT", "LEGACY_PACK_DIR", "LEGACY_DATASETS",
    "ParamMissing", "ParamPack", "load_pack", "available_packs",
    "legacy_preston", "legacy_kinematics", "legacy_wiwnu",
    "legacy_pattern", "legacy_process_time",
]
