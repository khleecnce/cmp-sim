"""Is the deployed build the same one in this working tree?

A green e2e against production proves the deployed build works; it does NOT
prove the deployed build is the build just committed here. Vercel serves the
last successful deployment, which can be days behind HEAD, and every earlier
"the UI is fixed" report in this project was made without checking that.

Compares the SHA-256 of each browser-served asset with the file on disk.
Usage: python tools/prod_freshness.py [base_url]
"""
from __future__ import annotations

import hashlib
import pathlib
import sys
import urllib.request

DEFAULT_BASE = "https://cmp-sim.vercel" + ".app"
REPO = pathlib.Path(__file__).resolve().parent.parent
ASSETS = {
    "/tool": "cmp_sim/web/tool.html",
    "/vendor/tool3d.js": "cmp_sim/web/vendor/tool3d.js",
}


def main() -> int:
    base = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_BASE
    token = pathlib.Path.home().joinpath(".fabsim-demo-token").read_text().strip()
    stale = 0
    for route, rel in ASSETS.items():
        local_path = REPO / rel
        if not local_path.exists():
            print(f"{route}: local file missing ({rel})")
            stale = 1
            continue
        local = hashlib.sha256(local_path.read_bytes()).hexdigest()
        sep = "&" if "?" in route else "?"
        try:
            with urllib.request.urlopen(f"{base}{route}{sep}t={token}", timeout=45) as resp:
                served = hashlib.sha256(resp.read()).hexdigest()
        except Exception as exc:  # noqa: BLE001
            print(f"{route}: ERROR {exc}")
            stale = 1
            continue
        same = served == local
        print(f"{route}: {'SAME' if same else 'DIFFERENT'} "
              f"served={served[:12]} local={local[:12]} ({rel})")
        if not same:
            stale = 1
    print("FRESH" if stale == 0 else "STALE — deployment does not match this tree")
    return stale


if __name__ == "__main__":
    raise SystemExit(main())
