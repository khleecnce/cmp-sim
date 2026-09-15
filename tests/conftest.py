"""pytest setup — put the repo root on sys.path and install the legacy bridge.

The legacy modules use bare imports (`from kinematics import ...`), exactly as in
their home repository; ``cmp_sim.core.legacy_bridge`` is the single place that
handles that, so importing it here is enough.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import cmp_sim.core.legacy_bridge  # noqa: E402,F401  (installs legacy sys.path)
