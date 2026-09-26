"""Check the deployed instance answers on every public route.

Reads the token from ~/.fabsim-demo-token (never committed, never printed).
Usage: python tools/prod_check.py [base_url]
"""
from __future__ import annotations

import pathlib
import sys
import urllib.request

DEFAULT_BASE = "https://cmp-sim.vercel" + ".app"
ROUTES = ["/tool", "/api/meta", "/api/model?film=cu"]


def main() -> int:
    base = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_BASE
    token = pathlib.Path.home().joinpath(".fabsim-demo-token").read_text().strip()
    worst = 0
    for route in ROUTES:
        sep = "&" if "?" in route else "?"
        url = f"{base}{route}{sep}t={token}"
        try:
            with urllib.request.urlopen(url, timeout=45) as resp:
                body = resp.read()
            print(f"{route}: {resp.status} {len(body)} bytes :: {body[:100]!r}")
        except Exception as exc:  # noqa: BLE001 - report, do not raise
            print(f"{route}: ERROR {exc}")
            worst = 1
    return worst


if __name__ == "__main__":
    raise SystemExit(main())
