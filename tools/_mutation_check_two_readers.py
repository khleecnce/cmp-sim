"""Mutation check for tests/test_two_absolute_readers_disagree.py.

Not a test — a one-shot verification that the enforcing test BITES.  Each
mutation below is a plausible way a future session could hollow the finding out;
each must turn the suite red.  Run:
    .venv/bin/python tools/_mutation_check_two_readers.py
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROBE = ROOT / "tools" / "envelope_jurisdiction_overlap_probe.py"
TEST = "tests/test_two_absolute_readers_disagree.py"

MUTATIONS = {
    "classifier collapsed to one class": (
        'out["hidden-by-median"].append(r)',
        'out["scale-only"].append(r)'),
    "forbidden blocks silently filled with 0.0": (
        "ls = None\n", "ls = 0.0\n"),
    "refusals deleted from the printed output": (
        '"⚠ NOT a licence to widen an envelope or to drop a block; the"',
        '""'),
    "bar re-declared locally": (
        "from tools.absolute_scale_audit import SCALE_BAR  # noqa: E402",
        "SCALE_BAR = 3.0"),
    "probe given a write path": (
        "def report() -> str:",
        "def _save(p, t):\n    Path(p).write_text(t)\n\n\ndef report() -> str:"),
}


def main() -> int:
    original = PROBE.read_text(encoding="utf-8")
    bitten = 0
    try:
        for name, (old, new) in MUTATIONS.items():
            if old not in original:
                print("SKIP  %-45s (anchor not found)" % name)
                continue
            PROBE.write_text(original.replace(old, new, 1), encoding="utf-8")
            r = subprocess.run([sys.executable, "-m", "pytest", TEST, "-q"],
                               cwd=ROOT, capture_output=True, text=True)
            ok = r.returncode != 0
            bitten += ok
            print("%-5s %-45s" % ("BITE" if ok else "MISS", name))
    finally:
        PROBE.write_text(original, encoding="utf-8")
    print("\n%d/%d mutations bitten" % (bitten, len(MUTATIONS)))
    return 0 if bitten == len(MUTATIONS) else 1


if __name__ == "__main__":
    raise SystemExit(main())
